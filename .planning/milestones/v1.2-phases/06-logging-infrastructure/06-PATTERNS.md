# Phase 6: Logging Infrastructure — Pattern Map

**Mapped:** 2026-05-18
**Files analyzed:** 24 (15 NEW + 9 MODIFY)
**Analogs found:** 22 / 24
**No-analog files:** 2 (`pyproject.toml` test-config block, `.github/workflows/ci.yml` for host)

---

## File Classification

| File | Status | Role | Closest analog | Match |
|------|--------|------|---------------|-------|
| `.planning/catalog/messages.toml` | NEW | catalog (data source) | `firestarter_app/firestarter/data/chip_database.json` | role-match |
| `.planning/catalog/codegen.py` | NEW | codegen tool | `firestarter_app/tools/build_db.py` | exact |
| `.planning/catalog/sync_to_subrepos.sh` | NEW | vendored-sync-script | `firestarter_app/firestarter_test.sh` | role-only |
| `firestarter/tools/catalog/messages.toml` | NEW | catalog (vendored copy) | (mirror of meta-repo) | mirror |
| `firestarter/tools/catalog/codegen.py` | NEW | codegen (vendored copy) | (mirror of meta-repo) | mirror |
| `firestarter/include/messages.h` | NEW (generated) | firmware-header | `firestarter/include/logging.h` + `firestarter/include/rurp_shield.h` | role-match |
| `firestarter/src/messages.c` | NEW (generated) | firmware PROGMEM table | `firestarter/src/logging.c` | exact |
| `firestarter/include/logging_id.h` | NEW (hand-written) | convenience-macro header | `firestarter/include/logging.h` | exact |
| `firestarter_app/tools/catalog/messages.toml` | NEW | catalog (vendored copy) | (mirror of meta-repo) | mirror |
| `firestarter_app/tools/catalog/codegen.py` | NEW | codegen (vendored copy) | (mirror of meta-repo) | mirror |
| `firestarter_app/firestarter/messages.py` | NEW (generated) | host catalog module | `firestarter_app/firestarter/constants.py` | role-match |
| `firestarter/test/native/avr/test_messages/test_rurp_log_id.cpp` | NEW | firmware native test | `firestarter/test/native/avr/test_dispatch/test_configure_memory.cpp` | exact |
| `firestarter/test/native/avr/test_messages/host_stubs.cpp` | NEW | firmware native stubs | `firestarter/test/native/avr/test_dispatch/host_stubs.cpp` | exact |
| `firestarter/test/native/avr/test_messages/avr/pgmspace.h` | NEW | firmware native pgm shim | `firestarter/test/native/avr/test_dispatch/avr/pgmspace.h` | exact |
| `firestarter_app/tests/__init__.py` | NEW | pytest package marker | (none — sub-repo has zero pytest infra) | no-analog |
| `firestarter_app/tests/conftest.py` | NEW | pytest fixtures | (none — sub-repo has zero pytest infra) | no-analog |
| `firestarter_app/tests/test_decoder.py` | NEW | host unit test (decoder) | (none — pattern from PIO Unity suite) | partial |
| `firestarter_app/tests/test_fwguard.py` | NEW | host unit test (fw guard) | (none — pattern from PIO Unity suite) | partial |
| `firestarter_app/.github/workflows/ci.yml` | NEW | host CI workflow | `firestarter/.github/workflows/build.yml` | role-match |
| `firestarter/include/rurp_shield.h` | MODIFY | firmware-decl | line 132-133 alongside `rurp_log_P` | self |
| `firestarter/src/boards/uno_rurp_shield.cpp` | MODIFY | firmware-helper (Uno) | line 83-100 alongside `rurp_log` | self |
| `firestarter/src/boards/leonardo_rurp_shield.cpp` | MODIFY | firmware-helper (Leonardo) | (relies on weak default — no current override) | analog-of-absence |
| `firestarter/src/boards/rurp_serial_utils.cpp` | MODIFY | firmware frame emitter | line 14-28 (`_firestarter_log_ram/_progmem`) + lines 113-120 (weak default) | self |
| `firestarter_app/firestarter/serial_comm.py` | MODIFY | host decoder | line 213-231 (`_read_and_parse_lines`) + line 363-415 (`_probe_port`) | self |
| `firestarter_app/firestarter/firmware.py` | MODIFY | host fw-guard | line 55-97 (`check_current_firmware`) | self |
| `firestarter/.github/workflows/build.yml` | MODIFY | firmware CI | existing build steps lines 26-53 | self |
| `firestarter_app/pyproject.toml` | MODIFY | host test config | existing `[project]`/`[tool.setuptools]` block | self |
| `firestarter/platformio.ini` | MODIFY (confirm) | firmware PIO env | existing `[env:native]` lines 43-62 | self |

---

## Pattern Assignments

### `.planning/catalog/codegen.py` (codegen tool — NEW)

**Analog:** `firestarter_app/tools/build_db.py` (the only other Python tool in `tools/` in either sub-repo; both produce a committed data artifact that downstream code consumes).

**Lines to read first (executor must read):** `firestarter_app/tools/build_db.py:1-44, 287-end`.

**Pattern to mirror — header + config constants + main() + `__main__` guard:**

```python
import xml.etree.ElementTree as ET
import json
import os
import requests
import sys

# ==========================================
# 1. CONFIGURATION
# ==========================================
MINIPRO_XML_URL = "https://gitlab.com/DavidGriffith/minipro/-/raw/master/infoic.xml"
_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "firestarter", "data")
OUTPUT_FILE = os.path.join(_DATA_DIR, "chip_database.json")
PINOUT_FILE = os.path.join(_DATA_DIR, "pinouts.json")
```

…and at the file's tail:

```python
    print(f"Done! {total_chips} chips processed. Saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
```

**Conventions called out:**
- **`os.path.join(os.path.dirname(__file__), …)`** — make path resolution work no matter what cwd the script is invoked from. Mandatory for codegen — both CI and dev invocation must resolve the same path.
- **Module-level UPPERCASE constants** for config (`OUTPUT_FILE`, `KNOWN_PROTOCOLS`). Adopt for `CATALOG_DEFAULT_PATH`, `CPP_HEADER_TEMPLATE`, etc.
- **`def main()` + `if __name__ == "__main__": main()`** — call this exactly. No `sys.exit(main())` wrapper.
- **`print(...)` for human-visible CLI output**, plain stdout, no logging framework. CI captures stdout/stderr; visibility comes from there.
- **No external dependencies in tools/**: `build_db.py` uses `xml.etree`, `json`, `os`, `requests`, `sys` only. `requests` is the only non-stdlib — and the project already declares it in `dependencies` in `pyproject.toml`. Codegen MUST stay stdlib-only (use `tomllib` from Py 3.11, NOT PyYAML).

**Gotchas:**
- `build_db.py` does NOT use `argparse` today — it has hard-coded paths. Codegen NEEDS `argparse` because the same script runs from two sub-repos with different target paths (`--catalog`, `--target`, `--language`, `--check`). The argparse skeleton is documented in RESEARCH.md §"Codegen Tool Design"; add it but keep the human-readable `print` output consistent with `build_db.py`'s style.
- `build_db.py` writes JSON via `json.dump(..., indent=2)` (last lines). For LCAT-05 byte-identical determinism, codegen MUST use `Path.write_text(content, encoding='utf-8', newline='\n')` after assembling the full output string — do NOT use `print` to file or stream writers (line-ending behaviour can drift between platforms).

---

### `firestarter/include/messages.h` (NEW — generated)

**Analog:** `firestarter/include/rurp_shield.h:1-19` (header guard + `extern "C"` + standard includes); `firestarter/include/logging.h:20-28` (PROGMEM extern declarations).

**Lines to read first:** `firestarter/include/rurp_shield.h:1-19, 132-133`; `firestarter/include/logging.h:1-30`.

**Pattern to mirror — header guard + extern C + AVR/PROGMEM includes:**

```cpp
/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 */

#ifndef __RURP_SHIELD_H__
#define __RURP_SHIELD_H__

