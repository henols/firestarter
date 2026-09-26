---
phase: 152-outward-facing-close-operator-gated
plan: 10
subsystem: release-engineering
tags: [git, ci, pytest, platformio, merge-verification, cherry-oracle]

requires:
  - phase: 152-05..09
    provides: claim gate, five outward drafts (frozen with APP_TAG_TBD / FW_TAG_TBD placeholders)
provides:
  - A live, both-directions `git cherry` merge picture for both sub-repos, re-measured 2026-08-21
  - Confirmation that all three repos are already tracked-porcelain-clean with only the recorded pre-existing untracked set present
  - Confirmation that both meta-repo gitlinks already agree with their submodule HEADs
  - A green app test suite (1762 passed / 63 skipped) under BOTH Python 3.12.13 (devcontainer) and Python 3.11.16 (provisioned CI-parity venv), with the sibling firmware root severed to an empty directory
  - A green firmware native suite (170/170) and a green erase-path over-voltage source-scan gate (`check_erase_no_vpp.py`)
affects: [152-11, 152-12]

tech-stack:
  added: []
  patterns:
    - "git cherry as the sole merge oracle (never merge-base --is-ancestor)"
    - "FIRESTARTER_FW_ROOT env override to sever the devcontainer's sibling-firmware-checkout masking layout"
    - "uv venv --python 3.11 for local CI-parity provisioning, installing only the repo's own declared .[test] extra"

key-files:
  created:
    - .planning/phases/152-outward-facing-close-operator-gated/152-10-SUMMARY.md
  modified: []

key-decisions:
  - "No commit was made in any of the three repos this task — all three were already tracked-porcelain-clean at task start, and the untracked set in each exactly matched the RESEARCH-recorded pre-existing set. Task 2's acceptance criteria are satisfied by verification alone, with zero staging/commit actions."
  - "CI-parity was measured, not assumed: a Python 3.11.16 venv was provisioned with `uv venv --python 3.11` (UV_CACHE_DIR set to a scratch dir) and the app's own `.[test]` extra installed into it via `uv pip install -e '.[test]'`, then the full suite run under that interpreter. Both the 3.12.13 devcontainer run and the 3.11.16 parity run are green with identical counts (1762 passed, 63 skipped) — no local-vs-CI gap was found, and this is a measured finding, not an assumption."
  - "Per must_haves.prohibitions: no `git merge-base --is-ancestor` invocation appears anywhere in this task or SUMMARY; `git cherry` is the only oracle used. No `git add -A`/`git add .` was run in either submodule (moot, since nothing needed staging). No re-pinning of gitlinks to origin/beta was performed — that is Plan 152-12's job."
  - "requirements.mark-complete was deliberately NOT invoked for OUT-04 by this plan. This plan performs no posting and no network write; OUT-04 is discharged by the posting plan, not by this measurement/merge-prep plan."

requirements-completed: []

coverage:
  - id: D1
    description: "Both sub-repos' merge pictures re-measured live in both directions with git cherry as the sole oracle; gitlink/submodule-status and release/registry pictures captured"
    verification:
      - kind: other
        ref: "git -C /workspaces/firestarter rev-list --left-right --count origin/beta...HEAD (0 39); git cherry origin/beta HEAD (39 '+', 0 '-'); git -C /workspaces/firestarter_app rev-list --left-right --count origin/beta...HEAD (7 85); git cherry origin/beta HEAD (80 '+', 5 '-')"
        status: pass
    human_judgment: false
  - id: D2
    description: "All three repos tracked-porcelain-clean; untracked set equals the recorded pre-existing set in each; both gitlinks agree with submodule HEADs; every repo still on the milestone branch"
    verification:
      - kind: other
        ref: "git status --porcelain | grep -v '^??' (empty in all three repos, both before and after the test runs); git submodule status (no '+' prefix on either entry); git rev-parse --abbrev-ref HEAD (gsd/v1.32-at28c-write-path-root-cause-report-provenance in all three repos)"
        status: pass
    human_judgment: false
  - id: D3
    description: "App suite and firmware native suite run with the sibling firmware root severed to an empty directory; interpreter versions recorded; local-vs-CI gap recorded rather than assumed"
    verification:
      - kind: other
        ref: "FIRESTARTER_FW_ROOT=<empty tmpdir> python3 -m pytest -o addopts=\"\" -q (3.12.13: 1762 passed, 63 skipped, rc=0; 3.11.16 venv: 1762 passed, 63 skipped, rc=0); pio test -e native (170/170, rc=0); python3 scripts/check_erase_no_vpp.py (PASS, rc=0)"
        status: pass
    human_judgment: false

