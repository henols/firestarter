---
phase: 141-per-byte-program-loop
plan: 04
subsystem: firmware
tags: [avr, platformio, eprom, embedded-c, progmem, firestarter]

# Dependency graph
requires:
  - phase: 140-parameter-table
    provides: eprom_params_for() PROGMEM table (overprogram_cap_us, energy_cap_us, max_pulses, overprogram_factor, verify_mode, vpp_path), keyed on protocol_id
  - phase: 141-per-byte-program-loop (141-01)
    provides: MSG_ERR_PULSE_TOO_WIDE / MSG_ERR_MAX_PULSES / MSG_ERR_ENERGY_CAP message ids, 141-PREDICTIONS.md
  - phase: 141-per-byte-program-loop (141-02)
    provides: mem_util_delay_us / mem_util_split_delay 32-bit-safe delay helper, already wired into memory_set_data
provides:
  - The per-byte fixed-width pulse-to-verify write loop (LOOP-01, LOOP-04, LOOP-05, LOOP-06, LOOP-08 implementations)
  - configure_eprom pre-flight refusals for an unrecognised protocol and an over-cap pulse (D-03, D-05)
  - eprom_overprogram_us pure arithmetic function (LOOP-03/D-08 oracle)
  - eprom_internal_report_budget_failure single budget-failure reporter (LOOP-05/D-04)
  - The erase pulse routed through mem_util_delay_us, completing LOOP-07's two-site inventory
affects: [141-05, 141-06, 141-07, 141-08, 141-09, 142-vpp-routing, 144-trace-and-baseline-reconciliation]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Per-byte pulse-to-verify loop: skip-check read, then fixed-width pulse + verify, budgets checked only after a failed verify"
    - "Hoist-all-PROGMEM-reads-once-per-block, never inside the per-byte loop"
    - "Single shared failure reporter for a class of exit (disable route, pack payload, emit, set response_code) rather than duplicating the sequence per call site"

key-files:
  created: []
  modified:
    - firestarter/include/eprom.h
    - firestarter/src/proms/eprom.cpp

key-decisions:
  - "Implemented D-01..D-09 exactly as specified in 141-CONTEXT.md; no new decisions required at execution time"
  - "verify_mode is CONSUMED (plan's own pre-decided disposition): 0x07/0x08 run one final full-block verify pass after the byte loop; 0x0B does not"
  - "eprom_overprogram_us(.... cap_us=0) yields 0 without a special case, since a positive product always compares greater than a zero cap (plan's own pre-decided disposition)"
  - "Followed PLAN.md's literal Task 3 ordering (VPE-assert -> D-09 branch -> row lookup/hoist) even though 141-RESEARCH.md's earlier pseudocode suggested the row lookup first; PLAN.md is the checker-reviewed, authoritative document for this plan"

requirements-completed: []  # Frontmatter requirements: [] is deliberate -- this plan lands LOOP-01..08's implementation but completes none of them. Plan 141-09 owns the flip.

duration: 40min
completed: 2026-08-10
status: complete
---

# Phase 141 Plan 04: Per-Byte Program Loop Rewrite Summary

**Replaced `eprom_write_execute`'s block-level mismatch-mask retry loop with a per-byte fixed-width pulse-to-verify loop driven by Phase 140's `eprom_params_for()` table, added D-03's pre-flight refusal to `configure_eprom`, and rerouted the erase pulse through `mem_util_delay_us`.**

## Performance

- **Duration:** 40 min
- **Started:** 2026-08-10T15:55:00Z (approx.)
- **Completed:** 2026-08-10T16:35:38Z
- **Tasks:** 3
- **Files modified:** 2 (`firestarter/include/eprom.h`, `firestarter/src/proms/eprom.cpp`)

## Accomplishments

