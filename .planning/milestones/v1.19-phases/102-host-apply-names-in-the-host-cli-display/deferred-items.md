# Deferred Items — Phase 102 Plan 01

## Out-of-scope pre-existing failure (not fixed — scope boundary)

**`tests/test_audit_coverage_matrix.py::TestAuditCoverageMatrix::test_golden_file_matches`**

- **Status:** FAILING before and after this plan's changes (confirmed via `git stash`
  against the pre-Task-1 commit — same byte-count drift, same diff index).
- **Symptom:** regenerated coverage matrix (186034 bytes) drifts from the committed
  golden fixture (184631 bytes); diff starts at index 1178 (` ` vs `|`, table
  formatting).
- **Why out of scope:** This test golden-file compares a generated coverage-matrix
  document unrelated to `ic_layout.py` protocol display names, `_get_protocol_info_structured`,
  or `get_chip_type_string`. Phase 102's `<files_modified>` scope is limited to
  `ic_layout.py` + `test_ic_layout.py` + the one `test_characterization.ambr` snapshot.
  Per the executor scope boundary rule, pre-existing failures in unrelated files are
  logged here, not fixed.
- **Action:** None taken. Full suite (`pytest tests/ --cov=firestarter --cov-fail-under=70`)
  passes at 78.12% coverage when this one pre-existing test is deselected; all
  Phase-102-relevant tests (`test_ic_layout.py`, `test_characterization.py`,
  `test_dispatch_mirror.py`, `test_check_dispatch_invariants.py`) are green.
