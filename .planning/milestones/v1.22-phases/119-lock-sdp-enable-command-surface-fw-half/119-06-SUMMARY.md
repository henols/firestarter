---
phase: 119-lock-sdp-enable-command-surface-fw-half
plan: 06
subsystem: firmware-sdp-lock
tags: [firmware, firestarter_app, sdp, at28c, eeprom28c, native-tests, unity, source-scan-gate]

# Dependency graph
requires:
  - phase: 119-lock-sdp-enable-command-surface-fw-half
    plan: "04"
    provides: "EEPROM_SDP_ENABLE[3] (external linkage), eeprom28c_emit_sdp_sequence_timed(), eeprom28c_sdp_lock_execute()/eeprom28c_sdp_unlock_execute()"
  - phase: 119-lock-sdp-enable-command-surface-fw-half
    plan: "05"
    provides: "Four SDP_FIXED_LOCK_* goldens, drive_lock_op()/make_lock_handle(), the scripted micros() tick queue, cases 13-19"
provides:
  - "test_lock05_three_way_enable_table_identity / test_lock05_enable_table_objects_distinct (test_sdp_harness.cpp) -- the three-way byte-identity and pairwise-distinctness guard over the production EEPROM_SDP_ENABLE / FLASH_ENABLE_WRITE_PROTECTION / FLASH_ENABLE_WRITE objects"
  - "Cases 20-23 (test_eeprom28c_sdp.cpp) -- D-12's report-shape proof, D-14's budget-WARN fires/does-not-fire pair, D-13's standalone-unlock-equals-auto-unlock stream proof"
  - "test_eeprom_sdp_enable_matches_flash_enable_write_and_write_protection (test_sdp_table_parity.py) -- a second, independent source-text oracle for the same three-way identity"
  - "LOCK-05 Complete in REQUIREMENTS.md"
affects: [119-07, 119-10]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Two independent oracles for the same safety claim (link-time object comparison in firmware + source-text comparison in host pytest), each named by its distinct failure mode, rather than one oracle asserted twice"
    - "Anti-hollow paired assertions for a runtime budget check: a case that proves the check FIRES plus a case that proves it does NOT fire at a normal value, with the negative case also asserting the INFO ids are present so it cannot pass vacuously"
    - "Overriding firestarter_get_data with the address-keyed no-strobe mock even when driving `main` directly (not via drive_write_init), whenever the driven op performs its own get_data reads (completion poll) and the comparison target used the same override"

key-files:
  created: []
  modified:
    - firestarter/test/native/avr/test_sdp_harness/test_sdp_harness.cpp
    - firestarter/test/native/avr/test_eeprom28c_sdp/test_eeprom28c_sdp.cpp
    - firestarter_app/tests/test_sdp_table_parity.py

key-decisions:
  - "Two separately-messaged identity legs (ENABLE vs WRITE_PROTECTION, ENABLE vs WRITE) rather than one transitive assertion, so a failure names which pair diverged -- mirrors the plan's explicit instruction and the pattern test_fix05_terminal_byte_and_table_identity_guards already uses"
  - "Distinctness case additionally asserts EEPROM_SDP_ENABLE is a distinct object from EEPROM_SDP_DISABLE with differing length (3 vs 6) -- cheap completeness against the one-nibble hazard class, complementing Plan 119-05's stream-level lock-vs-unlock divergence (cases 18/19)"
  - "Case 23's standalone-unlock drive explicitly overrides firestarter_get_data with mock_get_data_keyed even though it calls h.firestarter_operation_main directly (not drive_write_init) -- without this override the completion poll's reads would hit the real memory_get_data and inject extra recorded strobes the auto-unlock comparison target (which DOES override get_data via drive_write_init) never contributes, which would have broken the byte-identity claim for a reason unrelated to D-13"
  - "Case 21/22 use synthetic native-host tick values (301 us over budget, 50 us in budget) rather than F-118-01's measured real-hardware figures (572/600, ~286/300) -- native host timing via the scripted micros() queue is a controlled input, not a hardware measurement, so the real numbers are cited in the case comments for context (why the check is genuinely load-bearing) but the scripted values are chosen to unambiguously straddle the 300 us lock budget"
  - "Criterion-5 deviation (recorded per plan instruction): ROADMAP criterion 5's 'header comment' on flash_utils.h was NOT added -- flash_utils.h stays FIX-04 byte-frozen (git diff --quiet confirmed). The rationale instead lives in two places: eeprom_28c.cpp's EEPROM_SDP_ENABLE comment (Plan 119-04) and the pre-existing test_sdp_harness.cpp:291-296 comment (Plan 117-04). This is the same deviation class as Phase 119's D-05 (LOCK-04 mechanism correction) and D-15 (headroom correction) -- mechanism-corrected, intent-satisfied, never failed"

