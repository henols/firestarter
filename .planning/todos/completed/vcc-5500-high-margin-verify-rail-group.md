---
created: 2026-08-19T00:00:00Z
title: "vcc == 5500 high-margin verify-rail group (28 chips) reports the wrong operating voltage"
area: host
resolves_phase: 198
files:
  - firestarter_app/tools/build_db.py
  - .planning/phases/148-numeric-database-values-the-at28c-vcc-decode/148-DB-DIFF.md
---

## Problem

Phase 148 (DATA-01/DATA-05) corrected a 56-chip group whose decoded `vcc_mv` landed on the TL866's
**low**-margin verify rail (`VCC_VOLTAGES[0x02] == 4000`) by substituting the chip's own decoded
`vdd_mv`. There is a second, inverted instance of the exact same category error that Phase 148
deliberately did **not** touch: **28 chips** whose decoded `vcc_mv` lands on the TL866's
**high**-margin verify rail (`VCC_VOLTAGES[0x04] == 5500`), so `firestarter info` currently reports
**5.5 V** for parts that actually run at either 3.3 V or 5.0 V.

Measured directly against the live `firestarter/data/chip_database.json` (748-chip generation from
this phase), partitioned by `electrical.vdd_mv`:

**Sub-group 1 — 16 chips at `vcc_mv: 5500` / `vdd_mv: 3300`** (genuinely-3.3V Microchip
memory-family parts, plus AMD's second-sourced equivalents), all algorithm `0x0D`:
`AM28C16A` · `AM28C17A` · `2804` · `2816` · `2817` · `28C04A` · `28C04AF` · `28C16A` · `28C16AF` ·
`28C17A` · `28C17AF` · `28C256,28C256F` · `28C64A` · `28C64AF` · `28C64B` · `28LV64A`

**Sub-group 2 — 12 chips at `vcc_mv: 5500` / `vdd_mv: 5000`** (genuinely-5V EXEL and ST/SGS-THOMSON
parts), all algorithm `0x0D`:
`XL2804A` · `XL2816A,XLE28C16A,XLS28C16A` · `XLE2865A,XLS2865A` · `XLE28C16B,XLS28C16B` ·
`XLE28C64A,XLS28C64A` · `XLE28C64B,XLS28C64B` · `XLE28C256,XLS28C256` (manufacturer `EXEL`) ·
`M28C64,M28C64A` (manufacturer `SGS-THOMSON`) · `M28C64-xxW` (manufacturer `SGS-THOMSON`) ·
`M28C64,M28C64A` (manufacturer `ST` — a distinct database entry from the `SGS-THOMSON` one above,
same part number) · `M28C64-xxW` (manufacturer `ST`) · `M28LV64` (manufacturer `ST`)

**16 + 12 = 28** (not 29 — 148-CONTEXT.md's `<deferred>` prose said 29/16+13, but its own D-03
table said 12 for the second row, and 148-RESEARCH.md F-6 confirmed 12 by direct measurement; D-03
was correct).

## Why this is not fixed yet

Unlike the 56-chip group Phase 148 corrected — where `vdd_mv` was unambiguously the right
substitution target — the correct target for this group is **unproven**. Algorithm `0x07` shows
`vdd` taking **both** 5500 and 6500 across different chips in that same family, so a simple
"read-rail vs. program-rail" reading of `infoic.xml`'s two voltage nibbles is **not uniform**
across chip families. Applying the same "substitute `vdd_mv`" mechanism here without first
establishing, per family, what the two nibbles actually encode would repeat exactly the kind of
unproven category assumption Phase 148's own D-03 justification was careful to avoid for the
56-chip group.

## Solution (TBD)

Candidate next step: enumerate every algorithm family touching `VCC_VOLTAGES[0x04]` (5500 mV) and
independently establish, from `infoic.xml`'s own field semantics (or upstream minipro source) per
family, whether the two nibbles at that position encode a read-rail/program-rail split uniformly
or whether some families need a different substitution (or no substitution at all). Only once that
is established should a `RULE_VCC_HIGH_MARGIN_RAIL`-shaped correction (mirroring
`RULE_VCC_MARGIN_RAIL`'s decode-table-only, value-keyed shape) be added to `build_db.py` and
`diff_db.py`.

Cross-reference: `.planning/phases/148-numeric-database-values-the-at28c-vcc-decode/148-DB-DIFF.md`
§"Non-claim" for the full derivation, citation, and blast-radius discipline this group must be held
to before any fix lands.
