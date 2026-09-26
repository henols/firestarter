---
phase: 132-retire-dev-sdp-discharge-the-mypy-debt
plan: 05
subsystem: testing
tags: [mypy, pytest, typing, test-fixtures, cast, AppContext]

# Dependency graph
requires:
  - phase: 132-04
    provides: "dev sdp deleted, roster of eight, tests/test_sdp_honesty.py needing no local AppContext factory -- mypy count re-measured at 63 (checked 122 source files) as this plan's pre-change baseline"
provides:
  - "tests/conftest.py's make_app_context: a keyword-only, six-parameter, fully-annotated AppContext factory that narrows Mock/real/None doubles to the real field type with an explicit cast at one seam, plus a thin app_context fixture"
  - "tests/test_dev_test_cmd.py and tests/test_write_skip_erase_0x0d.py migrated onto the shared factory with their local **overrides: object copies deleted"
  - "tests/test_write_skip_sdp_unlock.py and tests/test_validate_family_cmd.py retyped as thin delegates onto the shared factory, preserving their real-operator-default and port-clearing non-default behaviours respectively"
  - "measured mypy count 63 -> 38 (-25), matching the four surviving factories' combined error count exactly, with zero relocation to any call site or mock-assertion site (verified by full before/after diff)"
  - "RETIRE-05 marked Complete in REQUIREMENTS.md"
affects: [132-06, 132-09]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Typed test-double factory with in-body deferred firestarter imports (TYPE_CHECKING at module scope, real imports inside the function) -- preserves conftest's existing import-time-binding discipline while making a fully-annotated def type-checked from birth with zero pyproject.toml change"
    - "Cast-at-the-seam, not at the call site or the mock builder -- each of AppContext's six constructor arguments is narrowed with typing.cast exactly once, inside the shared factory, with a docstring stating what the cast does and does not guarantee"
    - "Thin typed delegate forwarding to a shared factory -- a module keeping non-default construction behaviour (a real operator default, an explicit singleton-port clear) retypes its own local factory with the same six keyword-only parameters and forwards everything else unchanged, rather than either duplicating the shared factory's body or losing the behaviour"

key-files:
  created: []
  modified:
    - firestarter_app/tests/conftest.py
    - firestarter_app/tests/test_dev_test_cmd.py
    - firestarter_app/tests/test_write_skip_erase_0x0d.py
    - firestarter_app/tests/test_write_skip_sdp_unlock.py
    - firestarter_app/tests/test_validate_family_cmd.py

key-decisions:
  - "Confirmed mypy special-cases unittest.mock.Mock as assignable to any class in argument/return position -- a minimal repro (`def f(x: Real | Mock | None) -> Real: ...`) type-checks with zero errors. This means the explicit `cast(...)` calls in make_app_context are not strictly load-bearing against a Mock double (mypy would accept it either way); they remain in the code exactly as the plan's D-10 risk-A decision specifies, because they ARE load-bearing against a non-double wrong type (a plain string, the wrong manager class), which the old `**overrides: object` splat also caught but a bare `RealType | Mock | None` annotation alone would not distinguish as clearly to a reader. Recorded here as a measured fact discovered during the planted-error demonstration, not a design change -- the resolved risk in 132-CONTEXT.md D-10/132-05-PLAN.md was not re-litigated."
  - "The planted-error demonstration required two attempts. The first plant (removing the `cast` on `db` while leaving the Mock-typed default in play) produced ZERO new mypy errors, because of the Mock-compatibility fact above. The working plant instead assigned `config_manager` (a real, non-Mock, non-EpromDatabase class) to the `db` field -- this produced the required error at tests/conftest.py:315, confirmed the factory's body is genuinely type-checked, then was reverted."
  - "tests/test_write_skip_erase_0x0d.py's local factory (deleted in Task 2, treated as canonical-shape per the plan) had one detail beyond the plan's own measured-anchors note: its default eprom_operator preset `write_eprom.return_value = True`, which the shared factory's plain `Mock(spec=EpromOperator)` default does not. Verified this is inert: none of the module's six tests inspect write_eprom's return value directly (only `assert_called_once()` and the emitted `operation_flags`), and cli_handlers.py's `write` command does `sys.exit(0 if ok else 1)` where a bare auto-created Mock is truthy by default -- so the substitution changes nothing observable. All six tests pass unchanged."

