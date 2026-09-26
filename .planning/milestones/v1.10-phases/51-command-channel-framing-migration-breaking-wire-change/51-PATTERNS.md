# Phase 51: Command-Channel Framing Migration — Pattern Map

**Mapped:** 2026-06-02
**Files analyzed:** 7 (2 new, 5 modify)
**Analogs found:** 7 / 7

---

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `firestarter/test/native/avr/test_cobs_cmd_frame/test_cobs_cmd_frame.cpp` | test | request-response | `firestarter/test/native/avr/test_cobs_data_frame/test_cobs_data_frame.cpp` | exact |
| `firestarter/test/native/avr/test_cobs_cmd_frame/host_stubs.cpp` | test-support | — | `firestarter/test/native/avr/test_cobs_data_frame/host_stubs.cpp` | exact |
| `firestarter/src/firestarter.cpp` | controller | request-response | itself (lines 161-174 deleted; lines 109-144 modified) — COBS data-path in `rurp_serial_utils.cpp` is the behavioral analog | role-match |
| `firestarter/src/boards/rurp_serial_utils.cpp` | utility | streaming | itself — no source changes; signatures exposed for call-site reference | reference |
| `firestarter/include/firestarter.h` | config | — | itself — existing constant block (lines 18-41) is the parity pattern | role-match |
| `firestarter_app/firestarter/constants.py` | config | — | itself — existing `BUFFER_SIZE`/`COMMAND_*` block (lines 21-57) is the parity pattern | role-match |
| `firestarter_app/firestarter/serial_comm.py` | service | request-response | itself `send_bytes()` (lines 134-148) + `test_cobs.py` `build_cobs_frame()` for encode pattern | role-match |
| `firestarter_app/tests/test_serial_comm.py` | test | request-response | itself (lines 132-146) + `firestarter_app/tests/test_cobs.py` (lines 44-55, 79-146) | exact |

---

## Pattern Assignments

### `firestarter/test/native/avr/test_cobs_cmd_frame/test_cobs_cmd_frame.cpp` (test, Unity)

**Analog:** `firestarter/test/native/avr/test_cobs_data_frame/test_cobs_data_frame.cpp`

**File-level header and includes** (lines 1-51):
```cpp
#include <Arduino.h>
#include <ArduinoFake.h>
#include <unity.h>

#include <cstdint>
#include <cstddef>
#include <cstring>
#include <vector>

/* Shared mock helper — wires Serial.read/available/peek to a queued vector. */
#include "serial_read_mock.h"

extern "C" {
#include "rurp_shield.h"
#include "firestarter.h"
}

using namespace fakeit;
```

**Shared test state** (lines 56-58):
```cpp
static char data_buffer[DATA_BUFFER_SIZE];
static std::vector<uint8_t> rx_queue;
static size_t rx_pos;
```

**Reference CRC8 (table-free, independent of production PROGMEM table)** (lines 65-76):
```cpp
static uint8_t ref_crc8(const uint8_t* data, size_t n) {
    uint8_t crc = 0;
    for (size_t i = 0; i < n; i++) {
        crc ^= data[i];
        for (int k = 0; k < 8; k++) {
            crc = (crc & 0x80)
                      ? (uint8_t)((crc << 1) ^ 0x07)
                      : (uint8_t)(crc << 1);
        }
    }
    return crc;
}
```

**Test-side COBS encoder** (lines 89-112):
```cpp
static size_t test_cobs_encode(const uint8_t* src, size_t len, uint8_t* dst) {
    size_t out = 0;
    size_t code_pos = out++;
    uint8_t code = 1;
    for (size_t i = 0; i < len; i++) {
        if (src[i] == 0x00) {
            dst[code_pos] = code;
            code_pos = out++;
            code = 1;
        } else {
            dst[out++] = src[i];
            code++;
            if (code == 0xFF) {
                dst[code_pos] = code;
                code_pos = out++;
                code = 1;
            }
        }
    }
    dst[code_pos] = code;
    return out;
}
```

