---
phase: 185-records-and-checks-that-are-current
plan: 06
subsystem: tooling
tags: [ci-retirement, github-actions, requirements-amendment, roadmap-amendment, gitlink]

# Dependency graph
requires:
  - phase: 185-05
    provides: "tools/catalog/sync_to_subrepos.sh's two repaired, genuinely-testable post-generation verifications — the sole surviving mechanism asserting cross-sub-repo catalog identity"
provides:
  - "CLAIM-08's verdict document, quoting the workflow's comment and both assertion steps verbatim before deletion"
  - "catalog-sync-check.yml deleted; meta repo runs no CI"
  - "CLAIM-08 and ROADMAP Phase 185 criterion 5 amended to the reachable form (D-02)"
  - "both sub-repo gitlinks advanced to this milestone's commits"
affects: []

actuals:
  tokens: 5852
  tasks: 3
  commits: 3

tech-stack:
  added: []
  patterns:
    - "verdict-document-before-deletion: quote the primary source into a .planning/notes/ record while it still exists, then delete it — the fourth note in this series after 182/183/184"

key-files:
  created:
    - .planning/notes/catalog-sync-check-retirement.md
  modified:
    - .planning/REQUIREMENTS.md
    - .planning/ROADMAP.md
    - firestarter (gitlink)
    - firestarter_app (gitlink)

key-decisions:
  - "Deleted .github/workflows/catalog-sync-check.yml outright per D-01 (operator's own decision against the orchestrator's recommendation to re-point the trigger at beta) — not re-pointed, not trigger-edited, not moved."
  - "Amended CLAIM-08 and ROADMAP Phase 185 criterion 5 by hand (D-02) rather than via any requirements/roadmap tooling verb, since those verbs reformat the whole file and this project's ROADMAP is hand-authored at ~6,300 lines. Both edits are section-scoped (REQUIREMENTS.md +10/-6 lines, ROADMAP.md +6/-2 lines over the Phase 185 section only)."
  - "Filed no successor guard and no backlog item for the residual cross-repo vendored-catalog-identity gap named in the verdict document, per D-04 — an explicit operator decision, not an oversight."
  - "Left all 92 .planning/ files citing the deleted workflow untouched — historical-by-intent, per this project's rule that .planning-internal citations record what was true when written and are not subject to the stale file:LINE repair rule."

requirements-completed: [CLAIM-08]

coverage:
  - id: D1
    description: "CLAIM-08's verdict document exists with all five required contents (cause, why the 2026-08-18 fix did not fix it, the workflow's own now-false comment corrected, the beta-fallback counterfactual, the residual gap named explicitly), quoted from the live workflow before deletion."
    requirement: "CLAIM-08"
    verification:
      - kind: other
        ref: "ls -l .planning/notes/catalog-sync-check-retirement.md (15056 bytes, >4000 byte floor)"
        status: pass
      - kind: other
        ref: "/usr/bin/grep -c '33447867312' .planning/notes/catalog-sync-check-retirement.md == 4"
        status: pass
      - kind: other
        ref: "/usr/bin/grep -c '57e63429' .planning/notes/catalog-sync-check-retirement.md == 3"
        status: pass
      - kind: other
        ref: "/usr/bin/grep -c '^## ' .planning/notes/catalog-sync-check-retirement.md == 7 (>= 6 floor)"
        status: pass
      - kind: other
        ref: "/usr/bin/grep -c 'required_status_checks\\|required status checks' .planning/notes/catalog-sync-check-retirement.md == 2"
        status: pass
    human_judgment: false
  - id: D2
    description: "catalog-sync-check.yml is deleted, nothing outside .planning/ references it, and the historical .planning/ citations survive untouched."
    requirement: "CLAIM-08"
    verification:
      - kind: other
        ref: "test ! -e .github/workflows/catalog-sync-check.yml -> workflow deleted"
        status: pass
      - kind: other
        ref: "git grep -n catalog-sync-check -- . ':!.planning' ; exit=1 (no match)"
        status: pass
      - kind: other
        ref: "git grep -l catalog-sync-check -- .planning | wc -l == 92 (non-zero, non-vacuity control)"
        status: pass
      - kind: other
        ref: "git log --oneline -1 --diff-filter=D -- .github/workflows/catalog-sync-check.yml -> 7d7179ec"
        status: pass
    human_judgment: false
  - id: D3
    description: "CLAIM-08 and ROADMAP Phase 185 criterion 5 both read in the amended D-02 form; Phase 185 still has exactly five criteria and neighbouring Phase 184/186 headings are intact; both sub-repo gitlinks advanced by name."
    requirement: "CLAIM-08"
    verification:
      - kind: other
        ref: "/usr/bin/grep -c 'retired' .planning/REQUIREMENTS.md == 2"
        status: pass
      - kind: other
        ref: "/usr/bin/grep -n '^### Phase 18[4-6]:' .planning/ROADMAP.md -> 3 lines (184, 185, 186 all present)"
        status: pass
      - kind: other
        ref: "sed -n Phase-185-section,+30p | grep -c '^[0-9]\\.' == 5"
        status: pass
      - kind: other
        ref: "git diff --stat -- .planning/REQUIREMENTS.md .planning/ROADMAP.md (10+/6-, 6+/2- respectively — section-scoped, not a reformat)"
        status: pass
      - kind: other
        ref: "git diff --cached --submodule=short -- firestarter firestarter_app (both paths named; ec7c1bbd..14be84c0, a745cb64..bffbba8e)"
        status: pass
      - kind: other
        ref: "git -C firestarter status --porcelain --untracked-files=no && git -C firestarter_app status --porcelain --untracked-files=no -> empty"
        status: pass
    human_judgment: false

