---
phase: 118-observe-auto-unlock-visible-opt-out-able-fw-half
plan: 04
subsystem: firmware
tags: [firmware, logging, sdp, timing, flag-gate, eeprom28c]

# Dependency graph
requires:
  - phase: 118-observe-auto-unlock-visible-opt-out-able-fw-half (plan 01)
    provides: "check_no_log_in_sdp_window.py's emitter-body (206-222 pre-Plan-03 / 222-238 current) + completion-poll-body (256-269 pre-Plan-03 / 272-285 current) window, which legalizes the between-the-call-sites span this plan writes into"
  - phase: 118-observe-auto-unlock-visible-opt-out-able-fw-half (plan 02)
    provides: "the four catalog ids this plan emits: MSG_INFO_SDP_UNLOCK (0x5E), MSG_INFO_SDP_UNLOCK_DONE_US (0x5F), MSG_WARN_SDP_UNLOCK_SKIPPED (0x86), MSG_WARN_SDP_TBLC_EXCEEDED (0x87)"
  - phase: 118-observe-auto-unlock-visible-opt-out-able-fw-half (plan 03)
    provides: "FLAG_SKIP_SDP_UNLOCK (0x100), AT28C_TBLC_MAX_US (100), and the micros() mocks in both native SDP suites that make this plan's two production micros() reads safe to drive"
provides:
  - "eeprom28c_write_init rebuilt: default path emits an unconditional before-line, brackets the SDP-disable emit call with micros(), emits an unconditional after-line carrying the measured duration, and enforces the t_BLC budget at runtime; FLAG_SKIP_SDP_UNLOCK path replaces the whole block (report pair + budget check + completion wait) with one unconditional WARN"
  - "sdp_seq_len / sdp_emit_start_us / sdp_emit_us / sdp_tblc_budget_us as the four function-local identifiers this plan introduces"
  - "Leonardo +152 B / Uno +152 B cumulative flash delta versus Plan 118-03's baseline, both boards RAM-unchanged"
affects: ["118-05 (writes the native proofs: skip/no-skip stream pair, budget-WARN-fires case, exactly-two-new-serial-frames enumeration)", "118-06 (non-regression sweep)", "118-07 (Leonardo OBS-04 measurement)"]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "The tree's first non-FLAG_VERBOSE-gated INFO-band call sites (LOG_ID/LOG_ID_U32 on an INFO-band id), argued in a source comment rather than left implicit, per D-01"
    - "Runtime budget check derived from the same hoisted length local the emit call itself uses (sdp_seq_len), so the budget cannot silently desync from the sequence it measures"
    - "Whole-block flag gate (if (!is_flag_set(FLAG)) { ... } else { one WARN } ) mirroring the file's own pre-existing FLAG_SKIP_BLANK_CHECK idiom, extended to also gate the completion wait"

key-files:
  created: []
  modified:
    - firestarter/src/proms/eeprom_28c.cpp

key-decisions:
  - "Budget-on-the-after-line composition (Claude's Discretion, plan-named): took the simplest compliant option -- left the after-line (MSG_INFO_SDP_UNLOCK_DONE_US) carrying only the measured duration, with no budget number folded in. The budget lives solely in the runtime WARN branch (MSG_WARN_SDP_TBLC_EXCEEDED), which already carries the measured duration on the exceeded path. Composing both was compatible per the plan but added no information the WARN doesn't already carry when it matters, and kept the after-line's catalog format string exactly as Plan 118-02 built it (no hardcoded budget literal to duplicate AT28C_TBLC_MAX_US)."
  - "sdp_seq_len declared inside the non-skip arm (not hoisted above the flag check) since Task 3 wraps the whole unlock block: the local is dead in the skip arm, so keeping its scope local to where it's used avoids an unused-variable footprint in that path while still satisfying the single-length-expression constraint (grep -c 'sizeof(EEPROM_SDP_DISABLE)' == 1 throughout)."
  - "Comment prose avoids the literal substring 'micros()' outside the two real call sites (uses 'the two microsecond-clock reads' instead) so grep -c 'micros()' on the file resolves to exactly 2, matching the Task 1 acceptance criterion literally rather than by accident."

