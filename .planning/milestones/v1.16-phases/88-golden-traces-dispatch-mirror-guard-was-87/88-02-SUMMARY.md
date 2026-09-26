---
phase: 88-golden-traces-dispatch-mirror-guard-was-87
plan: 02
subsystem: testing
tags: [unity, native, golden-trace, recording-bus, eeprom28c, flash_intel, prim-01, safe-02]

requires:
  - phase: 88-golden-traces-dispatch-mirror-guard-was-87
    provides: "_shared/golden_trace.h: assert_trace_eq() + GOLDEN_BLESS print mode (88-01)"

provides:
  - "golden_eeprom28c_write.inc: pinned 17-entry (reg,data) trace for eeprom28c 0x0D write (SDP unlock P7 + DQ7 poll P5)"
  - "golden_eeprom28c_chip_id.inc: pinned 17-entry (reg,data) trace for eeprom28c A9-12V chip-id check (P4/P7)"
  - "golden_flash_intel_write.inc: pinned 7-entry (reg,data) trace for flash_intel 0x10 write (VPP-gate P3)"
  - "golden_flash_intel_chip_id.inc: pinned 6-entry (reg,data) trace for flash_intel CMD_CHECK_CHIP_ID autoselect (P4)"
  - "test_val_eeprom28c.cpp extended with 2 golden test functions wired in main() RUN_TEST"
  - "test_val_flash_intel.cpp extended with 2 golden test functions + delayMicroseconds/millis() stubs wired in main() RUN_TEST"

affects:
  - 88-03-flash3-and-flash4-golden-traces
  - 89-primitive-recompose
  - phase-89-recompose-oracle

tech-stack:
  added: []
  patterns:
    - "eeprom28c chip-id golden trace uses CMD_WRITE + chip_id>0 (not CMD_CHECK_CHIP_ID): the chip-id path is embedded in eeprom28c_write_init, not a separate dispatch arm"
    - "flash_intel golden write test requires delayMicroseconds + millis() stubs in setUp() to reach operation_main (first time write_execute is called in this suite)"
    - "scripted-byte mock re-assigned AFTER configure_memory() for both chip-id paths (Pitfall 3: configure_memory overwrites get_data pointer)"
    - "millis() mocked to return 0 always; SR poll exits via scripted get_data returning 0x80 (bit7 set → SR ready, no error bits)"

key-files:
  created:
    - firestarter/test/native/avr/test_val_eeprom28c/golden_eeprom28c_write.inc
    - firestarter/test/native/avr/test_val_eeprom28c/golden_eeprom28c_chip_id.inc
    - firestarter/test/native/avr/test_val_flash_intel/golden_flash_intel_write.inc
    - firestarter/test/native/avr/test_val_flash_intel/golden_flash_intel_chip_id.inc
  modified:
    - firestarter/test/native/avr/test_val_eeprom28c/test_val_eeprom28c.cpp
    - firestarter/test/native/avr/test_val_flash_intel/test_val_flash_intel.cpp

key-decisions:
  - "eeprom28c chip-id trace uses CMD_WRITE + chip_id=0x1F08 + operation_init only (not main): eeprom_28c.cpp has no CMD_CHECK_CHIP_ID dispatch arm; the check runs inside write_init when chip_id>0; traces the A9-12V path + SDP unlock"
  - "flash_intel write test needed delayMicroseconds + millis() stubs added to setUp(): write_execute calls memory_set_data which calls delayMicroseconds(3); millis() needed by flash_intel_poll_sr timeout loop"
  - "flash_intel SR poll exited via scripted get_data returning 0x80 (bit7=ready, no error bits); millis always returns 0 so deadline loop runs until SR read succeeds"
  - "golden_flash_intel_chip_id trace is 6 entries (2 set_data calls × 3 writes each): write 0x90 + write 0xFF; reads at 0x0000/0x0001 use get_data which does not write to registers"

patterns-established:
  - "Pattern: when a family has no CMD_CHECK_CHIP_ID dispatch arm (eeprom28c), use CMD_WRITE + chip_id>0 + call operation_init only to isolate the chip-id path golden trace"
  - "Pattern: add delayMicroseconds to setUp() when any golden test calls operation_main (memory_set_data uses delayMicroseconds unconditionally)"
  - "Pattern: flash_intel SR poll exit = scripted get_data 0x80 + millis always-0 (loop enters, reads SR, bit7 set, returns true immediately)"

