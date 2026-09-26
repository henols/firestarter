---
phase: 90-per-protocol-bench-validation-ledger
plan: 04
subsystem: testing
tags: [bench-validation, hardware, regression, sha256, vpp, flash, eprom, fram, recompose]

requires:
  - phase: 90-01
    provides: check_ledger.py self-consistency checker (D-09 PASS constraint)
  - phase: 90-02
    provides: PROTOCOL-LEDGER.{json,md} with bench-pending on-hand rows
  - phase: 89
    provides: recomposed firmware a296195 (P3/P4/P5/P7 primitives) under test
provides:
  - Hardware bench regression of the 4 on-hand protocols on the recompose (a296195)
  - BENCH-LOG.md with per-chip read+write-cycle SHA verdicts vs v1.15 baseline
  - 0x05 + 0x28 flipped to PASS with D-09 evidence references
  - 0x06 + 0x07 recorded FAIL-INVESTIGATE — reproducible recompose write-path regression
affects: [v1.16-milestone-disposition, phase-90-verification, recompose-write-path-rca, w27c512, sst39sf040]

tech-stack:
  added: []
  patterns:
    - "write -b direct path (write A/verify -> write B/verify -> consistency-check N=3) is the v1.15-faithful write-cycle method for ALL flash/EPROM/FRAM chips; dev write-cycle blank-checks and fails on flash4"
    - "Per-dir SHA256SUMS.txt as committed bench evidence (no large binaries; v1.15 convention)"

key-files:
  created:
    - .planning/v1.16/ledger/bench/BENCH-LOG.md
    - .planning/v1.16/ledger/bench/<chip>-{read,wcB}/SHA256SUMS.txt (8 dirs)
  modified:
    - .planning/v1.16/ledger/PROTOCOL-LEDGER.json
    - .planning/v1.16/ledger/PROTOCOL-LEDGER.md

key-decisions:
  - "Deviation (grounded in v1.15 EVIDENCE): used write -b direct path for all 4 chips, not dev write-cycle (which blank-checks and fails on flash4's no-bulk-erase model and would defeat the auto-erase proof)"
  - "2/4 write paths fail reproducibly -> recorded FAIL-INVESTIGATE, NOT auto-passed (D-03); only 0x05+0x28 flipped to PASS"
  - "Bench evidence committed as per-dir SHA256SUMS + BENCH-LOG (no ~5MB binaries); D-09 satisfied by non-empty p90_artifacts path list (operator delegated the call)"
  - "Submodule gitlinks NOT bumped — stay pinned at b10 (D-06); checked-out test builds (fw a296195 / app e46549f) not committed to meta"

patterns-established:
  - "12V-VPP write-path failure axis: the two 12V flash/EPROM paths (0x06, 0x07) fail; the two 5V/no-VPP paths (0x05 flash4, 0x28 SRAM) pass; all 4 read paths clean"

requirements-completed: [LEDGER-02]

duration: ~75min
completed: 2026-06-26
---

# Phase 90 Plan 04: Bench Validation Summary

**Hardware bench regression on the recomposed firmware (a296195) surfaced a reproducible 12V-VPP write-path regression: all 4 read paths are byte-identical to v1.15, but 2 of 4 write paths (W27C512/0x07, SST39SF040/0x06) fail reproducibly — only W29C020/0x05 and FM1608/0x28 earned PASS.**

## Performance
- **Duration:** ~75 min (operator-gated bench session)
- **Tasks:** 3/3 executed
- **Oracle:** Leonardo on /dev/ttyACM0, RURP shield Rev 2.0 (operator silkscreen-confirmed), fw a296195 (re-flashed + verified, Flash 87.7%/25136 B)

## Accomplishments
- Bench-tested all 4 on-hand protocols (read N≥3 + write-cycle A→B) against the v1.15 byte-exact baseline.
- **All 4 READ paths byte-identical to v1.15** (recompose read path is behavior-preserving).
- **W29C020 (0x05) + FM1608 (0x28): PASS** — read + write-cycle both byte-identical; auto-erase proven (B over A, no explicit erase); neg-control verify(A) RC=1.
- **W27C512 (0x07) + SST39SF040 (0x06): FAIL-INVESTIGATE** — reproducible write-path failures on the recompose (read clean).
- Flipped only the 2 PASS rows; `check_ledger.py` exits 0 with the D-09 PASS constraint active+satisfied; D-04 no-copy guard holds.

