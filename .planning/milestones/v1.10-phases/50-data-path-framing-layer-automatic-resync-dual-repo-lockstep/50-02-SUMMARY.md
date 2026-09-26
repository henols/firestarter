---
phase: 50-data-path-framing-layer-automatic-resync-dual-repo-lockstep
plan: 02
subsystem: firmware-serial-transport
tags: [cobs, crc8, serial, avr, arduino, framing, resync]

# Dependency graph
requires:
  - phase: 50-data-path-framing-layer-automatic-resync-dual-repo-lockstep/50-01
    provides: RED Unity test suite for COBS decode/resync + serial_read_mock.h queued-byte mock

provides:
  - streaming COBS decode-in-place in rurp_communication_read_data (removes 2 s timeout_ms loop)
  - streaming COBS encode in rurp_communication_write (removes len_u16 prefix + XOR checksum)
  - drain-to-0x00 bounded resync on any COBS/CRC failure
  - delimiter-driven case '#' precheck in operation_utils.cpp

affects:
  - 50-03 (host-side COBS encode + frame_parser.py cobs_encode/decode)
  - 50-04 (Uno RAM gate post-change)

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "COBS decode-in-place with 1-byte output lookahead (last_byte) — CRC byte never written to buffer"
    - "implicit_zero_pending deferred flag — commits zero only on next run-code, discards on 0x00 delimiter"
    - "drain-to-0x00 before error return — re-anchors RX cursor at frame boundary"
    - "COBS encode with source-buffer slices — writes directly from buffer[], no second copy"

key-files:
  created: []
  modified:
    - firestarter/src/boards/rurp_serial_utils.cpp
    - firestarter/src/operation_utils.cpp

key-decisions:
  - "1-byte output lookahead (last_byte) with implicit_zero_pending flag — avoids needing DATA_BUFFER_SIZE+1 bytes for a full-size payload"
  - "COBS encode writes sub-slices directly from source buffer via SERIAL_PORT.write(buf+run_start, run_len) — no second buffer"
  - "case '#' precheck changed from <4 to <=0 — only gate on available() > 0, let decoder accumulate to 0x00 delimiter"
  - "static _drain_to_delimiter() helper — avoids code duplication across multiple error paths"
  - "Forward declaration for crc8_ccitt — allows placing decode/encode before the PROGMEM table definition"

patterns-established:
  - "COBS decode-in-place with lookahead: when in doubt, trace the implicit-zero handling for the final run separately from mid-stream runs"
  - "Defer implicit-zero emission until next run-code arrival (not at run-code load time)"

requirements-completed: [FRAME-01, FRAME-02, FRAME-03, CRC-01]

# Metrics
duration: 50min
completed: 2026-06-01
---

# Phase 50 Plan 02: COBS GREEN Implementation Summary

**Streaming COBS decode-in-place with 1-byte lookahead + CRC8 verify + drain-to-0x00 resync turns the Wave-0 firmware suite GREEN and removes the 2 s timeout_ms cascade source**

## Performance

- **Duration:** ~50 min
- **Started:** 2026-06-01T16:52:00Z
- **Completed:** 2026-06-01T17:42:19Z
- **Tasks:** 2
- **Files modified:** 2 (firestarter submodule)

## Accomplishments

- `rurp_communication_read_data` rewritten: streaming COBS decode-in-place into `data_buffer` using 1-byte output lookahead (`last_byte`) and `implicit_zero_pending` deferred flag; CRC byte never written to buffer; drain-to-0x00 on any error
- `rurp_communication_write` rewritten: COBS streaming encoder that writes directly from source buffer slices to `SERIAL_PORT.write()`; CRC8 folded as (N+1)th payload byte; terminates with 0x00 + flush
- `operation_utils.cpp` `case '#'` precheck relaxed from `<4` (len-era) to `<=0` (delimiter-driven)
- All 3 Wave-0 firmware Unity cases GREEN: valid frame decode, bounded resync, all-zero 512 B round-trip
- Full native suite 28/28 GREEN; log/telemetry `test_rurp_log_id.cpp` untouched

## Task Commits

Each task was committed atomically inside the `firestarter` submodule on branch `v1.10-serial-transport-hardening`:

1. **Task 1: Rewrite rurp_communication_read_data** - `32fca0b` (feat)
2. **Task 2: Rewrite rurp_communication_write + case '#' precheck** - `fe91714` (feat)

## Files Created/Modified

- `firestarter/src/boards/rurp_serial_utils.cpp` — `rurp_communication_read_data` (COBS decode-in-place), `_drain_to_delimiter` helper, `rurp_communication_write` (COBS encode), forward decl for `crc8_ccitt`
- `firestarter/src/operation_utils.cpp` — `case '#'` precheck changed from `< 4` to `<= 0`

