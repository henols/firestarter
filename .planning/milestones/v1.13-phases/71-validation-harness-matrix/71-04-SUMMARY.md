---
phase: 71-validation-harness-matrix
plan: "04"
subsystem: firmware-native-tests
tags:
  - unity
  - platformio
  - native-tests
  - recording-bus
  - tier1-validation
  - vpp-safety
  - harn-01

# Dependency graph
requires:
  - "71-01 (HOST_STUBS_RECORD_BUS recording API)"
  - "71-02 (validation_matrix.h generated header)"
provides:
  - "6 Tier-1 native Unity suites (one per algorithm family)"
  - "VPP families: eprom 6 tests, flash_intel 3 tests — positive write+init and negative control"
  - "Non-VPP families: eeprom28c 3 tests, flash3 4 tests, flash4 6 tests — configure-phase 5V proof"
  - "SRAM: 6 tests — 4 direct handler (zero-write no-op baseline) + 2 dispatch no-VPP proof"
  - "platformio.ini test_filter and build_flags updated with all 6 suites"
  - "77/77 full native battery passes (8 pre-existing + 6 new suites)"
affects:
  - "firestarter/test/native/avr/ — 6 new suite directories"
  - "firestarter/platformio.ini — test_filter + build_flags extended"

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Tier-1 recording suite pattern: define HOST_STUBS_RECORD_BUS before shared include, declare recording API extern C, call configure_memory + firestarter_operation_init for positive tests"
    - "Negative control via configure-only phase: call configure_memory without init for CMD_READ — proves dispatch phase never enables VPP"
    - "CTRL_VPP_VPE_DROP_ENABLE (0x100 with HARDWARE_REVISION) truncates to 0 in uint8_t recording — assert only 8-bit-fit VPP bits (CTRL_VPP_REGULATOR_ENABLE=0x80, CTRL_VPP_P1_ENABLE=0x08)"
    - "SRAM two-tier test: configure_sram standalone (zero writes) + configure_memory dispatch (no VPP, NULL init)"
    - "HOST_STUBS_CUSTOM_HW_REVISION in VPP suites: default stub returns REVISION_0=0 causing early-return in eprom/flash_intel VPP check; override to return 1 (non-REV0)"

key-files:
  created:
    - "firestarter/test/native/avr/test_val_eprom/test_val_eprom.cpp"
    - "firestarter/test/native/avr/test_val_eprom/host_stubs.cpp"
    - "firestarter/test/native/avr/test_val_flash_intel/test_val_flash_intel.cpp"
    - "firestarter/test/native/avr/test_val_flash_intel/host_stubs.cpp"
    - "firestarter/test/native/avr/test_val_eeprom28c/test_val_eeprom28c.cpp"
    - "firestarter/test/native/avr/test_val_eeprom28c/host_stubs.cpp"
    - "firestarter/test/native/avr/test_val_flash3/test_val_flash3.cpp"
    - "firestarter/test/native/avr/test_val_flash3/host_stubs.cpp"
    - "firestarter/test/native/avr/test_val_flash4/test_val_flash4.cpp"
    - "firestarter/test/native/avr/test_val_flash4/host_stubs.cpp"
    - "firestarter/test/native/avr/test_val_sram/test_val_sram.cpp"
    - "firestarter/test/native/avr/test_val_sram/host_stubs.cpp"
  modified:
    - "firestarter/platformio.ini"

decisions:
  - "D-07 honored: all 6 families have Tier-1 cells GREEN under pio test -e native"
  - "D-08 (verify-can-fail): VPP families include negative-control CMD_READ configure-only tests that go RED if configure_memory/configure_eprom accidentally enables VPP"
  - "Positive tests for VPP families call configure_memory + firestarter_operation_init (mirrors test_flash_intel_vpp.cpp pattern); negative controls call configure_memory alone"
  - "CTRL_VPP_VPE_DROP_ENABLE (0x100 with HARDWARE_REVISION defined) does not fit uint8_t; assertions use CTRL_VPP_REGULATOR_ENABLE and CTRL_VPP_P1_ENABLE only — documented in code comments"
  - "SRAM test uses configure_sram direct call (not configure_memory) for the bus_recording_count()==0 assertion, plus configure_memory dispatch tests for full coverage"
  - "HOST_STUBS_CUSTOM_HW_REVISION required in eprom+flash_intel host_stubs.cpp to prevent REVISION_0 early-return path in eprom_check_vpp/flash_intel_check_vpp"

metrics:
  duration: ~45min
  completed: 2026-06-16
  tasks_completed: 3
  tasks_total: 3
  files_created: 12
  files_modified: 1
