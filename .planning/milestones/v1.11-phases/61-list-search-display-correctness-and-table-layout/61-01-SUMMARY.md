---
phase: 61-list-search-display-correctness-and-table-layout
plan: "01"
subsystem: firestarter_app
tags: [display, list, search, type-label, vpp, table-layout, parity, tdd]
dependency_graph:
  requires: [Phase 60 electrical.type decode correctness, database._map_data, ic_layout.EpromSpecBuilder]
  provides: [single resolve_type_label helper, electrical-type in mapped dict, rewired print_eprom_list_table, parity tests]
  affects: [firestarter list, firestarter search, eprom_info.py, ic_layout.py, database.py]
tech_stack:
  added: []
  patterns: [single-source-of-truth helper, dynamic-width table, parametrized parity test, caplog fixture for logger capture]
key_files:
  created: []
  modified:
    - firestarter_app/firestarter/ic_layout.py
    - firestarter_app/firestarter/database.py
    - firestarter_app/firestarter/eprom_info.py
    - firestarter_app/tests/test_eprom_info.py
    - firestarter_app/tests/__snapshots__/test_characterization.ambr
decisions:
  - D-04: Single resolve_type_label helper on EpromSpecBuilder — _ELECTRICAL_TYPE_LABEL lookup + protocol fallback in one place; both info and list call it
  - D-05: Legacy fallback (None/"" electrical_type) returns protocol-based label via get_chip_type_string; never crashes
  - D-03: VPP gate is vpp_mv > 0 AND electrical-type != "SRAM" — identical to info gate; SRAM shows '-' despite vpp_mv=12000
  - D-01: Name width clamped to [13,20]; names >20 truncated with '…' ellipsis counting toward cap
  - D-02: VPP column width fixed at 5 (widened from 4); every voltage string is 5 chars
  - Snapshot update: test_list + test_search_w27 syrupy snapshots updated to reflect new table format (Rule 1 deviation)
metrics:
  duration: ~40 minutes
  completed: 2026-06-10
  tasks_completed: 3
  files_changed: 5
---

# Phase 61 Plan 01: List/Search Display Correctness and Table Layout Summary

**One-liner:** Rewire `firestarter list`/search Type+VPP through a single `resolve_type_label` helper sourced from `electrical.type`, eliminating the IN-01 info-vs-list divergence for EEPROM-family chips and SRAM spurious-VPP; enforce Name width [13,20] and VPP width 5.

## Tasks Completed

| Task | Name | Commit | Key files |
|------|------|--------|-----------|
| 1 | Shared resolve_type_label helper + electrical-type in _map_data | fca5f3e | ic_layout.py, database.py |
| 2 | Rewire print_eprom_list_table — Type+VPP via shared helper; width clamp | 1383934 | eprom_info.py |
| 3 | Parity + width-floor + legacy-fallback tests; update list/search snapshots | aebb7d0 | test_eprom_info.py, test_characterization.ambr |

## What Was Built

### Task 1: Single Source of Truth (ic_layout.py + database.py)

Added `EpromSpecBuilder.resolve_type_label(electrical_type, type_int, protocol_id)` as the single canonical label helper. It looks up the `_ELECTRICAL_TYPE_LABEL` curated map and falls back to `get_chip_type_string()` for legacy entries with absent `electrical.type` (D-05). `build_specifications` now calls this helper instead of its previously-inline block — the `_ELECTRICAL_TYPE_LABEL` dict is referenced only inside `resolve_type_label`.

In `database._map_data`, added `"electrical-type": electrical.get("type", "")` to the returned mapped dict so search/list results expose the ground-truth field (D-04).

### Task 2: Rewired print_eprom_list_table (eprom_info.py)

- **Type (D-04):** replaced `get_chip_type_string(ic.get("type"))` with `spec_builder.resolve_type_label(ic.get("electrical-type"), ic.get("type", 0), ic.get("protocol-id"))`.
- **VPP (D-03):** replaced `ic.get("type") == 1` gate with the info-parity gate: `int(vpp_mv or 0) > 0 AND electrical-type != "SRAM"`. SRAM chips (which carry `vpp_mv=12000` as an infoic.xml decode artifact) now correctly show `-`.
- **Name width (D-01):** dynamic `max(13, min(20, widest_rendered_name))`. Names >20 chars truncated to 19 + `…`.
- **VPP width (D-02):** fixed at 5 (from 4). All other columns (Manufacturer 17, Pins 5, Chip ID 11, Type 12) unchanged.

### Task 3: Tests (test_eprom_info.py)

