---
phase: 174-blast-radius-invariance-harness
plan: 03
subsystem: testing
tags: [dedup_fingerprint, to_dict, schema-pin, shape-registry-closure, rekey-ledger, anti-vacuity]

requires:
  - phase: 174-blast-radius-invariance-harness (plans 01, 02, 04)
    provides: "report_shapes.py's sixteen-shape SHAPE_IDS/FROZEN_HASHES registry, RESERVED_SHAPE_IDS already populated, LADDER_PINS, the sixteen committed to_dict() snapshots, and rekey_ledger.py's one seeded row plus the meta-side checker"
provides:
  - "tests/test_blast_radius_invariance.py: seven element-wise to_dict() key-list pins (D-07) -- top-level, voltage, banner, auto_capture, transport_health, db_diff, steps[0] -- plus a SCHEMA_VERSION triple-equality pin and an anti-vacuity leg proving the pins move on both a deleted and an added key"
  - "tests/fixtures/shape_ids.json: the committed sorted sixteen-entry anchor D-10 pins SHAPE_IDS against, element-wise"
  - "tests/test_blast_radius_invariance.py: the four-way shape_id closure (committed anchor, FROZEN_HASHES, LADDER_PINS, snapshot filenames), a build_shape resolution test for all three RESERVED_SHAPE_IDS, and its own anti-vacuity leg"
  - "tests/fixtures/rekey_ledger.py: all six pre-seeded ledger rows, every before_hash recomputed this session from a committed builder, every after_hash None"
  - "tests/test_rekey_ledger.py: ledger_id/pair uniqueness, no-declared-row-moved-nothing, exact-row-count, single-row-sweep, undeclared-never-abstains, ascending-order, and a reverse-direction orphan-MILESTONES-row anti-vacuity leg"
  - ".planning/MILESTONES.md: the v1.36 Re-Key Ledger section narrating all six rows plus a Claim/As-inherited/As-measured corrections table"
affects: ["175 (read-back gating)", "177", "178", "179", "181"]

actuals:
  tokens: 7555
  tasks: 3
  commits: 5

tech-stack:
  added: []
  patterns:
    - "Element-wise sorted-list pin applied to a schema key set AND to a shape_id registry with the same idiom, both asserting list equality (never membership/subset) against a committed constant"
    - "Four-way closure sentinel: one hand-written committed anchor plus three independently-derived set equalities against it, modelled on test_shipped_ops_never_reach_sdp_arm's explicit-list-plus-derived-set idiom"
    - "In-process anti-vacuity via dict mutation on a real to_dict()/list-copy result, rather than a subprocess-level planted fixture, for every new gate in this plan"

key-files:
  created:
    - firestarter_app/tests/fixtures/shape_ids.json
    - .planning/phases/174-blast-radius-invariance-harness/evidence/174-03-schema-pins.txt
    - .planning/phases/174-blast-radius-invariance-harness/evidence/174-03-ledger-closure.txt
  modified:
    - firestarter_app/tests/test_blast_radius_invariance.py
    - firestarter_app/tests/fixtures/rekey_ledger.py
    - firestarter_app/tests/test_rekey_ledger.py
    - .planning/MILESTONES.md

key-decisions:
  - "All six ledger before-hashes were RECOMPUTED in this session against the real dedup_fingerprint on a freshly-built shape from a committed builder -- none were transcribed from the plan text or from any prior document. All six matched the plan's stated literals exactly on first measurement; there was nothing to report as a disagreement for the ledger rows themselves."
  - "db_diff is None on a bare build_shape() report -- the D-07 db_diff key-list pin needed a helper (_to_dict_with_db_diff) that composes a real DbDiff via build_db_diff before calling to_dict(), mirroring tools/snapshot_report_shapes.py:render_shape's own composition rather than duplicating a second copy of it. Without this, the plan's own literal Task 1 verify snippet (sorted(d['db_diff']) on a bare build_shape() result) would raise TypeError: 'NoneType' object is not iterable."
  - "The MILESTONES.md 'Projected after_hash' sentence beneath the ledger table was reworded to name the row by shape_id + owner rather than repeating the literal ledger_id string RK-174-01-p177-readback-gating a second time in the file -- otherwise Task 3's own verify gate (grep -c 'RK-174-0' .planning/MILESTONES.md -eq 6) would count 7 occurrences and fail on a row that is not actually duplicated in the ledger table."

