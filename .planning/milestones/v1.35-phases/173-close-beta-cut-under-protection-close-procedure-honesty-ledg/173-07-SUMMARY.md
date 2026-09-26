---
phase: 173-close-beta-cut-under-protection-close-procedure-honesty-ledg
plan: 07
subsystem: infra
tags: [github-api, github-graphql, issue-tracker, honesty-ledger, upstream-replies]

requires:
  - phase: 173-close-beta-cut-under-protection-close-procedure-honesty-ledg
    provides: "173-04's four drafted reply bodies behind a blocking wording review; 173-03's ruleset rejection probe evidence"
provides:
  - "Four public comments on henols/firestarter_prom (gh#5, gh#6, gh#7, gh#9), each byte-identical to an operator-approved body file"
  - "gh#6's Delivered bullet amended to cite the performed push rejected by GH013, not an API ruleset read-back — the operator's one condition on approval"
  - "gh#7 and gh#6 closed; gh#5 and gh#9 stay open"
  - "gh#9 pinned via the GraphQL pinIssue mutation — prom's pinned-issue count goes from 0 to 1"
  - "173-UPSTREAM-REPLIES.md flipped from PENDING OPERATOR REVIEW to APPROVED AND POSTED, with a comment URL beside each body"
affects: [173-08, 173-09]

actuals:
  tokens: 9500
  tasks: 3
  commits: 3

tech-stack:
  added: []
  patterns:
    - "Hash-bound on-disk approval file (D-13 blocking wording review made mechanical): a checkpoint alone cannot authorize an outward-facing post; only an approval file carrying sha256 of the exact bytes about to go public can."
    - "--body-file for every outward-facing comment, never composed at posting time, then read the posted comment back from the API to prove byte-identity."

key-files:
  created:
    - .planning/phases/173-close-beta-cut-under-protection-close-procedure-honesty-ledg/evidence/173-07-operator-approval.txt
    - .planning/phases/173-close-beta-cut-under-protection-close-procedure-honesty-ledg/evidence/173-07-post-transcript.txt
    - .planning/phases/173-close-beta-cut-under-protection-close-procedure-honesty-ledg/evidence/173-07-issue-state-after.json
  modified:
    - .planning/phases/173-close-beta-cut-under-protection-close-procedure-honesty-ledg/evidence/bodies/173-gh6.md
    - .planning/phases/173-close-beta-cut-under-protection-close-procedure-honesty-ledg/173-UPSTREAM-REPLIES.md

key-decisions:
  - "The D-13 blocking wording review was conducted by the orchestrator with the operator before this plan ran (verdict: 'Approve, strengthen gh#6' — approve all four, amend gh#6's verification sentence first). This plan made that review mechanical: it wrote the on-disk approval file hash-bound to the four bodies as amended, and the plan's own gates asserted the file and the hashes before anything was posted — consistent with the plan's own warning that 'an approved-looking checkpoint is not' authorization by itself."
  - "gh#6's amendment cites only what 173-03's probe transcripts actually measured — an empty commit pushed at each protected main, rejected by GitHub's own GH013 rule-violation text naming the pull-request requirement, paired with an accepted-then-deleted push to a throwaway ref — and makes no CI-observation claim the transcripts do not support."
  - "The amendment was applied identically to evidence/bodies/173-gh6.md and to the embedded copy inside 173-UPSTREAM-REPLIES.md, so the two stay byte-identical, and no other sentence in gh#6 or byte of the other three bodies changed."

patterns-established:
  - "Corrected-verify-script pattern: when a plan's own <verify> asserts an invariant that predates and is unrelated to the plan's action (here, a zero-comment baseline across an entire centralized issue tracker), the executor documents the defect as a Rule 1 deviation and substitutes a narrower check that actually proves the plan's own claim (here, a comment-creation-timestamp scan), rather than silently skipping the gate."

requirements-completed: [POLICY-04]

