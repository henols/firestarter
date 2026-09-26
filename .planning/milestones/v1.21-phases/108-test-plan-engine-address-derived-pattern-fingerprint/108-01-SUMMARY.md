---
phase: 108-test-plan-engine-address-derived-pattern-fingerprint
plan: 01
subsystem: api
tags: [python, exceptions, error-handling, firestarter_app]

# Dependency graph
requires: []
provides:
  - "EpromOperationError.error_code optional attribute (int | None)"
  - "_raise_for_error_response chokepoint threading firmware response.id onto error_code"
  - "test_error_code_seam.py bench-free regression suite"
affects: [108-02, 108-03, 108-04, 110-diagnostic-report]

# Tech tracking
tech-stack:
  added: []
  patterns: ["optional backward-compatible exception kwarg (PEP-604 union)"]

key-files:
  created:
    - firestarter_app/tests/test_error_code_seam.py
  modified:
    - firestarter_app/firestarter/exceptions.py
    - firestarter_app/firestarter/eprom_operations.py

key-decisions:
  - "Added error_code=response.id to the ProtocolNotImplementedError branch too (discretionary symmetry option from the plan), not just the generic EpromOperationError branch"

patterns-established:
  - "Optional exception metadata kwarg with a safe default (error_code: int | None = None) so all pre-existing raise sites keep working unmodified"

requirements-completed: [RPT-03]

coverage:
  - id: D1
    description: "EpromOperationError(msg, error_code=0xA4) stores 0xA4 on .error_code; default is None for existing call sites"
    requirement: "RPT-03"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_error_code_seam.py#test_eprom_operation_error_stores_code"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_error_code_seam.py#test_eprom_operation_error_default_none"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_error_code_seam.py#test_subclass_inherits_error_code"
        status: pass
    human_judgment: false
  - id: D2
    description: "_raise_for_error_response threads response.id onto EpromOperationError.error_code; ProtocolNotImplementedError dispatch fork preserved"
    requirement: "RPT-03"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_error_code_seam.py#test_raise_for_error_carries_id"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_error_code_seam.py#test_protocol_not_impl_fork_preserved"
        status: pass
      - kind: integration
        ref: "firestarter_app/tests/test_consistency_check.py (9 tests, unchanged, all pass)"
        status: pass
    human_judgment: false

# Metrics
duration: 20min
completed: 2026-07-02
status: complete
---

# Phase 108 Plan 01: error_code Seam Summary

**EpromOperationError gains a backward-compatible `error_code` attribute carrying the firmware `response.id` byte, threaded through the single `_raise_for_error_response` chokepoint.**

## Performance

- **Duration:** 20 min
- **Started:** 2026-07-02T17:41:11Z
- **Completed:** 2026-07-02T17:44:54Z
- **Tasks:** 3 completed
- **Files modified:** 3 (2 modified, 1 created) — all inside `firestarter_app/` submodule

## Accomplishments
- `EpromOperationError.__init__` now accepts an optional `error_code: int | None = None` kwarg, stored as `self.error_code`, fully backward-compatible with every existing bare `raise EpromOperationError("...")` call site
- `_raise_for_error_response` (the single chokepoint dispatching firmware ERROR responses) now passes `error_code=response.id` on both the generic `EpromOperationError` path and the `ProtocolNotImplementedError` fork
- New dedicated test file `firestarter_app/tests/test_error_code_seam.py` (5 tests, bench-free) proves the kwarg, its default, subclass inheritance, and the chokepoint pass-through for both dispatch branches

## Task Commits

Each task was committed atomically inside the `firestarter_app` submodule on branch `v1.21-community-chip-validation-command`:

1. **Task 1: Add optional error_code kwarg to EpromOperationError** - `a257ab7` (feat)
2. **Task 2: Thread response.id through the _raise_for_error_response chokepoint** - `09e8a64` (feat)
3. **Task 3: Write the error_code seam unit test file** - `6216834` (test)

**Plan metadata:** committed in the meta repo (this SUMMARY + STATE.md/ROADMAP.md commit follows)

_Note: tasks were `tdd="true"` but tests were authored as one dedicated file (Task 3) covering the behavior introduced in Tasks 1-2, per the plan's task ordering (foundational kwarg first, chokepoint second, dedicated test file third) — all three tasks' acceptance criteria were independently verified against the final test file before committing._

## Files Created/Modified
- `firestarter_app/firestarter/exceptions.py` - `EpromOperationError.__init__(self, *args: object, error_code: int | None = None) -> None`; subclasses `ProtocolNotImplementedError`/`ChipNotImplementedError` inherit unchanged
- `firestarter_app/firestarter/eprom_operations.py` - `_raise_for_error_response` (line ~84-86) now passes `error_code=response.id` to both raised exception types
- `firestarter_app/tests/test_error_code_seam.py` - new bench-free test file (5 tests)

## Decisions Made
- Added `error_code=response.id` to the `ProtocolNotImplementedError` branch as well as the generic `EpromOperationError` branch, per the plan's discretionary symmetry option — the id is always `MSG_ERR_PROTOCOL_NOT_IMPLEMENTED` (0xBB) there, so this costs nothing and gives every `EpromOperationError`-family exception a consistent `.error_code`.

## Deviations from Plan

None - plan executed exactly as written. One incidental auto-format: `ruff format` reformatted the new test file's multi-line `Response(...)` call onto separate lines (cosmetic, no semantic change) — applied before the Task 3 commit, not treated as a deviation requiring separate documentation.

## Issues Encountered
None.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- The `error_code` seam is now available for Plans 108-02/03/04 (`chip_test.py`, `derive_plan()`, `run_plan()`, pattern generator, fingerprint classifier) and later Phase 110's diagnostic report, which all depend on capturing the exact firmware message-id byte per step.
- Full `firestarter_app` test suite run: all tests pass except the pre-existing `tests/test_audit_coverage_matrix.py::TestAuditCoverageMatrix::test_golden_file_matches` golden-fixture drift, confirmed via `git stash` to predate this plan's changes (out of scope per the executor's scope boundary; already logged as a deferred item at prior milestone closes).
- No blockers for Plan 108-02.

---
*Phase: 108-test-plan-engine-address-derived-pattern-fingerprint*
*Completed: 2026-07-02*

## Self-Check: PASSED

All created files and commit hashes verified present:
- `firestarter_app/tests/test_error_code_seam.py` — FOUND
- `.planning/phases/108-test-plan-engine-address-derived-pattern-fingerprint/108-01-SUMMARY.md` — FOUND
- `a257ab7` (firestarter_app) — FOUND
- `09e8a64` (firestarter_app) — FOUND
- `6216834` (firestarter_app) — FOUND
- `5ed62e6` (meta repo) — FOUND
