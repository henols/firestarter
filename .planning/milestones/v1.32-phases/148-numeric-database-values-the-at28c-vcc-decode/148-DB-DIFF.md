# 148-DB-DIFF.md — Phase 148 D-12 review artifact

Per D-12 (148-CONTEXT.md), this is the single reviewable document carrying the phase's `diff_db.py`
run output, the mover list, the D-03 justification, and the explicit non-claim about the untouched
`vcc=5500` group. Later plans in this phase append `## After`, the 56-chip mover list, the
justification, and the non-claim sections below the `## Before` section captured here.

## Before

Measured this session from `/workspaces/firestarter_app`, HEAD `9701209` (pre-Phase-148 content for
`tools/build_db.py`, `firestarter/data/chip_database.json`, `firestarter/database.py`) — same tree
Plan 01 Task 1 captured the wire-dict golden against.

### `python3 tools/diff_db.py ; echo EXIT=$?`

```
========================================================================
GATE-02 Per-chip Diff Report
  Baseline: /workspaces/firestarter_app/tools/baseline/chip_database.baseline.json  (746 chips, 746 diffed)
  Current:  /workspaces/firestarter_app/tools/../firestarter/data/chip_database.json  (746 chips, 746 diffed)
========================================================================

--- CHANGED chips (744 total) ---

[PGSZ_PAGE_SIZE] (2 chips)
  Phase 94 PGSZ-01 / CR-01 — datasheet-sourced per-chip page_size field added.
  Affected part_numbers (2):
    W29C020,W29C020C,W29C022
    W29C040,W29C042

[PROV01_PROTECT_METADATA] (742 chips)
  Phase 136.1 PROV-01 — flags bit 14/15 + raw page_size decode added to the
  programming block: protect_off_before, protect_on_after, infoic_page_size_raw.
  Metadata only — no algorithm / pinout / vpp / electrical.type delta; the
  84/43/41 SDP ALLOW/REFUSE partition (tests/test_sdp_db_invariant.py) is
  unchanged.
  Affected part_numbers (742): [full list measured, omitted here for length —
  reproducible verbatim via the command above]

--- COMPOUND changes (2) — algo+other deltas ---

  W29C020,W29C020C,W29C022 [PGSZ_PAGE_SIZE] + secondary: programming.infoic_page_size_raw, programming.protect_off_before, programming.protect_on_after
  W29C040,W29C042 [PGSZ_PAGE_SIZE] + secondary: programming.infoic_page_size_raw, programming.protect_off_before, programming.protect_on_after

--- NEW chips (0) — expected Rule 1 unblock (DIP24_2816 + algo=0x0D) ---

--- MISSING chips (0) ---

PASS: all 744 changed chips explained (0 new chips confirmed; 0 chips removed from baseline)
EXIT=0
```

**Why 744 is the correct baseline, not "zero changed chips" (RESEARCH F-2).**
`tools/baseline/chip_database.baseline.json` predates Phase 136.1 — it carries no
`protect_off_before` / `protect_on_after` / `infoic_page_size_raw` and no `page_size`, so 744 of 746
chips already diff against it today, and every one of those 744 is already explained by a named,
cited rule (`PGSZ_PAGE_SIZE`, `PROV01_PROTECT_METADATA`). The baseline is **NOT re-pinned** by this
phase (**D-11**) — `tools/baseline/chip_database.baseline.json` stays as-is, and `diff_db.py`'s
comparator is what normalizes the migration's 56 movers into their own new bucket, not a baseline
regeneration. A criterion phrased "`diff_db.py` reports zero changed chips" would therefore be a
false RED: it is unachievable against this un-re-pinned baseline and was never the correct target —
the achievable, equally strong form is that the changed-chip total and every existing bucket count
stay unchanged after migration, with the 56 movers appearing as their own new, separately-named
bucket.

### `python3 tools/check_dispatch.py ; echo EXIT=$?`

```
PASS: all 746 chips scanned; 736 supported; 10 chips confirmed non-dispatchable (D-12: host guard
covers non-supported chips with real handlers; non-handler outcomes also safe); 0
non_supported_dispatchable (gate GREEN because chip_resolver.resolve_chip refuses, not because sim
pretends mem_type=None); 0 dispatch regressions; 0 consistency violations
EXIT=0
```

