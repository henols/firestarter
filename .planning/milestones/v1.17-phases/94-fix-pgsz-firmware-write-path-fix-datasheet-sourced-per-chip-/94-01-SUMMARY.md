---
phase: 94-fix-pgsz-firmware-write-path-fix-datasheet-sourced-per-chip-
plan: 01
subsystem: firmware/host
tags: [fix, safety, flash4, T-93-CANERASE, FIX-01a, FIX-03, SAFE-02, dual-repo]
dependency_graph:
  requires: [93-04]
  provides: [FIX-01a, T-93-CANERASE-mitigated, SAFE-01-cleared]
  affects: [firestarter_app/firestarter/database.py, firestarter/src/proms/flash_type_4.cpp]
tech_stack:
  added: []
  patterns:
    - "Protocol-gated FLAG_CAN_ERASE derivation in convert_to_programmer (algorithm!=5)"
    - "D-06 firmware guard: handle->protocol==0x05 erase-skip in flash4_write_init"
key_files:
  created:
    - path: firestarter_app/tests/test_val_wire_flash4.py
      note: "Extended with 4 FIX-01a assertions (new tests only; existing tests unchanged)"
  modified:
    - path: firestarter_app/firestarter/database.py
      note: "convert_to_programmer: gate FLAG_CAN_ERASE on algorithm!=5"
    - path: firestarter_app/tests/test_database_conversion.py
      note: "Update W29C040 pinning test from hazardous (0x02) to correct (0x00) assertion"
    - path: firestarter/src/proms/flash_type_4.cpp
      note: "flash4_write_init: add protocol==0x05 erase-skip guard (defense-in-depth)"
    - path: firestarter/test/native/avr/test_val_flash4/test_val_flash4.cpp
      note: "Add test_flash4_init_no_vpp_when_can_erase_protocol5 (12th native test)"
decisions:
  - "FIX-01a implemented as defense-in-depth (host+firmware both fixed) per plan"
  - "Guard keyed on handle->protocol==0x05 per D-06 (not vpp_mv — W29C040 carries vpp_mv=12000 as chip-ID datum)"
  - "Flash4 erase path unchanged for non-0x05 protocols — no behavioral regression"
  - "Pre-existing test_convert_w29c040_flash_eeprom_flag_can_erase updated to assert the correct (safe) behavior"
metrics:
  duration: "~12 minutes"
  completed: "2026-06-27"
  tasks_completed: 2
  tasks_total: 2
  files_modified: 5
---

# Phase 94 Plan 01: FIX-01a T-93-CANERASE Fix Summary

**One-liner:** Defense-in-depth removal of the FLAG_CAN_ERASE 12V-on-5V hazard for protocol 0x05 flash4 chips: host flag derivation gated on algorithm!=5, firmware guard keyed on handle->protocol==0x05, dual-repo lockstep.

## Objective

Eliminate the T-93-CANERASE hardware hazard (identified by SAFE-01-PREFLIGHT in Phase 93):
`convert_to_programmer` was setting `FLAG_CAN_ERASE (0x02)` for all `Flash/EEPROM`-typed chips
including 5V-only protocol-0x05 (flash4) chips. On the wire, this routed firmware
`flash4_write_init` → `flash4_erase_execute` which asserts
`CTRL_VPP_REGULATOR_ENABLE | CTRL_VPP_VPE_DROP_ENABLE | CTRL_VPE_ENABLE` — 12V boost on a 5V
chip (RED/HIGH hardware-damage hazard).

## Pre-change Baseline

| Suite | Before | After |
|-------|--------|-------|
| Native `test_val_flash4` (firestarter) | 11 tests PASS | 12 tests PASS |
| Host pytest (firestarter_app) | 689 tests PASS | 693 tests PASS |
| W29C040 wire flags | 0x02 (FLAG_CAN_ERASE SET — hazardous) | 0x00 (safe) |
| W27C512 wire flags | 0x02 (FLAG_CAN_ERASE) | 0x02 (unchanged — correct) |

## Tasks Executed

### Task 1 (TDD): Host FIX-01a — gate FLAG_CAN_ERASE on protocol in convert_to_programmer

**Files:** `firestarter_app/firestarter/database.py`, `firestarter_app/tests/test_val_wire_flash4.py`

**TDD RED commit:** `0192246` — Added 4 failing assertions to `test_val_wire_flash4.py`:
- `test_flash4_rep_chip_no_flag_can_erase` — AT29C040 (flash4 rep chip) flags must have no FLAG_CAN_ERASE
- `test_w29c040_no_flag_can_erase` — W29C040 wire flags must be exactly 0x00
- `test_non_flash4_eeprom_still_has_flag_can_erase` — W27C512 (0x07) still carries FLAG_CAN_ERASE
- `test_flash4_eeprom_type_chip_no_flag_can_erase` — Flash/EEPROM-typed protocol-0x05 chip yields flags==0x00