# Metrics
duration: 33min
completed: 2026-08-21
status: complete
---

# Phase 152 Plan 10: Pre-Merge Measure, Commit, Test Summary

**Re-measured both sub-repos' merge pictures with `git cherry` as the sole oracle, found all three repos already tracked-clean, and proved the app suite green under both the devcontainer interpreter and a freshly provisioned CI-parity interpreter with the sibling firmware root severed.**

## Performance

- **Duration:** 33 min
- **Started:** 2026-08-21T15:53:24Z
- **Completed:** 2026-08-21T16:06:37Z (test runs) — SUMMARY authored immediately after
- **Tasks:** 3
- **Files modified:** 0 (measurement/verification plan; SUMMARY.md is the only file this plan writes)

## Accomplishments

- Re-verified the merge picture for both sub-repos, live, in both directions, with `git cherry` as the sole oracle (never `--is-ancestor`).
- Confirmed all three repos (meta, firestarter, firestarter_app) are already tracked-porcelain-clean, with the untracked set in each exactly matching the recorded pre-existing set — no commit was needed or made.
- Confirmed both meta-repo gitlinks already agree with their submodule HEADs (`git submodule status` shows no `+` prefix).
- Severed the devcontainer's sibling-firmware-checkout masking layout via `FIRESTARTER_FW_ROOT` pointed at an empty temporary directory, and ran the app test suite green under it on both the devcontainer's Python 3.12.13 and a freshly provisioned Python 3.11.16 CI-parity venv — identical counts on both, no gap.
- Ran the firmware native test suite (170/170) and the erase-path over-voltage source-scan gate (`check_erase_no_vpp.py`), both green.
- Re-confirmed all three repos still tracked-porcelain-clean after the test runs (no artifact leakage from either suite).

## Task 1 — Re-measured merge picture, both sub-repos, both directions

All commands run live, 2026-08-21, starting `2026-08-21T15:53:24Z`.

### `firestarter` (firmware)

```
$ git -C /workspaces/firestarter fetch origin --quiet
$ git -C /workspaces/firestarter rev-list --left-right --count origin/beta...HEAD
0	39
$ git -C /workspaces/firestarter cherry origin/beta HEAD | awk '{print $1}' | sort | uniq -c
     39 +
$ git -C /workspaces/firestarter log --oneline HEAD..origin/beta
(empty)
$ git -C /workspaces/firestarter status --short
(empty)
$ git -C /workspaces/firestarter rev-parse --abbrev-ref HEAD
gsd/v1.32-at28c-write-path-root-cause-report-provenance
```

**0 behind, 39 ahead, all 39 genuinely new (`+`), zero already-upstream, working tree clean.** Matches the RESEARCH baseline (§A-2) exactly — no delta. The firmware PR to `beta` remains a clean fast-forwardable merge.

### `firestarter_app` (host CLI)

```
$ git -C /workspaces/firestarter_app fetch origin --quiet
$ git -C /workspaces/firestarter_app rev-list --left-right --count origin/beta...HEAD
7	85
$ git -C /workspaces/firestarter_app cherry origin/beta HEAD | awk '{print $1}' | sort | uniq -c
     80 +
      5 -
```

The 5 `-` (already-upstream-by-patch-id) SHAs on the milestone branch: `ebbc299`, `da6572b`, `94d327d`, `a7e554d`, `c495e98` — this is exactly the false-negative class the D-04 decision warns about; `git merge-base --is-ancestor` would report these absent, `git cherry` correctly classifies them as already landed under different SHAs on `beta`.

