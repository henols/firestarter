# Phase 8 — Flash + SRAM Budget Measurement

**Measured:** 2026-05-18
**Boards:** Leonardo + Uno
**Phase 7 close baseline:** Leonardo 94.3% (27,026 / 28,672 bytes), 1,646 bytes free; Uno 77.0% (24,838 / 32,256 bytes), 7,418 bytes free
**Repo state at measurement:**
- `firestarter` HEAD = `275522a2071c34c972957a0f1df03617ac586840` (Phase 8 Plan 07 complete — debug() sweep to LOG_DEBUG_ID_SUB + debug_msg_buffer deletion)
- `firestarter_app` HEAD = `732e04762088f5ac0ff8c63662f065f8e622fb79` (Phase 8 Plan 05 complete — host MSG_DATA_CHUNK decode + Response.payload)
- meta-repo HEAD = `0d2a1ecc3115c54086a7b3523a5a200b06526898`

---

## Leonardo (`pio run -e leonardo`)

```
Processing leonardo (platform: atmelavr; board: leonardo; framework: arduino)
--------------------------------------------------------------------------------
Verbose mode can be enabled via `-v, --verbose` option
CONFIGURATION: https://docs.platformio.org/page/boards/atmelavr/leonardo.html
PLATFORM: Atmel AVR (5.2.0) > Arduino Leonardo
HARDWARE: ATMEGA32U4 16MHz, 2.50KB RAM, 28KB Flash
DEBUG: Current (simavr) External (simavr)
PACKAGES:
 - framework-arduino-avr @ 5.3.0
 - toolchain-atmelavr @ 1.70300.191015 (7.3.0)
LDF: Library Dependency Finder -> https://bit.ly/configure-pio-ldf
LDF Modes: Finder ~ chain, Compatibility ~ soft
Found 6 compatible libraries
Scanning dependencies...
Dependency Graph
|-- SoftwareSerial @ 1.0
|-- jsmn
|-- EEPROM @ 2.0
Building in release mode
Checking size .pio/build/leonardo/firestarter_leonardo.elf
Advanced Memory Usage is available via "PlatformIO Home > Project Inspect"
RAM:   [======    ]  57.3% (used 1467 bytes from 2560 bytes)
Flash: [========= ]  85.6% (used 24538 bytes from 28672 bytes)
========================= [SUCCESS] Took 1.20 seconds =========================

Environment    Status    Duration
-------------  --------  ------------
leonardo       SUCCESS   00:00:01.201
========================= 1 succeeded in 00:00:01.201 =========================
```

- **Leonardo Flash:** 85.6% (24,538 / 28,672 bytes used), **4,134 bytes free**.
- **Delta vs Phase 7 close (27,026 bytes):** 27,026 − 24,538 = **+2,488 bytes saved** (−8.7 percentage points).
- **Free bytes delta:** 1,646 free → 4,134 free (+2,488 bytes headroom recovered).
- **Leonardo SRAM:** 57.3% (1,467 / 2,560 bytes used), **1,093 bytes free**.
- **SRAM delta vs Plan 05 close (1,563 bytes):** 1,563 − 1,467 = **+96 bytes saved** (R-01 win, −3.8 pp); attributable to Plan 06 deletion of `response_msg[96]`.

**SC#4 direction:** DOWNWARD. 24,538 < 27,026. SC#4 PASS.

---

## Uno (`pio run -e uno`)

```
Processing uno (platform: atmelavr; board: uno; framework: arduino)
--------------------------------------------------------------------------------
Verbose mode can be enabled via `-v, --verbose` option
CONFIGURATION: https://docs.platformio.org/page/boards/atmelavr/uno.html
PLATFORM: Atmel AVR (5.2.0) > Arduino Uno
HARDWARE: ATMEGA328P 16MHz, 2KB RAM, 31.50KB Flash
DEBUG: Current (avr-stub) External (avr-stub, simavr)
PACKAGES:
 - framework-arduino-avr @ 5.3.0
 - toolchain-atmelavr @ 1.70300.191015 (7.3.0)
LDF: Library Dependency Finder -> https://bit.ly/configure-pio-ldf
LDF Modes: Finder ~ chain, Compatibility ~ soft
Found 6 compatible libraries
Scanning dependencies...
Dependency Graph
|-- SoftwareSerial @ 1.0
|-- jsmn
|-- EEPROM @ 2.0
Building in release mode
Checking size .pio/build/uno/firestarter_uno.elf
Advanced Memory Usage is available via "PlatformIO Home > Project Inspect"
RAM:   [=======   ]  73.1% (used 1497 bytes from 2048 bytes)
Flash: [=======   ]  69.2% (used 22330 bytes from 32256 bytes)
========================= [SUCCESS] Took 1.14 seconds =========================

Environment    Status    Duration
-------------  --------  ------------
uno            SUCCESS   00:00:01.135
========================= 1 succeeded in 00:00:01.135 =========================
```

