---
phase: 121-dev-test-fix-gates-docs-redesign
plan: "02"
subsystem: testing
tags: [dev-test, fail-closed, dispatch, chip_test.py, host-only]

# Dependency graph
requires:
  - phase: 121-01
    provides: audit-matrix golden regen + py3.11 CI-parity venv + ruff extend-exclude for tests/golden,tests/fixtures
provides:
  - "_dispatch_multi_run and _dispatch_step both refuse any op string outside the live _MULTI_RUN_OPS allow-list, before any operator method call"
  - "_MULTI_RUN_OPS repurposed from a dead documentation-only frozenset (RESEARCH C-5: zero references) into the live dispatch allow-list both dispatch layers gate on"
  - "RED-then-GREEN proof with erase_eprom.assert_not_called() as the load-bearing negative-call assertion (RESEARCH Pitfall 1a closed before OP_WRITE_PARTIAL exists)"
affects: [121-06, 121-05, 121-09]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Fail-closed dispatch guard hoisted above all side effects (temp-file creation, pattern generation, operator calls) rather than inline inside the run loop only"
    - "Negative-call assertion (operator.erase_eprom.assert_not_called()) as the load-bearing test proof instead of verdict-only or exit-code-only checks"

key-files:
  created: []
  modified:
    - firestarter_app/firestarter/chip_test.py
    - firestarter_app/tests/test_chip_test.py

key-decisions:
  - "_MULTI_RUN_OPS made LIVE as the dispatch allow-list (answers RESEARCH Open Question 4) rather than documented dead, per the plan's locked deviation from RESEARCH's recommendation"
  - "Refusal check hoisted to the top of _dispatch_multi_run, ahead of _write_region_for/generate_pattern/temp-file creation, so an unrecognised op creates no temp file and computes no pattern"
  - "Inner run-loop else arm kept as a defensive unreachable AssertionError rather than duplicating the refusal logic, since the top-of-function guard already excludes any op outside {OP_WRITE, OP_VERIFY, OP_ERASE} by the time the loop starts"

patterns-established:
  - "Host mirror of Phase 119 D-06/D-07's firmware NULL-main refusal: an unrecognised input never reaches a branch that performs an action; refusal is a spoken StepResult naming the op, never a silent default"

requirements-completed: []  # DEVTEST-04 contributes-only per requirement_ownership; closed later by Plan 121-09. Nothing ticked in REQUIREMENTS.md by this plan.

coverage:
  - id: D1
    description: "_dispatch_multi_run refuses any op string not in _MULTI_RUN_OPS before any operator call, temp-file creation, or pattern computation"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_chip_test.py#test_unhandled_op_fails_closed_never_erases"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_chip_test.py#test_unhandled_op_fails_closed_names_the_op_in_the_reason"
        status: pass
    human_judgment: false
  - id: D2
    description: "_dispatch_step dispatches to _dispatch_multi_run only when step.op is in the live _MULTI_RUN_OPS allow-list; otherwise refuses with a BAD StepResult"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_chip_test.py#test_dispatch_step_refuses_an_op_outside_the_multi_run_allow_list"
        status: pass
    human_judgment: false

# Metrics
duration: 35min
completed: 2026-07-29
status: complete
---

# Phase 121 Plan 02: Fail-Closed Dispatch Guard on Unmapped Op Strings Summary

**Closed RESEARCH Pitfall 1a: an unmapped `Step.op` string can no longer reach `operator.erase_eprom()` or report `VERDICT_OK` in `firestarter_app/firestarter/chip_test.py`'s `_dispatch_step`/`_dispatch_multi_run` dispatch layer — the host mirror of Phase 119 D-06/D-07's firmware NULL-`main` refusal, closed before `OP_WRITE_PARTIAL` (Plan 121-06) exists.**

## Performance

- **Duration:** ~35 min
- **Started:** 2026-07-29T16:14:55Z (per STATE.md session start)
- **Completed:** 2026-07-29T16:55:43Z
- **Tasks:** 2 (RED, GREEN)
- **Files modified:** 2 (`firestarter/chip_test.py`, `tests/test_chip_test.py`)

## Accomplishments

