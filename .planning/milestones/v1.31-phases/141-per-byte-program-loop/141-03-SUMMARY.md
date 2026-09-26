---
phase: 141-per-byte-program-loop
plan: 03
subsystem: firmware
tags: [firmware, native-test, platformio, unity, arduinofake, host-stubs, gh-15]

# Dependency graph
requires: []
provides:
  - "A sixth native PlatformIO env, [env:native_loop_v131], compiling+running test/native/avr/test_loop_eprom_v131 by name -- absent from default_envs and from both pinned envs' test_filter/build_flags, never fed to check_size_baseline.py or check_build_warnings.py, no CI leg in either repo (run-by-name obligation)"
  - "host_stubs.cpp composing HOST_STUBS_REAL_REGISTER_UTILS + HOST_STUBS_RECORD_TIMING + HOST_STUBS_CUSTOM_READ_DATA_BUFFER (in that order) plus rurp_register_utils.h included AFTER the shared .inc, so production's real cache-elision/latch-strobe sequencing runs"
  - "A 16-bit-latched-address-keyed, uint16_t-countered read-back model (loop_readback_reset/seed/reads/seeded_count + rurp_read_data_buffer) that represents an uncapped per-byte pulse count and a block crossing the A16 boundary -- a deliberate departure from the trace suite's 4-entry, base-0-only '& 0x03' index"
  - "A strong rurp_log_id override (clear_logged_ids/logged_id_count/_at/_param_count/_param/_overflowed) capturing every logged message id and its packed params"
  - "A fixed drive-helper contract (make_loop_handle + drive_loop_write + LOOP_BUS_CONFIG_0x07/_0x08/_0x0B), authored ahead of use and left [[maybe_unused]], for plans 141-07/141-08 to extend this same test file against"
  - "Six loop-independent harness cases (incl. two negative controls) proving the harness itself is non-vacuous, true both before and after plan 141-04's loop rewrite"
affects: [141-04-loop-rewrite, 141-07-loop-cases, 141-08-dip32-overprogram-cases, 141-09-requirement-flip]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "16-bit-latched-address key (LSB | MSB<<8) for a chip read-back model, instead of a 4-entry '& 0x03' index -- needed whenever a model must represent an uncapped per-byte read/pulse count or a block that crosses the A16 boundary (bit 16 lives in CONTROL, not in the LSB/MSB latches, for the 32-pin config)"
    - "Sixth-native-env, named-suite-only precedent (native_params_v131 lineage): test_filter names only the new suite, never folded into a pinned env, absent from default_envs, excluded from both check_size_baseline.py and check_build_warnings.py by design, no CI leg -- counts are a run-by-name obligation recorded in the phase record/SUMMARY, never implied as CI coverage"
    - "Authored-ahead, currently-unused test infrastructure ([[maybe_unused]] on the helper functions and bus_config literals) so a later plan extending the SAME test file inherits a fixed, already-reviewed contract instead of re-deriving one"

key-files:
  created:
    - firestarter/test/native/avr/test_loop_eprom_v131/host_stubs.cpp
    - firestarter/test/native/avr/test_loop_eprom_v131/test_loop_eprom_v131.cpp
  modified:
    - firestarter/platformio.ini
    - firestarter/CLAUDE.md

key-decisions:
  - "Declared the six-strobe/six-timing shared-.inc accessor prototypes (strobe_count, timing_count, etc.) directly inside test_loop_eprom_v131.cpp rather than authoring a new shared '_expected.h'-style header -- this plan's task list names only two new files, and plans 141-07/141-08 extend this SAME .cpp (not a new file), so declaring them once here gives every later case in this file the full set from a single place."
  - "loop_readback_seed re-seeds in place (resets read_count, updates target/converge_after) when called twice for the same address within one case, rather than only ever appending -- an unspecified-but-safe elaboration of the plan's contract that does not change any of the six required cases' behavior."
  - "Marked make_loop_handle, drive_loop_write and the three LOOP_BUS_CONFIG_0x07/_0x08/_0x0B literals [[maybe_unused]] (C++17 standard attribute) rather than any GCC-specific idiom -- no existing in-tree precedent for 'authored but not yet called' test infrastructure was found via search, so the portable standard attribute was chosen; all four are genuinely unused by this plan's own six cases by design (they exist for plans 141-07/141-08)."

requirements-completed: []