requirements-completed: [RETIRE-05]

coverage:
  - id: D1
    description: "A typed, keyword-only, six-parameter AppContext factory (make_app_context) plus a thin app_context fixture exist in tests/conftest.py, exported in its module docstring, with firestarter imports deferred into the factory body (TYPE_CHECKING at module scope only)."
    requirement: "RETIRE-05"
    verification:
      - kind: unit
        ref: "python -c \"from tests.conftest import make_app_context as f; a=f(); assert all(getattr(a,n) is not None for n in (...)); print('FACTORY OK')\" -- FACTORY OK"
        status: pass
      - kind: unit
        ref: "python -c \"...Mock(spec=EpromOperator)... assert f(eprom_operator=m).eprom_operator is m; print('IDENTITY OK')\" -- IDENTITY OK"
        status: pass
      - kind: unit
        ref: "python -c \"...f(None)... except TypeError: print('KEYWORD-ONLY OK')\" -- KEYWORD-ONLY OK"
        status: pass
      - kind: unit
        ref: "AST-based import-discipline check over tests/conftest.py's top-level statements -- IMPORT DISCIPLINE OK"
        status: pass
    human_judgment: false
  - id: D2
    description: "The factory's body is genuinely type-checked (not merely assumed): a planted type error inside the factory raises the mypy count and names tests/conftest.py, then is reverted with a clean git status."
    requirement: "RETIRE-05"
    verification:
      - kind: unit
        ref: "bash tools/ci_replica_venv.sh / tools/check_mypy_watermark.py before/after the plant -- 63 -> 64, error line 'tests/conftest.py:315: error: Argument \"db\" to \"AppContext\" has incompatible type \"ConfigManager | Mock\"; expected \"EpromDatabase\"  [arg-type]', then reverted to 63 with `git status --porcelain` showing only the intended diff"
        status: pass
    human_judgment: false
  - id: D3
    description: "tests/test_dev_test_cmd.py and tests/test_write_skip_erase_0x0d.py's local **overrides: object factories are deleted; both import the shared factory via a relative import; no call site was edited; the two mock builders in test_dev_test_cmd.py keep returning Mock with a comment explaining why."
    requirement: "RETIRE-05"
    verification:
      - kind: unit
        ref: "grep -c 'def make_app_context' on both files returns 0; git diff HEAD~1 -- tests/test_dev_test_cmd.py shows only the factory definition and import changed, no call-site line"
        status: pass
      - kind: unit
        ref: "python -m pytest tests/test_dev_test_cmd.py tests/test_write_skip_erase_0x0d.py -q --tb=short -- 26 + 6 = 32 collected, zero failures"
        status: pass
      - kind: unit
        ref: "tools/check_mypy_watermark.py -- 63 -> 51 (-12), matching 6+6"
        status: pass
    human_judgment: false
  - id: D4
    description: "tests/test_write_skip_sdp_unlock.py and tests/test_validate_family_cmd.py's local factories are retyped as thin typed delegates onto the shared factory, preserving the real-EpromOperator default and the port-clearing behaviour respectively; no call site was edited; the measured post-plan count (38) is recorded against the 25-error projection."
    requirement: "RETIRE-05"
    verification:
      - kind: unit
        ref: "AST check: both delegates have no *args/**kwargs and >=6 keyword-only params (test_validate_family_cmd.py's leading `port` param allowed) -- DELEGATE OK, DELEGATE2 OK"
        status: pass
      - kind: unit
        ref: "python -c \"from tests.test_write_skip_sdp_unlock import make_app_context as f; ... isinstance(a.eprom_operator, EpromOperator)\" -- REAL OPERATOR DEFAULT OK"
        status: pass
      - kind: unit
        ref: "python -m pytest tests/test_write_skip_sdp_unlock.py tests/test_validate_family_cmd.py -q -- 7 + 11 = 18 collected, zero failures; full suite python -m pytest tests/ -q -- 1295 passed, 0 failures"
        status: pass
      - kind: unit
        ref: "tools/check_mypy_watermark.py -- 63 -> 38 (-25 total); before/after full mypy diff shows zero relocated errors (the only apparent 'new' lines are the 3 pre-existing test_dev_test_cmd.py attr-defined errors shifted by line-number drift from the earlier deletion)"
        status: pass
      - kind: unit
        ref: "grep -c 'mypy_error_watermark = 35' pyproject.toml -- 1; git diff --stat pyproject.toml firestarter/eprom_operations.py -- empty"
        status: pass
    human_judgment: false

