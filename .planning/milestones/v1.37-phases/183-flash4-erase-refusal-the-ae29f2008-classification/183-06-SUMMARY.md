---
phase: 183-flash4-erase-refusal-the-ae29f2008-classification
plan: 06
subsystem: docs
tags: [requirements-traceability, roadmap-amendment, record-close-out]

# Dependency graph
requires:
  - phase: 183-01
    provides: "SAFE-07's measured M1/M2/M3 pricing table and the M3 decision on D-02 grounds"
  - phase: 183-02
    provides: "SAFE-09's equivalence-based classification verdict"
  - phase: 183-03
    provides: "The shipped flash4_erase_gate.py and its refusal_text shape, which the amended SAFE-06 text and ROADMAP criterion 1 now quote"
  - phase: 183-04
    provides: "SAFE-08's four-site deletion and the native case count moving 184 to 185"
  - phase: 183-05
    provides: "The measured post-deletion flash shrink and the observed default-mode/merge05-mode gate divergence"
provides:
  - "SAFE-06 amended to D-07's wording in .planning/REQUIREMENTS.md, with an inline amendment note naming D-07/D-08 and pointing to Phase 187's REPLY-03 (D-09)"
  - "Phase 183's Goal and success criterion 1 amended in .planning/ROADMAP.md to match the one-line refusal the operator chose"
  - "Phase 185's Depends on line amended to name Phase 183 and both size_baseline.json inputs (flash shrink, native case count 184->185)"
  - "SAFE-06, SAFE-07, SAFE-08 and SAFE-09 marked complete in .planning/REQUIREMENTS.md, each with a Trace: pointer"
  - "The phase's four adjudications (SAFE-07's mechanism choice, SAFE-08's deletion and disposition (a), SAFE-09's verdict, D-13's unreachability statement) consolidated in this SUMMARY"
affects: [185, 187]

actuals:
  tokens: 3200
  tasks: 3
  commits: 3
  plan_head_before: c6afe81541dc1048309755ad71494110053a29c4

tech-stack:
  added: []
  patterns:
    - "Amendment-note-inline pattern: SAFE-06's superseded clause is replaced (not deleted-and-silent), with a trailing note naming the deciding decision IDs, the operator's knowing choice, and the pointer to where the moved content now lives — same register SAFE-01 through SAFE-04 already established in this file"
    - "Depends-on-line verification constraint: a grep-based verify block that matches only the physical line containing the literal string 'Depends on' requires the cited evidence (phase numbers) to appear on that same physical line, not merely somewhere in the surrounding paragraph"

key-files:
  created: []
  modified:
    - ".planning/REQUIREMENTS.md"
    - ".planning/ROADMAP.md"

key-decisions:
  - "SAFE-06's amended text avoids restating the exact superseded phrase 'self-erases per page during the write' (the Task 1 verify block asserts its ABSENCE file-wide), instead pointing to REPLY-03 as the destination of the cause and the alternative without re-deriving the cause in requirements prose"
  - "Phase 185's Depends-on line was restructured across two edit attempts: the plan's own verify block scans only the single physical line containing the literal string 'Depends on', not the full paragraph, so the phase-number digits (184, 185) had to be moved onto that exact line rather than a later line in the same paragraph — a mechanical constraint discovered while iterating, not a deviation from the plan's intent"
  - "Traceability table rows for SAFE-06 through SAFE-09 were updated from 'Pending' to 'Complete' alongside the checkbox flips, matching the register SAFE-01 through SAFE-05 already use in the same table — not explicitly required by the task's acceptance criteria, but keeping the checkbox and the table in the same state avoids a self-contradicting file"

patterns-established:
  - "Record-close-out plans (a phase's final wave-4 plan) run last specifically so every amendment can cite a landed SUMMARY rather than an intention — this plan's own precondition on 183-01 through 183-05 having landed is the mechanism"

requirements-completed: [SAFE-06, SAFE-07, SAFE-08, SAFE-09]

