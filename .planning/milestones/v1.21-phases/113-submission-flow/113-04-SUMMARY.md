---
phase: 113-submission-flow
plan: 04
subsystem: submission
tags: [click, cli-wiring, ast-scan, safe-03, submit, dev-test]

# Dependency graph
requires:
  - phase: 113-submission-flow (Plan 01-03)
    provides: dedup_fingerprint/is_submittable (Plan 01), overall_verdict/build_title/
      build_body/build_issue_url/gh_available/submit_via_gh (Plan 02), submit_via_browser
      + submit_report (Plan 03) — the complete submit.py module
  - phase: 112-dev-test-handler-wiring
    provides: the `dev test` Click handler in cli_handlers.py, its render/persist call
      site, and the SAFE-03 AST checker (chip_test.py full scan + cli_handlers.py
      scoped handler scan)
provides:
  - "--submit Click is_flag on `dev test` + submit:bool parameter"
  - "Lazy `from firestarter import submit as submit_mod` call site inside dev_test,
    placed after the report is rendered+persisted and before sys.exit, calling
    submit_mod.submit_report(report, chip, json_file, console=console) — consumes the
    in-memory report and the already-resolved json_file path, never re-runs the sweep"
  - "FIRESTARTER_DEVTEST_SUBMIT env-override constant + a third full-scan leg in
    check_devtest_orchestrator.py's main() covering firestarter/submit.py in FULL
    (via _scan_file, mirroring the chip_test.py leg)"
  - "_assert_host_only coverage extended to the new submit.py target"
affects: [114-disposition-no-auto-graduate-lock]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Lazy intra-package import inside an `if submit:` block keeps submit.py off
      every other command's import path (mirrors the module's own SAFE-02
      orchestrator-only framing) — the import statement itself is invisible to the
      SAFE-03 AST scan since it only fires when the flag is set"
    - "Third full-scan leg via _scan_file (not _scan_target_functions) for a fresh,
      zero-pre-existing-force module — mirrors the chip_test.py leg exactly, distinct
      from the scoped cli_handlers.py handler-function-name-filtered scan reserved
      for large pre-existing multi-command files"

key-files:
  created: []
  modified:
    - firestarter_app/firestarter/cli_handlers.py
    - firestarter_app/tests/test_dev_test_cmd.py
    - firestarter_app/tools/check_devtest_orchestrator.py
    - firestarter_app/tests/test_check_devtest_orchestrator.py

key-decisions:
  - "Patched firestarter.submit.submit_report (module-attribute patch) rather than
    firestarter.cli_handlers.submit_mod — the import is lazy and local to the `if
    submit:` block, so the module-level patch target is the only stable seam across
    both the mocked-call-site tests and the end-to-end real-submit_report test"
  - "The off-TTY end-to-end test patches firestarter.submit.webbrowser.open and
    firestarter.submit.subprocess.run defensively, but the assertions hold
    structurally regardless: submit_report's own D-04 off-TTY branch returns before
    either seam is ever reached, since CliRunner's replaced sys.stdin naturally
    reports isatty()==False"
  - "submit.py is scanned in FULL (not scoped) because it is a fresh Phase-113 module
    with zero pre-existing force/VPP/wire-dict usage, exactly like chip_test.py —
    the scoped _scan_target_functions path stays reserved for the large,
    pre-existing cli_handlers.py"

requirements-completed: [SUB-01, SUB-02]

