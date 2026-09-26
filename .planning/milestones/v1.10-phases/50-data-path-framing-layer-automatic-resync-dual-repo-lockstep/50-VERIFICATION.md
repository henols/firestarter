---
phase: 50-data-path-framing-layer-automatic-resync-dual-repo-lockstep
verified: 2026-06-01T21:00:00Z
status: passed
score: 4/4 roadmap success criteria verified
overrides_applied: 0
---

# Phase 50: Data-Path Framing Layer + Auto-Resync Verification Report

**Phase Goal:** The host-firmware data-block path uses the Phase-49 framing layer end to end — full board-buffer payloads (512 B Uno / 1024 B Leonardo) frame transparently, the firmware encoder/decoder streams with no second encode buffer (proven by a post-change Uno RAM report), CRC8 is retained on every framed payload, and the receiver automatically resyncs to the next delimiter after any framing or integrity error — eliminating the 2 s `len_u16`-corruption timeout-desync cascade.
**Verified:** 2026-06-01T21:00:00Z
**Status:** passed
**Re-verification:** No — initial verification

---

## Goal Achievement

### Observable Truths (Roadmap Success Criteria)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | The bare `[len_u16][xor][payload]` boundary is replaced by delimiter-based framing on both directions; a corrupted byte no longer cascades to the 2 s timeout | VERIFIED | `grep -c 'timeout_ms = 2000' rurp_serial_utils.cpp` = 0; `grep -c 'size >> 8' rurp_serial_utils.cpp` = 0 (len_u16 gone); `grep -c 'to_bytes(2, "big")' eprom_operations.py` = 0; `grep -c 'operator.xor' eprom_operations.py` = 0; COBS decode drives to `0x00` delimiter |
| 2 | After a deliberately injected framing/integrity error, the receiver discards bytes up to the next delimiter and recovers within a single packet — bounded to one frame | VERIFIED | `test_cobs_resync_bounded` (firmware Unity) PASSED; `test_cobs_resync` (host pytest) PASSED; firmware `_drain_to_delimiter()` confirmed at lines 88-98 of `rurp_serial_utils.cpp`; firmware full suite 29/29 including `test_cobs_data_frame` |
| 3 | Post-change Uno RAM report shows streaming (no second ~512 B buffer), under ~545 B free-RAM ceiling; 512 B and 1024 B payloads frame without re-chunking | VERIFIED | `bash firestarter/scripts/check_uno_ram.sh` exits 0 — free=545 B >= floor=545 B (RAM unchanged from baseline); `50-RAM-REPORT.md` documents 0 B delta; COBS state is ~6 B stack-local; 512 B and 1024 B paths both validated by parameterized COBS round-trip tests |
| 4 | CRC8-CCITT (poly 0x07, seed 0x00, no reflection, no final XOR) computed and verified on every framed data-block payload; no polynomial swap | VERIFIED | `grep -c 'crc8_ccitt' rurp_serial_utils.cpp` = 10 (PROGMEM table unchanged, 10 uses); `_CRC8_CCITT_TABLE` in `frame_parser.py` defined by existing `_build_crc8_table()`; `grep -cE 'def _.*crc|CRC.*TABLE' frame_parser.py` = 4 (unchanged count); `test_crc_polynomial_smoke` (firmware) + `test_crc8_data_payload` (host) both PASSED |

**Score:** 4/4 truths verified

---

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|---------|--------|---------|
| `firestarter/src/boards/rurp_serial_utils.cpp` | Streaming COBS encode/decode + CRC8 + drain-to-0x00 resync | VERIFIED | COBS read/write functions present (lines 44-276); no timeout_ms=2000; no len_u16; `_drain_to_delimiter` at lines 88-98; CRC8 PROGMEM table unchanged |
| `firestarter/src/operation_utils.cpp` | case '#' precheck delimiter-driven; res<0 -> OP_MSG_ERROR preserved | VERIFIED | `case '#'` block at lines 159-171; `LOG_ERROR_ID_U16(MSG_ERR_DATA_ERR_N` present; `OP_MSG_ERROR` returned on res<0; dead `available()<=0` guard removed (WR-02 fix) |
| `firestarter_app/firestarter/frame_parser.py` | `cobs_encode` / `cobs_decode` helpers; CRC8 reused unchanged | VERIFIED | `def cobs_encode(` at line 58; `def cobs_decode(` at line 103; CR-01 fix confirmed: `if run_len == 254:` branch appears before `elif i < n and payload[i] == 0x00:` at lines 90/94 |
| `firestarter_app/firestarter/eprom_operations.py` | COBS-framed send in `_main_phase_send_data`; atomic write | VERIFIED | `cobs_encode(data_chunk + bytes([crc]))` at line 379; `frame = b"#" + body + b"\x00"` at line 380; single `self.comm.send_bytes(frame)` call at line 388; `from firestarter.frame_parser import _crc8_ccitt, cobs_encode` at line 50 |
| `firestarter/test/native/avr/test_cobs_data_frame/test_cobs_data_frame.cpp` | Firmware COBS decode + resync Unity cases (FRAME-01/02) | VERIFIED | File exists (13,634 B); `RUN_TEST(test_cobs_decode_valid_frame)`, `RUN_TEST(test_cobs_resync_bounded)`, `RUN_TEST(test_cobs_all_zero_payload)`, `RUN_TEST(test_cobs_254_run_then_zero)` all present; 29/29 native suite passes |
| `firestarter/test/native/avr/test_messages/serial_read_mock.h` | ArduinoFake Serial.read/available/peek queued-byte mock | VERIFIED | File exists (3,732 B); documents `read()`, `available()`, `peek()` over `rx_queue` vector |
| `firestarter_app/tests/test_cobs.py` | Host COBS contract + resync tests | VERIFIED | File exists (15,775 B); 23 tests collected and passed; `cobs_resync` tested (2 matches); 254-run boundary tests present (8 matches for "254"); 0 references to `_read_and_parse_lines`, `MSG_DATA_CHUNK`, `MAGIC_PREAMBLE` |
| `firestarter/scripts/check_uno_ram.sh` | Scripted Uno RAM-ceiling assertion (FRAME-03) | VERIFIED | File exists, executable; `RAM_FLOOR=545` at line 26; parses RAM line via awk; exits 0 on current build |
| `.planning/phases/50-.../50-RAM-REPORT.md` | Post-change Uno RAM figures vs Phase-49 baseline | VERIFIED | Exists; documents 1503/2048 B used (545 B free, 0 B delta); "no second ~512 B static buffer"; Leonardo A/B-pin disposition recorded |

