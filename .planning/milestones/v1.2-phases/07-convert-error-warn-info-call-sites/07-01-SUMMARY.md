---
phase: 07-convert-error-warn-info-call-sites
plan: 01
subsystem: firmware
tags: [platformio, logging, macros, arduino, c++, avr]

# Dependency graph
requires:
  - phase: 06-logging-infrastructure
    provides: LOG_ID_* primitives and LOG_INFO_ID_* family that the new families alias

provides:
  - LOG_ERROR_ID family (6 macros, unconditional, in logging_id.h)
  - LOG_WARN_ID family (6 macros, unconditional, in logging_id.h)

affects:
  - 07-02-PLAN through 07-13-PLAN (all call-site conversion plans depend on this infrastructure)

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Unconditional severity macros: LOG_ERROR_ID_* and LOG_WARN_ID_* are thin one-line aliases over LOG_ID_* with no FLAG_VERBOSE gate"
    - "Section comment style: // --- Unconditional ERROR severity --- mirrors // --- Unconditional ID-frame emit --- pattern"

key-files:
  created: []
  modified:
    - firestarter/include/logging_id.h

key-decisions:
  - "Macros are one-line aliases (not do-while wrappers) — they expand to a single statement so wrapping is unnecessary"
  - "No FLAG_VERBOSE gate on ERROR/WARN families per D-02 — these always emit unconditionally"
  - "Zero flash cost at this stage — header-only additions; cost materializes only when call-sites are converted in subsequent plans"

patterns-established:
  - "Unconditional severity pattern: #define LOG_ERROR_ID(id) LOG_ID(id) — direct alias, no control flow wrapper"
  - "Severity readability: macro name encodes severity (LOG_ERROR_ID vs LOG_ID) even though underlying primitive is the same"

requirements-completed:
  - LMIG-02

# Metrics
duration: 1min
completed: 2026-05-18
---

# Phase 7 Plan 01: Add LOG_ERROR_ID_* and LOG_WARN_ID_* Macro Families Summary

**12 unconditional logging macros added to logging_id.h as one-line aliases over LOG_ID_* primitives — Wave-1 infrastructure enabling all Phase 7 call-site conversion plans**

## Performance

- **Duration:** 1 min
- **Started:** 2026-05-18T15:13:18Z
- **Completed:** 2026-05-18T15:14:21Z
- **Tasks:** 1
- **Files modified:** 1

## Accomplishments
- Added `LOG_ERROR_ID` family: 6 unconditional macros (_U8, _U16, _U24, _U32, _BYTES, zero-param)
- Added `LOG_WARN_ID` family: 6 unconditional macros (same surface, same unconditional semantics)
- Both AVR boards (Uno 80.9%, Leonardo 98.7%) build clean — zero flash change since no call-sites use the macros yet
- Native `test_messages` suite: 5/5 tests pass — Phase 6 emit path untouched

## Task Commits

Each task was committed atomically:

1. **Task 1: Add LOG_ERROR_ID_* and LOG_WARN_ID_* macro families to logging_id.h** - `59bf551` (feat) — in firestarter submodule
2. **Submodule pointer bump** - `4b27d94` (deps) — in superproject

## Files Created/Modified
- `firestarter/include/logging_id.h` — Added 12 new macros: 6 LOG_ERROR_ID family + 6 LOG_WARN_ID family, each a one-line alias over matching LOG_ID_* primitive, grouped under section comments

## Decisions Made
- Used one-line `#define` form (not `do { } while (0)` wrapper) because each alias expands to a single statement — the INFO family's do-while is needed for multi-statement if-guards but is not required here
- No `FLAG_VERBOSE` gate per D-02 — ERROR and WARN must always emit regardless of verbosity setting

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- All 12 macros present in `logging_id.h` and compile cleanly
- Wave-2 and Wave-3 plans (07-02 through 07-13) can now use `LOG_ERROR_ID_*` and `LOG_WARN_ID_*` at call-sites
- Flash baselines unchanged: Uno 80.9% (26,100/32,256 B), Leonardo 98.7% (28,292/28,672 B) — savings will appear when call-sites are converted and PROGMEM strings are deleted in Phase 9

---

## Acceptance Criteria Verification

| Check | Result |
|-------|--------|
| `grep -c '^#define LOG_ERROR_ID'` ≥ 6 | 6 PASS |
| `grep -c '^#define LOG_WARN_ID'` ≥ 6 | 6 PASS |
| `grep -c 'FLAG_VERBOSE'` unchanged (7) | 7 PASS |
| `pio run -e uno` exits 0 | PASS |
| `pio run -e leonardo` exits 0 | PASS |
| `pio test -e native -f "*test_messages*"` exits 0 | 5/5 PASS |
| Submodule commit subject matches plan | PASS |
| `rurp_register_utils.h` still modified-but-unstaged | PASS |

---
*Phase: 07-convert-error-warn-info-call-sites*
*Completed: 2026-05-18*
