---
phase: 118-observe-auto-unlock-visible-opt-out-able-fw-half
verified: 2026-07-28T15:42:53Z
status: passed
score: 12/12 must-haves verified
behavior_unverified: 0
overrides_applied: 0
findings:
  - id: F-118-01
    title: "D-09's 'should never fire' premise is measured at ~4.7% margin, not a wide margin"
    detail: >
      Measured Leonardo SDP-disable emit duration is 572 us against a 600 us budget
      (6 x AT28C_TBLC_MAX_US), i.e. 28 us / 4.7% headroom. CONTEXT.md D-09 framed the
      runtime check as one that "on a 16 MHz AVR ... should never fire", implying
      comfortable headroom. The actual measurement shows the real MCU consumes ~95%
      of the per-byte t_BLC budget. This is not a phase defect -- the code does exactly
      what was decided, the check is genuinely a runtime WARN (not decorative), and it
      correctly did not fire. But the premise that a future edit is required to make it
      fire is optimistic: on this hardware, a handful of extra cycles per byte-load
      (e.g. compiler codegen drift, a future -O level change, or an added instruction
      in the loop) could tip it. D-10 additionally documents that eeprom28c_write_execute's
      page-load loop shares the identical constraint with no runtime check at all, so
      this same ~5% margin applies there too, uninstrumented. Recommend Phase 119/122
      treat this 572/600 figure as "tight", not "comfortable", when judging whether the
      page-load loop (gh#11's actual locus, per Phase 117's conflation finding) needs its
      own check, and note the margin explicitly in any headroom judgement rather than
      inheriting D-09's "should never fire" framing uncritically.
    severity: informational
    routes_to: "Phase 119 / Phase 122 close (LOCK-06 headroom judgement, D-10 follow-up)"
---

# Phase 118: OBSERVE — auto-unlock visible + opt-out-able (FW half) Verification Report

**Phase Goal:** Today's silent, unconditional auto-unlock becomes something the user can see happened and can decline — without ever risking the SDP timing window by logging inside it.
**Verified:** 2026-07-28T15:42:53Z
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths (ROADMAP Success Criteria, verbatim)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | A `0x0D` write reports one line before the unlock sequence and one line after it — never inside it — proven by a source-scan test with a planted `LOG_` fixture inside the timing window that goes RED | ✓ VERIFIED | `check_no_log_in_sdp_window.py` (rewritten by 118-01) re-run live: `PASS: no logging call in SDP timing window (..., emitter lines 222-238, completion-poll lines 272-285)`, exit 0. `tests/fixtures/planted_log_in_window.cpp:35` plants `LOG_INFO_ID(MSG_DEBUG)` inside the re-planted `eeprom28c_emit_command_sequence` body; running the checker against that fixture (`FIRESTARTER_SDP_SRC=...`) independently confirmed FAIL/exit 1. `eeprom_28c.cpp:355` (`LOG_ID(MSG_INFO_SDP_UNLOCK)`) sits after the identity check and before the emit call; `eeprom_28c.cpp:334` (`LOG_ID_U32(MSG_INFO_SDP_UNLOCK_DONE_US, sdp_emit_us)`) sits after the emit call — both outside the emitter/poll bodies the gate scans. |
| 2 | Setting `FLAG_SKIP_SDP_UNLOCK` (`0x100`) on a write causes firmware to skip the unlock sequence entirely, observable via the Phase 116/117 trace harness as the sequence's total absence from the emitted stream; omitting the flag runs the sequence as before | ✓ VERIFIED | `test_case9_skip_flag_suppresses_unlock_stream` drives PRODUCTION `eeprom28c_write_init` and asserts exact-index-0 divergence from `SDP_FIXED_DIP28_28C256` plus a payload-byte-absence walk over every recorded `STROBE_KIND_DATA` entry (content-positional, not count-based). `test_case10_flag_absent_emits_full_unlock_stream` asserts the full golden stream from the same handle factory/row. **Independently re-verified by this verifier**: inverted the skip condition in `eeprom_28c.cpp:284` (`if (!is_flag_set(...))` → `if (true)`) — case 9 and case 12 FAILED as expected (`Expected 0 Was -1`, `Expected 1 Was 2`); reverted cleanly (`git diff` empty). |
| 3 | A named `AT28C_TBLC_MAX_US = 100` constant is cited at every call site the timing window touches | ✓ VERIFIED | `#define AT28C_TBLC_MAX_US 100` at `eeprom_28c.cpp:54`; cited at the sibling `AT28C_TWC_MAX_MS` forward-reference comment (:35-41), the page-load loop citation in `eeprom28c_write_execute` (comment-only, D-10, verified every added line begins with `//`), and the runtime budget expression in `eeprom28c_write_init` (`sdp_tblc_budget_us = sdp_seq_len * AT28C_TBLC_MAX_US`). `grep -c 'AT28C_TBLC_MAX_US'` = 4 in the file. |
| 4 | The host-side duration of the emitted sequence is measured via `micros()` on at least one board and logged after the sequence completes | ✓ VERIFIED | `118-MEASUREMENT.md`: one real Leonardo run (`controller: leonardo` on `/dev/ttyACM0`, firmware SHA `1880054`), verbatim raw log shows `I: SDP unlock: disabling write protection` then `I: SDP unlock emitted in 572 us`. Flash/RAM figures in the document (25680/28672, 1998/2560) match figures this verifier independently rebuilt from the same commit. Code: `sdp_emit_start_us = micros()` / `sdp_emit_us = (uint32_t)(micros() - sdp_emit_start_us)` bracket the emit call only (outside `eeprom28c_emit_command_sequence`'s body), matching `grep -c 'micros()'` = 2 confirmed. |
| 5 | With no new flag set, a `0x0D` write's outward behavior is byte-identical to `3.0.0b11` apart from the corrected emitter (Phase 117) and the two new report lines | ✓ VERIFIED | Bus-stream half: all three `_shared/` files (`sdp_expected.h`, `host_stubs_common.inc`, `sdp_bus_config.h`) independently re-derived blob-SHA-identical between phase base `f8d10a5` and HEAD `1880054`. `git diff --name-only f8d10a5..HEAD` = exactly 6 paths, none under `_shared/`. Serial-channel half: `test_case12_flag_absent_emits_exactly_two_report_frames` enumerates exactly `MSG_INFO_SDP_UNLOCK` then `MSG_INFO_SDP_UNLOCK_DONE_US` on the default path, and exactly `MSG_WARN_SDP_UNLOCK_SKIPPED` on the skip path (independently re-run, 12/12 passing). `118-NONREGRESSION.md` enumerates the exception in one table and never lets "byte-identical" stand unqualified. |

**Score:** 5/5 ROADMAP success criteria verified, 0 present-but-behavior-unverified.

### Decision-Contract Spot Checks (13 tracked decisions + D-08)

| Decision | Claim | Status | Evidence |
|----------|-------|--------|----------|
| D-01 | Report lines via `LOG_ID`/`LOG_ID_U32`, NOT `LOG_INFO_ID*`; convention break argued in source | ✓ VERIFIED | `eeprom_28c.cpp:355,334` use bare `LOG_ID`/`LOG_ID_U32`; `logging_id.h:42-84` confirms `LOG_INFO_ID*` is the only `FLAG_VERBOSE`-gated family and all 19 pre-existing `MSG_INFO_*` call sites use it (grep-confirmed no `LOG_INFO_ID` on the new lines). Source comment at `eeprom_28c.cpp:322-341` explicitly argues the break. |
| D-02 | Skip path emits WARN and never writes `response_code` on the SDP path | ✓ VERIFIED | `LOG_WARN_ID(MSG_WARN_SDP_UNLOCK_SKIPPED)` at the skip arm; `grep -n 'response_code' eeprom_28c.cpp` shows the only writes are inside `eeprom28c_check_chip_id` (pre-existing, Phase 117) — none inside the unlock/skip arms (lines ~291-410). `test_case8_completion_poll_preserves_prior_severity` (still green) and case 11's explicit `RESPONSE_CODE_OK` assertion both hold. |
| D-05 | Both `micros()` calls sit outside `eeprom28c_emit_command_sequence`'s body, bracketing the call only | ✓ VERIFIED | `grep -c 'micros()'` = 2, both between the identity block and `eeprom28c_wait_for_sdp_completion`'s call; emitter body (lines 222-238) and poll body (272-285) are byte-unchanged per the whole-plan diff (`@@ -293,24 +293,122 @@`, entirely inside `write_init`). |
| D-07 | OBS-05 byte-identity asserted via git blob-SHA on `_shared/`, no golden regen; two new serial frames a named exception | ✓ VERIFIED | Blob SHAs independently re-derived and matched (see truth 5 above). |
| D-08 (discretion) | Skip-proof drives PRODUCTION `eeprom28c_write_init`; asserts stream CONTENT not count; flag-absent counterpart ships same commit | ✓ VERIFIED | `drive_write_init` → `configure_memory` dispatch (not `drive_reference_emitter`); case 9's load-bearing assertions are exact-index divergence + payload-byte-absence walk, with the bare count check explicitly demoted to "secondary corroboration ONLY" in a comment; case 10 ships in the same commit (`de12c79`). |
| D-09/D-10 | t_BLC budget is a RUNTIME check on the unlock only; page-load loop gets a citation comment only, no per-byte compare | ✓ VERIFIED | Runtime check at `eeprom_28c.cpp:346-348`; page-load citation at `eeprom28c_write_execute` is comment-only (all 15 added lines begin with `//`, confirmed by this verifier's read of the diff region). See Finding F-118-01 for a judgment note on the premise, not a code defect. |
| D-11 | No citation-presence assertion added to the gate or any sibling | ✓ VERIFIED | `check_no_log_in_sdp_window.py`'s docstring states this explicitly; no `AT28C_TBLC_MAX_US` string-scan logic exists in the file (reviewed). |

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `firestarter_app/tools/check_no_log_in_sdp_window.py` | Rewritten window (emitter+poll body union) | ✓ VERIFIED | Runs PASS against real source; append-only anchor tuples present; parameterized `_find_function_body` confirmed |
| `firestarter_app/tests/fixtures/planted_log_in_window.cpp` | Re-planted inside emitter body | ✓ VERIFIED | Line 35, inside `eeprom28c_emit_command_sequence`; header comment records rationale |
| `firestarter_app/tests/test_check_no_log_in_sdp_window.py` | 7 cases, all green | ✓ VERIFIED | 7 passed on independent re-run |
| `tools/catalog/messages.toml` (+2 mirrors) | 4 new ids, byte-identical across 3 repos | ✓ VERIFIED | 3-way `cmp` exit 0; ids 0x5E/0x5F/0x86/0x87 present with correct severities/format strings |
| `firestarter/include/messages.h` | Regenerated, no reflow | ✓ VERIFIED | 4 `#define`s present, correct hex values |
| `firestarter_app/firestarter/messages.py` | Regenerated | ✓ VERIFIED | 4 catalog entries present, correct hex values |
| `firestarter/include/firestarter.h` | `FLAG_SKIP_SDP_UNLOCK 0x100` | ✓ VERIFIED | Present, 9th flag, `ctrl_flags` confirmed `uint32_t` |
| `firestarter/src/proms/eeprom_28c.cpp` | Constant + 2 citations + runtime check + flag gate + report lines | ✓ VERIFIED | All present, read in full by this verifier |
| `firestarter/test/native/avr/test_eeprom28c_sdp/test_eeprom28c_sdp.cpp` | 12 cases (8 orig + 4 new) | ✓ VERIFIED | 12/12 passing, independently re-run |
| `firestarter/test/native/avr/test_eeprom28c_sdp/RED-BASELINE.md` | Appended observability baseline section | ✓ VERIFIED | 118 insertions / 0 deletions confirmed via `git diff --stat` |
| `.planning/phases/.../118-NONREGRESSION.md` | 8-section sweep record | ✓ VERIFIED | All 8 sections present; every claim re-checked independently in this verification |
| `.planning/phases/.../118-MEASUREMENT.md` | Standalone measurement artifact | ✓ VERIFIED | 7 sections present; validation-ceiling review confirmed no silicon claim |

### Key Link Verification

| From | To | Via | Status | Details |
|------|-----|-----|--------|---------|
| `eeprom28c_write_init` | `eeprom28c_emit_command_sequence` | call retains `handle, EEPROM_SDP_DISABLE` substring | ✓ WIRED | Confirmed by grep; append-only `_EMIT_ANCHOR_PATTERNS` still matches |
| Gate window | firmware source | `_find_function_body` brace-matcher | ✓ WIRED | Live run against real `eeprom_28c.cpp` resolves both bodies correctly |
| `MSG_WARN_SDP_TBLC_EXCEEDED` catalog id | firmware call site | `LOG_WARN_ID_U32` | ✓ WIRED | Call site present; independently forced to fire and confirmed absent under budget |
| `FLAG_SKIP_SDP_UNLOCK` wire bit | `is_flag_set` check | `ctrl_flags` (uint32_t) + `extract_long` | ✓ WIRED | No parser/struct change needed or made; confirmed via `json_parser.c` read |
| Codec unknown-id path | released b11 host | `codec.py:206-209` | ✓ WIRED | Confirmed: logs and drops frame, no crash |

### Behavioral Spot-Checks (independently performed by this verifier)

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Gate catches planted violation | `FIRESTARTER_SDP_SRC=tests/fixtures/planted_log_in_window.cpp python tools/check_no_log_in_sdp_window.py` | exit 1, FAIL at line 35 | ✓ PASS |
| Gate passes on real source | `python tools/check_no_log_in_sdp_window.py` | exit 0, PASS naming emitter 222-238 / poll 272-285 | ✓ PASS |
| Skip-condition inversion breaks case 9 & 12 | inverted `if (!is_flag_set(FLAG_SKIP_SDP_UNLOCK))` → `if (true)`, ran suite, reverted | case 9 FAILED (`Expected 0 Was -1`), case 12 FAILED (`Expected 1 Was 2`); reverted, diff clean | ✓ PASS |
| Budget-comparison inversion breaks case 11 & 12 | inverted `sdp_emit_us > sdp_tblc_budget_us` → `<`, ran suite, reverted | case 11 FAILED, case 12 FAILED; reverted, diff clean | ✓ PASS |
| Full native suite | `pio test -e native` | 112/112, no SIGABRT | ✓ PASS |
| Full host suite | `python -m pytest --tb=no` | 974 passed, 1 pre-existing failure (`test_audit_coverage_matrix`) | ✓ PASS |
| Cross-repo gate checklist | 6 host gate files | 27 passed | ✓ PASS |
| Board rebuild | `pio run -e leonardo -e uno` | Leonardo 25680/28672, Uno 23542/32256 — exact match to recorded figures | ✓ PASS |
| Catalog 3-way identity | `cmp` all 3 `messages.toml` | exit 0 both comparisons | ✓ PASS |
| Golden blob-SHA identity | `git rev-parse f8d10a5:<path>` vs `HEAD:<path>` for 3 `_shared/` files | identical | ✓ PASS |

### Requirements Coverage

| Requirement | Source Plans | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| OBS-01 | 118-01, 118-02, 118-04, 118-06 | Report lines, never inside window | ✓ SATISFIED | REQUIREMENTS.md `[x]`; code + gate confirmed |
| OBS-02 | 118-02, 118-03, 118-04, 118-05 | `FLAG_SKIP_SDP_UNLOCK` honoured | ✓ SATISFIED | REQUIREMENTS.md `[x]`; native cases + independent spot-check |
| OBS-03 | 118-01, 118-02, 118-03, 118-04, 118-05 | Constant cited + runtime check + anti-hollow proof | ✓ SATISFIED | REQUIREMENTS.md `[x]`; code + independent spot-check |
| OBS-04 | 118-02, 118-04, 118-07 | Measured via `micros()`, logged | ✓ SATISFIED | REQUIREMENTS.md `[x]`; `118-MEASUREMENT.md` reviewed |
| OBS-05 | 118-05, 118-06 | Byte-identical apart from named exceptions | ✓ SATISFIED | REQUIREMENTS.md `[x]`; blob-SHA + frame enumeration confirmed |

No orphaned requirements: every ID mapped to Phase 118 in REQUIREMENTS.md's traceability table (OBS-01..05) is claimed by at least one plan's `requirements` frontmatter, and all five plan-level ownership sequences match the SUMMARYs' stated closure points.

### Anti-Patterns Found

None. Scanned all phase-modified files (`eeprom_28c.cpp`, `firestarter.h`, `check_no_log_in_sdp_window.py`, `test_eeprom28c_sdp.cpp`, `test_sdp_harness.cpp`, `planted_log_in_window.cpp`, `test_check_no_log_in_sdp_window.py`, `RED-BASELINE.md`, `118-NONREGRESSION.md`, `118-MEASUREMENT.md`) for `TBD`/`FIXME`/`XXX`/`TODO`/`HACK`/`PLACEHOLDER`, empty-return stubs, and hardcoded-empty-data patterns. Zero matches. No debt markers.

### Known Dispositions (confirmed, not re-litigated)

- `catalog-sync-check.yml` red-until-merge (ref: main checkouts) — confirmed, correctly documented in `118-NONREGRESSION.md` §6.
- `test_audit_coverage_matrix` stale golden — confirmed pre-existing, unrelated to this phase's diff.
- `test_no_programmer_found_*` passing despite live boards present — an honestly-recorded unexplained divergence, not a phase defect.
- Submodule gitlinks unbumped — correct per milestone convention; confirmed `git show --stat HEAD` in each repo lists only that repo's own paths.
- `0x0D` remains `UNVERIFIED`; no `support_status` change; 84-chip count unchanged — confirmed by reading `118-MEASUREMENT.md` and `118-NONREGRESSION.md`'s validation-ceiling sections line by line; no sentence in either document is readable as bench-validating AT28C silicon.

### Finding for Downstream Phases (not a phase defect)

**F-118-01 — D-09's "should never fire" premise is tighter than framed.** The real Leonardo measurement (572 µs / 600 µs budget, 28 µs / ~4.7% headroom) does not strongly support D-09's characterization of the runtime check as one that "should never fire" on a 16 MHz AVR — 4.7% margin is a narrow tolerance, not a comfortable one. This is not a defect in Phase 118's implementation: the constant, the citation, the runtime check, and the anti-hollow proof are all exactly what was decided and all are load-bearing and independently re-verified in this report. It is a note that the *decision's premise* was optimistic, with direct bearing on D-10's identically-exposed, uninstrumented page-load loop (the actual locus of gh#11, per Phase 117's conflation finding). Recorded here as a finding for Phase 119/122's LOCK-06 headroom judgement, per the task's explicit request to draw this distinction rather than mark it as a phase failure.

### Human Verification Required

None. All observable truths, artifacts, key links, and anti-hollow proofs were verified against the live codebase and independently re-derived by this verifier (including three separate spot-check code inversions, each observed to fail the intended case and cleanly reverted). The one empirical (real-hardware) result — OBS-04's 572 µs measurement — is documented with internally-consistent, independently-corroborated provenance (flash/RAM figures matching an independent rebuild, catalog ids matching the live catalog, log format matching the live `LOG_ID`/`LOG_ID_U32` call sites) and requires no further human confirmation for this verification pass.

### Gaps Summary

No gaps. All five ROADMAP success criteria are met; all 13 tracked CONTEXT.md decisions (plus D-08's discretion) landed as decided; all five OBS requirements are Complete with real, non-orphaned coverage; the native and host test suites are green at the same counts the SUMMARYs claim; three independent anti-hollow spot-checks (skip-condition inversion, skip-arm forcing via the same inversion, budget-comparison inversion) confirmed the load-bearing tests actually fail when the code regresses. One informational finding (F-118-01) is recorded for downstream judgement, not as a blocking or warning-tier gap.

---

*Verified: 2026-07-28T15:42:53Z*
*Verifier: Claude (gsd-verifier)*