```
$ git -C /workspaces/firestarter_app log --oneline HEAD..origin/beta
f505ae7 Apply automatic changes
eaca13e Merge pull request #52 from henols/fix/fw-update-path-and-port-targeting
16f5680 fix: flash the port the identity came from — defect A survived via the config path
04916e9 fix: the not-found hint blamed 2.x alone; pre-b8 3.0.0 fails identically
8610e93 fix: route the saved port through one writer — da6572b missed the flash path
cbebc05 fix: make --port authoritative, allow blind install, stop transient config leaking
a3163d7 fix: unblock the firmware-update path on pre-CAP-02 firmware
$ git -C /workspaces/firestarter_app status --short
?? .planning/config.json
?? SECURITY.md
?? datasheets/M27C1001.pdf
?? datasheets/M27C512.pdf
?? datasheets/W27C512.pdf
?? datasheets/W27E257.pdf
?? write_test_port.sh
$ git -C /workspaces/firestarter_app rev-parse --abbrev-ref HEAD
gsd/v1.32-at28c-write-path-root-cause-report-provenance
```

**7 behind, 85 ahead, 80 `+` / 5 `-`.** Matches the RESEARCH baseline (§A-1) exactly — no delta from the 2026-08-21 research measurement. The app PR to `beta` is a real merge (not a fast-forward); the 7 behind-commits are PR #52's fw-update-path/port-targeting fixes plus their auto-commit. The 6 untracked files above are the RESEARCH-named pre-existing set.

### Meta repo — gitlink and submodule state

```
$ git submodule status
 d990a4ce80fcb56c9becf2312d1fe8757e1fc54d firestarter (v1.23-117-gd990a4c)
 a0bfd5e8b32989a60fc93b94e7b102506e6cf56f firestarter_app (v1.23-116-ga0bfd5e)
$ git ls-tree HEAD firestarter firestarter_app
160000 commit d990a4ce80fcb56c9becf2312d1fe8757e1fc54d	firestarter
160000 commit a0bfd5e8b32989a60fc93b94e7b102506e6cf56f	firestarter_app
$ git rev-parse --abbrev-ref HEAD
gsd/v1.32-at28c-write-path-root-cause-report-provenance
$ git status --short
 ? firestarter_app
?? .claude/skills/devtest-rootcause/
?? package-lock.json
?? package.json
```

**No `+` prefix on either `submodule status` entry** — both gitlinks agree with the corresponding sub-repo's current HEAD exactly. The `git status` "modified: firestarter_app (untracked content)" line (rendered as `" ? firestarter_app"` in the short form) is confirmed via `git status` (long form) to be caused solely by the 6 pre-existing untracked files inside the submodule, not a gitlink SHA divergence — verified by comparing `git ls-tree HEAD firestarter_app` against `git -C firestarter_app rev-parse HEAD`: both are `a0bfd5e8b32989a60fc93b94e7b102506e6cf56f`.

### Release / registry picture

```
$ gh release list --repo henols/firestarter_app --limit 10
3.0.0b22   Pre-release  3.0.0b22   2026-08-19T19:40:06Z
3.0.0b21   Pre-release  3.0.0b21   2026-08-18T09:58:57Z
2.0.8      Latest       2.0.8      2026-08-07T18:00:45Z
3.0.0b20 … 3.0.0b14 (all Pre-release, 2026-08-02..2026-08-07)
$ gh release list --repo henols/firestarter --limit 10
3.0.0b19   Pre-release  3.0.0b19   2026-08-18T10:00:08Z
3.0.0b18 … 3.0.0b10 (all Pre-release, 2026-06-18..2026-08-07)
$ curl -s https://pypi.org/pypi/firestarter/json | python3 -c "..."
pypi stable info.version: 2.0.7
```

