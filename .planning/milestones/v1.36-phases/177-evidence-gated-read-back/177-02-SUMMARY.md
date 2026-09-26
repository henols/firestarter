---
phase: 177-evidence-gated-read-back
plan: 02
subsystem: testing
tags: [rekey-ledger, dedup_fingerprint, blast-radius, fingerprint-classification, milestones]

requires:
  - phase: 177-01
    provides: "The evidence-gated read-back behaviour change (PRUNE-01/02/03) and the measured, committed RED blast-radius evidence (evidence/177-01-red-capture.txt) this plan declares against."
provides:
  - "Re-baselined FROZEN_HASHES for the three shapes PRUNE-03 moved, each value measured fresh in firestarter_app/.venv311 (independently re-measured by this continuation executor, not transcribed from the prior evidence file)"
  - "The re-pointed sst27sf512-six-step / sst27sf512-six-step-readback-gated pair (D-177-3 Option A), replacing the falsified fingerprint-dropped projection"
  - "prune03-synthesized-fingerprint-match registered in all four registries (_BUILDERS, FROZEN_HASHES, LADDER_PINS, shape_ids.json) and removed from RESERVED_SHAPE_IDS"
  - "The append-only ledger declaration: RK-174-01/05/06 declared, RK-174-07 (new shape, no Phase-174 row) and RK-174-09 (Phase-178 re-anchor) appended"
  - "The published old-to-new filed-corpus mapping (177-REKEY-MAPPING.md), independently re-measured, not transcribed"
  - "MILESTONES.md's corrections table extended with three newly falsified projections; the cross-tree checker binds both trees in both directions"
affects: [177-03-close-prune-04-and-seal-phase]

actuals:
  tokens: 16375
  tasks: 4
  commits: 5

tech-stack:
  added: []
  patterns:
    - "Measure-never-transcribe extended through declaration: every FROZEN_HASHES/ledger after_hash value used in this plan was produced by a fresh dedup_fingerprint(build_shape(...)) call in .venv311 during this session -- including a from-scratch re-measurement of every value the prior (interrupted) executor's evidence file already recorded, so the checkpoint confirmation in Task 1 rests on independent proof, not trust in a file."
    - "Ledger re-anchoring on an unrelated re-key: a row whose shape moved for a reason outside its own owning phase's mechanism (RK-174-06, owned by Phase 178's status axis, moved instead by Phase 177's match bucket) is declared (so the reproduces-from-a-fresh-build invariant holds) and its assertion is re-anchored via a NEW appended row (RK-174-09) rather than an edit to the row it supersedes -- D-09's append-only rule extends to a re-key landing for the wrong owner's reason, not just the right one."

key-files:
  created:
    - .planning/phases/177-evidence-gated-read-back/177-REKEY-MAPPING.md
    - .planning/phases/177-evidence-gated-read-back/evidence/177-02-rebaseline.txt
    - .planning/phases/177-evidence-gated-read-back/evidence/177-02-ledger.txt
    - .planning/phases/177-evidence-gated-read-back/evidence/177-02-cross-tree.txt
    - firestarter_app/tests/fixtures/reports/prune03-synthesized-fingerprint-match.json
  modified:
    - .planning/phases/177-evidence-gated-read-back/177-DECISIONS.md
    - .planning/MILESTONES.md
    - firestarter_app/tests/fixtures/report_shapes.py
    - firestarter_app/tests/fixtures/shape_ids.json
    - firestarter_app/tests/fixtures/rekey_ledger.py
    - firestarter_app/tests/test_blast_radius_invariance.py
    - firestarter_app/tests/test_rekey_ledger.py
    - firestarter_app/tests/fixtures/reports/at28c256-full-all-ok-sdp.json
    - firestarter_app/tests/fixtures/reports/sst27sf512-full-all-ok.json
    - firestarter_app/tests/fixtures/reports/sst27sf512-six-step.json
    - firestarter_app/tests/fixtures/reports/sst27sf512-six-step-readback-gated.json
    - firestarter_app/tests/fixtures/reports/w27e257-full-all-ok.json

