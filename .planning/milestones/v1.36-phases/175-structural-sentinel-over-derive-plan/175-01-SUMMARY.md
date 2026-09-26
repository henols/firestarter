---
phase: 175-structural-sentinel-over-derive-plan
plan: 01
subsystem: testing
tags: [derive_plan, chip_test, structural-sentinel, anti-vacuity, prune-06]

requires:
  - phase: 174-blast-radius-invariance-harness
    provides: "py3.11 CI-replica venv, dataclasses.replace mutation discipline (CR-01), the no-move-frozen-hash gate this plan re-runs unmoved"
provides:
  - "tests/plan_corpus.py -- shared REAL_DB / plan_corpus() / mock_operator() surface for every sentinel module Phase 175 adds"
  - "tests/test_derive_plan_structural_sentinel.py -- fail-closed 13-op partition, write-to-verify predicate anchored to production cycle_block_bounds, whole-database sweep, anti-vacuity in both shapes D-09 requires"
affects: [175-02, 175-03, 175-04, 175-05, 177]

actuals:
  tokens: 8190
  tasks: 2
  commits: 4

tech-stack:
  added: []
  patterns:
    - "Fail-closed op-vocabulary partition via vars(module) discovery + literal frozenset/dict, no derivation-by-subtraction"
    - "Predicate anchored to a production helper (cycle_block_bounds) rather than re-derived"
    - "dataclasses.replace for every corpus mutation, never copy.copy or in-place attribute assignment"
    - "Anti-vacuity in two shapes: hand-built counter-plans for unreachable edge shapes, mutated-corpus sweep for whole-database sensitivity, plus observed-RED weakening transcripts"

key-files:
  created:
    - firestarter_app/tests/plan_corpus.py
    - firestarter_app/tests/test_derive_plan_structural_sentinel.py
    - .planning/phases/175-structural-sentinel-over-derive-plan/evidence/175-01-tracer-end-to-end.txt
    - .planning/phases/175-structural-sentinel-over-derive-plan/evidence/175-01-anti-vacuity-red-green.txt
  modified:
    - firestarter_app/tests/test_devtest_issue_corpus.py

key-decisions:
  - "REQUIRES_VERIFY is a literal frozenset({OP_WRITE, OP_WRITE_PARTIAL}), never derived by subtraction, per D-01"
  - "write_verify_violations calls the production cycle_block_bounds helper once and treats an out-of-block write as a VIOLATION, never a skip, per D-02"
  - "The plan's '373 plans' UV-block-width figure was measured and found wrong -- the real count is 540 plans (270 distinct UV part numbers x 2 scopes), all 540 with a three-step erase(NA)-widened cycle block; documented in the module docstring using the measured number, not the plan's stated one"

requirements-completed: [PRUNE-06]

coverage:
  - id: D1
    description: "Fail-closed 13-op partition (2 requires-verify, 11 exempt-with-reason), union/intersection total, fourteenth-op injection makes it raise"
    requirement: PRUNE-06
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_derive_plan_structural_sentinel.py#test_op_vocabulary_is_totally_partitioned"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_derive_plan_structural_sentinel.py#test_a_fourteenth_op_fails_the_partition_closed"
        status: pass
    human_judgment: false
  - id: D2
    description: "write_verify_violations predicate: supported+field-matching verify at a higher index inside the same cycle_block_bounds block; out-of-block write is a violation, not a skip; unsupported write skipped by decision"
    requirement: PRUNE-06
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_derive_plan_structural_sentinel.py#test_no_shipped_plan_emits_a_write_without_a_verify"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_derive_plan_structural_sentinel.py#test_a_second_write_outside_the_block_is_a_violation_not_a_skip"
        status: pass
    human_judgment: false
  - id: D3
    description: "Anti-vacuity: nine hand-built counter-plans plus three mutated-corpus legs across all 1354 write-bearing plans, plus four deliberate predicate weakenings each observed RED and transcribed"
    requirement: PRUNE-06
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_derive_plan_structural_sentinel.py (19 tests, full module)"
        status: pass
      - kind: other
        ref: ".planning/phases/175-structural-sentinel-over-derive-plan/evidence/175-01-anti-vacuity-red-green.txt"
        status: pass
    human_judgment: false

duration: 45min
completed: 2026-09-04
status: complete
---

# Phase 175 Plan 01: Structural Sentinel Predicate Spine Summary

**A fail-closed 13-op partition plus a `cycle_block_bounds`-anchored write-to-verify predicate, swept clean across 1,354 shipped `derive_plan` outputs and proven non-vacuous by nine hand-built counter-plans, three mutated-corpus legs, and four deliberately-weakened predicates each observed to fail before being reverted.**

## Performance

