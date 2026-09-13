---
phase: 187-answered-reports
plan: 08
subsystem: infra
tags: [github-api, operator-gate, reply-posting]

requires:
  - phase: 187-05
    provides: "evidence/bodies/187-gh62.md draft, evidence/187-05-body-hashes.txt hash binding, 187-UPSTREAM-REPLIES.md gh#62 PENDING OPERATOR REVIEW status line"
  - phase: 187-07
    provides: "the per-issue approval/post/round-trip discipline this plan repeats verbatim for a second issue"
provides:
  - "gh#62 posted, labelled cause:firmware, left OPEN — REPLY-03 delivered"
  - "evidence/187-08-gh62-operator-approval.txt, evidence/187-08-post-transcript.txt, evidence/187-08-comment-id.txt — the per-issue approval/posting evidence chain"
affects: [187-09, 187-10, 187-11, 187-12]

actuals:
  tokens: 2427
  tasks: 2
  commits: 2
  plan_head_before: "02620422"

tech-stack:
  added: []
  patterns:
    - "Approve-as-drafted path: when the operator selects `approve` with no amendment, the pre-existing 187-05 sha256 binds unchanged straight through to the post — no diff, no recompute, no inline-copy re-amend step (contrast with 187-07's `amend` path)."
    - "Byte-identity proof via a Python JSON round trip (decode .body, compare raw bytes/hashes) rather than `gh api --jq '.body'` piped into diff, which false-alarms on jq's own trailing newline."

key-files:
  created:
    - .planning/phases/187-answered-reports/evidence/187-08-gh62-operator-approval.txt
    - .planning/phases/187-answered-reports/evidence/187-08-post-transcript.txt
    - .planning/phases/187-answered-reports/evidence/187-08-comment-id.txt
  modified:
    - .planning/phases/187-answered-reports/187-UPSTREAM-REPLIES.md

key-decisions:
  - "Operator approved the gh62 body exactly as drafted in 187-05 — no amendment — so the recorded sha256 (7edb9aa6e9a2fa366f51771497b67fceba255d0ec6442d27ae0c24dc264bd065) carried unchanged from the pre-gate draft straight through to the post."
  - "Operator selected the `cause:firmware` label (the reading that the missing chip-erase capability is a firmware gap) over the `no label` alternative; `needs:report` was explicitly and separately declined because the body asks the reporter for nothing."
  - "Operator confirmed the gh#65/gh#66 acknowledgement line stands as drafted with no rewording, and explicitly confirmed gh#62 is NOT closed — the refusal is correct behaviour, but the software chip-erase capability (backlog 999.63) is real, undelivered work."

requirements-completed: [REPLY-03]

coverage:
  - id: D1
    description: "The operator's Task 1 decision (approve body as drafted, cause:firmware label, no acknowledgement reword, no close) was recorded in evidence/187-08-gh62-operator-approval.txt with the required literal, operator identity/date, decision prose explicitly labelled as a rendering of a menu selection rather than a verbatim quotation, and the sha256 binding — before anything was posted"
    requirement: "REPLY-03"
    verification:
      - kind: other
        ref: "head -1 evidence/187-08-gh62-operator-approval.txt == 'APPROVED-FOR-POST: gh62'; sha256sum evidence/bodies/187-gh62.md bound into the approval file (grep -qF match); commit 80b2bac5 predates the post commit ea095e9f"
        status: pass
    human_judgment: false
  - id: D2
    description: "The approved body was posted to gh#62 via --body-file, proven byte-identical to the file on disk by a JSON round trip (not the prohibited jq/diff form), labelled cause:firmware, left OPEN, and the resulting state/label set/comment count all match the approval file"
    requirement: "REPLY-03"
    verification:
      - kind: other
        ref: "gh issue view 62 --json state,labels,comments -> OPEN/[cause:firmware]/1; python round trip -> BYTE-IDENTICAL, exit 0; both recorded in evidence/187-08-post-transcript.txt"
        status: pass
    human_judgment: false
  - id: D3
    description: "gh#60, gh#23, gh#28 and gh#31 are unchanged by this plan; 187-UPSTREAM-REPLIES.md's gh#62 status/Posted lines were flipped and the other four issues' status lines were left untouched"
    requirement: "REPLY-03"
    verification:
      - kind: other
        ref: "gh issue view 60 -> CLOSED/COMPLETED/[fix:released]/1 comment (unchanged); gh issue view 23/31 -> comments 3/2 (unchanged); grep '^**Status — gh#' 187-UPSTREAM-REPLIES.md -> 5 lines, exactly 3 still PENDING OPERATOR REVIEW (gh#23/#28/#31), gh#60 and gh#62 both flipped"
        status: pass
    human_judgment: false

