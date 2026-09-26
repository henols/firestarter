---
phase: 133-sdp-leg-mechanism
plan: 01
subsystem: testing
tags: [pytest, mypy, chip_test, exception-handling, ci-parity]

# Dependency graph
requires:
  - phase: 132-retire-dev-sdp-discharge-the-mypy-debt
    provides: mypy watermark at 32 (35), checked 122 source files; ci_replica_venv.sh numpy-free venv
provides:
  - "tests/test_chip_test_sdp_leg.py: the SDP-extended operator-double harness (_OPERATOR_METHODS +
    sdp_lock/sdp_unlock) later plans 133-02..133-07 build on"
  - "_SHIPPED_OPS_SEQUENCE: the frozen shipped-ops-behaviour before-image (criterion 4, D-13a)"
  - "_PRE_EDIT_PRECEDENCE_MATRIX / _EXPECTED_PRECEDENCE_MATRIX / _INTENDED_PRECEDENCE_DELTA: the
    three-constant exception-precedence delta-gate mechanism (criterion 4, D-08)"
  - "133-BASELINE.md: the pre-edit CI-parity recipe result with a real (non-devcontainer-truncated)
    mypy count"
affects: [133-02, 133-03, 133-04, 133-05, 133-06, 133-07]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Three-constant frozen-before-image / current-expectation / named-delta triple for proving a
      behavioural change is fully accounted for (D-08 mechanism)"
    - "Non-vacuity leg sharing the real comparison helper with the gate it proves (not a
      re-implementation)"

key-files:
  created:
    - firestarter_app/tests/test_chip_test_sdp_leg.py
    - .planning/phases/133-sdp-leg-mechanism/133-BASELINE.md
  modified: []

key-decisions:
  - "ChipNotImplementedError measured to land on _run_step's EpromOperationError clause (BAD), not
    the narrower ChipNotImplementedError/ChipNotFoundError clause (SKIPPED) -- confirms 133-CONTEXT.md
    D-08's latent finding by live measurement rather than inheriting it"
  - "Split the plan's two file-touching tasks into two separate atomic commits (b191952, 7f62cf5)
    even though both target the same new file, to preserve one-commit-per-task traceability"
  - "Real mypy count via tools/ci_replica_venv.sh: 32 errors (watermark 35), checked 123 source files
    (122 + 1) -- confirms research assumption A1 (a new plain test module contributes 0 mypy errors)
    by measurement, not by inheriting the unmeasured LOW-confidence claim"

patterns-established:
  - "_derive_precedence_row / _assert_delta_matches_intended: shared helpers so a non-vacuity leg
    exercises the real comparison code path, not a parallel re-implementation"

requirements-completed: []
# LEG-11 evidence foundation only -- this plan does NOT tick LEG-11 (shared with 133-02, 133-05;
# only 133-07 is permitted to mark any LEG requirement Complete, per this plan's own
# <requirement_fence>). .planning/REQUIREMENTS.md was not touched -- verified below.

coverage:
  - id: D1
    description: "SDP-extended operator-double test harness (_OPERATOR_METHODS with sdp_lock/sdp_unlock) in a new tests/test_chip_test_sdp_leg.py"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_chip_test_sdp_leg.py#test_shipped_ops_sequence_unchanged"
        status: pass
    human_judgment: false
  - id: D2
    description: "Frozen shipped-ops-behaviour before-image (_SHIPPED_OPS_SEQUENCE) for M8720, criterion 4's first baseline"
    requirement: "LEG-11"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_chip_test_sdp_leg.py#test_shipped_ops_sequence_unchanged"
        status: pass
    human_judgment: false
  - id: D3
    description: "Three-constant exception-precedence delta-gate mechanism (_PRE_EDIT_PRECEDENCE_MATRIX / _EXPECTED_PRECEDENCE_MATRIX / _INTENDED_PRECEDENCE_DELTA) with a non-vacuity proof"
    requirement: "LEG-11"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_chip_test_sdp_leg.py#test_exception_precedence_matrix"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_chip_test_sdp_leg.py#test_precedence_matrix_delta_is_exactly_intended"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_chip_test_sdp_leg.py#test_precedence_matrix_deriver_is_non_vacuous"
        status: pass
    human_judgment: false
  - id: D4
    description: "133-BASELINE.md: pre-edit CI-parity recipe result, no-board condition, and a real mypy count from the numpy-free replica venv"
    verification:
      - kind: other
        ref: "bash tools/ci_replica_venv.sh (CI-REPLICA: PASS, mypy errors: 32 watermark: 35, checked 123 source files)"
        status: pass
    human_judgment: false

