---
phase: 76-spec-only-gaps-adapter-required-x88c64
plan: "01"
subsystem: host-db-pipeline
tags: [gap-closure, db-classification, build_db, named-rule-arm, tdd]
dependency_graph:
  requires: []
  provides: [named-AT28C04-arm, X88C64-reason-reword, regenerated-chip-db]
  affects: [chip_database.json, diff_db-gate, check_dispatch-gate]
tech_stack:
  added: []
  patterns: [named-rule-arm-in-build_db, alias-extraction-idiom, tdd-red-green]
key_files:
  created: []
  modified:
    - firestarter_app/tools/build_db.py
    - firestarter_app/tests/test_build_db_inclusion.py
    - firestarter_app/firestarter/data/chip_database.json
decisions:
  - "D-03 named arm fires AFTER Site B (not before) so its reason wins for any chip also matching Site B; proto_id NOT touched by the named arm. WR-01 correction: the matched AT28C04/16 chips carry 0x0D (VPP-free configure_eeprom28c) and never enter Site B — they are refused by support_status=adapter-required (host guard), not by proto_id demotion"
  - "D-02 X88C64P reason string: 'protocol not implemented: 0x34 (XICOR X88C64P — parallel DIP24 5V EEPROM, 8051 multiplexed-bus interface (ALE/WR/RD); feasible-candidate, handler not implemented)'"
  - "Test guard for AT28C16 uses 'AT28C04-ADAPTER.md' literal (not generic 'DIP24') to distinguish named-arm from Site B wording"
  - "diff_db reports 10-chip RULE_PHASE66 delta (9 adapter-required + X88C64P) — all reason-string-only, no support_status/dispatch change; accepted per plan Task 3"
metrics:
  duration: "~8 minutes"
  completed: "2026-06-18"
  tasks_completed: 3
  files_changed: 3
---

# Phase 76 Plan 01: Named AT28C04/AT28C16 Rule Arm + X88C64 Reason Reword Summary

**One-liner:** Named `_AT28C_DIP24_NAMES` rule arm in build_db.py classifies 14 AT28C04/AT28C16 aliases as adapter-required with explicit adapter-spec reference, plus X88C64P reason reworded to datasheet-accurate 8051 multiplexed-bus description.

## What Was Built

### GAP-01 (D-03): Named AT28C04/AT28C16 Rule Arm

Added `_AT28C_DIP24_NAMES` set with 14 chip-name aliases (`AT28C04`, `AT28HC04`, `AT28C04E`, `AT28C04F`, `AT28C16`, `AT28HC16`, `AT28HC16L`, `AT28C16E`, `AT28C16F`, `28C04A`, `28C04AF`, `28C16A`, `28C16AF`, `UPD28C04`) in `build_db.py`. The arm fires AFTER Site B so its named-arm wording (referencing `firestarter/doc/AT28C04-ADAPTER.md`) wins over any generic Site B reason. **WR-01 correction:** the chips this arm actually matches (DIP24_2816, proto_id `0x0D`) do NOT pass through Site B's 0x07/0x08/0x0B demotion at all — proto_id stays `0x0D` (a real, VPP-free `configure_eeprom28c` handler). Their in-host refusal comes from `support_status="adapter-required"` (host guard in `chip_resolver.resolve_chip`), not from proto_id demotion. The arm makes the classification explicit, declarative, and audit-friendly.

### GAP-02 (D-02): X88C64P Reason Reword

Replaced the old incorrect reason string `"protocol not implemented: 0x34 (XICOR NovRAM serial-parallel hybrid)"` with `"protocol not implemented: 0x34 (XICOR X88C64P — parallel DIP24 5V EEPROM, 8051 multiplexed-bus interface (ALE/WR/RD); feasible-candidate, handler not implemented)"`. The chip IS parallel (not serial-parallel); the old string was wrong on both axes. support_status stays `protocol-not-implemented`. No 0x34 firmware handler committed (D-01 preserved).

### Tests Added

Two new tests in `TestUnsupportedReasonStrings`:
- `test_at28c16_named_arm_reason_mentions_adapter_doc` — asserts AT28C16 adapter-required reason contains `'AT28C04-ADAPTER.md'` (named-arm wording)
- `test_x88c64p_reason_does_not_say_serial_parallel_hybrid` — regression guard against old wrong wording

