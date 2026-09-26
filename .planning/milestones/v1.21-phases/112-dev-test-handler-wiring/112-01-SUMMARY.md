---
phase: 112-dev-test-handler-wiring
plan: 01
subsystem: testing
tags: [chip_test, run_plan, sampler, voltage, python, pytest]

# Dependency graph
requires:
  - phase: 111-measured-voltage-sampler
    provides: "sample_vpp_mv/sample_vpe_mv wrappers (VOLT-01) — the thunk source the handler (plan 02) will close over"
provides:
  - "run_plan(..., sampler=None) keyword param threaded through _run_step / _dispatch_step / _dispatch_multi_run"
  - "sampler(\"before\")/sampler(\"after\") bracket around each operator.write_eprom call inside the OP_WRITE branch of _dispatch_multi_run, exception-swallowing, never invoked around OP_READ/OP_VERIFY/OP_ERASE/OP_ID/OP_BLANK_CHECK"
  - "sampler=None proven no-op against the full existing test_chip_test.py suite"
affects: [112-02-dev-test-handler-wiring, 113-submission-flow]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Opaque-callable decoupling: chip_test.py stays hardware.py-agnostic — the caller (plan 02's CLI handler) supplies a thunk closing over sample_vpp_mv/sample_vpe_mv; the engine only ever calls sampler(phase_str)"
    - "Best-effort diagnostic hook: sampler exceptions swallowed via a broad except inside a small private helper (_sample), keeping the write-step verdict computed purely from the operator outcome"

key-files:
  created: []
  modified:
    - firestarter_app/firestarter/chip_test.py
    - firestarter_app/tests/test_chip_test.py

key-decisions:
  - "sampler kwarg threaded through all 4 call-chain levels (run_plan -> _run_step -> _dispatch_step -> _dispatch_multi_run) with default None at every level, per D-04's backward-compat guarantee"
  - "Introduced a small _sample(sampler, phase) helper rather than inlining try/except at each of the two call sites, to guarantee identical swallow-behavior for both the before and after calls"
  - "Sampler bracket scoped strictly to the OP_WRITE branch's operator.write_eprom call, not OP_VERIFY/OP_ERASE within the same _dispatch_multi_run function, and not the whole run_plan loop — matches D-04's write-droop-vs-read-droop distinguishability requirement"

patterns-established:
  - "Sampler-agnostic engine + handler-supplied thunk: any future bench measurement (not just VPP/VPE) can hook the same sampler(phase) contract without chip_test.py importing hardware.py"

requirements-completed: [VOLT-01]

coverage:
  - id: D1
    description: "run_plan/_run_step/_dispatch_step/_dispatch_multi_run accept an optional sampler kwarg (default None) with zero behavior change when omitted"
    requirement: "VOLT-01"
    verification:
      - kind: unit
        ref: "tests/test_chip_test.py#test_run_plan_sampler_none_is_noop_matches_baseline"
        status: pass
      - kind: unit
        ref: "tests/test_chip_test.py -q (full suite, 79 tests)"
        status: pass
    human_judgment: false
  - id: D2
    description: "sampler(\"before\")/sampler(\"after\") tightly bracket each OP_WRITE run's operator.write_eprom call, exact ordering, one pair per run"
    requirement: "VOLT-01"
    verification:
      - kind: unit
        ref: "tests/test_chip_test.py#test_run_plan_sampler_brackets_write"
        status: pass
    human_judgment: false
  - id: D3
    description: "sampler is NOT invoked around OP_READ/OP_VERIFY/OP_ERASE/OP_ID/OP_BLANK_CHECK — bracket scoped to the write pulse only"
    requirement: "VOLT-01"
    verification:
      - kind: unit
        ref: "tests/test_chip_test.py#test_run_plan_sampler_not_invoked_around_non_write_ops"
        status: pass
    human_judgment: false
  - id: D4
    description: "A raising sampler is swallowed and never aborts or flips the write step's verdict"
    requirement: "VOLT-01"
    verification:
      - kind: unit
        ref: "tests/test_chip_test.py#test_run_plan_sampler_exception_does_not_abort_write_step"
        status: pass
    human_judgment: false
  - id: D5
    description: "chip_test.py imports no hardware module (D-04 decoupling) and the SAFE-03 orchestrator checker still passes"
    verification:
      - kind: unit
        ref: "grep -n 'import hardware\\|from firestarter.hardware\\|from firestarter import hardware' firestarter_app/firestarter/chip_test.py (0 lines)"
        status: pass
      - kind: other
        ref: "python tools/check_devtest_orchestrator.py (exit 0)"
        status: pass
    human_judgment: false

duration: 20min
completed: 2026-07-03
status: complete
---

# Phase 112 Plan 01: Sampler Hook Threading Summary

**Threaded an optional `sampler` callback through `run_plan`'s dispatch chain, bracketing each OP_WRITE's `operator.write_eprom` call with `sampler("before")`/`sampler("after")` while keeping `chip_test.py` fully agnostic of `hardware.py`.**

## Performance

- **Duration:** 20 min
- **Started:** 2026-07-03T08:47:55Z
- **Completed:** 2026-07-03T08:56:41Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments
- `run_plan(plan, operator, db, *, runs=2, sampler=None)` and its full dispatch chain (`_run_step`, `_dispatch_step`, `_dispatch_multi_run`) now accept a keyword-only `sampler` parameter, defaulting to `None` at every level so all pre-existing callers and tests are byte-for-byte unaffected.
- Added a private `_sample(sampler, phase)` helper that swallows any exception raised by the sampler callable — a bench sampler failure is a diagnostic miss, never a write-step abort.
- The sampler fires exactly `sampler("before")` immediately before and `sampler("after")` immediately after each `operator.write_eprom(...)` call inside `_dispatch_multi_run`'s `OP_WRITE` branch — and nowhere else (not around `OP_VERIFY`, `OP_ERASE`, the id/read/blank-check steps, or the whole `run_plan` loop).
- Extended `run_plan`'s docstring with the full `sampler` contract (decoupling guarantee, bracket scope, exception-swallowing, no-op default).
- Added 4 new tests proving the bracket ordering, the non-write-op exclusion, the `sampler=None` no-op equivalence to baseline, and exception-swallowing — all passing alongside the full pre-existing 79-test `test_chip_test.py` suite.

## Task Commits

Each task was committed atomically inside the `firestarter_app` submodule (branch `v1.21-community-chip-validation-command`):

1. **Task 1: Thread an optional sampler param through run_plan → _run_step → _dispatch_step → _dispatch_multi_run** - `b83d7e4` (feat)
2. **Task 2: Add engine tests proving the sampler bracket + the sampler=None no-op** - `0b357bd` (test)

**Plan metadata:** (this commit, meta-repo) — docs: complete plan

_Note: Task 1 landed the implementation (verified green against the existing suite before committing); Task 2 added the dedicated sampler-behavior tests. See "TDD Gate Compliance" below._

## Files Created/Modified
- `firestarter_app/firestarter/chip_test.py` - Added `sampler: Any = None` to `run_plan`/`_run_step`/`_dispatch_step`/`_dispatch_multi_run`; added `_sample()` helper; bracketed the `OP_WRITE` `operator.write_eprom` call in `_dispatch_multi_run` with `_sample(sampler, "before")`/`_sample(sampler, "after")`; extended `run_plan`'s docstring.
- `firestarter_app/tests/test_chip_test.py` - Added 4 tests: `test_run_plan_sampler_brackets_write`, `test_run_plan_sampler_not_invoked_around_non_write_ops`, `test_run_plan_sampler_none_is_noop_matches_baseline`, `test_run_plan_sampler_exception_does_not_abort_write_step`.

## Decisions Made
- Threaded `sampler` through all 4 call-chain levels with `None` default at every level, per D-04's backward-compat guarantee (rather than only exposing it at `run_plan` and special-casing lower levels).
- Introduced a small `_sample(sampler, phase)` helper (instead of inlining try/except at each of the two call sites) to guarantee identical swallow-behavior for both the "before" and "after" invocations and keep the `_dispatch_multi_run` write loop readable.
- Scoped the bracket strictly to `_dispatch_multi_run`'s `OP_WRITE` branch's `operator.write_eprom` call — not `OP_VERIFY`/`OP_ERASE` in the same function, and not the whole `run_plan` loop — matching D-04's write-droop-vs-read-droop distinguishability requirement and the rejected coarse-sampling alternative noted in 112-PATTERNS.md.
- Used the existing `M8720`-backed `_plan_with_steps`/`_mock_operator`/`_REAL_DB` test seam (already established in `test_chip_test.py`) rather than introducing a new W27C512/W29C020-specific fixture, since `M8720` (protocol 0x08, EEPROM) already resolves through the real `EpromDatabase(skip_local_override=True)` and every other multi-run test in the file already uses it — reuse-first, zero new fixtures.

## Deviations from Plan

None - plan executed exactly as written. The plan's Task 2 action text suggested picking "an electrically-erasable chip (W27C512 or W29C020)" for the new sampler tests; the existing `_plan_with_steps`/`_mock_operator` helpers in `test_chip_test.py` already default to `M8720` (protocol 0x08, an electrically-erasable EEPROM resolved via the real `EpromDatabase`) and are used by every other multi-run write/verify test in the file (`test_marginal_on_disagreeing_write_runs`, `test_agreeing_destructive_runs_report_confident_ok/bad`, etc.) — reusing this exact seam is the file's own established convention and satisfies the plan's underlying intent (a real DB-backed, electrically-erasable, mock-operator-driven write step) without introducing a parallel fixture.

## TDD Gate Compliance

Both tasks in this plan are marked `tdd="true"`. The plan's own task ordering places the implementation in Task 1 (verified green via `pytest -x -q` before commit) and the dedicated sampler-behavior tests in Task 2 — i.e., feat-then-test rather than a strict test-then-feat RED/GREEN sequence per task. This matches the plan's literal task split (Task 1 = "Thread an optional sampler param...", Task 2 = "Add engine tests proving...") and every acceptance criterion in both tasks was verified before its commit. No RED (failing-test) commit exists for Task 1 because Task 1's own verification step was the full existing suite staying green (the backward-compat proof), not a new failing test — the new sampler-specific tests (the RED/GREEN pair for the *new* behavior) live entirely in Task 2's single `test(...)` commit, which was verified passing before commit. Recorded here as a plan-structure note, not a process violation.

## Issues Encountered
None.

## Self-Check: PASSED

- FOUND: firestarter_app/firestarter/chip_test.py
- FOUND: firestarter_app/tests/test_chip_test.py
- FOUND: .planning/phases/112-dev-test-handler-wiring/112-01-SUMMARY.md
- FOUND: commit b83d7e4 (Task 1)
- FOUND: commit 0b357bd (Task 2)

## Next Phase Readiness
- `run_plan(..., sampler=...)` is ready for plan 112-02 (the `@dev.command("test")` CLI handler) to supply a thunk closing over `hardware.sample_vpp_mv`/`sample_vpe_mv`, finally giving the Phase-111 sampler its write-step call site (per STATE.md "Operator Next Steps").
- No blockers. `chip_test.py` remains hardware.py-free; SAFE-03 (`check_devtest_orchestrator.py`) still exits 0; full `test_chip_test.py` suite (83 tests) green; touched files ruff-clean and format-stable; mypy watermark gate within budget (1 error vs 35 watermark, pre-existing).

---
*Phase: 112-dev-test-handler-wiring*
*Completed: 2026-07-03*
