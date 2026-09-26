---
phase: 138-preconditions-baseline
plan: 01
subsystem: infra
tags: [git, github-api, branch-management, squash-merge, submodule, requirements-traceability, gh-cli]

# Dependency graph
requires: []
provides:
  - "gsd/v1.31-27c-programming-algorithm-fidelity branch in all three repos, each base named by full SHA and verified two independent ways"
  - "PREP-01 content-equivalence adjudication (four re-measured oracles) with the requirement's ancestry wording corrected in place"
  - "F-138-01 (squash-merge mechanism), F-138-02 (firmware beta drift + MERGE-05 headroom), F-138-03 (stale submodule gitlinks) — each recorded with a named owner, not fixed"
affects: [138-02, 138-03, 138-04, 138-05, 138-06, 138-07, Phase 139-146 (all fork from the bases this plan names), Phase 143/144 (F-138-02 owner), future git-hygiene work (F-138-03 owner)]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Four-oracle branch adjudication (GitHub PR record, ancestry check, ls-tree comm content-equivalence, attributable diff --stat) to distinguish a squash-merge ancestry false-negative from a genuine non-merge"
    - "F-NN finding style: mechanism + verdict + named owner + 'recorded, not fixed' — no reconciliation when a measured number diverges from a prior artifact's recorded number"

key-files:
  created:
    - .planning/phases/138-preconditions-baseline/138-BRANCH-BASES.md
  modified:
    - .planning/REQUIREMENTS.md

key-decisions:
  - "Executed OD-1 (PREP-01 discharged as content-equivalence finding F-138-01, not a merge — D-08 is a no-op, no PR opened)"
  - "Executed OD-2 (firmware forks at the decided base 3085084, not the live beta tip 6fab4ea; the +34B flash drift and MERGE-05 headroom carried forward as F-138-02, owners Phase 144/TEST-08 and Phase 143/144, per D-07)"
  - "Executed OD-3 (meta submodule gitlinks deliberately left stale; F-138-03, owner henols)"
  - "Folded the file-count divergence between this run's oracle 4 (15 files, post-fetch live tip) and 138-RESEARCH.md's recorded oracle 4 (12 files, stale cached ref) into F-138-01's own section rather than minting a new finding ID — same oracle, same mechanism, the difference is measurement methodology (fetch-before-diff) not a new remote-state fact"

requirements-completed: [PREP-01, PREP-02]

coverage:
  - id: D1
    description: "PREP-01 discharged as a content-equivalence finding via four independently re-measured, read-only oracles (GitHub PR record, ancestry false-negative, empty ls-tree comm, attributable diff), with the requirement's ancestry-based wording corrected in place in REQUIREMENTS.md"
    requirement: "PREP-01"
    verification:
      - kind: other
        ref: "138-BRANCH-BASES.md §1-2 (F-138-01) — gh pr view 44 prints MERGED; git merge-base --is-ancestor exits 1; comm -23 over both ls-tree listings is empty; REQUIREMENTS.md PREP-01 annotation cites all four"
        status: pass
    human_judgment: false
  - id: D2
    description: "gsd/v1.31-27c-programming-algorithm-fidelity exists, identically named, in meta/firestarter/firestarter_app, each base verified two ways and named by full 40-char SHA (meta d0f0c6a0, firmware 3085084 decided base, app 4d18b64 live tip)"
    requirement: "PREP-02"
    verification:
      - kind: other
        ref: "138-BRANCH-BASES.md §4 — git rev-parse --verify succeeds in all three repos; git merge-base --is-ancestor exits 0 for each base/branch pair; firmware symbolic-ref confirms checkout; app branch created but not checked out"
        status: pass
    human_judgment: false
  - id: D3
    description: "REQUIREMENTS.md traceability table and checkboxes updated: PREP-01/PREP-02 ticked with cited evidence, PREP-03/PREP-04 left untouched at [ ]/Pending (out of this plan's requirement scope)"
    requirement: "PREP-01"
    verification:
      - kind: other
        ref: "REQUIREMENTS.md — grep '^- \\[x\\] \\*\\*PREP-0[12]\\*\\*' each count 1; grep '^- \\[ \\] \\*\\*PREP-0[34]\\*\\*' both still match; traceability rows PREP-01/PREP-02 read Complete"
        status: pass
    human_judgment: false

# Metrics
duration: 17min
completed: 2026-08-08
status: complete
---

# Phase 138 Plan 01: Preconditions & Baseline — Branch Bases Summary

**Four-oracle proof that v1.30's app PR was squash-merged (not left unmerged) plus a named,
twice-verified `gsd/v1.31-27c-programming-algorithm-fidelity` base in all three repos.**

## Performance

- **Duration:** 17 min
- **Started:** 2026-08-08T21:21:25Z
- **Completed:** 2026-08-08T21:38:21Z
- **Tasks:** 3
- **Files modified:** 2 (1 created, 1 modified)

## Accomplishments

- Re-measured all four PREP-01 oracles live in `firestarter_app` (never copied from
  `138-RESEARCH.md`): GitHub PR **#44** is `MERGED` as a **squash** (single parent `16a313a`);
  `git merge-base --is-ancestor` exits **1** (the squash-merge false negative, not evidence of
  non-merger); `comm -23` over both branches' `git ls-tree` listings is **empty** — the load-bearing
  proof that zero files on the v1.30 branch are missing from `beta`; `git diff --stat` shows 15 files,
  every one attributable to `beta`'s later PRs #45/#46/#48/#49/#50. `git merge-tree` proves a re-merge
  would conflict on `tests/test_chip_test_sdp_leg.py` (added independently on both sides, different
  blobs).
