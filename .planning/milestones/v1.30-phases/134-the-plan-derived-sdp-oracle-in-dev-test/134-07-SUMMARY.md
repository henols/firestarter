---
phase: 134-the-plan-derived-sdp-oracle-in-dev-test
plan: 07
subsystem: testing
tags: [python, pytest, click, cli_handlers.py, sdp, leg-12, exit-code, d-15, mypy]

# Dependency graph
requires:
  - phase: 134-06
    provides: "DiagnosticReport.sdp_hold_state: str field, the eleventh to_dict()
      key, render()'s own console row, SCHEMA_VERSION 1.3 -- the CARRIAGE half
      of LEG-12, deliberately left unassigned (\"\") for this plan to fill"
  - phase: 134-05
    provides: "_EXIT_CODE_PRECEDENCE = (1, 2, 0) and _overall_exit_code(results)
      -- the explicit BAD-outranks-marginal precedence this plan's floor
      composes BENEATH, never replaces"
  - phase: 134-04
    provides: "sdp_hold_state(plan, results) -> str and sdp_oracle_applicable(plan)
      -> bool -- the pure, engine-side HELD/NOT-HELD/NOT-RUN(reason) derivation
      this plan assigns at the seam"
provides:
  - "report.sdp_hold_state = sdp_hold_state(plan, results), assigned immediately
    after report.banner = count_applicable(plan, results) -- the derive-in-engine
    / assign-in-handler seam, closing LEG-12 in both surfaces"
  - "_dev_test_exit_code(results, *, sdp_oracle_not_run: bool) -> int -- D-15's
    ALLOW-only exit floor, composed as a candidate code fed into
    _EXIT_CODE_PRECEDENCE's selection, never via max(code, 2)"
  - "make_held_lock_operator() (tests/test_dev_test_cmd.py) -- a state-tracking
    ALLOW-chip operator double simulating a GENUINELY held SDP lock (the
    inhibited-write call alone refuses to persist), the structural opposite of
    make_leaked_lock_operator"
  - "make_clean_notrun_operator() (tests/test_dev_test_cmd.py) -- an ALLOW-chip
    operator whose write_eprom raises ChipNotFoundError on every call, the ONE
    fixture that puts the oracle into NOT-RUN with zero BAD/marginal anywhere in
    the run, isolating D-15's floor contribution from D-14's precedence"
affects: [134-10, 137]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "The floor CONTRIBUTES a candidate code into _EXIT_CODE_PRECEDENCE's
      selection set, never max(code, 2) -- max(1, 2) == 2 would re-launder a
      BAD run's exit 1 into exit 2, recreating exactly the laundering D-14
      removed. _dev_test_exit_code mirrors _overall_exit_code's own shape
      (compute the observed-code set, then select by precedence) with one
      added member."
    - "ChipNotFoundError (a bare Exception subclass) reaches _run_step's
      belt-and-suspenders (ChipNotImplementedError, ChipNotFoundError) except
      clause and maps to SKIPPED; ChipNotImplementedError does NOT -- it is an
      EpromOperationError subclass, caught by the EARLIER, BAD-mapping except
      clause first. Measured live, not assumed from the class names."
    - "A verdict-multiset-preserving unit pin (two calls to
      _dev_test_exit_code against the IDENTICAL results list, varying only
      sdp_oracle_not_run) is the only honest way to pin D-15's stated
      non-purity cost -- every engine-level route to a NOT-RUN oracle changes
      at least one step's verdict too, so no CLI-driven fixture can hold the
      multiset literally constant while varying only the hold state."

key-files:
  created: []
  modified:
    - firestarter_app/firestarter/cli_handlers.py
    - firestarter_app/tools/check_devtest_orchestrator.py
    - firestarter_app/tests/test_check_devtest_orchestrator.py
    - firestarter_app/tests/test_dev_test_cmd.py

