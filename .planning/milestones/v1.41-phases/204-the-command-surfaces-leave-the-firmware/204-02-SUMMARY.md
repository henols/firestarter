---
phase: 204-the-command-surfaces-leave-the-firmware
plan: 02

subsystem: testing
tags: [source-contract-gate, native-unity-tests, message-id-assertion, platformio, arduinofake, verify-survival]

requires:
  - phase: 204-01
    provides: "ordinal 6 (CMD_VERIFY) retired from both ladders; FWCMD-05 and ROADMAP criterion 3 amended (D-03) to name the four real failure ids this plan's suite pins"
provides:
  - "the eighth house source-contract gate (`tests/test_verify_survival_source_contract.py`), proving the shared final-pass verify call stays contained inside the VERIFY_PER_PULSE_PLUS_FINAL arm"
  - "a new native Unity suite (`test/native/avr/test_verify_error_ids/`) asserting the actual emitted message id — not a generic error response code — for all four failure ids the amended FWCMD-05 names, each in both directions"
  - "both instruments committed and green BEFORE plan 03 sweeps ordinal 4, so the sweep runs with its safety net already proven to fail on the right violations"
affects: [204-03-blank-check-retirement]

actuals:
  tokens: 11300
  tasks: 3
  commits: 3

tech-stack:
  added: []
  patterns:
    - "Settable, address-independent rurp_read_data_buffer() stub (HOST_STUBS_CUSTOM_READ_DATA_BUFFER opt-in) — sufficient whenever a suite only needs to control WHICH id a site raises, never WHICH address mismatched; simpler than the recording-and-backward-scan model test_val_eprom's suite needs."
    - "Brace-matched containment (never line proximity) for a source-contract gate's central claim, with the violation planted directly into the real file, RED captured, then restored — repeats the house's established shape from test_write_path_source_contract_v131.py and test_blank_check_region_source_contract.py."

key-files:
  created:
    - firestarter_fw/tests/test_verify_survival_source_contract.py
    - firestarter_fw/test/native/avr/test_verify_error_ids/test_verify_error_ids.cpp
    - firestarter_fw/test/native/avr/test_verify_error_ids/host_stubs.cpp
  modified:
    - firestarter_fw/platformio.ini
    - .planning/REQUIREMENTS.md

key-decisions:
  - "The 28C page read-back and per-pulse budget-exit id groups reuse the SAME address-independent read-back stub as the memory-verify and DQ7-poll groups (host_stubs.cpp's single settable global byte) — no per-address tracking was needed anywhere in this suite, since every case asks only which id a site raises, never which address mismatched."
  - "The energy-cap budget test uses protocol 0x0B (max_pulses=255, energy_cap_us=50000), not one of the two plus-final protocols (0x07/0x08, energy_cap_us=0/uncapped) — CLAUDE.md's own measured fact states MSG_ERR_ENERGY_CAP is structurally unreachable on 0x07/0x08. A pulse_delay of 6000us was chosen so the energy cap exhausts at 9 of 255 pulses, far short of the pulse ceiling."
  - "flash_util_verify_operation is driven directly (not through flash_nor_unlock's full write path) after configure_memory(&h) wires the generic get_data/set_data/set_control_register pointers — the function needs no address remap at all (no firestarter_set_address call anywhere in its body), so the identity bus_config used elsewhere in this suite is not even required for that id group."

requirements-completed: [FWCMD-04, FWCMD-05]

coverage:
  - id: D1
    description: "The eighth house source-contract gate proves the shared final-pass verify call stays brace-matched inside the plus-final verify arm, and its RED has been observed for both violation shapes (deleted call, call moved outside the arm)"
    requirement: FWCMD-04
    verification:
      - kind: unit
        ref: "firestarter_fw/tests/test_verify_survival_source_contract.py (pytest tests/test_verify_survival_source_contract.py, 6/6 PASSED)"
        status: pass
    human_judgment: false
  - id: D2
    description: "A native Unity suite asserts the actual emitted message id — not a generic error response code — for all four failure ids the amended FWCMD-05 names, each in both directions, each with a non-zero frame-count precondition; the DQ7 data-poll wait is pinned to the timeout id and explicitly asserted to never raise the verify id"
    requirement: FWCMD-05
    verification:
      - kind: unit
        ref: "firestarter_fw/test/native/avr/test_verify_error_ids/test_verify_error_ids.cpp (pio test -e native -f \"*test_verify_error_ids*\", 8/8 PASSED)"
        status: pass
      - kind: unit
        ref: "pio test -e native_nodevtools -f \"*test_verify_error_ids*\" — same 8/8 PASSED, proving the shared platformio.ini filter reached the always-on CI leg"
        status: pass
    human_judgment: false
  - id: D3
    description: "Every RED leg this plan requires was actually run and observed failing for the intended reason — two planted violations against the source-contract gate, three transposed-id runs against the native suite — with each transcript captured verbatim and the working tree restored and reverified clean before committing"
    requirement: null
    verification:
      - kind: other
        ref: "verbatim transcripts recorded in this SUMMARY's RED Evidence section below; git status --porcelain / git diff confirmed empty after each restore"
        status: pass
    human_judgment: false

