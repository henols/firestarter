# VOLT-03 — The 28-Row `vcc_mv == 5500` Disposition

**Measured:** 2026-09-18, against `firestarter_app` HEAD `f155364` on
`v1.40-program-parameter-fidelity`, after plan `198-03` Task 1 landed `DECODE-NOTES.md` § 9's
general finding. This record is VOLT-03's evidence: every one of the 28 rows the `vdd < vcc`
predicate (D-06) selects, disposed with a reason, closing the todo that has blocked this group
since v1.32.

## Reproducible method

Filter: the generator's own DIP-parallel predicate `[VERIFIED: firestarter_app/tools/build_db.py,
the "--- FILTER: DIP PARALLEL ONLY ---" block]` — `24 <= pin_count <= 32`, not SMD, not serial,
`type in {1, 4}` — applied to the pinned `infoic.xml` at minipro commit
`a8efaedc236c1d9718bd28299dfbb99536b010ff` (sha256
`cdd21319ae6cce2316ca2361a9fb82cba89b27b66bb78d58b01032a441106b8a`, the same file `198-RESEARCH.md`
F-3 hashed). Comparison: decode `vcc_mv = VCC_VOLTAGES.get((voltages >> 8) & 0x0F, 5000)` and
`vdd_mv = VCC_VOLTAGES.get((voltages >> 12) & 0x0F, 5000)` against the **completed** table this
phase shipped, then select `vdd_mv < vcc_mv`. This is D-06's key: value-keyed and part-name-free.

```python
import sys
import xml.etree.ElementTree as ET

sys.path.insert(0, "/workspaces/firestarter_app")
from tools.build_db import VCC_VOLTAGES  # module import only — no network fetch at import time

XML_PATH = "<local copy of the pinned infoic.xml>"

rows = []
tree = ET.parse(XML_PATH)
for db in tree.getroot().findall(".//database[@type='INFOIC2PLUS']"):
    for mfg in db.findall(".//manufacturer"):
        mfg_name = mfg.get("name")
        for ic in mfg.findall(".//ic"):
            name = ic.get("name")
            try:
                pkg_val = int(ic.get("package_details"), 16)
                pin_count = (pkg_val & 0x7F000000) >> 24
                is_smd = pkg_val & 0x80000000
                is_serial = (pkg_val & 0x0000FF00) >> 8
                type_int = int(ic.get("type"), 16)
            except Exception:
                continue
            if not (24 <= pin_count <= 32):
                continue
            if is_smd or is_serial:
                continue
            if type_int not in (1, 4):
                continue
            voltages = int(ic.get("voltages"), 16)
            proto_id = int(ic.get("protocol_id"), 16)
            vcc_mv = VCC_VOLTAGES.get((voltages >> 8) & 0x0F, 5000)
            vdd_mv = VCC_VOLTAGES.get((voltages >> 12) & 0x0F, 5000)
            rows.append((mfg_name, name, voltages, proto_id, vcc_mv, vdd_mv))

