---
phase: 201-a-partial-write-is-gated-on-its-own-region
plan: 01
subsystem: testing
tags: [firmware, native-tests, blank-check, harness, unity, platformio]

# Dependency graph
requires:
  - phase: 201-RESEARCH
    provides: the modulo-16 aliasing defect (Open Question 4) and the D-15.1/D-15.2 contract text
provides:
  - An address-keyed (opt-in) read-back model in test_val_eprom's host_stubs.cpp, proven by a
    positive control not to alias modulo 16 — the harness plan 201-02's D-16.1 test needs.
  - Two native characterization tests pinning mem_util_blank_check's multi-call chunking contract
    (D-15.1) and CMD_ERASE's erase-end scan-from-zero arm (D-15.2), written against unmodified
    memory.cpp/eprom.cpp before the region split lands in plans 201-03/201-04.
affects: [201-02, 201-03, 201-04]

actuals:
  tokens: 4524
  tasks: 2
  commits: 3
  plan_head_before: a050730dbf2b4be8e52506e720b54659c018f215

tech-stack:
  added: []
  patterns:
    - "Opt-in shadow read-back model layered in front of an existing stub model (val_shadow_reset/enable/seed), so pre-existing cases stay byte-for-byte unaffected when it stays off."

key-files:
  created: []
  modified:
    - firestarter_fw/test/native/avr/test_val_eprom/host_stubs.cpp
    - firestarter_fw/test/native/avr/test_val_eprom/test_val_eprom.cpp

key-decisions:
  - "Substituted CONTROL_REGISTER for the plan's 'TOP_ADDRESS' register, which does not exist anywhere in this repository — production writes the top address bits (address bits 16-18) to CONTROL_REGISTER (mem_util_calculate_top_address_register), not to a dedicated third register."
  - "Added h.bus_config = VAL_EPROM_BUS_CONFIG_0x07 to both the Task 1 positive-control fixture and the new make_region_handle factory, though neither was listed in the plan's action text. A zero-initialized bus_config is degenerate (mem_util_remap_address_bus collapses every address to the same physical line), not an identity remap, per the file's own existing comment on VAL_EPROM_BUS_CONFIG_0x07 — without it the positive control could not distinguish 0x10 from 0x20/0x30/0x1010."
  - "Corrected the plan's HOST_STUBS_MAX_RECORDING=256 assumption to the measured, compiled value of 4096 (the shared host_stubs_common.inc default; this suite does not override it). A comment elsewhere in host_stubs.cpp states 256 but is stale and does not reflect the compiled macro."
  - "test_erase_end_blank_check_scans_from_zero asserts val_recording_saturated() is TRUE, not FALSE as the plan's action text specified. Measured fact: a single mem_util_blank_check call over a 16384-byte part scans one full 8192-byte BLANK_CHECK_CHUNK_SIZE chunk in that one call — 8192 * 3 = 24576 register writes, far past the 4096-entry recorder cap — so saturation is unavoidable regardless of chunk contents. This does not weaken the test: first_recorded_address() only needs the earliest occurrence of each register, and the recorder's own documented saturation behavior drops only the tail, keeping the prefix (and therefore the address-0 composition) valid."

requirements-completed: [BLANK-02]

coverage:
  - id: D1
    description: "Address-keyed shadow read-back model in host_stubs.cpp, proven by a positive control not to alias modulo 16 like the pre-existing 16-slot model."
    requirement: BLANK-02
    verification:
      - kind: unit
        ref: "test/native/avr/test_val_eprom/test_val_eprom.cpp#test_shadow_seed_is_address_keyed_not_modulo_aliased"
        status: pass
    human_judgment: false
  - id: D2
    description: "BLANK-02 chunking (D-15.1) and erase-end scan-from-zero (D-15.2) contracts pinned against unmodified firmware, before the region split lands."
    requirement: BLANK-02
    verification:
      - kind: unit
        ref: "test/native/avr/test_val_eprom/test_val_eprom.cpp#test_blank_check_resumes_across_chunks_and_restores_the_cursor"
        status: pass
      - kind: unit
        ref: "test/native/avr/test_val_eprom/test_val_eprom.cpp#test_erase_end_blank_check_scans_from_zero"
        status: pass
    human_judgment: false

