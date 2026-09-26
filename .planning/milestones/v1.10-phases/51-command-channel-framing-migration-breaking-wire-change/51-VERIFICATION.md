---
phase: 51-command-channel-framing-migration-breaking-wire-change
verified: 2026-06-02T11:00:00Z
status: passed
score: 6/6 must-haves verified
overrides_applied: 0
re_verification:
  previous_status: gaps_found
  previous_score: 2/4
  gaps_closed:
    - "CR-01 OOB write: PUSH overflow guard lowered to DATA_BUFFER_SIZE-1; belt-and-suspenders guard added in firestarter.cpp; NUL-terminate write provably in-bounds for all legal payloads"
    - "CR-02 truncated-frame hang: both spin sites in _drain_to_delimiter() and the main decode loop replaced with millis()-based bounded inter-byte deadlines; truncated frame returns negative instead of hanging"
  gaps_remaining: []
  regressions: []
deferred: []
human_verification: []
---

# Phase 51: Command-Channel Framing Migration — Re-Verification Report

**Phase Goal:** Migrate the host→fw JSON command channel into the COBS framing (CRC8-verified before the JSON parser sees the payload); firmware + host upgrade lockstep, no mixed-version interop.
**Verified:** 2026-06-02T11:00:00Z
**Status:** PASSED
**Re-verification:** Yes — after gap closure (plans 51-01 through 51-04)

---

## Goal Achievement

### Observable Truths

