---
phase: 115-beta-channel-install-and-firmware-flash-bench-validation-for
plan: 07
subsystem: bench-validation
tags: [onboarding, uno328pb, hardware-gated, best-effort, avrdude, smoke-test]

requires:
  - phase: 115 (plans 03, 04)
    provides: "both channels public at 3.0.0b11"
provides:
  - "chip-test/onboard-uno328pb.md — uno328pb per-board install->flash->smoke evidence (best-effort gate PASS, board stable this run)"
affects: [115-08-finalize-doc]

key-files:
  created:
    - chip-test/onboard-uno328pb.md
  modified: []

key-decisions:
  - "Board self-reports controller: uno328pb, so firestarter_uno328pb.hex is the correct asset — no plain-Uno substitution needed (D-05 'never silently substitute')"
  - "Best-effort gate (D-05): documented uno328pb bench-instability history did NOT recur this smoke-only run; recorded honestly as stable"

requirements-completed: [ONBOARD-01, ONBOARD-02, ONBOARD-03]

coverage:
  - id: P1
    description: "Fresh-venv install 3.0.0b11; bare fw -i -b uno328pb auto-routes --pre + flashes firestarter_uno328pb.hex + avrdude verify; fw reports controller uno328pb; hw live op OK"
    requirement: "ONBOARD-01, ONBOARD-02, ONBOARD-03"
    verification:
      - kind: command
        ref: "test -f chip-test/onboard-uno328pb.md && grep -q '3.0.0b11' && grep -q 'firestarter_uno328pb.hex'"
        status: pass
    human_judgment: false

duration: 2min
completed: 2026-07-27
status: complete
---

# Phase 115 Plan 07: uno328pb Onboarding Bench Validation Summary

**uno328pb best-effort gate PASSES — fresh-machine beta install flashed `firestarter_uno328pb.hex` via the `fw -i` `--pre` auto-route and the flashed stack is alive (fw + hw). The historically-unstable third board was stable this smoke-only run.**

## Accomplishments (all steps OK — see chip-test/onboard-uno328pb.md)
- **install:** fresh venv 3.0.0b11 from PyPI; **--version** 3.0.0b11 (ONBOARD-01).
- **fw -i -b uno328pb** on /dev/ttyUSB0: auto-route to --pre (D-23/D-24), downloaded `firestarter_uno328pb.hex` from the 3.0.0b11 prerelease, avrdude flash+verify OK (6.20s) — was 3.0.0b6 (ONBOARD-02).
- **fw:** 3.0.0b11, controller: uno328pb (ONBOARD-03 part 1). Trailing "Could not find firmware version or URL for board 'uno328pb' in the latest release" is the benign bare-`fw` STABLE-channel update check (uno328pb ships only prerelease `.hex`), NOT a version-read failure.
- **hw:** Rev 2.0-class — live protocol op OK (ONBOARD-03 part 2).

## Decisions / honest-fallback (D-05/D-08)
- Board self-identifies as uno328pb → its own `.hex` is correct; no substitution.
- Documented uno328pb instability (read timeouts / 0xff drift / VPP misread / PROGRAM brownout) did NOT recur — recorded as stable, not rubber-stamped. As best-effort, a failure here would have been a note + FUT item, not a close blocker; none needed.

## Deviations from Plan
- Shared fresh throwaway venv across boards for the install leg (as in Plans 05/06). No other deviations.

## Issues Encountered
None this run. (Board has a documented instability history; monitor on future benches.)

## Next Phase Readiness
Best-effort gate green. Evidence at chip-test/onboard-uno328pb.md feeds 115-08. All three boards validated → Wave 5 (doc finalize + gitlink bump) unblocked.

---
*Completed: 2026-07-27*

## Self-Check: PASSED
- FOUND: chip-test/onboard-uno328pb.md with 3.0.0b11 + firestarter_uno328pb.hex + avrdude flash+verify + fw/hw OK
