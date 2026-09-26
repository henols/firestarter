---
phase: 08-convert-state-machine-prefix-call-sites-ok-init-main-end
plan: 05
subsystem: firmware-logging, host-protocol
tags: [logging-migration, composite-macros, state-machine-acks, chunk-streaming, avr, python]
dependency_graph:
  requires: [08-01, 08-02, 08-03, 08-04]
  provides: [LOG_OK_ID_U8_U8, LOG_OK_ID_U8_U8_ASTR, MSG_DATA_CHUNK-streaming, P-02, P-03, P-04, W-04-chip-stream]
  affects:
    - firestarter/include/logging_id.h
    - firestarter/include/rurp_serial_utils.h
    - firestarter/include/rurp_shield.h
    - firestarter/src/boards/rurp_serial_utils.cpp
    - firestarter/src/boards/uno_rurp_shield.cpp
    - firestarter/src/hardware_operations.cpp
    - firestarter/src/firestarter.cpp
    - firestarter/src/eprom_operations.cpp
    - firestarter_app/firestarter/eprom_operations.py
    - firestarter_app/firestarter/serial_comm.py
    - firestarter_app/tests/test_decoder.py
tech_stack:
  added:
    - LOG_OK_ID_U8_U8 composite macro (P-02 MSG_OK_REV)
    - LOG_OK_ID_U8_U8_ASTR composite macro (P-04 MSG_OK_FW_HANDSHAKE)
    - LOG_DATA_ID_U16x4 composite macro (4x u16 for VPP/VPE catalog shape)
    - _firestarter_emit_frame_wide / rurp_log_id_wide (uint16_t loop for 512-byte chunks)
    - Response.payload field (bytes | None) for MSG_DATA_CHUNK
    - LogMessage.payload field (bytes | None) internal to decoder
  patterns:
    - do-while composite macro with fixed-size stack buffer (2+1+32 bytes)
    - sibling-function approach for wide emit (avoids signature widen across all callers)
    - sentinel-byte 0xFF for optional fields (P-02, P-03, P-04)
    - Response.payload for binary pass-through without stringify overhead
key_files:
  created: []
  modified:
    - firestarter/include/logging_id.h
    - firestarter/include/rurp_serial_utils.h
    - firestarter/include/rurp_shield.h
    - firestarter/src/boards/rurp_serial_utils.cpp
    - firestarter/src/boards/uno_rurp_shield.cpp
    - firestarter/src/hardware_operations.cpp
    - firestarter/src/firestarter.cpp
    - firestarter/src/eprom_operations.cpp
    - firestarter_app/firestarter/eprom_operations.py
    - firestarter_app/firestarter/serial_comm.py
    - firestarter_app/tests/test_decoder.py
decisions:
  - "VPP/VPE catalog shape (4 x u16) matched in firmware: pre-compute integer+decimal parts rather than changing Plan 01 catalog — avoids catalog regeneration; matches messages.py param_bytes=8"
  - "sibling function _firestarter_emit_frame_wide chosen over uint8_t→uint16_t widen to minimize caller diff surface (only eprom_operations.cpp calls the wide variant)"
  - "MSG_DATA_SENDING retained per-chunk as batch-start signal; MSG_DATA_CHUNK follows immediately; host skips DATA responses with no payload"
  - "Response.payload = None default preserves backwards compatibility for all existing Response consumers"
  - "LogMessage.payload = None default preserves existing test assertions (LogMessage comparisons still work with 3-field construction in test_decoder.py)"
metrics:
  duration: "~45 min"
  completed_date: "2026-05-18"
  tasks: 4
  files: 11
---

# Phase 08 Plan 05: Wave 5 Composite Call-Site Conversions + MSG_DATA_CHUNK Streaming Summary

Every state-machine ack and every DATA emit is now an ID frame — firmware emit to host decode — except the LFW-05 bootstrap path (MSG_OK_FW_VERSION stays text-emitted via send_ack_const per P-01).

## Tasks Completed

