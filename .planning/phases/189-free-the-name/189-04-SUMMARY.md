---
phase: 189-free-the-name
plan: 04
subsystem: infra
tags: [git-submodule, gitmodules, github-branch-protection, pull-request]

# Dependency graph
requires:
  - phase: 189-01
    provides: "Operator-performed GitHub rename of henols/firestarter to henols/firestarter_fw, confirmed live via numeric-id identity transcript"
  - phase: 189-02
    provides: ".gitmodules firmware URL repointed on the milestone branch, plus the three D-03 observables and the D-08 branch-disposition wording drafted in evidence/189-rename-02-observables.txt"
provides:
  - "The same one-line .gitmodules firmware-URL change landed on the meta repository's main branch, through a pull request (the only route branch protection allows)"
  - "A single evidence record, evidence/189-rename-02-branch-disposition.md, answering ROADMAP criterion 2's \"on both beta and main\" for all three branches this phase touches: the milestone branch (done), main (done via pull request), and beta (close-carried per D-08)"
affects: [190, 191, close]

# Actuals (#2632)
actuals:
  tokens: 1100
  tasks: 1
  commits: 1
  plan_head_before: 9a5adba52bb8d2a69dccd38bd908081d95bba6fe

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "A protected default branch is reached only through a prepared local branch (built in a scratch worktree, off origin/main) plus an operator-performed push/PR/merge behind a blocking-human checkpoint (D-7) -- the agent never pushes, opens, or merges."
    - "The merged state of a protected branch is verified by reading the file back from the GitHub contents API at the target ref, never from the local clone, since a local branch proves only what was prepared, not what landed."

key-files:
  created:
    - .planning/phases/189-free-the-name/evidence/189-rename-02-branch-disposition.md
  modified: []

key-decisions:
  - "D-07 honored: the main-branch .gitmodules change landed as its own pull request inside Phase 189, independent of Phase 191's firestarter_app main work."
  - "D-08 honored: the branch-disposition record states the beta half as close-carried -- a deliberate routing decision, not an incomplete requirement -- and states why an early beta merge is not an option (it fires a pre-release cut in both sub-repositories and publishes the host one to PyPI)."
  - "Verification for Task 3 was read from GitHub's contents API at ref=main, independently re-run rather than copied from the operator's or the continuation prompt's reported numbers, per the plan's must_haves."

requirements-completed: [RENAME-02]

coverage:
  - id: D1
    description: "The meta repository's main branch carries the repointed firmware submodule URL, landed via pull request henols/firestarter_prom#79 and merged (sha 6b518c74831c6d3cf56513d80134684fbd673fef), with the change verified by reading .gitmodules back from GitHub at ref=main rather than from the local clone"
    requirement: "RENAME-02"
    verification:
      - kind: other
        ref: "gh api \"repos/henols/firestarter_prom/contents/.gitmodules?ref=main\" -H \"Accept: application/vnd.github.raw\", asserted against three greps (new-URL count 1, bare-slug count 0, firestarter_app positive-control count 1) and recorded in evidence/189-rename-02-branch-disposition.md"
        status: pass
    human_judgment: false
  - id: D2
    description: "A single record exists answering ROADMAP criterion 2's \"on both beta and main\" for all three branches this phase's scope touches, so a verifier does not misread the deliberately close-carried beta half as incomplete"
    requirement: "RENAME-02"
    verification:
      - kind: other
        ref: "evidence/189-rename-02-branch-disposition.md contains one row each for v1.38-repository-rename, main and beta, with the beta row using the word close-carried; grep counts recorded above"
        status: pass
    human_judgment: false

duration: ~7min (Task 3 only, this continuation)
completed: 2026-09-13
status: complete
---

# Phase 189 Plan 04: Free the Name — Main-Branch Pull Request and Branch Disposition Summary

**Landed the one-line firmware-submodule URL change on the meta repository's protected `main` branch via operator-merged pull request `henols/firestarter_prom#79`, and recorded a single evidence file resolving RENAME-02's "on both `beta` and `main`" across all three branches this phase touches.**

## Performance

- **Duration:** Task 1 (prepare) and Task 3 (verify + record) were both agent-executed; Task 2 was the operator-performed push/PR/merge at a `blocking-human` gate in between. This continuation covered Task 3 only, ~7 minutes.
- **Started (this continuation):** 2026-09-13T14:19:xx Z (Task 1 commit already in place)
- **Completed:** 2026-09-13T14:26:12Z
- **Tasks:** 3 total (1 auto, 1 checkpoint:human-action, 1 auto) — all three complete
- **Files modified:** 1 (created)

