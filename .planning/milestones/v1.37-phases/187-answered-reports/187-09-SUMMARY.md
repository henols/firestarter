---
phase: 187-answered-reports
plan: 09
subsystem: infra
tags: [github-api, operator-gate, reply-posting]

requires:
  - phase: 187-06
    provides: "evidence/bodies/187-gh23.md draft, evidence/187-06-body-hashes.txt hash binding, 187-UPSTREAM-REPLIES.md gh#23 PENDING OPERATOR REVIEW status line"
  - phase: 187-08
    provides: "the per-issue approval/post/round-trip discipline this plan repeats verbatim for a third issue, and the window-start timestamp this phase's collateral proof anchors to"
provides:
  - "gh#23 posted, labelled cause:rig + needs:report (cause:database retained), left OPEN — REPLY-01 delivered"
  - "evidence/187-09-gh23-operator-approval.txt, evidence/187-09-post-transcript.txt, evidence/187-09-comment-id.txt — the per-issue approval/posting evidence chain, with the gate's delegation provenance recorded truthfully"
affects: [187-10, 187-11, 187-12]

actuals:
  tokens: 2474
  tasks: 2
  commits: 2
  plan_head_before: "c0111fb0"

tech-stack:
  added: []
  patterns:
    - "Delegated-gate provenance: when a blocking-human checkpoint is answered by an operator delegation ('you decide') rather than a menu selection, the approval file must record the delegation verbatim, attribute the actual body/label/close selection to the orchestrator under that delegation, and state the reasoning for each element — never render the selection as if the operator chose a listed option."
    - "Approve-as-drafted path repeated a third time: the pre-existing 187-06 sha256 binds unchanged straight through to the post — no diff, no recompute, no inline-copy re-amend step."
    - "Byte-identity proof via a Python JSON round trip (decode .body, compare raw bytes/hashes) rather than `gh api --jq '.body'` piped into diff, which false-alarms on jq's own trailing newline."

key-files:
  created:
    - .planning/phases/187-answered-reports/evidence/187-09-gh23-operator-approval.txt
    - .planning/phases/187-answered-reports/evidence/187-09-post-transcript.txt
    - .planning/phases/187-answered-reports/evidence/187-09-comment-id.txt
  modified:
    - .planning/phases/187-answered-reports/187-UPSTREAM-REPLIES.md

key-decisions:
  - "Task 1's blocking-human gate was answered by operator delegation ('you decide'), not a menu selection. The approval file records that delegation verbatim and attributes the body/label/no-close selection to the orchestrator acting under it, per the operator's own explicit instruction for this plan."
  - "Orchestrator selected: post the gh23 body byte-for-byte as drafted by 187-06 (no amendment, sha256 unchanged); add `cause:rig` and `needs:report`; keep `cause:database` and `dev-test`; do not close the issue."
  - "gh#23 remains OPEN — a close requires the reporter's confirmation or a superseding PASS, and neither exists in the tracker."

requirements-completed: [REPLY-01, REPLY-05, REPLY-06]

