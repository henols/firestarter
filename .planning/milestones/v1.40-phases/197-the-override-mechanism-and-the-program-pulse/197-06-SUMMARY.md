---
phase: 197-the-override-mechanism-and-the-program-pulse
plan: 06
subsystem: testing
tags: [python, wire-dict, golden-layer, pytest, gh-70]

# Dependency graph
requires:
  - phase: 197-05
    provides: "A database whose only diffs from 70c92ce are 13 changed rows (0 support_status changes): 9 unsupported_reason string swaps, RAMTRON/FM1608's electrical.type and electrical.vcc_mv, and the three Fujitsu pulse_duration_us corrections -- measured and recorded in 197-REGEN-DIFF.md."
provides:
  - "tests/golden/wire_dict_expected_deltas_197.json: the measured, non-vacuous, disjoint 197 wire-dict delta layer -- exactly 3 records, all setting pulse-delay, all attributable to datasheet-cited override entries."
  - "tests/test_wire_dict_equivalence.py wired at every site: test 1 renamed and composes all five layers; the 84-flags test composes the 197 layer under option (a), keeping its name, its == 84 and its == {\"flags\"} intact; the pairwise-disjointness tuple holds 10 pairs; a new capable-of-failing test proves the 197 layer's gate can redden."
  - "The full Python 3.11 suite is green: 2065 passed, 32 snapshots passed, 0 failed -- closing the known-red window opened in plan 197-02."
affects: [197-07, 198, 199, 200]

# Actuals (#2632) — pairs with the plan's `estimate` to calibrate future estimates.
# Multi-repo plan: gsd_run query commit disabled for this project per its standing note
# (has twice self-created a stray gsd/v1.40-... branch); commits measured by hand per
# repo, following the 197-01..05 precedent.
actuals:
  tokens: 4755
  tasks: 3
  commits: 5
  commits_by_repo:
    firestarter_app: 3
    meta: 2

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Measure the residual before writing the golden, not after: a throwaway script composed the golden with the four existing delta layers exactly as the test does, captured the live wire dicts through the module's own _capture_wire_dicts (never a reimplementation), and diffed per record -- the resulting collection, not an assumption from research prose, became the committed golden file."
    - "A database-level regeneration diff (13 changed rows) and a wire-level delta layer (3 changed records) are different measurements of the same phase, and the gap between them is itself evidence: the 9 unsupported_reason string swaps never reach the wire because adapter-required chips produce no wire dict, and FM1608's electrical.type/vcc_mv never reach the wire because vcc and type are asserted elsewhere (test_vcc_and_vpp_volts_never_cross_the_wire) to stay off the host-to-wire seam. The 197 golden's own honesty field states this reconciliation explicitly rather than leaving the smaller number unexplained."

key-files:
  created:
    - firestarter_app/tests/golden/wire_dict_expected_deltas_197.json
  modified:
    - firestarter_app/tests/test_wire_dict_equivalence.py
    - .planning/REQUIREMENTS.md

key-decisions:
  - "The measured residual matched the plan's own stated expectation exactly: 3 records, all FUJITSU, all setting pulse-delay, with no fourth record or second field from the FM1608 change. This was confirmed by measurement, not assumed from the plan text -- the throwaway script's output was inspected before the golden file was written, per the plan's own instruction to measure first and write second."
  - "Option (a) taken exactly as specified: the 197 layer is composed into test_exactly_84_records_change_flags_and_no_other_field_moves's expected side. The function keeps its name, its `== 84` and its `== {\"flags\"}` unchanged, and the 153 layer stays excluded from that composition (153 IS the 84 flags deltas the test measures)."
  - "PULSE-03 marked Complete in REQUIREMENTS.md (shared-ID gate, #2388): both plans declaring it in frontmatter (197-05, 197-06) have now finished. Hand-edited two lines (checkbox + traceability-table row), per this project's standing note that the requirements verb reformats the whole file."
  - "gsd_run query commit was not used for any commit in this plan, per this project's standing rule that the verb has twice self-created a stray gsd/v1.40-... branch mid-plan in this repository. All commits were made with plain git commit, with an explicit branch check before and after each one."
  - "The plan's own Task 2 <verify> leg requiring `_DELTAS_197` to appear >= 4 times could not be satisfied by Task 2 alone (it reached 3, exactly mirroring how the 194 layer -- which also has no dedicated capable-of-failing test -- sits at 3 permanently). The 4th reference comes only from Task 3's capable-of-failing test, exactly as the 182 layer's own 4th reference comes from its capable-of-failing test. Both tasks were completed in the same execution before either was treated as fully verified; by the time Task 3 landed, the count was 4 as the check requires."

