---
phase: 142-high-voltage-routing
plan: 02
subsystem: firmware
tags: [avr, unity, native-tests, eprom, vpp, hardware-revision, memory-utils, rurp_pinout]

# Dependency graph
requires:
  - phase: 142-01
    provides: "test_vpp_eprom_v131 suite skeleton wired into [env:native_loop_v131]; host_stubs.cpp's HOST_STUBS_REAL_REGISTER_UTILS strobe recorder; make_vpp_handle, VPP_BUS_CONFIG_0x08, reset_register_cache, control_write_count/_value, EPROM_HV_ROUTE_MASK/EPROM_HV_ALL_OFF_MASK, use_revision_2_2_for_this_case idiom"
provides:
  - "mem_util_calculate_top_address_register (memory.cpp) preserves CTRL_VPP_VPE_DROP_ENABLE for pins >= 32 on Rev 2-class hardware only (D-01/D-02), via an explicit four-case switch inside #ifdef HARDWARE_REVISION with a do-nothing default"
  - "A nine-row (pins, revision) preserve-mask truth table plus a 32-pin non-EPROM byte-identity baseline in test_vpp_eprom_v131.cpp, authored RED-before-GREEN"
  - "Empirical proof that the 0x08 write path is unmoved at this commit (eprom.cpp:217-219 still clears the bit before the first set_address) -- discharges L-3's ordering-safety claim for plan 142-04"
  - "The memory.cpp:187-190 hand-off comment (S-1) retired and replaced with the level-not-route / physical-jumper / revision-alone / Rev0-1-collision / fail-safe-default / widened-reach / named-proofs framing"
affects: [142-04, 142-05, 142-07]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "In-.cpp #ifdef HARDWARE_REVISION else-arm switch over rurp_get_hardware_revision(), explicit four-case Rev-2-class set with a do-nothing default -- pattern-matched from rurp_hw_rev_utils.h's own fail-safe mapper (F-3), applied here for the first time inside memory.cpp rather than inside the mapper itself"
    - "D-15 planted-violation-then-restore proof scoped via a single-use local boolean flag (set only inside the matched switch cases, consumed once after the mask application) rather than an unconditional statement -- keeps a temporary violation's blast radius identical to the real arm's scope so the RED result isolates the right rows"

key-files:
  created: []
  modified:
    - firestarter/src/proms/memory.cpp
    - firestarter/test/native/avr/test_vpp_eprom_v131/test_vpp_eprom_v131.cpp

key-decisions:
  - "D-01/D-02 implemented verbatim as amended: the pins < 32 arm is untouched; the new pins >= 32 preserve is gated on rurp_get_hardware_revision() alone (never handle->protocol, never a new handle field), inside #ifdef HARDWARE_REVISION, as an explicit four-case switch (REVISION_2_0/2_1/2_2/2_3) with a do-nothing default"
  - "Group A's nine truth-table rows are nine separate Unity test functions (not one table-driven function) so pio test's per-case report shows exactly which rows are RED -- a single function would longjmp out on the first TEST_ASSERT failure and hide the rest"
  - "Group B's protocol literal is written as raw hex 0x10 with a `/* PROTO_FLASH_INTEL */` comment, not the proto_constants.h symbolic constant -- matches the sibling test_loop_eprom_v131.cpp house convention (raw hex protocol literals throughout) and avoids adding a new include edge to a file that doesn't otherwise need proto_constants.h"
  - "P2's planted violation is implemented via a single local bool (p2_force_drop) set only inside the matched Rev-2-class switch cases and consumed once, immediately after the mask is applied to top_address -- this keeps the violation scoped to exactly the Rev-2 32-pin arm (not a blanket top_address |= that would also corrupt pins<32 rows), matching the plan's 'stray OR instead of a preserve' framing precisely"

patterns-established: []

requirements-completed: []

