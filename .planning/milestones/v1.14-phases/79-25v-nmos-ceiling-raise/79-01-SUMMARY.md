---
phase: 79-25v-nmos-ceiling-raise
plan: 01
subsystem: hardware-vpp-safety-gate
tags: [nmos, vpp, vpe, 25v, hardware-gate, direct-vpe, multimeter, dry-run, rev2.0, leonardo, corrected-methodology, rail-correction]
requires:
  - phase: 79 (standing bench precondition)
    provides: "operator-confirmed silkscreen shield rev + live R1/R2 readback + Leonardo controller identity so the firmware-mediated reading is trustworthy"
provides:
  - "NMOS-01 gate evidence (rail-corrected 2026-06-23): shield rev (Rev 2.0), controller identity (leonardo @ /dev/ttyACM0, fw 3.0.0b8), live R1/R2 (270000/44000), chip-OUT confirmation, pot-at-MAX. RAIL READINGS: VPP ~15-19V (operator DMM) / 18.7V (firmware `firestarter vpp`); VPE 22.4V (operator DMM, AUTHORITATIVE) / 23.9V (firmware `firestarter vpe`)."
  - "Verdict at the strict ≥25V bar: NOT CLEARED (VPE 22.4V < 25V) — but the ≥25V hard pre-gate was subsequently RETIRED by the operator (CONTEXT D-07 best-effort override). The 4 NMOS chips program on the VPE rail (~22.4V delivered), ~90% of 25V."
affects:
  - "79-02 (proceeded under D-07 override — best-effort graduation, NOT gated on ≥25V)"
  - "79-03 (informational best-effort bench validation — the only definitive test of whether ~22.4V VPE programs a real 25V NMOS chip)"
tech-stack:
  added: []
  patterns: ["safety-gate-first hardware dry-run", "operator-multimeter authoritative VPP/VPE measurement at max pot", "firmware `firestarter vpe` (CMD_READ_VPE, regulator-only 0x80) reads the SAME rail the 0x0B write path uses"]
key-files:
  created:
    - ".planning/phases/79-25v-nmos-ceiling-raise/79-01-SUMMARY.md (regenerated twice — corrected methodology, then rail-corrected)"
  modified: []
key-decisions:
  - "Shield rev = Rev 2.0 (operator silkscreen, authoritative); Modified Rev 0 excluded, not mounted"
  - "RAIL CORRECTION (operator, 2026-06-23): the ~15-19V originally logged as the 'direct VPE' reading was actually VPP. The VPE is 22.4V (operator DMM). Firmware ADC confirms the gap: `firestarter vpp`=18.7V (dropped path), `firestarter vpe`=23.9V (direct path)."
  - "The 4 NMOS chips are protocol 0x0B → both eprom_check_vpp (eprom.cpp:218) and eprom_write_execute (eprom.cpp:145) use CTRL_VPP_REGULATOR_ENABLE only (0x80) — the SAME config `firestarter vpe` reads (22.4-23.9V). So a real NMOS write programs off the ~22.4V VPE rail."
  - "≥25V hard pre-gate (D-05) RETIRED by operator override D-07; graduation proceeds best-effort regardless of the <25V reading"
patterns-established:
  - "Firmware VPP enforcement is over-voltage BLOCK + under-voltage WARN-and-proceed (eprom_check_vpp, eprom.cpp:209-272). At VPE ~22.4V vs a declared 25V, the firmware warns (22.4V < 23.75V = 95% threshold) and proceeds — best-effort. The firmware ADC reads the regulator RAIL (23.9V), not the socket-delivered pin voltage (22.4V DMM), so the only definitive proof is a real write + read-back SHA (79-03)."
requirements-completed: [NMOS-01]
duration: ~20min
completed: 2026-06-23
---

# Phase 79 Plan 01: 25V NMOS Ceiling Raise — Hardware Gate (NMOS-01) Summary

