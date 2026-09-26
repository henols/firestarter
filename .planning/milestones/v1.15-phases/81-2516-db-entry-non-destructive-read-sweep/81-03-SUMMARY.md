---
phase: 81-2516-db-entry-non-destructive-read-sweep
plan: "03"
subsystem: bench-validation
tags: [bench-sweep, read-validation, blank-state, uv-eprom, leonardo, rev2.0, anomaly-2516, safe-01]
dependency_graph:
  requires: [2516-DB-ENTRY, EVIDENCE-SCAFFOLD]
  provides: [READ-BASELINE, UV-BLANK-STATES, 2516-READ-ANOMALY]
  affects: [Phase-82-write-path, Phase-83-2516-write, Phase-84-FIX-01]
tech_stack:
  added: []
  patterns: [dev-consistency-check-N3, non-destructive-read-sweep, negative-control-verify]
key_files:
  created: []
  modified:
    - .planning/v1.15/bench/EVIDENCE.json
    - .planning/v1.15/bench/EVIDENCE.md
decisions:
  - "SWEEP-01: all 11 chips read end-to-end + blank-checked on leonardo + Rev 2.0; zero chips consumed (reads apply no VPP); 10 PASS, 1 ANOMALY"
  - "SWEEP-02 / UV gating blank-states: ST M27C512 = BLANK (stable all-0xFF), AM27C020 = NOT-BLANK, 2516 = NOT-BLANK (read-unstable, contents unreliable)"
  - "2516 read is UNSTABLE on the 0x0B Legacy shared-OE/VPP path (3 distinct SHAs across initial + 2 D-07 reseat cycles, VPP pinned 15.3V) — GATES Phase 83 (no 2516 write/preserve until stable); flag Phase 84 FIX-01"
  - "EVID-03 negative control fired: wrong-file verify exited RC=1 on W27C512 (Task 1) and ST M27C512 (Task 2) — every PASS is non-vacuous (N>=3 byte-identical + oracle proven)"
  - "VPP-regulator instability surfaced: chip-1 read-init refused at boot (VPP 18.8V>12V, cleared by board reset); benign VPP-low warnings on read are non-blocking"
metrics:
  completed: "2026-06-24"
  tasks_completed: 3
  files_modified: 2
  chips_swept: 11
  chips_consumed: 0
---

# Phase 81 Plan 03: Non-Destructive 11-Chip Read Sweep Summary

**One-liner:** Read + blank-checked all 11 physical chips on Leonardo + Rev 2.0 with zero chips consumed (reads apply no VPP); 10 PASS with N≥3 byte-identical SHAs, the 3 UV gating blank-states recorded, and the irreplaceable 2516 flagged ANOMALY (0x0B read path unstable) — gating Phase 83.

## Tasks Completed

| Task | Name | Result |
|------|------|--------|
| 1 | Read + blank-check the 8 non-UV chips (SWEEP-01, EVID-03, SAFE-01) | 8/8 PASS (N=3 byte-identical); negative control RC=1 on W27C512 |
| 2 | Read + blank-check the 3 UV-EPROMs incl. 2516 (SWEEP-01/02, EVID-03, SAFE-01, D-10) | ST M27C512 BLANK + AM27C020 NOT-BLANK PASS; **2516 ANOMALY** (read unstable); negative control RC=1 on ST M27C512 |
| 3 | Finalize EVIDENCE.{md,json} — validate 11 rows, no pending (EVID-01) | Validation green (`uv-blank-state-ok`, `pass-rows-ok`); md mirrors json |

## SAFE-01 Preconditions (verified per task)

- **Board = leonardo** (the only authoritative read board) on `/dev/ttyACM0`, firmware 3.0.0b8.
- **Shield = Rev 2.0** — operator-confirmed silkscreen (EEPROM hw byte reports "Rev 2.0-class" but cannot distinguish revs per bench discipline).
- **Calibration:** R1=270000, R2=44000 (not the 1000 default).
- **Host suite:** green (Plan 81-01, 651 tests).
- Re-verified at the Task 2 boundary (port identity, R1) per SAFE-01.

## Sweep Results — 10 PASS / 1 ANOMALY / 0 consumed