| Task | Name | Commit (firestarter) | Commit (firestarter_app) | Key Changes |
|------|------|----------------------|--------------------------|-------------|
| 1 | Add LOG_OK_ID_U8_U8 + LOG_OK_ID_U8_U8_ASTR + LOG_DATA_ID_U16x4 composites to logging_id.h | `a44b911` | — | 42 lines; 3 new do-while composite macros |
| 2 | Convert hardware_operations.cpp — Ready ack, VPP/VPE split, hw_get_version (P-02), hw_get_config (P-03); fw_get_version stays text | `ea2a3fb` | — | 5 call-site groups converted; hw_version_override() deleted |
| 3 | Convert firestarter.cpp PARSE_RESPONSE composite to LOG_OK_ID_U8_U8_ASTR (P-04) | `0f3c08f` | — | 2-branch #ifdef → single LOG_OK_ID_U8_U8_ASTR; -1502 B / -1504 B Uno/Leonardo |
| 4a | Firmware MSG_DATA_CHUNK chip-byte streaming | `1abadaa` | — | _firestarter_emit_frame_wide + rurp_log_id_wide + Uno override; eprom_operations.cpp wrap |
| 4b | Host MSG_DATA_CHUNK decode + Response.payload + tests | — | `732e047` | serial_comm.py payload field; eprom_operations.py rewrite; 2 new roundtrip tests |

## Flash / SRAM Usage After Each Commit

| Commit | Description | Uno Flash | Leonardo Flash |
|--------|-------------|-----------|----------------|
| pre-plan (08-04 close) | baseline | 24,712 B (76.6%) | 26,892 B (93.8%) |
| `a44b911` | logging_id.h composites (header-only) | 24,712 B (76.6%) | 26,892 B (93.8%) |
| `ea2a3fb` | hardware_operations conversions | 24,300 B (75.3%) | — |
| `0f3c08f` | PARSE_RESPONSE → LOG_OK_ID_U8_U8_ASTR | 22,798 B (70.7%) | 24,990 B (87.2%) |
| `1abadaa` | MSG_DATA_CHUNK wide emit + eprom_operations wrap | 23,000 B (71.3%) | 25,194 B (87.9%) |

**Net flash delta vs pre-plan: Uno −1,712 B (−5.3%), Leonardo −1,698 B (−5.9%)**

The MSG_DATA_CHUNK emit adds ~202 B on Uno (new wide emitter function + Uno strong override); the PARSE_RESPONSE elimination saves ~1,502 B — net large win.

## Call-Site Conversion Summary

**hardware_operations.cpp — 4 groups converted, 1 preserved:**
- `send_ack_const("Ready")` → `LOG_OK_ID(MSG_OK_READY)` (Site 1)
- `log_data_format(VPP/VPE)` → `LOG_DATA_ID_U16x4(MSG_DATA_VPP/VPE_VOLTAGE, v_int, v_dec, vc_int, vc_dec)` (Site 2)
- `send_ack_const(FW_VERSION)` — PRESERVED per LFW-05/P-01 + comment added (Site 3)
- `send_ack_format(hw_get_version)` → `LOG_OK_ID_U8_U8(MSG_OK_REV, physical, effective)` per P-02 (Site 4)
- `send_ack_format(hw_get_config)` → `LOG_ID_BYTES(MSG_OK_CFG, _cfg, 9)` with 9-byte u32+u32+u8 composite per P-03 (Site 5)
- `hw_version_override()` helper deleted (no callers remain)

**firestarter.cpp — 1 composite converted:**
- `#ifdef HARDWARE_REVISION / send_ack_format(PARSE_RESPONSE, ...) / #else ...` → `LOG_OK_ID_U8_U8_ASTR(MSG_OK_FW_HANDSHAKE, hw_rev, handle->cmd, FW_VERSION)` (P-04)
- `#define PARSE_RESPONSE` macros deleted
- `response_msg[0] = '\0'` clear sites at lines 67 + 168 preserved for Plan 06

**eprom_operations.cpp — 1 site wrapped:**
- `rurp_communication_write(handle->data_buffer, handle->data_size)` → `rurp_log_id_wide(MSG_DATA_CHUNK, (uint8_t*)handle->data_buffer, (uint16_t)handle->data_size)` (W-04)

**Total firmware call-sites converted: 6** (Ready, VPP/VPE x2, hw_get_version, hw_get_config, PARSE_RESPONSE, DATA_CHUNK wrap)
**Preserved: 1** (fw_get_version — LFW-05 bootstrap text path)

## Decision: sibling function vs uint8_t→uint16_t widen (W-04)

**Chose: sibling function** (`_firestarter_emit_frame_wide` + `rurp_log_id_wide`).

