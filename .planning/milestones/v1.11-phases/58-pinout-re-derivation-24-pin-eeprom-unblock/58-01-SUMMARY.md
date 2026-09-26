---
phase: 58-pinout-re-derivation-24-pin-eeprom-unblock
plan: "01"
subsystem: firestarter_app
tags: [pinouts, eeprom, tdd, safety, database, test-scaffolding]
dependency_graph:
  requires: []
  provides:
    - DIP24_2816 pinout entry in pinouts.json (SR-1-safe, no vpp-pin)
    - Five Wave 0 test classes in test_decoder.py (RED-first scaffolding)
  affects:
    - firestarter_app/firestarter/data/pinouts.json
    - firestarter_app/tests/test_decoder.py
tech_stack:
  added: []
  patterns:
    - RED-first TDD (Wave 0 test classes)
    - EpromDatabase(skip_local_override=True) integration test pattern
    - Import inside method body (established test convention)
    - SR-1 hardware-safety review for new pinout entry
key_files:
  created: []
  modified:
    - firestarter_app/firestarter/data/pinouts.json
    - firestarter_app/tests/test_decoder.py
decisions:
  - "DIP24_2816 pinout entry added with no vpp-pin field (SR-1-safe): pin 21 is rw-pin/WE, never VPP"
  - "TestDangerous24pinEEPROMFixed uses chip_database.json nested structure (programming.algorithm) for json.load tests and flat EpromDatabase structure (protocol-id, pin-map) for EpromDatabase tests"
  - "TestWarning5Rule is RED because CAT28C256 still has algorithm=0x07 in the current DB (AT28C256 was already fixed by WARNING-5)"
metrics:
  duration: 18min
  completed: "2026-06-09"
  tasks_completed: 2
  tasks_total: 2
  files_modified: 2
---

# Phase 58 Plan 01: Wave 0 Test Scaffolding + DIP24_2816 Pinout Entry

**One-liner:** SR-1-safe DIP24_2816 pinout entry (no vpp-pin) added to pinouts.json; five Wave 0 RED-first test classes committed establishing the GREEN bar for Plan 02.

## Summary

Plan 01 lays the test-first foundation for Phase 58's principled `resolve_pinout_key` rewrite and 24-pin EEPROM unblock. Two submodule commits:

1. **Task 1** (`feat`): `DIP24_2816` pinout entry added to `firestarter_app/firestarter/data/pinouts.json`, positioned immediately after `DIP24_6116` to keep the DIP24 family grouped. Electrically identical to DIP24_6116 (same JEDEC 24-pin 5V layout) but distinct for SR-1 traceability as a 5V EEPROM entry. The defining safety property: NO `vpp-pin` key — pin 21 is `rw-pin` (WE), never VPP. Contrast with DIP24_2716 which has `vpp-pin=[21]`.

2. **Task 2** (`test`): Five Wave 0 test classes appended to `firestarter_app/tests/test_decoder.py` following the established `TestBuildDbDecodeCorrectness` import-inside-method pattern. ruff check + ruff format clean.

## Wave 0 Test Class Status

| Class | Methods | Status | Why RED / Why GREEN |
|-------|---------|--------|---------------------|
| `TestResolvedPinoutKey` | 16 | **RED** | Current `resolve_pinout_key` signature lacks `type_int` and `mem_size` params (`TypeError` on all calls). Plan 02 rewrites the function to accept these. |
| `TestGuessTablesDeleted` | 3 | **RED** | `PIN_MAP_TO_PINOUT`, `PIN_MAP_PROTO_TO_PINOUT`, `DIP28_VARIANT_MAP` still present in build_db. Plan 02 deletes them. |
| `TestWarning5Rule` | 1 | **RED** | `CAT28C256` has `programming.algorithm=0x07` in current DB (WARNING-5 fired for AT28C256 but not CAT28C256). Plan 02 rewrite + DB regen fixes all pm_idx=20 chips. |
| `TestDIP24_2816Pinout` | 6 | **GREEN** | Depends only on Task 1 — DIP24_2816 exists in pinouts.json with correct pin assignments and no vpp-pin. SR-1 gate passes. |
| `TestDangerous24pinEEPROMFixed` | 10 | **RED** | 10 dangerous chips still have `algorithm=0x0B` + `pinout=DIP24_2716`; 9 blocked chips (AT28C04/AT28C16 family) not yet in DB (still skipped by current build_db). Plan 02 rewrite + DB regen fixes all. |

