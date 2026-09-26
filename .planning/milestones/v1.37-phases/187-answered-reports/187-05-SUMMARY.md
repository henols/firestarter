---
phase: 187-answered-reports
plan: 05
subsystem: infra
tags: [github-api, reply-drafting, permalinks, jp5-gate, ae29f2008]

requires:
  - phase: 187-04
    provides: "The pinned meta merge SHA (evidence/187-02-merge-sha.txt), the read app version (3.0.0b39) and firmware version (3.0.0b27) this plan's bodies cite verbatim, and the two commit-SHA permalink URLs with anchors copied from the rendered pages (evidence/187-02-meta-merge.txt)"
provides:
  - "evidence/bodies/187-gh60.md and evidence/bodies/187-gh62.md — the two REPLY-04/REPLY-03 posting payloads, drafted to disk and posted nowhere"
  - "187-UPSTREAM-REPLIES.md — opened with a per-issue PENDING OPERATOR REVIEW gate, a five-issue Dispositions table, and the gh#60/gh#62 sections carrying their bodies inline byte-identically"
  - "evidence/187-05-issue-state-before.json — the pre-post API state of all six issues plus the pinnedIssues read, and re-verification of the three drift facts (gh#65/#66 open not unanswered, gh#68 open naming AE29F2008, gh#61 closed/validated)"
  - "evidence/187-05-draft-link-check.txt and evidence/187-05-body-hashes.txt — every link resolved at the pinned SHA, and the two bodies hash-bound for the 187-07/187-08 approval gates"
affects: [187-06, 187-07, 187-08, 187-12]

actuals:
  tokens: 7016
  tasks: 3
  commits: 3
  plan_head_before: bc090ccb

tech-stack:
  added: []
  patterns:
    - "Built the issue-state evidence file with a small python script calling `gh issue view --json` per issue rather than shelling out to `jq` inline, to avoid quoting fragility across a mixed bash/jq/heredoc pipeline (an earlier bash-heredoc attempt hit a syntax error from nested single quotes)"
    - "Confirmed byte-identity between a review document's inline body and its standalone file with a small python regex extraction rather than eyeballing a diff, matching the plan's own byte-identical requirement"

key-files:
  created:
    - .planning/phases/187-answered-reports/evidence/bodies/187-gh60.md
    - .planning/phases/187-answered-reports/evidence/bodies/187-gh62.md
    - .planning/phases/187-answered-reports/187-UPSTREAM-REPLIES.md
    - .planning/phases/187-answered-reports/evidence/187-05-issue-state-before.json
    - .planning/phases/187-answered-reports/evidence/187-05-draft-link-check.txt
    - .planning/phases/187-answered-reports/evidence/187-05-body-hashes.txt

key-decisions:
  - "Named `fix:released` as the candidate label for gh#60's close and `cause:firmware` as the candidate for gh#62, per RESEARCH §8.3's analysis that these are the only defensible taxonomy fits — but flagged both explicitly in 187-UPSTREAM-REPLIES.md's Operator Review section as candidates for the operator to confirm or change at the 187-07/187-08 gates, per Open Question 1's resolution. No label edit was made; both issues remain in their original label state."
  - "Worded gh#62's acknowledgement of gh#65/gh#66 as 'open' with a maintainer datasheet cross-check dated 2026-09-10, never 'unanswered' — and flagged the reword explicitly in the review document per DRIFT-2 and Open Question 2's resolution, so the operator can decide at the gate whether the line survives at all."
  - "Used a small python script (not a bash/jq heredoc) to build the issue-state evidence file after a bash quoting failure, to keep the API-derived JSON exact rather than hand-transcribed."

requirements-completed: []

