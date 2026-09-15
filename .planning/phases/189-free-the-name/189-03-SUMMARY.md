---
phase: 189-free-the-name
plan: 03
subsystem: infra
tags: [git-submodule, gitmodules, github-rename, bare-slug-sweep, firmware-repo]

# Dependency graph
requires:
  - phase: 189-02
    provides: "The .gitmodules firmware URL repointed to firestarter_fw, propagated via git submodule sync --recursive, and a committed, re-runnable fresh-clone fixture with an already-captured passing RENAME-03 transcript pinned to a meta commit where the gitlink still pointed at the pushed beta tip"
provides:
  - "The firmware repository's own README Releases link and tests/meta_presence.py docstring both address henols/firestarter_fw, closing the gap D-09 identified between ROADMAP criterion 4 and Phase 192's SWEEP-01"
  - "A firmware-repository-wide bare-slug sweep (evidence/189-firmware-slug-sweep.txt) proving zero live tracked references remain, paired with a non-vacuity positive control"
  - "The meta repository's firestarter gitlink advanced to the commit carrying those two edits, performed only after 189-02's fresh-clone demonstration existed (D-05)"
  - "A second, clearly-labelled reading appended to evidence/189-rename-03-fresh-clone.txt proving the fixture's exit-code-3 branch is reachable and correctly names the unpushed sha, rather than reporting a URL regression"
affects: [189-04, 192]

# Actuals (#2632)
actuals:
  tokens: 2200
  tasks: 3
  commits: 4
  plan_head_before: e11a57bc7d6db984aee36b8cb54d804aab9bbfc3

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "The bare-slug discriminator regex (henols/firestarter([^_a-zA-Z0-9]|$)) is the only correct sweep pattern in this project; a plain substring match over-matches firestarter_app/_prom/_fw"
    - "Every zero-expectation sweep is paired with a positive control over the same tree and machinery, so an empty or misdirected scan cannot masquerade as a clean result"

key-files:
  created:
    - .planning/phases/189-free-the-name/evidence/189-firmware-slug-sweep.txt
  modified:
    - firestarter/README.md
    - firestarter/tests/meta_presence.py
    - firestarter (gitlink)
    - .planning/phases/189-free-the-name/evidence/189-rename-03-fresh-clone.txt

key-decisions:
  - "D-09 honored: both firmware-repository slug references (README.md:47, tests/meta_presence.py:22) were repointed in one surgical commit inside the submodule, with no comment or annotation added to either file per CLAUDE.md's non-overridable no-comments-in-product-source rule."
  - "D-10 honored: no source-scanning guard, workflow, or lint rule was added inside the firmware repository. Cleanliness is proved at verification time by evidence/189-firmware-slug-sweep.txt, which carries a positive control (henols/firestarter_prom, 4 matches) so its zero cannot be attributed to an empty or misdirected scan."
  - "D-05 honored: the gitlink advance (meta commit d0d598ba) happened strictly after confirming 189-02's fresh-clone transcript already carried a meta_commit: line, and the fixture was re-run post-advance to prove case-3 (exit 3, naming the unpushed sha c67a3301d507bccea89281c08af75f3a7bb76edb) rather than assumed."
  - "The pre-existing passing RENAME-03 transcript (meta_commit 5aba9dbc, exit 0, FRESH CLONE OK) was preserved byte-for-byte; the post-advance reading was appended under a section labelled 'after the gitlink advance' rather than overwriting it."

requirements-completed: [RENAME-01, RENAME-03]

coverage:
  - id: D1
    description: "Both firmware-repository slug references are repointed to firestarter_fw, with a firmware-repo-wide sweep proving zero bare-slug references remain and a positive control proving the sweep is not vacuous"
    requirement: "RENAME-01"
    verification:
      - kind: other
        ref: "git -C firestarter grep -lE 'henols/firestarter([^_a-zA-Z0-9]|$)' -- . (0 matches) and the paired control git -C firestarter grep -lE 'henols/firestarter_prom' -- . (4 matches), both recorded in evidence/189-firmware-slug-sweep.txt"
        status: pass
    human_judgment: false
  - id: D2
    description: "The meta repository's firestarter gitlink is advanced to the commit carrying the two edits, only after 189-02's fresh-clone demonstration existed, and the fixture proves the designed post-advance exit-code-3 behavior by actually reaching it"
    requirement: "RENAME-03"
    verification:
      - kind: other
        ref: "git -C /workspaces rev-parse HEAD:firestarter equals git -C /workspaces/firestarter rev-parse HEAD (c67a3301d507bccea89281c08af75f3a7bb76edb); bash fresh-clone-fixture.sh exits 3 and names the missing sha; appended reading in evidence/189-rename-03-fresh-clone.txt under 'after the gitlink advance'"
        status: pass
    human_judgment: false

duration: 25min
completed: 2026-09-13
status: complete
---

# Phase 189 Plan 03: Free the Name — Firmware Repo Slug Repoint and Gitlink Advance Summary

**Repointed the firmware repository's own two slug references to firestarter_fw, proved a repository-wide sweep finds zero remaining, then advanced the meta gitlink after confirming 189-02's fresh-clone demonstration already existed — and proved the fixture's exit-code-3 branch by actually reaching it.**

## Performance

- **Duration:** ~25 min
- **Started:** 2026-09-13T14:10:00Z (approx.)
- **Completed:** 2026-09-13T14:35:00Z (approx.)
- **Tasks:** 3
- **Files modified:** 5 (2 in firestarter submodule, 1 created + 1 modified in meta evidence, 1 gitlink)

