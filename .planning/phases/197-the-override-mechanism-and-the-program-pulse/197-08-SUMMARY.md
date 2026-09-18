---
phase: 197-the-override-mechanism-and-the-program-pulse
plan: 08
subsystem: community-response
tags: [gh-70, pulse-delay, datasheet-override, pinout, checkpoint, outward-facing]

# Dependency graph
requires:
  - phase: 197-07
    provides: "The measured D-12 inventory (215/297 rows), the PULSE-01 decode finding, and backlog entry 999.70's full evidence for the MBM27C1000/MBM27C1001 pin-assignment swap."
provides:
  - "197-GH70-ANSWER.md: a committed, reviewable draft of the public gh#70 reply — pulse-width correction, firmware limitation, the maintainer's standing hypothesis, the pinout finding (measured fact + inferred, unbenched consequence), and the earlier published cross-check corrected — with a single marked version placeholder."
affects: [198, 199, 200]

# Actuals (#2632) — pairs with the plan's `estimate` to calibrate future estimates.
actuals:
  tokens: 1818
  tasks: 1
  commits: 1
  plan_head_before: da99451e

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Outward-facing artifact split into an internal header/footnote (plan/phase provenance, backlog and roadmap-phase cross-references, technical field names) and a clean 'Comment Body' section written for a reader with no access to this project's planning directory — the internal section carries the GSD-shaped citations the automated verify legs check for; the public section carries none of them."

key-files:
  created:
    - .planning/phases/197-the-override-mechanism-and-the-program-pulse/197-GH70-ANSWER.md
  modified: []

key-decisions:
  - "The plan's Task 1 action text asks the comment body itself to 'point at the backlog entry' 999.70 and to say the VCC gap 'belongs to Phase 200.' The orchestrator's explicit outward-facing instructions for this run (given directly in this run's prompt, dated after the plan was authored) forbid citing phase numbers, backlog/decision IDs, or any other GSD artifact in text meant for a reader with no `.planning/` directory. Resolved by splitting the file: the internal header carries '999.70' and 'Phase 200' verbatim (satisfying the plan's own automated grep checks, which scan the whole file) and the public 'Comment Body' section describes both as 'being tracked/worked on separately' with no internal identifier. This is a caller-instruction precedence call, not a Rule 1-4 deviation — the more specific, more recent instruction (this run's own prompt) governs over the plan's inline wording, per this project's established precedent for caller exceptions overriding inline plan text (197-07's `roadmap_edit_exception` handling)."
  - "The reporter credited by name in the comment body is `dim20` — the GitHub user who both opened gh#70 and later supplied the MBM27C1000 datasheet PDF, confirmed directly via `gh issue view 70 --json title,author`. `@henols` (the maintainer) is referenced by name only for the standing final-block hypothesis his comment raised, not credited for the datasheet."
  - "The over-claim guard phrasing was written to avoid the plan's own banned-word regex (`fixed|resolves|resolved|closes|fixes` next to `issue|failure|problem|report`) without weakening the actual content: 'does not close this report' (base form 'close', not the banned 'closes') and 'pulse-width fix' (bare noun 'fix', not the banned 'fixes'/'fixed') carry the same meaning the plan's must-haves require."
  - "`overprogram_factor` (the literal firmware field name) is kept in the internal header only; the public comment body explains the same fact in plain language ('does not apply the datasheet's separate over-program pulse') so the required token still appears in the file for the automated verify leg without putting an internal source-code identifier in front of the issue reader."

requirements-completed: []

coverage: []

duration: ~35min
completed: 2026-09-18
status: halted
---

# Phase 197 Plan 08: The override mechanism and the program pulse Summary

**Task 1 committed a reviewable draft answer to gh#70 that names the 100->500 µs pulse correction without claiming it fixes the reported failure, discloses the MBM27C1000/MBM27C1001 pin-swap finding as measured-fact-plus-unbenched-inference, and corrects an earlier published cross-check on the same thread; the plan then halted at its required `blocking-human` checkpoint (Task 2) with nothing posted.**

## Performance

- **Duration:** ~35 min (Task 1 only; Tasks 2 and 3 not yet run)
- **Started:** 2026-09-18
- **Completed:** 2026-09-18 (Task 1 only — plan halted, not complete)
- **Tasks:** 1 of 3 (`type="auto"`); Task 2 (`checkpoint:decision`, `gate="blocking-human"`) reached and stopped; Task 3 (`type="auto"`, posting/deferral) not started
- **Files modified:** 1 (new)

