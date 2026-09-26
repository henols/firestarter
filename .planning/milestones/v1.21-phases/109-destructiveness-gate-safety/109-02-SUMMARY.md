---
phase: 109-destructiveness-gate-safety
plan: 02
subsystem: testing
tags: [chip_test, dev-test, safety-gate, banner-data, safe-02, firestarter_app]

# Dependency graph
requires:
  - phase: 109-destructiveness-gate-safety
    provides: "Plan.locked_destructive advisory field (109-01); derive_plan(destructive=False) structural strip"
provides:
  - "BannerCounts dataclass + count_applicable(plan, results) -> BannerCounts (SWEEP-05 banner DATA, no rendering)"
  - "SAFE-02 orchestrator-only property mechanically asserted by tests (routes-via-resolve_chip, source-scan, refusal-is-a-finding, restricted-method-set)"
affects: [110-diagnostic-report-provenance, 112-dev-test-handler-wiring]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Banner DATA vs rendering split: this phase emits (N, M, locked_steps) only; Phase 110/112 own presentation"
    - "M-from-single-Plan-object: count helper never re-derives via derive_plan (D-01/T-109-08), verified by a monkeypatch-raises test"
    - "AST-based source scan (not raw substring grep) to avoid false positives on prose/docstring mentions of the guarded terms"

key-files:
  created: []
  modified:
    - firestarter_app/firestarter/chip_test.py
    - firestarter_app/tests/test_chip_test.py

key-decisions:
  - "count_applicable(plan, results) -> BannerCounts{n_ran, m_applicable, locked_steps}: M = sum(supported plan.steps) + len(plan.locked_destructive); N = count of results with verdict in {OK, BAD, marginal}, excluding NA/SKIPPED"
  - "No print/render/CLI code added; verified by both a plan-authored 'no_print_or_render_introduced' test and manual grep review (grep's raw substring match on 'print(|click.|console' also matches pre-existing 'Fingerprint(' call sites -- those are unrelated to this task and predate it)"
  - "SAFE-02 source-scan test uses ast.walk (not raw text substring matching) to distinguish executable code (forbidden: raw dict keys 'cmd'/'bus-config'/'vpp_mv', force= kwargs, set_vpp calls, bare '--force' string literals outside docstrings) from prose/comments describing the safety property itself (e.g. 'passes no --force' in a docstring), which a naive grep would false-positive on"
  - "VPP-guard-refusal-is-a-finding tests cover both single-run (blank-check, exactly 1 call) and multi-run (destructive write, exactly 1 call -- the exception aborts run_plan's runs-loop for that step, not retried) shapes, per the plan's explicit single-vs-multi-run assertion split"

requirements-completed: [SWEEP-05, SAFE-02]

coverage:
  - id: D1
    description: "count_applicable(plan, results) returns applicable-only (N, M) plus the locked-step list, computed from the single Plan object; NA/SKIPPED excluded from both N and M's ran-count; a ran-but-BAD step counts toward N"
    requirement: SWEEP-05
    verification:
      - kind: unit
        ref: "tests/test_chip_test.py::test_count_applicable_uv_counts"
        status: pass
      - kind: unit
        ref: "tests/test_chip_test.py::test_count_applicable_eeprom_counts"
        status: pass
      - kind: unit
        ref: "tests/test_chip_test.py::test_count_applicable_bad_counts_as_ran"
        status: pass
      - kind: unit
        ref: "tests/test_chip_test.py::test_count_applicable_skipped_does_not_count_as_ran"
        status: pass
      - kind: unit
        ref: "tests/test_chip_test.py::test_count_applicable_m_from_single_plan_never_rederives"
        status: pass
      - kind: unit
        ref: "tests/test_chip_test.py::test_count_applicable_n_equals_m_when_destructive"
        status: pass
    human_judgment: false
  - id: D2
    description: "No print/render/CLI output introduced by the count helper (banner DATA only; rendering is Phase 110/112)"
    requirement: SWEEP-05
    verification:
      - kind: unit
        ref: "tests/test_chip_test.py::test_count_applicable_no_print_or_render_introduced"
        status: pass
    human_judgment: false
  - id: D3
    description: "Every op run_plan executes routes through chip_resolver.resolve_chip (guard-honoring), never derive_plan's guard-bypassing dict"
    requirement: SAFE-02
    verification:
      - kind: unit
        ref: "tests/test_chip_test.py::test_safe02_routes_via_resolve_chip_for_every_executed_step"
        status: pass
    human_judgment: false
  - id: D4
    description: "chip_test.py's executable code contains no VPP-set call, no raw wire/command dict key literal, and no force=True/--force pass-through (AST-based scan, docstring-exempt)"
    requirement: SAFE-02
    verification:
      - kind: unit
        ref: "tests/test_chip_test.py::test_safe02_no_vpp_no_wire_no_force_source_scan"
        status: pass
    human_judgment: false
  - id: D5
    description: "A firmware VPP-guard-flavored EpromOperationError is captured as a BAD StepResult with error_code, with NO silent retry-around (exact operator call-count assertion) -- both single-run and multi-run step shapes"
    requirement: SAFE-02
    verification:
      - kind: unit
        ref: "tests/test_chip_test.py::test_safe02_vpp_guard_refusal_is_a_finding_not_a_retry_single_run"
        status: pass
      - kind: unit
        ref: "tests/test_chip_test.py::test_safe02_vpp_guard_refusal_is_a_finding_not_a_retry_multi_run"
        status: pass
    human_judgment: false
  - id: D6
    description: "run_plan invokes only the six existing EpromOperator public methods (Mock(spec=[...]) restricted) -- a full destructive run completes without AttributeError"
    requirement: SAFE-02
    verification:
      - kind: unit
        ref: "tests/test_chip_test.py::test_safe02_only_known_operator_methods_no_attribute_error"
        status: pass
    human_judgment: false

