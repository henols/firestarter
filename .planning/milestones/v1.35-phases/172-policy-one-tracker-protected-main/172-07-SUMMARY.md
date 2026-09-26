---
phase: 172-policy-one-tracker-protected-main
plan: 07
subsystem: infra
tags: [github, pull-request, ci, rulesets, wiki-check, branch-protection]

# Dependency graph
requires:
  - phase: 172-policy-one-tracker-protected-main
    provides: "plan 172-06's active, enforcing 'Protect main' ruleset on all three repositories (verified via evidence/172-06-ruleset-readback.txt before this plan's Task 1 ran)"
provides:
  - "Three open, narrow pull requests carrying only .github/ paths into three protected main branches: firestarter_prom#54, firestarter#58, firestarter_app#57"
  - "A measured, tree-inspected Pitfall 5 verdict: merging the firmware PR will not fire build.yml (main's own paths-ignore already excludes .github/**, and py32f071.yml does not exist on main at all)"
  - "Server-side proof (gh pr view --json files) that each PR's scope is .github/-only, not merely the local diff's claim"
affects: [172-08, 173-policy-05]

# Actuals (#2632)
actuals:
  tokens: 1200
  tasks: 3
  commits: 2

tech-stack:
  added: []
  patterns: ["throwaway git worktrees cut from origin/main for building narrow-scope PR branches without touching the working checkout", "server-side scope verification via gh pr view --json files rather than trusting the local diff", "reading a PR's own check-run list as a free oracle before proposing any merge"]

key-files:
  created:
    - .planning/phases/172-policy-one-tracker-protected-main/evidence/172-07-pr-branches.txt
    - .planning/phases/172-policy-one-tracker-protected-main/evidence/172-07-pr-scope.txt
    - .planning/phases/172-policy-one-tracker-protected-main/evidence/172-07-fw-checkruns.txt
  modified: []

key-decisions:
  - "Three policy/contributor-policy branches were cut fresh from each repository's own fetched origin/main in a throwaway worktree, never from the milestone branch — this is the load-bearing choice the whole plan exists to enforce (a milestone-branch head would have carried 733/531/781 commits into a default branch)"
  - "The Pitfall 5 firmware-release question was answered by direct tree inspection, not inference from an empty check-run list alone: origin/main's own build.yml (a pre-refactor, 531-commits-behind copy) already lists '.github/**' in paths-ignore, and py32f071.yml is entirely absent from main's tree, so neither workflow can fire on the pushed branch — both causes independently sufficient, making the empty check-run list overdetermined rather than a registration-timing artifact"
  - "The coordinator's mid-execution message (resolving the two open questions ahead of Task 3) was incorporated into the recorded verdict, but the verdict itself was independently re-derived and measured from the actual origin/main tree rather than taken on the coordinator's say-so — the coordinator's bottom-line prediction (no release cut) held, but the mechanism differs and is stronger (an explicit '.github/**' exclusion plus a wholly absent workflow file, not merely a '**.md' match)"
  - "No requirement IDs (POLICY-02, LEGACY-01) were marked complete — gsd-tools query requirements.ready-ids reports 0/2 ready because sibling plans 172-08 and 172-09 also declare them and have not yet produced a SUMMARY.md"

requirements-completed: []

coverage:
  - id: D1
    description: "Three PR branches built in throwaway worktrees, each one commit ahead of its own repository's origin/main, carrying only .github/ paths"
    requirement: "POLICY-02"
    verification:
      - kind: other
        ref: "evidence/172-07-pr-branches.txt (git rev-list --count, git diff --name-only, both automated <verify> legs of Task 1)"
        status: pass
    human_judgment: false
  - id: D2
    description: "Three branches pushed and three pull requests opened into main, none with the milestone branch as head"
    requirement: "POLICY-02"
    verification:
      - kind: other
        ref: "evidence/172-07-pr-scope.txt (gh pr view --json files/headRefName/baseRefName, server-side, Task 3's automated <verify>)"
        status: pass
    human_judgment: false
  - id: D3
    description: "The firmware PR's own check-run list read and the Pitfall 5 verdict recorded explicitly before any merge is proposed"
    requirement: "LEGACY-01"
    verification:
      - kind: other
        ref: "evidence/172-07-fw-checkruns.txt (gh api check-runs, cross-checked against git ls-tree on origin/main and gh api actions/runs)"
        status: pass
    human_judgment: true
    rationale: "The verdict (no release cut) rests on reading GitHub's actual trigger behavior against a specific tree state; plan 172-08, which owns the merges, should re-read this evidence file before acting on it rather than treating this SUMMARY's restatement as sufficient on its own."

