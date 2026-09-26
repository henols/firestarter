---
phase: 60-display-layer-decode-correctness
plan: 01
subsystem: display
tags: [python, chip-database, ic_layout, eprom_info, electrical-type, decode-correctness]

requires:
  - phase: 59-correctness-gate
    provides: cca7d62 corrected electrical.type to EEPROM for W27C512/SST27VF512/etc.

provides:
  - "firestarter info derives Type/can-erase/VPP from electrical.type ground truth"
  - "D-03: _map_data sets info-flags 0x10 for EEPROM family (was Flash/EEPROM only)"
  - "D-07: _interpret_flags reconciled (0x10 = electrically erasable, dead entries removed)"
  - "D-01: build_specifications uses curated electrical_type->label map"
  - "D-02: can_erase_str derived from electrical.type not protocol_id"
  - "D-05: -- NOT VERIFIED -- marker removed"
  - "D-07-VPP: vpp_str gated on vpp_mv > 0 (not always-zero flags & 0x08)"
  - "D-04: synthetic per-electrical.type fixture tests + parametrized real-DB smoke set"

affects: [60-02, display-layer, ic_layout, test_characterization]

tech-stack:
  added: []
  patterns:
    - "electrical_type passed as explicit param from prepare_detailed_eprom_data to build_specifications (Option A plumbing)"
    - "curated _ELECTRICAL_TYPE_LABEL dict as sole type-label source with protocol-based fallback"

key-files:
  created: []
  modified:
    - firestarter_app/firestarter/database.py
    - firestarter_app/firestarter/ic_layout.py
    - firestarter_app/firestarter/eprom_info.py
    - firestarter_app/tests/test_eprom_database.py
    - firestarter_app/tests/test_eprom_info.py
    - firestarter_app/tests/__snapshots__/test_characterization.ambr

key-decisions:
  - "D-01: curated electrical_type->label map with 4 entries; fallback to protocol-based for absent/empty electrical.type"
  - "D-02: can_erase_str derives from electrical.type only — EEPROM/Flash -> electrically erasable, UV-EPROM -> UV-only, SRAM -> omit row"
  - "D-03/D-07 landed atomically: database.py L432 widened to in ('EEPROM', 'Flash/EEPROM'); _interpret_flags pruned to 0x10+0x20 only"
  - "D-05: verified_str key dropped entirely from output_data (presenter reads .get('verified_str', '') safely)"
  - "D-07-VPP: vpp_str gated on vpp_mv > 0 (was flags & 0x08 which was always 0)"
  - "Plumbing: Option A chosen — electrical_type passed as new keyword param to build_specifications"
  - "test_info_known_chip syrupy snapshot updated to post-fix correct W27C512 output"
  - "Pre-existing ruff I001 import-sort errors in test_address_parser.py/test_codec.py fixed (gate-blocking)"

requirements-completed: [DEC-01, DEC-02, DEC-03, DEC-04, DEC-05]

duration: 35min
completed: 2026-06-10
---

# Phase 60 Plan 01: Display-Layer Decode Correctness Summary

**`firestarter info` now derives Type/erasability/VPP from electrical.type ground truth: W27C512 shows EEPROM + electrically erasable + 12V VPP; 2764/M27C512/27C256 still show UV-EPROM + UV-only (no regression)**

## Performance

- **Duration:** ~35 min
- **Started:** 2026-06-10T08:35Z
- **Completed:** 2026-06-10T09:10Z
- **Tasks:** 3
- **Files modified:** 6

## Accomplishments

- Fixed all 6 confirmed display bugs (D-01 type label, D-02 can-erase, D-03 erasable bit, D-05 NOT VERIFIED marker, D-07 flags reconciliation, D-07-VPP VPP display)
- D-03 + D-07 landed atomically: `_map_data` and `_interpret_flags` now agree on bit 0x10 meaning "electrically erasable"
- W27C512 syrupy snapshot updated to reflect correct post-fix output (Type=EEPROM, Can be erased=yes, VPP=12.0v, Flags=0x30)
- Added 20 new tests: 3 erasable-flag unit + 3 interpret_flags unit + 7 synthetic fixture + 7 real-DB smoke
- Full suite: 539 tests passing, 75.97% coverage (up from 75.65% baseline), ruff clean

