# Phase 8: Convert State-Machine Prefix Call-Sites (OK/INIT/MAIN/END) - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-05-18
**Phase:** 8-convert-state-machine-prefix-call-sites-ok-init-main-end
**Areas discussed:** Wire-format for state-machine acks, `_check_response` buffer deconstruction, OK_REV/OK_CFG/FW_VERSION payload shape, debug() conversion

---

## Wire-format for state-machine acks

### Q1: Hybrid text prefix + ID-frame body vs pure ID-frame?

| Option | Description | Selected |
|--------|-------------|----------|
| Hybrid: text prefix + ID-frame body | `OK: <MAGIC>...` — host parser still does prefix-line matching first, then decodes post-prefix body. Smallest host parser delta; ROADMAP wording aligned. ~4 B/ack overhead from prefix. | |
| Pure ID-frame, no text prefix | `<MAGIC><len><id><params><crc>\n`. Severity from catalog band; host parser drops prefix matching. Smallest wire footprint; single uniform protocol. | ✓ |
| Hybrid for OK/DATA only | OK + DATA keep prefix; INIT/MAIN/END go pure. Compromise. | |

**User's choice:** Pure ID-frame, no text prefix
**Notes:** Drops the prefix-matching code path in `_read_and_parse_lines` entirely for state-machine acks.

### Q2: How does host distinguish ack vs log frames?

| Option | Description | Selected |
|--------|-------------|----------|
| Severity-band lookup | ID byte's catalog band tells acks (0x00-0x3F) from logs (0x40-0xDF) from DATA (0xE0-0xFF). No new wire metadata. | ✓ |
| Explicit ack-flag in catalog entry | Each entry gets `is_state_machine_ack` boolean. More flexible; adds catalog metadata. | |
| Two logical channels | Different MAGIC bytes for ack vs log. Cleanest separation but doubles wire-protocol surface. | |

**User's choice:** Severity-band lookup
**Notes:** Existing band layout (OK 0x00-0x0F, INIT 0x10-0x1F, MAIN 0x20-0x2F, END 0x30-0x3F, INFO 0x40-0x7F, WARN 0x80-0x9F, ERROR 0xA0-0xDF, DATA 0xE0-0xFF) is authoritative.

### Q3: DATA dual-use (log lines vs chip-read streaming) — convert which?

| Option | Description | Selected |
|--------|-------------|----------|
| Both pure ID-frame | Log lines → ID frames; streaming gets own framing token. Consistent. | ✓ |
| DATA log → ID; streaming keeps `DATA:` prefix | Minimal scope creep on the streaming path. | |
| Defer streaming — Phase 8 = log-class DATA only | Smallest blast radius; streaming gets its own phase. | |

**User's choice:** Both pure ID-frame (DATA-class log goes ID; streaming gets new framing)
**Notes:** Phase 8 owns both. Streaming-chunk framing detail in Q4.

### Q4: Chunk-size strategy under the wrapped-frame model?

| Option | Description | Selected |
|--------|-------------|----------|
| Extend `len` to u16 | Bump wire-format major version. Single frame carries up to ~64 KB. One change in 2 files. | ✓ |
| Sub-chunk: 253 B max payload per frame | Wire format unchanged; firmware splits buffer. 10-25 B overhead/op on Leo. | |
| Reduce buffer size to 252 B on both boards | Same wire; firmware buffer change. 4× more round-trips on Leo. | |

**User's choice:** Extend `len` to u16
**Notes:** Originally asked as a follow-up after the user paused to ask "in what order is the different parts of the protocol sent?" — Claude reflected the Phase 6 wire-format spec (MAGIC → len → id → params → crc → term) in plain text before re-presenting the chunk-size question.

---

## `_check_response` buffer deconstruction

### Q1: Fate of `handle->response_msg[96]`?

| Option | Description | Selected |
|--------|-------------|----------|
| Delete the field from `firestarter_handle_t` | ~96 B SRAM win/op. Uno 4.7%, Leo 3.8%. | ✓ |
| Keep field, mark deprecated | Transition cushion; Phase 9 deletes it. | |
| Delete but add `#ifdef DEV_DEBUG` cushion | Production deletion; optional dev variant. | |

