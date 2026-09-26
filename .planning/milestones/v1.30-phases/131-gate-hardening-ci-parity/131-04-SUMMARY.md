---
phase: 131-gate-hardening-ci-parity
plan: 04
subsystem: testing
tags: [ast, check_devtest_orchestrator, gate-hardening, fail-closed, pytest]

# Dependency graph
requires:
  - phase: 131-01
    provides: fail-closed mypy watermark gate baseline; no interaction with this plan's devtest-orchestrator work
provides:
  - "A body-only AST derivation (`_referenced_underscore_helpers_in_dev_test`) of every module-level `_`-prefixed helper referenced from `dev_test`'s body, deliberately excluding its decorator list"
  - "A subset leg (`test_every_helper_referenced_by_dev_test_is_listed`) asserting the derived set is a subset of `_HANDLER_FUNCTION_NAMES`, naming any omission -- converts an additive fail-open into an additive fail-closed"
  - "A non-vacuity proof (`test_derivation_flags_an_unlisted_helper_non_vacuous`) that a synthetic unlisted helper is caught and named by the SAME derivation, and that a decorator-referenced helper is proven excluded"
  - "A RED-preserving proof, seen and read: the naive whole-node walk leaked `_complete_eprom` (dev_test's shell_complete= decorator argument), confirming correction F-04 live rather than by assumption"
affects: [133-sdp-lock-leg, 134-sdp-unlock-leg, 137-close-honesty-ledger]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Body-only ast.walk over a function's statement list, never ast.walk() on the whole FunctionDef node -- the whole-node walk silently includes decorator_list, which can reference module-level names (Click's shell_complete=) that are not part of the function's real logic"
    - "A single helper taking `source: str` (not a path) so both the real leg and its non-vacuity counterpart drive the identical code path -- the non-vacuity leg proves the HELPER catches a real addition, not that the test does"
    - "Subset (never equality) assertion when the allow-list legitimately contains names the derivation cannot see (helpers called from other handler-side functions, not from dev_test directly)"

key-files:
  created: []
  modified:
    - firestarter_app/tests/test_check_devtest_orchestrator.py
    - .planning/REQUIREMENTS.md

key-decisions:
  - "D-15 honored literally: tools/check_devtest_orchestrator.py and firestarter/cli_handlers.py are both untouched. The narrow allow-list stays narrow -- cli_handlers.py carries 10 pre-existing legitimate --force flags on unrelated commands, so a whole-file scan would be permanently red by design."
  - "Correction F-04 measured and proven, not merely implemented: a first (deliberately naive) version of the derivation used ast.walk(dev_test_node) over the whole FunctionDef, which is RED because it returns SEVEN names -- the extra one being _complete_eprom, dev_test's `@click.argument(\"chip\", shell_complete=_complete_eprom)` decorator argument, a shell-completion callback shared by 15 unrelated commands. The RED was seen and read before the body-only fix (walking dev_test.body statement-by-statement) made the leg GREEN."
  - "Non-vacuity guard placed BEFORE the subset comparison in the real leg (non-empty, >=6 members) plus an exact-six equality assertion against a named expected set -- so a shrinking or vanishing derived set is caught even though a bare subset check would still trivially pass."
  - "Task 2's synthetic fixture is a single inline module-source string testing BOTH halves of F-04 at once: a body-referenced unlisted helper (_sdp_leg_probe, the exact shape Phases 133/134 will add) IS caught and named, and a decorator-referenced unlisted helper (_decorator_only_helper, mirroring the real _complete_eprom shape) is proven excluded, not merely assumed absent."

requirements-completed: [GATE-10]

coverage:
  - id: D1
    description: "Body-only AST derivation of dev_test's referenced module-level `_`-prefixed helpers, asserted as a subset of _HANDLER_FUNCTION_NAMES with omissions named"
    requirement: "GATE-10"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_check_devtest_orchestrator.py#test_every_helper_referenced_by_dev_test_is_listed"
        status: pass
    human_judgment: false
  - id: D2
    description: "Non-vacuity proof: a synthetic unlisted dev_test-body helper is caught and named by the same derivation; a decorator-referenced helper is proven excluded (F-04 positive proof)"
    requirement: "GATE-10"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_check_devtest_orchestrator.py#test_derivation_flags_an_unlisted_helper_non_vacuous"
        status: pass
    human_judgment: false

