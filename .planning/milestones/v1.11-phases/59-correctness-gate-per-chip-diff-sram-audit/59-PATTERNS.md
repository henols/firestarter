# Phase 59: Correctness Gate + Per-chip Diff + SRAM Audit — Pattern Map

**Mapped:** 2026-06-09
**Files analyzed:** 5 new/modified files
**Analogs found:** 5 / 5

---

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `firestarter_app/tools/diff_db.py` | utility/gate-script | transform (CRUD-read, batch compare) | `firestarter_app/tools/check_dispatch.py` | exact (same role, same data flow, same tool directory) |
| `firestarter_app/tools/build_db.py` (one-line edit: `sort_keys=True`) | utility/pipeline | transform (batch, file-I/O) | self — edit of existing file | N/A (in-place edit) |
| `firestarter_app/doc/sram-nvram-behavior.md` | documentation | N/A | `firestarter_app/doc/pinout-safety-review.md` | exact (same doc directory, same two-layer pattern, same phase structure) |
| `.planning/phases/59-.../59-SRAM-AUDIT.md` | planning artifact | N/A | `.planning/phases/58-.../58-SR-1-CHECKLIST.md` | exact (same meta-repo planning layer, same two-layer D-04 pattern) |
| SC#4 determinism harness (shell commands, no committed script) | utility/harness | file-I/O, batch | `build_db.py` invocation pattern + standard `diff` | role-match (manual shell harness, not a committed Python file) |

---

## Pattern Assignments

### `firestarter_app/tools/diff_db.py` (utility, transform/batch-compare)

**Analog:** `firestarter_app/tools/check_dispatch.py`

**Imports pattern** (check_dispatch.py lines 1–22):
```python
import json
import os
import sys

from firestarter.database import EpromDatabase
```
For `diff_db.py`: use only stdlib (`json`, `os`, `sys`). No `EpromDatabase` import needed — the diff works on raw JSON dicts, not on the database class. This matches the RESEARCH.md "no new packages" constraint.

**Path constants pattern** (check_dispatch.py lines 24–29):
```python
# Module-top path constants (mirrors firestarter_app/tools/build_db.py:11-13)
_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "firestarter", "data")
DB_FILE = os.environ.get(
    "FIRESTARTER_DB_FILE",
    os.path.join(_DATA_DIR, "chip_database.json"),
)
```
For `diff_db.py`: add a second env-overridable constant for the baseline path:
```python
_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "firestarter", "data")
_BASELINE_DIR = os.path.join(os.path.dirname(__file__), "baseline")

DB_FILE = os.environ.get(
    "FIRESTARTER_DB_FILE",
    os.path.join(_DATA_DIR, "chip_database.json"),
)
BASELINE_FILE = os.environ.get(
    "FIRESTARTER_BASELINE_FILE",
    os.path.join(_BASELINE_DIR, "chip_database.baseline.json"),
)
```
This matches the invocation pattern documented in RESEARCH.md §Code Examples.

**Core iteration pattern** (check_dispatch.py lines 87–115):
```python
def main():
    with open(DB_FILE, encoding="utf-8") as f:
        db_raw = json.load(f)

    errors = []
    total = 0
    for mfg, chips in db_raw.items():
        if not isinstance(chips, list):
            continue
        for chip in chips:
            total += 1
            # ... per-chip logic ...
```
For `diff_db.py`: load both JSONs with the same `encoding="utf-8"` pattern, build a flat `part_number → chip` index (not keyed on manufacturer name — see Pitfall 4 in RESEARCH.md), then iterate the index.

**Exit-code contract pattern** (check_dispatch.py lines 159–214):
```python
if (
    errors
    or sram_in_eprom
    or eeprom28c_in_eprom
    or vpp_eeprom_in_eprom
    or wire_regressions
):
    if errors:
        print(f"FAIL: {len(errors)} of {total} chips have no valid dispatch path:")
        for e in errors[:20]:
            print(f"  {e}")
        if len(errors) > 20:
            print(f"  ... and {len(errors) - 20} more")
    # ... other fail blocks ...
    sys.exit(1)

print(
    f"PASS: all {total} chips have a valid dispatch path; ..."
)
# (implicit sys.exit(0))
```
For `diff_db.py`: mirror this exactly. One `unexplained_diffs` list acts as the gate:
```python
if unexplained_diffs:
    print(f"FAIL: {len(unexplained_diffs)} chips with unexplained diffs:")
    for pn in unexplained_diffs[:20]:
        print(f"  {pn}")
    if len(unexplained_diffs) > 20:
        print(f"  ... and {len(unexplained_diffs) - 20} more")
    sys.exit(1)

print(
    f"PASS: all {changed_count} changed chips explained "
    f"({len(new_chips)} new chips confirmed; "
    f"{missing_count} chips removed from baseline)"
)
# implicit sys.exit(0)
```

**`__main__` guard** (check_dispatch.py line 216–217):
```python
if __name__ == "__main__":
    main()
```
Copy verbatim into `diff_db.py`.

