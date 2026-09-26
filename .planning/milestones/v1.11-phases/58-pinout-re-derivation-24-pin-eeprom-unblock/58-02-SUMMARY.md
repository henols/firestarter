---
phase: 58-pinout-re-derivation-24-pin-eeprom-unblock
plan: "02"
subsystem: firestarter_app
tags: [pinouts, eeprom, database, build_db, safety, principled-rules]
dependency_graph:
  requires:
    - 58-01 (DIP24_2816 pinout entry + Wave 0 RED-first tests)
  provides:
    - Principled resolve_pinout_key (no guess tables, no per-IC code)
    - Regenerated chip_database.json with 743 chips (9 unblocked + 10 fixed)
    - All 30 Wave 0 RED tests now GREEN
  affects:
    - firestarter_app/tools/build_db.py
    - firestarter_app/firestarter/data/chip_database.json
    - firestarter_app/tests/test_audit_coverage_matrix.py
    - firestarter_app/tests/golden/v1.3-COVERAGE-MATRIX.md
    - firestarter_app/tests/__snapshots__/test_characterization.ambr
tech_stack:
  added: []
  patterns:
    - Principled pinout selection keyed on (pin_count, pm_idx, variant_lo, type_int, mem_size, proto_id)
    - D-06 fail-safe skip for unclassifiable chips (no VPP-asserting dispatch)
    - Rule 1/2/3 named override outcomes (D-05)
    - Two-pass _etype invariant preserved (Pass 1 flags-based, Pass 2 protocol-aware)
key_files:
  created: []
  modified:
    - firestarter_app/tools/build_db.py
    - firestarter_app/firestarter/data/chip_database.json
    - firestarter_app/tests/test_audit_coverage_matrix.py
    - firestarter_app/tests/golden/v1.3-COVERAGE-MATRIX.md
    - firestarter_app/tests/__snapshots__/test_characterization.ambr
decisions:
  - "Rule 2 (WARNING-5) uses split discriminator: DIP28_28C256+proto=0x07 fires
    without flags&0x10 guard (type_int!=4 guard); DIP28_2764+proto=0x07 retains
    _etype==Flash/EEPROM guard to avoid misclassifying legitimate UV-EPROMs"
  - "CAT28C256 (flags=0xC000, no erasable bit) correctly gets algo=0x0D via Rule 2
    because it resolves to DIP28_28C256 (pm_idx=20); the pinout is the EEPROM discriminator"
  - "19 chips get Rule 1 (variant_lo=0x10 24-pin EEPROMs: 9 previously blocked + 10 previously dangerous)"
  - "12 chips get Rule 2 (DIP28_28C256 + proto=0x07 EEPROM class, incl. CAT28C256)"
  - "chip_database.json chip count: 734 → 743 (+9 unblocked AT28C04/16-family chips)"
  - "Audit coverage matrix counts updated: 339/212/127 → 332/205/127 (7 moved 0x07→0x0D)"
metrics:
  duration: 35min
  completed: "2026-06-09"
  tasks_completed: 2
  tasks_total: 2
  files_modified: 5
---

# Phase 58 Plan 02: Principled resolve_pinout_key Rewrite + DB Regeneration

**One-liner:** Three guess tables deleted; resolve_pinout_key rewritten as pure function of decoded fields; chip_database.json regenerated with 743 chips; all 30 Wave 0 RED tests now GREEN; GATE-03 0 violations.

## Summary

Plan 02 is the production code wave for Phase 58. It rewrites `resolve_pinout_key` in `firestarter_app/tools/build_db.py` as a principled, data-driven function per D-02/D-03/D-05/D-06, then regenerates `chip_database.json`.

### Task 1: Rewrite resolve_pinout_key

Commit `3f1b44a`: Deleted the three survey-built guess tables (`DIP28_VARIANT_MAP`, `PIN_MAP_TO_PINOUT`, `PIN_MAP_PROTO_TO_PINOUT`) and rewrote `resolve_pinout_key` as a pure branch on `(pin_count, pm_idx, variant_lo, type_int, mem_size, proto_id)`:

