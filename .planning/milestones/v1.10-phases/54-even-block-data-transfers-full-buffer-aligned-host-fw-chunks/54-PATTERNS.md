# Phase 54: Even-Block Data Transfers — Pattern Map

**Mapped:** 2026-06-04
**Files analyzed:** 9 new/modified files
**Analogs found:** 9 / 9

---

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `firestarter/src/boards/rurp_serial_utils.cpp` | service (codec) | request-response | self (existing function) | exact — edit in-place |
| `firestarter/src/boards/rurp_serial_utils.h` | config/header | request-response | self (existing declaration) | exact — edit in-place |
| `firestarter/src/firestarter.cpp` | controller | request-response | self (existing call site ~line 176) | exact — edit in-place |
| `firestarter/src/operation_utils.cpp` | service | request-response | self (existing call site ~line 164) | exact — edit in-place |
| `firestarter/include/firestarter.h` | config/header | — | self (existing `FW_VERSION` macro ~line 35) | exact — edit in-place |
| `firestarter_app/firestarter/serial_comm.py` | service | request-response | self (existing `_probe_port` ~lines 619–624) | exact — edit in-place |
| `firestarter_app/firestarter/eprom_operations.py` | service | CRUD | self (existing `_calculate_buffer_size` ~lines 163–179) | exact — edit in-place |
| `firestarter/test/native/avr/test_frame_vectors/test_frame_vectors.cpp` | test | — | self (existing `test_vector_decode_leg`) + `test_cobs_data_frame.cpp` | exact — extend in-place |
| `firestarter_app/tests/test_even_block.py` | test | — | `firestarter_app/tests/test_frame_vectors.py` (`TestPerBoardBufferNegotiation`, `TestHostChunkFitsFirmwareDecodeCap`) | role-match |

---

## Pattern Assignments

### `firestarter/src/boards/rurp_serial_utils.cpp` (service, decode)

**Analog:** self — the existing `rurp_communication_read_data` function (lines 128–241)

**Current function signature** (line 128):
```c
int rurp_communication_read_data(char* buffer) {
```

**Current PUSH macro** (lines 144–155) — this is the block to change:
```c
#define PUSH(b_)                                                   \
    do {                                                           \
        if (has_last) {                                            \
            if (out >= DATA_BUFFER_SIZE - 1) {                     \
                _drain_to_delimiter();                             \
                return -2;                                         \
            }                                                      \
            buffer[out++] = (char)last_byte;                       \
        }                                                          \
        last_byte = (b_);                                          \
        has_last = true;                                           \
    } while (0)
```

**After Phase 54:** The signature gains `size_t cap`; the hardcoded `DATA_BUFFER_SIZE - 1` literal inside PUSH becomes `cap`:
```c
int rurp_communication_read_data(char* buffer, size_t cap) {
    ...
#define PUSH(b_)                                \
    do {                                        \
        if (has_last) {                         \
            if (out >= cap) {                   \
                _drain_to_delimiter();          \
                return -2;                      \
            }                                   \
            buffer[out++] = (char)last_byte;    \
        }                                       \
        last_byte = (b_);                       \
        has_last = true;                        \
    } while (0)
```

No other logic in the function changes. The `#undef PUSH` at line 220 and everything after it (CRC verification, return) remain identical.

---

### `firestarter/src/boards/rurp_serial_utils.h` (header)

**Analog:** self — existing declaration at line 37

**Current declaration** (line 37):
```c
int rurp_communication_read_data(char* buffer);
```

**After Phase 54:**
```c
int rurp_communication_read_data(char* buffer, size_t cap);
```

No other lines in the header change. Note: `size_t` is already used by `rurp_communication_read_bytes` (line 35); no new include needed.

---

### `firestarter/src/firestarter.cpp` (controller — CMD_IDLE call site)

**Analog:** self — existing call at line 176 in `loop()`