**Key diff-specific pattern** (RESEARCH.md §Pattern 1 — not in check_dispatch.py, derived from it):

The `_classify_diff` function must handle the 5 root-cause categories. The combined BUG-2+BUG-3 case (188 chips) must be classified as `BUG2_AND_BUG3` before reaching the `None` (unexplained) fallthrough — see RESEARCH.md §Pitfall 2. Classification logic per RESEARCH.md:

```python
def _classify_diff(bl_chip, cu_chip):
    """Return root-cause label or None if diff cannot be explained."""
    bl_prog = bl_chip.get("programming", {})
    cu_prog = cu_chip.get("programming", {})
    bl_elec = bl_chip.get("electrical", {})
    cu_elec = cu_chip.get("electrical", {})

    timing_diff = bl_prog.get("pulse_duration") != cu_prog.get("pulse_duration")
    algo_diff   = bl_prog.get("algorithm") != cu_prog.get("algorithm")
    vcc_diff    = bl_elec.get("vcc") != cu_elec.get("vcc")
    vdd_diff    = bl_elec.get("vdd") != cu_elec.get("vdd")
    pinout_diff = bl_chip.get("pinout") != cu_chip.get("pinout")

    voltage_diff = vcc_diff or vdd_diff

    if algo_diff:
        return "RULE_ALGO"
    if timing_diff and voltage_diff:
        return "BUG2_AND_BUG3"
    if timing_diff and not voltage_diff and not pinout_diff:
        return "BUG2_TIMING"
    if voltage_diff and not timing_diff and not algo_diff:
        return "BUG3_VCC_VDD"
    if pinout_diff and not algo_diff and not timing_diff:
        return "SRAM_PINOUT"
    return None   # unexplained — D-03 BLOCK
```

---

### `firestarter_app/tools/build_db.py` (one-line edit: `sort_keys=True`)

**Analog:** self (in-place edit of existing file)

**Target line** (build_db.py line 517):
```python
# BEFORE:
json.dump(complete_db, f, indent=2)

# AFTER:
json.dump(complete_db, f, indent=2, sort_keys=True)
```

This is the only change to `build_db.py`. It makes the output key-order stable regardless of Python dict insertion order (Python 3.7+ is deterministic in practice, but `sort_keys` is an explicit guarantee). Per RESEARCH.md §SC#4 Pitfall 3, this edit must be made BEFORE the SC#4 two-run byte-compare, not between Run 1 and Run 2.

The edit must be ruff-clean (no import or formatting changes required for a single-argument addition).

---

### `firestarter_app/doc/sram-nvram-behavior.md` (documentation, N/A)

**Analog:** `firestarter_app/doc/pinout-safety-review.md`

**Header / front-matter pattern** (pinout-safety-review.md lines 1–8):
```markdown
# Pinout Safety Review — Phase 58

This document summarises the safety guarantees established by the Phase 58 principled
pinout re-derivation (`resolve_pinout_key` rewrite) and the new `DIP24_2816` pinout entry.

**Full audit trail:** `.planning/phases/58-pinout-re-derivation-24-pin-eeprom-unblock/58-SR-1-CHECKLIST.md`
(meta-repo, investigation-canonical).
```
For `sram-nvram-behavior.md`: use the same pattern — one-sentence scope, explicit pointer to the planning-layer audit trail:
```markdown
# SRAM / NVRAM Behavior — Phase 59

**Full audit trail:** `.planning/phases/59-correctness-gate-per-chip-diff-sram-audit/59-SRAM-AUDIT.md`
(meta-repo, investigation-canonical).
```

**Section structure pattern** (pinout-safety-review.md — two guaranteed-behavior sections, each with a header, prose, and a code fence for evidence):
```markdown
## Safety Guarantee: <title>

<prose: what the guarantee is, what it applies to>

Key facts:
- Fact 1
- Fact 2

Compare: <counterexample or contrast>
```
For `sram-nvram-behavior.md`: three required sections per D-04 — (a) blank-check limitation, (b) WP# behavior, (c) RTC-oscillator side effect. Each follows the same header → prose → bullet-facts structure.

**Citation format** (infoic-field-dictionary.md lines 9–11):
```markdown
**Citation commit:** `a8efaedc236c1d9718bd28299dfbb99536b010ff` (2026-03-23, ...)
**Permalink base:** `https://gitlab.com/DavidGriffith/minipro/-/blob/a8efaedc.../src/`
```
For `sram-nvram-behavior.md`: cite PITFALLS.md §E-3 (planning-canonical source) + datasheet family names (DS1225, M48T08). Use `[CITED: .planning/research/PITFALLS.md §E-3]` inline citation style consistent with the existing project convention.

---

### `.planning/phases/59-.../59-SRAM-AUDIT.md` (planning artifact, N/A)

**Analog:** `.planning/phases/58-pinout-re-derivation-24-pin-eeprom-unblock/58-SR-1-CHECKLIST.md`

This is the planning-layer (meta-repo) half of the D-04 two-layer doc. It is the investigation-canonical record; the shipped `sram-nvram-behavior.md` is the operator-facing subset.

**Structure pattern** (from shield-revision two-layer precedent and SR-1 pattern documented in RESEARCH.md §Pattern 2):
```markdown
# 59-SRAM-AUDIT.md — GATE-04 SRAM/NVRAM Behavioral Audit