duration: "~30min (from wave 1's completion at 2026-09-22T09:06:48Z to this plan's final task commit at 2026-09-22T09:31:54Z; excludes SUMMARY/state-update overhead)"
completed: 2026-09-22
status: complete
---

# Phase 204 Plan 02: Both verify-survival instruments built, RED seen five times, all green

**Built the eighth house source-contract gate and a new native Unity suite that together make Phase 204's central claim measurable: removing the command surface did not remove the verification. Both instruments were proven able to fail — five separate planted-violation runs, each RED for the intended reason, each restored clean — before being committed.**

## Performance

- **Duration:** ~30 min (commit span; see frontmatter `duration` for the precise window and its caveat)
- **Started:** 2026-09-22T09:15:30Z (Task 1's first commit)
- **Completed:** 2026-09-22T09:31:54Z (Task 3's final commit)
- **Tasks:** 3 automated tasks, no checkpoints
- **Files modified:** 4 in `firestarter_fw` (3 created, 1 modified) + `.planning/REQUIREMENTS.md`

## Accomplishments

- Built `firestarter_fw/tests/test_verify_survival_source_contract.py`, the eighth member of the house source-contract family: a containment leg (brace-matched, never line proximity) proving the shared final-pass verify call sits inside the plus-final verify arm; a positive leg pinning the parameter table's `0x07`/`0x08` rows keyed positionally against the table's own lookup-key array; a definition leg for the shared verify function; and the family's three standard belt-and-braces legs (non-vacuity, cannot-be-silently-skipped, own-needles-absent).
- Planted and observed RED for both violation shapes the gate must catch: the call deleted from the arm, and the call moved outside the arm's braces while staying in the enclosing function. Both transcripts recorded below; the real source file was restored and reverified clean (`git diff` empty) before either commit.
- Built `firestarter_fw/test/native/avr/test_verify_error_ids/`, a new native Unity suite (8 test cases) asserting the actual emitted message id for every failure site the amended FWCMD-05 names: the shared final-pass verify → `MSG_ERR_VERIFY`; the DQ7 data-poll wait (`flash_util_verify_operation`) → `MSG_ERR_OP_TIMEOUT`, explicitly asserted to never raise `MSG_ERR_VERIFY`; the 28C page read-back → `MSG_ERR_VERIFY`, driven through its only caller since the function is `static`; the per-pulse loop's two budget exits → `MSG_ERR_MAX_PULSES` and `MSG_ERR_ENERGY_CAP`, each asserted absent the other.
- Registered the suite with exactly one `test_filter` line and one include line in `[native_base]`; verified it runs in both `native` (PR-only) and `native_nodevtools` (always-on CI leg) off the shared filter.
- Planted and observed RED for three transposed-id pairs — one per task's own requirement — each restored and reverified clean before the corresponding commit.
- Ran the full four-leg firmware gate after both instruments landed: `pio test -e native` 245/245 (237 baseline + 8 new), `pio test -e native_nodevtools` 245/245, `pytest tests/` 299 passed / 17 failed (all 17 confined to the known pre-existing `tests/test_flash_path_record_sync.py` whole-repo-porcelain red), `pio run` all three firmware environments SUCCESS with `leonardo` unchanged at 24082 B — a test-only plan touches no production source and costs no flash.

## Task Commits

Each task was committed atomically, in `firestarter_fw` on `v1.41-verification-to-host`:

1. **Task 1: The eighth source-contract gate, with its RED seen** — `ad74763` (test)
2. **Task 2: The native id-asserting suite, registered, with the two independent ids pinned** — `2a23a5c` (test)
3. **Task 3: The two harder ids — the page read-back and the per-pulse budget exits** — `65e8d20` (test)

**Meta gitlink advance:** `afc0fcf2` (chore) — advances the `firestarter_fw` submodule pointer to `65e8d20`.

**Plan metadata:** this SUMMARY's own commit, made after this file.

_Total: 3 commits in `firestarter_fw` (measured: `git rev-list --count 268d844b..65e8d20` = 3), 1 gitlink-advance commit in the meta repo. `plan_head_before: 268d844b5c664e472527158d00a9bd342a39b0dc`._

## Files Created/Modified

- `firestarter_fw/tests/test_verify_survival_source_contract.py` — the eighth house source-contract gate; six test functions; FWCMD-04.
- `firestarter_fw/test/native/avr/test_verify_error_ids/test_verify_error_ids.cpp` — eight Unity test cases across four id groups; the amended FWCMD-05.
- `firestarter_fw/test/native/avr/test_verify_error_ids/host_stubs.cpp` — the settable, address-independent read-back stub every id group in this suite drives.
- `firestarter_fw/platformio.ini` — one `test_filter` line and one include line added to `[native_base]`; no per-environment filter.
- `.planning/REQUIREMENTS.md` — FWCMD-04 and FWCMD-05 checkboxes and traceability rows marked Complete.

## RED Evidence

**Task 1, violation 1 — the shared verify call deleted from the plus-final arm.** Deleted `memory_verify_execute(handle);` from the real `src/proms/eprom.cpp`, leaving an empty arm body. Ran `pytest tests/test_verify_survival_source_contract.py::test_the_final_verify_pass_is_still_called_for_plus_final`:

```
AssertionError: the plus-final verify arm no longer calls the shared final-pass verify function -- FWCMD-04's whole point is that removing the command surface did NOT remove this call.
  Got arm body:
  {
      }
assert None
 +  where None = <built-in method search of re.Pattern object at 0x5570fa916fd0>('{\n    }')
 +    where <built-in method search of re.Pattern object at 0x5570fa916fd0> = re.compile('\\bmemory_verify_execute\\s*\\(\\s*handle\\s*\\)\\s*;').search
```

Restored via `cp` from a pre-edit copy; `git diff -- src/proms/eprom.cpp` confirmed 0 lines before the second plant.

**Task 1, violation 2 — the call moved outside the arm's braces, still in the enclosing function.** Moved `memory_verify_execute(handle);` to immediately after the arm's closing brace (still inside `eprom_internal_write_execute_body`). Same test, same failure:

```
AssertionError: the plus-final verify arm no longer calls the shared final-pass verify function -- FWCMD-04's whole point is that removing the command surface did NOT remove this call.
  Got arm body:
  {
      }
assert None
```

Proves containment (never mere file presence) is what the leg actually checks — the call is textually still in the file, just outside the brace-matched span the leg searches. Restored; `git diff` confirmed empty; `git status --porcelain -- src/proms/eprom.cpp src/proms/eprom_params.cpp src/proms/memory.cpp` confirmed empty before committing Task 1.

**Task 2 — transposed id pair, the DQ7 data-poll wait.** Swapped `MSG_ERR_OP_TIMEOUT`/`MSG_ERR_VERIFY` in `test_flash_util_data_poll_timeout_raises_timeout_id_not_verify_id`'s both-directions assertion. Ran `pio test -e native -f "*test_verify_error_ids*"`:

```
test/native/avr/test_verify_error_ids/test_verify_error_ids.cpp:250:test_flash_util_data_poll_timeout_raises_timeout_id_not_verify_id:FAIL: a DQ7 bit that never matches must raise MSG_ERR_OP_TIMEOUT
8 Tests 1 Failures 0 Ignored
FAIL
```

Restored; `git status --porcelain` confirmed empty before committing Task 2.

**Task 3 — transposed id pair, the 28C page read-back.** Swapped `MSG_ERR_VERIFY`/`MSG_ERR_EEPROM_TIMEOUT` in `test_eeprom28c_page_readback_mismatch_raises_verify_id_not_eeprom_timeout`'s both-directions assertion:

```
test/native/avr/test_verify_error_ids/test_verify_error_ids.cpp:302:test_eeprom28c_page_readback_mismatch_raises_verify_id_not_eeprom_timeout:FAIL: a mismatching page read-back must raise MSG_ERR_VERIFY
8 Tests 1 Failures 0 Ignored
FAIL
```

Restored; verified clean.

**Task 3 — transposed id pair, the per-pulse budget exit.** Swapped `MSG_ERR_MAX_PULSES`/`MSG_ERR_ENERGY_CAP` in `test_per_pulse_loop_exhausts_pulse_budget_raises_max_pulses_not_energy_cap`'s both-directions assertion:

```
test/native/avr/test_verify_error_ids/test_verify_error_ids.cpp:361:test_per_pulse_loop_exhausts_pulse_budget_raises_max_pulses_not_energy_cap:FAIL: a byte that never converges, under an uncapped energy budget, must raise MSG_ERR_MAX_PULSES
8 Tests 1 Failures 0 Ignored
FAIL
```

Restored; `git status --porcelain` and `git diff --stat` both confirmed empty before committing Task 3. All five planted violations across this plan were observed failing for the intended reason and none was left in the working tree.

## Decisions Made

See frontmatter `key-decisions` for the three implementation decisions (address-independent readback stub reused across all four id groups; the energy-cap test's protocol choice, forced by CLAUDE.md's own measured "0x0B only" fact rather than the task text's literal "plus-final protocol" phrasing; `flash_util_verify_operation` driven directly rather than through a full protocol write path).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] `setUp` was missing a `micros()` stub**
- **Found during:** Task 3, first run of the 28C id group
- **Issue:** `eeprom28c_write_execute` calls `micros()` twice per byte to measure page-load cadence; the suite's `setUp` stubbed `delay`, `delayMicroseconds` and `millis` but not `micros`, so ArduinoFake threw `UnexpectedMethodCallException` and aborted the whole binary (SIGABRT) partway through the 5th test case.
- **Fix:** Added `When(Method(ArduinoFake(), micros)).AlwaysReturn(0);` to `setUp`. A fixed 0 is sufficient — this suite asserts only on emitted message ids, never on the reported cadence value.
- **Files modified:** `firestarter_fw/test/native/avr/test_verify_error_ids/test_verify_error_ids.cpp`
- **Verification:** re-ran `pio test -e native -f "*test_verify_error_ids*"`; all 8 cases passed.
- **Committed in:** `65e8d20` (part of Task 3's commit — the fix landed before Task 3 was ever committed, so no separate commit exists for it)

**2. [Rule 2 - Missing critical] Task 3's acceptance criterion for both-directions assertion counts needed one more positive assertion**
- **Found during:** Task 3, running the plan's own shape-conformance check (`t.count('TEST_ASSERT_TRUE') >= 6`)
- **Issue:** The suite had exactly 5 `TEST_ASSERT_TRUE_MESSAGE` calls (one per mismatch/timeout case), one short of the plan's required floor of 6, because the two "match" (success-path) tests for `memory_verify_execute` and `flash_util_verify_operation` correctly assert only absence (nothing is emitted on success) — there was no natural sixth positive assertion.
- **Fix:** Added a genuine non-vacuity positive assertion to `test_eeprom28c_page_readback_match_raises_no_verify_id`: `eeprom28c_write_execute` (unlike the other two success paths) unconditionally emits its `MSG_INFO_PAGE_LOAD_WORST_US` cadence-report frame even on full success, so asserting `frame_count >= 1` there is a real, non-decorative check that the drive actually ran.
- **Files modified:** `firestarter_fw/test/native/avr/test_verify_error_ids/test_verify_error_ids.cpp`
- **Verification:** re-ran the shape-conformance script; `TEST_ASSERT_TRUE` count is 6, `TEST_ASSERT_FALSE` count is 8.
- **Committed in:** `65e8d20`

---

**Total deviations:** 2 auto-fixed (1 blocking test-infrastructure gap, 1 missing-critical non-vacuity strengthening). **Impact on plan:** Both were necessary to complete the task as designed and both stayed inside the suite's own test file — neither touched production source, neither is scope creep.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Both FWCMD-04 and FWCMD-05 instruments are committed and green. Plan 03 (ordinal 4 / `CMD_BLANK_CHECK` retirement) can now proceed with its safety net already in place and already proven to fail on the exact violations it exists to catch — the whole point of building these before the sweep.
- The new native baseline for plan 03 to compare against: `pio test -e native` and `-e native_nodevtools` both 245/245 (20 suites), up from the wave 1 baseline of 237/237 (19 suites).
- `pio run -e leonardo`: 24082 B, unchanged from wave 1 — this plan touched no production source.
- All three repositories remain on `v1.41-verification-to-host`; no branch touched `beta` at any point; nothing was pushed.

---
*Phase: 204-the-command-surfaces-leave-the-firmware*
*Completed: 2026-09-22*

## Self-Check: PASSED

All created files verified present on disk; all four commits (`ad74763`, `2a23a5c`, `65e8d20` in `firestarter_fw`, `afc0fcf2` in the meta repo) verified present in `git log --oneline --all`.
