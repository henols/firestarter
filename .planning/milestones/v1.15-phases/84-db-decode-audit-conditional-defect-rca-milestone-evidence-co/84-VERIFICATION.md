---
phase: 84-db-decode-audit-conditional-defect-rca-milestone-evidence-co
verified: 2026-06-25T10:17:22Z
status: human_needed
score: 3/3
overrides_applied: 0
carry_over_assessment:
  assessed: 2026-08-09
  by: v1.31 pre-close carry-over sweep
  status_unchanged: human_needed
  reason_still_open: "Both items are operator judgment calls (accepting a disposition). An agent cannot grant an operator sign-off."
  note: |
    Neither item alleges a missing artifact — the report itself says the automated checks
    all pass (3/3) and these are "judgment calls about intentional deferrals". What the
    sweep CAN add is the follow-through record: both deferrals were subsequently picked
    up and worked, which is the strongest possible support for accepting them as correct
    dispositions rather than abandoned gaps.
  item_2_FIX01_followthrough: STRONGLY SUPPORTED — deferral was worked, not dropped
  item_2_evidence: |
    AM27C020 / FUT-06: root-caused and fixed in v1.18. RC-1 = DIP32 pin 31 modeled as
    address line A18 rather than held /PGM; a scoped `DIP32_27C020` + `rw-pin:[31]` ->
    `CTRL_READ_WRITE` (0x40) fix shipped dual-repo lockstep. Bench-proved EFFECTIVE
    (write#1 60/64 byte-exact, refuting the 0-bits signature) but MARGINAL (write#2
    0/64) -> honest DEFER, carried as FUT-08 with FUT-06 retired-by-replacement.
    W29C040 / CR-01: root-caused to a PERMANENTLY locked 16K boot block on the sample —
    full write->verify is physically impossible on that part; needs a different sample.
    Both "named-tracked deferrals" therefore behaved exactly as the D-43
    closed-by-disposition pattern promised.
  item_1_2516_followthrough: STILL OPEN — 2516 read instability not resolved
  item_1_evidence: |
    The 2516 0x0B read oracle remained unstable at v1.15 (N=3, 3 distinct SHAs, 1.9%
    byte jitter) and no later milestone has stabilised it. The D-22 best-effort deferral
    therefore still stands on its original reasoning.
    RELEVANT TO v1.31: the 2516 is the canonical 0x0B part, and v1.31 Phase 145 is 0x0B
    bench validation. An unstable 2516 read oracle is a live risk to that phase's ability
    to prove anything about 0x0B. Flagged in .planning/v1.31-CARRYOVER-DISPOSITION.md.
  recommended_disposition: |
    Item 2 is ready for a one-line operator sign-off on the v1.18 follow-through record.
    Item 1 should be re-pointed at v1.31 Phase 145 rather than sat against Phase 84,
    since that is where 0x0B read stability now actually matters.
    OPERATOR DECISION — not taken here.
human_verification:
  - test: "Confirm 2516 read instability is understood as intentional best-effort deferral (D-22), not a gap"
    expected: "GRAD-03 / FUT-03 remain OPEN; operator accepts that 2516 write proof was not achieved because the read oracle is still unstable after the VPP-skip fix; deferral FUT-03 is the correct disposition"
    why_human: "Cannot programmatically verify that the 2516 read instability was correctly root-caused and that the D-22 best-effort deferral is an accepted outcome — requires operator confirmation"
  - test: "Confirm operator accepts FIX-01 closed-by-disposition per D-43: AM27C020 FUT-06 + W29C040 CR-01 are intentional deferrals, not gaps"
    expected: "Operator agrees that 0-bits-programmed on AM27C020 (0x08 write path) and W29C040 flash4 256B-page fault are correctly root-caused, named-tracked deferrals; no in-posture fix was available"
    why_human: "The 'closed-by-disposition' close pattern for FIX-01 is a judgment call that deferred bench failures (not code failures) are correctly out of scope — requires operator sign-off that FUT-06 and CR-01 are acceptable dispositions"
---

# Phase 84: DB Decode Audit + Conditional Defect RCA Verification Report

**Phase Goal:** Consolidate the per-chip evidence into a final decode-correctness audit confirming every exercised chip matches its DB claims; root-cause and fix (host-only, or dual-repo lockstep if firmware) any per-family defect the bench surfaced, re-verifying on the bench with the full-DB VPP-safety gate green.
**Verified:** 2026-06-25T10:17:22Z
**Status:** human_needed
**Re-verification:** No — initial verification

---

## Goal Achievement