patterns-established:
  - "A generator helper (_to_dict_with_db_diff) shared between a single db_diff key-list pin test and any future db_diff-dependent test, rather than each test independently composing build_db_diff onto a bare build_shape() report."

requirements-completed: [GATE-01, GATE-02, GATE-05, GATE-06]

coverage:
  - id: D1
    description: "Seven element-wise to_dict() key-list pins (D-07): top-level, voltage, banner, auto_capture, transport_health, db_diff, steps[0] -- all three keys Phase 181 deletes (vpp_mv, vpe_mv, locked_steps) present and pinned, the additive canonical_part_number key absent and pinned absent, and a SCHEMA_VERSION triple-equality assertion"
    requirement: "GATE-05"
    verification:
      - kind: unit
        ref: "tests/test_blast_radius_invariance.py#test_to_dict_top_level_key_list_is_pinned"
        status: pass
      - kind: unit
        ref: "tests/test_blast_radius_invariance.py#test_to_dict_voltage_key_list_is_pinned"
        status: pass
      - kind: unit
        ref: "tests/test_blast_radius_invariance.py#test_to_dict_banner_key_list_is_pinned"
        status: pass
      - kind: unit
        ref: "tests/test_blast_radius_invariance.py#test_to_dict_auto_capture_key_list_is_pinned"
        status: pass
      - kind: unit
        ref: "tests/test_blast_radius_invariance.py#test_to_dict_transport_health_key_list_is_pinned"
        status: pass
      - kind: unit
        ref: "tests/test_blast_radius_invariance.py#test_to_dict_db_diff_key_list_is_pinned"
        status: pass
      - kind: unit
        ref: "tests/test_blast_radius_invariance.py#test_to_dict_steps_element_0_key_list_is_pinned"
        status: pass
      - kind: unit
        ref: "tests/test_blast_radius_invariance.py#test_schema_version_is_pinned"
        status: pass
      - kind: unit
        ref: "tests/test_blast_radius_invariance.py#test_to_dict_key_list_pins_are_sensitive_to_added_and_removed_keys"
        status: pass
    human_judgment: false
  - id: D2
    description: "The complete shape_id set is closed four ways against a committed sorted anchor (tests/fixtures/shape_ids.json): element-wise vs SHAPE_IDS, set-equal vs FROZEN_HASHES, set-equal vs LADDER_PINS, set-equal vs the committed snapshot filenames -- both widening and narrowing seen RED"
    requirement: "GATE-01"
    verification:
      - kind: unit
        ref: "tests/test_blast_radius_invariance.py#test_shape_ids_committed_anchor_matches_the_registry"
        status: pass
      - kind: unit
        ref: "tests/test_blast_radius_invariance.py#test_shape_ids_frozen_hashes_ladder_pins_and_snapshots_agree"
        status: pass
      - kind: unit
        ref: "tests/test_blast_radius_invariance.py#test_shape_ids_closure_is_sensitive_to_removed_and_added_entries"
        status: pass
    human_judgment: false
  - id: D3
    description: "The three later-phase shape names (prune03-synthesized-fingerprint-match, attr01-status-axis-transport-fault, uv-slot-write-pass) are reserved, asserted disjoint from the frozen SHAPE_IDS set, and build_shape raises rather than silently returning a report for any of the three"
    requirement: "GATE-01"
    verification:
      - kind: unit
        ref: "tests/test_blast_radius_invariance.py#test_build_shape_raises_for_every_reserved_shape_id"
        status: pass
      - kind: unit
        ref: "tests/test_blast_radius_invariance.py#test_shape_id_set_is_pinned_and_disjoint_from_reserved"
        status: pass
    human_judgment: false
  - id: D4
    description: "All six ledger rows pre-seeded, every before_hash recomputed from its own committed builder in this session, every after_hash None, ledger_id values unique and ascending, (shape_id, ledger_id) pairs unique, no declared row with before==after, row count exactly six, well-defined on a single-row tuple, and the undeclared case never abstains"
    requirement: "GATE-06"
    verification:
      - kind: unit
        ref: "tests/test_rekey_ledger.py#test_ledger_has_exactly_six_pre_seeded_rows"
        status: pass
      - kind: unit
        ref: "tests/test_rekey_ledger.py#test_ledger_id_values_are_unique"
        status: pass
      - kind: unit
        ref: "tests/test_rekey_ledger.py#test_shape_id_ledger_id_pairs_are_unique"
        status: pass
      - kind: unit
        ref: "tests/test_rekey_ledger.py#test_no_declared_row_has_after_hash_equal_to_before_hash"
        status: pass
      - kind: unit
        ref: "tests/test_rekey_ledger.py#test_ledger_sweep_is_well_defined_on_a_single_row_tuple"
        status: pass
      - kind: unit
        ref: "tests/test_rekey_ledger.py#test_undeclared_after_hash_routes_to_before_hash_and_never_abstains"
        status: pass
      - kind: unit
        ref: "tests/test_rekey_ledger.py#test_ledger_id_order_is_ascending"
        status: pass
      - kind: integration
        ref: "tools/rekey/check_rekey_ledger.py (exit 0, six rows bound)"
        status: pass
      - kind: integration
        ref: "tests/test_rekey_ledger.py#test_check_rekey_ledger_orphan_milestones_row_exits_one"
        status: pass
    human_judgment: false
  - id: D5
    description: "MILESTONES.md narrates all six ledger rows and records four falsified priors (filed-issue count, canonical-naming pair, UV collapse mechanism, lowercase-title claim) plus the operator-ratified D-06 26-of-26 scope widening (carrying no ledger_id), with the diff confined to the v1.36 section"
    requirement: "GATE-06"
    verification:
      - kind: integration
        ref: "tools/rekey/check_rekey_ledger.py (exit 0 against the real ledger and MILESTONES.md)"
        status: pass
    human_judgment: true
    rationale: "The checker verifies the ledger/MILESTONES binding mechanically (row presence, hash agreement, both directions), but whether the corrections table's prose accurately narrates the underlying research findings is a human-readable-content judgment, not something the checker's regex-based row parser evaluates."

