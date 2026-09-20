# Phase 197 — The 746-Row Regeneration Diff

**Measured:** 2026-09-18, against `firestarter_app` HEAD `b864cd7` (this plan's Task 1 commit) on
`v1.40-program-parameter-fidelity`, after plans `197-01` through `197-04` and this plan's Task 1 are
all committed — the database diffed here is the phase's final generated state.

This artifact is PULSE-03's evidence and OVR-05's restated acceptance evidence (D-13 superseded by
D-16): the regeneration diff against `70c92ce` is exactly 13 rows, zero `support_status` changes, 746
rows in, 746 rows out — each row attributed to a decode rule or to a datasheet-citing override, and
nothing else moved.

## Reproducible method

Baseline: `git show 70c92ce:firestarter/data/chip_database.json`. Live: the regenerated
`firestarter/data/chip_database.json` on disk after `python tools/build_db.py`.

Not `tools/baseline/chip_database.baseline.json` — it is stale, 475857 bytes against the live 432461,
and produces a large spurious diff. Not `tools/diff_db.py` — it does not exist.

The diff script below is a throwaway, run from `firestarter_app`'s repository root and NOT committed
under `tools/`:

```bash
python /path/to/regen_diff.py
```

Full script text:

```python
import json
import subprocess
import sys

BASELINE_REF = "70c92ce"
BASELINE_PATH = "firestarter/data/chip_database.json"
LIVE_PATH = "firestarter/data/chip_database.json"


def load_baseline():
    result = subprocess.run(
        ["git", "show", f"{BASELINE_REF}:{BASELINE_PATH}"],
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(result.stdout)


def load_live():
    with open(LIVE_PATH, encoding="utf-8") as f:
        return json.load(f)


def flatten(db):
    out = {}
    for mfg, rows in db.items():
        for row in rows:
            out[(mfg, row["part_number"])] = row
    return out


def field_paths(obj, prefix=""):
    paths = set()
    if isinstance(obj, dict):
        for k, v in obj.items():
            p = f"{prefix}.{k}" if prefix else k
            if isinstance(v, dict):
                paths |= field_paths(v, p)
            else:
                paths.add(p)
    else:
        paths.add(prefix)
    return paths


def get_path(obj, path):
    cur = obj
    for part in path.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return "<absent>"
        cur = cur[part]
    return cur


def main():
    baseline = flatten(load_baseline())
    live = flatten(load_live())

    base_keys = set(baseline)
    live_keys = set(live)
    if base_keys != live_keys:
        added = sorted(live_keys - base_keys)
        removed = sorted(base_keys - live_keys)
        print("KEY SET MISMATCH")
        print("added:", added)
        print("removed:", removed)
        sys.exit(1)

    print(f"rows_in={len(baseline)} rows_out={len(live)}")

    changed_rows = 0
    support_status_changes = 0
    rows_out_lines = []
    for key in sorted(baseline):
        mfg, part = key
        b_row = baseline[key]
        l_row = live[key]
        paths = field_paths(b_row) | field_paths(l_row)
        row_changed = False
        for path in sorted(paths):
            b_val = get_path(b_row, path)
            l_val = get_path(l_row, path)
            if b_val != l_val:
                row_changed = True
                if path == "support_status":
                    support_status_changes += 1
                rows_out_lines.append((mfg, part, path, b_val, l_val))
        if row_changed:
            changed_rows += 1

    print(f"changed_rows={changed_rows} support_status_changes={support_status_changes}")
    print("---TABLE---")
    for mfg, part, path, b_val, l_val in rows_out_lines:
        print(f"| {mfg} | {part} | {path} | {b_val!r} | {l_val!r} |")


if __name__ == "__main__":
    main()
```

The comparison keys on `(manufacturer, part_number)`, asserts the two key sets are equal BEFORE
comparing any field — an added or removed row would abort with `KEY SET MISMATCH` rather than being
silently absorbed into a field comparison — then, for each key in `sorted()` order, walks the union of
both sides' LEAF dotted field paths (a path present on one side only would report `<absent>` for the
other, via `get_path`) and reports every path whose values differ. Rows emit in sorted key order, so
re-running the script against the same two inputs produces byte-identical output.

## Row-count line

- **Rows in:** 746
- **Rows out:** 746
- **Rows changed:** 13
- **`support_status` values changed:** 0

This reconciles exactly against D-16's prediction (superseding D-13's "10 rows, 9 `support_status`
flips"): **13 rows, zero `support_status` changes** — measured here independently of the research-time
simulation, against the phase's actual final committed state. No discrepancy to record.

## The 14 changed fields, one line per field

