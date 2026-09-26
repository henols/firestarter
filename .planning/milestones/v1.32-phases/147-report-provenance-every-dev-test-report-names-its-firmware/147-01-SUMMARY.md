---
phase: 147-report-provenance-every-dev-test-report-names-its-firmware
plan: 01
subsystem: infra
tags: [git, submodule, branching, gitignore, skills, pytest]

# Dependency graph
requires: []
provides:
  - "firestarter_app on gsd/v1.32-at28c-write-path-root-cause-report-provenance, content-identical to origin/beta (3.0.0b21)"
  - "Recorded green full-suite baseline (1590 passed, 1 warning, 243.38s) for later Phase 147 plans to regress against"
  - ".claude/skills/devtest-triage/{SKILL.md,scripts/devtest_issues.py} tracked in the meta repo at their current, unmodified content"
  - ".gitignore un-ignore of .claude/skills/ committed in the meta repo"
affects: [147-02, 147-03, 147-04, 147-05, 147-06]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Verify sub-repo branch base by content diff (git diff --stat), not merge-base ancestry — ancestry is merge-shape-dependent"
    - "Stage named paths only in a dirty multi-repo meta tree; never git add -A"

key-files:
  created: []
  modified:
    - .gitignore
    - .claude/skills/devtest-triage/SKILL.md
    - .claude/skills/devtest-triage/scripts/devtest_issues.py

key-decisions:
  - "Unset upstream tracking (git branch --unset-upstream) after checking out firestarter_app's new branch from origin/beta, matching the meta repo's own milestone-branch convention of no upstream tracking — avoids an accidental push to beta"

patterns-established: []

requirements-completed: []

coverage:
  - id: D1
    description: "firestarter_app moved to gsd/v1.32-at28c-write-path-root-cause-report-provenance, forked off origin/beta (3.0.0b21), content-verified against v1.31 tip by git diff --stat"
    verification:
      - kind: other
        ref: "cd /workspaces/firestarter_app && git branch --show-current && git diff --stat gsd/v1.31-27c-programming-algorithm-fidelity origin/beta && git diff --stat HEAD origin/beta && python3 -c \"import firestarter; print(firestarter.__version__)\""
        status: pass
    human_judgment: false
  - id: D2
    description: "Full app test suite green on the new branch; pass count recorded as the Phase 147 baseline"
    verification:
      - kind: other
        ref: "cd /workspaces/firestarter_app && python3 -m pytest tests/ -o addopts=\"\" -q  =>  1590 passed, 1 warning in 243.38s"
        status: pass
    human_judgment: false
  - id: D3
    description: ".gitignore un-ignore of .claude/skills/ and first-ever tracking of the devtest-triage skill baseline (SKILL.md + scripts/devtest_issues.py), committed byte-identical to the pre-existing working-tree content"
    verification:
      - kind: other
        ref: "git ls-files .claude && git show HEAD --stat && git show HEAD:.gitignore | grep -c '^!\\.claude/skills/$' && git diff HEAD -- .claude/skills/devtest-triage && git status --porcelain .claude/skills/devtest-triage && git ls-files .claude/skills/find-skills"
        status: pass
    human_judgment: false

duration: ~15min
completed: 2026-08-18
status: complete
---

# Phase 147 Plan 01: Sub-repo branch move + devtest-triage skill tracking Summary

**Moved `firestarter_app` onto `gsd/v1.32-…` forked off `origin/beta` (3.0.0b21), recorded a 1590-passed baseline, and tracked the devtest-triage skill files in the meta repo for the first time via a `.gitignore` un-ignore.**

## Performance

- **Duration:** ~15 min
- **Completed:** 2026-08-18
- **Tasks:** 2
- **Files modified:** 3 (meta repo: `.gitignore`, `.claude/skills/devtest-triage/SKILL.md`, `.claude/skills/devtest-triage/scripts/devtest_issues.py`); `firestarter_app`: branch checkout only, no file edited, no commit

## Accomplishments

- `firestarter_app` HEAD moved from `gsd/v1.31-27c-programming-algorithm-fidelity` to a new branch `gsd/v1.32-at28c-write-path-root-cause-report-provenance`, checked out directly from `origin/beta`. Verified by content (`git diff --stat gsd/v1.31-27c-programming-algorithm-fidelity origin/beta` → exactly `firestarter/__init__.py | 2 +-`, one insertion/one deletion) rather than ancestry, per RESEARCH F-15's caution. `git diff --stat HEAD origin/beta` is empty (identical content) and `firestarter.__version__` reads `3.0.0b21`.
- Unset the new branch's upstream tracking (`git branch --unset-upstream`) after checkout — `git checkout -b <branch> origin/beta` auto-sets `origin/beta` as upstream, which would make a bare `git push` target the shared beta branch. This matches the meta repo's own milestone branch, which also carries no upstream.
- Ran the full app test suite on the new branch: `1590 passed, 1 warning in 243.38s (0:04:03)`, 30 snapshots passed. This is the RESEARCH assumption-A4 baseline every later plan in Phase 147 regresses against (matches the RESEARCH-measured `≥1590 passed` floor exactly).
- Committed the meta repo's already-present, unstaged `.gitignore` un-ignore (`.claude/*` + `!.claude/skills/`, keeping `scripts/__pycache__/` and the marketplace-installed `find-skills/` ignored) together with the two devtest-triage files at their current, unmodified content — `.claude/skills/devtest-triage/SKILL.md` and `.claude/skills/devtest-triage/scripts/devtest_issues.py`. `git diff HEAD -- .claude/skills/devtest-triage` is empty, confirming a byte-identical baseline commit.
- Staged named paths only throughout (`git add .gitignore .claude/skills/devtest-triage/SKILL.md .claude/skills/devtest-triage/scripts/devtest_issues.py`) — never `git add -A`. `git ls-files .claude` now lists exactly the two intended paths; `git ls-files .claude/skills/find-skills` is empty (marketplace skill stayed untracked).

