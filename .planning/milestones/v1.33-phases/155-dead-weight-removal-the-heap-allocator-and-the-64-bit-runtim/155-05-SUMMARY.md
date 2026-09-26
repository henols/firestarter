---
phase: 155-dead-weight-removal-the-heap-allocator-and-the-64-bit-runtim
plan: "05"
subsystem: firmware
tags: [firestarter, avr, memory-management, native-tests, unity, heap-removal]

requires:
  - phase: 155-01
    provides: "the before-figures record (handle sizes, RAM headroom derivation, symbol tables) this plan's comment quotes verbatim"
  - phase: 155-02
    provides: "scripts/check_no_heap_or_64bit_symbols.py, the link-time gate this plan's change is measured against"
  - phase: 155-04
    provides: "the 64-bit-runtime half of the phase's flash saving, already landed on this branch's HEAD"
provides:
  - "firestarter_handle_t no longer carries progress_data; mem_util_blank_check keeps its saved address in a file-scope static"
  - "the firmware image is heap-free on all three AVR targets (malloc/free/realloc/calloc/__brkval/__flp/__malloc_* all absent)"
  - "the unchecked-allocation dereference in mem_util_blank_check is closed by removing the allocation, not by adding a null check"
  - "both native suites' 'same statement' comment claim corrected to the true, stronger 'unconditionally adjacent statements' formulation, in three comment blocks"
affects: [155-06]

tech-stack:
  added: []
  patterns:
    - "file-scope static replacing a single-caller heap allocation for cross-call state in an event-driven, single-threaded firmware function"

key-files:
  created: []
  modified:
    - firestarter/src/proms/memory.cpp
    - firestarter/include/firestarter.h
    - firestarter/test/native/avr/test_val_5v_page/test_val_5v_page.cpp
    - firestarter/test/native/avr/test_eeprom28c_sdp/test_eeprom28c_sdp.cpp

key-decisions:
  - "Header edit (drop progress_data) and both native test-file edits landed in one commit, deliberately, because removing the struct member without the test edits is a hard compile error in both suites (172 -> 127 cases)."
  - "The rejected alternative -- keeping a permanently-NULL void* progress_data field just so the two NULL assertions kept compiling -- was considered and rejected: it would cost exactly 2 B of RAM per target and make both assertions vacuous (NULL == NULL on a field nothing writes), this repo's own named hollow-gate failure mode."
  - "Neither test file's replacement comment uses the literal identifier text 'progress_data' -- the acceptance criteria required a summed grep count of 0 for that string across all four edited files, so the comments describe 'the removed heap-allocated handle field' instead of naming it."

requirements-completed: []

coverage:
  - id: D1
    description: "mem_util_blank_check's cross-call saved address moved from a malloc'd struct to a file-scope static (blank_check_saved_address) in src/proms/memory.cpp; firestarter_handle_t::progress_data removed"
    requirement: "DEAD-01"
    verification:
      - kind: unit
        ref: "pio test -e native (test/native/avr/test_val_5v_page, test/native/avr/test_eeprom28c_sdp) -- 172/172, 17 suites"
        status: pass
      - kind: other
        ref: "python3 scripts/check_no_heap_or_64bit_symbols.py -- PASS: heap=0, 64bit=0, anchors=2/2 on uno, uno328pb, leonardo"
        status: pass
    human_judgment: false
  - id: D2
    description: "The unchecked-allocation dereference (progress_data->address = handle->address with no NULL test, immediately after malloc) is closed by removing the allocation entirely, and recorded here as a latent defect closed rather than incidental cleanup"
    requirement: "DEAD-02"
    verification:
      - kind: other
        ref: "git -C firestarter diff 98e70af~1 98e70af -- src/proms/memory.cpp (the malloc/cast/deref/free sequence is gone; blank_check_saved_address direct-assigns and direct-reads)"
        status: pass
    human_judgment: false
  - id: D3
    description: "Both native suites (test_val_5v_page.cpp, test_eeprom28c_sdp.cpp) updated to drop their h.progress_data == NULL assertions; the surviving is_operation_in_progress assertion still pins the behaviour; the false 'same statement' claim corrected to the true 'unconditionally adjacent statements' formulation in three comment blocks; the third stale memory.cpp line-number pin replaced by a symbol name; the rejected alternative recorded with its measured 2 B cost"
    requirement: "DEAD-06"
    verification:
      - kind: unit
        ref: "pio test -e native and pio test -e native_nodevtools -- both 172/172, 17 suites, run sequentially"
        status: pass
      - kind: other
        ref: "grep -c 'unconditionally adjacent statements' across both test files == 3; grep -c 'the same statement' == 0; avr-nm --print-size handle: 601/601/1113 B vs before-figures' 603/603/1115 B == 2 B cost"
        status: pass
    human_judgment: false

