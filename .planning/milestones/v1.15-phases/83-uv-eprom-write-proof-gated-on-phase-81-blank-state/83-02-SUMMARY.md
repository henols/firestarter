---
phase: 83-uv-eprom-write-proof-gated-on-phase-81-blank-state
plan: 02
subsystem: bench-evidence / uv-eprom-write-proof
tags: [uv-eprom, write-proof, st-m27c512, bench, leonardo, partial-spend, operator-gated]
requires:
  - "Plan 83-01 SAFE-02 gate green + ST M27C512 64KB image + SHA oracle"
  - "Phase 81 ST M27C512 BLANK blank-state (all-0xFF, N=3 byte-identical)"
  - "Leonardo + RURP Rev 2.0, r1=270000 (SAFE-01 / D-09 board lock)"
provides:
  - "ST M27C512 UV write-path PROVEN on silicon (partial 16-byte spend, read-back identical, N=3 stable, neg-control RC=1)"
  - "EVIDENCE.{md,json} ST M27C512 Phase 83 row/cell (PASS)"
  - "UV-04 DB-decode confirmation vs silicon (UV-EPROM / 13V / 65536 / 0x07)"
affects:
  - ".planning/v1.15/bench/EVIDENCE.md"
  - ".planning/v1.15/bench/EVIDENCE.json"
tech-stack:
  added: []
  patterns:
    - "Operator-gated irreversible spend authorization before any VPP (UV-01 → UV-02)"
    - "Partial-spend write proof: write -a + verify -a + N=3 read + wrong-file neg-control (non-vacuous EVID-03)"
    - "Board lock + live r1 readback to keep the verify read trustworthy"
key-files:
  created:
    - "/tmp/firestarter_bench_p83/ST_partial16.bin (out-of-repo, /tmp — 16-byte payload)"
  modified:
    - ".planning/v1.15/bench/EVIDENCE.md"
    - ".planning/v1.15/bench/EVIDENCE.json"
decisions:
  - "CLI name reconciliation: DB entry is `M27C512` (ST/SGS-THOMSON 0x203D); 'ST M27C512' is a human label and does NOT resolve as a CLI arg"
  - "Operator-directed DEVIATION from D-05 (full-image): minimal 16-byte partial-spend so the part stays mostly blank/reusable; non-vacuous proof assembled from write/verify/read/neg-control instead of `dev write-cycle`"
  - "DB VPP for this chip is 13V (UV-04 confirmed), not the plan's stated 12V — recorded, no DB edit"
metrics:
  completed: "2026-06-24"
  tasks: 2
  files_changed: 2
---

# Phase 83 Plan 02: ST M27C512 UV-EPROM Write Proof Summary

**One-liner:** Bench-proved the WRITE PATH of the read-stable BLANK UV-EPROM ST M27C512 on Leonardo + Rev 2.0. After re-confirming the BLANK state non-destructively (no VPP) and obtaining the operator's irreversible spend authorization, executed an operator-directed **minimal 16-byte partial-spend** (deviation from the plan's D-05 full-image): write 16 B @0x0000 (RC=0), `verify -a` of those bytes (RC=0), full-chip read-back showing first 16 B = payload / rest 0xFF, N=3 byte-identical reads (1 distinct SHA), and a wrong-file negative control (RC=1). Verdict **PASS**; the part remains mostly blank/reusable.

## What Was Built

### Task 1 — SAFE-01 bench gate + UV-01/UV-02 spend authorization
- **Board identity (D-09):** `firestarter fw` → `controller: leonardo on /dev/ttyACM0`, firmware 3.0.0b10.
- **Shield rev:** operator confirmed silkscreen **Rev 2.0** (EEPROM byte reports "Rev 2.0-class"; operator statement authoritative).
- **Calibration:** `firestarter config` → **R1: 270000** live readback (not the 1000 default) — VPP read trustworthy.
- **UV-01 blank-state re-confirm (no VPP):** `read M27C512` → 65536 B, SHA `71189f7f…48da9063` == the Phase 81 recorded BLANK SHA; all-0xFF (1 distinct byte); dedicated `blank M27C512` RC=0.
- **UV-02 spend gate:** operator authorized **SPEND**, scoped to a minimal ~16-byte partial write (see deviation).

