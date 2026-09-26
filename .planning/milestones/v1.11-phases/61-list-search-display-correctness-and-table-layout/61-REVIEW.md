---
phase: 61-list-search-display-correctness-and-table-layout
reviewed: 2026-06-10T00:00:00Z
depth: standard
files_reviewed: 4
files_reviewed_list:
  - firestarter/ic_layout.py
  - firestarter/database.py
  - firestarter/eprom_info.py
  - tests/test_eprom_info.py
findings:
  critical: 0
  warning: 2
  info: 2
  total: 4
status: issues_found
---

# Phase 61: Code Review Report

**Reviewed:** 2026-06-10
**Depth:** standard
**Files Reviewed:** 4
**Status:** issues_found

## Summary

Phase 61 introduces a shared `resolve_type_label` helper on `EpromSpecBuilder`, wires both
`build_specifications` (info view) and `print_eprom_list_table` (list view) through it, and
adds a dynamic name-column width clamp plus a new VPP gate. The structural refactor is sound:
the D-04 single-helper guarantee is correctly implemented, the D-03 gate logic is identical in
both views, the D-05 `or 0` coercion is defensive and correct, and the column arithmetic is
consistent between the divider/header/body strings (confirmed by calculation and by all 550
tests passing).

Two residual parity gaps survive in the legacy-entry fallback paths. Neither is triggered by any
of the 743 current DB chips, but both constitute spec violations under D-03/D-04 and are latent
landmines for operator-written `~/.firestarter/database.json` overrides.

---

## Warnings

### WR-01: Fallback label from `get_chip_type_string` overflows the 12-char Type column

**File:** `firestarter/eprom_info.py:384` (and `firestarter/ic_layout.py:506`)

**Issue:** The Type column is formatted with `{type_str: <12}`, a fixed-width field of 12
characters. `resolve_type_label` falls back to `get_chip_type_string` whenever
`electrical-type` is absent or not in `_ELECTRICAL_TYPE_LABEL`. The protocol-based labels
returned by that fallback range from 13 to 39 characters — examples:

| protocol | label | chars |
|---|---|---|
| 0x0B | `"UV-EPROM (legacy 24-pin)"` | 24 |
| 0x0D | `"EEPROM (5V parallel, 28C-family)"` | 32 |
| 0x05 | `"Flash/EEPROM (5V, AMD-std)"` | 26 |
| 0x06 | `"Flash/EEPROM (5V, AMD-alt sector-erase)"` | 39 |

Any of those labels will blow past the 12-char padding and rupture table alignment. All
743 current DB chips carry a known `electrical-type` so the path is not triggered today.
However, the D-07 width test (`test_width_floor_and_no_overflow`) uses only current DB
chips plus a synthetic SRAM row — it does not exercise the fallback path, so this
overflow can silently appear when an operator-override entry omits `electrical.type`, or
when `build_db.py` emits a novel type value not yet in `_ELECTRICAL_TYPE_LABEL`.

**Fix:** Truncate `type_str` to the column width before formatting, or add an explicit
clamp in `print_eprom_list_table`:

```python
# In print_eprom_list_table, before the logger.info body line:
type_str_display = type_str[:12] if len(type_str) > 12 else type_str
# then use type_str_display in the f-string
logger.info(
    f"| {name: <{name_w}}| {ic.get('manufacturer', ''): <17}|"
    f"{ic.get('pin-count', 0): >5} | {chip_id_str: <11}| {type_str_display: <12}| {vpp_str: <5}|"
)
```

Alternatively, add a guard case for short labels in `_ELECTRICAL_TYPE_LABEL` (the four
current entries all fit) and document that any new type value added there must be ≤12 chars.

---

### WR-02: `vpp_str` fallback value diverges between list and info views

**File:** `firestarter/eprom_info.py:373` vs `firestarter/ic_layout.py:578`

**Issue:** When the D-03 gate passes (`vpp_mv > 0` AND `etype != "SRAM"`) but
`vpp_volts` is absent from the dict, the two views produce different output:

```python
# list view (eprom_info.py L373):
vpp_str = f"{ic.get('vpp_volts', '-')}v"   # absent → "-v"

# info view (ic_layout.py L578):
output_data["vpp_str"] = f"{eprom_data.get('vpp_volts', 'N/A')}v"  # absent → "N/Av"
```

This violates D-03's parity guarantee. The `test_list_vs_info_parity` test does not
catch it because all 743 current DB chips have `vpp_volts` populated by `_map_data`,
so the fallback branch is never hit. An operator-override entry with `vpp_mv > 0` but
no `vpp_volts` key will produce mismatched display.

Note: `"-v"` (list) and `"N/Av"` (info) are also visually different artefacts — neither
is a well-formed voltage string.

**Fix:** Align the fallback to `"N/A"` in both views (matching the info convention), or
preferably suppress the VPP cell when `vpp_volts` is absent, consistent with the SRAM
gate:

```python
# list view: mirror info exactly
_vpp_volts = ic.get("vpp_volts")
if _etype != "SRAM" and _vpp_mv > 0 and _vpp_volts is not None:
    vpp_str = f"{_vpp_volts}v"
else:
    vpp_str = "-"
```

---

## Info

### IN-01: Redundant `etype` local in `build_specifications` after refactor

**File:** `firestarter/ic_layout.py:533`

**Issue:** After the refactor, `build_specifications` still computes:
```python
etype = electrical_type or ""
chip_type_str = self.resolve_type_label(electrical_type, ...)
```
The local `etype` is correctly used further down for the `can_erase_str` and `vpp_str`
gates (lines 563, 577), so it is not dead code. However, the `etype` assignment on
line 536 is now cosmetically redundant with the `etype = electrical_type or ""` implicit
in `resolve_type_label` itself. This is harmless but worth noting for a future cleanup: the
comment on line 534 says "etype = electrical_type or ''" is for the `if etype in (...)` guards
below, not for `resolve_type_label`. No change needed; just clarify the comment if desired.

**Fix:** No code change required. Optionally tighten the inline comment to make clear that
`etype` serves the `can_erase_str`/`vpp_str` gates below, not the `resolve_type_label` call.

---

### IN-02: Unreachable `default=13` in `max()` generator expression

**File:** `firestarter/eprom_info.py:352`

**Issue:**
```python
name_w = max(13, min(20, max((len(n) for n in rendered_names), default=13)))
```
The inner `max(..., default=13)` guard against an empty generator is unreachable: the
function returns early at line 331 (`if not eproms_data: return`), so `rendered_names`
is always non-empty when this line executes. The `default=13` is harmless defensive
code but adds a small amount of cognitive noise.

**Fix:** Either remove `default=13` (trusting the early return), or replace with a comment
explaining why it is retained as belt-and-suspenders. No functional impact either way.

---

_Reviewed: 2026-06-10_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
