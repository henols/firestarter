---
phase: 07-convert-error-warn-info-call-sites
plan: 10
subsystem: firmware
tags: [avr, arduino, logging, call-site-migration, catalog, binary-frames]

# Dependency graph
requires:
  - phase: 07-convert-error-warn-info-call-sites/01
    provides: LOG_ERROR_ID_* / LOG_WARN_ID_* / LOG_INFO_ID_* macros in logging_id.h
provides:
  - "20 direct-log call-sites in firestarter/src/firestarter.cpp converted to LOG_*_ID_* macros"
  - "Dead-code if(response_code==ERROR) block at :86 deleted (json_parse never sets it)"
  - "Hybrid log_error_format_buf at :176 converted to LOG_ERROR_ID_U8(MSG_ERR_CMD_TIMEOUT)"
  - "Hybrid log_error_P_int_buf at :243 converted to LOG_ERROR_ID_U8(MSG_ERR_UNKNOWN_CMD)"
  - "5 EXTRA_INFO_LOGGING-guarded and 2 DEV_TOOLS+EXTRA_INFO_LOGGING-guarded sites converted for SC#1 grep gate"
affects: [07-13, phase-9-cleanup]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "LOG_ERROR_ID_U8(MSG_ERR_*, handle.cmd) for command/timeout error sites with u8 param"
    - "Hybrid sites (format-buf pattern) convert to LOG_*_ID_* with no buffer touch and no response_code assignment"
    - "Guarded INFO sites (#ifdef EXTRA_INFO_LOGGING) converted to LOG_INFO_ID_U8/U16/U32 — guards kept, macro calls inside swapped"

key-files:
  created: []
  modified:
    - "firestarter/src/firestarter.cpp"

key-decisions:
  - "Assumption A1 reverified: grep response_code json_parser.c returned zero hits — dead-code block at :86 safely deleted"
  - "Hybrid at :176 converted as LOG_ERROR_ID_U8(MSG_ERR_CMD_TIMEOUT, handle.cmd) with no buffer touch — RESEARCH §5 confirms downstream command_done() resets handle immediately"
  - "Hybrid at :243 converted as LOG_ERROR_ID_U8(MSG_ERR_UNKNOWN_CMD, handle.cmd) per D-03 catalog-format normalization"

patterns-established:
  - "Pattern: Zero-param errors use LOG_ERROR_ID(MSG_ERR_*); single-u8 errors use LOG_ERROR_ID_U8(MSG_ERR_*, param)"
  - "Pattern: Guarded INFO blocks keep their #ifdef guards; only the macro call inside is replaced"

requirements-completed: [LMIG-02]

# Metrics
duration: 15min
completed: 2026-05-18
---

# Phase 07 Plan 10: firestarter.cpp Call-Site Conversion Summary

**20 direct-log call-sites in firestarter.cpp converted to LOG_*_ID_* macros; dead json_parse error block deleted; both hybrid sites (timeout + unknown-cmd) emit binary frames with no buffer touch**

## Performance

- **Duration:** ~15 min
- **Started:** 2026-05-18T15:40:00Z
- **Completed:** 2026-05-18T15:55:13Z
- **Tasks:** 1
- **Files modified:** 1 (firestarter/src/firestarter.cpp)

## Accomplishments

- Converted all 20 active direct-log call-sites (6 unguarded + 5 EXTRA_INFO_LOGGING-guarded + 2 DEV_TOOLS+EXTRA_INFO_LOGGING-double-guarded + 2 hybrid format sites) to LOG_*_ID_* macros
- Deleted dead-code `if (handle->response_code == RESPONSE_CODE_ERROR)` block at line 86 after reverifying that `json_parser.c` never assigns `response_code` (zero hits)
- Converted both hybrid sites (line 176 and line 243) to direct LOG_ERROR_ID_U8 emits with no `handle.response_msg` buffer writes
- Added `#include "logging_id.h"` to firestarter.cpp
- Both Uno and Leonardo AVR builds succeeded; 15/15 native dispatch tests passed

## Task Commits

1. **Task 1: Convert firestarter.cpp call-sites + delete line 86 dead-code + convert line 176/243 hybrids** - `5c07d34` (feat) — submodule commit
2. **Superproject pointer bump** - `7a5dedc` (deps) — superproject commit

## Files Created/Modified

- `firestarter/src/firestarter.cpp` — 21 edits: 20 macro conversions + 1 dead-code block deletion; net -3 lines (21 insertions, 24 deletions)

## Decisions Made

- Assumption A1 reverified before deletion: `grep -n 'response_code' firestarter/src/json_parser.c` returned zero hits, confirming `json_parse()` never sets `response_code = ERROR`. Dead-code block safely removed.
- Line 176 hybrid converted to `LOG_ERROR_ID_U8(MSG_ERR_CMD_TIMEOUT, handle.cmd)` with no `handle.response_code` or `handle.response_msg` assignment per RESEARCH §5 — `command_done()` immediately resets the handle after this point.
- Line 243 hybrid converted to `LOG_ERROR_ID_U8(MSG_ERR_UNKNOWN_CMD, handle.cmd)` per D-03 catalog-format normalization.
- `MSG_INFO_FLAG_SKIP_BLANK` used for `FLAG_SKIP_BLANK_CHECK` (catalog ID 0x49) — matches catalog short-name exactly.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## Known Stubs

None — no placeholder values or hardcoded stubs introduced.

## Threat Flags

None — no new network endpoints, auth paths, file access patterns, or schema changes introduced.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- firestarter.cpp is fully converted; no legacy `log_*` calls remain in this file
- SC#1 grep gate (Plan 07-13) will pass for firestarter.cpp — all guarded and unguarded sites converted
- Remaining unconverted files in Phase 7 wave: dev_tools.cpp, eprom_operations.cpp, hardware_operations.cpp, proms/*.cpp
- `rurp_register_utils.h` pre-existing dirty file left untouched as instructed

---
*Phase: 07-convert-error-warn-info-call-sites*
*Completed: 2026-05-18*
