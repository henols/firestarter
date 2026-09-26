---
title: "Fix JP4 labels + Rev-2 revision block in info jumper display"
date: 2026-07-02
priority: medium
resolves_phase: 999.58
---

# Fix JP4 labels + Rev-2 revision block in `info` jumper display

Safe, self-contained display fix. **No chip-database or firmware change** — does
NOT attempt to add the 3rd-position / 2516 support (that's the seed
`rev22-3pin-header-2516-family-support.md`).

## Split history (recorded 2026-09-10, Phase 182 Plan 07)

This todo carried three items and was **split** during Phase 182 (JP5 Destructive-Operation Gate):

- **Item 3 (delete the dead renderer) landed in Phase 182, 2026-09-10, as SAFE-05.** See
  `.planning/phases/182-jp5-destructive-operation-gate/182-04-SUMMARY.md` — `_get_rev2_2_jumper_settings_data`
  and its commented-out call site are deleted (`firestarter_app@2a9a335`). That work is done; item 3 below
  is retained only as a historical record of what Phase 182 resolved.
- **Items 1 and 2 move to the backlogged D-09 work, filed as `.planning/ROADMAP.md` Phase 999.58** (this
  todo's `resolves_phase` is re-pointed there accordingly). That phase does not exist yet — Phase 187
  (Answered Reports) must stay last in the v1.37 milestone, so a phase carrying this scope slots before it,
  which is an operator scope decision rather than a planner's to make. See Phase 999.58 in `ROADMAP.md` for
  the full backlog stub, including the three enlargements Phase 182 discovered to this job.
- **Both items 1 and 2's premises are corrected below**, dated 2026-09-10, with their evidence — the D-09
  work inherits the corrected premise rather than the one this todo originally carried.

## Scope

In [ic_layout.py:169-183](../../../firestarter_app/firestarter/ic_layout.py#L169-L183)
(`_get_rev2_jumper_settings_data`):

1. **Fix JP4's copy-paste labels.** `config_text` and `pin_text` are currently
   `"28pin"` / `"32pin"` (cloned from JP3) and render as meaningless text. JP4 is
   the VPP bypass jumper — its meaningful values are Open / Closed. Give it
   labels that describe VPP-on-pin-1, not pin count.

   **Corrected 2026-09-10 (Phase 182, D-10):** the standard to write to is still JP4's own
   silkscreen parenthetical — *"Only for ROMs with VPP on P1"* — but the clause beside it on the
   same silkscreen, *"Open for 32 pin ROMs, Closed for 28 pin ROMs"*, is **two-state language on a
   three-pole jumper and must NOT be reproduced** in the rewrite. On Rev 2.2 and later the existing
   `"28pin"`/`"32pin"` labels this item targets for removal are not merely meaningless, as originally
   stated — they are **wrong**: JP4 has a third position (the 24-pin pole, added at Rev 2.2) those two
   labels cannot express at all. Evidence: `.planning/phases/182-jp5-destructive-operation-gate/evidence/shield-rev2.2-jp4-jp5-jp6-jp9.jpg`
   (the silkscreen photograph) and `.planning/notes/jumper-display-ground-truth.md`.

2. **Relabel the Rev-2 block** from `"2.0 & 2.1"` to cover all four revs that
   share this JP4 header: `"2.0, 2.1, 2.2 & 2.3"` (WRONG, corrected 2026-09-10 below — original
   premise was: operator confirmed 2.2/2.3 have the same JP4, plus a 3rd angled pin handled
   separately by the seed).

   **Corrected 2026-09-10 (Phase 182, D-10):** this premise is now known wrong in a way that
   matters. Rev 2.2's JP4 is a **three-pole selector**, not the two-pin header Rev 2.0/2.1 carry, and
   the footprint change is at **Rev 2.1 → Rev 2.2** — not Rev 2.2 → Rev 2.3 as this item originally
   assumed. A single block covering revisions 2.0 through 2.3 therefore cannot describe all of them:
   2.0/2.1 share a 2-pin header state (2 values), 2.2/2.3 share a 3-pole state (3 values). Evidence:
   Rev 2.2's own pick-and-place CSV
   (`.planning/milestones/v1.7-artifacts/upstream-rurp/hardware/Rev2.2/W27C512Programmer-top-pos.csv`:
   `"JP4","P1_VPP_JMP","PinHeader_2x02_P2.54mm_Vertical"`) against Rev 2.1's
   (`.planning/milestones/v1.7-artifacts/upstream-rurp/hardware/Rev2.1/W27C512Programmer-top-pos.csv`:
   `"PinHeader_1x02_P2.54mm_Vertical"`), and the JP4 KiCad symbol
   (`.planning/milestones/v1.7-artifacts/upstream-rurp/hardware/RelativelyUniversalROMProgrammer.kicad_sch:22555-22620`,
   `Description "Jumper, 3-pole, both open"`). **The new block structure (how many blocks, which
   revisions in each) is left for the D-09 work (Phase 999.58) to design** — not decided here.

3. **Delete the dead `_get_rev2_2_jumper_settings_data`** method — **DONE 2026-09-10, Phase 182 SAFE-05**
   (`firestarter_app@2a9a335`, guarded by a `hasattr` deletion test and a positive survivor test for the
   live JP4 sibling — see `182-04-SUMMARY.md`). It invented a phantom "JP5" solder-jumper setting as an
   operator-settable Rev 2.2 config header, which does not exist on the hardware; the method and its
   commented-out call site are gone. *(Original citations, now stale since the deletion removed the
   lines: the method was at `ic_layout.py:186-201`, the commented call site at `ic_layout.py:656`. Both
   are rewritten here as this past-tense reference to the removing commit, per this project's citation
   hygiene rule — a citation to deleted lines is not "repaired" forward, it is replaced with the commit
   that removed them.)*

## Acceptance

Items 1 and 2 (still open, D-09 work):

- `firestarter info <a 28-pin UV-EPROM>` prints a JP4 line with sensible
  Open/Closed labels (no "28pin, 32pin"), checkable against JP4's own
  "Only for ROMs with VPP on P1" standard, and not reproducing the two-state
  "Open for 32 pin ROMs, Closed for 28 pin ROMs" clause.
- The Rev-2 jumper block(s) correctly describe 2.0 through 2.3, with the
  2-pin/3-pole split the corrected premise above requires — exact block
  structure is the D-09 work's to design.

Item 3 (done):

- No `_get_rev2_2` / phantom-JP5 references remain — confirmed 2026-09-10 (`182-04-SUMMARY.md`).

Whole file, at close of the D-09 work:

- Existing tests + ruff/format/mypy gate stay green.

## Context

See `notes/info-jumper-display-design-audit.md` for the full audit, and
`.planning/phases/182-jp5-destructive-operation-gate/182-CONTEXT.md` § "Folded Todos" and § D-10…D-15
for the split and correction history recorded above.