### DB Regenerated

`chip_database.json` regenerated via `python tools/build_db.py` (codegen-driven, not hand-edited). 744 chips total unchanged. All 9 adapter-required chips now carry the named-arm reason. X88C64P reason is datasheet-accurate.

## Gate Results

| Gate | Result | Details |
|------|--------|---------|
| `diff_db.py` | PASS (exit 0) | 10-chip RULE_PHASE66 delta: 9 AT28C04/16 chips (reason text change) + X88C64P (reason reword); NO support_status or dispatch change for any chip |
| `check_dispatch.py` | PASS (exit 0) | 744 chips, 730 supported, 14 non-dispatchable; 0 violations; no chip newly supported |
| `pytest --cov-fail-under=70` | PASS | 642 tests green; 76.83% coverage (floor 70% held) |
| No 0x34 firmware handler | PASS | No edits to firestarter/src/; D-01 preserved |
| Codegen-driven DB | PASS | JSON produced by `python tools/build_db.py`; not hand-edited |

## Commits

| Hash | Type | Description |
|------|------|-------------|
| `10388b5` | test | Wave-0 RED tests: named-arm reason + X88C64 hybrid guard |
| `9c1e019` | feat | Named AT28C04/AT28C16 rule arm (D-03) + X88C64 reason reword (D-02) + DB regeneration |

All commits are inside the `firestarter_app/` submodule on branch `v1.13-algo-validation`.

## Deviations from Plan

### Auto-adjusted Issues

**1. [Ordering] Named arm placement: AFTER Site B (not before)**
- **Found during:** Task 2 implementation
- **Issue:** PATTERNS.md showed the named arm before Site B. Placing it after Site B guarantees the named-arm reason wins for any chip that *also* satisfies Site B's predicate (DIP24 + 0x07/0x08/0x0B + electrically-erasable).
- **Fix:** Moved the named arm to AFTER Site B; both set `adapter-required` so status stays correct, and the named arm's reason wins. **Correction (review WR-01):** the chips actually matched by this arm (AT28C04/16 family, DIP24_2816) carry proto_id `0x0D` (EEPROM_POLL → `configure_eeprom28c`, VPP-free) straight from infoic.xml — they do NOT match Site B's 0x07/0x08/0x0B predicate, so Site B does not fire for them and proto_id stays `0x0D` (NOT demoted to `NON_DISPATCHABLE_ALGO`). They are refused in-host by `support_status="adapter-required"` (host guard in `chip_resolver.resolve_chip`), not by proto_id demotion; the 0x0D handler is VPP-free so there is no 12V path regardless.
- **Files modified:** `firestarter_app/tools/build_db.py`
- **No impact on gates:** All tests pass, all gate checks green.

**2. [Test precision] AT28C16 test guard uses literal 'AT28C04-ADAPTER.md' not 'DIP24'**
- **Found during:** Task 1 RED verification
- **Issue:** Original test draft checked for `"DIP24" in reason.upper()` — but the existing Site B reason already contains "DIP24" ("dedicated DIP24 EEPROM adapter"), so the test would have passed GREEN immediately against the pre-change DB.
- **Fix:** Tightened to check for `"AT28C04-ADAPTER.md" in reason` — this literal is only present in the named-arm reason string, not in the old Site B generic string.

**3. [ruff format] build_db.py required reformatting**
- **Found during:** Task 2 post-edit
- **Issue:** ruff format wanted to reformat the named arm block (set literal formatting, comprehension line length).
- **Fix:** Applied `python -m ruff format tools/build_db.py` — no logic change. Raw codegen output is ruff-clean per CLAUDE.md convention.

## Known Stubs

None. All changes are functional and fully wired.

## Threat Flags

None. No new network endpoints, auth paths, file access patterns, or schema changes beyond the planned reason-string rewrites.

## Self-Check: PASSED

- SUMMARY.md: FOUND at `.planning/phases/76-spec-only-gaps-adapter-required-x88c64/76-01-SUMMARY.md`
- Commit `10388b5`: FOUND (test RED phase)
- Commit `9c1e019`: FOUND (feat GREEN phase)
- Task 3 gates: no separate commit needed (verification only)