duration: 70min
completed: 2026-09-03
status: complete
---

# Phase 174 Plan 03: Close the Oracle Summary

**Seven element-wise `to_dict()` schema-key pins (D-07), a four-way `shape_id` closure against a committed sorted anchor (D-10) with the three later-phase names reserved and unresolvable, and all six re-key ledger rows pre-seeded with every before-hash recomputed this session from a committed builder -- closing the three ways a frozen-hash oracle can be defeated from inside.**

## Performance

- **Duration:** 70 min
- **Completed:** 2026-09-03
- **Tasks:** 3 (all `type="auto" tdd="true"`)
- **Files modified:** 7 (3 created: `shape_ids.json` + two evidence transcripts; 4 modified: `test_blast_radius_invariance.py`, `rekey_ledger.py`, `test_rekey_ledger.py`, `MILESTONES.md`)

## Accomplishments

- Pinned all seven of D-07's `to_dict()` key lists element-wise -- top-level (11 keys), `voltage` (6), `banner` (3), `auto_capture` (8), `transport_health` (5), `db_diff` (3), `steps[0]` (13) -- every measured list matching the plan's stated literals exactly on first measurement. The three keys Phase 181 deletes (`voltage.vpp_mv`, `voltage.vpe_mv`, `banner.locked_steps`) are all present today and all three are inside the pinned lists; the additive `auto_capture.canonical_part_number` key is confirmed absent and pinned absent, so RPT-F1's field lands as a pin failure rather than a silent widening.
- Added a `SCHEMA_VERSION` triple-equality assertion (`SCHEMA_VERSION == "1.7" == baked`) and an anti-vacuity leg proving the seven pins are sensitive in both directions: deleting `voltage` from a real `to_dict()` mapping and separately adding a `canonical_part_number` key both moved the sorted key list away from the pinned constant (transcribed in `evidence/174-03-schema-pins.txt`).
- Committed `tests/fixtures/shape_ids.json`, the sorted sixteen-entry anchor D-10 pins `SHAPE_IDS` against, and closed the registry four ways: the committed anchor (list equality, catching a duplicate too), `FROZEN_HASHES`, `LADDER_PINS`, and the committed snapshot filenames under `tests/fixtures/reports/` (three independent set equalities, each reporting the symmetric difference in both directions). Verified all four collapse to the same sixteen names.
- Proved `build_shape` raises rather than silently returning a report for all three `RESERVED_SHAPE_IDS` names (`prune03-synthesized-fingerprint-match`, `attr01-status-axis-transport-fault`, `uv-slot-write-pass`), and added the closure's own anti-vacuity leg (a locally-mutated copy of the committed anchor, one entry removed and one added, both moving away from `sorted(SHAPE_IDS)` without touching the committed file).
- **Grew the re-key ledger from one row to six.** Every `before_hash` was RECOMPUTED this session against the real `dedup_fingerprint` on a freshly-built shape from a committed builder -- none transcribed from the plan text. All six matched the plan's stated literals exactly: `sst27sf512-six-step` (`4dc282a5d596`, Phase 177 read-back gating), `m27c512-full-all-ok` (`6d3afbc52315`, rejected SDP-step pruning), `m27c512-full-canonical-name` (`776846bf2dc8`, Phase 181 canonical naming avoided), `m27c512-full-blank-check-bad` (`077a32d1a5c4`, Phase 179 UV collapse), `at28c256-full-all-ok-sdp` (`52fb759dc48c`, Phase 177 D-4/D-6 match bucket), `sst27sf512-full-all-ok` (`4b3e52cab987`, Phase 178 status-axis-must-not-rekey).
- Added the row-semantics assertions the ledger's growth requires: `ledger_id` uniqueness, `(shape_id, ledger_id)` pair uniqueness (two rows may legitimately share a `shape_id`), no declared row with `after_hash == before_hash`, exact row count of six, well-defined behaviour on a locally-constructed single-row tuple, the undeclared (`after_hash is None`) case asserting against `before_hash` rather than abstaining, and ascending `ledger_id` order.
- Added the reverse-direction anti-vacuity leg the ledger's own module docstring calls out as untested by plan 174-01: a `MILESTONES.md` copy carrying an extra `RK-174-97-orphan-row` for a `ledger_id` the app ledger does not have makes `check_rekey_ledger.py --milestones` exit 1, naming the orphan -- proving the MILESTONES-to-ledger direction is enforced, not merely ledger-to-MILESTONES.
- Extended `MILESTONES.md`'s `### v1.36 Re-Key Ledger` section to narrate all six rows and added a `| Claim | As inherited | As measured |` corrections table recording four further discrepancies this plan measured (filed-issue count 27 -> 26, the canonical-naming pair, the UV collapse mechanism, the lowercase-title claim falsified by gh#45's `W27E040`), plus the operator-ratified D-06 26-of-26 scope widening as a fifth row carrying no `ledger_id`. The diff is confined to the v1.36 section (`git diff --stat` shows exactly 19 lines changed, all inside lines 16-34).

