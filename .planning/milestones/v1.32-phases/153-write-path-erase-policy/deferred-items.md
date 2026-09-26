# Deferred Items

Out-of-scope discoveries logged rather than fixed, per the executor's scope-boundary rule
(only auto-fix issues directly caused by the current task's changes).

## 153-10

- **`ruff check .` (whole-tree, run to confirm plan-scoped files) surfaces 4 pre-existing
  errors in `tools/` files not touched by this plan**: `tools/audit_coverage_matrix.py`
  (I001 unsorted import block), `tools/catalog/codegen.py` (I001), `tools/catalog/codegen_vectors.py`
  (I001 + UP031 percent-format). None of these files are in this plan's `files_modified`
  list. Confirmed pre-existing by scope: `ruff check` scoped to this plan's four touched
  files (`firestarter/chip_test.py`, `tests/test_chip_test.py`, `tests/test_chip_test_sdp_leg.py`,
  `tests/test_chip_test_blank_check_order.py`) passes clean. Not fixed here.
