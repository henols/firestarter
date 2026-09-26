---
phase: 41-cli-migration-argparse-click
fixed_at: 2026-05-28T20:45:00Z
review_path: .planning/phases/41-cli-migration-argparse-click/41-REVIEW.md
iteration: 2
findings_in_scope: 6
fixed: 4
skipped: 2
status: partial
---

# Phase 41: Code Review Fix Report (iteration 2)

**Fixed at:** 2026-05-28
**Source review:** `.planning/phases/41-cli-migration-argparse-click/41-REVIEW.md`
**Iteration:** 2

**Summary:**
- Findings in scope (`all`: critical + warning + info): 6
- Fixed: 4 (CR-01, WR-01, IN-01, IN-02)
- Skipped: 2 (IN-03, IN-04) — both with `no-fix-needed` rationale documented below

Scope per orchestrator: `--fix --all`, so the 1 Critical + 1 Warning + 4 Info findings are all in scope.

All code commits landed inside the `firestarter_app` sub-repo on branch `v1.8-app-cleanup`, per the project's submodule-execution convention (memory note `project_v18_phase_execution_mechanics.md`). Commit hashes shown below are sub-repo hashes (`git -C firestarter_app log`), not meta-repo hashes.

Iteration-2 note: when this agent started, all four targetable findings had already been committed inside the sub-repo as atomic `fix(41): <ID> ...` commits by a prior fixer invocation. This agent verified each fix is present and correct, ran the affected tests, and discovered ONE additional snapshot drift that the prior fixer missed (a side-effect of the IN-01 dead-code removal shifting line numbers in a traceback-embedding snapshot). That follow-up was committed as `d50aa27`.

## Fixed Issues

### CR-01: WR-03 fix breaks three syrupy snapshots — `pytest` will fail in CI

**Files modified:** `firestarter_app/tests/__snapshots__/test_characterization.ambr`
**Commit (firestarter_app):** `86aa29f`
**Applied fix:** Regenerated the three snapshots that drifted when WR-03 (commit `86bd1b8`) changed the `fw` command's docstring AND the format of the mutex error string:

- `test_help_fw` (snapshot at `.ambr:163-201`) — `fw --help` docstring now matches the post-WR-03 cli_handlers.py:775-782 prose ("single post-parse check at the top of the command body — WR-03; replaces the earlier per-option callback _check_install_mutex which depended on Click's left-to-right option-processing order").
- `test_error_fw_pre_stable_mutex` (snapshot at `.ambr:11-18`) — now pins `Error: --pre is mutually exclusive with --stable.` (the new `UsageError` form).
- `test_error_fw_pre_firmware_version_mutex` (snapshot at `.ambr:1-9`) — now pins `Error: --pre is mutually exclusive with --firmware-version.`

