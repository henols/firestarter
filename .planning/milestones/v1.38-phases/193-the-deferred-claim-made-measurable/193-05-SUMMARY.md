---
phase: 193-the-deferred-claim-made-measurable
plan: 05
subsystem: docs
tags: [claude-md, gitmodules, github-releases, gate-02, gate-03, disposition]

# Dependency graph
requires:
  - phase: 193-the-deferred-claim-made-measurable
    provides: "193-01's tools/adoption/pypi_version_share.sh and its live reading (GATE-01). 193-02's rewritten seed trigger_condition. 193-04's .planning/notes/gitmodules-archaeology-trap.md carrying both GATE-03 workarounds and the sync hazard."
provides:
  - "CLAUDE.md's ## Milestone close and branch protection section gains a fifth bullet: the meta repository must never publish a GitHub Release. The version-comparison mechanism is stated inline. The full walkthrough is cited by section heading, not duplicated."
  - "CLAUDE.md's ## Repository Structure paragraph corrected to name both tools/catalog/ and tools/adoption/. The phase's own tools/adoption/ addition had made the prior single-occupant claim false. A new paragraph points at the .gitmodules archaeology trap note."
  - "evidence/193-disposition.md — a criterion-by-criterion record answering all four ROADMAP Phase 193 success criteria against named artefacts and transcripts"
affects: []

# Actuals (#2632)
actuals:
  tokens: 2829
  tasks: 3
  commits: 5
plan_head_before: 4b7e70c43de36b53ae34be95ae93adabb272c95b

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "CLAUDE.md's existing pattern extended to a second rule (GATE-02): state the rule in-line, cite the mechanism in a note by section heading. The ship.md close procedure already used this pattern."
    - "A phase's own new artefact (tools/adoption/) falsified an existing sentence in CLAUDE.md. The correction lands in the same edit that adds the citation depending on it, not in a later cleanup."

key-files:
  created:
    - .planning/phases/193-the-deferred-claim-made-measurable/evidence/193-disposition.md
  modified:
    - CLAUDE.md

key-decisions:
  - "D-13/D-14: GATE-02's rule is stated in CLAUDE.md's milestone-close section with its mechanism written inline (the PEP 440 v1.36-parses-as-1.36 argument). The full walkthrough is cited by path and section heading (999.9-repo-rename-impact-analysis.md § 'Standing rule this must produce') rather than duplicated. This keeps one source of truth for the detailed argument."
  - "D-15: GATE-03's pointer lives in CLAUDE.md's repository-structure area, not the close section, because that area is an archaeology session's actual starting point. It names .planning/notes/gitmodules-archaeology-trap.md. The pointer states plainly that the trap does not bite today, because the old firmware slug still redirects, so a reader does not conclude their own clone is already broken."
  - "The pre-existing repository-structure paragraph's claim that meta tools/ 'now holds catalog/ alone' was corrected in the same edit that added the archaeology pointer. Plan 193-01's tools/adoption/ addition had already made that claim false. Every other fact in that paragraph — retirement dates, the 5426d7ef short sha, the closing bolded wiki-guard clause — was left byte-identical."
  - "New CLAUDE.md prose and evidence/193-disposition.md prose were split into shorter, semicolon-free sentences to satisfy the devcontainer's ASD-STE100 lint hook. The one pre-existing long, semicolon-joined sentence in CLAUDE.md's repository-structure paragraph was left untouched. The plan's environment_notes and 193-PATTERNS.md require preserving that paragraph's established dense, semicolon-and-em-dash style and require every other fact in it to stay byte-identical."
  - "All three tasks' file changes were committed in one commit, not three. This plan's own Task 3 action text says so directly: 'Commit the disposition and CLAUDE.md's two edits together on the current branch.' This follows the plan's explicit instruction; it is not a deviation from the default per-task commit protocol."

requirements-completed: [GATE-02, GATE-03]

coverage:
  - id: D1
    description: "The no-Releases-on-the-meta-repo rule is recorded in CLAUDE.md's milestone-close section with its mechanism stated inline (v1.36 parses as PEP 440 1.36, so 3.0.0b29 >= 1.36 reads true) and the full walkthrough cited by section heading, not restated"
    requirement: GATE-02
    verification:
      - kind: other
        ref: "grep -o -F over CLAUDE.md confirming '3.0.0b29', '1.36', 'Standing rule this must produce', and '.planning/notes/999.9-repo-rename-impact-analysis.md' are each present. The four pre-existing close-section bullets and the file's heading count are unchanged."
        status: pass
    human_judgment: false
  - id: D2
    description: "The .gitmodules archaeology trap has a pointer in CLAUDE.md's repository-structure area naming the note with both workarounds, stating the trap does not bite today, and the tools/ inventory sentence this phase itself falsified is corrected in the same edit"
    requirement: GATE-03
    verification:
      - kind: other
        ref: "grep -o -F over CLAUDE.md confirming 'tools/catalog', 'tools/adoption', '.gitmodules', 'v1.35', and '.planning/notes/gitmodules-archaeology-trap.md' are present. The prior 'now holds catalog/ alone' claim no longer appears."
        status: pass
    human_judgment: false
  - id: D3
    description: "evidence/193-disposition.md answers all four ROADMAP Phase 193 success criteria, each naming the artefact or transcript that supports it, and states plainly that the instrument's figures are a capture rather than a standing fact"
    requirement: null
    verification:
      - kind: other
        ref: "grep -c -E '^## Criterion [1-4]' returns 4. Each criterion's named artefacts are present (tools/adoption/pypi_version_share.sh, SEED-claim-firestarter-slug.md, 193-gate-01-instrument-run.txt, both 193-gate-03-*.txt transcripts, v1.35, 'Standing rule this must produce', 3.0.0b29). 'a capture' and 'not a standing fact' are both present."
        status: pass
    human_judgment: false

