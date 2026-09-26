---
phase: 115-beta-channel-install-and-firmware-flash-bench-validation-for
plan: 03
subsystem: release-engineering
tags: [firmware-prerelease, github-release, beta-channel, operator-gated, irreversible]

# Dependency graph
requires:
  - phase: 115 (plan 02)
    provides: "green firmware pre-flight + operator-confirmed dispatch mechanism"
provides:
  - "EXTERNAL: GitHub prerelease 3.0.0b11 on henols/firestarter (isPrerelease=true, isDraft=false) carrying firestarter_uno.hex + firestarter_uno328pb.hex + firestarter_leonardo.hex — the ONBOARD-02 firmware channel"
  - "CI-side version-bump auto-commit on the remote v1.21 firmware branch (via git-auto-commit-action)"
affects: [115-05-bench-uno, 115-06-bench-leonardo, 115-07-bench-uno328pb, 115-08-finalize-doc]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Manual workflow_dispatch from the v1.21 branch ref with explicit -f beta_version=3.0.0b11 (NO beta merge; D-02/D-06 preserved)"
    - "Positive prerelease verification via the app's own fetch_release_info resolver (fw --list --pre), never a bare workflow-success (Pitfall 2 guard)"

key-files:
  created: []
  modified: []

key-decisions:
  - "Pushed the v1.21 branch to henols/firestarter as a prerequisite for workflow_dispatch --ref (branch was local-only); verified push auto-fires no workflow (beta-build.yml triggers only on push:beta or workflow_dispatch)"
  - "Dispatched with explicit -f beta_version=3.0.0b11 to avoid the version-mode trap (bare dispatch -> stable 3.0.1)"

requirements-completed: [ONBOARD-02]

coverage:
  - id: PR1
    description: "GitHub prerelease 3.0.0b11 exists on henols/firestarter (isPrerelease=true, isDraft=false) with all three board .hex assets"
    requirement: "ONBOARD-02"
    verification:
      - kind: command
        ref: "gh release view 3.0.0b11 --repo henols/firestarter --json isPrerelease,isDraft,assets"
        status: pass
    human_judgment: false
  - id: PR2
    description: "fw --list --pre resolves 3.0.0b11 (highest) + firestarter_<board>.hex asset URL for uno / uno328pb / leonardo — the exact fw -i path, no stable fallback"
    requirement: "ONBOARD-02"
    verification:
      - kind: command
        ref: "firestarter fw --list --pre -b {uno,uno328pb,leonardo}"
        status: pass
    human_judgment: false

duration: 5min
completed: 2026-07-26
status: complete
---

# Phase 115 Plan 03: Firmware `.hex` GitHub Prerelease Summary

**Published the `3.0.0b11` GitHub prerelease on `henols/firestarter` carrying all three board `.hex` assets, and positively confirmed it resolves through the app's own `fw -i` code path for every bench board — the ONBOARD-02 firmware half of Step 0 is public.**

## Performance
- **Duration:** ~5 min (branch push + CI build 1m54s + verification)
- **Tasks:** 2 (Task 1 operator-auth checkpoint — cleared by operator 2026-07-26; Task 2 dispatch + verify)
- **Files modified:** 0 repo files (external GitHub artifact + CI-side version bump on the remote branch)

## Accomplishments
- **Prerequisite:** pushed the local-only `v1.21-community-chip-validation-command` branch to `henols/firestarter` (23 commits ahead of `origin/beta`: v1.19+v1.20 protocol work + v1.21 fw fix `6976589`). Confirmed the push triggers no workflow.
- **Dispatch:** `gh workflow run beta-build.yml --repo henols/firestarter --ref v1.21-community-chip-validation-command -f beta_version=3.0.0b11` → run `30199560282`, **success in 1m54s**. CI steps all green: catalog check, messages.h codegen drift gate, native unit tests, update_version.py tests, version generation, git-auto-commit (version bump back to the remote v1.21 branch), 3-board PlatformIO build, and the Release (prerelease) step.
- **Positive verification (Pitfall 2 guard):**
  - `gh release view 3.0.0b11` → `tagName=3.0.0b11`, `isPrerelease=true`, `isDraft=false`, assets = `firestarter_leonardo.hex` + `firestarter_uno.hex` + `firestarter_uno328pb.hex`.
  - `firestarter fw --list --pre -b {uno,uno328pb,leonardo}` → each lists `3.0.0b11` as the highest prerelease with the correct `firestarter_<board>.hex` download URL. No stray stable `3.0.1`.

## Decisions Made
- Version-mode trap avoided by the explicit `-f beta_version=3.0.0b11` (a bare dispatch from a non-beta ref would produce a stable `3.0.1`).
- No beta merge / push-to-beta performed (D-02/D-06) — dispatch was branch-ref only.

## Deviations from Plan
- Added a branch-push prerequisite step (the plan assumed a dispatchable ref; the branch was local-only). Operator confirmed before the push. No other deviations.

## Issues Encountered
None. (Non-blocking: CI runners warn Node.js 20 actions forced to Node.js 24 — GitHub-side deprecation notice, not a build issue.)

## Next Phase Readiness
Firmware channel is public. **Note for 115-08:** the CI git-auto-commit added a version-bump commit to the *remote* v1.21 firmware branch, so local `firestarter` is now 1 commit behind `origin/v1.21…`; fetch/pull that commit before pinning the meta-repo gitlink to the published firmware tip. Plan 04 (PyPI) is next and holds at its own operator-authorization gate before dispatch.

---
*Phase: 115-beta-channel-install-and-firmware-flash-bench-validation-for*
*Completed: 2026-07-26*

## Self-Check: PASSED

- FOUND: GitHub prerelease 3.0.0b11 (isPrerelease=true) on henols/firestarter with all 3 board .hex assets
- FOUND: fw --list --pre resolves 3.0.0b11 + asset URL for uno / uno328pb / leonardo
- CONFIRMED: no stray stable 3.0.1; dispatch fired only after operator authorization
