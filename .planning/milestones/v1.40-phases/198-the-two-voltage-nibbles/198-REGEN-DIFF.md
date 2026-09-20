# Phase 198 — The 746-Row Regeneration Diff

**Measured:** 2026-09-18, against `firestarter_app` HEAD `80735b2` (this plan's Task 2 commit) on
`v1.40-program-parameter-fidelity`, after plans `198-01` and `198-02` are both committed — the
database diffed here is the phase's final generated state. This artifact is VOLT-01's and VOLT-03's
evidence: the full-phase regeneration diff against `0372cc6` (the commit immediately before this
phase's first edit) is exactly 15 rows, 17 field values, zero `support_status` changes, 746 rows in,
746 rows out — each field attributed to a decode rule or a datasheet-citing override, and nothing
else moved.

## Reproducible method

Baseline: `git show 0372cc6:firestarter/data/chip_database.json`. Live: the regenerated
`firestarter/data/chip_database.json` on disk after `python tools/build_db.py`.

Not `tools/baseline/chip_database.baseline.json` — RESEARCH measured it as stale and materially
larger than the live file. Not a committed diff tool — none exists. The comparison script below is
a throwaway, run from `firestarter_app`'s repository root and NOT committed under `tools/`, on the
`197-REGEN-DIFF.md` precedent:

```bash
python /path/to/regen_diff_198.py
```

Full script text:

```python
import json
import subprocess
import sys

BASELINE_REF = "0372cc6"
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
silently absorbed into a field comparison — then, for each key in `sorted()` order, walks the union
of both sides' LEAF dotted field paths (a path present on one side only would report `<absent>` for
the other, via `get_path`) and reports every path whose values differ. Rows emit in sorted key
order, so re-running the script against the same two inputs produces byte-identical output.

## Row-count line

- **Rows in:** 746
- **Rows out:** 746
- **Rows changed:** 15
- **`support_status` values changed:** 0

This reconciles exactly against the phase's pre-execution prediction (RESEARCH F-5 Run B: "exactly
15 rows change, 17 field values") and against `198-01-SUMMARY.md`'s measured Task 1 diff (3 rows, 5
field values) plus this plan's Task 1 measured diff (12 rows, 12 field values, all
`electrical.vdd_mv`): 3 + 12 = 15 rows, 5 + 12 = 17 field values. No divergence to flag.

## The 17 changed fields, one line per field

| Manufacturer | Part number | Field path | Before | After | Cause |
|---|---|---|---|---|---|
| FUJITSU | MBM27C1001 | `electrical.vpp_mv` | `12000` | `12500` | Override: entry `FUJITSU/MBM27C1001` in `tools/datasheet_overrides.json`, `datasheet: datasheets/MBM27C1001.pdf` (plan `198-01` Task 1, D-07/D-08). |
| FUJITSU | MBM27C1001 | `electrical.vdd_mv` | `5500` | `6000` | Override: entry `FUJITSU/MBM27C1001` in `tools/datasheet_overrides.json`, `datasheet: datasheets/MBM27C1001.pdf` (plan `198-01` Task 1, D-09). |
| FUJITSU | MBM27C4001 | `electrical.vpp_mv` | `12000` | `12500` | Override: entry `FUJITSU/MBM27C4001` in `tools/datasheet_overrides.json`, `datasheet: datasheets/MBM27C4001.pdf` (plan `198-01` Task 1, D-07/D-08). |
| FUJITSU | MBM27C4001 | `electrical.vdd_mv` | `5500` | `6000` | Override: entry `FUJITSU/MBM27C4001` in `tools/datasheet_overrides.json`, `datasheet: datasheets/MBM27C4001.pdf` (plan `198-01` Task 1, D-09). |
| FUJITSU | MBM27128 | `electrical.vdd_mv` | `5500` | `6000` | Override: entry `FUJITSU/MBM27128` in `tools/datasheet_overrides.json`, `datasheet: datasheets/MBM27128.pdf` (plan `198-01` Task 1, D-09). |
| FUJITSU | MBM27C1000P,MBM27C1000 | `electrical.vdd_mv` | `5000` | `6000` | Decode rule: `VCC_VOLTAGES` vdd index `0x0D` completed to 6000 (plan `198-02` Task 1, D-01). |
| FUJITSU | MBM27C2000P,MBM27C2000 | `electrical.vdd_mv` | `5000` | `6000` | Decode rule: `VCC_VOLTAGES` vdd index `0x0D` completed to 6000 (plan `198-02` Task 1, D-01). |
| HITACHI | HN27C301AG,HN27C301AP,HN27C301AFP | `electrical.vdd_mv` | `5000` | `6000` | Decode rule: `VCC_VOLTAGES` vdd index `0x0D` completed to 6000 (plan `198-02` Task 1, D-01). |
| HITACHI | HN27C301G | `electrical.vdd_mv` | `5000` | `6000` | Decode rule: `VCC_VOLTAGES` vdd index `0x0D` completed to 6000 (plan `198-02` Task 1, D-01). |
| MITSUBISHI | M5M27C101K | `electrical.vdd_mv` | `5000` | `6000` | Decode rule: `VCC_VOLTAGES` vdd index `0x0D` completed to 6000 (plan `198-02` Task 1, D-01). |
| FAIRCHILD | NMC27C16B,NMC27C16BQ | `electrical.vdd_mv` | `5000` | `6250` | Decode rule: `VCC_VOLTAGES` vdd index `0x0E` completed to 6250 (plan `198-02` Task 1, D-01). |
| NSC | NMC27C16 | `electrical.vdd_mv` | `5000` | `6250` | Decode rule: `VCC_VOLTAGES` vdd index `0x0E` completed to 6250 (plan `198-02` Task 1, D-01). |
| NSC | NMC27C16B | `electrical.vdd_mv` | `5000` | `6250` | Decode rule: `VCC_VOLTAGES` vdd index `0x0E` completed to 6250 (plan `198-02` Task 1, D-01). |
| NSC | NMC27C16Q | `electrical.vdd_mv` | `5000` | `6250` | Decode rule: `VCC_VOLTAGES` vdd index `0x0E` completed to 6250 (plan `198-02` Task 1, D-01). |
| OKI | MSM27C1000 | `electrical.vdd_mv` | `5000` | `6250` | Decode rule: `VCC_VOLTAGES` vdd index `0x0E` completed to 6250 (plan `198-02` Task 1, D-01). |
| OKI | MSM27C2000 | `electrical.vdd_mv` | `5000` | `6250` | Decode rule: `VCC_VOLTAGES` vdd index `0x0E` completed to 6250 (plan `198-02` Task 1, D-01). |
| SGS-THOMSON | M27C1000 | `electrical.vdd_mv` | `5000` | `6250` | Decode rule: `VCC_VOLTAGES` vdd index `0x0E` completed to 6250 (plan `198-02` Task 1, D-01). |

Every one of the 17 changed fields fits one of the two kinds this phase permits: a decode rule
naming the vdd index and its newly-mapped value (12 fields, all `electrical.vdd_mv` at indices
`0x0D` and `0x0E`), or an override entry naming the entry key and its vendored datasheet path
(5 fields: the 2 VPP corrections and the 3 vdd corrections on the three Fujitsu rows an index alone
cannot reach). No row fits neither kind.

## The two zero-diff claims

These are load-bearing and a table of CHANGES cannot show them — they are claims about what did NOT
move:

- **The twelve held `0x06` entries.** `VCC_VOLTAGES` now decodes vdd index `0x06` to 1800 mV for the
  seven EXEL, three ST and two SGS-THOMSON 28C-class rows carrying `voltages=0x64xx`, yet all twelve
  still emit `electrical.vdd_mv: 5000` in the table above — they are absent from it entirely. Twelve
  explicit `UNSOURCED` entries in `tools/datasheet_overrides.json` hold each row at the value it
  emitted before the table was completed. Proved in plan `198-02` Task 1 (commit
  `firestarter_app@0849135`): the task's own diff leg, run against the state immediately before that
  commit, asserted the changed-row set was exactly 12 (the `0x0D`/`0x0E` movers) and exactly 12
  (EXEL/ST/SGS-THOMSON) rows still read `(vdd_mv: 5000, vcc_mv: 5500)` afterward — none of the twelve
  reached 1800.
- **The two new `VPP_MV` indices (`0xF1`=25000, `0xF2`=21000).** No filtered row carries either index
  today, so completing the table to include them contributes zero rows to this diff. Proved in plan
  `198-01` Task 3 (commit `firestarter_app@254c4f7`): regenerating with the completed `VPP_MV` table
  in place reproduced `firestarter/data/chip_database.json` byte-identical to the database committed
  immediately before that task (`git diff --quiet` exited 0), and no row carrying `0xF1` or `0xF2`
  appears in the changed-fields table above.

Both mechanisms are exactly the D-04/D-16 zero-diff claims this phase made before regenerating, and
this diff's 15-row, 17-field, 0-`support_status` total confirms neither one contributed a row.

## Recorded here because this is their only home

**D-10 — the firmware guard-band consequence.** Raising `FUJITSU/MBM27C1001` and
`FUJITSU/MBM27C4001`'s `vpp_mv` to 12500 moves the firmware's settable band from
`vpp_mv × 95/100`–`vpp_mv + 500` = 11400–12500 (at the old 12000 target) to 11875–13000 (at the new
12500 target). This makes the datasheet's 12.2–12.8 V window fully settable, where the previous
12000 target did not reach it — `dim20`'s retest at 12.4 V failed for a different, already-posted
reason (the last-256-byte hypothesis), but the database itself could not have targeted 12.4 V
precisely before this correction. 13000 still sits below the datasheet's 13.5 V absolute-maximum
warning. No host-side test encodes this consequence, because doing so would duplicate a firmware
constant across repositories, and the public gh#66 answer does not mention it — that answer stays
strictly to the database values that changed.

**D-08 — a known, unsourced family inconsistency.** `FUJITSU/MBM27C2001` carries the identical
voltage word (`voltages=0x4000`) as `FUJITSU/MBM27C1001` and `FUJITSU/MBM27C4001`, but has no
vendored datasheet in this repository. It stays at `vpp_mv: 12000` while both siblings move to
12500 — a deliberate, held decision, not an oversight: citing a sibling's datasheet reading for an
unvendored row is exactly what this phase's own discipline forbids. `MBM27C2001` is visible in the
shipped characterization snapshot two lines below `MBM27C1001`, the corrected row directly above it.

## Honesty limit

This diff proves which values moved and why each was expected to, against the specific decode rule
or datasheet-citing override responsible. It does NOT prove any new value is electrically correct.
The five override-sourced field values (`MBM27128`'s vdd, `MBM27C1001`'s vpp and vdd, `MBM27C4001`'s
vpp and vdd) rest on datasheets read visually by a human researcher, not on an independent
electrical measurement. The twelve decode-rule-sourced `0x0D`/`0x0E` field values rest on upstream's
`xg_vcc_voltages[]` table, transcribed from the pinned `database.c` source and not independently
bench-verified against any of the twelve parts. The twelve held `0x06` entries rest on the judgment
that 1.8 V is not credible for a 5 V 28C-class part — a negative claim about what is not correct,
not a positive claim about what the true rail is; no datasheet in this repository backs the 5000 mV
each holds either.

---
*Phase: 198-the-two-voltage-nibbles*
*Measured: 2026-09-18*
