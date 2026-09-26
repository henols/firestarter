---
phase: 119-lock-sdp-enable-command-surface-fw-half
verified: 2026-07-28T21:49:06Z
status: passed
score: 6/6 must-haves verified (all six ROADMAP success criteria; three via corrected mechanism, per CONTEXT.md D-05/D-15, not the original literal wording)
behavior_unverified: 0
overrides_applied: 0
re_verification: no
---

# Phase 119: LOCK — SDP-enable + command surface (FW half) — Verification Report

**Phase Goal:** SDP-enable becomes a real, standalone firmware capability — the milestone's only
new state-mutating operation — landing on top of proven observability, with a
command-admission guard that's provably safe under both build configurations.

**Verified:** 2026-07-28T21:49:06Z
**Status:** passed
**Re-verification:** No — initial verification

This verification was performed goal-backward against **live source and live tool/test
execution** in both submodules (`firestarter` @ `0048b3d`, `firestarter_app` @ `9ead17f`, both on
`v1.22-at28c-software-data-protection-lifecycle`), not against SUMMARY.md or NONREGRESSION.md
prose. Every command below was re-run by this verifier in this session; none of the phase's own
self-report documents were taken as evidence on their own.

---

## Goal Achievement

### Observable Truths (ROADMAP Success Criteria, criteria 4/5/6 read per their documented correction)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | `CMD_SDP_UNLOCK`/`CMD_SDP_LOCK` issuable standalone — no payload, no `DONE` round-trip, because `init`/`end` are NULL | ✓ VERIFIED | `src/proms/eeprom_28c.cpp:214-219`: only `firestarter_operation_main` is assigned for both `CMD_SDP_UNLOCK`/`CMD_SDP_LOCK` in `configure_eeprom28c`'s switch — no `init`/`end` arm. RESEARCH F-T's correction is recorded in-source at `src/firestarter.cpp:231-245`: NULL `init`/`end` does not skip the INIT/END frame pairs, only the `DONE` round-trip and any `#` data frame — the code comment states this precisely, not overclaiming. `test_configure_memory.cpp` case group 3 (re-run, `pio test -e native`, PASSED) machine-checks non-NULL `main` + NULL `init`/`end` for both commands on `0x0D`. |
| 2 | Lock native trace is the 3-load + `t_WC`, no-payload body, distinct from unlock and chip-erase | ✓ VERIFIED | `src/proms/eeprom_28c.cpp:429-446` (`eeprom28c_sdp_lock_execute`): 3-write emit + `delay(AT28C_TWC_MAX_MS)`, no completion poll, no data write — matches D-11 exactly. `test_sdp_harness.cpp`'s `test_lock05_three_way_enable_table_identity`/`test_lock05_enable_table_objects_distinct` (re-run, PASSED) prove byte-identity to `FLASH_ENABLE_WRITE`/`FLASH_ENABLE_WRITE_PROTECTION` AND pointer-level distinctness (`(const void*)` inequality, not merely byte-equality — this is the correct falsification target per the verification brief's point 4). `test_eeprom28c_sdp.cpp` cases 13-19 (re-run, PASSED) pin four dump-authored `SDP_FIXED_LOCK_*` goldens per pinout and the exact-divergence-index proofs against unlock/erase streams. |
| 3 | `is_memory_cmd()` replaces the ordinal guard, proven identical with/without `-D DEV_TOOLS` | ✓ VERIFIED | `include/firestarter.h:109-123`: `is_memory_cmd()` body contains zero `#ifdef`/preprocessor conditionals, enumerates exactly `{CMD_READ, CMD_WRITE, CMD_ERASE, CMD_BLANK_CHECK, CMD_CHECK_CHIP_ID, CMD_VERIFY, CMD_SDP_UNLOCK, CMD_SDP_LOCK}`. `src/firestarter.cpp:86` calls it at the admission site with no conditional wrapper. `test_cmd_admission.cpp`'s `test_admission_truth_table_over_every_cmd_value` is exhaustive over **all 256** `uint8_t` values (not a sample) and uses bare numeric literals `7`/`8` for the DEV_TOOLS-gated `CMD_DEV_ADDRESS`/`CMD_DEV_REGISTER` (verified in source, lines 60-89 of the test file) — exactly the anti-vacuity requirement. Re-ran both `pio test -e native` and `pio test -e native_nodevtools` myself: **141/141 in both**, identical suite set, confirming DEV_TOOLS-invariance is a semantic proof, not textual. |
| 4 (corrected) | Lock/unlock fail-closed for `protocol != 0x0D`, never silently accepted (mechanism-corrected per D-05/D-06, not the literal `default:` arm) | ✓ VERIFIED (mechanism-corrected, intent-satisfied) | Confirmed live: `configure_eeprom28c` (`src/proms/eeprom_28c.cpp:189-221`) has **no `default:` arm** — verified by direct read and by `grep -n default: src/proms/eeprom_28c.cpp` (zero matches in this function). The generic guard lives at `src/operation_utils.cpp:63-173`: `op_execute_stateful_operation` falls through to `LOG_ERROR_ID(MSG_ERR_NOT_SUPPORTED); handle->response_code = RESPONSE_CODE_ERROR; return false;` when `firestarter_operation_main` is NULL — a single, generic, total guard, exactly D-06's shape. `test_configure_memory.cpp` case groups 1-6 (re-run, PASSED) machine-check read/write/verify stay non-NULL for every protocol while SDP cmds are NULL-main for every protocol other than `0x0D`. `REQUIREMENTS.md` line 69 records LOCK-04 as "Complete (mechanism-corrected, intent-satisfied)" — correctly worded, not silently reworded to imply the original literal mechanism shipped. |
| 5 (corrected) | `FLASH_ENABLE_WRITE_PROTECTION` preserved byte-identical, not deduped, rationale recorded (relocated out of `flash_utils.h`, which stays byte-frozen, per D-09) | ✓ VERIFIED (intent-satisfied in a different file) | `git diff 1880054..HEAD -- include/flash_utils.h` is **empty** — confirmed byte-identical to phase base by direct diff run in this session. `FLASH_ENABLE_WRITE_PROTECTION` still present at `flash_utils.h:42-53` (not deduplicated). The rationale comment lives beside the new `EEPROM_SDP_ENABLE[3]` table in `eeprom_28c.cpp` instead (verified present), machine-checked by the three-way identity/distinctness guard above plus `test_sdp_table_parity.py` (re-run, 5 passed, including the new parity leg added by Plan 119-06). |
| 6 (corrected) | Flash delta measured and judged against the corrected live headroom (2992 B, not the stale 3348 B), arithmetic shown | ✓ VERIFIED | Re-ran `pio run` myself: **3/3 SUCCESS** — Leonardo `26072/28672` (90.9%), Uno `23932/32256` (74.2%), uno328pb `23976/32384` (74.0%) — **exact byte-for-byte match** to `119-NONREGRESSION.md` §4's claimed figures. `2992 − 392 = 2600` cross-checked directly (`28672 − 26072 = 2600`); arithmetic is internally consistent and independently reproduced. `REQUIREMENTS.md` line 71 (LOCK-06) states the corrected arithmetic and the superseded-figure disclosure; the traceability table (line 175) reads "Complete". |