coverage:
  - id: D1
    description: "Pre-post state of all six issues (9, 23, 28, 31, 60, 62) plus the pinnedIssues read captured to disk, with the three drift facts re-verified against the live API rather than inherited from CONTEXT.md"
    verification:
      - kind: other
        ref: "python3 -c \"print(open('evidence/187-05-issue-state-before.json').read().count('\\\"state\\\"'))\" -> 12 (>=6); gh issue view 65/66 --json comments --jq '.comments|length' -> 1/1; gh issue view 68 --json state -> OPEN"
        status: pass
    human_judgment: false
  - id: D2
    description: "evidence/bodies/187-gh60.md and 187-gh62.md drafted as bare markdown bodies (no frontmatter, no title heading) answering the reporters' own questions with the pinned-SHA permalinks, the read app version, and no dev-test re-run ask"
    requirement: "REPLY-03, REPLY-04"
    verification:
      - kind: other
        ref: "head -1 of both files grep for ^(---|#) -> 0; grep -E 'blob/[0-9a-f]{40}/' both files -> 2; grep -F <pinned SHA> both files -> 2; grep -F <app version 3.0.0b39> both files -> 2; grep -i unanswered both files -> 0"
        status: pass
    human_judgment: true
    rationale: "Whether each body faithfully carries the substance of its source material (the four REPLY-03 load-bearing claims, the honest gh#60 limit) in a register a reporter can read is a judgment call the plan's own success criteria route to the operator gates in 187-07/187-08, not something a grep can certify."
  - id: D3
    description: "187-UPSTREAM-REPLIES.md opened with a per-issue PENDING OPERATOR REVIEW status line (D-16), a five-issue Dispositions table written before the remaining three bodies exist, and gh#60/gh#62 sections carrying their bodies inline byte-identically to the standalone files"
    verification:
      - kind: other
        ref: "grep -c 'PENDING OPERATOR REVIEW' -> 7 (>=5); python3 regex extraction of each ## gh#N inline body vs its file -> MATCH for both gh60 (2268 bytes) and gh62 (3914 bytes)"
        status: pass
    human_judgment: false
  - id: D4
    description: "Every URL in both drafts (3 distinct URLs: 2 commit-SHA permalinks, 1 issue cross-link) resolved at the pinned SHA with content confirmed, recorded in evidence/187-05-draft-link-check.txt; both bodies hash-bound in evidence/187-05-body-hashes.txt"
    verification:
      - kind: other
        ref: "gh api contents/...?ref=<pinned SHA> for both notes files -> 200, decoded content contains the targeted heading at the expected line; gh api issues/68 -> OPEN; grep -c 'sha256(' body-hashes.txt -> 2, both match sha256sum of the files on disk"
        status: pass
    human_judgment: false
  - id: D5
    description: "Nothing posted, labelled, or closed — this plan writes to disk only"
    verification:
      - kind: other
        ref: "gh issue view 60/62 --json state,labels re-read after all three tasks -> unchanged from Task 1's before-state (OPEN/[enhancement] and OPEN/[] respectively); git status --short shows only the plan's own new files plus pre-existing untracked anything.txt/tmp/firestarter_app"
        status: pass
    human_judgment: false

duration: 22min
completed: 2026-09-12
status: complete
---

# Phase 187 Plan 05: Draft gh#60 and gh#62 reply bodies Summary

**Drafted the two reply bodies for the issues that carry no prior comment — gh#60's JP5 hazard confirmation and gh#62's AE29F2008 chip-erase equivalence verdict — as bare markdown posting payloads pinned to the one meta merge SHA (`ebd80b53b06b49678e41f12d31136f5b9d3edd26`) and naming the read app version (`3.0.0b39`), with every link resolved and both bodies hash-bound for their operator gates.**

## Performance

- **Duration:** 22 min
- **Started:** 2026-09-12T14:52:00Z (approx.)
- **Completed:** 2026-09-12T15:14:00Z (approx.)
- **Tasks:** 3
- **Files modified:** 6 (all created)

## Accomplishments

- Captured the live pre-post state of all six issues this phase touches (9, 23, 28, 31, 60, 62)
  from the API — state, `stateReason`, labels, comment count — plus the `pinnedIssues` GraphQL
  read, into `evidence/187-05-issue-state-before.json`.
