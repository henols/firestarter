---
phase: 60-display-layer-decode-correctness
reviewed: 2026-06-10T00:00:00Z
depth: standard
files_reviewed: 5
files_reviewed_list:
  - firestarter_app/firestarter/database.py
  - firestarter_app/firestarter/ic_layout.py
  - firestarter_app/firestarter/eprom_info.py
  - firestarter_app/tests/test_eprom_database.py
  - firestarter_app/tests/test_eprom_info.py
findings:
  critical: 0
  warning: 3
  info: 3
  total: 6
status: issues_found
---

# Phase 60: Code Review Report

**Reviewed:** 2026-06-10
**Depth:** standard
**Files Reviewed:** 5
**Status:** issues_found

## Summary

This change reroutes `firestarter info`'s Type / erasability / VPP / flag-description
rendering to use the DB `electrical.type` ground truth instead of `protocol_id`. The
core feature works correctly: I traced W27C512 (EEPROM), 2764/27C256 (UV-EPROM), and
the synthetic Flash/SRAM fixtures through `prepare_detailed_eprom_data` and confirmed
the Type label, can-erase row, and the `_interpret_flags` 0x10 description are now
consistent with `electrical.type`. The full test suite (incl. 28 snapshots) passes,
and ruff check + format are clean.

The adversarial pass surfaced one real display-correctness regression that the new
tests do not catch (spurious VPP row on every SRAM), one robustness regression
(`vpp_mv > 0` crashes on a string-typed user override where the prior `flags & 0x08`
gate did not), and a cross-view label inconsistency between `info` and `list`. None
rise to BLOCKER — no data-loss, no wire-protocol change, no hardware-command path is
touched (this is display-layer only).

## Warnings

### WR-01: Every SRAM now displays a spurious `VPP: 12.0v` row

**File:** `firestarter_app/firestarter/ic_layout.py:533-535`
**Issue:** The VPP gate was changed from `flags & 0x08` (always 0 → never shown) to
`eprom_data.get("vpp_mv", 0) > 0`. All 76 SRAM chips in the packaged
`chip_database.json` carry `vpp_mv=12000` (an upstream infoic.xml voltage-field
decode artifact — the `voltages & 0xF0` index maps to 12V even for SRAM; see
`reference_infoic_xml_field_decode`). Verified live: `DS1220` now renders
`Type: SRAM` with `VPP: 12.0v`, even though SRAM is volatile and has no VPP pin.
This directly contradicts the phase's own SRAM intent (the can-erase row is correctly
omitted for SRAM as "volatile", but VPP is not). The display now asserts a 12V
programming voltage for a chip that has none.
**Fix:** Suppress the VPP row for SRAM, consistent with the can-erase handling:
```python
# D-07-VPP: gate on vpp_mv > 0, AND exclude SRAM (volatile, vpp_mv is an
# upstream infoic.xml decode artifact, not a real programming voltage).
if etype != "SRAM" and eprom_data.get("vpp_mv", 0) > 0:
    output_data["vpp_str"] = f"{eprom_data.get('vpp_volts', 'N/A')}v"
```

### WR-02: `vpp_mv > 0` raises TypeError on a string-typed user override

**File:** `firestarter_app/firestarter/ic_layout.py:537`
**Issue:** `eprom_data.get("vpp_mv", 0) > 0` assumes `vpp_mv` is numeric.
`_map_data` (database.py:411) passes `electrical.get("vpp_mv", 0)` through unchanged
with no coercion (unlike `vpp`/`vcc`, which have try/except float parsing). A legacy
`~/.firestarter/database.json` override entry with `"vpp_mv": "12000"` (string) makes
`firestarter info <chip>` crash with `TypeError: '>' not supported between instances
of 'str' and 'int'` (reproduced). The prior `flags & 0x08` gate operated on an int and
had no such exposure, so this is a robustness regression for the user-override path.
**Fix:** Coerce defensively, e.g. in `build_specifications`:
```python
try:
    _vpp_mv = int(eprom_data.get("vpp_mv", 0) or 0)
except (TypeError, ValueError):
    _vpp_mv = 0
if etype != "SRAM" and _vpp_mv > 0:
    output_data["vpp_str"] = f"{eprom_data.get('vpp_volts', 'N/A')}v"
```
(Coercing `vpp_mv` to int in `_map_data` would also address it at the source.)

### WR-03: Synthetic SRAM fixture masks the real-DB VPP behavior (test gap)

**File:** `firestarter_app/tests/test_eprom_info.py:217-229, 301-312`
**Issue:** `SYNTH_SRAM_RAW` hardcodes `vpp_mv=0`, which does not reflect the live DB
where every SRAM has `vpp_mv=12000`. Consequently `test_synthetic_sram_no_can_erase_row`
passes while never exercising the spurious-VPP path (WR-01). The parametrized real-DB
smoke set (`test_type_label_and_erase_smoke`) contains no SRAM entry and asserts
nothing about VPP, so neither test guards the regression. A reviewer relying on green
tests would not see WR-01.
**Fix:** Set `vpp_mv=12000` in `SYNTH_SRAM_RAW` to mirror the DB, and add an assertion
that SRAM produces no `vpp_str` row (after WR-01 is fixed). Optionally add a real SRAM
chip (e.g. `DS1220`) to the smoke parametrization asserting `"vpp_str" not in result`.

## Info

### IN-01: `info` vs `list` now show different Type labels for the same chip

**File:** `firestarter_app/firestarter/eprom_info.py:337` (`print_eprom_list_table`)
**Issue:** `firestarter info W27C512` now shows `Type: EEPROM` (from `electrical.type`),
but `print_eprom_list_table` still calls `get_chip_type_string(ic.get("type", 0))` with
the mem_type int (1 → "EPROM") and gates its VPP column on `ic.get("type") == 1`. The two
views disagree on both Type and VPP for the EEPROM-family chips this phase targets. The
list table is outside the changed regions, but the inconsistency is a direct consequence
of this phase's reframing and will read as a bug to users.
**Fix:** Out of scope for this phase; track a follow-up to route the list table through
the same `electrical.type` source, or note the divergence intentionally.

### IN-02: Rewritten docstring references a non-existent `get_eprom(..., full=True)` API

**File:** `firestarter_app/firestarter/ic_layout.py:488` (also `eprom_info.py:99,102`)
**Issue:** The `build_specifications` docstring (rewritten in this phase) states
`eprom_data` comes from `EpromDatabase.get_eprom(..., full=True)`, but `get_eprom`
(database.py:526) takes only `chip_name` — there is no `full` parameter. Doc-rot that
misleads future maintainers.
**Fix:** Change to `EpromDatabase.get_eprom(name)`.

### IN-03: `etype == "EEPROM" or etype == "Flash/EEPROM"` reads less clearly than membership test

**File:** `firestarter_app/firestarter/ic_layout.py:527`
**Issue:** Style only (ruff does not flag it). A membership test is more idiomatic and
matches the analogous condition in `database.py:432`
(`electrical.get("type") in ("EEPROM", "Flash/EEPROM")`).
**Fix:** `if etype in ("EEPROM", "Flash/EEPROM"):`

---

_Reviewed: 2026-06-10_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