Rationale: widening `_firestarter_emit_frame` from `uint8_t param_count` to `uint16_t` would require updating its signature in the header, the existing `LOG_ID_BYTES` forwarding call, and the Uno strong override — touching more files. The sibling function adds ~80 lines net but confines the change to files already being modified. Only one call-site (`eprom_operations.cpp`) uses the wide variant.

## Verification Results

- `pio run -e uno` — SUCCESS (23,000 B / 71.3% Flash, 1,593 B / 77.8% RAM)
- `pio run -e leonardo` — SUCCESS (25,194 B / 87.9% Flash, 1,563 B / 61.1% RAM)
- `pio test -e native -f "*test_messages*"` — 5/5 PASSED
- `pio test -e native -f "*test_dispatch*"` — 15/15 PASSED
- `python -m pytest tests/ -v` — 29/29 PASSED (25 decoder + 4 fw-guard)
- New tests: `test_data_chunk_payload_exposed_via_response_payload_field` PASSED; `test_chip_read_loop_concatenates_multiple_chunks` PASSED

**Post-plan assertion:** Every firmware state-machine ack is now an ID frame except MSG_OK_FW_VERSION (LFW-05 bootstrap). Phase 8 Success Criterion #2 ("firestarter write/read runs end-to-end with INIT/MAIN/END rendered from ID-frame decoding alone") is achieved.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] VPP/VPE catalog shape mismatch — pre-computed 4 u16 values**
- **Found during:** Task 2 analysis
- **Issue:** Plan said `LOG_DATA_ID_U16_U16(MSG_DATA_VPP_VOLTAGE, voltage_mv, vcc_mv)` (2 u16s = 4 bytes), but the Plan 01 catalog defines `params = [u16, u16, u16, u16]` (4 u16s = 8 bytes). Sending 4-byte params for an 8-byte catalog entry would cause `_decode_id_frame` to reject the frame via `param_bytes` shape check.
- **Fix:** Added `LOG_DATA_ID_U16x4` macro; firmware pre-computes `(voltage_mv+50)/1000`, `((voltage_mv+50)/100)%10` (and same for vcc_mv) before emitting — matching the existing catalog.
- **Files modified:** `firestarter/include/logging_id.h`, `firestarter/src/hardware_operations.cpp`
- **Commit:** `a44b911`, `ea2a3fb`

**2. [Rule 2 - Missing critical] Uno strong override for rurp_log_id_wide**
- **Found during:** Task 4 implementation
- **Issue:** The Uno has a strong override for `rurp_log_id` that applies the `com_mode` gate. Without a matching `rurp_log_id_wide` strong override, chip-read streaming on Uno would use the weak default which lacks the gate — potentially emitting on the data bus during programming.
- **Fix:** Added `rurp_log_id_wide` strong override in `uno_rurp_shield.cpp` with identical `com_mode` guard.
- **Files modified:** `firestarter/src/boards/uno_rurp_shield.cpp`
- **Commit:** `1abadaa`

## Known Stubs

None — all conversions wire to real catalog IDs; no placeholder text or empty data flows. `response_msg[0] = '\0'` clear sites in `firestarter.cpp` are intentionally preserved for Plan 06 deletion (documented in plan).

## Threat Flags

None — no new network endpoints, auth paths, or schema changes beyond what the plan's threat model anticipated. All mitigations (T-08-05-01 through T-08-05-05) implemented per plan.

## Self-Check: PASSED

- `firestarter/include/logging_id.h` — contains `#define LOG_OK_ID_U8_U8(` and `#define LOG_OK_ID_U8_U8_ASTR(`
- `firestarter/src/hardware_operations.cpp` — contains `LOG_OK_ID(MSG_OK_READY)` and `LOG_OK_ID_U8_U8(MSG_OK_REV` and `MSG_OK_CFG`
- `firestarter/src/firestarter.cpp` — contains `LOG_OK_ID_U8_U8_ASTR(MSG_OK_FW_HANDSHAKE`
- `firestarter/src/eprom_operations.cpp` — contains `MSG_DATA_CHUNK`
- `firestarter_app/firestarter/eprom_operations.py` — contains `MSG_DATA_CHUNK`
- `firestarter_app/firestarter/serial_comm.py` — contains `payload`
- All task commits present: `a44b911`, `ea2a3fb`, `0f3c08f`, `1abadaa`, `732e047`
