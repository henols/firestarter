---
phase: 142-high-voltage-routing
plan: 03
subsystem: firmware
tags: [platformio, unity, arduinofake, native-tests, eprom, vpp, over-voltage, planted-red, messages]

# Dependency graph
requires:
  - phase: 142-01
    provides: "test_vpp_eprom_v131 suite skeleton wired into [env:native_loop_v131]; host_stubs.cpp's four-layer recorder/mock composition (HOST_STUBS_REAL_REGISTER_UTILS + HOST_STUBS_RECORD_TIMING + HOST_STUBS_CUSTOM_READ_DATA_BUFFER + HOST_STUBS_CUSTOM_VOLTAGE_MV); make_vpp_handle/drive_vpp_init/drive_vpp_write contract; set_mock_vpp_mv; count_logged_id/find_logged_id/logged_id_param; control_write_count/_value; EPROM_HV_ROUTE_MASK/EPROM_HV_ALL_OFF_MASK composites"
  - phase: 142-02
    provides: "the REVISION_2_2 override idiom and its two independent reasons (Rev-0 early return vacuity, drop-bit/A16 physical collision); the last-clear-plus-paired-non-vacuity assertion idiom; the planted-violation-then-restore-then-hash-verify discipline extended here from two violations to five"
provides:
  - "Four VPP-04 legs in test_vpp_eprom_v131.cpp: (a) over-voltage refusal fires MSG_ERR_VPP_HIGH (0xB8) by id + RESPONSE_CODE_ERROR + 8-byte payload; (b) no HV route left asserted on that refusal path, with a paired non-vacuity control; (c) FLAG_FORCE downgrades the identical reading to MSG_WARN_VPP_HIGH (0x82) + RESPONSE_CODE_WARNING and still clears the route; (d) an in-range reading fires none of the three VPP message ids"
  - "Two VPP-03 pre-rewrite byte-identity baselines (Case E = CMD_ERASE, Case I = CMD_CHECK_CHIP_ID) pinning the CURRENT control-value stream as measured literals -- the 'before' side of research assumption A3, for plan 142-04's composite-mask conversion to reproduce identically"
  - "D-13 premise correction discharged and recorded: VPP-04's own wording presumed a refusal-by-id gate already existed for the EPROM path -- confirmed FALSE by grep (no test anywhere asserts MSG_ERR_VPP_HIGH/MSG_WARN_VPP_HIGH before this plan); this plan AUTHORS that gate rather than pointing at one belonging to another protocol family"
  - "Five named planted-violation transcripts (V1-V5), each independently seen RED for the exact reason it was planted, and eprom.cpp proven byte-restored (git hash-object unchanged) after each revert and after the fifth"
