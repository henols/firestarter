---
phase: 141-per-byte-program-loop
plan: 07
subsystem: firmware
tags: [firmware, native-test, platformio, unity, loop-cadence, energy-cap, skip-rules, gh-15]

# Dependency graph
requires:
  - phase: 141-per-byte-program-loop (141-03)
    provides: native_loop_v131 env, host_stubs.cpp's 16-bit-keyed read-back model, logged-id capture, drive_loop_write/make_loop_handle/LOOP_BUS_CONFIG_* fixed contract
  - phase: 141-per-byte-program-loop (141-04)
    provides: the rewritten eprom_write_execute per-byte pulse-to-verify loop, eprom_internal_report_budget_failure, eprom_overprogram_us
provides:
  - "LOOP-01 proven natively: fixed-width pulses (value set {1,3,100} on the delayMicroseconds stream, 1 being register-shift overhead not growth), one verify read per pulse, an exact per-byte pulse count (cross-checked by both loop_readback_reads and a by-value strobe filter), and success at the max_pulses=25 boundary"
  - "LOOP-06 proven natively in both directions: a 0xFF byte gets ZERO reads, an already-matching byte gets exactly ONE read and no pulse, an all-0xFF block emits no pulse (with a paired negative control above the structural 1-strobe floor), and the VERIFY_PER_PULSE_PLUS_FINAL final pass still reads a fully-skipped block"
  - "LOOP-04 proven natively at all three shipped 0x0B widths: exactly 100/50/250 pulses at 500/1000/200us, MSG_ERR_ENERGY_CAP (never MSG_ERR_MAX_PULSES) logged with the correct u24-address+u8-pulse-count payload, no overprogram pulse on any of the three live rows, and no final full-block verify pass on 0x0B's VERIFY_PER_PULSE row"
  - "A documented finding: rurp_internal_write_to_register shifts every non-elided register write (LSB/MSB/CONTROL) through the SAME rurp_write_data_buffer() call a genuine chip-data pulse uses, so STROBE_KIND_DATA is not a safe raw pulse-count oracle -- the by-value filter (count_data_pulses_with_value) is the robust replacement, now available to plan 141-08"