## Task Commits
1. **Task 1: flash a296195 + image-SHA sanity + BENCH-LOG header** — `108cd7b` (feat)
2. **Task 2: bench regression of 4 chips** — `65053b3` (feat)
3. **Task 3: flip 0x05+0x28 PASS, 0x06+0x07 FAIL-INVESTIGATE + checker** — `c2bd2b7` (feat)

## The Verdicts (8 SHA checks)

| Bucket | Chip | Read N≥3 vs v1.15 | Write-cycle vs v1.15 | Verdict |
|--------|------|-------------------|----------------------|---------|
| 0x05 | W29C020 | ✓ `47304933…` | ✓ `47304933…` (auto-erase) | **PASS** |
| 0x06 | SST39SF040 | ✓ `a38b13b4…` | ✗ `ebca6266…` (write A timeout; write B wrong content) | **FAIL-INVESTIGATE** |
| 0x07 | W27C512 | ✓ `e16b2a5b…` | ✗ `ce12c20a…` (bad bytes @0x0, clean 12.0V rail) | **FAIL-INVESTIGATE** |
| 0x28 | FM1608 | ✓ `3c23e7fc…` | ✓ `3c23e7fc…` | **PASS** |

> D-01 nuance (all 4 chips): each pre-write read returned image B (the v1.15 *write-cycle-final* SHA), because v1.15's own write-cycle left image B on the chip — the read-baseline contents are unreachable by design (RESEARCH line 130). Read PASS = N≥3 stable + byte-identical to the v1.15 write-cycle-final baseline.

## ⚠ Milestone-significant finding — recompose write-path regression
- **Failure axis:** the two 12V-VPP flash/EPROM write paths (0x06 flash3, 0x07 EPROM-STD) fail reproducibly (confirmed across reseat); the two 5V/no-VPP paths (0x05 flash4 auto-erase-at-5V, 0x28 SRAM) pass. All reads clean.
- **Symptoms differ:** W27C512 — `bad bytes ~921 @0x000000` at a clean 12.0V VPP rail; SST39SF040 — write A firmware timeout + write B deterministically-wrong content (`ebca6266`).
- **Primitives:** 0x07 uses P3 `vpp_check_window` (−402 B, biggest recompose change); flash3 (0x06) uses P4/P7 (no P3) — so a single-primitive (P3-only) explanation does NOT cover both. The common axis is the 12V-VPP write path.
- **fw vs host not yet isolated:** firmware-under-test = `firestarter@a296195`; host = `firestarter_app@e46549f` (also a v1.16 build, NOT the v1.15 host `98b3a92`). Recommended controlled A/B: reflash b10 fw (or check out v1.15 host) and re-run W27C512/SST39SF040.

## Deviations
- **Write method:** used the v1.15 `write -b` direct path for all 4 chips instead of the plan's `dev write-cycle` (which blank-checks and fails on flash4's no-bulk-erase model; v1.15 EVIDENCE confirms all 4 baselines were produced via `write -b`). The two failed `dev write-cycle` attempts on W29C020 wrote nothing (blank-check refused) and altered no state.
- **Evidence binaries:** committed per-dir `SHA256SUMS.txt` + BENCH-LOG (all SHAs) rather than ~5 MB of run binaries — v1.15 convention; D-09 satisfied by non-empty `p90_artifacts` path list (operator delegated the call).
- **Gitlinks:** NOT bumped (D-06 — pinned at b10).

## Self-Check: PASSED (plan tasks) / GOAL PARTIALLY MET
- All 3 tasks executed and committed atomically; `check_ledger.py` RC=0; D-04 clean; MD/JSON lockstep.
- **LEDGER-02 is satisfied for 0x05 + 0x28 only.** 0x06 + 0x07 are NOT graduated (reproducible write-path regression). The phase goal "each on-hand protocol bench-validated → PASS" is **partially unmet** — operator/verifier disposition required (carry 0x06/0x07 as recompose-regression defect rows vs pause v1.16 for a fw/host write-path fix).

## Follow-up
- RCA the 12V-VPP write-path regression (W27C512 + SST39SF040); reflash-b10 A/B test to confirm recompose-causality vs pre-existing; isolate fw (a296195) vs host (e46549f).
- Both failing chips currently hold partial/wrong content (`ce12c20a` / `ebca6266`); rewritable, recoverable once fixed.
