---
phase: 133-sdp-leg-mechanism
plan: 04
subsystem: testing
tags: [chip_test, cleanup-registry, finally, sdp, pytest, ruff, mypy, ast]

# Dependency graph
requires:
  - phase: 133-sdp-leg-mechanism (plan 03)
    provides: "OP_SDP_LOCK/OP_SDP_UNLOCK op strings, the _SDP_OPS
      dispatch allow-list, _dispatch_sdp wired as arm 5 of
      _dispatch_step, and the _DESTRUCTIVE_OPS asymmetry (OP_SDP_LOCK
      in, OP_SDP_UNLOCK out) that a real sdp_lock step now dispatches
      through, giving this plan's cleanup registry something real to
      register a cleanup from"
provides:
  - "A generic `cleanup: list[Callable[[], None]] = []` registry local
    to `run_plan`, populated only when an `OP_SDP_LOCK` step's verdict
    is OK, drained in a bare `try/finally` (no except clause of any
    width) wrapped around the whole step loop"
  - "`_UNLOCK_CLEANUP_SWALLOWED` -- the module constant naming exactly
    (SerialError, HardwareOperationError, EpromOperationError), the
    per-callable narrow exception set the drain wraps each cleanup in"
  - "The drain's per-callable wrapper: one try/except per registered
    callable, continuing the drain past a caught failure, never
    re-raising from the finally (D-10)"
  - "A mechanically-enforced prohibition: the drain never appends into
    or references the `results` list run_plan returns -- proven by an
    AST-level test over the installed source, not a comment"
  - "LEG-09 criterion 3's two cases proven non-vacuously: gate-closed-
    from-the-start (with an OPEN-gate mirror) and lock-ran-then-gate-
    closes (with the standing _DESTRUCTIVE_OPS invariant, mutation-
    proved)"