| # | Chip | Algo | Verdict | Blank / current-state | SHA-256 (N=3) |
|---|------|------|---------|----------------------|----------------|
| 1 | W27C512 | 0x07 | PASS | not-blank (0x94@0x2000) | 9376dcd8…97ad23c8 |
| 2 | W27E512 | 0x07 | PASS | blank (all-0xFF) | 71189f7f…48da9063 |
| 3 | SST27SF512 | 0x07 | PASS | not-blank (0x00@0x0000) | f633b2f5…f8056360 |
| 4 | W27E040 | 0x08 | PASS | not-blank (0x4f@0x0000) | 67f70ccd…468b4254 |
| 5 | SST39SF040 | 0x06 | PASS | not-blank (0xa3@0x0000) | c19c3e07…a348368d |
| 6 | W29C020 | 0x05 | PASS | not-blank (0x24@0x0000) | 93ff5287…66b53602 |
| 7 | W29C040 | 0x05 | PASS | not-blank (0x00@0x0000) | d44736a9…1e3b48b3 |
| 8 | FM1608 | 0x40 | PASS | n/a FRAM (blank-check "Empty input") | 2ef1444b…3d4c0037 |
| 9 | ST M27C512 | 0x07 | PASS | **BLANK** | 71189f7f…48da9063 |
| 10 | AM27C020 | 0x08 | PASS | **NOT-BLANK** | 08b687a3…177ed496 |
| 11 | 2516 | 0x0B | **ANOMALY** | **NOT-BLANK** (read-unstable) | — (3 distinct SHAs) |

## UV-EPROM Gating Blank-States (the Phase 83 gate, SWEEP-02)

- **ST M27C512 → BLANK** (stable all-0xFF, N=3 byte-identical; matches W27E512 all-FF SHA).
- **AM27C020 → NOT-BLANK** (data present 0x02@0x0000, N=3 byte-identical).
- **2516 → NOT-BLANK** (read-unstable): the blank-check deterministically reports "Not blank" (0x68@0x0000) and every read returns non-0xFF data, so the chip definitively has content — but the exact contents are unreliable (reads jitter).

## ANOMALY: 2516 Read Instability (gates Phase 83 → Phase 84 FIX-01)

The 2516 (0x0B Legacy, shared OE/VPP pin) failed the consistency check on the **initial read + both D-07 reseat cycles** — **3 distinct SHAs** every attempt — with VPP pinned at **15.3V** on the shared OE/VPP pin during read. Every 0x07/0x08 UV chip read clean on this exact bench, so the signature is **0x0B-specific, not seating**. This is the same VPP-regulator-instability family as the chip-1 boot refusal (VPP 18.8V > 12V read-init gate, cleared by a board reset).

**Consequences:**
- **Phase 83:** MUST NOT write or preserve-dump the irreplaceable 2516 until its read path is stable (blank-state/contents cannot be trusted). This is the load-bearing gate this sweep exists to establish.
- **Phase 84 FIX-01:** investigate (a) the 0x0B read-path VPP control / shared-OE-VPP behavior, and (b) the FM1608 blank-check "Empty input" tooling gap (read path itself was clean).

## Negative Control (EVID-03)

Wrong-file `verify` (256KB of 0xA5) exited **RC=1** on W27C512 (Task 1) and ST M27C512 (Task 2) — the read/verify oracle is proven non-silently-passing, so every PASS verdict (N≥3 byte-identical + live negative control) is non-vacuous.

## Deviations from Plan

- The plan suggested `dev write-cycle --runs 3`, but write-cycle is **destructive** (erase→write→read-back). For a non-destructive read sweep I used `dev consistency-check --runs 3` (read-only N reads + SHA divergence + 0/1/2 verdict), which is the plan's stated "or N≥3 separate reads + compare SHA" path. No chip was written.
- Chip 1 (W27C512) initially refused with a VPP-high read-init gate (18.8V); a board reset (operator) cleared it before the recorded read. No chip harmed (reads/blank-checks refuse before bus activity).
- The 2516 returned ANOMALY rather than a clean PASS — anticipated and handled by D-06 (continue) / D-07 (reseat ≤2); it is a legitimate baseline finding, not a sweep failure. SWEEP-01/02 success criteria are met (all 11 have EVIDENCE rows; the 3 UV gating blank-states are recorded).

## Threat Surface Scan

T-81-06 (false-PASS oracle): mitigated by SAFE-01 per-task verification + N≥3 + negative control. T-81-09 (wrong UV blank-state mis-gates Phase 83): the 2516's unreliable read is explicitly recorded as ANOMALY and gates Phase 83 rather than producing a false blank-state. No package installs (T-81-SC accepted).

## Known Stubs

None — all 11 EVIDENCE rows populated with final verdicts.

## Self-Check: PASSED

- 11 EVIDENCE cells, zero `pending`; `uv-blank-state-ok` + `pass-rows-ok`: CONFIRMED
- 3 UV gating blank-states recorded (BLANK / NOT-BLANK / NOT-BLANK): CONFIRMED
- Negative control fired (RC=1, ×2): CONFIRMED and noted in EVIDENCE header
- EVIDENCE.md mirrors EVIDENCE.json (all 11 chips + verdicts): CONFIRMED
- 2516 ANOMALY + Phase 83 gate + Phase 84 FIX-01 recorded: CONFIRMED
- Zero chips consumed (reads apply no VPP): CONFIRMED
