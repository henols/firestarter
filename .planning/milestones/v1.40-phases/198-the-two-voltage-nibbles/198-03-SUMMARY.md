---
phase: 198-the-two-voltage-nibbles
plan: 03
subsystem: database
tags: [chip-database, vcc, vdd, vpp, decode-provenance, disposition-record, backlog, todo-close]

requires:
  - phase: 198-the-two-voltage-nibbles
    provides: "198-01's completed VPP_MV table and 198-02's completed VCC_VOLTAGES table plus the twelve UNSOURCED 0x06 carve-out entries, both folded into this plan's § 9 general finding"
provides:
  - "DECODE-NOTES.md § 9 completed with the D-15 general finding: the voltage word's two nibbles and the VPP byte select a programmer rail index, not a chip requirement"
  - "198-VOLT03-DISPOSITION.md — every one of the 28 vcc_mv==5500 rows disposed with a reason, and the in-repo Phase-148-vs-pending-todo contradiction resolved in favor of the measurement"
  - "The vcc-5500-high-margin-verify-rail-group todo closed by pure rename (R100)"
  - "198-BACKLOG-DRAFT.md — the successor backlog entry (999.73) for the orchestrator to apply to ROADMAP.md"
affects: [199, 200, "any future phase touching VCC_VOLTAGES[0x04], VPP_MV, or the 28-row vcc_mv==5500 group"]

actuals:
  tokens: 21000
  tasks: 3
  commits: 5

tech-stack:
  added: []
  patterns:
    - "Section restructuring on completion: a decode-notes section opened across multiple plans is reordered into its template's slot order on the completing plan, rather than left in arrival order."
    - "A relational predicate (vdd < vcc) re-derived independently against the pinned upstream XML with a standalone script, rather than trusted from a prior plan's SUMMARY, as a cross-check before it becomes a disposition record's reproducible method."

key-files:
  created:
    - .planning/phases/198-the-two-voltage-nibbles/198-VOLT03-DISPOSITION.md
    - .planning/phases/198-the-two-voltage-nibbles/198-BACKLOG-DRAFT.md
    - .planning/todos/completed/vcc-5500-high-margin-verify-rail-group.md (by rename)
  modified:
    - firestarter_app/tools/DECODE-NOTES.md
  removed:
    - .planning/todos/pending/vcc-5500-high-margin-verify-rail-group.md (by rename)

key-decisions:
  - "D-15 applied: § 9 restructured into § 8's slot order (verdict, what-the-code-does-today, positive confirmation, falsification, arithmetic argument, edge case, limits, sources) rather than left in the 198-01/198-02 arrival order."
  - "D-15 correction applied: § 9 cites database.c lines 125-126, not the 123 the phase context carried."
  - "D-13 applied: sub-group 1's 15 non-28LV64A rows disposed as 5V-by-part-number-convention (inference, not datasheet reading); 28LV64A left unresolved either way per D-11, since its vcc_mv stays implausible regardless of which way vdd_mv reads."
  - "D-13 applied: the pending todo's 'genuinely 3.3V' premise is sided against, in favor of Phase 148's own discussion log, threat model and shipped build_db.py comment, all three calling the same 16 rows genuinely 5V."
  - "D-14 applied: 148-DB-DIFF.md's 'already records' claim about sub-group 2 is falsified in DECODE-NOTES.md § 9 and in 198-VOLT03-DISPOSITION.md, by pointing at the archived text -- the archived file itself is not edited."
  - "D-12 applied: the todo closed by pure git mv (R100, 0 insertions/deletions, verified via git diff --stat rather than the commit summary), and the successor backlog entry drafted to a phase-directory file rather than written directly to ROADMAP.md."

requirements-completed: [VOLT-01, VOLT-03]

