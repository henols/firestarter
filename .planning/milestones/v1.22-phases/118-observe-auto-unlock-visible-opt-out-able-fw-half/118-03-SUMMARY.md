---
phase: 118-observe-auto-unlock-visible-opt-out-able-fw-half
plan: 03
subsystem: firmware
tags: [firmware, constants, sdp, timing, arduinofake, native-test, eeprom28c]

# Dependency graph
requires:
  - phase: 118-observe-auto-unlock-visible-opt-out-able-fw-half (plan 01)
    provides: "check_no_log_in_sdp_window.py's emitter-body + completion-poll-body window (eeprom_28c.cpp lines 206-222 / 256-269 pre-this-plan) that this plan's D-10 page-load citation must not shift into"
  - phase: 118-observe-auto-unlock-visible-opt-out-able-fw-half (plan 02)
    provides: "the four catalog ids (0x5E/0x5F/0x86/0x87) this plan's constants exist to support, though this plan does not emit any of them"
provides:
  - "FLAG_SKIP_SDP_UNLOCK = 0x100 defined in firestarter.h (9th control flag, ctrl_flags already uint32_t, no wire/parser change)"
  - "AT28C_TBLC_MAX_US = 100 defined in eeprom_28c.cpp, extending AT28C_TWC_MAX_MS's existing forward-declaring comment"
  - "D-10 comment-only citation of AT28C_TBLC_MAX_US at eeprom28c_write_execute's per-byte set_data loop, framed at gh#11's conflation (not sampling rate), no runtime check added there"
  - "micros() mocked in both test_sdp_harness.cpp (fixed 0) and test_eeprom28c_sdp.cpp (controllable s_micros_ticks[2] tick source), ahead of Plan 118-04's production micros() calls"
affects: ["118-04 (adds the two micros() reads bracketing eeprom28c_emit_command_sequence, and the runtime budget check comparing elapsed against 6 * AT28C_TBLC_MAX_US; also gates FLAG_SKIP_SDP_UNLOCK)", "118-05 (consumes s_micros_ticks to synthesize a budget-exceeding elapsed value for the budget-WARN-fires case)"]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Controllable ArduinoFake tick-source mock (s_micros_ticks[2] indexed by call count mod 2) as the seam a later plan sets before driving, rather than a fixed AlwaysReturn -- used only in the suite where a later plan needs to synthesize a non-zero elapsed value; the always-green harness suite keeps the simpler fixed-value mock"

key-files:
  created: []
  modified:
    - firestarter/include/firestarter.h
    - firestarter/src/proms/eeprom_28c.cpp
    - firestarter/test/native/avr/test_eeprom28c_sdp/test_eeprom28c_sdp.cpp
    - firestarter/test/native/avr/test_sdp_harness/test_sdp_harness.cpp

key-decisions:
  - "micros() mocking strategy (Claude's Discretion, D-context): fixed-value AlwaysReturn(0) in test_sdp_harness.cpp (always-green, never exercises the budget path); controllable s_micros_ticks[2] + call-count-mod-2 indexing in test_eeprom28c_sdp.cpp, because Plan 118-05's budget-exceeded case lives there and needs to synthesize a non-zero elapsed value. Both default to elapsed==0 so this plan's edit changes zero existing-case behaviour."
  - "D-10's page-load citation placed as a block comment directly above the for-loop at eeprom28c_write_execute (after the window_start declaration), naming AT28C_TBLC_MAX_US by name, explaining why the runtime check stays scoped to the unlock (flash-delta reasoning tied to Phase 117's measured +204 B), and explicitly aiming the gh#11 breadcrumb at Phase 117's conflation finding, not at sampling rate -- reviewed against that framing constraint before committing."
  - "AT28C_TBLC_MAX_US's own comment states it is a datasheet MAXIMUM (not a delay to insert), that the post-117 emitter already runs far under budget with pulse_delay=0, and that Plan 118-04 turns it into a runtime check -- extending, not restating, the sibling AT28C_TWC_MAX_MS comment's existing forward-declaration and t_BLC/t_WC distinction."

