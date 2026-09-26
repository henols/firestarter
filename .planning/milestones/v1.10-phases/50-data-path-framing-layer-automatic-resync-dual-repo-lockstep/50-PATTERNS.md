# Phase 50: Data-Path Framing Layer + Automatic Resync (dual-repo lockstep) - Pattern Map

**Mapped:** 2026-06-01
**Files analyzed:** 7 (3 firmware + 4 host, per D-06 Option A)
**Analogs found:** 7 / 7 (all in-repo; the COBS encode/decode pair has no direct analog — nearest byte-loop patterns assigned)

> Scope is **D-06 Option A** (operator-locked): re-frame the WRITE-receive path
> (`rurp_communication_read_data`) + rewrite the dormant `rurp_communication_write` as its
> COBS mirror; **leave EPROM reads on `MSG_DATA_CHUNK`** (the `[0xAA55AA55]…[0x0A]` log/telemetry
> frame is UNCHANGED). Do NOT touch `_firestarter_emit_frame` / `_firestarter_emit_frame_wide` /
> `rurp_log_id_wide` / the host magic-preamble RX demux in `_read_and_parse_lines`.

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `firestarter/src/boards/rurp_serial_utils.cpp` (rewrite `rurp_communication_read_data` ~44-79) | transport (decode) | streaming, request-response | self — old `rurp_communication_read_data` + `_firestarter_emit_frame` byte/CRC discipline (same file ~109-184) | role-match (new COBS algo) |
| `firestarter/src/boards/rurp_serial_utils.cpp` (rewrite `rurp_communication_write` ~81-93) | transport (encode) | streaming, request-response | `_firestarter_emit_frame` byte-emit + CRC8 loop (same file 138-184) | role-match (new COBS algo) |
| `firestarter/src/operation_utils.cpp` (`case '#'` ~159-171) | dispatch/middleware | event-driven (marker demux) | self — `case '#'` is the unchanged error surface; `default:` consume-one-byte resync (172-174) | exact (surface preserved) |
| `firestarter/test/native/avr/test_messages/` (new resync Unity case) | test | streaming (fault-injection) | `test_rurp_log_id.cpp` (`OverloadedMethod(... write ...)` mock; needs new `read`/`available` queued mock) | role-match (write mock exists, read mock new) |
| `firestarter_app/firestarter/frame_parser.py` (add `cobs_encode`/`cobs_decode`) | utility (codec) | transform | `_crc8_ccitt` / `_build_crc8_table` / `_decode_param` byte-loop leaf functions (same file 28-109) | role-match (new COBS algo) |
| `firestarter_app/firestarter/eprom_operations.py` (`_main_phase_send_data` ~357-391) | service (TX) | streaming, request-response | self — existing `b"#" + len_u16 + xor + chunk` atomic send (377-391) | exact (contents-only change) |
| `firestarter_app/firestarter/serial_comm.py` (`send_bytes` ~134-148) | service (TX) | request-response | self — already atomic `write`+`flush` | exact (NO change; reuse as-is) |
| `firestarter_app/tests/` (new `test_cobs.py`) | test | transform (round-trip + fault-injection) | `tests/test_decoder.py` + `conftest.py` `_FakeSerial`/`build_frame` | role-match |

## Pattern Assignments

### `firestarter/src/boards/rurp_serial_utils.cpp` — rewrite `rurp_communication_read_data()` (decode, the load-bearing change)

**Analog:** self (old function 44-79, to be replaced) + the byte-emit/CRC discipline of `_firestarter_emit_frame` (138-184).

**OLD code being replaced** (lines 44-79) — note the literal SC1 cascade source (`timeout_ms = 2000`, 61-69) and the per-byte XOR (71-77):
```c
int rurp_communication_read_data(char* buffer) {
    uint8_t size_buf[2];
    if (rurp_communication_read_bytes((char*)size_buf, 2) != 2) { return -1; }
    size_t data_size = (size_buf[0] << 8) | size_buf[1];        // <-- len_u16: REMOVE
    ...
    unsigned long timeout_ms = 2000;   // <-- the 2 s cascade source SC1 targets: REMOVE
    while (len < data_size) { ... len += rurp_communication_read_bytes(...); }
    uint8_t checksum = 0;
    for (size_t i = 0; i < len; i++) { checksum ^= buffer[i]; }   // <-- XOR: REPLACE with CRC8
    if (checksum != checksum_rcvd) { return -4; }
    return len;
}
```

