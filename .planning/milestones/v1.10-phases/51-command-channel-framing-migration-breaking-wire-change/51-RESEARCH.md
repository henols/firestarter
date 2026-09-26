# Phase 51: Command-Channel Framing Migration (breaking wire change) — Research

**Researched:** 2026-06-02
**Domain:** Dual-repo serial protocol migration — COBS command-frame ingest (firmware C++), COBS command-frame emission (Python host)
**Confidence:** HIGH

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **D-01** No interop machinery — the framed protocol is the ONLY supported protocol. No capability
  negotiation, no dual-protocol/fallback support, no runtime handshake byte beyond what already exists.
  A mismatched old↔new pair simply fails (CMD_TIMEOUT or opaque frame decode error) — that is acceptable.
- **D-02** The breaking nature is documented for the beta cut (MILESTONES / READMEs note this is a
  breaking wire change; upgrade both repos in lockstep). Documentation is the SC3 guard equivalent.
- **D-04** The version probe (`CMD_FW_VERSION`) is framed like every other command. No unframed
  plaintext escape hatch — no chicken-and-egg problem because D-01 removes all obligation to old peers.
  The fw→host version response stays text (out of scope per ADR §4.2).
- **D-05** The `{`-peek / discard-non-`{` command-ingest loop (`firestarter.cpp` lines 162-172) is
  **deleted outright**. Firmware command ingest accepts ONLY COBS frames.
- **D-06** On COBS-decode or CRC8 failure: drain bytes up to and including the next `0x00` (resync),
  surface the existing error path immediately (fail-fast). Add a max-frame-size cap (`CMD_FRAME_MAX`),
  sized for the largest legitimate JSON command, to bound a stalled partial frame. No new idle timer.
- **Frame contract** `[COBS-encoded(JSON payload + CRC8 byte)][0x00 delimiter]` (ADR §4.1/§4.3).
  CRC8-CCITT poly 0x07, seed 0x00, no reflection, no final XOR. Same contract as Phase-50 data path.
- **CRC8-before-parse mandate** (V5 / §4.4): a frame that passes COBS delimiter but fails CRC8 is
  discarded — its bytes do NOT reach `json_parser.c`.
- **Full-frame consumption** (SAFE-01 sub-claim C): firmware frame decoder MUST consume the entire
  frame including the terminating `0x00` before calling the JSON parser.
- **Atomic single-write** (SAFE-01 sub-claim B): entire framed command assembled as one `bytes` object,
  passed to `send_bytes()` in a single call. Split-write of the delimiter is forbidden.
- **Dual-repo lockstep mandate**: `rurp_serial_utils.cpp`/`firestarter.cpp` (fw) ↔
  `serial_comm.py`/`frame_parser.py` (host) change together on branch `v1.10-serial-transport-hardening`.

### Claude's Discretion

- Exact firmware command-frame receive-buffer strategy (decode in place vs small dedicated buffer),
  provided the no-second-large-buffer / Uno-RAM constraint is respected.
- The concrete value/name of the max-frame-size cap (`CMD_FRAME_MAX`), sized from the largest
  legitimate command JSON with margin.
- Whether to bump the host version-floor constant (D-03) — incidental, planner's call.
- Placement/reuse of the COBS-decode + CRC8 helpers shared with the Phase-50 data path.
- Exact firmware/host symbol names for the new framed command encode/decode functions.

### Deferred Ideas (OUT OF SCOPE)

- Capability negotiation / dual-protocol support / runtime interop guard — explicit non-goal (D-01).
- Framing the fw→host command-response direction (`OK:`/`ERROR:`/`DATA:` + log/telemetry) — ADR §4.2
  freezes Framing 4 UNCHANGED.
- Block-level retransmit / ACK on the command channel — D-06 chose fail-fast.
- Full byte-compat round-trip / lockstep contract tests (Phase 52).
- Bench verification (Phase 53).
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| FRAME-05 | Host→firmware JSON command channel migrated to COBS framing layer — firmware decodes frame, verifies CRC8, hands payload to JSON parser; legacy `{`-peek path replaced. Breaking wire change, lockstep upgrade. | §Standard Stack (reusable primitives), §Firmware Command-Ingest Mechanics, §Host Encode Path, §CMD_FRAME_MAX Sizing all directly enable implementation. |
| CRC-01 | CRC8-CCITT retained unchanged on every framed payload, including the command channel. | D-05 lock confirmed — CRC8 table and `_crc8_ccitt()` are already shared; Phase 51 reuses them verbatim. Closed by FRAME-05. |
</phase_requirements>

---

## Summary

Phase 51 is a mechanical code migration, not a design problem. The COBS frame contract,
CRC8 polynomial, resync posture, and atomic-write mandate are all locked by the Phase-49
ADR. The Phase-50 primitives — `rurp_communication_read_data()` (firmware COBS decode-in-place +
CRC8 verify + drain-to-`0x00`), `cobs_encode`/`cobs_decode` (host), `_crc8_ccitt()` (host),
and `crc8_ccitt` PROGMEM accessor (firmware) — are proven and reused verbatim.

**The primary open questions are implementation mechanics,** not design choices:

1. The `CMD_IDLE` ingest loop (`firestarter.cpp` lines 162-172) currently peeks for `{`
   then calls `init_programmer()`, which itself calls the blocking
   `rurp_communication_read_bytes(handle->data_buffer, DATA_BUFFER_SIZE)`. The new loop
   replaces this two-call chain with a single COBS frame accumulator that calls
   `rurp_communication_read_data()` directly (the Phase-50 decoder already exists as
   the right function to call).

2. `CMD_FRAME_MAX` sizing is driven by a survey of actual commands: the largest legitimate
   JSON command is ~422 bytes in the absolute worst case (full bus-config, max-width
   integers). A cap of 512 bytes (= `DATA_BUFFER_SIZE`) is conservative, fits existing
   firmware RAM, and is a natural constant.

3. The host `send_json_command()` change is exactly three lines: compute CRC8 over the
   JSON bytes, encode with `cobs_encode(payload + bytes([crc]))`, emit one `send_bytes()`
   with the body + `b'\x00'` delimiter.