## Task Commits

Each task produced one or two commits (app submodule, then meta repo where the task also touched meta files), per this repo's sub-repo commit protocol.

1. **Task 1: Pin the report schema's key lists element-wise** (auto, tdd="true") -- `5693bf7` (test, app) + `2c3abd43` (docs, meta -- evidence + gitlink)
2. **Task 2: Close the shape registry four ways, reserve three names** (auto, tdd="true") -- `05f9bb7` (test, app only; no meta files this task)
3. **Task 3: Pre-seed all six ledger rows, narrate them in MILESTONES.md** (auto, tdd="true") -- `0c709fd` (test, app) + `26c88a7e` (docs, meta -- MILESTONES.md + evidence + gitlink)

## Files Created/Modified

- `firestarter_app/tests/fixtures/shape_ids.json` -- the committed sorted sixteen-entry `shape_id` anchor D-10 pins against, plus a `_note` banner
- `firestarter_app/tests/test_blast_radius_invariance.py` -- six new D-07 pinned key-list constants and their tests, a `SCHEMA_VERSION` triple-equality pin, a schema-pin anti-vacuity leg (Task 1: 43 -> 51 tests), plus the four-way `shape_id` closure test, a reserved-name resolution test, and the closure's own anti-vacuity leg (Task 2: 51 -> 55 tests; was 43 after plan 174-02)
- `firestarter_app/tests/fixtures/rekey_ledger.py` -- `LEDGER` grown from one row to six, every row's provenance documented in the module docstring
- `firestarter_app/tests/test_rekey_ledger.py` -- seven new row-semantics assertions plus the reverse-direction orphan-row anti-vacuity leg (16 total, was 8)
- `.planning/MILESTONES.md` -- the v1.36 Re-Key Ledger section grown to six rows plus the new corrections table
- `.planning/phases/174-blast-radius-invariance-harness/evidence/174-03-schema-pins.txt` -- the seven measured key lists beside the pinned constants, and the full pytest run
- `.planning/phases/174-blast-radius-invariance-harness/evidence/174-03-ledger-closure.txt` -- all six ledger rows' before/current recomputation, the checker on the real pair, the checker on a planted orphan-row `MILESTONES.md` copy, and the full ledger test-module run

