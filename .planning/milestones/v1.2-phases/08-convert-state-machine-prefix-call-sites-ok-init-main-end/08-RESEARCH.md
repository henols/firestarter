# Phase 8: Convert State-Machine Prefix Call-Sites (OK/INIT/MAIN/END) — Research

**Researched:** 2026-05-18
**Domain:** Embedded serial protocol migration — firmware C++ (AVR/Arduino) + host Python; binary framing, catalog codegen, SRAM struct refactor, debug sub-ID channel
**Confidence:** HIGH (all findings verified against live source files in both sub-repos)

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Wire format for state-machine acks**
- W-01: Pure ID-frame, no text prefix. `OK:` / `INIT:` / `MAIN:` / `END:` literal prefixes removed from the wire. Host prefix-line matching for these severities deleted; only `_decode_id_frame` remains for state-machine acks.
- W-02: Host distinguishes ack frames from log frames via catalog severity-band lookup (OK 0x00–0x0F, INIT 0x10–0x1F, MAIN 0x20–0x2F, END 0x30–0x3F, INFO 0x40–0x7F, WARN 0x80–0x9F, ERROR 0xA0–0xDF, DATA 0xE0–0xFF). `expect_ack()` filters by severity band.
- W-03: Both DATA-class log lines AND chip-read streaming convert in Phase 8. DATA-class logs (VPP/VPE/SENDING) become pure ID frames; chip-read streaming gets MAGIC-wrapped framing — see W-04. The current `DATA:` text prefix is removed everywhere.
- W-04: Chip-read streaming wraps each chunk inside a single MAGIC_PREAMBLE-prefixed ID frame (`MSG_DATA_CHUNK` catalog entry). Because the existing 1-byte `len` field caps params at 253 B and current buffers are 512 B (Uno/Leonardo both set to 512 per platformio.ini), **the wire-format `len` field widens from u8 to u16** (big-endian). This is a wire-format major-version bump — firmware and host must change together. Single localized change in `_firestarter_emit_frame` (firmware) and `_read_and_parse_lines` / `_decode_id_frame` (host).

**`_check_response` buffer deconstruction**
- R-01: Delete `response_msg[96]` from `firestarter_handle_t`. SRAM win: ~96 B per operation invocation.
- R-02: Populate-sites use two-line pattern locked in Phase 7 D-02: `LOG_*_ID_*(MSG_*, args); handle->response_code = RESPONSE_CODE_*;`
- R-03: `_check_response` minimal strip: drop `log_info(handle->response_msg)` at `operation_utils.cpp:320` and `log_data(handle->response_msg)` at `operation_utils.cpp:325`. Keep `rurp_communication_write(handle->data_buffer, handle->data_size)` in the DATA case. Keep `return false` in the ERROR case. Keep `op_reset_timeout()` and `handle->response_code = RESPONSE_CODE_OK` at the bottom.

**OK_REV / OK_CFG / FW_VERSION / FW_HANDSHAKE payload shape**
- P-01: `MSG_OK_FW_VERSION` (0x03) uses `ascii_str` as the single param.
- P-02: `MSG_OK_REV` (0x04) becomes fixed-shape: `u8 physical + u8 effective`. `effective = 0xFF` means no override.
- P-03: `MSG_OK_CFG` (0x05) becomes fixed-shape: `u32 r1 + u32 r2 + u8 override`. `override = 0xFF` means no override. 9 wire bytes fixed.
- P-04: `MSG_OK_FW_HANDSHAKE` (0x06) becomes composite: `u8 hw + u8 cmd + ascii_str fw_version`. Replaces both branches at `firestarter.cpp:150` and `:153`. When `HARDWARE_REVISION` is undefined, emit `hw = 0xFF`.
- VPP/VPE: `log_data_format(...)` at `hardware_operations.cpp:67-69` splits into two new DATA-class IDs: `MSG_DATA_VPP_VOLTAGE` and `MSG_DATA_VPE_VOLTAGE`, each `u16 voltage_mv + u16 vcc_mv` (4 wire bytes).

**debug() conversion via MSG_DEBUG + sub_id**
- B-01: Convert 34+ firmware `debug()` / `debug_format()` call-sites in Phase 8. Single main catalog entry `MSG_DEBUG`; sub_id namespace identifies each specific message. Production-stripped via `#ifdef SERIAL_DEBUG`.
- B-02: sub_id width = `u8` (256-entry namespace). Currently ~46 debug strings found in the codebase (exceeds the 34 cited in the CONTEXT, see Pitfalls).
- B-03: Debug-strings table lives inline in `tools/catalog/messages.toml` under a `[debug]` section. Codegen.py extends to emit `DBG_*` constants + `DEBUG_CATALOG` dict.
- B-04: Sub_id entries declare params just like main messages. Wire frame: `<MAGIC> <len_u16> MSG_DEBUG sub_id [params] <crc> <term>`.

### Claude's Discretion
- Commit cadence for the cutover
- Native test impact (test_messages Unity suite update timing)
- Host parser refactor depth
- Debug conversion ordering (single-sweep vs piecewise)
- `copy_to_buffer` helper fate