duration: 9min
completed: 2026-09-12
status: complete
---

# Phase 187 Plan 08: Post gh#62 reply, apply operator-approved label, leave open Summary

**Posted the operator-approved (unamended) REPLY-03 reply to gh#62, applied the `cause:firmware` label to a previously unlabelled issue, and confirmed it stays open — proven byte-identical end to end, with gh#60/#23/#28/#31 untouched.**

## Performance

- **Duration:** 9 min
- **Started:** 2026-09-12T15:41:00Z (approx.)
- **Completed:** 2026-09-12T15:50:00Z (approx.)
- **Tasks:** 2
- **Files modified:** 4 (3 created, 1 modified)

## Accomplishments

- Recorded the operator's already-answered Task 1 decision — approve the body byte-for-byte as
  drafted (sha256 `7edb9aa6e9a2fa366f51771497b67fceba255d0ec6442d27ae0c24dc264bd065`, unchanged
  from the 187-05 draft), apply `cause:firmware` only, leave the gh#65/gh#66 acknowledgement line
  as drafted, and do NOT close — into
  `evidence/187-08-gh62-operator-approval.txt`, with the operator's identity, the harness-mode
  disclosure, decision prose explicitly labelled as the orchestrator's rendering of the menu
  selection (not a verbatim quotation), and the hash binding. Committed (`80b2bac5`) before
  anything was posted.
- Posted the unamended body to gh#62 via `gh issue comment --body-file` (never interpolated onto
  the command line); the API read-back matched the file byte-for-byte via a Python JSON round trip
  (3939 bytes both sides, identical sha256) — the prohibited `gh api --jq '.body' | diff` form was
  never used.
- Applied `cause:firmware` to an issue that previously carried zero labels. Re-read confirms
  `state: OPEN`, `labels: [cause:firmware]`, `comments: 1`. No close was performed or attempted.
- Confirmed gh#60 still `CLOSED`/`COMPLETED`/`[fix:released]`/1 comment (undisturbed by 187-07),
  and gh#23 (3 comments) and gh#31 (2 comments) both unchanged before and after the post — no
  collateral act on any issue this gate did not approve. gh#9 was not touched at all.
- Flipped gh#62's top-level Status line and its section's Posted line in
  `187-UPSTREAM-REPLIES.md`; the three remaining issues' status lines are untouched.

## Task Commits

Each task was committed atomically:

1. **Task 1: Approve the exact body, label set and acknowledgement wording (checkpoint:decision, pre-answered)** -
   `80b2bac5` (docs) — approval file written recording the operator's already-supplied decision;
   nothing posted before this commit
2. **Task 2: Post to gh#62, prove byte-identity, apply the label, leave it open** - `ea095e9f`
   (feat) — comment posted, byte-identity proven, label applied, status lines flipped

**Plan metadata:** (this commit) — SUMMARY.md, STATE.md, ROADMAP.md

## Files Created/Modified

- `evidence/187-08-gh62-operator-approval.txt` - the per-issue approval literal, operator
  identity/date, decision prose, approved label list, acknowledgement decision, unchanged sha256
- `187-UPSTREAM-REPLIES.md` - gh#62 status/Posted lines updated; other four issues untouched
- `evidence/187-08-post-transcript.txt` - every command, exit code, and result for the pre-post
  baseline, the post, the round trip, the label edit, and the collateral-untouched proof
- `evidence/187-08-comment-id.txt` - the posted comment id alone (`5646897010`)

## Decisions Made

- Operator selected `approve` for the body (post byte-for-byte, no amendment), `cause:firmware`
  for the label (declining both "no label" and the unoffered `needs:report`), and confirmed the
  gh#65/gh#66 acknowledgement line stands as drafted with the issue remaining OPEN — see
  key-decisions above and the approval file for full detail.
