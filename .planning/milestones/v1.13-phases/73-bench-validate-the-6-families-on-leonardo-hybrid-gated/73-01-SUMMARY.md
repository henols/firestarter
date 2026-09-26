---
phase: 73-bench-validate-the-6-families-on-leonardo-hybrid-gated
plan: "01"
subsystem: bench-validation
tags: [val-matrix, tier1, tier2, skip-deferred, r1-precondition, eeprom28c, flash4, flash_intel]
dependency_graph:
  requires: [71-08-SUMMARY.md]
  provides: [val-results/eeprom28c/validation-matrix.json, val-results/flash4/validation-matrix.json, val-results/flash_intel/validation-matrix.json]
  affects: [73-02-PLAN.md, 73-03-PLAN.md, 73-04-PLAN.md]
tech_stack:
  added: []
  patterns: [SKIP-deferred-cell-emission, dev-validate-family-runner-reuse, r1-precondition-arming]
key_files:
  created:
    - firestarter_app/val-results/eeprom28c/validation-matrix.json
    - firestarter_app/val-results/eeprom28c/validation-matrix.md
    - firestarter_app/val-results/flash4/validation-matrix.json
    - firestarter_app/val-results/flash4/validation-matrix.md
    - firestarter_app/val-results/flash_intel/validation-matrix.json
    - firestarter_app/val-results/flash_intel/validation-matrix.md
  modified:
    - ~/.firestarter/config.json (host config — not repo file)
decisions:
  - "R1 precondition gate armed by directly writing r1=270000 to ~/.firestarter/config.json (firestarter config -r1 saves to Arduino EEPROM only, not to local JSON; config_manager.get_value reads from JSON)"
metrics:
  duration: "~3 minutes"
  completed: "2026-06-17T12:43:51Z"
  tasks_completed: 3
  files_created: 6
---

# Phase 73 Plan 01: Software Baseline + R1 Precondition + Chipless SKIP-Deferred Summary

**One-liner:** Confirmed all six families Tier-1/Tier-2 GREEN (28+26 tests), armed the R1 precondition gate (r1=270000 persisted to local config), and emitted three explicit SKIP-deferred Tier-3 matrix cells for the chipless families (eeprom28c/flash4/flash_intel).

## Tasks Completed

| Task | Name | Outcome | Commit |
|------|------|---------|--------|
| 1 | Re-confirm all six families' Tier-1 native + Tier-2 host wire cells GREEN | PASSED — 28 Tier-1 + 26 Tier-2 tests GREEN | (no source files changed) |
| 2 | Arm the live R1/R2 precondition (persist r1 ≈ 270000) and confirm Leonardo port identity | PASSED — Leonardo confirmed; R1=270000 in [202500,337500]; r1 persisted | (host config only) |
| 3 | Emit Tier-3 SKIP-deferred cells for the three chipless families (VAL-02, VAL-04, VAL-05) | PASSED — 3 artifacts emitted with SKIP-deferred verdict | c9a3319 (firestarter_app) |

## Task 1: Tier-1 Native + Tier-2 Host Wire Confirmation

**Command:** `cd /workspaces/firestarter && pio test -e native -f "native/avr/test_val_*"`

All six Tier-1 native suites PASSED (28 test cases total):

| Suite | Tests | Status |
|-------|-------|--------|
| native/avr/test_val_flash4 | 6 | PASSED |
| native/avr/test_val_flash3 | 4 | PASSED |
| native/avr/test_val_eprom | 6 | PASSED |
| native/avr/test_val_sram | 6 | PASSED |
| native/avr/test_val_flash_intel | 3 | PASSED |
| native/avr/test_val_eeprom28c | 3 | PASSED |
| **Total** | **28** | **ALL PASSED** |

**Command:** `cd /workspaces/firestarter_app && pytest tests/test_val_wire_*.py -v`

All six Tier-2 host wire suites PASSED (26 tests total):

| Suite | Tests | Status |
|-------|-------|--------|
| test_val_wire_eeprom28c.py | 4 | PASSED |
| test_val_wire_eprom.py | 4 | PASSED |
| test_val_wire_flash3.py | 4 | PASSED |
| test_val_wire_flash4.py | 4 | PASSED |
| test_val_wire_flash_intel.py | 4 | PASSED |
| test_val_wire_sram.py | 6 | PASSED |
| **Total** | **26** | **ALL PASSED** |

This satisfies ROADMAP SC#1 (Tier-1/Tier-2 GREEN for VAL-01..VAL-06) as a confirmed re-run at execution time.

## Task 2: Leonardo Identity + R1/R2 Precondition

**Controller identity:** `firestarter -p /dev/ttyACM0 fw` confirmed:
```
controller: leonardo, firmware 3.0.0b8
```

**Live calibration readback:** `firestarter -p /dev/ttyACM0 config` returned:
```
R1: 270000, R2: 44000, Override HW: Rev 2.0-class
```

R1=270000 is within the ±25% band [202500, 337500] — IN BAND (not a 999.1 confounder).

