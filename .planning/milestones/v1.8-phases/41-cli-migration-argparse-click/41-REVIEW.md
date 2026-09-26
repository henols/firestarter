---
phase: 41-cli-migration-argparse-click
reviewed: 2026-05-28T12:00:00Z
depth: standard
files_reviewed: 10
files_reviewed_list:
  - firestarter_app/firestarter/main.py
  - firestarter_app/firestarter/cli_handlers.py
  - firestarter_app/pyproject.toml
  - firestarter_app/autocomplete.md
  - firestarter_app/.github/workflows/ci.yml
  - firestarter_app/tests/test_cli_handlers.py
  - firestarter_app/tests/test_bug_characterization.py
  - firestarter_app/tests/test_firmware_install.py
  - firestarter_app/tests/test_consistency_check.py
  - firestarter_app/tests/__snapshots__/test_characterization.ambr
findings:
  critical: 1
  warning: 1
  info: 4
  total: 6
status: issues_found
---

# Phase 41: Code Review Report (re-review after `--fix --all` pass)

**Reviewed:** 2026-05-28
**Depth:** standard
**Files Reviewed:** 10
**Status:** issues_found

## Summary

Re-review of Phase 41 after the 5-commit `--fix --all` pass closed the 5
warnings from the prior review (WR-01..WR-05). Verification of each fix:

- WR-01 (`requirements.txt`): rewritten to `pyserial>=3.5 / requests>=2.20 /
  tqdm>=4.60 / click>=8.1 / rich>=14.0 / packaging>=21.0`; `argparse` and
  `argcomplete` removed. Matches `pyproject.toml [project].dependencies`
  byte-for-byte. **Closed.**
- WR-02 (`_setup_logging` ordering): `cli()` group callback now returns
  early when `ctx.obj` is a pre-built `AppContext` BEFORE calling
  `_setup_logging(verbose)` (`cli_handlers.py:274-277`). caplog isolation
  preserved. **Closed.**
- WR-03 (firmware-install mutex): per-option callback `_check_install_mutex`
  deleted; replaced with a single post-parse check at the top of `fw()`'s
  body (`cli_handlers.py:790-803`) raising `click.UsageError`. Deterministic
  error message regardless of option order. **Closed — but see CR-01:
  snapshot regen was skipped, breaking three snapshot tests in CI.**
- WR-04 (`id` shadows builtin): function renamed to `chip_id`, decorator
  remains `@cli.command(name="id")` (`cli_handlers.py:557`). **Closed.**
- WR-05 (`db._map_data` reach-through): new public wrapper
  `EpromDatabase.map_chip_record(ic, manufacturer)` added at
  `database.py:353-362`; cli_handlers.py:576 now calls
  `app.db.map_chip_record(...)`. **Closed.**

All 5 declared fixes landed in code. However, the WR-03 fix changed the
user-visible error string for `--pre` / `--firmware-version` / `--stable`
mutex violations AND the `fw --help` docstring, but the syrupy snapshots
pinning those exact strings were NOT regenerated. **This will fail CI**
the next time `pytest tests/test_characterization.py` runs.

Adjacent finding: two stale references to the removed
`_check_install_mutex` callback survive in test docstrings + an existing
snapshot — separate from CR-01 but in the same family.

The 7 Info-level findings from the prior review (IN-01..IN-07) are
unchanged — none were targeted by the fix pass. I've consolidated IN-04
into IN-01 (the requirements.txt thread now closed via WR-01) and re-cited
IN-01/IN-02/IN-03/IN-05/IN-07 as still-applicable, with IN-06 now
pertinent only to a post-py39 bump.

## Narrative Findings (AI reviewer)

## Critical Issues

### CR-01: WR-03 fix breaks three syrupy snapshots — `pytest` will fail in CI

**File:** `firestarter_app/tests/__snapshots__/test_characterization.ambr:1-18, 163-199`
**Issue:** The WR-03 fix (commit `86bd1b8`) replaced the per-option
`_check_install_mutex` callback (which raised `click.BadParameter`) with a
single post-parse `click.UsageError` inside `fw()`'s body. This changed:

1. The fw command's docstring (visible in `firestarter fw --help` output) —
   `cli_handlers.py:775-782` now reads:
   ```
   Implements TRAP #4 (3-way --pre / --firmware-version / --stable mutex via
   a single post-parse check at the top of the command body — WR-03; replaces
   the earlier per-option callback _check_install_mutex which depended on
   Click's left-to-right option-processing order) and TRAP #5 ...
   ```
   But the committed snapshot at `test_characterization.ambr:170` still
   contains the pre-fix text:
   ```
   Implements TRAP #4 (3-way --pre / --firmware-version / --stable mutex via
   per-option callback _check_install_mutex) and TRAP #5 ...
   ```

2. The user-visible error string for mutex violations changed. Before WR-03,
   `BadParameter` produced (snapshot `:11-18`):
   ```
   Error: Invalid value for '--stable': --stable is mutually exclusive with --pre.
   ```
   After WR-03, `UsageError` produces (verified by direct CliRunner call):
   ```
   Error: --pre is mutually exclusive with --stable.
   ```
   The `--firmware-version` variant similarly shifted from `Invalid value
   for '--firmware-version': --firmware-version is mutually exclusive with
   --pre.` to `Error: --pre is mutually exclusive with --firmware-version.`

Failing tests on the next `pytest` run:
- `tests/test_characterization.py::test_help_fw` (snapshot at `.ambr:163-199`)
- `tests/test_characterization.py::test_error_fw_pre_stable_mutex` (snapshot at `.ambr:11-18`)
- `tests/test_characterization.py::test_error_fw_pre_firmware_version_mutex` (snapshot at `.ambr:1-9`)

The mutex error message format is ALSO subtly less informative — the new
`f"--{set_channel_opts[0]} is mutually exclusive with --{set_channel_opts[1]}."`
always names "pre" first because `("pre", pre)` is the first tuple in the
filter list. The argparse-era error was order-sensitive but at least
identified the option Click was processing; the new form is deterministic
but also doesn't tell the user which option they typed first. The 3-pair
combinatorics are still covered (3 choose 2 = 3 cases) so this is not a
correctness bug — just a UX point. The PRIMARY defect is snapshot drift.

This is BLOCKER because Phase 41 ships with `ci.yml` running pytest +
coverage gate (`--cov-fail-under=50`). Snapshot drift fails before
coverage even runs.

**Fix:** Regenerate the three affected snapshots and commit the diff:
```bash
cd firestarter_app
pytest tests/test_characterization.py::test_help_fw \
       tests/test_characterization.py::test_error_fw_pre_stable_mutex \
       tests/test_characterization.py::test_error_fw_pre_firmware_version_mutex \
       --snapshot-update
git add tests/__snapshots__/test_characterization.ambr
git commit -m "test(41): regen syrupy snapshots after WR-03 mutex refactor"
```
Verify the new snapshots show:
- `test_help_fw`: docstring with "single post-parse check at the top of the
  command body — WR-03"
- `test_error_fw_pre_stable_mutex`: `Error: --pre is mutually exclusive with --stable.`
- `test_error_fw_pre_firmware_version_mutex`: `Error: --pre is mutually exclusive with --firmware-version.`

## Warnings

### WR-01: Stale docstring/comment references to deleted `_check_install_mutex` callback

**File:** `firestarter_app/tests/test_cli_handlers.py:432-433`,
`firestarter_app/firestarter/cli_handlers.py:670, 779`
**Issue:** WR-03 deleted the `_check_install_mutex` per-option callback
function but three docstring/comment references survived the fix commit:

1. `test_cli_handlers.py:432-433` — `test_fw_mutex_pre_and_firmware_version`'s
   docstring still claims:
   > "All three channel options share a per-option callback `_check_install_mutex`
   > that raises click.BadParameter (exit-2) when more than one is set."

   This is documentary lies — the test assertion (`exit_code == 2` and
   `"mutually exclusive" in result.output.lower()`) still passes because
   both implementations produce that exit code + substring, but a future
   reader following the docstring to find `_check_install_mutex` finds
   nothing.

2. `cli_handlers.py:670` (section banner comment) — describes "TRAPs #4 (3-way
   mutex enforced post-parse at top of fw() body — WR-03; previously per-option
   callback _check_install_mutex, now removed)". This one is accurate
   forward-pointer commentary; LEAVE as historical breadcrumb.