**Score:** 6/6 truths verified (0 present-but-behavior-unverified; 0 overrides needed — every "criterion" deviation is a documented, correctly-recorded mechanism correction, not a gap).

### The Command-Admission Guard: "Provably Safe Under Both Build Configurations"

Independently re-run in this session (not trusted from any summary):

| Check | Command | Result |
|---|---|---|
| Native suite, DEV_TOOLS present | `pio test -e native` | **141/141**, 17 suites, PASSED |
| Native suite, DEV_TOOLS absent | `pio test -e native_nodevtools` | **141/141**, 17 suites, PASSED — identical suite set to the row above |
| AVR builds | `pio run` | **3/3 SUCCESS** — Leonardo 26072/28672, Uno 23932/32256, uno328pb 23976/32384 (exact match to NONREGRESSION.md §4) |
| Exhaustive truth table | source read of `test_cmd_admission.cpp` | Loop `for (int c = 0; c <= 255; c++)` — every value, not a sample; DEV_TOOLS-gated cmds referenced only as bare literals `7`/`8` |
| Predicate purity | source read of `include/firestarter.h:109-123` | Zero `#ifdef`/preprocessor tokens inside `is_memory_cmd()`'s body |

### Anti-Hollow Gate Verification (Step 7c-adjacent, re-executed directly)