## Task Commits

1. **Task 1: Atomic D-03 + D-07-0x10** - `622ad37` (test + feat, TDD RED+GREEN in one atomic commit — D-03/D-07 must land together per Pitfall 4)
2. **Task 2: D-01/D-02/D-05/D-07-VPP** - `ea1cd32` (feat — display fixes + smoke tests + snapshot update)
3. **Task 3: Full-suite gate** - `833abee` (feat — ruff format/fix + verified 539 tests + 75.97% coverage)

## Files Created/Modified

- `firestarter_app/firestarter/database.py` — L432: widened erasable-bit condition to `in ("EEPROM", "Flash/EEPROM")`
- `firestarter_app/firestarter/ic_layout.py` — `_interpret_flags` reconciled (0x10=electrically erasable, dead entries removed); `build_specifications` accepts `electrical_type` param; `_ELECTRICAL_TYPE_LABEL` curated map added; D-02 can-erase and D-07-VPP vpp_str gating fixed; D-05 verified_str removed
- `firestarter_app/firestarter/eprom_info.py` — `prepare_detailed_eprom_data` passes `electrical_type` to `build_specifications`
- `firestarter_app/tests/test_eprom_database.py` — Added `TestErasableFlag` class (3 tests)
- `firestarter_app/tests/test_eprom_info.py` — Added `_interpret_flags` unit tests, synthetic per-electrical.type fixture tests, parametrized real-DB smoke set (7 chips); updated GATE-1.8b docstring
- `firestarter_app/tests/__snapshots__/test_characterization.ambr` — Updated `test_info_known_chip` snapshot to corrected W27C512 output

## Decisions Made

- Option A plumbing chosen (pass `electrical_type` as keyword param) — explicit, testable, minimal change to call sites
- `_ELECTRICAL_TYPE_LABEL` class-level dict with 4 entries + protocol-based fallback for absent/empty electrical.type (legacy override safety)
- SRAM: can_erase_str row omitted (volatile, no meaningful erasability)
- `verified_str` key dropped entirely from output_data dict rather than blanked — presenter uses `.get("verified_str", "")` so this is safe and produces no marker

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] `_map_data` requires manufacturer argument**
- **Found during:** Task 2 (synthetic fixture tests)
- **Issue:** `_map_synth` helper called `db._map_data(raw)` but the method signature requires `(ic, manufacturer)`
- **Fix:** Updated `_map_synth` to pass `manufacturer` argument
- **Files modified:** `tests/test_eprom_info.py`
- **Committed in:** ea1cd32 (Task 2 commit)

**2. [Rule 3 - Blocking] Pre-existing ruff I001 import-sort errors blocking gate**
- **Found during:** Task 3 (ruff check gate)
- **Issue:** `tests/test_address_parser.py` and `tests/test_codec.py` had pre-existing I001 (import block un-sorted) errors that caused `ruff check tests/` to fail
- **Fix:** Applied `ruff check --fix` to those two files (import sort only, no logic change)
- **Files modified:** `tests/test_address_parser.py`, `tests/test_codec.py`
- **Committed in:** 833abee (Task 3 commit)

---

**Total deviations:** 2 auto-fixed (both Rule 3 — blocking)
**Impact on plan:** Both fixes necessary for task completion. No scope creep.

## Issues Encountered

- Stash pop triggered a merge conflict in `firestarter/config.py` (from an old stash on a different branch). Resolved by `git restore --staged` + `git restore` to keep the current branch version. No actual content was lost.

## Next Phase Readiness

- Plan 02 (snapshot regeneration) is unblocked — all 6 display bugs are fixed and the test suite is clean
- `test_info_known_chip` snapshot updated to the correct post-fix output (regression canary ready)
- The `test_list` snapshot was NOT modified (uses a separate `print_eprom_list_table` code path via type-int only, not affected by D-01)

## Threat Flags

None — display-only host code reading a trusted local DB; no auth, session, access-control, crypto, network, or untrusted input.

## Known Stubs

None — all 6 display bugs fixed and wired to real DB data.

---

*Phase: 60-display-layer-decode-correctness*
*Completed: 2026-06-10*
