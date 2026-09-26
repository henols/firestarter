---
phase: 08-convert-state-machine-prefix-call-sites-ok-init-main-end
verified: 2026-05-18T00:00:00Z
status: human_needed
score: 3/4 must-haves verified
overrides_applied: 0
carry_over_assessment:
  assessed: 2026-08-09
  by: v1.31 pre-close carry-over sweep
  status_unchanged: human_needed
  reason_still_open: "Residual is hardware-only and Uno-side. NOT rubber-stamped."
  scope_reduced: true
  protocol_assertion: SATISFIED
  protocol_assertion_evidence: |
    08-HUMAN-UAT.md Test 1, bench session 2026-06-16 (Leonardo /dev/ttyACM0, W27C512
    seated, fw b8): "PHASE-08 DELIVERABLE VERIFIED WORKING: all acks render via ID-frame
    decoding with NO literal INIT:/MAIN:/END: text prefixes; bootstrap
    OK: FW: 3.0.0b8:leonardo shown. The SC#2 *protocol* assertion is satisfied."
  original_blocker: MSG_ERR_EMPTY_INPUT (0xA4) during the write MAIN phase
  original_blocker_status: RESOLVED (outside Phase 08, as the 2026-06-16 disposition intended)
  original_blocker_fix: |
    Host-side: INIT/END phases must not ack DATA frames. Present in the v1.31 tree at
    firestarter_app/firestarter/eprom_operations.py:488 (`ack_data=False`), with the
    documented contract at :497-501 and the regression guard
    tests/test_eprom_operations.py:135 test_init_phase_data_frames_not_acked.
  leonardo_leg: SUPERSEDED by later chip-seated evidence
  leonardo_leg_evidence: |
    Phase 91 (v1.16) graduated W27C512 to PASS with a full erase-enabled write+verify
    on Leonardo (chip-ID 0xDA08, erase SHA e16b2a5b) after proving the earlier failure
    was a `write -b` skip-erase test-method error, not a code fault. Phase 73 bench-
    validated the 6 families on Leonardo. v1.21 validated 3 boards.
  residual_open:
    - "SC#2/SC#3 on an **Uno** (not Leonardo) — never performed on any board of that class"
    - "SC#3 explicit `diff baseline.bin readback.bin` byte-identity check, on either board"
  recommended_disposition: |
    Close the Leonardo leg on the Phase 91 evidence and decide the Uno leg on policy:
    the project's standing bench posture is Leonardo-only validity (uno328pb is recorded
    bench-unstable, and Uno-class boards drive the shield bus during upload). If Uno-class
    bench validation is out of posture, this should be closed as such rather than left
    open indefinitely. OPERATOR DECISION — not taken here.
human_verification:
  - test: "Flash Phase 8 firmware (firestarter HEAD 275522a) to Uno, then run: FIRESTARTER_DEV_ALLOW_PRE_V12=1 firestarter write -e W27C512 -i <known.bin>. Confirm write completes with INIT/MAIN/END acks rendered without literal text prefixes and bootstrap OK: FW: ... line is still present."
    expected: "CLI output shows INIT/MAIN/END phase transitions through catalog-rendered format strings (e.g. 'INIT: (init done)'), no raw 'INIT:'/'MAIN:'/'END:' text prefixes, and 'OK: FW: ...' bootstrap line present at start."
    why_human: "SC#2 requires end-to-end write with a chip seated. No chips were available during the bench session (per 08-MEASUREMENT.md). Wire-protocol changes are confirmed; chip-physics integration requires hardware."
  - test: "After the write test above, run: FIRESTARTER_DEV_ALLOW_PRE_V12=1 firestarter read -e W27C512 -o /tmp/ph8-uno-out.bin. Diff against a pre-Phase-8 baseline: diff /tmp/ph8-uno-out.bin <baseline.bin>. Repeat on Leonardo."
    expected: "diff exits 0 (byte-identical file contents). Both Uno and Leonardo reads produce the same chip bytes as the pre-Phase-8 baseline."
    why_human: "SC#3 requires a chip-seated byte-identity check. The MSG_DATA_CHUNK streaming path was verified in simulation (host tests pass) but byte-identity on real hardware requires a chip seated on each board."