coverage:
  - id: D1
    description: "Four upstream replies posted, each byte-identical to its operator-approved body, via --body-file"
    requirement: POLICY-04
    verification:
      - kind: other
        ref: "Task 2 automated verify (comment count == 1 per issue, posted body == approved body file after newline normalization, for gh#5/6/7/9)"
        status: pass
    human_judgment: false
  - id: D2
    description: "gh#6's Delivered bullet amended to cite the performed GH013-rejected push, applied identically to the body file and the UPSTREAM-REPLIES.md embedded copy, no other byte changed"
    verification:
      - kind: other
        ref: "diff of embedded gh#6 body vs evidence/bodies/173-gh6.md (empty); Task 3 automated verify (body text still verbatim inside 173-UPSTREAM-REPLIES.md for all four issues)"
        status: pass
    human_judgment: false
  - id: D3
    description: "gh#7 and gh#6 closed; gh#5 and gh#9 remain open"
    requirement: POLICY-04
    verification:
      - kind: other
        ref: "Task 2 automated verify (issue state check via gh api) and Task 3 before/after reconciliation"
        status: pass
    human_judgment: false
  - id: D4
    description: "gh#9 pinned via GraphQL pinIssue; prom's pinned-issue count goes from 0 to 1"
    requirement: POLICY-04
    verification:
      - kind: other
        ref: "Task 3 automated verify (pinnedIssues totalCount==1, nodes==[9])"
        status: pass
    human_judgment: false
  - id: D5
    description: "Nothing posted before the on-disk operator approval existed, hash-bound to the four bodies"
    verification:
      - kind: other
        ref: "Task 1 automated verify (approval file literal + four sha256 lines + all four issues still zero comments before posting)"
        status: pass
    human_judgment: false
  - id: D6
    description: "173-UPSTREAM-REPLIES.md review status moved from PENDING OPERATOR REVIEW to APPROVED AND POSTED, with a comment URL recorded per issue"
    verification:
      - kind: other
        ref: "Task 3 automated verify (grep for PENDING OPERATOR REVIEW absent, APPROVED AND POSTED present, >=4 comment URLs, four body texts still verbatim)"
        status: pass
    human_judgment: false

duration: 12min
completed: 2026-09-02
status: complete
---

# Phase 173 Plan 07: Upstream Replies — Posted, Closed, Pinned Summary

**Four operator-approved upstream replies posted verbatim via `gh issue comment --body-file`, with gh#6's verification claim strengthened from an API ruleset read-back to the performed GH013-rejected push; gh#7 and gh#6 closed, gh#9 pinned via GraphQL, gh#5 left open.**

## Performance

- **Duration:** 12 min
- **Started:** 2026-09-02T14:44:00Z
- **Completed:** 2026-09-02T14:55:48Z
- **Tasks:** 3
- **Files modified:** 5 (3 created, 2 modified) + STATE.md

## Accomplishments
- D-13's blocking wording review, already conducted by the orchestrator with the operator (verdict: approve, strengthen gh#6), was made mechanical: `evidence/173-07-operator-approval.txt` carries the exact approval literal, the operator's name and date, and a sha256 for each of the four body files as amended — asserted by the plan's own gate before a single post.
- gh#6's third "Delivered" bullet was amended from "verified by reading the ruleset configuration back from the API" to citing the stronger evidence 173-03 actually measured: an empty commit pushed at each protected `main`, rejected by GitHub's own `GH013: Repository rule violations found` message naming the pull-request requirement, paired with an accepted-then-deleted push to an unprotected throwaway ref. Applied identically to `evidence/bodies/173-gh6.md` and the embedded copy in `173-UPSTREAM-REPLIES.md` (confirmed byte-identical by diff); no other sentence in gh#6 and no byte of the other three bodies changed.
- All four bodies posted to `henols/firestarter_prom` via `gh issue comment --body-file`: gh#5 (`#issuecomment-5511486703`), gh#6 (`#issuecomment-5511486995`), gh#7 (`#issuecomment-5511487257`), gh#9 (`#issuecomment-5511487546`) — each confirmed byte-identical to its approved file by reading the posted comment back from the API.
- gh#7 and gh#6 closed (`closedAt` 2026-09-02T14:50:51Z and 14:50:52Z); gh#5 and gh#9 left open.
- gh#9 pinned via the GraphQL `pinIssue` mutation, after re-resolving both node ids at run time (`R_kgDOSX4ERw`, `I_kwDOSX4ER88AAAABId5Qdw`) and confirming they matched the RESEARCH.md-measured values before mutating. `pinnedIssues` on `henols/firestarter_prom` goes from `totalCount: 0` to `totalCount: 1`, naming issue 9 — a gap both ROADMAP criterion 5 and Backlog 999.13 assumed already closed.
- `evidence/173-07-issue-state-after.json` reconciles against plan 173-04's before-capture on every field: all four comment counts 0→1, gh#6/gh#7 open→closed, gh#5/gh#9 stayed open, pinned count 0→1.
- `173-UPSTREAM-REPLIES.md` now reads `APPROVED AND POSTED`, records the operator and date, carries a comment URL beside each of the four bodies, and its "Posting outcome" section summarizes the result for a future reader.

## Task Commits

Each task was committed atomically:

1. **Task 1: The blocking wording review — operator reads all four bodies and writes the approval file** - `cefb6ae1` (docs)
2. **Task 2: Post the four approved bodies, byte for byte, and close the two issues D-12 closes** - `fda54631` (docs)
3. **Task 3: Pin gh#9 by the only API that can, then capture the after-state and flip the review record** - `658b5158` (docs)

**Plan metadata:** commit to follow (docs: complete plan)

