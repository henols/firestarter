---
phase: 197-the-override-mechanism-and-the-program-pulse
plan: 08
subsystem: community-response
tags: [gh-70, pulse-delay, datasheet-override, pinout, checkpoint, outward-facing, deferred]

# Dependency graph
requires:
  - phase: 197-07
    provides: "The measured D-12 inventory (215/297 rows), the PULSE-01 decode finding, and backlog entry 999.70's full evidence for the MBM27C1000/MBM27C1001 pin-assignment swap."
provides:
  - "197-GH70-ANSWER.md: a committed, operator-approved draft of the public gh#70 reply — pulse-width correction, firmware limitation, the maintainer's standing hypothesis, the pinout finding (measured fact + inferred, unbenched consequence), and the earlier published cross-check corrected — held pending the v1.40 beta cut per a recorded operator decision, with an explicit deferral record naming what releases the hold and the exact posting steps."
affects: [198, 199, 200]

# Actuals (#2632) — pairs with the plan's `estimate` to calibrate future estimates.
actuals:
  tokens: 2400
  tasks: 3
  commits: 4
  plan_head_before: da99451e

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Outward-facing artifact split into an internal header/footnote (plan/phase provenance, backlog and roadmap-phase cross-references, technical field names, and a held-pending deferral record) and a clean 'Comment Body' section written for a reader with no access to this project's planning directory — the internal section carries the GSD-shaped citations the automated verify legs check for; the public section carries none of them."
    - "A `blocking-human` checkpoint::decision resolved by an operator answer recorded verbatim in the SUMMARY, with the plan's own three named options (`post-with-beta`, `hold`, `post-with-commit`) used as the resolution vocabulary rather than a paraphrase."

key-files:
  created:
    - .planning/phases/197-the-override-mechanism-and-the-program-pulse/197-GH70-ANSWER.md
  modified: []

key-decisions:
  - "The plan's Task 1 action text asks the comment body itself to 'point at the backlog entry' 999.70 and to say the VCC gap 'belongs to Phase 200.' The orchestrator's explicit outward-facing instructions for this run (given directly in this run's prompt, dated after the plan was authored) forbid citing phase numbers, backlog/decision IDs, or any other GSD artifact in text meant for a reader with no `.planning/` directory. Resolved by splitting the file: the internal header carries '999.70' and 'Phase 200' verbatim (satisfying the plan's own automated grep checks, which scan the whole file) and the public 'Comment Body' section describes both as 'being tracked/worked on separately' with no internal identifier. This is a caller-instruction precedence call, not a Rule 1-4 deviation — the more specific, more recent instruction (this run's own prompt) governs over the plan's inline wording, per this project's established precedent for caller exceptions overriding inline plan text (197-07's `roadmap_edit_exception` handling)."
  - "The reporter credited by name in the comment body is `dim20` — the GitHub user who both opened gh#70 and later supplied the MBM27C1000 datasheet PDF, confirmed directly via `gh issue view 70 --json title,author`. `@henols` (the maintainer) is referenced by name only for the standing final-block hypothesis his comment raised, not credited for the datasheet."
  - "The over-claim guard phrasing was written to avoid the plan's own banned-word regex (`fixed|resolves|resolved|closes|fixes` next to `issue|failure|problem|report`) without weakening the actual content: 'does not close this report' (base form 'close', not the banned 'closes') and 'pulse-width fix' (bare noun 'fix', not the banned 'fixes'/'fixed') carry the same meaning the plan's must-haves require."
  - "`overprogram_factor` (the literal firmware field name) is kept in the internal header only; the public comment body explains the same fact in plain language ('does not apply the datasheet's separate over-program pulse') so the required token still appears in the file for the automated verify leg without putting an internal source-code identifier in front of the issue reader."
  - "OPERATOR DECISION recorded 2026-09-18, verbatim in effect (paraphrased here only for frontmatter brevity — see the '## Checkpoint — Task 2' section below for the full text): publication route is `hold`, not `post-with-beta` or `post-with-commit`. Reason: `v1.40-program-parameter-fidelity` has no upstream and sits 14 commits (`firestarter_app`) / 41 commits (meta) ahead of `origin/beta`; `git branch -r --contains` returns nothing for it in either repository, so any version or commit string named now would be unresolvable to a reader. `hold` is the only route on which every claim in the comment body is true at the moment it posts."
  - "OPERATOR DECISION, one text amendment approved and only one: the 'What changed' sentence claiming the datasheet PDF 'is committed to this project's repository at `datasheets/MBM27C1000.pdf` so anyone can check it directly' was replaced with wording that keeps the 500 µs correction and the tPW/page-4-68 citation but drops the claim about where the file lives — that claim advertised redistributing a vendor PDF and was also false until the branch is pushed. The proposed 215-row unverified-pulse-width paragraph was explicitly NOT added; no other wording in the comment body was changed."
  - "The `**Version:** PLACEHOLDER` line was resolved, under `hold`, to a plain statement that the version is held pending the v1.40 beta cut and will be filled in before posting — not to any version or commit string, since none exists yet and naming one would be false. This satisfies the plan's Task 3 must-have that the placeholder be resolved without requiring an actual post."
  - "PULSE-04 is explicitly carried forward, not marked complete. The requirement needs 'the version carrying' the correction, which does not exist inside this phase; the held-pending deferral in `197-GH70-ANSWER.md` names the artifact, the reason, the releasing event (the v1.40 beta cut), and the exact four steps to take at that point, so the deferral is a decision on record rather than a gap nobody noticed."

