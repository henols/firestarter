---
phase: 117-fix-remap-aware-0x0d-emitter-honest-completion-signal
plan: 01
subsystem: testing
tags: [platformio, unity, native-test, avr, sdp, at28c, eeprom28c]

# Dependency graph
requires:
  - phase: 116-ground-truth-trace-harness
    provides: the parked RED `test_eeprom28c_sdp` suite (`-I` entry only, no `test_filter`) + `RED-BASELINE.md`'s Phase-116 capture
provides:
  - "`test_eeprom28c_sdp` enabled in `[env:native]`'s `test_filter` (D-03 commit 1)"
  - "The suite's oracle rebuilt to encode the post-fix expectation: `set_data` un-mocked (D-01), five response-code assertions flipped to NOT_EQUAL + reordered, one new permanent severity-preservation case (D-02)"
  - "Verbatim 8/8-failing capture of the edited suite against the still-unfixed production tree, committed to `RED-BASELINE.md`"
affects: [117-02-fix-remap-aware-emitter, 117-05-close-frozen-artifact-proof]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Two-commit RED/GREEN discipline for an oracle edit that must precede a production fix (D-03): capture the edited-and-RED intermediate state before the fix lands, so neither commit alone could hide a hollow proof."
    - "Address-keyed mock toggle arm for a future toggle-bit poll (case 8's `s_poll_addr_toggles`): dispatch stays keyed on the read ADDRESS, with the toggle behavior derived from a per-address read counter, never from call order."

key-files:
  created: []
  modified:
    - firestarter/platformio.ini
    - firestarter/test/native/avr/test_eeprom28c_sdp/test_eeprom28c_sdp.cpp
    - firestarter/test/native/avr/test_eeprom28c_sdp/RED-BASELINE.md

key-decisions:
  - "Followed 117-CONTEXT.md D-01/D-02/D-03 exactly as locked: un-mocked set_data, flipped+reordered five response-code assertions, added case 8, captured the edited-and-RED intermediate before any production change."
  - "Cases 6-7's make_identity_handle factory needed a real bus_config once set_data stopped being a no-op; used SDP_BUS_CONFIGS[0] (AT28C256/DIP28_28C256) because its mem_size (32768) already matches the factory's own mem_size and derived mfr_addr (0x7FC0)."
  - "Case 8's toggle arm derives alternation from the existing s_reads_at_poll_addr counter (address-keyed, not call-order-keyed), per the mock's own established dispatch rule."
  - "Left the per-case top-of-function prose comments for cases 1-5 as-is (they accurately describe the current stream-divergence mechanism, which this plan does not change) — only the response-code assertions, case names, mock reassignments, and the suite/file header comments were rewritten, per the plan's explicit task scope."

requirements-completed: []  # Oracle half only (D-03 commit 1). FIX-01/FIX-02 close jointly with plan 117-02 per this plan's own "Requirement scoping" section — no checkbox ticked here.

coverage:
  - id: D1
    description: "native/avr/test_eeprom28c_sdp added to [env:native]'s test_filter allowlist; -I entry unduplicated; PARKED comment block replaced with the Phase-117 four-edit note"
    verification:
      - kind: unit
        ref: "firestarter/platformio.ini grep gates (test_filter count, -I count, TEST_IGNORE_MESSAGE presence, Post-suite-edit RED baseline heading reference) — all passed per Task 1 acceptance criteria"
        status: pass
    human_judgment: false
  - id: D2
    description: "D-01 un-mock: zero set_data no-op reassignments remain; mock_set_data_keyed deleted; cases 6-7 given a real bus_config"
    verification:
      - kind: unit
        ref: "grep -vE comment-lines mock_set_data_keyed count == 0; SDP_BUS_CONFIGS[0].bus_config count >= 1 in test_eeprom28c_sdp.cpp"
        status: pass
    human_judgment: false
  - id: D3
    description: "D-02: five response-code assertions flipped EQUAL->NOT_EQUAL and moved to end of case; new permanent case 8 added and registered"
    verification:
      - kind: unit
        ref: "TEST_ASSERT_NOT_EQUAL_MESSAGE(RESPONSE_CODE_ERROR count == 6; TEST_ASSERT_EQUAL_MESSAGE(RESPONSE_CODE_ERROR count == 0; RUN_TEST count == 8; test_case8_completion_poll_preserves_prior_severity count == 2 in test_eeprom28c_sdp.cpp"
        status: pass
    human_judgment: false
  - id: D4
    description: "Cases 1-3 renamed (no _shipped_stream_diverges_from_fixed identifier survives); suite header comment rewritten"
    verification:
      - kind: unit
        ref: "grep -c _shipped_stream_diverges_from_fixed test_eeprom28c_sdp.cpp == 0"
        status: pass
    human_judgment: false
  - id: D5
    description: "Suite compiles and runs 8 cases, all failing, against the still-unfixed production tree; verbatim capture committed to RED-BASELINE.md"
    verification:
      - kind: unit
        ref: ".pio/build/native/firestarter_native direct run: '8 Tests 8 Failures 0 Ignored', exit code 8 -- captured verbatim in RED-BASELINE.md's new section"
        status: pass
    human_judgment: false
  - id: D6
    description: "No production file changed (firestarter/src/ byte-untouched); FIX-04 frozen paths untouched; REQUIREMENTS.md unchanged"
    verification:
      - kind: unit
        ref: "git diff --name-only HEAD~1 HEAD -- src/ (empty); git diff --name-only HEAD~1 HEAD -- src/proms/flash_utils.cpp include/flash_utils.h src/proms/flash_5v_page.cpp src/proms/flash_nor_unlock.cpp (empty)"
        status: pass
    human_judgment: false

