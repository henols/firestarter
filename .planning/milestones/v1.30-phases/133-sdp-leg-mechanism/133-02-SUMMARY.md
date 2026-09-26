---
phase: 133-sdp-leg-mechanism
plan: 02
subsystem: testing
tags: [chip_test, exception-handling, pytest, ruff, mypy]

# Dependency graph
requires:
  - phase: 133-sdp-leg-mechanism (plan 01)
    provides: "tests/test_chip_test_sdp_leg.py's operator-double harness (with sdp_lock/sdp_unlock
      pre-added) and the three-constant precedence-matrix mechanism
      (_PRE_EDIT_PRECEDENCE_MATRIX / _EXPECTED_PRECEDENCE_MATRIX / _INTENDED_PRECEDENCE_DELTA)"
provides:
  - "_run_step widened to four except clauses: (ProgrammerNotFoundError, FirmwareOutdatedError):
    raise, then (SerialError, HardwareOperationError) -> BAD (no error_code), then the
    pre-existing EpromOperationError and (ChipNotImplementedError, ChipNotFoundError) clauses
    unchanged"
  - "_run_step's docstring corrected: states the resolve half sits outside the try (was:
    over-claimed 'wraps the ENTIRE step body')"
  - "_EXPECTED_PRECEDENCE_MATRIX advanced for exactly SerialError/SerialTimeoutError/
    HardwareOperationError; _INTENDED_PRECEDENCE_DELTA names the same three"
  - "LEG-11's four behavioural proofs: test_serial_timeout_degrades_one_step,
    test_hardware_error_degrades_one_step, test_run_fatal_escapes (parametrised x2),
    test_assertion_error_propagates"
affects: [133-03, 133-04, 133-05, 133-06, 133-07]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Re-raise-fatal-classes-first, then degrade-transport-classes ordering inside an except
      chain where both live in the same base-class hierarchy (D-08 mechanism)"

key-files:
  created: []
  modified:
    - firestarter_app/firestarter/chip_test.py
    - firestarter_app/tests/test_chip_test_sdp_leg.py

key-decisions:
  - "Measured delta was exactly the three classes the plan predicted (SerialError,
    SerialTimeoutError, HardwareOperationError) -- no reconciliation needed, matrix and delta
    updated to the measured values verbatim"
  - "Mutation proofs used a throwaway 4th SerialError subclass (for the standing-invariant test)
    and a temporarily-planted `except Exception` clause (for the no-broad-catch test), both
    reverted byte-identical to the pre-mutation source before committing"

requirements-completed: []
# LEG-11 evidence (implementation + 4 behavioural proofs) landed here, but this plan does NOT
# tick LEG-11 -- shared with 133-01 (done) and 133-05 (later); only 133-07 is permitted to mark
# any LEG requirement Complete, per this plan's own <requirement_fence>. .planning/REQUIREMENTS.md
# was not touched -- verified below.

coverage:
  - id: D1
    description: "_run_step's except chain widened per D-08: (ProgrammerNotFoundError,
      FirmwareOutdatedError) re-raise first, then (SerialError, HardwareOperationError) degrade
      to BAD without error_code, in the proven order ahead of the pre-existing clauses"
    requirement: "LEG-11"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_chip_test.py (full module, regression)"
        status: pass
      - kind: other
        ref: "AST inspection of _run_step's ExceptHandler order and bodies (see Verification Details)"
        status: pass
    human_judgment: false
  - id: D2
    description: "_run_step's docstring corrected to state the resolve half sits outside the try
      (was: over-claimed 'wraps the ENTIRE step body')"
    verification:
      - kind: other
        ref: "python3 -c AST get_docstring check: 'ENTIRE step body' absent, 'outside' present"
        status: pass
    human_judgment: false
  - id: D3
    description: "Precedence matrix advanced by exactly the three measured rows (SerialError,
      SerialTimeoutError, HardwareOperationError), named in _INTENDED_PRECEDENCE_DELTA in the
      same commit; frozen before-image untouched"
    requirement: "LEG-11"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_chip_test_sdp_leg.py#test_exception_precedence_matrix"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_chip_test_sdp_leg.py#test_precedence_matrix_delta_is_exactly_intended"
        status: pass
    human_judgment: false
  - id: D4
    description: "LEG-11's four behavioural proofs: SerialTimeoutError and HardwareOperationError
      each degrade one step (later step still runs OK); ProgrammerNotFoundError/
      FirmwareOutdatedError escape by object identity with a standing SerialError subclass-census
      invariant; the deliberate AssertionError still escapes (no broad catch introduced)"
    requirement: "LEG-11"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_chip_test_sdp_leg.py#test_serial_timeout_degrades_one_step"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_chip_test_sdp_leg.py#test_hardware_error_degrades_one_step"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_chip_test_sdp_leg.py#test_run_fatal_escapes"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_chip_test_sdp_leg.py#test_assertion_error_propagates"
        status: pass
    human_judgment: false

