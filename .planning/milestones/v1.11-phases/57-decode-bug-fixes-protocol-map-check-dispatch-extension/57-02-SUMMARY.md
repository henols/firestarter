---
phase: 57-decode-bug-fixes-protocol-map-check-dispatch-extension
plan: 02
subsystem: dispatch-guard
tags: [check_dispatch, gate03, vpp-safety, dec-05, dispatch, pinouts]

# Dependency graph
requires:
  - phase: 57-decode-bug-fixes-protocol-map-check-dispatch-extension
    plan: 01
    provides: KNOWN_PROTOCOLS cleaned of 0x35/0x39; build_db.py no longer emits chips with those algorithms

provides:
  - check_dispatch.py with 0x35/0x39 removed from _ALGO_MEM_TYPE and dispatch() (DEC-05 sync)
  - Full-class GATE-03 VPP-safety guard: any chip with vpp-pin pinout AND {0x05,0x06,0x0D} algorithm must not route to configure_eprom
  - _vpp_pinouts built dynamically from pinouts.json (Phase 58 additions auto-covered)
  - check_dispatch.py exits 0 on current 734-chip DB with extended PASS message
  - ruff-clean check_dispatch.py (pre-existing E701 style violations resolved)

affects: [57-03, 58, 59]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - Dynamic frozenset from JSON file (pinouts.json) to avoid hardcoding vpp-pin coverage
    - Guard-list pattern: append violations to named list, check at exit gate, report with truncation

key-files:
  created: []
  modified:
    - firestarter_app/tools/check_dispatch.py

key-decisions:
  - "GATE-03 predicate uses proto in _5v_eeprom_algos (not etype) — direct algorithm check, not derived type field"
  - "pinouts.json loaded dynamically inside main() so guard auto-covers Phase 58 pinout additions without code change"
  - "Pre-existing E701 (single-line if-return) violations in dispatch() fixed via two-line form + ruff format (required for plan's ruff gate)"
  - "DEC-05 sync: 0x35/0x39 removed from _ALGO_MEM_TYPE and dispatch() in Task 1; GATE-03 guard added in Task 2"

patterns-established:
  - "Dispatch safety guards: append-to-list + exit-gate + FAIL/PASS reporting pattern reusable for future guards"

requirements-completed: [GATE-03, DEC-05]

# Metrics
duration: 18min
completed: 2026-06-08
---

# Phase 57 Plan 02: check_dispatch Extension Summary

**GATE-03 full-class VPP-safety guard added to check_dispatch.py: dynamic vpp-pin pinout set from pinouts.json + {0x05,0x06,0x0D} algorithm check; 0x35/0x39 removed to sync with build_db.py (DEC-05)**

## Performance

- **Duration:** ~18 min
- **Started:** 2026-06-08T13:30:00Z
- **Completed:** 2026-06-08T13:48:00Z
- **Tasks:** 2 (both auto)
- **Files modified:** 1

## Accomplishments

- DEC-05 sync: removed `0x35: 5` and `0x39: 5` from `_ALGO_MEM_TYPE`; narrowed `dispatch()` configure_flash4 branch from tuple `(0x05, 0x35, 0x39)` to equality `== 0x05`
- GATE-03: added `_PINOUT_FILE` constant; inside `main()`, dynamically loads pinouts.json and builds `_vpp_pinouts` frozenset (currently: DIP24_2716, DIP24_2732, DIP28_2764, DIP28_27256, DIP28_27512, DIP32_STD)
- GATE-03: `_5v_eeprom_algos = frozenset({0x05, 0x06, 0x0D})` added
- GATE-03: `vpp_eeprom_in_eprom` error list, chip-loop check, exit-gate condition, FAIL reporting block, PASS message line — all added following eeprom28c_in_eprom idiom
- `python tools/check_dispatch.py` exits 0 on current 734-chip DB with message: `PASS: all 734 chips have a valid dispatch path; 0 SRAM chips route to configure_eprom; 0 DIP28_2764 Flash/EEPROM chips route to configure_eprom; 0 vpp-pin Flash/EEPROM chips route to configure_eprom; 0 wire-key regressions`
- 480 tests pass; ruff check + ruff format --check clean