coverage:
  - id: D1
    description: "The gate's delegation ('you decide') and the orchestrator's resulting selection (approve body as drafted, add cause:rig + needs:report, keep cause:database, no close) were recorded in evidence/187-09-gh23-operator-approval.txt with the required literal, operator identity/date, the delegation quoted verbatim, an explicit statement that the selection is the orchestrator's rendering under that delegation (not a verbatim operator quotation), and the sha256 binding — before anything was posted"
    requirement: "REPLY-01"
    verification:
      - kind: other
        ref: "head -1 evidence/187-09-gh23-operator-approval.txt == 'APPROVED-FOR-POST: gh23'; sha256sum evidence/bodies/187-gh23.md bound into the approval file (grep -qF match); commit 6b16b1ad predates the post commit 839294b0"
        status: pass
    human_judgment: false
  - id: D2
    description: "The approved body was posted to gh#23 via --body-file, proven byte-identical to the file on disk by a JSON round trip (not the prohibited jq/diff form), labelled cause:rig and needs:report additively (cause:database and dev-test retained), left OPEN, and the resulting state/label set/comment count all match the approval file and the pre-phase baseline plus the approved additions"
    requirement: "REPLY-01, REPLY-06"
    verification:
      - kind: other
        ref: "gh issue view 23 --json state,labels,comments -> OPEN/[cause:database,cause:rig,dev-test,needs:report]/4; python round trip -> BYTE-IDENTICAL, exit 0; both recorded in evidence/187-09-post-transcript.txt"
        status: pass
    human_judgment: false
  - id: D3
    description: "gh#28, gh#31 and gh#9 are unchanged by this plan (comment counts and labels identical to the 187-05 before-capture); gh#60 and gh#62 remain in their already-established post-187-07/187-08 states; 187-UPSTREAM-REPLIES.md's gh#23 status/Posted lines were flipped and gh#28/gh#31's status lines were left untouched"
    requirement: "REPLY-06"
    verification:
      - kind: other
        ref: "gh issue view 28 -> 4 comments/[dev-test,cause:harness] (unchanged); gh issue view 31 -> 2 comments/[dev-test,cause:harness,cause:database] (unchanged); gh issue view 9 -> 1 comment (unchanged); gh issue view 60 -> CLOSED/COMPLETED/[fix:released]/1 comment (unchanged); gh issue view 62 -> OPEN/[cause:firmware]/1 comment (unchanged); grep '^**Status — gh#' 187-UPSTREAM-REPLIES.md -> 5 lines, exactly 2 still PENDING OPERATOR REVIEW (gh#28, gh#31), gh#23/#60/#62 all flipped"
        status: pass
    human_judgment: false
  - id: D4
    description: "The delegation itself (the operator saying 'you decide' rather than selecting an option) was recorded truthfully rather than papered over as an ordinary menu selection, per the explicit gate-provenance instruction carried into this plan"
    human_judgment: true
    rationale: "Whether the recorded wording faithfully distinguishes 'operator delegated' from 'operator selected' is a judgment about prose honesty, not something a grep or hash can prove on its own. The approval file's own text is the evidence; a human should read it to confirm it does not imply a menu choice that never happened."

duration: 12min
completed: 2026-09-12
status: complete
---

# Phase 187 Plan 09: Post gh#23 reply, apply operator-delegated labels, leave open Summary

**Posted the orchestrator-selected (operator-delegated, not menu-selected) REPLY-01 reply to gh#23, added `cause:rig` and `needs:report` while retaining `cause:database`, and confirmed it stays open — proven byte-identical end to end, with gh#28/#31/#9/#60/#62 all unchanged.**

## Performance

- **Duration:** 12 min
- **Started:** 2026-09-12T15:55:00Z (approx.)
- **Completed:** 2026-09-12T16:07:00Z (approx.)
- **Tasks:** 2
- **Files modified:** 4 (3 created, 1 modified)

## Accomplishments

- Recorded the Task 1 gate's true provenance — the operator delegated the decision in their own
  words ("you decide") rather than selecting one of the three offered menu options — into
  `evidence/187-09-gh23-operator-approval.txt`, together with the orchestrator's resulting
  selection (approve body as drafted, add `cause:rig` + `needs:report`, keep `cause:database`, no
  close) and the reasoning for each element, explicitly labelled as the orchestrator's rendering
  under delegation and never as a verbatim operator quotation of a selection that did not happen.
  Committed (`6b16b1ad`) before anything was posted.
- Re-asserted the gate mechanically (recomputed sha256, matched the approval file) immediately
  before posting, per the task's `<precondition>`.
- Posted the unamended body to gh#23 via `gh issue comment --body-file` (never interpolated onto
  the command line); the API read-back matched the file byte-for-byte via a Python JSON round trip
  (3694 bytes both sides, identical sha256) — the prohibited `gh api --jq '.body' | diff` form was
  never used.
- Applied `cause:rig` and `needs:report` via `--add-label` only; re-read confirms `state: OPEN`,
  `stateReason: ""`, `labels: [cause:database, cause:rig, dev-test, needs:report]` (sorted),
  `comments: 4` (pre-phase 3 plus this post). `cause:database` and `dev-test` both survived. No
  close was performed or attempted.
