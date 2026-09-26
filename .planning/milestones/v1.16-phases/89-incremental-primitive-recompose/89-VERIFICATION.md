---
phase: 89-incremental-primitive-recompose
verified: 2026-06-26T11:35:19Z
status: passed
score: 8/8 must-haves verified
overrides_applied: 1
operator_resolutions:
  - item: "ROADMAP SC#4 — eprom_write_execute verify_and_update_mask not routed through poll_readback"
    decision: "ACCEPTED scope narrowing + D-02 deferral (operator, 2026-06-26)"
    rationale: "verify_and_update_mask is a genuinely different algorithm (whole-buffer bitmask, returns a count, no timeout frame / no error MSG). Routing it through the single-address poll_readback kernel would CHANGE behavior, violating the behavior-preserving contract. The exclusion was plan 89-04's explicit design decision and was independently corroborated by the code reviewer. Recorded as a D-02 deferral note in 89-04-SUMMARY.md; ROADMAP SC#4's third site is treated as aspirational wording, not a defect. Truth #4 and PRIM-05 are accepted as SATISFIED on this basis."
---

# Phase 89: Incremental Primitive Recompose — Verification Report

**Phase Goal:** Shared primitives are extracted from the duplicated handlers in biggest-saving-first order (P7 → P4 → P3 → P5), each step guarded so the refactor is independently reversible and the native golden traces stay green, with Leonardo flash net-decreasing.
**Verified:** 2026-06-26T11:35:19Z
**Status:** passed (operator-resolved SC#4 scope, 2026-06-26)
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|---------|
| 1 | P7 dedup: FLASH_ENABLE_WRITE_PROTECTION and EEPROM_SDP_DISABLE duplicates removed; eeprom_28c redirected to FLASH_DISABLE_WRITE_PROTECTION | VERIFIED | grep returns 0 for both symbols in src/include; FLASH_DISABLE_WRITE_PROTECTION in eeprom_28c.cpp:101; commit 0052c42 |
| 2 | P4 chip_id_report: new primitives module created; shared report tail serves all four call sites; CR-01 behavioral regression fixed (eprom CHECK_CHIP_ID path restored to unconditional ERROR) | VERIFIED | primitives.h declares void chip_id_report(handle, read_id, bool force_warning); primitives.cpp implements it with force_warning param (not FLAG_FORCE); eprom.cpp:317 passes error_code==RESPONSE_CODE_WARNING; commits a10871d + a296195 |
| 3 | P3 vpp_check_window: shared window body extracted; regulator routing, REV0 guard, and trailing clear stay handler-local; D-06 protocol keying NOT moved into primitive | VERIFIED | vpp_check_window in primitives.cpp:93 contains no REGULATOR references (grep = 0); eprom.cpp:272 still has protocol==0x0B keying; eprom.cpp:280 calls vpp_check_window; flash_intel.cpp:64 calls vpp_check_window; commit a52fd0a |
| 4 | P5 poll_readback: shared bounded poll kernel used by eeprom28c + flash4; iteration caps and per-site error frame byte orders preserved; eprom verify_and_update_mask untouched | VERIFIED (operator-resolved) | eeprom_28c.cpp:128 and flash_type_4.cpp:123 call poll_readback with correct caps (2000/1024); error frames stay in callers (addr-first vs expected-first confirmed); eprom.cpp poll_readback count=0; verify_and_update_mask count=2 (unchanged). ROADMAP SC#4's third site (eprom_write_execute verify) is a different algorithm — ACCEPTED as a D-02 scope narrowing by operator 2026-06-26 (see operator_resolutions + 89-04-SUMMARY D-02 note). Commit abbbb5c. |
| 5 | All native golden traces stay byte-identical at every extraction step (zero-diff) | VERIFIED | 105/105 tests PASS (pio test -e native confirmed live); test_val_eprom, test_val_flash_intel, test_val_eeprom28c, test_val_flash3, test_val_flash4, test_val_sram all PASSED |
| 6 | Leonardo flash net-decreasing: final bytes strictly below 25654 B Phase-88 baseline | VERIFIED | pio run -e leonardo: 25136 bytes (87.7%); 25136 < 25654; net delta = -518 B; D-01 PASS. (Note: ledger records 25090 B at abbbb5c; CR-01 fix added +46 B. Both values are net decreases from baseline.) |
| 7 | check_dispatch.py exits 0 violations, diff_db.py is empty (identity diff) at phase close — SAFE-03 | VERIFIED | check_dispatch.py: 746 chips, 0 dispatch regressions, 0 consistency violations; diff_db.py: 0 changed / 0 new / 0 missing |
| 8 | All 9 INV-01..09 ids greppable in >=3 files across doc/src/test (SAFE-02) | VERIFIED | INV-01=9, INV-02=3, INV-03=6, INV-04=4, INV-05=3, INV-06=3, INV-07=3, INV-08=3, INV-09=5 — all >= 3 |

**Score:** 8/8 truths verified (truth #4 SC#4 eprom-site scope narrowing ACCEPTED + D-02 by operator 2026-06-26)

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `firestarter/include/primitives.h` | Declarations-only header with chip_id_report, poll_readback, vpp_check_window | VERIFIED | Exists; __PRIMITIVES_H__ guard; extern "C"; 3 functions declared with full doc comments including CR-01 rationale |
| `firestarter/src/proms/primitives.cpp` | Implementations of all 3 primitives | VERIFIED | Exists; chip_id_report (force_warning param), poll_readback (bool return + observed_out), vpp_check_window (D-08 +500 threshold present at line 106) |
| `.planning/phases/89-incremental-primitive-recompose/89-FLASH-LEDGER.md` | Per-step flash ledger + final % + disposition (PRIM-06) | VERIFIED | Exists; contains "Final flash" marker; step table P7/P4/P3/P5 with bytes/delta/disposition; 25090 B final (pre-CR-01 snapshot) + net-decrease assertion PASS. Note: actual HEAD flash is 25136 B after the post-phase CR-01 fix; -518 B net decrease still holds. |
| `firestarter/src/proms/eprom.cpp` | CR-01 fix: eprom_internal_check_chip_id passes error_code-keyed force_warning | VERIFIED | eprom.cpp:317 calls chip_id_report(handle, eprom_get_chip_id(handle), error_code == RESPONSE_CODE_WARNING); CHECK_CHIP_ID caller at :139 passes RESPONSE_CODE_ERROR unconditionally |
| WR-02 tests in test_val_eprom | 3 mismatch-fork tests (test_wr02a/b/c) | VERIFIED | test_val_eprom.cpp:621 test_wr02a (force_warning=false always ERRORs even with FLAG_FORCE), :662 test_wr02b (force_warning=true yields WARNING), :688 test_wr02c (generic-init without FORCE yields ERROR); all 3 in RUN_TEST at :734-736 |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `eeprom_28c.cpp` | `primitives.cpp` | chip_id_report(handle, chip_id, is_flag_set(FLAG_FORCE)) | WIRED | eeprom_28c.cpp:91 |
| `flash_intel.cpp` | `primitives.cpp` | chip_id_report(handle, chip_id, is_flag_set(FLAG_FORCE)) | WIRED | flash_intel.cpp:176 |
| `flash_utils.cpp` | `primitives.cpp` | chip_id_report(handle, flash_util_get_chip_id(handle), is_flag_set(FLAG_FORCE)) | WIRED | flash_utils.cpp:107 |
| `eprom.cpp` | `primitives.cpp` | chip_id_report via eprom_internal_check_chip_id; force_warning = error_code==RESPONSE_CODE_WARNING | WIRED | eprom.cpp:317; CHECK_CHIP_ID path gets false (ERROR); generic-init path gets FLAG_FORCE-derived value |
| `eprom.cpp` | `primitives.cpp` | vpp_check_window(handle) from eprom_check_vpp | WIRED | eprom.cpp:280; protocol keying + regulator enable before, trailing clear after |
| `flash_intel.cpp` | `primitives.cpp` | vpp_check_window(handle) from flash_intel_check_vpp | WIRED | flash_intel.cpp:64; no trailing clear (caller holds VPP) |
| `eeprom_28c.cpp` | `primitives.cpp` | poll_readback(handle, address, expected, 2000, &observed) | WIRED | eeprom_28c.cpp:128 |
| `flash_type_4.cpp` | `primitives.cpp` | poll_readback(handle, address, expected, 1024, &observed) | WIRED | flash_type_4.cpp:123 |
| `eeprom_28c.cpp` | `flash_utils.h` | flash_execute_command(FLASH_DISABLE_WRITE_PROTECTION) | WIRED | eeprom_28c.cpp:101; P7 redirect confirmed |

### Data-Flow Trace (Level 4)

Not applicable — this is a firmware refactor with no dynamic data sources in the conventional sense. The "data flow" is behavioral correctness under the golden trace oracle, which is verified by pio test -e native (105/105 PASS).

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| All 105 native tests pass | pio test -e native | 105/105 PASS, all 14 suites green | PASS |
| Leonardo flash net-decrease from baseline | pio run -e leonardo | 25136 B (87.7%); -518 B vs 25654 B baseline | PASS |
| check_dispatch.py 0 violations | python tools/check_dispatch.py | 746 chips; 0 dispatch regressions; 0 consistency violations | PASS |
| diff_db.py identity diff | python tools/diff_db.py | 0 changed / 0 new / 0 missing | PASS |
| INV-01..09 each >= 3 files | grep -rln "INV-0N" firestarter/doc/ src/ test/ | All 9: min=3, max=9 | PASS |
| SAFE-06: host source untouched | git -C firestarter_app diff -- '*.py' '*.json' '*.sh' | Exit 0 (HOST SOURCE CLEAN) | PASS |
| CR-01 fix: chip_id_report has force_warning param | grep in primitives.h/cpp | force_warning parameter present and documented; FLAG_FORCE not read inside primitive | PASS |
| WR-02 tests registered | grep test_wr02a/b/c in test_val_eprom.cpp | All 3 found and in RUN_TEST | PASS |
| D-08 over-voltage threshold | grep "vpp_mv.*+.*500" primitives.cpp | Line 106: vpp_mv > (uint32_t)handle->vpp_mv + 500 | PASS |
| resolve_chip guard present | grep resolve_chip chip_resolver.py | Line 16: def resolve_chip(name, db) | PASS |
| 2516 UNVERIFIED status | grep verification_status near 2516 in chip_database.json | verification_status=UNVERIFIED, support_status=supported | PASS |

### Probe Execution

No conventional probe scripts (scripts/*/tests/probe-*.sh) exist for this phase. The phase uses PlatformIO native tests as its probe mechanism, run above.

### Requirements Coverage

| Requirement | Source Plan(s) | Description | Status | Evidence |
|-------------|---------------|-------------|--------|---------|
| PRIM-02 | 89-01 | SDP/const-table dedup | SATISFIED | FLASH_ENABLE_WRITE_PROTECTION and EEPROM_SDP_DISABLE removed; commit 0052c42 |
| PRIM-03 | 89-02 | chip_id_report primitive | SATISFIED | primitives.h+cpp with force_warning param; all 4 call sites wired; CR-01 fix at a296195 |
| PRIM-04 | 89-03 | vpp_check_window primitive | SATISFIED | D-06 keying preserved; no REGULATOR in primitive; D-08 threshold at primitives.cpp:106 |
| PRIM-05 | 89-04 | poll_readback primitive | SATISFIED | eeprom28c + flash4 wired (the "two single-address polls"); eprom verify_and_update_mask excluded by plan decision (different algorithm). ROADMAP SC#4 third site ACCEPTED as D-02 scope narrowing by operator 2026-06-26. |
| PRIM-06 | 89-05 | Leonardo flash measured every step; net-decrease; final % reported | SATISFIED | 89-FLASH-LEDGER.md records P7/P4/P3/P5 steps; final 25090 B at abbbb5c (pre-CR-01 snapshot; actual HEAD = 25136 B); both are net-decrease from 25654 B baseline; -518 B net decrease |
| SAFE-01 | All plans | Primitives key on handle->protocol, not electrical.type; WARNING-5 guards preserved | SATISFIED | No electrical.type usage in primitives.cpp/h; protocol==0x0B keying in eprom.cpp:272; check_dispatch.py 0 violations |
| SAFE-02 | All plans | INV-01..09 survive each step, greppable >= 3 files | SATISFIED | All 9 INV ids at >= 3 files; 105/105 native tests pass including INV asserts |
| SAFE-03 | All plans | check_dispatch.py 0 violations; diff_db.py empty | SATISFIED | Confirmed live: 0 violations; identity diff |

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| 89-FLASH-LEDGER.md | 28 | Stale final flash figure (25090 B) — authored before CR-01 fix which added +46 B | INFO — RESOLVED | Ledger refreshed 2026-06-26 to actual phase HEAD a296195: 25136 B / 87.7% / −518 B, with a CR-01 fix row added. D-01 net-decrease holds. |
| 89-FLASH-LEDGER.md | 61 | Test count "102/102" — stale (pre-CR-01 fix) | INFO — RESOLVED | Ledger refreshed to 105/105 (incl. the 3 WR-02 tests). |

No TBD, FIXME, or XXX markers found in any phase-89-modified firmware files (primitives.h, primitives.cpp, eprom.cpp, eeprom_28c.cpp, flash_intel.cpp, flash_type_4.cpp, flash_utils.cpp).

### Human Verification — RESOLVED (operator, 2026-06-26)

#### 1. ROADMAP SC#4 Eprom poll_readback Scope — ACCEPTED + D-02

**Original question:** ROADMAP §Phase 89 SC#4 names three poll_readback sites including the verify-readback half of `eprom_write_execute` (`verify_and_update_mask`, eprom.cpp). Plan 89-04 covered only eeprom28c + flash4 and excluded the eprom site without filing a D-02 deferral row.

**Resolution:** Operator ACCEPTED the scope narrowing. `verify_and_update_mask` is a genuinely different algorithm (whole-buffer bitmask, returns a count, no timeout frame / no error MSG); routing it through the single-address `poll_readback` kernel would CHANGE behavior, violating the behavior-preserving contract. The exclusion was plan 89-04's explicit, reviewer-corroborated design decision. ROADMAP SC#4's third site is treated as aspirational wording, not a defect. Recorded as a D-02 deferral note in 89-04-SUMMARY.md. Truth #4 / PRIM-05 accepted SATISFIED.

---

### Gaps Summary

No open gaps. The single SC#4 scope item was resolved by operator decision (ACCEPTED + D-02, 2026-06-26 — see operator_resolutions). All ROADMAP SCs (1/2/3/4/5) and all 8 requirement IDs (PRIM-02/03/04/05/06, SAFE-01/02/03) are implemented and verified in the codebase.

The 89-FLASH-LEDGER.md previously contained two stale figures (25090 B final flash, 102/102 tests) because it was authored before the post-phase CR-01 fix; it has been refreshed to the actual phase-HEAD values (25136 B, -518 B net decrease, 105/105 tests). The D-01 net-decrease criterion is met.

---

_Verified: 2026-06-26T11:35:19Z_
_Verifier: Claude (gsd-verifier)_
