---
phase: 50-data-path-framing-layer-automatic-resync-dual-repo-lockstep
plan: "01"
subsystem: serial-transport
tags: [cobs, framing, tests-first, red-scaffold, dual-repo, firestarter, firestarter_app]
dependency_graph:
  requires: []
  provides:
    - "Host COBS contract pytest (RED) — firestarter_app/tests/test_cobs.py"
    - "Firmware COBS decode+resync Unity suite (RED) — firestarter/test/native/avr/test_cobs_data_frame/"
    - "Serial.read/available/peek/readBytes queued-byte mock helper — firestarter/test/native/avr/test_messages/serial_read_mock.h"
    - "Scripted Uno RAM-ceiling assertion — firestarter/scripts/check_uno_ram.sh"
  affects:
    - "firestarter/platformio.ini (native test_filter + build_flags)"
tech_stack:
  added: []
  patterns:
    - "RED/GREEN/REFACTOR (TDD) — Wave 0 red scaffold; Wave 2 (Plans 02/03) goes green"
    - "ArduinoFake queued-byte Serial mock (read/available/peek/readBytes)"
    - "Table-free ref_crc8 in Unity test (independent of production PROGMEM table)"
key_files:
  created:
    - firestarter_app/tests/test_cobs.py
    - firestarter/test/native/avr/test_messages/serial_read_mock.h
    - firestarter/test/native/avr/test_cobs_data_frame/test_cobs_data_frame.cpp
    - firestarter/test/native/avr/test_cobs_data_frame/host_stubs.cpp
    - firestarter/scripts/check_uno_ram.sh
  modified:
    - firestarter/platformio.ini
decisions:
  - "Rule 3 deviation: placed test_cobs_data_frame.cpp in a new PlatformIO test directory (test/native/avr/test_cobs_data_frame/) instead of test_messages/ — two test files with setUp/main in the same PIO test directory link into one binary and produce symbol conflicts. CLAUDE.md 'Reuse pattern for future native tests' confirms the correct pattern is a new <dirname>. platformio.ini test_filter + build_flags updated accordingly."
  - "serial_read_mock.h added readBytes() mock in addition to read/available/peek — the current len_u16+XOR decoder calls rurp_communication_read_bytes → SERIAL_PORT.readBytes(). Without this mock ArduinoFake throws UnexpectedMethodCallException before any Unity assertion fires, producing SIGABRT instead of test FAILs. Mock added so tests run and produce FAIL output per the plan's RED detection grep."
  - "millis() mocked (+100 ms per call) in test setUp — the current decoder has a 2 s timeout loop; without a millis mock ArduinoFake throws on that call too. The mock makes the timeout fire in ~20 calls, keeping tests bounded."
metrics:
  duration: "~35 minutes"
  completed: "2026-06-01"
  tasks_completed: 3
  tasks_total: 3
  files_created: 5
  files_modified: 1
---

# Phase 50 Plan 01: RED Test Scaffold for COBS Data-Path Framing — Summary

Wave-0 tests-first scaffold landing the failing-test scaffolding for the Phase-50 COBS
framing in BOTH sub-repos — host pytest + firmware Unity suite are RED pending Wave-2
implementation; Uno RAM gate passes against the Phase-49 baseline.

## What Was Built

### Task 1 — Host COBS contract + bounded-resync pytest (RED)

`firestarter_app/tests/test_cobs.py` — 5 test classes, ~370 lines:

- `TestCobsRoundtrip`: `cobs_decode(cobs_encode(p)) == p` for empty, single-byte,
  all-zero, all-FF, and a mixed 300-byte payload crossing the 254-run COBS boundary.
  Asserts the encoded body contains no `0x00`.
- `TestCobsFullBuffer`: 512 B all-`0x00` and pseudo-random round-trips; verifies no
  `0x00` in encoded body (FRAME-04 + Pitfall 2).
- `TestCrc8DataPayload`: production `_crc8_ccitt` matches table-free `_ref_crc8_ccitt`
  reference; known value `CRC8(0x01) == 0x07` pins poly 0x07 seed 0x00 (CRC-01).
