---
phase: 160-rig-dual-arm-build-flash-provenance-the-shared-cell-procedur
plan: 01
subsystem: infra
tags: [bench, provenance, avrdude, worktree, venv, uv, git-worktree]

requires: []
provides:
  - ".planning/v1.34/rig-pins.json — the single machine-readable pin record (SHAs, avrdude, toolchain, per-target params, chip facts, forbidden lists) that plans 02-13 read"
  - ".planning/v1.34/arms-provenance.json — the D-06/D-07/D-08/D-09/Pitfall-8 bring-up record for the two host arms"
  - "Two live host arms at /workspaces/.v1.34-arms/{control,v133}, each a detached git worktree of firestarter_app with its own .venv and editable install"
  - "One frozen shared FIRESTARTER_CONFIG_DIR at .planning/v1.34/config, seeded and content-SHA'd"
affects: [160-02, 160-03, 160-04, 160-05, 160-06, 160-07, 160-08, 160-09, 160-10, 160-11, 160-12, 160-13]

tech-stack:
  added: [uv (venv + pip resolution), git worktree]
  patterns:
    - "Arm identity is the invoked absolute venv_bin path, never a version string — both arms report identical Firestarter 3.0.0b32"
    - "D-08 triple (rev-parse HEAD + empty porcelain + python -P __file__) as the standing per-arm proof"
    - "uv venv ships no pip module — use `uv pip freeze --python <venv>/bin/python`, not `<venv>/bin/python -m pip freeze`"

key-files:
  created:
    - .planning/v1.34/rig-pins.json
    - .planning/v1.34/README.md
    - .planning/v1.34/arms-provenance.json
    - .planning/v1.34/config/.gitkeep
    - .planning/v1.34/config/config.json
    - .planning/v1.34/bench/cells/.gitkeep
  modified:
    - .gitignore

key-decisions:
  - "Task 2 checkpoint: operator approved all six [SUS] transitive dependencies (click, pyserial, requests, rich, tqdm, packaging) verbatim as 'Approved' — none held, no partial install"
  - "Config dir seeded via ConfigManager.set_value() directly from the control arm's venv, not through a CLI subcommand — every firestarter CLI command that would persist state (config, dev *) issues a live serial COMMAND_CONFIG/handshake first, and no board is attached in this container"
  - "Dependency-set equality (Pitfall 8) measured with `uv pip freeze --python <venv>/bin/python`, not `<venv>/bin/python -m pip freeze` — `uv venv` (0.12.6) does not install a pip module into the venv"

requirements-completed: []

coverage:
  - id: D1
    description: "rig-pins.json created with every pinned value verified against a live measurement (4 SHAs, avrdude -A probe, toolchain versions, per-target params, chip facts) — Task 1"
    requirement: "RIG-01"
    verification:
      - kind: other
        ref: "python3 -c json-key-and-value assertion script (plan's own <verify><automated> block) — see Self-Check below"
        status: pass
    human_judgment: false
  - id: D2
    description: "Two host arms stood up as detached worktrees at pinned SHAs, each with its own venv + editable install, D-08 triple observed on both, dependency-set diff empty, frozen config dir seeded and SHA'd — Task 3"
    requirement: "RIG-01"
    verification:
      - kind: other
        ref: "plan's <verify><automated> shell block (rev-parse, porcelain, __file__ assertion, freeze diff) — re-run post-commit, genuinely green"
        status: pass
    human_judgment: false
  - id: D3
    description: "Package-legitimacy checkpoint before the two editable installs — Task 2"
    verification: []
    human_judgment: true
    rationale: "Human approval of a package-installation gate is the entire point of the checkpoint; there is nothing to automate."

duration: 22min
completed: 2026-08-26
status: complete
---

# Phase 160 Plan 01: Pin the Rig and Stand Up the Two Host Arms Summary

**Pinned all v1.34 rig constants into `rig-pins.json`, built two detached-worktree host arms of `firestarter_app` (control@`6bfa645`, v133@`cb189a9`) with independently-verified identical dependency sets, and seeded one frozen shared config dir — closing the "named source state" half of RIG-01/RIG-02.**

## Performance

- **Duration:** ~22 min for this continuation (Task 3 + SUMMARY); Tasks 1-2 executed in a prior session
- **Started:** 2026-08-26T21:07:55Z (task 1 commit) — this continuation started 2026-08-26T20:54Z
- **Completed:** 2026-08-26T21:16:11Z
- **Tasks:** 3/3 (1 auto, 1 checkpoint:human-verify, 1 auto)
- **Files modified:** 6 created (`rig-pins.json`, `README.md`, `arms-provenance.json`, 2× `.gitkeep`, `config.json`) + 1 modified (`.gitignore`), plus 2 out-of-tree worktrees/venvs

## Accomplishments