- **Proved the defect empirically before fixing it.** `_dispatch_multi_run("unmapped-op-for-fail-closed-proof", "AT28C256", {"memory-size": 32768}, operator, runs=2)` called `operator.erase_eprom` **twice** and returned `VERDICT_OK` on the pre-fix tree — matching RESEARCH Pitfall 1a's reproduction exactly (2 runs → 2 erase calls → OK).
- **Closed both fall-through paths.** `_dispatch_multi_run` now refuses any `op` not in `_MULTI_RUN_OPS` before `_write_region_for`, `generate_pattern`, or any temp-file creation runs — the refusal is hoisted above every side effect, not just above the operator call. `_dispatch_step`'s previously-unconditional trailing `return _dispatch_multi_run(...)` now gates on membership in `_MULTI_RUN_OPS` too, so an op outside `{OP_ID, OP_BLANK_CHECK, OP_READ} | _MULTI_RUN_OPS` never even reaches `_dispatch_multi_run`.
- **`_MULTI_RUN_OPS` made live, not documented dead.** Answers RESEARCH C-5 / Open Question 4: the frozenset had zero references anywhere in the tree before this plan (it existed only as a comment describing the N≥2 disagreement-policy scope). It is now the dispatch allow-list both `_dispatch_step` and `_dispatch_multi_run` gate on, with its history and the "add here or fail closed by construction" invariant recorded in its own comment block.
- **The run loop's terminal `else: # OP_ERASE`** is now an explicit `elif op == OP_ERASE:` followed by a defensive unreachable `else:` (raises `AssertionError` — the top-of-function guard already excludes everything else by the time the loop runs), replacing the bare `else` that was the literal defect RESEARCH found.
- **The refusal is spoken.** Both refusal paths return a `StepResult` with `verdict=VERDICT_BAD`, `run_count=0`, and a `reason` naming the offending op string and stating it was refused fail-closed rather than falling through — never a silent default that acts.

## Task Commits

1. **Task 1: RED — prove an unhandled op string reaches erase_eprom and reports OK** - `0431473` (test)
2. **Task 2: GREEN — fail-closed arms in _dispatch_multi_run and _dispatch_step, with _MULTI_RUN_OPS made live** - `9ec8e21` (fix)

**Plan metadata:** (this commit, meta repo)

## Files Created/Modified

- `firestarter_app/firestarter/chip_test.py` - `_dispatch_multi_run` refusal guard hoisted above all side effects; `_dispatch_step` allow-list gate; `_MULTI_RUN_OPS` comment rewritten to record it as the live dispatch allow-list; run loop's terminal `else` made explicit
- `firestarter_app/tests/test_chip_test.py` - three RED-then-GREEN tests (`test_unhandled_op_fails_closed_never_erases`, `test_unhandled_op_fails_closed_names_the_op_in_the_reason`, `test_dispatch_step_refuses_an_op_outside_the_multi_run_allow_list`), each asserting `operator.erase_eprom.assert_not_called()` as the load-bearing check

## RED Baseline (verbatim, pre-fix tree)

```
$ python3 -m pytest tests/test_chip_test.py -k fails_closed
FAILED tests/test_chip_test.py::test_unhandled_op_fails_closed_never_erases
  AssertionError: Expected 'erase_eprom' to not have been called. Called 2 times.
  Calls: [call('AT28C256', {'memory-size': 32768}),
   call('AT28C256', {'memory-size': 32768})].
FAILED tests/test_chip_test.py::test_unhandled_op_fails_closed_names_the_op_in_the_reason
  AssertionError: assert 'unmapped-op-for-fail-closed-proof' in ''
   +  where '' = StepResult(op='unmapped-op-for-fail-closed-proof', verdict='OK', reason='', error_code=None, fingerprint=None, run_count=2, divergence=None).reason
2 failed, 81 deselected
```

(The third test, `test_dispatch_step_refuses_an_op_outside_the_multi_run_allow_list`, does not match the `-k fails_closed` filter by name but also failed RED, verbatim: `assert 'OK' == 'BAD'`.) Both failures are real `erase_eprom` calls / a real `VERDICT_OK`, not import or collection errors — a correct RED baseline.

## Decisions Made