- **24-pin**: pm_idx=23 → variant_lo 0x01/0x10/else (2732/2816/2716); pm_idx=0 → 6116; else → None
- **28-pin**: pm_idx 22/21/20/19/18 (UV-EPROM/2764/28C256/28C64/28C64); pm_idx=0 → SRAM/flash; else → None
- **32-pin**: pm_idx=0 → SST39SF040 (SRAM); pm_idx in {5,7,9,10,11,12,13} → proto discriminates; else → None

D-06 fail-safe added after the call site: `pinout_key is None` → loud WARN + continue (never emits a VPP-asserting dispatch for an unclassifiable chip).

Three algorithm-override rules follow (mandatory execution order):
- **Rule 1** (28C-EEPROM): DIP24_2816 → proto=0x0D (replaces safety skip)
- **Rule 2** (WARNING-5): DIP28_28C256+proto=0x07 OR DIP28_2764+proto=0x07+Flash/EEPROM → proto=0x0D
- **Rule 3** (fm1608/SRAM): type=4 + proto in {0x07,0x08,0x0B} → proto=0x28

The two-pass `_etype` pattern is preserved exactly (Pass 1 flags-based before overrides; Pass 2 protocol-aware after overrides).

### Task 2: DB Regeneration + Test Fixes

Commit `0503394`: Regenerated `chip_database.json` via `python3 tools/build_db.py` (live infoic.xml fetch). Additionally:

- Fixed Rule 2 bug (CAT28C256 with flags=0xC000 not caught by old _etype guard) by splitting the DIP28_28C256 and DIP28_2764 sub-cases
- Updated `test_audit_coverage_matrix.py` row counts (339→332, 212→205, 743 total chips)
- Updated `tests/golden/v1.3-COVERAGE-MATRIX.md` to match new DB
- Updated `test_characterization.ambr` snapshot (9 new chips in `firestarter list`)

## Regenerated DB Statistics

| Metric | Value | Change from Phase 57 |
|--------|-------|---------------------|
| Total chips | 743 | +9 (9 unblocked AT28C04/16 family) |
| algo=0x0D chips | +19 Rule 1, +12 Rule 2 | 31 more on configure_eeprom28c |
| algo=0x07 chips | 205 | -7 (DIP28_28C256 EEPROM class corrected) |
| algo=0x08 chips | 127 | unchanged |
| In-scope (0x07+0x08) | 332 | -7 |
| D-06 unclassifiable skips | 0 | all chips classified |
| GATE-03 violations | 0 | clean |

## build_db.py Stderr Audit Trail (for Phase 59 GATE-02)

### Rule 1 Firings (19 chips — all variant_lo=0x10 24-pin EEPROMs)

