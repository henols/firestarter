---
phase: 156-duplicated-report-extraction-boolean-convention-repair-firmw
plan: "02"
subsystem: testing
tags: [unity, pio-test, native_loop_v131, native, logging_id, severity-fork, planted-negative]

requires:
  - phase: 156-duplicated-report-extraction-boolean-convention-repair-firmw plan 01
    provides: ".planning/v1.33/156-before-figures.md -- the authoritative before-half baselines this plan measured against (80/80 native_loop_v131, 172/172 native/native_nodevtools)"
provides:
  - "test_vpp_eprom_v131.cpp: two new cases (eprom.cpp + flash_intel.cpp) closing DEDUP-03 blind spot 1 -- the under-voltage severity pairing"
  - "test_eeprom28c_sdp.cpp: test_case7_mismatching_chip_id_with_force_warns strengthened in both fork directions, closing DEDUP-03 blind spot 2 -- the chip-ID message id, in CI"
affects: [156-03, 156-04, 156-05, 156-06, 156-07]

tech-stack:
  added: []
  patterns:
    - "Planted-negative proof discipline: every new severity-fork assertion demonstrated RED against a deliberately transposed pair in a throwaway git worktree named `firestarter` (never any other name -- test_checker_convention.py hard-codes it), then GREEN on the real tree, both recorded with the exact failing message"
    - "Anti-hollow re-drive (Case 11's shape, reused here): pin a conditional id in BOTH directions inside one case via captured_frames.clear() + a second un-flagged drive, so an id assertion that only ever sees one direction cannot pass against a swap of both"

key-files:
  created: []
  modified:
    - firestarter/test/native/avr/test_vpp_eprom_v131/test_vpp_eprom_v131.cpp
    - firestarter/test/native/avr/test_eeprom28c_sdp/test_eeprom28c_sdp.cpp

key-decisions:
  - "Cited include/logging_id.h's ACTUAL measured line numbers (LOG_ERROR_ID_BYTES at :110, LOG_WARN_ID_BYTES at :119) rather than the plan's own stated :105/:119 -- :105 is LOG_ERROR_ID_U32, not LOG_ERROR_ID_BYTES, confirmed by direct read. Consistent with 156-01's 'measure, don't assume' precedent: this phase corrects stale figures rather than repeating them, and a source-file line citation is exactly the kind of fact that must be measured, not copied."
  - "Kept flash_intel.cpp's under-voltage case (test_vpp04_f) rather than deleting it: reading drive_vpp_init/configure_memory correctly predicted the arm is reachable (protocol 0x10 -> configure_flash_intel -> flash_intel_write_init -> flash_intel_check_vpp), and the case measured count_logged_id(MSG_WARN_VPP_LOW) == 1 on first run -- so DEDUP-03's coverage ceiling 2 for flash_intel.cpp's VPP path is NARROWED (the under-voltage arm now has one executing case), not removed (the over-voltage arm and the rest of the path stay uncovered, and native_loop_v131 itself still carries NO CI COVERAGE)."
  - "Kept test_case7_mismatching_chip_id_with_force_warns's existing name rather than renaming it, per the plan's own preference -- the name remains true of the first (FLAG_FORCE) drive, and renaming would have required a tests/test_requirement_case_mapping_v131.py mapping-table edit for no correctness gain."

requirements-completed: []

coverage:
  - id: D1
    description: "The under-voltage severity pairing (MSG_WARN_VPP_LOW / RESPONSE_CODE_WARNING) on eprom.cpp now has an oracle where it had none, proven RED against a planted transposition and GREEN on the real tree"
    requirement: "DEDUP-03"
    verification:
      - kind: unit
        ref: "firestarter/test/native/avr/test_vpp_eprom_v131/test_vpp_eprom_v131.cpp#test_vpp04_e_undervoltage_warning_pairing_fires_by_id_with_payload_shape (pio test -e native_loop_v131, 82/82)"
        status: pass
    human_judgment: false
  - id: D2
    description: "The same under-voltage severity pairing closed on flash_intel.cpp's twin arm, narrowing (not removing) coverage ceiling 2"
    requirement: "DEDUP-03"
    verification:
      - kind: unit
        ref: "firestarter/test/native/avr/test_vpp_eprom_v131/test_vpp_eprom_v131.cpp#test_vpp04_f_flash_intel_undervoltage_warning_pairing (pio test -e native_loop_v131, 82/82)"
        status: pass
    human_judgment: false
  - id: D3
    description: "The chip-ID mismatch message id is pinned by both fork directions inside test_case7, in CI, at an unchanged case count of 172"
    requirement: "DEDUP-03"
    verification:
      - kind: unit
        ref: "firestarter/test/native/avr/test_eeprom28c_sdp/test_eeprom28c_sdp.cpp#test_case7_mismatching_chip_id_with_force_warns (pio test -e native and -e native_nodevtools, 172/172 both)"
        status: pass
    human_judgment: false
  - id: D4
    description: "Both new assertions were seen RED against a deliberately planted transposition in a throwaway worktree and GREEN on the real tree, recorded in both directions"
    requirement: "DEDUP-03"
    verification:
      - kind: other
        ref: "This SUMMARY's Planted-Negative Evidence section -- two throwaway worktrees (/tmp/probe156a/firestarter, /tmp/probe156b/firestarter), both removed and pruned; git -C firestarter worktree list shows only the primary tree afterward"
        status: pass
    human_judgment: false