**Frame-builder helper** (lines 117-134):
```cpp
/* Build COBS frame bytes: COBS(payload + CRC8(payload)) + 0x00
 * Command frames do NOT have the '#' marker (unlike data frames) — the
 * command channel is delimiter-only (0x00), no preamble byte. */
static void build_cobs_frame_bytes(
    const uint8_t* payload, size_t payload_len,
    std::vector<uint8_t>& out_vec
) {
    uint8_t crc = ref_crc8(payload, payload_len);
    std::vector<uint8_t> src(payload, payload + payload_len);
    src.push_back(crc);
    size_t max_enc = src.size() + src.size() / 254 + 2;
    std::vector<uint8_t> encoded(max_enc);
    size_t enc_len = test_cobs_encode(src.data(), src.size(), encoded.data());
    out_vec.insert(out_vec.end(), encoded.data(), encoded.data() + enc_len);
    out_vec.push_back(0x00);  /* frame delimiter */
}
```

Note: data-path frames prepend `b"#"` before the COBS body (see `test_cobs.py:build_cobs_frame`). Command frames do NOT use the `'#'` marker — the `CMD_IDLE` loop calls `rurp_communication_read_data()` directly when `rurp_communication_available() > 0`, with no preamble-byte dispatch. The `build_cobs_frame_bytes` helper from `test_cobs_data_frame.cpp` above is correct as-is for the command channel (no `'#'` prefix needed in the rx_queue).

**setUp / tearDown pattern** (lines 146-172):
```cpp
static unsigned long millis_counter;

void setUp(void) {
    ArduinoFakeReset();
    rx_queue.clear();
    rx_pos = 0;
    millis_counter = 0;
    memset(data_buffer, 0, sizeof(data_buffer));

    When(Method(ArduinoFake(Serial), flush)).AlwaysReturn();
    When(OverloadedMethod(ArduinoFake(Serial), write, size_t(uint8_t)))
        .AlwaysReturn((size_t)1);
    When(Method(ArduinoFake(Function), millis))
        .AlwaysDo([&]() -> unsigned long {
            millis_counter += 100;
            return millis_counter;
        });
}

void tearDown(void) {}
```

**Test case structure — valid frame** (lines 185-199 as model):
```cpp
void test_cobs_decode_valid_frame(void) {
    uint8_t payload[] = { /* small JSON bytes */ };
    size_t payload_len = sizeof(payload);

    build_cobs_frame_bytes(payload, payload_len, rx_queue);
    setup_serial_read_mock(rx_queue, rx_pos);

    int res = rurp_communication_read_data(data_buffer);

    TEST_ASSERT_GREATER_OR_EQUAL_INT(0, res);
    TEST_ASSERT_EQUAL_size_t(payload_len, (size_t)res);
    TEST_ASSERT_EQUAL_MEMORY(payload, data_buffer, payload_len);
}
```

**Test case structure — CRC8 reject (V5 / §4.4 headline behavioral proof)**:
```cpp
void test_cobs_crc_reject_does_not_reach_parser(void) {
    /* Deliberate CRC flip: COBS-encode a known payload but corrupt the CRC byte.
     * rurp_communication_read_data() must return < 0; parse_json() must NOT be called.
     * This is the V5 / §4.4 CRC8-before-parse mandate behavioral proof. */
    uint8_t payload[] = { 0xFF, 0xFF, 0xFF, 0xFF };
    uint8_t bad_crc = ref_crc8(payload, sizeof(payload)) ^ 0xAA;  /* deliberate flip */
    uint8_t bad_src[] = { 0xFF, 0xFF, 0xFF, 0xFF, bad_crc };
    /* COBS-encode the corrupted logical stream directly */
    uint8_t encoded[16];
    size_t enc_len = test_cobs_encode(bad_src, sizeof(bad_src), encoded);
    for (size_t i = 0; i < enc_len; i++) rx_queue.push_back(encoded[i]);
    rx_queue.push_back(0x00);

    setup_serial_read_mock(rx_queue, rx_pos);

    int res = rurp_communication_read_data(data_buffer);
    TEST_ASSERT_LESS_THAN_INT(0, res);
    /* data_buffer is NOT passed to parse_json — caller enforces `if (n > 0)` gate */
}
```

