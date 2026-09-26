---
phase: 93-rca-root-cause-the-w29c040-page-0-write-fault
plan: 01
subsystem: firmware-rca
tags: [flash4, W29C040, SAFE-01, native-tests, VPP-safety, FLAG_CAN_ERASE]

requires:
  - phase: 92-protocol-dispatch-hardening-v116
    provides: flash4 primitives recompose (a296195), P7/P4/P3/P5 shared primitives, golden traces

provides:
  - SAFE-01 pre-flight verification with four recorded verdicts and raw evidence
  - T-93-CANERASE HIGH-severity finding: FLAG_CAN_ERASE (0x02) IS set in W29C040 wire command
  - Native flash4 test suite confirmed PASS (11/11): VPP-free write, SDP emitted, 256B page confirmed
  - Phase-74 traps ruled out: SDP present + 256B page correct in a296195 firmware
  - 93-RCA-FINDINGS.md scaffold with H1–H5 disconfirming-test matrix + bench discipline log
  - evidence/signature/ and evidence/differential/ capture directories for Plans 02–04

affects:
  - 93-02 (repro plan — must use --skip-erase due to T-93-CANERASE)
  - 93-03 (differential plan — T-93-CANERASE bench mitigation required)
  - 93-04 (root-cause classification — T-93-CANERASE is itself an additional Phase 94 fix target)
  - 94 (FIX phase — T-93-CANERASE adds FIX-01 target: prevent FLAG_CAN_ERASE→flash4_erase_execute for 5V chips)

tech-stack:
  added: []
  patterns:
    - "SAFE-01 pre-flight checklist pattern: four recorded verdicts (VPP-free test, flag absent, SDP+page native, resolve_chip normal path)"
    - "T-93-CANERASE threat: FLAG_CAN_ERASE set on protocol 0x05 chips via Flash/EEPROM electrical.type — latent 12V-on-5V hazard"

key-files:
  created:
    - .planning/phases/93-rca-root-cause-the-w29c040-page-0-write-fault/evidence/safety/SAFE-01-PREFLIGHT.md
    - .planning/phases/93-rca-root-cause-the-w29c040-page-0-write-fault/evidence/93-RCA-FINDINGS.md
    - .planning/phases/93-rca-root-cause-the-w29c040-page-0-write-fault/evidence/signature/.gitkeep
    - .planning/phases/93-rca-root-cause-the-w29c040-page-0-write-fault/evidence/differential/.gitkeep
  modified: []

key-decisions:
  - "T-93-CANERASE is HIGH-severity: FLAG_CAN_ERASE (0x02) IS set in W29C040 wire flags via Flash/EEPROM electrical.type; flash4_erase_execute asserts 12V on a 5V chip — bench plans 02–04 MUST use --skip-erase; permanent fix goes to Phase 94 FIX-01"
  - "Phase-74 traps definitively ruled out by native evidence: SDP present (test_flash4_write_execute_emits_sdp PASSED) and 256B page correct (test_inv04_flash4_256b_page_boundary PASSED) — RCA must search deeper"
  - "flash4 write-execute path is VPP-free (test_flash4_write_execute_no_vpp PASSED) — T-93-NOVPP confirmed GREEN"

patterns-established:
  - "Evidence-before-bench discipline: SAFE-01 pre-flight runs autonomously (native+DB inspection) before any silicon is touched"
  - "T-93-CANERASE pattern: for protocol 0x05 (flash4) chips with Flash/EEPROM electrical.type, FLAG_CAN_ERASE routes through flash4_erase_execute (12V) — must be blocked at host or firmware layer"

requirements-completed: [SAFE-01]

duration: 25min
completed: 2026-06-26
---

# Phase 93 Plan 01: SAFE-01 Pre-flight & RCA Findings Scaffold Summary

