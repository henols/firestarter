---
phase: 174-blast-radius-invariance-harness
plan: 06
subsystem: testing
tags: [rekey-ledger, checker, blast-radius, deepcopy, aliasing, gate-06, tdd]

requires:
  - phase: 174-blast-radius-invariance-harness
    provides: "The six-row LEDGER, the sixteen-shape report registry, FROZEN_HASHES/LADDER_PINS, and the meta-side checker skeleton plans 174-01 through 174-05 built"
provides:
  - "A fail-closed tools/rekey/check_rekey_ledger.py: duplicate MILESTONES.md ledger_id rows collide at exit 2, the undeclared branch validates shape_id/before_hash/the exact (undeclared) literal, and an emptied ledger table is an exit-1 ERROR"
  - "Seven subprocess-level checker legs in firestarter_app/tests/test_rekey_ledger.py, each seen RED against the pinned pre-fix checker blob before GREEN"
  - "A non-aliasing report-shape registry: _clone_with_chip_override deep-copies results and plan, closing CR-01"
  - "Three RED-then-GREEN evidence transcripts binding every new leg to the two pinned pre-fix blobs"
affects: [177, 178, 179, 181]

actuals:
  tokens: 5839
  tasks: 3
  commits: 11

tech-stack:
  added: []
  patterns:
    - "Anti-vacuity via pinned pre-fix git blob materialized with git cat-file blob, never HEAD~1, so the RED half of a RED/GREEN pair stays reproducible forever"
    - "copy.deepcopy on a cached builder's output to break cross-key aliasing without dropping the cache"

key-files:
  created:
    - .planning/phases/174-blast-radius-invariance-harness/evidence/174-06-duplicate-row-red-green.txt
    - .planning/phases/174-blast-radius-invariance-harness/evidence/174-06-undeclared-row-red-green.txt
    - .planning/phases/174-blast-radius-invariance-harness/evidence/174-06-shape-aliasing-red-green.txt
  modified:
    - tools/rekey/check_rekey_ledger.py
    - firestarter_app/tests/test_rekey_ledger.py
    - firestarter_app/tests/fixtures/report_shapes.py
    - firestarter_app/tests/test_blast_radius_invariance.py

key-decisions:
  - "CR-01 fixed via copy.deepcopy(report.results)/copy.deepcopy(report.plan) in _clone_with_chip_override, not by dropping @functools.cache from _build_m27c512_full_all_ok — deepcopy targets the actual cross-shape-id aliasing defect, preserves the cache's cost benefit (the two derivatives stay uncached and already pay derive_plan/run_plan themselves), and avoids a seven-to-one cache asymmetry across the eight real-path builders that a partial cache removal would create."
  - "The undeclared branch's after-cell check now requires the exact literal '(undeclared)' rather than merely failing a twelve-lowercase-hex regex, closing the boundary hole where an eleven- or fourteen-character hex string, or an uppercase hash, silently passed."
  - "A zero-row MILESTONES.md table against a non-empty ledger is now an explicit exit-1 ERROR — deleting the whole ledger table is closed as a route past the gate on the meta side, matching D-10's existing app-side closure."

requirements-completed: [GATE-01, GATE-02, GATE-06]

