---
phase: 115-beta-channel-install-and-firmware-flash-bench-validation-for
plan: 06
subsystem: bench-validation
tags: [onboarding, leonardo, hardware-gated, avrdude, smoke-test]

requires:
  - phase: 115 (plans 03, 04)
    provides: "both channels public at 3.0.0b11"
provides:
  - "chip-test/onboard-leonardo.md — Leonardo per-board install->flash->smoke evidence (HARD gate PASS)"
affects: [115-08-finalize-doc]

key-files:
  created:
    - chip-test/onboard-leonardo.md
  modified: []

key-decisions:
  - "Board identity confirmed by controller self-report (controller: leonardo on /dev/ttyACM0) before flashing"
  - "Leonardo bootloader port re-enumeration handled internally by avr_tool; flash completed on /dev/ttyACM0"

requirements-completed: [ONBOARD-01, ONBOARD-02, ONBOARD-03]

coverage:
  - id: L1
    description: "Fresh-venv install 3.0.0b11; bare fw -i -b leonardo auto-routes --pre + flashes firestarter_leonardo.hex + avrdude verify; fw reports controller leonardo; hw live op OK"
    requirement: "ONBOARD-01, ONBOARD-02, ONBOARD-03"
    verification:
      - kind: command
        ref: "test -f chip-test/onboard-leonardo.md && grep -q '3.0.0b11' && grep -q 'firestarter_leonardo.hex'"
        status: pass
    human_judgment: false

duration: 2min
completed: 2026-07-27
status: complete
---

# Phase 115 Plan 06: Leonardo Onboarding Bench Validation Summary

**Arduino Leonardo HARD gate PASSES — fresh-machine beta install flashed the Leonardo beta firmware via the `fw -i` `--pre` auto-route and the flashed stack is alive (fw + hw).**

## Accomplishments (all steps OK — see chip-test/onboard-leonardo.md)
- **install:** fresh venv `pip install --pre firestarter` → 3.0.0b11 from PyPI; **--version** 3.0.0b11 (ONBOARD-01).
- **fw -i -b leonardo** on /dev/ttyACM0: auto-route to --pre (D-23/D-24), downloaded `firestarter_leonardo.hex` from the 3.0.0b11 prerelease, avrdude flash+verify OK (5.35s) — was 3.0.0b10 (ONBOARD-02).
- **fw:** 3.0.0b11, controller: leonardo (ONBOARD-03 part 1).
- **hw:** Rev 2.0-class, Override HW: Rev 2.0-class — live protocol op OK (ONBOARD-03 part 2).

## Decisions / isolation
- Identity confirmed via controller self-report before flash. D-07 isolation as in Plan 05 (fresh venv, clean FIRESTARTER_CONFIG_DIR). Leonardo caterina-bootloader re-enumeration handled by avr_tool.

## Deviations from Plan
- Shared fresh throwaway venv across boards for the install leg (as documented in Plan 05). No other deviations.

## Issues Encountered
None. No chip write (smoke only).

## Next Phase Readiness
Leonardo hard gate green. Evidence at chip-test/onboard-leonardo.md feeds 115-08.

---
*Completed: 2026-07-27*

## Self-Check: PASSED
- FOUND: chip-test/onboard-leonardo.md with 3.0.0b11 + firestarter_leonardo.hex + avrdude flash+verify + fw/hw OK
