# Phase 6: Logging Infrastructure (catalog + codegen + helper + decoder) - Context

**Gathered:** 2026-05-18
**Status:** Ready for planning
**Source:** /gsd-discuss-phase 6 — user selected `Wire frame format` only; the other three identified gray areas (catalog format, param-shape schema, decoder coexistence) deferred to researcher/planner discretion.

<domain>
## Phase Boundary

**In scope (Phase A of the locked v1.2 phased migration):**
- A single canonical **message catalog** in the meta-repo declares every firmware log message as `{id, symbolic_name, format_string, parameter_shape}`.
- A **codegen pipeline** produces `firestarter/include/messages.h` (C++ enum + ID constants + `MSG_PARAM_COUNT(id)` helper) and `firestarter_app/firestarter/messages.py` (host-side ID → format-string + shape lookup) deterministically (byte-identical on re-run).
- Catalog validation (unique 1-byte IDs, unique symbolic names, well-formed param shapes, non-empty format strings) fails the build on violation.
- A firmware `rurp_log_id(uint8_t msg_id, const uint8_t* params, uint8_t param_count)` helper compiles and links alongside the existing `rurp_log` / `rurp_log_P` family. **No existing call-site is converted yet** — both paths coexist.
- A host decoder in `firestarter_app/firestarter/serial_comm.py` reads an ID-encoded frame, validates it, and yields a `LogMessage(severity, text)` rendered against the catalog. Severity comes from the catalog entry's category.
- The host's firmware-version check refuses pre-v1.2 firmware with an operator-facing "upgrade firmware" message (host-side guard wired and unit-tested; LFW-05 firmware bump itself lands in Phase 9).
- Both sub-repo CI pipelines run codegen and assert `git diff --exit-code` on the generated files — drift fails CI visibly in the PR.

**Out of scope (deferred):**
- Conversion of any existing call-site (`OK:`/`INIT:`/`MAIN:`/`END:`/`INFO:`/`WARN:`/`ERROR:`) — that is Phases 7–8.
- Deletion of old `rurp_log` / `rurp_log_P` / `LOG_*_MSG` PROGMEM strings and the `log_info_const` / `log_error_format` / `log_warn` macros — that is Phase 9.
- Firmware major-version bump to v3.0.0 — wire-in happens in Phase 9; Phase 6 only lands the host-side guard that will refuse old firmware after the bump.
- Changes to the `DATA:` binary read-payload prefix — explicitly locked text-format for v1.2.

</domain>

<decisions>
## Implementation Decisions

### Wire Frame Format

- **D-01 — Framing: binary frame with 4-byte preamble, length, ID, params, CRC8, terminator.**
  Exact byte layout, MSB-first on the wire:

  ```
  byte 0..3 : 0xAA 0x55 0xAA 0x55   — 4-byte magic preamble
  byte 4    : len                    — count of bytes that FOLLOW the len byte (= 1 + param_bytes + 1)
  byte 5    : id                     — 1-byte message ID (0–255)
  byte 6..N : params                 — raw param bytes per catalog `parameter_shape`
  byte N+1  : crc8                   — CRC8 over [id, params]
  byte N+2  : 0x0A                   — terminator anchor for re-sync
  ```

  **Total per-frame overhead:** 7 bytes (4 magic + 1 len + 1 crc + 1 terminator). Smallest frame (zero-param ID): 7 bytes on wire vs typical pre-v1.2 text frame (e.g. `INFO: Main start\r\n` = 18 bytes). Flash savings come from eliminating per-call PROGMEM strings inside firmware, not from per-byte wire compression — wire-byte count is a secondary effect.

  Rationale (driven by the **Uno PORTD ghost-byte hazard** the operator surfaced during discussion): on the Uno, the serial TX pin shares PORTD with the lower address-bus lines. During programming/reading windows, bus toggles can leak as spurious bytes on the serial line. The 4-byte magic + length-authoritative + CRC8 design is foolproof against this class of corruption — single-byte sentinel was rejected for exactly this reason.

