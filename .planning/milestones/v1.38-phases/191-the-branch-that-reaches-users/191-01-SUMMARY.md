---
phase: 191-the-branch-that-reaches-users
plan: 01
subsystem: testing
tags: [pypi, pip-install, github-releases-api, redirect-contract, venv, tracer, fixture]

# Dependency graph
requires: []
provides:
  - "A board-free, re-runnable clean-install fixture (191-stable-install-fixture.sh) asserting redirects == 0 on the installed FIRESTARTER_RELEASE_URL, with a positive control proving the probe can see a redirect when one exists"
  - "A committed fail-first baseline transcript (191-stable-02-fixture-baseline.txt) proving the fixture correctly detects today's pre-change state (2.0.7, bare slug) before the stable is repointed"
affects: [191-02, 191-03, 191-04, 191-05, phase-193]

# Actuals (#2632)
actuals:
  tokens: 7301
  tasks: 2
  commits: 1

tech-stack:
  added: []
  patterns:
    - "Board-free clean-install fixture: scratch python3 -m venv outside /workspaces, pip install --no-cache-dir with no --pre and no local path, driven through the installed package's own API (ConfigManager/FirmwareManager) rather than hand-rolled requests calls"
    - "redirects == 0 (len(r.history)) as the sole observable distinguishing two byte-identical GitHub Releases API responses"
    - "Positive control read and printed before the subject assertion, so a failing run still carries proof the probe can see a redirect"
    - "Explicit-path-only removal of downloaded artefacts under ~/.firestarter, never a directory-wide or git clean removal, because that directory also holds the operator's own config.json and reports/"

key-files:
  created:
    - .planning/phases/191-the-branch-that-reaches-users/191-stable-install-fixture.sh
    - .planning/phases/191-the-branch-that-reaches-users/evidence/191-stable-02-fixture-baseline.txt
  modified: []

key-decisions:
  - "Task 1 deliberately does not commit; Task 2 commits the fixture and its fail-first baseline together, after re-runnability is demonstrated -- proof-before-commit for a tracer that only becomes trustworthy once shown to fail on cue."
  - "Fixture drives origin/main's real API surface (ConfigManager in firestarter.config, FirmwareManager(config_manager) positional, fetch_latest_release_info(board=), _download_firmware_file), not Phase 190's click/channel-based surface, which does not exist on main (D-07 correcting 190's D-16)."
  - "Every check is independently re-derived (each python child re-imports and re-calls fetch_latest_release_info) rather than passing state between checks, mirroring 190's per-check idiom."

requirements-completed: [STABLE-02]

coverage:
  - id: D1
    description: "191-stable-install-fixture.sh exists: 492 lines, strict mode, --help/bad-argument discipline, five checks (provenance+PyPI cross-check, release resolution, asset download+format check, redirect contract with positive control, porcelain guard), no --pre/git clean/bare grep anywhere"
    requirement: STABLE-02
    verification:
      - kind: other
        ref: "Task 1's 12 automated <verify> legs (strict-mode count, --no-cache-dir presence, --pre/git-clean/bare-grep absence on non-comment lines, --help exit 0 with Exit codes: line, bad-argument exit 2) -- all run directly, all pass"
        status: pass
    human_judgment: false
  - id: D2
    description: "Fail-first baseline transcript: run against today's published stable (2.0.7, still carrying the bare slug) exits 1, with checks 0-2 green, control_redirects: 1, and the redirect assertion failing by name -- the instrument is proven capable of detecting the pre-change state"
    requirement: STABLE-02
    verification:
      - kind: other
        ref: ".planning/phases/191-the-branch-that-reaches-users/evidence/191-stable-02-fixture-baseline.txt, and Task 1's 6 baseline-content <verify> legs (control_redirects: 1, installed_file under /tmp, installed_version N.N.N, CHECK2 OK, absence of the success verdict token)"
        status: pass
    human_judgment: false
  - id: D3
    description: "Fixture is re-runnable and idempotent: a second consecutive run agrees on verdict, control_redirects, and subject_redirects; both git working trees (meta and firestarter_app) are clean afterwards; no .hex residue in ~/.firestarter; the fixture and baseline are committed together on the milestone branch with .planning/config.json unmodified"
    requirement: STABLE-02
    verification:
      - kind: other
        ref: "Task 2's 7 automated <verify> legs (executable bit, no .hex in ~/.firestarter, firestarter_app porcelain, fixture committed, phase-dir porcelain clean, config.json porcelain clean, correct branch) plus the manual second-run comparison -- all pass"
        status: pass
    human_judgment: false

duration: 30min
completed: 2026-09-13
status: complete
---

# Phase 191 Plan 01: Board-Free Stable-Install Fixture Summary

**Wrote a clean-room `pip install firestarter` fixture that drives the installed package's own firmware API to a live GitHub release and asserts `redirects == 0` -- then proved it red against today's published 2.0.7, which still carries the bare slug.**

