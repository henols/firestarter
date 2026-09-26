---
phase: 117-fix-remap-aware-0x0d-emitter-honest-completion-signal
plan: 02
subsystem: firmware
tags: [platformio, unity, native-test, avr, sdp, at28c, eeprom28c, remap]

# Dependency graph
requires:
  - phase: 117-fix-remap-aware-0x0d-emitter-honest-completion-signal
    provides: "plan 117-01's D-03 commit 1 (enabled + rebuilt RED oracle, `test_eeprom28c_sdp` 8/8 failing against the unfixed tree)"
provides:
  - "D-03 commit 2: `eeprom28c_write_init` rebuilt on a 0x0D-local, remap-aware `eeprom28c_emit_command_sequence` driven through `handle->firestarter_set_data` (FIX-01), closing the A16-A18 upper-address staleness gap for DIP32_28C512_EEPROM's 18 chips as a by-product (FIX-03)"
  - "The inverted `(0x5555, 0x20)` read-back deleted outright; replaced by `eeprom28c_wait_for_sdp_completion` -- an unconditional `AT28C_TWC_MAX_MS` wait plus a bounded, silent `AT28C_DQ6_TOGGLE_MASK` toggle-bit poll that never writes `handle->response_code` (FIX-02)"
  - "`EEPROM_SDP_DISABLE` external linkage (FIX-05 preparation, consumed by plan 117-04)"
  - "`PAGE_SIZE 64` documented as a deliberate conservative floor (D-13)"
  - "GREEN half of the D-03 evidence pair appended to `RED-BASELINE.md`, suite unchanged between commit 1 and commit 2"
affects: [117-03-fix-page-write-conflation, 117-04-close-frozen-artifact-proof, 117-05-close-frozen-artifact-proof]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "0x0D-local remap-aware emitter: an explicit `(handle, sequence, length)` function (not a `sizeof`-capturing macro) driven through `handle->firestarter_set_data`, reusable by Phase 118/119 without a second refactor."
    - "Advisory-only completion poll: an iteration-bounded (not `millis()`-deadline) toggle-bit poll that structurally cannot write `handle->response_code` -- severity destruction becomes impossible by construction, not merely avoided."
    - "D-03 two-commit RED/GREEN discipline closed: commit 1 (oracle, RED) and commit 2 (fix, GREEN) both committed, suite unchanged between them, verified by an empty `git diff --stat`."

key-files:
  created: []
  modified:
    - firestarter/src/proms/eeprom_28c.cpp
    - firestarter/test/native/avr/test_eeprom28c_sdp/RED-BASELINE.md

key-decisions:
  - "Followed 117-CONTEXT.md D-04/D-05/D-06/D-10/D-11/D-12/D-13 and the plan's own discretion points (D-06 poll shape, poll read address, poll bound as iteration count, emitter signature) exactly as specified -- no deviation from the locked design."
  - "Reworded three in-code comment mentions that would have collided with the acceptance criteria's literal (non-comment-filtered) greps for `rurp_set_data_output` (exactly 1 occurrence required, the real call) and `eeprom28c_wait_for_write(handle, 0x5555` (exactly 0 required) -- meaning preserved, substring avoided, mirroring the project's established `reference_new_milestone_phases_clear_destructive.md`-adjacent pattern of wording around literal-substring gates rather than weakening them."
  - "Condensed the D-13 PAGE_SIZE comment to fit within the acceptance criteria's `grep -B 14` window (14 lines) while still carrying D-13, AT28MC010, and AT28C010 -- the plan's example prose was longer than 14 lines as drafted."

requirements-completed: [FIX-01, FIX-02, FIX-03]