- **D-02 — Magic value: `0xAA 0x55 0xAA 0x55` (alternating-bit preamble).**
  Classic UART preamble pattern (bits `10101010 01010101 10101010 01010101`). Maximum bit transitions; statistically incompatible with PORTD address-line aliasing (which clusters into runs of similar values).

- **D-03 — Length byte is authoritative; CRC8 over `[id, params]` only.**
  `len` = `1 + param_bytes + 1` (counts ID + params + CRC; does NOT count itself or the trailing 0x0A). The host parser uses `len` to read the exact number of remaining bytes **without consulting the catalog** — this preserves forward-compat: an unknown (future) ID can be skipped cleanly even if the host's catalog is older than the firmware's.

  CRC8 algorithm: polynomial **0x07** (CCITT / `crc-8`), seed 0x00, no reflection, no final XOR. Computed over the `len`-byte window starting at `id` and ending at the byte before `crc8` (i.e., over `[id, params]`). The 0x0A terminator is NOT part of the CRC — it is a re-sync anchor only.

- **D-04 — Terminator: trailing `0x0A` is a re-sync anchor, not a delimiter.**
  Parser does not rely on 0x0A to mark frame end (length does that). The 0x0A is present so a parser that has lost track mid-frame can re-anchor at the next newline boundary. Also means a frame on the wire looks like a "line" to debug tools doing line-buffered serial captures.

- **D-05 — Host parser: always-on byte-stream reader, magic-scan with text-line fallback.**
  `serial_comm.py` switches from line-by-line to byte-stream input. Pseudocode:

  ```
  accumulator = bytearray()
  loop:
      b = read_byte()
      accumulator.append(b)
      if accumulator[-4:] == b'\xAA\x55\xAA\x55':
          # Consume frame: read len, then len bytes, verify CRC, yield LogMessage.
          # Drop the 4 magic bytes from accumulator first so any preceding bytes are dispatched as a (possibly empty) text line.
          dispatch_text_line(bytes(accumulator[:-4]))
          accumulator.clear()
          consume_binary_frame()  # reads len, id, params, crc, 0x0A
      elif b == 0x0A:
          dispatch_text_line(bytes(accumulator))
          accumulator.clear()
      # else: keep accumulating
  ```

  Net effect: a single unified read loop handles both text lines (existing `OK:`/`INFO:`/`DATA:` etc.) **and** binary frames. The existing rightmost-prefix regex (`serial_comm.py:182`) continues to handle the printable-ASCII case unchanged. No firmware-version branching needed in the read path — the catalog itself is the protocol contract.

  This design is **decisive for Phase 7+**: when call-sites convert to `rurp_log_id`, the host already knows how to receive them.

- **D-06 — Decoder coexistence at end of Phase 6.**
  At Phase 6 close, the always-on reader is wired in but **no firmware call-site emits frames yet** (Phase 6 is infrastructure-only, per LMIG-01). The LHOST-01 acceptance fixture is a Python-side hand-crafted frame fed into `serial_comm.py` via a unit test or a `BytesIO`-style harness; this verifies the decoder end-to-end before any firmware byte hits the wire.

### Claude's Discretion (deferred to researcher/planner)

The operator explicitly skipped these gray areas during discussion. The researcher should recommend concrete choices, ground them in Phase 6's success criteria, and present them in PLAN.md / RESEARCH.md for the operator to accept or amend:

