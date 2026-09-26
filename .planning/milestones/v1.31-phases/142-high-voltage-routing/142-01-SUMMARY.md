---
phase: 142-high-voltage-routing
plan: 01
subsystem: firmware
tags: [platformio, unity, arduinofake, native-tests, eprom, vpp, rurp_pinout]

# Dependency graph
requires:
  - phase: 141-per-byte-program-loop
    provides: "native_loop_v131 env (Phase 141 D-10), the per-byte pulse-to-verify loop, the HOST_STUBS_REAL_REGISTER_UTILS + HOST_STUBS_RECORD_TIMING recorder composition, the sibling test_loop_eprom_v131 harness this plan's harness is modelled on"
  - phase: 140-parameter-table
    provides: "eprom_params_t table with the vpp_path column, already hoisted and (void)-cast in eprom_write_execute awaiting a consumer"
provides:
  - "EPROM_HV_ROUTE_MASK and EPROM_HV_ALL_OFF_MASK composite masks in rurp_pinout.h -- the shared mask set every later HV-routing plan in this phase consumes"
  - "test_vpp_eprom_v131 suite wired into the existing [env:native_loop_v131] (no seventh env)"
  - "host_stubs.cpp: voltage-injection seam (set_mock_vpp_mv), and a read-back model extended with a converge-then-mismatch window (vpp_readback_seed's 4th parameter)"
  - "test_vpp_eprom_v131.cpp harness: make_vpp_handle (vpp_mv-safe), drive_vpp_init/drive_vpp_write, VPP_BUS_CONFIG_0x07/_0x08/_0x0B, strobe/logged-id accessors, the REVISION_2_2 override idiom -- all authored as a fixed contract for plans 142-03/142-05/142-06 to extend"
affects: [142-03, 142-04, 142-05, 142-06, 142-07]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "First bitwise-OR composite #define precedent in rurp_pinout.h (zero existed before this plan)"
    - "Read-back model with a bounded mismatch window (converge_after/mismatch_from) so a stub can express a byte that converges mid-loop and then mismatches on a later full-array verify pass"

key-files:
  created:
    - firestarter/test/native/avr/test_vpp_eprom_v131/host_stubs.cpp
    - firestarter/test/native/avr/test_vpp_eprom_v131/test_vpp_eprom_v131.cpp
  modified:
    - firestarter/include/rurp_pinout.h
    - firestarter/platformio.ini

key-decisions:
  - "D-07 resolved default taken: EPROM_HV_* composites live in rurp_pinout.h beside the CTRL_* bits they are built from, not in eprom.h/eprom_params.h"
  - "CTRL_VPP_P1_ENABLE deliberately excluded from EPROM_HV_ALL_OFF_MASK -- the VPE-to-P1 remap in eprom_internal_set_control_register plus the Rev2 CTRL_ADDRESS_LINE_18/CTRL_VPP_P1_ENABLE bit collision (correction C-4)"
  - "D-14: the VPP-04 gate reuses the existing native_loop_v131 env (test_filter + -I, both required) rather than a seventh env; neither pinned env (native/native_nodevtools) references it"
  - "make_vpp_handle requires a vpp_setpoint_mv parameter and assigns h.vpp_mv -- avoids D-13's named vacuity trap (test_val_eprom.cpp:74's 0 vs 0 comparison)"
  - "Read-back model symbols renamed loop_* -> vpp_* (deliberate, not cosmetic) because the mismatch-window semantics diverge from the sibling suite's unbounded model"

patterns-established:
  - "Composite #define block comment records: EPROM_-prefix rationale against the zero-headroom warning watermark, logical-vs-physical framing, all four per-variant values, the legacy alias caveat, the cannot-be-a-#define preserve-mask exception, the 0-B-until-referenced rule, and the no-prior-precedent note"
  - "drive_vpp_init/drive_vpp_write share one prologue (configure_memory -> reset_register_cache -> clear_*) and diverge only in the terminal call (_init vs _main), so later plans extend one contract instead of two"

requirements-completed: []