**User's choice:** Delete the field from `firestarter_handle_t`
**Notes:** `response_code` stays as the operation-flow flag.

### Q2: Emit pattern at populate-sites?

| Option | Description | Selected |
|--------|-------------|----------|
| Two explicit lines per site | `LOG_*_ID_*(MSG_*, args); handle->response_code = RESPONSE_CODE_*;` — matches Phase 7 D-02. | ✓ |
| Single LOG_RESPONSE_ID_* combined macro | Tighter call-sites; hides state change. Phase 7 D-02 rejected this. | |
| Bare LOG_OK_ID_* / LOG_DATA_ID_* | Rely on response_code defaulting to OK. Smallest diff at OK + DATA sites. | |

**User's choice:** Two explicit lines per site (matches Phase 7 D-02)
**Notes:** Continuity with Phase 7 pattern. OK + DATA sites may still omit the `response_code` line where the default OK is already correct (per CONTEXT.md R-02).

### Q3: Final shape of `_check_response`?

| Option | Description | Selected |
|--------|-------------|----------|
| Strip log calls only | Drops `log_info`/`log_data` calls; keeps DATA buffer-write + ERROR abort + timeout reset. Smallest blast radius. | ✓ |
| Collapse to one-liner | Same semantics as guarded ifs; removes the switch. | |
| Inline DATA buffer-write at populate-site; delete `_check_response` | Eliminates indirection; spreads abort check. | |

**User's choice:** Strip log calls only; keep DATA buffer-write + ERROR abort
**Notes:** Same 3-branch switch structure preserved; just the log emit lines removed.

---

## OK_REV / OK_CFG / FW_VERSION payload shape

### Q1: MSG_OK_FW_VERSION shape?

| Option | Description | Selected |
|--------|-------------|----------|
| Fixed: 3×u8 (major.minor.patch) + u8 flags | 4 wire bytes. Loses arbitrary suffix flexibility. | |
| Fixed: 3×u8 only | 3 wire bytes. Drops suffix entirely. | |
| ascii_str | Variable. Preserves full string verbatim. | ✓ |

**User's choice:** ascii_str
**Notes:** Version strings are inherently free-form. Easiest to keep in sync with VERSION file.

### Q2: MSG_OK_REV shape?

| Option | Description | Selected |
|--------|-------------|----------|
| Fixed: u8 physical + u8 effective (0xFF = no override) | 2 wire bytes. Lossless. | ✓ |
| Fixed: u8 effective only | 1 wire byte. Drops physical-vs-override distinction. | |
| ascii_str | Status quo. | |

**User's choice:** Fixed: u8 physical + u8 effective (0xFF = no override)
**Notes:** Sentinel-byte encoding preserves the existing override-diagnostic surface.

### Q3: MSG_OK_CFG shape?

| Option | Description | Selected |
|--------|-------------|----------|
| Fixed: u32 r1 + u32 r2 + u8 override (0xFF = none) | 9 wire bytes. Mirrors HW_REV. | ✓ |
| Fixed: u32 r1 + u32 r2 | 8 wire bytes. Override info lives only in OK_REV. | |
| ascii_str | Status quo. | |

**User's choice:** Fixed: u32 r1 + u32 r2 + u8 override (0xFF = none)
**Notes:** Same sentinel convention as P-02; redundancy across OK_REV + OK_CFG is acceptable for diagnostic clarity.

### Q4: MSG_OK_FW_HANDSHAKE (per-command ack)?

| Option | Description | Selected |
|--------|-------------|----------|
| Single composite: u8 hw + u8 cmd + ascii_str fw_version | One ID-frame per command-ack. Same round-trip count as today. | ✓ |
| Split: MSG_OK_FW_VERSION at probe + MSG_OK_CMD_ACK per command | Saves ~10 B/command on steady state; two-stage probe logic. | |
| Drop FW + HW; only u8 cmd | Smallest wire on hot path. Lose context if host re-probes mid-session. | |

**User's choice:** Single composite: u8 hw + u8 cmd + ascii_str fw_version
**Notes:** Mirrors today's `PARSE_RESPONSE` template emit. Fixed-shape params first; ascii_str last per Phase 6 convention.

