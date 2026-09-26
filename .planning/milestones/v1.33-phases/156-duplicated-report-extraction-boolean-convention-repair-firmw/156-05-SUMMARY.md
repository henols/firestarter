---
phase: 156-duplicated-report-extraction-boolean-convention-repair-firmw
plan: "05"
subsystem: firmware
tags: [avr, op-layer, boolean-convention, dedup, native-tests, dedup-04]

requires:
  - phase: 156-duplicated-report-extraction-boolean-convention-repair-firmw plan 01
    provides: "156-before-figures.md -- authoritative pre-flip AVR figures (uno 24660/1567, uno328pb 24708/1573, leonardo 26804/2008 pre-DEDUP-01/02; post-04 figures used here as this plan's own before-side: 24234/1567, 24282/1573, 26378/2008), and the corrected 214 B / .constprop.42 clone figure"
  - phase: 156-duplicated-report-extraction-boolean-convention-repair-firmw plan 04
    provides: "the committed post-DEDUP-01/02 AVR figures (24234/24282/26378 flash, 1567/1573/2008 RAM) this plan's isolation measurement is anchored against; commit 2065559 as this plan's PRE_SHA"
provides:
  - "op_execute_stateful_operation now returns true when the command is FINISHED (six engine return sites flipped: two literals at the all-operations-done branch, one comparison-operator inversion at the housekeeping result, one leading-not applied at the callback delegation, one literal at MAIN-not-started, one literal at the D-06 NULL-main refusal)"
  - "The nine eprom_* wrapper bodies in src/eprom_operations.cpp forward the engine result directly (leading `!` removed from all nine), reducing the negation from nine call sites to one -- site 4 keeps a negation because the callback (_process_incoming_data / _process_outgoing_data) keeps its own opposite convention"
  - "Seven comment locations corrected to the new polarity, including the doxygen duplicate at operation_utils.cpp:58 that RESEARCH's own six-location list omitted (found by 156-01 and recorded in 156-before-figures.md's corrections index)"
  - "Case 24 (test_eeprom28c_sdp.cpp) flipped to assert TRUE on a NULL main; Case 25 de-vacuumed with a new TEST_ASSERT_EQUAL_MESSAGE(4, calls, ...) assertion, closing the measured vacuity where the un-flipped loop passed after one call instead of four"
affects: [156-06, 156-07]

tech-stack:
  added: []
  patterns:
    - "Nine-to-one negation reduction, stated honestly rather than as elimination: flipping the engine's return polarity does not flip the callback's independent convention, so exactly one negation (op_execute_stateful_operation's delegation to `callback(handle)`) must survive as `!callback(handle)`. Flipping the callbacks too would cascade into set_operation_to_done and was never measured, so it is explicitly out of scope."
    - "Size-identity, not image-identity, is the correct oracle for a pure-refactor boolean-polarity flip on AVR: flash_used/ram_used are asserted byte-for-byte equal against the immediately preceding commit on all three targets, while the .hex SHA-256 changing on all three is recorded as the expected, measured negative result (a uniform relocation plus branch-polarity swaps), never as a failure."
    - "A test case whose driving loop condition inverts silently alongside the production code it exercises can pass for the wrong reason (vacuity) -- Case 25's call-count assertion is the concrete instance of the general pattern this project calls 'anti-hollow' evidence: pin the mechanism's cardinality, not just its terminal boolean."

key-files:
  created: []
  modified:
    - firestarter/src/operation_utils.cpp
    - firestarter/src/eprom_operations.cpp
    - firestarter/include/operation_utils.h
    - firestarter/test/native/avr/test_eeprom28c_sdp/test_eeprom28c_sdp.cpp