coverage:
  - id: D1
    description: "A sixth native PlatformIO env ([env:native_loop_v131]) compiles and runs test/native/avr/test_loop_eprom_v131 by name, absent from default_envs and from both pinned envs' test_filter/build_flags"
    verification:
      - kind: integration
        ref: "pio test -e native_loop_v131 -> 6 test cases in 1 suite, all PASSED"
        status: pass
      - kind: other
        ref: "python3 configparser assertions: env:native_loop_v131 present, test_filter == ['native/avr/test_loop_eprom_v131'], not in default_envs, build_src_filter byte-identical to native_params_v131's, build_flags inherits ${env:native.build_flags} + its own -I entry, neither env:native nor env:native_nodevtools names test_loop_eprom_v131 in test_filter or build_flags -> 'OK sixth env wired, pinned envs untouched'"
        status: pass
    human_judgment: false
  - id: D2
    description: "The suite composes HOST_STUBS_REAL_REGISTER_UTILS (ordered strobe recorder) with production's REAL rurp_register_utils.h (included AFTER the shared .inc), so the cache-elision + latch-strobe sequencing this suite drives is the genuine article, not a replica"
    verification:
      - kind: other
        ref: "host_stubs.cpp Task 1 verify script: all three HOST_STUBS_* guards defined before the .inc include; #include \"rurp_register_utils.h\" appears after it; narrower HOST_STUBS_CUSTOM_HW_REVISION guard absent -> 'OK host_stubs.cpp 281 lines'"
        status: pass
      - kind: integration
        ref: "pio test -e native_loop_v131 links and runs successfully against the real rurp_register_utils.h + rurp_hw_rev_utils.h (transitively) -- a link/compile failure would result if the composition were wrong"
        status: pass
    human_judgment: false
  - id: D3
    description: "The suite records the argument of every mocked delay and delayMicroseconds call, in order, via the setUp() AlwaysDo hooks into timing_push"
    verification:
      - kind: unit
        ref: "test_loop_eprom_v131.cpp::test_timing_hook_records_both_delay_kinds_with_their_arguments -- delay(7) then delayMicroseconds(11) produce two ordered entries with the correct kind and us value each"
        status: pass
    human_judgment: false
  - id: D4
    description: "The suite models chip read-back per 16-bit latched address (LSB | MSB<<8), with uint16_t counters, so a per-byte pulse count is observable without the 4-byte/base-0/'& 0x03' cap, including across an A16 boundary"
    verification:
      - kind: unit
        ref: "test_loop_eprom_v131.cpp::test_readback_model_returns_ff_until_converge_then_the_target (positive case, converge_after=2 -> 3 reads)"
        status: pass
      - kind: unit
        ref: "test_loop_eprom_v131.cpp::test_readback_model_returns_ff_and_stays_unseeded_for_an_unknown_address (negative control: -1 reads, seeded_count stays 1)"
        status: pass
      - kind: unit
        ref: "test_loop_eprom_v131.cpp::test_readback_model_distinguishes_two_addresses_across_an_a16_crossing (0xFFFE and 0x0000 keep independent counters, 2 and 3 reads respectively)"
        status: pass
    human_judgment: false
  - id: D5
    description: "The suite captures every logged message id and its packed parameters via a strong rurp_log_id override"
    verification:
      - kind: unit
        ref: "test_loop_eprom_v131.cpp::test_logged_id_capture_records_the_id_and_its_packed_params -- rurp_log_id_u24(0xB1, 0x012345) captured as id 0xB1, param_count 3, params {0x01,0x23,0x45}"
        status: pass
    human_judgment: false
  - id: D6
    description: "native and native_nodevtools still report exactly 141 cases across 17 suites after this plan's change"
    verification:
      - kind: integration
        ref: "pio test -e native -> 141 test cases: 141 succeeded (17 suites)"
        status: pass
      - kind: integration
        ref: "pio test -e native_nodevtools -> 141 test cases: 141 succeeded (17 suites)"
        status: pass
    human_judgment: false

duration: 30min
completed: 2026-08-10
status: complete
---

# Phase 141 Plan 03: Native Per-Byte Loop Oracle (Sixth Env + Suite) Summary

