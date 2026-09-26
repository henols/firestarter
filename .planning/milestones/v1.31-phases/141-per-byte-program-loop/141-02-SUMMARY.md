---
phase: 141-per-byte-program-loop
plan: 02
subsystem: firmware
tags: [firmware, avr, delayMicroseconds, timing-safety, memory-utils, control-register, dip32, gh-15]

# Dependency graph
requires: []
provides:
  - "mem_util_split_delay(us, out_ms, out_us) + mem_util_delay_us(us): a 32-bit-safe microsecond delay helper with C linkage, declared in memory_utils.h and implemented beside the mem_util_calculate_* family in memory.cpp, gated by MEM_UTIL_DELAY_US_MAX (16383UL)"
  - "memory_set_data's program pulse rerouted from the unclamped delayMicroseconds(handle->pulse_delay) to mem_util_delay_us(handle->pulse_delay) -- LOOP-07 site 1 of 2 (D-06); closes a currently-reachable silently-short-pulse defect, not merely a Phase 143 pre-position"
  - "mem_util_calculate_top_address_register's pins<32 preserve-mask comment corrected to state the verified, revision-independent mechanism (the preserve mask itself, not a bit collision) and hand the DIP32 route choice to Phase 142 -- LOOP-08 groundwork (D-09)"
affects: [141-04-per-byte-loop-rewrite, 141-06-loop07-completion, 141-08-native-suite, 141-09-requirement-flip, 142-vpp-routing]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "32-bit split-delay pattern for any host-supplied timing value that could exceed AVR delayMicroseconds()'s 16383us ceiling: whole milliseconds via the 32-bit-safe delay(), sub-millisecond remainder (always <=999) via delayMicroseconds(); split fires strictly above the ceiling so every value at or below it is emitted unsplit and the existing trace does not move"
    - "Expose the pure split arithmetic (not static) so native tests -- which record no elapsed time -- can assert the ms/us split directly instead of only the (untestable) delay duration"

key-files:
  created: []
  modified:
    - firestarter/include/memory_utils.h
    - firestarter/src/proms/memory.cpp

key-decisions:
  - "Placed mem_util_split_delay / mem_util_delay_us physically between mem_util_calculate_top_address_register and mem_util_set_address in memory.cpp (next to the mem_util_calculate_* family, per the plan's action text) -- verified this does not interact badly with Task 2's own verify script, which slices the file from the top_address_register definition up to the next 'mem_util_set_address' occurrence"
  - "[Rule 3 - blocking] Reworded the new VPE-survives-verify comment sentence to avoid the literal substring 'mem_util_set_address': the first draft named that function directly, which collided with Task 2's own automated verify script (`fn.index('mem_util_set_address')`) -- the script found the comment's own mention of the identifier before the real next function definition and truncated the sliced text early, failing the '0x100'/'0x01' bit-value assertions. Reworded to 'every address write (the one caller of this function)', which preserves the same meaning without touching the collision string; no code or scope change, verification-script-compatibility only"

requirements-completed: []

