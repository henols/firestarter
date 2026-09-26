---
phase: 143-host-timeout-progress-pulse-override
plan: 05
subsystem: firmware
tags: [c, cpp, platformio, unity, avr, arduino, eprom, native-test, serial-protocol, progress]

# Dependency graph
requires:
  - phase: 143-01
    provides: "test_loop_eprom_v131.cpp at 45 cases (39 + six budget cases) -- the file this plan extends to 47; also eprom_budget.h/eprom_budget.cpp, unused directly by this plan's code but sharing the same TU family"
  - phase: 143-03
    provides: "the post-143-03 whole-firmware-repo pytest baseline (282 passed) and the post-143-03 leonardo flash figure (26798 B, 1874 B headroom) that this plan's own verification is measured against and reports a delta from"
provides:
  - "EPROM_PROGRESS_EMIT_INTERVAL_MS (include/eprom.h) -- the named cadence constant, 1000 ms"
  - "A time-gated, #ifndef SERIAL_ON_IO-guarded MSG_DATA_PROGRESS (0xE0) emission at the top of eprom_internal_write_execute_body's per-byte loop (src/proms/eprom.cpp) -- compiled in on leonardo and native, compiled out (variable and all) on uno/uno328pb"
  - "tests/golden/protocol_branch_inventory.json re-derived by an independent parse against the new eprom.cpp -- counts unchanged (26/1/25), protocol_lines unchanged ([70])"
  - "Two new native cadence cases in test_loop_eprom_v131.cpp proving the emission fires (>=2 frames, strictly increasing, in range, correct payload) and does not fire with a frozen clock"
affects: [143-06, 143-08, 143-10, 144, 145]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Compile-time #ifndef SERIAL_ON_IO guard as the mitigation for a fixed-size deferred-log buffer that a new emission would otherwise silently overflow on Uno-class targets -- the same defect class as an existing runtime handle->cmd guard elsewhere in the same file, but this call site has no handle->cmd to test"
    - "D-25 RED/GREEN evidence via named, single-line-or-block production-code plants applied to the .cpp only, run, captured, and reverted via `git checkout --` -- never planted in the test file"
    - "Advancing-clock Unity mock (file-static counter + AlwaysDo lambda) as the ONLY way to make a time-gated production code path reachable at all in a native harness whose default is a frozen clock"

key-files:
  created: []
  modified:
    - firestarter/include/eprom.h
    - firestarter/src/proms/eprom.cpp
    - firestarter/src/eprom_operations.cpp
    - firestarter/tests/golden/protocol_branch_inventory.json
    - firestarter/test/native/avr/test_loop_eprom_v131/test_loop_eprom_v131.cpp

key-decisions:
  - "EPROM_PROGRESS_EMIT_INTERVAL_MS = 1000 ms, named in include/eprom.h rather than file-local in eprom.cpp, specifically so the native cadence case can reference it instead of duplicating the literal"
  - "The emission and its state variable are BOTH guarded #ifndef SERIAL_ON_IO (not a runtime accessor, not a raised DEFERRED_LOG_MAX, not a reserve-headroom invariant) -- BF-2's mechanism (Uno's UART torn down for the whole programmer-mode window; a 5th deferred frame is silently dropped, which would starve a subsequent MSG_ERR_MAX_PULSES frame of its slot) makes every rejected alternative either RAM-costly or still zero-delivery on Uno"
  - "The emission sits BEFORE the two LOOP-06 skips, not after -- cadence independent of how many bytes are skipped, matching this plan's own D-25 plant 4 finding that moving it after the skips measurably changes the frame count"
  - "Payload is (absolute chip address, handle->mem_size), matching mem_util_blank_check's own MSG_DATA_PROGRESS emit byte for byte -- 0xE0 keeps exactly one payload contract, never a block-relative pair"
  - "Discovered during execution, not anticipated by the plan text: the advancing millis() mock (required so the time-gated emission is reachable at all) fires on EVERY pre-existing case's drive too, since the emission is unconditional-before-skips by design. A first attempt at a 500 ms/call step broke the pre-existing test_loop06_a_block_of_only_skipped_bytes_emits_no_pulse_at_all (logged_id_count() no longer 0). Fixed by lowering the step to 200 ms (keeps every pre-existing case's worst-case 4-iteration accumulated delta at 800 ms, under the 1000 ms interval) and by extending this plan's own two cases' block to 16 bytes (8 genuinely-programmed + 8 trailing 0xFF filler, still within the read-back model's 8-slot cap) rather than touching any pre-existing case -- no pre-existing case was modified."

patterns-established:
  - "Pattern: when a new time-gated (millis()) code path is added to production code compiled into a native suite whose clock mock was previously frozen, the mock must be converted to advancing BEFORE the new cadence case is even written, and every pre-existing case sharing that mock must be re-audited for any exact-count assertion the newly-reachable emission could perturb -- silence is not proof of safety here, since the emission is skip-count-independent by this plan's own design and will touch every drive, not just the new cases'."

