# Phase 7: Convert ERROR + WARN + INFO Call-Sites — Research

**Researched:** 2026-05-18
**Domain:** AVR C++ firmware call-site migration (legacy `log_*` macro tower → catalog-driven `rurp_log_id` binary frames)
**Confidence:** HIGH (all findings verified directly against source files at HEAD)

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **D-01** — Drop `log_*` calls in `_check_response` ERROR and WARN cases; keep response_code state machine. Each populate site emits immediately via `LOG_ERROR_ID_*(MSG_ERR_*, ...)` or `LOG_WARN_ID_*(MSG_WARN_*, ...)` AND sets `handle->response_code = RESPONSE_CODE_ERROR / RESPONSE_CODE_WARNING`. Inside `_check_response`, the WARNING and ERROR case bodies are deleted (log calls removed). `return false` in the ERROR case is KEPT. The OK and DATA branches are NOT touched in Phase 7 (Phase 8 territory). `handle->response_msg` field remains until Phase 9.

- **D-02** — Add symmetric `LOG_ERROR_ID_*` and `LOG_WARN_ID_*` families to `logging_id.h`, mirroring `LOG_INFO_ID_*` but unconditional (no `is_flag_set(FLAG_VERBOSE)` gate). Full family: `LOG_ERROR_ID`, `_U8`, `_U16`, `_U24`, `_U32`, `_BYTES` (and same for `LOG_WARN_ID_*`). These are thin aliases over `LOG_ID_*`. Multi-param purpose-built composers only for actual multi-param catalog entries — no preemptive proliferation.

- **D-03** — Locked catalog: any uncovered call-site is a Phase 6 gap, fixed via a separate `chore(catalog): ...` commit before resuming conversion. Format-string drift sub-case: call-site adapts to catalog format (catalog is canonical for the wire).

- **D-04a** — Convert `dev_tools.cpp`'s INFO call-sites. DEV_TOOLS is active (`-D DEV_TOOLS` in platformio.ini, not commented), so these compile into both firmware images.

- **D-04b** — Delete `operation_utils.cpp`'s ~14 commented-out `// log_*` breadcrumb lines in the same diff as the conversions.

### Claude's Discretion

