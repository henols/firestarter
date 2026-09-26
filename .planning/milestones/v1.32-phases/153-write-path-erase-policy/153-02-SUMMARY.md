---
phase: 153-write-path-erase-policy
plan: 02
subsystem: firmware
tags: [eeprom-28c, sdp, write-init, blank-check, native-test, erase-policy]

requires: ["153-01"]
provides:
  - "ERASE-01: write performs no blank check on 0x0D, with or without FLAG_SKIP_BLANK_CHECK"
  - "test_case30_write_init_no_blank_check_with_flag_clear_erase01 -- observed-RED-then-GREEN oracle for the deletion"
  - "make_sdp_handle_blank_check_enabled -- the only factory in the suite that leaves the blank-check axis live"
affects: [153-14]

tech-stack:
  added: []
  patterns:
    - "Observed-RED-before-deletion (Task 1 authors and runs a failing case; Task 2's deletion is what turns it green)"

key-files:
  created: []
  modified:
    - firestarter/test/native/avr/test_eeprom28c_sdp/test_eeprom28c_sdp.cpp
    - firestarter/src/proms/eeprom_28c.cpp

key-decisions:
  - "Cites D-153-05 verbatim in the replacement comment: no FLAG_CAN_ERASE-gated erase-on-write block added to eeprom28c_write_init in place of the deleted blank check"
  - "Deletion only -- no compensating set_operation_in_progress/clear_operation_in_progress pair, no firestarter_operation_end assignment, no rename of eeprom28c_write_init"

requirements-completed: [ERASE-01]

coverage:
  - id: T1
    description: "test_case30 observed FAILING before the deletion (assertion 1, is_operation_in_progress FALSE check) with the verbatim Unity failure line transcribed"
    requirement: "ERASE-01"
    verification:
      - kind: unit
        ref: "pio test -e native -f native/avr/test_eeprom28c_sdp (pre-deletion run)"
        status: pass
    human_judgment: false
  - id: T2
    description: "Pre-write blank check deleted from eeprom28c_write_init; test_case30 now PASSES; mem_util_blank_check appears exactly once in eeprom_28c.cpp (CMD_BLANK_CHECK arm); check_no_log_in_sdp_window.py PASSes; native/native_nodevtools agree at 164 cases/17 suites; test_sdp_table_parity.py and test_dispatch_mirror.py pass"
    requirement: "ERASE-01"
    verification:
      - kind: unit
        ref: "pio test -e native, pio test -e native_nodevtools, check_no_log_in_sdp_window.py, pytest tests/test_sdp_table_parity.py tests/test_dispatch_mirror.py"
        status: pass
    human_judgment: false

duration: 40min
completed: 2026-08-21
status: complete
---

# Phase 153 Plan 02: Delete the 0x0D Pre-Write Blank Check Summary

**Deleted the three-line `FLAG_SKIP_BLANK_CHECK`-gated `mem_util_blank_check` call from the tail of `eeprom28c_write_init`, proven by a native case that was observed failing before the deletion and passing after.**

## Performance

- **Duration:** ~40 min
- **Tasks:** 2/2 completed
- **Files modified:** 2

## Accomplishments

- Added `make_sdp_handle_blank_check_enabled` — the only factory in
  `test_eeprom28c_sdp.cpp` that leaves the blank-check axis live (`ctrl_flags = 0`)
  — and `test_case30_write_init_no_blank_check_with_flag_clear_erase01`, registered
  in `main`, without touching any of the 29 existing cases or `make_sdp_handle`.
- Ran the suite and observed the new case FAIL for the intended reason: assertion 1
  (`TEST_ASSERT_FALSE_MESSAGE(is_operation_in_progress(&h), ...)`) fired, because
  `mem_util_blank_check` still ran unconditionally with the skip flag clear. The
  other 29 cases passed in the same run (30 cases total: 1 failed, 29 succeeded).
- Deleted the three-line `if (!is_flag_set(FLAG_SKIP_BLANK_CHECK)) { mem_util_blank_check(handle); }`
  conditional at the tail of `eeprom28c_write_init`, replacing it with a comment
  naming `D-07`, ERASE-01, and `D-153-05`, and stating that the blank-check skip
  flag is now unread on this protocol.
- `test_case30` flipped GREEN; `pio test -e native` and `pio test -e native_nodevtools`
  both report 164 cases / 17 suites (up from 163/17 in the plan-01 cold baseline,
  and agreeing with each other); `check_no_log_in_sdp_window.py` still prints
  `PASS:`; `test_sdp_table_parity.py` and `test_dispatch_mirror.py` still pass.
- Rebuilt `uno` and `leonardo` to confirm the change compiles cleanly: flash usage
  dropped by 14 bytes on both targets (25418→25404 uno, 27500→27486 leonardo), as
  expected for a pure deletion. This figure is reported for visibility only — plan
  14 owns the formal MERGE-05/Caterina-cliff measurement and the named `v153`
  exemption; no claim about that budget is made here.