requirements-completed: []

coverage: []

duration: ~50min
completed: 2026-09-18
status: complete
---

# Phase 197 Plan 08: The override mechanism and the program pulse Summary

**Task 1 authored a reviewable draft answer to gh#70; the operator approved it with one wording amendment and chose to hold posting until the v1.40 beta cut rather than post-with-beta or post-with-commit, because the milestone branch has no upstream in either repository and names nothing a reader could resolve today. Task 3 applied that amendment, resolved the version placeholder honestly under `hold`, and recorded an explicit held-pending deferral — naming what releases the hold and the exact posting steps — so PULSE-04 is a decided deferral, not a silent gap. Nothing was posted, pushed, or published; gh#70 is unchanged.**

## Performance

- **Duration:** ~50 min total (Task 1 ~35 min in the prior session; Task 2 decision + Task 3 execution ~15 min in this continuation)
- **Started:** 2026-09-18
- **Completed:** 2026-09-18
- **Tasks:** 3 of 3 (`type="auto"` x2, `checkpoint:decision` x1) — all complete
- **Files modified:** 1 (created in Task 1, amended in Task 3)

## Accomplishments

- **Task 1 — the gh#70 answer, authored and committed** (prior session, unchanged by this continuation):
  - Read the live issue thread in full, including the reporter's datasheet cross-check, `dim20`'s
    confirmation comment with the vendored PDF, and `@henols`'s competing final-block hypothesis.
  - Wrote `.planning/phases/197-the-override-mechanism-and-the-program-pulse/197-GH70-ANSWER.md`
    with an internal header/footnote and a public "Comment Body" section.
  - Ran all seven of Task 1's automated verify legs before committing; all passed.
  - Committed the artifact (`meta@9e1134b8`); nothing posted.
- **Task 2 — the `blocking-human` checkpoint, answered by the operator (2026-09-18):**
  - The operator reviewed the draft and chose `hold` over `post-with-beta` and `post-with-commit`,
    for the reason recorded verbatim below.
  - The operator approved the comment body as written except for one sentence, which they supplied
    exact replacement wording for.
  - Full decision text is recorded in "## Checkpoint — Task 2" below.