key-decisions:
  - "Item 1 of the D-15 composition pins (\"ALLOW chip, oracle NOT-RUN, no BAD
    and no marginal anywhere\") is NOT achievable via a real, unmodified
    AT28C256 CLI run through either organic gate route: the baseline gate
    always introduces a BAD or marginal verdict on the baseline step itself
    (make_clean_operator's zero-length read-back; the all-zero-readback
    marginal case), and the destructive (chip-ID) gate route needs a synthetic
    nonzero-chip-id DB fixture -- explicitly Wave-0/134-10 territory (D-17),
    not this plan's to build. MEASURED the one legitimate engine route that
    keeps the whole run at zero BAD/marginal: raising ChipNotFoundError from
    write_eprom reaches _run_step's belt-and-suspenders except clause
    (verdict SKIPPED, not BAD) for every write_eprom-dispatched step,
    including both baseline directions -- closing the baseline gate via
    SKIPPED (which _baseline_closes_sdp_gate treats identically to BAD/
    marginal/NA) with nothing anywhere reporting BAD or marginal.
    make_clean_notrun_operator() implements this, verified live before
    committing (not assumed from the exception hierarchy)."
  - "The non-purity cost test (`test_identical_verdict_multiset_differing_exit_code`)
    is deliberately UNIT-level (direct calls to _dev_test_exit_code with the
    literal same results list), not CLI-driven -- the plan's own text asks for
    an \"identical verdict multiset\", and no real engine fixture can vary the
    hold state while holding the multiset constant (every route to NOT-RUN
    changes at least one verdict too, as the item-1 finding above shows).
    Documented in the test's own docstring rather than silently upgraded to a
    CLI test that would not actually satisfy \"identical\"."
  - "make_held_lock_operator gates on the FLAG_SKIP_SDP_UNLOCK bit (imported
    from firestarter.constants) rather than tracking call index or op name --
    _dispatch_sdp_leg sets this flag on the write-inhibited call ONLY (D-01),
    so keying the double off the flag itself (rather than a fragile
    call-count assumption) makes the fixture robust to any future step
    reordering."

requirements-completed: [LEG-12]
# LEG-13 is named in this plan's frontmatter `requirements:` field as
# CONTRIBUTES-TO-BUT-MUST-NOT-TICK, per the dispatch scope and 134-06-PLAN.md's
# own text: "LEG-13's discharging evidence is a pinning test on
# count_applicable for an ALLOW chip, which is plan 134-10's. Closed by plan
# 134-10." This plan wires the floor and proves count_applicable's ratio
# already drops (D-15's own measured finding: no new counting logic needed),
# but does NOT add the count_applicable pinning test 134-10 owns, and does
# NOT tick LEG-13. `git diff -- .planning/REQUIREMENTS.md` confirms LEG-12 is
# the ONLY row changed (checked below in Self-Check).