affects: [133-05, 133-06, 133-07, 134]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Bare try/finally (zero except clauses) as the one construct that
      reaches KeyboardInterrupt/SystemExit while still letting them
      propagate unchanged -- deliberately not `except BaseException:`,
      which would violate criterion 2 and would be flagged by plan
      133-05's coming deny-rule"
    - "A registered cleanup callable is a nested `def` (not a `lambda:
      _run_step(...)`), so its return value is discarded as a
      STATEMENT rather than an expression -- this is what makes the
      callable's actual inferred return type `None`, matching the
      registry's declared `Callable[[], None]` element type under
      mypy (a lambda returning the StepResult expression is a genuine
      mypy arg-type mismatch, not a style preference -- caught and
      fixed before commit, see Deviations)"
    - "AST-level acceptance criteria that resolve a handler's `except`
      clause back to the real class objects via `eval(ast.unparse(...),
      vars(module))` rather than string-matching source text -- proves
      the handler names exactly the module constant, not merely
      something that looks like it"

key-files:
  created: []
  modified:
    - firestarter_app/firestarter/chip_test.py
    - firestarter_app/tests/test_chip_test_sdp_leg.py

key-decisions:
  - "The registered cleanup is a nested `def _unlock_cleanup() -> None`
    inside the loop body, not a lambda -- discovered via the mypy
    ci-replica venv (not the ambient devcontainer run, which is
    fail-open on this project per prior phases) that a lambda wrapping
    `_run_step(...)` infers a `StepResult` return type, which is a real
    `arg-type` mismatch against `cleanup`'s declared `Callable[[],
    None]` element type -- this raised the watermark-relative count
    from 32 to 33 before the fix, and back to 32 after"
  - "_UNLOCK_CLEANUP_SWALLOWED is declared once as a module constant
    (not typed inline at each call site) so plan 133-06's op-registry
    parity reasoning and this plan's AST test both point at a single
    named fact"
  - "The drain's per-callable wrapper resolves its except-clause target
    via eval(ast.unparse(handler.type), vars(chip_test_mod)) rather than
    string-matching source text -- proves the handler names EXACTLY
    _UNLOCK_CLEANUP_SWALLOWED, not merely a class with a similar name"

requirements-completed: []
# LEG-09 and LEG-10 are BOTH named in this plan's frontmatter because
# this plan delivers all of LEG-10 and completes LEG-09's provability
# (criterion 3's two cases), but per the plan's own requirement_fence
# this plan must NOT tick either box. .planning/REQUIREMENTS.md was not
# touched -- verified below (git diff --name-only in the meta repo shows
# no change). Only plan 133-07 may mark any LEG requirement Complete.

coverage:
  - id: D1
    description: "Cleanup registry (list[Callable[[], None]]), the bare
      try/finally wrapping the whole step loop, the registration site
      (OP_SDP_LOCK success only), and the per-callable narrow-except
      drain wrapper (_UNLOCK_CLEANUP_SWALLOWED) added to run_plan"
    requirement: "LEG-10"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_chip_test_sdp_leg.py#test_finally_drains_on_exception"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_chip_test_sdp_leg.py#test_keyboard_interrupt_drains_and_propagates"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_chip_test_sdp_leg.py#test_system_exit_drains_and_propagates"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_chip_test_sdp_leg.py#test_empty_registry_noop"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_chip_test_sdp_leg.py#test_drain_continues_after_failure"
        status: pass
    human_judgment: false
  - id: D2
    description: "The drain provably never appends into or references
      the `results` list run_plan returns (AST-level, over the
      installed source); the per-callable handler resolves to exactly
      _UNLOCK_CLEANUP_SWALLOWED with no Raise in its body"
    requirement: "LEG-10"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_chip_test_sdp_leg.py#test_drain_does_not_mutate_results"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_chip_test_sdp_leg.py#test_drain_swallowed_classes_match_constant"
        status: pass
    human_judgment: false
  - id: D3
    description: "LEG-09 criterion 3's two cases proven non-vacuously:
      gate-closed-from-the-start (with the OPEN-gate mirror) and
      lock-ran-then-gate-closes (with the standing _DESTRUCTIVE_OPS
      invariant, mutation-proved to fail if OP_SDP_UNLOCK were ever
      added to _DESTRUCTIVE_OPS)"
    requirement: "LEG-09"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_chip_test_sdp_leg.py#test_gate_closed_from_start"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_chip_test_sdp_leg.py#test_lock_ran_then_gate_closes"
        status: pass
    human_judgment: false

# Metrics
duration: ~80min
completed: 2026-08-04
status: complete
---

# Phase 133 Plan 04: SDP Leg Mechanism -- Cleanup Registry Summary

**A generic cleanup registry drained in a bare `try/finally` around `run_plan`'s step loop -- registering a successful lock's unlock, reaching `KeyboardInterrupt`/`SystemExit` while still letting them propagate by identity, wrapping each cleanup callable in its own narrow except (never masking the in-flight exception), and mechanically proven -- at the AST level, not by comment -- to never touch the `results` list the caller holds.**

## Performance

- **Duration:** ~80 min
- **Completed:** 2026-08-04
- **Tasks:** 3
- **Files modified:** 2

## Accomplishments

- Added a local `cleanup: list[Callable[[], None]] = []` registry to `run_plan`, declared before the `try` alongside `results`/`destructive_gate_closed`; `runs < 2`'s early return stays outside the `try` unchanged (criterion-4 boundary).
- Wrapped the entire step loop in a bare `try/finally` with **zero** `except` clauses -- the one construct that reaches `KeyboardInterrupt`/`SystemExit` while still letting them propagate unchanged (criteria 1+2 simultaneously). `return results` stays inside the `try`, textually unchanged.
- Registration site: after `results.append(result)`, when `step.op == OP_SDP_LOCK and result.verdict == VERDICT_OK`, a nested `_unlock_cleanup()` function (not a lambda -- see Decisions) is appended, routed through `_run_step` (not `_dispatch_sdp` directly) since `run_plan` has no `eprom_data` in scope.
- Added the module constant `_UNLOCK_CLEANUP_SWALLOWED = (SerialError, HardwareOperationError, EpromOperationError)`; the drain wraps each cleanup call in its own `try/except _UNLOCK_CLEANUP_SWALLOWED: continue`, never re-raising from the `finally` (D-10).
- The drain's comment records, in-source: why a generic list beats a hardcoded lock-to-unlock window (D-06); why `contextlib.ExitStack` was rejected on measured evidence (LIFO drain order + re-raise-on-`close()` replaces the in-flight exception); why the run-fatal `SerialError` clause deliberately DOES catch `ProgrammerNotFoundError`/`FirmwareOutdatedError` here (a deliberate asymmetry with `_run_step`'s D-08 re-raise clause on the step path); and the D-10/D-16 reconciliation (see Residuals below).
- Updated `run_plan`'s docstring with a paragraph mirroring the existing `sampler=None` "proven no-op" wording for the empty-registry case.
- Added nine new tests to `tests/test_chip_test_sdp_leg.py`: five LEG-10 behavioural proofs (escaping exception, `KeyboardInterrupt`, `SystemExit`, empty-registry no-op, drain-continues-after-failure with its unwinding/masking variant), two AST-level structural proofs (`results`-never-referenced, per-callable handler resolves to exactly `_UNLOCK_CLEANUP_SWALLOWED` with no `Raise`), and two LEG-09 criterion-3 proofs (gate-closed-from-start with an OPEN-gate non-vacuity mirror, lock-ran-then-gate-closes with the standing `_DESTRUCTIVE_OPS` invariant).
- Full suite green: **1323 passed** (up from 1314 at 133-03's close; 9 new tests), 30 snapshots unchanged, `ruff check`/`ruff format --check` clean, mypy **32 errors** (watermark 35, checked 123 source files) via `tools/ci_replica_venv.sh` -- **unchanged from 133-03's baseline** after the lambda-vs-nested-def fix (see Deviations), coverage **81.84%** (floor 70%).

## Task Commits

Each task was committed atomically, in the submodule (`firestarter_app`) on `gsd/v1.30-sdp-surface-retirement`:

1. **Task 1: Add the cleanup registry, the try/finally, the registration site, and the per-callable wrapper** -- `35d4571` (feat)
2. **Task 2: Prove the drain -- five LEG-10 legs including KeyboardInterrupt, SystemExit and the empty-registry no-op** -- `23f895c` (test)
3. **Task 3: Prove LEG-09's two criterion-3 cases non-vacuously, and record the D-07/D-16 residuals** -- `5c8fb09` (test)

**Plan metadata:** this SUMMARY's own commit follows this document (meta repo).

## Files Created/Modified

- `firestarter_app/firestarter/chip_test.py` -- `Callable` imported from `collections.abc`; `_UNLOCK_CLEANUP_SWALLOWED` module constant added (immediately before `run_plan`); `run_plan`'s docstring gained the empty-registry no-op paragraph; `run_plan`'s body gained the `cleanup` local, the bare `try/finally` wrapping the loop, the registration site, and the drain. `git diff HEAD~3 -- firestarter/` touches only `firestarter/chip_test.py` -- verified.
- `firestarter_app/tests/test_chip_test_sdp_leg.py` -- nine new tests across two commits (Task 2's five LEG-10 legs plus two AST-level structural tests; Task 3's two LEG-09 criterion-3 tests), `ast`/`Path` imports added, `_DESTRUCTIVE_GATE_REASON`/`VERDICT_SKIPPED` imported, module docstring's Coverage/taxonomy list extended, `_FA_DIR` + `_run_plan_finally_node()` helper added for the AST-level proofs. No hunk inside `_PRE_EDIT_PRECEDENCE_MATRIX`, `_EXPECTED_PRECEDENCE_MATRIX`, `_INTENDED_PRECEDENCE_DELTA`, or `_SHIPPED_OPS_SEQUENCE` -- verified.

## Decisions Made

- **The registered cleanup is a nested `def`, not a `lambda` -- found via the mypy ci-replica venv, not the ambient devcontainer mypy (which is fail-open on this project, per prior-phase record).** The plan's own action text names `lambda: _run_step(...)` as the literal shape to append. Implemented verbatim first; `tools/ci_replica_venv.sh`'s Leg 4 (the only trustworthy local mypy count on this project) then reported **33 errors (watermark 35)** -- one MORE than 133-03's committed baseline of 32 -- with the new error being `firestarter/chip_test.py:902: error: Argument 1 to "append" of "list" has incompatible type "Callable[[], StepResult]"; expected "Callable[[], None]"  [arg-type]`. Root cause: a `lambda: _run_step(...)` infers its return type from the wrapped call's return value (`StepResult`), which does not satisfy the registry's declared `Callable[[], None]` element type -- this is a genuine type mismatch, not a false positive. **Fix:** replaced the lambda with a nested `def _unlock_cleanup() -> None:` whose body calls `_run_step(...)` as a bare statement (the return value is discarded as a statement, not returned as an expression), so the callable's actual inferred return type is `None`. Re-ran `tools/ci_replica_venv.sh`: **32 errors (watermark 35)** -- confirmed, via a temporary `git worktree add` of the pre-133-04 commit and a byte-level diff of the two mypy runs' full error lists, that this is the EXACT same 32-error set as 133-03's baseline (zero new errors, zero resolved errors) -- the fix is a pure type-annotation correction with no behavioural change, confirmed by the unchanged full pytest suite (1323 passed both before and after the fix).
- **`_UNLOCK_CLEANUP_SWALLOWED` placed as a module constant immediately before `run_plan`**, not typed inline at the drain's `except` clause -- gives plan 133-06's parity reasoning and this plan's own AST test (`test_drain_swallowed_classes_match_constant`) a single named fact to point at, matching the module's existing `_DESTRUCTIVE_GATE_REASON`-style constant-before-use placement.
- **The AST-level `results`-never-referenced test and the per-callable-handler test both operate on the INSTALLED source** (`Path(__file__).parent.parent / "firestarter" / "chip_test.py"`, re-parsed with `ast.parse`), not on the already-imported module's bytecode -- consistent with `tools/check_devtest_orchestrator.py`'s own AST-over-source-text idiom, and what makes these tests genuinely independent proofs rather than assertions against Python's own already-compiled representation.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] `lambda: _run_step(...)` registered against `cleanup: list[Callable[[], None]]` is a real mypy `arg-type` mismatch -- caught before commit, fixed to a nested `def`**
- **Found during:** Task 1, `tools/ci_replica_venv.sh`'s Leg 4 (the only trustworthy local mypy count on this project; the ambient devcontainer mypy run is fail-open per prior-phase record and would have silently missed this)
- **Issue:** the plan's literal action text (`cleanup.append(lambda: _run_step(...))`) type-checks the lambda's inferred return type as `Callable[[], StepResult]`, which does not satisfy the registry's own declared element type `Callable[[], None]` -- a genuine correctness gap between the plan's prose and mypy's own rules, not a false positive. This raised the measured mypy count from 133-03's baseline of 32 to 33 (still under the watermark of 35, but a real new error, and not the "zero new mypy errors" the plan's success criteria imply for a "provably byte-identical" change).
- **Fix:** replaced the lambda with a nested `def _unlock_cleanup() -> None:` that calls `_run_step(...)` as a statement (discarding its `StepResult` return value as a statement rather than an expression), matching the annotated element type exactly.
- **Files modified:** `firestarter_app/firestarter/chip_test.py`
- **Verification:** `tools/ci_replica_venv.sh` re-run: 32 errors (watermark 35) -- confirmed via a temporary `git worktree add` of the pre-133-04 commit and a line-by-line diff of the full mypy error lists that this is the identical 32-error set 133-03 shipped with (zero new, zero resolved); full `pytest tests/ -q` unaffected (1323 passed) both before and after the fix; `ruff check`/`ruff format --check` clean.
- **Committed in:** `35d4571` (Task 1 commit) -- the fix landed before the task's own commit, so no separate remediation commit was needed.

---

**Total deviations:** 1 auto-fixed (1 mypy correctness gap in the plan's own literal action text, caught by the mandatory `ci_replica_venv.sh` mypy leg before commit, not by the ambient devcontainer run which would have missed it)
**Impact on plan:** No scope creep and no behavioural change -- the fix is a pure type-annotation-satisfying refactor of how the cleanup callable discards its return value; the full test suite is byte-identical in pass count before and after.

## Issues Encountered

None beyond the mypy correctness gap above (documented as a deviation, caught and fixed within Task 1 before any commit).

## Mutation Proofs (verbatim observed failure messages, per plan_specific_warnings)

Three deliberate mutations were planted, observed to fail, then reverted -- confirmed passing again and the full suite re-run green after each revert.

**1. `results.append(...)` planted unconditionally inside `run_plan`'s `finally` (before the drain's `for cleanup_call in cleanup:` loop, so it fires regardless of registry contents) -- both `test_drain_does_not_mutate_results` AND `test_empty_registry_noop` were required to fail, and did:**

```
FAILED tests/test_chip_test_sdp_leg.py::test_empty_registry_noop - AssertionError: op sequence changed under an empty registry: ['id', 'read', 'blank-check', '__mutation_probe__'] vs frozen baseline ['id', 'read', 'blank-check']
assert ['id', 'read'...tion_probe__'] == ['id', 'read', 'blank-check']

  Left contains one more item: '__mutation_probe__'
  Use -v to get more diff

FAILED tests/test_chip_test_sdp_leg.py::test_drain_does_not_mutate_results - AssertionError: run_plan's cleanup-drain finally references the name 'results' 1 time(s) -- it must reference it ZERO times. results is returned BY REFERENCE, so a finally-time mutation is visible to the caller and feeds seven consumers in cli_handlers.py (run_plan's call site, count_applicable, the generic renderer, the JSON artifact, the markdown table, build_db_diff, sys.exit(max(...))) -- count_applicable would render N greater than M (e.g. '8 of 7 ran').
assert [<ast.Name ob...7f99cab6a7d0>] == []

  Left contains one more item: <ast.Name object at 0x7f99cab6a7d0>
  Use -v to get more diff