coverage:
  - id: D1
    description: "mem_util_split_delay + mem_util_delay_us declared with C linkage in memory_utils.h (uint32_t/uint16_t-only signatures, no Arduino.h leak) and implemented in memory.cpp with MEM_UTIL_DELAY_US_MAX=16383UL; memory_set_data's pulse now calls mem_util_delay_us(handle->pulse_delay) instead of the unclamped delayMicroseconds(handle->pulse_delay); delayMicroseconds(3) settle and memory_get_data's clamped read-timing delays left untouched"
    verification:
      - kind: other
        ref: "grep -n declarations in memory_utils.h; grep -c delayMicroseconds(handle->pulse_delay) src/proms/memory.cpp == 0; grep -c mem_util_delay_us(handle->pulse_delay) == 1; grep -c delayMicroseconds(3) == 1; grep -n MEM_UTIL_DELAY_US_MAX (all passed)"
        status: pass
      - kind: other
        ref: "pio run -e uno / -e uno328pb / -e leonardo (all SUCCESS: uno 24002B flash/1573B RAM, uno328pb 24052B/1579B, leonardo 26064B/2014B)"
        status: pass
      - kind: integration
        ref: "pio test -e native and pio test -e native_nodevtools (both 141 test cases / 17 suites, all PASSED, matching the pinned size_baseline.json counts)"
        status: pass
      - kind: integration
        ref: "pio test -e native_trace_v131 (5 test cases, all PASSED -- the frozen pre-change trace did not move, confirming the split fires strictly above 16383us and every shipped pulse width still emits a single delayMicroseconds call)"
        status: pass
      - kind: other
        ref: "cd firestarter && python3 -m pytest tests/ -q -o addopts=\"\" -> 244 passed (D-13 protocol-branch-inventory gate stays green; ran against a clean git tree per the known 141-01 gate hazard)"
        status: pass
    human_judgment: false
  - id: D2
    description: "mem_util_calculate_top_address_register's pins<32 comment no longer claims CTRL_VPP_VPE_DROP_ENABLE and CTRL_ADDRESS_LINE_16 'share the same CONTROL bit' (false on every build this project ships); replacement states the wide-layout bit values (0x01 / 0x100), names HARDWARE_REVISION, names the preserve mask as the real revision-independent mechanism, cross-references the D-09 handle->pins>=32 branch, and hands the DIP32 route choice to Phase 142 without pre-empting it; also documents the unconditional VPE/P1/A9/regulator preserve set as the real reason VPE survives a verify read. Code (`if (handle->pins < 32)` guard, `mask |= CTRL_VPP_VPE_DROP_ENABLE`) is byte-identical -- comment-only change"
    verification:
      - kind: other
        ref: "python3 assertion script: 'share the same control bit' absent, 'preserve'/'0x100'/'0x01'/'hardware_revision'/'phase 142' all present, 'pins < 32' and 'mask |= CTRL_VPP_VPE_DROP_ENABLE' unchanged -> 'OK preserve-mask comment corrected; code unchanged'"
        status: pass
      - kind: other
        ref: "git diff -U0 -- src/proms/memory.cpp piped through the plan's own comment-only diff-scope filter -> 'OK: no unexpected non-comment code lines changed in this task's diff scope'"
        status: pass
      - kind: other
        ref: "pio run -e uno post-change flash usage 24002 B -- byte-identical to the Task 1 measurement, confirming zero flash cost for the comment-only change"
        status: pass
      - kind: integration
        ref: "pio test -e native_trace_v131 re-run after the comment change (5 test cases, all PASSED)"
        status: pass
    human_judgment: false

duration: 20min
completed: 2026-08-10
status: complete
---

# Phase 141 Plan 02: Safe Split-Delay Helper + Preserve-Mask Comment Correction Summary

**32-bit-safe `mem_util_delay_us`/`mem_util_split_delay` helper added beside `memory.cpp`'s `mem_util_*` family and wired into the program pulse (LOOP-07 site 1 of 2), plus a corrected in-file comment replacing a disproven bit-collision claim with the verified preserve-mask mechanism (LOOP-08 groundwork) -- zero flash-byte cost, all gates green.**

## Performance

- **Duration:** 20 min
- **Started:** 2026-08-10T14:48:00Z
- **Completed:** 2026-08-10T15:08:00Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments
- Declared `mem_util_split_delay(uint32_t us, uint32_t* out_ms, uint16_t* out_us)` and `mem_util_delay_us(uint32_t us)` with C linkage in `memory_utils.h`, documenting the AVR `delayMicroseconds()` 16-bit ABI + `us <<= 2` overflow (ceiling 16383) with its toolchain citation, and why the split helper is exposed rather than static (native stubs record no elapsed time, only arguments)
- Implemented both in `memory.cpp` beside the `mem_util_calculate_*` family, gated by `MEM_UTIL_DELAY_US_MAX 16383UL`, splitting strictly **above** the ceiling (16383 itself does not split) so every shipped pulse width keeps emitting exactly one `delayMicroseconds` call
- Rerouted `memory_set_data`'s program pulse from the unclamped `delayMicroseconds(handle->pulse_delay)` to `mem_util_delay_us(handle->pulse_delay)` -- closing a currently-reachable silently-short-pulse defect (D-06 site 1 of 2; the erase-pulse site in `eprom.cpp` is plan 141-04's)
- Corrected `mem_util_calculate_top_address_register`'s `pins < 32` comment: removed the false "share the same CONTROL bit" claim and replaced it with the source-verified mechanism (distinct bits under the shipped `HARDWARE_REVISION` build; the real, revision-independent reason is the preserve mask itself, not a collision), cross-referencing D-09's `0x08` branch and handing the DIP32 route choice to Phase 142 without pre-empting it
- Verified the comment change costs exactly 0 flash bytes on `uno` (24002 B, identical before/after) and that `native_trace_v131` -- the frozen pre-change trace fixture -- still passes after both tasks

## Task Commits