Added 11 new tests (35 total in file), split across three categories:

- **D-06 parity (8 tests):** parametrized test for EEPROM display set (W27C512, SST27VF512, SST27SF512, W27C257) and UV-EPROM control set (M27C512, 27C256, 2764); one SRAM control test with synthetic `SRAM` row (mirrors live DB vpp_mv=12000 pattern). All assert `list_type_str == info_type_str` and `list_vpp_str == info_vpp_str`. SRAM control asserts Type=`SRAM`, VPP=`-`, and `12.0v` absent.
- **D-07 width-floor/no-break (1 test):** renders a 5-row `27C` slice + a synthetic long-name row (30-char alias `M48T08,M48T08Y,...`) and asserts divider segment widths are Name∈[13,20], Mfr=17, Pins=5, ChipID=11, Type=12, VPP=5; each body cell's visible content ≤ its column width.
- **D-05 legacy-fallback (2 tests):** assert `resolve_type_label(None)` and `resolve_type_label("")` return a non-empty string without raising.

Capture mechanism: `caplog.records[i].getMessage()` (not `caplog.text` which includes log-level prefix, and not `capsys` which does not capture `logger.info`).

## Final Gate Results

- **ruff check + ruff format --check:** CLEAN on all 4 changed files
- **mypy (non-strict):** 8 pre-existing errors in database.py/ic_layout.py; 0 new errors introduced
- **pytest tests/test_eprom_info.py:** 35/35 passed
- **pytest --cov=firestarter --cov-fail-under=70:** 550/550 passed, coverage 76.09% (floor 70%)

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Updated syrupy snapshots for test_list and test_search_w27**
- **Found during:** Task 3 final gate
- **Issue:** `test_characterization.py::test_list` and `test_characterization.py::test_search_w27` use syrupy snapshots that were correctly pinned to the old table format (14-wide Name, 4-wide VPP). After the Task 2 table changes, these snapshots correctly needed updating.
- **Fix:** `pytest --snapshot-update` on both tests regenerated the snapshots to reflect the new dynamic Name width and 5-wide VPP column.
- **Files modified:** `tests/__snapshots__/test_characterization.ambr`
- **Commit:** `aebb7d0` (included with Task 3 commit)

**2. [Rule 1 - Bug] Fixed caplog capture mechanism in tests**
- **Found during:** Task 3 first test run
- **Issue:** Initial implementation filtered `caplog.text.splitlines()` for lines starting with `|` or `+`. However `caplog.text` prepends the log-level and logger name (e.g. `INFO     EpromConsolePresenter:eprom_info.py:355 +---`), so a `lstrip().startswith("|")` filter missed all rows.
- **Fix:** Changed to `caplog.records[i].getMessage()` which returns the raw log message text without the prefix.
- **Files modified:** `tests/test_eprom_info.py`
- **Commit:** `aebb7d0` (included in same task commit — fix applied before committing)

**3. [Rule 1 - Bug] Fixed cell parsing to handle empty Chip ID cells**
- **Found during:** Task 3 first test run
- **Issue:** Cell extraction `[c.strip() for c in line.split("|") if c.strip()]` skipped empty cells (the Chip ID column is empty for chips without a chip-id value), yielding only 5 cells instead of 6.
- **Fix:** Changed to `line.split("|")[1:-1]` (drop only the leading/trailing empty strings from the outer `|` delimiters) then strip each cell, preserving empty Chip ID cells.
- **Files modified:** `tests/test_eprom_info.py`
- **Commit:** `aebb7d0`

## Known Stubs

None. All columns are wired to live DB data; no placeholder or hardcoded display values.

## Threat Flags

No new threat surface introduced. This is a pure read-path display change:
- No new endpoints, auth paths, or file access patterns.
- T-61-01 (long-name overflow) mitigated by Name-width clamp [13,20] + ellipsis.
- T-61-02 (spurious SRAM VPP) mitigated by D-03 gate.
- T-61-03 (legacy entry crash) mitigated by D-05 fallback in `resolve_type_label`.

## Self-Check: PASSED

| Check | Result |
|-------|--------|
| firestarter_app/firestarter/ic_layout.py exists | FOUND |
| firestarter_app/firestarter/database.py exists | FOUND |
| firestarter_app/firestarter/eprom_info.py exists | FOUND |
| firestarter_app/tests/test_eprom_info.py exists | FOUND |
| SUMMARY.md exists | FOUND |
| Task 1 commit fca5f3e exists | FOUND |
| Task 2 commit 1383934 exists | FOUND |
| Task 3 commit aebb7d0 exists | FOUND |