- **Catalog file format** — YAML / TOML / JSON / hand-rolled DSL. Constraint: human-editable, diff-friendly, deterministic to parse (no map-ordering surprises). Recommendation: TOML or YAML (with sorted-key serialization on regen). Default: pick one in research.
- **Catalog file path in the meta-repo** — REQUIREMENTS suggests `.planning/catalog/messages.yaml`; the planner is free to propose a different location if there is a clear reason (e.g., colocated with codegen tool).
- **Meta-repo → sub-repo distribution** — the two sub-repos (`firestarter/`, `firestarter_app/`) are independent git repos and don't currently track the meta-repo. Options: (a) commit a vendored copy of the catalog into each sub-repo (with the meta-repo as authoritative source + a copy-sync script), (b) git submodule from each sub-repo back to the meta, (c) commit only the *generated* files into each sub-repo and run codegen from a shared CI runner that has access to the meta. Researcher should weigh dev-ergonomics vs CI complexity. The locked end-state is the same regardless: generated files committed to both sub-repos, CI runs `regen && git diff --exit-code`.
- **Param shape representation + per-param render hints** — LHOST-02 requires that `[u24]` renders as `0x{:06X}`, so render rules must live somewhere. Two options: (a) shape carries types only, render rules derived from a per-type default table (`u24 → hex6`, `u16 → dec`, `i32 → signed-dec`); (b) shape entries carry an explicit `render` field (`{type: u24, render: hex_addr}`). Researcher should pick the smallest schema that covers the existing 66 unique log strings in `firestarter/src/`.
- **Codegen language + invocation** — Python script in `tools/` is the obvious default given existing `tools/build_db.py` precedent in `firestarter_app/`. Planner should confirm and pin the exact invocation path used by both sub-repo CIs.
- **`MSG_PARAM_COUNT(id)` implementation** — generated header could expose this as a `constexpr` lookup, a `switch`-based inline, or a PROGMEM table. Researcher picks the smallest-flash option for AVR.
- **`rurp_log_id` integration with `com_mode` + `SERIAL_DEBUG`** — the existing `rurp_log` honors a `com_mode` gate (boards/uno_rurp_shield.cpp:82) and duplicates output through `log_debug()` when `SERIAL_DEBUG` is set. The new helper should preserve both behaviors; the planner should mirror them in the new code path.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase scope + requirements (authoritative)
- `.planning/ROADMAP.md` §"Phase 6: Logging Infrastructure" — six success criteria (catalog determinism, codegen drift gate, helper coexistence with old path, host decoder fixture test, CI drift gate, host fw-version guard).
- `.planning/REQUIREMENTS.md` — LCAT-01..05, LFW-01, LFW-02, LFW-05, LHOST-01..04, LCI-01..04, LMIG-01 (17 requirements mapped to this phase).
- `.planning/PROJECT.md` §"Target features" + §"Constraints (locked at milestone start)" — milestone-level locks (1-byte IDs, raw byte arrays, English only, lockstep upgrade, CI drift gate).
- `.planning/STATE.md` §"v1.2 Decisions (locked at milestone start, 2026-05-18)" — same locks restated with the operative-decision wording.

### Existing firmware logging surface (the thing being rebuilt around, not yet removed)
- `firestarter/include/logging.h` — full macro tower (`log_info_const`, `log_info_format`, `log_warn`, `log_warn_format`, `log_error_const`, `log_error_format`, `log_data_const`, `send_ack_const`, `send_ack_format`, plus `send_main_done`/`send_init_done`/`send_end_done`). The new `LOG_*` macros wrapping `rurp_log_id` need to be no more verbose than these — see LFW-02.
- `firestarter/include/rurp_shield.h:127-128` — `rurp_log(PGM_P type, const char* msg)` + `rurp_log_P(PGM_P type, PGM_P msg)` declarations. The new `rurp_log_id` lives alongside these in the same header.
- `firestarter/src/logging.c` — `LOG_OK_MSG`, `LOG_INIT_DONE_MSG`, `LOG_MAIN_DONE_MSG`, `LOG_END_DONE_MSG`, `LOG_INFO_MSG`, `LOG_DATA_MSG`, `LOG_WARN_MSG`, `LOG_ERROR_MSG` PROGMEM strings. **Not deleted in Phase 6** — these stay until Phase 9.
- `firestarter/src/boards/uno_rurp_shield.cpp:80-97` — current `rurp_log` / `rurp_log_P` Uno implementation (with `com_mode` gate and `SERIAL_DEBUG` duplication). The new `rurp_log_id` should mirror both behaviors.
- `firestarter/src/boards/rurp_serial_utils.cpp:11-25` — `_firestarter_log_ram` / `_firestarter_log_progmem` — the actual `SERIAL_PORT.print(...).println(...).flush()` site for text frames. The new binary frame emitter is a sibling helper at this layer.
- `firestarter/src/firestarter.cpp:152-155` — `PARSE_RESPONSE` macro for the `OK: FW: ...` bootstrap; this single string stays text-formatted by design (LFW-05) so the host can read the version before loading the catalog.