---

# Phase 8: Convert State-Machine Prefix Call-Sites Verification Report

**Phase Goal:** The firmware emits OK: / INIT: / MAIN: / END: state-machine acks as ID-encoded frames via rurp_log_id, and the host parser switches from line-prefix matching to ID-frame decoding for those acks. The DATA: binary read-payload stream prefix marker remains a literal text prefix (explicitly out of scope per the locked v1.2 constraints). After this phase the only text-formatted log surface left in firmware is the bootstrap 'OK: FW: ...' version handshake response (per LFW-05).
**Verified:** 2026-05-18
**Status:** human_needed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|---------|
| 1 | SC#1: Only DATA: and bootstrap OK: FW: remain as line-prefix-matched entries; INIT/MAIN/END decoded exclusively as ID frames | ✓ VERIFIED | EXPECTED_PREFIXES = ["OK","INFO","DEBUG","ERROR","WARN","DATA"]; INIT/MAIN/END absent. STATE_MACHINE_PREFIXES = []. struct.unpack_from(">H", len_bytes) reads u16 frame len. test_decoder.py 25/25 pass including test_init_done_arrives_as_id_frame, test_main_done_arrives_as_id_frame, test_end_done_arrives_as_id_frame. |
| 2 | SC#2: firestarter write -e W27C512 runs end-to-end with INIT/MAIN/END rendered from ID-frame decoding alone | ? UNCERTAIN | Wire-protocol validated on bench with chipless boards (08-MEASUREMENT.md §Bench Verification). Firmware emits MSG_INIT_DONE/MSG_MAIN_DONE/MSG_END_DONE via LOG_INIT_ID/LOG_MAIN_ID/LOG_END_ID. Host decodes via _decode_id_frame. Full write end-to-end with chip seated not completed due to no chip available at bench session. |
| 3 | SC#3: firestarter read -e W27C512 -o out.bin produces byte-identical readback vs pre-Phase-8 baseline | ? UNCERTAIN | MSG_DATA_CHUNK streaming path exists and passes all 29 host tests (including test_chip_read_loop_concatenates_multiple_chunks). Byte-identity diff on real hardware not completed; no chip seated during bench session. |
| 4 | SC#4: pio run -e leonardo and pio run -e uno both compile, firmware binary measurably smaller than Phase 7 baseline | ✓ VERIFIED | Leonardo: 24,538 bytes (85.6%) vs Phase 7 27,026 bytes (94.3%) = -2,488 bytes. Uno: 22,330 bytes (69.2%) vs Phase 7 24,838 bytes (77.0%) = -2,508 bytes. Both strictly below baseline. |