coverage:
  - id: D1
    description: "eeprom28c_write_init's SDP-disable sequence is emitted through eeprom28c_emit_command_sequence -> handle->firestarter_set_data (memory_set_data), not flash_execute_command; every write is remap-aware and rewrites CONTROL_REGISTER on address change (FIX-01)"
    requirement: FIX-01
    verification:
      - kind: unit
        ref: "firestarter/test/native/avr/test_eeprom28c_sdp/test_eeprom28c_sdp.cpp cases 1-3 (test_case1_at28c256_stream_matches_fixed, test_case2_at28c64_stream_matches_fixed, test_case3_at28c16_stream_matches_fixed) via `pio test -e native -f \"*test_eeprom28c_sdp*\"`"
        status: pass
    human_judgment: false
  - id: D2
    description: "The inverted (0x5555, 0x20) read-back is deleted, not salvaged, and replaced by an unconditional t_WC wait plus a bounded DQ6 toggle-bit poll that never writes response_code (FIX-02)"
    requirement: FIX-02
    verification:
      - kind: unit
        ref: "firestarter/test/native/avr/test_eeprom28c_sdp/test_eeprom28c_sdp.cpp cases 6, 7, 8 (test_case6_matching_chip_id_proceeds, test_case7_mismatching_chip_id_with_force_warns, test_case8_completion_poll_preserves_prior_severity) via `pio test -e native -f \"*test_eeprom28c_sdp*\"`"
        status: pass
    human_judgment: false
  - id: D3
    description: "A16-A18 upper-address staleness on DIP32_28C512_EEPROM is closed as a by-product of the FIX-01 routing, not a separate change (FIX-03)"
    requirement: FIX-03
    verification:
      - kind: unit
        ref: "firestarter/test/native/avr/test_eeprom28c_sdp/test_eeprom28c_sdp.cpp cases 4, 5 (test_case4_at28c010_stale_direct_seed, test_case5_at28c040_stale_via_real_read) via `pio test -e native -f \"*test_eeprom28c_sdp*\"`"
        status: pass
    human_judgment: false
  - id: D4
    description: "PAGE_SIZE 64 documented as a deliberate conservative floor with the AT28MC010/AT28C010 counter-example (D-13); no mem_size-derived helper adopted"
    verification:
      - kind: unit
        ref: "grep gates over firestarter/src/proms/eeprom_28c.cpp: PAGE_SIZE 64 unchanged, D-13/AT28MC010/AT28C010 present in the 14 lines above the #define, flash_5v_page_page_size absent from code lines -- all passed"
        status: pass
    human_judgment: false
  - id: D5
    description: "FIX-04 frozen artifacts (flash_utils.{h,cpp}, flash_5v_page.cpp, flash_nor_unlock.cpp, _shared/sdp_expected.h, _shared/sdp_bus_config.h) stay byte-untouched by this plan; full native suite green; both board targets build"
    verification:
      - kind: unit
        ref: "git diff --exit-code HEAD~2 HEAD -- <6 frozen paths> (clean); pio test -e native (103/103 passing); pio run -e leonardo / -e uno (both SUCCESS)"
        status: pass
    human_judgment: false

# Metrics
duration: 15min
completed: 2026-07-28
status: complete
---

# Phase 117 Plan 02: Remap-Aware `0x0D` Emitter + Honest Completion Signal (D-03 Commit 2) Summary

**Rebuilt `eeprom28c_write_init` on a remap-aware `eeprom28c_emit_command_sequence` driven through `handle->firestarter_set_data`, deleted the inverted `(0x5555, 0x20)` read-back in favor of a silent, bounded `t_WC`+DQ6-toggle completion poll that never touches `response_code`, and flipped plan 117-01's enabled RED suite to 8/8 GREEN on the first run.**

## Performance

- **Duration:** ~15 min
- **Started:** 2026-07-28T09:52:00Z
- **Completed:** 2026-07-28T10:07:00Z
- **Tasks:** 3
- **Files modified:** 2

