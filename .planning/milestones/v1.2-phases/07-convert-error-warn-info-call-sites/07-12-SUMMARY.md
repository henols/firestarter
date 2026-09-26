---
phase: 07-convert-error-warn-info-call-sites
plan: 12
subsystem: firmware
tags: [avr, logging, log-migration, eprom-operations, hardware-operations, LOG_ERROR_ID]

# Dependency graph
requires:
  - phase: 07-convert-error-warn-info-call-sites
    provides: Plan 01 LOG_ERROR_ID macros in logging_id.h; Plan 06 messages.h catalog with MSG_ERR_* IDs

provides:
  - "3 log_error_const sites in eprom_operations.cpp converted to LOG_ERROR_ID(MSG_ERR_*)"
  - "2 log_error_const sites in hardware_operations.cpp converted to LOG_ERROR_ID(MSG_ERR_*)"
affects:
  - phase-07 subsequent plans (wave-3 complete for these two files)
  - phase-09 (LOG_* macro deletion pass — these files now use ID macros only)

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Single-file submodule commit per file for bisectability (plan 07-12 cadence)"

key-files:
  created: []
  modified:
    - firestarter/src/eprom_operations.cpp
    - firestarter/src/hardware_operations.cpp

key-decisions:
  - "No response_code assignments were present at any of the 5 sites — conversion is purely a one-line log macro swap"
  - "#ifdef HARDWARE_REVISION guard around MSG_ERR_REV0_VPP_RD site preserved as-is"

patterns-established:
  - "Direct-log ERROR sites: log_error_const(string) -> LOG_ERROR_ID(MSG_ERR_*); includes added once per file"

requirements-completed: [LMIG-02]

# Metrics
duration: 10min
completed: 2026-05-18
---

# Phase 07 Plan 12: Convert eprom_operations.cpp + hardware_operations.cpp ERROR Sites Summary

**5 trivial log_error_const calls across eprom_operations.cpp and hardware_operations.cpp replaced with LOG_ERROR_ID(MSG_ERR_*) via two per-file submodule commits**

## Performance

- **Duration:** ~10 min
- **Started:** 2026-05-18T00:00:00Z
- **Completed:** 2026-05-18T00:10:00Z
- **Tasks:** 2
- **Files modified:** 2 (firmware submodule)

## Accomplishments

- Converted all 3 `log_error_const` sites in `eprom_operations.cpp` (lines 40, 49, 95) to `LOG_ERROR_ID(MSG_ERR_NOT_SUPPORTED)`, `LOG_ERROR_ID(MSG_ERR_NO_CHIP_ID)`, `LOG_ERROR_ID(MSG_ERR_OUT_OF_RANGE)` — added `#include "logging_id.h"` and `#include "messages.h"`
- Converted 2 `log_error_const` sites in `hardware_operations.cpp` (lines 20, 33) to `LOG_ERROR_ID(MSG_ERR_REV0_VPP_RD)` and `LOG_ERROR_ID(MSG_ERR_CMD)` — `#ifdef HARDWARE_REVISION` guard around line 20 preserved
- Both AVR builds (Uno 77.1% Flash / Leonardo 94.3% Flash) and native dispatch + messages test suites passed (22/24 test cases; 2 pre-existing ERRORED suites unchanged from 07-11 baseline)

## Task Commits

Each task was committed atomically in the submodule:

1. **Task 1: Convert eprom_operations.cpp 3 ERROR sites** - `10d25bb` (feat) — submodule
2. **Task 2: Convert hardware_operations.cpp 2 ERROR sites** - `c3f24e7` (feat) — submodule
3. **Superproject pointer bump** - `9b94dfd` (deps)

**Plan metadata:** TBD (docs commit after SUMMARY)

## Files Created/Modified

- `firestarter/src/eprom_operations.cpp` - Added `logging_id.h`/`messages.h` includes; 3 log_error_const -> LOG_ERROR_ID conversions
- `firestarter/src/hardware_operations.cpp` - Added `logging_id.h`/`messages.h` includes; 2 log_error_const -> LOG_ERROR_ID conversions

## Decisions Made

None - followed plan as specified. No `response_code` assignments were present at any of the 5 sites, so no two-line form was needed.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None. The 2 pre-existing ERRORED native test suites (`test_flash_intel_vpp`, `test_eeprom28c_chip_id`) were confirmed as pre-existing by the 07-11 SUMMARY and unchanged here.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Wave-3 direct-log ERROR conversion is complete for `eprom_operations.cpp` and `hardware_operations.cpp`
- Remaining wave-3 / wave-4 files (`firestarter.cpp`, `operation_utils.cpp`, populate-sites in `proms/*.cpp`) proceed in subsequent plans
- No blockers

---
*Phase: 07-convert-error-warn-info-call-sites*
*Completed: 2026-05-18*