### Task 2 — ST M27C512 write proof + read oracle + negative control
- **Write (VPP applied):** `write M27C512 ST_partial16.bin -a 0x0000` → RC=0 (blank-check passed full chip, then wrote 16 B). Payload = first 16 B of the seed=1 image (`4420823cfde6f1c26b30f90ec7dd01e4`, SHA `f705354e…873897a`).
- **Verify written region:** `verify M27C512 ST_partial16.bin -a 0x0000` → RC=0 — write path proven (read-back identical to payload).
- **Negative control:** wrong-file (`0x00`×16) `verify -a 0x0000` → RC=1 (`0x00 != 0x44 @0x000000`).
- **Read oracle (EVID-03 non-vacuous bar):** 3 full-chip reads → **1 distinct SHA** `008948af…ec397c3f`; structure confirmed: first 16 B == payload, remaining 65520 B = 0xFF.
- **UV-04 decode vs silicon:** `firestarter info M27C512` → UV-EPROM / **VPP 13.0V** / size 0x10000 (65536) / chip-id 0x203D / protocol 0x07.
- **EVIDENCE row/cell** appended to both EVIDENCE.md (row 1) and EVIDENCE.json (phase83 descriptor + ST M27C512 cell, valid JSON), verdict **PASS**.

## Verification Performed

| Check | Result |
|-------|--------|
| controller: leonardo on /dev/ttyACM0 | ✓ |
| silkscreen Rev 2.0 (operator) + r1=270000 readback | ✓ |
| BLANK re-confirm (read SHA == Phase 81, blank RC=0, no VPP) | ✓ |
| write 16 B @0x0000 | RC=0 |
| verify written 16 B (`verify -a`) | RC=0 |
| negative control (wrong-file `verify -a`) | RC=1 |
| N=3 read consistency | 1 distinct SHA (`008948af…`) |
| post-write structure (first16=payload, rest 0xFF) | ✓ |
| UV-04 decode (UV-EPROM/13V/65536/0x07) | ✓ |

## Deviations from Plan

**Rule 1 (operator-directed scope change) — DEVIATION from D-05.** The plan specified a full 64KB deterministic image written via `dev write-cycle` (read-back SHA == image SHA). At the UV-02 spend gate the operator instead authorized a **minimal ~16-byte partial-spend** ("only write a small portion to the prom like 16 bytes"), so the part stays mostly blank and reusable. Honored as a SPEND (partial). Because `dev write-cycle` is full-image-and-full-SHA only, the equivalent **non-vacuous** proof was assembled from the lower-level commands: `write -a` + `verify -a` (proves the written region read-back-identical) + N=3 full-chip read (1 distinct SHA = stable) + wrong-file `verify -a` negative control (RC=1). This still exercises the write/VPP path and the trusted-read oracle; it exercises fewer address lines / bit patterns than the full image, which is the intended trade for preserving the chip. Recorded explicitly in the EVIDENCE row.

**Naming reconciliation (not a behavior deviation):** "ST M27C512" (plan/EVIDENCE human label) does not resolve as a CLI arg; the DB entry is `M27C512` (ST/SGS-THOMSON, chip-id 0x203D — same silicon). All bench commands used `M27C512`.

**DB-decode note:** the plan text stated "12V" for this chip; the DB and silicon decode is **13V VPP** (UV-04 confirmed). No DB edit — recorded as an observation.

## Known Stubs

None. The AM27C020 row (#2) and the GRAD-03/2516 → Phase 84 handoff remain for Plan 83-03.

## Threat Surface Notes

- **T-83-04 (wrong chip/image written irreversibly):** UV-01 BLANK re-confirm + UV-02 explicit operator spend gate before any VPP; exact payload + SHA recorded; `verify -a` asserts read-back == payload.
- **T-83-05 (vacuous PASS):** board locked to Leonardo + Rev 2.0 with r1=270000 readback; EVID-03 non-vacuous bar = N=3 byte-identical + negative control RC=1.
- **T-83-06 (over-voltage):** standard 0x07 13V VPP path (no VPE rail); over-voltage stayed blocked.
- **T-83-07 (2516):** no 2516 chip seated or selected anywhere in this plan.

## Self-Check: PASSED

- EVIDENCE.md row 1 populated (PASS); EVIDENCE.json phase83 cell appended and validates as JSON.
- Bench commands all returned the expected RCs (write 0, verify 0, neg-control 1, N=3 → 1 SHA).
- Operator spend authorization captured before any VPP was applied.
