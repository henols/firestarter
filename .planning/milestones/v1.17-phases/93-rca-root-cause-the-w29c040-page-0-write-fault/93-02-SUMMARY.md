---
phase: 93-rca-root-cause-the-w29c040-page-0-write-fault
plan: 02
subsystem: bench-evidence
tags: [w29c040, flash4, rca, page-write, bench, reproduction, serial-capture]

# Dependency graph
requires:
  - phase: 93-01
    provides: SAFE-01 pre-flight + T-93-CANERASE finding + RCA scaffold (93-RCA-FINDINGS.md)
provides:
  - "W29C040 page-0 write fault reproduced N=2 deterministically on seated chip (Leonardo + Rev 2.0)"
  - "Exact failure signature: ERROR Timeout verifying 0x04 at 0x0000ff (got 0x00)"
  - "H4 DISCONFIRMED: 0x0000ff stays 0x00 after N=5 settled reads — page never committed"
  - "Bench discipline row recorded: port=/dev/ttyACM0, R1=270000, R2=44000, Rev 2.0-class, chip-id=0xda46"
  - "Raw serial captures in evidence/signature/ (run1.txt, run2.txt, page0 reads, settled reads)"
  - "T-93-CANERASE gate resolved: all writes used --skip-erase, operator-authorized"
affects: [93-03, 93-04, 94-fix, phase-94]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "W29C040 repro command: firestarter write -b --skip-erase W29C040 <img> (T-93-CANERASE mitigation)"
    - "Deterministic test image: python tools/gen_test_image.py 1024 42 <path> (seed=42, SHA 1ba43bf5)"
    - "Post-fail H4 fork: dev read -a 0xff -s 1 repeated N×5 to test settled vs stale"

key-files:
  created:
    - ".planning/phases/93-rca-root-cause-the-w29c040-page-0-write-fault/evidence/signature/run1.txt"
    - ".planning/phases/93-rca-root-cause-the-w29c040-page-0-write-fault/evidence/signature/run2.txt"
    - ".planning/phases/93-rca-root-cause-the-w29c040-page-0-write-fault/evidence/signature/page0_readback_hex_after_run1.txt"
    - ".planning/phases/93-rca-root-cause-the-w29c040-page-0-write-fault/evidence/signature/page0_readback_hex_after_run2.txt"
    - ".planning/phases/93-rca-root-cause-the-w29c040-page-0-write-fault/evidence/signature/settled_read_0x0000ff.txt"
    - ".planning/phases/93-rca-root-cause-the-w29c040-page-0-write-fault/evidence/signature/settled_read_after_run2.txt"
    - ".planning/phases/93-rca-root-cause-the-w29c040-page-0-write-fault/evidence/signature/w29c040_test_1024b_seed42.bin"
    - ".planning/phases/93-rca-root-cause-the-w29c040-page-0-write-fault/evidence/signature/pages1to3_readback_hex_after_run2.txt"
  modified:
    - ".planning/phases/93-rca-root-cause-the-w29c040-page-0-write-fault/evidence/93-RCA-FINDINGS.md"

key-decisions:
  - "T-93-CANERASE gate cleared by operator decision 2026-06-27: all writes use --skip-erase; full fix deferred to Phase 94 FIX-01"
  - "H4 DISCONFIRMED: 0x0000ff stays 0x00 (not 0x04) after N=5 settled reads — page never committed (not poll-gave-up-on-committed-page)"
  - "Fault is at last byte of page 0 (0x0000ff, observed=0x00) — identical site to v1.15 Phase 82/84 baseline; different test image (expected=0x04 not 0xd7)"

patterns-established:
  - "RCA repro always uses --skip-erase on W29C040 (T-93-CANERASE mitigation)"
  - "Post-fail H4 fork: immediate repeated reads of failing address determine settled vs stale"

requirements-completed: [RCA-01, SAFE-01]

# Metrics
duration: 8min
completed: 2026-06-27
---

# Phase 93 Plan 02: Bench Reproduction + Failure Signature Capture Summary

**W29C040 page-0 write fault reproduced N=2 deterministically (0x0000ff stays 0x00 after N=5 settled reads — H4 disconfirmed, page never committed)**

## Performance

- **Duration:** 8 min
- **Started:** 2026-06-27T06:37:00Z
- **Completed:** 2026-06-27T06:42:00Z
- **Tasks:** 2 (Task 1 bench pre-flight + Task 2 fault reproduction + post-fail reads)
- **Files modified:** 13 (1 updated findings doc + 12 new capture files)

## Accomplishments

- Chip-id 0xda46 confirmed seated and responding on /dev/ttyACM0 before any write
- W29C040 page-0 write fault reproduced deterministically on N=2 independent runs with identical ERROR frame: `Timeout verifying 0x04 at 0x0000ff (got 0x00)`
- H4 DISCONFIRMED: address 0x0000ff reads 0x00 across N=5 repeated reads after failure — the page did NOT commit; the poll did not merely exhaust iterations on a completed write
- Bench discipline row recorded (R1=270000/R2=44000, Rev 2.0-class, chip-id=0xda46, post-HARD-01 host)
- T-93-CANERASE gate resolved by operator decision; all writes used `--skip-erase` (no 12V on 5V chip)