- Re-verified, with command and output rather than inheriting from `CONTEXT.md`, the three facts a
  body could otherwise get wrong: gh#65 and gh#66 each carry exactly one comment dated
  2026-09-10 (a maintainer datasheet cross-check) and are OPEN, not unanswered; gh#68 is OPEN and
  names `AE29F2008` explicitly in its own body (twice — once naming the chip, once cross-linking
  gh#62 by name); gh#61 is CLOSED/`COMPLETED` with `chip:validated`. Also recorded that gh#67
  exists as gh#68's sibling with a distinct scope, so gh#62's body does not conflate the two.
- Drafted `evidence/bodies/187-gh60.md` (REPLY-04): answers AstoriaFloyd's own question in the
  settled words (writing and erasing energize socket pin 1; reading, verifying, blank-checking and
  `id` do not), confirms their JP5-detection limit claim by quoting the shipped `jp5_gate.py`
  hazard text and the JP5 silkscreen legend verbatim, states what shipped in the released app
  version, links `jumper-display-ground-truth.md` at the pinned SHA with the copied anchor, and
  states the close disposition with a candidate label swap (`fix:released` for `enhancement`).
- Drafted `evidence/bodies/187-gh62.md` (REPLY-03): tells dim20 plainly, in the first two
  sentences, that both halves of the equivalence verdict are true at once — the classification is
  correct and the reporter is correct that the silicon can be chip-erased — then carries all four
  load-bearing claims of the classification verdict's REPLY-03 section (the erase was real; it
  used the documented six-cycle sequence; it was benign only by coincidence of pinout and voltage
  class; `--force` identity forgery is not a safe workaround in general) in substance, states
  where the actually-wanted capability stands (backlog 999.63, unbuilt, with the boot-block
  caveat, no timeline), cross-links gh#68 per D-12 without widening into gh#67's scope, notes
  gh#61's PASS context, links the verdict note at the pinned SHA, states the stays-open
  disposition with a candidate label, and acknowledges gh#65/gh#66 as open (never "unanswered").
- Opened `187-UPSTREAM-REPLIES.md`: a per-issue `PENDING OPERATOR REVIEW` status line for all five
  replied-to issues (D-16), a five-issue Dispositions table written before the remaining three
  bodies exist, an Operator Review section explicitly flagging the two candidate label choices and
  the gh#65/#66 rewording as decisions for the 187-07/187-08 gates rather than choices made here,
  a Pre-post state section, and `## gh#60` / `## gh#62` sections carrying each body inline
  byte-identically to its standalone file (confirmed by script, not by eye).
- Resolved all three distinct URLs across both bodies against the live GitHub API: both
  commit-SHA permalinks confirmed to exist at the pinned SHA with their decoded content proven to
  contain the exact heading each anchor targets; the gh#68 issue cross-link confirmed OPEN.
  Recorded all three, with method and result, in `evidence/187-05-draft-link-check.txt`, noting
  explicitly that neither permalink resolves at or before the meta merge's parent commit (the
  silent-stub failure mode `187-RESEARCH.md` §7.3 warns about).
- Wrote `evidence/187-05-body-hashes.txt` with one `sha256(<path>) = <hash>` line per body, for
  the 187-07/187-08 approval gates to bind against.
- Confirmed after all three tasks that neither gh#60 nor gh#62 changed state or labels on the live
  tracker, and that `git status` shows nothing beyond this plan's own new files plus the
  pre-existing untracked `anything.txt`/`tmp/`/`firestarter_app` — nothing was posted, labelled,
  or closed.

## Task Commits

Each task was committed atomically:

1. **Task 1: Capture the live pre-post state of all six issues** - `101c4120` (docs)
2. **Task 2: Draft gh#60 and gh#62 bodies and open the review document** - `d2d0a8de` (docs)
3. **Task 3: Resolve every link in both drafts and hash-bind the bodies** - `de590fb6` (docs)

