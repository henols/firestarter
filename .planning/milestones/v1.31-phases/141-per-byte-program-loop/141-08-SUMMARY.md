---
phase: 141-per-byte-program-loop
plan: 08
subsystem: firmware
tags: [firmware, native-test, platformio, unity, overprogram, hard-fail, delay-ceiling, dip32, a16-crossing, gh-15]

# Dependency graph
requires:
  - phase: 141-per-byte-program-loop (141-03)
    provides: native_loop_v131 env, host_stubs.cpp's 16-bit-latched-address read-back model, logged-id capture, drive_loop_write/make_loop_handle/LOOP_BUS_CONFIG_* fixed contract
  - phase: 141-per-byte-program-loop (141-04)
    provides: the rewritten eprom_write_execute per-byte pulse-to-verify loop, eprom_internal_report_budget_failure, eprom_overprogram_us, configure_eprom's D-03 pre-flight refusal
  - phase: 141-per-byte-program-loop (141-07)
    provides: 14 LOOP-01/LOOP-06/LOOP-04 cases (20 total pre-existing) plus two hard-won oracle findings (STROBE_KIND_DATA is not a safe raw pulse-count oracle; VERIFY_PER_PULSE_PLUS_FINAL's final pass adds +1 to every read count on 0x07/0x08)
provides:
  - "LOOP-03 proven through a pure function (eprom_overprogram_us) at all six named boundary inputs: the 3x product, the factor=0 gate every shipped row takes, the cap clamp at and above the boundary, 32-bit safety at 3*25*65535=4915125, and the cap_us=0 fail-safe reading -- the end-to-end path stays unreachable through the loop on any shipped row, exactly as D-08 states"
  - "LOOP-07's arithmetic proven at all eight split boundary rows (16383 not splitting; 16384/50000/75000/65535/4294967295 splitting and staying 32-bit safe) and its emitted call sequence at 75000/16384/0"
  - "LOOP-05 proven: a byte that misses within max_pulses aborts the WHOLE block (bytes after the failure never touched), reports MSG_ERR_MAX_PULSES with the correct u24-address+u8-pulse-count payload, and disables CTRL_VPP_REGULATOR_ENABLE in a non-vacuous, correctly-scoped assertion (operation_main's own strobes, never the whole command) -- paired with a negative control proving a successful block leaves the route set"
  - "LOOP-07's GLOBAL ceiling claim proven under a REAL drive at pulse_delay=50000 (over the 16383us ceiling, reachable today via json_parser.c's unclamped parse): no recorded delayMicroseconds() argument exceeds 16383, and the split's delay(50) calls prove the split actually fired"
  - "D-03's pre-flight refusal proven on 0x0B (the only row where energy_cap_us>0 makes it reachable): MSG_ERR_PULSE_TOO_WIDE with the correct u32 payload, and no CONTROL write ever carries the regulator-enable bit -- paired with a passing control at a legal width"
  - "LOOP-08 proven including the DIP32 A16-crossing seam: the route is asserted once and settled once before the first genuine pulse, survives every per-byte CONTROL rewrite via the unconditional preserve mask (never 'one CONTROL strobe per block', which is false), the drop bit is cleared deliberately before the first pulse on pins>=32 and never reappears, and a 4-byte 0x08 block at base 0x00FFFE genuinely crosses the A16 boundary with the route intact throughout -- backed by three paired negative/positive controls"
affects: [141-09-requirement-flip]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "A non-elided CONTROL_REGISTER write shows up as a fixed 3-entry strobe shape (DATA push carrying the physical byte, then PIN(CONTROL_REGISTER,1), then PIN(CONTROL_REGISTER,0)) -- locate the PIN(1) rising edge and read the DATA entry immediately before it to recover the emitted CONTROL byte in emission order, rather than fighting STROBE_KIND_DATA's known unsoundness as a raw pulse-count oracle."
    - "CTRL_ADDRESS_LINE_16 and CTRL_VPP_VPE_DROP_ENABLE collide onto the SAME physical control-register bit (0x01) under the default test hardware revision (REVISION_0, from host_stubs_common.inc's zero-initialised config) -- a case that must distinguish them (an A16-crossing case vs a drop-bit case on the SAME 32-pin block) must override rurp_get_config()->hardware_revision to a REVISION_2_x value first, where they map to distinct physical bits (0x20 vs 0x01). This is purely a strobe-recording artifact; every eprom.cpp/memory.cpp bit check operates on the pre-remap LOGICAL value and is unaffected."
    - "To drive a DIFFERENT firestarter_operation_main than the one the target protocol's configure_* would install (e.g. mem_util_blank_check instead of eprom_write_execute, as a negative control), set handle->cmd BEFORE calling configure_memory -- configure_memory/configure_eprom's own cmd-keyed switch installs the operation pointer; setting it AFTER configure_memory returns is silently overwritten by that same switch on the next configure_memory call inside drive_loop_write."
    - "loop_readback_reads() returns -1 ONLY for an address that was never seeded at all -- a seeded-but-never-read address (e.g. a byte after an aborted block) returns its own read_count of 0, not -1. Conflating the two is an easy, and easily caught, off-by-one in a fresh case's first draft."

key-files:
  created: []
  modified:
    - firestarter/test/native/avr/test_loop_eprom_v131/test_loop_eprom_v131.cpp

key-decisions:
  - "Deferred the shared CONTROL-write-stream helpers (control_write_count/value/strobe_index, first_genuine_pulse_strobe_index, count_timing_ms) to task 2's commit rather than task 1's, since task 1's pure-function cases need none of them -- task 3 reuses task 2's helpers unchanged."
  - "The LOOP-08 negative control (route presence is not vacuous) drives through mem_util_blank_check rather than a synthetic ctrl_flags path: setting handle.cmd = CMD_BLANK_CHECK BEFORE drive_loop_write's internal configure_memory call causes configure_eprom's own cmd-keyed switch to install mem_util_blank_check as operation_main, which reads every byte via a genuine, non-elided CONTROL write (pins==28 unconditionally ORs CTRL_ADDRESS_LINE_17 into the very first address write) but never asserts the regulator route -- a real, falsifiable, non-empty proof of absence."
  - "The two DIP32 cases (A16-crossing, drop-bit-clear) override rurp_get_config()->hardware_revision to REVISION_2_2 for their own duration, reset unconditionally in a newly-added tearDown() so a mid-case assertion failure (Unity's longjmp) cannot leak the override into a later case. The 28-pin drop-bit control case deliberately stays on the default REVISION_0, since its block never reaches address 0x010000 and its own bit (0x01) can therefore only ever mean the drop bit there."

requirements-completed: []  # Frontmatter requirements: [] is deliberate -- plan 141-09 flips LOOP-03/05/07/08 (and the native half of LOOP-07, already covered) after every piece of evidence exists. No checkbox touched by this plan.

duration: 130min
completed: 2026-08-10
status: complete
---

# Phase 141 Plan 08: LOOP-03/LOOP-05/LOOP-07/LOOP-08 Native Behaviour Cases Summary

**19 new native Unity cases (39 total in `native_loop_v131`) completing the phase's behavioural proof: the overprogram arithmetic as a pure function, the hard-fail exit with a non-vacuous, correctly-scoped route disable, the delay ceiling under a real over-ceiling drive plus the pre-flight refusal, and the DIP32 A16-crossing seam -- with both load-bearing safety assertions seen RED on a planted violation before being restored.**

## Performance

- **Duration:** ~130 min
- **Completed:** 2026-08-10
- **Tasks:** 3
- **Files modified:** 1 (`firestarter/test/native/avr/test_loop_eprom_v131/test_loop_eprom_v131.cpp`, +730 lines net: 994 -> 1723)

## Accomplishments

- **LOOP-03 / LOOP-07 arithmetic** (Task 1, 8 cases): `eprom_overprogram_us` proven at all six named boundary inputs including the factor=0 gate every shipped row takes, the cap clamp at and above the boundary, and 32-bit safety at `3*25*65535=4915125` (which overflows any `uint16_t` intermediate); `mem_util_split_delay` proven at all eight boundary rows including the exact 16383 non-split boundary and 16384's first-split boundary, up to `uint32_t` max; `mem_util_delay_us`'s emitted call sequence proven at 75000 (delay only), 16384 (both), and 0 (neither).
- **LOOP-05 / LOOP-07 drive cases** (Task 2, 5 cases): a byte that misses within `max_pulses` aborts the whole block (the two bytes after it get exactly 0 reads, never -1, since they WERE seeded -- an off-by-one caught and fixed during execution), logs `MSG_ERR_MAX_PULSES` with the correct payload, and disables the regulator route in an assertion correctly scoped to `operation_main`'s own strobes (never the whole command, since `command_done()` zeroes the register on every exit regardless); a paired negative control shows a successful block leaves the route set. LOOP-07's global ceiling claim proven under a real drive at `pulse_delay=50000`; D-03's pre-flight refusal proven on 0x0B with a paired passing control (the second call's shared `logged_ids` array required an explicit `clear_logged_ids()` between the two `configure_memory` calls -- also caught and fixed during execution).
- **LOOP-08** (Task 3, 6 cases): the route is asserted once and settled once, both before the first genuine pulse; survives every per-byte CONTROL rewrite via the unconditional preserve mask (the case explicitly never claims "one CONTROL strobe per block", which is false); a negative control via `mem_util_blank_check` (driven by setting `handle.cmd` before `configure_memory`, since `firestarter_operation_main` set any other way is silently overwritten) shows the bit correctly absent from a genuinely non-empty stream; a 4-byte 0x08 block at base `0x00FFFE` (seeded on the 16-bit latched keys `0xFFFE/0xFFFF/0x0000/0x0001`) genuinely crosses the A16 boundary with the regulator route intact throughout; the 32-pin drop-bit clear is proven deliberate and ordered before the first pulse, with a paired 28-pin control showing the drop bit is kept there.
- **39/39 cases pass** in `native_loop_v131` (20 pre-existing + 19 new, exactly matching the plan's target count). Both pinned envs (`native`, `native_nodevtools`) remain at exactly 141 cases / 17 suites. `native_params_v131` remains 9/9. All three AVR targets build SUCCESS with byte-identical flash/RAM to the pre-plan baseline (uno 24424/1573, uno328pb 24474/1579, leonardo 26400/2014 -- a test-only change moves nothing). `native_trace_v131` remains 3 failed / 2 succeeded of 6, unchanged (D-10, expected). `pytest tests/` is 256/256.
- **140 pre-existing warnings** in `native_loop_v131` (all ArduinoFake/`rurp_platform_compat.h` macro-redefinition noise, matching plans 141-03/141-07's own baseline exactly) -- zero new warnings introduced by this plan's 19 cases.
- **Two planted-RED transcripts captured** (D-15): removing `eprom_internal_report_budget_failure`'s disable call turned `test_loop05_the_loops_own_strobes_disable_the_high_voltage_route` RED on its own "LAST control value... CLEAR" assertion (all 32 other cases stayed green); reintroducing a raw `delayMicroseconds(handle->pulse_delay)` in `memory_set_data` turned `test_loop07_no_recorded_us_delay_exceeds_the_avr_ceiling_under_a_real_drive` RED naming "timing entry 5 (delayMicroseconds) has value 50000" -- both restored via `git checkout -- <file>` and re-confirmed green before the corresponding commit.

## Task Commits

Each task was committed atomically, inside `/workspaces/firestarter` on branch `gsd/v1.31-27c-programming-algorithm-fidelity`:

1. **Task 1: LOOP-03/LOOP-07 arithmetic -- the two pure functions, at their boundaries** - `6cf8194` (test)
2. **Task 2: LOOP-05 hard-fail/disable, LOOP-07's global ceiling under a real drive** - `dcd47e3` (test)
3. **Task 3: LOOP-08 -- route discipline across a DIP32 A16 crossing** - `4921388` (test)

**Plan metadata:** this SUMMARY + STATE.md/ROADMAP.md (meta repo).

## Files Created/Modified

- `firestarter/test/native/avr/test_loop_eprom_v131/test_loop_eprom_v131.cpp` - 19 new behaviour cases (LOOP-03 x5, LOOP-07-arithmetic x3, LOOP-05 x3, LOOP-07-drive x2, LOOP-08 x6) plus five new shared helpers (`control_write_count`, `control_write_strobe_index`, `control_write_value`, `first_genuine_pulse_strobe_index`, `count_timing_ms`) and an extended `tearDown()` (resets the hardware-revision override), appended after plan 141-07's fourteen cases. File grows from 994 to 1723 lines.

## Decisions Made

See frontmatter `key-decisions` for full detail. Summarized:
1. The shared CONTROL-write-stream helpers are introduced in task 2's commit (first use), not task 1's, since task 1's cases are pure-function calls needing no strobe inspection.
2. LOOP-08's "route presence is not vacuous" negative control drives `mem_util_blank_check` by setting `handle.cmd = CMD_BLANK_CHECK` BEFORE `drive_loop_write`'s internal `configure_memory` call -- setting `firestarter_operation_main` directly after `make_loop_handle` is silently overwritten by `configure_memory`/`configure_eprom`'s own cmd-keyed switch.
3. The two DIP32 cases override `rurp_get_config()->hardware_revision` to `REVISION_2_2` (reset in a newly-added `tearDown()`) to avoid the REVISION_0/1 physical-bit collision between `CTRL_ADDRESS_LINE_16` and `CTRL_VPP_VPE_DROP_ENABLE`; the 28-pin drop-bit control case stays on the default revision since its block never reaches the A16 boundary.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] `loop_readback_reads()` on a seeded-but-never-read address returns 0, not -1**
- **Found during:** Task 2, first `pio test -e native_loop_v131` run against the drafted LOOP-05 abort case
- **Issue:** The drafted case asserted `loop_readback_reads(2) == -1` and `loop_readback_reads(3) == -1` for the two bytes after the aborted block, reasoning "never read at all -> -1" by analogy with plan 141-03's harness contract for a genuinely *unseeded* address. But bytes 2 and 3 in this case WERE seeded (`loop_readback_seed(2, ...)` / `loop_readback_seed(3, ...)` were both called, so the loop could be shown to skip them specifically). `loop_readback_reads()`'s own contract (host_stubs.cpp) returns -1 only for an address that was never found in the seeded table at all; a seeded-but-untouched address returns its own `read_count`, which starts at 0 and was never incremented. The test observed `0`, not `-1`.
- **Fix:** Restated the expectation as `0` for both bytes, with a comment explaining the distinction between "never seeded" (-1) and "seeded but never touched" (0).
- **Files modified:** `test_loop_eprom_v131.cpp` (two assertions in `test_loop05_a_byte_that_misses_within_max_pulses_aborts_the_block`)
- **Verification:** `pio test -e native_loop_v131` re-run -- case passes with the corrected expectation.
- **Committed in:** `dcd47e3` (Task 2)

**2. [Rule 1 - Bug] The shared `logged_ids` array leaked a frame across two `configure_memory` calls in the same case**
- **Found during:** Task 2, same first test run as Deviation 1
- **Issue:** `test_loop07_an_over_cap_pulse_is_refused_before_any_high_voltage_on_a_capped_row` calls `configure_memory` twice within one case: once on a handle expected to be REFUSED (`pulse_delay=60000`), once on a paired passing control (`pulse_delay=500`) expected to log NOTHING. `setUp()` clears the logged-id capture once per CASE, not once per `configure_memory` call, so the first call's legitimate `MSG_ERR_PULSE_TOO_WIDE` frame was still present when the second call's `count_logged_id(MSG_ERR_PULSE_TOO_WIDE) == 0` assertion ran, observing `1` instead.
- **Fix:** Added an explicit `clear_logged_ids(); clear_strobes();` between the two `configure_memory` calls, with a comment naming the shared-array reason.
- **Files modified:** `test_loop_eprom_v131.cpp` (same case)
- **Verification:** `pio test -e native_loop_v131` re-run -- case passes; the passing control's own count is correctly 0.
- **Committed in:** `dcd47e3` (Task 2)

---

**Total deviations:** 2 auto-fixed (both Rule 1 -- bugs in this plan's own drafted test assertions, discovered only by actually running the suite against the real production code; neither required any change to `src/`)
**Impact on plan:** Zero impact on scope or on any shipped production behaviour -- both deviations are test-authoring corrections, each caught by the plan's own mandatory `pio test -e native_loop_v131` verification step before any commit, and each is now documented in the test file itself as a comment.

## Planted-RED Transcripts (D-15)

**Case 2 (`test_loop05_the_loops_own_strobes_disable_the_high_voltage_route`) -- disable call removed:**

Planted violation in `src/proms/eprom.cpp`, `eprom_internal_report_budget_failure`:
```
-    handle->firestarter_set_control_register(handle, CTRL_VPP_REGULATOR_ENABLE, 0);
+    // PLANTED VIOLATION (141-08 D-15 proof, reverted before commit):
+    // handle->firestarter_set_control_register(handle, CTRL_VPP_REGULATOR_ENABLE, 0);
```
Observed RED (`pio test -e native_loop_v131`):
```
test/native/avr/test_loop_eprom_v131/test_loop_eprom_v131.cpp:1266: test_loop05_the_loops_own_strobes_disable_the_high_voltage_route:
  the LAST control value emitted by operation_main must have CTRL_VPP_REGULATOR_ENABLE CLEAR
  -- eprom_internal_report_budget_failure's own disable  [FAILED]
34 test cases: 1 failed, 32 succeeded
```
Only the target case failed, on its own named assertion (not a compile or seeding error). Reverted via `git checkout -- src/proms/eprom.cpp`; re-run confirmed 33/33 green.

**Case 4 (`test_loop07_no_recorded_us_delay_exceeds_the_avr_ceiling_under_a_real_drive`) -- raw `delayMicroseconds` reintroduced:**

Planted violation in `src/proms/memory.cpp`, `memory_set_data`:
```
-    mem_util_delay_us(handle->pulse_delay);
+    delayMicroseconds(handle->pulse_delay);  // PLANTED VIOLATION (141-08 D-15 proof, reverted before commit)
```
Observed RED (`pio test -e native_loop_v131`):
```
test/native/avr/test_loop_eprom_v131/test_loop_eprom_v131.cpp:1326: test_loop07_no_recorded_us_delay_exceeds_the_avr_ceiling_under_a_real_drive:
  timing entry 5 (delayMicroseconds) has value 50000 -- must be <= 16383
  (the AVR delayMicroseconds() accurate ceiling)  [FAILED]
34 test cases: 1 failed, 32 succeeded
```
Only the target case failed, naming the exact entry index (5) and the exact offending value (50000). Reverted via `git checkout -- src/proms/memory.cpp`; re-run confirmed 33/33 green.

`git status --porcelain src/ include/` was empty after both plant/revert cycles, confirmed before each commit.

## Issues Encountered

None beyond the two auto-fixed deviations above, both caught by the plan's own mandatory verification step before any commit.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- **Ready for plan 141-09** (the requirement flip): LOOP-03, LOOP-05, LOOP-07 (arithmetic and drive halves) and LOOP-08 are now fully proven natively, with 39/39 cases green in `native_loop_v131` (a run-by-name obligation, no CI leg in either repo, per D-10 -- record this count, not an assumed CI pass). Combined with plan 141-07's own LOOP-01/LOOP-04/LOOP-06 proof and plan 141-06's native half of LOOP-07 already in place, all eight `LOOP-*` requirements now have their full evidence base. No requirement checkbox was touched by this plan; `REQUIREMENTS.md` is untouched.
- **Handed to Phase 142** (unchanged by this plan, as required): the duplicated VPP-route predicate, the DIP32 route choice (P1 vs drop resistor) and consolidating the mask sets, and generalising the budget-failure reporter's route-disable to every exit -- all named in this plan's own case comments (`Phase 142 / VPP-01`, `VPP-02`, `VPP-03`).
- No blockers or concerns for any downstream plan. Both deviations above are fully resolved and verified; neither is deferred.

---
*Phase: 141-per-byte-program-loop*
*Completed: 2026-08-10*

## Self-Check: PASSED

- FOUND: firestarter/test/native/avr/test_loop_eprom_v131/test_loop_eprom_v131.cpp
- FOUND: .planning/phases/141-per-byte-program-loop/141-08-SUMMARY.md
- FOUND: 6cf8194 (git -C firestarter log --oneline --all)
- FOUND: dcd47e3 (git -C firestarter log --oneline --all)
- FOUND: 4921388 (git -C firestarter log --oneline --all)