3. `cli_handlers.py:777` — the fw() docstring itself says "replaces the
   earlier per-option callback _check_install_mutex which depended on
   Click's left-to-right option-processing order". Again, accurate as
   migration history. LEAVE.

Item (1) is the only material problem — a test docstring describing a
function the test no longer exercises.

**Fix:** Update `test_cli_handlers.py:430-434` to:
```python
def test_fw_mutex_pre_and_firmware_version(runner: CliRunner) -> None:
    """TRAP #4 / D-13.4: --pre + --firmware-version exits 2 (mutually exclusive).

    Enforced by a single post-parse check at the top of fw()'s body
    (cli_handlers.py:790-803 — WR-03) raising click.UsageError when more
    than one of --pre / --firmware-version / --stable is set.
    """
```
The other two sites are accurate retrospective annotations.

## Info

### IN-01: Dead defensive `if eprom_details:` after `sys.exit(1)` (carry-over)

**File:** `firestarter_app/firestarter/cli_handlers.py:314-320`
**Issue:** Carried over verbatim from the prior review (IN-01). The handler
does:
```python
eprom_details = app.db.get_eprom(eprom)
if not eprom_details:
    logger.error(f"EPROM '{eprom}' not found in database.")
    sys.exit(1)

eprom_data_for_programmer = None
if eprom_details:                # <-- always True at this point
    eprom_data_for_programmer = app.db.convert_to_programmer(eprom_details)
```
Line 319's `if eprom_details:` is unreachable-as-false. The fix pass did
not target this. Not a regression — still latent.
**Fix:** Carry to Phase 42 cleanup. Same recommendation as before:
```python
if not eprom_details:
    logger.error(f"EPROM '{eprom}' not found in database.")
    sys.exit(1)
eprom_data_for_programmer = app.db.convert_to_programmer(eprom_details)
```

### IN-02: `cli_handlers.py` module docstring still describes pre-Wave-4 state (carry-over)

**File:** `firestarter_app/firestarter/cli_handlers.py:1-12`
**Issue:** Carried over verbatim from the prior review (IN-05). The
module docstring still reads:
```
Wave 2 lands the skeleton + 3 read-only commands (list/info/search); Wave 3
(this file's current state) lands the remaining 11 commands...
...
The entry point in main.py STAYS argparse until Wave 4 (Plan 41-04).
This module is feature-complete reviewable dead code from the user's
perspective until the entry-point swap.
```
Wave 4 has shipped (commit `3224f7e`, before the fix pass); main.py:9-12
documents itself as the post-swap stub re-exporting `cli` as `main`. The
cli_handlers.py docstring contradicts main.py and confuses readers.
**Fix:** Rewrite to describe the post-Wave-4 state. Same suggestion as
before:
```python
"""Click-based CLI handlers for firestarter (Phase 41 / v1.8).

This module is the production CLI surface; main.py re-exports `cli` as
`main` for the `firestarter` console-script entry point. The argparse
machinery in main.py was deleted in Plan 41-04.
"""
```

### IN-03: `_complete_eprom` instantiates a fresh `EpromDatabase` per completion invocation (carry-over)

**File:** `firestarter_app/firestarter/cli_handlers.py:87`
**Issue:** Carried over from prior review (IN-02). Each tab-completion
press triggers a subprocess that runs `_complete_eprom`, which constructs
`EpromDatabase()` (reads `chip_database.json`, ~1500 entries). This is
per-process, not per-key, and was inherited from the argcomplete-era
`EpromCompleter`. Not a correctness issue; no fix needed.
**Fix:** Acceptable as-is.

### IN-04: `ConfigManager` singleton port leak in integration test (carry-over)

**File:** `firestarter_app/tests/test_consistency_check.py:482-493`
**Issue:** Carried over from prior review (IN-07). The dispatch
integration test injects `-p /dev/null` via `sys.argv`; the cli() group
calls `config_manager.set_value("port", "/dev/null", persist=False)`.
`ConfigManager` is a singleton — `port=/dev/null` survives in-memory
across tests in the same pytest session. No flake observed yet.
**Fix:** Add a teardown that resets ConfigManager state, or move to
`monkeypatch` of ConfigManager internals. Not blocking — optional cleanup.

---

_Reviewed: 2026-05-28_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