coverage:
  - id: D1
    description: "A duplicated MILESTONES.md row for one ledger_id collides at exit 2 instead of the last row silently winning (CR-02 leg a)"
    requirement: "GATE-06"
    verification:
      - kind: integration
        ref: "tests/test_rekey_ledger.py#test_duplicate_milestones_row_for_one_ledger_id_fails_closed"
        status: pass
      - kind: other
        ref: "evidence/174-06-duplicate-row-red-green.txt (rc_prefix_dup=0 RED, rc_fixed_dup=2 GREEN)"
        status: pass
    human_judgment: false
  - id: D2
    description: "The undeclared branch validates shape_id, before_hash (case-sensitive, exact) and requires the after cell to be the exact '(undeclared)' literal; an emptied ledger table fails closed; output is order-stable"
    requirement: "GATE-06"
    verification:
      - kind: integration
        ref: "tests/test_rekey_ledger.py#test_corrupted_undeclared_row_shape_id_exits_one, #test_corrupted_undeclared_row_before_hash_exits_one, #test_uppercased_before_hash_exits_one, #test_after_cell_that_is_not_the_undeclared_literal_exits_one, #test_milestones_with_zero_rekey_rows_exits_one, #test_checker_error_output_is_order_stable"
        status: pass
      - kind: other
        ref: "evidence/174-06-undeclared-row-red-green.txt (six rc_prefix_*=0 RED lines, six rc_fixed_*=1 GREEN lines, order_stable=identical)"
        status: pass
    human_judgment: false
  - id: D3
    description: "No two shape_ids share a results or plan object; a mutation through a derivative no longer moves the base's frozen hash (CR-01)"
    requirement: "GATE-01"
    verification:
      - kind: integration
        ref: "tests/test_blast_radius_invariance.py#test_build_shape_never_shares_results_or_plan_between_shape_ids, #test_mutation_through_a_derived_shape_does_not_move_the_base_shapes_frozen_hash"
        status: pass
      - kind: other
        ref: "evidence/174-06-shape-aliasing-red-green.txt (prefix_alias_results=True/prefix_base_after=e9df6ca4627c RED, fixed_alias_results=False/fixed_base_after=6d3afbc52315 GREEN)"
        status: pass
    human_judgment: false

duration: 55min
completed: 2026-09-03
status: complete
---

# Phase 174 Plan 06: GATE-06 Binding Mechanism and CR-01 Aliasing Fix Summary

**Made `check_rekey_ledger.py` fail closed on duplicate/corrupted/deleted MILESTONES.md rows, and stopped three frozen report shapes from sharing one mutable `results`/`plan` object — both proven RED against pinned pre-fix blobs before GREEN.**

## Performance

- **Duration:** 55 min
- **Started:** 2026-09-03 (session start)
- **Completed:** 2026-09-03
- **Tasks:** 3 (Task 1 tracer, Task 2 auto, Task 3 auto+tdd)
- **Files modified:** 4 source files, 3 new evidence transcripts, 1 new summary

## Accomplishments

- **Task 1 (tracer):** `parse_milestones_rows` now raises `LedgerParseError` on a second row for an already-seen `ledger_id`, which `main` routes to exit 2 printing `ERROR: duplicate MILESTONES.md row for ledger_id 'RK-174-01-p177-readback-gating'`. Paired subprocess test added. Seen RED (exit 0) against the pinned pre-fix checker blob `5c0c7c9` before GREEN (exit 2).
- **Task 2:** The undeclared branch (`after_hash is None`) now compares the file's `(shape_id, before)` pair against the ledger's own values and requires the `after` cell to be the exact literal `(undeclared)`, replacing the old `_HASH_RE.match(m_row[2])` boundary hole. Added a zero-row guard: an emptied `MILESTONES.md` against a non-empty ledger is an exit-1 ERROR naming both counts. Six new subprocess legs, each seen RED then GREEN.
- **Task 3 (TDD):** `_clone_with_chip_override` now deep-copies `results` and `plan` instead of sharing the cached base's objects. RED: two new tests written and confirmed failing in isolation against the unfixed code (`AssertionError: 'm27c512-full-all-ok' and 'm27c512-full-canonical-name' share the same results object`; fingerprint moved `6d3afbc52315` → `e9df6ca4627c`). GREEN: fix applied, same tests pass, full four-module suite reports 122 passed.

## Task Commits

Meta repo (`/workspaces`):
1. **Task 1: duplicate ledger_id collision** — `12eb9cf7` (feat) — reject duplicate MILESTONES.md rows; carries `firestarter_app` gitlink bump to `2db07df` + evidence transcript
2. **Task 2: undeclared-branch validation** — `4a1bfe35` (feat) — validate shape_id/before_hash/after literal, zero-row guard; carries gitlink bump to `7367cc5` + evidence transcript
3. **Task 3: CR-01 aliasing fix** — `3a4dc611` (docs) — record CR-01 aliasing RED/GREEN transcript; carries gitlink bump to `e907e6d`

App submodule (`/workspaces/firestarter_app`, on `gsd/v1.36-dev-test-fidelity`):
1. `2db07df` (test) — bind duplicate MILESTONES.md ledger_id rows to exit 2
2. `7367cc5` (test) — bind undeclared-row shape_id/before_hash/after-literal checks
3. `64669b1` (test) — add failing tests for non-aliasing shape registry (CR-01) — **RED**
4. `c4e16c6` (feat) — deep-copy results and plan in `_clone_with_chip_override` (CR-01) — **GREEN**
5. `e907e6d` (docs) — cite the CR-01 transcript in the Reachability block; reformat

