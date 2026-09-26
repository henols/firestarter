---
phase: 127-host-dfu-installer
plan: 04
subsystem: host-cli
tags: [click, cli, channel-gating, pytest-subprocess, syrupy, snapshot-testing]

# Dependency graph
requires:
  - phase: 127-01
    provides: "feature/py32f071-fw-install @ 4ee64a1 merged onto v1.23-py32f071-integration — _ALL_BOARDS, _BOARD_CHOICES, _PY32_ENABLED, --usb-id/--dfu-probe options, channel.py all exist on the branch"
provides:
  - "_reject_py32_only_option(name, given) — the single shared refusal mechanism for py32-only CLI options, closing the live --usb-id-accepted-on-stable gap (HOST-02)"
  - "tests/test_py32_channel_gating.py — subprocess-per-simulated-version harness proving channel gating both ways (HOST-08), plus Criterion 5's import-time-by-construction proof, the helper's in-process truth table, and the one-code-path source-scan guard"
  - "tests/test_characterization.py::test_help_fw fixed for both release channels — the app suite is 1230/1230 green again"
affects: [127-05, 127-06, 127-07, 127-08, 127-09, 127-10, 127-11, 127-12]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "One subprocess per simulated version: patch firestarter.__version__ before the version-reading module (cli_handlers) is ever imported in that child process, guarded by the child's own sys.modules pre-assertion. Import-time computation becomes a structural fact, not an assertion about a mock."
    - "click.testing.CliRunner forces click.formatting.FORCED_WIDTH = 80, which wraps --help text differently than a real subprocess's unforced width (shutil.get_terminal_size() -> 80, then HelpFormatter subtracts 2 -> effective width 78). Calling cli.main() directly with stdout redirected reproduces the real, unforced wrapping — needed anywhere a golden --help snapshot must match the actual installed entry point byte-for-byte."
    - "One shared refusal helper reading a module global at call time (not a captured default) — directly unit-testable via monkeypatch while the Click command surface built at import time stays frozen."

key-files:
  created:
    - firestarter_app/tests/test_py32_channel_gating.py
  modified:
    - firestarter_app/firestarter/cli_handlers.py (_reject_py32_only_option + two call sites; nested --dfu-probe-only refusal removed)
    - firestarter_app/tests/test_characterization.py (test_help_fw now simulates both channels; added-scope fix, not in the original plan)
    - firestarter_app/tests/__snapshots__/test_characterization.ambr (test_help_fw -> test_help_fw[test_help_fw_stable] + test_help_fw[test_help_fw_prerelease]; stable body byte-identical to the prior golden)

key-decisions:
  - "_reject_py32_only_option reads _PY32_ENABLED at call time (module global), not a captured default — required for in-process monkeypatch unit tests while the Click surface stays import-frozen"
  - "Channel-gating harness uses functools.lru_cache (not functools.cache) per the plan's explicit naming, with a targeted # noqa: UP033 rather than switching to the ruff-preferred equivalent"
  - "test_help_fw's fix calls cli_handlers.cli.main() directly instead of click.testing.CliRunner, because CliRunner's forced width=80 wraps text differently than the real, unforced firestarter fw --help subprocess this file otherwise characterizes via run_firestarter() — confirmed by measuring both against the pre-existing stable snapshot until they matched byte-for-byte"
  - "test_help_fw's two channel snapshots are named (snapshot(name=...)), following this file's own pre-existing convention (test_info_known_chip's stderr snapshot) rather than pytest.mark.parametrize, which would have produced a different naming scheme"

requirements-completed: []  # HOST-02/HOST-08 intentionally left unticked — only Plan 127-12 may tick HOST-01..HOST-08 (Phase-116 4x premature-tick guard)