Each task was committed atomically, inside `/workspaces/firestarter` on branch `gsd/v1.31-27c-programming-algorithm-fidelity`:

1. **Task 1: Declare and implement the safe split delay, and route the program pulse through it** - `1b03f19` (feat)
2. **Task 2: Correct the preserve-mask comment that states a disproven collision** - `3e98d4b` (docs)

**Plan metadata:** pending (docs: complete plan, this SUMMARY + STATE.md + ROADMAP.md, meta repo)

## Files Created/Modified
- `firestarter/include/memory_utils.h` - added `mem_util_split_delay` / `mem_util_delay_us` declarations (C linkage, `uint32_t`/`uint16_t`-only signatures) with the AVR-ceiling rationale comment
- `firestarter/src/proms/memory.cpp` - added `MEM_UTIL_DELAY_US_MAX`, implemented both functions, rerouted `memory_set_data`'s pulse call, and corrected the preserve-mask comment in `mem_util_calculate_top_address_register`

## Decisions Made
- Placed the two new functions physically between `mem_util_calculate_top_address_register` and `mem_util_set_address`, matching the plan's "next to the existing `mem_util_calculate_*` functions" instruction and confirmed compatible with Task 2's own file-slicing verify script.
- [Rule 3 - blocking] Reworded one sentence of the new preserve-mask comment to avoid the literal substring `mem_util_set_address`, which had collided with Task 2's own automated verify script (see Deviations below).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Task 2's own verify script tripped on its comment's use of the literal function name it slices on**
- **Found during:** Task 2, first verification attempt
- **Issue:** The plan's Task 2 verify script locates the corrected comment by slicing `memory.cpp` from `mem_util_calculate_top_address_register`'s definition up to the next occurrence of the substring `mem_util_set_address`, assuming that substring appears next only as the following function's definition. The first draft of the new preserve-mask comment (correctly, per the action's 4th bullet) explained that "`mem_util_set_address()` writes CONTROL_REGISTER unconditionally on every byte" -- which introduced an earlier occurrence of that exact substring inside the comment itself, truncating the verify script's slice to 503 characters and failing the `'0x100' in fn` / `'0x01' in fn` assertions (both true statements, just outside the truncated window).
- **Fix:** Reworded the sentence to "every address write (the one caller of this function) writes CONTROL_REGISTER unconditionally..." -- same meaning, no use of the colliding identifier string.
- **Files modified:** `firestarter/src/proms/memory.cpp` (comment text only, same file/task already in scope)
- **Verification:** Re-ran the plan's own Python assertion script and the diff-scope filter; both passed. `pio run -e uno` re-confirmed 24002 B (unchanged). `pio test -e native_trace_v131` re-confirmed 5/5 passing.
- **Committed in:** `3e98d4b` (Task 2 commit; the fix was applied before the first commit of this task, so no separate commit was needed)

---

**Total deviations:** 1 auto-fixed (1 blocking, verification-script-compatibility only -- no code, scope, or meaning change)
**Impact on plan:** Zero impact on delivered behavior or comment content's substance; purely a wording adjustment to avoid a self-referential collision with the plan's own gate.

## Issues Encountered
None beyond the deviation above.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- LOOP-07's helper exists and is proven at site 1 of 2 (the program pulse); plan 141-04 must reroute `eprom.cpp:283`'s erase pulse through the same `mem_util_delay_us` to complete the global claim (plan 141-06 is where LOOP-07 itself flips).
- LOOP-08's preserve-mask mechanism is now correctly documented in-tree; plan 141-08's native suite has an accurate comment to build its DIP32/A16-boundary assertions against, and Phase 142 (VPP-01/VPP-03) has an explicit, non-pre-empted hand-off for the final DIP32 route choice.
- `native_trace_v131` remains green through this plan by design (every shipped pulse width is at or below 16383 us and stays unsplit) -- Phase 141's later plans (141-04's loop rewrite) are expected to turn it RED per D-10, not this plan.
- No requirements were flipped (frontmatter `requirements: []`, honored) -- LOOP-07/LOOP-08 stay `[ ]` until plan 141-09's evidence-complete hand edit.

---
*Phase: 141-per-byte-program-loop*
*Completed: 2026-08-10*

## Self-Check: PASSED

- FOUND: firestarter/include/memory_utils.h
- FOUND: firestarter/src/proms/memory.cpp
- FOUND: 1b03f19 (git -C firestarter log --oneline --all)
- FOUND: 3e98d4b (git -C firestarter log --oneline --all)