---

# Phase 71 Plan 04: Tier-1 Native Validation Suites Summary

**Six Tier-1 native Unity suites prove each family's VPP/non-VPP behavior by
recorded register-write side-effect, with in-tier negative controls for VPP
families and a documented zero-write no-op for SRAM; all 6 suites pass under
`pio test -e native` (77/77 total); zero production flash added.**

## Performance

- **Duration:** ~45 min
- **Started:** 2026-06-16T~13:30Z
- **Completed:** 2026-06-16T~14:15Z
- **Tasks:** 3 (Task 1: 5 suites; Task 2: SRAM suite; Task 3: platformio.ini)
- **Files created:** 12 (test + host_stubs pairs × 6)
- **Files modified:** 1 (platformio.ini)

## Accomplishments

### Task 1: VPP and non-VPP families (5 suites)

**test_val_eprom** (protocols 0x07/0x08/0x0B, 6 tests):
- 3 positive tests: CMD_WRITE + `firestarter_operation_init` call → records
  `CTRL_VPP_REGULATOR_ENABLE` in CTL register (confirmed from eprom.cpp source:
  `eprom_check_vpp` calls `firestarter_set_control_register(handle, CTRL_VPP_REGULATOR_ENABLE | CTRL_VPP_VPE_DROP_ENABLE, 1)`)
- 3 negative controls: CMD_READ configure-only (no init call) → CTRL_VPP_REGULATOR_ENABLE
  never set in recording (D-08 verify-can-fail)

**test_val_flash_intel** (protocol 0x10, 3 tests):
- 2 positive tests: CMD_WRITE + init → records both CTRL_VPP_P1_ENABLE and
  CTRL_VPP_REGULATOR_ENABLE (confirmed from flash_intel.cpp:
  `flash_intel_write_init` line 107: `CTRL_VPP_REGULATOR_ENABLE | CTRL_VPP_P1_ENABLE`)
- 1 negative control: CMD_READ configure-only → no P1 or regulator bits

**test_val_eeprom28c** (protocol 0x0D, 3 tests):
- Configure-phase 5V-only proof for CMD_READ/WRITE/BLANK_CHECK — no VPP-enable CTL bits
- (eeprom28c A9-12V chip-id check is gated by chip_id>0; test sets chip_id=0)

**test_val_flash3** (protocol 0x06, 4 tests):
- Configure-phase 5V-only proof for CMD_READ/WRITE/ERASE/BLANK_CHECK

**test_val_flash4** (protocols 0x05/0x35/0x39, 6 tests):
- Configure-phase 5V-only proof for read+write × 3 protocols
- Note: flash4_erase_execute uses VPP (OE=12V erase), but that is an operation-phase
  VPP use, not a configure-phase use. Configure-only phase is VPP-safe.

### Task 2: SRAM suite (6 tests)

**test_val_sram** (protocols 0x0E/0x27/0x28/0x29, 6 tests):
- 4 direct handler tests: call `configure_sram` standalone → `bus_recording_count() == 0`
  (documents that sram.cpp:15-17 is a pure no-op — Phase 74 FIX-01 will revisit)
- 2 dispatch tests via `configure_memory`: `h.firestarter_operation_init == NULL`
  AND no VPP-enable bits in recording (SRAM never reaches VPP regulator)
- Clear VAL-06 deferral comment in test body

### Task 3: platformio.ini update

- Added 6 `native/avr/test_val_*` entries to `test_filter` allowlist
- Added 6 matching `-I test/native/avr/test_val_*` entries to `build_flags`
- 12 total `test_val_` occurrences in platformio.ini (≥12 required per acceptance criteria)
- Full native battery: 77/77 tests pass (8 pre-existing suites + 6 new suites)
- Production flash unchanged: Leonardo 88.9% (25482/28672 B)

## Task Commits

All commits inside `firestarter/` submodule on `v1.13-algo-validation`:

| # | Hash | Subject |
|---|------|---------|
| 1 | `47fd28f` | `test(71-04): add Tier-1 validation suites for eprom, flash_intel, eeprom28c, flash3, flash4` |
| 2 | `897577c` | `test(71-04): add Tier-1 SRAM validation suite (zero-write no-op baseline)` |
| 3 | `67960c7` | `feat(71-04): register 6 test_val_* suites in platformio.ini allowlist + build_flags` |

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] CTRL_VPP_VPE_DROP_ENABLE overflow in uint8_t recording**
- **Found during:** Task 1 — first test run of test_val_eprom
- **Issue:** When HARDWARE_REVISION is defined, CTRL_VPP_VPE_DROP_ENABLE = 0x100
  (not 0x01). Using it in assertions against the uint8_t recording buffer (which
  stores only the low byte of `rurp_register_t data`) silently truncates to 0x00,
  making the check ineffective and causing a compiler warning.