**Current call site** (lines 176–185):
```c
int n = rurp_communication_read_data(handle.data_buffer);
if (n > 0) {
    handle.data_size = (uint32_t)n;
    /* CR-01 belt-and-suspenders: the decoder caps n at
     * DATA_BUFFER_SIZE-1 (PUSH guard), so n < DATA_BUFFER_SIZE
     * always holds post-fix and data_buffer[n] is in-bounds.
     * This guard documents the invariant at the write site and
     * protects against any future caller that forgets the cap. */
    if (n < DATA_BUFFER_SIZE) {
        handle.data_buffer[n] = '\0';
    }
```

**After Phase 54:** pass `DATA_BUFFER_SIZE - 1` as `cap` — the NUL-slot reservation stays intact:
```c
int n = rurp_communication_read_data(handle.data_buffer, DATA_BUFFER_SIZE - 1);
```

The `if (n < DATA_BUFFER_SIZE) { handle.data_buffer[n] = '\0'; }` guard at line 184 remains unchanged (it is still correct and intentional for this path).

---

### `firestarter/src/operation_utils.cpp` (service — MAIN data call site)

**Analog:** self — existing call inside `case '#':` at lines 163–170

**Current call site** (lines 163–170):
```c
case '#': {  // Data packet
    // Phase 50 Plan 02: COBS framing is delimiter-driven (no fixed
    // header size).  Execution reaches here only after peak()=='#'
    // confirmed available()>=1; the inner guard is unreachable.
    rurp_communication_read();  // consume '#'
    int res = rurp_communication_read_data(handle->data_buffer);
    if (res < 0) {
        LOG_ERROR_ID_U16(MSG_ERR_DATA_ERR_N, (uint16_t)res);
        return OP_MSG_ERROR;
    }
    handle->data_size = res;
    return OP_MSG_DATA;
}
```

**After Phase 54:** pass `DATA_BUFFER_SIZE` as `cap` — no NUL write follows on this path:
```c
int res = rurp_communication_read_data(handle->data_buffer, DATA_BUFFER_SIZE);
```

No NUL write after this call (confirmed from research trace — consumers use `handle->data_buffer[i]` index only). Nothing else in the case block changes.

---

### `firestarter/include/firestarter.h` (config/header — FW_VERSION macro)

**Analog:** self — existing `FW_VERSION` macro at lines 33–35

**Current macro** (lines 26–35):
```c
/* FW identity string: "<version>:<board>:<data_buffer_size>". The trailing
 * data-buffer-size field lets the host size its host->fw data chunks to the
 * board's ACTUAL decode capacity (chunk + CRC8 <= DATA_BUFFER_SIZE-1), so a
 * 1024-buffer board (Leonardo) can use ~1022-byte chunks while a 512-buffer
 * board (Uno) uses 510 — no hardcoded per-board map on the host. Backward
 * compatible: older hosts split on ':' and read only [version]/[board],
 * ignoring the trailing field. (#transport-protocol-verify / Phase 53 1K) */
#define FS_STRINGIFY2(x) #x
#define FS_STRINGIFY(x) FS_STRINGIFY2(x)
#define FW_VERSION VERSION ":" RURP_BOARD_NAME ":" FS_STRINGIFY(DATA_BUFFER_SIZE)
```

**After Phase 54:** append a 4th `:<maxchunk>` field. Because Candidate A makes the MAIN-path cap equal to `DATA_BUFFER_SIZE` exactly, both fields use the same macro:
```c
#define FW_VERSION VERSION ":" RURP_BOARD_NAME ":" FS_STRINGIFY(DATA_BUFFER_SIZE) ":" FS_STRINGIFY(DATA_BUFFER_SIZE)
// emits e.g. "3.0.0b8:uno:512:512" or "3.0.0b8:leonardo:1024:1024"
```

Update the comment block above the macro to reflect that field 4 is `<maxchunk>` — the MAIN-path decode capacity the host should use as chunk size, eliminating the `buf−2` arithmetic.

---

### `firestarter_app/firestarter/serial_comm.py` (service — `SerialCommunicator.__init__` + `_probe_port`)

**Analog:** self — existing `firmware_buffer_size` attribute (lines 117–118) and `_probe_port` parse block (lines 619–624)