- **Duration:** ~45 min
- **Completed:** 2026-09-04T12:06:37Z
- **Tasks:** 2 (Task 1 tracer spine, Task 2 anti-vacuity)
- **Files modified:** 5 (2 new test-side modules, 1 pre-existing test module reformatted, 2 committed evidence transcripts)

## Accomplishments

- `firestarter_app/tests/plan_corpus.py` -- the shared `REAL_DB` / `all_rows` / `PART_NUMBERS` / `SWEEP_SCOPES` / `plan_corpus()` / `mock_operator()` / `plan_with_steps()` / `step()` surface every sentinel module in this phase imports from, built on one `EpromDatabase(skip_local_override=True)` singleton (D-07).
- `firestarter_app/tests/test_derive_plan_structural_sentinel.py` -- the fail-closed 13-op partition (`REQUIRES_VERIFY` = 2 members, `EXEMPT_REASONS` = 11 reasoned entries), the `write_verify_violations` predicate anchored to the production `cycle_block_bounds` helper (D-02), and a whole-database sweep reporting zero violations across all 1,354 shipped `full`/`partial` plans.
- Anti-vacuity in both shapes D-09 requires: nine hand-built counter-plans covering every edge shape the shipped corpus cannot reach (a second write outside the cycle block, a verify at a lower index, an unsupported verify, three field-skewed verifies, a lone write, the vacuously-clean no-write cases, and the currently-unreachable unsupported-write arm), plus three mutated-corpus legs sweeping all 1,354 write-bearing shipped plans.
- Four deliberate weakenings of `write_verify_violations` (unconditional empty return, dropped `supported` conjunct, dropped field-equality conjuncts, out-of-block violation turned into a skip) were each applied, observed to turn the module RED with the exact expected failure set, and reverted -- transcribed verbatim into `evidence/175-01-anti-vacuity-red-green.txt`.
- Measured, not copied: rows=746, names=677, plans=1354, steps=16248, unsupported=9304, all matching the plan's pinned `must_haves`. Every Phase 174 frozen hash (`test_blast_radius_invariance.py` + `test_rekey_ledger.py`) still reports 114 passed. mypy watermark unmoved at 35/35. `firestarter_app/firestarter/` and the firmware repo both report a clean `git status --porcelain`.

## Task Commits

Each task was committed atomically, in `firestarter_app` (test code) and the meta repo (evidence + gitlink):

1. **Task 1: predicate spine** - `8fa6a90` (test) -- `tests/plan_corpus.py` and the first cut of `test_derive_plan_structural_sentinel.py` (7 tests: op census, partition, fourteenth-op non-vacuity, corpus census, whole-database sweep, unsupported-write-count, one-chip `run_plan` alignment). Included a Rule 3 auto-fix reformatting `tests/test_devtest_issue_corpus.py` (pre-existing drift, unrelated to this plan's content, blocking the plan's own whole-tree `ruff format --check` gate).
2. **Task 2 Part A/B: anti-vacuity** - `d386e78` (test) -- nine hand-built counter-plans and three mutated-corpus legs appended to the same sentinel module (19 tests total).
3. **Fix: comment-line removal** - `49c136d` (fix) -- moved two `#`-comment section dividers introduced in commit `d386e78` into function docstrings, restoring the zero-comments invariant this plan's own acceptance criteria assert.
4. **Meta: evidence + gitlink** - `7dabacef` (docs, meta repo) -- both evidence transcripts committed, `firestarter_app` gitlink advanced to `49c136d`.

**Plan metadata:** this SUMMARY's own commit follows, in the meta repo.

## Files Created/Modified

- `firestarter_app/tests/plan_corpus.py` -- shared corpus/operator-double surface (new)
- `firestarter_app/tests/test_derive_plan_structural_sentinel.py` -- the sentinel itself, 19 tests (new)
- `firestarter_app/tests/test_devtest_issue_corpus.py` -- whitespace-only reformat, no semantic change (Rule 3 deviation)
- `.planning/phases/175-structural-sentinel-over-derive-plan/evidence/175-01-tracer-end-to-end.txt` -- Task 1's tracer transcript (census, partition, sweep, alignment, 7-test green run)
- `.planning/phases/175-structural-sentinel-over-derive-plan/evidence/175-01-anti-vacuity-red-green.txt` -- Task 2's W1-W4 RED transcripts plus the restored clean 19-passed run

## Decisions Made

