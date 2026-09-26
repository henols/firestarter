---
status: complete
phase: 90-per-protocol-bench-validation-ledger
source: [90-01-SUMMARY.md, 90-02-SUMMARY.md, 90-03-SUMMARY.md, 90-04-SUMMARY.md]
started: 2026-06-26T14:05:23Z
updated: 2026-06-26T14:09:00Z
---

## Current Test

[testing complete]

## Tests

### 1. Ledger Self-Consistency Checker Passes
expected: check_ledger.py exits 0; reports 12 rows, 3 open_defects, all LEDGER-01/02/03 + D-09 assertions satisfied (join keys resolve into EVIDENCE.json + validation_matrix_spec.json, no copied SHA, PASS rows carry oracle+artifacts)
result: pass

### 2. Protocol Ledger Holds All 12 Buckets With Correct Statuses
expected: PROTOCOL-LEDGER.json + .md each carry one row per all 12 protocol buckets — 2 PASS (0x05 W29C020, 0x28 FM1608), 2 FAIL-INVESTIGATE (0x06 SST39SF040, 0x07 W27C512), 6 UNVERIFIED no-silicon (0x0D/0x0E/0x10/0x27/0x29/0x34), 2 open-defect-carried (0x08, 0x0B). 3 open_defects (CR-01/FUT-06/FUT-03) all status_changed=false. JSON and MD mirror each other.
result: pass

### 3. Checker Test Suite Passes (Exit-Code Contract)
expected: `pytest .planning/v1.16/ledger/tools/test_check_ledger.py` → 5 passed; covers the 0/1/2 exit-code contract (valid→0, violation→1, missing file→2) via subprocess + env-var fixture injection.
result: pass

### 4. SAFE-04 Guards Present + Frozen World Intact
expected: Firmware under test is a296195. The VPP over-voltage guard is present at primitives.cpp:106 (`vpp_mv > handle->vpp_mv + 500`) and the host support_status guard is present in chip_resolver.py — both unmodified. Frozen-world gates (check_dispatch 0 violations, diff_db identity, 105/105 native tests) green; 2516 stays UNVERIFIED. No gitlink bump (pinned at b10).
result: pass

### 5. Bench Regression Recorded Honestly (LEDGER-02 / D-03)
expected: All 4 on-hand chips were bench-run on the recompose (a296195, Leonardo/Rev2.0). All 4 READ paths byte-identical to v1.15. Write-cycle: W29C020 (0x05) + FM1608 (0x28) PASS (byte-identical, auto-erase proven); SST39SF040 (0x06) + W27C512 (0x07) recorded FAIL-INVESTIGATE — a reproducible 12V-VPP write-path regression, NOT auto-passed (D-03). Per-dir SHA256SUMS committed as evidence. This matches what you observed at the bench.
result: pass

## Summary

total: 5
passed: 5
issues: 0
pending: 0
skipped: 0
blocked: 0

## Gaps

[none yet]