## Decisions Made

- **All six ledger before-hashes were recomputed, not transcribed** -- every one matched the plan's stated literal on first measurement, so there was no disagreement to report for the ledger rows themselves. This is the third phase-174 plan in a row (research falsified three of D-12's four inherited pairs; 174-02 found a chip-ID mismatch and a snapshot-determinism gap; 174-04 found the discriminator-tag split disagreed with the plan's stated numbers) where the measured value was checked directly against a real function rather than assumed -- this plan's six rows simply confirmed the plan's own already-measured literals exactly.
- **`db_diff` needed a composition helper.** A bare `build_shape()` report's `db_diff` is `None`; the D-07 db_diff key-list pin needed `_to_dict_with_db_diff`, which composes a real `DbDiff` via `build_db_diff` before calling `to_dict()`, mirroring `tools/snapshot_report_shapes.py:render_shape`'s own composition. Without it, the plan's own literal Task 1 verify snippet (`sorted(d['db_diff'])` on a bare `build_shape()` result) raises `TypeError: 'NoneType' object is not iterable` -- confirmed by running the snippet literally before adding the helper.
- **The MILESTONES.md "Projected after_hash" sentence was reworded** to name the read-back-gating row by shape_id and owner rather than repeating the literal ledger_id string a second time, so the file's total count of `RK-174-0` occurrences stays exactly six (one per row) rather than seven -- Task 3's own verify gate asserts exactly six.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking, source-affecting] `db_diff` is `None` on a bare `build_shape()` report, and the D-07 pin needs it populated**
- **Found during:** Task 1, while writing the `db_diff` key-list pin test
- **Issue:** `DiagnosticReport.db_diff` defaults to `None` and no builder in `report_shapes.py` sets it; `_db_diff_dict()` returns `None` when `self.db_diff is None`. The plan's own literal Task 1 verify snippet calls `sorted(d['db_diff'])` directly on `build_shape('sst27sf512-six-step').to_dict()`, which raises `TypeError: 'NoneType' object is not iterable` when run as written (confirmed).
- **Fix:** Added `_to_dict_with_db_diff(shape_id)` to `tests/test_blast_radius_invariance.py`, composing a real `DbDiff` via `build_db_diff` before calling `to_dict()` -- the same composition `tools/snapshot_report_shapes.py:render_shape` already performs for the committed snapshots, reused rather than duplicated. The `db_diff` pin test uses this helper; the other six pins use the simpler `build_shape(...).to_dict()` path since their dicts are never `None`.
- **Files modified:** `firestarter_app/tests/test_blast_radius_invariance.py`
- **Verification:** `test_to_dict_db_diff_key_list_is_pinned` passes; the evidence transcript shows `db_diff=["current_support_status", "ladder_state", "proposed_disposition"] n=3`.
- **Committed in:** `5693bf7` (Task 1 app commit)