- **Task 3 — the amendment applied and the deferral recorded:**
  - Replaced the PDF-vendoring sentence in "What changed" with the operator-supplied wording that
    keeps the 500 µs correction and its tPW/page-4-68 citation but drops the claim about where the
    file now lives.
  - Resolved `**Version:** PLACEHOLDER` to a plain, honest statement that the version is held
    pending the v1.40 beta cut, naming no version or commit string that does not yet exist.
  - Added a "## Held-pending deferral (internal — do not post)" section to `197-GH70-ANSWER.md`
    recording: what is held (the entire public comment body), why (nothing pushed, no resolvable
    version or commit), what releases the hold (the v1.40 beta cut), and the exact four steps to
    take at that point (substitute the version, re-run the no-over-claim/no-attribution checks,
    post only the "## Comment Body" section, record the returned URL and close PULSE-04).
  - Re-ran all of Task 3's automated verify legs against the final text: no unresolved placeholder,
    no AI attribution, no over-claim, and the required "held pending" token present. All passed.
  - Confirmed read-only via `gh issue view 70 --repo henols/firestarter --json state,comments` that
    gh#70 is still `OPEN` with 3 comments — unchanged by this plan. No `gh issue comment`, no push,
    no label or state change was made.
  - Committed the amended artifact (`meta@af2b2091`) on `v1.40-program-parameter-fidelity`; confirmed
    HEAD branch unchanged before and after.

## Task Commits

1. **Task 1: Author the gh#70 answer as a committed artifact** — `meta@9e1134b8` (docs)
2. **Task 2: DECISION checkpoint** — no commit of its own; the decision is recorded in this SUMMARY
3. **Task 3: Apply the amendment and record the held-pending deferral** — `meta@af2b2091` (docs)

Interstitial halt-record commit from the prior session: `meta@f2d94a42` (docs — halt at the Task 2
checkpoint, recording Task 1's draft).

**Plan metadata:** this SUMMARY.md, committed in the plan's final metadata commit.

## Files Created/Modified

- `.planning/phases/197-the-override-mechanism-and-the-program-pulse/197-GH70-ANSWER.md` — created
  in Task 1 (draft, unposted); amended in Task 3 (operator's approved wording change, honest version
  resolution under `hold`, and the held-pending deferral record). Still unposted.

## Decisions Made

See frontmatter `key-decisions` for the full list, including the caller-instruction precedence call
from Task 1 and the reporter-credit confirmation. The decisions made in this continuation:

- **The operator chose `hold`, recorded verbatim 2026-09-18:**

  > **1. Publication route: `hold`.**
  > Hold the comment until the v1.40 beta cut, then post naming the real published version. Record
  > this as a held-pending deferral. DO NOT POST ANYTHING NOW.
  >
  > The operator's reason, which you should record: nothing is pushed. The branch
  > `v1.40-program-parameter-fidelity` has NO upstream and sits 14 commits (firestarter_app) and 41
  > commits (meta) ahead of `origin/beta`. So `post-with-beta` would name a version that does not
  > exist, and `post-with-commit` would name a commit a reader cannot resolve either — the
  > orchestrator verified `git branch -r --contains` returns nothing for it. `hold` is the only
  > route on which every claim in the draft is true at the moment it posts.
  >
  > **2. One text amendment: soften the PDF-vendoring line.**
  > The operator did NOT approve the body as-is and did NOT want the 215-row addition. Make exactly
  > this one change and no other.
  >
  > Replace this sentence in the `## Comment Body` section:
  >
  > > That value is now corrected to 500 µs, taken directly from that table, and the datasheet PDF
  > > you supplied is committed to this project's repository at `datasheets/MBM27C1000.pdf` so
  > > anyone can check it directly.
  >
  > with wording that keeps the correction and the citation but drops the claim about where the
  > file now lives — it advertises redistributing a vendor PDF, and it is also FALSE until the
  > branch is pushed.
  >
  > Do not add the 215-row paragraph. Do not make any other wording change. Everything else in the
  > comment body was reviewed and approved as it stands.

- **The version placeholder was resolved honestly, not by manufacturing a string.** Under `hold`,
  the correct resolution is a statement that the version will be supplied when posting occurs, not
  a version or commit identifier — both were rejected options and neither exists yet.
- **PULSE-04 is not marked complete.** It is explicitly carried forward as a decided deferral with
  the artifact path, the reason, the releasing event, and the exact steps to satisfy it later — all
  recorded in `197-GH70-ANSWER.md`'s "## Held-pending deferral" section.

## Deviations from Plan

None under Rules 1-4. Task 3's action text describes three branches (`post-with-beta`,
`post-with-commit`, `hold`); the operator's decision selected the `hold` branch exactly as the plan
anticipated, including its explicit instruction to "make the carry-forward visible rather than
implicit." No plan wording was overridden in Task 3; the caller-instruction precedence resolution
from Task 1 (public comment body omitting GSD identifiers) is unchanged and documented above.

