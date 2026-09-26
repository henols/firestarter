---
phase: 141-per-byte-program-loop
verified: 2026-08-10T23:59:00Z
status: passed
score: 5/5 success criteria verified (8/8 LOOP requirements satisfied)
overrides_applied: 0
gaps: []
---

# Phase 141: Per-Byte Program Loop Verification Report

**Phase Goal:** Programming a 27C byte applies fixed-width pulses, counts them, verifies after each
one, and fails safely and informatively when a byte cannot be programmed within its budget —
replacing the block-level mismatch-mask retry loop end to end.

**Verified:** 2026-08-10
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths (ROADMAP Success Criteria)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | Fixed-width pulse, verify after each, per-byte count tracked; the four named legacy constructs no longer exist anywhere in the write path | VERIFIED | `src/proms/eprom.cpp:254-277` — `pulses`/`accumulated` locals, `org_delay` never mutated inside the loop, one `firestarter_set_data`+`firestarter_get_data` pair per iteration. Whole-tree grep: `program_mismatched_bytes`, `verify_and_update_mask`, `NUMBER_OF_RETRIES`, the `org + org*retries/20` growth formula and `mismatch_bitmask` are absent from `src/`/`include/` (only referenced in comments/frozen fixtures explaining the *old* behaviour). `test_write_path_source_contract_v131.py` (12 legs, all green) and `native_loop_v131`'s `test_loop01_*` (4 cases, all green) both assert this mechanically. |
| 2 | `overprogram_factor > 0` → one extra `3×N×pulse` pulse capped at `overprogram_cap_us`; `0x0B` caps accumulated time at 50 ms with no overprogram pulse | VERIFIED (pure-function + zero-live-row scope, honestly recorded) | `eprom_overprogram_us()` (`eprom.cpp:154-160`, declared `eprom.h:35`) implements the exact formula with the `factor==0`/cap-clamp/32-bit-safety behaviour, proven at 5 boundary points by `native_loop_v131`'s `test_loop03_*` (5/5 green, independently re-run). `0x0B`'s energy-cap loop exit is proven by `test_loop04_energy_cap_stops_at_exactly_{100,50,250}_pulses_at_{500,1000,200}us` (all green) and `test_loop04_no_live_row_emits_an_overprogram_pulse`. **Recorded non-claim, verified honest:** `overprogram_factor` is `0` on every shipped row (140-PARAM-TABLE-RECORD §§3-4), so `eprom_write_execute` itself is never driven with a nonzero factor — LOOP-RECORD §3 states this plainly as unproven-through-the-loop, not glossed as proven end-to-end. |
| 3 | A byte that fails to verify within `max_pulses` hard-fails the block — write aborts, every active HV route disables, failing address + pulse count reported | VERIFIED | `eprom_internal_report_budget_failure()` (`eprom.cpp:173-182`) clears `CTRL_VPP_REGULATOR_ENABLE` (the route's actual voltage source — the drop bit is a routing config bit that de-energizes with it) and packs a 4-byte `{addr_hi,addr_mid,addr_lo,pulse_count}` payload under `MSG_ERR_MAX_PULSES`/`MSG_ERR_ENERGY_CAP`. `test_loop05_a_byte_that_misses_within_max_pulses_aborts_the_block`, `test_loop05_the_loops_own_strobes_disable_the_high_voltage_route` (with an explicit vacuity trap + a paired negative control `test_loop05_a_successful_block_does_not_disable_the_route`) — all green. Firmware-level abort propagation (no further blocks processed) traced and confirmed against live source in `141-LOOP-RECORD.md` §4 (`_process_incoming_data` returns `false` immediately; `handle->address` never advances; `command_done()` fires). |
| 4 | `0xFF`/already-matching bytes never pulsed; any delay >16383 µs passes through the 32-bit-safe split helper, never a bare over-ceiling `delayMicroseconds()` | VERIFIED | `eprom.cpp:244-249` skips both cases before any pulse. `mem_util_split_delay`/`mem_util_delay_us` (`memory.cpp:202-222`) implemented and used at both D-06 sites (`memory.cpp:374` pulse, `eprom.cpp:405` erase pulse). Full-tree `delayMicroseconds(` inventory (9 call sites) confirmed: every remaining bare call takes a compile-time literal (`10`,`1`,`3`) or an already-clamped value (`settling`/`strobe`, capped at 1000UL; `rem`, guaranteed ≤16383 by the split helper) — zero unclamped over-ceiling call sites. `test_loop06_*` (4 cases) and `test_loop07_*` (7 cases across `native_loop_v131`) all green. |
| 5 | VPE asserted/settled once per block, survives per-byte verify read; DIP32 collision handled explicitly | VERIFIED | `eprom.cpp:189-198` asserts once, gated on `get_control_register(...)==0` (idempotent re-entry guard). `memory.cpp:163-200`'s `mem_util_calculate_top_address_register` unconditionally preserves `CTRL_VPE_ENABLE`/`CTRL_VPP_P1_ENABLE`/`CTRL_VPP_A9_ENABLE`/`CTRL_VPP_REGULATOR_ENABLE` across every address write (survives the verify read). DIP32: explicit `if (handle->pins >= 32) { ...drop_enable, 0); }` at `eprom.cpp:217-219`, keyed on `handle->pins` (never `protocol`, confirmed not a 4th tier-1 site by the D-13 gate). `test_loop08_*` (6 cases incl. a real A16-boundary crossing with a paired negative control on the 28-pin row) all green. `CTRL_ADDRESS_LINE_16`(0x01)/`CTRL_VPP_VPE_DROP_ENABLE`(0x100) confirmed as genuinely distinct bits under the shipped `-D HARDWARE_REVISION` build (`include/rurp_pinout.h:88,96`), matching the corrected (non-collision) mechanism the phase record names. |

**Score:** 5/5 success criteria verified.

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|---|---|---|---|---|
| LOOP-01 | 141-09 (centralized; evidence from 141-04/07) | Fixed-width pulses, verified per pulse, counted | SATISFIED | See Truth 1 |
| LOOP-02 | 141-09 (evidence from 141-04/06) | Four named legacy constructs removed | SATISFIED | See Truth 1; `test_write_path_source_contract_v131.py` 12/12 green |
| LOOP-03 | 141-09 (evidence from 141-04/08) | Overprogram pulse formula + cap | SATISFIED (pure-function scope, honestly recorded) | See Truth 2 |
| LOOP-04 | 141-09 (evidence from 141-04/07) | `0x0B` accumulated-time cap, no overprogram | SATISFIED | See Truth 2 |
| LOOP-05 | 141-09 (evidence from 141-04/08) | Hard-fail, disable, report address+count | SATISFIED | See Truth 3 |
| LOOP-06 | 141-09 (evidence from 141-04/07) | Skip `0xFF`/matching bytes, no pulse | SATISFIED (pulse-skip universal; read-skip correctly scoped to `0x0B` in the record, F-141-08) | See Truth 4; §7 of `141-LOOP-RECORD.md` |
| LOOP-07 | 141-09 (evidence from 141-02/06/08) | Safe 32-bit delay helper, no bare over-ceiling call | SATISFIED | See Truth 4 |
| LOOP-08 | 141-09 (evidence from 141-02/04/08) | VPE once per block, DIP32 explicit path | SATISFIED | See Truth 5 |

All eight requirement IDs cross-reference cleanly against `.planning/REQUIREMENTS.md` (lines 183-201), which marks all eight `[x]` Complete and maps all eight to Phase 141 with status "Complete" in the coverage table (lines 309-316). No orphaned requirements: plans 141-01…08 correctly declare `requirements: []` (by design, per the phase's centralized-ticking convention stated in ROADMAP.md and `141-09-PLAN.md`'s own "Requirement ownership" note), and 141-09 is the sole plan declaring all eight IDs, ticking them only after every plan's evidence exists. `TABLE-05` (the D-13 gate's underlying requirement) belongs to, and is already marked Complete under, Phase 140 — not orphaned here.

