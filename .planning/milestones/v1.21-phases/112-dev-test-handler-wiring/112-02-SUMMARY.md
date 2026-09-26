---
phase: 112-dev-test-handler-wiring
plan: 02
subsystem: cli
tags: [click, cli-handlers, diagnostic-report, chip-test, sampler, python]

# Dependency graph
requires:
  - phase: 112-01
    provides: "run_plan(..., sampler=None) keyword param threaded through _run_step/_dispatch_step/_dispatch_multi_run, bracketing OP_WRITE's operator.write_eprom call"
  - phase: 111-measured-voltage-sampler
    provides: "sample_vpp_mv/sample_vpe_mv wrappers (VOLT-01) on HardwareManager"
  - phase: 110-diagnostic-report-model
    provides: "DiagnosticReport/AutoCapture/TransportHealth/Provenance/DbDiff, prompt_provenance, build_db_diff, is_submittable"
  - phase: 108-109-test-plan-engine
    provides: "derive_plan/run_plan/count_applicable/BannerCounts, verdict vocabulary"
provides:
  - "dev_test — the @dev.command(\"test\") Click handler in cli_handlers.py, registered as a sibling of dev validate-family"
  - "firestarter dev test <chip> [--destructive] [--output-dir DIR] [-y/--yes] end-to-end: prompt -> derive_plan -> run_plan (sampler-wired) -> DiagnosticReport -> render(stdout) -> optional dual-artifact write -> sys.exit(0/1/2)"
  - "_verdict_code / _is_interactive / _make_sampler / _is_uv_eprom / _chip_id_fields / _sanitize_chip_token private composition helpers"
affects: [112-03-safe03-checker-repoint-and-handler-tests, 113-submission-flow]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "TTY-check factored into a private _is_interactive() function rather than an inline sys.stdin.isatty() call, because click.testing.CliRunner.invoke replaces sys.stdin with its own stream for the duration of the call — a test-time patch(\"sys.stdin.isatty\") applied before invoke() does not survive, but patch(\"firestarter.cli_handlers._is_interactive\") does."
    - "Sampler thunk as a closure factory (_make_sampler) returning a function that mutates the DiagnosticReport's before/after voltage slots in place, keeping chip_test.py fully hardware.py-agnostic per 112-01's contract."
    - "Single-source dual render/artifact: report.to_dict() is the only serialization path; the .md artifact wraps report.to_json_block() beneath a small human table rather than hand-maintaining a second field list."

key-files:
  created: []
  modified:
    - firestarter_app/firestarter/cli_handlers.py
    - firestarter_app/tests/__snapshots__/test_characterization.ambr

key-decisions:
  - "Landed Task 1 (registration/flags/exit-code) and Task 2 (sampler/TTY/artifacts) as a single commit rather than two: both tasks modify the same contiguous dev_test function body, and splitting them would have required writing then rewriting the same lines with no independently-meaningful intermediate state. Documented as a plan-structure note (mirrors 112-01's own TDD Gate Compliance note)."
  - "chip_id_actual/chip_id_mismatch_reason are recovered by parsing the id StepResult's reason string (the only place chip_test._dispatch_id records the detected id) rather than widening StepResult's schema — keeps chip_test.py's public contract unchanged (112-01's non-goal)."
  - "fw_board_identity is left None (best-effort) because EpromOperator.comm is a transient per-operation connection that is explicitly set back to None after every operator call (_disconnect_programmer) — there is no live comm object to read programmer_info off of after run_plan returns without opening a new, extraneous connection (which would violate the orchestrator-only invariant)."
  - "_sanitize_chip_token replaces every non [A-Za-z0-9._-] character with _ (handles parens, slashes, spaces in chip names like DS1220(RW)) — deterministic and simple over a more elaborate slug scheme."

patterns-established:
  - "TTY-gated CLI prompt seam: any future interactive CLI handler tested via CliRunner should factor its isatty() check into its own patchable function rather than relying on sys.stdin being patchable directly."

requirements-completed: [SWEEP-01, SWEEP-02, SWEEP-03, SWEEP-04, SWEEP-05, PATT-01, PATT-02, PATT-03, RPT-01, RPT-02, RPT-03, RPT-04, RPT-05, VOLT-01, XPORT-01]

