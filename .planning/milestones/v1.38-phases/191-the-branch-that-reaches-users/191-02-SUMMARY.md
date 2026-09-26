---
phase: 191-the-branch-that-reaches-users
plan: 02
subsystem: testing
tags: [pip-install, github-releases-api, branch-protection, backlog, firestarter_app, main]

# Dependency graph
requires:
  - phase: 191-01
    provides: "The board-free STABLE-02 install fixture that will later measure this plan's change"
provides:
  - "A local, unpushed firestarter_app branch v1.38-url-02-main (one commit, three files, forked from origin/main) that repoints the sole firmware-release constant to henols/firestarter_fw and bumps __version__ to 2.0.9"
  - "Two backlog items recording main's stable release pipeline defects (release.yml auto-commit vs. Protect main ruleset; publish.yml's release:published trigger never firing), each naming beta-release.yml's pypi job as the proven fix"
  - "A readings transcript (191-url-02-prepared-branch.txt) proving the prepared branch's diff, the boundary-aware slug sweep, and its non-vacuity control"
affects: [191-03, 191-04, 191-05]

# Actuals (#2632)
actuals:
  tokens: 2687
  tasks: 2
  commits: 2
  plan_head_before: b95e02517c842e424f01a58b5af79d5c2f21d089

tech-stack:
  added: []
  patterns:
    - "Protected-branch changes are prepared in a scratch worktree (mktemp -d, outside /workspaces) off origin/main, committed there with plain git commit, then the worktree is removed and the branch survives — never pushed, opened, or merged by the agent (189-04 precedent, reused unmodified)."
    - "A boundary-aware slug sweep (henols/firestarter([^_a-zA-Z0-9]|$)) always runs alongside a non-vacuity positive control (henols/firestarter_app) in the same transcript, so a zero reads as a real absence rather than an empty response."

key-files:
  created:
    - .planning/todos/pending/2026-09-13-release-yml-autocommit-vs-ruleset.md
    - .planning/todos/pending/2026-09-13-publish-yml-release-published-never-fires.md
    - .planning/phases/191-the-branch-that-reaches-users/evidence/191-url-02-prepared-branch.txt
  modified: []

key-decisions:
  - "Followed D-01 exactly: repointed the one FIRESTARTER_RELEASE_URL constant that exists on origin/main; did not backport FIRESTARTER_RELEASES_URL or FIRESTARTER_RELEASE_BY_TAG_URL, which are beta-only surface with no consumer on main."
  - "The third D-09 finding (_compare_versions cannot parse a 3.0.0bNN firmware string on main) is recorded here as a SUMMARY observation rather than a third backlog item — Claude's Discretion per the plan; see Deviations/Observations below."
  - "No GSD state-writing verb was invoked during this plan's execution, so the .planning/config.json sub_repos prune hazard the plan warns about never had an opportunity to fire; verified intact by direct read before and after both tasks."

requirements-completed: [URL-02]

coverage:
  - id: D1
    description: "Branch v1.38-url-02-main exists off origin/main with exactly one commit touching three files (constants.py, README.md, __init__.py) at 1 insertion/1 deletion each; the repointed constant, README link and version string all read as specified; boundary-aware slug sweep is zero with a non-zero positive control; no comment added; no worktree or gitlink left dangling."
    requirement: URL-02
    verification:
      - kind: other
        ref: "Task 1's 12 automated <verify> legs (rev-parse, numstat count=3, 1/1 count=3, constant grep=1, __init__.py content, bare-slug sweep=0, positive control=6, comment-added grep=0, worktree-list grep=0, both branch --show-current checks, meta gitlink diff=0) -- all run directly, all pass"
        status: pass
    human_judgment: false
  - id: D2
    description: "Both pipeline-defect backlog items exist, are frontmatter-valid, name beta-release.yml as the proven pattern, and record their measurements (ruleset 22046179, workflow_dispatch-only run history, the on-disk GitHub-2.0.8-vs-PyPI-2.0.7 inconsistency); no .github/workflows/ file was modified in any repository"
    requirement: URL-02
    verification:
      - kind: other
        ref: "Task 2's 7 automated <verify> legs (file existence, beta-release.yml mention x2, workflow_dispatch mention, 22046179 mention, resolves_phase: unassigned x2, app .github porcelain=0, meta todos+config porcelain pre-commit) -- all run directly, all pass"
        status: pass
    human_judgment: false