duration: 45min
completed: 2026-08-03
status: complete
---

# Phase 132 Plan 05: Typed AppContext Factory Migration Summary

**One typed, keyword-only, six-parameter `make_app_context` factory (plus a thin `app_context` fixture) landed in `tests/conftest.py`, discharging all 25 of the four surviving `**overrides: object` copies' mock-typing errors -- mypy count measured 63 -> 38, with zero relocation to any call site or mock-assertion site, verified against a full before/after diff.**

## Performance

- **Duration:** ~45 min
- **Started:** 2026-08-03T19:17:12Z (STATE.md's prior session marker, 132-04 complete)
- **Completed:** 2026-08-03T20:00:34Z
- **Tasks:** 3
- **Files modified:** 5 (`conftest.py`, `test_dev_test_cmd.py`, `test_write_skip_erase_0x0d.py`, `test_write_skip_sdp_unlock.py`, `test_validate_family_cmd.py`)

## Accomplishments

- **Task 1 (RETIRE-05, D-10):** Added `make_app_context` to `tests/conftest.py` -- keyword-only, six parameters (`db`, `config_manager`, `eprom_operator`, `hardware_manager`, `firmware_manager`, `eprom_presenter`), each typed `RealType | Mock | None = None`. `from __future__ import annotations` makes the `X | Y` unions valid on the project's `py39` ruff target. The six `firestarter` type imports live in a module-scope `TYPE_CHECKING` block (mypy-only); the runtime imports of the same six modules happen **inside the factory body**, mirroring `make_comm`'s existing deferred-import convention, so conftest's module-scope import set stays free of any `firestarter` module (preserving the tree's recorded import-time-binding traps). Each of the six values is passed through an explicit `cast(...)` at the one seam where a deliberately-substituted double is admitted into the `AppContext` constructor call -- the docstring states what the cast does and does not guarantee, and why the cast is not pushed out to the call sites (25 errors relocate) or the mock builders (attribute-defined errors at every assertion site instead, per the tree's own receipt at `test_validate_family_cmd.py:221`'s `# type: ignore[attr-defined]` and `test_dev_test_cmd.py:597-598`'s two live errors of that class). A thin `app_context` fixture wraps a no-argument call. Both new names are added to the module docstring's export enumeration. `tests.conftest` was deliberately NOT added to any mypy strict island (D-10 risk B) -- the factory's body is checked because it is fully annotated, not because of an override; the docstring states the residual (conftest's pre-existing unannotated fixtures stay unchecked). **Planted-error proof:** the first attempted plant (dropping the `cast` on `db` while its default stayed a `Mock`) produced **zero** new errors -- discovered live that mypy special-cases `unittest.mock.Mock` as assignable to any real class in argument/return position (confirmed via a 6-line minimal repro). The working plant instead assigned `config_manager` (a real, non-Mock, non-`EpromDatabase` class) to the `db` field: mypy count rose 63 -> 64 with the verbatim new line `tests/conftest.py:315: error: Argument "db" to "AppContext" has incompatible type "ConfigManager | Mock"; expected "EpromDatabase"  [arg-type]`, then reverted, count back to 63, `git status --porcelain` clean of anything but the intended diff. Committed as `ab1a9b4`.
- **Task 2:** Deleted the local `make_app_context` from `tests/test_dev_test_cmd.py` and `tests/test_write_skip_erase_0x0d.py`, importing the shared factory via `from .conftest import make_app_context`. Pure substitution, verified by diff: only the factory definition and import lines changed in `git diff HEAD~1`, no call-site line appears. `test_dev_test_cmd.py`'s two mock builders (`make_clean_operator`, `make_hardware_manager`) keep returning `Mock`, each now carrying a one-line comment pointing at the factory's cast-comment rationale. `test_write_skip_erase_0x0d.py`'s local factory additionally preset `operator.write_eprom.return_value = True` on its default double -- not called out in the plan's own measured-anchors note as a preserved behaviour, and verified inert before the substitution: none of the module's six tests inspect that return value directly, and `cli_handlers.py`'s `write` command does `sys.exit(0 if ok else 1)`, where an auto-created `Mock` is truthy by default -- all six tests pass unchanged with the plain shared-factory default. Mypy count: 63 -> 51 (-12, matching 6+6 exactly). Both modules' collected test counts unchanged (26 + 6 = 32). Committed as `82d17a0`.
- **Task 3:** Retyped the two remaining local factories as thin typed delegates. `tests/test_write_skip_sdp_unlock.py`'s delegate resolves `config_manager` before building a **real** `EpromOperator` from it when `eprom_operator` is `None` (preserving the load-bearing ordering that was the source of this module's seventh mypy error), then forwards everything to the shared factory imported as `_make_app_context`. `tests/test_validate_family_cmd.py`'s delegate keeps its leading `port` parameter (verified: no call site in the module passes it today, kept anyway per the plan's explicit "no silent behavioural narrowing" instruction) and its explicit port-clear-on-a-fresh-ConfigManager behaviour (load-bearing because `ConfigManager` is a process-wide singleton), forwarding the rest. Neither module's call sites were edited (confirmed via diff: only the factory definitions changed). Mypy count: 51 -> 38 (-13, matching 7+6 exactly). **Full-diff relocation check:** compared the complete before/after mypy error line sets; the only lines present after but not before are the three pre-existing `test_dev_test_cmd.py` `[attr-defined]` errors (unrelated to this plan, present before too) shifted by line-number drift from the earlier factory deletions -- zero genuinely new errors, zero relocation to any call site or mock-assertion site. Full suite: `python -m pytest tests/ -q` and the full `tools/ci_replica_venv.sh` leg 5 (`pytest --cov=firestarter --cov-fail-under=70`) both report **1295 passed, 0 failures**, coverage **81.72%**. `pyproject.toml` and `firestarter/eprom_operations.py` diffs both empty (watermark untouched at 35, ring-fence untouched). Committed as `1077b89`.
- **Requirements marked Complete:** RETIRE-05. No other RETIRE id touched.

