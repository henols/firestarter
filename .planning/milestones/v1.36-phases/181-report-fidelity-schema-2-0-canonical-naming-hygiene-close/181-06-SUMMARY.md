---
phase: 181-report-fidelity-schema-2-0-canonical-naming-hygiene-close
plan: 06
subsystem: dev-test-engine
tags: [duration-mean, elapsed, wall-clock, hyg-04, dedup-fingerprint]

requires:
  - phase: 181-report-fidelity-schema-2-0-canonical-naming-hygiene-close
    plan: "05"
    provides: "the additive AutoCapture.canonical_part_number key, 19 regenerated report snapshots, and D-16 re-proven at 14 to_dict() top-level keys"
provides:
  - "_aggregate_cycle_results's duration_s narrowed from a sum across cycles to the MEAN over the cycles that ran (drawn from `ran`, not `results`) -- a per-operation cost whose meaning does not vary with run_count, D-05's stated caveat and denominator recorded in the docstring"
  - "DiagnosticReport.elapsed (float | None, default None) -- a stored wall-clock measurement from CLI entry to immediately before the first serialization, assigned once by cli_handlers.dev_test, never computed inside to_dict()"
  - "The Click group's first body statement stamps a monotonic start time into ctx.meta under a private key; a new _cli_start_time() helper reads it back through click.get_current_context(silent=True); the group's --help text moved to the decorator's help= kwarg (byte-identical output) so the stamp could occupy body[0]"
  - "render()'s render-only summed 'steps total' row deleted outright (computation, guard, and its own under-report-admitting comment); replaced by one elapsed row reading the stored value off the exported dict, omitted when absent"
  - "submit.build_body gains an elapsed line beside the canonical-part-number line, rendered via the same _duration_text formatter the table already uses, omitted when absent"
  - "_cli_start_time registered in HYG-04's _HANDLER_FUNCTION_NAMES allow-list in the same commit as its call site; the referenced-helpers floor re-measured 6 -> 7"
  - "_TO_DICT_KEYS gains elapsed (alphabetically sorted); its counted-keys docstring moved to fifteen; 19 report-shape snapshots regenerated, one additive line each"
  - "D-16 re-proven after both changes: all 19 FROZEN_HASHES literals byte-identical to app base 04fd982, zero moved lines"
affects: [181-07, 181-08, 181-09, 181-10]

actuals:
  tokens: 10728
  tasks: 3
  commits: 6

tech-stack:
  added: []
  patterns:
    - "click-group-entry-stamp-via-context-meta: a monotonic start time recorded as the group's first body statement into ctx.meta under a private key, read back through click.get_current_context(silent=True) rather than module state -- per-invocation, so one CliRunner invocation cannot hand a later one a stale base; the group's docstring relocated to the decorator's help= kwarg (same --help output) so the stamp, not the docstring, occupies body[0]"
    - "stored-not-computed for a field a hand-written to_dict() exports three times per run: elapsed is assigned once by the handler and read as a plain attribute inside to_dict(), mirroring the existing is_uv/run_status precedent -- a value computed inside to_dict() would answer a different question on each of the three real invocations (console render, saved .json, saved .md's fenced block)"