coverage:
  - id: D1
    description: "report.sdp_hold_state assigned at the seam
      (cli_handlers.py, immediately after report.banner =
      count_applicable(plan, results)) from chip_test.sdp_hold_state(plan,
      results) -- the derive-in-engine / assign-in-handler shape every other
      derived report field in this handler already follows"
    requirement: LEG-12
    verification:
      - kind: unit
        ref: "tests/test_dev_test_cmd.py::TestHoldStateLeg12::test_hold_state_held_reaches_both_surfaces"
        status: pass
      - kind: unit
        ref: "tests/test_dev_test_cmd.py::TestHoldStateLeg12::test_hold_state_not_held_reaches_both_surfaces"
        status: pass
      - kind: unit
        ref: "tests/test_dev_test_cmd.py::TestHoldStateLeg12::test_hold_state_not_run_reason_reaches_both_surfaces"
        status: pass
    human_judgment: false
  - id: D2
    description: "The NOT-RUN reason survives into BOTH the console
      (normalized against Rich's box-drawing/word-wrapping) and the JSON
      artifact -- LEG-12 says NOT-RUN(reason), and a reason reaching only
      the JSON is half the requirement. Also demonstrates
      operator.sdp_lock.assert_not_called() and the banner's dropped
      n_ran < m_applicable ratio (LEG-13's own mechanism, not touched by
      this plan) end to end."
    requirement: LEG-12
    verification:
      - kind: unit
        ref: "tests/test_dev_test_cmd.py::TestHoldStateLeg12::test_hold_state_not_run_reason_reaches_both_surfaces"
        status: pass
    human_judgment: false
  - id: D3
    description: "_dev_test_exit_code composes D-15's ALLOW-only exit floor
      as a precedence candidate, never max(code, 2): a clean ALLOW-chip
      NOT-RUN run floors to exit 2; a BAD+NOT-RUN run still exits 1; a
      marginal+NOT-RUN run exits 2; a REFUSE chip's legitimate NOT-RUN is
      never floored (exits 0)."
    verification:
      - kind: unit
        ref: "tests/test_dev_test_cmd.py::TestExitFloorD15::test_clean_notrun_floors_to_2"
        status: pass
      - kind: unit
        ref: "tests/test_dev_test_cmd.py::TestExitFloorD15::test_bad_and_notrun_exits_1_not_2"
        status: pass
      - kind: unit
        ref: "tests/test_dev_test_cmd.py::TestExitFloorD15::test_marginal_and_notrun_exits_2"
        status: pass
      - kind: unit
        ref: "tests/test_dev_test_cmd.py::TestExitFloorD15::test_refuse_chip_notrun_exits_0"
        status: pass
    human_judgment: false
  - id: D4
    description: "D-15's stated cost, pinned mechanically: dev test's exit
      code stops being a pure function of step verdicts -- two calls to
      _dev_test_exit_code against the IDENTICAL results list differ only in
      sdp_oracle_not_run and produce different exit codes (0 vs 2)."
    verification:
      - kind: unit
        ref: "tests/test_dev_test_cmd.py::TestExitFloorD15::test_identical_verdict_multiset_differing_exit_code"
        status: pass
    human_judgment: false
  - id: D5
    description: "count_applicable/chip_test.py/diagnostic_report.py are
      UNTOUCHED by this plan (git diff --stat is empty for both production
      files) -- the ratio already drops per D-15's own measurement, no new
      counting logic added, and the parity inversion guard stays green."
    verification:
      - kind: other
        ref: "git diff --stat firestarter/chip_test.py firestarter/diagnostic_report.py -- empty"
        status: pass
      - kind: unit
        ref: "tests/test_op_registration_parity.py::test_non_registry_still_has_no_ops"
        status: pass
    human_judgment: false

# Metrics
duration: 29min
completed: 2026-08-04
status: complete
---

# Phase 134 Plan 07: The Hold-State Seam and D-15's ALLOW-Only Exit Floor Summary

**Assigned `chip_test.sdp_hold_state(plan, results)` at the derive-in-engine / assign-in-handler
seam (closing LEG-12 in both surfaces), and composed D-15's non-running-oracle exit floor as a
precedence candidate beneath D-14's BAD-outranks-marginal ordering, never via `max(code, 2)`.**

## Performance

- **Duration:** 29 min
- **Started:** 2026-08-04T17:59:45Z (134-06's last commit; this plan's context-reading began here)
- **Completed:** 2026-08-04T18:28:56Z (last task commit, submodule)
- **Tasks:** 2 (plus one Rule-3 deviation commit between them)
- **Files modified:** 4, all inside `firestarter_app` submodule (2 production, 1 tooling, 1 test)

## Accomplishments

- Assigned `report.sdp_hold_state = sdp_hold_state(plan, results)` in `cli_handlers.py`,
  immediately after `report.banner = count_applicable(plan, results)` -- the exact seam named at
  dispatch, matching the derive-in-engine / assign-in-handler shape every other derived report
  field there already follows. Imported `sdp_hold_state`/`sdp_oracle_applicable`/`SDP_HOLD_NOT_RUN`
  from `firestarter.chip_test`.
- Added `_dev_test_exit_code(results: list[StepResult], *, sdp_oracle_not_run: bool) -> int` beside
  `_overall_exit_code` in the mypy STRICT island, fully annotated. It computes the observed-code set
  exactly as `_overall_exit_code` does, adds `2` to that set when `sdp_oracle_not_run` is `True`, and
  selects via `_EXIT_CODE_PRECEDENCE` -- never `code = max(code, 2)` (which would return `2` for a
  BAD+NOT-RUN run, `max(1, 2) == 2`, re-creating exactly the laundering D-14 removed). Verified the
  acceptance-criteria python snippet's four assertions pass (OK+NOT-RUN=2, BAD+NOT-RUN=1,
  marginal+NOT-RUN=2, OK+RUN=0) and `grep -c 'max(code, 2)\|max(2, code)'` returns 0 in the shipped
  source (the docstring itself had to be reworded once it tripped that same grep on its own
  illustrative prose -- see Deviations).