duration: 55min
completed: 2026-09-19
status: complete
---

# Phase 201 Plan 01: Address-Keyed Shadow Model + BLANK-02 Contract Freeze Summary

**Extended `test_val_eprom`'s native harness with an address-keyed read-back model (proven non-aliased by a positive control) and froze the two BLANK-02 whole-device behaviours against unmodified firmware — zero production source changed.**

## Performance

- **Duration:** 55 min
- **Started:** 2026-09-19T23:04:00Z (approx, based on session start)
- **Completed:** 2026-09-19T23:58:58Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments
- The native suite can now express "non-blank at exactly one absolute address" without modulo-16 aliasing, proved by `test_shadow_seed_is_address_keyed_not_modulo_aliased` (a positive control, not an assertion of the harness's own correctness).
- `test_blank_check_resumes_across_chunks_and_restores_the_cursor` pins the multi-call chunking contract (D-15.1): three calls to `mem_util_blank_check` over a 16384-byte part advance the cursor by exactly one `BLANK_CHECK_CHUNK_SIZE` (8192) per call and restore `handle->address` to its pre-call value (0x2A) on completion — not zero.
- `test_erase_end_blank_check_scans_from_zero` pins the erase-end arm (D-15.2): `CMD_ERASE`'s `firestarter_operation_end` always scans from address 0, even with `handle->address` seeded to 8000 beforehand.
- Both pinned native environments (`native`, `native_nodevtools`) went from a measured 232 to 235 succeeding cases, 0 failed, at every step of this plan.

## Task Commits

Each task was committed atomically, inside the `firestarter_fw` submodule on `v1.40-program-parameter-fidelity`:

1. **Task 1: Address-keyed shadow read-back model + positive control** - `35de4fc` (test)
2. **Task 2: BLANK-02 chunking and erase-end contract freeze** - `a7746d0` (test)

**Meta-repository gitlink advance:** `d5256603` (test) — `firestarter_fw` pointer moved from `a050730d` to `a7746d0c` in `/workspaces` on `v1.40-program-parameter-fidelity`.

_Note: this plan's `<output>` also asked for a SUMMARY.md; that is this file, committed separately below._

## Files Created/Modified
- `firestarter_fw/test/native/avr/test_val_eprom/host_stubs.cpp` - Adds the address-keyed shadow model (`VAL_EPROM_SHADOW_SIZE`, `val_shadow_reset/enable/seed`, and a shadow-first branch in `rurp_read_data_buffer`), with a saturation fallback via `s_val_last_address`. Legacy 16-slot model untouched.
- `firestarter_fw/test/native/avr/test_val_eprom/test_val_eprom.cpp` - Adds three `extern "C"` prototypes and a `val_shadow_reset()` call in `setUp`; adds `test_shadow_seed_is_address_keyed_not_modulo_aliased`; adds `make_region_handle`, `first_recorded_address`, `test_blank_check_resumes_across_chunks_and_restores_the_cursor`, `test_erase_end_blank_check_scans_from_zero`; adds `#include "eprom.h"` / `#include "operation_utils.h"`.

## Decisions Made
- See `key-decisions` in frontmatter for the four substantive deviations (CONTROL_REGISTER for the non-existent "TOP_ADDRESS", the required `bus_config` addition to two fixtures, the corrected `HOST_STUBS_MAX_RECORDING` value, and the corrected saturation-true assertion). All four are measured facts about the actual codebase that the plan's prose got wrong or omitted; none is an architectural change, and none touches production source.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] "TOP_ADDRESS" register does not exist; substituted CONTROL_REGISTER**
- **Found during:** Task 1 (read_first review of the register enum)
- **Issue:** The plan's action and read_first text names a register `TOP_ADDRESS` for the third component of the absolute-address composition (`lsb | (msb << 8) | ((top & 0x07) << 16)`). No such symbol exists anywhere in the repository (`git grep -n "TOP_ADDRESS"` returns nothing). Production writes the top address bits to `CONTROL_REGISTER` (`mem_util_calculate_top_address_register`, called from `mem_util_set_address`, `memory.cpp`), mixed with unrelated VPP-route preserve bits.
- **Fix:** Scanned `CONTROL_REGISTER` writes in that role instead. For every address this suite drives through the shadow (< 65536), production's own top-address expression (`(address >> 16) & mask`) is structurally 0, so this substitution recovers exactly the same (zero) contribution the plan's formula expected — verified by both new tests passing and by the `test_shadow_seed_is_address_keyed_not_modulo_aliased` control specifically.
- **Files modified:** `host_stubs.cpp`, `test_val_eprom.cpp` (documented inline at both use sites)
- **Verification:** `pio test -e native` / `-e native_nodevtools` both 235/235
- **Committed in:** `35de4fc`, `a7746d0`

**2. [Rule 2 - Missing Critical] Added `bus_config = VAL_EPROM_BUS_CONFIG_0x07` to two fixtures the plan omitted it from**
- **Found during:** Task 1 (tracing `mem_util_remap_address_bus` for a zero-initialized handle)
- **Issue:** The plan's action text for the Task 1 positive-control handle and for `make_region_handle` lists `protocol`, `cmd`, `mem_size`, `ctrl_flags`, `chip_id`, `vpp_mv` but not `bus_config`. A zero-initialized `bus_config` is not an identity address map — `mem_util_remap_address_bus`'s per-line remap loop and its unconditional `rw_line`/`vpp_line` OR-in collapse every address passed to it onto the same physical line, regardless of the address argument. Without this fix, the Task 1 positive control could not have distinguished 0x10 from 0x20/0x30/0x1010, and the region tests could not have driven distinct addresses either.
- **Fix:** Set `h.bus_config = VAL_EPROM_BUS_CONFIG_0x07` (the suite's own pre-existing identity-mapped config, already used by `make_write_handle`) in both the Task 1 fixture and `make_region_handle`.
- **Files modified:** `test_val_eprom.cpp`
- **Verification:** `test_shadow_seed_is_address_keyed_not_modulo_aliased` passes and genuinely discriminates the four probe addresses.
- **Committed in:** `35de4fc`, `a7746d0`

**3. [Rule 1 - Bug] Corrected `HOST_STUBS_MAX_RECORDING` from the plan's stated 256 to the measured 4096**
- **Found during:** Task 2 (before writing the saturation assertion for the erase-end test)
- **Issue:** The plan's read_first and must_haves both state `HOST_STUBS_MAX_RECORDING` is 256, citing an in-file comment as verification. That comment (`host_stubs.cpp`, pre-existing, unrelated to this plan) is itself stale: the actual compiled value comes from `host_stubs_common.inc`'s `#ifndef HOST_STUBS_MAX_RECORDING #define HOST_STUBS_MAX_RECORDING 4096`, which this suite's `host_stubs.cpp` does not override, and no `-D HOST_STUBS_MAX_RECORDING` build flag exists in `platformio.ini` for these envs.
- **Fix:** Used the measured value (4096) when reasoning about saturation for the erase-end test's arithmetic (see deviation 4). Did not touch the stale pre-existing comment (out of scope — not introduced by this plan).
- **Files modified:** none (documentation-only correction in new comments added by this plan)
- **Verification:** Confirmed both native envs at 235/235 with the erase-end test's actual saturation state asserted as measured.
- **Committed in:** `a7746d0`

**4. [Rule 1 - Bug] `test_erase_end_blank_check_scans_from_zero` asserts saturation TRUE, not FALSE as planned**
- **Found during:** Task 2 (running the test for the first time)
- **Issue:** The plan's action text says to assert `val_recording_saturated()` is false for this case. Measured: one call to `mem_util_blank_check` over a 16384-byte part scans a full 8192-byte `BLANK_CHECK_CHUNK_SIZE` chunk in that single call (8192 × 3 registers/byte = 24576 write attempts), which saturates the 4096-entry recorder every time, regardless of chunk contents. This is a structural property of driving the real production chunking loop through a real dispatch entry point — it is not fixable by tuning the fixture without either shrinking `mem_size` below what Task 1's shared model expects, or writing fewer than a full chunk, contradicting the plan's own `make_region_handle(0x07, CMD_ERASE, 16384)` instruction.
- **Fix:** Asserted the measured fact (`val_recording_saturated()` is true) with a message explaining why, instead of the plan's stated expectation. This does not weaken the test: the plan's own PLAN.md acceptance_criteria for this specific case (as opposed to its action prose) does not require a saturation-false assertion — it requires the operation_end non-null check and the first-composed-address-is-0 check, both of which this test still performs and which the recorder's documented tail-drops/prefix-stays-valid saturation behavior does not threaten.
- **Files modified:** `test_val_eprom.cpp`
- **Verification:** `test_erase_end_blank_check_scans_from_zero` passes; `first_recorded_address()` returns 0 as required.
- **Committed in:** `a7746d0`

**5. [Rule 1 - Bug] Corrected the plan's own "outside_suite"/production-diff verify command, which fails closed even when clean**
- **Found during:** Task 1, running the plan's literal verify leg
- **Issue:** The plan's verify command `CHANGED=$(printf '%s\n' "$ALL" | grep -v '^test/...' | grep -v '^$')` reports a non-zero exit from the `CHANGED=...` assignment itself whenever the filtered result is genuinely empty, because the final `grep -v '^$'` finds zero matching lines on empty input and exits 1 — independent of whether any production file actually changed. This aborts the `&&` chain before the intended `test -z "$CHANGED"` check ever runs, so the command as written cannot report success even in the fully-passing case.
- **Fix:** Ran a corrected version (`... | grep -v '^$'; true`) to obtain the true, intended result. Confirmed at both checkpoints (after Task 1's commit and after Task 2's commit) that no files outside `test/native/avr/test_val_eprom/` changed, and separately confirmed `git diff --name-only <base>..HEAD -- src/ include/` (Task 2's verify leg, which has no such bug) is empty.
- **Files modified:** none (this is a defect in the plan's verify prose, not in shipped code)
- **Verification:** `git diff --name-only a050730d..a7746d0c` lists exactly the two files under `test/native/avr/test_val_eprom/`; `git diff --name-only a050730d..a7746d0c -- src/ include/` is empty.
- **Committed in:** N/A (verification-only finding)

---

**Total deviations:** 5 (2 Rule 3/blocking substitutions for a non-existent register/missing identity map, 2 Rule 1 bug corrections to the plan's own asserted expectations, 1 Rule 1 correction to the plan's own verify-command shell logic).
**Impact on plan:** All five were necessary to make the plan's own stated tests pass against the real, measured codebase. None changed production source, none is an architectural change, and none weakens what the tests actually prove — each is a correction of the plan's prose to match measured fact, applied inline and documented at the point of use in the source.

## Issues Encountered
None beyond the deviations documented above.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Plan 201-02 can now write its D-16.1 region-gated blank-check test using `val_shadow_reset/enable/seed` to seed a single absolute address without modulo-16 aliasing.
- Plans 201-03 and 201-04 have a tripwire: any change to `mem_util_blank_check`'s chunking or to `configure_eprom`'s `CMD_ERASE` → `firestarter_operation_end` assignment will now fail `test_blank_check_resumes_across_chunks_and_restores_the_cursor` or `test_erase_end_blank_check_scans_from_zero` immediately.
- No blockers. All three repositories remain on `v1.40-program-parameter-fidelity`.

## Self-Check: PASSED

- FOUND: `firestarter_fw/test/native/avr/test_val_eprom/host_stubs.cpp`
- FOUND: `firestarter_fw/test/native/avr/test_val_eprom/test_val_eprom.cpp`
- FOUND: commit `35de4fc` (`git -C firestarter_fw log --oneline --all`)
- FOUND: commit `a7746d0` (`git -C firestarter_fw log --oneline --all`)
- FOUND: commit `d5256603` (`git log --oneline --all`, meta repo gitlink advance)
- Re-ran acceptance criteria and plan-level `<verification>`: `pio test -e native` 235/235, `pio test -e native_nodevtools` 235/235, `FIRESTARTER_META_ROOT=/tmp/no-meta pytest tests/` 269 passed / 32 skipped / 0 failed, `git diff --name-only <base>..HEAD -- src/ include/` empty, `git -C firestarter_fw rev-parse --abbrev-ref HEAD` == `v1.40-program-parameter-fidelity`.

---
*Phase: 201-a-partial-write-is-gated-on-its-own-region*
*Completed: 2026-09-19*