- Created `gsd/v1.31-27c-programming-algorithm-fidelity` in all three repos on named, twice-verified
  bases: **meta** off `d0f0c6a0…` (confirmed the fork point, not `00af5771…`, the shorter-named v1.30
  branch — pre-existing, re-verified); **firestarter** created and **checked out** at the decided base
  `3085084…` (worktree confirmed clean before the switch); **firestarter_app** created as a **ref
  only** (not checked out) at the live, re-fetched beta tip `4d18b64…`.
- Ticked **PREP-01** and **PREP-02** in `REQUIREMENTS.md` with in-place, dated wording corrections
  (never rewriting the historical text) and evidence citations to `138-BRANCH-BASES.md`. **PREP-03**
  and **PREP-04** were left untouched (`[ ]`, `Pending`) — out of this plan's requirement scope.
- Recorded three findings with named owners, per D-07 ("record, do not fix"): **F-138-01** (the
  squash-merge mechanism and content-equivalence verdict), **F-138-02** (firmware `beta` drift, +34 B
  flash on all three AVR targets, MERGE-05 band headroom down to 2–8 B — owners Phase 144/TEST-08,
  Phase 143/144), **F-138-03** (meta submodule gitlinks deliberately not advanced — owner henols).

## Task Commits

Each task was committed atomically:

1. **Task 1: Re-measure the four PREP-01 oracles and both live tips, then write the adjudication** -
   `f6672b8d` (docs)
2. **Task 2: Create and verify the v1.31 milestone branch in all three repos** - `3679423b` (docs)
3. **Task 3: Tick PREP-01 and PREP-02 with the wording correction recorded** - `9821de1f` (docs)

**Plan metadata:** (this commit, immediately following)

_No sub-repo commits were made — this plan's `commits_land_in` is meta-only, plus local-only branch
refs inside the two submodules (no submodule commit, no push)._

## Files Created/Modified

- `.planning/phases/138-preconditions-baseline/138-BRANCH-BASES.md` (created, 258 lines) - the
  four-oracle adjudication (§1-2), live-tip-vs-cached-cache table and firmware drift enumeration (§3),
  the three verified base commits (§4), F-138-02 (§5), F-138-03 (§6), and the hand-off to later plans
  (§7)
- `.planning/REQUIREMENTS.md` (modified) - PREP-01/PREP-02 checkboxes ticked with in-place dated
  correction annotations; traceability table rows for both changed from `Pending` to `Complete`

## Decisions Made

This plan executed three operator decisions already recorded in `138-CONTEXT.md`/`STATE.md`
(OD-1, OD-2, OD-3) rather than making new ones — see `key-decisions` in the frontmatter above for the
literal execution record of each. One executor-level judgment call: this session's re-measured oracle
4 found **15** drifted files where `138-RESEARCH.md` recorded **12** — both are correct measurements
taken against different local refs (research's ran pre-fetch against a stale cache, this plan's ran
post-fetch against the live tip, which by now includes PR #50). This was folded into **F-138-01**'s
own section rather than minting a new finding ID, since it is the same oracle and the same mechanism,
not a new remote-state fact — recorded per D-06's "measured number wins, both stated, no
reconciliation" rule.

## Deviations from Plan

None — plan executed exactly as written. All three tasks' automated `<verify>` blocks and every
acceptance criterion in `138-01-PLAN.md` passed on the first measurement; no bug, missing
functionality, blocking issue, or architectural question arose.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required. (`gh` CLI was already authenticated as `henols`
with no setup needed.)

## Next Phase Readiness

- **Firmware** (`/workspaces/firestarter`) is checked out on `gsd/v1.31-27c-programming-algorithm-fidelity`
  at `3085084…`, ready for Wave 2's firmware plans (Phases 140/141/142) to land commits directly.
- **App** (`/workspaces/firestarter_app`) has the same-named branch created at the live beta tip
  `4d18b64…` but is still on `fix/dev-test-blank-check-after-erase` — Plan 04 (this phase's own later
  plan) is the one that checks it out.
- **Meta** is already on the branch (unpushed, no upstream — expected, matches pre-existing state).
- Three base SHAs are on record in `138-BRANCH-BASES.md` §4 for `138-BASELINE.md` (a later plan in
  this phase) to cite directly.
- **F-138-02**'s MERGE-05 headroom (2–8 B remaining on `uno`/`uno328pb` before the band fails) is worth
  watching in Phase 143/144 — it is not this plan's or this phase's job to close it.
- **F-138-03** (stale gitlinks) awaits a future, explicit git-hygiene decision — not blocking, not
  addressed here.
- No push, no CI dispatch, no gitlink bump, and no re-build of the live firmware tip occurred — all
  explicitly out of this plan's scope (see `138-BRANCH-BASES.md` §7 Hand-off).

## Self-Check: PASSED

- FOUND: `.planning/phases/138-preconditions-baseline/138-BRANCH-BASES.md`
- FOUND: `.planning/REQUIREMENTS.md`
- FOUND commit: `f6672b8d`
- FOUND commit: `3679423b`
- FOUND commit: `9821de1f`

No missing items.

---
*Phase: 138-preconditions-baseline*
*Completed: 2026-08-08*
