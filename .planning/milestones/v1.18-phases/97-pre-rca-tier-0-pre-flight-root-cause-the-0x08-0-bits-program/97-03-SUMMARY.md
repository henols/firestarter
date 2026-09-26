---
phase: 97-pre-rca-tier-0-pre-flight-root-cause-the-0x08-0-bits-program
plan: 03
subsystem: testing
tags: [rca, bench, rca-02, rca-03, differential, w27c512, m27c512, 0x07, 0x08, root-cause, operator-witnessed]

# Dependency graph
requires:
  - phase: 97 (plan 02)
    provides: reproduced 0x08 0-bits signature + PRE-01 + the code-level H2-disproof (P1 route asserted) that feeds the RC-2 verdict
provides:
  - RCA-02 differential CONFIRMED — passing 0x07 W27C512 control (byte-exact write→verify) exonerates all shared axes; isolates cause to the 32-pin-only axes
  - RCA-03 closed — RC-1 CONFIRMED + RC-2 EXONERATED (each with bench+code evidence, D-03), RC-3/RC-4 not-pursued (RC-1 accounts), RC-5 INDETERMINATE (no deferral)
  - Named root cause RC-1 (pin 31 = A18 address line, not held PGM) classified host-pinout + firmware-algorithm; Phase-98 fix surfaces handed off
affects: [98-fix (DIP32_27C020 pinout / pin-31-as-PGM redirect, scoped to 0x08-UV-32-pin), 99-bench-ledger]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "2xN differential isolation: same-session same-handler passing 0x07 sibling exonerates every shared axis, collapsing the candidate space to the 0x08-only delta"
    - "Verdict survives a tooling-blocked measurement: pair each bench reading with a code-analysis finding (RC-1/RC-2 stand on code + differential when the held-rail DMM is unavailable)"

key-files:
  modified:
    - .planning/v1.18/bench/EVIDENCE.json
    - .planning/v1.18/bench/EVIDENCE.md
    - .planning/phases/97-.../evidence/97-RCA-FINDINGS.md

key-decisions:
  - "Differential control run on the Winbond W27C512 (electrically-erasable → reversible clean write→verify) after the operator first seated an ST M27C512 (UV/13V, id 0x203d) whose chip-ID check aborted the write (left pristine). The Winbond part matches the plan + check_diff07 gate + needs no rig change (VPP 12V, JP4 open)."
  - "RC-1 CONFIRMED by code + differential + elimination (not by direct pin-31 DMM, which stayed tooling-blocked). RC-2 EXONERATED by the code decode (0x188→0x89 P1 asserted) + the passing 0x07 sibling. Honest residual: the one unmeasured link is the physical pin-31/pin-1 DMM."
  - "RC-3/RC-4 explicitly NOT pursued (D-03 conditional trigger not met — RC-1 accounts for the 0-bits symptom). RC-5 INDETERMINATE pre-fix, never deferral (D-06). No deferral disposition recorded in Phase 97."

requirements-completed: [RCA-02, RCA-03]

# Metrics
duration: ~1 session segment (operator-witnessed bench, same session as 97-02)
completed: 2026-06-30
---

# Phase 97 Plan 03: RCA-02 Differential + RCA-03 Named Root Cause Summary

**Closed the RCA: the passing 0x07 Winbond W27C512 control wrote byte-exact in the same session (write 6.52s, verify 0.64s, readback SHA `d9471636…` matched) where the 0x08 AM27C020 programmed 0 bits — exonerating every shared axis. Combined with Plan 02's code-level H2-disproof (VPP IS routed to pin 1), the cause is named RC-1: socket pin 31 is modeled as address line A18 (DIP32_STD) rather than a held program-active PGM pin, so the chip gets VPP but never a program strobe. Classified host-pinout + firmware-algorithm; Phase-98 fix surfaces handed off. RC-1 CONFIRMED + RC-2 EXONERATED (D-03 exit bar met), RC-3/RC-4 not-pursued, RC-5 INDETERMINATE (no deferral).**

## Accomplishments

