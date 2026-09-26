---
phase: 143-host-timeout-progress-pulse-override
plan: 01
subsystem: firmware
tags: [c, cpp, platformio, unity, avr, arduino, eprom, native-test]

# Dependency graph
requires: []
provides:
  - "eprom_worst_pulses / eprom_per_byte_budget_us / eprom_block_budget_s (include/eprom_budget.h, src/proms/eprom_budget.cpp) -- the BF-3-corrected per-block worst-case write-time budget, as a new unpinned TU"
  - "Six native Unity cases in test_loop_eprom_v131.cpp proving the corrected arithmetic, each seen RED under a named production-code plant"
  - "eprom_budget.cpp registered in platform/py32f071/CMakeLists.txt's FIRESTARTER_COMMON_SOURCES (BASE-04 gate fix)"
affects: [143-05, 143-10, 144, 145]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Pure-arithmetic, Arduino-free, unpinned TU under src/proms/ (build_src_filter's +<proms/> glob compiles it automatically, no platformio.ini edit) to keep new logic off a golden-pinned file"
    - "D-25 RED/GREEN evidence via named, single-line production-code plants applied to the .cpp only, run, captured, and reverted -- never planted in the test file"

key-files:
  created:
    - firestarter/include/eprom_budget.h
    - firestarter/src/proms/eprom_budget.cpp
  modified:
    - firestarter/test/native/avr/test_loop_eprom_v131/test_loop_eprom_v131.cpp
    - firestarter/platform/py32f071/CMakeLists.txt

key-decisions:
  - "eprom_worst_pulses/eprom_per_byte_budget_us take column values explicitly (not a protocol id) so the overprogram term stays reachable by a native case even though every shipped row carries overprogram_factor 0"
  - "eprom_block_budget_s CALLS eprom_params_for + eprom_overprogram_us rather than restating either -- the budget cannot drift from the shipped loop's runtime behaviour"
  - "Registered src/proms/eprom_budget.cpp in platform/py32f071/CMakeLists.txt's FIRESTARTER_COMMON_SOURCES (Rule 3 auto-fix) -- it is pure, Arduino-free arithmetic with no AVR-only dependency, exactly like its neighbours eprom.cpp/eprom_params.cpp, both already common sources; excluding it would have been factually wrong (there IS an ARM analogue)"

patterns-established:
  - "Pattern: a per-block firmware budget lives in its own unpinned src/proms/ TU when the file it would naturally extend is blob-pinned by a golden fixture"
  - "Pattern: D-25 evidence captured by plant-run-revert cycles against the .cpp, never the test file, with the real (not reconstructed) transcript pasted into the SUMMARY"

requirements-completed: []

coverage:
  - id: D1
    description: "Corrected BF-3 pulse-count and per-byte budget arithmetic (ceil, UNCAPPED guard, zero-pulse-width guard, overprogram term calling the shipped function)"
    verification:
      - kind: unit
        ref: "firestarter/test/native/avr/test_loop_eprom_v131/test_loop_eprom_v131.cpp#test_budget_uncapped_energy_cap_is_not_a_cap_at_zero"
        status: pass
      - kind: unit
        ref: "firestarter/test/native/avr/test_loop_eprom_v131/test_loop_eprom_v131.cpp#test_budget_pulse_count_ceils_because_the_loop_tests_after_it_increments"
        status: pass
      - kind: unit
        ref: "firestarter/test/native/avr/test_loop_eprom_v131/test_loop_eprom_v131.cpp#test_budget_0x0b_at_49999us_is_99998us_per_byte_not_50000"
        status: pass
      - kind: unit
        ref: "firestarter/test/native/avr/test_loop_eprom_v131/test_loop_eprom_v131.cpp#test_budget_overprogram_term_is_zero_for_factor_zero_and_clamped_for_factor_three"
        status: pass
      - kind: unit
        ref: "firestarter/test/native/avr/test_loop_eprom_v131/test_loop_eprom_v131.cpp#test_budget_zero_pulse_width_never_divides_by_zero"
        status: pass
    human_judgment: false
  - id: D2
    description: "eprom_block_budget_s: per-block advertised seconds against all three shipped rows, the non-EPROM 'advertise nothing' contract, and the x2+2 padding rule"
    verification:
      - kind: unit
        ref: "firestarter/test/native/avr/test_loop_eprom_v131/test_loop_eprom_v131.cpp#test_budget_block_seconds_matches_the_shipped_rows_and_is_padded"
        status: pass
    human_judgment: false
  - id: D3
    description: "Zero added warnings on all three AVR targets, native warning watermark unmoved (measured COLD), both pinned native envs unmoved at 141/17, and the new TU registered in the py32f071 CMake manifest"
    verification:
      - kind: unit
        ref: "python3 scripts/check_build_warnings.py --rebuild (cold, post .pio/build/native* clean)"
        status: pass
      - kind: unit
        ref: "python3 -m pytest tests/ -o addopts=\"\" -q"
        status: pass
      - kind: unit
        ref: "pio run -e uno / -e uno328pb / -e leonardo"
        status: pass
    human_judgment: false

duration: 36min
completed: 2026-08-12
status: complete
---

# Phase 143 Plan 01: BF-3-Corrected Write-Time Budget Arithmetic Summary

**New `eprom_budget.h`/`eprom_budget.cpp` implement the corrected per-block worst-case write-time budget (ceil pulse count, UNCAPPED zero-cap guard, overprogram term delegated to the shipped function, divide-before-multiply seconds conversion, x2+2 padding), proven by six native Unity cases each seen RED under a named production-code plant.**

## Performance

- **Duration:** ~36 min
- **Started:** 2026-08-12T22:41:35Z (STATE.md `last_updated` at hand-off)
- **Completed:** 2026-08-12T23:16:44Z
- **Tasks:** 2 completed (both `type="auto"`, no checkpoints)
- **Files touched:** 4 (2 created, 2 modified)

## Accomplishments

- `include/eprom_budget.h` + `src/proms/eprom_budget.cpp`: a new, unpinned translation unit under `src/proms/` implementing BF-3's corrected formula end to end -- `eprom_worst_pulses` (ceil pulse count), `eprom_per_byte_budget_us` (pulse-only time plus the shipped overprogram term), and `eprom_block_budget_s` (per-block seconds, padded x2+2, `uint16_t`).
- Every one of BF-3's two named corrections is implemented and independently verified by hand (a standalone `gcc` check, run before touching the firmware build) before it ever reached the firmware build: the pulse count ceils rather than floors (`0x0B` @ `--pulse-us 49999` is 2 pulses / 99998 us per byte, not 1 pulse / 50000 us), and the overprogram term is produced by *calling* the shipped `eprom_overprogram_us` rather than restating its formula.
- Six native Unity cases added to `test_loop_eprom_v131.cpp` (39 -> 45 cases in that suite; 71 -> 77 in the `native_loop_v131` env), each seen RED under a named, single-line production-code plant (D-25) and reverted before the next.
- Discovered and fixed a real, pre-existing whole-repo pytest gate failure (`check_cmake_manifest.py`'s BASE-04 drift gate) that the new TU tripped, by registering it in `platform/py32f071/CMakeLists.txt`'s `FIRESTARTER_COMMON_SOURCES` -- the same list its neighbours `eprom.cpp`/`eprom_params.cpp` are already in.
- All three AVR targets (`uno`, `uno328pb`, `leonardo`) build clean; `leonardo` uses 26542 B of the 28672 B ceiling (2130 B headroom, matching F-142-08's hand-off figure). `check_build_warnings.py --rebuild`, measured COLD, reports zero AVR warnings and native holding at exactly the 1166 watermark on both pinned envs -- unmoved from before this plan.
- Whole-repo `python3 -m pytest tests/ -o addopts="" -q` reports **272 passed** (the plan's own stated target), committed first per L-1.

## Task Commits

Each task was committed atomically, inside `/workspaces/firestarter` on branch `gsd/v1.31-27c-programming-algorithm-fidelity`:

1. **Task 1: Author `include/eprom_budget.h` and `src/proms/eprom_budget.cpp` with the corrected BF-3 arithmetic** - `f1b17cd` (feat)
2. **Task 2: Add six budget-arithmetic cases to `test_loop_eprom_v131` and see each RED on a planted violation** - `610cb01` (test)
   - **Rule 3 auto-fix, part of reaching this task's own verification target** - `e9f6a92` (fix) -- see Deviations below

**Plan metadata:** committed in the meta repo (`/workspaces`), see below.

## Files Created/Modified

- `firestarter/include/eprom_budget.h` - declares `eprom_worst_pulses`, `eprom_per_byte_budget_us`, `eprom_block_budget_s`; states all four semantic rules (UNCAPPED, ceil, zero-pulse guard, "0 = advertise nothing") and the x2+2 padding rule in prose
- `firestarter/src/proms/eprom_budget.cpp` - the corrected arithmetic; reads the PROGMEM `eprom_params` row via `pgm_read_byte`/`pgm_read_dword` and calls the shipped `eprom_overprogram_us`
- `firestarter/test/native/avr/test_loop_eprom_v131/test_loop_eprom_v131.cpp` - six new cases + one new include, additions-only (134 insertions, 0 deletions; `setUp`/`tearDown`/the `millis` mock/every pre-existing case untouched)
- `firestarter/platform/py32f071/CMakeLists.txt` - one line added to `FIRESTARTER_COMMON_SOURCES` (Rule 3 fix, see Deviations)

## Decisions Made

- **Explicit column-value API, not protocol-keyed.** `eprom_worst_pulses`/`eprom_per_byte_budget_us` take `max_pulses`/`energy_cap_us`/`overprogram_factor`/`overprogram_cap_us` directly rather than a protocol id, because `overprogram_factor` is 0 on every one of the three shipped rows -- a protocol-keyed-only API would make the overprogram term structurally unreachable by any native case, and case 4 (the only reachable proof the term is wired at all) would be impossible to write.
- **Call, never restate, the shipped `eprom_overprogram_us`.** Confirmed by Plant 3 below: stubbing the call to a literal `0U` breaks *only* case 4, proving the term's correctness is entirely dependent on that call and not reachable by any other case's shipped-data inputs.
- **Registered the new TU in the py32f071 CMake manifest (Rule 3).** See Deviations.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Registered `eprom_budget.cpp` in `platform/py32f071/CMakeLists.txt`**
- **Found during:** Task 2's own verification step (`python3 -m pytest tests/ -o addopts="" -q`, run after committing both tasks per L-1)
- **Issue:** `tests/test_check_cmake_manifest.py::test_armed_and_passing_on_the_real_tree` went RED: `check_cmake_manifest.py`'s BASE-04 drift gate scans every `.cpp`/`.c` under `src/` and requires each to be either named in `platform/py32f071/CMakeLists.txt`'s `FIRESTARTER_COMMON_SOURCES` or covered by a reasoned `PY32_EXCLUDED` comment. The new `src/proms/eprom_budget.cpp` (this plan's task 1) matched neither, so the whole-repo pytest suite reported 271 passed / 1 failed instead of the plan's own stated "272 passed" target.
- **Fix:** Added `"${REPOSITORY_ROOT}/src/proms/eprom_budget.cpp"` to `FIRESTARTER_COMMON_SOURCES`, next to its neighbours `eprom.cpp`/`eprom_params.cpp` (both already common sources). `eprom_budget.cpp` is pure, Arduino-free arithmetic with no AVR-only dependency -- there genuinely IS an ARM analogue, so a `PY32_EXCLUDED` entry (which requires a "no ARM analogue" -class reason) would have been factually wrong.
- **Files modified:** `firestarter/platform/py32f071/CMakeLists.txt`
- **Verification:** `python3 scripts/check_cmake_manifest.py` reports `PASS` (28 enforced sources resolved); `python3 -m pytest tests/ -o addopts="" -q` reports **272 passed**.
- **Committed in:** `e9f6a92`

---

**Total deviations:** 1 auto-fixed (1 blocking, Rule 3)
**Impact on plan:** Necessary to reach the plan's own stated verification target (272 passed). No scope creep: the fix is a single line in a manifest file that exists solely to track which firmware sources the ARM port re-compiles, and does not touch any file this plan's `<threat_model>` disposes, any pinned golden, `platformio.ini`, or `size_baseline.json`.

## D-25 Evidence: RED-on-plant, then GREEN, for all six cases

Per the plan's obligation, each plant was applied to `src/proms/eprom_budget.cpp` **only** (never the test file), run via `pio test -e native_loop_v131 -f "*test_loop_eprom_v131*"`, captured, and reverted (confirmed byte-identical to the committed file via `git diff`) before the next plant. Every transcript below is the **real** captured output; the ~39 pre-existing `[PASSED]` lines that are identical across every run are elided (marked `...`) to keep this section readable -- nothing about the six new cases or the run's outcome is trimmed.

**Environment note:** every RED run below ends with `[ERRORED]` and a received signal (`SIGQUIT`/`SIGHUP`/`SIGFPE`, varying across runs) rather than a clean `[FAILED]`-only exit. This is a **pre-existing artifact of this native test harness when any case in this specific suite fails** -- the same category `platformio.ini` already documents for `test_flash_intel_vpp` ("Unity teardown abort"), just a different signal. Confirmed independent of this plan's code: Unity's own per-assertion `[PASSED]`/`[FAILED]` lines (printed *before* the signal) are correct and complete for every plant, which is what D-25 requires; the signal/`[ERRORED]` wrapper is not evaluated by any acceptance criterion (those name the **final, all-GREEN** state only, which is clean -- see the final GREEN transcript below, no `ERRORED`, no `SIGABRT`).

### Plant 1 -- ceil numerator zeroed (`+ pulse_us - 1U` -> `+ 0U`)

Targets cases 2 and 3 (BF-3's ceil correction).

```
...
test/native/avr/test_loop_eprom_v131/test_loop_eprom_v131.cpp:1875: test_budget_uncapped_energy_cap_is_not_a_cap_at_zero	[PASSED]
test/native/avr/test_loop_eprom_v131/test_loop_eprom_v131.cpp:1723: test_budget_pulse_count_ceils_because_the_loop_tests_after_it_increments: Expected 2 Was 1. BF-3: ceil(50000/49999) == 2 -- the naive min(max_pulses*pulse, cap) reading would yield 1, because the loop increments accumulated before testing it	[FAILED]
test/native/avr/test_loop_eprom_v131/test_loop_eprom_v131.cpp:1743: test_budget_0x0b_at_49999us_is_99998us_per_byte_not_50000: Expected 99998 Was 49999. 0x0B @ --pulse-us 49999 is 99998 us/byte (two pulses), not the naive 50000 -- firestarter/CLAUDE.md's 0x0B row derives the same figure independently (F-141-10); a 50000 us budget would time out a WORKING write at ~51 s (D-09)	[FAILED]
test/native/avr/test_loop_eprom_v131/test_loop_eprom_v131.cpp:1878: test_budget_overprogram_term_is_zero_for_factor_zero_and_clamped_for_factor_three	[PASSED]
test/native/avr/test_loop_eprom_v131/test_loop_eprom_v131.cpp:1879: test_budget_zero_pulse_width_never_divides_by_zero	[PASSED]
test/native/avr/test_loop_eprom_v131/test_loop_eprom_v131.cpp:1800: test_budget_block_seconds_matches_the_shipped_rows_and_is_padded: Expected 208 Was 106. 0x0B @ 49999us/1024B (the BF-3 pathological width): raw 102.4s ceils to 103s, padded x2+2 == 208 -- proves the ceil pulse-count correction survives all the way to the advertised seconds value	[FAILED]
Program received signal SIGQUIT (Quit)
- native_loop_v131:native/avr/test_loop_eprom_v131 [ERRORED] Took 1.06 seconds -

=================================== SUMMARY ===================================
Environment       Test                             Status    Duration
----------------  -------------------------------  --------  ------------
native_loop_v131  native/avr/test_loop_eprom_v131  ERRORED   00:00:01.056

============ 46 test cases: 3 failed, 42 succeeded in 00:00:01.056 ============
```

**Finding (honest, not glossed):** this plant broke case 2 and case 3 as required, **plus** case 6's first sub-assertion (`0x0B`/49999/1024) -- expected, since `eprom_block_budget_s` calls `eprom_per_byte_budget_us` -> `eprom_worst_pulses` for `0x0B`'s energy-capped rows too. No case failed to go RED.

### Plant 2 -- UNCAPPED guard mistargeted (`energy_cap_us == 0U` -> `== 1U`)

Targets case 1 (the UNCAPPED guard).

```
...
test/native/avr/test_loop_eprom_v131/test_loop_eprom_v131.cpp:1709: test_budget_uncapped_energy_cap_is_not_a_cap_at_zero: Expected 25 Was 0. energy_cap_us == 0 means UNCAPPED (0x07/0x08 both ship it) -- an unguarded min() would clamp every one of their bytes to zero instead of returning max_pulses	[FAILED]
test/native/avr/test_loop_eprom_v131/test_loop_eprom_v131.cpp:1876: test_budget_pulse_count_ceils_because_the_loop_tests_after_it_increments	[PASSED]
test/native/avr/test_loop_eprom_v131/test_loop_eprom_v131.cpp:1877: test_budget_0x0b_at_49999us_is_99998us_per_byte_not_50000	[PASSED]
test/native/avr/test_loop_eprom_v131/test_loop_eprom_v131.cpp:1758: test_budget_overprogram_term_is_zero_for_factor_zero_and_clamped_for_factor_three: Expected 25000 Was 0. factor 0 (every shipped row): overprogram term is 0, total is pulse-only 25*1000	[FAILED]
test/native/avr/test_loop_eprom_v131/test_loop_eprom_v131.cpp:1879: test_budget_zero_pulse_width_never_divides_by_zero	[PASSED]
test/native/avr/test_loop_eprom_v131/test_loop_eprom_v131.cpp:1789: test_budget_block_seconds_matches_the_shipped_rows_and_is_padded: Expected 8 Was 2. 0x07 @ 100us/1024B: raw 2.5s ceils to 3s, padded x2+2 == 8	[FAILED]
Program received signal SIGQUIT (Quit)
- native_loop_v131:native/avr/test_loop_eprom_v131 [ERRORED] Took 1.37 seconds -

=================================== SUMMARY ===================================
Environment       Test                             Status    Duration
----------------  -------------------------------  --------  ------------
native_loop_v131  native/avr/test_loop_eprom_v131  ERRORED   00:00:01.372

============ 46 test cases: 3 failed, 42 succeeded in 00:00:01.372 ============
```

**Finding:** broke case 1 as required, **plus** case 4 and case 6's first sub-assertion -- both also call `eprom_worst_pulses`/`eprom_block_budget_s` with `energy_cap_us == 0` (0x07/0x08's shipped value). No case failed to go RED.

### Plant 3 -- overprogram term stubbed to zero (`eprom_overprogram_us(...)` call -> literal `0U`)

Targets case 4 only -- the plan's own prediction that this is the *only* reachable proof.

```
...
test/native/avr/test_loop_eprom_v131/test_loop_eprom_v131.cpp:1875: test_budget_uncapped_energy_cap_is_not_a_cap_at_zero	[PASSED]
test/native/avr/test_loop_eprom_v131/test_loop_eprom_v131.cpp:1876: test_budget_pulse_count_ceils_because_the_loop_tests_after_it_increments	[PASSED]
test/native/avr/test_loop_eprom_v131/test_loop_eprom_v131.cpp:1877: test_budget_0x0b_at_49999us_is_99998us_per_byte_not_50000	[PASSED]
test/native/avr/test_loop_eprom_v131/test_loop_eprom_v131.cpp:1760: test_budget_overprogram_term_is_zero_for_factor_zero_and_clamped_for_factor_three: Expected 100000 Was 25000. factor 3, cap 75000: overprogram term must come from CALLING eprom_overprogram_us (25*1000 pulse + 75000 overprogram) -- a literal 3*factor*pulse restatement would yield 25000+9000=34000, not 100000, an 8.3x under-estimate on the overprogram term	[FAILED]
test/native/avr/test_loop_eprom_v131/test_loop_eprom_v131.cpp:1879: test_budget_zero_pulse_width_never_divides_by_zero	[PASSED]
test/native/avr/test_loop_eprom_v131/test_loop_eprom_v131.cpp:1880: test_budget_block_seconds_matches_the_shipped_rows_and_is_padded	[PASSED]
Program received signal SIGHUP (Hangup)
- native_loop_v131:native/avr/test_loop_eprom_v131 [ERRORED] Took 1.38 seconds -

=================================== SUMMARY ===================================
Environment       Test                             Status    Duration
----------------  -------------------------------  --------  ------------
native_loop_v131  native/avr/test_loop_eprom_v131  ERRORED   00:00:01.375

============ 46 test cases: 1 failed, 44 succeeded in 00:00:01.375 ============
```

**Finding:** broke **only** case 4, cleanly -- confirming the plan's own claim that the factor-3 assertions are the sole reachable proof the overprogram term is wired to the real function at all, since every shipped row's `overprogram_factor == 0` makes the term's output identical (`0`) whether it is called or stubbed.

### Plant 4 -- `pulse_us == 0U` guard arm removed (`... || pulse_us == 0U` deleted)

Targets case 5 -- the plan explicitly anticipates "crash or return a wrong value."

```
...
test/native/avr/test_loop_eprom_v131/test_loop_eprom_v131.cpp:1875: test_budget_uncapped_energy_cap_is_not_a_cap_at_zero	[PASSED]
test/native/avr/test_loop_eprom_v131/test_loop_eprom_v131.cpp:1876: test_budget_pulse_count_ceils_because_the_loop_tests_after_it_increments	[PASSED]
test/native/avr/test_loop_eprom_v131/test_loop_eprom_v131.cpp:1877: test_budget_0x0b_at_49999us_is_99998us_per_byte_not_50000	[PASSED]
test/native/avr/test_loop_eprom_v131/test_loop_eprom_v131.cpp:1878: test_budget_overprogram_term_is_zero_for_factor_zero_and_clamped_for_factor_three	[PASSED]
Program received signal SIGFPE (Floating point exception)
- native_loop_v131:native/avr/test_loop_eprom_v131 [ERRORED] Took 1.29 seconds -

=================================== SUMMARY ===================================
Environment       Test                             Status    Duration
----------------  -------------------------------  --------  ------------
native_loop_v131  native/avr/test_loop_eprom_v131  ERRORED   00:00:01.294

================= 44 test cases: 43 succeeded in 00:00:01.294 =================
```

**Finding:** case 5 (`test_budget_zero_pulse_width_never_divides_by_zero`) genuinely **crashes** the test binary with `SIGFPE` (integer division by zero, `50000 / 0`) partway through, exactly as the plan anticipated. Case 6 never gets a chance to run in this invocation because the whole process dies -- this is the crash outcome, not a graceful per-assertion failure, and it is the strongest possible proof that the guard is load-bearing.

### Plant 5 -- padding multiplier dropped (`raw_s * 2UL + 2UL` -> `raw_s + 2UL`)

Targets case 6 only.

```
...
test/native/avr/test_loop_eprom_v131/test_loop_eprom_v131.cpp:1875: test_budget_uncapped_energy_cap_is_not_a_cap_at_zero	[PASSED]
test/native/avr/test_loop_eprom_v131/test_loop_eprom_v131.cpp:1876: test_budget_pulse_count_ceils_because_the_loop_tests_after_it_increments	[PASSED]
test/native/avr/test_loop_eprom_v131/test_loop_eprom_v131.cpp:1877: test_budget_0x0b_at_49999us_is_99998us_per_byte_not_50000	[PASSED]
test/native/avr/test_loop_eprom_v131/test_loop_eprom_v131.cpp:1878: test_budget_overprogram_term_is_zero_for_factor_zero_and_clamped_for_factor_three	[PASSED]
test/native/avr/test_loop_eprom_v131/test_loop_eprom_v131.cpp:1879: test_budget_zero_pulse_width_never_divides_by_zero	[PASSED]
test/native/avr/test_loop_eprom_v131/test_loop_eprom_v131.cpp:1789: test_budget_block_seconds_matches_the_shipped_rows_and_is_padded: Expected 8 Was 5. 0x07 @ 100us/1024B: raw 2.5s ceils to 3s, padded x2+2 == 8	[FAILED]
Program received signal SIGHUP (Hangup)
- native_loop_v131:native/avr/test_loop_eprom_v131 [ERRORED] Took 1.45 seconds -

=================================== SUMMARY ===================================
Environment       Test                             Status    Duration
----------------  -------------------------------  --------  ------------
native_loop_v131  native/avr/test_loop_eprom_v131  ERRORED   00:00:01.451

============ 46 test cases: 1 failed, 44 succeeded in 00:00:01.451 ===========
```

**Finding:** broke **only** case 6, cleanly -- none of cases 1-5 call `eprom_block_budget_s`, so the padding rule is fully isolated to this one case, as expected.

### Final GREEN (all five plants reverted; `git diff` against the committed file is empty)

```
...
test/native/avr/test_loop_eprom_v131/test_loop_eprom_v131.cpp:1875: test_budget_uncapped_energy_cap_is_not_a_cap_at_zero	[PASSED]
test/native/avr/test_loop_eprom_v131/test_loop_eprom_v131.cpp:1876: test_budget_pulse_count_ceils_because_the_loop_tests_after_it_increments	[PASSED]
test/native/avr/test_loop_eprom_v131/test_loop_eprom_v131.cpp:1877: test_budget_0x0b_at_49999us_is_99998us_per_byte_not_50000	[PASSED]
test/native/avr/test_loop_eprom_v131/test_loop_eprom_v131.cpp:1878: test_budget_overprogram_term_is_zero_for_factor_zero_and_clamped_for_factor_three	[PASSED]
test/native/avr/test_loop_eprom_v131/test_loop_eprom_v131.cpp:1879: test_budget_zero_pulse_width_never_divides_by_zero	[PASSED]
test/native/avr/test_loop_eprom_v131/test_loop_eprom_v131.cpp:1880: test_budget_block_seconds_matches_the_shipped_rows_and_is_padded	[PASSED]
- native_loop_v131:native/avr/test_loop_eprom_v131 [PASSED] Took 1.51 seconds -

=================================== SUMMARY ===================================
Environment       Test                             Status    Duration
----------------  -------------------------------  --------  ------------
native_loop_v131  native/avr/test_loop_eprom_v131  PASSED    00:00:01.508
================= 45 test cases: 45 succeeded in 00:00:01.508 =================
```

**No `ERRORED`, no `SIGABRT`, no signal at all** -- clean PASSED, satisfying the task's own acceptance criterion literally. Every named case (1 through 6) went RED under its designated plant (or crashed, for case 5, as anticipated) and GREEN once reverted; none required more than its named plant to demonstrate the correction.

## Verification Results (final state, all reverted)

| Check | Result |
|---|---|
| `pio test -e native_loop_v131 -f "*test_loop_eprom_v131*"` | `PASSED`, 45 test cases: 45 succeeded (was 39 before this plan) |
| `pio test -e native_loop_v131` (both suites, bare) | 77 test cases: 77 succeeded (`test_loop_eprom_v131` 45 + `test_vpp_eprom_v131` 32; was 71 before this plan) |
| `pio test -e native` | 141 test cases: 141 succeeded, 17 suites -- unmoved |
| `pio test -e native_nodevtools` | 141 test cases: 141 succeeded, 17 suites -- unmoved |
| `pio run -e uno` | SUCCESS; RAM 76.8%, Flash 76.2% (24568/32256 B) |
| `pio run -e uno328pb` | SUCCESS; RAM 77.1%, Flash 76.0% (24618/32384 B) |
| `pio run -e leonardo` | SUCCESS; RAM 78.7%, Flash 92.6% (26542/28672 B) -- under the ceiling, D-22 |
| `python3 scripts/check_build_warnings.py --rebuild` (COLD -- `.pio/build/native*` removed first) | `PASS`: `uno`/`uno328pb`/`leonardo` macro_redefinition=0; `native`/`native_nodevtools` total warnings=1166 (== watermark 1166) |
| `python3 scripts/check_cmake_manifest.py` | `PASS`: 28 enforced sources resolved; allow-listed omissions unchanged |
| `git status --porcelain` in `/workspaces/firestarter` | clean (before running the pytest suite, per L-1) |
| `python3 -m pytest tests/ -o addopts="" -q` | **272 passed** |
| `git diff` on `src/proms/eprom_budget.cpp` after all five plants | empty -- byte-identical to the committed version |
| `git diff -- test/native/avr/test_loop_eprom_v131/test_loop_eprom_v131.cpp` | 134 insertions, 0 deletions -- `setUp`/`tearDown`/the `millis` mock/every pre-existing case untouched |
| `git diff --exit-code -- platformio.ini scripts/baseline/size_baseline.json` | clean, no changes |
| `native_trace_v131` | not run, not mentioned as fixed, per D-24 |

## Issues Encountered

- **Native-warning count measurement is cache-sensitive (Pitfall 9, already documented in 143-RESEARCH.md).** The very first `check_build_warnings.py --rebuild` run (right after committing task 1) reported native/native_nodevtools at exactly 1166 (COLD, matching the watermark). A second run later in the session -- after I had personally run `pio test -e native`/`-e native_nodevtools` in between, warming the build cache -- reported 998 (`size_baseline.json`'s documented WARM figure exactly). This is not a regression: `check_build_warnings.py`'s `_rebuild_native` helper runs `pio test -e <env>` without a preceding clean (unlike its AVR counterpart, which does clean first), so a warm PlatformIO build cache skips recompiling unchanged `src/proms/*.o` files and their warnings. Resolved by explicitly removing `.pio/build/native` and `.pio/build/native_nodevtools` before the final, authoritative measurement, which reproduced exactly 1166 on both envs. No code change; a measurement-methodology note only.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- The firmware half of HOST-01 (the budget arithmetic itself) is complete and proven; plan 143-10 flips the `HOST-*` requirement checkboxes once every plan's evidence exists. This plan intentionally marks no requirement Complete (frontmatter `requirements: []`).
- `eprom_block_budget_s` is ready to be called from the wire-emission site (`MSG_OK_READY`'s CAP-03 extension) in a later plan in this phase (143-03 per the phase's artifact map) -- nothing here wires it onto the wire yet; this plan is arithmetic-only, no wire change, no ack change, no `eprom.cpp` edit, exactly as scoped.
- `include/eprom_budget.h`'s `[ASSUMED]` per-pulse overhead figure (20-60 us, RESEARCH A1) remains unmeasured; Phase 145 may record the real number, per the header's own note.
- No blockers. All pinned artifacts (`platformio.ini`, `size_baseline.json`, `eprom.cpp`, `eprom_params.cpp`, `tests/golden/protocol_branch_inventory.json`) are untouched, confirmed by `git diff --exit-code`.

## Self-Check: PASSED

- FOUND: `firestarter/include/eprom_budget.h`
- FOUND: `firestarter/src/proms/eprom_budget.cpp`
- FOUND: `firestarter/test/native/avr/test_loop_eprom_v131/test_loop_eprom_v131.cpp`
- FOUND: `firestarter/platform/py32f071/CMakeLists.txt`
- FOUND commit `f1b17cd` (Task 1)
- FOUND commit `610cb01` (Task 2)
- FOUND commit `e9f6a92` (Rule 3 deviation)

---
*Phase: 143-host-timeout-progress-pulse-override*
*Completed: 2026-08-12*
