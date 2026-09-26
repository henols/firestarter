# Phase 6: Logging Infrastructure (catalog + codegen + helper + decoder) — Research

**Researched:** 2026-05-18
**Domain:** Embedded protocol design (Arduino C++ AVR) + Python host codegen pipeline + binary wire-frame decoding
**Confidence:** HIGH on existing-code inventory and wire-frame mechanics (verified via grep + read); MEDIUM-HIGH on codegen/catalog format recommendations (verified against environment); MEDIUM on AVR flash-cost claims (cited from AVR-GCC convention, not benchmarked in this session).

## Summary

Phase 6 is **infrastructure-only**. It introduces a canonical message catalog (meta-repo authoritative), a deterministic codegen tool that emits `firestarter/include/messages.h` + `firestarter_app/firestarter/messages.py`, a new firmware helper `rurp_log_id(uint8_t, const uint8_t*, uint8_t)` that emits the wire-frame defined in CONTEXT.md §D-01..D-04, and a host always-on byte-stream reader that decodes those frames into `LogMessage(severity, text)` objects (CONTEXT.md §D-05). No existing call-site is converted; both old text-format and new ID-frame paths coexist after Phase 6 (CONTEXT.md §D-06, LMIG-01).

The wire frame is locked: `0xAA 0x55 0xAA 0x55 | len | id | params… | crc8 | 0x0A`. CRC8 polynomial 0x07, seed 0x00, computed over `[id, params]` only. Total per-frame overhead = 7 bytes. The 4-byte magic + CRC8 design is the operator-validated answer to PORTD ghost-byte aliasing on the Uno (single-byte sentinels explicitly rejected).

The firmware grep below identifies **62 unique, active log call-sites** clustered into 7 severity categories (OK / INIT / MAIN / END / INFO / WARN / ERROR / DATA). Of these, **~52 unique format-strings** become catalog entries — fewer than the "66" estimate in the prompt because (a) several call-sites share an identical format string (e.g., `"VPP is low: %u.%uV < %u.%uV"` appears in both `eprom.cpp` and `flash_intel.cpp`; `"Chip ID %#04x dont match expected ID %#04x"` appears in 3 handlers), and (b) commented-out `// log_*` lines were excluded.

**Primary recommendation:** Use **TOML** (catalog source format) + **Python 3 stdlib** (`tomllib`, `pathlib`, `argparse`) for the codegen tool with **zero external dependencies**; the catalog lives at **`.planning/catalog/messages.toml`** (meta-repo authoritative) and is **vendored** into each sub-repo at `{sub-repo}/tools/catalog/messages.toml` via a checked-in sync script. Codegen emits LF-only files with a DO-NOT-EDIT banner and sorted-by-ID entries for byte-identical determinism. Both sub-repo CIs gain a pre-build "Codegen drift gate" step. Phase 6 **seeds the catalog with the full inventory of 52 unique strings** (with stable IDs allocated up-front) so Phases 7–9 are pure mechanical substitution.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|--------------|----------------|-----------|
| Canonical catalog (source of truth) | Meta-repo (planning) | — | Single point of edit; both sub-repos consume generated artifacts |
| Codegen tool | Meta-repo + vendored to both sub-repos (identical script) | — | Lives in `tools/` in each sub-repo so CI can invoke locally; sourced from meta-repo via sync script |
| Wire-frame emission | Firmware (AVR C++) | — | Hardware-side encoder lives in `boards/rurp_serial_utils.cpp` (board-agnostic) |
| `com_mode` + `SERIAL_DEBUG` gating | Firmware (board-specific) | — | Mirrors existing `rurp_log` discipline in `boards/uno_rurp_shield.cpp` |
| Always-on byte-stream reader | Host (Python) | — | `firestarter_app/firestarter/serial_comm.py` |
| Frame → `LogMessage` rendering | Host (Python) | — | Uses generated `messages.py` catalog for format-string + render hints |
| FW-version refuse guard | Host (Python) | — | `firestarter_app/firestarter/serial_comm.py:_probe_port` + `firmware.py:check_current_firmware` |
| CRC8 implementation | Firmware (shared C) + Host (Python) | — | Identical polynomial (0x07, no reflection) on both sides; firmware uses 256-byte PROGMEM table; host computes inline |
| CI drift gate | Both sub-repo CI (GitHub Actions) | — | `regen && git diff --exit-code` in each sub-repo workflow |

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| LCAT-01 | Single canonical catalog file with `{id, symbolic_name, format_string, parameter_shape}` per message | §"Catalog Format + Schema" + §"Catalog Seeding Policy" |
| LCAT-02 | Catalog validation: unique IDs, unique names, well-formed shapes, non-empty format strings | §"Catalog Format + Schema" §"Validation Rules" |
| LCAT-03 | Codegen produces `firestarter/include/messages.h` (C++ enum + `MSG_PARAM_COUNT(id)` helper) | §"Codegen Tool Design" §"Generated messages.h skeleton" |
| LCAT-04 | Codegen produces `firestarter_app/firestarter/messages.py` (host catalog) | §"Codegen Tool Design" §"Generated messages.py skeleton" |
| LCAT-05 | Codegen output is byte-identical on re-run (no timestamps, deterministic) | §"Codegen Idempotence Proof" |
| LFW-01 | `rurp_log_id(uint8_t, const uint8_t*, uint8_t)` helper exists, emits wire frame | §"Firmware `rurp_log_id` Design" |
| LFW-02 | Convenience macros `LOG_INFO(MSG_X)` etc. exist; no more verbose than current macros | §"Firmware `rurp_log_id` Design" §"Convenience Macros" |
| LFW-05 | Host fw-version check refuses pre-v1.2 firmware with operator-facing message | §"Host FW-Version Refuse Guard" |
| LHOST-01 | `serial_comm.py` parses ID-encoded frames, yields `LogMessage(severity, text)` | §"Host Decoder Design" + §"LHOST-01 Acceptance Fixture" |
| LHOST-02 | Per-param render hints: `[u24]` → `0x{:06X}` etc. | §"Param Shape + Render Hints" |
| LHOST-03 | Severity routing preserved (OK / INIT / MAIN / END / INFO / WARN / ERROR / DATA) | §"Host Decoder Design" §"Severity Routing" |
| LHOST-04 | FW-version refuse guard implemented + unit-tested | §"Host FW-Version Refuse Guard" |
| LCI-01 | Firmware sub-repo CI runs codegen, asserts no diff | §"CI Drift Gates" §"firestarter CI" |
| LCI-02 | Host sub-repo CI runs codegen, asserts no diff | §"CI Drift Gates" §"firestarter_app CI" |
| LCI-03 | Both sub-repo builds run codegen before compile/test | §"CI Drift Gates" |
| LCI-04 | Catalog validity is checked as part of codegen + CI | §"Catalog Format + Schema" §"Validation Rules" |
| LMIG-01 | Phase A: infrastructure-only; both old + new paths coexist; no call-sites converted | §"Catalog Seeding Policy" + §"Firmware `rurp_log_id` Design" §"Coexistence with `rurp_log`" |

</phase_requirements>

---

## User Constraints (from CONTEXT.md)

### Locked Decisions

- **D-01 Wire frame:** `0xAA 0x55 0xAA 0x55 | len | id | params… | crc8 | 0x0A`. `len` = 1 (id) + N (params) + 1 (crc); excludes itself + terminator.
- **D-02 Magic value rationale:** alternating-bit transitions, anti-PORTD-ghost-byte defence.
- **D-03 CRC8:** polynomial 0x07 (CCITT crc-8), seed 0x00, no reflection, no final XOR; over `[id, params]` only.
- **D-04 Terminator:** trailing `0x0A` is a re-sync anchor, NOT a delimiter.
- **D-05 Host parser:** always-on byte-stream reader, magic-scan with text-line fallback. Replaces line-by-line loop in `serial_comm.py:_read_and_parse_lines`.
- **D-06 Decoder coexistence:** No firmware call-site emits frames in Phase 6; LHOST-01 acceptance fixture is a Python-side hand-crafted frame.

### Claude's Discretion

Research recommends:
1. **Catalog file format** — TOML
2. **Catalog file path** — `.planning/catalog/messages.toml`
3. **Sub-repo distribution** — vendored copy + sync script (option a)
4. **Param shape + render hints** — per-type default render table + optional `render` field override (hybrid)
5. **Codegen language** — Python 3 (stdlib only)
6. **`MSG_PARAM_COUNT(id)` impl** — single `PROGMEM` table indexed by ID
7. **`rurp_log_id` + com_mode + SERIAL_DEBUG** — mirror exact discipline of existing `rurp_log` family

### Deferred Ideas (OUT OF SCOPE)

None — the operator stayed strictly within the wire-frame design space during discussion.

The three gray areas the operator deliberately skipped (catalog format, param-shape schema, decoder coexistence specifics) are NOT deferred ideas — they are explicit Claude's-Discretion items captured under `<decisions>` for the researcher to flesh out within Phase 6.

---

## Project Constraints (from CLAUDE.md)

- **Meta-repo** tracks only `.planning/` + `.claude/`. Sub-repos `firestarter/` (Arduino C++) and `firestarter_app/` (Python CLI) are independent git repos with their own `CLAUDE.md`.
- **Protocol changes** must be kept in sync between `firestarter_app/firestarter/serial_comm.py` and `firestarter/src/firestarter.cpp` — the catalog + generated files become the new mechanism for this synchronization.
- **Constants / flag bits** are duplicated between `firestarter_app/firestarter/constants.py` and `firestarter/include/firestarter.h`. The catalog **adds** a third surface (`messages.h`/`messages.py`) but does NOT change the constants duplication policy for command codes / flag bits.
- **Buffer sizes differ by board:** Uno = 512-byte data buffer; Leonardo = 1024 bytes (currently forced to 512 via `-D DATA_BUFFER_SIZE=512` in the Leonardo env for an A/B test). `rurp_log_id` wire-frame buffer is tiny (max ~32 bytes per frame for any realistic ID with ≤24 param bytes) so unaffected by board choice.
- **`pio run -e leonardo` Flash is at 98.7%** — every byte counts. `MSG_PARAM_COUNT` implementation choice is constrained by this. (See §"`MSG_PARAM_COUNT(id)` Implementation".)
- **`[env:native]` test rig** exists (`pio test -e native`) and is the recommended LHOST/codegen verification venue for the C++ side. ArduinoFake provides the `Serial.write` mock.
- **Host parser already survives PORTD ghost bytes** via the rightmost-prefix-wins discipline in `serial_comm.py:182`. Binary path inherits equivalent defence via 4-byte magic + CRC8. CLAUDE.md doesn't forbid touching either; both paths coexist after Phase 6.

---

## Existing Log Surface Inventory

This is the **load-bearing data** for catalog seeding. Phase 6 reserves IDs for every entry below; Phases 7–9 do mechanical substitution against this table.

**Method:** `grep -rE 'log_[a-z_]*\(|send_ack[_a-z]*\(|send_(init|main|end)_done\(|firestarter_(error|warning|data)_response[_a-z]*\(' src/ include/` in `firestarter/`, then deduplicated by format-string identity. Commented-out (`//`) lines excluded. 84 raw call-sites → **62 distinct active call-sites** → **52 unique format-strings** after deduplication. `[VERIFIED: grep results in /tmp/logsites.txt]`

### Severity Categories (current firmware mapping)

| Category | Firmware emit macro | Old prefix | Catalog ID range (recommended) | Count |
|----------|---------------------|-----------|--------------------------------|-------|
| OK       | `send_ack*` / `send_init_done` / `send_main_done` / `send_end_done` | `OK:` | 0x00 reserved-MSG_NONE; 0x01–0x0F | 6 |
| INIT     | `send_init_done` (state-machine ack) | `INIT:` | 0x10–0x1F | 1 |
| MAIN     | `send_main_done` (state-machine ack) | `MAIN:` | 0x20–0x2F | 1 |
| END      | `send_end_done` (state-machine ack) | `END:` | 0x30–0x3F | 1 |
| INFO     | `log_info*` | `INFO:` | 0x40–0x7F | ~25 |
| WARN     | `log_warn*` / `firestarter_warning_response*` | `WARN:` | 0x80–0x9F | ~5 |
| ERROR    | `log_error*` / `firestarter_error_response*` | `ERROR:` | 0xA0–0xDF | ~17 |
| DATA     | `log_data*` / `firestarter_data_response*` | `DATA:` | 0xE0–0xEF | ~3 |
| reserved | — | — | 0xF0–0xFF (future) | 0 |

**ID range rationale:** Categories cluster in ID ranges so a parser can extract severity from the ID itself if the catalog is unavailable (debugging convenience — not load-bearing, since the catalog is the protocol contract). Reserve gaps at the end of each range for future additions. `MSG_NONE = 0x00` is reserved as a sentinel.

### Full Catalog Seed (52 entries)

Tagged `[OK]`, `[INIT]`, `[MAIN]`, `[END]`, `[INFO]`, `[WARN]`, `[ERROR]`, `[DATA]`. `[ASSUMED]` annotations note where call-site grouping is ambiguous.

