---
phase: 07-convert-error-warn-info-call-sites
plan: 05
subsystem: firmware
tags: [avr, cpp, logging, eprom, flash, platformio]

# Dependency graph
requires:
  - phase: 07-convert-error-warn-info-call-sites plan 01
    provides: LOG_ERROR_ID / LOG_ERROR_ID_BYTES macros in logging_id.h
  - phase: 06
    provides: MSG_ERR_FL4_VERIFY_TIMEOUT (0xB3) and MSG_ERR_OP_TIMEOUT (0xB7) in messages catalog

provides:
  - flash_type_4.cpp ERROR populate-site at line 88 converted to LOG_ERROR_ID_BYTES(MSG_ERR_FL4_VERIFY_TIMEOUT)
  - flash_utils.cpp ERROR populate-site at line 46 converted to LOG_ERROR_ID(MSG_ERR_OP_TIMEOUT)

affects:
  - 07-06-PLAN onwards (remaining wave-2 populate-site conversions)
  - 07-13 (final grep gate verification)

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Multi-param populate-site: pack params into named uint8_t _b[N] array in a { } block, then call LOG_ERROR_ID_BYTES"
    - "Zero-param populate-site: direct LOG_ERROR_ID(MSG_*) + response_code = RESPONSE_CODE_ERROR, no buffer needed"

key-files:
  created: []
  modified:
    - firestarter/src/proms/flash_type_4.cpp
    - firestarter/src/proms/flash_utils.cpp

key-decisions:
  - "Pack u8+u24+u8 params as named local _b[5] (not compound literal) per RESEARCH Pitfall 5 — AVR compiler handles named locals more reliably than compound array literals in this context"
  - "flash_utils.cpp needed handle pointer for response_code; it was already available via function signature (firestarter_handle_t* handle) so no signature change required"

patterns-established:
  - "Zero-param ERROR site: LOG_ERROR_ID(id) + handle->response_code = RESPONSE_CODE_ERROR"
  - "Multi-param ERROR site with mixed types: named local array _b[N] packed MSB-first, then LOG_ERROR_ID_BYTES"

requirements-completed: [LMIG-02]

# Metrics
duration: 1min
completed: 2026-05-18
---

# Phase 7 Plan 05: flash_type_4.cpp + flash_utils.cpp ERROR Populate-Site Conversion Summary

**Two single-site ERROR populate-sites converted to catalog-driven LOG_ERROR_ID_BYTES / LOG_ERROR_ID macros; both AVR targets link cleanly with Leonardo at 98.4% flash headroom confirmed**

## Performance

- **Duration:** ~1 min
- **Started:** 2026-05-18T15:30:33Z
- **Completed:** 2026-05-18T15:31:50Z
- **Tasks:** 2
- **Files modified:** 2 (submodule) + 1 superproject submodule pointer

## Accomplishments

- Converted `flash_type_4.cpp:88` (`firestarter_error_response_format` with 3 params) to `LOG_ERROR_ID_BYTES(MSG_ERR_FL4_VERIFY_TIMEOUT, _b, 5)` with [u8 expected, u24 MSB-first address, u8 observed] packed into named local array
- Converted `flash_utils.cpp:47` (`firestarter_error_response`) to `LOG_ERROR_ID(MSG_ERR_OP_TIMEOUT)` (zero-param)
- Both conversions preserve `handle->response_code = RESPONSE_CODE_ERROR` after the emit
- OK-path `copy_to_buffer(handle->response_msg, "Skipping erase.")` at flash_type_4.cpp:51 untouched (out of scope per plan)
- All 15 native dispatch tests pass; Uno Flash 80.7% (26044/32256); Leonardo Flash 98.4% (28208/28672)

## Task Commits

Each task was committed atomically in the submodule:

1. **Task 1: Convert flash_type_4.cpp:88** - `096812d` (feat)
2. **Task 2: Convert flash_utils.cpp:47** - `1292826` (feat)

**Superproject submodule bump:** `55445ca` (deps)

## Files Created/Modified

- `firestarter/src/proms/flash_type_4.cpp` - Added `#include "logging_id.h"`; replaced `firestarter_error_response_format` at line 88 with `{ uint8_t _b[5]; ... LOG_ERROR_ID_BYTES(MSG_ERR_FL4_VERIFY_TIMEOUT, _b, 5); handle->response_code = RESPONSE_CODE_ERROR; }`
- `firestarter/src/proms/flash_utils.cpp` - Added `#include "logging_id.h"`; replaced `firestarter_error_response("Operation timed out")` at line 46 with `LOG_ERROR_ID(MSG_ERR_OP_TIMEOUT); handle->response_code = RESPONSE_CODE_ERROR;`

## Decisions Made

- Used named local `uint8_t _b[5]` inside a `{ }` block for `flash_type_4.cpp` multi-param site (matching RESEARCH §10 Pitfall 5 and flash_intel.cpp pattern reference)
- `flash_utils.cpp` `flash_util_verify_operation` already receives `firestarter_handle_t* handle` so `handle->response_code` assignment required no signature change

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None. Leonardo flash headroom confirmed (98.4% = 464 bytes free); the conversion freed 36 bytes relative to the post-Task-1 state (Task 2 removed the string literal "Operation timed out" from flash).

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Wave-2 populate-site conversions continue in plans 06-09 (remaining `proms/*.cpp` files)
- Pre-existing dirty `firestarter/include/rurp_register_utils.h` remains untouched as expected
- Leonardo flash headroom is critically tight (~1.6% free / 464 bytes); plans 06-09 must confirm headroom after each conversion

---
*Phase: 07-convert-error-warn-info-call-sites*
*Completed: 2026-05-18*
