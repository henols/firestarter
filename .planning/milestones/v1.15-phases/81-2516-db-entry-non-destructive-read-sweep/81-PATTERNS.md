# Phase 81: 2516-db-entry-non-destructive-read-sweep — Pattern Map

**Mapped:** 2026-06-23
**Files analyzed:** 4 deliverables (user-override JSON, safety-review doc, test assertion, bench evidence artifacts)
**Analogs found:** 4 / 4

---

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `~/.firestarter/database.json` (2516 entry) | config / data | CRUD (hand-authored) | `firestarter_app/firestarter/data/chip_database.json` AM2716 entry (lines 66–86) | exact — same UV-EPROM / DIP24_2716 / 0x0B family |
| `81-2516-SAFETY-REVIEW.md` | doc / checklist | manual gate | `.planning/phases/58-pinout-re-derivation-24-pin-eeprom-unblock/58-SR-1-CHECKLIST.md` | exact — SR-1 format, same pinout class |
| `firestarter_app/tests/test_database_conversion.py` (new assertion) | test | request-response | `test_convert_at28c256_flash_eeprom_flag_can_erase` (lines 98–104) | exact — same FLAG_CAN_ERASE pattern |
| `.planning/v1.15/bench/EVIDENCE.{md,json}` | artifact / evidence | batch / append | `firestarter_app/val-results/eprom/validation-matrix.{json,md}` | role-match — same per-family matrix schema |

---

## Pattern Assignments

### `~/.firestarter/database.json` (2516 user-override entry)

**Analog:** `firestarter_app/firestarter/data/chip_database.json`, AMD section, AM2716 entry (lines 66–86)

**Key facts about the merge path:**
- `~/.firestarter/database.json` is loaded by `get_local_database()` in `firestarter_app/firestarter/config.py` (line 25).
- `_merge_databases()` in `database.py` (lines 226–250) adds new items: it checks `manual_item.get("name")` against existing `part_number` keys. User-override entries use a `"name"` key (not `"part_number"`) to trigger the add-new-item path (line 244–246).
- Loaded only when `EpromDatabase(skip_local_override=False)` — tests use `skip_local_override=True` so this entry is invisible to the automated suite (correct behavior).

**Chip structure to copy** (chip_database.json lines 66–86):
```json
{
  "electrical": {
    "pin_count": 24,
    "size_bytes": 2048,
    "type": "UV-EPROM",
    "vcc": "5V",
    "vdd": "6.5V",
    "vpp": "25V",
    "vpp_mv": 25000
  },
  "part_number": "AM2716",
  "pinout": "DIP24_2716",
  "programming": {
    "algorithm": 11,
    "chip_id_check": false,
    "chip_id_value": "0x00000000",
    "pulse_duration": "500 us"
  },
  "support_status": "supported"
}
```