coverage:
  - id: D1
    description: "--usb-id is rejected on a stable channel exactly as --dfu-probe already is, through one shared _reject_py32_only_option() code path"
    requirement: HOST-02
    verification:
      - kind: unit
        ref: "tests/test_py32_channel_gating.py::test_simulated_stable_usb_id_rejected"
        status: pass
      - kind: unit
        ref: "tests/test_py32_channel_gating.py::test_simulated_stable_dfu_probe_rejected"
        status: pass
      - kind: unit
        ref: "tests/test_py32_channel_gating.py::test_reject_py32_only_option_disabled_and_given_raises_usage_error"
        status: pass
      - kind: unit
        ref: "tests/test_py32_channel_gating.py::test_refusal_message_and_helper_occur_exactly_once_and_three_times"
        status: pass
    human_judgment: false
  - id: D2
    description: "Channel gating proven both ways in one test module via one subprocess per simulated version, with an explicit import-time-by-construction assertion (ROADMAP Criterion 5)"
    requirement: HOST-08
    verification:
      - kind: unit
        ref: "tests/test_py32_channel_gating.py::test_board_choices_are_computed_at_import_not_cached_across_a_version_change"
        status: pass
      - kind: unit
        ref: "tests/test_py32_channel_gating.py::test_simulated_prerelease_board_choices_and_flag"
        status: pass
      - kind: unit
        ref: "tests/test_py32_channel_gating.py::test_simulated_prerelease_dfu_probe_and_usb_id_not_refused"
        status: pass
    human_judgment: false
  - id: D3
    description: "Added scope (approved, beyond this plan's own tasks): tests/test_characterization.py::test_help_fw made correct on both release channels; full app suite green with 0 failures"
    verification:
      - kind: unit
        ref: "pytest tests/test_characterization.py::test_help_fw -q -> 1 passed"
        status: pass
      - kind: unit
        ref: "pytest tests/ -q --no-cov -> 1230 collected / 1230 passed / 0 failed"
        status: pass
    human_judgment: false

# Metrics
duration: 45min
completed: 2026-08-01
status: complete
---

# Phase 127 Plan 04: Close the `--usb-id` Gap and Prove Channel Gating Both Ways Summary

**One shared `_reject_py32_only_option()` closes the live `--usb-id`-accepted-on-stable gap; `tests/test_py32_channel_gating.py` proves channel gating both ways via one subprocess per simulated version; and, as approved added scope, `test_help_fw` — broken by 127-01's merge — is fixed for both channels, restoring the app suite to 1230/1230 green.**

## Performance

- **Duration:** ~45 min
- **Completed:** 2026-08-01
- **Tasks:** 3/3 plan tasks + 1 added-scope task, all executed
- **Files modified:** 4 (1 source, 2 test, 1 snapshot)

## Accomplishments

