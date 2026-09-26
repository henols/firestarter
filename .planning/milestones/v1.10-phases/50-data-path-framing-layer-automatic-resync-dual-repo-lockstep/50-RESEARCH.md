# Phase 50: Data-Path Framing Layer + Automatic Resync (dual-repo lockstep) - Research

**Researched:** 2026-06-01
**Domain:** Embedded serial transport (streaming COBS framing, AVR firmware ↔ Python host, dual-repo lockstep)
**Confidence:** HIGH (mechanism frozen by Phase-49 ADR; all open edges traced against live source on branch `v1.10-serial-transport-hardening`)

## Summary

Phase 50 replaces the bare `[len_u16 BE][xor][payload]` data-block boundary with the Phase-49-frozen
`[COBS(payload + CRC8)][0x00]` frame on the host↔firmware data path, in lockstep across both sub-repos.
The mechanism (streaming COBS, `0x00` delimiter, `len_u16` removed, XOR→CRC8) is LOCKED and must not be
re-litigated. This research pins the implementation edges the ADR/CONTEXT leave open: the corrupted-`#`-marker
resync structure, the zero-extra-buffer streaming decode-in-place strategy under the Uno ~545 B free-RAM
ceiling, the exact byte-discard resync loop in both repos, the atomic-write discipline, the host RX demux
disambiguation, and the D-02 test mechanics.

**A load-bearing architectural finding the planner MUST resolve before writing tasks:** the *current*
fw→host data block (Framing 3, the EPROM read path) does **NOT** flow through `rurp_communication_write()`.
Reads emit chip bytes via `rurp_log_id_wide(MSG_DATA_CHUNK, …)` over the **unchanged** magic-preamble
log/telemetry framing (`_firestarter_emit_frame_wide`, `eprom_operations.cpp:114`). `rurp_communication_write()`
is only reachable through `_check_response()`'s `RESPONSE_CODE_DATA` case, and the only writer of
`RESPONSE_CODE_DATA` (`memory.cpp:413`) is behind `#ifdef RAW_DATA_PROGRESS`, which is **not defined** in any
build. So `rurp_communication_write()` is effectively dead code in the shipping firmware. Framing 3 (fw→host
data) is therefore *already* carried by the magic-preamble frame the ADR declares "UNCHANGED in v1.10."

This creates a direct tension with ADR §4.2 ("Framing 3 (fw→host data block): Phase 50") and §4.6 (which
maps `rurp_communication_write` as a Phase-50 change). See **Open Questions Q1** — this must be reconciled
with the operator before the planner locks the scope. The honest reading of the live code is that Phase 50's
real, load-bearing change is **Framing 2 (host→fw data block, the WRITE path)** via `rurp_communication_read_data()`,
plus converting the now-correct `rurp_communication_write()` for contract-completeness/symmetry even though it
is dormant.

**Primary recommendation:** Implement the streaming COBS encoder/decoder in `rurp_serial_utils.cpp`
(replacing `rurp_communication_read_data` + `rurp_communication_write`), add a streaming COBS decode helper
to `frame_parser.py` and rework the host WRITE-path framing in `eprom_operations.py` + `serial_comm.py`,
keep the `#` marker with a resync loop that re-anchors on `0x00` even when `#` itself is corrupt, and pin
recovery (not just detection) with one host pytest + one firmware Unity case. Resolve Open Question Q1 first.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Host→fw data-block frame encode (WRITE path) | Host (`eprom_operations.py` + `frame_parser.py`) | `serial_comm.send_bytes` | Host builds the frame as one `bytes` object and writes atomically |
| Host→fw data-block frame decode (WRITE path) | Firmware (`rurp_serial_utils.cpp::rurp_communication_read_data`) | `operation_utils.cpp` `case '#'` | Firmware streams bytes off UART into `data_buffer`, decode-in-place |
| fw→host data-block frame encode (READ path) | Firmware — see Open Q1 (currently `_firestarter_emit_frame_wide`, NOT `rurp_communication_write`) | — | Scope ambiguity; planner must reconcile with operator |
| fw→host data-block frame decode (READ path) | Host (`serial_comm._read_and_parse_lines`) | `frame_parser` | Host demuxes the framed stream |
| Resync / byte-discard on error | Both receivers | — | Symmetric: discard to next `0x00`, bounded to one frame |
| CRC8-CCITT integrity (poly 0x07) | Both repos, reused unchanged (D-05) | — | Existing PROGMEM table + `_build_crc8_table()` |
| Atomic delimiter write | Host (`send_bytes`) | — | Single `write()`+`flush()`, no split-write window |

## Standard Stack

This phase hand-rolls a transport per the frozen ADR — there is no external library to add. COBS is a
~40-line firmware / ~30-line host algorithm, deliberately not a dependency (AVR has no package manager;
the host avoids a dependency for a trivial, audit-critical primitive). No packages are installed.

| Component | Where | Purpose | Why this way |
|-----------|-------|---------|--------------|
| Streaming COBS encoder | `rurp_serial_utils.cpp` (fw), `frame_parser.py`/`eprom_operations.py` (host) | Frame payload+CRC8 with no `0x00` in body | Hand-rolled per ADR §4.1; zero extra RAM on AVR |
| Streaming COBS decoder | `rurp_serial_utils.cpp` (fw), `frame_parser.py` (host) | Decode-in-place into `data_buffer` | No second ~512 B buffer (D-04) |
| CRC8-CCITT table | `rurp_serial_utils.cpp:108-128` (PROGMEM), `frame_parser.py:28-44` | Integrity over raw payload | Reused UNCHANGED (D-05) — byte-compatible across repos |

### Package Legitimacy Audit

No external packages are installed by this phase. CRC8/COBS are hand-rolled in-repo per the frozen ADR.
slopcheck / registry verification is therefore **not applicable** (N/A). The only "dependencies" are the
existing pyserial (host, already present) and the Arduino framework (firmware, already present); neither
changes.

## Architecture Patterns

### System Architecture Diagram

```
WRITE PATH (Framing 2, host→fw)  — the load-bearing Phase-50 change
─────────────────────────────────────────────────────────────────
host: eprom_operations._main_phase_send_data
   reads buffer_size bytes from file
   crc8 = _crc8_ccitt(chunk)                         [frame_parser, UNCHANGED table]
   body = cobs_encode(chunk + bytes([crc8]))         [NEW host helper]
   frame = b"#" + body + b"\x00"                      [atomic — single bytes object]
        │
        ▼  send_bytes(frame)  → connection.write(frame); connection.flush()   [ONE call, atomic-write mandate]
        │
   ════ SERIAL 250000 baud ════
        │
        ▼
fw: op_get_message()  peek=='#'  → consume '#'        [operation_utils.cpp:167-179]
        │
        ▼  rurp_communication_read_data(data_buffer)   [REWRITTEN: COBS streaming decode-in-place]
           accumulate bytes until 0x00 delimiter
           cobs_decode into data_buffer (in place)
           verify CRC8 over decoded payload
           res<0 on COBS/CRC fail → discard to next 0x00 (resync)
        │
        ├─ res>=0 → handle->data_size=res; OP_MSG_DATA
        └─ res<0  → LOG_ERROR_ID_U16(MSG_ERR_DATA_ERR_N,res) → OP_MSG_ERROR   [op_utils.cpp:165-167]

READ PATH (Framing 3, fw→host)  — SEE OPEN QUESTION Q1
─────────────────────────────────────────────────────────────────
fw: _process_outgoing_data → rurp_log_id_wide(MSG_DATA_CHUNK,…)  [CURRENTLY magic-preamble frame, "UNCHANGED"]
   (rurp_communication_write is dead: only reached via RESPONSE_CODE_DATA behind #ifdef RAW_DATA_PROGRESS)
        │
        ▼  host: _read_and_parse_lines demuxes [0xAA55AA55]…[0x0A]  → MSG_DATA_CHUNK payload
```

