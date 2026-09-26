---
phase: 153-write-path-erase-policy
plan: 06
subsystem: firmware
tags: [flash4, flash-5v-page, write-init, blank-check, native-test, erase-policy]

requires: ["153-05"]
provides:
  - "ERASE-02 (partial): write performs no blank check on 0x05, with or without FLAG_SKIP_BLANK_CHECK -- located-in-code evidence recorded"
  - "test_5v_page_write_init_no_blank_check_with_flag_clear_erase02 -- observed-RED-then-GREEN oracle for the deletion"
  - "make_write_init_handle_blank_check_enabled -- the only factory in the suite that drives flash_5v_page_write_init itself"
affects: [153-13, 153-14]

tech-stack:
  added: []
  patterns:
    - "Observed-RED-before-deletion (Task 1 authors and runs a failing case; Task 2's deletion is what turns it green) -- mirrors 153-02"

key-files:
  created: []
  modified:
    - firestarter/test/native/avr/test_val_5v_page/test_val_5v_page.cpp
    - firestarter/src/proms/flash_5v_page.cpp

key-decisions:
  - "Located the conditional in code before touching it: it is at flash_5v_page.cpp lines 88-90, NOT 87-89 as the pattern map recorded, and matching RESEARCH's original 88-90 figure. The pattern map's 'correction' was itself wrong."
  - "Cites D-153-05 in the replacement comment, describing the FLAG_CAN_ERASE erase-on-write block generically ('the erase-enable block', 'a bulk-erase call') rather than by literal token, so grep -c counts for FLAG_CAN_ERASE (1) and flash_5v_page_erase_execute (4) stay pinned at their pre-task values -- an explicit acceptance criterion in this plan, distinct from 153-02's eeprom_28c.cpp comment (which had no such pinning constraint because that file has no erase-on-write block of its own)"
  - "Deletion only -- no compensating state machinery, no operation_end arm, no rename of flash_5v_page_write_init"
  - "ERASE-02 left In Progress, not Complete: plan 13 also claims it (corrects the prose docs) and has not run yet"

requirements-completed: []

coverage:
  - id: T1
    description: "The 0x05 blank-check conditional was located in code (lines 88-90) and quoted verbatim before being changed; test_5v_page_write_init_no_blank_check_with_flag_clear_erase02 observed FAILING before the deletion (assertion 1, is_operation_in_progress FALSE check) with the verbatim Unity failure line transcribed"
    requirement: "ERASE-02"
    verification:
      - kind: unit
        ref: "pio test -e native -f native/avr/test_val_5v_page (pre-deletion run)"
        status: pass
    human_judgment: false
  - id: T2
    description: "Pre-write blank check deleted from flash_5v_page_write_init; new case now PASSES; mem_util_blank_check appears exactly once in flash_5v_page.cpp (the pre-existing CMD_BLANK_CHECK dispatch arm, not inside write_init); FLAG_CAN_ERASE and flash_5v_page_erase_execute occurrence counts unchanged from pre-task (1 and 4); the four out-of-scope handlers' blank-check counts unchanged; native/native_nodevtools agree at 170 cases/17 suites; check_erase_no_vpp.py, check_no_log_in_sdp_window.py, check_dispatch.py, test_dispatch_mirror.py and test_sdp_table_parity.py all pass; git diff --quiet holds on tools/check_dispatch.py"
    requirement: "ERASE-02"
    verification:
      - kind: unit
        ref: "pio test -e native, pio test -e native_nodevtools, check_erase_no_vpp.py, check_no_log_in_sdp_window.py, check_dispatch.py, pytest tests/test_dispatch_mirror.py tests/test_sdp_table_parity.py"
        status: pass
    human_judgment: false

duration: 35min
completed: 2026-08-21
status: complete
---

# Phase 153 Plan 06: Delete the 0x05 Pre-Write Blank Check Summary

**Located the flash4 (0x05) blank-check conditional in code at `flash_5v_page.cpp:88-90` (correcting a stale pattern-map figure of 87-89), then deleted it, proven by a native case observed failing before the deletion and passing after, with the sibling erase-on-write block and four other-protocol blank checks provably untouched.**

## Performance