- Added `_reject_py32_only_option(name: str, given: bool) -> None` to `firestarter/cli_handlers.py`, reading `_PY32_ENABLED` at call time, and routed both `--usb-id` and `--dfu-probe` through it unconditionally, before either option is consumed. Removed the nested refusal that previously covered only `--dfu-probe`. Live-measured: on a simulated stable build, `fw --usb-id 1a86:8012 --list` now exits **2** with `no such option: --usb-id` (previously exit 0); `fw --dfu-probe` is unchanged at exit 2.
- `grep -c '_reject_py32_only_option' firestarter/cli_handlers.py` == 3 (one definition, two call sites); `grep -c 'no such option' firestarter/cli_handlers.py` == 1 (the single shared code path).
- Created `tests/test_py32_channel_gating.py` (14 tests): a `functools.lru_cache`-wrapped `_run_cli(version, argv)` harness spawning one `python -c` child per `(version, argv)` pair, patching `firestarter.__version__` before `firestarter.cli_handlers` is ever imported in that process, guarded by the child's own `"firestarter.cli_handlers" not in sys.modules"` pre-assertion. Covers both directions (simulated stable `3.0.0` and simulated pre-release `3.0.0b1`), the import-time-by-construction proof quoting ROADMAP Criterion 5 verbatim, the helper's four-case truth table in-process via monkeypatch, and the one-code-path source-scan guard (behind a non-vacuity precondition).
- No `importlib.reload`, no skip marker, no `ALLOWED_SKIP_REASONS` entry added. `tests/test_skip_census.py` still passes with its existing 4 allow-list entries.
- **Added scope (operator-approved, beyond this plan's own tasks):** fixed `tests/test_characterization.py::test_help_fw`, which 127-01's merge broke (adding `py32f071` to `_ALL_BOARDS` made `fw --help`'s `--board` choices and the `--usb-id`/`--dfu-probe` options channel-dependent, but the one stored golden was pinned against whichever channel happened to be pip-installed). Fixed by simulating both channels via a new `_run_fw_help_at_version()` helper reusing this plan's subprocess-per-simulated-version mechanism, with two named snapshots (`test_help_fw_stable` / `test_help_fw_prerelease`) replacing the single channel-blind one. The stable snapshot's body is byte-identical to the prior golden.
- Full app suite: **1230 collected / 1230 passed / 0 failed** (was 1215/1216 after 127-01's merge). `ruff check`, `ruff format --check`, and the mypy watermark (1 error vs. watermark 35) all pass.
- No requirement checkbox in `.planning/REQUIREMENTS.md` was ticked (verified: HOST-01..HOST-08 all still `[ ]` Pending). `/workspaces/firestarter` (firmware repo) `git status --porcelain` unchanged throughout.

## Task Commits

1. **Task 1: One shared `_reject_py32_only_option` helper, called for both py32-only options** — `4b1165d` (feat)
2. **Task 2: `tests/test_py32_channel_gating.py` — the subprocess harness and both directions** — `19b41ca` (test)
3. **Task 3: Import-time-by-construction proof, the in-process helper unit tests, and the one-code-path guard** — `86cbfce` (test)
4. **Added scope: fix `test_help_fw` for both release channels** — `7e2459a` (fix)

**Meta-repo tracking commit:** pending (this SUMMARY + gitlink bump, committed next per `<final_commit>`)

## Files Created/Modified

- `firestarter_app/firestarter/cli_handlers.py` — `_reject_py32_only_option()` + two call sites; removed the nested `--dfu-probe`-only refusal it replaces
- `firestarter_app/tests/test_py32_channel_gating.py` — new; 14 tests, subprocess-per-simulated-version harness + import-time proof + helper truth table + one-code-path guard
- `firestarter_app/tests/test_characterization.py` — `test_help_fw` rewritten to simulate both channels via a new `_run_fw_help_at_version()` helper; module docstring gets a short note explaining the exception to D-01
- `firestarter_app/tests/__snapshots__/test_characterization.ambr` — `test_help_fw` entry replaced by `test_help_fw[test_help_fw_stable]` (byte-identical body to the prior golden) and `test_help_fw[test_help_fw_prerelease]` (new)

## Decisions Made

- `_reject_py32_only_option` reads `_PY32_ENABLED` at call time rather than capturing it as a default argument — the one property that makes it both a frozen-at-import Click surface AND a directly monkeypatch-testable function.
- Kept `functools.lru_cache(maxsize=None)` with a targeted `# noqa: UP033` rather than switching to `functools.cache`, because the plan names `lru_cache` explicitly as the required mechanism.
- Fixed `test_help_fw` by calling `cli_handlers.cli.main()` directly (stdout redirected) instead of `click.testing.CliRunner`, after discovering live that `CliRunner.isolation()` forces `click.formatting.FORCED_WIDTH = 80`, which wraps `--help` text one word later per line than the real, unforced `firestarter fw --help` subprocess (a non-tty falls back to `shutil.get_terminal_size()` → 80 columns, then Click's `HelpFormatter` subtracts 2 → effective width 78). This was measured, not assumed: an initial CliRunner-based draft produced a byte-for-byte different wrap on the `--pre` option line versus the pre-existing golden, and switching to `cli.main()` directly resolved it exactly.
- Used `snapshot(name=...)` for the two channel variants (this file's own pre-existing convention, see `test_info_known_chip`'s stderr snapshot) rather than `pytest.mark.parametrize`, keeping the naming scheme consistent with the rest of the file.

## Deviations from Plan

### Approved Added Scope (not a deviation rule 1-4 — explicitly assigned by the orchestrator)

**1. Fixed `tests/test_characterization.py::test_help_fw` for both release channels**
- **Found during:** Wave 1 (127-01), carried forward as this plan's assigned added scope.
- **Issue:** 127-01's merge added `py32f071` to `_ALL_BOARDS`, making `fw --help`'s `--board` choices and the `--usb-id`/`--dfu-probe` options channel-dependent. The one stored golden (captured pre-py32f071, at Phase 120) could only ever be correct for one channel, and this checkout (`3.0.0b14`, a pre-release) diverges from it in **more than the `--board` line**: the real diff also adds `--usb-id` and `--dfu-probe` to the rendered help text, a larger surface than the "just the board choices" framing in the added-scope brief anticipated.
- **Fix:** Built `_run_fw_help_at_version(version)`, reusing this plan's own subprocess-per-simulated-version mechanism, and rewrote `test_help_fw` to assert both channels against two named snapshots. Discovered along the way that `click.testing.CliRunner` (the natural first choice, since the channel-gating harness in this same plan uses it) cannot be reused unmodified here: its forced `--help` width of 80 columns disagrees with the real subprocess entry point's unforced width of 78, so `_run_fw_help_at_version` calls `cli.main()` directly instead.
- **Verification:** `pytest tests/test_characterization.py::test_help_fw -q` → 1 passed; full app suite `pytest tests/ -q --no-cov` → 1230 passed / 0 failed; `ruff check`, `ruff format --check`, and the mypy watermark all pass.
- **Finding recorded (disproves 127-RESEARCH.md's C-1):** 127-RESEARCH.md's C-1 measured "a real `git merge --no-ff 4ee64a1` … 1216 collected · 0 failed … **Zero fixups**." That measurement does not hold on the real sibling-checkout tree: the merge, once landed for real in 127-01, left the suite at 1215/1216 with `test_help_fw` failing — a genuine, reproducible fixup, not a research-scratch-worktree artifact. Reproduction command: `cd /workspaces/firestarter_app && python -m pytest tests/test_characterization.py::test_help_fw -q`. Plan 127-12 is required to carry this C-1 correction forward at phase close, citing this reproduction command.
- **Files modified:** `firestarter_app/tests/test_characterization.py`, `firestarter_app/tests/__snapshots__/test_characterization.ambr`
- **Committed in:** `7e2459a`

---

**Total deviations:** 1 approved added-scope item (not a Rule 1-4 auto-fix — explicitly assigned by the orchestrator with its own rationale and constraints).
**Impact on plan:** All of this plan's own three tasks (HOST-02's shared refusal helper, HOST-08's both-directions proof, Criterion 5's import-time assertion) landed exactly as planned, with no deviations. The added-scope item restores the app suite to fully green and records, on the record, that C-1's "zero fixups" prediction does not survive contact with the real merge.

## Issues Encountered

None beyond the added-scope item documented above, which was itself the expected/assigned work, not an unplanned obstacle.

## User Setup Required

None — no external service configuration required.

## Claim Ceiling

This plan proves a CLI refusal behaviour and two release-channel simulations against mocked/simulated version strings, run in ordinary Python subprocesses. It proves nothing about a PY32F071 board: no PCB exists, and nothing here touches USB hardware, a bootloader, or an attached device. No sentence in this SUMMARY should be read as claiming the DFU install works end to end.

## Next Phase Readiness

- `firestarter/cli_handlers.py`'s py32-only option surface is now singly-gated; any later plan adding a third py32-only option can call `_reject_py32_only_option` directly rather than re-deriving the refusal.
- `tests/test_py32_channel_gating.py` exists and is available as a reference subprocess-per-simulated-version pattern for any later plan needing the same discipline (e.g. Plan 127-06's `collect_ignore` probe work, which needs its own import-time-sensitive proof).
- The app suite is back to fully green (1230/1230); Plan 127-12's closing session can re-run the full suite without inheriting this plan's fixup.
- **Open item for Plan 127-12 (C-1 correction):** 127-RESEARCH.md's C-1 "zero fixups" claim is disproved on the real sibling checkout, not just in a scratch worktree. 127-12 must carry this forward with the reproduction command above when it revisits C-1 at phase close.
- No requirement checkbox was ticked by this plan; HOST-01..HOST-08 remain `[ ]` Pending in `.planning/REQUIREMENTS.md`, correctly deferred to Plan 127-12.

## Self-Check: PASSED