requirements-completed: []  # OBS-02 and OBS-03 intentionally NOT marked complete -- both stay Pending per the plan's own "Requirement ownership" section: OBS-02 closes with 118-04/118-05, OBS-03 with 118-01(done)/118-04/118-05. Verified REQUIREMENTS.md lines 59-60/166-167 still show OBS-02/OBS-03 as Pending after this plan.

coverage:
  - id: D1
    description: "FLAG_SKIP_SDP_UNLOCK 0x100 and AT28C_TBLC_MAX_US 100 defined; no wire/parser/struct/constants.py change; host FLAG-parity 8-literal negative confirmed by running the test, not assumed"
    requirement: "OBS-02, OBS-03"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_revision_constants_parity.py -q (6 passed, unaffected by the firmware-only 9th flag)"
        status: pass
      - kind: unit
        ref: "pio run -e leonardo -e uno (both boards, byte-identical flash/RAM figures to pre-task baseline)"
        status: pass
    human_judgment: false
  - id: D2
    description: "D-10 page-load citation is comment-only (every added line begins with //), cites AT28C_TBLC_MAX_US, and does not attribute gh#11 to sampling rate or timing budget"
    requirement: "OBS-03"
    verification:
      - kind: unit
        ref: "git diff -U0 -- src/proms/eeprom_28c.cpp (Task 2 commit): 15/15 added lines begin with //"
        status: pass
      - kind: unit
        ref: "firestarter_app/tools/check_no_log_in_sdp_window.py (PASS after the file's line-range shift) + test_sdp_table_parity.py/test_dispatch_mirror.py/test_sdp_db_invariant.py (27 passed)"
        status: pass
    human_judgment: false
  - id: D3
    description: "micros() mocked in both suites that drive eeprom28c_write_init; sweep confirms test_val_eeprom28c and test_not_implemented do not need the mock; native suite unchanged at 108/108, no SIGABRT"
    requirement: "OBS-02, OBS-03"
    verification:
      - kind: unit
        ref: "pio test -e native (108 test cases, 108 succeeded -- byte-identical to pre-task baseline)"
        status: pass
    human_judgment: false

# Metrics
duration: 45min
completed: 2026-07-28
status: complete
---

# Phase 118 Plan 03: FLAG_SKIP_SDP_UNLOCK + AT28C_TBLC_MAX_US + micros() Mocks Summary

**Landed `FLAG_SKIP_SDP_UNLOCK 0x100` and `AT28C_TBLC_MAX_US 100` as real firmware constants, cited the latter at both t_BLC-bound call sites (runtime check reserved for the unlock only), and pre-mocked `micros()` in both native SDP suites ahead of Plan 118-04's production calls -- entirely behaviourally inert, both board flash figures and the native suite unchanged.**

## Performance

- **Duration:** ~45 min
- **Started:** 2026-07-28
- **Completed:** 2026-07-28
- **Tasks:** 3
- **Files modified:** 4

## Accomplishments