**Reuse UNCHANGED — the CRC8 PROGMEM table + accessor** (lines 109-131, then 129-131):
```c
static const uint8_t CRC8_TABLE[256] PROGMEM = { 0x00, 0x07, 0x0E, 0x09, ... };
static uint8_t crc8_ccitt(uint8_t crc, uint8_t b) {
    return pgm_read_byte(&CRC8_TABLE[crc ^ b]);
}
```

**Byte-read primitives to use** (same file, do NOT use `readBytes` — Pitfall 4):
```c
int rurp_communication_available();   // line 28 — SERIAL_PORT.available()
int rurp_communication_read();        // line 32 — SERIAL_PORT.read() (one byte)
int rurp_communication_peak();        // line 36 — SERIAL_PORT.peek()
```

**New decode shape (decode-in-place, RESEARCH Pattern 2 + Pattern 3 directive):**
- Read bytes one at a time via `rurp_communication_read()`, decode COBS incrementally into `buffer[out++]` (write cursor never overtakes read cursor → no second buffer).
- Cap `out` at `DATA_BUFFER_SIZE`; return `-2` on overflow (preserves the existing too-large guard at old line 56-58).
- Last decoded byte is the CRC8: recompute `crc8_ccitt` over `buffer[0..out-2]`, compare to `buffer[out-1]`; mismatch → error.
- **MANDATORY (Pattern 3 / D-06 corrupted-`#` directive):** on ANY COBS-decode or CRC8 failure, *consume bytes up to and including the next `0x00`* before returning the negative code, so the RX cursor is re-anchored at a frame boundary. Never early-return leaving a partial frame.
- Keep the negative-code contract (`res < 0`) — callers only check `res < 0` (Assumption A4); specific codes are only logged.

---

### `firestarter/src/boards/rurp_serial_utils.cpp` — rewrite `rurp_communication_write()` (encode, dormant mirror)

**Analog:** `_firestarter_emit_frame` (138-184) — the canonical "single-byte writes + running CRC8 + `.flush()` at end" discipline. Copy this byte-emit cadence; swap the magic-preamble/len framing for COBS + `0x00`.

**OLD code being replaced** (lines 81-93) — XOR + `len_u16` prefix to drop:
```c
size_t rurp_communication_write(const char* buffer, size_t size) {
    uint8_t checksum = 0;
    for (size_t i = 0; i < size; i++) { checksum ^= buffer[i]; }
    SERIAL_PORT.write(size >> 8);     // <-- len_u16: REMOVE
    SERIAL_PORT.write(size & 0xFF);   // <-- len_u16: REMOVE
    SERIAL_PORT.write(checksum);      // <-- XOR: REPLACE with CRC8, COBS-encoded
    size_t bytes = SERIAL_PORT.write(buffer, size);
    SERIAL_PORT.flush();
    return bytes;
}
```

**Emit/CRC discipline to mimic** (from `_firestarter_emit_frame`, 164-183):
```c
uint8_t crc = 0;
SERIAL_PORT.write(id);            crc = crc8_ccitt(crc, id);
for (uint8_t i = 0; i < param_count; i++) {
    uint8_t b = params[i];
    SERIAL_PORT.write(b);         crc = crc8_ccitt(crc, b);
}
SERIAL_PORT.write(crc);           // CRC byte
SERIAL_PORT.write((uint8_t)0x0A); // (here: 0x00 delimiter instead, COBS-encoded body before it)
SERIAL_PORT.flush();
```

**New encode shape (streaming COBS, RESEARCH Pattern 1):** compute `crc8_ccitt` over `buffer[0..size-1]`; stream COBS run-codes + run-bytes directly to `SERIAL_PORT.write()` over the logical stream `[buffer .. crc]` (CRC byte folded in as the (N+1)th payload byte per ADR §4.3); terminate with a single `0x00`; `SERIAL_PORT.flush()`. ~6 B stack, no second buffer (FRAME-03). Handle the 254-run / phantom-zero edges (Pitfall 2) and the all-`0x00` blank-EPROM case (each zero → `0x01` run code).

