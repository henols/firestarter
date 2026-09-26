---
phase: 189-free-the-name
plan: 02
subsystem: infra
tags: [git-submodule, gitmodules, github-rename, fresh-clone-fixture]

# Dependency graph
requires:
  - phase: 189-01
    provides: "Operator-performed GitHub rename of henols/firestarter to henols/firestarter_fw, confirmed live via numeric-id identity transcript"
provides:
  - ".gitmodules firmware URL repointed at git@github.com:henols/firestarter_fw.git (URL-only change per D-01/D-02), with the superproject config and the submodule's own remote.origin.url propagated via git submodule sync --recursive (D-03)"
  - "Three recorded D-03 observables proving the existing clone resolves the new URL without relying on the redirect"
  - "A committed, re-runnable RENAME-03 fixture (fresh-clone-fixture.sh) that clones the local meta repository over file:// while its submodule leg resolves against the real GitHub remotes (D-04)"
  - "A captured real run of that fixture, taken while the gitlinks still point at the pushed beta tips (D-05), proving both submodules resolve their recorded URLs directly"
affects: [189-03, 189-04, 193]

# Actuals (#2632)
actuals:
  tokens: 3695
  tasks: 2
  commits: 3
  plan_head_before: 9ccf0414d7a2d86e5e97b6cf1db2da01737bfc81

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "git submodule set-url + git submodule sync --recursive is the only mechanism that reaches all three D-03 observables (.gitmodules, local config, submodule's own remote.origin.url) -- set-url alone rewrites the file only"
    - "RENAME-03 demonstrated via a file:// superproject clone with a real-remote submodule leg (D-04), so the demonstration needs no push and is reusable by Phase 193's GATE-03"

key-files:
  created:
    - .planning/phases/189-free-the-name/fresh-clone-fixture.sh
    - .planning/phases/189-free-the-name/evidence/189-rename-02-observables.txt
    - .planning/phases/189-free-the-name/evidence/189-rename-03-fresh-clone.txt
  modified:
    - .gitmodules

key-decisions:
  - "D-01/D-02 honored: only the url = line under [submodule \"firestarter\"] changed (one insertion, one deletion, TAB indentation preserved); section name, path, and SSH transport are untouched."
  - "D-03 honored: repointed via git submodule set-url followed by git submodule sync --recursive, and all three propagated observables (.gitmodules, local config, firestarter/'s remote.origin.url) were asserted, not just the file."
  - "D-04/D-05/D-06 honored: the fresh-clone fixture clones the LOCAL meta repository over file:// with a real-remote submodule leg, was run and captured while the gitlinks still point at the pushed beta tips, and is committed as a re-runnable script under the phase directory rather than a one-off transcript."
  - "D-08 honored in the RENAME-02 evidence transcript: the beta half of ROADMAP criterion 2 is recorded as close-carried, not an incomplete requirement."

requirements-completed: [RENAME-02, RENAME-03]

coverage:
  - id: D1
    description: "RENAME-02's existing-clone half: .gitmodules, the superproject's local submodule.firestarter.url, and firestarter/'s own remote.origin.url all resolve git@github.com:henols/firestarter_fw.git, with firestarter_app left untouched as a control"
    requirement: "RENAME-02"
    verification:
      - kind: other
        ref: "git config --file .gitmodules submodule.firestarter.url / git config --local submodule.firestarter.url / git -C firestarter remote get-url origin, all read live and recorded in evidence/189-rename-02-observables.txt"
        status: pass
    human_judgment: false
  - id: D2
    description: "RENAME-03: a clone taken fresh from the milestone tip (file:// superproject, real-remote submodule leg) initialises both submodules from the recorded URLs, the firmware one naming firestarter_fw, proven by an actual run of the committed fixture"
    requirement: "RENAME-03"
    verification:
      - kind: other
        ref: "bash .planning/phases/189-free-the-name/fresh-clone-fixture.sh, captured verbatim in evidence/189-rename-03-fresh-clone.txt (exit 0, FRESH CLONE OK, all four assertions passed)"
        status: pass
    human_judgment: false

duration: 9min
completed: 2026-09-13
status: complete
---

# Phase 189 Plan 02: Free the Name — .gitmodules Repoint and Fresh-Clone Proof Summary

**Repointed the firmware submodule to git@github.com:henols/firestarter_fw.git via `set-url` + `sync --recursive`, then proved with a real, committed clone fixture that a fresh checkout resolves it directly rather than through GitHub's rename redirect.**

## Performance

- **Duration:** ~9 min
- **Started:** 2026-09-13T14:00:00Z (approx.)
- **Completed:** 2026-09-13T14:09:16Z
- **Tasks:** 2 (1 tracer, 1 auto)
- **Files modified:** 4 (1 modified, 3 created)