# Metrics
duration: ~45min
completed: 2026-08-04
status: complete
---

# Phase 133 Plan 01: SDP Leg Mechanism -- Pre-Edit Baseline Capture Summary

**Captured the two pre-edit baselines ROADMAP criterion 4 is provable against (shipped-ops
behaviour, exception-clause precedence) in a new `tests/test_chip_test_sdp_leg.py`, plus a real
CI-parity recipe run with a measured (not inherited) mypy count -- zero production files touched.**

## Performance

- **Duration:** ~45 min
- **Completed:** 2026-08-04T07:49:04Z
- **Tasks:** 3
- **Files modified:** 2 (both new)

## Accomplishments

- Copied the operator-double harness (`_REAL_DB`, `_OPERATOR_METHODS`, `_mock_operator`,
  `_plan_with_steps`, `_result`) from `tests/test_chip_test.py`, extending `_OPERATOR_METHODS` with
  `"sdp_lock"`/`"sdp_unlock"` so later plans' dispatch tests do not `AttributeError` against the
  `Mock(spec=[...])` double.
- Froze `_SHIPPED_OPS_SEQUENCE` by actually running `derive_plan("M8720", _REAL_DB)` +
  `run_plan(...)` at this commit: op sequence `["id", "read", "blank-check"]`, per-step
  `(verdict, run_count)` `[("NA", 0), ("OK", 2), ("OK", 1)]`, `len(results) == 3`. Mutation-proven
  (see below).
- Derived the exception-precedence three-constant triple (`_PRE_EDIT_PRECEDENCE_MATRIX` FROZEN,
  `_EXPECTED_PRECEDENCE_MATRIX` current, `_INTENDED_PRECEDENCE_DELTA` empty) by injecting all nine
  exception classes into `check_eprom_blank` through a real `run_plan()` call, never
  hand-transcribed. Confirmed the latent finding live: `ChipNotImplementedError` (a subclass of
  `EpromOperationError`) matches `_run_step`'s **first** except clause today and lands on `BAD`
  (`error_code=None`), never reaching the narrower `ChipNotImplementedError`/`ChipNotFoundError`
  clause's `SKIPPED` mapping.
- Recorded `133-BASELINE.md`: the no-board condition, the four-leg `ci_parity.sh` result (leg 4's
  local exit 2 is the expected numpy-truncation shape), and a **real** mypy count via
  `tools/ci_replica_venv.sh`: **32 errors (watermark 35), checked 123 source files** -- confirming
  research assumption A1 (a new plain test module contributes 0 mypy errors) by measurement rather
  than inheriting the unmeasured LOW-confidence claim.

## Task Commits

Each task was committed atomically, in the correct repo:

1. **Task 1: Create tests/test_chip_test_sdp_leg.py with the operator-double harness and the
   D-13a frozen op-sequence literal** -- `b191952` (test, submodule `firestarter_app`)
2. **Task 2: Add the three-constant exception-precedence triple, derived from the real run_plan,
   with a non-vacuity leg** -- `7f62cf5` (test, submodule `firestarter_app`)
3. **Task 3: Record 133-BASELINE.md -- the pre-edit half of the CI-parity recipe with a REAL mypy
   count** -- `8a7b0190` (docs, meta repo `/workspaces`)

