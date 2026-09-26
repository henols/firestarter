---
phase: 84-db-decode-audit-conditional-defect-rca-milestone-evidence-co
plan: "03"
subsystem: host-app
tags: [db-relabel, fram, can-erase, diff-db, label-only, decode-correctness]
dependency_graph:
  requires: []
  provides: [FM1608-FRAM-relabel, RULE_PHASE84_RELABEL, CAN_ERASE-pinning-tests]
  affects: [chip_database.json, ic_layout.py, eprom_info.py, diff_db.py, test_suite]
tech_stack:
  added: []
  patterns: [per-chip-codegen-override, diff-db-rule, display-layer-gate-extension]
key_files:
  created: []
  modified:
    - firestarter_app/tools/build_db.py
    - firestarter_app/tools/diff_db.py
    - firestarter_app/firestarter/ic_layout.py
    - firestarter_app/firestarter/eprom_info.py
    - firestarter_app/firestarter/data/chip_database.json
    - firestarter_app/tests/test_database_conversion.py
    - firestarter_app/tests/test_diff_db_gate.py
    - firestarter_app/tests/test_ic_layout.py
    - firestarter_app/tests/__snapshots__/test_characterization.ambr
decisions:
  - "sst-keep: SST39SF040 stays Flash/EEPROM; relabeling to Flash drops FLAG_CAN_ERASE (database.py:605); Phase-77/82 auto-erase preserved; observation recorded for DECODE-AUDIT plan 84-04"
  - "fm-fram-full: FM1608 SRAM→FRAM via build_db.py per-chip override after Pass-2; _ELECTRICAL_TYPE_LABEL extended; VPP gate widened to not-in-{SRAM,FRAM}"
  - "RULE_PHASE84_RELABEL placed before BUG_A_ETYPE in classify_diff chain (part_number-scoped rule must take priority for named chips)"
metrics:
  duration: "8 minutes"
  completed: "2026-06-25"
  tasks_completed: 4
  files_changed: 9
---

# Phase 84 Plan 03: DB Relabel (fm-fram-full / sst-keep) Summary

FM1608 SRAM→FRAM cosmetic relabel proven label-only; SST39SF040 kept Flash/EEPROM per D-40 STOP; diff_db RULE_PHASE84_RELABEL gate + CAN_ERASE pinning + FRAM display-layer guards all green.

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Checkpoint resolved (operator decisions) | (pre-resolved) | — |
| 2 | Wave-0 RED: RULE_PHASE84_RELABEL + CAN_ERASE + FRAM display tests | d8ca7a2 | diff_db.py, test_database_conversion.py, test_diff_db_gate.py, test_ic_layout.py |
| 3 | FM1608 relabel in build_db.py + ic_layout/eprom_info + regen | 47c86c9 | build_db.py, ic_layout.py, eprom_info.py, chip_database.json |
| 4 | Full-DB gates + snapshot update + ruff format | 4d5b3de | test_characterization.ambr, test_diff_db_gate.py, test_ic_layout.py |

## Task 1: Checkpoint Resolution (Operator Decisions)

The operator resolved the D-40 STOP-and-resurface checkpoint before execution. Per-chip decisions:

**SST39SF040 = sst-keep**
- **Collision:** Relabeling `Flash/EEPROM` → `Flash` would remove SST39SF040 from the
  `{"EEPROM","Flash/EEPROM"}` set at `database.py:605`, flipping `FLAG_CAN_ERASE` OFF.
  This breaks Phase-77/82-proven auto-erase (the very path that passed on silicon).
- **Decision:** KEEP `Flash/EEPROM`. No code change. The cosmetic `Flash` label
  observation is recorded here and forwarded to plan 84-04 DECODE-AUDIT.

**FM1608 = fm-fram-full**
- **Collision 1 (resolved):** Relabeling `SRAM` → `FRAM` turns ON the VPP display
  (`ic_layout.py` + `eprom_info.py` gate was `etype != "SRAM"`; FM1608 has
  `vpp_mv=12000` from infoic.xml artifact). Fix: extend gate to
  `etype not in {"SRAM","FRAM"}`.
- **Collision 2 (resolved):** `_ELECTRICAL_TYPE_LABEL` had no `"FRAM"` key —
  `resolve_type_label("FRAM")` would fall back to the protocol-based label instead
  of showing "FRAM". Fix: add `"FRAM": "FRAM"` to the map.