**2. [Rule 3 - Blocking, verification-only] The plan's own Task 1 `<verify>` uses `/usr/bin/grep -qx` against JSON-array-shaped lines, tripping the same BRE bracket-range trap 174-01's SUMMARY documented**
- **Found during:** Task 1, running the plan's own literal verify command
- **Issue:** `/usr/bin/grep -qx 'top=["auto_capture", ...]'` and the six sibling lines fail (`rc=1`, no error message, silently non-matching) because POSIX basic regular expressions parse `["..."]` as a bracket expression. This is a defect in the plan's own verify text, not in the evidence file's content -- confirmed by re-running each line with `grep -xF` (fixed-string mode), which matches exactly.
- **Fix:** No source file changed. Verified all seven exact-match lines present via `grep -xF` instead of the plan's literal `-qx`.
- **Files modified:** none (verification-only)
- **Verification:** All seven `-xF` checks pass; the evidence file's content is exactly as measured.
- **Committed in:** N/A (no file changed; documented here for transparency)

**3. [Rule 3 - Blocking, verification-only] The plan's own Task 2 `<verify>` imports `LADDER_PINS` from the wrong module**
- **Found during:** Task 2, running the plan's own literal verify command
- **Issue:** `from tests.fixtures.report_shapes import SHAPE_IDS, FROZEN_HASHES, LADDER_PINS, RESERVED_SHAPE_IDS, build_shape` fails with `ImportError: cannot import name 'LADDER_PINS' from 'tests.fixtures.report_shapes'`. `LADDER_PINS` is defined in `tests/test_blast_radius_invariance.py` (added by plan 174-02), not in `report_shapes.py`. This mirrors the same class of plan-verify-text defect 174-04's SUMMARY documented for a wrong import module.
- **Fix:** No source file changed. Generated the closure-check evidence by importing `LADDER_PINS` from `tests.test_blast_radius_invariance` instead, where it actually lives.
- **Files modified:** none (verification-only)
- **Verification:** The corrected import produces `frozen_eq=True`, `ladder_eq=True`, `snapshot_eq=True`, all matching the plan's expected output.
- **Committed in:** N/A (no file changed; documented here for transparency)