- Confirmed gh#28 (4 comments, `[dev-test, cause:harness]`), gh#31 (2 comments,
  `[dev-test, cause:harness, cause:database]`) and gh#9 (1 comment) all unchanged from the 187-05
  before-capture, and gh#60 (`CLOSED`/`COMPLETED`/`[fix:released]`/1 comment) and gh#62
  (`OPEN`/`[cause:firmware]`/1 comment) both undisturbed from their already-posted 187-07/187-08
  states.
- Flipped gh#23's top-level Status line and added a Posted-line field to its section in
  `187-UPSTREAM-REPLIES.md`; gh#28's and gh#31's status lines are untouched.

## Task Commits

Each task was committed atomically:

1. **Task 1: Apply orchestrator-delegated gh23 decision and record approval (checkpoint:decision, delegated)** -
   `6b16b1ad` (docs) — approval file written recording the delegation and the resulting selection;
   nothing posted before this commit
2. **Task 2: Post to gh#23, prove byte-identity, apply the labels, leave it open** - `839294b0`
   (feat) — comment posted, byte-identity proven, labels applied, status line flipped

**Plan metadata:** (this commit) — SUMMARY.md, STATE.md, ROADMAP.md

## Files Created/Modified

- `evidence/187-09-gh23-operator-approval.txt` - the per-issue approval literal, the delegation
  quoted verbatim, the orchestrator's selection and reasoning, the approved label list, the no-close
  record, unchanged sha256
- `187-UPSTREAM-REPLIES.md` - gh#23 status/Posted lines updated; gh#28/gh#31 status lines untouched
- `evidence/187-09-post-transcript.txt` - every command, exit code, and result for the pre-post
  baseline, the post, the round trip, the label edits, and the collateral-untouched proof
- `evidence/187-09-comment-id.txt` - the posted comment id alone (`5647009393`)

## Decisions Made