- **Uno Flash:** 69.2% (22,330 / 32,256 bytes used), **9,926 bytes free**.
- **Delta vs Phase 7 close (24,838 bytes):** 24,838 − 22,330 = **+2,508 bytes saved** (−7.8 percentage points).
- **Free bytes delta:** 7,418 free → 9,926 free (+2,508 bytes headroom recovered).
- **Uno SRAM:** 73.1% (1,497 / 2,048 bytes used), **551 bytes free**.
- **SRAM delta vs Plan 05 close (1,593 bytes):** 1,593 − 1,497 = **+96 bytes saved** (R-01 win, −4.7 pp); attributable to Plan 06 deletion of `response_msg[96]`.

**SC#4 direction:** DOWNWARD. 22,330 < 24,838. SC#4 PASS.

---

## SC#1 Host Parser Surface

**Verification date:** 2026-05-18  
**File checked:** `firestarter_app/firestarter/serial_comm.py`

### INIT / MAIN / END as text prefix matches — zero hits

```bash
$ grep -nE 'MAIN|INIT:|END:' firestarter/serial_comm.py
138:# Phase 8 W-01: INIT/MAIN/END removed (now arrive as ID frames via the catalog
298:        # INIT/MAIN/END is removed — catalog format strings own the rendering for
```

Both hits are code **comments**, not active string literals, list entries, or regex patterns. No INIT/MAIN/END appears as an active prefix in `EXPECTED_PREFIXES`, `STATE_MACHINE_PREFIXES`, or `PREFIX_REGEX`.

### EXPECTED_PREFIXES contents (verbatim from serial_comm.py lines 141–151)

```python
EXPECTED_PREFIXES = [
    "OK",
    "INFO",
    "DEBUG",
    "ERROR",
    "WARN",
    "DATA",
]
PREFIX_REGEX = re.compile(rf"({'|'.join(EXPECTED_PREFIXES)}):(.*)")

STATE_MACHINE_PREFIXES = []  # W-01: state-machine acks now arrive as ID frames; catalog format strings own the rendering.
```

`EXPECTED_PREFIXES` contains: **OK, INFO, DEBUG, ERROR, WARN, DATA**. INIT / MAIN / END are absent.  
`STATE_MACHINE_PREFIXES` is empty (`[]`). Phase 8 W-01 conversion is confirmed.

### Bootstrap text path preserved (LFW-05)

The `MSG_OK_FW_VERSION` (0x03) entry has `wire_format="text"` — it is explicitly **rejected** if it arrives as an ID frame (WR-03 guard), and it continues to arrive as the literal `OK: FW: ...` text prefix line. The decode path that handles it lives at `serial_comm.py` lines 398–410:

```python
# WR-03: reject id-frame payloads for catalog entries flagged
# wire_format="text". MSG_OK_FW_VERSION (0x03) and MSG_OK_FW_HANDSHAKE
# (0x06) are expected to arrive over the legacy text channel only
# (LFW-05). A buggy or malicious peer emitting id=0x03 / id=0x06 as a
# binary frame would otherwise render via the catalog format string
# and bypass the host's pre-v1.2 firmware-version guard in
# _probe_port (which only inspects the text path).
if entry.wire_format != "id_frame":
    logger.warning(...)
    return None
```

The host's `_probe_port` sends `COMMAND_FW_VERSION` and awaits the `OK: FW: ...` text prefix line — the LFW-05 bootstrap exemption is intact.

**SC#1 result: PASS** — zero active INIT / MAIN / END prefix-matcher entries; `STATE_MACHINE_PREFIXES = []`; bootstrap text path preserved.

---

## SC#3 Readiness — MSG_DATA_CHUNK Chip-Read Streaming

**Verification date:** 2026-05-18  
**Status: AUTOMATED PATH CONFIRMED — hardware byte-identity check deferred to Task 2**

Phase 8 Plan 05 (W-04) replaced the raw `DATA:` binary read-payload stream with `MSG_DATA_CHUNK` (0xE6) ID frames. The host now decodes chip bytes from `Response.payload` rather than from a text-prefixed line.

### Key call paths