| ID | Symbolic name | Severity | Format string | Param shape | Source call-site(s) |
|----|--------------|----------|---------------|-------------|---------------------|
| 0x00 | `MSG_NONE` | — | (reserved sentinel) | `[]` | — |
| 0x01 | `MSG_OK_READY` | OK | `Ready` | `[]` | `hardware_operations.cpp:42` |
| 0x02 | `MSG_OK_REQ_DATA` | OK | `Req data` | `[]` | `eprom_operations.cpp:78` |
| 0x03 | `MSG_OK_FW_VERSION` | OK | `FW_VERSION` (text literal) | (special — see below) | `hardware_operations.cpp:78` |
| 0x04 | `MSG_OK_REV` | OK | `Rev%d%s` | `[u8, ascii_str]` (special) | `hardware_operations.cpp:87` |
| 0x05 | `MSG_OK_CFG` | OK | `R1: %ld, R2: %ld%s` | `[i32, i32, ascii_str]` | `hardware_operations.cpp:97,99` |
| 0x06 | `MSG_OK_FW_HANDSHAKE` | OK | `FW: %s, HW: Rev%d, Cmd: 0x%02x` | (special — see below) | `firestarter.cpp:152-156` |
| 0x10 | `MSG_INIT_DONE` | INIT | `` (empty) | `[]` | `operation_utils.cpp:274` |
| 0x20 | `MSG_MAIN_DONE` | MAIN | `` (empty) | `[]` | `operation_utils.cpp:197` |
| 0x30 | `MSG_END_DONE` | END | `` (empty) | `[]` | `operation_utils.cpp:276` |
| 0x40 | `MSG_INFO_MAIN_START` | INFO | `Main start` | `[]` | `operation_utils.cpp:226` |
| 0x41 | `MSG_INFO_MAIN_DONE` | INFO | `Main done` | `[]` | `operation_utils.cpp:195` |
| 0x42 | `MSG_INFO_INIT_START` | INFO | `Init start` | `[]` | `operation_utils.cpp:258` |
| 0x43 | `MSG_INFO_END_START` | INFO | `End start` | `[]` | `operation_utils.cpp:260` |
| 0x44 | `MSG_INFO_BUF_VAL` | INFO | `Buf val: 0x%02x` | `[u8]` | `firestarter.cpp:66` |
| 0x45 | `MSG_INFO_TOKEN_COUNT` | INFO | `Token count: %d` | `[i16]` | `firestarter.cpp:73` |
| 0x46 | `MSG_INFO_FLAG_FORCE` | INFO | `Force: %d` | `[u8]` | `firestarter.cpp:93` |
| 0x47 | `MSG_INFO_FLAG_CAN_ERASE` | INFO | `Can erase: %d` | `[u8]` | `firestarter.cpp:94` |
| 0x48 | `MSG_INFO_FLAG_SKIP_ERASE` | INFO | `Skip erase: %d` | `[u8]` | `firestarter.cpp:91` |
| 0x49 | `MSG_INFO_FLAG_SKIP_BLANK` | INFO | `Skip blank check: %d` | `[u8]` | `firestarter.cpp:92` |
| 0x4A | `MSG_INFO_FLAG_VPE_AS_VPP` | INFO | `VPE as VPP: %d` | `[u8]` | `firestarter.cpp:93` |
| 0x4B | `MSG_INFO_FLAG_OUTPUT_EN` | INFO | `Output enable: %d` | `[u8]` | `firestarter.cpp:102` |
| 0x4C | `MSG_INFO_FLAG_CHIP_EN` | INFO | `Chip enable: %d` | `[u8]` | `firestarter.cpp:103` |
| 0x4D | `MSG_INFO_BUFFER_SIZE` | INFO | `Buffer size: %d` | `[u16]` | `firestarter.cpp:127` |
| 0x4E | `MSG_INFO_MEM_SIZE` | INFO | `Memory size 0x%lx` | `[u32]` | `firestarter.cpp:142` |
| 0x4F | `MSG_INFO_ADDR_MASK` | INFO | `Address mask 0x%lx` | `[u32]` | `firestarter.cpp:143` |
| 0x50 | `MSG_INFO_MATCH_LINES` | INFO | `Matching lines %u` | `[u16]` | `firestarter.cpp:144` |
| 0x51 | `MSG_INFO_RETRIES` | INFO | `Number of retries: %d` | `[u8]` | `eprom.cpp:170` |
| 0x52 | `MSG_INFO_REG_HEADER` | INFO | `%s: 0x%02X` | `[ascii_str, u8]` | `dev_tools.cpp:23` |
| 0x53 | `MSG_INFO_BIT_HEADER` | INFO | `%s\|D7\|D6\|D5\|D4\|D3\|D2\|D1\|D0\|` | `[ascii_str]` | `dev_tools.cpp:26` |
| 0x54 | `MSG_INFO_BIT_STR` | INFO | `%s` | `[ascii_str]` | `dev_tools.cpp:46` |
| 0x55 | `MSG_INFO_CE_OE` | INFO | `CE: %d, OE: %d` | `[u8, u8]` | `dev_tools.cpp:66,102` |
| 0x56 | `MSG_INFO_ADDR` | INFO | `Address: 0x%06x` | `[u24]` | `dev_tools.cpp:103` |
| 0x57 | `MSG_INFO_ADDR_REMAP` | INFO | `Address: 0x%06x remappend` | `[u24]` | `dev_tools.cpp:105` |
| 0x58 | `MSG_INFO_SKIPPING_ERASE` | INFO | `Skipping erase.` | `[]` | `eprom.cpp:103`, `flash_type_4.cpp:51` |
| 0x59 | `MSG_INFO_SKIPPING_ERASE_MEM` | INFO | `Skipping erase of memory` | `[]` | `flash_type_3.cpp:87` |
| 0x80 | `MSG_WARN_REV0_VPP_UNSUPPORTED` | WARN | `Rev0 dont support reading VPP/VPE` | `[]` | `flash_intel.cpp:29`, `eprom.cpp:203` |
| 0x81 | `MSG_WARN_VPP_LOW` | WARN | `VPP is low: %u.%uV < %u.%uV` | `[u16, u16, u16, u16]` `[ASSUMED]` (four `%u.%u` slots — current code passes 4 args via `_format`) | `flash_intel.cpp:45`, `eprom.cpp:227` |
| 0x82 | `MSG_WARN_VPP_HIGH` | WARN | `VPP is high: %u.%uV > %u.%uV` | `[u16, u16, u16, u16]` | `flash_intel.cpp:41`, `eprom.cpp:223` |
| 0x83 | `MSG_WARN_CHIP_ID_MISMATCH` | WARN | `Chip ID %#04x dont match expected ID %#04x` | `[u16, u16]` | `flash_intel.cpp:159`, `flash_type_3.cpp:135`, `eeprom_28c.cpp:71` |
| 0x84 | `MSG_WARN_MEM_SIZE_TOO_SMALL` | WARN | `mem_size %lu too small for chip-id check` | `[u32]` | `eeprom_28c.cpp:58` |
| 0xA0 | `MSG_ERR_BAD_JSON` | ERROR | `Bad JSON` | `[]` | `firestarter.cpp:67` |
| 0xA1 | `MSG_ERR_NO_CMD` | ERROR | `No cmd` | `[]` | `firestarter.cpp:75` |
| 0xA2 | `MSG_ERR_SETUP` | ERROR | `Setup error` | `[]` | `firestarter.cpp:96` |
| 0xA3 | `MSG_ERR_PARSE_CFG` | ERROR | `Failed parsing config` | `[]` | `firestarter.cpp:111` |
| 0xA4 | `MSG_ERR_EMPTY_INPUT` | ERROR | `Empty input` | `[]` | `firestarter.cpp:130` |
| 0xA5 | `MSG_ERR_NOT_SUPPORTED` | ERROR | `Not supported` | `[]` | `eprom_operations.cpp:41` |
| 0xA6 | `MSG_ERR_NO_CHIP_ID` | ERROR | `No chip ID` | `[]` | `eprom_operations.cpp:50` |
| 0xA7 | `MSG_ERR_OUT_OF_RANGE` | ERROR | `Out of range` | `[]` | `eprom_operations.cpp:91` |
| 0xA8 | `MSG_ERR_TIMEOUT` | ERROR | `Timeout` | `[]` | `operation_utils.cpp:124` |
| 0xA9 | `MSG_ERR_DATA_ERR_N` | ERROR | `Data err %d` | `[i16]` | `operation_utils.cpp:179` (was `log_error_P_int("Data err ", res)`) |
| 0xAA | `MSG_ERR_CMD_TIMEOUT` | ERROR | `Cmd: %d, timeout` | `[u8]` | `firestarter.cpp:171` |
| 0xAB | `MSG_ERR_UNKNOWN_CMD` | ERROR | `Unknown cmd: %d` | `[u8]` | `firestarter.cpp:238` (was `log_error_P_int_buf`) |
| 0xAC | `MSG_ERR_REV0_VPP_RD` | ERROR | `Rev0 dont support reading VPP/VPE` | `[]` | `hardware_operations.cpp:20` |
| 0xAD | `MSG_ERR_CMD` | ERROR | `Error cmd` | `[]` | `hardware_operations.cpp:33` |
| 0xAE | `MSG_ERR_MEM_TYPE_UNSUPPORTED` | ERROR | `Memory type 0x%02x not supported` | `[u8]` | `memory.cpp:116` |
| 0xAF | `MSG_ERR_VERIFY` | ERROR | `0x%02x != 0x%02x at 0x%06x` | `[u8, u8, u24]` | `memory.cpp:223` |
| 0xB0 | `MSG_ERR_NOT_BLANK` | ERROR | `Not blank, at 0x%06x, v: 0x%02x` | `[u24, u8]` | `memory.cpp:359` |
| 0xB1 | `MSG_ERR_WRITE_FAILED` | ERROR | `Failed to write memory, 0x%06x, retries: %d, bad bytes: %d` | `[u24, u8, u16]` | `eprom.cpp:182` |
| 0xB2 | `MSG_ERR_EEPROM_TIMEOUT` | ERROR | `EEPROM timeout at 0x%06lx: wrote 0x%02x got 0x%02x` | `[u24, u8, u8]` | `eeprom_28c.cpp:120` |
| 0xB3 | `MSG_ERR_FL4_VERIFY_TIMEOUT` | ERROR | `Timeout verifying 0x%02x at 0x%06lx (got 0x%02x)` | `[u8, u24, u8]` | `flash_type_4.cpp:88` |
| 0xB4 | `MSG_ERR_INTEL_VPP` | ERROR | `Intel flash: VPP error` | `[]` | `flash_intel.cpp:135` |
| 0xB5 | `MSG_ERR_INTEL_PROGRAM` | ERROR | `Intel flash: program error` | `[]` | `flash_intel.cpp:140` |
| 0xB6 | `MSG_ERR_INTEL_SR_TIMEOUT` | ERROR | `Intel flash: SR timeout` | `[]` | `flash_intel.cpp:147` |
| 0xB7 | `MSG_ERR_OP_TIMEOUT` | ERROR | `Operation timed out` | `[]` | `flash_utils.cpp:47` |
| 0xE0 | `MSG_DATA_PROGRESS` | DATA | `%lu/%lu` | `[u32, u32]` | `memory.cpp:375` |
| 0xE1 | `MSG_DATA_VOLTAGE` | DATA | `%s: %u.%uV, Internal VCC: %u.%uV` | `[ascii_str, u16, u16, u16, u16]` | `hardware_operations.cpp:65` |
| 0xE2 | `MSG_DATA_SENDING` | DATA | `Sending data` | `[]` | `eprom_operations.cpp:114` |

**Special handling required:**

- **`MSG_OK_FW_HANDSHAKE` (ID 0x06)** — locked text-format per LFW-05 (the FW version handshake response must be text-format so the host can read the version BEFORE loading the catalog). Catalog declares this entry with `wire_format: text` so codegen knows NOT to generate an `LOG_OK(MSG_OK_FW_HANDSHAKE)` macro for it; the firmware keeps using `send_ack_format(PARSE_RESPONSE, …)` until Phase 9 (and even there, the FW response stays text per LFW-05). Phase 6 catalog records the format string for completeness only.
- **`MSG_OK_FW_VERSION` (ID 0x03)** — same exemption (`send_ack_const(FW_VERSION)` in `hardware_operations.cpp:78` carries the version string for `fw_get_version`).
- **`MSG_INFO_BIT_STR` (ID 0x54)** — `log_info(bit_str)` where `bit_str` is a runtime-formatted RAM string from `dev_tools.cpp:30-45`. Two options: (a) catalog declares it as `[ascii_str]` and the firmware sends the buffer as raw bytes prefixed by a length byte; (b) firmware converts the bit-string render into structured params and host re-renders. **Recommendation:** option (a) — simplest, preserves dev-tool semantics; adds a single `ascii_str` shape type to the catalog (see §"Param Shape + Render Hints").
- **`handle->response_msg` dispatch in `operation_utils.cpp:_check_response` (lines 324, 328, 331, 336)** — these `log_info(handle->response_msg)` / `log_warn(...)` / `log_data(...)` / `log_error(...)` calls forward an already-formatted RAM buffer back to the host. The buffer was populated by some upstream `firestarter_error_response_format("...")` call which IS in the catalog (e.g., `MSG_ERR_VERIFY`, `MSG_WARN_VPP_LOW`, `MSG_DATA_PROGRESS`). Phases 7–8 will refactor these dispatches to call `rurp_log_id` directly at the populate site, eliminating the `response_msg` round-trip. Phase 6 ONLY enumerates the catalog; the dispatch refactor lives in Phase 7. (Catalog seeds cover both the populate-site format-strings and the dispatch-time category indirection.)

**Format-string preservation rule:** Catalog format strings use C-style printf specifiers verbatim (`%d`, `%u`, `%lu`, `%02x`, `%06x`, `%#04x`, `%s`, `%c`, etc.). Host renders them via Python's `%`-formatting (which is compatible with C printf for these specifiers, with `%lu` mapped to `%d` since Python ints are arbitrary precision). LHOST-02 per-type defaults (e.g., `u24` → `0x{:06X}`) are applied ONLY when the catalog declares `render: hex_addr` explicitly — verbatim format-string preservation is the default. See §"Param Shape + Render Hints".

