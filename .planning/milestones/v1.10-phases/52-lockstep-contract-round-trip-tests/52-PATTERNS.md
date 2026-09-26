# Phase 52: Lockstep Contract + Round-Trip Tests — Pattern Map

**Mapped:** 2026-06-02
**Files analyzed:** 17 new/modified files across both sub-repos
**Analogs found:** 17 / 17

---

## File Classification

| New/Modified File | Repo | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|------|-----------|----------------|---------------|
| `tools/catalog/frame-vectors.toml` | firmware | catalog | batch | `firestarter/tools/catalog/messages.toml` | role-match |
| `tools/catalog/codegen_vectors.py` | firmware | codegen | batch/transform | `firestarter/tools/catalog/codegen.py` | exact |
| `include/frame_vectors.h` | firmware | generated artifact | batch | `firestarter/include/messages.h` | exact |
| `test/native/avr/test_frame_vectors/test_frame_vectors.cpp` | firmware | Unity test | request-response | `firestarter/test/native/avr/test_cobs_cmd_frame/test_cobs_cmd_frame.cpp` | exact |
| `test/native/avr/test_frame_vectors/host_stubs.cpp` | firmware | test stub | — | `firestarter/test/native/avr/test_cobs_cmd_frame/host_stubs.cpp` | exact |
| `test/native/avr/test_frame_vectors/serial_read_mock.h` | firmware | test utility | — | `firestarter/test/native/avr/test_cobs_cmd_frame/serial_read_mock.h` | exact |
| `platformio.ini` (extended) | firmware | config | — | existing `[env:native]` | exact |
| `.github/workflows/build.yml` (extended) | firmware | CI workflow | — | existing `Catalog validity check` + `Codegen drift gate` steps | exact |
| `tools/catalog/frame-vectors.toml` | host | catalog | batch | `firestarter_app/tools/catalog/messages.toml` (byte-identical to fw) | exact |
| `tools/catalog/codegen_vectors.py` | host | codegen | batch/transform | `firestarter_app/tools/catalog/codegen.py` (byte-identical to fw) | exact |
| `firestarter/frame_vectors.py` | host | generated artifact | batch | `firestarter_app/firestarter/messages.py` | exact |
| `tests/test_frame_vectors.py` | host | pytest test | request-response | `firestarter_app/tests/test_cobs.py` | exact |
| `tests/test_revision_constants_parity.py` (extended) | host | parity test | — | existing file lines 76–185 (`@pytest.mark.skipif` pattern) | exact |
| `.github/workflows/ci.yml` (extended) | host | CI workflow | — | existing `Catalog validity check` + `Codegen drift gate` steps | exact |
| `firestarter/src/boards/rurp_serial_utils.cpp` | firmware | exercised-by (read-only) | COBS I/O | — | exercised only |
| `firestarter_app/firestarter/frame_parser.py` | host | exercised-by (read-only) | COBS I/O | — | exercised only |
| `firestarter_app/firestarter/constants.py` | host | read (parity subject) | — | — | parity subject |

---

## Pattern Assignments

### `tools/catalog/frame-vectors.toml` (firmware + host — byte-identical)

**Analog:** `firestarter/tools/catalog/messages.toml`

**Top-level catalog table pattern** (lines 13–15):
```toml
[catalog]
version = 1
project = "firestarter"
```

**Array-of-tables entry shape** (lines 21–40 of messages.toml):
```toml
[[messages]]
id          = 0x01
name        = "MSG_OK_READY"
severity    = "OK"
format      = "Ready"
params      = []
wire_format = "id_frame"
```

For `frame-vectors.toml` the entry shape is simpler — no `severity`, `format`, `params`, or `wire_format`:
```toml
[[vectors]]
id          = 0x01
name        = "VEC_EMPTY"
description = "Empty payload — COBS(CRC8([])) + 0x00"
payload_hex = ""
frame_hex   = "0101 00"
```

**Key rules (from messages.toml header + codegen.py LCAT-05 contract):**
- `id`: u8 unique, sorted ascending for emission (edit order does not matter).
- `name`: `VEC_[A-Z][A-Z0-9_]*` (mirrors `MSG_[A-Z][A-Z0-9_]*` pattern).
- `payload_hex`: hex string of raw payload bytes; empty string `""` for zero-length.
- `frame_hex`: hex string of complete frame bytes including trailing `00` delimiter.
- File header comment must note byte-identity with the other sub-repo's copy and the paired-commit discipline (D-09).