# Metrics
duration: 20min
completed: 2026-09-14
status: complete
---

# Phase 193 Plan 05: The No-Releases Rule, the Archaeology Pointer, and the Phase Disposition Summary

**Added the GATE-02 no-Releases rule and the GATE-03 `.gitmodules`-trap pointer to `CLAUDE.md`, and wrote the phase's four-criterion disposition record.**

## Performance

- **Duration:** ~20 min
- **Tasks:** 3
- **Files modified:** 2 (`CLAUDE.md` edited twice; `evidence/193-disposition.md` created)

## Accomplishments

- `CLAUDE.md`'s `## Milestone close and branch protection` section now carries a fifth bullet. It states the meta repository must never publish a GitHub Release. The PEP 440 version-parsing mechanism is stated inline. The full walkthrough is cited by section heading in `999.9-repo-rename-impact-analysis.md`, never duplicated.
- `CLAUDE.md`'s `## Repository Structure` paragraph now names both `tools/catalog/` and `tools/adoption/` as meta `tools/`'s occupants. This corrects the single-occupant claim this phase's own `tools/adoption/` addition had made false. A new paragraph right after it points at `.planning/notes/gitmodules-archaeology-trap.md` for the `.gitmodules` archaeology trap. It states plainly that the trap does not bite today, because the old firmware slug still redirects.
- `evidence/193-disposition.md` answers each of the phase's four ROADMAP success criteria in its own section. Each section names the artefact, seed file, or transcript that supports it. It closes with an honest-limits paragraph distinguishing capture from standing fact.

## Task Commits

All three tasks' changes were committed together in one commit, per this plan's own Task 3 instruction ("Commit the disposition and `CLAUDE.md`'s two edits together on the current branch"):

1. **Task 1: The no-Releases rule** — bullet added to `CLAUDE.md`.
2. **Task 2: The archaeology pointer and the corrected tools/ inventory** — two edits to `CLAUDE.md`.
3. **Task 3: The phase disposition record** — `evidence/193-disposition.md` written.

**Combined commit:** `e594466d` (docs(193-05): put the no-Releases rule and archaeology pointer into CLAUDE.md)

## Files Created/Modified

- `CLAUDE.md` — one new bullet in the milestone-close section (GATE-02). One corrected sentence plus one new paragraph in the repository-structure area (GATE-03). 77 → 80 lines.
- `.planning/phases/193-the-deferred-claim-made-measurable/evidence/193-disposition.md` — new. Criterion-by-criterion disposition record for all four ROADMAP Phase 193 success criteria.

## Decisions Made

See `key-decisions` in the frontmatter above: the D-13/D-14 citation-not-duplication choice, the D-15 pointer placement, the same-edit correction of the falsified `tools/` inventory sentence, the STE100 sentence-splitting scope, and the single combined commit per the plan's own instruction.

## Deviations from Plan

### Auto-fixed Issues

None. No bug, missing functionality, or blocking issue was found in the target files. Both items below concern the plan's own `<verify><automated>` commands. Each command produced a number different from what its `<fails_when>` clause expected, even though the underlying acceptance criteria it was meant to check are genuinely satisfied. These are documented as deviations in the plan's verification tooling, not as changes to the delivered artifacts.

**1. [Rule 1 - Bug in plan verify command] `grep -c` with multiple `-e` patterns counts matching lines, not total pattern occurrences**
- **Found during:** Task 1's fourth automated verify leg (`grep -c -F -e '3.0.0b29' -e 'Standing rule this must produce' -e '...999.9...md' CLAUDE.md`, expecting >= 3) and Task 2's third and fifth legs (`tools/adoption`/`tools/catalog` expecting >= 2; `5426d7ef`/`no automated wiki guard exists now` expecting >= 2).
- **Issue:** GNU/BSD `grep -c` counts the number of *matching lines*, not the number of pattern matches. The plan's own shape requirement for these bullets and paragraphs mandates a single unwrapped line ("a single line, no wrapping"). When all three (or two) required substrings sit on that one line, `grep -c` returns `1`, not `3` or `2`, even though every required substring is genuinely present.
- **Verification performed instead:** `grep -o -F -e ... CLAUDE.md | sort | uniq -c` confirmed each of `3.0.0b29`, `Standing rule this must produce`, `.planning/notes/999.9-repo-rename-impact-analysis.md`, `tools/adoption`, `tools/catalog`, `5426d7ef`, and `no automated wiki guard exists now` appears exactly once. This satisfies the plan's plain-English acceptance criteria, which require only that the substrings be present, not a specific `grep -c` count.
- **Files modified:** None. This is a defect in the plan's verify commands, not in `CLAUDE.md`.
- **Impact:** No change to the delivered bullet or paragraph text. The single-line shape the plan explicitly required is what makes `grep -c`'s per-line counting undercount. Rewriting the bullets across multiple lines to inflate the `grep -c` count would have violated the plan's own "single line, no wrapping" acceptance criterion, which would be a worse outcome.