### RCA-02 — 0x07 differential control (PASS)
- **W27C512 byte-exact write→verify→readback** on the seated Winbond W27C512 (12.0V VPP, JP4 open, same session/same `configure_eprom` handler): write successful (6.52s), verify successful (0.64s), readback first-4KB SHA `d9471636ca34b84f863a666eff6ff6aa4fc44396b2ff11a38e036e54b4b39ee3` == image SHA.
- The passing sibling **exonerates all shared axes** (handler `memory.cpp:122`, pulse width, CE-only program model, regulator, VPE-drop, verify). The 8-row differential matrix collapses to the two 32-pin-only axes: **P1-VPP-delivery** + **pin-31-as-address**.

### RCA-03 — verdicts + named cause (D-03 exit bar)
- **RC-1 CONFIRMED (leading):** pin 31 modeled as A18 address line (`database.py:141` pin_conversions[32][31]=22), CE-only strobe (`memory.cpp:346`) → chip gets VPP at pin 1 but no program-enable on pin 31 → 0 bits. Backed by code + the 0x07/0x08 differential + RC-2 elimination.
- **RC-2 EXONERATED:** `-f 0x188` → physical `CTRL 0x89`, P1-route asserted (H2 disproven) + VPP level 13.0V → VPP reaches pin 1; 0x07 sibling proves regulator/drop/pulse. (Routing is code-confirmed; bench pin-1 DMM tooling-blocked.)
- **RC-3 / RC-4 not pursued** — D-03 trigger not met (RC-1 accounts for the symptom). RC-4's 0x08 alias (`CTRL_VPP_P1_ENABLE_REV2 == CTRL_ADDRESS_LINE_18_REV2`, dormant at A18=0) flagged as a Phase-98 fix-design concern.
- **RC-5 INDETERMINATE pre-fix** — 0-flip consistent with broken-path AND OTP; never triggers deferral (D-01/D-06). No deferral disposition recorded.
- **Classification: host-pinout (primary) + firmware-algorithm (secondary).**

### Phase-98 hand-off
- Primary fix surface: a dedicated **`DIP32_27C020`** pinout entry redirecting pin 31 from the address bus to a held PGM control, **scoped to the 0x08-UV-32-pin class** so existing 27C040/SST39SF040-family DIP32 users (pin 31 = A18/WE) are not broken (`pinouts.json` + `database.py`).
- Secondary: hold the program-enable across the full program-pulse window (`eprom.cpp`); resolve the 0x08 `P1_ENABLE == A18` firmware alias if the fix touches A18.

## Deviations from Plan
1. **Control chip = Winbond W27C512, but the operator first seated an ST M27C512** (UV, 13V, id 0x203d). Its chip-ID check (expected 0xda08) aborted the write before any program pulse, so the M27C512 stayed pristine. Swapped to the intended electrically-erasable Winbond W27C512 — the better control (reversible clean write→verify, matches the gate, no rig change). Recorded as an anomaly, not glossed (D-02).
2. **Held-rail pin-1/pin-31 DMM not physically measured** (carried from Plan 02's tooling bug). RC-1/RC-2 verdicts rest on code + the differential instead; the one unmeasured link is noted honestly as a residual that Phase-98 fix-validation closes.

## Issues Encountered
- ST M27C512 vs Winbond W27C512 confusion (both "512", very different: UV/13V/0x203d vs EEPROM/12V/0xda08). Resolved by the chip-ID readback. No chip harmed.

## Verification
- `python3 .planning/v1.18/bench/check_diff07.py` → PASS (W27C512 verdict recorded).
- `python3 .planning/v1.18/bench/check_verdict.py` → PASS (RC-1 + RC-2 verdicted, classified, 0x07 cell filled).
- 97-RCA-FINDINGS.md status = COMPLETE; differential matrix + RC-1..RC-5 table + named cause + classification + Phase-98 hand-off; no deferral recorded (D-06).

## Self-Check: PASSED
- 0x07 control result recorded verbatim (PASS); M27C512 anomaly recorded, not glossed; no fabricated values (D-02).
- check_diff07.py + check_verdict.py PASS.
- No source modified under `firestarter/` or `firestarter_app/` (diagnostic phase; Phase-98 fix named, not applied).

---
*Phase: 97-pre-rca-tier-0-pre-flight-root-cause-the-0x08-0-bits-program*
*Completed: 2026-06-30*
