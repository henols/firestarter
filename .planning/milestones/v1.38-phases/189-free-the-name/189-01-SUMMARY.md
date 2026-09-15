---
phase: 189-free-the-name
plan: 01
subsystem: infra
tags: [github, gh-cli, repository-rename, identity-verification]

# Dependency graph
requires: []
provides:
  - "Operator-performed GitHub rename of henols/firestarter to henols/firestarter_fw, confirmed"
  - "Committed identity transcript proving the old slug still redirects and was not re-occupied"
  - "Phase 189 unblocked for plans 02, 03 and 04"
affects: [189-02, 189-03, 189-04]

# Actuals (#2632)
actuals:
  tokens: 167
  tasks: 2
  commits: 1
  plan_head_before: 97ecb03f8f4b1cd55f3d370c2efb875748c7dbd4

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Rename-identity assertion via numeric GitHub repository id, never by name alone (D-12), so a redirect is distinguishable from a re-occupied slug"

key-files:
  created:
    - .planning/phases/189-free-the-name/evidence/189-rename-01-identity.txt
  modified: []

key-decisions:
  - "D-11 honored: the GitHub rename was operator-performed at a blocking-human checkpoint; no task in this plan ran a rename or repository-modifying command."
  - "D-12 honored: the identity transcript asserts both .id and .full_name for the old slug, plus the meta repository's .id, so the redirect is proven distinct from a re-occupied slug rather than assumed from the name alone."

requirements-completed: [RENAME-01]

coverage:
  - id: D1
    description: "GitHub rename of henols/firestarter to henols/firestarter_fw confirmed live, with the old slug still redirecting and not re-occupied by any other repository (D-1 honored)"
    requirement: "RENAME-01"
    verification:
      - kind: other
        ref: "gh api repos/henols/firestarter --jq '.id' (810276812), gh api repos/henols/firestarter --jq '.full_name' (henols/firestarter_fw), gh api repos/henols/firestarter_fw --jq '.id' (810276812), gh api repos/henols/firestarter_prom --jq '.id' (1232995399)"
        status: pass
    human_judgment: false

duration: 1min
completed: 2026-09-13
status: complete
---

# Phase 189 Plan 01: Free the Name — Identity Gate Summary

**Confirmed the operator-performed GitHub rename of henols/firestarter to henols/firestarter_fw via a numeric-id-anchored identity transcript, proving the redirect is live and the old slug was not re-occupied.**

## Performance

- **Duration:** 1 min (Task 2 only — Task 1 was an operator-performed action in a prior session)
- **Started:** 2026-09-13T13:59:00Z
- **Completed:** 2026-09-13T14:00:47Z
- **Tasks:** 2 (1 checkpoint:human-action, 1 auto)
- **Files modified:** 1

## Accomplishments
- Operator renamed `henols/firestarter` to `henols/firestarter_fw` on GitHub, at a `blocking-human` checkpoint no task could perform itself (D-11).
- Captured and committed a four-reading identity transcript that asserts both `.id` and `.full_name` per D-12, proving the rename landed, the old slug still redirects, and it resolves to the firmware repository's id rather than the meta repository's id (D-1 honored).
- All six of Task 2's `<verify>` legs were re-run live against the real GitHub API and the working tree, and all six passed.

## Task Commits

1. **Task 1: Operator renames henols/firestarter to henols/firestarter_fw** — no commit (operator-performed GitHub Settings action; produces no repository commit by design). Cleared by the operator and verified by the orchestrator before this continuation began.
2. **Task 2: Capture and assert the RENAME-01 identity evidence** — `c2047210` (docs)

**Plan metadata:** (this commit, docs: complete plan)

## Files Created/Modified
- `.planning/phases/189-free-the-name/evidence/189-rename-01-identity.txt` - four labelled `gh api` readings (old-slug id, old-slug full_name, new-slug id, meta-repo id), a capture timestamp, and the one-sentence D-12 rationale

## Decisions Made
- None beyond the plan's own D-11/D-12, both followed exactly as written. No architectural deviation.

## Task 1 Evidence: Pre-Rename and Post-Rename Transition

Task 1 is a `checkpoint:human-action` gate and produces no commit of its own; its acceptance criteria require the before/after transition to be recorded here rather than asserted.

**Pre-rename reading**, captured before the checkpoint was raised (2026-09-13):
```
gh api repos/henols/firestarter --jq '.full_name'  ->  henols/firestarter
gh api repos/henols/firestarter --jq '.id'         ->  810276812
gh api repos/henols/firestarter_fw                 ->  404 Not Found (HTTP 404)
```

The operator then performed the rename via the GitHub Settings page (Settings → General → Repository name, `firestarter` → `firestarter_fw`) and reported "renamed".

**Post-rename verification**, re-measured live in this session (2026-09-13T13:59Z), not copied from any prior reading:
```
repos/henols/firestarter      .id        -> 810276812
repos/henols/firestarter      .full_name -> henols/firestarter_fw
repos/henols/firestarter_fw   .id        -> 810276812
repos/henols/firestarter_prom .id        -> 1232995399
```

The old slug's id is unchanged (810276812) and its full_name now reads `henols/firestarter_fw`; the new slug resolves to the same id; the meta repository's id (1232995399) is distinct, confirming the old slug was not re-occupied and D-1 has not been violated.

**No task in this plan ran a rename command, a PATCH against the repository, or any repository-modifying call.** Task 1's only action was to hand the rename to the operator and record the pre-rename reading; Task 2's only actions were read-only `gh api` queries and a file write/commit.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required. (Task 1's `user_setup` entry describing the GitHub rename was the operator action itself, already completed and cleared before this continuation.)

## Next Phase Readiness

- RENAME-01 is complete and evidenced. Plans 189-02, 189-03 and 189-04 may now proceed — none of them re-opens D-1, D-7, D-11 or D-12.
- The firmware gitlink advance (D-05) is explicitly deferred to 189-02/03, after the fresh-clone demonstration; this plan touched no submodule.
- Branch `v1.38-repository-rename` unchanged throughout; nothing was pushed.

## Self-Check: PASSED

- `.planning/phases/189-free-the-name/evidence/189-rename-01-identity.txt` — FOUND on disk.
- Commit `c2047210` — FOUND in `git log --oneline --all`.
- All four transcript readings match the values re-measured live in this session.
- `.planning/config.json` not modified by any `gsd_run` call during this task.
- Branch still `v1.38-repository-rename` after the commit.

---
*Phase: 189-free-the-name*
*Completed: 2026-09-13*