**Current `__init__` attribute** (lines 117–118):
```python
# Phase 53: the firmware advertises its DATA_BUFFER_SIZE in the FW identity
# string ("<ver>:<board>:<bufsize>"); _probe_port populates this so the host
# can size host->fw data chunks to the board's actual decode capacity
# (chunk + CRC8 <= bufsize-1). None until probed / for pre-advertise firmware.
self.firmware_buffer_size: Optional[int] = None
```

**After Phase 54:** add the new attribute immediately after `firmware_buffer_size`, mirroring the same pattern:
```python
self.firmware_buffer_size: Optional[int] = None
# Phase 54 (EVEN-01): firmware advertises effective MAIN-path decode capacity in
# field 4 ("<ver>:<board>:<buf>:<maxchunk>"). Host uses this value directly as
# the write/verify chunk size — no arithmetic. None until probed (D-05: no
# fallback to buf-2; old firmware raises FirmwareOutdatedError in _calculate_buffer_size).
self.firmware_max_chunk: Optional[int] = None
```

**Current `_probe_port` parse block** (lines 619–624):
```python
fw_payload = fw_msg.split("FW:", 1)[-1].strip()
fw_fields = fw_payload.split(":")
if len(fw_fields) >= 3 and fw_fields[2].strip().isdigit():
    communicator.firmware_buffer_size = int(
        fw_fields[2].strip()
    )
```

**After Phase 54:** add the `firmware_max_chunk` parse immediately after the `firmware_buffer_size` assignment, using the same `.isdigit()` guard pattern:
```python
fw_payload = fw_msg.split("FW:", 1)[-1].strip()
fw_fields = fw_payload.split(":")
if len(fw_fields) >= 3 and fw_fields[2].strip().isdigit():
    communicator.firmware_buffer_size = int(
        fw_fields[2].strip()
    )
if len(fw_fields) >= 4 and fw_fields[3].strip().isdigit():
    communicator.firmware_max_chunk = int(fw_fields[3].strip())
```

The `.isdigit()` guard is the existing validation pattern for all `fw_fields[N]` integer parses — copy it verbatim. Do not change any other part of `_probe_port`.

---

### `firestarter_app/firestarter/eprom_operations.py` (service — `_calculate_buffer_size`)

**Analog:** self — existing `_calculate_buffer_size` method (lines 163–179)

**Current implementation** (lines 163–179):
```python
def _calculate_buffer_size(self) -> int:
    # For write/verify, we use a "pull" protocol where the Arduino requests a
    # data block when it's ready. The chunk must fit the firmware COBS decoder's
    # committed-payload cap: the decoded payload is data_chunk + CRC8, and
    # rurp_communication_read_data commits at most DATA_BUFFER_SIZE-1 bytes
    # (CR-01 NUL-slot reservation). A full-buffer chunk overflows -> "Data
    # error: -2" (bench-confirmed, Phase 53).
    #
    # The firmware advertises its DATA_BUFFER_SIZE in the FW identity string;
    # _probe_port stores it on the communicator. Size the chunk to that board's
    # actual capacity (e.g. Leonardo 1024 -> 1022, Uno 512 -> 510), so the host
    # is self-correcting with no hardcoded per-board map. Fall back to the safe
    # MAX_DATA_CHUNK (BUFFER_SIZE - 2 = 510) for pre-advertise firmware.
    fw_buf = getattr(self.comm, "firmware_buffer_size", None) if self.comm else None
    if fw_buf is not None and fw_buf >= 3:
        return fw_buf - 2  # reserve 1 byte CRC8 + 1 byte decoder NUL slot
    return MAX_DATA_CHUNK
```

**After Phase 54:** replace the entire body with the `firmware_max_chunk` read. The `getattr(self.comm, …, None)` pattern, the `if self.comm else None` guard, and the `FirmwareOutdatedError` exception class are all already established in this codebase:
```python
def _calculate_buffer_size(self) -> int:
    # Phase 54 (EVEN-01/D-04): read the firmware-advertised max-chunk field
    # (4th ':' field of "<ver>:<board>:<buf>:<maxchunk>") — no arithmetic, no
    # per-board constant. The firmware MAIN-path decode cap is DATA_BUFFER_SIZE
    # (Candidate A NUL-skip); <maxchunk> == DATA_BUFFER_SIZE exactly.
    # D-05: no fallback; host and firmware must be upgraded together (lockstep).
    max_chunk = getattr(self.comm, "firmware_max_chunk", None) if self.comm else None
    if max_chunk is not None and max_chunk >= 1:
        return max_chunk
    raise FirmwareOutdatedError(
        "Firmware does not advertise a max-chunk capacity field. "
        "Please upgrade the firmware using 'firestarter fw --install'."
    )
```