**Test case structure — resync/bounded recovery** (lines 211-244 as model):
```cpp
void test_cobs_resync_bounded(void) {
    /* [garbled frame][0x00][valid frame][0x00] — mirrors test_cobs_data_frame.cpp lines 211-244 */
    uint8_t good_payload[] = { /* small valid JSON */ };
    /* ... build garbled frame, append 0x00, append valid frame ... */
    /* First call: must return error (res < 0) */
    int res1 = rurp_communication_read_data(data_buffer);
    TEST_ASSERT_LESS_THAN_INT(0, res1);
    /* Second call: must decode correctly (bounded recovery, not mere detection) */
    int res2 = rurp_communication_read_data(data_buffer);
    TEST_ASSERT_GREATER_OR_EQUAL_INT(0, res2);
    TEST_ASSERT_EQUAL_MEMORY(good_payload, data_buffer, good_len);
}
```

**main() runner** (lines 306-317):
```cpp
int main(int argc, char** argv) {
    (void)argc;
    (void)argv;
    UNITY_BEGIN();

    RUN_TEST(test_cobs_decode_valid_json_command);
    RUN_TEST(test_cobs_crc_reject_does_not_reach_parser);
    RUN_TEST(test_cobs_resync_bounded);
    RUN_TEST(test_cobs_oversized_frame_bounded_recovery);

    return UNITY_END();
}
```

**`serial_read_mock.h` location:** The `test_cobs_data_frame` directory does NOT contain `serial_read_mock.h` as a file (it was not found). The mock is referenced via the `-I test/native/avr/test_cobs_data_frame` build flag in `platformio.ini`. Check whether `serial_read_mock.h` lives in another directory (e.g., `test_messages/`) and add the correct `-I` path. Planner must verify the actual file location (`find /workspaces/firestarter/test -name serial_read_mock.h`).

---

### `firestarter/test/native/avr/test_cobs_cmd_frame/host_stubs.cpp` (test-support)

**Analog:** `firestarter/test/native/avr/test_cobs_data_frame/host_stubs.cpp`

**Complete file content — copy verbatim** (lines 1-30):
```cpp
/*
 * Phase 51 Plan NN — host stub TU for the test_cobs_cmd_frame suite.
 *
 * Provides no-op rurp_* symbol implementations so the test binary links
 * against boards/rurp_serial_utils.cpp on the host platform = native.
 *
 * Mirrors test_cobs_data_frame/host_stubs.cpp (Phase 50 Plan 01).
 * No suite-specific overrides — defaults from the shared include are correct.
 */

#include <stdint.h>
#include <stddef.h>
#include <string.h>

#include <Arduino.h>
#include <ArduinoFake.h>

extern "C" {
#include "rurp_shield.h"
#include "rurp_types.h"
}

#include "../_shared/host_stubs_common.inc"
```

The `host_stubs_common.inc` shared file (`firestarter/test/native/avr/_shared/host_stubs_common.inc`) provides all `rurp_*` no-ops and the `Serial_::operator bool()` definition. No suite-specific overrides are required for `test_cobs_cmd_frame` — the defaults suffice because the suite only calls `rurp_communication_read_data()` (which is in `rurp_serial_utils.cpp`, pulled in by `build_src_filter`).

---

### `firestarter/src/firestarter.cpp` — `CMD_IDLE` loop surgery (controller, request-response)

