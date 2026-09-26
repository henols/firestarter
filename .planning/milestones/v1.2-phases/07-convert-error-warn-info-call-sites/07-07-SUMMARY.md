---
phase: 07-convert-error-warn-info-call-sites
plan: 07
subsystem: firmware
tags: [arduino, cpp, logging, eprom, flash, sram, platformio]

# Dependency graph
requires:
  - phase: 07-convert-error-warn-info-call-sites
    plan: 01
    provides: LOG_ERROR_ID_* / LOG_WARN_ID_* macros in logging_id.h

provides:
  - memory.cpp line 116 dispatch fallthrough now emits MSG_ERR_MEM_TYPE_UNSUPPORTED via LOG_ERROR_ID_U8
  - memory.cpp line 219 verify mismatch now emits MSG_ERR_VERIFY via LOG_ERROR_ID_BYTES (5-byte u8+u8+u24)
  - memory.cpp line 287 blank-check failure now emits MSG_ERR_NOT_BLANK via LOG_ERROR_ID_BYTES (4-byte u24+u8)
  - test_configure_memory setUp stubbed for Serial.write so error path no longer SIGABRTs

affects:
  - 07-08-PLAN.md through 07-13-PLAN.md (remaining populate-site and direct-log waves)
  - Phase 9 (cleanup of firestarter_error_response_format and handle->response_msg)

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Two-line populate-site pattern: LOG_ERROR_ID_*(MSG, args) + handle->response_code = RESPONSE_CODE_ERROR"
    - "Multi-param byte-pack: named uint8_t _b[N] inside inner {} scope, then LOG_ERROR_ID_BYTES"
    - "Serial stub in dispatch test setUp for ArduinoFake to survive LOG_ERROR_ID_* calls"

key-files:
  created: []
  modified:
    - firestarter/src/proms/memory.cpp
    - firestarter/test/native/avr/test_dispatch/test_configure_memory.cpp

key-decisions:
  - "Added inner {} scope for multi-param byte-pack arrays to avoid C++ variable-length array warnings and keep stack lifetime explicit"
  - "Stubbed Serial.write+flush in test_configure_memory setUp (Rule 2 deviation) — previously the dispatch test never exercised the error path's emit; after conversion it does"
  - "test_configure_memory.cpp modified alongside memory.cpp in the same commit (test harness fix is inseparable from the conversion)"

patterns-established:
  - "Two-line error populate-site: LOG_ERROR_ID_* emit + response_code = RESPONSE_CODE_ERROR assignment are always adjacent"
  - "Multi-param packing uses a named uint8_t _b[] with explicit MSB-first byte extraction, computed address in a local variable"

requirements-completed:
  - LMIG-02

# Metrics
duration: 15min
completed: 2026-05-18
---

# Phase 7 Plan 07: Convert memory.cpp populate-sites to LOG_ERROR_ID_* macros Summary

**Three firestarter_error_response_format populate-sites in memory.cpp converted to LOG_ERROR_ID_U8 / LOG_ERROR_ID_BYTES with explicit response_code assignment; dispatch test gate passes and both AVR builds clean.**

## Performance

- **Duration:** ~15 min
- **Started:** 2026-05-18T15:25:00Z
- **Completed:** 2026-05-18T15:41:30Z
- **Tasks:** 1
- **Files modified:** 2 (submodule) + 1 (superproject pointer)

## Accomplishments

- Line 116 dispatch fallthrough: `firestarter_error_response_format("Memory type 0x%02x not supported", handle->mem_type)` replaced with `LOG_ERROR_ID_U8(MSG_ERR_MEM_TYPE_UNSUPPORTED, handle->mem_type)` + `handle->response_code = RESPONSE_CODE_ERROR`
- Line 219 verify mismatch: 3-param format (`u8+u8+u24`) replaced with 5-byte named-local pack + `LOG_ERROR_ID_BYTES(MSG_ERR_VERIFY, _b, 5)` + response_code assignment
- Line 287 blank-check failure: 2-param format (`u24+u8`) replaced with 4-byte named-local pack + `LOG_ERROR_ID_BYTES(MSG_ERR_NOT_BLANK, _b, 4)` + response_code assignment
- `#include "logging_id.h"` added to memory.cpp
- All 15 native dispatch tests pass (including `test_unknown_protocol_with_unknown_mem_type_errors` gate test)
- Uno 79.9% flash / Leonardo 97.4% flash — both build clean

## Task Commits

1. **Task 1: Convert memory.cpp populate-sites (lines 116, 219, 287)** — submodule `0979c0f` (feat)
2. **Superproject submodule pointer bump** — `b118b15` (deps)

## Files Created/Modified

- `firestarter/src/proms/memory.cpp` — added `#include "logging_id.h"`, converted 3 error populate-sites to LOG_ERROR_ID_* macros with explicit response_code assignment
- `firestarter/test/native/avr/test_dispatch/test_configure_memory.cpp` — added Serial.write+flush stubs in setUp so error dispatch path no longer SIGABRTs

## Decisions Made

- Used inner `{}` scopes for multi-param byte-pack arrays to keep variable lifetimes tight and avoid potential warnings on older compilers
- The test file fix was committed in the same submodule commit as the source change — it is not a separate test-only commit because the test harness change is strictly required by and inseparable from the conversion

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Missing Critical] Added Serial.write+flush stubs to test_configure_memory setUp**
- **Found during:** Task 1 (Convert memory.cpp populate-sites)
- **Issue:** After conversion, `test_unknown_protocol_with_unknown_mem_type_errors` triggered `LOG_ERROR_ID_U8` → `rurp_log_id` → `_firestarter_emit_frame` → `SERIAL_PORT.write()` which hit an unmocked ArduinoFake method, causing SIGABRT. The previous `firestarter_error_response_format` macro did not emit via serial; the new path does.
- **Fix:** Added `When(OverloadedMethod(ArduinoFake(Serial), write, ...)).AlwaysReturn(1)` and `When(Method(ArduinoFake(Serial), flush)).AlwaysReturn()` to the `setUp` function in `test_configure_memory.cpp`. Dispatch tests only assert `response_code`, not serial output — the stubs are intentionally no-op.
- **Files modified:** `firestarter/test/native/avr/test_dispatch/test_configure_memory.cpp`
- **Verification:** All 15 native dispatch tests pass (exit 0); `test_unknown_protocol_with_unknown_mem_type_errors` asserts `RESPONSE_CODE_ERROR` as required.
- **Committed in:** `0979c0f` (same commit as memory.cpp conversion)

---

**Total deviations:** 1 auto-fixed (Rule 2 — missing Serial stub for new emit path)
**Impact on plan:** Required for test correctness; no scope creep.

## Issues Encountered

- None beyond the Rule 2 deviation above.

## Next Phase Readiness

- memory.cpp has zero legacy `firestarter_error_response_format` populate-sites remaining
- Wave 2 of populate-site conversions for other proms/*.cpp modules can proceed
- Both AVR environments compile cleanly; native dispatch suite fully green

---
*Phase: 07-convert-error-warn-info-call-sites*
*Completed: 2026-05-18*
