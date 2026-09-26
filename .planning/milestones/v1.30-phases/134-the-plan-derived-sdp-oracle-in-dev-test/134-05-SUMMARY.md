---
phase: 134-the-plan-derived-sdp-oracle-in-dev-test
plan: 05
subsystem: testing
tags: [python, pytest, click, cli_handlers.py, exit-code, sdp, leg-06, mypy]

# Dependency graph
requires:
  - phase: 134-02
    provides: "_dispatch_sdp_leg (the read-back-equality oracle) and LEG-06's engine half
      (test_lock_leaked_write_ok_true_b_readback_is_bad, proving (True, B) => BAD),
      deliberately left unticked pending this plan's exit-code half"
  - phase: 134-04
    provides: "_baseline_closes_sdp_gate, the SDP leg's six-step wiring in run_plan, and
      the D-20 unlock-gating that lets a completed leg reach write-restored"
provides:
  - "_overall_exit_code(results) -> int and _EXIT_CODE_PRECEDENCE = (1, 2, 0) -- explicit
    exit-code precedence replacing the naive max() that let marginal (2) numerically
    outrank BAD (1), restoring what the source comment and dev_test's own docstring
    already claimed (D-14, correction 3)"
  - "make_leaked_lock_operator() (tests/test_dev_test_cmd.py) -- a state-tracking,
    read-back-capable ALLOW-chip operator double whose write_eprom genuinely persists
    bytes and whose read_eprom returns whatever was last persisted, with sdp_lock/
    sdp_unlock as pure bookkeeping -- reusable by any later plan needing a full
    six-step SDP leg exercised end to end through the real CLI"
  - "LEG-06 fully discharged (both halves): the engine-level BAD arm (134-02) plus this
    plan's end-to-end exit-1 proof and the mixed BAD+marginal precedence pin (D-14)"