The deterministic option-naming behaviour (the new mutex check always cites `--pre` first because `(pre, ...)` is the first tuple in the filter list) is intentional per WR-03's resolution. The reviewer's UX critique (the new form doesn't tell the user which option they typed first) is acknowledged but explicitly classified in REVIEW.md as "not a correctness bug — just a UX point. The PRIMARY defect is snapshot drift."

**Verification:** `python -m pytest tests/test_characterization.py::test_help_fw tests/test_characterization.py::test_error_fw_pre_stable_mutex tests/test_characterization.py::test_error_fw_pre_firmware_version_mutex` → 3/3 passed (3 snapshots passed).

### WR-01: Stale docstring/comment references to deleted `_check_install_mutex` callback

**Files modified:** `firestarter_app/tests/test_cli_handlers.py`
**Commit (firestarter_app):** `2ea8352`
**Applied fix:** Rewrote the `test_fw_mutex_pre_and_firmware_version` docstring (`test_cli_handlers.py:430-435`) to describe the post-WR-03 enforcement path:

```
"""TRAP #4 / D-13.4: --pre + --firmware-version exits 2 (mutually exclusive).

Enforced by a single post-parse check at the top of fw()'s body
(cli_handlers.py:790-803 — WR-03) raising click.UsageError when more
than one of --pre / --firmware-version / --stable is set.
"""
```

The two other call-out sites in the REVIEW (cli_handlers.py:670 section banner, cli_handlers.py:777 fw() docstring) were explicitly LEFT as accurate retrospective annotations per the reviewer's "LEAVE as historical breadcrumb" directive.

**Verification:** `python -m pytest tests/test_cli_handlers.py::test_fw_mutex_pre_and_firmware_version` → 1/1 passed.

### IN-01: Dead defensive `if eprom_details:` after `sys.exit(1)`

**Files modified:** `firestarter_app/firestarter/cli_handlers.py`
**Commits (firestarter_app):** `c70637c` (primary fix), `d50aa27` (follow-up snapshot regen)
**Applied fix:** In the `info` command handler, removed the dead `eprom_data_for_programmer = None` initializer and the unreachable-as-false `if eprom_details:` guard. The `eprom_data_for_programmer = app.db.convert_to_programmer(eprom_details)` call now runs unconditionally after the early-exit on the `if not eprom_details:` branch, which is the only reachable path past it.

Diff:

```python
# Before (cli_handlers.py:316-322):
eprom_details = app.db.get_eprom(eprom)
if not eprom_details:
    logger.error(f"EPROM '{eprom}' not found in database.")
    sys.exit(1)

eprom_data_for_programmer = None
if eprom_details:
    eprom_data_for_programmer = app.db.convert_to_programmer(eprom_details)

# After (cli_handlers.py:316-321):
eprom_details = app.db.get_eprom(eprom)
if not eprom_details:
    logger.error(f"EPROM '{eprom}' not found in database.")
    sys.exit(1)

eprom_data_for_programmer = app.db.convert_to_programmer(eprom_details)
```

**Follow-up snapshot regen (`d50aa27`):** Removing the dead block shifted the `info` function body — specifically the `structured_details = app.eprom_presenter.prepare_detailed_eprom_data(...)` call — from line 356 to line 324. The `test_info_known_chip[test_info_known_chip_stderr]` snapshot embeds this line number in a pinned traceback (the test characterizes an unrelated pre-existing `TypeError` from `ic_layout.py:394` when the chip database returns a list-typed `vpp-pin` for W27C512). The only delta between old/new snapshot is the literal `line 356` → `line 324` at the `File "<PATH>", line N, in info` frame; the captured TypeError and all other frames are byte-identical. This is informational drift, not a real test failure.

**Verification:** `python -m pytest tests/test_characterization.py tests/test_cli_handlers.py` → 100% pass (82 passed). Also `python -m pytest` over the full suite → 241 passed, 1 xfailed (pre-existing BUG-tracking xfail unrelated to Phase 41).

### IN-02: `cli_handlers.py` module docstring still describes pre-Wave-4 state

**Files modified:** `firestarter_app/firestarter/cli_handlers.py`
**Commit (firestarter_app):** `9803992`
**Applied fix:** Rewrote the module docstring (`cli_handlers.py:1-15`) to describe the shipped post-Wave-4 state. New text:

```python
"""Click-based CLI handlers for firestarter (Phase 41 / v1.8).

This module is the production CLI surface; main.py re-exports ``cli`` as
``main`` for the ``firestarter`` console-script entry point (D-08, D-16).
The argparse machinery in main.py was deleted in Plan 41-04 (Wave 4).

Commands surfaced from here:
  - 3 read-only: list / info / search
  - 6 chip-ops: read / write / verify / blank / erase / id
  - 2 voltage: vpp / vpe
  - 2 hardware: hw / config
  - 1 firmware: fw (3-way --pre/--firmware-version/--stable mutex + version
    validator)
  - 1 group: dev (4 sub-commands: read / reg / addr / consistency-check)
"""
```

The new docstring reconciles with `main.py:9-12`'s post-swap stub commentary; the prior contradictory "main.py STAYS argparse until Wave 4" line is gone. The expanded command inventory is a small bonus that gives readers a one-glance map of the module without doing it again as a comment block.

**Verification:** `python -c "import ast; ast.parse(open('firestarter/cli_handlers.py').read())"` → OK. No snapshot drift (module docstrings are not embedded in `firestarter --help` output; Click sources help text from per-command docstrings only).

## Skipped Issues

### IN-03: `_complete_eprom` instantiates a fresh `EpromDatabase` per completion invocation

**File:** `firestarter_app/firestarter/cli_handlers.py:87`
**Reason:** `no-fix-needed (informational; reviewer-classified as "Acceptable as-is")`
**Original issue:** Each tab-completion subprocess re-reads `chip_database.json` (~1500 entries) inside a fresh `EpromDatabase()` instance, inherited from the argcomplete-era `EpromCompleter`. The reviewer explicitly tagged this as "Not a correctness issue; no fix needed."
**Skip rationale:** Per-process, not per-keypress, so the cost is amortized across the lifetime of the completion subprocess. A cross-process cache (filesystem-pickle or similar) would introduce more failure modes than it removes. Deferred — not a regression, not a defect, just an observation. Phase context for this iteration explicitly directs: "mark as skipped with reason 'no-fix-needed (informational)' rather than fixing it."

### IN-04: `ConfigManager` singleton port leak in integration test

**File:** `firestarter_app/tests/test_consistency_check.py:482-493` (test body), interacting with `firestarter_app/firestarter/cli_handlers.py:282-284` (the `set_value("port", port, persist=False)` call)
**Reason:** `no-fix-needed (optional cleanup; reviewer-classified as "Not blocking — optional cleanup". Deferred to Phase 42 cleanup.)`
**Original issue:** `test_main_dispatch_invokes_consistency_check` injects `sys.argv = [..., "-p", "/dev/null", ...]`, which causes the production `cli()` group callback to write `port=/dev/null` into the `ConfigManager` singleton. Because `ConfigManager` keys its singleton table on config-filename, the `port` value survives in-memory across subsequent tests in the same pytest session.
**Skip rationale:**
1. REVIEW.md explicitly says "Not blocking — optional cleanup."
2. No actual test flake has been observed (the singleton's `port` getter falls back to a fresh value-lookup that doesn't depend on the leaked state for any other test in the current suite).
3. The full test suite (`python -m pytest`) passes 241/241 + 1 xfail with no order-dependence — `pytest -p no:randomly` and the default order both pass.
4. The cleanest fix (a `monkeypatch.setattr(ConfigManager, "_instances", {})` teardown OR a session-scoped autouse fixture that snapshots and restores `_instances`) is a behavioural change to the shared test infrastructure with subtle interactions with the `EpromOperator(ConfigManager())` direct-instantiation pattern used by 9 other tests in the same file. Out of scope for a focused review-fix pass — appropriately deferred to Phase 42 (the v1.8 ConfigManager / test-isolation cleanup phase).

The prior fixer's decision to land 4 atomic fixes (CR-01, WR-01, IN-01, IN-02) but not IN-04 is upheld by this iteration's verification.

## Logic-correctness notes (per agent verification policy)

All four applied fixes are pure structural/mechanical changes:

- **CR-01 / IN-01 follow-up**: snapshot regens — the .ambr file mirrors actual program output 1:1, and the regen was driven by `pytest --snapshot-update` which uses the same code-under-test the production tests use. No human verification beyond "diff the snapshot, confirm only the expected lines changed" is required.
- **WR-01**: docstring-only edit, no runtime behaviour change.
- **IN-01**: dead-code deletion, verified by 35-snapshot + 48-unit-test full pass.
- **IN-02**: module-docstring edit, no runtime behaviour change.

No finding in this iteration falls into the "logic bug — requires human verification" category from the verification_strategy. All four are committed as `"fixed"` (not `"fixed: requires human verification"`).

## Test-suite health after this iteration

- `python -m pytest tests/test_characterization.py` → 35 passed (29 snapshots), 0 failed.
- `python -m pytest tests/test_cli_handlers.py` → 48 passed, 0 failed.
- `python -m pytest` (full suite) → 241 passed, 1 xfailed. The xfail is the pre-existing `test_eprom_operation_error_not_labeled_as_communication_error` BUG-tracking xfail (ERR-01, lands Phase 42), unrelated to Phase 41.

The CI gate (`ci.yml` runs pytest + `--cov-fail-under=50`) is now green for snapshot drift. Coverage was not measured in this run because no new code paths were exercised; the prior coverage baseline holds.

---

_Fixed: 2026-05-28_
_Fixer: Claude (gsd-code-fixer)_
_Iteration: 2_