`FirmwareOutdatedError` is already imported in `eprom_operations.py` (Phase 38 STRUCT-04). Do not add a new import. Also add a comment next to `MAX_DATA_CHUNK` in `constants.py` marking it as obsolete (leave the constant in place per RESEARCH D-04 note).

---

### `firestarter/test/native/avr/test_frame_vectors/test_frame_vectors.cpp` (test — firmware Unity)

**Analog:** self — the existing `test_vector_decode_leg` function (lines 226–258) and the overall test structure

**Current `test_vector_decode_leg` skip guard** (lines 232–235):
```cpp
/* Skip encoder-only vectors (decode leg capped at 511 bytes, CR-01). */
if (vec.payload_len > DATA_BUFFER_SIZE - 1) {
    continue;
}
```

And the existing decode call at line 247:
```cpp
int res = rurp_communication_read_data(data_buffer);
```

**What must change:** the existing `test_vector_decode_leg` must be updated — it now calls the new two-argument signature. The skip guard must also be updated: after Phase 54 the MAIN-path cap is `DATA_BUFFER_SIZE` (not `DATA_BUFFER_SIZE - 1`), so vectors with `payload_len == DATA_BUFFER_SIZE` (512 or 1024) are now valid on the MAIN path but must still overflow on the CMD_IDLE path.

The established pattern for adding new test functions is shown by `test_crc8_known_answer`, `test_vector_encode_leg`, `test_vector_decode_leg` — each is a standalone `void test_*(void)` function, registered via `RUN_TEST(...)` in `main()`.

**New tests to add** (three new `void test_*(void)` functions following the existing style):

1. **`test_vector_decode_leg_main_path`** — calls `rurp_communication_read_data(data_buffer, DATA_BUFFER_SIZE)` (MAIN-path cap) for ALL vectors including 512/1024-byte ones; asserts round-trip success. Mirrors `test_vector_decode_leg` but with `cap=DATA_BUFFER_SIZE` and no skip guard on 512-byte vectors.

2. **`test_cmd_idle_overflow_at_full_block`** — calls `rurp_communication_read_data(data_buffer, DATA_BUFFER_SIZE - 1)` (CMD_IDLE cap) with a 512-byte all-`0xFF` payload (use `VEC_512_ALL_FF` frame bytes from `FRAME_VECTORS`); asserts return value `< 0` (overflow, -2). This pins the CMD_IDLE NUL-slot reservation (CR-01) and guards against the Pitfall 1 regression.

3. **`test_even_block_no_remainder`** — no serial mock needed; pure arithmetic assertion:
   ```cpp
   void test_even_block_no_remainder(void) {
       TEST_ASSERT_EQUAL_UINT32(0, (uint32_t)(65536 % DATA_BUFFER_SIZE));
   }
   ```

The existing `test_vector_decode_leg` must also be updated: change its `rurp_communication_read_data(data_buffer)` call to `rurp_communication_read_data(data_buffer, DATA_BUFFER_SIZE - 1)` (CMD_IDLE signature). The skip guard `payload_len > DATA_BUFFER_SIZE - 1` remains correct for this test (it tests the CMD_IDLE cap). Add a comment explaining the cap distinction.

**setUp/tearDown pattern** (lines 144–171): copy verbatim for the new test functions; no changes needed to the shared test state or mock wiring.

**main() additions**: add `RUN_TEST(test_vector_decode_leg_main_path)`, `RUN_TEST(test_cmd_idle_overflow_at_full_block)`, `RUN_TEST(test_even_block_no_remainder)` after the existing `RUN_TEST` calls.

