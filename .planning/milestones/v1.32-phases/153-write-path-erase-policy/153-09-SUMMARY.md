---
phase: 153-write-path-erase-policy
plan: 09
subsystem: testing
tags: [python, pytest, erase-policy, wire-protocol, sdp, host]

# Dependency graph
requires:
  - phase: 153-07
    provides: "FLAG_CAN_ERASE restored on the wire for all 84 algorithm-13 rows at the source (database.py's exclusion tuple)"
provides:
  - "Conversion-layer proof that AT28C256 (and the other 83 algorithm-13 rows by extension) carries FLAG_CAN_ERASE, by name and by assertion"
  - "SDP composed-command wire-shape proof that the erase bit is restored, asserted against the named FLAG_CAN_ERASE constant"
  - "A previously-silent tier-2 family wire contract (eeprom28c) now pins the capability bit and its exclusivity (no skip/sector bits)"
  - "Host suite reduced from the inherited 7 failures to exactly 5 (plan 10's remaining set), verified by name"
affects: [153-10, 153-11, 153-12, 153-13, 153-16]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Assertion inversion keeps a positive assertion and extends (never replaces) the REVERSAL RECORD docstring voice, appending each new reversal in sequence"
    - "New capability-flag legs observed FAILING against a temporary local revert of the source tuple edit before being trusted as real gates (T-153-48 anti-vacuity proof)"

key-files:
  created: []
  modified:
    - firestarter_app/tests/test_database_conversion.py
    - firestarter_app/tests/test_eprom_operations.py
    - firestarter_app/tests/test_val_wire_eeprom28c.py

key-decisions:
  - "Both negative controls (M27C512 UV-EPROM, W29C040 algorithm-5) left byte-unchanged; git diff shows zero hunks inside either function body -- the scope proof that the flag did not bleed to a 12V-hazard or UV-EPROM exclusion"
  - "SDP wire-shape docstring cites D-153-05 explicitly: carrying the bit on an SDP frame does not mean an SDP command erases -- the bit is a capability advertisement read only by eprom_erase's standalone refusal gate"
  - "New tier-2 legs assert against the named FLAG_CAN_ERASE constant, not a bare integer, and the second leg cites D-153-04's sector-address disposition (0x0D erase is device-global by construction)"

requirements-completed: []
# ERASE-03 is NOT flipped here -- plans 10, 11, 12, 13 also claim it and have not yet run.

coverage:
  - id: D1
    description: "Invert the AT28C256 conversion test (test_database_conversion.py) to assert FLAG_CAN_ERASE SET, renamed to state the outcome, with both negative controls left untouched"
    requirement: "ERASE-03"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_database_conversion.py -o addopts=\"\" -q -- 20 passed"
        status: pass
    human_judgment: false
  - id: D2
    description: "Invert the SDP composed-command wire-shape test (test_eprom_operations.py) to assert the erase bit is CARRIED, against the named FLAG_CAN_ERASE constant"
    requirement: "ERASE-03"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_eprom_operations.py -k SdpOperationsWireShape -o addopts=\"\" -q -- 6 passed; full module -- 43 passed"
        status: pass
    human_judgment: false
  - id: D3
    description: "Add two new tier-2 wire-contract legs in test_val_wire_eeprom28c.py pinning the restored capability bit and its exclusivity (no skip/sector flags), both observed failing against a temporary revert"
    requirement: "ERASE-03"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_val_wire_eeprom28c.py -o addopts=\"\" -q -- 6 passed (4 pre-existing + 2 new)"
        status: pass
    human_judgment: false

# Metrics
duration: 45min
completed: 2026-08-21
status: complete
---

# Phase 153 Plan 09: Invert Host Erase-Bit Assertions and Pin the Family Wire Contract Summary

**Inverted the two committed host assertions that pinned FLAG_CAN_ERASE clear (conversion layer + SDP wire-shape layer), and added the positive capability-flag proof the eeprom28c tier-2 wire suite was missing — leaving both anti-bleed negative controls provably untouched.**

## Performance

- **Duration:** ~45 min
- **Completed:** 2026-08-21
- **Tasks:** 3/3 completed
- **Files modified:** 3

## Accomplishments

- **Task 1 — Inverted `test_database_conversion.py`'s AT28C256 test.** Renamed
  `test_convert_at28c256_flash_eeprom_flag_can_erase_cleared` to
  `test_convert_at28c256_flash_eeprom_flag_can_erase_set`, inverted the assertion from
  `== 0` to a positive truthiness check (`assert out["flags"] & FLAG_CAN_ERASE`). Extended
  the existing Phase 121 D-12 REVERSAL RECORD docstring in place with the fourth reversal:
  D-12's policy was correct given its premise, but Phase 153 changed the premise — a real
  `CMD_ERASE` arm now exists in `configure_eeprom28c`, and `eprom_operations.cpp`'s
  `eprom_erase` precondition reads the flag as its refusal gate, so the bit is no longer
  firmware-inert on this protocol. Recorded as mechanism-corrected/intent-satisfied. Both
  negative controls (`test_convert_uv_eprom_no_flag_can_erase`,
  `test_convert_w29c040_no_flag_can_erase`) confirmed byte-unchanged via `git diff` (zero
  hunks inside either function). Module: **20 passed**.