# Metrics
duration: 12min
completed: 2026-07-28
status: complete
---

# Phase 117 Plan 01: Enable + Rebuild the Parked 0x0D SDP Oracle (D-03 Commit 1) Summary

**Enabled Phase 116's parked `test_eeprom28c_sdp` suite in `[env:native]`, rebuilt it per D-01/D-02 to encode the post-fix expectation (un-mocked `set_data`, flipped five response-code assertions, added a permanent severity-preservation case), and captured its verbatim 8/8-failing output against the still-unfixed production tree into `RED-BASELINE.md`.**

## Performance

- **Duration:** ~12 min
- **Started:** 2026-07-28T09:38:00Z
- **Completed:** 2026-07-28T09:49:25Z
- **Tasks:** 3
- **Files modified:** 3

## Accomplishments
- `native/avr/test_eeprom28c_sdp` is now in `[env:native]`'s `test_filter` allowlist (previously compiled via `-I` only, never run by `pio test -e native`).
- The suite's oracle no longer contradicts FIX-01/FIX-02's target state: `firestarter_set_data` is left as the real `memory_set_data` everywhere (D-01), and the five `RESPONSE_CODE_ERROR`-must-equal assertions were flipped to `NOT_EQUAL` and reordered to the end of each case so the stream-equality evidence stays visible in a RED capture (D-02).
- New permanent regression case `test_case8_completion_poll_preserves_prior_severity` proves the completion poll can never destroy a prior `RESPONSE_CODE_WARNING`, even when the poll's mock is set (via `s_poll_addr_toggles`) to never settle.
- `RED-BASELINE.md` now carries a second, self-contained capture — "Post-suite-edit RED baseline (Phase 117 commit 1 — D-03)" — proving the *edited* suite (not just Phase 116's original) was genuinely RED before any production change landed.
- Verified `pio test -e native` (full run, all 16 suites): 104 cases, 95 pass, 8 fail — the 8 failures are exactly this suite's 8 cases; all 15 other suites remain green.

## Task Commits

All three tasks landed in **one** commit, per the plan's explicit D-03 instruction (Task 3's action: "Commit this plan's three files as **one** commit"):

1. **Tasks 1-3 combined** (enable suite + D-01/D-02 suite edits + RED-BASELINE.md capture) — `e5b9e87` (test)

**Plan metadata:** pending (this SUMMARY + STATE.md/ROADMAP.md update, in the meta repo)

_Note: this is a firmware-submodule-only plan; the meta repo's docs commit is separate (see `<final_commit>`)._

## Files Created/Modified
- `firestarter/platformio.ini` - Added `test_filter` line for `test_eeprom28c_sdp`; replaced the Phase-116 PARKED comment block with a Phase-117 ENABLED note describing the real four-edit mechanics.
- `firestarter/test/native/avr/test_eeprom28c_sdp/test_eeprom28c_sdp.cpp` - D-01 un-mock (4 sites) + `mock_set_data_keyed` deletion; `make_identity_handle` given a real `bus_config`; D-02 five assertions flipped + reordered; new case 8 + `s_poll_addr_toggles` state; cases 1-3 renamed; suite header rewritten.
- `firestarter/test/native/avr/test_eeprom28c_sdp/RED-BASELINE.md` - New "Post-suite-edit RED baseline (Phase 117 commit 1 — D-03)" section with the verbatim direct-binary capture, expected-count reasoning, and a per-case observed-RED-reason table keyed by the new case names; "What Phase 117 must do" and the first-divergence table's case-name cross-references updated.

