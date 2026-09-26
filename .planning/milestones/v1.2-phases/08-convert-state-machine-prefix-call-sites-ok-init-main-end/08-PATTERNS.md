# Phase 8: Convert State-Machine Prefix Call-Sites (OK/INIT/MAIN/END) — Pattern Map

**Mapped:** 2026-05-18
**Files analyzed:** 16 new/modified files
**Analogs found:** 16 / 16 (all have close analogs from Phase 7 output or Phase 6 infrastructure)

---

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `tools/catalog/messages.toml` | catalog | transform | `tools/catalog/messages.toml` (Phase 7 Plan 02 additions) | exact — same file, same append pattern |
| `tools/catalog/codegen.py` | codegen | transform | `tools/catalog/codegen.py` (existing `emit_cpp_header` / `emit_python`) | role-match — extend existing emitter |
| `firestarter/include/logging_id.h` | firmware header / macro | transform | `firestarter/include/logging_id.h` lines 121–137 (Phase 7 Plan 01 output) | exact — same one-line-alias pattern |
| `firestarter/src/boards/rurp_serial_utils.cpp` | firmware emit | request-response | `firestarter/src/boards/rurp_serial_utils.cpp` lines 156–200 (`_firestarter_emit_frame`) | exact — modify the single write in this function |
| `firestarter_app/firestarter/serial_comm.py` | host decode | request-response | `firestarter_app/firestarter/serial_comm.py` lines 391–512 (`_read_and_parse_lines`) | exact — targeted edits in this function |
| `firestarter/include/firestarter.h` | firmware struct | CRUD | `firestarter/include/firestarter.h` lines 21, 79 (field to delete) | exact — struct field deletion |
| `firestarter/src/operation_utils.cpp` | firmware utility | request-response | `firestarter/src/operation_utils.cpp` lines 309–327 (`_check_response`) | exact — strip two log calls from existing switch |
| `firestarter/src/firestarter.cpp` | firmware controller | request-response | `firestarter/src/firestarter.cpp` lines 148–154 (PARSE_RESPONSE sites) | exact — convert two `send_ack_format` calls |
| `firestarter/src/hardware_operations.cpp` | firmware service | request-response | `firestarter/src/hardware_operations.cpp` lines 44, 67–69, 80–103 | exact — convert 5 site groups |
| `firestarter/src/eprom_operations.cpp` | firmware service | streaming | `firestarter/src/eprom_operations.cpp` lines 80, 121 | exact — convert 2 call-sites |
| `firestarter/src/proms/eprom.cpp` | firmware proms | CRUD | `firestarter/src/proms/eprom.cpp` lines 104, 171 (Phase 7 Plan 03 pattern) | exact — same two-line populate-site pattern |
| `firestarter/src/proms/flash_type_3.cpp` | firmware proms | CRUD | Phase 7 Plan 05/12 populate-site conversions | role-match |
| `firestarter/src/proms/flash_type_4.cpp` | firmware proms | CRUD | Phase 7 Plan 05/12 populate-site conversions | role-match |
| `firestarter/src/proms/memory.cpp` | firmware proms | streaming | `firestarter/src/proms/memory.cpp` line 325 (DATA path) | exact |
| `firestarter/test/native/avr/test_messages/test_rurp_log_id.cpp` | firmware test (Unity) | request-response | `test_rurp_log_id.cpp` lines 86–107 (existing frame assertions) | exact — update offsets in same file |
| `firestarter_app/tests/test_decoder.py` | host test (pytest) | request-response | `firestarter_app/tests/test_decoder.py` lines 58–200 (existing `TestIdFrameDecoder`) | exact — update + add to same file |
| `firestarter_app/tests/conftest.py` | host test fixture | transform | `firestarter_app/tests/conftest.py` lines 52–61 (`build_frame`) | exact — update single function |

---

## Pattern Assignments

### `tools/catalog/messages.toml` (catalog, transform)

**Analog:** `tools/catalog/messages.toml` — the Phase 7 Plan 02 additions (entries 0xB8–0xBA appended to the ERROR section) establish the append-after-last-entry-in-band pattern.

**Entry shape pattern** (lines 33–39, existing MSG_OK_READY as template):
```toml
[[messages]]
id          = 0x01
name        = "MSG_OK_READY"
severity    = "OK"
format      = "Ready"
params      = []
wire_format = "id_frame"
```

**Multi-param fixed-shape pattern** (lines 59–68, MSG_OK_REV current shape — to be reshaped in Phase 8):
```toml
[[messages]]
id          = 0x04
name        = "MSG_OK_REV"
severity    = "OK"
format      = "Rev%d%s"
params      = [
    { type = "u8" },
    { type = "ascii_str" },
]
wire_format = "id_frame"
```

**Phase 8 shape targets:** In Phase 8, `MSG_OK_REV` (0x04) becomes `{type="u8"} + {type="u8"}` (sentinel 0xFF), `MSG_OK_CFG` (0x05) becomes `{type="u32"} + {type="u32"} + {type="u8"}`, `MSG_OK_FW_HANDSHAKE` (0x06) becomes `{type="u8"} + {type="u8"} + {type="ascii_str"}` with `wire_format = "id_frame"` (drops from "text"). New DATA IDs use `{type="u16"} + {type="u16"}`.