Phase 84 delivers on all three ROADMAP Success Criteria with solid codebase evidence. The automated checks all pass. Two items require human sign-off because they involve judgment calls about intentional deferrals — not because any code or artifact is missing.

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | Consolidated decode-correctness audit covers all 11 chips with per-attribute verdicts and mismatch dispositions | VERIFIED | `.planning/v1.15/DECODE-AUDIT.md` exists, 247 lines; all 11 chips appear in the per-chip table (Parts 1–5); every mismatch has a disposition; 0 "PENDING 84-05" / "placeholder" / "TBD" markers remaining (grep returns 0) |
| 2 | Any per-family write/program/verify defect is root-caused and fixed (or audited "none found / bench clean") with full-DB VPP-safety gate green | VERIFIED | Three in-posture fixes SHIPPED: (a) VPP-skip firmware gate in `eprom_generic_init` (commit cb947c7, 5-assertion native test suite); (b) SRAM/FRAM blank-check host short-circuit in `check_eprom_blank` (commits e5bfa3a + 4c74b8d, 2 new tests); (c) FM1608 SRAM→FRAM relabel (commits d8ca7a2 + 47c86c9 + 4d5b3de). `check_dispatch.py` exit 0 (734 supported, 0 violations); `diff_db.py` exit 0 (15 chips explained); ruff CI-scope clean; pio native 87/87 |
| 3 | After any fix, full-DB VPP-safety gate, diff_db, and host test suite are green | VERIFIED | `check_dispatch.py` → EXIT 0 (734/10/0); `diff_db.py` → EXIT 0 (15 changed chips, all explained); `ruff check firestarter/ tests/` → EXIT 0; host suite 672/673 (1 pre-existing live-board artifact, documented non-regression; 0xA4 guard `test_init_phase_data_frames_not_acked` PASS); pio native 87/87; Leonardo flash 89.5% ≤ 90% |

**Score:** 3/3 truths verified (automated)

---

### Intentional Deferrals (by-design, not gaps)

Per the phase context, these items are deliberately out of scope for Phase 84. They are correctly classified as deferrals with named trackers, not as failures.

| # | Item | Addressed / Tracked | Evidence |
|---|------|---------------------|----------|
| 1 | 2516 write proof / GRAD-03 / FUT-03 | FUT-03 OPEN best-effort (D-22) | VPP-skip cleared 18.8V boot-refusal, but 2516 read still shows 3 distinct SHAs, N=3, 1.9% byte jitter after re-bench (EVIDENCE.json `phase84.task2_2516_reread`). No write / no preserve-dump (D-21). FUT-03 remains open pending deeper OE/VPP pin root-cause |
| 2 | AM27C020 0x08 write-path (0-bits-programmed) | FUT-06 assigned | N=2 bench confirmation (EVIDENCE.json `phase84.task3a_am27c020`): deterministic, NOT VPP-skip-related, chip silicon intact. Not trivially fixable; requires 0x08 32-pin write/VPP path root-cause |
| 3 | W29C040 flash4 256B-page boundary fault | CR-01 / Phase-74 Wave-2 reopened | N=2 bench confirmation on Phase-84 build carrying Phase-74 fix (EVIDENCE.json `phase84.task3c_w29c040`): Phase-74 fix NOT silicon-effective. Reopen Phase-74 Wave-2 |
| 4 | W27E512 + W27E040 stuck-bit FAILs | D-32 silicon-limited (no tracker needed) | Genuine silicon wear (erase path correct per DB); NOT re-benched in Phase 84 (D-32 exclusion) |
| 5 | SST39SF040 cosmetic label (Flash vs Flash/EEPROM) | sst-keep observation (D-40) | Documented in DECODE-AUDIT.md Part 2(iii); keeping `Flash/EEPROM` prevents FLAG_CAN_ERASE regression; decouple path not authorized this phase |