The only structural subtlety is the non-blocking accumulation contract for `CMD_IDLE`:
because `rurp_communication_read_data()` is itself a blocking loop (it spins on
`rurp_communication_available()` until the delimiter), the ingest in `CMD_IDLE` should
call it directly once bytes are available — mirroring the existing pattern where the `{`-peek
triggers `init_programmer()`. The accumulation-across-loop-iterations concern in D-06 is
handled by `rurp_communication_read_data()`'s internal spin, plus the `CMD_FRAME_MAX` cap
bounding pathological inputs.

**Primary recommendation:** Reuse `rurp_communication_read_data()` verbatim as the command-frame
decoder; remove the `{`-peek/discard branch from `CMD_IDLE`; replace `init_programmer()`'s
`rurp_communication_read_bytes` call with data already in `handle->data_buffer` filled by the
new frame-decode step.

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| COBS frame emission (host→fw) | Host (Python CLI) | — | `send_json_command()` in `serial_comm.py` assembles and writes the framed command |
| COBS frame reception + decode | Firmware (Arduino C++) | — | `CMD_IDLE` loop accumulates bytes and decodes via `rurp_communication_read_data()` |
| CRC8-before-parse enforcement | Firmware (Arduino C++) | — | Decoder verifies CRC8 before handing decoded buffer to `parse_json()` — V5 mandate |
| Resync / size-cap on command channel | Firmware (Arduino C++) | — | `_drain_to_delimiter()` (Phase 50, already in `rurp_serial_utils.cpp`) + `CMD_FRAME_MAX` cap |
| COBS encode helpers | Host frame_parser.py | Firmware rurp_serial_utils.cpp | `cobs_encode`/`cobs_decode` (host) and `rurp_communication_read_data` (fw) already exist |
| Version-floor version-check (D-03) | Host (Python CLI) | — | Optional bump to `_validate_firmware_version()` floor in `serial_comm.py` |
| Constant parity (`CMD_FRAME_MAX`) | `firestarter.h` + `constants.py` | — | CLAUDE.md constant-parity requirement — define in both, change both together |

---

## Standard Stack

### Core — Reuse verbatim from Phase 50 (no new libraries)

| Symbol | Repo / File | Phase-50 Line(s) | Purpose in Phase 51 |
|--------|-------------|-----------------|---------------------|
| `rurp_communication_read_data(char* buffer)` | `firestarter/src/boards/rurp_serial_utils.cpp` | 100-191 | **Decode command frame** — COBS decode-in-place + CRC8 verify + `_drain_to_delimiter()` on error. Returns payload length (≥0) or negative error code. |
| `_drain_to_delimiter()` | `firestarter/src/boards/rurp_serial_utils.cpp` | 88-98 | Internal; called by `rurp_communication_read_data` on failure. Also directly usable if Phase 51 adds an outer size-cap drain path. |
| `crc8_ccitt(uint8_t crc, uint8_t b)` | `firestarter/src/boards/rurp_serial_utils.cpp` | 312-314 (PROGMEM table 293-310) | Incremental CRC8 accumulator — used internally by `rurp_communication_read_data`. No need to call directly unless Phase 51 computes CRC separately. |
| `rurp_communication_available()` | `firestarter/src/boards/rurp_serial_utils.cpp` | 28-30 | Guards the `CMD_IDLE` byte-check before calling the frame decoder |
| `cobs_encode(payload: bytes) -> bytes` | `firestarter_app/firestarter/frame_parser.py` | 58-100 | Encode JSON + CRC8 byte before emission on host |
| `cobs_decode(encoded: bytes) -> bytes` | `firestarter_app/firestarter/frame_parser.py` | 103-128 | Not directly needed for Phase 51 host-side (host only encodes); present for Phase 52 round-trip tests |
| `_crc8_ccitt(data: bytes) -> int` | `firestarter_app/firestarter/frame_parser.py` | 50-55 | Compute CRC8 over raw JSON payload before wrapping in COBS frame |

**No new packages, no new framing algorithm.** [VERIFIED: live source read]

### Supporting — Existing firmware read helpers (unchanged)

| Symbol | File | Lines | Role |
|--------|------|-------|------|
| `rurp_communication_read()` | `rurp_serial_utils.cpp` | 32-34 | Single-byte UART read — used internally by `rurp_communication_read_data()` |
| `rurp_communication_peak()` | `rurp_serial_utils.cpp` | 36-38 | Peek without consuming — **deleted from CMD_IDLE** per D-05; the frame decoder does not need peek |
| `rurp_communication_read_bytes()` | `rurp_serial_utils.cpp` | 40-42 | Blocking `readBytes` — **deleted from `init_programmer()`** (replaced by frame decoder output) |
| `parse_json(handle)` | `firestarter/src/firestarter.cpp` | 52-107 | Unchanged JSON parser entry point; Phase 51 changes its *caller*, not the function itself |
| `init_programmer(handle)` | `firestarter/src/firestarter.cpp` | 109-144 | Needs internal surgery: remove `rurp_communication_read_bytes` call (line 113), rely instead on data already placed in `handle->data_buffer` by the new frame decoder step in the `CMD_IDLE` loop |
| `send_bytes(data_bytes: bytes) -> int` | `firestarter_app/firestarter/serial_comm.py` | 134-148 | Unchanged — already performs atomic `write()`+`flush()`. Phase 51 passes the complete frame here. |

---

## Package Legitimacy Audit

No external packages are installed by Phase 51. All COBS/CRC8 code is hand-rolled in-repo
(per REQUIREMENTS.md: "REJECT all off-the-shelf libraries"). No audit table required.

---

## Architecture Patterns

### System Architecture Diagram

```
HOST (Python)                                    FIRMWARE (Arduino C++)
─────────────────────────────────────────────────────────────────────
send_json_command(cmd_dict)
  │
  ├─ json.dumps(cmd_dict)  → raw_json (bytes)
  ├─ _crc8_ccitt(raw_json) → crc8 (1 byte)
  ├─ cobs_encode(raw_json + bytes([crc8])) → body (bytes, no 0x00)
  ├─ frame = body + b'\x00'
  └─ send_bytes(frame)  [one atomic write + flush]
       │
       ╔═══════════════ 250000-baud serial ══════════════════╗
       ║  [COBS body bytes...][0x00]                         ║
       ╚═════════════════════════════════════════════════════╝
                                                              │
                               loop() CMD_IDLE:               │
                               if (rurp_communication_available() > 0)
                                 │
                                 ▼
                               rurp_communication_read_data(handle->data_buffer)
                               ┌────────────────────────────────────────────┐
                               │ spin: read bytes until 0x00                │
                               │ COBS decode-in-place → data_buffer[0..N-1] │
                               │ CRC8 verify (V5 / §4.4)                   │
                               │   FAIL → _drain_to_delimiter() + error     │
                               │   PASS → return payload length N           │
                               └────────────────────────────────────────────┘
                                 │ N ≥ 0
                                 ▼
                               handle->data_size = N
                               handle->data_buffer[N] = '\0'
                               parse_json(handle)  [unchanged]
                                 │
                                 ▼
                               init_programmer(handle)  [OK ack emitted]
                                 │
                                 ▼
                               loop() dispatches CMD_READ/CMD_WRITE/etc.
```

