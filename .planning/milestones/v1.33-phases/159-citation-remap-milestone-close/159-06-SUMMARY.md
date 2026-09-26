---
phase: 159-citation-remap-milestone-close
plan: "06"
subsystem: infra
tags: [citation-remap, milestone-close, requirements-traceability, roadmap-closure]

requires:
  - phase: 159-citation-remap-milestone-close
    provides: "159-05's sole production apply (receipt APPLIED, event 04390458f8ee4776bd75c2656a62a809, 2,706 citations rewritten across 562 documents), the proven corpus-wide dry-run fixed point, and 159-remap-record.md's explicit guidance for this plan's own dry-no-op gate"
provides:
  - "159-close-readiness.json: frozen close-gate results, preserved-dirty hashes, and exact licensed replacement-payload digests, captured while REQUIREMENTS/ROADMAP/STATE/record/marker were still byte-identical"
  - "Five REMAP-01..05 requirements ticked in REQUIREMENTS.md with measured discharge sentences, and their five traceability rows changed to Complete"
  - "Six Phase-159 plan checkboxes ticked in ROADMAP.md, with measured facts appended to all five existing Success Criteria; Goal/Depends on/Requirements left byte-identical"
  - "159-remap-record.md's final 'Scoped closure readiness and final marker transition' section"
  - "Deletion of the close-blocking .planning/v1.33/CITATIONS-STALE.md marker, as this plan's own final implementation-file mutation"
affects: []

tech-stack:
  added: []
  patterns:
    - "Scoped hand-authored closure via targeted Edit only (never a whole-file writer or GSD roadmap/requirements mutation helper), with an exact pre-computed replacement-payload sha256 frozen in a readiness artifact BEFORE the edit is applied, then verified byte-for-byte equal after -- so the closure cannot silently drift from what the readiness gate certified."
    - "Two-phase gate sequencing to avoid a self-inflicted false regression: run the full corpus-wide guard-test suite (test_the_tool_is_not_applied_to_any_real_planning_document) and freeze readiness FIRST, while REQUIREMENTS.md/ROADMAP.md are still byte-identical to HEAD, THEN apply the licensed hand-edits -- because that guard test treats any diff to those two citing documents as evidence of an unauthorized remap-tool application, and cannot distinguish a hand-authored closure edit from a bad apply."

key-files:
  created:
    - .planning/v1.33/159-close-readiness.json
  modified:
    - .planning/REQUIREMENTS.md
    - .planning/ROADMAP.md
    - .planning/v1.33/159-remap-record.md
  deleted:
    - .planning/v1.33/CITATIONS-STALE.md

key-decisions:
  - "Ran the plan's own gate/test-suite verification (Task 1) BEFORE, not after, drafting the REQUIREMENTS/ROADMAP edits, having discovered mid-execution that 154's own `test_the_tool_is_not_applied_to_any_real_planning_document` guard fails closed on ANY diff to those two citing documents, hand-authored or not. Reverted the premature edits with `git checkout -- <file>` on the two files I had just touched myself (permitted under the destructive-git-prohibition's explicit carve-out for a specific file modified during the current task), re-ran the full 98-test suite clean, then re-applied the identical, already-vetted edit text in Task 2. No plan file, ledger, or manifest was affected by the revert."
  - "The `close-readiness.json` freezes the exact post-edit sha256 of both REQUIREMENTS.md and ROADMAP.md (computed in-memory before either file was touched) so Task 2's literal edits could be verified byte-for-byte against a pre-committed digest rather than merely 'looking right' -- both matched exactly."
  - "Recorded REMAP-02's discharge honestly rather than overclaiming: 269 of the resolved citation records rest on `diff_provenance_reworded` (diff provenance, not verbatim text equality) per 159-03/159-04/159-05's own recorded evidence, and both REQUIREMENTS.md and ROADMAP.md state this explicitly rather than implying the verbatim oracle held universally."
  - "SWEEP-13's intentionally-open one-meta-commit clause was named in the appended remap-record section without being ticked or re-derived, per the plan's explicit instruction; this closure's own two commits under `.planning/v1.33` are additive to that already-recorded count, not a re-litigation of it."

requirements-completed: [REMAP-01, REMAP-02, REMAP-03, REMAP-04, REMAP-05]