**Plan metadata:** committed alongside this SUMMARY (see final commit below).

## Files Created/Modified

- `.planning/phases/187-answered-reports/evidence/187-05-issue-state-before.json` - live pre-post
  state of all six issues, the pinnedIssues read, and the three re-verified drift facts
- `.planning/phases/187-answered-reports/evidence/bodies/187-gh60.md` - REPLY-04 posting payload
- `.planning/phases/187-answered-reports/evidence/bodies/187-gh62.md` - REPLY-03 posting payload
- `.planning/phases/187-answered-reports/187-UPSTREAM-REPLIES.md` - the review/approval document,
  opened with the per-issue gate, dispositions table, and the two drafted sections
- `.planning/phases/187-answered-reports/evidence/187-05-draft-link-check.txt` - all three URLs
  resolved at the pinned SHA, with content and anchor confirmation
- `.planning/phases/187-answered-reports/evidence/187-05-body-hashes.txt` - sha256 for both bodies

## Decisions Made

- Named `fix:released` (gh#60) and `cause:firmware` (gh#62) as candidate labels in each body,
  matching `187-RESEARCH.md` §8.3's analysis of the only defensible taxonomy fits — but flagged
  both explicitly as candidates for the operator to confirm or change at the 187-07/187-08 gates,
  per the plan's carried-forward Open Question 1. No label edit was made by this plan.
- Worded gh#62's one-line acknowledgement of gh#65/gh#66 as "open" (with the maintainer
  cross-check date), never "unanswered" — the word CONTEXT.md's Deferred Ideas block used before
  the drift was discovered — and flagged the reword in the review document per DRIFT-2/Open
  Question 2, so the operator can decide at the gate whether the acknowledgement survives at all.
- Built the issue-state evidence file with a small python script after an initial bash/jq heredoc
  attempt hit a quoting syntax error, to keep the API JSON exact rather than hand-transcribed.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

- An initial attempt to build `evidence/187-05-issue-state-before.json` via a bash heredoc mixing
  single-quoted `jq` filters inside an outer single-quoted heredoc hit a shell syntax error before
  any file was written. Rewritten as a small python script calling `gh issue view --json` per
  issue and writing structured output directly — no data was lost, and the corrected approach
  produced output that was independently cross-checked against direct `gh` calls for the same six
  issues (Task 1's `<verify>` legs).

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- `187-06` extends this same `187-UPSTREAM-REPLIES.md` with gh#23/#28/#31's bodies and evidence,
  without altering the Dispositions table's rows (only the "drafted below" / "drafted by 187-06"
  annotations need correcting, which 187-06 owns).
- `187-07` and `187-08` have everything they need to run the per-issue operator gates for gh#60
  and gh#62 respectively: the hash-bound bodies, the flagged label candidates, and the flagged
  gh#65/#66 rewording — all recorded rather than pre-decided.
- No blockers. Nothing public changed; the tracker is exactly as Task 1 found it.

## Self-Check: PASSED

- `.planning/phases/187-answered-reports/evidence/bodies/187-gh60.md` — FOUND
- `.planning/phases/187-answered-reports/evidence/bodies/187-gh62.md` — FOUND
- `.planning/phases/187-answered-reports/187-UPSTREAM-REPLIES.md` — FOUND
- `.planning/phases/187-answered-reports/evidence/187-05-issue-state-before.json` — FOUND
- `.planning/phases/187-answered-reports/evidence/187-05-draft-link-check.txt` — FOUND
- `.planning/phases/187-answered-reports/evidence/187-05-body-hashes.txt` — FOUND
- Commit `101c4120` — FOUND
- Commit `d2d0a8de` — FOUND
- Commit `de590fb6` — FOUND
- All Task 1-3 `<verify>` legs and acceptance criteria re-run and passed (see body above);
  gh#60/gh#62 confirmed unchanged on the live tracker after all three tasks.

---
*Phase: 187-answered-reports*
*Completed: 2026-09-12*