coverage:
  - id: D1
    description: "dev test is a registered Click subcommand (sibling of dev validate-family) with positional chip arg + --destructive/--output-dir/-y flags"
    requirement: "SWEEP-01"
    verification:
      - kind: unit
        ref: "python -c \"from firestarter.cli_handlers import cli; assert 'test' in cli.commands['dev'].commands\""
        status: pass
      - kind: manual_procedural
        ref: "CliRunner(['dev','test','--help']) output lists chip arg + --destructive/--output-dir/-y (manual smoke, this session)"
        status: pass
    human_judgment: false
  - id: D2
    description: "Without --destructive: id+read+blank-check only (N<M, exit 0); with --destructive: adds write/erase/verify"
    requirement: "SWEEP-02"
    verification:
      - kind: manual_procedural
        ref: "CliRunner smoke: M8720 non-destructive -> banner '3 of 5 ran', exit 0; --destructive -> write_eprom invoked, sample_vpp_mv called 4x (before/after brackets)"
        status: pass
    human_judgment: false
  - id: D3
    description: "3-way exit code: BAD->1 (incl. chip-ID mismatch), marginal-only->2, OK/NA/SKIPPED-only->0, computed as max over per-verdict codes"
    requirement: "SWEEP-05"
    verification:
      - kind: manual_procedural
        ref: "CliRunner smoke: AS29F002T with mismatched detected chip-id (0xDEAD vs expected 0x52B0) -> exit 1; clean M8720 sweep -> exit 0"
        status: pass
    human_judgment: false
  - id: D4
    description: "TTY-aware prompting: on-TTY prompts provenance + one-line destructive confirm; off-TTY skips both, blank Provenance, --destructive itself is consent; -y bypasses only the destructive confirm, never provenance"
    requirement: "RPT-04"
    verification:
      - kind: manual_procedural
        ref: "CliRunner smoke with patch(\"firestarter.cli_handlers._is_interactive\", True): prompt_provenance+Confirm.ask both called; with -y: prompt_provenance called, Confirm.ask NOT called; declining confirm aborts before write_eprom is called"
        status: pass
    human_judgment: false
  - id: D5
    description: "Sampler thunk fills split before/after voltage slots on destructive runs; standalone read fills vpp_mv/vpe_mv on non-destructive runs (Phase-111 D-04)"
    requirement: "VOLT-01"
    verification:
      - kind: manual_procedural
        ref: "CliRunner smoke: destructive run's rendered voltage row shows vpp/vpe before/after populated from mocked hardware_manager; non-destructive run's row shows vpp=12000 vpe=5000 standalone with before/after=not measured"
        status: pass
    human_judgment: false
  - id: D6
    description: "report.render() always prints to stdout; --output-dir writes exactly dev-test-<chip>.json and dev-test-<chip>.md; no files written without --output-dir"
    requirement: "RPT-01"
    verification:
      - kind: manual_procedural
        ref: "CliRunner smoke with tempfile.TemporaryDirectory(): os.listdir(d) == ['dev-test-M8720.json', 'dev-test-M8720.md'] after invoking with --output-dir"
        status: pass
    human_judgment: false
  - id: D7
    description: "Orchestrator-only: no VPP-set, no raw wire-dict, no --force in the new handler"
    verification:
      - kind: other
        ref: "cd firestarter_app && python tools/check_devtest_orchestrator.py (exits 0, scans chip_test.py; handler-scan is Plan 03's repoint)"
        status: pass
      - kind: other
        ref: "grep -nE 'set_vpp|enable_vpp|write_vpp|vpp_enable|assert_vpp|raise_vpp|--force' firestarter/cli_handlers.py — all hits fall in pre-existing commands above line 1650 (dev_test starts at 1650), zero inside the new handler"
        status: pass
    human_judgment: false
  - id: D8
    description: "ruff check / ruff format --check / mypy watermark gate all pass on cli_handlers.py"
    verification:
      - kind: unit
        ref: "cd firestarter_app && ruff check firestarter/ && ruff format --check firestarter/ && python tools/check_mypy_watermark.py"
        status: pass
      - kind: unit
        ref: "cd firestarter_app && python -m mypy firestarter/cli_handlers.py -> 'Success: no issues found in 1 source file'"
        status: pass
    human_judgment: false
  - id: D9
    description: "Dedicated CliRunner unit test module (test_dev_test_cmd.py) proving these behaviors under pytest, not just manual smoke"
    human_judgment: true
    rationale: "Plan 112-03's frontmatter explicitly lists tests/test_dev_test_cmd.py as ITS files_modified deliverable (Task 2), not this plan's. This plan's own tasks list only firestarter/cli_handlers.py under files_modified. Behavior was proven via manual CliRunner scripts against a mock AppContext during this session (see verification refs on D1-D6 above) and the full existing suite (pytest tests/ minus one pre-existing unrelated failure) stayed green, but the codified pytest module is intentionally deferred to 112-03 per the plan split — a human/future-plan should confirm 112-03 actually lands that coverage."