coverage:
  - id: D1
    description: "--submit is a Click is_flag flag on `dev test`, defaulting False, wired to a submit:bool parameter"
    requirement: SUB-01
    verification:
      - kind: unit
        ref: "tests/test_dev_test_cmd.py::TestSubmitFlag::test_submit_flag_calls_submit_report_once_with_report_chip_json_file"
        status: pass
    human_judgment: false
  - id: D2
    description: "A bare `dev test <chip>` run (no --submit) never calls submit_report — no submission side effect on a plain run"
    requirement: SUB-02
    verification:
      - kind: unit
        ref: "tests/test_dev_test_cmd.py::TestSubmitFlag::test_bare_run_never_calls_submit_report"
        status: pass
    human_judgment: false
  - id: D3
    description: "--submit invokes submit_report exactly once with the in-memory report, chip, and resolved json_file path (no re-run of the sweep)"
    requirement: SUB-01
    verification:
      - kind: unit
        ref: "tests/test_dev_test_cmd.py::TestSubmitFlag::test_submit_flag_calls_submit_report_once_with_report_chip_json_file"
        status: pass
    human_judgment: false
  - id: D4
    description: "Off-TTY --submit through the REAL submit_report prints body+URL and never opens a browser or shells out to gh (D-04 reuse)"
    requirement: SUB-02
    verification:
      - kind: unit
        ref: "tests/test_dev_test_cmd.py::TestSubmitFlag::test_submit_off_tty_end_to_end_never_opens_browser_or_runs_gh"
        status: pass
    human_judgment: false
  - id: D5
    description: "SAFE-03 checker gains a third full-scan leg for submit.py; the real module passes with the PASS line naming it"
    verification:
      - kind: integration
        ref: "tests/test_check_devtest_orchestrator.py::test_checker_exits_zero_on_real_submit_and_pass_line_names_it"
        status: pass
      - kind: other
        ref: "python tools/check_devtest_orchestrator.py"
        status: pass
    human_judgment: false
  - id: D6
    description: "Anti-hollow proof: a planted VPP-set / force=True fixture injected via FIRESTARTER_DEVTEST_SUBMIT flips the checker non-zero; a clean fixture through the same seam still passes"
    verification:
      - kind: integration
        ref: "tests/test_check_devtest_orchestrator.py::test_checker_exits_nonzero_on_planted_submit_vpp_set_violation"
        status: pass
      - kind: integration
        ref: "tests/test_check_devtest_orchestrator.py::test_checker_exits_nonzero_on_planted_submit_force_violation"
        status: pass
      - kind: integration
        ref: "tests/test_check_devtest_orchestrator.py::test_env_override_points_at_a_clean_submit_fixture_still_passes"
        status: pass
    human_judgment: false

duration: 35min
completed: 2026-07-03
status: complete
---

# Phase 113 Plan 04: Wire `--submit` into `dev test` + extend SAFE-03 to submit.py Summary

**`--submit` Click flag + lazy `submit_report` call site closes SUB-01/02; SAFE-03 orchestrator gate now scans `submit.py` as a third full-scan leg, proven non-hollow via planted-violation fixtures — this closes Phase 113.**

## Performance

- **Duration:** 35 min
- **Tasks:** 2
- **Files modified:** 4

## Accomplishments
- `dev test` gained a real, explicit `--submit` flag: a bare run never submits (SUB-02); `--submit` files the already-rendered, already-persisted report via a single lazy call to `submit_report(report, chip, json_file, console=console)` — no sweep re-run, no re-derivation.
- The lazy `from firestarter import submit as submit_mod` import stays entirely inside the `if submit:` block, keeping `submit.py` off the import path of every other CLI command.
- The SAFE-03 AST checker (`check_devtest_orchestrator.py`) now scans `submit.py` as a third, full-scan target (`FIRESTARTER_DEVTEST_SUBMIT`, mirroring the `chip_test.py` leg) — the real module passes and the PASS line names it.
- Anti-hollow proof for the new leg: planted VPP-set and `force=True` fixtures injected via `FIRESTARTER_DEVTEST_SUBMIT` flip the checker to non-zero with a `FAIL:` summary; a clean fixture through the same env-override still passes.
- Phase 113 (Submission Flow) is now feature-complete: SUB-01, SUB-02, and SUB-03 (Plan 01) are all satisfied.

## Task Commits

Each task was committed atomically:

1. **Task 1: --submit flag + lazy submit_report call site in dev_test (+ end-to-end tests)** - `dffcca9` (feat) — inside `firestarter_app` submodule
2. **Task 2: SAFE-03 — add submit.py as a third full-scan leg + anti-hollow test** - `b052092` (test) — inside `firestarter_app` submodule

**Plan metadata:** committed separately in the meta-repo (this commit).

## Files Created/Modified
- `firestarter_app/firestarter/cli_handlers.py` - `--submit` Click option + `submit: bool` param on `dev_test`; lazy `submit_report` call site after persist, before `sys.exit`; docstring updated
- `firestarter_app/tests/test_dev_test_cmd.py` - new `TestSubmitFlag` class: bare-run-never-calls, called-once-with-args, off-TTY end-to-end via the real `submit_report`
- `firestarter_app/tools/check_devtest_orchestrator.py` - `_DEFAULT_DEVTEST_SUBMIT` / `FIRESTARTER_DEVTEST_SUBMIT` constants; third full-scan leg in `main()`'s `targets`/scan/aggregation; module docstring updated
- `firestarter_app/tests/test_check_devtest_orchestrator.py` - new Test 8 block: real-submit PASS-line-naming assertion, planted VPP-set + force=True submit-shaped fixtures, clean-fixture env-override sanity check

## Decisions Made
- Patched `firestarter.submit.submit_report` (the module attribute) rather than any `cli_handlers`-local alias, since the import inside `dev_test` is lazy and local — this is the one stable seam that works for both the mocked-call-site assertions and the real-`submit_report` end-to-end test.
- `submit.py` is scanned in FULL via `_scan_file` (not the scoped `_scan_target_functions` handler path) because it is a fresh Phase-113 module with zero pre-existing force/VPP/wire-dict usage, exactly mirroring the existing `chip_test.py` leg — the scoped path stays reserved for the large, pre-existing `cli_handlers.py`.
- The off-TTY `--submit` end-to-end test patches `firestarter.submit.webbrowser.open` / `firestarter.submit.subprocess.run` defensively for readability, but the assertions hold structurally regardless of whether the patch affects `submit_report`'s already-bound default parameters: `submit_report`'s own D-04 off-TTY branch returns before either seam is ever reached, since `CliRunner`'s replaced `sys.stdin` naturally reports `isatty() == False`.

## Deviations from Plan

None — plan executed exactly as written. Both tasks landed with zero Rule 1/2/3 auto-fixes; no architectural questions arose.

## Issues Encountered

None. `python tools/check_devtest_orchestrator.py` stayed green after Task 1 (adding the `--submit` flag + call site introduced no VPP-set/wire-dict/force violation to the scoped `cli_handlers.py` handler scan) and after Task 2 (the real `submit.py` has zero pre-existing violations, so the new full-scan leg passes on the first run).

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

Phase 113 (Submission Flow) is complete: SUB-01/02/03 all satisfied, SAFE-03 extended and non-hollow across all three orchestrator surfaces (`chip_test.py`, `cli_handlers.py` scoped, `submit.py` full). Ready for `/gsd-execute-phase 114` (Disposition / No-Auto-Graduate Lock, feature close) — Phase 114 depends only on the DB-diff from Phase 110, never on any code in this plan.

---
*Phase: 113-submission-flow*
*Completed: 2026-07-03*

## Self-Check: PASSED

- FOUND: firestarter_app/firestarter/cli_handlers.py
- FOUND: firestarter_app/tests/test_dev_test_cmd.py
- FOUND: firestarter_app/tools/check_devtest_orchestrator.py
- FOUND: firestarter_app/tests/test_check_devtest_orchestrator.py
- FOUND: .planning/phases/113-submission-flow/113-04-SUMMARY.md
- FOUND commit: dffcca9 (firestarter_app)
- FOUND commit: b052092 (firestarter_app)
