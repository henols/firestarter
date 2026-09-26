---
phase: 71-validation-harness-matrix
plan: "05"
subsystem: validation-tier2-wire-roundtrip
tags:
  - validation
  - tier2
  - wire-roundtrip
  - dispatch
  - sram-safety
  - harn-01
dependency_graph:
  requires:
    - 71-02
  provides:
    - test_val_wire_eprom.py (Tier-2 eprom family wire round-trip)
    - test_val_wire_eeprom28c.py (Tier-2 eeprom28c family wire round-trip)
    - test_val_wire_flash3.py (Tier-2 flash3 family wire round-trip)
    - test_val_wire_flash4.py (Tier-2 flash4 family wire round-trip)
    - test_val_wire_flash_intel.py (Tier-2 flash_intel family wire round-trip)
    - test_val_wire_sram.py (Tier-2 sram family wire round-trip + BLOCKER-2 safety assertion)
  affects:
    - firestarter_app/tests/ (6 new Tier-2 test files)
    - firestarter_app/tools/validation_matrix_spec.json (flash4 rep_chip corrected)
tech_stack:
  added: []
  patterns:
    - Tier-2 host wire round-trip (EpromDatabase.convert_to_programmer + dispatch(), no serial)
    - Single-source-of-truth rep_chip from validation_matrix_spec.json
    - BLOCKER-2 safety assertion (SRAM never routes to configure_eprom)
key_files:
  created:
    - firestarter_app/tests/test_val_wire_eprom.py
    - firestarter_app/tests/test_val_wire_eeprom28c.py
    - firestarter_app/tests/test_val_wire_flash3.py
    - firestarter_app/tests/test_val_wire_flash4.py
    - firestarter_app/tests/test_val_wire_flash_intel.py
    - firestarter_app/tests/test_val_wire_sram.py
  modified:
    - firestarter_app/tools/validation_matrix_spec.json
decisions:
  - D-10 honored: rep_chip sourced from validation_matrix_spec.json in every test file (single source of truth)
  - D-10 honored: wire dicts built via EpromDatabase.convert_to_programmer(), dispatch via check_dispatch.dispatch() — no hand-rolled JSON or dispatch mirrors
  - flash4 rep_chip corrected to AT29C040 (SST39SF040 has algo=6 = flash3, not flash4)
  - SRAM test adds extra safety assertions (BLOCKER-2 + _SRAM_PROTOCOLS membership)
metrics:
  duration: ~15min
  completed: 2026-06-16
  tasks_completed: 2
  tasks_total: 2
  files_created: 6
  files_modified: 1
---

# Phase 71 Plan 05: Tier-2 Host Wire Round-Trip Suites Summary

**One-liner:** Six pytest wire round-trip suites prove each family's rep chip (from the
authored matrix spec) builds the correct algorithm field and dispatches to the correct
handler without a serial port, reusing the production converter + dispatch.

## What Was Built

### Task 1: Tier-2 Wire Round-Trips for EPROM + EEPROM28c + Flash Families

Five test files, each loading its rep chip from `tools/validation_matrix_spec.json`
and asserting two invariants via the production pipeline:

| File | Rep Chip | Expected Algorithm | Expected Handler |
|------|----------|--------------------|-----------------|
| test_val_wire_eprom.py | W27C512 | 7 (0x07) | configure_eprom |
| test_val_wire_eeprom28c.py | AT28C256 | 13 (0x0D) | configure_eeprom28c |
| test_val_wire_flash3.py | AM29F040 | 6 (0x06) | configure_flash3 |
| test_val_wire_flash4.py | AT29C040 | 5 (0x05) | configure_flash4 |
| test_val_wire_flash_intel.py | AM28F010 | 16 (0x10) | configure_flash_intel |

Each test file contains 4 tests:
1. `test_*_rep_chip_sourced_from_spec` — validates spec field is non-empty string
2. `test_*_wire_dict_has_algorithm_field` — wire dict contains "algorithm" key (uses make_comm/fake_serial)
3. `test_*_wire_dict_algorithm_in_family_protocols` — algorithm matches family's protocol set (uses make_comm/fake_serial)
4. `test_*_wire_dict_dispatches_to_configure_*` — dispatch(algo, type) == expected handler (uses make_comm/fake_serial)