key-decisions:
  - "D-177-5: proceed with the measured values as declared (Option A) -- re-measured independently in .venv311, not transcribed from evidence/177-01-red-capture.txt. Every disagreement against 177-RESEARCH.md's projections named: distinct_arms measures 4, not the projected 3; sst27sf512-six-step-readback-gated's inherited projection is falsified (converges onto the tracer's own value); gh47-sst27sf512-pass's corpus-level projection (1f812aae49ca) is not applied to its FROZEN_HASHES entry."
  - "D-177-6 (new, recorded this session): gh47-sst27sf512-pass is NOT re-pointed -- stays inside D-177-3's stated scope (the two sst27sf512-six-step builders only). Its FROZEN_HASHES entry does not move and gets no ledger row (RK-174-08 is deliberately unused)."
  - "RK-174-06 declared by Phase 177, not deferred to Phase 178: its shape (sst27sf512-full-all-ok) moved for the SAME match-bucket reason as RK-174-05, and test_every_ledger_row_shape_id_resolves_and_recomputes requires an undeclared row's before_hash to still reproduce from a fresh build. RK-174-09 re-anchors Phase 178's ATTR-04 assertion at the new post-177 value via an appended row, never by editing RK-174-06's before cell."

requirements-completed: [PRUNE-03]

coverage:
  - id: D1
    description: "Every frozen shape whose dedup_fingerprint moved under plan 177-01 (at28c256-full-all-ok-sdp, sst27sf512-full-all-ok, w27e257-full-all-ok) is re-baselined to a value produced by a run in .venv311, never transcribed"
    requirement: PRUNE-03
    verification:
      - kind: unit
        ref: "tests/test_blast_radius_invariance.py#test_dedup_fingerprint_is_frozen[at28c256-full-all-ok-sdp/sst27sf512-full-all-ok/w27e257-full-all-ok]"
        status: pass
      - kind: other
        ref: "evidence/177-02-rebaseline.txt (stale_frozen= empty)"
        status: pass
    human_judgment: false
  - id: D2
    description: "Every declared ledger row's after_hash equals a freshly computed dedup_fingerprint(build_shape(...)) and differs from before_hash; no before_hash overwritten"
    requirement: PRUNE-03
    verification:
      - kind: unit
        ref: "tests/test_rekey_ledger.py#test_every_ledger_row_shape_id_resolves_and_recomputes"
        status: pass
      - kind: unit
        ref: "tests/test_rekey_ledger.py#test_no_declared_row_has_after_hash_equal_to_before_hash"
        status: pass
      - kind: other
        ref: "evidence/177-02-ledger.txt (before_cells_overwritten= empty, inconsistent= empty)"
        status: pass
    human_judgment: false
  - id: D3
    description: "gh23-w27e257-fail stays frozen at exactly 7a89fcea856a; the nine other unmoved shapes keep their committed values byte-for-byte"
    requirement: PRUNE-03
    verification:
      - kind: other
        ref: "evidence/177-02-rebaseline.txt (gh23_unmoved=True, unmoved_drifted= empty)"
        status: pass
    human_judgment: false
  - id: D4
    description: "LADDER_PINS still covers exactly four distinct (proposed_disposition, ladder_state) pairs after the D-4/D-6 flip -- the INCONCLUSIVE arm is re-populated, not left empty"
    requirement: PRUNE-03
    verification:
      - kind: unit
        ref: "tests/test_blast_radius_invariance.py#test_ladder_pins_cover_all_four_build_db_diff_arms"
        status: pass
      - kind: unit
        ref: "tests/test_blast_radius_invariance.py#test_build_db_diff_ladder_pin_for_tracer_shape"
        status: pass
    human_judgment: false
  - id: D5
    description: "prune03-synthesized-fingerprint-match is registered in _BUILDERS, FROZEN_HASHES, LADDER_PINS and shape_ids.json at once, and removed from RESERVED_SHAPE_IDS"
    requirement: PRUNE-03
    verification:
      - kind: unit
        ref: "tests/test_blast_radius_invariance.py#test_shape_ids_frozen_hashes_ladder_pins_and_snapshots_agree"
        status: pass
      - kind: unit
        ref: "tests/test_blast_radius_invariance.py#test_shape_id_set_is_pinned_and_disjoint_from_reserved"
        status: pass
    human_judgment: false
  - id: D6
    description: "tests/fixtures/reports/*.json are regenerated by tools/snapshot_report_shapes.py, never hand-edited, and --check reports no drift"
    requirement: PRUNE-03
    verification:
      - kind: other
        ref: "./.venv311/bin/python tools/snapshot_report_shapes.py --check (exit 0, 17 snapshots match)"
        status: pass
    human_judgment: false
  - id: D7
    description: "The app-side ledger and .planning/MILESTONES.md agree in both directions: python3 tools/rekey/check_rekey_ledger.py run from /workspaces exits 0"
    requirement: PRUNE-03
    verification:
      - kind: other
        ref: "python3 tools/rekey/check_rekey_ledger.py (exit 0, OK: 8 ledger row(s), 8 MILESTONES.md row(s) bound)"
        status: pass
    human_judgment: false
  - id: D8
    description: "The declaration lands in commits separate from 177-01's behaviour commit, so the re-key is a reviewable unit"
    requirement: PRUNE-03
    verification:
      - kind: other
        ref: "git log --oneline (5 commits this plan: 649848e3, 693c0c3, 4fd1ef6, bec178b, 14c168f3 -- none is 3f01714, the 177-01 behaviour commit)"
        status: pass
    human_judgment: false
  - id: D9
    description: "The measured filed-corpus re-key count (18 of 26) is recorded with its per-issue before/after mapping in 177-REKEY-MAPPING.md; agreement with the inherited projection of 18 is recorded in MILESTONES.md"
    requirement: PRUNE-03
    verification:
      - kind: other
        ref: ".planning/phases/177-evidence-gated-read-back/177-REKEY-MAPPING.md (18 issue rows, independently re-measured)"
        status: pass
    human_judgment: false
  - id: D10
    description: "The falsified sst27sf512-six-step-readback-gated projection is corrected in prose in both MILESTONES.md and rekey_ledger.py's provenance docstring; every pre-existing row's before cell is untouched"
    requirement: PRUNE-03
    verification:
      - kind: other
        ref: ".planning/MILESTONES.md corrections table + firestarter_app/tests/fixtures/rekey_ledger.py RK-174-01 provenance paragraph"
        status: pass
      - kind: other
        ref: "evidence/177-02-ledger.txt (before_cells_overwritten= empty)"
        status: pass
    human_judgment: false

