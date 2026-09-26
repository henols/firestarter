---
phase: 175-structural-sentinel-over-derive-plan
plan: 04
subsystem: testing
tags: [derive_plan, chip_test, run_plan, no-drop-proof, prune-05, anti-vacuity, child-suite-timeout]

requires:
  - phase: 175-structural-sentinel-over-derive-plan
    plan: 01
    provides: "tests/plan_corpus.py shared REAL_DB / PART_NUMBERS / plan_corpus() / mock_operator() surface this plan's sweep imports rather than rebuilding"
  - phase: 175-structural-sentinel-over-derive-plan
    plan: 03
    provides: "tests/fixtures/plan_shapes.json + tests/test_plan_shapes_drift.py -- the frozen half of D-10's no-drop proof this plan's execution half completes"
provides:
  - "alignment_violations(plan, results) and na_verdict_violations(plan, results) -- the execution half of D-10's no-drop proof over the whole shipped database"
  - "SENSITIVITY_SLICE -- a pinned, deterministic 40-plan slice for cheap sensitivity legs any later plan in this phase can reuse"
  - "tests/test_skip_census.py's child-suite timeout raised 180s -> 420s, unblocking every later plan's test additions in this phase from turning that shipped test RED"
affects: [175-05, 177]

actuals:
  tokens: 3958
  tasks: 2
  commits: 2

tech-stack:
  added: []
  patterns:
    - "Execution half + frozen half as two separately-named, mutually-irreplaceable proofs of the same no-drop requirement (D-10), matching 175-03's own docstring argument for why neither substitutes for the other"
    - "A cached whole-database sweep pass (_run_whole_database_sweep, mirroring plan_corpus()'s own caching idiom) shared by two assertion-group test functions to keep a 37-second sweep from being paid twice in one pytest process"
    - "A pinned, deterministic sensitivity slice (SENSITIVITY_SLICE) sized as an absolute floor asserted inside every leg that uses it, so a slice that silently emptied cannot pass"
    - "dataclasses.replace for every StepResult mutation in the sensitivity legs, never an in-place attribute assignment or a copy.copy on the module-cached corpus objects (T-175-20, Phase 174's CR-01 defect in a new shape)"

key-files:
  created:
    - firestarter_app/tests/test_derive_plan_no_drop_sweep.py
    - .planning/phases/175-structural-sentinel-over-derive-plan/evidence/175-04-no-drop-sweep.txt
  modified:
    - firestarter_app/tests/test_skip_census.py

key-decisions:
  - "AT28C256 is not a plan_corpus() key -- the database's part_number field stores comma-joined alias groups (e.g. 'AT28C256,AT28C256E,AT28C256F,AT28HC256,...'), so a bare 'AT28C256' lookup raises KeyError. Measured and corrected during Task 1's own verify gate: every single-plan lookup in this module (the runs=1 guard leg, the short-results-list leg) uses ('M8720', 'full') instead -- the same key test_chip_test.py:2609 already uses for its own one-chip run_plan assertion, so this plan does not introduce a new precedent."
  - "The two whole-database assertion groups (alignment, NA-verdict) share one cached sweep pass via _run_whole_database_sweep rather than each calling run_plan over all 1,354 plans independently -- two independent passes were measured at ~62s combined in this environment (2x ~31s), over the plan's own 70-second combine-or-not threshold, so the shared-cache shape was the one taken, exactly as the plan's action text anticipated."
  - "Child-suite cap raised to 420s, not merely to a value just above the measured 167s-181s range, because 175-05's Gate 5 re-runs this same child suite in wave 3 after all three wave-2 plans (175-02, 175-03, 175-04) have landed their test time together -- 420 carries real headroom for that combined total, not just for this plan's own slice."

requirements-completed: [PRUNE-05]