See key-decisions in frontmatter. In short: the gate was answered by delegation, not selection; the
orchestrator, acting under that delegation, chose to post the body unamended, add `cause:rig` and
`needs:report` while retaining `cause:database`, and leave the issue open.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Verify-leg literal count stale] The plan's `PENDING OPERATOR REVIEW` grep leg expects 2, raw grep returns 4**
- **Found during:** Task 2 (post-flip verification)
- **Issue:** The plan's automated verify leg `grep -c 'PENDING OPERATOR REVIEW' 187-UPSTREAM-REPLIES.md` expects exactly `2` after gh#23's status line flips. As already documented in `187-07-SUMMARY.md` and `187-08-SUMMARY.md`, the file carries two pre-existing prose sentences (written by 187-05) containing the literal `PENDING OPERATOR REVIEW` that are explanatory text, not per-issue `**Status — gh#N:**` lines — inflating the raw literal count above the per-issue invariant both before and after this plan's flip.
- **Fix:** No plan text was altered (the discrepancy belongs to 187-05's authored prose, out of this plan's scope). Verified the actual invariant instead: `grep '^**Status — gh#' 187-UPSTREAM-REPLIES.md'` returns 5 total per-issue status lines, of which exactly 2 remain `PENDING OPERATOR REVIEW` (gh#28, gh#31) and gh#23/gh#60/gh#62 are all flipped to their posted states. This matches the plan's own acceptance-criterion wording more precisely than the raw literal grep the automated `<verify>` leg uses.
- **Files modified:** None (verification-only; the file's prose sentences are unchanged, inherited as-is from 187-05)
- **Verification:** `grep -c '^\*\*Status — gh#' 187-UPSTREAM-REPLIES.md` = 5; `grep '^\*\*Status — gh#' ... | grep -c 'PENDING OPERATOR REVIEW'` = 2
- **Committed in:** 839294b0 (Task 2 commit)

**2. [Rule 4-adjacent — provenance wording divergence, resolved by explicit instruction, not auto-decided] Approval file records a delegation, not a menu selection**
- **Found during:** Task 1 (before writing the approval file)
- **Issue:** The plan's own Task 1 text instructs writing "decision prose explicitly labelled as the orchestrator's rendering of a menu selection plus its option description rather than a verbatim operator quotation" — wording that presumes the operator picked one of the three offered options (`approve`/`amend`/`hold`). That did not happen here: the operator delegated the entire decision ("you decide") rather than selecting an option, and the dispatching prompt for this plan carried an explicit, detailed instruction (a `<gate_provenance_READ_THIS_FIRST>` block) requiring the approval file to record that delegation truthfully — the operator's verbatim words, an explicit statement that the SELECTION was the orchestrator's under that delegation, and the orchestrator's own reasoning for each element — and forbidding any prose implying a menu choice that never occurred.
- **Fix:** Followed the explicit dispatching instruction over the plan's literal wording, which itself anticipates exactly this case: "If the plan's acceptance criteria are worded assuming an operator selection, satisfy their INTENT (an auditable record of who decided what, and on what basis) and record the wording divergence as a deviation in SUMMARY.md." `evidence/187-09-gh23-operator-approval.txt` quotes "you decide" verbatim, states plainly that the body/label/no-close selection was made by the orchestrator under that delegation, and gives the orchestrator's reasoning for each element. This satisfies the acceptance criterion's actual intent (an auditable, non-fabricated record of who decided what and why) without asserting a menu selection that did not happen.
- **Files modified:** `evidence/187-09-gh23-operator-approval.txt` (this is the file the deviation concerns; no other file was affected)
- **Verification:** File committed (`6b16b1ad`) before any public act; `head -1` reads the literal; the delegation quote and the "selection was the orchestrator's" statement are both present and legible in the committed text.
- **Committed in:** 6b16b1ad (Task 1 commit)

---

**Total deviations:** 2 auto-fixed (1 stale verify-leg literal inherited from 187-05's own documented discrepancy, same known non-defect 187-07/187-08 already surfaced; 1 wording divergence resolved per an explicit, more specific instruction that itself anticipated and pre-authorized this exact deviation)
**Impact on plan:** No scope creep. The true acceptance criterion — an auditable record of who decided what, on what basis — holds; the approval file records the delegation honestly rather than fabricating a selection. The verify-leg literal-count staleness is a pre-existing, already-documented non-defect in 187-05's prose.

## Issues Encountered

None beyond the two documented deviations above.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- REPLY-01 delivered end to end: gh#23 posted, labelled `cause:rig` + `needs:report` (with
  `cause:database` retained), left open, and provably byte-identical.
- REPLY-05's schema_version/dedup_fingerprint re-run sentence is present in the posted body (in
  the "If you want to re-run it." section), and REPLY-06 (no unilateral close) held: the issue
  remains OPEN.
- Two issues (gh#28, gh#31) remain `PENDING OPERATOR REVIEW` for Plans 187-10 and 187-11, each
  gated the same way — approve on disk, post via `--body-file`, read back, prove byte-identical.
- `evidence/187-07-window-start.txt` (already captured, not re-taken by this plan) remains the
  phase's single window-start timestamp for Plan 187-12's collateral-comment sweep.

---
*Phase: 187-answered-reports*
*Completed: 2026-09-12*

## Self-Check: PASSED

- All key-files.created found on disk (3/3): `evidence/187-09-gh23-operator-approval.txt`,
  `evidence/187-09-post-transcript.txt`, `evidence/187-09-comment-id.txt`.
- `git log --oneline --all --grep="187-09"` returns 2 task commits (`6b16b1ad`, `839294b0`).
- Acceptance criteria re-verified live: `head -1` approval file (`APPROVED-FOR-POST: gh23`), sha256
  binding (`BOUND`), byte-identity round trip (`BYTE-IDENTICAL`, exit 0), `gh issue view 23`
  state/labels/comments (`OPEN`/`[cause:database,cause:rig,dev-test,needs:report]`/4), gh#28
  (4 comments) and gh#31 (2 comments) and gh#9 (1 comment) unchanged, gh#60/gh#62 undisturbed —
  all PASS (see transcript for full command output).
- Plan-level `<verification>` re-run: approval file exists with delegation record, selection and
  reasoning, and a hash covering the posted body; posted comment reads back byte-identical; gh#23
  OPEN with exactly one more comment than the before-capture and exactly the approved label set;
  gh#28/gh#31/gh#9/gh#60/gh#62 all unchanged; two pending status lines remain (per the per-issue
  status-line invariant — see Deviations for the raw-grep discrepancy this leg inherits).