---

### `firestarter/src/operation_utils.cpp` — `case '#'` (~159-171, surface UNCHANGED)

**Analog:** self — this is the error surface D-01 reuses; do NOT change its shape.

**Excerpt (159-171) — keep `res < 0 → OP_MSG_ERROR`; only adjust the `available() < 4` precheck to be delimiter-driven (planner detail):**
```c
case '#': {  // Data packet
    if (rurp_communication_available() < 4) { return OP_MSG_INCOMPLETE; }  // <-- '4' is len-era; revisit for delimiter-driven read
    rurp_communication_read();                                  // consume '#'
    int res = rurp_communication_read_data(handle->data_buffer);  // REWRITTEN (above)
    if (res < 0) {
        LOG_ERROR_ID_U16(MSG_ERR_DATA_ERR_N, (uint16_t)res);    // fail-fast, no 2 s hang (D-01)
        return OP_MSG_ERROR;
    }
    handle->data_size = res;
    return OP_MSG_DATA;
}
```

**Corrupted-`#` resync mechanism (RESEARCH Pattern 3, VALIDATED)** — the `default:` arm already self-heals a flipped marker by consuming one junk byte per loop (172-174):
```c
default:
    rurp_communication_read();   // discard one junk byte, loop continues
    break;
```
Combined with the rewritten reader's drain-to-`0x00`, a flipped marker re-anchors on the next delimiter and never strands the parser. **Do NOT add new marker handling — the existing two arms (the `case '#'` reader + this `default`) are sufficient once the reader drains-on-error.**

> Note the `'D'`/"DONE" arm (148-157) consumes 4 bytes on a partial/false match — a known residual risk the comment flags; out of Phase 50 scope, do not change.

---

### `firestarter/test/native/avr/test_messages/` — new Unity resync decoder case (D-02)

**Analog:** `test_rurp_log_id.cpp` (the only suite in this dir). It mocks **only** `Serial.write`; the decoder test needs a **new** `Serial.read`/`available` queued-byte mock helper (RESEARCH Wave-0 gap).

**Existing write-mock pattern to extend** (test_rurp_log_id.cpp 52-67):
```cpp
void setUp(void) {
    ArduinoFakeReset();
    captured.clear();
    When(OverloadedMethod(ArduinoFake(Serial), write, size_t(uint8_t)))
        .AlwaysDo([](uint8_t b) -> size_t { captured.push_back(b); return (size_t)1; });
    When(Method(ArduinoFake(Serial), flush)).AlwaysReturn();
}
```

**New mock helper to ADD (drive a queued byte vector for `read`/`available`/`peek`):** mirror the above with `When(OverloadedMethod(ArduinoFake(Serial), read, int(void)))` popping from a `std::vector<uint8_t>` front-cursor, plus `When(Method(ArduinoFake(Serial), available))` returning `(remaining)` and `peek` returning the front byte. Feed `[garbled frame][0x00][valid frame][0x00]`; assert (a) first `rurp_communication_read_data` call returns `res < 0` AND the read cursor is left at the start of the valid frame (drain-to-`0x00` worked), (b) a second call returns the correct decoded length with `data_buffer` matching the expected payload (SC2 bounded recovery, not mere detection).

**Reference CRC discipline for expected values** (test_rurp_log_id.cpp 76-85) — the table-free `ref_crc8` recompute pattern is reusable for asserting the expected CRC8 byte independently of the production table.

**Suite wiring** (test_rurp_log_id.cpp 251-263): add `RUN_TEST(...)` lines in `main()`. New suites can also be dropped under a new `test/native/avr/<dirname>/` per the firmware CLAUDE.md "Reuse pattern for future native tests."

---

### `firestarter_app/firestarter/frame_parser.py` — add `cobs_encode` / `cobs_decode` (CONTEXT: placement is Claude's discretion; this file is the recommended home — stdlib-only, testable without serial I/O)

**Analog:** the existing leaf byte-loop functions in this file — `_build_crc8_table` (28-44), `_crc8_ccitt` (50-55), `_decode_param` (58-109). Same module role: pure transforms over `bytes`, no I/O, raise `ValueError` on malformed input.

