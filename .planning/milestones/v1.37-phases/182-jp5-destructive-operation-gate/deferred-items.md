## Deferred Items

- Pre-existing `ruff check` failures in `firestarter_app/tools/audit_coverage_matrix.py`,
  `firestarter_app/tools/build_devtest_issue_corpus.py`, `firestarter_app/tools/catalog/codegen.py`,
  `firestarter_app/tools/catalog/codegen_vectors.py`, `firestarter_app/tools/snapshot_report_shapes.py`
  status: open
  **What:** `.venv311/bin/python -m ruff check firestarter/ tools/ tests/` reports 8 errors (I001
  unsorted imports x4, UP031 percent-format, E402 module-level-import-not-at-top x3) across these five
  files. None were created or modified by Phase 182 Plan 03 (confirmed via
  `git diff --stat -- <files>` returning empty against this plan's commits) — out of scope per the
  executor scope boundary rule. `ruff check` on the specific files this plan touched
  (`tools/diff_db.py`, `tests/test_diff_db_gate.py`, `tests/test_wire_dict_equivalence.py`) exits 0.
