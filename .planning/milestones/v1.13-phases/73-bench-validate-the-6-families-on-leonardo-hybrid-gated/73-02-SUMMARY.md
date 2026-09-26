---
phase: 73-bench-validate-the-6-families-on-leonardo-hybrid-gated
plan: 02
subsystem: testing
tags: [bench-validation, eprom, w27c512, leonardo, tier-3, hil, val-01]

# Dependency graph
requires:
  - phase: 73-01
    provides: "r1=270000 persisted to config.json, chipless SKIP-deferred cells emitted, Leonardo confirmed on /dev/ttyACM0"
provides:
  - "VAL-01 Tier-3 closed: W27C512 PASS on Leonardo, pass_type=authoritative"
  - "Passing negative control: wrong-file verify exited non-zero, oracle proven non-vacuous"
  - "Tier-3 eprom cell in val-results/eprom/validation-matrix.json with evidence_sha"
affects: [73-03, phase-74, phase-75]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "dev validate-family eprom invoked with --board leonardo --chip W27C512 --source <image> --output-dir val-results/eprom"
    - "Negative control: firestarter verify W27C512 <wrong-file> must exit non-zero after a PASS run"

key-files:
  created:
    - "firestarter_app/val-results/eprom/validation-matrix.json"
    - "firestarter_app/val-results/eprom/validation-matrix.md"
    - "firestarter_app/val-results/eprom/w27c512-source.bin"
    - "firestarter_app/val-results/eprom/w27c512-wrongfile.bin"
    - "firestarter_app/val-results/eprom/cycle_01_readback.bin"
  modified: []

key-decisions:
  - "W27C512 confirmed as electrically-erasable EEPROM (12V VPP, configure_eprom 0x07 family) per D-04 — NOT UV-EPROM; ROADMAP UV-EPROM label is handler-family shorthand"
  - "val-results/eprom .bin files force-added to git despite *.bin gitignore rule (evidence artifacts required by plan must_haves)"
  - "Tier-3 verdict = PASS; no routing to Phase 74 (FAIL would have routed per D-12)"

patterns-established:
  - "Pre-write gate sequence: fw (controller id) -> hw (shield rev) -> config (R1 in-band) before any HIL write"
  - "Negative control immediately after PASS: verify against wrong-file must exit non-zero"

requirements-completed: [VAL-01]

# Metrics
duration: 3min
completed: 2026-06-17
---

# Phase 73 Plan 02: W27C512 Tier-3 eprom HIL cell PASS on Leonardo with authoritative pass_type + passing negative control

**W27C512 (electrically-erasable EEPROM, 12V VPP, configure_eprom 0x07) achieves authoritative Tier-3 PASS on Leonardo/Rev 2.0 — write_cycle_eprom erase+write+readback SHA match confirmed, negative control oracle proven non-vacuous (wrong-file verify exits 1)**

## Performance

- **Duration:** 3 min
- **Started:** 2026-06-17T13:23:37Z
- **Completed:** 2026-06-17T13:26:54Z
- **Tasks:** 1 (Task 1: Verify Leonardo identity + live R1, then run the W27C512 Tier-3 eprom cell)
- **Files modified:** 5 (all in firestarter_app/val-results/eprom/)

## Accomplishments

- Pre-write gate confirmed: controller=leonardo, shield=Rev 2.0, R1=270000 (within [202500,337500])
- W27C512 Tier-3 HIL cell: `dev validate-family eprom --board leonardo --chip W27C512` exited 0 (PASS)
- Emitted cell: `verdict=PASS, pass_type=authoritative, evidence_sha=9521375d0847e99b46c6db8d5590d120aaea87c529272243decece3b22ef3490, retry_count=1`
- Negative control PASS: `firestarter verify W27C512 w27c512-wrongfile.bin` exited 1 (verify FAILED, oracle proven)
- VAL-01 Tier-3 closed per D-12 on Leonardo

## Bench Run Details

### Pre-Write Gate (T-73-05, T-73-07 mitigated)

| Check | Command | Result |
|-------|---------|--------|
| Controller identity | `firestarter -p /dev/ttyACM0 fw` | `controller: leonardo` (firmware 3.0.0b8) |
| Shield revision | `firestarter -p /dev/ttyACM0 hw` | `Rev 2.0-class` (operator-confirmed Rev 2.0) |
| Live R1 | `firestarter -p /dev/ttyACM0 config` | R1=270000 (in band [202500,337500]) |
| r1 gate armed | `~/.firestarter/config.json` | `"r1": 270000` persisted from 73-01 |

### W27C512 Tier-3 Cell

- **Chip:** W27C512 (WINBOND EEPROM, `electrical.type: EEPROM`, 12V VPP, 28-pin DIP)
- **Family:** eprom (`configure_eprom`, algorithm 0x07)
- **Source image:** 65536-byte deterministic non-trivial pattern (position-mixed 0xA5/0x5A)
  SHA256=`9521375d0847e99b46c6db8d5590d120aaea87c529272243decece3b22ef3490`