## Task Commits

Each task was committed atomically, in the repo that owns the file:

1. **Task 1: typed factory + fixture in conftest.py (RETIRE-05, D-10)** — `ab1a9b4` (feat, `firestarter_app` submodule)
2. **Task 2: migrate test_dev_test_cmd + test_write_skip_erase_0x0d onto shared factory** — `82d17a0` (feat, `firestarter_app` submodule)
3. **Task 3: typed delegates for test_write_skip_sdp_unlock + test_validate_family_cmd** — `1077b89` (feat, `firestarter_app` submodule)

**Plan metadata:** this summary + STATE.md/ROADMAP.md/REQUIREMENTS.md updates (meta-repo, separate commit per `<final_commit>`).

## Files Created/Modified

- `firestarter_app/tests/conftest.py` — `make_app_context` factory + `app_context` fixture added; module docstring export list updated.
- `firestarter_app/tests/test_dev_test_cmd.py` — local factory deleted, shared factory imported, two mock-builder comments added.
- `firestarter_app/tests/test_write_skip_erase_0x0d.py` — local factory deleted, shared factory imported.
- `firestarter_app/tests/test_write_skip_sdp_unlock.py` — local factory retyped as a thin delegate onto the shared factory.
- `firestarter_app/tests/test_validate_family_cmd.py` — local factory retyped as a thin delegate onto the shared factory, `port` parameter preserved.