**Analog:** `firestarter/src/boards/rurp_serial_utils.cpp` `rurp_communication_read_data()` (lines 100-191) — the function that replaces the peek/discard path.

**Current code to DELETE** (`firestarter.cpp` lines 161-175):
```c
} else if (handle.cmd == CMD_IDLE) {
    if (rurp_communication_available() > 0) {
        // Look for the start of a JSON object '{' before trying to parse.
        if (rurp_communication_peak() == '{') {
            if (init_programmer(&handle)) {
                return;
            }
        } else {
            rurp_communication_read();  // Discard non-'{' character
        }
    }
    return;
}
```

**Replacement pattern (D-05):**
```c
} else if (handle.cmd == CMD_IDLE) {
    if (rurp_communication_available() > 0) {
        // Phase 51: COBS frame decoder replaces {-peek path (D-05).
        // rurp_communication_read_data() spins until 0x00 delimiter,
        // COBS-decodes in-place into handle.data_buffer, verifies CRC8,
        // drains on error (D-06). Returns decoded payload length or negative.
        int n = rurp_communication_read_data(handle.data_buffer);
        if (n > 0) {
            handle.data_size = (uint32_t)n;
            handle.data_buffer[n] = '\0';
            if (init_programmer_framed(&handle)) {
                return;
            }
        } else {
            // n == 0: empty frame; n < 0: COBS/CRC/overflow error.
            // _drain_to_delimiter() already called inside rurp_communication_read_data().
            LOG_ERROR_ID(MSG_ERR_BAD_FRAME);  // new ID, or reuse MSG_ERR_EMPTY_INPUT
        }
    }
    return;
}
```

**`init_programmer()` current code — lines to remove** (lines 109-121):
```c
bool init_programmer(firestarter_handle_t* handle) {
    handle->response_code = RESPONSE_CODE_OK;
    handle->operation_state = 0;

    handle->data_size = rurp_communication_read_bytes(   // ← DELETE this line
        handle->data_buffer, DATA_BUFFER_SIZE);          // ← DELETE this line
    handle->ctrl_flags = 0x80;
    LOG_DEBUG_ID_SUB_U16(DBG_BUFFER_SIZE, (uint16_t)handle->data_size);
    if (handle->data_size == 0) {
        LOG_ERROR_ID(MSG_ERR_EMPTY_INPUT);
        return false;
    }
    LOG_DEBUG_ID_SUB(DBG_SETUP);
    handle->data_buffer[handle->data_size] = '\0';      // ← already done in CMD_IDLE
```

**`init_programmer_framed()` skeleton — code from line 115 onward is UNCHANGED:**
```c
// Precondition: handle->data_buffer populated with N decoded bytes,
//               handle->data_size == N, handle->data_buffer[N] == '\0'.
bool init_programmer_framed(firestarter_handle_t* handle) {
    handle->response_code = RESPONSE_CODE_OK;
    handle->operation_state = 0;
    handle->ctrl_flags = 0x80;

    LOG_DEBUG_ID_SUB_U16(DBG_BUFFER_SIZE, (uint16_t)handle->data_size);
    if (handle->data_size == 0) {
        LOG_ERROR_ID(MSG_ERR_EMPTY_INPUT);
        return false;
    }
    LOG_DEBUG_ID_SUB(DBG_SETUP);
    // data_buffer[data_size] = '\0' already done by caller (CMD_IDLE).
    if (!parse_json(handle)) {
        return false;
    }
    // Lines 127-143 UNCHANGED (mem_size debug, LOG_INFO identity echo, LOG_OK_ID, op_reset_timeout).
```

**Forward declaration to update** (`firestarter.cpp` line 28):
```c
// Change:
bool init_programmer(firestarter_handle_t* handle);
// To:
bool init_programmer_framed(firestarter_handle_t* handle);
```

---

### `firestarter/src/boards/rurp_serial_utils.cpp` — REUSE only, no source changes