coverage:
  - id: D1
    description: "SAFE-06 amended in REQUIREMENTS.md to name the part and state the cause/alternative are not carried in the CLI, with an inline note pointing to REPLY-03"
    requirement: "SAFE-06"
    verification:
      - kind: other
        ref: "grep -n 'self-erases per page during the write' .planning/REQUIREMENTS.md (exit 1, absent); grep -c 'REPLY-03' .planning/REQUIREMENTS.md (3, non-zero)"
        status: pass
    human_judgment: false
  - id: D2
    description: "Phase 183's Goal and success criterion 1 amended in ROADMAP.md to the one-line, part-naming refusal shape, quoting the shipped refusal_text format"
    requirement: "SAFE-06"
    verification:
      - kind: other
        ref: "grep -n 'says the reason' .planning/ROADMAP.md (exit 1, absent); git diff --numstat -- .planning/ROADMAP.md scoped to Phase 183 section"
        status: pass
    human_judgment: false
  - id: D3
    description: "Phase 185's Depends on line names Phase 183 and both size_baseline.json inputs (flash shrink, native case count 184->185), replacing the 'independent' claim"
    requirement: "SAFE-08"
    verification:
      - kind: other
        ref: "awk range Phase185..Phase186 | grep 'Depends on' | grep -q 'Phase 183' -> DEPENDS_ON_183; same | grep -qE '18[45]' -> BOTH_INPUTS_PRESENT"
        status: pass
    human_judgment: false
  - id: D4
    description: "SAFE-06, SAFE-07, SAFE-08 and SAFE-09 marked [x] complete in REQUIREMENTS.md, each with a Trace: pointer to the landed artifact, after an audit confirmed no checkbox was flipped early by an earlier plan"
    requirement: "SAFE-06, SAFE-07, SAFE-08, SAFE-09"
    verification:
      - kind: other
        ref: "grep -cE '^- \\[x\\] \\*\\*SAFE-0[6-9]\\*\\*' .planning/REQUIREMENTS.md == 4; grep -cE '^- \\[ \\] \\*\\*REPLY-0' .planning/REQUIREMENTS.md == 7 (unchanged)"
        status: pass
    human_judgment: false
  - id: D5
    description: "The phase's four adjudications (SAFE-07 mechanism choice, SAFE-08 deletion + disposition (a), SAFE-09 verdict, D-13 unreachability statement) consolidated in one place in this SUMMARY, readable without reassembling five files"
    verification:
      - kind: other
        ref: "See 'The Phase's Four Adjudications' section below"
        status: pass
    human_judgment: false

duration: 20min
completed: 2026-09-11
status: complete
---

# Phase 183 Plan 06: Record Close-Out — Amending SAFE-06, Phase 183's Goal, and Phase 185's Dependency Summary

**Amended three documents to describe the one-line refusal the operator actually chose (D-07/D-08), gave Phase 185 an explicit dependency on Phase 183 naming both `size_baseline.json` inputs (D-15), and closed SAFE-06 through SAFE-09 with traceability pointers after confirming no earlier plan had flipped a checkbox prematurely.**

## Performance

- **Duration:** ~20 min
- **Started:** 2026-09-11 (session continuation)
- **Completed:** 2026-09-11
- **Tasks:** 3
- **Files modified:** 2 (`.planning/REQUIREMENTS.md`, `.planning/ROADMAP.md`)

## Accomplishments
- `.planning/REQUIREMENTS.md` § SAFE-06 no longer claims the CLI states its cause and its alternative; it now says the refusal names the part, that the cause/alternative are deliberately not carried in the CLI, and points to Phase 187's REPLY-03 (D-09) as where they went — with an inline note naming the operator's knowing choice against the original wording (D-07/D-08).
- `.planning/ROADMAP.md` Phase 183's **Goal** and **success criterion 1** were rewritten to match: the refusal names the part, the reason is answered in REPLY-03 rather than printed, and criterion 1 quotes the shipped `Erase not supported for <EPROM>` line shape instead of the superseded cause/alternative wording.
- Phase 185's **Depends on** line was replaced: it now names Phase 183 explicitly and states both `size_baseline.json` inputs — the measured flash shrink and the native test case count moving 184 to 185 on both `native` and `native_nodevtools` — plus the no-new-MERGE-05-exemption fact from `183-05`'s `--policy merge05` run against BASE-01.
- SAFE-06, SAFE-07, SAFE-08 and SAFE-09 are marked `[x]` complete in `.planning/REQUIREMENTS.md`, each with a `Trace:` pointer to the SUMMARY(s) and artifact(s) that satisfy it, and the Traceability table rows were brought in line (Pending -> Complete). An audit prior to marking found no checkbox had been flipped early by an earlier plan in this phase.