- **Runner:** `dev validate-family eprom --board leonardo --chip W27C512 --source val-results/eprom/w27c512-source.bin --output-dir val-results/eprom`
- **Erase:** 4.92s (eprom_internal_erase, 12V VPP via A9/OE-VPP high rail — Assumption A1 confirmed)
- **Write:** 22.86s (write_eprom, pulse-delay retry loop converged)
- **Readback:** Full 65536-byte read → SHA compare matched → PASS
- **Exit code:** 0 (PASS)

### Emitted Tier-3 Cell

```json
{
  "family": "eprom",
  "board": "leonardo",
  "tier": 3,
  "verdict": "PASS",
  "pass_type": "authoritative",
  "evidence_sha": "9521375d0847e99b46c6db8d5590d120aaea87c529272243decece3b22ef3490",
  "retry_count": 1
}
```

### Negative Control (T-73-06 mitigated)

- **Wrong file:** 65536-byte distinct pattern (position-mixed 0x5A/0xA5+0x33)
  SHA256=`4c47a7eef7f5f2d6dfc84c43e15f18fabf66b2ac2baef35988f7906f75204b9f`
- **Command:** `firestarter -p /dev/ttyACM0 verify W27C512 val-results/eprom/w27c512-wrongfile.bin`
- **Result:** ERROR: `0x33 != 0x00 at 0x000000` — verify FAILED, exit code=1
- **Oracle proven non-vacuous:** verify CAN distinguish a bad write from a good one

## Task Commits

1. **Task 1: W27C512 Tier-3 eprom HIL cell + negative control** - `d3b6302` in firestarter_app (feat)

**Plan metadata:** (docs commit follows in meta repo)

## Files Created/Modified

- `firestarter_app/val-results/eprom/validation-matrix.json` — Tier-3 eprom cell with PASS verdict, authoritative pass_type, evidence_sha
- `firestarter_app/val-results/eprom/validation-matrix.md` — human-readable cell table
- `firestarter_app/val-results/eprom/w27c512-source.bin` — 65536-byte non-trivial source image (force-added, *.bin gitignored)
- `firestarter_app/val-results/eprom/w27c512-wrongfile.bin` — 65536-byte wrong-file for negative control (force-added)
- `firestarter_app/val-results/eprom/cycle_01_readback.bin` — full post-write readback artifact from write_cycle_eprom (force-added)

## Decisions Made

- W27C512 is an electrically-erasable EEPROM (12V VPP, configure_eprom 0x07 family), NOT a UV-EPROM. The ROADMAP "UV-EPROM 0x07/08/0B" label is handler-family shorthand (D-04).
- Verdict = PASS; no routing to Phase 74 (D-12 — FAIL would have routed there).
- .bin evidence artifacts force-added to git (plan must_haves require them despite *.bin gitignore).
- Assumption A1 confirmed: write_cycle_eprom's erase_eprom step handles W27C512 pre-erase correctly (erase fires at 12V VPP, chip accepts it, write succeeds).

## Deviations from Plan

None - plan executed exactly as written. The only minor note is that `.bin` files in `firestarter_app/` are gitignored by `*.bin` in `.gitignore`; used `git add -f` to force-track the evidence artifacts as required by the plan's `files_modified` frontmatter.

## Issues Encountered

- `.bin` files blocked by `*.bin` gitignore rule in firestarter_app. Resolved with `git add -f` since the plan explicitly requires these as committed evidence artifacts (D-12 evidence sha).

## Threat Surface Scan

No new network endpoints, auth paths, or schema changes. This plan drives hardware via existing CLI — no new production surface introduced.

## Next Phase Readiness

- VAL-01 Tier-3 is closed with authoritative PASS on Leonardo — no Phase 74 routing needed for eprom family.
- Plan 73-03 (flash3 / AM29F040 HIL cell) is unblocked. The AM29F040 chip replacement checkpoint is next (operator must swap chip to AM29F040).
- Phase 75 (erase path) is informed: write_cycle_eprom's explicit erase works (A1 confirmed); Phase 75 scope = wire FLAG_CAN_ERASE from electrical.type so standalone `firestarter erase W27C512` routes correctly.

## Self-Check: PASSED

- FOUND: firestarter_app/val-results/eprom/validation-matrix.json
- FOUND: firestarter_app/val-results/eprom/w27c512-source.bin
- FOUND: firestarter_app/val-results/eprom/w27c512-wrongfile.bin
- FOUND: .planning/phases/73-bench-validate-the-6-families-on-leonardo-hybrid-gated/73-02-SUMMARY.md
- FOUND: submodule commit d3b6302 (firestarter_app)
- FOUND: meta commit 701dd59 (SUMMARY.md + STATE.md + ROADMAP.md)

---
*Phase: 73-bench-validate-the-6-families-on-leonardo-hybrid-gated*
*Completed: 2026-06-17*
