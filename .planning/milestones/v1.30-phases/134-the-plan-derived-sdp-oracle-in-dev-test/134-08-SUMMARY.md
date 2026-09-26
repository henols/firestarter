---
phase: 134-the-plan-derived-sdp-oracle-in-dev-test
plan: 08
subsystem: testing
tags: [python, pytest, click, cli_handlers.py, chip_test.py, sdp, leg-14, leg-12, honesty, mypy]

# Dependency graph
requires:
  - phase: 134-07
    provides: "report.sdp_hold_state assigned at the seam, _dev_test_exit_code
      composing D-15's ALLOW-only exit floor beneath D-14's precedence
      (LEG-12 closed in both surfaces) -- this plan's _sdp_recovery_line
      keys directly on report.sdp_hold_state's value"
  - phase: 134-03
    provides: "derive_plan emitting the D-06 six-step SDP leg for the 43
      measured ALLOW chips -- the six-step count this plan's derived
      pass-count test computes FROM a live plan, never restating 6"
provides:
  - "_ALWAYS_WRITES_PASS_COUNT = 6 (cli_handlers.py): the notice's
    write-pass number single-sourced in exactly one place, interpolated
    into _ALWAYS_WRITES_NOTICE -- never restated as a second literal"
  - "_ALWAYS_WRITES_NOTICE rewritten: true pass count, SDP lock named in
    prose, completed-run outcome stated, aborted-run recovery in the word
    'rewrite' -- D-04's printed-FIRST/unconditional ordering and its
    committed pin (test_always_writes_notice_is_the_first_line_
    unconditionally) both stay byte-identically green"
  - "sdp_left_writable(results) -> bool (chip_test.py): pure engine
    predicate, True iff write-restored is present with verdict OK -- the
    'confirmed the part writable again' term D-12's LOUD form keys on"
  - "_SDP_RECOVERY_LOUD / _SDP_RECOVERY_NEUTRAL / SDP_RECOVERY_CONSTANT_NAMES
    (cli_handlers.py): D-12's two named recovery-string constants plus the
    tuple naming them -- LEG-14's scan target for plan 134-09's scoped
    pytest, and the handoff Phase 137's CLOSE-03 extends rather than
    duplicates"
  - "_sdp_recovery_line(*, hold_state, left_writable) -> str: the one thin,
    fully-annotated selector echoed via click.echo after submit_report and
    before the exit computation, on every completed run"
affects: [134-09, 137]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "The notice's number is single-sourced (_ALWAYS_WRITES_PASS_COUNT)
      and interpolated once, then re-derived independently by a live
      derive_plan-driven test -- never restated as a second literal
      anywhere (P-08 prevention 2)."
    - "A whole-report grep for recovery wording is ruled out by
      construction: derive_plan's 0x0D NA reason, the shipped 'erase' op
      string, and the notice's own prose all legitimately contain 'erase'.
      SDP_RECOVERY_CONSTANT_NAMES names the SCOPED subset a future gate
      (134-09, then Phase 137 CLOSE-03) must scan instead."
    - "Recovery selection logic stays a pure string-selector in the mypy
      STRICT island (cli_handlers.py); the op-string knowledge it depends
      on (sdp_left_writable) lives in chip_test.py (P-07's full-scan
      surface, and headroom protection -- cli_handlers.py has only 2
      slots)."
    - "A single make_restore_failed_operator fixture (persist every
      write_eprom call except the globally-LAST one) isolates 'lock
      emitted but restore not confirmed' from 'lock leaked' -- neither
      make_held_lock_operator nor make_leaked_lock_operator can produce
      write-restored's own non-OK verdict, since both persist that call
      for real."

key-files:
  created: []
  modified:
    - firestarter_app/firestarter/cli_handlers.py
    - firestarter_app/firestarter/chip_test.py
    - firestarter_app/tools/check_devtest_orchestrator.py
    - firestarter_app/tests/test_check_devtest_orchestrator.py
    - firestarter_app/tests/test_dev_test_cmd.py

