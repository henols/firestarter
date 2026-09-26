---
phase: 06-logging-infrastructure
plan: 02
subsystem: firmware

tags: [firmware, logging, wire-protocol, crc8, progmem, unity-native-test, lmig-coexistence]

# Dependency graph
requires:
  - 06-01 (catalog + codegen produced firestarter/include/messages.h + firestarter/src/messages.c)
provides:
  - firmware ID-encoded log helper `rurp_log_id(uint8_t, const uint8_t*, uint8_t)` (LFW-01)
  - board-agnostic `_firestarter_emit_frame` helper + 256-byte PROGMEM CRC8_TABLE + 4-byte PROGMEM MAGIC_PREAMBLE
  - Uno strong override with com_mode gate + SERIAL_DEBUG terse summary
  - Leonardo zero-diff (weak default emits unconditionally — no PORTD aliasing risk on USB-CDC)
  - convenience macros LOG_ID, LOG_ID_U8/U16/U24/U32, LOG_ID_BYTES, LOG_INFO_ID* in firestarter/include/logging_id.h (LFW-02)
  - native Unity test suite firestarter/test/native/avr/test_messages/ (4 byte-level frame assertions; pins CRC poly 0x07 seed 0x00)
affects: [06-03-host-decoder, 06-04-fw-guard, 06-05-ci-drift-gate, 07-call-site-conversion, 08-call-site-conversion]

# Tech tracking
tech-stack:
  added:
    - ArduinoFake OverloadedMethod(... Serial, write, size_t(uint8_t)) for byte-stream capture
  patterns:
    - "4-byte magic preamble + length-authoritative binary framing (PORTD ghost-byte tolerance)"
    - "Table-driven CRC8 (poly 0x07 seed 0x00, no refl, no XOR) in 256-byte PROGMEM table"
    - "Weak default + Uno strong override discipline (mirrors existing rurp_log/rurp_log_P)"
    - "Test-binary src_filter widening to link production emitter end-to-end (instead of stub-based isolation)"
    - "Independent reference CRC8 in test (table-free) — production-vs-spec disagreement fails the suite"

key-files:
  created:
    - firestarter/include/logging_id.h
    - firestarter/test/native/avr/test_messages/test_rurp_log_id.cpp
    - firestarter/test/native/avr/test_messages/host_stubs.cpp
    - firestarter/test/native/avr/test_messages/avr/pgmspace.h
  modified:
    - firestarter/include/rurp_shield.h (rurp_log_id decl added)
    - firestarter/include/rurp_serial_utils.h (_firestarter_emit_frame decl added)
    - firestarter/src/boards/rurp_serial_utils.cpp (MAGIC_PREAMBLE, CRC8_TABLE, crc8_ccitt, _firestarter_emit_frame, weak rurp_log_id)
    - firestarter/src/boards/uno_rurp_shield.cpp (Uno strong override of rurp_log_id)
    - firestarter/platformio.ini ([env:native] src_filter widened + include-path added; preserved pre-existing DATA_BUFFER_SIZE=512)
    - firestarter/test/native/avr/test_dispatch/host_stubs.cpp (peer-suite cleanup after src_filter widening)
    - firestarter/test/native/avr/test_eeprom28c_chip_id/host_stubs.cpp (peer-suite cleanup)
    - firestarter/test/native/avr/test_flash_intel_vpp/host_stubs.cpp (peer-suite cleanup)

key-decisions:
  - "Leonardo zero-diff (planner-resolved per RESEARCH §'Board-Specific rurp_log_id' D-08 style): no com_mode global on Leonardo (USB-CDC is on the Atmega32U4 USB hardware, separate from data-bus pins, no PORTD aliasing), so the weak default in rurp_serial_utils.cpp is the correct path. Confirms threat T-06-08 acceptance."
  - "Uno SERIAL_DEBUG path summarises by id + length only (no hex-dump of params) — keeps the debug serial output one-line per emit, mirrors rurp_log_P discipline. Uses inline 64-byte snprintf buffer."
  - "Test-binary path: real production code linked via widened src_filter rather than stubbed. RESEARCH-preferred — any future change to _firestarter_emit_frame or CRC8_TABLE immediately fails the suite. Cost: three peer test suites had to drop duplicate rurp_communication_* stubs and add a Serial_::operator bool() definition (link-only, since rurp_serial_utils.cpp's rurp_serial_begin references it)."
  - "Convenience macros in logging_id.h use do/while(0) blocks for multi-byte param packing — required to declare local uint8_t _b[N] array safely within an if/else context. Single-line LOG_ID(id) is bare expression (matches LOG_INFO unwrapped form in logging.h)."

