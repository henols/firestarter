---
phase: 07-convert-error-warn-info-call-sites
plan: 11
subsystem: firmware
tags: [arduino, c++, logging, dev-tools, platformio]

# Dependency graph
requires:
  - phase: 07-convert-error-warn-info-call-sites
    plan: 01
    provides: LOG_INFO_ID_BYTES, LOG_INFO_ID_U24 macros in logging_id.h
provides:
  - dev_tools.cpp with all 7 INFO call-sites converted to LOG_INFO_ID_* macros
  - Fixed-size stack buffer packing for ascii_str, u8+u8, and u24 param shapes
affects:
  - 07-convert-error-warn-info-call-sites (wave 3 completion)

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "ascii_str packing: fixed-size uint8_t _b[N] with clamped length, _b[0]=len, memcpy(&_b[1], str, len)"
    - "CE/OE 2-byte pack: uint8_t _b[2] = {ce_val, oe_val}; LOG_INFO_ID_BYTES"
    - "u24 address emit: LOG_INFO_ID_U24(MSG_INFO_ADDR / MSG_INFO_ADDR_REMAP, address)"

key-files:
  created: []
  modified:
    - firestarter/src/dev_tools.cpp

key-decisions:
  - "Fixed-size stack buffers used throughout (16, 8, 32 bytes) per RESEARCH Pitfall 5 — no VLAs"
  - "strlen clamped to buffer capacity minus 2 (for length byte + null) to prevent overrun"
  - "logging_id.h added as include; Arduino.h already provides string.h on AVR so no separate include needed"

patterns-established:
  - "ascii_str packing for BIT_HEADER uses 8-byte buffer (prefix is at most 3 bytes: |D8)"
  - "ascii_str packing for BIT_STR uses 32-byte buffer (bit string is up to 28 bytes for 9-bit register)"
  - "ascii_str packing for REG_HEADER uses 16-byte buffer with reg name clamped to 14 chars"

requirements-completed:
  - LMIG-02

# Metrics
duration: 3min
completed: 2026-05-18
---

# Phase 07 Plan 11: dev_tools.cpp INFO Call-Site Conversion Summary

**All 7 INFO call-sites in dev_tools.cpp converted to LOG_INFO_ID_BYTES/_U24 using fixed-size stack buffers for ascii_str packing and 2-byte arrays for CE/OE**

## Performance

- **Duration:** 3 min
- **Started:** 2026-05-18T16:02:03Z
- **Completed:** 2026-05-18T16:05:23Z
- **Tasks:** 1
- **Files modified:** 1

## Accomplishments

- Added `#include "logging_id.h"` to dev_tools.cpp
- Converted all 3 ascii_str call-sites (REG_HEADER, BIT_HEADER, BIT_STR) using fixed-size stack buffers with clamped lengths
- Converted both CE/OE call-sites (in dt_set_registers and dt_set_address) to LOG_INFO_ID_BYTES with 2-byte array
- Converted 2 address call-sites (MSG_INFO_ADDR and MSG_INFO_ADDR_REMAP) to LOG_INFO_ID_U24
- Both AVR builds (Uno + Leonardo) clean; dispatch and messages native tests pass

## Task Commits

1. **Task 1: Convert dev_tools.cpp INFO call-sites** - `246f2be` (feat — in firestarter submodule)
2. **Superproject pointer bump** - `179010a` (deps)

## Files Created/Modified

- `firestarter/src/dev_tools.cpp` - 7 INFO call-sites converted; logging_id.h added as include

## Decisions Made

- Fixed-size stack buffers (not VLAs) per RESEARCH Pitfall 5 — predictable stack pressure on AVR
- REG_HEADER uses 16-byte buffer (name clamped to 14 chars + 1 length byte + 1 reg byte = 16)
- BIT_HEADER uses 8-byte buffer (prefix is `|D8` = 3 chars max, plus length byte)
- BIT_STR uses 32-byte buffer (bit_str is up to 28 chars for 9-bit register: 9*3+1 = 28, plus length byte)
- Arduino.h already provides string.h on AVR, so no additional `#include <string.h>` was needed

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

- `pio test -e native` showed 2 pre-existing ERRORED suites (`test_flash_intel_vpp`, `test_eeprom28c_chip_id`). Confirmed pre-existing by running against baseline (git stash). Unrelated to dev_tools.cpp changes. The `test_dispatch` and `test_messages` suites both PASSED (22/24 test cases, same as baseline).

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Plan 11 complete; dev_tools.cpp fully converted
- Wave 3 continues with plans 12 and 13
- No blockers

## Self-Check: PASSED

- SUMMARY.md: FOUND at .planning/phases/07-convert-error-warn-info-call-sites/07-11-SUMMARY.md
- dev_tools.cpp: FOUND at firestarter/src/dev_tools.cpp
- Submodule commit 246f2be: FOUND
- Superproject commit 179010a: FOUND

---
*Phase: 07-convert-error-warn-info-call-sites*
*Completed: 2026-05-18*