**4. [Rule 3 - Blocking, editorial] MILESTONES.md's pre-existing "Projected after_hash" sentence repeats the read-back-gating row's `ledger_id`, which would break Task 3's own exact-count verify gate**
- **Found during:** Task 3, running the plan's own literal second verify command
- **Issue:** The sentence beneath the ledger table (carried over from plan 174-01) names `RK-174-01-p177-readback-gating` a second time. `test "$(/usr/bin/grep -c 'RK-174-0' .planning/MILESTONES.md)" -eq 6` -- the plan's own gate -- counted 7 occurrences with the sentence unmodified.
- **Fix:** Reworded the sentence to identify the row by shape_id and owner (`the read-back-gating row (sst27sf512-six-step, owner Phase 177)`) instead of repeating the ledger_id literal. No ledger row or hash value changed.
- **Files modified:** `.planning/MILESTONES.md`
- **Verification:** `grep -c 'RK-174-0' .planning/MILESTONES.md` now reads exactly `6`.
- **Committed in:** `26c88a7e` (Task 3 meta commit)

---

**Total deviations:** 4 (1 Rule 3 source-affecting addition needed for the plan's own db_diff pin to be constructible, 2 Rule 3 verification-only plan-text defects, 1 Rule 3 editorial fix needed for the plan's own exact-count verify gate to pass)
**Impact on plan:** None touched a frozen hash literal's value, a ledger row's content, or `firestarter_app/firestarter/`. All four were necessary for the plan's own stated acceptance criteria and verify gates to actually run and pass as written.

## Issues Encountered

None beyond the four deviations above, all resolved within the task they were found in.

## User Setup Required

None -- no external service configuration required.

## Next Phase Readiness

- All three ways a frozen-hash oracle can be defeated from inside are now structurally closed: row deletion (D-10's four-way closure), silent widening (the same closure plus the disjoint-reservation assertion), and an unpinned additive schema key slipping in (D-07's seven element-wise pins).
- The milestone's total known blast radius is stated up front: all six ledger rows carry a recomputed `before_hash` and an empty `after_hash`, so Phases 177/178/179/181 each have a row already waiting for their commit to fill in (D-11's separate-commit rule applies to all four).
- `firestarter_app/firestarter/` (production code) was never touched, confirmed by an empty `git status --porcelain firestarter/` after every commit in this plan.
- All four phase test modules pass together: 110 collected/passed (55 + 16 + 35 + 4), up from the 90-test baseline recorded at plan start -- `tests/test_skip_census.py` was not collected by any command in this plan.
- No blockers.

## Self-Check: PASSED

- `firestarter_app/tests/fixtures/shape_ids.json` -- FOUND, 16 sorted entries, `_note` present
- `firestarter_app/tests/test_blast_radius_invariance.py` -- FOUND, 55 tests collected
- `firestarter_app/tests/fixtures/rekey_ledger.py` -- FOUND, 6 rows, plain unannotated `LEDGER` assignment, 0 comment lines
- `firestarter_app/tests/test_rekey_ledger.py` -- FOUND, 16 tests collected
- `.planning/MILESTONES.md` -- FOUND, 6 `RK-174-0` occurrences, corrections table present, diff confined to the v1.36 section
- `.planning/phases/174-blast-radius-invariance-harness/evidence/174-03-schema-pins.txt` -- FOUND
- `.planning/phases/174-blast-radius-invariance-harness/evidence/174-03-ledger-closure.txt` -- FOUND
- Commit `5693bf7` -- FOUND in `git log` (firestarter_app)
- Commit `2c3abd43` -- FOUND in `git log` (meta)
- Commit `05f9bb7` -- FOUND in `git log` (firestarter_app)
- Commit `0c709fd` -- FOUND in `git log` (firestarter_app)
- Commit `26c88a7e` -- FOUND in `git log` (meta)
- `firestarter_app/firestarter/` porcelain check -- EMPTY (no production code touched) after every commit
- All four phase test modules together -- 110 passed, 0 failed, 0 skipped
- `python3 tools/rekey/check_rekey_ledger.py` -- exits 0, `OK: 6 ledger row(s), 6 MILESTONES.md row(s) bound`
- `tools/snapshot_report_shapes.py --check` -- exits 0, 16/16 match

---
*Phase: 174-blast-radius-invariance-harness*
*Completed: 2026-09-03*