duration: 45 min
completed: 2026-09-11
status: complete
---

# Phase 185 Plan 06: Retire the catalog sync workflow and amend its unreachable requirement Summary

**Deleted `catalog-sync-check.yml` (the meta repo's only workflow) after recording its failure's cause in a verdict document, then hand-amended CLAIM-08 and ROADMAP criterion 5 to the retirement's reachable form and advanced both sub-repo gitlinks.**

## Performance

- **Duration:** 45 min
- **Completed:** 2026-09-11
- **Tasks:** 3
- **Files modified:** 4 (1 created, 3 modified) plus 2 gitlinks

## Accomplishments
- `.planning/notes/catalog-sync-check-retirement.md` carries all five required contents: the exit-2 missing-file cause (with the failing step and run `33447867312` cited), why fix `57e63429` could not reach `main`, the correction of the workflow's own now-false "never once succeeded" comment (quoted verbatim before deletion), the byte/sha counterfactual proving a naive `beta` fallback would only change which assertion fails, and the residual gap — nothing compares the two vendored catalogs except at `sync_to_subrepos.sh`'s run time, with the meta repo's zero-CI consequence stated plainly.
- `.github/workflows/catalog-sync-check.yml` deleted outright (D-01); `.github/workflows/` is now empty. Confirmed via `git grep` that no reference to the workflow survives outside `.planning/`; the 92 historical `.planning/` citations are untouched.
- `gh run list` confirms no new run appeared since the last recorded failure (`33447867312`) — recorded in the note with the explicit caveat that this listing is not proof of the amended requirement, since GitHub only de-registers the workflow once the deletion reaches the protected default branch.
- CLAIM-08 in `.planning/REQUIREMENTS.md` and ROADMAP Phase 185 criterion 5 both amended by hand to the D-02 form, each stating the original demand, why it is unsatisfiable (two independent reasons), the amended wording, and the precedent (Phase 183 D-08, Phase 184 D-03).
- Both sub-repo gitlinks advanced by name: `firestarter` `ec7c1bbd9768c58908a3cf1b3c15b7695036b3e6` → `14be84c02a49bdd456add39832d0278a80768ae4`; `firestarter_app` `a745cb647743e7d8738e4d8b9dbe8f17aef38653` → `bffbba8e6179a181f9ac381d11a2d86d6204ec37`. Both sub-repos confirmed clean of tracked changes and on the milestone branch before staging.

## Task Commits

1. **Task 1: Read the workflow, then author the verdict document with all five required contents (D-03)** - `d7641e15` (docs)
2. **Task 2: Delete the workflow, and prove nothing dangles outside `.planning/` (D-01, CLAIM-08)** - `7d7179ec` (fix)
3. **Task 3: Amend CLAIM-08 and ROADMAP criterion 5 to the reachable form, and advance both sub-repo gitlinks (D-02)** - `735d03c4` (docs)

**Plan metadata:** this SUMMARY's own commit (docs)

## Files Created/Modified
- `.planning/notes/catalog-sync-check-retirement.md` - CLAIM-08's verdict document, quoting the workflow before deletion
- `.github/workflows/catalog-sync-check.yml` - deleted
- `.planning/REQUIREMENTS.md` - CLAIM-08 amended to the D-02 form
- `.planning/ROADMAP.md` - Phase 185 success criterion 5 amended to match; nothing else in the section touched
- `firestarter` (gitlink) - advanced to `14be84c02a49bdd456add39832d0278a80768ae4`
- `firestarter_app` (gitlink) - advanced to `bffbba8e6179a181f9ac381d11a2d86d6204ec37`

## Decisions Made
See `key-decisions` in frontmatter: outright deletion per D-01, hand-edits only per D-02 (no tooling verb), no successor guard filed per D-04, and the 92 historical `.planning/` citations left untouched.

## Deviations from Plan

None - plan executed exactly as written. The measured historical-citation count (92) differs from CONTEXT.md's discussion-time figure of 87 — expected, since this phase's own planning artifacts (RESEARCH.md, CONTEXT.md, the PLAN.md, 185-05's SUMMARY, and this note) accumulated additional citations after that measurement was taken. The plan's acceptance criterion only requires the count be recorded and non-zero, which it is.

## Issues Encountered
None.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- CLAIM-08 is closed: the workflow is retired, its failure's cause is on the record, and both tracking documents state a requirement the phase can satisfy.
- Phase 185 is now fully closed across all four CLAIM strands (CLAIM-04 through CLAIM-08 previously landed in plans 01-05; this plan closes CLAIM-08's final Wave 4 close-out task).
- The residual cross-repo vendored-catalog-identity gap is named in the verdict document and deliberately not filed, per D-04 — a later phase reopening this question should read the verdict document first.

---
*Phase: 185-records-and-checks-that-are-current*
*Completed: 2026-09-11*

## Self-Check: PASSED

- `.planning/notes/catalog-sync-check-retirement.md` exists on disk: FOUND (15056 bytes)
- `.github/workflows/catalog-sync-check.yml` absent: FOUND (deleted, confirmed by `test ! -e`)
- Commit `d7641e15` exists: FOUND
- Commit `7d7179ec` exists: FOUND
- Commit `735d03c4` exists: FOUND
- `.planning/REQUIREMENTS.md` contains amended CLAIM-08 text: FOUND
- `.planning/ROADMAP.md` Phase 185 criterion 5 amended, Phase 184/186 headings intact: FOUND
- Both sub-repo gitlinks staged and committed at the recorded SHAs: FOUND
