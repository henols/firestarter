---
phase: 142-high-voltage-routing
plan: 05
subsystem: firmware
tags: [platformio, unity, arduinofake, native-tests, eprom, vpp, hv-routing, planted-red, control-register-cache]

# Dependency graph
requires:
  - phase: 142-01
    provides: "test_vpp_eprom_v131 harness (make_vpp_handle, drive_vpp_init/_write, set_mock_vpp_mv, control_write_count/_value/_strobe_index, first_genuine_pulse_strobe_index, VPP_BUS_CONFIG_0x07/_0x08/_0x0B, the vpp_readback_seed mismatch-window model, REVISION_2_2 override idiom) -- the fixed contract this plan extends with zero harness changes"
  - phase: 142-02
    provides: "the REVISION_2_x-gated drop-bit preserve in mem_util_calculate_top_address_register -- the mechanism the REVISION_1 negative case in this plan proves does NOT apply outside Rev 2-class"
  - phase: 142-03
    provides: "the VPP-04 refusal-gate cases (a-d) and the pre-rewrite CMD_ERASE/CMD_CHECK_CHIP_ID control-value baselines already landed in this same suite file, unmoved by this plan"
  - phase: 142-04
    provides: "eprom_hv_route_mask (exposed in include/eprom.h) -- the resolver every case in this plan drives or calls directly; the two conditional single-exit wrappers (eprom_write_init, eprom_write_execute) whose disable guarantee this plan's Task 3 proves and stress-tests via two planted violations; the D-04 removal of the explicit pins>=32 clear that makes the REVISION_1 negative case meaningful as a negative"
provides:
  - "The resolver's full (protocol, ctrl_flags) -> mask truth table (Group T, 8 cases incl. the mandatory non-vacuity leg), asserted by direct calls to eprom_hv_route_mask on a bare handle -- no drive, no revision override -- including the fail-closed NULL-row arm that is UNREACHABLE through any drive"
  - "Three route-strobe proofs (Group R) that the resolved mask reaches the wire: 0x0B's direct path with no drop bit; --vpe-as-vpp forcing the direct path onto 0x07; and the D-02 negative -- a 32-pin part on REVISION_1 still strips the drop bit after the first set_address"
  - "The VPP-03 headline proof: eprom_check_vpp's measured route and eprom_write_execute's applied route at the first genuine program pulse are the SAME physical byte on the 0x08/32-pin row, with a planted violation reproducing the exact pre-142-04 divergence"
  - "Three VPP-02 write-path exit cases (the MSG_ERR_VERIFY final-pass failure -- the exit that disabled NOTHING before this phase; the 0x0B-only MSG_ERR_ENERGY_CAP exit; eprom_write_init's defensive error exit) plus the row==NULL exit named covered-by-construction rather than faked, plus two planted violations (W1, W2) proving the write-path wrapper is both load-bearing and correctly conditional"