- **CAN_ERASE:** Unaffected — `FRAM ∉ {"EEPROM","Flash/EEPROM"}` at `database.py:605`.
- **Decision:** Proceed with fm-fram-full (relabel + display-layer companion changes).

## Task 2: Wave-0 RED (Tests First)

Added before any implementation, so they started RED for the display-layer tests:

**diff_db.py RULE_PHASE84_RELABEL:**
- New rationale entry in `_RATIONALES` explaining the FM1608 label correction
  and the SST39SF040 sst-keep observation.
- New field-path set in `_RULE_FIELD_PATHS`: `{("electrical","type")}`.
- New `_PHASE84_RELABEL_PART_NUMBERS = frozenset({"FM1608"})` — part_number scope.
- New elif branch in `_classify_diff` placed **before** `BUG_A_ETYPE` (so the
  part_number-scoped rule takes priority for named chips; BUG_A_ETYPE is a superset
  match that would otherwise win first).

**CAN_ERASE pinning assertions (test_database_conversion.py):**
- `test_sst39sf040_flag_can_erase_unchanged`: SST39SF040 carries FLAG_CAN_ERASE (sst-keep proof).
- `test_fm1608_flag_can_erase_off`: FM1608 does NOT carry FLAG_CAN_ERASE (label-only proof).
- Both were GREEN immediately (the current DB already has correct flags; the tests
  confirm the relabel won't change them).

**FRAM display-layer companion tests (test_ic_layout.py):**
- `test_electrical_type_label_includes_fram`: `_ELECTRICAL_TYPE_LABEL["FRAM"] == "FRAM"` — RED.
- `test_resolve_type_label_fram`: `resolve_type_label("FRAM") == "FRAM"` — RED.
- `test_fm1608_vpp_row_hidden_after_relabel`: FM1608 `vpp_str` absent after relabel — RED.

**diff_db unit tests (test_diff_db_gate.py TestDiffDbPhase84Relabel):**
- FM1608 SRAM→FRAM classified as RULE_PHASE84_RELABEL — was initially classified
  as BUG_A_ETYPE (until the priority reordering in diff_db.py was done).
- SST39SF040 type-only change NOT classified as RULE_PHASE84_RELABEL (sst-keep scope check).
- Unrelated chip type change NOT classified as RULE_PHASE84_RELABEL.

## Task 3: GREEN (Build_db.py Override + Display Changes)

**build_db.py:**
```python
# Phase 84 D-40 per-chip cosmetic relabel (fm-fram-full decision).
# Runs AFTER Pass-2 (line 644), BEFORE Site C (NMOS correction).
_PHASE84_RELABEL = {"FM1608": "FRAM"}
part_aliases_set = {a.split("@")[0].strip() for a in name.split(",")}
for _relabel_pn, _relabel_etype in _PHASE84_RELABEL.items():
    if _relabel_pn in part_aliases_set:
        _etype = _relabel_etype
        break
```
Does NOT touch `proto_id` / `pinout` / `vpp` / `algorithm` — label-only.

**ic_layout.py:**
- `_ELECTRICAL_TYPE_LABEL` extended: `"FRAM": "FRAM"` added.
- VPP gate: `etype != "SRAM"` → `etype not in {"SRAM", "FRAM"}`.

**eprom_info.py:**
- `print_eprom_list_table` VPP gate: `_etype != "SRAM"` → `_etype not in {"SRAM", "FRAM"}`.

**chip_database.json:**
- Regenerated via `python tools/build_db.py`. 744 chips. FM1608 `electrical.type = "FRAM"`.
- SST39SF040 unchanged: `Flash/EEPROM`.

**All Task 2 tests GREEN after this task.**

## Task 4: Full-DB Safety Gates + Final Cleanup

**check_dispatch.py exit 0:**
```
PASS: all 744 chips scanned; 734 supported; 10 chips confirmed non-dispatchable;
0 non_supported_dispatchable; 0 dispatch regressions; 0 consistency violations
```

**diff_db.py exit 0:**
- FM1608 classified as `BUG3_VCC_VDD` (primary — vcc/vdd swap pre-existing) + `electrical.type`
  as secondary delta. The secondary delta is in `_all_rule_paths` (claimed by RULE_PHASE84_RELABEL),
  so the chip IS fully explained (compound change, not unexplained). Exit 0 PASS.
- No other chip's `electrical.type` changed. No CAN_ERASE / VPP / pinout / algorithm delta.
- Baseline NOT re-pinned (diff guard preserved).

**Full host suite: 673/673 tests pass** (snapshot updated: FM1608 list row shows
`FRAM` instead of `SRAM`; VPP column stays `-`).

**CI-scoped ruff:** `ruff check firestarter/ tests/` + `ruff format --check firestarter/ tests/` → CLEAN.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Priority reordering of RULE_PHASE84_RELABEL in _classify_diff**
- **Found during:** Task 2 RED phase test run
- **Issue:** RULE_PHASE84_RELABEL was placed AFTER BUG_A_ETYPE in the elif chain.
  BUG_A_ETYPE matches all type-diff-without-algo-diff cases, so it claimed FM1608
  first. The test `test_fm1608_sram_to_fram_classified_as_phase84_relabel` failed
  with `got 'BUG_A_ETYPE'`.
- **Fix:** Moved RULE_PHASE84_RELABEL before BUG_A_ETYPE in the elif chain.
  The part_number scope check makes it more specific; it must precede the generic
  type-diff rule to take effect for named chips.
- **Files modified:** `tools/diff_db.py`
- **Commit:** d8ca7a2 (included in Task 2 commit)

**2. [Rule 2 - Missing functionality] Snapshot update for FM1608 list view**
- **Found during:** Task 4 full suite run
- **Issue:** `test_characterization.py::test_list` snapshot contained `SRAM` for FM1608
  but the live output now shows `FRAM`. Snapshot was legitimately stale.
- **Fix:** Updated snapshot via `--snapshot-update`.
- **Files modified:** `tests/__snapshots__/test_characterization.ambr`
- **Commit:** 4d5b3de

### SST39SF040: DECODE-AUDIT Observation (for plan 84-04)

SST39SF040 ships **no code change** (sst-keep decision). The following observation
is recorded for plan 84-04 DECODE-AUDIT.md:

> **SST39SF040 cosmetic-label observation:** The upstream minipro classification
> suggests `Flash` (not `Flash/EEPROM`). However, `electrical.type` is the SOLE
> input to `FLAG_CAN_ERASE` at `database.py:605`. SST39SF040 (proto 0x06, flash3)
> requires `Flash/EEPROM` to preserve `FLAG_CAN_ERASE = 0x02` on the wire, enabling
> the Phase-77/82-proven auto-erase path. The display label `Flash/EEPROM` is
> functionally correct for the RURP programmer's purposes even if cosmetically
> imprecise. To display `Flash` without breaking erase, a decoupled display/erase
> mechanism would be needed (sst-decouple path — not authorized this phase).

## Threat Surface Scan

No new network endpoints, auth paths, file access patterns, or schema changes at
trust boundaries introduced. The relabel affects only the `electrical.type` string
in the generated JSON (not a trust boundary in the network/auth sense). The
hardware-safety threats (T-84-07/08/09/10) were mitigated per the threat register:
- T-84-07: CAN_ERASE pinning tests + sst-keep decision confirm FLAG_CAN_ERASE unchanged.
- T-84-08: check_dispatch.py exit 0 (no dispatch/VPP-safety regression).
- T-84-09: VPP gate extended to not-in-{SRAM,FRAM}; FM1608 vpp_str absent (confirmed by test).
- T-84-10: Override in build_db.py (not hand-edit); diff_db.py guard preserved (no re-baseline).

## Self-Check: PASSED

| Check | Result |
|-------|--------|
| diff_db.py exists | FOUND |
| build_db.py exists | FOUND |
| ic_layout.py exists | FOUND |
| eprom_info.py exists | FOUND |
| chip_database.json exists | FOUND |
| test_database_conversion.py exists | FOUND |
| test_diff_db_gate.py exists | FOUND |
| SUMMARY.md exists | FOUND |
| commit d8ca7a2 (Task 2) | FOUND |
| commit 47c86c9 (Task 3) | FOUND |
| commit 4d5b3de (Task 4) | FOUND |
| RULE_PHASE84_RELABEL in diff_db.py | FOUND |
| FLAG_CAN_ERASE pinning assertions in test_database_conversion.py | FOUND |
| FM1608 type = FRAM in chip_database.json | VERIFIED |
| SST39SF040 type = Flash/EEPROM (unchanged) | VERIFIED |
| check_dispatch.py exit 0 | PASSED (734/10/0) |
| diff_db.py exit 0 | PASSED (15 chips explained) |
| Full host suite | PASSED (673/673) |
| CI-scoped ruff | CLEAN |
