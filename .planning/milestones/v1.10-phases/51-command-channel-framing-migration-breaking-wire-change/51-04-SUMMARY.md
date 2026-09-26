---
phase: 51-command-channel-framing-migration-breaking-wire-change
plan: 04
subsystem: firmware
tags: [cobs, crc8, serial, arduino, unity, tdd, memory-safety, dos-hardening]

# Dependency graph
requires:
  - phase: 51-command-channel-framing-migration-breaking-wire-change
    provides: "COBS+CRC8 command decode (51-01), host framing (51-02), docs (51-03)"

provides:
  - "CR-01 closed: PUSH overflow cap lowered to DATA_BUFFER_SIZE-1; NUL-terminate write in firestarter.cpp provably in-bounds for all legal payloads"
  - "CR-02 closed: both _drain_to_delimiter and main decode loop spin sites replaced with millis()-based bounded inter-byte deadline; truncated frames return negative instead of hanging until physical reset"
  - "Three new Unity cases pinning both defects: test_cobs_exact_buffer_size_payload, test_cobs_max_accepted_payload, test_cobs_truncated_frame_no_hang"
  - "Suite-local serial_read_mock.h for test_cobs_cmd_frame with documented finite-stream semantics"
  - "test_cobs_data_frame updated to use DATA_BUFFER_SIZE-1 boundary (Rule 1 auto-fix)"
  - "D-06 reconciliation written: bounded mid-frame guard honors D-06 intent (no idle timer), refines its letter"

affects:
  - phase-52-lockstep-contract
  - phase-53-bench-verification
  - v1.9-read-bug-rca

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Decoder-cap invariant: PUSH guard at DATA_BUFFER_SIZE-1 guarantees n <= DATA_BUFFER_SIZE-1, making caller NUL write always in-bounds by construction"
    - "Bounded mid-frame inter-byte deadline: millis()-based timeout armed only after first byte consumed; no idle timer on truly-idle path"
    - "Suite-local mock: explicit local copy of serial_read_mock.h prevents cross-suite -I path ambiguity"

key-files:
  created:
    - firestarter/test/native/avr/test_cobs_cmd_frame/serial_read_mock.h
  modified:
    - firestarter/src/boards/rurp_serial_utils.cpp
    - firestarter/src/firestarter.cpp
    - firestarter/test/native/avr/test_cobs_cmd_frame/test_cobs_cmd_frame.cpp
    - firestarter/test/native/avr/test_cobs_data_frame/test_cobs_data_frame.cpp

key-decisions:
  - "CR-01: decoder-cap fix (PUSH guard to DATA_BUFFER_SIZE-1) chosen over call-site-only guard; makes the invariant hold at the single source of truth (the decoder) unconditionally"
  - "CR-01: belt-and-suspenders guard added in firestarter.cpp (if n < DATA_BUFFER_SIZE) to document the invariant at the write site; costs nothing and protects future callers"
  - "CR-01: CMD_FRAME_MAX unchanged in firestarter.h; constants.py untouched; decoder cap is an internal invariant, not a public wire constant; no parity mirror needed"
  - "CR-02: bounded inter-byte deadline (approach B) chosen over full resumable decoder (approach A); approach A is a large state-machine rewrite with higher regression risk; approach B is the minimal correct fix"
  - "CR-02: TIMEOUT_MS (1000 ms) reused; no new constant defined; no parity mirror needed (firmware-internal timing, not a wire constant)"
  - "D-06 reconciliation: bounded mid-frame guard honors D-06 intent (no reintroduced idle wall-clock timer; SC1 win preserved) while consciously refining D-06's letter (size-cap-only mechanism was insufficient for host-silence failure mode; operator explicitly delegated this call to the planner)"
  - "Rule 1 auto-fix: test_cobs_data_frame/test_cobs_all_zero_payload updated from 512 to 511 bytes; the 512-byte DATA_BUFFER_SIZE payload never passes through rurp_communication_read_data in production (data-block path uses MSG_DATA_CHUNK magic-preamble frames per ADR §4.2)"

patterns-established:
  - "TDD RED→GREEN: RED cases committed first (two failing cases + one hang-demonstrating case), then GREEN source fix committed; RUN_TEST order: original 4 then 3 new"
  - "Finite-stream mock: existing setup_serial_read_mock available()-returns-0 / read()-returns--1-after-exhaustion semantics are sufficient for truncated-frame tests; no new mock variant needed"

requirements-completed: [FRAME-05, CRC-01]

# Metrics
duration: 25min
completed: 2026-06-02
---

# Phase 51 Plan 04: Gap-Closure — CR-01 OOB Write + CR-02 Truncated-Frame Hang Summary

**Decoder-cap lowered to DATA_BUFFER_SIZE-1 (CR-01 OOB write closed) and both spin sites bounded with millis()-based inter-byte deadline (CR-02 hang closed); 7/7 Unity cases green; SC1 win and D-06 intent preserved.**

## Performance