- **Fix:** Removed CTRL_VPP_VPE_DROP_ENABLE from recording assertions; documented
  in code comments. All 8-bit-fit VPP enable bits (0x80, 0x08) are still checked.
- **Commit:** `47fd28f` (inline with Task 1)

**2. [Rule 2 - Missing critical guard] HOST_STUBS_CUSTOM_HW_REVISION in VPP suites**
- **Found during:** Design analysis of Task 1 eprom/flash_intel suites
- **Issue:** The shared `host_stubs_common.inc` returns REVISION_0=0 by default
  for `rurp_get_hardware_revision()`. Both `eprom_check_vpp` and
  `flash_intel_check_vpp` check `if (rurp_get_hardware_revision() == REVISION_0)`
  and return early WITHOUT writing VPP bits when true. The positive test would fail
  (no VPP bit recorded).
- **Fix:** Added `HOST_STUBS_CUSTOM_HW_REVISION` opt-out in eprom and flash_intel
  `host_stubs.cpp` with a stub returning 1 (non-REV0). Documented in host_stubs.cpp.
- **Commit:** `47fd28f` (inline with Task 1)

**3. [Rule 1 - Deviation] SRAM bus_recording_count() == 0 via direct handler call**
- **Found during:** Task 2 design
- **Issue:** PATTERNS.md example calls `configure_memory(&h)` and asserts
  `bus_recording_count() == 0`. However, `configure_memory` calls
  `mem_util_set_address(handle, 0)` which writes LSB/MSB/CONTROL registers (3 writes)
  even for SRAM. The assertion would be 3, not 0.
- **Fix:** SRAM test uses TWO test categories: (a) direct `configure_sram(&h)` call
  for the zero-write assertion (correct: configure_sram is a LOG-only no-op), plus
  (b) full `configure_memory` dispatch tests for the VPP-safety and NULL-init proof.
  This is strictly more correct and more informative than the PATTERNS.md example.
- **Commit:** `897577c` (inline with Task 2)

## Known Stubs

None. All suites are fully functional and test real production code paths.

## Threat Flags

None. All test files live under `test/` (excluded from production `src_filter`).
Production flash byte-count verified unchanged (Leonardo 88.9% = 25482 B, no delta).
No new network endpoints, auth paths, or schema changes at trust boundaries.

## Verification Results

```
# Individual suite runs
pio test -e native -f "*test_val_eprom*"        → 6/6 PASSED
pio test -e native -f "*test_val_flash_intel*"  → 3/3 PASSED
pio test -e native -f "*test_val_eeprom28c*"    → 3/3 PASSED
pio test -e native -f "*test_val_flash3*"       → 4/4 PASSED
pio test -e native -f "*test_val_flash4*"       → 6/6 PASSED
pio test -e native -f "*test_val_sram*"         → 6/6 PASSED

# Full native battery (all suites including pre-existing)
pio test -e native  → 77/77 PASSED in 44 seconds

# Production flash (unchanged)
pio run -e leonardo → 88.9% (25482 / 28672 B) — delta == 0 vs pre-plan baseline

# platformio.ini allowlist
grep -c "test_val_" platformio.ini → 12 (≥12 required)
```

## Self-Check

- [x] `firestarter/test/native/avr/test_val_eprom/` exists with both files
- [x] `firestarter/test/native/avr/test_val_flash_intel/` exists with both files
- [x] `firestarter/test/native/avr/test_val_eeprom28c/` exists with both files
- [x] `firestarter/test/native/avr/test_val_flash3/` exists with both files
- [x] `firestarter/test/native/avr/test_val_flash4/` exists with both files
- [x] `firestarter/test/native/avr/test_val_sram/` exists with both files
- [x] Commit `47fd28f` exists in `firestarter/` on `v1.13-algo-validation`
- [x] Commit `897577c` exists in `firestarter/` on `v1.13-algo-validation`
- [x] Commit `67960c7` exists in `firestarter/` on `v1.13-algo-validation`
- [x] 77/77 tests pass under `pio test -e native`
- [x] Production flash unchanged: Leonardo 88.9%
- [x] platformio.ini has ≥12 `test_val_` occurrences

## Self-Check: PASSED

---
*Phase: 71-validation-harness-matrix*
*Completed: 2026-06-16*