2 failed, 24 deselected in 0.07s
```

(An earlier, narrower placement of the same probe -- inside the per-cleanup `for` loop rather than unconditionally in the `finally` -- was tried first and found to leave `test_empty_registry_noop` passing, because an empty registry never enters that loop at all. Corrected to the unconditional placement above, which is what makes both legs fail together as the plan requires.)

Reverted; `pytest tests/test_chip_test_sdp_leg.py -k "drain_does_not_mutate_results or empty_registry_noop" -q` re-passed (2 passed), full suite re-ran green (1323 passed, 30 snapshots).

**2. The bare `finally` temporarily supplemented with `except BaseException: pass` on the enclosing `try` (a swallowing handler) -- `test_keyboard_interrupt_drains_and_propagates` was required to fail, and did:**

```
FAILED tests/test_chip_test_sdp_leg.py::test_keyboard_interrupt_drains_and_propagates - Failed: DID NOT RAISE KeyboardInterrupt
1 failed, 25 deselected in 0.07s
```

Reverted; `pytest tests/test_chip_test_sdp_leg.py -q` re-passed (26 passed), full suite re-ran green.

**3. `OP_SDP_UNLOCK` temporarily added to `_DESTRUCTIVE_OPS` -- `test_lock_ran_then_gate_closes` was required to fail, and did:**

```
FAILED tests/test_chip_test_sdp_leg.py::test_lock_ran_then_gate_closes - AssertionError: OP_SDP_UNLOCK must stay OUT of _DESTRUCTIVE_OPS: were it a member, a closing gate could skip a plan-derived unlock step and ship a locked part to the caller (133-CONTEXT.md D-11, LEG-09)
assert 'sdp-unlock' not in frozenset({'erase', 'sdp-lock', 'sdp-unlock', 'write', 'write-partial'})
1 failed, 25 deselected in 0.06s
```

Reverted (verified `git diff --stat firestarter/chip_test.py` empty afterward); `pytest tests/test_chip_test_sdp_leg.py -q` re-passed (26 passed), full suite re-ran green (1323 passed, 30 snapshots), `ruff check`/`ruff format --check` clean.

## Residuals and Qualifiers (verbatim, for plan 133-07's record)

**D-11 qualifier.** In Phase 133 the unlock reaches the chip **only** via the registry drain; it is not a derived plan step, and `OP_SDP_UNLOCK`'s absence from `_DESTRUCTIVE_OPS` is **forward-protection for Phase 134**, where the unlock becomes step 4 of the derived leg. The absence does **not** gate a live 133 path -- there is no plan-derived SDP step in this phase for it to gate.

**D-07 residual.** After a Ctrl-C mid-leg the chip has an unlock **attempted** (the drain still runs it), but the user sees **no `dev test` report at all** -- the production caller does `results = run_plan(...)` (`cli_handlers.py:2161`), so a propagating exception means the assignment never completes and there is nothing to render. The report is honestly forfeited.

**D-16 residual.** A **failed** unlock is proven by **test-observability only** in Phase 133 (through the operator double's call assertions) and is **not user-visible** until Phase 134's `HELD`/`NOT-RUN` field (LEG-12). `chip_test.py` was deliberately not given a logger.

**The D-10 / D-16 reconciliation, as implemented.** No in-module recorder was created. `chip_test.py` has no logger and no `logging` import at all (verified: `test_drain_swallowed_classes_match_constant`'s sibling assertion in `test_chip_test_sdp_leg.py` and the module's own docstring both hold this invariant); `exc.add_note()` is 3.11+ against this module's `>=3.9` floor; and the drain must not touch `results` (the seven-consumer detonation risk). A local failure list read by nobody would be a dead surface of exactly the kind this module's history warns about (`_MULTI_RUN_OPS` once shipped with zero references tree-wide). Instead, the attempt and its outcome are observable only through the operator double in this phase.

**The Evidence Ceiling split.** This plan proves the *mechanism* cannot strand a chip or lose a report. It proves **nothing** about SDP behaviour on silicon: a locked die is unrepresentable in either repo's stubs, protection state is unreadable on this family, `0x0D` stays `UNVERIFIED`, and no AT28C part has ever been in operator inventory. Any artifact claiming more is the v1.22 C-5 overclaim class.

## Measured Values (quoted verbatim per plan `<output>` requirement)

**AST re-check, `run_plan`'s bare try/finally:** exactly one `ast.Try` with `handlers == []` and non-empty `finalbody`; the `for step in plan.steps` loop and `return results` are both inside its `body`; the `runs < 2` `If` (and the `results`/`destructive_gate_closed`/`cleanup` assignments) all precede it in `run_plan`'s statement list.

**AST re-check, `results`-never-referenced:** `ast.walk` over the empty-handler `Try`'s `finalbody` finds zero `ast.Name` nodes with `id == "results"` and zero `results.append(...)` `Call` nodes.

**AST re-check, per-callable handler:** exactly one nested `ast.Try` inside the drain's `for` loop, with exactly one `ast.ExceptHandler` whose `type`, resolved via `eval(ast.unparse(handler.type), vars(chip_test_mod))`, equals `chip_test_mod._UNLOCK_CLEANUP_SWALLOWED` (`(SerialError, HardwareOperationError, EpromOperationError)`) exactly, and whose body contains zero `ast.Raise` nodes.

**Broad-handler census (unchanged from 133-01):** exactly one handler in `chip_test.py` whose `type` is `None`/`Exception`/`BaseException`, enclosed by `_sample`. `chip_test.py` imports zero `logging` names.

**`git diff HEAD~3 -- firestarter/`:** touches only `firestarter/chip_test.py`. `git diff --stat HEAD -- firestarter/cli_handlers.py firestarter/diagnostic_report.py firestarter/eprom_operations.py firestarter/sdp_honesty.py`: no output.

**Suite state at finish:** `pytest tests/ -q` -- **1323 passed** (133-03's baseline was 1314; +9 new tests), 30 snapshots passed (unchanged). `ruff check firestarter/ tests/` and `ruff format --check firestarter/ tests/` both exit 0. `tools/ci_replica_venv.sh`'s full 5-leg run: Leg 1 (venv reuse) exit 0, Leg 2 (numpy absent) exit 0, Leg 3 (ruff) exit 0, Leg 4 (mypy watermark) `Found 32 errors in 12 files (checked 123 source files)` -- `mypy errors: 32 (watermark: 35)`, **identical to 133-03's baseline, unchanged, watermark not moved**, Leg 5 (`pytest --cov --cov-fail-under=70`) exit 0, `Required test coverage of 70% reached. Total coverage: 81.84%`. `CI-REPLICA: PASS`.

## User Setup Required

None -- no external service configuration required.

## Next Phase Readiness

- The cleanup registry, the bare try/finally, and `_UNLOCK_CLEANUP_SWALLOWED` are the mechanism Phase 134's four-step leg depends on (ROADMAP Phase 134's "Depends on" line names the cleanup registry verbatim) -- a real derived `sdp_lock` step in 134 will register a real unlock through the exact same drain proven here.
- `.planning/REQUIREMENTS.md` was not touched by this plan (verified: `git diff --name-only HEAD -- .planning/REQUIREMENTS.md` in the meta repo shows no change). Both LEG-09 and LEG-10 remain open pending plan 133-07's centralized tick against all four LEG requirements at once.
- No blockers.

---
*Phase: 133-sdp-leg-mechanism*
*Completed: 2026-08-04*

## Self-Check: PASSED

- FOUND: `firestarter_app/firestarter/chip_test.py`
- FOUND: `firestarter_app/tests/test_chip_test_sdp_leg.py`
- FOUND: `.planning/phases/133-sdp-leg-mechanism/133-04-SUMMARY.md`
- FOUND commit: `35d4571` (submodule `firestarter_app`)
- FOUND commit: `23f895c` (submodule `firestarter_app`)
- FOUND commit: `5c8fb09` (submodule `firestarter_app`)