- Because no amendment was requested, this plan's evidence chain skips the amend-then-recompute
  steps 187-07 needed (no `.amendment.diff`, no stale-hash marker in `187-05-body-hashes.txt` —
  that file's gh#62 hash line was never superseded).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Verify-leg literal count stale] The plan's `PENDING OPERATOR REVIEW` grep leg expects 3, raw grep returns 5**
- **Found during:** Task 2 (post-flip verification)
- **Issue:** The plan's automated verify leg `grep -c 'PENDING OPERATOR REVIEW' 187-UPSTREAM-REPLIES.md` expects exactly `3` after gh#62's status line flips. As already documented in `187-07-SUMMARY.md`, the file carries two pre-existing prose sentences (written by 187-05) containing the literal `PENDING OPERATOR REVIEW` that are explanatory text, not per-issue `**Status — gh#N:**` lines — inflating the raw literal count above the per-issue invariant both before and after this plan's flip.
- **Fix:** No plan text was altered (the discrepancy belongs to 187-05's/187-06's authored prose, out of this plan's scope). Verified the actual invariant instead: `grep '^**Status — gh#' 187-UPSTREAM-REPLIES.md'` returns 5 total per-issue status lines, of which exactly 3 remain `PENDING OPERATOR REVIEW` (gh#23, gh#28, gh#31) and gh#60/gh#62 are both flipped to their posted states. This matches the plan's own acceptance-criterion wording ("exactly three pending status lines remaining") more precisely than the raw literal grep the automated `<verify>` leg uses.
- **Files modified:** None (verification-only; the file's prose sentences are unchanged, inherited as-is from 187-05/187-06)
- **Verification:** `grep -c '^\*\*Status — gh#' 187-UPSTREAM-REPLIES.md` = 5; `grep '^\*\*Status — gh#' ... | grep -c 'PENDING OPERATOR REVIEW'` = 3
- **Committed in:** ea095e9f (Task 2 commit)

---

**Total deviations:** 1 auto-fixed (1 stale verify-leg literal, inherited from 187-05/187-06's own documented discrepancy — same known non-defect 187-07 already surfaced)
**Impact on plan:** No scope creep. The true acceptance criterion — three per-issue status lines still pending — holds; only the automated verify leg's raw-count arithmetic is stale, and that staleness was already flagged as a known, not-owned discrepancy by 187-07's SUMMARY.

## Issues Encountered

None beyond the documented deviation above.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- REPLY-03 delivered end to end: gh#62 posted, labelled `cause:firmware`, left open, and provably
  byte-identical.
- Three issues (gh#23, gh#28, gh#31) remain `PENDING OPERATOR REVIEW` for Plans 187-09 through
  187-11, each gated the same way — approve on disk, post via `--body-file`, read back, prove
  byte-identical.
- `evidence/187-07-window-start.txt` (already captured, not re-taken by this plan) remains the
  phase's single window-start timestamp for Plan 187-12's collateral-comment sweep.

---
*Phase: 187-answered-reports*
*Completed: 2026-09-12*

## Self-Check: PASSED

- All key-files.created found on disk (3/3): `evidence/187-08-gh62-operator-approval.txt`,
  `evidence/187-08-post-transcript.txt`, `evidence/187-08-comment-id.txt`.
- `git log --oneline --all --grep="187-08"` returns 2 task commits (`80b2bac5`, `ea095e9f`).
- Acceptance criteria re-verified live: `head -1` approval file (`APPROVED-FOR-POST: gh62`), sha256
  binding (`BOUND`), byte-identity round trip (`BYTE-IDENTICAL`, exit 0), `gh issue view 62`
  state/labels/comments (`OPEN`/`[cause:firmware]`/1), gh#60 unchanged (`CLOSED`/`COMPLETED`/
  `[fix:released]`/1), gh#23 (3 comments) and gh#31 (2 comments) unchanged — all PASS (see
  transcript for full command output).
- Plan-level `<verification>` re-run: approval file exists with literal + hash; posted comment
  reads back byte-identical; gh#62 OPEN with exactly one comment and exactly the approved label
  set; gh#60/gh#23/gh#31 comment counts unchanged; three pending status lines remain (per the
  per-issue status-line invariant — see Deviations for the raw-grep discrepancy this leg inherits).