requirements-completed: [PULSE-03]

coverage:
  - id: D1
    description: "The 197 wire-dict delta layer is measured from the live capture (never transcribed): exactly 3 records (FUJITSU/MBM27128, FUJITSU/MBM27C1000P,MBM27C1000, FUJITSU/MBM27C1001), all setting pulse-delay, non-vacuous against the frozen baseline, and field-disjoint from all four prior layers"
    requirement: PULSE-03
    verification:
      - kind: other
        ref: "python -c '...' asserting deltas/meta keys, meta's 5 keys, non-empty deltas -> LAYER 3 ['pulse-delay']"
        status: pass
      - kind: other
        ref: "python -c '...' non-vacuity against wire_dict_baseline.json -> NON_VACUOUS_OK"
        status: pass
      - kind: other
        ref: "python -c '...' pairwise field-disjointness against 149/153/182/194 -> DISJOINT_OK"
        status: pass
      - kind: other
        ref: "git diff 70c92ce --name-only -- wire_dict_baseline.json + 4 prior delta files -> empty"
        status: pass
    human_judgment: false
  - id: D2
    description: "Both wire-dict tests wired: test 1 renamed to name all five layers and composes them; test_exactly_84_records_change_flags_and_no_other_field_moves composes the 197 layer under option (a), keeping its name and both assertions (== 84, == {\"flags\"}) unchanged; pairwise-disjointness tuple holds 10 pairs; module docstring updated at every site"
    requirement: PULSE-03
    verification:
      - kind: unit
        ref: "tests/test_wire_dict_equivalence.py -o addopts='' -q -rf -> 9 passed"
        status: pass
      - kind: other
        ref: "grep for the renamed test-1 function, the unchanged 84-test name/assertions, _DELTAS_197 count (4), pairwise-disjointness pair count (10) -> all found"
        status: pass
      - kind: other
        ref: "ruff check firestarter/ tests/ && ruff format --check firestarter/ tests/ -> clean"
        status: pass
    human_judgment: false
  - id: D3
    description: "test_the_197_delta_layer_is_capable_of_failing added and passing; full Python 3.11 suite reports zero failures and zero snapshot failures with a passed count above the 2024 pre-phase baseline -- the known-red window opened in 197-02 is closed"
    requirement: PULSE-03
    verification:
      - kind: unit
        ref: "tests/test_wire_dict_equivalence.py::test_the_197_delta_layer_is_capable_of_failing"
        status: pass
      - kind: unit
        ref: "pytest tests/ -o addopts='' -q -rf on Python 3.11.16 -> 2065 passed, 32 snapshots passed, 0 failed"
        status: pass
      - kind: other
        ref: "ruff check/format clean; git status --porcelain empty except a pre-existing unrelated untracked file"
        status: pass
    human_judgment: false

duration: ~50min
completed: 2026-09-18
status: complete
---

# Phase 197 Plan 06: The override mechanism and the program pulse Summary

**Measured the phase's real wire-dict residual at exactly 3 Fujitsu pulse-delay records, wired the new golden layer into both wire-dict tests under option (a), and closed the two-test-red window that had been open since plan `197-02` -- full Python 3.11 suite now 2065 passed, 32 snapshots passed, 0 failed.**

## Performance

- **Duration:** ~50 min
- **Started:** 2026-09-18
- **Completed:** 2026-09-18
- **Tasks:** 3 (all `type="auto"`, two also `tdd="true"`)
- **Files modified:** 3 (1 new golden file, 1 test module edited across 3 commits, 1 REQUIREMENTS.md), plus 1 gitlink

## Accomplishments

- **Task 1 -- measured, not assumed:**
  - Wrote a throwaway script (not committed under `tools/`) that composed `wire_dict_baseline.json`'s
    `records` with the four existing delta layers (149, 153, 182, 194) exactly as the test itself does,
    captured the live wire dicts through the module's own `_capture_wire_dicts` (never a
    reimplementation), and diffed per record.
  - **Measured: exactly 3 records differ**, all `FUJITSU`, all setting only `pulse-delay`:
    `FUJITSU|MBM27128|2` -> 1000, `FUJITSU|MBM27C1000P,MBM27C1000|6` -> 500,
    `FUJITSU|MBM27C1001|7` -> 500. This matched the plan's own stated expectation exactly -- no fourth
    record, no second field, from the `RAMTRON/FM1608` change. The measurement was run and inspected
    before the golden file was written.
  - Emitted `tests/golden/wire_dict_expected_deltas_197.json` from the script's output with the 194
    layer's exact two-key structure and all five `meta` keys, naming the three override entries
    (`tools/datasheet_overrides.json`) that caused each record and their datasheet citations, and
    stating explicitly in `honesty` that the phase's other 10 changed database fields (9
    `unsupported_reason` strings, FM1608's `electrical.type`/`vcc_mv`) were measured to contribute zero
    wire deltas.
  - All four of the task's own `<verify>` checks passed: two-key/five-key structure, non-vacuity against
    the frozen baseline, pairwise field-disjointness against all four prior layers, and zero diff on the
    baseline and prior delta files against `70c92ce`.
