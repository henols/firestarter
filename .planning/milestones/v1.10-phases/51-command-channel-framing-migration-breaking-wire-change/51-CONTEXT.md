# Phase 51: Command-Channel Framing Migration (breaking wire change) - Context

**Gathered:** 2026-06-02
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 51 migrates the **host→firmware JSON command channel** (Framing 1) into the
Phase-49 COBS `0x00` framing layer, in **lockstep across the firmware and host sub-repos**.
The firmware decodes a frame, **verifies its CRC8 BEFORE the JSON parser sees the payload**,
then hands the decoded bytes to `parse_json()`. The legacy `{`-peek / discard-non-`{`
command-ingest loop is **deleted outright** — the framed protocol is the only command path.
The command channel, which previously had **no checksum**, now gains end-to-end integrity
(closing the CRC-01 command-channel obligation under FRAME-05).

This is a **breaking wire-protocol change** with **no mixed-version interop** (cf. the v1.2
Message-ID rework). The framed protocol is the ONLY supported protocol — backwards
compatibility is an explicit non-goal (operator-locked 2026-06-02). Beta-only; nothing
promoted to stable without operator authorization.

**In scope:**
- Framing 1 (host→fw JSON command) only — both repos in lockstep.
- Firmware: replace the `CMD_IDLE` `{`-peek ingest loop (`firestarter.cpp` ~lines 162-172)
  with a COBS frame decoder → CRC8 verify → `parse_json()`. Fully consume the frame incl.
  the trailing `0x00` before parsing.
- Host: extend `send_json_command()` (`serial_comm.py` ~lines 155-159) to wrap the JSON
  payload + CRC8 in a single COBS frame, emitted as one atomic `send_bytes()` call.
- ALL host→fw commands are framed — **including** the `CMD_FW_VERSION` version probe.
- Reuse the Phase-50 COBS decode + CRC8 + resync primitives already built on the data path.

**Out of scope (later phases / non-goals — do NOT pull forward):**
- fw→host command **responses** (`OK:`/`ERROR:`/`DATA:` text + log/telemetry frames) stay
  UNCHANGED — ADR §4.2 scopes Phase 51 to the host→fw direction only; Framing 4 unchanged.
- Full byte-compat round-trip / lockstep contract tests (incl. pathological all-delimiter
  command payloads) → **Phase 52** (LOCK-01/LOCK-02).
- Bench verification across Uno/Leonardo/uno328pb → **Phase 53**.
- Any mixed-version interop / capability-negotiation / dual-protocol support → **non-goal**.
- Data-block framing (Framing 2/3) — already shipped in **Phase 50**.

</domain>

<decisions>
## Implementation Decisions

### Carried forward — LOCKED by Phase 49 ADR (`.planning/v1.10-FRAMING-DECISION.md`; do NOT re-litigate)
- **Frame contract = `[COBS-encoded(JSON payload + CRC8 byte)][0x00 delimiter]`** (§4.1/§4.3).
  The CRC8 byte is appended to the raw JSON payload *before* COBS encoding and is itself
  COBS-encoded. Same contract as the Phase-50 data path.
- **CRC8-CCITT poly 0x07, seed 0x00, no reflection, no final XOR**, computed over the raw JSON
  payload. Existing CRC8 tables reused unchanged in both repos (D-05): firmware PROGMEM table
  (`rurp_serial_utils.cpp` ~lines 109-131) + host `frame_parser.py` `_build_crc8_table()`/`_crc8_ccitt()`.
- **CRC8-before-parse mandate (V5 / §4.4):** a frame that passes the COBS delimiter check but
  fails CRC8 is discarded — its bytes do NOT reach `json_parser.c`. This is the security
  obligation this phase exists to satisfy on the command channel.
- **Full-frame consumption (SAFE-01 sub-claim C / §1.3):** the firmware frame decoder MUST
  consume the entire frame INCLUDING the terminating `0x00` before calling the JSON parser.
- **Atomic single-write (SAFE-01 sub-claim B):** the entire framed command — JSON + CRC8 +
  COBS body + trailing `0x00` — is assembled as one `bytes` object and passed to `send_bytes()`
  in a single call. A split-write of the delimiter is forbidden (preserves the SAFE-01 proof).
