---
phase: 90-per-protocol-bench-validation-ledger
plan: "01"
subsystem: meta/ledger-tools
tags:
  - ledger
  - self-consistency
  - gate
  - stdlib-only
dependency_graph:
  requires:
    - ".planning/v1.15/bench/EVIDENCE.json"
    - "firestarter_app/tools/validation_matrix_spec.json"
  provides:
    - ".planning/v1.16/ledger/tools/check_ledger.py"
    - ".planning/v1.16/ledger/tools/test_check_ledger.py"
    - ".planning/v1.16/ledger/tools/fixtures/ledger_valid.json"
  affects:
    - "Plans 90-02, 90-04 (must pass this gate before ledger rows are accepted)"
tech_stack:
  added: []
  patterns:
    - "0/1/2 exit-code contract (WR-04) from diff_db.py"
    - "_load_db load-or-exit-2 helper"
    - "env-overridable path constants (FIRESTARTER_*_FILE seam)"
    - "collect-then-report-then-exit(1)-iff-nonempty main() structure"
key_files:
  created:
    - ".planning/v1.16/ledger/tools/check_ledger.py"
    - ".planning/v1.16/ledger/tools/test_check_ledger.py"
    - ".planning/v1.16/ledger/tools/fixtures/ledger_valid.json"
    - ".planning/v1.16/ledger/tools/fixtures/evidence_min.json"
    - ".planning/v1.16/ledger/tools/fixtures/matrix_min.json"
  modified: []
decisions:
  - "Checker placed under .planning/v1.16/ledger/tools/ (not firestarter_app/tools/) to avoid py3.11 CI ruff/mypy gates — per PATTERNS.md planner note and RESEARCH Pitfall 4"
  - "LEDGER-03 asserts exactly {0x0D,0x0E,0x10,0x27,0x29,0x34} are UNVERIFIED; 0x08 and 0x0B are open-defect-carried per RESEARCH §12-Bucket Row Identities"
  - "valid fixture uses abbreviated SHA cross-references (evidence_chip keys only, no 64-hex strings) — confirms D-04 compose-by-cross-reference is structurally enforced by the fixture itself"
metrics:
  duration: "15min"
  completed: "2026-06-26"
  tasks_completed: 2
  files_created: 5
---

# Phase 90 Plan 01: Ledger Self-Consistency Checker (Wave-0 Gate) Summary

**One-liner:** Stdlib-only ledger gate with pytest-proven 0/1/2 exit-code contract enforcing LEDGER-01 join keys, D-04 no-copy SHA guard, LEDGER-02/D-09 PASS structural constraint, and LEDGER-03 UNVERIFIED/defect-status rules.

## What Was Built

A self-contained Wave-0 gate tool and its test/fixture suite:

- **`check_ledger.py`** (273 lines) — The authoritative ledger consistency checker. Loads `PROTOCOL-LEDGER.json`, `EVIDENCE.json`, and `validation_matrix_spec.json` via env-overridable path constants. Runs three assertion groups:
  - **LEDGER-01:** All 12 buckets present; `matrix_family` join key resolves against the matrix spec (or null for 0x34); `evidence_chip` join keys resolve against EVIDENCE cells; no raw 64-hex SHA string in the serialized ledger (D-04 no-copy guard).
  - **LEDGER-02 / D-09:** Every PASS row has `oracle == "leonardo+Rev2.0"`, non-empty `p90_artifacts`, and both `p90_*_sha_matches_v115 == true`.
  - **LEDGER-03:** Exactly the 6 no-silicon buckets (0x0D/0x0E/0x10/0x27/0x29/0x34) carry `UNVERIFIED`; all `open_defects[].status_changed == false`; every row's `verification_status` is in the `{PASS, UNVERIFIED, FAIL-INVESTIGATE, open-defect-carried}` enum.

- **`test_check_ledger.py`** (167 lines) — 5 pytest tests covering all three exit paths via `subprocess.run()` with env-var fixture injection.

- **JSON fixtures** (3 files):
  - `ledger_valid.json` — All 12 buckets: 4 PASS rows (W29C020/SST39SF040/W27C512/FM1608), 6 UNVERIFIED no-silicon rows, 2 open-defect-carried rows (0x08/0x0B), 3 `open_defects` with `status_changed: false`. No 64-hex strings.
  - `evidence_min.json` — 8 EVIDENCE cells for the 4 on-hand chips.
  - `matrix_min.json` — 6 family entries matching the real spec (flash4/flash3/eprom/sram/eeprom28c/flash_intel).

## Verification Results

```
python -m py_compile .planning/v1.16/ledger/tools/check_ledger.py  → OK
python -m pytest .planning/v1.16/ledger/tools/test_check_ledger.py -q → 5 passed
python -m json.tool .planning/v1.16/ledger/tools/fixtures/ledger_valid.json → OK
grep -rE "[0-9a-f]{64}" .planning/v1.16/ledger/tools/fixtures/ledger_valid.json → (no match)
check_ledger.py against valid fixture → PASS exit 0
```

## Deviations from Plan

None - plan executed exactly as written.

## Threat Surface Scan

No new network endpoints, auth paths, or file access patterns introduced. The checker reads only local JSON files; no untrusted input. T-90-01/02/03/SC threats from the plan's threat model are all mitigated by the checker itself (D-09 constraint, D-04 SHA guard, exit-2 load gate).

## Known Stubs

None. The Wave-0 gate is complete and functional. The `ledger_valid.json` fixture intentionally holds **pre-bench** PASS rows (all four `p90_*_sha_matches_v115: true`) — these are fixture values for the checker test, not real bench verdicts. The real bench runs and PROTOCOL-LEDGER.json are authored in Plans 90-02 through 90-04.

## Self-Check: PASSED

- `.planning/v1.16/ledger/tools/check_ledger.py` — FOUND (273 lines ≥ 80)
- `.planning/v1.16/ledger/tools/test_check_ledger.py` — FOUND (167 lines ≥ 40)
- `.planning/v1.16/ledger/tools/fixtures/ledger_valid.json` — FOUND
- `.planning/v1.16/ledger/tools/fixtures/evidence_min.json` — FOUND
- `.planning/v1.16/ledger/tools/fixtures/matrix_min.json` — FOUND
- Commit d3b7ea6 (feat: check_ledger.py) — FOUND
- Commit 983bb23 (test: pytest + fixtures) — FOUND