- `eprom_write_execute` is now a per-byte fixed-width pulse-to-verify loop: `0xFF` and already-matching bytes are skipped before any pulse; a byte pulses at a fixed width (never grown) until it verifies or a budget trips; both budgets (`max_pulses`, `energy_cap_us`) are checked only after a failed verify so a byte converging on its last permitted pulse succeeds.
- `program_mismatched_bytes`, `verify_and_update_mask`, `NUMBER_OF_RETRIES`, the flat block-retry loop, and the adaptive pulse-width growth formula are gone from `src/proms/eprom.cpp` entirely (confirmed by grep — zero occurrences of any of the six removed identifiers).
- Both budget failures funnel through one new reporter, `eprom_internal_report_budget_failure`, which disables `CTRL_VPP_REGULATOR_ENABLE`, packs a 4-byte `{u24 address, u8 pulse_count}` payload matching the catalog's `MSG_ERR_MAX_PULSES` / `MSG_ERR_ENERGY_CAP` shape, and sets `RESPONSE_CODE_ERROR`.
- `configure_eprom` now fails closed, before any hardware is touched, on an unrecognised protocol (`eprom_params_for() == NULL` -> `MSG_ERR_PROTOCOL_NOT_IMPLEMENTED`) and on a pulse wider than the row's energy cap (`MSG_ERR_PULSE_TOO_WIDE`, guarded on `energy_cap_us > 0` since `0` means uncapped).
- `eprom_overprogram_us(pulse_count, pulse_us, factor, cap_us)` is a new pure function (declared in `eprom.h` for direct native testing), verified by hand-trace and by a mirrored Python simulation against all six of the plan's worked cases (300 / 75000 / 75000 / 75000 / 0 / 0 — see "Arithmetic verification" below).
- The 32-pin DIP32 case is an explicit, commented branch keyed on `handle->pins >= 32` (never `protocol`) that clears `CTRL_VPP_VPE_DROP_ENABLE`, matching D-09.
- The once-per-block VPE-assert/settle block and the tier-1 `handle->protocol == 0x0B || is_flag_set(FLAG_VPE_AS_VPP)` predicate survive **verbatim** inside `eprom_write_execute` — only their line number moved. Tier-1 protocol-keyed sites remain exactly 3 (confirmed by the D-13 scanner, see below).
- `verify_mode` is consumed: `0x07`/`0x08` (`VERIFY_PER_PULSE_PLUS_FINAL`) run one additional full-block read-and-compare pass after the byte loop, mirroring `memory_verify_execute`'s `MSG_ERR_VERIFY` 5-byte payload exactly; `0x0B` (`VERIFY_PER_PULSE`) does not.
- The erase pulse in `eprom_internal_erase` now routes through `mem_util_delay_us(handle->pulse_delay)` instead of a bare `delayMicroseconds(handle->pulse_delay)`, completing LOOP-07's two-site inventory (`memory.cpp`'s pulse site was already fixed by plan 141-02). `grep -n delayMicroseconds src/proms/eprom.cpp` now returns **zero** matches anywhere in the file.
- Every `row->` field access (7 occurrences total) is wrapped in `pgm_read_byte`/`pgm_read_dword` — none is a direct dereference.

## Task Commits

1. **Task 1: Contracts — pure overprogram function, shared failure reporter, erase-pulse reroute** - `aeac4e7` (feat)
2. **Task 2: configure_eprom pre-flight refusals** - `ef0e075` (feat)
3. **Task 3: Rewrite eprom_write_execute as the per-byte pulse-to-verify loop** - `3504e50` (feat)

All three commits are inside the `firestarter` submodule, on branch `gsd/v1.31-27c-programming-algorithm-fidelity` (verified before each commit).

**Plan metadata:** committed separately in the meta repo (this SUMMARY + STATE.md/ROADMAP.md).

## Files Created/Modified

