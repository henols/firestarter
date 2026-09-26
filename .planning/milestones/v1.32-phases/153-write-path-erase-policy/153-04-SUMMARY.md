---
phase: 153-write-path-erase-policy
plan: 04
subsystem: firmware
tags: [eeprom-28c, erase, at28c, sdp, dispatch, native-test, unity, fakeit]

requires:
  - phase: 153-write-path-erase-policy
    provides: "153-03: eeprom28c_erase_execute + case CMD_ERASE: arm, and the two intentional native REDs this plan inverts"
provides:
  - "test_case_group4a_0x0d_erase_dispatches_to_a_real_op_erase03 / test_case_group4b_0x0d_chip_id_null_main_devtest01: split, inverted dispatch-layer proof"
  - "make_erase_handle / drive_erase_op: factory + real-op driver for CMD_ERASE in test_eeprom28c_sdp.cpp, mirroring make_lock_handle / drive_lock_op"
  - "test_case25_cmd_erase_on_0x0d_dispatches_and_succeeds_erase03: inverted end-to-end op-layer proof, driven through a fed ACK stream"
  - "Cases 31-33: the erase's emitted stream pinned against the tree at head (SDP-disable golden), tail (chip-erase terminal byte vs SDP-disable terminal byte), and exact divergence index"
  - "test_eeprom28c_erase_configure_no_vpp: configure-phase no-VPP proof for CMD_ERASE, scope stated per D-153-03"
  - "both native envs (native, native_nodevtools) at 169 cases / 17 suites, green and in agreement"
affects: [153-05, 153-07, 153-08, 153-09, 153-10, 153-11, 153-12, 153-13, 153-14]

tech-stack:
  added: []
  patterns:
    - "Split-not-edit for a dual-claim test function whose name outlives one half of its assertion (Case group 4a/4b)"
    - "Fed-ACK-stream harness (local Serial available/peek/read mocks + bounded drive loop) for driving a real op through the ACK-gated op-layer state machine in a native test, where the existing suite convention (call main() directly) does not apply because the WHOLE point of the case is to exercise the op layer"
    - "Stream-pinning triad (head/tail/divergence) against in-tree tables rather than retyped literals, extending the Case 17-19 idiom to a two-sequence-concatenated (prefix + body) operation"

key-files:
  created: []
  modified:
    - firestarter/test/native/avr/test_dispatch/test_configure_memory.cpp
    - firestarter/test/native/avr/test_eeprom28c_sdp/test_eeprom28c_sdp.cpp
    - firestarter/test/native/avr/test_val_eeprom28c/test_val_eeprom28c.cpp

key-decisions:
  - "Case 25's drive mechanism deviated from the plan's literal instruction (Rule 1/3, discovered mid-task): op_execute_simple_operation with a non-NULL main enters the REAL ACK-gated INIT/MAIN/END state machine, which busy-loops forever against this suite's constant-0 millis() mock unless fed an ACK -- added a local Serial available/peek/read mock (continuous virtual OK stream) and a bounded 4-iteration drive loop, rather than the single call the old NULL-main short-circuit needed"
  - "Case 25's handle factory switched from make_lock_handle+manual h.cmd=CMD_ERASE to the new make_erase_handle, and firestarter_get_data reassigned to mock_get_data_keyed before driving, for the same recorder-flood reason drive_erase_op documents"
  - "Cases 31-33 measured (not assumed) the erase's full emitted stream length empirically before trusting the plan's SDP_FIXED_DIP28_28C256_LEN - 3 divergence-index prediction: 102 total entries (SDP-disable prefix's 54 plus the chip-erase body's 48, the body's own first write elided against the prefix's last write's address), divergence at index 51 (54-3) -- the prediction held exactly, confirmed empirically rather than assumed"
  - "Case 32's terminal-byte assertions read both FLASH_ERASE and EEPROM_SDP_DISABLE by their own sizeof-computed lengths, never a retyped literal or a hardcoded array size"

patterns-established:
  - "Fed-ACK-stream harness for op-layer-level native test cases (Case 25) -- reusable if a future plan needs to drive another real op end-to-end through op_execute_simple_operation/op_execute_stateful_operation rather than by calling the operation function pointer directly"