**`[debug]` section shape pattern** (new in Phase 8 — no existing analog, see RESEARCH.md §Code Examples):
```toml
[debug]

[[debug.messages]]
id     = 0x00
name   = "DBG_FIRESTARTER_STARTED"
format = "Firestarter started"
params = []
```

**Drift gate / sync workflow** (from Phase 7 Plan 02 task action):
After every TOML edit: `python tools/catalog/codegen.py && bash tools/catalog/sync_to_subrepos.sh`. Re-run codegen and assert zero `git diff` on generated artifacts (idempotence check). Commit sub-repos with `chore(catalog):` subject.

---

### `tools/catalog/codegen.py` (codegen, transform)

**Analog:** `tools/catalog/codegen.py` — existing `emit_cpp_header` (lines 342–385) and `emit_python` (lines 388–459) establish the complete emitter pattern.

**Existing section emitter pattern** (`emit_cpp_header`, lines 371–378):
```python
parts.append("// --- Message IDs (sorted ascending) ---\n")
max_name_len = max(len(m["name"]) for m in messages)
name_col = max_name_len + 2
for m in messages:
    parts.append(
        f"#define {m['name']:<{name_col}}0x{m['id']:02X}\n"
    )
```

**Extension for `[debug]` section — new DBG_* emit block** (add after main MSG_* block in `emit_cpp_header`):
Phase 8 must add a parallel loop over `catalog.get("debug", {}).get("messages", [])` (sorted by `id` ascending), emitting `#define DBG_* 0xXX` constants using the same column-aligned pattern. Prefix `DBG_` instead of `MSG_`.

**Extension for `DEBUG_CATALOG` in `emit_python`** (add after `CATALOG` dict):
```python
parts.append("\n\n# --- Debug sub-ID catalog ---\n")
parts.append("DEBUG_CATALOG: dict[int, MessageDef] = {\n")
for dbg in sorted(debug_messages, key=lambda m: m["id"]):
    # Same MessageDef construction as CATALOG entries above.
    ...
parts.append("}\n")
```

**`NAME_PATTERN` constraint for debug names:** The existing `NAME_PATTERN = re.compile(r"^MSG_[A-Z][A-Z0-9_]*$")` applies to the main `[[messages]]` array. For `[[debug.messages]]` a parallel pattern `DBG_PATTERN = re.compile(r"^DBG_[A-Z][A-Z0-9_]*$")` is needed (or the `validate_catalog` function accepts the `[debug]` section using the same rules with a renamed prefix check).

**`VALID_SEVERITIES`** (line 46): The existing tuple includes `"DATA"`. `MSG_DEBUG` (0xF0 in the DATA band) should use `severity = "DATA"` — no new severity code needed.

---

### `firestarter/include/logging_id.h` (firmware header, transform)

**Analog:** `firestarter/include/logging_id.h` lines 121–137 — Phase 7's `LOG_ERROR_ID_*` and `LOG_WARN_ID_*` addition. This is the direct template.

**Existing one-line alias pattern** (lines 121–128):
```cpp
// --- Unconditional ERROR severity ---

#define LOG_ERROR_ID(id)               LOG_ID(id)
#define LOG_ERROR_ID_U8(id, p1)        LOG_ID_U8((id), (p1))
#define LOG_ERROR_ID_U16(id, p1)       LOG_ID_U16((id), (p1))
#define LOG_ERROR_ID_U24(id, p1)       LOG_ID_U24((id), (p1))
#define LOG_ERROR_ID_U32(id, p1)       LOG_ID_U32((id), (p1))
#define LOG_ERROR_ID_BYTES(id, b, n)   LOG_ID_BYTES((id), (b), (n))
```

**Phase 8 additions** (insert before `#endif  // __LOGGING_ID_H__` at line 139, using the same one-line alias pattern):