below = [r for r in rows if r[5] < r[4]]
equal = [r for r in rows if r[5] == r[4]]
above = [r for r in rows if r[5] > r[4]]
print(len(rows), len(below), len(equal), len(above))
```

Run against the pinned XML this session: `767 28 373 366` — **28 + 373 + 366 = 767**, an exact
partition of the full filtered population, with zero rows falling into neither bucket. The 28
split, by decoded `vdd_mv`, into **16 at `(vcc 5500, vdd 3300)`** and **12 at `(vcc 5500, vdd
1800)`** — the completed table's own decode of index `0x06`, before the twelve `UNSOURCED`
override entries hold them back at the emitted `5000`. Phase 148 measured and rejected the
**inverse** relation (`vcc < vdd`, 225 rows, sweeping 167 UV-EPROMs it had no business moving);
this predicate is its complement and does not inherit that defect, because a program rail
genuinely below the read rail is internally contradictory in a way the inverse is not.

## The 28-row census

**Sub-group 1 — 16 rows, decoded `(vcc_mv 5500, vdd_mv 3300)`, all algorithm `13` (promoted from
upstream `0x07`/`0x0B`).** The manufacturer string is literally `MICROCHIP memory` — a space, then
lowercase `memory` — exactly as it appears upstream; any override key or test literal must match it
verbatim.

| # | Manufacturer | infoic `name` | `voltages` | upstream `protocol_id` | Emitted `part_number` | `support_status` |
|---|---|---|---|---|---|---|
| 1 | AMD | `AM28C16A@DIP24` | `0x1400` | `0x0b` | `AM28C16A` | supported |
| 2 | AMD | `AM28C17A@DIP28,AM28C17A@SOIC28` | `0x1400` | `0x07` | `AM28C17A` | supported |
| 3 | MICROCHIP memory | `2804` | `0x1400` | `0x0b` | `2804` | supported |
| 4 | MICROCHIP memory | `2816` | `0x1400` | `0x0b` | `2816` | supported |
| 5 | MICROCHIP memory | `2817` | `0x1400` | `0x07` | `2817` | supported |
| 6 | MICROCHIP memory | `28C04A,28C04A@SOIC24` | `0x1400` | `0x0b` | `28C04A` | **adapter-required** |
| 7 | MICROCHIP memory | `28C04AF,28C04AF@SOIC24` | `0x1400` | `0x0b` | `28C04AF` | **adapter-required** |
| 8 | MICROCHIP memory | `28C16A,28C16A@SOIC24` | `0x1400` | `0x0b` | `28C16A` | **adapter-required** |
| 9 | MICROCHIP memory | `28C16AF,28C16AF@SOIC24` | `0x1400` | `0x0b` | `28C16AF` | **adapter-required** |
| 10 | MICROCHIP memory | `28C17A,28C17A@SOIC28` | `0x1400` | `0x07` | `28C17A` | supported |
| 11 | MICROCHIP memory | `28C17AF,28C17AF@SOIC28` | `0x1400` | `0x07` | `28C17AF` | supported |
| 12 | MICROCHIP memory | `28C256,28C256F` | `0x1400` | `0x07` | `28C256,28C256F` | supported |
| 13 | MICROCHIP memory | `28C64A,28C64A@SOIC28` | `0x1400` | `0x07` | `28C64A` | supported |
| 14 | MICROCHIP memory | `28C64AF,28C64AF@SOIC28` | `0x1400` | `0x07` | `28C64AF` | supported |
| 15 | MICROCHIP memory | `28C64B,28C64B@SOIC28` | `0x1400` | `0x07` | `28C64B` | supported |
| 16 | MICROCHIP memory | `28LV64A,28LV64A@SOIC28` | **`0x1401`** | `0x07` | `28LV64A` | supported |

Fifteen of the sixteen carry `voltages = 0x1400`; only `28LV64A` carries `0x1401` — the low bit
set, the same bit that distinguishes the `0x70`/`0x71` VPP-index pairing in the census § 9 reads as
an option flag. That is a measured signal, and it cuts for the low-voltage reading of that one row.
Two of the sixteen are AMD, not Microchip — the todo's own text says *"plus AMD's second-sourced
equivalents"*, so classifying this group as purely Microchip understates what the todo itself
says; the disposition below counts all sixteen together as one class, Microchip and AMD alike.
Four rows (`28C04A`, `28C04AF`, `28C16A`, `28C16AF`) are `adapter-required` under the AT28C
hardware-damage guard `.planning/notes/197-at28c-guard-evidence-for-phase-199.md` inherits; the
other twelve are `supported`.

**Sub-group 2 — 12 rows, decoded `(vcc_mv 5500, vdd_mv 1800)` under the completed table, held at
emitted `vdd_mv 5000` by the twelve `UNSOURCED` override entries `198-02` shipped.**

| # | Manufacturer | infoic `name` | `voltages` | Emitted `part_number` |
|---|---|---|---|---|
| 17 | EXEL | `XL2804A` | `0x6400` | `XL2804A` |
| 18 | EXEL | `XL2816A,XLE28C16A,XLS28C16A` | `0x6400` | `XL2816A,XLE28C16A,XLS28C16A` |
| 19 | EXEL | `XLE2865A,XLS2865A` | `0x6400` | `XLE2865A,XLS2865A` |
| 20 | EXEL | `XLE28C16B,XLE28C16B@SIOC24,XLS28C16B,XLS28C16B@SIOC24` | `0x6400` | `XLE28C16B,XLS28C16B` |
| 21 | EXEL | `XLE28C256,XLS28C256` | `0x6400` | `XLE28C256,XLS28C256` |
| 22 | EXEL | `XLE28C64A,XLS28C64A` | `0x6400` | `XLE28C64A,XLS28C64A` |
| 23 | EXEL | `XLE28C64B,XLE28C64B@SOIC28,XLS28C64B,XLS28C64B@SOIC28` | `0x6400` | `XLE28C64B,XLS28C64B` |
| 24 | SGS-THOMSON | `M28C64,M28C64@SOIC28,M28C64A,M28C64A@SOIC28` | `0x6400` | `M28C64,M28C64A` |
| 25 | SGS-THOMSON | `M28C64-xxW,M28C64-xxW@SOIC28` | **`0x6401`** | `M28C64-xxW` |
| 26 | ST | `M28C64,M28C64@SOIC28,M28C64A,M28C64A@SOIC28` | `0x6400` | `M28C64,M28C64A` |
| 27 | ST | `M28C64-xxW,M28C64-xxW@SOIC28` | **`0x6401`** | `M28C64-xxW` |
| 28 | ST | `M28LV64,M28LV64@SOIC28` | **`0x6401`** | `M28LV64` |

EXEL ×7, ST ×3, SGS-THOMSON ×2 — exactly D-04's split. All 28 carry `programming.algorithm: 13` —
they are promoted rows, so their `programming.*` fields belong to another algorithm entirely, a
fact `198-CONTEXT.md` § Established Patterns already records.

## Per-row disposition

**All 28 rows ship unchanged (D-11).** VOLT-03 explicitly permits this outcome — *"Leaving them
unproven and unchanged is an acceptable outcome; changing them on an unproven assumption is
not."* No plausibility floor, no clamp to `vdd_mv`, no `support_status` change. The
fail-the-build, mark-unproven and clamp-to-vcc alternatives were each offered and declined during
context-gathering.

**Sub-group 1's 15 non-`28LV64A` rows — against `vdd` substitution.** These are the canonical 5 V
28C-family parallel EEPROMs by part-number convention (`2804`/`2816`/`2817` and their `28Cxx`/`AF`/
`A` successors, plus AMD's `AM28C16A`/`AM28C17A` second sources). A `vdd`-keyed rewrite would set
every one of them to 3.3 V. **This is an inference from part-number class, not a datasheet
reading** — see the honesty limit below.

**`28LV64A` — internally odd either way, and left that way.** The `LV` designator and the row's
distinct `0x1401` voltage word both point toward a genuine 3.3 V rail, unlike its fifteen siblings.
But its own `vcc_mv` of 5500 stays implausible regardless of which way `vdd_mv` is read — a 3.3 V
part reporting a 5.5 V read rail is odd on either reading. The disposition does not resolve this
row in one direction; it stays disposed exactly like the other fifteen, unchanged, for the same
D-11 reason.

**The decisive in-repo contradiction, already shipped in code.** The pending todo characterises
sub-group 1 as *"genuinely-3.3V Microchip memory-family parts, plus AMD's second-sourced
equivalents"* `[VERIFIED: .planning/todos/pending/vcc-5500-high-margin-verify-rail-group.md,
quoted verbatim]`. Phase 148's own decision record calls the identical sixteen rows the opposite:
its discussion log states *"sixteen 5 V Microchip EEPROMs"*
`[VERIFIED: .planning/milestones/v1.32-phases/148-numeric-database-values-the-at28c-vcc-decode/148-DISCUSSION-LOG.md:44]`,
its plan's threat model records *"over-broad margin-rail condition setting 16 genuinely-5 V
EEPROMs to 3.3 V"*
`[VERIFIED: .planning/milestones/v1.32-phases/148-numeric-database-values-the-at28c-vcc-decode/148-06-PLAN.md:458]`,
and the comment shipped on the value-keyed `vcc_mv`-from-`vdd_mv` rewrite in
`firestarter_app/tools/build_db.py` — cited, not edited — says the same thing about the same
substitution: *"Do NOT widen this to a type, algorithm or relational key without re-measuring: all
three were tried and each drags in sixteen genuinely-5V EEPROMs and sets them to 3.3V — worse than
the defect being fixed."* Three independent citations, one shipped in source, call the same rows
genuinely 5 V; the pending todo alone calls them genuinely 3.3 V. **These are provably the same
sixteen rows** — exactly sixteen rows in the live database carry the pair `(vcc_mv 5500, vdd_mv
3300)`, and they are the only rows a type- or algorithm-keyed `vcc := vdd` rule could move. This
disposition sides with the measurement: Phase 148's three independent, previously-shipped
citations against the pending todo's single unevidenced characterisation.

**Sub-group 2's contrast, and the falsified archived claim (D-14).** The archived
`148-DB-DIFF.md` § "Non-claim" states that these twelve rows' operating voltage is *"the actual
... 5.0 V operating rail their own `vdd_mv` already records"*
`[VERIFIED: .planning/milestones/v1.32-phases/148-numeric-database-values-the-at28c-vcc-decode/148-DB-DIFF.md,
§ "Non-claim", "already records"]`. **This phase falsifies that.** Before this phase's
`VCC_VOLTAGES` completion, vdd index `0x06` was unmapped, so the `5000` these twelve rows carried
was never a decode of anything — it was the `.get(idx, 5000)` unmapped-index fallback. The
completed table now decodes `0x06` to `1800`, which is why these twelve are held at their
pre-completion `5000` by explicit `UNSOURCED` override entries rather than left to fall through.
The `148-DB-DIFF.md` text is not edited — archived records are historical-by-intent, and rewriting
one destroys the evidence of what was believed at the time — but its claim is recorded against
here and in `DECODE-NOTES.md` § 9, by pointing at the archived text, path and section.

## Honesty limit

The repository vendors **13** datasheet PDFs (`AT28C256.pdf`, `LST62832I.pdf` *(untracked)*,
`M27C1001.pdf`, `M27C512.pdf`, `MBM27128.pdf`, `MBM27C1000.pdf`, `MBM27C1001.pdf`,
`MBM27C4001.pdf`, `MX27C4000.pdf`, `SST39SF0x0A.pdf`, `W27C020.pdf`, `W27C512.pdf`,
`W27E257.pdf`), and **not one of them is a Microchip datasheet or an AMD datasheet.** The two ST
parts vendored (`M27C1001`, `M27C512`) are UV EPROMs, unrelated to the 28C-family EEPROMs this
group is about. So **not one of the 16 sub-group-1 rows has a vendored datasheet**, and every
disposition above for those sixteen is a part-class inference plus an in-repo measurement — never
a datasheet reading. This is a real gap, not a formality: closing any of the sixteen with
confidence requires a Microchip or AMD datasheet this repository does not have. Sub-group 2 fares
no better — its twelve `UNSOURCED` override entries each say plainly that no datasheet backs the
`5000` they hold.

## What the successor entry must carry

28 rows still report `vcc_mv: 5500`; 12 of them are additionally held at an unsourced `5000`;
closing any of the 28 with confidence requires one datasheet per row, and 16 of the 28 (all of
sub-group 1) have no route to that closure without a Microchip or AMD datasheet first entering
this repository. `198-BACKLOG-DRAFT.md` carries this forward as the successor to the todo this
record closes.

---
*Phase: 198-the-two-voltage-nibbles*
*Measured: 2026-09-18*