## Decisions Made
- Un-mocked `firestarter_set_data` at all four sites (`drive_write_init`, `drive_write_init_after_real_read`, cases 6-7) rather than any partial approach — D-01 is explicit that FIX-01's emitter is built on exactly this pointer.
- Gave `make_identity_handle` a real `bus_config` from `SDP_BUS_CONFIGS[0]` (AT28C256/DIP28_28C256) rather than leaving it zero-initialized, because dropping the `set_data` no-op now routes cases 6-7 through the real `memory_set_data` / `mem_util_remap_address_bus` for the first time; row 0's `mem_size` (32768) already matches the factory's own `h.mem_size` and derived `mfr_addr` (0x7FC0), so no new inconsistency was introduced.
- Moved the five response-code assertions to the end of each case body (Unity aborts a case at first failure) so this plan's RED capture keeps showing the stream-divergence evidence, matching Phase 116's baseline text, rather than masking it behind an earlier response-code failure.
- Used the direct binary run (`.pio/build/native/firestarter_native`) as the authoritative capture, not `pio test`'s own harness output, because `pio test` reported `[ERRORED]`/`SIGFPE` after the 8 `FAIL` lines but before its own summary — the same documented non-zero-exit summary-reporting quirk `RED-BASELINE.md` already records for `[ERRORED]`/`SIGBUS`. The direct binary exits cleanly with exit code 8 and a plain `8 Tests 8 Failures 0 Ignored` summary.
- Ticked **no** requirement in `REQUIREMENTS.md` — per the plan's own "Requirement scoping" section, FIX-01/FIX-02 close jointly with plan 117-02, which is not yet landed.

## Deviations from Plan

None — plan executed exactly as written. All Task 1/2/3 acceptance criteria and automated verify gates passed on the first attempt; no auto-fixes, no blocking issues, no architectural questions.

## Issues Encountered

`pio test -e native -f "*test_eeprom28c_sdp*"` reported `[ERRORED]` with a `SIGFPE` after printing all eight cases' `FAIL` lines but before its own Unity summary line. This is the same documented class of quirk `RED-BASELINE.md`'s own procedure note already records for `[ERRORED]`/`SIGBUS` (`pio test`'s harness, not the test binary, mis-reports a suite that exits non-zero due to *expected* test failures) — the plan's Task 3 action anticipated exactly this and directed taking the authoritative capture from the built binary directly. Running `.pio/build/native/firestarter_native` directly produced a clean exit (code 8) with the plain Unity summary `8 Tests 8 Failures 0 Ignored`, which is what was committed to `RED-BASELINE.md`.

## FIX-04 frozen-file blob SHAs (pre-phase baseline)

Measured from `/workspaces/firestarter` at commit `e5b9e87` (this plan's commit), via:

```
for p in src/proms/flash_utils.cpp include/flash_utils.h src/proms/flash_5v_page.cpp src/proms/flash_nor_unlock.cpp test/native/avr/_shared/sdp_expected.h test/native/avr/_shared/sdp_bus_config.h; do printf "%s  %s\n" "$(git rev-parse HEAD:$p)" "$p"; done
```

| Blob SHA | Path |
|---|---|
| `8cc0d576600c454958f481f13bdd660737af7077` | `src/proms/flash_utils.cpp` |
| `75399319ff64f84317f81307126c24732e13f275` | `include/flash_utils.h` |
| `6507e32c4f0aa8eebf9c426c19bc1ef2a92e3914` | `src/proms/flash_5v_page.cpp` |
| `e2e36ac88e75fc89f206aff5082050b004d22a27` | `src/proms/flash_nor_unlock.cpp` |
| `b0566b80a360261cf825df5f23ecc05c7d0f885e` | `test/native/avr/_shared/sdp_expected.h` |
| `e0111e6452dcb1bd8f44c5d36f3f6a67b893f4ad` | `test/native/avr/_shared/sdp_bus_config.h` |

All six match the plan's expected table (measured at phase start from commit `ada4bdc7`) byte-for-byte — confirmed this plan's production-file-frozen constraint holds, and the phase base is what the plan was written against.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- Plan 117-02 is unblocked: it must land the production fix (`eeprom28c_emit_command_sequence` on `handle->firestarter_set_data`, the `t_WC` wait + bounded DQ6 poll replacing the inverted `(0x5555,0x20)` check) as **commit 2**, then re-run `pio test -e native -f "*test_eeprom28c_sdp*"` and append the GREEN capture to this same `RED-BASELINE.md` file.
- No blockers. `firestarter/src/` is confirmed byte-untouched by this plan; all FIX-04 frozen paths (both production files and the two `_shared/` golden headers) are confirmed byte-identical to the phase-start baseline.

---
*Phase: 117-fix-remap-aware-0x0d-emitter-honest-completion-signal*
*Completed: 2026-07-28*

## Self-Check: PASSED

- FOUND: `firestarter/platformio.ini`
- FOUND: `firestarter/test/native/avr/test_eeprom28c_sdp/test_eeprom28c_sdp.cpp`
- FOUND: `firestarter/test/native/avr/test_eeprom28c_sdp/RED-BASELINE.md`
- FOUND: commit `e5b9e87` in `firestarter` submodule history
- FOUND: `.planning/phases/117-fix-remap-aware-0x0d-emitter-honest-completion-signal/117-01-SUMMARY.md`