| Gate | Command | Result |
|---|---|---|
| `check_is_memory_cmd_no_ifdef.py` against real source | `python3 tools/check_is_memory_cmd_no_ifdef.py` | PASS, exit 0 |
| Same tool against planted-violation fixture | `FIRESTARTER_CMD_ADMISSION_SRC=tests/fixtures/planted_ifdef_in_predicate.h python3 tools/check_is_memory_cmd_no_ifdef.py` | **FAIL, exit 1** — correctly fails closed |
| Same tool against unreadable path | `FIRESTARTER_CMD_ADMISSION_SRC=/nonexistent/path.h python3 tools/check_is_memory_cmd_no_ifdef.py` | **ERROR, exit 1** — correctly fails closed |
| Its pytest | `pytest tests/test_check_is_memory_cmd_no_ifdef.py -q` | 6 passed |
| `check_no_log_in_sdp_window.py` | `python3 tools/check_no_log_in_sdp_window.py` | PASS, exit 0 (emitter 298-314, poll 348-361) |
| `gen_sdp_bus_config.py --check` | `python3 tools/gen_sdp_bus_config.py --check` | OK — matches a fresh regeneration |
| `check_dispatch.py` | `python3 tools/check_dispatch.py` | PASS — 746 scanned, 736 supported, 0 regressions |
| Six host-gate pytest modules combined | `pytest test_sdp_table_parity.py test_check_no_log_in_sdp_window.py test_sdp_bus_config_drift.py test_revision_constants_parity.py test_dispatch_mirror.py -q` | **24 passed** (5+7+4+6+2) |
| Catalog three-way parity | `cmp` × 2 + `codegen.py --check` × 2 | All 4 exit 0, "OK: catalog valid (73 messages, version 1)" both sub-repos |
| Full host pytest | `python3 -m pytest --tb=no -q` (from `firestarter_app`) | Exactly **one** failure: `test_audit_coverage_matrix.py::test_golden_file_matches` — confirmed pre-existing/documented (`.planning` memory `reference_audit_coverage_matrix_golden_stale.md`), unrelated to this phase's diff |

### Anti-Hollow Checks Beyond the Gate List

| Check | Evidence |
|---|---|
| `SDP_FIXED_LOCK_*` goldens are dump-derived, not hand-transcribed | Source (`test_eeprom28c_sdp.cpp:472,1738`) contains a real `#ifdef SDP_TRACE_DUMP` dump block, confirmed present; 119-05-SUMMARY.md documents the dump-and-hand-check provenance in detail; RESEARCH A1's independent arithmetic prediction matched the dump exactly for 3 of 4 pinouts, cross-validating the dump wasn't fabricated to match a prior assumption |
| `t_BLC` budget WARN fires AND does not fire (both directions, both sequences) | `test_case11_tblc_budget_exceeded_warns` (unlock, fires) + anti-hollow default-elapsed control (unlock, does not fire) + `test_case21_lock_tblc_budget_warn_fires` (lock, fires) + `test_case22_lock_tblc_budget_warn_does_not_fire_at_normal_elapsed` (lock, does not fire) — all four present in source and passing in the 141/141 run |
| LOCK-05's three tables are distinct objects, not merely byte-identical | `test_lock05_enable_table_objects_distinct` casts to `(const void*)` and uses `TEST_ASSERT_NOT_EQUAL` — pointer inequality, not a second byte-comparison; a single deduplicated table would fail this test even though it would pass the byte-identity test above it |
| Cases 11/12 re-verified by name after Wave 5's `micros()` mock upgrade | Source comment at `test_eeprom28c_sdp.cpp:989`: "Plan 119-05 Task 1 (re-verified under the scripted `micros()` queue…" directly above `test_case12_flag_absent_emits_exactly_two_report_frames` |
| `_shared/host_stubs_common.inc` honesty | `git diff 1880054..HEAD` shows a clean **14-line addition only** (`op_reset_timeout` stub) — no pre-existing line touched; NONREGRESSION.md states this honestly rather than claiming false blob-identity |
| `_shared/sdp_expected.h` per-array identity (whole-file SHA legitimately changed) | `git diff 1880054..HEAD -- .../sdp_expected.h \| grep '^-' \| grep -v '^---'` → **zero lines** — confirmed additions-only; every pre-existing golden array is untouched |

### Scope Boundaries Held

| Boundary | Status | Evidence |
|---|---|---|
| DEVTEST-01 stays `Pending` | ✓ HELD | `REQUIREMENTS.md` line 84: checkbox `[ ]`, traceability row (line 182) reads "Pending". No plan's `requirements:` frontmatter or SUMMARY prose marks it Complete — 119-07/119-09 both name it as firmware-half-only, host half explicitly deferred to Phase 121 |
| D-17: lock's hardware duration NOT attempted | ✓ HELD | `119-MEASUREMENT.md` §5: "zero attempts at cmd 9 or cmd 10" stated explicitly; no raw-frame script exists in the repo diff |
| `flash_utils.h` byte-frozen | ✓ HELD | `git diff 1880054..HEAD -- include/flash_utils.h` empty (re-run, confirmed) |
| No host CLI surface added (`dev sdp`, `constants.py` CMD_*, etc.) | ✓ HELD | `constants.py`/`cli_handlers.py`/`argparse` or Click surfaces untouched — `test_revision_constants_parity.py` (6 passed) confirms `CMD_SDP_UNLOCK`/`CMD_SDP_LOCK` deliberately absent from `constants.py`, matching HOST-03's Phase 120 scope |

### Requirements Coverage

