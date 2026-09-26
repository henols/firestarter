---
phase: 142-high-voltage-routing
plan: 04
subsystem: firmware
tags: [avr, unity, pytest, eprom, vpp, hv-routing, rurp_pinout, protocol-branch-inventory]

# Dependency graph
requires:
  - phase: 142-01
    provides: "EPROM_HV_ROUTE_MASK / EPROM_HV_ALL_OFF_MASK composites in rurp_pinout.h; test_vpp_eprom_v131 harness (make_vpp_handle, drive_vpp_init/_write, set_mock_vpp_mv, control_write_count/_value, REVISION_2_2 override idiom)"
  - phase: 142-02
    provides: "mem_util_calculate_top_address_register's revision-gated drop-bit preserve mask -- the fix that makes D-04's clear-removal correct rather than a regression"
  - phase: 142-03
    provides: "the VPP-04 refusal-gate oracle (four legs) and the pre-rewrite CMD_ERASE/CMD_CHECK_CHIP_ID control-value baselines ([0x80,0x90,0x96,0x10] / [0x80,0x82,0x92,0x10]) that make VPP-03's mask conversion a MEASURED no-op"
provides:
  - "eprom_hv_route_mask(handle) -- the single exposed function (include/eprom.h + src/proms/eprom.cpp) that resolves the EPROM HV route from the eprom_params table's vpp_path column, with FLAG_VPE_AS_VPP forcing the direct-VPE path on top of it. Both eprom_write_execute and eprom_check_vpp call it."
  - "Two conditional single-exit wrappers (eprom_write_init, eprom_write_execute) that clear EPROM_HV_ALL_OFF_MASK only when response_code == RESPONSE_CODE_ERROR -- structural, not remembered, so a future `return` inside either body cannot escape the guarantee. Closes eprom_write_execute's pre-existing MSG_ERR_VERIFY leak."
  - "D-04: the explicit `pins >= 32` drop-bit clear (Phase 141) is REMOVED -- plan 142-02's revision-gated preserve now makes the drop bit survive a 32-pin block's set_address() on Rev 2-class hardware, and this removal is what makes that survival observable in the strobe stream. Proven by the rewritten test_vpp01_dip32_drop_bit_survives_the_block_on_rev2_class."
  - "Q6: eprom_internal_ensure_regulator_enabled deleted -- zero callers anywhere in the tree, a dead duplicate of the resolver's own guard."
  - "The re-derived D-18 golden (tests/golden/protocol_branch_inventory.json, 26 sites, tier-1 3->1) and the strictly-stronger re-pinned locator (test_exactly_one_protocol_keyed_site_at_the_pinned_line), landed in the SAME commit as the eprom.cpp source change."
affects: [142-05, 142-06, 142-07]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Route-resolver-plus-conditional-wrapper: a table-driven resolver replacing duplicated hand-rolled forks, paired with a static-body-plus-public-wrapper split whose disable is gated on response_code rather than unconditional -- the house answer to 'guarantee a cleanup on every error exit without re-paying a per-block cost on success'"
    - "Golden re-derivation via live extractor import, never hand-typed -- diffed against the committed inventory, with hand-authored class/reason fields layered on top of the mechanically-produced (line, predicate, keyed_on, tier) tuples"

key-files:
  created: []
  modified:
    - firestarter/include/eprom.h
    - firestarter/src/proms/eprom.cpp
    - firestarter/test/native/avr/test_loop_eprom_v131/test_loop_eprom_v131.cpp
    - firestarter/tests/golden/protocol_branch_inventory.json
    - firestarter/tests/test_protocol_branch_inventory.py