**GitHub-versus-registry comparison, explicit:** GitHub's app stable release is `2.0.8` (2026-08-07T18:00:45Z); PyPI's `info.version` is `2.0.7`, and PyPI's full `releases` key list does **not** contain `2.0.8`. **The registry does not have the latest GitHub stable tag.** App latest pre-release on GitHub is `3.0.0b22` (2026-08-19); firmware latest pre-release on GitHub is `3.0.0b19` (2026-08-18). This reproduces RESEARCH §A-4/§A-5 exactly, byte-for-byte on the version strings — no delta.

**No `git merge-base --is-ancestor` invocation was used anywhere above or in this SUMMARY.**

## Task 2 — Commit every tracked change; prove the untracked set is the recorded pre-existing one

**Verified, and zero commits were needed:** at task start, `git status --porcelain | grep -v '^??'` was already empty in all three repos (meta, firestarter, firestarter_app). Every prior-wave commit (the claim gate, the five frozen outward drafts) had already been committed in earlier plans of this phase. There was no tracked modification for this task to stage.

Per-repo untracked-set enumeration, confirmed to pre-date this phase (per RESEARCH §A-3):

| Repo | Untracked entries | Pre-existing? |
|---|---|---|
| meta (`/workspaces`) | `.claude/skills/devtest-rootcause/`, `package-lock.json`, `package.json` | yes |
| `firestarter` | (none) | n/a |
| `firestarter_app` | `.planning/config.json`, `SECURITY.md`, `datasheets/M27C1001.pdf`, `datasheets/M27C512.pdf`, `datasheets/W27C512.pdf`, `datasheets/W27E257.pdf`, `write_test_port.sh` | yes |

No `git add -A` or `git add .` was run in either submodule (nothing required staging). No gitlink bump was made — `git submodule status` already showed no `+` prefix (verified above in Task 1's meta section, and re-verified after Task 3's test runs). `git rev-parse --abbrev-ref HEAD` in all three repos, checked repeatedly across this plan's execution, returned `gsd/v1.32-at28c-write-path-root-cause-report-provenance` every time — `gsd-tools query commit` was never invoked, so the measured branch-switch risk did not materialize.

**No commit SHAs were created by this task** — there was nothing to commit.

## Task 3 — Severed the sibling firmware root; ran both test suites the CI will run

**Severance mechanism, confirmed from `firestarter_app/tests/fw_presence.py`:** the module resolves `FW_ROOT` at import time from `os.environ.get("FIRESTARTER_FW_ROOT", str(_DEFAULT_FW_ROOT))`, where `_DEFAULT_FW_ROOT` is the sibling `../firestarter` directory. Because this binds at import (not via `monkeypatch.setenv`), the override must be set in the child process's environment before `python3 -m pytest` starts — done via inline env-var assignment on the invocation itself.

```
$ EMPTY_FW_ROOT=$(mktemp -d)
$ FIRESTARTER_FW_ROOT="$EMPTY_FW_ROOT" python3 -m pytest -o addopts="" -q
```

### App suite — devcontainer interpreter (Python 3.12.13)

```
32 snapshots passed.
1762 passed, 63 skipped, 1 warning in 262.54s (0:04:22)
APPSUITE rc=0
```

### App suite — CI-parity interpreter (Python 3.11.16)

Provisioned live with `uv venv --python 3.11 <scratch-venv-dir>` (`UV_CACHE_DIR` pointed at a scratch cache dir), then installed only the app's own declared `.[test]` extra into that venv via `uv pip install -e '.[test]'` — no new third-party package introduced beyond what `pyproject.toml` already declares. Same severed-root env var, same invocation, against the venv's `python3`:

```
32 snapshots passed.
1762 passed, 63 skipped, 1 warning in 236.37s (0:03:56)
APPSUITE311 rc=0
```

**Local-vs-CI interpreter gap: none found, measured.** Both the devcontainer interpreter (3.12.13) and a freshly provisioned CI-parity interpreter (3.11.16) produced identical counts — 1762 passed, 63 skipped — both green, both with the sibling firmware root severed. This is a measured parity result, not an assumed one; the parity venv was successfully provisioned (tooling was available), so no fail-open record is owed here.