- **Dual-repo lockstep mandate:** `rurp_serial_utils.cpp`/`firestarter.cpp` (fw) ↔
  `serial_comm.py`/`frame_parser.py` (host) change together; commits land inside each sub-repo
  on branch `v1.10-serial-transport-hardening`.

### Breaking-change guard (SC3) — operator-locked 2026-06-02
- **D-01:** **No interop machinery — the framed protocol is the ONLY supported protocol.**
  Backwards compatibility is an explicit **non-goal**. No capability negotiation, no
  dual-protocol/fallback support, no runtime handshake byte beyond what already exists. A
  mismatched old↔new firmware/host pair is unsupported; if run, it simply fails (frame-only
  firmware cannot parse a raw `{...}` → command never inits → existing `CMD_TIMEOUT`; an old
  host driving new firmware likewise fails) — and that is acceptable.
- **D-02:** **The breaking nature is documented for the beta cut** (MILESTONES / READMEs note
  this is a breaking wire change; upgrade both repos in lockstep) — documentation is the
  "equivalent" guard SC3 calls for, given D-01.
- **D-03 (Claude's discretion / planner's call):** the host already runs a `CMD_FW_VERSION`
  probe + `_validate_firmware_version()` 2.0.0 floor at connect (`serial_comm.py` ~lines
  466-520). Retaining it as-is is fine; OPTIONALLY bump the floor to the v1.10 framing version
  so a stale firmware yields a clean "reflash" error rather than an opaque timeout. Not
  load-bearing under D-01 — incidental UX nicety, not a compatibility mechanism.

### Probe framing (chicken-and-egg) — resolved by D-01
- **D-04:** **The version probe (`CMD_FW_VERSION`) is framed like every other command.** No
  unframed plaintext escape hatch. There is no chicken-and-egg problem because there is no old
  peer we are obligated to detect or speak to (D-01). Both matched new peers speak frames from
  the first byte. (The fw→host version *response* stays text — out of scope per §4.2.)

### Legacy `{`-peek command-ingest path (SC2)
- **D-05:** **Deleted outright.** Remove the `{`-peek / discard-non-`{` loop
  (`firestarter.cpp` ~lines 162-172) entirely. Firmware command ingest accepts ONLY COBS
  frames: accumulate bytes until `0x00` → COBS decode → CRC8 verify → `parse_json()`. No raw
  `{` path remains (no dev/debug fallback) — smallest attack/maintenance surface, matches the
  "only supported protocol" stance, and avoids reintroducing a CRC-less ingest path that would
  conflict with the CRC8-before-parse mandate.

### Garbled / incomplete command-frame handling (mirrors Phase 50 D-01 fail-fast + resync)
- **D-06:** **Mirror the Phase-50 data-path posture + add a size cap.**
  - On COBS-decode or CRC8 failure: **drain bytes up to and including the next `0x00`**
    (resync — desync bounded to one frame) and surface the existing error path immediately
    (fail-fast, no hang). Reuses the Phase-50 resync primitive and the existing firmware error
    surface; the user re-runs the operation. No block-level retransmit/ACK is added.
  - Partial-frame bound: the `CMD_IDLE` ingest accumulates bytes **non-blocking** across loop
    iterations; if accumulation exceeds a **max-frame-size cap** (`CMD_FRAME_MAX` or equivalent,
    sized for the largest legitimate JSON command), drain to the next `0x00` and error.
  - **No new idle wall-clock timer.** A stalled partial frame whose `0x00` never arrives is
    handled by the size cap, not a new timeout — keeps the idle loop free of new timer state.

### Claude's Discretion
- Exact firmware command-frame receive-buffer strategy and where the decoded JSON lands
  (decode in place vs a small dedicated buffer), provided the no-second-large-buffer / Uno-RAM
  constraint is respected (JSON commands are small, well under 256 B).
- The concrete value/name of the max-frame-size cap (`CMD_FRAME_MAX`), sized from the largest
  legitimate command JSON with margin.
- Whether to bump the host version-floor constant (D-03) — incidental, planner's call.
- Placement/reuse of the COBS-decode + CRC8 helpers shared with the Phase-50 data path
  (function reuse vs a thin command-channel wrapper).
