---
phase: 178-fault-attribution-the-two-axis-vocabulary
plan: 03
subsystem: dev-test-diagnostics
tags: [chip_test, diagnostic_report, report_shapes, blast-radius-invariance, status-axis, fixture-corpus]

# Dependency graph
requires:
  - phase: 178-fault-attribution-the-two-axis-vocabulary
    provides: "plan 178-01's STATUS_COMPLETE/ERROR/SKIP vocabulary, StepResult.status, the re-pointed (SerialError, HardwareOperationError) transport arm, and plan 178-02's ATTR-04 Leg B -- this plan registers the 18th frozen shape that finally EXERCISES the status axis in the corpus itself"
provides:
  - "D-178-1: the operator decision on how the frozen shape is constructed (real-path, Option A), recorded in 178-DECISIONS.md"
  - "The reserved shape_id attr01-status-axis-transport-fault registered across all eight gate-enforced sites (_BUILDERS, FROZEN_HASHES, RESERVED_SHAPE_IDS, LADDER_PINS, _PINNED_SHAPE_ID_SET, shape_ids.json, the committed snapshot, and the two prose repairs) plus its measured hash 93cef8030c40"
  - "ATTR-04's Leg A: the whole 18-shape corpus reproduces its FROZEN_HASHES entries, and all 17 inherited hashes are measured byte-identical to their pre-phase values"
  - "RK-174-09's after_hash confirmed still None -- the deliberate non-move, sealed as a measurement in evidence/178-03-attr04-seal.txt"
affects: [178-04-attr06-rail-reading-disclosure]

# Actuals (#2632) -- pairs with the plan's estimate to calibrate future estimates.
actuals:
  tokens: 4037
  tasks: 3
  commits: 3

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Reserved shape_id registration is an eight-gate-enforced-site, single-commit operation (builder, _BUILDERS, FROZEN_HASHES, RESERVED_SHAPE_IDS removal, LADDER_PINS, _PINNED_SHAPE_ID_SET, shape_ids.json, generated snapshot) -- any partial state is red by construction because SHAPE_IDS derives from _BUILDERS"
    - "A real-path frozen shape's fault injection rides Mock's side_effect-over-return_value precedence: setting operator.check_eprom_id.side_effect AFTER _fixed_return_operator() builds the double, with no edit to the helper or to _build_real_path_report"

key-files:
  created:
    - firestarter_app/tests/fixtures/reports/attr01-status-axis-transport-fault.json
  modified:
    - firestarter_app/tests/fixtures/report_shapes.py
    - firestarter_app/tests/fixtures/shape_ids.json
    - firestarter_app/tests/test_blast_radius_invariance.py
    - .planning/phases/178-fault-attribution-the-two-axis-vocabulary/178-DECISIONS.md

key-decisions:
  - "D-178-1: Option A (real-path), operator-selected. Built via _build_real_path_report(chip=\"m27c512\", write_scope=\"full\", operator=<_fixed_return_operator() with check_eprom_id.side_effect=SerialError(...)>, runs=2) -- chip m27c512 was picked because it is already exercised by three registered real-path shapes, so derive_plan coverage was understood rather than novel. Option B's statuses= seam on build_shape_from_step_specs was explicitly rejected and NOT added."
  - "The new shape's measured hash is 93cef8030c40, confirmed distinct from all 17 inherited FROZEN_HASHES values before being written."
  - "The measured (proposed_disposition, ladder_state) pair for the new shape is (_DISPOSITION_INCONCLUSIVE, \"\") -- the ERROR guard arm plan 178-01 added routes it there, never to the community-reported candidate arm. LADDER_PINS' four-distinct-pairs coverage sentinel stays at 4 since this pair already existed (gh47-sst27sf512-pass, sst27sf512-six-step-readback-gated)."
  - "Both prose repairs (module docstring's reserved-name roster, and test_build_shape_raises_for_every_reserved_shape_id's stale 'all three' sentence) were made in the same commit as the registration, per the plan's own instruction."

patterns-established: []

requirements-completed: [ATTR-01, ATTR-04]

