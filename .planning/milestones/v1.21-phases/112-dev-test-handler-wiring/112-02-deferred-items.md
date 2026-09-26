# Deferred Items — Plan 112-02

Out-of-scope issues discovered during verification but NOT caused by this
plan's changes (`firestarter_app/firestarter/cli_handlers.py`). Logged per
scope-boundary rule; not fixed.

- `tests/test_audit_coverage_matrix.py::TestAuditCoverageMatrix::test_golden_file_matches`
  — fails both before and after this plan's changes (confirmed via `git
  stash` + rerun). The regenerated v1.3 coverage matrix has drifted from its
  committed golden fixture (`tests/golden/v1.3-COVERAGE-MATRIX.md`) for
  reasons unrelated to `dev test` (byte diff starts at index 1178, well
  outside any Phase 112 content). Pre-existing; `cli_handlers.py` is not
  read by this test's code path.