- **Duration:** ~35 min
- **Tasks:** 2/2 completed
- **Files modified:** 2

## Accomplishments

- **Located the conditional in code, not by assumed symmetry.** Read
  `flash_5v_page_write_init` (lines 74-91) directly and measured the blank-check
  conditional's real position: **lines 88-90**, quoted verbatim:
  ```cpp
  88:    if (!is_flag_set(FLAG_SKIP_BLANK_CHECK)) {
  89:        mem_util_blank_check(handle);
  90:    }
  ```
  This is `153-RESEARCH.md`'s original figure (88-90), **not** the `153-PATTERNS.md`
  "correction" to 87-89 that the plan cited as the pattern map's finding — line 87
  is the closing brace of the unrelated `FLAG_CAN_ERASE` block above it, confirmed
  by counting lines directly in the file before editing. ERASE-02's
  located-in-code requirement is discharged by this measurement, not by symmetry
  with `0x0D`.
- Added `make_write_init_handle_blank_check_enabled` — the only factory in
  `test_val_5v_page.cpp` that drives `flash_5v_page_write_init` itself (every
  other case in the suite bypasses `write_init` and calls `operation_main`
  directly) — with `FLAG_CAN_ERASE` and `FLAG_SKIP_BLANK_CHECK` both clear and
  `mem_size = 2048` (`BLANK_CHECK_CHUNK_SIZE`, though the oracle does not depend
  on this value). Added `test_5v_page_write_init_no_blank_check_with_flag_clear_erase02`,
  registered in `main`, without touching `make_write_handle_with_data` or any of
  the 13 pre-existing cases.
- Ran the suite and observed the new case FAIL for the intended reason:
  assertion 1 (`TEST_ASSERT_FALSE_MESSAGE(is_operation_in_progress(&h), ...)`)
  fired, because `mem_util_blank_check` still ran unconditionally with the skip
  flag clear. All 13 pre-existing cases passed in the same run (14 cases total:
  1 failed, 13 succeeded).