### Required Artifacts

| Artifact | Expected | Status | Details |
|---|---|---|---|
| `firestarter/src/proms/eprom.cpp` | Per-byte pulse→verify loop, pre-flight refusals, budget-failure reporter, DIP32 branch | VERIFIED | Read in full; matches all five success criteria (see Truths 1-5) |
| `firestarter/include/eprom.h` | `eprom_overprogram_us` declaration | VERIFIED | Present, documented, matches implementation signature |
| `firestarter/src/proms/memory.cpp` | `mem_util_split_delay`/`mem_util_delay_us`, DIP32 preserve-mask fix | VERIFIED | Present at `:198-218`; preserve mask at `:163-196` matches D-09's corrected mechanism |
| `firestarter/include/memory_utils.h` | Delay helper declarations | VERIFIED | Present, documented with the 16383 µs ceiling rationale |
| `firestarter/test/native/avr/test_loop_eprom_v131/` | `native_loop_v131`'s own suite (D-10) | VERIFIED | 39/39 passing, independently re-run; non-vacuous (negative controls present) |
| `firestarter/tests/golden/protocol_branch_inventory.json` | Re-derived D-13 golden | VERIFIED | Re-run gate green (7/7); blob SHA `b36d3c4c7c854c1d8b24ab262b1319f7111f11cf` matches `git rev-parse HEAD:src/proms/eprom.cpp` exactly; tier counts (3 tier-1 / 24 "other") match the record's claimed 3/24 split |
| `tools/catalog/messages.toml` + generated `messages.h`/`messages.py` | Three new message IDs, tri-repo synced | VERIFIED | `MSG_ERR_PULSE_TOO_WIDE`(0xAE)/`MSG_ERR_MAX_PULSES`(0xBD)/`MSG_ERR_ENERGY_CAP`(0xBE) present and identical across meta catalog, firmware header, host `messages.py` |
| `.planning/phases/141-per-byte-program-loop/141-LOOP-RECORD.md` | Phase close record | VERIFIED | 40KB, substantive, self-correcting (names its own must_have wording error re: the determinism leg, §10.1) |
| `.planning/phases/141-per-byte-program-loop/141-NEW-TRACE.md` | Post-change trace artifact | VERIFIED | Contains exact reproducible commands + banners; independently re-run and matched byte-for-byte (91/119/59) |
| `.planning/phases/141-per-byte-program-loop/141-PREDICTIONS.md` | Pre-registered flash/RAM/D-13 predictions | VERIFIED | Committed at `4c5d9172` (14:43:00), strictly before the first `eprom.cpp` change (`aeac4e7`, 16:13:38) — ordering requirement satisfied |