New unconditional families — `LOG_OK_ID_*`, `LOG_INIT_ID_*`, `LOG_MAIN_ID_*`, `LOG_END_ID_*`, `LOG_DATA_ID_*`:
```cpp
// --- Unconditional OK severity ---
#define LOG_OK_ID(id)                  LOG_ID(id)
#define LOG_OK_ID_U8(id, p1)           LOG_ID_U8((id), (p1))
// ... same surface up to LOG_OK_ID_BYTES

// --- Unconditional INIT severity ---
#define LOG_INIT_ID(id)                LOG_ID(id)
// (zero-param only needed in practice; full surface for symmetry)

// --- Unconditional MAIN severity ---
#define LOG_MAIN_ID(id)                LOG_ID(id)

// --- Unconditional END severity ---
#define LOG_END_ID(id)                 LOG_ID(id)

// --- Unconditional DATA severity ---
#define LOG_DATA_ID(id)                LOG_ID(id)
#define LOG_DATA_ID_U16_U16(id, p1, p2) \
    do { \
        uint16_t _v1 = (uint16_t)(p1); uint16_t _v2 = (uint16_t)(p2); \
        uint8_t _b[4] = { \
            (uint8_t)((_v1>>8)&0xFF),(uint8_t)(_v1&0xFF), \
            (uint8_t)((_v2>>8)&0xFF),(uint8_t)(_v2&0xFF) }; \
        rurp_log_id((id), _b, 4); \
    } while (0)
#define LOG_DATA_ID_U32_U32(id, p1, p2) \
    do { \
        uint32_t _v1 = (uint32_t)(p1); uint32_t _v2 = (uint32_t)(p2); \
        uint8_t _b[8] = { \
            (uint8_t)((_v1>>24)&0xFF),(uint8_t)((_v1>>16)&0xFF), \
            (uint8_t)((_v1>>8)&0xFF),(uint8_t)(_v1&0xFF), \
            (uint8_t)((_v2>>24)&0xFF),(uint8_t)((_v2>>16)&0xFF), \
            (uint8_t)((_v2>>8)&0xFF),(uint8_t)(_v2&0xFF) }; \
        rurp_log_id((id), _b, 8); \
    } while (0)
```

New `#ifdef SERIAL_DEBUG`-gated family — `LOG_DEBUG_ID_*`:
```cpp
// --- SERIAL_DEBUG-gated DEBUG severity ---
#ifdef SERIAL_DEBUG
#define LOG_DEBUG_ID_SUB(sub_id)           LOG_ID_U8(MSG_DEBUG, (sub_id))
#define LOG_DEBUG_ID_SUB_U8(sub_id, p1) \
    do { uint8_t _b[2] = {(uint8_t)(sub_id),(uint8_t)(p1)}; \
         rurp_log_id(MSG_DEBUG, _b, 2); } while(0)
#define LOG_DEBUG_ID_SUB_U16(sub_id, p1) \
    do { uint16_t _v=(uint16_t)(p1); \
         uint8_t _b[3]={(uint8_t)(sub_id),(uint8_t)((_v>>8)&0xFF),(uint8_t)(_v&0xFF)}; \
         rurp_log_id(MSG_DEBUG, _b, 3); } while(0)
#define LOG_DEBUG_ID_SUB_U24(sub_id, p1) \
    do { uint32_t _v=(uint32_t)(p1); \
         uint8_t _b[4]={(uint8_t)(sub_id),(uint8_t)((_v>>16)&0xFF), \
             (uint8_t)((_v>>8)&0xFF),(uint8_t)(_v&0xFF)}; \
         rurp_log_id(MSG_DEBUG, _b, 4); } while(0)
#else
#define LOG_DEBUG_ID_SUB(sub_id)
#define LOG_DEBUG_ID_SUB_U8(sub_id, p1)
#define LOG_DEBUG_ID_SUB_U16(sub_id, p1)
#define LOG_DEBUG_ID_SUB_U24(sub_id, p1)
#endif
```

**New composite pattern for `LOG_OK_ID_U8_U8_ASTR`** (needed for P-04 FW_HANDSHAKE with ascii_str last):
```cpp
// Composite: u8 + u8 + ascii_str (used by MSG_OK_FW_HANDSHAKE P-04).
// Fixed-shape params precede the variable-length ascii_str field per Phase 6 D-04.
#define LOG_OK_ID_U8_U8_ASTR(id, p1, p2, str_ptr) \
    do { \
        const char* _s = (str_ptr); \
        uint8_t _slen = (uint8_t)strlen(_s); \
        uint8_t _b[2 + 1 + 32]; \
        _b[0] = (uint8_t)(p1); \
        _b[1] = (uint8_t)(p2); \
        _b[2] = _slen; \
        memcpy(_b + 3, _s, _slen); \
        rurp_log_id((id), _b, (uint8_t)(3 + _slen)); \
    } while (0)
```

**Import required:** `#include <string.h>` for `strlen` and `memcpy` in the composite macro — verify `logging_id.h` already pulls this in transitively via `firestarter.h` / `rurp_shield.h`.

**Build verification** (from Phase 7 Plan 01):
```bash
cd firestarter && pio run -e uno --target clean && pio run -e uno && \
    pio run -e leonardo --target clean && pio run -e leonardo && \
    pio test -e native -f "*test_messages*"
```

---

### `firestarter/src/boards/rurp_serial_utils.cpp` (firmware emit, request-response)

**Analog:** `firestarter/src/boards/rurp_serial_utils.cpp` lines 156–200 — `_firestarter_emit_frame`. Phase 8 modifies exactly two lines inside this function (W-04).

**Current `len` write pattern** (lines 165–177):
```cpp
if (param_count > 253) {
    return;
}
// ...
uint8_t len = (uint8_t)(1 + param_count + 1);
SERIAL_PORT.write(len);
```

**Phase 8 replacement** (W-04 — u8 → u16 len, two write calls):
```cpp
if (param_count > 65533) {   // u16 max (65535) - 2 (id + crc)
    return;
}
// ...
uint16_t len_u16 = (uint16_t)(1 + param_count + 1);
SERIAL_PORT.write((uint8_t)(len_u16 >> 8));    // MSB
SERIAL_PORT.write((uint8_t)(len_u16 & 0xFF));  // LSB
```