## Task Commits

Each task was committed atomically:

1. **Task 1: Amend SAFE-06 and Phase 183's Goal and criterion 1 to D-07's wording (D-08)** - `90ff59ef` (docs)
2. **Task 2: Make Phase 185 depend on Phase 183, naming both inputs (D-15)** - `ece7c65a` (docs)
3. **Task 3: Close SAFE-06..SAFE-09 with traceability and one consolidated decision record** - `fa708225` (docs)

**Plan metadata:** commit for this SUMMARY.md follows immediately after this file is written.

## Files Created/Modified
- `.planning/REQUIREMENTS.md` - SAFE-06's clause amended and its checkbox flipped to `[x]`; SAFE-07/08/09 checkboxes flipped to `[x]` with `Trace:` pointers added; Traceability table rows for SAFE-06..09 updated to Complete
- `.planning/ROADMAP.md` - Phase 183's Goal and success criterion 1 rewritten; Phase 185's `**Depends on:**` line replaced

## Decisions Made
- Avoided restating the exact superseded phrase `self-erases per page during the write` anywhere in the amended SAFE-06 text, since Task 1's own verify block asserts that phrase's file-wide absence — the amendment points to REPLY-03 rather than re-deriving the cause in requirements prose.
- Restructured Phase 185's `Depends on` paragraph so the phase-number digits (183, 184, 185) sit on the single physical line containing the literal string "Depends on" — the plan's own verify block scans only that one matched line via `grep 'Depends on'`, not the full paragraph, so evidence placed on a later line in the same paragraph would not be seen by the check. This was discovered iteratively while running the verify commands and fixed within Task 2 before committing.
- Updated the Traceability table's SAFE-06..09 rows from Pending to Complete alongside the checkbox flips — not explicitly listed in Task 3's acceptance criteria, but necessary so the same file does not simultaneously say `[x]` and "Pending" for the same requirement, matching the precedent SAFE-01..05 already set in the same table.

## Deviations from Plan

None - plan executed exactly as written. (One mechanical iteration during Task 2, documented above in Decisions Made and in `key-decisions`, was a verify-script-driven correction discovered and fixed within the task's own execution — not a deviation from the plan's action or acceptance criteria, which were satisfied as specified.)

## The Phase's Four Adjudications

Consolidated here per Task 3's instruction, so a later reader does not have to reassemble them from five SUMMARYs.

**1. SAFE-07 — the chosen mechanism.** Three mechanisms were priced (`183-01`): **M1** (new firmware message id + `handle->protocol` compare-and-branch, firmware/post-connect) measured **+12 B flash / +0 B RAM on all three AVR targets** (uno, uno328pb, leonardo) via a reverted throwaway probe; **M2** (host renders better text against the existing `MSG_ERR_NOT_SUPPORTED`, host/post-connect) is a **structural zero** — no file under `firestarter/` is touched; **M3** (host pre-flight policy gate, host/pre-connect) is also a **structural zero**. **M3 was chosen.** The deciding constraint is **D-02**: M1 and M2 both fire *after* `Connecting... OK` — the exact sequence gh#62's reporter read as a malfunction — while M3 fires pre-connect, before that sequence starts. **The flash figures did NOT decide this choice** — no target showed a flash cliff; leonardo (the tightest target, 0 B MERGE-05 band headroom) sat 1808 B below its BASE-01 reference figure even before this plan's own measurement, with 724 B of named exemptions already stacked on top and unused. M1's +12 B would not have been a flash-budget problem on any target measured — it was eliminated by D-02, not by size.