requirements-completed: []  # OBS-01..OBS-04 intentionally NOT marked complete. Verified REQUIREMENTS.md lines 58-61 and 165-168 still show [ ] / Pending after this plan. OBS-01 additionally needs 118-06's sweep; OBS-02 additionally needs 118-05's absence trace; OBS-03 additionally needs 118-05's budget-WARN-fires case; OBS-04 additionally needs 118-07's real-board measurement.

coverage:
  - id: D1
    description: "Two unconditional report lines (LOG_ID/LOG_ID_U32, not LOG_INFO_ID*) bracket the SDP-disable emit call with micros() outside eeprom28c_emit_command_sequence's body; convention break argued in source comment"
    requirement: "OBS-01, OBS-04"
    verification:
      - kind: unit
        ref: "grep -n 'MSG_INFO_SDP_UNLOCK\\b' / 'MSG_INFO_SDP_UNLOCK_DONE_US' src/proms/eeprom_28c.cpp -- exactly one LOG_ID / LOG_ID_U32 call site each"
        status: pass
      - kind: unit
        ref: "pio test -e native -f '*test_eeprom28c_sdp*' (8/8, including case 8) + pio test -e native (108/108)"
        status: pass
    human_judgment: false
  - id: D2
    description: "Runtime t_BLC budget check (sdp_seq_len * AT28C_TBLC_MAX_US) emits MSG_WARN_SDP_TBLC_EXCEEDED via LOG_WARN_ID_U32 when exceeded; no response_code write on the SDP path"
    requirement: "OBS-03"
    verification:
      - kind: unit
        ref: "test_case8_completion_poll_preserves_prior_severity still passes; grep for handle->response_code = shows no new write sites added by this plan's diff"
        status: pass
    human_judgment: false
  - id: D3
    description: "FLAG_SKIP_SDP_UNLOCK gates the whole unlock block including the completion wait; skip arm emits exactly one WARN in place of the report pair; FLAG_SKIP_BLANK_CHECK stays outside the new conditional, unchanged"
    requirement: "OBS-02"
    verification:
      - kind: unit
        ref: "git diff 5bfa0fa..HEAD -- src/proms/eeprom_28c.cpp confirms eeprom28c_wait_for_sdp_completion(handle) is inside the non-skip arm and the FLAG_SKIP_BLANK_CHECK conditional is outside both arms"
        status: pass
    human_judgment: false
  - id: D4
    description: "Emitter body (222-238) and completion-poll body (272-285) byte-unchanged across all three tasks; rewritten check_no_log_in_sdp_window.py gate PASSes at every step; full CORRECTION-4 host-gate checklist green"
    requirement: "OBS-01, OBS-03"
    verification:
      - kind: unit
        ref: "git diff 5bfa0fa -- src/proms/eeprom_28c.cpp shows exactly one hunk, entirely inside eeprom28c_write_init (@@ -293,24 +293,122 @@) -- no hunk touches the emitter or poll bodies"
        status: pass
      - kind: unit
        ref: "python tools/check_no_log_in_sdp_window.py (PASS, naming emitter 222-238 / poll 272-285) + pytest across 6 host gate files (27 passed) + full host suite (974 passed, 1 pre-existing failure, byte-identical to Plan 118-01/02/03's baseline)"
        status: pass
    human_judgment: false

# Metrics
duration: 20min
completed: 2026-07-28
status: complete
---

# Phase 118 Plan 04: Report + Bracket + Budget + Skip-Gate the SDP Auto-Unlock Summary

