---
phase: 173-close-beta-cut-under-protection-close-procedure-honesty-ledg
plan: 04
subsystem: docs
tags: [github-api, graphql, upstream-issues, honesty-ledger, wording-review]

requires:
  - phase: 172-policy-one-tracker-protected-main
    provides: "NON-CLAIM 2 (gh#6's two declined items, named); the tracker/policy facts these replies restate"
provides:
  - "173-UPSTREAM-REPLIES.md — the four upstream reply bodies, reviewable, PENDING OPERATOR REVIEW"
  - "evidence/bodies/173-gh5.md, 173-gh6.md, 173-gh7.md, 173-gh9.md — the exact bytes plan 173-07 posts with --body-file"
  - "evidence/173-04-issue-state-before.json — the pre-post state of all four issues plus prom's pinned count"
  - "evidence/173-04-draft-link-check.txt — every URL in every body, mechanically resolved"
affects: [173-07]

actuals:
  tokens: 4381
  tasks: 2
  commits: 2

tech-stack:
  added: []
  patterns:
    - "Drafted-then-reviewed public text: body stored once as a file, embedded verbatim in a reviewable record, so what the operator approves is byte-identical to what --body-file posts later (D-13, v1.22 D-02 precedent)."

key-files:
  created:
    - .planning/phases/173-close-beta-cut-under-protection-close-procedure-honesty-ledg/173-UPSTREAM-REPLIES.md
    - .planning/phases/173-close-beta-cut-under-protection-close-procedure-honesty-ledg/evidence/173-04-issue-state-before.json
    - .planning/phases/173-close-beta-cut-under-protection-close-procedure-honesty-ledg/evidence/173-04-draft-link-check.txt
    - .planning/phases/173-close-beta-cut-under-protection-close-procedure-honesty-ledg/evidence/bodies/173-gh5.md
    - .planning/phases/173-close-beta-cut-under-protection-close-procedure-honesty-ledg/evidence/bodies/173-gh6.md
    - .planning/phases/173-close-beta-cut-under-protection-close-procedure-honesty-ledg/evidence/bodies/173-gh7.md
    - .planning/phases/173-close-beta-cut-under-protection-close-procedure-honesty-ledg/evidence/bodies/173-gh9.md
  modified:
    - .planning/STATE.md

key-decisions:
  - "gh#5's body names FUT-W-01 through FUT-W-05 by ID and states 'deferred, not delivered' rather than describing them only in prose, so the acceptance gate and any future reader can grep the exact tokens."
  - "gh#6's body names both Phase 172 D-11 declines (required status checks, required review-thread resolution) explicitly, per NON-CLAIM 2's own instruction that these must not read as quietly delivered."
  - "gh#9's body states plainly that nothing was declined against it, rather than forcing a 'declined' section where none applies — honest omission over a padded one."
  - "Every URL kept in plain https://github.com/... form (no shortlinks, no markdown-only refs) so the Backlog 999.9 rename sweep this phase's own CONTEXT.md commits to can grep them later."

requirements-completed: [POLICY-04]

coverage:
  - id: D1
    description: "Pre-post state of all four issues (gh#5, gh#6, gh#7, gh#9) captured from the live API — open, zero comments — plus prom's pinned-issue count (0), before any draft was written."
    requirement: POLICY-04
    verification:
      - kind: other
        ref: "Task 1 <verify> — evidence/173-04-issue-state-before.json shape + live re-read of comment counts"
        status: pass
    human_judgment: false
  - id: D2
    description: "Four reply bodies drafted, stored as files under evidence/bodies/, and embedded verbatim inside 173-UPSTREAM-REPLIES.md, satisfying D-12's per-issue disposition and the three universal content requirements (delivered / declined-and-why / surviving tracker)."
    requirement: POLICY-04
    verification:
      - kind: other
        ref: "Task 2 <verify> — verbatim-embedding check, gh#6 decline-string check, gh#5 FUT-W token check, gh#7 date+pointer check, gh#9 stays-open check, Protocol-Flags/Protocol-ID absence check"
        status: pass
    human_judgment: false
  - id: D3
    description: "Every URL across the four bodies mechanically resolved (no 4xx/5xx/000), recorded one status line per URL."
    requirement: POLICY-04
    verification:
      - kind: other
        ref: "Task 2 second <verify> — evidence/173-04-draft-link-check.txt, 3 URLs, all 200"
        status: pass
    human_judgment: false
  - id: D4
    description: "The prose content of each reply reads as accurate, well-scoped, and appropriately worded for a public tracker — this is exactly what D-13's blocking operator review exists to judge, and no automated check substitutes for it."
    human_judgment: true
    rationale: "D-13 requires an explicit operator wording review before anything in this plan's output is posted. The mechanical gates prove structure and factual anchors (required tokens present, links resolve, nothing posted); they cannot judge tone, completeness of nuance, or whether the operator is comfortable with this exact phrasing going out under their name. 173-UPSTREAM-REPLIES.md's review status is left PENDING OPERATOR REVIEW for exactly this reason."

duration: ~15min
completed: 2026-09-02
status: complete
---

# Phase 173 Plan 04: Drafted Upstream Replies Summary

**Four upstream reply bodies for gh#5, gh#6, gh#7 and gh#9 drafted verbatim into a reviewable phase record and separate `--body-file` payloads, with the pre-post issue state and a mechanical link check captured — nothing posted.**

## Performance

- **Duration:** ~15 min
- **Completed:** 2026-09-02T14:16:10Z
- **Tasks:** 2
- **Files modified:** 8 (7 created under the phase directory, plus `.planning/STATE.md`)