## Performance

- **Duration:** ~30 min
- **Started:** 2026-09-13 (session start)
- **Completed:** 2026-09-13T20:34:35Z
- **Tasks:** 2
- **Files modified:** 2 (both new)

## Accomplishments
- Built `191-stable-install-fixture.sh` (492 lines): scratch `python3 -m venv`, no-cache `pip install firestarter` with no `--pre`/no local path, five checks (provenance + PyPI cross-check, release resolution via `ConfigManager`/`FirmwareManager`, asset download + Intel-HEX format check, the redirect contract with a positive control, a porcelain guard), `--help`/bad-argument discipline, `/usr/bin/grep -qFe` verdict tokens throughout, explicit-path-only cleanup.
- Ran the fixture against the stable published **today** (2.0.7, bare slug) and captured the deliberate **fail-first baseline**: checks 0-2 green, `control_redirects: 1` (the non-vacuity control), and the redirect assertion failing by name (`subject_redirects: 1`) -- exit 1, exactly as required. This is machine proof the instrument can detect the pre-change state before Phase 191's later plans do anything irreversible.
- Demonstrated re-runnability: a second consecutive run produced the identical verdict and identical `control_redirects`/`subject_redirects` readings, with both git working trees clean and no `.hex` residue in `~/.firestarter` (whose `config.json` and `reports/` -- the operator's own data -- were left untouched).
- Committed the fixture and its baseline together in one commit on the milestone branch.

## Task Commits

Each task was committed atomically:

1. **Task 1: Write 191-stable-install-fixture.sh and prove it red against today's published stable** - no commit (deliberate; see Decisions Made)
2. **Task 2: Prove the fixture re-runnable and idempotent, then commit it with its baseline** - `26401224` (test)

**Plan metadata:** commit pending (this SUMMARY + STATE/ROADMAP/REQUIREMENTS)

## Files Created/Modified
- `.planning/phases/191-the-branch-that-reaches-users/191-stable-install-fixture.sh` - the board-free, re-runnable STABLE-02 fixture
- `.planning/phases/191-the-branch-that-reaches-users/evidence/191-stable-02-fixture-baseline.txt` - the committed fail-first baseline transcript (2.0.7, exit 1)

## Decisions Made
- Task 1 writes and proves the fixture red but does not commit; Task 2 commits both files together only after re-runnability is demonstrated, per the plan's explicit RED-before-commit structure for this tracer.
- The fixture's release-management calls go through `firestarter.config.ConfigManager` (module is `config.py`, not `config_manager.py` -- confirmed by spike-installing 2.0.7 into a throwaway venv before writing the script) and `firestarter.firmware.FirmwareManager(config_manager)`, matching `origin/main`'s real, argparse-based 2.0.x surface rather than Phase 190's click/channel-based one.
- `PHASE_REL`/`FIXTURE_REL`/`BASELINE_REL` are derived at runtime via `realpath --relative-to` rather than hardcoded, so the porcelain guard (check 4) stays correct if the phase directory is ever relocated -- within the plan's stated "Claude's Discretion" for path strategy.
- Every check independently re-derives its own state (each Python child re-imports and re-calls `fetch_latest_release_info`) rather than threading values between checks, mirroring 190's per-check idiom and keeping each check meaningful in isolation.

## Deviations from Plan

None - plan executed exactly as written. Before writing the script, a throwaway scratch venv (outside the repo, removed afterward) was used to confirm real 2.0.7 module layout and signatures (`firestarter.config.ConfigManager`, `firestarter.firmware.FirmwareManager`, `fetch_latest_release_info`, `_download_firmware_file`) against the plan's cited facts -- this was verification of the plan's own claims, not a change to them, and all cited facts (constants.py's parenthesised assignment, `HOME_PATH` in firmware.py, the redirect counts) were confirmed accurate.

## Issues Encountered
None.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- The STABLE-02 instrument exists, is committed, and is proven capable of catching the pre-change state. It is ready to be re-run, unmodified, once 191-02 through 191-05 land the repointed constant and cut/publish the new stable -- at which point `subject_redirects: 0` should finally print and the script should exit 0 with `STABLE INSTALL CONTRACT OK`.
- No blockers. 191-02 and onward can proceed; 191-03 and 191-04 remain `autonomous: false` operator gates and this phase must not run under `--auto`/`--chain`.

---
*Phase: 191-the-branch-that-reaches-users*
*Completed: 2026-09-13*

## Self-Check: PASSED
- FOUND: .planning/phases/191-the-branch-that-reaches-users/191-stable-install-fixture.sh
- FOUND: .planning/phases/191-the-branch-that-reaches-users/evidence/191-stable-02-fixture-baseline.txt
- FOUND: commit 26401224