coverage:
  - id: D1
    description: "The execution half of D-10's no-drop proof: all 1,354 shipped plans run through the real run_plan at runs=2 yield exactly one StepResult per Plan.steps entry (16,248 total, zero misalignments), and every one of the 9,304 unsupported steps' results carries the NA verdict"
    requirement: PRUNE-05
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_derive_plan_no_drop_sweep.py#test_every_plan_yields_one_result_per_step"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_derive_plan_no_drop_sweep.py#test_every_unsupported_step_result_carries_the_na_verdict"
        status: pass
      - kind: other
        ref: ".planning/phases/175-structural-sentinel-over-derive-plan/evidence/175-04-no-drop-sweep.txt (measured sweep census)"
        status: pass
    human_judgment: false
  - id: D2
    description: "The runs=1 plan-guard behaviour proven as a tested fact rather than a comment: run_plan(..., runs=1) returns a single __plan__/BAD result, and runs=1 with allow_single_run=True restores one result per step -- justifying the sweep's deliberate default runs=2"
    requirement: PRUNE-05
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_derive_plan_no_drop_sweep.py#test_a_single_run_returns_only_the_plan_guard_result"
        status: pass
    human_judgment: false
  - id: D3
    description: "Both sweep predicates proven sensitive at 40 of 40 on a pinned, size-asserted slice, a short-results-list guard proven to report rather than truncate, and three deliberate weakenings each observed to turn the module RED before being reverted"
    requirement: PRUNE-05
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_derive_plan_no_drop_sweep.py (6 tests, full module)"
        status: pass
      - kind: other
        ref: ".planning/phases/175-structural-sentinel-over-derive-plan/evidence/175-04-no-drop-sweep.txt (N1-N3 observed RED, restored GREEN)"
        status: pass
    human_judgment: false
  - id: D4
    description: "tests/test_skip_census.py's child-suite timeout raised 180s -> 420s in the same commit as the sweep, with only the timeout literal and the stale docstring duration figure changed -- no assertion, allow-list entry, or parsing rule touched"
    requirement: PRUNE-05
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_skip_census.py (5 tests, unchanged assertions, all pass after the raise)"
        status: pass
      - kind: other
        ref: ".planning/phases/175-structural-sentinel-over-derive-plan/evidence/175-04-no-drop-sweep.txt (measured child-suite wall time before and after)"
        status: pass
    human_judgment: false

duration: 70min
completed: 2026-09-04
status: complete
---

# Phase 175 Plan 04: Execution Half of the No-Drop Proof Summary

**The execution half of D-10's no-drop proof over `derive_plan`: all 1,354 shipped plans run through the real `run_plan` yield exactly one `StepResult` per step (16,248 total, zero misalignments) and every one of 9,304 unsupported steps' results carries the `NA` verdict, both predicates proven sensitive at 40 of 40 on a pinned slice and three deliberate weakenings each observed RED -- plus the child-suite timeout raise this phase's added test time required.**

## Performance

- **Duration:** ~70 min
- **Completed:** 2026-09-04
- **Tasks:** 2 (Task 1 the sweep module + cap raise, Task 2 the sensitivity legs)
- **Files modified:** 3 (1 new test module, 1 modified test module, 1 committed evidence transcript)

## Accomplishments

- `firestarter_app/tests/test_derive_plan_no_drop_sweep.py` -- `alignment_violations(plan, results)` and `na_verdict_violations(plan, results)`, the two predicates D-10's execution half rests on, both imported from the shared `tests/plan_corpus.py` corpus and operator double (never a second `EpromDatabase`, never `monkeypatch`).
- A whole-database sweep at the default `runs=2`, cached once per pytest process (`_run_whole_database_sweep`) and shared by two test functions: `test_every_plan_yields_one_result_per_step` (1,354 plans, 16,248 steps, 16,248 results, zero misalignments) and `test_every_unsupported_step_result_carries_the_na_verdict` (9,304 of 9,304 unsupported steps carry `NA`).
- `test_a_single_run_returns_only_the_plan_guard_result` -- Pitfall 4 as a tested fact: `run_plan(..., runs=1)` returns exactly one `__plan__`/`BAD` result; `runs=1, allow_single_run=True` restores one result per step. Documents why the sweep deliberately uses the default `runs=2`.
- `SENSITIVITY_SLICE` -- a pinned, deterministic 40-plan slice (first 20 `(name, "full")` + first 20 `(name, "partial")` from `sorted(PART_NUMBERS)`), and three sensitivity/guard legs proving both predicates are non-vacuous: dropping a result flags 40/40 plans; flipping one unsupported step's verdict away from `NA` flags 40/40 plans; a results list shorter than the step list is reported, not silently truncated by a positional zip.
- Three deliberate weakenings (N1: `alignment_violations` returns `[]` unconditionally; N2: `na_verdict_violations` returns `[]` unconditionally; N3: the slice-size floor changed from 40 to 41) each applied, observed to turn the module RED with the exact expected failures, and reverted -- transcribed verbatim into `evidence/175-04-no-drop-sweep.txt`, along with the restored clean 6/6-passed run.
- `tests/test_skip_census.py`'s child-suite `timeout=` raised from 180s to 420s in the same commit as the sweep -- the planner-discovered blocker this plan's environment preamble flagged. Measured, not assumed: the child run was 139s at the branch base (with 175-01/02/03 already present) and 167s with this plan's new module also present; 420 carries real headroom for 175-05's Gate 5, which re-runs the same child suite after all three wave-2 plans have landed together.
- Measured, not copied, and every one of the plan's pinned numbers matched on first (corrected) measurement: `sweep_plans=1354`, `sweep_steps=16248`, `sweep_results=16248`, `sweep_misaligned=0`, `sweep_unsupported=9304`, `sweep_na_violations=0`, `single_run_len=1`/`op=__plan__`/`verdict=BAD`. The whole app suite reports **2,151 passed, 0 failed** (2,145 baseline from 175-03 plus these 6 new tests). Phase 174's frozen hashes (`test_blast_radius_invariance.py` + `test_rekey_ledger.py`) still report 114 passed. `ruff check`/`ruff format --check` exit 0. mypy watermark unmoved at 35/35. `firestarter_app/firestarter/` and the firmware repo both report a clean `git status --porcelain`.