**Rail-corrected 2026-06-23 (operator).** The chip-OUT dry-run at max pot measured both rails. **VPP ≈ 15–19V** (operator DMM) / **18.7V** (firmware `firestarter vpp`, dropped path). **VPE = 22.4V** (operator DMM, authoritative) / **23.9V** (firmware `firestarter vpe`, direct path). The 4 NMOS chips program on the **VPE rail (~22.4V)** — ~90% of the rated 25V. At the strict ≥25V bar the gate is NOT CLEARED (22.4V < 25V), **but that bar was retired by the operator (CONTEXT D-07)** in favor of best-effort graduation. An earlier version of this summary mis-attributed the ~15–19V VPP reading to the VPE rail and wrongly concluded a boost-stage hardware change was required — that is corrected here.

## Standing Bench Precondition (Task 1)

| Item | Value | Source |
|------|-------|--------|
| Silkscreen shield rev | **Rev 2.0** (accepted; NOT Modified Rev 0) | Operator (authoritative, 2026-06-23) |
| Controller identity | `leonardo` on `/dev/ttyACM0`, firmware `3.0.0b8` | `firestarter -p /dev/ttyACM0 fw` |
| Hardware revision (EEPROM byte) | Rev 2.0-class | `firestarter -p /dev/ttyACM0 hw` |
| Live R1 / R2 readback | **R1 = 270000, R2 = 44000** | `firestarter -p /dev/ttyACM0 config` |

Rev 0 is excluded by the standing bench rule (`eprom_check_vpp` WARNs, never errors, on `REVISION_0`). R1/R2 match the calibrated unit, so the firmware ADC readings are trustworthy.

## Chip-OUT Rail Measurement at MAX pot (Task 2 — T-79-VPP)

| Rail | Operator DMM (authoritative) | Firmware ADC | Register config | What uses it |
|------|------------------------------|--------------|-----------------|--------------|
| **VPP (dropped path)** | **~15–19 V** | 18.7V (`firestarter vpp`) | `CTRL_VPP_REGULATOR_ENABLE \| CTRL_VPP_VPE_DROP_ENABLE` | EPROM_STD/QUICK (0x07/0x08) |
| **VPE (direct path)** | **22.4 V** | 23.9V (`firestarter vpe`) | `CTRL_VPP_REGULATOR_ENABLE` only (0x80) | **0x0B / EPROM_LEGACY — the 4 NMOS chips** |

Socket confirmed EMPTY (chip-OUT); pot at MAX. The 0x0B NMOS write path and `eprom_check_vpp` both use the regulator-only (0x80) config — the same rail `firestarter vpe` reads — so the chips program off the **~22.4V VPE rail**.

## Verdict & Disposition

- **Strict ≥25V bar:** NOT CLEARED — VPE 22.4V (DMM) / 23.9V (ADC) is below 25V.
- **Operator override (CONTEXT D-07):** the ≥25V hard pre-gate is **retired**; no hardware change, ever. The 4 NMOS chips graduate to `supported` **best-effort** (79-02, shipped) and program on the VPE rail at ~22.4V. The firmware warns under-voltage (22.4V < 23.75V = 95% of 25V) and proceeds; over-voltage stays blocked as the damage boundary. An under-driven write cannot damage the chip; it may simply not fully verify.
- **Caveat:** the firmware ADC measures the regulator rail (23.9V), not the socket-delivered pin voltage (22.4V DMM). The definitive test of whether ~22.4V actually programs a real 25V NMOS chip is the **79-03 bench write + independent read-back SHA**, deferred until a physical chip is on hand.

## Threat Model Disposition

- **T-79-VPP** (hardware damage): **mitigated** — over-voltage is impossible at 22.4V < 25V; under-voltage is harmless.
- **T-79-WRONGRAIL** (false safety signal): **mitigated/clarified** — the prior wrong-rail confusions (2026-06-22 `firestarter vpp`=~12V; the mis-attributed ~15-19V) are resolved: VPP ≈ 15-19V, VPE = 22.4V, and the chips use VPE.
- **T-79-REV0**: **mitigated** — Rev 2.0 confirmed; Rev 0 not mounted.

## Self-Check: PASSED

The gate was evaluated and the rail readings recorded accurately (after the operator's rail correction). The ≥25V verdict is moot under the D-07 override; the substantive outcome is that the NMOS chips program on the ~22.4V VPE rail, best-effort, pending the 79-03 bench confirmation.
