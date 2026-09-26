---
phase: 115-beta-channel-install-and-firmware-flash-bench-validation-for
plan: 08
subsystem: docs + release-consistency
tags: [onboarding, doc-finalize, gitlink-bump, close-loop, onboard-04]

requires:
  - phase: 115 (plans 04, 05, 06, 07)
    provides: "b11 published + three per-board bench evidence records"
provides:
  - "firestarter_app/doc/beta-testing-install.md finalized from live bench findings (draft caveat removed, 328PB known-quirks note added)"
  - "meta-repo submodule gitlinks bumped off PINNED b10 to the 3.0.0b11 commits (firestarter 0fd7992, firestarter_app 204df99)"
affects: []

key-files:
  created: []
  modified:
    - firestarter_app/doc/beta-testing-install.md
    - firestarter
    - firestarter_app

key-decisions:
  - "Fast-forwarded both submodules to their CI version-bump tips (b10->b11) before the doc finalize + gitlink bump — local was 1 behind origin after the CI git-auto-commit"
  - "Bench runs were all clean, so the doc finalize is a light truing-up: removed draft caveat, added 328PB-Uno known-quirks note (benign bare-fw stable-channel not-found notice + historical instability caveat). Scope unchanged; community-validation.md hand-off intact"
  - "Committed doc on firestarter_app v1.21 + pushed (community reads from GitHub/v1.21, D-04); gitlink bump committed in meta repo only (not pushed — operator handles meta merge)"

requirements-completed: [ONBOARD-04]

coverage:
  - id: F1
    description: "beta-testing-install.md finalized from the three evidence records; draft caveat removed; hand-off + firestarter_uno.hex refs intact"
    requirement: "ONBOARD-04"
    verification:
      - kind: command
        ref: "grep -q community-validation && grep -q firestarter_uno.hex && ! grep -q 'Draft note'"
        status: pass
    human_judgment: false
  - id: F2
    description: "meta-repo submodule gitlinks bumped off PINNED b10 to the 3.0.0b11 commits; both sub-repo version strings read 3.0.0b11 at the pinned commits"
    requirement: "ONBOARD-04"
    verification:
      - kind: command
        ref: "firestarter/include/version.h + firestarter_app/firestarter/__init__.py read 3.0.0b11; git shows gitlink move 2d93379->0fd7992, e0bdea4->204df99"
        status: pass
    human_judgment: false

duration: 5min
completed: 2026-07-27
status: complete
---

# Phase 115 Plan 08: Doc Finalize + Gitlink Bump Summary

**Closed the loop: finalized the ONBOARD-04 onboarding doc from the three clean per-board bench runs and bumped the meta-repo submodule gitlinks off the long-standing PINNED-at-b10 hold to the public `3.0.0b11` commits.**

## Accomplishments
- **Submodule sync:** fast-forwarded `firestarter` (6976589→0fd7992) and `firestarter_app` (5cf3607→74c18e2→204df99) to their CI version-bump tips (b10→b11) — local was 1 behind after the CI git-auto-commit from the publishes.
- **Task 1 — doc finalize (`204df99`, pushed to v1.21):** removed the draft-first caveat (replaced with a bench-validated note), added a 328PB-Uno known-quirks note (the benign bare-`fw` stable-channel "not found" notice + the historical instability caveat). Scope unchanged; `community-validation.md` hand-off + per-board `.hex` table intact. The bench runs were all clean, so this is a light truing-up, not a rewrite.
- **Task 2 — gitlink bump (`4d8b33c`, meta repo):** `firestarter` 2d93379→0fd7992, `firestarter_app` e0bdea4→204df99. Both sub-repo version strings read `3.0.0b11` at the pinned commits.

## Decisions Made
- Doc committed + pushed on the firestarter_app v1.21 branch (community reads docs from GitHub/v1.21 regardless of pip build, D-04). Meta-repo gitlink commit is not pushed — operator owns meta-repo push/merge.
- Left the pre-existing `firestarter_app/.gitignore` local modification untouched (not mine; not part of the gitlink, which records the committed HEAD).

## Deviations from Plan
None material. (The doc finalize is lighter than the plan anticipated because no board surfaced a blocking gotcha — all three passed.)

## Scope guardrail honored (D-02/D-06)
No `v1.21` git tag, no `--no-ff` beta merge, no `/gsd-ship` / `/gsd-complete-milestone`. Those remain the separate operator-gated close step AFTER phase verification.

## Next Phase Readiness
All 8 plans complete. Phase deliverables done (both channels public, three boards validated, doc finalized, gitlinks at b11). Ready for phase verification, then the operator-gated milestone-close ceremony.

---
*Completed: 2026-07-27*

## Self-Check: PASSED
- FOUND: beta-testing-install.md finalized (draft caveat gone, hand-off intact) committed 204df99 + pushed
- FOUND: gitlinks bumped to 0fd7992 / 204df99 (b11) committed 4d8b33c; version strings read 3.0.0b11
