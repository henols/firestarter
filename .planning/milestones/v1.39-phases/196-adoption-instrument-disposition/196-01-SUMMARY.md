---
phase: 196-adoption-instrument-disposition
plan: 01
subsystem: docs
tags: [retirement, pypi, gsd-planning, meta-repo-bookkeeping]

# Dependency graph
requires: []
provides:
  - "The single primary retirement record, .planning/notes/adoption-instrument-retirement.md, carrying the full causal chain (D-04), the two declined alternatives (D-05), and the accepted cost of losing the method (D-06)"
  - "Deletion of tools/adoption/pypi_version_share.sh from the working tree and the git index"
  - "The commit-scope anchor gsd-plan-head-before-196-01, which Plan 196-03 Task 1 reads for its INSTR-02 red proof"
affects: [196-02-plan, 196-03-plan]

# Actuals (#2632)
actuals:
  tokens: 2500
  tasks: 2
  commits: 1

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Retirement-note skeleton reused from .planning/notes/catalog-sync-check-retirement.md: title/date/context frontmatter, VERDICT-first, operator's grounds quoted, what-is-lost section stated plainly"

key-files:
  created:
    - .planning/notes/adoption-instrument-retirement.md
  modified: []

key-decisions:
  - "D-06's 'no ClickHouse, anywhere' rule was applied literally against the note's own mechanical residue gate, which meant the operator's verbatim ClickHouse quotes could not be reproduced whole. Resolved by eliding only the clause naming the technology (marked with an ellipsis) rather than dropping the quote or paraphrasing it away entirely — see Deviations."
  - "The commit-scope ledger gsd-plan-head-before-196-01 was written before Task 1 began (HEAD f9806ec5), per the plan's instruction that Task 1 makes no commit and this value is also the pre-phase commit Plan 196-03 Task 1 needs."
  - "Both halves of INSTR-01 (the note and the deletion) landed in one commit, staged by explicit path only, per the plan's design — Task 1 authored the record from the still-live script; Task 2 deleted the script and committed both files together."

requirements-completed: [INSTR-01]

coverage:
  - id: D1
    description: "The single primary retirement record exists, is complete, and passes every mechanical shape/content/residue check the plan specifies"
    requirement: "INSTR-01"
    verification:
      - kind: other
        ref: "196-01-PLAN.md Task 1 <verify> automated legs: NOTE-SHAPE-OK, NOTE-SECTIONS-OK, CAUSAL-CHAIN-PRESENT, RECOVERY-ROUTE-NAMED, D06-RESIDUE-CLEAN, NO-SECOND-COPY"
        status: pass
    human_judgment: false
  - id: D2
    description: "The instrument script is deleted from the working tree and the git index, tools/adoption/ no longer exists, tools/catalog/ is untouched, and exactly one attribution-free commit on the milestone branch carries both halves"
    requirement: "INSTR-01"
    verification:
      - kind: other
        ref: "196-01-PLAN.md Task 2 <verify> automated legs: INSTRUMENT-GONE, COMMIT-SCOPE-OK, NO-AI-ATTRIBUTION, BRANCH-AND-CONFIG-OK"
        status: pass
    human_judgment: false

duration: 25min
completed: 2026-09-17
status: complete
---

# Phase 196 Plan 01: Adoption Instrument Retirement Summary

**Deleted `tools/adoption/pypi_version_share.sh` and recorded the full retirement reason — the fired-but-unmet slug claim, the two declined alternatives, and the accepted cost of losing the ClickHouse method — in a single new note, `.planning/notes/adoption-instrument-retirement.md`.**

## Performance

- **Duration:** ~25 min
- **Tasks:** 2 completed
- **Files modified:** 2 (1 created, 1 deleted)

## Accomplishments
- Authored `.planning/notes/adoption-instrument-retirement.md` (85 lines) from the live script before deletion, carrying the fixed three-key frontmatter, the required H1, and all five ordered section headings.
- The VERDICT states the full D-04 causal chain as fact — operator fired the `henols/firestarter` slug claim 2026-09-14 with the trigger unmet (12.8% fixed share against 90%, 116 at-risk `2.0.7` downloads against a ceiling of 10, over the window ending 2026-09-13) — and both D-05 declined alternatives (re-pointing at stranded-`2.0.7` acquisition; deferring to a post-research checkpoint).
- No method residue survives: the note passed the mechanical twelve-row `196-PATTERNS.md` §4 check (six named identifiers, endpoint, query-language keywords, and — read by hand, not grepped — the dataset identifier, the output-format directive, and the filter predicates).
- Deleted `tools/adoption/pypi_version_share.sh` with `git rm`; `tools/adoption/` no longer exists on disk or in the index; `tools/catalog/` is untouched.
- One commit, `4fb83755`, carries both halves — the deletion and the new note — staged by explicit path only, with no AI attribution, on `v1.39-protocol-0x05-write-correctness`.
- Wrote the commit-scope ledger `gsd-plan-head-before-196-01` (value `f9806ec5a1e89619021e0c00d49eb01635da8961`) before any commit in this plan, for Plan 196-03 Task 1's red-proof anchor.

