---
phase: 201-a-partial-write-is-gated-on-its-own-region
plan: 02
subsystem: firmware-protocol
tags: [json-parser, wire-protocol, blank-check, native-tests, unity, platformio, cross-repo-constant]

# Dependency graph
requires:
  - phase: 201-01
    provides: the address-keyed shadow read-back model (val_shadow_reset/enable/seed) and the
      BLANK-02 chunking/erase-end contract freeze, both needed to express and observe D-16.1
provides:
  - "region-end" wire key, parsed into uint32_t handle->region_end (firestarter_handle_t),
    reset per command, read by nothing yet
  - JSON_KEY_REGION_END host constant pinned against the firmware PROGMEM key string
  - the D-16.1 regression test, run and observed RED against unmodified firmware, with its
    paired negative control observed GREEN
affects: [201-03, 201-04, 201-05]

actuals:
  tokens: 4136
  tasks: 2
  commits: 4
  plan_head_before: "649c9601 (meta); a7746d0c6a28aed6dc0af1e6482ff8172968e96a (firestarter_fw); b3a777e38a3ee0787f3f90587c1f7ab49b36f711 (firestarter_app)"

tech-stack:
  added: []
  patterns:
    - "Wire field landed inert-first, consumer-later: region_end is parsed and reset for a full
      plan before anything reads it, so the next plan's diff is a pure behavior change with no
      accompanying plumbing noise."
    - "A regression test authored, run, and captured RED in the same commit that adds it -- the
      commit message quotes the failing transcript verbatim rather than asserting it happened."

key-files:
  created: []
  modified:
    - firestarter_fw/include/firestarter.h
    - firestarter_fw/src/json_parser.c
    - firestarter_fw/test/native/avr/test_val_eprom/test_val_eprom.cpp
    - firestarter_app/firestarter/constants.py
    - firestarter_app/tests/test_eprom_operations.py

key-decisions:
  - "Did not call configure_eprom(&h) a second time after configure_memory(&h) in the two new
    D-16.1 tests, despite the plan's literal action text instructing both calls. configure_memory
    already dispatches to configure_eprom for protocol 0x07, and a second explicit call re-reads
    the eprom_internal_set_control_register wrapper configure_eprom just installed and assigns it
    to the module-global ep_set_control_register, making that wrapper call itself. Any path that
    touches handle->firestarter_set_control_register (eprom_check_vpp, on the very first init call)
    then recurses until the stack overflows -- measured as SIGSEGV, not asserted."
  - "clear_bus_recording() is called before every loop iteration inside the driving helper, not
    once before the loop starts. One BLANK_CHECK_CHUNK_SIZE (8192-byte) chunk scan performs 24576
    register writes, which saturates HOST_STUBS_MAX_RECORDING (4096) well inside a single call;
    once saturated, the address-keyed shadow model's backward address-recovery scan falls back to
    the last address it recovered before saturation and repeats that stale byte for the remainder
    of the call. The negative control's target (offset 1024 into chunk 2) was silently unreachable
    without a per-call clear, because chunk 1's own saturated recording was still active when
    chunk 2's scan began."
  - "The driving loop is a do-while, not the plan's literal 'while' framing: before the first call
    to firestarter_operation_init, the operation has not started, so is_operation_in_progress
    reads false and a while-loop would never invoke init at all -- both cases would spuriously
    read RESPONSE_CODE_OK, unchanged from the fixture's own default, rather than exercising the
    blank check."

requirements-completed: [BLANK-03]