coverage:
  - id: T1
    description: "Nine-row (pins, revision) preserve-mask truth table plus the 32-pin non-EPROM byte-identity baseline, calling mem_util_calculate_top_address_register directly in logical bit space; RED-before-GREEN against unchanged memory.cpp"
    verification:
      - kind: unit
        ref: "pio test -e native_loop_v131 -f \"*test_vpp_eprom_v131*\" (direct binary invocation, .pio/build/native_loop_v131/firestarter_native): 11 Tests, 3 Failures, 0 Ignored -- exactly the pins==32 REVISION_2_0/2_2/2_3 rows, each failing its own named TEST_ASSERT"
        status: pass
      - kind: other
        ref: "git diff --exit-code -- src/proms/memory.cpp exits 0 (no production source touched by this task)"
        status: pass
      - kind: other
        ref: "pio test -e native / -e native_nodevtools -- both unmoved at 141 test cases: 141 succeeded, 17 suites"
        status: pass
    human_judgment: false
  - id: T2
    description: "Revision-gated preserve arm landed in memory.cpp; hand-off comment retired; both D-15 green-on-arrival legs (P1 unconditional preserve, P2 stray OR) seen RED on a named planted violation and restored; full sweep unmoved"
    verification:
      - kind: unit
        ref: "pio test -e native_loop_v131 -- 50/50 green (both suites); the same Group B literals (count=1, physical byte 0x20) measured pre-change in T1 reproduce unchanged post-change -- D-02's byte-identity proof"
        status: pass
      - kind: other
        ref: "Planted violation P1 (unconditional preserve, no revision gate): pins==32 REVISION_1/REVISION_0/REVISION_UNKNOWN rows go RED on their own TEST_ASSERT; Rev-2-class rows and Group B stay green. Restored, re-ran green."
        status: pass
      - kind: other
        ref: "Planted violation P2 (stray OR into top_address instead of into mask): test_vpp01_truthtable_pins32_rev2_2_preserve_never_introduces AND test_vpp01_dip32_nonEprom_0x10_route_is_byte_identical_before_and_after both go RED (leaked physical byte 0x01). Restored, re-ran green."
        status: pass
      - kind: unit
        ref: "pio test -e native / -e native_nodevtools -- unmoved at 141/141, 17 suites each"
        status: pass
      - kind: other
        ref: "python3 scripts/check_build_warnings.py --rebuild -- native/native_nodevtools 998/1166 (unmoved, 168 below watermark); uno/uno328pb/leonardo macro_redefinition=0; all three link"
        status: pass
      - kind: other
        ref: "pio run -e uno / -e uno328pb / -e leonardo -- all SUCCESS; leonardo 26404/28672 B (92.1%), 2268 B headroom (4 B added vs. the Phase 141 tip's 26400 B)"
        status: pass
      - kind: other
        ref: "python3 -m pytest tests/ -o addopts=\"\" -q -- 256 passed (committed first, per L-1)"
        status: pass
      - kind: other
        ref: "pio test -e native_trace_v131 -- expected RED (D-17), not fixed: Expected 198 Was 91 (0x07), Expected 221 Was 119 (0x08), Expected 201 Was 59 (0x0B) -- byte-identical to the Phase 141 tip recorded in 141-NEW-TRACE.md and 142-RESEARCH.md, confirming the strobe stream is unmoved by this plan"
        status: pass

duration: 28min
completed: 2026-08-11
status: complete
---

# Phase 142 Plan 02: High-Voltage Routing -- Revision-Gated Drop-Bit Preserve Summary

**`mem_util_calculate_top_address_register` now preserves `CTRL_VPP_VPE_DROP_ENABLE` for 32-pin EPROM parts on Rev 2-class hardware (an explicit four-case switch inside `#ifdef HARDWARE_REVISION`), proven by a RED-before-GREEN nine-row truth table and two planted-violation transcripts, with the `0x08` write path empirically unmoved at this commit.**

## Performance