- Exact firmware/host symbol names for the new framed command encode/decode functions.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### The frozen contract (read FIRST — this is the binding spec)
- `.planning/v1.10-FRAMING-DECISION.md` — the Phase-49 decision ADR. **Specifically for Phase 51:**
  - §1.3 — SAFE-01 host-half proof (sub-claim B atomic-write mandate; sub-claim C full-frame
    consumption-before-parse) — both are mandatory Phase-51 design constraints.
  - §4.1 — Delimiter + streaming-COBS scheme + atomic-write mandate.
  - §4.2 — Scope of framing (Framing 1 = Phase 51; Framing 4 / fw→host responses UNCHANGED).
  - §4.3 — Frame layout table (`[COBS(payload+CRC8)][0x00]`; `len_u16` removed; CRC8 placement).
  - §4.4 — **CRC8-before-parse security mandate (V5 / T-49-01)** — the load-bearing Phase-51 rule.
  - §4.6 — Per-file change map; note the trailing paragraph: Phase 51 modifies
    `firestarter.cpp` lines 162-172 (the `{`-peek loop), outside the four-file data-path map.

### Prior phase context (the framing primitives Phase 51 reuses)
- `.planning/phases/50-data-path-framing-layer-automatic-resync-dual-repo-lockstep/50-CONTEXT.md`
  — Phase-50 decisions: D-01 fail-fast + resync posture (mirrored here as D-06), the COBS
  encode/decode + CRC8 helpers added to `frame_parser.py`, the resync-to-next-`0x00` discipline,
  the corrupted-marker drain directive. Phase 51 reuses these primitives for the command channel.
- `.planning/phases/49-framing-mechanism-decision-cobs-0x00-vs-slip-0xc0/49-CONTEXT.md`
  — mechanism-decision context (COBS selected; neutral-matrix rationale; D-04/D-05 upstream locks).

### Upstream evaluation (immutable input)
- `.planning/v1.9-COBS-DECISION.md` — survey + constraints record; D-04 (Uno-fit) / D-05 (keep
  CRC8). The v1.10 ADR supersedes only its DEFER line for the mechanism.

### Requirements & roadmap
- `.planning/REQUIREMENTS.md` — **FRAME-05** (the one requirement this phase satisfies) +
  **CRC-01** (command-channel integrity obligation, now closed via FRAME-05); v1.10 Non-Goals
  (note: re-framing fw→host log/telemetry is explicitly a non-goal).
