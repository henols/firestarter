**Draft for the orchestrator to apply to `.planning/ROADMAP.md`.** The executor drafts and
verifies this entry but does not write `ROADMAP.md` — that file is a single-writer artifact the
orchestrator applies after confirming it is byte-identical to its pre-dispatch snapshot. Insert the
block below immediately after the entry for backlog phase `999.72` (the current last backlog
entry, so the next free number is `999.73`), preserving the existing `---` separator convention
between entries.

---

### Phase 999.73: The 28-row `vcc_mv == 5500` group still reports the wrong operating voltage for 16 of its rows (BACKLOG — filed 2026-09-18 during v1.40 Phase 198, from `198-VOLT03-DISPOSITION.md`)

**Goal:** Close each of the 28 rows with the vendor-specific datasheet that would settle whether
its reported `vcc_mv: 5500` should move to its `vdd_mv`, or revert to the same value the read for
that class of chip has always used.

**MEASURED** (from `198-VOLT03-DISPOSITION.md`, the phase's per-row disposition record): 28 rows
still report `vcc_mv: 5500` — 16 at decoded `(vcc 5500, vdd 3300)` and 12 at decoded `(vcc 5500,
vdd 1800)`. All 28 ship unchanged this phase (D-11), as VOLT-03 explicitly permits. 12 of the 28
are additionally held at an unsourced `vdd_mv: 5000` by twelve explicit `UNSOURCED` entries in
`tools/datasheet_overrides.json`, each naming the part's own datasheet as what would close it.
The repository vendors 13 datasheet PDFs and not one is a Microchip or an AMD datasheet, so 16 of
the 28 (all of sub-group 1: `AM28C16A`, `AM28C17A`, `2804`, `2816`, `2817`, `28C04A`, `28C04AF`,
`28C16A`, `28C16AF`, `28C17A`, `28C17AF`, `28C256,28C256F`, `28C64A`, `28C64AF`, `28C64B`,
`28LV64A`) have no route to closure without a new PDF entering this repository first.

**What would close each:** one datasheet per row, vendored and git-tracked. The 15 non-`28LV64A`
sub-group-1 rows each need a Microchip or AMD datasheet for that specific part; `28LV64A` needs
Microchip's own 28LV64A datasheet, which would also settle whether its `vcc_mv: 5500` is itself
wrong (a 3.3 V part reporting a 5.5 V read rail is odd regardless of how `vdd_mv` reads). The 12
sub-group-2 rows each need the EXEL, ST or SGS-THOMSON datasheet the corresponding `UNSOURCED`
override entry already names.

**Consequence of leaving them:** `firestarter info` continues to report 5.5 V for 28 parts whose
own decoded program rail (`vdd_mv`) already disagrees with that figure, exactly the same category
error Phase 148 corrected for 56 other rows in the inverse direction. The group is now fully
disposed and the in-repo contradiction between the pending todo's premise and Phase 148's own
prior measurement is resolved in favor of the measurement, but resolving the contradiction did not
change a single emitted value — closing any of the 28 with confidence still requires the datasheet
this repository does not yet vendor for it.

---