affects: [134-06, 134-07, 134-09, 134-10, 134-11, 137]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Explicit precedence over max(): _overall_exit_code walks an ordered tuple
      (most-severe-first) and returns the first code present in the run's set of
      per-step codes, mirroring dev_validate_family's own `if verdict_int >
      overall_verdict` pattern -- never a numeric max, which silently inverts when a
      less-severe verdict's mapped integer happens to be larger."
    - "State-tracking operator double over static-payload doubles: a fixture whose
      write_eprom persists bytes and whose read_eprom returns them back is more robust
      than either make_clean_operator (writes no file) or a single static payload
      (cannot support a multi-step leg whose steps legitimately expect DIFFERENT
      read-backs in sequence) -- and it makes the 'leaked lock' scenario emerge
      structurally rather than needing bespoke per-step scripting."
    - "A P-07 fail-open handler census (tools/check_devtest_orchestrator.py's
      _HANDLER_FUNCTION_NAMES) must be updated in the SAME commit as any new
      dev_test-body helper, or the deny-list scan silently under-covers the new code --
      caught by the full-suite run, not the plan's own narrower <automated> verify."

key-files:
  created: []
  modified:
    - firestarter_app/firestarter/cli_handlers.py
    - firestarter_app/tests/test_dev_test_cmd.py
    - firestarter_app/tools/check_devtest_orchestrator.py
    - firestarter_app/tests/test_check_devtest_orchestrator.py

key-decisions:
  - "The live D-14 audit re-confirmed RESEARCH's finding exactly, not merely inherited
    it: grep for `exit_code == 2` across the suite found 12 sites total. Two
    (test_dev_test_cmd.py:202/217) are Click's own 'no such option' code. Six
    (test_cli_handlers.py:599/608/619/634/643/753/796) belong to unrelated commands
    (fw mutex errors, --json-without--list, invalid firmware version, the
    consistency-check/write-cycle 3-way hardware-error verdict). Three
    (test_py32_channel_gating.py:178/187/195) are simulated-stable Click Choice/option
    rejections. One (test_validate_oracle.py:307) is dev_validate_family's own r1-abort
    path, an entirely separate command with its own explicit-precedence exit computation.
    test_marginal_disagreement_exits_2 (:648) and its parametrized twin
    (test_exit_code_tristate_unchanged id='marginal', :696) both produce
    write_eprom.side_effect=[True, False] with NO BAD step anywhere. Zero sites mix
    BAD and marginal -- the audit table is recorded here, live, not copied from
    134-CONTEXT.md/RESEARCH.md."
  - "make_leaked_lock_operator's write_outcomes parameter overrides write_eprom's
    RETURN VALUE by call index while STILL persisting the bytes -- chosen over a
    second, entirely separate fixture, so the mixed BAD+marginal pin
    (test_mixed_bad_and_marginal_exits_1_not_2) reuses the exact same state-tracking
    read-back machinery the leaked-lock proof depends on, rather than needing its own
    bespoke double."
  - "_overall_exit_code lives beside _verdict_code/_VERDICT_EXIT_CODES in
    cli_handlers.py (the mypy STRICT island), fully annotated
    (results: list[StepResult]) -> int) per the plan's own headroom constraint (2 of 35).
    StepResult is imported from firestarter.chip_test for the type hint; ruff's isort
    placed it after the VERDICT_* constants (alphabetically, not where I first wrote it) --
    applied ruff's own --fix rather than hand-guessing import order."
  - "Registering _overall_exit_code with tools/check_devtest_orchestrator.py's
    _HANDLER_FUNCTION_NAMES (and the paired _EXPECTED_DEV_TEST_REFERENCED_HELPERS pin in
    tests/test_check_devtest_orchestrator.py) was NOT caught by this task's own narrower
    <automated> verify (test_dev_test_cmd.py + test_cli_handlers.py only) -- it surfaced
    only when the full ci_replica suite ran. Fixed as a Rule 3 (blocking issue) deviation,
    documented below rather than silently folded into the task-1 commit."

requirements-completed: [LEG-06]

coverage:
  - id: D1
    description: "Explicit exit-code precedence (_overall_exit_code/_EXIT_CODE_PRECEDENCE)
      replaces the naive max() so BAD (exit 1) outranks marginal (exit 2) -- D-14"
    requirement: LEG-06
    verification:
      - kind: unit
        ref: "tests/test_dev_test_cmd.py::TestExitPrecedenceLeg06::test_mixed_bad_and_marginal_exits_1_not_2"
        status: pass
      - kind: unit
        ref: "manual: python -c assertions in the plan's acceptance criteria (_overall_exit_code polarity)"
        status: pass
    human_judgment: false
  - id: D2
    description: "LEG-06 end to end: a write that unexpectedly succeeds after the SDP
      lock reports BAD on write-inhibited and exits 1 through the real CLI, with
      sdp_unlock still called (the part is not left locked)"
    requirement: LEG-06
    verification:
      - kind: unit
        ref: "tests/test_dev_test_cmd.py::TestExitPrecedenceLeg06::test_leaked_lock_exits_1"
        status: pass
      - kind: unit
        ref: "tests/test_dev_test_cmd.py::TestExitPrecedenceLeg06::test_baseline_steps_stay_ok_around_the_leaked_lock"
        status: pass
    human_judgment: false
  - id: D3
    description: "Guard: the shipped exit-2 (marginal-only) contract is unedited and
      still passes"
    verification:
      - kind: unit
        ref: "tests/test_dev_test_cmd.py::TestExitCodeMapping::test_marginal_disagreement_exits_2"
        status: pass
      - kind: unit
        ref: "tests/test_dev_test_cmd.py::TestExitCodeMapping::test_exit_code_tristate_unchanged[marginal]"
        status: pass
    human_judgment: false
  - id: D4
    description: "Non-vacuity obligation #5: reverting D-14's precedence fix back to the
      naive max() observed RED once (assert 2 == 1 on the mixed-run test), then
      firestarter/cli_handlers.py restored byte-identically and re-run green"
    verification:
      - kind: other
        ref: "manual RED-then-restore cycle, verbatim output in this SUMMARY's own section below"
        status: pass
    human_judgment: false

# Metrics
duration: 33min
completed: 2026-08-04
status: complete
---

# Phase 134 Plan 05: Exit-Code Precedence (D-14) and LEG-06 End to End Summary

**Replaced `dev test`'s naive `max()` exit-code reduction with explicit precedence
(`_overall_exit_code`) so BAD outranks `marginal`, then discharged LEG-06's remaining
half with an end-to-end CLI proof that a write succeeding after the SDP lock reports
BAD and exits 1 -- plus the mixed BAD+marginal pin D-14 exists for.**

## Performance

- **Duration:** 33 min
- **Started:** 2026-08-04T17:11:37Z (134-04's last commit; this plan's context-reading began here)
- **Completed:** 2026-08-04T17:39:33Z (last task commit, submodule)
- **Tasks:** 2 (plus one Rule-3 deviation commit between them)
- **Files modified:** 4, all inside `firestarter_app` submodule (1 production, 2 test, 1 tooling)

## Accomplishments

- **Re-verified D-14's blocking audit live**, not inherited from RESEARCH/CONTEXT: grepped
  every `exit_code == 2` site across the suite (12 total). Both `test_dev_test_cmd.py`
  sites (`:202`/`:217`) are Click's own "no such option" code. Six `test_cli_handlers.py`
  sites belong to unrelated commands (`fw` mutex errors, `--json` without `--list`,
  invalid firmware version, the `consistency-check`/`write-cycle` 3-way hardware-error
  verdict). Three `test_py32_channel_gating.py` sites are simulated-stable Click
  rejections. One `test_validate_oracle.py` site is `dev_validate_family`'s own r1-abort
  path (a separate command, its own precedence mechanism already). `test_marginal_
  disagreement_exits_2` and its parametrized twin (`id="marginal"`) both produce
  `[True, False]` write disagreement with **no BAD anywhere**. Zero sites mix BAD and
  marginal -- confirmed live, matching the plan's expected result exactly.
- Added `_EXIT_CODE_PRECEDENCE: tuple[int, ...] = (1, 2, 0)` and a fully-annotated
  `_overall_exit_code(results: list[StepResult]) -> int` to `cli_handlers.py`, replacing
  `code = max(_verdict_code(r.verdict) for r in results)` at the exit computation site.
  `_verdict_code`'s `.get(verdict, 0)` stays the single vocabulary source (no sixth
  verdict status introduced). Amended the `:1888-1890`-region comment so its mechanism
  clause is true (explicit precedence, not a numeric maximum) while leaving its
  contract clause and `dev_test`'s own docstring exit contract (`:2119-2121`) byte-unchanged
  -- confirmed via `git diff` showing no hunk in that region.
- Built `make_leaked_lock_operator()` in `tests/test_dev_test_cmd.py`: a
  `Mock(spec=EpromOperator)` whose `write_eprom` persists the bytes it is given (into a
  closure-captured `state` dict, keyed by call order) and whose `read_eprom` returns
  whatever was most recently persisted. `sdp_lock`/`sdp_unlock` are pure bookkeeping --
  nothing in the double enforces a lock, so a `write_eprom` call issued after a
  successful `sdp_lock` still lands. Driving the real CLI against this operator on
  `AT28C256` (a measured SDP-ALLOW chip: `algorithm=13`, `chip-id=0`,
  `memory-size=32768`) makes the six-step SDP leg's `write-baseline-b`/`-a` steps report
  OK (their expected read-backs are exactly what was written), `sdp-lock`/`sdp-unlock`
  report OK, and `write-inhibited` report BAD by construction -- the state-tracking
  design reproduces LEG-06's exact hazard without any bespoke per-step scripting.
  `write_outcomes`, an optional parameter, overrides `write_eprom`'s return value by
  call index while still persisting bytes, used only to manufacture the shipped
  `write` step's own marginal disagreement for the mixed-run pin.
- `test_leaked_lock_exits_1`: drives `runner.invoke(cli, ["dev", "test", "AT28C256"])`
  end to end and asserts BOTH `result.exit_code == 1` AND the `write-inhibited` step's
  own JSON-artifact verdict is `BAD` -- the exit-code assertion alone would not
  discharge LEG-06 (a laundering implementation could satisfy `exit_code == 1` via an
  unrelated BAD step while the leaked write itself reports SKIPPED/NA/OK). Also
  asserts `operator.sdp_unlock.assert_called()`, proving the part is not left locked.
- `test_baseline_steps_stay_ok_around_the_leaked_lock`: a companion proof that the
  leg's other five steps (`write-baseline-b`/`-a`, `sdp-lock`, `sdp-unlock`,
  `write-restored`) all report OK around the BAD `write-inhibited` -- confirming the
  leg genuinely dispatched the inhibited-write step rather than the baseline gate
  (D-08) skipping it.
- `test_mixed_bad_and_marginal_exits_1_not_2` (D-14's own acceptance criterion): a run
  containing both the leaked-lock BAD step and a `marginal` step (the shipped `write`
  op's two runs disagreeing via `write_outcomes=[True, False]`) exits 1, driven end to
  end through the real CLI/`run_plan` wiring rather than by calling
  `_overall_exit_code` directly -- the pin covers the wiring, not just the helper.
- Observed non-vacuity obligation #5 RED once (planted a revert of the exit
  computation back to the naive `max()`; the mixed-run test failed with
  `assert 2 == 1`), then restored `firestarter/cli_handlers.py` byte-identically
  (`git diff` confirmed empty) and re-ran green (verbatim output below).
- Guarded the shipped exit-2 contract: confirmed (via `git diff`, no hunk) that
  `test_marginal_disagreement_exits_2` and its parametrized twin
  (`test_exit_code_tristate_unchanged[marginal]`) are unedited and still pass.
- Ticked **LEG-06** `Complete` in `REQUIREMENTS.md` -- the only requirement this plan
  may mark, per dispatch scope. Both halves cited: the engine-level BAD arm
  (`firestarter_app` commit `4ac946a`, 134-02) and this plan's end-to-end exit-1 proof
  plus the mixed-run pin (commits `d9b14ef`/`6596f4f`/`c56fc32`).

## Task Commits

Each task was committed atomically, inside the `firestarter_app` submodule on
`gsd/v1.30-sdp-surface-retirement`:

1. **Task 1: explicit exit-code precedence (D-14)** - `d9b14ef` (fix)
2. **Deviation (Rule 3): register `_overall_exit_code` with the P-07 handler census +
   ruff's own import-sort fix** - `6596f4f` (fix) -- caught by the full `ci_replica`
   run, not Task 1's own narrower `<automated>` verify.
3. **Task 2: LEG-06 end to end -- leaked lock exits 1, mixed BAD+marginal pin** -
   `c56fc32` (test)

**Plan metadata:** committed with this SUMMARY (docs: complete plan), in the meta repo.

## Files Created/Modified

- `firestarter_app/firestarter/cli_handlers.py` -- `_EXIT_CODE_PRECEDENCE`,
  `_overall_exit_code`; the exit computation site now calls it; the `_VERDICT_EXIT_CODES`
  block comment amended for correction 3; `StepResult` imported from `firestarter.chip_test`.
- `firestarter_app/tests/test_dev_test_cmd.py` -- `_CHIP_ALLOW = "AT28C256"`;
  `make_leaked_lock_operator()`; `TestExitPrecedenceLeg06` with
  `test_leaked_lock_exits_1`, `test_baseline_steps_stay_ok_around_the_leaked_lock`, and
  `test_mixed_bad_and_marginal_exits_1_not_2`.
- `firestarter_app/tools/check_devtest_orchestrator.py` -- `_overall_exit_code` added to
  `_HANDLER_FUNCTION_NAMES` (P-07's fail-open handler census).
- `firestarter_app/tests/test_check_devtest_orchestrator.py` --
  `_EXPECTED_DEV_TEST_REFERENCED_HELPERS` swapped `_verdict_code` for
  `_overall_exit_code` (the derived-subset pin against `dev_test`'s literal body; the
  count stays six).
- `.planning/REQUIREMENTS.md` (meta repo) -- LEG-06 ticked `Complete`, both halves cited.

## Decisions Made

- **State-tracking operator over static-payload or per-op scripted doubles** for the
  new `make_leaked_lock_operator` -- a fixture that persists whatever it is given and
  reads it back makes every one of the leg's four write-shaped steps' read-backs
  correct by construction, regardless of call order or count, and makes the "leaked
  lock" scenario emerge structurally (nothing in the double enforces the lock) rather
  than needing a hand-scripted sequence of returns keyed to call index.
- **`write_outcomes` reuses the same state-tracking machinery** for the mixed
  BAD+marginal pin, rather than a second bespoke fixture -- the shipped `write` step's
  disagreement and the SDP leg's structural BAD coexist in one operator instance,
  which is what makes the pin end-to-end rather than a synthetic composition.
- **`_overall_exit_code` placed beside `_verdict_code`/`_VERDICT_EXIT_CODES`**, fully
  annotated, rather than as a method or a broader refactor -- smallest diff that
  satisfies the mypy STRICT island's `disallow_untyped_defs` requirement within the
  2-of-35 headroom.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] `_overall_exit_code` was not registered with the P-07 fail-open
handler census, tripping `test_every_helper_referenced_by_dev_test_is_listed`**
- **Found during:** the full `tools/ci_replica_venv.sh` run after Task 1 (Task 1's own
  narrower `<automated>` verify, `test_dev_test_cmd.py`+`test_cli_handlers.py`, does not
  exercise `tests/test_check_devtest_orchestrator.py` and so did not catch this).
- **Issue:** `tools/check_devtest_orchestrator.py`'s `_HANDLER_FUNCTION_NAMES` allow-list
  (the P-07 fail-open handler census that converts a prose obligation into a mechanical,
  permanently-enforced invariant, GATE-10) did not list the new `_overall_exit_code`
  helper `dev_test`'s body now references (in place of the direct `_verdict_code` call
  the derived-subset pin previously expected).
- **Fix:** added `_overall_exit_code` to `_HANDLER_FUNCTION_NAMES`
  (`tools/check_devtest_orchestrator.py`) and swapped `_verdict_code` for
  `_overall_exit_code` in `_EXPECTED_DEV_TEST_REFERENCED_HELPERS`
  (`tests/test_check_devtest_orchestrator.py`) -- the count of referenced helpers stays
  six, only the specific name changed, since `_verdict_code` is now called only from
  inside `_overall_exit_code`, not directly from `dev_test`'s body.
- **Files modified:** `firestarter/tools/check_devtest_orchestrator.py`,
  `tests/test_check_devtest_orchestrator.py`. Also folded in ruff's own `--fix` for an
  import-sort ordering (`StepResult` placement in the `firestarter.chip_test` import
  block) discovered by the same full-suite run.
- **Verification:** `pytest tests/test_check_devtest_orchestrator.py -o addopts="" -q`
  -- 26 passed. Full `tools/ci_replica_venv.sh` re-run afterward: all 5 legs green.
- **Commit:** `6596f4f`

---

**Total deviations:** 1 auto-fixed (Rule 3, blocking -- a gate tripped by this plan's own
Task 1 change, surfaced only by the full-suite run).
**Impact on plan:** No scope creep; the fix is a direct, minimal consequence of Task 1's
own new helper.

## Non-Vacuity Obligation #5 (RED output, verbatim)

Reverted the exit computation in `firestarter/cli_handlers.py` from
`code = _overall_exit_code(results)` back to
`code = max(_verdict_code(r.verdict) for r in results)`, then ran
`pytest tests/test_dev_test_cmd.py -k "mixed_bad_and_marginal" -o addopts="" -q`:

```
FAILED tests/test_dev_test_cmd.py::TestExitPrecedenceLeg06::test_mixed_bad_and_marginal_exits_1_not_2
AssertionError: ...
assert 2 == 1
 +  where 2 = <Result SystemExit(2)>.exit_code