**Nothing else changes** in this function — magic preamble writes, CRC accumulation, param loop, CRC write, 0x0A anchor all stay byte-identical. The `param_count` parameter type stays `uint8_t` since the catalog 24-byte PARAM_BUDGET cap means callers never pass > 24; the guard is widened to future-proof for `MSG_DATA_CHUNK` callers who may pass 512.

**Atomicity constraint:** This change MUST be committed in the same commit as the `_read_and_parse_lines` host change and the `test_rurp_log_id.cpp` test update (Group 2). A firmware-only or host-only half-commit creates a wire-format desync.

---

### `firestarter_app/firestarter/serial_comm.py` (host decode, request-response)

**Analog:** `firestarter_app/firestarter/serial_comm.py` — four targeted edit sites.

**Site 1: `EXPECTED_PREFIXES` list** (lines 123–133) — remove `"MAIN"`, `"INIT"`, `"END"` entries; keep `"OK"` and `"DATA"` until W-03 conversion:
```python
EXPECTED_PREFIXES = [
    "OK",
    "INFO",
    "DEBUG",
    "ERROR",
    "WARN",
    "DATA",
    # "MAIN", "INIT", "END" removed — W-01: these are now pure ID frames
]
```
`PREFIX_REGEX` is recompiled from this list at module load, so the regex shrinks automatically.

**Site 2: `STATE_MACHINE_PREFIXES`** (line 146) — remove or empty:
```python
STATE_MACHINE_PREFIXES = []  # Removed: MAIN/INIT/END now arrive as ID frames (W-01)
```

**Site 3: `_read_and_parse_lines` — `len` widening** (lines 451–464) — current reads 1 byte; Phase 8 reads 2 bytes:
```python
# BEFORE (line 453-464):
len_bytes = self.connection.read(1)
if not len_bytes:
    logger.warning("Magic preamble seen but length byte not received ...")
    continue
frame_len = len_bytes[0]

# AFTER (Phase 8 W-04):
import struct  # ensure struct is imported at module level
len_bytes = self.connection.read(2)   # u16 big-endian
if len(len_bytes) < 2:
    logger.warning(
        "Magic preamble seen but length bytes not received — re-syncing."
    )
    continue
frame_len = struct.unpack_from(">H", len_bytes)[0]
```

**Site 4: `_decode_id_frame` WR-03 guard** (lines 338–351) — currently rejects binary frames for `wire_format="text"` entries, which includes 0x06 (`MSG_OK_FW_HANDSHAKE`). After P-04 changes `MSG_OK_FW_HANDSHAKE` to `wire_format="id_frame"`, the guard naturally allows it — **no code change needed** in the guard itself, but `test_decoder.py::test_wire_format_text_catalog_id_rejected_as_id_frame` must be updated to only assert rejection for 0x03, not 0x06.

**`expect_ack()` — no change needed:** It already routes by `response.type == "OK"`, which `_decode_id_frame` sets from the catalog severity label. The severity-band dispatch (W-02) is already implemented via this path.

---

### `firestarter/include/firestarter.h` (firmware struct, CRUD)

**Analog:** `firestarter/include/firestarter.h` lines 21 and 79 — the two lines to delete.

**Current state to remove** (lines 21, 79):
```cpp
#define RESPONSE_MSG_SIZE 96         // line 21 — delete

char response_msg[RESPONSE_MSG_SIZE];  // line 79 — delete
```

**Ordering constraint (R-01):** This deletion commits LAST in Group 5, after ALL populate-sites in Groups 3–4 are converted. All `handle->response_msg` references must be gone from every TU before this field is deleted. Compile error on deletion = a populate-site was missed.

**Grep gate** (run before Group 5 commit):
```bash
grep -rn "response_msg" firestarter/src/ firestarter/include/
# Expected: zero hits (or only firestarter.h itself before the edit)
```

---

### `firestarter/src/operation_utils.cpp` (firmware utility, request-response)

**Analog:** `firestarter/src/operation_utils.cpp` lines 309–327 — `_check_response` switch.

**Current switch to strip** (lines 309–327):
```cpp
static inline bool _check_response(firestarter_handle_t* handle) {
    switch (handle->response_code) {
        case RESPONSE_CODE_OK:
            log_info(handle->response_msg);   // R-03: DELETE this line
            break;
        case RESPONSE_CODE_WARNING:
            break;
        case RESPONSE_CODE_DATA:
            log_data(handle->response_msg);   // R-03: DELETE this line
            rurp_communication_write(handle->data_buffer, handle->data_size);
            break;
        case RESPONSE_CODE_ERROR:
        default:
            return false;
    }
    op_reset_timeout();
    handle->response_code = RESPONSE_CODE_OK;
    return true;
}
```