## Task Commits

1. **Task 1: Move firestarter_app to the v1.32 branch off origin/beta and record the green baseline** — no commit (branch checkout + baseline measurement only, as the plan specifies; the app repo tree remains clean of any edit and no gitlink was staged in the meta repo).
2. **Task 2: Land the meta .gitignore un-ignore and track the devtest-triage skill baseline** — `1a49ebe5` (chore)

**Plan metadata:** committed via this SUMMARY + STATE.md + ROADMAP.md docs commit (see below).

## Files Created/Modified

- `.gitignore` - un-ignore `.claude/skills/` (was blanket `.claude/`); keeps `scripts/__pycache__/` and `find-skills/` ignored; carries a trailing `node_modules` line as an unrelated pre-existing hunk
- `.claude/skills/devtest-triage/SKILL.md` - tracked for the first time, unmodified content
- `.claude/skills/devtest-triage/scripts/devtest_issues.py` - tracked for the first time, unmodified content
- `firestarter_app` (submodule, not committed here) - branch state only: now on `gsd/v1.32-at28c-write-path-root-cause-report-provenance` at `origin/beta`'s tip (`7aae46c`)

## Decisions Made

- Unset upstream tracking on the new `firestarter_app` branch after `git checkout -b … origin/beta` auto-set it, to avoid a bare `git push` accidentally targeting the shared `beta` branch. Matches the meta repo's own convention (its active milestone branch also carries no upstream).
- Confirmed the one expected unrelated hunk in the `.gitignore` diff (trailing `node_modules` line) is correct for the pre-existing untracked `package.json`/`package-lock.json` and left it in place rather than splitting the commit, per the plan's explicit instruction to land it "together with" the skill files and document it rather than "fix" it.

## Deviations from Plan

None - plan executed exactly as written.

One acceptance-criterion wording note (not a deviation, since it required no fix): Task 1's acceptance criterion `cd /workspaces/firestarter_app && git status --porcelain` prints no output` does not hold literally — the app repo tree carries six **pre-existing** untracked files (`.planning/config.json`, `SECURITY.md`, `datasheets/M27C1001.pdf`, `datasheets/M27C512.pdf`, `datasheets/W27C512.pdf`, `datasheets/W27E257.pdf`, `write_test_port.sh`) that were present before this plan touched anything (captured in the session's very first `git status` call, prior to any branch checkout) and persist unchanged across the branch move. Per the deviation-rules SCOPE BOUNDARY, these are out of scope for this plan — not caused by Task 1, not fixed, not committed. `git diff HEAD origin/beta` (tracked-content identity) and `git diff --stat` (branch-base content) are the load-bearing oracles this task actually relies on, and both pass exactly as specified.

## Issues Encountered

The full-suite pytest run (`python3 -m pytest tests/ -o addopts="" -q`) exceeds the 120s default Bash timeout and was moved to background automatically; re-ran and read the background output file directly rather than retrying in the foreground. No functional issue — just a longer-than-2-minutes command.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- `firestarter_app` is unblocked for plans 147-02 through 147-05 to make source edits and gitlink-bumping commits on top of `gsd/v1.32-at28c-write-path-root-cause-report-provenance`.
- Plan 147-06 can now edit `.claude/skills/devtest-triage/{SKILL.md,scripts/devtest_issues.py}` as a reviewable tracked-file diff instead of an untracked-file add.
- The 1590-passed baseline is available in this SUMMARY for any later plan's regression comparison.
- No blockers.

## Self-Check: PASSED

- FOUND: `/workspaces/firestarter_app` on branch `gsd/v1.32-at28c-write-path-root-cause-report-provenance`
- FOUND: commit `1a49ebe5` in meta repo (`git log --oneline --all | grep 1a49ebe5`)
- FOUND: `.claude/skills/devtest-triage/SKILL.md` and `.claude/skills/devtest-triage/scripts/devtest_issues.py` tracked (`git ls-files .claude`)

---
*Phase: 147-report-provenance-every-dev-test-report-names-its-firmware*
*Completed: 2026-08-18*
