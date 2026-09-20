# Phase 199 Plan 01 — The 746-Row Regeneration Diff

**Measured:** 2026-09-19, against `firestarter_app` HEAD `7e02494` (this plan's Task 2 commit) on
`v1.40-program-parameter-fidelity`, after this plan's Task 1 and Task 2 are both committed — the
database diffed here is this plan's final generated state.

This artifact is RAIL-02's database-half evidence (D-17): the regeneration diff against `f155364`
(the commit immediately before this plan's first edit) is exactly one row, one field, zero
`support_status` changes, 746 rows in, 746 rows out — the single row is attributed to a
datasheet-citing override, and nothing else moved.

## Reproducible method

Baseline: `git show f155364:firestarter/data/chip_database.json`. Live: the regenerated
`firestarter/data/chip_database.json` on disk after `python tools/build_db.py`.

Not `tools/baseline/chip_database.baseline.json` — the 197 and 198 records both measured it as
stale and materially larger than the live file, and nothing in this plan changed that. Not a
committed diff tool — none exists; `tools/` sits outside every CI gate (no mypy, no `ruff check`,
no `ruff format`), so a script placed there would be unguarded and still would not fail when the
answer changes. The comparison script below is a throwaway, run from `firestarter_app`'s repository
root and deliberately NOT committed under `tools/`, on the `197-REGEN-DIFF.md` / `198-REGEN-DIFF.md`
precedent:

```bash
python /path/to/regen_diff_199.py
```

Full script text:

```python
import json
import subprocess
import sys

BASELINE_REF = "f155364"
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
- **Rows changed:** 1
- **`support_status` values changed:** 0

This reconciles exactly against D-17's prediction ("exactly one row's value moves") and against this
plan's own Task 1 verify leg, run independently during execution against the same `HEAD` baseline
(`REGEN_199_OK`): one changed tuple, `(('FUJITSU','MBM27128'), 'electrical', 'vpp_mv', 18000, 21000)`.
No discrepancy to record.

## The one changed field

| Manufacturer | Part number | Field path | Before | After | Cause |
|---|---|---|---|---|---|
| FUJITSU | MBM27128 | `electrical.vpp_mv` | `18000` | `21000` | Override: entry `FUJITSU/MBM27128` in `tools/datasheet_overrides.json`, `datasheet: datasheets/MBM27128.pdf` (plan `199-01` Task 1, D-17). |

The single changed field fits the one kind D-17 permits: an override entry that cites a vendored
datasheet for it. No row fits neither kind, and no second row was touched.

## The two positive no-drift claims

These are load-bearing and a table of CHANGES cannot show them — they are claims about what did NOT
move, and the table above has no other row to show them with:

- **No other row moved.** The regeneration diff's own key-set-equality check (run before any field
  comparison) found `set(fa) == set(fb)` — the same 746 `(manufacturer, part_number)` keys on both
  sides — and the field-level walk over the union of every row's leaf paths found exactly one
  differing tuple. Proved in this plan's Task 1 verify leg (`REGEN_199_OK`), run against `HEAD`
  before the commit that introduced the change.
- **No row's `support_status` moved.** `sorted(r.get('support_status') for r in fb.values()) ==
  sorted(r.get('support_status') for r in fa.values())` in that same verify leg — the two
  `support_status` multisets are identical before and after, so D-01 holds: 21000 sits strictly below
  `RURP_VPP_CEILING_MV` at 25000, and the ceiling comparison is `>`, so `MBM27128` stays `supported`.

Both claims were re-measured independently by the throwaway script above (`support_status_changes=0`
and `changed_rows=1`, with no `KEY SET MISMATCH`), confirming the Task 1 in-flight verify leg's
result against the phase's final committed state rather than resting on it alone.

## Honesty limit

This diff proves that exactly one value moved and that nothing else did. It does NOT prove that
21000 is electrically correct — the figure was read from a vendored datasheet page (Figure 3, the
Quick Pro flow chart on page 4-20 of `datasheets/MBM27128.pdf`, which states VPP = 21V +/- 0.5V), not
measured on a bench. It also does NOT prove that any shield revision can deliver 21 V to socket pin
1 — that question belongs to this phase's bench-measurement plan (`199-02`), not to this diff. A
datasheet-cited correction and a delivered rail are two different claims, and this artifact makes
only the first one.

---
*Phase: 199-what-the-rails-can-actually-deliver*
*Plan: 01*
*Measured: 2026-09-19*