requirements-completed: [LOCK-05]

coverage:
  - id: D1
    description: "Three-way byte-identity guard: EEPROM_SDP_ENABLE proven byte-identical to both FLASH_ENABLE_WRITE_PROTECTION and FLASH_ENABLE_WRITE (two separately-messaged legs), plus all three entries' address/byte pairs pinned including the terminal {0x5555, 0xA0}"
    requirement: LOCK-05
    verification:
      - kind: unit
        ref: "test_lock05_three_way_enable_table_identity -- pio test -e native and -e native_nodevtools -f \"*test_sdp_harness*\", 17/17 (was 15/15)"
        status: pass
    human_judgment: false
  - id: D2
    description: "Three-way distinctness guard: three pairwise (const void*) inequalities among the three production tables (alias-refactor hazard), plus distinctness/length-difference from EEPROM_SDP_DISABLE"
    requirement: LOCK-05
    verification:
      - kind: unit
        ref: "test_lock05_enable_table_objects_distinct -- same 17/17 run as D1"
        status: pass
    human_judgment: false
  - id: D3
    description: "D-12's report shape: MSG_INFO_SDP_LOCK then MSG_INFO_SDP_LOCK_DONE_US, ordered, with FLAG_VERBOSE unset; response_code stays RESPONSE_CODE_OK; unlock's ids and MSG_WARN_SDP_UNLOCK_SKIPPED absent from the lock path"
    requirement: LOCK-05
    verification:
      - kind: unit
        ref: "test_case20_lock_report_shape_and_response_code -- pio test -e native and -e native_nodevtools -f \"*test_eeprom28c_sdp*\", 23/23 (was 19/19)"
        status: pass
    human_judgment: false
  - id: D4
    description: "D-14's t_BLC budget WARN proven to fire over budget AND to not fire at a normal elapsed time (anti-hollow pair), response_code untouched on both paths"
    requirement: LOCK-05
    verification:
      - kind: unit
        ref: "test_case21_lock_tblc_budget_warn_fires / test_case22_lock_tblc_budget_warn_does_not_fire_at_normal_elapsed -- same 23/23 run as D3"
        status: pass
    human_judgment: false
  - id: D5
    description: "D-13's claim made assertable: standalone CMD_SDP_UNLOCK's stream proven byte-identical (exact divergence -1) to the auto-unlock's stream from eeprom28c_write_init, plus reused-ids membership"
    requirement: LOCK-05
    verification:
      - kind: unit
        ref: "test_case23_standalone_unlock_matches_auto_unlock_stream -- same 23/23 run as D3"
        status: pass
    human_judgment: false
  - id: D6
    description: "Second, independent source-text oracle for D-10's three-way identity: test_eeprom_sdp_enable_matches_flash_enable_write_and_write_protection parses EEPROM_SDP_ENABLE (eeprom_28c.cpp) and both flash_utils.h tables, asserting all three pair lists equal plus length-3 and terminal-pair checks"
    requirement: LOCK-05
    verification:
      - kind: unit
        ref: "python3 -m pytest tests/test_sdp_table_parity.py -q -- 5/5 (was 4/4)"
        status: pass
    human_judgment: false
  - id: D7
    description: "Full non-regression sweep: both native envs 129/129 across 17 suites (was 123/123); pio run 3/3 SUCCESS, flash unchanged (test-only plan); flash_utils.h byte-frozen; 30/30 across six named host-gate pytest modules; four checker scripts exit 0; sdp_bus_config.h blob-identical; ruff clean against py3.9 target"
    verification:
      - kind: unit
        ref: "pio test -e native / -e native_nodevtools -- 129/129 across 17 suites, both envs"
        status: pass
      - kind: unit
        ref: "pio run -- 3/3 SUCCESS (Leonardo 25954/28672, unchanged)"
        status: pass
      - kind: unit
        ref: "python3 -m pytest tests/test_sdp_table_parity.py tests/test_check_no_log_in_sdp_window.py tests/test_check_is_memory_cmd_no_ifdef.py tests/test_sdp_bus_config_drift.py tests/test_revision_constants_parity.py tests/test_dispatch_mirror.py -q -- 30 passed"
        status: pass
      - kind: unit
        ref: "check_no_log_in_sdp_window.py / check_is_memory_cmd_no_ifdef.py / check_dispatch.py / check_devtest_orchestrator.py -- all exit 0"
        status: pass
      - kind: unit
        ref: "gen_sdp_bus_config.py --check -- OK: matches a fresh regeneration"
        status: pass
      - kind: unit
        ref: "ruff check + ruff format --check tests/test_sdp_table_parity.py -- All checks passed / already formatted (ruff 0.15.20, py39 target per pyproject.toml)"
        status: pass
    human_judgment: false