---

### `tools/catalog/codegen_vectors.py` (firmware + host — byte-identical)

**Analog:** `firestarter/tools/catalog/codegen.py` (full file, 739 lines)

**Module docstring / determinism contract pattern** (lines 1–34):
```python
#!/usr/bin/env python3
"""
Firestarter v1.10 frame-vector catalog codegen.

Reads tools/catalog/frame-vectors.toml (or a vendored copy in a sub-repo's
tools/catalog/ directory) and emits one of two deterministic outputs:

  --language cpp-vectors    -> include/frame_vectors.h
                               (PROGMEM const struct array)
  --language python-vectors -> firestarter/frame_vectors.py
                               (Python tuple list)

Determinism contract (LCAT-05): two consecutive runs against the same catalog
file produce byte-identical output. Achieved by:
  - sorting vectors by id ascending before emission
  - no timestamps, hostnames, or hashes in the banner
  - LF line endings via Path.write_text(..., newline='\\n')
  - upper-case 2-digit hex literals ("0x%02X")
  - explicit dict iteration via sorted(...)

Validation (--check): validates the catalog and exits 0/1 without writing
files. Must not require [[messages]] — this catalog uses [[vectors]].

Stdlib only (Python 3.11+ for tomllib).
"""
```

**Import block pattern** (lines 36–40 of codegen.py):
```python
import argparse
import re
import sys
import tomllib
from pathlib import Path
```

**`--check` flag shape and validation exit pattern** (lines 693–734 of codegen.py):
```python
def main():
    args = _build_argparser().parse_args()

    if not args.catalog.is_file():
        print(f"ERROR: catalog file not found: {args.catalog}", file=sys.stderr)
        return 2

    try:
        catalog = _load_catalog(args.catalog)
    except tomllib.TOMLDecodeError as e:
        print(f"ERROR: failed to parse TOML in {args.catalog}: {e}", file=sys.stderr)
        return 1

    try:
        validate_catalog(catalog)
    except CatalogError as e:
        print(f"ERROR: catalog validation failed: {e}", file=sys.stderr)
        return 1

    if args.check:
        n = len(catalog["vectors"])
        print(f"OK: catalog valid ({n} vectors, version "
              f"{catalog['catalog']['version']}).")
        return 0

    if args.target is None or args.language is None:
        print("ERROR: --target and --language are required unless --check.",
              file=sys.stderr)
        return 2

    emitter = LANGUAGE_EMITTERS[args.language]
    output = emitter(catalog)

    args.target.parent.mkdir(parents=True, exist_ok=True)
    # LF endings guaranteed on all platforms (LCAT-05):
    args.target.write_text(output, encoding="utf-8", newline="\n")
    print(f"OK: wrote {args.target} ({args.language}, "
          f"{len(catalog['vectors'])} vectors).")
    return 0
```

**Sorted-emission pattern** (lines 466–468 of codegen.py):
```python
def _sorted_messages(catalog):
    return sorted(catalog["messages"], key=lambda m: m["id"])
```
For vectors: `sorted(catalog["vectors"], key=lambda v: v["id"])`.

**LF write pattern** (line 731 of codegen.py):
```python
args.target.write_text(output, encoding="utf-8", newline="\n")
```

**`--check` argparse flag** (lines 688–690 of codegen.py):
```python
p.add_argument("--check", action="store_true",
               help="Validate the catalog and exit 0/1. No files written.")
```

**Pitfall:** The existing `validate_catalog()` in `codegen.py` requires a non-empty `[[messages]]` array. The new `codegen_vectors.py` must validate `[[vectors]]` independently — do NOT call the existing `validate_catalog()` from `codegen.py`.

---

### `include/frame_vectors.h` (firmware — codegen'd C++ PROGMEM header)

**Analog:** `firestarter/include/messages.h` (first 40 lines — banner + header guard shape)