### Key Link Verification

| From | To | Via | Status | Details |
|---|---|---|---|---|
| `configure_eprom` | `eprom_params_for(handle->protocol)` | table read + D-03/D-05 refusals | WIRED | `eprom.cpp:85-110`; row NULL and energy-cap-exceeded both fail closed before any HV touch |
| `eprom_write_execute` | `eprom_internal_report_budget_failure` | two budget-exhaustion exits | WIRED | `eprom.cpp:267,274`; both exits proven distinct by native tests asserting the correct message ID at each |
| `eprom_write_execute` | `eprom_overprogram_us` | post-convergence overprogram gate | WIRED (pure-function only, per LOOP-03's recorded scope) | `eprom.cpp:284-289`; inert on every shipped row, by design |
| `memory_set_data` / erase pulse | `mem_util_delay_us` | both D-06 sites | WIRED | `memory.cpp:374`, `eprom.cpp:405` — both confirmed via direct read, not just grep |
| `mem_util_calculate_top_address_register` | DIP32 preserve-mask exclusion | `pins < 32` guard | WIRED | `memory.cpp:172-189`; corrected comment matches H1's stated (non-collision) mechanism |

### Behavioral Spot-Checks / Gate Re-Runs (independently executed by this verifier)

| Check | Command | Result | Status |
|---|---|---|---|
| Legacy constructs absent | `grep -rn "program_mismatched_bytes\|verify_and_update_mask\|NUMBER_OF_RETRIES\|mismatch_bitmask" src/ include/` | zero hits outside comments/frozen fixtures | PASS |
| Firmware pytest | `python3 -m pytest tests/ -q -o addopts=""` | 256 passed | PASS (matches stated baseline exactly) |
| `native_loop_v131` | `pio test -e native_loop_v131` | 39/39 succeeded | PASS (matches baseline exactly) |
| `native` / `native_nodevtools` | `pio test -e native` / `-e native_nodevtools` | 141/17 each, all passed | PASS (matches baseline exactly) |
| `native_params_v131` | `pio test -e native_params_v131` | 9/9 succeeded | PASS (matches baseline exactly) |
| `native_trace_v131` (expected RED) | `pio test -e native_trace_v131` | 3 failed/2 succeeded, exact expected/observed values (198/221/201 vs 91/119/59) | EXPECTED RED — matches D-10 exactly, not a gap |
| D-13 golden gate | `pytest tests/test_protocol_branch_inventory.py` | 7 passed | PASS; blob SHA verified against live `git rev-parse` |
| `test_write_path_source_contract_v131.py` | `pytest tests/test_write_path_source_contract_v131.py` | 12 passed | PASS (matches the 12-leg gate the record describes) |
| MERGE-05 policy (expected RED) | `check_size_baseline.py --policy merge05` against a cold `pio run` on all three AVR targets | FAIL exactly as recorded: uno +492, uno328pb +498, leonardo +328 vs the 64/64/0 B band | EXPECTED RED — matches F-141-01 exactly, not a gap |
| Cold AVR flash/RAM | cold `pio run -e uno\|uno328pb\|leonardo` (verified with `rm -rf .pio/build/<env>` first) | 24424/24474/26400 B flash, 1573/1579/2014 B RAM | PASS (byte-identical to the stated baseline) |
| `check_build_warnings.py --rebuild` (cold on native) | after `rm -rf .pio/build/native{,_nodevtools}` | exact-zero macro-redefinition on all AVR; native/native_nodevtools both = 1166 (exactly at watermark) | PASS — confirms "zero headroom" claim precisely; a warm-cache first attempt returned 998 (INFO, not FAIL), consistent with the documented warm/cold asymmetry in `size_baseline.json`'s own note |
| Host app pytest | `python3 -m pytest tests/ -q -o addopts=""` (firestarter_app) | 1547 passed | PASS (matches stated baseline exactly) |

### Anti-Patterns Found

None. Scanned all files this phase modified (`eprom.cpp`, `eprom.h`, `memory.cpp`, `memory_utils.h`, the new `native_loop_v131`/`native_trace_v131` test suites, `test_write_path_source_contract_v131.py`, `test_protocol_branch_inventory.py`) for `TBD`/`FIXME`/`XXX`/`TODO`/`HACK`/`PLACEHOLDER`, empty implementations, and `TEST_IGNORE`/skip patterns. Zero hits. No debt markers found anywhere in this phase's own code.

### Human Verification Required

None. This phase's success criteria are all statically/behaviorally verifiable via native tests and AVR compilation — no live-hardware claim is made or required by this phase (that is Phase 145 / Bench Validation's scope, explicitly deferred). No plan in this phase carries a deferred `<human-check>` block.