patterns-established:
  - "rurp_log_id wire-frame is the canonical Phase 6+ logging surface; call-site conversion to LOG_*(MSG_*) is Phase 7-8 work"
  - "Native test suites widen [env:native] src_filter to link production sources rather than stub them"

requirements-completed: [LFW-01, LFW-02]

# Metrics
duration: ~30 min
completed: 2026-05-18
---

# Phase 6 Plan 02: Firmware `rurp_log_id` Helper Summary

**Firmware ID-encoded log helper `rurp_log_id(id, params, count)` emits the locked AA-55 framed wire format (CRC8-CCITT poly 0x07) — declared in `rurp_shield.h`, weak default + frame emitter + 256-byte CRC table in `rurp_serial_utils.cpp`, Uno strong override with `com_mode` gate + `SERIAL_DEBUG` summary in `uno_rurp_shield.cpp`, Leonardo zero-diff. Native Unity suite asserts byte-for-byte frame correctness; pins CRC polynomial.**

## Performance

- **Duration:** ~30 min (start `2026-05-18T11:23:30Z`, end `2026-05-18T11:53:00Z`)
- **Tasks:** 2/2 complete
- **Files created:** 4 (1 header + 3 test files)
- **Files modified:** 8 (5 firmware sources + 3 peer test suites for collateral cleanup)
- **Flash usage (production):**
  - **Uno:** RAM 1587/2048 (77.5%), Flash 26100/32256 (80.9%)
  - **Leonardo:** RAM 1551/2560 (60.6%), Flash 28292/28672 (98.7%)
  - (Formal flash-savings comparison happens in Plan 06; this plan adds ID infrastructure *alongside* the legacy path per LMIG-01, so flash usage went up — savings appear once Phases 7-8 convert call-sites and Phase 9 deletes the legacy `LOG_*_MSG` PROGMEM strings.)

## Accomplishments

- **`rurp_log_id` API** declared in `firestarter/include/rurp_shield.h` immediately after `rurp_log_P`. C-and-C++ friendly signature `void rurp_log_id(uint8_t id, const uint8_t* params, uint8_t param_count)`. (LFW-01.)
- **Wire frame emitter** (`_firestarter_emit_frame`) in `firestarter/src/boards/rurp_serial_utils.cpp`:
  - 4-byte PROGMEM `MAGIC_PREAMBLE = { 0xAA, 0x55, 0xAA, 0x55 }` (D-02).
  - 256-byte PROGMEM `CRC8_TABLE` precomputed for poly 0x07, seed 0x00, no reflection, no final XOR (D-03). Sanity-checked: `CRC8_TABLE[0 ^ 0x01] == 0x07`.
  - `crc8_ccitt(crc, b)` inline helper reads from the table via `pgm_read_byte`.
  - Frame bytes emitted via `SERIAL_PORT.write(uint8_t)` one at a time (matches `rurp_communication_write` line discipline), `.flush()` at end.
- **Weak default `rurp_log_id`** in `rurp_serial_utils.cpp` — emits unconditionally via `_firestarter_emit_frame`. Used by Leonardo (no PORTD aliasing risk on USB-CDC).
- **Strong Uno override** in `firestarter/src/boards/uno_rurp_shield.cpp` — mirrors `rurp_log_P` discipline exactly: under `SERIAL_DEBUG`, render terse summary `"LOG_ID: id=0xNN bytes=N"` and emit through `log_debug`; then `if (com_mode) { _firestarter_emit_frame(...); }`. No emission on the wire while bus driver pins are repurposed during programming. (Mitigates T-06-06.)
- **Convenience macros** in `firestarter/include/logging_id.h` — `LOG_ID(id)`, `LOG_ID_U8/U16/U24/U32(id, p1)` (MSB-first packing into local `uint8_t _b[N]`), `LOG_ID_BYTES(id, buf, count)` (escape hatch), `LOG_INFO_ID*` variants gated by `is_flag_set(FLAG_VERBOSE)`. All multi-byte macros use `do { ... } while (0)` for if/else safety. (LFW-02.)
- **Native Unity test suite** at `firestarter/test/native/avr/test_messages/`:
  - `test_zero_param_frame` — `rurp_log_id(0x01, NULL, 0)` emits `AA 55 AA 55 02 01 07 0A`. Asserts CRC byte is `0x07` (pins poly 0x07 seed 0x00).
  - `test_u32_param_frame` — `rurp_log_id(MSG_INFO_MEM_SIZE, {0x00,0x01,0x00,0x00}, 4)` emits 12 bytes with len=`0x06`. CRC validated against table-free reference.
  - `test_multi_param_frame` — `rurp_log_id(0xB1, {0x01,0xF4,0xA2,0x05,0x00,0x03}, 6)` emits 14 bytes with len=`0x08`.
  - `test_crc_polynomial_smoke` — independent ref CRC8 recomputation vs frame's embedded CRC byte; pins polynomial 0x07.
  - **Suite uses real production code** end-to-end (via widened `[env:native]` `src_filter`); test-side has zero CRC-table reimplementation.