# Metrics
duration: 45min
completed: 2026-07-03
status: complete
---

# Phase 112 Plan 02: dev test Handler Wiring Summary

**Built the `firestarter dev test <chip>` end-to-end CLI flow — provenance/destructive-confirm prompts, derive_plan/run_plan/count_applicable composition with a hardware-sampler thunk bracketing the write step, DiagnosticReport assembly, stdout render, optional dual-artifact write, and a 3-way (0/1/2) scriptable exit code.**

## Performance

- **Duration:** 45 min
- **Started:** 2026-07-03T09:12:22Z
- **Completed:** 2026-07-03T09:57:00Z
- **Tasks:** 2
- **Files modified:** 2 (1 source, 1 snapshot fixture)

## Accomplishments
- Registered `@dev.command(name="test")` in `cli_handlers.py` as a sibling of `dev_validate_family`, with a positional `chip` argument (shell-completion via `_complete_eprom`) plus `--destructive`, `--output-dir`, and `-y/--yes` flags — all CLI-only, never read from `config_manager` or environment.
- Composed the full sweep: `derive_plan(chip, app.db, destructive=destructive)` → `run_plan(plan, app.eprom_operator, app.db, sampler=<thunk or None>)` → `count_applicable(plan, results)` for the N-of-M banner → `DiagnosticReport` assembly (`AutoCapture`, `TransportHealth`, `Provenance`, `DbDiff` via `build_db_diff`).
- Built `_make_sampler`, a closure factory that wraps `app.hardware_manager.sample_vpp_mv()`/`sample_vpe_mv()` and writes into the report's `vpp_before_mv`/`vpp_after_mv`/`vpe_before_mv`/`vpe_after_mv` slots — passed to `run_plan` only on `--destructive` runs (verified: exactly 4 sampler calls, 2 before + 2 after, around the write). On non-destructive runs, a standalone single read fills `vpp_mv`/`vpe_mv` instead (Phase-111 D-04), leaving before/after `None` (renders `not measured`).
- Implemented TTY-aware gating (D-02/D-03) via a new `_is_interactive()` seam: on a TTY, `prompt_provenance(is_uv)` runs before the sweep and (when `--destructive` and not `-y`) a `Confirm.ask("--destructive will sacrifice the chip. Continue?", default=False)` gate must be accepted or the command aborts cleanly with exit 0 before any operator call; off-TTY, both prompts are skipped, a blank `Provenance()` is used (`is_submittable` → `False`, correct-not-a-gap), and `--destructive` itself is the consent signal.
- Implemented the 3-way exit code via `_verdict_code` (OK/NA/SKIPPED→0, marginal→2, BAD→1) and `sys.exit(max(_verdict_code(r.verdict) for r in results))`; verified a chip-ID mismatch (id step BAD) exits 1, a clean sweep exits 0, and an empty result list exits 0.
- Implemented the dual-artifact write (D-05): only under `--output-dir`, writes `dev-test-<safe_chip>.json` (`report.to_dict()`) and `dev-test-<safe_chip>.md` (a small results table + `report.to_json_block()`), via a new `_sanitize_chip_token` helper that replaces filesystem-unsafe characters. `report.render(console)` (fresh `rich.console.Console()`) runs unconditionally before the artifact-write branch and before `sys.exit`.
- Added `_is_uv_eprom` (mirrors `chip_test._write_region_for`'s OR'd `electrical-type == "UV-EPROM"` / `algorithm == 0x0B` signal) to drive `prompt_provenance`'s `owns_eraser` gate, and `_chip_id_fields` to recover `chip_id_expected`/`chip_id_actual`/`chip_id_mismatch_reason` for `AutoCapture` — the mismatch fields are parsed from the id step's `StepResult.reason` text (the only place that data exists today) rather than widening `chip_test.py`'s schema.

