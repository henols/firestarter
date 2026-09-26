---
phase: 142-high-voltage-routing
verified: 2026-08-12T02:19:32Z
status: passed
score: 17/17 must-haves verified
overrides_applied: 0
---

# Phase 142: High-Voltage Routing Verification Report

**Phase Goal:** Every 27C protocol drives its correct high-voltage path through one shared, mask-based mechanism, every write-path exit disables every active route, and the pre-existing over-voltage refusal still holds after the loop rewrite. (VPP-01, VPP-02, VPP-03, VPP-04)

**Verified:** 2026-08-12T02:19:32Z
**Status:** passed
**Re-verification:** No — initial verification (no prior `142-VERIFICATION.md` existed)

## Method

This report is built entirely from independent re-derivation, not from trusting `142-VPP-RECORD.md` or the seven `SUMMARY.md` files. For every claim checked below I either read the actual source at the cited line, ran the actual test/build command myself in this session, or diffed actual git history — the record and summaries were used only to know *where* to look, never as the evidence itself. Where my own run reproduced a number from the record byte-for-byte (test counts, flash bytes, `Was`/`Expected` trace values, MERGE-05 deltas), that is called out explicitly.

Commands actually executed this session (all from `/workspaces/firestarter`, HEAD `1d64bb5`, working tree clean):
- `pio test -e native` → **141/141 passed** (independently reproduced)
- `pio test -e native_nodevtools` → **141/141 passed** (independently reproduced)
- `pio test -e native_loop_v131` → **71/71 passed** (39 `test_loop_eprom_v131` + 32 `test_vpp_eprom_v131`, independently reproduced)
- `pio test -e native_params_v131` → **9/9 passed**, unmoved (independently reproduced)
- `pio test -e native_trace_v131` → **3 failed / 2 succeeded**, `Was 91/115/59` vs `Expected 198/221/201` — byte-identical to the record's claimed expected-RED values (independently reproduced)
- `python3 -m pytest tests/ -o addopts="" -q` → **272 passed** (independently reproduced)
- `python3 -m pytest tests/test_hv_routing_source_contract_v142.py -v` → **16/16 passed**
- `python3 -m pytest tests/test_protocol_branch_inventory.py` → **7/7 passed**
- `pio run -t clean -e uno && pio run -e uno` (cold) plus warm `pio run -e uno328pb` / `-e leonardo` → **24568 / 24618 / 26542 B flash**, **1573 / 1579 / 2014 B RAM** — byte-identical to the record's cold figures
- `python3 scripts/check_size_baseline.py --policy merge05 --rebuild` → **FAIL**, deltas `+614/+614/+526` — byte-identical to the record
- same, with `--baseline scripts/baseline/size_baseline_base01.json` → **FAIL**, deltas `+636/+642/+470` — byte-identical to the record
- `python3 scripts/check_build_warnings.py --rebuild` → **PASS**, `998` vs watermark `1166` — byte-identical to the record
- `git diff --exit-code -- scripts/baseline/size_baseline*.json` → clean (both baseline JSONs untouched)
- `git rev-list --count 4a890b9..01836fc` → `1` (the D-18 one-commit property, independently confirmed)
- `git rev-parse HEAD:src/proms/eprom.cpp` / `HEAD:src/proms/eprom_params.cpp` → match the golden's `blob_shas` exactly
- `git diff --stat 4921388..1d64bb5` (Phase-141 tip → Phase-142 tip) → exactly the 12 files the seven plans' `files_modified` union declares, nothing more
- `git grep "MSG_ERR_VPP_HIGH\|MSG_WARN_VPP_HIGH" 4921388 -- test/ tests/` → **zero hits** (independently confirms VPP-04's gate is genuinely new, D-13)
- Meta repo: `git show c061d24a` → exactly an 8-line `REQUIREMENTS.md` diff + 4-line `ROADMAP.md` diff + new `142-VPP-RECORD.md`, no collateral changes

## Goal Achievement

### Observable Truths

| # | Truth | SC | Status | Evidence |
|---|---|---|---|---|
| 1 | A single resolver `eprom_hv_route_mask()` selects 0x07/0x08 → regulator+drop path, 0x0B → direct path, from the table's `vpp_path` column, replacing the two duplicated hand-rolled predicates | SC1 | VERIFIED | `src/proms/eprom.cpp:255-267` (resolver body); called at `:286` (write path) and `:458` (`eprom_check_vpp`) — exactly 2 sites, confirmed by `grep -n eprom_hv_route_mask`. 8 resolver truth-table tests (`test_vpp01_resolver_*`) all PASSED. |
| 2 | `--vpe-as-vpp` (`FLAG_VPE_AS_VPP`) still forces the direct-VPE path on top of the resolver, for any protocol | SC1 | VERIFIED | `eprom.cpp:256-258` (checked first in the resolver). `test_vpp01_route_vpeasvpp_forces_the_direct_path_onto_0x07` PASSED. |
| 3 | On Rev 2-class hardware (`REVISION_2_0.._2_3`) the drop bit for a 32-pin (0x08) block now survives every `set_address()` of the block; on Rev 0 / Rev 1 / unknown / legacy it is deliberately, unchangedly still stripped | SC1 (qualified) | VERIFIED — see note below | `memory.cpp:199-228` (revision-gated preserve mask). Physical bit-sharing claim independently confirmed at `rurp_hw_rev_utils.h:28-32` and `rurp_pinout.h:170` (`CTRL_ADDRESS_LINE_16_REV1` **is** `CTRL_VPP_VPE_DROP_ENABLE_REV1` — a genuine alias, not asserted-only). Positive proof `test_vpp01_dip32_drop_bit_survives_the_block_on_rev2_class` and negative proof `test_vpp01_route_0x08_on_rev1_still_strips_the_drop_bit` both read and both PASSED. |
| 4 | Every reachable error-type exit of the write path (max-pulse, energy-cap, and — new this phase — the final-pass verify-mismatch exit) structurally disables the shared composite via a single-exit wrapper | SC2 | VERIFIED | `eprom.cpp:401-429` (`eprom_write_execute` wrapper, `if (response_code==ERROR) { ...EPROM_HV_ALL_OFF_MASK, 0); }`). **Confirmed via git history, not just the plan's prose:** at the Phase-141 tip (`4921388:src/proms/eprom.cpp:294-312`), the `MSG_ERR_VERIFY` final-pass exit set `response_code = RESPONSE_CODE_ERROR` and returned **with no disable call at all** — a real, pre-existing gap this phase closes. Tests `test_vpp02_x4_the_final_pass_verify_failure_disables_the_route`, `test_vpp02_x3_the_energy_cap_exit_disables_the_route` PASSED. |
| 5 | `eprom_write_init`'s defensive wrapper carries the identical conditional-disable structure | SC2 | VERIFIED | `eprom.cpp:163-180`. `test_vpp02_e1_write_init_error_exit_leaves_no_route_asserted` PASSED. |
| 6 | The operation-level exit of the whole `CMD_WRITE` command (success or abort/timeout) unconditionally disables every route via `command_done()`, reached from both of `loop()`'s dispatch arms | SC2 | VERIFIED (source-level only) | `firestarter.cpp:162-171` zeroes `CONTROL_REGISTER`/`LEAST_SIGNIFICANT_BYTE`/`MOST_SIGNIFICANT_BYTE` unconditionally; called at `:176` (timeout-abort arm) and `:290` (`if (finished)` arm) — both read directly. Asserted as a **source contract** by 4 dedicated pytest legs (`test_command_done_*`), all PASSED — correctly **not** claimed as behaviorally proven on real AVR hardware (`firestarter.cpp`/`eprom_operations.cpp` sit outside every native `build_src_filter`; this is disclosed, not hidden). |
| 7 | A **successful block** mid-transfer deliberately leaves the route energized (avoids re-paying the once-per-block 500 ms settle); this is a continuation of Phase 141's own LOOP-08 design, not an unpatched exit | SC2 (see note) | VERIFIED — see note below | `eprom.cpp:406-422` comment + `test_loop05_a_successful_block_does_not_disable_the_route` (test/native/avr/test_loop_eprom_v131, PASSED) asserts the route stays SET on a converged block. |
| 8 | `eprom_check_vpp()` and the write path resolve and apply their route through the *same* function and the *same* two composites | SC3 | VERIFIED | `eprom.cpp:458` and `:286` both call `eprom_hv_route_mask()`; `:505` and `:427` both clear via `EPROM_HV_ALL_OFF_MASK`. `test_vpp03_check_vpp_measures_the_route_the_write_path_applies_at_the_first_pulse` PASSED. |
| 9 | `EPROM_HV_ROUTE_MASK` / `EPROM_HV_ALL_OFF_MASK` are each defined exactly once across `include/` | SC3 | VERIFIED | `rurp_pinout.h:150-151`, confirmed sole definitions by direct grep. Structural pytest `test_each_hv_composite_is_defined_exactly_once_across_include` (globs all of `include/`, non-vacuity-guarded) PASSED. |
| 10 | No hand-rolled duplicate of the old `protocol==0x0B \|\| FLAG_VPE_AS_VPP` fork survives in the write path; protocol-keyed (tier-1) sites fell 3→1 | SC3 | VERIFIED | `tests/golden/protocol_branch_inventory.json`: `counts = {total: 26, protocol_keyed: 1, other: 25}`; the one surviving tier-1 site is line 70's untouched pulse-fallback switch. Structural pytest legs `test_no_second_algorithm_selector_predicate_survives_in_the_write_path` and `test_no_literal_regulator_and_drop_bit_or_sequence_survives` PASSED. |
| 11 | An out-of-range EPROM VPP reading refuses (`MSG_ERR_VPP_HIGH`/ERROR), downgrades under `FLAG_FORCE` (`MSG_WARN_VPP_HIGH`/WARNING), and an in-range reading fires neither | SC4 | VERIFIED | `eprom.cpp:463-484`. Four dedicated tests `test_vpp04_a/b/c/d_*` all PASSED. |
| 12 | The refusal path leaves no high-voltage route asserted | SC4 | VERIFIED | `test_vpp04_b_no_hv_route_left_asserted_on_the_refusal_path` PASSED. |
| 13 | This VPP-04 gate is genuinely newly-authored, not a re-verification of a pre-existing gate (VPP-04's own wording presumed one already existed for the EPROM path — a premise this phase corrects) | SC4 | VERIFIED | `git grep -c "MSG_ERR_VPP_HIGH\|MSG_WARN_VPP_HIGH" 4921388 -- test/ tests/` → **0 matches** anywhere in the tree before this phase, independently confirming the D-13 premise correction rather than trusting the record's own claim. |
| 14 | Golden `protocol_branch_inventory.json` was re-derived in the **same commit** as the `eprom.cpp` rewrite (D-18's one-commit property), and its recorded blob SHAs match the live tree | Cross-cutting | VERIFIED | `git rev-list --count 4a890b9..01836fc` = `1`. `git rev-parse HEAD:src/proms/eprom.cpp` = `17f5f418...`, `HEAD:src/proms/eprom_params.cpp` = `5dffe841...` — both match `meta.blob_shas` in the JSON exactly. |
| 15 | `firestarter/CLAUDE.md`'s algorithm-handler documentation is reconciled with the shipped resolver; the old "pre-existing defect" framing for 0x08 is retired with a replacement, not silently deleted | Cross-cutting | VERIFIED | `git diff 4921388..1d64bb5 -- CLAUDE.md`: the 0x08 row's VPP cell and Notes are fully rewritten (route resolution, Rev-class qualification, "honest headline", D-03 boundary) — content replaced, not removed; 0x07/0x0B rows updated consistently. |
| 16 | VPP-01..04 flipped to Complete in `REQUIREMENTS.md`/`ROADMAP.md` in one minimal, evidence-following edit, no collateral changes | Cross-cutting | VERIFIED | Meta commit `c061d24a`: exactly an 8-line `REQUIREMENTS.md` diff (4 checkbox flips + 4 coverage-table flips) and a 4-line `ROADMAP.md` diff (4 coverage-table flips), read in full — nothing else moved. No orphaned requirements: `142-07-PLAN.md` is the only plan declaring `requirements:` and it names exactly VPP-01..04, matching `REQUIREMENTS.md`'s Phase-142 mapping. |
| 17 | Per-target flash/RAM measured cold on all three AVR targets; MERGE-05 correctly left RED (not this phase's job — D-16); `native_trace_v131` correctly left RED (expected — D-17) | Cross-cutting | VERIFIED | Independently reproduced byte-for-byte: uno 24568 B / 1573 B, uno328pb 24618 B / 1579 B, leonardo 26542 B / 2014 B (cold-verified for uno via `pio run -t clean` + rebuild). MERGE-05 fails with the exact recorded deltas against both anchors; baseline JSONs confirmed byte-unchanged. |

**Score:** 17/17 truths verified (0 overrides used)

**Two items above ("qualified" / "see note") deserve explicit human attention even though I classify both as VERIFIED — they are not gaps, but a future reader taking `ROADMAP.md`'s SC1/SC2 wording 100% literally could reasonably disagree with my reading:**

- **SC1's literal wording** ("`0x07` and `0x08` route through the regulator + VPE-to-VPP dropping path") is **unconditionally true only for route *selection*** (the resolver always picks the drop path for 0x08 regardless of hardware revision). Whether that asserted drop bit **survives** past the first byte of a multi-byte block is revision-dependent: true on Rev 2-class, **not** true on Rev 0/Rev 1 (deliberately, because the drop bit and `CTRL_ADDRESS_LINE_16` are the same physical register bit on those revisions — I verified this directly in `rurp_hw_rev_utils.h`, not just in a comment). `142-VPP-RECORD.md` §5 states this qualification explicitly; I independently re-derived and confirmed it rather than accepting the prose.
- **SC2's literal wording** lists "success" alongside "verify failure, max-pulse failure, error return" as write-path exits that must all disable. I read "success" as the **operation-level** exit (the whole `CMD_WRITE` finishing, handled unconditionally by `command_done()`), not the **per-block** success inside a still-continuing multi-block transfer (which deliberately stays energized, per Phase 141's pre-existing LOOP-08 optimization and the operator-confirmed C-1/D-10 amendment). I traced the actual control flow (`op_execute_function` → `RESPONSE_CODE_ERROR` → `finished=true` → `command_done()` on the **same** `loop()` iteration for every error case) to confirm every *terminating* exit does disable; only a genuinely-continuing intermediate block does not, which is not "an exit from the write path" under that reading.

Both readings are well-supported by direct source and test evidence and match a documented, operator-approved decision (C-1). I flag them here rather than silently resolving them because a stricter literal reading exists and the operator should be aware this report chose the non-literal-but-intentional reading.

### Required Artifacts

| Artifact | Expected | Status | Details |
|---|---|---|---|
| `firestarter/include/rurp_pinout.h` | `EPROM_HV_ROUTE_MASK` / `EPROM_HV_ALL_OFF_MASK` composites | VERIFIED | Lines 151-152, both build variants documented and correct (0x81/0x180, 0x87/0x186 per the header's own worked example) |
| `firestarter/include/eprom.h` | Exposed resolver declaration | VERIFIED | `include/eprom.h:58` |
| `firestarter/src/proms/eprom.cpp` | Resolver + 2 call sites + 2 conditional single-exit wrappers + composite disables + deletions (dead helper, `pins>=32` clear) | VERIFIED | Read in full 130-560; `eprom_internal_ensure_regulator_enabled` confirmed absent (`grep` zero hits) |
| `firestarter/src/proms/memory.cpp` | Revision-gated preserve arm | VERIFIED | Lines 163-231 |
| `firestarter/platformio.ini` | `test_vpp_eprom_v131` wired into `[env:native_loop_v131]` (`test_filter` + `-I`) | VERIFIED | Lines 419, 423 |
| `firestarter/test/native/avr/test_vpp_eprom_v131/host_stubs.cpp` | Recorder + injection layers, min 200 lines | VERIFIED | 322 lines |
| `firestarter/test/native/avr/test_vpp_eprom_v131/test_vpp_eprom_v131.cpp` | Full VPP-01..04 harness + cases, min 200/300 lines (per-plan) | VERIFIED | 1379 lines, 32 cases run in this env |
| `firestarter/tests/golden/protocol_branch_inventory.json` | Re-derived counts/blob SHAs | VERIFIED | `{total:26, protocol_keyed:1, other:25}`; blob SHAs match live tree |
| `firestarter/tests/test_protocol_branch_inventory.py` | Re-pinned locator (`[70]`) | VERIFIED | 7/7 passed |
| `firestarter/tests/test_hv_routing_source_contract_v142.py` | 16-leg structural gate, min 200 lines | VERIFIED | 806 lines, 16/16 passed |
| `firestarter/CLAUDE.md` | Algorithm-handler rows reconciled | VERIFIED | Diff read in full |
| `.planning/phases/142-high-voltage-routing/142-VPP-RECORD.md` | Phase record, min 150 lines | VERIFIED | 522 lines; cross-checked claim-by-claim against source/tests/git history above |
| `.planning/REQUIREMENTS.md`, `.planning/ROADMAP.md` | VPP-01..04 flipped Complete | VERIFIED | Commit `c061d24a`, minimal diff confirmed |

### Key Link Verification

| From | To | Via | Status | Details |
|---|---|---|---|---|
| `platformio.ini` `[env:native_loop_v131]` | `test/native/avr/test_vpp_eprom_v131/` | `test_filter` + `-I` entries | WIRED | Both lines present (:419, :423); suite executes and passes |
| `eprom.cpp` write path | `eprom_hv_route_mask` | direct call | WIRED | 2 call sites (`:286`, `:458`) |
| `eprom.cpp` | `eprom_params_for(handle->protocol)` → `pgm_read_byte(&row->vpp_path)` | resolver body | WIRED | `:259-266`; `EPROM_PARAM_KEYS = {0x07,0x08,0x0B}` matches `configure_memory`'s own EPROM dispatch precondition exactly, so the `row==NULL` fail-closed arm is unreachable by construction, not merely by assertion (independently re-derived, not taken on faith) |
| `tests/golden/protocol_branch_inventory.json` | `src/proms/eprom.cpp` / `eprom_params.cpp` | `meta.blob_shas` equality | WIRED | Confirmed via `git rev-parse` |
| `tests/test_hv_routing_source_contract_v142.py` | `src/firestarter.cpp` / `src/proms/eprom.cpp` | `FIRESTARTER_HV_SCAN_DISPATCH_SOURCE` / `FIRESTARTER_HV_SCAN_EPROM_SOURCE` env seams | WIRED | Both seams read at import time, confirmed in source; 16/16 tests pass against the real files by default |
| `firestarter.cpp:loop()` | `command_done()` | both dispatch arms | WIRED | `:176` (timeout-abort), `:290` (`if (finished)`) — both read directly |
| `.planning/REQUIREMENTS.md` / `.planning/ROADMAP.md` | VPP-01..04 | hand edit, commit `c061d24a` | WIRED | Diff confirmed minimal and correct |

### Data-Flow / Control-Flow Trace (Level 4, firmware-adapted)

There is no UI/DB data flow in this phase; the equivalent trace is table value → resolver → physical register write, which I followed end to end rather than trusting the resolver's existence alone:

| Stage | Source | Confirms |
|---|---|---|
| Table column | `eprom_params.cpp`'s `EPROM_PARAMS[].vpp_path` (PROGMEM) | Read only via `pgm_read_byte`, never a raw dereference (would silently return RAM garbage on AVR) |
| Resolver | `eprom_hv_route_mask()` | Maps `vpp_path` → `CTRL_VPP_REGULATOR_ENABLE` (direct) or `EPROM_HV_ROUTE_MASK` (drop), with `FLAG_VPE_AS_VPP` and `row==NULL` handled first, both fail-closed |
| Application | `eprom_check_vpp()` and `eprom_internal_write_execute_body()` | Both apply the resolver's return value directly to `firestarter_set_control_register`, proven byte-identical by `test_vpp03_check_vpp_measures_the_route_the_write_path_applies_at_the_first_pulse` |
| Persistence across the block | `mem_util_calculate_top_address_register()`'s preserve mask | Revision-gated; proven both ways (Rev2 positive, Rev1 negative) against the real per-byte `set_address()` path, not a synthetic call |
| Teardown | `command_done()` | Unconditional zero of the 3 registers carrying every route bit this phase touches |

Status: **FLOWING** at every stage — no static/hardcoded shortcut found anywhere in this chain.

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|---|---|---|---|
| Native dispatch/protocol suites unaffected | `pio test -e native` | 141/141 passed | PASS |
| Native dispatch suites (no-devtools variant) unaffected | `pio test -e native_nodevtools` | 141/141 passed | PASS |
| New VPP suite + existing loop suite | `pio test -e native_loop_v131` | 71/71 passed | PASS |
| Params table unmoved | `pio test -e native_params_v131` | 9/9 passed | PASS |
| Trace fixture expected-RED reproduces exact values | `pio test -e native_trace_v131` | 3 failed/2 succeeded, `Was 91/115/59` vs `Expected 198/221/201` | PASS (matches expected-RED design) |
| Firmware host-side pytest suite | `python3 -m pytest tests/ -o addopts="" -q` | 272 passed | PASS |
| AVR builds succeed within budget | `pio run -t clean -e uno && pio run -e uno`, `pio run -e uno328pb`, `pio run -e leonardo` | SUCCESS, 24568/24618/26542 B | PASS |
| MERGE-05 correctly stays RED (not this phase's job) | `check_size_baseline.py --policy merge05 --rebuild` (both anchors) | FAIL, deltas match record exactly | PASS (expected/deliberate RED) |
| Warning watermark holds | `check_build_warnings.py --rebuild` | PASS, 998 vs 1166 | PASS |

### Probe Execution

No `scripts/*/tests/probe-*.sh` files exist in this repository and neither the plans nor the summaries for this phase declare any probe script. **SKIPPED (no probes declared or found for this phase).**

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|---|---|---|---|---|
| VPP-01 | 142-07 (cites 142-02, 142-04, 142-05) | `0x07`/`0x08` use the regulator+drop path, `0x0B` the direct path, selected by `vpp_path` | SATISFIED | Truths 1-3 above |
| VPP-02 | 142-07 (cites 142-04, 142-05, 142-06) | Every exit from the write path disables every active route | SATISFIED | Truths 4-7 above |
| VPP-03 | 142-07 (cites 142-04, 142-05, 142-06) | `eprom_check_vpp()` and all write/error paths share one mask set | SATISFIED | Truths 8-10 above |
| VPP-04 | 142-07 (cites 142-03) | Over-voltage refusal unchanged, re-verified against the existing gate | SATISFIED | Truths 11-13 above |

**Orphan check:** `REQUIREMENTS.md` maps exactly VPP-01..04 to Phase 142; no additional requirement IDs are mapped to this phase. No orphans found. Plans 142-01 through 142-06 correctly declare `requirements: []` (centralised ticking design, stated in `ROADMAP.md`'s Phase 142 block and honored — verified no plan ticked early).

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|---|---|---|---|---|
| `test/native/avr/test_vpp_eprom_v131/test_vpp_eprom_v131.cpp` | 594 | `PLACEHOLDER` (grep hit) | INFO — false positive | Read in context: the comment documents the test-*authoring* method ("PLACEHOLDER -- overwritten with the measured literal before commit"); the actual assertions on the next two lines contain real measured literals (`1`, `0x20`), not a live stub. Not a defect. |

No `TBD`/`FIXME`/`XXX`/`TODO`/`HACK` debt markers found in any of the 12 files this phase touched. No empty-implementation or hardcoded-empty-data patterns found. The two expected-RED gates (`native_trace_v131`, MERGE-05) are deliberate, disclosed, operator-accepted non-goals of this phase (owned by Phase 144), not anti-patterns.

### Human Verification Required

None. Every truth this phase actually claims is verifiable at the source/native-test level and was independently re-derived above. The items the phase's own record explicitly declines to claim (0x08 silicon behavior, the drop-resistor's real output voltage, any timing claim, `command_done()`'s behavior on a genuine AVR abort) are correctly scoped to bench validation in the later **Phase 145: Bench Validation** — raising them here as "needs human testing" would incorrectly imply this phase failed to do something it never claimed to do.

### Gaps Summary

No gaps found. All four roadmap Success Criteria and all 17 consolidated truths (roadmap + plan-level) verified against the actual codebase: source read line-by-line for every touched function, all native/host test suites re-run independently with results matching the record byte-for-byte, all three AVR builds reproduced (cold-verified for `uno`), the D-18 one-commit property and golden blob-SHA pinning independently confirmed via `git rev-list`/`git rev-parse`, the VPP-04 gate's novelty independently confirmed via `git grep` against the pre-phase tree, and the meta-repo requirement-flip commit read in full to confirm a minimal, uncollateralized diff.

Two design decisions ("qualified SC1", "operation- vs. block-level SC2 success") deviate from a maximally-literal reading of `ROADMAP.md`'s Success-Criteria prose but are, on independent source-level investigation, correct, deliberate, tested, and consistent with real hardware constraints and an operator-confirmed amendment (C-1/D-10) — they are called out explicitly above for the record, not treated as failures.

Two REDs (`native_trace_v131`, `MERGE-05`) were independently reproduced and confirmed to be exactly the expected/disclosed non-goals this phase's own record describes (owned by Phase 144, not this phase) — reproducing them here as a check on the record's own honesty, not as phase-142 gaps.

One structural test-coverage decision was scrutinized on request (plan 142-06's unplanted "include/-wide composite-count" leg, Coverage 10): its assertion is a simple, non-vacuity-guarded, strict-equality regex count over a real filesystem glob (not a complex construct prone to silent vacuity), and the stated reason for not planting a violation (no third env seam exists by the module's own fixed two-seam contract; a transient edit to the real zero-headroom header was explicitly and reasonably avoided) holds up under inspection — accepted as reasonable, not a gap.

One additional adversarial check (not prompted by the record) was run to close a potential "error path with no test coverage": whether `eprom_internal_write_execute_body`'s `row==NULL` branch (which, unlike every other exit, does not set `RESPONSE_CODE_ERROR` and so would not trigger the wrapper's disable) is genuinely unreachable rather than merely asserted to be. Independently confirmed unreachable by construction: `EPROM_PARAM_KEYS = {0x07, 0x08, 0x0B}` in `eprom_params.cpp` exactly matches the protocol set `configure_memory` already restricts to before ever calling `configure_eprom` (documented in `firestarter/CLAUDE.md`'s dispatch order and confirmed passing in `test_dispatch`), so `eprom_params_for()` cannot return `NULL` for any protocol that legitimately reaches this function. No gap.

---

*Verified: 2026-08-12T02:19:32Z*
*Verifier: Claude (gsd-verifier)*
