---
phase: 08-convert-state-machine-prefix-call-sites-ok-init-main-end
plan: "06"
subsystem: firmware-logging
tags: [avr, sram, response_msg, copy_to_buffer, _check_response, r-01, r-03]
dependency_graph:
  requires:
    - phase: 08-05
      provides: "all R-02 populate-sites converted; response_msg field zeroed but not deleted"
  provides:
    - "response_msg[96] field deleted from firestarter_handle_t (R-01 SRAM win realized)"
    - "_check_response log-emit-free (R-03)"
    - "copy_to_buffer macro deleted from logging.h"
    - "RESPONSE_MSG_SIZE define deleted"
  affects:
    - firestarter/include/firestarter.h
    - firestarter/src/firestarter.cpp
    - firestarter/src/operation_utils.cpp
    - firestarter/src/proms/eprom.cpp
    - firestarter/include/logging.h
tech-stack:
  added: []
  patterns:
    - "_check_response as pure operation-flow dispatcher — no log-emit side effects; switch drives control flow only"
key-files:
  created: []
  modified:
    - firestarter/src/operation_utils.cpp
    - firestarter/include/firestarter.h
    - firestarter/src/firestarter.cpp
    - firestarter/src/proms/eprom.cpp
    - firestarter/include/logging.h
key-decisions:
  - "eprom.cpp:169 clear site deleted alongside the three documented clear sites (plan listed 3, actual count was 4 including eprom.cpp:169 — all were clears, not populate-sites; gate confirmed no dangling references)"
  - "logging.h macro definitions referencing response_msg (log_info_format, log_data_format, etc.) intentionally left for Phase 9 deletion; they are dead code with zero call-sites in src/ — build is clean because macros are not instantiated"
  - "copy_to_buffer removed from its own definition only; format_P_int and format_P_char macros that reference it internally are dead code (no callers) and survive until Phase 9 cleans the full logging.h macro tower"
  - "R-01 SRAM win exactly 96 bytes on both boards — struct field size matches expectation with no compiler-padding effects"
requirements-completed:
  - LMIG-03

duration: "~12 min"
completed: "2026-05-18"
---

# Phase 08 Plan 06: Structural Deletion — response_msg Buffer, RESPONSE_MSG_SIZE, copy_to_buffer, and _check_response Log Emits

**Deleted the 96-byte `response_msg` scratch buffer from `firestarter_handle_t`, stripping all clear-sites and `_check_response` log emits, yielding exactly 96 bytes SRAM recovered on both Uno and Leonardo.**

## Performance

- **Duration:** ~12 min
- **Completed:** 2026-05-18
- **Tasks:** 2
- **Files modified:** 5

## Accomplishments

- `_check_response` is now a pure operation-flow dispatcher: switch drives return-false-on-ERROR, rurp_communication_write-on-DATA, and op_reset_timeout always — zero log-emit side effects
- `char response_msg[RESPONSE_MSG_SIZE]` field gone from `firestarter_handle_t`; `#define RESPONSE_MSG_SIZE 96` gone from `firestarter.h`
- All 4 response_msg clear sites deleted: `firestarter.cpp` (parse_json + command_done), `operation_utils.cpp` (_execute_operation), `eprom.cpp` (write retry path)
- `copy_to_buffer` macro deleted from `logging.h`
- SRAM win: Uno −96 B (77.8% → 73.1%); Leonardo −96 B (61.1% → 57.3%)

## SRAM Delta (R-01 Win Realized)

| Board | Pre-plan (08-05 close) | Post-plan (08-06 close) | Delta |
|-------|------------------------|-------------------------|-------|
| Uno | 1,593 B / 2,048 B (77.8%) | 1,497 B / 2,048 B (73.1%) | **−96 B (−4.7%)** |
| Leonardo | 1,563 B / 2,560 B (61.1%) | 1,467 B / 2,560 B (57.3%) | **−96 B (−3.8%)** |

**Nominal R-01 win realized: exactly 96 bytes on both boards** (no compiler-padding effect).

## copy_to_buffer Caller Count

- Before plan: 1 definition + 3 uses in macro bodies (format_P_int, format_P_char, firestarter_set_response) — all dead code with zero call-sites in `src/`
- After plan: 0 (definition deleted; macro bodies referencing it are Phase 9 deletion targets)

## Task Commits

Each task was committed atomically:

1. **Task 1: Strip log_info/log_data calls inside _check_response (R-03)** - `828485d` (refactor)
2. **Task 2: Delete response_msg field + RESPONSE_MSG_SIZE + copy_to_buffer (R-01)** - `436789b` (refactor)