duration: 90min
completed: 2026-09-05
status: complete
---

# Phase 177 Plan 02: Declare the Re-Key Summary

**Re-baselined the three PRUNE-03-moved frozen shapes and registered the reserved `prune03-synthesized-fingerprint-match` shape to measured values (never transcribed), declared the append-only ledger across both trees with a Phase-178 re-anchor row, and published the 18-issue filed-corpus old-to-new mapping -- full 2210-test app suite green at close.**

## Performance

- **Duration:** ~90 min (continuation from the Task 1 checkpoint; the prior executor made zero commits, only measured)
- **Completed:** 2026-09-05
- **Tasks:** 4 (Task 1's checkpoint confirmation completed this session; Tasks 2-4 executed this session)
- **Files modified:** 17 (11 in `firestarter_app`, 6 in the meta repo)

## Accomplishments

- Confirmed Task 1's checkpoint by independently re-measuring every hash in `firestarter_app/.venv311` (not by trusting `evidence/177-01-red-capture.txt`), and recorded `D-177-5` (proceed with the measured values, every disagreement named) and the operator's new `D-177-6` (gh47-sst27sf512-pass is not re-pointed) in `177-DECISIONS.md`.
- Re-baselined `FROZEN_HASHES` for the three shapes PRUNE-03 moved (`at28c256-full-all-ok-sdp`, `sst27sf512-full-all-ok`, `w27e257-full-all-ok`), re-pointed the two hand-specified `sst27sf512-six-step*` builders per D-177-3 Option A (the tracer moves `indeterminate` -> `match`; the paired `-readback-gated` shape moves to the gate's failing branch, verdict `marginal`, real `indeterminate` classification kept), and registered `prune03-synthesized-fingerprint-match` in all four registries at once -- keeping the four-arm `LADDER_PINS` invariant intact (measured `distinct_arms=4`) and the ten unmoved shapes, including `gh23-w27e257-fail` and `gh47-sst27sf512-pass`, byte-for-byte unchanged.
- Declared `RK-174-01`, `RK-174-05` and `RK-174-06` in the append-only ledger with measured `after_hash` values, appended `RK-174-07` (a shape Phase 174 owned no row for) and `RK-174-09` (re-anchoring Phase 178's ATTR-04 assertion at `RK-174-06`'s new post-177 value, since Phase 177 moved that baseline for an unrelated reason), and corrected `RK-174-01`'s provenance paragraph to name the falsified inherited projection while keeping it visible as the superseded claim.
- Declared the same three rows plus the two appended rows in `MILESTONES.md`, extended its corrections table with three newly falsified projections (the `-readback-gated` shape's projection, the `distinct_arms` count, and `gh47-sst27sf512-pass`'s projected-but-undeclared value), recorded the measured filed-corpus re-key (18 of 26, matching the inherited projection exactly), and published the full old-to-new mapping at `177-REKEY-MAPPING.md` -- independently re-measured, including one value (issue gh#48) whose reproduction required the broader OK-verdict transform rather than the narrower indeterminate-only one. `python3 tools/rekey/check_rekey_ledger.py` binds both trees in both directions and exits 0.

## Task Commits

1. **Task 1: Confirm the measured hashes before they become the published record** - `649848e3` (docs, meta)
2. **Task 2: Re-baseline the moved shapes and register the reserved one** - `693c0c3` (test, `firestarter_app`)
3. **Task 3: Declare it in the ledger** - `4fd1ef6` (test, `firestarter_app`), plus a deviation fix `bec178b` (fix, `firestarter_app`) landed alongside Task 4's meta commit once MILESTONES.md's declaration surfaced it
4. **Task 4: The meta half -- MILESTONES.md, the falsified projection, and the published mapping** - `14c168f3` (docs, meta)

_Note: five commits total (three in `firestarter_app`, two in the meta repo) rather than the plan's stated four (two + two) -- `bec178b` is a Rule 1 deviation fix, documented below, that only became visible once Task 4's MILESTONES.md declaration landed._

## Files Created/Modified

- `firestarter_app/tests/fixtures/report_shapes.py` - re-baselined `FROZEN_HASHES` for the three moved shapes, re-pointed the two `sst27sf512-six-step*` builders, added `_build_prune03_synthesized_fingerprint_match` and registered it in `_BUILDERS`/`FROZEN_HASHES`/`RESERVED_SHAPE_IDS`
- `firestarter_app/tests/fixtures/shape_ids.json` - added `prune03-synthesized-fingerprint-match` to the committed sorted anchor
- `firestarter_app/tests/test_blast_radius_invariance.py` - updated `LADDER_PINS` for the flipped shapes and the new registration, updated the tracer shape's ladder-pin test and the `_TRACER_CANONICAL`/`_PINNED_SHAPE_ID_SET` pins
- `firestarter_app/tests/fixtures/rekey_ledger.py` - declared `RK-174-01`/`05`/`06`, appended `RK-174-07`/`09`, corrected `RK-174-01`'s provenance paragraph
- `firestarter_app/tests/test_rekey_ledger.py` - updated the row-count gate (6 -> 8), narrowed the undeclared-sweep test to the still-undeclared subset with a non-empty guard, drove the zero-rekey-rows checker test's row count off `len(LEDGER)`, and retargeted the undeclared-after-cell boundary legs off row 01 (now declared) onto `RK-174-02` (deviation, see below)
- `firestarter_app/tests/fixtures/reports/*.json` - 5 files regenerated by `tools/snapshot_report_shapes.py` (4 moved shapes + the new registration), 12 unchanged
- `.planning/phases/177-evidence-gated-read-back/177-DECISIONS.md` - `D-177-5` and `D-177-6` recorded
- `.planning/MILESTONES.md` - ledger table declarations, `RK-174-06` change-cell amendment, three new corrections-table rows, the GATE-06 filed-corpus re-key paragraph
- `.planning/phases/177-evidence-gated-read-back/177-REKEY-MAPPING.md` - the published 18-issue old-to-new mapping
- `.planning/phases/177-evidence-gated-read-back/evidence/177-02-{rebaseline,ledger,cross-tree}.txt` - this session's verification transcripts

## Decisions Made

See `key-decisions` in the frontmatter for `D-177-5`, `D-177-6`, and the RK-174-06/RK-174-09 declare-vs-reanchor split.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] `test_after_cell_that_is_not_the_undeclared_literal_exits_one` mutated a row that Task 4's own declaration made no longer undeclared**
- **Found during:** Task 4, after landing `MILESTONES.md`'s declaration of `RK-174-01`
- **Issue:** This pre-existing test proves the checker rejects any after-cell value on an undeclared row except the exact literal `(undeclared)`, by mutating `RK-174-01-p177-readback-gating`'s row (chosen because it was undeclared when the test was written in Phase 174). Once this plan declared that row, the test's mutated fixture no longer represented an undeclared-row corruption, and its assertion on the checker's specific error text stopped matching.
- **Fix:** Generalized `_row_01_cells`/`_mutated_row_01_milestones` to `_row_cells`/`_mutated_row_milestones`, parameterized by `ledger_id` (defaulting to row 01 for the legs that mutate a structural cell regardless of declared state), and retargeted the four after-cell-boundary parametrizations at `RK-174-02-rejected-sdp-step-pruning`, which stays undeclared.
- **Files modified:** `firestarter_app/tests/test_rekey_ledger.py`
- **Verification:** `pytest tests/test_rekey_ledger.py` -- 26 passed, 0 failed.
- **Committed in:** `bec178b`

**2. [Rule 1 - Bug] Two pre-existing tests asserted literals this plan's own declared change invalidated**
- **Found during:** Task 3
- **Issue:** `test_dedup_fingerprint_truncation_is_a_plain_slice` asserted the tracer shape's hash against the pre-177 canonical pre-image (`write=OK:indeterminate|verify=OK:indeterminate`); `test_shape_id_set_is_pinned_and_disjoint_from_reserved` asserted `SHAPE_IDS` against a 16-entry pinned list. Both are direct, necessary consequences of this plan's own declared registration and re-key.
- **Fix:** Updated `_TRACER_CANONICAL` to the re-pointed `match` classification and added `prune03-synthesized-fingerprint-match` to `_PINNED_SHAPE_ID_SET`.
- **Files modified:** `firestarter_app/tests/test_blast_radius_invariance.py`
- **Verification:** `pytest tests/test_blast_radius_invariance.py` -- 197 passed, 0 failed.
- **Committed in:** `693c0c3`

**3. [Rule 1 - Bug] `ruff format` reformatted two edited files**
- **Found during:** Tasks 2 and 3
- **Issue:** A manually-wrapped multi-line assert and a manually-wrapped generator expression did not match `ruff format`'s canonical single-line rendering.
- **Fix:** Ran `ruff format` on the two files; re-verified tests still pass.
- **Files modified:** `firestarter_app/tests/test_blast_radius_invariance.py`, `firestarter_app/tests/test_rekey_ledger.py`
- **Verification:** `ruff format --check` clean; tests re-run green.
- **Committed in:** `693c0c3`, `bec178b`

---

**Total deviations:** 3 auto-fixed (all Rule 1 -- pre-existing test assertions or formatting made stale by this plan's own declared registration and re-key; none touches `firestarter_app/firestarter/` or the firmware submodule).
**Impact on plan:** All three are necessary consequences of the declaration this plan exists to make. The extra commit (`bec178b`) beyond the plan's stated two-app-commit structure is a direct, documented result of Deviation 1 and does not change the plan's D-11 separate-commit intent (the ledger declaration and its own test-suite fixes stay in `firestarter_app`, separate from the meta-repo `MILESTONES.md` commit).

## Issues Encountered

None beyond the deviations above. One transient, expected state: after Task 3's ledger-declaration commit landed but before Task 4's `MILESTONES.md` commit, `tests/test_rekey_ledger.py::test_check_rekey_ledger_clean_input_exits_zero` failed (the cross-tree checker correctly reported the newly-declared/appended rows as orphaned against the not-yet-updated `MILESTONES.md`) -- this is the D-11 separate-commit protocol working as designed, not a defect; it was re-confirmed green immediately after Task 4 landed.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

Ready for `177-03` (close PRUNE-04 measured-empty per D-177-1, and PRUNE-07's seed amendment, sealing the phase with the full suite GREEN). This plan leaves the full `firestarter_app` suite at 2210 passed, 0 failed, 0 skipped (0:05:25) -- the Phase 174 blast-radius gate that `177-01` deliberately reddened is confirmed fully GREEN again, the append-only ledger and `MILESTONES.md` agree in both directions (`check_rekey_ledger.py` exits 0), and no fixture, snapshot, or ledger row outside this plan's declared scope was touched.

---
*Phase: 177-evidence-gated-read-back*
*Completed: 2026-09-05*

## Self-Check: PASSED

- All 13 claimed files (5 created, 8 modified/re-verified) confirmed present via `[ -f ]`.
- All 5 commit hashes (`649848e3`, `693c0c3`, `4fd1ef6`, `bec178b`, `14c168f3`) confirmed present via `git log --oneline --all`.
- Re-ran plan-level `<verification>` at close: `python3 tools/rekey/check_rekey_ledger.py` exits 0 (`OK: 8 ledger row(s), 8 MILESTONES.md row(s) bound`); `pytest tests/test_blast_radius_invariance.py tests/test_rekey_ledger.py tests/test_devtest_issue_corpus.py tests/test_diagnostic_report.py` -- 223 passed, 0 failed; `tools/snapshot_report_shapes.py --check` -- 17 snapshots match a fresh regeneration.
- Full `firestarter_app` suite re-run at close: 2210 passed, 1 warning (pre-existing, unrelated Click deprecation), 0 failed, in 325.11s.
- `git -C /workspaces/firestarter_app status --short` and `git status --short` (meta) both clean except the expected `firestarter_app` gitlink bump, left uncommitted per instructions.
