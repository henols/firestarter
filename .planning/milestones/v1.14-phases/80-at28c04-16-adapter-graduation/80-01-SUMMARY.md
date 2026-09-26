---
phase: 80-at28c04-16-adapter-graduation
plan: 01
subsystem: hardware-adapter-gate
tags: [at28c04, at28c16, dip24-dip32-adapter, hardware-gate, dmm-continuity, we-reroute, not-cleared, clean-deferral, fut-04, eeprom28c, 0x0d]
requires:
  - phase: 76 (verified DIP24→DIP32 pin map, D-04)
    provides: "the operator-canonical adapter wiring table (firestarter/doc/AT28C04-ADAPTER.md) the build would follow"
provides:
  - "ADPT-01 hardware-gate evaluated: verdict NOT CLEARED — the physical DIP24→DIP32 adapter is not built and no AT28C04/AT28C16 chip is confirmed on hand; no board is connected at evaluation time"
  - "Clean-deferral record: zero DB/code/constants change; the 9 AT28C chips stay honestly support_status='adapter-required'; the v1.12 host-guard refusal is untouched"
affects:
  - "80-02 (BLOCKED — RED graduation tests must not run; nothing to graduate without a CLEARED adapter gate)"
  - "80-03 (BLOCKED — the _AT28C_DIP24_NAMES arm must NOT be deleted; no DB regen)"
  - "80-04 (BLOCKED — no adapter + no chip → no bench proof possible)"
tech-stack:
  added: []
  patterns: ["gating hardware dry-run FIRST", "gate-NOT-CLEARED → clean deferral with zero source/DB change (mirrors Phase 78 DEFER + Phase 79 NMOS-01 NOT CLEARED discipline)"]
key-files:
  created:
    - ".planning/phases/80-at28c04-16-adapter-graduation/80-01-SUMMARY.md"
  modified: []
key-decisions:
  - "Operator elected to DEFER CLEANLY: the DIP24→DIP32 adapter is not built and no AT28C04/AT28C16 chip is confirmed on hand for the Plan 04 bench proof"
  - "No board connected at evaluation (no /dev/ttyACM* or /dev/ttyUSB*), so the standing bench precondition (port identity, live r1≈270000 readback) could not be recorded — but it is moot: the gate fails at the adapter-build / chip-availability precondition regardless"
  - "Because 0x0D (configure_eeprom28c) is VPP-free (5V-only), the deferred risk class is non-function, not damage — but the graduation still requires the build + the final Leonardo bench proof, neither of which can run now"
patterns-established:
  - "The physical adapter is the only hardware gate in this phase; with no adapter and no chip there is nothing to validate and no honest basis to flip the chips to 'supported' — the clean-deferral branch is the correct terminal outcome"
requirements-completed: [ADPT-01]
duration: ~5min
completed: 2026-06-22
---

# Phase 80 Plan 01: AT28C04/16 Adapter Graduation — Hardware Gate (ADPT-01) Summary

**The gating DIP24→DIP32 adapter is not built and no AT28C04/AT28C16 chip is confirmed on hand; no board is connected at evaluation time. Gate verdict: HARDWARE-GATE NOT CLEARED. Per the operator decision the phase DEFERS CLEANLY — zero DB/code/constants change, the 9 AT28C chips stay honestly `adapter-required`, Plans 02/03/04 are BLOCKED, and a FUT-04 unblock item is recorded.**

## Performance

- **Duration:** ~5 min
- **Completed:** 2026-06-22T21:20:45Z
- **Tasks:** 2 (both `checkpoint:human` gates evaluated)
- **Files modified:** 0 source / 0 DB / 0 constants (deferral record only)

## Standing Bench Precondition (Task 1)

| Item | Value | Source |
|------|-------|--------|
| Board connected | **None** (`/dev/ttyACM*` and `/dev/ttyUSB*` both absent) | devcontainer device scan |
| Silkscreen shield rev | Not recorded — no board mounted | — |
| Controller identity | Not recorded — no board mounted | — |
| Live R1 / R2 readback | Not recorded — no board mounted | — |
| **AT28C04 / AT28C16 chip on hand** | **Not confirmed on hand** | Operator (authoritative) |