- **Task 2 — Inverted `test_eprom_operations.py`'s SDP wire-shape test.** Renamed
  `test_sdp_command_flags_do_not_carry_the_db_can_erase_bit` to
  `test_sdp_command_flags_carry_the_db_can_erase_bit`, inverted the assertion to compare
  against the named `FLAG_CAN_ERASE` constant (imported locally, matching the file's
  existing per-test import idiom) rather than a bare integer. Docstring extended with the
  Phase 153 reversal and an explicit D-153-05 citation forecloses the misreading that a
  carried bit on an SDP frame means an SDP command erases — it is a capability
  advertisement read only by the standalone-erase precondition. Class filter: **6 passed**;
  full module: **43 passed**.
- **Task 3 — Added two new legs to `test_val_wire_eeprom28c.py`.**
  `test_eeprom28c_wire_dict_carries_flag_can_erase` asserts the family's representative
  chip (AT28C256, read from `validation_matrix_spec.json`, unchanged) carries the bit in
  the wire dict built via `EpromDatabase.convert_to_programmer()`.
  `test_eeprom28c_wire_dict_carries_no_skip_or_sector_flags` asserts the wire `flags` value
  carries **only** the capability bit, citing D-153-04 (0x0D erase is device-global by
  construction, no sector address participates). Both legs were observed FAILING
  (`wire flags 0x00 must carry FLAG_CAN_ERASE`) against a temporary local revert of
  `database.py`'s exclusion tuple from `(5,)` back to `(5, 13)`; the revert was then undone
  and confirmed via `git diff --quiet -- firestarter/database.py`. Module docstring
  extended with the design-list addition and an explicit note on what is deliberately
  *not* pinned (operation-time skip flags, sector addressing — composed by the CLI, not
  the database). `validation_matrix_spec.json` untouched (`git diff --stat` empty). Module:
  **6 passed** (4 pre-existing + 2 new).
- **Remaining red set confirmed by name.** Scoped run of the three files plan 10 owns
  (`test_chip_test.py`, `test_chip_test_blank_check_order.py`,
  `test_chip_test_sdp_leg.py`) shows exactly **5 failed, 189 passed** —
  `test_devtest01_0x0d_sweep_erase_is_na_and_erase_eprom_never_called`,
  `test_count_applicable_sdp_gated_allow_chip_ratio_drops`,
  `test_count_applicable_sdp_banner_row_renders_the_dropped_ratio`,
  `test_at28c256_blank_check_is_na_with_family_fact_reason`,
  `test_baseline_gate_closes_dead_write_path_allow_chip_full_leg` — matching the inherited
  7-failure count minus this plan's 2 fixes. Per the wave constraint, the full host suite
  (deliberately RED until plan 12) was not run to completion; a background full-suite
  invocation was started in error and killed immediately without being relied upon.
- **`ruff check` / `ruff format --check`** pass on all three touched files.
- **mypy watermark:** `35 == 35`, verified on a `uv venv --python 3.11` (the app's actual
  CI interpreter) — the devcontainer's native Python 3.12 fails open on an unrelated
  numpy-stub syntax error, a pre-existing environment mismatch, not this plan's change.
- `firestarter/` sub-repo confirmed clean of tracked modifications (`git status --short`
  empty); `tools/check_dispatch.py` confirmed untouched (`git diff --quiet` holds).

## Task Commits

1. **Task 1: Invert and rename the conversion test, leaving both negative controls untouched** - `0bb663f` (test, firestarter_app)
2. **Task 2: Invert the SDP-command wire-shape leg in `test_eprom_operations.py`** - `1683156` (test, firestarter_app)
3. **Task 3: Pin the erase bit in the tier-2 EEPROM28c wire round-trip suite** - `7a497b0` (test, firestarter_app)

**Plan metadata:** pending (this commit)

## Files Created/Modified
- `firestarter_app/tests/test_database_conversion.py` - AT28C256 test renamed + inverted to assert FLAG_CAN_ERASE SET; both negative controls untouched
- `firestarter_app/tests/test_eprom_operations.py` - SDP composed-command wire-shape test renamed + inverted to assert erase bit CARRIED, against the named constant
- `firestarter_app/tests/test_val_wire_eeprom28c.py` - two new capability-flag legs pinning the eeprom28c family's restored wire contract

## Decisions Made
- Extended existing REVERSAL RECORD docstrings in place rather than replacing them, preserving the full Phase 119/120/121 reversal chain as history.
- Imported `FLAG_CAN_ERASE` locally inside the SDP wire-shape test (matching the file's existing per-test import idiom for `FLAG_SKIP_SDP_UNLOCK`) rather than adding a module-level import, for consistency with the surrounding file style.
- Chose to prove the two new tier-2 legs' failure-capability via a temporary local revert-and-restore of `database.py` rather than trusting them on inspection alone, per T-153-48's anti-vacuity requirement.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

A scoped background full-host-suite invocation was started while gathering context on the remaining red set; this violates the wave-level "no plan may run the full host suite" constraint (it is deliberately RED until plan 12, and running it risks cross-plan-execution contention). It was killed immediately and its result was never used — the remaining red set was instead confirmed via a scoped run of exactly the three files plan 10 owns.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- ERASE-03's host proof now spans conversion layer, SDP composed-command wire layer, and the eeprom28c tier-2 family wire contract — all three assert the restored capability bit positively.
- Remaining red set (5, all plan 10's) confirmed by name: `test_chip_test.py`'s sweep + two count/banner accountings, `test_chip_test_blank_check_order.py` case 3, `test_chip_test_sdp_leg.py`'s baseline gate.
- No blockers for plan 10.

---
*Phase: 153-write-path-erase-policy*
*Completed: 2026-08-21*

## Self-Check: PASSED
