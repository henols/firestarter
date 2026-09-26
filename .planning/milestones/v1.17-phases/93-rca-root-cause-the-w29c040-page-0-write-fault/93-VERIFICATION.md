---
phase: 93-rca-root-cause-the-w29c040-page-0-write-fault
verified: 2026-06-27T08:30:00Z
status: passed
score: 4/4
overrides_applied: 0
---

# Phase 93: RCA — Root-Cause the W29C040 Page-0 Write Fault — Verification Report

**Phase Goal:** The W29C040 flash4 (0x05) page-0 write fault is reproduced on real silicon with a captured failure signature, differentially isolated against the passing 0x05 sibling W29C020, and named to a specific root cause (or ranked hypotheses each with disconfirming evidence) — classified as firmware-algorithm, timing, addressing, or silicon — sufficient to design a targeted fix.
**Verified:** 2026-06-27T08:30:00Z
**Status:** passed
**Re-verification:** No — initial verification

---

## Critical Framing Note

This is an RCA (diagnosis) phase. The correct deliverable is EVIDENCE (reproduced signature + differential + named/ranked cause + SAFE-01 held), NOT corrected firmware. The absence of a code fix is not a gap — it is correct. Firmware correction is Phase 94's job.

---

## Goal Achievement

### Observable Truths (from ROADMAP.md Success Criteria)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | W29C040 page-0 write fault reproduces on seated chip (Leonardo + Rev 2.0) with recorded failure signature — failing addresses/bytes + observed DQ7/DQ6 poll behavior + operator-witnessed bench discipline | VERIFIED | `evidence/signature/run1.txt` + `run2.txt`: N=2 identical `ERROR: Timeout verifying 0x04 at 0x0000ff (got 0x00)`; bench discipline row recorded in FINDINGS §"Bench Discipline Log" (Plan 02 row: port=/dev/ttyACM0, R1=270000, R2=44000, Rev 2.0-class, chip-id=0xda46) |
| 2 | W29C040 write path differentially compared against passing sibling W29C020 across all 4 candidate axes (SDP, timing, A18 addressing, page size) with differing variable(s) isolated and unchanged axes exonerated | VERIFIED | Datasheet differential in FINDINGS §RCA-02 exonerates SDP/pinout/VPP/page-size-value; live disconfirming matrix in Plans 02–03 exonerates H1 (single-byte FAIL), H2 (DEBUG_ADDRESS trace + A18=1 PASS at 0x40000), H3 (same SDP path; A18=1 pages pass), H4 (settled read stays 0x00 N=5); boot-block §6.6 isolation proved by exact 16K boundary sweep (0x3F00 FAIL / 0x4000 PASS) |
| 3 | Named root cause (or ranked hypotheses each with disconfirming evidence) recorded and classified firmware-algorithm / timing / addressing / silicon, with enough detail to design a targeted fix without further RCA | VERIFIED | FINDINGS §"RCA-03 — Named Root Cause": H5 CONFIRMED; classification = SILICON (chip-instance-specific hardware-feature-state); H1/H2/H3/H4 each carry direct bench disconfirming evidence; Phase-94 hand-off present with two explicit action items (§6.6 reversibility check + T-93-CANERASE FIX-01) |
| 4 | Throughout the RCA, over-voltage stays blocked at firmware VPP check and host `chip_resolver.resolve_chip` guard is never bypassed — W29C040 flows through normal dispatch, no test-only escape hatch | VERIFIED | FINDINGS §"SAFE-01 — Non-Bypass Confirmation": 4-item checklist with per-plan citations; `test_flash4_write_execute_no_vpp` PASSED (Plan 01 native); resolve_chip normal path confirmed; T-93-CANERASE FOUND (flags=0x02) but mitigated via `--skip-erase` throughout Plans 02–03 with operator authorization; SAFE-01 = HELD (conditional) |

**Score: 4/4 truths verified**

---

## Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `evidence/safety/SAFE-01-PREFLIGHT.md` | SAFE-01 pre-flight with four recorded verdicts and raw evidence | VERIFIED | 203 lines; all 4 checklist items with raw evidence; T-93-CANERASE RED/HIGH recorded; native test output verbatim |
| `evidence/93-RCA-FINDINGS.md` | Canonical RCA findings with RCA-01/02/03 sections + H1–H5 disconfirming matrix + SAFE-01 close-out + Phase-94 hand-off (≥80 non-comment lines) | VERIFIED | 499 total lines, 360 non-comment lines (far exceeds the ≥80 threshold); all required sections present; H1–H5 matrix complete with verdicts; Named Root Cause section with classification; Hand-off to Phase 94 section; SAFE-01 phase-close section |
| `evidence/signature/` (directory with raw captures) | Raw serial ERROR frames + post-fail read-backs | VERIFIED | 11 files present: `run1.txt`, `run2.txt`, `settled_read_0x0000ff.txt`, `page0_readback_*`, `pages1to3_readback_*`, `settled_read_after_run2.txt`, `w29c040_test_1024b_seed42.bin` |
| `evidence/differential/` (directory with raw captures) | Paired differential captures + DEBUG_ADDRESS traces + boundary sweep | VERIFIED | 21 files present: `test2_single_byte_write.txt`, `test3_debug_trace_1byte.txt`, `test4_page_at_0x1000.txt`, `test5_page_at_0x40000.txt`, `test_diag_0x*.txt` (7 files), `test_summary.txt`, test images (3 .bin), additional readback files |
| `93-VALIDATION.md` | Signed-off validation with nyquist_compliant: true + all 4 verification-map rows confirmed + evidence map | VERIFIED | frontmatter: `status: complete`, `nyquist_compliant: true`, `signed_off: 2026-06-27`; all 4 Per-Task rows show confirmed status; Evidence Map table present; Validation Sign-Off checklist all checked; Approval signed |

