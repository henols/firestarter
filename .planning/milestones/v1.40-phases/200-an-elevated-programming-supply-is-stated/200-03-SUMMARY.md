---
phase: 200-an-elevated-programming-supply-is-stated
plan: 03
subsystem: testing
tags: [firestarter_app, eprom_info, chip_database, census, vcc]

# Dependency graph
requires:
  - phase: 200-an-elevated-programming-supply-is-stated
    provides: "plan 200-01's _SHIELD_FIXED_VCC_MV and programming_vcc_over_rail_mv in firestarter/eprom_info.py -- the shipped predicate this census imports rather than reimplements"
provides:
  - "tests/test_programming_vcc_census.py -- the 284-of-746-row census, asserted as an equality against the SHIPPED predicate over the live database, proved non-vacuous four separate ways"
  - "the pinned 3-versus-281 datasheet-cited-provenance split behind the 2026-09-19 amendment of D-04's verb"
  - "the pinned disjointness (overlap 0) between Phase 198's 28-row VOLT-03 set and the 284-row elevated set"
affects: []

# Actuals (#2632)
actuals:
  tokens: 5400
  tasks: 2
  commits: 2
plan_head_before: cc99e03

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Single _census(db) helper every test calls, returning a five-tuple of rows plus four histograms, so a failure names which property moved rather than which reimplementation disagreed with which -- carried over unchanged from tests/test_vpp_rail_classification.py (Phase 199)."
    - "Source-shape guard whose own literals are all `+`-joined fragments, so the guard cannot count or match its own definition -- same discipline as the Phase 199 template."
    - "part_number comma-split before override-key matching (MANUFACTURER/ALIAS), because the field holds comma-joined aliases such as MBM27C1000P,MBM27C1000."

key-files:
  created:
    - firestarter_app/tests/test_programming_vcc_census.py

key-decisions:
  - "Split Task 1's and Task 2's file-writing into two atomic commits matching the plan's task boundaries: the first commit ships the five census legs with a 5-item Coverage docstring; the second extends the same file to eleven legs (boundary, fail-open, three non-vacuity mutations, source-shape guard) with the docstring's Coverage list extended to match, exactly as the plan's Task 2 action specifies ('Extend the module docstring's numbered Coverage: list so it covers all eleven legs')."
  - "All measured figures (284/746, the vdd_mv/algorithm/type/status histograms, 34 vendors, 28 VOLT-03 rows with 0 overlap, 3-versus-281 provenance) were independently re-derived from the live chip_database.json and tools/datasheet_overrides.json before writing any assertion, and matched the plan's stated figures exactly -- no wording or number needed to be revised."

requirements-completed: [VCC-01]

coverage:
  - id: D1
    description: "The shipped predicate programming_vcc_over_rail_mv selects exactly 284 of 746 rows, asserted as an equality derived from the live database, with vdd_mv/algorithm/type/status histograms, vendor count, VOLT-03 disjointness, and the 3-versus-281 datasheet-provenance split all pinned as exact equalities rather than floors."
    requirement: "VCC-01"
    verification:
      - kind: unit
        ref: "tests/test_programming_vcc_census.py -- all 11 tests (5 census legs + boundary + fail-open + 3 non-vacuity legs + source-shape guard)"
        status: pass
    human_judgment: false
  - id: D2
    description: "Every count in the module is proved capable of failing: three in-module planted mutations (injected row -> 285, rewritten vdd_mv, rewritten support_status) plus an external planted mutation on _EXPECTED_TOTAL_ROWS in this plan's own verify, all observed to fail; the on-disk chip_database.json is confirmed byte-identical to the phase base (0d6be3f) before and after a full module run."
    verification:
      - kind: unit
        ref: "tests/test_programming_vcc_census.py::test_injecting_a_synthetic_row_makes_the_total_go_to_285, ::test_rewriting_a_vdd_value_moves_the_histogram, ::test_rewriting_a_support_status_breaks_the_all_supported_claim, ::test_module_source_shape_guards_against_weakening"
        status: pass
      - kind: other
        ref: "external sed-planted mutation of _EXPECTED_TOTAL_ROWS to 283, re-run as its own verify command"
        status: pass
    human_judgment: false

# Metrics
duration: ~25min
completed: 2026-09-19
status: complete
---

# Phase 200 Plan 03: The 284-row elevated-programming-VCC census Summary

**284 of 746 rows in the live `chip_database.json` now have a falsifiable, non-vacuous test asserting they need more than the shield's fixed 5.0 V rail — pinned against the shipped predicate, not a copy of it, with the 3-versus-281 datasheet-provenance split and the Phase 198 VOLT-03 disjointness (overlap 0) both measured and asserted as exact equalities.**

## Performance

- **Duration:** ~25 min
- **Completed:** 2026-09-19
- **Tasks:** 2
- **Files modified:** 1 (new file)

