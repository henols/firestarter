---
phase: 81-2516-db-entry-non-destructive-read-sweep
plan: "01"
subsystem: firestarter_app/tests
tags: [db-audit, flag-can-erase, flash-eeprom, test-pinning, safe-03]
dependency_graph:
  requires: []
  provides: [DB-02-AUDIT, D-05-TEST, SAFE-02-CONFIRMED, SAFE-03-CONFIRMED]
  affects: [Phase-82-write-path]
tech_stack:
  added: []
  patterns: [EpromDatabase-hermetic-fixture, FLAG_CAN_ERASE-electrical-type-direct-read]
key_files:
  created: []
  modified:
    - firestarter_app/tests/test_database_conversion.py
decisions:
  - "DB-02 re-audit verdict: Flash/EEPROM branch SOUND at convert_to_programmer line 605; no production change needed (D-04 independent re-derive confirmed)"
  - "D-05 pinning test added for W29C040 (0x05, Flash/EEPROM) — extends ERASE-01/D-01/D-02 lock to flash4 family"
  - "SAFE-03 parity confirmed: FLAG_CAN_ERASE = 0x02 in both constants.py:80 and firestarter.h:60"
metrics:
  duration: "~8 minutes"
  completed: "2026-06-23"
  tasks_completed: 2
  files_modified: 1
---

# Phase 81 Plan 01: FLAG_CAN_ERASE DB-02 Re-Audit + Flash/EEPROM Pinning Test Summary

**One-liner:** Fresh adversarial re-audit of the FLAG_CAN_ERASE decode chain for Flash/EEPROM (W29C040 / 0x05) confirmed SOUND; pinned by new test `test_convert_w29c040_flash_eeprom_flag_can_erase`; 651 tests green.

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Fresh adversarial re-audit of FLAG_CAN_ERASE decode chain (DB-02/D-04) | (no file change — audit-only) | — |
| 2 | Add Flash/EEPROM pinning test + confirm 0xA4 guard + full suite green (D-05/SAFE-02) | `0cfc23b` (firestarter_app) | `tests/test_database_conversion.py` |

## DB-02 Decode Chain Re-Audit Trace (D-04 — independent re-derive, no Phase-77 trust)

**Verdict: Flash/EEPROM branch SOUND — no production change needed.**

The four-stage decode chain was re-derived from scratch for `W29C040` (Flash/EEPROM, algorithm 0x05):

### Stage 1 — `build_db.py` Pass-2 `_etype` re-derivation (lines 607–643)

`build_db.py` re-derives `_etype` after all algorithm overrides. For `proto_id in {0x05, 0x06, 0x0D, 0x10}` (line 639):
```python
elif proto_id in {0x05, 0x06, 0x0D, 0x10}:
    _etype = "Flash/EEPROM"
```
W29C040 has `proto_id = 0x05` (flash4 / FLASH_AMD_STD). Pass-2 sets `_etype = "Flash/EEPROM"`. This value flows into `chip_database.json` as `electrical.type = "Flash/EEPROM"`.

### Stage 2 — `database.py _map_data` (lines 434, 456)

`_map_data` reads `electrical.get("type")` from the chip entry. Two relevant operations:

1. **Synthetic `info_flags |= 0x10`** (line 434): `if electrical.get("type") in ("EEPROM", "Flash/EEPROM"): info_flags |= 0x00000010` — sets the `can_be_electrically_erased` info flag.
2. **`electrical-type` passthrough** (line 456): `"electrical-type": electrical.get("type", "")` — carries the raw `"Flash/EEPROM"` string verbatim into the chip data dict.

W29C040: `electrical-type = "Flash/EEPROM"` passes through to the data dict.

### Stage 3 — `database.py convert_to_programmer` (lines 592–607)

The canonical FLAG_CAN_ERASE set site (Phase 77 D-01/D-02 wiring, confirmed here independently):
```python
simple_flags = 0
if full_eprom_data.get("electrical-type", "") in ("EEPROM", "Flash/EEPROM"):
    simple_flags |= FLAG_CAN_ERASE  # FLAG_CAN_ERASE is 0x02
programmer_data["flags"] = simple_flags
```
Key observation: this reads `electrical-type` **directly** (not the fragile `info-flags & 0x10` round-trip). Both `"EEPROM"` and `"Flash/EEPROM"` are in the membership tuple. W29C040's `"Flash/EEPROM"` matches → `simple_flags |= 0x02`.