## Decisions Made

- **1-byte lookahead for CRC isolation**: A payload of exactly `DATA_BUFFER_SIZE` bytes needs DATA_BUFFER_SIZE+1 decoded bytes (payload + CRC). Holding the most-recently decoded byte in `last_byte` (1-byte lookahead) keeps `out ≤ DATA_BUFFER_SIZE` — the CRC is extracted from `last_byte` at frame end without ever writing it to `buffer[]`.
- **`implicit_zero_pending` flag**: The key algorithmic insight — implicit zeros from completed COBS runs are deferred (not immediately placed in `last_byte`) and only emitted when the next run-code arrives. When the 0x00 delimiter arrives, the pending zero is discarded (it's the trailing implicit zero COBS omits at stream end). This correctly handles the all-zero payload case where CRC=0.
- **Encoder uses source-buffer slices**: `SERIAL_PORT.write(buffer + run_start, run_len)` writes directly from the source `buffer` without any intermediate copy. The CRC byte is handled as a special 1-byte case after the payload loop.
- **No bounded safety timeout**: Removed the 2 s `timeout_ms` loop entirely (SC1 win). The `while (rurp_communication_available() <= 0) {}` spin in the decode loop is bounded by the op-level ACK timeout machinery in `op_wait_for_ack`, not by a per-byte timeout.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] COBS implicit-zero end-of-stream edge case — algorithm design required 3 iterations**

- **Found during:** Task 1
- **Issue:** Initial decode designs incorrectly placed implicit zeros in `last_byte` at run-code load time (before knowing whether the 0x00 delimiter would follow). This caused the all-zero 512 B payload to return out=3 instead of out=2 for a 3-zero test case, because the CRC byte's implicit zero was being committed to buffer prematurely.
- **Fix:** Introduced `implicit_zero_pending` flag: set when a non-254 run completes, committed only when the NEXT run-code arrives (not the delimiter). The delimiter discards it. This correctly models the COBS "no trailing zero at stream end" rule in a streaming decoder without pre-reading.
- **Files modified:** `firestarter/src/boards/rurp_serial_utils.cpp`
- **Verification:** `pio test -e native -f "*test_cobs_data_frame*"` GREEN on all 3 cases including all-zero 512 B
- **Committed in:** `32fca0b`

---

**Total deviations:** 1 auto-fixed (algorithmic correctness)
**Impact on plan:** Algorithm iteration within the single task; no scope creep. The final design is correct and matches the test contract exactly.

## Issues Encountered

- Forward declaration for `crc8_ccitt` was needed because the new decode/encode functions are placed before the PROGMEM table definition in the file. Added `static uint8_t crc8_ccitt(uint8_t crc, uint8_t b);` forward decl immediately before `_drain_to_delimiter`.

## Known Stubs

None — both functions are fully implemented with correct COBS encode/decode and CRC8 verify.

## Threat Flags

No new network endpoints, auth paths, or schema changes introduced. T-50-01 (buffer overflow guard via DATA_BUFFER_SIZE cap + -2 return) and T-50-02 (CRC8 verify before payload delivery) are fully implemented per the plan's threat register dispositions.

## Self-Check

Verifying claims before finalizing:

- `firestarter/src/boards/rurp_serial_utils.cpp` modified: confirmed (git log shows 32fca0b, fe91714)
- `firestarter/src/operation_utils.cpp` modified: confirmed (fe91714)
- `pio test -e native -f "*test_cobs_data_frame*"` GREEN: confirmed (3/3 passed)
- `pio test -e native` full suite GREEN: confirmed (28/28 passed)
- `grep -c 'timeout_ms = 2000' src/boards/rurp_serial_utils.cpp` = 0: confirmed
- `_firestarter_emit_frame`, `rurp_log_id_wide`, `MAGIC_PREAMBLE` unchanged: confirmed (git diff empty for those regions)
- CRC8 PROGMEM table byte-unchanged: confirmed (no diff on lines 221-239)

## Self-Check: PASSED

## Next Phase Readiness

- Phase 50 Plan 03 (host-side COBS encode in `frame_parser.py` + `eprom_operations.py`) can proceed; the firmware decoder is the inverse of the test's `build_cobs_frame_bytes` helper
- Phase 50 Plan 04 (Uno RAM gate) can now run `check_uno_ram.sh` against the updated firmware build to confirm < 545 B free
- The wire protocol is BREAKING: host and firmware must be updated together (D-03); mixed-version pairs will fail to communicate

---
*Phase: 50-data-path-framing-layer-automatic-resync-dual-repo-lockstep*
*Completed: 2026-06-01*