requirements-completed: []
# ERASE-03 and ERASE-04 are NOT flipped by this plan, per the phase's
# requirement-flip rule: ERASE-03 is also claimed by plans 07/08/09/10/11/12/13
# (none run yet), and ERASE-04 is also claimed by plan 05 (not run yet).
# This plan lands the FIRMWARE-TEST half of ERASE-03 (the dispatch arm is now
# proven to route to a real, stream-verified operation, not merely to a
# non-NULL pointer) and the STREAM half of ERASE-04 (head/tail/divergence
# pinned against the tree). ERASE-04's BODY half (the brace-matched negative
# source scan of eeprom28c_erase_execute for VPP/VPE tokens) is plan 05's job,
# explicitly deferred here per D-153-03 and this plan's own comment in
# test_eeprom28c_erase_configure_no_vpp.

coverage:
  - id: D1
    description: "Case group 4 split into 4a (CMD_ERASE, inverted: NOT_NULL main, NULL init, NULL end) and 4b (CMD_CHECK_CHIP_ID, unchanged: NULL main) -- the old combined function's name no longer outlives its assertion"
    requirement: "ERASE-03"
    verification:
      - kind: unit
        ref: "pio test -e native -f native/avr/test_dispatch (test_case_group4a_0x0d_erase_dispatches_to_a_real_op_erase03, test_case_group4b_0x0d_chip_id_null_main_devtest01, both PASSED; 23/23 total)"
        status: pass
    human_judgment: false
  - id: D2
    description: "Case 25 inverted end-to-end: CMD_ERASE on 0x0D dispatches through op_execute_simple_operation to RESPONSE_CODE_OK with no MSG_ERR_NOT_SUPPORTED, driven through the real ACK-gated state machine (not a synthetic short-circuit)"
    requirement: "ERASE-03"
    verification:
      - kind: unit
        ref: "pio test -e native -f native/avr/test_eeprom28c_sdp (test_case25_cmd_erase_on_0x0d_dispatches_and_succeeds_erase03, PASSED; 33/33 total)"
        status: pass
    human_judgment: false
  - id: D3
    description: "The erase op's emitted stream is pinned against the tree at head (positional equality with SDP_FIXED_DIP28_28C256 over its full length, plus proof the stream continues past it), tail (terminal payload equals FLASH_ERASE's own last byte, not EEPROM_SDP_DISABLE's), and divergence (exact index against a bare chip-erase-only reference, never != -1)"
    requirement: "ERASE-04"
    verification:
      - kind: unit
        ref: "pio test -e native -f native/avr/test_eeprom28c_sdp (test_case31_erase_stream_head_equals_sdp_disable_golden_erase04, test_case32_erase_stream_terminates_on_chip_erase_byte_erase04, test_case33_erase_stream_diverges_from_bare_chip_erase_at_exact_index_erase04, all PASSED)"
        status: pass
    human_judgment: true
    rationale: "Each of the three new stream cases was observed failing under a planted single-token mutation (transcribed below) before being trusted, but the ERASE-04 body-half control (the brace-matched negative source scan for VPP/VPE tokens) is explicitly deferred to plan 05 (D-153-03) -- routing to human_judgment keeps this deliverable from reading as ERASE-04's full discharge until plan 05 lands."
  - id: D4
    description: "test_eeprom28c_erase_configure_no_vpp: the CONFIGURE phase for CMD_ERASE sets no VPP-enable control bit, with the case's own comment stating this proves nothing about the erase operation body"
    requirement: "ERASE-04"
    verification:
      - kind: unit
        ref: "pio test -e native -f native/avr/test_val_eeprom28c (test_eeprom28c_erase_configure_no_vpp, PASSED; 12/12 total)"
        status: pass
    human_judgment: true
    rationale: "Deliberately scope-limited by this plan's own comment and D-153-03 -- the body-half GATE-03 control is plan 05's job, so this deliverable is not the full ERASE-04 proof and should not auto-pass as if it were."
  - id: D5
    description: "Both native environments (native, native_nodevtools) fully green and in agreement at 169 cases / 17 suites"
    verification:
      - kind: unit
        ref: "pio test -e native (169 test cases: 169 succeeded); pio test -e native_nodevtools (169 test cases: 169 succeeded); both report 17 suites"
        status: pass
    human_judgment: false

duration: ~19min
completed: 2026-08-21
status: complete
---