**FLAG_CAN_ERASE (0x02) IS set in W29C040 wire flags (T-93-CANERASE HIGH-severity), flash4_write_execute is VPP-free, Phase-74 traps ruled out by native evidence (11/11 tests PASSED), and the canonical 93-RCA-FINDINGS.md H1–H5 scaffold is ready for bench Plans 02–04**

## Performance

- **Duration:** ~25 min
- **Started:** 2026-06-26T22:17:32Z
- **Completed:** 2026-06-26
- **Tasks:** 2
- **Files modified:** 4 created (SAFE-01-PREFLIGHT.md, 93-RCA-FINDINGS.md, two gitkeep placeholders)

## Accomplishments

- Confirmed `test_flash4_write_execute_no_vpp` PASSED — flash4 write-execute path sets zero VPP control bits (CTRL_VPP_REGULATOR_ENABLE=0, CTRL_VPP_P1_ENABLE=0). T-93-NOVPP: GREEN.
- Found HIGH-severity T-93-CANERASE: `FLAG_CAN_ERASE (0x02)` IS set in W29C040 wire `flags=0x02` via `database.py:convert_to_programmer` (Flash/EEPROM electrical.type). This routes `flash4_write_init` through `flash4_erase_execute` which asserts 12V (CTRL_VPP_REGULATOR_ENABLE | CTRL_VPP_VPE_DROP_ENABLE | CTRL_VPE_ENABLE) on a 5V-only chip. This was previously believed latent ("no flash4 chip sets FLAG_CAN_ERASE") — that assessment was incorrect.
- Ruled out Phase-74 traps: `test_flash4_write_execute_emits_sdp` PASSED (SDP present) and `test_inv04_flash4_256b_page_boundary` PASSED (256B page confirmed for 512KB W29C040).
- Confirmed `resolve_chip("W29C040")` resolves normally (support_status=supported, no --force bypass).
- Scaffolded `evidence/93-RCA-FINDINGS.md` with six sections and H1–H5 disconfirming-test matrix ready for bench plans to fill.

## Task Commits

1. **Task 1: SAFE-01 native + wire pre-flight verification** - `2e4872d` (feat)
2. **Task 2: Scaffold 93-RCA-FINDINGS.md** - `9e7b577` (feat)

## Files Created/Modified

- `.planning/phases/93-rca-root-cause-the-w29c040-page-0-write-fault/evidence/safety/SAFE-01-PREFLIGHT.md` — Four recorded SAFE-01 verdicts; T-93-CANERASE HIGH-severity finding with causal chain
- `.planning/phases/93-rca-root-cause-the-w29c040-page-0-write-fault/evidence/93-RCA-FINDINGS.md` — Canonical RCA findings scaffold: bench discipline log, RCA-01 prior baseline, RCA-02 axis table, RCA-03 H1–H5 matrix, SAFE-01 section
- `.planning/phases/93-rca-root-cause-the-w29c040-page-0-write-fault/evidence/signature/.gitkeep` — Capture dir for ERROR frames, DEBUG_ADDRESS traces, post-fail reads
- `.planning/phases/93-rca-root-cause-the-w29c040-page-0-write-fault/evidence/differential/.gitkeep` — Capture dir for W29C040 vs W29C020 paired write attempts

## Decisions Made

1. **T-93-CANERASE is HIGH-severity:** Bench plans 02–04 MUST use `--skip-erase` flag on all write commands to bypass `flash4_erase_execute`. Permanent fix (prevent FLAG_CAN_ERASE from routing to 12V erase for 5V flash4 chips) goes to Phase 94 FIX-01. This is a new fix target not in the original Phase 94 scope.

2. **Phase-74 traps definitively ruled out:** Both native tests (SDP + 256B page) PASS on `a296195`. The bench RCA must find the deeper cause; the RESEARCH's ranked hypotheses H1 (timing T_BLC), H2 (A18/addressing), H3 (SDP re-arm), H4 (poll site), H5 (silicon) remain the candidate space.