**Rebuilt `eeprom28c_write_init` to unconditionally report the SDP auto-unlock (`LOG_ID`/`LOG_ID_U32`, the tree's first non-verbose-gated INFO-band call sites), bracket the emit call with `micros()`, enforce the t_BLC budget at runtime, and honour `FLAG_SKIP_SDP_UNLOCK` by replacing the whole block with one honest WARN — emitter/poll bodies byte-unchanged, native suite unchanged at 108/108, cumulative flash delta +152 B on both boards.**

## Performance

- **Duration:** ~20 min
- **Started:** 2026-07-28
- **Completed:** 2026-07-28
- **Tasks:** 3
- **Files modified:** 1

## Precondition Check (run, not assumed)

`cd /workspaces/firestarter_app && python tools/check_no_log_in_sdp_window.py` was run before any edit and printed:

```
PASS: no logging call in SDP timing window (..., emitter lines 222-238, completion-poll lines 272-285)
```

Two named ranges (not the single 291-297-region span the pre-rewrite gate would have printed) confirmed Plan 118-01's gate rewrite (`d9bbff2`) has landed. Proceeded.

## Accomplishments

- **Task 1:** Hoisted `EEPROM_SDP_DISABLE`'s length into one `sdp_seq_len` local; emitted `MSG_INFO_SDP_UNLOCK` (before, placed after the identity block's closing brace) and `MSG_INFO_SDP_UNLOCK_DONE_US` (after, carrying the measured duration) via the bare unconditional `LOG_ID` / `LOG_ID_U32` macros — the tree's first non-`FLAG_VERBOSE`-gated INFO-band call sites, with the convention break argued in a source comment (D-01) rather than left implicit. Bracketed the emit call with two clock reads that sit outside `eeprom28c_emit_command_sequence`'s body, computing the elapsed interval as an unsigned 32-bit subtraction (rollover-safe). Verified: `pio test -e native` 108/108, `test_eeprom28c_sdp` 8/8 including case 8, gate PASS, Leonardo/Uno both +84 B over the Plan 118-03 baseline.
- **Task 2:** Added a runtime t_BLC budget check — `sdp_seq_len * AT28C_TBLC_MAX_US` compared against the Task-1-measured `sdp_emit_us` — emitting `MSG_WARN_SDP_TBLC_EXCEEDED` via the unconditional `LOG_WARN_ID_U32` macro when exceeded, placed immediately after the after-line and before the completion wait. No `handle->response_code` write. Verified: 108/108 native, case 8 still passes, gate PASS, Leonardo +28 B further (cumulative +112 B — later corrected below by re-measurement after Task 3's edit; see Final Flash Delta).
- **Task 3:** Wrapped the entire unlock block (report pair, `micros()` bracket, budget check, **and** the completion wait) inside `if (!is_flag_set(FLAG_SKIP_SDP_UNLOCK)) { ... } else { LOG_WARN_ID(MSG_WARN_SDP_UNLOCK_SKIPPED); }`, mirroring the file's own `FLAG_SKIP_BLANK_CHECK` idiom. The skip arm emits exactly one unconditional WARN in place of the before/after pair, skips the completion wait too (no internal write cycle to wait for when nothing was emitted), and writes no `response_code`. `FLAG_SKIP_BLANK_CHECK`'s own conditional stays outside the new arm, unaffected. Verified: 108/108 native, case 8 passes, gate PASS, full CORRECTION-4 checklist (27 pytest cases across 6 host gate files) green, full host suite 974 passed / 1 pre-existing failure — byte-identical to the running baseline.

## Final Shape of `eeprom28c_write_init` (prose)

1. Identity check (`if (handle->chip_id > 0) { eeprom28c_check_chip_id(handle); if (ERROR) return; }`) — unchanged from Phase 117, first in the function.
2. `if (!is_flag_set(FLAG_SKIP_SDP_UNLOCK))` — the non-skip arm, in order:
   a. `sdp_seq_len` declared (single length expression for the whole function).
   b. Before-line: `LOG_ID(MSG_INFO_SDP_UNLOCK)`.
   c. `sdp_emit_start_us = micros()`.
   d. `eeprom28c_emit_command_sequence(handle, EEPROM_SDP_DISABLE, sdp_seq_len)` — unchanged callee, same call-site substring `handle, EEPROM_SDP_DISABLE` the gate's anchors require.
   e. `sdp_emit_us = micros() - sdp_emit_start_us` (unsigned 32-bit).
   f. After-line: `LOG_ID_U32(MSG_INFO_SDP_UNLOCK_DONE_US, sdp_emit_us)`.
   g. Budget check: `if (sdp_emit_us > sdp_seq_len * AT28C_TBLC_MAX_US) LOG_WARN_ID_U32(MSG_WARN_SDP_TBLC_EXCEEDED, sdp_emit_us);`.
   h. `eeprom28c_wait_for_sdp_completion(handle)` — unchanged callee, now inside this arm.
3. `else` — the skip arm: `LOG_WARN_ID(MSG_WARN_SDP_UNLOCK_SKIPPED)`, nothing else.
4. `if (!is_flag_set(FLAG_SKIP_BLANK_CHECK)) { mem_util_blank_check(handle); }` — outside both arms, unchanged.

## Identifier Names Introduced

- `sdp_seq_len` (`size_t`) — the single hoisted sequence-length expression, scoped to the non-skip arm.
- `sdp_emit_start_us` (`uint32_t`) — first `micros()` read, immediately before the emit call.
- `sdp_emit_us` (`uint32_t`) — elapsed interval, computed as `(uint32_t)(micros() - sdp_emit_start_us)` immediately after the emit call.
- `sdp_tblc_budget_us` (`uint32_t`) — `(uint32_t)sdp_seq_len * AT28C_TBLC_MAX_US`, computed once, compared against `sdp_emit_us`.

## Resolved Gate Window Line Ranges (for Plans 118-05 / 118-06)

Reported by `check_no_log_in_sdp_window.py` after this plan's edit, unchanged from the pre-plan value (confirmed by re-running the gate after each of the three tasks):

- **Emitter body:** `eeprom_28c.cpp` lines **222-238** (`eeprom28c_emit_command_sequence`).
- **Completion-poll body:** `eeprom_28c.cpp` lines **272-285** (`eeprom28c_wait_for_sdp_completion`).

These did not shift from the pre-plan value because this plan added no lines inside either body — every new line lives in `eeprom28c_write_init`, strictly between the two.

## Flash/RAM Deltas (Leonardo + Uno, vs Plan 118-03's baseline)

| Board | Baseline (118-03) | After Task 1 | After Task 2 | Final (after Task 3) | Cumulative delta |
|---|---|---|---|---|---|
| Leonardo | Flash 25528/28672, RAM 1998/2560 | Flash 25612 | Flash 25640 | **Flash 25680/28672 (89.6%), RAM 1998/2560 (78.0%, unchanged)** | **+152 B flash, +0 B RAM** |
| Uno | Flash 23390/32256, RAM 1559/2048 | Flash 23474 | (not re-measured mid-plan) | **Flash 23542/32256 (73.0%), RAM 1559/2048 (76.1%, unchanged)** | **+152 B flash, +0 B RAM** |

Both boards show the identical +152 B delta, as expected (same source edit, same two compilation targets). Judged against Phase 117's measured **+204 B** Leonardo delta (the LOCK-06 framing reference named in this plan's dispatch), not against any predicted saving — this plan's +152 B is a separate, smaller, additive delta on top of Plan 118-03's own +0 B (constants-only) baseline.