- **`_MULTI_RUN_OPS` made live rather than documented dead** — this is the plan's locked deviation from RESEARCH's original recommendation, per the phase's plan graph (`121-CONTEXT`/`121-RESEARCH` C-5 / Open Question 4). Any future op added to the vocabulary (e.g. Plan 121-06's `OP_WRITE_PARTIAL`) must be added to `_MULTI_RUN_OPS` or it fails closed by construction — this is now stated in-source.
- **The op string used for the proof (`"unmapped-op-for-fail-closed-proof"`) is deliberately not `"write-partial"`** and not any of the six existing `OP_*` values, so the guard is proven against a real unrecognised op before `OP_WRITE_PARTIAL` exists, and this proof can never be silently satisfied by a later plan's op addition.
- **The refusal check is hoisted to the very top of `_dispatch_multi_run`**, ahead of `_write_region_for`/`generate_pattern`/temp-file creation, rather than only guarding the operator-call branch inside the loop — this closes T-121-08 (Denial of Service via orphan temp file) as a side effect of closing T-121-05/06.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] `ruff format --check` required a line-collapse in the Task-1 RED test**
- **Found during:** Task 2 (verifying `ruff check`/`ruff format --check` per the task's acceptance criteria)
- **Issue:** The RED test `test_dispatch_step_refuses_an_op_outside_the_multi_run_allow_list`'s `_dispatch_step(...)` call, written across three lines, was one character short of ruff's line-length limit collapsed onto a single line — `ruff format --check firestarter/ tests/` failed with `1 file would be reformatted`, which is a required Task 2 acceptance criterion.
- **Fix:** Ran `ruff format` on the one affected file; the diff is a single line-collapse with zero test-logic change (same assertion, same arguments).
- **Files modified:** `tests/test_chip_test.py` (formatting only; included in the Task 2 GREEN commit alongside `chip_test.py` rather than as a separate third commit, to honor the plan's "exactly two commits" verification target while still meeting the ruff-format acceptance criterion)
- **Verification:** `ruff format --check firestarter/ tests/` exits 0; `python3 -m pytest tests/test_chip_test.py` still 83 passed (no test assertions changed)
- **Committed in:** `9ec8e21` (Task 2 GREEN commit)

---

**Total deviations:** 1 auto-fixed (Rule 3 — blocking CI-gate formatting issue)
**Impact on plan:** Whitespace-only; no test logic, no production logic beyond the planned fail-closed guard. No scope creep.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- `_MULTI_RUN_OPS` is now load-bearing — Plan 121-06 (`OP_WRITE_PARTIAL`) must add the new op string to this frozenset or writes using it will refuse fail-closed by construction (this is the intended safety property, not a bug to route around).
- Full host suite: **1055 passed, 0 failed** (baseline 1052 + 3 new tests from this plan). `ruff check`/`ruff format --check` both exit 0. `tools/check_devtest_orchestrator.py` prints `PASS:` and exits 0.
- `REQUIREMENTS.md` untouched — DEVTEST-04 remains Pending, to be closed by Plan 121-09.
- No blockers for Wave 2's remaining plans (121-03, 121-04).

## Self-Check: PASSED

- FOUND: firestarter_app/firestarter/chip_test.py
- FOUND: firestarter_app/tests/test_chip_test.py
- FOUND commit 0431473 (RED, test-only)
- FOUND commit 9ec8e21 (GREEN, fix)
- Full suite: 1055 passed, 0 failed (`python3 -m pytest tests/ -p no:cacheprovider`)
- `ruff check firestarter/ tests/`: All checks passed
- `ruff format --check firestarter/ tests/`: 96 files already formatted
- `tools/check_devtest_orchestrator.py`: PASS, exit 0
- `sorted(_MULTI_RUN_OPS)` == `['erase', 'verify', 'write']`; `sorted(_DESTRUCTIVE_OPS)` == `['erase', 'write']`
- `git -C /workspaces/firestarter_app status --short`: no untracked/modified files outside this plan's scope
- `.planning/REQUIREMENTS.md`: byte-unchanged (verified via `git status`, not staged/modified)

---
*Phase: 121-dev-test-fix-gates-docs-redesign*
*Completed: 2026-07-29*