## Accomplishments

- Captured the pre-post state of all four upstream issues from the live GitHub API — all four `open` with `0` comments — and prom's `pinnedIssues` count via GraphQL, confirmed empty, into `evidence/173-04-issue-state-before.json`.
- Drafted all four replies criterion 5 owes (widened to include gh#6 per D-12): gh#5 stays open as the FUT-W-01 through FUT-W-05 tracker; gh#6 and gh#7 are drafted reply-and-close; gh#9 is drafted reply-stays-open-and-gets-pinned.
- Named both of Phase 172 D-11's declines — required status checks and required review-thread resolution — explicitly in the gh#6 body, per NON-CLAIM 2's instruction that they must not read as quietly delivered.
- Named all five FUT-W-01…05 requirements by ID in the gh#5 body and stated "deferred, not delivered."
- Stored each body once as a file under `evidence/bodies/173-gh<n>.md` and embedded it byte-for-byte inside `173-UPSTREAM-REPLIES.md`, so the operator's review and plan 173-07's `--body-file` post cannot diverge.
- Mechanically resolved every URL across the four bodies (3 distinct URLs: two wiki pages, one cross-issue link) — all returned `200` — and recorded the result in `evidence/173-04-draft-link-check.txt`.
- Re-confirmed all four issues at zero comments after drafting. `173-UPSTREAM-REPLIES.md`'s review status is `PENDING OPERATOR REVIEW`.

## Task Commits

Each task was committed atomically:

1. **Task 1: Capture what the four issues say and what this milestone actually delivered against each** - `17ed2d9c` (docs)
2. **Task 2: Draft the four replies into the phase record, as the exact bytes that will be posted** - `db2cfaaa` (docs)

**Plan metadata:** commit pending (this SUMMARY + STATE.md)

## Files Created/Modified

- `.planning/phases/173-.../evidence/173-04-issue-state-before.json` - Pre-post capture: state, comment count, title, URL for gh#5/6/7/9, plus prom's pinned-issue count (0).
- `.planning/phases/173-.../173-UPSTREAM-REPLIES.md` - The reviewable record: header, D-13 review status, disposition table, and all four bodies embedded verbatim.
- `.planning/phases/173-.../evidence/bodies/173-gh5.md` - The exact bytes for gh#5's reply (stays open, FUT-W-01…05 tracker).
- `.planning/phases/173-.../evidence/bodies/173-gh6.md` - The exact bytes for gh#6's reply (reply and close; both D-11 declines named).
- `.planning/phases/173-.../evidence/bodies/173-gh7.md` - The exact bytes for gh#7's reply (reply and close; premise rejected 2026-07-27, content lives on in gh#5).
- `.planning/phases/173-.../evidence/bodies/173-gh9.md` - The exact bytes for gh#9's reply (stays open, gets pinned; configured end state).
- `.planning/phases/173-.../evidence/173-04-draft-link-check.txt` - One status line per URL across all four bodies; all `200`.
- `.planning/STATE.md` - Current Position advanced to plan 04 (frontmatter and body updated together).

## Decisions Made

- gh#5's body names `FUT-W-01` through `FUT-W-05` as literal tokens (not just prose description) alongside "deferred, not delivered," so the requirement identifiers are greppable in the posted text itself, not only in `.planning/`.
- gh#6's body treats the two D-11 declines as a first-class named section rather than a passing mention, matching NON-CLAIM 2's own instruction from Phase 172's closing sweep.
- gh#9's body states outright that nothing was declined against it, rather than manufacturing a decline to fit a template — the three universal content requirements (delivered / declined-and-why / surviving tracker) are satisfied per-issue on their own terms, not mechanically repeated where they don't apply.
- All URLs kept in plain, greppable `https://github.com/henols/firestarter_prom/...` form per the CONTEXT.md instruction that this phase's own outputs join the Backlog 999.9 re-sweep set.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required. `gh` was already authenticated as `henols` with read access; no write calls were made.

## ROADMAP.md / REQUIREMENTS.md Untouched (orchestrator-owned artifacts)

Asserted per this plan's hard prohibition. Both files are provably unchanged by this plan's two commits:

```
$ git diff --quiet HEAD~2 HEAD -- .planning/ROADMAP.md .planning/REQUIREMENTS.md; echo $?
0
$ git diff --quiet HEAD~1 HEAD -- .planning/ROADMAP.md .planning/REQUIREMENTS.md; echo $?
0
```

Both exit `0` (no difference) against the pre-plan `HEAD~2` and against the intermediate `HEAD~1` — neither file was touched by either task commit. `.planning/REQUIREMENTS.md`'s POLICY-04 checkbox remains unflipped: this plan drafts a required deliverable toward POLICY-04 (the reviewable replies) but does not itself close the requirement — POLICY-04 and POLICY-05 are both multi-plan requirements this phase's later plans complete.

## Next Phase Readiness

- `173-UPSTREAM-REPLIES.md` and the four `evidence/bodies/173-gh<n>.md` files are ready for the operator's D-13 wording review. Plan 173-07 is gated on that review changing the status line away from `PENDING OPERATOR REVIEW`.
- `evidence/173-04-issue-state-before.json` is the before-half plan 173-07 needs for its own after-comparison.
- No blockers. Plan 173-03 has not yet run (independent wave-1 plan with `depends_on: []`, same as this one) — not a dependency of this plan or of 173-07.

---
*Phase: 173-close-beta-cut-under-protection-close-procedure-honesty-ledg*
*Completed: 2026-09-02*