```
INFO: AMD/AM28C16A@DIP24 algorithm 0x0B->0x0D (Rule 1: 28C-EEPROM family, variant_lo=0x10; configure_eeprom28c, no VPP)
INFO: ATMEL/AT28C04@DIP24,AT28C04@SOIC24,AT28HC04 algorithm 0x0B->0x0D (Rule 1...)
INFO: ATMEL/AT28C04E@DIP24,AT28C04E@SOIC24,AT28C04F@DIP24,AT28C04F@SOIC24 algorithm 0x0B->0x0D (Rule 1...)
INFO: ATMEL/AT28C16@DIP24,AT28C16@SOIC24,AT28HC16,AT28HC16L algorithm 0x0B->0x0D (Rule 1...)
INFO: ATMEL/AT28C16E@DIP24,AT28C16E@SOIC24,AT28C16F@DIP24,AT28C16F@SOIC24 algorithm 0x0B->0x0D (Rule 1...)
INFO: CATALYST(CSI)/CAT28C16A,CAT28C16A@SOIC24,CAT28C16AI,CAT28C16AI@SOIC24 algorithm 0x0B->0x0D (Rule 1...)
INFO: EXEL/XL2804A algorithm 0x0B->0x0D (Rule 1...)
INFO: EXEL/XL2816A,XLE28C16A,XLS28C16A algorithm 0x0B->0x0D (Rule 1...)
INFO: EXEL/XLE28C16B,XLE28C16B@SIOC24,XLS28C16B,XLS28C16B@SIOC24 algorithm 0x0B->0x0D (Rule 1...)
INFO: MICROCHIP memory/2804 algorithm 0x0B->0x0D (Rule 1...)
INFO: MICROCHIP memory/2816 algorithm 0x0B->0x0D (Rule 1...)
INFO: MICROCHIP memory/28C04A,28C04A@SOIC24 algorithm 0x0B->0x0D (Rule 1...)
INFO: MICROCHIP memory/28C04AF,28C04AF@SOIC24 algorithm 0x0B->0x0D (Rule 1...)
INFO: MICROCHIP memory/28C16A,28C16A@SOIC24 algorithm 0x0B->0x0D (Rule 1...)
INFO: MICROCHIP memory/28C16AF,28C16AF@SOIC24 algorithm 0x0B->0x0D (Rule 1...)
INFO: NEC/UPD28C04@DIP24,UPD28C04@SOIC24 algorithm 0x0B->0x0D (Rule 1...)
INFO: XICOR/X2804A,X2804AI algorithm 0x0B->0x0D (Rule 1...)
INFO: XICOR/X2816A algorithm 0x0B->0x0D (Rule 1...)
INFO: XICOR/X2816B,X2816C algorithm 0x0B->0x0D (Rule 1...)
```

Split: 9 previously-blocked (flags=0x10) + 10 previously-dangerous (flags=0x00).

### Rule 2 Firings (12 chips — DIP28_28C256 EEPROM class with proto=0x07)

```
INFO: ATMEL/AT28BV256,AT28LV256 algorithm override 0x07->0x0D (Rule 2 WARNING-5...)
INFO: ATMEL/AT28C256,... algorithm override 0x07->0x0D (Rule 2 WARNING-5...)
INFO: CATALYST(CSI)/CAT28C256,CAT28C256@SOIC28,CAT28C257,CAT28C257@SOIC28 algorithm override 0x07->0x0D (Rule 2 WARNING-5...)
INFO: CATALYST(CSI)/CAT28LV256,CAT28LV256@SOIC28 algorithm override 0x07->0x0D (Rule 2...)
INFO: CYPRESS/FM28V020@SOP28 algorithm override 0x07->0x0D (Rule 2...)
INFO: EXEL/XLE28C256,XLS28C256 algorithm override 0x07->0x0D (Rule 2...)
INFO: FUJITSU/MB85R256H@SO28 algorithm override 0x07->0x0D (Rule 2...)
INFO: HITACHI/HN58C256AP@DIP28 algorithm override 0x07->0x0D (Rule 2...)
INFO: MICROCHIP memory/28C256,28C256F algorithm override 0x07->0x0D (Rule 2...)
INFO: NEC/UPD28C256 algorithm override 0x07->0x0D (Rule 2...)
INFO: ST/M28256,M28256@SOIC28 algorithm override 0x07->0x0D (Rule 2...)
INFO: XICOR/X28256,X28C256 algorithm override 0x07->0x0D (Rule 2...)
```

### D-06 Unclassifiable Skips

None — 0 chips skipped for unclassifiable pinout. All 24/28/32-pin DIP chips in infoic.xml were classified by the principled rules.

## Test Results

| Class | Tests | Status |
|-------|-------|--------|
| TestResolvedPinoutKey | 16 | GREEN |
| TestGuessTablesDeleted | 3 | GREEN |
| TestWarning5Rule | 1 | GREEN |
| TestDIP24_2816Pinout | 6 | GREEN (was already GREEN in Plan 01) |
| TestDangerous24pinEEPROMFixed | 10 | GREEN |
| **Full suite** | **516** | **ALL PASSED** |
| GATE-03 check_dispatch.py | — | 0 violations / 743 chips |