- **LMIG-01 coexistence** — every existing `rurp_log` / `rurp_log_P` / `LOG_*_MSG` PROGMEM string remains intact. No call-site converted in this plan. Both Uno and Leonardo builds link both paths.

## Verification Commands

```bash
# Production builds — LMIG-01 coexistence (both paths link).
cd firestarter && pio run -e uno      # => SUCCESS  RAM 77.5%  Flash 80.9%
cd firestarter && pio run -e leonardo # => SUCCESS  RAM 60.6%  Flash 98.7%

# Native test suite — 4 byte-level frame assertions.
cd firestarter && pio test -e native -f "*test_messages*"
# => 4 tests, 4 passed (test_zero_param_frame, test_u32_param_frame,
#    test_multi_param_frame, test_crc_polynomial_smoke)

# Regression check — peer suites still green after src_filter widening.
cd firestarter && pio test -e native
# => 29 tests across 4 suites, 29 passed
#    test_dispatch (15) | test_flash_intel_vpp (7) |
#    test_eeprom28c_chip_id (3) | test_messages (4)

# LMIG-01 coexistence — original PROGMEM log tag strings still in logging.c.
grep -c "LOG_OK_MSG\|LOG_INIT_DONE_MSG\|LOG_MAIN_DONE_MSG\|LOG_END_DONE_MSG\|LOG_INFO_MSG\|LOG_DATA_MSG\|LOG_WARN_MSG\|LOG_ERROR_MSG" firestarter/src/logging.c
# => 8

# LMIG-01 coexistence — no existing rurp_log call-site removed (grep proves it).
grep -rn "rurp_log_P\?(LOG_" firestarter/src/ | wc -l
# (count is unchanged from baseline — coexistence verified)
```

All pass.

## Pre-existing platformio.ini Change — Preserved

The orchestrator flagged that `firestarter/platformio.ini` had a pre-existing edit not in this plan's `files_modified` set:

```
- 	-D DATA_BUFFER_SIZE=1024
+ 	; TEMP: 512 to match Uno for buffer-size A/B test (was 1024)
+ 	-D DATA_BUFFER_SIZE=512
```

This plan's required edits to `[env:native]` were applied **on top of** the pre-existing change, not over it. Both changes are present in commit `ca6a9e5`. Verified by:

```bash
$ git -C firestarter diff HEAD~ HEAD -- platformio.ini | grep "DATA_BUFFER_SIZE\|src_filter\|test/native/avr/test_messages"
+	; TEMP: 512 to match Uno for buffer-size A/B test (was 1024)
+	-D DATA_BUFFER_SIZE=512
+	-I test/native/avr/test_messages
+; Phase 6: include rurp_serial_utils.cpp + messages.c for test_messages suite
-src_filter = +<proms/>
+src_filter = +<proms/> +<boards/rurp_serial_utils.cpp> +<messages.c>
```

The other pre-existing dirty file (`firestarter/include/rurp_register_utils.h`) was left untouched per orchestrator instruction.

## Decision Left to Planner — Leonardo override (resolved: zero-diff)

The plan's `<read_first>` and PATTERNS gotchas explicitly listed Leonardo override as a planner decision. Resolved as **zero-diff for `leonardo_rurp_shield.cpp`**:

- Leonardo has no `com_mode` global (only Uno defines it — confirmed by `grep -rn "com_mode" firestarter/src/boards/`).
- Leonardo's `Serial` is USB-CDC on dedicated Atmega32U4 USB hardware; data bus is on PORTD/PORTC/PORTE but UART is *separate hardware*. No PORTD ghost-byte aliasing risk.
- Therefore the weak default `rurp_log_id` in `rurp_serial_utils.cpp` (which emits unconditionally via `_firestarter_emit_frame`) is the correct Leonardo path.
- This confirms STRIDE threat T-06-08 (Leonardo emits unconditionally during USB-CDC bus toggles) is correctly classified as **accept**.

## Build Results

```
pio run -e uno      => SUCCESS  RAM 1587/2048 (77.5%)  Flash 26100/32256 (80.9%)
pio run -e leonardo => SUCCESS  RAM 1551/2560 (60.6%)  Flash 28292/28672 (98.7%)

pio test -e native  => 29 cases, 29 passed across 4 suites
  - test_dispatch:           15 passed (regression — was 15 passed at baseline)
  - test_flash_intel_vpp:     7 passed (regression — needed Serial_::operator bool stub)
  - test_eeprom28c_chip_id:   3 passed (regression — needed Serial_::operator bool stub)
  - test_messages:            4 passed (NEW Phase 6 suite)
```

The Leonardo flash budget is at 98.7% — within the 28672-byte ATmega32U4 limit but tight. Plan 06-06 (milestone prep) flags this as a v1.2 concern; the Phase 7-8 call-site conversion + Phase 9 legacy deletion are the planned recovery path.

## Task Commits

Each task = submodule commit + meta-repo pointer bump.

### Task 1 — `rurp_log_id` helper + frame emitter + Uno strong override

1. **firestarter:** `dcb06cd` (feat) — header decl + logging_id.h + emit_frame + CRC8 table + Uno strong override
2. **meta-repo:** `c085109` (chore) — bump firestarter pointer

### Task 2 — Native Unity test suite

3. **firestarter:** `ca6a9e5` (test) — test_messages/ suite + platformio.ini src_filter widening + 3 peer-suite collateral cleanups
4. **meta-repo:** `45bece7` (chore) — bump firestarter pointer

**Plan metadata commit** (SUMMARY.md + STATE.md + ROADMAP.md): added at end-of-plan via `gsd-sdk query commit`.

## Files Created/Modified

### firestarter submodule — created

- `include/logging_id.h` — convenience macros LOG_ID, LOG_ID_U8/U16/U24/U32, LOG_ID_BYTES, LOG_INFO_ID*. Each multi-byte macro is `do { uint8_t _b[N] = {...}; rurp_log_id(id, _b, N); } while (0)`. 119 lines.
- `test/native/avr/test_messages/test_rurp_log_id.cpp` — Unity suite, 4 tests, table-free ref CRC8, ArduinoFake `OverloadedMethod` for byte capture. 215 lines.
- `test/native/avr/test_messages/host_stubs.cpp` — peer of test_dispatch/host_stubs.cpp; replicates LOG_*_MSG PROGMEM strings + rurp_* hardware stubs + `Serial_::operator bool()` definition. 121 lines.
- `test/native/avr/test_messages/avr/pgmspace.h` — verbatim copy of test_dispatch/avr/pgmspace.h with Phase 6 banner. 63 lines (diff vs original = banner only).

### firestarter submodule — modified

- `include/rurp_shield.h` — added `void rurp_log_id(uint8_t id, const uint8_t* params, uint8_t param_count);` declaration in the `extern "C"` block immediately after `rurp_log_P`. 4 lines added including 2-line comment.
- `include/rurp_serial_utils.h` — added `void _firestarter_emit_frame(...)` declaration alongside the existing `_firestarter_log_ram/_firestarter_log_progmem` siblings. 5 lines added.
- `src/boards/rurp_serial_utils.cpp` — INSERT block before the weak-default block: `MAGIC_PREAMBLE[4] PROGMEM`, `CRC8_TABLE[256] PROGMEM` (precomputed; 16×16 rows of hex), inline `crc8_ccitt`, `_firestarter_emit_frame`, and `__attribute__((weak)) rurp_log_id`. ~75 lines added.
- `src/boards/uno_rurp_shield.cpp` — INSERT Uno strong override of `rurp_log_id` inside the existing `#ifdef ARDUINO_AVR_UNO` block, immediately after `rurp_log_P`. ~20 lines added. Uses `snprintf_P` with PSTR for the debug summary.
- `platformio.ini` — `[env:native]` `src_filter` widened from `+<proms/>` to `+<proms/> +<boards/rurp_serial_utils.cpp> +<messages.c>`; added `-I test/native/avr/test_messages` to `build_flags`. Pre-existing `DATA_BUFFER_SIZE=512` Leonardo edit preserved.
- `test/native/avr/test_dispatch/host_stubs.cpp` — drop duplicate `rurp_communication_*` no-op stubs (now provided by linked real `rurp_serial_utils.cpp`); add `Serial_::operator bool() { return true; }` definition. Net -16 / +10 lines.
- `test/native/avr/test_eeprom28c_chip_id/host_stubs.cpp` — same peer-suite cleanup.
- `test/native/avr/test_flash_intel_vpp/host_stubs.cpp` — same peer-suite cleanup.