## Files Created/Modified
- `evidence/173-07-operator-approval.txt` - On-disk approval, hash-bound to the four bodies as amended, recording the orchestrator's rendering of the operator's approve-with-amendment verdict
- `evidence/173-07-post-transcript.txt` - Per-issue posting command, returned URL, comment id, closure timestamps, and the corrected collateral-comment sweep
- `evidence/173-07-issue-state-after.json` - Complete after-state read from the API, same shape as 173-04's before-capture
- `evidence/bodies/173-gh6.md` - Amended verification sentence in the third Delivered bullet
- `173-UPSTREAM-REPLIES.md` - Review status flipped PENDING → APPROVED AND POSTED; Operator Review section added; comment URL added beside each body; Posting outcome section added

## Decisions Made
- Recorded the D-13 review outcome as the orchestrator's rendering of a menu selection plus its option description, not a fabricated operator quotation — per the orchestrator's explicit instruction not to attribute invented quotations to the operator.
- Applied the gh#6 amendment to both the standalone body file and the embedded copy inside `173-UPSTREAM-REPLIES.md` in the same edit, so the two never diverge, matching the file's own stated invariant ("stored a second time, byte-identical").
- Recorded an intermediate review-status value ("APPROVED, AMENDMENT TO GH#6 APPLIED — AWAITING POST") after Task 1's approval-file write and before Task 2's posting, then finalized to "APPROVED AND POSTED" at the end of Task 3 — both transitions move the status strictly away from the pending-review literal, satisfying both the pre-post assertions and Task 3's final gate.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Corrected Task 2's collateral-comment verify script, which asserted a false baseline**
- **Found during:** Task 2 (the second automated `<verify>` leg)
- **Issue:** The plan's script queries every issue in `henols/firestarter_prom` and asserts zero of them, outside 5/6/7/9, carry any comment. This assumes a clean baseline that has never existed: the repository is the project's centralized issue tracker (dev-test chip-validation reports and other work), and 39 of its 53 issues already carried comments before this plan ran. Run literally, the script fails on every execution regardless of what this plan does — it has no before/after comparison.
- **Fix:** Ran the intended check instead: queried every comment across the repository filtered to `created_at` within this plan's actual posting window (2026-09-02T14:50:00Z onward) and confirmed exactly four comments were created, one each on issues 5, 6, 7 and 9, and none elsewhere.
- **Files modified:** `evidence/173-07-post-transcript.txt` (corrected check and its result recorded there)
- **Verification:** `gh api repos/henols/firestarter_prom/issues/comments --paginate` filtered to the window returned exactly the four expected comment ids on the four expected issues.
- **Committed in:** `fda54631` (Task 2 commit)

---

**Total deviations:** 1 auto-fixed (1 bug in the plan's own verify tooling)
**Impact on plan:** No scope creep. The underlying claim the gate exists to protect — this plan touched no issue outside 5, 6, 7 and 9 — is proven true by the corrected check; the plan's literal script was simply unrunnable against this repository's real, pre-existing state.

## Issues Encountered
None beyond the deviation above.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- ROADMAP criterion 5 is discharged by sending, on all four issues including D-12's widening to gh#6, and gh#9's pin closes a gap that was measured rather than assumed.
- The four comment URLs are now on record in `173-UPSTREAM-REPLIES.md` and this Summary for plan 173-08's criterion-4 sweep, which owes them into the set of this phase's own outputs Backlog 999.9's rename will invalidate.
- Plans 06, 08 and 09 remain. ROADMAP.md and REQUIREMENTS.md were not touched by this plan (verified against `HEAD~3` and `HEAD~1`); those writes remain the orchestrator's.

## Self-Check: PASSED

- `evidence/173-07-operator-approval.txt` — FOUND
- `evidence/173-07-post-transcript.txt` — FOUND
- `evidence/173-07-issue-state-after.json` — FOUND
- `git log --oneline --all --grep="173-07"` returns 3 commits (`cefb6ae1`, `fda54631`, `658b5158`) — FOUND
- All 3 tasks' `<acceptance_criteria>` re-verified passing at time of writing (Task 1 approval-literal + hash gate, Task 2 post/close gate plus corrected collateral-comment sweep, Task 3 pin/reconciliation/record gate) — PASSED
- Plan-level `<verification>` bullets re-checked: on-disk approval precedes any post (PASS); each of gh#5/6/7/9 carries exactly one comment byte-identical to its approved body (PASS); gh#7/gh#6 closed, gh#5/gh#9 open (PASS); gh#9 pinned, count 1 naming issue 9 (PASS); no issue outside the four carries a comment created in this plan's window (PASS, corrected check); before/after reconciles on every field (PASS); `173-UPSTREAM-REPLIES.md` reads APPROVED AND POSTED with four comment URLs and matching body text (PASS)
- `.planning/ROADMAP.md` and `.planning/REQUIREMENTS.md` unchanged: `git diff --stat HEAD~3 HEAD -- .planning/ROADMAP.md .planning/REQUIREMENTS.md` and `git diff --stat HEAD~1 HEAD -- .planning/ROADMAP.md .planning/REQUIREMENTS.md` both empty — FOUND

---
*Phase: 173-close-beta-cut-under-protection-close-procedure-honesty-ledg*
*Completed: 2026-09-02*