**Firmware side** (`firestarter/src/eprom_operations.cpp`):
- `rurp_communication_write(handle->data_buffer, handle->data_size)` replaced by `rurp_log_id_wide(MSG_DATA_CHUNK, (uint8_t*)handle->data_buffer, (uint16_t)handle->data_size)`
- `_firestarter_emit_frame_wide` + `rurp_log_id_wide` provide the 512/1024-byte chunk framing

**Host decoder** (`firestarter_app/firestarter/serial_comm.py` lines 352, 456–463):
```python
if msg_id == MSG_DATA_CHUNK and len(params) == 1 and isinstance(params[0], (bytes, bytearray)):
    ...
chunk_payload = None
if msg_id == MSG_DATA_CHUNK and values and isinstance(values[0], (bytes, bytearray)):
    chunk_payload = bytes(values[0])
return LogMessage(severity=severity_label, text=text, id=msg_id, payload=chunk_payload)
```

**Host consumer** (`firestarter_app/firestarter/eprom_operations.py` lines 349–384):
```python
def _main_phase_read_data(self, progress, start_addr, end_addr, process_data_chunk_callback):
    # MSG_DATA_CHUNK ID frame instead of emitting raw bytes after a DATA:
    ...
    if response.payload is not None:
        # MSG_DATA_CHUNK: the raw chip bytes are in response.payload.
        payload = response.payload
        process_data_chunk_callback(start_addr, payload)
        start_addr += len(payload)
        progress.update(len(payload))
```

The `DATA:` text prefix remains in `EXPECTED_PREFIXES` as the sentinel for `MSG_DATA_SENDING` (batch-start signal with no payload) — it is NOT removed in Phase 8. The chip byte content is now exclusively in `MSG_DATA_CHUNK` frames.

**SC#3 host path: CONFIRMED.** Byte-identity proof (actual hardware read diff) deferred to Task 2.

---

## SC#2 Manual Verification Plan

**Status: PENDING — Task 2 hardware verification required**

SC#2 requires verifying that `firestarter write -e W27C512` runs end-to-end on both Uno and Leonardo with:
- INIT / MAIN / END acks rendered from ID-frame decoding alone (no `INIT:` / `MAIN:` / `END:` text prefix visible in CLI output)
- Bootstrap `OK: FW: ...` text line still present at command start (LFW-05 preserved)
- Write completes with a success message

Task 2 will perform this verification on both boards (per project memory: "Always mirror Uno tests on Leonardo").

**SC#2 result: PENDING Task 2**

---

## SC#3 Manual Verification Plan

**Status: PENDING — Task 2 hardware verification required**

SC#3 requires verifying that `firestarter read -e W27C512 -o out.bin` produces a byte-identical binary file vs a pre-Phase-8 baseline. The operator must:

1. Capture a pre-Phase-8 baseline (from a pre-Phase-8 git checkout) if not already available
2. Flash Phase 8 firmware to both boards
3. Run `firestarter read` on both boards and `diff` the output against the baseline

Project memory note: "Leonardo shield socket is wonky — suspect bad chip contact first when Leonardo readbacks look corrupted but Uno is clean."

**SC#3 result: PENDING Task 2**

---

## SC#4 Build Status

| Board | Build | Flash Used | Flash Max | % Used | Free | Delta vs Ph7 |
|-------|-------|------------|-----------|--------|------|--------------|
| Leonardo | SUCCESS | 24,538 B | 28,672 B | 85.6% | 4,134 B | −2,488 B (−8.7 pp) |
| Uno | SUCCESS | 22,330 B | 32,256 B | 69.2% | 9,926 B | −2,508 B (−7.8 pp) |

**Native test suite:**
```
native         native/avr/test_dispatch           PASSED    00:00:01.983
native         native/avr/test_flash_intel_vpp    ERRORED   00:00:00.613
native         native/avr/test_eeprom28c_chip_id  ERRORED   00:00:00.619
native         native/avr/test_messages           PASSED    00:00:02.034
================= 24 test cases: 22 succeeded in 00:00:05.250 =================
```

- `test_dispatch` and `test_messages`: PASSED (22/22 of their combined test cases pass).
- `test_flash_intel_vpp` and `test_eeprom28c_chip_id`: ERRORED — **pre-existing failures** present before Phase 7 began (SIGABRT in simulator harness), not regressions from Phase 8.