coverage:
  - id: D1
    description: "The frozen corpus carries a shape whose steps exercise the status axis -- attr01-status-axis-transport-fault is registered, removed from RESERVED_SHAPE_IDS, and its to_dict() snapshot pins the exported key name status and the value ERROR on the transport-faulted id step"
    requirement: "ATTR-01"
    verification:
      - kind: unit
        ref: "tests/test_blast_radius_invariance.py (18-shape FROZEN_HASHES suite, test_shape_id_set_is_pinned_and_disjoint_from_reserved, test_shape_ids_frozen_hashes_ladder_pins_and_snapshots_agree, test_committed_snapshot_matches_a_fresh_regeneration[attr01-status-axis-transport-fault])"
        status: pass
      - kind: e2e
        ref: ".planning/phases/178-fault-attribution-the-two-axis-vocabulary/evidence/178-03-shape-registration.txt (shape_count=18, registered=True, snapshot_step_status_values=COMPLETE,ERROR,SKIP, new_hash=93cef8030c40)"
        status: pass
    human_judgment: false
  - id: D2
    description: "Registering the status-bearing shape does not move any of the 17 pre-existing frozen hashes -- the status axis contributes nothing to dedup_fingerprint even at corpus scale with a status-bearing shape present"
    requirement: "ATTR-04"
    verification:
      - kind: unit
        ref: "tests/test_blast_radius_invariance.py::test_dedup_fingerprint_is_frozen (all 17 inherited parametrizations unchanged)"
        status: pass
      - kind: e2e
        ref: ".planning/phases/178-fault-attribution-the-two-axis-vocabulary/evidence/178-03-shape-registration.txt (inherited_count=17, inherited_drifted=) and evidence/178-03-attr04-seal.txt (corpus_size=18, stale_frozen=, inherited_drifted=)"
        status: pass
    human_judgment: false
  - id: D3
    description: "RK-174-09 stays undeclared (after_hash=None) and the ledger is byte-unchanged at 8 rows -- the non-move is a measurement, not a bookkeeping edit"
    requirement: "ATTR-04"
    verification:
      - kind: unit
        ref: "tests/test_rekey_ledger.py (full suite, including test_no_declared_row_has_after_hash_equal_to_before_hash and test_undeclared_after_hash_routes_to_before_hash_and_never_abstains)"
        status: pass
      - kind: e2e
        ref: ".planning/phases/178-fault-attribution-the-two-axis-vocabulary/evidence/178-03-attr04-seal.txt (rows=8, rk09_after_is_none=True, rk09_before=14d306256076, undeclared_count=4, ledger_diff=0, cross-tree checker: OK: 8 ledger row(s), 8 MILESTONES.md row(s) bound)"
        status: pass
    human_judgment: false

duration: 20min
completed: 2026-09-06
status: complete
---

# Phase 178 Plan 03: Fault Attribution -- the Two-Axis Vocabulary Summary

**Registered the reserved shape `attr01-status-axis-transport-fault` (real-path, hash `93cef8030c40`) across all eight gate-enforced sites, growing the frozen corpus to 18 entries while every one of the 17 inherited `dedup_fingerprint` hashes measured unmoved -- ATTR-04's Leg A stopped being an argument about an empty set.**

## Performance

- **Duration:** ~20 min
- **Completed:** 2026-09-06T13:05:00Z
- **Tasks:** 3 (Task 1: checkpoint decision, resumed from operator answer; Task 2: eight-site registration; Task 3: the ATTR-04 seal)
- **Files modified:** 5 (1 meta-repo decisions file, 3 app fixture/test files, 1 new committed snapshot) plus 2 evidence files

## Accomplishments

- Recorded `D-178-1` (Option A, real-path) into `178-DECISIONS.md`, resuming a prior executor's checkpoint at exactly the point it stopped.
- Added `_build_attr01_status_axis_transport_fault()` -- a real `m27c512` full-scope run through `derive_plan`/`run_plan` whose operator double raises `SerialError` from `check_eprom_id`, exercising the ACTUAL re-pointed transport-fault arm (`VERDICT_SKIPPED`/`STATUS_ERROR`) and the ACTUAL destructive-write gate closure, never a hand-specified stand-in.
- Landed all eight gate-enforced edit sites plus the two stale-prose repairs in one commit: `_BUILDERS`, `FROZEN_HASHES` (measured `93cef8030c40`, confirmed distinct from all 17 others), `RESERVED_SHAPE_IDS` (now holds only `uv-slot-write-pass`), `LADDER_PINS` (measured `(_DISPOSITION_INCONCLUSIVE, "")`), `_PINNED_SHAPE_ID_SET`, `tests/fixtures/shape_ids.json`, and the generated (never hand-written) snapshot.
- Sealed ATTR-04's Leg A as a measurement, not an assertion: the full 18-shape corpus reproduces, the 17 inherited literals are unmoved, `RK-174-09`'s `after_hash` is confirmed still `None`, the ledger stays byte-unchanged at 8 rows, and the cross-tree checker binds 8 to 8.

## Task Commits

