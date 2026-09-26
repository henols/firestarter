---
status: complete
phase: 71-validation-harness-matrix
source: [71-01-SUMMARY.md, 71-02-SUMMARY.md, 71-03-SUMMARY.md, 71-04-SUMMARY.md, 71-05-SUMMARY.md, 71-06-SUMMARY.md, 71-07-SUMMARY.md, 71-08-SUMMARY.md]
started: 2026-06-16T19:30:05Z
updated: 2026-06-16T19:31:30Z
---

## Current Test

[testing complete]

## Tests

### 1. dev validate-family — no-hardware SKIP-deferred path
expected: `firestarter dev validate-family eprom` with no hardware exits 0 and emits validation-matrix.json + .md with cells SKIP-deferred (leonardo) / N/A (uno328pb).
result: pass
evidence: "exit 0; both artifacts emitted; eprom/leonardo=SKIP-deferred, eprom/uno328pb=N/A (skip_boards)"

### 2. Validation matrix codegen drift gate
expected: Re-running `tools/gen_validation_header.py` produces a byte-identical validation_matrix.h (11 rows, VAL_FAMILY_COUNT 11, all 6 handlers present); test_gen_validation_header.py passes.
result: pass
evidence: "regenerated header byte-identical (diff -q clean); VAL_FAMILY_COUNT 11; 11 handler rows; test_gen_validation_header.py green"

### 3. check_dispatch.py CI gate (HARN-04)
expected: `python tools/check_dispatch.py` scans all 744 chips, exits 0, reports per-family VPP invariants enforced and 0 non_supported_dispatchable (non-hollow inverse detector).
result: pass
evidence: "exit 0; 744 chips scanned, 730 supported, 14 non-dispatchable, 0 non_supported_dispatchable, 0 dispatch regressions, 0 consistency violations; test_check_dispatch_invariants.py green"

### 4. Tier-2 host wire round-trip suites (HARN-01)
expected: 6 pytest suites prove each family's rep chip builds the correct algorithm field and dispatches to the correct configure_* handler with no serial port; SRAM never routes to configure_eprom (BLOCKER-2 hardware-safety guard).
result: pass
evidence: "all 6 test_val_wire_*.py suites green incl SRAM BLOCKER-2 (never dispatches configure_eprom)"

### 5. Non-vacuous PASS oracle (HARN-03)
expected: Oracle tests prove Leonardo gives authoritative PASS / other boards advisory, negative-control SHA mismatch → FAIL, uno328pb hard N/A, r1 ±25% precondition, and verdict is driven by write_cycle_eprom's real return code (not a source==source self-compare).
result: pass
evidence: "test_validate_oracle.py green; verdict driven by write_cycle_eprom return code + pass_type (authoritative/advisory); GAP-1 closed by 71-07"

### 6. Full app test suite + CI gates
expected: `pytest tests/` (640+ tests) passes, coverage ≥70%, mypy watermark gate OK, snapshots pass. Phase-71 files are ruff-clean.
result: pass
evidence: "640 passed; coverage 76.83% ≥ 70%; 29 snapshots pass; mypy watermark OK (35/35); phase-71 files ruff-clean (4 pre-existing I001/UP031 errors are in unrelated tools/catalog + audit_coverage_matrix files, not phase-71 scope)"

### 7. Tier-1 native Unity suites (pio test -e native)
expected: All 6 new test_val_* suites pass under `pio test -e native` (77/77 total battery); no linker errors with HOST_STUBS_RECORD_BUS off for existing suites.
result: skipped
reason: "PlatformIO + AVR toolchain not available in the devcontainer — cannot run `pio test`. Summary 71-04 records 77/77 native PASS at execution time; operator to re-confirm on bench (HIL evidence lands in Phase 73)."

### 8. Firmware flash byte-count unchanged (pio run)
expected: `pio run -e uno` and `pio run -e leonardo` show zero flash-byte delta vs pre-Phase-71 baseline — the test-only .inc lives under test/ and is excluded from production src_filter.
result: skipped
reason: "PlatformIO + AVR toolchain not available in the devcontainer — cannot run `pio run`. Summaries 71-01/71-04 record zero flash delta (Uno 72.4%, Leonardo 88.9%); operator to re-confirm on bench."

## Summary

total: 8
passed: 6
issues: 0
pending: 0
skipped: 2
blocked: 0

## Gaps

[none yet]