duration: ~15min active (across two segments separated by the Task 2 human-action checkpoint, which paused across the day boundary awaiting operator authorization)
completed: 2026-09-02
status: complete
---

# Phase 172 Plan 07: Three `.github`-only pull requests into protected `main` branches Summary

**Pushed three `policy/contributor-policy` branches — built in throwaway worktrees cut from each repository's own `origin/main`, never the milestone branch — and opened three narrow pull requests (`firestarter_prom#54`, `firestarter#58`, `firestarter_app#57`); server-side file lists prove `.github/`-only scope, and the firmware PR's own check-run list, cross-checked against `origin/main`'s actual workflow tree, shows the merge will not fire `build.yml`. No merge performed.**

## Performance

- **Duration:** ~15 min of active execution, split by the Task 2 human-action checkpoint (operator authorization arrived after a day-boundary pause)
- **Started:** 2026-09-01T21:4x (Task 1)
- **Completed:** 2026-09-02T07:47:42Z (Task 3)
- **Tasks:** 3 (Task 1 auto, Task 2 checkpoint:human-action, Task 3 auto)
- **Files modified:** 3 created (all evidence files, meta repo only)

## Accomplishments
- Built and locally verified three one-commit-ahead PR branches (`prom`: 6 `.github/` paths including `wiki-check.yml`; `firestarter` and `firestarter_app`: 1 `.github/CONTRIBUTING.md` each) without ever switching branches in the three working checkouts
- Pushed all three branches and opened all three pull requests after explicit operator authorization at the Task 2 gate
- Proved each PR's scope from the GitHub API (`gh pr view --json files`), not the local diff — 8 total `.github/` paths, zero paths outside `.github/`
- Answered the Pitfall 5 question (does the `.github`-only merge cut a firmware release?) definitively: **no** — `origin/main`'s own `build.yml` already excludes `.github/**` via `paths-ignore`, and `py32f071.yml` does not exist on `main`'s tree at all, so neither workflow can trigger on the pushed branch

## Task Commits

Each task was committed atomically:

1. **Task 1: Build three PR branches in throwaway worktrees cut from origin/main, and prove their scope before anything is pushed** - `cff88081` (docs) — meta-repo evidence commit; the three branch commits themselves (`4b87023a` prom, `579f04a` firestarter, `992f111` firestarter_app) exist in the throwaway worktrees, not yet pushed at this point
2. **Task 2: checkpoint:human-action** — no commit (gate only); operator typed "go", authorizing Task 3
3. **Task 3: Push, open the three pull requests, and read the firmware PR's own check list** - `6ed53a87` (docs) — meta-repo evidence commit, after the three branches were pushed (`git push -u origin HEAD` ×3) and the three PRs opened (`gh pr create` ×3, none denied by the harness classifier)

**Plan metadata:** captured in this SUMMARY's own commit (below)

## Files Created/Modified
- `.planning/phases/172-policy-one-tracker-protected-main/evidence/172-07-pr-branches.txt` - per-repository branch name, base sha, ahead-count, and full `.github/`-only path list, recorded before anything was pushed; also records the one documented pre-existing-file deviation (see below)
- `.planning/phases/172-policy-one-tracker-protected-main/evidence/172-07-pr-scope.txt` - server-side `gh pr view --json files/headRefName/baseRefName` read-back for all three open pull requests
- `.planning/phases/172-policy-one-tracker-protected-main/evidence/172-07-fw-checkruns.txt` - firmware PR number, head sha, the (empty) check-run list read twice 15 seconds apart, and the explicit Pitfall 5 verdict with its measured root cause