## Task Commits

1. **Task 1: Remove 0x35/0x39 (DEC-05 sync)** — `89cae4e` (feat)
2. **Task 2: Add GATE-03 full-class VPP-safety guard** — `2c29be6` (feat)

## Files Created/Modified

- `firestarter_app/tools/check_dispatch.py` — 0x35/0x39 removed from _ALGO_MEM_TYPE and dispatch(); dispatch() reformatted to two-line if-return; _PINOUT_FILE constant added; GATE-03 guard with dynamic _vpp_pinouts + _5v_eeprom_algos; updated exit gate + FAIL/PASS reporting

## Decisions Made

- Used `proto in _5v_eeprom_algos` as the predicate (not `etype == "Flash/EEPROM"`) for GATE-03, since the algorithm field is the authoritative dispatch key — no reliance on the derived electrical.type field
- Loaded pinouts.json dynamically inside `main()` rather than at module top, to keep the pattern consistent with how DB_FILE is used and avoid side effects at import time
- Pre-existing E701 violations in `dispatch()` (single-line `if condition: return value`) fixed by expanding to two-line form and applying `ruff format` — same approach used in plan 57-01 for build_db.py pre-existing violations

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed pre-existing E701 ruff violations in dispatch()**
- **Found during:** Task 1 (ruff check on check_dispatch.py)
- **Issue:** All six `if ...: return ...` statements in dispatch() were single-line (ruff E701: Multiple statements on one line). These pre-dated this plan — the style was there before any edits. The plan's acceptance criteria requires `ruff check ... pass`.
- **Fix:** Expanded all six if-return pairs to standard two-line form; applied `ruff format` to normalize spacing
- **Files modified:** `firestarter_app/tools/check_dispatch.py`
- **Verification:** `ruff check tools/check_dispatch.py && ruff format --check tools/check_dispatch.py` exits 0; all assertions pass
- **Committed in:** 89cae4e (Task 1 commit)

---

**Total deviations:** 1 auto-fixed (Rule 1 - pre-existing ruff compliance blocker)
**Impact on plan:** Required fix — no logic change, only style. No scope creep.

## Issues Encountered

None — all insertion points matched the patterns.md specification exactly. GATE-03 produced 0 violations on the current DB as predicted by research (AT29C256/AT29LV256 route to configure_flash4, not configure_eprom).

## Next Phase Readiness

- check_dispatch.py is now the full-class GATE-03 guard — ready for plan 57-03's DB regeneration pass
- Wave-2 (57-03) can proceed: both wave-1 plans (57-01 build_db.py + 57-02 check_dispatch.py) are complete
- Phase 58 pinout additions will auto-cover under GATE-03 (dynamic pinouts.json load)

## Threat Surface Scan

No new network endpoints, auth paths, or file access patterns introduced. `_PINOUT_FILE` reads from the same `firestarter/data/` directory as `DB_FILE` — same trust boundary, same read pattern. No new threat surface.

## Self-Check

Files exist:
- `firestarter_app/tools/check_dispatch.py` — modified (confirmed in place)

Commits exist in firestarter_app submodule (v1.11-infoic-decode-correctness branch):
- 89cae4e feat(57-02): remove 0x35/0x39 from check_dispatch.py (DEC-05 sync)
- 2c29be6 feat(57-02): add GATE-03 full-class vpp-pin VPP-safety guard (GATE-03)

## Self-Check: PASSED

Both files confirmed present. Both task commits confirmed in submodule git log. 480 tests pass. ruff check + format --check clean.

---
*Phase: 57-decode-bug-fixes-protocol-map-check-dispatch-extension*
*Completed: 2026-06-08*