coverage:
  - id: D1
    description: "EPROM_HV_ROUTE_MASK (0x81 legacy / 0x180 wide) and EPROM_HV_ALL_OFF_MASK (0x87 legacy / 0x186 wide) added to rurp_pinout.h, correctly placed between the wide arm's #endif and CTRL_ADDRESS_LINE_13, P1-free"
    verification:
      - kind: unit
        ref: "pio test -e native && pio test -e native_nodevtools -- both report 141 test cases: 141 succeeded, 17 suites (unmoved)"
        status: pass
      - kind: other
        ref: "Task 1 <verify> inline python script -- asserts single definition, correct membership, placement bounds, and CTRL_VPP_P1_ENABLE absence"
        status: pass
      - kind: other
        ref: "python3 scripts/check_build_warnings.py --rebuild -- native/native_nodevtools warnings 998/1166 (unmoved), uno/uno328pb/leonardo macro_redefinition=0"
        status: pass
    human_judgment: false
  - id: D2
    description: "test_vpp_eprom_v131 suite directory wired into [env:native_loop_v131] via both required lines (test_filter + -I); host_stubs.cpp composes four opt-in recorder/mock layers plus the voltage-injection seam"
    verification:
      - kind: unit
        ref: "pio test -e native_loop_v131 -f \"*test_vpp_eprom_v131*\" -- 1 test case: 1 succeeded, suite PASSED"
        status: pass
      - kind: other
        ref: "Task 2 <verify> inline python script -- asserts both platformio.ini lines, neither pinned env references the suite, all four guards precede the .inc, vpp_readback_* rename complete"
        status: pass
    human_judgment: false
  - id: D3
    description: "Suite harness (make_vpp_handle, drive_vpp_init/_write, bus configs, strobe/logged-id accessors, REVISION_2_2 idiom) plus one self-check case proving clean recorders, P1-free composites, and the mismatch-window sequence 0xFF / target / ~target"
    verification:
      - kind: unit
        ref: "pio test -e native_loop_v131 -- 2 suites, 40 test cases: 40 succeeded (39 sibling-suite cases + 1 new)"
        status: pass
      - kind: other
        ref: "Planted-mutation run: deleted the mismatch_from branch in host_stubs.cpp, re-ran the suite (FAILED: Expected 0xAA Was 0x55 at the read-3 assertion), reverted, re-ran GREEN"
        status: pass
    human_judgment: false

duration: 32min
completed: 2026-08-11
status: complete
---

# Phase 142 Plan 01: High-Voltage Routing Prerequisites Summary

**Shared EPROM_HV_* composite masks in rurp_pinout.h plus a new test_vpp_eprom_v131 Unity suite (wired into the existing native_loop_v131 env) whose harness and one self-check case prove the recorders, the composites, and a converge-then-mismatch read-back window all work before any behavioural VPP-routing leg lands.**

## Performance

- **Duration:** 32 min
- **Started:** 2026-08-11T21:12:52Z
- **Completed:** 2026-08-11T21:44:00Z
- **Tasks:** 3
- **Files modified:** 4 (2 created, 2 modified)

## Accomplishments
- Added `EPROM_HV_ROUTE_MASK` and `EPROM_HV_ALL_OFF_MASK` to `rurp_pinout.h`, positioned beside the `CTRL_*` bits they are built from, with a block comment carrying all seven required recorded points plus the two independent reasons `CTRL_VPP_P1_ENABLE` is excluded. This is the first bitwise-OR composite `#define` in the header's history.
- Wired a new `test_vpp_eprom_v131` suite into the existing `[env:native_loop_v131]` (both the `test_filter` and `-I` lines, per Phase 119 D-04) without creating a seventh env, editing the pinned baseline, or touching `[env:native]` / `[env:native_nodevtools]`.
- Authored `host_stubs.cpp` composing four opt-in recorder/mock layers (real register utils, timing, custom read-data-buffer, custom voltage) and extended the sibling suite's read-back model with a bounded mismatch window (`vpp_readback_seed`'s `mismatch_from` parameter) -- the exact shape VPP-02's later `MSG_ERR_VERIFY` leg needs and the sibling's unbounded model cannot express.
- Authored the suite harness (`make_vpp_handle`, `drive_vpp_init`/`drive_vpp_write`, three bus configs, strobe/logged-id accessors, the `REVISION_2_2` override idiom) and one self-check case proving three independently-failable things: the recorders start clean, the two composites are exactly correct and P1-free, and the mismatch-window model returns `0xFF` / `target` / `~target` across three reads.
- Confirmed the mismatch-window assertion is load-bearing via a planted mutation (removed the `mismatch_from` branch, watched the case go RED with the exact expected failure, reverted).

## Task Commits

