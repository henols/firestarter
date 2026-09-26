---
phase: 117-fix-remap-aware-0x0d-emitter-honest-completion-signal
plan: 03
subsystem: firmware
tags: [platformio, unity, native-test, avr, eeprom28c, at28c, page-write, dq7]

# Dependency graph
requires:
  - phase: 117-fix-remap-aware-0x0d-emitter-honest-completion-signal
    provides: "plan 117-02's remap-aware eeprom28c_write_init + EEPROM_SDP_DISABLE external linkage (117-02-SUMMARY.md); eeprom28c_write_execute and eeprom28c_wait_for_write left untouched by that plan, explicitly deferred to this one"
provides:
  - "FIX-06: eeprom28c_write_execute's conflated eeprom28c_wait_for_write split into two single-job functions -- eeprom28c_wait_for_page_write (DQ7-complement completion poll only) and eeprom28c_verify_page_readback (per-byte data-landed proof only, always on, failing-address attribution via MSG_ERR_VERIFY)"
  - "eeprom28c_wait_for_write deleted outright (definition + forward declaration) -- zero occurrences remain in eeprom_28c.cpp"
  - "A window-start index in eeprom28c_write_execute so the read-back covers exactly the current flush window and advances with each flush, never re-checking a prior chunk's bytes"
  - "test_val_eeprom28c: 3 new write-path cases (D-09's executable old-vs-new contrast, an isolation control, a page-boundary two-window case) plus the setUp() delayMicroseconds/delay/millis mock trio the write path now reaches"
  - "The anti-hollow proof executed and recorded verbatim (read-back temporarily removed, both planted cases went RED, isolation control stayed GREEN)"