## Accomplishments
- Prepared branch `v1.38-gitmodules-main` (Task 1, prior session) in a scratch worktree off `origin/main`, containing exactly one commit that changes one line of `.gitmodules` — the firmware submodule URL — with the section name, `path = firestarter`, and the untouched `firestarter_app` section all preserved.
- The operator pushed that branch, opened pull request `henols/firestarter_prom#79` against `main`, and merged it (Task 2, operator-performed at a `blocking-human` gate; not re-run or re-raised by this agent).
- Independently re-verified the merge against GitHub — not against the operator's report and not against the local clone — reading `repos/henols/firestarter_prom/pulls/79` (`merged: true`, `merge_commit_sha: 6b518c74831c6d3cf56513d80134684fbd673fef`) and `.gitmodules` at `ref=main` via the contents API, confirming exactly one occurrence of `git@github.com:henols/firestarter_fw.git`, zero bare-slug references, and one `firestarter_app` positive control (proving the zero was a real absence, not an empty response).
- Wrote `.planning/phases/189-free-the-name/evidence/189-rename-02-branch-disposition.md`, the phase's single answer to ROADMAP criterion 2's "on both `beta` and `main`": the milestone branch is done (commit `5aba9dbc8d760e530638931d19ede0a227dd1a60`, from `189-02`), `main` is done via the merged pull request above, and `beta` is recorded as close-carried per D-08 — a deliberate routing decision, not an incomplete requirement, because an early `beta` merge would fire a pre-release cut in both sub-repositories and publish the host one to PyPI.

## Task Commits

Each task was committed atomically:

1. **Task 1: Prepare the one-line main-branch change on v1.38-gitmodules-main** — `d1a83997` (fix, on branch `v1.38-gitmodules-main`, not on `v1.38-repository-rename`) — completed in a prior session.
2. **Task 2: Operator pushes v1.38-gitmodules-main, opens the PR and merges it** — operator-performed; no agent commit. Landed as pull request `henols/firestarter_prom#79`, merge commit `6b518c74831c6d3cf56513d80134684fbd673fef`.
3. **Task 3: Verify the merged main and record the RENAME-02 branch disposition** — `a428b487` (docs, on `v1.38-repository-rename`)

**Plan metadata:** pending (this commit, docs: complete plan)

_Note: Task 1's commit lives on the separate branch `v1.38-gitmodules-main`, prepared in a scratch worktree that has since been removed; it is not an ancestor of `v1.38-repository-rename`'s history, which is why the `actuals.commits` count above (measured against this plan's ledger on the primary branch) reads 1 rather than 2._

## Files Created/Modified
- `.planning/phases/189-free-the-name/evidence/189-rename-02-branch-disposition.md` - the RENAME-02 branch-disposition record: one row each for the milestone branch (done), `main` (done via PR #79, with the GitHub read-back and its capture timestamp), and `beta` (close-carried per D-08)

## Decisions Made
- Followed D-07 and D-08 exactly as specified in `189-CONTEXT.md`; no architectural deviation.
- Re-ran every verification reading myself against the live GitHub API rather than trusting the operator's or the continuation prompt's reported PR number and merge sha — the prompt's `<task_2_result>` explicitly asked for this, and the plan's `must_haves` require the merged state to be "verified against GitHub rather than against the local clone."

## Deviations from Plan

None - plan executed exactly as written. All three `<verify>` legs for Task 3 were re-run live and passed (new-URL count 1, bare-slug count 0, positive-control count 1, `close-carried` count 3, `v1.38-repository-rename` count 2, branch still `v1.38-repository-rename`). No `must_haves.prohibitions` were violated: no push, pull request creation, or merge was performed by this agent; nothing was merged or fast-forwarded onto `beta`; the primary working tree was never switched away from `v1.38-repository-rename`.

## Issues Encountered

None. The untracked scratch paths `anything.txt` and `tmp/` at the repository root were present at task start and left untouched, per the branch-and-repo constraints. `.planning/config.json` was not modified by any `gsd-tools` invocation during this task (none was invoked for Task 3's file-writing work).

## User Setup Required

None for this continuation — Task 2's `user_setup` (push/PR/merge) was already completed by the operator before this continuation began, and is recorded as such above, not re-raised.

## Next Phase Readiness
- RENAME-02 is now fully evidenced across all three named branches. `.planning/phases/189-free-the-name/evidence/189-rename-02-branch-disposition.md` is the single record a verifier or a future phase should read for "on both `beta` and `main`."
- `beta`'s close-carried disposition (D-08) is explicit and will need no further action from this phase; it lands automatically when the milestone merges.
- Branch `v1.38-repository-rename` unchanged throughout this plan; nothing was pushed, opened, or merged by the agent at any point; the local branch `v1.38-gitmodules-main` remains in place, un-deleted, per the constraints.

## Self-Check: PASSED

- `.planning/phases/189-free-the-name/evidence/189-rename-02-branch-disposition.md` - FOUND on disk, contains "close-carried" (3 occurrences) and "v1.38-repository-rename" (2 occurrences).
- Commit `a428b487` - FOUND in `git log --oneline --all`.
- Commit `d1a83997` - FOUND in `git log --oneline --all` (on branch `v1.38-gitmodules-main`).
- Pull request `henols/firestarter_prom#79` - confirmed merged via `gh api repos/henols/firestarter_prom/pulls/79` (`merged: true`, `merge_commit_sha: 6b518c74831c6d3cf56513d80134684fbd673fef`).
- Branch still `v1.38-repository-rename` after the commit.
- `.planning/config.json` not modified during this task.

---
*Phase: 189-free-the-name*
*Completed: 2026-09-13*