## Issues Encountered

None. The read-only `gh issue view` confirmation in Task 3 required `XDG_CACHE_HOME` pointed at a
writable directory, as in Task 1; this was set for the invocation and worked without incident. No
`gh issue comment`, `gh pr`, `gh api` write, label change, or issue state change was made at any
point in this plan.

## Known Stubs

None. The version line in the comment body is an intentional, explicitly-marked hold statement — not
an unintentional stub — and it is paired with a deferral record that names exactly what resolves it.

## Checkpoint — Task 2: RESOLVED (2026-09-18)

**This plan's `blocking-human` checkpoint was answered by the operator, not auto-approved.** Per this
project's own checkpoint rules (`gate="blocking-human"` is never auto-approved in any mode, including
`--auto`/`--chain`), the prior session halted here and a human read and answered it.

**Decision recorded verbatim** — see "## Decisions Made" above for the full operator text. In
summary: option `hold` was chosen over `post-with-beta` and `post-with-commit`; one text amendment
(the PDF-vendoring sentence) was approved and applied; the proposed 215-row paragraph was explicitly
rejected; everything else in the comment body was approved as written.

**Resolution:** Task 3 (this continuation) applied the amendment, resolved the version placeholder
honestly under `hold`, and recorded the held-pending deferral. See "## Accomplishments" and "## Files
Created/Modified" above.

## User Setup Required

None — no external service configuration required. The remaining action (posting the comment) is a
future step gated on the v1.40 beta cut, recorded as a deferral, not a setup step.

## Next Phase Readiness

- **Plan complete.** All three tasks (Task 1, Task 2's decision, Task 3) are finished. `status:
  complete` in this SUMMARY's frontmatter.
- **PULSE-04 is NOT satisfied by this plan and is NOT marked complete** in `requirements-completed`
  or in `.planning/REQUIREMENTS.md`. It is explicitly carried forward: the artifact is
  `.planning/phases/197-the-override-mechanism-and-the-program-pulse/197-GH70-ANSWER.md`, the
  releasing event is the v1.40 beta cut, and the exact four steps to satisfy it are recorded in that
  file's "## Held-pending deferral" section. Whoever closes the v1.40 milestone should read that
  section before treating PULSE-04 as done.
- **No blockers.** `v1.40-program-parameter-fidelity` HEAD confirmed unchanged in branch name after
  both this plan's commits; no file under `firestarter_app/` or `firestarter_fw/` was touched;
  `.planning/STATE.md` and `.planning/ROADMAP.md` were not touched by this plan; gh#70 remains
  `OPEN` with 3 comments, unmodified.

## Self-Check: PASSED

- FOUND: `.planning/phases/197-the-override-mechanism-and-the-program-pulse/197-GH70-ANSWER.md`
- FOUND commit: `meta@9e1134b8`
- FOUND commit: `meta@f2d94a42`
- FOUND commit: `meta@af2b2091`
- Confirmed `v1.40-program-parameter-fidelity` is still the current branch after every commit in
  this plan
- Confirmed gh#70 is still `OPEN` with 3 comments (`gh issue view 70 --json state,comments`) — no
  post was made by this plan, at any point
- Confirmed `.planning/STATE.md` and `.planning/ROADMAP.md` are untouched by this plan (`git status
  --short` shows no changes to either)
- Confirmed the amended `197-GH70-ANSWER.md` contains no `PLACEHOLDER`/`<VERSION>`/`TO BE SUPPLIED`
  token, no AI attribution, no over-claim wording, and does contain the required "held pending" token
- Confirmed the public "## Comment Body" section no longer claims the PDF is committed to
  `datasheets/MBM27C1000.pdf`, and does not contain the rejected 215-row paragraph

---
*Phase: 197-the-override-mechanism-and-the-program-pulse*
*Completed: 2026-09-18*