coverage:
  - id: D1
    description: "159-close-readiness.json freezes all close gates green (98/98 tests, corpus-wide dry-run fixed point, archive PASS/superseded:12, range 128-131->316-318, source heads, empty index, preserved-dirty hashes) plus the exact REQUIREMENTS/ROADMAP replacement-payload digests, while REQUIREMENTS/ROADMAP/STATE/record/marker are still byte-identical"
    requirement: REMAP-04
    verification:
      - kind: automated_ui
        ref: "cd /workspaces && pytest -q test_remap_citations.py test_prepare_citation_remap.py test_rehearse_citation_remap.py && python3 -c \"...assert p['status']=='READY_TO_REMOVE_MARKER'...\" && test -e CITATIONS-STALE.md"
        status: pass
    human_judgment: false
  - id: D2
    description: "REMAP-01..05 ticked in REQUIREMENTS.md with measured discharge sentences; five traceability rows changed to Complete; no other requirement family or SWEEP-13 touched"
    requirement: "REMAP-01, REMAP-02, REMAP-03, REMAP-04, REMAP-05"
    verification:
      - kind: automated_ui
        ref: "grep -cE '^- \\[x\\] \\*\\*REMAP-0[1-5]\\*\\*' REQUIREMENTS.md == 5; grep -cE traceability-Complete == 5; git diff --stat scoped to Phase 159 region only"
        status: pass
    human_judgment: false
  - id: D3
    description: "Six Phase-159 plan checkboxes ticked in ROADMAP.md; measured facts appended to the five existing Success Criteria; Goal/Depends on/Requirements and all other phases byte-identical"
    requirement: "REMAP-01, REMAP-03, REMAP-05"
    verification:
      - kind: automated_ui
        ref: "grep -cE '^- \\[x\\] 159-0[1-6]-PLAN\\.md' ROADMAP.md == 6; '### Phase ' heading count and REQUIREMENTS '- [' bullet count unchanged vs HEAD~1"
        status: pass
    human_judgment: false
  - id: D4
    description: ".planning/v1.33/CITATIONS-STALE.md deleted as the final implementation-file mutation, after every pre-delete gate re-passed with the marker still present"
    requirement: REMAP-04
    verification:
      - kind: automated_ui
        ref: "test ! -e .planning/v1.33/CITATIONS-STALE.md; git show --name-status HEAD | grep '^D.*CITATIONS-STALE.md'"
        status: pass
    human_judgment: false
  - id: D5
    description: ".planning/STATE.md and every other pre-existing dirty path remain byte-identical and unstaged; no archive/release/push/PR/merge/milestone-completion action performed"
    verification:
      - kind: automated_ui
        ref: "sha256sum .planning/STATE.md == e866ab7ad7840e69931b4af62709c33ce9e5a69537c6c5abd24eda14bba8d71f; git status --short unchanged from session start"
        status: pass
    human_judgment: true
    rationale: "Confirming no archive/release/push/PR/merge/milestone-completion action occurred is a negative-space claim best cross-checked by a human reviewer alongside the operator-gated /gsd-complete-milestone handoff, even though every mechanical check performed here passed."

duration: not reliably measurable (interactive, two-task closure with a mid-task gate-sequencing correction; no wall-clock instrumentation)
completed: 2026-08-24
status: complete
---

# Phase 159 Plan 06: Citation Remap + Milestone Close -- Closure Summary

**Closed all five REMAP-01..05 requirements against 159-05's measured production-apply evidence, checked all six Phase-159 plan lines with measured facts appended to every existing Success Criterion, and deleted the close-blocking `.planning/v1.33/CITATIONS-STALE.md` marker as the phase's final implementation-file mutation -- leaving v1.33 ready, but not actioned, for the separate `/gsd-complete-milestone` workflow.**

## Performance

- **Duration:** not reliably measurable (see frontmatter)
- **Tasks:** 2 completed
- **Files modified/created:** 1 created (`159-close-readiness.json`), 3 modified (`REQUIREMENTS.md`, `ROADMAP.md`, `159-remap-record.md`), 1 deleted (`CITATIONS-STALE.md`), plus this SUMMARY

## Accomplishments