- `REQUIRES_VERIFY` is a literal `frozenset({chip_test.OP_WRITE, chip_test.OP_WRITE_PARTIAL})` per D-01 -- never derived by subtraction from `_CYCLE_BLOCK_START_OPS` or `_DESTRUCTIVE_OPS`, even though both happen to equal the correct answer today.
- The write-inhibited SDP-leg op's exemption reason explicitly names the inequality expectation (`_dispatch_sdp_leg` writes pattern B, expects to read back pattern A) and cites `chip_test.py:3291-3296`, per the plan's load-bearing case.
- `write_verify_violations` treats a write outside `cycle_block_bounds`'s returned range as a VIOLATION, never a skip -- proven with the hand-built `[write, verify, sdp-lock, write, verify]` counter-plan, whose second write at index 3 is flagged exactly as the plan specifies.
- **Measured disagreement with the plan's prose, reported rather than silently reconciled:** the plan's `read_first` narrative states the UV-block-width defect ("the real UV block is three steps wide") affects "373 plans". Measuring against the actual shipped corpus found **540 plans** (270 distinct UV part numbers x 2 scopes), every one of which carries the three-step `write, verify, erase(NA)` block. The module docstring uses the measured 540/270 figures, not the plan's stated 373. This number was not a pinned `must_haves` assertion (those all matched exactly), so no acceptance criterion is affected -- it is prose commentary only, but the anti-vacuity discipline requires reporting a disagreement rather than adjusting either side to match the other.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Reformatted pre-existing ruff-format drift in `tests/test_devtest_issue_corpus.py`**
- **Found during:** Task 1, running the plan's own whole-tree `ruff format --check firestarter/ tests/` gate.
- **Issue:** This file (untouched by this plan, last modified by 174-04's commit `ae077a5`) failed `ruff format --check` with a whitespace-only line-wrap difference, unrelated to this plan's own two new files. It blocked the literal gate command this plan's `<verify>` block runs.
- **Fix:** Ran `ruff format` on that single file. Diff is whitespace-only (one assert statement's message wrapped onto its own line); no semantic change. Confirmed via `ruff format --diff` before applying and by re-running that file's own test suite (42 passed) afterward.
- **Files modified:** `firestarter_app/tests/test_devtest_issue_corpus.py`
- **Verification:** `ruff format --check firestarter/ tests/` now exits 0; `pytest tests/test_devtest_issue_corpus.py` still 100% green.
- **Committed in:** `8fa6a90` (Task 1 commit)

**2. [Rule 1 - Bug] Removed two `#`-comment section dividers introduced in the Task 2 commit**
- **Found during:** Task 2, running the plan's own comment-line scan (`grep -cE '^\s*#'`) after committing Part A/B.
- **Issue:** The Part A and Part B sections were separated by `#`-comment header blocks explaining what each section proves -- a direct violation of this project's standing zero-comments hard rule and this plan's own acceptance criterion.
- **Fix:** Moved both blocks' explanatory prose into the docstrings of the first function each section introduces (`test_planted_counter_plan_with_no_verify_is_flagged` for Part A, `_write_bearing_plans` for Part B). No behavior change: 19 tests passed identically before and after.
- **Files modified:** `firestarter_app/tests/test_derive_plan_structural_sentinel.py`
- **Verification:** `grep -nE '^\s*#'` over both new files now returns nothing; `pytest` still 19 passed; ruff/mypy unchanged.
- **Committed in:** `49c136d`

---

**Total deviations:** 2 auto-fixed (1 blocking pre-existing drift, 1 self-caught rule violation).
**Impact on plan:** Both fixes were mechanical (formatting / prose relocation), no logic changed in either case. No scope creep into production code.

## Issues Encountered

None beyond the two deviations above, both self-detected and self-corrected within this plan's own gates before the final commit.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- The predicate spine (`plan_corpus.py`, `write_verify_violations`, `REQUIRES_VERIFY`/`EXEMPT_REASONS`) is committed, green, and proven non-vacuous. Plans 175-02 through 175-05 expand across this spine per the phase's own dependency plan (erase-blank-check leg, no-drop proof, UV write-scope ceiling pin, phase seal).
- `plan_corpus()`'s cached corpus and `mock_operator()` are ready for the next sentinel module to import via `from tests.plan_corpus import ...` without rebuilding the database or the operator double.
- The 540/270 UV-block-width measurement (vs. the plan's stated 373) should be carried forward as ground truth by any later plan in this phase that cites the UV cycle-block shape.

## Self-Check: PASSED

All key files confirmed present on disk (`plan_corpus.py`, `test_derive_plan_structural_sentinel.py`, both evidence transcripts). All five commit hashes (`8fa6a90`, `d386e78`, `49c136d` in `firestarter_app`; `7dabacef`, `3fb60cfd` in the meta repo) confirmed present in their respective repos' `git log`. All plan-level `<verification>` commands re-run clean: 19/19 sentinel tests pass, 114/114 Phase 174 frozen-hash tests pass, `ruff check`/`ruff format --check` exit 0, mypy watermark reports 35 (watermark: 35), both `git status --porcelain` checks against production code report empty.

---
*Phase: 175-structural-sentinel-over-derive-plan*
*Completed: 2026-09-04*