3. **H1 (timing) remains the leading candidate** per the RESEARCH pre-analysis: W29C040 loads 2× more bytes per page than W29C020 within the same ~200µs T_BLC window; the documented real-world failure mode for AMD/JEDEC page-write parts is "programmer loads too slowly." Post-bench confirmation or disconfirmation is Plan 02–03's task.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Corrected RESEARCH/Pitfall-3 assertion "no flash4 chip sets FLAG_CAN_ERASE"**
- **Found during:** Task 1 (SAFE-01 preflight inspection)
- **Issue:** The RESEARCH (Pitfall 3) stated that `flash4_erase_execute`'s 12V VPP assertion was "latent dead code" because "no flash4 DB chip sets FLAG_CAN_ERASE." Direct inspection of `database.py:convert_to_programmer` and `resolve_chip("W29C040")` showed `flags=0x02` IS returned — the RESEARCH's assessment was based on an incorrect prior belief.
- **Fix:** Recorded as HIGH-severity T-93-CANERASE in SAFE-01-PREFLIGHT.md (not subjective "looks safe" language) as required by the plan's acceptance criteria. Documented bench mitigation (`--skip-erase`) and Phase 94 fix target.
- **Files modified:** SAFE-01-PREFLIGHT.md (reflects the actual finding), 93-RCA-FINDINGS.md (SAFE-01 section updated accordingly)
- **Committed in:** 2e4872d (Task 1 commit)

---

**Total deviations:** 1 (Rule 1 correction of RESEARCH assumption; no code changed — this is a documentation/evidence deviation)
**Impact on plan:** The T-93-CANERASE finding STRENGTHENS the RCA by identifying an additional hazard. Bench plans 02–04 require `--skip-erase` (already noted in repro commands). Phase 94 FIX-01 scope expands to include this flag-propagation bug.

## Issues Encountered

None beyond the T-93-CANERASE deviation documented above.

## Threat Surface Scan

| Flag | File | Description |
|------|------|-------------|
| threat_flag: hardware-voltage | `firestarter_app/firestarter/database.py` | `convert_to_programmer` sets FLAG_CAN_ERASE for ALL Flash/EEPROM electrical.type chips including protocol 0x05 (flash4). On protocol 0x05, this routes through `flash4_erase_execute` which asserts CTRL_VPP_REGULATOR_ENABLE (12V) — wrong for 5V flash4 chips. Existing T-93-CANERASE; documented; Phase 94 FIX-01 target. |

## Known Stubs

The `93-RCA-FINDINGS.md` scaffold contains intentional placeholder sections (TBD rows in all tables under Plans 02–04 scope). These are by design — the document is the bench plan's fill target, not a complete findings doc. No stubs exist in the SAFE-01-PREFLIGHT.md (all four verdicts are fully recorded).

## Next Phase Readiness

**Plan 02 (93-02) is ready to proceed** with these constraints carried forward:

1. **MUST use `--skip-erase`** on all `firestarter write` commands for W29C040 during the RCA (T-93-CANERASE bench mitigation).
2. The failure signature to reproduce: `ERROR "Timeout verifying 0xd7 at 0x0000ff (got 0x00)"` (N≥2 deterministic, from Phase 82/84).
3. Post-fail `dev read` of `0x0000ff` is the cheapest H4 disconfirmer (free with the repro).
4. Operator must seat W29C040 on Leonardo + Rev 2.0 and run standing bench discipline (R1/R2 readback, controller identity verification).

**Phase 94 FIX-01 scope update:** Add the T-93-CANERASE fix (prevent FLAG_CAN_ERASE from reaching `flash4_erase_execute` for protocol 0x05 chips, either at host DB layer or firmware flash4 handler layer).

## Self-Check: PASSED

---
*Phase: 93-rca-root-cause-the-w29c040-page-0-write-fault*
*Completed: 2026-06-26*
