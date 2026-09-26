---
phase: 115-beta-channel-install-and-firmware-flash-bench-validation-for
plan: 02
subsystem: release-engineering
tags: [pre-flight, ci-parity, beta-cut, operator-gate, no-op-repo]

# Dependency graph
requires: []
provides:
  - "Verified release-gate parity for both v1.21 trees (app beta-release.yml gates + firmware beta-build.yml gates) — green modulo documented pre-existing REDs"
  - "Operator-confirmed publish preconditions (gh auth henols, repo secrets, workflow_dispatch-from-v1.21 trigger mechanism with -f beta_version=3.0.0b11)"
affects: [115-03-firmware-prerelease, 115-04-app-pypi-publish]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Local CI-gate parity pre-flight before an irreversible single-shot publish (RESEARCH Pitfall 5 — avoid half-published state)"
    - "Honest CI-PENDING record for the py3.11 target under a 3.12-only devcontainer (Phase 98/103 precedent — never fabricate a py3.11 PASS)"

key-files:
  created: []
  modified: []

key-decisions:
  - "Confirmed beta-release.yml does NOT run repo-wide `ruff check .` / `ruff format --check .` — only catalog-check + messages.py-scoped codegen drift gate + pytest; so the new 2-file ruff-format drift does not block the dispatch"
  - "Classified all 3 app pytest failures as documented pre-existing bench REDs (audit_coverage_matrix golden + two no_programmer_found characterization tests), byte-identical to origin/beta"
  - "firestarter_leonardo.hex was a pio-cached (up-to-date) build; CI beta-build.yml builds the authoritative assets fresh on dispatch, so not a blocker"

requirements-completed: [ONBOARD-01, ONBOARD-02]

coverage:
  - id: T1
    description: "App release CI gates reproduced green locally on the v1.21 tree (messages.py codegen drift clean, ruff, pytest green modulo pre-existing REDs)"
    requirement: "ONBOARD-01"
    verification:
      - kind: command
        ref: "cd firestarter_app && git diff --exit-code firestarter/messages.py && python -m pytest tests/ -q"
        status: pass
    human_judgment: false
  - id: T2
    description: "Firmware gates reproduced (messages.h codegen drift clean, pio test -e native 80/80, pio run built all three firestarter_<board>.hex)"
    requirement: "ONBOARD-02"
    verification:
      - kind: command
        ref: "cd firestarter && git diff --exit-code include/messages.h && pio test -e native && ls .pio/build/{uno,uno328pb,leonardo}/firestarter_*.hex"
        status: pass
    human_judgment: false
  - id: T3
    description: "Operator confirmed gh auth + repo secrets + workflow_dispatch-from-v1.21 trigger mechanism (-f beta_version=3.0.0b11); no publish fired"
    requirement: "ONBOARD-01"
    verification:
      - kind: other
        ref: "Operator reply 2026-07-26: 'preconditions confirmed — dispatch from v1.21 with beta_version=3.0.0b11'"
        status: pass
    human_judgment: true

duration: 6min
completed: 2026-07-26
status: complete
---

# Phase 115 Plan 02: Release Pre-Flight Summary

**Reproduced the app (`beta-release.yml`) and firmware (`beta-build.yml`) release CI gates locally on the exact v1.21 trees — both green modulo documented pre-existing REDs — and cleared the operator publish-precondition gate. No repo files changed; no publish/push/merge fired.**

## Performance
- **Duration:** ~6 min (executor)
- **Tasks:** 3 (2 auto + 1 blocking human-verify checkpoint)
- **Files modified:** 0 (pre-flight is read-only + runs tests)

## Accomplishments
- **Task 1 — App pre-flight** (`firestarter_app`, branch `v1.21-community-chip-validation-command`): `pip install -e '.[test]']` clean; catalog valid (66 messages); `messages.py` codegen drift gate exit 0 (zero drift); `pytest tests/ -v` → **943 passed, 3 failed**. All 3 failures cross-checked as the documented pre-existing bench REDs (`test_audit_coverage_matrix::test_golden_file_matches` stale golden + `test_characterization::test_no_programmer_found_read`/`_erase` live-board environmental), confirmed byte-identical to `origin/beta`. py3.11 target recorded **CI-PENDING** (devcontainer is 3.12-only; ran under 3.12 per Phase 98/103 precedent).
- **Task 2 — Firmware pre-flight** (`firestarter`, branch `v1.21-community-chip-validation-command`): catalog valid; `include/messages.h` codegen drift gate exit 0 (zero drift); `pio test -e native` → **80/80** across 14 native suites; `pio run` → all three `.hex` present (`firestarter_uno.hex`, `firestarter_uno328pb.hex`, `firestarter_leonardo.hex`). Firmware tree fully clean after the run.
- **Task 3 — Operator precondition gate (blocking, D-03)**: operator confirmed 2026-07-26 — gh authed as `henols` (repo+workflow), secrets `PERSONAL_ACCESS_TOKEN`+`PYPI_API_TOKEN` present on `henols/firestarter_app`, `henols/firestarter` correctly uses built-in `GITHUB_TOKEN`; trigger mechanism = `workflow_dispatch` from the `v1.21-community-chip-validation-command` ref with explicit `-f beta_version=3.0.0b11` (no beta merge; D-02/D-06 preserved).

## Decisions Made
- `beta-release.yml` runs only catalog-check + `messages.py`-scoped codegen gate + `pytest` (verified) — it does NOT run repo-wide `ruff check .` / `ruff format --check .`, so it is the authoritative dispatch gate here.
- All 3 pytest failures classified pre-existing (not v1.21 regressions) via `git diff origin/beta..HEAD`.

## Deviations from Plan
None on the two auto tasks. **New finding surfaced (non-blocking for the dispatch):** `firestarter_app/tests/test_validate_family_cmd.py` + `tools/check_dispatch.py` carry `ruff format` drift introduced by the v1.20/v1.21 protocol-rename work (verified clean on `origin/beta`, so new). It does NOT gate `beta-release.yml` (no repo-wide format check there) but would fail the general `ci.yml` PR gate later (e.g. at the eventual `--no-ff` beta merge). Recommended a one-shot `ruff format` fix on the v1.21 branch — deferred to operator's call.

## Issues Encountered
None blocking. Discovered downstream (see Next-Phase Readiness): the `v1.21` branch is not yet pushed to either sub-repo remote, which is a prerequisite for the `workflow_dispatch --ref v1.21…` publish mechanism.

## Next Phase Readiness
Both trees are release-gate-ready and the operator cleared the precondition gate, so Plans 03/04 can fire the cut. **Prerequisite for Plan 03:** the `v1.21-community-chip-validation-command` branch must be pushed to `henols/firestarter` (+ `henols/firestarter_app` for Plan 04) so the manual dispatch can check the ref out — currently the branch is local-only (fw 23 ahead of `origin/beta`, app 131 ahead). Pushing does NOT auto-fire any publish (all publish workflows trigger only on `push:beta` or `workflow_dispatch`).

---
*Phase: 115-beta-channel-install-and-firmware-flash-bench-validation-for*
*Completed: 2026-07-26*

## Self-Check: PASSED

- Task 1 app gates reproduced green (verified: messages.py no drift, pytest 943/3-known-fail)
- Task 2 firmware gates reproduced green (verified: messages.h no drift, pio native 80/80, 3 .hex present)
- Task 3 operator precondition gate cleared 2026-07-26; no publish/push/merge fired; no version string hand-edited
