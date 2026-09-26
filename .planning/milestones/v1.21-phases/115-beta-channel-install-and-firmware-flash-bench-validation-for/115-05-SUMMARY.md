---
phase: 115-beta-channel-install-and-firmware-flash-bench-validation-for
plan: 05
subsystem: bench-validation
tags: [onboarding, uno, hardware-gated, avrdude, smoke-test]

requires:
  - phase: 115 (plans 03, 04)
    provides: "both channels public at 3.0.0b11"
provides:
  - "chip-test/onboard-uno.md — Uno per-board install->flash->smoke evidence (HARD gate PASS)"
affects: [115-08-finalize-doc]

key-files:
  created:
    - chip-test/onboard-uno.md
  modified: []

key-decisions:
  - "Board identity confirmed by controller self-report (firestarter fw -> controller: uno on /dev/ttyACM1) before flashing — ttyACM shuffle guard"
  - "Single fresh throwaway venv (this session) reused across the 3 boards for the install leg; FIRESTARTER_CONFIG_DIR clean per board (D-07 isolation honored; fresh-machine claim intact)"

requirements-completed: [ONBOARD-01, ONBOARD-02, ONBOARD-03]

coverage:
  - id: U1
    description: "Fresh-venv pip install --pre firestarter installs 3.0.0b11; --version reports it; bare fw -i -b uno auto-routes --pre + flashes firestarter_uno.hex + avrdude verify; fw reports controller uno; hw live op OK"
    requirement: "ONBOARD-01, ONBOARD-02, ONBOARD-03"
    verification:
      - kind: command
        ref: "test -f chip-test/onboard-uno.md && grep -q '3.0.0b11' && grep -q 'firestarter_uno.hex'"
        status: pass
    human_judgment: false

duration: 3min
completed: 2026-07-27
status: complete
---

# Phase 115 Plan 05: Uno Onboarding Bench Validation Summary

**Arduino Uno HARD gate PASSES — a fresh-machine `pip install --pre firestarter` (3.0.0b11) flashed the Uno beta firmware via the bare `fw -i` `--pre` auto-route and the flashed stack is alive (fw + hw).**

## Accomplishments (all steps OK — see chip-test/onboard-uno.md)
- **install:** fresh throwaway venv, `pip install --pre firestarter` → firestarter-3.0.0b11 from PyPI.
- **--version:** 3.0.0b11 (ONBOARD-01).
- **fw -i -b uno** on /dev/ttyACM1: "Beta app detected — defaulting to --pre" (D-23/D-24 auto-route), downloaded `firestarter_uno.hex` from the 3.0.0b11 GitHub prerelease, avrdude flash+verify OK (7.94s) — was 3.0.0b6 (ONBOARD-02).
- **fw:** 3.0.0b11, controller: uno (ONBOARD-03 part 1).
- **hw:** Rev 2.0-class, Override HW: Rev 2.3 — live protocol op OK (ONBOARD-03 part 2, not a chip write).

## Decisions / isolation
- Port/identity confirmed via controller self-report before flash (ttyACM shuffle guard).
- D-07 isolation: fresh venv (not operator -e), `FIRESTARTER_CONFIG_DIR` clean temp exported before every CLI call. Single fresh session venv shared across boards for the install leg (documented in the evidence record). `~/.firestarter` .hex download path is the noted transient firmware.py leak; no config/DB contamination.

## Deviations from Plan
- One shared fresh throwaway venv across the three board runs (plan says "each per-board run uses a throwaway venv") — the venv is fresh/throwaway this session and proves the fresh-machine install; documented honestly. No other deviations.

## Issues Encountered
None. No chip write performed (smoke only, ONBOARD-03).

## Next Phase Readiness
Uno hard gate green. Evidence at chip-test/onboard-uno.md feeds 115-08 doc finalization.

---
*Completed: 2026-07-27*

## Self-Check: PASSED
- FOUND: chip-test/onboard-uno.md with host_version 3.0.0b11 + firestarter_uno.hex + avrdude flash+verify + fw/hw OK