requirements-completed: []

coverage:
  - id: D1
    description: "Time-gated MSG_DATA_PROGRESS emission at the top of the per-byte write loop, guarded #ifndef SERIAL_ON_IO (both the emission and its state variable), landed in the same commit as the re-derived golden (D-23)"
    verification:
      - kind: unit
        ref: "firestarter/tests/test_protocol_branch_inventory.py::test_blob_shas_match_the_recorded_inventory (post-commit)"
        status: pass
      - kind: unit
        ref: "firestarter/tests/test_protocol_branch_inventory.py::test_branch_sites_match_the_recorded_inventory"
        status: pass
      - kind: unit
        ref: "firestarter/tests/test_protocol_branch_inventory.py::test_exactly_one_protocol_keyed_site_at_the_pinned_line"
        status: pass
      - kind: unit
        ref: "python3 scripts/check_build_warnings.py --rebuild (all three AVR targets)"
        status: pass
      - kind: unit
        ref: "pio test -e native / -e native_nodevtools (141 test cases: 141 succeeded, 17 suites each)"
        status: pass
    human_judgment: false
  - id: D2
    description: "Cadence proven in both directions on the native oracle: >=2 increasing, in-range, correctly-payloaded frames when the mocked clock advances; zero frames with the clock frozen; every case seen RED under its own named D-25 plant"
    verification:
      - kind: unit
        ref: "firestarter/test/native/avr/test_loop_eprom_v131/test_loop_eprom_v131.cpp#test_progress_emits_when_the_clock_advances_past_the_interval"
        status: pass
      - kind: unit
        ref: "firestarter/test/native/avr/test_loop_eprom_v131/test_loop_eprom_v131.cpp#test_progress_emits_nothing_when_the_clock_does_not_advance"
        status: pass
    human_judgment: false
  - id: D3
    description: "Zero AVR warnings, leonardo fits under 28672 B (cold-measured), both pinned native envs unmoved at 141/17, whole firmware pytest suite at 282 (unchanged from post-143-03), check_size_baseline.py RED for the recorded MERGE-05/OD-2 reasons only, native_trace_v131 RED and unchanged from pre-plan values (D-24)"
    verification:
      - kind: unit
        ref: "pio run -e uno / -e uno328pb / -e leonardo (cold)"
        status: pass
      - kind: unit
        ref: "python3 -m pytest tests/ -o addopts=\"\" -q"
        status: pass
      - kind: unit
        ref: "python3 scripts/check_size_baseline.py --rebuild"
        status: pass
    human_judgment: false

duration: 44min
completed: 2026-08-13
status: complete
---

# Phase 143 Plan 05: Intra-Block MSG_DATA_PROGRESS Emission, Guarded off SERIAL_ON_IO Summary

**A time-gated `MSG_DATA_PROGRESS` (0xE0) emission now fires from inside `eprom.cpp`'s per-byte write loop on leonardo and native, compiled out entirely on uno/uno328pb (BF-2's deferred-log-buffer hazard), landed in one commit with a parse-re-derived `protocol_branch_inventory.json` golden, plus two native cases proving the cadence both fires and doesn't vacuously.**

## Performance

- **Duration:** ~44 min
- **Started:** 2026-08-13T01:28:59Z (STATE.md `last_updated` at hand-off from 143-03)
- **Completed:** 2026-08-13T02:12:36Z
- **Tasks:** 2 completed (both `type="auto"`, no checkpoints)
- **Files touched:** 5 (0 created, 5 modified)

## Accomplishments

