---
phase: 73-bench-validate-the-6-families-on-leonardo-hybrid-gated
verified: 2026-06-18T07:15:00Z
status: passed
score: 4/4 must-haves verified
overrides_applied: 0
---

# Phase 73: Bench-Validate the 6 Families on Leonardo (hybrid-gated) Verification Report

**Phase Goal:** The validation matrix is populated with real evidence — every family's Tier-1/Tier-2 software cells run, and the Tier-3 HIL cells run on Leonardo for the families with chips + a working shield on hand (others recorded SKIP-deferred) — and the SRAM empty-no-op question is resolved, classifying SRAM as a table-stakes PASS or as a FIX-01 correctness defect.
**Verified:** 2026-06-18T07:15:00Z
**Status:** passed
**Re-verification:** No — initial verification

---

## Goal Achievement

### Observable Truths (ROADMAP Success Criteria)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | All six families have GREEN Tier-1 native + Tier-2 host wire round-trip cells | VERIFIED | 73-01-SUMMARY: 28 Tier-1 + 26 Tier-2 tests passed; 6 families each confirmed |
| 2 | Each family with chips on hand has a Tier-3 Leonardo cell with independent post-write read + SHA + passing negative control; chipless families are SKIP-deferred with reason | VERIFIED | eprom=PASS (authoritative, SHA recorded, neg ctrl exit 1); flash3=PASS (SST39SF040 bonus, authoritative, neg ctrl); flash4=FAIL (authoritative, W29C040 hw-error, neg ctrl); sram=PASS (authoritative, two-pattern); eeprom28c/flash_intel=SKIP-deferred with recorded reason |
| 3 | Every Tier-3 cell records live R1/R2 readback (r1≈270000) + retry count; no uno328pb program/write cell recorded as PASS | VERIFIED | Pre-write gate confirmed at each task start; R1=270000 in-band; uno328pb cells are N/A in all matrices |
| 4 | VAL-06 SRAM no-op question resolved with bench evidence — definitive verdict (table-stakes-PASS or FIX-01), never SKIP-deferred or inconclusive | VERIFIED | val06-perbyte-verdict.txt contains "VAL-06 = table-stakes-PASS"; sram validation-matrix.json: verdict=PASS, pass_type=authoritative, retry_count=2; two-pattern A/B N=2 zero mismatches; D-09 hard gate satisfied |

**Score:** 4/4 truths verified

---

### Per-Requirement Verdict Table

| Req ID | Family | Expected Tier-3 State | Actual (from JSON on disk) | Status |
|--------|--------|-----------------------|---------------------------|--------|
| VAL-01 | eprom (W27C512) | PASS | PASS, pass_type=authoritative, evidence_sha=9521375d…, retry_count=1 | VERIFIED |
| VAL-02 | eeprom28c | SKIP-deferred (no chip) | SKIP-deferred, reason="no board/chip/source provided" | VERIFIED |
| VAL-03 | flash3 (SST39SF040 bonus) | PASS (bonus chip substitution per phase context) | PASS, pass_type=authoritative, chip=SST39SF040, evidence_sha=c19c3e07…, retry_count=1 | VERIFIED |
| VAL-04 | flash4 (W29C040) | FAIL (valid per D-12) | FAIL, pass_type=authoritative, Phase-74 reason documented | VERIFIED |
| VAL-05 | flash_intel | SKIP-deferred (no chip) | SKIP-deferred, reason="no board/chip/source provided" | VERIFIED |
| VAL-06 | sram (FM1608) | PASS (table-stakes-PASS, hard gate D-09) | PASS, pass_type=authoritative, evidence_sha=1ae62b31…, retry_count=2, two-pattern confirmed | VERIFIED |