- `firestarter/include/eprom.h` - declares `eprom_overprogram_us` (extern "C", commented with D-08's rationale and both decided semantics)
- `firestarter/src/proms/eprom.cpp` - the whole write path: `configure_eprom`'s two refusals, `eprom_overprogram_us`'s implementation, the new `eprom_internal_report_budget_failure`, the rewritten `eprom_write_execute`, and the erase-pulse reroute

## Decisions Made

None new — this plan's `<objective>` names D-01 through D-09 by number and both of the plan's own pre-decided dispositions (`verify_mode` consumed; `cap_us == 0` yields 0), and execution followed all of them exactly as specified. The one execution-time judgment call was about *which source document to follow* when two disagreed (see Deviations).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking, verification-only] Task 3's own automated verify script has a locator bug**

- **Found during:** Task 3 verification
- **Issue:** The plan's Task 3 `<automated>` verify script computes `w = t[t.index('void eprom_write_execute'):]` to isolate the function body for its assertions. `t.index(...)` returns the **first** match, which is the forward declaration at the top of the file (`void eprom_write_execute(firestarter_handle_t* handle);`, ends in `;`), not the actual definition. The subsequent `w[:w.index('void eprom_check_vpp')]` then also matches `eprom_check_vpp`'s own forward declaration a few lines later, so `w` collapses to a ~6-line slice of forward declarations containing none of the real function body. Run literally, the script fails its very first content assertion (`'handle->protocol == 0x0B' in w`) against a **correct** implementation, because it isn't actually looking at the function.
- **Fix:** Re-ran the identical assertion set with the locator corrected to anchor on the definition's signature including the opening brace (`t.index('void eprom_write_execute(firestarter_handle_t* handle) {')`), per this project's own "fix the locator, not the assertion" convention (D-15). All assertions then pass. No plan file, test file, or source file was modified to work around this — only my own ad-hoc verification command.
- **Files modified:** None (verification-only; no committed file changed)
- **Verification:** Re-ran the corrected script; all listed assertions passed. Independently cross-checked the specific properties by direct `grep`: `handle->protocol == 0x08` absent from the whole file; `handle->pulse_delay =` appears exactly twice inside `eprom_write_execute`; `handle->pins >= 32` appears once as code; all 7 `row->` accesses are `pgm_read_*`-wrapped.
- **Committed in:** N/A (no code change resulted)
- **Flag for downstream plans:** if any of plans 141-05 through 141-09 write a similar `t.index('void <fn>')`-based locator against `eprom.cpp` (which now has more forward declarations above more functions than before), the same bug class can recur. Worth a locator that anchors on `(firestarter_handle_t* handle) {` rather than the bare function name.

---

**Total deviations:** 1, verification-tooling-only (no source, test, or plan file changed as a result)
**Impact on plan:** None on the shipped code. The locator bug affects only how *I* confirmed the acceptance criteria this session; the underlying properties were all independently re-verified by direct grep/read as well.

## Arithmetic verification (Task 1 acceptance criteria)

Hand-traced against the implementation and cross-checked with a mirrored Python simulation (both methods agree):

| Inputs `(pulse_count, pulse_us, factor, cap_us)` | Expected | Got |
|---|---|---|
| `(1, 100, 3, 75000)` | 300 | 300 |
| `(25, 1000, 3, 75000)` | 75000 | 75000 |
| `(25, 1001, 3, 75000)` | 75000 | 75000 |
| `(25, 65535, 3, 75000)` | 75000 | 75000 |
| `(5, 100, 0, 75000)` | 0 | 0 |
| `(5, 100, 3, 0)` | 0 | 0 |

Energy-cap predicate (D-01's worked example, `energy_cap_us = 50000`), simulated with the exact `pulses++; accumulated += width; if (energy_cap_us && accumulated >= energy_cap_us)` shape:

| Pulse width | Pulses | Accumulated | Expected pulses |
|---|---|---|---|
| 200 us | 250 | 50000 | 250 |
| 500 us | 100 | 50000 | 100 |
| 1000 us | 50 | 50000 | 50 |

## Verification results

- `pio run -e uno / uno328pb / leonardo`: all SUCCESS, zero compiler warnings at the final (Task 3) commit.
- `pio test -e native` and `-e native_nodevtools`: **141 cases / 17 suites**, unchanged, on both.
- `pio test -e native_loop_v131`: **6/6** passing (141-03's harness self-checks; none drive `eprom_write_execute` yet, so they were unaffected by this plan and remained green throughout).
- `pio test -e native_params_v131`: **9/9** passing.
- `python3 -m pytest tests/ -q -o addopts="" --ignore=tests/test_protocol_branch_inventory.py`: **237 passed**, including `test_golden_trace_identity_eprom_v131.py`, `test_eprom_params_citations.py`, and `test_check_cmake_manifest.py` (proving no frozen fixture moved, no table value moved, no new `src/` translation unit was added).
- **Known gate hazard confirmed exactly as flagged:** `tests/test_flash_path_record_sync.py::test_planted_mutation_of_the_real_subset_is_detected` failed once, transiently, on an uncommitted mid-change diff (unscoped `git status --porcelain` check). Resolved by committing before re-running the broad suite, per the carried-forward guidance; not a real regression.

## D-13 inventory movement (for plan 141-05 — RED as designed, D-11)

`python3 -m pytest tests/test_protocol_branch_inventory.py -q -o addopts=""` fails on **exactly the three predicted tests**, no others:

- `test_blob_shas_match_the_recorded_inventory` — `src/proms/eprom.cpp` blob SHA changed (recorded `8dfa4cc…`, observed `37f0a04…`), as it must.
- `test_branch_sites_match_the_recorded_inventory` — first divergence at index 0 (every line number below the file's edits shifted).
- `test_exactly_three_protocol_keyed_sites_at_the_pinned_lines` — found `[70, 190, 340]` against the pinned `[71, 145, 218]`.

The other 4 of the 7 tests in that module (`test_inventory_is_non_vacuous`, `test_params_table_has_no_second_selector`, `test_default_targets_resolve_inside_this_repository`, `test_git_is_required_not_optional`) still pass.

**Live inventory, extracted via the module's own `_extract_predicates` (the sanctioned re-derivation path, run but not written back):**

- **Before (recorded golden):** 24 total = 3 tier-1 (lines 71, 145, 218) + 21 tier-2.
- **After (live, this commit):** **27 total = 3 tier-1 (lines 70, 190, 340) + 24 tier-2.** Tier-1 predicate text is byte-identical at each site, only the line number moved. No fourth tier-1 site exists.
- **Tier-2 sites removed (3, exactly as 141-PREDICTIONS.md's P3 predicted):** the two loop bounds and the verify-comparison inside the now-deleted `program_mismatched_bytes`/`verify_and_update_mask`.
- **Tier-2 sites added (6 — lower than P3's point-estimate of 12; see divergence note below):**
  - `106`: `if (energy_cap_us > 0 && handle->pulse_delay > energy_cap_us)` (D-03's refusal, keyed on `pulse_delay`)
  - `217`: `if (handle->pins >= 32)` (D-09's branch)
  - `237`: `i < handle->data_size` (the byte-loop bound)
  - `247`: `if (handle->firestarter_get_data(handle, addr) == expected)` (LOOP-06's already-matching skip)
  - `260`: `if (handle->firestarter_get_data(handle, addr) == expected)` (the pulse-verify loop's convergence check — same predicate text as 247, a distinct site)
  - `297`: `i < handle->data_size` (the final full-block verify pass's loop bound)
- **Net: tier-2 grows 21 -> 24 (+3), tier-1 stays 3.** P3's core claim ("tier-2 grows, it does not shrink") is confirmed; only its point-estimate magnitude (+9, for a predicted total of 33) was too high.
- **Divergence from the P3 prediction, explained:** of the 12 new predicates P3 enumerated, only 6 are textually visible to `_extract_predicates`'s `_is_relevant` filter (`"handle->" in span_text`, or one of three named helper calls). The other 6 — `expected == 0xFF`, `pulses >= max_pulses`, `energy_cap_us && accumulated >= energy_cap_us`, `row == NULL` (both occurrences, in `configure_eprom` *and* `eprom_write_execute`), `if (op_us)`, `verify_mode == VERIFY_PER_PULSE_PLUS_FINAL`, and `byte != expected` in the final pass — all operate on **local variables hoisted from `handle->`/table fields one statement earlier**, so the condition's own text contains no `handle->` substring and the scanner (a text scanner, not a data-flow analyzer) does not count them, even though they are real branches keyed on handle-derived data. This is a structural property of the extractor's heuristic, not a bug in my code or a defect in the extractor for its stated purpose (catching a *second protocol-keyed dispatch axis*, which does not care about tier-2 undercounting).
- **Full live inventory dump** (all 27 sites, line/tier/keyed_on/predicate) was captured this session and is available in the executor's tool transcript for 141-05 to cross-reference; re-deriving the golden from `_extract_predicates` directly (as D-11 mandates) will reproduce it exactly.

## native_trace_v131 (for Phase 144 / TEST-06 — RED as designed, D-10)

`pio test -e native_trace_v131` **compiles cleanly** (only the pre-existing, unrelated 14 macro-redefinition warnings from pairing `<Arduino.h>` with `<ArduinoFake.h>` in a test TU) and reports:

| Case | Result |
|---|---|
| `test_smoke_setup_leaves_both_recorders_clean` | PASSED |
| `test_smoke_timing_hook_fires_for_delay_and_delaymicroseconds` | PASSED |
| `test_protocol_0x07_am27c512_capture_is_sound_and_deterministic` | **FAILED** — stream length: expected 198, was 91 |
| `test_protocol_0x08_am27c020_capture_is_sound_and_deterministic` | **FAILED** — stream length: expected 221, was 119 |
| `test_protocol_0x0B_am2716_capture_is_sound_and_deterministic` | **FAILED** — stream length: expected 201, was 59 |

All three failures originate inside the shared `v131_assert_stream_equals` helper's length-equality assertion (the first sub-check of "the ordered positional comparison" named in the plan's acceptance criteria) — exactly the predicted failure mode: the new loop's skip logic (0xFF bytes, already-matching bytes) and its removal of the flat multi-pass retry loop produce a much shorter merged strobe+timing stream than the frozen pre-change capture. `RESPONSE_CODE_OK` is confirmed reached in every case (it is asserted immediately before the length check inside the same helper, and the helper's abort happens strictly after it).

**Determinism finding, stated precisely rather than glossed over:** the helper's own intra-process "drive twice, compare positionally" determinism check (lines 308-320 of `test_trace_eprom_v131.cpp`) is **structurally unreached** in this run for all three protocol cases — Unity's `TEST_ASSERT_EQUAL_MESSAGE`/`TEST_FAIL_MESSAGE` perform a `longjmp` abort on the first failure, which happens at the length check, strictly *before* the second `drive_v131_write()` call in the same function. This is not a failure of determinism; it is simply never executed. Independent evidence that the new cadence is nonetheless deterministic: running `pio test -e native_trace_v131` twice, as two fully independent process invocations, produced byte-identical recorded lengths (91/119/59) both times. Combined with a source read confirming `eprom_write_execute` has no `static` locals, no RNG, and no time-dependent branching, this is strong (though not the exact intra-process form the helper itself checks) evidence against a non-reproducible cadence. Flagging for whoever next touches this suite (141-09 or Phase 144/TEST-06): the determinism section's unreachability once the primary assertion fails is a pre-existing structural property of `assert_v131_protocol_case`'s ordering, not something this plan introduced or is in scope to fix (touching `_shared/eprom_v131_expected.h` or the trace test files is explicitly out of scope here).

No frozen fixture was touched: `_shared/eprom_v131_expected.h` is unmodified (confirmed — this plan's `git diff` touches only the two declared files).

## Flash / RAM measurement vs 141-PREDICTIONS.md

**RAM: exactly 0 delta on all three AVR targets — P2's prediction confirmed exactly.**

| Target | RAM before | RAM after | Delta |
|---|---|---|---|
| uno | 1573 B | 1573 B | 0 |
| uno328pb | 1579 B | 1579 B | 0 |
| leonardo | 2014 B | 2014 B | 0 |

**Flash: measured per-task, and cumulatively, against this plan's own immediate pre-plan baseline** (given at execution start: uno 24002 B, uno328pb 24052 B, leonardo 26064 B — independently re-confirmed by building the exact pre-141-04 commit, `6029423`, in a throwaway worktree):

| Target | Pre-plan | After Task 1 | After Task 2 | After Task 3 (final) | **Total delta** |
|---|---|---|---|---|---|
| uno | 24002 | 24024 (+22) | 24220 (+196) | 24424 (+204) | **+422** |
| uno328pb | 24052 | 24074 (+22) | 24270 (+196) | 24474 (+204) | **+422** |
| leonardo | 26064 | 26086 (+22) | 26280 (+194) | 26400 (+120) | **+336** |

**This substantially exceeds 141-PREDICTIONS.md's P1 point-estimate (+30 B / +30 B / +18 B).** Measured against that document's own "live tip" reference point (uno 23954, uno328pb 24004, leonardo 26016 — captured mid-way through plan 141-01, *before* plan 141-02's delay-helper addition and this plan's own changes), the true deltas are **+470 / +470 / +384 B** — roughly 15-20x the point estimate, and beyond even the wide worst-case range 141-PREDICTIONS.md's own ingredient ledger acknowledged as plausible (recomputed from that ledger's own high-adds/low-removes extremes: approximately +274 B).

**Grounded, symbol-level breakdown** (via `avr-nm --print-size`, comparing the pre-141-04 commit's linked ELF against this plan's final ELF; LTO is active in this build — confirmed by `__gnu_lto_slim`/`__gnu_lto_v1` markers in every `.o`, which is *why* `eprom_overprogram_us`, `eprom_params_for`, and `configure_eprom` do not appear as separate linked symbols in either build: all three are small enough, and now have few enough call sites, for the link-time optimizer to inline them into their callers):

- `eprom_write_execute` itself: 898 B -> 1006 B, **+108 B** — modest growth given the function now does meaningfully more (skip-checks, dual budget tracking, the DIP32 branch, the overprogram gate, the final-pass loop) than the old block loop plus its two now-deleted helper functions (both of which LTO had already inlined into the old `eprom_write_execute`, making this an apples-to-apples comparison).
- `eprom_internal_report_budget_failure` (new, standalone — kept separate by LTO because it has two call sites): **+110 B**.
- `configure_memory` (the dispatcher `configure_eprom` is inlined into, since `configure_eprom` itself has exactly one call site): 864 B -> 1020 B, **+156 B** — this is where `configure_eprom`'s two new refusals land once inlined, *and* it is the first place `eprom_params_for()`'s own linear-scan body becomes linked at all (previously fully `--gc-sections`-collected per Phase 140 F-140-02), so this single number captures both costs together.
- Remainder (**+422 - 108 - 110 - 156 = +48 B**): consistent with `EPROM_PARAMS[]` (36 B) + `EPROM_PARAM_KEYS[]` (3 B) PROGMEM data becoming genuinely linked for the first time, plus alignment/padding.

**Why the point-estimate undershot, as best as this evidence supports:** the prediction's ingredient ledger budgeted roughly 70-80 B combined for "the accessor body" and "six hoisted PROGMEM reads," but the measured first-live-reference cost (the `configure_memory` delta, +156 B) is nearly double that alone, before the per-byte loop's own growth or the new reporter are even counted. The retry-loop-removal's reclaim also plausibly landed toward the *low* end of the ledger's own acknowledged range (the named uncertainty about a shared, already-linked `libgcc` multiply/divide routine).

**Not reconciled here, by design:** 141-PREDICTIONS.md itself states plan 141-09 is where predicted-vs-measured is formally paired, and Phase 144 / TEST-08 is where the full 138-143 cross-phase flash/RAM delta is reconciled. This section provides the accurate measured numbers and a grounded explanation for the divergence; it does not attempt to make the numbers match by altering the implementation, and no task's own `<verify>` block in this plan invokes `check_size_baseline.py` or enforces a MERGE-05 budget — that policy check is confirmed absent from this plan's actual gates. **Flagging explicitly for 141-09/Phase 144:** the cumulative delta from BASE-01 (uno 23932, uno328pb 23976, leonardo 26072) through this plan is now uno +492 B, uno328pb +498 B, leonardo +328 B — all three well beyond the `MERGE05_UNO_CLASS_FLASH_BAND = 64` B policy band 141-PREDICTIONS.md described (and leonardo's separate "must not grow" rule). Of that, roughly +70 B predates this plan (Phase 140 +22 B, plan 141-02 +48 B, both already spent before this plan started), and this plan itself contributed the remaining ~+422 B (uno/uno328pb) / +336 B (leonardo).

## Issues Encountered

None beyond the verify-script locator bug documented under Deviations, and the known, pre-flagged `test_flash_path_record_sync.py` git-porcelain false-positive (resolved by commit ordering, as anticipated).

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- **Ready for plan 141-05** (D-13 golden re-derivation): the live inventory (27 sites: 3 tier-1 at `[70, 190, 340]`, 24 tier-2) is fully captured above; the one hard-coded assertion literal (`test_protocol_branch_inventory.py:446`'s `[71, 145, 218]`) needs updating to `[70, 190, 340]` alongside the golden JSON re-derivation.
- **Ready for plan 141-06** (source contract): `eprom_internal_report_budget_failure`, `eprom_overprogram_us`, and the hoisted six-column read pattern are all in place and named exactly as the phase's `<artifacts_this_phase_produces>` predicted.
- **Ready for plans 141-07/141-08** (native behavior cases): `eprom_write_execute` is fully rewritten; the existing `test_loop_eprom_v131.cpp` harness (`drive_loop_write`, `make_loop_handle`, the three `LOOP_BUS_CONFIG_*` literals, the readback/logged-id recorders) needs no changes to start driving it.
- **Blocker/concern for plan 141-09** (measurement): the flash-delta divergence documented above is real and should be paired against 141-PREDICTIONS.md explicitly, not silently absorbed. RAM is clean (exact 0 delta, as predicted). The D-13 inventory divergence (27 vs. predicted 33) is explained and not a concern — tier-1 stayed at exactly 3, which is D-13's actual invariant.
- **Handed to Phase 142** (unchanged by this plan, as required): the duplicated VPP-route predicate at (now) lines 190/340, the DIP32 route choice, and generalizing the budget-failure reporter's route-disable to every exit.
- **Handed to Phase 144**: the new (RED) trace lengths for all three protocols, the note about the determinism check's structural unreachability once the primary length assertion fails, and the flash/RAM reconciliation flagged above.

---
*Phase: 141-per-byte-program-loop*
*Completed: 2026-08-10*

## Self-Check: PASSED

- FOUND: `firestarter/include/eprom.h`
- FOUND: `firestarter/src/proms/eprom.cpp`
- FOUND: `.planning/phases/141-per-byte-program-loop/141-04-SUMMARY.md`
- FOUND: commit `aeac4e7` (Task 1)
- FOUND: commit `ef0e075` (Task 2)
- FOUND: commit `3504e50` (Task 3)
- FOUND: commit `0eefac98` (meta repo, this SUMMARY)
- Re-verified `grep -c delayMicroseconds src/proms/eprom.cpp` = 0 and `grep -c "row->" src/proms/eprom.cpp` = 7, matching this document's claims.
