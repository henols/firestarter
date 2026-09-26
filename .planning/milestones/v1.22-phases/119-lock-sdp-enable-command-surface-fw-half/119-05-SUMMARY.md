---
phase: 119-lock-sdp-enable-command-surface-fw-half
plan: 05
subsystem: firmware-sdp-lock
tags: [firmware, firestarter, sdp, at28c, eeprom28c, native-tests, golden-trace, unity]

# Dependency graph
requires:
  - phase: 119-lock-sdp-enable-command-surface-fw-half
    plan: "04"
    provides: "EEPROM_SDP_ENABLE[3], eeprom28c_emit_sdp_sequence_timed(), eeprom28c_sdp_lock_execute()/eeprom28c_sdp_unlock_execute(), CMD_SDP_LOCK dispatchable via configure_eeprom28c"
provides:
  - "SDP_FIXED_LOCK_DIP28_28C256 / _DIP28_28C64 / _DIP24_2816 / _DIP32_28C512_EEPROM (+ _LEN macros) -- dump-authored goldens pinning the production CMD_SDP_LOCK stream per pinout"
  - "make_lock_handle() / drive_lock_op() helpers in test_eeprom28c_sdp.cpp -- the load-bearing configure_memory -> reset_register_cache -> clear_strobes -> firestarter_operation_main drive order for any future CMD_SDP_LOCK case"
  - "Scripted micros() tick queue (s_micros_script/s_micros_cursor/s_micros_tail + sdp_script_micros()) replacing the two-slot parity alternator -- the seam Plan 119-08's page-load tracker needs"
  - "Cases 13-19: per-pinout lock-stream equality (13-16), the no-payload termination proof (17), and exact-divergence-index proofs against the unlock and chip-erase streams (18-19)"
  - "The complete frame-count-assertion inventory across all 17 native suites (below) -- confirms none currently drives eeprom28c_write_execute, the input Plan 119-08 needs"
affects: [119-06, 119-08, 119-10]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Scripted tick queue (vector + monotonic cursor + documented tail value) replacing a fixed-size parity alternator whenever a mock must survive a driven path calling the same function an unbounded/growing number of times"
    - "Static array golden dumped from a temporary #ifdef-gated printf block, built with a one-off platformio.ini macro definition reverted before commit, and run via the built binary directly (pio test swallows test-body printf)"
    - "Exact-divergence-index assertions (never `!= -1`) as the discipline for proving two similar-but-distinct command streams diverge at a specific, named byte position"

key-files:
  created: []
  modified:
    - firestarter/test/native/avr/_shared/sdp_expected.h
    - firestarter/test/native/avr/test_eeprom28c_sdp/test_eeprom28c_sdp.cpp

key-decisions:
  - "Kept the temporary SDP_TRACE_DUMP dump helper (dump_strobes_ready_to_paste + test_dump_lock_goldens) permanently behind #ifdef SDP_TRACE_DUMP, matching test_sdp_harness.cpp's style, rather than deleting it after use -- available for any future re-derivation without reconstructing the drive order from scratch."
  - "Cases 18/19 drive the unlock and chip-erase reference tables through drive_reference_emitter (the SAME remap-aware FIXED emitter the lock op itself uses) rather than comparing against the static SDP_FIXED_DIP28_28C256 golden directly -- this is what makes sdp_snapshot's mandatory use load-bearing (drive_reference_emitter's clear_strobes() would otherwise erase the live lock stream) and keeps the comparison apples-to-apples on emitter shape."
  - "DIP32_28C512_EEPROM's lock golden was recorded under the SAME deliberately stale upper-address CONTROL seed (CTRL_ADDRESS_LINE_17|18) cases 4/5 use for the unlock table, per the plan's explicit instruction -- it is NOT length-30/index-27 like the other three; it is length 33 with an extra CONTROL_REGISTER-clearing write folded into write #1 only, confirming the same stale-bit-clearing finding cases 4/5 established for the unlock table now holds for the lock table too."
  - "Case 17's payload index is derived as SDP_FIXED_LOCK_DIP28_28C256_LEN - 3 rather than a second hardcoded 27, so the no-payload proof's own indexing can never silently drift from the golden's actual shape."