## Files Created/Modified

- `firestarter/src/operation_utils.cpp` — _check_response log emits removed (Task 1); response_msg clear site in _execute_operation removed (Task 2)
- `firestarter/include/firestarter.h` — RESPONSE_MSG_SIZE define deleted; response_msg field deleted from firestarter_handle_t
- `firestarter/src/firestarter.cpp` — response_msg clear sites removed from parse_json + command_done
- `firestarter/src/proms/eprom.cpp` — response_msg clear site removed from write retry path
- `firestarter/include/logging.h` — copy_to_buffer macro definition deleted

## Decisions Made

1. **eprom.cpp:169 was a 4th clear site** — the PLAN.md body listed 3 clear sites but the CONTEXT.md R-01 section had already listed 4 (firestarter.cpp:64/168, operation_utils.cpp:300, eprom.cpp:169). The pre-deletion gate confirmed it was a clear-only site (not a populate-site), so it was deleted alongside the others.

2. **logging.h macro definitions left intact** — Macros like `log_info_format`, `log_data_format`, `send_ack_format`, `firestarter_set_response`, `format_P_int`, `format_P_char` all reference `handle->response_msg` in their bodies. These are dead code (zero call-sites in `src/`) and builds are clean because macros are only compiled when instantiated. Phase 9 (LFW-03/04) deletes the entire legacy logging.h macro tower.

3. **format_P_int / format_P_char reference copy_to_buffer** — These macros internally call `copy_to_buffer`, which was just deleted. Since neither macro has call-sites in `src/`, the build stays clean. Phase 9 cleans them up together with the rest of the macro tower.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Extra clear site in eprom.cpp:169**
- **Found during:** Task 2 (pre-deletion grep gate)
- **Issue:** Plan listed 3 clear sites but eprom.cpp:169 (`handle->response_msg[0] = '\0'`) was a 4th clear site inside the write retry path. It was referenced in CONTEXT.md R-01 but omitted from PLAN.md's Task 2 action steps.
- **Fix:** Deleted the clear site from eprom.cpp as part of the atomic Task 2 commit. Verified it was a clear-only site (not a populate-site) before deletion.
- **Files modified:** `firestarter/src/proms/eprom.cpp`
- **Verification:** Build clean; grep gate confirms zero response_msg references in src/ after deletion
- **Committed in:** `436789b` (Task 2 commit)

---

**Total deviations:** 1 auto-fixed (Rule 1 - extra clear site in plan description)
**Impact on plan:** Required for completeness; without it the field deletion would have left a dangling reference.

## Verification Results

- `pio run -e uno` (clean) — SUCCESS (1,497 B RAM / 22,330 B Flash)
- `pio run -e leonardo` (clean) — SUCCESS (1,467 B RAM / 24,538 B Flash)
- `pio test -e native` — test_dispatch: 15/15 PASSED; test_messages: 5/5 PASSED
- `python -m pytest tests/ -v` — 29/29 PASSED (host side unchanged)
- Post-deletion grep gate:
  - `grep -rn "response_msg\b" src/ include/` — zero hits in `src/`; 13 hits are dead macro definitions in `logging.h` (Phase 9 targets)
  - `grep -rn "copy_to_buffer\b" src/ include/` — zero hits in `src/`; 3 hits are dead macro bodies in `logging.h` (Phase 9 targets)
  - `grep -rn "RESPONSE_MSG_SIZE\b" src/ include/` — zero hits

## Known Stubs

None — all deletions are structural; no placeholder data flows introduced.

## Threat Flags

None — no new network endpoints, auth paths, or schema changes.

## Self-Check: PASSED

- `firestarter/src/operation_utils.cpp` — `_check_response` contains `case RESPONSE_CODE_OK:` followed immediately by `break;` (no log_info); `case RESPONSE_CODE_DATA:` followed by `rurp_communication_write` (no log_data)
- `firestarter/include/firestarter.h` — does NOT contain `RESPONSE_MSG_SIZE` or `response_msg`
- `firestarter/include/logging.h` — does NOT contain `#define copy_to_buffer`
- `firestarter/src/firestarter.cpp` — does NOT contain `handle->response_msg[0]`
- `firestarter/src/proms/eprom.cpp` — does NOT contain `handle->response_msg[0]`
- Task commits present: `828485d`, `436789b`
- SRAM delta file: `/tmp/ph8-06-sram-delta.txt`

---
*Phase: 08-convert-state-machine-prefix-call-sites-ok-init-main-end*
*Completed: 2026-05-18*