coverage:
  - id: D1
    description: "region-end wire field landed on both sides of the seam (uint32_t region_end on
      the firmware handle, JSON_KEY_REGION_END on the host), parsed, reset per command, read by
      nothing yet."
    requirement: BLANK-03
    verification:
      - kind: unit
        ref: "firestarter_fw pio test -e native_nodevtools (235/235, unchanged count)"
        status: pass
      - kind: unit
        ref: "firestarter_app tests/test_eprom_operations.py#test_region_end_key_constant"
        status: pass
      - kind: other
        ref: "firestarter_fw pio run (uno, uno328pb, leonardo all SUCCESS -- AVR-layout _Static_assert proof)"
        status: pass
    human_judgment: false
  - id: D2
    description: "D-16.1 regression test authored, run, and SEEN failing against unmodified
      firmware (the whole-device blank check refuses a write whose own region is blank, because
      it has no notion of a region yet); its paired negative control observed green."
    requirement: BLANK-03
    verification:
      - kind: unit
        ref: "test/native/avr/test_val_eprom/test_val_eprom.cpp#test_write_init_accepts_blank_region_on_non_blank_part"
        status: fail
      - kind: unit
        ref: "test/native/avr/test_val_eprom/test_val_eprom.cpp#test_write_init_still_refuses_when_target_region_is_non_blank"
        status: pass
    human_judgment: true
    rationale: "The positive case's status is intentionally 'fail' -- that is the designed D-16.1
      outcome this plan exists to produce, and plan 201-03 greens it. A deterministic classifier
      that treats any non-pass status as needing human review is exactly correct here: a human (or
      the next plan) must confirm the RED is the deliberate one this plan documents, not a stray
      regression, before trusting the fix that follows."

duration: 65min
completed: 2026-09-20
status: complete
---

# Phase 201 Plan 02: Region-End Wire Field + D-16.1 RED Regression Test Summary

**Landed an inert `region-end` wire field on both sides of the firestarter_fw/firestarter_app seam, then authored and ran the D-16.1 native regression test — watched it fail against today's whole-device blank check with its paired negative control green, and committed the transcript.**

## Performance

- **Duration:** ~65 min
- **Tasks:** 2
- **Files modified:** 5

## Accomplishments
- `uint32_t region_end` added to `firestarter_handle_t` between `page_size` and `data_buffer`, parsed from the `"region-end"` wire key via the existing `FIELD` table machinery (clamp `0`, offset `_Static_assert`, row-count assert `11` → `12`), and reset to `0` per command in `json_parse`'s prologue — with a comment stating the fail-open direction a missing reset would create (D-04).
- `JSON_KEY_REGION_END = "region-end"` added to `firestarter_app/firestarter/constants.py`, paired in the same logical change as the firmware key, with a literal-pinning test (`test_region_end_key_constant`) in the compliant post-`088d2b7` shape.
- `test_write_init_accepts_blank_region_on_non_blank_part` (D-16.1) written, run, and **observed RED**: a write whose own target region `[8192, 12288)` is blank is refused today, because the whole-device blank check has no notion of "the write's own region" yet and hits a non-blank byte at address `0x10`, well outside the region. The transcript is captured verbatim below and in the Task Commits section.
- `test_write_init_still_refuses_when_target_region_is_non_blank`, the paired negative control, is **green**: a non-blank byte genuinely inside the target region still refuses the write, proving the fix plan 201-03 will apply *scopes* the check rather than deleting it.
- All three AVR environments (`uno`, `uno328pb`, `leonardo`) still build successfully with the new field in place. Both native environments' pre-existing case counts are unchanged (235/235 on `native_nodevtools`) except for the two new D-16.1 cases.
- Nothing reads `region_end` yet — `database.py`, `serial_comm.py` and `chip_test.py` are byte-unchanged, confirmed by an explicit diff against each task's own pre-edit base commit.

## Task Commits

Each task was committed atomically, across two submodules plus one meta-repo gitlink advance, all on `v1.40-program-parameter-fidelity`:

1. **Task 1 (firestarter_fw half): land `region-end` wire field, parsed and reset, unread** — `666195b` (feat)
2. **Task 1 (firestarter_app half): add `JSON_KEY_REGION_END` host constant** — `a36b9ec` (feat)
3. **Task 2: write the D-16.1 regression test, run it, and see it RED** — `af47bf4` (test)