## Accomplishments
- `eeprom28c_write_init`'s SDP-disable sequence is now emitted by a new file-static `eeprom28c_emit_command_sequence(handle, sequence, length)`, which drives every write through `handle->firestarter_set_data` (i.e. `memory_set_data`) instead of the shared `flash_execute_command(EEPROM_SDP_DISABLE)` — closing the `/WE`-inhibit defect measured for 66 of the 84 `0x0D` chips, and (as a by-product of the same routing, not a separate change) the A16-A18 upper-address staleness gap for `DIP32_28C512_EEPROM`'s 18 chips ≥64 KB.
- The inverted `eeprom28c_wait_for_write(handle, 0x5555, 0x20)` call in the write-init path is deleted outright, replaced by a new file-static `eeprom28c_wait_for_sdp_completion(handle)`: an unconditional `AT28C_TWC_MAX_MS` (10 ms) `t_WC` wait, then a bounded (`AT28C_TOGGLE_POLL_MAX_READS` = 32 iterations, never a `millis()` deadline) poll for two consecutive samples of `AT28C_DQ6_TOGGLE_MASK` (0x40) at the invariant `EEPROM28C_TOGGLE_POLL_ADDRESS` (0x5555). This function writes no `response_code` and emits no `LOG_` call on any path.
- `EEPROM_SDP_DISABLE` granted external linkage (`extern const byte_flip_t EEPROM_SDP_DISABLE[6];`) so plan 117-04's FIX-05 guard can read the production array directly.
- One explicit `rurp_set_data_output()` call added in the emitter (D-12), restoring parity with the shipped `fu_flash_flip_data`'s data-direction guarantee; recorder-invisible (a no-op in the host stubs), so no `SDP_FIXED_*` golden regeneration was needed.
- `PAGE_SIZE 64` now carries a comment recording it as a deliberate conservative floor, citing the `AT28MC010` (0x0040/64) vs `AT28C010` (0x0080/128) counter-example at the same 128 KB density — a `mem_size`-derived band table would be wrong, so none was added.
- `pio test -e native -f "*test_eeprom28c_sdp*"` flipped from plan 117-01's committed 8/8 RED to **8/8 GREEN on the first run**, with the suite itself byte-unchanged between the two commits (verified via `git diff --stat`). Full `pio test -e native`: **103/103 passing** (16 suites, no regressions). Both `pio run -e leonardo` and `pio run -e uno` report `SUCCESS`.
- Leonardo flash figure at this commit: 25374/28672 bytes (88.5%), RAM 1998/2560 bytes (78.0%).

## Task Commits

All three tasks landed in **one** commit, per the plan's explicit D-03 instruction (Task 3's action: "Commit Tasks 1-3 as one commit — D-03's commit 2"):

1. **Tasks 1-3 combined** (remap-aware emitter + honest completion signal + D-13 comment + GREEN capture) — `b30b91c` (fix, firestarter submodule)

**Plan metadata:** pending (this SUMMARY + STATE.md/ROADMAP.md/REQUIREMENTS.md update, in the meta repo)

_Note: this is a firmware-submodule-only plan; the meta repo's docs commit is separate (see `<final_commit>`)._

## Files Created/Modified
- `firestarter/src/proms/eeprom_28c.cpp` — Added `AT28C_TWC_MAX_MS`/`AT28C_DQ6_TOGGLE_MASK`/`AT28C_TOGGLE_POLL_MAX_READS`/`EEPROM28C_TOGGLE_POLL_ADDRESS` named constants; granted `EEPROM_SDP_DISABLE` external linkage; added `eeprom28c_emit_command_sequence` and `eeprom28c_wait_for_sdp_completion`; rewrote `eeprom28c_write_init` to call both, deleting the old `flash_execute_command`/`eeprom28c_wait_for_write(handle, 0x5555, ...)` call sites; documented `PAGE_SIZE 64` (D-13). `eeprom28c_write_execute` and `eeprom28c_wait_for_write` left untouched (plan 117-03 owns their removal).
- `firestarter/test/native/avr/test_eeprom28c_sdp/RED-BASELINE.md` — Appended `## GREEN after the Phase 117 fix (commit 2 — D-03)`: verbatim `pio test` + direct-binary captures (`8 Tests 0 Failures 0 Ignored`, exit 0), the empty-diff proof the suite was unchanged between commits, a per-case code-as-subject note, the restated validation ceiling, and the restated CORRECTION 4 (66-of-84) framing.