**Banner + header guard pattern** (lines 1–25 of messages.h):
```cpp
/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 *
 * Firestarter -- v1.10 frame-vector catalog (C++ firmware side)
 *
 * DO NOT EDIT -- generated by tools/catalog/codegen_vectors.py from
 *               tools/catalog/frame-vectors.toml.
 * Re-run codegen after editing the canonical catalog.
 *
 * Catalog version: {version}
 * Total vectors: {count}
 */

#ifndef __FRAME_VECTORS_H__
#define __FRAME_VECTORS_H__

#ifdef __cplusplus
extern "C" {
#endif

#include <stdint.h>
#include <avr/pgmspace.h>
```

**Expected emit shape** — a PROGMEM struct array, not `#define` constants (unlike `messages.h` which emits `#define MSG_*`). The vector suite accesses elements by index. Shape example:
```cpp
// --- Frame vectors (sorted by id ascending) ---
typedef struct {
    uint8_t  id;
    uint8_t  payload[MAX_PAYLOAD_LEN];
    uint16_t payload_len;
    uint8_t  frame[MAX_FRAME_LEN];
    uint16_t frame_len;
} frame_vector_t;

static const frame_vector_t FRAME_VECTORS[] PROGMEM = {
    { 0x01, {}, 0, {0x01, 0x01, 0x00}, 3 },  /* VEC_EMPTY */
    /* ... */
};
static const uint16_t FRAME_VECTOR_COUNT PROGMEM = ...;
```

**Upper-case hex literal pattern** (lines 512–515 of codegen.py):
```python
parts.append(
    f"#define {m['name']:<{name_col}}0x{m['id']:02X}\n"
)
```
For vector byte arrays: `"0x%02X"` format for each byte.

---

### `test/native/avr/test_frame_vectors/test_frame_vectors.cpp` (firmware — Unity test)

**Primary analog:** `firestarter/test/native/avr/test_cobs_cmd_frame/test_cobs_cmd_frame.cpp`
**Secondary analog:** `firestarter/test/native/avr/test_cobs_data_frame/test_cobs_data_frame.cpp`

**Includes pattern** (lines 39–56 of test_cobs_cmd_frame.cpp):
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

Also include the generated header:
```cpp
#include "frame_vectors.h"
```

**Shared test state pattern** (lines 61–64 of test_cobs_cmd_frame.cpp):
```cpp
static char data_buffer[DATA_BUFFER_SIZE];
static std::vector<uint8_t> rx_queue;
static size_t rx_pos;
```

**`ref_crc8` — independent table-free reference** (lines 71–82 of test_cobs_cmd_frame.cpp — copy verbatim):
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

**`test_cobs_encode` helper** (lines 95–118 of test_cobs_cmd_frame.cpp — copy verbatim):
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

**`build_cobs_frame_bytes` helper** (lines 124–141 of test_cobs_cmd_frame.cpp — copy verbatim):
```cpp
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
    out_vec.push_back(0x00);
}
```

**`setUp` / `tearDown` pattern** (lines 149–176 of test_cobs_cmd_frame.cpp):
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

**Both-legs assertion shape per vector (D-02):**
```cpp
// Leg 1: encode(payload) == frozen frame bytes
void test_vector_encode_leg(void) {
    for (uint16_t i = 0; i < FRAME_VECTOR_COUNT; i++) {
        /* Read vector from PROGMEM */
        frame_vector_t vec;
        memcpy_P(&vec, &FRAME_VECTORS[i], sizeof(frame_vector_t));

        std::vector<uint8_t> built;
        build_cobs_frame_bytes(vec.payload, vec.payload_len, built);

        TEST_ASSERT_EQUAL_size_t(vec.frame_len, built.size());
        TEST_ASSERT_EQUAL_MEMORY(vec.frame, built.data(), vec.frame_len);
    }
}

// Leg 2: decode(frozen frame) == payload  (cmd-sized vectors only, ≤511 bytes)
void test_vector_decode_leg(void) {
    for (uint16_t i = 0; i < FRAME_VECTOR_COUNT; i++) {
        frame_vector_t vec;
        memcpy_P(&vec, &FRAME_VECTORS[i], sizeof(frame_vector_t));
        if (vec.payload_len > DATA_BUFFER_SIZE - 1) continue;  /* encoder-only */

        rx_queue.clear();
        rx_pos = 0;
        rx_queue.insert(rx_queue.end(), vec.frame, vec.frame + vec.frame_len);
        setup_serial_read_mock(rx_queue, rx_pos);

        int res = rurp_communication_read_data(data_buffer);
        TEST_ASSERT_GREATER_OR_EQUAL_INT(0, res);
        TEST_ASSERT_EQUAL_size_t(vec.payload_len, (size_t)res);
        TEST_ASSERT_EQUAL_MEMORY(vec.payload, data_buffer, vec.payload_len);
    }
}
```