affects: [142-06, 142-07]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Read the unbounded control-register CACHE (firestarter_get_control_register) instead of a bounded strobe recorder's tail, whenever a case's own pulse count can overflow the 512-entry strobe cap (T-141-CAP, test_loop_eprom_v131.cpp's own named finding) -- the cache always reflects the true final logical state; a truncated strobe tail can silently misname a mid-stream entry as 'the last write'"
    - "Place an equality assertion's non-vacuity guard on the leg that is UNAFFECTED by the planted violation under test, not on the leg being probed -- so the plant's failure lands exactly on the equality line rather than on a redundant guard that would fire first and obscure which property actually broke"

key-files:
  created: []
  modified:
    - firestarter/test/native/avr/test_vpp_eprom_v131/test_vpp_eprom_v131.cpp

key-decisions:
  - "Task 3's X3 (energy-cap exit) case does not assert strobe_overflowed()==0 and does not read control_write_value(n-1) -- a 100-pulse 0x0B drive legitimately overflows the 512-entry strobe recorder (T-141-CAP), so the LAST recorded strobe would not be the genuine final write. It instead reads h.firestarter_get_control_register(&h, CTRL_VPP_REGULATOR_ENABLE/CTRL_VPP_VPE_DROP_ENABLE) directly -- the same unbounded cache production's own top-of-block gate reads -- for the final-state assertion, and control_write_value(0) (always intact, long before overflow) for the non-vacuity partner."
  - "Case E1 (write_init's error exit) is deliberately mechanically identical to plan 142-03's VPP-04(b) (both drive an over-voltage refusal through drive_vpp_init) -- restated here under VPP-02's own requirement (D-12: which functions carry the disable guarantee) rather than invented as a distinct drive, per 142-RESEARCH.md's own instruction that 'a single case asserting the last control value is route-clear after a write_init that errors is cheap non-regression.' Framed explicitly as defensive cover (C-3), not a fix."
  - "Task 2's non-vacuity guard (leg A's masked value must carry both route bits) is asserted on leg A alone, never on leg B or on the two legs jointly, before the final equality assertion runs -- leg A (measured via eprom_check_vpp) is untouched by the Task 2 planted violation (which only edits the write-path body), so this ordering guarantees the plant's failure lands on the EQUALITY line specifically, matching the plan's stated expected transcript exactly rather than failing one line earlier on a coincidentally-also-broken guard."
  - "No new harness helper needed for Group R's 0x0B case beyond a local vpp_k0b(addr) = addr+0x2000 adapter (mirroring test_loop_eprom_v131.cpp's k0b()) -- VPP_BUS_CONFIG_0x0B's nonzero static_high_mask (bit 13) means this is the FIRST 0x0B write this suite drives, and the adapter is now available for any later plan in this suite that needs one."

patterns-established: []

requirements-completed: []

coverage:
  - id: D1
    description: "The resolver's full (protocol, ctrl_flags) -> mask truth table: 7 named rows (0x07/0x08 no-flag -> EPROM_HV_ROUTE_MASK; 0x0B no-flag -> CTRL_VPP_REGULATOR_ENABLE exactly; 0x07/0x08/0x0B with FLAG_VPE_AS_VPP -> CTRL_VPP_REGULATOR_ENABLE; and the fail-closed NULL-row arm for protocol 0x99, unreachable through any drive) plus the mandatory 0x0B-differs-from-0x07 non-vacuity leg -- 8 cases total, each calling eprom_hv_route_mask directly on a bare handle with no configure_memory and no revision override"
    verification:
      - kind: unit
        ref: "pio test -e native_loop_v131 -f \"*test_vpp_eprom_v131*\" -- all 8 test_vpp01_resolver_* cases PASSED"
        status: pass
      - kind: other
        ref: "Manual review: each case's message names its row; the fail-closed row's comment states configure_eprom (:86-90) already refuses an unknown protocol first, so this arm is reachable only via the direct call this plan's Group T authors"
        status: pass
    human_judgment: false
  - id: D2
    description: "Three route-strobe proofs that the resolved mask reaches the wire: 0x0B takes the direct path with no drop bit in any control value (500us -- the only pulse width configure_eprom's Refusal 2 permits on this energy-capped row); --vpe-as-vpp forces the direct path onto a 0x07 handle, paired against test_loop08_the_28_pin_row_keeps_its_drop_bit (the identical row, without the flag, keeping the drop bit) so the pair isolates the flag as the cause; and the D-02 negative -- a 32-pin part on REVISION_1 has its drop bit SET only at the top-of-block assert and CLEAR at every later control value, the load-bearing case since Rev 1 carries no eprom_check_vpp refusal of its own"
    verification:
      - kind: unit
        ref: "pio test -e native_loop_v131 -f \"*test_vpp_eprom_v131*\" -- test_vpp01_route_0x0b_takes_the_direct_path, test_vpp01_route_vpeasvpp_forces_the_direct_path_onto_0x07, test_vpp01_route_0x08_on_rev1_still_strips_the_drop_bit all PASSED"
        status: pass
      - kind: other
        ref: "Manual bit-trace against mem_util_calculate_top_address_register (memory.cpp:163-303) and rurp_map_ctrl_reg_for_hardware_revision (rurp_hw_rev_utils.h:15-41) confirming the REVISION_1 case's expected physical bytes (0x81 at index 0, 0x80 thereafter) before the case was run -- confirmed correct on first execution"
        status: pass
    human_judgment: false
  - id: D3
    description: "eprom_check_vpp's measured route (leg A, control_write_value(0) under drive_vpp_init) and eprom_write_execute's applied route at the first genuine program pulse (leg B, located via first_genuine_pulse_strobe_index + the largest control-write index preceding it) are the SAME physical byte, masked to CTRL_VPP_REGULATOR_ENABLE|CTRL_VPP_VPE_DROP_ENABLE_REV2, on the 0x08/32-pin row where the divergence lived -- three non-vacuity guards (leg A decodable, leg B's pulse and index both located, the shared masked value non-zero and carrying both bits) precede the equality assertion"
    verification:
      - kind: unit
        ref: "pio test -e native_loop_v131 -f \"*test_vpp_eprom_v131*\" -- test_vpp03_check_vpp_measures_the_route_the_write_path_applies_at_the_first_pulse PASSED"
        status: pass
      - kind: other
        ref: "Planted violation (re-introduced the deleted `if (handle->pins >= 32) { handle->firestarter_set_control_register(handle, CTRL_VPP_VPE_DROP_ENABLE, 0); }` immediately after the route assert in eprom_internal_write_execute_body) -- case went RED exactly on the equality assertion: 'Expected 129 Was 128' (0x81 regulator+drop vs 0x80 regulator-only), reproducing the exact pre-142-04 divergence. Confirmed via direct binary invocation (32 Tests 1 Failures 0 Ignored, clean exit, no signal -- the pio CLI wrapper's SIGHUP is the known non-defect artifact). Restored; git diff --exit-code -- src/ include/ confirmed 0; re-ran green (32/32)."
        status: pass
    human_judgment: false
  - id: D4
    description: "Three VPP-02 write-path exit cases -- X4 (MSG_ERR_VERIFY final-pass failure, the headline: this exit disabled NOTHING before this phase), X3 (MSG_ERR_ENERGY_CAP, 0x0B-only by data), E1 (eprom_write_init's error exit, defensive cover per C-3) -- each pins its own message id while asserting the other write-body ids absent, and each proves the route disabled via the B-9 last-clear-plus-paired-non-vacuity idiom (X3 via the unbounded register cache, per T-141-CAP). The row==NULL exit is recorded as covered-by-construction in main()'s registration comment, not faked as a case."
    verification:
      - kind: unit
        ref: "pio test -e native_loop_v131 -f \"*test_vpp_eprom_v131*\" -- test_vpp02_x4_the_final_pass_verify_failure_disables_the_route, test_vpp02_x3_the_energy_cap_exit_disables_the_route, test_vpp02_e1_write_init_error_exit_leaves_no_route_asserted all PASSED"
        status: pass
      - kind: other
        ref: "X3's first draft asserted strobe_overflowed()==0 and read control_write_value(n-1) -- FAILED (Expected 0 Was 1) on first run, because a 100-pulse 0x0B drive legitimately overflows the 512-entry strobe recorder (T-141-CAP). Rewritten to read the unbounded control-register cache instead; re-ran green. Documented under Issues Encountered, not as a Rule 1-4 deviation (never committed in the broken form)."
        status: pass
    human_judgment: false
  - id: D5
    description: "Two planted violations against eprom_write_execute's wrapper, each independently run and reverted: W1 (removed the wrapper's ERROR-gated clear) drives X4 RED on its last-value-clear assertion while X3, E1, and the sibling suite's X2 (test_loop05_the_loops_own_strobes_disable_the_high_voltage_route) all stay GREEN, because eprom_internal_report_budget_failure carries its own independent disable; W2 (made the wrapper unconditional) drives 6 of test_loop_eprom_v131's cases RED, not merely the single named tiebreaker -- the executable form of C-1's tiebreaker, proving the wrapper is both load-bearing (W1) and correctly conditional (W2)"
    verification:
      - kind: other
        ref: "W1: `pio test -e native_loop_v131` (both suites) -- test_vpp02_x4_the_final_pass_verify_failure_disables_the_route FAILED ('...CTRL_VPP_REGULATOR_ENABLE CLEAR -- this exit disabled NOTHING before this phase...'); test_vpp02_x3_the_energy_cap_exit_disables_the_route, test_vpp02_e1_write_init_error_exit_leaves_no_route_asserted, and test_loop05_the_loops_own_strobes_disable_the_high_voltage_route all PASSED. Confirmed via direct binary invocation: 32 Tests 1 Failures 0 Ignored (this suite), 39 Tests 0 Failures (sibling suite). Restored; git diff --exit-code -- src/ include/ confirmed 0."
        status: pass
      - kind: other
        ref: "W2: bare `pio test -e native_loop_v131` (both suites in scope, per the plan) -- 6 test_loop_eprom_v131 cases FAILED: test_loop06_a_block_of_only_skipped_bytes_emits_no_pulse_at_all, test_loop05_a_successful_block_does_not_disable_the_route, test_loop08_the_route_bit_is_present_in_every_control_value_across_the_block, test_loop08_dip32_block_crossing_an_a16_boundary_keeps_the_route_and_toggles_a16, test_vpp01_dip32_drop_bit_survives_the_block_on_rev2_class, test_loop08_the_28_pin_row_keeps_its_drop_bit; all 32 test_vpp_eprom_v131 cases stayed PASSED. Confirmed via direct binary invocation: 39 Tests 6 Failures 0 Ignored, clean exit. Restored; git diff --exit-code -- src/ include/ confirmed 0; re-ran green (71/71 across both suites)."
        status: pass
    human_judgment: false

duration: ~42min
completed: 2026-08-12
status: complete
---

# Phase 142 Plan 05: High-Voltage Routing -- Behavioural Evidence Summary

**15 new native cases proving what Phase 142 actually changed (the resolver truth table incl. its fail-closed NULL-row arm, three route-strobe proofs incl. the Rev 1 negative, and the eprom_check_vpp/write-path route equality on the 0x08 row) and what it did not (every write-path error exit still disables), with three named planted violations -- one reproducing the exact pre-142-04 measure/apply divergence, two proving the write-path wrapper is both load-bearing and correctly conditional -- all landed in one commit, src/ and include/ byte-identical throughout.**

## Performance

- **Duration:** ~42 min
- **Started:** 2026-08-11T23:35:53Z (immediately following plan 142-04's completion)
- **Completed:** 2026-08-12T00:16:48Z
- **Tasks:** 3
- **Files modified:** 1

## Accomplishments

- **Group T (Task 1) -- the resolver truth table, no drive at all.** Eight cases calling `eprom_hv_route_mask` directly on a bare handle (`h.protocol` + `h.ctrl_flags` only, no `configure_memory`, no revision override -- the returned mask is logical, the per-revision mapper runs later): the seven named rows (`0x07`/`0x08` no-flag -> `EPROM_HV_ROUTE_MASK`; `0x0B` no-flag -> `CTRL_VPP_REGULATOR_ENABLE` exactly, drop bit absent; all three protocols with `FLAG_VPE_AS_VPP` -> `CTRL_VPP_REGULATOR_ENABLE`; and the fail-closed NULL-row arm for an unrecognised protocol `0x99` -> `EPROM_HV_ROUTE_MASK`, unreachable through any drive since `configure_eprom` already refuses an unknown protocol before an operation pointer is ever installed) plus the mandatory `0x0B`-differs-from-`0x07` non-vacuity leg.
- **Group R (Task 1) -- three route-strobe proofs that the resolved mask reaches the wire.** `0x0B` takes the direct path with no drop bit in any control value (driven at 500us -- the only pulse width `0x0B`'s own energy-cap refusal permits); `--vpe-as-vpp` forces the direct path onto a `0x07` handle, paired against the pre-existing `test_loop08_the_28_pin_row_keeps_its_drop_bit` (the identical row, without the flag, still showing the drop bit) so the pair isolates the flag as the cause; and the D-02 negative -- a 32-pin part on `REVISION_1` has the drop bit SET only at the top-of-block assert and CLEAR at every subsequent control value, the load-bearing negative since Rev 1 carries no `eprom_check_vpp` refusal of its own (unlike Rev 0's `MSG_WARN_REV0_VPP_UNSUPPORTED`).
- **Task 2 -- VPP-03's honest headline, proven directly.** One case captures `eprom_check_vpp`'s measured route (the physical byte its first non-elided control write asserts) and `eprom_write_execute`'s applied route at the first genuine program pulse (located via `first_genuine_pulse_strobe_index` + the largest preceding control-write index) on the `0x08`/32-pin row -- the row where the divergence lived -- and asserts they are the SAME masked physical byte, with three non-vacuity guards preceding the equality. A planted violation (re-introducing the deleted `pins>=32` clear) reproduced the exact pre-142-04 divergence: the case failed with `Expected 129 Was 128` (regulator+drop vs regulator-only), exactly the drop-bit-sized gap D-03 names.
- **Task 3 -- every write-path error exit disables the route.** Three cases: `X4` (the headline `MSG_ERR_VERIFY` final-pass failure, an exit that disabled NOTHING before this phase), `X3` (the `0x0B`-only `MSG_ERR_ENERGY_CAP` exit, unreachable on `0x07`/`0x08` by data), and `E1` (`eprom_write_init`'s error exit, explicitly framed as defensive cover per correction C-3, not a fix). The `row == NULL` exit is recorded as covered-by-construction in `main()`'s registration comment -- no case is faked for an exit no drive can reach.
- **Two planted violations against the write-path wrapper, both measured (not assumed) and both reverted.** `W1` (removed the wrapper's `ERROR`-gated clear) drove `X4` RED on its last-value-clear assertion while `X3`, `E1`, and the sibling suite's own `X2` case all stayed GREEN -- `eprom_internal_report_budget_failure` carries its own independent disable, unaffected by the wrapper. `W2` (made the wrapper unconditional) drove **six** of `test_loop_eprom_v131`'s cases RED, not merely the single tiebreaker the plan names -- measured, not predicted, and reported in full below.

## Task Commits

This plan's three tasks land in a **single** commit, per Task 3's own action text (the only place a commit instruction appears in the plan) and the established two-plan precedent for this file (142-02, 142-03): Tasks 1 and 2 add only test cases plus one planted-and-reverted violation each with no lingering production-source diff, and Task 3's two additional planted-violation-then-revert cycles leave `eprom.cpp`/`eprom.h` byte-identical to the plan-142-04 tip throughout.

1. **Task 1 (Group T + Group R) + Task 2 (VPP-03 equality + planted violation) + Task 3 (X4/X3/E1 + covered-by-construction non-case + planted violations W1/W2)** - `1292a97` (test, in the `firestarter` submodule, branch `gsd/v1.31-27c-programming-algorithm-fidelity`)

Verified against the pre-task anchor: `git rev-list --count 01836fc..1292a97` == `1`.

**Plan metadata:** committed separately in the meta repo (this SUMMARY + STATE.md + ROADMAP.md).

## Files Created/Modified

- `firestarter/test/native/avr/test_vpp_eprom_v131/test_vpp_eprom_v131.cpp` - added 15 cases (8 Group T resolver-truth-table cases, 3 Group R route-strobe cases, 1 VPP-03 measure/apply equality case, 3 VPP-02 write-path exit cases) and their `main()` registration; suite grows from 17 to 32 cases. `src/proms/eprom.cpp` and `include/eprom.h` are byte-identical to the plan-142-04 tip (`git diff --exit-code -- src/ include/` confirmed 0 after every one of the three planted-violation reverts).

## Decisions Made

- **Task 3's X3 oracle avoids the strobe-tail idiom.** A 100-pulse `0x0B` drive (needed to bind the energy cap at exactly 500us x 100 = 50000us) legitimately overflows the 512-entry strobe recorder -- `test_loop_eprom_v131.cpp`'s own named finding, T-141-CAP, applies here identically. `control_write_value(n-1)` would therefore not reliably name the genuine final write. X3 instead reads `h.firestarter_get_control_register(&h, bit)` directly -- the same unbounded logical cache production's own top-of-block gate check reads -- for the final-state assertion, and `control_write_value(0)` (always intact, long before any overflow) for the non-vacuity partner.
- **Case E1 is deliberately, explicitly, the same drive as plan 142-03's VPP-04(b).** Both reach `eprom_check_vpp`'s identical over-voltage refusal through `drive_vpp_init` -- there is no way to exercise `eprom_write_init`'s error exit that does not also exercise `eprom_check_vpp`'s. Per 142-RESEARCH.md's own instruction ("a single case... is cheap non-regression"), this is restated deliberately under VPP-02's requirement (which functions carry the disable guarantee, D-12) rather than invented as a distinct drive, and the case comment states plainly it is defensive cover (C-3), not evidence of a fix.
- **Task 2's non-vacuity guard is asserted on leg A alone, before the equality check.** Leg A (measured via `eprom_check_vpp`) is untouched by the Task 2 planted violation, which edits only the write-path body. Asserting the guard on leg A alone (never on leg B, never jointly) guarantees the plant's failure lands exactly on the equality assertion, matching the plan's own predicted transcript rather than failing one line earlier on a guard that happens to also be broken.
- **A local `vpp_k0b(addr) = addr + 0x2000` adapter was added for `0x0B`'s nonzero `static_high_mask`** (mirroring `test_loop_eprom_v131.cpp`'s `k0b()`) -- this suite's Group R case is the first `0x0B` WRITE it has ever driven; VPP-04's and VPP-03's prior `0x0B`-adjacent cases in this file used only `drive_vpp_init` or non-write commands, never a seeded write requiring the read-back model's key.

## Deviations from Plan

None (Rules 1-4) -- the plan executed exactly as written. Every case, planted violation, and non-case matches the plan's own action text; no bugs, missing functionality, blocking issues, or architectural questions arose during committed work.

## Issues Encountered

**X3's first-draft assertion shape failed on the first run, before any commit.** The initial implementation of `test_vpp02_x3_the_energy_cap_exit_disables_the_route` copied the B-9 idiom verbatim (`strobe_overflowed() == 0` plus `control_write_value(n-1)`), matching the shape used successfully for `X4` and `E1`. It failed immediately (`Expected 0 Was 1` on `strobe_overflowed()`), because `X3` -- uniquely among this plan's three exit cases -- drives 100 pulses on `0x0B` before the energy cap binds, and each pulse's chip-enable/-disable and register-shift strobes push the total past the 512-entry recorder cap. This is not a new discovery: `test_loop_eprom_v131.cpp` names the identical mechanism as T-141-CAP for its own analogous 100-pulse case and deliberately never asserts `strobe_overflowed() == 0` there. The case was rewritten (see Decisions Made) before any task's verification was run for real, so this is normal authoring iteration, not a Rule 1-4 deviation -- nothing broken was ever committed.

**`pio test`'s CLI wrapper mis-reported every multi-run planted-violation check as `[ERRORED]`/`SIGHUP`/`SIGABRT`, not a test defect.** This is the same documented artifact from every prior plan's SUMMARY in this phase (142-02 `SIGQUIT`, 142-03 `SIGINT`, 142-04 `SIGHUP`), reproduced here three more times (once per planted violation, `SIGHUP` for the Task 2 plant and W1, `SIGABRT` for W2) -- and, notably, this time it fired even on runs with only **one** Unity failure (Task 2's plant, W1), not only the ">1 failure" case the gotcha documents. Every one of the three was confirmed via direct binary invocation (`.pio/build/native_loop_v131/firestarter_native`), which reported the authoritative, unambiguous result each time (clean process exit, correct `Tests`/`Failures` counts, no signal) -- not a defect in this suite, the sibling suite, or the underlying Unity result stream.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- All of VPP-01's behavioural evidence (the resolver truth table incl. its unreachable-by-drive fail-closed arm, and all three route-strobe proofs incl. the Rev 1 negative) is now authored and green, ready for plan 142-07 to cite when it flips the requirement checkboxes.
- VPP-03's headline claim (`eprom_check_vpp()` and the write path apply the same routing) is now proven directly on the `0x08` row with a planted-violation transcript reproducing the exact pre-phase divergence -- the strongest form of evidence this milestone offers, and D-03's non-claims (nothing about `0x08` silicon, nothing about AM27C020, no `support_status` change, logical not physical per C-4) are stated in the case's own comment for a future reader who does not have this SUMMARY open.
- VPP-02's exit map is now fully accounted for: `X2` (covered pre-existing, `test_loop_eprom_v131`), `X3`/`X4`/`E1` (covered here), `X1`/row==NULL (named covered-by-construction, no case), `X5`/success (covered pre-existing, the negative control). Both planted violations (W1, W2) demonstrate the write-path wrapper is simultaneously load-bearing (W1: removing its disable breaks the one exit that has no independent clear) and correctly conditional (W2: making it unconditional breaks not one but six pre-existing success-path assertions) -- the full, measured blast radius of W2 is recorded above rather than only the single tiebreaker case the plan names, since a future reader deciding whether to touch this wrapper needs the complete picture.
- No requirement was marked complete (`requirements: []` by design, per this plan's explicit scope boundary) -- `VPP-01`...`VPP-04` remain open for plan 142-07, which now has every piece of evidence VPP-01/02/03 need (VPP-04's evidence landed in plan 142-03).
- `test_vpp_eprom_v131` now carries 32 cases (71 alongside the sibling suite in `native_loop_v131`); plan 142-06 owns a **separate** new file (`firestarter/tests/test_hv_routing_source_contract_v142.py`) and does not touch this one further.
- Every pre-existing gate confirmed unmoved: `native`/`native_nodevtools` at 141/17 each, the 256-test pytest suite, the warning watermark (998/1166), all three AVR targets linking with `macro_redefinition=0`, and `native_trace_v131`'s expected-RED state byte-identical to the 142-04 tip (`Expected 198 Was 91` / `Expected 221 Was 115` / `Expected 201 Was 59`).

---
*Phase: 142-high-voltage-routing*
*Completed: 2026-08-12*

## Self-Check: PASSED

- FOUND: firestarter/test/native/avr/test_vpp_eprom_v131/test_vpp_eprom_v131.cpp
- FOUND commit: 1292a97 (firestarter submodule)
