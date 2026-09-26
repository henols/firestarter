---
phase: 91-12v-vpp-write-path-regression-rca
verified: 2026-06-26T18:00:00Z
status: passed
score: 3/3
overrides_applied: 0
---

# Phase 91: 12V-VPP Write-Path Regression RCA — Verification Report

**Phase Goal:** RCA the reproducible 0x06 SST39SF040 + 0x07 W27C512 write failures from Phase 90; drive the SST39SF040 to a WORKING write (operator's must-prove).
**Verified:** 2026-06-26
**Status:** passed
**Re-verification:** No — initial verification

---

## Goal Achievement

### Success Criteria (ROADMAP Contract)

| # | Criterion | Status | Evidence |
|---|-----------|--------|----------|
| SC-1 | Regression attributed via controlled A/B (recompose a296195 vs b10 a1953c2; host e46549f vs 98b3a92) — fw vs host isolated | MET | 91-RCA.md "Decision Gate": b10 fw a1953c2 and recompose a296195 fail **identically** (`0x1c != 0x04 at 0x000000`). Both legs documented in `bench/SST39SF040-ab/SHA256SUMS.txt`. Host axis ruled out: DB wire params byte-identical across 98b3a92↔e46549f; host write path (eprom_operations.py) zero-delta on flash3/EPROM. |
| SC-2 | Both symptoms explained (W27C512 bad-bytes-921-@0x0; SST39SF040 write-A-timeout + deterministically-wrong write-B); A P3-only explanation must not be claimed | MET | 91-RCA.md "Both Symptoms Explained": single axis = `write -b` sets `FLAG_SKIP_ERASE` → erase skipped on NOR/erase-required chips. SST39SF040 is 5V-only, uses P4/P7 never P3, never enables VPP regulator — explicitly rules out P3-only. W27C512 bad-bytes @0x0 = same mechanism (non-blank chip, erase skipped). P3-only explanation explicitly rejected in the RCA. |
| SC-3 | Fix (or accepted deferral) proposed; 0x06/0x07 PROTOCOL-LEDGER rows dispositioned | MET | 0x06 → **PASS** in PROTOCOL-LEDGER.{json,md}; 0x07 → **bench-pending** with attribution + W27C512-OPERATOR-CHECKLIST.md turnkey checklist. `check_ledger.py` exits RC=0. |

**Score:** 3/3 success criteria verified

---

## Observable Truths (Goal-Backward Derivation)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| T-1 | Controlled A/B performed: recompose a296195 vs b10 a1953c2 on SST39SF040 | VERIFIED | `bench/SST39SF040-ab/SHA256SUMS.txt` records both legs: recompose fail `0x1c != 0x04 @0x0`; b10 fail — byte-identical. Confirmed via file read. |
| T-2 | Both symptoms explained by a single non-P3 mechanism | VERIFIED | 91-RCA.md: `write -b` → `FLAG_SKIP_ERASE` → flash3 skips erase SST39SF040 requires; W27C512 same axis. flash3 is 5V-only, never enables VPP regulator, never calls P3. |
| T-3 | SST39SF040 write+verify is byte-identical to v1.15 baseline (a38b13b4…) | VERIFIED | `bench/SST39SF040-fix/SHA256SUMS.txt`: 3 runs, all `a38b13b4d285756c1f385a75d0cdf89f72720764c21fd933ced75ebdd970b96b` == v1.15 gate. `grep -c` returned 4 (3 data lines + 1 comment). |
| T-4 | 0x06 PROTOCOL-LEDGER row is PASS; 0x07 row is bench-pending (not auto-passed) | VERIFIED | PROTOCOL-LEDGER.json confirmed: `"0x06": "PASS"`, `"0x07": "bench-pending"`. D-04 check passes — no raw 64-hex SHAs in PROTOCOL-LEDGER.json. |
| T-5 | W27C512 deferral properly tracked (not silently dropped) | VERIFIED | W27C512-OPERATOR-CHECKLIST.md exists with turnkey procedure, correct root cause (plain `write` not `write -b`), and v1.15 PASS gate SHA `e16b2a5b…`. check_ledger.py RC=0. |
| T-6 | Firmware byte-identical to recompose a296195 (exploratory delay change reverted; SAFE-04 intact) | VERIFIED | `git -C firestarter status --porcelain src include` → empty. HEAD = a296195. `vpp_check_window` +500 mV guard present at `primitives.cpp:106`. |

---

## Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `.planning/v1.16/ledger/rca/91-RCA.md` | RCA with diff forensics, ebca6266 forensic, A/B decision gate, definitive root cause, fix, board restore + SAFE-04, wrap-up | VERIFIED | All sections present. Root cause: `write -b` sets `FLAG_SKIP_ERASE`, 5-point chain of evidence. FIX-91 GATE MET declaration present with SHA. Wave 4/Wrap-Up section complete. |
| `.planning/v1.16/ledger/bench/SST39SF040-fix/SHA256SUMS.txt` | Must contain gate SHA `a38b13b4…` — 3 runs | VERIFIED | SHA appears 4 times (3 data + 1 comment line in the header). `grep -c` = 4. |
| `.planning/v1.16/ledger/bench/SST39SF040-ab/SHA256SUMS.txt` | A/B: both legs fail identically | VERIFIED | Records recompose leg FAIL + b10 leg FAIL, both `0x1c != 0x04 @0x0`; verdict "recompose INNOCENT". |
| `.planning/v1.16/ledger/bench/BENCH-LOG.md` | Must contain "## Phase 91 A/B + Fix Results" section | VERIFIED | Section heading `## Phase 91 A/B + Fix Results — 2026-06-26 (RCA + FIX-91)` confirmed present. |
| `.planning/v1.16/ledger/PROTOCOL-LEDGER.json` | 0x06 → PASS; 0x07 → bench-pending; no raw 64-hex SHAs | VERIFIED | `0x06: PASS`, `0x07: bench-pending`. D-04 check: no raw 64-hex SHAs. |
| `.planning/v1.16/ledger/PROTOCOL-LEDGER.md` | 0x06 → PASS; 0x07 → bench-pending, lockstep with JSON | VERIFIED | Table rows confirmed. JSON/MD lockstep. |
| `.planning/v1.16/ledger/rca/W27C512-OPERATOR-CHECKLIST.md` | Turnkey; uses plain `write`, gate `e16b2a5b…` | VERIFIED | Checklist present. Uses plain `firestarter write` (not `write -b`). PASS gate = `e16b2a5b26d99440a8e596963faa0f2d64fff4e1dd9682b93b2f8f1ddc326ab5`. |
| Phase 91 SUMMARY files (01-04) | All 4 plans have SUMMARY.md | VERIFIED | 91-01-SUMMARY.md through 91-04-SUMMARY.md all present and self-check = PASSED. |

---

## Key Checks (Programmatic)

| Check | Command | Result | Status |
|-------|---------|--------|--------|
| check_ledger.py RC=0 | `python3 .planning/v1.16/ledger/tools/check_ledger.py` | `PASS: ledger self-consistency check OK — 12 rows, 3 open_defects, all LEDGER-01/02/03 + D-09 assertions satisfied.` Exit 0. | PASS |
| Gate SHA ≥3 in fix SHASUMS | `grep -c a38b13b4… SST39SF040-fix/SHA256SUMS.txt` | 4 (3 data + 1 comment) | PASS |
| D-04: no raw SHA in PROTOCOL-LEDGER.json | Python regex `[0-9a-f]{64}` scan | No matches found | PASS |
| Firmware porcelain clean | `cd firestarter && git status --porcelain src include` | Empty — exit 0 | PASS |
| SAFE-04 guard present | `grep -n "vpp_mv.*500" primitives.cpp` | Line 106: `vpp_mv > (uint32_t)handle->vpp_mv + 500` | PASS |

---

## Operator-Gated Deferral (W27C512)

The W27C512 live bench re-validation is explicitly deferred to operator return (chip swap required). This is correct scoping:

- RCA is complete and documented (same root cause as 0x06 — `write -b` skips required erase)
- PROTOCOL-LEDGER row set to `bench-pending` (not auto-passed, D-03 honored)
- Turnkey checklist (`W27C512-OPERATOR-CHECKLIST.md`) authored with correct method, PASS gate SHA, and diagnostics
- `check_ledger.py` RC=0 confirms `bench-pending` is a valid recognized status

This is a proper deferral with tracking, not a dropped item.

---

## Anti-Patterns Scan

Files modified by this phase scanned for debt markers and stubs.

| File | Pattern | Severity | Impact |
|------|---------|----------|--------|
| `91-RCA.md` | Contains `CORRECTED` and `SUPERSEDED` inline — these are editorial revision markers within a living RCA doc, referencing superseded hypotheses with explicit correction notes. Not unreferenced debt. | Info | None — the RCA documents the investigation path including the corrected intermediate hypothesis. |
| All SUMMARY files | No TBD/FIXME/XXX markers found | — | None |
| PROTOCOL-LEDGER.{json,md} | No TBD/FIXME/XXX markers found | — | None |

No blockers found.

---

## Human Verification Required

None. The headline deliverable (SST39SF040 write+verify byte-identical to v1.15 baseline) is confirmed via `SHA256SUMS.txt` artifacts with consistent SHAs. The W27C512 deferral is correctly tracked. No visual, real-time, or ambiguous behavior requires human assessment beyond the operator-gated bench session already scoped as deferred.

---

## Summary

All three ROADMAP success criteria are MET. The phase delivered:

1. **Controlled A/B attribution** — both `a296195` (recompose) and `a1953c2` (b10) fail identically with `write -b`, exonerating the recompose firmware. Host axis ruled out by byte-identical DB entries and write-path delta analysis.

2. **Both symptoms explained by a single non-P3 mechanism** — `write -b` sets `FLAG_SKIP_ERASE`; flash3 (NOR, 5V-only, P4/P7 only, no P3, no VPP regulator) requires erase-before-write; the erase is silently skipped; the DQ7-only poll masks the failure. W27C512 same axis. A P3-only or 12V-VPP explanation is explicitly ruled out.

3. **0x06 graduated to PASS via FIX-91** (plain `write` instead of `write -b`) — 3/3 consistency-check runs produce `a38b13b4…` == v1.15 gate. 0x07 carried as `bench-pending` with attribution and turnkey checklist. `check_ledger.py` RC=0. Firmware byte-identical to `a296195`; SAFE-04 guard intact.

---

_Verified: 2026-06-26T18:00:00Z_
_Verifier: Claude (gsd-verifier)_