duration: 22min
completed: 2026-07-02
status: complete
---

# Phase 109 Plan 02: SWEEP-05 Banner Data + SAFE-02 Verification Summary

**Applicable-only N-of-M banner count helper (`count_applicable`) reads Phase 109-01's `Plan.locked_destructive` field without a second derivation, and the SAFE-02 orchestrator-only safety property is now asserted by 5 mechanical tests instead of merely documented**

## Performance

- **Duration:** ~22 min
- **Started:** 2026-07-02T19:52:00Z
- **Completed:** 2026-07-02T20:14:00Z
- **Tasks:** 2
- **Files modified:** 2 (1 source + 1 test, both inside `firestarter_app/` submodule)

## Accomplishments

- Added `BannerCounts` dataclass (`n_ran`, `m_applicable`, `locked_steps`) and `count_applicable(plan, results) -> BannerCounts` to `chip_test.py`: M is computed as `sum(supported plan.steps)` + `len(plan.locked_destructive)` from the SINGLE `Plan` object produced by one `derive_plan` call; N counts `StepResult`s whose verdict is in `{OK, BAD, marginal}` (a ran-but-BAD step counts as ran; NA/SKIPPED do not).
- Verified applicable-only counting against two real DB chips: AM2716 (UV-EPROM, `N=3 < M=4`, locked={write}) and M8720 (EEPROM with `FLAG_CAN_ERASE`, `N=3 < M=5`, locked={write, erase}) — both prove the SWEEP-05 banner-trigger condition (N < M) fires correctly for a non-destructive run, and that a `destructive=True` run of the same chip yields `N == M` (banner would not fire).
- Proved (via a `monkeypatch`-raises-on-`derive_plan` test) that `count_applicable` never re-derives the plan — M comes exclusively from the one `Plan` object passed in (D-01, T-109-08).
- Added the SAFE-02 orchestrator-only verification suite: a spy-based test proving every executed step in `run_plan` resolves through `chip_resolver.resolve_chip` (never reusing `derive_plan`'s guard-bypassing dict); an AST-based source scan of `chip_test.py`'s executable code (docstrings excluded) asserting no VPP-set call, no raw wire/command dict key literal (`"cmd"`/`"bus-config"`/`"vpp_mv"`), and no `force=True`/bare `"--force"` string; two VPP-guard-refusal tests (single-run blank-check + multi-run destructive write) proving a firmware refusal becomes a captured `BAD` finding with `error_code` and is never silently retried (exact operator call-count == 1 in both cases); and a `Mock(spec=[six methods])` full destructive run proving `run_plan` never reaches for an out-of-spec method (e.g. a VPP setter).
- No production behavior change in `run_plan`/`_run_step`/`_dispatch_*` — the SAFE-02 property was already true from Phase 108/109-01; this plan adds the explicit mechanical assertion only.

## Task Commits

Both tasks committed atomically **inside the `firestarter_app` submodule** (branch `v1.21-community-chip-validation-command`):

1. **Task 1: applicable-only N-of-M banner-data count helper (SWEEP-05)** - `5f74b83` (feat)
2. **Task 2: SAFE-02 orchestrator-only verification tests** - `7246720` (test)

**Meta plan-metadata commit:** recorded below (see Self-Check / final commit).

## Files Created/Modified

- `firestarter_app/firestarter/chip_test.py` - `BannerCounts` dataclass + `count_applicable(plan, results)` (Task 1 only; Task 2 was test-only, no source change)
- `firestarter_app/tests/test_chip_test.py` - Task 1: `test_count_applicable_uv_counts`, `test_count_applicable_eeprom_counts`, `test_count_applicable_bad_counts_as_ran`, `test_count_applicable_skipped_does_not_count_as_ran`, `test_count_applicable_m_from_single_plan_never_rederives`, `test_count_applicable_n_equals_m_when_destructive`, `test_count_applicable_no_print_or_render_introduced`. Task 2: `test_safe02_routes_via_resolve_chip_for_every_executed_step`, `test_safe02_no_vpp_no_wire_no_force_source_scan`, `test_safe02_vpp_guard_refusal_is_a_finding_not_a_retry_single_run`, `test_safe02_vpp_guard_refusal_is_a_finding_not_a_retry_multi_run`, `test_safe02_only_known_operator_methods_no_attribute_error`

## Decisions Made

- **`count_applicable` return shape:** a `BannerCounts` dataclass (`n_ran`, `m_applicable`, `locked_steps`) rather than a bare tuple — gives Phase 110/112 named fields to consume for the report/banner render without re-deriving field order from a tuple index (Claude's discretion per the plan).
- **SAFE-02 source-scan uses `ast.walk`, not raw substring `grep`.** The plan's own acceptance-criterion grep (`grep -nE 'print\(|click\.|console'`) matches pre-existing, unrelated code (`Fingerprint(` / `classify_fingerprint(` call sites) as false positives, and a raw substring scan for `"--force"` would also false-positive on the module's own docstrings/comments describing the safety property in prose (e.g. "passes no `--force`"). The test instead parses the module's AST and inspects only `Call`/`Attribute`/`Dict` nodes and non-docstring `Constant` string nodes — precisely distinguishing executable code from descriptive prose, which is a stronger and more maintainable guard than the plan's illustrative grep example. The plan's grep was itself explicitly a "human-readable companion, not a replacement" for the eventual Plan 03 AST checker; this test partially previews that AST approach at the unit-test level.
- **VPP-guard-refusal test uses a synthetic `error_code=0xA9`** (not a specific named firmware constant) since no dedicated "VPP guard refused" error code constant exists in `exceptions.py`/`constants.py` yet — the test asserts the mechanism (any `EpromOperationError.error_code` is captured and surfaces as a `BAD` finding with no retry), which is code-independent and will hold once/if a dedicated VPP-guard error code is defined by firmware/host in a later phase.

## Deviations from Plan

None - plan executed exactly as written. Both tasks' behavior specs, action items, and acceptance criteria were implemented as designed; no Rule 1-4 auto-fixes were needed (the plan's target code — `run_plan`/`_run_step`/`_dispatch_*` — already satisfied SAFE-02 from Phase 108/109-01, exactly as the plan anticipated).

## Issues Encountered

- The plan's illustrative acceptance-criterion grep (`grep -nE 'print\(|click\.|console'`) produces false-positive matches against pre-existing `Fingerprint(`/`classify_fingerprint(` identifiers in `chip_test.py` (unrelated to render/print, predating this plan). Resolved by writing the actual test assertion (`test_count_applicable_no_print_or_render_introduced`) with a tighter word-boundary regex (`\bprint\(|\bclick\.|\bconsole`), and by documenting in this Summary that the raw grep is a discretionary manual-review aid, not a hard gate — the plan's `<verification>` section frames it as "Manual: confirm...", not an automated CI check.
- Similarly, a raw substring test for `"--force" not in src` failed against the module's own prose (docstrings mentioning "passes no --force" as documentation of the safety property). Resolved by switching that assertion to an AST-based scan that exempts docstring `Constant` nodes, which is both more precise and more robust to future prose edits than a substring ban.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- `count_applicable(plan, results) -> BannerCounts` is ready for Phase 110's diagnostic report model and Phase 112's `dev test` CLI handler to consume directly (no further `chip_test.py` change needed) — the `(n_ran, m_applicable, locked_steps)` triple is exactly the data Phase 110/112 need to render the "only N of M tests ran — pass `--destructive` on a scrap chip for the rest" banner and name the specific missing ops.
- SAFE-02's orchestrator-only property is now proven by 5 dedicated tests (routing, source-scan, single/multi-run refusal-is-a-finding, restricted-method-set) rather than merely asserted in comments — this is the exact "hollow-gate" avoidance this project's own v1.12 GATE-03 history calls for, and gives Plan 03's SAFE-03 AST checker (`tools/check_devtest_orchestrator.py`) a proven-correct human-readable reference to mirror.
- The `firestarter_app` gitlink was intentionally left un-bumped in the meta repo per standing policy (operator-gated at milestone close).

---
*Phase: 109-destructiveness-gate-safety*
*Completed: 2026-07-02*

## Self-Check: PASSED

- FOUND: `.planning/phases/109-destructiveness-gate-safety/109-02-SUMMARY.md`
- FOUND: `firestarter_app/firestarter/chip_test.py`
- FOUND: `firestarter_app/tests/test_chip_test.py`
- FOUND: submodule commit `5f74b83` (Task 1)
- FOUND: submodule commit `7246720` (Task 2)
- FOUND: meta commit `64acc52` (SUMMARY.md)