- **Duration:** ~25 min
- **Started:** 2026-06-02T10:15Z (approx)
- **Completed:** 2026-06-02T10:40Z (approx)
- **Tasks:** 2 (TDD RED + GREEN)
- **Files modified:** 5 (4 modified + 1 created)

## Accomplishments

- Closed CR-01: changed PUSH overflow guard from `out >= DATA_BUFFER_SIZE` to `out >= DATA_BUFFER_SIZE - 1`, reserving the NUL-terminator slot. A 512-byte payload now takes the overflow/drain path (returns -2). The caller's `data_buffer[n] = '\0'` is in-bounds for every legal payload (n <= 511 always). Added belt-and-suspenders guard at the write site in firestarter.cpp.
- Closed CR-02: replaced both bare `while (rurp_communication_available() <= 0) {}` spins in `_drain_to_delimiter()` and the main decode loop with `millis()`-based bounded inter-byte deadlines. A truncated command frame (host silence mid-frame) now returns a negative value instead of hanging until physical reset.
- Three new Unity cases: `test_cobs_exact_buffer_size_payload` (512-byte payload must return <0), `test_cobs_max_accepted_payload` (511-byte payload round-trips correctly), `test_cobs_truncated_frame_no_hang` (truncated frame must return bounded). Suite-local `serial_read_mock.h` created with finite-stream semantics documented.
- Full native regression: 36/36 PASSED (`pio test -e native`). CMD_FRAME_MAX and constants.py untouched.

## D-06 Reconciliation

D-06 (CONTEXT.md) stated two clauses:

1. CMD_IDLE ingest accumulates bytes "non-blocking" across loop iterations.
2. "No new idle wall-clock timer" — stalled partial frame handled by the size cap, not a timeout.