**Plan metadata:** this SUMMARY.md commit (meta, next)

_TDD gate compliance (Task 3): RED commit `64669b1` precedes GREEN commit `c4e16c6`, both in the correct order. No REFACTOR commit — the fix was already minimal._

## Files Created/Modified

- `tools/rekey/check_rekey_ledger.py` — duplicate-`ledger_id` guard in `parse_milestones_rows`; `check()`'s undeclared branch now validates `shape_id`, `before_hash` and the exact `(undeclared)` literal; zero-row guard; `_HASH_RE` removed (sole consumer gone), `_UNDECLARED` constant added; docstring corrected twice
- `firestarter_app/tests/test_rekey_ledger.py` — 7 new subprocess-level legs: `test_duplicate_milestones_row_for_one_ledger_id_fails_closed`, `test_corrupted_undeclared_row_shape_id_exits_one`, `test_corrupted_undeclared_row_before_hash_exits_one`, `test_uppercased_before_hash_exits_one`, `test_after_cell_that_is_not_the_undeclared_literal_exits_one` (parametrized, 4 cases), `test_milestones_with_zero_rekey_rows_exits_one`, `test_checker_error_output_is_order_stable`
- `firestarter_app/tests/fixtures/report_shapes.py` — `import copy`; `_clone_with_chip_override` passes `copy.deepcopy(report.results)` and `copy.deepcopy(report.plan)`; two docstrings corrected
- `firestarter_app/tests/test_blast_radius_invariance.py` — `test_build_shape_never_shares_results_or_plan_between_shape_ids`, `test_mutation_through_a_derived_shape_does_not_move_the_base_shapes_frozen_hash`; Reachability block extended
- `.planning/phases/174-blast-radius-invariance-harness/evidence/174-06-duplicate-row-red-green.txt` — Task 1 transcript
- `.planning/phases/174-blast-radius-invariance-harness/evidence/174-06-undeclared-row-red-green.txt` — Task 2 transcript
- `.planning/phases/174-blast-radius-invariance-harness/evidence/174-06-shape-aliasing-red-green.txt` — Task 3 transcript

## RED/GREEN `rc` Pairs (verbatim, per plan output contract)

**Task 1 — duplicate `ledger_id`:**
```
rc_prefix_dup=0   (pre-fix blob 5c0c7c9, prints "OK: 6 ledger row(s), 6 MILESTONES.md row(s) bound")
rc_fixed_dup=2    (fixed checker, prints "ERROR: duplicate MILESTONES.md row for ledger_id 'RK-174-01-p177-readback-gating'")
rc_fixed_clean=0  (real unmutated pair still binds)
```

**Task 2 — undeclared branch, six legs:**
```
rc_prefix_wrongshape=0    rc_fixed_wrongshape=1
rc_prefix_wrongbefore=0   rc_fixed_wrongbefore=1
rc_prefix_upperbefore=0   rc_fixed_upperbefore=1
rc_prefix_wideafter=0     rc_fixed_wideafter=1
rc_prefix_shortafter=0    rc_fixed_shortafter=1
rc_prefix_emptytable=0    rc_fixed_emptytable=1
order_stable=identical
rc_fixed_clean=0
```
New `ERROR:` texts (exact, quoted verbatim from the transcript):
- `ERROR: 'RK-174-01-p177-readback-gating' MILESTONES.md row (shape_id, before)=('TOTALLY-WRONG-SHAPE', '4dc282a5d596') does not match ledger row (shape_id, before_hash)=('sst27sf512-six-step', '4dc282a5d596')`
- `ERROR: 'RK-174-01-p177-readback-gating' MILESTONES.md row (shape_id, before)=('sst27sf512-six-step', '000000000000') does not match ledger row (shape_id, before_hash)=('sst27sf512-six-step', '4dc282a5d596')`
- `ERROR: 'RK-174-01-p177-readback-gating' MILESTONES.md row (shape_id, before)=('sst27sf512-six-step', '4DC282A5D596') does not match ledger row (shape_id, before_hash)=('sst27sf512-six-step', '4dc282a5d596')`
- `ERROR: 'RK-174-01-p177-readback-gating' is undeclared in the ledger but MILESTONES.md's after cell 'ffffffffffffff' is not the exact literal '(undeclared)'`
- `ERROR: 'RK-174-01-p177-readback-gating' is undeclared in the ledger but MILESTONES.md's after cell '4dc282a5d59' is not the exact literal '(undeclared)'`
- `ERROR: MILESTONES.md carries 0 RK-174- row(s) while the ledger declares 6 row(s)`