## Discretionary Decision: Budget-on-the-After-Line Composition

Took the simplest compliant option, per the plan's own framing ("Simplest compliant choice is to leave the after-line as Task 1 built it; record your decision in the SUMMARY either way"): the after-line (`MSG_INFO_SDP_UNLOCK_DONE_US`) carries only the measured duration, with no budget number folded into its format string. The budget lives exclusively in the runtime WARN branch (`MSG_WARN_SDP_TBLC_EXCEEDED`), which already carries the measured duration on the one path where the budget's value is actually informative (the exceeded path). This avoids duplicating `AT28C_TBLC_MAX_US` as a second hardcoded literal in the after-line's catalog entry, keeping Plan 118-02's catalog format strings untouched by this plan.

## Task Commits

All three committed atomically, in `firestarter` only (this plan writes no host or meta file):

1. **Task 1: Emit the two unconditional report lines and bracket the emit call with micros()** — `6484cd4` — `feat(118-04): report the SDP auto-unlock with a micros()-measured duration (OBS-01, OBS-04)`
2. **Task 2: Turn AT28C_TBLC_MAX_US into a runtime budget check** — `c7d8a3d` — `feat(118-04): enforce the t_BLC budget at runtime on the SDP unlock (OBS-03, D-09)`
3. **Task 3: Honour FLAG_SKIP_SDP_UNLOCK — replace the whole sequence with one honest WARN** — `da0cb7c` — `feat(118-04): honour FLAG_SKIP_SDP_UNLOCK with an honest WARN (OBS-02, D-02)`