key-files:
  created:
    - .planning/phases/181-report-fidelity-schema-2-0-canonical-naming-hygiene-close/evidence/181-06-duration-mean.txt
    - .planning/phases/181-report-fidelity-schema-2-0-canonical-naming-hygiene-close/evidence/181-06-elapsed-surfaces.txt
  modified:
    - firestarter_app/firestarter/chip_test.py
    - firestarter_app/firestarter/diagnostic_report.py
    - firestarter_app/firestarter/cli_handlers.py
    - firestarter_app/firestarter/submit.py
    - firestarter_app/tools/check_devtest_orchestrator.py
    - firestarter_app/tests/test_chip_test_timing.py
    - firestarter_app/tests/test_diagnostic_report.py
    - firestarter_app/tests/test_dev_test_cmd.py
    - firestarter_app/tests/test_blast_radius_invariance.py
    - firestarter_app/tests/test_check_devtest_orchestrator.py
    - firestarter_app/tests/fixtures/reports/*.json (19 files, one additive line each)

key-decisions:
  - "duration_s's mean is taken over `ran`, not `results` -- the numerator and denominator (run_count) describe the same population by construction, so they can never disagree about which cycles are being described. This resolves the plan's own flagged risk: the pre-existing durations comprehension was over `results`, invisible while the fold was a sum but load-bearing the moment it became a mean."
  - "The Click group's docstring moved from an inline function-body string literal to the @click.group(help=...) decorator kwarg. The plan's own AST verify leg requires g.body[0] to be the monotonic stamp; a docstring positioned as body[0] would either block the stamp from that position or (if placed after an assignment) silently stop being recognized as __doc__ by Python, breaking --help with no error. Moving it to help= preserves the exact user-facing text (verified via a real --help invocation) while satisfying the ordering constraint without deleting or degrading the docstring."
  - "The one-run exclusion comparison (Section 10, evidence transcript) is recorded as a relation (elapsed >= old_would_be_sum) with the milestone's house rule stated explicitly, not as a pass/fail threshold on either absolute number -- both numbers are mock-timing artifacts of one CliRunner invocation."

requirements-completed: [RPT-D1, RPT-D2]

coverage:
  - id: D1
    description: "_aggregate_cycle_results folds duration_s to the mean over the cycles that ran, proven by a standalone leg and order-insensitive; a fold with no measured duration stays None; a single-cycle list returns unchanged by identity"
    requirement: RPT-D1
    verification:
      - kind: unit
        ref: "Task 1 inline verify leg 1 (two-cycle fold, reversed-order fold, None case, single-result identity)"
        status: pass
      - kind: unit
        ref: "tests/test_chip_test_timing.py::test_the_fold_reports_the_mean_not_the_sum, ::test_the_mean_equals_sum_over_count_for_a_slowed_pair, ::test_a_fold_with_no_measured_duration_stays_none, ::test_a_single_cycle_result_is_returned_unchanged, ::test_cycle_order_does_not_change_the_folded_mean"
        status: pass
    human_judgment: false
  - id: D2
    description: "The durations comprehension draws from `ran`, not `results`, so the mean's numerator and denominator (run_count) describe the same population by construction; the round(..., 3) wrapper and the None guard survive unchanged (no new precision rule)"
    requirement: RPT-D1
    verification:
      - kind: unit
        ref: "Task 1 inline verify leg 3 (AST: round( present, sum(durations), 3 absent, docstring mentions mean)"
        status: pass
      - kind: unit
        ref: "tests/test_blast_radius_invariance.py (103 passed, includes the 19-way frozen-hash parametrization proving the fold change moved no hash)"
        status: pass
    human_judgment: false
  - id: D3
    description: "DiagnosticReport.elapsed is a stored field, stamped once at CLI entry, exported by to_dict() as a plain attribute read with no call node; a context-less report carries elapsed is None; two consecutive to_dict() calls on the same report return the same elapsed"
    requirement: RPT-D2
    verification:
      - kind: unit
        ref: "Task 2 inline verify legs 1-2 and 5 (AST: elapsed export has no Call node; a bare build_shape() report has elapsed is None and 15 top-level keys; elapsed is an annotated DiagnosticReport field)"
        status: pass
      - kind: e2e
        ref: "tests/test_dev_test_cmd.py::test_a_real_invocation_saves_a_nonnegative_elapsed_stable_across_to_dict_calls (saved JSON's elapsed vs the embedded block inside the saved .md -- the run's 2nd and 3rd real to_dict() calls agree)"
        status: pass
    human_judgment: false
  - id: D4
    description: "The Click group's FIRST body statement stamps a monotonic start into ctx.meta ahead of the test-mode short-circuit; dev_test's report.elapsed assignment is the statement immediately before report.render(console); AppContext gained no field and no module-level mutable state was introduced"
    requirement: RPT-D2
    verification:
      - kind: unit
        ref: "Task 2 inline verify leg 3 (AST: cli()'s body[0] contains 'monotonic'; dev_test's statement immediately before the render( call contains 'elapsed')"
        status: pass
      - kind: unit
        ref: "manual AppContext field-count check (6 fields, unchanged) plus a real `--help` invocation confirming byte-identical output after the docstring relocated to help="
        status: pass
    human_judgment: false
  - id: D5
    description: "_cli_start_time is registered in HYG-04's _HANDLER_FUNCTION_NAMES allow-list in the same commit as its call site; the referenced-helpers floor is re-measured (6 -> 7), not computed from prose"
    requirement: RPT-D2
    verification:
      - kind: unit
        ref: "tests/test_check_devtest_orchestrator.py (26 passed, includes test_every_helper_referenced_by_dev_test_is_listed and the >= 7 floor)"
        status: pass
      - kind: other
        ref: "tools/check_devtest_orchestrator.py exit 0"
        status: pass
    human_judgment: false
  - id: D6
    description: "The render-only summed row (computation, guard, table.add_row call, and its own under-report-admitting comment) is deleted outright; an elapsed row takes its exact table position, read off the exported dict, present only when the value is not None; no second derived duration number was introduced anywhere"
    requirement: RPT-D2
    verification:
      - kind: unit
        ref: "Task 3 inline verify legs 1-2 (grep: no 'steps total' literal anywhere in diagnostic_report.py, present '\"elapsed\"'; two-pass render leg: elapsed row present with a value, absent when None, no row containing 'total')"
        status: pass
      - kind: unit
        ref: "tests/test_diagnostic_report.py::test_elapsed_row_replaces_the_removed_summed_row, ::test_elapsed_row_is_absent_when_the_value_is_absent"
        status: pass
    human_judgment: false
  - id: D7
    description: "submit.build_body emits an elapsed line via _duration_text beside the canonical-part-number line when present, omits it when absent"
    requirement: RPT-D2
    verification:
      - kind: unit
        ref: "Task 3 inline verify leg 3 (build_body with elapsed=42.5 contains 'elapsed'; with elapsed=None does not)"
        status: pass
      - kind: unit
        ref: "tests/test_submit.py (110 passed, unchanged -- no existing test asserted exact body content that would collide)"
        status: pass
    human_judgment: false
  - id: D8
    description: "All 19 FROZEN_HASHES literals stay byte-identical to app base 04fd982 across both duration_s's fold change and elapsed's addition; the dedup-immunity test is byte-unchanged and green"
    requirement: RPT-D1
    verification:
      - kind: unit
        ref: "tests/test_blast_radius_invariance.py -k test_dedup_fingerprint_is_frozen (19 passed, run after both Task 1 and Task 3)"
        status: pass
      - kind: other
        ref: "git diff 04fd982 -- tests/fixtures/report_shapes.py | grep for twelve-hex literal lines: empty, both after Task 1 and after Task 3"
        status: pass
    human_judgment: false
  - id: D9
    description: "Zero # comments added to product source across the full seven-file set plus the pin module; the one file that rose (tools/check_devtest_orchestrator.py, non-product-source tooling) is a documented, pre-approved exemption matching 181-04/181-05's precedent"
    verification:
      - kind: unit
        ref: "Full tokenize COMMENT-token census, mandated script over git diff --name-only 04fd982..HEAD: 1/25 files OVER (tools/check_devtest_orchestrator.py, 91->92, tooling exemption); all product-source files at or below baseline"
        status: pass
    human_judgment: false
  - id: D10
    description: "Whole-repo porcelain across the meta repo, the firmware submodule, and the app repo after this plan's commits; chip_database.json byte-unchanged"
    verification:
      - kind: other
        ref: "git -C /workspaces/firestarter status --porcelain (clean); git -C /workspaces/firestarter_app status --porcelain firestarter/ (clean); git -C /workspaces/firestarter_app status --porcelain (clean, whole repo); git diff --stat 04fd982..HEAD -- firestarter/data/chip_database.json (empty)"
        status: pass
    human_judgment: false

duration: ~35min
completed: 2026-09-09
status: complete
---

# Phase 181 Plan 06: `duration_s` becomes a per-operation mean; a stored wall-clock `elapsed` replaces the render-only sum Summary

**`_aggregate_cycle_results` folds `duration_s` to the mean over the cycles that ran instead of their sum, a stored `DiagnosticReport.elapsed` measures the whole `dev test` command from CLI entry to just before the first serialization, and the render-only "steps total" row — which admitted in its own removed comment that it under-reported — is deleted and replaced by one row reading the stored value off the exported dict.**

## Performance

- **Duration:** ~35 min
- **Started:** 2026-09-09T12:48Z (precondition check)
- **Completed:** 2026-09-09T13:2xZ
- **Tasks:** 3 of 3 completed
- **Files modified:** 8 app-repo product/test files + 19 regenerated report-snapshot fixtures + 2 meta-repo evidence transcripts

## Accomplishments

- **Task 1 — `duration_s` becomes the mean, drawn from the same population `run_count` names.** `_aggregate_cycle_results`'s `duration_s=round(sum(durations), 3) if durations else None` became `round(sum(durations) / len(durations), 3) if durations else None`, with `durations` re-sourced from `ran` (the cycles that reached the operator) rather than `results` — a change invisible while the fold was a sum but load-bearing the instant it became a mean, since a non-`ran` cycle carrying a duration would otherwise enter the numerator without entering `run_count`'s denominator. The `round(..., 3)` wrapper and the `if durations else None` guard are untouched — no new precision rule (D-25), and the field still stays `None` rather than `0.0` when nothing produced a duration. The field-by-field docstring now states the mean, names its denominator as the population `run_count` already reports, and carries D-05's caveat that cycle 1 and cycle 2 are not the same operation; the clause that justified summing by reference to the render-only row is removed (that row dies in Task 3). Five new tests in `tests/test_chip_test_timing.py` (11 total, was 6) pin the mean-equals-sum-over-count relation against real per-cycle measurements, the strictly-smaller-than-sum property, the `None` case, the single-cycle identity return, and order-insensitivity.
- **Task 2 — a stored wall-clock `elapsed`, stamped once.** `DiagnosticReport` gained an additive `elapsed: float | None = None` field, exported by `to_dict()` as a plain attribute read (no call node — the AST leg proves it) so the value cannot differ across the run's three real `to_dict()` invocations. The Click group's FIRST body statement now stamps `time.monotonic()` into `ctx.meta` under a private key, ahead of the test-mode short-circuit that every `CliRunner` test takes — this required moving the group's `--help` text from an inline docstring to the `@click.group(help=...)` decorator kwarg, since the plan's own AST leg requires `body[0]` to be the stamp and Python only recognizes a bare string literal as `__doc__` when it is literally the first statement; a real `--help` invocation confirms byte-identical output after the move. A new `_cli_start_time()` helper resolves the stamp via `click.get_current_context(silent=True)`, returning `None` with no active context (a direct handler call). `dev_test` assigns `report.elapsed` from that helper as the statement immediately before `report.render(console)` — nothing sits between the stamp and the first serialization. `AppContext` gained no field; no module-level mutable state was introduced. `_cli_start_time` joined HYG-04's `_HANDLER_FUNCTION_NAMES` allow-list in the same commit as its call site; the referenced-helpers floor moved 6 → 7 (re-measured live). `_TO_DICT_KEYS` gained `elapsed` (alphabetically sorted, docstring moved to fifteen keys); this additive key moved all 19 report snapshots by one line each, regenerated via `tools/snapshot_report_shapes.py`. A new end-to-end test proves a real `dev test` run's saved JSON carries a non-negative `elapsed`, and that the run's second and third real `to_dict()` calls (the saved `.json` and the embedded JSON block inside the saved `.md`) agree on `elapsed`.
- **Task 3 — the sum-of-sums row is gone, `elapsed` takes its place and reaches the filed body.** `render()`'s "steps total" row — its `total = sum(...)` comprehension, its `if total:` guard, its `table.add_row(...)` call, and the comment above it that named the row's own exclusions (the identity read, plan derivation, the report write, the submit prompt) — is deleted in full; nothing is left describing a row that no longer exists. In its exact table position, one row now reads `d["elapsed"]` off the exported dict via the existing `_duration_cell` formatter, added only when the value is not `None`. `render()`'s docstring records the swap and the removed row's exclusions (phrased without the literal retired label, since the plan's own verify leg forbids that string surviving anywhere in the module). `submit.build_body` gained one line beside the canonical-part-number line, sourced from `sanitized_dict["elapsed"]` and rendered via the same `_duration_text` formatter the results table already uses — the two duration surfaces cannot disagree on precision — omitted entirely when the value is absent. `tests/test_diagnostic_report.py`'s summed-row test is replaced by two tests: one asserting the `elapsed` row's rendered cell and that no row containing "total" survives, and one asserting the row's absence when `elapsed is None`; the dedup-immunity test at the module's end is byte-unchanged and green. `tools/check_diagnostic_report_claims.py` and `tools/snapshot_report_shapes.py --check` both exit 0 (the row swap touches only `render()`, never `to_dict()`, so no snapshot drifted). Zero twelve-hex frozen-hash literal lines moved since app base `04fd982`, confirmed both after Task 1's fold change and after this task's row swap. A one-run exclusion comparison (a real `dev test` invocation against a clean-path mock: `elapsed=0.066`, `old_would_be_sum=0.004`) is recorded in the evidence transcript as the relation the removed row's own comment already conceded — `elapsed` covers strictly more of the run — stated per the milestone's house rule as evidence of the exclusion, never as a pass/fail threshold on either number.

## Task Commits

Each task committed atomically, split across the app submodule (code) and the meta repo (evidence):

1. **Task 1: `duration_s` becomes the mean over the cycles that ran**
   - `32f4ff7` (fix, app repo): the fold change, the docstring, five new tests
   - `0b2db34f` (docs, meta repo): `181-06-duration-mean.txt`
2. **Task 2: a stored wall-clock `elapsed`, stamped once at CLI entry**
   - `b595700` (feat, app repo): the field, the stamp, the helper, HYG-04 registration, the key-list pin, 19 regenerated snapshots, the new end-to-end test
   - `35e97296` (docs, meta repo): `181-06-elapsed-surfaces.txt` (Task 2 portion)
3. **Task 3: swap the render-only summed row for `elapsed`; carry it to the filed body**
   - `9db56fe` (fix, app repo): the row deletion/swap, `build_body`'s new line, the re-pointed test
   - `49d16f52` (docs, meta repo): `181-06-elapsed-surfaces.txt` extended (Task 3 portion, final)

**Plan metadata commit:** this SUMMARY.md, committed separately in the meta repo per the sequential-executor protocol (`STATE.md`/`ROADMAP.md` NOT touched — owned by the orchestrator).

## Files Created/Modified

- `firestarter_app/firestarter/chip_test.py` — `_aggregate_cycle_results`'s `duration_s` fold (sum → mean over `ran`); its field-by-field docstring
- `firestarter_app/firestarter/diagnostic_report.py` — `DiagnosticReport.elapsed` field; `to_dict()`'s fifteenth key; `render()`'s row swap and docstring
- `firestarter_app/firestarter/cli_handlers.py` — `import time`; `_CLI_START_MONOTONIC_META_KEY`; `_cli_start_time()`; the group's `help=` decorator kwarg and its first-statement stamp; `dev_test`'s `report.elapsed` assignment
- `firestarter_app/firestarter/submit.py` — `build_body`'s new elapsed line
- `firestarter_app/tools/check_devtest_orchestrator.py` — `_HANDLER_FUNCTION_NAMES` gains `_cli_start_time`; its fail-open comment updated
- `firestarter_app/tests/test_chip_test_timing.py` — five new mean-fold tests, module docstring extended
- `firestarter_app/tests/test_diagnostic_report.py` — the summed-row test replaced by two elapsed-row tests
- `firestarter_app/tests/test_dev_test_cmd.py` — one new end-to-end elapsed-stability test
- `firestarter_app/tests/test_blast_radius_invariance.py` — `_TO_DICT_KEYS` gains `elapsed`; the planted-mutation test's hardcoded `14` re-measured to `15`
- `firestarter_app/tests/test_check_devtest_orchestrator.py` — `_EXPECTED_DEV_TEST_REFERENCED_HELPERS` gains `_cli_start_time`; the `>= 6` floor re-measured to `>= 7`; one docstring sentence extended
- `firestarter_app/tests/fixtures/reports/*.json` (19 files) — regenerated via `tools/snapshot_report_shapes.py`; one additive line each
- `.planning/phases/181-.../evidence/181-06-duration-mean.txt` — Task 1's fold/relation transcript
- `.planning/phases/181-.../evidence/181-06-elapsed-surfaces.txt` — Tasks 2+3's stamp/export/row-swap/exclusion-comparison transcript

## Anchors That Had Moved (recorded per the plan's environment note)

- **`dev_test`'s `derive_plan` call site** is now a single expression (`write_scope="partial" if _is_uv_eprom(app, chip) else "full"`), not the two-line `interactive = _is_interactive(); write_scope = _resolve_write_scope(...)` the plan's `<read_first>` described — 181-04 already inlined that rule. `_cli_start_time`'s call and the `report.elapsed` assignment were placed accordingly, immediately before `report.render(console)`.
- **The Click group's docstring is no longer a body-position-0 string literal.** The plan's own AST verify leg requires `body[0]` to be the monotonic stamp; the pre-existing docstring occupied that position. Resolved by moving the text to `@click.group(help=...)`, verified byte-identical via a real `--help` invocation — not anticipated by the plan's read_first, which did not flag this conflict.
- **`render()`'s "steps total" row** was at `:1036-1049` at this plan's start (181-05 had already shifted it from the `<orchestrator_dispositions>`-stated `:993-1007`); confirmed by direct read before editing.

## Decisions Made

See `key-decisions` in frontmatter for the full text. In summary: the mean's `durations` comprehension is re-sourced from `ran` rather than `results` so the numerator and denominator can never describe different populations; the Click group's docstring moved to the decorator's `help=` kwarg to satisfy the plan's literal `body[0]` AST check without breaking `--help` or silently losing the string as an orphaned, unrecognized statement; and the one-run exclusion comparison is recorded as a relation, not a threshold, per the milestone's operation-counts-never-seconds house rule.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] The Click group's docstring occupied `body[0]`, blocking the plan's own AST verify leg**
- **Found during:** Task 2, before writing the stamp
- **Issue:** `cli()`'s existing docstring (`"""EPROM programmer for Arduino and Relatively-Universal-ROM-Programmer shield."""`) was `body[0]`; the plan's verify leg requires `body[0]` to unparse to the monotonic-stamp assignment. Placing the stamp before the docstring would leave the string as a dead, unrecognized expression statement — Python only treats a bare string literal as `__doc__` when it is the true first statement — silently breaking `--help` with no error.
- **Fix:** Moved the docstring's exact text to `@click.group(help="...")`. Verified byte-identical `--help` output via a real invocation before and is unaffected after.
- **Files modified:** `firestarter_app/firestarter/cli_handlers.py`
- **Verification:** `python -m firestarter.main --help` output unchanged; the AST leg's `body[0]` assertion passes
- **Committed in:** `b595700` (Task 2 commit)

**2. [Rule 3 - Blocking] Adding `elapsed` to `to_dict()` moved all 19 report-shape snapshots and one hardcoded key-count literal**
- **Found during:** Task 2, running `tests/test_dev_test_cmd.py tests/test_blast_radius_invariance.py`
- **Issue:** The additive `elapsed` key changed `to_dict()`'s output for every registered shape, failing all 19 `test_committed_snapshot_matches_a_fresh_regeneration` cases and one test with a hardcoded `assert len(keys) == 14`.
- **Fix:** Regenerated all 19 snapshots via `tools/snapshot_report_shapes.py` (one additive line each, no other drift); re-measured the hardcoded literal to `15`.
- **Files modified:** `firestarter_app/tests/fixtures/reports/*.json`, `firestarter_app/tests/test_blast_radius_invariance.py`
- **Verification:** `tools/snapshot_report_shapes.py --check` exits 0; `tests/test_blast_radius_invariance.py` 103 passed
- **Committed in:** `b595700` (Task 2 commit)

**3. [Rule 3 - Blocking] `dev_test`'s body now referencing `_cli_start_time` was not yet listed in HYG-04's allow-list**
- **Found during:** Task 2, running `tests/test_check_devtest_orchestrator.py`
- **Issue:** `test_every_helper_referenced_by_dev_test_is_listed` walks `dev_test`'s body for `_`-prefixed helper calls; `_cli_start_time` appeared in the derived set but not in `_HANDLER_FUNCTION_NAMES` or `_EXPECTED_DEV_TEST_REFERENCED_HELPERS`.
- **Fix:** Registered `_cli_start_time` in both (same commit as its call site, per D-19); re-measured the `>= 6` floor live to `>= 7`.
- **Files modified:** `firestarter_app/tools/check_devtest_orchestrator.py`, `firestarter_app/tests/test_check_devtest_orchestrator.py`
- **Verification:** `tests/test_check_devtest_orchestrator.py` 26 passed; `tools/check_devtest_orchestrator.py` exits 0
- **Committed in:** `b595700` (Task 2 commit)

---

**Total deviations:** 3 auto-fixed, all Rule 3 (blocking). **Impact:** All three were necessary to satisfy this plan's own acceptance criteria and verify legs as written; none widened scope beyond RPT-D1/RPT-D2/D-19. None reached a committed state without the fix.

## Issues Encountered

None beyond the deviations above.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

RPT-D1 and RPT-D2 are both fully discharged. `duration_s` is a per-operation mean whose meaning does not vary with `run_count`; `DiagnosticReport.elapsed` is a stored, once-stamped wall-clock measurement reaching the console, the saved artifact, and the filed issue body; the render-only sum-of-sums row is gone rather than kept beside its replacement. All 19 `FROZEN_HASHES` literals are proven byte-identical to app base `04fd982` after both changes. Waves 6-9 (`181-07` through `181-10`) can proceed against a `dev test` report whose `to_dict()` now carries fifteen top-level keys instead of fourteen, with HYG-04's allow-list and D-16's zero-re-key claim both current.

**Do not run the seven-leg green-tree battery or `check_rekey_ledger.py` against this plan's own scope** — per the plan's own `<verification>` section, that battery runs once, in `181-10`, with floor 2239. This plan's own automated legs (per-module pytest across every touched module, `ruff check`/`ruff format --check`, the mypy watermark, the claim scanner, the snapshot-drift check, the orchestrator checker, the mandated tokenize census, and the three porcelain legs) all pass independently of that battery.

## Comment Census (mandated full census, `git diff --name-only 04fd982..HEAD`, all `.py` files)

```
files over baseline: 1 / 25
  OVER: tools/check_devtest_orchestrator.py base=91 now=92
```

**Note on the one `OVER` line:** `tools/check_devtest_orchestrator.py` is NOT product source — both `/workspaces/CLAUDE.md`'s comment discipline and this plan's own `<comment_discipline>` section state so explicitly, and this exact exemption was already applied and recorded in plans `181-04` and `181-05`'s SUMMARYs for the same file. The added line is a legitimate, deliberate update to the fail-open allow-list's own explanatory comment, naming the helper (`_cli_start_time`) that just joined — required by this plan's Task 2 action text. All 24 remaining touched `.py` files (everything else in the mandated diff, including every product-source and test file this plan itself edited) are at or below their measured baselines.

## Self-Check: PASSED

- Both evidence transcripts confirmed present on disk with `[ -f ]`.
- All six commit hashes confirmed present via `git log --oneline --all`: app `32f4ff7`, `b595700`, `9db56fe`; meta `0b2db34f`, `35e97296`, `49d16f52`.
- `pytest` re-run across all six touched/dependent test modules combined: `392 passed`, zero failed/error/skipped.
- All plan-level `<verification>` items re-confirmed: the mean fold with order-insensitivity, the `None` case, and the single-result identity; the mean's denominator equal to `run_count`, drawn from `ran`; `to_dict()` carrying `elapsed` as a plain attribute read at fifteen top-level keys, `_TO_DICT_KEYS` moved in the same commit; the Click group's first statement the monotonic stamp, `report.elapsed`'s assignment the statement immediately before the first serialization; a context-less report carrying `elapsed is None`, two `to_dict()` calls agreeing on `elapsed`; the console carrying an `elapsed` row and no summed-total row, the filed body carrying an elapsed line, both omitted when absent; `tools/check_diagnostic_report_claims.py` and `tools/snapshot_report_shapes.py --check` both exiting 0; zero twelve-hex frozen-hash literal lines moved since app base `04fd982`, the dedup-immunity test byte-unchanged and green; zero comment count rises in product source (one documented, pre-approved tooling exemption), all three porcelain legs printing nothing.
- `ruff check firestarter/ tests/` and `ruff format --check firestarter/ tests/` both green.
- `tools/check_mypy_watermark.py`: `35` errors, at the pre-existing watermark, unchanged by this plan's edits.
- `firestarter/data/chip_database.json` confirmed byte-unchanged (`git diff --stat 04fd982..HEAD` empty for that path).

---
*Phase: 181-report-fidelity-schema-2-0-canonical-naming-hygiene-close*
*Completed: 2026-09-09*