### Pattern 1: Streaming COBS encode, no second buffer (firmware)
**What:** Scan `data_buffer[0..N-1]` for runs of non-zero bytes (max 254), emit a run-length code byte
then the run bytes directly to `SERIAL_PORT.write()`, terminate with `0x00`. The CRC8 byte is appended to
the logical payload *before* encoding, so it is COBS-encoded too (ADR §4.3).
**When to use:** fw encode side (write completion / dormant `rurp_communication_write`).
**Example:**
```c
// Source: v1.9-COBS-DECISION §3 streaming reference snippet (adapted; CRC8 appended before encode)
// RAM cost: 3 locals (~6 B stack). The CRC8 byte must be folded into the encoded stream as if it
// were the (N+1)th payload byte — handle it after the data_buffer loop so a trailing zero CRC encodes correctly.
size_t i = 0;
uint8_t crc = 0;
for (size_t k = 0; k < N; k++) crc = crc8_ccitt(crc, (uint8_t)buffer[k]);
// Encode payload bytes + the crc byte as one logical stream of length N+1.
// (Simplest correct form: build a 1-byte tail and run COBS over a "virtual" stream;
//  in practice encode [buffer..N-1] then encode the single crc byte as its own short run.)
```
**Subtlety (MUST handle):** a blank-EPROM all-`0x00` payload makes every byte a run of length 0 — each emits
a `0x01` run code and no data bytes, so a 512 B all-zero payload encodes to 513 code bytes + delimiter. The
encoder must NOT materialize this; it streams. The 255-byte block boundary (`run_len == 254` → emit code,
start new run without consuming a zero) and the implicit phantom-zero rule must be exact or the host decode
diverges. Pin this with the Phase-52 byte-compat matrix; Phase 50 only needs the all-zero case to *round-trip*
in the resync test.