**Error path:** if `rurp_communication_read_data()` returns negative → surface existing error
(`MSG_ERR_BAD_FRAME` or reuse existing `MSG_ERR_EMPTY_INPUT`/`MSG_ERR_BAD_JSON`) →
`handle->cmd` stays `CMD_IDLE` → loop continues.

### Recommended Project Structure (no new files required)

```
firestarter/
├── src/
│   ├── firestarter.cpp            ← CMD_IDLE loop surgery (lines 162-172 replaced)
│   │                                  init_programmer() line 113 surgery
│   └── boards/
│       └── rurp_serial_utils.cpp  ← no changes (decoder already built in Phase 50)
├── include/
│   └── firestarter.h              ← add CMD_FRAME_MAX constant
└── test/
    └── native/avr/
        └── test_cobs_cmd_frame/   ← NEW PlatformIO test directory (per CLAUDE.md pattern)
            ├── test_cobs_cmd_frame.cpp
            └── host_stubs.cpp

firestarter_app/
├── firestarter/
│   ├── serial_comm.py             ← send_json_command() wrapped + probe path (D-04)
│   ├── frame_parser.py            ← no changes (cobs_encode/_crc8_ccitt already built)
│   └── constants.py               ← add CMD_FRAME_MAX mirror constant
└── tests/
    └── test_serial_comm.py        ← extend with framed send_json_command tests
```

### Pattern 1: CMD_IDLE Frame-Ingest Loop (firmware)

**What:** Replace the `{`-peek / discard-non-`{` branch with a single call to the existing
`rurp_communication_read_data()` when bytes are available.

**Current code (lines 161-174 of `firestarter.cpp` — to DELETE):**
```c
} else if (handle.cmd == CMD_IDLE) {
    if (rurp_communication_available() > 0) {
        if (rurp_communication_peak() == '{') {      // DELETE: peek/branch
            if (init_programmer(&handle)) {
                return;
            }
        } else {
            rurp_communication_read();  // Discard non-'{' character  // DELETE
        }
    }
    return;
}
```

**New code (Phase 51):**
```c
} else if (handle.cmd == CMD_IDLE) {
    if (rurp_communication_available() > 0) {
        // Phase 51: COBS frame decoder replaces {-peek path (D-05).
        // rurp_communication_read_data() spins until 0x00 delimiter,
        // COBS-decodes in-place, verifies CRC8, drains on error (D-06).
        int n = rurp_communication_read_data(handle.data_buffer);
        if (n > 0 && n <= CMD_FRAME_MAX) {
            handle.data_size = (uint32_t)n;
            handle.data_buffer[n] = '\0';
            if (init_programmer_framed(&handle)) {    // see Pattern 3
                return;
            }
        } else if (n == 0 || n < 0) {
            // Decode failure or empty frame: _drain_to_delimiter() already
            // called inside rurp_communication_read_data(); surface error.
            LOG_ERROR_ID(MSG_ERR_BAD_FRAME);  // or reuse MSG_ERR_EMPTY_INPUT
        }
        // n > CMD_FRAME_MAX: oversized, drain already done, fall through
    }
    return;
}
```
[VERIFIED: live source read of firestarter.cpp lines 157-175]

**Key integration note:** `rurp_communication_read_data()` already handles the drain-to-delimiter
on any COBS or CRC8 failure (Pattern 3 from Phase-50 PATTERNS.md). No additional drain logic is
needed in the `CMD_IDLE` handler. The size-cap (D-06) is enforced by checking `n <= CMD_FRAME_MAX`
after the call returns — if `rurp_communication_read_data()` returns `-2` (overflow, drain already
done) the existing negative-return path fires. [VERIFIED: rurp_serial_utils.cpp lines 113-116, 128-130]

### Pattern 2: `init_programmer()` Surgery (firmware)

**What:** Remove the `rurp_communication_read_bytes()` call from `init_programmer()`. The function
currently reads the command data itself (line 113). After Phase 51, the data is already in
`handle->data_buffer` (filled by the CMD_IDLE frame decoder before `init_programmer()` is called).

**Current `init_programmer()` lines 109-125 (the surgery target):**
```c
bool init_programmer(firestarter_handle_t* handle) {
    handle->response_code = RESPONSE_CODE_OK;
    handle->operation_state = 0;

    handle->data_size = rurp_communication_read_bytes(  // ← DELETE THIS LINE
        handle->data_buffer, DATA_BUFFER_SIZE);          // ← DELETE THIS LINE
    handle->ctrl_flags = 0x80;
    LOG_DEBUG_ID_SUB_U16(DBG_BUFFER_SIZE, (uint16_t)handle->data_size);
    if (handle->data_size == 0) { ... }
    handle->data_buffer[handle->data_size] = '\0';      // ← already done in CMD_IDLE
    if (!parse_json(handle)) { return false; }
    ...
```

**After Phase 51:** `init_programmer()` receives `handle` with `data_buffer` and `data_size`
already populated and NUL-terminated. Remove lines 113-114; the `data_size == 0` guard is
retained (it now catches the `n == 0` empty-frame edge). The function can be renamed to
`init_programmer_framed()` or kept as `init_programmer()` — planner's discretion on symbol name.
[VERIFIED: live source read of firestarter.cpp lines 109-144]

### Pattern 3: Host `send_json_command()` Wrap (Python)

**What:** Extend `send_json_command()` to wrap the JSON payload in a COBS frame before sending.
The existing `send_bytes()` + `flush()` at line 141 is UNCHANGED — only the data passed to it
changes.