- **Task 2 -- wired the layer in at every site, option (a):**
  - Added the `_DELTAS_197` path constant; renamed test 1 to
    `test_live_capture_matches_golden_plus_the_149_and_153_and_182_and_194_and_197_deltas`; added its
    load, non-vacuity block, exact-count block (`== 3`), and folded it into the composition.
  - Extended the pairwise-disjointness tuple from 6 to 10 pairs (197 against each of 149, 153, 182, 194)
    and updated the failure message to name all five layers.
  - Took option (a) on `test_exactly_84_records_change_flags_and_no_other_field_moves`: composed the
    197 layer into `expected` alongside 149, 182 and 194. The function's name, its `assert
    len(changed_keys) == 84` and its `assert changed_fields == {"flags"}` are byte-unchanged; 153 stays
    excluded from this test's composition. Both assertions held on the first run with the layer
    composed in -- no re-measurement in Task 1 was needed.
  - Updated the module docstring's layer list, what-each-layer-sets line, assertion catalogue and
    test-6 description to mention 197.
  - `ruff check`/`ruff format --check` clean; all 8 tests in the module passed after this task.
- **Task 3 -- proved the gate can fail, took the suite green:**
  - Added `test_the_197_delta_layer_is_capable_of_failing`, mirroring the 182 test: composes all five
    delta layers, mutates `FUJITSU|MBM27128|2`'s `pulse-delay` to an illegitimate value, and asserts
    `_describe_record_diff` reports exactly that one record and field.
  - Added the new test to the module docstring's numbered test list (item 9).
  - Ran the full suite on the pinned Python 3.11.16 venv (`/tmp/fs-venv311`): **2065 passed, 32
    snapshots passed, 0 failed** -- above the 2024 pre-phase baseline, with the interpreter confirmed
    as a 3.11 release. `ruff check`/`ruff format --check` clean; `git status --porcelain` in the
    submodule showed only this plan's own uncommitted-then-committed changes plus one pre-existing,
    unrelated untracked file (`datasheets/LST62832I.pdf`, present before this plan started).

## How a reader can tell the tests pass for the right reason

Both previously-red tests now pass because the golden layer they compose against records what
was actually measured to move on the wire, not because the assertions were relaxed:

- The layer's record count (`3`) and field set (`{"pulse-delay"}`) came from a script that captured the
  live database through the same `_capture_wire_dicts` path the test itself uses, diffed it against the
  composed prior golden, and wrote down whatever it found -- the file was written *after* that
  measurement printed `RESIDUAL_RECORD_COUNT=3`, not before.
- `test_exactly_84_records_change_flags_and_no_other_field_moves` still asserts `== 84` and `==
  {"flags"}`, byte-unchanged. If a second, unnoticed wire change had ridden along with this phase's
  work, composing the 197 layer in would have made one of those two assertions fail, and per the plan's
  own instruction that would have sent the work back to Task 1 to re-measure -- it did not fail, on the
  first attempt, because the golden layer is the complete residual.
- The new `test_the_197_delta_layer_is_capable_of_failing` proves the layer's own gate can redden: it is
  not a golden that would pass even if nothing were checked.
- Every entry in the layer is attributable to a named override: all three records trace to
  `tools/datasheet_overrides.json` entries (`FUJITSU/MBM27128`, `FUJITSU/MBM27C1000`,
  `FUJITSU/MBM27C1001`), each citing a datasheet.

## Reconciliation against the orchestrator's ground truth

The orchestrator's independently measured ground truth for this phase (against fork point `70c92ce`)
is 13 changed database rows: 3 Fujitsu pulse corrections, 9 `unsupported_reason` wording changes, and
`RAMTRON/FM1608` (`electrical.type` and `electrical.vcc_mv`). This plan's wire-level measurement found
only 3 changed *wire* records -- the same 3 Fujitsu pulse rows, and no others. This is not a
disagreement; it is a different, narrower measurement (what reaches the wire, not what changed in the
generated JSON), and the gap is fully explained:

- The 9 `unsupported_reason` changes never reach the wire because `support_status="adapter-required"`
  rows produce no wire dict at all (`chip_resolver` rejects them before a wire dict is built) -- these 9
  rows are exactly the same 9 named in `197-REGEN-DIFF.md`.
- `RAMTRON/FM1608`'s `electrical.type` and `electrical.vcc_mv` never reach the wire because neither
  `type` nor `vcc`/`vcc_mv` crosses the host-to-wire seam -- `test_vcc_and_vpp_volts_never_cross_the_wire`
  (unchanged by this plan) already asserts `vcc` never appears in any live wire dict, and `type` is not
  one of the nine wire keys `test_wire_key_union_is_exactly_nine_keys` pins.

13 database rows changed; 3 of them move a value that crosses the wire. Both numbers are correct
measurements of different things, and the 197 golden's own `honesty` field states this reconciliation
so a future reader does not have to re-derive it.

## Task Commits

Each task was committed atomically, inside the submodule (except the gitlink advance):

1. **Task 1: Measure the real wire residual and emit the 197 delta layer** - `firestarter_app@4296908` (feat)
2. **Task 2: Wire the layer into both wire-dict tests, option (a)** - `firestarter_app@224034a` (test)
3. **Task 3: Prove the gate can fail, take the whole suite green** - `firestarter_app@0ac77fe` (test)

**Gitlink advance:** `meta@69ffc74f` (chore: advance firestarter_app gitlink)

**Plan metadata:** committed alongside this SUMMARY.md and REQUIREMENTS.md (see final commit in this plan's history)

_Note: Tasks 2 and 3 are `tdd="true"`; correctness was proven via the plan's own `<verify>` automation
(module test run, structural greps, ruff, the full-suite run) plus the module's existing and new unit
tests, rather than a separate RED->GREEN->REFACTOR commit sequence -- as in plans `197-02` through
`197-05`, each new leg's correctness gate is its own dedicated assertion, executed and inspected before
staging rather than committed as a separate RED commit._

## Files Created/Modified

- `firestarter_app/tests/golden/wire_dict_expected_deltas_197.json` - new; the measured 197 wire-dict delta layer, 3 records, `deltas` + `meta` (5 keys)
- `firestarter_app/tests/test_wire_dict_equivalence.py` - test 1 renamed and extended to compose 5 layers; `test_exactly_84_records_change_flags_and_no_other_field_moves` composes the 197 layer under option (a), name and both assertions unchanged; pairwise-disjointness tuple extended to 10 pairs; new `test_the_197_delta_layer_is_capable_of_failing`; module docstring updated throughout
- `.planning/REQUIREMENTS.md` - `PULSE-03` checkbox and traceability-table row flipped to Complete (2-line diff; both declaring plans, 197-05 and 197-06, now finished)
- `firestarter_app` (gitlink in meta repo) - advanced to `0ac77fe`

## Decisions Made

- **The measured residual matched the plan's stated expectation exactly** (3 records, all `pulse-delay`,
  all Fujitsu) -- confirmed by running the measurement script and inspecting its output before writing
  the golden file, not assumed from the plan text or `197-REGEN-DIFF.md`.
- **Option (a) taken exactly as specified**: the 197 layer composes into the 84-flags test's `expected`
  side; the function's name and both its exact assertions are untouched; 153 stays excluded from that
  composition.
- **`PULSE-03` marked Complete in `REQUIREMENTS.md`** by hand (checkbox + table row only), per this
  project's standing note that the requirements verb reformats the whole file, and per the shared-ID
  gate (#2388) -- both `197-05` and `197-06`, the only two plans declaring it, have now finished.
- **`gsd_run query commit` was not used for any commit**, per this project's standing rule that the verb
  has twice self-created a stray `gsd/v1.40-...` branch mid-plan in this repository. All commits were
  made with plain `git commit`, with an explicit branch check before and after each one.
- **The plan's Task 2 `_DELTAS_197 >= 4` verify leg was satisfied cumulatively across Tasks 2 and 3, not
  by Task 2 alone.** After Task 2, the constant appears 3 times (declaration + load in test 1 + load in
  the 84-test) -- identical to the 194 layer's permanent count, since 194 also has no dedicated
  capable-of-failing test. The 4th reference comes only from Task 3's capable-of-failing test's own
  load, exactly mirroring how the 182 layer's count of 4 comes from its capable-of-failing test. Both
  tasks were completed in the same execution session before either was treated as fully verified, and
  by the time Task 3 landed the count was 4, satisfying the check. See Deviations below.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Plan-authoring inconsistency, self-caught] Task 2's own `_DELTAS_197` reference-count check could not pass from Task 2's edits alone**
- **Found during:** Task 2, running its own `<verify>` block before committing
- **Issue:** The plan's Task 2 `<verify>` includes `test "$(grep -c '_DELTAS_197' ...)" -ge 4`, but Task
  2's scope (wiring test 1 and the 84-test) only produces 3 references -- the same count the 194 layer
  permanently sits at, since 194 has no dedicated capable-of-failing test either. The 4th reference is
  structurally only available once Task 3 adds `test_the_197_delta_layer_is_capable_of_failing`'s own
  load of the constant, mirroring exactly how the 182 layer's 4th reference comes from its
  capable-of-failing test.
- **Fix:** Completed Task 2's commit with the 3 references its own scope produces (matching the 194
  precedent), proceeded immediately to Task 3 in the same execution, and confirmed the count reached 4
  once Task 3's capable-of-failing test was added -- before treating the plan as complete.
- **Files modified:** none beyond what Task 2 and Task 3 already touch (`tests/test_wire_dict_equivalence.py`)
- **Verification:** `grep -c '_DELTAS_197' tests/test_wire_dict_equivalence.py` read `3` after Task 2's
  commit and `4` after Task 3's commit.
- **Committed in:** `224034a` (Task 2), `0ac77fe` (Task 3)

---

**Total deviations:** 1 auto-fixed (1 plan-authoring sequencing detail; no functional, test-strength or
golden-content change)
**Impact on plan:** None on substance. The two-task split of a single wiring gate is a plan-authoring
detail, not a weakening of any assertion, count, or the golden layer's content.

## Issues Encountered

None beyond the plan-authoring sequencing detail documented above. `/tmp/fs-venv311` (Python 3.11.16)
was reused without modification; `ruff` was available in that same venv. The full suite (166.49s) ran
to completion in every invocation. No network access was required for this plan (no
`tools/build_db.py` regeneration was needed -- the database was already the phase's final generated
state from plan `197-05`).

## Known Stubs

None.

## Deleted-comment report (CLAUDE.md "Source code comments — hard rule")

**No comment line was added to any staged `.py` file across all three tasks.** The mandatory check
(`git diff --cached -- '*.py' | grep -E '^\+\s*#' | grep -v '^\+\s*#!'`) printed nothing before every
one of the three `firestarter_app` commits (`4296908`, `224034a`, `0ac77fe`). No existing comment was
deleted or modified in `tests/test_wire_dict_equivalence.py` by this plan -- every edit added new code
alongside the existing structure, and the new golden JSON file has no comment syntax.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- The known-red window opened in plan `197-02` is closed: both
  `tests/test_wire_dict_equivalence.py::test_live_capture_matches_golden_plus_the_149_and_153_and_182_and_194_and_197_deltas`
  and `tests/test_wire_dict_equivalence.py::test_exactly_84_records_change_flags_and_no_other_field_moves`
  pass, and the full Python 3.11 suite reports zero failures and zero snapshot failures.
- `PULSE-03` is answered at both the database level (`197-REGEN-DIFF.md`, from plan `197-05`) and the
  wire level (this plan's golden layer and its reconciliation note).
- No blockers. `197-07`'s inventory work and any later phase can rely on a green suite and a
  five-layer, field-disjoint, capable-of-failing wire-dict golden.
- **PULSE-03 is now Complete in `REQUIREMENTS.md`.** No requirement in this phase's frontmatter is left
  Pending pending a future plan's completion.

## Self-Check: PASSED

- FOUND: `firestarter_app/tests/golden/wire_dict_expected_deltas_197.json`
- FOUND: `firestarter_app/tests/test_wire_dict_equivalence.py`
- FOUND commit: `firestarter_app@4296908`
- FOUND commit: `firestarter_app@224034a`
- FOUND commit: `firestarter_app@0ac77fe`
- FOUND commit: `meta@69ffc74f`
- Both `firestarter_app` and meta repo HEAD confirmed on `v1.40-program-parameter-fidelity`
- Gitlink in meta repo confirmed pointing at `firestarter_app@0ac77fe`
- Full Python 3.11 suite re-run after all tasks: `2065 passed, 32 snapshots passed, 0 failed`
- `.planning/ROADMAP.md` confirmed untouched (`git diff --stat` empty)
- `.planning/STATE.md` confirmed untouched (`git diff --stat` empty)

---
*Phase: 197-the-override-mechanism-and-the-program-pulse*
*Completed: 2026-09-18*