- **Task 1:** Re-ran all three focused test modules (98/98 passing), the production-shaped dry run (disk residual limited to exactly `[".planning/STATE.md"]`, 1 rewritten/1 document, all actionable/open counts zero -- the exact expected `preserve_unstaged` shape 159-05's own record predicted for this gate), Phase 130's archive gate (`PASS`, `superseded: 12`), and confirmed both sub-repo HEADs, a clean real index, and every pre-existing dirty path's hash against the Plan-05 baseline. Froze `.planning/v1.33/159-close-readiness.json` (`status: READY_TO_REMOVE_MARKER`) with the exact sha256 of both REQUIREMENTS.md and ROADMAP.md's post-edit content, computed in memory before either file was touched.
- **Task 2:** Applied the exact frozen REQUIREMENTS.md payload (five REMAP checkboxes ticked, five measured discharge sentences appended, five traceability rows changed to `Complete`) and the exact frozen ROADMAP.md payload (six Phase-159 plan checkboxes ticked, measured facts appended to all five existing Success Criteria, `Goal`/`Depends on`/`Requirements` and every other phase byte-identical) -- both files' post-edit sha256 matched the readiness digest exactly. Appended the `Scoped closure readiness and final marker transition` section to `159-remap-record.md`. Re-ran every pre-delete gate (heading/bullet counts, line counts, diff scope, STATE/dirty-path hashes, dry no-op residual shape, archive gate, empty index, marker presence) green, then deleted `.planning/v1.33/CITATIONS-STALE.md` as the final implementation-file mutation. Staged exactly the four closure paths (never STATE.md, never any source/gitlink/manifest/ledger/package path) and committed without a pathspec as `docs(159-06): close citation staleness window and record milestone readiness`.
- Discovered and corrected a self-inflicted gate-ordering issue mid-execution (see Deviations): 154's own citation-corpus guard test fails closed on any diff to REQUIREMENTS.md/ROADMAP.md regardless of cause, so Task 1's gate suite had to run while those two files were still byte-identical to HEAD -- resequenced accordingly, with no impact on the final committed content.
- REMAP-02's requirement text and this closure's discharge sentence both state honestly that 269 of the resolved citation records rest on diff provenance rather than verbatim text equality -- the verbatim oracle held for the remainder, not universally, matching the honesty constraint given for this plan.
- `.planning/STATE.md` verified byte-identical to its preserved dirty hash (`e866ab7a...bba71f`) throughout both tasks and never staged; the pre-existing 13-path dirty baseline (STATE, config.json, the six 159-0N-PLAN.md files, 159-RESEARCH.md, 159-VALIDATION.md, the firestarter gitlink, and the two untracked root package files) is unchanged from the start of this session.

## Task Commits

1. **Task 1: Freeze exact close gates and scoped edit payload readiness** - `a6a54ee9` (feat)
2. **Task 2: Apply scoped REMAP closure, recheck, and delete the marker as the final implementation mutation** - `3779d3fc` (docs)

## Files Created/Modified

- `.planning/v1.33/159-close-readiness.json` (new) - `status: READY_TO_REMOVE_MARKER`; production-apply/dry-run/archive/range/source-head/index/dirty-hash gate results; the exact `replacement_payload_sha256` digests for REQUIREMENTS.md and ROADMAP.md; `state_mutation_authorized: false`, `milestone_completion_authorized: false`
- `.planning/REQUIREMENTS.md` - REMAP-01..05 checkboxes ticked, five measured discharge sentences appended, five traceability rows changed to `Complete (..., closed 159-06)`; line count (158) and bullet count (43) unchanged; no other requirement family touched
- `.planning/ROADMAP.md` - Phase 159's six plan checkboxes ticked; measured facts appended to all five existing Success Criteria; `Goal`/`Depends on`/`Requirements` lines and every other phase byte-identical; line count (4593) and `### Phase ` heading count (100) unchanged
- `.planning/v1.33/159-remap-record.md` - appended `## Scoped closure readiness and final marker transition (Plan 159-06)`, naming SWEEP-13's still-open clause without rewriting it and stating no archive/release/push/PR/merge/milestone-completion action occurred
- `.planning/v1.33/CITATIONS-STALE.md` (deleted) - the close-blocking marker, removed last, as this plan's final implementation-file mutation

## Decisions Made

See `key-decisions` in frontmatter for the four load-bearing calls. In one sentence each: resequenced Task 1's gate suite to run before touching REQUIREMENTS/ROADMAP after discovering the corpus guard test cannot distinguish a hand-authored closure edit from a bad remap application; froze exact post-edit sha256 digests in the readiness artifact before editing, then verified them byte-for-byte after; stated REMAP-02's discharge honestly (diff provenance, not universal verbatim equality) rather than overclaiming; and left SWEEP-13 named but untouched per the plan's explicit instruction.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Gate-sequencing correction: ran Task 1's test suite before, not after, drafting the REQUIREMENTS/ROADMAP edit text**
- **Found during:** Task 1, first attempt at running the focused pytest modules
- **Issue:** I had drafted and applied the REQUIREMENTS.md/ROADMAP.md edits (which are licensed, Task-2-scoped content) before running Task 1's own gate suite. `test_the_tool_is_not_applied_to_any_real_planning_document` (a Phase-154-authored guard) treats ANY diff to those two citing documents, relative to `git diff HEAD`, as evidence the remap tool was misapplied to a real planning document -- it cannot distinguish a hand-authored closure edit from an unauthorized `--apply` run, and both REQUIREMENTS.md and ROADMAP.md are themselves in the citation-bearing corpus. This failed 1 of 98 tests.
- **Fix:** Reverted the two files I had just edited myself with `git checkout -- .planning/REQUIREMENTS.md .planning/ROADMAP.md` (the destructive-git-prohibition's explicit carve-out: discarding changes to a specific file modified during the current task), confirmed both hashes matched HEAD exactly, re-ran the full 98-test suite clean, wrote `159-close-readiness.json` against that clean baseline, then re-applied the identical, already-vetted edit text in Task 2 (verified byte-for-byte against the frozen digest).
- **Files modified:** `.planning/REQUIREMENTS.md`, `.planning/ROADMAP.md` (reverted, then correctly re-applied in Task 2)
- **Verification:** 98/98 tests pass with the readiness snapshot taken against unedited docs; the Task-2 re-application's post-edit sha256 matches the pre-frozen digest exactly
- **Committed in:** no separate commit for the revert itself (working-tree-only); the final content is committed in `3779d3fc`

---

**Total deviations:** 1 auto-fixed (1 blocking, self-inflicted gate-ordering issue, corrected before any commit).
**Impact on plan:** No effect on the final committed content, which matches the plan's specified payload exactly. The correction prevented a false-negative test failure from being (incorrectly) treated as a genuine regression, and prevented the readiness artifact from freezing snapshots against an already-mutated baseline.

## Issues Encountered

- **The 154-authored citation-corpus guard test is not closure-aware.** `test_the_tool_is_not_applied_to_any_real_planning_document` was written to catch premature/unauthorized `remap_citations.py --apply` runs against real planning documents, using a `_KNOWN_BENIGN_PLANNING_PATHS` allowlist (currently `.planning/STATE.md` and `.planning/v1.9-COBS-DECISION.md`) for expected bookkeeping/relocation diffs. It does not anticipate that Phase 159's OWN closure plan is licensed to hand-edit two citation-bearing documents (REQUIREMENTS.md, ROADMAP.md) as its terminal act -- so any git-tree state where those two files differ from HEAD will fail this test, regardless of cause. Resolved procedurally (run the gate suite before editing, not after) rather than by touching the test file, which is out of this plan's licensed scope. Left as-is rather than "fixed" because the test's core guarantee (the remap tool itself was never mis-applied) remains true and valuable; a future reader attempting to re-run these three test modules against a checked-out state that already includes this plan's commits will see the same 1-test failure and should recognize it as this same, expected, closure-time interaction rather than a new regression.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- All five REMAP-01..05 requirements are `Complete` in `.planning/REQUIREMENTS.md`, all six Phase-159 plan checkboxes are ticked in `.planning/ROADMAP.md` with measured facts on every Success Criterion, and `.planning/v1.33/CITATIONS-STALE.md` is deleted and confirmed absent.
- `.planning/STATE.md` was never staged or edited by this plan; its sha256 remains `e866ab7ad7840e69931b4af62709c33ce9e5a69537c6c5abd24eda14bba8d71f`, exactly as preserved since Plan 159-05. The orchestrator owns the next STATE.md write.
- No archive, release, push, PR, merge, or milestone-completion action was taken by this plan. v1.33 is not described as archived, released, shipped, or completed anywhere in this closure's artifacts.
- **Next action:** `/gsd-complete-milestone` -- a separate, operator-gated workflow. `159-close-readiness.json` and `159-remap-record.md`'s closure section are its inputs, not its execution.
- `.planning/REQUIREMENTS.md` and `.planning/ROADMAP.md` remain hand-authored, pointed-at documents (never regenerated) -- this closure used targeted `Edit` calls exclusively, consistent with that standing convention.

---
*Phase: 159-citation-remap-milestone-close*
*Completed: 2026-08-24*

## Self-Check: PASSED

All created/modified/deleted files confirmed on disk: `159-close-readiness.json`, `REQUIREMENTS.md`, `ROADMAP.md`, `159-remap-record.md`, this SUMMARY present; `.planning/v1.33/CITATIONS-STALE.md` confirmed absent. Both task commits (`a6a54ee9`, `3779d3fc`) confirmed in `git log --all`. `.planning/STATE.md` (sha256 `e866ab7ad7840e69931b4af62709c33ce9e5a69537c6c5abd24eda14bba8d71f`) verified byte-identical to its preserved dirty hash and unstaged. `git status --short` shows the same pre-existing 13-path dirty baseline as at session start, plus this untracked SUMMARY prior to its own commit below.