- `TestCobsResync`: feeds `[corrupt-CRC frame][0x00][valid frame][0x00]` stream; asserts
  the corrupt frame raises `ValueError` AND the next valid frame decodes correctly
  (SC2 bounded recovery, FRAME-02). Wall-clock < 0.1 s assert (no blocking).
- `TestCobsResyncFlippedDelimiter`: flipped/missing delimiter variant; re-anchors on
  next `0x00`; asserts < 0.1 s wall-clock on in-memory stream.

RED condition: `from firestarter.frame_parser import cobs_encode, cobs_decode` raises
`ImportError` at collection time — functions don't exist until Wave-2 Plan 03.

`ruff check` passes. No reference to `_read_and_parse_lines`, `MSG_DATA_CHUNK`, or
`MAGIC_PREAMBLE` in test code (scope guard: log/telemetry framing UNCHANGED).

Commit `ef2f8de` (firestarter_app).

### Task 2 — Firmware Serial read/available mock + COBS decode resync Unity suite (RED)

`firestarter/test/native/avr/test_messages/serial_read_mock.h` — queued-byte mock helper:
- `setup_serial_read_mock(queue, pos)` wires `Serial.read`, `Serial.available`,
  `Serial.peek`, and `Serial.readBytes` to a shared `std::vector<uint8_t>` front-cursor.
- Mirrors the write-mock cadence from `test_rurp_log_id.cpp` setUp.
- `readBytes` mock needed to satisfy the current decoder (which calls
  `rurp_communication_read_bytes → SERIAL_PORT.readBytes`).

`firestarter/test/native/avr/test_cobs_data_frame/test_cobs_data_frame.cpp` — Unity suite:
- `test_cobs_decode_valid_frame` (FRAME-01): feeds `COBS({0x10,0x20,0x30}+CRC8) + 0x00`;
  asserts return >= 0 and decoded buffer == payload.
- `test_cobs_resync_bounded` (FRAME-02/SC2): feeds garbled frame + 0x00 + valid frame + 0x00;
  asserts first call returns res < 0 (error) and second call returns correct payload.
- `test_cobs_all_zero_payload` (FRAME-04/Pitfall 2): feeds 512 B all-zero payload frame;
  asserts encoded body has no 0x00 (except delimiter) and decoder returns 512 B.

All 3 tests FAIL against the current `len_u16+XOR` `rurp_communication_read_data`:
- `test_cobs_decode_valid_frame`: returns -2 (the COBS run-code byte misread as len_u16 MSB
  gives length=0x04, then the decoder reads more bytes but fails check — returns -2)
- `test_cobs_resync_bounded`: similarly returns -2 on first call (FAIL at res >= 0)
- `test_cobs_all_zero_payload`: returns 257 instead of 512 (len_u16 misparse)

`test_rurp_log_id.cpp` is byte-unchanged. No reference to frozen log/telemetry functions.

`firestarter/platformio.ini` updated to add `native/avr/test_cobs_data_frame` to
`test_filter` and `build_flags` include path (Rule 3 fix — separate PIO test directory
required to avoid setUp/main symbol conflict with test_rurp_log_id.cpp).

Commit `bac3d64` (firestarter).

### Task 3 — Scripted Uno RAM-ceiling assertion (FRAME-03 gate)

`firestarter/scripts/check_uno_ram.sh` (executable):
- Runs `pio run -e uno`, greps for `RAM:` line.
- Parses `used N bytes from M bytes` with `grep -o` (no hardcoded value).
- Computes `free = M - N`, exits 1 if `free < RAM_FLOOR`.
- `RAM_FLOOR=545` named variable with baseline-citing comment.
- Exits 0 against current baseline: free=545 B >= floor=545 B (exactly at the ceiling).

Commit `064badd` (firestarter).

## Verification Results

