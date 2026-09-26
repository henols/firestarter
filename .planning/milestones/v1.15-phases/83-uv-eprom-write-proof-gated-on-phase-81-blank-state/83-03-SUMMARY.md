---
phase: 83-uv-eprom-write-proof-gated-on-phase-81-blank-state
plan: 03
subsystem: bench-evidence / uv-eprom-write-proof / requirements-tracker
tags: [uv-eprom, write-proof, am27c020, bench, leonardo, anomaly, grad-03, phase-84-handoff, operator-gated]
requires:
  - "Plan 83-02 (ST M27C512 row recorded)"
  - "Plan 83-01 AM27C020 256KB all-0x00 image + SHA oracle"
  - "Phase 81 AM27C020 NOT-BLANK blank-state (data 0x02@0x0000)"
  - "Leonardo + RURP Rev 2.0, r1=270000, JP4 closed for 32-pin (SAFE-01 / D-09)"
provides:
  - "AM27C020 UV write path bench-tested → ANOMALY recorded (0x08 write/VPP path, 0 bits programmed; flagged Phase 84 FIX-01)"
  - "EVIDENCE.{md,json} AM27C020 Phase 83 row/cell"
  - "GRAD-03 / SC#4 / FUT-03 → Phase 84 documented handoff (EVIDENCE + REQUIREMENTS + ROADMAP); D-08 PASS bar pre-recorded"
affects:
  - ".planning/v1.15/bench/EVIDENCE.md"
  - ".planning/v1.15/bench/EVIDENCE.json"
  - ".planning/REQUIREMENTS.md"
  - ".planning/ROADMAP.md"
tech-stack:
  added: []
  patterns:
    - "Operator-gated irreversible spend authorization before any VPP (UV-01 → UV-02)"
    - "D-14 write-failure disposition: retry budget exhausted → ANOMALY + CONTINUE (phase not halted)"
    - "Documented requirement reassignment (GRAD-03/FUT-03 → Phase 84) instead of silent drop"
key-files:
  created:
    - "/tmp/firestarter_bench_p83/zeros16.bin (out-of-repo, 16B all-0x00 payload)"
  modified:
    - ".planning/v1.15/bench/EVIDENCE.md"
    - ".planning/v1.15/bench/EVIDENCE.json"
    - ".planning/REQUIREMENTS.md"
    - ".planning/ROADMAP.md"
decisions:
  - "Operator-directed DEVIATION from D-06 (full all-0x00 wipe): minimal 16-byte 0x00 partial-spend"
  - "AM27C020 write failure classified ANOMALY (operator decision): 0 bits programmed + chip reads clean = 0x08 write/VPP-path issue, NOT silicon wear; flag Phase 84 FIX-01"
  - "JP4 (32-pin) confirmed closed by operator mid-session; did not change the failure (still deterministic)"
  - "GRAD-03/SC#4/FUT-03 reassigned Phase 83 → Phase 84 per CONTEXT D-01 (2516 read path unstable, irreplaceable part)"
metrics:
  completed: "2026-06-24"
  tasks: 3
  files_changed: 4
---

# Phase 83 Plan 03: AM27C020 UV Write Proof + GRAD-03 Phase-84 Handoff Summary

**One-liner:** Bench-tested the AM27C020 (0x08, NOT-BLANK, DIP32) write path on Leonardo + Rev 2.0. After re-confirming NOT-BLANK non-destructively and obtaining operator spend authorization (a minimal 16-byte 0x00 partial-spend, deviation from D-06), the `write` deterministically failed — `bad bytes 15/16`, **zero bits programmed**, chip data intact — across the initial attempt + 2 retries (incl. operator closing JP4), plus a mild intermittent read glitch. Operator classified it **ANOMALY** (0x08 write/VPP path on this bench, not silicon wear), flagged Phase 84 FIX-01, phase not halted (D-14). Then recorded the GRAD-03 / 2516 → Phase 84 handoff across EVIDENCE + REQUIREMENTS + ROADMAP.

## What Was Built

### Task 1 — SAFE-01 bench gate + UV-01/UV-02 spend authorization (AM27C020)
- Board re-verified after chip swap: `controller: leonardo on /dev/ttyACM0`, fw 3.0.0b10; `R1: 270000`; operator confirmed silkscreen **Rev 2.0**.
- **UV-01 NOT-BLANK re-confirm (no VPP):** `read AM27C020` → 262144 B, SHA `08b687a3…177ed496` == Phase 81; byte 0x02@0x0000; `blank AM27C020` RC=1 (not blank).
- **UV-02 spend gate:** operator authorized **SPEND**, scoped to a minimal 16-byte 0x00 partial write.