- Commit cadence / batching strategy (planner picks; recommended: macro-additions commit first, then populate-site wave per proms/*.cpp module, then direct-log wave per file, ~12 commits total).
- Multi-param composer macros (planner picks; context leans toward raw `LOG_ID_BYTES` escape hatch for the edge cases, no new macro proliferation).
- `log_error_format_buf(handle.response_msg, "Cmd: %d, timeout", handle.cmd)` at `firestarter.cpp:171` → convert to `LOG_ERROR_ID_U8(MSG_ERR_CMD_TIMEOUT, handle.cmd)` with no buffer touch.
- `host_stubs.cpp` link-time impact (researcher confirms below — no changes needed).
- Flash-savings target wording (planner picks; "any non-zero reduction" is the stated threshold).
- `_check_response` test coverage gate (planner picks mechanism).

### Deferred Ideas (OUT OF SCOPE)

- `OK:` / `INIT:` / `MAIN:` / `END:` state-machine acks (Phase 8 / LMIG-03).
- `firestarter_data_response_format` populate sites (DATA prefix stays text per v1.2 lock).
- Deletion of old `log_*_const / log_*_format` macros and `LOG_*_MSG` PROGMEM strings (Phase 9 / LMIG-04).
- Deletion of `handle->response_msg` buffer (Phase 9 after Phase 8 clears OK/INIT/MAIN/END branches).
- Firmware major-version bump to 3.0.0 (Phase 9 / LFW-03).
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| LMIG-02 | Phase B (error + info conversion): firmware ERROR + WARN + INFO log call-sites converted to `rurp_log_id` form; each batch commits separately by call-site cluster (one PROM module at a time); old log helpers still present for OK/INIT/MAIN/END prefixes | Full call-site inventory verified (sections 1–3 below); catalog pre-flight audit confirms 3 catalog gaps that must be fixed first (section 2); multi-param approach confirmed (section 3); host stubs confirmed no-change (section 4); commit cadence proposed (section 8) |
</phase_requirements>

---

## Summary

Phase 7 is a high-volume, low-judgment call-site migration: replace every `log_error_*`, `log_warn_*`, and `log_info_*` firmware call (plus the `firestarter_error_response_format` / `firestarter_warning_response_format` populate-sites in `proms/*.cpp`) with the catalog-driven `LOG_ERROR_ID_*` / `LOG_WARN_ID_*` / `LOG_INFO_ID_*` macros introduced in Phase 6. The Phase 6 infrastructure (catalog, `messages.h`, `rurp_log_id`, host decoder) is complete and verified. Phase 7 does not touch host code.

**Primary recommendation:** Commit the `LOG_ERROR_ID_*` / `LOG_WARN_ID_*` macro additions to `logging_id.h` FIRST as an infrastructure commit, then run the catalog gap fixes (3 gaps, separate `chore(catalog):` commits, see section 2), then convert call-sites in populate-site / direct-log waves. Total: ~15 commits.

A D-03 pre-flight audit of the current firmware HEAD against the catalog found **3 catalog gaps** (missing ERROR-severity variants of dynamic-severity sites) plus **1 format-string drift** (eprom.cpp chip-ID format string differs from catalog). These are Phase 6 gaps, addressed via chore commits before conversion proceeds, per D-03 protocol.

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Frame emission (binary wire encoding) | Firmware (AVR) | — | `LOG_ERROR_ID_*` macros pack params and call `rurp_log_id` directly in firmware |
| Frame decoding | Host (Python) | — | `_decode_id_frame` already wired in Phase 6; no Phase 7 host changes |
| Catalog lookup + format render | Host (Python) | — | `CATALOG` dict in `messages.py`; firmware sends only IDs + raw bytes |
| Severity routing (host logger) | Host (Python) | — | `_log_rurp_feedback` reads `Response.type` from decoded frame; unchanged |
| Response-code state machine | Firmware (AVR) | — | `_check_response` keeps `return false` on ERROR; Phase 7 drops only the text-log side-effect lines |
| `EXTRA_INFO_LOGGING` conditional INFO sites | Firmware (AVR) | — | These compile into the binary only when `-D EXTRA_INFO_LOGGING` is added; they MUST still be converted for SC#1 grep to pass (grep does not preprocess) |

---

## 1. Definitive Call-Site Inventory

**Method:** Direct read of every file listed in CONTEXT.md canonical_refs. Lines confirmed against current HEAD. `[VERIFIED: source file read 2026-05-18]`

**Important nuance on EXTRA_INFO_LOGGING sites:** `platformio.ini` currently has `-D EXTRA_INFO_LOGGING` commented out — these sites do not compile into the production binary. However, SC#1 requires grep to return zero hits (grep does not preprocess), so they MUST be converted. They are included in the table below.

### Direct-Log Call-Sites (by file)

#### `firestarter/src/firestarter.cpp`

| Line | Current Macro | Guard | Target MSG_* | Target New Macro | Param shape | Notes |
|------|--------------|-------|-------------|-----------------|-------------|-------|
| 69 | `log_info_format("Buf val: 0x%02x", handle->data_buffer[0])` | none | `MSG_INFO_BUF_VAL` (0x44) | `LOG_INFO_ID_U8` | u8 | active |
| 70 | `log_error_const("Bad JSON")` | none | `MSG_ERR_BAD_JSON` (0xA0) | `LOG_ERROR_ID` | — | active |
| 76 | `log_info_format("Token count: %d", token_count)` | none | `MSG_INFO_TOKEN_COUNT` (0x45) | `LOG_INFO_ID_U16` | i16 (pass as u16) | active |
| 78 | `log_error_const("No cmd")` | none | `MSG_ERR_NO_CMD` (0xA1) | `LOG_ERROR_ID` | — | active |
| 86 | `log_error(handle->response_msg)` | none | — | **DELETE** | — | DEAD CODE: json_parse() (json_parser.c) never sets response_code=ERROR; response_msg is always empty at this point. Remove the entire `if (handle->response_code == RESPONSE_CODE_ERROR)` guard block and its log call. |
| 93 | `log_info_format("Force: %d", is_flag_set(FLAG_FORCE))` | `#ifdef EXTRA_INFO_LOGGING` | `MSG_INFO_FLAG_FORCE` (0x46) | `LOG_INFO_ID_U8` | u8 | guarded; convert for SC#1 grep |
| 94 | `log_info_format("Can erase: %d", is_flag_set(FLAG_CAN_ERASE))` | `#ifdef EXTRA_INFO_LOGGING` | `MSG_INFO_FLAG_CAN_ERASE` (0x47) | `LOG_INFO_ID_U8` | u8 | guarded |
| 95 | `log_info_format("Skip erase: %d", is_flag_set(FLAG_SKIP_ERASE))` | `#ifdef EXTRA_INFO_LOGGING` | `MSG_INFO_FLAG_SKIP_ERASE` (0x48) | `LOG_INFO_ID_U8` | u8 | guarded |
| 96 | `log_info_format("Skip blank check: %d", is_flag_set(FLAG_SKIP_BLANK_CHECK))` | `#ifdef EXTRA_INFO_LOGGING` | `MSG_INFO_FLAG_SKIP_BLANK` (0x49) | `LOG_INFO_ID_U8` | u8 | guarded |
| 97 | `log_info_format("VPE as VPP: %d", is_flag_set(FLAG_VPE_AS_VPP))` | `#ifdef EXTRA_INFO_LOGGING` | `MSG_INFO_FLAG_VPE_AS_VPP` (0x4A) | `LOG_INFO_ID_U8` | u8 | guarded |
| 100 | `log_error_const("Setup error")` | none | `MSG_ERR_SETUP` (0xA2) | `LOG_ERROR_ID` | — | active |
| 106 | `log_info_format("Output enable: %d", is_flag_set(FLAG_OUTPUT_ENABLE))` | `#ifdef DEV_TOOLS` + `#ifdef EXTRA_INFO_LOGGING` | `MSG_INFO_FLAG_OUTPUT_EN` (0x4B) | `LOG_INFO_ID_U8` | u8 | guarded by both |
| 107 | `log_info_format("Chip enable: %d", is_flag_set(FLAG_CHIP_ENABLE))` | `#ifdef DEV_TOOLS` + `#ifdef EXTRA_INFO_LOGGING` | `MSG_INFO_FLAG_CHIP_EN` (0x4C) | `LOG_INFO_ID_U8` | u8 | guarded by both |
| 115 | `log_error_const("Failed parsing config")` | none | `MSG_ERR_PARSE_CFG` (0xA3) | `LOG_ERROR_ID` | — | active |
| 131 | `log_info_format("Buffer size: %d", handle->data_size)` | `#ifdef EXTRA_INFO_LOGGING` | `MSG_INFO_BUFFER_SIZE` (0x4D) | `LOG_INFO_ID_U16` | u16 | guarded |
| 134 | `log_error_const("Empty input")` | none | `MSG_ERR_EMPTY_INPUT` (0xA4) | `LOG_ERROR_ID` | — | active |
| 146 | `log_info_format("Memory size 0x%lx", handle->mem_size)` | `#ifdef EXTRA_INFO_LOGGING` | `MSG_INFO_MEM_SIZE` (0x4E) | `LOG_INFO_ID_U32` | u32 | guarded |
| 147 | `log_info_format("Address mask 0x%lx", handle->bus_config.address_mask)` | `#ifdef EXTRA_INFO_LOGGING` | `MSG_INFO_ADDR_MASK` (0x4F) | `LOG_INFO_ID_U32` | u32 | guarded |
| 148 | `log_info_format("Matching lines %u", handle->bus_config.matching_lines)` | `#ifdef EXTRA_INFO_LOGGING` | `MSG_INFO_MATCH_LINES` (0x50) | `LOG_INFO_ID_U16` | u16 | guarded |
| 176 | `log_error_format_buf(handle.response_msg, "Cmd: %d, timeout", handle.cmd)` | none | `MSG_ERR_CMD_TIMEOUT` (0xAA) | `LOG_ERROR_ID_U8` | u8 | HYBRID — see section 5 |
| 243 | `log_error_P_int_buf(handle.response_msg, "Unknown cmd: ", handle.cmd)` | none | `MSG_ERR_UNKNOWN_CMD` (0xAB) | `LOG_ERROR_ID_U8` | u8 | active; note the old macro's format string "Unknown cmd: " + int differs from catalog "Unknown cmd: %d" — call-site adapts per D-03 |

**firestarter.cpp subtotal:** 21 call-sites → 1 DELETE + 20 conversions (6 active direct + 11 EXTRA_INFO_LOGGING guarded + 2 format-producing hybrids at 176/243 + 2 DEV_TOOLS+EXTRA_INFO_LOGGING).

#### `firestarter/src/operation_utils.cpp`

| Line | Current Macro | Guard | Target MSG_* | Target New Macro | Notes |
|------|--------------|-------|-------------|-----------------|-------|
| 118 | `log_error_const("Timeout")` | none | `MSG_ERR_TIMEOUT` (0xA8) | `LOG_ERROR_ID` | active direct |
| 171 | `log_error_P_int("Data err ", res)` | none | `MSG_ERR_DATA_ERR_N` (0xA9) | `LOG_ERROR_ID_U16` | active direct; `res` is `int` (signed, pass as i16 / u16) |
| 187 | `log_info_const("Main done")` | none | `MSG_INFO_MAIN_DONE` (0x41) | `LOG_INFO_ID` | active direct |
| 218 | `log_info_const("Main start")` | none | `MSG_INFO_MAIN_START` (0x40) | `LOG_INFO_ID` | active direct |
| 250 | `log_info_const("Init start")` | none | `MSG_INFO_INIT_START` (0x42) | `LOG_INFO_ID` | active direct |
| 252 | `log_info_const("End start")` | none | `MSG_INFO_END_START` (0x43) | `LOG_INFO_ID` | active direct |
| 324 | `log_info(handle->response_msg)` | `_check_response` OK branch | — | **KEEP** | Phase 8 territory (OK-path text ack) |
| 328 | `log_warn(handle->response_msg)` | `_check_response` WARN branch | — | **DELETE** | D-01: WARN case body drops log_warn call |
| 336 | `log_error(handle->response_msg)` | `_check_response` ERROR branch | — | **DELETE** | D-01: ERROR case body drops log_error call; `return false` STAYS |

Also: ~14 commented-out `// log_*` breadcrumb lines (lines 78, 80, 134, 139, 146, 178, 202, 204, 208, 211, 241, 243, 245, 325) — **DELETE per D-04b**.

**operation_utils.cpp subtotal:** 6 direct-log conversions + 2 _check_response deletions + 14 comment deletions.

#### `firestarter/src/dev_tools.cpp`

| Line | Current Macro | Target MSG_* | Target New Macro | Param shape | Notes |
|------|--------------|-------------|-----------------|-------------|-------|
| 23 | `log_info_format("%s: 0x%02X", reg_name, reg)` | `MSG_INFO_REG_HEADER` (0x52) | `LOG_INFO_ID_BYTES` | [ascii_str, u8] | reg_name is `const char*`; build stack array `{len, bytes..., reg_byte}` |
| 26 | `log_info_format("%s|D7|D6|D5|D4|D3|D2|D1|D0|", size == 9 ? "\|D8" : "")` | `MSG_INFO_BIT_HEADER` (0x53) | `LOG_INFO_ID_BYTES` | [ascii_str] | arg is `"\|D8"` (3 chars) or `""` (0 chars); build stack array `{len, bytes...}` |
| 46 | `log_info(bit_str)` | `MSG_INFO_BIT_STR` (0x54) | `LOG_INFO_ID_BYTES` | [ascii_str] | `bit_str` is a 28-byte max RAM string; build `{strlen(bit_str), bit_str[0]...}` |
| 66 | `log_info_format("CE: %d, OE: %d", is_flag_set(FLAG_CHIP_ENABLE), is_flag_set(FLAG_OUTPUT_ENABLE))` | `MSG_INFO_CE_OE` (0x55) | `LOG_INFO_ID_BYTES` | [u8, u8] | two-param; use LOG_ID_BYTES with `{(uint8_t)ce, (uint8_t)oe}` |
| 102 | `log_info_format("CE: %d, OE: %d", ...)` | `MSG_INFO_CE_OE` (0x55) | `LOG_INFO_ID_BYTES` | [u8, u8] | same as :66 in different function |
| 103 | `log_info_format("Address: 0x%06x", handle->address)` | `MSG_INFO_ADDR` (0x56) | `LOG_INFO_ID_U24` | u24 | `handle->address` is `uint32_t`; top byte dropped |
| 105 | `log_info_format("Address: 0x%06x remappend", address)` | `MSG_INFO_ADDR_REMAP` (0x57) | `LOG_INFO_ID_U24` | u24 | catalog spells "remappend" (typo preserved — catalog is authoritative) |

**dev_tools.cpp subtotal:** 7 call-sites (6 unique MSG IDs, MSG_INFO_CE_OE used twice).

#### `firestarter/src/eprom_operations.cpp`

| Line | Current Macro | Target MSG_* | Target New Macro | Notes |
|------|--------------|-------------|-----------------|-------|
| 40 | `log_error_const("Not supported")` | `MSG_ERR_NOT_SUPPORTED` (0xA5) | `LOG_ERROR_ID` | active |
| 49 | `log_error_const("No chip ID")` | `MSG_ERR_NO_CHIP_ID` (0xA6) | `LOG_ERROR_ID` | active |
| 95 | `log_error_const("Out of range")` | `MSG_ERR_OUT_OF_RANGE` (0xA7) | `LOG_ERROR_ID` | active |

**eprom_operations.cpp subtotal:** 3 direct-log conversions.

#### `firestarter/src/hardware_operations.cpp`

| Line | Current Macro | Target MSG_* | Target New Macro | Notes |
|------|--------------|-------------|-----------------|-------|
| 20 | `log_error_const("Rev0 dont support reading VPP/VPE")` | `MSG_ERR_REV0_VPP_RD` (0xAC) | `LOG_ERROR_ID` | active; guarded by `#ifdef HARDWARE_REVISION` |
| 33 | `log_error_const("Error cmd")` | `MSG_ERR_CMD` (0xAD) | `LOG_ERROR_ID` | active |

**hardware_operations.cpp subtotal:** 2 direct-log conversions.

### Populate-Site Call-Sites (proms/*.cpp)

Populate sites currently call `firestarter_error_response_format(...)` or `firestarter_warning_response_format(...)` which: (a) formats into `handle->response_msg`, and (b) sets `handle->response_code`. Phase 7 replaces them with: (a) `LOG_ERROR_ID_*(MSG_ERR_*, params)` or `LOG_WARN_ID_*(MSG_WARN_*, params)` at the call site, and (b) `handle->response_code = RESPONSE_CODE_ERROR / RESPONSE_CODE_WARNING` immediately after. Two-line form; no single combo macro.

#### `firestarter/src/proms/eprom.cpp`

| Line | Current Call | Severity | Target MSG_* | Target Pattern | Notes |
|------|------------|---------|-------------|---------------|-------|
| 182 | `firestarter_error_response_format("Failed to write memory, 0x%06x, retries: %d, bad bytes: %d", handle->address, retries, mismatch)` | ERROR | `MSG_ERR_WRITE_FAILED` (0xB1) | `LOG_ERROR_ID_BYTES(MSG_ERR_WRITE_FAILED, buf3, 5); handle->response_code = RESPONSE_CODE_ERROR;` | Params: u24(address) + u8(retries) + u16(mismatch); 5 wire bytes; use stack array or purpose-built `LOG_ERROR_ID_U24_U8_U16` (see section 3) |
| 203 | `firestarter_warning_response("Rev0 dont support reading VPP/VPE")` | WARN | `MSG_WARN_REV0_VPP_UNSUPPORTED` (0x80) | `LOG_WARN_ID(MSG_WARN_REV0_VPP_UNSUPPORTED); handle->response_code = RESPONSE_CODE_WARNING;` | zero-param |
| 223-225 | `firestarter_response_format(response_code, "VPP is high: %u.%uV > %u.%uV", ...)` | WARN/ERROR (dynamic) | `MSG_WARN_VPP_HIGH` (0x82) when FLAG_FORCE; **`MSG_ERR_VPP_HIGH` (TBD — CATALOG GAP)** when !FLAG_FORCE | Two emit branches; see section 2 | CATALOG GAP: no `MSG_ERR_VPP_HIGH` exists yet |
| 227-229 | `firestarter_warning_response_format("VPP is low: %u.%uV < %u.%uV", ...)` | WARN | `MSG_WARN_VPP_LOW` (0x81) | `LOG_WARN_ID_BYTES(MSG_WARN_VPP_LOW, buf8, 8); handle->response_code = RESPONSE_CODE_WARNING;` | 4×u16 = 8 wire bytes; see section 3 |
| 264 | `firestarter_response_format(error_code, "Chip ID: %#x dont match: %#x", chip_id, handle->chip_id)` | WARN/ERROR (dynamic) | `MSG_WARN_CHIP_ID_MISMATCH` (0x83) when FLAG_FORCE; **`MSG_ERR_CHIP_ID_MISMATCH` (TBD — CATALOG GAP)** when !FLAG_FORCE | **D-03 FORMAT DRIFT**: current code has `"Chip ID: %#x dont match: %#x"` (colon after ID, uses `%#x` not `%#04x`, missing "expected ID"); catalog has `"Chip ID %#04x dont match expected ID %#04x"` — call-site adapts. | Two catalog gaps + format drift |

#### `firestarter/src/proms/flash_intel.cpp`

| Line | Current Call | Severity | Target MSG_* | Notes |
|------|------------|---------|-------------|-------|
| 29 | `firestarter_warning_response("Rev0 dont support reading VPP/VPE")` | WARN | `MSG_WARN_REV0_VPP_UNSUPPORTED` (0x80) | same as eprom.cpp:203 |
| 41-43 | `firestarter_response_format(response_code, "VPP is high: %u.%uV > %u.%uV", ...)` | WARN/ERROR (dynamic) | `MSG_WARN_VPP_HIGH` / **`MSG_ERR_VPP_HIGH` (CATALOG GAP)** | same pattern as eprom.cpp:223 |
| 45-47 | `firestarter_warning_response_format("VPP is low: %u.%uV < %u.%uV", ...)` | WARN | `MSG_WARN_VPP_LOW` (0x81) | same as eprom.cpp:227 |
| 135 | `firestarter_error_response("Intel flash: VPP error")` | ERROR | `MSG_ERR_INTEL_VPP` (0xB4) | `LOG_ERROR_ID(MSG_ERR_INTEL_VPP); handle->response_code = RESPONSE_CODE_ERROR;` |
| 140 | `firestarter_error_response("Intel flash: program error")` | ERROR | `MSG_ERR_INTEL_PROGRAM` (0xB5) | `LOG_ERROR_ID(MSG_ERR_INTEL_PROGRAM); handle->response_code = RESPONSE_CODE_ERROR;` |
| 147 | `firestarter_error_response("Intel flash: SR timeout")` | ERROR | `MSG_ERR_INTEL_SR_TIMEOUT` (0xB6) | `LOG_ERROR_ID(MSG_ERR_INTEL_SR_TIMEOUT); handle->response_code = RESPONSE_CODE_ERROR;` |
| 159 | `firestarter_response_format(response_code, "Chip ID %#04x dont match expected ID %#04x", ...)` | WARN/ERROR (dynamic) | `MSG_WARN_CHIP_ID_MISMATCH` / **`MSG_ERR_CHIP_ID_MISMATCH` (CATALOG GAP)** | format matches catalog; two severity branches |

#### `firestarter/src/proms/flash_type_4.cpp`

| Line | Current Call | Target MSG_* | Notes |
|------|------------|-------------|-------|
| 88 | `firestarter_error_response_format("Timeout verifying 0x%02x at 0x%06lx (got 0x%02x)", expected, address, observed)` | `MSG_ERR_FL4_VERIFY_TIMEOUT` (0xB3) | Params: u8(expected) + u24(address) + u8(observed); 5 wire bytes; use stack array or purpose-built `LOG_ERROR_ID_U8_U24_U8` |

#### `firestarter/src/proms/flash_utils.cpp`

| Line | Current Call | Target MSG_* | Notes |
|------|------------|-------------|-------|
| 46 | `firestarter_error_response("Operation timed out")` | `MSG_ERR_OP_TIMEOUT` (0xB7) | zero-param; `LOG_ERROR_ID(MSG_ERR_OP_TIMEOUT); handle->response_code = RESPONSE_CODE_ERROR;` |

#### `firestarter/src/proms/eeprom_28c.cpp`

| Line | Current Call | Severity | Target MSG_* | Notes |
|------|------------|---------|-------------|-------|
| 62 | `firestarter_response_format(response_code, "mem_size %lu too small for chip-id check", (unsigned long)handle->mem_size)` | WARN/ERROR (dynamic) | `MSG_WARN_MEM_SIZE_TOO_SMALL` (0x84) when FLAG_FORCE; **`MSG_ERR_MEM_SIZE_TOO_SMALL` (CATALOG GAP)** when !FLAG_FORCE | u32 param; two severity branches |
| 75 | `firestarter_response_format(response_code, "Chip ID %#04x dont match expected ID %#04x", chip_id, handle->chip_id)` | WARN/ERROR (dynamic) | `MSG_WARN_CHIP_ID_MISMATCH` / **`MSG_ERR_CHIP_ID_MISMATCH` (CATALOG GAP)** | format matches catalog |
| 126 | `firestarter_error_response_format("EEPROM timeout at 0x%06lx: wrote 0x%02x got 0x%02x", address, expected, observed)` | ERROR | `MSG_ERR_EEPROM_TIMEOUT` (0xB2) | Params: u24(address) + u8(expected) + u8(observed); 5 wire bytes |

#### `firestarter/src/proms/memory.cpp`

| Line | Current Call | Target MSG_* | Notes |
|------|------------|-------------|-------|
| 116 | `firestarter_error_response_format("Memory type 0x%02x not supported", handle->mem_type)` | `MSG_ERR_MEM_TYPE_UNSUPPORTED` (0xAE) | u8 param |
| 219 | `firestarter_error_response_format("0x%02x != 0x%02x at 0x%06x", expected, byte, handle->address + i)` | `MSG_ERR_VERIFY` (0xAF) | Params: u8(expected) + u8(byte) + u24(address); 5 wire bytes |
| 287 | `firestarter_error_response_format("Not blank, at 0x%06x, v: 0x%02x", i, val)` | `MSG_ERR_NOT_BLANK` (0xB0) | Params: u24(i) + u8(val); 4 wire bytes; use `LOG_ERROR_ID_BYTES` or purpose-built `LOG_ERROR_ID_U24_U8` |

#### `firestarter/src/proms/flash_type_3.cpp`

| Line | Current Call | Severity | Target MSG_* | Notes |
|------|------------|---------|-------------|-------|
| 135 | `firestarter_response_format(response_code, "Chip ID %#04x dont match expected ID %#04x", chip_id, handle->chip_id)` | WARN/ERROR (dynamic) | `MSG_WARN_CHIP_ID_MISMATCH` / **`MSG_ERR_CHIP_ID_MISMATCH` (CATALOG GAP)** | format matches catalog |

**Note on `flash_type_3.cpp`:** CONTEXT.md listed `proms/flash_type_3.cpp` among the "Existing firmware logging surface" references and the Phase 6 RESEARCH inventory included it at line 169 (MSG_WARN_CHIP_ID_MISMATCH, MSG_INFO_SKIPPING_ERASE_MEM). The dynamic-severity chip-ID site at line 135 is in scope. The `MSG_INFO_SKIPPING_ERASE_MEM` site (if present) should be confirmed — the `copy_to_buffer(handle->response_msg, "Skipping erase of memory")` call would route through OK path in `_check_response` (Phase 8 territory) if it uses RESPONSE_CODE_OK. Check this during implementation.

**Also OUT OF SCOPE (OK-path populate-sites in proms):**
- `eprom.cpp:103` and `flash_type_4.cpp:51`: `copy_to_buffer(handle->response_msg, "Skipping erase.")` — sets response_msg on the OK path; `_check_response` passes it through `log_info(handle->response_msg)` which stays (Phase 8).
- `eprom.cpp:168-170`: `format(handle->response_msg, "Number of retries: %d", retries)` — same OK-path pattern.

---

## 2. D-03 Pre-Flight Audit: Catalog ↔ Call-Site Coverage

### CATALOG GAPS DISCOVERED (Phase 6 Gaps — require chore commits before conversion)

All of the following gaps arise from **dynamic-severity sites** where `firestarter_response_format(response_code, ...)` uses a runtime `response_code` that can be either `RESPONSE_CODE_ERROR` or `RESPONSE_CODE_WARNING` depending on `FLAG_FORCE`. The Phase 6 catalog only allocated the WARN variant for these messages. The ERROR variant needs new entries with ERROR severity and the same format string. `[VERIFIED: catalog read 2026-05-18]`

| Gap | Format String | WARN ID (exists) | ERROR ID (needed) | Affected Call-Sites |
|-----|--------------|-------------------|-------------------|---------------------|
| GAP-1 | `"VPP is high: %u.%uV > %u.%uV"` | `MSG_WARN_VPP_HIGH` (0x82) | `MSG_ERR_VPP_HIGH` | `eprom.cpp:223`, `flash_intel.cpp:41` |
| GAP-2 | `"Chip ID %#04x dont match expected ID %#04x"` | `MSG_WARN_CHIP_ID_MISMATCH` (0x83) | `MSG_ERR_CHIP_ID_MISMATCH` | `eprom.cpp:264`†, `eeprom_28c.cpp:71`, `flash_intel.cpp:159`, `flash_type_3.cpp:135` |
| GAP-3 | `"mem_size %lu too small for chip-id check"` | `MSG_WARN_MEM_SIZE_TOO_SMALL` (0x84) | `MSG_ERR_MEM_SIZE_TOO_SMALL` | `eeprom_28c.cpp:58` |

†`eprom.cpp:264` also has **format-string drift** (see below).

**D-03 gap protocol for each:**
1. Add new entry to `.planning/catalog/messages.toml` with next available ID in `0xA0–0xDF` range.
2. Run `sync_to_subrepos.sh` to vendor copies.
3. Run `codegen.py --language cpp` + `codegen.py --language python` in both sub-repos; verify drift gate passes.
4. Commit: `chore(catalog): add MSG_ERR_VPP_HIGH / MSG_ERR_CHIP_ID_MISMATCH / MSG_ERR_MEM_SIZE_TOO_SMALL (Phase 6 gap fix, see Phase 7)`.
5. Resume conversion.

**Suggested new IDs** (next available in ERROR range after 0xB7):
- `MSG_ERR_VPP_HIGH` = 0xB8
- `MSG_ERR_CHIP_ID_MISMATCH` = 0xB9
- `MSG_ERR_MEM_SIZE_TOO_SMALL` = 0xBA

### FORMAT-STRING DRIFT (D-03 sub-case — call-site adapts, catalog stays)

| Call-Site | Current Code Format | Catalog Format | Action |
|-----------|--------------------|--------------|----|
| `eprom.cpp:264` | `"Chip ID: %#x dont match: %#x"` | `"Chip ID %#04x dont match expected ID %#04x"` | **Call-site adapts**: change args to pass chip_id and handle->chip_id unchanged, macro targets `MSG_WARN_CHIP_ID_MISMATCH` or `MSG_ERR_CHIP_ID_MISMATCH` depending on FLAG_FORCE. The rendered string on the host will change (adds "expected ID", uses 4-digit hex). This is an intentional normalization per D-03. |

### CONFIRMED CLEAN (all other call-sites match catalog)

All other active format strings in the call-site inventory exactly match their catalog entries. `[VERIFIED: cross-referenced against messages.toml 2026-05-18]`

---

## 3. Multi-Param Composer Recommendation

Three multi-param patterns need handling. The existing `LOG_ID_BYTES` escape hatch is the recommended approach — keeps `logging_id.h` small and all edge cases go through one well-tested code path.

**Approach: raw `LOG_ID_BYTES` escape hatch with per-call stack arrays.** The CONTEXT.md "Specifics" note leans this way. The call-site readability is acceptable because the `LOG_ERROR_ID_BYTES(id, arr, n)` pattern expands to a single `rurp_log_id` call and the comment above each call explains the param layout.

**Pattern template for multi-param sites:**
```c
// Packs: u24(addr) + u8(retries) + u16(bad_bytes) → MSG_ERR_WRITE_FAILED (0xB1)
uint32_t _addr = handle->address;
uint8_t _b[5] = {
    (uint8_t)((_addr >> 16) & 0xFF),  // u24 MSB
    (uint8_t)((_addr >> 8)  & 0xFF),
    (uint8_t)(_addr         & 0xFF),  // u24 LSB
    (uint8_t)(retries),               // u8
    (uint8_t)((mismatch >> 8) & 0xFF),// u16 MSB
    // wait — that's 6 bytes, u16 is 2 bytes
};
// Corrected: u24(3) + u8(1) + u16(2) = 6 bytes
uint8_t _b[6] = {
    (uint8_t)((_addr >> 16) & 0xFF),
    (uint8_t)((_addr >> 8)  & 0xFF),
    (uint8_t)(_addr         & 0xFF),
    (uint8_t)(retries),
    (uint8_t)((uint16_t)(mismatch) >> 8) & 0xFF),
    (uint8_t)((uint16_t)(mismatch) & 0xFF),
};
LOG_ERROR_ID_BYTES(MSG_ERR_WRITE_FAILED, _b, 6);
handle->response_code = RESPONSE_CODE_ERROR;
```

**Multi-param sites summary:**

| Format Pattern | Wire bytes | Catalog entry | Stack array approach |
|---------------|------------|--------------|---------------------|
| u24 + u8 + u16 | 6 | `MSG_ERR_WRITE_FAILED` (0xB1) | 6-byte stack array |
| u24 + u8 + u8 | 5 | `MSG_ERR_EEPROM_TIMEOUT` (0xB2), `MSG_ERR_NOT_BLANK` (0xB0) | 5-byte stack array |
| u8 + u24 + u8 | 5 | `MSG_ERR_FL4_VERIFY_TIMEOUT` (0xB3) | 5-byte stack array |
| u8 + u8 + u24 | 5 | `MSG_ERR_VERIFY` (0xAF) | 5-byte stack array |
| u16×4 | 8 | `MSG_WARN_VPP_LOW` (0x81), `MSG_WARN_VPP_HIGH` (0x82) | 8-byte stack array |
| ascii_str + u8 | var | `MSG_INFO_REG_HEADER` (0x52) | `{len, s[0]..., val}` stack array |
| ascii_str | var | `MSG_INFO_BIT_HEADER` (0x53), `MSG_INFO_BIT_STR` (0x54) | `{len, s[0]...}` stack array |
| u8 + u8 | 2 | `MSG_INFO_CE_OE` (0x55) | 2-byte stack array |
| u24 | 3 | `MSG_INFO_ADDR` (0x56), `MSG_INFO_ADDR_REMAP` (0x57) | use `LOG_INFO_ID_U24` (already exists) |

**Stack pressure assessment:** All stack arrays are ≤8 bytes for fixed-type params. The ascii_str arrays (MSG_INFO_BIT_STR) are the largest — bit_str in dev_tools.cpp is at most ~28 bytes (`| 0|` × 9 bits + trailing `\0`) → 29 bytes for the array with length prefix. This is safe on both Uno (2KB RAM) and Leonardo (2.5KB RAM). These calls occur in dev-tool interactive paths (not in write tight loops) so stack depth is shallow. `[ASSUMED: no profiling of native stack depth; but the call chain depth at dt_decode_register is shallow]`

**RAM concern for u16×4 in VPP check (in write init hot path):** The VPP check in `flash_intel_write_init` / `eprom_write_init` runs once per write command, not per-byte. 8-byte stack array is negligible.

---

## 4. host_stubs.cpp Link-Time Impact

**Finding: No changes needed to host_stubs.cpp or host_stubs_common.inc.** `[VERIFIED: source file read 2026-05-18]`

After Phase 7, the native test binary links `src/proms/*.cpp` which will call `LOG_ERROR_ID_*` / `LOG_WARN_ID_*` macros. These macros expand to `LOG_ID_*(...)` which expands to `rurp_log_id(...)`. The `rurp_log_id` symbol is provided by `rurp_serial_utils.cpp`, which is already in the `[env:native]` `src_filter` (added in Phase 6 for `test_messages`). The linker resolves it. No new stub needed.

**Stubs to remove:** None. The `LOG_OK_MSG`, `LOG_ERROR_MSG`, `LOG_WARN_MSG`, `LOG_INFO_MSG`, etc. PROGMEM string definitions in `host_stubs_common.inc` (lines 46-54) still resolve references from `logging.h` which stays intact until Phase 9. The `_check_response` OK and DATA branches still call `log_info(handle->response_msg)` and `log_data(...)` which use those strings. **Do not remove them in Phase 7.**

**Stubs to add:** None. `rurp_log_id` is the only new symbol called by converted sites, and it is already provided.

**Concrete test that confirms this:** `pio test -e native -f "*test_dispatch*"` must pass after each commit. The dispatch tests exercise `configure_memory` → `configure_eprom` / `configure_flash_intel` / etc., which in Phase 7 will call `LOG_ERROR_ID_*` / `LOG_WARN_ID_*` at populate sites. Since `rurp_log_id` no-ops on native (the weak implementation in `rurp_serial_utils.cpp` calls `_firestarter_emit_frame` which calls `SERIAL_PORT.write` — the ArduinoFake implementation discards it), the dispatch tests continue to verify response_code routing without needing any stub additions.

---

## 5. The `firestarter.cpp:171` Hybrid

**Finding: Convert directly to `LOG_ERROR_ID_U8`, no buffer touch, no response_code mutation needed.** `[VERIFIED: source context read 2026-05-18]`

The hybrid site at line 176:
```c
// Current (firestarter.cpp:171)
log_error_format_buf(handle.response_msg, "Cmd: %d, timeout", handle.cmd);
command_done(&handle);
```

Context: this is in `loop()`, inside:
```c
if (handle.cmd != CMD_IDLE && timeout < millis()) {
    log_error_format_buf(handle.response_msg, "Cmd: %d, timeout", handle.cmd);
    command_done(&handle);
```

`command_done()` resets `handle.cmd` to `CMD_IDLE` and nulls `handle.response_msg[0]`. It does NOT read `handle.response_msg` or `handle.response_code`. `handle.response_code` is not consulted by anything downstream of this path either — the command is being forcibly terminated by timeout, not by the state machine. Therefore:

**Conversion:**
```c
// Phase 7 (firestarter.cpp:171)
LOG_ERROR_ID_U8(MSG_ERR_CMD_TIMEOUT, handle.cmd);
command_done(&handle);
```

No `handle.response_code` mutation. No `handle.response_msg` write. The emit happens before `command_done()` nulls the buffer, so timing is fine. `handle.cmd` is `uint8_t`-compatible (it's an enum that fits in a byte).

---

## 6. `_check_response` Surgical Edit (operation_utils.cpp:329-350)

**Exact unified-diff sketch:**

```diff
--- a/firestarter/src/operation_utils.cpp
+++ b/firestarter/src/operation_utils.cpp
@@ -321,14 +321,10 @@
 static inline bool _check_response(firestarter_handle_t* handle) {
     switch (handle->response_code) {
         case RESPONSE_CODE_OK:
             log_info(handle->response_msg);
-            // log_info_const("- OK -");
             break;
         case RESPONSE_CODE_WARNING:
-            log_warn(handle->response_msg);
             break;
         case RESPONSE_CODE_DATA:
             log_data(handle->response_msg);
             rurp_communication_write(handle->data_buffer, handle->data_size);
             break;
         case RESPONSE_CODE_ERROR:
         default:
-            log_error(handle->response_msg);
             return false;
     }
```

Note: the `// log_info_const("- OK -")` commented line at the current line 325 is one of the 14 breadcrumbs deleted by D-04b. It appears between the `log_info` call and `break`, so it's removed in the same diff.

**Post-edit behavior:**
- `RESPONSE_CODE_OK` → `log_info(handle->response_msg)` (stays — Phase 8 territory). The OK-path populate sites (`"Skipping erase."`, `"Number of retries: %d"`) still write response_msg; `_check_response` still emits it as text. Unchanged.
- `RESPONSE_CODE_WARNING` → no log call. Emit already happened at the populate site via `LOG_WARN_ID_*`. `break` stays.
- `RESPONSE_CODE_DATA` → `log_data` + binary write stay. Phase 8 territory.
- `RESPONSE_CODE_ERROR` → no log call. `return false` stays (drives operation-flow abort). Emit already happened at the populate site via `LOG_ERROR_ID_*`.

**Verification of `return false` staying:** The operation-flow abort depends entirely on `_check_response` returning `false`. That `return false` in the ERROR case is the state machine's abort mechanism. It is KEPT per D-01. The Phase 7 change is: the error has already been announced to the host via the binary frame at the populate site; `_check_response` no longer needs to re-announce it via text.

**`handle->response_msg` field:** Not removed in Phase 7. The OK/DATA branches still use it. The field stays on `firestarter_handle_t` until Phase 9.

---

## 7. Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework (firmware) | Unity via PlatformIO `[env:native]` |
| Framework (host) | pytest 7+ |
| Config file (firmware) | `firestarter/platformio.ini` |
| Config file (host) | `firestarter_app/pyproject.toml` |
| Quick run (firmware native) | `cd firestarter && pio test -e native` |
| Quick run (host) | `cd firestarter_app && python -m pytest tests/ -q` |
| Full build check | `cd firestarter && pio run -e uno && pio run -e leonardo` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | Notes |
|--------|----------|-----------|-------------------|-------|
| LMIG-02 SC#1 | grep for legacy log macros returns zero | Grep check | `grep -rn "log_info_const\|log_info_format\|log_warn\|log_error_const\|log_error_format\|log_error_P_\|firestarter_error_response\|firestarter_warning_response" firestarter/src/ \| grep -v "// " \| grep -v "^.*#define" \| wc -l` must return 0 | Run at phase close |
| LMIG-02 SC#2 | ERROR/WARN/INFO lines rendered by catalog decoder | E2E manual | Run `firestarter write -e W27C512` against real hardware OR simulator; verify INFO/WARN/ERROR lines appear; toggle decoder off and confirm those lines disappear | Manual bench verification |
| LMIG-02 SC#3 | State-machine acks still text-format | Host pytest regression | `cd firestarter_app && python -m pytest tests/test_decoder.py -k "text" -v` | Existing tests cover text-coexistence path |
| LMIG-02 SC#4 | Both boards compile; binary size drops | Build check | `cd firestarter && pio run -e uno && pio run -e leonardo` then record flash usage in `07-FLASH-MEASUREMENT.md` | After each commit wave |
| LMIG-02 build gate | Native test suite passes | Unity | `cd firestarter && pio test -e native` | After EVERY commit |
| LMIG-02 dispatch regression | configure_memory routes correctly | Unity | `cd firestarter && pio test -e native -f "*test_dispatch*"` | After every proms/*.cpp commit |
| LMIG-02 wire-frame regression | Phase 6 frame emit path unchanged | Unity | `cd firestarter && pio test -e native -f "*test_messages*"` | After logging_id.h commit |
| LMIG-02 host decode regression | Decoder handles ERROR/WARN/INFO frames | pytest | `cd firestarter_app && python -m pytest tests/test_decoder.py -v` | After every commit wave |
| LMIG-02 _check_response flow | WARNING case doesn't abort, ERROR case does | Unity | `pio test -e native -f "*test_dispatch*"` (existing dispatch tests exercise the response_code flow via configure_memory returning ERROR response_code when chip-ID fails) | Existing tests exercise code path |

### Sampling Rate

- **Per commit (every single commit in phase):** `cd firestarter && pio test -e native`
- **Per wave (populate-site wave + direct-log wave):** `cd firestarter && pio run -e uno && pio run -e leonardo && pio test -e native`
- **Phase gate:** Full suite green before `/gsd-verify-work`:
  - `cd firestarter && pio run -e uno && pio run -e leonardo && pio test -e native`
  - `cd firestarter_app && python -m pytest tests/ -v`
  - SC#1 grep returns 0
  - SC#4 flash-measurement artifact written

### Wave 0 Gaps

No new test files needed. All required test infrastructure exists from Phase 6:
- `firestarter/test/native/avr/test_messages/test_rurp_log_id.cpp` — covers `rurp_log_id` frame emit
- `firestarter/test/native/avr/test_dispatch/test_configure_memory.cpp` — covers dispatch routing and response_code flow
- `firestarter_app/tests/test_decoder.py` — 12 tests covering binary frame decode, text coexistence, error paths

**Optional extension (Claude's Discretion):** Add 2-3 new tests to `test_decoder.py` covering multi-param MSG IDs that Phase 7 actually emits (e.g., `MSG_ERR_WRITE_FAILED` with a u24+u8+u16 payload, `MSG_WARN_VPP_LOW` with 4×u16). This improves SC#2 coverage in the automated suite. Not required for phase gate, but useful for the verifier.

---

## 8. Commit Cadence Recommendation

**Recommended: 15 commits total** (was ~12 in CONTEXT; gaps add 3 catalog commits).

### Commit Order

| # | Scope | Description | Files |
|---|-------|-------------|-------|
| C-01 | Infrastructure | `feat(logging_id.h): add LOG_ERROR_ID_* and LOG_WARN_ID_* families` | `firestarter/include/logging_id.h` |
| C-02 | Catalog gap 1 | `chore(catalog): add MSG_ERR_VPP_HIGH 0xB8 (Phase 6 gap, see Phase 7)` | `messages.toml`, generated `messages.h`, `messages.c`, `messages.py` |
| C-03 | Catalog gap 2 | `chore(catalog): add MSG_ERR_CHIP_ID_MISMATCH 0xB9 (Phase 6 gap, see Phase 7)` | same |
| C-04 | Catalog gap 3 | `chore(catalog): add MSG_ERR_MEM_SIZE_TOO_SMALL 0xBA (Phase 6 gap, see Phase 7)` | same |
| C-05 | Populate wave | `feat(eprom.cpp): convert populate-sites to LOG_ERROR_ID_*/LOG_WARN_ID_*` | `firestarter/src/proms/eprom.cpp` |
| C-06 | Populate wave | `feat(flash_intel.cpp): convert populate-sites to LOG_ERROR_ID_*/LOG_WARN_ID_*` | `firestarter/src/proms/flash_intel.cpp` |
| C-07 | Populate wave | `feat(flash_type_4.cpp): convert populate-site to LOG_ERROR_ID_BYTES` | `firestarter/src/proms/flash_type_4.cpp` |
| C-08 | Populate wave | `feat(flash_utils.cpp): convert populate-site to LOG_ERROR_ID` | `firestarter/src/proms/flash_utils.cpp` |
| C-09 | Populate wave | `feat(eeprom_28c.cpp): convert populate-sites to LOG_ERROR_ID_*/LOG_WARN_ID_*` | `firestarter/src/proms/eeprom_28c.cpp` |
| C-10 | Populate wave | `feat(memory.cpp): convert populate-sites to LOG_ERROR_ID_BYTES` | `firestarter/src/proms/memory.cpp` |
| C-11 | Populate wave | `feat(flash_type_3.cpp): convert populate-site to LOG_WARN_ID_*/LOG_ERROR_ID_*` | `firestarter/src/proms/flash_type_3.cpp` |
| C-12 | Direct-log wave | `feat(firestarter.cpp): convert direct log_* calls to LOG_{SEV}_ID_*` | `firestarter/src/firestarter.cpp` |
| C-13 | Direct-log wave | `feat(operation_utils.cpp): convert direct log_* calls, drop _check_response emit, delete breadcrumbs` | `firestarter/src/operation_utils.cpp` |
| C-14 | Direct-log wave | `feat(dev_tools.cpp): convert INFO call-sites to LOG_INFO_ID_BYTES/*` | `firestarter/src/dev_tools.cpp` |
| C-15 | Direct-log wave | `feat(eprom_operations.cpp, hardware_operations.cpp): convert log_error_const sites` | both files (trivial — 5 total one-liners, collapse into one commit) |

**Collapses justified:** C-15 collapses `eprom_operations.cpp` (3 sites) and `hardware_operations.cpp` (2 sites) into one commit — each conversion is a single-line `log_error_const` → `LOG_ERROR_ID(MSG_*)` replacement with no complexity. Similarly, the three catalog gap commits (C-02..C-04) could be batched into one if the planner prefers, though separate commits improve bisectability.

**Split justified:** firestarter.cpp (C-12) at 21 call-sites is the largest single-file batch. The CONTEXT suggested possibly splitting INFO vs ERROR sub-batches; given that many of the INFO sites are `#ifdef EXTRA_INFO_LOGGING`-guarded (not in production binary but must be converted for SC#1 grep), the planner may choose to split: C-12a (active direct-log sites: lines 70, 78, 100, 115, 134, 176, 243, and the DELETE at 86) and C-12b (EXTRA_INFO_LOGGING-guarded sites: lines 69, 76, 93-97, 106-107, 131, 146-148). This keeps each commit reviewable.

---

## 9. Build + Size Measurement Protocol

**Mirror of `06-FLASH-MEASUREMENT.md` shape.**

```bash
# Working directory: firestarter/
# Run AFTER each commit wave (or at minimum at phase close)

# Uno build + size
pio run -e uno 2>&1 | tee /tmp/ph7-uno-build.txt
grep "Flash:" /tmp/ph7-uno-build.txt

# Leonardo build + size
pio run -e leonardo 2>&1 | tee /tmp/ph7-leo-build.txt
grep "Flash:" /tmp/ph7-leo-build.txt

# Native tests
pio test -e native 2>&1 | tee /tmp/ph7-native-tests.txt
```

**Cache invalidation:** After editing `logging_id.h`, PlatformIO's build cache may not recompile all consumers. Force clean rebuild with:
```bash
pio run -e uno --target clean && pio run -e uno
pio run -e leonardo --target clean && pio run -e leonardo
```
Or use the `-f` / `--force` flag. This is particularly important after C-01 (the `logging_id.h` macro additions commit) and after C-02..C-04 (catalog changes regenerate `messages.h` / `messages.c`).

**Artifact:** Write `07-FLASH-MEASUREMENT.md` at phase close. Required fields:
- Repo state (git SHA) at measurement
- Leonardo Flash: X% (Y/28672 bytes), Z bytes free; delta vs Phase 6 close (28,292 bytes used)
- Uno Flash: X% (Y/32256 bytes), Z bytes free; delta vs Phase 6 close (26,100 bytes used)
- Interpretation (direction must be downward per SC#4)

**Expected direction:** Phase 7 activates the `rurp_log_id` call chain (CRC8 table, frame emitter — currently dead weight per Phase 6 analysis) while eliminating the per-call PROGMEM string literals from `log_error_const`/`log_warn_const`/`log_info_const`. Net flash impact:
- Cost: `_firestarter_emit_frame` (~100 bytes) + CRC8_TABLE (256 bytes) pulled in from dead weight to live code
- Benefit: Per-call PROGMEM strings removed (each `log_error_const("Bad JSON")` = ~9 bytes PROGMEM for the string + 4-6 bytes for the `rurp_log_P` call; ~55 unique format strings × average ~15 bytes = ~825 bytes released)
- Net expected: ~450-650 bytes flash reduction on Leonardo. Trend must be downward (SC#4).

---

## 10. Risks and Pitfalls

### Pitfall 1: Dynamic-Severity Site Conversion Error
**What goes wrong:** Developer converts `firestarter_response_format(response_code, msg, ...)` to always emit `LOG_WARN_ID_*(MSG_WARN_*, ...)` without the `if/else` branch, losing the ERROR emission when `FLAG_FORCE=0`.
**Why it happens:** The old macro used a runtime `response_code`; the new macro has severity baked into the name.
**How to avoid:** Every `firestarter_response_format(response_code, ...)` site must become a branch:
```c
if (is_flag_set(FLAG_FORCE)) {
    LOG_WARN_ID_*(MSG_WARN_*, params);
    handle->response_code = RESPONSE_CODE_WARNING;
} else {
    LOG_ERROR_ID_*(MSG_ERR_*, params);
    handle->response_code = RESPONSE_CODE_ERROR;
}
```
**Warning signs:** Chip-ID mismatch no longer aborts the write when `FLAG_FORCE=0`.

### Pitfall 2: D-03 Triggered Mid-Batch (Catalog Gap Found During Conversion)
**What goes wrong:** A convert attempt discovers a format string not in the catalog, stalls.
**Why it happens:** Phase 6 Research may have missed some call-sites.
**How to avoid:** The pre-flight audit above (section 2) identified all known gaps. The three chore commits (C-02..C-04) resolve them before conversion begins. If an additional gap surfaces during conversion, follow D-03 protocol: stop batch, add catalog entry, regen, commit `chore(catalog):`, resume.
**Warning signs:** No matching `MSG_*` symbol for a format string being converted.

### Pitfall 3: `log_error(handle->response_msg)` Ghost Sites
**What goes wrong:** The `firestarter.cpp:86` `log_error(handle->response_msg)` is deleted but the developer misses that the surrounding `if (handle->response_code == RESPONSE_CODE_ERROR)` guard is also dead code and leaves it, resulting in a stale `if` block with no body.
**How to avoid:** Delete both the `if` condition check AND the `log_error` call AND the `return false` inside that block (the false return is from this dead-code path, not from the state machine — the actual parse error returns are at lines 72-79 and line 102).
**Clarification:** `firestarter.cpp:84-88` reads:
```c
json_parse(...);
if (handle->response_code == RESPONSE_CODE_ERROR) {
    log_error(handle->response_msg);  // DELETE THIS LINE
    return false;                     // DELETE THIS LINE (dead path)
}
```
The entire `if` block is dead code. Delete it. The `return false` lines at 72, 79, 102, 116 are NOT dead code and stay.

### Pitfall 4: PlatformIO Build Cache Stale After `logging_id.h` Edit
**What goes wrong:** After adding the `LOG_ERROR_ID_*` macros to `logging_id.h`, subsequent `pio run` uses cached object files that don't include the new macro definitions.
**Why it happens:** PlatformIO's dependency tracking sometimes misses header-only changes when the header modification timestamp is close to a previous build.
**How to avoid:** After C-01 (logging_id.h commit), run `pio run -e uno --target clean && pio run -e uno` to force a full rebuild. Same after C-02..C-04 (catalog regen changes `messages.h` and `messages.c`).

### Pitfall 5: Stack Array Init in C++ `do { } while(0)` Macro Context
**What goes wrong:** A VLA (variable-length array) or compound literal used inside a `do { } while (0)` macro body on avr-g++ emits a warning or error.
**Why it happens:** The `LOG_ID_BYTES` macro uses a direct call to `rurp_log_id`, not wrapped in `do {...}`. The stack arrays are created at the call-site (not inside the macro), so this is not an issue. The call-site builds the array and passes it to `LOG_ERROR_ID_BYTES`.
**How to avoid:** Always build the stack array as a named local variable (`uint8_t _b[N] = {...};`) before the `LOG_*_ID_BYTES` call, not as an inline compound literal in the macro argument.

### Pitfall 6: `eprom.cpp` Retries Format-String in Wrong Direction
**What goes wrong:** `eprom.cpp:170` (`format(handle->response_msg, "Number of retries: %d", retries)`) looks like a candidate for conversion but is an OK-path populate site (response_code stays OK). Developer converts it and breaks the retries feedback display.
**Why it happens:** The surrounding code does not set `response_code = RESPONSE_CODE_ERROR`. The `_check_response` OK branch calls `log_info(handle->response_msg)` which emits it as text (Phase 8 territory).
**How to avoid:** This site is explicitly OUT OF SCOPE. Leave it unchanged. The `Skipping erase.` sites in `eprom.cpp:103` and `flash_type_4.cpp:51` are similarly OK-path.

### Pitfall 7: Uno RAM Budget for `LOG_ID_BYTES` Stack Arrays
**What goes wrong:** A developer adds `LOG_ID_BYTES` calls inside a tight inner loop (e.g., inside `eprom_write_execute`'s retry loop), allocating stack arrays on every iteration.
**Why it happens:** `LOG_ERROR_ID_BYTES` is called with an error param inside the write loop.
**Risk assessment:** LOW. The ERROR/WARN sites that use multi-param arrays are in error-path or init-path code, not in the byte-per-byte write inner loop. The write inner loop (`eprom_write_execute`) uses `firestarter_error_response_format` only at the end (when retry limit is exhausted), not per-iteration. `[VERIFIED: source read 2026-05-18]` Uno RAM: 77.5% used (1587/2048 bytes) at Phase 6 close — 461 bytes free. A 6-byte stack array in an error path is well within budget.

---

## Standard Stack

### Core (Phase 6 Infrastructure — No Changes Needed)

| Library | Version | Purpose |
|---------|---------|---------|
| `firestarter/include/logging_id.h` | Phase 6 | `LOG_ID_*` + `LOG_INFO_ID_*` macros — Phase 7 adds ERROR/WARN families here |
| `firestarter/include/messages.h` | Phase 6 codegen | `MSG_*` ID defines — Phase 7 call-sites use these constants |
| `firestarter/src/boards/rurp_serial_utils.cpp` | Phase 6 | `rurp_log_id` weak + `_firestarter_emit_frame` — no Phase 7 changes |
| `firestarter/include/logging.h` | Legacy | Legacy macro tower — stays intact through Phase 7; deletion in Phase 9 |

### New in Phase 7

| Addition | File | Purpose |
|----------|------|---------|
| `LOG_ERROR_ID` + `_U8` + `_U16` + `_U24` + `_U32` + `_BYTES` | `logging_id.h` | Unconditional ERROR frame emit macros |
| `LOG_WARN_ID` + `_U8` + `_U16` + `_U24` + `_U32` + `_BYTES` | `logging_id.h` | Unconditional WARN frame emit macros |
| `MSG_ERR_VPP_HIGH` (0xB8) | `messages.toml` → `messages.h` | Catalog gap fix |
| `MSG_ERR_CHIP_ID_MISMATCH` (0xB9) | `messages.toml` → `messages.h` | Catalog gap fix |
| `MSG_ERR_MEM_SIZE_TOO_SMALL` (0xBA) | `messages.toml` → `messages.h` | Catalog gap fix |

---

## Code Examples

### `LOG_ERROR_ID_*` and `LOG_WARN_ID_*` macro additions (logging_id.h)

```c
// Source: mirror of existing LOG_INFO_ID_* pattern in logging_id.h, unconditional
// (no is_flag_set(FLAG_VERBOSE) gate — ERROR + WARN always emit)

#define LOG_ERROR_ID(id)               LOG_ID(id)
#define LOG_ERROR_ID_U8(id, p)         LOG_ID_U8((id), (p))
#define LOG_ERROR_ID_U16(id, p)        LOG_ID_U16((id), (p))
#define LOG_ERROR_ID_U24(id, p)        LOG_ID_U24((id), (p))
#define LOG_ERROR_ID_U32(id, p)        LOG_ID_U32((id), (p))
#define LOG_ERROR_ID_BYTES(id, b, n)   LOG_ID_BYTES((id), (b), (n))

#define LOG_WARN_ID(id)                LOG_ID(id)
#define LOG_WARN_ID_U8(id, p)          LOG_ID_U8((id), (p))
#define LOG_WARN_ID_U16(id, p)         LOG_ID_U16((id), (p))
#define LOG_WARN_ID_U24(id, p)         LOG_ID_U24((id), (p))
#define LOG_WARN_ID_U32(id, p)         LOG_ID_U32((id), (p))
#define LOG_WARN_ID_BYTES(id, b, n)    LOG_ID_BYTES((id), (b), (n))
```

### Simple zero-param ERROR populate-site conversion (flash_intel.cpp)

```c
// BEFORE
firestarter_error_response("Intel flash: VPP error");

// AFTER
LOG_ERROR_ID(MSG_ERR_INTEL_VPP);
handle->response_code = RESPONSE_CODE_ERROR;
```

### Dynamic-severity site conversion (eprom.cpp VPP high)

```c
// BEFORE
int response_code = is_flag_set(FLAG_FORCE) ? RESPONSE_CODE_WARNING : RESPONSE_CODE_ERROR;
firestarter_response_format(response_code, "VPP is high: %u.%uV > %u.%uV",
    (vpp_mv + 50) / 1000, (((vpp_mv + 50) / 100) % 10),
    (handle->vpp_mv + 50) / 1000, (((handle->vpp_mv + 50) / 100) % 10));

// AFTER (requires MSG_ERR_VPP_HIGH catalog gap fix first)
uint16_t _v0 = (uint16_t)((vpp_mv + 50) / 1000);
uint16_t _v1 = (uint16_t)(((vpp_mv + 50) / 100) % 10);
uint16_t _v2 = (uint16_t)((handle->vpp_mv + 50) / 1000);
uint16_t _v3 = (uint16_t)(((handle->vpp_mv + 50) / 100) % 10);
uint8_t _b[8] = {
    (uint8_t)(_v0 >> 8), (uint8_t)(_v0 & 0xFF),
    (uint8_t)(_v1 >> 8), (uint8_t)(_v1 & 0xFF),
    (uint8_t)(_v2 >> 8), (uint8_t)(_v2 & 0xFF),
    (uint8_t)(_v3 >> 8), (uint8_t)(_v3 & 0xFF),
};
if (is_flag_set(FLAG_FORCE)) {
    LOG_WARN_ID_BYTES(MSG_WARN_VPP_HIGH, _b, 8);
    handle->response_code = RESPONSE_CODE_WARNING;
} else {
    LOG_ERROR_ID_BYTES(MSG_ERR_VPP_HIGH, _b, 8);
    handle->response_code = RESPONSE_CODE_ERROR;
}
```

### Multi-param ERROR convert (eprom.cpp write failed)

```c
// BEFORE
firestarter_error_response_format("Failed to write memory, 0x%06x, retries: %d, bad bytes: %d",
    handle->address, retries, mismatch);

// AFTER — MSG_ERR_WRITE_FAILED params: u24(addr) + u8(retries) + u16(bad_bytes)
{
    uint32_t _addr = handle->address;
    uint16_t _bad  = (uint16_t)mismatch;
    uint8_t _b[6] = {
        (uint8_t)((_addr >> 16) & 0xFF),
        (uint8_t)((_addr >> 8)  & 0xFF),
        (uint8_t)(_addr         & 0xFF),
        (uint8_t)(retries),
        (uint8_t)((_bad >> 8)   & 0xFF),
        (uint8_t)(_bad          & 0xFF),
    };
    LOG_ERROR_ID_BYTES(MSG_ERR_WRITE_FAILED, _b, 6);
    handle->response_code = RESPONSE_CODE_ERROR;
}
```

### ascii_str populate for dev_tools.cpp:46 (bit_str)

```c
// BEFORE
log_info(bit_str);

// AFTER — MSG_INFO_BIT_STR params: [ascii_str] = {len, data...}
{
    uint8_t _len = (uint8_t)strlen(bit_str);
    uint8_t _b[1 + _len];  // VLA — or use a fixed max: uint8_t _b[32];
    _b[0] = _len;
    memcpy(&_b[1], bit_str, _len);
    LOG_INFO_ID_BYTES(MSG_INFO_BIT_STR, _b, 1 + _len);
}
// NOTE: avr-g++ supports VLAs but they add stack allocation overhead.
// Alternative: uint8_t _b[32]; _b[0] = _len; memcpy(&_b[1], bit_str, _len);
// Prefer the fixed-size version for AVR predictability.
```

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | `firestarter.cpp:86` `log_error(handle->response_msg)` is dead code because `json_parse()` in `json_parser.c` never sets `response_code = RESPONSE_CODE_ERROR` | Section 1 + Section 3 | If json_parse CAN set ERROR somehow, deleting this block loses an error report. Mitigated by noting json_parser.c was read and has no `response_code` assignment. Verify with a grep during implementation. |
| A2 | Stack arrays for `LOG_ID_BYTES` multi-param calls do not create RAM pressure issues on Uno | Section 3 + Section 10 | If Uno RAM is tighter than observed, multi-param error paths could overflow stack. Mitigated: error paths are rare and call-stack depth is shallow at those sites. |
| A3 | `flash_type_3.cpp` "Skipping erase of memory" site (MSG_INFO_SKIPPING_ERASE_MEM) is an OK-path `copy_to_buffer` call, not an ERROR/WARN populate-site, and is therefore Phase 8 territory | Section 1 | If it's actually a populate-site with ERROR/WARN code, it needs Phase 7 conversion. Verify during flash_type_3.cpp read in implementation. |

---

## Environment Availability

Phase 7 is firmware-only code edits. All required tools are present in the devcontainer.

| Dependency | Required By | Available | Version | Notes |
|------------|------------|-----------|---------|-------|
| PlatformIO CLI | Firmware builds + tests | Yes (devcontainer) | See `pio --version` | Required for `pio run` + `pio test` |
| Python 3.11+ | Catalog codegen + pytest | Yes (devcontainer) | 3.12.13 | Required for `codegen.py` |
| pytest 7+ | Host test suite | Yes (installed in venv) | per pyproject.toml | Required for `python -m pytest tests/` |
| avr-gcc toolchain | Firmware cross-compile | Yes (PlatformIO managed) | 7.3.0 (toolchain-atmelavr) | Managed by PIO |

No missing dependencies.

---

## Sources

### Primary (HIGH confidence — directly read source files)
- `firestarter/src/firestarter.cpp` — all call-sites enumerated by direct read [VERIFIED]
- `firestarter/src/operation_utils.cpp` — all call-sites enumerated by direct read [VERIFIED]
- `firestarter/src/dev_tools.cpp` — all call-sites enumerated by direct read [VERIFIED]
- `firestarter/src/eprom_operations.cpp` — all call-sites enumerated by direct read [VERIFIED]
- `firestarter/src/hardware_operations.cpp` — all call-sites enumerated by direct read [VERIFIED]
- `firestarter/src/proms/eprom.cpp` — all call-sites enumerated [VERIFIED]
- `firestarter/src/proms/flash_intel.cpp` — all call-sites enumerated [VERIFIED]
- `firestarter/src/proms/flash_type_4.cpp` — all call-sites enumerated [VERIFIED]
- `firestarter/src/proms/flash_utils.cpp` — all call-sites enumerated [VERIFIED]
- `firestarter/src/proms/eeprom_28c.cpp` — all call-sites enumerated [VERIFIED]
- `firestarter/src/proms/memory.cpp` — all call-sites enumerated [VERIFIED]
- `.planning/catalog/messages.toml` — D-03 pre-flight audit, all 68 entries cross-checked [VERIFIED]
- `firestarter/include/logging_id.h` — existing macro surface confirmed [VERIFIED]
- `firestarter/include/logging.h` — legacy macro tower confirmed intact [VERIFIED]
- `firestarter/test/native/avr/_shared/host_stubs_common.inc` — link-time stub inventory confirmed [VERIFIED]
- `firestarter/platformio.ini` — DEV_TOOLS active, EXTRA_INFO_LOGGING commented [VERIFIED]
- `.planning/phases/06-logging-infrastructure/06-VERIFICATION.md` — Phase 6 baseline numbers [CITED]
- `.planning/phases/06-logging-infrastructure/06-FLASH-MEASUREMENT.md` — measurement template [CITED]
- `.planning/phases/07-convert-error-warn-info-call-sites/07-CONTEXT.md` — locked decisions D-01..D-04b [CITED]

---

## Metadata

**Confidence breakdown:**
- Call-site inventory: HIGH — every file read directly at HEAD; grep cross-verified
- Catalog gap discovery: HIGH — all catalog entries cross-checked against all populate-sites
- host_stubs analysis: HIGH — stub file and src_filter both read directly
- firestarter.cpp:171 hybrid analysis: HIGH — surrounding context read; `command_done()` verified no downstream response_msg/response_code use
- Stack pressure for LOG_ID_BYTES: MEDIUM — no AVR stack profiling; assessment based on call-site depth and array sizes
- Flash delta estimate: MEDIUM — based on string-size arithmetic; actual linker output determines truth

**Research date:** 2026-05-18
**Valid until:** 2026-06-18 (stable codebase; valid until any proms/*.cpp call-site change)

---

## RESEARCH COMPLETE

**Phase:** 7 — Convert ERROR + WARN + INFO Call-Sites
**Confidence:** HIGH

### Key Findings

1. **3 catalog gaps confirmed (Phase 6 gaps):** `MSG_ERR_VPP_HIGH`, `MSG_ERR_CHIP_ID_MISMATCH`, `MSG_ERR_MEM_SIZE_TOO_SMALL` — all needed for dynamic-severity sites (FLAG_FORCE toggles WARN↔ERROR). Must be added via `chore(catalog):` commits before those call-sites can be converted (D-03 protocol).

2. **1 format-string drift:** `eprom.cpp:264` uses `"Chip ID: %#x dont match: %#x"` while catalog has `"Chip ID %#04x dont match expected ID %#04x"`. Call-site adapts per D-03.

3. **`firestarter.cpp:86` is dead code** — `log_error(handle->response_msg)` inside `if (handle->response_code == RESPONSE_CODE_ERROR)` after `json_parse()` is unreachable because `json_parser.c` never sets `response_code`. Delete the entire `if` block.

4. **host_stubs.cpp requires no changes** — `LOG_ERROR_ID_*` / `LOG_WARN_ID_*` macros expand to `rurp_log_id()` which is already provided by `rurp_serial_utils.cpp` in the native `src_filter`. No stub additions or removals.

5. **Recommended commit plan: 15 commits** — C-01 (logging_id.h infrastructure) → C-02..C-04 (catalog gap chore commits) → C-05..C-11 (populate-site wave, one per proms/*.cpp module) → C-12..C-15 (direct-log wave, one per file cluster). Full native test suite after every commit.

### File Created

`.planning/phases/07-convert-error-warn-info-call-sites/07-RESEARCH.md`

### Confidence Assessment

| Area | Level | Reason |
|------|-------|--------|
| Call-site inventory | HIGH | Every target file read directly; grep cross-verified |
| Catalog gap audit (D-03) | HIGH | All catalog entries read and cross-checked against populate-sites |
| Macro design (D-02) | HIGH | Direct template from existing LOG_INFO_ID_* in logging_id.h |
| host_stubs impact | HIGH | Source files read; linker dependency chain traced |
| Multi-param approach | HIGH | All param shapes verified in catalog; stack array approach confirmed from LOG_ID_BYTES precedent |
| Flash delta direction | MEDIUM | Estimate based on PROGMEM string accounting; linker output is authoritative |

### Open Questions

1. **flash_type_3.cpp "Skipping erase of memory" site** — is it an OK-path `copy_to_buffer` (Phase 8, leave alone) or an ERROR/WARN populate-site? Implementation should verify. Low risk: if it's OK-path, it doesn't affect SC#1 (grep only looks for `log_*` macros and `firestarter_error/warning_response*`).

2. **firestarter.cpp:86 defensive block removal** — should the `return false` inside the dead-code `if` block be retained as a guard, or deleted entirely? Recommendation: delete entirely (it's dead code). But the implementor should run a quick grep to confirm `json_parser.c` has no `response_code` assignments.

### Ready for Planning

**3 catalog gaps identified — D-03 pre-flight NOT clean.**
Gap summary: `MSG_ERR_VPP_HIGH` (0xB8), `MSG_ERR_CHIP_ID_MISMATCH` (0xB9), `MSG_ERR_MEM_SIZE_TOO_SMALL` (0xBA) — all needed for dynamic-severity populate-sites. Plan must include 3 catalog-gap chore commits (C-02..C-04) before the affected populate-site conversion commits (C-05, C-06, C-09, C-11).
