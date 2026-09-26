---
phase: 158-residual-optimizations-cold-baseline-re-record-firmware-only
plan: "07"
subsystem: planning-documents
tags: [requirements-closure, roadmap-closure, meta-repo, hand-authored-docs]
dependency-graph:
  requires: ["158-06"]
  provides: ["158-land-requirements-closed", "158-roadmap-closed"]
  affects: ["159-remap-and-close"]
tech-stack:
  added: []
  patterns: ["scoped Edit replacements only, never a whole-file Write, on hand-authored planning documents"]
key-files:
  created:
    - .planning/phases/158-residual-optimizations-cold-baseline-re-record-firmware-only/158-07-SUMMARY.md
  modified:
    - .planning/ROADMAP.md
    - .planning/REQUIREMENTS.md
decisions:
  - "OD-9 as amended by the orchestrator: ROADMAP.md and REQUIREMENTS.md are never regenerated, but ARE edited by this one closure plan using scoped Edit replacements only -- the same template Phase 157 used at its own landing plan."
  - "Every superseded figure (LAND-03's observed=172, LAND-06's flat +22 B, LAND-07's 57 tokens/7 headroom, LAND-05's +30 B flash) was left in place beside a correction sentence rather than deleted, matching how Phases 155-157 handled their own corrections."
metrics:
  duration: "~35 minutes"
  completed: 2026-08-24
status: complete
---

# Phase 158 Plan 07: Close out LAND-01..08 and scope-correct the stale ROADMAP figures Summary

One-liner: Scoped `Edit`-only closure of `.planning/ROADMAP.md` §Phase 158 and `.planning/REQUIREMENTS.md` §5 — all eight LAND requirements ticked and Complete, three stale figures corrected in place, both diffs provably confined to their own sections.

## What was built

This plan performed no code change and touched no file under `firestarter/` or `firestarter_app/`. It closed the two hand-authored `.planning/` documents this phase supersedes:

**`.planning/REQUIREMENTS.md` §5** — all eight `LAND-0N` bullets ticked (three, LAND-01/02/06, were already ticked by earlier plans but had no discharge sentence; all eight now carry one). Each bullet's original text survives verbatim, with a `**Discharged 2026-08-24 by plan 158-NN against [158-after-figures.md](v1.33/158-after-figures.md) §N.**` sentence appended, followed by the corrections that bear on it in the same `**Correction (C-N):**` shape §2/§3/§4 already use. The eight `LAND-0N` traceability rows moved from `Pending`/plain-`Complete` to `Complete (158-NN[/158-NN], closed 158-07)`, matching the DEAD/DEDUP/DECODE row format exactly.

**`.planning/ROADMAP.md` §Phase 158** — a new `**Measured**` line was inserted between `**Requirements**` and `**Success Criteria**`, in the same sibling position Phases 155 and 157 use, stating the per-target cold-to-cold flash delta (`-138/-138/-136 B`) and RAM saving (`-128 B`), attributed to LAND-05. Each of the eight success criteria got an appended closure naming its discharging plan and the record section carrying the evidence. The plan-checkbox list's seventh entry (`158-07-PLAN.md`) was ticked, completing the seven-of-seven set. A trailing sentence records the `tests/test_checker_convention.py` `FLOOR`/`FIXTURE_FLOOR` carry-forward as closed by plan 158-05 (correction C-10).

**Three figures scope-corrected in place, beside the number they supersede, never replacing it:**
1. LAND-03 / criterion 3 — the observed native case count `172` stands, with correction C-1 naming the re-measured **184** beside it, and C-12's corrected exit-1 mechanism (the AVR comparison runs first and passes; it is the report line that is suppressed, not the comparison).
2. LAND-06 / criterion 6 — the flat mask cost `+22 B` stands, with correction C-3 naming the per-target figures `+22/+24/+22 B` beside it.
3. LAND-07 / criterion 7 — `57 tokens`/`7 tokens of headroom` stand, with correction C-4 naming the three derived bounds (`50/14`, `51/13`, `55/9`) beside them, and C-5 stating the budget-argument, not-impossibility conclusion.

LAND-05's `+30 B flash` prediction (criterion 5) is likewise left in place with correction C-2 naming the measured flash *reduction* beside it, and the ARM outcome stated exactly as the record states it (both sides built, not a ceiling).