**Task 3 — CR-01 aliasing:**
```
prefix_alias_results=True         fixed_alias_results=False
prefix_base_before=6d3afbc52315   fixed_alias_plan=False
prefix_base_after=e9df6ca4627c    fixed_alias_results_joined=False
rc_prefix=0                       fixed_base_before=6d3afbc52315
                                   fixed_base_after=6d3afbc52315
                                   fixed_base_matches_frozen=True
                                   rc_fixed=0
rc_suite=0, 122 passed
```

## Decisions Made

- **CR-01 fix: `copy.deepcopy` over dropping `@functools.cache`.** The review offered two alternatives. Deep-copying the clone's `results`/`plan` targets the actual defect (aliasing ACROSS `shape_id`s) rather than a proxy for it; it preserves the cache's cost benefit (this phase's recorded 7.92-second figure for its test count is a number later phases compare against, and the two canonical-naming derivatives were already uncached, so nothing new pays `derive_plan`/`run_plan` twice); and it avoids leaving a seven-to-one cache asymmetry across the eight real-path builders that dropping one builder's cache would create — which would also half-fix WR-02 (explicitly out of this plan's scope) in a way that made the remaining seven builders look intentionally different rather than outstanding.
- **Exact-literal comparison over a loosened regex.** WR-01's fix keeps the undeclared-branch's `after`-cell check simple: require the string to equal `_UNDECLARED = "(undeclared)"` exactly, rather than widening `_HASH_RE`'s twelve-lowercase-hex pattern to also reject near-miss values. The exact-literal check subsumes every boundary case (short, long, uppercase, empty) with one comparison instead of a more complex regex.

## Deviations from Plan

None - plan executed exactly as written. The plan-level verification step 3's "seven `rc_prefix_*=0` RED lines" count refers precisely to the underscore-suffixed `rc_prefix_<name>=0` family (1 from Task 1 + 6 from Task 2); Task 3's differently-named `rc_prefix=0` (against the *other* pinned blob, `report_shapes.py`) is an additional, separately-verified eighth RED line — both counts checked explicitly and both pass.

## Issues Encountered

None. All three tasks' automated `<verify>` blocks ran and passed exactly as specified in the plan, with every literal count, exact-string, and `rc` assertion matching.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- GATE-06's binding mechanism is now fail-closed: a fabricated, corrupted, or deleted `MILESTONES.md` row can no longer pass the checker silently. Phase 174's single recorded gap is closed.
- CR-01 is fixed before Phase 181 writes `RK-174-03-p181-canonical-naming-avoided`'s anti-vacuity leg — the collateral false-RED risk the verifier flagged no longer exists.
- All sixteen `FROZEN_HASHES`, all sixteen `LADDER_PINS`, `shape_ids.json`, the twenty-six-row issue corpus, and `part_number_delta.json` remain byte-identical to their pre-plan state (verified via empty `git status --porcelain` on each). No declared re-key occurred.
- WR-02 (in-place `db_diff` assignment on cached real-path shapes), IN-01 and IN-02 are explicitly left untouched, exactly as the plan's prohibitions require — they remain open items for a future plan, not silently absorbed here.
- No file under `firestarter_app/firestarter/` or the `firestarter` firmware submodule was touched; this stayed a test-and-tooling-only plan.

---
*Phase: 174-blast-radius-invariance-harness*
*Completed: 2026-09-03*

## Self-Check: PASSED

All 7 created/modified source and evidence files verified present on disk with `[ -f ]`. All 4 meta commit hashes (`12eb9cf7`, `4a1bfe35`, `3a4dc611`, `f6fc9883`) and all 5 app-submodule commit hashes (`2db07df`, `7367cc5`, `64669b1`, `c4e16c6`, `e907e6d`) verified present in their respective `git log --oneline --all`.