The standing bench precondition is moot for this evaluation: with no board connected and no AT28C chip confirmed available, the gate fails at the adapter-build / chip-availability precondition before any serial readback would matter. (Last-known bench state, for the eventual resume, was leonardo @ /dev/ttyACM0, fw 3.0.0b8, shield Rev 2.0, R1=270000/R2=44000 — re-verify live, do not trust stale.)

## Adapter Build + DMM Continuity Gate (Task 2 — T-80-WIRE)

| Item | State | Notes |
|------|-------|-------|
| Physical DIP24→DIP32 adapter | **Not built** | per `firestarter/doc/AT28C04-ADAPTER.md` (would-be source) |
| DMM continuity check (chip OUT) | **Not performed** | no adapter to check |
| Critical /WE reroute (chip pin 21 → socket pin 30) | **Not verified** | the single error-prone wire; deferred with the build |
| AT28C04 A9/A10 NC-pin routing | **Not verified** | deferred with the build |
| **Verdict** | **NOT CLEARED — adapter not built / no chip** | clean-deferral branch taken |

The gate is purely mechanical (adapter-built vs not) — no dangerous voltage measurement is involved because the 0x0D handler is VPP-free (5V-only). The adapter simply does not exist yet, and no AT28C chip is confirmed on hand for the eventual Plan 04 bench proof, so there is nothing to build-verify and nothing to bench-prove.

## Verdict & Deferral

**Gate verdict: HARDWARE-GATE NOT CLEARED.** Per the operator decision, the phase takes the built-in **clean-deferral** branch (mirroring Phase 78 FUT-01 and Phase 79 NMOS-01 NOT CLEARED):

- **No DB change** — `chip_database.json` untouched.
- **No code change** — `build_db.py` `_AT28C_DIP24_NAMES` named arm stays in place.
- **No constants change** — `constants.py` / `firestarter.h` untouched (SAFE-03 parity holds trivially).
- The 9 AT28C04/AT28C16 chips stay honestly `support_status='adapter-required'`; the v1.12 `chip_resolver` host-guard refusal is preserved.
- **Plans 02/03/04 are BLOCKED** — there is nothing to graduate and no honest basis to flip the chips to `supported` without the adapter build + Leonardo bench proof.

**FUT-04 (future unblock):** *Phase 80 ADPT-01 hardware gate not cleared — physical DIP24→DIP32 adapter not built and no AT28C04/AT28C16 chip on hand. Resume Phase 80 (re-run `/gsd-execute-phase 80`) once (a) the adapter is built per `firestarter/doc/AT28C04-ADAPTER.md` and DMM-continuity-verified (esp. /WE chip-pin-21 → socket-pin-30, with the 21→21 short absent), and (b) an AT28C04 or AT28C16 chip is on hand and the Leonardo is connected.*

## Threat Model Disposition

- **T-80-WIRE** (Tampering — adapter wiring, esp. /WE chip-pin-21 → socket-pin-30): **deferred, not exposed** — no adapter is built, so the mis-wire risk does not exist yet; the DMM continuity check (the mitigation) is deferred with the build to the resume.
- **T-80-NOFUNC** (DoS / non-function via mis-wire): **N/A** — 0x0D is VPP-free; with no adapter and no chip there is no write path and no hazard. The lowest hazard class in v1.14 regardless.

## Self-Check: PASSED

The plan's job was to evaluate the gating hardware step and record the verdict + (deferral) decision — it did. A NOT-CLEARED verdict with a clean deferral is an explicitly authorized terminal outcome of this plan (the plan's own `<action>` defines this branch). Zero source/DB/constants changed, the chips remain honestly `adapter-required`, and FUT-04 captures the resume conditions.

## Phase Status

**Phase 80 HALTS after Plan 01.** Plans 80-02 (RED graduation tests), 80-03 (GREEN delete-arm + DB regen), and 80-04 (Leonardo bench proof) cannot execute on a NOT-CLEARED gate. Resume the phase only after the operator builds + DMM-verifies the DIP24→DIP32 adapter and has an AT28C04/AT28C16 chip on hand (FUT-04).