# Metrics
duration: 35min
completed: 2026-08-03
status: complete
---

# Phase 131 Plan 04: GATE-10 Derived Handler-List Subset Leg Summary

**A body-only AST derivation proves every module-level helper `dev_test` actually calls is listed in `_HANDLER_FUNCTION_NAMES`, converting the allow-list's additive fail-open into an additive fail-closed, without touching the checker or the handler.**

## Performance

- **Duration:** ~35 min
- **Tasks:** 2
- **Files modified:** 1 (`firestarter_app/tests/test_check_devtest_orchestrator.py`), plus `.planning/REQUIREMENTS.md`

## Accomplishments

- Added `_referenced_underscore_helpers_in_dev_test(source: str) -> set[str]`: `ast.parse`s the given
  module source, collects every module-level `_`-prefixed `FunctionDef`/`AsyncFunctionDef` name, locates
  the module-level `dev_test` `FunctionDef`, and walks **only its body statements** (never `ast.walk()`
  on the whole node, which would include `decorator_list`), returning the intersection of names
  referenced there with the module-level set. Raises if `dev_test` is absent rather than returning an
  empty set, which would make a subset assertion vacuously true.
- Added `test_every_helper_referenced_by_dev_test_is_listed`: against the real, shipped
  `firestarter/cli_handlers.py`, asserts the derivation is non-empty and has at least six members
  (non-vacuity, checked BEFORE the comparison), asserts it equals exactly the six measured names
  (`_chip_id_fields`, `_is_interactive`, `_make_sampler`, `_resolve_write_scope`,
  `_sanitize_chip_token`, `_verdict_code`), asserts it is a subset of `_HANDLER_FUNCTION_NAMES` naming
  any omission, and asserts `_complete_eprom` is explicitly excluded.