---

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `firestarter_app/val-results/eprom/validation-matrix.json` | Tier-3 PASS, authoritative pass_type, evidence_sha | VERIFIED | family=eprom, board=leonardo, verdict=PASS, pass_type=authoritative, evidence_sha present |
| `firestarter_app/val-results/eeprom28c/validation-matrix.json` | Tier-3 SKIP-deferred | VERIFIED | verdict=SKIP-deferred, reason recorded |
| `firestarter_app/val-results/flash3/validation-matrix.json` | Tier-3 PASS (SST39SF040, bonus) | VERIFIED | verdict=PASS, pass_type=authoritative, chip=SST39SF040, note documenting bonus run |
| `firestarter_app/val-results/flash4/validation-matrix.json` | Tier-3 FAIL (W29C040, valid per D-12) | VERIFIED | verdict=FAIL, pass_type=authoritative, Phase-74 reason recorded |
| `firestarter_app/val-results/flash_intel/validation-matrix.json` | Tier-3 SKIP-deferred | VERIFIED | verdict=SKIP-deferred, reason recorded |
| `firestarter_app/val-results/sram/validation-matrix.json` | Tier-3 PASS, authoritative, retry_count=2 | VERIFIED | verdict=PASS, pass_type=authoritative, retry_count=2, method=two-pattern, FM1608 noted |
| `firestarter_app/val-results/sram/val06-perbyte-verdict.txt` | Contains "VAL-06 = table-stakes-PASS" | VERIFIED | File exists, 4827 bytes; contains "VAL-06 = table-stakes-PASS" at lines 79, 105, 114 |
| `firestarter_app/val-results/sram/fm1608-baseline.bin` | 8192 bytes | VERIFIED | 8192 bytes confirmed |
| `firestarter_app/val-results/sram/pattern_a.bin` | 8192 bytes, non-trivial | VERIFIED | 8192 bytes; 0x5A repeating (non-trivial, non-0x00/0xFF) |
| `firestarter_app/val-results/sram/pattern_b.bin` | 8192 bytes, non-trivial, distinct from A | VERIFIED | 8192 bytes; 0xA5 repeating (bitwise complement of A — maximum separation) |
| `firestarter_app/val-results/sram/readback_a_run1.bin` | 8192 bytes | VERIFIED | 8192 bytes confirmed |
| `firestarter_app/val-results/sram/readback_b_run1.bin` | 8192 bytes | VERIFIED | 8192 bytes confirmed |
| `firestarter_app/val-results/sram/readback_a_run2.bin` | 8192 bytes | VERIFIED | 8192 bytes confirmed |
| `firestarter_app/val-results/sram/readback_b_run2.bin` | 8192 bytes | VERIFIED | 8192 bytes confirmed |
| `firestarter_app/val-results/eprom/w27c512-source.bin` | 65536 bytes (W27C512 image) | VERIFIED | 65536 bytes confirmed |
| `firestarter_app/val-results/eprom/w27c512-wrongfile.bin` | 65536 bytes (negative control image) | VERIFIED | 65536 bytes confirmed |

---

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `dev validate-family eprom --board leonardo --chip W27C512` | `val-results/eprom/validation-matrix.json` | write_cycle_eprom → verdict mapped | VERIFIED | JSON cell records verdict=PASS, pass_type=authoritative |
| `dev validate-family flash3 --board leonardo --chip SST39SF040` | `val-results/flash3/validation-matrix.json` | bonus bench run post-plan, same runner | VERIFIED | JSON cell records verdict=PASS, chip=SST39SF040, note documents bonus |
| `dev validate-family flash4 --board leonardo --chip W29C040` | `val-results/flash4/validation-matrix.json` | write_cycle_eprom exit code 2 → FAIL | VERIFIED | JSON cell records verdict=FAIL with hw-error detail and Phase-74 route |
| `firestarter write FM1608 pattern_{a,b}.bin -b` → readback compare | `val-results/sram/val06-perbyte-verdict.txt` + `validation-matrix.json` | two-pattern N=2 per-byte D-08 logic | VERIFIED | perbyte file shows 0 mismatches on all 4 (pattern, run) pairs; matrix records PASS |
| `dev validate-family eeprom28c` (no --board) | `val-results/eeprom28c/validation-matrix.json` | auto-SKIP-deferred path, no chip | VERIFIED | verdict=SKIP-deferred |
| `dev validate-family flash_intel` (no --board) | `val-results/flash_intel/validation-matrix.json` | auto-SKIP-deferred path, no chip | VERIFIED | verdict=SKIP-deferred |

---

### Data-Flow Trace (Level 4)

This is a hardware bench-validation phase, not a software data-rendering phase. The "data" is the raw bytes written to and read back from physical chips, captured in committed binary artifacts and summarized in JSON verdict files. The relevant Level 4 check is whether the JSON verdict accurately reflects what the bench actually recorded:

| Artifact | Data Variable | Source | Produces Real Data | Status |
|----------|---------------|--------|--------------------|--------|
| `eprom/validation-matrix.json` | verdict=PASS | `dev validate-family eprom` runner — `write_cycle_eprom` erase+write+SHA compare exit 0 | YES — evidence_sha matches w27c512-source.bin SHA256 | FLOWING |
| `flash3/validation-matrix.json` | verdict=PASS | bonus `dev validate-family flash3` runner — SST39SF040 erase+write+SHA compare exit 0 | YES — evidence_sha matches sst39sf040-source.bin SHA256 | FLOWING |
| `flash4/validation-matrix.json` | verdict=FAIL | `dev validate-family flash4` runner — exit code 2 (hw-error); fallback write also failed | YES — reason field documents chip behavior at 0x000000 | FLOWING |
| `sram/validation-matrix.json` | verdict=PASS | two-pattern write+read-back N=2 via `firestarter write FM1608 -b` + `firestarter read FM1608` | YES — readback bin files present (8192 bytes each); perbyte file shows 0 mismatches | FLOWING |
| `sram/val06-perbyte-verdict.txt` | VAL-06 = table-stakes-PASS | per-byte comparison of readback bins vs pattern bins | YES — zero mismatches across 4 (pattern, run) combinations documented with offsets | FLOWING |

---

### Behavioral Spot-Checks

Step 7b is partially applicable to this hardware bench phase. The runnable checks are the JSON schema validations; the hardware runs themselves cannot be re-executed without physical hardware.

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| eprom cell has correct fields | `python3 -c "import json; c=json.load(open('…/eprom/validation-matrix.json')); cell=[x for x in c['cells'] if x['family']=='eprom' and x['board']=='leonardo']; assert cell[0]['verdict']=='PASS' and cell[0]['pass_type']=='authoritative'"` | assertion passes | PASS |
| sram cell has retry_count=2 and verdict=PASS | `python3 -c "import json; c=json.load(open('…/sram/validation-matrix.json')); cell=[x for x in c['cells'] if x['family']=='sram' and x['board']=='leonardo']; assert cell[0]['retry_count']==2 and cell[0]['verdict']=='PASS'"` | assertion passes | PASS |
| val06 perbyte file contains definitive verdict | `grep -Eq 'VAL-06 *= *(table-stakes-PASS\|FIX-01)' val06-perbyte-verdict.txt` | matches "VAL-06 = table-stakes-PASS" | PASS |
| All 7 sram binary artifacts are 8192 bytes | `stat -c%s` on each bin | all return 8192 | PASS |
| eeprom28c and flash_intel are SKIP-deferred | python3 JSON parse | both verdict=SKIP-deferred | PASS |
| flash4 verdict is FAIL with authoritative pass_type | python3 JSON parse | verdict=FAIL, pass_type=authoritative | PASS |

---

### Requirements Coverage

| Requirement | Phase | Source Plan | Status | Evidence |
|-------------|-------|-------------|--------|----------|
| VAL-01 | 73 | 73-02-PLAN.md | SATISFIED | eprom/validation-matrix.json: verdict=PASS, pass_type=authoritative, evidence_sha |
| VAL-02 | 73 | 73-01-PLAN.md | SATISFIED | eeprom28c/validation-matrix.json: verdict=SKIP-deferred (valid per D-02/D-13) |
| VAL-03 | 73 | 73-03-PLAN.md | SATISFIED | flash3/validation-matrix.json: verdict=PASS via SST39SF040 bonus (same configure_flash3/0x06 family) |
| VAL-04 | 73 | 73-01-PLAN.md (SKIP initial) + 73-03-PLAN.md (upgraded to real run) | SATISFIED | flash4/validation-matrix.json: verdict=FAIL (valid per D-12, routes to Phase 74) |
| VAL-05 | 73 | 73-01-PLAN.md | SATISFIED | flash_intel/validation-matrix.json: verdict=SKIP-deferred (valid per D-02/D-13) |
| VAL-06 | 73 | 73-04-PLAN.md | SATISFIED | sram/validation-matrix.json: verdict=PASS, retry_count=2; val06-perbyte-verdict.txt: "VAL-06 = table-stakes-PASS"; D-09 hard gate met |