## Task Commits

Each task was committed atomically, in `firestarter_app` (test code); the meta commit (evidence + gitlink + this SUMMARY) follows this SUMMARY's own creation:

1. **Task 1: the sweep module and the child-suite cap raise** - `cc4b73c` (test) -- `tests/test_derive_plan_no_drop_sweep.py` (3 tests: whole-database alignment, whole-database NA-verdict, the `runs=1` guard leg) and `tests/test_skip_census.py`'s `timeout=180` -> `timeout=420` plus its corrected docstring duration figure.
2. **Task 2: the sensitivity legs** - `a9c0bde` (test) -- `SENSITIVITY_SLICE` and three more tests (40/40 alignment sensitivity, 40/40 NA-verdict sensitivity, the short-results-list guard), taking the module from 3 to 6 tests.

**Plan metadata:** this SUMMARY's own commit follows, in the meta repo, alongside the evidence transcript and the `firestarter_app` gitlink advance.

## Files Created/Modified

- `firestarter_app/tests/test_derive_plan_no_drop_sweep.py` -- the execution half of D-10's no-drop proof, 6 tests (new)
- `firestarter_app/tests/test_skip_census.py` -- child-suite `timeout=180` -> `timeout=420`, docstring duration figure corrected (modified, 2 lines of substance)
- `.planning/phases/175-structural-sentinel-over-derive-plan/evidence/175-04-no-drop-sweep.txt` -- measured sweep census, child-suite timing before/after, all three weakenings' observed RED output and the restored clean run (new)

## Decisions Made