**Role:** utility, streaming. No modifications to this file in Phase 51.

**Function signatures to call** (from `firestarter/include/rurp_serial_utils.h`):
```c
int rurp_communication_available();           // line 29 — byte-availability guard in CMD_IDLE
int rurp_communication_read_data(char* buffer); // line 37 — COBS decode-in-place + CRC8 verify + drain
// Do NOT call in Phase 51:
int rurp_communication_peak();               // line 33 — deleted from CMD_IDLE (D-05)
size_t rurp_communication_read_bytes(char* buffer, size_t size); // line 35 — deleted from init_programmer
```

**`rurp_communication_read_data()` contract summary** (`rurp_serial_utils.cpp` lines 100-191):
- Spins on `rurp_communication_available()` until `0x00` delimiter arrives.
- COBS-decodes in-place into `buffer[]` using 1-byte lookahead (`last_byte`) so CRC byte is never written to `buffer`.
- On any COBS violation or CRC8 mismatch: calls `_drain_to_delimiter()` and returns a negative code (`-1` underrun, `-2` overflow/drain, `-3` mid-run delimiter, `-4` CRC mismatch).
- On success: returns `(int)out` where `out` is the decoded payload byte count (excludes the CRC byte). Callers gate on `n > 0`.
- `DATA_BUFFER_SIZE` (512) is the internal overflow cap — the `-2` return path fires when `out >= DATA_BUFFER_SIZE`. This is the `CMD_FRAME_MAX` enforcement.

**`_drain_to_delimiter()` contract** (`rurp_serial_utils.cpp` lines 88-98):
```c
static void _drain_to_delimiter(void) {
    while (1) {
        while (rurp_communication_available() <= 0) {}
        int d = rurp_communication_read();
        if (d < 0 || (uint8_t)d == 0x00) {
            break;
        }
    }
}
```
Called internally by `rurp_communication_read_data()` on any failure — the `CMD_IDLE` handler does not need to call it separately.

---

### `firestarter/include/firestarter.h` — constant addition (config)

**Analog:** existing constant block, lines 18-41.

**Existing constant block pattern** (lines 18-41):
```c
#ifndef DATA_BUFFER_SIZE
#define DATA_BUFFER_SIZE 512
#endif

#define TIMEOUT_MS 1000

#define CMD_IDLE 0
#define CMD_READ 1
// ... (lines 24-41)
#define CMD_FW_VERSION 13
```

**New constant to add — `CMD_FRAME_MAX`:**
```c
// Phase 51: maximum decoded command-frame payload length.
// Equals DATA_BUFFER_SIZE (512) — the internal overflow cap in
// rurp_communication_read_data(). Defined here for constant-parity
// with constants.py (CLAUDE.md requirement). Sized from largest
// legitimate JSON command: ~422 bytes worst-case + 90 bytes headroom.
#define CMD_FRAME_MAX DATA_BUFFER_SIZE
```

Place immediately after the `DATA_BUFFER_SIZE` block (before `TIMEOUT_MS`). The `CMD_FRAME_MAX` check in `CMD_IDLE` is redundant with the decoder's internal `-2` overflow guard (RESEARCH §CMD_FRAME_MAX Sizing), but the constant is required for host/firmware parity documentation.

---

### `firestarter_app/firestarter/constants.py` — constant addition (config)

**Analog:** existing `BUFFER_SIZE`/`COMMAND_*` block (`constants.py` lines 21-57).

**Existing constant pattern** (lines 21-23):
```python
# Constants
BAUD_RATE = "250000"

BUFFER_SIZE = 512
LEONARDO_BUFFER_SIZE = 1024
```

**New constant to add — `CMD_FRAME_MAX`:**
```python
# Phase 51: maximum decoded command-frame payload length (bytes).
# Firmware sync: firestarter.h CMD_FRAME_MAX — CLAUDE.md constant-parity requirement.
# Sized from largest legitimate JSON command (~422 bytes) + headroom = 512.
CMD_FRAME_MAX = 512  # equals BUFFER_SIZE
```