---

### `firestarter_app/tests/test_even_block.py` (NEW test — host pytest)

**Analog:** `firestarter_app/tests/test_frame_vectors.py` — specifically `TestPerBoardBufferNegotiation` (lines 228–261) and `TestHostChunkFitsFirmwareDecodeCap` (lines 177–225)

**File header pattern** (from `test_frame_vectors.py` lines 1–26):
```python
"""
Project Name: Firestarter
Copyright (c) 2024 Henrik Olsson

Permission is hereby granted under MIT license.

Phase 54 Plan XX — Host pytest even-block suite.

<module docstring describing purpose>
"""
```

**Class structure pattern** — use class-per-concern (matching `TestPerBoardBufferNegotiation`, `TestHostChunkFitsFirmwareDecodeCap`, `TestFrameVectorsEncodeLeg`):

```python
class TestEvenBlockNoRemainder:
    """No-remainder arithmetic assertions (EVEN-01 SC2)."""

    def test_full_chip_no_remainder_uno(self) -> None:
        assert 65536 % 512 == 0, "65536-byte chip divides exactly into 512-byte blocks"

    def test_full_chip_no_remainder_leonardo(self) -> None:
        assert 65536 % 1024 == 0, "65536-byte chip divides exactly into 1024-byte blocks"
```

**`firmware_max_chunk` parse pattern** — mirrors `TestPerBoardBufferNegotiation.test_calculate_buffer_size_uses_advertised` (lines 245–261) which uses `SimpleNamespace` to inject a fake communicator:
```python
from types import SimpleNamespace
from firestarter.config import ConfigManager
from firestarter.eprom_operations import EpromOperator

op = EpromOperator(ConfigManager())
op.comm = SimpleNamespace(firmware_max_chunk=512)  # type: ignore[assignment]
assert op._calculate_buffer_size() == 512
```

**`FirmwareOutdatedError` raise pattern** — mirrors the negative tests in `test_serial_comm.py` (lines 45–71) using `pytest.raises`:
```python
import pytest
from firestarter.exceptions import FirmwareOutdatedError

with pytest.raises(FirmwareOutdatedError):
    op._calculate_buffer_size()  # comm has no firmware_max_chunk
```

**Import block pattern** (from `test_frame_vectors.py` lines 28–33):
```python
import pytest
from types import SimpleNamespace

from firestarter.config import ConfigManager
from firestarter.eprom_operations import EpromOperator
from firestarter.exceptions import FirmwareOutdatedError
```

**Test classes to include:**

1. `TestEvenBlockNoRemainder` — `test_full_chip_no_remainder_uno`, `test_full_chip_no_remainder_leonardo`, `test_power_of_two_chip_sizes_uno`, `test_power_of_two_chip_sizes_leonardo`
2. `TestFirmwareMaxChunkParse` — `test_calculate_buffer_size_uses_max_chunk_512`, `test_calculate_buffer_size_uses_max_chunk_1024`, `test_calculate_buffer_size_raises_without_max_chunk`, `test_max_chunk_replaces_fw_buf_minus_2`
3. `TestEvenBlockFrameVectorsCapBoundary` — confirm the existing `VEC_512_ALL_FF` and `VEC_512_ALL_ZERO` vectors can decode at `DATA_BUFFER_SIZE=512` cap (use `cobs_decode` from `frame_parser` as in `test_frame_vectors.py`)

**Note on `TestHostChunkFitsFirmwareDecodeCap` in `test_frame_vectors.py`** (lines 177–225): this existing test class has a `test_calculate_buffer_size_respects_decode_cap` that calls `op._calculate_buffer_size()` without setting `op.comm.firmware_max_chunk`. After Phase 54 that will raise `FirmwareOutdatedError` instead of returning a value. This existing test MUST be updated in `test_frame_vectors.py` when `_calculate_buffer_size` is changed — flag this as a required edit in the plan.

---

## Shared Patterns