coverage:
  - id: D1
    description: "DECODE-NOTES.md § 9 carries exactly one heading, a 155-line body opening with the verdict before any evidence, the corrected database.c#L125-L126 citation, the 5.75-6.25V arithmetic argument, both dead VPP indices (0xF1/0xF2), the D-03 surviving-fallback note, the documented D-06 predicate, and all four named limits (n=3 Fujitsu-only, the 167 unreached vdd-0x4 rows Phase 200 owns, no per-row correctness claim, and the non-upstream-attested low-nibble reading) -- ending with its own sources paragraph."
    requirement: "VOLT-01"
    verification:
      - kind: command
        ref: "python -c SECTION9_OK / LIMITS_OK assertions (§9 shape and mandatory-limit tokens)"
        status: pass
      - kind: command
        ref: "git diff --quiet -- tools/build_db.py firestarter/data/chip_database.json (NO_CODE_DRIFT)"
        status: pass
    human_judgment: false
  - id: D2
    description: "198-VOLT03-DISPOSITION.md enumerates all 16 sub-group-1 and all 12 sub-group-2 rows with no elision (32 table lines), reproduces the vdd<vcc predicate independently against the pinned infoic.xml (28/373/366 over 767 filtered rows, matching D-06 exactly), and states the honesty limit that no Microchip or AMD datasheet is vendored in this repository."
    requirement: "VOLT-03"
    verification:
      - kind: command
        ref: "python -c SECTIONS_OK / ROWS_OK / TABLE_LINES / LIMIT_OK assertions"
        status: pass
      - kind: command
        ref: "standalone re-derivation script against infoic_pinned.xml (sha256 cdd21319...), independently confirming 767/28/373/366 and the exact 16+12 row split"
        status: pass
    human_judgment: false
  - id: D3
    description: "The todo is closed by a verified pure rename (R100, 0/0 diff, unedited resolves_phase: 198 frontmatter), 198-BACKLOG-DRAFT.md holds exactly one backlog heading (999.73) with the required residue tokens, and ROADMAP.md/the archived 148-DB-DIFF.md/milestones directory are all confirmed byte-unchanged."
    requirement: "VOLT-03"
    verification:
      - kind: command
        ref: "python -c TODO_OK / DRAFT_OK assertions; git diff --stat; git show --stat HEAD"
        status: pass
      - kind: command
        ref: "git diff --quiet HEAD -- .planning/ROADMAP.md; git status --porcelain -- .planning/milestones/"
        status: pass
    human_judgment: false

duration: ~35min
completed: 2026-09-18
status: complete
commits: 4
plan_head_before: 7acb22ff3dad257d7d75e7bbc48ec8de52acdc3b
---

# Phase 198 Plan 03: The general voltage-decode finding, the 28-row disposition, and the closed todo Summary

**Completed `DECODE-NOTES.md` § 9 with the general D-15 finding — the voltage word's two nibbles and the VPP byte select a programmer rail index, not a chip requirement — disposed of all 28 `vcc_mv==5500` rows individually against an in-repo contradiction the repository was already carrying, and closed the v1.32 todo that has blocked that group since Phase 148.**

## Performance

- **Duration:** ~35 min
- **Completed:** 2026-09-18
- **Tasks:** 3
- **Files modified:** 4 (3 newly created, 1 renamed, 1 edited)

## Accomplishments

- `firestarter_app/tools/DECODE-NOTES.md` § 9 restructured from the arrival order `198-01` and
  `198-02` left it in into § 8's slot order, opening with the verdict before any evidence, and
  extended with the general D-15 finding, the model-dependence falsification quoting upstream's
  own comment at the corrected `database.c#L125-L126` citation, the 5.75–6.25 V arithmetic
  argument against the model's 5.5/6.5 V rails, the saturation-at-the-maximum pattern (28 rows at
  `0xF0`=18000 mV), the D-16 dead-branch record for `0xF1`/`0xF2`, the D-03 surviving-fallback
  note, the D-06 predicate, and all four named limits. Final body: **155 lines** (§ 8 is 66).
- `.planning/phases/198-the-two-voltage-nibbles/198-VOLT03-DISPOSITION.md` written: all 16
  sub-group-1 and all 12 sub-group-2 rows enumerated with no elision (**32 table lines**), the
  `vdd < vcc` predicate independently re-derived against the pinned `infoic.xml`
  (sha256 `cdd21319...`, confirmed identical to the copy `198-RESEARCH.md` hashed) rather than
  trusted from a prior plan's SUMMARY — **767 total, 28 below / 373 equal / 366 above**, an exact
  partition — and the decisive in-repo contradiction named: the pending todo calls sub-group 1
  *"genuinely-3.3V"*, while Phase 148's own discussion log, its plan's threat model and the shipped
  `build_db.py` comment on the value-keyed rewrite all call the same sixteen rows *"genuinely 5V"*.
  The disposition sides with the measurement.
- `28LV64A` is left disposed exactly like its fifteen siblings — unchanged — because its own
  `vcc_mv: 5500` stays implausible under either reading of `vdd_mv`, and D-11 forbids resolving a
  row on an unproven assumption in either direction.
- The archived `148-DB-DIFF.md` § "Non-claim" statement that sub-group 2's `vdd_mv` *"already
  records"* 5.0 V is falsified — that 5000 was always the unmapped-index fallback, never a decode —
  and the falsification is recorded in `DECODE-NOTES.md` § 9 and in the disposition record, by
  pointing at the archived text's path and section. The archived file itself is untouched.
- The pending todo `vcc-5500-high-margin-verify-rail-group.md` closed by a verified pure `git mv`
  (**R100, 0 insertions / 0 deletions**), with its `resolves_phase: 198` frontmatter unedited.