# Phase 153 Plan 04: Invert the Two Intended REDs and Pin the Erase Stream (ERASE-03/ERASE-04) Summary

**Split and inverted the two firmware-test assertions that claimed `CMD_ERASE` on `0x0D` is refused, then added three stream-equality cases (head/tail/divergence, all pinned against in-tree tables) plus a configure-phase no-VPP case, bringing both native environments to 169/17, fully green and in agreement.**

## Performance

- **Duration:** ~19 min (task commits span 2026-08-21T07:31:44Z-07:50:17Z)
- **Tasks:** 3/3 completed
- **Files modified:** 3 (all native test TUs, no production source changed)

## Accomplishments

- Split `test_case_group4_0x0d_erase_and_chip_id_null_main_devtest01` into `test_case_group4a_0x0d_erase_dispatches_to_a_real_op_erase03` (inverted: `NOT_NULL` main, `NULL` init, `NULL` end) and `test_case_group4b_0x0d_chip_id_null_main_devtest01` (unchanged chip-id half) -- the old name no longer outlives one half of its own assertion.
- Added `make_erase_handle` / `drive_erase_op` to `test_eeprom28c_sdp.cpp`, mirroring `make_lock_handle` / `drive_lock_op`, with `drive_erase_op` reassigning `firestarter_get_data` to `mock_get_data_keyed` -- load-bearing, since the erase's SDP-disable prefix polls via `get_data` and the real read path would flood the 512-entry strobe recorder.
- Inverted Case 25 (`test_case25_cmd_erase_on_0x0d_dispatches_and_succeeds_erase03`) end to end, all four beats positive. Discovered mid-task that the plan's literal drive shape ("keep `op_execute_simple_operation` as-is") crashes once `main` is non-NULL, because the real op-layer housekeeping state machine gates every phase transition behind `op_wait_for_ack()`, which busy-loops forever against this suite's constant-0 `millis()` mock unless fed an ACK. Fixed by adding a local Serial `available`/`peek`/`read` mock feeding a continuous virtual "OK" stream and a bounded 4-call drive loop (the deterministic trace needs exactly 4: INIT-ack, MAIN-ack + the actual erase run, END-ack, final-ack).
- Added Cases 31, 32, 33 pinning `eeprom28c_erase_execute`'s emitted stream against the tree: Case 31 (head equals `SDP_FIXED_DIP28_28C256` positionally, plus proof the stream continues past it), Case 32 (terminal payload equals `FLASH_ERASE`'s own last byte, not `EEPROM_SDP_DISABLE`'s -- FIX-05's one-nibble hazard class), Case 33 (exact divergence index against a bare chip-erase-only reference, `SDP_FIXED_DIP28_28C256_LEN - 3` = 51, never `!= -1`).
- Measured the erase op's actual emitted stream length empirically (102 entries total) before trusting the plan's divergence-index prediction -- the prediction (`LEN - 3` = 51) held exactly.
- Added `test_eeprom28c_erase_configure_no_vpp` to `test_val_eeprom28c.cpp`, with a comment stating its scope honestly per D-153-03: configure-phase only, proves nothing about the erase body, `check_dispatch.py` cannot see a handler-body register write.
- Every new/inverted stream and no-VPP case was observed failing under a planted single-token mutation before being trusted (transcribed below); every mutation was reverted, confirmed by a clean `git diff --stat -- src/proms/eeprom_28c.cpp` after each.
- Confirmed `pio test -e native` and `pio test -e native_nodevtools` both report 169 cases / 17 suites, fully green and in agreement (+6 cases across the phase so far vs. the 163/17 pre-change baseline: +1 from plan 02, +5 from this plan -- split +1, Cases 31-33 +3, no-VPP case +1).
- Ran the host gate checks from `firestarter_app/`: `check_no_log_in_sdp_window.py` PASS, `check_dispatch.py` exit 0 (746 chips scanned), `git diff --quiet -- tools/check_dispatch.py` exit 0 (checker untouched).

## Task Commits

1. **Task 1: Split and invert Case group 4 in `test_configure_memory.cpp`** - `374f9c9` (test)
2. **Task 2: Invert Case 25 and add the three erase-stream cases in `test_eeprom28c_sdp.cpp`** - `5f87ac3` (test)
3. **Task 3: Add the `CMD_ERASE` no-VPP configure case and turn both native environments green** - `73a943d` (test)