| Manufacturer | Part number | Field path | Before | After | Cause |
|---|---|---|---|---|---|
| ATMEL | AT28C04,AT28HC04 | `unsupported_reason` | `adapter required: AT28C04/AT28C16 DIP24 chip — requires a physical DIP24-to-DIP32 adapter; see the wiki page AT28C04 Adapter` | `adapter required: requires a dedicated DIP24 EEPROM adapter or firmware handler — socket pin 21 = WE, which the RURP DIP24_2716 pinout maps to the 12V VPP rail (hardware-damage path)` | Decode rule: the hardware-damage guard at `build_db.py`'s `pin_count == 24 and proto_id in (0x07, 0x08, 0x0B) and (flags & 0x10)` check is now the SOLE writer of `unsupported_reason` on this row, since Plan `197-04` deleted the competing `_AT28C_DIP24_NAMES` name-list arm that used to overwrite the guard's reason string with wiki-page text. `support_status` stays `adapter-required` — only the string changed. |
| ATMEL | AT28C04E,AT28C04F | `unsupported_reason` | `adapter required: AT28C04/AT28C16 DIP24 chip — requires a physical DIP24-to-DIP32 adapter; see the wiki page AT28C04 Adapter` | `adapter required: requires a dedicated DIP24 EEPROM adapter or firmware handler — socket pin 21 = WE, which the RURP DIP24_2716 pinout maps to the 12V VPP rail (hardware-damage path)` | Decode rule: same hardware-damage guard, sole writer since Plan `197-04`'s deletion. |
| ATMEL | AT28C16,AT28HC16,AT28HC16L | `unsupported_reason` | `adapter required: AT28C04/AT28C16 DIP24 chip — requires a physical DIP24-to-DIP32 adapter; see the wiki page AT28C04 Adapter` | `adapter required: requires a dedicated DIP24 EEPROM adapter or firmware handler — socket pin 21 = WE, which the RURP DIP24_2716 pinout maps to the 12V VPP rail (hardware-damage path)` | Decode rule: same hardware-damage guard, sole writer since Plan `197-04`'s deletion. |
| ATMEL | AT28C16E,AT28C16F | `unsupported_reason` | `adapter required: AT28C04/AT28C16 DIP24 chip — requires a physical DIP24-to-DIP32 adapter; see the wiki page AT28C04 Adapter` | `adapter required: requires a dedicated DIP24 EEPROM adapter or firmware handler — socket pin 21 = WE, which the RURP DIP24_2716 pinout maps to the 12V VPP rail (hardware-damage path)` | Decode rule: same hardware-damage guard, sole writer since Plan `197-04`'s deletion. |
| MICROCHIP memory | 28C04A | `unsupported_reason` | `adapter required: AT28C04/AT28C16 DIP24 chip — requires a physical DIP24-to-DIP32 adapter; see the wiki page AT28C04 Adapter` | `adapter required: requires a dedicated DIP24 EEPROM adapter or firmware handler — socket pin 21 = WE, which the RURP DIP24_2716 pinout maps to the 12V VPP rail (hardware-damage path)` | Decode rule: same hardware-damage guard, sole writer since Plan `197-04`'s deletion. |
| MICROCHIP memory | 28C04AF | `unsupported_reason` | `adapter required: AT28C04/AT28C16 DIP24 chip — requires a physical DIP24-to-DIP32 adapter; see the wiki page AT28C04 Adapter` | `adapter required: requires a dedicated DIP24 EEPROM adapter or firmware handler — socket pin 21 = WE, which the RURP DIP24_2716 pinout maps to the 12V VPP rail (hardware-damage path)` | Decode rule: same hardware-damage guard, sole writer since Plan `197-04`'s deletion. |
| MICROCHIP memory | 28C16A | `unsupported_reason` | `adapter required: AT28C04/AT28C16 DIP24 chip — requires a physical DIP24-to-DIP32 adapter; see the wiki page AT28C04 Adapter` | `adapter required: requires a dedicated DIP24 EEPROM adapter or firmware handler — socket pin 21 = WE, which the RURP DIP24_2716 pinout maps to the 12V VPP rail (hardware-damage path)` | Decode rule: same hardware-damage guard, sole writer since Plan `197-04`'s deletion. |
| MICROCHIP memory | 28C16AF | `unsupported_reason` | `adapter required: AT28C04/AT28C16 DIP24 chip — requires a physical DIP24-to-DIP32 adapter; see the wiki page AT28C04 Adapter` | `adapter required: requires a dedicated DIP24 EEPROM adapter or firmware handler — socket pin 21 = WE, which the RURP DIP24_2716 pinout maps to the 12V VPP rail (hardware-damage path)` | Decode rule: same hardware-damage guard, sole writer since Plan `197-04`'s deletion. |
| NEC | UPD28C04 | `unsupported_reason` | `adapter required: AT28C04/AT28C16 DIP24 chip — requires a physical DIP24-to-DIP32 adapter; see the wiki page AT28C04 Adapter` | `adapter required: requires a dedicated DIP24 EEPROM adapter or firmware handler — socket pin 21 = WE, which the RURP DIP24_2716 pinout maps to the 12V VPP rail (hardware-damage path)` | Decode rule: same hardware-damage guard, sole writer since Plan `197-04`'s deletion. |
| RAMTRON | FM1608 | `electrical.type` | `FRAM` | `SRAM` | Decode rule: Plan `197-04`'s deletion of `_ETYPE_RELABEL` lets FM1608 fall through to `classify()`'s natural SRAM/FRAM arm (`type_int == 4 or proto_id in {0x0E, 0x27, 0x28, 0x29}`), which returns `"SRAM"` for every part on this arm — the relabel was the only thing keeping this one row's label at `FRAM`. |
| RAMTRON | FM1608 | `electrical.vcc_mv` | `3300` | `5000` | Decode rule: the SRAM single-rail rewrite at `build_db.py:773-776` (`if _etype == "SRAM": chip_entry["electrical"]["vcc_mv"] = chip_entry["electrical"]["vdd_mv"]`) now fires for this row as a direct consequence of the `electrical.type` flip above — the `FRAM` label had been bypassing this rewrite, so `vcc_mv` stayed at the raw decoded 3300 instead of being replaced by `vdd_mv` (5000), same as its `SRAM`-labelled Ramtron siblings. |
| FUJITSU | MBM27128 | `programming.pulse_duration_us` | `200` | `1000` | Override: entry `FUJITSU/MBM27128` in `tools/datasheet_overrides.json`, `datasheet: datasheets/MBM27128.pdf` (this plan's Task 1). |
| FUJITSU | MBM27C1000P,MBM27C1000 | `programming.pulse_duration_us` | `100` | `500` | Override: entry `FUJITSU/MBM27C1000` in `tools/datasheet_overrides.json`, `datasheet: datasheets/MBM27C1000.pdf` (Plan `197-02`). |
| FUJITSU | MBM27C1001 | `programming.pulse_duration_us` | `100` | `500` | Override: entry `FUJITSU/MBM27C1001` in `tools/datasheet_overrides.json`, `datasheet: datasheets/MBM27C1001.pdf` (this plan's Task 1). |

Every one of the 14 changed fields fits one of the two kinds PULSE-03 requires: a decode rule that
explains it (11 fields: the 9 `unsupported_reason` strings and FM1608's 2 fields), or an override entry
that cites a datasheet for it (3 fields: the 3 pulse-duration values). No row fits neither kind.

## The two zero-diff claims

These are load-bearing and a table of CHANGES cannot show them — they are claims about what did NOT
move:

- **The six NMOS override entries** (`INTEL/M2716`, `INTEL/M2732`, `SGS-THOMSON/M2716`,
  `SGS-THOMSON/M2732A`, `ST/M2716`, `ST/M2732A`, each on `electrical.vpp_mv`) reproduce the six values
  they replaced and contribute zero changed rows. Proved in Plan `197-03` Task 2 (commit
  `firestarter_app@047a5bd`): regenerating with the six entries in place reproduced
  `firestarter/data/chip_database.json` byte-identical to the database Plan `197-02` committed
  (`git diff --quiet` exited 0), and the same six rows are absent from this diff's changed-row table.
- **The `_PGM_ON_PIN31_MAX_SIZE` size-threshold derivation** (`(mem_size - 1).bit_length() <= 18`,
  replacing the deleted `262144` constant at the `DIP32_27C020` vs `DIP32_STD` fork) regenerates
  byte-identically. Proved in Plan `197-01` Task 3 (commit `firestarter_app@5fec5eb`): an exhaustive
  integer-identity check over the practical domain plus a full-pipeline regeneration byte-identical to
  the committed generated artifact.

Both mechanisms are exactly the D-06/D-09 zero-diff claims this phase made before regenerating, and
this diff's 13-row, 0-`support_status` total confirms neither one contributed a row.

## Honesty limit

This diff proves which values moved and why each was expected to, against the specific decode rule or
datasheet-citing override responsible. It does NOT prove any new value is electrically correct. The
three pulse values (`MBM27128`, `MBM27C1000P,MBM27C1000`, `MBM27C1001`) rest on datasheets read
visually by a human researcher, not on an independent electrical measurement. The six NMOS `vpp_mv`
values referenced above (contributing zero diff here, so absent from the table) rest on an inherited
hardcode carried forward as `UNSOURCED` in `tools/datasheet_overrides.json` — an Intel-sourced figure
applied, in four of the six entries, to a different vendor's part with no vendor-specific datasheet
backing it. Both classes of value are stated, not re-derived, by this diff.

---
*Phase: 197-the-override-mechanism-and-the-program-pulse*
*Measured: 2026-09-18*