---

## Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `evidence/93-RCA-FINDINGS.md` | `evidence/safety/SAFE-01-PREFLIGHT.md` | SAFE-01 section references the preflight verdict | WIRED | Line 26: `See [SAFE-01-PREFLIGHT.md](safety/SAFE-01-PREFLIGHT.md)` in the SAFE-01 update header; further citations in SAFE-01 phase-close section with per-plan references |
| `evidence/93-RCA-FINDINGS.md` RCA-01 section | `evidence/signature/` raw captures | signature section cites the captured frame files | WIRED | Lines 85, 93, 123–129 cite specific files under `evidence/signature/` including `run1.txt`, `run2.txt`, `settled_read_0x0000ff.txt`, etc. |
| `evidence/93-RCA-FINDINGS.md` RCA-03 matrix | `evidence/differential/` raw captures | each matrix verdict cites its capture file | WIRED | Lines 216–220: each H1–H5 row cites a specific file under `differential/` (e.g. `differential/test2_single_byte_write.txt`, `differential/test3_debug_trace_1byte.txt`, `differential/test4_page_at_0x1000.txt`, etc.) |
| `93-VALIDATION.md` evidence map | `evidence/93-RCA-FINDINGS.md` | each requirement maps to a named section | WIRED | Lines 79–84 in VALIDATION.md: Evidence Map table links RCA-01/02/03/SAFE-01 each to their FINDINGS section with named evidence entries |

---

## Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|------------|-------------|--------|----------|
| RCA-01 | 93-02-PLAN.md | W29C040 page-0 write fault reproduced on seated chip with captured failure signature | SATISFIED | N=2 deterministic `ERROR: Timeout verifying 0x04 at 0x0000ff (got 0x00)` in `run1.txt`/`run2.txt`; H4 disconfirmed (settled read stays 0x00); bench discipline row recorded |
| RCA-02 | 93-03-PLAN.md | W29C040 write path differentially compared against W29C020 across all candidate axes | SATISFIED | Datasheet differential: SDP/pinout/VPP all SAME → exonerated; live bench disconfirmers: H1/H2/H3/H4 all disconfirmed; boot-block §6.6 isolation via boundary sweep; W29C020 live control deferred best-effort (explicitly documented, operator-authorized) |
| RCA-03 | 93-04-PLAN.md | Named root cause recorded, classified, sufficient to design a targeted fix | SATISFIED | H5 CONFIRMED (SILICON); H1–H4 all carry disconfirming bench evidence; Phase-94 hand-off with two action items and milestone done-bar impact |
| SAFE-01 | 93-01-PLAN.md + 93-04-PLAN.md | Over-voltage blocked at firmware VPP check; host guard never bypassed | SATISFIED (conditional) | `test_flash4_write_execute_no_vpp` PASSED; resolve_chip normal path; T-93-CANERASE FOUND + mitigated via `--skip-erase` throughout; SAFE-01 = HELD with documented caveat; FIX-01 deferred to Phase 94 |

**Orphaned requirements check:** All 4 requirement IDs (RCA-01, RCA-02, RCA-03, SAFE-01) appear in REQUIREMENTS.md and map to Phase 93 with status "Complete". No orphaned requirements.

---

## Raw Capture Spot-Checks