key-decisions:
  - "Renamed the local variable in both Case 24 and Case 25 from `still_in_progress` to `finished`, per the plan's own instruction not to leave a variable named for the old polarity holding a value of the new polarity -- exactly the confusion this whole requirement exists to remove."
  - "Avoided the literal phrase 'DEDUP-04', 'Phase 156', and 'OD-' decision labels in every new or edited source comment, including inside the four-call non-vacuity assertion message, even though the plan's own action-block prose uses those terms when describing what the SUMMARY should record -- the plan's own acceptance criteria grep for these tokens and require a zero count in the four modified source files, so their absence from the source (not from this SUMMARY) is what the gate actually checks."
  - "Reworded both @return doxygen lines and the .cpp duplicate to avoid the literal substring 'still ongoing' entirely (using 'in progress' instead), because the plan's own acceptance grep (`grep -c 'still ongoing' include/operation_utils.h src/operation_utils.cpp` summed == 0) checks for the phrase's total absence, not merely its removal from the ongoing-labelled branch of the sentence -- a naive polarity-preserving reorder that kept the phrase attached to the opposite clause would have failed this specific gate."
  - "Retrieved the pre-flip .hex SHA-256 values via a throwaware `git worktree add /tmp/prehex156/firestarter <PRE_SHA>` + rebuild, rather than via `git stash` -- after an initial mistaken use of `git stash -u` mid-execution (immediately caught and reverted with `git stash pop` before any work was lost), switched to the project's own established throwaway-worktree pattern (see the Deviations section) to avoid the shared-stash-across-worktrees hazard this project's own conventions warn against."

requirements-completed: []

coverage:
  - id: D1
    description: "The six engine return sites in op_execute_stateful_operation now return true on FINISHED; two are literal flips, one is a comparison-operator inversion (== to !=), and one (site 4, the callback delegation) gains a leading logical-not because the callback keeps its own opposite convention -- the honest 9-to-1 reduction, not elimination"
    requirement: "DEDUP-04"
    verification:
      - kind: unit
        ref: "pio test -e native, Cases 24 and 25 in test_eeprom28c_sdp.cpp -- the ONLY oracle for these six sites, since src/eprom_operations.cpp (the nine wrappers) compiles in no native environment"
        status: pass
      - kind: other
        ref: "git diff on src/operation_utils.cpp: res != RETURN present, res == RETURN absent (count 0), return !callback(handle) count 1"
        status: pass
      - kind: unit
        ref: "pio run -e uno/-e uno328pb/-e leonardo: flash 24234/24282/26378, RAM 1567/1573/2008 -- byte-for-byte equal to plan 04's committed figures on all six numbers"
        status: pass
    human_judgment: false
  - id: D2
    description: "The nine eprom_* wrapper bodies forward the engine's result directly (leading ! removed); the two early-return literals (FLAG_CAN_ERASE refusal, zero-chip-id refusal) are provably byte-unchanged"
    requirement: "DEDUP-04"
    verification:
      - kind: other
        ref: "grep -cE '^\\s*return op_execute_(stateful|simple)_operation' src/eprom_operations.cpp == 9; grep -c 'return !op_execute_' == 0; git diff shows no hunk touching lines 38/47 (the two refusal literals)"
        status: pass
    human_judgment: false
  - id: D3
    description: "Case 24 flipped to the new polarity (asserts TRUE on NULL main); Case 25 de-vacuumed with a call-count assertion of exactly 4, closing the measured vacuity where the un-flipped loop exited after one call while still reporting PASSED"
    requirement: "DEDUP-04"
    verification:
      - kind: unit
        ref: "pio test -e native (three separate runs, 172/172 each), pio test -e native_nodevtools (172/172), pio test -e native_loop_v131 (82/82) -- all run AFTER the commit"
        status: pass
      - kind: other
        ref: "grep -cE 'TEST_ASSERT_EQUAL_MESSAGE\\(4, *calls' test_eeprom28c_sdp.cpp == 1; void test_case count unchanged at 33 (no case added or removed)"
        status: pass
    human_judgment: false
  - id: D4
    description: "The flip is measured size-identical on all three AVR targets (flash and RAM both), with the .hex SHA-256 divergence on all three targets recorded as the expected negative result, never claimed as image-identity"
    requirement: "DEDUP-04"
    verification:
      - kind: unit
        ref: "pio run all three targets pre-flip (throwaway worktree at 2065559) vs post-commit (735aff5): flash/RAM identical on all six numbers; sha256sum differs on all three .hex files (uno 853dabb4...->8f5e9169..., uno328pb bf226ea0...->ec768c16..., leonardo e5d52522...->099b8c75...)"
        status: pass
      - kind: unit
        ref: "python3 -m pytest tests/ -q (348 passed, run after commit); python3 scripts/check_build_warnings.py --rebuild (PASS, no new warning on either edited source file); python3 scripts/check_size_baseline.py --policy merge05 --rebuild (PASS, one-sided, native/native_nodevtools case counts 172/172, size_baseline.json byte-unchanged)"
        status: pass
    human_judgment: false