**2. [Rule 1 - Bug in plan verify command] Task 2's heading-count verify leg expects 5, but `CLAUDE.md` had 6 top-level `## ` headings before this plan touched it**
- **Found during:** Task 2's final automated verify leg (`grep -c '^## ' CLAUDE.md`, expecting exactly `5`).
- **Issue:** `CLAUDE.md` has six `## ` headings before this plan runs: `Repository Structure`, `System Overview`, `Development Commands`, `Key Architecture Points`, `Source code comments — hard rule`, `Milestone close and branch protection`. This was verified by reading the file at the start of this plan, before any edit. This plan adds a paragraph and a bullet, not a heading, confirmed by inspecting the diff. So the count stays at 6 after this plan, not 5. The `5` baked into the verify leg appears to be a miscount made when the plan was authored.
- **Verification performed instead:** Confirmed no `## ` heading was added or removed, by diffing the heading list before and after. `grep -n '^## ' CLAUDE.md` gave the same six headings, at the same line offsets adjusted only by the two inserted lines above them.
- **Files modified:** None.
- **Impact:** No change to the delivered content. The plan's own acceptance-criteria prose for this leg — "this phase adds no heading to the file" — is satisfied. Only the specific expected number in the automated proxy check was wrong.

---

**Total deviations:** 0 changes to delivered artifacts. 2 documented defects in the plan's own `<verify>` automated commands, both `grep -c` counting or heading-count discrepancies, not implementation bugs.
**Impact on plan:** None on scope or content. `CLAUDE.md` and `evidence/193-disposition.md` satisfy every plain-English acceptance criterion in the plan. Only two of the automated proxy checks meant to confirm this printed numbers inconsistent with the shape the plan itself required.

## Issues Encountered

None beyond the deviations above. The devcontainer's ASD-STE100 lint hook flagged several long or semicolon-joined sentences in the newly authored prose, in both `CLAUDE.md`'s new pointer paragraph and `evidence/193-disposition.md`. All newly authored sentences were revised to comply. One pre-existing long, semicolon-joined sentence in `CLAUDE.md`'s repository-structure paragraph was left untouched. The plan's explicit instructions require it: "leave every other fact... byte-identical," and preserve the paragraph's "one dense unwrapped line... chained with semicolons" style (193-PATTERNS.md).

## User Setup Required

None. No external service configuration required.

## Next Phase Readiness

- Phase 193 is now feature-complete. All five plans (193-01 through 193-05) have committed SUMMARY.md files. GATE-01 was marked Complete at 193-02. GATE-02 and GATE-03 are marked Complete by this plan. GATE-02 was declared only by this plan. GATE-03 is a shared ID also declared by 193-03 and 193-04. `requirements.ready-ids` confirmed all three declaring plans have a SUMMARY.md before this plan marked it Complete.
- No blockers. `evidence/193-disposition.md`'s own honest-limits paragraph names the two things that remain deliberately unverified by construction: the instrument's figures move daily, and the post-claim failure shape cannot be tested without performing the destructive claim this milestone declines to perform.
- The milestone's next step is whatever `/gsd-verify-work` and `/gsd-complete-milestone` require for v1.38. This plan does not perform either.

## Self-Check: PASSED

- `CLAUDE.md` exists on disk with both edits present.
- `.planning/phases/193-the-deferred-claim-made-measurable/evidence/193-disposition.md` exists on disk.
- `.planning/phases/193-the-deferred-claim-made-measurable/193-05-SUMMARY.md` (this file) exists on disk.
- `git rev-list --count 4b7e70c4..HEAD` measures 5 commits for this plan: `e594466d` (production commit — CLAUDE.md and the disposition record), `eb8bd3ff` (metadata commit — SUMMARY, STATE.md, ROADMAP.md, REQUIREMENTS.md), `ebf74dc6` and `a58a774d` (two small self-check and actuals corrections to this SUMMARY), and the commit landing this final correction.
- All acceptance criteria in the plan's three tasks were independently re-verified after the two documented plan-verify-command defects (see Deviations above), using `grep -o` in place of the miscounting `grep -c` legs, and by inspecting the heading list directly for the heading-count leg.

---
*Phase: 193-the-deferred-claim-made-measurable*
*Completed: 2026-09-14*