key-decisions:
  - "D-05/Q4 resolved: eprom_hv_route_mask is EXPOSED (declared in eprom.h), matching the eprom_overprogram_us precedent -- a direct (protocol, ctrl_flags) -> mask truth table is the only way to test the fail-closed NULL-row arm without a full drive."
  - "D-10 amended per operator-confirmed correction C-1: the wrapper's disable is CONDITIONAL on response_code == RESPONSE_CODE_ERROR, not unconditional. Forced by test_loop05_a_successful_block_does_not_disable_the_route, whose assertion was left byte-identical (only its stale comment was replaced)."
  - "D-12 boundary held: no wrapper added to eprom_erase_execute, eprom_check_chip_id_execute or eprom_get_chip_id -- each already clears everything it asserts with no intervening return, so PROJECT.md:189-190 forbids treating that as required shared cleanup."
  - "Q6 resolved: deleted, not kept -- eprom_internal_ensure_regulator_enabled reclaims 0 B (--gc-sections already collected it) and its dead duplicate of the resolver's guard is exactly the divergence risk VPP-03 exists to remove."
  - "Correction (this plan): two of the four 'expected new site' categories named in the plan's own Part M (the resolver's row==NULL fail-closed arm and its vpp_path column comparison) do NOT appear as new tier-2 sites in the live extraction -- both predicates reference only local variables (`row`, not `handle->...`), so _extract_predicates' `_is_relevant` filter excludes them, exactly as it already excluded the pre-existing, structurally identical row==NULL check inside eprom_write_execute. Only the FLAG_VPE_AS_VPP flag check and the two wrappers' response_code gates actually materialized as new sites (3 added, not up to 4). The golden and locator were derived from the mechanical truth, not the plan's prediction."
  - "The :285 (was :189) site's hand-authored reason is corrected, not merely carried forward: its old text cited a stale line-number cross-reference to a branch that no longer exists (the route decision is a function call now). Named explicitly in the golden's own text and in the commit message, mirroring the 141-05 precedent's one named reason-correction."

patterns-established: []

requirements-completed: []

