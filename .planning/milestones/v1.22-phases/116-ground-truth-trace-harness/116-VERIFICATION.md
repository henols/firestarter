---
phase: 116-ground-truth-trace-harness
verified: 2026-07-27T23:10:00Z
status: passed
score: 6/6 must-haves verified
behavior_unverified: 0
overrides_applied: 0
---

# Phase 116: Ground Truth + Trace Harness Verification Report

**Phase Goal:** Build the trace oracle that can prove — before any production code changes — whether the shipped SDP-disable sequence and its success check actually work, and prove the harness itself can distinguish lock from unlock from erase. Zero production-code risk, so this phase can never be blocked by the fix it exists to verify.
**Verified:** 2026-07-27
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths (ROADMAP Success Criteria)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | The extended `HOST_STUBS_RECORD_BUS`/`HOST_STUBS_REAL_REGISTER_UTILS` records data bytes and `/CE`/`/OE` edges in the same ordered stream as register writes, behind a new opt-in flag; every pre-existing suite stays byte-exact when not opted in | ✓ VERIFIED | Independently ran `cd firestarter && pio test -e native` → **95/95, 0 failures** (matches the plan's 82→95 progression). `host_stubs_common.inc` gates the recorder behind `#ifdef HOST_STUBS_REAL_REGISTER_UTILS`; `test_sdp_harness.cpp` cases `test_case1_ordered_capture_dip28_28c256`, `test_case2_elision_is_real`, `test_case3_ce_oe_edges_distinguishable` all present and passing in the 95/95 run |
| 2 | The new `0x0D` SDP trace suite (`test_eeprom28c_sdp`), run against today's unfixed tree, is RED because the expected-vs-actual `(LSB, MSB, data, CE-pulse)` stream diverges, for all four `0x0D` pinouts | ✓ VERIFIED | Independently temporarily added `native/avr/test_eeprom28c_sdp` to `platformio.ini`'s `test_filter`, ran `pio test -e native -f "*test_eeprom28c_sdp*"` → **7/7 fail**, output byte-for-byte matches `RED-BASELINE.md`'s captured messages (index-0 `/OE`-ordering divergence for DIP28_28C256/64 and DIP24_2816; 54-vs-57 length divergence for the two DIP32 stale-seed cases). Direct binary execution (`.pio/build/native/firestarter_native`) confirmed a clean exit code 7, no crash — confirming the divergence reason is genuine stream inequality, not a compile/link/missing-symbol failure. Restored `platformio.ini` to its committed byte-identical state afterward (`git status --short platformio.ini` empty, `md5sum` matched pre-edit) and re-ran the default suite → 95/95 confirmed restored |
| 3 | Each of the four planted-fault negative traces independently goes RED when its fault is injected | ✓ VERIFIED | **03a** (`test_negativeA_unlock_mutated_diverges_and_matches_erase`, `test_sdp_harness.cpp:215`) and **03b** (`test_negativeB_lock_table_swapped_for_write_prefix`, `:244`) exist and are exercised in the passing 95/95 run (they assert on the *mutation's* divergence being present — i.e., the fault-injection mechanism is itself proven, per the suite's own design). **03c**: independently ran `FIRESTARTER_SDP_SRC=tests/fixtures/planted_log_in_window.cpp python tools/check_no_log_in_sdp_window.py` → exit 1, `FAIL: 1 logging call(s) found ... line 29: LOG_INFO_ID(...)`, confirming the checker is not hollow; clean-tree run exits 0. **03d**: `test_protocol_0x0C_adjacent_not_implemented`/`test_protocol_0x0F_adjacent_not_implemented` in `test_not_implemented.cpp:117-131` assert `RESPONSE_CODE_ERROR` + null operation pointers, present in the passing 95/95 run |
| 4 | The call-ordered scripted `mock_get_data` is replaced by an address-keyed version; `test_eeprom28c_chip_id.cpp`'s prior scripted `(0x5555,0x20)` assertion no longer exists in that form | ✓ VERIFIED | `test/native/avr/test_eeprom28c_chip_id/` directory confirmed absent (`ls` returns nothing). `grep -rn "s_mock_byte_idx\|s_mock_bytes" test/` returns zero hits anywhere under the native test tree. `test_sdp_harness.cpp` and `test_eeprom28c_sdp.cpp` both use an address-keyed `mock_get_data_keyed`/`mock_set_data_keyed` pattern (confirmed by reading the mock implementations and their per-address dispatch) |
| 5 | A host test pins `chip_id_check: false` across all 84 `algorithm == 13` DB entries as a machine-checked fact | ✓ VERIFIED | Independently ran `python -m pytest tests/test_sdp_db_invariant.py -v` → **4/4 passed**. `grep -c "skipif" tests/test_sdp_db_invariant.py` → **0** (no skip marker of any kind — always runs). Test asserts exactly 84 entries and `chip_id_check is False` for all of them, plus a non-vacuity leg (synthetic violating row raises) |
| 6 | A written premise-verification artifact states, with evidence from this phase's harness, whether `firestarter write at28c256` aborts at INIT on the current tree, and records any PROJECT.md correction that finding implies | ✓ VERIFIED | `116-PREMISE.md` exists, cites `RED-BASELINE.md` with a re-runnable command (independently re-run above, confirmed matching), states the finding (`RESPONSE_CODE_ERROR` before any data byte transfers, all four pinouts), and states the validation ceiling explicitly (software-layer only, no AT28C part on bench, citation not observation). `PROJECT.md`'s third ⚠ correction block (`git show f8264c2 -- .planning/PROJECT.md`) is **exactly 6 additive lines, 0 deletions** — the two pre-existing ⚠ blocks are confirmed byte-unchanged in the same diff. The block carries the 66-of-84 per-pinout table and explicitly states `support_status`/84-count are unchanged — independently confirmed via `git diff --name-only beta..HEAD -- data/` (empty) in `firestarter` |

**Score:** 6/6 truths verified (0 present-but-behavior-unverified)

### Judgment call on Criterion 2's DIP32 cases (documented, not a gap)

Plan 116-06 deviated from a literal reading of "assert against the canonical `SDP_FIXED_DIP32_28C512_EEPROM` constant" by instead asserting Cases 4-5 against a **dynamically-driven reference-emitter snapshot** taken under a deliberately stale `CTRL_ADDRESS_LINE_17/18` seed. Independently verified this is not evasion: 116-05's own passing `test_fixed_guard_at28c010`/`test_fixed_guard_at28c040` cases confirm the shipped and fixed streams are byte-identical under a *zero*-seeded CONTROL register for this pinout (because `fu_flash_fast_address` never writes `CONTROL_REGISTER`), which would make a plain zero-seed comparison decorative — passing before and after the Phase 117 fix, proving nothing about the real write-inhibit hazard. The stale-seed comparison (54 vs 57 entries — a difference in kind, an entire extra CONTROL-clearing event) is a genuine, reproducible RED for the real bug this pinout has, and is self-repairing once Phase 117 lands. This reading is accepted as satisfying Criterion 2's intent ("the suite ... is RED ... for the four `0x0D` pinouts") rather than its most literal wording, because the literal wording would have produced a weaker, non-discriminating test.

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `firestarter/test/native/avr/_shared/host_stubs_common.inc` | Opt-in ordered strobe recorder | ✓ VERIFIED | `HOST_STUBS_REAL_REGISTER_UTILS` guard present; 95/95 confirms inert-by-default |
| `firestarter/test/native/avr/test_sdp_harness/` | Always-green harness suite | ✓ VERIFIED | 13 cases, all passing in 95/95 run |
| `firestarter/test/native/avr/test_eeprom28c_sdp/` | Parked RED suite, `-I` only | ✓ VERIFIED | Compiles, 7/7 RED confirmed independently, absent from `test_filter` |
| `firestarter/test/native/avr/test_eeprom28c_sdp/RED-BASELINE.md` | Committed RED evidence | ✓ VERIFIED | Present; verbatim output matches independent re-run |
| `firestarter/test/native/avr/_shared/sdp_bus_config.h` | Generated, DO NOT EDIT | ✓ VERIFIED | Present, drift-gated by `test_sdp_bus_config_drift.py` (4/4 pass) |
| `firestarter_app/tools/gen_sdp_bus_config.py` | Live-derivation generator | ✓ VERIFIED | Present, used by drift gate |
| `firestarter_app/tools/check_no_log_in_sdp_window.py` | Structural scan | ✓ VERIFIED | Independently run clean-tree (exit 0) and planted-fixture (exit 1) |
| `firestarter_app/tests/fixtures/planted_log_in_window.cpp` | Committed violating fixture | ✓ VERIFIED | Present, never compiled, drives the checker's fail path |
| `firestarter_app/tests/test_sdp_db_invariant.py` | TRACE-05 machine-checked fact, no skipif | ✓ VERIFIED | 4/4 pass, 0 skipif |
| `firestarter_app/tests/test_sdp_table_parity.py` | Closes F6 transcription gap | ✓ VERIFIED | 4/4 pass (part of the 8/8 combined run) |
| `.planning/phases/116-ground-truth-trace-harness/116-PREMISE.md` | TRACE-06 artifact | ✓ VERIFIED | Present, ceiling-honest, cites re-runnable evidence |
| `.planning/PROJECT.md` third ⚠ block | 66-of-84 correction | ✓ VERIFIED | Exactly 6 additive lines, prior blocks byte-unchanged |
| `firestarter/test/native/avr/test_eeprom28c_chip_id/` | Retired wholesale | ✓ VERIFIED | Directory confirmed absent |

### Key Link Verification

| From | To | Via | Status | Details |
|------|-----|-----|--------|---------|
| `platformio.ini` `test_filter` | default `pio test -e native` run | allowlist membership | WIRED | `test_eeprom28c_sdp` has `-I` but no `test_filter` entry — confirmed by direct `awk`-scoped read; parking mechanism works as designed (RED suite excluded, GREEN suites included) |
| `check_no_log_in_sdp_window.py` | `eeprom_28c.cpp` real source | `FIRESTARTER_SDP_SRC` override / default path | WIRED | Default run resolves and scans the real file (lines 109-111); override redirects to the planted fixture and correctly fails |
| `test_sdp_db_invariant.py` | `chip_database.json` | direct JSON read, no `EpromDatabase` indirection | WIRED | Test passes against the live DB file in the repo; no skipif possible drift |
| `gen_sdp_bus_config.py` | `EpromDatabase.get_eprom`/`convert_to_programmer` | live derivation, not transcription | WIRED | Drift gate (`test_sdp_bus_config_drift.py`) passes; regenerate-and-diff proven to fail on a hand-edit per 116-02-SUMMARY's captured failure message (not independently re-verified in this pass, but drift gate currently green and the mechanism was inspected) |

### Zero-Production-Code Fence

| Check | Result |
|-------|--------|
| `git -C firestarter diff --name-only beta..HEAD -- src/ include/` | Empty — confirmed independently |
| `firestarter/src/proms/flash_utils.cpp` | Not in the `beta..HEAD` diff — byte-untouched |
| `firestarter/data/chip_database.json` | Not in the `beta..HEAD` diff |
| `firestarter_app` production files (`chip_database.json`, `messages.py`, DB pipeline) | `git -C firestarter_app diff --name-only beta..HEAD` shows only 7 new SDP-specific files (`tools/gen_sdp_bus_config.py`, `tools/check_no_log_in_sdp_window.py`, `tests/test_sdp_bus_config_drift.py`, `tests/test_sdp_db_invariant.py`, `tests/test_sdp_table_parity.py`, `tests/test_check_no_log_in_sdp_window.py`, `tests/fixtures/planted_log_in_window.cpp`) |

Both fences independently confirmed empty/clean — Phase 117 can proceed without inheriting any premature production-code change.

### Requirements Coverage

| Requirement | Source Plan(s) | Description | Status | Evidence |
|-------------|-----------------|--------------|--------|----------|
| TRACE-01 | 116-01, 116-05 | Ordered strobe recorder, byte-exact opt-out | ✓ SATISFIED | 95/95 run; `host_stubs_common.inc` opt-in guard |
| TRACE-02 | 116-02, 116-06 | RED `0x0D` trace suite, per pinout | ✓ SATISFIED | 7/7 independently reproduced RED |
| TRACE-03 | 116-01, 116-04, 116-05 | Four planted-fault negatives | ✓ SATISFIED | All four independently confirmed executable and RED-on-fault |
| TRACE-04 | 116-05 | Address-keyed mock, old fixture retired | ✓ SATISFIED | `test_eeprom28c_chip_id/` absent, zero `s_mock_byte_idx`/`s_mock_bytes` survivors |
| TRACE-05 | 116-03 | 84-entry DB invariant, no skipif | ✓ SATISFIED | 4/4 pass, 0 skipif, independently confirmed |
| TRACE-06 | 116-06, 116-07 | Premise artifact + PROJECT.md correction | ✓ SATISFIED | `116-PREMISE.md` + additive-only PROJECT.md diff confirmed |

**Orphaned requirements check:** `REQUIREMENTS.md` §Traceability maps only TRACE-01 through TRACE-06 to Phase 116 (36/36 total requirements mapped across the milestone; Phase 116's share is exactly these 6). No orphans.

### Anti-Patterns Found

Scanned every file in `git diff --name-only beta..HEAD` (both sub-repos) for `TBD`/`FIXME`/`XXX`/`TODO`/`HACK`/`PLACEHOLDER`: zero `TBD`/`FIXME`/`XXX` hits. Two pre-existing `TODO` markers survive in `platformio.ini` (`TODO(v1.5)`, unrelated pre-existing debt; `TODO(v1.22 Phase 117)`, which names a specific future phase and is the documented parking mechanism itself — not an unreferenced debt marker). No blocker-level anti-patterns found.

### Behavioral Spot-Checks / Probe Execution

No `scripts/*/tests/probe-*.sh` convention exists in this repo; this phase's "probes" are the native Unity suite and host pytest suites, both executed directly above (95/95 native; 963/964 host with 1 documented pre-existing unrelated failure) rather than via a probe-script wrapper.

### Pre-existing failure re-confirmed unrelated

`firestarter_app/tests/test_audit_coverage_matrix.py::TestAuditCoverageMatrix::test_golden_file_matches` fails (963 passed / 1 failed in the full host run). Independently confirmed: `git -C firestarter_app diff --name-only beta..HEAD` shows only the 7 new SDP files — the golden fixture, matrix generator, test file, and `chip_database.json` are all outside this phase's diff. Not a Phase-116 regression; matches project memory `reference_audit_coverage_matrix_golden_stale.md`.

### Human Verification Required

None. All six success criteria are independently machine-verifiable and were independently re-executed (not merely re-read from SUMMARY.md) in this verification pass, including a live, temporary, fully-restored `test_filter` toggle to observe the parked suite's RED state firsthand.

### Gaps Summary

No gaps found. All six ROADMAP success criteria independently reproduced against the live codebase:
- 95/95 native baseline reproduced exactly.
- The parked RED suite's 7/7 failure was independently triggered and its output matched `RED-BASELINE.md` verbatim, then `platformio.ini` was restored to a byte-identical state (verified via `git status --short` and `md5sum`).
- All four TRACE-03 negatives were independently confirmed executable, including running the `check_no_log_in_sdp_window.py` checker directly against both the clean tree and the planted-violation fixture via `FIRESTARTER_SDP_SRC`.
- TRACE-04's retirement (directory removed, zero fixture survivors) and TRACE-05's DB invariant (4/4 pass, 0 skipif) were independently re-run.
- TRACE-06's premise artifact and the PROJECT.md correction were checked for honesty (ceiling language, no silicon claim, 84-count/support_status unchanged) and the correction's additive-only nature was confirmed via `git show`.
- The zero-production-code fence was independently confirmed empty in both sub-repos.

One judgment call is documented (116-06's DIP32 stale-seed comparison target vs. a literal reading of "assert against the canonical fixed constant") and resolved in favor of PASS, with the reasoning recorded above — this is a documented design choice with a compelling technical justification (a literal zero-seed comparison would have been decorative), not a gap.

---

_Verified: 2026-07-27_
_Verifier: Claude (gsd-verifier)_