**Phase 8 target shape** (R-03 — drop the two log lines, keep everything else):
```cpp
static inline bool _check_response(firestarter_handle_t* handle) {
    switch (handle->response_code) {
        case RESPONSE_CODE_OK:
            break;
        case RESPONSE_CODE_WARNING:
            break;
        case RESPONSE_CODE_DATA:
            rurp_communication_write(handle->data_buffer, handle->data_size);
            break;
        case RESPONSE_CODE_ERROR:
        default:
            return false;
    }
    op_reset_timeout();
    handle->response_code = RESPONSE_CODE_OK;
    return true;
}
```

**Also in this file (R-01 clear site):** `_execute_operation` at line 292 contains `handle->response_msg[0] = '\0';` — this disappears when the field is deleted in Group 5.

---

### `firestarter/src/firestarter.cpp` (firmware controller, request-response)

**Analog:** `firestarter/src/firestarter.cpp` lines 148–154 — P-04 `PARSE_RESPONSE` sites.

**Current pattern** (lines 148–154):
```cpp
#ifdef HARDWARE_REVISION
#define PARSE_RESPONSE "FW: " FW_VERSION ", HW: Rev%d, Cmd: 0x%02x"
    send_ack_format(PARSE_RESPONSE, rurp_get_hardware_revision(), handle->cmd);
#else
#define PARSE_RESPONSE "FW: " FW_VERSION ", Cmd: 0x%02x"
    send_ack_format(PARSE_RESPONSE, handle->cmd);
#endif
```

**Phase 8 replacement** (P-04 — composite `u8 hw + u8 cmd + ascii_str fw_version`):
```cpp
{
    uint8_t hw_rev;
#ifdef HARDWARE_REVISION
    hw_rev = (uint8_t)rurp_get_hardware_revision();
#else
    hw_rev = 0xFF;  // sentinel: no hardware revision override
#endif
    LOG_OK_ID_U8_U8_ASTR(MSG_OK_FW_HANDSHAKE, hw_rev, (uint8_t)handle->cmd, FW_VERSION);
}
```

Note: `#define PARSE_RESPONSE` can be deleted along with the `send_ack_format` call. The two-line macro definition + call both collapse to the single `LOG_OK_ID_U8_U8_ASTR` emit.

**Also in this file (R-01 clear site):** Lines 67 and 168 contain `handle->response_msg[0] = '\0';` — deleted in Group 5.

---

### `firestarter/src/hardware_operations.cpp` (firmware service, request-response)

**Analog:** Phase 7 call-site conversion pattern (D-02 two-line pattern). The hardware_operations sites use `send_ack_const`, `send_ack_format`, and `log_data_format` — all convert to `LOG_*_ID_*` + `handle->response_code = ...;`.

**Site: `send_ack_const("Ready")` (line 44):**
```cpp
// BEFORE:
send_ack_const("Ready");

// AFTER:
LOG_OK_ID(MSG_OK_READY);
// response_code = OK is the default; no state-set line needed (per R-02 note)
```

**Site: VPP/VPE voltage (lines 67–69) — splits into two new DATA IDs:**
```cpp
// BEFORE:
const char* type = (handle->cmd == CMD_READ_VPE) ? "VPE" : "VPP";
log_data_format("%s: %u.%uV, Internal VCC: %u.%uV", type,
                (voltage_mv + 50) / 1000, (((voltage_mv + 50) / 100) % 10),
                (vcc_mv + 50) / 1000, (((vcc_mv + 50) / 100) % 10));

// AFTER (voltage values passed as raw mv integers — host renders the decimal):
if (handle->cmd == CMD_READ_VPE) {
    LOG_DATA_ID_U16_U16(MSG_DATA_VPE_VOLTAGE, voltage_mv, vcc_mv);
} else {
    LOG_DATA_ID_U16_U16(MSG_DATA_VPP_VOLTAGE, voltage_mv, vcc_mv);
}
```

**Site: `fw_get_version` (line 80) — P-01:**
```cpp
// BEFORE:
send_ack_const(FW_VERSION);

// AFTER (P-01: MSG_OK_FW_VERSION stays wire_format="text"; this path uses text):
// No change in the call; FW_VERSION stays text per LFW-05. Confirm whether
// this site actually uses send_ack_const (text path) or needs an ID-frame emit.
// Per RESEARCH §Open Question 3 and CONTEXT P-01: 0x03 stays wire_format="text".
// The fw_get_version path likely stays as send_ack_const(FW_VERSION) — not converted.
```

**Site: `hw_get_version` (lines 85–91) — P-02:**
```cpp
// BEFORE:
send_ack_format("Rev%d%s", rurp_get_physical_hardware_revision(), revStr);

// AFTER (P-02: u8 physical + u8 effective, 0xFF = no override):
uint8_t effective = (rurp_config->hardware_revision < 0xFF)
    ? rurp_config->hardware_revision : 0xFF;
LOG_OK_ID_U8_U8(MSG_OK_REV,
    (uint8_t)rurp_get_physical_hardware_revision(),
    effective);
```