duration: 40min
completed: 2026-08-23
status: complete
---

# Phase 155 Plan 05: The atomic heap-removal commit and DEAD-06's test-suite update Summary

**Removed the sole `malloc`/`free` call site in the firmware -- a 4-byte allocation carrying a saved address across two calls of `mem_util_blank_check` -- replacing it with a file-scope static, and closed the unchecked-allocation dereference that call carried, in one compiler-forced commit updating both native test suites.**

## Performance

- **Duration:** ~40 min
- **Completed:** 2026-08-23T10:51:35Z
- **Tasks:** 2 (1 code commit, 1 verification-only)
- **Files modified:** 4

## Accomplishments

- `firestarter_handle_t::progress_data` (a `void*`) is deleted from `include/firestarter.h`.
- `src/proms/memory.cpp` no longer contains any `malloc`/`free` call; a new file-scope static `blank_check_saved_address` (`uint32_t`) carries the address across the two dispatch calls, with a comment recording the removed allocation's cost, the defect it carried, the corrected per-target RAM derivation, why the static is correct here, and the net RAM ledger.
- Both native test suites (`test_val_5v_page.cpp`, `test_eeprom28c_sdp.cpp`) had their `TEST_ASSERT_NULL_MESSAGE(h.progress_data, ...)` assertions deleted and replaced with explanatory comments; the companion `is_operation_in_progress` assertions are unchanged and still pin the behaviour.
- The false "same statement" claim (RESEARCH C-5) -- that the surviving `is_operation_in_progress` assertion is set by the same statement as the removed allocation -- is corrected to the true, strictly stronger formulation ("unconditionally adjacent statements in the same then-branch of the same `if`, with no intervening control flow, early return or condition") in the three comment blocks that needed it: the case-preceding comment and the assertion-replacement comment in `test_val_5v_page.cpp`, and the assertion-replacement comment in `test_eeprom28c_sdp.cpp`.
- The third stale `memory.cpp:NNN` line-number pin (`test_val_5v_page.cpp`'s factory comment, previously pinned to a line that was already wrong) is replaced by naming the `BLANK_CHECK_CHUNK_SIZE` symbol instead of a line number. The one pre-existing stale pin that does not mention the removed field (`test_eeprom28c_sdp.cpp:97`, `mem_util_set_address`) was left byte-unchanged, as instructed.
- The firmware is now heap-free on all three AVR targets: `python3 scripts/check_no_heap_or_64bit_symbols.py` exits 0 with `heap=0, 64bit=0, anchors=2/2` on `uno`, `uno328pb` and `leonardo` (the 64-bit half was already cleared by plan 04; this plan clears the heap half, which is the phase's headline link-time proof).
- Measured flash/RAM on all three targets matches the plan's stated target exactly: `uno` 24660/1567, `uno328pb` 24708/1573, `leonardo` 26804/2008 -- the full phase saving now realized (plan 04's half plus this plan's heap-removal half).
- Measured the rejected alternative's cost directly: `avr-nm --print-size` reports the `handle` object at 601 B on `uno`/`uno328pb` and 1113 B on `leonardo`, exactly 2 B less than the before-figures' 603/603/1115 B -- confirming the retained-dead-field alternative would cost exactly 2 B of RAM per target, as DEAD-06 requires recording.

## Task Commits

1. **Task 1: The atomic four-file edit -- static, member removal and both native suites in ONE commit** - `98e70af` (refactor)
2. **Task 2: Post-commit verification and the DEAD-06 rejected-alternative record** - no commit (verification-only task; see below)

**Plan metadata:** committed separately per the executor's final-commit step.

## Files Created/Modified

- `firestarter/src/proms/memory.cpp` - deleted `blank_check_progress_data_t` typedef and the `malloc`/cast/deref/`free` sequence inside `mem_util_blank_check`; added file-scope static `blank_check_saved_address` with a rationale comment carrying the corrected RAM derivation
- `firestarter/include/firestarter.h` - deleted the `void* progress_data;` member from `firestarter_handle_t`
- `firestarter/test/native/avr/test_val_5v_page/test_val_5v_page.cpp` - three sites: factory comment's allocation description and stale line pin removed; case comment restated around the surviving `is_operation_in_progress` observable with the corrected adjacency formulation; the `h.progress_data == NULL` assertion deleted and replaced with an explanatory comment
- `firestarter/test/native/avr/test_eeprom28c_sdp/test_eeprom28c_sdp.cpp` - two sites: case comment's stale line pin removed; the `h.progress_data == NULL` assertion (Case 30 / ERASE-01) deleted and replaced with an explanatory comment carrying the same corrected formulation

## Decisions Made

- **One commit, not three.** Per the plan's critical constraint, the header edit and both native test-file edits landed together in `98e70af`. Verified this was in fact compiler-forced by nature of the change (both suites reference `h.progress_data`, which no longer exists once the header member is removed) rather than assumed.
- **No literal `progress_data` text survives anywhere in the four edited files**, including inside the replacement comments. The plan's own reference text (quoted in `155-PATTERNS.md`) uses the phrase `` `h.progress_data must be NULL` `` in its suggested replacement comment, but the acceptance criteria for this task require `grep -rc 'progress_data'` summed over all four files to equal exactly 0. Both replacement comments were written to describe "the removed heap-allocated handle field" instead of naming it, and the memory.cpp comment's one initial reference to `handle->progress_data` was rephrased to "the removed field." Verified: `grep -rc 'progress_data' <all four files> == 0`.
- **The rejected alternative is recorded with its measured cost, not estimated.** Retaining a permanently-NULL `void* progress_data` member solely to keep the two `TEST_ASSERT_NULL_MESSAGE` assertions compiling was considered and rejected: `avr-nm --print-size` shows the `handle` object drops from 603 B to 601 B on `uno`/`uno328pb` and from 1115 B to 1113 B on `leonardo` -- exactly 2 B per target, confirming the plan's stated cost. The alternative is rejected because the retained field would make both assertions vacuous (`NULL == NULL` on a field nothing writes), which is this project's own named hollow-gate failure mode (cited by `tests/test_check_size_baseline.py`'s docstring precedent). The surviving `is_operation_in_progress` assertion is set in the same unconditional branch as the removed allocation and is a strictly non-weaker witness.
- **DEAD-02 is recorded here as a latent defect CLOSED, not incidental cleanup:** the pre-change code wrote `progress_data->address = handle->address` immediately after `malloc(sizeof(blank_check_progress_data_t))` with no NULL test, on a part with under 473 B of **shared heap-and-stack headroom** (the corrected phrase; `ram_used` counts only `.data`/`.bss`, and the AVR call stack grows down into that same region during every operation, so the true margin at the allocation site was less than 473 B). It is closed by removing the allocation entirely -- because the allocation had no reason to exist -- rather than by adding a null check.

## Deviations from Plan

**1. [Rule 1 - Correctness] Corrected memory.cpp's `progress_data` self-reference to satisfy the plan's own acceptance criterion**
- **Found during:** Task 1, post-edit verification
- **Issue:** The first draft of the `blank_check_saved_address` rationale comment in `src/proms/memory.cpp` used the phrase "nothing outside this function ever read `handle->progress_data`" -- a literal use of the identifier the plan's own acceptance criteria require to be absent (`grep -rc 'progress_data'` summed over the four edited files must equal 0).
- **Fix:** Reworded to "nothing outside `mem_util_blank_check` ever read the removed field."
- **Files modified:** `firestarter/src/proms/memory.cpp`
- **Verification:** `grep -rc 'progress_data' <all four edited files>` sums to 0.
- **Committed in:** `98e70af` (part of the task 1 commit)

**2. [Rule 1 - Correctness] Rewrote the reference-style replacement comments in both test files to avoid the same literal identifier**
- **Found during:** Task 1, drafting the two assertion-replacement comments per `155-PATTERNS.md`'s quoted reference text
- **Issue:** `155-PATTERNS.md`'s quoted reference replacement comment for the deleted assertion uses the literal text `` `h.progress_data must be NULL` `` -- copying that phrasing verbatim would have violated this task's own acceptance criterion (grep count of 0 for `progress_data` across all four edited files).
- **Fix:** Both replacement comments (in `test_val_5v_page.cpp` and `test_eeprom28c_sdp.cpp`) describe "the companion \"must be NULL\" assertion on the removed heap-allocated handle field" instead of naming the field, while preserving the reference's substantive content (the assertion and field are both gone, the loss is a redundant probe not lost coverage, the corrected adjacency-statement reasoning).
- **Files modified:** `firestarter/test/native/avr/test_val_5v_page/test_val_5v_page.cpp`, `firestarter/test/native/avr/test_eeprom28c_sdp/test_eeprom28c_sdp.cpp`
- **Verification:** `grep -rc 'progress_data' <all four edited files>` sums to 0; `pio test -e native` and `-e native_nodevtools` both 172/172.
- **Committed in:** `98e70af` (part of the task 1 commit)

---

**Total deviations:** 2 auto-fixed (both Rule 1 -- corrections to satisfy the plan's own stated acceptance criteria; the plan's narrative text and its own literal grep-count criterion were in tension, and the criterion governed since it is mechanically checked).
**Impact on plan:** No scope creep. Both fixes are wording-only, confined to comments, and do not change any code behaviour, assertion, or the corrected substantive content the plan required.

## Issues Encountered

None beyond the deviations above. Both native legs (`native`, `native_nodevtools`) passed green on the first run each -- no re-run for load-flakiness was needed (RESEARCH.md Pitfall 5 / D-04).

## Verification Record (Task 2)

- `pio test -e native_nodevtools`: **172 test cases: 172 succeeded**, 17 suites, run sequentially after `pio test -e native` (which also reported 172/172, 17 suites, as part of Task 1's pre-commit verification). Neither leg required a re-run.
- `python3 -m pytest tests/ -q` (system `python3`, run after the firmware commit landed): **347 passed, 0 failed** in 30.63 s. This is higher than the before-figures' 323 baseline because plan 02's symbol-gate tests and plan 04's voltage-reformulation oracle tests have landed on this branch since the before-figures were measured; this plan added zero pytest cases of its own.
- `python3 scripts/check_no_heap_or_64bit_symbols.py`: exit 0. `PASS: leonardo(heap=0,64bit=0,anchors=2/2), uno(heap=0,64bit=0,anchors=2/2), uno328pb(heap=0,64bit=0,anchors=2/2)`.
- `avr-nm --print-size .pio/build/uno/firestarter_uno.elf | grep ' handle$'`: `00000259 b handle` = 601 B (matching `uno328pb`'s 601 B and `leonardo`'s 1113 B), each exactly 2 B below the before-figures' 603/603/1115 B -- the rejected alternative's measured cost.
- `python3 scripts/check_build_warnings.py --log uno=<clean uno build log>`: `PASS: uno: macro_redefinition=0 (== 0)`. No new warning attributable to `memory.cpp` or `firestarter.h`.
- **Two things NOT claimed, per the plan's Step 6:** (1) `check_size_baseline.py`'s per-target flash delta against `scripts/baseline/size_baseline.json` was not computed in this session (it needs `--avr-log`/`--native-log`/`--rebuild` inputs this task did not construct), but per the before-figures record any such delta would be measured against the already-+478/+476/+540-B-stale baseline, not against this phase's true before-position (`155-before-figures.md`'s §2), and is not this phase's saving figure. (2) The pre-existing red on the canonical `--policy merge05` invocation (a frozen native case count from an earlier phase, per RESEARCH.md Pitfall 7) is not attributed to this change; it is Phase 158's item.
- `check_dead05_phrasing.py` was run and correctly resolved all 19 in-scope corpus files including this plan's four edited firmware files, reporting **no forbidden-phrasing violation** in the negative half before exiting 2 on a required positive target (`.planning/v1.33/155-after-figures.md`) that does not exist yet -- that file is plan 06's deliverable, not this plan's, so the exit code here is expected and does not indicate a defect in this plan's work.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- DEAD-01, DEAD-02 and DEAD-06 are code-complete and measured, but deliberately left `Pending` in `REQUIREMENTS.md` per this plan's constraint 10 -- plan 06 (the landing plan) closes them against the phase gate.
- Plan 06 can now build `.planning/v1.33/155-after-figures.md`, satisfying `check_dead05_phrasing.py`'s one remaining required positive target and completing the phase's before/after record.
- `firestarter/tests/fixtures/clean_no_heap_or_64bit_symbols_postchange_uno/` and the new `test_real_postchange_listing_exits_zero` leg (plan 06's deliverables per the phase artifact table) can now be captured against a genuinely heap-free `uno` ELF.
- No blockers. `git -C firestarter status --porcelain` is empty; the meta-repo's pre-existing, operator-gated noise (`firestarter` and `firestarter_app` gitlinks, `.planning/config.json`, `package.json`/`package-lock.json`) is untouched and still present exactly as found.

---
*Phase: 155-dead-weight-removal-the-heap-allocator-and-the-64-bit-runtim*
*Completed: 2026-08-23*

## Self-Check: PASSED

- FOUND: `.planning/phases/155-dead-weight-removal-the-heap-allocator-and-the-64-bit-runtim/155-05-SUMMARY.md`
- FOUND: `firestarter/src/proms/memory.cpp`
- FOUND: `firestarter/include/firestarter.h`
- FOUND: commit `98e70af` in `firestarter` history