**Meta-repository gitlink advance:** `7fcdbe5a` (feat) — `firestarter_fw` pointer moved `a7746d0c` → `af47bf46`, `firestarter_app` pointer moved `b3a777e3` → `a36b9eca`, both in `/workspaces` on `v1.40-program-parameter-fidelity`.

### D-16.1 RED transcript, verbatim

Command: `pio test -e native_nodevtools -f native/avr/test_val_eprom` (default, non-verbose invocation — this is the exact runner text form used by the plan's own verify legs and by CI's `pio test -e native_nodevtools` step):

```
test/native/avr/test_val_eprom/test_val_eprom.cpp:697: test_eprom_0x07_write_enables_vpp_regulator	[PASSED]
test/native/avr/test_val_eprom/test_val_eprom.cpp:698: test_eprom_0x08_write_enables_vpp_regulator	[PASSED]
test/native/avr/test_val_eprom/test_val_eprom.cpp:699: test_eprom_0x0B_write_enables_vpp_regulator	[PASSED]
test/native/avr/test_val_eprom/test_val_eprom.cpp:702: test_eprom_0x07_read_configure_only_does_not_enable_vpp	[PASSED]
test/native/avr/test_val_eprom/test_val_eprom.cpp:703: test_eprom_0x08_read_configure_only_does_not_enable_vpp	[PASSED]
test/native/avr/test_val_eprom/test_val_eprom.cpp:704: test_eprom_0x0B_read_configure_only_does_not_enable_vpp	[PASSED]
test/native/avr/test_val_eprom/test_val_eprom.cpp:709: test_writeperf_route_is_asserted_once_per_pass_not_once_per_byte	[PASSED]
test/native/avr/test_val_eprom/test_val_eprom.cpp:710: test_writeperf_route_assert_count_tracks_passes_not_pulses	[PASSED]
test/native/avr/test_val_eprom/test_val_eprom.cpp:714: test_shadow_seed_is_address_keyed_not_modulo_aliased	[PASSED]
test/native/avr/test_val_eprom/test_val_eprom.cpp:719: test_blank_check_resumes_across_chunks_and_restores_the_cursor	[PASSED]
test/native/avr/test_val_eprom/test_val_eprom.cpp:720: test_erase_end_blank_check_scans_from_zero	[PASSED]
test/native/avr/test_val_eprom/test_val_eprom.cpp:653: test_write_init_accepts_blank_region_on_non_blank_part: D-16.1: a non-blank byte OUTSIDE the write's own target region [8192, 12288) must not refuse the write. RED at this commit means the whole-device blank check does not yet scope to the region -- plan 201-03's fix is what greens this.	[FAILED]
test/native/avr/test_val_eprom/test_val_eprom.cpp:729: test_write_init_still_refuses_when_target_region_is_non_blank	[PASSED]
Program received signal SIGHUP (Hangup)
--- native_nodevtools:native/avr/test_val_eprom [ERRORED] Took 1.09 seconds ---

=================================== SUMMARY ===================================
Environment        Test                       Status    Duration
-----------------  -------------------------  --------  ------------
native_nodevtools  native/avr/test_val_eprom  ERRORED   00:00:01.093

============ 14 test cases: 1 failed, 12 succeeded in 00:00:01.093 ============
```

**Runner text form, exact and distinct between modes:**
- **PlatformIO's default (table-row) form**, used above: `<file>:<line>: <name>: <failure message>\t[FAILED]` for a failing case, `<file>:<line>: <name>\t[PASSED]` for a passing one — one literal TAB character before the bracketed status.
- **Unity's own `-v` form** (`pio test ... -v`), NOT the same string: `<file>:<line>:<name>:FAIL: <failure message>` for a failing case (colon-separated, no tab, no space after the second colon) — `test/native/avr/test_val_eprom/test_val_eprom.cpp:653:test_write_init_accepts_blank_region_on_non_blank_part:FAIL: D-16.1: a non-blank byte OUTSIDE the write's own target region [8192, 12288) must not refuse the write. RED at this commit means the whole-device blank check does not yet scope to the region -- plan 201-03's fix is what greens this.` A future grep against a failing case must pick the form matching its invocation mode; the two are not interchangeable strings.

