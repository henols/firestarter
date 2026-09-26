---
phase: 07-convert-error-warn-info-call-sites
plan: 08
subsystem: firmware
tags: [avr, cpp, logging, catalog, flash, chip-id]

# Dependency graph
requires:
  - phase: 07-convert-error-warn-info-call-sites
    plan: 01
    provides: "LOG_WARN_ID_BYTES / LOG_ERROR_ID_BYTES macros in logging_id.h"
  - phase: 07-convert-error-warn-info-call-sites
    plan: 02
    provides: "MSG_ERR_CHIP_ID_MISMATCH (0xB9) in messages.h catalog"
provides:
  - "flash_type_3.cpp chip-ID mismatch site converted to LOG_WARN_ID_BYTES / LOG_ERROR_ID_BYTES with FLAG_FORCE branching"
  - "flash_type_3.cpp:87 classified as OK-path, deferred to Phase 8 (MSG_INFO_SKIPPING_ERASE_MEM 0x59)"
affects:
  - phase-08-ok-path-conversion
  - host-decoder

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Dynamic-severity chip-ID pattern: FLAG_FORCE gates WARN vs ERROR branch; uint8_t _b[4] MSB-first packs two u16 params; response_code set explicitly after emit"

key-files:
  created: []
  modified:
    - "firestarter/src/proms/flash_type_3.cpp"

key-decisions:
  - "flash_type_3.cpp:87 Skipping-erase site confirmed OK-path (no ERROR/WARNING response_code set); deferred to Phase 8 as MSG_INFO_SKIPPING_ERASE_MEM (0x59)"
  - "Used eprom.cpp eprom_internal_check_chip_id pattern as reference for the dual-severity chip-ID mismatch conversion"

patterns-established:
  - "Dynamic-severity BYTES pattern: pack two u16 params MSB-first into _b[4], then branch on is_flag_set(FLAG_FORCE) for WARN vs ERROR"

requirements-completed:
  - LMIG-02

# Metrics
duration: 5min
completed: 2026-05-18
---

# Phase 7 Plan 08: flash_type_3.cpp Chip-ID Populate-Site Conversion Summary

**Dynamic-severity chip-ID mismatch site in flash_type_3.cpp converted from firestarter_response_format to LOG_WARN_ID_BYTES / LOG_ERROR_ID_BYTES with FLAG_FORCE branching; line 87 OK-path confirmed and deferred to Phase 8**

## Performance

- **Duration:** 5 min
- **Started:** 2026-05-18T15:40:00Z
- **Completed:** 2026-05-18T15:45:47Z
- **Tasks:** 1
- **Files modified:** 1

## Accomplishments

- Converted `flash3_check_chip_id_execute` at flash_type_3.cpp:135 from `firestarter_response_format` to dual-severity `LOG_WARN_ID_BYTES(MSG_WARN_CHIP_ID_MISMATCH)` / `LOG_ERROR_ID_BYTES(MSG_ERR_CHIP_ID_MISMATCH)` with explicit FLAG_FORCE branching
- Packed two u16 params (chip_id, handle->chip_id) MSB-first into `uint8_t _b[4]`; `response_code` set explicitly in each branch (RESPONSE_CODE_WARNING / RESPONSE_CODE_ERROR)
- Added `#include "logging_id.h"` include directive; removed the intermediate `int response_code` local variable
- Classified flash_type_3.cpp:87 ("Skipping erase of memory") as OK-path (no ERROR/WARNING response_code set in that branch) — left unchanged, documented for Phase 8 conversion to MSG_INFO_SKIPPING_ERASE_MEM (0x59)
- Both AVR builds (Uno + Leonardo) clean; all 15 native dispatch tests pass

## Task Commits

1. **Task 1: Convert flash_type_3.cpp:135 dynamic-severity chip-id site** - `abb8d49` (feat) — submodule commit
2. **Superproject pointer bump** - `d019415` (deps)

## Files Created/Modified

- `firestarter/src/proms/flash_type_3.cpp` - Converted chip-ID mismatch site; added logging_id.h include

## Decisions Made

- Used eprom.cpp `eprom_internal_check_chip_id` as the canonical reference pattern for dual-severity chip-ID conversion (same MSG IDs, same _b[4] MSB-first packing)
- Confirmed line 87 as OK-path by reading lines 80-95: the surrounding `else` branch under `FLAG_SKIP_ERASE` never sets `response_code = ERROR/WARNING`, confirming Phase 8 deferral per plan Assumption A3

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Plan 08 complete; the only remaining RESEARCH open question (line 87 classification) is now resolved and documented
- Phase 7 Wave 2 populate-site conversion continues with plans 09+
- Phase 8 will convert flash_type_3.cpp:87 OK-path site to MSG_INFO_SKIPPING_ERASE_MEM (0x59)

---
*Phase: 07-convert-error-warn-info-call-sites*
*Completed: 2026-05-18*