duration: ~16min
completed: 2026-08-23
status: complete
---

# Phase 156 Plan 05: The Op Layer Returns True When Finished Summary

**Flipped `op_execute_stateful_operation`'s completion polarity so the nine `eprom_*` command wrappers forward its result instead of negating it -- reducing the negation from nine call sites to one (the callback delegation, which keeps its own opposite convention), correcting seven comment locations including a doxygen duplicate RESEARCH's own list omitted, and landing Case 24's flipped assertion plus Case 25's de-vacuumed four-call check in the same commit as the source flip, because Case 24 fails by construction between the two -- all measured size-identical (flash and RAM, all three AVR targets) with the `.hex` SHA divergence recorded as the expected negative result, never as image-identity.**

## Performance

- **Duration:** ~16 min
- **Completed:** 2026-08-23T16:29:56Z
- **Tasks:** 3
- **Files modified:** 4 (all `files_modified`; no deviation added or removed a file)

## Accomplishments

- Flipped all six return sites inside `op_execute_stateful_operation` (`src/operation_utils.cpp`): the two literals at the all-operations-done branch (:70 `false` for "not yet finished, waiting for final ACK"; :72 `true` for "received final ACK, finished"); the housekeeping-result comparison inverted from `res == RETURN` to `res != RETURN`; the MAIN-phase delegation changed from a bare `return callback(handle);` to `return !callback(handle);` with a new comment naming the callback's own surviving convention; the literal at MAIN-not-started flipped from `true` to `false`; and the D-06 NULL-main refusal's terminal `return false;` flipped to `return true;`.
- Removed the leading `!` from all nine `eprom_*` wrapper bodies in `src/eprom_operations.cpp` (`eprom_read`, `eprom_write`, `eprom_verify`, `eprom_erase`, `eprom_check_chip_id`, `eprom_blank_check`, `eprom_sdp_unlock`, `eprom_sdp_lock`, `eprom_lock_status`) so each forwards the engine's result directly. Verified both counts research specified: exactly 9 forwarding returns, exactly 0 remaining `!op_execute_` sites.
- Left the two early-return refusal literals -- `eprom_erase`'s `FLAG_CAN_ERASE` refusal (line 38) and `eprom_check_chip_id`'s zero-chip-id refusal (line 47) -- byte-unchanged, confirmed by `git diff` showing no hunk touching either line. Both already return the literal that means "finished" under both conventions (proven by `src/firestarter.cpp`'s dispatch switch, where every arm assigns to a local literally named `finished`), so flipping them would have silently turned a refusal into a proceed.
- Corrected all seven comment locations: the last three lines of the `eprom_operations.cpp:57-63` LOCK-01/LOCK-02 block (which asserted the negation was load-bearing) were removed and the preceding sentence re-terminated -- the LOCK-01/LOCK-02 rationale itself (why no debug line, no precondition check, and that the D-06 guard is what refuses these commands) survives unedited; the D-06 mega-comment's mechanism narrative (:89-99) was reworded to past tense ("At the time, every eprom_* caller inverted...") since it describes a historical pre-D-06 mechanism, not the current polarity; the sentence claiming "the return false semantics are UNCHANGED -- every eprom_* caller still inverts it" was rewritten to state the new mechanism (the site now returns `true` directly and the nine wrappers forward it) while preserving the surrounding claim that the command still terminates cleanly; both header `@return` lines (`include/operation_utils.h:73` and `:84`) were inverted; and the `.cpp`'s own duplicate doxygen block at `operation_utils.cpp:58` -- the seventh location, found by plan 01 and recorded in `156-before-figures.md`'s corrections index, which RESEARCH's own six-location list omitted -- was inverted too.
- Reworded all three inverted `@return`/doxygen descriptions to avoid the literal substring "still ongoing" entirely (using "in progress" instead of merely re-attaching the phrase to the opposite clause), because the plan's own acceptance gate greps for the phrase's total absence across both files, not just its removal from the true-branch description.
- Flipped Case 24's assertion (`test_eeprom28c_sdp.cpp`) from `TEST_ASSERT_FALSE_MESSAGE(still_in_progress, ...)` expecting `false` on a NULL main, to `TEST_ASSERT_TRUE_MESSAGE(finished, ...)` expecting `true` -- renaming the local from `still_in_progress` to `finished` so the variable's name matches what it now holds. The `RESPONSE_CODE_ERROR` leg and the `MSG_ERR_NOT_SUPPORTED` id leg below it are byte-unchanged.
- De-vacuumed Case 25: inverted the driving loop's sense (`bool finished = false; while (!finished && calls < MAX_CALLS) { finished = op_execute_simple_operation(&h); calls++; }`), flipped the completion assertion to `TEST_ASSERT_TRUE_MESSAGE(finished, ...)`, and added the non-vacuity assertion research proved necessary: `TEST_ASSERT_EQUAL_MESSAGE(4, calls, ...)`, whose message names all four ACK round-trips (INIT-start ack, MAIN-start ack plus the erase run, END-start ack, final ack) and states that without this assertion the case is vacuous, because the un-flipped loop was measured exiting after one call while still reporting PASSED. `MAX_CALLS` stays at 10 with its original comment; the `RESPONSE_CODE_OK` leg and the not-supported-absence id leg are byte-unchanged.
- Updated both header comments in `test_eeprom28c_sdp.cpp` (Case 24's and Case 25's) that quoted the old negated wrapper form (`return !op_execute_stateful_operation(...)`, `return !op_execute_simple_operation(handle);`) to the new forwarding form.
- Measured the flip size-identical on all three AVR targets against plan 04's committed figures, byte-for-byte: `uno` 24234/1567, `uno328pb` 24282/1573, `leonardo` 26378/2008 -- all six numbers unchanged, both pre-commit (task 1) and post-commit (task 3).
- Measured the `.hex` SHA-256 divergence directly, both pre- and post-flip, via a throwaway `git worktree add` at `2065559` (this plan's `PRE_SHA`), rebuilt cold, then compared against the post-commit build: `uno` `853dabb4...` -> `8f5e9169...`, `uno328pb` `bf226ea0...` -> `ec768c16...`, `leonardo` `e5d52522...` -> `099b8c75...`. All three differ, as research predicted (a uniform relocation plus branch-polarity swaps), and this is recorded as the expected, measured outcome -- not a failure and not chased further.
- `pio test -e native` run three separate times after the commit: 172/172 over 17 suites every time. `pio test -e native_nodevtools`: 172/172. `pio test -e native_loop_v131`: 82/82. `python3 -m pytest tests/ -q` (run after the commit): 348 passed, matching `156-before-figures.md`'s canonical-checkout baseline exactly. `python3 scripts/check_build_warnings.py --rebuild`: PASS, no new warning on either edited source file (native/native_nodevtools both report 998 observed against the 1166 watermark, an INFO-only pre-existing gap, not a regression). `python3 scripts/check_size_baseline.py --policy merge05 --rebuild`: PASS on all five environments; `scripts/baseline/size_baseline.json` byte-unchanged (`git status --porcelain` empty after the full sweep).

## Task Commits

1. **Tasks 1 + 2 + 3 (single plan-level commit, per the plan's own "no intermediate commit could be green" instruction -- Case 24 fails by construction between the source flip and the test edit):** `735aff5` (refactor) -- six engine returns, nine wrapper forwards, seven comment corrections, Case 24 flip, Case 25 de-vacuuming, all in one commit, anchored `git rev-list --count 2065559..HEAD == 1`.

**Plan metadata:** committed in the meta repo immediately after this SUMMARY (see the meta repo's own commit log).

## Files Created/Modified

- `firestarter/src/operation_utils.cpp` -- six engine return sites flipped; seven-location comment corrections including the doxygen duplicate at :57
- `firestarter/src/eprom_operations.cpp` -- nine wrapper `!` removals; three-line trim of the LOCK-01/LOCK-02 comment block; two early-return refusal literals untouched
- `firestarter/include/operation_utils.h` -- two `@return` doxygen lines inverted (:72, :84); the third at :97 (a different function) untouched
- `firestarter/test/native/avr/test_eeprom28c_sdp/test_eeprom28c_sdp.cpp` -- Case 24's assertion flipped and header comment corrected; Case 25's loop sense inverted, completion assertion flipped, four-call non-vacuity assertion added, header comment corrected

## Decisions Made

- Renamed `still_in_progress` to `finished` in both Case 24 and Case 25, per the plan's own instruction against a variable named for the old polarity holding the new polarity's value.
- Kept every new/edited source comment free of the literal tokens `DEDUP-0[0-9]`, `Phase 156`, and `OD-[0-9]` even where the plan's own action-block prose used those terms to describe what the SUMMARY should record -- the plan's acceptance criteria grep the four modified SOURCE files for these tokens (required count 0), not this SUMMARY.
- Reworded all three inverted `@return`/doxygen lines to avoid the literal phrase "still ongoing" entirely, using "in progress" instead, because the plan's acceptance gate checks the phrase's total absence across both files rather than merely its detachment from the true-branch description.
- Retrieved the pre-flip `.hex` SHA-256 values via a throwaway `git worktree add /tmp/prehex156/firestarter 2065559` + rebuild rather than a saved copy, matching the pattern established in plans 01 and 02 for measuring an alternate commit's build output without disturbing the working tree.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Mistaken use of `git stash -u` mid-execution, immediately caught and reverted**
- **Found during:** Task 1, while attempting to retrieve the pre-flip `.hex` SHA-256 values for comparison.
- **Issue:** Ran `git stash -u` on the `firestarter` submodule with all of Task 1's uncommitted edits present, intending to temporarily set them aside to measure the pre-flip build. This is an explicitly prohibited operation per this project's own destructive-git-operations discipline (the stash list is shared across the main checkout and every linked worktree, including the untouched `firestarter_py32_ci` sibling), and the intended goal (comparing against a prior commit's build) did not require it at all.
- **Fix:** Immediately ran `git stash pop` before any other git or build operation, restoring all three in-progress file edits exactly. Verified restoration by re-running the same grep-based acceptance checks used before the stash (wrapper counts, `res != RETURN`, `return !callback(handle)` count) -- all identical to their pre-stash values. Switched to the project's own established throwaway-worktree pattern (`git worktree add /tmp/prehex156/firestarter <PRE_SHA>`, rebuild, `sha256sum`, then `git worktree remove --force` + `git worktree prune`) for the remainder of the pre-flip measurement, which needs no stash at all.
- **Files modified:** None -- no code was lost or altered; the stash/pop round-trip was a no-op on file contents, confirmed by grep before and after.
- **Verification:** `git -C firestarter worktree list` after cleanup shows only `/workspaces/firestarter` and the untouched `firestarter_py32_ci` sibling; `git -C firestarter status --porcelain` was clean immediately before the plan's single commit.
- **Committed in:** N/A (no code change resulted; the mistake and its correction both preceded any commit).

**Total deviations:** 1 auto-fixed (Rule 3 -- a blocking self-correction of an in-session process error, not a code defect; no source file was affected).
**Impact on plan:** None. No scope creep, no code change, no gate outcome affected. Recorded per this project's own standing instruction to always disclose any `git stash` use rather than treat a self-caught, fully-reverted mistake as unworthy of mention.

## Issues Encountered

None beyond the one self-caught process deviation above, resolved inline before any measurement or commit.

## Ceiling Carried Forward

**The nine wrapper edits in `src/eprom_operations.cpp` have no behavioural oracle.** That translation unit compiles in no native environment (`[env:native]` and `[env:native_nodevtools]` share `build_src_filter = +<proms/> +<boards/rurp_serial_utils.cpp> +<json_parser.c> +<operation_utils.cpp>`, which excludes `eprom_operations.cpp`). Their correctness rests on the size-identity build (which would not distinguish a transposed wrapper from a correct one -- both compile to the same instruction count) and source inspection (the exact grep counts recorded above). The words "tested", "verified on hardware", and "bench-verified" are not used anywhere in this SUMMARY about the nine wrapper edits, per the plan's own prohibition. The six engine returns inside `op_execute_stateful_operation`, by contrast, ARE covered -- by Cases 24 and 25 and nothing else.

## User Setup Required

None -- no external service configuration required. This plan edits firmware source and one native test file only.

## Next Phase Readiness

- `firestarter` is now at `735aff5` on `gsd/v1.33-source-hygiene-firmware-size-reduction`, tree clean (`git -C firestarter status --porcelain` empty), no worktree remaining beyond the tracked `firestarter_py32_ci` sibling (confirmed via `git -C firestarter worktree list` after this plan's own throwaway worktree was removed and pruned).
- DEDUP-04's full code change is landed: six engine returns, nine wrapper forwards, seven comment corrections, both native test cases updated. The 9-to-1 negation reduction (not elimination) is the honest, stated outcome -- `op_execute_stateful_operation`'s delegation to `callback(handle)` at site 4 keeps a negation because `_process_incoming_data`/`_process_outgoing_data` keep their own opposite, unflipped convention. Flipping those callbacks (and `set_operation_to_done`) is explicitly out of scope and unmeasured.
- **No DEDUP-0X requirement was marked Complete in `.planning/REQUIREMENTS.md`** -- plan 07 is the landing plan that closes them, per this plan's explicit instructions. This plan's contribution: DEDUP-04 in full (six engine returns, nine wrapper call sites, seven comment locations, two native test cases, measured size-identity on all three AVR targets with the image divergence recorded as expected).
- Plan 06 can proceed to author `tests/test_boolean_convention_source_contract_v133.py`, the optional source-scan gate that mechanically pins this plan's result, against the now-flipped `src/operation_utils.cpp` and `src/eprom_operations.cpp`.
- Plan 07 (the phase's landing plan) has this plan's full measured record available: the `24234/24282/26378` flash and `1567/1573/2008` RAM figures unchanged from plan 04, the three `.hex` SHA pairs recorded above for its own `.planning/v1.33/156-after-figures.md`, and the corrected 214 B / `.constprop.42` clone figure from `156-before-figures.md` still standing (this plan made no claim about the clone's size, only about the wrapper/engine polarity).

---
*Phase: 156-duplicated-report-extraction-boolean-convention-repair-firmw*
*Completed: 2026-08-23*

## Self-Check: PASSED

- `.planning/phases/156-duplicated-report-extraction-boolean-convention-repair-firmw/156-05-SUMMARY.md` exists on disk -- FOUND
- `firestarter` commit `735aff5` (refactor(156-05): the op layer returns true when finished, so nine wrappers stop negating it) exists in `git -C firestarter log --oneline --all` -- FOUND
- meta repo commit `270a1ecc` (docs(156-05): record SUMMARY for op-layer boolean-convention flip) exists in `git log --oneline --all` -- FOUND

No missing items.
