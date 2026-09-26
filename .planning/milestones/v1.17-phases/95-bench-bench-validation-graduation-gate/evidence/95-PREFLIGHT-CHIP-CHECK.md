---
artifact: 95-PREFLIGHT-CHIP-CHECK
phase: 95-bench-bench-validation-graduation-gate
recorded: 2026-06-29
recorder: orchestrator (bench, operator-authorized unattended)
---

# Phase 95 Pre-flight — Seated-Chip Boot-Block Check

Operator chose "seat a different (unlocked) W29C040" for the Phase 95 graduation path
(2026-06-27). This pre-flight checks whether the currently-seated chip is unlocked
BEFORE attempting the full byte-exact graduation (BENCH-01).

## Bench discipline
- Port: /dev/ttyACM0 · controller: Rev 2.0-class (Leonardo + RURP Rev 2.0)
- R1 = 270000, R2 = 44000 (live readback) — matches milestone lock
- Firmware: Phase-94 build (FIX-01a CANERASE + PGSZ + FIX-01b boot-block detect)

## Result: STILL LOCKED — graduation precondition NOT met

Page-0 write probe (64 B @ 0x0, normal `write -a 0 -b`, post-fix safe path):
```
firestarter -p /dev/ttyACM0 write W29C040 probe_page0.bin -a 0 -b
→ ERROR: boot block locked -- 0x00003f not programmable (W29C040 §6.6 irreversible lockout)
```
The seated chip is the SAME locked W29C040 (or another locked sample). The unlocked
chip has not yet been physically swapped in. **Phase 95 BENCH-01 cannot proceed until
an unlocked W29C040 is seated** (operator action).

## Bonus: Phase-94 FIX-01b CONFIRMED live on real silicon
This probe ALSO closes the one open item from Phase 94 Plan 04 ("boot-block detect
live-trigger not achieved — blank check fired first"). With `-b` (skip blank check),
the write reached page 0, hit the lock, and the firmware §6.6 detect fired the clean
`boot block locked` diagnostic (host MSG_ERR_FL4_BOOT_BLOCK_LOCKED 0xBC path) INSTEAD
of the old cryptic `Timeout verifying ...`. No 12V asserted (CANERASE fix holds).
FIX-01b end-to-end verified on hardware.

## Minor polish item (non-blocking)
The host diagnostic renders the section sign as "ss6.6" ("W29C040 ss6.6 irreversible
lockout") — the `§` likely got ASCII-mangled in the message string. Cosmetic; worth a
one-line fix when convenient.

## Next
Awaiting operator: seat an unlocked W29C040 (boot block NOT locked), then re-run — the
pre-flight page-0 probe must PASS (program+verify) before BENCH-01 graduation runs.
