---
id: write-modifications-md-rework-trace
title: Write full MODIFICATIONS.md rework trace for operator's Modified Rev 0 (Phase 31 follow-up #4)
captured: 2026-05-26
status: deferred
type: documentation
target_milestone: none (deferred 2026-08-29 by operator direction)
priority: MEDIUM
related_phase: 31
resolves_phase_followups: [Phase 31 follow-up #4]
deferred_from: Phase 35 (per Phase 35 CONTEXT.md D-07)
resolves_phase: 164
depends_on: photograph-modified-rev-0
---

# Write full MODIFICATIONS.md rework trace for operator's Modified Rev 0 (Phase 31 follow-up #4)

## ⏸ DEFERRED 2026-08-29 by operator direction — do not plan this

Operator directed on 2026-08-29 to **skip Rev 0 and defer it**. This todo is parked with **no target
milestone**. It is split out of backlog **999.42**, which now covers only the six unswept chips and the
two unswept shields; it is **not** a blocker on that item and must not be sized into a resumption of it.

Pick this up only if the operator puts the Modified Rev 0 board on the bench for some other reason.
Nothing downstream depends on it: firmware handles the board correctly today via the broad-bucket
`REVISION_2_0` + EEPROM override fall-through, regardless of how the rework landed.


## ⚠ STATUS UPDATE 2026-08-29 — v1.34 Phase 164 closed UNRUN; now carried as backlog 999.42

`resolves_phase: 164` is retained, but **Phase 164 never ran.** v1.34 closed early and scope-reduced
by operator direction on 2026-08-29; Phase 163 (cell B1) never put the board on the bench, so Phase
164 — which was scheduled to photograph it *while it was already out for B1* — never started either.

**Current home: backlog 999.42** ("Finish the v1.34 sweep — six chips, two shields, and the Rev 0
rework trace"). See `.planning/ROADMAP.md` §Phase 999.42 and `.planning/milestones/v1.34-artifacts/CLOSE-RECORD.md` §2.3.

**The third deferral in this todo's life** (Phase 31 → Phase 35 → post-v1.7 → Phase 164 → 999.42),
and the board is **still never physically inspected**. No photographs of it exist anywhere.
### PARTIALLY ADVANCED at the desk by `0e114fb7` (2026-08-29) — read before restarting

Desk work done with **no board in hand and no photographs**, so the trace itself is still blocked.
What it settled, and what it did not:

- **The schematic reference this todo would have been traced against was WRONG.** Every prior
  citation named blob `d2a7f691` / `UniversalProgrammerRev0b0.zip::W27C512Programmer.kicad_sch`.
  Both halves are wrong: `d2a7f691` is `hardware/W27C512Programmer.kicad_sch` on `origin/rev2.0`, and
  it is a bare `.kicad_sch`, not a member of that zip. **The true Rev 0 schematic is blob `cfe6139f`
  at commit `486f3d1`.**
- **This would have wasted the photo session.** The two differ by 23 components, concentrated exactly
  where a rework trace looks. Rev 0 has JP1 (24-pin ROM VCC), JP2 (≥SST39SF020 & 28C512 need A17),
  JP3 (W27C010/AT27C010 needs p1 VPE/VPP) and global label A18. `rev2.0` instead has JP4/JP5, R41=4k7
  at A3, Q9–Q12, RN2-5/7-8 at 10k not 4k7, and drops RN1/RN9. A tracer working from `d2a7f691` would
  hunt the board for JP4/JP5 **that are not on it** and never inspect JP1/JP2/JP3 **that are** — and
  JP2 is the A17 strap, directly relevant to the Bug A upper-address jitter.
- **`.planning/milestones/v1.7-artifacts/MODIFICATIONS.md` is no longer the stub this todo was written against.** It now
  carries the reference correction with the full delta table, a corrected identity table including
  the Rev 2.2 10 kΩ ADC collision, an empty-but-structured rework inventory ready to be filled from
  photographs, and a seven-item inspection priority list derived from the Rev 0 netlist.
- **The ten `TBD pending Phase 35` sentinel cells in `v1.7-SHIELD-REVS.md` §4/§5 are discharged**
  (10 → 0) via REV0-03's *named-reason* branch — each cell now names the specific artefact that is
  missing (a photograph, a continuity probe, a DMM reading) instead of saying "pending". Two resolved
  to real attested values (the 10 kΩ A3 pull-up — an **addition**, since Rev 0 has no A3 divider at
  all), and the §5 "gated" cell resolved to gated on that pull-up's electrical nature.

**What remains for this todo is unchanged and still blocked:** the actual cut-and-jumper trace, which
needs the photographs from `photograph-modified-rev-0.md`. Use `cfe6139f`, **not** `d2a7f691`, and
start from the seven-item inspection priority list rather than from scratch.

## The deferral

Companion to `photograph-modified-rev-0.md` — the rework trace requires the photographs as evidentiary substrate. Both deferred from Phase 31 → Phase 35 → post-v1.7 per Phase 35 D-07. Independence from v1.7 detect-fw substrate confirmed by Phase 35 Wave 3 bench session: firmware correctly handles the Modified Rev 0 board via the broad-bucket `REVISION_2_0` + override fall-through path regardless of rework internals.

Phase 35 bench discovery: the Modified Rev 0 board's A3 net reads in the mid band (220-600) → firmware classifies as `REVISION_2_3`. Implies the rework added an external 10k pull-up on A3. Exact wiring (which trace was cut, which jumper added, what net it connects to) is uninventoried.

## What's needed

Author `.planning/milestones/v1.7-artifacts/MODIFICATIONS.md` (currently a stub created in Phase 31 Plan 05) with:

Per-rework-entry trace against upstream Rev 0 schematic blob `d2a7f691` on `origin/rev2.0`:

For each cut + jumper:
1. **Net affected** (which schematic net was the cut on; which two nets does the jumper bridge)
2. **Schematic-side delta** (compare modified state against the upstream blob — what would have been connected pre-rework vs post-rework)
3. **Capability matrix delta** (does this rework change which chip families / algorithms the board can program? Likely no — the rework is the hardware-bug-A/B fix, not a capability change)
4. **Bench evidence** (the Phase 35 ADC mid-band reading + the `MSG_OK_REV` `Rev 2.0-class, Override HW: Rev 2.3` output is one data point; additional evidence as needed)
5. **Rationale** (what was the original bug being fixed; cite memory `[[user_shield_revisions]]` for "hardware-bug-A/B" context if relevant)

Cross-link from `.planning/milestones/v1.7-SHIELD-REVS.md` Modified Rev 0 rows to the new MODIFICATIONS.md sections.

## Sentinel resolution

Once both todos close, upgrade the following `.planning/milestones/v1.7-SHIELD-REVS.md` rows from `as-modified — pending Phase 35` to bench-verified state:
- §1 row 4 (`state` flips to `operator-photographed`; `photo_dir` to `.planning/milestones/v1.7-artifacts/photos/rev-0-modified/`)
- §4 row 8 (Rev 2.2 → Modified Rev 0 electrical delta — fill with per-cut/per-jumper specifics)
- §5 row 7 (mechanical delta)
- §6 row 91 (capability matrix Modified Rev 0 row — should match parent Rev 0 capability set if rework is the hardware-bug-A/B fix without capability changes)
- §7 row 16+17 (R41 + JP4 alias rows — Modified Rev 0 column)

Bench-evidence-35.md analysis is the seed for the rework-trace narrative.

## When to triage

**AFTER** `photograph-modified-rev-0.md` resolves. Sequence:
1. Schedule operator photo session (or fold into next bench-touch milestone)
2. Operator captures the 5+ photos to `.planning/milestones/v1.7-artifacts/photos/rev-0-modified/`
3. Author working through the photos + upstream schematic blob + Phase 35 bench evidence → write MODIFICATIONS.md
4. Update SHIELD-REVS.md sentinel rows
5. Close both todos atomically

## Cross-references

- Phase 35 CONTEXT D-07 — deferral rationale
- Phase 31 Plan 05 — original MODIFICATIONS.md stub creation
- Phase 35 bench evidence: `.planning/milestones/v1.7-artifacts/bench-evidence-35.md` §"Modified Rev 0 Board" — 10k pull-up inference seed
- Upstream Rev 0 schematic blob `d2a7f691` on `origin/rev2.0` in `firestarter` sub-repo's upstream clone (`.planning/milestones/v1.7-artifacts/upstream-rurp/`)
- Companion (predecessor) todo: `photograph-modified-rev-0.md` (Phase 31 follow-up #3)
- Memory `[[user_shield_revisions]]` — "hardware-bug-A/B" rework context