### Task 2 — AM27C020 write proof attempt + read oracle + negative control → ANOMALY
- **Write (VPP applied):** `write AM27C020 zeros16.bin -b -a 0x0000` → **RC=1**, `bad bytes 15/16, retries 20` at 0x000000.
- **D-14 disposition:** idempotent retry (RC=1, read-back unchanged) → operator closed **JP4** (32-pin) → retry (RC=1, identical). Retry budget exhausted; deterministic; **0 bits programmed** (chip silicon intact).
- **N=3 read oracle:** 2 of 3 reads byte-identical (`08b687a3…`); 3rd read a localized 12-byte glitch reading `0x00` at 0x008004–0x00800f (`90cd45f5…`) → 2 distinct SHAs.
- **Negative control:** wrong-file `verify -a 0x0000` → RC=1 (`0x00 != 0x02 @0x000000`, confirms no programming).
- **UV-04 decode vs silicon:** `info AM27C020` → UV-EPROM / VPP 13.0V / 0x40000 (262144) / chip-id 0x197 / protocol 0x08 / DIP32.
- **Verdict (operator decision): ANOMALY** — 0x08 (32-pin Large EPROM) write/VPP path on this bench (the 0x07 28-pin part wrote clean the same session), not chip wear. Flagged Phase 84 FIX-01. EVIDENCE.{md,json} row 2 recorded.

### Task 3 — GRAD-03 / 2516 → Phase 84 handoff + tracker update (autonomous)
- **EVIDENCE.{md,json}:** explicit "GRAD-03 / 2516 → Phase 84" record (deferral rationale = Phase 81 0x0B read instability; D-08 PASS bar pre-recorded); plus an AM27C020-ANOMALY → Phase 84 FIX-01 handoff note. EVIDENCE.json gained `phase83_grad03`.
- **REQUIREMENTS.md:** GRAD-03 + FUT-03 rows reassigned Phase 83 → Phase 84 with rationale; UV-01/02/03/04 marked Complete with per-chip outcome notes.
- **ROADMAP.md:** 83-03 checkbox ticked; Phase 83 Outcome block (ST PASS / AM27C020 ANOMALY / GRAD-03·SC#4·FUT-03 → Phase 84); success criterion #4 marked DEFERRED → Phase 84.

## Verification Performed

| Check | Result |
|-------|--------|
| board re-verify (leonardo/ACM0, r1=270000, Rev 2.0) | ✓ |
| AM27C020 NOT-BLANK re-confirm (read SHA == Phase 81, blank RC=1, no VPP) | ✓ |
| write 16 B 0x00 @0x0000 (initial + 2 retries, JP4 closed) | RC=1, 0 bits programmed (deterministic) |
| N=3 read | 2 distinct SHAs (intermittent 12-byte glitch) |
| negative control (wrong-file `verify -a`) | RC=1 |
| UV-04 decode (UV-EPROM/13V/262144/0x08/DIP32) | ✓ |
| Task 3 automated gate (grep GRAD-03 + Phase 84 + REQUIREMENTS + JSON valid) | ALL PASS |

## Deviations from Plan

**Rule 1 (operator-directed scope change) — DEVIATION from D-06 (full all-0x00 wipe).** Operator authorized a minimal 16-byte 0x00 partial-spend (matching the ST M27C512 partial-spend pattern) rather than wiping all 262144 bytes. Used `firestarter write -b` (skip blank-check — the chip is NOT-BLANK and UV cannot erase) instead of `dev write-cycle`.

**Bench finding (recorded, not root-caused inline per D-14):** the AM27C020 0x08 write path takes no programming on this bench — distinct from the chip's clean Phase 81 read and from the 0x07 part's clean write this session. Operator-classified ANOMALY; chip silicon intact (0 bits programmed); flagged Phase 84 FIX-01. JP4 (32-pin) was confirmed closed mid-session and did not change the result.

**DB-decode note:** plan text said "12V"; DB and silicon decode is **13V VPP** (UV-04). No DB edit.

## Known Stubs

None for Phase 83. The AM27C020 0x08 write/VPP-path issue and the 2516/0x0B read-path instability are both explicitly deferred to **Phase 84 FIX-01** (documented, not dropped). GRAD-03/SC#4/FUT-03 are Phase 84 deliverables.

## Threat Surface Notes

- **T-83-08 (wrong chip/image written irreversibly):** UV-01 NOT-BLANK re-confirm + UV-02 operator spend gate before any VPP; exact payload + SHA recorded; the write failed safely (0 bits programmed, chip intact).
- **T-83-09 (vacuous PASS):** board locked to Leonardo + Rev 2.0 (r1=270000); EVID-03 bar applied (N=3 read + neg-control RC=1) — surfaced the read instability honestly rather than masking it.
- **T-83-10 (over-voltage):** standard 0x08 13V VPP path; over-voltage stayed blocked.
- **T-83-11 (2516):** no 2516 chip selected, seated, or written anywhere in Phase 83.

## Self-Check: PASSED

- EVIDENCE.md row 2 (ANOMALY) + GRAD-03/AM27C020 Phase-84 notes present; EVIDENCE.json AM27C020 cell + `phase83_grad03` appended and validates.
- REQUIREMENTS.md GRAD-03/FUT-03 → Phase 84; UV-01..04 Complete with notes.
- ROADMAP.md 83-03 ticked + Outcome block added.
- Task 3 automated verify gate: ALL PASS.
