---
phase: 173-close-beta-cut-under-protection-close-procedure-honesty-ledg
plan: 02
subsystem: infra
tags: [gsd-config, git-base-branch, branch-protection, honesty-ledger]

requires:
  - phase: 172-policy-one-tracker-protected-main
    provides: three active `Protect main` rulesets with `current_user_can_bypass: never`, measured and read back from the API rather than the settings page
provides:
  - "`.planning/config.json` `git.base_branch: beta` and `git.protected_branches: [main]`, tier-1 configuration that repoints every GSD consumer of `git.base-branch` from `main` to `beta`"
  - "`.planning/notes/v135-close-procedure-under-protection.md` — the mechanics note: all seven consumer sites, the pull-request-only route into `main` with no admin bypass to document, the version-bump block per Backlog 999.46, banked evidence of the route already working, and the correction to `REQUIREMENTS.md:119`'s false premise"
  - "`CLAUDE.md` pointer, auto-loaded into every session in this repo, so the next close agent reads the procedure before it fails rather than after"
affects: [173-08-close-record, 173-09-requirements-sweep]

actuals:
  tokens: 4539
  tasks: 3
  commits: 3

tech-stack:
  added: []
  patterns:
    - "GSD tier-1 config repoint over prose: a criterion that must hold by construction gets a config key with a proven read-back, not a document the tooling can ignore."
    - "Distinguishing read-back: assert the flip (`main`→`beta`), not just the post-state, because a base-branch-folded-into-protected-list resolver can read `true` before the fix too."

key-files:
  created:
    - .planning/notes/v135-close-procedure-under-protection.md
    - .planning/phases/173-close-beta-cut-under-protection-close-procedure-honesty-ledg/evidence/173-02-base-branch-readback.txt
    - .planning/phases/173-close-beta-cut-under-protection-close-procedure-honesty-ledg/evidence/173-02-consumer-sites.txt
  modified:
    - .planning/config.json
    - CLAUDE.md

key-decisions:
  - "D-06 (config-first): `.planning/config.json` gains `git.base_branch: beta` and `git.protected_branches: [main]`, nested under the existing `git` object, hand-edited rather than through a GSD verb."
  - "D-07 (auto-loaded pointer): the mechanics live in a `.planning/notes/` file; the pointer lives in meta's `CLAUDE.md` because being read is the requirement POLICY-05 exists to satisfy."
  - "D-08 (no bypass to document): the admin-bypass branch of POLICY-05 is recorded as impossible — `current_user_can_bypass` is `never` on all three rulesets — rather than invented."
  - "REQUIREMENTS.md:119's stated rationale (`/gsd-complete-milestone` pushes `main` directly) is false; the real failure surface is a local squash-merge onto an unpushable `main`, `ship.md --base main`, and three fork-point consumers, all fixed by the same repoint."

patterns-established:
  - "Before/after read-back pairs in one evidence file, with an explicit note on which read-backs are non-distinguishing (here: `--is-protected main` reads `true` both before and after)."

requirements-completed: [POLICY-05]

coverage:
  - id: D1
    description: "git.base-branch resolves beta instead of main, proven by a read-back that would fail before the edit"
    requirement: "POLICY-05"
    verification:
      - kind: other
        ref: "evidence/173-02-base-branch-readback.txt — base-branch before/after, --is-protected beta/main/milestone-branch before/after"
        status: pass
    human_judgment: false
  - id: D2
    description: "Close-procedure note records the mechanics, the blocked stable-release route, and the corrected REQUIREMENTS.md:119 premise"
    requirement: "POLICY-05"
    verification:
      - kind: other
        ref: "evidence/173-02-consumer-sites.txt — all 13 cited constructs resolve in the vendored workflow tree"
        status: pass
    human_judgment: false
  - id: D3
    description: "CLAUDE.md points the next close agent at the note without deleting existing content"
    requirement: "POLICY-05"
    verification:
      - kind: other
        ref: "task 3 verify legs — heading present, pointer path resolves, section placed after Key Architecture Points, numstat deletions = 0, sub-repo CLAUDE.md files untouched"
        status: pass
    human_judgment: false

duration: 35min
completed: 2026-09-02
status: complete
---

# Phase 173 Plan 02: Repoint the base branch and record the close procedure — Summary

**POLICY-05 fixed by construction: `git.base-branch` now resolves `beta` instead of `main`, proven by a distinguishing before/after read-back, with the mechanics and the still-blocked stable-release route written into an auto-loaded `CLAUDE.md` pointer.**