The shipped implementation honored neither fully: it was a blocking spin (violates clause 1's "non-blocking" letter), and D-06's "size cap" only fires when bytes keep arriving — it does NOT cover host silence mid-frame (the CR-02 hole).

**Why the chosen fix (bounded inter-byte deadline) honors D-06's INTENT while consciously refining its letter:**

D-06's "no new idle wall-clock timer" targeted the pre-Phase-50 2-second idle timeout-cascade desync (the SC1 win). The concern is about the truly-idle path: a programmer sitting at CMD_IDLE with NO frame in progress must not arm a wall-clock timer that fires on normal idle and cascades into desync.

The CR-02 fix preserves that exactly:
- The deadline is armed ONLY when a frame is already in progress (decoding is underway, first byte consumed). The truly-idle path is unaffected: `loop()` still gates decoder entry on `rurp_communication_available() > 0`.
- This is a MID-FRAME INTER-BYTE guard, not an idle wall-clock timeout. The 2-second idle cascade D-06 forbade does not return.
- Approach A (full resumable decoder) would be the maximal interpretation of D-06's "non-blocking" clause, but is a large state-machine rewrite (checkpoint `out`, `block_remaining`, `last_byte`, `has_last`, etc. across `loop()` iterations) — high regression risk for a hardware-safety patch. Approach B is the minimal correct fix. The operator delegated this call to the planner.

**Conclusion:** Approach B refines D-06's letter (adds a bounded mid-frame deadline D-06 did not name) while fully honoring D-06's intent (no reintroduced idle wall-clock timeout; SC1 win preserved; bounded recovery from host silence).

## Task Commits

Each task was committed atomically in the `firestarter/` submodule on branch `v1.10-serial-transport-hardening`:

1. **Task 1: RED — finite-stream mock + 3 new Unity cases** - `6c3c392` (test)
2. **Task 2: GREEN — CR-01 decoder cap + CR-02 bounded waits + call-site guard** - `c523f49` (feat)

## Files Created/Modified

- `/workspaces/firestarter/test/native/avr/test_cobs_cmd_frame/serial_read_mock.h` — Suite-local ArduinoFake Serial mock with finite-stream semantics (available()=0, read()=-1 after exhaustion); documents why no separate finite-mode wrapper is needed
- `/workspaces/firestarter/test/native/avr/test_cobs_cmd_frame/test_cobs_cmd_frame.cpp` — Added 3 new Unity cases (boundary, max-accepted, truncated-no-hang) and registered them in main(); existing 4 cases unchanged
- `/workspaces/firestarter/src/boards/rurp_serial_utils.cpp` — PUSH guard lowered to DATA_BUFFER_SIZE-1 (CR-01); both spin sites replaced with millis()-bounded inter-byte deadlines (CR-02); updated comments
- `/workspaces/firestarter/src/firestarter.cpp` — Belt-and-suspenders guard `if (n < DATA_BUFFER_SIZE)` before NUL write (CR-01 call-site documentation)
- `/workspaces/firestarter/test/native/avr/test_cobs_data_frame/test_cobs_data_frame.cpp` — test_cobs_all_zero_payload updated from 512 to 511 bytes (Rule 1 auto-fix, see Deviations)

## Decisions Made

- CR-01 decoder-cap fix chosen (not call-site-only guard): makes the invariant `n <= DATA_BUFFER_SIZE-1` hold unconditionally at the single source of truth; future callers cannot reintroduce the OOB write by forgetting the guard.
- CMD_FRAME_MAX stays at `DATA_BUFFER_SIZE` (512) in `firestarter.h` and `constants.py` — the decoder cap is an INTERNAL invariant (`DATA_BUFFER_SIZE - 1`), not a public wire constant; no parity mirror needed; no `constants.py` edit.
- CR-02 approach B (bounded inter-byte deadline, TIMEOUT_MS reused) chosen over approach A (resumable cross-loop decoder): minimal correct fix, no new constant, low regression risk.
- D-06 reconciliation written into plan and SUMMARY explicitly — deviation from D-06's letter is deliberate and reasoned, not an oversight.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Updated test_cobs_all_zero_payload to use DATA_BUFFER_SIZE-1 bytes**

- **Found during:** Task 2 (GREEN — full native regression run)
- **Issue:** `test_cobs_data_frame/test_cobs_all_zero_payload` fed a 512-byte all-zero payload to `rurp_communication_read_data()` and expected success (`>= 0`). After the CR-01 PUSH guard change (lowered cap to `DATA_BUFFER_SIZE - 1 = 511`), a 512-byte payload now overflows and returns -2, causing the test to FAIL.
- **Fix:** Updated the test to use `DATA_BUFFER_SIZE - 1 = 511` bytes. Added comment explaining: `rurp_communication_read_data()` is the HOST→FW command decoder; the fw→host data-block path uses MSG_DATA_CHUNK magic-preamble frames (ADR §4.2, unchanged in v1.10) and never passes a 512-byte payload through this function in production. Largest legitimate JSON command is ~422 B, well under the 511-byte cap.
- **Files modified:** `firestarter/test/native/avr/test_cobs_data_frame/test_cobs_data_frame.cpp`
- **Verification:** Full native suite `pio test -e native` exits 0, 36/36 PASSED
- **Committed in:** `c523f49` (Task 2 GREEN commit)

---

**Total deviations:** 1 auto-fixed (Rule 1 — existing test broken by correct source fix)
**Impact on plan:** Auto-fix necessary for correctness. No scope creep. The 512-byte DATA_BUFFER_SIZE payload is not a production use case for `rurp_communication_read_data()` (command-frame decoder); the max accepted payload of 511 bytes is sufficient for all legitimate JSON commands (~422 B max per CONTEXT.md).

## Issues Encountered

- The `test_cobs_truncated_frame_no_hang` case was not run before Task 2 to avoid hanging the test harness on the bare spin-wait. The RED state was demonstrated by analysis of the source (confirmed bare spin-wait at lines 92 and 125) and the fact that compilation succeeded but execution would hang on queue exhaustion with the current source. The GREEN state was demonstrated by the test passing after Task 2.

## Threat Surface Scan

No new network endpoints, auth paths, file access patterns, or schema changes introduced. The changes harden existing COBS decode paths (firmware-internal). T-51-01 and T-51-02 are now mitigated per the plan's threat register.

## Known Stubs

None — all changes are functional (source hardening + test pinning). No placeholder values, mock data flows, or TODO wiring left in modified files.

## Self-Check

- [x] firestarter/src/boards/rurp_serial_utils.cpp modified with CR-01 + CR-02 fixes
- [x] firestarter/src/firestarter.cpp modified with belt-and-suspenders guard
- [x] firestarter/test/native/avr/test_cobs_cmd_frame/test_cobs_cmd_frame.cpp — 3 new cases + registered
- [x] firestarter/test/native/avr/test_cobs_cmd_frame/serial_read_mock.h — created
- [x] firestarter/test/native/avr/test_cobs_data_frame/test_cobs_data_frame.cpp — updated
- [x] `grep -n "DATA_BUFFER_SIZE - 1" firestarter/src/boards/rurp_serial_utils.cpp` matches PUSH guard
- [x] `grep -n "millis()" firestarter/src/boards/rurp_serial_utils.cpp` matches 4 lines (2 start= assignments, 2 comparisons)
- [x] No bare `while (rurp_communication_available() <= 0) {}` remains in rurp_serial_utils.cpp
- [x] CMD_FRAME_MAX unchanged in firestarter.h; constants.py untouched
- [x] `pio test -e native -f "native/avr/test_cobs_cmd_frame"` exits 0 — 7 cases passed
- [x] `pio test -e native` exits 0 — 36 cases passed
- [x] Commits: 6c3c392 (RED), c523f49 (GREEN) on branch v1.10-serial-transport-hardening

## Self-Check: PASSED

## Next Phase Readiness

- CR-01 and CR-02 are closed; FRAME-05 and CRC-01 requirements fully satisfied including the firmware memory-safety and DoS-on-stall dimensions.
- Phase 51 is now complete (all 4 plans: decode+CRC8, host framing, docs, gap-closure).
- Phase 52 (Lockstep Contract + Round-Trip Tests) can proceed: the command decode primitive is hardened and its behavioral contract is fully pinned by 7 Unity cases.

---
*Phase: 51-command-channel-framing-migration-breaking-wire-change*
*Completed: 2026-06-02*