requirements-completed: [PRIM-01, SAFE-02]

duration: 30min
completed: 2026-06-26
---

# Phase 88 Plan 02: Golden Traces — eeprom28c + flash_intel Families Summary

**Byte-exact golden register traces for eeprom28c 0x0D (SDP unlock P7 + DQ7 poll P5 + A9 chip-id P4) and flash_intel 0x10 (VPP-gate P3 + command-register P4), all 10 suite tests green**

## Performance

- **Duration:** ~30 min
- **Started:** 2026-06-26T09:00:00Z
- **Completed:** 2026-06-26T09:30:00Z
- **Tasks:** 2 of 2
- **Files modified:** 6

## Accomplishments

- Blessed and pinned four golden `.inc` fixtures (eeprom28c write 17-entry, eeprom28c chip-id 17-entry, flash_intel write 7-entry, flash_intel chip-id 6-entry) via GOLDEN_BLESS bless workflow established in 88-01
- Extended `test_val_eeprom28c.cpp` with 2 golden test functions alongside all 3 existing INV/VPP assertions — SAFE-02 intact
- Extended `test_val_flash_intel.cpp` with 2 golden test functions; added `delayMicroseconds` + `millis()` stubs to `setUp()` (required deviation — Rule 2 correctness: write_execute was never called before)
- All 10 suite tests pass (5 eeprom28c + 5 flash_intel); production `flash_intel.cpp` unmodified (D-08)

## Task Commits

1. **Task 1: Bless + pin eeprom28c 0x0D write + chip-id golden traces** — `0b1ce93` (feat)
2. **Task 2: Bless + pin flash_intel 0x10 write + chip-id golden traces** — `fa0f908` (feat)

## Files Created/Modified

- `firestarter/test/native/avr/test_val_eeprom28c/test_val_eeprom28c.cpp` — Added 2 golden test functions, scripted-byte mock, golden array declarations, 2 new RUN_TEST entries; delay/delayMicroseconds stubs already present in setUp
- `firestarter/test/native/avr/test_val_eeprom28c/golden_eeprom28c_write.inc` — 17 entries; eeprom28c 0x0D write init (SDP P7) + execute trace
- `firestarter/test/native/avr/test_val_eeprom28c/golden_eeprom28c_chip_id.inc` — 17 entries; eeprom28c A9-12V chip-id check (P4/P7) via write_init
- `firestarter/test/native/avr/test_val_flash_intel/test_val_flash_intel.cpp` — Added 2 golden test functions, scripted-byte mock, golden array declarations, 2 new RUN_TEST entries; added delayMicroseconds + millis() to setUp
- `firestarter/test/native/avr/test_val_flash_intel/golden_flash_intel_write.inc` — 7 entries; flash_intel 0x10 VPP-gate (P3) init + command-register execute trace
- `firestarter/test/native/avr/test_val_flash_intel/golden_flash_intel_chip_id.inc` — 6 entries; flash_intel CMD_CHECK_CHIP_ID autoselect sequence (P4)

## Decisions Made