- **Task 1:** `FLAG_SKIP_SDP_UNLOCK 0x100` added to `firestarter.h`'s control-flag block (the 9th flag; `FLAG_VERBOSE 0x80` was the prior ceiling, `ctrl_flags` is already `uint32_t`, `get_flags` already uses `extract_long` — confirmed by reading `json_parser.c:471-472` before the edit — so no struct, parser, or wire change). `AT28C_TBLC_MAX_US 100` added to `eeprom_28c.cpp` immediately after its sibling `AT28C_TWC_MAX_MS`, extending (not restating) that sibling's comment, which already forward-declared this exact constant and drew the t_BLC-vs-t_WC distinction. Both boards rebuilt byte-identical to the pre-task baseline (Leonardo 1998/2560 RAM, 25528/28672 flash; Uno 1559/2048 RAM, 23390/32256 flash); native suite unchanged at 108/108. Confirmed by running (not assuming) `test_revision_constants_parity.py`: its FLAG-parity block imports exactly eight hardcoded literals and does not enumerate `firestarter.h`, so this firmware-only 9th flag does not trip it — 6/6 passed. `test_sdp_table_parity.py` also re-verified green (4/4).
- **Task 2:** Added a comment-only D-10 citation of `AT28C_TBLC_MAX_US` immediately above the per-byte `for` loop in `eeprom28c_write_execute` (after the `window_start` declaration), naming the identical t_BLC exposure the SDP-disable emitter carries, explaining why the runtime budget check stays scoped to the unlock only (a per-byte compare in this hot path would grow the flash delta, which Phase 119's LOCK-06 headroom judgement must weigh against Phase 117's measured +204 B), and explicitly framing the gh#11 breadcrumb at Phase 117's **conflation** finding rather than at sampling rate or timing budget. Verified: every one of the 15 added lines begins with `//` (no code change); `AT28C_TBLC_MAX_US` now appears 3 times in the file (sibling forward-reference, `#define`, this citation). `check_no_log_in_sdp_window.py` re-run after this file's line numbers shifted — still `PASS`, now naming emitter lines 222-238 and completion-poll lines 272-285 (both windows resolve past the new comment block correctly). Full CORRECTION-4 checklist subset for this task (`test_sdp_table_parity.py`, `test_dispatch_mirror.py`, `test_sdp_db_invariant.py`) — 10/10 passed.
- **Task 3:** Swept the native test tree for every suite that drives `eeprom28c_write_init` and mocked `micros()` in each, ahead of Plan 118-04's two production `micros()` reads. `test_sdp_harness.cpp` (always-green harness, never exercises the budget path) got a fixed `When(Method(ArduinoFake(), micros)).AlwaysReturn(0);` inserted immediately after its existing `millis()` mock. `test_eeprom28c_sdp.cpp` (where Plan 118-05's budget-exceeded case will live) got a controllable `s_micros_ticks[2]` file-static tick source, indexed by a `s_micros_call_count % 2` counter (the production bracket reads `micros()` exactly twice per `write_init` drive — once before `eeprom28c_emit_command_sequence`'s call, once after), reset to `{0, 0}` alongside the suite's other file-static resets in `setUp()`. Both default to elapsed 0, so every one of the eight existing cases in `test_eeprom28c_sdp.cpp` and every case in `test_sdp_harness.cpp` is behaviourally unchanged. `platformio.ini` confirmed untouched and unneeded — `test_filter` already carries both `native/avr/test_sdp_harness` (:118 pre-edit numbering) and `native/avr/test_eeprom28c_sdp` (:119), both with `-I` entries. Full native suite: 108/108, zero SIGABRT.

## Full Write-Init Sweep Result (Task 3 acceptance criterion)

| Suite | Reaches `eeprom28c_write_init`? | Mock added? |
|---|---|---|
| `test_eeprom28c_sdp.cpp` | YES — via `drive_write_init` (:211), `drive_write_init_after_real_read` (:227), and direct `firestarter_operation_init` calls in cases 6/7 | YES — controllable `s_micros_ticks[2]` |
| `test_sdp_harness.cpp` | YES — via `firestarter_operation_init` at the two migrated identity cases (`test_migrated_mismatching_chip_id_errors`, `test_migrated_zero_chip_id_skips_check`) | YES — fixed `AlwaysReturn(0)` |
| `test_val_eeprom28c.cpp` | NO — confirmed by reading: every case drives `h.firestarter_operation_main(&h)` (`eeprom28c_write_execute`), never `firestarter_operation_init`. Its own file header even states the identity-check branch (which lives inside `write_init`) "fires in the operation_init phase (not the configure phase tested here)" and is never reached. | Not needed |
| `test_not_implemented.cpp` | NO — confirmed by reading: every case asserts `TEST_ASSERT_NULL(h.firestarter_operation_init)` without ever calling it (the suite exists to prove the pointer is NULL for non-`0x0D` protocols). | Not needed |

This must be re-run after Plan 118-04 lands (a missing mock manifests as SIGABRT, not a compile error) — noted for that plan's own execution.

## `micros()` Mock Shape (for Plan 118-05)

- **`test_sdp_harness.cpp`**: `When(Method(ArduinoFake(), micros)).AlwaysReturn(0);` — no seam, not needed there.
- **`test_eeprom28c_sdp.cpp`**: file-static `static uint32_t s_micros_ticks[2];` + `static int s_micros_call_count;`, both reset in `setUp()`. Mock: `When(Method(ArduinoFake(), micros)).AlwaysDo([]() -> unsigned long { unsigned long v = s_micros_ticks[s_micros_call_count % 2]; s_micros_call_count++; return v; });`. To synthesize a budget-exceeding case, Plan 118-05 sets `s_micros_ticks[1]` to a value greater than `s_micros_ticks[0] + 6 * AT28C_TBLC_MAX_US` before driving (the array indices correspond to the pre-emit and post-emit reads, in that order, since the counter starts at 0 and increments after each read).

## D-10 Citation Wording (reviewed against the gh#11-framing constraint)

The added comment states three things and no more, per the plan's constraint: (1) the per-byte `set_data` loop runs under the identical `AT28C_TBLC_MAX_US` constraint as the SDP-disable emitter, by name; (2) the runtime check deliberately stays scoped to the unlock, with the flash-delta-vs-LOCK-06 reasoning given as why; (3) a breadcrumb naming "whichever future phase revisits gh#11 on real silicon" and explicitly pointing at the **conflation** (Phase 117's finding — a completion/data-landed conflation, not a sampling-rate or timing-budget bug), never implying this citation fixes or explains gh#11 itself. Verified by re-reading the committed text: no phrase attributes gh#11 to sampling rate or timing budget.