- Added `test_derivation_flags_an_unlisted_helper_non_vacuous`: a synthetic inline module source
  defines `_decorator_only_helper` (referenced only from `dev_test`'s decorator) and `_sdp_leg_probe`
  (referenced from `dev_test`'s body, deliberately not in `_HANDLER_FUNCTION_NAMES`). Drives the SAME
  `_referenced_underscore_helpers_in_dev_test` the real leg calls and asserts: the body-referenced
  name IS in the derived set; the decorator-referenced name is NOT; and the omission list (derived
  minus `_HANDLER_FUNCTION_NAMES`) equals exactly `['_sdp_leg_probe']`.
- Both new legs are documented as entries 9 and 10 in the module's `Coverage:` docstring.
- `tools/check_devtest_orchestrator.py` and `firestarter/cli_handlers.py` remain byte-unchanged across
  all three of this plan's commits (verified via `git diff --name-only`).
- GATE-10 ticked in `.planning/REQUIREMENTS.md` with an evidence clause naming both new test functions;
  Traceability row updated to Complete.

## Task Commits

Task 1 was executed as a genuine RED -> GREEN cycle (`tdd="true"`):

1. **Task 1a (RED):** `e5bb029` — `test(131-04): RED - naive whole-node AST walk leaks decorator name (GATE-10)`.
   The helper was deliberately implemented first as `ast.walk(dev_test_node)` over the WHOLE
   `FunctionDef` (including `decorator_list`). Run and SEEN to fail: the derivation returned **seven**
   names against the real `cli_handlers.py` (`_chip_id_fields, _complete_eprom, _is_interactive,
   _make_sampler, _resolve_write_scope, _sanitize_chip_token, _verdict_code`), one more than the
   expected six -- the extra name, read from the actual pytest failure output, was `_complete_eprom`,
   exactly correction F-04's predicted defect. The failure was RED for the correct, substantive
   reason (the decorator-list leak), not a locator or import error.
2. **Task 1b (GREEN):** `40a9c26` — `feat(131-04): GREEN - body-only AST derivation excludes decorator (GATE-10)`.
   Changed the walk to iterate `dev_test_node.body` statement-by-statement (`for stmt in
   dev_test_node.body: for sub in ast.walk(stmt): ...`), excluding the decorator list by construction.
   Re-ran: exactly six names, `_complete_eprom` no longer present, all assertions pass.
3. **Task 2:** `632434f` — `test(131-04): non-vacuity proof for the derived-subset gate (GATE-10)`.
   Added the synthetic-fixture non-vacuity leg described above. No RED/GREEN cycle needed (this task
   is `type="auto"` without `tdd="true"`) -- the leg passed on first run because it drives the
   already-fixed helper from Task 1.

**Plan metadata:** this SUMMARY + `.planning/REQUIREMENTS.md` GATE-10 tick (meta-repo commit, separate
from the three `firestarter_app` commits above per the submodule commit protocol).

## Files Created/Modified

- `firestarter_app/tests/test_check_devtest_orchestrator.py` — added
  `_referenced_underscore_helpers_in_dev_test`, `test_every_helper_referenced_by_dev_test_is_listed`,
  `test_derivation_flags_an_unlisted_helper_non_vacuous`; extended the module `Coverage:` docstring
  with entries 9 and 10; added `ast` and `inspect` imports. 18 tests now collected (16 pre-existing +
  2 new).
- `.planning/REQUIREMENTS.md` — ticked `GATE-10`, added its evidence clause, updated the Traceability
  row to Complete.

## Decisions Made

See `key-decisions` in frontmatter. Summarized:

1. **Untouched-by-design confirmed, not merely stated.** `tools/check_devtest_orchestrator.py` and
   `firestarter/cli_handlers.py` are byte-identical to their state before this plan began (`git diff
   --name-only HEAD~3 HEAD` inside the submodule lists exactly one file across all three commits:
   `tests/test_check_devtest_orchestrator.py`).
2. **F-04 measured live, not inherited from the plan's prose.** The naive whole-node walk was
   actually written, actually run, and actually observed to return seven names with `_complete_eprom`
   as the extra one — matching the plan's own measured claim exactly, confirmed independently in this
   execution rather than trusted on the plan's say-so.
3. **Subset, never equality, against the real allow-list** — because `_default_uv_write_confirm` and
   `_is_uv_eprom` are legitimately listed in `_HANDLER_FUNCTION_NAMES` but not referenced from
   `dev_test`'s own body (they are called from other handler-side helper functions). An equality
   assertion there would be red on day one for the opposite reason.

## Deviations from Plan

None — plan executed exactly as written, including the explicit TDD RED-then-GREEN sequence the
`tdd="true"` attribute on Task 1 calls for.

## Issues Encountered

None.

## User Setup Required

None — no external service configuration required.

## Known Stubs

None.

## Next Phase Readiness

- GATE-10 is fully discharged; no follow-up work is owed by this plan.
- **Forward-looking note for Phases 133/134 (D-16, carried in the plan, not new work here):** prefer
  putting new `dev test`-adjacent logic in `firestarter/chip_test.py` (scanned by the checker in
  FULL) rather than as a new helper inside `cli_handlers.py`'s `dev_test` — that sidesteps the
  allow-list maintenance burden entirely. If a new helper IS added to `dev_test` without a matching
  `_HANDLER_FUNCTION_NAMES` entry, `test_every_helper_referenced_by_dev_test_is_listed` (this plan's
  leg) will now go red and name it, rather than silently passing.
- No blockers for Phase 131's remaining plans (`131-05`, `131-06`, `131-07`) or for Phase 132.

---
*Phase: 131-gate-hardening-ci-parity*
*Completed: 2026-08-03*

## Self-Check: PASSED

- FOUND: `.planning/phases/131-gate-hardening-ci-parity/131-04-SUMMARY.md`
- FOUND: `e5bb029` (test RED)
- FOUND: `40a9c26` (feat GREEN)
- FOUND: `632434f` (test non-vacuity proof)