Measured summary: 746 scanned, 736 supported, 0 violations (0 dispatch regressions + 0 consistency
violations, the tool's own two named violation counters), `EXIT=0`.

### `python3 -m pytest tests/test_chip_database_field_inventory.py -o addopts="" -q`

```
........                                                                 [100%]
8 passed in 0.09s
```

### `firestarter info AT28C256` (with `FIRESTARTER_CONFIG_DIR` pointed at an empty scratch dir)

```
Eprom Info
Name:               AT28C256,AT28C256E,AT28C256F,AT28HC256,AT28HC256E,AT28HC256F,AT28HC256L
Manufacturer:       ATMEL
Number of pins:     28
Memory size         0x8000
Type:               EEPROM
Can be erased:      yes (electrically erasable)
VCC:                4.0v
VPP:                12.0v
Chip ID:            -
...
Protocol: EEPROM - 5V parallel, SDP + DQ7 poll (ID: 0x0D)
Flags: 0x00000010
  - Electrically erasable
```

`VCC:` reads `4.0v` and `VPP:` reads `12.0v` — the pre-change AT28C256 decode this phase's later
plans will correct.

## Wire equivalence (D-14 / D-06)

Measured this session from `/workspaces/firestarter_app`, on the `gsd/v1.32-at28c-write-path-root-cause-report-provenance`
branch, after Plan 04 Task 1 (`database.py`'s coercion layer deleted, `format_mv` added, direct
indexing on `vcc_mv`/`vpp_mv`/`pulse_duration_us`) and Task 2 (all three display call sites moved
onto `format_mv`) both landed.

### `python3 -m pytest tests/test_wire_dict_equivalence.py -o addopts="" -q`

```
.....                                                                    [100%]
5 passed in 0.55s
```

All 5 tests pass, including the byte-identity leg: the live 746-chip
`EpromDatabase(skip_local_override=True) -> get_eprom -> convert_to_programmer` capture is
**byte-identical** to the Plan 01 pre-change golden (`tests/golden/wire_dict_baseline.json`,
SHA-256 `027a43a0dcef1085afa6a35d2500bd35556140dde4b838dfcd65bfae8cac7dab`). The golden itself was
**not** re-pinned or regenerated by this plan.

### `git diff --stat tests/__snapshots__/test_characterization.ambr`

```
(empty output)
```

The pinned characterization snapshot is **byte-unchanged** — `git diff --quiet` on it succeeds.

### `python3 tools/check_dispatch.py ; echo EXIT=$?`

```
PASS: all 746 chips scanned; 736 supported; 10 chips confirmed non-dispatchable (D-12: host guard
covers non-supported chips with real handlers; non-handler outcomes also safe); 0
non_supported_dispatchable (gate GREEN because chip_resolver.resolve_chip refuses, not because sim
pretends mem_type=None); 0 dispatch regressions; 0 consistency violations
EXIT=0
```

**Claim for the record:** the numeric migration changed no value that reaches the firmware and no
byte that reaches the user. Mechanism: `vcc` and `vpp_volts` are absent from all nine wire keys
`convert_to_programmer` emits (`database.py`'s mapped dict now carries `vcc_mv`/`vpp_mv` only, and
`convert_to_programmer` reads `vpp_mv` directly), so a VCC decode change cannot reach `write` — the
wire never carried `vcc` in the first place (**D-06**). The render contract
`f"{mv / 1000:.1f}v"` (`format_mv`) is byte-exact for all 13 distinct database voltages, so no
rendered byte moved either (**D-15**).

**Correction to the record (RESEARCH F-3):** CONTEXT.md's D-15 supporting prose stated the proof as
"the snapshot diff changes on exactly the AT28C-family lines" — this proof mechanism does **not**
exist. No AT28C VCC line appears in any pinned snapshot; the only info-view snapshot in
`test_characterization.py` runs `firestarter info W27C512`, which is not a mover (its VCC/VPP values
are unaffected by the AT28C-specific decode this phase's later plans address). The criterion this
phase actually holds to, and the one measured above, is the stronger one: the `.ambr` file is
**byte-unchanged** in its entirety. Criterion 1 (AT28C256's `VCC:` line moving to the corrected
value) gets a **new**, dedicated test in Plan 06 — it does not exist yet and was never claimed to
exist in this section.

## Plan 06 — the VCC margin-rail substitution (D-01/D-02/D-03)

Measured this session from `/workspaces/firestarter_app`, on the
`gsd/v1.32-at28c-write-path-root-cause-report-provenance` branch, immediately after
`build_db.py`'s `_VCC_MARGIN_RAIL_MV` constant and post-construction margin-rail substitution
landed (before `diff_db.py`'s `RULE_VCC_MARGIN_RAIL` classification rule existed).

### RED — `python3 tools/diff_db.py ; echo EXIT=$?` (before the diff_db.py rule)

**Correction to the plan's predicted mechanism.** `148-06-PLAN.md`'s Task 1 predicted `EXIT=1`
with the 56 movers landing in `UNEXPLAINED`, on the theory that no rule claims the
`("electrical","vcc_mv")` path for them. That theory did not hold: the pre-existing `BUG3_VCC_VDD`
rule's condition (`voltage_diff and not timing_diff and not algo_diff`) does not check
`pinout_diff`/`type_diff`/`vpp_diff`, so it matches ANY chip whose only voltage field changed —
including these 56 movers — and **misattributes them to the Phase 57/58 vcc/vdd label-swap
rationale**, which is not what happened here (D-01: the vcc/vdd labels are correct; only the
margin-rail value is substituted). The measured RED is therefore `EXIT=0`, not `EXIT=1` — arguably
a **stronger** proof of D-11's need than the predicted RED: before the new rule, the movers are
silently swallowed by the WRONG existing rule rather than surfaced as unexplained.

```
--- CHANGED chips (744 total) ---

[BUG3_VCC_VDD] (56 chips)
  BUG-3 vcc/vdd label swap only — inverted field labels corrected.
    bits 11-8 = vcc (VCC supply voltage), bits 15-12 = vdd (VDD programming voltage).
    Previously the decode had these reversed.
    [VERIFIED: minipro database.c#L921-L923 @ a8efaedc —
     https://gitlab.com/DavidGriffith/minipro/-/blob/a8efaedc/src/database.c#L921]
  Affected part_numbers (56):
    AM28C64A,AM28C64AE,AM28C64B,AM28C64BE
    AT28BV256,AT28LV256
    AT28BV64,AT28LV64
    AT28BV64B,AT28LV64B
    AT28C010,AT28C010E
    AT28C04,AT28HC04
    AT28C040,AT28C040E
    AT28C04E,AT28C04F
    AT28C16,AT28HC16,AT28HC16L
    AT28C16E,AT28C16F
    AT28C17
    AT28C17E,AT28C17F
    AT28C256,AT28C256E,AT28C256F,AT28HC256,AT28HC256E,AT28HC256F,AT28HC256L
    AT28C64,AT28C64B(Non-Standard),AT28HC64,AT28HC64L
    AT28C64B,AT28HC64B,AT28HC64BF
    AT28C64E,AT28C64F
    AT28LV010
    AT28MC010
    AT28MC020
    AT28MC040
    AT28PC64,AT28PC64E
    CAT28C010
    CAT28C020
    CAT28C040
    CAT28C16A,CAT28C16AI
    CAT28C17A
    CAT28C256,CAT28C257
    CAT28C512
    CAT28C64A,CAT28C65
    CAT28C64B
    CAT28LV256
    CAT28LV64,CAT28LV65
    FM28V020
    HN58C256AP
    28C010,28C010T,28C011,28C011T
    UPD28C04
    UPD28C256
    UPD28C64
    KM28C64
    KM28C64A,KM28C65A
    M28010
    M28010
    M28256
    WE128K8
    WE256K8
    WE512K8
    WME128K8
    X2804A,X2804AI
    X2816A
    X2816B,X2816C
    X28256,X28C256
    X2864AP
    X28C010
    X28C64(NonStandard),X28HC64(NonStandard)
    X28C64,X28HC64
    X88C64P,X88C64S

[PGSZ_PAGE_SIZE] (2 chips)
  ... (unchanged from Before)

[PROV01_PROTECT_METADATA] (686 chips)
  ... (the 56 movers dropped OUT of this bucket relative to the pre-migration 742,
       because they now ALSO have a voltage delta -- but they land in the WRONG
       bucket, BUG3_VCC_VDD, not their own)

--- COMPOUND changes (58) — algo+other deltas ---
  (the 56 movers appear here too, each: [BUG3_VCC_VDD] + secondary:
   programming.infoic_page_size_raw, programming.protect_off_before,
   programming.protect_on_after)

--- NEW chips (0) ---
--- MISSING chips (0) ---

PASS: all 744 changed chips explained (0 new chips confirmed; 0 chips removed from baseline)
EXIT=0
```

**Structural regen proof (Task 1's own acceptance criteria, still valid):** the regenerated
`chip_database.json` has 746 chips total, **0** chips at `vcc_mv == 4000`, and no chip's `vcc_mv`
lower than its pre-rule value — confirmed independently of `diff_db.py`'s classification bucket
naming.

### GREEN — `python3 tools/diff_db.py ; echo EXIT=$?` (after `RULE_VCC_MARGIN_RAIL` landed)

`RULE_VCC_MARGIN_RAIL` inserted into `_RATIONALES`, `_RULE_FIELD_PATHS`, and a value-scoped
`_classify_diff` branch placed **before** `BUG3_VCC_VDD` (baseline `vcc_mv == 4000` AND current
`vcc_mv == current vdd_mv` AND current `vcc_mv != 4000`, with the usual
algo/timing/pinout/type exclusivity terms).

```
--- CHANGED chips (744 total) ---

[RULE_VCC_MARGIN_RAIL] (56 chips)
  Phase 148 DATA-01 (D-01/D-02/D-03) — VCC margin-rail substitution.
    infoic.xml's VCC nibble 2 (VCC_VOLTAGES[0x02] = 4000 mV) is decoded FAITHFULLY —
    this is not a decode repair. The defect is semantic: minipro's vcc is the TL866's
    low-margin VCC *verify* rail, and firestarter surfaced it as the chip's operating
    supply. The substitution targets the already-decoded vdd_mv (itself an
    infoic.xml-decoded value, so nothing is invented) whenever vcc_mv lands on this
    rail: build_db.py::_VCC_MARGIN_RAIL_MV, applied post-construction.
    No other delta: exactly 56 chips move, every one 4000 -> 5000 mV, and no chip's
    vcc_mv is ever lowered by this rule (Test 3's no-decrease guard,
    tests/test_vcc_margin_rail.py).
    [VERIFIED: minipro database.c#L130-L135 @ a8efaedc —
     https://gitlab.com/DavidGriffith/minipro/-/blob/a8efaedc/src/database.c#L130]
    [CITED: .planning/phases/148-numeric-database-values-the-at28c-vcc-decode/148-DB-DIFF.md]
  Affected part_numbers (56):
    AM28C64A,AM28C64AE,AM28C64B,AM28C64BE
    AT28BV256,AT28LV256
    AT28BV64,AT28LV64
    AT28BV64B,AT28LV64B
    AT28C010,AT28C010E
    AT28C04,AT28HC04
    AT28C040,AT28C040E
    AT28C04E,AT28C04F
    AT28C16,AT28HC16,AT28HC16L
    AT28C16E,AT28C16F
    AT28C17
    AT28C17E,AT28C17F
    AT28C256,AT28C256E,AT28C256F,AT28HC256,AT28HC256E,AT28HC256F,AT28HC256L
    AT28C64,AT28C64B(Non-Standard),AT28HC64,AT28HC64L
    AT28C64B,AT28HC64B,AT28HC64BF
    AT28C64E,AT28C64F
    AT28LV010
    AT28MC010
    AT28MC020
    AT28MC040
    AT28PC64,AT28PC64E
    CAT28C010
    CAT28C020
    CAT28C040
    CAT28C16A,CAT28C16AI
    CAT28C17A
    CAT28C256,CAT28C257
    CAT28C512
    CAT28C64A,CAT28C65
    CAT28C64B
    CAT28LV256
    CAT28LV64,CAT28LV65
    FM28V020
    HN58C256AP
    28C010,28C010T,28C011,28C011T
    UPD28C04
    UPD28C256
    UPD28C64
    KM28C64
    KM28C64A,KM28C65A
    M28010
    M28010
    M28256
    WE128K8
    WE256K8
    WE512K8
    WME128K8
    X2804A,X2804AI
    X2816A
    X2816B,X2816C
    X28256,X28C256
    X2864AP
    X28C010
    X28C64(NonStandard),X28HC64(NonStandard)
    X28C64,X28HC64
    X88C64P,X88C64S

[PGSZ_PAGE_SIZE] (2 chips)
  (unchanged)

[PROV01_PROTECT_METADATA] (686 chips)
  (unchanged bucket rationale; count dropped from the pre-migration 742 by exactly
   the 56 chips that now correctly classify as RULE_VCC_MARGIN_RAIL instead)

--- COMPOUND changes (58) — algo+other deltas ---
  28C010,... [RULE_VCC_MARGIN_RAIL] + secondary: programming.infoic_page_size_raw,
    programming.protect_off_before, programming.protect_on_after
  (55 more RULE_VCC_MARGIN_RAIL compound entries, same secondary set;
   2 PGSZ_PAGE_SIZE compound entries, unchanged from Before)

--- NEW chips (0) ---
--- MISSING chips (0) ---

PASS: all 744 changed chips explained (0 new chips confirmed; 0 chips removed from baseline)
EXIT=0
```

**Measured distribution (exactly as predicted by 148-CONTEXT.md D-11's corrected mechanism):**
changed-chip total **744** (unchanged), `RULE_VCC_MARGIN_RAIL` **56** (new bucket),
`PROV01_PROTECT_METADATA` **686** (dropped from 742 by exactly the 56 movers),
`PGSZ_PAGE_SIZE` **2** (unchanged), `NEW` **0**, `MISSING` **0**. Every pre-existing bucket count
is unchanged except `PROV01_PROTECT_METADATA`'s drop, which is exactly accounted for by the new
bucket. `tools/baseline/chip_database.baseline.json` is **NOT re-pinned** (confirmed
`git diff --quiet` clean). `tools/check_dispatch.py` (GATE-03) is byte-unchanged and exits 0 with
0 violations.

### The 56-chip mover list (D-12) — by manufacturer

Measured across 12 manufacturers: ATMEL 20, CATALYST(CSI) 11, XICOR 9, WED 4, NEC 3, SAMSUNG 2,
ST 2, AMD 1, CYPRESS 1, HITACHI 1, MAXWELL 1, SGS-THOMSON 1 — matching 148-CONTEXT.md D-03's
measured blast radius exactly. See the full part-number list in the RED/GREEN transcripts above
(identical set in both; only the classifying bucket differs).

### Justification (D-03, restated with its citation)

`_VCC_MARGIN_RAIL_MV = VCC_VOLTAGES[0x02]` (`build_db.py`), keyed on the **decoded value alone** —
`chip_entry["electrical"]["vcc_mv"] == _VCC_MARGIN_RAIL_MV` → substitute `vdd_mv`. No part number,
no `type`, no `algorithm`. `[VERIFIED: minipro database.c#L130-L135 @ a8efaedc —
tl866ii_vcc_voltages[]]`. Rejected alternatives, measured: type-keyed → 85 movers (16 set to
3.3V); algorithm-keyed (`0x0D`) → 84 movers (16 set to 3.3V); relation-keyed
(`vcc < vdd <= 5500`) → 225 movers (sweeps in UV-EPROMs whose `vdd` is the 6.5V program rail).

### Explicit non-claim: the `vcc=5500` EEPROM-class group (29 chips) is untouched

Sixteen Microchip parts (`28C256`, `28C16A`, `28C64A`, `2817`, `2804`, `28LV64A`, …) carry
`vcc_mv: 5500` against `vdd_mv: 3300`; thirteen EXEL / SGS-THOMSON / ST parts (`XL2816A`,
`XLE28C64A`, `M28C64`, …) carry `vcc_mv: 5500` against `vdd_mv: 5000`. This is the SAME category
error inverted — a high-margin verify rail surfaced as the operating supply — and it means
`firestarter info` still reports 5.5V for parts that run at 5V. **This phase makes no claim about
that group and does not touch it**: the correct target is unproven without establishing from
`infoic.xml` what the two nibbles encode per family (148-CONTEXT.md `<deferred>`). Filed as a
pending todo, not fixed here.

**Correction (Plan 08 / RESEARCH F-6):** the "29 chips" heading above is superseded. CONTEXT.md's
`<deferred>` prose said 29 (16 + 13), but its own D-03 table said 12, not 13, for the second row.
148-RESEARCH.md F-6 measured the second sub-group directly against the live database: **12**, not
13 — total **28**, not 29. D-03's table was correct; the `<deferred>` prose's 13 was the stale
number. See `## Non-claim` below for the corrected, exact-count restatement with full part lists.

## The 56 movers

Plan 08 (D-12): the full per-chip mover list, derived programmatically from
`firestarter/data/chip_database.json` against `tools/baseline/chip_database.baseline.json`
(matched on `(manufacturer, part_number, index)` — part numbers are not unique across
manufacturers, e.g. `M28010` appears under both `SGS-THOMSON` and `ST`), grouped by manufacturer
with each chip's `programming.algorithm`. Every one of these 56 chips moves `vcc_mv` from
`4000 -> 5000`; no other field changes. Measured distribution by manufacturer, 12 manufacturers,
56 chips total — matching 148-CONTEXT.md D-03's measured blast radius exactly:

**ATMEL — 20 — all algorithm `0x0D`:**
`AT28BV64,AT28LV64` · `AT28BV64B,AT28LV64B` · `AT28BV256,AT28LV256` · `AT28C010,AT28C010E` ·
`AT28C04,AT28HC04` · `AT28C04E,AT28C04F` · `AT28C040,AT28C040E` · `AT28C16,AT28HC16,AT28HC16L` ·
`AT28C16E,AT28C16F` · `AT28C17` · `AT28C17E,AT28C17F` ·
`AT28C256,AT28C256E,AT28C256F,AT28HC256,AT28HC256E,AT28HC256F,AT28HC256L` ·
`AT28C64,AT28C64B(Non-Standard),AT28HC64,AT28HC64L` · `AT28C64B,AT28HC64B,AT28HC64BF` ·
`AT28C64E,AT28C64F` · `AT28LV010` · `AT28MC010` · `AT28MC020` · `AT28MC040` ·
`AT28PC64,AT28PC64E`

**CATALYST(CSI) — 11 — all algorithm `0x0D`:**
`CAT28C16A,CAT28C16AI` · `CAT28C17A` · `CAT28C256,CAT28C257` · `CAT28C64A,CAT28C65` ·
`CAT28C64B` · `CAT28C512` · `CAT28C010` · `CAT28C020` · `CAT28C040` · `CAT28LV64,CAT28LV65` ·
`CAT28LV256`

**XICOR — 9 — 8 on algorithm `0x0D`, 1 on algorithm `0x34` (protocol-not-implemented):**
`X2804A,X2804AI` · `X2816A` · `X2816B,X2816C` · `X28256,X28C256` · `X2864AP` · `X28C010` ·
`X28C64,X28HC64` · `X28C64(NonStandard),X28HC64(NonStandard)` — all `0x0D`; and
`X88C64P,X88C64S` — algorithm `0x34` (this is the one non-`0x0D` mover; the rule is keyed on the
decoded voltage value alone, not on algorithm, so it correctly reaches this chip too).

**WED — 4 — all algorithm `0x0D`:**
`WE128K8` · `WE256K8` · `WE512K8` · `WME128K8`

**NEC — 3 — all algorithm `0x0D`:**
`UPD28C04` · `UPD28C256` · `UPD28C64`

**SAMSUNG — 2 — all algorithm `0x0D`:**
`KM28C64` · `KM28C64A,KM28C65A`

**ST — 2 — all algorithm `0x0D`:**
`M28010` (manufacturer key `ST`) · `M28256`

**AMD — 1 — algorithm `0x0D`:**
`AM28C64A,AM28C64AE,AM28C64B,AM28C64BE`

**CYPRESS — 1 — algorithm `0x0D`:**
`FM28V020`

**HITACHI — 1 — algorithm `0x0D`:**
`HN58C256AP`

**MAXWELL — 1 — algorithm `0x0D`:**
`28C010,28C010T,28C011,28C011T`

**SGS-THOMSON — 1 — algorithm `0x0D`:**
`M28010` (manufacturer key `SGS-THOMSON` — a distinct database entry from `ST`'s `M28010` above;
same part number, two different manufacturer-keyed rows, both movers)

Total: 20+11+9+4+3+2+2+1+1+1+1+1 = **56**. 55 chips on algorithm `0x0D`, 1 chip
(`X88C64P,X88C64S`) on algorithm `0x34`.

## Why this condition

`_VCC_MARGIN_RAIL_MV = VCC_VOLTAGES[0x02]` (`tools/build_db.py`) — a **lookup**, never a re-typed
literal — into the existing, faithfully-decoded `VCC_VOLTAGES` table:
`[VERIFIED: minipro database.c#L130-L135 @ a8efaedc — tl866ii_vcc_voltages[] —
https://gitlab.com/DavidGriffith/minipro/-/blob/a8efaedc/src/database.c#L130]`. The claim is about
the decode table itself, not a patch aimed at one family:
**4 V is a real number that is not a real voltage** — no part in this 746-chip database has a
4.0 V nominal operating supply. Index
`0x02` of `tl866ii_vcc_voltages[]` is the TL866 programmer's low-margin **verify** rail, not any
chip's operating supply, so whenever a chip's decoded `vcc_mv` lands on this rail
(`chip_entry["electrical"]["vcc_mv"] == _VCC_MARGIN_RAIL_MV`), the rule substitutes the chip's own
already-decoded `vdd_mv` (itself an `infoic.xml`-decoded value — nothing is invented). Keyed on the
decoded value alone: no part number, no `type`, no `algorithm`.

**The four-way `0x0D` split, as measured (148-CONTEXT.md D-03 / 148-RESEARCH.md), the load-bearing
measurement that must not be re-derived or the condition widened against:** `vcc != vdd` on 358 of
746 chips overall, and within the `0x0D` family specifically it splits four ways —

| count | vcc | vdd | aligning to vdd would give |
|---|---|---|---|
| 55 | 4000 | 5000 | **5000 ✓** — the intended movers |
| 16 | 5500 | 3300 | **3300 ✗** — Microchip `28C256`, `28C16A`, `2817`… genuinely 5 V parts |
| 12 | 5500 | 5000 | 5000 — EXEL / ST 28C64-family (see `## Non-claim` below) |
| 1 | 3300 | 5000 | 5000 |

**Rejected alternatives, measured blast radius:**
- **Type-keyed** (`type in {EEPROM, Flash/EEPROM}`) → **85** movers, of which **16** would be set
  to **3.3 V** — genuinely 5 V Microchip EEPROMs, worse than the 4 V defect being fixed.
- **Algorithm-keyed** (`algorithm == 0x0D`) → **84** movers, of which **16** would also be set to
  **3.3 V** — the same 16 false positives as the type-keyed rule.
- **Relation-keyed** (`vcc < vdd <= 5500`) → **225** movers. By construction this rule can only
  ever raise a voltage (0 chips land on 3.3 V), but its real defect is that it sweeps in **167**
  UV-EPROMs whose `vdd` is the elevated 6.5 V program rail, not any operating supply those chips
  actually have — a different category error, not a fix.

All three rejected conditions were measured, not argued, before being rejected — the discipline
this phase's own `RULE_VCC_MARGIN_RAIL` mechanism is held to.

## Non-claim

**The `vcc == 5500` group is 28 chips (16 + 12), not 29 (16 + 13) — deliberately left untouched.**
(Supersedes this document's earlier "29 chips" heading above; see the "Correction (Plan 08 /
RESEARCH F-6)" note immediately preceding this section. 148-CONTEXT.md's own D-03 table already
said 12 for the second row — 148-RESEARCH.md F-6 confirmed 12 by direct measurement against the
live database, and D-03's table, not the `<deferred>` prose's 13, is correct.)

**Sub-group 1 — 16 chips at `vcc_mv: 5500` / `vdd_mv: 3300`** (Microchip memory-family parts,
`manufacturer` key `MICROCHIP memory`, plus AMD's two second-sourced parts), all algorithm `0x0D`:
`AM28C16A` · `AM28C17A` · `2804` · `2816` · `2817` · `28C04A` · `28C04AF` · `28C16A` · `28C16AF` ·
`28C17A` · `28C17AF` · `28C256,28C256F` · `28C64A` · `28C64AF` · `28C64B` · `28LV64A`

**Sub-group 2 — 12 chips at `vcc_mv: 5500` / `vdd_mv: 5000`** (EXEL and ST/SGS-THOMSON parts),
all algorithm `0x0D`:
`XL2804A` · `XL2816A,XLE28C16A,XLS28C16A` · `XLE2865A,XLS2865A` · `XLE28C16B,XLS28C16B` ·
`XLE28C64A,XLS28C64A` · `XLE28C64B,XLS28C64B` · `XLE28C256,XLS28C256` (all `EXEL`) ·
`M28C64,M28C64A` (manufacturer `SGS-THOMSON`) · `M28C64-xxW` (manufacturer `SGS-THOMSON`) ·
`M28C64,M28C64A` (manufacturer `ST` — a distinct database entry from the `SGS-THOMSON` one above,
same part number) · `M28C64-xxW` (manufacturer `ST`) · `M28LV64` (manufacturer `ST`)

**16 + 12 = 28.** Both lists derived directly from the live database (`electrical.vcc_mv == 5500`,
partitioned on `electrical.vdd_mv`), not copied from CONTEXT.md's illustrative examples.

**This is the SAME category error, inverted.** Just as the 56 movers had the TL866's low-margin
verify rail (`0x02` → 4000 mV) surfacing as the operating supply, these 28 chips have the TL866's
**high-margin** verify rail (`0x04` → 5500 mV) surfacing as the operating supply instead of the
actual 3.3 V or 5.0 V operating rail their own `vdd_mv` already records. Concretely:
`firestarter info` on any of these 28 parts today reports **5.5 V**, when the part actually runs
at **3.3 V** (sub-group 1) or **5.0 V** (sub-group 2).

**This phase makes no claim about this group and does not touch it.** The correct substitution
target is **unproven**, unlike the 56-chip case where `vdd_mv` was unambiguously the answer:
algorithm `0x07` shows `vdd_mv` taking **both** 5500 and 6500 across different chips in that same
family, so a read-rail-vs-program-rail reading of the two nibbles is **not uniform** across
families in `infoic.xml`. Applying the same "substitute vdd" mechanism here without first
establishing, per family, what the two nibbles actually encode risks repeating exactly the kind of
unproven category assumption this phase's own D-03 justification was careful to avoid. Filed as a
pending todo (`.planning/todos/pending/vcc-5500-high-margin-verify-rail-group.md`), not fixed
here. Neither this phase's code nor this document treats gh#21 / #32 / #11 / #12 as closed, treats
`0x0D` as verified, or changes any chip's `support_status` as a result of this non-claim.

## Evidence Ceiling

This phase corrects data the generator emits (`tools/build_db.py`'s VCC decode) and makes **no
claim** about AT28C silicon behaviour. `0x0D` stays `UNVERIFIED`, no `support_status` changes as a
result of this phase, and gh#21 / #32 / #11 / #12 stay OPEN. `vcc` is inert on the wire (D-06,
Plan 01's 9-key capture) — nothing in this correction can explain or fix `write BAD`.