- Deleted the three-line conditional at `flash_5v_page.cpp:88-90`, replacing it
  with a comment naming `D-07`, ERASE-02 and `D-153-05`, and describing the
  `FLAG_CAN_ERASE` erase-on-write block above it generically (as "the
  erase-enable block" / "a bulk-erase call") rather than by literal token — a
  deliberate wording choice, required by this plan's acceptance criteria, so
  `grep -c 'FLAG_CAN_ERASE'` and `grep -c 'flash_5v_page_erase_execute'` stay
  pinned at their unchanged pre-task values (1 and 4 respectively) rather than
  being inflated by the comment naming them directly.
- The new case flipped GREEN. `pio test -e native` and
  `pio test -e native_nodevtools` both report **170 cases / 17 suites** (up
  from the 169/17 baseline recorded in this plan's critical notes), agreeing
  with each other. `scripts/check_erase_no_vpp.py`, `tools/check_no_log_in_sdp_window.py`
  and `tools/check_dispatch.py` all still pass; `tests/test_dispatch_mirror.py`
  and `tests/test_sdp_table_parity.py` pass; `git diff --quiet -- tools/check_dispatch.py`
  holds.
- Rebuilt `uno` and `leonardo` before and after the deletion (via a targeted
  single-file `git checkout <pre-task-commit> -- src/proms/flash_5v_page.cpp`
  / restore, working tree left clean before and after) to confirm the change
  compiles cleanly and to measure the delta: flash usage dropped by **30
  bytes on both targets** (25578→25548 uno, 27660→27630 leonardo). This figure
  is reported for visibility only — plan 14 owns the formal MERGE-05/Caterina-cliff
  measurement and any named `v153` exemption; no claim about that budget is
  made here. Both targets shrank, as expected for a pure deletion.

## Task Commits

1. **Task 1: Locate and quote the 0x05 conditional, add write-INIT case, OBSERVE it fail** - `bf01e2b` (test)
2. **Task 2: Delete the 0x05 blank-check conditional and turn the case GREEN** - `dcb30fe` (feat)

**Plan metadata:** (final commit hash recorded after this summary is committed)

## Files Created/Modified

- `firestarter/test/native/avr/test_val_5v_page/test_val_5v_page.cpp` - added
  `#include "operation_utils.h"`, new factory
  `make_write_init_handle_blank_check_enabled`, and new case
  `test_5v_page_write_init_no_blank_check_with_flag_clear_erase02`, registered
  via `RUN_TEST`
- `firestarter/src/proms/flash_5v_page.cpp` - deleted the pre-write
  blank-check conditional at the tail of `flash_5v_page_write_init` (lines
  88-90), replaced with a comment citing `D-07`, ERASE-02, `D-153-05`

## Located-in-Code Evidence (Task 1)

Verbatim, with measured line numbers, before any edit:

```cpp
88:    if (!is_flag_set(FLAG_SKIP_BLANK_CHECK)) {
89:        mem_util_blank_check(handle);
90:    }
```

This is `153-RESEARCH.md`'s original figure of 88-90. `153-PATTERNS.md`'s
"correction" to 87-89 is itself incorrect — line 87 is `}`, the closing brace
of the preceding, unrelated `FLAG_CAN_ERASE` block (lines 80-86), which stays
untouched. The conditional's existence (not absence) is confirmed: this was
not assumed by symmetry with `0x0D`.

## Observed RED (Task 1, before the deletion)

Unity failure line, verbatim:

```
test/native/avr/test_val_5v_page/test_val_5v_page.cpp:334: test_5v_page_write_init_no_blank_check_with_flag_clear_erase02: ERASE-02: is_operation_in_progress must be FALSE after exactly one flash_5v_page_write_init call with FLAG_SKIP_BLANK_CHECK clear -- mem_util_blank_check is the only setter of this flag on the write-INIT path, so TRUE here would mean the pre-write blank check still ran and left a multi-call INIT loop pending	[FAILED]
```

Assertion 1 fired first (assertions 2-4 were never reached in that run, since
Unity aborts the test function on the first failed `TEST_ASSERT_*`). All 13
pre-existing cases passed in the same run (14 cases: 1 failed, 13 succeeded).
The runner also emitted a `SIGHUP` after recording the failure — the same
non-blocking artifact `153-02-SUMMARY.md` already noted for this sandboxed
test runner's handling of a failing Unity process; it did not recur once the
case passed post-deletion.

## After the deletion (Task 2)

- `test_5v_page_write_init_no_blank_check_with_flag_clear_erase02` passes: all
  4 assertions hold — `is_operation_in_progress(&h)` FALSE, `h.progress_data`
  NULL, `h.response_code` not `RESPONSE_CODE_ERROR`, and no VPP-enable control
  bit in the recording.
- `grep -c 'mem_util_blank_check' src/proms/flash_5v_page.cpp` → **1**. This
  differs from `153-02`'s `eeprom_28c.cpp` result of 1 (also the
  `CMD_BLANK_CHECK` arm) in one respect: **unlike `eeprom_28c.cpp`, protocol
  `0x05` DOES have its own `CMD_BLANK_CHECK` dispatch arm**
  (`configure_flash_5v_page`, line 52: `case CMD_BLANK_CHECK: handle->firestarter_operation_main = mem_util_blank_check;`).
  The plan's acceptance criteria anticipated this ("If the count is non-zero,
  the summary must name the surviving site and justify it") — the single
  surviving hit is that pre-existing standalone-`blank`-command dispatch arm,
  not any reference inside `write_init`. This is the legitimate remaining
  reference this plan's own criteria foresaw, and `blank` remains available
  as its own step (ERASE-05 non-regression).
- `grep -c 'FLAG_SKIP_BLANK_CHECK' src/proms/flash_5v_page.cpp` → **1**, inside
  the replacement comment only (not inside any function body) — one of the two
  acceptance-criteria-permitted outcomes.
- `grep -c 'FLAG_CAN_ERASE'` → **1** and `grep -c 'flash_5v_page_erase_execute'`
  → **4**, both **unchanged** from their pre-task values (measured against the
  Task-1 commit, before Task 2's edit) — the erase-on-write block survives
  intact, and the replacement comment names it descriptively rather than by
  literal token so as not to inflate either count.
- The blank-check counts in `eprom.cpp` (5), `flash_intel.cpp` (2) and
  `flash_nor_unlock.cpp` (3) are unchanged — this phase's policy stays scoped
  to the two auto-erasing protocols only.
- `pio test -e native` and `pio test -e native_nodevtools` both report
  **170 test cases: 170 succeeded** across 17 suites, agreeing with each other.
- `python3 scripts/check_erase_no_vpp.py` → `PASS: eeprom28c_erase_execute() ...`
  exit 0 (this checker's scope is the `0x0D` erase body from plan 05; it is
  unaffected by this plan's `0x05` edit and confirmed still green).
- `check_no_log_in_sdp_window.py` → `PASS:` exit 0; `check_dispatch.py` →
  `PASS: all 746 chips scanned ...` exit 0;
  `pytest tests/test_dispatch_mirror.py tests/test_sdp_table_parity.py` → 7
  passed.
- `git diff --quiet -- tools/check_dispatch.py` holds (exit 0) — that checker
  itself is untouched, per `D-153-03`'s independent invariant.
- `git diff` on `flash_5v_page.cpp` shows exactly one hunk: the three-line
  deletion plus the replacement comment.

## Decisions Made

- Confirmed and corrected a stale line-number claim rather than trusting it:
  the real conditional is at lines 88-90, matching `153-RESEARCH.md`'s
  original figure; `153-PATTERNS.md`'s "correction" to 87-89 was itself wrong.
  No decisions document was updated for this (a measurement correction, not a
  new policy decision) — recorded here for the record per this plan's
  explicit instruction to report the real figure.
- No new `D-153-NN` decision needed — this plan implements the already-settled
  `D-153-05` (recorded by plan 01/02) rather than deciding anything new. The
  replacement comment restates `D-153-05`'s prohibition at the exact
  `0x05` site where an executor mirroring this protocol's own shape into
  `eeprom28c_write_init` would be tempted to add an erase-on-write block.

## Deviations from Plan

None — plan executed exactly as written. The comment-wording choice to
describe the `FLAG_CAN_ERASE` block generically (rather than by literal
token) was already anticipated by this plan's acceptance criteria (the
grep-count pinning requirement), not an improvisation outside its scope.

## Issues Encountered

None blocking. The `SIGHUP` runner artifact noted above under "Observed RED"
is a non-blocking environment observation, consistent with the same artifact
already on record in `153-02-SUMMARY.md`.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- ERASE-02's located-in-code requirement is discharged by measurement, not
  assumption — `firestarter write` on `0x05` now performs no blank check
  whether or not the skip flag is set, and write-INIT remains single-shot.
- `flash_5v_page_erase_execute` (the hardware `CTRL_VPP_REGULATOR_ENABLE`
  erase path) and the `FLAG_CAN_ERASE`-gated erase-on-write block above the
  deleted conditional are both provably untouched (occurrence counts pinned).
- The `CMD_BLANK_CHECK` dispatch arm and standalone `blank` command are
  untouched and unaffected (ERASE-05 non-regression) on protocol `0x05`.
- **ERASE-02 is left `In Progress`, not `Complete`**, in `REQUIREMENTS.md`:
  plan 13 also claims it (correcting the prose docs, e.g. `doc/PROTOCOLS.md`'s
  `0x05` erase-policy description) and has not run yet. Only plan 13 should
  flip it to Complete.
- Native case/suite counts (170/17, both environments) are the new reference
  point for plan 14's cold-baseline comparison — up from 153-02's 164/17 by
  6 (accounting for plans 03/04/05's own additions plus this plan's +1).
- Plan 14 has a fresh AVR size delta to fold in: both targets shrank by 30 B
  from this deletion (uno 25578→25548, leonardo 27660→27630), ahead of any
  additive change later plans in this phase will make. All firmware source
  changes for ERASE-01/ERASE-02 are now complete.

---
*Phase: 153-write-path-erase-policy*
*Completed: 2026-08-21*

## Self-Check: PASSED

- FOUND: `firestarter/test/native/avr/test_val_5v_page/test_val_5v_page.cpp`
- FOUND: `firestarter/src/proms/flash_5v_page.cpp`
- FOUND: `.planning/phases/153-write-path-erase-policy/153-06-SUMMARY.md`
- FOUND: commit `bf01e2b`
- FOUND: commit `dcb30fe`
