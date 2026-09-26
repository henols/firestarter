# Deferred Items — Phase 99

## From Plan 99-01

### Pre-existing ruff findings in check_ledger.py / test_check_ledger.py (out of scope)

**Found during:** Task 3 (REFACTOR) ruff-clean verification.

**Findings:**
1. `test_check_ledger.py:32` — `F401 pytest imported but unused`. Confirmed present
   in the file BEFORE this plan's Task-1 edits (verified against
   `git show 1dfa162~1:.../test_check_ledger.py`).
2. `check_ledger.py` — `ruff format --check` reports the whole file "would be
   reformatted". Confirmed the diff (`ruff format --diff`) touches only
   pre-existing lines (line-wrapping of `_EVIDENCE_DIR`/`_MATRIX_DIR`,
   `_REQUIRED_BUCKETS`, `_VALID_STATUSES`, blank-line-before-def spacing,
   etc.) — none of the reformat hunks fall inside the `_assert_ledger02_d09`
   region this plan's Task 2 modified. Confirmed pre-existing against
   `git show 1dfa162~1:.../check_ledger.py`.

**Why deferred:** Per the executor's scope boundary rule, only auto-fix issues
directly caused by the current task's changes. These two findings predate
Phase 99 entirely (the gate script and its test file were authored in v1.16
and have carried this lint debt since). Fixing them here would touch
unrelated lines and expand the diff beyond this plan's stated
`files_modified` scope.

**Disposition:** Not fixed. Carry forward — a future cleanup plan (or the
next time either file is touched for an unrelated reason) should run
`ruff check --fix` + `ruff format` on both files as a standalone
`refactor(...)` commit.