**New `[env:native_loop_v131]` plus `test_loop_eprom_v131/` (host_stubs.cpp + test_loop_eprom_v131.cpp): a 16-bit-latched-address read-back model, a strong logged-id capture, and a fixed drive-helper contract for plans 141-04/141-07/141-08 -- six loop-independent harness cases green, both pinned native envs still exactly 141/17, zero AVR flash delta.**

## Performance

- **Duration:** 30 min
- **Started:** 2026-08-10T15:11:46Z
- **Completed:** 2026-08-10T15:41:00Z
- **Tasks:** 3
- **Files modified:** 4 (2 created, 2 modified)

## Accomplishments
- Authored `test/native/avr/test_loop_eprom_v131/host_stubs.cpp` (281 lines): composes `HOST_STUBS_REAL_REGISTER_UTILS` + `HOST_STUBS_RECORD_TIMING` + `HOST_STUBS_CUSTOM_READ_DATA_BUFFER` in the required order before the shared `.inc`, includes the real `rurp_register_utils.h` afterwards, and adds a 16-bit-latched-address-keyed, `uint16_t`-countered read-back model plus a strong `rurp_log_id` override -- both new to this suite and neither present in any sibling suite.
- Authored `test/native/avr/test_loop_eprom_v131/test_loop_eprom_v131.cpp` (400 lines): `setUp()` wiring all three recorder layers; `make_loop_handle` + `drive_loop_write` (a fixed contract for plans 141-07/141-08, which extend this same file); the three `LOOP_BUS_CONFIG_0x07/_0x08/_0x0B` literals copied byte-for-byte from the trace suite; and six loop-independent harness cases (including two explicit negative controls) proving the harness itself is non-vacuous.
- Added `[env:native_loop_v131]` to `platformio.ini` on the `native_params_v131` precedent: names only its own suite, absent from `default_envs`, `build_src_filter` byte-identical to the sibling native envs, comment block states all four HARD CONSTRAINTs (never folded into a pinned env; not in `default_envs`; never fed to either check script; no CI leg in either repo).
- Extended `CLAUDE.md`'s "Exception (Phase 140 D-11)" paragraph to name both `native_params_v131` and `native_loop_v131`, so the general "add to both pinned envs" instruction directly above does not read as still binding for the new suite.
- Verified end to end: `pio test -e native_loop_v131` (6/6 passing, 140 warnings -- all pre-existing ArduinoFake/`rurp_platform_compat.h` macro-redefinition noise, zero new unused-function/variable warnings after marking the authored-ahead helpers `[[maybe_unused]]`); `pio test -e native` and `-e native_nodevtools` (141/141 each, 17 suites, unaffected); `pio test -e native_trace_v131` (5/5, unaffected); `pio run -e uno` (SUCCESS, 24002 B flash -- byte-identical to the pre-plan figure); `python3 -m pytest tests/ -q -o addopts=""` (244 passed).

## Task Commits

Each task was committed atomically, inside `/workspaces/firestarter` on branch `gsd/v1.31-27c-programming-algorithm-fidelity`:

1. **Task 1: Author host_stubs.cpp -- three recorder layers, a 16-bit-keyed read-back model, logged-id capture** - `927e069` (test)
2. **Task 2: Author the suite skeleton -- setUp hooks, the drive helper contract, six loop-independent harness cases** - `60ed0e5` (test)
   - Deviation fix (see below) - `05f980c` (fix)
3. **Task 3: Add [env:native_loop_v131] and extend CLAUDE.md's pinned-env exception** - `6029423` (feat)

**Plan metadata:** pending (docs: complete plan, this SUMMARY + STATE.md + ROADMAP.md, meta repo)

## Files Created/Modified
- `firestarter/test/native/avr/test_loop_eprom_v131/host_stubs.cpp` - three composed recorder layers, the 16-bit-keyed read-back model, strong `rurp_log_id` override
- `firestarter/test/native/avr/test_loop_eprom_v131/test_loop_eprom_v131.cpp` - setUp hooks, `make_loop_handle`/`drive_loop_write`, three bus_config literals, six harness cases, explicit `RUN_TEST` main
- `firestarter/platformio.ini` - new `[env:native_loop_v131]` section
- `firestarter/CLAUDE.md` - extended the pinned-env exception paragraph to name the new env