**Current code (lines 155-159 of `serial_comm.py` — to modify):**
```python
def send_json_command(self, command_dict: dict) -> int:
    """Serialise `command_dict` as compact JSON and send it over the serial port."""
    self._log_command_details(command_dict)
    json_data = json.dumps(command_dict, separators=(",", ":"))
    return self.send_string(json_data)            # ← plain text, no framing
```

**After Phase 51:**
```python
def send_json_command(self, command_dict: dict) -> int:
    """Serialise `command_dict` as a COBS+CRC8 framed command (Phase 51 / FRAME-05).

    Frame contract (ADR §4.1/§4.3):
        [COBS(json_bytes + CRC8(json_bytes))][0x00]

    The full frame is assembled as one bytes object and passed to send_bytes()
    in a single call (SAFE-01 sub-claim B atomic-write mandate).
    """
    self._log_command_details(command_dict)
    json_bytes = json.dumps(command_dict, separators=(",", ":")).encode("ascii")
    crc = _crc8_ccitt(json_bytes)
    body = cobs_encode(json_bytes + bytes([crc]))
    frame = body + b"\x00"                       # atomic: one bytes object
    return self.send_bytes(frame)
```

**Required imports to add:** `cobs_encode` from `firestarter.frame_parser` (already imported
for `_crc8_ccitt` — just extend the from-import). [VERIFIED: serial_comm.py lines 47-53]

**Sub-claim B compliance:** `frame` is a single `bytes` object. `send_bytes()` calls
`self.connection.write(frame)` followed by `self.connection.flush()`. The entire frame including
the trailing `0x00` is covered by the single flush. [VERIFIED: serial_comm.py lines 140-141]

### Pattern 4: Version Probe Framing (D-04)

The `CMD_FW_VERSION` probe in `_probe_port()` (line 550) uses:
```python
communicator.send_json_command({"state": COMMAND_FW_VERSION})
```

After Phase 51, `send_json_command()` wraps ALL commands — including this probe — in a COBS frame.
No special handling is needed; D-04 is satisfied automatically when `send_json_command()` is
updated. The fw→host response (`OK: FW: <version>` text line) is UNCHANGED (out of scope). The
two `expect_ack()` calls that follow (lines 554-565) remain valid — they read text responses via
the existing `_read_and_parse_lines` path. [VERIFIED: serial_comm.py lines 547-601]

### Anti-Patterns to Avoid

- **Keeping `rurp_communication_read_bytes` in `init_programmer()`:** It reads raw bytes without
  COBS framing and will hang or mis-decode if the host sends a framed command. Delete this call.
- **Re-adding `{`-peek as a fallback:** D-05 explicitly forbids any raw `{` path. Even a dev/debug
  escape hatch reintroduces a CRC-less ingest path violating the CRC8-before-parse mandate.
- **Split-write of the delimiter:** SAFE-01 sub-claim B mandates one `bytes` object. Do not do
  `send_bytes(body); send_bytes(b'\x00')` — this leaves a window between writes.
- **Calling `parse_json()` before checking the decode return:** If `rurp_communication_read_data()`
  returns a negative code, the data_buffer contents are undefined/corrupt. Must gate on `n > 0`.
- **Reusing `readBytes` in the new ingest loop:** The `read()`/`available()` byte-by-byte pattern
  used by `rurp_communication_read_data()` is correct; `readBytes` is the old blocking-without-COBS
  path. Don't mix them.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| COBS decode on firmware | Custom command-channel COBS decoder | `rurp_communication_read_data()` (already in `rurp_serial_utils.cpp`) | Phase 50 built and proven this; decode-in-place, CRC8 verify, drain-to-delimiter — all correct |
| COBS encode on host | Custom command-channel encoder | `cobs_encode()` (already in `frame_parser.py`) | Phase 50 built and tested this; 254-run edge, no-`0x00`-in-body invariant proven |
| CRC8 computation | New CRC routine | `_crc8_ccitt()` (host) / `crc8_ccitt()` firmware PROGMEM table | Polynomial is locked (D-05/CRC-01); table already exists in both repos |
| Drain-to-delimiter on error | New drain loop | `_drain_to_delimiter()` helper in `rurp_serial_utils.cpp` | Already exists from Phase 50; called internally by `rurp_communication_read_data()` on any failure |
| Size-cap accumulator | A separate byte-accumulation buffer | Read via `rurp_communication_read_data()` which returns -2 on overflow | The existing overflow guard (return -2 + internal drain) handles the size-cap case |

**Key insight:** Every Phase 51 primitive is a call-site change, not a new algorithm. The planner
should structure tasks as "update caller X to call existing function Y" rather than "implement Z".

---

## CMD_FRAME_MAX Sizing

**Survey of all host→firmware JSON commands (from `serial_comm.py`, `eprom_operations.py`, `hardware.py`):**

| Command | JSON Keys | Typical Size | Max Size |
|---------|-----------|-------------|---------|
| `CMD_FW_VERSION` (`{"state":13}`) | 1 | 12 B | 12 B |
| `CMD_HW_VERSION` (`{"state":15}`) | 1 | 12 B | 12 B |
| `CMD_CONFIG` (read: `{"state":14}`) | 1 | 12 B | 12 B |
| `CMD_CONFIG` (write: + r1/r2/rev/flags) | 4 | ~50 B | ~60 B |
| `CMD_READ_VPP`/`CMD_READ_VPE` | 1 | 12 B | 12 B |
| `CMD_DEV_REGISTERS` (`{"cmd":8,"flags":N}`) | 2 | ~25 B | ~30 B |
| `CMD_WRITE`/`CMD_READ`/`CMD_VERIFY` (with full bus-config) | ~12 + 20-element array | ~300 B | **~422 B** |

**Worst-case measured:** `{"cmd":2,"type":1,"algorithm":7,"memory-size":4294967295,"vpp_mv":12000,"pulse-delay":65535,"chip-id":65535,"pin-count":40,"flags":255,"address":4294967295,"read_settling_us":65535,"read_strobe_us":65535,"bus-config":{"address_lines":[100,...119],"address_mask":4294967295,"matching_lines":20,"rw_line":100,"vpp_line":100,"static_high_mask":4294967295}}` = **422 bytes** [VERIFIED: measured in devcontainer Python]

**COBS overhead on 422-byte payload + 1 CRC byte = 423 bytes:** maximum +2 run-code bytes
(⌈423/254⌉ = 2 run blocks) → worst-case encoded body ≤ 425 bytes + 1 delimiter = 426 bytes.
This fits well within `DATA_BUFFER_SIZE=512`.