All three commits land in the `firestarter` sub-repo (`commits_land_in: [firestarter]`), on branch `gsd/v1.32-at28c-write-path-root-cause-report-provenance`.

## Files Created/Modified

- `firestarter/test/native/avr/test_dispatch/test_configure_memory.cpp` -- Case group 4 split into 4a (inverted) and 4b (unchanged); `RUN_TEST` list updated.
- `firestarter/test/native/avr/test_eeprom28c_sdp/test_eeprom28c_sdp.cpp` -- `make_erase_handle`, `drive_erase_op`, Case 25 inverted (renamed, ACK-fed drive loop, local Serial mocks), Cases 31-33 added, `RUN_TEST` list updated.
- `firestarter/test/native/avr/test_val_eeprom28c/test_val_eeprom28c.cpp` -- `test_eeprom28c_erase_configure_no_vpp` added, `RUN_TEST` list updated.

No production source file (`src/proms/eeprom_28c.cpp`) was modified by this plan's commits -- every mutation planted for reachability proof was reverted before committing (`git diff --stat -- src/proms/eeprom_28c.cpp` confirmed clean after each task).

## Decisions Made

- **Case group 4 split, not edited (per the plan's own instruction):** `test_case_group4a_0x0d_erase_dispatches_to_a_real_op_erase03` carries the inverted erase half; `test_case_group4b_0x0d_chip_id_null_main_devtest01` carries the still-true chip-id half verbatim, unreworded.
- **Case 25's handle factory switched from `make_lock_handle` + manual `h.cmd = CMD_ERASE` to the new `make_erase_handle`**, and `firestarter_get_data` reassigned to `mock_get_data_keyed` before driving -- the plan explicitly anticipated this switch might be needed and asked for the route and reason to be recorded (done, in the case's own comment).
- **Case 25's drive loop bounded at 10 iterations** even though the deterministic trace needs exactly 4 -- a generous safety margin against a state-machine shape change, not an escape hatch; if the shape ever changes such that completion isn't reached within 10 calls, the case fails loudly (`still_in_progress` stays true) rather than hanging.
- **Case 33's expected divergence index expressed as `SDP_FIXED_DIP28_28C256_LEN - 3`**, per the plan's binding instruction, and confirmed empirically (measured 51, matching the computed value) rather than trusted blind.
- **Case 32 reads both terminal bytes via `sizeof(...)/sizeof(...[0])`-computed lengths** (`FLASH_ERASE`, `EEPROM_SDP_DISABLE`) -- no retyped literal, no hardcoded array size.
- **`snapshot` buffer for Case 33 sized 128 entries**, per the plan's own note that the 64-entry size Cases 18/19 use is not enough for a stream roughly twice that length (measured 102 total for the erase's full stream -- comfortably inside 128).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - self-inflicted, discovered running the plan's own literal instruction] Case 25's `op_execute_simple_operation` drive crashed once `main` stopped being NULL**