| Requirement | Source Plan | Status | Evidence |
|---|---|---|---|
| LOCK-01 | 119-05 | ✓ SATISFIED | Four dump-authored goldens pin the 3-load stream on all 4 pinouts; no-payload termination asserted positionally (Case 17) |
| LOCK-02 | 119-04, 119-07 | ✓ SATISFIED | Standalone commands wired; NULL init/end confirmed; op-layer refusal proven end-to-end (cases 24/25) |
| LOCK-03 | 119-02, 119-03 | ✓ SATISFIED | Exhaustive 2-env truth table (re-run, 141/141 both) + textual anti-hollow gate (re-run, fails on planted fixture) |
| LOCK-04 | 119-07 | ✓ SATISFIED (mechanism-corrected, intent-satisfied) | Confirmed no `default:` arm exists; generic NULL-main guard confirmed live in `operation_utils.cpp` |
| LOCK-05 | 119-06 | ✓ SATISFIED | Byte-identity AND pointer-distinctness both machine-checked and passing |
| LOCK-06 | 119-10, 119-11 | ✓ SATISFIED | `pio run` re-run, exact figure match; arithmetic independently cross-checked |
| DEVTEST-01 (fw half) | 119-07, 119-09 | ✓ SATISFIED (fw half only) | Generic guard closes `CMD_ERASE`/`CMD_CHECK_CHIP_ID` phantom-success on `0x0D`; host half correctly left Pending |

### Anti-Patterns Scan

No `TBD`/`FIXME`/`XXX` markers found in any file this phase touched (`include/firestarter.h`, `src/firestarter.cpp`, `src/operation_utils.cpp`, `src/proms/eeprom_28c.cpp`, `src/eprom_operations.cpp`). Comments extensively document rejected alternatives and deliberate non-actions (D-06's "deliberately not taken" items) — these are decision records, not debt markers, and each cites its own decision id. No placeholder/stub return patterns found in the new code paths (`eeprom28c_sdp_lock_execute`, `eeprom28c_sdp_unlock_execute`, the op-layer guard) — all perform real, traced-and-tested work.

### Bench Measurement Honesty (D-19/D-20, `119-MEASUREMENT.md`)

Reviewed in full. The Leonardo/Uno-class ~70x divergence (6080 µs vs 84/88 µs) is explained structurally (§1/§4): the Leonardo's write crossed the page-1→page-2 boundary, folding in a completion-poll-plus-64-byte-readback-verify into one reported interval, while the Uno-class boards aborted during page 1's own verify and never crossed the boundary — a clean within-page figure. The document explicitly warns the two kinds of number are not comparable and states this is not evidence about AT28C silicon anywhere. The Uno-class 84/88 µs vs the 100 µs/byte datasheet max is reported plainly with unrounded provenance (not smoothed into "under budget" framing). Per-port `controller:` identity was verified by command before driving each board (§2a). No fabricated PASS found; the honest divergence from the plan's anticipated flow (Leonardo succeeded fully where Uno-class failed at readback) is recorded rather than hidden.

### Decision Coverage

All 20 CONTEXT.md decisions (D-01 through D-20, with D-19 nested inside D-18) are traceable to implementation, verified directly against source/tests in this session for the load-bearing ones (D-01, D-02, D-03, D-04, D-05, D-06, D-07, D-09, D-10, D-11, D-12, D-13, D-14, D-15, D-16, D-17, D-18/D-19, D-20) and against `REQUIREMENTS.md`/`ROADMAP.md`/`PROJECT.md` prose for the documentation-only ones. No decision found unimplemented, contradicted, or silently dropped.

### Human Verification Required

None. All must-haves are either machine-verified via re-executed tests/gates in this session or directly confirmed against live source. No behavior-dependent truth was left unexercised — every state-transition claim (INIT/END frame pairs still emitting on a NULL init/end, the NULL-main refusal firing, the t_BLC WARN firing/not-firing in both directions) has a passing, re-run native test backing it.

---

## Gaps Summary

None. Every ROADMAP success criterion holds — three (4, 5, 6) via a documented, correctly-recorded mechanism correction rather than their literal original wording, exactly as the phase's own CONTEXT.md/ROADMAP.md correction blocks describe, and this verifier confirmed each correction against live source rather than accepting the correction's existence as self-certifying. All 141 native tests pass identically in both build configurations (re-run independently). All three AVR builds succeed with flash figures matching claimed figures byte-for-byte (re-run independently). All anti-hollow gates fail closed against their planted-violation fixtures (re-run independently). Scope boundaries (DEVTEST-01 Pending, no host CLI surface, `flash_utils.h` frozen, lock's hardware duration not attempted) all held. The one pre-existing host pytest failure (`test_audit_coverage_matrix`) is confirmed unrelated to this phase's diff.

---

_Verified: 2026-07-28T21:49:06Z_
_Verifier: Claude (gsd-verifier)_