coverage:
  - id: D1
    description: "eprom_hv_route_mask resolves the EPROM HV route from one exposed function driven by the eprom_params table's vpp_path column (FLAG_VPE_AS_VPP overriding on top); both eprom_write_execute and eprom_check_vpp call it, replacing the two duplicated protocol==0x0B||FLAG_VPE_AS_VPP forks. No handle->protocol == comparison remains anywhere in eprom.cpp except the untouched configure_eprom pulse-fallback switch."
    verification:
      - kind: unit
        ref: "Task 1 <verify> inline python script (parts A-H) -- asserts exactly one resolver definition, >=2 call sites, pgm_read_byte read, zero handle->protocol == predicates, exactly one surviving switch(handle->protocol)"
        status: pass
      - kind: unit
        ref: "pio test -e native_loop_v131 -- 56/56 (both suites), including all 4 VPP-04 legs and all 9 VPP-01 truthtable rows from plans 142-01/142-02/142-03, unmoved by this rewrite"
        status: pass
      - kind: unit
        ref: "pio test -e native (141/141, 17 suites) and pio test -e native_nodevtools (141/141, 17 suites) -- both unmoved"
        status: pass
    human_judgment: false
  - id: D2
    description: "Two conditional single-exit wrappers (eprom_write_init, eprom_write_execute) clear EPROM_HV_ALL_OFF_MASK only on response_code == RESPONSE_CODE_ERROR, closing eprom_write_execute's pre-existing MSG_ERR_VERIFY leak structurally while leaving the successful-block case's regulator-stays-SET assertion untouched."
    verification:
      - kind: unit
        ref: "test_loop_eprom_v131.cpp::test_loop05_a_successful_block_does_not_disable_the_route -- assertion lines byte-identical (git diff HEAD~1 confirms only comments changed), PASSED"
        status: pass
      - kind: unit
        ref: "test_loop_eprom_v131.cpp::test_loop05_the_loops_own_strobes_disable_the_high_voltage_route -- widened with a REVISION_2_2 override and a drop-bit clear-leg (K-1), PASSED"
        status: pass
      - kind: other
        ref: "Task 1 <verify> inline python script -- asserts exactly one static eprom_internal_write_execute_body, one static eprom_internal_write_init_body, >=2 response_code==RESPONSE_CODE_ERROR gates, >=6 EPROM_HV_ALL_OFF_MASK references (4 converted disables + 2 wrapper disables)"
        status: pass
    human_judgment: false
  - id: D3
    description: "D-04: the explicit pins>=32 drop-bit clear is removed; D-01/D-02's revision-gated preserve now survives observably. VPP-01's positive proof: test_vpp01_dip32_drop_bit_survives_the_block_on_rev2_class (renamed and inverted from the old test_loop08_dip32_drop_bit_is_cleared_deliberately_before_the_first_pulse) asserts the drop bit present in EVERY control value across a 32-pin block on Rev 2-class hardware, including across an A16 crossing. Q6: the dead eprom_internal_ensure_regulator_enabled helper is deleted."
    verification:
      - kind: unit
        ref: "test_loop_eprom_v131.cpp::test_vpp01_dip32_drop_bit_survives_the_block_on_rev2_class -- PASSED; its 28-pin partner test_loop08_the_28_pin_row_keeps_its_drop_bit unaffected, PASSED"
        status: pass
      - kind: other
        ref: "Pre-edit isolation run confirmed the OLD (pre-142-04) case went RED for exactly the predicted reason ('control write 1 (the explicit pins>=32 clear) must have the drop bit CLEAR') once eprom.cpp's D-04 removal landed but before the test file was rewritten -- 39 Tests 1 Failures 0 Ignored, confirmed via direct binary invocation past the pio test CLI wrapper's known SIGHUP/ERRORED mis-report on a >1-failure-adjacent run"
        status: pass
      - kind: other
        ref: "Task 1 <verify> inline python script -- asserts 'eprom_internal_ensure_regulator_enabled' absent from eprom.cpp"
        status: pass
    human_judgment: false
  - id: D4
    description: "VPP-03 mask consolidation: all four hand-rolled disables (eprom_internal_report_budget_failure, eprom_get_chip_id, eprom_check_vpp, eprom_internal_erase) now reference EPROM_HV_ALL_OFF_MASK. Measured, not just reasoned, byte-identical on the wire via plan 142-03's pre-rewrite CMD_ERASE / CMD_CHECK_CHIP_ID control-value baselines."
    verification:
      - kind: unit
        ref: "test_vpp_eprom_v131.cpp::test_vpp03_case_e_cmd_erase_control_stream_is_pinned_pre_rewrite -- PASSED, reproduces [0x80,0x90,0x96,0x10] unchanged"
        status: pass
      - kind: unit
        ref: "test_vpp_eprom_v131.cpp::test_vpp03_case_i_cmd_check_chip_id_control_stream_is_pinned_pre_rewrite -- PASSED, reproduces [0x80,0x82,0x92,0x10] unchanged"
        status: pass
    human_judgment: false
  - id: D5
    description: "The D-18 golden (protocol_branch_inventory.json) is re-derived by importing the live extractor -- never hand-typed -- and landed in the SAME commit as the eprom.cpp source change (26 sites, tier-1 3->1, 4 removed / 3 added). The locator (renamed test_exactly_one_protocol_keyed_site_at_the_pinned_line) is re-pinned to [70] and proven armed in both directions via planted-violation transcripts run in a child process against a scratch copy."
    verification:
      - kind: unit
        ref: "python3 -m pytest tests/test_protocol_branch_inventory.py -q -o addopts='' -- 7 passed (post-commit); 6 passed/1 failed (pre-commit, the blob-SHA leg only, exactly as L-1 predicts)"
        status: pass
      - kind: other
        ref: "Planted violation A (inserted a fourth handle->protocol==0x08 branch into a /tmp scratch copy via FIRESTARTER_BRANCH_SCAN_SOURCE in a child process) -- RED, found [70, 434], failing on the assertion itself"
        status: pass
      - kind: other
        ref: "Planted violation B (removed the surviving tier-1 site's handle->protocol read from the scratch copy) -- RED, found [], failing on the assertion itself. env | grep -c FIRESTARTER_BRANCH_SCAN confirmed 0 after unsetting both seams; real tree re-ran green."
        status: pass
      - kind: unit
        ref: "python3 -m pytest tests/ -q -o addopts='' -- 256 passed (run only after the commit, per L-1)"
        status: pass
    human_judgment: false

duration: 31min
completed: 2026-08-11
status: complete
---

# Phase 142 Plan 04: High-Voltage Routing -- The `eprom.cpp` Rewrite Summary

**One exposed resolver (`eprom_hv_route_mask`) now drives EPROM HV route selection from the `eprom_params` table's `vpp_path` column at both call sites, two conditional single-exit wrappers close the write path's pre-existing `MSG_ERR_VERIFY` disable leak, the Rev-2-class drop bit now survives a 32-pin block observably, and the D-18 protocol-branch-inventory golden was re-derived and landed in the same single commit as the source change (26 sites, tier-1 3->1) -- all five files, one commit, verified by direct binary invocation past a known `pio test` CLI wrapper artifact and two child-process planted-violation transcripts.**

## Performance