- **Duration:** 28 min
- **Started:** 2026-08-11T21:51:54Z
- **Completed:** 2026-08-11T22:19:27Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments
- Authored a nine-row `(pins, revision)` truth table in `test_vpp_eprom_v131.cpp` calling `mem_util_calculate_top_address_register` directly in logical bit space -- covering both unchanged-behaviour rows (`pins==28`), the three new-behaviour rows (`pins==32` at `REVISION_2_0`/`_2_2`/`_2_3`), the three fail-safe negatives (`pins==32` at `REVISION_1`/`REVISION_0`/`REVISION_UNKNOWN`), and a structural "preserve, never introduce" leg -- plus a 32-pin non-EPROM (`protocol = 0x10`) address sweep across the A16 boundary asserting byte-identity against a measured pre-change literal sequence.
- Confirmed via **direct binary invocation** (bypassing a `pio test` CLI wrapper quirk, see Issues Encountered) that against the unchanged tree, exactly the three `pins==32` Rev-2-class rows go RED on their own named `TEST_ASSERT`, and every other row -- including the Group B byte-identity baseline -- is GREEN. Captured the measured baseline literal (one non-elided `CONTROL_REGISTER` write, physical byte `0x20`) as the "before" side of D-02's byte-identity claim.
- Landed the revision-gated preserve arm in `memory.cpp`: the pre-existing `pins < 32` arm is untouched; a new `#ifdef HARDWARE_REVISION`-wrapped `else` arm adds a `switch` over `rurp_get_hardware_revision()` with an explicit four-case Rev-2-class set (`REVISION_2_0`/`_2_1`/`_2_2`/`_2_3`, never a range test) that also preserves the drop bit, with a `default: break;` that adds nothing -- the fail-safe direction for `REVISION_0`, `REVISION_1`, `REVISION_UNKNOWN`, and any unrecognised byte.
- Retired the `memory.cpp:187-190` hand-off comment (S-1) in place, replacing it with all seven required points: the level-not-route framing (Phase 141 H1), the physical-jumper framing (operator's verbatim correction, no jumper designator or net asserted), the revision-alone rationale with both rejected alternatives named, the Rev 0/1 physical-`0x01` collision, the fail-safe `default` direction, the widened nominal reach, and the two named proofs that close it.
- Armed both D-15 green-on-arrival legs on named planted violations and restored cleanly: **P1** (unconditional preserve, no revision gate) turned the three negative rows RED while leaving the Rev-2-class rows and Group B green; **P2** (a stray OR into `top_address` instead of into `mask`) turned the "preserve, never introduce" leg and the Group B byte-identity assertion RED (a leaked physical byte `0x01`) while leaving everything else green.
- Confirmed the `0x08` write path is **observably unchanged** at this commit: `test_loop08_dip32_drop_bit_is_cleared_deliberately_before_the_first_pulse` (the sibling suite's case) stayed green throughout, and `native_trace_v131`'s three expected-RED strobe-count assertions reproduced the exact `Expected/Was` values recorded at the Phase 141 tip -- empirical proof that L-3's plan ordering (this plan before 142-04's `eprom.cpp` work) leaves no window with no drop route.

## Task Commits

Each task was committed atomically (in the `firestarter` submodule, branch `gsd/v1.31-27c-programming-algorithm-fidelity`):

1. **Task 1: Author the preserve-mask truth table and the 32-pin non-EPROM baseline, and see them RED before the change** - `6971aab` (test)
2. **Task 2: Gate the drop-bit preserve on Rev 2-class revisions, retire the hand-off comment, and arm the green-on-arrival legs** - `35e9fe0` (feat)

**Plan metadata:** committed separately in the meta repo (this SUMMARY + STATE.md + ROADMAP.md).

## Files Created/Modified
- `firestarter/test/native/avr/test_vpp_eprom_v131/test_vpp_eprom_v131.cpp` - nine-row `(pins, revision)` truth table + 32-pin non-EPROM byte-identity baseline (Task 1); unchanged in Task 2 (same literals reproduce GREEN post-change)
- `firestarter/src/proms/memory.cpp` - `mem_util_calculate_top_address_register`'s preserve mask, revision-gated for `pins >= 32`; hand-off comment retired (Task 2)

## Decisions Made
- **D-01/D-02, implemented verbatim as amended:** revision alone gates the widened preserve; no `handle` field, no `handle->protocol` key, no `EPROM_HV_*` composite inside `memory.cpp` (that composite is EPROM-family-scoped; this file serves every protocol).
- **Nine separate Unity cases, not one table-driven function**, for Group A -- gives `pio test`'s per-case report exact row-level RED/GREEN visibility, which a single longjmp-on-first-failure function would hide.
- **Group B's protocol literal is raw hex `0x10`** with a clarifying comment, matching the sibling suite's house convention and avoiding an unnecessary new include.
- **P2's planted violation uses a single-use local `bool` flag**, scoped to the matched switch cases and consumed once after the mask application -- isolates the violation to exactly the Rev-2 32-pin arm rather than corrupting `pins<32` rows too.

## Deviations from Plan

None (Rules 1-4) - the plan executed exactly as written; no bugs, missing functionality, blocking issues, or architectural questions arose. One implementation-detail choice (raw hex vs. symbolic protocol constant, above) was made within the plan's own stated flexibility ("exact name/signature is the planner's" analog for test code) and is recorded under Decisions Made rather than as a deviation.

## Issues Encountered

**`pio test` CLI wrapper mis-reports a RED (>1 failure) run as `[ERRORED]`/`SIGQUIT`, not a Unity/test defect.** After Task 1 (RED state, 3 failures), `pio test -e native_loop_v131 -f "*test_vpp_eprom_v131*"` printed all 11 individual `PASSED`/`FAILED` lines correctly, then reported `Program received signal SIGQUIT (Quit)`, `[ERRORED]`, and a summary line reading `12 test cases: 3 failed, 8 succeeded` (12 vs. the actual 11 -- also a miscount). Running the compiled binary directly (`.pio/build/native_loop_v131/firestarter_native`) showed the authoritative result: `11 Tests 3 Failures 0 Ignored`, exit code 3, clean process exit, no signal. Once Task 2 landed (GREEN, exit code 0), the identical `pio test` invocation reported `[PASSED]` cleanly with no SIGQUIT -- confirming the quirk is an artifact of `pio test`'s wrapper only special-casing Unity's `UNITY_END()` return value at 0 or 1, not a defect in this suite's tests or in the underlying Unity result stream. Documented here per D-15's evidence-capture requirement; the acceptance criteria's "Unity `TEST_ASSERT` failures naming the row, not a SIGABRT, a link error, or a -1-undecodable-value failure" is satisfied and independently confirmed via the direct binary run.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Plan 142-04 (wave 4, `eprom.cpp` resolver work) can now land its own removal of the explicit `handle->pins >= 32` clear (`eprom.cpp:217-219`) safely: this plan's preserve-mask change is confirmed a no-op on the current `0x08` write path (the sibling suite's `test_loop08_dip32_drop_bit_is_cleared_deliberately_before_the_first_pulse` stayed green throughout, and `native_trace_v131`'s expected-RED values are byte-identical to the Phase 141 tip), so 142-04 becomes the change that makes the drop bit actually survive on real Rev 2-class hardware, per L-3's ordering.
- The nine-row truth table and the 32-pin non-EPROM byte-identity case are now permanent fixtures of `test_vpp_eprom_v131.cpp` for plans 142-03/142-05/142-06 to extend alongside (no further env or harness wiring needed).
- No requirement was marked complete (`requirements: []` by design, per this plan's explicit scope boundary) -- `VPP-01`...`VPP-04` remain open for plan 142-07 to flip after all evidence lands across the phase.
- Every pinned gate, the warning watermark, all three AVR links, and the 256-test pytest suite are confirmed unmoved; `native_trace_v131`'s expected-RED state is named as such (D-17), not silenced or re-frozen.

---
*Phase: 142-high-voltage-routing*
*Completed: 2026-08-11*

## Self-Check: PASSED

- FOUND: firestarter/src/proms/memory.cpp
- FOUND: firestarter/test/native/avr/test_vpp_eprom_v131/test_vpp_eprom_v131.cpp
- FOUND commit: 6971aab
- FOUND commit: 35e9fe0