## Performance

- **Duration:** 35 min
- **Started:** 2026-09-02T14:05:00Z (approx.)
- **Completed:** 2026-09-02T14:40:00Z (approx.)
- **Tasks:** 3/3 completed
- **Files modified:** 5 (2 modified, 3 created)

## Accomplishments

- `.planning/config.json` gained `git.base_branch: "beta"` and `git.protected_branches: ["main"]`, nested inside the existing `git` object, hand-edited and byte-identical elsewhere against `HEAD`. Read-back proved the two distinguishing flips: `git.base-branch` `main`→`beta`, `--is-protected beta` `false`→`true`, with `--is-protected` on the current milestone branch staying `false` before and after — proof the resolver verified rather than fell closed.
- `.planning/notes/v135-close-procedure-under-protection.md` records D-06's read-back, all seven consumer sites (`complete-milestone.md`, `ship.md`, `execute-phase.md`, `quick.md`, `pr-branch.md`, `protected-branch.md`) with line numbers, the stale-local-`beta` trap on `ship.md:316`, the pull-request-only route into `main` with no admin bypass to document, the version-bump breakage per Backlog 999.46, three already-merged `main` pull requests as banked evidence the route works, and the correction of `REQUIREMENTS.md:119`'s false "pushes `main` directly" premise — the real failure surface is a local squash-merge that never gets pushed, `ship.md --base main`, and three fork-point consumers.
- `CLAUDE.md` gained a `## Milestone close and branch protection` section after `## Key Architecture Points`, naming the ruleset, the `beta` close target, the stale-local-`beta` trap, and the note path — auto-loaded into every session, so the next close agent reads this before it fails rather than after.

## Task Commits

Each task was committed atomically:

1. **Task 1: Repoint the base branch in configuration, and prove it by the read-back that would fail before the edit** - `a9eb80fa` (feat)
2. **Task 2: Write the close-procedure note** - `9a9783ac` (docs)
3. **Task 3: Point the auto-loaded CLAUDE.md at the note** - `51bcc058` (docs)

## Files Created/Modified

- `.planning/config.json` - `git` object gains `base_branch` and `protected_branches`
- `.planning/notes/v135-close-procedure-under-protection.md` - the mechanics, the blocked route, the false-premise correction
- `CLAUDE.md` - new pointer section, nothing removed
- `.planning/phases/173-close-beta-cut-under-protection-close-procedure-honesty-ledg/evidence/173-02-base-branch-readback.txt` - before/after resolver output, pointer read-back
- `.planning/phases/173-close-beta-cut-under-protection-close-procedure-honesty-ledg/evidence/173-02-consumer-sites.txt` - all 13 cited constructs demonstrated in the vendored tree

## Decisions Made

None beyond the plan's own D-06/D-07/D-08 — followed the plan as specified, including its explicit prohibitions (no ruleset touched, no top-level config keys, `.planning/config.json` hand-edited, no comments written).

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Orchestrator-owned artifacts — provably untouched

`.planning/ROADMAP.md` and `.planning/REQUIREMENTS.md` were not written by this plan. Verified with
empty diffs against both the pre-plan commit and the current `HEAD`:

```
$ git diff --stat aa7e665a -- .planning/ROADMAP.md .planning/REQUIREMENTS.md
(no output)
$ git diff --stat HEAD~3 -- .planning/ROADMAP.md .planning/REQUIREMENTS.md
(no output)
```

No `roadmap.*` or `requirements.*` gsd-tools verb was invoked. POLICY-04 and POLICY-05 checkboxes
remain unmarked in `.planning/REQUIREMENTS.md`, as required — only plan 173-09 flips them.

## Next Phase Readiness

POLICY-05 is now satisfied by construction: the resolver returns `beta` and every GSD consumer of
`git.base-branch` follows it, with the one branch of the requirement that cannot be satisfied
(a documented admin bypass) recorded as impossible rather than invented. Ready for the remaining
Phase 173 plans (POLICY-04 probe/cut, the honesty ledger, upstream replies, and the closing sweep
at 173-09 that flips the requirement checkboxes).

---
*Phase: 173-close-beta-cut-under-protection-close-procedure-honesty-ledg*
*Completed: 2026-09-02*

## Self-Check: PASSED

All 6 key files found on disk; all 3 task commits found in git log.