- **Duration:** 31 min
- **Started:** 2026-08-11T22:59:11Z
- **Completed:** 2026-08-11T23:30:54Z
- **Tasks:** 1 (deliberately one large atomic task, per the plan's one-commit constraint)
- **Files modified:** 5

## Accomplishments

- Added `eprom_hv_route_mask(firestarter_handle_t* handle)` -- declared in `include/eprom.h` (Q4: exposed, not file-static, matching the `eprom_overprogram_us` precedent), defined in `src/proms/eprom.cpp`. Resolution order: `FLAG_VPE_AS_VPP` first (D-06, forces the direct-VPE path on top of the table), then `eprom_params_for(handle->protocol)`/`row == NULL` fail-closed toward `EPROM_HV_ROUTE_MASK`, then `row->vpp_path` (via `pgm_read_byte` only) selecting the direct-VPE or drop-resistor mask. Both `eprom_write_execute`'s body and `eprom_check_vpp` now call this one function (VPP-03), replacing the two byte-identical hand-rolled `protocol==0x0B||FLAG_VPE_AS_VPP` forks that used to live at what were `:190` and `:340`.
- Removed the explicit `pins >= 32` drop-bit clear Phase 141 added (D-04): plan 142-02's revision-gated preserve mask now makes an explicit clear here actively wrong on Rev 2-class hardware, since it would re-strip the very bit the route guard just asserted before the fix ever gets a chance to matter.
- Split `eprom_write_execute` and `eprom_write_init` into `static` inner bodies plus public wrappers that clear `EPROM_HV_ALL_OFF_MASK` **only** when `response_code == RESPONSE_CODE_ERROR` (D-10 as amended, operator-confirmed correction C-1, D-12) -- structural, so a future `return` inside either body cannot silently escape the guarantee. `eprom_write_execute`'s wrapper is corrective (closes the pre-existing `MSG_ERR_VERIFY` leak, the headline VPP-02 gap that disabled nothing before this plan); `eprom_write_init`'s is defensive (neither of its own exits leaked a route before this plan). Held D-12's boundary: no wrapper added to `eprom_erase_execute`, `eprom_check_chip_id_execute`, or `eprom_get_chip_id`, per `PROJECT.md:189-190`.
- Converted all four hand-rolled disables (`eprom_internal_report_budget_failure`, `eprom_get_chip_id`, `eprom_check_vpp`, `eprom_internal_erase`) to reference the shared `EPROM_HV_ALL_OFF_MASK` composite (VPP-03). Confirmed byte-identical on the wire, measured rather than reasoned: plan 142-03's pre-rewrite `CMD_ERASE` (`[0x80,0x90,0x96,0x10]`) and `CMD_CHECK_CHIP_ID` (`[0x80,0x82,0x92,0x10]`) control-value baselines both reproduce identically against this commit.
- Deleted `eprom_internal_ensure_regulator_enabled` (Q6) -- zero callers anywhere in `src/`, `include/`, `test/` or `tests/`, a dead duplicate of the resolver's own once-per-block guard.
- Rewrote and renamed `test_loop08_dip32_drop_bit_is_cleared_deliberately_before_the_first_pulse` to `test_vpp01_dip32_drop_bit_survives_the_block_on_rev2_class` (Q1) -- the inversion VPP-01 needs: the `v0` top-of-block assertion survives unchanged, and the old `v1`-clears / ordering assertions are replaced by a positive claim that the drop bit is present in **every** control value across the whole block, including across the A16 crossing this block deliberately drives through.
- Widened `test_loop05_the_loops_own_strobes_disable_the_high_voltage_route` (K-1) to also assert the drop bit clears on the wrapper's error exit, which required adding a `REVISION_2_2` override (L-6: the assertion would otherwise be undecidable, not merely weak, since the drop bit and A16 share a physical bit on the default `REVISION_0` this case used to run on).
- Re-derived the D-18 golden (`tests/golden/protocol_branch_inventory.json`) by importing the live extractor and diffing its output against the committed inventory -- never hand-typed. Net movement: 27 -> 26 total sites, tier-1 3 -> 1 (4 removed, 3 added), landed in the exact same commit as the `eprom.cpp` change so the D-18 gate goes RED once, for one reason.
- Re-pinned the locator (renamed `test_exactly_three_protocol_keyed_sites_at_the_pinned_lines` to `test_exactly_one_protocol_keyed_site_at_the_pinned_line`, literal `[70, 190, 340]` -> `[70]`) and proved it armed in both directions with planted-violation transcripts run in a child process against a `/tmp` scratch copy.

## Task Commits

This plan is deliberately **one task, one commit** (per the plan's own `<one_commit_constraint>`: the D-18 golden pins `eprom.cpp`'s blob SHA, so splitting the source change from its golden re-derivation would leave the gate RED between commits for no nameable reason):

1. **Task 1: Rewrite `eprom.cpp`'s high-voltage routing, re-point the LOOP-08 case and re-derive the D-18 golden -- five files, ONE commit** - `01836fc` (feat, in the `firestarter` submodule, branch `gsd/v1.31-27c-programming-algorithm-fidelity`)

Verified against the pre-task anchor: `git rev-list --count 4a890b93c4844a3b980465aa1feb5488bcb7feca..HEAD` == `1`.

**Plan metadata:** committed separately in the meta repo (this SUMMARY + STATE.md + ROADMAP.md).

## Files Created/Modified

- `firestarter/include/eprom.h` - declared `eprom_hv_route_mask` (Q4: exposed, not file-static)
- `firestarter/src/proms/eprom.cpp` - the resolver, its two call sites, the two conditional single-exit wrappers, the four composite disables, deleted the `pins >= 32` clear and the dead regulator helper
- `firestarter/test/native/avr/test_loop_eprom_v131/test_loop_eprom_v131.cpp` - renamed/rewrote the inverted LOOP-08 case as VPP-01's positive proof, widened the disable case with a `REVISION_2_2` override, updated a stale comment (assertion untouched) in the must-stay-green successful-block case
- `firestarter/tests/golden/protocol_branch_inventory.json` - re-derived `sites[]` (26, tier-1 3->1), updated counts/blob-SHA/`frozen_for`/`allowlist_rationale`
- `firestarter/tests/test_protocol_branch_inventory.py` - renamed and re-pinned the tier-1 locator test to `[70]`

## Decisions Made

- **D-05/Q4 (resolved):** `eprom_hv_route_mask` is exposed via `include/eprom.h`, matching the `eprom_overprogram_us` precedent -- a direct `(protocol, ctrl_flags) -> mask` truth table is the only way to test the fail-closed NULL-row arm without a full drive.
- **D-10 amended (operator-confirmed correction C-1):** both wrappers' disables are conditional on `response_code == RESPONSE_CODE_ERROR`, not unconditional. The tiebreaker, `test_loop05_a_successful_block_does_not_disable_the_route`, was left assertion-for-assertion byte-identical (`git diff HEAD~1` confirms only its comment changed) -- an unconditional disable would re-arm the once-per-block guard and re-pay `delay(500)` on the next block too, ~64s over a 64K Uno write.
- **D-12 boundary held:** no wrapper on `eprom_erase_execute`, `eprom_check_chip_id_execute`, or `eprom_get_chip_id` -- each already clears everything it asserts with no intervening `return`, so `PROJECT.md:189-190` forbids treating a wrapper there as required shared cleanup.
- **Q6 (resolved):** `eprom_internal_ensure_regulator_enabled` is deleted, not kept -- it reclaims 0 B (`--gc-sections` already collected it) and is exactly the kind of dead duplicate VPP-03 exists to remove.
- **Correction to the plan's own Part M prediction:** the plan anticipated up to four new tier-2 sites from the resolver (the `FLAG_VPE_AS_VPP` check, the `row == NULL` fail-closed arm, the `vpp_path` comparison) plus the two wrapper gates. Running the live extractor shows only **three** new sites actually materialize: the `FLAG_VPE_AS_VPP` check and the two wrapper gates. The `row == NULL` and `vpp_path` comparisons reference only the local `row` variable, never `handle->...` or one of the three predicate helpers, so `_extract_predicates`' `_is_relevant` filter excludes them -- exactly as it already excluded the pre-existing, structurally identical `row == NULL` check inside `eprom_write_execute` before this plan touched anything. The golden and locator are derived from this measured truth, not the plan's prediction, per the explicit instruction to "derive the real number; do not assume it."
- **One named reason-correction (mirroring the 141-05 precedent):** the surviving site at (now) `:285` (was `:189`) had a hand-authored reason citing a stale line-number cross-reference to a branch that is no longer there at all (the route decision is a single function call now, not an inline fork). Rewritten to name no line number for that call, so it cannot go stale the same way twice -- named explicitly in the golden's own text and in the commit message rather than silently carried forward.

## Deviations from Plan

None (Rules 1-4) -- the plan executed exactly as written; no bugs, missing functionality, blocking issues, or architectural questions arose. The one discrepancy worth naming (documented under Decisions Made above, not as a Rule 1-4 auto-fix) is that the plan's own speculative count of "new sites the resolver might introduce" over-predicted by one relative to what the live extractor actually produces -- this is a measurement correcting a prediction, not a deviation from any instruction, and the plan itself anticipated this possibility ("Derive the real number; do not assume it").

## Issues Encountered

**`pio test`'s CLI wrapper mis-reported the pre-edit isolation run (1 Unity failure) as `[ERRORED]`/`SIGHUP`, not a test defect.** After landing `eprom.cpp`'s D-04 removal but before rewriting the test file, `pio test -e native_loop_v131 -f "*test_loop_eprom_v131*"` printed the one expected `FAILED` line correctly, then reported `Program received signal SIGHUP (Hangup)` and `[ERRORED]`. Running `.pio/build/native_loop_v131/firestarter_native` directly showed the authoritative, unambiguous result: `39 Tests 1 Failures 0 Ignored`, clean process exit, the exact predicted failure text ("control write 1 (the explicit pins>=32 clear) must have the drop bit CLEAR"). This is the same documented artifact from 142-02's and 142-03's SUMMARYs (there `SIGQUIT`/`SIGINT`), reproduced here as `SIGHUP` -- a different signal name, same non-defect: `pio test`'s wrapper only special-cases `UNITY_END()`'s return value at exactly 0 or 1. `native_trace_v131`'s later run in this same session hit the identical artifact (`SIGQUIT`, 3 failures) and was likewise confirmed via direct binary invocation.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Plan 142-05 and 142-06 can now extend `test_vpp_eprom_v131.cpp` against the landed resolver, wrappers, and composite conversions -- no further `eprom.cpp` structural change is expected from either.
- `native_trace_v131`'s expected-RED state (D-17, not fixed, not silenced) moved for the first time this milestone on the `0x08` row specifically: `Expected 221 Was 115` (was `Was 119` at the Phase 141 tip through plan 142-03) -- a decrease of exactly 4, consistent with this being the first plan to actually remove a control-register write from the 32-pin write path (D-04's clear-removal). The `0x07` (`Expected 198 Was 91`) and `0x0B` (`Expected 201 Was 59`) rows are unmoved, exactly as expected since neither protocol's write path changed. Plan 142-07 should cite this new value, not the old one, when it names the RED as expected.
- Flash/RAM figures for all three AVR targets, measured incrementally (the authoritative **cold** triple-target measurement is plan 142-07's per the plan's own instruction): `uno` 24568/32256 B (76.2%) / 1573/2048 B RAM (76.8%); `uno328pb` 24618/32384 B (76.0%) / 1579/2048 B RAM (77.1%); `leonardo` 26542/28672 B (**92.6%**, 2130 B headroom) / 2014/2560 B RAM (78.7%). Leonardo's headroom decreased by 138 B relative to the 142-02 tip's 2268 B (26404 B used there) -- still a comfortable link success, not a failure, but Phase 143 needs to be aware the margin narrowed further this plan.
- The native warning watermark is unmoved: 998/1166 on both `native` and `native_nodevtools`, 168 below the zero-headroom ceiling.
- No requirement was marked complete (`requirements: []` by design, per this plan's explicit scope boundary) -- `VPP-01`...`VPP-04` remain open for plan 142-07 to flip after all evidence exists across the whole phase.
- `firestarter/CLAUDE.md`'s `0x08` row (the pre-existing-defect Notes paragraph) is now stale relative to this plan's fix and is plan 142-07's own docs-only commit to update, per the house convention confirmed in 142-PATTERNS.md §J-1 (checked against the last 10 `CLAUDE.md`-touching commits: zero also touched `src/proms/`).

---
*Phase: 142-high-voltage-routing*
*Completed: 2026-08-11*

## Self-Check: PASSED

- FOUND: firestarter/include/eprom.h
- FOUND: firestarter/src/proms/eprom.cpp
- FOUND: firestarter/test/native/avr/test_loop_eprom_v131/test_loop_eprom_v131.cpp
- FOUND: firestarter/tests/golden/protocol_branch_inventory.json
- FOUND: firestarter/tests/test_protocol_branch_inventory.py
- FOUND commit: 01836fc (firestarter submodule)