**KAT (D-06) pattern** (from RESEARCH.md Example 4):
```cpp
void test_crc8_known_answer(void) {
    const uint8_t input[] = { 0x01 };
    TEST_ASSERT_EQUAL_HEX8(0x07, ref_crc8(input, 1));
    TEST_ASSERT_EQUAL_HEX8(0x00, ref_crc8(NULL, 0));
}
```

**`main()` pattern** (lines 449–463 of test_cobs_cmd_frame.cpp):
```cpp
int main(int argc, char** argv) {
    (void)argc;
    (void)argv;
    UNITY_BEGIN();

    RUN_TEST(test_crc8_known_answer);
    RUN_TEST(test_vector_encode_leg);
    RUN_TEST(test_vector_decode_leg);

    return UNITY_END();
}
```

---

### `test/native/avr/test_frame_vectors/host_stubs.cpp` (firmware)

**Analog:** `firestarter/test/native/avr/test_cobs_cmd_frame/host_stubs.cpp` (full file, 30 lines)

**Full file pattern** (lines 1–30 of test_cobs_cmd_frame/host_stubs.cpp — copy with updated phase comment):
```cpp
/*
 * Phase 52 Plan XX — host stub TU for the test_frame_vectors suite.
 *
 * Provides no-op rurp_* symbol implementations so the test binary links
 * against boards/rurp_serial_utils.cpp on the host platform = native.
 *
 * Mirrors the pattern from test_cobs_cmd_frame/host_stubs.cpp (Phase 51).
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

---

### `test/native/avr/test_frame_vectors/serial_read_mock.h` (firmware)

**Analog:** `firestarter/test/native/avr/test_cobs_cmd_frame/serial_read_mock.h` (full file, 119 lines)

Copy verbatim from `test_cobs_cmd_frame/serial_read_mock.h` with updated header comment (phase reference). The `setup_serial_read_mock()` function signature and lambda capture semantics must be preserved exactly — the finite-stream behavior (returns -1 after queue exhaustion) is required for deterministic timeout behavior in any truncated-frame scenarios.

**Core function signature to preserve** (lines 81–119 of serial_read_mock.h):
```cpp
static void setup_serial_read_mock(const std::vector<uint8_t>& queue, size_t& pos) {
    When(OverloadedMethod(ArduinoFake(Serial), read, int(void)))
        .AlwaysDo([&queue, &pos]() -> int {
            if (pos >= queue.size()) return -1;
            return (int)(uint8_t)queue[pos++];
        });
    When(Method(ArduinoFake(Serial), available))
        .AlwaysDo([&queue, &pos]() -> int {
            int remaining = (int)(queue.size() - pos);
            return (remaining > 0) ? remaining : 0;
        });
    /* ... peek and readBytes overloads follow same pattern ... */
}
```

---

### `platformio.ini` (firmware — extend `[env:native]`)

**Analog:** Existing `[env:native]` section (lines 67–113 of platformio.ini)

**`test_filter` allowlist extension** (lines 78–84 of platformio.ini — add one entry):
```ini
test_filter =
    native/avr/test_dispatch
    native/avr/test_messages
    native/avr/test_data_input
    native/avr/test_read_timing
    native/avr/test_cobs_data_frame
    native/avr/test_cobs_cmd_frame
    native/avr/test_frame_vectors          ; ADD THIS
```

**`build_flags -I` extension** (lines 85–94 of platformio.ini — add one entry):
```ini
build_flags =
    ${env.build_flags}
    -std=gnu++17
    -I include
    -I test/native/avr/test_dispatch
    -I test/native/avr/test_messages
    -I test/native/avr/test_data_input
    -I test/native/avr/test_read_timing
    -I test/native/avr/test_cobs_data_frame
    -I test/native/avr/test_cobs_cmd_frame
    -I test/native/avr/test_frame_vectors   ; ADD THIS
    -D RURP_BOARD_NAME=\"native\"