All six must-haves are drawn from the merged 51-01 and 51-04 PLAN frontmatter (51-04 supersedes the two failed truths from the previous verification, the original 51-01 truths SC1–SC4 are the base, 51-04 adds the gap-closure truths).

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | A corrupted command frame (CRC8 mismatch) makes rurp_communication_read_data() return < 0 and parse_json() is never invoked | VERIFIED | `test_cobs_crc_reject_does_not_reach_parser` PASSED. Decoder returns -4 on CRC mismatch; gate in firestarter.cpp is strictly `n > 0`, so parse_json is never reached on any negative return. Confirmed by reading firestarter.cpp lines 176-195. |
| 2 | A valid COBS+CRC8 command frame decodes into handle.data_buffer and reaches parse_json() with the exact JSON payload | VERIFIED | `test_cobs_decode_valid_json_command` PASSED. firestarter.cpp CMD_IDLE branch calls `rurp_communication_read_data(handle.data_buffer)`, gates on `n > 0`, NUL-terminates, calls `init_programmer_framed()` which calls `parse_json()`. All 7 cmd_frame cases PASS. |
| 3 | A command frame whose decoded payload is EXACTLY DATA_BUFFER_SIZE bytes decodes/returns correctly and the CMD_IDLE NUL-terminate write never touches data_buffer[DATA_BUFFER_SIZE] — no OOB write into handle.data_size (closes CR-01) | VERIFIED | `test_cobs_exact_buffer_size_payload` PASSED — 512-byte payload returns < 0 (overflow path). `test_cobs_max_accepted_payload` PASSED — 511-byte payload decodes to n==511 and data matches. PUSH guard confirmed at rurp_serial_utils.cpp:144: `if (out >= DATA_BUFFER_SIZE - 1)`. Belt-and-suspenders guard in firestarter.cpp:179: `if (n < DATA_BUFFER_SIZE)`. No path writes data_buffer[512]. |
| 4 | A truncated command frame (bytes arrive then host goes silent before the 0x00) makes rurp_communication_read_data() RETURN a negative value within a bounded mid-frame inter-byte deadline — it does NOT spin forever (closes CR-02) | VERIFIED | `test_cobs_truncated_frame_no_hang` PASSED. Both spin sites in rurp_serial_utils.cpp now use millis()-bounded waits (lines 114-118 in _drain_to_delimiter, lines 168-174 in main decode loop). grep confirms 4 millis() references (2 `start=millis()` assignments, 2 `millis()-start >= TIMEOUT_MS` comparisons). No bare `while (available() <= 0) {}` remains. |
| 5 | The truly-idle CMD_IDLE path keeps the SC1 win: no 2-second idle wall-clock timeout is reintroduced — the bounded guard is armed only once a frame is in progress (first byte seen) | VERIFIED | loop() in firestarter.cpp gates decoder entry on `rurp_communication_available() > 0` (line 163). millis() appears in firestarter.cpp only on the op-command timeout path (line 159: `handle.cmd != CMD_IDLE`) and op_reset_timeout() (line 259). No millis() on the CMD_IDLE idle branch. The bounded wait in rurp_serial_utils.cpp is armed only inside the decode call — after loop() has already confirmed bytes are available. |
| 6 | The legacy {-peek / discard-non-{ command-ingest loop no longer exists in firestarter.cpp; breaking-change documentation in both sub-repo READMEs; host emits COBS+CRC8 framed commands atomically; CMD_FRAME_MAX parity holds | VERIFIED | grep confirms absence of `rurp_communication_peak`, `== '{'`, and in-path `rurp_communication_read_bytes` in firestarter.cpp. Both READMEs contain "Breaking Changes (v1.10)" with "breaking", COBS/CRC8, lockstep requirement. serial_comm.py send_json_command: CRC8 over raw json_bytes, cobs_encode(json_bytes+crc), single frame = body+b"\x00", one send_bytes() call. CMD_FRAME_MAX = 512 in both firestarter.h (via DATA_BUFFER_SIZE) and constants.py. |

**Score:** 6/6 truths verified

---

## Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `firestarter/src/boards/rurp_serial_utils.cpp` | In-bounds decode cap (out capped at DATA_BUFFER_SIZE-1) + bounded mid-frame inter-byte wait on both spin sites | VERIFIED | PUSH guard: `if (out >= DATA_BUFFER_SIZE - 1)` at line 147. Both spin sites: millis()-bounded waits at lines 114-119 (_drain_to_delimiter) and 168-174 (main loop). Drain-on-expiry pattern intact. |
| `firestarter/src/firestarter.cpp` | CMD_IDLE COBS frame decode; init_programmer_framed; belt-and-suspenders NUL guard | VERIFIED | `rurp_communication_read_data(handle.data_buffer)` at line 176. Gate `n > 0` at line 177. `if (n < DATA_BUFFER_SIZE)` guard at line 184. `handle.data_buffer[n] = '\0'` at line 185. `init_programmer_framed(&handle)` at line 187. No rurp_communication_peak, no `== '{'`, no in-path rurp_communication_read_bytes. |
| `firestarter/test/native/avr/test_cobs_cmd_frame/test_cobs_cmd_frame.cpp` | 7 Unity cases including exact-boundary + max-accepted + truncated-no-hang | VERIFIED | All 7 cases present and PASSED: decode_valid, crc_reject, resync_bounded, oversized_bounded_recovery, exact_buffer_size_payload, max_accepted_payload, truncated_frame_no_hang. |
| `firestarter/test/native/avr/test_cobs_cmd_frame/serial_read_mock.h` | Suite-local finite-stream mock (available()=0, read()=-1 after exhaustion) | VERIFIED | Local copy present; finite-stream semantics documented in header comment; `setup_serial_read_mock()` lambdas return 0/−1 after pos >= queue.size(). |
| `firestarter/test/native/avr/test_cobs_cmd_frame/host_stubs.cpp` | Native-platform rurp_* stubs via _shared/host_stubs_common.inc | VERIFIED (from prior verification, unchanged) | Present; includes host_stubs_common.inc. |
| `firestarter/include/firestarter.h` | CMD_FRAME_MAX = DATA_BUFFER_SIZE; TIMEOUT_MS = 1000; struct field order data_buffer then data_size | VERIFIED | `#define CMD_FRAME_MAX DATA_BUFFER_SIZE` at line 26. `#define TIMEOUT_MS 1000` at line 28. `char data_buffer[DATA_BUFFER_SIZE]` at line 95, `uint32_t data_size` at line 96. |
| `firestarter_app/firestarter/serial_comm.py` | Framed send_json_command (COBS+CRC8, atomic write, no send_string) | VERIFIED (from prior verification, unchanged) | Lines 156-175: CRC over json_bytes, cobs_encode(json_bytes+crc), frame=body+b"\x00", single send_bytes(frame). No send_string call inside send_json_command. |
| `firestarter_app/firestarter/constants.py` | CMD_FRAME_MAX = 512 | VERIFIED (from prior verification, unchanged) | Line 28: `CMD_FRAME_MAX = 512` with sync comment. |
| `firestarter_app/tests/test_serial_comm.py` | Three framed-command tests | VERIFIED (from prior verification, unchanged) | test_send_json_command_emits_cobs_frame, test_send_json_command_atomic_frame, test_send_json_command_version_probe_is_framed — all 3 PASSED. |
| `firestarter/README.md` | Breaking wire-change note | VERIFIED (from prior verification, unchanged) | "Breaking Changes (v1.10)" section confirmed. |
| `firestarter_app/README.md` | Breaking wire-change note | VERIFIED (from prior verification, unchanged) | "Breaking Changes (v1.10)" section confirmed. |

---

## Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `firestarter.cpp CMD_IDLE branch` | `rurp_communication_read_data(handle.data_buffer)` | Frame decode replacing {-peek | WIRED | Line 176; gate strictly `n > 0`; no legacy peek remains |
| `firestarter.cpp CMD_IDLE` | `init_programmer_framed(&handle)` | Called after n > 0, with pre-filled data_buffer | WIRED | Line 187; data_buffer NUL-terminated at line 185 under guard |
| `rurp_serial_utils.cpp spin loops` | `millis()-based mid-frame inter-byte deadline` | Bounded wait armed on first available byte; return negative + drain on expiry | WIRED | 4 millis() references confirmed; both spin sites covered |
| `firestarter.cpp CMD_IDLE` | `rurp_communication_read_data() return value n` | n bounded to DATA_BUFFER_SIZE-1 by decoder; NUL write in-bounds | WIRED | PUSH guard at `out >= DATA_BUFFER_SIZE - 1`; call-site guard `if (n < DATA_BUFFER_SIZE)` |
| `firestarter/platformio.ini` | `native/avr/test_cobs_cmd_frame` | test_filter + -I build flag | WIRED | 2 entries: line 84 (test_filter), line 94 (-I flag) |
| `send_json_command` | `cobs_encode / _crc8_ccitt` | COBS+CRC8 wrap before send_bytes | WIRED | serial_comm.py lines 53 (import), 172-173 (usage) |
| `send_json_command` | `send_bytes(frame)` | Single atomic write | WIRED | Line 175: one bytes object, one call |
| `firestarter.h CMD_FRAME_MAX` | `constants.py CMD_FRAME_MAX` | Constant parity (CLAUDE.md) | WIRED | Both = 512 confirmed |

---

## Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|----------|--------------|--------|--------------------|--------|
| `firestarter.cpp CMD_IDLE` | `handle.data_buffer` / `handle.data_size` | `rurp_communication_read_data()` reads from serial RX buffer, COBS-decodes in place, CRC8-verifies | Yes — live serial bytes from host command frame | FLOWING |
| `serial_comm.py send_json_command` | `frame` bytes | `json.dumps(command_dict)` + CRC8 + `cobs_encode` | Yes — computed from caller's command dict; test suite verifies round-trip decode | FLOWING |

---

## Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| All 7 cmd_frame Unity cases pass | `pio test -e native -f "native/avr/test_cobs_cmd_frame"` | 7/7 PASSED in 6.24s | PASS |
| Full firmware native regression (36 cases) | `pio test -e native` | 36/36 PASSED in 30.8s (dispatch, read_timing, cobs_cmd_frame, cobs_data_frame, data_input, messages) | PASS |
| Host framing tests (3 cases) | `pytest -k "cobs_frame or atomic_frame or version_probe_is_framed"` | 3/3 PASSED | PASS |
| Full host suite with coverage floor | `python -m pytest --cov-fail-under=70` | 413 PASSED, 29 snapshots passed | PASS |

---

## Probe Execution

No probes declared in plan frontmatter or SUMMARY. Conventional `scripts/*/tests/probe-*.sh` not present for this phase. SKIPPED.

---

## Requirements Coverage

| Requirement | Source Plans | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| FRAME-05 | 51-01, 51-02, 51-03, 51-04 | Host→fw command channel migrated to COBS framing; firmware decodes frame, verifies CRC8 before JSON parser; legacy {-peek replaced; breaking lockstep change | SATISFIED | All sub-claims verified: CRC8-before-parse (test pinned), {-peek deleted (grep confirmed), breaking-change documented (both READMEs), host emits framed commands (3 host tests pass), full native suite green. CR-01 and CR-02 closed by plan 51-04. |
| CRC-01 | 51-01, 51-02, 51-04 | CRC8-CCITT verified before parse on every command frame; command channel previously had no checksum | SATISFIED | CRC8 verify logic correct and confirmed by `test_cobs_crc_reject_does_not_reach_parser` (PASSED). CR-01 OOB write closed — decoder cap at DATA_BUFFER_SIZE-1 ensures n <= DATA_BUFFER_SIZE-1 always, so CRC verify runs on a cleanly bounded buffer. CR-02 hang closed — truncated frame returns bounded negative. Both FRAME-05 and CRC-01 fully satisfied including memory-safety and DoS-on-stall dimensions. |

Both requirement IDs declared in plan frontmatter are accounted for. REQUIREMENTS.md marks FRAME-05 and CRC-01 as Complete for Phase 51. No orphaned requirements for this phase.

---

## Anti-Patterns Found

No debt markers (TBD, FIXME, XXX) found in any modified file. No warning-level markers (TODO, PLACEHOLDER) found in production source files. The 51-04 SUMMARY notes WR-01 (`CMD_FRAME_MAX` declared in constants.py but not enforced on the host send path) and WR-02 (`MSG_ERR_EMPTY_INPUT` reused for all decode failures) as out-of-scope advisories from the code review. Both are documented follow-ups explicitly deferred by plan scope; neither violates a stated must-have.

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `firestarter/src/firestarter.cpp` | 193-195 | `LOG_ERROR_ID(MSG_ERR_EMPTY_INPUT)` reused for all decode failures | INFO (WR-02 advisory) | Misleading error ID for CRC mismatch / COBS violation — out-of-scope follow-up; deferred by plan |
| `firestarter_app/firestarter/constants.py` | 28 | `CMD_FRAME_MAX = 512` defined but not enforced on send path | INFO (WR-01 advisory) | Host can send oversized commands — out-of-scope advisory; deferred by plan |

Neither is a BLOCKER. The two items that were BLOCKERs in the previous verification (CR-01, CR-02) are closed.

---

## Human Verification Required

None. All must-haves are verified programmatically from source and test run output.

---

## Gaps Summary

No gaps remain. Both BLOCKERs from the previous verification are closed:

**CR-01 (closed):** PUSH overflow guard lowered to `DATA_BUFFER_SIZE - 1` at rurp_serial_utils.cpp:144. Belt-and-suspenders `if (n < DATA_BUFFER_SIZE)` guard at firestarter.cpp:179. Boundary pinned by `test_cobs_exact_buffer_size_payload` (512-byte payload returns < 0) and `test_cobs_max_accepted_payload` (511-byte payload round-trips cleanly). The NUL-terminate write `data_buffer[n] = '\0'` at line 185 is unreachable for n >= DATA_BUFFER_SIZE by construction.

**CR-02 (closed):** Both bare spin-wait sites replaced with millis()-bounded inter-byte deadlines. The deadline is armed only when decoding is underway (loop() gates entry on available() > 0), so the truly-idle path runs no timer — D-06 intent honored. Pinned by `test_cobs_truncated_frame_no_hang` (call returns negative; test binary terminates).

WR-01 and WR-02 are out-of-scope advisories, not gaps. They are noted as potential follow-up work for Phase 52 or later.

---

_Verified: 2026-06-02T11:00:00Z_
_Verifier: Claude (gsd-verifier)_
