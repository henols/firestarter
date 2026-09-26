---
phase: 115-beta-channel-install-and-firmware-flash-bench-validation-for
plan: 04
subsystem: release-engineering
tags: [pypi, beta-channel, operator-gated, irreversible, onboard-01]

# Dependency graph
requires:
  - phase: 115 (plans 01, 02, 03)
    provides: "draft doc on branch; green app pre-flight; firmware channel live"
provides:
  - "EXTERNAL: PyPI firestarter 3.0.0b11 (pip install --pre firestarter) — the ONBOARD-01 Python-package channel"
  - "EXTERNAL: GitHub release 3.0.0b11 on henols/firestarter_app (isPrerelease=true) whose release commit ships doc/beta-testing-install.md (D-04)"
  - "CI-side __init__.py b10->b11 bump auto-commit on the remote app v1.21 branch"
affects: [115-05-bench-uno, 115-06-bench-leonardo, 115-07-bench-uno328pb, 115-08-finalize-doc]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Two-workflow PyPI path: beta-release.yml (bump + GH release, no PyPI) then manual publish.yml -f tag=3.0.0b11 (PAT-created release suppresses the auto release.published trigger)"
    - "Positive PyPI verification via pip index versions --pre (b11 highest, no stray 3.0.1), never a bare workflow-success"

key-files:
  created: []
  modified:
    - firestarter_app/tests/test_dispatch_mirror.py

key-decisions:
  - "First beta-release.yml dispatch FAILED SAFELY at the pytest gate (before any bump/release/publish): test_dispatch_mirror.py cross-repo legs (PROTOCOLS.md doc leg + test_configure_memory.cpp firmware leg) FileNotFoundError in the app-only CI checkout. Local pre-flight (115-02) could not catch this — firmware is a sibling locally so the legs pass"
  - "Fix (5cf3607, test-only, no product behavior change): FW_ABSENT skipif guard on the two cross-repo legs, mirroring test_revision_constants_parity.py + the validation_matrix guard (5b6f8a5). Verified: legs still pass locally, ruff check+format clean. Re-dispatch green"
  - "Explicit -f beta_version / -f tag = 3.0.0b11 on both dispatches (version-mode trap avoidance); no beta merge / tag / ship (D-02/D-06)"

requirements-completed: [ONBOARD-01]

coverage:
  - id: PY1
    description: "PyPI exposes 3.0.0b11 to pip install --pre (highest prerelease), and no stray stable 3.0.1 was produced"
    requirement: "ONBOARD-01"
    verification:
      - kind: command
        ref: "pip index versions firestarter --pre"
        status: pass
    human_judgment: false
  - id: PY2
    description: "app GH release 3.0.0b11 exists (isPrerelease=true) and its release tree includes doc/beta-testing-install.md (D-04) with __init__.py bumped to 3.0.0b11"
    requirement: "ONBOARD-01"
    verification:
      - kind: command
        ref: "gh release view 3.0.0b11 --repo henols/firestarter_app; git show origin/v1.21...:firestarter/__init__.py"
        status: pass
    human_judgment: false

duration: 20min
completed: 2026-07-26
status: complete
---

# Phase 115 Plan 04: PyPI `firestarter 3.0.0b11` Publish Summary

**Published `firestarter 3.0.0b11` to PyPI (`pip install --pre firestarter`) and the matching app GitHub release — the ONBOARD-01 Python-package half of Step 0. With Plan 03, BOTH community channels are now public; the milestone is community-installable and the PINNED-at-b10 gitlinks can move forward.**

## Performance
- **Duration:** ~20 min (incl. one safe CI failure + fix + re-dispatch)
- **Tasks:** 2 (Task 1 operator-auth checkpoint — cleared 2026-07-26 "publish b11 to PyPI"; Task 2 dispatch + verify)
- **Files modified:** 1 (test-only fix); external PyPI + GH artifacts + CI-side version bump

## Accomplishments
- **beta-release.yml (attempt 1) FAILED SAFELY** at the pytest gate — version bump / commit / Release steps never ran, so nothing was published. Root cause: `tests/test_dispatch_mirror.py` cross-repo legs read sibling `firestarter/` firmware files (`doc/PROTOCOLS.md`, `test/native/avr/test_dispatch/test_configure_memory.cpp`) that don't exist in the app-only CI checkout → 2 FileNotFoundError. Local 115-02 pre-flight passed them (firmware present as a sibling locally), so this was a local-vs-CI checkout-topology gap.
- **Fix `5cf3607`** (test-only): added `FW_ABSENT` skipif guard to the two legs, mirroring the established `test_revision_constants_parity.py` idiom + the `validation_matrix` cross-repo guard (`5b6f8a5`). Verified legs still run+pass locally, ruff `check`+`format` clean. Pushed to the app v1.21 branch.
- **beta-release.yml (attempt 2) GREEN** (run 30209122003): pytest passed, `__init__.py` bumped b10→b11 (CI git-auto-commit on the remote v1.21 branch), app GH release `3.0.0b11` (isPrerelease=true) created; release tree includes `doc/beta-testing-install.md` (D-04).
- **publish.yml GREEN** (run 30209183847): built + uploaded the wheel/sdist to PyPI.
- **Positive PyPI verification:** `pip index versions firestarter --pre` → `firestarter (3.0.0b11)` is the highest; no stray stable `3.0.1`.

## Deviations from Plan
- One safe CI failure + test-only fix + re-dispatch (documented above). The fix is a legitimate release-engineering enabler (D-01) — test-only, no product behavior change. No other deviations.

## Issues Encountered
- Cross-repo test gap (fixed, above). Non-blocking PyPI annotations: Trusted-Publisher suggestion + Node.js 20→24 deprecation (GitHub-side).

## Next Phase Readiness
- **Both channels public.** Community path (`pip install --pre firestarter` → `fw -i` → board `.hex`) is reachable — Wave 4 per-board bench validation (Plans 05-07) is unblocked (needs physical hardware).
- **Note for 115-08:** local `firestarter_app` is now behind `origin/v1.21…` by the CI b11 version-bump commit (and local `firestarter` by its CI bump); fetch/pull both before pinning the meta-repo gitlinks to the published tips.

---
*Phase: 115-beta-channel-install-and-firmware-flash-bench-validation-for*
*Completed: 2026-07-26*

## Self-Check: PASSED

- FOUND: PyPI firestarter 3.0.0b11 highest prerelease (pip index versions --pre); no stray 3.0.1
- FOUND: app GH release 3.0.0b11 (isPrerelease=true) with doc in release tree; __init__.py=3.0.0b11
- CONFIRMED: dispatches fired only after operator authorization; safe CI failure caused no partial publish
