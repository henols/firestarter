---
phase: 133-sdp-leg-mechanism
plan: 07
subsystem: testing
tags: [ci-parity, mypy, requirements, honesty-record, sdp, chip_test]

# Dependency graph
requires:
  - phase: 133-sdp-leg-mechanism (plans 01-06)
    provides: "the phase's final engine + gate source at commit 57e8eb5 -- _run_step's widened
      exception handling, the _dispatch_sdp arm, the cleanup registry drain, the broad-except
      deny bucket, and the op-registration parity gate -- this plan measures and closes against
      that final state, adding no further engine or test-module code itself"
provides:
  - "133-CI-PARITY.md: the after-half of the CI-parity recipe with a real mypy count (33 errors,
    watermark 35, checked 124 source files), the no-board condition asserted, leg 4's local
    exit 2 recorded as expected, and A1 discharged by measurement with its real texture (not a
    clean zero-delta) stated plainly"
  - "133-RECORD.md: requirement accounting for LEG-09/10/11/15, decision coverage for D-01..D-16
    (D-05/D-07/D-10-D-16-reconciliation/D-12 flagged non-literal or refined), all five ROADMAP
    criteria discharged with named evidence, 10 corrections carried forward, 6 residuals, and
    the Evidence Ceiling stated plainly"
  - "REQUIREMENTS.md: exactly LEG-09, LEG-10, LEG-11, LEG-15 ticked with evidence clauses naming
    the delivering plan and green pytest -k selectors; the other 14 LEG rows (Phase 134's)
    byte-unchanged"
affects: ["134-plan-derived-sdp-oracle"]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Delta-against-baseline measurement discipline: every after-figure in 133-CI-PARITY.md is
      reported as an explicit delta against 133-BASELINE.md's pre-edit figures, not a bare number"
    - "Requirement-tick centralization: one plan per phase permitted to edit REQUIREMENTS.md,
      ticking against named plan+test evidence, diff-asserted confined to exactly those lines"

key-files:
  created:
    - .planning/phases/133-sdp-leg-mechanism/133-CI-PARITY.md
    - .planning/phases/133-sdp-leg-mechanism/133-RECORD.md
  modified:
    - .planning/REQUIREMENTS.md

key-decisions:
  - "mypy count reported honestly as 32->33 (not a clean zero-delta): plan 133-06's import of
    tools.check_devtest_orchestrator made mypy reach that module for the first time, surfacing
    one pre-existing (133-05-introduced, never-before-reachable) type error -- recorded as a
    gate blind spot, not smoothed over as pre-existing"
  - "Traceability table's LEG-09/10/11/15 rows (Pending -> Complete) updated alongside the
    checkbox ticks, matching house convention already visible on every ticked GATE/RETIRE row --
    scoped to the same four IDs, not creep into the other 14"
  - "Criterion 4's group=None clause recorded as satisfied VACUOUSLY (no Step.group field exists)
    with intent met by _SDP_OPS membership instead -- never restated as tested"
  - "Criterion 5's/LEG-15's inherited 'eight previously fail-open registries' recorded as
    measured-wrong; real breakdown is 6 policed registries + 6 declared non-registries, quoted
    from 133-06-SUMMARY.md's own measured census, not re-derived"

requirements-completed: [LEG-09, LEG-10, LEG-11, LEG-15]

coverage:
  - id: D1
    description: "The after-half of the CI-parity recipe measured and recorded with a real mypy
      count (33 errors, watermark 35, checked 124 source files), the no-board condition
      asserted, leg 4's local exit 2 recorded as expected, and A1 discharged by measurement"
    verification:
      - kind: other
        ref: "tools/ci_replica_venv.sh (CI-REPLICA: PASS, mypy errors: 33 watermark: 35, checked 124 source files); tools/ci_parity.sh (CI-PARITY: FAIL (legs:4), leg 4 exit 2 expected); pytest tests/ -q (1338 passed, 30 snapshots)"
        status: pass
    human_judgment: false
  - id: D2
    description: "LEG-09, LEG-10, LEG-11, LEG-15 ticked in REQUIREMENTS.md, each with an evidence
      clause naming the delivering plan and at least one green pytest -k selector; exactly
      fourteen LEG rows remain open; nothing else in the file changed"
    requirement: "LEG-09"
    verification:
      - kind: other
        ref: "inline python REQ_FENCE_OK check (4 ticked: LEG-09/10/11/15; 14 open); git diff -- .planning/REQUIREMENTS.md confined to those four entries"
        status: pass
    human_judgment: false
  - id: D3
    description: "133-RECORD.md discharges all five ROADMAP success criteria with named evidence,
      carries criterion 4's vacuity correction and criterion 5's measured-count correction, D-01..D-16
      decision coverage with non-literal honourings flagged, corrections, residuals, and the
      Evidence Ceiling"
    verification:
      - kind: other
        ref: "grep checks: 6 numbered sections present; 'vacuous' present; 'measured-wrong' present; 'v1.22 C-5 overclaim' present; all five Evidence-Ceiling clauses present"
        status: pass
    human_judgment: false

# Metrics
duration: ~90min
completed: 2026-08-04
status: complete
---

# Phase 133 Plan 07: SDP Leg Mechanism -- Phase Close Summary

**Measured the after-half of the CI-parity recipe (33 mypy errors / watermark 35, checked 124
source files, 1338 tests passing), wrote the phase's honesty record discharging all five ROADMAP
criteria with named evidence (criterion 4's `group=None` recorded vacuous, criterion 5's "eight
registries" corrected to a measured 6+6 breakdown), and ticked exactly LEG-09/10/11/15 in
`REQUIREMENTS.md` against named plan evidence -- closing Phase 133 with the mechanism proven and
the Evidence Ceiling (nothing about SDP behaviour on silicon) stated plainly.**

## Performance

- **Duration:** ~90 min
- **Completed:** 2026-08-04
- **Tasks:** 2
- **Files modified:** 3 (2 created, 1 modified)

## Accomplishments

- Measured the no-board condition (still absent), `bash tools/ci_parity.sh` (legs 1-3 exit 0, leg
  4's local exit 2 recorded as expected -- ambient devcontainer numpy PEP-695 stub truncation,
  unchanged reason from the baseline and from Phase 131's own record), and `pytest tests/ -q`
  (**1338 passed**, 30 snapshots, +37 over `133-BASELINE.md`'s 1301, attributed plan-by-plan
  against each plan's own SUMMARY).
- Ran `tools/ci_replica_venv.sh` for the **real** mypy count: **33 errors (watermark 35), checked
  124 source files** -- both in range (`33 <= 35`, `124 >= 120`). Reported the delta against the
  baseline's 32/123 honestly: **not** a clean zero-delta. Plan 133-06's import of
  `tools.check_devtest_orchestrator` (to read `_HANDLER_FUNCTION_NAMES`) made mypy reach that
  module for the first time -- its only prior test coverage drives it via `subprocess`, never
  `import` -- surfacing one pre-existing type error introduced by plan 133-05's own commit
  (`feb90f6`), invisible to every gate in the phase until 133-06's import exposed it. Recorded this
  as a **gate blind spot** the phase's own toolchain had, not as an inert "pre-existing" condition.
- Confirmed exactly two new source files across the whole phase (`ls tests/*.py | wc -l` = 90 = 88
  + 2), spending both slots of the `MIN_CHECKED_SOURCE_FILES` margin D-15 budgeted exactly; confirmed
  `pyproject.toml` and `tools/check_mypy_watermark.py` byte-unchanged.
- Wrote `133-CI-PARITY.md` (the after-half recipe, delta-annotated against `133-BASELINE.md`
  throughout) and `133-RECORD.md` (six mandatory sections: requirement accounting; D-01..D-16
  decision coverage with D-05/D-07/D-10-D-16-reconciliation/D-12 explicitly flagged non-literal or
  refined, plus the `OP_SDP_LOCK` ∈ `_DESTRUCTIVE_OPS` derivation named as such; all five ROADMAP
  criteria discharged with named evidence and their two mandatory corrections; 10 corrections
  carried forward; 6 residuals each with an owner or a stated reason for having none; the Evidence
  Ceiling's five clauses plus the v1.22 C-5 overclaim class named).
- Ticked **exactly** LEG-09, LEG-10, LEG-11, LEG-15 in `.planning/REQUIREMENTS.md`, each with an
  evidence clause naming the delivering plan's commit(s) and green `pytest -k` selectors; updated
  the traceability table's status column for the same four IDs (Pending → Complete), matching the
  house convention already visible on every ticked GATE/RETIRE row. Verified via the plan's own
  inline check: `REQ_FENCE_OK ['LEG-09', 'LEG-10', 'LEG-11', 'LEG-15']`, 14 LEG rows still open, and
  `git diff -- .planning/REQUIREMENTS.md` confined to exactly those four entries.

## Task Commits

Each task was committed atomically, in the meta repo (`/workspaces`, branch
`gsd/v1.30-sdp-surface-retirement-behavioral-lock-proof`) -- this plan makes no edit inside the
`firestarter_app` submodule:

1. **Task 1: Measure and record the after-half of the CI-parity recipe with a real mypy count** --
   `52dbd98` (docs)
2. **Task 2: Write 133-RECORD.md and tick LEG-09/10/11/15 in REQUIREMENTS.md** -- `bd58946` (docs)

## Files Created/Modified

- `.planning/phases/133-sdp-leg-mechanism/133-CI-PARITY.md` -- new: the after-half CI-parity
  recipe, every figure reported as a delta against `133-BASELINE.md`.
- `.planning/phases/133-sdp-leg-mechanism/133-RECORD.md` -- new: the phase's six-section honesty
  record.
- `.planning/REQUIREMENTS.md` -- modified: exactly the four LEG-09/10/11/15 entries (checkbox +
  evidence clause) plus their traceability-table status; no other line touched.

## Decisions Made

- **Reported the mypy delta (32→33) honestly rather than smoothing it into "unchanged."** The
  dispatch context's own sharper framing was carried forward verbatim into both `133-CI-PARITY.md`
  and `133-RECORD.md`: 133-05 shipped a real type error no gate in the phase's own toolchain could
  see at the time, because the affected module's only test coverage shells out via `subprocess`
  rather than importing it. This is a phase-owned gate blind spot, not inert pre-existing debt.
- **Updated the traceability table's status for the same four IDs alongside the checkbox ticks.**
  Every already-ticked GATE/RETIRE row in `REQUIREMENTS.md` shows "Complete" in both places; leaving
  LEG-09/10/11/15 at "Pending" in the tracking table while their checkboxes read `[x]` would be an
  internal inconsistency for a later reader (Phase 137's ledger) to trip over. Scoped strictly to
  the same four IDs -- the diff still touches none of the other fourteen LEG rows.
- **Quoted each prior plan's own SUMMARY figures verbatim rather than re-deriving them** in the
  test-count delta table and the registry-census breakdown, per this plan's own instruction not to
  paraphrase a measurement it did not take.

## Deviations from Plan

None. All acceptance criteria were met on first implementation: the real mypy count landed in
range on the first `ci_replica_venv.sh` run, the `REQUIREMENTS.md` edit was confined to the four
lines on the first attempt (confirmed by `git diff`), and no gate threshold needed to be moved.

## Issues Encountered

None beyond the already-logged, out-of-scope findings in `deferred-items.md` (from plan 133-06),
both re-confirmed still pre-existing and unrelated to this plan: the three `tools/` ruff findings
from Phase 63/70, and the mypy blind-spot finding this plan's own record restates with sharper
attribution (133-05, not "pre-existing").

## User Setup Required

None -- no external service configuration required.

## Next Phase Readiness

- Phase 133 is closed: LEG-09, LEG-10, LEG-11, LEG-15 are ticked with evidence; exactly fourteen
  LEG rows remain open, all belonging to Phase 134.
- `133-RECORD.md`'s Evidence Ceiling section and Forward-handoff-equivalent residuals (D-07's
  forfeited report, D-16's failed unlock not user-visible until Phase 134's `HELD`/`NOT-RUN` field,
  research assumption A2, the still-unowned watermark ratchet, the mypy blind-spot correction) are
  the inputs Phase 134 and Phase 137's ledger both inherit.
- No push, merge, tag, CI dispatch, or release occurred; no gate threshold was moved;
  `pyproject.toml` and `tools/check_mypy_watermark.py` are confirmed byte-unchanged.
- No blockers. STATE.md and ROADMAP.md are intentionally NOT modified by this plan -- the
  orchestrator owns those writes after the wave completes.

---
*Phase: 133-sdp-leg-mechanism*
*Completed: 2026-08-04*

## Self-Check: PASSED

- FOUND: `.planning/phases/133-sdp-leg-mechanism/133-CI-PARITY.md`
- FOUND: `.planning/phases/133-sdp-leg-mechanism/133-RECORD.md`
- FOUND: `.planning/phases/133-sdp-leg-mechanism/133-07-SUMMARY.md`
- FOUND commit: `52dbd98` (meta repo)
- FOUND commit: `bd58946` (meta repo)
- FOUND commit: `24003a8` (meta repo)