**Plan metadata** (in the meta-repo): committed separately below (this SUMMARY.md + STATE.md + ROADMAP.md). No `firestarter`/`firestarter_app` gitlink bump, per the no-in-milestone-bump convention.

## Files Created/Modified

- `firestarter/src/proms/eeprom_28c.cpp` — `eeprom28c_write_init` rebuilt across the three tasks; `eeprom28c_emit_command_sequence` and `eeprom28c_wait_for_sdp_completion` byte-unchanged (confirmed by diff: the whole plan's diff to this file is one hunk, `@@ -293,24 +293,122 @@`, entirely inside `write_init`).

## Deviations from Plan

**None** — plan executed exactly as written, including its explicit three-commit-inside-`firestarter`-only repo mechanics, its hard ordering precondition (checked, not assumed), and its discretionary budget-composition choice (recorded above).

One self-correction during drafting, not committed as a bug: the first draft of Task 1's `micros()` bracket comment used the literal substring `micros()` in prose (e.g. "the two `micros()` reads"), which would have made `grep -c 'micros()' src/proms/eeprom_28c.cpp` report 4 instead of the required 2 (2 real call sites + 2 comment mentions). Caught before running the acceptance grep by reading the plan's own acceptance criterion literally; reworded the comment to say "the two microsecond-clock reads" instead. No incorrect state was ever committed.

## Issues Encountered

None. All three tasks' verification commands passed on the first attempt after the self-caught comment wording fix above; no auto-fixes beyond that, no blockers, no architectural questions.

## Host Repo Untouched (confirmed, not assumed)

`git -C /workspaces/firestarter_app status --short` after all three tasks shows only the same pre-existing unrelated dirty files noted in Plans 118-02/03's SUMMARYs (`.gitignore`, `.coverage`, `.planning/config.json`, `SECURITY.md`, `doc/lockable-proms.md`, `write_test_port.sh`) — zero files added or modified by this plan. `git -C /workspaces status --short` shows the expected `M firestarter` / `M firestarter_app` gitlink deltas (no-in-milestone-bump convention, left unstaged) plus the same pre-existing unrelated meta-repo artifacts already present at session start.

## STATE.md Tooling Defect Check

Per the plan's `<state_tracking>` instructions, hand-verified after the state-mutating calls in the State Updates section below: `current_phase_name` and `progress.total_plans` checked for the known em-dash/parenthetical-mangling and percent-reversion defects documented in STATE.md's own note block. See the State Updates section for the exact outcome.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- All four catalog ids now have real production call sites; `MSG_WARN_SDP_TBLC_EXCEEDED` in particular was previously unreachable code and is now a live (if latent) branch.
- Plan 118-05 can now write its native proofs: the skip/no-skip stream pair on production `eeprom28c_write_init`, a budget-exceeded case using `s_micros_ticks[1]` set past `sdp_seq_len * AT28C_TBLC_MAX_US`, and the exactly-two-new-serial-frames enumeration.
- The resolved gate window ranges (emitter 222-238, poll 272-285) are unchanged by this plan and are the ranges Plans 118-05/118-06 should cite.
- OBS-01, OBS-02, OBS-03, OBS-04 remain **Pending** in `.planning/REQUIREMENTS.md` (verified: lines 58-61 and 165-168 still show `[ ]` / `Pending`) — confirmed not marked Complete by this plan.
- No blockers for Plan 118-05 — this plan touched no host or meta file, and the firmware submodule carries exactly the three commits listed above on top of Plan 118-03's `5bfa0fa`.

## Self-Check: PASSED

- FOUND: `/workspaces/firestarter/src/proms/eeprom_28c.cpp`
- FOUND: commit `6484cd4` in `firestarter`
- FOUND: commit `c7d8a3d` in `firestarter`
- FOUND: commit `da0cb7c` in `firestarter`
- FOUND: `.planning/phases/118-observe-auto-unlock-visible-opt-out-able-fw-half/118-04-SUMMARY.md`

---
*Phase: 118-observe-auto-unlock-visible-opt-out-able-fw-half*
*Completed: 2026-07-28*