## Task Commits

Both tasks landed together inside the `firestarter_app` submodule (branch `v1.21-community-chip-validation-command`) — see "Deviations from Plan" for why:

1. **Task 1 + Task 2: dev test handler (registration, exit-code, sampler, TTY prompts, report assembly, dual-artifact write)** - `ccfb7e6` (feat)
2. **Snapshot update for the new subcommand appearing in `dev --help`** - `009c296` (test)

**Plan metadata:** (this commit, meta-repo) — docs: complete plan

## Files Created/Modified
- `firestarter_app/firestarter/cli_handlers.py` — Added imports (`rich.console.Console`, `rich.prompt.Confirm`, `chip_test.{OP_ID,VERDICT_*,count_applicable,derive_plan,run_plan}`, `diagnostic_report.{AutoCapture,DiagnosticReport,Provenance,TransportHealth,build_db_diff,prompt_provenance}`); added the `dev_test` handler and its private helpers (`_verdict_code`, `_sanitize_chip_token`, `_is_uv_eprom`, `_chip_id_fields`, `_is_interactive`, `_make_sampler`) after `dev_validate_family`.
- `firestarter_app/tests/__snapshots__/test_characterization.ambr` — Regenerated the `dev --help` snapshot (single additive line for the new `test` subcommand).

## Decisions Made
- Landed both plan tasks in one commit (see Deviations) since they modify the same contiguous function body and an artificial mid-function split would add rewrite churn with no independently-compiling intermediate state.
- `_is_interactive()` factored out of the inline `sys.stdin.isatty()` call specifically because `click.testing.CliRunner.invoke` replaces `sys.stdin` with its own stream object for the duration of the call, so a test-time `patch("sys.stdin.isatty", ...)` applied before `invoke()` silently does not take effect — verified this empirically during manual smoke testing (a `patch("sys.stdin.isatty", return_value=True)` produced `False` inside a `CliRunner`-invoked command). Patching the module-level `_is_interactive` function survives because `CliRunner` never touches it.
- `fw_board_identity` is left `None` (the `AutoCapture` default, honest "not measured" for this field) rather than reading `app.eprom_operator.comm.programmer_info`, because `EpromOperator.comm` is torn down (`self.comm = None`) after every single operator call via `_disconnect_programmer` (`eprom_operations.py:384-388`) — by the time `run_plan` returns, there is no live `comm` to read from, and opening a fresh connection solely to read board identity would be an extra, unaccounted-for hardware touch outside the orchestrator-only contract.
- `chip_id_actual`/`chip_id_mismatch_reason` are recovered by parsing the id step's `StepResult.reason` string (`"chip-ID mismatch: expected 0x.., detected 0x.."`, the only place `chip_test._dispatch_id` records the detected id today) rather than adding a new field to `StepResult` — keeps 112-01's already-landed `chip_test.py` schema untouched, per this plan's read-only relationship to that module.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Regenerated the `dev --help` characterization snapshot**
- **Found during:** Post-Task-2 full-suite verification
- **Issue:** Registering the new `dev test` subcommand legitimately changes `firestarter dev --help`'s output (a new line for `test` in the subcommand listing), which broke the pinned `tests/__snapshots__/test_characterization.ambr` snapshot for `test_help_dev`.
- **Fix:** Regenerated via `pytest tests/test_characterization.py::test_help_dev --snapshot-update`; diffed the change (single additive line, `test  Run the community chip-validation sweep for CHIP...`) before committing to confirm no unrelated drift.
- **Files modified:** `firestarter_app/tests/__snapshots__/test_characterization.ambr`
- **Verification:** `pytest tests/test_characterization.py -q` green; diff reviewed and minimal.
- **Committed in:** `009c296`

---