**Deviation from the plan's literal file-per-task split:** the plan lists the same file
(`firestarter_app/tests/test_chip_test_sdp_leg.py`) under both Task 1 and Task 2's `<files>`. To
preserve one-commit-per-task traceability (task_commit_protocol), Task 1's commit contains only the
harness + `_SHIPPED_OPS_SEQUENCE` + `test_shipped_ops_sequence_unchanged`; Task 2's commit adds the
exception-precedence triple + its three tests on top, in a second commit against the same file. Both
commits independently pass `ruff check`/`ruff format --check` and their own targeted `pytest -k`
selector.

**Plan metadata:** this plan's SUMMARY/self-check commit follows this document (meta repo).

## Files Created/Modified

- `firestarter_app/tests/test_chip_test_sdp_leg.py` -- new SDP-leg test module (238 lines): the
  operator-double harness, the shipped-ops before-image, and the exception-precedence delta-gate
  mechanism. Zero production files touched.
- `.planning/phases/133-sdp-leg-mechanism/133-BASELINE.md` -- new: the pre-edit CI-parity recipe
  result and a real mypy count, with the before-images reproduced verbatim outside the test file.

## Decisions Made

- **ChipNotImplementedError precedence, measured not assumed:** confirmed live that it lands on
  `_run_step`'s `EpromOperationError` clause (BAD) rather than the narrower
  `ChipNotImplementedError`/`ChipNotFoundError` clause (SKIPPED), because it is a subclass of
  `EpromOperationError` and Python matches the first satisfying `except` clause. This measurement
  wins over any "should be SKIPPED" reading and is recorded verbatim in both the test module and
  `133-BASELINE.md`.
- **Two commits for the plan's two file-touching tasks:** the plan's Task 1 and Task 2 both list
  `tests/test_chip_test_sdp_leg.py` as their sole file. Rather than folding both into one commit
  (which would blur task-level traceability), Task 1's commit lands the harness + first baseline
  alone (verified green + ruff-clean on its own), then Task 2's commit adds the precedence triple on
  top (also independently verified). Neither task's own acceptance criteria required a specific
  commit boundary, so this is a mechanical interpretation of `task_commit_protocol`'s
  one-commit-per-task rule, not a plan deviation requiring a rule citation.
- **Real mypy count taken from `tools/ci_replica_venv.sh`, not the devcontainer's own mypy run:**
  the devcontainer's ambient numpy install truncates mypy (exit 2) before it can check a single
  file, which is the documented, expected local shape (`ci_parity.sh` leg 4). The replica venv is
  the only local path to a trustworthy count, and it confirmed A1 exactly: 32 errors unchanged from
  the 132-CI-GREEN.md baseline, `checked` moved from 122 to 123 (exactly this plan's one new file).

## Deviations from Plan

None beyond the task-commit-splitting note above (not a Rule 1/2/3/4 deviation -- a mechanical
interpretation of an ambiguous commit boundary, not a fix to broken/missing/architecturally-wrong
code). No auto-fixes were needed: the plan's acceptance criteria were all met on first
implementation, verified live against the real, unmodified engine.

## Issues Encountered

None. `ci_parity.sh` leg 4's local exit 2 is the documented expected shape (ambient numpy PEP-695
stub truncation), not an issue -- discharged by the replica-venv run per the plan's own instructions.

## Mutation Proofs (verbatim observed failure messages)

**1. `_SHIPPED_OPS_SEQUENCE["op_sequence"]` mutated to append a phantom op
(`"extra-mutated-op"`):**

```
E       AssertionError: derive_plan('M8720', _REAL_DB)'s derived op sequence changed: measured ['id', 'read', 'blank-check'], frozen baseline ['id', 'read', 'blank-check', 'extra-mutated-op'] (133-01 before-image, criterion 4)
E       assert ['id', 'read', 'blank-check'] == ['id', 'read'...a-mutated-op']
E
E         Right contains one more item: 'extra-mutated-op'
E         Use -v to get more diff
```