## Boundary audit (per task 3's requirement)

Diffing both files against their pre-task-1 snapshots, every changed hunk was confirmed inside its licensed region:

- **ROADMAP.md**: two hunks, at the original lines 411 (Phase 158's `**Requirements**`/`**Success Criteria**` block, original range 409–457) and 451–454 (the plan-checkbox list, same range). Both fall strictly inside §Phase 158; §Phase 159 is checksum-identical to `HEAD~1`.
- **REQUIREMENTS.md**: all changed lines fall inside §5's eight `LAND-0N` bullets or the eight `LAND-0N` traceability rows — confirmed by diffing the post-edit file against the snapshot and filtering out exactly those two line classes, which left zero residual lines.

Cross-file consistency: the 8 ticked `LAND-0N` ids in §5 exactly equal the 8 `Complete` Phase-158 traceability ids; all eight cite `158-after-figures.md`; the ROADMAP carries 7 ticked plan entries and a `158-0N-PLAN.md` file exists on disk for each of `158-01` through `158-07`.

Guard invariants, all confirmed unchanged: ROADMAP `^### Phase ` heading count (100, same before/after), both files' line counts (neither fell), REQUIREMENTS' whole-file `^- \[` bullet count (unchanged), the five `REMAP-0N | Phase 159 | Pending` rows (byte-unchanged), zero `SWEEP`/`DEAD`/`DEDUP`/`DECODE`/`REMAP` bullet or row on any diff line, zero `**Goal**`/`**Depends on**`/`**Requirements**` lines added or removed.

## Deviations from Plan

None — plan executed exactly as written. Both files were edited with scoped `Edit` replacements only; no `Write` and no GSD roadmap/requirements mutation verb touched either file.

## The four residuals handed to Phase 159

1. **Citations.** Every `file:LINE` citation this phase wrote — in both `.planning/v1.33/158-*` records and in the two closures this plan just added to ROADMAP.md/REQUIREMENTS.md — was measured against the tree at the time of writing and is in scope for Phase 159's single composite pre-154 → post-158 remap pass (D-01, D-05). This plan ran no remap and repaired no citation.
2. **The staleness marker.** `.planning/v1.33/CITATIONS-STALE.md` is untouched (confirmed byte-unchanged against `HEAD~1`) and remains close-blocking; REMAP-04 owns its removal.
3. **The gitlinks.** Both gitlinks in the meta repo are still recorded, unmoved by this plan:
   - `firestarter`: meta records `2ad5b322a37ba4a88afd09cc946f5c4114e51483`, actual HEAD `2ccda8d43c8161a34fb5f83b9ab12c37a443bf22` — **drifted**, pre-existing since Phase 154, operator-gated, not re-pinned by this phase (OD-10).
   - `firestarter_app`: meta records `38f0d839a1984fa71cb16ea98afa4d8a4e6bcfe2`, actual HEAD `38f0d839a1984fa71cb16ea98afa4d8a4e6bcfe2` — matches, not drifted.
   - **Operational trap for whoever re-pins:** `git commit -- <path>` **discards** a gitlink `update-index` staged for that path — the commit that re-pins a gitlink must be made **without** a pathspec, or the re-pin silently vanishes.
4. **Phase state.** `.planning/STATE.md` is untouched by every plan of this phase (confirmed byte-unchanged against `HEAD~1`); marking Phase 158 complete belongs to the orchestrator's completion step, not to this plan.

## Commit

- `664801a7` — `docs(158-07): close out LAND-01..08 and scope-correct the stale ROADMAP figures` — lists exactly `.planning/REQUIREMENTS.md` and `.planning/ROADMAP.md`, zero paths beginning `firestarter`.

## Self-Check: PASSED

- `.planning/ROADMAP.md` exists and contains the ticked `158-07-PLAN.md` entry and the `**Measured**` line — FOUND.
- `.planning/REQUIREMENTS.md` exists with all 8 `LAND-0N` bullets ticked and all 8 traceability rows `Complete` — FOUND.
- Commit `664801a7` exists in `git log --oneline` — FOUND.
- `git -C firestarter status --porcelain` empty, `git show --stat --name-only HEAD` lists exactly the two `.planning/` paths — CONFIRMED.