requirements-completed: [LOCK-01]

coverage:
  - id: D1
    description: "micros() mock upgraded from a two-slot parity alternator to a scripted tick queue; cases 11 and 12 re-verified by name under it; the t_BLC budget check re-proven load-bearing by a reverted comparison inversion"
    requirement: LOCK-01
    verification:
      - kind: unit
        ref: "pio test -e native -f \"*test_eeprom28c_sdp*\" and -e native_nodevtools -- both 12/12 before Task 3's additions"
        status: pass
      - kind: unit
        ref: "manual: sdp_emit_us > sdp_tblc_budget_us temporarily inverted to <, case 11 (and case 12, as a side effect) observed FAILED, then reverted -- git diff --quiet -- src/proms/eeprom_28c.cpp confirms the revert"
        status: pass
    human_judgment: false
  - id: D2
    description: "Four SDP_FIXED_LOCK_* goldens (DIP28_28C256, DIP28_28C64, DIP24_2816, DIP32_28C512_EEPROM) authored empirically from the production CMD_SDP_LOCK op via a temporary SDP_TRACE_DUMP dump, run from the built binary directly, hand-checked before pasting"
    requirement: LOCK-01
    verification:
      - kind: unit
        ref: "pio test -e native -f \"*test_eeprom28c_sdp*\" cases 13-16 -- pass on first attempt against the dump-derived goldens (no iteration needed)"
        status: pass
    human_judgment: false
  - id: D3
    description: "Cases 13-16: the production lock op's stream matches its pinout's golden exactly, including DIP32 under the deliberately stale upper-address seed"
    requirement: LOCK-01
    verification:
      - kind: unit
        ref: "pio test -e native and -e native_nodevtools -f \"*test_eeprom28c_sdp*\" -- 19/19"
        status: pass
    human_judgment: false
  - id: D4
    description: "Case 17: the no-payload termination asserted positionally -- stream length equals the golden's, final entry is a CE-deassert PIN edge (not DATA), and no DATA entry follows the third write's payload index"
    requirement: LOCK-01
    verification:
      - kind: unit
        ref: "test_case17_lock_terminates_after_three_writes_no_trailing_data -- PASSED"
        status: pass
    human_judgment: false
  - id: D5
    description: "Cases 18/19: exact-divergence-index proofs (index 27, both) against the six-write unlock stream and the chip-erase stream, driven live through the same FIXED emitter"
    requirement: LOCK-01
    verification:
      - kind: unit
        ref: "test_case18_lock_diverges_from_unlock_at_exact_index / test_case19_lock_diverges_from_chip_erase_at_exact_index -- PASSED"
        status: pass
    human_judgment: false
  - id: D6
    description: "Non-regression: every pre-existing SDP_SHIPPED_*/SDP_FIXED_* array proven byte-identical to phase base (additions-only diff); host_stubs_common.inc and sdp_bus_config.h blob-SHA identical; both native envs 123/123 across 17 suites; pio run 3/3 SUCCESS with flash unchanged; host gate set at Plan 119-04's baseline; no production file modified"
    verification:
      - kind: unit
        ref: "diff against git show 1880054:.../sdp_expected.h -- additions only; git hash-object host_stubs_common.inc/sdp_bus_config.h match 1880054"
        status: pass
      - kind: unit
        ref: "pio test -e native / -e native_nodevtools -- 123/123 across 17 suites, both envs"
        status: pass
      - kind: unit
        ref: "pio run -- 3/3 SUCCESS, Leonardo 25954/28672, Uno 23814/32256, uno328pb 23858/32384 (unchanged from 119-04)"
        status: pass
      - kind: unit
        ref: "check_no_log_in_sdp_window.py / check_is_memory_cmd_no_ifdef.py / check_dispatch.py all exit 0; pytest across the five firmware-scanning modules -- 27 passed"
        status: pass
      - kind: unit
        ref: "git diff --quiet -- include/flash_utils.h -- exits 0"
        status: pass
    human_judgment: false