Each task was committed atomically (in the `firestarter` submodule, branch `gsd/v1.31-27c-programming-algorithm-fidelity`):

1. **Task 1: Add the two EPROM_HV_* composites to rurp_pinout.h (D-07)** - `3613438` (feat)
2. **Task 2: Wire the new suite into [env:native_loop_v131] and author its stub layer (D-14)** - `9156791` (feat)
3. **Task 3: Author the suite harness and a self-check case that proves the composites and the recorders** - `6a4336b` (test)

**Plan metadata:** committed separately in the meta repo (this SUMMARY + STATE.md + ROADMAP.md).

## Files Created/Modified
- `firestarter/include/rurp_pinout.h` - added `EPROM_HV_ROUTE_MASK` / `EPROM_HV_ALL_OFF_MASK` composites + block comment
- `firestarter/platformio.ini` - added `test_vpp_eprom_v131` to `[env:native_loop_v131]`'s `test_filter` and `-I` list, plus a header-comment paragraph
- `firestarter/test/native/avr/test_vpp_eprom_v131/host_stubs.cpp` - four-layer stub composition, voltage mock, extended read-back model, logged-id capture
- `firestarter/test/native/avr/test_vpp_eprom_v131/test_vpp_eprom_v131.cpp` - suite harness + one self-check case

## Decisions Made
- **D-07 (resolved):** composites live in `rurp_pinout.h`, not `eprom.h`/`eprom_params.h` -- both `eprom.cpp` and `memory.cpp` already include it, and a composite beside its own bits cannot drift from them.
- **D-14 (resolved):** the VPP-04 gate reuses `native_loop_v131` rather than a new env, following the `native_trace_v131`/`native_params_v131` precedent for gate-invisible native suites.
- **Vacuity-trap avoidance (D-13):** `make_vpp_handle` takes `vpp_setpoint_mv` as a required parameter (not optional, not defaulted) so no later case can accidentally repeat the `test_val_eprom.cpp:74` failure mode of comparing `0` against `0`.
- **Naming:** read-back model symbols renamed `loop_*` -> `vpp_*` deliberately, since the extended model's semantics (bounded mismatch window) diverge from the sibling suite's unbounded one.

## Deviations from Plan

None - plan executed exactly as written. All three tasks' automated verification scripts passed on the first implementation attempt; no Rule 1-4 auto-fixes were needed.

## Issues Encountered

None. One expected, plan-documented non-event worth recording: after Task 2 (before Task 3 authored `main()`), `pio test -e native_loop_v131 -f "*test_vpp_eprom_v131*"` reported `ERRORED` with "undefined reference to `main`" -- this is exactly what the plan's own Task 2 acceptance criteria predicts ("it will report no cases until task 3 lands `main()`"), not a defect.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- The shared mask set (`EPROM_HV_ROUTE_MASK` / `EPROM_HV_ALL_OFF_MASK`) is available for plan 142-04's `eprom.cpp` resolver and disable-guarantee work, and for plan 142-02's `memory.cpp` preserve-mask change.
- The `test_vpp_eprom_v131` suite and its harness (`make_vpp_handle`, `drive_vpp_init`/`drive_vpp_write`, accessors, revision-override idiom) are ready for plans 142-03, 142-05 and 142-06 to extend with behavioural VPP-01/VPP-02/VPP-04 cases -- no further env wiring is needed, only new `RUN_TEST` cases in the existing file.
- No requirement was marked complete (frontmatter `requirements: []`, by design) -- VPP-01...VPP-04 remain open for plan 142-07 to flip after all behavioural evidence lands.
- Both pinned native envs (141 cases / 17 suites each), the native warning watermark (998/1166), `size_baseline.json` (byte-unchanged), and the 256-test pytest suite are all confirmed unmoved -- this plan is a pure additive prerequisite with zero blast radius on existing gates.

---
*Phase: 142-high-voltage-routing*
*Completed: 2026-08-11*

## Self-Check: PASSED

- FOUND: firestarter/include/rurp_pinout.h
- FOUND: firestarter/platformio.ini
- FOUND: firestarter/test/native/avr/test_vpp_eprom_v131/host_stubs.cpp
- FOUND: firestarter/test/native/avr/test_vpp_eprom_v131/test_vpp_eprom_v131.cpp
- FOUND commit: 3613438
- FOUND commit: 9156791
- FOUND commit: 6a4336b
