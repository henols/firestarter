---
phase: 07-convert-error-warn-info-call-sites
plan: 09
subsystem: firmware
tags: [arduino, cpp, logging, operation_utils, breadcrumbs, dispatch]

# Dependency graph
requires:
  - phase: 07-convert-error-warn-info-call-sites plan 01
    provides: LOG_ERROR_ID_* and LOG_INFO_ID_* macros in logging_id.h; MSG_ERR_TIMEOUT, MSG_ERR_DATA_ERR_N, MSG_INFO_MAIN_START, MSG_INFO_MAIN_DONE, MSG_INFO_INIT_START, MSG_INFO_END_START IDs in messages.h
provides:
  - operation_utils.cpp with 6 direct-log call-sites converted to LOG_*_ID_* macros
  - _check_response WARNING+ERROR case bodies stripped of log calls; OK+DATA branches preserved verbatim
  - ~14 commented-out // log_* breadcrumb lines deleted
  - ERROR case still returns false (operation-flow abort intact)
affects: [phase-08-ok-data-path-conversion, phase-09-delete-response-msg-buffer]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Direct-log call-sites replaced with LOG_ERROR_ID / LOG_INFO_ID macros referencing catalog MSG_* IDs"
    - "_check_response drop-and-preserve pattern: WARN+ERROR cases drop log calls; OK+DATA stay verbatim until Phase 8"

key-files:
  created: []
  modified:
    - firestarter/src/operation_utils.cpp

key-decisions:
  - "D-01 applied verbatim: _check_response OK branch log_info(handle->response_msg) and DATA branch log_data(handle->response_msg) PRESERVED — Phase 8 territory; over-eager deletion would silently break Phase 7"
  - "logging_id.h added as include — macros already existed from Plan 01; only the #include was missing from this file"
  - "14 breadcrumb lines deleted per D-04b in same commit (they interleave within the file; separate commit would leave awkward state)"

patterns-established:
  - "Submodule-then-superproject two-commit pattern: submodule feat commit + superproject deps pointer bump"
  - "Breadcrumb deletion in same diff as conversions when breadcrumbs are co-located with changed lines"

requirements-completed:
  - LMIG-02

# Metrics
duration: 10min
completed: 2026-05-18
---

# Phase 7 Plan 09: operation_utils.cpp Direct-Log + Dispatcher + Breadcrumb Cleanup Summary

**6 direct-log call-sites in operation_utils.cpp converted to LOG_ERROR_ID/LOG_INFO_ID, _check_response WARN+ERROR log calls stripped (OK+DATA preserved per D-01), and 14 commented-out breadcrumb lines deleted in one atomic commit.**

## Performance

- **Duration:** ~10 min
- **Started:** 2026-05-18T15:40:00Z
- **Completed:** 2026-05-18T15:50:22Z
- **Tasks:** 1
- **Files modified:** 1 (firestarter/src/operation_utils.cpp)

## Accomplishments
- Added `#include "logging_id.h"` to operation_utils.cpp (macros from Plan 01 now accessible)
- 6 direct-log conversions: `log_error_const("Timeout")` -> `LOG_ERROR_ID(MSG_ERR_TIMEOUT)`, `log_error_P_int("Data err ", res)` -> `LOG_ERROR_ID_U16(MSG_ERR_DATA_ERR_N, (uint16_t)res)`, `log_info_const("Main done/start/init start/end start")` -> `LOG_INFO_ID(MSG_INFO_MAIN_DONE/MAIN_START/INIT_START/END_START)`
- `_check_response` WARNING case: `log_warn(handle->response_msg)` deleted, bare `break` remains
- `_check_response` ERROR case: `log_error(handle->response_msg)` deleted, `return false` preserved (operation-flow abort intact)
- `_check_response` OK + DATA cases: `log_info(handle->response_msg)` and `log_data(handle->response_msg)` preserved verbatim (D-01: Phase 8 territory)
- 14 commented-out `// log_*` breadcrumb lines deleted (lines 78, 80, 134, 139, 146, 178, 202, 204, 208, 211, 241, 243, 245, plus the `// log_info_const("- OK -")` inside _check_response)
- All 15 native dispatch tests pass: WARNING falls through, ERROR aborts, OK+DATA branches intact
- Uno build: Flash 79.4% (25606/32256), RAM 77.5%
- Leonardo build: Flash 96.8% (27768/28672), RAM 60.6%

## Task Commits

1. **Task 1: Convert direct-log sites + _check_response strip + breadcrumb deletion** - `84e06c4` (feat) — submodule commit
2. **Superproject pointer bump** - `24d0f84` (deps) — superproject submodule ref update

## Files Created/Modified
- `firestarter/src/operation_utils.cpp` - 6 direct-log conversions, _check_response WARNING+ERROR log calls stripped, 14 breadcrumbs deleted, #include "logging_id.h" added

## Decisions Made
- D-01 applied strictly: OK branch `log_info(handle->response_msg)` and DATA branch `log_data(handle->response_msg)` deliberately preserved — Phase 8 will convert those; deleting them in Phase 7 would silently break the host's OK/DATA path
- `logging_id.h` include added (it was missing from the file; macros were already defined in Plan 01)
- All 3 change categories (conversions, dispatcher edit, breadcrumbs) landed in a single submodule commit — they interleave within the same file; a half-commit would leave an inconsistent state

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
None.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- operation_utils.cpp is now clean of all legacy direct-log macros and breadcrumbs
- _check_response ERROR + WARNING cases no longer double-emit; Wave 2 populate-site conversions are now effective for those paths
- OK + DATA branches still emit via `log_info(handle->response_msg)` / `log_data(handle->response_msg)` — Phase 8 will convert these
- Both AVR builds green; dispatch test suite green

---
*Phase: 07-convert-error-warn-info-call-sites*
*Completed: 2026-05-18*
