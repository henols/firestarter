---
quick_id: 260625-f1g
slug: fix-write-cycle-consistency-check-output-dir
status: complete
date: 2026-06-25
repo: firestarter_app (submodule)
commit: bc55b29
files_changed: 3
tests: "672 passed (2 known board-present false-fails unrelated)"
---

# SUMMARY — Quick Task 260625-f1g

**Outcome:** ✅ Complete.

`dev consistency-check` and `dev write-cycle` now group their default auto-named
output folders under `firestarter-runs/` instead of dumping timestamped folders
directly in the launch directory. Explicit `--output-dir` unchanged.

## Commits

- `firestarter_app` @ `bc55b29` — fix(dev): group write-cycle/consistency-check
  runs under firestarter-runs/ (eprom_operations.py, cli_handlers.py,
  test_consistency_check.py).
- meta `.gitignore` — ignore `firestarter-runs/` + legacy stray-folder patterns.

## Verification

- New regression test `test_default_output_dir_nested_under_runs_folder` passes.
- Full app suite: 672 passed. The only failure (`test_no_programmer_found_read`)
  is the documented environment false-fail (a live board is on the saved config
  port); does not touch the read path this change modified.
- ruff lint + format clean.

## Notes

- The ~20 pre-existing stray `consistency-check-*/` / `write-cycle-*/` folders
  in `/workspaces` are now git-ignored but NOT deleted (left for operator to
  remove at will — they predate this change).
- Gitlink for `firestarter_app` left unbumped in the meta repo per the v1.15
  pin-until-beta-cut convention; the code commit lives on the
  `v1.15-bench-validation-of-operator-inventory` sub-repo branch.