---

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `firestarter/src/operation_utils.cpp` | `rurp_communication_read_data` | `case '#'` dispatch | VERIFIED | `rurp_communication_read_data(handle->data_buffer)` confirmed at line 164 (1 match) |
| `firestarter/src/boards/rurp_serial_utils.cpp` | `crc8_ccitt` | CRC8 over decoded payload before accept | VERIFIED | `grep -c 'crc8_ccitt' rurp_serial_utils.cpp` = 10; called in decode (lines ~182-187) and encode (lines ~205-208) |
| `firestarter_app/firestarter/eprom_operations.py` | `firestarter.frame_parser.cobs_encode` | import + frame build | VERIFIED | `from firestarter.frame_parser import _crc8_ccitt, cobs_encode` at line 50; `cobs_encode(data_chunk` at line 379 (2 grep matches) |
| `firestarter_app/firestarter/eprom_operations.py` | `self.comm.send_bytes` | single atomic send of `b'#' + body + b'\x00'` | VERIFIED | `self.comm.send_bytes(frame)` at line 388 (1 match); frame assembled as one object at line 380 |

---

### Data-Flow Trace (Level 4)

The host write-path data flow traces cleanly:

1. `_main_phase_send_data` reads `data_chunk` from file
2. `crc = _crc8_ccitt(data_chunk)` computes integrity byte
3. `body = cobs_encode(data_chunk + bytes([crc]))` produces COBS body
4. `frame = b"#" + body + b"\x00"` assembles atomic frame
5. `self.comm.send_bytes(frame)` sends in one call

The firmware decode path:
1. `op_get_message` peaks `'#'`, consumes it, calls `rurp_communication_read_data(handle->data_buffer)`
2. `rurp_communication_read_data` streams bytes until `0x00`, decodes COBS in-place into `buffer`
3. CRC8 verified over decoded payload; mismatch drains to next `0x00` and returns -4
4. On success, `handle->data_size = res` and `OP_MSG_DATA` returned

| Artifact | Data Variable | Source | Produces Real Data | Status |
|----------|--------------|--------|--------------------|--------|
| `eprom_operations.py:_main_phase_send_data` | `data_chunk` | binary file read | Yes | FLOWING |
| `rurp_serial_utils.cpp:rurp_communication_read_data` | `buffer[out]` | serial RX bytes via `rurp_communication_read()` | Yes | FLOWING |

---

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Host COBS test suite (23 tests) | `cd firestarter_app && python -m pytest tests/test_cobs.py -v` | 23 passed in 0.03s | PASS |
| Firmware native suite (29 tests, 5 suites) | `cd firestarter && pio test -e native` | 29 succeeded in 10.3s | PASS |
| Host full suite (410 tests, coverage 71.71%) | `cd firestarter_app && python -m pytest --cov-fail-under=70` | 410 passed, coverage floor held | PASS |
| Uno RAM ceiling gate | `cd firestarter && bash scripts/check_uno_ram.sh` | free=545 B >= floor=545 B, exits 0 | PASS |
| timeout_ms = 2000 loop absent | `grep -c 'timeout_ms = 2000' rurp_serial_utils.cpp` | 0 | PASS |
| len_u16 absent from firmware write path | `grep -c 'size >> 8' rurp_serial_utils.cpp` | 0 | PASS |
| len_u16 absent from host send path | `grep -c 'to_bytes(2, "big")' eprom_operations.py` | 0 | PASS |
| Log/telemetry path untouched | `grep -c '_firestarter_emit_frame' rurp_serial_utils.cpp` | 5 (present, unchanged) | PASS |

---

### Probe Execution

No `probe-*.sh` files declared or found. Step 7c not applicable for this phase.