### Function signature extension (firmware C)
**Source:** `rurp_serial_utils.h` line 37 + `rurp_serial_utils.cpp` line 128
**Apply to:** `rurp_serial_utils.h` (declaration) and `rurp_serial_utils.cpp` (definition) and both call sites
**Pattern:** Add `size_t cap` as a second parameter. The `size_t` type is already used by `rurp_communication_read_bytes` in the same header. The macro `#define PUSH` is file-local (between definition and `#undef`); replace the single hardcoded literal.

### Optional attribute with `getattr` guard (Python)
**Source:** `eprom_operations.py` lines 176–179
**Apply to:** `eprom_operations.py` `_calculate_buffer_size`, `serial_comm.py` new attribute init
**Pattern:**
```python
value = getattr(self.comm, "attribute_name", None) if self.comm else None
if value is not None and value >= threshold:
    return value
```

### `isdigit()` integer field parse (Python)
**Source:** `serial_comm.py` lines 621–624
**Apply to:** `serial_comm.py` new `fw_fields[3]` parse
**Pattern:**
```python
if len(fw_fields) >= N and fw_fields[N-1].strip().isdigit():
    communicator.attribute = int(fw_fields[N-1].strip())
```

### `pytest.raises` negative test (Python)
**Source:** `test_serial_comm.py` lines 45–48
**Apply to:** `test_even_block.py` `FirmwareOutdatedError` raise assertion
**Pattern:**
```python
with pytest.raises(FirmwareOutdatedError):
    <code that should raise>
```

### `SimpleNamespace` fake communicator injection (Python)
**Source:** `test_frame_vectors.py` lines 253–261
**Apply to:** `test_even_block.py` `TestFirmwareMaxChunkParse`
**Pattern:**
```python
from types import SimpleNamespace
op = EpromOperator(ConfigManager())
op.comm = SimpleNamespace(firmware_max_chunk=512)  # type: ignore[assignment]
assert op._calculate_buffer_size() == 512
```

### Unity test function structure (firmware C++)
**Source:** `test_frame_vectors.cpp` lines 183–258
**Apply to:** all new `void test_*(void)` functions
**Pattern:** standalone `void test_*(void)` function; assert with `TEST_ASSERT_*` macros; load frame bytes into `rx_queue`, call `setup_serial_read_mock(rx_queue, rx_pos)`, call `rurp_communication_read_data(data_buffer, cap)`, assert return value and buffer content.

### `RUN_TEST` registration (firmware C++)
**Source:** `test_frame_vectors.cpp` lines 268–272
**Apply to:** `main()` in `test_frame_vectors.cpp`
**Pattern:** add `RUN_TEST(new_test_function)` after existing registrations, before `return UNITY_END()`.

---

## No Analog Found

All files have close analogs in the codebase. No entry in this table.

---

## Key Invariant: Two Cap Values, One Decoder

The single most important pattern constraint for this phase:

| Call site | File | Cap argument | Reason |
|---|---|---|---|
| CMD_IDLE / JSON command | `firestarter.cpp` line 176 | `DATA_BUFFER_SIZE - 1` | `data_buffer[n] = '\0'` follows; NUL slot must be free |
| MAIN / write-receive | `operation_utils.cpp` line 164 | `DATA_BUFFER_SIZE` | No NUL write; buffer consumed by `data_buffer[i]` index only |

Every new test that calls `rurp_communication_read_data` must explicitly pass the cap and must test the CORRECT cap for the path being exercised. Never call it with one argument after Phase 54.

---

## Drift Gate Reminder (D-07)

`firestarter/tools/catalog/frame-vectors.toml` and `firestarter_app/tools/catalog/frame-vectors.toml` are **not modified** in Phase 54 (existing 512/1024 vectors already serve as the even-block corpus). The `codegen_vectors.py --check` drift gate therefore passes without a regen step. If the planner chooses to add new named vectors, both TOML files must be updated byte-identically and both repos' generated `frame_vectors.h` / `frame_vectors.py` regenerated.

---

## Metadata

**Analog search scope:** `firestarter/src/`, `firestarter/include/`, `firestarter/test/native/`, `firestarter_app/firestarter/`, `firestarter_app/tests/`
**Files read:** 16 source files
**Pattern extraction date:** 2026-06-04