```

**Note:** `build_src_filter = +<proms/> +<boards/rurp_serial_utils.cpp> +<json_parser.c>` (line 111) already includes `rurp_serial_utils.cpp`, so the new suite has `rurp_communication_read_data()` available without further changes.

---

### `.github/workflows/build.yml` (firmware — extend with vector drift gate)

**Analog:** Lines 60–69 of `firestarter/.github/workflows/build.yml` (existing v1.2 catalog validity + drift gate steps)

**Pattern to mirror** (lines 60–69 of build.yml):
```yaml
- name: Catalog validity check
  run: python3 tools/catalog/codegen.py --catalog tools/catalog/messages.toml --check

- name: Codegen drift gate (messages.h)
  run: |
    python3 tools/catalog/codegen.py \
      --catalog tools/catalog/messages.toml \
      --target include/messages.h \
      --language cpp
    git diff --exit-code include/messages.h
```

**New steps to add immediately after the existing drift gate** (before `Install PlatformIO Core`):
```yaml
- name: Vector catalog validity check
  run: python3 tools/catalog/codegen_vectors.py --catalog tools/catalog/frame-vectors.toml --check

- name: Codegen drift gate (frame_vectors.h)
  run: |
    python3 tools/catalog/codegen_vectors.py \
      --catalog tools/catalog/frame-vectors.toml \
      --target include/frame_vectors.h \
      --language cpp-vectors
    git diff --exit-code include/frame_vectors.h
```

---

### `tools/catalog/frame-vectors.toml` (host — byte-identical to firmware copy)

Same pattern as the firmware version. File header comment must reference the firmware copy and paired-commit discipline:
```toml
# Firestarter v1.10 frame-vector catalog (vendored copy — byte-identical to
# firestarter/tools/catalog/frame-vectors.toml).
#
# DO NOT EDIT without making the same change in the firmware sub-repo copy.
# These two files must remain byte-identical; drift is detected by per-repo
# CI drift gates + paired-commit discipline (D-09, Phase 52).
```

---

### `tools/catalog/codegen_vectors.py` (host — byte-identical to firmware copy)

Same pattern as the firmware version. All patterns from the firmware `codegen_vectors.py` section apply. The file is byte-identical to the firmware copy (including the `--language cpp-vectors` emitter, even though the host CI only uses `--language python-vectors`). This mirrors the existing `firestarter_app/tools/catalog/codegen.py` being byte-identical to the firmware's — confirmed by the RESEARCH.md source note.

---

### `firestarter/frame_vectors.py` (host — codegen'd Python module)

**Analog:** `firestarter_app/firestarter/messages.py` (first 40 lines — banner + module structure)

**Banner pattern** (lines 1–15 of messages.py):
```python
"""
Project Name: Firestarter
Copyright (c) 2024 Henrik Olsson

Permission is hereby granted under MIT license.

Firestarter -- v1.10 frame-vector catalog (host side)

DO NOT EDIT -- generated by tools/catalog/codegen_vectors.py from
              tools/catalog/frame-vectors.toml.
Re-run codegen after editing the canonical catalog.

Catalog version: {version}
Total vectors: {count}
"""
```

**Expected emit shape** — a list of named tuples or simple dataclasses, one per vector:
```python
from typing import NamedTuple

class FrameVector(NamedTuple):
    id: int
    name: str
    payload: bytes
    frame: bytes