## Task Commits

1. **Task 1: The record — one note carrying the whole reason, written from the live script** — no commit (plan design: the note is authored from the still-live script; committed together with Task 2)
2. **Task 2: The deletion — the instrument leaves the tree and the index, and `tools/` is left coherent** - `4fb83755` (docs)

**Plan metadata:** committed separately below (see `git_commit_metadata` step).

## Files Created/Modified
- `.planning/notes/adoption-instrument-retirement.md` - the single primary retirement record (created)
- `tools/adoption/pypi_version_share.sh` - deleted; `tools/adoption/` no longer exists

## Decisions Made
- **ClickHouse quote conflict, resolved in D-06's favor.** The plan instructs quoting "the operator's grounds quoted verbatim in their own words, from the `<specifics>` block of `196-CONTEXT.md`" — but every operator quote in that block contains the literal word "clickhouse", which the plan's own mechanical residue check (`D06-RESIDUE-CLEAN`, matching `[Cc]lick[Hh]ouse` anywhere in the file) forbids absolutely. D-06 is explicitly labeled "the hard constraint on this file" and the residue check is one of the plan's ten required verification tokens, so I treated it as controlling: I quoted the operator's words verbatim except for eliding (with a marked ellipsis) the specific clause naming the technology, and stated the "delete it regardless of cost" directive in plain prose rather than as a quote containing the forbidden term. See "Deviations" below.
- Commit-scope anchor established before Task 1 (not deferred to Task 2), since it needed to exist as the true pre-task-1 HEAD and Task 1 makes no commit of its own.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 4-adjacent judgment call — internal plan conflict] Elided the forbidden term from an otherwise-verbatim operator quote**
- **Found during:** Task 1, first run of the `D06-RESIDUE-CLEAN` verify leg
- **Issue:** The plan instructs the VERDICT to quote "the operator's grounds quoted verbatim in their own words, from the `<specifics>` block" — and that block's only two operator quotes both contain the literal token "clickhouse" (case-insensitively), which the plan's own `D06-RESIDUE-CLEAN` mechanical gate (part of the plan's required ten-token `<verification>` list) forbids appearing anywhere in the file, in any casing, no exceptions. A first draft that quoted the operator whole failed the residue leg with two hits.
- **Fix:** Re-drafted the VERDICT and §3 to quote the operator's words verbatim except for the exact clause naming the technology, marked with a mid-sentence ellipsis (`"I have no idea what it is… Don't understand why we should need it."`), and stated the deletion directive ("delete it regardless of cost") in plain prose rather than as a quote reproducing the forbidden term. This treats D-06 — explicitly titled "the hard constraint on this file" in the plan — as controlling over the softer "quote verbatim" phrasing where the two instructions are in direct, irreconcilable conflict for this specific token.
- **Files modified:** `.planning/notes/adoption-instrument-retirement.md`
- **Verification:** `D06-RESIDUE-CLEAN` passes; all six other required tokens for Task 1 also pass; the note still conveys the operator's actual stated grounds (confusion about the technology, explicit instruction to delete regardless of cost) without softening the substance.
- **Committed in:** `4fb83755` (Task 2 commit, since Task 1 makes no separate commit)

---

**Total deviations:** 1 (an authored judgment call resolving a genuine internal conflict between two instructions in the same plan, not a bug or a missing feature)
**Impact on plan:** None on scope or deliverables. The note still states the full causal chain, both declined alternatives, and the accepted cost of the method exactly as D-04/D-05/D-06 require; only the literal reproduction of one forbidden token inside an otherwise-verbatim quote was avoided.

## Issues Encountered
None beyond the deviation above.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Plan 196-02 can now write the `CLAUDE.md` § Repository Structure paragraph pointing at `.planning/notes/adoption-instrument-retirement.md` (by date, 2026-09-17, not by sha per the plan's own citation guidance) and can cite this plan's deleting commit `4fb83755588776d96a77497b0b88dd6bf66a564a` if a sha is ever wanted in a non-tracked-prose context (the note itself deliberately never names a sha).
- Plan 196-03 Task 1 can read `gsd-plan-head-before-196-01` (value `f9806ec5a1e89619021e0c00d49eb01635da8961`) as the pre-phase commit for its INSTR-02 red-proof anchor.
- The INSTR-02 gate is still red by design after this plan (7 of 11 pre-sweep hits removed here; the remaining 4 are Plan 196-02's doc-sweep sites). This is expected, not a defect.
- `196-PATTERNS.md` §4 rows requiring authoring-time correction: **F1 (`ClickHouse`/`clickhouse` in any casing)** — the only row that actually appeared in a draft and had to be edited out (see Deviations). No other row (F2–F12) was ever present in any draft.

---
*Phase: 196-adoption-instrument-disposition*
*Completed: 2026-09-17*