**Score:** 2/4 truths fully verified (SC#1 + SC#4 VERIFIED; SC#2 + SC#3 UNCERTAIN — pending hardware)

### Deferred Items

No items deferred to later phases. SC#2 and SC#3 are hardware-integration checks that the phase itself documents as pending (not deferred to a later phase — they are part of this phase's close criteria).

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `tools/catalog/messages.toml` | MSG_DATA_VPP_VOLTAGE, MSG_DATA_VPE_VOLTAGE, MSG_DATA_CHUNK, MSG_DEBUG, [debug] section with DBG_* entries, reshaped OK_REV/OK_CFG/FW_HANDSHAKE | ✓ VERIFIED | wire_format="text" preserved on MSG_OK_FW_VERSION; MSG_OK_FW_HANDSHAKE has wire_format="id_frame"; [debug] section present |
| `tools/catalog/codegen.py` | DBG_* emit, DEBUG_CATALOG dict emit, [debug] section parsing | ✓ VERIFIED | DEBUG_CATALOG present in messages.py output; 41 DBG_* defines in messages.h |
| `firestarter/include/messages.h` | MSG_DATA_VPP_VOLTAGE, MSG_DATA_CHUNK, MSG_DEBUG, DBG_* defines | ✓ VERIFIED | DBG_FIRESTARTER_STARTED through DBG_* range (0x00..0x28) present; MSG_DATA_CHUNK 0xE6 present |
| `firestarter_app/firestarter/messages.py` | DEBUG_CATALOG dict, new MSG_* constants | ✓ VERIFIED | DEBUG_CATALOG: dict[int, MessageDef] at line 256; MSG_DATA_VPP_VOLTAGE/VPE/CHUNK/DEBUG all present |
| `firestarter/src/boards/rurp_serial_utils.cpp` | u16 big-endian len field (len_u16), _firestarter_emit_frame_wide for large payloads | ✓ VERIFIED | len_u16 at line 177; _firestarter_emit_frame_wide (uint16_t param_count) at line 208; guard 65533 at line 165 |
| `firestarter_app/firestarter/serial_comm.py` | struct.unpack_from(">H") for u16 frame_len, STATE_MACHINE_PREFIXES=[], INIT/MAIN/END removed from EXPECTED_PREFIXES, sentinel-byte handling for P-02/P-03/P-04 | ✓ VERIFIED | struct.unpack_from(">H", len_bytes) at line 538; STATE_MACHINE_PREFIXES = [] at line 161; MSG_OK_REV/CFG/FW_HANDSHAKE sentinel branches at lines 334-352 |
| `firestarter_app/tests/conftest.py` | struct.pack(">H", length) for u16 len in build_frame | ✓ VERIFIED | struct.pack(">H", length) at line 63 |
| `firestarter_app/tests/test_decoder.py` | test_init_done_arrives_as_id_frame, test_fw_handshake_p04_*, test_ok_rev_p02_*, test_ok_cfg_p03_*, test_data_chunk_body_over_253_bytes_decodes | ✓ VERIFIED | All tests present and passing (25/25 pass) |
| `firestarter/include/logging_id.h` | LOG_OK_ID_*, LOG_INIT_ID_*, LOG_MAIN_ID_*, LOG_END_ID_*, LOG_DATA_ID_*, LOG_DATA_ID_U16_U16, LOG_DATA_ID_U32_U32, LOG_OK_ID_U8_U8, LOG_OK_ID_U8_U8_ASTR, LOG_DEBUG_ID_SUB* (#ifdef SERIAL_DEBUG gated) | ✓ VERIFIED | 8 LOG_OK_ID_* macros, 6 each for INIT/MAIN/END/DATA; LOG_DATA_ID_U32_U32 and LOG_DATA_ID_U16_U16 present; LOG_DATA_ID_U16x4 (4-param VPP/VPE variant); LOG_OK_ID_U8_U8 and LOG_OK_ID_U8_U8_ASTR present; LOG_DEBUG_ID_SUB family with #ifdef SERIAL_DEBUG gating (18 macros: 9 emit + 9 no-op) |
| `firestarter/src/operation_utils.cpp` | LOG_MAIN_ID(MSG_MAIN_DONE), LOG_INIT_ID(MSG_INIT_DONE), LOG_END_ID(MSG_END_DONE); _check_response with log_info/log_data stripped | ✓ VERIFIED | Lines 184, 254, 256 have the three LOG_*_ID macros; _check_response has RESPONSE_CODE_OK/DATA cases without any log_info/log_data calls |
| `firestarter/src/hardware_operations.cpp` | LOG_OK_ID(MSG_OK_READY), LOG_DATA_ID_U16x4(MSG_DATA_VPP/VPE_VOLTAGE), LOG_OK_ID_U8_U8(MSG_OK_REV), LOG_ID_BYTES(MSG_OK_CFG, _cfg, 9); send_ack_const(FW_VERSION) preserved | ✓ VERIFIED | All four conversion sites confirmed; send_ack_const(FW_VERSION) at line 86 (LFW-05 preserved) |
| `firestarter/src/firestarter.cpp` | LOG_OK_ID_U8_U8_ASTR(MSG_OK_FW_HANDSHAKE, ...) replacing PARSE_RESPONSE composite | ✓ VERIFIED | Line 153; no PARSE_RESPONSE or send_ack_format found |
| `firestarter/src/eprom_operations.cpp` | MSG_DATA_CHUNK via rurp_log_id_wide; legacy send_ack_const/log_data_const converted | ✓ VERIFIED | rurp_log_id_wide(MSG_DATA_CHUNK, ...) at line 120; LOG_OK_ID(MSG_OK_REQ_DATA) at line 76; LOG_DATA_ID(MSG_DATA_SENDING) at line 119 |
| `firestarter_app/firestarter/eprom_operations.py` | MSG_DATA_CHUNK ID-frame decode loop; response.payload extraction | ✓ VERIFIED | _main_phase_read_data uses response.payload for MSG_DATA_CHUNK frames (lines 353-384) |
| `firestarter/include/firestarter.h` | response_msg field absent; RESPONSE_MSG_SIZE absent | ✓ VERIFIED | Neither response_msg nor RESPONSE_MSG_SIZE found in firestarter.h or any src/ files |
| `.planning/phases/08-.../08-MEASUREMENT.md` | Phase-close measurement artifact; 50+ lines; SC#1/SC#4 verified; SC#2/SC#3 marked pending | ✓ VERIFIED | 387 lines; SC#1 and SC#4 marked PASS; SC#2/SC#3 marked PENDING Task 2 |
| `firestarter_app/firestarter/serial_comm.py` | Response.payload field on namedtuple | ✓ VERIFIED | Response = namedtuple('Response', ['type', 'message', 'payload'], defaults=[None]) at line 40 |

### Key Link Verification

| From | To | Via | Status | Details |
|------|-----|-----|--------|---------|
| `tools/catalog/messages.toml` | `firestarter/include/messages.h` | codegen.py --language cpp | ✓ WIRED | MSG_DATA_VPP_VOLTAGE, DBG_* defines present in messages.h |
| `tools/catalog/messages.toml` | `firestarter_app/firestarter/messages.py` | codegen.py --language python | ✓ WIRED | DEBUG_CATALOG dict + MSG_DATA_VPP_VOLTAGE present in messages.py |
| `firestarter/src/boards/rurp_serial_utils.cpp` | `firestarter_app/firestarter/serial_comm.py` | u16 big-endian len field | ✓ WIRED | Firmware writes 2 bytes MSB+LSB (len_u16); host reads 2 bytes and struct.unpack_from(">H") |
| `firestarter/src/operation_utils.cpp` | `firestarter_app/firestarter/serial_comm.py` | MSG_MAIN_DONE/INIT_DONE/END_DONE catalog severity routing | ✓ WIRED | LOG_*_ID macros emit ID frames that _decode_id_frame routes by CATALOG[msg_id].severity |
| `firestarter/src/firestarter.cpp` | `firestarter_app/firestarter/serial_comm.py` | MSG_OK_FW_HANDSHAKE composite frame (P-04) | ✓ WIRED | LOG_OK_ID_U8_U8_ASTR emits; _format_message sentinel branch handles params; P-04 tests pass |
| `firestarter/src/eprom_operations.cpp` | `firestarter_app/firestarter/eprom_operations.py` | MSG_DATA_CHUNK streaming (W-04) | ✓ WIRED | rurp_log_id_wide(MSG_DATA_CHUNK,...) emits; _main_phase_read_data reads response.payload |
| `firestarter_app/tests/conftest.py` | `firestarter_app/tests/test_decoder.py` | build_frame helper (u16 len) | ✓ WIRED | struct.pack(">H", length) in build_frame; used by all 25 decoder tests |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|----------|--------------|--------|-------------------|--------|
| `serial_comm.py` _read_and_parse_lines | frame_len (u16) | struct.unpack_from(">H", len_bytes) from serial | Yes — decodes real wire bytes from pyserial connection | ✓ FLOWING |
| `eprom_operations.py` _main_phase_read_data | response.payload | decoded MSG_DATA_CHUNK frame via serial_comm.get_response() | Yes — payload extracted from real ID frame params[0] | ✓ FLOWING |
| `serial_comm.py` _format_message | sentinel branches | msg_id == MSG_OK_REV/CFG/FW_HANDSHAKE; params[N] == 0xFF check | Yes — branches produce rendered text from real decoded param bytes | ✓ FLOWING |
| `operation_utils.cpp` _check_response | response_code | handle->response_code set by firmware operation callbacks | Yes — drives real operation flow; rurp_communication_write on DATA | ✓ FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Host decoder tests all pass (25 tests) | cd firestarter_app && python -m pytest tests/test_decoder.py -v | 25 passed in 0.27s | ✓ PASS |
| All host tests pass (29 tests) | cd firestarter_app && python -m pytest tests/ -v | 29 passed in 0.28s | ✓ PASS |
| INIT/MAIN/END absent from EXPECTED_PREFIXES | grep '"INIT"\|"MAIN"\|"END"' firestarter_app/firestarter/serial_comm.py \| grep -v '#' | No output (zero hits) | ✓ PASS |
| STATE_MACHINE_PREFIXES empty | grep "STATE_MACHINE_PREFIXES = \[\]" firestarter_app/firestarter/serial_comm.py | 1 match at line 161 | ✓ PASS |
| u16 len in host decoder | grep 'struct.unpack_from.*">H"' firestarter_app/firestarter/serial_comm.py | Match at line 538 | ✓ PASS |
| len_u16 in firmware emit | grep 'len_u16' firestarter/src/boards/rurp_serial_utils.cpp | Match at line 177 | ✓ PASS |
| LOG_DEBUG_ID_SUB gated by SERIAL_DEBUG | grep '#ifdef SERIAL_DEBUG' firestarter/include/logging_id.h | Match at line 262 | ✓ PASS |
| No legacy debug() call-sites remain | grep -rcE 'debug\(\|debug_format\(' firestarter/src/ | Only logging.h (2 hits — dead macro bodies in LOG_*_MSG macros, no src/ calls) and uno_rurp_shield.cpp (log_debug helper definition — different symbol) | ✓ PASS |
| response_msg field deleted | grep -rn "response_msg" firestarter/include/firestarter.h firestarter/src/firestarter.cpp firestarter/src/operation_utils.cpp | Zero hits in all three files | ✓ PASS |
| FW binary smaller than Phase 7 baseline | 08-MEASUREMENT.md §SC#4 | Uno 22,330 < 24,838; Leonardo 24,538 < 27,026 | ✓ PASS |

### Probe Execution

Step 7c: SKIPPED — no probe scripts discovered under scripts/*/tests/probe-*.sh for this phase. Phase 08-08-PLAN.md Task 1 ran automated checks during execution; results are in 08-MEASUREMENT.md.

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|------------|-------------|--------|---------|
| LMIG-03 | 08-01 through 08-08 | Phase C: OK/INIT/MAIN/END call-sites converted; host parser switches from line-prefix to ID-frame decoding; DATA: prefix stays text | ✓ SATISFIED | EXPECTED_PREFIXES no longer contains INIT/MAIN/END; all state-machine acks emit via LOG_*_ID macros; host decodes via _decode_id_frame; DATA: remains in EXPECTED_PREFIXES; REQUIREMENTS.md marks LMIG-03 as [x] Complete |

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `firestarter/include/logging.h` | 102, 108, 181 | copy_to_buffer macro references in dead macro bodies (format_P_int, format_P_char, firestarter_set_response) | INFO | Dead code — copy_to_buffer has no definition in any header/source file; the macros that reference it (firestarter_set_response, format_P_int, format_P_char) have zero callers in src/. This is Phase 9 cleanup target (LMIG-04). The undefined copy_to_buffer does NOT cause compile errors because the macros containing it are never expanded. Builds succeed (SC#4 verified). |
| `firestarter/include/logging.h` | 30-37 | Legacy send_main_done/send_init_done/send_end_done macro definitions (rurp_log_P path) still present | INFO | Zero call-sites in src/ (operation_utils.cpp converts to LOG_MAIN_ID etc. in Plan 04). Definitions remain as dead code. Phase 9 deletion target per Plan 06 scope note. |

No TBD, FIXME, or XXX markers found in any phase-modified source file.

### Human Verification Required

#### 1. SC#2: write end-to-end with chip seated

**Test:** Flash Phase 8 firmware (firestarter HEAD 275522a) to Uno. Seat a W27C512 chip. Run: `FIRESTARTER_DEV_ALLOW_PRE_V12=1 firestarter write -e W27C512 -i <known.bin> 2>&1 | tee /tmp/ph8-08-uno-write.txt`. Repeat on Leonardo. Inspect CLI output.

**Expected:** Write completes with a success message. INIT/MAIN/END acks appear without literal "INIT:"/"MAIN:"/"END:" text prefixes — they are rendered by catalog format strings (e.g. "INIT: (init done)" from MSG_INIT_DONE format string). The bootstrap "OK: FW: ..." text line appears at command start (LFW-05 preserved). No raw binary bytes in CLI output.

**Why human:** SC#2 requires a chip seated in the socket. No chips were available during the Phase 8 bench session (per 08-MEASUREMENT.md §Bench Verification). The wire-protocol (INIT/MAIN/END as ID frames) was exercised chipless via `firestarter id W27C512` which exercises INIT_DONE (documented in §Bench Verification table — "INIT_DONE observed in id W27C512 flow"). Full write with multiple MAIN acks and chip-programming cycles requires a chip.

#### 2. SC#3: byte-identical read vs pre-Phase-8 baseline

**Test:** After SC#2 write, run: `FIRESTARTER_DEV_ALLOW_PRE_V12=1 firestarter read -e W27C512 -o /tmp/ph8-uno-out.bin`. If no pre-Phase-8 baseline exists, capture one first (git stash to a pre-Phase-8 SHA, flash old firmware, read, restore Phase 8 firmware). Run: `diff /tmp/ph8-uno-out.bin <baseline.bin>`. Repeat on Leonardo. Note: if Leonardo readback looks corrupted, suspect the wonky Leonardo shield socket first (per project memory).

**Expected:** diff exits 0 on both boards. MSG_DATA_CHUNK streaming delivers byte-identical chip content vs the pre-Phase-8 raw-bytes path.

**Why human:** Byte-identity check requires a chip seated. The MSG_DATA_CHUNK path is fully wired and tested (29 host tests pass including test_chip_read_loop_concatenates_multiple_chunks), but the integration with real chip-physics read timing has not been exercised without a chip in the socket.

### Gaps Summary

No FAILED gaps. SC#2 and SC#3 are UNCERTAIN (not FAILED) because:

1. The wire-protocol changes Phase 8 introduced were exercised on live hardware in a chipless bench session (08-MEASUREMENT.md §Bench Verification): P-02/P-03/P-04 frames, W-03 voltage frames, W-04 u16 len, INIT frame observed via `firestarter id W27C512` flow.
2. The MSG_DATA_CHUNK streaming is fully implemented and tested (both directions) with 29 passing host tests.
3. The reason for not-yet-completed hardware verification is physical availability of test chips — not a code defect.

The phase orchestrator acknowledged this explicitly in the ROADMAP success criteria note: "Treat SC#2 and SC#3 as 'pending operator hardware run with chip seated' — verifiable, but blocked on bench access, not on Phase 8 code defects."

---

_Verified: 2026-05-18_
_Verifier: Claude (gsd-verifier)_