## Commits

| Hash | Repo | Type | Description |
|------|------|------|-------------|
| `3f1b44a` | firestarter_app | `refactor(58-02)` | Rewrite resolve_pinout_key, delete guess tables (D-02/D-03/D-05/D-06) |
| `0503394` | firestarter_app | `feat(58-02)` | Regenerate chip_database.json + fix Rule 2 for pm_idx=20 chips (PIN-03) |

Both commits on branch `v1.11-infoic-decode-correctness`.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Rule 2 (WARNING-5) predicate needed split for DIP28_28C256 vs DIP28_2764**

- **Found during:** Task 2 — after DB regeneration, `TestWarning5Rule` failed because `CAT28C256` (flags=0xC000, no `flags & 0x10` bit) had `algorithm=0x07` despite being on `DIP28_28C256` pinout.
- **Issue:** The original WARNING-5 predicate `_etype == "Flash/EEPROM"` (from Pass 1) requires `flags & 0x10`, which CAT28C256 lacks. But `DIP28_28C256` is an EEPROM-only pinout — no UV-EPROM can reach it via the principled rules (pm_idx=20 is exclusively 28C256 EEPROM class).
- **Fix:** Split Rule 2 into two sub-cases: (1) `DIP28_28C256 + proto=0x07 + type_int!=4` fires unconditionally (pinout IS the EEPROM discriminator); (2) `DIP28_2764 + proto=0x07 + _etype==Flash/EEPROM` retains the flags guard (UV-EPROMs legitimately land on DIP28_2764 via pm_idx=21/22). Added `type_int != 4` guard to sub-case 1 so SRAM chips at pm_idx=0 that resolve to DIP28_28C256 (mem_size > 8K) are still handled by Rule 3 (fm1608), not Rule 2.
- **Files modified:** `firestarter_app/tools/build_db.py`
- **Commit:** `0503394`

**2. [Rule 1 - Bug] Audit coverage matrix snapshot counts stale after DB regeneration**

- **Found during:** Task 2 — `test_enumeration_row_count` expected 339/212/127 but new DB has 332/205/127; `test_summary_stats` checked for "734" in body but new DB has 743 chips; `test_golden_file_matches` byte-exact comparison failed.
- **Issue:** These tests contain hardcoded counts that were correct for the pre-Phase-58 DB. The DB regeneration intentionally changes these counts (9 chips unblocked, 7 chips corrected from 0x07→0x0D).
- **Fix:** Updated hardcoded counts in `test_audit_coverage_matrix.py`; regenerated `tests/golden/v1.3-COVERAGE-MATRIX.md`; updated `test_characterization.ambr` snapshot.
- **Files modified:** `firestarter_app/tests/test_audit_coverage_matrix.py`, `firestarter_app/tests/golden/v1.3-COVERAGE-MATRIX.md`, `firestarter_app/tests/__snapshots__/test_characterization.ambr`
- **Commit:** `0503394`

## Known Stubs

None — all 30 Wave 0 RED tests are now GREEN. DB regeneration is complete. GATE-03 passes with 0 violations.

## Threat Flags

None. The `DIP24_2816` pinout has no `vpp-pin` field (SR-1 invariant maintained). All 19 variant_lo=0x10 chips now route to `configure_eeprom28c` (algo=0x0D, no VPP regulator assertion). GATE-03 confirms 0 Flash/EEPROM chips route to configure_eprom.

## Self-Check: PASSED

Files verified:
- `/workspaces/firestarter_app/tools/build_db.py` — FOUND (guess tables deleted, principled resolve_pinout_key present)
- `/workspaces/firestarter_app/firestarter/data/chip_database.json` — FOUND (743 chips)

Commits verified:
- `3f1b44a` — FOUND (firestarter_app git log)
- `0503394` — FOUND (firestarter_app git log)

Test results confirmed:
- 36 Wave 0 tests: ALL GREEN
- Full suite: 516 passed, 0 failed
- GATE-03: 0 violations