affects: [141-08-dip32-overprogram-cases, 141-09-requirement-flip]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Filter STROBE_KIND_DATA entries by strobe_value() == the expected byte, not by raw count, whenever a native case needs to prove an exact pulse count -- register-shift writes (LSB/MSB/CONTROL latches) push the identical strobe kind/pin shape as a genuine chip-data pulse, and for at least one bus_config (0x08's rw_line-keyed CONTROL toggle) that noise SCALES with pulse count rather than adding a fixed per-drive floor, so neither a bare count nor a 0-pulse baseline delta is sound in general."
    - "loop_readback_reads() alone cannot prove absence of a pulse that is not followed by a verify read (D-07's overprogram save/restore idiom never calls get_data) -- only a strobe-level, by-value signal can."
    - "On a VERIFY_PER_PULSE_PLUS_FINAL protocol (0x07/0x08), every loop_readback_reads() count in a native case must add +1 for the unconditional final full-block pass, which reads every byte once more regardless of whether it converged, was skipped, or already matched."

key-files:
  created: []
  modified:
    - firestarter/test/native/avr/test_loop_eprom_v131/test_loop_eprom_v131.cpp

key-decisions:
  - "Cases proving LOOP-06 (0xFF-skip and already-matching-skip) are driven on protocol 0x0B, not 0x07 as the plan's <action> prose specified -- 0x07 ships VERIFY_PER_PULSE_PLUS_FINAL, whose unconditional final pass would add +1 to every loop_readback_reads() value and directly contradict the plan's own <acceptance_criteria> numbers (0 reads for the 0xFF byte, 1 read for the already-matching byte). 0x0B (VERIFY_PER_PULSE, no final pass) is the only protocol on which those exact numbers are literally true. The plan's own case 4 (deliberately 0x07) exists specifically to prove the final pass still runs -- confirming 0x0B was the intended choice for cases 1-3, and 0x07 the intended choice only for case 4."
  - "STROBE_KIND_DATA is proven, empirically, NOT to be a safe raw pulse-count oracle: rurp_internal_write_to_register (include/rurp_register_utils.h) shifts every non-elided LSB/MSB/CONTROL register write through the identical rurp_write_data_buffer() call memory_set_data uses for a genuine chip-data pulse -- same kind, same pin (0). Replaced every strobe-count-based pulse assertion with a filter on the strobe's VALUE (the byte actually programmed), which a register value can never coincidentally match for the addresses this suite uses."
  - "LOOP-04's all-0xFF-block assertion is 1, not 0: the once-per-block VPE-assert control-register write always fires (the cache always starts clear), producing exactly one STROBE_KIND_DATA entry that is structural, not caused by any byte. The paired negative control asserts > 1 (not > 0) so it cannot pass vacuously against that unavoidable floor."
  - "Every loop_readback_reads() expectation on a VERIFY_PER_PULSE_PLUS_FINAL protocol (0x07/0x08) case is stated as 2 + pulses (not 1 + pulses): 1 skip-check read + N verify reads + 1 unconditional final-pass read."

requirements-completed: []  # Frontmatter requirements: [] is deliberate -- plan 141-09 flips LOOP-01/04/06 after every piece of evidence exists. No checkbox touched by this plan.

duration: 100min
completed: 2026-08-10
status: complete
---

# Phase 141 Plan 07: LOOP-01/LOOP-06/LOOP-04 Native Behaviour Cases Summary

**14 new native Unity cases (20 total in `native_loop_v131`) proving the per-byte loop's fixed-width cadence, its two skip rules, and the 0x0B energy cap at all three shipped widths -- driven against the real `eprom_write_execute`, with a documented finding that register-shift writes share `STROBE_KIND_DATA`'s exact shape with a genuine chip-data pulse and must be filtered by value, not counted raw.**

## Performance

- **Duration:** ~100 min (includes empirical debugging of two structural findings not knowable from source reading alone)
- **Completed:** 2026-08-10T21:59:27Z
- **Tasks:** 3
- **Files modified:** 1 (`firestarter/test/native/avr/test_loop_eprom_v131/test_loop_eprom_v131.cpp`, +590 lines net: 401 -> 994)

## Accomplishments

- **LOOP-01** (Task 1, 4 cases): each byte in a 4-byte 0x07 block gets exactly its seeded number of fixed-width pulses (cross-checked by both `loop_readback_reads()` and a by-value strobe filter); the `delayMicroseconds()` value set stays `{1, 3, 100}` with no fourth/growth value; a verify read follows every pulse; a byte converging on its very last permitted pulse (25/25) succeeds rather than failing at the boundary.
- **LOOP-06** (Task 2, 4 cases): a 0xFF target byte gets zero reads and zero pulses; an already-matching byte gets exactly one read and zero pulses; a block of only skipped bytes emits no pulse at all (backed by a strobe-count negative control above the structural floor); the `VERIFY_PER_PULSE_PLUS_FINAL` final pass still reads every byte of a fully-skipped block.
- **LOOP-04** (Task 3, 6 cases): the 0x0B energy cap stops at exactly 100/50/250 pulses at 500/1000/200us, each logging `MSG_ERR_ENERGY_CAP` (never `MSG_ERR_MAX_PULSES`, though `max_pulses`=255 is above all three) with the correct u24-address + u8-pulse-count payload; no live row (0x07/0x08/0x0B) emits a third, overprogram pulse; 0x0B runs no final full-block verify pass, unlike 0x07/0x08.
- **20/20 cases pass** in `native_loop_v131` (6 pre-existing harness cases from plan 141-03 + 14 new); both pinned envs (`native`, `native_nodevtools`) remain at exactly 141 cases / 17 suites; `native_params_v131` remains 9/9; all three AVR targets (uno/uno328pb/leonardo) build SUCCESS with byte-identical flash/RAM to the pre-plan baseline (24424/1573, 24474/1579, 26400/2014 -- a test-only change moves nothing); `pytest tests/` is 256/256.
- **140 pre-existing warnings** in `native_loop_v131` (all ArduinoFake/`rurp_platform_compat.h` macro-redefinition noise, matching plan 141-03's own baseline exactly) -- zero new warnings introduced by this plan's 14 cases.

## Task Commits

Each task was committed atomically, inside `/workspaces/firestarter` on branch `gsd/v1.31-27c-programming-algorithm-fidelity`:

1. **Task 1: LOOP-01 -- fixed-width pulses, verify after each, per-byte pulse count** - `1cceb12` (test)
2. **Task 2: LOOP-06 -- skip rules for 0xFF and already-matching bytes** - `0281034` (test)
3. **Task 3: LOOP-04 -- the 0x0B energy cap at all three shipped widths** - `56e9830` (test)

**Plan metadata:** this SUMMARY + STATE.md/ROADMAP.md (meta repo).

## Files Created/Modified
- `firestarter/test/native/avr/test_loop_eprom_v131/test_loop_eprom_v131.cpp` - 14 new behaviour cases (LOOP-01 x4, LOOP-06 x4, LOOP-04 x6) plus four new local helpers (`count_logged_id`, `count_data_pulses_with_value`, `count_strobe_kind`, `find_logged_id`, `k0b`), appended after plan 141-03's six harness cases; file grows from 401 to 994 lines.

## Decisions Made

See frontmatter `key-decisions` for full detail. Summarized:
1. LOOP-06 cases 1-3 drive protocol 0x0B (not 0x07 as the plan's action prose said) so the plan's own literal acceptance numbers are actually true against 0x07's unconditional final verify pass.
2. `STROBE_KIND_DATA` counts must be filtered by byte VALUE, never taken raw, because register-shift writes (LSB/MSB/CONTROL) are indistinguishable-by-kind from a genuine chip-data pulse -- and for 0x08 specifically that noise scales with pulse count, not just a fixed per-drive floor.
3. LOOP-06's all-0xFF-block strobe assertion is `1` (the structural once-per-block VPE-assert write), not `0`; its negative control requires `> 1`.
4. Every read-count expectation on a `VERIFY_PER_PULSE_PLUS_FINAL` protocol case is `2 + pulses`, not `1 + pulses`.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] LOOP-06 cases 1-3 use protocol 0x0B, not 0x07 as the plan's `<action>` prose specified**
- **Found during:** Task 2, first `pio test -e native_loop_v131` run
- **Issue:** The plan's action text names protocol 0x07 for cases 1-3 ("same protocol" for case 2). 0x07 ships `VERIFY_PER_PULSE_PLUS_FINAL` (`eprom_params.cpp:46`); `eprom_write_execute`'s final full-block pass reads EVERY byte once more, unconditionally, after the per-byte loop -- including 0xFF-skipped and already-matching bytes. Driving cases 1-3 on 0x07 as written would make `loop_readback_reads()` for the 0xFF byte come back `1` (not the plan's own stated `0`) and for the already-matching byte come back `2` (not the plan's own stated `1`) -- the plan's `<action>` prose and its own `<acceptance_criteria>` numbers are mutually inconsistent for that protocol choice.
- **Fix:** Drove cases 1-3 on protocol 0x0B (`VERIFY_PER_PULSE`, no final pass), on which every stated acceptance number (0 reads for the 0xFF byte; 1 and 3 reads for the already-matching-byte case) is literally true. Case 4 (the plan's own dedicated "final pass still runs" case) stays on 0x07 -- it is the case that specifically needs the PLUS_FINAL protocol to be meaningful, confirming 0x0B was the intended choice for 1-3 and 0x07 only for case 4. Documented as a file-level comment ahead of the LOOP-06 section.
- **Files modified:** `test_loop_eprom_v131.cpp` (protocol/handle literals in cases 1-3 only; assertion values match the plan's own stated numbers unchanged)
- **Verification:** `pio test -e native_loop_v131` -- all four LOOP-06 cases pass with the plan's own literal acceptance numbers.
- **Committed in:** `0281034` (Task 2)

**2. [Rule 1 - Bug] `STROBE_KIND_DATA` raw counts are not a sound pulse-count oracle -- register-shift writes share the identical strobe shape**
- **Found during:** Task 1, first `pio test -e native_loop_v131` run against the drafted LOOP-01/LOOP-06/LOOP-04 cases (8 of 21 registered cases failed, plus a `SIGFPE` crash from an unrelated array-bounds issue in a since-removed debug probe)
- **Issue:** `rurp_internal_write_to_register` (`include/rurp_register_utils.h:63-89`, production code, real via `HOST_STUBS_REAL_REGISTER_UTILS`) shifts every non-elided LSB/MSB/CONTROL register write through `rurp_write_data_buffer()` -- the exact same function `memory_set_data` calls for the genuine chip-data pulse. Both therefore push an indistinguishable-by-kind `STROBE_KIND_DATA` entry. A drafted case asserting a bare `count_strobe_kind(STROBE_KIND_DATA) == 10` for a 4-byte 0x07 block observed `19`, not `10`: the once-per-block VPE-assert control write (always non-elided, cache starts clear) and, for a pins==28 handle specifically, `mem_util_calculate_top_address_register`'s unconditional `CTRL_ADDRESS_LINE_17` OR into the first address-set (`memory.cpp:196-198`, a 28-pin electrical quirk unrelated to any of LOOP-01/04/06's claims) both contribute additional, indistinguishable `STROBE_KIND_DATA` entries. Attempting to fix this with an empirically-measured "0-pulse baseline, then delta" technique also failed for protocol 0x08 specifically: `LOOP_BUS_CONFIG_0x08`'s `rw_line` (22) makes every read<->write direction change force a non-elided `CONTROL` rewrite, so that noise SCALES with pulse count (a 2-pulse run showed a delta of 6 against its own 0-pulse baseline, not 2) rather than adding a fixed per-drive floor.
- **Fix:** Replaced every pulse-count-via-strobes assertion with a filter on the strobe's VALUE, not a raw count: `count_data_pulses_with_value(byte)` counts only `STROBE_KIND_DATA` entries whose recorded value equals the actual byte being programmed. A genuine pulse's `rurp_write_data_buffer(data)` call always carries `data == expected`; a register-shift's call carries a register value (an LSB/MSB address byte under 256, or a CONTROL bitmask in the 0x80-0x91 range) that can never coincidentally equal any of this file's chosen byte values (0x3C, 0x55, 0xAA, 0x0F). This is sound regardless of how the register-write noise scales, and needed no baseline drive at all. Also discovered and documented a third legitimate `delayMicroseconds()` value (`1`, `rurp_internal_write_to_register`'s own fixed post-latch delay, `include/rurp_register_utils.h:86`) that LOOP-01 case 2's timing-value-set check had to be widened to allow (`{1, 3, 100}`, not `{3, 100}`) -- `1` is register-shift overhead, not LOOP-02's adaptive growth.
- **Files modified:** `test_loop_eprom_v131.cpp` (LOOP-01 cases 1-3, LOOP-06 case 3, LOOP-04 case 5 -- all strobe-count-based assertions; added `count_data_pulses_with_value`, `count_strobe_kind` helpers; removed a since-abandoned `measure_data_strobe_noise_floor` helper used only during the intermediate baseline-delta attempt)
- **Verification:** `pio test -e native_loop_v131` -- all 20 cases pass. Cross-checked `count_data_pulses_with_value`'s soundness by construction (byte values chosen never collide with any observed register value in these specific handle/address scenarios) rather than by further empirical probing.
- **Committed in:** `1cceb12` (Task 1, for the LOOP-01/count_data_pulses_with_value portion), `0281034` (Task 2, for the LOOP-06 case 3 portion), `56e9830` (Task 3, for the LOOP-04 case 5 portion) -- the finding and its fix span all three task commits since the plan's own strobe-count assertions appeared in cases across all three tasks.

**3. [Rule 1 - Bug] `loop_readback_reads()` expectations on `VERIFY_PER_PULSE_PLUS_FINAL` protocols must add +1 for the final pass**
- **Found during:** Task 1, same first test run as Deviation 2
- **Issue:** LOOP-01's four cases all drive protocol 0x07 (`VERIFY_PER_PULSE_PLUS_FINAL`). The drafted read-count expectations assumed `loop_readback_reads(addr) == 1 + pulses` (skip-check + N verify reads only), observing e.g. `3` where `2` was expected for a byte needing 1 pulse. The unconditional final full-block pass (`eprom.cpp:296-314`) reads every byte one more time after the per-byte loop, regardless of convergence, adding exactly 1 more read to every byte's count.
- **Fix:** Restated every LOOP-01 read-count expectation as `2 + pulses` and documented the mapping explicitly in each case's comment.
- **Files modified:** `test_loop_eprom_v131.cpp` (LOOP-01 cases 1 and 4)
- **Verification:** `pio test -e native_loop_v131` -- both cases pass with the corrected counts.
- **Committed in:** `1cceb12` (Task 1)

---

**Total deviations:** 3 auto-fixed (all Rule 1 -- bugs in this plan's own drafted test assertions, discovered only by actually running the suite against the real production code; none required any change to `src/`)
**Impact on plan:** Zero impact on scope or on any shipped production behaviour -- all three deviations are test-authoring corrections, each caught by the plan's own mandatory `pio test -e native_loop_v131` verification step before any commit, and each is now documented in the test file itself as a comment so a future reader of plan 141-08 (which extends this same file) does not rediscover the same traps.

## Issues Encountered

An early debugging aid (a temporary `DEBUG_test_loop01_dump` case using `printf`) was added, used to capture the exact strobe/read sequence that led to Deviation 2's finding, and removed before any commit -- it never reached a commit and is not part of the final suite.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- **Ready for plan 141-08** (LOOP-03, LOOP-05, LOOP-07, LOOP-08 cases, extending this same file): inherits `count_logged_id`, `count_strobe_kind`, `find_logged_id`, `k0b`, and `count_data_pulses_with_value` -- the last of these is the load-bearing replacement for any strobe-based pulse-count claim plan 141-08 might need, and its own comment documents why a raw `STROBE_KIND_DATA` count is unsound. Plan 141-08 should read this SUMMARY's Deviations 1-3 before drafting its own assertions, since the same traps (final-pass +1, register-shift noise, protocol choice for skip-rule cases) are structurally available to recur there too.
- **Ready for plan 141-09** (the requirement flip): LOOP-01, LOOP-04 and LOOP-06 are now fully proven natively, with 20/20 cases green in `native_loop_v131` (a run-by-name obligation, no CI leg in either repo, per D-10 -- record this count, not an assumed CI pass). No requirement checkbox was touched by this plan; `REQUIREMENTS.md` is untouched.
- No blockers or concerns for any downstream plan. The three deviations above are fully resolved and verified; none is deferred.

---
*Phase: 141-per-byte-program-loop*
*Completed: 2026-08-10*

## Self-Check: PASSED

- FOUND: firestarter/test/native/avr/test_loop_eprom_v131/test_loop_eprom_v131.cpp
- FOUND: .planning/phases/141-per-byte-program-loop/141-07-SUMMARY.md
- FOUND: 1cceb12 (git -C firestarter log --oneline --all)
- FOUND: 0281034 (git -C firestarter log --oneline --all)
- FOUND: 56e9830 (git -C firestarter log --oneline --all)