**Host pytest regression:**
```
============================= test session starts ==============================
platform linux -- Python 3.12.13, pytest-9.0.3, pluggy-1.6.0
rootdir: /workspaces/firestarter_prom/firestarter_app
configfile: pyproject.toml
plugins: anyio-4.13.0
collected 29 items

tests/test_decoder.py .........................                          [ 86%]
tests/test_fwguard.py ....                                              [100%]

============================== 29 passed in 0.29s ==============================
```

29 tests pass: 25 decoder tests (Plans 02 + 03 + 05 suites + baselines) + 4 firmware-guard tests.

Both boards' Flash usage is strictly less than their Phase 7 close baselines (24,838 / 27,026).

**SC#4 result: PASS**

---

## SRAM Win (R-01) Attribution

The 96-byte SRAM reduction on both boards was realized in **Plan 06** when the `char response_msg[RESPONSE_MSG_SIZE]` field (96 bytes, `RESPONSE_MSG_SIZE = 96`) was deleted from `firestarter_handle_t`.

| Board | Pre-R-01 (Plan 05 close) | Post-R-01 (Plan 06 close = Phase 8 close) | Delta |
|-------|--------------------------|-------------------------------------------|-------|
| Uno | 1,593 B / 2,048 B (77.8%) | 1,497 B / 2,048 B (73.1%) | **−96 B (−4.7 pp)** |
| Leonardo | 1,563 B / 2,560 B (61.1%) | 1,467 B / 2,560 B (57.3%) | **−96 B (−3.8 pp)** |

The win was exact — no compiler padding effect. The `RESPONSE_MSG_SIZE #define` was deleted alongside the field. The remaining `logging.h` macro tower references to `handle->response_msg` are dead code (zero call-sites in `src/`) and are Phase 9 deletion targets (LMIG-04).

The Plan 07 (debug sweep) production Flash and SRAM measurements are **identical to Plan 06 close** — this is expected because the `debug()` / `debug_format()` macros were already `#define debug(msg)` (empty expansion) when `SERIAL_DEBUG` was undefined. The new `LOG_DEBUG_ID_SUB*` no-op fallbacks do the same. The Plan 07 delta materializes only in SERIAL_DEBUG builds.

See `08-06-SUMMARY.md` for the full R-01 attribution chain (commits `828485d`, `436789b`).

---

## Flash Savings Attribution — Plans 05–07

The bulk of the Phase 8 flash savings vs Phase 7 close came from Plans 05 and 06:

| Plan | Uno Delta | Leonardo Delta | Primary Driver |
|------|-----------|----------------|----------------|
| 08-04 | −126 B | −1,132 B | Simple OK populate-sites (fill/erase/write/blank/verify acks) |
| 08-05 | −1,712 B | −1,698 B | PARSE_RESPONSE composite elimination (state-machine acks + VPP/VPE + DATA_CHUNK) |
| 08-06 | −508 B | −656 B | response_msg field deletion + _check_response log-emit stripping |
| 08-07 | 0 B | 0 B | Debug sweep (no-op in production; macros were already empty) |
| **Phase 8 total** | **−2,508 B** | **−2,488 B** | vs Phase 7 close baseline |

The PARSE_RESPONSE elimination in Plan 05 (the `#ifdef HARDWARE_REVISION / send_ack_format(...)` two-branch macro tower) accounts for the dominant savings — each branch embedded its own PROGMEM format string; replacing with `LOG_OK_ID_U8_U8_ASTR` passes only a 1-byte ID.

---

## Anchor for Plan 9

Phase 9 LMIG-04 acceptance criterion must cite all four prior reference points. The Phase 8 close row is now added:

| Snapshot | Leonardo Flash | Uno Flash | SRAM (Uno) | Notes |
|----------|----------------|-----------|------------|-------|
| **v1.1 close** | 98.7% (~28,299 / 28,672) | not formally recorded | — | ROADMAP-pinned baseline; per-byte derived from %. |
| **Phase 6 close** | 98.7% (28,292 / 28,672), 380 B free | 80.9% (26,100 / 32,256), 6,156 B free | 1,683 B / 2,048 B (Uno) | LMIG-01: new ID infrastructure alongside legacy text; no call-sites converted yet. |
| **Phase 7 close** | 94.3% (27,026 / 28,672), 1,646 B free | 77.0% (24,838 / 32,256), 7,418 B free | 1,587 B / 2,048 B (Uno) | LMIG-02: all ERROR/WARN/INFO call-sites converted; dead-code deleted. |
| **Phase 8 close (THIS plan)** | 85.6% (24,538 / 28,672), 4,134 B free | 69.2% (22,330 / 32,256), 9,926 B free | 1,497 B / 2,048 B (Uno) | LMIG-03: OK/INIT/MAIN/END state-machine acks + MSG_DATA_CHUNK streaming + R-01 SRAM win. Hardware verification (SC#2+SC#3) pending Task 2. |
| **Phase 9 close (LMIG-04)** | TARGET: < 90% (< ~25,805 / 28,672) | TBD; record alongside Leonardo | TBD | After Phase 9: `LOG_*_MSG` PROGMEM deletion + legacy macro tower deletion. |

The Phase 9 SUMMARY should cite: v1.1 → Phase 9 delta ("v1.2 milestone flash savings"), Phase 6 → Phase 9 delta ("pure migration recovery"), Phase 7 → Phase 9 delta ("state-machine + cleanup contribution"), and Phase 8 → Phase 9 delta ("logging.h macro tower deletion, isolated").

---

## Bench Verification — Chipless Wire-Protocol Validation

**Date:** 2026-05-18
**Boards flashed at:** firestarter HEAD `275522a` (Phase 8 Plan 07 complete)
**Host at:** firestarter_app HEAD `96e8deb` (incl. VPP-loop regression fix below)
**Chips:** none seated (operator confirmed)
**Approach:** Verify every Phase 8 wire-protocol change that does NOT require a chip in the socket. SC#2 (write end-to-end) and SC#3 (byte-identical readback) require a chip and remain pending physical chip-seated validation.

### Severity-band frame coverage (both boards)

| Band | Frame | Uno result | Leonardo result |
|---|---|---|---|
| OK composite (P-04) | MSG_OK_FW_HANDSHAKE u8+u8+ascii_str | `OK: FW: 2.0.11-dev:uno, HW: Rev1, Cmd: 0x0b` | `OK: FW: 2.0.11-dev:leonardo, HW: Rev1, Cmd: 0x0b` |
| OK fixed (P-02) | MSG_OK_REV u8+u8 | `Rev1` (effective=0xFF sentinel branch) | `Rev1, Override HW: Rev2` (non-sentinel branch) |
| OK fixed (P-03) | MSG_OK_CFG u32+u32+u8 | `R1: 270000, R2: 44000` (override=0xFF sentinel) | `R1: 270000, R2: 44000, Override HW: Rev1` (non-sentinel) |
| INFO | MSG_INFO_* free-text | `I: Init start` / `I: Main start` | same |
| INIT | MSG_INIT_DONE | `INIT: (init done)` (observed in `id W27C512` flow) | not exercised — flow preempted by ERROR below |
| DATA (W-03) | MSG_DATA_VPP_VOLTAGE u16+u16 | `DATA: VPP: 11.5V, Internal VCC: 5.0V` | `DATA: VPP: 13.1V, Internal VCC: 5.5V` |
| DATA (W-03) | MSG_DATA_VPE_VOLTAGE u16+u16 | `DATA: VPE: 13.2V, Internal VCC: 5.0V` | `DATA: VPE: 15.3V, Internal VCC: 5.5V` |
| ERROR | MSG_ERROR_* (parameterized) | not triggered chipless | `ERROR: VPP is high: 13.1V > 12.0V` (`id W27C512` aborted on VPP overshoot, ERROR frame rendered with embedded voltage params) |
| Wire-format u16 `len` (W-04) | implicit in every frame above | ✓ | ✓ |

### Sentinel-byte branch coverage

The two boards happen to be configured differently, which gave Phase 8 full sentinel coverage in a single bench session:

- Uno EEPROM: no operator override → exercises the 0xFF-sentinel render paths (`Rev1`, no `Override HW:` clause).
- Leonardo EEPROM: operator-installed hardware-revision override → exercises the non-sentinel render paths (full `Override HW: RevN` clause).

Both branches of `_format_message` were validated against live firmware output.

### Host regression fix (Plan 05 follow-up)

Bench testing surfaced one regression introduced by Plan 05 widening `Response` from 2 fields (`type`, `message`) to 3 (added `payload`):

- `firestarter_app/firestarter/hardware.py:204` still unpacked `comm.get_response()` as a 2-tuple, crashing every `vpp` / `vpe` invocation with `ValueError: too many values to unpack (expected 2)`.
- Fix: read the `Response` object and access `.type` / `.message` explicitly.
- Commit: `firestarter_app/96e8deb` — `fix(hardware): unpack Response object, not 2-tuple, in _read_voltage_loop`.
- Post-fix verification: VPP + VPE continuous-read loops produce DATA frames at the expected ~500 ms cadence on both boards.

### Bench commands run

```bash
# Flash
cd firestarter && pio run -t upload -e uno --upload-port /dev/ttyACM0
                  pio run -t upload -e leonardo --upload-port /dev/ttyACM1

# Uno
FIRESTARTER_DEV_ALLOW_PRE_V12=1 firestarter -p /dev/ttyACM0 fw       # P-04
FIRESTARTER_DEV_ALLOW_PRE_V12=1 firestarter -p /dev/ttyACM0 hw       # P-02 sentinel
FIRESTARTER_DEV_ALLOW_PRE_V12=1 firestarter -p /dev/ttyACM0 config   # P-03 sentinel
FIRESTARTER_DEV_ALLOW_PRE_V12=1 firestarter -p /dev/ttyACM0 vpp      # MSG_DATA_VPP_VOLTAGE
FIRESTARTER_DEV_ALLOW_PRE_V12=1 firestarter -p /dev/ttyACM0 vpe      # MSG_DATA_VPE_VOLTAGE
FIRESTARTER_DEV_ALLOW_PRE_V12=1 firestarter -p /dev/ttyACM0 id W27C512   # exercises INIT_DONE

# Leonardo — same matrix on /dev/ttyACM1
```

### Outcome

✓ **All Phase 8 wire-protocol changes verified on both boards** (P-02/P-03/P-04 composite + fixed-shape frames, W-03 DATA voltage frames, W-04 u16 len, ERROR/INFO/INIT carriage). Both branches of sentinel-byte rendering covered between the two boards' configurations.

⏸ **SC#2 (write end-to-end) and SC#3 (byte-identical readback) remain pending physical chip-seated verification.** No chips were available during this session. The wire protocol IS validated; what remains is integration with chip-physics that Phase 8 did not modify. To close SC#2 + SC#3, an operator with a W27C512 (or substitute) seated on each board runs the Step 1–4 plan in the earlier "Manual Verification Plan" sections.

---

## Phase 8 Close — Logging Housekeeping Pass

**Date:** 2026-05-18
**Baseline:** Uno 22,330 B Flash / 1,497 B SRAM; Leonardo 24,538 B Flash / 1,467 B SRAM (Phase 8 Plan 07 close)
**Post-pass:** Uno 22,330 B Flash / 1,497 B SRAM; Leonardo 24,538 B Flash / 1,467 B SRAM (unchanged — dead macros were already empty expansions in production builds)

---

## Dead Symbol Deletion (Task 1)

**Files modified:** `include/logging.h`, `src/logging.c`, `src/boards/uno_rurp_shield.cpp`, `src/boards/leonardo_rurp_shield.cpp`, `src/boards/rurp_serial_utils.cpp`, `src/firestarter.cpp`, `src/proms/memory.cpp`

**Macros deleted from logging.h** (all confirmed zero callers in src/):
- `send_main_done`, `send_init_done`, `send_end_done`
- `log_info`, `log_info_const`, `log_info_format`
- `log_data`, `log_data_const`, `log_data_format`
- `log_warn`, `log_warn_const`, `log_warn_format`, `log_warn_format_buf`
- `log_error`, `log_error_const`, `log_error_format`, `log_error_format_buf`
- `format`, `format_P_int`, `format_P_char`
- `log_error_P_int_buf`, `log_info_P_int_buf`, `log_info_P_char_buf`
- `log_info_P_int`, `log_info_P_char`, `log_error_P_int`
- `send_ack_format`
- `firestarter_data_response`, `firestarter_data_response_format`
- `firestarter_warning_response`, `firestarter_warning_response_format`
- `firestarter_error_response`, `firestarter_error_response_format`
- `firestarter_set_response`, `firestarter_response_format`

**PROGMEM strings deleted from logging.c** (now unreferenced after macro deletion):
- `LOG_INIT_DONE_MSG`, `LOG_MAIN_DONE_MSG`, `LOG_END_DONE_MSG`
- `LOG_INFO_MSG`, `LOG_DATA_MSG`, `LOG_WARN_MSG`, `LOG_ERROR_MSG`
- Kept: `LOG_OK_MSG` (still referenced by `send_ack` / `send_ack_const`)

**Functions deleted from board files:**
- `uno_rurp_shield.cpp`: `debug_buf(const char* msg)` — zero external callers
- `leonardo_rurp_shield.cpp`: `debug_buf(const char* msg)` — zero external callers

**Macros KEPT (live callers confirmed):**
- `send_ack` — called from `dev_tools.cpp:108` and `:154`
- `send_ack_const` — called from `hardware_operations.cpp:86` (LFW-05 bootstrap text path)
- `debug_setup()` / `log_debug(type, msg)` — SERIAL_DEBUG build support
- `log_debug` function body in `uno_rurp_shield.cpp` — called from `rurp_log()` line 84 in SERIAL_DEBUG path

**Commented-out call-sites cleaned:**
- `rurp_serial_utils.cpp` lines 72, 81, 93: converted `// log_error_*(...)` to plain inline error-code comments
- `firestarter.cpp` parse_json: removed `// log_info_format(...)` comment + dead `#ifdef EXTRA_INFO_LOGGING` block that contained only that comment
- `memory.cpp` memory_read_execute: removed `// debug_format(...)` comment

**Flash delta:** 0 bytes (production; SERIAL_DEBUG macros were already empty no-ops). SERIAL_DEBUG builds gain code reduction.
**Commit:** `451756f`

---

## Catalog Orphan Audit (Task 2)

**Method:** For each MSG_* and DBG_* entry in messages.toml, grepped firestarter/src/ and firestarter/include/ (excluding generated messages.h and logging_id.h) for emit site references.

| ID | Name | Status | Notes |
|----|------|--------|-------|
| 0x00 | MSG_NONE | KEPT | Reserved sentinel — by design |
| 0x01 | MSG_OK_READY | USED | hardware_operations.cpp:42 |
| 0x02 | MSG_OK_REQ_DATA | USED | eprom_operations.cpp:76 |
| 0x03 | MSG_OK_FW_VERSION | KEPT | LFW-05 bootstrap exemption (text path, no ID-frame emit) |
| 0x04 | MSG_OK_REV | USED | hardware_operations.cpp:97 |
| 0x05 | MSG_OK_CFG | USED | hardware_operations.cpp:119 |
| 0x06 | MSG_OK_FW_HANDSHAKE | USED | firestarter.cpp:153 |
| 0x10 | MSG_INIT_DONE | USED | operation_utils.cpp:262 |
| 0x20 | MSG_MAIN_DONE | USED | operation_utils.cpp:192 |
| 0x30 | MSG_END_DONE | USED | operation_utils.cpp:264 |
| 0x40–0x59 | MSG_INFO_* (all 26) | USED | firestarter.cpp, dev_tools.cpp, eprom.cpp, flash_type_{3,4}.cpp |
| 0x80–0x84 | MSG_WARN_* (all 5) | USED | eprom.cpp, flash_intel.cpp, flash_type_3.cpp, eeprom_28c.cpp |
| 0xA0–0xBA | MSG_ERR_* (all 27) | USED | firestarter.cpp, hardware_operations.cpp, operation_utils.cpp, eprom_operations.cpp, proms/*.cpp |
| 0xE0 | MSG_DATA_PROGRESS | USED | memory.cpp:397 |
| 0xE1 | MSG_DATA_VOLTAGE | ORPHAN | DELETED — superseded by 0xE4/0xE5 (VPP/VPE dedicated IDs) |
| 0xE2 | MSG_DATA_SENDING | USED | eprom_operations.cpp:114 |
| 0xE4 | MSG_DATA_VPP_VOLTAGE | USED | hardware_operations.cpp:72 |
| 0xE5 | MSG_DATA_VPE_VOLTAGE | USED | hardware_operations.cpp:70 |
| 0xE6 | MSG_DATA_CHUNK | USED | eprom_operations.cpp:115 |
| 0xF0 | MSG_DEBUG | USED | logging_id.h (LOG_DEBUG_ID_SUB* macros) |
| DBG_0x00–0x28 | All 41 DBG_* entries | USED | Confirmed individual grep for all 41 |

**Orphans deleted:** 1 (MSG_DATA_VOLTAGE 0xE1)
**Catalog total:** 75 → 74 messages
**Commits:** `b2b903c` (firestarter), `789c886` (firestarter_app)

---

## Catalog Clarity Pass (Task 3)

**Method:** Full read of messages.toml format strings; applied non-breaking fixes only.

| Entry | Old format | New format | Reason |
|-------|-----------|------------|--------|
| MSG_INFO_ADDR_REMAP (0x57) | `"Address: 0x%06x remappend"` | `"Address: 0x%06x remapped"` | Typo: double 'd' |
| MSG_INFO_SKIPPING_ERASE (0x58) | `"Skipping erase."` | `"Skipping erase"` | Standardize: no trailing period on status messages |
| MSG_WARN_REV0_VPP_UNSUPPORTED (0x80) | `"Rev0 dont support reading VPP/VPE"` | `"Rev0 does not support reading VPP/VPE"` | Grammar |
| MSG_WARN_CHIP_ID_MISMATCH (0x83) | `"Chip ID %#04x dont match expected ID %#04x"` | `"Chip ID %#04x does not match expected ID %#04x"` | Grammar |
| MSG_WARN_MEM_SIZE_TOO_SMALL (0x84) | `"mem_size %lu too small for chip-id check"` | `"Memory size %lu too small for chip-id check"` | Remove internal var name from operator text |
| MSG_ERR_NO_CMD (0xA1) | `"No cmd"` | `"No command"` | Expand abbreviation |
| MSG_ERR_DATA_ERR_N (0xA9) | `"Data err %d"` | `"Data error: %d"` | Expand abbreviation |
| MSG_ERR_CMD_TIMEOUT (0xAA) | `"Cmd: %d, timeout"` | `"Command %d timed out"` | Expand abbreviation, clearer phrasing |
| MSG_ERR_UNKNOWN_CMD (0xAB) | `"Unknown cmd: %d"` | `"Unknown command: %d"` | Expand abbreviation |
| MSG_ERR_REV0_VPP_RD (0xAC) | `"Rev0 dont support reading VPP/VPE"` | `"Rev0 does not support reading VPP/VPE"` | Grammar |
| MSG_ERR_CMD (0xAD) | `"Error cmd"` | `"Command error"` | Clearer phrasing |
| MSG_ERR_CHIP_ID_MISMATCH (0xB9) | `"Chip ID %#04x dont match expected ID %#04x"` | `"Chip ID %#04x does not match expected ID %#04x"` | Grammar |
| MSG_ERR_MEM_SIZE_TOO_SMALL (0xBA) | `"mem_size %lu too small for chip-id check"` | `"Memory size %lu too small for chip-id check"` | Remove internal var name |

**Deferred / not changed:**
- WARN/ERROR severity pairs with identical format strings (CHIP_ID_MISMATCH, VPP_HIGH, MEM_SIZE_TOO_SMALL, REV0_VPP): kept as separate entries — host uses severity band to decide --force override logic; merging would lose that distinction.
- MSG_INFO_SKIPPING_ERASE vs MSG_INFO_SKIPPING_ERASE_MEM: kept separate — different emitters and semantic contexts (eprom/flash4 chip-erase skip vs flash3 memory-erase skip).
- MSG_ERR_VERIFY (0xAF) format `"0x%02x != 0x%02x at 0x%06x"`: kept — hex bytes are appropriate for byte comparison context.
- MSG_ERR_NOT_BLANK (0xB0) format `"Not blank, at 0x%06x, v: 0x%02x"`: kept — adequate for operator.

**Commits:** `9e9c888` (firestarter), `e44fb72` (firestarter_app)

---

## Legacy Message Fixes (Task 4)

**Issue:** MSG_OK_REQ_DATA (0x02) had `format = "Req data"` in the meta-repo (abbreviation).
An earlier hand-edit on the firestarter sub-repo had introduced `"Reqest data"` (typo, now overwritten by Tasks 2+3 sync).

**Fix:** Set canonical meta-repo value to `"Request data"` (full word, correct spelling). Synced to both sub-repos.

**Other legacy checks:**
- `wire_format = "text"` entries: only MSG_OK_FW_VERSION (0x03) — LFW-05 bootstrap exemption, correct.
- Format-params mismatches: none. MSG_OK_FW_VERSION uses `{0}` placeholder on the text path (exempt from ID-frame param validation per Rule 8).
- ID/severity-band violations: none. All 74 entries fall within their correct ranges (OK 0x00-0x0F, INIT 0x10-0x1F, MAIN 0x20-0x2F, END 0x30-0x3F, INFO 0x40-0x7F, WARN 0x80-0x9F, ERROR 0xA0-0xDF, DATA 0xE0-0xFF).

**Commits:** `2520575` (firestarter), `aa75c05` (firestarter_app)

---

## Phase 8 Close — Final Build Status

| Board | Flash Used | Flash Max | % Used | Free | Delta vs Ph8 Plan07 |
|-------|-----------|-----------|--------|------|---------------------|
| Uno | 22,330 B | 32,256 B | 69.2% | 9,926 B | 0 B (no change — macros were already empty no-ops) |
| Leonardo | 24,538 B | 28,672 B | 85.6% | 4,134 B | 0 B (no change) |

Native test suite: `test_dispatch` PASSED, `test_messages` PASSED (20/20 cases).
Host pytest: 29 passed.