Wire dicts are built via `EpromDatabase.convert_to_programmer(db.get_eprom(rep_chip))`.
Dispatch is via `tools.check_dispatch.dispatch(algo, mem_type)`.
No serial I/O; make_comm/fake_serial fixtures confirm the no-port posture.

### Task 2: Tier-2 Wire Round-Trip for SRAM (BLOCKER-2 Safety)

`test_val_wire_sram.py` — 6 tests for the 6116 SRAM rep chip:

1. `test_sram_rep_chip_sourced_from_spec` — spec field validation
2. `test_sram_wire_dict_has_algorithm_field` — wire dict has "algorithm" key
3. `test_sram_wire_dict_algorithm_in_sram_protocols` — algo in {14, 39, 40, 41}
4. `test_sram_wire_dict_dispatches_to_configure_sram` — dispatch == "configure_sram"
5. `test_sram_wire_dict_never_dispatches_to_configure_eprom` — dispatch != "configure_eprom" (BLOCKER-2)
6. `test_sram_algorithm_is_in_sram_protocols_set` — algo in check_dispatch._SRAM_PROTOCOLS

The BLOCKER-2 assertion explicitly guards the hardware-destruction path:
configure_eprom asserts the 12V VPP boost regulator on write — a 5V SRAM part (6116)
would be electrically destroyed if routed to configure_eprom.

## Verification Results

```
pytest tests/test_val_wire_eprom.py tests/test_val_wire_eeprom28c.py \
    tests/test_val_wire_flash3.py tests/test_val_wire_flash4.py \
    tests/test_val_wire_flash_intel.py -x -q
20 passed in 0.2s

pytest tests/test_val_wire_sram.py -x -q
6 passed in 0.1s

ruff check tests/test_val_wire_*.py
All checks passed!

ruff format --check tests/test_val_wire_*.py
6 files already formatted

pytest tests/ --cov=firestarter --cov-fail-under=70 -q
595 passed in 26.19s
Total coverage: 76.27%  (Required: 70%)
```

## Commits

| Submodule | Hash | Subject |
|-----------|------|---------|
| firestarter_app | cddd66e | test(71-05): add failing Tier-2 wire round-trip tests for all 6 families (RED) |
| firestarter_app | 870bb52 | feat(71-05): fix flash4 rep_chip + make all 6 Tier-2 wire tests GREEN |

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed flash4 rep_chip in validation_matrix_spec.json**
- **Found during:** Task 1 TDD RED phase
- **Issue:** The authored spec (from Plan 02) set flash4 `rep_chip: SST39SF040`, but
  SST39SF040 has `algorithm=6` (configure_flash3 via FLASH_AMD_ALT) in chip_database.json.
  Flash4 protocols are {5, 53, 57} (0x05/0x35/0x39, FLASH_AMD_STD variants). The test
  correctly failed: `wire algorithm 6 for 'SST39SF040' not in expected flash4 protocols {5, 53, 57}`.
- **Fix:** Updated `validation_matrix_spec.json` flash4 entry: `rep_chip` and `tier3.test_chip`
  changed from `SST39SF040` to `AT29C040` (ATMEL, algo=5, supported, dispatch → configure_flash4).
- **Files modified:** `firestarter_app/tools/validation_matrix_spec.json`
- **Commit:** 870bb52
- **Impact:** Drift gate (test_gen_validation_header.py) unaffected — the C++ header generator
  only uses `protocols`, `id`, and `handler` fields; `rep_chip`/`tier3.test_chip` are not emitted.

## Known Stubs

None. All 6 test files are fully functional with real production pipeline calls.

## Threat Flags

None. No new network endpoints, auth paths, file access patterns, or schema changes at
trust boundaries. The SRAM safety assertion (T-71-SRAM-EPROM) is the threat mitigation
as specified in the plan's threat register — it is now proven by test.

## TDD Gate Compliance

- RED gate: commit cddd66e (test(71-05): ...) — 6 test files created, flash4 test fails RED
- GREEN gate: commit 870bb52 (feat(71-05): ...) — spec corrected, all 26 tests pass

## Self-Check: PASSED