- **eeprom28c chip-id uses CMD_WRITE + operation_init only:** `eeprom_28c.cpp` has no `CMD_CHECK_CHIP_ID` case in `configure_eeprom28c`; the check runs inside `eeprom28c_write_init` when `chip_id > 0`. Used `CMD_WRITE + chip_id=0x1F08` + call `operation_init` only to isolate the chip-id + SDP trace. This is exact analog of the `test_eeprom28c_chip_id.cpp` pattern.
- **flash_intel write trace excludes cleanup:** `flash_intel_cleanup` (firestarter_operation_end) is NOT called in the golden write test, consistent with the plan's "drive init then main" instruction. The VPP is left enabled in the trace (P3 gate pinned), matching the Phase 89 extraction target.
- **millis() + scripted SR get_data for poll exit:** millis() always returns 0 (deadline = 0 + 150 = 150; loop enters since 0 < 150); scripted get_data returns 0x80 on first call → bit7 set, no error bits → `flash_intel_poll_sr` returns true immediately. This is the minimal stub to exercise the write execute path without hardware.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Missing Critical] Added delayMicroseconds + millis() stubs to flash_intel setUp()**
- **Found during:** Task 2 (test_golden_flash_intel_write implementation)
- **Issue:** The existing `setUp()` in `test_val_flash_intel.cpp` only mocked `delay()` because prior tests only called `operation_init` (not `operation_main`). Adding `test_golden_flash_intel_write` calls `operation_main` = `flash_intel_write_execute` → `memory_set_data` → `delayMicroseconds(3)` (ArduinoFake aborts on unmocked calls). Also `flash_intel_poll_sr` calls `millis()`. ArduinoFake threw `UnexpectedMethodCallException`.
- **Fix:** Added `When(Method(ArduinoFake(), delayMicroseconds)).AlwaysReturn()` and `When(Method(ArduinoFake(Function), millis)).AlwaysReturn(0)` to `setUp()`. These are correctness requirements for any test that calls `operation_main` on flash_intel.
- **Files modified:** `firestarter/test/native/avr/test_val_flash_intel/test_val_flash_intel.cpp`
- **Verification:** All 5 flash_intel tests pass with the stubs; existing 3 INV/VPP tests unaffected (they don't call `operation_main`)
- **Committed in:** `fa0f908` (Task 2 commit)

---

**Total deviations:** 1 auto-fixed (Rule 2 — missing critical stubs for operation_main path)
**Impact on plan:** Auto-fix necessary for correctness; adds stubs that were always implicitly needed. No scope creep.

## Issues Encountered

None beyond the ArduinoFake stub gap handled in the deviation above. The key insight discovered: `eeprom28c` embeds chip-id check inside `write_init` (not a separate `CMD_CHECK_CHIP_ID` handler), so the chip-id golden trace uses `CMD_WRITE + chip_id>0 + init-only` instead of `CMD_CHECK_CHIP_ID`. This matches the `test_eeprom28c_chip_id.cpp` analog exactly and was anticipated by the patterns doc.

## Threat Flags

None — no new network endpoints, auth paths, file access patterns, or schema changes introduced. This plan adds test-only files under `test/native/` and committed `.inc` fixtures; production firmware source was not modified (D-08 flash delta unaffected).

## Next Phase Readiness

- `golden_trace.h` + eeprom28c + flash_intel fixtures ready for Phase 89 recompose oracle
- 88-03 (flash3 + flash4 golden traces) can proceed immediately; same bless workflow and setUp patterns apply
- eeprom28c chip-id pattern (CMD_WRITE + init-only) documented for Phase 89 extraction of P4/P7 primitives

## Self-Check

- `firestarter/test/native/avr/test_val_eeprom28c/golden_eeprom28c_write.inc` exists: FOUND
- `firestarter/test/native/avr/test_val_eeprom28c/golden_eeprom28c_chip_id.inc` exists: FOUND
- `firestarter/test/native/avr/test_val_flash_intel/golden_flash_intel_write.inc` exists: FOUND
- `firestarter/test/native/avr/test_val_flash_intel/golden_flash_intel_chip_id.inc` exists: FOUND
- Commit 0b1ce93 exists in firestarter submodule: FOUND (Task 1)
- Commit fa0f908 exists in firestarter submodule: FOUND (Task 2)
- `pio test -e native -f "*test_val_eeprom28c*"` exits 0: CONFIRMED (5/5 passed)
- `pio test -e native -f "*test_val_flash_intel*"` exits 0: CONFIRMED (5/5 passed)
- No existing INV/VPP assertions removed: CONFIRMED (3 eeprom28c + 3 flash_intel original tests intact)
- 2 RUN_TEST golden entries per suite: CONFIRMED (lines 270-271 eeprom28c; 306-307 flash_intel)
- flash_intel.cpp unmodified: CONFIRMED (git diff shows no changes)
- Meta gitlinks NOT committed: CONFIRMED (commits in firestarter submodule only)
- config.json NOT touched: CONFIRMED

## Self-Check: PASSED

---
*Phase: 88-golden-traces-dispatch-mirror-guard-was-87*
*Completed: 2026-06-26*
