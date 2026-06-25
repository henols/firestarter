---
quick_id: 260625-f1g
slug: fix-write-cycle-consistency-check-output-dir
date: 2026-06-25
mode: quick
repo: firestarter_app (submodule)
branch: v1.15-bench-validation-of-operator-inventory
---

# Quick Task 260625-f1g: Group dev-diagnostic run folders under a parent dir

## Problem

`firestarter dev consistency-check` and `firestarter dev write-cycle` created their
auto-named per-run output folders directly in the current working directory:

- `consistency-check-<chip>-<board>-<TS>/`
- `write-cycle-<chip>-<board>-<TS>/`

Every bench run scattered a new timestamped folder in the launch directory
(visible as ~20 such folders cluttering the `/workspaces` git status).

## Decision

**Operator chose: subfolder in CWD** (over `~/.firestarter/runs/`).
When no explicit `--output-dir` is passed, nest the auto-named folder under a
single parent `firestarter-runs/` in the launch directory.

## Changes

1. `firestarter/eprom_operations.py`
   - Added module constant `DEFAULT_RUN_OUTPUT_DIR = "firestarter-runs"`.
   - `consistency_check_eprom` / `write_cycle_eprom`: when `output_dir is None`,
     nest the auto-named folder under `DEFAULT_RUN_OUTPUT_DIR`. Explicit
     `--output-dir` still honored verbatim. `mkdir(parents=True)` already
     creates the parent.
2. `firestarter/cli_handlers.py` — updated the two `--output-dir` help strings.
3. `tests/test_consistency_check.py` — regression test
   `test_default_output_dir_nested_under_runs_folder` locks the new behavior.
4. (meta repo) `.gitignore` — ignore `firestarter-runs/` + legacy
   `consistency-check-*/` / `write-cycle-*/` patterns.

## Verification

- `pytest tests/test_consistency_check.py` — green (incl. new test).
- Full suite: 672 passed; only the 2 documented board-present false-fails
  (`test_no_programmer_found_{read,erase}`) remain — unrelated to this change.
- `ruff check` + `ruff format --check` clean on all touched files.
- `validate-family` inherits the change via `write_cycle_eprom` (passes
  `output_dir` through; default-None path now grouped).
