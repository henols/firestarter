---
phase: 07-convert-error-warn-info-call-sites
plan: 03
subsystem: firmware
tags: [eprom, logging, message-ids, rurp_log_id, AVR, PlatformIO]

# Dependency graph
requires:
  - phase: 07-convert-error-warn-info-call-sites plan 01
    provides: LOG_ERROR_ID_* / LOG_WARN_ID_* macro families in logging_id.h
  - phase: 07-convert-error-warn-info-call-sites plan 02
    provides: MSG_ERR_VPP_HIGH (0xB8) and MSG_ERR_CHIP_ID_MISMATCH (0xB9) catalog IDs
provides:
  - All 5 ERROR/WARN populate-sites in eprom.cpp emit via rurp_log_id (MSG_ERR_WRITE_FAILED, MSG_WARN_REV0_VPP_UNSUPPORTED, MSG_WARN/ERR_VPP_HIGH, MSG_WARN_VPP_LOW, MSG_WARN/ERR_CHIP_ID_MISMATCH)
  - WRITE_FAILED frame is exactly 6 wire bytes (u24 addr + u8 retries + u16 mismatch) packed MSB-first
  - Dynamic-severity sites (VPP high, chip ID mismatch) keep both WARN and ERROR branches gated on FLAG_FORCE / error_code
  - OK-path sites (Skipping erase, Number of retries) untouched — Phase 8 territory
affects:
  - 07-convert-error-warn-info-call-sites plans 04-13 (same populate-site pattern to follow in other modules)
  - Phase 8 (OK/INIT/MAIN/END call-site conversion will continue on eprom.cpp)
  - Phase 9 (flash savings measurement)

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "6-byte MSB-first stack array for WRITE_FAILED: uint8_t _b[6] inside braced block, LOG_ERROR_ID_BYTES(MSG_ERR_WRITE_FAILED, _b, 6)"
    - "8-byte MSB-first stack array for 4xu16 VPP params: uint8_t _b[8] inside braced block"
    - "4-byte MSB-first stack array for 2xu16 chip-ID params"
    - "Dynamic-severity branch via FLAG_FORCE (VPP high) or error_code parameter (chip ID)"
    - "response_code assigned immediately after LOG_*_ID_* emit (state machine contract preserved)"

key-files:
  created: []
  modified:
    - firestarter/src/proms/eprom.cpp

key-decisions:
  - "CHIP_ID_MISMATCH uses error_code parameter (not FLAG_FORCE re-check) because the function eprom_internal_check_chip_id receives severity as a resolved arg from two call-sites with different policies"
  - "VPP HIGH uses is_flag_set(FLAG_FORCE) inline branch (WARN vs ERROR) since it is evaluated at the call-site, not via a parameter"
  - "WRITE_FAILED packs [u24, u8, u16] = 6 wire bytes (not 5); RESEARCH §3 self-correction confirmed"

patterns-established:
  - "Braced block isolation: uint8_t _b[N] declared inside { } to avoid variable-name collisions across multiple emit sites in the same function"
  - "Separate u16 temp vars (_v0.._v3) computed before packing into _b[] — avoids expression in array initializer"

requirements-completed: [LMIG-02]

# Metrics
duration: 15min
completed: 2026-05-18
---

# Phase 07 Plan 03: eprom.cpp ERROR+WARN Call-Site Conversion Summary

**All 5 ERROR/WARN populate-sites in eprom.cpp converted to LOG_*_ID_* macros — WRITE_FAILED emits 6 wire bytes (u24+u8+u16 MSB-first); VPP HIGH/LOW and CHIP_ID_MISMATCH use 8- and 4-byte MSB-first arrays with FLAG_FORCE / error_code dynamic-severity branches preserved.**

## Performance

- **Duration:** ~15 min
- **Started:** 2026-05-18T15:35:00Z
- **Completed:** 2026-05-18T15:50:00Z
- **Tasks:** 1
- **Files modified:** 1

## Accomplishments

- Added `#include "logging_id.h"` to eprom.cpp
- Replaced 5 `firestarter_*_response*` calls with `LOG_ERROR_ID_BYTES` / `LOG_WARN_ID_BYTES` / `LOG_WARN_ID` + explicit `handle->response_code` assignment
- WRITE_FAILED: 6-byte stack array `_b[6]` packing `[u24 addr, u8 retries, u16 mismatch]` MSB-first
- VPP HIGH: 8-byte array packing 4 u16 display values; full FLAG_FORCE branch (WARN vs ERROR) kept
- VPP LOW: 8-byte array; always WARN (no FLAG_FORCE path exists for this condition)
- CHIP_ID_MISMATCH: 4-byte array packing `[u16 chip_id, u16 handle->chip_id]` MSB-first; both branches kept via `error_code == RESPONSE_CODE_WARNING` predicate
- OK-path sites (line 104 "Skipping erase." and line 171 "Number of retries: %d") untouched
- Native dispatch tests: 15/15 pass; Uno 81.8% flash, Leonardo 99.6% flash — both SUCCESS

## Task Commits

1. **Task 1: Convert eprom.cpp populate-sites** - `e6f49fc` (feat) — submodule commit
2. **Superproject submodule pointer bump** - `79f4e83` (deps)

## Files Created/Modified

- `firestarter/src/proms/eprom.cpp` — added `logging_id.h` include; 5 populate-sites converted

## Decisions Made

- `eprom_internal_check_chip_id` receives `error_code` as a resolved parameter (set by callers based on FLAG_FORCE or always-error policy). The conversion branches on `error_code == RESPONSE_CODE_WARNING` rather than re-evaluating `is_flag_set(FLAG_FORCE)` inline, preserving the existing API contract.
- Braced block isolation (`{ }`) used at each emit site so `_b` and `_v0..v3` variable names do not collide in the same function scope (eprom_check_vpp has both VPP HIGH and VPP LOW emit blocks).

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## Known Stubs

None.

## Threat Flags

None — no new network endpoints, auth paths, file access patterns, or schema changes introduced.

## Self-Check: PASSED

- `firestarter/src/proms/eprom.cpp` exists and was modified.
- Submodule commit `e6f49fc` exists: confirmed via `git log`.
- Superproject commit `79f4e83` exists: confirmed via `git log`.
- Zero non-comment `firestarter_(error|warning)_response` references in eprom.cpp.
- Zero non-comment `firestarter_response_format` references in eprom.cpp.
- 7 MSG_* symbols referenced.
- `LOG_ERROR_ID_BYTES(MSG_ERR_WRITE_FAILED, _b, 6)` present.
- No `uint8_t _b[5]` array.
- `copy_to_buffer(handle->response_msg` count unchanged (1 line).
- Native dispatch: 15/15 PASSED.
- Uno build: SUCCESS (81.8% flash).
- Leonardo build: SUCCESS (99.6% flash).

## Next Phase Readiness

- Pattern established for remaining eprom.cpp-style populate-site conversions in Plans 04-13
- Phase 8 can continue converting OK/INIT/MAIN/END call-sites in eprom.cpp unchanged baseline

---
*Phase: 07-convert-error-warn-info-call-sites*
*Completed: 2026-05-18*
