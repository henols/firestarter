---
phase: 91-12v-vpp-write-path-regression-rca
plan: 04
subsystem: ledger-disposition
tags: [ledger, disposition, bench-log, operator-checklist, ledger-02, w27c512-deferred]
requires:
  - phase: 91-03
    provides: FIX-91 confirmation (SST39SF040 PASS) + root cause (write -b skips erase)
provides:
  - 0x06 SST39SF040 PROTOCOL-LEDGER row graduated to PASS (LEDGER-02 for 0x06)
  - 0x07 W27C512 row set bench-pending with RCA attribution + operator-checklist pointer
  - check_ledger.py RC=0 (+ its own test suite 5/5)
  - BENCH-LOG.md Phase 91 A/B + Fix Results section
  - W27C512-OPERATOR-CHECKLIST.md (turnkey, corrected to the true root cause)
  - 91-RCA.md Phase 91 Wrap-Up
affects: [v1.16-milestone-disposition, ledger-02, w27c512-operator-bench]
key-files:
  created:
    - .planning/v1.16/ledger/rca/W27C512-OPERATOR-CHECKLIST.md
  modified:
    - .planning/v1.16/ledger/PROTOCOL-LEDGER.json
    - .planning/v1.16/ledger/PROTOCOL-LEDGER.md
    - .planning/v1.16/ledger/bench/BENCH-LOG.md
    - .planning/v1.16/ledger/rca/91-RCA.md
key-decisions:
  - "0x06 SST39SF040 -> PASS: write-cycle now byte-identical to v1.15 via the erase-enabled plain write; p90_writecycle_sha_matches_v115 set true with a p91_note documenting the method correction; evidence bench/SST39SF040-fix/. Checker RC=0; D-04 no-raw-SHA honored (referenced by path)."
  - "0x07 W27C512 -> bench-pending (valid status; not auto-passed, D-03). RCA + fix known (same write -b skip-erase cause; use plain write); live re-bench DEFERRED to operator (chip swap)."
  - "No checker edit needed (PASS + bench-pending are existing valid statuses); avoided touching the checker test suite."
  - "W27C512 operator checklist REWRITTEN to the true root cause: use plain `firestarter write` (erase), NOT `write -b`; do not 'fix' by adding -b."
requirements-completed: [FIX-91 (disposition + checklist); LEDGER-02 satisfied for 0x06]
duration: ~15min
completed: 2026-06-26
---

# Phase 91 Plan 04: Ledger Disposition + W27C512 Checklist — Summary

**0x06 SST39SF040 graduated to PASS (LEDGER-02 satisfied for 0x06); 0x07 W27C512 carried as
bench-pending with the RCA attribution and a turnkey operator checklist; check_ledger.py RC=0;
BENCH-LOG + RCA wrap-up complete. W27C512 live bench is the sole operator-deferred item.**

## Accomplishments
- **PROTOCOL-LEDGER.{json,md} (lockstep):** 0x06 → **PASS** (oracle leonardo+Rev2.0, evidence
  `bench/SST39SF040-fix/`, p91 provenance note); 0x07 → **bench-pending** (RCA done; operator bench
  deferred; pointer to checklist). `check_ledger.py` RC=0; its own pytest suite 5/5; D-04 holds
  (no raw 64-hex SHA in the ledger).
- **BENCH-LOG.md:** appended "## Phase 91 A/B + Fix Results" (forensic, A/B, fix, disposition) —
  Phase-90 history not rewritten.
- **W27C512-OPERATOR-CHECKLIST.md:** turnkey single-session procedure, **corrected to the true root
  cause** — use plain `firestarter write` (erase), not `write -b`; PASS gate SHA `e16b2a5b…`.
- **91-RCA.md:** Phase 91 Wrap-Up (RCA-91 + FIX-91 + 0x07 deferral + LEDGER-02 status + hardening
  recommendation).

## Verification
- `python3 .planning/v1.16/ledger/tools/check_ledger.py` RC=0 ✓ ; pytest 5/5 ✓
- `grep "Phase 91" BENCH-LOG.md` ✓ ; checklist contains gate SHA e16b2a5b… ✓ ; RCA has Wrap-Up ✓
- 0x06 row PASS with evidence refs; 0x07 bench-pending; JSON/MD lockstep ✓

## Deviations
- 0x07 status = `bench-pending` (not the plan's tentative "carried-pending-operator") — bench-pending
  is an existing valid checker status and accurately means "awaiting operator bench"; avoided a
  checker edit + its test-suite risk.

## Task 3 (checkpoint:human-action) — DEFERRED (operator-only)
W27C512 live bench re-validation requires a chip swap. It stays OPEN/deferred and does NOT block the
SST39SF040 (0x06) deliverable. Resolve via `rca/W27C512-OPERATOR-CHECKLIST.md` on operator return.

## Self-Check: PASSED
Ledger honestly dispositioned (checker RC=0), BENCH-LOG + checklist + wrap-up done; W27C512 live
bench is the sole deferred item.