- **HOST-02's firmware half is implemented.** `include/eprom.h` names `EPROM_PROGRESS_EMIT_INTERVAL_MS` (1000 ms, with the full four-part cadence rationale: 10x margin on the old response window, ~2 frames/block at the modal 0x07 width, ~1678 frames/~17 kB over ~28 min at the CLI's own 65535us ceiling on an uncapped row, and why 5 s would feel dead). `src/proms/eprom.cpp`'s `eprom_internal_write_execute_body` now carries a doubly-guarded (`#ifndef SERIAL_ON_IO` on both the state variable and the emit) time-gated `MSG_DATA_PROGRESS` emission at the top of the per-byte loop, before the two LOOP-06 skips, with a payload of `(absolute address, handle->mem_size)` matching `mem_util_blank_check`'s own emit byte for byte.
- **BF-2's trap is closed, not merely noted.** The comment block above the guard carries BF-2's full mechanism (UART torn down for the whole programmer-mode window; the Uno's `rurp_log_id` defers into a 4-slot buffer; a 5th frame is silently dropped, which would starve a subsequent `MSG_ERR_MAX_PULSES` frame of its slot -- turning a program failure into a host transport timeout, HOST-03's exact anti-goal on a path that works today), cites both in-tree sites that already document the same trap at runtime, names all three rejected mitigations with their costs, and states D-06's now-two-dimension non-claim verbatim.
- **`src/eprom_operations.cpp`'s stale "host shows its own progress" comment is replaced** with language naming both halves of D-06's non-claim (comment-only; `git diff` on this file shows a comment-only change).
- **The golden is re-derived by an independent parse, not a hand-edit.** A throwaway script imported `_extract_predicates`/`_scan_params_table` directly from `tests/test_protocol_branch_inventory.py` and ran them against the committed `eprom.cpp`; the diff against the prior golden showed exactly what the plan predicted: `counts` unchanged at 26/1/25, `protocol_lines` still `[70]`, and every site at or below the insertion point (old line >= 321) shifted line number only -- zero sites added, removed, or re-keyed. `blob_shas["src/proms/eprom.cpp"]` was set to `git hash-object`'s output on the final working-tree file, confirmed equal to `git rev-parse HEAD:src/proms/eprom.cpp` after the commit.
- **All four files landed in ONE commit (D-23).** Pre-commit, `test_blob_shas_match_the_recorded_inventory` was the ONLY red leg (the intended one-reason window); all other six legs were already green because the golden was updated before the commit. Post-commit, all seven legs are green.
- **Zero AVR warnings, cold-measured, with a real per-target delta.** `uno` and `uno328pb` show **zero flash delta** from post-143-03 (24824 B / 24874 B, byte-identical) -- direct, measured proof the `#ifndef SERIAL_ON_IO` guard truly excludes the code on those targets, not merely an assertion about source text. `leonardo` grew by **+108 B** (26798 -> 26906 / 28672, 1766 B headroom remaining of F-142-08's 2130 B hand-off).
- **Both pinned native envs unmoved at 141/141, 17 suites** -- confirming the new `millis()` call inside the write body causes no ArduinoFake SIGABRT in either `native` or `native_nodevtools` (neither compiles a suite that drives the write body with an unmocked `millis`).
- **Two new native cases prove the cadence in both directions**, each seen RED under a named, real plant against `src/proms/eprom.cpp` (never the test file) and GREEN once reverted. `native_loop_v131`'s own suite grew from 45 to 47 cases (77 -> 79 across both its suites).
- **`native_trace_v131` reproduces exactly the pre-plan RED values** (0x07 expected 198 was 91; 0x08 expected 221 was 115; 0x0B expected 201 was 59) -- byte-identical to 143-03's recorded state, confirming D-24's claim that this emission adds zero new frames to that frozen trace (its own `millis()` is pinned to `AlwaysReturn(0)`).
- **A genuine interaction was discovered and fixed during execution** (see Deviations below): the advancing clock mock a time-gated emission requires also perturbs every pre-existing drive in the same suite, because the emission fires before the skip checks by design. Fixed without touching any pre-existing case.

## Task Commits

Each task was committed atomically, inside `/workspaces/firestarter` on branch `gsd/v1.31-27c-programming-algorithm-fidelity`:

1. **Task 1: The interval constant, the guarded time-gated emission, the stale comment and the re-derived golden -- ONE commit (D-23)** - `b4f0779` (feat)
2. **Task 2: Replace the frozen millis() mock with an advancing counter and prove the cadence in both directions** - `7a130b6` (test)
   - **Rule 1 auto-fix, caught during this plan's own SUMMARY-writing review** - `9398d40` (fix) -- see Deviations below

**Plan metadata:** committed in the meta repo (`/workspaces`), see below.

## Files Created/Modified

- `firestarter/include/eprom.h` - `EPROM_PROGRESS_EMIT_INTERVAL_MS` (1000), with the full cadence rationale, appended after `eprom_hv_route_mask`'s declaration inside the existing `extern "C"` block
- `firestarter/src/proms/eprom.cpp` - `eprom_internal_write_execute_body`: a guarded `last_emit_ms` state variable after `org_delay`, and a guarded time-gated `MSG_DATA_PROGRESS` emit at the top of the per-byte loop, before the LOOP-06 skips; nothing else in the function changed (confirmed by `git diff`)
- `firestarter/src/eprom_operations.cpp` - the stale "host shows its own progress" comment in `_process_incoming_data` replaced with D-06's two-dimension non-claim (comment-only)
- `firestarter/tests/golden/protocol_branch_inventory.json` - re-derived by independent parse: 13 sites' line numbers shifted (all at or below the insertion point), `counts` unchanged, `blob_shas`/`recorded_at_head`/`recorded_by`/`frozen_for` updated per D-23's own `how_to_update`
- `firestarter/test/native/avr/test_loop_eprom_v131/test_loop_eprom_v131.cpp` - a new file-static `millis_counter`, `setUp`'s frozen `millis()` mock replaced with an advancing 200 ms/call `AlwaysDo` lambda, two new cases (`test_progress_emits_when_the_clock_advances_past_the_interval`, `test_progress_emits_nothing_when_the_clock_does_not_advance`) registered in `main()`; every pre-existing case, `tearDown`, `make_loop_handle`, `drive_loop_write`, the `LOOP_BUS_CONFIG_*` constants and the `micros` mock are byte-unchanged

## Decisions Made

- **`EPROM_PROGRESS_EMIT_INTERVAL_MS` named in the header, not file-local.** So the native cadence case references it by name (no duplicated literal), per the plan's own instruction.
- **Guard shape: compile-time `#ifndef SERIAL_ON_IO`, not a runtime accessor.** All three rejected alternatives (runtime `com_mode` accessor, raised `DEFERRED_LOG_MAX`, reserve-headroom invariant) were considered and rejected with recorded reasons, per BF-2's own analysis -- each keeps the Uno-delivery trap at a real cost (an accessor call everywhere, RAM on the tightest target, or a fragile cross-file invariant) while still delivering zero intra-block progress there.
- **Emission placed before the LOOP-06 skips**, matching the plan's instruction that cadence should be independent of skip count -- and empirically confirmed load-bearing by D-25 plant 4 (relocating it after the skips measurably changed the achievable frame count in this plan's own case).
- **200 ms/call advancing-clock step, not the 500 ms tried first** (see Deviations) -- the smallest round number that keeps every pre-existing case's worst-case accumulated delta under the 1000 ms interval while still letting this plan's own 16-byte cases cross the interval multiple times.
- **16-byte block (8 real + 8 trailing 0xFF filler) for both new cases**, not a pure 8-byte non-0xFF block as the plan's literal prose suggested -- the read-back model's `LOOP_READBACK_MAX_ENTRIES` (8) caps how many DISTINCT addresses can be seeded, and the trailing 0xFF bytes need no seed at all (LOOP-06's own first skip rule short-circuits before any read), so they extend the achievable iteration count without needing more read-back slots. The first 8 bytes alone still prove "the per-byte loop actually runs" (genuine pulse-and-verify convergence); the filler bytes exist purely to extend the mocked-clock's iteration budget.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Discovered and fixed an interaction between the advancing clock mock and a pre-existing LOOP-06 case**
- **Found during:** Task 2, on the first full run of the updated suite (`pio test -e native_loop_v131 -f "*test_loop_eprom_v131*"`), immediately after adding the two new cases with a first-attempt 500 ms/call advancing mock and an 8-byte block
- **Issue:** `test_loop06_a_block_of_only_skipped_bytes_emits_no_pulse_at_all` (a pre-existing, Phase-141-authored case driving a 4-byte, all-0xFF block and asserting `logged_id_count() == 0`) went RED: "Expected 0 Was 2". Root cause: this plan's emission fires at the TOP of the per-byte loop, BEFORE the two LOOP-06 skips, by design (so the cadence is skip-count-independent) -- so it fires on every iteration of EVERY drive in the suite, not just this plan's own two cases. With the clock advancing at 500 ms/call, the mocked time crossed `EPROM_PROGRESS_EMIT_INTERVAL_MS` (1000 ms) twice within that pre-existing case's own 4 iterations, producing 2 unexpected `MSG_DATA_PROGRESS` frames it had never accounted for (it predates this plan's emission by two milestones).
- **Fix:** Lowered the advancing step to 200 ms/call (the pre-existing suite's longest block is 4 bytes, grep-confirmed across every `drive_loop_write` call; 4 iterations' worst-case accumulated delta at 200 ms/call is 800 ms, safely under the 1000 ms interval) and extended this plan's own two cases' block from 8 to 16 bytes (8 genuinely-programmed bytes + 8 trailing 0xFF filler, still within the read-back model's 8-slot cap) so the mocked clock still crosses the interval multiple times within the longer block. No pre-existing case's own code was touched.
- **Files modified:** `firestarter/test/native/avr/test_loop_eprom_v131/test_loop_eprom_v131.cpp` (same file this plan already modifies; folded into task 2's own commit, not a separate one, since the fix was found and applied before that commit)
- **Verification:** Full suite re-run: 47 test cases: 47 succeeded (0 failed), including the previously-broken case; both pinned native envs (`native`, `native_nodevtools`) still 141/141, 17 suites.
- **Committed in:** `7a130b6` (Task 2's own commit -- the fix was applied before that commit was made, so no separate commit exists for it)

**2. [Rule 1 - Bug] Corrected a stale "8-byte drive" reference in the cadence case's own assertion message**
- **Found during:** Writing this SUMMARY, on a final review pass of the test file's diff
- **Issue:** `test_progress_emits_when_the_clock_advances_past_the_interval`'s `TEST_ASSERT_TRUE_MESSAGE` for the `progress_count >= 2` check still read "across this 8-byte drive" after the block was extended to 16 bytes (deviation 1, above) -- a stale diagnostic string, not a logic error (the assertion itself was always correct).
- **Fix:** Updated the message to "16-byte drive". Message text only.
- **Files modified:** `firestarter/test/native/avr/test_loop_eprom_v131/test_loop_eprom_v131.cpp`
- **Verification:** Suite re-run: 47 test cases: 47 succeeded, unchanged.
- **Committed in:** `9398d40`

---

**Total deviations:** 2 auto-fixed (2 bugs, both Rule 1)
**Impact on plan:** Deviation 1 was necessary to satisfy this plan's own "no change to any pre-existing case" constraint while still meeting its ">= 2 frames" cadence requirement -- the two constraints are in real tension given the read-back model's 8-slot cap and the emission's skip-independent placement, and the fix resolves it without touching pre-existing behaviour. Deviation 2 is cosmetic (a diagnostic string). Neither touches any pinned golden, `platformio.ini`, `host_stubs.cpp`, `size_baseline.json`, or `test_trace_eprom_v131/`.

## D-25 Evidence: RED-on-plant for all four required plants, then GREEN, for `test_loop_eprom_v131.cpp`'s two new cases

Per the plan's obligation, each plant was applied to the **committed** `src/proms/eprom.cpp` (never the test file) via the Edit tool, run, captured, and reverted via `git checkout -- src/proms/eprom.cpp` (confirmed byte-identical to the committed file via `git diff --exit-code` after every revert) before the next plant. The suite's ~45 pre-existing `[PASSED]` lines that are identical across every run are elided (`...`) below to keep this section readable; nothing about the failing/passing outcome of any case is trimmed. As in 143-01/143-03, every RED run below ends with `[ERRORED]` and a received signal (varying across runs) rather than a clean `[FAILED]`-only exit -- the same pre-existing native-harness artifact those plans already documented (Unity's own per-assertion `[PASSED]`/`[FAILED]` lines, printed before the signal, are complete and correct for every plant; the signal/`[ERRORED]` wrapper and the header's off-by-one "N test cases" count are not evaluated by any acceptance criterion, which names only the final, all-GREEN state -- clean below, no `ERRORED`, no signal).

### Plant 1 -- delete the emit (`LOG_DATA_ID_U32_U32(...)` call replaced with a comment)

Targets case 1 RED (via zero frames) and doubles as the reachability proof the plan requires.

```
...
test/native/avr/test_loop_eprom_v131/test_loop_eprom_v131.cpp:2041: test_progress_emits_when_the_clock_advances_past_the_interval: at least 2 MSG_DATA_PROGRESS frames must have fired while the mocked clock advanced past EPROM_PROGRESS_EMIT_INTERVAL_MS repeatedly across this 16-byte drive -- zero would mean the emission never fires (deleted or unreachable); exactly 1 would not prove the cadence REPEATS	[FAILED]
test/native/avr/test_loop_eprom_v131/test_loop_eprom_v131.cpp:2042: test_progress_emits_nothing_when_the_clock_does_not_advance	[PASSED]
Program received signal SIGHUP (Hangup)
- native_loop_v131:native/avr/test_loop_eprom_v131 [ERRORED] Took 1.10 seconds -

=================================== SUMMARY ===================================
Environment       Test                             Status    Duration
----------------  -------------------------------  --------  ------------
native_loop_v131  native/avr/test_loop_eprom_v131  ERRORED   00:00:01.104

============ 48 test cases: 1 failed, 46 succeeded in 00:00:01.104 ============
```

**Finding:** exactly the targeted case (case 1) went RED; case 2 (the frozen-clock control) correctly stayed GREEN -- with zero frames either way (none ever emitted, none ever expected), which is precisely the asymmetry the plan names as the proof. Case 1's RED with the emit deleted is also the plan's own required reachability check: it proves the positive case genuinely depends on the emission firing, not on some other incidental side effect of the drive.

### Plant 2 -- comparison inverted (`>=` to `<=`)

Targets case 2 RED (frames would appear with a frozen clock).

```
...
test/native/avr/test_loop_eprom_v131/test_loop_eprom_v131.cpp:1983: test_loop06_an_already_matching_byte_is_read_once_and_never_pulsed	[PASSED]
test/native/avr/test_loop_eprom_v131/test_loop_eprom_v131.cpp:800: test_loop06_a_block_of_only_skipped_bytes_emits_no_pulse_at_all: Expected 0 Was 4. no error id logged for an all-0xFF block	[FAILED]
test/native/avr/test_loop_eprom_v131/test_loop_eprom_v131.cpp:1995: test_loop06_the_ff_rule_does_not_suppress_the_final_verify_pass	[PASSED]
...
test/native/avr/test_loop_eprom_v131/test_loop_eprom_v131.cpp:2041: test_progress_emits_when_the_clock_advances_past_the_interval	[PASSED]
test/native/avr/test_loop_eprom_v131/test_loop_eprom_v131.cpp:1970: test_progress_emits_nothing_when_the_clock_does_not_advance: Expected 0 Was 16. zero MSG_DATA_PROGRESS frames with the clock frozen at a constant (matching native_trace_v131's own AlwaysReturn(0) pin, D-24) -- the emission must be genuinely time-gated, never unconditional	[FAILED]
Program received signal SIGINT (Interrupt)
- native_loop_v131:native/avr/test_loop_eprom_v131 [ERRORED] Took 1.09 seconds -

=================================== SUMMARY ===================================
Environment       Test                             Status    Duration
----------------  -------------------------------  --------  ------------
native_loop_v131  native/avr/test_loop_eprom_v131  ERRORED   00:00:01.090

============ 48 test cases: 2 failed, 45 succeeded in 00:00:01.090 ============
```

**Finding (honest, not glossed): this plant broke case 2 as required, PLUS the pre-existing `test_loop06_a_block_of_only_skipped_bytes_emits_no_pulse_at_all`.** With `<=` instead of `>=`, the comparison is true almost every call (a diff of 0 or any small value already satisfies `<= 1000`), so the emission fires on nearly every single iteration of every drive in the suite, not just case 2's frozen-clock one. This is a stronger, not weaker, result than the minimum asked for -- it independently confirms the emission's placement (before every drive's skip checks) makes it suite-wide-observable the moment the guard condition is wrong in either direction, exactly the property deviation 1 above had to design around.

### Plant 3 -- payload's second parameter changed (`handle->mem_size` to `handle->data_size`)

Targets case 1's geometry assertion.

```
...
test/native/avr/test_loop_eprom_v131/test_loop_eprom_v131.cpp:2042: test_progress_emits_nothing_when_the_clock_does_not_advance	[PASSED]
Program received signal SIGHUP (Hangup)
- native_loop_v131:native/avr/test_loop_eprom_v131 [ERRORED] Took 3.12 seconds -

=================================== SUMMARY ===================================
Environment       Test                             Status    Duration
----------------  -------------------------------  --------  ------------
native_loop_v131  native/avr/test_loop_eprom_v131  ERRORED   00:00:03.124

============ 48 test cases: 1 failed, 46 succeeded in 00:00:03.124 ============
```

The single failing line:
```
test/native/avr/test_loop_eprom_v131/test_loop_eprom_v131.cpp:1928: test_progress_emits_when_the_clock_advances_past_the_interval: Expected 65536 Was 16. progress frame's second u32 must equal handle->mem_size (D-04's one payload contract -- absolute address plus chip geometry, never a block-relative pair)	[FAILED]
```

**Finding:** only the targeted case failed, on exactly the geometry assertion the plant targets (`Expected 65536` -- the handle's real `mem_size` -- `Was 16` -- the block's own `data_size`, the wrong field the plant substituted). Case 2 and every pre-existing case stayed GREEN.

### Plant 4 -- emit relocated after the LOOP-06 skips

Targets case 1's cadence assertions, per the plan's own instruction to drive a buffer with 0xFF content and observe the placement dependency.

```
...
test/native/avr/test_loop_eprom_v131/test_loop_eprom_v131.cpp:2042: test_progress_emits_nothing_when_the_clock_does_not_advance	[PASSED]
Program received signal SIGHUP (Hangup)
- native_loop_v131:native/avr/test_loop_eprom_v131 [ERRORED] Took 3.56 seconds -

=================================== SUMMARY ===================================
Environment       Test                             Status    Duration
----------------  -------------------------------  --------  ------------
native_loop_v131  native/avr/test_loop_eprom_v131  ERRORED   00:00:03.562

============ 48 test cases: 1 failed, 46 succeeded in 00:00:03.562 ============
```

The single failing line:
```
test/native/avr/test_loop_eprom_v131/test_loop_eprom_v131.cpp:1939: test_progress_emits_when_the_clock_advances_past_the_interval: at least 2 MSG_DATA_PROGRESS frames must have fired while the mocked clock advanced past EPROM_PROGRESS_EMIT_INTERVAL_MS repeatedly across this 16-byte drive -- zero would mean the emission never fires (deleted or unreachable); exactly 1 would not prove the cadence REPEATS	[FAILED]
```

**Finding, stated honestly (a different specific assertion than the plan anticipated, same underlying property proven):** the plan's own wording expected "case 1's strictly-increasing or in-range assertion RED" via "a buffer that begins with 0xFF bytes." This plan's actual block places its 8 real bytes FIRST and its 8 0xFF filler bytes LAST (deviation 1's fix, not a leading-0xFF layout) -- so relocating the emit after the skips does not corrupt any IN-RANGE or MONOTONIC frame (every frame that does fire is still a genuine, correctly-ordered, correctly-addressed one); instead, it removes the filler bytes' chance to ever reach the (now relocated) emit at all, since they are skipped via the 0xFF check before reaching it. Two of this drive's three normal frames land on filler-byte iterations (measured), so the achievable count drops from 3 to 1, and the FINAL floor assertion (`>= 2`) is what catches it -- a RED for the identical underlying reason the plan names (placement sensitivity), reached via a different specific line within the same case. Case 2 and every pre-existing case stayed GREEN.

### Final GREEN (all four plants reverted; `git diff --exit-code -- src/proms/eprom.cpp` clean throughout)

```
...
test/native/avr/test_loop_eprom_v131/test_loop_eprom_v131.cpp:2041: test_progress_emits_when_the_clock_advances_past_the_interval	[PASSED]
test/native/avr/test_loop_eprom_v131/test_loop_eprom_v131.cpp:2042: test_progress_emits_nothing_when_the_clock_does_not_advance	[PASSED]
- native_loop_v131:native/avr/test_loop_eprom_v131 [PASSED] Took 3.41 seconds -

=================================== SUMMARY ===================================
Environment       Test                             Status    Duration
----------------  -------------------------------  --------  ------------
native_loop_v131  native/avr/test_loop_eprom_v131  PASSED    00:00:03.412
================= 47 test cases: 47 succeeded in 00:00:03.412 =================
```

**No `ERRORED`, no signal at all** -- clean PASSED, satisfying the task's own acceptance criterion literally. Every plant produced a RED for the reason it targets (with two honest, stronger-than-required findings noted above) and GREEN once reverted.

## Verification Results (final state, all reverted)

| Check | Result |
|---|---|
| `python3 -m pytest tests/test_protocol_branch_inventory.py -v -o addopts=""` (pre-commit) | 6 passed, 1 failed (`test_blob_shas_match_the_recorded_inventory` -- the intended one-reason D-23 window, pre-commit only) |
| `python3 -m pytest tests/test_protocol_branch_inventory.py -v -o addopts=""` (post-commit) | **7 passed** |
| `git log --stat -1` (task 1's commit) | exactly `include/eprom.h`, `src/eprom_operations.cpp`, `src/proms/eprom.cpp`, `tests/golden/protocol_branch_inventory.json` |
| `pio run -e uno` (cold) | SUCCESS; RAM 76.8% (1573/2048 B, unchanged from 143-03); Flash 77.0% (24824/32256 B) -- **byte-identical to post-143-03**, confirming zero code compiled on this SERIAL_ON_IO target |
| `pio run -e uno328pb` (cold) | SUCCESS; RAM 77.1% (1579/2048 B, unchanged); Flash 76.8% (24874/32384 B) -- **byte-identical to post-143-03** |
| `pio run -e leonardo` (cold) | SUCCESS; RAM 78.7% (2014/2560 B, unchanged); Flash 93.8% (26906/28672 B, **+108 B** vs. 143-03's 26798) -- **1766 B headroom remaining** of F-142-08's 2130 B hand-off, D-22 |
| `python3 scripts/check_build_warnings.py --rebuild` (cold) | `PASS`: uno/uno328pb/leonardo macro_redefinition=0; native/native_nodevtools total warnings=1166 (== watermark) -- unmoved. Independently re-confirmed by a direct `grep -i warning` over the raw cold AVR build logs: **zero warning lines of any kind** on all three AVR targets (see Issues Encountered for a gate-mechanism note) |
| `pio test -e native` | 141 test cases: 141 succeeded, 17 suites -- unmoved |
| `pio test -e native_nodevtools` | 141 test cases: 141 succeeded, 17 suites -- unmoved |
| `pio test -e native_loop_v131 -f "*test_loop_eprom_v131*"` | 47 test cases: 47 succeeded (was 45 before this plan) |
| `pio test -e native_loop_v131` (bare, both suites) | 79 test cases: 79 succeeded (`test_loop_eprom_v131` 47 + `test_vpp_eprom_v131` 32; was 77 before this plan) |
| `pio test -e native_trace_v131` | `ERRORED` (expected, D-24): 0x07 expected 198 was 91; 0x08 expected 221 was 115; 0x0B expected 201 was 59 -- **byte-identical to 143-03's recorded values**, confirming this emission adds zero new frames there |
| `python3 -m pytest tests/ -o addopts="" -q` (post both commits) | **282 passed** -- the post-143-03 count, unchanged |
| `python3 scripts/check_size_baseline.py --rebuild` | `FAIL` (expected, D-22/OD-2): `uno: flash_used baseline=23954 observed=24824`; `uno328pb: flash_used baseline=24004 observed=24874`; `leonardo: flash_used baseline=26016 observed=26906` -- flash_used only, on all three AVR targets; no RAM mismatch, no native mismatch. uno/uno328pb figures are byte-identical to 143-03's own recording (this plan added zero bytes there); leonardo's `observed` grew by exactly this plan's +108 B. `size_baseline.json` untouched (`git diff --exit-code` clean) |
| `git diff --exit-code -- scripts/baseline/size_baseline.json platformio.ini test/native/avr/test_loop_eprom_v131/host_stubs.cpp test/native/avr/test_trace_eprom_v131/` | clean |
| `git status --short` in `/workspaces/firestarter_app` | not applicable this plan -- firmware submodule only (D-01) |

## Issues Encountered

- **`check_build_warnings.py`'s AVR check measures `macro_redefinition` specifically, not a general "total" warning count.** The plan's own acceptance criteria describe this gate as "the criterion that catches an unguarded `last_emit_ms` declaration" via "all three AVR targets at `total: 0`" -- reading the script directly (`check_env`, `scripts/check_build_warnings.py:121-149`) shows the AVR branch only regex-matches the macro-redefinition diagnostic shape and reports that count; it never computes or asserts a general warning total for AVR envs (only the two native envs get a `total_count` comparison). This means an unused-variable warning would not, in fact, be caught by this specific script's AVR arm. Not a defect introduced by this plan (the script's own behaviour is pre-existing and unchanged); worth naming so a future reader does not over-trust this one gate for that specific class. Independently closed the gap for this plan's own claim by grepping the raw cold `pio run -e uno`/`-e uno328pb`/`-e leonardo` output directly for any `warning` line (not just macro-redefinition) and confirming zero on all three -- the true, stronger evidence that the guard placement produces no warning of any kind, not just no macro-redefinition.
- **The advancing-clock/pre-existing-case interaction** (deviation 1, above) was the substantive issue this session; documented in full there.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- The firmware half of HOST-02 (the intra-block progress emission itself) is complete and proven on leonardo/native; the Uno-class non-delivery is proven as a source contract by construction here and will be pinned mechanically by plan 143-08's dedicated gate (`tests/test_progress_emission_is_leonardo_only.py`), not behaviourally -- this plan does not attempt that proof, per its own scope.
- **D-06's non-claim, both dimensions, restated for the phase record:** intra-block write progress is emitted on the EPROM path only (not flash/EEPROM/SRAM), and delivered on `leonardo` only (compiled out on `uno`/`uno328pb`).
- **D-05's other half (a stray mid-block host ack on Leonardo aborting the write with no error frame) is unchanged firmware code** -- noted per the plan's own instruction, owned by plan 143-06 on the host side.
- This plan intentionally marks no requirement Complete (frontmatter `requirements: []`); plan 143-10 flips the `HOST-*` checkboxes once every plan's evidence exists.
- **Flash headroom consumed:** this plan spent 108 B of F-142-08's 2130 B hand-off, on `leonardo` only (uno/uno328pb both stayed at zero delta, confirming the guard). `leonardo` has **1766 B** of headroom remaining for the phase's one other firmware plan, 143-08 (the Leonardo-only source-contract gate) -- worth tracking, not yet a concern.
- `check_size_baseline.py`'s flash-growth RED and `native_trace_v131`'s RED both remain exactly as recorded and operator-accepted; neither is this plan's or this phase's to fix (Phase 144/TEST-06, TEST-08).
- No blockers. All pinned artifacts this plan must not touch (`scripts/baseline/size_baseline.json`, `platformio.ini`, `test/native/avr/test_loop_eprom_v131/host_stubs.cpp`, `test/native/avr/test_trace_eprom_v131/`) are confirmed untouched by `git diff --exit-code`.

## Self-Check: PASSED

- FOUND: `firestarter/include/eprom.h` (modified)
- FOUND: `firestarter/src/proms/eprom.cpp` (modified)
- FOUND: `firestarter/src/eprom_operations.cpp` (modified)
- FOUND: `firestarter/tests/golden/protocol_branch_inventory.json` (modified)
- FOUND: `firestarter/test/native/avr/test_loop_eprom_v131/test_loop_eprom_v131.cpp` (modified)
- FOUND commit `b4f0779` (Task 1)
- FOUND commit `7a130b6` (Task 2)
- FOUND commit `9398d40` (Rule 1 deviation)

---
*Phase: 143-host-timeout-progress-pulse-override*
*Completed: 2026-08-13*
