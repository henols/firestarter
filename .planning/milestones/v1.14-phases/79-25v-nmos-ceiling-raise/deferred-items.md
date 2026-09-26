# Phase 79 Deferred Items

Out-of-scope discoveries during 79-02 execution (NOT fixed — pre-existing, unrelated to the ceiling raise).

## Pre-existing ruff errors/format issues in firestarter_app (py39 target)

Confirmed pre-existing by stashing the 79-02 changes — these 4 errors and 4 format
deltas are present on the clean tree at HEAD (`5d8a5b1`) and are NOT introduced by
the `RURP_VPP_CEILING_MV` raise. The files I edited (`tools/build_db.py`,
`tools/check_dispatch.py`) are ruff-clean at `--target-version py39`.

- `ruff check --target-version py39 .` → 4 errors (3 auto-fixable, 1 hidden) in:
  - `tools/catalog/codegen.py`
  - `tools/catalog/codegen_vectors.py`
  - `.github/scripts/update_version.py` (format)
  - `tools/check_mypy_watermark.py` (format)
- `ruff format --check --target-version py39 .` → would reformat:
  - `.github/scripts/update_version.py`
  - `tools/catalog/codegen.py`
  - `tools/catalog/codegen_vectors.py`
  - `tools/check_mypy_watermark.py`

Action: none in this plan (SCOPE BOUNDARY — only auto-fix issues directly caused by
the current task). Address in a dedicated lint-debt task if desired.