1. **Task 1: D-178-1 recorded (checkpoint resume)** - `bf9d4774` (docs, meta-repo)
2. **Task 2: Register the reserved shape -- eight gate-enforced edit sites** - `c753b47` (test, firestarter_app)
3. **Task 3: The ATTR-04 seal (evidence-only, no source/test edit)** - committed with this SUMMARY (meta-repo)

**Plan metadata:** committed separately in the meta-repo (`.planning/`), together with Task 3's evidence.

## Files Created/Modified

- `.planning/phases/178-fault-attribution-the-two-axis-vocabulary/178-DECISIONS.md` - `D-178-1` recorded (Option A, real-path)
- `firestarter_app/tests/fixtures/report_shapes.py` - new builder `_build_attr01_status_axis_transport_fault`, `_BUILDERS`/`FROZEN_HASHES` entries, removed from `RESERVED_SHAPE_IDS`, module docstring repaired, new `SerialError` import
- `firestarter_app/tests/fixtures/shape_ids.json` - 17 -> 18 committed sorted anchor entries
- `firestarter_app/tests/test_blast_radius_invariance.py` - `LADDER_PINS`/`_PINNED_SHAPE_ID_SET` entries, `test_build_shape_raises_for_every_reserved_shape_id`'s stale count sentence repaired
- `firestarter_app/tests/fixtures/reports/attr01-status-axis-transport-fault.json` - new committed snapshot, generated by `tools/snapshot_report_shapes.py`, pinning `status`/`run_status` at schema 1.8
- `.planning/phases/178-fault-attribution-the-two-axis-vocabulary/evidence/178-03-shape-registration.txt` - Task 2's measured registration evidence
- `.planning/phases/178-fault-attribution-the-two-axis-vocabulary/evidence/178-03-attr04-seal.txt` - Task 3's measured ATTR-04 seal

## Decisions Made

- Followed the operator's `D-178-1` answer exactly: real-path construction via `_build_real_path_report`, chip `m27c512` (already exercised by three registered real-path shapes), `SerialError` side_effect on `check_eprom_id` set after the fixed-return double is built -- `_build_real_path_report` needed no edit, since Mock's `side_effect` takes precedence over the `return_value` it stamps.
- Did NOT add a `statuses=` seam to `build_shape_from_step_specs` (Option B, explicitly rejected).
- Both prose repairs (module docstring reserved-name roster, and the stale "all three `RESERVED_SHAPE_IDS` names" sentence) were made in the same commit as the registration, since the docstring was already stale before this phase (two names, not three) and would have stayed stale otherwise.

## Deviations from Plan

None - plan executed exactly as written. Task 1 was already gated by a prior executor's checkpoint stop; this session recorded the operator's answer and proceeded through Tasks 2 and 3 without incident. No auto-fix was needed: the eight-site registration, the measured hash, the measured ladder pin, and the generated snapshot all landed clean on the first attempt, and every `<verify>` block in the plan passed as written.

## Issues Encountered

None -- both automated `<verify>` blocks for Task 2 passed in full (the registry-closure/oracle/ledger check and the diff/ruff/porcelain check), and Task 3's precondition (`python3 tools/rekey/check_rekey_ledger.py` runnable from `/workspaces`) held, producing a clean `OK: 8 ledger row(s), 8 MILESTONES.md row(s) bound` seal.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- The frozen corpus now carries 18 shapes, one of which genuinely exercises the status axis end-to-end (real transport fault, real gate closure, real hash), and ATTR-04's Leg A is measured rather than argued from an empty set.
- `RESERVED_SHAPE_IDS` retains exactly one name, `uv-slot-write-pass` (Phase 179's), ready for that phase's own registration to follow the same eight-site protocol this plan exercised.
- Plan `178-04` (ATTR-06 rail-reading disclosure) can proceed independently; it does not depend on this plan's fixture-corpus surface.
- No blockers.

---
*Phase: 178-fault-attribution-the-two-axis-vocabulary*
*Completed: 2026-09-06*

## Self-Check: PASSED
- FOUND: .planning/phases/178-fault-attribution-the-two-axis-vocabulary/178-DECISIONS.md
- FOUND: firestarter_app/tests/fixtures/report_shapes.py, shape_ids.json, reports/attr01-status-axis-transport-fault.json, test_blast_radius_invariance.py
- FOUND: evidence/178-03-shape-registration.txt, evidence/178-03-attr04-seal.txt
- FOUND: commit bf9d4774 (Task 1, meta-repo)
- FOUND: commit c753b47 (Task 2, firestarter_app)
- FOUND: commit ede78e6b (Task 3 + SUMMARY.md, meta-repo)