---

## debug() conversion

### Q1: Touch the 34 debug() sites in Phase 8?

| Option | Description | Selected |
|--------|-------------|----------|
| Keep as text — status quo | Already free in release (SERIAL_DEBUG gate). Zero catalog cost. | |
| Single MSG_DEBUG with ascii_str | One generic ID receives debug strings. +1 ID; ~0 production cost. | |
| Per-string debug IDs | +33 IDs. Full structured invariant. | |

**User's choice (free-text):** "I want the debug to use the MSG_DEBUG and a sub id for the debug value"
**Notes:** Hybrid not in the menu — single main `MSG_DEBUG` catalog entry + separate `sub_id` namespace for the specific debug string. Claude reflected this back in plain text and proposed concrete shape (`<MAGIC><len><MSG_DEBUG><sub_id><params><crc><term>`) before continuing.

### Q2: How nailed-down should the design be before research/planning?

| Option | Description | Selected |
|--------|-------------|----------|
| Lock the basics; leave details to researcher | sub_id width, table location, params semantics open | |
| Decide more now | Take 2-3 more questions to lock here | ✓ |
| Defer entirely | Phase 8 mentions MSG_DEBUG; details for a later phase | |

**User's choice:** Decide more now

### Q3: sub_id width?

| Option | Description | Selected |
|--------|-------------|----------|
| u8 (256 entries) | 34 today; ~7× headroom. Smallest wire. | ✓ |
| u16 (65,536 entries) | Future-proof; +1 B/frame. | |

**User's choice:** u8 (256 entries)

### Q4: Where does the debug-strings table live?

| Option | Description | Selected |
|--------|-------------|----------|
| Separate canonical: tools/catalog/debug_strings.toml | Mirror messages.toml; codegen produces firmware header + host Python. Distinct namespace. | |
| Inline in messages.toml under a [debug] section | Single canonical file with two sections; same codegen handles both. | ✓ |
| Pure firmware-side #define / host-side hardcoded dict | No catalog file; smallest tooling delta; no drift gate. | |

**User's choice:** Inline in messages.toml under a [debug] section
**Notes:** Single canonical file with `[messages]` + `[debug]` sections. Codegen drift gate covers both.

### Q5: Can sub_id frames carry fixed-shape params after the sub_id?

| Option | Description | Selected |
|--------|-------------|----------|
| Yes — sub_id entries declare params like main messages | Symmetric with main catalog; debug_format converts cleanly. | ✓ |
| No — sub_id is the entire payload | Pure-string debug only; debug_format does not convert cleanly. | |
| Yes, but only u8/u16/u32 (no ascii_str/bytes) | Fixed-shape only. Covers most debug_format cases. | |

**User's choice:** Yes — sub_id entries declare params like main messages
**Notes:** `LOG_DEBUG_ID_U24(DBG_ADDR, addr)` becomes a clean pattern; `DBG_ADDR` declares its own `params = [{type = "u24"}]` in `[debug.DBG_ADDR]`.

---

## Claude's Discretion

The operator did not lock these — researcher and planner propose concrete choices in RESEARCH.md / PLAN.md without re-asking:

- Commit cadence for the cutover (suggested grouping in CONTEXT.md).
- Native test impact (test_messages assertions break under W-04; fold the test update into the wire-format commit).
- Host parser refactor depth (smallest surgical removal of prefix-matching path).
- Debug conversion ordering (single sweep at end of Phase 8 vs piecewise alongside each touched file).
- `copy_to_buffer` helper fate (deprecate / delete now vs Phase 9).

## Deferred Ideas

- Firmware major-version bump to 3.0.0 (Phase 9).
- Deletion of legacy `logging.h` macro tower (Phase 9 / LFW-03/04).
- Final Leonardo flash measurement vs Phase 6 baseline (Phase 9 — after legacy strings drop out).
- Host CLI rendering of decoded debug frames (silent-by-default or `--debug` flag — host concern, Phase 8 plan or later).
- Wire-format minor-version negotiation (hard cutover for now; negotiation if mixed-version fleet ever matters).