Place in the `# Constants` block alongside `BUFFER_SIZE` (line 22). Update the comment on `BUFFER_SIZE` to note both constants' relationship:
```python
BUFFER_SIZE = 512  # Uno data-block buffer; also CMD_FRAME_MAX for command frames
```

---

### `firestarter_app/firestarter/serial_comm.py` — `send_json_command()` modification (service, request-response)

**Analog:** `firestarter_app/tests/test_cobs.py` `build_cobs_frame()` (lines 44-55) — shows the correct encode order. `serial_comm.py` `send_bytes()` (lines 134-148) — the unchanged atomic write primitive.

**Existing `send_bytes()` — UNCHANGED** (lines 134-148):
```python
def send_bytes(self, data_bytes: bytes) -> int:
    """Write raw bytes to the serial port and return the byte count written."""
    if not self.is_connected():
        raise SerialError("Not connected.")
    assert self.connection is not None
    try:
        written_bytes = self.connection.write(data_bytes)
        self.connection.flush()
        logger.debug(f"Sent {written_bytes} bytes to {self.port_name}.")
        return written_bytes if written_bytes is not None else 0
    except serial.SerialTimeoutException as e:
        raise SerialTimeoutError(f"Timeout writing to {self.port_name}: {e}") from e
    except serial.SerialException as e:
        raise SerialError(f"Serial error writing to {self.port_name}: {e}") from e
```

**Current `send_json_command()` to REPLACE** (lines 155-159):
```python
def send_json_command(self, command_dict: dict) -> int:
    """Serialise `command_dict` as compact JSON and send it over the serial port."""
    self._log_command_details(command_dict)
    json_data = json.dumps(command_dict, separators=(",", ":"))
    return self.send_string(json_data)
```

**Replacement (Phase 51 / FRAME-05):**
```python
def send_json_command(self, command_dict: dict) -> int:
    """Serialise ``command_dict`` as a COBS+CRC8 framed command (Phase 51 / FRAME-05).

    Frame contract (ADR §4.1/§4.3):
        [COBS(json_bytes + CRC8(json_bytes))][0x00]

    The full frame is assembled as one bytes object and passed to send_bytes()
    in a single call (SAFE-01 sub-claim B atomic-write mandate).
    """
    self._log_command_details(command_dict)
    json_bytes = json.dumps(command_dict, separators=(",", ":")).encode("ascii")
    crc = _crc8_ccitt(json_bytes)
    body = cobs_encode(json_bytes + bytes([crc]))
    frame = body + b"\x00"                      # atomic: one bytes object
    return self.send_bytes(frame)
```

**Encode order is critical — from `test_cobs.py` lines 52-55:**
```python
# CORRECT order (from test_cobs.py build_cobs_frame):
crc = _crc8_ccitt(payload)                     # CRC8 over RAW json_bytes first
body = cobs_encode(payload + bytes([crc]))      # THEN COBS-encode(payload + crc_byte)
# WRONG: cobs_encode first, then _crc8_ccitt — every frame fails firmware CRC8 verify
```

**Import change required** (extend the existing `from firestarter.frame_parser import` at lines 47-53):
```python
from firestarter.frame_parser import (  # noqa: F401  — re-exports for test_decoder.py
    MAGIC_PREAMBLE,
    LogMessage,
    Response,
    _crc8_ccitt,
    _decode_param,
    cobs_encode,        # ADD THIS — Phase 51
)
```

**Version probe framing (D-04):** The `_probe_port()` call at line 550 is:
```python
communicator.send_json_command({"state": COMMAND_FW_VERSION})
```
No change needed — `send_json_command()` wraps ALL commands including this probe after Phase 51. D-04 is satisfied automatically.

---