# --- Frame vectors (sorted by id ascending) ---
FRAME_VECTORS: list[FrameVector] = [
    FrameVector(id=0x01, name="VEC_EMPTY",
                payload=b"",
                frame=bytes([0x01, 0x01, 0x00])),
    # ...
]
```

Hex byte literals emitted as `0x%02X` (e.g. `0x01, 0x42`) to match the LCAT-05 upper-case contract.

---

### `tests/test_frame_vectors.py` (host — pytest vector + KAT assertions)

**Primary analog:** `firestarter_app/tests/test_cobs.py` (full file, 395 lines)

**Imports pattern** (lines 33–37 of test_cobs.py):
```python
from firestarter.frame_parser import (
    _crc8_ccitt,
    cobs_decode,
    cobs_encode,
)
```

Also import the generated vector module:
```python
from firestarter.frame_vectors import FRAME_VECTORS
```

**`_ref_crc8_ccitt` helper** (lines 58–71 of test_cobs.py — this is a module-level function there, but also available as `conftest._ref_crc8_ccitt`):
```python
def _ref_crc8_ccitt(data: bytes) -> int:
    """Table-free CRC8 reference — poly 0x07, seed 0x00, no reflection, no final XOR."""
    crc = 0
    for b in data:
        crc ^= b
        for _ in range(8):
            if crc & 0x80:
                crc = ((crc << 1) ^ 0x07) & 0xFF
            else:
                crc = (crc << 1) & 0xFF
    return crc
```

The same reference is available from `conftest.py` (lines 33–46 of conftest.py) as a module-level function. Either reuse the conftest definition (import it) or inline it at the module level of `test_frame_vectors.py` (matching the `test_cobs.py` approach). The table-free independence from the production `_crc8_ccitt` is what matters.

**Both-legs assertion shape (D-02)** — per-vector parametrize or loop pattern:
```python
class TestFrameVectorsEncodeLeg:
    """Leg 1: encode(payload) == frozen frame bytes for every golden vector."""

    def test_all_vectors_encode(self) -> None:
        for vec in FRAME_VECTORS:
            crc = _crc8_ccitt(vec.payload)
            encoded = cobs_encode(vec.payload + bytes([crc]))
            assert encoded + b'\x00' == vec.frame, (
                f"Vector {vec.name}: encode leg failed"
            )


class TestFrameVectorsDecodeLeg:
    """Leg 2: decode(frozen frame) == payload for vectors within decode cap."""

    def test_all_vectors_decode(self) -> None:
        for vec in FRAME_VECTORS:
            if len(vec.payload) > 511:
                continue  # encoder-only for ≥512 B payloads (Pitfall 5)
            body = vec.frame[:-1]  # strip 0x00 delimiter
            decoded = cobs_decode(body)
            assert decoded[:-1] == vec.payload, (
                f"Vector {vec.name}: decode leg payload mismatch"
            )
            assert decoded[-1] == _crc8_ccitt(vec.payload), (
                f"Vector {vec.name}: decode leg CRC mismatch"
            )
```

**KAT pattern** (from RESEARCH.md Example 4 + test_cobs.py `TestCrc8DataPayload.test_crc8_known_value` at line 224):
```python
class TestCrc8KnownAnswer:
    """D-06 SC4: known-answer test pins CRC8 poly 0x07, seed 0x00."""

    def test_crc8_of_0x01_is_0x07(self) -> None:
        """CRC8([0x01]) == 0x07 — the polynomial value itself."""
        assert _crc8_ccitt(bytes([0x01])) == 0x07

    def test_crc8_of_empty_is_seed(self) -> None:
        """CRC8([]) == 0x00 — empty payload returns seed."""
        assert _crc8_ccitt(b"") == 0x00
```

---

### `tests/test_revision_constants_parity.py` (host — extend existing file)

**Analog:** Existing file, specifically:
- Lines 55–58: `FIRMWARE_HEADER` / `FW_ABSENT` definitions (the skipif proxy)
- Lines 76–77: `@pytest.mark.skipif(FW_ABSENT, ...)` decorator pattern
- Lines 88–91: local import style inside the function body

**`FIRMWARE_HEADER` / `FW_ABSENT` definitions** (lines 55–58 of test_revision_constants_parity.py):
```python
FIRMWARE_HEADER = (
    Path(__file__).parent.parent.parent / "firestarter" / "include" / "firestarter.h"
)
FW_ABSENT = not FIRMWARE_HEADER.exists()
```

**New function to add** (after line 185, following the `test_ctrl_values_match_firmware` function):
```python
@pytest.mark.skipif(FW_ABSENT, reason="firestarter firmware checkout absent")
def test_cmd_frame_max_parity():
    """Assert host CMD_FRAME_MAX == firmware Uno DATA_BUFFER_SIZE floor (512).

    Firmware: firestarter.h #define CMD_FRAME_MAX DATA_BUFFER_SIZE
    On Uno/uno328pb: DATA_BUFFER_SIZE == 512 (the default, per firestarter.h).
    On Leonardo: DATA_BUFFER_SIZE may be 1024 via platformio.ini build_flags;
    CMD_FRAME_MAX on that board would be 1024. BUT 512 is the binding minimum
    the host must not exceed — a command frame >512 B is not a legitimate use
    case in v1.10. Host hardcodes 512; this is acceptable for v1.10 (D-07).
    """
    from firestarter.constants import CMD_FRAME_MAX
    assert CMD_FRAME_MAX == 512  # == Uno DATA_BUFFER_SIZE floor