**Recommendation:** `CMD_FRAME_MAX 512` (= `DATA_BUFFER_SIZE`). Rationale:
- 422 bytes worst-case payload + 90 bytes headroom = natural ceiling
- Equals existing `DATA_BUFFER_SIZE` — reuses an existing named constant, no new RAM
- The COBS decoder already returns `-2` and drains when the decoded payload would exceed
  `DATA_BUFFER_SIZE`; setting `CMD_FRAME_MAX = DATA_BUFFER_SIZE` means checking `n <= CMD_FRAME_MAX`
  in `CMD_IDLE` is always satisfied for any frame the decoder accepted — it degrades to a
  documentation/symmetry constant rather than an independent check
- **Alternative interpretation:** `CMD_FRAME_MAX` can be defined as the COBS-encoded frame size
  cap (426 bytes + 1 = 427) for an outer reject-before-decode path, but since
  `rurp_communication_read_data()` already enforces the decoded-payload cap internally, the
  simpler approach is to use `DATA_BUFFER_SIZE` as the sentinel and gate on the decoded length.

The planner should define `CMD_FRAME_MAX` in `firestarter.h` and mirror it in `constants.py`
per CLAUDE.md constant-parity requirements. [VERIFIED: CLAUDE.md + constants.py pattern]

---

## Firmware Command-Ingest Mechanics — Deep Trace

### Current `CMD_IDLE` path (what gets deleted)

`firestarter.cpp` lines 161-174 [VERIFIED: live source]:
1. `rurp_communication_available() > 0` — byte-availability guard
2. `rurp_communication_peak() == '{'` — peek for JSON start marker
3. If yes → `init_programmer(&handle)` → internally calls `rurp_communication_read_bytes(
   handle->data_buffer, DATA_BUFFER_SIZE)` (blocking, reads up to 512 bytes, returns when
   count reached or timeout) → then `parse_json()`
4. If no → `rurp_communication_read()` (discard the non-`{` byte)