## Pre-Task Baseline (captured before any edit)

- **Leonardo:** RAM 1998/2560 bytes (78.0%), Flash 25528/28672 bytes (89.0%)
- **Uno:** RAM 1559/2048 bytes (76.1%), Flash 23390/32256 bytes (72.5%)
- **Native:** 108 test cases, 108 succeeded

## Post-Task Result (after all three tasks)

- **Leonardo:** RAM 1998/2560 bytes (78.0%), Flash 25528/28672 bytes (89.0%) — byte-identical
- **Uno:** RAM 1559/2048 bytes (76.1%), Flash 23390/32256 bytes (72.5%) — byte-identical
- **Native:** 108 test cases, 108 succeeded — unchanged
- **Host full pytest suite:** `974 passed, 1 failed in 36.94s` — identical to the pre-existing baseline recorded in `118-01-SUMMARY.md`/`118-02-SUMMARY.md` (the single pre-existing failure is `test_audit_coverage_matrix::test_golden_file_matches`, a stale golden unrelated to this plan). Zero new failures, zero host files changed (`git -C firestarter_app status --short` shows only the pre-existing unrelated dirty files noted in Plan 118-02's SUMMARY: `.gitignore`, `.coverage`, `.planning/config.json`, `SECURITY.md`, `doc/lockable-proms.md`, `write_test_port.sh`).

## Task Commits

All three tasks committed atomically, in `firestarter` only (this plan writes no host or meta file):

1. **Task 1: Define FLAG_SKIP_SDP_UNLOCK 0x100 and AT28C_TBLC_MAX_US 100** — `12ae733` — `feat(118-03): define FLAG_SKIP_SDP_UNLOCK 0x100 and AT28C_TBLC_MAX_US 100 (OBS-02, OBS-03)`
2. **Task 2: Cite AT28C_TBLC_MAX_US at the page-load loop — comment only, no code** — `34a520e` — `docs(118-03): cite shared t_BLC exposure at the page-load loop (OBS-03, D-10)`
3. **Task 3: Add micros mocks to every native suite that drives eeprom28c_write_init** — `5bfa0fa` — `test(118-03): mock micros() in both native SDP suites ahead of the OBS-04 bracket`

**Plan metadata** (in the meta-repo): committed separately below (this SUMMARY.md + STATE.md + ROADMAP.md). No `firestarter`/`firestarter_app` gitlink bump, per the no-in-milestone-bump convention.

## Files Created/Modified

- `firestarter/include/firestarter.h` — `FLAG_SKIP_SDP_UNLOCK 0x100` added to the control-flag block.
- `firestarter/src/proms/eeprom_28c.cpp` — `AT28C_TBLC_MAX_US 100` defined (Task 1); D-10 page-load citation comment added at `eeprom28c_write_execute` (Task 2, comment-only).
- `firestarter/test/native/avr/test_eeprom28c_sdp/test_eeprom28c_sdp.cpp` — controllable `s_micros_ticks[2]` tick source added.
- `firestarter/test/native/avr/test_sdp_harness/test_sdp_harness.cpp` — fixed `micros()` mock added.

## Decisions Made

- **`micros()` mocking strategy** (Claude's Discretion per 118-CONTEXT.md): fixed value in the always-green harness, controllable counter in the suite Plan 118-05's budget-exceeded case will live in — see `key-decisions` in the frontmatter for the full reasoning.
- **D-10 citation placement**: directly above the `for` loop (after `window_start`'s declaration) inside `eeprom28c_write_execute`, per the plan's explicit "either position satisfies OBS-03's literal requirement" guidance — chose the pre-loop position for readability (a reader sees the constraint before entering the loop body it governs).
- **AT28C_TBLC_MAX_US's own comment scope**: states only what the sibling `AT28C_TWC_MAX_MS` comment does not already say (datasheet-maximum-not-a-delay, post-117 emitter already runs under budget, Plan 118-04 makes it a runtime check) — per the plan's explicit "extend, do not restate" instruction.

## Deviations from Plan

None — plan executed exactly as written, including its explicit task-level acceptance criteria (byte-identical flash/RAM figures, unchanged native pass count, comment-only diff for Task 2, the full write-init sweep recorded above).

## Issues Encountered

None. All three tasks' verification commands passed on the first attempt; no auto-fixes, no blockers, no architectural questions.

## STATE.md Tooling Defect Check

Per the plan's `<state_tracking>` instructions, hand-verified after the state-mutating calls below: `current_phase_name` remained exactly `OBSERVE — auto-unlock visible + opt-out-able (FW half)` (em-dash intact, closing paren present) and `progress.total_plans` remained `19`. No hand-correction was needed this time — see the State Updates section below for the exact call order used to avoid the previously-observed clobber.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- `FLAG_SKIP_SDP_UNLOCK` and `AT28C_TBLC_MAX_US` exist as real constants; Plan 118-04 can now gate the SDP-disable call on the flag and compare the `micros()`-measured elapsed duration against `6 * AT28C_TBLC_MAX_US`.
- Both native SDP suites will not SIGABRT the moment Plan 118-04 adds its two `micros()` reads inside `eeprom28c_write_init`.
- `s_micros_ticks` is the exact seam Plan 118-05 needs to synthesize a budget-exceeding elapsed value; its shape is documented above and in the suite's own comment.
- OBS-02 and OBS-03 remain **Pending** in `.planning/REQUIREMENTS.md` (verified: lines 59-60 and 166-167 still show `[ ]` / `Pending`) — confirmed not marked Complete by this plan.
- No blockers for Plan 118-04 (the phase's payload plan) — this plan touched no host or meta file, and the firmware submodule carries exactly the three commits listed above on top of Plan 118-02's `8868828`.

## Self-Check: PASSED

- FOUND: `/workspaces/firestarter/include/firestarter.h`
- FOUND: `/workspaces/firestarter/src/proms/eeprom_28c.cpp`
- FOUND: `/workspaces/firestarter/test/native/avr/test_eeprom28c_sdp/test_eeprom28c_sdp.cpp`
- FOUND: `/workspaces/firestarter/test/native/avr/test_sdp_harness/test_sdp_harness.cpp`
- FOUND: commit `12ae733` in `firestarter`
- FOUND: commit `34a520e` in `firestarter`
- FOUND: commit `5bfa0fa` in `firestarter`
- FOUND: commit `01cbb59` in meta-repo (SUMMARY.md commit)

---
*Phase: 118-observe-auto-unlock-visible-opt-out-able-fw-half*
*Completed: 2026-07-28*