#ifdef __cplusplus
extern "C" {
#endif

#include <stdint.h>
#include <stddef.h>
#include <string.h>
#include <avr/pgmspace.h>
#include "rurp_types.h"
```

**Pattern to mirror — PROGMEM extern declarations (from `logging.h:20-28`):**

```cpp
// Declare logging type strings defined in logging.c
extern const char LOG_OK_MSG[] PROGMEM;
extern const char LOG_INIT_DONE_MSG[] PROGMEM;
// ...
extern const char LOG_ERROR_MSG[] PROGMEM;
```

For Phase 6 the generated `messages.h` declares `extern const uint8_t MSG_PARAM_BYTES_TABLE[256] PROGMEM;` (defined in generated `messages.c`).

**Conventions called out:**
- **Header guard naming:** `__MESSAGES_H__` (matches `__RURP_SHIELD_H__`, `__LOGGING_H__` — double-underscore + uppercase).
- **MIT copyright banner** — first 5 lines. Generated files swap the banner for the "DO NOT EDIT — generated by tools/catalog/codegen.py" warning per RESEARCH.md §"Generated `messages.h` Skeleton", but keep the same overall comment-block shape.
- **`extern "C"` wrapper** — REQUIRED so both `.c` (logging.c, messages.c) and `.cpp` callers see C linkage.
- **`#include <avr/pgmspace.h>`** — required for `PROGMEM` and `pgm_read_byte`.
- **Constant prefix:** all `MSG_*` ID `#define`s mirror the all-caps + underscore style of `VPE_TO_VPP`, `A9_VPP_ENABLE`, `FLAG_FORCE`, `LOG_OK_MSG`.

**Gotchas:**
- The native test build includes the **shim** `test/native/avr/test_dispatch/avr/pgmspace.h`, NOT the real AVR header. The shim defines `PROGMEM` as empty, `PGM_P` as `const char *`, and `pgm_read_byte(addr)` as `(*(const uint8_t*)(addr))`. The generated `messages.h` MUST compile cleanly against both the real `<avr/pgmspace.h>` (production) and the shim (`test_messages/avr/pgmspace.h` — a copy of `test_dispatch/avr/pgmspace.h`). Stick to `PROGMEM` + `pgm_read_byte` only; don't use exotic accessors.
- AVR-GCC supports C99 designated initializers (`[0x01] = 0`). The generated `messages.c` uses these per RESEARCH.md §"Generated `messages.h` Skeleton" — this is verified to compile against `avr-gcc` on PlatformIO's atmelavr platform.

---

### `firestarter/src/messages.c` (NEW — generated; holds PROGMEM 256-byte table)

**Analog:** `firestarter/src/logging.c` (entire file — 14 lines; one-job-only TU that defines PROGMEM constants).

**Lines to read first:** `firestarter/src/logging.c:1-14` (whole file).

**Pattern to mirror — full file:**

```c
#include "logging.h"

#include "firestarter.h"

// Define all logging type strings in PROGMEM to save RAM and flash.
// These are declared as extern in logging.h
const char LOG_OK_MSG[] PROGMEM = "OK";
const char LOG_INIT_DONE_MSG[] PROGMEM = "INIT";
const char LOG_MAIN_DONE_MSG[] PROGMEM = "MAIN";
const char LOG_END_DONE_MSG[] PROGMEM = "END";
const char LOG_INFO_MSG[] PROGMEM = "INFO";
const char LOG_DATA_MSG[] PROGMEM = "DATA";
const char LOG_WARN_MSG[] PROGMEM = "WARN";
const char LOG_ERROR_MSG[] PROGMEM = "ERROR";
```

Generated `messages.c` swaps this for a single PROGMEM byte array initialized with designated initializers per RESEARCH.md §"Generated `messages.h` Skeleton".

**Conventions called out:**
- **`.c` extension** (not `.cpp`) — matches `logging.c`. C compiler is sufficient; no STL needed; cheaper symbol resolution from C++ TUs.
- **First include is the matching header** (`#include "logging.h"` → `#include "messages.h"`).
- **Comment block above the data** explains *why* PROGMEM (saves RAM and flash). Generated file replaces with DO-NOT-EDIT warning.
- **`const char […] PROGMEM = …`** — exact storage qualifier ordering. Use `const uint8_t MSG_PARAM_BYTES_TABLE[256] PROGMEM = { … };` for the param-count table.

**Gotchas:**
- `logging.c` is INCLUDED in production builds (Uno, Leonardo) but EXCLUDED from `[env:native]` via `src_filter = +<proms/>`. The new `messages.c` (PROGMEM param-count table) MUST be reachable on `[env:native]` too — because `test_messages/test_rurp_log_id.cpp` will exercise `MSG_PARAM_COUNT(id)`. Solution: replicate the PROGMEM table in `test_messages/host_stubs.cpp` (mirroring how `test_dispatch/host_stubs.cpp:40-48` replicates the `LOG_*_MSG` strings) OR widen `src_filter` to include `src/messages.c` for `[env:native]` — research recommends the latter. Planner picks; document the decision.

---

### `firestarter/include/logging_id.h` (NEW — hand-written convenience macros)

**Analog:** `firestarter/include/logging.h` (the entire file — same role: hand-written macro tower that fronts the lower-level `rurp_log` / `rurp_log_P`).

**Lines to read first:** `firestarter/include/logging.h:30-99` (high-level macro tower).

**Pattern to mirror — verbosity-gated macro + `do { … } while(0)` block + handle->response_msg avoidance:**

```cpp
#define log_info(msg)                               \
    if (is_flag_set(FLAG_VERBOSE) && (msg)[0] != '\0') { \
        rurp_log(LOG_INFO_MSG, msg);                \
    }

#define log_info_const(msg)                        \
    if (is_flag_set(FLAG_VERBOSE)) {               \
        rurp_log_P(LOG_INFO_MSG, PSTR(msg));       \
    }

#define log_info_format(cformat, ...)                       \
    if (is_flag_set(FLAG_VERBOSE)) {                        \
        format(handle->response_msg, cformat, __VA_ARGS__); \
        log_info(handle->response_msg)                      \
    }
```

**Conventions called out:**
- **`FLAG_VERBOSE` gate around INFO** (line 40-43). The new `LOG_INFO_ID` family MUST replicate this — see RESEARCH.md §"Convenience Macros" (`#define LOG_INFO_ID(id) do { if (is_flag_set(FLAG_VERBOSE)) { LOG_ID(id); } } while (0)`).
- **No `do { … } while (0)` wrapper in the existing single-statement macros** (`log_info_const` is a bare `if`-statement). The new `LOG_ID_U8` etc. use `do { … } while (0)` per RESEARCH.md because they declare local `uint8_t _b[N]`; this is correct and safe.
- **Macro arg naming** — single-char-friendly (`msg`, `cformat`, `value`). Adopt for new macros (`id`, `p1`, `buf_array`, `count`).
- **`PSTR(...)`** for PROGMEM string literals — REQUIRED in any `rurp_log_P` callsite. New helper does NOT take format strings, so PSTR is not needed in the macro body.

**Gotchas:**
- `log_*_format` macros reference `handle->response_msg` BY NAME at the call site — they assume the caller has a local variable named `handle`. The new `LOG_ID_*` macros avoid this entirely (params packed into a fresh `_b[N]` array local to the macro). This is the primary flash-savings mechanism per RESEARCH.md "Key Insight".
- `is_flag_set()` is declared in `firestarter.h` (transitively included via `rurp_shield.h`). The new header needs `#include "firestarter.h"` to pick it up — match the order in `logging.h:14-18`.

---

### `firestarter/src/boards/rurp_serial_utils.cpp` (MODIFY — add `_firestarter_emit_frame` + CRC8 helper)

**Analog:** itself, lines 14-28 (`_firestarter_log_ram` / `_firestarter_log_progmem`) + lines 113-120 (weak default `rurp_log` / `rurp_log_P`).

**Lines to read first:** `firestarter/src/boards/rurp_serial_utils.cpp:1-27, 113-120`.

**Pattern to mirror — sibling-helper layout (the new `_firestarter_emit_frame` sits right next to these two text-log helpers):**

```cpp
// Core logging function for RAM messages. Takes type from PROGMEM.
 void _firestarter_log_ram(PGM_P type, const char* msg) {
    SERIAL_PORT.print((const __FlashStringHelper*)type);
    SERIAL_PORT.print(F(": ")); 
    SERIAL_PORT.println(msg);
    SERIAL_PORT.flush();
}

// Core logging function for PROGMEM messages.
 void _firestarter_log_progmem(PGM_P type, PGM_P p_msg) {
    SERIAL_PORT.print((const __FlashStringHelper*)type);
    SERIAL_PORT.print(F(": "));
    SERIAL_PORT.println((const __FlashStringHelper*)p_msg);
    SERIAL_PORT.flush();
}
```

**Pattern to mirror — weak-default for board override:**

```cpp
// Provide weak default implementations for logging.
// These can be overridden by a strong implementation in board-specific code.
__attribute__((weak)) void rurp_log(PGM_P type, const char* msg) {
    _firestarter_log_ram(type, msg);
}
__attribute__((weak)) void rurp_log_P(PGM_P type, PGM_P msg) {
    _firestarter_log_progmem(type, msg);
}
```

**Conventions called out:**
- **`SERIAL_PORT` macro** — alias for `Serial` or `SerialUSB` depending on board. Use `SERIAL_PORT.write(uint8_t)` (single-byte binary; NOT `print` which formats as ASCII) — this is called out explicitly in CONTEXT.md §"Reusable Assets".
- **`.flush()` after writes** — REQUIRED; mirrors lines 19, 27. Without this, the host can timeout waiting for bytes the Arduino has buffered.
- **`__attribute__((weak))` for default impl** — the new `rurp_log_id` follows the same discipline: weak default in `rurp_serial_utils.cpp` (calls `_firestarter_emit_frame` unconditionally — no `com_mode` gate), strong override in `uno_rurp_shield.cpp` (adds the `com_mode` gate + `SERIAL_DEBUG` duplication).
- **Public-ish `_firestarter_log_*` naming** — leading underscore signals "internal helper, callable from board-specific TUs but not from app code". New emitter: `_firestarter_emit_frame`.

**Pattern to mirror — CRC8 table over [id, params] (NEW addition; sibling to the simple XOR checksum at lines 100-103):**

The closest existing pattern is the data-block checksum at lines 87-94 (`checksum ^= buffer[i]`), but that's XOR-1-byte. For CRC8 poly 0x07, follow RESEARCH.md §"Firmware `rurp_log_id` Design" Implementation Layer — emit a 256-byte PROGMEM table:

```cpp
static const uint8_t CRC8_TABLE[256] PROGMEM = { /* 256 precomputed bytes */ };

static uint8_t crc8_ccitt(uint8_t crc, uint8_t b) {
    return pgm_read_byte(&CRC8_TABLE[crc ^ b]);
}
```

**Gotchas:**
- The existing `rurp_communication_write` at lines 99-111 uses `SERIAL_PORT.write(size >> 8)` for the binary-byte API to send the DATA block size. **Mirror exactly the `SERIAL_PORT.write(uint8_t)` shape** — single-byte writes, NOT `SERIAL_PORT.write(buf, size)` (which is fine too but harder to interleave CRC computation).
- The 4-byte magic preamble can live in PROGMEM (`static const uint8_t MAGIC_PREAMBLE[4] PROGMEM = { 0xAA, 0x55, 0xAA, 0x55 };`) to save RAM. Read via `pgm_read_byte(&MAGIC_PREAMBLE[i])` — same pattern as the CRC8 table.

---

### `firestarter/src/boards/uno_rurp_shield.cpp` (MODIFY — add Uno strong override for `rurp_log_id`)

**Analog:** itself, lines 83-100 (`rurp_log` + `rurp_log_P`).

**Lines to read first:** `firestarter/src/boards/uno_rurp_shield.cpp:19-28, 83-100, 142-163`.

**Pattern to mirror — strong override with `com_mode` gate + `SERIAL_DEBUG` duplication:**

```cpp
bool com_mode = true;

#ifdef SERIAL_DEBUG
#define RX_DEBUG  A0
#define TX_DEBUG  A1

void log_debug(PGM_P type, const char* msg);
#else
#define log_debug(type, msg)
#endif

// ...

void rurp_log(PGM_P type, const char* msg) {
    log_debug(type, msg);
    if (com_mode) {
        _firestarter_log_ram(type, msg);
    }
}

void rurp_log_P(PGM_P type, PGM_P msg) {
    // For debug logging, we need to copy the PROGMEM message to RAM.
    // We can reuse the debug_msg_buffer for this.
    #ifdef SERIAL_DEBUG
    strcpy_P(debug_msg_buffer, msg);
    log_debug(type, debug_msg_buffer);
    #endif
    if (com_mode) {
        _firestarter_log_progmem(type, msg);
    }
}
```

**Conventions called out:**
- **`bool com_mode` is a global at line 19** — the gate variable. `rurp_set_programmer_mode()` sets `com_mode = false`; `rurp_set_communication_mode()` sets `com_mode = true`. The new `rurp_log_id` MUST respect this — same `if (com_mode) { … }` discipline.
- **`SERIAL_DEBUG` is `#ifdef`-gated** — when set, the function ALSO emits via `log_debug` (SoftwareSerial on A0/A1). The new `rurp_log_id` should emit a hex-dump form via debug per RESEARCH.md §"Board-Specific `rurp_log_id`". Use `snprintf_P` + `PSTR(...)` for the debug-side rendering exactly like lines 154-162.
- **Wrap inside `#ifdef ARDUINO_AVR_UNO`** — the entire file is gated at line 8 (`#ifdef ARDUINO_AVR_UNO`) / line 164 (`#endif`). New code lands inside this gate.

**Gotchas:**
- The existing `rurp_log_P` does the `strcpy_P` into `debug_msg_buffer` BEFORE the `com_mode` check (lines 92-96). This is intentional — the debug serial uses A0/A1 which are NOT the same pins as PORTD bit 1 (UART TX), so debug remains alive even during programming mode. Mirror this ordering: debug first, then `com_mode`-gated production emit.
- `debug_msg_buffer` is declared `extern char* debug_msg_buffer;` in `logging.h:154`. Re-using it for the hex-dump string is the path of least resistance; alternatively (per RESEARCH.md), render a short summary line ("LOG: ID 0x06 (4 bytes)") and skip the hex bytes.

---

### `firestarter/src/boards/leonardo_rurp_shield.cpp` (MODIFY — add Leonardo strong override OR rely on weak default)

**Analog:** the absence of any current `rurp_log` / `rurp_log_P` override in this file. Lines 1-152 of the entire file — there's no `rurp_log` body anywhere.

**Lines to read first:** `firestarter/src/boards/leonardo_rurp_shield.cpp:1-152` (skim — confirm no `rurp_log` body).

**Pattern to mirror — Leonardo uses the weak default in `rurp_serial_utils.cpp`:**

```cpp
// (No rurp_log override in leonardo_rurp_shield.cpp — uses the weak default
//  at rurp_serial_utils.cpp:113-117, which is just _firestarter_log_ram.)
```

So `rurp_log_id` on Leonardo will use the weak default in `rurp_serial_utils.cpp` (just calls `_firestarter_emit_frame` directly — no `com_mode` gate since Leonardo's serial is a separate USB-CDC bridge, no PORTD aliasing risk).

**Conventions called out:**
- **`#ifdef ARDUINO_AVR_LEONARDO`** wrapper — same gating discipline as Uno (line 9 / line 151).
- **Leonardo has no `com_mode` global** — confirmed by grep: this variable is Uno-only.
- **Leonardo's `SERIAL_PORT` is `Serial` on USB-CDC** (Atmega32U4 has separate USB hardware; the data bus pins are PORTD/PORTC/PORTE but UART is separate). No ghost-byte hazard → no `com_mode` gate needed.

**Gotchas:**
- The `leonardo_rurp_shield.cpp:148` block uses `rurp_log("DEBUG", msg)` inside `#ifdef SERIAL_DEBUG` for `debug_buf` — this calls the weak default. The new `rurp_log_id` will likewise be available globally via the weak default; Leonardo callers see it transparently.
- **Phase 6 may leave this file untouched** if the weak default is sufficient. The planner's prompt lists it under "to modify" — confirm with the operator whether they want a Leonardo strong override (e.g., to add a `SERIAL_DEBUG` hex-dump path on Leonardo too) or to leave the file at zero diff. Default: zero diff for Leonardo.

---

### `firestarter/include/rurp_shield.h` (MODIFY — add `rurp_log_id` declaration)

**Analog:** itself, lines 132-133.

**Lines to read first:** `firestarter/include/rurp_shield.h:106-129`.

**Pattern to mirror — add declaration immediately after `rurp_log_P`:**

```cpp
    void rurp_log(PGM_P type, const char* msg);
    void rurp_log_P(PGM_P type, PGM_P msg);

    // NEW (Phase 6):
    void rurp_log_id(uint8_t id, const uint8_t* params, uint8_t param_count);
```

**Conventions called out:**
- **4-space indentation** for prototypes inside the `extern "C"` block — see lines 111-159. Match exactly.
- **Single-line prototypes** (no inline doc comments) for `rurp_log` / `rurp_log_P`. New declaration can carry a 1-2 line comment per RESEARCH.md §"Declaration", but keep it short and put the longer narrative in the .cpp implementation file.
- **Plain `uint8_t` types** for the param-count helper signature — header already pulls in `<stdint.h>` at line 15, so `uint8_t` is available without further includes.

**Gotchas:**
- The header is `extern "C"`-wrapped (lines 11-13 + 172-174). The new prototype lands INSIDE that block. `void rurp_log_id(uint8_t id, const uint8_t* params, uint8_t param_count);` is valid C and C++ — no overloading hazard.

---

### `firestarter_app/firestarter/serial_comm.py` (MODIFY — always-on byte-stream reader + fw-guard)

**Analog:** itself, lines 213-231 (`_read_and_parse_lines`) and 362-436 (`_probe_port`).

**Lines to read first:** `firestarter_app/firestarter/serial_comm.py:28-58` (Response namedtuple, EXPECTED_PREFIXES, PREFIX_REGEX), `163-211` (`_parse_response_line`, `_log_rurp_feedback`), `213-231` (current read loop), `362-415` (`_probe_port` with the fw-version check).

**Pattern to mirror — `Response` namedtuple + rightmost-prefix regex (lines 28-58, 163-188):**

```python
# Define a structured object for responses to improve clarity over tuples.
Response = namedtuple('Response', ['type', 'message'])

EXPECTED_PREFIXES = [
    "OK", "INFO", "DEBUG", "ERROR", "WARN", "DATA", "MAIN", "INIT", "END",
]
PREFIX_REGEX = re.compile(rf"({'|'.join(EXPECTED_PREFIXES)}):(.*)")
```

…and the rightmost-match logic:

```python
matches = list(PREFIX_REGEX.finditer(line_str))
if matches:
    match = matches[-1]
    return Response(type=match.group(1), message=match.group(2).strip())
```

**Pattern to mirror — current read loop (the thing being REPLACED — see lines 213-231):**

```python
def _read_and_parse_lines(self, timeout: float) -> Generator[Response, None, None]:
    """A generator that continuously reads lines from the serial port,
    parses them, logs them, and yields them as Response objects.
    Resets the timeout if any data is received."""
    if not self.is_connected():
        raise SerialError("Not connected.")

    start_time = time.time()
    while time.time() - start_time < timeout:
        line_bytes = self.read_line_bytes()
        if line_bytes:
            response = self._parse_response_line(line_bytes)
            if response:
                self._log_rurp_feedback(response)
                yield response
                start_time = time.time()  # Reset timeout on any valid line
        time.sleep(0.01)  # Prevent busy-waiting
```

**Pattern to mirror — `_probe_port` fw-version check (lines 380-415; the new pre-v3 guard slots in here):**

```python
if msg and "FW:" in msg:
    match = re.search(r"FW:\s*([\d.x]+)", msg)
    if match:
        current_version = match.group(1).strip()
        if not SerialCommunicator._is_version_sufficient(current_version, "2.0.0"):
            raise FirmwareOutdatedError(
                f"Firmware version {current_version} is outdated. "
                f"Version 2.0.0 or higher is required. "
                f"Please upgrade the firmware using 'firestarter fw --install'."
            )
```

**Conventions called out:**
- **`namedtuple` is the public response surface** — `LogMessage` (new) MUST live alongside `Response` at the top of the module (lines ~29) and follow the same naming pattern: `LogMessage = namedtuple('LogMessage', ['severity', 'text', 'id'])`.
- **`Generator[Response, None, None]` return type** — keep the public signature of `_read_and_parse_lines` unchanged so the existing `get_response`, `expect_ack`, `consume_remaining_input` consumers (lines 233-283) need ZERO changes. The new loop yields `Response` for both text-line and ID-frame branches; the binary-frame branch internally builds a `LogMessage` then translates `→ Response(type=severity, message=text)` before yielding (per RESEARCH.md §"`LogMessage` as a Public Surface").
- **`logger.warning(...)` for CRC failure / unknown ID** — line 245 shows the pattern (`logger.warning("Timeout waiting for...")`). Mirror for `logger.warning(f"CRC mismatch for ID 0x{msg_id:02x}: ...")`.
- **`FirmwareOutdatedError` is already declared at line 80** — re-use it for the pre-v3 refuse. Same exception class; new error message wording per RESEARCH.md §"Operator-Facing Error Message Wording".
- **`_is_version_sufficient` static method (lines 347-359)** — re-usable for both the existing v2.0.0 floor AND a `major < 3` check. The new guard adds a separate `int(current_version.split(".")[0]) < 3` check upstream of the existing v2.0.0 comparison.
- **`MAGIC_PREAMBLE` as a module-level constant** — match the style of `EXPECTED_PREFIXES`, `DEFAULT_SERIAL_TIMEOUT` (uppercase, module-level, immediately after `Response = namedtuple(...)`). `MAGIC_PREAMBLE = b'\xAA\x55\xAA\x55'`.

**Gotchas:**
- The existing `read_line_bytes` (lines 153-161) uses `self.connection.readline()` (waits for `\n`). The new byte-stream reader uses `self.connection.read(1)` instead — DO NOT call `read_line_bytes` from the new loop. The old method stays untouched for backward compatibility (some callers may still want a single-line read).
- The host's `_parse_response_line` filters non-printable bytes BEFORE the regex (lines 170-172: `res_bytes = bytes(b for b in line_bytes if 32 <= b <= 126)`). The new text-line branch in the always-on loop MUST go through `_parse_response_line` unchanged so the ghost-byte tolerance survives. The binary-frame branch bypasses this filter entirely (by definition, the bytes are non-printable).
- The `_probe_port` block at lines 384-409 has multi-tier exception handling (`FirmwareOutdatedError`, `(IndexError, AttributeError)`, etc.). The new pre-v3 guard adds another `try/except` for `int(...)` parsing; mirror the existing wording style of the error messages — they use multi-sentence `f"..."` with the concrete remedy embedded.
- **`FIRESTARTER_DEV_ALLOW_PRE_V12=1` escape hatch (RESEARCH.md §"Pragma")** — check via `os.environ.get("FIRESTARTER_DEV_ALLOW_PRE_V12") == "1"` and skip the major-version check when set. This MUST land in the same block as the version comparison so dev-mode bench testing continues working through Phase 7-8.

---

### `firestarter_app/firestarter/firmware.py` (MODIFY — `check_current_firmware` lines 55-97)

**Analog:** itself, lines 55-97.

**Lines to read first:** `firestarter_app/firestarter/firmware.py:55-97`.

**Pattern to mirror — current shape:**

```python
def check_current_firmware(
    self, preferred_port: str | None = None,
    flags: int = 0,
) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """Checks the currently installed firmware version on the programmer.
    Returns: (port_name, current_version, board_name) or (None, None, None) on failure."""
    logger.info("Reading current firmware version...")
    command_dict = {"state": COMMAND_FW_VERSION}
    if flags:
        command_dict["flags"] = flags
    comm = None
    try:
        comm = SerialCommunicator.find_and_connect(
            command_dict, self.config_manager, preferred_port=preferred_port
        )
        is_ok, msg = comm.expect_ack()
        # ...
    except (ProgrammerNotFoundError, SerialError) as e:
        logger.error(f"Failed to read firmware version: {e}")
        return None, None, None
    finally:
        if comm:
            comm.disconnect()
```

**Conventions called out:**
- **`Tuple[Optional[str], Optional[str], Optional[str]]` return** — three-element tuple of port/version/board; preserve the signature. The new pre-v3 guard fires INSIDE `find_and_connect` (which calls `_probe_port`) and raises `FirmwareOutdatedError`. `check_current_firmware`'s outer `except (ProgrammerNotFoundError, SerialError)` currently catches `SerialError` but NOT `FirmwareOutdatedError` — that's intentional: `FirmwareOutdatedError` propagates upward to `manage_firmware_update`. **Verify the propagation is clean** — `FirmwareOutdatedError` inherits from `SerialError` (line 80-83), so the existing `except (ProgrammerNotFoundError, SerialError)` clause WOULD catch it. The current code at lines 91-93 catches it as a generic `SerialError` and returns `(None, None, None)`. For Phase 6, the new guard's error message is informative enough that swallowing it inside `check_current_firmware` is acceptable — the operator sees the `logger.error` message. Confirm with planner: either keep swallow + log, or add `except FirmwareOutdatedError: raise` BEFORE the broad catch.
- **`logger.info` / `logger.error`** discipline — mirrors lines 63, 82, 87, 92. New pre-v3 guard logs via `logger.error` if it ends up handling the exception locally.

**Gotchas:**
- The `serial_comm.py:_probe_port` lines 471-475 already re-raises `FirmwareOutdatedError` from `find_and_connect`. `check_current_firmware`'s `except SerialError` clause WILL swallow it (per the inheritance chain). The Phase 6 plan should verify whether the operator wants the pre-v3 error to surface DIRECTLY (re-raise) or be swallowed (current behaviour with v2.0.0 floor). RESEARCH.md §"Host FW-Version Refuse Guard" implies surfacing; planner picks.

---

### `firestarter/test/native/avr/test_messages/test_rurp_log_id.cpp` (NEW — native Unity test for `rurp_log_id`)

**Analog:** `firestarter/test/native/avr/test_dispatch/test_configure_memory.cpp` (exact role match — Unity suite under `[env:native]`, exercises a single firmware function via ArduinoFake).

**Lines to read first:** `firestarter/test/native/avr/test_dispatch/test_configure_memory.cpp:1-50, 157-183`.

**Pattern to mirror — Unity setUp/tearDown + RUN_TEST main:**

```cpp
#include <Arduino.h>
#include <ArduinoFake.h>
#include <unity.h>

extern "C" {
#include "memory.h"
}
#include "firestarter.h"

using namespace fakeit;

void setUp(void) {
    ArduinoFakeReset();
}

void tearDown(void) {
}

/* Build a zero-initialized handle with only the three named fields set. */
static firestarter_handle_t make_handle(uint32_t protocol, uint8_t mem_type, uint8_t cmd) {
    firestarter_handle_t h = {};
    h.protocol = protocol;
    h.mem_type = mem_type;
    h.cmd = cmd;
    h.response_code = RESPONSE_CODE_OK;
    return h;
}

void test_protocol_0x06_dispatches_flash3(void) {
    firestarter_handle_t h = make_handle(0x06, 0, CMD_READ);
    configure_memory(&h);
    TEST_ASSERT_NOT_EQUAL(RESPONSE_CODE_ERROR, h.response_code);
}

// ...

int main(int argc, char** argv) {
    (void)argc;
    (void)argv;
    UNITY_BEGIN();
    RUN_TEST(test_protocol_0x06_dispatches_flash3);
    // ...
    return UNITY_END();
}
```

**Conventions called out:**
- **`extern "C" { #include "<header>.h" }`** — required because the Unity TU is compiled as C++ (test framework is C++-y) but the firmware headers are mostly C with `extern "C"` guards. Match line 35-37 exactly. For the new test, include `rurp_shield.h` and `messages.h`:
  ```cpp
  extern "C" {
  #include "rurp_shield.h"
  #include "messages.h"
  }
  ```
- **`using namespace fakeit;`** — required for any `Mock(...)` / `When(...).Return(...)` usage from ArduinoFake.
- **`void setUp` calls `ArduinoFakeReset()`** — REQUIRED to clear mock state between tests.
- **One file per suite; flat `void test_*` functions; explicit `RUN_TEST` in `main`** — NO test discovery magic. The Phase 6 test file lists every test in `main` exactly like lines 162-180.
- **TEST_ASSERT_*** — Unity macros. Use `TEST_ASSERT_EQUAL_UINT8`, `TEST_ASSERT_EQUAL_HEX8`, `TEST_ASSERT_EQUAL_MEMORY` for byte-stream comparisons. Reference: line 66 (`TEST_ASSERT_NOT_EQUAL`).
- **Comment block at top explains test scope** — lines 1-29 of `test_configure_memory.cpp` document RED-state, what the test asserts, and why a particular assertion shape was chosen. Mirror this for the new file (document: "rurp_log_id emits the exact wire frame `AA 55 AA 55 | len | id | params | crc | 0A` per CONTEXT.md §D-01").

**Gotchas:**
- **`SERIAL_PORT.write` is a `Mock`** — capture writes via:
  ```cpp
  When(Method(ArduinoFake(Serial), write).Using(Any<uint8_t>())).AlwaysReturn(1);
  // ... call rurp_log_id(...) ...
  Verify(Method(ArduinoFake(Serial), write).Using(0xAA)).Once();
  ```
  Pattern reference: ArduinoFake docs (this repo doesn't have an existing example beyond ArduinoFakeReset; check `lib_deps = fabiobatsilva/ArduinoFake@^0.4.0` in `platformio.ini:53`).
- **`com_mode` global** is defined in Uno's TU (`uno_rurp_shield.cpp:19`) — that TU is EXCLUDED from `[env:native]` (`src_filter = +<proms/>` excludes `src/boards/`). The Phase 6 test must NOT depend on `com_mode` being defined; the weak default in `rurp_serial_utils.cpp` doesn't check it. RESEARCH.md says rurp_serial_utils.cpp is *also* excluded by `src_filter = +<proms/>` — so test_messages will need its own `host_stubs.cpp` that provides `_firestarter_emit_frame` either as the real implementation (re-compiled in the test build) or a mock. **Planner picks**: either widen `src_filter` to `+<proms/> +<boards/rurp_serial_utils.cpp>` for the test_messages suite, or provide a host-side `_firestarter_emit_frame` stub that captures writes.
- **`UNITY_BEGIN` / `UNITY_END` are mandatory** — lines 160, 181. Without them, the test binary exits without running any tests (silent green).

---

### `firestarter/test/native/avr/test_messages/host_stubs.cpp` (NEW — native test stubs)

**Analog:** `firestarter/test/native/avr/test_dispatch/host_stubs.cpp` (exact pattern — copy-and-adapt).

**Lines to read first:** `firestarter/test/native/avr/test_dispatch/host_stubs.cpp:1-160` (entire file).

**Pattern to mirror — file-header comment block + `extern "C"` blocks + PROGMEM string replication:**

```cpp
/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 *
 * Phase 12 Wave 1 — host stub TU for the [env:native] dispatch test build.
 *
 * Compiling firmware sources (src/proms/*.cpp) on platform = native leaves
 * the linker hungry for hardware-side symbols defined in the AVR-only TUs
 * (src/boards/*.cpp, src/logging.c). This TU provides no-op host
 * implementations of every rurp_* symbol the proms reference, plus the
 * PROGMEM log-tag globals from src/logging.c, so the dispatch test binary
 * can link.
 */

#include <stdint.h>
#include <stddef.h>
#include <string.h>

extern "C" {
#include "rurp_shield.h"
#include "rurp_types.h"
}

/* PROGMEM log-tag strings — defined in src/logging.c on AVR; replicated here
 * so the [env:native] link finds them. The PSTR() macro in the pgmspace stub
 * is a no-op, so these are plain const char[] in the host binary. */
extern "C" {
const char LOG_OK_MSG[] PROGMEM = "OK";
const char LOG_INIT_DONE_MSG[] PROGMEM = "INIT";
// ...
}

/* rurp_log* — no-op on host. The dispatch test never reads serial output. */
extern "C" void rurp_log(PGM_P type, const char* msg) {
    (void)type;
    (void)msg;
}
```

**Conventions called out:**
- **`extern "C"` blocks around symbol definitions** — REQUIRED to match the `extern "C"` declarations in `rurp_shield.h`. Match lines 31-34, 39-48 exactly.
- **`(void)param;` to silence unused-param warnings** — mirror lines 52-54.
- **MIT copyright + Phase reference block** — line 1-25. New file: update phase to "Phase 6" and the rationale paragraph.
- **No `pio test` directives** — the file is auto-discovered by PIO via its `test/native/avr/<dirname>/*.cpp` glob. No `extra_scripts` or `lib_deps` changes needed.

**Pattern to mirror — PROGMEM table replication for `messages.c`:**

If `src/messages.c` is NOT pulled into `[env:native]` via widened `src_filter`, the new `host_stubs.cpp` must replicate the PROGMEM table:

```cpp
extern "C" {
const uint8_t MSG_PARAM_BYTES_TABLE[256] PROGMEM = {
    [0x00] = 0xFF,
    [0x01] = 0,
    [0x02] = 0,
    // ... full 52 entries from messages.toml
};
}
```

**Gotchas:**
- The new file MUST stub `_firestarter_emit_frame` IF the test doesn't widen `src_filter` to include `boards/rurp_serial_utils.cpp`. Two paths:
  - **Stub path:** capture writes via a host-side global `std::vector<uint8_t>` or similar, expose to the test via an `extern` accessor — the test asserts byte-for-byte against this buffer.
  - **Real path:** widen `src_filter` to `+<proms/> +<boards/rurp_serial_utils.cpp>` in `platformio.ini` `[env:native]`. This pulls the real CRC8 table and frame-emit logic into the test binary; ArduinoFake's `Serial.write` mock captures bytes.

  RESEARCH.md prefers the real path because it validates production code end-to-end. Planner picks; document in the wave that lands this file.

---

### `firestarter/test/native/avr/test_messages/avr/pgmspace.h` (NEW — pgm shim)

**Analog:** `firestarter/test/native/avr/test_dispatch/avr/pgmspace.h` (exact pattern — copy verbatim, no changes).

**Lines to read first:** `firestarter/test/native/avr/test_dispatch/avr/pgmspace.h:1-63` (entire file).

**Pattern to mirror — exact verbatim copy:**

```cpp
/*
 * Phase 12 Wave 0 — host-side stub for <avr/pgmspace.h>
 *
 * ...
 */
#ifndef _AVR_PGMSPACE_H_STUB_
#define _AVR_PGMSPACE_H_STUB_

#include <stdint.h>
#include <string.h>

#ifndef PROGMEM
#define PROGMEM
#endif

#ifndef PSTR
#define PSTR(s) (s)
#endif

#ifndef PGM_P
#define PGM_P const char *
#endif

#ifndef pgm_read_byte
#define pgm_read_byte(addr) (*(const uint8_t*)(addr))
#endif

// ... (other pgm_read_word, pgm_read_dword, pgm_read_ptr, strcpy_P, strlen_P, memcpy_P)

#endif /* _AVR_PGMSPACE_H_STUB_ */
```

**Conventions called out:**
- **Header guard `_AVR_PGMSPACE_H_STUB_`** — exact name (matches the existing shim's guard).
- **All defines are `#ifndef`-guarded** — REQUIRED because ArduinoFake provides its own `<arduino/pgmspace.h>` later in the include order. Without `#ifndef`, redefinition warnings fail the build (per the existing file's comment at line 27-33).

**Gotchas:**
- This file is a verbatim copy; only the phase reference in the header comment needs updating ("Phase 6 — host-side stub for `<avr/pgmspace.h>`"). NO other changes.

---

### `firestarter_app/tests/test_decoder.py` (NEW — LHOST-01 decoder fixture)

**Analog:** `firestarter/test/native/avr/test_dispatch/test_configure_memory.cpp` (different language — pytest vs Unity — but identical role: hermetic unit test, one assertion per case, exhaustive enumeration of inputs).

**Lines to read first:** `firestarter_app/firestarter/serial_comm.py:163-211` (the function being tested + the `Response` shape) and `firestarter/test/native/avr/test_dispatch/test_configure_memory.cpp:42-180` (RED-state + per-case test structure).

**Pattern to mirror — test class with one method per assertion case:**

The firmware Unity precedent uses flat `void test_*()` + explicit `RUN_TEST`. pytest convention is a class with `def test_*(self):` methods (auto-discovered). The two are isomorphic; the Phase 6 test file follows the pytest convention (RESEARCH.md §"LHOST-01 Acceptance Fixture" gives the full skeleton).

```python
import io
import pytest
from firestarter.serial_comm import (
    SerialCommunicator,
    LogMessage,
    MAGIC_PREAMBLE,
)
from firestarter.messages import CATALOG, MSG_INFO_ADDR, MSG_ERR_WRITE_FAILED


def _crc8_ccitt(data: bytes) -> int:
    """Reference CRC8 — duplicates the implementation in messages.py for test isolation."""
    crc = 0
    for b in data:
        crc ^= b
        for _ in range(8):
            crc = ((crc << 1) ^ 0x07) & 0xFF if (crc & 0x80) else (crc << 1) & 0xFF
    return crc


def _build_frame(msg_id: int, params: bytes) -> bytes:
    body = bytes([msg_id]) + params
    crc = _crc8_ccitt(body)
    length = len(body) + 1
    return MAGIC_PREAMBLE + bytes([length]) + body + bytes([crc, 0x0A])


class TestIdFrameDecoder:
    def test_zero_param_frame_yields_logmessage(self):
        frame = _build_frame(0x01, b"")
        result = _decode_via_serial_comm(frame)
        assert isinstance(result, LogMessage)
        assert result.severity == "OK"
        assert result.text == "Ready"
```

**Conventions called out:**
- **One file per concern** — `test_decoder.py` for LHOST-01/02/03, `test_fwguard.py` for LFW-05/LHOST-04, `test_catalog_parse.py` for codegen validity. Mirrors the firmware suite's "one suite per directory" structure (`test_dispatch/`, `test_messages/`).
- **Class-based grouping (`class TestIdFrameDecoder:`)** — pytest auto-discovers `Test*` classes and `test_*` methods. This mirrors the Unity suite's `void test_*()` pattern.
- **Per-test one-line docstring** — line 1188-1191 of RESEARCH.md show the pattern; match the Unity suite's "/* Comment explains scope */" precedent (test_configure_memory.cpp lines 63-67).
- **Hermetic — no `pyserial` import for the actual hardware port** — use a `_FakeSerial` class that wraps `io.BytesIO`. This mirrors the Unity `ArduinoFake` mock (test_configure_memory.cpp:42-44).

**Gotchas:**
- The host sub-repo has **zero existing pytest infrastructure** (`find . -name 'test_*.py'` returns empty). Phase 6 introduces:
  - `firestarter_app/tests/__init__.py` (empty, just makes `tests/` a package).
  - `firestarter_app/tests/conftest.py` (shared `_FakeSerial` fixture + `_build_frame` helper).
  - `pyproject.toml` `[project.optional-dependencies] dev = ["pytest>=7.0"]` block.
  - `pyproject.toml` `[tool.pytest.ini_options]` section setting `testpaths = ["tests"]` and `addopts = "-ra -q"`.
- **`MAGIC_PREAMBLE` is imported from `serial_comm`** — exposed as a module-level constant so tests don't hard-code the bytes. Same import shape as `from firestarter.constants import *` (line 22 of serial_comm.py).
- **`SerialCommunicator.__new__(SerialCommunicator)`** is the way to construct an instance without invoking `__init__` (which tries to open a real serial port). See RESEARCH.md `_decode_via_serial_comm` helper at lines 1259-1271.

---

### `firestarter_app/tests/test_fwguard.py` (NEW — LFW-05 + LHOST-04 fw-version refuse guard)

**Analog:** `firestarter/test/native/avr/test_dispatch/test_configure_memory.cpp` (role-match: hermetic unit test asserting one function's behaviour against multiple inputs).

**Lines to read first:** `firestarter_app/firestarter/serial_comm.py:362-436` (the function being tested + the `FirmwareOutdatedError` raise sites).

**Pattern to mirror — `unittest.mock.patch.object` to short-circuit serial connection:**

```python
import pytest
from unittest.mock import MagicMock, patch
from firestarter.serial_comm import SerialCommunicator, FirmwareOutdatedError


class TestFirmwareVersionGuard:
    def test_refuse_pre_v3_firmware(self):
        mock_msg = "FW: 2.0.11, HW: Rev2, Cmd: 0x0d"
        with patch.object(SerialCommunicator, "expect_ack", return_value=(True, mock_msg)), \
             patch.object(SerialCommunicator, "send_json_command", return_value=42), \
             patch.object(SerialCommunicator, "consume_remaining_input", return_value=None), \
             patch.object(SerialCommunicator, "__init__", lambda self, port, **k: None):
            with pytest.raises(FirmwareOutdatedError, match="pre-v1.2"):
                SerialCommunicator._probe_port(
                    port_name="/dev/null",
                    baud_rate=250000,
                    command_to_send={"state": 1},
                    config_manager=MagicMock(),
                )
```

**Conventions called out:**
- **`pytest.raises(FirmwareOutdatedError, match="...")`** — the `match` kw asserts on the exception message text. Use the operator-facing wording from RESEARCH.md §"Operator-Facing Error Message Wording" so the test fails if anyone softens the message.
- **Multi-`patch.object` with backslash continuation** — RESEARCH.md `test_fw_version_guard.py` shows this. Match exactly.
- **`monkeypatch.setenv("FIRESTARTER_DEV_ALLOW_PRE_V12", "1")`** for the escape-hatch test — pytest's `monkeypatch` fixture is the standard way to mutate env vars per-test (auto-restored after the test).

**Gotchas:**
- The `_probe_port` static method's signature in `serial_comm.py:362-370` is `(port_name, baud_rate, command_to_send, config_manager)`. Tests MUST pass `port_name` positionally and `config_manager=MagicMock()` so the function doesn't try to call `.set_value("port", ...)` against `None`.
- **`FirmwareOutdatedError` inherits from `SerialError`** (line 80-83) which inherits from `Exception`. Tests catch the specific subclass; don't broaden to `SerialError` (would mask the assertion).

---

### `firestarter_app/.github/workflows/ci.yml` (NEW — host CI workflow)

**Analog:** `firestarter/.github/workflows/build.yml` (firmware CI — same shape: setup-python, install deps, run gate, run tests).

**Lines to read first:** `firestarter/.github/workflows/build.yml:1-62` (entire file).

**Pattern to mirror — workflow shape (header + jobs):**

```yaml
name: Firestarter CI
on:
  push:
    branches:
    - main
    paths-ignore:
    - '**.md'
    - '**.sh'
    - '.gitignore'
    - 'docs/**'
    - 'documents/**'
    - 'test/**'
    - 'images/**'
    - '.github/**'
    - '.vscode/**'
    - '.editorconfig/**'
    - 'tools/**'

jobs:
  build:
    runs-on: ubuntu-latest
    permissions:
      contents: write

    steps:
      - uses: actions/checkout@v4

      - uses: actions/cache@v4
        with:
          path: |
            ~/.cache/pip
            ~/.platformio/.cache
          key: ${{ runner.os }}-pio

      - uses: actions/setup-python@v4
      # ...
      - name: Install PlatformIO Core
        run: pip install --upgrade platformio

      - name: Build PlatformIO Project
        run: pio run
```

**Conventions called out:**
- **`name:` is the displayed workflow title** — pick "CI" or "Host CI" for the new host workflow.
- **`on: push: branches: [main]` + `paths-ignore`** — match the firmware sub-repo's filter so docs-only commits don't trigger CI.
- **`runs-on: ubuntu-latest` + `actions/checkout@v4`** — standard. Match version exactly.
- **`actions/setup-python@v4`** — note the version. RESEARCH.md uses `v5` for the codegen step; `v4` is fine too. Match whichever the existing firmware build.yml uses for consistency.
- **CRITICAL: remove `'tools/**'` from the host CI's `paths-ignore`** — for the firmware CI, `tools/` is excluded (the firmware tools dir is just `build_db.py` etc.). For Phase 6, edits to `tools/catalog/messages.toml` or `tools/catalog/codegen.py` MUST trigger CI on both sub-repos — otherwise the drift gate is meaningless. **Drop `'tools/**'` from `paths-ignore`** in the new host ci.yml (and remove it from the firmware build.yml in the modify step).

**Pattern to mirror — codegen drift gate (RESEARCH.md §"firestarter_app CI" lines 1314-1347):**

```yaml
      - name: Codegen drift gate (messages.py)
        run: |
          python3 tools/catalog/codegen.py \
            --catalog tools/catalog/messages.toml \
            --target firestarter/messages.py \
            --language python
          git diff --exit-code firestarter/messages.py

      - name: Catalog validity check
        run: python3 tools/catalog/codegen.py --catalog tools/catalog/messages.toml --check

      - name: Install dev dependencies
        run: pip install -e . pytest

      - name: Run pytest
        run: pytest tests/ -v
```

**Gotchas:**
- The host sub-repo currently has only `release.yml` (release-on-push) and `publish.yml` (publish-on-release). Neither runs any tests; Phase 6 adds the first ever real CI workflow.
- **`git diff --exit-code firestarter/messages.py`** is the load-bearing assertion — if the committed file differs from the regenerated one, the step exits non-zero and CI fails. Test this manually before merging by deliberately editing `messages.py` and pushing a branch.
- The new `ci.yml` MUST run on `pull_request` events too — the existing `release.yml` runs on `push: main` only. Add `pull_request: branches: [main]` to the `on:` block so PRs see drift failures before merge.

---

### `firestarter/.github/workflows/build.yml` (MODIFY — add codegen drift gate)

**Analog:** itself, lines 26-53 (existing build steps).

**Lines to read first:** `firestarter/.github/workflows/build.yml:25-53`.

**Pattern to mirror — step shape (each step has `name:` + `run: |` multi-line bash):**

```yaml
      - uses: actions/setup-python@v4

      - name: Generate release version
        id: version
        run: .github/scripts/update_version.py

      - uses: stefanzweifel/git-auto-commit-action@v5

      - name: Install PlatformIO Core
        run: pip install --upgrade platformio

      - name: Build PlatformIO Project
        run: pio run
```

**Pattern to mirror — INSERT the drift gate BEFORE "Install PlatformIO Core" (RESEARCH.md §"firestarter CI" lines 1280-1304):**

```yaml
      - name: Set up Python (for codegen)
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Codegen drift gate (messages.h)
        run: |
          python3 tools/catalog/codegen.py \
            --catalog tools/catalog/messages.toml \
            --target include/messages.h \
            --language cpp
          python3 tools/catalog/codegen.py \
            --catalog tools/catalog/messages.toml \
            --target src/messages.c \
            --language cpp-table
          git diff --exit-code include/messages.h src/messages.c

      - name: Catalog validity check
        run: python3 tools/catalog/codegen.py --catalog tools/catalog/messages.toml --check
```

**Conventions called out:**
- **6-space indent for `- name:`** — matches existing file's indent style. Match exactly.
- **`run: |` for multi-line bash** — line 31-32 (paths-ignore is a YAML list, not a multi-line string). The drift gate's multi-step bash uses `run: |` with `\`-continued lines.
- **Step order:** `checkout → cache → setup-python → generate version → codegen → install pio → build → release`. Codegen lands BEFORE `Install PlatformIO Core` per RESEARCH.md so a failed codegen short-circuits the slower PIO install.

**Gotchas:**
- The existing workflow uses `actions/setup-python@v4` at line 35. The codegen drift gate's `actions/setup-python@v5` is a different invocation (passes `python-version: '3.11'` explicitly to ensure `tomllib` is available). DO NOT collapse both — keep them as two separate setup-python steps OR upgrade the existing one to `@v5` + `python-version: '3.11'`.
- **Remove `'tools/**'` from `paths-ignore` (line 17)** — same rationale as the host ci.yml: edits to `tools/catalog/messages.toml` and `tools/catalog/codegen.py` MUST trigger the drift gate.

---

### `firestarter_app/.github/workflows/release.yml` AND `publish.yml` (MODIFY — push CI into new ci.yml, leave release/publish as-is)

**Analog:** existing `release.yml:1-44` and `publish.yml:1-19`.

**Lines to read first:** both files (small, already shown above).

**Pattern to mirror — `release.yml` is the model for "this workflow runs only on release events; don't add test/codegen here":**

The current `release.yml` runs `.github/scripts/update_version.py` and creates a GitHub release tag. `publish.yml` runs `python3 -m build` + `gh-action-pypi-publish` on release-published.

**Recommendation per RESEARCH.md §"firestarter_app CI"**: do NOT add codegen drift to these workflows. Put codegen drift in the NEW `ci.yml`. The two existing workflows stay untouched.

**Conventions called out:**
- **Separation of concerns** — `release.yml` = tag creation, `publish.yml` = PyPI push, new `ci.yml` = test gate. Don't multi-purpose a workflow.

**Gotchas:**
- **If the host CI doesn't gate releases**, an operator could push a bad catalog → tag created → PyPI publishes a broken release. Mitigation: add a "needs: ci" dependency in `release.yml` so it waits for the new `ci.yml` to succeed. RESEARCH.md doesn't call this out explicitly; planner can decide. Conservative path: add `needs: [ci]` to release.yml's `github:` job.

---

### `firestarter/platformio.ini` (MODIFY — confirm `[env:native]` supports the new test suite)

**Analog:** itself, lines 43-62 (the entire `[env:native]` section).

**Lines to read first:** `firestarter/platformio.ini:43-62`.

**Pattern to mirror — current `[env:native]` config:**

```ini
[env:native]
platform = native
test_framework = unity
build_flags =
	${env.build_flags}
	-std=gnu++17
	-I include
	-I test/native/avr/test_dispatch
	-D RURP_BOARD_NAME=\"native\"
lib_deps =
	fabiobatsilva/ArduinoFake@^0.4.0
; Phase 12 Wave 1: pull in ONLY src/proms/*.cpp from the firmware tree so
; configure_memory() and the configure_*() handlers link into the host
; test binary. AVR-only sources (src/boards/*.cpp, src/dev_tools.cpp,
; src/eprom_operations.cpp, src/logging.c) are excluded; their rurp_log
; / rurp_* / PROGMEM-string symbols are stubbed by
; test/native/avr/test_dispatch/host_stubs.cpp (auto-discovered by PIO
; under test/).
src_filter = +<proms/>
test_build_src = yes
```

**Pattern to mirror — change required for `test_messages` suite:**

Add an `-I test/native/avr/test_messages` line to `build_flags`. (PIO does NOT auto-add include paths for new test directories; you must list each one explicitly. Reference: line 50 adds `-I test/native/avr/test_dispatch`.)

Optionally widen `src_filter` (per the "Gotcha" in the `host_stubs.cpp` section above) to:

```ini
src_filter = +<proms/> +<boards/rurp_serial_utils.cpp> +<messages.c>
```

…so `_firestarter_emit_frame` and the 256-byte `MSG_PARAM_BYTES_TABLE` PROGMEM array are linked from production sources rather than re-stubbed. Planner picks; document the choice in the wave that lands this change.

**Conventions called out:**
- **Tab indentation in build_flags** — see lines 28-30, 38-41 etc. PlatformIO accepts both tabs and spaces, but tabs are the prevailing style. Match.
- **Inline `;` comments** are standard INI — the existing `[env:leonardo]` line 40 (`; TEMP: 512 to match Uno...`) uses this. New `src_filter` edits should carry a comment ("; Phase 6: include rurp_serial_utils.cpp + messages.c for test_messages suite").

**Gotchas:**
- `src_filter = +<proms/>` is **load-bearing** for the dispatch test — widening it must NOT regress the dispatch test. Verify by running `pio test -e native -f "*test_dispatch*"` after the change.
- The native env passes `-D HARDWARE_REVISION` (transitively via `${env.build_flags}` at line 16). The `#ifdef HARDWARE_REVISION` blocks in `rurp_shield.h:35-89` are active in native; `rurp_register_t` is a 16-bit field. This is fine for the new test (no register I/O involved), but document it in the test's header comment.

---

### `firestarter_app/pyproject.toml` (MODIFY — add `[tool.pytest.ini_options]` + dev dep on pytest)

**Analog:** itself, the existing `[project]` + `[tool.setuptools]` blocks.

**Lines to read first:** `firestarter_app/pyproject.toml:1-73` (entire file).

**Pattern to mirror — existing block structure (TOML table headers + key-value pairs):**

```toml
[project]
authors = [{ name = "Henrik Olsson", email = "henols@gmail.com" }]
name = "firestarter"
# ...
dependencies = [
    "pyserial>=3.5",
    "requests>=2.20",
    "tqdm>=4.60",
    "argcomplete>=3.6.2",
    "rich>=14.0",
]

[tool.setuptools]
include-package-data = true
packages = ["firestarter"]
```

**Pattern to add — `[project.optional-dependencies]` dev block + `[tool.pytest.ini_options]`:**

```toml
[project.optional-dependencies]
dev = [
    "pytest>=7.0",
]

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-ra -q"
```

**Conventions called out:**
- **4-space TOML indentation inside multi-line arrays** — see `dependencies = [...]` (lines 48-54) and `classifiers = [...]` (lines 32-46). Match exactly.
- **Alphabetical-ish ordering inside dependency arrays** — `pyserial, requests, tqdm, argcomplete, rich` is not strictly alphabetical (`argcomplete` < `pyserial`), so the file doesn't enforce strict alpha. Group by purpose: runtime deps first, dev deps in their own block.
- **TOML table header order** — `[build-system]` → `[tool.setuptools_scm]` → `[project]` → `[project.scripts]` → `[tool.setuptools]` → `[tool.setuptools.package-data]` → `[tool.setuptools.dynamic]`. New `[project.optional-dependencies]` goes between `[project]` and `[project.scripts]`; new `[tool.pytest.ini_options]` goes at the end of the file (after `[tool.setuptools.dynamic]`).

**Gotchas:**
- **`requires-python = ">=3.9"` stays unchanged** — `pytest>=7.0` supports Python 3.7+, no need to bump the minimum. The codegen `tomllib` requires Python ≥3.11, but the codegen runs only at the meta-repo / CI level; the installed package itself (`firestarter`) doesn't need `tomllib`.
- The host sub-repo today **has no `requirements.txt`** — everything's in `pyproject.toml`. Do NOT introduce a new `requirements.txt`; add `pytest` to `[project.optional-dependencies]` and install via `pip install -e .[dev]` in CI.

---

## Shared Patterns

### Auth / Gating

#### `com_mode` gate (firmware)
**Source:** `firestarter/src/boards/uno_rurp_shield.cpp:19, 85, 97`
**Apply to:** Uno strong override of `rurp_log_id` (must `if (com_mode)` before emitting; mirrors `rurp_log`).
```cpp
bool com_mode = true;  // global at file scope

void rurp_log(PGM_P type, const char* msg) {
    log_debug(type, msg);
    if (com_mode) {
        _firestarter_log_ram(type, msg);
    }
}
```

#### `SERIAL_DEBUG` duplication (firmware)
**Source:** `firestarter/src/boards/uno_rurp_shield.cpp:21-28, 92-96, 154-162`
**Apply to:** Uno strong override of `rurp_log_id` (mirror the `#ifdef SERIAL_DEBUG { strcpy_P + log_debug }` pattern, but render a hex-dump summary since the new frame is binary).
```cpp
#ifdef SERIAL_DEBUG
strcpy_P(debug_msg_buffer, msg);
log_debug(type, debug_msg_buffer);
#endif
```

#### `FLAG_VERBOSE` gate (firmware)
**Source:** `firestarter/include/logging.h:40-43, 45-48, 50-54`
**Apply to:** All new `LOG_INFO_ID*` macros (mirror `log_info_*` discipline — INFO is silent unless `FLAG_VERBOSE` is set; OK/WARN/ERROR/DATA are unconditional).
```cpp
#define log_info_const(msg)                        \
    if (is_flag_set(FLAG_VERBOSE)) {               \
        rurp_log_P(LOG_INFO_MSG, PSTR(msg));       \
    }
```

### Error Handling

#### `FirmwareOutdatedError` propagation (host)
**Source:** `firestarter_app/firestarter/serial_comm.py:80-83, 392-415, 471-475`
**Apply to:** The Phase 6 pre-v3 refuse guard in `_probe_port`. Same `f"..."` multi-sentence error message + concrete remedy + `raise FirmwareOutdatedError(...)`.
```python
class FirmwareOutdatedError(SerialError):
    """Custom exception for outdated firmware."""
    pass

# Inside _probe_port:
if not SerialCommunicator._is_version_sufficient(current_version, "2.0.0"):
    raise FirmwareOutdatedError(
        f"Firmware version {current_version} is outdated. "
        f"Version 2.0.0 or higher is required. "
        f"Please upgrade the firmware using 'firestarter fw --install'."
    )
```

#### CRC mismatch / unknown ID logging (host)
**Source:** `firestarter_app/firestarter/serial_comm.py:245, 506-508` (`logger.warning` style)
**Apply to:** All `_decode_id_frame` failure paths. Use `logger.warning(f"...")` with the ID in hex (`0x{msg_id:02x}`), then return `None` from the decoder so the read loop skips and continues.
```python
logger.warning(f"Timeout waiting for a response from {self.port_name}.")
```

### Validation

#### Designated-initializer PROGMEM table (firmware)
**Source:** `firestarter/src/logging.c:7-14` (extern PROGMEM strings); RESEARCH.md §"Generated `messages.h` Skeleton" lines 519-530 (designated-init form)
**Apply to:** Generated `messages.c` 256-byte `MSG_PARAM_BYTES_TABLE`.
```c
const uint8_t MSG_PARAM_BYTES_TABLE[256] PROGMEM = {
    [0x00] = 0xFF,
    [0x01] = 0,
    // ...
};
```

#### Catalog validation rules (codegen)
**Source:** RESEARCH.md §"Validation Rules (LCAT-02 + LCI-04)" lines 290-303
**Apply to:** `codegen.py --check` mode. 10 explicit rules: unique ID, unique name, well-formed shape, non-empty format, valid severity, valid wire_format, format-string-vs-param-count consistency, 24-byte total param budget.
```python
# (codegen.py validation loop pseudocode)
if msg["id"] in seen_ids:
    raise CatalogError(f"Duplicate ID 0x{msg['id']:02x} for {msg['name']}")
if not re.match(r"^MSG_[A-Z][A-Z0-9_]*$", msg["name"]):
    raise CatalogError(f"Invalid name format: {msg['name']}")
```

### Testing

#### Unity native test main() (firmware)
**Source:** `firestarter/test/native/avr/test_dispatch/test_configure_memory.cpp:157-182`
**Apply to:** `test/native/avr/test_messages/test_rurp_log_id.cpp:main()`. Flat `RUN_TEST` calls, one per test function.
```cpp
int main(int argc, char** argv) {
    (void)argc; (void)argv;
    UNITY_BEGIN();
    RUN_TEST(test_emit_frame_zero_params);
    RUN_TEST(test_emit_frame_u24_payload);
    // ...
    return UNITY_END();
}
```

#### Hermetic mock-based unit test (host)
**Source:** `firestarter/test/native/avr/test_dispatch/test_configure_memory.cpp:42-44` (`setUp(ArduinoFakeReset)`) — pattern translates to pytest's `unittest.mock.patch.object` for the host.
**Apply to:** All new pytest files in `firestarter_app/tests/`. Never open a real serial port; never hit network; never spawn subprocesses.
```python
with patch.object(SerialCommunicator, "__init__", lambda self, port, **k: None):
    # ... test body ...
```

### Naming / Conventions

#### MIT copyright banner (firmware)
**Source:** Every C/C++ file in `firestarter/`. Lines 1-6:
```cpp
/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 */
```
**Apply to:** All new `.cpp`, `.h`, `.c` files. Generated files swap the banner for a DO-NOT-EDIT warning that still leads with the copyright line.

#### Python module docstring banner (host)
**Source:** `firestarter_app/firestarter/serial_comm.py:1-7`, `firmware.py:1-8`:
```python
"""
Project Name: Firestarter
Copyright (c) 2024 Henrik Olsson

Permission is hereby granted under MIT license.

<Module purpose>
"""
```
**Apply to:** `messages.py` (generated — banner is a DO-NOT-EDIT warning), `tests/conftest.py`, `tests/test_*.py`. The banner is one paragraph; module purpose follows.

#### Header guard naming (firmware)
**Source:** All `firestarter/include/*.h`:
- `__RURP_SHIELD_H__` (rurp_shield.h:8)
- `__LOGGING_H__` (logging.h:8)
- `__MESSAGES_H__` (new file — match pattern)

#### Constant casing (host)
**Source:** `firestarter_app/firestarter/constants.py:13-46` — `BAUD_RATE`, `BUFFER_SIZE`, `COMMAND_*`, `FLAG_*`. **Apply to:** New constants in `messages.py` — `SEVERITY_OK = 0x01`, `MSG_OK_READY = 0x01`, etc. All uppercase with underscores; integer constants set to hex with `0x` prefix when they're protocol IDs / flag bits.

---

## No Analog Found

| File | Role | Reason planner falls back to RESEARCH.md |
|------|------|-------------------------------------------|
| `firestarter_app/tests/__init__.py` | pytest package marker | Sub-repo has zero existing pytest infrastructure (`find . -name 'test_*.py'` returns empty). Use the empty-package convention (`# Phase 6 pytest infrastructure` one-line comment + nothing else) — there's no project precedent, but every pytest project follows the same shape. |
| `firestarter_app/tests/conftest.py` | pytest shared fixtures | Same reason — no existing pytest fixtures to mirror. RESEARCH.md §"LHOST-01 Acceptance Fixture" shows the `_FakeSerial`/`_build_frame` helpers; lift them verbatim into conftest.py as `@pytest.fixture` functions. |

---

## Metadata

**Analog search scope:**
- `/workspaces/firestarter_prom/firestarter/include/` (8 headers scanned; primary references: `rurp_shield.h`, `logging.h`, `firestarter.h`)
- `/workspaces/firestarter_prom/firestarter/src/` (`logging.c`, `firestarter.cpp` lines 140-160 for PARSE_RESPONSE)
- `/workspaces/firestarter_prom/firestarter/src/boards/` (3 files: `uno_rurp_shield.cpp`, `leonardo_rurp_shield.cpp`, `rurp_serial_utils.cpp` — all read in full)
- `/workspaces/firestarter_prom/firestarter/test/native/avr/test_dispatch/` (3 files: `test_configure_memory.cpp`, `host_stubs.cpp`, `avr/pgmspace.h` — all read in full)
- `/workspaces/firestarter_prom/firestarter_app/firestarter/` (`serial_comm.py`, `firmware.py`, `constants.py`)
- `/workspaces/firestarter_prom/firestarter_app/tools/` (`build_db.py` head + tail; `check_dispatch.py` listed only)
- `/workspaces/firestarter_prom/firestarter_app/.github/workflows/` (both files)
- `/workspaces/firestarter_prom/firestarter/.github/workflows/` (`build.yml`)
- `/workspaces/firestarter_prom/firestarter/platformio.ini`
- `/workspaces/firestarter_prom/firestarter_app/pyproject.toml`

**Files scanned:** 18 distinct source files + 2 config files = 20 analog targets read.

**Pattern extraction date:** 2026-05-18