## Decisions Made

- **The `cast(...)` calls remain exactly as D-10 specifies, even though mypy's Mock-compatibility special-case means they are not strictly load-bearing against a Mock double.** Discovered live via a minimal repro that `Real | Mock` unions type-check against a `Real`-typed parameter/field with zero mypy complaint, regardless of the cast. This does not change the design: the casts are still load-bearing against a genuinely wrong, non-double type (confirmed by the working planted-error demonstration, which used exactly such a value), and the plan's own resolved-risk block explicitly forbids re-litigating D-10's decision. Recorded as a measured fact for whichever later plan or reader next touches this factory.
- **`test_write_skip_erase_0x0d.py`'s `write_eprom.return_value = True` preset was measured, not assumed, to be inert before dropping it in the pure substitution.** Verified against both the module's own assertions (none inspect the return value) and `cli_handlers.py`'s exit-code logic (truthy-by-default `Mock` return produces the same `sys.exit(0)`).
- **Chose `config_manager` (not the originally-suggested "remove the cast on `db`") as the working planted-error value**, after the first attempt produced zero new errors due to mypy's Mock-special-case — recorded as a plan-execution finding, not a plan deviation, since the acceptance criterion ("a planted error rises the count and names conftest.py") was still satisfied on the second attempt.

## Deviations from Plan

None — plan executed exactly as written. The two items above (Mock-compatibility discovery, the `write_eprom.return_value` inertness check) are measured findings recorded during execution, not deviations from the plan's instructions: no Rule 1-4 auto-fix was needed, no architectural change occurred, and every acceptance criterion in `132-05-PLAN.md` was met as specified.

## Issues Encountered

None beyond the two measured findings documented above under Decisions Made.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- **RETIRE-05's real guarantee, stated honestly per the plan's own instruction:** a new test module in Phase 133/134 that imports `tests.conftest.make_app_context` instead of hand-rolling a sixth untyped copy cannot reproduce the 30-error `**overrides: object` splat pattern. RETIRE-05 does **not** mean "everything in `conftest.py` is type-checked" — the module's pre-existing unannotated fixtures (e.g. `make_comm`'s inner `_factory`) remain unchecked, exactly as D-10 risk B's resolution states.
- **Measured count: 38 (checked 122 source files), watermark unchanged at 35.** This is **not yet at or below 35** — plan 132-06's six `[var-annotated]` fixes (`config.py:84,85,102`, `database.py:174,175,325`) remain owed before the watermark clears; the ledger's own projection (32) still requires that plan's contribution.
- Full test suite green: 1295 passed, 0 failures, coverage 81.72% (floor 70%). `ruff check` + `ruff format --check` both exit 0 across `firestarter/` and `tests/`.
- `pyproject.toml` and `firestarter/eprom_operations.py` are both byte-unchanged by this plan (verified via empty `git diff --stat`) — the watermark and the ring-fence both held.
- No blockers. RETIRE-01/02/03 (already Complete) remain untouched; RETIRE-04 (132-08), RETIRE-06 (132-09), RETIRE-07 (132-07), RETIRE-08 (132-08) remain untouched, as required. 132-06 can proceed against the newly-measured 38-error baseline.

---
*Phase: 132-retire-dev-sdp-discharge-the-mypy-debt*
*Completed: 2026-08-03*

## Self-Check: PASSED

Created/modified files verified present on disk:
- `.planning/phases/132-retire-dev-sdp-discharge-the-mypy-debt/132-05-SUMMARY.md` — FOUND
- `firestarter_app/tests/conftest.py` — FOUND
- `firestarter_app/tests/test_dev_test_cmd.py` — FOUND
- `firestarter_app/tests/test_write_skip_erase_0x0d.py` — FOUND
- `firestarter_app/tests/test_write_skip_sdp_unlock.py` — FOUND
- `firestarter_app/tests/test_validate_family_cmd.py` — FOUND

Commits verified present in the owning repo's history (`firestarter_app` submodule):
- `ab1a9b4` — FOUND
- `82d17a0` — FOUND
- `1077b89` — FOUND
