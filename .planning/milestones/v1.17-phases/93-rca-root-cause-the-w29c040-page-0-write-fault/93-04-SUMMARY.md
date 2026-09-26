---
phase: 93-rca-root-cause-the-w29c040-page-0-write-fault
plan: "04"
subsystem: firmware-rca
tags: [w29c040, flash4, boot-block, rca, silicon, safe-01, phase-close]

# Dependency graph
requires:
  - phase: 93-03
    provides: "H1–H5 disconfirming matrix fully populated; H5 CONFIRMED (§6.6 boot-block); all bench captures in evidence/differential/"

provides:
  - "RCA-03: Named root cause — W29C040 §6.6 first-16K boot-block programming lockout, classified SILICON (chip-instance-specific hardware-feature-state)"
  - "Lock-reversibility fork (a) software-reversible vs (b) hardware-permanent — disambiguating test identified as Phase 94 first step"
  - "Phase-94 hand-off: (1) §6.6 UNLOCK check + fix path; (2) T-93-CANERASE FIX-01 scope; (3) milestone done-bar impact"
  - "SAFE-01 phase-close: 4-item checklist consolidated across Plans 01–03; HELD (conditional on --skip-erase mitigation); T-93-CANERASE caveat"
  - "93-VALIDATION.md signed off: nyquist_compliant=true, all 4 rows confirmed, evidence map complete"

affects:
  - "94-fix-pgsz-w29c040"
  - "95-bench-graduation"
  - "96-ledger-close"

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Lock-reversibility fork pattern: always check if a hardware protection is software-reversible BEFORE assuming it is silicon-permanent; the bench data is agnostic — the datasheet must be read directly"
    - "Phase-close SAFE-01 pattern: consolidate per-item verdicts with per-plan citations; HELD verdict + mitigation caveat + downstream precondition"
    - "Phase 44 D-07 causal bar applied: the variable that moves the failure (address region < vs >= 0x4000) uniquely confirms H5 while competitors are disconfirmed by direct bench evidence"

key-files:
  created:
    - ".planning/phases/93-rca-root-cause-the-w29c040-page-0-write-fault/93-04-SUMMARY.md"
  modified:
    - ".planning/phases/93-rca-root-cause-the-w29c040-page-0-write-fault/evidence/93-RCA-FINDINGS.md"
    - ".planning/phases/93-rca-root-cause-the-w29c040-page-0-write-fault/93-VALIDATION.md"

key-decisions:
  - "Root cause classified SILICON (chip-instance-specific boot-block state), NOT firmware-algorithm: the write algorithm is proven correct for unlocked pages (0x4000+); the fault is a chip hardware feature state"
  - "Lock reversibility NOT overclaimed: evidence is agnostic on (a) software-reversible vs (b) hardware-permanent; §6.6 datasheet text must be read directly in Phase 94 as the first investigation step"
  - "T-93-CANERASE recorded as a REQUIRED Phase 94 FIX-01 (independent of boot-block outcome): FLAG_CAN_ERASE=0x02 routes flash4_write_init through flash4_erase_execute (12V on 5V chip); host-side fix in convert_to_programmer is the clean approach"
  - "SAFE-01 = HELD (conditional): held ONLY because --skip-erase was used throughout; underlying hazard is OPEN until Phase 94 FIX-01"
  - "Milestone done-bar impact noted for operator: if lock is permanent, Phase 95 BENCH-01 requires a different (unlocked) W29C040 sample OR re-scope to addresses >= 0x4000"

patterns-established:
  - "Do not state 'irreversible' for silicon protection features without reading the datasheet — present the (a)/(b) fork and name the disambiguating test instead"
  - "SAFE-01 phase-close requires per-item citations to the specific plan where evidence was recorded, not a blanket assertion"

requirements-completed: [RCA-03, SAFE-01]

# Metrics
duration: 20min
completed: 2026-06-27
---

# Phase 93 Plan 04: RCA-03 Named Root Cause + SAFE-01 Phase-Close Summary

**W29C040 §6.6 first-16K boot-block programming lockout named as root cause (SILICON/chip-instance-specific state), firmware algorithm proven correct for unlocked pages, Phase-94 hand-off complete with T-93-CANERASE FIX-01 and lock-reversibility fork**

## Performance

- **Duration:** ~20 min
- **Started:** 2026-06-27T07:35:00Z
- **Completed:** 2026-06-27T07:55:00Z
- **Tasks:** 2 (Task 1: named root cause + Phase-94 hand-off; Task 2: SAFE-01 phase-close + validation sign-off)
- **Files modified:** 2 (evidence/93-RCA-FINDINGS.md, 93-VALIDATION.md)

## Accomplishments

- **RCA-03 complete:** H5 CONFIRMED (SILICON) as the sole surviving hypothesis. H1/H2/H3/H4 all carry disconfirming evidence from direct bench results; none left "untested". The Phase 44 D-07 causal bar is met — the variable that moves the failure is uniquely the address region relative to the §6.6 first-16K boundary.
- **Lock-reversibility fork presented precisely:** The synthesis guidance required not overclaiming "permanent." The (a) software-reversible / (b) hardware-permanent fork is stated with the disambiguating test (read §6.6 for UNLOCK command) identified as the Phase 94 first step. Research notes lean toward (b), but the PDF was not directly readable during synthesis; (b) is stated as the working classification pending Phase 94 datasheet confirmation.
- **Phase-94 hand-off written with two required items:** (1) boot-block reversibility check and the two-fork fix path; (2) T-93-CANERASE as a required FIX-01 scope item (FLAG_CAN_ERASE 12V hazard, independent of boot-block outcome); (3) milestone done-bar impact noted for the operator.
- **SAFE-01 phase-close consolidated:** 4-item checklist with per-plan citations; verdict HELD (conditional on --skip-erase mitigation throughout); T-93-CANERASE caveat recorded; phases 94–96 precondition stated.
- **93-VALIDATION.md signed off:** nyquist_compliant=true, all 4 verification-map rows updated to confirmed status, evidence map linking every requirement to its artifact, Approval signed 2026-06-27.