**Site: `hw_get_config` (lines 94–104) — P-03:**
```cpp
// BEFORE:
send_ack_format("R1: %ld, R2: %ld%s", rurp_config->r1, rurp_config->r2, revStr);

// AFTER (P-03: u32 r1 + u32 r2 + u8 override, 0xFF = no override):
uint8_t override_byte = (rurp_config->hardware_revision < 0xFF)
    ? rurp_config->hardware_revision : 0xFF;
// Use LOG_ID_BYTES for the 9-byte composite (u32+u32+u8):
uint8_t _cfg[9];
_cfg[0] = (uint8_t)(rurp_config->r1 >> 24 & 0xFF);
// ... pack r1 (4 bytes), r2 (4 bytes), override_byte (1 byte)
LOG_ID_BYTES(MSG_OK_CFG, _cfg, 9);
```

---

### `firestarter/src/eprom_operations.cpp` (firmware service, streaming)

**Analog:** Phase 7 call-site conversion pattern (D-02).

**Site: `send_ack_const("Req data")` (line 80):**
```cpp
// BEFORE:
send_ack_const("Req data");

// AFTER:
LOG_OK_ID(MSG_OK_REQ_DATA);
```

**Site: `log_data_const("Sending data")` (line 121) — this site also has `rurp_communication_write` immediately after:**
```cpp
// BEFORE:
log_data_const("Sending data");
rurp_communication_write(handle->data_buffer, handle->data_size);

// AFTER (W-04: wrap chip bytes in MSG_DATA_CHUNK ID frame via rurp_communication_write
//        with a framing header, OR emit MSG_DATA_SENDING then send raw bytes):
// Per W-03/W-04: the DATA_CHUNK wrapping is done at the emit level.
// Minimal conversion: LOG_DATA_ID(MSG_DATA_SENDING) replaces log_data_const.
// The MSG_DATA_CHUNK wrapping of the raw chip bytes is a separate emit on
// rurp_communication_write — may require a wrapper in rurp_serial_utils.cpp.
LOG_DATA_ID(MSG_DATA_SENDING);
rurp_communication_write(handle->data_buffer, handle->data_size);
// TODO: MSG_DATA_CHUNK wrapping of raw bytes is the full W-04 streaming change;
// confirm host-side eprom_operations.py receive loop before converting this site.
```

---

### `firestarter/src/proms/eprom.cpp` (firmware proms, CRUD)

**Analog:** Phase 7 Plan 03 (eprom.cpp call-site conversion) — two-line populate-site pattern (D-02).

**Site: `copy_to_buffer(handle->response_msg, "Skipping erase.")` (line 104) — R-02:**
```cpp
// BEFORE:
copy_to_buffer(handle->response_msg, "Skipping erase.");

// AFTER (two-line pattern: LOG emit + no response_code change since INFO is non-acking):
LOG_INFO_ID(MSG_INFO_SKIPPING_ERASE);   // existing ID 0x58
```

**Site: `format(handle->response_msg, "Number of retries: %d", retries)` (line 171) — R-02:**
```cpp
// BEFORE:
format(handle->response_msg, "Number of retries: %d", retries);

// AFTER:
LOG_INFO_ID_U8(MSG_INFO_RETRIES, (uint8_t)retries);  // existing ID 0x51
```

---

### `firestarter/src/proms/flash_type_3.cpp` and `flash_type_4.cpp` (firmware proms, CRUD)

**Analog:** Same two-line populate-site pattern as eprom.cpp above.

**`flash_type_3.cpp` line 88:**
```cpp
// BEFORE:
copy_to_buffer(handle->response_msg, "Skipping erase of memory");

// AFTER:
LOG_INFO_ID(MSG_INFO_SKIPPING_ERASE_MEM);  // existing ID 0x59
```

**`flash_type_4.cpp` line 52:**
```cpp
// BEFORE:
copy_to_buffer(handle->response_msg, "Skipping erase.");

// AFTER:
LOG_INFO_ID(MSG_INFO_SKIPPING_ERASE);  // existing ID 0x58
```

---

### `firestarter/src/proms/memory.cpp` (firmware proms, streaming)

**Analog:** Phase 7 D-02 pattern for DATA-path populate-sites.

**Site: `firestarter_data_response_format("%lu/%lu", handle->address, handle->mem_size)` (line 325) — R-02:**
```cpp
// BEFORE:
firestarter_data_response_format("%lu/%lu", handle->address, handle->mem_size);

// AFTER (existing ID 0xE0 MSG_DATA_PROGRESS with u32+u32 params):
LOG_DATA_ID_U32_U32(MSG_DATA_PROGRESS, handle->address, handle->mem_size);
// response_code is RESPONSE_CODE_DATA (set by caller); no state-set line needed here.
```

---

### `firestarter/test/native/avr/test_messages/test_rurp_log_id.cpp` (firmware test, request-response)

**Analog:** `test_rurp_log_id.cpp` lines 86–142 — the existing `test_zero_param_frame` and `test_u32_param_frame` assertions. Phase 8 updates all byte offsets by +1 (len field widens from 1 to 2 bytes).