**Reuse UNCHANGED (D-05 / CRC-01):**
```python
def _crc8_ccitt(data: bytes) -> int:
    """Compute CRC8-CCITT (poly 0x07, seed 0x00) over `data` via lookup table."""
    crc = 0
    for byte in data:
        crc = _CRC8_CCITT_TABLE[crc ^ byte]
    return crc
```

**Decode helper to add** (RESEARCH Code Examples — note the implicit-zero / 254-run edges, and `ValueError` on `0x00` in body, matching the module's `_decode_param` raise-on-malformed style):
```python
def cobs_decode(encoded: bytes) -> bytes:
    """Decode a COBS body (NO trailing 0x00 delimiter). Raises ValueError on malformed input."""
    out = bytearray()
    i, n = 0, len(encoded)
    while i < n:
        code = encoded[i]
        if code == 0:
            raise ValueError("0x00 inside COBS body")
        i += 1
        end = i + code - 1
        if end > n:
            raise ValueError("COBS run exceeds buffer")
        out.extend(encoded[i:end]); i = end
        if code < 0xFF and i < n:
            out.append(0)
    return bytes(out)
```
**`cobs_encode`** is the inverse (RESEARCH Pattern 1); build a `bytearray`, scan runs of ≤254 non-zero bytes. Type hints + docstring required (the strict-8 mypy set includes `frame_parser.py` — RESEARCH Project Constraints).

---

### `firestarter_app/firestarter/eprom_operations.py` — `_main_phase_send_data` (~357-391, change CONTENTS only)

**Analog:** self — the existing atomic send (377-391). The build/send shape is already atomic; only the frame *contents* change.

**OLD code (377-390) — `len_u16` + XOR to replace:**
```python
data_chunk = file_handle.read(buffer_size)
checksum = functools.reduce(operator.xor, data_chunk, 0)
header = b"#" + len(data_chunk).to_bytes(2, "big") + checksum.to_bytes(1)
...
self.comm.send_bytes(header + data_chunk)   # ONE call — atomic (preserve this)
```

**NEW contents (RESEARCH / CONTEXT D-06; atomic-write mandate — keep the single `send_bytes`):**
```python
crc = _crc8_ccitt(data_chunk)                       # from frame_parser (UNCHANGED table)
body = cobs_encode(data_chunk + bytes([crc]))       # NEW helper
frame = b"#" + body + b"\x00"                        # one bytes object — delimiter NOT split
self.comm.send_bytes(frame)
```
Add the import (`from firestarter.frame_parser import cobs_encode, _crc8_ccitt` or via a public re-export). The `functools`/`operator` imports (lines 10, 13) become unused if no other XOR caller remains — check before removing (ruff will flag). Update the stale comment block (384-389) that describes the `[len_u16][xor]` header.

---

### `firestarter_app/firestarter/serial_comm.py` — `send_bytes` (~134-148, NO change)

**Analog:** self — already satisfies the atomic-write mandate (single `write` + `flush`). Reuse as-is; the new `frame` from `_main_phase_send_data` flows through unchanged.
```python
def send_bytes(self, data_bytes: bytes) -> int:
    ...
    written_bytes = self.connection.write(data_bytes)
    self.connection.flush()
    ...
```
**Do NOT touch `_read_and_parse_lines` (224-336)** — it is ring-fenced (GATE-1.8d, v1.9 RCA territory, header comment 213-223) AND carries the unchanged `MSG_DATA_CHUNK` read path (D-06 Option A). The COBS data frame is host→fw (send) only; there is no host RX decode of it.

---

### `firestarter_app/tests/test_cobs.py` (new, D-02 host pytest)

**Analog:** `tests/test_decoder.py` + `conftest.py`.

**Round-trip / pure-transform style** — test `cobs_encode`/`cobs_decode`/`_crc8_ccitt` directly on `bytes` (no serial), as `test_decoder.py` does for `_decode_id_frame`. Cover: round-trip, all-zero 512 B payload (FRAME-04 + Pitfall 2), 254-run boundary, CRC8-over-payload (CRC-01).

**Fault-injection / resync (SC2 bounded recovery)** — assert `cobs_decode` raises a clean `ValueError` on a corrupt-CRC frame and on a flipped/missing `0x00`, AND that the **next** valid frame in a `[corrupt][0x00][valid][0x00]` stream decodes correctly (recovery within one frame, not mere detection). Assert no blocking/2 s hang (wall-clock bound or no blocking read entered).

**Fixtures to reuse** (conftest.py): `_FakeSerial` (65-118, BytesIO-backed `read(n)`/`feed`), `fake_serial` (121-124), `make_comm` (127+), and the `build_frame` helper pattern (52-62) — adapt `build_frame` into a `build_cobs_frame(payload)` that emits `b"#" + cobs_encode(payload + bytes([_crc8_ccitt(payload)])) + b"\x00"`. New COBS code must pass `ruff` + strict `mypy` + keep coverage ≥ 70 (near-zero headroom — add tests with the code).

## Shared Patterns

### CRC8-CCITT (reused UNCHANGED, both repos — D-05 / CRC-01)
**Source (fw):** `firestarter/src/boards/rurp_serial_utils.cpp:107-128` (`CRC8_TABLE` PROGMEM + `crc8_ccitt(crc, b)` accessor).
**Source (host):** `firestarter_app/firestarter/frame_parser.py:28-55` (`_build_crc8_table` + `_crc8_ccitt`).
**Apply to:** every framed payload, both encode and decode, both repos. Poly 0x07, seed 0x00, no reflection, no final XOR — byte-compatible; do NOT introduce a new CRC routine. Pinned by `test_crc_polynomial_smoke` (fw, test_rurp_log_id.cpp:185-201) and the host `test_decoder.py`/`_ref_crc8_ccitt`.

### Single-byte writes + `.flush()` at end (firmware serial discipline)
**Source:** `_firestarter_emit_frame` (`rurp_serial_utils.cpp:135-181`).
**Apply to:** the rewritten `rurp_communication_write` COBS encoder — same cadence (running CRC, per-byte `SERIAL_PORT.write`, terminate, `flush`).

### Atomic-write mandate (host)
**Source:** `serial_comm.py:send_bytes` (134-148) — single `write` + `flush`; called once with one `bytes` object by `_main_phase_send_data` (390).
**Apply to:** the new `frame = b"#" + cobs_body + b"\x00"` — never split the `0x00` delimiter into a second write (ADR §4.1 / SAFE-01).

### Drain-to-`0x00` on error (both receivers — FRAME-02 / Pattern 3)
**Source:** RESEARCH Pattern 3 directive (no prior analog — this is the new resync invariant).
**Apply to:** fw `rurp_communication_read_data` (consume up to AND including next `0x00` before returning `res < 0`) and host `cobs_decode` callers (raise, advance past next `0x00`). Bounded to one frame.

### Marker-dispatched MAIN-state loop (preserved — D-04)
**Source:** `operation_utils.cpp:134-186` (`op_get_message`); the `default:` consume-one-byte arm (172-174) is the marker-corruption self-heal.
**Apply to:** keep unchanged; only the post-`#` payload framing changes.

## No Analog Found

| File / unit | Role | Data Flow | Reason |
|-------------|------|-----------|--------|
| COBS encode/decode algorithm (both repos) | codec | transform | No existing COBS in either repo; nearest patterns are the CRC8 table-driven byte loops + `_firestarter_emit_frame` emit discipline (assigned above). Algorithm comes from ADR §4.1 + v1.9-COBS-DECISION §3 reference snippet, not from a codebase analog. |
| fw `Serial.read`/`available` queued-byte Unity mock | test fixture | — | `test_messages/` currently mocks only `Serial.write`; the read mock helper must be authored new (extend the `OverloadedMethod(... write ...)` pattern). |

## Metadata

**Analog search scope:** `firestarter/src/boards/`, `firestarter/src/`, `firestarter/test/native/avr/` (test_messages, test_data_input, test_read_timing); `firestarter_app/firestarter/` (frame_parser, serial_comm, eprom_operations), `firestarter_app/tests/` (test_decoder, conftest).
**Files scanned:** 11 source/test files read end-to-end or in targeted ranges + 2 directory listings.
**Branch:** `v1.10-serial-transport-hardening` (both sub-repos).
**Pattern extraction date:** 2026-06-01