# Metrics
duration: ~50min
completed: 2026-08-04
status: complete
---

# Phase 133 Plan 02: SDP Leg Mechanism -- Widened Exception Handling Summary

**`_run_step` now re-raises `ProgrammerNotFoundError`/`FirmwareOutdatedError` before degrading
`SerialError`/`HardwareOperationError` to a recorded BAD step, closing LEG-11's real gap
(`HardwareOperationError` is a sibling of `Exception`, not an `EpromOperationError` subclass) while
proving, against 133-01's frozen before-image, that exactly three of the nine precedence rows
moved and the other six -- including the shipped ops' entire behaviour -- did not.**

## Performance

- **Duration:** ~50 min
- **Completed:** 2026-08-04T08:35:00Z (approx)
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments

- Added two new `except` clauses to `_run_step`, in the load-bearing order D-08 requires: first
  `except (ProgrammerNotFoundError, FirmwareOutdatedError): raise` (bare re-raise, unchanged),
  then `except (SerialError, HardwareOperationError) as exc:` returning
  `StepResult(verdict=BAD, reason=str(exc), run_count=1)` with `error_code` deliberately omitted
  (neither class carries that attribute). Both new clauses sit above the pre-existing
  `except EpromOperationError` and `except (ChipNotImplementedError, ChipNotFoundError)` clauses,
  which are byte-unchanged.
- Corrected `_run_step`'s docstring: it claimed to wrap "the ENTIRE step body (resolve +
  dispatch)"; measured, the resolve call (`_resolve_or_none`) sits outside the `try` and is
  covered only by its own narrower two-class handler. The docstring now states this and names
  the residual (an exception class other than those two raised during resolution still
  propagates unchanged) as research assumption A2's current mitigation.
