---
phase: 88-golden-traces-dispatch-mirror-guard-was-87
plan: 03
subsystem: testing
tags: [unity, native, golden-trace, recording-bus, flash3, flash4, prim-01, safe-02, inv-04, inv-09]

requires:
  - phase: 88-golden-traces-dispatch-mirror-guard-was-87
    plan: 01
    provides: _shared/golden_trace.h assert_trace_eq() helper

provides:
  - "golden_flash3_write.inc: pinned 12-entry (reg,data) trace for flash3 0x06 AMD/SST unlock write"
  - "golden_flash4_write.inc: pinned 206-entry (reg,data) trace for flash4 0x05 write (65-byte INV-04 probe)"
  - "golden_flash4_chip_id.inc: pinned 16-entry (reg,data) trace for flash4 chip-id (P4 via flash_utils)"
  - "test_val_flash3.cpp extended with 1 golden write test wired in main() RUN_TEST"
  - "test_val_flash4.cpp extended with 2 golden tests (write + chip-id) wired in main() RUN_TEST"

affects:
  - 89-primitive-recompose

tech-stack:
  added: []
  patterns:
    - "delay/delayMicroseconds/millis ArduinoFake stubs added to flash3 setUp() for operation-phase tests"
    - "Scripted-byte mock re-assigned AFTER configure_memory() to avoid Pitfall 3 pointer clobber (flash4 chip-id)"
    - "FLAG_SKIP_BLANK_CHECK|FLAG_SKIP_ERASE in golden write tests to suppress init side-effects and isolate execute trace"
    - "65-byte INV-04 minimal probe reused for flash4 write golden trace (D-04 discipline)"

key-files:
  created:
    - firestarter/test/native/avr/test_val_flash3/golden_flash3_write.inc
    - firestarter/test/native/avr/test_val_flash4/golden_flash4_write.inc
    - firestarter/test/native/avr/test_val_flash4/golden_flash4_chip_id.inc
  modified:
    - firestarter/test/native/avr/test_val_flash3/test_val_flash3.cpp
    - firestarter/test/native/avr/test_val_flash4/test_val_flash4.cpp

key-decisions:
  - "flash3 setUp() extended with delay/delayMicroseconds/millis stubs (Pitfall 4) — flash_util_verify_operation calls millis(); ArduinoFakeReset() resets stubs so they must be in setUp()"
  - "flash4 chip-id uses chip_id=0xBFB7 (SST39SF040 mfr+dev), scripted mock returns matching bytes; no error path fires"
  - "flash4 write 206-entry trace: 8 SDP + 195 set_data (65×3) + 3 poll = 206 < 256 cap (D-04 guard satisfied)"
  - "flash4 chip-id 16-entry trace: FLASH_ENABLE_ID (8) + FLASH_DISABLE_ID (8); scripted mock reads bypass rurp_write_to_register — 0 entries from get_data calls"
  - "flash3 12-entry trace: FLASH_ENABLE_WRITE SDP (8 entries) + memory_set_data (2 entries: LSB+MSB, CTL via mem_util_remap_address) + flash_util_verify_operation CTL (1 entry: CTRL_READ_WRITE set) + CTL cleanup (1 entry)"

patterns-established:
  - "Pattern: millis() stub required in setUp() for any suite that drives flash_util_verify_operation (flash3 write path)"
  - "Pattern: FLAG_SKIP_BLANK_CHECK|FLAG_SKIP_ERASE isolates execute-only trace in golden write tests across all families"

requirements-completed: [PRIM-01, SAFE-02]

duration: 20min
completed: 2026-06-26
---

# Phase 88 Plan 03: Golden Traces — Flash3 + Flash4 Families Summary

**Byte-exact golden register traces pinned for flash3 0x06 write and flash4 0x05 write + chip-id; all suite tests (6 + 11) pass with INV-04 and INV-09 intact**

## Performance

- **Duration:** ~20 min
- **Started:** 2026-06-26T09:40:00Z
- **Completed:** 2026-06-26T10:00:00Z
- **Tasks:** 2 of 2
- **Files modified:** 5

## Accomplishments

- Extended `test_val_flash3.cpp` with `test_golden_flash3_write`: 1-byte AMD/SST unlock write trace, delay/delayMicroseconds/millis stubs added to setUp(), 12-entry golden_flash3_write.inc pinned — all 6 tests pass including INV-09
- Extended `test_val_flash4.cpp` with `test_golden_flash4_write` (65-byte INV-04 probe, 206 entries) and `test_golden_flash4_chip_id` (scripted-byte mock, 16 entries) — all 11 tests pass including INV-04
- Confirmed no flash3 chip-id fixture authored (flash3 is NOT a P4 chip-id site per D-03 coverage map)
- All acceptance criteria verified: INV-04 and INV-09 present, no spurious fixtures, correct RUN_TEST wiring