key-decisions:
  - "The recovery echo site sits right before the exit computation (after
    submit_report, not immediately after report.render) -- the plan named
    a range ('after report.render(console) and before the exit
    computation'), and placing it last means it is the final thing
    printed before dev_test decides its exit code, maximizing the chance
    a tester actually reads it."
  - "click.echo(_sdp_recovery_line(...)) is written across three
    statements (hold_state = ...; left_writable = ...; click.echo(...))
    instead of one nested call, because the single-line nested form is
    106+ characters and ruff-format always wraps it across multiple
    physical lines regardless of E501's lint-ignore status -- the task's
    own acceptance criterion (a single-line grep for
    'click.echo(_sdp_recovery_line') needs the call on ONE line, which
    only the three-statement form achieves under the 88-column formatter
    budget."
  - "make_restore_failed_operator persists every write_eprom call except
    the GLOBALLY LAST one (index _ALWAYS_WRITES_PASS_COUNT - 1), rather
    than tracking a per-op counter -- a full ALLOW-chip run's write_eprom
    call sequence is fixed (shipped write x2, then baseline-b,
    baseline-a, inhibited, restored), so the last call is always
    write-restored regardless of chip, and this reuses the same
    single-sourced constant the derived-count test itself proves against
    a live plan."
  - "The Ctrl-C residual test asserts the MEASURED behaviour, not the
    plan's literal framing: Click's BaseCommand.main (standalone mode,
    which CliRunner.invoke uses) catches KeyboardInterrupt itself, prints
    \"Aborted!\", and converts it to sys.exit(1) -- so KeyboardInterrupt
    never propagates OUT of runner.invoke(). The test was written to
    assert that instead (no report file, neither recovery constant in
    result.output), rather than asserting a propagating exception the
    real CliRunner does not produce."

requirements-completed: []
# This plan ticks NOTHING, per its own dispatch scope (repeated verbatim
# from the plan header): LEG-14's recovery wording and its named
# constants land here, but LEG-14's discharging evidence is plan 134-09's
# committed scoped gate PLUS its planted-violation non-vacuity leg --
# closed by 134-09, not here. LEG-12 was already closed by 134-07; this
# plan's recovery lines are an additional surface, not a second discharge
# -- LEG-12 is NOT re-ticked. `git diff -- .planning/REQUIREMENTS.md`
# (run at Self-Check below) confirms zero rows changed.

coverage:
  - id: D1
    description: "_ALWAYS_WRITES_PASS_COUNT single-sources the notice's
      write-pass number (6), interpolated once into _ALWAYS_WRITES_NOTICE;
      a live derive_plan-driven test computes the SAME number independently
      and asserts equality, never restating 6 as a literal in the
      assertion (P-08)."
    requirement: LEG-14
    verification:
      - kind: unit
        ref: "tests/test_dev_test_cmd.py::TestAlwaysWritesNoticeDerivedCountD09::test_pass_count_is_derived_from_a_live_plan_never_a_literal"
        status: pass
    human_judgment: false
  - id: D2
    description: "_ALWAYS_WRITES_NOTICE names the SDP lock in prose, states
      the completed-run outcome, gives the aborted-run recovery in the
      word 'rewrite', and contains no hyphenated _SDP_LEG_OPS literal --
      D-04's printed-FIRST/unconditional pin
      (test_always_writes_notice_is_the_first_line_unconditionally) stays
      untouched and green."
    requirement: LEG-14
    verification:
      - kind: unit
        ref: "tests/test_dev_test_cmd.py::TestAlwaysWritesNoticeDerivedCountD09::test_notice_names_sdp_lock_completed_run_and_rewrite_recovery"
        status: pass
      - kind: unit
        ref: "tests/test_dev_test_cmd.py::TestAlwaysWritesNoticeDerivedCountD09::test_notice_contains_no_sdp_leg_op_literal"
        status: pass
      - kind: unit
        ref: "tests/test_dev_test_cmd.py::TestAlwaysWritesNotice::test_always_writes_notice_is_the_first_line_unconditionally"
        status: pass
    human_judgment: false
  - id: D3
    description: "D-12's two named recovery forms print in the right case,
      end to end through the real CLI: happy path prints NEUTRAL not
      LOUD; lock emitted but write-restored not confirmed prints LOUD not
      NEUTRAL; a gated run that never locks prints NEUTRAL and never
      calls sdp_lock."
    requirement: LEG-14
    verification:
      - kind: unit
        ref: "tests/test_dev_test_cmd.py::TestSdpRecoveryFormsD12::test_happy_path_prints_neutral_not_loud"
        status: pass
      - kind: unit
        ref: "tests/test_dev_test_cmd.py::TestSdpRecoveryFormsD12::test_lock_emitted_and_not_confirmed_writable_prints_loud"
        status: pass
      - kind: unit
        ref: "tests/test_dev_test_cmd.py::TestSdpRecoveryFormsD12::test_gated_run_never_locked_prints_neutral"
        status: pass
      - kind: unit
        ref: "tests/test_dev_test_cmd.py::TestSdpRecoveryFormsD12::test_recovery_constant_names_resolve_to_the_two_real_constants"
        status: pass
    human_judgment: false
  - id: D4
    description: "133 D-07's Ctrl-C residual is recorded, not closed: a
      mid-run KeyboardInterrupt leaves no report and neither recovery
      constant ever reaches result.output; no finally handler was added."
    verification:
      - kind: unit
        ref: "tests/test_dev_test_cmd.py::TestCtrlCResidualNotClosedD12::test_keyboard_interrupt_mid_run_plan_leaves_no_report_and_no_recovery_line"
        status: pass
    human_judgment: false

# Metrics
duration: 38min
completed: 2026-08-04
status: complete
---

# Phase 134 Plan 08: The Rewritten Always-Writes Notice and D-12's Two SDP Recovery Forms Summary

**Rewrote `_ALWAYS_WRITES_NOTICE` with a single-sourced, derived write-pass count (2, was "written
twice"; is 6) that names the SDP lock and gives the aborted-run recovery in the word "rewrite", and
added D-12's two named recovery-string constants (`_SDP_RECOVERY_LOUD`/`_SDP_RECOVERY_NEUTRAL`)
printed via a thin selector on every completed `dev test` run.**

## Performance

- **Duration:** 38 min
- **Started:** 2026-08-04T18:28:56Z (134-07's last commit; this plan's context-reading began here)
- **Completed:** 2026-08-04T19:06:32Z (last task commit, submodule)
- **Tasks:** 3
- **Files modified:** 5, all inside `firestarter_app` submodule (2 production, 3 test/tooling)

## Accomplishments

- Added `_ALWAYS_WRITES_PASS_COUNT = 6` (`cli_handlers.py`) as the notice's single-sourced write-pass
  number, interpolated into `_ALWAYS_WRITES_NOTICE`'s prose exactly once (P-08 prevention 2 -- derive
  it, never write it twice). Measured: the shipped `write` step's own `runs=2` default writes pattern
  A twice, and the SDP leg adds four more single-run write passes of its own (`write-baseline-b` writes
  B, `write-baseline-a` writes A, `write-inhibited` writes B, `write-restored` writes A) -- 2 + 4 = 6,
  against the pre-134 notice's stale claim of "written twice".
- Rewrote `_ALWAYS_WRITES_NOTICE`'s prose: states the true pass count via the new constant, names the
  **SDP lock** (never a hyphenated op literal -- `SDP lock` with a space), states the part is left
  unlocked on a **completed** run, and gives the aborted-run recovery in the word **rewrite** (protocol
  0x0D has no bulk-clear operation at all). D-04's printed-FIRST/unconditional ordering guarantee is
  unchanged: still one static string, same `click.echo` call site (line number still below
  `derive_plan(...)`'s), and the shipped ordering pin
  (`test_always_writes_notice_is_the_first_line_unconditionally`) is untouched and green.
- Added `sdp_left_writable(results: list[StepResult]) -> bool` (`chip_test.py`): a pure engine
  predicate, `True` iff the `write-restored` result exists and its verdict is `VERDICT_OK` -- the "the
  run confirmed the part writable again" term D-12's LOUD recovery form keys on. Lives in the engine
  (P-07's full-scan surface, plus `cli_handlers.py`'s 2-slot mypy headroom), not the handler.
- Added `_SDP_RECOVERY_LOUD`/`_SDP_RECOVERY_NEUTRAL` (`cli_handlers.py`): D-12's two named recovery
  constants. LOUD prints when the lock was genuinely emitted and the run did NOT confirm the part
  writable again; NEUTRAL prints on the happy path and on every NOT-RUN case. Both compose
  `sdp_honesty.unreadable_state_caveat()` at composition time rather than restating its sentence;
  neither contains a hyphenated op literal or the five-letter bulk-clear word.
- Added `SDP_RECOVERY_CONSTANT_NAMES`: the tuple naming exactly these two constants -- LEG-14's scan
  target for plan 134-09's scoped pytest, with an in-source comment recording WHY a whole-report grep
  is ruled out (the report legitimately contains "erase" in `derive_plan`'s 0x0D NA reason, the shipped
  "erase" op string, and the notice's own prose) and handing Phase 137's CLOSE-03 the same tuple to
  extend rather than duplicate.
- Added `_sdp_recovery_line(*, hold_state: str, left_writable: bool) -> str`: the one thin, fully
  annotated selector (STRICT island, headroom 2). Returns LOUD iff `hold_state` is `HELD`/`NOT-HELD`
  (the lock was emitted) AND `left_writable` is `False`; NEUTRAL otherwise. Echoed via `click.echo`
  after `submit_report` and before the exit computation -- the LAST thing `dev_test` prints before
  deciding its exit code, on every completed run (a line prints on the happy path too; silence is not a
  statement, D-12).
- Registered `_sdp_recovery_line` with the P-07 handler census (`tools/check_devtest_orchestrator.py`'s
  `_HANDLER_FUNCTION_NAMES`) and the paired derived-subset expectation
  (`tests/test_check_devtest_orchestrator.py`'s `_EXPECTED_DEV_TEST_REFERENCED_HELPERS`), since
  `dev_test`'s body now calls it directly -- the referenced-helper count moves from six to seven.
- Added `TestAlwaysWritesNoticeDerivedCountD09` (3 tests): a derived-count test that computes the write
  pass count from a live `derive_plan(AT28C256, ..., write_scope="full")` result (`run_plan`'s own
  `runs` default for the multi-run write step, plus one per supported SDP-leg write op) and asserts
  equality with `_ALWAYS_WRITES_PASS_COUNT` -- never restating `6` as a literal; plus two content pins
  (names the SDP lock/completed-run/rewrite, and contains no `_SDP_LEG_OPS` hyphenated substring).
- Added `TestSdpRecoveryFormsD12` (4 tests): three end-to-end CLI runs pinning D-12's two forms --
  happy path (`make_held_lock_operator`) prints NEUTRAL not LOUD; lock emitted but `write-restored` not
  confirmed writable (new `make_restore_failed_operator`, persists every `write_eprom` call except the
  globally-last one) prints LOUD not NEUTRAL; a gated run that never locks (`make_clean_operator`)
  prints NEUTRAL and never calls `sdp_lock` -- plus a resolution pin proving
  `SDP_RECOVERY_CONSTANT_NAMES` resolves to exactly the two real, non-empty constants.
- Added `TestCtrlCResidualNotClosedD12` (1 test): records 133 D-07's residual truthfully rather than
  the plan's literal framing -- MEASURED that Click's `BaseCommand.main` (standalone mode, which
  `CliRunner.invoke` uses) catches `KeyboardInterrupt` itself, prints "Aborted!", and converts it to
  `sys.exit(1)`, so `KeyboardInterrupt` never propagates OUT of `runner.invoke()`. The test instead
  asserts what actually matters for the residual: no report file is ever written, and neither recovery
  constant ever reaches `result.output`. No `finally` handler was added to `dev_test`.
- Ticked **ZERO** requirements in `REQUIREMENTS.md`, per this plan's explicit dispatch scope. LEG-14's
  recovery wording and named constants land here, but its discharging evidence is plan 134-09's
  committed scoped gate plus its planted-violation non-vacuity leg (closed there). LEG-12 was already
  closed by 134-07 and is NOT re-ticked.

## Task Commits

Each task was committed atomically, inside the `firestarter_app` submodule on
`gsd/v1.30-sdp-surface-retirement`:

1. **Task 1: single-source the notice's pass count; rewrite `_ALWAYS_WRITES_NOTICE`; add
   `sdp_left_writable`** - `6ab1304` (feat)
2. **Task 2: D-12's two named SDP recovery forms, echoed after every completed run** - `afe9fce` (feat)
3. **Task 3: D-09's derived-count pin and D-12's two-form behavioural proofs** - `eae4e13` (test)

**Plan metadata:** committed with this SUMMARY (docs: complete plan), in the meta repo.

## Files Created/Modified

- `firestarter_app/firestarter/cli_handlers.py` -- `sdp_honesty` import; `_ALWAYS_WRITES_PASS_COUNT`;
  `_ALWAYS_WRITES_NOTICE` rewritten; `_SDP_RECOVERY_LOUD`/`_SDP_RECOVERY_NEUTRAL`/
  `SDP_RECOVERY_CONSTANT_NAMES`; `_sdp_recovery_line`; the echo call site in `dev_test`.
- `firestarter_app/firestarter/chip_test.py` -- `sdp_left_writable`.
- `firestarter_app/tools/check_devtest_orchestrator.py` -- `_sdp_recovery_line` added to
  `_HANDLER_FUNCTION_NAMES`.
- `firestarter_app/tests/test_check_devtest_orchestrator.py` --
  `_EXPECTED_DEV_TEST_REFERENCED_HELPERS` gained `_sdp_recovery_line` (six to seven).
- `firestarter_app/tests/test_dev_test_cmd.py` -- new imports (`inspect`, `OP_WRITE`,
  `OP_WRITE_PARTIAL`, `_SDP_LEG_OPS`, `derive_plan`, `run_plan`, `_ALWAYS_WRITES_PASS_COUNT`,
  `_SDP_RECOVERY_LOUD`, `_SDP_RECOVERY_NEUTRAL`, `SDP_RECOVERY_CONSTANT_NAMES`, `EpromDatabase`);
  `_REAL_DB` module constant; `make_restore_failed_operator`;
  `TestAlwaysWritesNoticeDerivedCountD09` (3 tests); `TestSdpRecoveryFormsD12` (4 tests);
  `TestCtrlCResidualNotClosedD12` (1 test).

## Decisions Made

- **The recovery echo sits right before the exit computation** (after `submit_report`, not immediately
  after `report.render`) -- the plan named a range, and placing it last means it is the final line
  printed before `dev_test` decides its exit code.
- **`click.echo(_sdp_recovery_line(...))` is split across three statements**, not one nested call --
  the single-line nested form is 106+ characters and `ruff format` always wraps it regardless of
  E501's lint-ignore status; the plan's own acceptance criterion (a single-line grep for
  `click.echo(_sdp_recovery_line`) needs the call on one physical line, which only the three-statement
  form achieves under the 88-column formatter budget.
- **`make_restore_failed_operator` persists every call except the GLOBALLY LAST one**, not a per-op
  counter -- a full ALLOW-chip run's `write_eprom` call sequence is fixed (shipped write x2, then
  baseline-b, baseline-a, inhibited, restored), so the last call is always `write-restored` regardless
  of chip, reusing the same single-sourced `_ALWAYS_WRITES_PASS_COUNT` the derived-count test proves
  against a live plan.
- **The Ctrl-C residual test asserts the MEASURED Click behaviour**, not the plan's literal framing:
  `KeyboardInterrupt` is converted to `sys.exit(1)` by Click's own standalone-mode `main()` before it
  can ever reach `CliRunner.invoke()`'s caller, so the test asserts "no report, no recovery constant in
  output" rather than a propagating exception the real `CliRunner` does not produce.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] A code comment tripped its own `click.echo(_ALWAYS_WRITES_NOTICE)` count-1
acceptance grep**
- **Found during:** Task 1, self-check against the plan's own acceptance criterion
  (`grep -c 'click.echo(_ALWAYS_WRITES_NOTICE)' firestarter/cli_handlers.py` must return 1)
- **Issue:** The D-04 comment above the notice originally quoted the literal call
  `` `click.echo(_ALWAYS_WRITES_NOTICE)` `` as prose, so a plain-text grep counted 2 occurrences (the
  comment plus the real call) -- the same self-catch class 134-07 hit for its own docstring.
- **Fix:** Reworded the comment to describe the call without repeating the literal substring.
- **Files modified:** `firestarter/cli_handlers.py`
- **Verification:** `grep -c 'click.echo(_ALWAYS_WRITES_NOTICE)' firestarter/cli_handlers.py` returns
  `1`; all other acceptance-criteria checks unchanged.
- **Commit:** `6ab1304`

**2. [Rule 3 - Blocking] The single-line nested `click.echo(_sdp_recovery_line(...))` call exceeded
ruff-format's 88-column budget**
- **Found during:** Task 2, verifying the plan's own single-line grep acceptance criterion
- **Issue:** `click.echo(_sdp_recovery_line(hold_state=report.sdp_hold_state,
  left_writable=sdp_left_writable(results)))` is 110 characters with its indentation; `ruff format`
  always wraps a call this long across multiple physical lines regardless of E501's lint-ignore
  status (confirmed by a standalone reproduction), which would make the plan's single-line grep
  acceptance criterion unsatisfiable.
- **Fix:** Extracted `hold_state`/`left_writable` into two short local variables first, so the final
  `click.echo(_sdp_recovery_line(hold_state=hold_state, left_writable=left_writable))` line is 86
  characters and stays on one physical line under `ruff format`.
- **Files modified:** `firestarter/cli_handlers.py`
- **Verification:** `ruff format --check firestarter/ tests/` exits 0;
  `grep -c 'click.echo(_sdp_recovery_line' firestarter/cli_handlers.py` returns `1`.
- **Commit:** `afe9fce`

**3. [Rule 3 - Blocking] `_sdp_recovery_line` was not registered with the P-07 fail-open handler
census, tripping `test_every_helper_referenced_by_dev_test_is_listed`**
- **Found during:** the quick verify set (`test_check_devtest_orchestrator.py` included), same class of
  gap 134-05/134-07 each hit for their own new handler-side helper.
- **Issue:** `tools/check_devtest_orchestrator.py`'s `_HANDLER_FUNCTION_NAMES` allow-list did not list
  the new `_sdp_recovery_line` helper `dev_test`'s body now calls directly.
- **Fix:** Added `_sdp_recovery_line` to `_HANDLER_FUNCTION_NAMES` and to
  `_EXPECTED_DEV_TEST_REFERENCED_HELPERS` (the referenced-helper count moves from six to seven).
- **Files modified:** `tools/check_devtest_orchestrator.py`, `tests/test_check_devtest_orchestrator.py`
- **Verification:** `pytest tests/test_check_devtest_orchestrator.py -o addopts="" -q` -- 26 passed.
- **Commit:** `afe9fce`

---

**Total deviations:** 3 auto-fixed (1 Rule 1 documentation-only self-catch, 2 Rule 3 blocking gates
tripped by this plan's own new code, same class each prior plan in this phase has hit).
**Impact on plan:** None affect behavior. No scope creep.

## Issues Encountered

None beyond the three deviations documented above.

## User Setup Required

None -- no external service configuration required.

## Threat Flags

None new. This plan's `<threat_model>` (T-134-31/32/33/34) is fully covered by the implementation as
written: T-134-31 (the notice under-describing the run) is mitigated by the single-sourced
`_ALWAYS_WRITES_PASS_COUNT` plus the derived-count test over a live `derive_plan`; T-134-32 (wrong
recovery advice naming a bulk-clear operation `0x0D` does not have) is mitigated by the "rewrite"
wording in both named constants, pending plan 134-09's scoped gate plus its planted-violation
non-vacuity leg (not yet built -- this plan's own scope explicitly excludes authoring that gate);
T-134-33 (a hyphenated op literal entering `_ALWAYS_WRITES_NOTICE`) is mitigated by the "SDP lock" prose
form, asserted against `_SDP_LEG_OPS` by this plan's own test and re-measured by the parity gate's
substring test (`test_non_registry_still_has_no_ops`); T-134-34 (claiming a recovery line prints after
Ctrl-C) is mitigated by `TestCtrlCResidualNotClosedD12` recording the residual as open, with plan 134-08
itself named as the mitigation owner via the up-front notice, never a `finally` handler.

## Next Phase Readiness

- The recovery wording and its named constants (`SDP_RECOVERY_CONSTANT_NAMES`) are in place for plan
  134-09 to build its scoped pytest gate against, plus a planted-violation non-vacuity leg proving the
  gate actually fails on a constant saying "erase". This plan deliberately did NOT author that gate
  (D-13, out of scope) and did NOT add a `tools/check_*.py` scanner (Phase 137's CLOSE-03).
- LEG-14 is NOT ticked here -- 134-09 closes it with the committed scoped gate.
- No blockers. mypy headroom unchanged at 2 (33/35, `checked` unchanged at 124 -- no new source modules
  added this plan, only additions to two existing production modules and three existing
  test/tooling modules). Full suite: 1409 -> 1417 passed (+8 new tests), coverage 82.12% (>= 70% floor),
  30 snapshots unchanged. `tools/ci_replica_venv.sh`: all 5 legs green, run twice (once before, once
  after this plan's commits) to confirm the fully-committed state matches the verified working-tree
  state.

## Self-Check: PASSED

- `firestarter_app/firestarter/cli_handlers.py` -- FOUND, contains `_ALWAYS_WRITES_PASS_COUNT = 6`,
  `_SDP_RECOVERY_LOUD`, `_SDP_RECOVERY_NEUTRAL`, `SDP_RECOVERY_CONSTANT_NAMES`, and
  `def _sdp_recovery_line(`.
- `firestarter_app/firestarter/chip_test.py` -- FOUND, contains `def sdp_left_writable(`.
- `firestarter_app/tests/test_dev_test_cmd.py` -- FOUND, contains `class
  TestAlwaysWritesNoticeDerivedCountD09` (3 tests), `class TestSdpRecoveryFormsD12` (4 tests), `class
  TestCtrlCResidualNotClosedD12` (1 test); 45/45 tests in this file pass.
- `firestarter_app/tools/check_devtest_orchestrator.py` -- FOUND, `"_sdp_recovery_line"` present in
  `_HANDLER_FUNCTION_NAMES`.
- Commit `6ab1304` (submodule) -- FOUND in `git -C firestarter_app log --oneline --all`.
- Commit `afe9fce` (submodule) -- FOUND in `git -C firestarter_app log --oneline --all`.
- Commit `eae4e13` (submodule) -- FOUND in `git -C firestarter_app log --oneline --all`.
- `.planning/REQUIREMENTS.md` -- ZERO rows changed (confirmed via `git diff`); LEG-12/LEG-14 and every
  other row untouched.

---
*Phase: 134-the-plan-derived-sdp-oracle-in-dev-test*
*Completed: 2026-08-04*