```

**Where `CMD_FRAME_MAX` is defined** (`firestarter_app/firestarter/constants.py` lines 24–28):
```python
# Command-channel frame size limit — Firmware sync: firestarter.h CMD_FRAME_MAX
# Largest legitimate JSON command (~422 B) + headroom = 512; equals BUFFER_SIZE.
# Firmware parity: firestarter.h #define CMD_FRAME_MAX DATA_BUFFER_SIZE
CMD_FRAME_MAX = 512
```

---

### `.github/workflows/ci.yml` (host — extend with vector drift gate)

**Analog:** Lines 34–43 of `firestarter_app/.github/workflows/ci.yml` (existing catalog validity + drift gate steps)

**Pattern to mirror** (lines 34–43 of ci.yml):
```yaml
- name: Catalog validity check
  run: python3 tools/catalog/codegen.py --catalog tools/catalog/messages.toml --check

- name: Codegen drift gate (messages.py)
  run: |
    python3 tools/catalog/codegen.py \
      --catalog tools/catalog/messages.toml \
      --target firestarter/messages.py \
      --language python
    git diff --exit-code firestarter/messages.py
```

**New steps to add immediately after the existing drift gate** (before `Install package + test deps`):
```yaml
- name: Vector catalog validity check
  run: python3 tools/catalog/codegen_vectors.py --catalog tools/catalog/frame-vectors.toml --check

- name: Codegen drift gate (frame_vectors.py)
  run: |
    python3 tools/catalog/codegen_vectors.py \
      --catalog tools/catalog/frame-vectors.toml \
      --target firestarter/frame_vectors.py \
      --language python-vectors
    git diff --exit-code firestarter/frame_vectors.py