## Task Commits

1. **Task 1: Add the blank-check-enabled write-INIT case and OBSERVE it fail** - `1810db2` (test)
2. **Task 2: Delete the pre-write blank check from `eeprom28c_write_init` and turn the case GREEN** - `0d90e5c` (feat)

**Plan metadata:** (final commit hash recorded after this summary is committed)

## Files Created/Modified

- `firestarter/test/native/avr/test_eeprom28c_sdp/test_eeprom28c_sdp.cpp` - new factory
  `make_sdp_handle_blank_check_enabled` and new case `test_case30_write_init_no_blank_check_with_flag_clear_erase01`,
  registered via `RUN_TEST`
- `firestarter/src/proms/eeprom_28c.cpp` - deleted the pre-write blank-check
  conditional at the tail of `eeprom28c_write_init`, replaced with a comment
  citing `D-07`, ERASE-01, `D-153-05`

## Observed RED (Task 1, before the deletion)

Unity failure line, verbatim:

```
test/native/avr/test_eeprom28c_sdp/test_eeprom28c_sdp.cpp:1734: test_case30_write_init_no_blank_check_with_flag_clear_erase01: Case 30 (ERASE-01): is_operation_in_progress must be FALSE after exactly one eeprom28c_write_init call with FLAG_SKIP_BLANK_CHECK clear -- mem_util_blank_check is the only setter of this flag on the write-INIT path, so TRUE here would mean the pre-write blank check still ran and left a multi-call INIT loop pending	[FAILED]
```

Assertion 1 fired first (the other two assertions were never reached in that
run, since Unity aborts the test function on the first failed `TEST_ASSERT_*`).
The suite run reported "31 test cases: 1 failed, 29 succeeded" as PlatformIO's
runner label (30 cases registered at that point in the plan: case 30 failed,
cases 1-29 passed). `pio test` also reported the process receiving `SIGHUP`
after the failure was recorded; this did not recur once case 30 passed
post-deletion, so it is attributed to the sandboxed test-runner's handling of a
failing Unity process rather than to the test or production code — noted here
for the record, not treated as a plan deviation since it did not block
observing or transcribing the required RED.

## After the deletion (Task 2)

- `test_case30` passes: `is_operation_in_progress(&h)` is FALSE, `h.progress_data`
  is NULL, and the recorded stream equals `SDP_FIXED_DIP28_28C256` exactly.
- `grep -c 'mem_util_blank_check' src/proms/eeprom_28c.cpp` → `1` (the
  `CMD_BLANK_CHECK` switch arm only).
- `grep -n 'FLAG_SKIP_BLANK_CHECK' src/proms/eeprom_28c.cpp` → one hit, inside
  the replacement comment only (not inside any function body).
- `grep -nE 'set_operation_in_progress|clear_operation_in_progress|firestarter_operation_end' src/proms/eeprom_28c.cpp` → no hits.
- `git diff` on `eeprom_28c.cpp` shows exactly one hunk: the three-line deletion
  plus the 11-line replacement comment.

## Decisions Made

None new — this plan implements `D-153-05` (already settled in `153-DECISIONS.md`
by plan 01) rather than deciding anything new. The replacement comment restates
`D-153-05`'s prohibition at the exact site an executor would be tempted to add an
erase-on-write block.

## Deviations from Plan

None — plan executed exactly as written. All verification checks passed as
specified. The `SIGHUP` runner artifact noted above is an environment
observation, not a deviation from the plan's instructions.

## Issues Encountered

None blocking. See the `SIGHUP` note above for a non-blocking environment
observation during the Task 1 RED run.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- ERASE-01 is satisfied by a deletion, with no compensating state machinery
  added — `firestarter write` on `0x0D` now performs no blank check whether or
  not the skip flag is set, and write-INIT remains single-shot.
- The `CMD_BLANK_CHECK` arm and standalone `blank` command are untouched and
  unaffected (ERASE-05 non-regression).
- `check_no_log_in_sdp_window.py`'s fail-closed rename tripwire still resolves
  and prints `PASS:` — the edit stayed within the three-line scope the gate
  expects.
- Native case/suite counts (164/17, both environments) are the new reference
  point for any later plan in this phase that also touches native tests.
- Plan 14 has a fresh AVR size delta to fold into its cold-baseline comparison
  (both targets shrank by 14 B from this deletion, ahead of any additive change
  later plans in this phase will make).

---
*Phase: 153-write-path-erase-policy*
*Completed: 2026-08-21*

## Self-Check: PASSED

- FOUND: `firestarter/test/native/avr/test_eeprom28c_sdp/test_eeprom28c_sdp.cpp`
- FOUND: `firestarter/src/proms/eeprom_28c.cpp`
- FOUND: `.planning/phases/153-write-path-erase-policy/153-02-SUMMARY.md`
- FOUND: commit `1810db2`
- FOUND: commit `0d90e5c`
