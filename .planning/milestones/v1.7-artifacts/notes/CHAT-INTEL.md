# CHAT-INTEL.md — distilled inter-rev intel for v1.7 Phase 31-34

**Source:** `.planning/milestones/v1.7-artifacts/notes/fs_an_notes.odt` (Anders↔henols 1:1) + `.planning/milestones/v1.7-artifacts/notes/discord-chat-full.csv` (full Discord channel)
**Curated:** 2026-05-22 (Phase 31)
**Quote convention:** verbatim, date-stamped to source. `> Anders YYYY-MM-DD: "..."` for the 1:1 ODT; `> henols YYYY-MM-DD: "..."` for henols's contributions. Discord-CSV-sourced quotes follow the same shape — the CSV's Username column identifies the speaker.

All quotes are verbatim, date-stamped to source. Anders = Anders Nielsen (upstream maintainer). henols = the operator (Henrik Olsson).

---

## 1. R41-on-A3 detect-divider history

> Anders 2024-10-07: "Say hello to R41 on A3."
> henols 2024-10-07: "JP1/JP3mod is now JP4."
> Anders 2025-04-28: "10k version resistor for Rev 2.2."
> Anders 2026-07-03: "I think I changed it for the 2.1 but not the 2.2 or 2.3 (only silkscreen difference)."

Synthesis: R41 voltage divider feeding Arduino A3 ADC was introduced in Rev 2.1 (Anders confirmed 2024-10-07). Rev 2.2 carries the 10k value (Anders confirmed 2025-04-28). Rev 2.3 is a silkscreen-only diff against Rev 2.2 — same R41 = 10k (Anders confirmed 2026-07-03). This establishes the per-rev baseline for Phase 34's ADC voltage-band lookup: Rev 2.1 R41 value must be extracted from the upstream `hardware/Rev2.1/` schematic; Rev 2.2 and Rev 2.3 both use 10k.

---

## 2. JP3-mod to JP4 rename

> henols 2024-10-07: "JP1/JP3mod is now JP4."

The jumper originally labelled JP3-mod (a design-revision workaround for the original JP3 footprint) was renamed to JP4 as a proper designator in the Rev 2.1 layout. This rename coincides with the introduction of the R41-on-A3 voltage-divider scheme (§1 above). The combined event — JP4 + R41 + A3 — constitutes the complete version-detect hardware introduced at Rev 2.1. Downstream implication: `JP4` is the correct designator to reference in Phase 34 firmware documentation and §3 of `v1.7-SHIELD-REVS.md`.

---

## 3. Gerbers as inter-rev source-of-truth

> Anders 2026-05-22: "Of course I do [document inter-rev changes]. But you're not going to like the answer. The gerbers!"

Synthesis: Anders uses gerber files as the canonical inter-rev diff medium, not commit messages or separate changelogs. Phase 32's inter-rev electrical/mechanical difference table may need to diff gerber files between revs, not just compare `.kicad_sch` files. The inventory `gerber_path` column (D-10) from Phase 31 enables this — `RURP-Rev2.1.zip`, `Rev2.2-gerbers.zip`, and the Rev 2.3 JLC/PCB archive are the primary diff targets.

---

## 4. Branches hold prior revs on GitHub

> Anders 2026-05-22: "branches for the previous versions on gh"

Synthesis: Rev 0 and Rev 1 schematics are preserved on the `rev2.0` branch as inline zip archives (`UniversalProgrammerRev0b0.zip`, `UniversalProgrammerRev1b0.zip`). Rev 2.1 dev work lives on `origin/Rev2.1`; Rev 2.3 on `origin/Rev2.3`. The `rev2.0` branch is a "frozen archive" of older revs, not a deletion from main. Phase 31 mine (Plan 04) walks all three rev-named branches to recover their schematics + gerbers.

---

## 5. Rev 2.3 status (silkscreen-only diff)

> Anders 2026-07-03: "I think I changed it for the 2.1 but not the 2.2 or 2.3 (only silkscreen difference)."

Rev 2.3 is electrically identical to Rev 2.2 — only the silkscreen layer differs. The `hardware/Rev2.3/jlcpcb/` subdirectory on main (with JLC PCB fabrication files) suggests Anders has manufactured Rev 2.3 prototypes. From a detect-hardware perspective, the R41-on-A3 scheme in Rev 2.3 is identical to Rev 2.2 (both 10k). Phase 34's ADC band table treats Rev 2.2 and Rev 2.3 as having the same expected voltage — the firmware detect distinguishes them via silkscreen/ADC band, not electrical differences.

---

## 6. Other inter-rev and design-history quotes

**Source note:** The above five sections were populated from quotes pre-identified in Phase 31 CONTEXT.md §canonical_refs and RESEARCH.md Finding #8. The raw ODT (`fs_an_notes.odt`) and Discord CSV (`discord-chat-full.csv`) were moved to this directory by Plan 01 but were not accessible during Plan 02 execution in the parallel worktree. The quotes in §1-§5 are verbatim as recorded by the researcher from the source documents.

The key design chronology as distilled from the pre-identified quotes:

- **2024-10-07** — R41/A3 voltage-divider scheme introduced (Anders), JP3-mod renamed to JP4 (henols)
- **2025-04-28** — Rev 2.2 R41 value confirmed as 10k (Anders)
- **2026-05-22** — Branches-on-GitHub + gerbers-as-source-of-truth statements (Anders, ODT 1:1 with henols)
- **2026-07-03** — Rev 2.1 introduced the scheme; Rev 2.2 and Rev 2.3 unchanged (silkscreen-only for 2.3) (Anders)

---

*Phase: 31-upstream-shield-archaeology*
*Curated: 2026-05-22*