## Task Commits (in firestarter submodule)

1. **Task 1: flash3 0x06 write golden trace** — `1282c32` (feat)
2. **Task 2: flash4 0x05 write + chip-id golden traces** — `e6cce3e` (feat)

## Files Created/Modified

- `firestarter/test/native/avr/test_val_flash3/test_val_flash3.cpp` — Added golden_trace.h include, setUp() delay/delayMicroseconds/millis stubs, golden_flash3_write[] array, test_golden_flash3_write() function, RUN_TEST entry
- `firestarter/test/native/avr/test_val_flash3/golden_flash3_write.inc` — 12 entries; flash3 0x06 1-byte write trace (AMD/SST SDP unlock sequence + set_data + DQ7 verify)
- `firestarter/test/native/avr/test_val_flash4/test_val_flash4.cpp` — Added golden_trace.h include, golden array declarations, scripted-byte mock, test_golden_flash4_write() + test_golden_flash4_chip_id() functions, 2 RUN_TEST entries
- `firestarter/test/native/avr/test_val_flash4/golden_flash4_write.inc` — 206 entries; flash4 0x05 65-byte probe write trace (1 SDP + 65×set_data + 1 poll)
- `firestarter/test/native/avr/test_val_flash4/golden_flash4_chip_id.inc` — 16 entries; flash4 P4 chip-id trace (FLASH_ENABLE_ID + FLASH_DISABLE_ID, scripted mock reads generate 0 register writes)

## Decisions Made

- flash3 setUp() needed `delay`, `delayMicroseconds`, and `millis` stubs added — the existing configure-only tests didn't need them but `flash_util_verify_operation` (called from flash3_write_execute) calls `millis()` for the DQ7 poll timeout
- flash4 chip-id scripted bytes chosen as {0xBF, 0xB7} = SST39SF040 manufacturer/device ID; chip_id=0xBFB7 matches so no error path fires; 5 entries from the two FLASH_ENABLE/DISABLE_ID sequences + 0 from scripted mock reads
- flash4 write: FLAG_SKIP_BLANK_CHECK|FLAG_SKIP_ERASE suppress flash4_write_init side-effects; driving init+main means init is a no-op and the trace is purely flash4_write_execute
- 206-entry flash4 write trace satisfies D-04 (< 256 cap): anti-truncation guard in assert_trace_eq confirmed not tripped

## Deviations from Plan

None — plan executed exactly as written.

## Issues Encountered

One deviation encountered and resolved automatically (Rule 3 auto-fix): flash3's existing setUp() lacked `millis()` stub required by `flash_util_verify_operation`. Added alongside the existing `delay`/`delayMicroseconds` stubs. This is a missing-stub issue, not a production code change.

## Threat Flags

None — no new network endpoints, auth paths, file access patterns, or schema changes introduced. This plan adds test-only files under `test/native/` and the `_shared/` test header; no production firmware source was modified (D-08 flash delta unaffected).

## Self-Check

- [x] `firestarter/test/native/avr/test_val_flash3/golden_flash3_write.inc` exists: FOUND (12 entries)
- [x] `firestarter/test/native/avr/test_val_flash4/golden_flash4_write.inc` exists: FOUND (206 entries)
- [x] `firestarter/test/native/avr/test_val_flash4/golden_flash4_chip_id.inc` exists: FOUND (16 entries)
- [x] `pio test -e native -f "*test_val_flash3*"` exits 0: CONFIRMED (6/6 passed)
- [x] `pio test -e native -f "*test_val_flash4*"` exits 0: CONFIRMED (11/11 passed)
- [x] `RUN_TEST(test_golden_flash3_write)` — 1 match: CONFIRMED
- [x] `RUN_TEST(test_golden_flash4_write)` and `RUN_TEST(test_golden_flash4_chip_id)` — 2 matches: CONFIRMED
- [x] INV-09 assertion present in test_val_flash3.cpp: CONFIRMED
- [x] INV-04 assertion present in test_val_flash4.cpp: CONFIRMED
- [x] No `golden_flash3_chip_id.inc` file (flash3 not a P4 site): CONFIRMED (no such file)
- [x] Commits 1282c32 and e6cce3e exist in firestarter submodule: CONFIRMED

## Self-Check: PASSED

---
*Phase: 88-golden-traces-dispatch-mirror-guard-was-87*
*Completed: 2026-06-26*