## Task Commits

Each task was committed atomically:

1. **Task 1+2: Bench reproduction + RCA-01 evidence capture** — `bda0081` (feat)

## Files Created/Modified

- `.planning/phases/93-rca-root-cause-the-w29c040-page-0-write-fault/evidence/93-RCA-FINDINGS.md` — bench discipline row + full RCA-01 repro results section filled
- `.../evidence/signature/run1.txt` — full serial capture Run 1 (ERROR frame verbatim)
- `.../evidence/signature/run2.txt` — full serial capture Run 2 (identical ERROR frame)
- `.../evidence/signature/w29c040_test_1024b_seed42.bin` — deterministic 1024B test image
- `.../evidence/signature/page0_readback_hex_after_run1.txt` — page 0 hex dump after Run 1
- `.../evidence/signature/page0_readback_hex_after_run2.txt` — page 0 hex dump after Run 2 (identical)
- `.../evidence/signature/settled_read_0x0000ff.txt` — N=5 repeated reads of 0x0000ff (all 0x00)
- `.../evidence/signature/settled_read_after_run2.txt` — point reads at 0x00ff/0x0000/0x00fe post-Run-2
- `.../evidence/signature/pages1to3_readback_hex_after_run2.txt` — pages 1–3 hex dump

## Decisions Made

- **T-93-CANERASE gate cleared by operator decision (2026-06-27):** The operator authorized proceeding with `--skip-erase` mitigation. All W29C040 writes used `firestarter write -b --skip-erase W29C040 <img>`. Full fix (preventing FLAG_CAN_ERASE from routing through flash4_erase_execute for protocol 0x05 chips) deferred to Phase 94 FIX-01.

- **H4 DISCONFIRMED:** Address 0x0000ff does not settle to written value 0x04 after N=5 repeated reads (stays 0x00). The page never committed — the poll did not merely give up on a late-completing write. This sharpens the remaining hypotheses toward H1 (timing/T_BLC violation) and H3 (SDP rejection), to be resolved in Plan 03.

## Deviations from Plan

### Auto-fixed Issues

None — plan executed exactly as written, with the CRITICAL_SAFETY_OVERRIDE applied as specified: all writes used `--skip-erase` per the operator's authorized proceed-with-mitigation decision.

**T-93-CANERASE STOP clause resolution:** The plan's Task 1 acceptance criterion #2 says "if [SAFE-01] recorded T-93-CANERASE, STOP." This was resolved by the operator's explicit proceed-with-skip-erase authorization in the execution prompt (CRITICAL_SAFETY_OVERRIDE). The gate was not bypassed — it was cleared by the operator before bench work began.

**Note on `write-cycle --runs 2`:** The `firestarter dev write-cycle` command does not support `--skip-erase`, so N=2 determinism was established by running `firestarter write -b --skip-erase` twice manually, which is the equivalent method cited in RESEARCH § "Alternatives Considered."

## Issues Encountered

None. The chip was seated and responding at the expected address before any write. The fault reproduced identically on both runs.

## RCA-01 Findings Summary

| Item | Value |
|------|-------|
| Failing address | `0x0000ff` — last byte of 256B page 0 |
| Expected byte (Run 1+2) | `0x04` (test image seed=42 offset 255) |
| Observed byte (Run 1+2) | `0x00` |
| Decoded frame | `[expected=0x04, A16=0x00, A8=0x00, A0=0xFF, observed=0x00]` |
| N=2 determinism | CONFIRMED — identical ERROR frame on both runs |
| Post-fail 0x0000ff settled read | `0x00` (N=5 reads, stable) |
| H4 verdict | DISCONFIRMED — page never committed (not poll-gave-up) |
| SAFE-01 reaffirmed | All writes via normal 0x05 dispatch + `--skip-erase` |

**Comparison to v1.15 baseline (Phase 82/84):** Same failing address (0x0000ff), same observed=0x00. Expected byte differs (0x04 vs historical 0xd7) because a different test image was used; the fault pattern is identical. RCA-01 reproduction confirmed.

## Next Phase Readiness

Plan 03 (differential W29C040 vs W29C020) is ready to proceed. The H4 disconfirmation result narrows the active hypotheses:

- **H4 DISCONFIRMED:** page never committed (settled read stays 0x00)
- **H1 active** (timing T_BLC violation): disconfirming test = single-byte write to page 0
- **H3 active** (SDP rejection): disconfirming test shares the single-byte write with H1
- **H2 active** (A18 addressing): disconfirming test = DEBUG_ADDRESS trace across one page-0 load
- **H5 active** (silicon defect): disconfirming test = write to non-page-0 address

The chip remains seated on Leonardo + Rev 2.0 for Plan 03.

---
*Phase: 93-rca-root-cause-the-w29c040-page-0-write-fault*
*Completed: 2026-06-27*