The `SIGHUP`/`ERRORED` wrapper around the summary is PlatformIO's own harness behavior when a Unity suite reports failures with no `-v`/serial monitor attached; it is not itself a defect and is present identically whether 1 or 0 cases fail (confirmed against plan 201-01's own clean 235/235 run, which does not show it).

### `pio run` flash figures, all three environments (unchanged shape, field added)

```
uno:       Flash 21730/32768 B (66.3%), RAM 1398/2048 B (68.3%)
uno328pb:  Flash 21774/32768 B (66.4%), RAM 1404/2048 B (68.6%)
leonardo:  Flash 23850/32768 B (72.8%), RAM 1839/2560 B (71.8%)
```

## Files Created/Modified
- `firestarter_fw/include/firestarter.h` — adds `uint32_t region_end;` to `firestarter_handle_t`, positioned strictly between `page_size` and `data_buffer` so its `offsetof` stays under 256 on leonardo (`DATA_BUFFER_SIZE` = 1024 there).
- `firestarter_fw/src/json_parser.c` — adds the `key_region_end` PROGMEM string, the `FIELD(key_region_end, region_end, 0)` row, an offset `_Static_assert` for `region_end`, edits the row-count assert `11` → `12`, and adds `handle->region_end = 0;` to `json_parse`'s per-command reset prologue.
- `firestarter_fw/test/native/avr/test_val_eprom/test_val_eprom.cpp` — adds `unity_capped_iterations` (the bounded, do-while, per-iteration-clearing driving helper), `test_write_init_accepts_blank_region_on_non_blank_part` (D-16.1, RED at this commit), and `test_write_init_still_refuses_when_target_region_is_non_blank` (paired negative control, GREEN), both registered with `RUN_TEST`.
- `firestarter_app/firestarter/constants.py` — adds `JSON_KEY_REGION_END = "region-end"` with the `Firmware sync: json_parser.c (key_region_end)` comment convention and an explicit statement of D-04's absent-semantics inversion.
- `firestarter_app/tests/test_eprom_operations.py` — adds `test_region_end_key_constant`, in the exact literal-pinning shape of `test_read_timing_settling_key_constant`.