---

### Requirements Coverage

| Requirement | Source Plans | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| FRAME-01 | 50-01, 50-02, 50-03 | Delimiter-based framing on data-block path, replacing `[len_u16][xor][payload]` | SATISFIED | COBS `[body][0x00]` frame in both repos; len_u16/XOR gone from both encoder and decoder; `test_cobs_decode_valid_frame` passes |
| FRAME-02 | 50-01, 50-02, 50-03 | Auto-resync — bounded to one frame; 2 s cascade eliminated | SATISFIED | `_drain_to_delimiter()` on any error path; `timeout_ms=2000` loop absent (grep=0); `test_cobs_resync_bounded` passes in firmware; `test_cobs_resync` passes in host |
| FRAME-03 | 50-01, 50-02, 50-04 | Streaming, no second ~512 B buffer, fits Uno ~545 B free-RAM ceiling | SATISFIED | `check_uno_ram.sh` exits 0; RAM delta = 0 B; Flash +320 B (not a binding constraint); `50-RAM-REPORT.md` attests |
| FRAME-04 | 50-01, 50-02, 50-04 | 512 B (Uno) and 1024 B (Leonardo) transfers frame transparently | SATISFIED | `test_cobs_all_zero_payload` (512 B) passes; COBS is size-agnostic; Leonardo `DATA_BUFFER_SIZE=512` A/B pin is a deliberate operator decision (keep-512-documented), not a defect; 1024 B path test-validated by parameterized COBS round-trips |
| CRC-01 | 50-01, 50-02, 50-03 | CRC8-CCITT poly 0x07, seed 0x00 retained; no polynomial swap | SATISFIED | PROGMEM table unchanged in firmware; `_build_crc8_table` unchanged in host; `test_crc_polynomial_smoke` + `test_crc8_data_payload` pass; CR-01 254-run-boundary bug in `cobs_encode` fixed (branch order swapped) |

Note: REQUIREMENTS.md traceability table still shows `- [ ]` (Pending) for all Phase-50 requirements — this is the standard milestone-tracking format; the checkboxes are updated at milestone close by the operator, not by individual phase executors.

---

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `rurp_serial_utils.cpp` | 92, 125 | `while (rurp_communication_available() <= 0) {}` — unbounded byte-wait spin | Warning (WR-01, deferred) | See WR-01 assessment below |

No `TBD`, `FIXME`, or `XXX` markers found in any modified files.

**WR-01 Assessment (unbounded spin — deferred advisory):**

The spin at lines 92 and 125 of `rurp_serial_utils.cpp` has no per-byte timeout. If the host stops mid-frame (crash, disconnect), the firmware hangs until board reset. The code reviewer (50-REVIEW.md) flagged this as WR-01 and proposed a 3 s byte-level deadline.

The plan explicitly removed the 2 s `timeout_ms` loop (D-01/D-03) with the stated rationale that "incomplete frame → `OP_MSG_INCOMPLETE`, governed by existing op-level timeout machinery." However, `_drain_to_delimiter` and the main decoder loop are BELOW the op-level timeout — they are called from inside `rurp_communication_read_data`, which is called from `case '#'`, which is called from `op_get_message`, which IS guarded by the outer `op_wait_for_ack` 1000 ms timeout and the operation state machine. The gap is: once the `'#'` byte is consumed and execution enters `rurp_communication_read_data`, NO op-level timeout can interrupt it — the spin is beneath that layer.

**Judgment:** WR-01 is a genuine residual risk (firmware hang on mid-frame host disconnect), but it does not defeat any of the four phase success criteria. The 2 s cascade source (the `len_u16`-corruption path that triggered wrong-length reads) is eliminated. The unbounded spin is a new but qualitatively different failure mode — a clean firmware hang rather than a corrupt transfer. It is advisable to add a frame-level deadline in a follow-up phase. Per the context notes, this is classified as advisory/deferred, not a blocker.

---

### Human Verification Required

None. All must-haves are verified programmatically. No visual, real-time, or external-service behaviors require human testing at this phase gate.

Hardware bench verification (byte-exact transport proof on real boards) is explicitly scoped to Phase 53 (XACT-01/XACT-02/XACT-03) and is not a Phase 50 success criterion.

---

### Gaps Summary

No gaps. All four roadmap success criteria are verified, all required artifacts exist and are substantive, all key links are wired, and all requirement IDs (FRAME-01..04, CRC-01) are satisfied.

The one advisory item (WR-01, unbounded byte-wait spin) does not defeat any success criterion and is deferred per the design decision recorded in 50-REVIEW.md.

---

**Post-review fix verification:** CR-01 (`cobs_encode` dropped a zero byte at 254-run boundaries) was fixed before this verification. The fix is confirmed at `frame_parser.py` lines 90-94: `if run_len == 254:` branch precedes `elif i < n and payload[i] == 0x00:`. The regression test (`test_254_run_boundary_followed_by_zero`) is present in `test_cobs.py` and passes as part of the 23-test COBS suite.

---

_Verified: 2026-06-01T21:00:00Z_
_Verifier: Claude (gsd-verifier)_
