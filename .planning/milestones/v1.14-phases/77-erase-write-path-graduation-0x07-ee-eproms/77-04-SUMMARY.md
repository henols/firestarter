---
phase: 77-erase-write-path-graduation-0x07-ee-eproms
plan: 04
subsystem: testing
tags: [bench, leonardo, w27c512, auto-erase, vpp, sha-match, negative-control, erase-02]

requires:
  - phase: 77-erase-write-path-graduation-0x07-ee-eproms
    provides: FLAG_CAN_ERASE on the wire (Plan 01) + 0xA4 guard (Plan 02) + SAFE gates (Plan 03)
provides:
  - hardware graduation evidence — write→auto-erase→program→verify proven on real W27C512
affects: [v1.14, phase-78, phase-79, phase-80]

tech-stack:
  added: []
  patterns: [chip-out-vpp-dry-run, sha-match-read-oracle, non-vacuous-negative-control]

key-files:
  created: []
  modified: []

key-decisions:
  - "Raise the erase rail for the chip-OUT dry-run via `dev reg 0 0 0x86 -f` (REGULATOR|A9|VPE, no drop resistor) — mirrors eprom_internal_erase; vpp/vpe CLI is measure-only and won't route to socket"

patterns-established:
  - "Held-register erase-rail dry-run for a steady DMM reading (vs chasing the brief auto-erase pulse)"

requirements-completed: [ERASE-02]

duration: 25min
completed: 2026-06-22
---

# Phase 77 Plan 04: Leonardo Bench Proof Summary

**The full write→auto-erase→program→verify cycle is proven on a real non-blank W27C512 on the Leonardo: clean no-`-b` write (no 0xA4), independent read SHA-matches the source, and a wrong-file verify exits non-zero — the milestone's first hardware graduation (ERASE-02 / SC#2 / SC#3).**

## Performance

- **Duration:** ~25 min (operator bench session, Claude driving serial over USB passthrough)
- **Tasks:** 3 (all blocking-human checkpoints)
- **Files modified:** 0 (bench evidence only)

## Bench Record

### Standing precondition (Task 1)
- **Board:** Leonardo — firmware reports `controller: leonardo`, version **3.0.0b8** — on **/dev/ttyACM0** (re-verified this session; Leonardo is the only trustworthy write/verify board, v1.9 read bug). Leonardo exempt from chip-OUT-before-sideload.
- **Shield rev:** **Rev 2.0** — operator-confirmed off the silkscreen; the EEPROM `hw` byte also reports `Rev 2.0-class, Override HW: Rev 2.0-class` (agrees).
- **R1/R2:** `R1: 270000, R2: 44000` — `r1 ≈ 270000` reconciled (VPP-calibration value correct, so the VPP measurement is meaningful).

### SC#3 — chip-OUT 14V erase-rail VPP dry-run (Task 2)
- **Chip OUT confirmed** by operator before energizing.
- Erase rail raised + held via `firestarter -p /dev/ttyACM0 dev reg 0 0 0x86 -f` — asserts `CTRL_VPP_REGULATOR_ENABLE(0x80) | CTRL_VPP_A9_ENABLE(0x02) | CTRL_VPE_ENABLE(0x04)` with the dropping resistor NOT set, mirroring `eprom_internal_erase` (eprom.cpp:274-288) → full VPE routed to the A9 + VPE/PGM socket pins.
- **Measured VPP ≈ 14V** (operator DMM, chip OUT) — under the **22V** `RURP_VPP_CEILING_MV` ceiling. **SC#3 PASS.**
- Rail explicitly cleared afterward (`dev reg 0 0 0x00 -f -d`).
- Note: the `vpp`/`vpe` CLI commands are measure-only (enable regulator + read; no A9/VPE/P1 socket routing), so the held-register method above is the correct way to get a steady, measurable erase rail at the socket.

### SC#2 — seated write→auto-erase→program→verify + SHA + negative control (Task 3)
- **Non-blank W27C512 seated** (operator) so auto-erase is genuinely exercised.
- **Default write (no `-b`):** `write W27C512 /workspaces/W27C512.bin` → `Write to W27C512 successful (22.86s)`, exit 0. The log shows two passes (blank-check/erase-init DATA progress, then program); **completed clean with no 0xA4 / empty-input error** — live D-07 proof that the no-`-b` auto-erase path completes clean.
- **Independent read SHA match (read oracle):**
  - source `/workspaces/W27C512.bin`: `71189f7fb6aed638640078fba3a35fda6c39c8962e74dcc75935aac948da9063`
  - readback: `71189f7fb6aed638640078fba3a35fda6c39c8962e74dcc75935aac948da9063` — **identical**.
- **Non-vacuous negative control:** `verify W27C512 wrong.bin` (source with first byte flipped) → `ERROR: 0x00 != 0xff at 0x000000`, `Verify for W27C512 failed.`, **exit 1** (non-zero). Proves the verify oracle is real.

## Decisions Made
- Erase-rail dry-run method: held-register `dev reg 0 0 0x86 -f` for a steady DMM reading (operator-authorized), since `vpp`/`vpe` do not route to the socket.
- Per D-04, a SINGLE bench cycle is sufficient for this graduation (N≥5 not required).

## Deviations from Plan
None - the plan's bench sequence executed as written; the "equivalent erase-rail command" was resolved to the held-register `dev reg` form after confirming `vpp`/`vpe` are measure-only.

## Issues Encountered
None. Write 22.86s, read 7.26s, both clean; negative control behaved correctly.

## Next Phase Readiness
- ERASE-02 graduation evidence on record — Phase 77 erase write-path graduation is complete on real silicon.
- Establishes the SAFE-01/02/03 graduation pattern for Phases 78-80 (standing bench precondition + chip-OUT VPP dry-run + SHA-match oracle + non-vacuous negative control).

---
*Phase: 77-erase-write-path-graduation-0x07-ee-eproms*
*Completed: 2026-06-22*
