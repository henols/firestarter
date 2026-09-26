---
phase: 58-pinout-re-derivation-24-pin-eeprom-unblock
plan: "03"
subsystem: firestarter_app
tags: [pinouts, eeprom, safety, sr-1, gate-03, documentation]
dependency_graph:
  requires:
    - 58-02 (regenerated chip_database.json, 743 chips, 0 GATE-03 violations)
  provides:
    - GATE-03 verified against Plan 02 regenerated DB (0 violations / 743 chips)
    - SR-1 safety review in both layers (planning artifact + operator doc)
    - PIN-02 mechanical proof: no Flash/EEPROM chip routes to configure_eprom
    - PIN-03 closure: unblocked family CLI-reachable + SR-1-reviewed
  affects:
    - .planning/phases/58-pinout-re-derivation-24-pin-eeprom-unblock/58-SR-1-CHECKLIST.md
    - firestarter_app/doc/pinout-safety-review.md
tech_stack:
  added: []
  patterns:
    - Two-layer SR-1 doc pattern (planning artifact + operator subset, mirrors Phase 35 shield-revisions)
    - GATE-03 pinout-agnostic VPP-safety verification
    - D-09 citation convention (minipro SHA permalink, no per-chip list)
key_files:
  created:
    - .planning/phases/58-pinout-re-derivation-24-pin-eeprom-unblock/58-SR-1-CHECKLIST.md
    - firestarter_app/doc/pinout-safety-review.md
  modified: []
decisions:
  - "SR-1 scope per D-11 covers: DIP24_2816 (new, 9-item checklist), DIP24_2716 (chips moved OUT), DIP28_28C256 (12 algo corrections), DIP28_2764 (UV-EPROM guard preserved), DIP28_27512/27256 (pm_idx discriminator verified unchanged)"
  - "Assumption A1 (DIP24_2816 pin assignment is JEDEC-standard) flagged for operator datasheet confirmation; A2 (variant_lo=0x10 chips are genuine 5V EEPROMs) is very low risk with non-destructive failure mode if wrong"
  - "BENCH-01 (real-hardware write/program validation) deferred to v2 per REQUIREMENTS.md; Phase 58 satisfies source-correctness only"
metrics:
  duration: 5min
  completed: "2026-06-09"
  tasks_completed: 2
  tasks_total: 2
  files_modified: 2
---

# Phase 58 Plan 03: GATE-03 Verification + SR-1 Safety Review

**One-liner:** GATE-03 returns 0 violations on all 743 chips; AT28C04/16-family confirmed CLI-reachable with algo=0x0D; SR-1 safety review authored in both doc layers covering DIP24_2816 and every pinout the Phase 58 re-derivation changed.

## Summary

Plan 03 closes the safety gates for Phase 58.

### Task 1: GATE-03 Verification + CLI Reachability (PIN-02, PIN-03)

**GATE-03 result:**
```
PASS: all 743 chips have a valid dispatch path; 0 SRAM chips route to configure_eprom;
0 DIP28_2764 Flash/EEPROM chips route to configure_eprom;
0 Flash/EEPROM chips route to configure_eprom; 0 wire-key regressions
```

**CLI reachability (spot-checks):**
- `firestarter info AT28C16` — exits 0, type=EEPROM, algo=0x0D, pinout=DIP24_2816 ✓
- `firestarter info AT28C04` — exits 0, type=EEPROM, algo=0x0D, pinout=DIP24_2816 ✓
- `firestarter info AM28C16A` — exits 0, type=EEPROM, algo=0x0D, pinout=DIP24_2816 ✓

**Full test suite:** 516 passed, 0 failed (including all 36 Wave 0 tests).

Task 1 is verification-only — no files were created or modified. No commit needed for Task 1.

### Task 2: SR-1 Safety Review (PIN-03, D-10/D-11)

Commit `f822498` (firestarter_app): Created `doc/pinout-safety-review.md`.

Two-layer SR-1 documentation per D-10:

**Planning layer** (`58-SR-1-CHECKLIST.md`, meta-repo): Full audit trail. Covers:
- **DIP24_2816** (new): 9-item SR-1 checklist — vpp-pin absent, rw-pin=21=WE#, all 24 pins
  accounted for, pin 21 vs DIP24_2716 contrast documented, PASS verdict
- **DIP24_2716**: chips moved OUT reviewed (10 dangerous chips correctly migrated)
- **DIP28_28C256**: 12 algo corrections from 0x07→0x0D reviewed (VPP path removed, PASS)
- **DIP28_2764**: UV-EPROM guard retention reviewed (5V EEPROMs rerouted, UV-EPROMs unchanged, PASS)
- **DIP28_27512 / DIP28_27256**: pm_idx=22 variant_lo discriminator preserved (PASS)
- **DIP32 pinouts**: unchanged, pre-existing PASS
- Assumptions A1/A2 flagged for operator confirmation
- BENCH-01 deferral documented

**Operator layer** (`firestarter_app/doc/pinout-safety-review.md`, sub-repo): Strict subset covering:
- DIP24_2816 5V-only guarantee (no vpp-pin)
- GATE-03 0-violation proof (743 chips)
- configure_eeprom28c 5V-safety
- What changed in Phase 58 (summary table)
- BENCH-01 deferral
- Minipro citation (SHA a8efaedc)

## GATE-03 Violation Count

**0 violations / 743 chips** — PIN-02 mechanical proof satisfied.

## Changed Pinouts Under SR-1 Scope (D-11)

| Pinout | SR-1 Status |
|--------|-------------|
| DIP24_2816 (NEW) | PASS (A1 operator-confirmation flagged) |
| DIP24_2716 (chips moved OUT) | No review needed (definition unchanged) |
| DIP28_28C256 (12 algo corrections) | PASS (VPP path removed) |
| DIP28_2764 (UV-EPROM guard retained) | PASS |
| DIP28_27512 (discriminator preserved) | PASS |
| DIP28_27256 (discriminator preserved) | PASS |
| DIP32 family (unchanged) | Pass (pre-existing) |

## Commits

| Hash | Repo | Type | Description |
|------|------|------|-------------|
| `f822498` | firestarter_app | `docs(58-03)` | Add SR-1 safety review doc for DIP24_2816 + Phase 58 (PIN-03, D-10) |

Planning artifacts committed in final metadata commit (meta-repo).

## Deviations from Plan

None — plan executed exactly as written. Task 1 was verification-only (no file changes);
Task 2 created both required docs with correct content and two-layer lockstep.

## Known Stubs

None. The SR-1 review is complete for all pinouts in D-11 scope. Assumption A1 is flagged
as a forward-action item (operator datasheet confirmation), not a stub — the safety guarantee
holds regardless (GATE-03 provides the mechanical proof; A1 is belt-and-suspenders for the
pin-assignment itself).

## Threat Flags

None. The new `doc/pinout-safety-review.md` is documentation only — no new network endpoints,
auth paths, or schema changes.

## Self-Check: PASSED

Files verified:
- `/workspaces/.planning/phases/58-pinout-re-derivation-24-pin-eeprom-unblock/58-SR-1-CHECKLIST.md` — FOUND
- `/workspaces/firestarter_app/doc/pinout-safety-review.md` — FOUND
- Both contain "DIP24_2816" ✓
- Planning checklist contains "vpp-pin" ✓

Commits verified:
- `f822498` — FOUND (git -C firestarter_app log --oneline -1)

GATE-03: 0 violations ✓
CLI reachability: AT28C16, AT28C04, AM28C16A all exit 0 ✓
Full test suite: 516 passed, 0 failed ✓