### `firestarter_app/tests/test_serial_comm.py` — new test functions (test, request-response)

**Analog:** `firestarter_app/tests/test_serial_comm.py` lines 132-146 (existing `send_*` tests) + `firestarter_app/tests/test_cobs.py` lines 44-55 (frame-assembly helper pattern).

**Existing test style to copy** (lines 132-146):
```python
def test_send_string_routes_through_send_bytes(make_comm) -> None:
    """send_string encodes ASCII bytes via send_bytes."""
    comm = make_comm()
    n = comm.send_string("hello", encoding="ascii")
    assert n == 5


def test_send_json_command_routes_through_send_string(make_comm) -> None:
    """send_json_command serialises the dict as compact JSON."""
    comm = make_comm()
    n = comm.send_json_command({"cmd": 2, "value": 42})
    assert n > 10
```

**`make_comm` fixture** (from `conftest.py` lines 127-145): builds a `SerialCommunicator` using `__new__` + injected `_FakeSerial` (BytesIO-backed). The `fake_serial.write()` records bytes and returns the byte count. Use `fake_serial` to capture the emitted frame bytes for assertion.

**New test functions to add:**

```python
# Required imports to add at top of test_serial_comm.py:
from firestarter.frame_parser import _crc8_ccitt, cobs_decode, cobs_encode


def test_send_json_command_emits_cobs_frame(make_comm, fake_serial) -> None:
    """send_json_command emits a well-formed COBS+CRC8 frame (FRAME-05)."""
    comm = make_comm()
    cmd = {"cmd": 2, "value": 42}
    comm.send_json_command(cmd)

    # Capture what was written to the fake serial
    import json
    fake_serial._buf.seek(0)
    written = fake_serial._buf.read()

    # Frame must end with 0x00 delimiter
    assert written[-1:] == b"\x00", "frame must end with 0x00 delimiter"

    # COBS body (everything before the delimiter) must contain no 0x00
    body = written[:-1]
    assert b"\x00" not in body, "COBS body must not contain 0x00"

    # Decode COBS body and verify CRC8 (ADR §4.3)
    decoded = cobs_decode(body)
    json_payload = decoded[:-1]
    rcvd_crc = decoded[-1]
    assert rcvd_crc == _crc8_ccitt(json_payload), "CRC8 mismatch after decode"
    assert json.loads(json_payload) == cmd


def test_send_json_command_atomic_frame(make_comm, fake_serial) -> None:
    """Frame is assembled as one bytes object — no split write of delimiter
    (SAFE-01 sub-claim B). Verified by inspecting the single write() call."""
    comm = make_comm()
    # Monkeypatch write to record call count
    write_calls = []
    original_write = fake_serial.write
    fake_serial.write = lambda data: (write_calls.append(data), original_write(data))[1]

    comm.send_json_command({"state": 13})

    # send_bytes() calls connection.write() exactly once with the full frame
    assert len(write_calls) == 1, "must be a single write() call (atomic frame)"
    assert write_calls[0][-1:] == b"\x00", "delimiter must be in the single write"


def test_send_json_command_version_probe_is_framed(make_comm, fake_serial) -> None:
    """CMD_FW_VERSION probe goes through framed path (D-04 — no plaintext escape)."""
    from firestarter.constants import COMMAND_FW_VERSION
    comm = make_comm()
    comm.send_json_command({"state": COMMAND_FW_VERSION})

    fake_serial._buf.seek(0)
    written = fake_serial._buf.read()

    # A framed command ends with 0x00; plain JSON starts with '{'
    assert written[-1:] == b"\x00", "probe must be COBS-framed (ends with 0x00)"
    assert written[:1] != b"{", "probe must NOT be raw JSON (no { prefix)"
```

---

## Shared Patterns