- `.planning/ROADMAP.md` — Phase 51 entry (Goal + 4 Success Criteria + Depends-on); Phase 52
  (round-trip/lockstep tests that pin this phase's command-frame contract) + Phase 53 (bench).

### Code to change — firmware (`v1.10-serial-transport-hardening` branch in `firestarter/`)
- `firestarter/src/firestarter.cpp` — `loop()` `CMD_IDLE` command-ingest (~lines 158-176): the
  `{`-peek / discard-non-`{` loop to **delete** and replace with the COBS frame decoder →
  CRC8 → `parse_json()`. `init_programmer()`/`parse_json()` call sites are the integration point.
- `firestarter/src/boards/rurp_serial_utils.cpp` — COBS decode + CRC8 primitives from Phase 50
  (PROGMEM CRC8 table ~lines 109-131) reused for command-frame decode. `rurp_communication_*`
  read helpers feed the ingest loop.
- `firestarter/include/firestarter.h` — `FW_VERSION`/`CMD_FW_VERSION` (~lines 16/39); home for
  any new `CMD_FRAME_MAX`-style constant (constant-parity with host per CLAUDE.md).
- `firestarter/test/native/avr/test_messages/` — Unity home for the command-frame decode/resync
  cases (full byte-compat matrix is Phase 52, but a minimal decode + CRC8-reject + resync case
  belongs with the change).

### Code to change — host (`v1.10-serial-transport-hardening` branch in `firestarter_app/`)
- `firestarter_app/firestarter/serial_comm.py` — `send_json_command()` (~lines 155-159) to wrap
  JSON + CRC8 in one COBS frame via a single atomic `send_bytes()` (~line 134); the existing
  `CMD_FW_VERSION` probe + `_validate_firmware_version()`/`_is_version_sufficient()` (~lines
  466-520) now drive a framed probe (D-04); `expect_ack`/`get_response`/`_read_and_parse_lines`
  (response side) stay on the existing text/log path (out of scope).
- `firestarter_app/firestarter/frame_parser.py` — COBS encode/decode + `_crc8_ccitt()`
  (~lines 28-44) from Phase 50, reused for the command frame.
- `firestarter_app/firestarter/constants.py` — host mirror of any new `CMD_FRAME_MAX`-style
  constant (firmware/host constant-parity per CLAUDE.md).

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **Phase-50 COBS encode/decode + CRC8 helpers** (both repos) — already built and contract-frozen
  for the data path; Phase 51 reuses them verbatim for the command frame (only the call sites and
  the payload source differ). No new framing algorithm.
- **Host version handshake** (`serial_comm.py` ~lines 466-520) — `_validate_firmware_version`,
  `_is_version_sufficient`, 2.0.0 floor, `CMD_FW_VERSION` text probe. Present and working; the
  optional D-03 floor bump rides this, no new mechanism needed.
- **`init_programmer()` / `parse_json()`** (`firestarter.cpp`) — the existing command-parse entry
  the new frame decoder feeds; the decoder replaces the byte-source, not the parser.

### Established Patterns
- **Marker/peek-dispatched command ingest** (`firestarter.cpp` `loop()` `CMD_IDLE` branch) — the
  byte-peek robustness trick is exactly what Phase 51 **deletes** (D-05): framing makes byte-peeking
  obsolete because the `0x00` delimiter gives unambiguous command boundaries with integrity.
- **Fail-fast + resync-to-next-`0x00`** — the Phase-50 data-path recovery posture (D-01), mirrored
  here for the command channel (D-06). Same discipline, command-side application.
- **Breaking lockstep upgrade, no mixed-version interop** — v1.2 Message-ID precedent; D-01 commits
  to it absolutely (only-supported-protocol stance, backwards-compat as non-goal).
- **Firmware/host constant parity** (CLAUDE.md) — any new `CMD_FRAME_MAX`-style constant must be
  duplicated in `firestarter.h` + `constants.py` and is guarded by the parity tests (Phase 52).

### Integration Points
- Firmware: COBS frame decoder output → CRC8 verify → `parse_json()` → `init_programmer()`; CRC8
  failure → drain-to-next-`0x00` + existing error surface (no new error path).
- Host: `send_json_command()` → COBS+CRC8 wrap → single `send_bytes()`/`flush()`; response read
  path unchanged.
- This phase's command-frame contract is the direct input to **Phase 52** (round-trip tests pin
  data-block AND command frames, incl. pathological all-delimiter command payloads).

</code_context>

<specifics>
## Specific Ideas

- "Don't care about backwards compatibility — this protocol is the only supported" (operator,
  2026-06-02). This is the load-bearing steer: it removes capability-negotiation/fallback work
  from scope and makes documentation the SC3 "guard equivalent".
- The CRC8-before-parse rule is the *point* of framing the command channel — the command channel
  had no checksum before. The decoder must NOT leak any byte of a CRC-failing frame to
  `json_parser.c` (V5 / §4.4). A test asserting "corrupted command frame → parser never invoked,
  clean error" is the headline behavioral proof for SC1.
- The size cap (D-06) is the command-channel analog of Phase 50's bounded-desync goal: an
  oversized accumulation (delimiter never arrives) resyncs rather than growing without bound — the
  test should assert bounded recovery, not merely "an error was raised".
- Framing the `CMD_FW_VERSION` probe (D-04) means there is no plaintext command path at all —
  a deliberate consequence of the only-supported-protocol stance, worth calling out in the beta
  breaking-change note.

</specifics>

<deferred>
## Deferred Ideas

- **Capability negotiation / dual-protocol support / runtime interop guard** — explicitly a
  **non-goal** (D-01), not a future phase. Recorded so it is not re-raised.
- **Framing the fw→host command-response direction** (`OK:`/`ERROR:`/`DATA:` + log/telemetry) —
  out of scope per ADR §4.2 (Framing 4 unchanged); not planned for v1.10.
- **Block-level retransmit / ACK on the command channel** — D-06 chose fail-fast; transparent
  auto-recovery would be a new capability, its own phase if ever wanted.
- **Full byte-compat round-trip / lockstep contract tests** (incl. pathological all-delimiter
  command payloads, both encode directions) → **Phase 52** (LOCK-01/LOCK-02).
- **Bench verification** (Uno/Leonardo/uno328pb, operator-gated) → **Phase 53**.

None — discussion stayed within phase scope (no todos matched Phase 51).

</deferred>

---

*Phase: 51-command-channel-framing-migration-breaking-wire-change*
*Context gathered: 2026-06-02*
