---
phase: 07-convert-error-warn-info-call-sites
plan: 04
subsystem: firmware
tags: [avr, arduino, logging, flash-intel, catalog-id, cpp]

# Dependency graph
requires:
  - phase: 07-convert-error-warn-info-call-sites/plan-01
    provides: LOG_ERROR_ID_* / LOG_WARN_ID_* macro families in logging_id.h
  - phase: 07-convert-error-warn-info-call-sites/plan-02
    provides: MSG_ERR_VPP_HIGH (0xB8) + MSG_ERR_CHIP_ID_MISMATCH (0xB9) catalog IDs
provides:
  - All 7 ERROR+WARN populate-sites in flash_intel.cpp converted to LOG_*_ID_* macros
  - Dynamic-severity FLAG_FORCE branches preserved for VPP high + chip ID mismatch
  - response_code state machine assignments preserved alongside each LOG emit
affects:
  - plan 07-05 through 07-13 (remaining call-site conversion plans)
  - Phase 09 (flash savings measurement — flash_intel.cpp legacy strings eligible for deletion)

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Braced _b[N] stack array for multi-param LOG_*_ID_BYTES calls (matches eprom.cpp pattern)"
    - "Dual-branch FLAG_FORCE pattern: if(is_flag_set(FLAG_FORCE)){ LOG_WARN... } else { LOG_ERROR... }"

key-files:
  created: []
  modified:
    - firestarter/src/proms/flash_intel.cpp

key-decisions:
  - "flash_intel_poll_sr response_code was missing before LOG_ERROR_ID calls — added RESPONSE_CODE_ERROR assignments as Rule 2 (missing critical functionality for state machine correctness)"

patterns-established:
  - "flash_intel.cpp follows same _b[] braced-block pattern as eprom.cpp for VPP voltage params"
  - "SR polling error sites: LOG_ERROR_ID first, then response_code, then SR reset + return false"

requirements-completed:
  - LMIG-02

# Metrics
duration: 15min
completed: 2026-05-18
---

# Phase 07 Plan 04: flash_intel.cpp ERROR+WARN Populate-Site Conversion Summary

**All 7 ERROR+WARN populate-sites in flash_intel.cpp converted to catalog-driven LOG_ERROR_ID_*/LOG_WARN_ID_* macros with dynamic-severity FLAG_FORCE branching preserved**

## Performance

- **Duration:** ~15 min
- **Started:** 2026-05-18T15:30:00Z
- **Completed:** 2026-05-18T15:45:00Z
- **Tasks:** 1
- **Files modified:** 1

## Accomplishments

- 7 legacy `firestarter_(error|warning)_response` + `firestarter_response_format` populate-sites eliminated from flash_intel.cpp
- Dynamic-severity sites (VPP high, chip ID mismatch) converted to dual-branch FLAG_FORCE pattern emitting MSG_WARN_VPP_HIGH/MSG_ERR_VPP_HIGH and MSG_WARN_CHIP_ID_MISMATCH/MSG_ERR_CHIP_ID_MISMATCH
- 4-param VPP voltage sites pack four u16 values into 8-byte MSB-first arrays using braced _b[] block (matches eprom.cpp pattern)
- SR polling error sites (VPP error, program error, SR timeout) converted to zero-param LOG_ERROR_ID with explicit response_code = RESPONSE_CODE_ERROR
- Both AVR builds green: Uno 81.1% (6,090 B free), Leonardo 98.8% (28,330/28,672 B, 342 B free — no overflow)
- All 15 native dispatch tests pass

## Task Commits

1. **Task 1: Convert flash_intel.cpp populate-sites** - `6dfd214` (feat) — submodule commit
2. **Superproject pointer bump** - `04bfaf9` (deps) — superproject commit

## Files Created/Modified

- `firestarter/src/proms/flash_intel.cpp` — 7 populate-sites converted; #include "logging_id.h" added; 60 insertions, 13 deletions

## Decisions Made

- Added `handle->response_code = RESPONSE_CODE_ERROR` assignments at the three `flash_intel_poll_sr` error sites (SR VPP error, program error, SR timeout). The original code omitted these — the caller checked `flash_intel_poll_sr`'s `return false` for control flow but the response_code was never set, leaving it at its default (RESPONSE_CODE_OK). Adding the assignment is a Rule 2 auto-fix: `response_code` is the firmware's state machine signal that determines whether the operation aborts; omitting it would break the pattern established across all other convert plans and leave the host without an error severity signal.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Missing Critical] Added response_code assignments at flash_intel_poll_sr error sites**
- **Found during:** Task 1 (conversion of lines 135, 140, 147)
- **Issue:** Original `flash_intel_poll_sr` error branches used `firestarter_error_response()` which internally set both the log message and response_code. The plan's replacement template only showed `LOG_ERROR_ID(...)` — without `handle->response_code = RESPONSE_CODE_ERROR`. Leaving response_code unset would mean the state machine never sees an error signal even though the function returns false.
- **Fix:** Added `handle->response_code = RESPONSE_CODE_ERROR;` immediately after each `LOG_ERROR_ID()` call at the three SR polling error sites.
- **Files modified:** firestarter/src/proms/flash_intel.cpp
- **Verification:** Builds pass, grep confirms pattern matches must_haves truth: "response_code state machine still drives operation-flow abort"
- **Committed in:** 6dfd214

---

**Total deviations:** 1 auto-fixed (Rule 2 — missing critical functionality)
**Impact on plan:** Essential for state machine correctness. No scope creep.

## Issues Encountered

- Leonardo flash at 98.8% (28,330 B) after this plan — 38 bytes consumed vs. plan-03 baseline (28,292 B). Still 342 bytes free; no overflow. Flash usage within acceptable range for continued conversion plans.

## Known Stubs

None.

## Threat Flags

None — no new network endpoints, auth paths, file access patterns, or schema changes introduced.

## Next Phase Readiness

- flash_intel.cpp fully converted for ERROR+WARN populate-sites
- Plan 07-05 (next PROM module conversion) can proceed without blockers
- Leonardo flash headroom: 342 B — marginal but sufficient for remaining conversion plans (converting replaces text strings with IDs, net flash reduction expected in Phase 09)
- Pre-existing dirty `firestarter/include/rurp_register_utils.h` remains unstaged (unrelated to Phase 07)

## Self-Check: PASSED

- [x] `firestarter/src/proms/flash_intel.cpp` exists and modified
- [x] Submodule commit 6dfd214 exists
- [x] Superproject commit 04bfaf9 exists
- [x] Zero non-comment legacy log calls in flash_intel.cpp
- [x] MSG_ERR_INTEL_VPP, MSG_ERR_INTEL_PROGRAM, MSG_ERR_INTEL_SR_TIMEOUT all present (3 hits)
- [x] MSG_ERR_VPP_HIGH present (1 hit)
- [x] MSG_ERR_CHIP_ID_MISMATCH present (1 hit)
- [x] Native dispatch tests: 15/15 PASSED
- [x] Uno build: SUCCESS 81.1%
- [x] Leonardo build: SUCCESS 98.8% (no overflow)

---
*Phase: 07-convert-error-warn-info-call-sites*
*Completed: 2026-05-18*