### Existing host parser (the thing the new decoder slots into)
- `firestarter_app/firestarter/serial_comm.py:160-211` — `_parse_response_line` (rightmost-prefix regex), `_log_rurp_feedback` (severity routing), `_read_and_parse_lines` (current read loop). The new always-on byte-stream reader replaces the loop in `_read_and_parse_lines`; the prefix regex stays for the text fallback.
- `firestarter_app/firestarter/serial_comm.py:170-188` — the comment block explaining why "rightmost prefix wins" exists (PORTD ghost-byte tolerance for text). The binary-frame design respects the same constraint via 4-byte magic.
- `firestarter_app/firestarter/serial_comm.py:380-415` — current FW-version handshake. The Phase 6 host-side "refuse pre-v1.2 firmware" guard slots in here.
- `firestarter_app/firestarter/firmware.py:55-97` — `FirmwareManager.check_current_firmware` — operator-facing version-check entry point.
- `firestarter_app/firestarter/constants.py` — `COMMAND_FW_VERSION = 13`. Must stay in sync with `firestarter/include/firestarter.h:40`.

### Firmware version source-of-truth + CI
- `firestarter/include/version.h` — `#define VERSION "2.0.11-dev"`. Phase 9 bumps the major to `3.0.0`; the Phase 6 host-side guard reads `firmware_version.split(".")[0]` and refuses < 3.
- `firestarter/.github/workflows/build.yml` + `firestarter/.github/scripts/update_version.py` — firmware CI. The catalog-drift gate (`regen && git diff --exit-code`) lives in a new pre-build step.
- `firestarter_app/.github/workflows/release.yml` + `firestarter_app/.github/workflows/publish.yml` — host CI. Same drift gate logic.
- `firestarter/platformio.ini` — `[env:uno]` / `[env:leonardo]` / `[env:native]`. Build must continue to succeed for all three; native (`pio test -e native`) is the unit-test gate for `rurp_log_id` linking.

### Existing native test harness (LHOST-01 decoder fixture template)
- `firestarter/test/native/avr/test_dispatch/host_stubs.cpp` — pattern for host-side stubs. A new `test_messages/` suite can mirror this layout for the codegen output's C++ side.
- `firestarter_app/firestarter_test.sh` + `firestarter_app/write_test.sh` — bench integration tests. Phase 6 should NOT regress these against the unchanged text-format firmware (since no call-site converts in Phase 6).

### Carry-forward awareness (not in scope; just don't break)
- `.planning/debug/fm1608-fresh-chip-baseline.md` — v1.1 FM1608 byte-0 read bug, parked. Phase 6 doesn't touch the EPROM read path; just don't regress.
- `firestarter_app/firestarter_test.sh:31, 48-67` — WARNING-4 schema drift (carried from v1.1). Out of scope for Phase 6; flag if test scripts must be modified for any reason.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **`rurp_log` / `rurp_log_P` core path** (boards/rurp_serial_utils.cpp) — the new `rurp_log_id` is a sibling at the same layer. Reuse `SERIAL_PORT.write(uint8_t)` for binary bytes (not `print` which formats as ASCII).
- **`com_mode` gating** (uno_rurp_shield.cpp:82) — must be preserved: `rurp_log_id` is a no-op when `com_mode == false` (i.e., when the serial pins are repurposed as bus lines during programming).
- **`SERIAL_DEBUG` duplication path** (uno_rurp_shield.cpp:90-93) — when set, current `rurp_log_P` also routes through `log_debug(type, msg)`. The new helper can either render the same way for debug duplication, or output a hex-dump form — researcher picks.
- **Host rightmost-prefix discipline** (serial_comm.py:176-188) — already designed against ghost bytes for text; the binary path inherits the same defensive posture via 4-byte magic.
- **Native test harness** (test/native/avr/test_dispatch/) — template for the codegen-side header-link tests.
- **`tools/build_db.py` in `firestarter_app/`** — precedent for a Python-based codegen tool living in the sub-repo's `tools/` directory. Codegen for messages may follow the same pattern.