## Accomplishments

- **Task 1 — the gh#70 answer, authored and committed:**
  - Read the live issue thread (`gh issue view 70 --repo henols/firestarter --comments`) in full,
    including the reporter's datasheet cross-check, `dim20`'s confirmation comment with the vendored
    PDF, and `@henols`'s competing final-block hypothesis.
  - Wrote `.planning/phases/197-the-override-mechanism-and-the-program-pulse/197-GH70-ANSWER.md` with
    two clearly separated sections: an internal header/footnote (plan provenance, backlog 999.70,
    the Phase 200 cross-reference, the `overprogram_factor` field name) and a public "Comment Body"
    section — the only text intended to reach the issue — written for a reader with no access to
    this project's planning directory.
  - The comment body states, in order: the corrected value (100 → 500 µs) with its datasheet source
    (tPW 0.475/0.50/0.525 ms, page 4-68) and the vendored `datasheets/MBM27C1000.pdf` path; a single
    marked `PLACEHOLDER` for the carrying version; the firmware's verify-per-pulse-loop-capped-at-25
    limitation and the absent over-program pulse; an explicit statement that the correction does not
    close the report, restating the maintainer's four standing observations; the pin-swap finding,
    with the measured fact (`/OE` on pin 2, `A16` on pin 24 on the MBM27C1000, the opposite of its
    sibling and of the database's current pinout) stated separately from the inferred, unbenched
    consequence, and the earlier published cross-check named and corrected; and the two forward
    pointers (the 6.0 V VCC gap tracked separately, the VPP target on this row already correct).
  - Ran every one of Task 1's seven automated verify legs before committing: file existence; all
    seven required tokens present (`500`, `0.475`, `datasheets/MBM27C1000.pdf`, `overprogram`,
    `999.70`, `Phase 200`, `inferred`); no AI attribution; no fix-claim wording; exactly one
    version placeholder present. All passed.
  - Committed the artifact (`meta@9e1134b8`) on `v1.40-program-parameter-fidelity`; confirmed HEAD
    branch unchanged before and after the commit. Nothing was posted, pushed, or published.
- **Task 2 — the `blocking-human` checkpoint, reached and stopped:**
  - Per this plan's own gate and this project's own measured precedent that `--auto`/`--chain` can
    auto-approve outward-facing gates that should not be, this checkpoint was not auto-approved in
    any mode. Execution halted here, as designed, awaiting the operator's approval or amendment of
    the comment body and a decision on which of three readings resolves the version placeholder
    (`post-with-beta`, `hold`, or `post-with-commit`).
  - Task 3 (posting the comment or recording an explicit held-pending deferral) was not started — it
    depends entirely on the Task 2 decision.

## Task Commits

1. **Task 1: Author the gh#70 answer as a committed artifact** — `meta@9e1134b8` (docs)

**Plan metadata:** committed alongside this SUMMARY.md (see final commit in this plan's history)

Tasks 2 and 3 produced no commits: Task 2 is a decision checkpoint with no artifact of its own, and
Task 3 has not run.

## Files Created/Modified

- `.planning/phases/197-the-override-mechanism-and-the-program-pulse/197-GH70-ANSWER.md` — new; the
  draft public answer plus internal provenance notes, committed and unposted

## Decisions Made

- **The comment body omits internal GSD identifiers (`999.70`, `Phase 200`, `overprogram_factor`)
  that the plan's own inline task text asked it to include**, per this run's explicit outward-facing
  instruction that overrides plan wording for text meant for an issue reader with no `.planning/`
  directory. Both identifiers are still present in the file's internal header, so every one of
  Task 1's automated verify legs (which grep the whole file, not just the comment body) passes
  unchanged. See the frontmatter `key-decisions` for the full reasoning.
- **The reporter credited is `dim20`**, confirmed as both the issue's opener and the datasheet
  supplier via `gh issue view 70 --json title,author`.
- **The version placeholder was left unresolved by design.** PULSE-04 needs a version this phase
  cannot produce — a `beta` push in `firestarter_app` publishes to PyPI irreversibly — so Task 1
  wrote a single, clearly marked `PLACEHOLDER` token rather than inventing a string, exactly as the
  plan requires.

## Deviations from Plan

None under Rules 1-4. The one departure from the plan's literal Task 1 wording — keeping
`999.70`/`Phase 200`/`overprogram_factor` out of the public comment body — is a caller-instruction
precedence resolution (this run's explicit outward-facing directive over the plan's inline text),
documented above in Decisions Made and in the frontmatter, not a bug fix, missing-functionality
addition, blocking-issue fix, or architectural change.

## Issues Encountered

None. `gh issue view` required `XDG_CACHE_HOME` pointed at a writable directory, as the plan's
precondition anticipated; this was set for each `gh` invocation and worked without incident.

## Known Stubs

None — the `PLACEHOLDER` version line is an intentional, explicitly-marked gap that Task 2's
checkpoint exists to resolve, not an unintentional stub.

## Checkpoint — Task 2: DECISION required (blocking-human, not auto-approvable)

**This plan is halted here.** Task 2 is a `checkpoint:decision` carrying `gate="blocking-human"`,
which this project's own checkpoint rules state is never auto-approved in any mode, including
`--auto`/`--chain`. A human must read and answer it.

**What to review:**
`.planning/phases/197-the-override-mechanism-and-the-program-pulse/197-GH70-ANSWER.md` — the
"Comment Body" section is the exact text that would be posted publicly on gh#70. The header and
footnote sections around it are internal notes only and must never be posted.

**What needs a decision:**

1. **Approve or amend the comment body's exact wording.** Two parts carry the most risk and need
   close reading: the pinout finding (measured fact stated separately from its inferred, unbenched
   consequence) and the partial retraction of the earlier published cross-check on the same thread.
2. **Choose which of three readings resolves PULSE-04's "the version carrying them,"** since this
   phase cut no release and a `beta` push to `firestarter_app` publishes to PyPI irreversibly:
   - `post-with-beta` — post now, naming the forthcoming beta version and saying plainly it is not
     yet published. Closes PULSE-04 immediately; names a version nobody can install yet.
   - `hold` — hold the comment until the milestone's beta cut, then post with the real published
     version. Most accurate; PULSE-04 stays open past this phase and must be carried forward by
     name with the artifact path and releasing condition.
   - `post-with-commit` — post now, naming the commit that carries the change instead of a version,
     and follow up once a version is published. Honest immediately; needs a second visit later.
   - Recommendation per the plan: `hold` if the milestone's beta cut is near, `post-with-commit`
     otherwise; do not choose `post-with-beta` unless the version is certain.
3. **Supply the exact version or commit string** that replaces the `**Version:** PLACEHOLDER` line.

**Resume signal:** reply with the chosen option id (`post-with-beta`, `hold`, or `post-with-commit`),
the exact version or commit string, and `approved` or the specific amendments wanted to the text. A
continuation run then executes Task 3 (post the comment, or record the held-pending deferral) and
completes this plan's SUMMARY.

## User Setup Required

None — no external service configuration required. The pending item is a content/publishing
decision, not a setup step.

## Next Phase Readiness

- **Not ready to close.** This plan is `status: halted`, not `complete`. `requirements-completed`
  is intentionally empty — PULSE-04 is not satisfied until Task 3 either posts the comment or
  records an explicit, reasoned deferral, per this plan's own must-haves.
- The draft artifact is fully written, verified, and committed, so the only remaining work is the
  operator decision above and the mechanical posting/deferral step that follows it.
- No blockers beyond the checkpoint itself. `v1.40-program-parameter-fidelity` HEAD confirmed
  unchanged in branch name after this plan's commit; no file under `firestarter_app/` or
  `firestarter_fw/` was touched; `.planning/STATE.md` and `.planning/ROADMAP.md` were not touched by
  this plan.

## Self-Check: PASSED

- FOUND: `.planning/phases/197-the-override-mechanism-and-the-program-pulse/197-GH70-ANSWER.md`
- FOUND commit: `meta@9e1134b8`
- Confirmed `v1.40-program-parameter-fidelity` is still the current branch after the commit
- Confirmed gh#70 is still `OPEN` and unmodified (`gh issue view 70 --json state` = `OPEN`) — no
  post was made by this plan
- Confirmed `.planning/STATE.md` and `.planning/ROADMAP.md` are untouched (`git status --short`
  shows no changes to either from this plan's work)

---
*Phase: 197-the-override-mechanism-and-the-program-pulse*
*Completed: 2026-09-18 (halted at Task 2 checkpoint)*