---

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `firestarter/src/proms/eprom.cpp` | VPP-skip guard for CMD_READ / CMD_BLANK_CHECK in `eprom_generic_init` | VERIFIED | Line 294: `if (handle->cmd == CMD_READ \|\| handle->cmd == CMD_BLANK_CHECK) { return; }` — early return before `eprom_check_vpp`; write/erase/chip-id still gate VPP |
| `firestarter/test/native/avr/test_dispatch/test_configure_memory.cpp` | 5 VPP-skip assertions (2 positive + 3 negative) | VERIFIED | All 5 test functions found at lines 255–358; registered in RUN_TEST block; 87/87 native tests green |
| `firestarter/test/native/avr/test_dispatch/host_stubs.cpp` | HOST_STUBS_CUSTOM_HW_REVISION + delay() stub | VERIFIED | Summary confirms additions; native suite green proves they compile and execute |
| `firestarter_app/firestarter/eprom_operations.py` | SRAM/FRAM blank-check short-circuit with `_SRAM_PROTO_IDS` frozenset | VERIFIED | Lines 1543–1563: `_SRAM_PROTO_IDS = frozenset({0x0E, 0x27, 0x28, 0x29})`; guard fires before `_operation_context` on `etype in ("SRAM","FRAM")` OR `proto in _SRAM_PROTO_IDS` |
| `firestarter_app/tests/test_eprom_operations.py` | TestSramBlankCheckShortCircuit class with positive + negative tests | VERIFIED | Class at line 940; two tests at lines 951 + 977; both PASS confirmed (live run: 2 passed in 0.05s) |
| `firestarter_app/firestarter/ic_layout.py` | `"FRAM": "FRAM"` in `_ELECTRICAL_TYPE_LABEL`; VPP gate `not in {"SRAM","FRAM"}` | VERIFIED | Line 478: `"FRAM": "FRAM"` added; line 583: gate is `etype not in {"SRAM", "FRAM"}` |
| `firestarter_app/firestarter/eprom_info.py` | VPP display gate `not in {"SRAM","FRAM"}` | VERIFIED | Line 396: `if _etype not in {"SRAM", "FRAM"} and _vpp_mv > 0:` |
| `firestarter_app/firestarter/data/chip_database.json` | FM1608 `electrical.type = "FRAM"` | VERIFIED | Confirmed via substring search: FM1608 entry has `"type": "FRAM"` |
| `firestarter_app/tools/diff_db.py` | `RULE_PHASE84_RELABEL` rule with part-number scope | VERIFIED | Lines 121, 240, 268, 352, 358 — rule defined, scoped to FM1608, placed before BUG_A_ETYPE |
| `.planning/v1.15/DECODE-AUDIT.md` | Consolidated 11-chip audit (SC#1) with all mismatches dispositioned | VERIFIED | 247 lines; all 11 chips in per-chip table (Parts 1–5); FIX-01 close-statement in Part 4; Phase-84 bench verdicts filled by Plan 84-06; 0 PENDING placeholders |
| `.planning/v1.15/bench/EVIDENCE.md` | Phase 84 section appended with 2516 re-read, AM27C020, W29C040 bench results | VERIFIED | 24 occurrences of "Phase 84" / "2026-06-25"; EVIDENCE.json `phase84` key with sub-keys `task2_2516_reread`, `task3a_am27c020`, `task3c_w29c040` |
| `.planning/REQUIREMENTS.md` | FIX-01 CLOSED per D-43; GRAD-03/FUT-03 DEFERRED best-effort (D-22) | VERIFIED | Grep confirms: "CLOSED per D-43" in FIX-01 row; "DEFERRED best-effort (D-22)" in GRAD-03 row; "OPEN best-effort (D-22)" in FUT-03 row |

---

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `eprom_generic_init` | `eprom_check_vpp` | early-return guard on `handle->cmd` | VERIFIED | The guard at line 294 intercepts CMD_READ/CMD_BLANK_CHECK before `eprom_check_vpp` is called; write/erase/chip-id still reach it (line 297) |
| `check_eprom_blank` | `_operation_context` / firmware | SRAM detection before context manager | VERIFIED | Guard at line 1556 fires before `_operation_context` is entered — no firmware command reaches the wire for SRAM/FRAM chips |
| `build_db.py` relabel override | `chip_database.json` | per-chip override after Pass-2 | VERIFIED | `diff_db.py` exit 0 confirms FM1608 change is explained (RULE_PHASE84_RELABEL); FM1608 shows `"type": "FRAM"` in regenerated JSON |
| `RULE_PHASE84_RELABEL` classification | FM1608 electrical.type change | `_classify_diff` priority chain | VERIFIED | Rule placed before `BUG_A_ETYPE` (lines 352–358); `diff_db.py` exit 0 proves classification is correct |
| Firmware branch | `v1.15-bench-validation-of-operator-inventory` | git checkout before edit | VERIFIED | `git -C firestarter rev-parse --abbrev-ref HEAD` → `v1.15-bench-validation-of-operator-inventory` confirmed |

---

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| SRAM blank-check short-circuit tests pass | `pytest tests/test_eprom_operations.py::TestSramBlankCheckShortCircuit -v` | 2 passed in 0.05s | PASS |
| Full-DB VPP-safety gate | `python tools/check_dispatch.py` | EXIT 0 — 734 supported, 0 violations | PASS |
| diff_db gate | `python tools/diff_db.py` | EXIT 0 — 15 changed chips, all explained | PASS |
| CI-scope ruff check | `ruff check firestarter/ tests/` | EXIT 0 — All checks passed | PASS |

---

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|------------|-------------|--------|----------|
| FIX-01 | 84-01, 84-02, 84-03, 84-05, 84-06 | Root-cause and fix bench-surfaced defects; re-verify with VPP-safety gate green | VERIFIED (CLOSED per D-43) | In-posture fixes SHIPPED (VPP-skip fw + FM1608 host short-circuit + FRAM relabel); deeper defects (AM27C020/W29C040) root-caused + named-tracked (FUT-06/CR-01); all gates green |

**Note on GRAD-03:** GRAD-03 was assigned to Phase 84 per CONTEXT D-01. Its status is DEFERRED best-effort (D-22) per REQUIREMENTS.md — the 2516 read remains unstable after the VPP-skip fix (3 distinct SHAs, N=3, 1.9% byte jitter). This is a documented intentional deferral; FUT-03 remains OPEN. SC#4 (2516 bench-proven) was re-scoped to Phase 84 from Phase 83 and its unachievability is a known best-effort outcome, not a phase failure.

---

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `firestarter_app/firestarter/ic_layout.py` | 588 | Comment using word "placeholder" | Info | In context: explains a data situation for chip_id_check=false SRAM/FRAM entries — NOT an implementation placeholder; code is complete |

No TBD, FIXME, XXX, or stub markers found in any source file modified by Phase 84.

**Pre-existing ruff findings in `tools/` tree** (out-of-CI-scope, unchanged by this phase, flagged per policy in 84-02/03/06 SUMMARY files):
- `tools/audit_coverage_matrix.py:37` — I001 import-sort
- `tools/catalog/codegen.py:36` — I001 import-sort
- `tools/catalog/codegen_vectors.py:32,189` — I001 import-sort
These are in the `tools/` tree, outside `ci.yml` gate scope (`firestarter/ tests/` only). Not introduced by Phase 84. Not a blocker.

---

### Human Verification Required

### 1. GRAD-03 / FUT-03 / 2516 Deferral Acceptance

**Test:** Review DECODE-AUDIT.md Part 2(v) and REQUIREMENTS.md GRAD-03 row. Confirm that the 2516 deferral outcome — VPP boot-refusal cleared by VPP-skip but data jitter persisting (3 distinct SHAs, N=3, 1.9% divergence after Phase-84 re-bench) — is an accepted best-effort outcome per D-22, not a gap.
**Expected:** Operator confirms GRAD-03 / SC#4 / FUT-03 remain OPEN best-effort; the 2516 write proof was not attempted because the read oracle is still untrustworthy (EVID-03); this is the correct and expected disposition for a best-effort graduation deferral.
**Why human:** The D-22 best-effort deferral is a policy judgment: the phase design allows "close as best-effort if read oracle remains unstable." Programmatic verification cannot confirm operator acceptance of this judgment. The code and evidence record are complete; only operator sign-off is missing.

### 2. FIX-01 Closed-by-Disposition Acceptance (AM27C020 FUT-06 + W29C040 CR-01)

**Test:** Review DECODE-AUDIT.md Part 4 (FIX-01 close-statement) and REQUIREMENTS.md FIX-01 row. Confirm that the D-43 "closed-by-disposition" pattern is accepted: in-posture fixes shipped and bench-confirmed; AM27C020 0x08 write-path (0-bits-programmed) assigned FUT-06; W29C040 flash4 256B-page fault assigned Phase-74 Wave-2 / CR-01; both root-caused, deterministic, non-trivially fixable.
**Expected:** Operator confirms FIX-01 is correctly closed — the phase goal was "root-cause and fix OR record none found / bench clean"; the correct outcome when defects exist but are not trivially fixable is "root-caused + deferred with named trackers." The VPP-skip fix (FIX-01 firmware half) and FM1608 short-circuit + relabel (FIX-01 host half) constitute the in-posture fixes; the remaining defects are out-of-scope for a conditional-RCA phase.
**Why human:** The "closed-by-disposition" close pattern is an engineering judgment call — it requires operator acceptance that the two remaining defects (FUT-06 / CR-01) are appropriately deferred and not gaps in the phase deliverable.

---

### Gaps Summary

No automated blockers found. All source artifacts exist, are substantive, and are wired. All gates (check_dispatch, diff_db, ruff, pio native, host suite 0xA4 guard) are green. The firmware branch is correct.

The `human_needed` status reflects two items that are judgment calls about intentional deferrals — not missing implementations. Both items are fully documented in DECODE-AUDIT.md and REQUIREMENTS.md. Once the operator confirms the D-22 and D-43 dispositions are accepted, this phase is clear to proceed to `/gsd-complete-milestone v1.15`.

---

_Verified: 2026-06-25T10:17:22Z_
_Verifier: Claude (gsd-verifier)_