### Established Patterns
- **Constants duplicated between Python and firmware** — `constants.py` ↔ `firestarter.h`. The catalog + generated files become the *new* canonical surface for the log-message subset of this duplication; the planner should explicitly note that `messages.py` and `messages.h` replace the per-string `LOG_*_MSG` PROGMEM declarations *for log content*, but command codes and flag bits still duplicate the legacy way.
- **`firestarter_handle_t.response_msg`** — the 96-byte RAM scratch buffer used by today's `log_*_format` macros to render before sending. The new `rurp_log_id` can bypass this buffer entirely — params go directly on the wire as bytes — which is one of the flash-savings mechanisms.
- **PlatformIO `[env:native]`** — host-side unit tests run via `pio test -e native -f "*test_messages*"` should be the LHOST-side gate; mirror the dispatch-test suite's structure.

### Integration Points
- **Host read loop entry** — `SerialCommunicator._read_and_parse_lines` is the single integration point on the host. Today it calls `read_line_bytes()`; the new implementation reads bytes (via `serial.read(1)` or buffered equivalent) and dispatches per D-05.
- **Firmware emit point** — `rurp_log_id` lands in `boards/uno_rurp_shield.cpp` + `boards/leonardo_rurp_shield.cpp` (board-specific) with a shared declaration in `rurp_shield.h`. The frame-emit helper itself can live in `rurp_serial_utils.cpp` as a board-agnostic sibling to `_firestarter_log_ram` / `_firestarter_log_progmem`.
- **CI hook** — both sub-repos get a new "Codegen drift gate" step **before** the `pio run` / `pip install` step in their respective workflows. Drift fails the build with a diff visible in the PR.
- **Host fw-version refuse path** — `firmware.py:check_current_firmware` already extracts the version; the Phase 6 guard adds a major-version comparison and a hard error with an upgrade message. No fallback to text-protocol parsing (lockstep).

</code_context>

<specifics>
## Specific Ideas

- **Operator-supplied constraint (load-bearing):** PORTD on the Uno is dual-purpose — serial TX pins overlap with bus address lines during programming and reading. Address-line toggles can leak as ghost bytes on the serial wire. Any wire-frame design MUST be foolproof against this. The 4-byte magic preamble + length-authoritative + CRC8 + 0x0A re-sync anchor is the operator-validated answer; single-byte sentinels were explicitly rejected.
- The existing text path already survives this hazard via "rightmost-prefix wins" (serial_comm.py:182). The new binary path achieves equivalent defense via the multi-byte magic + CRC; both paths coexist after Phase 6.
- 0xAA 0x55 0xAA 0x55 was preferred over 0xDEADBEEF and 0xFF00FF00 specifically for its maximum bit-transition density — least likely to alias to any single bus-line pattern.

</specifics>

<deferred>
## Deferred Ideas

None — the operator stayed strictly within the wire-frame design space during discussion. No scope creep, no out-of-phase capabilities surfaced.

The three gray areas the operator deliberately skipped (catalog format, param-shape schema, decoder coexistence specifics) are NOT deferred ideas — they are explicit Claude's-Discretion items captured under `<decisions>` for the researcher to flesh out within Phase 6.

</deferred>

---

*Phase: 6-Logging Infrastructure (catalog + codegen + helper + decoder)*
*Context gathered: 2026-05-18*
