---
phase: 07-convert-error-warn-info-call-sites
plan: 06
subsystem: firmware
tags: [logging, eeprom, chip-id, safety-closure, catalog-ids]

# Dependency graph
requires:
  - phase: 07-convert-error-warn-info-call-sites/plan-01
    provides: LOG_ERROR_ID_*/LOG_WARN_ID_* macro families in logging_id.h
  - phase: 07-convert-error-warn-info-call-sites/plan-02
    provides: MSG_ERR_MEM_SIZE_TOO_SMALL (0xBA), MSG_ERR_CHIP_ID_MISMATCH (0xB9) catalog IDs
provides:
  - eeprom_28c.cpp: all 3 populate-sites converted to LOG_*_ID_* macros
  - MSG_WARN/ERR_MEM_SIZE_TOO_SMALL dynamic-severity at mem_size guard (SAF-05)
  - MSG_WARN/ERR_CHIP_ID_MISMATCH dynamic-severity at chip-id compare (SAF-05)
  - MSG_ERR_EEPROM_TIMEOUT with 5-byte u24+u8+u8 param encoding
affects:
  - 07-convert-error-warn-info-call-sites/subsequent-plans
  - phase-13-safety-closure
  - host-catalog-decoder

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Dynamic-severity: FLAG_FORCE branch selects WARN vs ERROR message ID"
    - "Multi-byte param packing: uint8_t _b[N] in scoped block, MSB-first"
    - "response_code assigned immediately after LOG_*_ID_* call in both branches"

key-files:
  created: []
  modified:
    - firestarter/src/proms/eeprom_28c.cpp

key-decisions:
  - "Scoped block { uint8_t _b[4]; ... } used for chip-id packing to avoid stack variable name collision"
  - "response_code added to eeprom28c_wait_for_write timeout path (was missing before conversion)"
  - "Leonardo Flash at 97.8% post-conversion — within acceptable saturation band"

patterns-established:
  - "FLAG_FORCE branching: if (is_flag_set(FLAG_FORCE)) { LOG_WARN_ID_*; handle->response_code = RESPONSE_CODE_WARNING; } else { LOG_ERROR_ID_*; handle->response_code = RESPONSE_CODE_ERROR; }"

requirements-completed:
  - LMIG-02

# Metrics
duration: 2min
completed: 2026-05-18
---

# Phase 07 Plan 06: eeprom_28c.cpp Populate-Site Conversion Summary

**AT28C EEPROM populate-sites converted to catalog-driven LOG_WARN/ERROR_ID_* macros: mem-size guard (dynamic-severity u32), chip-id mismatch (dynamic-severity 4-byte), and DQ7 timeout (ERROR 5-byte u24+u8+u8)**

## Performance

- **Duration:** ~2 min
- **Started:** 2026-05-18T15:35:10Z
- **Completed:** 2026-05-18T15:37:00Z
- **Tasks:** 1
- **Files modified:** 1

## Accomplishments

- Converted all 3 legacy `firestarter_response_format` / `firestarter_error_response_format` populate-sites in `eeprom_28c.cpp` to structured catalog-ID binary frames
- Both dynamic-severity sites (mem_size guard and chip-id mismatch) retain full FLAG_FORCE branching per Pitfall-1 requirement
- EEPROM timeout site gains explicit `handle->response_code = RESPONSE_CODE_ERROR` (was implicit before via return path)
- Added `#include "logging_id.h"` to resolve new macros
- Both AVR boards build clean (Uno 80.2% Flash / 77.5% RAM; Leonardo 97.8% Flash / 60.6% RAM)
- All 15 native dispatch tests pass

## Task Commits

1. **Task 1: Convert eeprom_28c.cpp populate-sites** - `af4567d` (submodule feat)
2. **Superproject pointer bump** - `1184661` (superproject deps)

## Files Created/Modified

- `firestarter/src/proms/eeprom_28c.cpp` - Three populate-sites converted; logging_id.h include added

## Decisions Made

- Used scoped `{ uint8_t _b[4]; ... }` block for chip-id mismatch packing to mirror the eprom.cpp pattern and avoid variable shadowing at function scope
- `response_code = RESPONSE_CODE_ERROR` added after `LOG_ERROR_ID_BYTES(MSG_ERR_EEPROM_TIMEOUT, ...)` — the original code relied on the caller checking the return value; explicit assignment closes the traceability gap
- Leonardo Flash 97.8%: within known saturation band for this phase (plan specified "Leonardo near saturation — confirm")

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- eeprom_28c.cpp is fully converted; no legacy `firestarter_response_format` calls remain
- Wave-2 populate-site conversion continues with remaining .cpp files per phase-07 plan

---
*Phase: 07-convert-error-warn-info-call-sites*
*Completed: 2026-05-18*