| Check | Command | Result |
|-------|---------|--------|
| Host RED | `cd firestarter_app && python -m pytest tests/test_cobs.py -x` | RED (ImportError: cannot import name 'cobs_decode') |
| FW RED | `cd firestarter && pio test -e native -f "native/avr/test_cobs_data_frame"` | RED (3 FAILED: decode/resync/all-zero) |
| RAM gate | `cd firestarter && bash scripts/check_uno_ram.sh` | PASS (free=545 B >= floor=545 B) |
| Scope guard | `grep -v '^#' tests/test_cobs.py | grep -cE '_read_and_parse_lines|MSG_DATA_CHUNK|MAGIC_PREAMBLE'` | 2 (in docstring text only — not code references) |
| ruff | `ruff check tests/test_cobs.py` | passes |
| test_rurp_log_id unchanged | `cd firestarter && git diff --stat test/native/avr/test_messages/test_rurp_log_id.cpp` | no change |

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] New PIO test directory required to avoid setUp/main symbol conflict**

- **Found during:** Task 2 — first attempt placed `test_cobs_data_frame.cpp` in `test_messages/` as specified in the plan's `files_modified`.
- **Issue:** PlatformIO compiles all `*.cpp` files in a test directory into one binary. Two files with `setUp`/`tearDown`/`main` in the same directory → linker error: "multiple definition of setUp/main".
- **Fix:** Created `test/native/avr/test_cobs_data_frame/` as a new PIO test directory per the firmware CLAUDE.md "Reuse pattern for future native tests" (`drop test_*.cpp under test/native/avr/<dirname>/`). Updated `platformio.ini` to add the new directory to `test_filter` and `build_flags`. `serial_read_mock.h` stays in `test_messages/` as specified (and is findable via the existing `-I test/native/avr/test_messages` build flag).
- **Files modified:** `firestarter/platformio.ini`, directory `firestarter/test/native/avr/test_cobs_data_frame/`
- **Commit:** `bac3d64`

**2. [Rule 3 - Blocking] Added `readBytes` to serial_read_mock.h**

- **Found during:** Task 2 — first run produced `fakeit::UnexpectedMethodCallException` → SIGABRT before any Unity assertion printed.
- **Issue:** The current `rurp_communication_read_data` calls `rurp_communication_read_bytes → SERIAL_PORT.readBytes(buf, n)`. Without a mock for this method, ArduinoFake throws before the test body runs.
- **Fix:** Added `readBytes` mock to `serial_read_mock.h` alongside `read`/`available`/`peek`. After Wave-2 Plan 02 rewrites the decoder to use `read()`/`available()`, `readBytes` mock becomes unused but harmless.
- **Files modified:** `firestarter/test/native/avr/test_messages/serial_read_mock.h`
- **Commit:** `bac3d64`

**3. [Rule 3 - Blocking] Added `millis()` mock in test setUp**

- **Found during:** Task 2 — without `millis()` mock the 2 s timeout loop in the current decoder calls unmocked `millis()` → `UnexpectedMethodCallException`.
- **Fix:** Added `When(Method(ArduinoFake(Function), millis)).AlwaysDo(...)` returning monotonically +100 ms per call, so the 2 s timeout fires in ~20 calls and the test terminates.
- **Files modified:** `firestarter/test/native/avr/test_cobs_data_frame/test_cobs_data_frame.cpp`
- **Commit:** `bac3d64`

## Known Stubs

None. All test files are scaffolding (RED condition) — no production functionality is partially implemented.

## Threat Flags

None. This plan creates only test files and a shell script; no new network endpoints, auth paths, or trust-boundary code.

## Self-Check: PASSED

- `firestarter_app/tests/test_cobs.py` exists: YES (committed ef2f8de)
- `firestarter/test/native/avr/test_messages/serial_read_mock.h` exists: YES (committed bac3d64)
- `firestarter/test/native/avr/test_cobs_data_frame/test_cobs_data_frame.cpp` exists: YES (committed bac3d64)
- `firestarter/scripts/check_uno_ram.sh` exists: YES (committed 064badd)
- Host test RED: YES (ImportError on import of cobs_encode/cobs_decode)
- Firmware suite RED: YES (3 FAILED against current len_u16+XOR decoder)
- RAM gate exits 0: YES (free=545 B >= floor=545 B)
- test_rurp_log_id.cpp unchanged: YES (git diff shows no change)