### Stage 4 — Wire JSON `flags` → firmware `eprom_write_init`

The wire JSON carries `"flags": 0x02`. The firmware `eprom_write_init` in `eprom.cpp` checks `is_flag_set(FLAG_CAN_ERASE)` to trigger auto-erase before write. Since W29C040 routes to `configure_flash4` (0x05 dispatch), not `configure_eeprom28c` (0x0D), the D-03 carry-forward (0x0D firmware-inert) does not apply — flash4 does honor the erase flag.

### Empirical Confirmation

Live verification:
```
W29C040: electrical-type=Flash/EEPROM, protocol-id=5, wire_flags=0x02, FLAG_CAN_ERASE_set=True
W29C020: electrical-type=Flash/EEPROM, protocol-id=5, wire_flags=0x02, FLAG_CAN_ERASE_set=True
W27C512: electrical-type=EEPROM, protocol-id=7, wire_flags=0x02, FLAG_CAN_ERASE_set=True
M27C512: electrical-type=UV-EPROM, protocol-id=7, wire_flags=0x00, FLAG_CAN_ERASE_set=False
```

The plan verify one-liner:
```
cd firestarter_app && python3 -c "from firestarter.database import EpromDatabase; db=EpromDatabase(skip_local_override=True); print(all(db.convert_to_programmer(db.get_eprom(c))['flags'] & 0x02 for c in ('W29C040','W29C020','W27C512')) and db.convert_to_programmer(db.get_eprom('M27C512'))['flags'] & 0x02 == 0)"
```
Output: **`True`**

### SAFE-03 Parity Confirmation

```
constants.py:80:FLAG_CAN_ERASE = 0x02
firestarter.h:60:#define FLAG_CAN_ERASE 0x02
```
Both files define `FLAG_CAN_ERASE = 0x02`. No constant change needed. Parity CONFIRMED.

## Task 2: Flash/EEPROM Pinning Test

New test `test_convert_w29c040_flash_eeprom_flag_can_erase` added to `firestarter_app/tests/test_database_conversion.py` after line 104 (after `test_convert_at28c256_flash_eeprom_flag_can_erase`, before the `# ---` separator):

```python
def test_convert_w29c040_flash_eeprom_flag_can_erase(db: EpromDatabase) -> None:
    """W29C040 (Flash/EEPROM, algorithm 0x05) carries FLAG_CAN_ERASE — extends the
    electrical-type derivation lock (ERASE-01 / D-01/D-02) to the flash4 (0x05)
    Flash/EEPROM family per D-05.  W29C020/W29C040 are bench-proven for the FIRST
    time in Phase 82; this pinning test independently verifies the Flash/EEPROM branch
    without inheriting Phase 77's EEPROM-only proof (DB-02 / D-04)."""
    full = db.get_eprom("W29C040")
    assert full is not None
    out = db.convert_to_programmer(full)
    assert out["flags"] & FLAG_CAN_ERASE
```

- No new imports added (reuses `FLAG_CAN_ERASE` from line 7 and `db` fixture from lines 11–14)
- Negative control `test_convert_uv_eprom_no_flag_can_erase` (M27C512) pre-existing, not duplicated

### Verification Results

| Check | Result |
|-------|--------|
| `pytest tests/test_database_conversion.py::test_convert_w29c040_flash_eeprom_flag_can_erase -q` | PASS |
| `pytest tests/test_eprom_operations.py::test_init_phase_data_frames_not_acked -q` (0xA4 guard, SAFE-02) | PASS |
| `ruff check tests/test_database_conversion.py` | CLEAN |
| `ruff format --check tests/test_database_conversion.py` | CLEAN (already formatted) |
| Full suite `pytest -q` | 651 passed |

## Deviations from Plan

None — plan executed exactly as written. The re-audit confirmed the Flash/EEPROM branch is SOUND and no production code change was needed, consistent with the expected finding.

## Threat Surface Scan

No new network endpoints, auth paths, file access patterns, or schema changes introduced. This plan is test-only; no production code modified.

## Known Stubs

None.

## Self-Check: PASSED

- `firestarter_app/tests/test_database_conversion.py` exists and has the new test: FOUND
- Submodule commit `0cfc23b` on `v1.15-bench-validation-of-operator-inventory`: FOUND
- `FLAG_CAN_ERASE = 0x02` parity in both `constants.py` and `firestarter.h`: CONFIRMED
- Full suite 651 passed: CONFIRMED