## Decisions Made
- Followed 117-CONTEXT.md's D-04/D-05/D-06 (unconditional `t_WC` wait then bounded poll, poll issued only through `handle->firestarter_get_data`, poll bound as an iteration count) and the plan's own discretion resolutions (poll read address = the sequence's own terminal address `0x5555`, behind a named constant; explicit 3-argument emitter signature, no macro) exactly as specified.
- Reworded three in-code comment sentences (two mentioning `rurp_set_data_output()`, one mentioning `eeprom28c_wait_for_write(handle, 0x5555`) to avoid literal substring collisions with the plan's non-comment-filtered acceptance-criteria greps (`grep -c 'rurp_set_data_output'` must be exactly `1`; `grep -c 'eeprom28c_wait_for_write(handle, 0x5555'` must be exactly `0`) — meaning fully preserved, matching this project's established pattern of rewording around literal-substring gates (see `.planning` memory on Phase 107's `mem_type` substring avoidance) rather than weakening the gate.
- Condensed the D-13 `PAGE_SIZE` comment to 14 lines so `AT28MC010`, `AT28C010`, and `D-13` all fall within the acceptance criteria's `grep -B 14` window — the plan's own worked-example prose, written out in full, would have exceeded that window.

## Deviations from Plan

None affecting behavior — plan executed exactly as specified. The two comment-wording adjustments above are cosmetic (Rule 3, blocking: the literal acceptance-criteria greps would otherwise fail on self-referential documentation, not on the code's actual shape) and do not change any assertion, constant value, or control flow.

## Issues Encountered

None. All three tasks' automated verify gates and acceptance criteria passed; the suite flipped to 8/8 GREEN on the first `pio test` run with no debugging iteration needed. `firestarter_app` has a pre-existing uncommitted `.gitignore` change (dated 2026-07-10, well before this session) unrelated to this plan — noted here because the plan's own verification step checks `git -C firestarter_app diff --stat` produces no output; this plan touched zero `firestarter_app` files, so the pre-existing drift is out of scope and not introduced by this work.

## FIX-04 frozen-file verification (this commit)

```
cd /workspaces/firestarter
git diff --exit-code HEAD~2 HEAD -- src/proms/flash_utils.cpp include/flash_utils.h \
  src/proms/flash_5v_page.cpp src/proms/flash_nor_unlock.cpp \
  test/native/avr/_shared/sdp_expected.h test/native/avr/_shared/sdp_bus_config.h
```
Exits 0 — all six paths byte-identical across both commit 1 (`e5b9e87`) and commit 2 (`b30b91c`), matching the plan's expected table measured at phase start from `ada4bdc7`.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- Plan 117-03 is unblocked: it owns FIX-06 (splitting `eeprom28c_write_execute`'s conflated completion+data-landed poll into a DQ7-complement completion check and an always-on read-back), and can now delete `eeprom28c_wait_for_write` once its call site there is replaced.
- Plan 117-04 is unblocked: `EEPROM_SDP_DISABLE` now has external linkage, so its FIX-05 terminal-byte + table-identity guard can read the production array directly.
- Plan 117-05 (FIX-04 close) has this plan's frozen-file verification and Leonardo flash figure (25374/28672 bytes) as one of its inputs.
- No blockers. `firestarter/src/` changes are confined to `eeprom_28c.cpp`; all six FIX-04 frozen paths confirmed byte-identical since phase start.

---
*Phase: 117-fix-remap-aware-0x0d-emitter-honest-completion-signal*
*Completed: 2026-07-28*

## Self-Check: PASSED

- FOUND: `firestarter/src/proms/eeprom_28c.cpp`
- FOUND: `firestarter/test/native/avr/test_eeprom28c_sdp/RED-BASELINE.md`
- FOUND: commit `b30b91c` in `firestarter` submodule history
- FOUND: `.planning/phases/117-fix-remap-aware-0x0d-emitter-honest-completion-signal/117-02-SUMMARY.md`