- Wired the call site: `code = _dev_test_exit_code(results, sdp_oracle_not_run=sdp_oracle_applicable(plan)
  and report.sdp_hold_state.startswith(SDP_HOLD_NOT_RUN))` -- the floor gates on
  `sdp_oracle_applicable(plan)`, so a REFUSE chip's legitimate `NOT-RUN` (the oracle was never
  applicable at all) is never floored.
- Registered `_dev_test_exit_code` with `tools/check_devtest_orchestrator.py`'s
  `_HANDLER_FUNCTION_NAMES` (P-07's fail-open handler census, GATE-10) and swapped the name in
  `tests/test_check_devtest_orchestrator.py`'s `_EXPECTED_DEV_TEST_REFERENCED_HELPERS` -- the
  derived-subset count stays six (`_overall_exit_code` is now called only from inside
  `_dev_test_exit_code`, mirroring `_verdict_code`'s own earlier demotion in plan 134-05).
- Built `make_held_lock_operator()` (`tests/test_dev_test_cmd.py`): a state-tracking ALLOW-chip
  double whose `write_eprom` persists every call EXCEPT the one carrying `FLAG_SKIP_SDP_UNLOCK`
  (the inhibited-write call, D-01's one flag narrowing) -- that call returns `True` (the state
  machine completed, the ack was observed) but does not persist, simulating a die that genuinely
  refuses the write. The structural opposite of `make_leaked_lock_operator` (134-05).
- Built `make_clean_notrun_operator()`: `write_eprom` raises `ChipNotFoundError` on every call.
  MEASURED live (not assumed from the exception class names) that `ChipNotFoundError` -- unlike
  `ChipNotImplementedError`, which IS an `EpromOperationError` subclass and is caught by the
  earlier, BAD-mapping `except EpromOperationError` clause first -- reaches `_run_step`'s
  belt-and-suspenders `except (ChipNotImplementedError, ChipNotFoundError)` clause and maps every
  `write_eprom`-dispatched step (including both baseline directions) to `SKIPPED`, never `BAD`.
  `_baseline_closes_sdp_gate` treats `SKIPPED` identically to `BAD`/`marginal`/`NA` (D-08), so this
  is the ONE fixture that puts the oracle into `NOT-RUN` with ZERO `BAD`/`marginal` anywhere in the
  whole run -- isolating D-15's floor contribution from D-14's precedence, which the separate
  BAD+NOT-RUN pin exercises.
- Added `TestHoldStateLeg12` (3 tests): `HELD`/`NOT-HELD`/`NOT-RUN(reason)` each proven to reach
  BOTH the console (via a `_normalize_console_text` helper that strips Rich's box-drawing borders
  and collapses word-wrapping, since the `NOT-RUN` reason wraps across three console lines at
  default width) and the JSON artifact (strict equality against the imported `SDP_HOLD_*`
  constants -- deliberately checking the `sdp_hold_state ` PREFIX together with the value in the
  console assertions, since `NOT-HELD` contains `HELD` as a substring and a bare `"HELD" in output`
  check would false-positive on a `NOT-HELD` run). The `NOT-RUN` test also asserts
  `operator.sdp_lock.assert_not_called()` and `banner["n_ran"] < banner["m_applicable"]`.
- Added `TestExitFloorD15` (5 tests): the four end-to-end composition pins (clean NOT-RUN floors to
  2; BAD+NOT-RUN exits 1 not 2; marginal+NOT-RUN exits 2; REFUSE-chip NOT-RUN exits 0) plus a
  direct unit-level `_dev_test_exit_code` pin proving the IDENTICAL `results` list (literally the
  same object) exits differently (0 vs 2) depending solely on `sdp_oracle_not_run` -- D-15's stated
  non-purity cost, made mechanical.
- Confirmed `git diff --stat firestarter/chip_test.py firestarter/diagnostic_report.py` is empty --
  this plan touches neither file, per its own declared scope.
- Ticked **LEG-12** `Complete` in `REQUIREMENTS.md` -- the only requirement this plan may mark, per
  dispatch scope. **LEG-13 explicitly left `[ ]`** (134-10's to close with its own pinning test on
  `count_applicable`).

## Task Commits

Each task was committed atomically, inside the `firestarter_app` submodule on
`gsd/v1.30-sdp-surface-retirement`:

1. **Task 1: assign the hold state at the seam; compose D-15's floor beneath D-14's precedence** -
   `defb0f5` (feat)
2. **Deviation (Rule 3): register `_dev_test_exit_code` with the P-07 handler census** - `a20bcf9`
   (fix) -- required the instant `dev_test`'s body stopped calling `_overall_exit_code` directly.
3. **Task 2: LEG-12 end to end in both surfaces, plus the D-15 exit-floor composition pins** -
   `361aafe` (test)

**Plan metadata:** committed with this SUMMARY (docs: complete plan), in the meta repo.

## Files Created/Modified

- `firestarter_app/firestarter/cli_handlers.py` -- `sdp_hold_state`/`sdp_oracle_applicable`/
  `SDP_HOLD_NOT_RUN` imports; `report.sdp_hold_state = sdp_hold_state(plan, results)` at the seam;
  `_dev_test_exit_code`; the exit computation call site updated.
- `firestarter_app/tools/check_devtest_orchestrator.py` -- `_dev_test_exit_code` added to
  `_HANDLER_FUNCTION_NAMES`.
- `firestarter_app/tests/test_check_devtest_orchestrator.py` --
  `_EXPECTED_DEV_TEST_REFERENCED_HELPERS` swapped `_overall_exit_code` for `_dev_test_exit_code`.
- `firestarter_app/tests/test_dev_test_cmd.py` -- `make_held_lock_operator`,
  `make_clean_notrun_operator`, `_normalize_console_text`; `TestHoldStateLeg12` (3 tests);
  `TestExitFloorD15` (5 tests); new imports (`SDP_HOLD_*`, `_dev_test_exit_code`,
  `FLAG_SKIP_SDP_UNLOCK`, `ChipNotFoundError`, `VERDICT_OK`, `StepResult`, `re`).
- `.planning/REQUIREMENTS.md` (meta repo) -- LEG-12 ticked `Complete` with evidence; LEG-13
  untouched (`[ ]`).

## Decisions Made

- **`ChipNotFoundError`, not `ChipNotImplementedError`, for the clean-NOT-RUN fixture** -- measured
  live that `ChipNotImplementedError` is an `EpromOperationError` subclass and is caught by the
  earlier, BAD-mapping `except` clause in `_run_step`, never reaching the belt-and-suspenders
  `(ChipNotImplementedError, ChipNotFoundError)` clause the code comment describes as
  defensive/dead in the normal dispatch path. `ChipNotFoundError` is a bare `Exception` subclass
  and does reach it, mapping to `SKIPPED`.
- **The non-purity cost test is unit-level, not CLI-driven** -- no real ALLOW-chip fixture through
  the actual engine can hold the verdict multiset IDENTICAL while varying only the hold state
  (every organic route to `NOT-RUN` changes at least one step's own verdict too, as the other four
  `TestExitFloorD15` tests demonstrate). A direct `_dev_test_exit_code` call against the literal
  same `results` list is the only honest way to pin "identical multiset, different exit code."
- **Item 1's fixture (`make_clean_notrun_operator`) required abandoning the destructive-gate
  route** -- a synthetic nonzero-chip-id DB entry could also produce a clean NOT-RUN run, but that
  fixture machinery is explicitly Wave-0/134-10 territory (D-17's R1/R2 causal chain); building a
  parallel copy here would be scope creep into a later plan's declared deliverable.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] `_dev_test_exit_code`'s own docstring tripped its own acceptance-criteria grep**
- **Found during:** Task 1, self-check against the plan's own acceptance criterion
  (`grep -c 'max(code, 2)\|max(2, code)' firestarter/cli_handlers.py` must return 0)
- **Issue:** The first draft of `_dev_test_exit_code`'s docstring illustrated the forbidden
  anti-pattern by literally writing `` `code = max(code, 2)` `` as explanatory prose -- a plain-text
  grep (matching the letter of the acceptance criterion, mirroring 134-06's identical self-catch
  for the D-11 dedup comment) cannot distinguish a comment from code.
- **Fix:** Reworded the docstring to describe the anti-pattern without the literal substring
  (`"the builtin numeric maximum applied between the observed code and the floor value"`).
- **Files modified:** `firestarter/cli_handlers.py`
- **Verification:** `grep -c 'max(code, 2)\|max(2, code)' firestarter/cli_handlers.py` returns `0`;
  the acceptance-criteria python snippet's four assertions still pass unchanged.
- **Commit:** `defb0f5`

**2. [Rule 3 - Blocking] `_dev_test_exit_code` was not registered with the P-07 fail-open handler
census, tripping `test_every_helper_referenced_by_dev_test_is_listed`**
- **Found during:** the quick verify set (`test_check_devtest_orchestrator.py` included), same
  class of gap 134-05 hit for `_overall_exit_code`.
- **Issue:** `tools/check_devtest_orchestrator.py`'s `_HANDLER_FUNCTION_NAMES` allow-list did not
  list the new `_dev_test_exit_code` helper `dev_test`'s body now references directly (in place of
  the direct `_overall_exit_code` call the derived-subset pin previously expected).
- **Fix:** added `_dev_test_exit_code` to `_HANDLER_FUNCTION_NAMES` and swapped the name in
  `_EXPECTED_DEV_TEST_REFERENCED_HELPERS` -- the count of referenced helpers stays six, since
  `_overall_exit_code` is now called only from inside `_dev_test_exit_code`, not directly from
  `dev_test`'s body (mirroring `_verdict_code`'s own earlier demotion).
- **Files modified:** `tools/check_devtest_orchestrator.py`, `tests/test_check_devtest_orchestrator.py`
- **Verification:** `pytest tests/test_check_devtest_orchestrator.py -o addopts="" -q` -- 26 passed.
  Full targeted quick set re-run afterward: all green.
- **Commit:** `a20bcf9`

---

**Total deviations:** 2 auto-fixed (1 Rule 1 documentation-only self-catch before commit, 1 Rule 3
blocking gate tripped by Task 1's own new helper, same class as 134-05's identical finding).
**Impact on plan:** Neither affects behavior. No scope creep.

## 133 D-07's Residual (Recorded, Not Closed)

Per the plan's own Task 1 instruction (D): after a Ctrl-C mid-leg, `results = run_plan(...)`
(`cli_handlers.py:2197`, unchanged by this plan) never returns, so neither `sdp_hold_state`'s
assignment nor the exit computation this plan adds is ever reached -- there is no report at all.
This residual is inherited from 133 D-07 and is NOT closed here; the mitigation is plan 134-08's
rewritten up-front notice (printed where it is guaranteed to be seen), not a `finally` handler.
Stated here rather than silently claimed fixed, matching every prior plan's honesty discipline in
this phase.

## Issues Encountered

None beyond the two deviations documented above.

## User Setup Required

None -- no external service configuration required.

## Threat Flags

None new. This plan's `<threat_model>` (T-134-27/28/29/30) is fully covered by the implementation as
written: T-134-27 (a non-running oracle exiting 0 and being filed as PASS) is mitigated by D-15's
ALLOW-only floor, pinned end to end by `test_clean_notrun_floors_to_2`; T-134-28 (the floor
re-laundering a BAD run into exit 2) is mitigated by the precedence-candidate composition, pinned by
`test_bad_and_notrun_exits_1_not_2` and the docstring's own naming of the rejected `max(code, 2)`
alternative; T-134-29 (a REFUSE chip's legitimate NOT-RUN inflating its exit code) is mitigated by
`sdp_oracle_applicable(plan)` gating the floor, pinned by `test_refuse_chip_notrun_exits_0`;
T-134-30 (claiming the Ctrl-C report residual is closed) is mitigated by the explicit "Recorded, Not
Closed" section above, naming plan 134-08 as the mitigation owner.

## Next Phase Readiness

- LEG-12 is fully discharged in both surfaces; nothing later in the phase adds to it.
- `_dev_test_exit_code`/`sdp_hold_state`/`sdp_oracle_applicable` are the wiring plan `134-10`'s
  `count_applicable` pinning test (LEG-13) and its six R1-R6 laundering-route tests (LEG-17) both
  build on -- this plan deliberately did NOT add a `count_applicable` pinning test or touch
  `chip_test.py`/`diagnostic_report.py` at all (confirmed empty `git diff --stat` for both).
- `make_held_lock_operator()`/`make_clean_notrun_operator()` are available in
  `tests/test_dev_test_cmd.py` for any later plan needing a genuinely-held-lock double or a
  zero-BAD/marginal NOT-RUN fixture.
- No blockers. mypy headroom unchanged at 2 (33/35, `checked` unchanged at 124 -- no new source
  modules added this plan). Full suite: 1401 -> 1409 passed (+8 new tests), coverage 82.07% (>= 70%
  floor), 30 snapshots unchanged. `tools/ci_replica_venv.sh`: all 5 legs green.

## Self-Check: PASSED

- `firestarter_app/firestarter/cli_handlers.py` -- FOUND, contains
  `def _dev_test_exit_code(results: list[StepResult], *, sdp_oracle_not_run: bool) -> int:` and
  `report.sdp_hold_state = sdp_hold_state(plan, results)`.
- `firestarter_app/tests/test_dev_test_cmd.py` -- FOUND, contains `class TestHoldStateLeg12` (3
  tests) and `class TestExitFloorD15` (5 tests); 37/37 tests in this file pass.
- `firestarter_app/tools/check_devtest_orchestrator.py` -- FOUND, `"_dev_test_exit_code"` present in
  `_HANDLER_FUNCTION_NAMES`.
- Commit `defb0f5` (submodule) -- FOUND in `git -C firestarter_app log --oneline --all`.
- Commit `a20bcf9` (submodule) -- FOUND in `git -C firestarter_app log --oneline --all`.
- Commit `361aafe` (submodule) -- FOUND in `git -C firestarter_app log --oneline --all`.
- `.planning/REQUIREMENTS.md` -- LEG-12 is the ONLY requirement row changed (confirmed via
  `git diff`); LEG-13/14/17/18 and LEG-01…11/15/16 all untouched.

---
*Phase: 134-the-plan-derived-sdp-oracle-in-dev-test*
*Completed: 2026-08-04*