1 failed, 28 deselected in 1.97s
```

As expected: with the naive `max()` restored, a run containing both the leaked-lock BAD
step and the shipped write's marginal disagreement exits 2 (marginal's exit code
numerically outranking BAD's), failing the test that pins exit 1. Restored
`firestarter/cli_handlers.py` byte-identically (`git diff firestarter/cli_handlers.py`
confirmed empty immediately before the real commit); re-ran
`pytest tests/test_dev_test_cmd.py -k "exit" -o addopts="" -q` -- 10 passed.

## Issues Encountered

None beyond the one deviation documented above.

## User Setup Required

None -- no external service configuration required.

## Threat Flags

None new. This plan's `<threat_model>` (T-134-19..22) is fully covered by the
implementation as written: T-134-19 (the milestone's headline finding arriving with the
inconclusive exit code) is mitigated by `_overall_exit_code`'s explicit precedence,
pinned by `test_mixed_bad_and_marginal_exits_1_not_2` and non-vacuity obligation #5
observed RED above; T-134-20 (an unrecognised verdict exiting 0) is mitigated by
`_verdict_code`'s `.get(verdict, 0)` staying the single vocabulary source, unchanged;
T-134-21 (an exit-code-only test passing while the verdict is SKIPPED) is mitigated by
`test_leaked_lock_exits_1`'s verdict assertion alongside its exit-code assertion;
T-134-22 (a leaked-lock run leaving the part locked) is mitigated by the same test's
`operator.sdp_unlock.assert_called()`.

## Next Phase Readiness

- LEG-06 is fully discharged (both halves); nothing later in the phase adds to it.
- `_overall_exit_code`/`_EXIT_CODE_PRECEDENCE` are the mechanism plan `134-07`'s D-15
  NOT-RUN exit floor composes ON TOP OF -- this plan deliberately did NOT implement
  that floor (134-07's to add), and left the precedence tuple `(1, 2, 0)` in a form
  that a floor can extend without re-deriving the BAD-outranks-marginal ordering.
- `make_leaked_lock_operator()` is available in `tests/test_dev_test_cmd.py` for any
  later plan needing a full six-step SDP leg exercised end to end through the real CLI
  (e.g. plan `134-10`'s laundering-route tests, though those are chip-ID/gate-shaped
  rather than read-back-shaped and may not need it directly).
- No blockers. mypy headroom unchanged at 2 (33/35, `checked` unchanged at 124 -- no
  new source modules added this plan). Full suite: 1391 -> 1394 passed (+3 new tests),
  coverage 82.09% (>= 70% floor), 30 snapshots unchanged. `tools/ci_replica_venv.sh`:
  all 5 legs green (ruff check + format, mypy watermark, full pytest+coverage).

## Self-Check: PASSED

- `firestarter_app/firestarter/cli_handlers.py` -- FOUND, contains
  `def _overall_exit_code(` and `_EXIT_CODE_PRECEDENCE`.
- `firestarter_app/tests/test_dev_test_cmd.py` -- FOUND, contains
  `def make_leaked_lock_operator(` and `class TestExitPrecedenceLeg06`; 29/29 tests in
  this file pass.
- `firestarter_app/tools/check_devtest_orchestrator.py` -- FOUND,
  `"_overall_exit_code"` present in `_HANDLER_FUNCTION_NAMES`.
- Commit `d9b14ef` (submodule) -- FOUND in `git -C firestarter_app log --oneline --all`.
- Commit `6596f4f` (submodule) -- FOUND in `git -C firestarter_app log --oneline --all`.
- Commit `c56fc32` (submodule) -- FOUND in `git -C firestarter_app log --oneline --all`.
- `.planning/REQUIREMENTS.md` -- LEG-06 is the ONLY requirement row changed (confirmed
  via `git diff`); LEG-12/13/14/17/18 and LEG-09/10/11/15 all untouched.

---
*Phase: 134-the-plan-derived-sdp-oracle-in-dev-test*
*Completed: 2026-08-04*