duration: ~50min
completed: 2026-07-28
status: complete
---

# Phase 119 Plan 05: Dump-Authored Lock Goldens, Scripted micros() Queue, and the No-Payload/Divergence Proofs Summary

**Pinned the production `CMD_SDP_LOCK` op's emitted stream byte-exact on all four `0x0D` pinouts against dump-authored goldens (DIP32 under a deliberately stale upper-address seed), proved the no-payload termination and the exact divergence from both the unlock and chip-erase streams positionally, and upgraded the suite's `micros()` mock to a scripted queue so it survives Plan 119-08's upcoming page-load tracker -- LOCK-01 closed.**

## Performance

- **Duration:** ~50 min
- **Completed:** 2026-07-28
- **Tasks:** 3/3
- **Files modified:** 2 (both firmware test files)

## Accomplishments

- Replaced the two-slot `micros()` parity alternator (`s_micros_ticks[2]` indexed by call count modulo 2) with a scripted `std::vector<uint32_t>` queue (`s_micros_script`/`s_micros_cursor`/`s_micros_tail` + `sdp_script_micros()` helper), documented with the retirement reason (D-16's page-load tracker, Plan 119-08, will call `micros()` inside `eeprom28c_write_execute`, which the modulo-2 model cannot survive) and the tail value's exhaustion semantics.
- Re-verified `test_case11_tblc_budget_exceeded_warns` and `test_case12_flag_absent_emits_exactly_two_report_frames` **by name** under the new mock -- both pass unchanged, and Case 12 gained a comment recording that its `write_init`-only scope is now load-bearing (D-16 will add its own `micros()` calls inside `write_execute`, which Case 12 never drives).
- Independently re-proved the t_BLC budget check is load-bearing (not dead code): temporarily inverted `sdp_emit_us > sdp_tblc_budget_us` to `<`, observed Case 11 (and, as a side effect, Case 12) go **RED**, then reverted before committing (`git diff --quiet -- src/proms/eeprom_28c.cpp` confirms).
- Enumerated every frame-count/frame-set assertion across all 17 native suites (full table below) -- only two exist (Cases 11/12 in this suite), and neither drives `eeprom28c_write_execute`, so Plan 119-08's new report line inside `write_execute` perturbs no existing frame-count expectation.
- Authored `SDP_FIXED_LOCK_DIP28_28C256`, `_DIP28_28C64`, `_DIP24_2816`, `_DIP32_28C512_EEPROM` (+ `_LEN` macros) in `_shared/sdp_expected.h`, dump-derived from the production `CMD_SDP_LOCK` op via a temporary `#ifdef SDP_TRACE_DUMP` block (kept permanently behind the ifdef, harness style) built with a one-off `platformio.ini -D SDP_TRACE_DUMP` (reverted before commit) and run from `.pio/build/native/firestarter_native` directly (`pio test` swallows the printf dump).
- Added seven cases (13-19) driving the production lock op end to end: per-pinout stream equality (13-16), the no-payload termination proof (17), and exact-divergence-index proofs against the unlock and chip-erase streams (18-19). All 19/19 in this suite passed **on the first attempt** against the dump-derived goldens.
- Marked **LOCK-01 Complete** in `REQUIREMENTS.md`; confirmed LOCK-02, LOCK-04, LOCK-05, LOCK-06 all still read Pending.

## RESEARCH A1 prediction vs. the dump

RESEARCH A1 predicted, arithmetically, a 30-entry stream with write #3's payload at index 27 (10 entries per un-elided write x 3 writes, none elided since each write's address differs from the one before it). **The dump confirmed this exactly** for the three non-DIP32 pinouts:

| Pinout | Dumped length | Dumped payload index | Predicted length | Predicted index | Match? |
|---|---|---|---|---|---|
| DIP28_28C256 | 30 | 27 (byte 0xA0) | 30 | 27 | YES |
| DIP28_28C64 | 30 | 27 (byte 0xA0) | 30 | 27 | YES |
| DIP24_2816 | 30 | 27 (byte 0xA0) | 30 | 27 | YES |
| DIP32_28C512_EEPROM (stale seed) | **33** | **30** (byte 0xA0) | 30 | 27 | N/A -- A1 did not predict the stale-seed case; the +3/+3 shift is the extra CONTROL_REGISTER-clearing write folded into write #1, matching cases 4/5's finding for the unlock table |

No discrepancy to record for the three non-DIP32 pinouts. The DIP32 golden's different shape is expected, not a prediction miss -- A1's arithmetic covered only the canonical (zero-seed) case, and the plan explicitly required the DIP32 golden to use the stale seed instead.

## Frame-count-assertion inventory (all 17 native suites, per Task 1's RESEARCH Open Question 4)

| Suite | File | What it counts | Drives `eeprom28c_write_execute`? |
|---|---|---|---|
| test_eeprom28c_sdp | test_eeprom28c_sdp.cpp Case 11 (`test_case11_tblc_budget_exceeded_warns`) | Presence/order of two specific report-frame ids in `captured_frames` (not a bare count) | No -- drives `drive_write_init` only |
| test_eeprom28c_sdp | test_eeprom28c_sdp.cpp Case 12 (`test_case12_flag_absent_emits_exactly_two_report_frames`) | `ids.size() == 2` (flag absent) and `ids_skip.size() == 1` (flag set) | No -- drives `drive_write_init` only |
| test_messages | test_rurp_log_id.cpp (8 assertion sites: lines 91, 117, 154, 193, 210, 257, 268, 279) | `captured.size()` -- the BYTE length of a single `rurp_log_id()` call's wire frame, not a count of frames across an operation | No -- calls `rurp_log_id()` directly, never `configure_memory`/any `write_execute` |
| test_cobs_cmd_frame | test_cobs_cmd_frame.cpp | Decoded payload byte length (`(size_t)res`), unrelated to report-frame counting | No |
| test_cobs_data_frame | test_cobs_data_frame.cpp | Decoded payload byte length, unrelated to report-frame counting | No |
| test_frame_vectors | test_frame_vectors.cpp | Built/decoded frame byte length (`vec.frame_len`, `vec.payload_len`), unrelated to report-frame counting | No |
| test_cmd_admission | test_cmd_admission.cpp | Comment only ("produces two error frames") -- no executable assertion; this suite is deliberately orthogonal to `json_parse`/`configure_memory` | No |
| test_dispatch, test_not_implemented, test_data_input, test_read_timing, test_val_eprom, test_val_eeprom28c, test_val_nor_unlock, test_val_5v_page, test_val_flash_intel, test_val_sram, test_sdp_harness | (various) | No frame-count/frame-set assertions found (Serial write mocked with plain `AlwaysReturn(1)`, no capture) | No |

**Conclusion for Plan 119-08:** no existing frame-count assertion anywhere in the 17-suite tree currently covers `eeprom28c_write_execute`. A new report line inside `write_execute` is free to land without re-scoping any case in this file or elsewhere.

## Per-array byte-identity (replaces the whole-file blob-SHA proof for this file only)

`_shared/sdp_expected.h`'s whole-file blob SHA necessarily changed (D-10 forces it, since four new arrays were added). Verified instead:

- `diff` of the current file against `git show 1880054:test/native/avr/_shared/sdp_expected.h` (1880054 = the last commit of Phase 118, i.e. this phase's base, confirmed as `36a85ad^`) shows **additions only** -- every pre-existing `SDP_SHIPPED_*`/`SDP_FIXED_*` array is untouched, byte-for-byte, in the diff.
- The other two `_shared/` files kept the old whole-file shorthand and are confirmed still blob-SHA identical to phase base 1880054: `host_stubs_common.inc` (`675166d...`) and `sdp_bus_config.h` (`e0111e6...`) both match exactly.

## Task Commits

Each task was committed atomically inside the `firestarter/` submodule:

1. **Task 1: Upgrade the micros() mock to a scripted tick queue and re-verify cases 11 and 12** -- `4fcee1c` (test)
2. **Task 2: Author the four SDP_FIXED_LOCK_* goldens empirically from the production lock op** -- `0363d46` (test)
3. **Task 3: Pin the lock stream per pinout, its three-write termination, and its exact divergence indices** -- `730d8e2` (test)

**Plan metadata:** committed alongside this SUMMARY (docs, meta commit staging the gitlink + SUMMARY.md; `firestarter_app/` untouched -- confirmed via `git status --short`, only the same pre-existing unrelated files from prior plans' SUMMARYs remain).

## Files Created/Modified

- `firestarter/test/native/avr/_shared/sdp_expected.h` -- four new `SDP_FIXED_LOCK_*` arrays + `_LEN` macros (additions only; no pre-existing array touched)
- `firestarter/test/native/avr/test_eeprom28c_sdp/test_eeprom28c_sdp.cpp` -- scripted `micros()` queue, `make_lock_handle`/`drive_lock_op` helpers, the temporary (permanently `#ifdef`-gated) `SDP_TRACE_DUMP` dump routine, and cases 13-19

## Decisions Made

See `key-decisions` in frontmatter for the four load-bearing ones (dump-helper retention, reference-emitter comparison shape for cases 18/19, DIP32's stale-seed golden, Case 17's derived-not-hardcoded payload index). All are consistent with the plan's `must_haves.truths`/`prohibitions` verbatim -- no deviation from the plan's explicit instructions was required.

## Deviations from Plan

None -- plan executed exactly as written. RESEARCH A1's prediction held exactly for three of the four pinouts (recorded above, not a deviation since the plan itself anticipated this outcome as the expected case). The DIP32 pinout's different shape (length 33, index 30) is the plan's own explicitly-required stale-seed treatment, not a deviation.

## Issues Encountered

None. All 19 cases in this suite passed on the first build after Task 3's cases were added, confirming the hand-check against the dump (and the hand-derivation performed independently before writing any code) was correct.

## User Setup Required

None -- no external service configuration required.

## Known Stubs

None. This plan is test-only (native Unity suite additions); no UI or data-rendering path is affected, and no production file was modified (`git diff --quiet -- include/flash_utils.h` exits 0, and `git status --short` in the `firestarter/` submodule shows only the two test files across all three task commits).

## Requirement Status

**LOCK-01 is Complete.** `REQUIREMENTS.md` shows only that one row changed (`git diff` confirms); LOCK-02, LOCK-04, LOCK-05, LOCK-06 all still read Pending. **LOCK-05 stays OPEN** as instructed -- this plan advances it (the no-payload stream-length assertion, Case 17, is the stream half of LOCK-05) but does not close it; Plan 119-06 closes LOCK-05 with the three-way table-identity and distinctness guard.

## Next Phase Readiness

- The scripted `micros()` queue (`sdp_script_micros()`) is ready for Plan 119-08's page-load tracker to reuse without needing its own mock upgrade.
- The frame-count-assertion inventory above is the input Plan 119-08 needs to decide what its new `write_execute` report line perturbs (answer: nothing existing).
- `make_lock_handle`/`drive_lock_op` and the four `SDP_FIXED_LOCK_*` goldens are ready for Plan 119-06's three-way identity/distinctness guard (unlock == lock's shared prefix, lock vs. erase, lock vs. `FLASH_ENABLE_WRITE_PROTECTION`).
- Leonardo flash headroom for LOCK-06's later arithmetic is **unchanged at 2718 B free** (this plan is test-only in firmware; `pio run` confirms identical figures to Plan 119-04's ending state).
- No blockers for Plan 119-06.

---
*Phase: 119-lock-sdp-enable-command-surface-fw-half*
*Completed: 2026-07-28*

## Self-Check: PASSED

- FOUND: `firestarter/test/native/avr/_shared/sdp_expected.h`
- FOUND: `firestarter/test/native/avr/test_eeprom28c_sdp/test_eeprom28c_sdp.cpp`
- FOUND: `4fcee1c` (Task 1 commit, firestarter submodule)
- FOUND: `0363d46` (Task 2 commit, firestarter submodule)
- FOUND: `730d8e2` (Task 3 commit, firestarter submodule)