**Problem with the legacy path:** `rurp_communication_read_bytes` calls `SERIAL_PORT.readBytes()`
which is a blocking call with an internal `timeout` (Arduino's `Stream::readBytes`). It is NOT
a COBS-aware reader and would mis-interpret a COBS-encoded frame (the first byte of a COBS body
is a run-length code, never `{`).

### New `CMD_IDLE` path (what Phase 51 builds)

1. `rurp_communication_available() > 0` — byte-availability guard (unchanged)
2. Call `rurp_communication_read_data(handle.data_buffer)` — this spins internally until
   the `0x00` delimiter arrives (or error), decodes COBS in-place into `handle.data_buffer`,
   verifies CRC8, drains on error. Returns decoded length or negative.
3. On `n > 0`: `handle.data_size = n`, `handle.data_buffer[n] = '\0'`, call `init_programmer_framed()`
   (or restructured `init_programmer()` that skips the old `readBytes` call).
4. On `n <= 0`: log error, stay in `CMD_IDLE`.

**Non-blocking question (D-06):** The current `rurp_communication_read_data()` spins on
`while (rurp_communication_available() <= 0) {}` inside the decode loop. This means once the
`CMD_IDLE` guard fires (bytes available), the decoder spins until the full frame arrives —
it does NOT return mid-frame for other loop work. This is the SAME behavior as the current
`rurp_communication_read_bytes` blocking call. There is no regression and no new blocking
behavior. The existing `TIMEOUT_MS` op-level timer is for the CMD != CMD_IDLE case
(line 158-160 of `firestarter.cpp`); it does not fire during CMD_IDLE. The size-cap
(D-06) is the defense against a frame whose `0x00` never arrives: the decoder accumulates
bytes and returns `-2` (overflow) when `DATA_BUFFER_SIZE` would be exceeded (since the logical
stream = payload + CRC, and the PUSH macro drains + returns -2 on buffer full). [VERIFIED: rurp_serial_utils.cpp lines 110-121]

### `init_programmer()` after Phase 51

After Phase 51, `init_programmer()` receives a handle with:
- `handle->data_buffer` — decoded JSON payload (NUL-terminated)
- `handle->data_size` — decoded length

Remove line 113 (`rurp_communication_read_bytes` call). The NUL-termination (`handle->data_buffer[n] = '\0'`) is done in `CMD_IDLE` before calling `init_programmer_framed()`. The rest of `init_programmer()` from line 115 onward is unchanged. [VERIFIED: firestarter.cpp lines 109-144]

---

## Runtime State Inventory

Phase 51 is a wire-protocol migration, not a rename/refactor. No stored data, live service config, OS-registered state, secrets, or build artifacts reference the command-channel format — the format is stateless per-connection. Applies: **omitted per phase type**.

---

## Common Pitfalls

### Pitfall 1: Leaving `rurp_communication_read_bytes` in `init_programmer()`

**What goes wrong:** If `init_programmer()` still calls `rurp_communication_read_bytes()` after
the `CMD_IDLE` loop calls `rurp_communication_read_data()`, the blocking `readBytes` runs on an
already-consumed RX buffer and hangs forever (or times out reading zero bytes).

**Why it happens:** `init_programmer()` currently combines "read bytes" + "parse JSON". The surgery
must separate the two responsibilities — read is now done in `CMD_IDLE`, parse remains in
`init_programmer()`.

**How to avoid:** Replace or remove lines 112-114 of `firestarter.cpp`. The simplest approach is
an `init_programmer_framed()` function that starts at line 115 (after `data_size` and `data_buffer`
are already set). Alternatively, keep `init_programmer()` and add a `bool from_frame` parameter
that skips the read.

**Warning signs:** Firmware hangs after the first framed command in bench test (Phase 53).

### Pitfall 2: CRC8 computed over the COBS-encoded body instead of the raw JSON

**What goes wrong:** If the host computes `crc = _crc8_ccitt(body)` instead of
`crc = _crc8_ccitt(json_bytes)` before COBS encoding, the CRC byte embedded in the frame
does not match what the firmware recomputes over the decoded payload. Every command fails CRC8
verification.

**Why it happens:** The ADR §4.3 is explicit: "CRC8 byte... computed over the raw payload bytes
only; appended after payload, before COBS encoding." But it is easy to compute CRC after encoding
if the order is not carefully followed.

**How to avoid:** In `send_json_command()`: (1) compute `_crc8_ccitt(json_bytes)`, (2) then
`cobs_encode(json_bytes + bytes([crc]))`. Never swap steps 1 and 2.

### Pitfall 3: `parse_json()` called on a CRC-failed / negative-return frame

**What goes wrong:** If the caller calls `parse_json()` unconditionally after the decoder returns,
a garbled or partially-decoded buffer reaches `jsmn_parse()`. Depending on buffer contents this
may parse garbage as a valid command or trigger a null-pointer operation.

**Why it happens:** Negative return codes from `rurp_communication_read_data()` are easy to miss
if the guard is written as `if (n >= 0)` vs `if (n > 0)`.

**How to avoid:** Gate strictly on `n > 0` before proceeding to `init_programmer_framed()`. A
zero-length decoded payload is not a valid JSON command either.

**Warning signs:** Firmware emits `MSG_ERR_BAD_JSON` or `MSG_ERR_NO_CMD` immediately after a
corrupted frame.

### Pitfall 4: Version-probe double-frame (D-04 chicken-and-egg confusion)

**What goes wrong:** A developer adds a special-case `if cmd == CMD_FW_VERSION: send_string(raw_json)`
bypass in `send_json_command()`, believing the probe must be unframed to bootstrap the handshake.

**Why it happens:** D-04 is non-obvious — without reading the context it looks like there should
be a chicken-and-egg problem.

**How to avoid:** D-04 resolves this: there is no old peer to be compatible with (D-01). Both
the new host and new firmware speak COBS from byte 1. The probe is wrapped in `send_json_command()`
like every other command. No special-case path needed.

### Pitfall 5: New PlatformIO test directory not added to `test_filter`

**What goes wrong:** Placing `test_cobs_cmd_frame.cpp` under a new directory without updating
`platformio.ini`'s `test_filter` → the suite is silently not run by `pio test -e native`.

**Why it happens:** PlatformIO requires an explicit `test_filter` allowlist (confirmed in Phase 50
Plan 01 deviation note).

**How to avoid:** Add `native/avr/test_cobs_cmd_frame` to both the `test_filter` list and the
`build_flags` `-I` include path in `platformio.ini`. [VERIFIED: platformio.ini lines 78-92]

### Pitfall 6: Oversize command detection — misunderstanding what `rurp_communication_read_data` returns

**What goes wrong:** The decoder returns `-2` when the decoded payload would overflow
`DATA_BUFFER_SIZE` (it drains internally and returns). The `CMD_IDLE` handler may misinterpret
this as an empty input rather than an oversize frame, emitting a misleading `MSG_ERR_EMPTY_INPUT`.

**How to avoid:** Use a dedicated `MSG_ERR_BAD_FRAME` error ID (or distinguish `-1`, `-2`, `-3`,
`-4` return codes for logging). The existing negative-code contract (callers check `res < 0` only)
means the distinction doesn't affect control flow, only log output.

---

## Code Examples

### Host: complete framed `send_json_command()` (Phase 51)

```python
# Source: serial_comm.py lines 155-159 (current) → Phase 51 replacement
# Import additions required at top of file:
#   from firestarter.frame_parser import _crc8_ccitt, cobs_encode  (extend existing import)

def send_json_command(self, command_dict: dict) -> int:
    """Serialise command_dict as COBS+CRC8 framed command (Phase 51 / FRAME-05).

    Frame: [COBS(json_bytes + CRC8(json_bytes))][0x00]
    Atomic write — full frame in one send_bytes() call (SAFE-01 sub-claim B).
    """
    self._log_command_details(command_dict)
    json_bytes = json.dumps(command_dict, separators=(",", ":")).encode("ascii")
    crc = _crc8_ccitt(json_bytes)
    body = cobs_encode(json_bytes + bytes([crc]))
    frame = body + b"\x00"
    return self.send_bytes(frame)
```

### Firmware: new `CMD_IDLE` branch skeleton (Phase 51)

```c
// firestarter.cpp loop() CMD_IDLE branch — Phase 51 (D-05: {-peek path DELETED)
} else if (handle.cmd == CMD_IDLE) {
    if (rurp_communication_available() > 0) {
        // rurp_communication_read_data() spins to 0x00 delimiter, COBS-decodes
        // in-place into handle.data_buffer, verifies CRC8, drains on error (D-06).
        int n = rurp_communication_read_data(handle.data_buffer);
        if (n > 0) {
            handle.data_size = (uint32_t)n;
            handle.data_buffer[n] = '\0';
            // init_programmer_framed() assumes data_buffer + data_size are populated.
            if (init_programmer_framed(&handle)) {
                return;
            }
        } else {
            // n == 0: empty frame; n < 0: COBS/CRC/overflow error.
            // _drain_to_delimiter() already called inside rurp_communication_read_data().
            LOG_ERROR_ID(MSG_ERR_BAD_FRAME);  // new error ID, or reuse MSG_ERR_EMPTY_INPUT
        }
    }
    return;
}
```

### Firmware: `init_programmer_framed()` skeleton (Phase 51)

```c
// Replaces init_programmer() for the framed command path.
// Precondition: handle->data_buffer is populated with N decoded bytes,
//               handle->data_size == N, handle->data_buffer[N] == '\0'.
bool init_programmer_framed(firestarter_handle_t* handle) {
    handle->response_code = RESPONSE_CODE_OK;
    handle->operation_state = 0;
    handle->ctrl_flags = 0x80;

    LOG_DEBUG_ID_SUB_U16(DBG_BUFFER_SIZE, (uint16_t)handle->data_size);
    if (handle->data_size == 0) {
        LOG_ERROR_ID(MSG_ERR_EMPTY_INPUT);
        return false;
    }
    LOG_DEBUG_ID_SUB(DBG_SETUP);
    // data_buffer[data_size] = '\0' already done by caller.
    if (!parse_json(handle)) {
        return false;
    }
    // ... rest identical to current init_programmer() from line 127 onward ...
}
```

### Firmware: Unity test skeleton for Phase 51 command-frame cases

```cpp
// New: firestarter/test/native/avr/test_cobs_cmd_frame/test_cobs_cmd_frame.cpp
// Tests rurp_communication_read_data() in the command-channel context:
//   1. Valid JSON command frame → decoded correctly, CRC passes
//   2. Corrupted CRC → decoder returns < 0, parser NOT invoked (V5 / §4.4)
//   3. Oversized frame → -2 return, drain completed
// Uses serial_read_mock.h (already in test_messages/).
// New PIO test directory — add to platformio.ini test_filter.
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `{`-peek + `readBytes()` blocking ingest | COBS frame decoder with CRC8-before-parse | Phase 51 | Command channel gains end-to-end integrity; CRC-01 obligation on command channel closed |
| Plain JSON emission (`json.dumps` → `send_string`) | COBS-framed JSON + CRC8 → `send_bytes` | Phase 51 | Host cannot send a corrupted command silently; atomic frame boundary enforced |
| `rurp_communication_read_bytes()` in `init_programmer()` | Data pre-filled in CMD_IDLE by frame decoder | Phase 51 | Blocking `readBytes` removed from command-init path |

**Deprecated after Phase 51:**
- `rurp_communication_peak()` — no longer called from `CMD_IDLE`; still defined (used nowhere else — can be retained as dead code or removed if cleanup desired; not a Phase 51 task)
- The `{`-peek / discard-non-`{` logic — deleted by D-05

---

## Open Questions (RESOLVED)

> All four were planner-discretion items, resolved in the Phase-51 plans (51-01/51-02). Markers added post-planning.

1. **Symbol name: `init_programmer_framed` vs modified `init_programmer`**
   - What we know: the function body from line 115 onward is unchanged; only the read-preamble at lines 112-114 is removed.
   - What's unclear: whether to create a new `init_programmer_framed()` function or modify `init_programmer()` in place (e.g., via a parameter or by simply removing the read lines).
   - Recommendation: modify in place — rename to `init_programmer_framed()` or add a comment block. Avoids a dead unreachable old function. Planner's discretion.
   - **RESOLVED:** `init_programmer_framed()` (51-01 Task 2).

2. **Error ID for bad command frame (`MSG_ERR_BAD_FRAME`)**
   - What we know: existing error IDs are defined in `logging_id.h`; the firmware already has `MSG_ERR_EMPTY_INPUT`, `MSG_ERR_BAD_JSON`, `MSG_ERR_NO_CMD`.
   - What's unclear: whether to reuse `MSG_ERR_EMPTY_INPUT` (already covers `n == 0`) for the new error path or add a `MSG_ERR_BAD_FRAME` entry.
   - Recommendation: add `MSG_ERR_BAD_FRAME` to `logging_id.h` for distinction; planner's call. If not adding, `MSG_ERR_EMPTY_INPUT` is the least-wrong existing code.
   - **RESOLVED:** add `MSG_ERR_BAD_FRAME` to `logging_id.h` (51-01 Task 2; `logging_id.h` now in 51-01 `files_modified`).

3. **D-03: host version-floor bump**
   - What we know: current floor is "2.0.0" in `_validate_firmware_version()`. The framing-version firmware is 3.0.0b6.
   - What's unclear: whether bumping to "3.0.0" floor provides a meaningfully cleaner error for stale firmware.
   - Recommendation: bump floor to "3.0.0b6" or "3.0.0" so a stale firmware gets `FirmwareOutdatedError("Please reflash")` instead of an opaque COBS decode failure. Low-effort, useful UX. Planner should decide.
   - **RESOLVED:** see 51-02 Task 2 (D-03 disposition; non-load-bearing per D-01).

4. **`CMD_FRAME_MAX` as decoded-length check vs COBS-body-length check**
   - What we know: `rurp_communication_read_data()` already enforces a decoded-payload cap at `DATA_BUFFER_SIZE`. Defining `CMD_FRAME_MAX = DATA_BUFFER_SIZE` means the `CMD_IDLE` check `n <= CMD_FRAME_MAX` is always satisfied for successful decodes and always violated for `-2` returns (which the `n > 0` gate already catches).
   - Recommendation: define `CMD_FRAME_MAX` = 512 as documentation/parity constant; the real enforcement is the decoder's internal overflow guard. Planner may choose to omit the `n <= CMD_FRAME_MAX` check and rely solely on `n > 0`.
   - **RESOLVED:** `CMD_FRAME_MAX = 512` (= `DATA_BUFFER_SIZE`) as a documentation/parity constant in both repos (51-01 Task 1 + 51-02 Task 1); decoder overflow guard is the real enforcement.

---

## Environment Availability

Phase 51 is purely code/config changes with no new external dependencies beyond what Phase 50 established. Both sub-repos are on `v1.10-serial-transport-hardening` with all Phase-50 primitives already committed and green.

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| PlatformIO (`pio`) | Firmware build + native tests | Confirmed (Phase 50 used it) | — | — |
| Python 3 + pytest | Host tests | Confirmed (Phase 50: 408/408 green) | — | — |
| `firestarter/scripts/check_uno_ram.sh` | FRAME-03 RAM gate | Confirmed (Phase 50 Plan 04) | — | — |
| `firestarter_app/tests/test_cobs.py` (21 cases) | COBS primitive contract regression | Already GREEN (Phase 50 Plan 03) | — | — |

**No missing dependencies.** Phase 50 dual-repo green gate (28/28 firmware, 408/408 host) is the baseline for Phase 51.

---

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework (firmware) | Unity via PlatformIO `[env:native]` |
| Framework (host) | pytest + coverage |
| Config file (firmware) | `firestarter/platformio.ini` — `[env:native]` (lines 67-101) |
| Config file (host) | `firestarter_app/pyproject.toml` / `pytest.ini` |
| Quick firmware run | `pio test -e native -f "native/avr/test_cobs_cmd_frame"` |
| Full firmware run | `pio test -e native` |
| Quick host run | `python -m pytest tests/test_serial_comm.py tests/test_cobs.py -x` |
| Full host run | `python -m pytest --cov-fail-under=70` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| FRAME-05 / V5 | CRC8-before-parse: corrupted command frame → `rurp_communication_read_data()` returns < 0, `parse_json()` never called | unit (firmware Unity) | `pio test -e native -f "native/avr/test_cobs_cmd_frame"` | ❌ Wave 0 — new directory |
| FRAME-05 | Valid framed command → decoded correctly, `parse_json()` receives correct payload | unit (firmware Unity) | `pio test -e native -f "native/avr/test_cobs_cmd_frame"` | ❌ Wave 0 |
| FRAME-05 D-06 | Oversized frame → bounded recovery (drain + return, no hang) | unit (firmware Unity) | `pio test -e native -f "native/avr/test_cobs_cmd_frame"` | ❌ Wave 0 |
| FRAME-05 host | `send_json_command()` emits correct COBS+CRC8 frame | unit (host pytest) | `python -m pytest tests/test_serial_comm.py -x` | Partially — file exists, new test functions needed |
| FRAME-05 D-04 | Version probe (`{"state":13}`) goes through framed path, not raw text | unit (host pytest) | `python -m pytest tests/test_serial_comm.py -x` | ❌ new test function |
| CRC-01 | COBS primitives + CRC8 polynomial unchanged from Phase 50 | regression (both) | `pio test -e native -f "native/avr/test_cobs_data_frame"` + `pytest tests/test_cobs.py` | ✅ Phase 50 tests stay green |

### Sampling Rate

- **Per task commit:** `pio test -e native -f "native/avr/test_cobs_cmd_frame"` + `python -m pytest tests/test_serial_comm.py tests/test_cobs.py -x`
- **Per wave merge:** `pio test -e native` + `python -m pytest --cov-fail-under=70`
- **Phase gate:** Full dual-repo suite green before `/gsd-verify-work`

### Wave 0 Gaps (test infrastructure needed before implementation)

- [ ] `firestarter/test/native/avr/test_cobs_cmd_frame/test_cobs_cmd_frame.cpp` — new Unity suite for command-frame decode + CRC8-reject + resync
- [ ] `firestarter/test/native/avr/test_cobs_cmd_frame/host_stubs.cpp` — minimal stubs (include `_shared/host_stubs_common.inc`; see `test_cobs_data_frame/host_stubs.cpp` as model)
- [ ] `firestarter/platformio.ini` — add `native/avr/test_cobs_cmd_frame` to `test_filter` + `build_flags` `-I` path
- [ ] Host `tests/test_serial_comm.py` — add test functions for framed `send_json_command()` output, version-probe framing, and CRC8-reject path

*(If no gaps: existing test infrastructure covers all phase requirements — FALSE for Phase 51; gaps above are real.)*

---

## Security Domain

`security_enforcement` is not set to `false` in project config; section included.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | — |
| V3 Session Management | no | — |
| V4 Access Control | no | — |
| V5 Input Validation | **yes** | CRC8-before-parse mandate (§4.4 / T-49-01): framed input is validated (CRC8 verify) before the JSON parser ever sees bytes. `rurp_communication_read_data()` implements this control. |
| V6 Cryptography | no — CRC8 is an integrity check, not a cryptographic primitive | CRC8-CCITT (poly 0x07) via PROGMEM table; `_crc8_ccitt()` on host |

### Known Threat Patterns

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Corrupted / crafted command byte stream reaching JSON parser | Tampering | CRC8-before-parse (V5 / §4.4) — `rurp_communication_read_data()` discards CRC-failed frames before `parse_json()` is called |
| Unbounded accumulation from a frame whose `0x00` never arrives | Denial of Service | `CMD_FRAME_MAX` cap + internal `DATA_BUFFER_SIZE` overflow guard in decoder → bounded recovery via `_drain_to_delimiter()` |
| Split-write creating a `0x00` window during programmer mode transition | Timing / Bus-aliasing | SAFE-01 proof (ADR §1.3): sub-claim B (atomic write) + sub-claim C (full-frame consumption before `rurp_set_programmer_mode()`) enforced by design contract |

---

## Sources

### Primary (HIGH confidence)

- Live source read of `firestarter/src/firestarter.cpp` (lines 157-174, 109-144) — COBS/`{`-peek change targets [VERIFIED: live source]
- Live source read of `firestarter/src/boards/rurp_serial_utils.cpp` (lines 88-191, 204-276) — Phase-50 COBS decode + encode + CRC8 + drain [VERIFIED: live source]
- Live source read of `firestarter_app/firestarter/frame_parser.py` (lines 28-128) — `cobs_encode`, `cobs_decode`, `_crc8_ccitt` [VERIFIED: live source]
- Live source read of `firestarter_app/firestarter/serial_comm.py` (lines 134-159, 465-601) — `send_bytes`, `send_json_command`, `_probe_port` version handshake [VERIFIED: live source]
- Live source read of `firestarter/include/firestarter.h` (lines 18-42) — `DATA_BUFFER_SIZE`, `CMD_IDLE`, `CMD_FW_VERSION` [VERIFIED: live source]
- Live source read of `firestarter/include/rurp_serial_utils.h` — function signatures [VERIFIED: live source]
- Live source read of `firestarter/platformio.ini` (lines 67-101) — test_filter pattern [VERIFIED: live source]
- `.planning/v1.10-FRAMING-DECISION.md` — §1.3 SAFE-01 proof, §4.1-§4.6 frame contract [CITED: planning artifact]
- Phase 50 SUMMARY files (01-04) — confirmed what was actually built, patterns established, decisions made [CITED: planning artifacts]
- `.planning/phases/51-command-channel-framing-migration-breaking-wire-change/51-CONTEXT.md` — locked decisions D-01..D-06 [CITED: planning artifact]

### Secondary (MEDIUM confidence)

- Python measurement of worst-case JSON command size (422 bytes) — `json.dumps` of max-width bus-config command [VERIFIED: devcontainer measurement]
- Phase 50 `50-RAM-REPORT.md` — confirmed 545 B free RAM ceiling still holds post-Phase-50 changes [CITED: planning artifact]

---

## Assumptions Log

All key claims were verified against live source or planning artifacts. No `[ASSUMED]` tags in this research.

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| — | All claims verified | — | — |

**This table is empty:** All claims in this research were verified or cited.

---

## Metadata

**Confidence breakdown:**
- Standard stack (reusable symbols): HIGH — live source confirmed all function signatures, bodies, and locations
- Architecture (command-ingest mechanics): HIGH — live source trace of both the current path and Phase-50 decoder
- CMD_FRAME_MAX sizing: HIGH — measured via Python against all command types in the codebase
- Pitfalls: HIGH — derived from direct inspection of the code being deleted and the integration point
- Test patterns: HIGH — Phase-50 test infrastructure confirmed and directory convention verified

**Research date:** 2026-06-02
**Valid until:** Stable — no external dependencies; all primitives are in-repo. Valid until a new command type is added that exceeds the 422-byte worst-case (unlikely).