### Deferred Ideas (OUT OF SCOPE)
- Firmware major-version bump to 3.0.0 (Phase 9)
- Deletion of legacy `logging.h` macro tower (Phase 9 / LFW-03/04)
- Final Leonardo flash measurement vs Phase 6 baseline (Phase 9)
- Host CLI rendering of decoded debug frames (Phase 8 plan or Phase 9 polish)
- Wire-format minor-version negotiation
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| LMIG-03 | Phase C (state-machine prefix conversion): `OK:` / `INIT:` / `MAIN:` / `END:` call-sites are converted. Host parser switches from line-prefix matching to ID-frame decoding for state-machine acks. `DATA:` prefix marker remains as literal text (gates the host's binary read loop and is not changed in v1.2). | W-01/W-02/W-03/W-04 firmware changes + R-01/R-02/R-03 SRAM cleanup + P-01..P-04 payload shapes + B-01..B-04 debug channel + host parser surgical removal |
</phase_requirements>

---

## Summary

Phase 8 is the largest structural shift in the v1.2 migration. Phase 7 converted all ERROR/WARN/INFO call-sites; Phase 8 eliminates the remaining text-format surfaces: state-machine acks (OK/INIT/MAIN/END), DATA-class log lines (VPP/VPE/SENDING/PROGRESS), chip-read binary streaming, and the debug() channel. After Phase 8, the firmware emits zero text to the serial port in production mode — every byte is either a binary ID frame or a MAGIC-wrapped `MSG_DATA_CHUNK` envelope.

The dominant technical complexity is **W-04: the `len` field widening from u8 to u16**. This is a coordinated breaking change across `_firestarter_emit_frame` (firmware), `_read_and_parse_lines` and `_decode_id_frame` (host), `test_messages` Unity assertions, and `test_decoder.py`. It must land as an atomic firmware+host commit with `test_messages` updated in the same commit. All other changes are evolutionary extensions of the Phase 6/7 patterns.

The **SRAM win from R-01** (deleting `response_msg[96]`) is independent and substantial: ~96 bytes recovered from the RAM-critical Uno (2 KB total, currently 77.5% used per Phase 7 measurement). The buffer deletion commits after all populate-sites are converted, ensuring no dangling reference.

The **catalog additions** are the prerequisite for all call-site conversions, exactly mirroring Phase 7's catalog-first (Wave 1) → call-site conversion (Wave 2+) ordering.

**Primary recommendation:** Execute in six commit groups — (1) catalog additions + codegen sub_id support, (2) wire-format `len` u8→u16 with `test_messages` update (firmware+host atomic), (3) new macro families in `logging_id.h`, (4) per-file call-site conversions (firmware-side), (5) `_check_response` strip + `response_msg` deletion + `copy_to_buffer` deletion, (6) `debug()` single-sweep conversion.

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Wire-frame emission (ID frame) | Firmware (AVR) | — | `_firestarter_emit_frame` in `rurp_serial_utils.cpp` owns the byte layout |
| Wire-frame `len` widening (u8→u16) | Firmware + Host coordinated | Native test suite | Single function firmware-side; single read-site host-side; test must update atomically |
| Catalog additions (VPP/VPE/CHUNK/DEBUG/shape changes) | Meta-repo tool | Both sub-repos (codegen sync) | `tools/catalog/messages.toml` is authoritative; `sync_to_subrepos.sh` distributes |
| Codegen extension (DBG_* + DEBUG_CATALOG) | Meta-repo tool | Both sub-repos | `tools/catalog/codegen.py` extended; same drift-gate CI covers new output |
| OK/INIT/MAIN/END call-site conversion | Firmware API layer | `logging_id.h` macros | New `LOG_OK_ID_*` / `LOG_INIT_ID_*` / `LOG_MAIN_ID_*` / `LOG_END_ID_*` / `LOG_DATA_ID_*` / `LOG_DEBUG_ID_*` families alias down to the existing `LOG_ID_*` primitives |
| `response_msg` buffer deletion | Firmware struct (`firestarter.h`) | All populate-sites | R-01 commits last; all sites must be clear first |
| Host prefix-matching deletion | Host Python (`serial_comm.py`) | — | `EXPECTED_PREFIXES` / `STATE_MACHINE_PREFIXES` / `_parse_response_line` minimal surgery |
| `expect_ack()` severity-band dispatch | Host Python (`serial_comm.py`) | — | Already routes by `response.type`; catalog severity-band ensures correct routing |
| Debug channel (MSG_DEBUG + sub_id) | Firmware `#ifdef SERIAL_DEBUG` | Host `DEBUG_CATALOG` | Production wire unaffected; host side optional rendering |
| Chip-read streaming (MSG_DATA_CHUNK) | Firmware `eprom_operations.cpp` | Host reader | Replaces `DATA:` text prefix + raw bytes pattern |
| Flash/SRAM measurement | Both boards (hardware) | — | Phase 8 close deliverable (not Phase 9 target, but delta record) |

---

## Standard Stack

### Core (unchanged from Phase 7 — all already in place)
| Library / Tool | Version | Purpose | Notes |
|----------------|---------|---------|-------|
| PlatformIO | 6.x | Firmware build + test orchestration | `pio run -e uno/leonardo/native` |
| ArduinoFake | 0.4.0 | Mock `Serial` in `[env:native]` test binary | Provides `OverloadedMethod(ArduinoFake(Serial), write, ...)` |
| Unity | bundled | C firmware unit test framework | `test_messages` + `test_dispatch` suites |
| Python 3.12 | 3.12 | Host CLI + codegen | `tomllib` (stdlib since 3.11) for TOML parsing |
| pytest | 9.0.3 | Host decoder regression suite | `tests/test_decoder.py` |
| pyserial | — | Serial I/O | `serial.Serial`, `serial.read(1)` byte-at-a-time loop |

### Key Files (Phase 8 modification targets — verified existence)
| File | Current State | Phase 8 Action |
|------|--------------|----------------|
| `tools/catalog/messages.toml` | 68 entries (1 sentinel + 7 OK + 1 INIT + 1 MAIN + 1 END + 3 DATA + 26 INFO + 5 WARN + 24 ERROR) | Add VPP_VOLTAGE / VPE_VOLTAGE / DATA_CHUNK IDs; reshape OK_REV (0x04) / OK_CFG (0x05) / OK_FW_HANDSHAKE (0x06); add `[debug]` section |
| `tools/catalog/codegen.py` | Emits `--language cpp` (messages.h) and `--language python` (messages.py) | Extend to emit `DBG_*` defines + `DEBUG_CATALOG` dict for `[debug]` section |
| `firestarter/include/logging_id.h` | Has `LOG_ID_*` primitives + `LOG_INFO_ID_*` / `LOG_ERROR_ID_*` / `LOG_WARN_ID_*` | Add `LOG_OK_ID_*` / `LOG_INIT_ID_*` / `LOG_MAIN_ID_*` / `LOG_END_ID_*` / `LOG_DATA_ID_*` / `LOG_DEBUG_ID_*` families |
| `firestarter/src/boards/rurp_serial_utils.cpp:173` | `uint8_t len = (uint8_t)(1 + param_count + 1);` / `SERIAL_PORT.write(len);` | Widen to u16: `uint16_t len_u16 = (uint16_t)(2 + param_count + 1);` / write MSB then LSB |
| `firestarter/include/firestarter.h:21,79` | `#define RESPONSE_MSG_SIZE 96` / `char response_msg[RESPONSE_MSG_SIZE];` | Delete both after all populate-sites cleared |
| `firestarter/src/operation_utils.cpp:300,320,325` | Buffer clear + `log_info(handle->response_msg)` + `log_data(handle->response_msg)` | R-01 clears go away with field; R-03 drops the two log lines |
| `firestarter_app/firestarter/serial_comm.py:451-464` | Reads 1-byte `frame_len` | Widen to read 2 bytes big-endian |
| `firestarter_app/firestarter/serial_comm.py:299-389` | `_decode_id_frame(frame_len: int, body: bytes)` | Unchanged signature; only the caller changes `frame_len` to be u16-derived |
| `firestarter_app/firestarter/serial_comm.py:123-147` | `EXPECTED_PREFIXES` list includes `"MAIN"`, `"INIT"`, `"END"` / `STATE_MACHINE_PREFIXES` list / `PREFIX_REGEX` | Remove `"MAIN"` / `"INIT"` / `"END"` from `EXPECTED_PREFIXES`, remove or empty `STATE_MACHINE_PREFIXES`; keep `"OK"` / `"DATA"` until both are converted below |
| `firestarter/test/native/avr/test_messages/test_rurp_log_id.cpp` | Asserts `len = 1 + param_count + 1` as 1 byte at `captured[4]` | Update all assertions: magic still 4 bytes; `len` now occupies bytes 4–5 (u16 big-endian); id moves to byte 6; frame body shifts by 1 byte throughout |
| `firestarter_app/tests/test_decoder.py` | Tests `build_frame` which computes `len = len(body) + 1` as 1 byte | Update `build_frame` in `conftest.py` and all frame-length computations to u16 |

---

## Architecture Patterns

### System Architecture Diagram

```
[Host Python CLI]                    [Arduino Firmware]
      |                                      |
      | JSON command (text, 250k baud) -->   |
      |                               init_programmer()
      |                               parse_json()
      | <-- MSG_OK_FW_HANDSHAKE (ID frame) --| send_ack_format() → LOG_OK_ID_U8_U8_ASTR()
      |
 _probe_port() parses "FW:" from text          send_main_done() → LOG_MAIN_ID()
  (bootstrap path — stays text per LFW-05)    send_init_done() → LOG_INIT_ID()
      |                                        send_end_done() → LOG_END_ID()
      |  <-- INIT/MAIN/END ID frames -------   |
      |  (severity-band dispatch in            |
      |   expect_ack / get_response)           |
      |                                        |
      |  <-- MSG_OK_READY (ID frame, 0x01) --  | send_ack_const("Ready") → LOG_OK_ID()
      |  <-- MSG_OK_REQ_DATA (0x02) ---------  | send_ack_const("Req data") → LOG_OK_ID()
      |  <-- MSG_DATA_CHUNK (u16-len frame) --  | raw chip bytes wrapped in ID envelope
      |  <-- MSG_DATA_PROGRESS (ID frame) ---   | firestarter_data_response_format() → LOG_DATA_ID_U32_U32()
      |  <-- MSG_DATA_VPP_VOLTAGE (ID frame) -  | log_data_format("VPP...") → LOG_DATA_ID_U16_U16()
      |  <-- MSG_DATA_VPE_VOLTAGE (ID frame) -  | log_data_format("VPE...") → LOG_DATA_ID_U16_U16()
      |  <-- MSG_DATA_SENDING (ID frame) -----  | log_data_const("Sending data") → LOG_DATA_ID()
      |
  _read_and_parse_lines() byte-stream loop:
    magic preamble → read u16 len → read body → _decode_id_frame()
    0x0A → text line (only FW-version bootstrap survives)
      |
  _decode_id_frame() → CATALOG lookup → severity-band → Response(type, message)
```

### Recommended Commit Group Structure

Based on the Phase 7 per-file commit pattern and Phase 8's larger semantic shifts, six commit groups are recommended. Within each group, multiple files may land in one commit when they form an atomic unit (e.g., `len` widening must be firmware+host+native test together):

**Group 1 — Catalog + codegen (Wave 1, meta-repo)**
- `tools/catalog/messages.toml`: add `MSG_DATA_VPP_VOLTAGE`, `MSG_DATA_VPE_VOLTAGE`, `MSG_DATA_CHUNK`; reshape `MSG_OK_REV` (0x04) to `u8+u8`; reshape `MSG_OK_CFG` (0x05) to `u32+u32+u8`; reshape `MSG_OK_FW_HANDSHAKE` (0x06) to `u8+u8+ascii_str` (wire_format→id_frame); add `MSG_DEBUG` (0xF0) main entry; add `[debug]` section with all `DBG_*` entries
- `tools/catalog/codegen.py`: extend to parse `[debug]` section, emit `DBG_*` #defines in messages.h + `DEBUG_CATALOG` dict in messages.py
- Run `sync_to_subrepos.sh` → commit in sub-repos

**Group 2 — Wire-format `len` widening (atomic: firmware + host + test_messages)**
- `firestarter/src/boards/rurp_serial_utils.cpp`: widen `len` to u16 in `_firestarter_emit_frame`
- Update `firestarter/src/boards/rurp_serial_utils.cpp` param guard: `param_count > 65533` (new safe cap for u16-len)
- `firestarter_app/firestarter/serial_comm.py`: read 2 bytes for `frame_len` in `_read_and_parse_lines`; update `_decode_id_frame` signature if needed
- `firestarter_app/tests/conftest.py`: update `build_frame` helper to emit u16 len
- `firestarter/test/native/avr/test_messages/test_rurp_log_id.cpp`: update all byte-offset assertions (+1 shift from byte 4 onward)

**Group 3 — New `logging_id.h` macro families**
- `firestarter/include/logging_id.h`: add `LOG_OK_ID_*` / `LOG_INIT_ID_*` / `LOG_MAIN_ID_*` / `LOG_END_ID_*` / `LOG_DATA_ID_*` / `LOG_DEBUG_ID_*` families (one-line aliases over `LOG_ID_*`, same pattern as Phase 7)
- Multi-param composers needed: `LOG_OK_ID_U8_U8_ASTR` (for P-04 FW_HANDSHAKE), `LOG_DATA_ID_U16_U16` (for VPP/VPE), `LOG_DATA_ID_U32_U32` (already exists as `LOG_ID_U32_U32` if present; verify)

**Group 4 — Per-file call-site conversions (firmware, parallel commits)**
- `operation_utils.cpp`: convert `send_main_done()` / `send_init_done()` / `send_end_done()` at lines 184/254/256
- `hardware_operations.cpp`: convert VPP/VPE voltage path (lines 67-69), `send_ack_const("Ready")` (line 44), `fw_get_version` (line 80 → P-01), `hw_get_version` (line 89 → P-02), `hw_get_config` (line 100-102 → P-03)
- `eprom_operations.cpp`: convert `send_ack_const("Req data")` (line 80) + `log_data_const("Sending data")` (line 121)
- `firestarter.cpp`: convert `send_ack_format(PARSE_RESPONSE, ...)` at lines 150/153 (P-04 composite)
- PROM populate-sites (R-02): `eprom.cpp:104`, `eprom.cpp:171`, `flash_type_3.cpp:88`, `flash_type_4.cpp:52`, `memory.cpp:397`

**Group 5 — `_check_response` strip + `response_msg` deletion + `copy_to_buffer` deletion**
- `operation_utils.cpp:320,325`: drop `log_info(handle->response_msg)` and `log_data(handle->response_msg)`
- `firestarter.h:21,79`: delete `RESPONSE_MSG_SIZE` define + `char response_msg[RESPONSE_MSG_SIZE]` field
- `logging.h`: delete `copy_to_buffer` macro definition (all callers now gone)
- Remove all `response_msg` clear sites (`firestarter.cpp:64,163`, `operation_utils.cpp:300`)

**Group 6 — debug() single-sweep conversion**
- All `debug()` / `debug_format()` call-sites (46 found in codebase — see Pitfalls note) across all source files
- Single commit sweep using `LOG_DEBUG_ID(DBG_*, ...)` macros

### Host Parser Surgical Removal Map

The smallest surgical removal for `serial_comm.py` is four targeted edits:

1. **`EXPECTED_PREFIXES` list (line 123-133):** Remove `"MAIN"`, `"INIT"`, `"END"` entries. Keep `"OK"` and `"DATA"` for the bootstrap text path and the `MSG_OK_FW_VERSION` text response (LFW-05 exemption). After W-03, `"DATA"` is also removed.

2. **`STATE_MACHINE_PREFIXES` list (line 146):** Remove or empty. The `_log_rurp_feedback` method uses this list only to replace the message text with `"Done"` for display. Once these acks are ID frames, the catalog format string handles display.

3. **`_log_rurp_feedback` (line 282-283):** Remove the `if response.type in STATE_MACHINE_PREFIXES: message = "Done"` branch. The decoded ID frame already carries the rendered text from the catalog format string.

4. **`_read_and_parse_lines` — no structural change needed for the text path.** The magic-preamble detection already handles binary frames; the 0x0A text path continues to handle the one surviving text line (FW-version handshake). No new code paths required — only the prefix matching in `_parse_response_line` becomes a no-op for these removed prefixes.

The `PREFIX_REGEX` is recompiled from `EXPECTED_PREFIXES` at module load, so removing entries from the list automatically shrinks the regex.

**`expect_ack()` is already severity-band-correct.** It checks `response.type == "OK"` — which is the severity label returned by `_decode_id_frame` when `CATALOG[msg_id].severity == "OK"`. No change needed to `expect_ack` for the ID-frame path (the severity label is the same string `"OK"` in both paths).

### Anti-Patterns to Avoid

- **Splitting the `len` widening across separate commits.** The firmware emitting a u16 `len` while the host still reads a u8 `len` is a desync that silently corrupts all subsequent frames. Firmware + host + test must change together in a single atomic commit.
- **Changing `wire_format` on MSG_OK_FW_VERSION (0x03).** This ID must remain `wire_format = "text"` to preserve the `_probe_port` bootstrap path (LFW-05). The `_decode_id_frame` WR-03 guard explicitly rejects this ID as a binary frame.
- **Deleting `response_msg` before all populate-sites are converted.** The field is still written by the OK + DATA branches of `_check_response` until Group 4 completes. Deletion in Group 5 is the correct ordering.
- **Adding `LOG_DEBUG_ID_*` call-sites before `MSG_DEBUG` is in the catalog.** Group 1 (catalog) must land before Group 6 (debug sweep) to keep the CI drift gate green.
- **Forgetting the `DATA_BUFFER_SIZE=512` constraint.** platformio.ini currently sets Leonardo to 512 B (matching Uno) as a "TEMP" comment. `MSG_DATA_CHUNK` params = 512 bytes max → u16 `len` = 515 (`1 id + 512 params + 1 crc + 1 anchor` needs len=514 if counting id+params+crc; verify exact arithmetic in emit function). The 253-byte cap enforced by `_firestarter_emit_frame`'s old guard must become a 65533-byte cap (u16 max - 2 for id+crc).

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Wire-frame `len` u8→u16 | Custom multi-byte len scheme | Direct: MSB-first u16 at position 4-5 (same big-endian convention as all existing params) | The host decoder already unpacks big-endian params; reuse `struct.unpack_from(">H", ...)` |
| CRC computation | Re-derive polynomial | `crc8_ccitt` / `_CRC8_CCITT_TABLE` already in place; CRC covers `[id, params]` — unchanged | Same algorithm; widening `len` does not change what CRC covers |
| TOML `[debug]` section validation | Custom parser extension | Extend `validate_catalog` in `codegen.py` to validate the new `[debug]` array; reuse all 10 existing rules structurally | Rules 1-10 apply identically to debug entries (id uniqueness within debug namespace, name format `DBG_*`, param budget, etc.) |
| Per-debug-string catalog IDs | Allocate 46 separate main-catalog IDs for debug | `MSG_DEBUG` (single main ID) + `u8 sub_id` namespace | B-01 explicitly chose this to avoid catalog bloat; the debug channel is production-stripped anyway |
| Host `DEBUG_CATALOG` rendering | Inline debug string rendering in `serial_comm.py` | `codegen.py` emits `DEBUG_CATALOG` dict using the same `MessageDef` dataclass already used by `CATALOG` | Zero new host decoding logic; the existing `_decode_id_frame` path can handle `MSG_DEBUG` frames if the outer reader extracts `sub_id` first |

---

## Common Pitfalls

### Pitfall 1: debug() call-site count mismatch (CONTEXT says 34; codebase has 46)
**What goes wrong:** The CONTEXT.md B-01 cites 34 `debug()` call-sites. A fresh grep of the codebase (`debug\|debug_format` across all firmware source files) finds 46 active call-sites (including `sram.cpp:15`, `eprom.cpp` has 8 sites not 7 as expected, `flash_intel.cpp` has 4 sites, `memory.cpp` has 4 sites, etc.). [VERIFIED: grep output above, 46 total matches]
**Why it happens:** The CONTEXT count may have been derived from an earlier code state or from a subset of source files. The actual number of `DBG_*` sub_id entries to allocate in `[debug]` depends on the real count.
**How to avoid:** Before writing the `[debug]` section in `messages.toml`, run `grep -rn "debug\|debug_format" firestarter/src/ | grep -v "//"` and enumerate all unique string arguments to assign `DBG_*` names. Some strings repeat across files (e.g., `"Configuring..."` appears in multiple proms); these can share a sub_id or be kept distinct — researcher recommends distinct for grep-ability.
**Warning signs:** A Wave-6 debug sweep that finds more sites than the catalog has `DBG_*` entries will fail to build.

### Pitfall 2: test_messages byte-offset shift from `len` widening
**What goes wrong:** Every byte-level assertion in `test_rurp_log_id.cpp` hard-codes offsets relative to the start of the captured buffer. With u8 `len` at `captured[4]`, the ID was at `captured[5]`, params at `captured[6]`, etc. With u16 `len` at `captured[4..5]` (MSB-first), every subsequent assertion shifts by +1.
**Why it happens:** The test was written when `len` was 1 byte. The widening is invisible to the test unless offsets are updated.
**How to avoid:** Update `test_rurp_log_id.cpp` in the same commit as `_firestarter_emit_frame`. The new frame layout:
- `captured[0..3]` — magic preamble (unchanged)
- `captured[4]` — `len` MSB
- `captured[5]` — `len` LSB
- `captured[6]` — id (was `captured[5]`)
- `captured[7..N]` — params (were `captured[6..N-1]`)
- `captured[N+1]` — crc (was `captured[N]`)
- `captured[N+2]` — 0x0A (was `captured[N+1]`)
The `test_oversize_param_count_rejected` test currently pins the 253-byte safe max (producing `captured[4] = 0xFF`). After widening, the new maximum is 65533 params (impractical to test fully); update the guard logic and the boundary test accordingly.
**Warning signs:** `test_messages` FAILED after Group 2 commit means the assertion update was missed.

### Pitfall 3: `conftest.py` `build_frame` helper encodes old u8 len
**What goes wrong:** `firestarter_app/tests/conftest.py:61` computes `length = len(body) + 1` and packs it as a single byte: `bytes([length])`. After W-04, frame length must be 2 bytes (u16 big-endian). All 9 tests in `test_decoder.py` that call `build_frame` will silently produce frames with an incorrect length field, causing the host decoder to read 1 garbage byte as the second length byte.
**Why it happens:** `conftest.py` was written to the Phase 6 wire format.
**How to avoid:** Update `build_frame` in Group 2: `length = len(body) + 1; return MAGIC_PREAMBLE_REF + struct.pack(">H", length) + body + bytes([crc, 0x0A])`. Add `import struct` if not already present.
**Warning signs:** `test_decoder.py` seeing `frame_len = 0` or garbage values after Group 2.

### Pitfall 4: `MSG_OK_FW_HANDSHAKE` wire_format change breaks WR-03 guard
**What goes wrong:** Currently `MSG_OK_FW_HANDSHAKE` (0x06) has `wire_format = "text"` in `messages.toml`. P-04 changes it to an ID frame (`u8 hw + u8 cmd + ascii_str fw_version`). The existing `_decode_id_frame` WR-03 guard in `serial_comm.py:345-351` explicitly rejects binary frames for `wire_format="text"` catalog entries — and `test_decoder.py:test_wire_format_text_catalog_id_rejected_as_id_frame` pins this behavior for both 0x03 and 0x06.
**Why it happens:** The guard and test were written when 0x06 was `wire_format="text"`. After P-04 changes the catalog, the guard correctly allows ID frames for 0x06 — but the test must be updated to no longer assert rejection for 0x06.
**How to avoid:** In Group 1 (catalog change) and Group 2 (host+test update), update `test_wire_format_text_catalog_id_rejected_as_id_frame` to only assert rejection for 0x03 (`MSG_OK_FW_VERSION`). Add a positive test for 0x06 decoding as an ID frame with the P-04 shape.
**Warning signs:** `test_decoder.py::test_wire_format_text_catalog_id_rejected_as_id_frame` FAILED after Group 1 catalog update (test still expects 0x06 to be rejected).

### Pitfall 5: `DATA:` prefix removal breaks the chip-read host loop
**What goes wrong:** The host's chip-read receive loop in `eprom_operations.py` (or the equivalent in `serial_comm.py`) currently detects the `DATA:` prefix to know when chip bytes are incoming, then reads `data_size` raw bytes off the wire. After W-04, the chunk arrives as a `MSG_DATA_CHUNK` ID frame. If the host still looks for a `DATA:` text prefix, it will time out.
**Why it happens:** The DATA streaming path is more complex than the simple log-line paths. The host does not just decode a log message — it drives a state machine (send ACK, receive DATA chunk, decode chunk size from frame, forward to file).
**How to avoid:** Map the exact host chip-read receive path before committing the firmware-side `eprom_operations.cpp:116` change. The relevant host code is in `firestarter_app/firestarter/eprom_operations.py` (not `serial_comm.py`). The `MSG_DATA_CHUNK` decode needs special handling: the params bytes ARE the chip data, not a rendered string. The host reader must extract the raw bytes from the frame body.
**Warning signs:** Read operations hang or produce zero-byte output after Group 4 `eprom_operations.cpp` conversion.

### Pitfall 6: P-04 `send_ack_format` / `format()` macro still references `handle->response_msg`
**What goes wrong:** The current `send_ack_format(PARSE_RESPONSE, ...)` macro at `firestarter.cpp:150,153` expands to `format(handle->response_msg, PARSE_RESPONSE, ...); send_ack(handle->response_msg)`. The `format` macro uses `handle->response_msg` as its RAM scratch buffer. After R-01 deletes the field, this buffer reference is a use-after-delete.
**Why it happens:** The macro is still present in `logging.h` (Phase 9 scope for deletion) but the field it writes to is gone.
**How to avoid:** Convert the `firestarter.cpp:150,153` sites (Group 4, P-04) before deleting `response_msg` (Group 5). The P-04 conversion emits `LOG_OK_ID_U8_U8_ASTR(MSG_OK_FW_HANDSHAKE, hw_rev, cmd, fw_version_str)` using a local stack buffer for the ascii_str — no `response_msg` needed.
**Warning signs:** Firmware compile error `'firestarter_handle_t' has no member named 'response_msg'` if Group 5 lands before Group 4.

### Pitfall 7: `copy_to_buffer` helper deletion — verify all callers
**What goes wrong:** `logging.h` defines `copy_to_buffer(buf, msg)` as `strcpy_P(buf, PSTR(msg))`. Phase 8 is supposed to eliminate all callers (they're all populate-sites filling `response_msg`). But `copy_to_buffer` may also be used by other code not in the R-02 site list (e.g., `hw_version_override` at `hardware_operations.cpp:110` uses `strcpy_P` directly but similar patterns might exist elsewhere).
**Why it happens:** The R-02 site list focuses on the known `response_msg`-filling sites; other uses of `copy_to_buffer` may exist.
**How to avoid:** Before Group 5, run `grep -rn "copy_to_buffer" firestarter/src/ firestarter/include/` and verify the result is zero or exclusively the `#define` line in `logging.h`. [VERIFIED: flash_type_3.cpp:88 and flash_type_4.cpp:52 use `copy_to_buffer` directly — both are in the R-02 site list. No other callers found in the initial grep.]
**Warning signs:** Compile error referencing `copy_to_buffer` after `logging.h` macro deletion.

---

## Code Examples

### Adding new LOG_*_ID_* macro families (Group 3 pattern)
```cpp
// Source: firestarter/include/logging_id.h (Phase 7 pattern — extend to OK/INIT/MAIN/END/DATA/DEBUG)
// All are thin aliases over the same LOG_ID_* primitives — zero runtime cost.

// --- Unconditional OK severity ---
#define LOG_OK_ID(id)               LOG_ID(id)
#define LOG_OK_ID_U8(id, p)         LOG_ID_U8((id), (p))
// ... same surface as LOG_ERROR_ID_*

// --- Unconditional INIT severity ---
#define LOG_INIT_ID(id)             LOG_ID(id)
// (INIT acks are all zero-param so only LOG_INIT_ID needed in practice)

// --- Unconditional DATA severity ---
#define LOG_DATA_ID(id)             LOG_ID(id)
#define LOG_DATA_ID_U16_U16(id, p1, p2) \
    do { \
        uint16_t _v1 = (uint16_t)(p1); uint16_t _v2 = (uint16_t)(p2); \
        uint8_t _b[4] = { \
            (uint8_t)((_v1>>8)&0xFF),(uint8_t)(_v1&0xFF), \
            (uint8_t)((_v2>>8)&0xFF),(uint8_t)(_v2&0xFF) }; \
        rurp_log_id((id), _b, 4); \
    } while (0)

// --- SERIAL_DEBUG-gated DEBUG severity ---
#ifdef SERIAL_DEBUG
#define LOG_DEBUG_ID_SUB(sub_id)    LOG_ID_U8(MSG_DEBUG, (sub_id))
#define LOG_DEBUG_ID_SUB_U8(sub_id, p1) /* sub_id + p1 packed into LOG_ID_BYTES */ \
    do { uint8_t _b[2] = {(uint8_t)(sub_id),(uint8_t)(p1)}; rurp_log_id(MSG_DEBUG, _b, 2); } while(0)
#else
#define LOG_DEBUG_ID_SUB(sub_id)
#define LOG_DEBUG_ID_SUB_U8(sub_id, p1)
#endif
```

### Wire-format `len` widening in `_firestarter_emit_frame`
```cpp
// Source: firestarter/src/boards/rurp_serial_utils.cpp (Phase 6, line ~156-200)
// BEFORE (u8 len):
//   if (param_count > 253) return;
//   uint8_t len = (uint8_t)(1 + param_count + 1);
//   SERIAL_PORT.write(len);

// AFTER (u16 len, Phase 8 W-04):
//   if (param_count > 65533) return;   // 65535 - 2 (for id+crc)
//   uint16_t len_u16 = (uint16_t)(1 + param_count + 1);
//   SERIAL_PORT.write((uint8_t)(len_u16 >> 8));   // MSB
//   SERIAL_PORT.write((uint8_t)(len_u16 & 0xFF));  // LSB
// CRC, ID, params writes: UNCHANGED
```

### Host `len` widening in `_read_and_parse_lines`
```python
# Source: firestarter_app/firestarter/serial_comm.py (Phase 6, line ~451-464)
# BEFORE:
#   len_bytes = self.connection.read(1)
#   frame_len = len_bytes[0]

# AFTER (Phase 8 W-04):
#   len_bytes = self.connection.read(2)   # Read 2 bytes for u16
#   if len(len_bytes) < 2:
#       logger.warning("Magic preamble seen but length bytes not received — re-syncing.")
#       continue
#   import struct
#   frame_len = struct.unpack_from(">H", len_bytes)[0]  # big-endian u16
```

### `conftest.py` `build_frame` update
```python
# Source: firestarter_app/tests/conftest.py
# BEFORE:
#   length = len(body) + 1
#   return MAGIC_PREAMBLE_REF + bytes([length]) + body + bytes([crc, 0x0A])

# AFTER (Phase 8 W-04):
import struct
def build_frame(msg_id: int, params: bytes) -> bytes:
    body = bytes([msg_id]) + params
    crc = _ref_crc8_ccitt(body)
    length = len(body) + 1  # id + params + crc
    return MAGIC_PREAMBLE_REF + struct.pack(">H", length) + body + bytes([crc, 0x0A])
```

### P-04 FW_HANDSHAKE conversion (two-line firmware pattern)
```cpp
// Source: firestarter/src/firestarter.cpp:148-154 (existing)
// BEFORE:
// #ifdef HARDWARE_REVISION
// #define PARSE_RESPONSE "FW: " FW_VERSION ", HW: Rev%d, Cmd: 0x%02x"
//     send_ack_format(PARSE_RESPONSE, rurp_get_hardware_revision(), handle->cmd);
// #else
// #define PARSE_RESPONSE "FW: " FW_VERSION ", Cmd: 0x%02x"
//     send_ack_format(PARSE_RESPONSE, handle->cmd);
// #endif

// AFTER (P-04 composite: u8 hw + u8 cmd + ascii_str fw_version):
{
    uint8_t hw_rev;
    #ifdef HARDWARE_REVISION
    hw_rev = (uint8_t)rurp_get_hardware_revision();
    #else
    hw_rev = 0xFF;  // sentinel: no hardware revision
    #endif
    uint8_t cmd_byte = (uint8_t)handle->cmd;
    const char* fw_str = FW_VERSION;
    uint8_t fw_len = (uint8_t)strlen(fw_str);
    // ascii_str wire encoding: 1-byte length prefix + N data bytes
    uint8_t _b[2 + 1 + 32] = { hw_rev, cmd_byte, fw_len };
    memcpy(_b + 3, fw_str, fw_len);
    LOG_ID_BYTES(MSG_OK_FW_HANDSHAKE, _b, 3 + fw_len);
}
```

### Catalog `[debug]` section shape
```toml
# tools/catalog/messages.toml — new [debug] section (B-03)
# MSG_DEBUG main ID in [[messages]]:
[[messages]]
id          = 0xF0
name        = "MSG_DEBUG"
severity    = "INFO"  # or a new DEBUG severity if codegen is extended
format      = "[debug] %s"   # host rendering placeholder
params      = []             # actual decode handled via DEBUG_CATALOG sub_id lookup
wire_format = "id_frame"

# Inline debug catalog:
[debug]

[[debug.messages]]
id     = 0x00
name   = "DBG_FIRESTARTER_STARTED"
format = "Firestarter started"
params = []

[[debug.messages]]
id     = 0x01
name   = "DBG_FW_VERSION"
format = "Firmware version: %s"
params = [{ type = "ascii_str" }]

# ... (one entry per unique debug string, 46 total after audit)
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Text-prefix line matching for all firmware output | Binary ID frames for ERROR/WARN/INFO (Phase 7) | Phase 7 complete | State-machine acks still text |
| Fixed u8 `len` field (253-byte param cap) | u16 `len` field (65533-byte param cap) | Phase 8 W-04 | Enables 512-byte DATA_CHUNK frames |
| `response_msg[96]` SRAM scratch for all log text | No scratch buffer — params encoded directly to wire | Phase 8 R-01 | ~96 bytes SRAM recovered |
| `debug()` via `#ifdef SERIAL_DEBUG` text string | `MSG_DEBUG + sub_id` binary sub-ID channel | Phase 8 B-01 | Same production-stripping; catalog-uniform |

**Deprecated/outdated after Phase 8:**
- `send_ack_const` / `send_ack_format` macros in `logging.h`: all callers gone; definitions remain until Phase 9 deletion
- `log_data_const` / `log_data_format` macros: same
- `send_main_done()` / `send_init_done()` / `send_end_done()` macros: all callers gone; definitions remain until Phase 9 deletion
- `copy_to_buffer` macro: all callers gone by Group 5; definition deleted in Phase 8 (NOT deferred to Phase 9)
- `format()` macro: callers gone for the `response_msg` patterns; may still be referenced inside `send_ack_format` body (but macro itself stays until Phase 9)

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | `DATA_BUFFER_SIZE` is effectively 512 on both boards (platformio.ini sets `DATA_BUFFER_SIZE=512` for Leonardo explicitly; Uno default is 512). | Standard Stack | If Leonardo reverts to 1024 between now and Phase 8 execution, the `MSG_DATA_CHUNK` param-max arithmetic changes — still fits in u16 but the guard threshold changes |
| A2 | 46 active `debug()`/`debug_format()` call-sites found by grep. The CONTEXT says 34. | Common Pitfalls P1 | If the count is wrong (e.g., some are in `#if 0` blocks or conditional code not compiled), the `[debug]` section sub_id count will be over-allocated — harmless but untidy |
| A3 | The chip-read host receive loop is in `firestarter_app/firestarter/eprom_operations.py` and reads `DATA:` prefix-tagged lines. The specific function name and line numbers were not verified. | Common Pitfalls P5 | If the read loop is in `serial_comm.py` or elsewhere, the Pitfall 5 advice targets the wrong file |
| A4 | `hw_version_override()` at `hardware_operations.cpp:107-114` uses `strcpy_P` directly (not `copy_to_buffer`). Confirmed by code read. | Pitfall 7 | [VERIFIED] — not an assumed claim |

---

## Open Questions

1. **`DATA_BUFFER_SIZE` restoration for Leonardo**
   - What we know: `platformio.ini` comment says `; TEMP: 512 to match Uno for buffer-size A/B test (was 1024)`. This was explicitly set to 512 during Phase 6/7 work.
   - What's unclear: Whether Phase 8 should restore Leonardo to 1024 before designing the `MSG_DATA_CHUNK` frame, or keep 512. If 1024 is restored, the `msg_data_chunk` params can be up to 1020 bytes (u16 handles this easily) but the native test binary and SRAM budget must account for it.
   - Recommendation: Keep 512 for Phase 8. The TEMP comment suggests the restore is a separate decision. Note in the plan.

2. **`MSG_DEBUG` severity band assignment**
   - What we know: Catalog currently has no `DEBUG` severity. The B-03 design puts debug strings in a `[debug]` section with `MSG_DEBUG` as the single main ID.
   - What's unclear: Whether `MSG_DEBUG` should use `severity = "INFO"` (stays in the INFO band 0x40–0x7F, but uses ID 0xF0 which is in the DATA band) or whether a new `DEBUG` severity should be added to codegen.
   - Recommendation: Use `severity = "DATA"` for `MSG_DEBUG` since 0xF0 falls in the DATA band (0xE0–0xFF). The host can check for `msg_id == MSG_DEBUG` and look up the `sub_id` in `DEBUG_CATALOG`. Production rendering can be silenced by default (`logger.debug` level only).

3. **`MSG_OK_FW_VERSION` (0x03) ascii_str shape change (P-01)**
   - What we know: Currently `wire_format = "text"` with `params = []`. P-01 changes it to `ascii_str` param and presumably `wire_format = "id_frame"`.
   - What's unclear: The FW-version handshake must still flow as text (LFW-05) for the bootstrap probe path. P-01 appears to define the catalog shape for when it IS an ID frame — but `_probe_port` must still parse `"FW: 2.0.11-dev:uno, HW: Rev1, Cmd: 0x0f"` as a text response. The resolution: after Phase 8, `MSG_OK_FW_VERSION` stays `wire_format = "text"` at 0x03 (bootstrap), but `MSG_OK_FW_HANDSHAKE` at 0x06 becomes the ID-frame channel (P-04). Confirm whether P-01 means "add a new ascii_str-param ID at 0x03 for id-frame use" or something else.
   - Recommendation: P-01 most likely means the catalog entry for 0x03 gains a declared `ascii_str` param shape for documentation purposes while keeping `wire_format = "text"`. The planner should confirm with the CONTEXT.md wording — it says "MSG_OK_FW_VERSION (0x03) uses `ascii_str` as the single param" without specifying wire_format. Given LFW-05, keep `wire_format = "text"` and `params = [{type = "ascii_str"}]` — the WR-03 guard still rejects binary frames for this ID.

---

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| PlatformIO CLI (`pio`) | Build + test (`pio run -e uno/leonardo/native`) | ✓ | Installed (project uses it — Phase 7 measurements show build output) | — |
| Python 3.12 + tomllib | `codegen.py` TOML parsing | ✓ | 3.12.13 (per Phase 7 verification output) | — |
| pytest | `firestarter_app/tests/` | ✓ | 9.0.3 (per Phase 7 verification) | — |
| Arduino Uno (hardware) | Hardware integration test (SC#2) | ✓ | `/dev/ttyACM0` confirmed Phase 7 | Simulate-only if unavailable |
| Arduino Leonardo (hardware) | Hardware integration test (SC#2) | ✓ | `/dev/ttyACM1` confirmed Phase 7 | Simulate-only if unavailable |
| `FIRESTARTER_DEV_ALLOW_PRE_V12=1` | Bench bypass until Phase 9 v3.0.0 bump | ✓ | Set by operator per Phase 7 SC#2 | — |

---

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework (firmware native) | Unity (via PlatformIO `test_framework = unity`) |
| Framework (host) | pytest 9.0.3 |
| Config file (firmware) | `firestarter/platformio.ini` `[env:native]` |
| Config file (host) | `firestarter_app/pyproject.toml` |
| Quick run command (firmware) | `cd firestarter && pio test -e native -f "*test_messages*"` |
| Quick run command (host) | `cd firestarter_app && python -m pytest tests/test_decoder.py -v` |
| Full suite command (firmware) | `cd firestarter && pio test -e native && pio run -e uno && pio run -e leonardo` |
| Full suite command (host) | `cd firestarter_app && python -m pytest tests/ -v` |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| LMIG-03 / W-04 | u16 `len` field emitted correctly by firmware | unit | `pio test -e native -f "*test_messages*"` | ✅ `test_rurp_log_id.cpp` (needs update) |
| LMIG-03 / W-04 | u16 `len` field decoded correctly by host | unit | `python -m pytest tests/test_decoder.py -v` | ✅ `test_decoder.py` (needs update) |
| LMIG-03 / W-01/W-02 | OK/INIT/MAIN/END arrive as ID frames, decoded by severity band | unit | `python -m pytest tests/test_decoder.py -v` | ❌ New tests needed in Wave 0 |
| LMIG-03 / P-04 | MSG_OK_FW_HANDSHAKE composite frame round-trips | unit | `python -m pytest tests/test_decoder.py -v` | ❌ New test needed |
| LMIG-03 / P-02 | MSG_OK_REV `u8+u8` with 0xFF sentinel decoded correctly | unit | `python -m pytest tests/test_decoder.py -v` | ❌ New test needed |
| LMIG-03 / P-03 | MSG_OK_CFG `u32+u32+u8` with 0xFF sentinel decoded correctly | unit | `python -m pytest tests/test_decoder.py -v` | ❌ New test needed |
| LMIG-03 / R-01 | `response_msg` field deleted, both boards build | smoke | `pio run -e uno && pio run -e leonardo` | ✅ Part of existing build |
| LMIG-03 / R-03 | `_check_response` switch is log-emit-free | manual | Code review / grep `log_info\|log_data` in `operation_utils.cpp` | ✅ (grep gate) |
| LMIG-03 / B-03 | `DBG_*` constants emitted by codegen, no drift | unit | `cd firestarter && python tools/catalog/codegen.py --catalog tools/catalog/messages.toml --language cpp --target include/messages.h && git diff --exit-code include/messages.h` | ✅ CI drift gate (needs debug section) |
| LMIG-03 / B-01 | debug() call-sites compile to no-ops in production build | smoke | `pio run -e uno` (no `SERIAL_DEBUG` flag in default build) | ✅ platformio.ini `; -D SERIAL_DEBUG` |
| LMIG-03 / hardware | End-to-end command cycle (FW_HANDSHAKE + INIT + MAIN + END as ID frames) | integration | `FIRESTARTER_DEV_ALLOW_PRE_V12=1 firestarter hw` (both boards) | manual |

### Sampling Rate
- **Per task commit:** `pio test -e native -f "*test_messages*"` + `python -m pytest tests/test_decoder.py -v`
- **Per wave merge:** Full suite: `pio test -e native && pio run -e uno && pio run -e leonardo && python -m pytest tests/ -v`
- **Phase gate:** Full suite green + hardware integration test on both Uno + Leonardo before `/gsd-verify-work`

### Wave 0 Gaps
- [ ] `firestarter_app/tests/test_decoder.py` — add tests for MSG_OK_INIT_DONE / MSG_MAIN_DONE / MSG_END_DONE as ID frames (REQ: W-01/W-02)
- [ ] `firestarter_app/tests/test_decoder.py` — add test for MSG_OK_FW_HANDSHAKE P-04 composite frame decode (REQ: P-04)
- [ ] `firestarter_app/tests/test_decoder.py` — add test for MSG_OK_REV P-02 shape (REQ: P-02)
- [ ] `firestarter_app/tests/test_decoder.py` — add test for MSG_OK_CFG P-03 shape (REQ: P-03)
- [ ] `firestarter_app/tests/test_decoder.py` — update `test_wire_format_text_catalog_id_rejected_as_id_frame` to no longer assert rejection for 0x06 (REQ: P-04)
- [ ] `firestarter/test/native/avr/test_messages/test_rurp_log_id.cpp` — update all byte-offset assertions for u16 `len` (REQ: W-04) — must land in Group 2
- [ ] `firestarter_app/tests/conftest.py` — update `build_frame` to emit u16 `len` (REQ: W-04) — must land in Group 2

*(Existing `test_dispatch` suite: no changes expected — `_check_response` R-03 strip does not add new link-time symbols. The host stubs in `_shared/host_stubs_common.inc` do not need changes for Phase 8 unless `response_msg` field removal causes a compile error in the dispatch test build. Verify: `response_msg` is accessed by dispatch tests only through `firestarter_handle_t`; its deletion from the struct will cause a compile error in `test_dispatch` if any dispatch test directly accesses `handle.response_msg`. Check `test_configure_memory.cpp` — likely does not access `response_msg` directly.)*

---

## Security Domain

> `security_enforcement` is not explicitly set to `false` in `.planning/config.json` — treated as enabled.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | No | No user authentication in this embedded protocol |
| V3 Session Management | No | Stateless serial command/response |
| V4 Access Control | No | Physical serial port access controls this |
| V5 Input Validation | Yes | `_decode_id_frame` bounds-checks `frame_len`, CRC validates, `ascii_str` length-prefix validated (WR-04 guard) |
| V6 Cryptography | No — CRC8 is integrity-only, not cryptographic | CRC8-CCITT is the existing design; the wire is physically controlled |

### Known Threat Patterns for Embedded UART + Binary Framing

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Frame desync from ghost bytes (Uno PORTD aliasing) | Tampering | 4-byte MAGIC preamble + CRC8 + length-authoritative decode (already implemented Phase 6) |
| u16 `len` overflow (adversarial frame claiming 65535-byte body) | Denial of Service | `connection.read(frame_len)` with pyserial timeout; `if len(body) != frame_len: continue` guard already present |
| `ascii_str` length-prefix overflow | Tampering | WR-04 guard already in `_decode_param`: raises `ValueError` if `end > len(buf)` |
| Unknown sub_id for `MSG_DEBUG` | Information Disclosure | `DEBUG_CATALOG.get(sub_id)` returns `None`; host logs warning and continues |
| `MSG_DATA_CHUNK` claiming larger body than actual chip data | Tampering | u16 `len` + CRC8 catches truncation; host reads exactly `frame_len` bytes from serial |

---

## Sources

### Primary (HIGH confidence — verified against live source files)
- `firestarter/src/boards/rurp_serial_utils.cpp` — wire-frame emit function (`_firestarter_emit_frame`), len write at line 176-177, full function lines 156-200
- `firestarter_app/firestarter/serial_comm.py` — `_decode_id_frame` lines 299-389, `_read_and_parse_lines` lines 391-512, `_parse_response_line` lines 249-274, `EXPECTED_PREFIXES` / `STATE_MACHINE_PREFIXES` lines 123-147
- `firestarter/include/firestarter.h` — `RESPONSE_MSG_SIZE` line 21, `response_msg` field line 79
- `firestarter/include/logging_id.h` — full Phase 7 macro family (verified current state)
- `firestarter/include/logging.h` — full macro tower; `copy_to_buffer`, `send_ack_format`, `send_main_done`, `send_init_done`, `send_end_done` all verified
- `firestarter/src/operation_utils.cpp` — `_check_response` lines 309-327, `_execute_operation` lines 290-299
- `firestarter/src/hardware_operations.cpp` — VPP/VPE path lines 60-76, `fw_get_version` line 79-81, `hw_get_version` lines 85-91, `hw_get_config` lines 94-104
- `firestarter/src/firestarter.cpp` — `PARSE_RESPONSE` sites lines 148-154, `response_msg` clear lines 67, 168
- `firestarter/src/eprom_operations.cpp` — `send_ack_const("Req data")` line 80, `log_data_const("Sending data")` line 121
- `firestarter/src/proms/eprom.cpp` — `copy_to_buffer("Skipping erase.")` line 104, `format(response_msg, "Number of retries: %d", retries)` line 171
- `firestarter/src/proms/flash_type_3.cpp` — `copy_to_buffer("Skipping erase of memory")` line 88
- `firestarter/src/proms/flash_type_4.cpp` — `copy_to_buffer("Skipping erase.")` line 52
- `firestarter/src/proms/memory.cpp` — `firestarter_data_response_format("%lu/%lu", ...)` line 325
- `tools/catalog/messages.toml` — full 68-entry catalog (verified); existing IDs for OK/INIT/MAIN/END/DATA confirmed
- `tools/catalog/codegen.py` — full codegen source (verified); VALID_SEVERITIES, emitters, validate_catalog
- `firestarter/test/native/avr/test_messages/test_rurp_log_id.cpp` — all test assertions verified; len byte at `captured[4]`, id at `captured[5]`
- `firestarter_app/tests/test_decoder.py` — 12-test suite; `test_wire_format_text_catalog_id_rejected_as_id_frame` pins 0x03 and 0x06
- `firestarter_app/tests/conftest.py` — `build_frame` helper; `length = len(body) + 1` as single byte
- `.planning/phases/07-convert-error-warn-info-call-sites/07-FLASH-MEASUREMENT.md` — Phase 7 close: Leonardo 94.3% (27,026 B), Uno 77.0% (24,838 B)
- `firestarter/platformio.ini` — `DATA_BUFFER_SIZE=512` confirmed for both boards in current config

### Secondary (MEDIUM confidence)
- `.planning/phases/08-convert-state-machine-prefix-call-sites-ok-init-main-end/08-CONTEXT.md` — CONTEXT decisions W-01..W-04, R-01..R-03, P-01..P-04, B-01..B-04 (user-authored)
- `.planning/phases/06-logging-infrastructure/06-CONTEXT.md` — D-01..D-06 wire-format spec
- `.planning/phases/07-convert-error-warn-info-call-sites/07-CONTEXT.md` — D-01 (check_response preserve OK+DATA branches), D-02 (two-line populate-site pattern)
- `.planning/REQUIREMENTS.md` — LMIG-03 requirement text

### Tertiary (LOW confidence)
- None — all factual claims are verified against source files.

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — all libraries/tools verified against live build output and source files
- Architecture (wire-format, emit path): HIGH — source verified line-by-line
- Catalog / codegen extension: HIGH — codegen.py structure fully read; extension pattern is clear
- Host parser surgical removal: HIGH — `serial_comm.py` `EXPECTED_PREFIXES` / `STATE_MACHINE_PREFIXES` / `_parse_response_line` all verified
- debug() call-site count: MEDIUM — grep output is reliable but manual review recommended for conditional-compilation cases
- `MSG_DATA_CHUNK` host-read integration: MEDIUM — host chip-read receive loop in `eprom_operations.py` not fully read (file not inspected; see Open Question 3 / Pitfall 5)
- SRAM impact of R-01: HIGH — `response_msg[96]` field confirmed, Phase 7 SRAM baseline verified (60.6% Leonardo = 1551/2560 bytes used, 1009 bytes free)

**Research date:** 2026-05-18
**Valid until:** 2026-06-18 (30 days; stable codebase between Phase 7 and Phase 8 with no external dependencies changing)