## Task Commits

Both tasks committed atomically in a single commit (they write to the same files and form a coherent Plan 04 unit):

1. **Tasks 1+2: named root cause + phase-close** — `0000177` (feat)

## Files Created/Modified

- `.planning/phases/93-rca-root-cause-the-w29c040-page-0-write-fault/evidence/93-RCA-FINDINGS.md` — Added: frontmatter status update; "Lock Reversibility Fork" subsection in RCA-03; full "Hand-off to Phase 94" section (boot-block disambiguation + T-93-CANERASE FIX-01 + done-bar impact); replaced stub SAFE-01 section with full phase-close (4-item checklist + consolidated HELD verdict)
- `.planning/phases/93-rca-root-cause-the-w29c040-page-0-write-fault/93-VALIDATION.md` — Updated: frontmatter (nyquist_compliant: true, status: complete, signed_off); per-task verification-map rows all updated to confirmed; Validation Sign-Off checklist all checked; Evidence Map table added; Approval signed

## Decisions Made

- **Lock reversibility: present the fork, do not overclaim.** The existing "Named Root Cause" section from Plan 03 stated the lock was "irreversible silicon-level hardware protection state." The synthesis guidance explicitly required not overclaiming. The fork (a)/(b) is now presented with the disambiguating test. The working classification is (b) HARDWARE-PERMANENT per the research record, but Phase 94 must confirm by reading §6.6 directly.

- **Phase-94 hand-off: T-93-CANERASE is a REQUIRED FIX-01 regardless of boot-block outcome.** The entire RCA required `--skip-erase` to avoid hardware damage. This flag cannot remain as an operational requirement on users. The host-side fix in `database.py:convert_to_programmer` (do not set FLAG_CAN_ERASE for algorithm==5 chips) is identified as the clean approach.

- **Milestone done-bar: flag for operator, do not decide.** Whether the chip's lock is reversible or permanent determines whether Phase 95 BENCH-01 can proceed on the seated chip. This is an operator decision; the hand-off states both scenarios clearly without picking one.

## Deviations from Plan

None — plan executed as written. The synthesis was driven entirely from evidence already recorded in Plans 01–03. No new bench work was needed or performed.

The one deviation from the initial Plan 03 "Named Root Cause" text was adding the (a)/(b) lock-reversibility fork to avoid overclaiming — this was explicitly required by the synthesis guidance and the plan's threat model (T-93-PH74: mis-named cause sends the fix in the wrong direction).

## Issues Encountered

- **W29C040.pdf §6.6 not directly readable** (PDF rendering unavailable in environment — `pdftoppm` not installed). The lock reversibility determination relied on the research notes from 93-RESEARCH.md, which describe the lock as "set by a 7-byte command sequence and is permanent." Rather than claim this is confirmed from the PDF, the (a)/(b) fork is presented and Phase 94 is required to read §6.6 directly. This is the correct conservative treatment.

## Known Stubs

None — this is an RCA synthesis plan. All evidence references point to existing artifacts from Plans 01–03.

## Threat Flags

None — no new network endpoints, auth paths, file access patterns, or schema changes. This plan modifies only `.planning/` documentation files.

## Next Phase Readiness

**Phase 94 (FIX + PGSZ) is ready to begin.**

Required first step: Read W29C040.pdf §6.6 for boot-block UNLOCK command:
- If UNLOCK exists (a): add boot-block unlock to flash4 write path for 0x0000–0x3FFF addresses; re-pin golden traces; milestone done-bar achievable on seated chip
- If no UNLOCK (b): FIX-01 is T-93-CANERASE only + PGSZ; operator decision on new chip vs re-scope BENCH-01

**FIX-01 scope (required regardless of outcome):**
- Prevent FLAG_CAN_ERASE from routing through flash4_erase_execute for protocol 0x05 chips
- Recommended: `database.py:convert_to_programmer` should not set FLAG_CAN_ERASE for algorithm==5
- Check constants parity (SAFE-02: constants.py <-> firestarter.h)

**Phase 93 is closed.** All 4 plans complete. RCA-01/02/03 + SAFE-01 satisfied. 93-VALIDATION.md signed off.

## Self-Check: PASSED

| Item | Status |
|------|--------|
| `evidence/93-RCA-FINDINGS.md` exists | FOUND |
| `93-VALIDATION.md` exists | FOUND |
| `93-04-SUMMARY.md` exists | FOUND |
| Task commit `0000177` exists in git log | FOUND |
| Docs commit `571f0a3` exists in git log | FOUND |
| NAMED_CAUSE_OK automated check | PASSED |
| SAFE_SIGNOFF_OK automated check | PASSED |
| nyquist_compliant: true in VALIDATION.md | CONFIRMED |
| RCA-FINDINGS.md line count (≥80 non-comment) | 499 lines total |

---
*Phase: 93-rca-root-cause-the-w29c040-page-0-write-fault*
*Completed: 2026-06-27*