All 6 requirements claimed by Phase 73 plans are satisfied. No orphaned requirements found — REQUIREMENTS.md maps VAL-01..VAL-06 exclusively to Phase 73, and all are now marked Complete.

---

### Anti-Patterns Found

No TBD, FIXME, or XXX markers found in any file modified by this phase. No stub patterns found in the JSON artifacts. All verdict fields contain real bench-derived values, not placeholders.

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| (none) | — | — | — | — |

---

### Noteworthy Deviations (Not Defects)

The following deviations from original plans occurred during execution. All are documented in SUMMARYs, are legitimate per the phase CONTEXT decisions, and do NOT affect the phase goal:

1. **flash3 plan target replaced by SST39SF040 (bonus run):** Plan 73-03 targeted AM29F040. No AM29F040 was available; the operator had W29C040 (flash4 family) seated. The plan executed as: flash3/VAL-03 recorded SKIP-deferred (no AM29F040), flash4/VAL-04 upgraded from SKIP-deferred to a real FAIL run on W29C040. Subsequently, a bonus SST39SF040 bench run upgraded flash3/VAL-03 from SKIP-deferred to authoritative PASS. Both SST39SF040 and AM29F040 use configure_flash3/algorithm 0x06 — the substitution is family-equivalent. The phase context explicitly permits this pattern (D-12/D-13).

2. **flash4 verdict is FAIL, not PASS:** A FAIL is a valid VAL outcome per D-12. The FAIL records a real algorithmic incompatibility finding (configure_flash4 erase+write vs W29C040 SDP/page-write timing), routes to Phase 74 for investigation. This is not a phase gap.

3. **W27C020 bonus run attempted and reverted in 73-02:** The operator attempted a bonus W27C020 eprom run that was aborted mid-run due to an API outage. The partial state was reverted; the eprom/validation-matrix.json shows only the canonical W27C512 VAL-01 PASS cell. The revert is confirmed — no W27C020 artifacts are present in val-results/eprom/.

4. **R1 persistence mechanism:** The `firestarter config -r1 270000` command writes to Arduino EEPROM only, not to local JSON. The plan's Task 2 auto-corrected by writing r1=270000 directly to ~/.firestarter/config.json. This is documented as a "Rule 1 - Bug" deviation in 73-01-SUMMARY and the fix is correct.

---

### Human Verification Required

None. This phase is a hardware bench-validation phase. All required verdicts have been recorded in committed artifacts on disk. The bench hardware runs are complete and their results are captured in binary artifacts + JSON verdict files. No additional human testing is needed to confirm the phase goal.

The operator authorized all chip-substitution and session decisions at execution time (2026-06-17). The phase is closed.

---

## Conclusion

Phase 73's goal is fully achieved. All four ROADMAP success criteria are verified:

- SC#1: 28 Tier-1 + 26 Tier-2 tests GREEN across all 6 families — confirmed from 73-01-SUMMARY execution results.
- SC#2: All 6 families have recorded Tier-3 Leonardo cells (eprom=PASS, flash3=PASS, flash4=FAIL, sram=PASS, eeprom28c=SKIP-deferred, flash_intel=SKIP-deferred). On-hand families have authoritative pass_type + evidence_sha + passing negative control. Chipless families have explicit SKIP-deferred reason. The phase is closeable at this partial coverage (D-13).
- SC#3: Live R1 precondition (r1≈270000) confirmed at every pre-write gate; retry_count recorded in every cell; uno328pb=N/A in all matrices.
- SC#4: VAL-06 hard gate (D-09) satisfied — definitive verdict "VAL-06 = table-stakes-PASS" in val06-perbyte-verdict.txt and sram validation-matrix.json (verdict=PASS, pass_type=authoritative, retry_count=2). FIX-01 is closed not-needed with evidence. Phase 74 SRAM scope is eliminated.

All 6 VAL requirements are satisfied. The matrix is fully populated. Phase 74 receives a clear scope: flash4 configure_flash4 algorithm investigation (W29C040 SDP/page-write compatibility); SRAM FIX-01 is not needed.

---

_Verified: 2026-06-18T07:15:00Z_
_Verifier: Claude (gsd-verifier)_