### Pattern 2: Decode-in-place into `data_buffer` (firmware, recommended)
**What:** The decoder reads UART bytes one at a time. Because COBS-decoded output is always ≤ encoded input
and the decoded bytes are written at a write-cursor that never overtakes the read position, you can decode
**in place** with a single index into `data_buffer` — no second buffer.
**When to use:** `rurp_communication_read_data()` rewrite (the load-bearing decode).
**Recommended strategy (Claude's-discretion area per CONTEXT):** *incremental decode while reading*, writing
the decoded byte to `buffer[out++]` as each run completes, rather than buffering the encoded form then decoding.
This is provably zero-extra-buffer: state is `out` (write cursor), `block_remaining` (current run countdown),
and a "was this a 254-run" flag — ~5–6 B stack. Bound `out` by `DATA_BUFFER_SIZE` and return `-2` on overflow
(preserves the existing too-large guard). The last decoded byte is the CRC8; pop it, recompute CRC8 over
`buffer[0..out-2]`, compare.

### Pattern 3: Corrupted-`#`-marker resync (D-04 open edge — VALIDATED)
**What:** Confirm a flipped/corrupt `#` marker byte re-anchors cleanly and does not strand the parser.
**Trace (`operation_utils.cpp:134-186`):** `op_get_message()` peeks one byte. If it is not `'O'`/`'D'`/`'#'`,
the `default:` case **consumes one byte and loops** (`rurp_communication_read(); break;`). So a corrupted `#`
(e.g. `0x23`→`0x22`) lands in `default`, is discarded, and the loop continues consuming bytes. Critically,
the *following* COBS frame body is `0x00`-free by construction and ends in a `0x00` delimiter — so after the
bad marker, the parser discards the entire orphaned frame body byte-by-byte through `default` until it has
chewed past the `0x00` delimiter, and the **next** `#` (the next packet's marker) re-anchors cleanly.
**The residual risk and the required structure:** the orphaned frame body could, by chance, contain a `'#'`,
`'O'`, or `'D'` byte that mis-triggers a marker case mid-garbage. The mitigation already in place: a false
`'#'` enters `rurp_communication_read_data`, which (rewritten) accumulates to the next `0x00`, fails CRC8,
returns `res<0`, surfaces `OP_MSG_ERROR`, and the operation fails fast (D-01) — bounded to one frame, no
2 s hang. **Planner directive:** the rewritten `rurp_communication_read_data` MUST, on any COBS/CRC failure,
*consume bytes up to and including the next `0x00`* before returning the error code, so the read cursor is
left re-anchored at a frame boundary for the next `op_get_message` call. Do NOT return early leaving a
partial frame in the RX buffer — that is the only way the marker-corruption edge strands the parser.
**Confidence:** HIGH — traced directly against live `operation_utils.cpp`.

### Pattern 4: Atomic-write discipline (host) — already satisfied
**What:** Assemble `b"#" + cobs_body + b"\x00"` as one `bytes` object; pass to `send_bytes()` once.
**Current state (`serial_comm.py:134-148`, `eprom_operations.py:380-390`):** the existing write path
*already* builds `header + data_chunk` as a single `bytes` object and calls `self.comm.send_bytes(...)` once;
`send_bytes` does `connection.write(data_bytes)` then `connection.flush()`. This already satisfies the
atomic-write mandate (ADR §4.1 / SAFE-01 sub-claim B). **Planner directive:** preserve this — change only the
frame *contents* (`b"#" + cobs_encode(chunk+crc) + b"\x00"`), never split the delimiter into a second write.

### Anti-Patterns to Avoid
- **Splitting the `0x00` delimiter into a second `write()`** — forbidden by ADR §4.1; would reopen the
  SAFE-01 timing window. Keep one `bytes` object.
- **Materializing a second encode buffer on AVR** — violates D-04 / FRAME-03. Stream directly to `Serial.write`.
- **Retaining or re-adding any `len_u16`** — ADR §4.3 removes it; a length count undermines the resync goal.
- **Touching `_firestarter_emit_frame` / `_firestarter_emit_frame_wide` / the `[0xAA55AA55]…[0x0A]` format** —
  explicitly UNCHANGED in v1.10 (ADR §4.2). The read path currently *uses* this; see Open Q1.
- **Returning a decode error without draining to the next `0x00`** — strands the parser (Pattern 3).

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| CRC8-CCITT | A new CRC routine / different polynomial | Existing `crc8_ccitt()` (fw PROGMEM table) + `_crc8_ccitt()`/`_build_crc8_table()` (host) | D-05 locks poly 0x07; tables are byte-compatible and test-pinned; any swap breaks lockstep |
| fw→host data framing | A new COBS frame for the read path | The existing `MSG_DATA_CHUNK` magic-preamble frame (see Open Q1) | It is "UNCHANGED in v1.10" per ADR §4.2; do not duplicate framing |
| Serial line discipline | A new write/flush pattern | Existing `send_bytes()` (`write`+`flush`) | Already atomic; reuse it |

**Key insight:** The only genuinely new code is the COBS encode/decode pair (both repos). Everything else
(CRC8, atomic write, marker dispatch, error surface) already exists and is reused unchanged.

## Common Pitfalls

### Pitfall 1: Assuming the READ path uses `rurp_communication_write`
**What goes wrong:** Planner writes a task to "convert `rurp_communication_write` to COBS" believing it
carries EPROM reads. It does not — reads use `rurp_log_id_wide(MSG_DATA_CHUNK,…)`. Converting only
`rurp_communication_write` changes nothing observable on the read path.
**Why it happens:** ADR §4.6 maps `rurp_communication_write` as the fw→host data writer; the live code
diverged (read path moved to MSG_DATA_CHUNK ID frames in Phase 8 W-04).
**How to avoid:** Resolve Open Q1 with the operator first. Treat the WRITE path (`rurp_communication_read_data`)
as the load-bearing change; treat `rurp_communication_write` as a dormant-but-contract-correct rewrite.
**Warning signs:** A "read test" that passes without touching the new COBS code.

### Pitfall 2: COBS 254-byte block boundary / phantom-zero off-by-one
**What goes wrong:** A 254-byte non-zero run boundary or the implicit trailing zero is mis-encoded; host
and firmware disagree by one byte on long runs or on payloads ending in `0x00`.
**Why it happens:** COBS has two notorious edges — the `0xFF`/254 run code (no implicit zero consumed) and
the phantom zero appended to the logical stream.
**How to avoid:** Encode the CRC8 byte as part of the same logical stream (ADR §4.3) and pin the all-zero
512 B case in the resync round-trip. Full pathological matrix is Phase 52, but the all-zero and the
254-run cases should at least round-trip in Phase 50's tests.
**Warning signs:** Decode succeeds for short payloads but CRC fails for full-buffer or all-`0xFF` payloads.

### Pitfall 3: Decode error leaves a partial frame in the buffer
**What goes wrong:** On CRC/COBS failure the firmware returns `-4` immediately, leaving the rest of the
corrupt frame (and its `0x00`) in the RX buffer; the next `op_get_message` mis-parses the residue.
**Why it happens:** The natural early-return on error.
**How to avoid:** Pattern 3 directive — always drain to and including the next `0x00` before returning.
This is exactly what makes "bounded to one frame" (SC2/FRAME-02) true.

### Pitfall 4: `readBytes` timeout semantics vs. delimiter-driven read
**What goes wrong:** The new decoder still relies on `SERIAL_PORT.readBytes(buf, n)` (which has the
Arurp 1 s `Stream` timeout) and reintroduces a timeout stall.
**Why it happens:** Copying the old `rurp_communication_read_bytes` loop.
**How to avoid:** The streaming decoder reads byte-by-byte via `rurp_communication_read()` /
`rurp_communication_available()` gated by `op_get_message`'s availability check, accumulating until `0x00`.
The 2 s `timeout_ms` loop (`rurp_serial_utils.cpp:59-66`) — the exact cascade source SC1 targets — is
**removed**. Keep a bounded safety timeout only if needed to avoid an infinite wait on a never-arriving
delimiter, but it must be the delimiter, not a length, that ends the frame.

## Code Examples

### Host streaming COBS decode helper (frame_parser.py — recommended home)
```python
# Source: ADR §4.1 + standard COBS (decode is the inverse of the §3 reference encoder).
# Placement is Claude's discretion (CONTEXT) — frame_parser.py keeps it stdlib-only and testable
# without serial I/O, matching the module's existing _crc8_ccitt/_decode_param leaf role.
def cobs_decode(encoded: bytes) -> bytes:
    """Decode a COBS body (NO trailing 0x00 delimiter included). Raises ValueError on malformed input."""
    out = bytearray()
    i = 0
    n = len(encoded)
    while i < n:
        code = encoded[i]
        if code == 0:
            raise ValueError("0x00 inside COBS body")  # delimiter must not appear in body
        i += 1
        end = i + code - 1
        if end > n:
            raise ValueError("COBS run exceeds buffer")
        out.extend(encoded[i:end])
        i = end
        if code < 0xFF and i < n:
            out.append(0)  # implicit zero, except after a 254-run or at stream end
    return bytes(out)
```

### Firmware decode return-code contract (operation_utils.cpp:167-179 — UNCHANGED surface)
```c
// Source: live operation_utils.cpp — the error surface D-01 reuses, DO NOT change.
case '#': {
    if (rurp_communication_available() < 4) { return OP_MSG_INCOMPLETE; }
    rurp_communication_read();                 // consume '#'
    int res = rurp_communication_read_data(handle->data_buffer);  // REWRITTEN to COBS+resync
    if (res < 0) {
        LOG_ERROR_ID_U16(MSG_ERR_DATA_ERR_N, (uint16_t)res);  // fail-fast, no 2 s hang
        return OP_MSG_ERROR;
    }
    handle->data_size = res;
    return OP_MSG_DATA;
}
```

### Existing atomic write (eprom_operations.py:380-390 — change CONTENTS only)
```python
# Source: live eprom_operations.py — already atomic. Phase 50 changes the header/body construction:
#   crc = _crc8_ccitt(data_chunk)
#   body = cobs_encode(data_chunk + bytes([crc]))
#   frame = b"#" + body + b"\x00"
#   self.comm.send_bytes(frame)        # ONE call, write+flush — atomic-write mandate satisfied
```

## Runtime State Inventory

> This is a wire-protocol change, not a rename/migration, but the lockstep/dual-repo nature warrants the audit.

| Category | Items Found | Action Required |
|----------|-------------|------------------|
| Stored data | None — no on-disk/EEPROM persisted form of the data-block wire frame. EPROM contents are unaffected (byte payload identical; only the transport envelope changes). | None — verified by grep of EEPROM/`rurp_configuration_t` (calibration only). |
| Live service config | None — no external service holds the frame format. | None. |
| OS-registered state | None. | None. |
| Secrets/env vars | `FIRESTARTER_DEV_ALLOW_PRE_V12` exists (`serial_comm.py:577`) — gates the *log-frame* version handshake, NOT the data-block transport. D-03 defers the data-path version guard to Phase 51. | None in Phase 50 (document the breaking nature per D-03). |
| Build artifacts | `firestarter_app` is an editable pip install (`pip install -e .`) — source edits are live, no stale artifact. Firmware rebuilds from source each `pio run`. | None — re-run `pip install -e '.[test]'` only if the toolchain was wiped (see MEMORY note). |
| Wire-protocol lockstep | `rurp_serial_utils.cpp` ↔ `serial_comm.py`/`frame_parser.py` MUST change in the same change-set on branch `v1.10-serial-transport-hardening` in each sub-repo. CRC8 tables/constants duplicated (`constants.py` ↔ `firestarter.h`) — no framing constant is duplicated yet; if one is added (e.g. a delimiter `#define`), add it to BOTH. | Lockstep commits inside each sub-repo. |

**The canonical question:** after both repos are updated, is there any cached/stored form of the OLD
`[len_u16][xor]` frame anywhere? **Answer: no** — the frame exists only in-flight on the wire. A mixed-version
host/firmware pair will simply fail to communicate (accepted breaking upgrade, D-03).

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| PlatformIO (`pio`) | `pio run -e uno` RAM report (SC3/FRAME-03), `pio test -e native` | ✓ | core 6.x, atmelavr 5.2.0, framework-arduino-avr 5.3.0 | — |
| avr-gcc toolchain | Firmware build | ✓ | toolchain-atmelavr 1.70300.191015 (gcc 7.3.0) | — |
| Unity + ArduinoFake | Firmware Unity resync test (D-02) | ✓ | ArduinoFake ^0.4.0 | — |
| Python + pytest | Host pytest (D-02) | ✓ (use `/usr/local` python; `pip install -e '.[test]'`) | — | — |
| pyserial | Host serial path (already imported) | ✓ | — | — |
| Bench hardware (Uno/Leonardo/uno328pb) | Phase 53 only — NOT Phase 50 | n/a | — | Phase 50 is host/native-test only |

**Baseline RAM report captured this session (`pio run -e uno`, 2026-06-01):**
`RAM: 73.4% (used 1503 bytes from 2048 bytes)` → **545 bytes free** — matches the ADR's ~545 B ceiling.
`Flash: 69.7% (22492/32256 bytes)`. SC3 requires the post-change report to stay under this ceiling; the
~6 B stack COBS state leaves ample margin. **No external dependencies block Phase 50.**

## Validation Architecture

> nyquist_validation: treated as ENABLED (no explicit `false` found in config; section included).

### Test Framework
| Property | Value |
|----------|-------|
| Framework (firmware) | Unity via PlatformIO `[env:native]` (ArduinoFake Serial mock) |
| Framework (host) | pytest |
| Firmware config | `firestarter/platformio.ini` `[env:native]`, `test_filter` includes `native/avr/test_messages` |
| Host config | `firestarter_app/pyproject.toml` `[dev]`/`[test]` extras; ruff+mypy+pytest CI gate (`.github/workflows/ci.yml`) |
| Firmware quick run | `pio test -e native -f "*test_messages*"` |
| Firmware full suite | `pio test -e native` |
| Host quick run | `pytest tests/ -x -k cobs` (new test file) |
| Host full suite | `pytest --cov-fail-under=70` |
| Firmware RAM gate | `pio run -e uno` (assert RAM < 545 B free ceiling, no second buffer) |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| FRAME-01 | `[len_u16][xor]` boundary replaced by `[COBS(payload+CRC8)][0x00]` both directions | unit (round-trip) | `pio test -e native -f "*test_messages*"` + `pytest -k cobs_roundtrip` | ❌ Wave 0 (new cases) |
| FRAME-02 | Receiver discards to next `0x00`, recovers within ONE frame after injected fault | unit (fault-injection, both repos) | `pio test -e native -f "*test_messages*"` + `pytest -k cobs_resync` | ❌ Wave 0 |
| FRAME-03 | Streaming encode/decode, no second ~512 B buffer, < 545 B free RAM | build report | `pio run -e uno` (parse RAM line) | ✅ build exists; assertion is manual/scripted |
| FRAME-04 | Full 512 B / 1024 B payload frames without re-chunking | unit (full-buffer round-trip) | `pytest -k cobs_full_buffer` + `pio test -e native` | ❌ Wave 0 |
| CRC-01 | CRC8-CCITT poly 0x07 over raw payload, byte-compatible both repos | unit (CRC pin) | existing `test_crc_polynomial_smoke` + new `pytest -k crc8_data_payload` | ⚠ partial (fw smoke exists; data-payload case new) |

### Sampling Rate
- **Per task commit:** `pio test -e native -f "*test_messages*"` (fw) / `pytest -x -k cobs` (host).
- **Per wave merge:** `pio test -e native` (fw full) + `pytest --cov-fail-under=70` (host full) + `pio run -e uno` RAM report.
- **Phase gate:** both full suites green + RAM report under ceiling, before `/gsd-verify-work`.

### SC2 assertion shape (the load-bearing one)
The resync tests MUST assert **bounded recovery**, not mere detection:
- **Host pytest:** feed the decoder a stream of `[corrupt-CRC frame][0x00][valid frame][0x00]` and a variant
  with a flipped/missing delimiter; assert (a) the first frame raises a clean exception / returns an error
  (no 2 s hang — assert wall-clock < e.g. 0.1 s, or that no blocking read is entered), AND (b) the **next**
  valid frame decodes to the correct payload. Use a fake/in-memory serial (feed `bytes`), not real hardware.
- **Firmware Unity (`test_messages/`):** using the ArduinoFake `Serial.read`/`available` mock (drive a queued
  byte vector — extend the existing `When(OverloadedMethod(... read ...))` pattern), feed
  `[garbled frame][0x00][valid frame][0x00]` into `rurp_communication_read_data`; assert the first call
  returns `res < 0` AND the buffer read cursor is left at the start of the valid frame, AND a second call
  returns the correct decoded length with `data_buffer` matching the expected payload.

### Wave 0 Gaps
- [ ] `firestarter_app/tests/test_cobs.py` (or extend `tests/test_decoder.py`) — `cobs_encode`/`cobs_decode`
      round-trip, all-zero 512 B payload, resync-after-fault, CRC8-over-payload — covers FRAME-01/02/04, CRC-01.
- [ ] `firestarter/test/native/avr/test_messages/` new RUN_TEST cases for COBS decode-in-place + resync —
      covers FRAME-01/02. ArduinoFake `Serial.read`/`available` queued-byte mock helper.
- [ ] A scripted RAM-ceiling assertion around `pio run -e uno` (parse the `RAM: … (used N bytes…)` line) —
      covers FRAME-03.
- [ ] If a shared host stub for queued serial reads does not exist in `test_messages/`, add one (the suite
      currently only mocks `Serial.write`; the decoder test needs `read`/`available`).

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `[len_u16 BE][xor][payload]` + 2 s timeout on data block | `[COBS(payload+CRC8)][0x00]`, delimiter-driven, fail-fast | Phase 50 (this) | Eliminates the `len_u16`-corruption → wrong-length read → 2 s timeout cascade |
| XOR checksum on data path | CRC8-CCITT poly 0x07 (reused table) | Phase 50 | Stronger integrity; lockstep with log-frame CRC8 |
| READ path raw-bytes-after-`DATA:` | `MSG_DATA_CHUNK` over magic-preamble frame | Phase 8 (W-04, already shipped) | Read path already self-delimiting — relevant to Open Q1 |

**Deprecated/outdated:**
- `rurp_communication_write()` — effectively dead (only reachable via `RESPONSE_CODE_DATA` behind
  `#ifdef RAW_DATA_PROGRESS`, undefined in all builds). Rewrite for contract-correctness, but it is not the
  load-bearing path. See Open Q1.
- The 2 s `timeout_ms` loop (`rurp_serial_utils.cpp:59-66`) — removed by this phase (the SC1 win).

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | The READ path (Framing 3) is carried by `MSG_DATA_CHUNK`/magic-preamble, NOT `rurp_communication_write`; the latter is dead code | Summary, Open Q1 | If a build *does* define `RAW_DATA_PROGRESS`, `rurp_communication_write` is live and IS the read path — re-scope. Verified `RAW_DATA_PROGRESS` undefined in all `[env:*]` and headers this session, so risk is LOW. |
| A2 | `incremental decode-in-place` stays ≤ encoded length and never overtakes the read cursor (no second buffer) | Pattern 2 | If wrong, FRAME-03 fails. COBS output ≤ input is a mathematical property; risk LOW. Confirm on post-change RAM report. |
| A3 | Keeping a bounded safety timeout (not a length) does not reintroduce the cascade | Pitfall 4 | A too-short safety timeout could false-fail slow transfers. Tune against 250000 baud full-buffer timing; risk LOW. |
| A4 | Removing the 2 s loop does not break any caller that relied on its return codes (-1/-2/-3/-4) | Code Examples | Callers only check `res < 0` (op_utils:165); specific codes are only logged. Risk LOW. |

## Open Questions

1. **Scope of Framing 3 (fw→host READ path) — reconcile ADR vs. live code.** [DECISION NEEDED — operator]
   - What we know: ADR §4.2/§4.6 assign `rurp_communication_write` (fw→host data) to Phase 50. The live read
     path emits chip bytes via `rurp_log_id_wide(MSG_DATA_CHUNK,…)` over the magic-preamble frame, which the
     ADR declares UNCHANGED. `rurp_communication_write` is dead (`#ifdef RAW_DATA_PROGRESS`, undefined).
   - What's unclear: Does Phase 50 (a) only re-frame the WRITE path (`rurp_communication_read_data`) and
     rewrite the dormant `rurp_communication_write` for contract symmetry, leaving reads on the unchanged
     MSG_DATA_CHUNK frame — OR (b) also migrate the READ path off MSG_DATA_CHUNK onto the new COBS data frame
     (which would contradict "Framing 4/log-telemetry UNCHANGED" since reads ride that frame)?
   - Recommendation: **Option (a).** Re-frame the WRITE path (the real cascade source — host sends `[len][xor]`
     today), rewrite `rurp_communication_write` to the COBS contract for symmetry/future use, and leave the
     READ path on its already-self-delimiting MSG_DATA_CHUNK frame. This honors "log/telemetry UNCHANGED,"
     delivers the SC1 anti-cascade win, and keeps the diff minimal. Confirm with operator before planning;
     update STATE.md/ADR errata if (a) is chosen.

2. **Bounded safety timeout on the delimiter wait?**
   - What we know: removing the 2 s loop is the SC1 win; but a never-arriving `0x00` (e.g. host died mid-frame)
     must not hang forever.
   - What's unclear: keep a large coarse watchdog (e.g. one tied to the existing op-level timeout) vs. rely
     purely on `op_get_message` being non-blocking.
   - Recommendation: rely on the non-blocking `op_get_message` availability gate; if a frame is incomplete,
     return `OP_MSG_INCOMPLETE` and let the existing op-level ACK/timeout machinery (`op_wait_for_ack`,
     `op_reset_timeout`) govern. No per-byte 2 s loop. Planner to confirm the read loop integrates with
     `op_get_message`'s `available()` check rather than blocking.

## Project Constraints (from CLAUDE.md)

- **Protocol lockstep:** serial-protocol changes must be kept in sync between `serial_comm.py` and
  `firestarter.cpp`/`rurp_serial_utils.cpp`. (Dual-repo lockstep mandate — both sub-repos, branch
  `v1.10-serial-transport-hardening`.)
- **Duplicated constants:** flag bits/constants duplicated between `constants.py` and `firestarter.h` must
  change together. If a framing constant (e.g. delimiter) is added, add it to both.
- **Board buffer difference:** Uno 512 B / Leonardo 1024 B affects chunked transfer in `eprom_operations.py`.
  NOTE: live `platformio.ini` currently pins `[env:leonardo] -D DATA_BUFFER_SIZE=512` ("TEMP: 512 to match
  Uno for buffer-size A/B test (was 1024)"). FRAME-04 nominally requires 1024 B Leonardo framing — but the
  Leonardo build is currently 512 B. The COBS algorithm is size-agnostic ("works for any N"), so this does
  not block Phase 50; the 1024 B path is exercised by changing the define. Flag to planner: SC3/FRAME-04's
  "1024 B Leonardo" is currently a 512 B build; either restore 1024 for the test or note the A/B-test pin.
- **Firmware:** chip OUT of socket before any sideload (bench only — not Phase 50, which is host/native-test).
- **Tooling gate (host):** `ruff check` + `ruff format --check` + `mypy` (strict; `serial_comm.py` +
  `frame_parser.py` are both in the strict-8 set) + `pytest --cov-fail-under=70`. New COBS code must pass
  all four. Coverage floor has ~0 headroom historically — add tests with the code.

## Security Domain

> security_enforcement treated as enabled.

### Applicable ASVS Categories
| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V5 Input Validation | yes | CRC8 integrity gate + bounded COBS decode (reject `0x00` in body, reject run overruns, cap at `DATA_BUFFER_SIZE`) on the data-block path |
| V6 Cryptography | no | CRC8 is an integrity check, not crypto — correctly not used for authentication |
| V2/V3/V4 (auth/session/access) | no | Local serial transport; no auth surface in scope |

Note: the **CRC8-before-parse** mandate (ADR §4.4, V5 / threat T-49-01) applies to the *command* channel and
is a **Phase 51** constraint — out of scope for Phase 50 (data path). Phase 50's V5 control is the
bounded-decode + CRC8 verify on the data block before it reaches the eprom read/write loop.

### Known Threat Patterns for serial transport
| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Corrupted length field → over-read/under-read | Tampering / DoS (2 s hang) | Remove `len_u16`; delimiter-bounded frame (FRAME-01) |
| Bit-flip in payload | Tampering | CRC8-CCITT verify, discard frame on mismatch (CRC-01) |
| Desync cascade past one frame | DoS | Resync to next `0x00`, drain-on-error, bounded to one frame (FRAME-02) |
| Decode buffer overrun (oversize run/payload) | Tampering | Cap decode output at `DATA_BUFFER_SIZE`, return error (existing `-2` guard) |

## Sources

### Primary (HIGH confidence)
- `.planning/v1.10-FRAMING-DECISION.md` §3, §4.1–§4.6 — frozen frame contract (read in full).
- `.planning/v1.9-COBS-DECISION.md` §3 — streaming COBS reference encoder snippet; D-04/D-05.
- Live source (branch `v1.10-serial-transport-hardening`): `firestarter/src/boards/rurp_serial_utils.cpp`,
  `firestarter/src/operation_utils.cpp`, `firestarter/src/eprom_operations.cpp`,
  `firestarter/src/proms/memory.cpp`, `firestarter/include/firestarter.h`, `firestarter/platformio.ini`,
  `firestarter/test/native/avr/test_messages/test_rurp_log_id.cpp`,
  `firestarter/test/native/avr/test_data_input/test_rurp_set_data_input.cpp`,
  `firestarter_app/firestarter/serial_comm.py`, `firestarter_app/firestarter/frame_parser.py`,
  `firestarter_app/firestarter/eprom_operations.py`, `firestarter_app/firestarter/constants.py`.
- `pio run -e uno` executed this session — RAM 1503/2048 B (545 B free) baseline.
- `.planning/REQUIREMENTS.md` (FRAME-01..05, CRC-01, v1.10 Non-Goals), `.planning/ROADMAP.md` (Phase 50–53).
- `CLAUDE.md` (meta, firmware, app) — project constraints.

### Secondary (MEDIUM confidence)
- COBS algorithm general behavior (254-run / phantom-zero edges) — standard, cross-checked against the
  v1.9 reference snippet; full byte-exactness deferred to Phase 52 tests.

### Tertiary (LOW confidence)
- None. (All claims traced to live source or frozen ADR.)

## Metadata

**Confidence breakdown:**
- Standard stack / mechanism: HIGH — frozen by ADR, hand-rolled, no packages.
- Architecture (marker resync, decode-in-place, atomic write): HIGH — traced against live source.
- READ-path scope (Framing 3): MEDIUM — ADR/live-code divergence surfaced as Open Q1; needs operator confirm.
- Pitfalls: HIGH — derived from live control flow.
- RAM ceiling: HIGH — baseline build executed this session.

**Research date:** 2026-06-01
**Valid until:** ~2026-07-01 (stable in-repo domain; re-confirm only if the ADR or `platformio.ini`
Leonardo buffer pin changes).


---

## Framing-3 Scope Deep Trace (operator addendum)

**Appended:** 2026-06-01 · **Author:** trace-and-confirm pass on branch `v1.10-serial-transport-hardening` · **Status:** validates Open Q1; does NOT re-litigate the frozen COBS/CRC8/`0x00` mechanism.

### RECOMMENDATION — **Option A.** (one-paragraph justification)

Re-frame **only** the host→fw WRITE-receive path (`rurp_communication_read_data`, which IS the literal 2 s `len_u16`-corruption cascade source at `rurp_serial_utils.cpp:59-66`) and rewrite the dormant `rurp_communication_write` as its COBS-encode counterpart for symmetry/testability — and leave the fw→host EPROM-READ data stream on its existing `MSG_DATA_CHUNK` magic-preamble frame, untouched. The live call graph is unambiguous: EPROM reads do **not** flow through `rurp_communication_write`; they flow through `rurp_log_id_wide(MSG_DATA_CHUNK,…)` over the `[0xAA55AA55]…[0x0A]` log/telemetry frame that CONTEXT.md §"Out of scope" and ADR §4.2 both freeze as UNCHANGED. Option A delivers the entire SC1 anti-cascade win (the cascade lives on the WRITE path), satisfies FRAME-01..04 + CRC-01 as written, and never touches the frozen log/telemetry boundary. Option B (migrating reads onto a new COBS `0x00` data frame) is the only path that *contradicts* the locked CONTEXT.md scope, roughly doubles the dual-repo diff, and buys no cascade-elimination the WRITE-path change doesn't already deliver — because the read frame is already self-delimiting and length-authoritative, it has no `len_u16`-corruption-into-2 s-timeout failure mode to fix.

> **Verdict line is at the very bottom of this addendum.**

---

### Trace Target 1 — The EPROM-READ emit path (fw→host), end to end

**CONFIRMED: read data leaves the firmware via `rurp_log_id_wide(MSG_DATA_CHUNK,…)` over the magic-preamble log/telemetry frame — NOT via `rurp_communication_write()`.**

Call chain (all `firestarter/src/…`, branch `v1.10-serial-transport-hardening`):

1. `eprom_read()` → `op_execute_stateful_operation(_process_outgoing_data, handle)` — **`eprom_operations.cpp:19-21`**.
2. `_process_outgoing_data()` runs the chip-read main op, then emits the chunk — **`eprom_operations.cpp:110-121`**:
   - `LOG_DATA_ID(MSG_DATA_SENDING);` — batch-start signal (`eprom_operations.cpp:113`).
   - `rurp_log_id_wide(MSG_DATA_CHUNK, (const uint8_t*)handle->data_buffer, (uint16_t)handle->data_size);` — **`eprom_operations.cpp:114-116`** — the actual chip bytes.
3. `rurp_log_id_wide` is the W-04 wide ID-frame emitter (Uno strong override `uno_rurp_shield.cpp:88-90`; weak default `rurp_serial_utils.cpp:277`), which writes the `[0xAA55AA55][len_u16][id][params][crc8][0x0A]` frame documented at `rurp_serial_utils.cpp:97-103`. This is **Framing 4 (log/telemetry)**, frozen UNCHANGED by ADR §4.2.

`rurp_communication_write()` appears **nowhere** in the read path. There is exactly one in-tree caller of it (Target 2). The prior research summary (lines 17-24) is correct; this trace re-confirms it line-for-line.

---

### Trace Target 2 — Is `rurp_communication_write()` actually dead?

**CONFIRMED DEAD in all shipping envs (`uno`, `uno328pb`, `leonardo`) and in `native`.**

Full caller enumeration (`grep -rn rurp_communication_write firestarter/src firestarter/include`):

| Site | Role |
|------|------|
| `rurp_serial_utils.cpp:81` | definition |
| `rurp_serial_utils.h:35`, `rurp_shield.h:75` | declarations |
| **`operation_utils.cpp:322`** | **the only call site** |

The sole call site is inside `_check_response()`, `case RESPONSE_CODE_DATA:` — **`operation_utils.cpp:321-323`**:
```c
case RESPONSE_CODE_DATA:
    rurp_communication_write(handle->data_buffer, handle->data_size);
    break;
```

Reachability of `RESPONSE_CODE_DATA` (`grep -rn RESPONSE_CODE_DATA`): the value is **only ever assigned** at one place — **`memory.cpp:413`** — and that assignment is behind a guard that is **commented out**:
```c
// memory.cpp:411-413
// #define RAW_DATA_PROGRESS          <-- commented out
#ifdef RAW_DATA_PROGRESS
    handle->response_code = RESPONSE_CODE_DATA;   // line 341 — never compiled
```

`RAW_DATA_PROGRESS` is defined **nowhere else** — confirmed by `grep -rn RAW_DATA_PROGRESS` over `*.cpp/*.h/*.c` and `platformio.ini`: the only two hits are the commented `#define` (`memory.cpp:411`) and its own `#ifdef` (`memory.cpp:412`). It is **not** in `[env]`, `[env:uno]`, `[env:uno328pb]`, `[env:leonardo]`, or `[env:native]` build_flags (`platformio.ini:18,31,40,57,67`; each env's `build_flags` inherits `${env.build_flags}` which contains only `MONITOR_SPEED`, `HARDWARE_REVISION`, `DEV_TOOLS`, board name, `SERIAL_ON_IO`, and per-env `DATA_BUFFER_SIZE` — no `RAW_DATA_PROGRESS`).

**Conclusion:** with `RAW_DATA_PROGRESS` undefined in every env, `memory.cpp:413` is never compiled, so `handle->response_code` is never set to `RESPONSE_CODE_DATA`, so `operation_utils.cpp:322` is never reached. `rurp_communication_write()` is dead in `uno`, `uno328pb`, `leonardo`, and `native`. (Assumption A1 in the main research is hereby upgraded from "verified this session, risk LOW" to **VERIFIED — dead in all envs**.)

---

### Trace Target 3 — What the host expects on the READ path

**CONFIRMED: the host receives chip data on reads as `MSG_DATA_CHUNK` magic-preamble frames — it does NOT parse a `[len_u16][xor][payload]` data block on the read path. That `[len_u16][xor]` block exists ONLY on the host→fw WRITE *send* direction.**

Read-path receive (`firestarter_app/firestarter/…`):
- `_main_phase_read_data()` — **`eprom_operations.py:395-447`** — loops on `self.comm.get_response()` and, for a `DATA` response with `response.payload is not None`, treats `response.payload` as the raw chip bytes of a `MSG_DATA_CHUNK` frame (`eprom_operations.py:428-438`), then `send_ack()`. The docstring (`eprom_operations.py:404-409`) states this verbatim: "the firmware now wraps each chip-byte chunk inside a MSG_DATA_CHUNK ID frame instead of emitting raw bytes."
- `response.payload` is populated by `_read_and_parse_lines()` → `_decode_id_frame()` over the magic-preamble frame — **`serial_comm.py:224-336`**: it matches `MAGIC_PREAMBLE` (`serial_comm.py:251,269-275`), reads the length-authoritative body (`serial_comm.py:301`), consumes the `0x0A` anchor (`serial_comm.py:313-322`), and yields `Response(..., payload=decoded.payload)` (`serial_comm.py:324-334`). `MAGIC_PREAMBLE = b"\xaa\x55\xaa\x55"` (`frame_parser.py:25`).

WRITE-path send (the `[len_u16][xor]` block — note: **send**, not receive):
- `_main_phase_send_data()` — **`eprom_operations.py:357-391`** — builds `header = b"#" + len(data_chunk).to_bytes(2,"big") + checksum.to_bytes(1)` with `checksum = functools.reduce(operator.xor, data_chunk, 0)` (`eprom_operations.py:379-382`) and `send_bytes(header + data_chunk)` (`eprom_operations.py:390`). Its own comment (`eprom_operations.py:384-389`) names the firmware counterpart: `rurp_communication_read_data` in `rurp_serial_utils.cpp`.

**Implication for scope:** there is **no host-side `[len_u16][xor]` decoder on the read path to migrate** — the only host code that constructs/parses the bare data-block frame is the WRITE *send* side (`_main_phase_send_data`) paired with firmware `rurp_communication_read_data`. So migrating reads to COBS (Option B) would require **inventing a brand-new host-side COBS data-frame receive path** that has no current counterpart, *in addition to* re-plumbing `_read_and_parse_lines`/`_main_phase_read_data` off `MSG_DATA_CHUNK`. Option A, by contrast, has its host counterpart already located and minimal (change the frame *contents* in `_main_phase_send_data` + add a `cobs_decode` helper; firmware `rurp_communication_read_data` rewrite).

---

### Trace Target 4 — Reconcile ADR vs live code

**ADR text that assigns Framing 3 / `rurp_communication_write` to Phase 50** (quoted verbatim):

- §4.2 (lines 173-176): "The new framing applies to: … - Framing 2 (host→fw data block): Phase 50 / - **Framing 3 (fw→host data block): Phase 50**". And §4.2 lines 178-181: "Framing 4 (fw→host log/telemetry: `[0xAA55AA55][len_u16][id][params][crc8][0x0A]`) is **UNCHANGED in v1.10**. … The `_firestarter_emit_frame` path … and the `[0xAA55AA55]` log/telemetry format are not modified."
- §4.6 per-file change map (line 236): for `rurp_serial_utils.cpp`, Phase 50 — "**Replace `rurp_communication_write()` and `rurp_communication_read_data()`** with COBS streaming encoder/decoder functions that emit/consume a `0x00` frame delimiter…".

**How it diverges from the live call graph:** The ADR's mental model is that "Framing 3 (fw→host data block)" is the function `rurp_communication_write()`. In the live code, `rurp_communication_write()` is **dead** (Target 2) and the **actual** fw→host data block — the EPROM-read chip stream — rides `MSG_DATA_CHUNK` over the very `[0xAA55AA55]…[0x0A]` frame the same ADR §4.2 freezes as Framing 4 "UNCHANGED." So the ADR simultaneously (a) tells Phase 50 to re-frame "Framing 3 = `rurp_communication_write`" and (b) freezes the frame that *actually* carries fw→host reads. These can only be reconciled if "Framing 3 = `rurp_communication_write`" refers to the **dormant** data-write function, not the live read path.

**Best-evidenced reading: (a) + (b combined) — the ADR is naming the *historical/contract* data-block writer, and §4.6's "Replace `rurp_communication_write()`" is a contract-completeness rewrite of currently-dormant code, NOT a directive to move live EPROM reads off `MSG_DATA_CHUNK`.** Evidence for this reading over a "the ADR wants reads migrated" reading: §4.2 explicitly and separately freezes the `[0xAA55AA55]…[0x0A]` frame and `_firestarter_emit_frame`; if the ADR intended to move the read stream (which uses `rurp_log_id_wide`, a sibling of `_firestarter_emit_frame` on that same frozen path), it would be self-contradictory. The coherent interpretation is that the ADR pairs `rurp_communication_read_data` (live WRITE-receive, the cascade source) with `rurp_communication_write` (its dormant encode mirror) as "the data-block path," authored from the function-name/contract layout rather than the post-Phase-8 live call graph (which moved reads to `MSG_DATA_CHUNK` per the State-of-the-Art table, main research line 372). This is exactly Open Q1's tension, now resolved by direct citation. **Action: record an ADR/STATE errata noting "Framing 3 fw→host *reads* are carried by MSG_DATA_CHUNK and remain UNCHANGED; the §4.6 `rurp_communication_write` rewrite is dormant-contract symmetry, not the live read path."**

---

### Trace Target 5 — Cost/risk of each option, concretely

#### Option A — re-frame WRITE-receive + rewrite dormant write encoder; leave reads on `MSG_DATA_CHUNK`

Files/functions touched:

| Repo / file | Function | Change |
|-------------|----------|--------|
| `firestarter/src/boards/rurp_serial_utils.cpp` | `rurp_communication_read_data()` (44-79) | Replace `[len_u16][xor]`+2 s loop with streaming COBS decode-in-place + CRC8 + drain-to-`0x00` on error. **Removes the 2 s `timeout_ms` loop (62-69) — the SC1 win.** |
| `firestarter/src/boards/rurp_serial_utils.cpp` | `rurp_communication_write()` (81-93) | Rewrite as streaming COBS encode + CRC8 + `0x00` delimiter (dormant-but-contract-correct mirror). |
| `firestarter/src/operation_utils.cpp` | `op_get_message` `case '#'` (159-171) | **Surface unchanged** (still `res<0 → OP_MSG_ERROR`); the rewritten decode just needs the `available()<4` precheck relaxed/adjusted to delimiter-driven (planner detail). |
| `firestarter_app/firestarter/eprom_operations.py` | `_main_phase_send_data` (357-391) | Change frame *contents*: `crc=_crc8_ccitt(chunk)`, `body=cobs_encode(chunk+bytes([crc]))`, `frame=b"#"+body+b"\x00"`, one `send_bytes` (390). |
| `firestarter_app/firestarter/frame_parser.py` | new `cobs_encode`/`cobs_decode` | Add COBS helpers; reuse `_crc8_ccitt`/`_build_crc8_table` (28-50) UNCHANGED (CRC-01/D-05). |

Requirement coverage **without touching log/telemetry framing**:
- **SC1 / cascade**: the 2 s loop is on the WRITE-receive path (`rurp_serial_utils.cpp:59-66`); removing it there eliminates the cascade. ✔
- **FRAME-01**: `[len_u16][xor]` → `[COBS(payload+CRC8)][0x00]` on the data block, **both directions of the data-block path** (`read_data` decode + `write` encode). ✔ (Note: "both directions" = the two ends of the *write* data block + the dormant encode; the *read chip stream* is a different frame, see FRAME-03 note in Target 6.)
- **FRAME-02**: drain-to-`0x00` on CRC/COBS fail in `rurp_communication_read_data` + host `cobs_decode` raising; bounded to one frame (main research Pattern 3 directive). ✔
- **FRAME-03**: streaming, no second ~512 B buffer, <545 B Uno (decode-in-place). ✔
- **FRAME-04**: full 512/1024 B payloads on the WRITE block; COBS is size-agnostic. ✔
- **CRC-01**: CRC8-CCITT poly 0x07 reused, tables unchanged. ✔
- **Log/telemetry boundary `[0xAA55AA55]…[0x0A]`**: **NOT touched** — `_firestarter_emit_frame`, `rurp_log_id_wide`, `_read_and_parse_lines` magic-preamble demux all unchanged. ✔ Honors CONTEXT.md "Out of scope" + ADR §4.2.

#### Option B — ALSO migrate fw→host READ data block off `MSG_DATA_CHUNK` onto a new COBS `0x00` frame

Additional files/functions touched **on top of Option A**:

| Repo / file | Function | Added change |
|-------------|----------|--------------|
| `firestarter/src/eprom_operations.cpp` | `_process_outgoing_data` (110-131) | Replace `rurp_log_id_wide(MSG_DATA_CHUNK,…)` (119-121) with a new COBS data-frame emitter — i.e. divert the read stream off the frozen `[0xAA55AA55]…[0x0A]` frame. |
| `firestarter/src/boards/…` | new fw COBS read-frame emitter | New emit function (or reuse the rewritten `rurp_communication_write`) wired into the read path. |
| `firestarter_app/firestarter/serial_comm.py` | `_read_and_parse_lines` (224-336) | Add a **second** framing discipline: demux a COBS `0x00` data frame *alongside* the magic-preamble + `0x0A`-text disciplines already multiplexed on one byte stream. |
| `firestarter_app/firestarter/eprom_operations.py` | `_main_phase_read_data` (395-447) | Re-plumb from `response.payload` (MSG_DATA_CHUNK) to the new COBS data-frame receive. |

**Does Option B contradict the locked CONTEXT.md scope? YES.** CONTEXT.md "Out of scope" line 28: "The fw→host log/telemetry framing (`[0xAA55AA55]…[0x0A]`) — **UNCHANGED in v1.10**." The live read stream *rides that exact frame* (Target 1). Diverting reads off `MSG_DATA_CHUNK` necessarily either (i) modifies/forks the `[0xAA55AA55]…[0x0A]` path, or (ii) introduces a competing `0x00`-delimited frame interleaved on the same UART that the host's `_read_and_parse_lines` magic-preamble/`0x0A` demux must now disambiguate from log frames — both of which cross the frozen boundary. It also re-opens the SAFE-01 surface (a fw-emitted `0x00` during reads) that the ADR §1 proof scoped to Phase 51 command direction only.

**Added diff surface vs Option A:** Option A ≈ 2 firmware functions + 1 host function edited + 2 host COBS helpers. Option B adds ≥ 2 more firmware edits (read emitter + wiring) and ≥ 2 more host edits (a new RX framing discipline in the most delicate function, `_read_and_parse_lines`, plus `_main_phase_read_data` re-plumb) — **roughly 2× the dual-repo diff** and concentrated in the highest-risk RX demux. For **zero** additional cascade-elimination: the read frame is length-authoritative + self-delimiting (`MAGIC`+`len_u16`+`0x0A`), so it has no `len_u16`-corruption→2 s-timeout failure mode to remove (that mode is exclusive to the bare WRITE block).

---

### Trace Target 6 — Does Option A leave any FRAME-03 requirement unsatisfied?

**FRAME-03 verbatim** (`.planning/REQUIREMENTS.md:20`):
> "**FRAME-03**: The firmware encoder/decoder is streaming — no second ~512 B encode buffer is materialized; the change fits the Uno ~545 B free-RAM ceiling, proven by a post-change `pio run -e uno` RAM report (D-04)."

**Judgment: Option A literally satisfies FRAME-03 as written.** FRAME-03 is a property of *the firmware encoder/decoder* (streaming, no second buffer, RAM ceiling) — it does **not** name the read path, does **not** require the EPROM-read chip stream to move off `MSG_DATA_CHUNK`, and does **not** mention Framing 3 / `rurp_communication_write`. Option A's rewritten `rurp_communication_read_data` (decode-in-place) and `rurp_communication_write` (stream-to-`SERIAL_PORT`) are exactly "a streaming firmware encoder/decoder with no second ~512 B buffer," and the post-change `pio run -e uno` RAM report (D-04, baseline 1503/2048 B → 545 B free, main research line 308-311) discharges the ceiling clause. Nothing in FRAME-03's wording demands the READ path move. (FRAME-04's "1024 B Leonardo" caveat — currently a 512 B A/B-test pin in `platformio.ini:65` — is the only buffer-related watch-item, already flagged in the main research Project Constraints; it is orthogonal to the read-vs-write scope question.)

The companion requirements confirm the read path need not move: **FRAME-01** targets "the … data-block path … bare `[len_u16][xor][payload]` frame boundary" — which is precisely (and only) the WRITE block; the read stream never had a bare `[len_u16][xor]` boundary (it has the magic-preamble frame), so FRAME-01 has no read-path obligation either.

---

### OPERATOR VERDICT (one line)

**Choose Option A: re-frame `rurp_communication_read_data` (WRITE-receive, the 2 s cascade source) + rewrite the dead `rurp_communication_write` as its dormant COBS mirror, leave EPROM reads on the frozen `MSG_DATA_CHUNK` frame — this satisfies FRAME-01..04 + CRC-01 + SC1, honors the locked "log/telemetry UNCHANGED" scope, and avoids the ~2× higher-risk diff of Option B; record a one-line ADR/STATE errata that §4.6's `rurp_communication_write` change is dormant-contract symmetry, not the live read path.**