- `('AT28C256', 'full')` is not a valid `plan_corpus()` key -- the shipped database's `part_number` field groups aliases into one comma-joined string (`'AT28C256,AT28C256E,AT28C256F,...'`), so a bare `'AT28C256'` lookup raises `KeyError`. This is a **measured disagreement with the plan's own verify-script prose**, reported rather than silently reconciled: both single-plan lookups in this module (`test_a_single_run_returns_only_the_plan_guard_result` and `test_a_short_results_list_is_reported_not_truncated`) use `('M8720', 'full')` instead -- the same key `tests/test_chip_test.py:2609` already uses for its own one-chip `run_plan` assertion (`test_safe02_only_known_operator_methods_no_attribute_error`), so this is not a new precedent.
- The two whole-database assertion groups share one cached sweep pass rather than each independently sweeping all 1,354 plans -- measured at ~31s per independent pass in this environment, so two separate passes (~62s combined) would have exceeded the plan's own 70-second "consider combining" threshold. The module docstring records this choice and the measurement that drove it.
- The child-suite cap was set to 420s, not to a tighter value just above the measured 167s (this plan's own child run, with only its own new module present). 175-05's Gate 5 re-runs the same child suite after 175-02 and 175-03's test time also lands, and 420 is sized against that combined total per the plan's own explicit instruction, not against this plan's isolated measurement.
- Every sensitivity-leg mutation uses `dataclasses.replace` for `StepResult` field changes and builds a fresh list (`results[:-1]`, `list(results)`) rather than mutating the module-cached corpus's shared `Step`/`StepResult` objects in place -- Phase 174's CR-01 defect, reapplied here as T-175-20's mitigation.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Corrected the plan's `AT28C256` example key to a real corpus key, `M8720`**
- **Found during:** Task 1, running the plan's own verify-script census command, which itself used `c[('AT28C256','full')]` and raised `KeyError` before printing the `single_run_*` lines.
- **Issue:** The plan's action text and its own verify automation both assumed `('AT28C256', 'full')` is a valid `plan_corpus()` key. Measured against the real corpus: it is not -- `PART_NUMBERS` stores comma-joined alias groups, and the AT28C256 family's actual key is `'AT28C256,AT28C256E,AT28C256F,AT28HC256,AT28HC256E,AT28HC256F,AT28HC256L'`.
- **Fix:** Used `('M8720', 'full')` instead, in both the module's own test code and the ad-hoc verify-script invocation -- the same chip `test_chip_test.py` already uses for its own equivalent one-chip `run_plan` assertion, so no new example-chip precedent was introduced.
- **Files modified:** `firestarter_app/tests/test_derive_plan_no_drop_sweep.py`
- **Verification:** The corrected key resolves; `single_run_len=1`, `single_run_op=__plan__`, `single_run_verdict=BAD` all measured and pinned in the evidence transcript exactly as the plan's `must_haves` specify.
- **Committed in:** `cc4b73c` (Task 1 commit)

**2. [Rule 1 - Bug] Re-ran the N2 and N3 weakening legs after a self-caught evidence-transcript corruption**
- **Found during:** Task 2's own weakening-and-restore sequence. After N1 (weaken `alignment_violations`), the module was restored with `git checkout -- tests/test_derive_plan_no_drop_sweep.py` -- but Task 2's `SENSITIVITY_SLICE` and its three new test functions were still uncommitted at that point (only Task 1's content was on `HEAD`), so `git checkout` silently reverted the working tree all the way back to the Task 1 commit, discarding all of Task 2's uncommitted work. The subsequent N2 run therefore executed against a 3-test file, not the intended 6-test file, and produced a false `3 passed, rc_n2=0` reading -- a corrupted, non-load-bearing transcript entry rather than a real weakening result.
- **Fix:** Restored Task 2's content from an in-session file backup (taken before N1, deliberately as a precaution against exactly this class of mistake) rather than from git. Truncated the evidence transcript back to the end of the valid N1 section, then re-ran N2 (this time correctly reddening 2 of 6 tests) and N3 from the correctly-restored 6-test file, using the same file-backup restore (never `git checkout`) between each weakening for the remainder of the sequence.
- **Files modified:** `firestarter_app/tests/test_derive_plan_no_drop_sweep.py` (working-tree content, no net change versus the intended design); `.planning/phases/175-structural-sentinel-over-derive-plan/evidence/175-04-no-drop-sweep.txt` (corrupted N2 section replaced with the correct one).
- **Verification:** Re-ran the full N1-N2-N3-RESTORED sequence end to end from the corrected 6-test file; N1/N2/N3 each show the expected failure count and `rc_n<N>=1`; the restored run shows `6 passed`/`rc_clean=0`; `diff` against the pre-N1 backup file confirms the restored module is byte-identical to the intended clean state.
- **Committed in:** `a9c0bde` (Task 2 commit) -- the committed module reflects only the correct, final content; the corrupted intermediate state was never staged or committed.

---

**Total deviations:** 2 auto-fixed (1 measured-fact correction against the plan's own text, 1 self-caught execution-mechanics mistake with no effect on the final committed content).
**Impact on plan:** Both fixes are test-side only. The first strengthens accuracy against the plan's own prose (an honest disagreement, per this phase's anti-vacuity discipline); the second was fully self-detected and self-corrected before either weakening result was trusted or committed -- no incorrect evidence reached the final transcript or SUMMARY. No scope creep into production code.

## Issues Encountered

None beyond the two deviations above, both self-detected and self-corrected within this plan's own verification gates before the final commits.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Both halves of D-10's no-drop proof are now committed and green: the frozen half (175-03's `plan_shapes.json` + `test_plan_shapes_drift.py`) and this plan's execution half (`test_derive_plan_no_drop_sweep.py`). Neither substitutes for the other, as both modules' docstrings state.
- `SENSITIVITY_SLICE` is available for any later plan in this phase that needs a cheap, pinned, deterministic sample of the corpus without re-deriving one.
- `tests/test_skip_census.py`'s child-suite cap is now 420s with 253s of headroom over this plan's own measured 167s figure. 175-05's Gate 5 must still confirm the combined post-merge child-suite wall time (all four of this phase's new test modules present) stays under that cap -- this plan's own `child_seconds=167` is explicitly recorded in the evidence transcript as a lower bound, not the final figure.
- No blockers for 175-05's phase seal.

## Self-Check: PASSED

All key files confirmed present on disk (`test_derive_plan_no_drop_sweep.py`, modified `test_skip_census.py`, `evidence/175-04-no-drop-sweep.txt`). Both `firestarter_app` commit hashes (`cc4b73c`, `a9c0bde`) confirmed present via `git log --oneline`. All plan-level `<verification>` commands re-run clean: 6/6 sweep-module tests pass, 5/5 `test_skip_census.py` tests pass after the cap raise, 114/114 Phase 174 frozen-hash tests pass, `ruff check`/`ruff format --check` exit 0, mypy watermark reports 35 (watermark: 35), both `git status --porcelain` checks against production code report empty, and the full app suite reports 2,151 passed, 0 failed.

---
*Phase: 175-structural-sentinel-over-derive-plan*
*Completed: 2026-09-04*