- `.planning/v1.34/{images,tools,config,bench/cells}` skeleton scaffolded (D-16)
- All four source SHAs (fw control/v133, app control/v133) re-verified live via `gh pr view --json headRefOid` and `git merge-base`, matching CONTEXT.md's table exactly — no substitution needed
- Pinned avrdude's `-A` acceptance probed and confirmed (fails at port-open, not option-parse); no fallback substitution required
- `rig-pins.json` written with every top-level key, all target/chip parameter tables, forbidden flags/binaries/argv0
- Operator approved all six `[SUS]` transitive dependencies at the Task 2 checkpoint (verbatim: "Approved") — they are pre-existing declared floors in `firestarter_app/pyproject.toml:43-50`, not a new choice
- Two git worktrees created `--detach` off `firestarter_app` at the pinned SHAs under `/workspaces/.v1.34-arms/`
- Both venvs created and editable-installed back to back (Pitfall 8 mitigation)
- D-08 triple (rev-parse HEAD, empty porcelain, `python -P` `__file__`) observed and recorded on both arms
- Pitfall 1's trap reproduced live in this container: the same `__file__` probe *without* `-P`, from cwd `/workspaces`, printed `None` on both arms
- Dependency-set equality (Pitfall 8) confirmed empty via `uv pip freeze` diff, sha256 `b9eeb29...` on both sides
- Both arms confirmed reporting the identical `Firestarter, version 3.0.0b32` string and both register `dev consistency-check --help` (exit 0) — the measured proof that no version-based check can distinguish the arms
- Frozen shared `FIRESTARTER_CONFIG_DIR` seeded at `.planning/v1.34/config`, content sha256 `77adfdd2...` recorded; `~/.firestarter` confirmed still absent after seeding
- Both sub-repos (`firestarter`, `firestarter_app`) and both new worktrees confirmed porcelain-clean throughout — no sub-repo commit, branch, or push

## Task Commits

1. **Task 1: Pin the rig — scaffold `.planning/v1.34/`, re-verify the four SHAs, write `rig-pins.json`** - `6004342c` (feat) — executed in prior session
2. **Task 2: Package-legitimacy gate before the two editable installs** - checkpoint, no commit; operator responded "Approved"
3. **Task 3: Stand up the two host arms — worktrees, venvs, frozen config dir, D-08 triple, dependency-set equality** - `cd24512f` (feat)

**Plan metadata:** committed below (this SUMMARY + STATE.md/ROADMAP.md)

## Files Created/Modified

- `.planning/v1.34/rig-pins.json` - single machine-readable pin record (Task 1)
- `.planning/v1.34/README.md` - orientation page, avrdude rationale, D-09 non-claim (Task 1)
- `.planning/v1.34/config/.gitkeep`, `.planning/v1.34/bench/cells/.gitkeep` - tracked empty dirs (Task 1)
- `.gitignore` - added `/.v1.34-arms/` line (Task 1)
- `.planning/v1.34/arms-provenance.json` - D-06/07/08/09 + Pitfall-8 bring-up record for both arms (Task 3)
- `.planning/v1.34/config/config.json` - frozen shared config dir's seed artifact (Task 3)
- `/workspaces/.v1.34-arms/control/`, `/workspaces/.v1.34-arms/v133/` - detached worktrees + venvs + editable installs (out-of-tree, not committed; gitignored)

## Decisions Made