affects: [142-04, 142-05, 142-07]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Five-planted-violation-then-restore cycle against a single production file in one task, each plant independently run, captured (including a direct-binary-invocation confirmation when the pio test CLI wrapper's known >1-failure mis-report fired), and reverted with a git hash-object check before the next plant -- extends the two-violation precedent from 142-02 to five in a single task"
    - "Pre-rewrite control-value baselines for CMD_ERASE/CMD_CHECK_CHIP_ID hand-derived from the register-cache-elision + Rev2-physical-remap semantics (rurp_register_utils.h + rurp_hw_rev_utils.h), then confirmed correct on the FIRST execution against the unchanged tree -- the derivation was verified by running, not asserted in prose, per RESEARCH's explicit instruction on assumption A3"

key-files:
  created: []
  modified:
    - firestarter/test/native/avr/test_vpp_eprom_v131/test_vpp_eprom_v131.cpp

key-decisions:
  - "Single commit for all three tasks, landed only after task 3's five planted-violation-then-revert cycles leave eprom.cpp byte-identical to its pre-task-1 state -- tasks 1 and 2 add only test cases (no production-source diff of their own to commit), and the plan's own task-3 action text is the only place a commit instruction appears"
  - "CMD_ERASE / CMD_CHECK_CHIP_ID drive prologues (configure_memory -> reset_register_cache -> three clear_*() calls -> firestarter_operation_main) written inline per case rather than as a new shared drive_* harness helper -- keeps the 142-01 harness contract (make_vpp_handle/drive_vpp_init/drive_vpp_write) unchanged, since only two cases ever need this exact shape"
  - "V3's planted violation disables the FLAG_FORCE fork via `if (false && is_flag_set(FLAG_FORCE))` rather than deleting the fork's body -- a one-line, obviously-temporary, trivially-revertible planted change with the smallest possible diff"
  - "V1 widens the over-voltage compare's tolerance from +500 to +50000 (rather than removing the compare) -- keeps the change to a single literal, and the boundary-plus-one injected value (13501) makes the widened tolerance unambiguously unreachable"

patterns-established: []

requirements-completed: []

coverage:
  - id: D1
    description: "Four VPP-04 legs authored against the CURRENT, unrewritten eprom_check_vpp: refusal by message id with 8-byte payload shape (a), no-route-left-asserted with paired non-vacuity (b), the FLAG_FORCE downgrade (c), and an in-range control proving the injection seam changes the outcome (d)"
    verification:
      - kind: unit
        ref: "pio test -e native_loop_v131 -f \"*test_vpp_eprom_v131*\" -- 17 test cases: 17 succeeded"
        status: pass
      - kind: other
        ref: "Planted violations V1 (widen the over-voltage compare) and V3 (disable the FLAG_FORCE fork) -- each independently drove legs (a)/(c) RED for the predicted reason, confirmed via direct binary invocation (17 Tests, 2 Failures then 1 Failure, 0 Ignored, clean exit -- no SIGABRT/link/undecodable-value failure), then eprom.cpp restored and git hash-object re-confirmed"
        status: pass
    human_judgment: false
  - id: D2
    description: "Leg (b)'s route-clear property proven non-vacuous specifically against the regression it exists to catch: a refusal that leaves the rail energised"
    verification:
      - kind: other
        ref: "Planted violation V2 (early return after the ERROR assignment, eprom.cpp:371) -- leg (b) went RED (\"non-vacuity: at least the over-voltage assert and the refusal's own disable must both have written CONTROL\") while leg (a) STAYED GREEN, demonstrating a refusal-only gate would have passed this exact regression; eprom.cpp restored and git hash-object re-confirmed afterward"
        status: pass
    human_judgment: false
  - id: D3
    description: "Two VPP-03 pre-rewrite byte-identity baselines (CMD_ERASE Case E, CMD_CHECK_CHIP_ID Case I) pinning the CURRENT control-value stream as measured literals, so plan 142-04's composite-mask conversion at eprom.cpp:174/:327/:393/:409 is a measured no-op rather than a reasoned one"
    verification:
      - kind: unit
        ref: "pio test -e native_loop_v131 -f \"*test_vpp_eprom_v131*\" -- both cases PASSED on the first run against the unchanged tree with hand-derived literals confirmed correct by execution"
        status: pass
      - kind: other
        ref: "Planted violations V4 (widen the erase-path assert mask, eprom.cpp:399) and V5 (narrow the chip-id clear, eprom.cpp:327) -- Case E went RED at index 0 (Expected 0x80 Was 0x81) and Case I went RED at index 3 (Expected 0x10 Was 0x12), each for the exact planted reason; eprom.cpp restored and git hash-object re-confirmed after each"
        status: pass
    human_judgment: false
  - id: D4
    description: "eprom.cpp proven byte-restored after all five planted violations, and every pre-existing gate (native, native_nodevtools, pytest, warning watermark, three AVR links, native_trace_v131's expected-RED) confirmed unmoved"
    verification:
      - kind: other
        ref: "git hash-object src/proms/eprom.cpp == b36d3c4c7c854c1d8b24ab262b1319f7111f11cf (unchanged from before the first plant) and git diff --exit-code -- src/ include/ exits 0, both re-confirmed after the fifth restore"
        status: pass
      - kind: unit
        ref: "pio test -e native (141 test cases: 141 succeeded, 17 suites) and pio test -e native_nodevtools (141 test cases: 141 succeeded, 17 suites) -- both unmoved"
        status: pass
      - kind: other
        ref: "python3 -m pytest tests/ -o addopts=\"\" -q -- 256 passed (run after the commit, per L-1)"
        status: pass
      - kind: other
        ref: "python3 scripts/check_build_warnings.py --rebuild -- PASS: uno/uno328pb/leonardo macro_redefinition=0, all three link; native/native_nodevtools warnings 998/1166 (unmoved, 168 below watermark)"
        status: pass
      - kind: other
        ref: "pio test -e native_trace_v131 -- expected RED (D-17), reproduced byte-identical to the Phase 141 tip: Expected 198 Was 91 (0x07), Expected 221 Was 119 (0x08), Expected 201 Was 59 (0x0B) -- confirms this plan's revert left the strobe stream genuinely unmoved"
        status: pass
    human_judgment: false

duration: 27min
completed: 2026-08-11
status: complete
---

# Phase 142 Plan 03: VPP-04 Over-Voltage Refusal Gate + VPP-03 Pre-Rewrite Baselines Summary

**Authors the VPP-04 over-voltage refusal gate (by message id, route-clear with paired non-vacuity, FLAG_FORCE downgrade, in-range control) as a regression oracle against the CURRENT, unrewritten `eprom_check_vpp`, and pins the pre-rewrite `CMD_ERASE`/`CMD_CHECK_CHIP_ID` control-value streams as measured literals for VPP-03 -- five named planted violations, each independently seen RED for its own reason and byte-exact restored.**

## Performance

- **Duration:** 27 min
- **Started:** 2026-08-11T22:24:24Z
- **Completed:** 2026-08-11T22:51:20Z
- **Tasks:** 3
- **Files modified:** 1

## Accomplishments
- Discharged D-13's premise correction: grepped `test/` and `tests/` and confirmed `MSG_ERR_VPP_HIGH`/`MSG_WARN_VPP_HIGH` appear in **no** test anywhere before this plan -- `test_val_eprom` pins `vpp_mv = 0` against a 0-returning stub precisely so the compare never fires, and `test_flash_intel_vpp` (protocol `0x10`) runs in no PlatformIO environment and SIGABRTs after case 1. This plan **authors** the gate rather than pointing at one belonging to another protocol family.
- Added four VPP-04 legs to `test_vpp_eprom_v131.cpp`, each setting `hardware_revision = REVISION_2_2` first (mandatory: the Rev-0 early return and the drop-bit/A16 physical collision would otherwise make the case vacuous), driven via `make_vpp_handle(0x07, 28, 65536, 100, 13000, <flags>, VPP_BUS_CONFIG_0x07)` + `set_mock_vpp_mv` + `drive_vpp_init`:
  - (a) an injected 13501 mV reading (one mV past the 13000+500 boundary) refuses with `MSG_ERR_VPP_HIGH` (0xB8) by id, `RESPONSE_CODE_ERROR`, and an 8-byte payload -- the first test in this tree to assert this id.
  - (b) that refusal path leaves no HV route asserted: the last control value has both `CTRL_VPP_REGULATOR_ENABLE` and the drop bit clear, paired with a `saw_earlier_set` non-vacuity control (borrowing `test_flash_intel_vpp.cpp:159-171`'s SAF-04 *intent*, not its interception mechanism, per RESEARCH C-5).
  - (c) `FLAG_FORCE` downgrades the identical reading to `MSG_WARN_VPP_HIGH` (0x82) + `RESPONSE_CODE_WARNING` and still clears the route.
  - (d) an in-range reading (`== setpoint`) fires none of `MSG_ERR_VPP_HIGH`/`MSG_WARN_VPP_HIGH`/`MSG_WARN_VPP_LOW` -- the control proving the injection seam actually changes the outcome.
- Added two VPP-03 baselines pinning the **current** `CMD_ERASE` and `CMD_CHECK_CHIP_ID` control-value streams as enumerated literal sequences (`n=4` each), derived from the register-cache-elision (`rurp_register_utils.h:39-41`) and Rev2-physical-remap (`rurp_hw_rev_utils.h:15-27`) semantics and confirmed correct by direct execution against the unchanged tree on the first attempt -- research assumption A3's "before" measurement, not a prose argument.
- Ran five named planted violations against `src/proms/eprom.cpp`, one at a time, each independently confirmed RED for its predicted reason and then byte-exact restored (`git hash-object` re-checked after every restore):
  - **V1** (widen the over-voltage compare `:351` from `+500` to `+50000`) -- legs (a) and (c) RED, (b)/(d) stayed green.
  - **V2** (early `return` after the ERROR assignment `:371`) -- leg (b) RED **while leg (a) stayed green**, the direct demonstration that a refusal-only gate would have passed the exact regression VPP-02 exists to prevent.
  - **V3** (disable the `FLAG_FORCE` fork via `if (false && is_flag_set(FLAG_FORCE))`) -- leg (c) RED, (a)/(b)/(d) stayed green.
  - **V4** (widen the erase-path assert mask `:399` to also assert the drop bit) -- Case E's `CMD_ERASE` baseline RED at index 0 (`Expected 0x80 Was 0x81`).
  - **V5** (narrow the chip-id clear `:327` to drop `CTRL_VPP_A9_ENABLE`) -- Case I's `CMD_CHECK_CHIP_ID` baseline RED at index 3 (`Expected 0x10 Was 0x12`).
- Confirmed the full sweep unmoved after committing: `native`/`native_nodevtools` still 141/17, the pytest gate still 256 passed, the warning watermark still 998/1166, all three AVR targets link with `macro_redefinition=0`, and `native_trace_v131` remains RED with byte-identical `Expected`/`Was` values to the Phase 141 tip (D-17, not silenced or re-frozen).

## Task Commits

This plan's three tasks land in a **single** commit, per task 3's own action text (the only place a commit instruction appears) and the D-15 discipline that `eprom.cpp` must be byte-restored before any commit: tasks 1 and 2 add only test cases with no production-source diff of their own, and task 3's five planted-violation-then-revert cycles leave `eprom.cpp` byte-identical to its pre-task-1 state, so the natural commit boundary is after task 3, not after each task individually.

1. **Task 1 (VPP-04 legs a-d) + Task 2 (VPP-03 Case E/I baselines) + Task 3 (five planted violations, proven RED and reverted)** - `4a890b9` (test, in the `firestarter` submodule, branch `gsd/v1.31-27c-programming-algorithm-fidelity`)

**Plan metadata:** committed separately in the meta repo (this SUMMARY + STATE.md + ROADMAP.md).

## Files Created/Modified
- `firestarter/test/native/avr/test_vpp_eprom_v131/test_vpp_eprom_v131.cpp` - added 4 VPP-04 legs, 2 VPP-03 baselines, and their `main()` registration (17 cases total in this suite now; `src/proms/eprom.cpp` and `include/` are byte-identical to before this plan -- `git diff --exit-code -- src/ include/` passes)

## Decisions Made
- **Single commit for all three tasks** (see Task Commits above) -- tasks 1/2 have nothing of their own to commit before task 3's planted-violation proof completes and `eprom.cpp` is confirmed byte-restored.
- **Inline drive prologues for Case E/Case I** rather than a new shared `drive_*` helper -- only two cases ever need the "configure_memory → reset_register_cache → clear_*() → `firestarter_operation_main` directly" shape (skipping `_init` deliberately, so `eprom_check_vpp` is never invoked and the measured stream is undisturbed by a VPP compare). Keeps the 142-01 harness contract (`make_vpp_handle`/`drive_vpp_init`/`drive_vpp_write`) exactly as later plans expect it.
- **V3's mechanism** (`if (false && is_flag_set(FLAG_FORCE))`) chosen over deleting the fork's body -- a one-line, obviously-temporary, trivially-revertible change.
- **V1's mechanism** (widen `+500` to `+50000`) chosen over removing the compare outright -- keeps the plant to one literal, and the boundary-plus-one injected value (13501) makes the widened tolerance unambiguously unreachable without needing a second injected-value change.

## Deviations from Plan

None (Rules 1-4) -- the plan executed exactly as written. Every literal value for the VPP-03 baselines (Case E: `[0x80, 0x90, 0x96, 0x10]`; Case I: `[0x80, 0x82, 0x92, 0x10]`) was hand-derived from the register-cache-elision and Rev2-remap source before writing the assertions, then confirmed correct by running against the unchanged tree on the first attempt -- no placeholder-then-correct round trip was needed, but the values are still a **measurement** (the test run is the proof), not a prose assertion, satisfying RESEARCH's explicit instruction on assumption A3.

## Issues Encountered

**`pio test`'s CLI wrapper mis-reported every planted-violation run with >1 Unity failure as `[ERRORED]`/`SIGINT`, not a test defect.** This is the same documented artifact from 142-02's SUMMARY (there recorded as `SIGQUIT`), just a different signal name this session. V1 (2 failures) and every other planted run (1 failure each, still routed through the wrapper's non-0/1 exit-code special case) triggered it. Each time, `.pio/build/native_loop_v131/firestarter_native` was invoked directly, which reported the authoritative, unambiguous result (`17 Tests N Failures 0 Ignored`, exit code 0, clean process exit, no signal) with the exact failing assertion text. Not a defect in this suite or in the underlying Unity result stream.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- VPP-04's full evidence (legs a-d, all seen RED on a named planted violation) is now authored and ready for plan 142-07 to cite when it flips the `VPP-*` requirement checkboxes -- this plan marks none (`requirements: []` by design).
- VPP-03's byte-identity baselines (Case E, Case I) are ready for plan 142-04: after that plan converts the hand-rolled disables at `eprom.cpp:174`/`:327`/`:393`/`:409` into `EPROM_HV_ALL_OFF_MASK`, these same two cases must reproduce the identical `[0x80, 0x90, 0x96, 0x10]` / `[0x80, 0x82, 0x92, 0x10]` sequences -- a measured no-op, not a reasoned one.
- No requirement was marked complete (`requirements: []` by design, per this plan's explicit scope boundary) -- `VPP-01`...`VPP-04` remain open for plan 142-07.
- Every pre-existing gate is confirmed unmoved: `native`/`native_nodevtools` at 141/17 each, the 256-test pytest suite, the warning watermark (998/1166), all three AVR targets linking with zero macro-redefinition warnings, and `native_trace_v131`'s expected-RED state byte-identical to the Phase 141 tip.
- `test_vpp_eprom_v131` now carries 17 cases total (56 alongside the sibling suite in `native_loop_v131`); plans 142-05 and 142-06 extend the same file per the fixed contract, no further env or harness wiring needed.

---
*Phase: 142-high-voltage-routing*
*Completed: 2026-08-11*

## Self-Check: PASSED

- FOUND: firestarter/test/native/avr/test_vpp_eprom_v131/test_vpp_eprom_v131.cpp
- FOUND commit: 4a890b9 (firestarter submodule)
- FOUND commit: b5413315 (meta repo, this SUMMARY)