**Current frame layout asserted** (u8 len at `captured[4]`, id at `captured[5]`):
```cpp
TEST_ASSERT_EQUAL_HEX8(0x02, captured[4]);    // len = u8
TEST_ASSERT_EQUAL_HEX8(0x01, captured[5]);    // id
TEST_ASSERT_EQUAL_HEX8(0x07, captured[6]);    // crc
TEST_ASSERT_EQUAL_HEX8(0x0A, captured[7]);    // anchor
```

**Phase 8 layout** (u16 len at `captured[4..5]`, id at `captured[6]`):
```cpp
// Total bytes: 4 (magic) + 2 (len u16) + 1 (id) + 0 (params) + 1 (crc) + 1 (anchor) = 9
TEST_ASSERT_EQUAL_size_t(9, captured.size());

TEST_ASSERT_EQUAL_HEX8(0x00, captured[4]);    // len MSB (= 0x00 since len <= 0xFF for these tests)
TEST_ASSERT_EQUAL_HEX8(0x02, captured[5]);    // len LSB (same numeric value as before)
TEST_ASSERT_EQUAL_HEX8(0x01, captured[6]);    // id (shifted +1)
TEST_ASSERT_EQUAL_HEX8(0x07, captured[7]);    // crc (shifted +1)
TEST_ASSERT_EQUAL_HEX8(0x0A, captured[8]);    // anchor (shifted +1)
```

**Also update:** `test_u32_param_frame` (captured[4]=0x06 → captured[4..5]=0x00/0x06, id at [6], params at [7..10], crc at [11], anchor at [12]). `test_multi_param_frame` (same +1 shift pattern). `test_oversize_param_count_rejected` (guard value changes from 253 to 65533).

**Pattern:** update `TEST_ASSERT_EQUAL_size_t` count +1 per test, and every offset `captured[N]` where N >= 4 becomes `captured[N+1]`, with `captured[4]` becoming the MSB (0x00 for all normal-sized frames) and `captured[5]` the LSB.

---

### `firestarter_app/tests/test_decoder.py` (host test, request-response)

**Analog:** `firestarter_app/tests/test_decoder.py` lines 58–200 — existing `TestIdFrameDecoder` class.

**Existing test pattern** (lines 61–75 — template for new tests):
```python
def test_zero_param_frame_decodes_as_ready(self, fake_serial, make_comm):
    """LHOST-01: zero-param MSG_OK_READY frame → Response(type='OK', message='Ready')."""
    comm = make_comm()
    frame = build_frame(MSG_OK_READY, b"")
    fake_serial.feed(frame)

    response = _drive_one_response(comm)
    assert response is not None
    assert response.type == "OK"
    assert response.message == "Ready"
```

**New tests to add (Wave 0 gaps from RESEARCH.md):**
- `test_init_done_arrives_as_id_frame` — feed `build_frame(MSG_INIT_DONE, b"")`, assert `response.type == "INIT"`
- `test_main_done_arrives_as_id_frame` — feed `build_frame(MSG_MAIN_DONE, b"")`, assert `response.type == "MAIN"`
- `test_end_done_arrives_as_id_frame` — feed `build_frame(MSG_END_DONE, b"")`, assert `response.type == "END"`
- `test_fw_handshake_p04_composite_decodes` — feed `build_frame(MSG_OK_FW_HANDSHAKE, bytes([0x01, 0x0E]) + bytes([5]) + b"2.0.0")`, assert decoded text
- `test_ok_rev_p02_shape_decodes` — feed `build_frame(MSG_OK_REV, bytes([0x01, 0xFF]))`, assert `effective=0xFF` sentinel renders correctly
- `test_ok_cfg_p03_shape_decodes` — feed `build_frame(MSG_OK_CFG, r1_bytes + r2_bytes + bytes([0xFF]))`, assert render
- Update `test_wire_format_text_catalog_id_rejected_as_id_frame` — remove the 0x06 assertion (after catalog changes `MSG_OK_FW_HANDSHAKE` to `wire_format="id_frame"`); keep 0x03 rejection only

**Import additions for new tests** (following existing pattern at lines 28–38):
```python
from firestarter.messages import (
    ...,
    MSG_INIT_DONE,
    MSG_MAIN_DONE,
    MSG_END_DONE,
    MSG_OK_FW_HANDSHAKE,
    MSG_OK_REV,
    MSG_OK_CFG,
    MSG_DATA_VPP_VOLTAGE,
    MSG_DATA_VPE_VOLTAGE,
)
```

---

### `firestarter_app/tests/conftest.py` (host test fixture, transform)

**Analog:** `firestarter_app/tests/conftest.py` lines 52–61 — `build_frame` function.

**Current `build_frame`** (line 60 — the only line changing):
```python
def build_frame(msg_id: int, params: bytes) -> bytes:
    body = bytes([msg_id]) + params
    crc = _ref_crc8_ccitt(body)
    length = len(body) + 1  # id + params + crc
    return MAGIC_PREAMBLE_REF + bytes([length]) + body + bytes([crc, 0x0A])
```

