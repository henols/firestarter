---
phase: 77-erase-write-path-graduation-0x07-ee-eproms
plan: 01
subsystem: database
tags: [flag_can_erase, electrical-type, convert_to_programmer, wire-protocol, erase]

requires:
  - phase: 76-x88c64-at28c-spec-classification
    provides: electrical.type ground truth + WARNING-5 0x07/0x0D dispatch split
provides:
  - convert_to_programmer derives FLAG_CAN_ERASE canonically from electrical-type (not synthetic info-flags round-trip)
  - 3 wire-level FLAG_CAN_ERASE lock tests (EEPROM set / UV-EPROM clear / Flash-EEPROM set)
affects: [77-03, 77-04, erase-write-path]

tech-stack:
  added: []
  patterns: [canonical-field-derivation-over-synthetic-roundtrip]

key-files:
  created: []
  modified:
    - firestarter_app/firestarter/database.py
    - firestarter_app/tests/test_database_conversion.py

key-decisions:
  - "Read electrical-type directly in convert_to_programmer instead of info-flags & 0x10 (D-01/D-02)"
  - "Record D-03 firmware-inert confirmation as in-code comment (no firmware edit)"

patterns-established:
  - "Wire-flag derivations key off the same canonical field _map_data uses, locked by wire-output tests"

requirements-completed: [ERASE-01]

duration: 6min
completed: 2026-06-22
---

# Phase 77 Plan 01: Canonical FLAG_CAN_ERASE Derivation Summary

**`convert_to_programmer` now sets FLAG_CAN_ERASE directly from `electrical-type ∈ {EEPROM,Flash/EEPROM}`, locked by 3 wire-level tests — a zero-behavioral-delta canonicality improvement (RF-01).**

## Performance

- **Duration:** ~6 min
- **Started:** 2026-06-22T06:45:00Z
- **Completed:** 2026-06-22T06:51:00Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments
- Added 3 named wire-level tests asserting `out["flags"] & FLAG_CAN_ERASE`: W27C512 set, M27C512 (UV-EPROM negative control) clear, AT28C256 (Flash/EEPROM, 0x0D) set.
- Switched the `convert_to_programmer` flag derivation from the synthetic `info-flags & 0x00000010` round-trip to the canonical `electrical-type` field membership check.
- Recorded the D-03 firmware-inert assertion in-code: the 0x0D `configure_eeprom28c` path (`firestarter/src/proms/eeprom_28c.cpp`) reads only `FLAG_FORCE` / `FLAG_SKIP_BLANK_CHECK`, never `FLAG_CAN_ERASE` — verified by grep before encoding the comment.

## Task Commits

1. **Task 1 (RED): add 3 wire-level FLAG_CAN_ERASE tests** — `92898f8` (test)
2. **Task 2 (GREEN): canonical electrical-type derivation** — `b55dd86` (refactor)

(committed inside the `firestarter_app` submodule on branch `v1.14-feasible-gap-implementation`)

## Files Created/Modified
- `firestarter_app/firestarter/database.py` — `convert_to_programmer` flag block reads `electrical-type`; D-01/D-02/D-03 documented in-code
- `firestarter_app/tests/test_database_conversion.py` — `FLAG_CAN_ERASE` import + 3 lock tests

## Decisions Made
- None beyond the plan. RF-01 zero-delta confirmed empirically (see below).

## Deviations from Plan
None - plan executed exactly as written.

## Issues Encountered
- **Pre-edit observed state (RED):** All 3 new tests PASSED *before* the source edit, exactly as RESEARCH RF-01 predicted — the flag was already correct on the wire via the synthetic `info-flags & 0x10` indirection. The tests therefore LOCK the derivation rather than fill a gap; the GREEN edit is a canonicality refactor with zero behavioral delta. Post-edit: all 17 tests in the file pass; ruff clean (`target-version=py39`).

## Next Phase Readiness
- Plan 03 can now run the post-edit gate evidence (check_dispatch.py, parity, suite+coverage).
- Plan 04 (bench) depends on this wiring being on the wire — satisfied.

---
*Phase: 77-erase-write-path-graduation-0x07-ee-eproms*
*Completed: 2026-06-22*