- **Task 2 checkpoint outcome (recorded verbatim per instructions):** The operator was presented with all six `[SUS]` packages (`click`, `pyserial`, `requests`, `rich`, `tqdm`, `packaging`) with their registry URLs and reason sets, and with the fact that all six are pre-existing declared floors in `firestarter_app/pyproject.toml:43-50` rather than a choice this phase makes. The operator's response was: **"Approved"**. No package was held. The full declared dependency set was therefore authorized and installed into both arm venvs.
- Config dir seeding used the app's own `ConfigManager.set_value(..., persist=True)` API directly rather than a CLI invocation, because every `firestarter` subcommand capable of persisting a value (`config`, `dev *`) issues a live serial handshake (`COMMAND_CONFIG` or similar) first, and this container has no board attached (`/dev/ttyACM*`/`/dev/ttyUSB*` both confirmed absent). This dogfoods the same public write path (`_save_config()`) any real CLI invocation would use, without fabricating a hardware session.
- Dependency-set equality measured with `uv pip freeze --python <venv>/bin/python` rather than `<venv>/bin/python -m pip freeze` as the plan's Code Example 7 literally shows — `uv venv` 0.12.6 does not install a `pip` module into the venv it creates, so the module form errors with `No module named pip`. `uv pip freeze` performs the equivalent introspection using the same resolver `uv pip install` used, and is recorded as the exact command used in `arms-provenance.json`.
- Requirements RIG-01 and RIG-02 are intentionally **not** marked complete (`requirements-completed: []`). The plan's own "Requirement completion" section states this plan closes only the *named source state* half of RIG-01 (images land in plan 02, on-device read-back confirmation lands in plans 08/09/10) and only the *firmware/host SHA* fields of RIG-02's provenance block (board signature, `controller:` string, shield revision land in plans 04/11). Marking either checkbox now would be a premature multi-plan-requirement completion (a known project failure mode — see standing memory `reference_executors_prematurely_mark_requirements_complete`). `REQUIREMENTS.md` stays `Pending` for both until the phase's later plans close the remaining halves.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] `uv pip freeze` used in place of `python -m pip freeze` for the Pitfall-8 dependency-equality check**
- **Found during:** Task 3
- **Issue:** The plan's Code Example 7 and acceptance criteria specify `<venv>/bin/python -m pip freeze`. Running it against either arm's venv fails with `No module named pip` — `uv venv --python 3.12 .venv` (uv 0.12.6, this container) does not seed a `pip` module into the venv it creates.
- **Fix:** Used `uv pip freeze --python <venv>/bin/python` instead, which performs the equivalent introspection against the resolved environment (the same mechanism `uv pip install -e .` used to populate it). Confirmed a genuinely empty diff between both arms with `UV_CACHE_DIR` correctly exported (see self-caught near-miss below).
- **Files modified:** none (measurement-only change; recorded in `arms-provenance.json`'s `dep_freeze_command_note`)
- **Verification:** `diff <(uv pip freeze --python control/.venv/bin/python | grep -vi firestarter | grep -v '^-e file://') <(uv pip freeze --python v133/.venv/bin/python | ...)` → empty, sha256 identical on both sides (`b9eeb295...`)
- **Committed in:** `cd24512f` (Task 3 commit)

---

**Total deviations:** 1 auto-fixed (1 blocking)
**Impact on plan:** No scope creep — a measurement-tool substitution forced by this container's `uv` version, functionally equivalent to the plan's intent (Pitfall 8's dependency-drift check).

## Issues Encountered

**Self-caught near-miss, not a deviation requiring a fix, but worth recording as a live demonstration of Pitfall 9's exact failure shape:** during a *post-commit* re-run of the plan's own `<verify><automated>` block to double-check the committed state, I ran the `uv pip freeze` diff in a **fresh Bash call without re-exporting `UV_CACHE_DIR`** (each Bash tool invocation is a fresh subshell — exported env vars do not persist across calls). Both sides of the diff failed identically with `uv`'s root-owned-cache `Permission denied` error; because I had piped `2>/dev/null`, both process substitutions emitted empty stdout and the diff reported "no differences" — a textbook false green from a silently-and-symmetrically-failed command, structurally identical to the trap Pitfall 9 warns about. Caught by checking the exit code of one side directly (`uv pip freeze --python ... ` without stderr suppression → `exit=2`, `Permission denied`). Re-ran with `UV_CACHE_DIR` correctly exported and confirmed the diff is genuinely empty (matches the value already recorded in `arms-provenance.json` from the original in-task measurement, which *did* have `UV_CACHE_DIR` exported at the top of that script). No file was affected — this was a verification-only close call, not a data-integrity issue in the committed artifact.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- `rig-pins.json` and `arms-provenance.json` are both on disk and machine-readable; every later plan in this phase can read paths, SHAs, per-target parameters, and both arm venv binaries from them without re-deriving anything.
- Both host arms are live at `/workspaces/.v1.34-arms/{control,v133}` with working editable installs — plans 02+ can invoke either arm by its absolute `venv_bin` path immediately.
- The frozen `FIRESTARTER_CONFIG_DIR` exists and is seeded; later plans should re-verify its content SHA against `77adfdd2...` after each cell, per D-07.
- No blockers. The user-site editable install at `/home/vscode/.local/lib/python3.12/site-packages` remains present and un-neutralized, as instructed — it is documented in `arms-provenance.json.user_site_editable_install` as the named target for later `PROCEDURE.md`/`gate_record.py` argv checks.

## Self-Check: PASSED

- `FOUND: .planning/v1.34/rig-pins.json`
- `FOUND: .planning/v1.34/arms-provenance.json`
- `FOUND: .planning/v1.34/config/config.json`
- `FOUND: /workspaces/.v1.34-arms/control/.venv/bin/firestarter`
- `FOUND: /workspaces/.v1.34-arms/v133/.venv/bin/firestarter`
- `FOUND: commit 6004342c` (Task 1)
- `FOUND: commit cd24512f` (Task 3)
- `git -C /workspaces/firestarter status --porcelain` → empty
- `git -C /workspaces/firestarter_app status --porcelain` → empty
- `git -C /workspaces/.v1.34-arms/control status --porcelain` → empty
- `git -C /workspaces/.v1.34-arms/v133 status --porcelain` → empty

---
*Phase: 160-rig-dual-arm-build-flash-provenance-the-shared-cell-procedur*
*Completed: 2026-08-26*