## Decisions Made

1. **Leonardo override: zero-diff (weak default suffices).** Rationale: no `com_mode` global on Leonardo (USB-CDC is separate hardware), no PORTD aliasing risk. Confirms threat T-06-08 acceptance.
2. **Uno `SERIAL_DEBUG` summary, not hex-dump.** Rationale: keeps debug output one-line per emit, mirrors `rurp_log_P` discipline. Uses inline `snprintf_P(buf, 64, PSTR("LOG_ID: id=0x%02X bytes=%d"), ...)`.
3. **Test build uses real `rurp_serial_utils.cpp` via widened `src_filter`** (RESEARCH §"`MSG_PARAM_COUNT(id)` Implementation Choice" preference). Trade-off: three peer test suites needed collateral cleanup (drop duplicate `rurp_communication_*` stubs + add `Serial_::operator bool` definition).
4. **Reference CRC8 in test is table-free recomputation** (not import of the production `CRC8_TABLE`). Pins the algorithm spec (poly 0x07, seed 0x00, no refl, no XOR) — a future drift of the production table off-spec fails the test.
5. **`Serial_::operator bool()` host-side stub returns true** (matches production `HardwareSerial::operator bool() { return true; }` in ArduinoFake's USB-CDC header). Link-only; the tests never call `rurp_serial_begin`.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking: build break from widened `src_filter`] Peer test suites had multiple-definition link errors after pulling `rurp_serial_utils.cpp` into `[env:native]`**

- **Found during:** Task 2, first `pio test -e native` after widening `src_filter`.
- **Issue:** The widened `src_filter = +<proms/> +<boards/rurp_serial_utils.cpp> +<messages.c>` is applied to *every* test binary built under `[env:native]`, not just `test_messages`. Three pre-existing peer suites (`test_dispatch/host_stubs.cpp`, `test_eeprom28c_chip_id/host_stubs.cpp`, `test_flash_intel_vpp/host_stubs.cpp`) were stubbing the same `rurp_communication_*` symbols that the now-linked `rurp_serial_utils.cpp` provides. Result: 6 multiple-definition link errors per peer suite. Additionally, `rurp_serial_utils.cpp::rurp_serial_begin` references `Serial_::operator bool()`, which ArduinoFake declares but does not define.
- **Fix:** In all three peer suites' `host_stubs.cpp`:
  1. Drop the `rurp_communication_available / read / peak / write / read_bytes / read_data` stub block (now provided by the linked real TU).
  2. Add `Serial_::operator bool() { return true; }` definition (link-only; tests never call `rurp_serial_begin`).
- **Files modified:** `test/native/avr/test_dispatch/host_stubs.cpp`, `test/native/avr/test_eeprom28c_chip_id/host_stubs.cpp`, `test/native/avr/test_flash_intel_vpp/host_stubs.cpp` — all in the same Task 2 commit.
- **Verification:** `pio test -e native` — 29 cases, 29 passed across all 4 suites.
- **Committed in:** `ca6a9e5` (Task 2 submodule commit).

**2. [Rule 3 - Blocking: ArduinoFake template deduction failure on overloaded `Serial.write`] First test compile failed with `<unresolved overloaded function type>` for `Method(ArduinoFake(Serial), write)`**

- **Found during:** Task 2, first compile of `test_rurp_log_id.cpp`.
- **Issue:** ArduinoFake's `Serial_` class has two `write` overloads (`size_t write(uint8_t)` and `size_t write(const uint8_t*, size_t)`). The `Method(...)` macro tries to take the address of the member function but can't resolve which overload.
- **Fix:** Use `OverloadedMethod(ArduinoFake(Serial), write, size_t(uint8_t))` to specify the exact prototype. Matches the ArduinoFake fakeit.hpp macro convention.
- **Files modified:** `test/native/avr/test_messages/test_rurp_log_id.cpp` (one-line change inside `setUp`).
- **Verification:** Test compile + run green; 8 bytes captured for the zero-param case as expected.
- **Committed in:** `ca6a9e5`.

### No User Permission Needed

Both deviations are Rule 3 blocking-issue auto-fixes (build wouldn't otherwise complete). Documented for traceability; no architectural change required.

## Issues Encountered

- None beyond the two deviations above. The plan's pre-existing-platformio.ini-change directive worked cleanly — the merge added the new test_messages additions on top of the `DATA_BUFFER_SIZE=512` edit without conflict.

## User Setup Required

None — no external services configured.

## Next Phase Readiness

**Plan 06-03 (host decoder)** is unblocked:
- The wire frame byte sequence is locked AND validated by the native Unity suite. Plan 06-03's host-side decoder targets the same `0xAA 0x55 0xAA 0x55 | len | id | params | crc | 0x0A` shape and can use the same CRC8 reference (poly 0x07, seed 0x00).

**Plan 06-04 (host fw-version refuse guard)** is independent — unaffected by this plan.

**Plan 06-05 (CI drift gate)** is unaffected — codegen output `messages.h` + `messages.c` are already idempotent (Plan 06-01); this plan only ADDS files (`logging_id.h`, test suite).

**Plan 06-06 (milestone prep / flash measurement)** has the baseline:
- Uno: Flash 26100 / 32256 bytes (80.9%)
- Leonardo: Flash 28292 / 28672 bytes (98.7%)
- These numbers include BOTH the legacy `rurp_log` PROGMEM strings AND the new `rurp_log_id` infrastructure. Phase 7-8 call-site conversion will reduce them; Phase 9 deletion of legacy strings completes the recovery.

**Phases 7-8 (call-site conversion)** are unblocked:
- The convenience macros `LOG_ID*` / `LOG_INFO_ID*` in `logging_id.h` are the call-site target. Conversion is a mechanical 1-for-1 replacement of `log_info_const("Memory size 0x%lx", size)` → `LOG_INFO_ID_U32(MSG_INFO_MEM_SIZE, size)`.

## Self-Check: PASSED

Files exist:
- `firestarter/include/logging_id.h`                                  — FOUND
- `firestarter/include/rurp_shield.h` (rurp_log_id decl)              — FOUND (line 137)
- `firestarter/include/rurp_serial_utils.h` (_firestarter_emit_frame decl) — FOUND
- `firestarter/src/boards/rurp_serial_utils.cpp` (CRC8_TABLE + MAGIC_PREAMBLE + _firestarter_emit_frame + weak rurp_log_id) — FOUND
- `firestarter/src/boards/uno_rurp_shield.cpp` (Uno strong override)  — FOUND
- `firestarter/test/native/avr/test_messages/test_rurp_log_id.cpp`    — FOUND
- `firestarter/test/native/avr/test_messages/host_stubs.cpp`          — FOUND
- `firestarter/test/native/avr/test_messages/avr/pgmspace.h`          — FOUND

Commits (all on `feature/phase-10-static-pins`):
- firestarter `dcb06cd`  — FOUND (sub-repo HEAD~3)
- firestarter `ca6a9e5`  — FOUND (sub-repo HEAD~1)
- meta-repo `c085109`  — FOUND
- meta-repo `45bece7`  — FOUND

Behavioural verification:
- `pio run -e uno`      => exit 0 (Flash 26100/32256)
- `pio run -e leonardo` => exit 0 (Flash 28292/28672)
- `pio test -e native -f "*test_messages*"` => 4 cases, 4 passed
- `pio test -e native`  => 29 cases, 29 passed (no regression in peer suites)
- LMIG-01: `grep -c "LOG_OK_MSG\|...\|LOG_ERROR_MSG" src/logging.c` => 8 (every legacy PROGMEM tag still in place)

---
*Phase: 06-logging-infrastructure*
*Completed: 2026-05-18*