## Accomplishments
- Repointed `firestarter/README.md:47` (Releases link) and `firestarter/tests/meta_presence.py:22` (docstring) to `henols/firestarter_fw` in one surgical commit inside the submodule, leaving the five other README lines and line 16's submodule-directory reference byte-unchanged, and adding no comment of any kind.
- Swept the whole firmware repository with the bare-slug discriminator from `189-PATTERNS.md`: zero live tracked references remain, paired with a non-vacuity control (`henols/firestarter_prom`, 4 matches) and a workflow-file check (0 matches) proving D-10's no-guard boundary was not silently crossed.
- Advanced the meta repository's `firestarter` gitlink from `10ec1b0e` to `c67a330` only after confirming `189-02`'s fresh-clone transcript already carried a `meta_commit:` line (D-05's ordering).
- Re-ran the fresh-clone fixture post-advance: it exited `3` and named the unpushed sha exactly as designed, exercising the case-3 branch for the first time and proving it works rather than merely existing unreachable. Appended that reading to `evidence/189-rename-03-fresh-clone.txt` under a section labelled "after the gitlink advance," leaving the pre-existing passing transcript (exit 0, `meta_commit: 5aba9dbc...`) untouched above it.

## Task Commits

Each task was committed atomically (spanning both repositories):

1. **Task 1: Repoint the firmware repository's own two slug references** — `c67a330` (feat, inside `firestarter` submodule)
2. **Task 2: Sweep the firmware repository for the bare slug, with a control** — `331b6625` (docs, meta repository)
3. **Task 3: Advance the firmware gitlink, and prove the fixture names the consequence** — `d0d598ba` (feat, gitlink advance) + `d3983cdc` (docs, appended transcript reading), both meta repository

**Plan metadata:** pending (this commit, docs: complete plan)

## Files Created/Modified
- `firestarter/README.md` - Releases link now addresses `https://github.com/henols/firestarter_fw/releases`; all other lines unchanged
- `firestarter/tests/meta_presence.py` - docstring line 22 now names `henols/firestarter_fw`; provenance lines and line 16's submodule-directory reference untouched
- `.planning/phases/189-free-the-name/evidence/189-firmware-slug-sweep.txt` - new firmware-repo-wide bare-slug sweep with pre-state, post-state, positive control, and workflow-file check
- `.planning/phases/189-free-the-name/evidence/189-rename-03-fresh-clone.txt` - appended a second, labelled reading captured after the gitlink advance
- `firestarter` (gitlink in the meta repository) - advanced from `10ec1b0e24d98f04c3b4aa076b9d84231ac5da04` to `c67a3301d507bccea89281c08af75f3a7bb76edb`

## Decisions Made
- Followed D-05, D-09, D-10 exactly as specified in `189-CONTEXT.md`; no architectural deviation.
- Used `git -C <repo>` invocations directly (not `gsd-tools commit-to-subrepo`) for the submodule commit, per the plan's explicit instruction to commit "with plain `git -C /workspaces/firestarter commit`" and "with plain `git -C /workspaces commit`" — this is a two-repository plan with an established per-phase pattern (commit inside the submodule, then re-pin the gitlink in the meta repo), not the `sub_repos` config-driven multi-repo commit path.

## Deviations from Plan

None - plan executed exactly as written. All `<verify>` legs for all three tasks were re-run live and passed; `must_haves.prohibitions` were checked and none were violated (no comment or annotation added to either firmware file, no strip/reword of existing docstring provenance, the five must-not-change README lines and meta_presence.py line 16 are byte-identical, no source-scanning gate or workflow added inside the firmware repository, the gitlink was advanced strictly after confirming 189-02's demonstration transcript already existed).

## Issues Encountered

None. `.planning/config.json` was not modified by any `gsd-tools` call during this plan (none were invoked — all work used plain `git` commands per the plan's explicit instructions). The operator's untracked scratch paths (`anything.txt`, `tmp/`) were left untouched, and `.gitignore` was not modified.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- ROADMAP criterion 4 is satisfied: the firmware repository's own README and release links address the new name, and Phase 192 will find it already clean.
- D-09's boundary holds: `firestarter/tests/meta_presence.py:22`, named by neither ROADMAP criterion 4 nor Phase 192's SWEEP-01, was not left to fall through the gap.
- The firmware gitlink now names an unpushed commit, which is ordinary unpushed phase work under the standing push-at-ship-time rule; the fixture accurately reports this state (exit 3, sha named) rather than reading as a broken URL.
- Branch `v1.38-repository-rename` unchanged throughout in both repositories; nothing was pushed.

## Self-Check: PASSED

- `firestarter/README.md` - FOUND, line 47 contains `henols/firestarter_fw/releases`.
- `firestarter/tests/meta_presence.py` - FOUND, line 22 contains `henols/firestarter_fw`.
- `.planning/phases/189-free-the-name/evidence/189-firmware-slug-sweep.txt` - FOUND on disk.
- `.planning/phases/189-free-the-name/evidence/189-rename-03-fresh-clone.txt` - FOUND on disk, contains both the original `FRESH CLONE OK` transcript and the appended `after the gitlink advance` section.
- Commits `c67a330` (firestarter), `331b6625`, `d0d598ba`, `d3983cdc` (meta) - FOUND in `git log --oneline --all` in their respective repositories.
- `git -C /workspaces rev-parse HEAD:firestarter` equals `git -C /workspaces/firestarter rev-parse HEAD` (`c67a3301d507bccea89281c08af75f3a7bb76edb`).
- Branch `v1.38-repository-rename` confirmed current in both repositories after every commit.
- `.planning/config.json` not modified (no `gsd-tools` calls were made during this plan).

---
*Phase: 189-free-the-name*
*Completed: 2026-09-13*
