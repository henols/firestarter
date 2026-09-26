# Deferred Items — Phase 98 Plan 03

## Out-of-scope pre-existing test failure

- **Test:** `tests/test_audit_coverage_matrix.py::TestAuditCoverageMatrix::test_golden_file_matches`
- **Found during:** Plan 98-03 Task 3 (full `pytest -q` run, run as a scope-boundary
  sanity check beyond the plan's required verification commands).
- **Symptom:** Regenerated coverage matrix (186034 bytes) drifts from the golden
  fixture (184631 bytes) at byte index 1178.
- **Confirmed pre-existing:** Reproduces identically at commit `27da013` (the tip
  BEFORE this plan's two commits `3659121`/`9e3d17e`). Neither commit touches
  `tests/test_audit_coverage_matrix.py` or any file that feeds the audit coverage
  matrix generator — `git diff 27da013 HEAD --stat -- tests/test_audit_coverage_matrix.py`
  shows no delta.
- **Disposition:** Out of scope per the executor scope-boundary rule (only
  auto-fix issues directly caused by the current task's changes). Not fixed.
  Logged here per protocol; not blocking 98-03's success criteria (the plan's
  own verification commands — ruff/diff_db/check_dispatch/parity — all pass).

## Plan 98-05 — pre-existing blanket `ruff check .` failures (out of scope)

- **Found during:** Plan 98-05 Task 3 (full-repo `ruff check .` run as a
  scope-boundary sanity check beyond the plan's required verify commands).
- **Symptom:** 4 ruff errors, all in files untouched by 98-05:
  `tools/audit_coverage_matrix.py:37` (I001 unsorted imports),
  `tools/catalog/codegen.py:36` (I001), `tools/catalog/codegen_vectors.py:32`
  (I001) and `:189` (UP031 percent-format).
- **Confirmed pre-existing/out-of-scope:** `ruff check firestarter/ tests/`
  (the CI-scoped tree) and `ruff check tools/build_db.py tools/diff_db.py
  tools/check_dispatch.py` (the specific `tools/` files this phase touches)
  both pass clean. None of the 4 flagged files were modified by 98-01
  through 98-05.
- **Disposition:** Out of scope per the executor scope-boundary rule. Not
  fixed. 98-05's own required verify commands (`ruff check firestarter/
  tests/` + `ruff format --check firestarter/ tests/` per the plan's Task 3)
  pass; the plan does not require a blanket `ruff check .`.