## Accomplishments
- `firestarter_app/tests/test_programming_vcc_census.py` created (509 lines, 11 tests), importing `_SHIELD_FIXED_VCC_MV` and `programming_vcc_over_rail_mv` from `firestarter.eprom_info` — zero local reimplementation of the predicate.
- Five census legs (Task 1): row total (746) and `vdd_mv` histogram (`{5500: 164, 6000: 8, 6250: 7, 6500: 105}`) against `_EXPECTED_TOTAL_ROWS = 284`; all-supported/all-UV-EPROM; algorithm split (`{7: 161, 8: 102, 11: 21}`) and 34-vendor count; VOLT-03 28-row disjointness (overlap 0); the 3-versus-281 datasheet-cited-provenance split (`FUJITSU/MBM27128`, `FUJITSU/MBM27C1001`, `FUJITSU/MBM27C4001`).
- Six more legs (Task 2): strictly-above-the-rail boundary (5000 excluded, 5001 included); six D-06 fail-open cases (absent/`None`/`0`/non-numeric `vdd_mv`, absent `electrical`, `None` record) — all return `None`, none raise; three planted-mutation non-vacuity legs (injected row → 285, rewritten `vdd_mv`, rewritten `support_status`); a source-shape guard whose own literals are `+`-joined so it cannot count or match its own definition.
- Every measured figure in the module was independently re-derived from the live `chip_database.json` and `tools/datasheet_overrides.json` before being written into an assertion, and matched the plan's stated numbers exactly — no wording or number needed correction.
- `firestarter/data/chip_database.json` confirmed byte-identical to the phase base `0d6be3f` (git hash-object `6ee16860a3c679f5831b690ce622bfc7f0635896`, identical before and after a full module run) and `tools/datasheet_overrides.json` untouched — both are read-only inputs to this module.
- External planted mutation (`_EXPECTED_TOTAL_ROWS` 284 → 283 via `sed`, then restored): `mutated_rc=1` — the total-row leg failed as required, proving the 284 is a real equality and not decorative.
- Full `tests/` tree on the Python 3.11 CI replica: **2100 passed / 36 snapshots**, up from the pre-plan baseline of **2089 passed / 36 snapshots** — exactly the 11 new legs, nothing else moved.

## Task Commits

Each task was committed atomically, inside `firestarter_app` on `v1.40-program-parameter-fidelity`:

1. **Task 1: The census — 284 of 746, asserted against the shipped predicate and against the live database** - `5cf4cb1` (test)
2. **Task 2: The boundary, the silence, and proof that every count can fail** - `6a45804` (test)

**Gitlink advance:** `99efdbf6` (docs, meta repo) — advances the `firestarter_app` submodule pointer to `6a45804`.

**Plan metadata:** committed separately in the meta repo per this plan's `<commit_protocol>`.

_Note: `plan_head_before: cc99e03` is the `firestarter_app` HEAD immediately before this plan's first commit (the HEAD left by plan 200-02); `git rev-list --count cc99e03..HEAD` inside `firestarter_app` reports 2, matching the two task commits above (the gitlink advance is a meta-repo commit, counted separately)._

## Files Created/Modified
- `firestarter_app/tests/test_programming_vcc_census.py` — new module, 509 lines: `_census(db)` five-tuple helper, `_load_db`/`_load_overrides`/`_all_chips`, 14 named constants, 11 tests, and the source-shape guard's three guard structures (`_REQUIRED_TEST_NAMES`, `_DEFINITION_GUARD_COUNTS`, `_WEAKENING_IDIOMS`).

## Decisions Made
- Split the single-file deliverable into two atomic commits along the plan's own task boundaries, rather than one commit for the whole file: Task 1's commit ships the 5-leg module with a 5-item `Coverage:` docstring (no forward references to legs that do not exist yet), and Task 2's commit extends the same file to 11 legs with the docstring's `Coverage:` list extended to match — exactly what the plan's Task 2 action text specifies ("Extend the module docstring's numbered Coverage: list so it covers all eleven legs"). Verified both intermediate states pass every one of their own task's `<verify>` legs independently before committing.
- No numeric or wording correction was needed anywhere in the module: every plan-stated figure (284/746, the four histograms, 34 vendors, 28/0 VOLT-03, 3/281 provenance) was measured fresh against the live files before being written into an assertion and matched on the first attempt.

## Deviations from Plan

None - plan executed exactly as written. All measured figures matched the plan's stated numbers; no fix-attempt cycles were needed on any acceptance criterion.

## Issues Encountered
None.

## User Setup Required
None — no external service configuration required.

## Next Phase Readiness
- All three plans in Phase 200 (200-01, 200-02, 200-03) are now complete and committed on `v1.40-program-parameter-fidelity`, inside the `firestarter_app` submodule, with the meta gitlink advanced after each.
- VCC-01's scope is now a falsifiable, non-vacuous measurement (284 of 746 rows) rather than a number in a planning document; VCC-02's shortfall-statement shape (plan 200-01) and its two rendered-output classes (plan 200-02) are pinned alongside it.
- No blockers. STATE.md, ROADMAP.md, and REQUIREMENTS.md updates are deferred to the orchestrator per this plan's execution instructions.

---
*Phase: 200-an-elevated-programming-supply-is-stated*
*Completed: 2026-09-19*

## Self-Check: PASSED

- `FOUND: firestarter_app/tests/test_programming_vcc_census.py`
- `FOUND: .planning/phases/200-an-elevated-programming-supply-is-stated/200-03-SUMMARY.md`
- Commit `5cf4cb1` (test, Task 1) present in `firestarter_app` history
- Commit `6a45804` (test, Task 2) present in `firestarter_app` history
- Commit `99efdbf6` (gitlink advance) present in meta history
- `git -C firestarter_app rev-parse --abbrev-ref HEAD` == `v1.40-program-parameter-fidelity`
- `git rev-parse --abbrev-ref HEAD` (meta) == `v1.40-program-parameter-fidelity`