**Date:** 2026-06-09
**Phase:** 59

## Scope
What was audited: firmware `configure_sram`, host-side SRAM dispatch (`check_dispatch.py` BLOCKER-2), NVRAM behavioral truths.

## Firmware Layer Audit
[Inline sram.cpp source + verdict]

## Host-Side Dispatch Audit
[check_dispatch.py BLOCKER-2 guard + SRAM protocols enumerated]

## NVRAM Behavioral Truths
### (a) Blank-Check Limitation
### (b) WP# Pin Behavior (DS1225 / M48T08 class)
### (c) RTC Oscillator Side Effect

## Safety Verdict
No genuine safety issue found. No firmware escalation needed.

## Shipped Doc
`firestarter_app/doc/sram-nvram-behavior.md` (operator-facing subset, committed in lockstep)
```

---

### SC#4 Determinism Harness (shell commands, not a committed script)

**Analog:** `build_db.py` invocation pattern + standard `diff`

Per RESEARCH.md and CONTEXT.md deferred notes, SC#4 is demonstrated as a manual shell procedure (not wired into CI). The harness is three shell commands run after the `sort_keys=True` edit and DB regeneration:

```bash
cd /workspaces/firestarter_app

# Run 1
python3 tools/build_db.py
cp firestarter/data/chip_database.json /tmp/chip_database_run1.json

# Run 2 — immediate re-run, same upstream XML
python3 tools/build_db.py
cp firestarter/data/chip_database.json /tmp/chip_database_run2.json

# Compare
diff /tmp/chip_database_run1.json /tmp/chip_database_run2.json && echo "SC#4 PASS: byte-identical"
```

No committed harness file is needed. The procedure is documented in the plan and its output (empty diff) is recorded in the plan summary.

---

## Shared Patterns

### Module docstring + exit-code contract
**Source:** `firestarter_app/tools/check_dispatch.py` lines 1–16
**Apply to:** `diff_db.py`
```python
"""
<One-paragraph description of what the script does and what the exit codes mean.>

Exit codes:
  0 — all <N> changed chips explained; no unexplained diffs; <M> new chips confirmed.
  1 — at least one chip has an unexplained diff (D-03 BLOCK: investigate build_db.py).
"""
```
The docstring must state the exit-code contract explicitly. This is the established pattern across all `tools/` gate scripts.

### `encoding="utf-8"` for JSON file opens
**Source:** `firestarter_app/tools/check_dispatch.py` line 89
**Apply to:** `diff_db.py` (both JSON opens)
```python
with open(DB_FILE, encoding="utf-8") as f:
    db_raw = json.load(f)
```
Always pass `encoding="utf-8"` — this is the project convention for reading JSON files.

### Path constants at module top, env-overridable
**Source:** `firestarter_app/tools/check_dispatch.py` lines 24–29; `firestarter_app/tools/build_db.py` lines 12–14
**Apply to:** `diff_db.py`

All path constants are module-level, computed relative to `__file__`, and overridable via environment variable. This makes the scripts testable with alternate files without modifying source.

### Ruff compliance (CI gate)
**Source:** `firestarter_app/CLAUDE.md` §Tooling gate
**Apply to:** `diff_db.py`, `build_db.py` (one-line edit)

The CI gate enforces `ruff check` + `ruff format --check` on all Python files. `diff_db.py` must be ruff-clean on creation. The `sort_keys=True` addition to `build_db.py` requires no import changes and is already ruff-clean (a keyword argument addition).

### Two-layer doc lockstep commit discipline
**Source:** `firestarter_app/CLAUDE.md` §Constants (last paragraph); MEMORY.md `project_v17_shield_docs_layering.md`
**Apply to:** `59-SRAM-AUDIT.md` + `sram-nvram-behavior.md` pair

Both layers must be committed in the same commit (or a closely-coupled commit sequence within the same plan wave). The planning-layer artifact (meta-repo `.planning/`) and the shipped sub-repo doc (`firestarter_app/doc/`) are committed in lockstep. The shipped doc's front matter must explicitly reference the planning-layer audit trail file path.

---

## No Analog Found

All 5 files have close analogs. No files require fallback to RESEARCH.md patterns only.

---

## Metadata

**Analog search scope:** `firestarter_app/tools/`, `firestarter_app/doc/`, `.planning/phases/58-*/`
**Files scanned:** 5 (check_dispatch.py, build_db.py, pinout-safety-review.md, infoic-field-dictionary.md, 58-SR-1-CHECKLIST structure via RESEARCH.md)
**Pattern extraction date:** 2026-06-09
