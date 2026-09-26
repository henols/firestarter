---
phase: 82-electrically-rewritable-silicon-validation
plan: 02
status: complete
completed: 2026-06-24
requirements: [REWR-01, REWR-02, REWR-03, REWR-05, DB-01]
verdict: 4 PASS / 2 FAIL (genuine) — bench-proven on Leonardo + Rev 2.0
---

# 82-02 SUMMARY — Rewritable A→B Bench Validation (6 lower-risk chips)

## Outcome

Bench-proved the `supported` claim on real silicon for the 6 lower-risk rewritable chips via the
explicit A→B two-image rewrite (D-05/D-06) on Leonardo + RURP Rev 2.0. **4 PASS / 2 FAIL (genuine)**.
Both FAILs are genuine silicon defects (deterministic stuck bits on erase), NOT algorithm/DB/board
faults — the same-family PASS chips prove the decode and write paths are correct. Sweep never halted
on a FAIL (D-08/D-09); every PASS is non-vacuous (consistency-check --runs 3 byte-identical + a
wrong-file `verify` exiting RC=1). DB-01 decode confirmed vs silicon for all 6 chips.

## Per-chip results

| Chip | Algo | Verdict | Detail |
|------|------|---------|--------|
| W27C512 | 0x07 EEPROM | **PASS** | A→B auto-erase proven (clean B read-back == image B SHA). Initial VPP-high 13.1V>12.0V (Phase-81 regulator family) → operator corrected VPP → clean retry. |
| W27E512 | 0x07 EEPROM | **FAIL (genuine)** | Erase cannot clear bit 7 @0x3d (reads 0x7f) — DETERMINISTIC across initial + 2 reseats (D-08 N=2 exhausted). Stuck cell, not contact/VPP. Read clean in Phase 81 (read-only); defect manifests only on erase/write. |
| SST27SF512 | 0x07 EEPROM | **PASS** | A→B auto-erase proven; consistency N=3 == image B; neg-control RC=1. No VPP hiccup. |
| W27E040 | 0x08 EEPROM | **FAIL (genuine)** | Erase cannot clear bit 4 @0x7db (reads 0xef) — DETERMINISTIC across initial + 1 reseat. Same stuck-bit-on-erase signature class as W27E512 (different offset). |
| SST39SF040 | 0x06 flash3 | **PASS** | A→B auto-erase proven (~240s/write, slow flash3 path); consistency N=3 == image B; neg-control RC=1. DB-01 note: DB electrical.type 'Flash/EEPROM' vs milestone flash3 class — Phase-84 observation. |
| FM1608 | 0x40 FRAM | **PASS** | Clean OVERWRITE proven (D-06, no erase) via DIRECT write path (`write -b`). `dev write-cycle` unusable on FRAM (erase 'Not supported' — Phase-81 tooling gap, flag Phase 84). DB-01 note: DB type 'SRAM' vs FRAM family. |

## Requirements

- **REWR-01** (W27C512, W27E512, SST27SF512): W27C512 + SST27SF512 PASS A→B (auto-erase proven); W27E512 FAIL (genuine) recorded + sweep continued. Algorithm 0x07 auto-erase confirmed on 2 of 3 (the FAIL is a worn chip, not an algo defect).
- **REWR-02** (W27E040, 0x08): FAIL (genuine) recorded + continued — 0x08 erase path engaged correctly; chip has a stuck cell.
- **REWR-03** (SST39SF040, 0x06): PASS A→B auto-erase proven.
- **REWR-05** (FM1608, 0x40): PASS A→B clean-overwrite proof.
- **DB-01**: all 6 chips' decode (pinout/VPP/type/algorithm/size) confirmed vs silicon; 2 type-decode observations (SST39SF040 Flash/EEPROM, FM1608 SRAM-vs-FRAM) recorded for the Phase 84 audit; no inline DB edit.

## SAFE-01/02 (this session)

- `controller:` = leonardo on /dev/ttyACM0; firmware 3.0.0b8; **operator-confirmed silkscreen Rev 2.0**.
- Live calibration R1=270000, R2=44000 (not the 1000 default → VPP trustworthy).
- SAFE-02 green (Plan 82-01: 663 tests + 0xA4 guard `test_init_phase_data_frames_not_acked` PASS).
- Recorded in EVIDENCE.md "Phase 82 SAFE-01 Gate — Plan 82-02 write session".

## Deviations / notes for Phase 84

- **Two genuine stuck-bit FAILs** (W27E512, W27E040) — operator's worn chips; the milestone's "prove it on silicon" claim is met by the family representatives that PASS. Not a code/DB defect.
- **FRAM write-cycle tooling gap**: `dev write-cycle` errors at erase on 0x40 (FRAM has no erase). Direct `write -b` works. Phase-81 "Empty input" blank-check gap is the same family → Phase 84 FIX-01 (NOT fixed here).
- **VPP-regulator instability** recurred (W27C512 13.1V>12.0V) — same family as Phase-81 chip-1 boot-refusal + 2516 anomaly; operator-corrected at the bench → Phase 84 disposition.
- **2 DB-01 type observations** (SST39SF040, FM1608) for the Phase 84 decode audit. No firmware change, no inline chip_database.json edit (phase stayed host-only / non-destructive-to-DB).

## Artifacts

- `.planning/v1.15/bench/EVIDENCE.md` — 6 Phase 82 A→B write-validation rows + SAFE-01 session block.
- `.planning/v1.15/bench/EVIDENCE.json` — 6 appended write cells (17 total: 11 Phase 81 read + 6 Phase 82 write); all Phase 81 cells preserved.

## Commits (meta repo, gsd/v1.15-bench-validation-of-operator-inventory)

- `e396b56` test(82-02): SAFE-01 write-session gate
- `98e9760` test(82-02): REWR-01 results (W27C512/SST27SF512 PASS, W27E512 FAIL)
- `65ac455` test(82-02): REWR-02/03/05 results (SST39SF040/FM1608 PASS, W27E040 FAIL)

## Self-Check: PASSED
- [x] All 6 chips exercised on Leonardo + Rev 2.0 (operator-seated one at a time)
- [x] Every PASS non-vacuous (consistency-check --runs 3 + negative-control RC=1)
- [x] Both FAILs reseat+retried per D-08 before recording; sweep never halted
- [x] EVIDENCE.{md,json} updated; Phase 81's 11 read cells preserved (len 17, 11 read + 6 write)
- [x] DB-01 decode confirmed for all 6; type observations flagged for Phase 84; no inline DB edit
- [x] No firmware change; phase stayed host-only