**Total deviations:** 1 auto-fixed (Rule 3 - blocking, snapshot drift caused directly by this plan's own change).
**Impact on plan:** Necessary and expected consequence of adding a new subcommand; no scope creep.

**Structural note (not a Rule 1-4 deviation):** Task 1 and Task 2 of this plan were committed together as a single commit (`ccfb7e6`) instead of two separate task commits. Both tasks modify the same contiguous `dev_test` function body in `cli_handlers.py` (Task 1: decorators/flags/is_uv/plan-derive/exit-code skeleton; Task 2: sampler thunk/TTY prompts/report assembly/artifact write) — there is no meaningful intermediate state where Task 1's code compiles and passes its own acceptance criteria independently of Task 2's additions (e.g., the exit-code test needs `run_plan`'s results, which need the sampler wiring to be destructive-run-correct). Each task's behavior was still verified independently via manual CliRunner smoke scripts before combining into the single commit. This mirrors the same kind of plan-structure note 112-01's SUMMARY recorded for its own TDD gate sequencing.

## Issues Encountered
- Initial attempt to test TTY-gating with `unittest.mock.patch("sys.stdin.isatty", return_value=True)` silently failed (patched value never took effect) because `click.testing.CliRunner.invoke()` replaces `sys.stdin` with its own I/O stream object for the duration of the invocation — the patch applied to the pre-invocation `sys.stdin` object does not survive. Resolved by factoring the check into a private `_is_interactive()` function that tests patch directly (`patch("firestarter.cli_handlers._is_interactive", return_value=True)`), which does survive `CliRunner.invoke()`. This is now documented in the function's own docstring for the next plan (112-03) that will write the codified pytest module.
- `M8720` (the sampler test seam's default chip from 112-01) has a chip-id sentinel of `0` in the DB, so its `id` step is always `NA` — a mock `check_eprom_id` return value has no effect on its verdict. Used `AS29F002T` (which has a real chip-id) instead when manually verifying the chip-ID-mismatch → exit 1 path.
- `tests/test_audit_coverage_matrix.py::TestAuditCoverageMatrix::test_golden_file_matches` fails both before and after this plan's changes (confirmed via `git stash` + rerun) — pre-existing, unrelated drift in the v1.3 coverage-matrix golden fixture. Logged to `112-02-deferred-items.md`, not fixed (out of scope).

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- `dev test <chip>` is fully wired end-to-end and independently verified via manual CliRunner smoke tests covering SC1 (registration/flags), SC2 (destructive vs non-destructive plan shape), SC3/D-01 (3-way exit incl. chip-ID mismatch and N<M), D-02/D-03 (TTY gating + `-y` scope), D-04 (sampler thunk + standalone read), and D-05 (dual-artifact gating).
- Plan 112-03 can now: (a) repoint `check_devtest_orchestrator.py`'s `_DEVTEST_CLI_HANDLER` constant at the real `cli_handlers.py` location (this handler lives there, not a separate `dev_test_cli.py`, per the pattern map) and de-stub its scope-tolerance, and (b) write the dedicated `tests/test_dev_test_cmd.py` CliRunner unit-test module — this plan intentionally left that codified test file to 112-03 per the plan's own `files_modified` split, and the `_is_interactive` patch seam documented above is exactly what that test module should use.
- No blockers. `ruff check`/`ruff format --check`/`python tools/check_mypy_watermark.py` all green on `cli_handlers.py`; `python tools/check_devtest_orchestrator.py` exits 0 (still scanning only `chip_test.py`, as expected pre-112-03); full `pytest tests/` suite green except the one pre-existing, unrelated `test_audit_coverage_matrix.py` failure (deferred, not this plan's origin).

## Self-Check: PASSED

- FOUND: firestarter_app/firestarter/cli_handlers.py
- FOUND: .planning/phases/112-dev-test-handler-wiring/112-02-SUMMARY.md
- FOUND: commit ccfb7e6 (Task 1+2, firestarter_app submodule)
- FOUND: commit 009c296 (snapshot update, firestarter_app submodule)
- FOUND: commit d5c49fc (docs: complete plan, meta-repo)

---
*Phase: 112-dev-test-handler-wiring*
*Completed: 2026-07-03*