```

---

## Shared Patterns

### `ref_crc8` / `_ref_crc8_ccitt` — independent table-free CRC8 reference
**Source (C++):** `firestarter/test/native/avr/test_cobs_cmd_frame/test_cobs_cmd_frame.cpp` lines 71–82
**Source (Python):** `firestarter_app/tests/conftest.py` lines 33–46 (module-level), also inline at `firestarter_app/tests/test_cobs.py` lines 58–71
**Apply to:** `test_frame_vectors.cpp` (copy verbatim), `tests/test_frame_vectors.py` (import from conftest or copy inline)

The key invariant: **table-free** implementation independent of the production `CRC8_TABLE` PROGMEM array (firmware) and `_CRC8_CCITT_TABLE` bytes object (host). If the production table regresses to a different polynomial, the table-free reference catches it.

### COBS test helpers — `test_cobs_encode` + `build_cobs_frame_bytes`
**Source:** `firestarter/test/native/avr/test_cobs_cmd_frame/test_cobs_cmd_frame.cpp` lines 95–141
**Also in:** `test_cobs_data_frame/test_cobs_data_frame.cpp` lines 89–134 (identical)
**Apply to:** `test_frame_vectors.cpp` — copy both functions verbatim. These helpers are test-side COBS primitives independent of the production `rurp_communication_write()` encoder.

### `setup_serial_read_mock` — ArduinoFake queued-byte mock
**Source:** `firestarter/test/native/avr/test_cobs_cmd_frame/serial_read_mock.h` lines 81–119
**Apply to:** `test_frame_vectors/serial_read_mock.h` — copy verbatim (per the local-copy-over-shared pattern documented in the source file's header comment)

### `ArduinoFakeReset` + stub chain in `setUp`
**Source:** `firestarter/test/native/avr/test_cobs_cmd_frame/test_cobs_cmd_frame.cpp` lines 149–176
**Apply to:** `test_frame_vectors.cpp` `setUp()` — copy the flush stub, write stub, and millis stub chain exactly.

### Determinism contract for codegen (LCAT-05)
**Source:** `firestarter/tools/catalog/codegen.py` docstring lines 22–28
**Apply to:** `codegen_vectors.py` in both repos — the four rules (sort by id, no timestamps, LF via `newline='\n'`, upper-case hex) must all be honored.

### `FW_ABSENT` skipif guard pattern
**Source:** `firestarter_app/tests/test_revision_constants_parity.py` lines 55–58 (`FIRMWARE_HEADER`, `FW_ABSENT`) + line 76 (`@pytest.mark.skipif`)
**Apply to:** The new `test_cmd_frame_max_parity` function — use the existing `FW_ABSENT` variable already defined in the file.

### `build_src_filter` — `rurp_serial_utils.cpp` already included
**Source:** `firestarter/platformio.ini` line 111: `build_src_filter = +<proms/> +<boards/rurp_serial_utils.cpp> +<json_parser.c>`
**Apply to:** No change needed — the new `test_frame_vectors` suite gets `rurp_communication_read_data()` from the existing `build_src_filter` entry.

---

## Exercised-By References (Read-Only, Not Modified)

| File | Purpose in Phase 52 | Notes |
|------|---------------------|-------|
| `firestarter/src/boards/rurp_serial_utils.cpp` | Provides `rurp_communication_read_data()` for decode-leg assertions | Already linked via `build_src_filter` in `[env:native]` |
| `firestarter_app/firestarter/frame_parser.py` | Provides `cobs_encode()`, `cobs_decode()`, `_crc8_ccitt()` for all host assertions | Already installed via `pip install -e .` |
| `firestarter/include/firestarter.h` | Parity subject: `CMD_FRAME_MAX` (~line 26), `DATA_BUFFER_SIZE` | Read by `test_revision_constants_parity.py` via `FIRMWARE_HEADER` path |
| `firestarter_app/firestarter/constants.py` | Parity subject: `CMD_FRAME_MAX = 512` (line 28) | Imported inside `test_cmd_frame_max_parity` |

---

## No Analog Found

No files in this phase lack a close analog. All patterns exist in the codebase.

---

## Critical Pitfalls to Embed in Plans

1. **Pitfall 3 (platformio.ini positive allowlist):** A new suite directory is **silently skipped** by `pio test -e native` if not added to BOTH `test_filter` AND `build_flags -I`. The `[env:native]` uses a positive allowlist (not `test_ignore`) due to a PIO version quirk — both entries are mandatory.

2. **Pitfall 6 (codegen.py `--check` schema mismatch):** The existing `validate_catalog()` in `codegen.py` requires `[[messages]]`. A separate `codegen_vectors.py` with its own `[[vectors]]` validator avoids this entirely.

3. **Pitfall 5 (512-byte cap):** `rurp_communication_read_data()` caps at 511 bytes (CR-01). The decode leg of VEC_512_* and VEC_1024_* vectors must be skipped (`if len(vec.payload) > 511: continue` in C++; `if len(vec.payload) > 511: continue` in Python). These vectors are encoder-only.

4. **Pitfall 2 ('#' marker):** Vector frame bytes in the catalog store COBS body + `0x00` only — no `'#'` prefix. The `'#'` is consumed upstream of `rurp_communication_read_data()` on the data path and is an application-layer concern outside the COBS layer being tested.

5. **Pitfall 4 (LF endings):** `codegen_vectors.py` must use `Path.write_text(..., newline='\n')` to guarantee LF on all platforms for the `git diff --exit-code` gate.

---

## Metadata

**Analog search scope:** `firestarter/tools/catalog/`, `firestarter/include/`, `firestarter/test/native/avr/`, `firestarter/.github/workflows/`, `firestarter_app/tools/catalog/`, `firestarter_app/firestarter/`, `firestarter_app/tests/`, `firestarter_app/.github/workflows/`
**Files scanned:** 16 source files read directly
**Pattern extraction date:** 2026-06-02