duration: ~50min
completed: 2026-08-23
status: complete
---

# Phase 156 Plan 02: Close Both DEDUP-03 Blind Spots Summary

**Authored an oracle for the under-voltage severity pairing (eprom.cpp and its flash_intel.cpp twin) and strengthened the existing chip-ID mismatch case in both fork directions -- every new assertion demonstrated RED against a planted transposition (in a throwaway `firestarter`-named worktree) and GREEN on the real tree, with the CI native case count unchanged at 172.**

## Performance

- **Duration:** ~50 min
- **Completed:** 2026-08-23
- **Tasks:** 2
- **Files modified:** 2 (both in `firestarter/test/native/avr/`)

## Accomplishments

- Closed DEDUP-03 blind spot 1 (RESEARCH probe B): added `test_vpp04_e_undervoltage_warning_pairing_fires_by_id_with_payload_shape` to `test_vpp_eprom_v131.cpp`, asserting `MSG_WARN_VPP_LOW` fires exactly once with `RESPONSE_CODE_WARNING` on an injected 12349 mV reading (setpoint 13000, boundary 12350), and that neither over-voltage id (`MSG_ERR_VPP_HIGH`, `MSG_WARN_VPP_HIGH`) also fires.
- Extended the same closure to `flash_intel.cpp`'s twin arm with `test_vpp04_f_flash_intel_undervoltage_warning_pairing` (protocol 0x10, setpoint 12000, injected 11399 mV, boundary 11400) -- the arm was reachable on first attempt, so DEDUP-03's coverage ceiling 2 for `flash_intel.cpp`'s VPP path is narrowed, not removed.
- `pio test -e native_loop_v131` now reports **82/82** over 2 suites, up from the 80/80 recorded in `156-before-figures.md`.
- Closed DEDUP-03 blind spot 2 (RESEARCH probe D): strengthened the existing `test_case7_mismatching_chip_id_with_force_warns` in `test_eeprom28c_sdp.cpp` with both fork directions -- `MSG_WARN_CHIP_ID_MISMATCH` present / `MSG_ERR_CHIP_ID_MISMATCH` absent under `FLAG_FORCE`, then (via a `captured_frames.clear()` re-drive copying Case 11's anti-hollow shape) the reverse under no flag. No new case was added -- `pio test -e native` and `-e native_nodevtools` both still report exactly **172/172** over 17 suites.
- Both new pieces of evidence were proven RED against a deliberately planted transposition in a throwaway worktree named `firestarter` (per the naming pitfall this tree's own `test_checker_convention.py` enforces), and GREEN on the real tree -- see the Planted-Negative Evidence section below for the exact substitutions, failing case names, and assertion messages.
- Confirmed assumption A3 empirically: `python3 -m pytest tests/test_requirement_case_mapping_v131.py -q` passes (9/9) after Task 1's commit, proving the per-suite floor really is a floor and adding cases to `test_vpp_eprom_v131` is genuinely free.
- Ran the full `pytest tests/ -q` leg after both commits landed: **348 passed, 0 failed** -- matches `156-before-figures.md`'s canonical-checkout figure exactly (not the stale 313/0/32 research quoted from an isolated worktree), comfortably clearing the phase gate's `>= 313 passed, 0 failed` floor.

## Task Commits

1. **Task 1: Close blind spot 1 -- the under-voltage severity pairing in test_vpp_eprom_v131** — `c764e27` (test)
2. **Task 2: Close blind spot 2 -- the chip-ID message id, in CI, at an unchanged case count** — `3d0b73d` (test)

**Plan metadata:** committed in the meta repo immediately after this SUMMARY (see the meta repo's own commit log).

## Files Created/Modified

- `firestarter/test/native/avr/test_vpp_eprom_v131/test_vpp_eprom_v131.cpp` — added `test_vpp04_e_undervoltage_warning_pairing_fires_by_id_with_payload_shape` and `test_vpp04_f_flash_intel_undervoltage_warning_pairing`, both registered in `RUN_TEST`
- `firestarter/test/native/avr/test_eeprom28c_sdp/test_eeprom28c_sdp.cpp` — strengthened `test_case7_mismatching_chip_id_with_force_warns` with WARN-direction and ERROR-direction id assertions (no new case; `RUN_TEST` count and `void test_case` count both unchanged at 34/33)

## Decisions Made

- Cited `include/logging_id.h`'s measured line numbers (`:110` for `LOG_ERROR_ID_BYTES`, `:119` for `LOG_WARN_ID_BYTES`) rather than the plan's own stated `:105`/`:119` -- direct read confirmed `:105` is `LOG_ERROR_ID_U32`, not `LOG_ERROR_ID_BYTES`. This is a plan-citation drift of the same kind `156-before-figures.md` catalogued for ROADMAP/REQUIREMENTS prose; corrected here rather than perpetuated, per the phase's own "measure, don't assume" discipline.
- Kept the `flash_intel.cpp` case (`test_vpp04_f`) rather than falling back to the plan's stated deletion path, because it reached the arm and passed on first run -- `count_logged_id(MSG_WARN_VPP_LOW)` returned `1`, not `0`. Recorded as narrowing coverage ceiling 2, not removing it: the over-voltage arm and the rest of `flash_intel.cpp`'s VPP path remain uncovered, and `native_loop_v131` itself still carries NO CI COVERAGE.
- Kept `test_case7`'s existing name rather than renaming it (the plan's stated preference when the name stays accurate) -- avoided an unnecessary `tests/test_requirement_case_mapping_v131.py` mapping-table edit.
- Removed all `DEDUP-0X` / `156-02` provenance tokens from source-file comments after an initial draft accidentally introduced them (self-caught via the plan's own `grep -cE 'DEDUP-0[0-9]|Phase 156|OD-[0-9]'` acceptance check, which must read `0`) -- Phase 154 removed this provenance style from shipped source deliberately, and this plan's own prohibitions restate it.

## Deviations from Plan

None from the plan's substantive instructions. One self-corrected authoring slip (not a Rule 1/2/3 deviation against the *plan's* code, but worth recording): an initial draft of the two new `test_vpp_eprom_v131.cpp` case comments named `156-02` and `DEDUP-03` directly, violating the plan's own explicit prohibition against GSD provenance tokens in shipped source comments. Caught by re-running the plan's own acceptance grep before committing, fixed in place, and re-verified GREEN (82/82) before the commit that shipped. No incorrect code was ever committed.

## Issues Encountered

- `tests/test_requirement_case_mapping_v131.py`'s porcelain-dependent tests (`test_planted_renamed_case_is_detected`, `test_planted_emptied_scan_root_fails_the_non_vacuity_leg`) failed when run against the dirty tree between editing and committing Task 1 -- expected behavior (these tests assert the firmware repo's working tree is clean), not a defect. Re-ran after Task 1's commit and all 9 tests passed, which is the empirical A3 confirmation the plan calls for.

## Planted-Negative Evidence

### Task 1 -- under-voltage severity pairing (eprom.cpp + flash_intel.cpp)

- **Worktree:** `/tmp/probe156a/firestarter` (created at `adf1a31`, removed and pruned afterward)
- **Substitution applied:** in both `src/proms/eprom.cpp:720` and `src/proms/flash_intel.cpp:46`, replaced `handle->response_code = RESPONSE_CODE_WARNING;` with `handle->response_code = RESPONSE_CODE_ERROR;` immediately after the `LOG_WARN_ID_BYTES(MSG_WARN_VPP_LOW, _b, 8);` call (the `(MSG_WARN_VPP_LOW, RESPONSE_CODE_WARNING)` pair, transposed toward ERROR).
- **Result:** `pio test -e native_loop_v131` reported `83 test cases: 2 failed, 80 succeeded` (a stray `SIGINT` after the failures truncated the run summary line, but both failures were captured before it). Both new cases failed:
  - `test_vpp04_e_undervoltage_warning_pairing_fires_by_id_with_payload_shape: Expected 2 Was 0. an injected 12349 mV reading (setpoint 13000, boundary 12350) must warn with RESPONSE_CODE_WARNING`
  - `test_vpp04_f_flash_intel_undervoltage_warning_pairing: Expected 2 Was 0. an injected 11399 mV reading (setpoint 12000, boundary 11400) must warn with RESPONSE_CODE_WARNING`
  - (`RESPONSE_CODE_WARNING == 2`, `RESPONSE_CODE_ERROR == 0` -- `include/firestarter.h`.)
- **Contrast:** before this plan, `156-before-figures.md` §5 recorded the whole `native_loop_v131` suite at `80 test cases: 80 succeeded` with no oracle on `MSG_WARN_VPP_LOW` at all -- the identical transposition planted against that pre-plan tree would have passed 80/80 GREEN (RESEARCH probe B, "BLIND EVERYWHERE"). After this plan, the same transposition is RED.
- Worktree removed via `git worktree remove --force` + `git worktree prune`; `git -C firestarter worktree list` confirmed only the primary tree remains; `git -C firestarter status --porcelain` confirmed clean before the commit.

### Task 2 -- chip-ID mismatch message id (eeprom_28c.cpp)

- **Worktree:** `/tmp/probe156b/firestarter` (created at `adf1a31`, removed and pruned afterward)
- **Substitution applied:** in `src/proms/eeprom_28c.cpp`'s `eeprom28c_check_chip_id`, swapped the id argument between the `FLAG_FORCE` branch and its `else`: `LOG_WARN_ID_BYTES(MSG_ERR_CHIP_ID_MISMATCH, _b, 4)` under `FLAG_FORCE` (was `MSG_WARN_CHIP_ID_MISMATCH`) and `LOG_ERROR_ID_BYTES(MSG_WARN_CHIP_ID_MISMATCH, _b, 4)` under the `else` (was `MSG_ERR_CHIP_ID_MISMATCH`), leaving both `response_code` stores (`RESPONSE_CODE_WARNING` / `RESPONSE_CODE_ERROR`) unchanged.
- **Result:** `pio test -e native -f "*test_eeprom28c_sdp*"` reported `34 test cases: 1 failed, 32 succeeded` (a stray `SIGHUP` after teardown truncated the run, matching this suite's own documented deferred-teardown flake, D-13 -- the failure itself was captured cleanly before it). The failing case:
  - `test_case7_mismatching_chip_id_with_force_warns: Case 7 (chip-ID severity fork, WARN direction): MSG_WARN_CHIP_ID_MISMATCH must appear in the captured frame ids under FLAG_FORCE -- severity rides entirely in the id (LOG_WARN_ID_BYTES / LOG_ERROR_ID_BYTES are the same alias of LOG_ID_BYTES), so this leg is what a transposed id would trip`
- **Contrast:** before this plan, RESEARCH measured the whole 172-case CI suite `172/172` GREEN under the equivalent transposition ("BLIND EVERYWHERE") -- `MSG_WARN_CHIP_ID_MISMATCH` and `MSG_ERR_CHIP_ID_MISMATCH` appeared in zero test files anywhere in the tree. After this plan, the identical transposition is RED.
- Worktree removed via `git worktree remove --force` + `git worktree prune`; `git -C firestarter worktree list` confirmed only the primary tree remains; `git -C firestarter status --porcelain` confirmed clean before the commit.

## User Setup Required

None — no external service configuration required. This plan adds and strengthens native host-side unit tests only.

## Next Phase Readiness

- Both DEDUP-03 blind spots RESEARCH identified are closed with regression evidence proven against the PRE-refactor code (both commits land at `adf1a31`'s successor state, before plans 03/04 touch `eprom.cpp`, `flash_intel.cpp`, or `eeprom_28c.cpp`), so these new assertions are genuine regression guards for plans 03 and 04 rather than post-hoc description of them.
- `firestarter` is now at `3d0b73d` on `gsd/v1.33-source-hygiene-firmware-size-reduction`, tree clean, no worktree remaining beyond the tracked `firestarter_py32_ci` sibling.
- Full verification block re-confirmed after both commits: `pio test -e native` 172/172, `-e native_nodevtools` 172/172, `-e native_loop_v131` 82/82, `tests/test_requirement_case_mapping_v131.py` 9/9, `pytest tests/ -q` 348/0.
- Plans 03 and 04 can proceed against `eprom.cpp`/`flash_intel.cpp`/`eeprom_28c.cpp` with this plan's two new/strengthened test cases now standing as regression evidence for the severity forks those plans must not disturb.
- No DEDUP-0X requirement was marked Complete in `.planning/REQUIREMENTS.md` — plan 07 is the landing plan that closes them. This plan's full contribution to DEDUP-03: both of RESEARCH's identified blind spots (probe B and probe D) are now closed, each with RED/GREEN planted-negative evidence recorded above.

---
*Phase: 156-duplicated-report-extraction-boolean-convention-repair-firmw*
*Completed: 2026-08-23*

## Self-Check: PASSED

- `.planning/phases/156-duplicated-report-extraction-boolean-convention-repair-firmw/156-02-SUMMARY.md` exists on disk — FOUND
- `firestarter` commit `c764e27` (test(156-02): pin the under-voltage severity pairing that nothing asserted) exists in `git log --oneline --all` — FOUND
- `firestarter` commit `3d0b73d` (test(156-02): pin the chip-ID mismatch message id in both fork directions) exists in `git log --oneline --all` — FOUND
- meta repo commit `2a2067fc` (docs(156-02): record SUMMARY for closing both DEDUP-03 blind spots) exists in `git log --oneline --all` — FOUND

No missing items.
