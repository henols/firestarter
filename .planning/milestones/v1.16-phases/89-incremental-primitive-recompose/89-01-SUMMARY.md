---
phase: 89-incremental-primitive-recompose
plan: "01"
subsystem: firmware
tags: [refactor, dedup, const-table, P7, flash-utils, eeprom28c, PRIM-02]
dependency_graph:
  requires: [88-05]
  provides: [P7-dedup-committed]
  affects: [firestarter/include/flash_utils.h, firestarter/src/proms/eeprom_28c.cpp]
tech_stack:
  added: []
  patterns: [refactor-under-test, delete-not-merge, per-step-gate]
key_files:
  created: []
  modified:
    - firestarter/include/flash_utils.h
    - firestarter/src/proms/eeprom_28c.cpp
decisions:
  - "P7 executed as delete-not-merge: tables verified byte-identical at execution time before edit"
  - "FLASH_ENABLE_WRITE_PROTECTION had zero callers — safe to delete"
  - "EEPROM_SDP_DISABLE single caller redirected to FLASH_DISABLE_WRITE_PROTECTION"
  - "Pre-existing firestarter_app .gitignore diff noted — not a source change, out of P7 scope"
metrics:
  duration: "8min"
  completed: "2026-06-26"
  tasks_completed: 2
  files_modified: 2
---

# Phase 89 Plan 01: P7 SDP / Const-Table Dedup Summary

P7 (PRIM-02) warm-up dedup: deleted dead `FLASH_ENABLE_WRITE_PROTECTION` from `flash_utils.h` (zero callers, byte-identical to `FLASH_ENABLE_WRITE`) and deleted local `EEPROM_SDP_DISABLE` from `eeprom_28c.cpp` (byte-identical to `FLASH_DISABLE_WRITE_PROTECTION`), redirecting its single caller to the shared table. All golden traces zero-diff, flash delta = 0 B.

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Delete FLASH_ENABLE_WRITE_PROTECTION + redirect EEPROM_SDP_DISABLE | firestarter@0052c42 | flash_utils.h, eeprom_28c.cpp |
| 2 | Per-step P7 gate — full native suite + flash delta + host gates + INV grep | (gate-run, no code change) | — |

## P7 Step Ledger (PRIM-06 input)

| Metric | Value |
|--------|-------|
| Baseline (Phase 88 close) | 25654 B |
| Post-P7 Leonardo flash | 25654 B |
| Delta | 0 B (well within +16 B gate — D-01 PASS) |
| Flash % | 89.5% |

## Gate Results

| Gate | Result | Detail |
|------|--------|--------|
| Full native suite (`pio test -e native`) | PASS | 102/102 tests green |
| In-filter golden traces (eeprom28c/flash3/flash4) | PASS | 22/22 PASS, zero-diff |
| Flash delta D-01 | PASS | 0 B (25654 → 25654 B, delta = 0) |
| `check_dispatch.py` | PASS | Exit 0, 0 dispatch regressions, 0 consistency violations (746 chips) |
| `diff_db.py` | PASS | Exit 0, 0 changed / 0 new / 0 missing (identity diff) |
| SAFE-06 host source change | PASS (pre-existing .gitignore note) | Only change in firestarter_app is a pre-existing `.gitignore` annotation (`consistency*`) — not a source file, not caused by P7 |
| INV-01..09 greppability (SAFE-02) | PASS | All 9 INV ids hit ≥ 3 files: INV-01=9, INV-02=3, INV-03=6, INV-04=4, INV-05=3, INV-06=3, INV-07=3, INV-08=3, INV-09=5 |

## Acceptance Criteria Verification

- `grep -rn FLASH_ENABLE_WRITE_PROTECTION firestarter/src/ firestarter/include/` → 0 matches (PASS)
- `grep -rn EEPROM_SDP_DISABLE firestarter/src/ firestarter/include/` → 0 matches (PASS)
- `grep -c FLASH_DISABLE_WRITE_PROTECTION firestarter/src/proms/eeprom_28c.cpp` → 1 (PASS)
- All three golden trace suites: 22/22 test cases green, zero-diff (PASS)

## Deviations from Plan

None — plan executed exactly as written. The pre-existing `.gitignore` change in `firestarter_app` was noted (not caused by P7; predates this plan; not a source-code change).

## Known Stubs

None.

## Threat Flags

None. P7 only deleted const data tables; no regulator routing, dispatch, or wire values were touched. `check_dispatch.py` confirmed 0 violations; `diff_db.py` confirmed identity diff.

## Self-Check: PASSED

- `firestarter/include/flash_utils.h` — modified (FLASH_ENABLE_WRITE_PROTECTION deleted)
- `firestarter/src/proms/eeprom_28c.cpp` — modified (EEPROM_SDP_DISABLE deleted + caller redirected)
- Commit `0052c42` exists in firestarter submodule on v1.16 branch
- All 102 native tests green
- Flash delta = 0 B (baseline 25654 / post 25654)
- Both host gates exit 0
- INV-01..09 all ≥ 3 files