- **Found during:** Task 2, first run of the newly-inverted Case 25.
- **Issue:** The plan's Task 2(b) instruction said to "keep the `op_execute_simple_operation` drive... as they are." With `main` non-NULL, `op_execute_stateful_operation` no longer short-circuits at the top-level NULL-main guard -- it enters the real INIT/MAIN/END housekeeping state machine (`operation_utils.cpp`), which gates every phase transition behind `op_wait_for_ack()`. That function polls `op_get_message` -> `rurp_communication_available()`, which routes through the REAL `src/boards/rurp_serial_utils.cpp` -> `Serial` (pulled into this suite's link by Phase 6's `[env:native]` widening) -- and this suite's `setUp()` never mocks `Serial.available()`/`peek()`/`read()` (only `write()`/`flush()`). The first call `terminate()`d with `fakeit::UnexpectedMethodCallException` (SIGABRT), confirmed by running `.pio/build/native/firestarter_native` directly (`pio test`'s wrapper only reported `[ERRORED]`).
- **Root-cause trace (for the record):** even with `Serial` mocked to answer immediately, a SINGLE call cannot complete the operation -- the deterministic trace through `operation_utils.cpp`'s state machine (`operation_state` values `INIT=1, MAIN=3, END=5, ENDED=6`) needs exactly 4 calls to `op_execute_simple_operation`, each consuming one ACK: call 1 (INIT-start ack, `operation_state` 0->2), call 2 (MAIN-start ack, runs the actual erase via `_single_step_operation_callback`, `operation_state` 2->4), call 3 (END-start ack, `operation_state` 4->6/ENDED), call 4 (the final ack `is_all_operations_done()` checks, returns `false`/complete).
- **Fix:** Added a local, case-scoped Serial mock (`case25_serial_available`/`_peek`/`_read`, backed by a file-scope `s_case25_ack_pos` counter) feeding a continuous virtual "OK" byte stream, and replaced the single call with a bounded loop (`MAX_CALLS = 10`, generous margin over the deterministic 4) calling `op_execute_simple_operation` until it returns `false`.
- **Files modified:** `firestarter/test/native/avr/test_eeprom28c_sdp/test_eeprom28c_sdp.cpp` (same file, same commit -- caught and fixed before the Task 2 commit was made).
- **Verification:** `pio test -e native -f native/avr/test_eeprom28c_sdp` -- 33/33 passed, including Case 25.
- **Committed in:** `5f87ac3` (Task 2 commit).

---

**Total deviations:** 1 auto-fixed (Rule 1, a bug in the plan's literal drive instruction against the real state machine, caught and fixed before committing).
**Impact on plan:** None on the plan's stated intent -- Case 25 still proves what it was meant to prove (CMD_ERASE on 0x0D dispatches to a real op and succeeds through the op layer, not just at the dispatch level), now driven correctly through the real ACK-gated machinery instead of a shape that could never have completed.

## Issues Encountered

**1. `grep -c '!= -1'` over `test_eeprom28c_sdp.cpp` does not return 0, for a reason unrelated to this plan's changes.** The plan's Task 2 acceptance criteria and the phase-level `<verification>` block both state this count must be 0. The file already carried 7 pre-existing occurrences before this plan touched it (confirmed via `git show HEAD~3:...|grep -c`, i.e. the state before Task 1's commit): five are legitimate `TEST_ASSERT_TRUE_MESSAGE(idx != -1, ...)` vector-index-lookup idioms in Cases 11 and 20 (unrelated to stream divergence), and two are explanatory-comment prose (lines 862, 1140) stating the "never `!= -1`" rule itself. This plan adds exactly two more occurrences, both also in explanatory comments (the new Case 33's header comment and its assertion message text), never in an actual assertion -- Case 33's real assertion is `TEST_ASSERT_EQUAL_MESSAGE(expected_div, div, ...)`, an exact-equality check. The underlying intent of the criterion (no stream-divergence case may use a bare not-equal check) fully holds; the literal grep count does not, and never could have, for reasons predating this plan. Same class of pre-existing-content gap as plan 03's `default:` grep finding, documented there for the same reason.
**2. `pio test` reported the process receiving `SIGHUP`/`SIGABRT` during mid-task debugging runs (both while chasing Case 25's crash and confirming the observed-RED transcripts), causing PlatformIO to label some runs `[ERRORED]` rather than `[FAILED]`.** Same non-blocking runner artifact documented in `153-02-SUMMARY.md` and `153-03-SUMMARY.md`. Running `.pio/build/native/firestarter_native` directly (bypassing `pio test`'s wrapper) reliably surfaced the real Unity/fakeit output in every case. Not treated as a plan deviation; noted for the record.

Neither issue blocked completion of any task or its verification.

## Reachability Evidence (planted mutations, observed and reverted)

**Case 31/33 -- SDP-disable prefix call removed from `eeprom28c_erase_execute`:**
```
test_case31_...: Expected 32 Was 16. Case 31 (ERASE-04): erase stream index 51 must equal SDP_FIXED_DIP28_28C256's entry at the same index ...
test_case33_...: Expected 51 Was -1. Case 33 (ERASE-04): the erase op's full stream must diverge from a BARE chip-erase-only reference stream at EXACTLY SDP_FIXED_DIP28_28C256_LEN - 3 ...
```
Reverted; `git diff --stat -- src/proms/eeprom_28c.cpp` empty afterward.

**Case 32 -- sixth erase write's byte changed `0x10` -> `0x20` (the SDP-disable terminal byte):**
```
test_case32_...: Expected 16 Was 32. Case 32 (ERASE-04): the terminal command payload must equal FLASH_ERASE's own last entry's byte, read from flash_utils.h (FIX-04 frozen) -- never a retyped literal
```
Reverted; `git diff --stat -- src/proms/eeprom_28c.cpp` empty afterward.

**`test_eeprom28c_erase_configure_no_vpp` -- planted `handle->firestarter_set_control_register(handle, CTRL_VPP_REGULATOR_ENABLE, 1);` inside the `case CMD_ERASE:` arm:**
```
test_eeprom28c_erase_configure_no_vpp: Expected XXXXXXXXXXXXXXXXXXXXXXXX0XXXXXXX Was XXXXXXXXXXXXXXXXXXXXXXXX1XXXXXXX. configure_eeprom28c CMD_ERASE must NOT set any VPP-enable CTL bit
```
Reverted; `git diff --stat -- src/proms/eeprom_28c.cpp` empty afterward.

## Native Test Evidence

**`pio test -e native`:** `169 test cases: 169 succeeded` (17 suites, all `[PASSED]`).
**`pio test -e native_nodevtools`:** `169 test cases: 169 succeeded` (17 suites, all `[PASSED]`).
Both agree with each other. This is `+6` against the `153-DECISIONS.md`-recorded pre-change baseline (163/17): `+1` from plan 02, `+5` from this plan (Case group 4 split `+1`, Cases 31-33 `+3`, the no-VPP case `+1`). **Recorded for plan 14**, which owns the formal `size_baseline.json` `native_envs` re-record; `check_size_baseline.py --avr-log` default mode will report a `cases` mismatch until then -- expected, not a regression, per this plan's own `<verification>` block and plan 03's identical note.

**Host gate checks (from `firestarter_app/`):**
- `python3 tools/check_no_log_in_sdp_window.py` -> `PASS: no logging call in SDP timing window ...` exit 0.
- `python3 tools/check_dispatch.py` -> `PASS: all 746 chips scanned; 736 supported; ...` exit 0.
- `git diff --quiet -- tools/check_dispatch.py` -> exit 0 (checker untouched, GATE-03 unweakened/unexempted/un-re-baselined).
- `firestarter_app/` left with zero tracked modifications (pre-existing untracked files in that repo predate this session and were not touched).

## User Setup Required

None -- no external service configuration required.

## Next Phase Readiness

- Both mandatory dispatch/end-to-end inversions have landed, each keeping a positive assertion, with the split function's naming now matching its assertions exactly.
- The erase's emitted stream is pinned against the in-tree tables at head, tail, and divergence, with no retyped byte literal in any oracle -- and every new stream/no-VPP assertion was observed failing under a planted mutation before being trusted.
- **ERASE-03 and ERASE-04 remain `In Progress`** -- per the phase's requirement-flip rule, neither flips here: ERASE-03 is also claimed by plans 07-13 (none run yet, host-half and doc-half work), and ERASE-04's real body-half control (plan 05's brace-matched negative source scan of `eeprom28c_erase_execute` for VPP/VPE tokens) has not yet landed.
- **Plan 05 owns ERASE-04's remaining half** -- the negative source scan, with its own planted-violation leg observed to fail before being trusted, per D-153-03.
- **Plan 14 owns the formal native-env re-baseline** (`size_baseline.json` `native_envs`, currently 163/17, needs to become 169/17 once the full phase's test additions are known) and the formal MERGE-05 flash/RAM measurement this plan's `eeprom28c_erase_execute` cost still needs.
- No production source file was changed by this plan -- `src/proms/eeprom_28c.cpp` is byte-identical to what plan 03 left it, confirmed by `git diff --stat` after every reachability-proof mutation was reverted.

---
*Phase: 153-write-path-erase-policy*
*Completed: 2026-08-21*

## Self-Check: PASSED

- FOUND: `firestarter/test/native/avr/test_dispatch/test_configure_memory.cpp`
- FOUND: `firestarter/test/native/avr/test_eeprom28c_sdp/test_eeprom28c_sdp.cpp`
- FOUND: `firestarter/test/native/avr/test_val_eeprom28c/test_val_eeprom28c.cpp`
- FOUND: `.planning/phases/153-write-path-erase-policy/153-04-SUMMARY.md`
- FOUND: `374f9c9` (Task 1 commit)
- FOUND: `5f87ac3` (Task 2 commit)
- FOUND: `73a943d` (Task 3 commit)