### Two Deliberate REDs — Confirmed Exactly As Documented, Not Gaps

1. **`native_trace_v131`** — 3 failed / 2 succeeded, identical failure shape (stream-length equality at `test_trace_eprom_v131.cpp:176`, observed 91/119/59 vs frozen 198/221/201) independently reproduced by this verifier. D-10/Phase 144-TEST-06 owns the re-freeze. Confirmed no more and no fewer failures than documented.
2. **MERGE-05 flash-band policy** — RED on all three AVR targets, independently reproduced with cold builds and the exact same deltas (+492/+498/+328 B against a 64/64/0 B band). Operator decision ("Continue; 141-09 records it") is recorded faithfully in `141-LOOP-RECORD.md` §1, with RAM confirmed exact-zero delta on all three targets (independently re-measured). `F-141-01` in the findings register correctly attributes this to the operator and does not soften the RED.

### Gaps Summary

No gaps found. Every roadmap success criterion is independently verified against the live codebase (not merely against SUMMARY.md claims): the rewritten `eprom_write_execute` loop, the pure `eprom_overprogram_us` function, the budget-failure reporter, the DIP32 branch, and the 32-bit-safe delay helper were all read directly and their behavior cross-checked against 39 independently-re-run native test cases plus 256 firmware pytest cases plus 1547 host pytest cases — all passing at exactly the counts the phase record claims. The two intentionally-RED gates were independently reproduced with byte-identical failure numerics to what the record and the phase's own predecessor findings state, confirming neither is a hidden additional regression. The phase's own self-corrections (LOOP-RECORD §7's scoped LOOP-06 read-skip claim, §10.1's correction of its own "still passing" must_have wording, §9's arithmetic correction) were independently checked against source/tests and found accurate rather than glossed. Requirement traceability is clean: all eight LOOP-* IDs are satisfied, ticked in one hand-edit by the designated plan, and no requirement is orphaned.

---

*Verified: 2026-08-10*
*Verifier: Claude (gsd-verifier)*