## Decisions Made
See `key-decisions` in frontmatter for the three substantive deviations (the self-recursive `configure_eprom` double-call, the per-iteration `clear_bus_recording()` requirement, and the do-while loop shape). All three are measured facts about the real, compiled behavior of the fixtures against production code; none is an architectural change, and none touches `src/` or `include/` inside the commit that is supposed to carry only the failing test (verified by an explicit empty-diff check against that commit's own pre-edit base).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Removed the plan's instructed second `configure_eprom(&h)` call — it caused a stack-overflow SIGSEGV**
- **Found during:** Task 2, first run of `test_write_init_accepts_blank_region_on_non_blank_part`
- **Issue:** The plan's action text says to call `configure_memory(&h)` **and** `configure_eprom(&h)`, matching the shape plan 201-01's `make_region_handle`-based tests use. `configure_memory` already dispatches to `configure_eprom` internally for protocol `0x07` (`memory.cpp`: `if (handle->protocol == PROTO_EPROM_28PIN || ...) { configure_eprom(handle); return; }`). `configure_eprom`'s own body does `ep_set_control_register = handle->firestarter_set_control_register; handle->firestarter_set_control_register = eprom_internal_set_control_register;` — a second, explicit call reads back the WRAPPER the first call just installed and assigns it to the module-global `ep_set_control_register`, making `eprom_internal_set_control_register` call itself. Every code path this test exercises (`eprom_write_init` → `eprom_generic_init` → `eprom_check_vpp`) calls `handle->firestarter_set_control_register` on the very first `firestarter_operation_init` call, so the corrupted pointer recurses until the stack overflows. Measured directly: the test binary run standalone printed debug markers through `val_shadow_seed(0x10, 0x00)` and then crashed with `SIGSEGV` on the very first line inside the loop body, before any Unity output for that case.
- **Fix:** Removed the explicit `configure_eprom(&h)` call from both new test functions; `configure_memory(&h)` alone is sufficient and correct, since it dispatches to `configure_eprom` itself. The two pre-existing plan-201-01 tests that use the same double-call shape (`test_blank_check_resumes_across_chunks_and_restores_the_cursor`, `test_erase_end_blank_check_scans_from_zero`) never trip this, because they drive `firestarter_operation_main`/`firestarter_operation_end` (`mem_util_blank_check`), which never calls the control-register setter — left untouched, out of scope for this plan.
- **Files modified:** `test_val_eprom.cpp`
- **Verification:** Both new cases run to completion with no crash; the positive case reports `FAIL` for the expected reason, the negative control reports `PASS`.
- **Committed in:** `af47bf4`

**2. [Rule 1 - Bug] `clear_bus_recording()` must run before every loop iteration, not once before the loop — the negative control silently could not see its own seeded byte otherwise**
- **Found during:** Task 2, second run (after fixing deviation 1) — the negative control failed with `Expected 0 Was 1`, meaning it never detected the non-blank byte it seeded
- **Issue:** One `BLANK_CHECK_CHUNK_SIZE` (8192-byte) chunk scan performs `8192 * 3 = 24576` register writes (address set + read, per `test_erase_end_blank_check_scans_from_zero`'s own pre-existing comment), which blows past `HOST_STUBS_MAX_RECORDING` (4096) well inside a single call. The address-keyed shadow model's `rurp_read_data_buffer()` recovers the current address by scanning the recorder **backward**; once the recorder saturates, it falls back to `s_val_last_address` — the last address it recovered **before** saturation — and repeats that one stale byte for the remainder of the call, rather than tracking the real, advancing address. The negative control's target (`0x2400` = 9216, offset 1024 into the SECOND chunk `[8192, 16384)`) was unreachable because chunk 1's own scan (which completes fully, finding nothing, since its seeded counterpart lives in chunk 2) already saturates the recorder well before chunk 1 ends, and that saturated state was still active when chunk 2's scan began — chunk 2 therefore never correctly tracked its own addresses at all.
- **Fix:** Added `clear_bus_recording()` immediately before each call to `h->firestarter_operation_init(h)` inside the shared `unity_capped_iterations` helper. Each chunk's own scan now starts address recovery fresh, and since both D-16.1 targets sit at a relative offset (16, or 1024) well inside the ~1365-entry window before a fresh recording saturates, and both cases return with an error (or complete) well before finishing a full 8192-byte chunk, saturation never actually recurs at the point either assertion is checked.
- **Files modified:** `test_val_eprom.cpp`
- **Verification:** `test_write_init_still_refuses_when_target_region_is_non_blank` now reports `PASS`; both cases' `TEST_ASSERT_FALSE_MESSAGE(val_recording_saturated(), ...)` assertions hold.
- **Committed in:** `af47bf4`

**3. [Rule 1 - Bug] Driving loop must be `do-while`, not `while` — the plan's literal framing would never call `firestarter_operation_init` at all**
- **Found during:** Task 2, first run (before either fix above) — both new cases silently read `RESPONSE_CODE_OK` unchanged from the fixture default, meaning nothing in the loop body had executed
- **Issue:** The plan's action text says: "Loop `h.firestarter_operation_init(&h)` while `is_operation_in_progress(&h)` is true and `h.response_code != RESPONSE_CODE_ERROR`". Read as a `while`-loop, the condition is checked BEFORE the first call — and before any call, the operation has not started, so `is_operation_in_progress` reads `false` and the loop body never executes at all.
- **Fix:** Implemented as a `do-while`: call first, then re-check the same two-clause condition to decide whether to loop again. This matches the plan's own stated intent ("A single call ... proves nothing ... drive it to completion or to an error") which requires at least one call to happen.
- **Files modified:** `test_val_eprom.cpp`
- **Verification:** Both cases now genuinely exercise `eprom_write_init` and its embedded blank check; confirmed by the RED/GREEN split matching the plan's designed outcome exactly.
- **Committed in:** `af47bf4`

---

**Total deviations:** 3 (all Rule 1 — bug corrections to the plan's own prose, made necessary by measured facts about the compiled fixture and production code). All three were required to make the plan's own stated tests actually exercise `eprom_write_init`'s blank check rather than silently no-op or crash. None touches `src/` or `include/` inside the Task 2 commit (confirmed by an explicit diff check against that commit's pre-edit base); none is an architectural change.
**Impact on plan:** Necessary corrections only. The RED/GREEN outcome the plan designed (one deliberately failing case, one green negative control, zero unrelated regressions) is exactly what was observed once all three were applied.

## Issues Encountered
None beyond the deviations documented above.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Plan 201-03 has its target: teach `mem_util_blank_check` (or the write-init call site) to scope to `[handle->address, handle->region_end)` when `region_end` is non-zero, and green `test_write_init_accepts_blank_region_on_non_blank_part` without breaking `test_write_init_still_refuses_when_target_region_is_non_blank` or any of the pre-existing 235 (now 237, including this plan's negative control and the RED case once it flips) native cases.
- The RED case's exact commit is `af47bf4` in `firestarter_fw`; plan 201-03's fix commit is expected to flip it to `PASSED` with no other change to this suite's pass/fail split.
- `database.py`, `serial_comm.py` and `chip_test.py` remain byte-unchanged from this plan, confirmed against each task's own pre-edit base commit — no key reached `convert_to_programmer`, and `test_wire_dict_equivalence.py`'s nine-key union pin is untouched.
- No blockers. All three repositories remain on `v1.40-program-parameter-fidelity`.

## Self-Check: PASSED

- FOUND: `firestarter_fw/include/firestarter.h`
- FOUND: `firestarter_fw/src/json_parser.c`
- FOUND: `firestarter_fw/test/native/avr/test_val_eprom/test_val_eprom.cpp`
- FOUND: `firestarter_app/firestarter/constants.py`
- FOUND: `firestarter_app/tests/test_eprom_operations.py`
- FOUND: commit `666195b` (`git -C firestarter_fw log --oneline --all`)
- FOUND: commit `af47bf4` (`git -C firestarter_fw log --oneline --all`)
- FOUND: commit `a36b9ec` (`git -C firestarter_app log --oneline --all`)
- FOUND: commit `7fcdbe5a` (`git log --oneline --all`, meta repo gitlink advance)
- Re-ran acceptance criteria and plan-level `<verification>`: `pio run` 3/3 SUCCESS (fw); `pio test -e native_nodevtools -f native/avr/test_val_eprom` 1 failed (the intended D-16.1 positive case), 12 succeeded, negative control PASSED; `FIRESTARTER_META_ROOT=/tmp/no-meta pytest tests/` 269 passed / 32 skipped / 0 failed (fw); `pytest tests/test_eprom_operations.py tests/test_wire_dict_equivalence.py` 55 passed (app); `ruff check` / `ruff format --check` clean (app); row-count assert reads `== 12` exactly once and `== 11` zero times; `region_end` declared strictly between `page_size` and `data_buffer`; `handle->region_end = 0;` present in `json_parse`'s reset prologue; diff from each task's pre-edit base over `database.py`/`serial_comm.py`/`chip_test.py` and over `src/`/`include/` (Task 2's own commit) both empty; `git -C firestarter_fw rev-parse --abbrev-ref HEAD`, `git -C firestarter_app rev-parse --abbrev-ref HEAD` and `git rev-parse --abbrev-ref HEAD` (meta) all `== v1.40-program-parameter-fidelity`.

---
*Phase: 201-a-partial-write-is-gated-on-its-own-region*
*Completed: 2026-09-20*
