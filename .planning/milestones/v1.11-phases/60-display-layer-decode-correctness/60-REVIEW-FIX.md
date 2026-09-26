---
phase: 60-display-layer-decode-correctness
fixed_at: 2026-06-10T00:00:00Z
review_path: .planning/phases/60-display-layer-decode-correctness/60-REVIEW.md
iteration: 1
findings_in_scope: 5
fixed: 5
skipped: 0
status: all_fixed
---

# Phase 60: Code Review Fix Report

**Fixed at:** 2026-06-10
**Source review:** `.planning/phases/60-display-layer-decode-correctness/60-REVIEW.md`
**Iteration:** 1

**Summary:**
- Findings in scope: 5 (WR-01, WR-02, WR-03, IN-02, IN-03; IN-01 explicitly out of scope per task)
- Fixed: 5
- Skipped: 0

## Fixed Issues

### WR-01: Every SRAM now displays a spurious `VPP: 12.0v` row

**Files modified:** `firestarter/ic_layout.py`
**Commit:** `3ccdfc2`
**Applied fix:** Added `etype != "SRAM"` guard to the VPP row gate in `build_specifications`.
All 76 SRAM chips in the packaged DB carry `vpp_mv=12000` as an upstream infoic.xml decode
artifact; the new guard suppresses the VPP row for SRAM regardless of `vpp_mv` value.

### WR-02: `vpp_mv > 0` raises TypeError on a string-typed user override

**Files modified:** `firestarter/ic_layout.py`
**Commit:** `3ccdfc2`
**Applied fix:** Wrapped the `vpp_mv` comparison in a `try/except (TypeError, ValueError)`
block that coerces to `int(...or 0)` before comparison, matching the defensive pattern used
for `vcc`/`vpp` in `_map_data`. Combined with WR-01 fix in a single code block.

### WR-03: Synthetic SRAM fixture masks the real-DB VPP behavior (test gap)

**Files modified:** `tests/test_eprom_info.py`
**Commit:** `3ccdfc2`
**Applied fix:** Set `vpp_mv=12000` in `SYNTH_SRAM_RAW` to mirror the live DB (comment
explains infoic.xml artifact). Added assertion `"vpp_str" not in result` to
`test_synthetic_sram_no_can_erase_row`, which now guards the WR-01 regression path.

### IN-02: Rewritten docstring references a non-existent `get_eprom(..., full=True)` API

**Files modified:** `firestarter/ic_layout.py`, `firestarter/eprom_info.py`
**Commit:** `3ccdfc2`
**Applied fix:** Changed `EpromDatabase.get_eprom(..., full=True)` to
`EpromDatabase.get_eprom(name)` in the `build_specifications` docstring; changed
`db.get_eprom(name, full=True)` and `db.get_eprom(name, full=False)` inline parameter
comments in `prepare_detailed_eprom_data` to `db.get_eprom(name)`.

### IN-03: `etype == "EEPROM" or etype == "Flash/EEPROM"` reads less clearly than membership test

**Files modified:** `firestarter/ic_layout.py`
**Commit:** `3ccdfc2`
**Applied fix:** Changed to `etype in ("EEPROM", "Flash/EEPROM")` for idiom parity with
`database.py:432`.

## Deferred / Out of Scope

### IN-01: `info` vs `list` now show different Type labels for the same chip

Explicitly out of scope for this fix run, as directed. The `print_eprom_list_table`
divergence in `eprom_info.py:337` is tracked in the review as a follow-up.

## Gate Results

All checks passed after fixes:

- `ruff check firestarter/ tests/` — All checks passed
- `ruff format --check firestarter/ tests/` — 55 files already formatted
- `pytest --cov=firestarter --cov-fail-under=70 -q` — 28 snapshots passed, coverage 75.93% >= 70%
- W27C512 info snapshot (`test_info_known_chip`) — unchanged, still passes (EEPROM, not SRAM)

**Submodule commit:** `3ccdfc2f767aee0802a91531bdf07c9f4af8a96f`
(branch `v1.11-infoic-decode-correctness` in `firestarter_app/`)

---

_Fixed: 2026-06-10_
_Fixer: Claude (gsd-code-fixer)_
_Iteration: 1_