**Adaptations for the 2516 entry:**
- Top-level key: `"INTEL"` (or `"USER"` / `"Custom"` — use a manufacturer-like key that doesn't collide).
- `"name"` instead of `"part_number"` to engage the user-override add-new-item path in `_merge_databases`.
- `size_bytes`: 2048 (2516 = 2KB).
- `vpp`: `"25V"`, `vpp_mv`: 25000 (2516 datasheet; confirmed under v1.14 Phase 79 ceiling raise).
- `pinout`: `"DIP24_2716"` (24-pin UV-EPROM standard — same as AM2716).
- `algorithm`: 11 (0x0B = NMOS/EPROM_NMOS path per v1.14 Phase 79 graduation).
- `support_status`: `"supported"`.
- `chip_id_check`: false (2516 has no chip-ID register).
- `pulse_duration`: `"500 us"` (standard Intel 2516 programming pulse — confirm from datasheet).

**User-override JSON wrapper structure** (from `_merge_databases` pattern):
```json
{
  "INTEL": [
    {
      "name": "2516",
      "electrical": { ... },
      "pinout": "DIP24_2716",
      "programming": { ... },
      "support_status": "supported"
    }
  ]
}
```

---

### `81-2516-SAFETY-REVIEW.md` (safety review checklist doc)

**Analog:** `.planning/phases/58-pinout-re-derivation-24-pin-eeprom-unblock/58-SR-1-CHECKLIST.md`

**Header structure to copy** (lines 1–17):
```markdown
# Phase 81 SR-1 Safety Review — 2516 User-Override Entry

**Scope:** The hand-authored `~/.firestarter/database.json` entry for the Intel 2516
(24-pin UV-EPROM, DIP24_2716 pinout, algorithm 0x0B).

**Standard:** SR-1 (Safety Review 1) — VPP-pin safety checklist.

**GATE-03 status:** Not applicable — user-override entries are not scanned by
`tools/check_dispatch.py` (which operates on the generated chip_database.json only).
Safety is established by this manual review.
```

**SR-1 Item Legend to preserve** (lines 20–34):

The checklist covers the same 9-item structure as 58-SR-1:
1. `vpp-pin` present and correct (DIP24_2716 HAS a vpp-pin — this is the positive case)
2. `rw-pin` = datasheet WE#/PGM# pin
3. `oe-pin` correct
4. `ce-pin` correct
5. `vcc-pin` and `gnd-pin` correct
6. Address bus pins — no overlap with VCC/GND/control
7. Data bus pins — no overlap
8. VPP-safety assertion (25V on the correct physical pin; not a 5V-only part)
9. All DIP pins accounted for

**Summary table format to copy** (lines 258–266):
```markdown
| Item | Result | Notes |
|------|--------|-------|
| vpp-pin present at correct pin | PASS/FAIL | pin N = VPP per 2516 datasheet |
| ... | ... | ... |

**Overall SR-1 result: PASS / NEEDS-REVIEW**

**Operator sign-off:** [ ] Approved — _name / date_
```

**Key difference from 58-SR-1:** DIP24_2716 DOES have a `vpp-pin` (this is a genuine UV-EPROM needing 25V programming), so item 1 is a positive VPP-presence check rather than a VPP-absence check.

---

### `firestarter_app/tests/test_database_conversion.py` (new W29C040 FLAG_CAN_ERASE assertion)

**Analog:** Lines 98–104 — `test_convert_at28c256_flash_eeprom_flag_can_erase`

**Exact pattern to copy** (lines 98–104):
```python
def test_convert_at28c256_flash_eeprom_flag_can_erase(db: EpromDatabase) -> None:
    """AT28C256 (Flash/EEPROM, routed to 0x0D) carries FLAG_CAN_ERASE — the flag is
    firmware-inert on the 0x0D configure_eeprom28c path (D-03), so setting it is safe."""
    full = db.get_eprom("AT28C256")
    assert full is not None
    out = db.convert_to_programmer(full)
    assert out["flags"] & FLAG_CAN_ERASE
```

**New assertion for W29C040 (0x05 Flash/EEPROM):**
```python
def test_convert_w29c040_flash_eeprom_flag_can_erase(db: EpromDatabase) -> None:
    """W29C040 (Flash/EEPROM, algorithm 0x05) carries FLAG_CAN_ERASE — extends the
    electrical-type derivation lock (ERASE-01 / D-01/D-02) to the flash4 family."""
    full = db.get_eprom("W29C040")
    assert full is not None
    out = db.convert_to_programmer(full)
    assert out["flags"] & FLAG_CAN_ERASE
```

**Placement:** Append after line 104 (after `test_convert_at28c256_flash_eeprom_flag_can_erase`), before the `# ---` separator at line 107.

**Imports already present** (lines 1–14): `FLAG_CAN_ERASE` from `firestarter.constants` and `EpromDatabase` from `firestarter.database` are already imported. The `db` fixture at line 11–14 (`skip_local_override=True`) is shared — reuse it.

**Negative-control pattern** (lines 89–95) is already present as `test_convert_uv_eprom_no_flag_can_erase` for M27C512 — no duplicate needed.

---

### `.planning/v1.15/bench/EVIDENCE.{md,json}` (bench validation evidence artifacts)

**Analog:** `firestarter_app/val-results/eprom/validation-matrix.{json,md}`

**JSON schema to copy** (val-results/eprom/validation-matrix.json, lines 1–15):
```json
{
  "generated": "2026-06-17T13:25:16Z",
  "harness_version": "71",
  "cells": [
    {
      "family": "eprom",
      "board": "leonardo",
      "tier": 3,
      "verdict": "PASS",
      "pass_type": "authoritative",
      "evidence_sha": "9521375d0847e99b46c6db8d5590d120aaea87c529272243decece3b22ef3490",
      "retry_count": 1
    }
  ]
}
```

**Adaptations for v1.15 EVIDENCE.json** (per-chip, not per-family):
- `"harness_version"`: `"81"` (this phase)
- One cell per physical chip in the 11-chip sweep
- Additional fields per cell: `"chip"` (part number), `"size_bytes"`, `"read_count"` (N≥3), `"blank_check_result"` (true/false), `"sha256"` of the read binary
- `"verdict"`: `"PASS"` / `"SKIP-no-chip"` / `"FAIL"`

**Markdown table to copy** (val-results/eprom/validation-matrix.md):
```markdown
# V1.15 Bench Validation Evidence

| Chip | Board | Reads | Blank? | SHA256 (first 16) | Verdict |
| ---- | ----- | ----- | ------ | ----------------- | ------- |
| 2516 | leonardo | 3 | yes | …                | PASS |
| ...  | ...      | … | …   | …                | …    |
```

**Location:** `.planning/v1.15/bench/EVIDENCE.md` and `.planning/v1.15/bench/EVIDENCE.json`. The `.planning/v1.15/` directory does not yet exist — create it along with the `bench/` subdirectory.

---

## Shared Patterns

### EpromDatabase fixture (hermetic, skip_local_override=True)
**Source:** `firestarter_app/tests/test_database_conversion.py`, lines 11–14
**Apply to:** All new test functions in `test_database_conversion.py`
```python
@pytest.fixture(scope="module")
def db() -> EpromDatabase:
    """Hermetic DB: no ``~/.firestarter`` override interference (Phase 36 D-06)."""
    return EpromDatabase(skip_local_override=True)
```
The 2516 user-override entry is INVISIBLE to this fixture — correct. It can only be verified manually via `firestarter info 2516` with the real `~/.firestarter/database.json` installed.

### FLAG_CAN_ERASE import
**Source:** `firestarter_app/tests/test_database_conversion.py`, line 7
```python
from firestarter.constants import FLAG_CAN_ERASE
```
Already present — no change needed.

### SR-1 pinout verification pattern
**Source:** `.planning/phases/58-pinout-re-derivation-24-pin-eeprom-unblock/58-SR-1-CHECKLIST.md`, lines 58–106
**Apply to:** `81-2516-SAFETY-REVIEW.md`
For DIP24_2716, the relevant pinouts.json entry already exists (the 2516 uses the pre-existing pinout, not a new one). The SR-1 review is for the chip entry's field values, not for a new pinout definition.

---

## No Analog Found

None — all four deliverables have close analogs in the codebase or planning artifacts.

---

## Metadata

**Analog search scope:** `firestarter_app/firestarter/data/`, `firestarter_app/tests/`, `firestarter_app/val-results/`, `.planning/phases/58-*/`, `.planning/phases/71-*/`
**Files scanned:** 8 source files, 4 planning artifacts
**Pattern extraction date:** 2026-06-23