**Phase 8 replacement** (W-04 — `bytes([length])` → `struct.pack(">H", length)`):
```python
import struct  # add to module imports

def build_frame(msg_id: int, params: bytes) -> bytes:
    """Assemble a wire frame: magic | len_u16 | id | params | crc | 0x0A.

    `len` (u16, big-endian) counts (id + params + crc) per Phase 8 W-04.
    """
    body = bytes([msg_id]) + params
    crc = _ref_crc8_ccitt(body)
    length = len(body) + 1  # id + params + crc
    return MAGIC_PREAMBLE_REF + struct.pack(">H", length) + body + bytes([crc, 0x0A])
```

**Impact:** All 9+ existing callers of `build_frame` in `test_decoder.py` automatically use the new u16 len after this single-function update — no per-test changes needed for the len encoding itself. The tests will need offset-independent updates only for new shape assertions (P-02, P-03, P-04).

---

## Shared Patterns

### Two-line populate-site pattern (Phase 7 D-02 — applies to all R-02 sites)

**Source:** Phase 7 CONTEXT.md §D-02 + Phase 7 call-site execution outputs
**Apply to:** All R-02 populate-site conversions (eprom.cpp, flash_type_3.cpp, flash_type_4.cpp, memory.cpp, hardware_operations.cpp)

```cpp
// Pattern: emit the log frame, then set the response code (if needed).
// For OK-path sites where default RESPONSE_CODE_OK is already correct, the
// response_code line may be omitted. For DATA-path sites, keep the code.
LOG_INFO_ID(MSG_INFO_SKIPPING_ERASE);                    // emit ID frame
// handle->response_code = RESPONSE_CODE_OK;             // often omitted (default)

LOG_DATA_ID_U32_U32(MSG_DATA_PROGRESS, addr, mem_size); // DATA-path emit
// response_code already RESPONSE_CODE_DATA at this call-site; no change needed
```

### Catalog-first workflow (Phase 7 D-03 — applies to all Wave 1 catalog additions)

**Source:** Phase 7 Plan 02 task action + Phase 7 D-03 decision
**Apply to:** `tools/catalog/messages.toml` additions, `codegen.py` extension

```bash
# After every catalog edit:
python tools/catalog/codegen.py               # regenerate both artifacts
bash tools/catalog/sync_to_subrepos.sh        # vendor to sub-repos
python tools/catalog/codegen.py               # idempotence: must produce zero diff
# Then commit sub-repos with chore(catalog): subject
```

### Sentinel byte for optional fields (Phase 8 P-02/P-03)

**Source:** CONTEXT.md P-02, P-03 decisions
**Apply to:** `MSG_OK_REV` (effective field), `MSG_OK_CFG` (override field), `MSG_OK_FW_HANDSHAKE` (hw_rev field when no HARDWARE_REVISION define)

```cpp
// Convention: 0xFF means "no override active" / "field not applicable".
uint8_t effective = (rurp_config->hardware_revision < 0xFF)
    ? rurp_config->hardware_revision
    : 0xFF;  // no override
```

### Atomic wire-format widening constraint (W-04)

**Source:** RESEARCH.md §Anti-Patterns + CONTEXT.md W-04
**Apply to:** Group 2 commit containing: `rurp_serial_utils.cpp`, `serial_comm.py`, `conftest.py`, `test_rurp_log_id.cpp`

These four files MUST be committed atomically. Any partial commit creates a wire-format desync where the firmware emits 2-byte len but the host reads 1 byte — silent frame corruption.

### Build verification sequence (Phase 7 Plan 01 pattern)

**Source:** Phase 7 Plan 01 task action
**Apply to:** After every firmware file change

```bash
cd firestarter && pio run -e uno && pio run -e leonardo && \
    pio test -e native -f "*test_messages*"
cd firestarter_app && python -m pytest tests/test_decoder.py -v
```

---

## No Analog Found

All Phase 8 files have close analogs. However, the following specific sub-patterns are genuinely new with no prior codebase precedent:

| Pattern | File | Reason | Resolution |
|---------|------|---------|------------|
| `[debug]` TOML section + `DEBUG_CATALOG` host dict | `messages.toml`, `codegen.py` | No debug sub-ID channel exists yet | Use RESEARCH.md §Code Examples §"Catalog [debug] section shape" directly |
| `LOG_OK_ID_U8_U8_ASTR` composite macro | `logging_id.h` | No existing multi-param macro with ascii_str final | Derive from `LOG_ID_BYTES` escape-hatch pattern (line 74) |
| `MSG_DATA_CHUNK` streaming wrap (chip-read) | `eprom_operations.cpp` host-side | No existing binary-wrapped streaming frame | Pitfall 5 in RESEARCH.md — map host chip-read receive loop in `eprom_operations.py` before implementing |

---

## Metadata

**Analog search scope:** `firestarter/`, `firestarter_app/`, `tools/catalog/`
**Files scanned:** 16 primary source files + Phase 7 Plan 01/02 plans
**Key plan files read:** `07-01-PLAN.md` (macro family pattern), `07-02-PLAN.md` (catalog append + codegen workflow)
**Pattern extraction date:** 2026-05-18