Outside meta (not committed here, GitHub-side state only): three pushed `policy/contributor-policy` branches (`henols/firestarter_prom`, `henols/firestarter`, `henols/firestarter_app`) and three open pull requests (`#54`, `#58`, `#57`).

## Decisions Made
See `key-decisions` in frontmatter. In summary: branches were cut from `origin/main` in throwaway worktrees (never the milestone branch), the Pitfall 5 verdict was independently re-derived from the actual tree rather than accepted from the coordinator's prediction alone, and requirement IDs were left unmarked pending sibling plans 172-08/172-09.

## Deviations from Plan

### Auto-fixed Issues

None — no bugs, missing functionality, or blockers required fixing during execution.

### Documented Non-Fixes (out of scope, not auto-fixed)

**1. [Scope boundary] Task 1's second automated `<verify>` leg reports `firestarter_app` as non-porcelain-clean**
- **Found during:** Task 1
- **Issue:** The plan's second automated verify command asserts `git -C firestarter_app status --porcelain` is empty. It is not: `tools/build_db.py` carries an unstaged modification.
- **Root cause:** This modification pre-dates this plan's Task 1 entirely — confirmed present in the very first `git status` check of this session, before any fetch, worktree, or checkout operation ran. It is explicitly named in the orchestrator's `working_tree_note` as an unrelated, pre-existing modification that must not be touched or committed.
- **Fix:** None applied — touching it is out of scope and explicitly forbidden. The worktree operations added zero net change to this file (confirmed: the diff is unchanged before and after).
- **Files modified:** none (deliberately left untouched)
- **Verification:** `git -C /workspaces/firestarter_app diff --stat -- tools/build_db.py` shows the same 2-line change both before Task 1 began and after Task 3 completed
- **Committed in:** not committed (intentionally left as working-tree state, per instruction)

**Total deviations:** 0 auto-fixed, 1 documented non-fix (pre-existing, out-of-scope, explicitly forbidden to touch). **Impact:** none — the underlying invariant the verify leg exists to prove (worktree operations did not disturb the working checkouts) holds; the one non-empty status line is unrelated to this plan's actions.

## Authentication Gates

None. `gh auth status` was already authenticated (`henols`, scopes `gist, read:org, repo, workflow`) throughout.

## Known Stubs

None.

## Threat Flags

None — this plan's three STRIDE threats (T-172-27 milestone-branch-as-head, T-172-28 unintended firmware release, T-172-29 accidental `git switch`) were all in the plan's own `<threat_model>` and are exactly what the evidence files and verify legs above discharge; no new, unlisted surface was introduced.

## Self-Check: PASSED

- `[ -f .planning/phases/172-policy-one-tracker-protected-main/evidence/172-07-pr-branches.txt ]` → FOUND
- `[ -f .planning/phases/172-policy-one-tracker-protected-main/evidence/172-07-pr-scope.txt ]` → FOUND
- `[ -f .planning/phases/172-policy-one-tracker-protected-main/evidence/172-07-fw-checkruns.txt ]` → FOUND
- `git log --oneline --all --grep="172-07"` → FOUND (`cff88081`, `6ed53a87`)
- All task-level `<acceptance_criteria>` re-verified: Task 1's two automated `<verify>` legs both re-run (first: exit 0; second: exit 1 on the single pre-existing, documented, out-of-scope line, addressed above); Task 3's two automated `<verify>` legs both re-run at exit 0
- Plan-level `<verification>` re-checked: three open PRs (head `policy/contributor-policy`, base `main`) ✓; 8 total `.github/` paths, none outside `.github/` ✓; all three working checkouts still on the milestone branch, `firestarter` porcelain-clean, `firestarter_app` clean except the documented pre-existing file ✓; firmware check-run list captured with explicit verdict ✓; no merge performed ✓ (`gh pr list` re-checked `mergeable: MERGEABLE, state: OPEN` for all three immediately before this SUMMARY was written)

Next: Phase 172 has one more execution plan, 172-08 (merges), plus 172-09. Ready for 172-08.