duration: ~45min
completed: 2026-07-28
status: complete
---

# Phase 119 Plan 06: Three-Way AA-55-A0 Identity, D-12/D-14 Proofs, and the Standalone-Unlock Equality Summary

**Closed LOCK-05 with a three-way byte-identity + three-way distinctness guard over the production `EEPROM_SDP_ENABLE`/`FLASH_ENABLE_WRITE_PROTECTION`/`FLASH_ENABLE_WRITE` objects (two independent oracles: a link-time firmware guard and a source-text host parity leg), plus D-12's report-shape proof, D-14's fires/does-not-fire budget-WARN pair, and D-13's standalone-unlock-equals-auto-unlock stream equality — all as new native Unity cases beside the pre-existing two-way leg, never replacing it.**

## Performance

- **Duration:** ~45 min
- **Completed:** 2026-07-28
- **Tasks:** 3/3
- **Files modified:** 3 (2 firmware test files, 1 host test file)

## Accomplishments

- Added `extern const byte_flip_t EEPROM_SDP_ENABLE[3];` to `test_sdp_harness.cpp` beside `EEPROM_SDP_DISABLE`'s existing extern, copying its load-bearing-linkage comment shape.
- `test_lock05_three_way_enable_table_identity`: two separately-messaged byte-identity legs (`EEPROM_SDP_ENABLE` vs `FLASH_ENABLE_WRITE_PROTECTION`, and vs `FLASH_ENABLE_WRITE`) via `sdp_tables_identical`, plus all three entries' address/byte pairs pinned directly (including the terminal `{0x5555, 0xA0}`) — extends beside `test_lock05_enable_write_and_write_protection_identical` without modifying it (confirmed by `git diff` on that hunk).
- `test_lock05_enable_table_objects_distinct`: three pairwise `(const void*)` inequalities among the three production tables (the alias-refactor hazard guard), plus distinctness and length-difference (3 vs 6) from `EEPROM_SDP_DISABLE`.
- Added cases 20-23 to `test_eeprom28c_sdp.cpp`, all driving production ops:
  - **Case 20** (D-12): `MSG_INFO_SDP_LOCK` then `MSG_INFO_SDP_LOCK_DONE_US`, ordered positions asserted, `response_code` still `RESPONSE_CODE_OK`, driven with `FLAG_VERBOSE` unset (pins the unconditional bare `LOG_ID` spelling), unlock's ids and `MSG_WARN_SDP_UNLOCK_SKIPPED` asserted absent.
  - **Cases 21/22** (D-14): the t_BLC budget WARN proven to fire (scripted 301 µs against the derived 300 µs lock budget) and proven NOT to fire (scripted 50 µs), with the negative case also asserting both lock INFO ids are present so it cannot pass vacuously; `response_code` untouched on both paths.
  - **Case 23** (D-13): drove the standalone `CMD_SDP_UNLOCK` op directly via `h.firestarter_operation_main` (init/end are NULL per LOCK-02), snapshotted its stream, then drove the auto-unlock via `drive_write_init` and asserted exact-divergence `-1` — byte-identical streams — plus the reused-ids membership check (both unlock ids present, both lock ids absent).