Reverted (`git diff` against the pre-mutation copy showed zero difference); `pytest -k
shipped_ops_sequence_unchanged` passed again.

**2. `_INTENDED_PRECEDENCE_DELTA` mutated to `frozenset({"EpromOperationError"})` with both
matrices left unchanged:**

```
E       AssertionError: computed precedence delta [] != declared _INTENDED_PRECEDENCE_DELTA ['EpromOperationError'] -- a chip_test.py exception-clause behavioural change was made without naming it in _INTENDED_PRECEDENCE_DELTA (133-CONTEXT.md D-08 mechanism)
E       assert set() == frozenset({'E...rationError'})
E
E         Extra items in the right set:
E         'EpromOperationError'
E         Use -v to get more diff
```

Reverted (file byte-identical to the pre-mutation copy via `diff`); `pytest -k
precedence_matrix_delta` passed again.

## Measured Values (quoted verbatim per plan `<output>` requirement)

**`_SHIPPED_OPS_SEQUENCE`:**
```python
{
    "op_sequence": ["id", "read", "blank-check"],
    "verdict_run_count": [("NA", 0), ("OK", 2), ("OK", 1)],
    "len_results": 3,
}
```

**`_PRE_EDIT_PRECEDENCE_MATRIX`** (nine rows, all measured live):
```python
{
    "SerialError": ("SerialError", None, None),
    "SerialTimeoutError": ("SerialTimeoutError", None, None),
    "ProgrammerNotFoundError": ("ProgrammerNotFoundError", None, None),
    "FirmwareOutdatedError": ("FirmwareOutdatedError", None, None),
    "EpromOperationError": (None, "BAD", 0x42),
    "ChipNotImplementedError": (None, "BAD", None),
    "ChipNotFoundError": (None, "SKIPPED", None),
    "HardwareOperationError": ("HardwareOperationError", None, None),
    "AssertionError": ("AssertionError", None, None),
}
```

**Mypy count:** `mypy errors: 32 (watermark: 35)`, `checked 123 source files` (via
`tools/ci_replica_venv.sh`, numpy-free Python 3.11.15 venv).

## User Setup Required

None -- no external service configuration required.

## Next Phase Readiness

- `tests/test_chip_test_sdp_leg.py`'s harness (with `sdp_lock`/`sdp_unlock` already in
  `_OPERATOR_METHODS`) is ready for plan 133-02's `_dispatch_sdp` wiring and D-08's exception-clause
  widening -- 133-02 must add any changed precedence row's exception-class name to
  `_INTENDED_PRECEDENCE_DELTA` in the SAME commit that edits `_EXPECTED_PRECEDENCE_MATRIX`, or
  `test_precedence_matrix_delta_is_exactly_intended` turns RED (proven capable of doing so above).
- `133-BASELINE.md`'s file-count accounting confirms `tests/test_op_registration_parity.py`
  (plan 133-06) is the second and last new source file this phase may add before the
  `MIN_CHECKED_SOURCE_FILES` margin discussion in 133-CONTEXT.md D-15 is exhausted.
- No blockers. `.planning/REQUIREMENTS.md` was not touched (verified: `git diff --name-only HEAD --
  .planning/REQUIREMENTS.md` in the meta repo shows no change from this plan's commit).

---
*Phase: 133-sdp-leg-mechanism*
*Completed: 2026-08-04*

## Self-Check: PASSED

- FOUND: `firestarter_app/tests/test_chip_test_sdp_leg.py`
- FOUND: `.planning/phases/133-sdp-leg-mechanism/133-BASELINE.md`
- FOUND commit: `b191952` (submodule `firestarter_app`)
- FOUND commit: `7f62cf5` (submodule `firestarter_app`)
- FOUND commit: `8a7b019` (meta repo)