### Firmware native suite

```
$ pio test -e native
================ 170 test cases: 170 succeeded in 00:00:58.900 ================
FWNATIVE rc=0
```

170/170 passed, 17 suites, rc=0.

### Firmware source-scan gate — erase-path over-voltage scan

```
$ python3 scripts/check_erase_no_vpp.py
PASS: eeprom28c_erase_execute() in /workspaces/firestarter/src/proms/eeprom_28c.cpp (lines 545-560, 16 lines scanned) contains no VPP/VPE control-register, chip-enable/disable, or bus-config-bypassing hazard token
ERASE-VPP rc=0
```

Exit code 0. This is GATE-03's real primary control on the `0x0D` erase path (per Phase 153's own D-153-03 record — `check_dispatch.py` is DB-and-dispatch-table scoped and structurally cannot see a handler-body register write; `check_erase_no_vpp.py` is the control that actually guards the hardware-damage hazard this milestone's erase-path work touches).

### No hand-normalization of generated files

No file under either repo's codegen output (`messages.py`, `include/messages.h`) was touched by this task.

### Post-run porcelain re-check

```
$ for r in /workspaces /workspaces/firestarter /workspaces/firestarter_app; do git -C $r status --porcelain | grep -v '^??'; done
(meta: only the pre-existing "modified: firestarter_app (untracked content)" marker — no gitlink SHA change)
(firestarter: empty)
(firestarter_app: empty)
```

The untracked `??` sets in all three repos after the test runs are byte-identical to the sets enumerated in Task 2 — neither suite left an artifact in the tree.

## Files Created/Modified
- `.planning/phases/152-outward-facing-close-operator-gated/152-10-SUMMARY.md` — this document (the only file this plan writes)

## Decisions Made
- No commit was needed in any of the three repos — all were already tracked-clean at task start. Recorded as a measured finding, not treated as a plan deviation.
- CI-parity was measured via a provisioned Python 3.11.16 venv rather than recorded as unmeasurable — tooling (`uv`) was available, so the plan's fail-open fallback branch was not needed.
- `requirements.mark-complete` was not invoked for OUT-04. This plan posts nothing; OUT-04 is discharged by the posting plan (152-11), not by this pre-merge measurement plan.

## Deviations from Plan

None — plan executed exactly as written. Task 2 found nothing requiring a commit action, which is a valid outcome of "prove clean," not a deviation from the task's instructions.

## Issues Encountered

The app suite's default 2-minute shell timeout was insufficient (`python3 -m pytest` takes ~4-4.5 minutes including a self-test that spawns a nested `pytest tests/ -rs -q --ignore=tests/test_skip_census.py` subprocess). Resolved by running both suite invocations as backgrounded commands and blocking on their wrapper PIDs via `tail --pid=<pid> -f /dev/null` rather than a sleep-poll loop.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- The pre-merge measurement Plan 152-12 (`152-MERGE-RECORD.md`) can cite this plan's live `git cherry` output directly.
- Plan 152-11 can proceed to open PRs to `beta` in both sub-repos with confidence that: (a) the merge pictures are current and oracle-verified, (b) both trees are already committed/clean, and (c) the app suite is CI-green under the actual CI interpreter (3.11), not merely the devcontainer's (3.12).
- **No push, no PR, no merge, and no post occurred in this plan** — full compliance with `must_haves.prohibitions`.

This ships software-proven and unvalidated on silicon.

## Self-Check: PASSED

- FOUND: `/workspaces/.planning/phases/152-outward-facing-close-operator-gated/152-10-SUMMARY.md`
- Claim gate: `FIRESTARTER_CLAIMSCAN_TARGETS_152=<this file> python3 152-check-claims.py` → rc=0 (PASS)
- No commit SHAs were created by this plan (Tasks 1-3 were measurement/verification-only; nothing required staging in any of the three repos) — there are no commit hashes to verify against `git log`.

---
*Phase: 152-outward-facing-close-operator-gated*
*Completed: 2026-08-21*