## Decisions Made
- Declared the shared strobe/timing accessor prototypes directly in `test_loop_eprom_v131.cpp` (no new shared header authored) -- see key-decisions in frontmatter for the full rationale.
- `loop_readback_seed` re-seeds in place on a repeat call for the same address within one case (an unspecified-but-safe elaboration; does not change any of the six cases' asserted behavior).
- Used the C++17 `[[maybe_unused]]` standard attribute (no in-tree precedent existed) to silence the expected unused-function/variable warnings on the authored-ahead-of-use helpers and bus_config literals, per the plan's explicit "silence... rather than deleting" instruction.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Accidental early comment-close broke compilation of test_loop_eprom_v131.cpp**
- **Found during:** Task 3's verification (`pio test -e native_loop_v131`), first build attempt
- **Issue:** A doc comment above `reset_register_cache`'s declaration read `(loop_readback_*/logged_id_*)` -- the trailing `_*` immediately followed by `/` forms a literal `*/` token, closing the C-style comment early. Everything from `logged_id_*) are new to this suite...` onward became live (uncommented) source text, which failed to compile: `'logged_id_' does not name a type`, and `'reset_register_cache' was not declared in this scope` at every call site (its own `extern "C"` declaration, two lines later, had been swallowed by the same broken comment).
- **Fix:** Reworded the sentence to name both symbol families in prose ("the `loop_readback_` and `logged_id_` families") without ever producing the `*/` substring.
- **Files modified:** `firestarter/test/native/avr/test_loop_eprom_v131/test_loop_eprom_v131.cpp` (comment text only)
- **Verification:** `pio test -e native_loop_v131` re-run -> 6/6 passing. Re-scanned both new files for the same hazard (`grep -n '[a-zA-Z0-9_]\*/'`) -> no further occurrences.
- **Committed in:** `05f980c` (separate fix commit, since the bug was discovered only once Task 3 attempted the first real build of Task 2's file)

---

**Total deviations:** 1 auto-fixed (1 bug -- a self-inflicted authoring mistake in a comment, not a plan defect)
**Impact on plan:** Zero impact on delivered behavior, scope, or suite content -- a comment-wording fix only, caught by the very first build attempt and re-verified against the full task 3 verification chain.

## Issues Encountered
None beyond the deviation above.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Plan 141-04 (the loop rewrite in `eprom.cpp`) can now be verified against a real oracle: `native_loop_v131` compiles and links against production's real register-utils path, and `native_trace_v131` is confirmed still green today (it is expected to go RED once 141-04 lands, per D-10 -- that is not a regression).
- Plans 141-07 and 141-08 (which both declare `files_modified: [.../test_loop_eprom_v131.cpp]`, extending this same file) inherit a fixed, already-reviewed contract: `make_loop_handle`, `drive_loop_write`, and `LOOP_BUS_CONFIG_0x07/_0x08/_0x0B`, plus the full six-strobe/six-timing accessor declarations and the four kind/cap constants, all already in place and unused-warning-clean.
- The read-back model's read-count-to-pulse-count mapping (`converge_after = N` pulses matched on read `N+1`) is documented in `host_stubs.cpp` and is the exact contract plan 141-07's "per-byte pulse count is exactly the number the read-back model was seeded to require" truth depends on.
- `native_loop_v131` runs in **no CI leg of either repository** -- this is a run-by-name obligation for every future invocation, recorded here and in `platformio.ini`'s own comment block and `CLAUDE.md`'s exception paragraph. Both pinned envs (`native`, `native_nodevtools`) remain at exactly 141 cases / 17 suites.
- No requirements were flipped (frontmatter `requirements: []`, honored) -- LOOP-01..08 stay `[ ]` until plan 141-09's evidence-complete hand edit.

---
*Phase: 141-per-byte-program-loop*
*Completed: 2026-08-10*

## Self-Check: PASSED

- FOUND: firestarter/test/native/avr/test_loop_eprom_v131/host_stubs.cpp
- FOUND: firestarter/test/native/avr/test_loop_eprom_v131/test_loop_eprom_v131.cpp
- FOUND: firestarter/platformio.ini
- FOUND: firestarter/CLAUDE.md
- FOUND: .planning/phases/141-per-byte-program-loop/141-03-SUMMARY.md
- FOUND: 927e069 (git -C firestarter log --oneline --all)
- FOUND: 60ed0e5 (git -C firestarter log --oneline --all)
- FOUND: 05f980c (git -C firestarter log --oneline --all)
- FOUND: 6029423 (git -C firestarter log --oneline --all)