## Accomplishments
- Repointed `.gitmodules`' firmware URL to `git@github.com:henols/firestarter_fw.git` via `git submodule set-url` + `git submodule sync --recursive`, changing exactly one line (one insertion, one deletion) with the existing TAB indentation preserved and the section name / path untouched.
- Verified all three D-03 observables independently carry the new URL (`.gitmodules`, the superproject's local config, and `firestarter/`'s own `remote.origin.url`), plus the untouched `firestarter_app` control — recorded in `evidence/189-rename-02-observables.txt`.
- Wrote and committed `fresh-clone-fixture.sh`, a re-runnable RENAME-03 demonstration modelled on `lockstep-dryrun-fixture.sh` (shape), `sync_to_subrepos.sh` (temp-dir + trap), `run_gates.sh` (argument handling, exit codes) and `check-migration.sh` (bail-on-first assertions), with documented exit codes 0/1/2/3 including the not-yet-reachable "gitlink commit not present on remote" case 189-03 will exercise.
- Ran the fixture for real — clone from `file:///workspaces` at `v1.38-repository-rename`, submodule legs resolving against the real GitHub remotes — and captured its output verbatim as `evidence/189-rename-03-fresh-clone.txt`, showing both submodules resolved directly (`firestarter_fw` and `firestarter_app`) with no redirect in the path, while the gitlink is still unadvanced (D-05).

## Task Commits

1. **Task 1: End-to-end — repoint the firmware submodule URL and prove a fresh clone resolves it** — `5aba9dbc` (feat, `.gitmodules` repoint) + `d49b543c` (feat, fixture + evidence transcript)
2. **Task 2: Record the existing-clone observables for RENAME-02** — `6020cf82` (docs)

**Plan metadata:** pending (this commit, docs: complete plan)

## Files Created/Modified
- `.gitmodules` - firmware submodule URL repointed to `git@github.com:henols/firestarter_fw.git`; section name, path, and SSH transport unchanged
- `.planning/phases/189-free-the-name/fresh-clone-fixture.sh` - re-runnable RENAME-03 fixture: clones the meta repo over `file://`, asserts both submodules populated and resolving the recorded (non-bare-slug) URLs, documents exit codes 0/1/2/3
- `.planning/phases/189-free-the-name/evidence/189-rename-02-observables.txt` - three D-03 observables read from the existing clone, the `firestarter_app` control, section/path integrity readings, and the D-08 branch-disposition statement
- `.planning/phases/189-free-the-name/evidence/189-rename-03-fresh-clone.txt` - captured output of an actual fixture run, pinned to `meta_commit: 5aba9dbc8d760e530638931d19ede0a227dd1a60`

## Decisions Made
- Followed D-01 through D-06 and D-08 exactly as specified in `189-CONTEXT.md`; no architectural deviation. The one implementation choice left to discretion — the fixture's exact shape, argument handling, and temp-dir strategy — used `mktemp -d` outside `/workspaces` with a `KEEP_CLONE=1` escape hatch and a `--help`/fail-closed argument loop, following the analogs `189-PATTERNS.md` named.
- Verified the exact git diagnostic strings used to detect exit-code-3 ("gitlink commit not present on remote") directly from this machine's `git-submodule--helper` binary via `strings` (`Fetched in submodule path '%s', but it did not contain %s. Direct fetching of that commit failed.`, `Server does not allow request for unadvertised object %s`, `reference is not a tree: %s`) rather than guessing the wording, since a local `file://` submodule test could not reproduce the real-remote restriction that produces it.

## Deviations from Plan

None - plan executed exactly as written. All `<verify>` legs for both tasks were re-run live and passed; `must_haves.prohibitions` were checked and none were violated (no section/path rename, no HTTPS/relative transport, no `--reference`/shared-object-store/pre-seeded-submodule shortcut, no fabricated transcript, no touch to `.planning/milestones/`).

## Issues Encountered

One incidental cleanup: exploratory local-clone testing (used to confirm git's exact exit-3 diagnostic wording before writing the detection logic) left a stray `clone.log` file at the repository root from a failed test command that inherited the persisted working directory. Removed before staging; it was never part of any commit. A separate, pre-existing uncommitted `.gitignore` modification (adding `tmp/` and `anything.*`) was present in the working tree at task start, is unrelated to this plan's `files_modified` list, and was left untouched per the branch-and-repo constraints on the operator's scratch paths.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- RENAME-02 and RENAME-03 are both complete and evidenced. The firmware gitlink remains unadvanced (`git diff --name-only HEAD -- firestarter` empty at task end), leaving 189-03 free to advance it next per D-05's ordering.
- `fresh-clone-fixture.sh` is committed and re-runnable; Phase 193's GATE-03 can extend it for its two history-trap clone cases rather than reinventing it.
- Branch `v1.38-repository-rename` unchanged throughout; nothing was pushed; `.planning/config.json` was not modified by any `gsd-tools` call during this plan.

## Self-Check: PASSED

- `.gitmodules` - FOUND, contains `url = git@github.com:henols/firestarter_fw.git` under `[submodule "firestarter"]`.
- `.planning/phases/189-free-the-name/fresh-clone-fixture.sh` - FOUND on disk, executable, re-run produces `FRESH CLONE OK` / exit 0.
- `.planning/phases/189-free-the-name/evidence/189-rename-02-observables.txt` - FOUND on disk.
- `.planning/phases/189-free-the-name/evidence/189-rename-03-fresh-clone.txt` - FOUND on disk, contains `meta_commit: 5aba9dbc8d760e530638931d19ede0a227dd1a60`.
- Commits `5aba9dbc`, `d49b543c`, `6020cf82` - FOUND in `git log --oneline --all`.
- Branch still `v1.38-repository-rename` after every commit.
- `.planning/config.json` not modified by any `gsd-tools` call during this plan (none were invoked).

---
*Phase: 189-free-the-name*
*Completed: 2026-09-13*