- Added `test_eeprom_sdp_enable_matches_flash_enable_write_and_write_protection` to `test_sdp_table_parity.py`: a second, independent source-text oracle reusing the unmodified `_extract_byte_flip_pairs`, asserting all three extracted pair lists equal (two separately-messaged legs) plus the length-3 and terminal-pair `(0x5555, 0xA0)` checks.
- Marked **LOCK-05 Complete** in `REQUIREMENTS.md`, with a parenthetical naming all four proofs (the two firmware cases, Plan 119-05's Case 17, and the host parity leg); wording of the requirement itself unchanged; LOCK-02/LOCK-04/LOCK-06 confirmed still Pending, LOCK-01/LOCK-03 confirmed still Complete.

## Test Counts

| Suite/module | Before | After | Delta |
|---|---|---|---|
| `test_sdp_harness` (both native envs) | 15/15 | 17/17 | +2 |
| `test_eeprom28c_sdp` (both native envs) | 19/19 | 23/23 | +4 |
| Full `pio test -e native` (17 suites) | 123/123 | 129/129 | +6 |
| Full `pio test -e native_nodevtools` (17 suites) | 123/123 | 129/129 | +6 |
| `test_sdp_table_parity.py` | 4/4 | 5/5 | +1 |
| Six named host-gate modules combined | (29) | 30/30 | +1 |

`pio run`: 3/3 SUCCESS on all three AVR envs, flash figures unchanged from Plan 119-05's ending state (Leonardo 25954/28672, Uno 23814/32256, uno328pb 23858/32384) — this plan is test-only in both repos, spending zero flash.

## check_no_log_in_sdp_window.py Baseline

Unchanged from Plan 119-04/119-05's baseline: `PASS: no logging call in SDP timing window (.../eeprom_28c.cpp, emitter lines 298-314, completion-poll lines 348-361)`, exit 0. This plan is test-only and touched no production source, so no shift occurred — confirmed empirically, not assumed.

## EEPROM_SDP_ENABLE Extraction Under the Unmodified Host Extractor

Confirmed empirically (RESEARCH F-L's prediction held): `_extract_byte_flip_pairs("EEPROM_SDP_ENABLE")` extracted cleanly on the first attempt against the real `eeprom_28c.cpp` declaration syntax (`const byte_flip_t EEPROM_SDP_ENABLE[3] = { ... };`), with zero changes to the extractor's regex. `_extract_byte_flip_pairs` itself remains byte-unmodified (verified via `git diff` on `test_sdp_table_parity.py` — only the new test function and its context strings were added).

## Task Commits

Each task was committed atomically inside its own submodule:

1. **Task 1: Machine-check the three-way AA-55-A0 identity and distinctness** (`firestarter/`) — `2150163` (test)
2. **Task 2: Prove the lock's report shape, budget-WARN both ways, and standalone-vs-auto-unlock stream identity** (`firestarter/`) — `24f1494` (test)
3. **Task 3: Add the EEPROM_SDP_ENABLE source-text parity leg** (`firestarter_app/`) — `9ead17f` (test)

**Plan metadata:** committed alongside this SUMMARY (docs, meta commit staging both gitlinks + SUMMARY.md + REQUIREMENTS.md + STATE.md + ROADMAP.md).

## Files Created/Modified

- `firestarter/test/native/avr/test_sdp_harness/test_sdp_harness.cpp` — `extern const byte_flip_t EEPROM_SDP_ENABLE[3]` declaration; `test_lock05_three_way_enable_table_identity`; `test_lock05_enable_table_objects_distinct`
- `firestarter/test/native/avr/test_eeprom28c_sdp/test_eeprom28c_sdp.cpp` — cases 20-23 (D-12 report shape, D-14 budget-WARN pair, D-13 standalone-vs-auto-unlock equality)
- `firestarter_app/tests/test_sdp_table_parity.py` — `test_eeprom_sdp_enable_matches_flash_enable_write_and_write_protection`
- `.planning/REQUIREMENTS.md` — LOCK-05 checkbox + parenthetical only

## Decisions Made

See `key-decisions` in frontmatter for the five load-bearing ones (two-legs-not-transitive shape, distinctness completeness against EEPROM_SDP_DISABLE, Case 23's get_data override rationale, synthetic-vs-measured tick values, and the criterion-5 deviation). All are consistent with the plan's `must_haves.truths`/`prohibitions` verbatim — no deviation from the plan's explicit instructions was required beyond the plan's own pre-named criterion-5 deviation.

## Deviations from Plan

**None beyond the plan's own pre-named criterion-5 deviation** (ROADMAP criterion 5's "header comment" satisfied via the `eeprom_28c.cpp` comment + the pre-existing `test_sdp_harness.cpp:291-296` comment, deliberately not by editing the FIX-04 byte-frozen `flash_utils.h` — recorded above and in `key-decisions`, same deviation class as D-05/D-15). Plan executed exactly as written otherwise, including:
- `test_lock05_enable_write_and_write_protection_identical` unmodified (verified by `git diff` showing pure additions around it).
- No trace-based negative added between `FLASH_ENABLE_WRITE_PROTECTION` and `FLASH_ENABLE_WRITE`.
- `_extract_byte_flip_pairs` unmodified.
- No production file touched in either repo (`git diff --quiet -- include/flash_utils.h` exits 0; `git diff --stat` on both firmware commits shows only the two test files).
- No `CMD_SDP_*` added to `firestarter_app/firestarter/constants.py` (Phase 120 HOST-03 scope, untouched).

## Issues Encountered

None. All new cases passed on the first build/run in both native environments; the host parity leg extracted cleanly on the first attempt, matching RESEARCH F-L's prediction.

## User Setup Required

None — no external service configuration required.

## Known Stubs

None. This plan is test-only in both repositories; no UI or data-rendering path is affected, and `CMD_SDP_LOCK`/`CMD_SDP_UNLOCK` remain unreachable from the shipped CLI this phase (Phase 120 scope), which is a pre-existing, deliberate scope boundary, not a new stub introduced here.

## Requirement Status

**LOCK-05 is Complete.** `.planning/REQUIREMENTS.md` shows only that one row's checkbox changed (`git diff` confirms — wording of the requirement itself is byte-unchanged, only the trailing checkbox and a new parenthetical were added); the traceability table row for LOCK-05 was updated from Pending to Complete, and no other row was touched. **LOCK-02 stays OPEN** — this plan advances it (Case 20's report proof and Case 23's stream-identity proof are LOCK-02-relevant evidence) but does not close it; Plan 119-07's dispatch proofs close LOCK-02. LOCK-04 and LOCK-06 remain Pending as instructed; LOCK-01 and LOCK-03 remain Complete, untouched.

## Next Phase Readiness

- `EEPROM_SDP_ENABLE`'s three-way identity/distinctness is now machine-checked twice (link-time object comparison + source-text comparison), closing LOCK-05 — Plan 119-07 can build on this without re-litigating the safety claim.
- Case 20's report-shape proof and Case 23's stream-identity proof are ready evidence for Plan 119-07's LOCK-02-closing dispatch matrix.
- Leonardo flash headroom for LOCK-06's later arithmetic is **unchanged at 2718 B free** (this plan is test-only in firmware; `pio run` confirms identical figures to Plan 119-05's ending state).
- `check_no_log_in_sdp_window.py`'s baseline (emitter 298-314, poll 348-361) is unchanged and remains the reference for any future gate-range assertion.
- No blockers for Plan 119-07.

---
*Phase: 119-lock-sdp-enable-command-surface-fw-half*
*Completed: 2026-07-28*

## Self-Check: PASSED

- FOUND: `firestarter/test/native/avr/test_sdp_harness/test_sdp_harness.cpp`
- FOUND: `firestarter/test/native/avr/test_eeprom28c_sdp/test_eeprom28c_sdp.cpp`
- FOUND: `firestarter_app/tests/test_sdp_table_parity.py`
- FOUND: `2150163` (Task 1 commit, firestarter submodule)
- FOUND: `24f1494` (Task 2 commit, firestarter submodule)
- FOUND: `9ead17f` (Task 3 commit, firestarter_app submodule)