### COBS Primitives — Reuse Only
**Source (firmware):** `firestarter/src/boards/rurp_serial_utils.cpp` lines 88-191 (decode) + lines 204-276 (encode)
**Source (host):** `firestarter_app/firestarter/frame_parser.py` lines 58-128 (`cobs_encode`, `cobs_decode`, `_crc8_ccitt`)
**Apply to:** All Phase 51 changes. No new COBS algorithm — call existing functions.

Phase 51 is caller-side changes only. The primitives are proven and contract-frozen. "Don't hand-roll" rule applies to all five functions: `rurp_communication_read_data()`, `_drain_to_delimiter()`, `crc8_ccitt()`, `cobs_encode()`, `_crc8_ccitt()`.

### CRC8-Before-Parse Gate (V5 / §4.4)
**Source (firmware):** `rurp_serial_utils.cpp` lines 173-189 — CRC8 verify inside `rurp_communication_read_data()`, which returns `-4` on mismatch (drain already done).
**Apply to:** `firestarter.cpp` `CMD_IDLE` handler — gate on `n > 0` before calling `init_programmer_framed()`. Never call `parse_json()` when `n <= 0`.
```c
/* The only acceptable gate: */
if (n > 0) {
    /* safe to parse */
} else {
    /* n == 0 or n < 0: COBS/CRC/overflow failure; decoder already drained */
    LOG_ERROR_ID(MSG_ERR_BAD_FRAME);
}
```

### Atomic Write Mandate (SAFE-01 sub-claim B)
**Source (host):** `serial_comm.py` `send_bytes()` lines 134-148 — `write()` + `flush()` in one call.
**Apply to:** `send_json_command()` replacement. The entire frame (`body + b"\x00"`) must be a single `bytes` object passed to `send_bytes()`. Never: `send_bytes(body); send_bytes(b'\x00')`.

### Constant Parity (CLAUDE.md)
**Source:** `firestarter/include/firestarter.h` lines 18-41 (firmware) + `firestarter_app/firestarter/constants.py` lines 21-57 (host).
**Apply to:** `CMD_FRAME_MAX` — define in BOTH files in the same commit. The CLAUDE.md rule: "Constants/flag bits are duplicated between `firestarter_app/firestarter/constants.py` (Python) and `firestarter/include/firestarter.h` (C++)."

### Error ID for Bad Command Frame
**Source:** `firestarter/src/firestarter.cpp` lines 63, 117 — existing usage: `LOG_ERROR_ID(MSG_ERR_BAD_JSON)`, `LOG_ERROR_ID(MSG_ERR_EMPTY_INPUT)`.
**Apply to:** New error surface in `CMD_IDLE` for negative-return frames. If `MSG_ERR_BAD_FRAME` is added to `logging_id.h`, use it. If not, `MSG_ERR_EMPTY_INPUT` is the fallback. RESEARCH §Open Question 2 recommends adding `MSG_ERR_BAD_FRAME` — planner's call.

### PlatformIO Test Registration
**Source:** `firestarter/platformio.ini` lines 78-93.
**Apply to:** New `test_cobs_cmd_frame` directory — must be added to BOTH `test_filter` AND `build_flags` `-I` list. Failure to add to `test_filter` means the suite runs silently if not explicitly filtered.

**Pattern to replicate** (existing lines for `test_cobs_data_frame`):
```ini
test_filter =
    ...
    native/avr/test_cobs_data_frame
    native/avr/test_cobs_cmd_frame    # ADD

build_flags =
    ...
    -I test/native/avr/test_cobs_data_frame
    -I test/native/avr/test_cobs_cmd_frame    # ADD
```

---

## No Analog Found

All Phase 51 files have close analogs. No entries in this section.

---

## Metadata

**Analog search scope:** `firestarter/test/native/avr/`, `firestarter/src/`, `firestarter/include/`, `firestarter_app/firestarter/`, `firestarter_app/tests/`
**Files scanned:** 14 source files read directly
**Pattern extraction date:** 2026-06-02