- `198-BACKLOG-DRAFT.md` written: the successor backlog entry, numbered `999.73` (the next free
  number after the roadmap's current highest, `999.72`), carrying the 28-row / 12-row residue and
  the no-vendored-Microchip/AMD-datasheet limit forward. Not written to `ROADMAP.md` — that file
  is confirmed byte-unchanged with no uncommitted modification, for the orchestrator to apply.

## Task Commits

Each task was committed atomically, on `v1.40-program-parameter-fidelity` in both repositories:

1. **Task 1: DECODE-NOTES § 9 — the finding, and the four things it does not claim** —
   `firestarter_app@f155364` (docs) / meta `2edf63aa` (gitlink advance)
2. **Task 2: The 28-row disposition, and the contradiction already in the repository** —
   meta `91f365b0` (docs, no `firestarter_app` commit — this task touches only `.planning/`)
3. **Task 3: Close the todo, draft its successor, and write nothing to the roadmap** —
   meta `b6b60058` (the backlog draft) and meta `62be43f2` (the todo rename), as two separate
   commits per the hazard note (commit the content edit before the `git mv`)

**Plan metadata:** this SUMMARY's own commit (below).

_No STATE.md/ROADMAP.md commit — the orchestrator owns those writes for this phase per the
execution brief. This plan additionally does not write `ROADMAP.md` at all — see
`198-BACKLOG-DRAFT.md`._

## Files Created/Modified

- `firestarter_app/tools/DECODE-NOTES.md` — § 9 fully restructured and completed (149 insertions,
  75 deletions against the pre-plan text; net body length 155 lines).
- `.planning/phases/198-the-two-voltage-nibbles/198-VOLT03-DISPOSITION.md` — new, 207 lines, the
  per-row disposition record.
- `.planning/phases/198-the-two-voltage-nibbles/198-BACKLOG-DRAFT.md` — new, 41 lines, the
  successor backlog entry draft for the orchestrator.
- `.planning/todos/completed/vcc-5500-high-margin-verify-rail-group.md` — moved from
  `.planning/todos/pending/`, byte-identical (R100).

## Decisions Made

- **D-15** applied: § 9's heading and body restructured into § 8's slot order; the general finding
  stated as the opening verdict, before any evidence.
- **D-15 correction** applied: § 9 cites `database.c#L125-L126`, not the `123` the phase context
  carried — verified against the pinned sha this session (line 123 is a different line of the same
  four-line comment block).
- **D-16** applied: the `0xF1`/`0xF2` dead-branch record — no filtered row carries either index,
  proof is byte-identical regeneration (already proved in `198-01`), and no test can cover them
  until upstream ships such a row.
- **D-03** applied: the surviving silent `.get(idx, default)` fallback named explicitly, since
  nothing mechanical reports it.
- **D-06** applied: the `vdd < vcc` predicate stated with its exact 767-row partition, and
  independently re-derived (not merely cited from `198-02`'s SUMMARY) against the pinned
  `infoic.xml` as a cross-check before it became the disposition record's reproducible method.
- **D-13** applied: sub-group 1 classified by part-number-class inference (against `vdd`
  substitution for 15 of 16 rows); `28LV64A` left internally odd and unresolved, per its distinct
  `0x1401` voltage word and its own implausible `vcc_mv` either way. The todo's premise is sided
  against, in favor of three independent Phase-148-era citations (discussion log, threat model,
  shipped source comment) all calling the same sixteen rows genuinely 5 V.
- **D-14** applied: `148-DB-DIFF.md`'s `"already records"` claim about sub-group 2 falsified in
  two places (this plan's own artifacts), the archived file itself untouched — verified with a
  porcelain check on `.planning/milestones/` after every artifact-writing task.
- **D-11** applied: all 28 rows ship unchanged; no `support_status` change, no clamp, no
  substitution — verified by confirming `firestarter/data/chip_database.json` byte-unchanged
  throughout this plan.
- **D-12** applied: the todo closed by pure rename with no frontmatter edit; the successor entry
  drafted to a phase-directory file rather than written directly to `ROADMAP.md`.

## Deviations from Plan

None of Rule 1-4 category. No auto-fixes, no architectural decisions, no blockers encountered.

**Total deviations:** 0.
**Impact:** None — the plan executed as written, including its explicit instruction to leave the
VOLT-03 flagged assumption unresolved (see "Issues Encountered" below).

## Measured Values (per plan `<output>` spec)

- **§ 9's final body line count:** 155 (measured via `len(t.split('## 9.')[1].splitlines())`
  after Task 1 landed; § 8 for comparison is 66 lines).
- **Disposition record's table-line count:** 32 (16 sub-group-1 rows + header/separator, plus 12
  sub-group-2 rows + header/separator: `2 + 16 = 18` and `2 + 12 = 14`, `18 + 14 = 32`).
- **Backlog phase number chosen:** `999.73` — the roadmap's highest existing backlog heading is
  `999.72` (`grep -c '^### Phase 999\.' ROADMAP.md` returns 68 total headings today; the highest
  numbered one is `999.72`), so `999.73` is the next free number.
- **Todo close rename similarity:** `R100`, confirmed via `git diff --stat --cached` immediately
  after `git mv` and before committing — `0 insertions(+), 0 deletions(-)` — and independently via
  `git log --diff-filter=R --name-status` after the commit landed.
- **The three verification legs the orchestrator should re-run after applying
  `198-BACKLOG-DRAFT.md`'s entry to `ROADMAP.md`** (per the plan's explicit instruction, since the
  executor does not write that file):
  1. The entry (heading text `### Phase 999.73: The 28-row \`vcc_mv == 5500\` group still reports
     the wrong operating voltage for 16 of its rows`) is present in the applied `ROADMAP.md`.
  2. The count of `### Phase 999.` headings in `ROADMAP.md` rose by exactly one (from 68 to 69),
     with none of the prior 68 lost.
  3. Every required token from `198-BACKLOG-DRAFT.md`'s block — `BACKLOG`, `Phase 998`-style
     "filed 2026-09-18 during v1.40 Phase 198" wording, `28`, `12`, `Microchip`, `close` — is found
     in the applied text at the new heading's location.