| Capture | Matches Cited Claim | Result |
|---------|---------------------|--------|
| `evidence/signature/run1.txt` | `ERROR: Timeout verifying 0x04 at 0x0000ff (got 0x00)` | VERIFIED — file contains exact ERROR string; exit code 1 |
| `evidence/signature/run2.txt` | Identical ERROR frame on Run 2 (N=2 determinism) | VERIFIED — identical frame present |
| `evidence/signature/settled_read_0x0000ff.txt` | Address 0x0000ff reads 0x00 stably N=5 | VERIFIED — 5 reads all return `000000ff: 00` |
| `evidence/differential/test2_single_byte_write.txt` | Single byte to 0x000000 FAILS with `Timeout verifying 0x39 at 0x000000 (got 0x00)` | VERIFIED — file contains exact ERROR string |
| `evidence/differential/test5_page_at_0x40000.txt` | A18=1 page write PASSES (Write successful) | VERIFIED — file shows `Write to W29C040 successful (0.09s)` |
| `evidence/differential/test_diag_0x3f00_result.txt` | 0x3F00 (last page in first 16K) FAILS | VERIFIED — `ERROR: Timeout verifying 0x03 at 0x003fff (got 0x00)` |
| `evidence/differential/test_diag_0x4000.txt` | 0x4000 (first page outside 16K) PASSES | VERIFIED — `Write to W29C040 successful (0.10s)` |
| `evidence/differential/test_summary.txt` | Boot-block lock pattern documented with exact 16K boundary | VERIFIED — matches all claimed test results; root cause statement consistent |

---

## Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `evidence/93-RCA-FINDINGS.md` | 40 | `TBD` in Plan 04 bench discipline log row | INFO | Plan 04 is explicitly autonomous synthesis (no bench hardware); the row stub is structurally correct — Plan 04 involved no bench session. No hardware was touched. The TBD cells are void-by-design, not a missing evidence gap. |

**Debt marker gate assessment:** The single `TBD` on line 40 is in the bench discipline log row for Plan 04, which is documented in the plan and summary as `autonomous: true` — no bench hardware involved. Plan 04's objective explicitly states "This is autonomous synthesis of evidence already captured — no new bench work." The TBD cells (timestamp, controller identity, port, R1/R2) are inapplicable to an autonomous plan; they are not missing evidence. This is NOT a blocker under the debt-marker gate rule because the context makes the void unambiguous — no bench session means no bench identity to record. No unreferenced unresolvable debt.

---

## W29C020 Live Differential — Scope Decision Assessment

The Plan 03 must-have stated: "The passing sibling W29C020 writes→auto-erases→verifies clean on the identical bench + firmware build (the differential control)."

**What happened:** The operator authorized a datasheet-only differential fallback because the W29C020 was not seated (operator cannot swap chips unattended). This is:
- Explicitly documented in `evidence/93-RCA-FINDINGS.md` §RCA-02: `OPERATOR_DECISION_SCOPE (2026-06-27): No live W29C020 write was performed`
- Marked `DEFERRED (best-effort)` in the findings
- Recorded in the 93-03-SUMMARY.md as a deliberate key decision
- Defensible: The datasheet analysis confirmed that SDP/pinout/VPP are identical between the two chips. The key differential was established by the live bench tests on the W29C040 itself (single-byte failure, A18=1 pass, boot-block boundary sweep), which together exonerate all axes that would have been tested by the W29C020 live write. The root cause (silicon boot-block lock) was confirmed without needing the live sibling.

**Assessment:** This is a legitimate, explicitly documented scope fallback. The RCA-02 requirement (isolate differing variable with exonerated unchanged axes) is satisfied by the combination of datasheet diff + live W29C040 disconfirming tests. The verification instructions explicitly accept this as a documented fallback.

---

## Milestone Done-Bar Impact (Informational — Not a Phase 93 Gap)

The v1.17 milestone done-bar (Phase 95 BENCH-01) requires a byte-exact full-image write→verify on the seated W29C040. The Phase 93 RCA established that:

- The **first 16K (0x0000–0x3FFF)** of the seated chip has the §6.6 boot-block programming lockout permanently (or reversibly, per the (a)/(b) fork) activated.
- Addresses **0x4000 and above** write and verify correctly with the current firmware.
- The lock reversibility fork (a) software-reversible vs (b) hardware-permanent is unresolved — Phase 94's first step must read W29C040.pdf §6.6 directly.

**Operator decision required at Phase 94:**
- If (a) UNLOCK command exists: Phase 94 can add unlock sequence; Phase 95 proceeds on the seated chip.
- If (b) no UNLOCK: Phase 95 needs either a different (unlocked) W29C040 sample OR the done-bar is re-scoped to addresses ≥ 0x4000. The write algorithm is proven correct for unlocked regions.

This is surfaced to the operator here as required. It is NOT a Phase 93 gap — the phase correctly identified the constraint and handed it off.

---

## Human Verification Required

None. All RCA evidence is programmatically verifiable: raw serial captures exist, line numbers are confirmed, boundary test results match claim. The bench was operator-witnessed (operator seating the chip and authorizing bench proceeds), but the captures are machine-readable and self-consistent.

---

## Gaps Summary

No gaps. All 4 ROADMAP Success Criteria are verified against actual recorded evidence in the codebase. The W29C020 live differential fallback is explicitly documented as operator-authorized scope. The Plan 04 TBD bench discipline row is void-by-design (autonomous plan). T-93-CANERASE is correctly recorded as a HIGH-severity finding with documented mitigation rather than being silently ignored.

---

_Verified: 2026-06-27T08:30:00Z_
_Verifier: Claude (gsd-verifier)_