**TDD GREEN commit:** `7725641` — Implementation in `database.py`:
```python
algo = programmer_data["algorithm"]
if full_eprom_data.get("electrical-type", "") in ("EEPROM", "Flash/EEPROM"):
    if algo != 5:
        # FIX-01a: flash4 (0x05) auto-erases per page; no 12V bulk erase needed
        simple_flags |= FLAG_CAN_ERASE
```

Also updated `test_database_conversion.py`: renamed `test_convert_w29c040_flash_eeprom_flag_can_erase`
→ `test_convert_w29c040_no_flag_can_erase`, updated assertion from `assert flags & FLAG_CAN_ERASE`
to `assert flags & FLAG_CAN_ERASE == 0` (the prior test was pinning the hazardous behavior).

**Verification:**
- `pytest tests/test_val_wire_flash4.py -x -q`: 8 passed
- `pytest` (full suite): 693 passed
- `ruff check` + `ruff format --check`: clean

### Task 2: Firmware defense-in-depth — protocol==0x05 erase-skip guard + native no-VPP test

**Files:** `firestarter/src/proms/flash_type_4.cpp`, `firestarter/test/native/avr/test_val_flash4/test_val_flash4.cpp`

**Commit:** `48a0c64`

**Guard added in `flash4_write_init`:**
```c
if (handle->protocol != 0x05) {
    flash4_erase_execute(handle);
}
```
Keyed on `handle->protocol == 0x05` per D-06 boundary. NOT on `handle->vpp_mv` (W29C040
carries `vpp_mv=12000` as chip-ID datum, not a program rail — a voltage heuristic would
never fire, Pitfall 3 / 94-RESEARCH.md).

**New native test `test_flash4_init_no_vpp_when_can_erase_protocol5`:**
- Setup: protocol=0x05, CMD_WRITE, ctrl_flags=FLAG_CAN_ERASE (no FLAG_SKIP_ERASE)
- Drives flash4_write_init (via firestarter_operation_init) + flash4_write_execute (data_size=0)
- Asserts: `assert_no_vpp_in_recording` finds NO `CTRL_VPP_REGULATOR_ENABLE` or `CTRL_VPP_P1_ENABLE` bits
- Failure mode if guard reverted: flash4_erase_execute is called → CTRL_VPP_REGULATOR_ENABLE bit appears → test FAILS

**Verification:**
- `pio test -e native -f "*test_val_flash4*"`: 12 tests passed (golden write trace + chip-id trace still green)
- `pio run -e leonardo`: SUCCESS (87.7% flash / 78.1% RAM, +16 bytes from guard code)

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Updated pre-existing test that was pinning hazardous behavior**
- **Found during:** Task 1 GREEN phase (pytest run caught failing test)
- **Issue:** `tests/test_database_conversion.py::test_convert_w29c040_flash_eeprom_flag_can_erase` asserted `out["flags"] & FLAG_CAN_ERASE` (i.e., the flag IS set). This test was correctly describing the old behavior but was now asserting a bug.
- **Fix:** Renamed test to `test_convert_w29c040_no_flag_can_erase`; updated assertion to verify the fix: `assert out["flags"] & FLAG_CAN_ERASE == 0`
- **Files modified:** `firestarter_app/tests/test_database_conversion.py`
- **Commit:** `7725641`

## Threat Surface Scan

No new network endpoints, auth paths, file access patterns, or schema changes at trust
boundaries were introduced. T-93-CANERASE (the pre-existing threat) was mitigated:
- Host: no longer emits FLAG_CAN_ERASE for protocol 0x05 chips
- Firmware: guard ensures flash4_erase_execute never runs for protocol 0x05 even with stale wire JSON
- T-94-HANDCRAFT mitigated: firmware guard blocks even hand-crafted JSON carrying FLAG_CAN_ERASE
- T-94-VHEURISTIC mitigated: guard correctly keyed on handle->protocol, not vpp_mv

## Submodule Commits

| Repo | Commit | Description |
|------|--------|-------------|
| firestarter_app | `0192246` | test(94-01): RED — failing FIX-01a assertions |
| firestarter_app | `7725641` | feat(94-01): GREEN — gate FLAG_CAN_ERASE on algorithm!=5 |
| firestarter | `48a0c64` | feat(94-01): firmware defense-in-depth guard + native test |

Gitlink bump in meta-repo: firestarter `a1953c2` → `48a0c64`, firestarter_app `98b3a92` → `7725641`.

## Self-Check: PASSED

- [x] `firestarter_app/firestarter/database.py` modified — verified
- [x] `firestarter_app/tests/test_val_wire_flash4.py` modified — verified
- [x] `firestarter_app/tests/test_database_conversion.py` modified — verified
- [x] `firestarter/src/proms/flash_type_4.cpp` modified — verified
- [x] `firestarter/test/native/avr/test_val_flash4/test_val_flash4.cpp` modified — verified
- [x] Host pytest: 693 passed (was 689)
- [x] Native flash4 suite: 12 passed (was 11)
- [x] Leonardo build: SUCCESS
- [x] ruff check + ruff format --check: CLEAN
- [x] W29C040 wire flags == 0x00
- [x] W27C512 wire flags == 0x02 (unchanged)
- [x] Golden write trace + chip-id trace: still PASSED
