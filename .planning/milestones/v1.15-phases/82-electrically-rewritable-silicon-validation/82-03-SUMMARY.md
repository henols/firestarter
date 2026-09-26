---
phase: 82-electrically-rewritable-silicon-validation
plan: 03
status: complete
completed: 2026-06-24
requirements: [REWR-04, DB-01]
verdict: W29C020 PASS (auto-erase proven) / W29C040 FAIL (genuine flash4 page-write)
deviation: board firmware reflashed 3.0.0b8 → 3.0.0b10 (operator-authorized; no firmware SOURCE change)
---

# 82-03 SUMMARY — flash4 A→B Bench Validation (W29C040, W29C020)

## Outcome

Bench-attempted REWR-04 (the two 0x05 flash4 Winbond chips) via A→B rewrite on Leonardo + Rev 2.0.
**W29C020 PASS / W29C040 FAIL (genuine, flash4 page-write)** — the opposite of the plan's expectation.
REWR-04 SC#3 (auto-erase confirmed for the `Flash/EEPROM` electrical type) **IS met**, via W29C020's
clean A→B (the first silicon proof of the FLAG_CAN_ERASE Flash/EEPROM branch). W29C040 fails a
mid-page poll at the 256B page-0 boundary — a distinct flash4 write-path fault handed to Phase 84.

## Per-chip results

| Chip | Size | Verdict | Detail |
|------|------|---------|--------|
| W29C040 | 512KB | **FAIL (genuine, flash4 page-write)** | write A (-b) times out verifying byte @0x0000ff (256B page-0 boundary), byte stays 0x00 (page not auto-erased/programmed). DETERMINISTIC across initial + 1 reseat. Per-page auto-erase NOT confirmed for this chip. |
| W29C020 | 256KB | **PASS** | A→B auto-erase proven: write B over A (no explicit erase) → clean verify B. consistency N=3 == image B; neg-control RC=1. The CR-01 page-size risk did NOT manifest on b10. |

## Requirements

- **REWR-04**: W29C020 PASS (A→B auto-erase proven — REWR-04 SC#3 / FLAG_CAN_ERASE Flash/EEPROM branch confirmed on silicon). W29C040 FAIL (genuine flash4 page-write) recorded + sweep continued. The milestone's "Flash/EEPROM auto-erase on real silicon" claim is met by W29C020; W29C040's distinct fault → Phase 84.
- **DB-01**: both chips' decode (DIP32 / Flash/EEPROM / 12V / 0x05; sizes 524288 / 262144) confirmed vs silicon via `firestarter info`; failures are write-path, not decode. No inline DB edit.

## KEY DEVIATION — firmware reflash b8 → b10

The board arrived on **3.0.0b8**, which predates the Phase-74 flash4 W29C040 SDP/256B-page fix.
On b8, W29C040 write failed immediately at the pre-write blank-check (`Not blank @0x0 v:0x00`) and the
standalone erase was a 0.06s no-op. **Operator authorized flashing the board to 3.0.0b10** (the v1.13
release with the Phase-74 fix) via `firestarter fw --install --firmware-version 3.0.0b10`. This is a
**board-state change only — no firmware SOURCE was modified** (D-01 "no firmware change in this phase"
is honored at the code level; the firestarter submodule stayed untouched on `beta`). Calibration
persisted across the reflash (R1=270000/R2=44000); port stayed /dev/ttyACM0.

**Consequence for the bench baseline:** Phase 81 + Plan 82-02 ran on b8; Plan 82-03 ran on b10. The
b8→b10 delta is recorded so later phases know the flash4 results are b10-specific. All subsequent bench
work in this session is on b10.

## CRITICAL FINDING for Phase 84 (reopens Phase-74 Wave-2)

W29C040 is the **first real-silicon test of the Phase-74 W29C040 SDP/256B-page fix** — Phase-74 Wave-2
(the W29C040 hardware re-bench) was DEFERRED, so that fix was only ever native-test-verified. On b10
silicon it **FAILS** at the 256B page boundary (mid-page-poll timeout). Meanwhile W29C020 (256KB,
same flash4 family, the supposedly CR-01-affected one) PASSES cleanly. This inverts the Phase-74/CR-01
expectation and is the headline Phase-84 FIX-01 item: the flash4 page-write/poll is wrong for the
512KB W29C040 geometry, not (or not only) the 256KB W29C020.

## SAFE-01 (flash4 session)

- `controller:` = leonardo / /dev/ttyACM0 (re-verified, no replug); **operator-re-confirmed silkscreen Rev 2.0**.
- Calibration R1=270000/R2=44000 (persisted across reflash). SAFE-02 green (unchanged).
- Recorded in EVIDENCE.md "Phase 82 SAFE-01 Gate — Plan 82-03 flash4 write session".

## Notes / deferrals for Phase 84

- **W29C040 flash4 page-write fault** (mid-page poll @0xff, 512KB) → Phase 84 FIX-01 / reopen Phase-74 Wave-2 (dual-repo lockstep firmware fix likely).
- **flash4 has no working bulk-erase**: standalone `erase` is a 0.06s no-op on both b8 and b10 (chips stay non-blank); the real mechanism is per-page auto-erase during `write -b`. `dev write-cycle` blank-checks before write so it cannot drive flash4 — used direct `write -b` (same as FM1608). Tooling observation for Phase 84.
- No firmware SOURCE change; no inline chip_database.json edit; phase stayed host-only at the code level.

## Artifacts

- `.planning/v1.15/bench/EVIDENCE.md` — 2 flash4 A→B rows (W29C040 FAIL, W29C020 PASS) + flash4 SAFE-01 session block.
- `.planning/v1.15/bench/EVIDENCE.json` — 2 appended write cells (19 total: 11 Phase 81 read + 8 Phase 82 write); all Phase 81 cells preserved.

## Commits (meta repo, gsd/v1.15-bench-validation-of-operator-inventory)

- `daf7e8e` test(82-03): REWR-04 flash4 A→B — W29C020 PASS, W29C040 FAIL; fw b8→b10

## Self-Check: PASSED
- [x] Both flash4 chips exercised on Leonardo + Rev 2.0 (b10), operator-seated
- [x] W29C020 PASS is non-vacuous (consistency-check N=3 + negative-control RC=1) — REWR-04 SC#3 confirmed
- [x] W29C040 FAIL reseat+retried per D-08; deterministic; recorded + sweep continued
- [x] EVIDENCE.{md,json} updated; Phase 81's 11 read cells preserved (19 cells = 11 read + 8 write)
- [x] DB-01 decode confirmed for both; no inline DB edit
- [x] Firmware reflash b8→b10 documented as a deviation; no firmware SOURCE change (D-01 honored at code level)
- [x] W29C040 finding flagged for Phase 84 / Phase-74 Wave-2 reopen
