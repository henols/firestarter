# Deferred Items — Phase 106

Out-of-scope discoveries logged per the executor scope-boundary rule (not fixed, not part of this plan's declared verification scope).

## From Plan 106-01

- **`tests/test_audit_coverage_matrix.py::TestAuditCoverageMatrix::test_golden_file_matches`** — FAILS identically on a clean pre-106-01 checkout (confirmed via `git stash`). Pre-existing golden-fixture drift unrelated to the `mem_type`/`type` removal. Out of scope for this plan; not touched.
- **`tests/test_chip_resolver.py::test_resolve_chip_hit_has_required_programmer_keys`** — Expected ripple from Task 1's `database.py` change (required-keys tuple still lists `"type"`). Plan 106-01's own text explicitly assigns ownership of this file's inversion to **Plan 03** ("do NOT touch `test_chip_resolver.py` in this plan") to avoid a file-write conflict. Left failing on purpose; Plan 03 will invert it.