duration: 6min
completed: 2026-09-13
status: complete
---

# Phase 191 Plan 02: URL-02's Prepared Branch and Filed Pipeline Defects Summary

**Prepared one local, unpushed firestarter_app commit that repoints `FIRESTARTER_RELEASE_URL` to `henols/firestarter_fw` and bumps `__version__` to 2.0.9 on a scratch branch off `origin/main`, and filed the two pipeline defects (a ruleset-rejected auto-commit push, and a `release: published` trigger that has never fired) that will stop that commit reaching PyPI on its own.**

## Performance

- **Duration:** ~6 min
- **Started:** 2026-09-13T20:38:30Z
- **Completed:** 2026-09-13T20:43:54Z
- **Tasks:** 2
- **Files modified:** 6 (3 in `firestarter_app` on the new branch only, 3 new in the meta repository)

## Accomplishments
- Created a scratch worktree of `firestarter_app` outside `/workspaces` (`mktemp -d`), forked branch `v1.38-url-02-main` off `origin/main`, made exactly three one-line edits (`constants.py`'s URL literal, `README.md:17`'s firmware link, `firestarter/__init__.py`'s version), committed with plain `git commit`, and removed the worktree — the branch survives, unpushed, waiting for the operator (189-04 precedent, reused unmodified).
- Verified the prepared branch twelve ways: exactly three files at 1/1 each against `origin/main`; the constant, README link and version string read exactly as specified; a boundary-aware slug sweep (`henols/firestarter([^_a-zA-Z0-9]|$)`) over the branch returns zero with a six-file, non-zero `henols/firestarter_app` positive control in the same run; zero added comment lines in either Python file; no dangling worktree entry; both primary working trees (meta and `firestarter_app`) still on their milestone branches; the meta repository's `firestarter_app` gitlink unchanged.
- Captured the full readings transcript to `.planning/phases/191-the-branch-that-reaches-users/evidence/191-url-02-prepared-branch.txt` and committed it in the meta repository.
- Filed two backlog items under `.planning/todos/pending/`, each naming `beta-release.yml`'s `pypi` job (`uses: ./.github/workflows/publish.yml`, `secrets: inherit`, `target_commitish`) as the proven, unported fix: (1) `release.yml`'s `git-auto-commit-action` push to `main` is rejected by ruleset `22046179` ("Protect main", bypass actor `DeployKey` only, `current_user_can_bypass: never`); (2) `publish.yml`'s `release: published` trigger has never fired in 8 of 8 recorded runs (all `workflow_dispatch`), with GitHub release `2.0.8` already orphaned unpublished on PyPI as the on-disk consequence.
- No `.github/workflows/` file in any repository was read-write touched — both items were written from `git show` reads only, per D-05.

## Task Commits

Each task was committed atomically:

1. **Task 1: Prepare branch v1.38-url-02-main — three files, one commit, off origin/main:**
   - `186a1524f13a4df6e4d9ac5a4c1b3e7177a7ee79` (fix) — in `firestarter_app`, on branch `v1.38-url-02-main` (unpushed, forked from `origin/main`; this branch does NOT sit on the milestone branch and its commit is not reachable from `v1.38-repository-rename`)
   - `89f65e16` (test) — in the meta repository, on the milestone branch: the evidence transcript
2. **Task 2: File the two pipeline defects:**
   - `ce672bed` (docs) — in the meta repository, on the milestone branch: both backlog items

**Plan metadata:** commit pending (this SUMMARY + STATE/ROADMAP/REQUIREMENTS)

## Files Created/Modified
- `firestarter_app/firestarter/constants.py` (on branch `v1.38-url-02-main` only) — `FIRESTARTER_RELEASE_URL` repointed to `https://api.github.com/repos/henols/firestarter_fw/releases/latest`
- `firestarter_app/README.md` (on branch `v1.38-url-02-main` only) — line 17 firmware link repointed to `https://github.com/henols/firestarter_fw`
- `firestarter_app/firestarter/__init__.py` (on branch `v1.38-url-02-main` only) — `__version__` `2.0.8` → `2.0.9`
- `.planning/phases/191-the-branch-that-reaches-users/evidence/191-url-02-prepared-branch.txt` — the readings transcript
- `.planning/todos/pending/2026-09-13-release-yml-autocommit-vs-ruleset.md` — filed defect 1
- `.planning/todos/pending/2026-09-13-publish-yml-release-published-never-fires.md` — filed defect 2

## Decisions Made
- D-01 applied literally: one constant repointed, the two beta-only names not backported.
- D-03's three-file, one-PR scope was verified as the *complete* boundary-aware sweep before editing (`git grep` against `origin/main` returned exactly `README.md:17` and `constants.py:9`), matching the plan's cited facts exactly — no re-derivation needed, no surprises.
- D-04's version bump (`2.0.9`) was carried in the same commit as the URL fix, per the plan, so the merged commit is already correct for a hand-cut release.
- The `_compare_versions` beta-string parse defect (D-09, deferred in `191-CONTEXT.md`) is recorded here as an observation rather than filed as a third backlog item: `main`'s `_compare_versions` (`firestarter/firmware.py:132-146`) splits version strings on `.` and calls `int()` on each part; a firmware string like `3.0.0b22` raises `ValueError` on `int("0b22")`, is caught, logs `"Could not parse version strings for comparison"`, and returns `False` — causing the stable CLI to treat every beta-flashed board as out of date and offer a downgrade. This is a real, previously-measured `main`-branch defect (not reproduced live in this plan, which touches no hardware) and is left unfixed and unfiled beyond this note, consistent with the milestone's stated D-02 posture that `main` carries no regression guard and this milestone does not add one.
- No GSD state-writing verb (`gsd_run query state.*` / `commit`) was invoked in the course of this plan; commits were made directly with `git commit` per the plan's explicit instruction, so the previously-observed `.planning/config.json` sub_repos-pruning hazard had no trigger. `sub_repos` was confirmed to hold all four entries (`firestarter`, `firestarter_app`, `firestarter_app_py32`, `firestarter_py32_ci`) both before and after execution.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
None.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- The prepared branch `v1.38-url-02-main` exists locally in `firestarter_app`, unpushed, one commit, three files, waiting for the operator's `blocking-human` gate in 191-03 (push, open PR, merge).
- Both pipeline defects are on record with their proven fix named, so 191-03/191-04's live `release.yml` observation and hand-cut/`workflow_dispatch` sequence have a written reference rather than needing to be rediscovered mid-gate.
- No blockers. 191-03 and 191-04 remain `autonomous: false` operator gates; this phase must not run under `--auto`/`--chain`.

---
*Phase: 191-the-branch-that-reaches-users*
*Completed: 2026-09-13*

## Self-Check: PASSED
- FOUND: .planning/todos/pending/2026-09-13-release-yml-autocommit-vs-ruleset.md
- FOUND: .planning/todos/pending/2026-09-13-publish-yml-release-published-never-fires.md
- FOUND: .planning/phases/191-the-branch-that-reaches-users/evidence/191-url-02-prepared-branch.txt
- FOUND: commit 186a1524f13a4df6e4d9ac5a4c1b3e7177a7ee79 (firestarter_app, branch v1.38-url-02-main)
- FOUND: commit 89f65e16 (meta)
- FOUND: commit ce672bed (meta)