- Advanced `_EXPECTED_PRECEDENCE_MATRIX` for exactly the three rows measured to change --
  `SerialError`, `SerialTimeoutError`, `HardwareOperationError`, all moving from "escapes" to
  `(None, "BAD", None)` -- and named the same three in `_INTENDED_PRECEDENCE_DELTA` in the same
  commit. `_PRE_EDIT_PRECEDENCE_MATRIX` (133-01's frozen before-image) is byte-unchanged.
- Added LEG-11's four behavioural proofs to `tests/test_chip_test_sdp_leg.py`
  (`test_serial_timeout_degrades_one_step`, `test_hardware_error_degrades_one_step`,
  `test_run_fatal_escapes` (parametrised over both run-fatal classes, plus the
  `SerialError.__subclasses__()` standing invariant), `test_assertion_error_propagates`), and
  mutation-proved two of the new gate legs (see below).
- Full suite green: 1306 tests, 30 snapshots (unchanged), `ruff check`/`ruff format --check`
  clean on `firestarter/` and `tests/`, mypy count unchanged at 32 errors (watermark 35, checked
  123 source files) via `tools/ci_replica_venv.sh`.

## Task Commits

Each task was committed atomically, in the submodule (`firestarter_app`) on
`gsd/v1.30-sdp-surface-retirement`:

1. **Task 1: Add the two ordered except clauses to `_run_step` and correct its over-claiming
   docstring** -- `9d7c0cc` (feat)
2. **Task 2: Advance the precedence matrix by exactly three named rows and add LEG-11's four
   behavioural proofs** -- `e613864` (test)

**Plan metadata:** this SUMMARY's own commit follows this document (meta repo).

## Files Created/Modified

- `firestarter_app/firestarter/chip_test.py` -- `_run_step` widened to four `except` clauses in
  the proven order; docstring corrected; four new imports added to the existing
  `from firestarter.exceptions import (...)` block (`FirmwareOutdatedError`,
  `HardwareOperationError`, `ProgrammerNotFoundError`, `SerialError`), kept alphabetised.
- `firestarter_app/tests/test_chip_test_sdp_leg.py` -- `_EXPECTED_PRECEDENCE_MATRIX` and
  `_INTENDED_PRECEDENCE_DELTA` advanced; four new behavioural tests added; module docstring's
  `Coverage:`-equivalent taxonomy list extended with the new test names; two new imports added
  (`pytest`, `OP_READ`, `VERDICT_BAD`, `VERDICT_OK`).

## Decisions Made

- **Measured delta matched the predicted set exactly, no reconciliation needed.** Running
  `_derive_precedence_row` against the edited engine for all nine classes produced exactly
  `{SerialError, SerialTimeoutError, HardwareOperationError}` as the changed set --
  `ProgrammerNotFoundError`/`FirmwareOutdatedError` still escape (re-raised), and
  `EpromOperationError`/`ChipNotImplementedError`/`ChipNotFoundError`/`AssertionError` rows are
  untouched. The plan's own escalation clause ("a delta containing
  ProgrammerNotFoundError/FirmwareOutdatedError/EpromOperationError/ChipNotImplementedError/
  ChipNotFoundError/AssertionError means the clause order is wrong") was not triggered.
- **Mutation proofs used throwaway/temporary source edits, reverted byte-identical before
  committing.** For `test_run_fatal_escapes`'s standing invariant, a throwaway fourth
  `SerialError` subclass was added to the test module and the test observed to FAIL (see
  verbatim message below); reverted via `diff` confirming byte-identity, then re-ran green. For
  `test_assertion_error_propagates`, a temporary `except Exception` clause was planted in
  `_run_step` in `firestarter/chip_test.py`, observed to make the test FAIL (`DID NOT RAISE
  AssertionError`), reverted via `diff` confirming byte-identity, then re-ran the full precision
  suite green.

## Deviations from Plan

None. All acceptance criteria were met on first implementation; both tasks' AST/behavioural
checks passed exactly as specified, and the measured precedence delta matched the plan's
predicted three-row set without requiring escalation.

## Issues Encountered

None.

## Mutation Proofs (verbatim observed failure messages, per plan_specific_warnings)

**1. `test_run_fatal_escapes`'s standing invariant, with a throwaway fourth `SerialError`
subclass added to the test module (`class _ThrowawayFourthSerialSubclass(SerialError): ...`),
placed immediately above the `@pytest.mark.parametrize` decorator:**

```
E       AssertionError: SerialError gained or lost a subclass since D-08 was measured -- _run_step's (ProgrammerNotFoundError, FirmwareOutdatedError) re-raise clause is only complete against the THREE-class census D-08 names; a new subclass here would silently fall through to the (SerialError, HardwareOperationError) degrade clause instead of escaping, turning a no-board/old-firmware run into a false BAD-step report (133-CONTEXT.md D-08).
E       assert {<class 'fire...ialSubclass'>} == {<class 'fire...imeoutError'>}
E
E         Extra items in the left set:
E         <class 'tests.test_chip_test_sdp_leg._ThrowawayFourthSerialSubclass'>
E         Use -v to get more diff
```

Reverted (`diff` against the pre-mutation copy showed zero difference); `pytest -k
run_fatal_escapes` passed again (2 passed).

**2. `test_assertion_error_propagates`, with a temporary `except Exception as exc:` clause
planted in `_run_step`'s chain (after the existing `(ChipNotImplementedError,
ChipNotFoundError)` clause), returning a BAD `StepResult` instead of letting the AssertionError
escape:**

```
>       with pytest.raises(AssertionError) as excinfo:
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       Failed: DID NOT RAISE AssertionError
```

Reverted (`diff` against the pre-mutation copy showed zero difference); `pytest -k
assertion_error_propagates` passed again, and the full suite (`pytest tests/ -q`) re-ran green
(1306 passed, 30 snapshots).

## Measured Values (quoted verbatim per plan `<output>` requirement)

**Post-edit nine-row precedence matrix** (`_EXPECTED_PRECEDENCE_MATRIX`, measured live against
the edited `_run_step`):

```python
{
    "SerialError": (None, "BAD", None),                    # CHANGED (was escaping)
    "SerialTimeoutError": (None, "BAD", None),              # CHANGED (was escaping)
    "ProgrammerNotFoundError": ("ProgrammerNotFoundError", None, None),   # unchanged
    "FirmwareOutdatedError": ("FirmwareOutdatedError", None, None),      # unchanged
    "EpromOperationError": (None, "BAD", 0x42),              # unchanged
    "ChipNotImplementedError": (None, "BAD", None),          # unchanged
    "ChipNotFoundError": (None, "SKIPPED", None),            # unchanged
    "HardwareOperationError": (None, "BAD", None),           # CHANGED (was escaping)
    "AssertionError": ("AssertionError", None, None),        # unchanged
}
```

**`_INTENDED_PRECEDENCE_DELTA`:** `frozenset({"SerialError", "SerialTimeoutError",
"HardwareOperationError"})` -- exactly three names, all among the set the plan named as expected.

**AST-verified `_run_step` handler order:**
`[(ProgrammerNotFoundError, FirmwareOutdatedError), (SerialError, HardwareOperationError),
EpromOperationError, (ChipNotImplementedError, ChipNotFoundError)]` -- exactly the order D-08
requires.

**Suite state at finish:** `pytest tests/ -q` -- 1306 passed, 30 snapshots passed (unchanged from
133-01's baseline, no new snapshot). `ruff check firestarter/ tests/` and
`ruff format --check firestarter/ tests/` both exit 0. `tools/ci_replica_venv.sh`'s mypy leg:
`checked 123 source files`, `mypy errors: 32 (watermark: 35)` -- unchanged from 133-01's baseline;
watermark not moved.

## User Setup Required

None -- no external service configuration required.

## Next Phase Readiness

- `_run_step`'s four-clause chain and the advanced precedence matrix are the foundation plans
  133-03/133-04 build on (the `_dispatch_sdp` arm and the cleanup registry both call through
  `_run_step`'s existing dispatch path, now widened).
- `.planning/REQUIREMENTS.md` was not touched by this plan (verified: `git diff --name-only HEAD
  -- .planning/REQUIREMENTS.md` in the meta repo shows no change). LEG-11 remains open pending
  133-05's second, independent proof (the build-time no-broad-except gate) before 133-07 ticks it.
- No blockers.

---
*Phase: 133-sdp-leg-mechanism*
*Completed: 2026-08-04*

## Self-Check: PASSED

- FOUND: `firestarter_app/firestarter/chip_test.py`
- FOUND: `firestarter_app/tests/test_chip_test_sdp_leg.py`
- FOUND: `.planning/phases/133-sdp-leg-mechanism/133-02-SUMMARY.md`
- FOUND commit: `9d7c0cc` (submodule `firestarter_app`)
- FOUND commit: `e613864` (submodule `firestarter_app`)
- FOUND commit: `1da121c` (meta repo)