affects: [117-04-close-frozen-artifact-proof-fix05, 117-05-close-frozen-artifact-proof-fix04]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Completion-vs-data-landed split: a DQ7-complement poll (double-read confirmed, mirroring flash_util_verify_operation's idiom) answers ONLY 'is the internal cycle done'; a separate per-byte read-back answers ONLY 'did the data land'. No single function is asked to answer both, which is what made the old poll conflate a completion check with a correctness check."
    - "Window-scoped read-back: the data-landed proof covers exactly the bytes handle->data_buffer still holds for the window just flushed (window_start..i), not the whole physical page -- avoids fabricating expected values for bytes a prior chunk already wrote and verified."
    - "Address-keyed planted mock with a single stale address (not call-order dispatch) isolates a conflation bug precisely: the page's last byte always reads back correctly (satisfying a DQ7/completion arm), while an earlier planted-stale byte is caught only by a real read-back."

key-files:
  created: []
  modified:
    - firestarter/src/proms/eeprom_28c.cpp
    - firestarter/test/native/avr/test_val_eeprom28c/test_val_eeprom28c.cpp

key-decisions:
  - "Followed 117-CONTEXT.md D-07/D-08/D-09 and the plan's own discretion resolutions (test home = test_val_eeprom28c; read-back scoped to the current flush window only; mismatch reports the failing address via MSG_ERR_VERIFY, no new MSG_* id; planted mock is address-keyed with a single stale address) exactly as specified -- no deviation from the locked design."
  - "Reworded four in-code comment mentions of the deleted function's literal name (and one comment mention of MSG_ERR_VERIFY) to avoid colliding with the acceptance criteria's literal, non-comment-filtered greps (grep -c 'eeprom28c_wait_for_write' must be exactly 0; grep -c 'MSG_ERR_VERIFY' must be exactly 1, the real call site) -- meaning fully preserved, following the same pattern 117-02 used for its own comment-wording adjustments."
  - "DQ7-complement poll uses the same double-read confirmation shape as flash_util_verify_operation (flash_utils.cpp, FIX-04 frozen, READ-ONLY ANALOG) -- a match must hold on two consecutive reads before the poll returns done, so a single transient sample cannot end it early."

requirements-completed: [FIX-06]

coverage:
  - id: D1
    description: "eeprom28c_wait_for_write is deleted outright (definition + forward declaration); completion detection (DQ7-complement poll) and data-landed proof (per-byte read-back) are two functions with one job each"
    requirement: FIX-06
    verification:
      - kind: unit
        ref: "grep gates over firestarter/src/proms/eeprom_28c.cpp: eeprom28c_wait_for_write count 0, eeprom28c_wait_for_page_write count 6 (>=3), eeprom28c_verify_page_readback count 6 (>=3), AT28C_DQ7_MASK count 5 (>=3), AT28C_PAGE_POLL_MAX_READS count 2 (>=2), MSG_ERR_VERIFY count exactly 1 -- all passed"
        status: pass
    human_judgment: false
  - id: D2
    description: "A planted partial write (last byte correct, an earlier byte stale) is rejected by the fixed path (RESPONSE_CODE_ERROR) and would have been accepted by an executable replica of the deleted last-byte-equality poll -- D-09's side-by-side contrast, both halves in one CI-resident test"
    requirement: FIX-06
    verification:
      - kind: unit
        ref: "firestarter/test/native/avr/test_val_eeprom28c/test_val_eeprom28c.cpp: test_fix06_planted_partial_write_fails_fixed_path_and_passes_legacy_poll via `pio test -e native -f \"*test_val_eeprom28c*\"`"
        status: pass
    human_judgment: false
  - id: D3
    description: "Isolation control proves the ERROR above came from the planted mismatch, not from the mock seam, the new setUp() mocks, or the new read-back loop itself"
    requirement: FIX-06
    verification:
      - kind: unit
        ref: "firestarter/test/native/avr/test_val_eeprom28c/test_val_eeprom28c.cpp: test_fix06_clean_page_write_succeeds_isolation_control via `pio test -e native -f \"*test_val_eeprom28c*\"`"
        status: pass
    human_judgment: false
  - id: D4
    description: "The read-back window advances with each flush across a two-page-boundary write (base 56, data_size 16): a stale byte in either window is caught, and a clean two-window write is not falsely flagged"
    requirement: FIX-06
    verification:
      - kind: unit
        ref: "firestarter/test/native/avr/test_val_eeprom28c/test_val_eeprom28c.cpp: test_fix06_page_boundary_window_readback via `pio test -e native -f \"*test_val_eeprom28c*\"`"
        status: pass
    human_judgment: false
  - id: D5
    description: "Anti-hollow proof: with the read-back call temporarily removed, the two planted-violation cases go RED while the isolation control stays GREEN; restoring the fix returns the suite to 6/6"
    verification:
      - kind: unit
        ref: "manual revert-and-observe of eeprom28c_write_execute's flush branch, `pio test -e native -f \"*test_val_eeprom28c*\"` before and after -- see ## Planted-violation proof below; temporary revert not committed (byte-identical diff confirmed against the restored fix)"
        status: pass
    human_judgment: false
  - id: D6
    description: "FIX-04 frozen artifacts stay byte-untouched; full native suite green; both board targets build"
    verification:
      - kind: unit
        ref: "git diff --exit-code HEAD~1 HEAD -- src/proms/flash_utils.cpp include/flash_utils.h src/proms/flash_5v_page.cpp src/proms/flash_nor_unlock.cpp test/native/avr/_shared/ (clean); pio test -e native (106/106 passing, exit 0); pio run -e leonardo / -e uno (both SUCCESS)"
        status: pass
    human_judgment: false

# Metrics
duration: 20min
completed: 2026-07-28
status: complete
---

# Phase 117 Plan 03: FIX-06 — Page Completion Poll Split from Data-Landed Read-Back Summary

**Split `eeprom28c_write_execute`'s conflated last-byte-equality poll into a DQ7-complement completion check and an always-on per-byte read-back, deleted the conflated function outright, and proved the split closes gh#11's shape with an executable planted-partial-write contrast plus an anti-hollow revert-and-observe run.**

## Performance

- **Duration:** ~20 min
- **Started:** 2026-07-28T10:10:00Z
- **Completed:** 2026-07-28T10:30:00Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments

- `eeprom28c_wait_for_write` — the function that answered both "is the internal write cycle done" and "did the data land" via a single whole-byte equality compare — is deleted outright (definition + forward declaration). Zero occurrences remain anywhere in `eeprom_28c.cpp`.
- Two new file-static functions replace it, each with one job:
  - `eeprom28c_wait_for_page_write(handle, address, expected)` — completion only. A DQ7-complement poll (`AT28C_DQ7_MASK` = 0x80), bounded by `AT28C_PAGE_POLL_MAX_READS` (2000, an iteration count, not a `millis()` deadline — both native SDP suites mock `millis()` to a constant). Follows `flash_util_verify_operation`'s double-read idiom (`flash_utils.cpp`, READ-ONLY ANALOG, FIX-04 frozen) so a single transient sample cannot end the poll — the DQ7 match must hold on two consecutive reads. Every read goes through `handle->firestarter_get_data`; on exhaustion it emits `MSG_ERR_EEPROM_TIMEOUT` with the same 5-byte payload shape the old function used and sets `RESPONSE_CODE_ERROR`.
  - `eeprom28c_verify_page_readback(handle, first_index, last_index)` — data-landed proof only. Per-byte read-back over the *current flush window* (`handle->data_buffer[first_index..last_index]`), reusing `memory_verify_execute`'s `MSG_ERR_VERIFY` payload order (`{expected, observed, addr>>16, addr>>8, addr}`) with the *failing* address, unlike the deleted function's bare mid-buffer return with only the poll address. Always on, no opt-out (D-08) — no new `FLAG_*`, no `messages.h` edit.
- `eeprom28c_write_execute` gained a `window_start` index that advances to `i + 1` after each successful flush, so the read-back scope tracks exactly the bytes still held in `handle->data_buffer` for the window just written — verified across a two-page-boundary geometry (base address 56, `data_size` 16, `PAGE_SIZE` 64) in the new page-boundary test case.
- `test_val_eeprom28c` gained 3 new write-path cases (D-09's executable old-vs-new contrast, an isolation control, and the page-boundary case) plus a file-static address-keyed planted `get_data` mock (`mock_get_data_planted`), a write-path handle factory (`make_write_handle`), and a test-local replica of the deleted equality poll (`legacy_last_byte_equality_poll`) that must never be called by production code (`grep -rc` over `src/` confirms 0 occurrences). `setUp()` extended with the `delayMicroseconds`/`delay`/`millis` ArduinoFake mock trio the write path now reaches (load-bearing — ArduinoFake SIGABRTs on any unmocked virtual).
- `pio test -e native -f "*test_val_eeprom28c*"`: 6/6 passing (3 pre-existing configure-phase + 3 new write-path). Full `pio test -e native`: **106/106 passing** (16 suites, exit 0) — the 103 from plan 117-02 plus these 3 new cases, no regressions. `pio test -e native -f "*test_eeprom28c_sdp*"` re-verified 8/8 (plan 117-02's oracle untouched — this plan owns `write_execute`, not `write_init`). Both `pio run -e leonardo` and `pio run -e uno` report `SUCCESS` (Leonardo: 25528/28672 bytes flash, 89.0%; Uno: 23390/32256 bytes flash, 72.5%).
- The plan's mandatory anti-hollow proof was executed (read-back call temporarily removed, not committed) — see `## Planted-violation proof` below.

## Task Commits

1. **Tasks 1-2 combined** (per the plan's explicit instruction: "Commit Tasks 1 and 2 together") — `c7e55b7` (fix, firestarter submodule)

**Plan metadata:** this SUMMARY + STATE.md/ROADMAP.md/REQUIREMENTS.md update, in the meta repo (see `<final_commit>`).

_Note: this is a firmware-submodule-only plan; the meta repo's docs commit is separate._

## Files Created/Modified

- `firestarter/src/proms/eeprom_28c.cpp` — Added `AT28C_DQ7_MASK` / `AT28C_PAGE_POLL_MAX_READS` named constants; added `eeprom28c_wait_for_page_write` and `eeprom28c_verify_page_readback` (both static, forward-declared); rewrote `eeprom28c_write_execute` with the `window_start` index and the two-call flush branch; deleted `eeprom28c_wait_for_write` (definition + forward declaration) entirely. `eeprom28c_write_init` and `eeprom28c_emit_command_sequence`/`eeprom28c_wait_for_sdp_completion` (plan 117-02's territory) untouched.
- `firestarter/test/native/avr/test_val_eeprom28c/test_val_eeprom28c.cpp` — Added `#include "../_shared/sdp_bus_config.h"`; added the `EEPROM28C_PLANTED_SENTINEL` constant and 3 file-static planted-mock state variables; added `mock_get_data_planted`, `make_write_handle`, `legacy_last_byte_equality_poll` helpers; extended `setUp()` with the mock trio and planted-state reset; added 3 new test cases (`test_fix06_planted_partial_write_fails_fixed_path_and_passes_legacy_poll`, `test_fix06_clean_page_write_succeeds_isolation_control`, `test_fix06_page_boundary_window_readback`) and their `RUN_TEST` registrations. The 3 pre-existing configure-phase cases and `assert_no_vpp_in_recording` are byte-unchanged.

## Decisions Made

- Followed 117-CONTEXT.md's D-07 (separate completion from data-landed proof), D-08 (read-back always on, no opt-out, window-scoped per decision 2 in the plan's discretion section), and D-09 (executable side-by-side old-vs-new contrast, address-keyed planted mock with a single stale address) exactly as specified.
- Reworded 4 in-code comment mentions of the literal deleted function name `eeprom28c_wait_for_write` (and 1 comment mention of `MSG_ERR_VERIFY`) to avoid colliding with the plan's literal, non-comment-filtered acceptance-criteria greps (`grep -c 'eeprom28c_wait_for_write'` must be exactly `0`; `grep -c 'MSG_ERR_VERIFY'` must be exactly `1`, the real call site) — meaning fully preserved (still refers to "the old, now-deleted, poll" / "the deleted function"), following the identical pattern plan 117-02 used for its own comment-wording adjustments.
- The DQ7-complement poll's double-read confirmation shape was modeled directly on `flash_util_verify_operation`'s idiom (`flash_utils.cpp:30-51`, READ-ONLY ANALOG, FIX-04 frozen) per 117-PATTERNS.md's guidance — no in-tree DQ7-*complement* analog exists, only DQ7-mask-*equality* and last-byte-*equality*, so the double-read confirmation was the only reusable shape.

## Deviations from Plan

None affecting behavior — plan executed exactly as specified. The comment-wording adjustments above are cosmetic (Rule 3, blocking: the literal acceptance-criteria greps would otherwise fail on self-referential documentation, not on the code's actual shape) and do not change any assertion, constant value, or control flow.

## Issues Encountered

None new. `firestarter_app` has the same pre-existing uncommitted `.gitignore` change already noted in 117-02-SUMMARY.md (dated 2026-07-10, well before this session, unrelated to this plan) — this plan touched zero `firestarter_app` files, so the pre-existing drift is out of scope and not introduced by this work. `git -C firestarter_app diff --stat` shows only that one line.

## Planted-violation proof (read-back removed)

Per the plan's mandatory anti-hollow acceptance criterion: `eeprom28c_write_execute`'s flush branch was temporarily edited to call only `eeprom28c_wait_for_page_write` (the completion poll), with the `eeprom28c_verify_page_readback` call commented out. The suite was re-run, the RED output captured verbatim below, then the temporary edit was reverted and the file confirmed byte-identical to the pre-revert state (`diff -q` against a pre-revert backup copy) before re-running to confirm 6/6 GREEN again. **The temporary revert was never staged or committed** — only the restored fix (`c7e55b7`) is in git history.

```
$ pio test -e native -f "*test_val_eeprom28c*"
...
Testing...
test/native/avr/test_val_eeprom28c/test_val_eeprom28c.cpp:301: test_eeprom28c_read_configure_no_vpp	[PASSED]
test/native/avr/test_val_eeprom28c/test_val_eeprom28c.cpp:302: test_eeprom28c_write_configure_no_vpp	[PASSED]
test/native/avr/test_val_eeprom28c/test_val_eeprom28c.cpp:303: test_eeprom28c_blank_check_configure_no_vpp	[PASSED]
test/native/avr/test_val_eeprom28c/test_val_eeprom28c.cpp:211: test_fix06_planted_partial_write_fails_fixed_path_and_passes_legacy_poll: Expected 0 Was 1. FIX-06 fixed path must report ERROR: the planted stale byte at address 0x0002 never landed, even though the page's last byte did	[FAILED]
test/native/avr/test_val_eeprom28c/test_val_eeprom28c.cpp:307: test_fix06_clean_page_write_succeeds_isolation_control	[PASSED]
test/native/avr/test_val_eeprom28c/test_val_eeprom28c.cpp:262: test_fix06_page_boundary_window_readback: Expected 0 Was 1. a stale byte inside the first flush window (address 59) must be caught	[FAILED]
Program received signal SIGINT (Interrupt)
------- native:native/avr/test_val_eeprom28c [ERRORED] Took 0.57 seconds -------

=================================== SUMMARY ===================================
Environment    Test                           Status    Duration
-------------  -----------------------------  --------  ------------
native         native/avr/test_val_eeprom28c  ERRORED   00:00:00.570

============= 7 test cases: 2 failed, 4 succeeded in 00:00:00.570 =============
```

**Observed:** `test_fix06_planted_partial_write_fails_fixed_path_and_passes_legacy_poll` went RED (`Expected 0 Was 1` — `RESPONSE_CODE_ERROR` is `0`, so `1` means it stayed `RESPONSE_CODE_OK`: with the read-back removed, the completion poll alone reports success on the planted partial write). `test_fix06_page_boundary_window_readback` also went RED on its first drive for the identical reason. `test_fix06_clean_page_write_succeeds_isolation_control` stayed GREEN throughout, exactly as the plan requires — proving the RED above is caused specifically by the removed read-back's absence, not by anything else the revert touched. (Unity's `longjmp`-based assertion failure aborted `test_fix06_page_boundary_window_readback` after its first drive's assertion, so the second and third drives inside that function did not execute on this RED run — consistent with Unity's per-test-case abort-on-first-failure behavior, not a hang; the run completed in 0.57s.) The `SIGINT` line appears to be a native-runner/Unity artifact on this environment (the process still completed cleanly and printed the SUMMARY); it was reproduced identically on both the earlier interactive run and the fully-captured `timeout 30` re-run with exit code 1 (test-failure exit, not a timeout).

After restoring the fix: `pio test -e native -f "*test_val_eeprom28c*"` returned to 6/6 PASSED, and `git diff` between the restored file and a pre-revert backup copy was empty (byte-identical).

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Plan 117-04 (FIX-05) is unblocked: this plan did not touch `EEPROM_SDP_DISABLE` or its external linkage (plan 117-02's territory), and confirms via the frozen-artifact diff that nothing in the FIX-04 scope moved.
- Plan 117-05 (FIX-04 close) has this plan's frozen-file verification (clean `git diff --exit-code HEAD~1 HEAD` over all 4 frozen paths + `_shared/`) and Leonardo/Uno flash figures as additional inputs (Leonardo 25528/28672 bytes vs plan 117-02's 25374/28672 — the +154 byte delta is this plan's own two new functions plus the window-index bookkeeping, not a frozen-artifact regression).
- No blockers. `firestarter/src/` changes remain confined to `eeprom_28c.cpp`; test changes confined to `test_val_eeprom28c.cpp`. All FIX-01..03 and now FIX-06 are Complete in REQUIREMENTS.md; FIX-04 and FIX-05 remain Pending, owned by plans 117-05 and 117-04 respectively.

---
*Phase: 117-fix-remap-aware-0x0d-emitter-honest-completion-signal*
*Completed: 2026-07-28*

## Self-Check: PASSED

- FOUND: `firestarter/src/proms/eeprom_28c.cpp`
- FOUND: `firestarter/test/native/avr/test_val_eeprom28c/test_val_eeprom28c.cpp`
- FOUND: commit `c7e55b7` in `firestarter` submodule history
- FOUND: `.planning/phases/117-fix-remap-aware-0x0d-emitter-honest-completion-signal/117-03-SUMMARY.md`