## Issues Encountered

**VOLT-03's flagged assumption stays unresolved, by instruction — not an issue, a deliberate
outcome.** The deterministic edge probe run during context-gathering returned `unclassified —
review manually` for VOLT-03. It was reviewed manually rather than auto-resolved with a backstop:
the requirement's own text makes leaving the 28 rows unchanged an acceptable outcome, so there is
no boundary, ordering, precision or emptiness condition to bound — the risk this requirement
carries is evidentiary (does the disposition's reasoning hold up), not computational (does some
predicate evaluate correctly). It is discharged by `198-VOLT03-DISPOSITION.md`'s per-row
disposition and its named honesty limit — not one of the 16 sub-group-1 rows has a vendored
datasheet, so every disposition for that class is a part-class inference plus an in-repo
measurement, never a datasheet reading — rather than by an acceptance predicate. A verifier
checking this plan's work should abstain to human review on this specific point rather than pass
or fail it on a predicate that was never meant to exist for it.

No other issues.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- `DECODE-NOTES.md` § 9 is now complete and closed — no further plan in this phase extends it.
- `198-VOLT03-DISPOSITION.md` and `198-BACKLOG-DRAFT.md` are both final; the orchestrator applies
  the backlog draft to `ROADMAP.md` using the three verification legs recorded above.
- The todo is closed; nothing further folds into it.
- `198-04` (if still open) inherits: the held gh#66 draft and the consolidated held-pending list
  are unaffected by this plan's work, which was scoped entirely to VOLT-01 and VOLT-03.
- Phase 199 inherits the D-15 general finding as the framing for its own warning wording; Phase
  200 inherits the 167 unreached `vdd`-index-`0x4` rows this plan's § 9 explicitly declines to
  make any claim about.
- `firestarter/data/chip_database.json` is confirmed byte-unchanged throughout this plan — no
  regeneration was run and none was needed, since this plan writes documentation and renames one
  file only.

---
*Phase: 198-the-two-voltage-nibbles*
*Completed: 2026-09-18*

## Self-Check: PASSED

- All created/modified files confirmed present on disk: `firestarter_app/tools/DECODE-NOTES.md`,
  `.planning/phases/198-the-two-voltage-nibbles/198-VOLT03-DISPOSITION.md`,
  `.planning/phases/198-the-two-voltage-nibbles/198-BACKLOG-DRAFT.md`,
  `.planning/todos/completed/vcc-5500-high-margin-verify-rail-group.md`; the pending copy confirmed
  absent.
- All task commit hashes (`firestarter_app@f155364`, meta `2edf63aa`, `91f365b0`, `b6b60058`,
  `62be43f2`) confirmed present in `git log --oneline --all` in their respective repositories.
- Both repositories confirmed on branch `v1.40-program-parameter-fidelity` after every commit.
- `git diff --quiet -- tools/build_db.py firestarter/data/chip_database.json` confirmed no code
  drift in `firestarter_app` after Task 1.
- `git status --porcelain -- .planning/milestones/` confirmed empty after every task — nothing
  under the archived milestones directory was touched.
- `git diff --quiet HEAD -- .planning/ROADMAP.md` confirmed byte-unchanged after Task 3.
- All nine plan-level `<verification>` legs re-run in this session and confirmed passing (see
  "Measured Values" above and the per-task verify legs run during execution).