**RED-first bar for Plan 02:** All 30 RED test methods must turn GREEN after Plan 02's build_db.py rewrite + DB regeneration.

## Commits

| Hash | Type | Description |
|------|------|-------------|
| `fa0c1a4` | `feat(58-01)` | Add DIP24_2816 pinout entry (SR-1-safe, no vpp-pin) |
| `11eb51a` | `test(58-01)` | Add five Wave 0 test classes for PIN-01/02/03 (RED-first) |

Both commits are in the `firestarter_app` submodule on branch `v1.11-infoic-decode-correctness`.

## Deviations from Plan

**1. [Rule 1 - Bug] Fixed TestDangerous24pinEEPROMFixed to use nested JSON structure**

- **Found during:** Task 2 — chip_database.json stores `algorithm` under `programming.algorithm` and `pin_count` under `electrical.pin_count`, not at root level. EpromDatabase returns a flat dict using `protocol-id` and `pin-map`, not `algorithm` and `pinout`.
- **Fix:** Updated all `_find_chip`-based tests to access `chip.get("programming", {}).get("algorithm")` and `chip.get("pinout")` (pinout is at root level in JSON). Updated EpromDatabase-based tests to use `chip.get("protocol-id")` and `chip.get("pin-map")`.
- **Files modified:** `firestarter_app/tests/test_decoder.py`
- **Commit:** `11eb51a`

**2. [Rule 1 - Bug] Fixed TestWarning5Rule to search chip_database.json nested fields**

- **Found during:** Task 2 — original test used `chip.get("pin_count")` (wrong key); correct key is `chip.get("electrical", {}).get("pin_count")`.
- **Fix:** Updated the AT28C256 lookup to use the nested `electrical.pin_count` path.
- **Files modified:** `firestarter_app/tests/test_decoder.py`
- **Commit:** `11eb51a`

**3. [Rule 2 - Missing critical] Applied ruff format**

- **Found during:** Task 2 — ruff format check flagged test_decoder.py for reformatting after appending the new classes.
- **Fix:** Applied `python3 -m ruff format tests/test_decoder.py` before committing.
- **Files modified:** `firestarter_app/tests/test_decoder.py`
- **Commit:** `11eb51a`

## Known Stubs

None — this plan adds only a static data entry and test scaffolding. The tests are intentionally RED-first (not stubs).

## Threat Flags

None. No new network endpoints, auth paths, or schema changes at trust boundaries. The only new surface is the DIP24_2816 pinout entry, which is covered by T-58-01 (no vpp-pin field — verified by Task 1 assertion and `TestDIP24_2816Pinout::test_dip24_2816_has_no_vpp_pin_field`).

## Self-Check: PASSED

Files created/modified:
- `/workspaces/firestarter_app/firestarter/data/pinouts.json` — FOUND (DIP24_2816 entry verified)
- `/workspaces/firestarter_app/tests/test_decoder.py` — FOUND (36 new test methods collected)

Commits verified:
- `fa0c1a4` — FOUND (git -C firestarter_app log --oneline -5)
- `11eb51a` — FOUND (git -C firestarter_app log --oneline -5)

TestDIP24_2816Pinout: 6 passed (GREEN confirmed)
TestResolvedPinoutKey: 16 FAILED as expected RED
TestGuessTablesDeleted: 3 FAILED as expected RED
TestWarning5Rule: 1 FAILED as expected RED
TestDangerous24pinEEPROMFixed: 10 FAILED as expected RED