**2. SAFE-08 — the deletion, and the disposition of `flash_5v_page_write_init`.** The unreachable 12V bulk-erase routine was **removed, not kept**, at all four sites (`183-04`): `flash_5v_page_erase_execute`'s definition and forward declaration, `configure_flash_5v_page`'s `CMD_ERASE` arm, and `flash_5v_page_write_init`'s `FLAG_CAN_ERASE` erase-on-write block. The sub-adjudication CONTEXT.md left open — what to do with the now-near-empty `flash_5v_page_write_init` function and its `firestarter_operation_init` assignment — was resolved as **disposition (a): KEPT**. Reason: nulling the init pointer would segfault an unguarded `h.firestarter_operation_init(&h)` call already present in `test_val_5v_page.cpp`, and `configure_sram` is the in-tree precedent for a body that is effectively a no-op past its own guard check — deleting the function and its assignment was not required for correctness and would have introduced a new crash risk in the test harness this same plan repaired.

**3. SAFE-09 — the classification verdict.** AE29F2008's `algorithm 5` classification is **CORRECT**, established via an equivalence chain (upstream `infoic.xml` transcription, shared `chip_id` with W29C020C, independent datasheet confirmation) rather than a direct AE29F2008 datasheet reading (`183-02`, `.planning/notes/ae29f2008-classification-verdict.md`). Simultaneously, **the gh#62 reporter is ALSO correct**: the `0x05` firmware path genuinely does not implement the chip-erase this silicon supports — a real capability gap, not a database defect. D-21's misclassification-override machinery (a `build_db.py` rule + regeneration) was held ready and **deliberately not invoked** — `chip_database.json` is byte-unchanged.

**4. D-13 — the precise unreachability statement.** Stated in its required form, not paraphrased: the `CMD_ERASE` arm's **ASSIGNMENT** ran on every flash4 INIT, via `configure_memory` (which executes at `firestarter.cpp:91` during INIT). It is the **FUNCTION POINTER** that arm installed that was **never invoked**, because `eprom_erase` returns at the `FLAG_CAN_ERASE` check (`firestarter.cpp:273`) before `op_execute_simple_operation` is ever reached. This is never to be stated as "the arm never runs" — the assignment ran every time; only the call through the installed pointer was unreachable.

## Issues Encountered

None. All three tasks' verify blocks passed after the mechanical Depends-on-line iteration documented above (resolved within Task 2's own execution, before commit).

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- All four of Phase 183's requirements (SAFE-06, SAFE-07, SAFE-08, SAFE-09) are now marked complete with traceability, closing the phase's requirement set.
- Phase 185 now has an explicit, evidence-backed dependency on Phase 183, naming both `size_baseline.json` inputs its own CLAIM-04 re-record must pick up.
- Phase 187's REPLY-03 has a clear pointer from SAFE-06 for what it owes gh#62: the cause and the alternative that the shipped CLI deliberately does not print.
- This is the phase's final plan (wave 4). No blockers.

---
*Phase: 183-flash4-erase-refusal-the-ae29f2008-classification*
*Completed: 2026-09-11*

## Self-Check: PASSED

- FOUND: `.planning/phases/183-flash4-erase-refusal-the-ae29f2008-classification/183-06-SUMMARY.md`
- FOUND: commit `90ff59ef` (Task 1)
- FOUND: commit `ece7c65a` (Task 2)
- FOUND: commit `fa708225` (Task 3)
- `git rev-parse --abbrev-ref HEAD` -> `gsd/v1.37-operator-safety-answered-reports-claim-hygiene` (unchanged throughout)
- `git diff .planning/config.json` -> empty (sub_repos not pruned)
- All task-level `<acceptance_criteria>` re-run and passing (see verification commands cited above and in each task's commit)
- Plan-level `<verification>` re-run:
  - `self-erases per page during the write` absent from `.planning/REQUIREMENTS.md`: PASS
  - `says the reason` absent from `.planning/ROADMAP.md`: PASS
  - Phase 185's `**Depends on:**` line names Phase 183 and both inputs: PASS
  - SAFE-06 through SAFE-09 are `[x]` with `Trace:` pointers; no REPLY or CLAIM checkbox moved: PASS
  - Both `.planning/` diffs are scoped, with no bulk deletion from either file: PASS (REQUIREMENTS.md 33/221 lines touched across all three commits; ROADMAP.md touches only the Phase 183 and Phase 185 sections)