---

## Catalog Format + Schema

### Recommendation: TOML

**Decision:** TOML over YAML / JSON / DSL.

| Criterion | TOML | YAML | JSON | DSL |
|-----------|------|------|------|-----|
| Stdlib parse (Py ≥3.11) | ✓ `tomllib` | ✗ requires PyYAML | ✓ `json` | ✗ |
| Deterministic-parse (no map-ordering surprises) | ✓ stable order | ⚠ YAML 1.1 vs 1.2 ambiguity | ✓ | ✓ |
| Human-editable / diff-friendly | ✓ | ✓ | ⚠ noisy quotes/braces | ✓ |
| Comment support | ✓ `#` | ✓ `#` | ✗ | ✓ |
| Quote handling for printf strings | ✓ basic strings + literal `'...'` for `\` | ⚠ ambiguous around `:` and special chars | ✓ | ✓ |
| External dependency risk | none | PyYAML not installed `[VERIFIED]` | none | bespoke parser to write |

`[VERIFIED: python3 -c "import tomllib"` succeeds on this machine; `import yaml` fails with `ModuleNotFoundError`. Python = 3.12.13.]`

TOML wins on **zero external dependency** (decisive given both sub-repos run codegen in CI; adding PyYAML to two `requirements.txt` files for what is essentially a constants table is unnecessary). TOML's deterministic-parse and array-of-tables syntax suit the catalog shape exactly.

**Trade-off:** TOML's array-of-tables `[[messages]]` syntax is slightly more verbose per entry than YAML; offset by zero install steps and unambiguous quoting.

### Schema

```toml
# .planning/catalog/messages.toml
# Firestarter v1.2 log-message catalog (canonical source — meta-repo authoritative)
#
# DO NOT REORDER ENTRIES. Codegen sorts by id ascending; the source file order is
# preserved for human-edit diff readability.

[catalog]
version = 1            # bumped when a breaking schema change happens (additive
                       # changes — new entries, new render types — keep version=1)
project = "firestarter"

# --- One [[messages]] table per log entry ---
[[messages]]
id            = 0x01                       # 1-byte unique integer 1-255 (0x00 reserved)
name          = "MSG_OK_READY"             # C++ enum symbol + Python constant
severity      = "OK"                       # OK | INIT | MAIN | END | INFO | WARN | ERROR | DATA
format        = "Ready"                    # printf-style format string (English)
params        = []                         # [] for no params
wire_format   = "id_frame"                 # id_frame (default) | text (legacy exemption for FW handshake)

[[messages]]
id            = 0x4E
name          = "MSG_INFO_MEM_SIZE"
severity      = "INFO"
format        = "Memory size 0x%lx"
params        = [{ type = "u32" }]         # implicit render: per-type default = "hex" for u32

[[messages]]
id            = 0x56
name          = "MSG_INFO_ADDR"
severity      = "INFO"
format        = "Address: 0x%06x"
params        = [{ type = "u24", render = "hex_addr" }]   # explicit render override

[[messages]]
id            = 0xB1
name          = "MSG_ERR_WRITE_FAILED"
severity      = "ERROR"
format        = "Failed to write memory, 0x%06x, retries: %d, bad bytes: %d"
params        = [
    { type = "u24", render = "hex_addr" },
    { type = "u8" },
    { type = "u16" },
]

[[messages]]
id            = 0x52
name          = "MSG_INFO_REG_HEADER"
severity      = "INFO"
format        = "%s: 0x%02X"
params        = [
    { type = "ascii_str" },
    { type = "u8", render = "hex_byte" },
]
```

### Validation Rules (LCAT-02 + LCI-04)

Codegen fails non-zero with a clear error if ANY of the following is violated:

1. `id` is missing, not an int, not in `[0, 255]`, or duplicates a prior `id`.
2. `name` is missing, not a string matching `^MSG_[A-Z][A-Z0-9_]*$`, or duplicates a prior `name`.
3. `format` is missing or empty.
4. `params` is missing or not a list of tables.
5. Each param's `type` ∈ {`u8`, `u16`, `u24`, `u32`, `i8`, `i16`, `i32`, `ascii_str`}. Anything else fails.
6. Each param's `render` (if present) ∈ {`dec`, `hex`, `hex_byte`, `hex_word`, `hex_addr`, `hex_dword`, `signed_dec`, `ascii_char`, `ascii_str`}. Anything else fails.
7. `severity` ∈ {`OK`, `INIT`, `MAIN`, `END`, `INFO`, `WARN`, `ERROR`, `DATA`}.
8. `wire_format` ∈ {`id_frame`, `text`}; default `id_frame`. Entries with `wire_format = "text"` may have `params = []` only (the host never decodes a text-format frame as an ID frame, so param shape is meaningless for them).
9. **Format-string vs param-count consistency:** count printf specifiers in `format` (excluding `%%`); compare against `len(params)`. Mismatch fails. (Implementation: simple regex `%[lh]?[duxX%s]` count.) `ascii_str` params count toward `%s` specifiers.
10. **Total param byte width ≤ 24** — a safety cap so the largest realistic frame fits comfortably under the firmware's wire-write buffer (max frame = 4 magic + 1 len + 1 id + 24 params + 1 crc + 1 nl = 32 bytes; well under the 64-byte serial TX buffer on both Uno and Leonardo). `ascii_str` counts as 1 byte for the length prefix + up to 31 bytes of payload (so a single `ascii_str` param uses ≤32 bytes alone; combining `ascii_str` with other params is fine as long as total budget stays under 64 bytes). Validation enforces 24-byte budget for non-ascii_str params; the single ascii_str case is special-cased.

---

## Catalog Location + Distribution Model

### Recommendation

**Catalog source-of-truth path (meta-repo authoritative):**
```
.planning/catalog/messages.toml
.planning/catalog/codegen.py             # the codegen tool
.planning/catalog/sync_to_subrepos.sh    # convenience script
```

**Vendored copy in each sub-repo:**
```
firestarter/tools/catalog/messages.toml       # vendored
firestarter/tools/catalog/codegen.py          # vendored
firestarter/include/messages.h                # generated, committed

firestarter_app/tools/catalog/messages.toml   # vendored
firestarter_app/tools/catalog/codegen.py      # vendored
firestarter_app/firestarter/messages.py       # generated, committed
```

### Why Vendored (option a)

| Option | Verdict | Why |
|--------|---------|-----|
| (a) Vendored copy + sync script | ✓ **chosen** | Sub-repos remain self-contained: clone → `pip install -e .` works without any external clones; CI step is trivial (`python tools/catalog/codegen.py && git diff --exit-code`); meta-repo authority enforced by the sync-and-PR convention + a CI assertion that `tools/catalog/messages.toml` matches the meta-repo copy (see below). |
| (b) Git submodule | ✗ | Adds submodule init complexity to every clone; the meta-repo isn't checked out alongside the sub-repos normally; failure modes (detached HEAD, submodule drift) are operationally noisy for a small constants table. |
| (c) Generated-only + shared CI runner | ✗ | Defeats LCI-03 ("developer who edits the canonical catalog locally sees the updated generated files appear in their working tree"). A developer editing the catalog couldn't regenerate locally without cloning the meta-repo first. |

### Sync Script (`sync_to_subrepos.sh`)

Bash script in the meta-repo. Idempotent. Path-aware (operator runs from the meta-repo root). Copies `messages.toml` and `codegen.py` into both sub-repos at the paths above. Operator runs it after editing the catalog; commits the result to both sub-repos as part of the same logical change. The script exits non-zero if either sub-repo is dirty or if the copies match (no-op feedback). Phase 6 plan includes both the script and a `make sync` convenience target if the operator prefers.

### Authority Assertion (recommended addition to both sub-repo CIs)

The meta-repo cannot directly enforce that `firestarter/tools/catalog/messages.toml` and the authoritative `.planning/catalog/messages.toml` are byte-identical (sub-repos don't see the meta-repo in CI). The pragmatic compromise:

1. The vendored copy is a **mirror** of the meta-repo canonical file; sync drift is a soft convention enforced by the operator's PR review.
2. **Both sub-repos' vendored copies MUST be byte-identical** to each other. CI step:
   ```
   diff firestarter/tools/catalog/messages.toml firestarter_app/tools/catalog/messages.toml
   ```
   This is added to whichever release/integration workflow runs against both sub-repos (e.g., the meta-repo's planning CI if it exists, or a manual pre-tag check). For Phase 6, the simpler path: ONE meta-repo CI workflow (new file: `.github/workflows/catalog-sync-check.yml`) clones both sub-repos and asserts the diff is empty. **This is the load-bearing assertion** that drift between sub-repos doesn't silently corrupt the protocol contract.
3. As a fallback, the operator can include a SHA-256 hash of the catalog in `[catalog]` metadata; both sub-repos verify the hash matches the file content at codegen time. This is belt-and-braces — the diff check is the canonical mechanism.

**Phase 6 plan:** include the vendored copies + sync script + the cross-sub-repo diff CI gate.

---

## Param Shape + Render Hints

### Recommendation: Per-type default render table + optional explicit override

**Decision:** Hybrid. Catalog declares `params = [{ type = "u24" }, ...]`; if no explicit `render` is given, the codegen looks up the per-type default render. Catalog can override with `render = "..."` per-param when the default doesn't fit (e.g., `u32` defaults to `hex` but `MSG_DATA_PROGRESS` wants `dec`).

### Per-Type Default Render Table

| Param `type` | Wire bytes (MSB first) | Default `render` | Python format spec | Example output |
|--------------|------------------------|------------------|--------------------|----------------|
| `u8` | 1 | `dec` | `"%d"` (from format string) | `42` |
| `i8` | 1 (signed, two's complement) | `signed_dec` | `"%d"` | `-1` |
| `u16` | 2 | `dec` | `"%u"` | `12345` |
| `i16` | 2 | `signed_dec` | `"%d"` | `-256` |
| `u24` | 3 | `hex_addr` | `"0x%06X"` | `0x01F4A2` |
| `u32` | 4 | `hex` | `"0x%lx"` (lowercase to match printf) | `0x12345678` |
| `i32` | 4 | `signed_dec` | `"%ld"` | `-2000000000` |
| `ascii_str` | 1 length byte + N data bytes (N ≤ 31) | `ascii_str` | `"%s"` | `"VPP"` |

### Override `render` Values

| `render` | Python format spec | When to use |
|----------|--------------------|-----|
| `dec` | `"%d"` / `"%u"` (per format string) | Decimal — most integer counts |
| `hex_byte` | `"%02x"` or `"%02X"` (case from format string) | 1-byte values rendered as 2 hex digits |
| `hex_word` | `"%04x"` / `"%04X"` | 2-byte values rendered as 4 hex digits |
| `hex_addr` | `"%06x"` / `"%06X"` | 3-byte addresses (24-bit address space) |
| `hex_dword` | `"%08x"` / `"%08X"` | 4-byte hex |
| `hex` | `"%x"` / `"%lx"` (variable-width, matches `%lx` in format) | Generic hex without padding |
| `signed_dec` | `"%d"` / `"%ld"` | Explicit signed |
| `ascii_char` | `"%c"` | Single character (paired with a `u8` that's an ASCII codepoint) |
| `ascii_str` | `"%s"` | Variable-length string |

**Key insight:** the catalog's `format` string already encodes the desired output format via printf specifiers. The `type` carries the wire-byte layout; the `render` is mostly a sanity-cross-check + an indicator for the host of how to extract the value (signed vs unsigned). The host always renders by applying the catalog's `format` to the decoded param tuple via Python's `%` operator (which handles `%d`, `%u`, `%x`, `%X`, `%lx`, `%lu`, `%02x`, `%06x`, `%s`, `%c` correctly).

### Schema Examples Covering Every Param Type

Every distinct `type` from the catalog seed appears at least once below; the hybrid scheme covers the full inventory of 52 entries.

```toml
# u8 (most common — flag values, counters)
[[messages]]
id     = 0x46
name   = "MSG_INFO_FLAG_FORCE"
format = "Force: %d"
params = [{ type = "u8" }]

# u16
[[messages]]
id     = 0x4D
name   = "MSG_INFO_BUFFER_SIZE"
format = "Buffer size: %d"
params = [{ type = "u16" }]

# u24 with default render (hex_addr)
[[messages]]
id     = 0x56
name   = "MSG_INFO_ADDR"
format = "Address: 0x%06x"
params = [{ type = "u24" }]

# u32 with override (default would be hex; this case wants decimal)
[[messages]]
id     = 0xE0
name   = "MSG_DATA_PROGRESS"
format = "%lu/%lu"
params = [{ type = "u32", render = "dec" }, { type = "u32", render = "dec" }]

# i16 (only for negative error codes — sparse usage)
[[messages]]
id     = 0xA9
name   = "MSG_ERR_DATA_ERR_N"
format = "Data err %d"
params = [{ type = "i16" }]

# Mixed shape with ascii_str + u8 + u16
[[messages]]
id     = 0xB1
name   = "MSG_ERR_WRITE_FAILED"
format = "Failed to write memory, 0x%06x, retries: %d, bad bytes: %d"
params = [{ type = "u24" }, { type = "u8" }, { type = "u16" }]
```

---

## Codegen Tool Design

### Recommendation: Python 3.11+ stdlib only

**Invocation (identical from each sub-repo):**

```bash
# from firestarter/ root:
python3 tools/catalog/codegen.py --catalog tools/catalog/messages.toml \
                                 --target firestarter/include/messages.h \
                                 --language cpp

# from firestarter_app/ root:
python3 tools/catalog/codegen.py --catalog tools/catalog/messages.toml \
                                 --target firestarter/messages.py \
                                 --language python
```

Single Python script (`codegen.py`) emits either C++ or Python depending on `--language`. Same script lives in both sub-repos (byte-identical via the sync script). `--check` flag does parse + validation only (LCI-04 standalone usage).

**Python version requirement:** ≥3.11 (for `tomllib`). Both sub-repos already declare `requires-python = ">=3.9"` in `pyproject.toml` `[VERIFIED: firestarter_app/pyproject.toml line shown above]`; for codegen specifically, CI bumps to Python 3.11+ (already standard on Ubuntu LTS GitHub Actions runners). The host CLI itself does not bump its minimum Python — `messages.py` is the GENERATED output, plain Python with no `tomllib` dependency, so it works on 3.9+ as today.

### Generated `messages.h` Skeleton

```cpp
/*
 * Firestarter — v1.2 log-message catalog (C++ side)
 *
 * DO NOT EDIT — generated by tools/catalog/codegen.py from
 *               tools/catalog/messages.toml.
 * Re-run codegen after editing the canonical catalog.
 *
 * Catalog version: 1
 * Total messages: 52
 */

#ifndef __MESSAGES_H__
#define __MESSAGES_H__

#include <stdint.h>
#include <avr/pgmspace.h>

// --- Severity codes (mirrors host catalog) ---
#define MSG_SEVERITY_OK     0x01
#define MSG_SEVERITY_INIT   0x02
#define MSG_SEVERITY_MAIN   0x03
#define MSG_SEVERITY_END    0x04
#define MSG_SEVERITY_INFO   0x05
#define MSG_SEVERITY_WARN   0x06
#define MSG_SEVERITY_ERROR  0x07
#define MSG_SEVERITY_DATA   0x08

// --- Message IDs (sorted ascending) ---
#define MSG_NONE                          0x00
#define MSG_OK_READY                      0x01
#define MSG_OK_REQ_DATA                   0x02
// ... etc ...
#define MSG_INFO_MEM_SIZE                 0x4E
// ...
#define MSG_DATA_SENDING                  0xE2

// --- Param-count lookup (PROGMEM table, 256 bytes flat) ---
// MSG_PARAM_COUNT(id) returns the wire-byte count of the params for the
// given ID, or 0xFF for unallocated IDs. Used by rurp_log_id callers that
// need to know the byte count before assembling the params buffer.
extern const uint8_t MSG_PARAM_BYTES_TABLE[256] PROGMEM;

#define MSG_PARAM_COUNT(id) ((uint8_t)pgm_read_byte(&MSG_PARAM_BYTES_TABLE[(id)]))

#endif  // __MESSAGES_H__
```

…plus a generated `messages.c` (companion TU) that defines the PROGMEM table:

```cpp
// DO NOT EDIT — generated by tools/catalog/codegen.py
#include "messages.h"

const uint8_t MSG_PARAM_BYTES_TABLE[256] PROGMEM = {
    [0x00] = 0xFF,         // MSG_NONE — sentinel
    [0x01] = 0,            // MSG_OK_READY — no params
    [0x02] = 0,            // MSG_OK_REQ_DATA — no params
    // ...
    [0x4E] = 4,            // MSG_INFO_MEM_SIZE — u32
    // ...
    [0xB1] = 6,            // MSG_ERR_WRITE_FAILED — u24+u8+u16 = 3+1+2 = 6
    // unallocated entries default to 0xFF via the C initializer rules:
};
```

Designated initializers (`[0x01] = 0`) are AVR-GCC compatible (C99+) and produce the same flat 256-byte PROGMEM array as a hand-written one. Unassigned positions get `0xFF` if the codegen emits an explicit fill, or `0x00` if relying on default-init — the codegen MUST emit the explicit `0xFF` fill for unassigned slots so the value of `MSG_PARAM_COUNT(<unallocated>)` is unambiguous.

### Generated `messages.py` Skeleton

```python
"""
Firestarter — v1.2 log-message catalog (host side)

DO NOT EDIT — generated by tools/catalog/codegen.py from
              tools/catalog/messages.toml.
Re-run codegen after editing the canonical catalog.

Catalog version: 1
Total messages: 52
"""

from dataclasses import dataclass
from typing import Tuple

# --- Severity codes (mirrors firmware) ---
SEVERITY_OK    = 0x01
SEVERITY_INIT  = 0x02
SEVERITY_MAIN  = 0x03
SEVERITY_END   = 0x04
SEVERITY_INFO  = 0x05
SEVERITY_WARN  = 0x06
SEVERITY_ERROR = 0x07
SEVERITY_DATA  = 0x08

SEVERITY_LABEL = {
    SEVERITY_OK: "OK",
    SEVERITY_INIT: "INIT",
    SEVERITY_MAIN: "MAIN",
    SEVERITY_END: "END",
    SEVERITY_INFO: "INFO",
    SEVERITY_WARN: "WARN",
    SEVERITY_ERROR: "ERROR",
    SEVERITY_DATA: "DATA",
}

@dataclass(frozen=True)
class MessageDef:
    id: int
    name: str
    severity: int
    format: str
    params: Tuple[Tuple[str, str], ...]   # ((type, render), ...)
    param_bytes: int                       # total wire byte count
    wire_format: str                       # "id_frame" or "text"

# --- ID constants (sorted ascending) ---
MSG_NONE              = 0x00
MSG_OK_READY          = 0x01
MSG_OK_REQ_DATA       = 0x02
# ... etc ...
MSG_INFO_MEM_SIZE     = 0x4E
# ...
MSG_DATA_SENDING      = 0xE2

# --- Catalog lookup ---
CATALOG: dict[int, MessageDef] = {
    0x01: MessageDef(id=0x01, name="MSG_OK_READY",
                     severity=SEVERITY_OK, format="Ready",
                     params=(), param_bytes=0, wire_format="id_frame"),
    0x02: MessageDef(id=0x02, name="MSG_OK_REQ_DATA",
                     severity=SEVERITY_OK, format="Req data",
                     params=(), param_bytes=0, wire_format="id_frame"),
    # ...
    0x4E: MessageDef(id=0x4E, name="MSG_INFO_MEM_SIZE",
                     severity=SEVERITY_INFO, format="Memory size 0x%lx",
                     params=(("u32", "hex"),), param_bytes=4, wire_format="id_frame"),
    # ...
}
```

### Codegen Idempotence Proof (LCAT-05)

The CI drift gate (`regen && git diff --exit-code`) is the operational proof. The script enforces idempotence by:

1. **Sort by ID ascending** — `messages` are read into a list, then sorted by `id` before emission. Source TOML order is irrelevant.
2. **No timestamps** — banner uses a fixed string, NOT `datetime.now()`.
3. **LF line endings only** — `pathlib.Path.write_text(content, newline='\n')`. Codegen explicitly opens with `newline=''` and writes `\n`-terminated strings.
4. **Explicit ordering of all dict iterations** — `for entry in sorted(catalog["messages"], key=lambda m: m["id"])` (not implicit dict iteration order). Even though Python 3.7+ preserves dict insertion order, sorting is the load-bearing contract.
5. **Stable string formatting** — integer values formatted as `0x%02X` (uppercase, 2-digit) consistently. No `repr()` calls (which can be implementation-dependent).
6. **Banner format:** literal string, no version or hash interpolated (the catalog `version` field IS interpolated, but it's a stable integer in the catalog itself).
7. **UTF-8 encoding throughout** — both files written with `encoding='utf-8'`.

**Verification command (LCAT-05 quick test):**
```bash
python3 tools/catalog/codegen.py --catalog tools/catalog/messages.toml --target /tmp/messages.h --language cpp
python3 tools/catalog/codegen.py --catalog tools/catalog/messages.toml --target /tmp/messages.h.2 --language cpp
diff /tmp/messages.h /tmp/messages.h.2 && echo "BYTE-IDENTICAL ✓"
```

### `MSG_PARAM_COUNT(id)` Implementation Choice

**Recommendation:** **PROGMEM table** (256 bytes flat), accessed via `pgm_read_byte`.

| Implementation | Flash cost (AVR-GCC -Os) | RAM cost | Lookup speed | Verdict |
|----------------|--------------------------|----------|--------------|---------|
| `constexpr` lookup | Header-only; per-call expansion; possibly inlines into the call site → up to 256 bytes of constant emission per call site `[ASSUMED]` | 0 | O(1) | ✗ multiplies call-site emissions |
| Inline `switch` (52 cases) | ~250-400 bytes flash + 4 bytes per case branch | 0 | O(log n) typical | ✗ size grows with catalog |
| **PROGMEM table (256 bytes)** | **256 bytes flat** | 0 | O(1) `pgm_read_byte` ≈ 4 cycles | ✓ smallest + fastest |

**Why PROGMEM table wins for AVR:**

- AVR-GCC stores `PROGMEM` arrays in flash (Harvard architecture); no RAM cost.
- 256 bytes is constant regardless of catalog size — adding the 200th message doesn't grow the table.
- `pgm_read_byte` is a single LPM instruction (1 µs at 16 MHz) — fastest possible AVR flash access.
- Designated-initializer syntax (`[id] = bytes`) produces compact and readable generated code.
- The 256-byte cost vs 52 active entries (15.6 bytes per entry on average for `switch`/`constexpr`) means PROGMEM breaks even at ~30 entries and wins decisively from ~50 entries on. We're at 52 today; v2+ growth keeps the win bigger.

**Caveat (HONEST):** I have not benchmarked these three implementations on AVR-GCC -Os specifically for this codebase. The 256-byte fixed cost vs ~400 bytes for a 52-entry switch is the conventional AVR wisdom `[ASSUMED — based on AVR-GCC docs convention; not benchmarked in this session]`. The planner should add a verification task: "Compile firmware with each implementation; record flash deltas; pick the smallest." If switch turns out to be 200 bytes in practice (unlikely but possible), use that. Implementation effort is identical for the codegen — three template variants.

---

## Firmware `rurp_log_id` Design

### Declaration (in `rurp_shield.h`, sibling to `rurp_log`)

```cpp
// New v1.2 ID-encoded log emitter. Coexists with rurp_log / rurp_log_P in
// Phase 6 (LMIG-01 — both paths available; no call-site converts in this phase).
//
// id           — catalog ID (see messages.h)
// params       — pointer to raw param bytes, MSB-first per type
// param_count  — number of param bytes (NOT number of param fields)
//
// No-op when com_mode == false (serial pins in programmer mode).
// When SERIAL_DEBUG is set, also emits a hex-dump via debug serial.
void rurp_log_id(uint8_t id, const uint8_t* params, uint8_t param_count);
```

**Note on signature:** the prompt's exact LFW-01 wording is `rurp_log_id(uint8_t msg_id, const uint8_t* params, uint8_t param_count)`. Matching that verbatim. Callers must pre-pack the params buffer (the convenience macros below do this for typical cases).

### Implementation Layer (board-agnostic helper in `rurp_serial_utils.cpp`)

```cpp
// rurp_serial_utils.cpp — sibling to _firestarter_log_ram / _firestarter_log_progmem
//
// Emits a single ID-encoded frame to SERIAL_PORT.
// Frame layout:  0xAA 0x55 0xAA 0x55 | len | id | params... | crc8 | 0x0A
// where len = 1 (id) + param_count (params) + 1 (crc), excluding len + 0x0A.
//
// Caller must guarantee param_count matches MSG_PARAM_COUNT(id) — codegen
// asserts this via the LOG_* macros below at compile time where possible.

#include "rurp_shield.h"   // for SERIAL_PORT
#include "messages.h"

static const uint8_t MAGIC_PREAMBLE[4] PROGMEM = { 0xAA, 0x55, 0xAA, 0x55 };

// CCITT CRC-8 polynomial 0x07 table (PROGMEM, 256 bytes, generated once)
static const uint8_t CRC8_TABLE[256] PROGMEM = { /* ... 256 precomputed bytes ... */ };

static uint8_t crc8_ccitt(uint8_t crc, uint8_t b) {
    return pgm_read_byte(&CRC8_TABLE[crc ^ b]);
}

void _firestarter_emit_frame(uint8_t id, const uint8_t* params, uint8_t param_count) {
    // Magic preamble
    SERIAL_PORT.write(pgm_read_byte(&MAGIC_PREAMBLE[0]));
    SERIAL_PORT.write(pgm_read_byte(&MAGIC_PREAMBLE[1]));
    SERIAL_PORT.write(pgm_read_byte(&MAGIC_PREAMBLE[2]));
    SERIAL_PORT.write(pgm_read_byte(&MAGIC_PREAMBLE[3]));

    // Length = 1 (id) + param_count + 1 (crc)
    uint8_t len = (uint8_t)(1 + param_count + 1);
    SERIAL_PORT.write(len);

    // CRC8 over [id, params]
    uint8_t crc = 0;
    crc = crc8_ccitt(crc, id);

    // id
    SERIAL_PORT.write(id);

    // params
    for (uint8_t i = 0; i < param_count; i++) {
        uint8_t b = params[i];
        SERIAL_PORT.write(b);
        crc = crc8_ccitt(crc, b);
    }

    // crc + re-sync terminator
    SERIAL_PORT.write(crc);
    SERIAL_PORT.write(0x0A);
    SERIAL_PORT.flush();
}
```

### Board-Specific `rurp_log_id` (in `uno_rurp_shield.cpp` + `leonardo_rurp_shield.cpp`)

Mirrors the existing `rurp_log` discipline byte for byte:

```cpp
// uno_rurp_shield.cpp — add immediately after rurp_log_P()

void rurp_log_id(uint8_t id, const uint8_t* params, uint8_t param_count) {
    // SERIAL_DEBUG duplication — emit a hex-dump of the frame for human-readable
    // debugging. Mirrors the existing rurp_log_P "log_debug(type, msg)" path.
    #ifdef SERIAL_DEBUG
    {
        // Render "ID 0x%02x params (%d bytes): %02x %02x ..." into debug_msg_buffer.
        // Caller's response_msg buffer is NOT used (rurp_log_id avoids that buffer
        // by design — see "key insight" below).
        snprintf_P(debug_msg_buffer, RURP_DEBUG_BUF_SIZE,
                   PSTR("ID 0x%02x (%d bytes)"), id, param_count);
        log_debug(PSTR("LOG"), debug_msg_buffer);   // "LOG: ID 0x06 (4 bytes)"
        // Hex-dump body emitted as separate debug line for terseness.
    }
    #endif

    // com_mode gate — identical to rurp_log; no emission when serial pins are in
    // programmer mode (PORTD bit 0 driven as data bus during programming).
    if (com_mode) {
        _firestarter_emit_frame(id, params, param_count);
    }
}
```

For the Leonardo board: the existing `leonardo_rurp_shield.cpp` does NOT override `rurp_log` (it relies on the weak default in `rurp_serial_utils.cpp:113-117`). For symmetry, `rurp_log_id` similarly relies on a **weak default in `rurp_serial_utils.cpp`** that just calls `_firestarter_emit_frame` unconditionally (no `com_mode` gate — Leonardo doesn't switch pins for programming, since it has a separate USB-CDC bridge). The Uno strong override is the one that adds the `com_mode` gate. `[VERIFIED: leonardo board file has no rurp_log() override; it uses the weak default]`

### Convenience Macros (LFW-02)

In a new generated header `messages.h` OR a hand-written `logging_id.h`. The LFW-02 requirement says these must be "no more verbose than the current `log_info_const` / `log_error_format`". The current macros take a single-string argument; the new ones take an ID + zero-or-more params.

```cpp
// logging_id.h — hand-written, sibling to logging.h
// Macros pack params at the call site and dispatch to rurp_log_id.

#include "messages.h"
#include "rurp_shield.h"

// Zero-param case — emit ID + empty params
#define LOG_ID(id) \
    rurp_log_id((id), NULL, 0)

// 1-byte param (u8)
#define LOG_ID_U8(id, p1) \
    do { uint8_t _b[1] = { (uint8_t)(p1) }; rurp_log_id((id), _b, 1); } while (0)

// 2-byte param (u16, MSB-first on wire)
#define LOG_ID_U16(id, p1) \
    do { \
        uint8_t _b[2]; uint16_t _v = (uint16_t)(p1); \
        _b[0] = (uint8_t)(_v >> 8); _b[1] = (uint8_t)(_v & 0xFF); \
        rurp_log_id((id), _b, 2); \
    } while (0)

// 3-byte param (u24 — pack a 32-bit value's low 24 bits)
#define LOG_ID_U24(id, p1) \
    do { \
        uint8_t _b[3]; uint32_t _v = (uint32_t)(p1); \
        _b[0] = (uint8_t)(_v >> 16); _b[1] = (uint8_t)(_v >> 8); _b[2] = (uint8_t)(_v & 0xFF); \
        rurp_log_id((id), _b, 3); \
    } while (0)

// 4-byte param (u32)
#define LOG_ID_U32(id, p1) \
    do { \
        uint8_t _b[4]; uint32_t _v = (uint32_t)(p1); \
        _b[0] = (uint8_t)(_v >> 24); _b[1] = (uint8_t)(_v >> 16); \
        _b[2] = (uint8_t)(_v >> 8);  _b[3] = (uint8_t)(_v & 0xFF); \
        rurp_log_id((id), _b, 4); \
    } while (0)

// Multi-param composer for the handful of multi-arg call sites
// (e.g., MSG_ERR_WRITE_FAILED has u24+u8+u16 = 6 bytes)
#define LOG_ID_BYTES(id, buf_array, count) \
    rurp_log_id((id), (buf_array), (count))

// Verbosity-gated INFO (mirrors the FLAG_VERBOSE check in old log_info)
#define LOG_INFO_ID(id) \
    do { if (is_flag_set(FLAG_VERBOSE)) { LOG_ID(id); } } while (0)
#define LOG_INFO_ID_U8(id, p1) \
    do { if (is_flag_set(FLAG_VERBOSE)) { LOG_ID_U8((id), (p1)); } } while (0)
// ... etc
```

**Equivalence with old macros:**
- Old: `log_info_const("Main start")` → ~30 chars
- New: `LOG_INFO_ID(MSG_INFO_MAIN_START)` → ~32 chars ✓ no worse

- Old: `log_error_format("Failed to write memory, 0x%06x, retries: %d, bad bytes: %d", addr, r, b)` → ~80 chars + format-string lives in PROGMEM at the call site
- New: assemble params buffer + `rurp_log_id(MSG_ERR_WRITE_FAILED, buf, 6)` → ~3 short lines + zero PROGMEM string cost (the savings)

### Coexistence with `rurp_log` (LMIG-01)

Phase 6 changes NO call-sites. Both APIs are available in the same TU:

```cpp
// Old call-site (unchanged in Phase 6) — emits text on the wire
log_info_const("Main start");

// New call-site (will exist in Phase 7+ — illustrative only) — emits a binary frame
LOG_INFO_ID(MSG_INFO_MAIN_START);
```

Old `LOG_*_MSG` PROGMEM strings (in `logging.c`) stay. Old `rurp_log` / `rurp_log_P` weak defaults stay. Old `_firestarter_log_ram` / `_firestarter_log_progmem` stay. Phase 9 deletes them; Phase 6 just adds.

### Key Insight (Flash-Savings Mechanism)

The old `log_info_format("Memory size 0x%lx", handle->mem_size)` emits:
1. The PROGMEM format-string `"Memory size 0x%lx"` (~17 bytes flash, present per call-site).
2. A call to `sprintf_P` that renders into `handle->response_msg` (96-byte RAM buffer).
3. A call to `rurp_log` that emits the rendered string to serial.

The new `LOG_INFO_ID_U32(MSG_INFO_MEM_SIZE, handle->mem_size)`:
1. Zero PROGMEM string at the call site (the format-string moves to the host catalog).
2. Direct serial emission of 4 wire bytes (the param value).
3. **No `response_msg` round-trip** — the 96-byte RAM buffer can shrink in Phase 9 (or possibly be repurposed).

This is the primary flash-savings mechanism. The catalog is the new home of every English-language format-string; firmware just emits IDs and bytes.

---

## Host Decoder Design

### Always-On Byte-Stream Reader (replaces `_read_and_parse_lines`)

Replaces the loop in `serial_comm.py` ~line 213. Magic-scan + text-line fallback per CONTEXT.md §D-05.

```python
# serial_comm.py — new method, replaces _read_and_parse_lines body
# (the public signature stays the same: Generator[Response, None, None])

MAGIC_PREAMBLE = b'\xAA\x55\xAA\x55'

from firestarter.messages import CATALOG, SEVERITY_LABEL

# (alongside Response namedtuple — add LogMessage)
LogMessage = namedtuple('LogMessage', ['severity', 'text', 'id'])

def _read_and_parse_lines(self, timeout: float) -> Generator[Response, None, None]:
    """
    Always-on byte-stream reader. Per byte:
      - Append to accumulator.
      - If the last 4 bytes are MAGIC: dispatch any text preceding the magic
        (which may be empty), then consume a binary frame.
      - Else if the byte is 0x0A (newline): dispatch the accumulated text line.
      - Else: keep accumulating.
    Yields Response namedtuples for both text lines (unchanged from existing
    behaviour — uses _parse_response_line) and decoded ID frames (new — uses
    _decode_id_frame).
    """
    if not self.is_connected():
        raise SerialError("Not connected.")

    accumulator = bytearray()
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            chunk = self.connection.read(1)   # read 1 byte (timeout from serial.Serial)
        except serial.SerialException as e:
            raise SerialError(f"Serial error reading from {self.port_name}: {e}") from e

        if not chunk:
            # No data — yield control briefly, no timeout reset
            time.sleep(0.001)
            continue

        b = chunk[0]
        accumulator.append(b)

        # Check magic preamble (last 4 bytes of accumulator)
        if len(accumulator) >= 4 and bytes(accumulator[-4:]) == MAGIC_PREAMBLE:
            # Dispatch any preceding text (drop the 4 magic bytes themselves)
            preceding = bytes(accumulator[:-4])
            if preceding:
                response = self._parse_response_line(preceding)
                if response:
                    self._log_rurp_feedback(response)
                    yield response
                    start_time = time.time()
            accumulator.clear()

            # Read len byte
            len_bytes = self.connection.read(1)
            if not len_bytes:
                logger.warning("Magic seen but length byte not received — re-sync.")
                continue
            frame_len = len_bytes[0]

            # Read exactly frame_len bytes (id + params + crc), then the trailing 0x0A
            body = self.connection.read(frame_len)
            if len(body) != frame_len:
                logger.warning(f"Frame truncated: expected {frame_len}, got {len(body)} — re-sync.")
                continue
            terminator = self.connection.read(1)
            # Terminator may or may not be 0x0A; we don't require it (D-04).

            # Decode and yield
            decoded = self._decode_id_frame(frame_len, body)
            if decoded is not None:
                # Convert LogMessage → Response so existing call-sites work unchanged
                response = Response(type=decoded.severity, message=decoded.text)
                self._log_rurp_feedback(response)
                yield response
                start_time = time.time()
            continue

        # Text-line fallback: 0x0A terminates a line
        if b == 0x0A:
            line_bytes = bytes(accumulator)
            accumulator.clear()
            response = self._parse_response_line(line_bytes)
            if response:
                self._log_rurp_feedback(response)
                yield response
                start_time = time.time()

        # Else: keep accumulating
```

### Frame Decode + CRC Validation

```python
import struct

CRC8_CCITT_TABLE = bytes([
    # 256 precomputed bytes — poly 0x07, seed 0x00, no reflection, no final XOR
    # Generated once at module-import or as a constant in messages.py.
])

def _crc8_ccitt(data: bytes) -> int:
    crc = 0
    for byte in data:
        crc = CRC8_CCITT_TABLE[crc ^ byte]
    return crc

def _decode_id_frame(self, frame_len: int, body: bytes) -> Optional[LogMessage]:
    """
    body = [id, param_bytes..., crc].
    Returns LogMessage or None (on CRC failure / unknown ID / shape mismatch).
    """
    if frame_len < 2:
        logger.warning(f"Frame too short: len={frame_len}")
        return None

    msg_id = body[0]
    crc_received = body[-1]
    params_bytes = bytes(body[1:-1])

    # Validate CRC8 over [id, params]
    crc_expected = _crc8_ccitt(bytes([msg_id]) + params_bytes)
    if crc_expected != crc_received:
        logger.warning(f"CRC mismatch for ID 0x{msg_id:02x}: "
                       f"expected 0x{crc_expected:02x}, got 0x{crc_received:02x}")
        return None

    # Lookup catalog entry
    entry = CATALOG.get(msg_id)
    if entry is None:
        logger.warning(f"Unknown message ID 0x{msg_id:02x} — catalog out of date?")
        return None

    # Shape check
    if len(params_bytes) != entry.param_bytes:
        logger.warning(f"ID 0x{msg_id:02x} ({entry.name}): "
                       f"expected {entry.param_bytes} param bytes, got {len(params_bytes)}")
        return None

    # Decode params per type
    values = []
    cursor = 0
    for (ptype, prender) in entry.params:
        v, used = _decode_param(ptype, params_bytes, cursor)
        values.append(v)
        cursor += used

    # Render
    try:
        text = entry.format % tuple(values) if values else entry.format
    except (TypeError, ValueError) as e:
        logger.warning(f"Format failure for {entry.name}: {e}")
        text = f"<format-error: {entry.name}>"

    return LogMessage(severity=SEVERITY_LABEL[entry.severity], text=text, id=msg_id)


def _decode_param(ptype: str, buf: bytes, cursor: int) -> Tuple[any, int]:
    """Decode one param starting at buf[cursor]; return (value, bytes_consumed)."""
    if ptype == "u8":   return (buf[cursor], 1)
    if ptype == "i8":   return (struct.unpack_from(">b", buf, cursor)[0], 1)
    if ptype == "u16":  return (struct.unpack_from(">H", buf, cursor)[0], 2)
    if ptype == "i16":  return (struct.unpack_from(">h", buf, cursor)[0], 2)
    if ptype == "u24":
        b = buf[cursor:cursor+3]
        return ((b[0] << 16) | (b[1] << 8) | b[2], 3)
    if ptype == "u32":  return (struct.unpack_from(">I", buf, cursor)[0], 4)
    if ptype == "i32":  return (struct.unpack_from(">i", buf, cursor)[0], 4)
    if ptype == "ascii_str":
        n = buf[cursor]
        return (buf[cursor+1:cursor+1+n].decode("ascii", errors="replace"), 1 + n)
    raise ValueError(f"Unknown param type: {ptype}")
```

### Severity Routing (LHOST-03)

Existing `_log_rurp_feedback` (line 190-211) already routes `response.type` → `logger.error`/`warning`/`debug`. The decoder feeds the same `Response(type=..., message=...)` shape, so this routing works unchanged. The `LogMessage` namedtuple is an INTERNAL value within `_decode_id_frame` that gets translated to `Response` before yielding. **Net change to `_log_rurp_feedback`: zero.**

### `LogMessage` as a Public Surface

The LHOST-01 acceptance criterion requires a `LogMessage(severity, text)` yield. Recommendation: yield BOTH for API clarity:

```python
# At the top of serial_comm.py
LogMessage = namedtuple('LogMessage', ['severity', 'text', 'id'])

# Inside _decode_id_frame: return LogMessage
# Inside _read_and_parse_lines: yield Response(type=lm.severity, message=lm.text)
# Tests can directly call _decode_id_frame and assert on LogMessage.
```

This keeps the internal Response surface backwards-compatible for all existing call-sites (a Response is what `get_response`, `expect_ack`, etc. consume), while exposing `LogMessage` as the documented unit-test entry point for LHOST-01.

---

## Host FW-Version Refuse Guard (LFW-05 + LHOST-04)

### Location

Two integration points:
1. **`serial_comm.py:_probe_port` (line ~382-415)** — already does FW-version parsing during the initial OK handshake. Add a major-version refuse check here.
2. **`firmware.py:check_current_firmware` (line ~55-97)** — operator-facing CLI entry. The refuse error from `_probe_port` propagates as `FirmwareOutdatedError` and is caught in the CLI layer.

### Code Shape (in `_probe_port`)

```python
# serial_comm.py — replace the existing version check block (lines ~388-409)

if msg and "FW:" in msg:
    match = re.search(r"FW:\s*([\d.x]+)", msg)
    if match:
        current_version = match.group(1).strip()

        # NEW (Phase 6) — v1.2 major-version refuse guard.
        # Pre-v1.2 firmware emits text-format frames; the host is now
        # ID-frame-only by design (lockstep upgrade per PROJECT.md).
        try:
            major = int(current_version.split(".")[0])
        except (ValueError, IndexError):
            major = 0
        if major < 3:  # firmware bumps to 3.0.0 in Phase 9
            raise FirmwareOutdatedError(
                f"Firmware version {current_version} is pre-v1.2 (text-format logging). "
                f"This host expects v1.2+ firmware emitting ID-encoded log frames. "
                f"Please upgrade the firmware to v3.0.0 or later using "
                f"'firestarter fw --install'. (No fallback to text-format protocol — "
                f"the host and firmware must be upgraded together; see PROJECT.md "
                f"\"Constraints\".)"
            )

        # Existing 2.0.0 minimum check stays as a defence-in-depth lower bound.
        if not SerialCommunicator._is_version_sufficient(current_version, "2.0.0"):
            raise FirmwareOutdatedError(...)  # unchanged
```

**Note on v1.2 firmware version:** The firmware bumps from `2.0.11-dev` (current) → `3.0.0` in Phase 9 per LFW-05. Phase 6 wires the host-side guard expecting `major >= 3`. Until Phase 9 ships, the host running this Phase 6 code refuses to talk to ANY current firmware build. **This is acceptable for v1.2 development** because the lockstep contract says host + firmware upgrade together, and the development branch is gated on Phase 9 anyway. Phase 6 cannot land standalone in `main` of the host sub-repo without breaking the bench against unchanged firmware — the planner must include a `--allow-prerelease-firmware` env var or `pytest`-only verification path (recommendation below).

**Pragma:** Phase 6 plan adds a `FIRESTARTER_DEV_ALLOW_PRE_V12=1` env var that **only** allows the version check to skip the major-version assertion when set. This lets `firestarter_test.sh` continue running against text-format firmware until Phase 7+ flips call-sites. Documentation calls this out as a developer-only escape hatch; the env var is NOT documented for end users.

### Operator-Facing Error Message Wording

Exact text (above): `"Firmware version X.Y.Z is pre-v1.2 (text-format logging). This host expects v1.2+ firmware emitting ID-encoded log frames. Please upgrade the firmware to v3.0.0 or later using 'firestarter fw --install'. (No fallback to text-format protocol — the host and firmware must be upgraded together; see PROJECT.md \"Constraints\".)"`.

Rationale: tells the operator (a) what version they have, (b) why the host refuses, (c) the concrete remedy (`firestarter fw --install`), (d) why there's no fallback (lockstep is intentional). No surprise, no easter-egg behaviour.

### Unit-Test Harness

Phase 6 introduces a `firestarter_app/tests/test_fw_version_guard.py` (new test file — the host sub-repo currently has NO pytest infrastructure `[VERIFIED: find . -name 'test_*.py' → empty]`).

Phase 6 plan must also include adding `pytest` to `requirements.txt` (dev dependency) + a `[tool.pytest.ini_options]` section in `pyproject.toml` + a `tests/` directory at the host sub-repo root.

```python
# firestarter_app/tests/test_fw_version_guard.py

import pytest
from unittest.mock import MagicMock, patch
from firestarter.serial_comm import (
    SerialCommunicator,
    FirmwareOutdatedError,
)

class TestFirmwareVersionGuard:
    def test_refuse_pre_v3_firmware(self):
        """v2.x firmware (current text-format) must be refused."""
        mock_msg = "FW: 2.0.11, HW: Rev2, Cmd: 0x0d"
        # Drive _probe_port with a fake serial that returns this OK message.
        # Use unittest.mock to short-circuit SerialCommunicator construction.
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

    def test_accept_v3_firmware(self):
        mock_msg = "FW: 3.0.0, HW: Rev2, Cmd: 0x0d"
        # Same patch surface, should NOT raise FirmwareOutdatedError.
        ...

    def test_dev_escape_hatch_env_var(self, monkeypatch):
        monkeypatch.setenv("FIRESTARTER_DEV_ALLOW_PRE_V12", "1")
        mock_msg = "FW: 2.0.11, HW: Rev2, Cmd: 0x0d"
        # Should NOT raise — env var bypasses the major-version assertion.
        ...
```

Test framework: **pytest** (Python ecosystem default). Run via `pytest firestarter_app/tests/`. Phase 6 plan must add the framework setup as Wave 0.

---

## LHOST-01 Acceptance Fixture

Pytest-style fixture proving the decoder end-to-end without touching real serial hardware. Phase 6 success criterion #4 (ROADMAP.md): "Sending a hand-crafted ID-encoded log frame from a Python test fixture into `serial_comm.py` yields a `LogMessage(severity, text)` whose severity matches the catalog category and whose text matches the catalog format string rendered against the supplied param bytes."

```python
# firestarter_app/tests/test_id_frame_decoder.py

import io
import pytest
from firestarter.serial_comm import (
    SerialCommunicator,
    LogMessage,
    MAGIC_PREAMBLE,
)
from firestarter.messages import CATALOG, MSG_INFO_ADDR, MSG_ERR_WRITE_FAILED

def _crc8_ccitt(data: bytes) -> int:
    """Reference CRC8 — duplicates the implementation in messages.py for test
    isolation (don't import the production CRC; assert byte-for-byte equality
    against a known-good table-free recomputation)."""
    crc = 0
    for b in data:
        crc ^= b
        for _ in range(8):
            crc = ((crc << 1) ^ 0x07) & 0xFF if (crc & 0x80) else (crc << 1) & 0xFF
    return crc

def _build_frame(msg_id: int, params: bytes) -> bytes:
    """Hand-build a wire frame per CONTEXT.md §D-01."""
    body = bytes([msg_id]) + params
    crc = _crc8_ccitt(body)
    length = len(body) + 1   # +1 for crc
    return MAGIC_PREAMBLE + bytes([length]) + body + bytes([crc, 0x0A])


class TestIdFrameDecoder:

    def test_zero_param_frame_yields_logmessage(self):
        """MSG_OK_READY (id=0x01, no params) — minimal frame."""
        frame = _build_frame(0x01, b"")
        # Frame = AA 55 AA 55 | 02 | 01 | <crc> | 0A  (8 bytes)
        assert len(frame) == 8

        result = _decode_via_serial_comm(frame)
        assert isinstance(result, LogMessage)
        assert result.severity == "OK"
        assert result.text == "Ready"
        assert result.id == 0x01

    def test_u24_param_renders_as_hex6(self):
        """MSG_INFO_ADDR (id=0x56) with u24=0x01F4A2 — must render '0x01f4a2'."""
        params = bytes([0x01, 0xF4, 0xA2])  # u24 MSB-first
        frame = _build_frame(MSG_INFO_ADDR, params)
        result = _decode_via_serial_comm(frame)
        assert result.severity == "INFO"
        # format string is "Address: 0x%06x"  — note lowercase x
        assert result.text == "Address: 0x01f4a2"

    def test_multi_param_frame(self):
        """MSG_ERR_WRITE_FAILED (id=0xB1, u24+u8+u16) — multi-param decode."""
        params = bytes([0x01, 0x00, 0x00,        # u24 = 0x010000
                        0x05,                     # u8  = 5
                        0x00, 0x03])              # u16 = 3
        frame = _build_frame(MSG_ERR_WRITE_FAILED, params)
        result = _decode_via_serial_comm(frame)
        assert result.severity == "ERROR"
        assert result.text == "Failed to write memory, 0x010000, retries: 5, bad bytes: 3"

    def test_bad_crc_rejected(self):
        frame = _build_frame(0x01, b"")
        # Corrupt the CRC byte
        bad_frame = frame[:-2] + bytes([(frame[-2] ^ 0xFF)]) + frame[-1:]
        result = _decode_via_serial_comm(bad_frame)
        # CRC failure → no LogMessage yielded; the reader logs a warning and re-syncs
        assert result is None

    def test_unknown_id_rejected(self):
        # 0xFF is reserved-unallocated; catalog does NOT contain it
        frame = _build_frame(0xFF, b"")
        result = _decode_via_serial_comm(frame)
        assert result is None

    def test_text_line_passthrough(self):
        """Existing text line ('OK: foo\\n') must still parse via the rightmost-prefix
        regex fallback — preserves backward compatibility for the FW handshake."""
        line = b"OK: Ready\n"
        result = _decode_via_serial_comm(line)
        # Text-line fallback yields a Response (not LogMessage), but the type/message
        # surface is identical for the public API.
        # ... assertion details ...


# --- Test plumbing: feed bytes into the decoder via a BytesIO-shaped fake ---

class _FakeSerial:
    """Minimal serial.Serial shim: supports read(n) only."""
    def __init__(self, payload: bytes):
        self.buf = io.BytesIO(payload)
        self.is_open = True
        self.timeout = 0.01

    def read(self, n=1):
        return self.buf.read(n)

    @property
    def in_waiting(self):
        return len(self.buf.getvalue()) - self.buf.tell()

def _decode_via_serial_comm(payload: bytes):
    """Drives SerialCommunicator._read_and_parse_lines against an in-memory
    byte stream; returns the first LogMessage yielded or None."""
    comm = SerialCommunicator.__new__(SerialCommunicator)
    comm.port_name = "<fake>"
    comm.connection = _FakeSerial(payload)
    comm.timeout = 0.05
    for response in comm._read_and_parse_lines(timeout=0.1):
        # Yielded item is a Response — translate back to LogMessage for assertion
        # (or have _decode_id_frame return a LogMessage that the test grabs
        #  before the Response conversion).
        return response
    return None
```

**Key design choice:** The fixture builds frames using a reference CRC implementation (the bitwise loop above) and asserts the decoder accepts them. The reference is INDEPENDENT of the production table-driven implementation — this catches any off-by-one in the production code. The fixture is hermetic (no hardware, no subprocess, no network).

---

## CI Drift Gates

### `firestarter/.github/workflows/build.yml` Addition

Add **before** the existing `Install PlatformIO Core` step:

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

The `git diff --exit-code` fails with a visible diff in the PR if anyone edits the generated files without rerunning codegen (LCI-01 + LCI-03 + LCI-04).

### `firestarter_app/.github/workflows/release.yml` + `publish.yml` Addition

Add a new pre-job step (since these workflows currently don't compile/test, only release):

**Recommendation:** add a NEW workflow file `firestarter_app/.github/workflows/ci.yml`:

```yaml
name: CI
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  ci:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'

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
        run: pytest firestarter_app/tests/ -v
```

**Note:** the host sub-repo currently has NO CI workflow at all that actually tests the code (only publish/release on tag) `[VERIFIED: ls .github/workflows/]`. Phase 6 needs to add this. The planner should flag the addition as a Phase 6 sub-task.

### Meta-Repo Cross-Sub-Repo Diff Workflow (recommended)

If the meta-repo has its own CI, add a `.github/workflows/catalog-sync-check.yml` that asserts both vendored copies are byte-identical:

```yaml
name: Catalog sync check
on:
  schedule:
    - cron: '0 0 * * 1'   # weekly safety net
  workflow_dispatch:

jobs:
  sync-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Clone sub-repos
        run: |
          git clone --depth 1 https://github.com/henols/firestarter.git
          git clone --depth 1 https://github.com/henols/firestarter_app.git
      - name: Diff vendored catalogs
        run: |
          diff .planning/catalog/messages.toml firestarter/tools/catalog/messages.toml
          diff .planning/catalog/messages.toml firestarter_app/tools/catalog/messages.toml
```

This is belt-and-braces; the operational discipline of running `sync_to_subrepos.sh` and committing both sub-repos in the same logical change is the primary mechanism.

---

## PORTD Ghost-Byte Analysis

### Background

On the Uno, the ATmega328P's `PORTD` pins are the data bus AND the UART pins:
- `PD0` = UART RX = data bus bit 0
- `PD1` = UART TX = data bus bit 1
- `PD2..PD7` = data bus bits 2..7

During programming, the firmware switches `PORTD` to OUTPUT and drives bytes onto the bus. If the UART hardware is enabled while `PORTD` is being driven, the UART TX line emits whatever value PD1 takes; the receiver (host PC) sees this as a serial byte. The existing `rurp_set_programmer_mode()` (uno_rurp_shield.cpp:73-77) disables the UART via `rurp_serial_end()` before flipping PD0 to output, but **transitions** are still observable as fractional bytes if the UART finishes a TX in flight or if the host's USB-CDC bridge is mid-frame.

Worst-case ghost-byte patterns observed in the firmware's bench logs (from CONTEXT.md and existing comments in `uno_rurp_shield.cpp:47-69`):
- Long runs of similar values (e.g., `0xFF` during high-address writes) leaking as `0xFF` bytes.
- Pattern bytes that match printable ASCII (e.g., `0x4F` = 'O', `0x4B` = 'K') triggering false-positive prefix matches in the OLD text parser (mitigated by rightmost-prefix-wins).
- Single bytes during the moment of mode-switch transition.

### Why 4-Byte Magic + CRC8 Is Foolproof

**Pattern requirement for false-positive frame start:** `0xAA 0x55 0xAA 0x55` in sequence. On PORTD aliasing, the data bus values during programming are determined by the address and data being written. Statistical analysis:

| Property | 4-byte magic | False-positive probability |
|----------|--------------|----------------------------|
| Random bytes (uniform 0-255) | 4 specific bytes in sequence | `1 / 256^4 = 1/4.3B` per starting position |
| Address-line aliasing | Slowly-varying address-line transitions | **0** — address bytes vary by 1 between consecutive writes; ghost bytes cluster as `0x00 0x01 0x02 ...` or `0xFE 0xFF 0xFF 0xFE`. The pattern `0xAA 0x55 0xAA 0x55` requires the LSB to flip on every byte, which only happens at specific address transitions (e.g., 0xAAAA → 0x55AB on a carry). Even then, the second byte `0x55` requires the high address byte to also be at a specific value. The four-byte sequence is essentially impossible from sequential address writes. |
| Data-byte aliasing | Data being written to ROM | Also unlikely, since program data rarely contains repeated `0xAA 0x55 0xAA 0x55` sequences (this is binary instruction stream; specific to a chip). Even if it does, the next byte read (the `len`) must be a valid byte (≤24 in our schema) AND the byte AFTER `len` must be a known catalog ID AND the CRC8 must validate. |

**Defence-in-depth layers:**

1. **4-byte magic** — prefix anchor; `1/4.3B` random-collision rate before the `len`/`id`/`crc` further constrains.
2. **`len` byte sanity** — host validates `len <= 26` (1 id + 24 param-bytes + 1 crc). Anything larger → re-sync.
3. **`id` byte sanity** — host validates `id` is in the catalog. Unknown IDs → log warning, re-sync.
4. **CRC8 validation** — 1/256 chance of random CRC passing for a corrupt frame. Combined with the above, end-to-end false-positive rate is `~ 1/4.3B × 1/100 × 1/256 = 1 / 10^14`. For comparison, at 250000 baud emitting frames continuously for 100 years, the expected false-positive count is 0.

5. **Re-sync via `0x0A`** — even if all of the above somehow misalign, the next `0x0A` anchors recovery.

**Bit-patterns statistically impossible from PORTD aliasing:**
- Sustained alternating-bit transitions over 4 consecutive bytes. PORTD writes during programming are dominated by address-line monotonic counting (which produces runs of similar values).
- Specifically: `0xAA 0x55 0xAA 0x55` requires bit transitions `10101010 → 01010101 → 10101010 → 01010101`. This is the **maximum** Hamming distance between consecutive bytes (8 bit flips each). Address-line counting produces minimum-Hamming-distance sequences (1-2 bit flips per byte). The two patterns are statistical opposites.

### Why Not a Single-Byte Sentinel (Rejected per D-02)

| Sentinel | Aliasing risk |
|----------|---------------|
| `0xFF` | High-address writes during programming produce `0xFF` runs (the "all-1s" data line state during chip-deselect transitions). |
| `0x00` | Low-address writes produce `0x00` runs (chip-init state). |
| `0xAA` alone | PORTD bit-toggle patterns during `OUTPUT_ENABLE` register strobes can briefly hit `0xAA`. |
| `0xDE 0xAD` (2-byte) | Better — `1/65536` collision rate — but DEADBEEF-style sequences still appear in random ROM data; the 4-byte `0xAA 0x55 0xAA 0x55` is provably better against the specific PORTD aliasing class. |

Operator's design (CONTEXT.md §D-02) is the correct one. Research confirms.

---

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework (firmware) | PlatformIO Unity (`pio test -e native`) for C++ host-side; integration tests against bench hardware out of scope for Phase 6. |
| Framework (host) | pytest (NEW — not yet installed). Add to `requirements.txt` + `pyproject.toml`. |
| Config file (firmware) | `firestarter/platformio.ini` `[env:native]` — extant; expand to include a new `test/native/avr/test_messages/` suite. |
| Config file (host) | `firestarter_app/pyproject.toml` — add `[tool.pytest.ini_options]` section + `firestarter_app/tests/` dir. |
| Quick run (firmware) | `pio test -e native -f "*test_messages*"` |
| Full suite (firmware) | `pio test -e native` |
| Quick run (host) | `pytest firestarter_app/tests/test_id_frame_decoder.py -x` |
| Full suite (host) | `pytest firestarter_app/tests/ -v` |
| Catalog validation | `python3 tools/catalog/codegen.py --catalog tools/catalog/messages.toml --check` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| LCAT-01 | Catalog file exists with `{id, name, format, params}` schema | unit (codegen) | `python3 tools/catalog/codegen.py --check` | ❌ Wave 0 |
| LCAT-02 | Duplicate IDs / duplicate names / malformed shape / empty format all fail | unit | `python3 tools/catalog/codegen.py --catalog <fixture-with-violation> --check` (multiple fixtures) | ❌ Wave 0 |
| LCAT-03 | `messages.h` emitted contains expected enum + table | unit | `python3 tools/catalog/codegen.py … --target /tmp/m.h && grep MSG_OK_READY /tmp/m.h` | ❌ Wave 0 |
| LCAT-04 | `messages.py` emitted contains expected `CATALOG` dict | unit | `python3 tools/catalog/codegen.py … --target /tmp/m.py && python3 -c "from m import CATALOG; assert MSG_OK_READY in CATALOG"` | ❌ Wave 0 |
| LCAT-05 | Re-running codegen produces byte-identical output | unit | run codegen twice; `diff /tmp/m.h /tmp/m.h.2` | ❌ Wave 0 |
| LFW-01 | `rurp_log_id` is declared and links | unit (PIO) | `pio test -e native -f "*test_messages*"` — Unity test that calls `rurp_log_id(MSG_OK_READY, NULL, 0)` and inspects the captured `SERIAL_PORT.write` byte stream | ❌ Wave 0 |
| LFW-02 | Convenience macro `LOG_INFO_ID(MSG_INFO_MAIN_START)` expands cleanly | smoke (compile) | `pio run -e leonardo` (compiles a sentinel TU using each macro form) | ❌ Wave 0 |
| LFW-05 | `pio run -e leonardo` and `pio run -e uno` both compile with both APIs | smoke | `pio run -e leonardo && pio run -e uno` | ✓ existing |
| LHOST-01 | Hand-crafted frame → LogMessage yield | unit | `pytest firestarter_app/tests/test_id_frame_decoder.py -x` | ❌ Wave 0 |
| LHOST-02 | u24 renders as `0x{:06X}` etc. | unit | (part of LHOST-01 fixture; per-type assertions) | ❌ Wave 0 |
| LHOST-03 | Severity routing unchanged | unit | `pytest firestarter_app/tests/test_severity_routing.py` | ❌ Wave 0 |
| LHOST-04 | FW-version refuse raises FirmwareOutdatedError | unit | `pytest firestarter_app/tests/test_fw_version_guard.py` | ❌ Wave 0 |
| LCI-01 | Firmware CI rejects edited messages.h | smoke (CI dry-run) | manually edit messages.h, push branch, observe red build | ❌ Wave 0 (workflow add) |
| LCI-02 | Host CI rejects edited messages.py | smoke (CI dry-run) | as above | ❌ Wave 0 |
| LCI-03 | Both sub-repos run codegen pre-build | smoke | grep workflow YAMLs for the codegen step | ❌ Wave 0 |
| LCI-04 | Invalid catalog fails CI | smoke | introduce duplicate ID into catalog; push; observe red build | ❌ Wave 0 |
| LMIG-01 | No call-sites converted | grep | `grep -rE 'rurp_log_id|LOG_ID' firestarter/src/ firestarter/include/ | wc -l` should be 0 except in the new helper definition + macros themselves | (manual) |

### Sampling Rate

- **Per task commit:** `pytest firestarter_app/tests/ -x` + `pio test -e native -f "*test_messages*"`.
- **Per wave merge:** Full suite (`pytest firestarter_app/tests/ -v` + `pio test -e native`).
- **Phase gate:** Both full suites green, both sub-repo CIs green on push, `firestarter_test.sh` end-to-end against the current text-format firmware still passes (regression check — Phase 6 doesn't break the legacy bench path because no call-site converts).

### Wave 0 Gaps

Files that must be created before Phase 6 implementation tasks can run:

- [ ] `firestarter_app/tests/__init__.py` — pytest package marker
- [ ] `firestarter_app/tests/conftest.py` — shared fixtures (the `_FakeSerial` helper)
- [ ] `firestarter_app/tests/test_id_frame_decoder.py` — LHOST-01 fixture body
- [ ] `firestarter_app/tests/test_fw_version_guard.py` — LFW-05/LHOST-04 unit tests
- [ ] `firestarter_app/tests/test_severity_routing.py` — LHOST-03 unit tests
- [ ] `firestarter_app/tests/test_catalog_parse.py` — direct test of `tools/catalog/codegen.py --check` against fixture catalogs
- [ ] `firestarter_app/pyproject.toml` — add `[tool.pytest.ini_options]` section + dev dep on `pytest>=7`
- [ ] `firestarter_app/requirements.txt` — add `pytest>=7.0` to dev deps (or use `[project.optional-dependencies] dev`)
- [ ] `firestarter_app/.github/workflows/ci.yml` — new CI workflow (codegen + pytest)
- [ ] `firestarter/test/native/avr/test_messages/test_rurp_log_id.cpp` — Unity test exercising the firmware emitter against a mocked `SERIAL_PORT.write`
- [ ] `firestarter/test/native/avr/test_messages/host_stubs.cpp` — copy/adapt from `test_dispatch/host_stubs.cpp`
- [ ] `firestarter/test/native/avr/test_messages/avr/pgmspace.h` — copy from `test_dispatch/avr/pgmspace.h`

### Minimum Coverage for `messages.py` and `messages.h`

- **`messages.py`:** every catalog entry's `MessageDef` is instantiated correctly (verified by `import firestarter.messages` succeeding + `len(CATALOG) == 52` assertion + at least 1 representative entry per severity category asserted directly).
- **`messages.h`:** every catalog entry's `MSG_*` constant compiles (verified by including `messages.h` into the test TU + a static_assert per representative ID matching its decimal value). `MSG_PARAM_BYTES_TABLE[id]` matches the expected param byte count for at least one entry per param-type shape (`u8`, `u16`, `u24`, `u32`, mixed).

---

## Security Domain

`security_enforcement` is not explicitly set in `.planning/config.json` — treat as enabled. However, **the threat surface of Phase 6 is essentially zero**: the firmware-host communication is over a local USB serial link (no network), no user-supplied input is parsed by the firmware in Phase 6 (call-site conversions are Phases 7+), and no secrets are involved.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|------------------|
| V2 Authentication | no | — (local USB only) |
| V3 Session Management | no | — |
| V4 Access Control | no | — |
| V5 Input Validation | yes | Frame validation: 4-byte magic + length + CRC8 + catalog ID lookup (multi-layer). Host MUST reject frames with unknown IDs, mismatched param-byte counts, or CRC failures (covered above). |
| V6 Cryptography | no | CRC8 is a checksum, not a security primitive. Operator is aware (CONTEXT.md). Don't hand-roll any crypto. |

### Known Threat Patterns for {C++ AVR firmware + Python host over USB serial}

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Buffer overflow in firmware decoder | T (Tampering) | N/A — Phase 6's firmware path is emit-only, not decode. Decode is host-side; Python buffer slicing is bounds-checked. |
| Catalog drift between firmware + host (silent protocol corruption) | T | CI drift gate (`regen && git diff --exit-code`); cross-sub-repo catalog hash check; lockstep version bump (firmware major v3 + host refuse-guard). |
| Untrusted catalog content (someone editing `messages.toml` maliciously) | T | Code-review gating on PRs; no escalation path since the catalog only declares format strings and integer IDs (no executable content). |
| Unicode/encoding issues in format strings | T | Catalog declares English-only (PROJECT.md "Constraints"); validator rejects non-ASCII format strings. |

---

## Common Pitfalls

### Pitfall 1: Catalog re-numbering between Phase 6 → 7

**What goes wrong:** Someone re-shuffles IDs in `messages.toml` between Phase 6 (seeding) and Phase 7 (call-site conversion). The firmware emits ID `0x46` (was `MSG_INFO_FLAG_FORCE`, now reassigned to `MSG_INFO_FLAG_CAN_ERASE`) — host renders wrong text.

**Why it happens:** Lack of explicit "once allocated, never reassigned" rule.

**How to avoid:** Catalog header comment + codegen-time check: a new validation rule that asserts existing IDs are not reassigned compared to a `messages.toml.lock` file (a checked-in snapshot). The lock file updates only by additive PRs. **For Phase 6: add the rule + the initial lock file.**

**Warning signs:** Any PR that touches `messages.toml` and reduces the number of `[[messages]]` entries OR reassigns an existing `name → id` binding.

### Pitfall 2: Forgetting `com_mode` gate on `rurp_log_id`

**What goes wrong:** The Uno's PORTD pins are dual-purpose. If `rurp_log_id` emits during programming mode (when PORTD is being driven as a data bus), the SERIAL TX pin will collide with PD1 (data bit 1), producing corruption on both the wire AND the chip-write operation.

**Why it happens:** Easy to copy `rurp_log_id` declaration without copying the `com_mode` discipline. The existing `rurp_log` (uno_rurp_shield.cpp:80-85) sets the precedent — new code must mirror it.

**How to avoid:** Explicit comment in the Uno strong override (recommended above). Code review checklist item.

**Warning signs:** Any call to `rurp_log_id` from inside a `_write_data` / `_write_byte` / `_program_pulse` function in a handler (`eprom.cpp`, `flash_intel.cpp` et al.). These execute while PORTD is in OUTPUT mode.

### Pitfall 3: Wrong endianness on the wire

**What goes wrong:** `u24` rendered as little-endian or mixed-endian. Host decodes `0x010203` as `0x030201`.

**Why it happens:** AVR is little-endian; PROGMEM tables and stack values are LSB-first. Convenience macros must pack MSB-first explicitly.

**How to avoid:** Convenience macros in `logging_id.h` (above) explicitly shift bytes into MSB-first order. Host decoder uses `struct.unpack(">H", ...)` (`>` = big-endian) for all multi-byte types.

**Warning signs:** Test failures in LHOST-01 fixture where the expected param values are byte-swapped.

### Pitfall 4: Forgetting to update `MSG_PARAM_BYTES_TABLE` for new IDs

**What goes wrong:** Manual edits to `messages.h` slip through (no codegen run). Table is missing an entry. `MSG_PARAM_COUNT(new_id) = 0xFF` (the default fill) — firmware thinks the message has 255 params, sends garbage. Host CRC validation rejects.

**Why it happens:** Manual edit instead of catalog edit.

**How to avoid:** CI drift gate (`git diff --exit-code`). DO-NOT-EDIT banner at the top of every generated file.

**Warning signs:** PR that touches `messages.h` or `messages.py` directly without touching `messages.toml`.

### Pitfall 5: Test scripts in `firestarter_test.sh` / `write_test.sh` break against Phase 6

**What goes wrong:** Bench integration tests run host against firmware. If the host adds the FW-version refuse guard expecting v3.x but the bench firmware is still v2.x, ALL bench tests fail immediately on connect.

**Why it happens:** The lockstep design (PROJECT.md). Phase 6 lands the host guard before Phase 9 bumps the firmware version.

**How to avoid:** The `FIRESTARTER_DEV_ALLOW_PRE_V12=1` env var escape hatch (above). Document it in the Phase 6 plan + Phase 7+ planner notes.

**Warning signs:** First `firestarter_test.sh` run after merging Phase 6 fails on every command with `FirmwareOutdatedError`.

---

## Risks + Landmines

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| **`FIRESTARTER_DEV_ALLOW_PRE_V12` env var leaks into prod usage** | LOW | MEDIUM (silent old-firmware behaviour) | Log a `logger.warning` whenever the env var is honored; document as dev-only; remove the env var honoring in Phase 9 once the firmware bump is in place. |
| **Cross-sub-repo catalog drift (the two `messages.toml` copies diverge)** | MEDIUM | HIGH (silent protocol corruption) | The meta-repo `catalog-sync-check` workflow + the sync script discipline; both CIs check their own catalog against the meta-repo via SHA-256 hash embedded in `[catalog]` table (recommended addition). |
| **PyYAML accidentally introduced as a dependency** | LOW | MEDIUM (CI install steps slow + breaks lockstep) | Codegen uses ONLY `tomllib` (stdlib). Plan must call this out. |
| **AVR-GCC version difference causes generated `messages.c` to fail compile** | LOW | HIGH (no build) | Designated-initializer syntax is C99; AVR-GCC has supported it for >15 years. `pio test -e native` covers the cross-compile. |
| **Codegen idempotence violation slips through** | LOW-MED | MEDIUM (CI red until fixed) | LCAT-05 explicit unit test that runs codegen twice and diffs the output. |
| **Existing bench tests break against text-format firmware after Phase 6** | HIGH | MEDIUM (bench unavailable) | Env-var escape hatch (above). |
| **Phase 6's catalog seeding is wrong for some entries (param types, format strings)** | MEDIUM | LOW-MED (Phase 7 catches it via call-site conversion) | Phase 7's call-site conversion task is the canonical reconciliation. Phase 6's catalog is "draft authoritative"; Phase 7 corrects on encounter. |
| **`response_msg` dispatch sites in `operation_utils.cpp` don't fit the ID model cleanly** | MEDIUM | LOW (Phase 7 problem) | Phase 6 catalog seeds only the populate-site format strings; Phase 7 refactors the dispatch indirection. Flagged above. |
| **CRC8 polynomial confusion (0x07 vs 0x07-reflected vs 0xE0)** | MEDIUM | HIGH (wire incompatibility) | LHOST-01 fixture computes CRC via independent reference implementation; production code uses table-driven. Mismatch → test failure. |
| **Catalog seeding underestimates entries (some hidden `log_*` call I missed)** | LOW | LOW (Phase 7 adds them; phase 6 still ships) | Phase 7 conversion is the canonical sweep; planner adds a Phase 7 acceptance criterion "grep for any remaining `log_*` macros returns 0" which catches my omissions. |
| **AT mega328P / Leonardo flash budget regression in Phase 6** | LOW | MEDIUM (Leonardo at 98.7%) | The new code in Phase 6 is additive (`rurp_log_id`, `_firestarter_emit_frame`, 256-byte CRC8 table, 256-byte `MSG_PARAM_BYTES_TABLE`, ~52 ID constants). Estimated flash cost: **~600-900 bytes**. Leonardo at 98.7% leaves ~520 bytes free — Phase 6 likely tips over 100%. **MITIGATION:** Phase 6 measures flash impact and may need to defer the CRC table to Phase 7 by including it conditionally (e.g., gated by a `LOG_ID_EMITTER_ENABLED` define that flips on in Phase 7). Plan must include the flash-impact measurement task. |

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | `MSG_WARN_VPP_LOW` format params are `[u16, u16, u16, u16]` (four `%u.%u` slots = 2 voltage pairs × 2 ints each) | Inventory | LOW — Phase 7 reconciles at conversion time |
| A2 | `MSG_PARAM_COUNT` PROGMEM-table impl is the smallest-flash option for AVR (vs switch / constexpr) | `MSG_PARAM_COUNT` Implementation | MEDIUM — planner should add a benchmark task; if switch wins, ~150 bytes flash difference but easy switch in codegen |
| A3 | The 4-byte magic preamble + CRC8 false-positive rate against PORTD aliasing is `~1/10^14` | PORTD Ghost-Byte Analysis | LOW — operator already validated the design qualitatively |
| A4 | Flash cost of Phase 6's additive code is ~600-900 bytes on Leonardo | Risks | MED — measure during execution; if it tips Leonardo over 100%, the planner needs a deferred-CRC-table strategy |
| A5 | Designated-initializer syntax (`[id] = value`) compiles cleanly under AVR-GCC -Os without bloat | `MSG_PARAM_COUNT` Implementation | LOW — long-standing AVR-GCC feature; will be validated at codegen + first `pio run` |
| A6 | All 17 phase requirements are covered by the design above (no requirement is ONLY a verification artifact with no implementation surface) | Phase Requirements table | LOW — explicit requirement-to-section mapping above |
| A7 | The host's existing rightmost-prefix regex (`serial_comm.py:182`) correctly handles the FW handshake `OK: FW: ...` text frame after the byte-stream reader is in place | Host Decoder Design | LOW — the text-line fallback path is byte-identical to the existing path; only the read loop wrapper changes |
| A8 | The 52-entry catalog seed enumerates EVERY active log call-site (62 raw → 52 unique after dedup) | Inventory | MEDIUM — I de-duplicated by exact format-string match; one site might emit a slightly-different format string that I treated as identical. Phase 7 conversion catches any gap. |
| A9 | `pytest` is the correct host-side test framework (no prior precedent in `firestarter_app/`) | Validation Architecture | LOW — pytest is the Python ecosystem default; alternatives (unittest, nose) would also work but pytest's fixture model is the cleanest |
| A10 | `ascii_str` param wire encoding is `1 length byte + N data bytes` with max N=31 | Param Shape + Render Hints | LOW — this is the simplest encoding; the only call-site that uses `ascii_str` today is `MSG_INFO_REG_HEADER` / `MSG_DATA_VOLTAGE` (short labels: "VPP", "VPE", register names). 31 bytes is plenty. |

---

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|-------------|-----------|---------|----------|
| Python 3 | Codegen + host runtime | ✓ | 3.12.13 | — |
| `tomllib` (stdlib) | Catalog parsing | ✓ | stdlib (Py ≥3.11) | If targeting Py 3.10, add `tomli` to dev deps |
| PyYAML | (not chosen) | ✗ | — | TOML chosen instead — no fallback needed |
| `pytest` | Host unit tests | ✗ | — | Add to dev requirements + `pyproject.toml`; install via `pip install pytest>=7` |
| PlatformIO Core | Firmware build + Unity tests | ✓ | 6.1.19 | — |
| `gh` CLI | (CI workflow auth) | ✗ on this machine | — | GitHub Actions runners have it preinstalled; not needed for local dev |
| AVR-GCC toolchain | Firmware build | ✓ (via PlatformIO) | (managed by PIO) | — |
| `serial.tools.list_ports` (pyserial) | Host serial enumeration | ✓ (in `firestarter_app/requirements.txt`) | ≥3.5 | — |
| `git diff --exit-code` | CI drift gate | ✓ (git standard) | — | — |

**Missing dependencies with no fallback:** None — `pytest` is a straightforward add.

**Missing dependencies with fallback:** None.

---

## Sources

### Primary (HIGH confidence)
- Read tool against `firestarter/include/logging.h` — full macro inventory.
- Read tool against `firestarter/src/logging.c` — eight `LOG_*_MSG` PROGMEM strings.
- Read tool against `firestarter/src/boards/uno_rurp_shield.cpp` — `rurp_log` Uno implementation (com_mode gate + SERIAL_DEBUG duplication).
- Read tool against `firestarter/src/boards/rurp_serial_utils.cpp` — `_firestarter_log_ram` / `_firestarter_log_progmem` weak defaults + `rurp_communication_write` precedent for binary wire write.
- Read tool against `firestarter/include/rurp_shield.h` + `rurp_serial_utils.h` — function declaration surface.
- Read tool against `firestarter_app/firestarter/serial_comm.py` (full, 250 lines + 250-end) — existing read loop + `_parse_response_line` rightmost-prefix discipline + `_probe_port` fw-version handling.
- Read tool against `firestarter_app/firestarter/firmware.py` (150 lines) — `check_current_firmware` entry point.
- Grep results in `/tmp/logsites.txt` — 84 raw log call-sites across firmware (`firestarter/src/`, `firestarter/include/`).
- Bash probe: `python3 -c "import tomllib"` (success), `python3 -c "import yaml"` (fail) — environment availability.
- Read tool against `firestarter/.github/workflows/build.yml` + `firestarter_app/.github/workflows/{publish,release}.yml` — current CI shape.
- Read tool against `firestarter/CLAUDE.md` + `firestarter_app/CLAUDE.md` + `/workspaces/firestarter_prom/CLAUDE.md` — project conventions.

### Secondary (MEDIUM confidence)
- AVR-GCC PROGMEM + designated-initializer conventions `[ASSUMED: based on long-standing AVR-GCC behaviour; not benchmarked in this session]`.
- CRC8 CCITT polynomial 0x07 algorithm `[CITED: standard CRC-8/CCITT reference; verified via the reference bitwise loop in the LHOST-01 fixture]`.
- PORTD aliasing pattern statistics `[ASSUMED: based on observed firmware bench logs referenced in CONTEXT.md and existing comments in uno_rurp_shield.cpp; not measured in this session]`.

### Tertiary (LOW confidence)
- Flash-cost estimate of ~600-900 bytes for Phase 6's additive code `[ASSUMED — Phase 6 plan must measure on first `pio run -e leonardo` and adjust if the estimate is wrong; this is risk A4]`.

---

## Metadata

**Confidence breakdown:**
- Standard stack (TOML + tomllib + Python stdlib + pytest): **HIGH** — verified env probe + Python ecosystem default + zero-dep design.
- Wire frame mechanics (CRC8, byte layout, frame emit/decode): **HIGH** — operator-locked in CONTEXT.md; algorithm verified.
- Existing-code inventory + catalog seed: **HIGH** — verified by grep + read of every source file.
- Codegen idempotence guarantees: **HIGH** — Python's `sorted()` + LF newlines + tomllib's deterministic parse are documented behaviour.
- AVR flash impact for `MSG_PARAM_COUNT` choice: **MEDIUM** — qualitative analysis; planner should benchmark.
- Phase 6 flash budget vs Leonardo's 98.7% baseline: **MEDIUM-LOW** — A4 in Assumptions Log; must measure.
- PORTD ghost-byte probabilistic analysis: **MEDIUM** — argument by Hamming distance + statistical bounds; operator's qualitative design is the load-bearing claim.
- LHOST-01 fixture design: **HIGH** — pure Python; no hardware dependencies; reference CRC implementation is independent.

**Research date:** 2026-05-18
**Valid until:** 2026-06-17 (30 days — stable embedded protocol + Python ecosystem; revisit if AVR-GCC version bumps or PlatformIO ships breaking changes).