**R1 precondition arming:** The `firestarter config -r1 270000` command writes to Arduino EEPROM hardware only — it does NOT persist to `~/.firestarter/config.json`. The `dev validate-family` runner reads `r1` via `config_manager.get_value("r1", None)` which reads from the local JSON. To arm the gate, `r1: 270000` was written directly to `~/.firestarter/config.json`. Confirmed present after write:

```json
{
    "port": "/dev/ttyACM0",
    "r1": 270000
}
```

The Wave-2 Tier-3 precondition gate will now fire correctly.

## Task 3: SKIP-Deferred Cells Emitted

Three chipless families recorded as Tier-3 SKIP-deferred per D-02/D-13 (partial coverage is explicit, never silent). The `dev validate-family` runner's auto-path (no `--board/--chip/--source` args) emits the cells and exits 0.

**VAL-02 — eeprom28c (AT28C256, no chip on hand):**
- Artifact: `val-results/eeprom28c/validation-matrix.json`
- Cell: `{"family": "eeprom28c", "board": "leonardo", "tier": 3, "verdict": "SKIP-deferred", "reason": "no board/chip/source provided", "evidence_sha": null, "retry_count": 0}`
- uno328pb cell: N/A (in skip_boards)
- Status: Closed as Tier-1/Tier-2 GREEN + Tier-3 SKIP-deferred (D-13)

**VAL-04 — flash4 (AT29C040, no chip on hand):**
- Artifact: `val-results/flash4/validation-matrix.json`
- Cell: `{"family": "flash4", "board": "leonardo", "tier": 3, "verdict": "SKIP-deferred", "reason": "no board/chip/source provided", "evidence_sha": null, "retry_count": 0}`
- uno328pb cell: N/A (in skip_boards)
- Status: Closed as Tier-1/Tier-2 GREEN + Tier-3 SKIP-deferred (D-13)

**VAL-05 — flash_intel (AM28F010, no chip on hand):**
- Artifact: `val-results/flash_intel/validation-matrix.json`
- Cell: `{"family": "flash_intel", "board": "leonardo", "tier": 3, "verdict": "SKIP-deferred", "reason": "no board/chip/source provided", "evidence_sha": null, "retry_count": 0}`
- uno328pb cell: N/A (in skip_boards)
- Status: Closed as Tier-1/Tier-2 GREEN + Tier-3 SKIP-deferred (D-13)

All three companion `validation-matrix.md` files also emitted.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] R1 persistence via config command doesn't write to local JSON**
- **Found during:** Task 2
- **Issue:** The plan states "run `firestarter config -r1 270000` to persist r1 into local config so the precondition gate fires". However, `set_hardware_config()` in `hardware.py` only sends the `r1` value to Arduino EEPROM — it does not call `config_manager.set_value("r1", ...)`. The `dev validate-family` runner reads `r1` via `config_manager.get_value("r1", None)` from local JSON. Running the command left `~/.firestarter/config.json` without an `r1` key.
- **Fix:** Directly wrote `"r1": 270000` to `~/.firestarter/config.json` (host config, not a repo file). The precondition gate is now armed.
- **Files modified:** `~/.firestarter/config.json` (host config only)
- **Commit:** None (not a repo file)

## Threat Model Verification

| Threat | Status |
|--------|--------|
| T-73-01: ACM port identity verification | CLOSED — `controller: leonardo` confirmed on /dev/ttyACM0 |
| T-73-02: r1 precondition silently skipped | CLOSED — r1=270000 now in local config.json; gate fires for Wave-2 |
| T-73-03: false GREEN on RED software cell | N/A — all 54 tests (28 Tier-1 + 26 Tier-2) GREEN; no RED cell |
| T-73-04: SKIP recorded silently as omission | CLOSED — all 3 chipless families have explicit SKIP-deferred verdict in JSON artifacts |

## Success Criteria Verification

| Criterion | Status |
|-----------|--------|
| VAL-01..VAL-06 software half (Tier-1 + Tier-2) confirmed GREEN (ROADMAP SC#1) | PASSED — 28 + 26 = 54 tests GREEN |
| VAL-02 / VAL-04 / VAL-05 Tier-3 SKIP-deferred recorded (ROADMAP SC#2, D-13) | PASSED — 3 explicit SKIP-deferred cells with reason |
| R1/R2 precondition armed and recorded (ROADMAP SC#3 enabling condition) | PASSED — r1=270000 in ~/.firestarter/config.json; R1/R2 live readback recorded |

## Known Stubs

None — all three SKIP-deferred artifacts are complete explicit records with correct schema. The chipless families' SKIP is intentional and documented per D-02/D-13.

## Threat Flags

None — this plan emits no new network endpoints, auth paths, file access patterns, or schema changes at trust boundaries.

## Self-Check: PASSED

| Check | Result |
|-------|--------|
| val-results/eeprom28c/validation-matrix.json | FOUND |
| val-results/flash4/validation-matrix.json | FOUND |
| val-results/flash_intel/validation-matrix.json | FOUND |
| 73-01-SUMMARY.md | FOUND |
| firestarter_app commit c9a3319 | FOUND |
