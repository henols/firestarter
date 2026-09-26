# Phase 49: Framing Mechanism Decision (COBS `0x00` vs SLIP `0xC0`) — Research

**Researched:** 2026-06-01
**Domain:** Serial protocol decision analysis — custom framing mechanism selection and bus-aliasing safety proof
**Confidence:** HIGH (all material claims verified against live source code; no external packages being adopted)

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **ADOPT a custom framing layer; REJECT all off-the-shelf libraries** (§2, §4). The entire §4
  candidate survey (PacketSerial, nanocobs, cobs-c/python, SerialTransfer, MIN) is settled.
- **CRC8-CCITT poly 0x07, seed 0x00, no reflection, no final XOR — kept unchanged** (D-05).
  No polynomial swap. Framing layers on top of the existing CRC8 byte.
- **Uno-fit filter binding** (D-04): streaming encode only, **no second ~512 B encode buffer**,
  ~545 B free-RAM ceiling. **Both finalists (streaming COBS §4.3, SLIP §4.2) already pass this**
  — so RAM is *not* a differentiator between them.
- **Lockstep dual-repo mandate**: any framing change touches `rurp_serial_utils.cpp` (fw) +
  `serial_comm.py`/`frame_parser.py` (host) + `test_messages` contract together.
- **D-01 (posture):** Neutral, evidence-driven. Phase 49 builds the full COBS-vs-SLIP comparison
  from scratch and the decision record picks the winner on merit. No thumb on the scale.
- **D-02 (criteria weighting):** Let the evidence rank them. Score all four criteria: safety
  (bus-aliasing risk class), provable byte-exactness, implementation simplicity (smallest
  auditable dual-repo diff), and overhead (COBS bounded +1/254 vs SLIP 2× worst case).
- **D-03 (proof rigor):** Code/architectural proof only for SAFE-01. No hardware. Resolved
  entirely within Phase 49.
- **D-04 (decisive fallback):** Inconclusive static proof → SLIP wins.
- **D-05 (artifact):** Write a new standalone ADR — `.planning/v1.10-FRAMING-DECISION.md` —
  that resolves COBS-DECISION §2.0 / Q2 / Q3. The v1.9 doc stays immutable.
- **D-06 (frozen contract):** Lock the full frame contract: delimiter byte, escape/run-length
  scheme, exact frame layout (CRC8 placement), per-file change map for all 4 files.

### Claude's Discretion

- Exact ADR filename and section structure (within the cross-link + immutability constraints).
- The specific scoring scale / matrix presentation format for D-02 (as long as all four
  criteria are scored and the aggregate ranking is shown).

### Deferred Ideas (OUT OF SCOPE)

- **Hardware/bench confirmation of the SAFE-01 timing guarantee** — explicitly NOT in Phase 49
  (D-03 keeps it a static proof). Any residual hardware confidence rides Phase 53.
- **Implementing the chosen framing** — Phase 50 (data path) / Phase 51 (command channel).
- `serial-cobs-resync-data-path.md` todo — re-pointed to Phase 50 (implementation); the
  evaluation it asked for is complete.
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| SAFE-01 | The SERIAL_ON_IO `0x00` bus-aliasing risk (COBS-DECISION Open Q2) is resolved and documented — either a code/architectural proof that the host cannot emit a `0x00` frame-boundary byte during the programmer↔communication mode transition window (COBS path), or adoption of SLIP's `0xC0` delimiter (Q3). Load-bearing because Phase 51 means the host now actively emits delimiter bytes on host→fw. | Verified firmware gate in `uno_rurp_shield.cpp`; verified host TX path in `serial_comm.py`; SAFE-01 proof structure detailed in §"SAFE-01 Static Proof Analysis" below. |
</phase_requirements>

---

## Summary

Phase 49 is a pure **decision and analysis** phase. It produces a binding ADR
(`.planning/v1.10-FRAMING-DECISION.md`) that chooses between two framing finalists —
streaming COBS (`0x00` delimiter) and SLIP/RFC-1055 (`0xC0` delimiter) — on a scored,
neutral evidence matrix, and resolves the SAFE-01 `0x00` bus-aliasing safety question via
static code proof. No code is written; the deliverable is a frozen frame contract document.

The code analysis performed here establishes the concrete facts the ADR author needs: the
firmware-side `com_mode` gate is verified and fully characterised; the host TX path is
verified and the SAFE-01 proof is structurally straightforward — it turns on whether
`send_json_command` (which today sends bare ASCII JSON with no `0x00` bytes) can be extended
to emit COBS-framed commands that include a trailing `0x00` delimiter while the firmware is
momentarily in programmer mode. The proof requires tracing the call chain from `_probe_port`
through `send_json_command`, confirming that no `0x00` byte is ever sent by the host except
as an explicit COBS frame delimiter, and that the host cannot race to send that delimiter
while the firmware's `com_mode` is `false`. This proof is achievable statically — it is
neither easy nor obviously inconclusive — and its outcome determines whether COBS or SLIP
wins under D-04.

The current frame layout (`rurp_serial_utils.cpp`) uses a length-prefix scheme for data
blocks and a magic-preamble scheme for log/telemetry. Both finalists add a delimiter layer
on top. The per-file change map is concrete and limited to four files.

**Primary recommendation:** Structure the ADR execution into three sequential tasks: (1)
perform the SAFE-01 static proof, (2) score the evidence matrix with the proof result as a
key input to the safety criterion, (3) write the full frozen frame contract. The decision
CAN and SHOULD be made at execute-time within Phase 49 — there is no blocker.

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| SAFE-01 static proof (firmware half) | Firmware (`uno_rurp_shield.cpp`) | — | `com_mode` gate and DDRD transitions live entirely in firmware; host has no visibility into or control over this state |
| SAFE-01 static proof (host half) | Host Python (`serial_comm.py`) | — | Host TX path is Python-only; the question is whether the Python code can emit `0x00` during the firmware's programmer-mode window |
| Scored evidence matrix | ADR document | — | Decision artifact, not code; both sides of the dual-repo are inputs but the matrix itself lives in the planning doc |
| Frozen frame contract | Planning doc (ADR) | Both repos (Phase 50+) | Spec lives in the ADR; implementation in Phase 50's code changes |
| CRC8-CCITT integrity layer | Both repos (existing code) | — | Table in `rurp_serial_utils.cpp` (PROGMEM) and computed in `frame_parser.py`; unchanged by Phase 49 |
| `{`-peek command ingest (FRAME-05 target) | Firmware (`firestarter.cpp` loop) | — | Lines 162-172 of `firestarter.cpp` — the path Phase 51 will replace; Phase 49 records it in the change map |
| Test contract (pinning frame layout) | Firmware `test_messages` Unity suite | Host parser tests | `test_rurp_log_id.cpp` pins the current frame byte-for-byte; Phase 52 updates it |

---

## Standard Stack

No external packages are adopted in this phase. The "stack" is the existing codebase under analysis.

### Core Artifacts Under Analysis

| File | Location | Role in Phase 49 |
|------|----------|-----------------|
| `rurp_serial_utils.cpp` | `firestarter/src/boards/` | Contains current frame layout; per-file change map target for Phase 50 |
| `uno_rurp_shield.cpp` | `firestarter/src/boards/` | Firmware half of SAFE-01 proof: `com_mode` gate, `rurp_set_programmer_mode()`, `rurp_set_communication_mode()` |
| `serial_comm.py` | `firestarter_app/firestarter/` | Host half of SAFE-01 proof: all TX paths (`send_json_command`, `send_bytes`, `send_string`, `send_ack`, `send_done`) |
| `frame_parser.py` | `firestarter_app/firestarter/` | CRC8-CCITT table; per-file change map target for Phase 50 |
| `firestarter.cpp` (lines 162-172) | `firestarter/src/` | Current `{`-peek command-ingest loop; change map entry for Phase 51 |
| `test_rurp_log_id.cpp` | `firestarter/test/native/avr/test_messages/` | `test_messages` Unity suite; change map entry for Phase 52 |

### No Package Legitimacy Audit Required

This phase installs no external packages. No `npm install`, `pip install`, or library adoption
occurs. The Package Legitimacy Gate is skipped.

---

## Architecture Patterns

### The Four Coexisting Framings (Current State)

[VERIFIED: live code review of `rurp_serial_utils.cpp` and `firestarter.cpp`]

```
Direction             File                          Current Framing
──────────────────────────────────────────────────────────────────────────────
host→fw JSON command  firestarter.cpp:162-172       ASCII JSON; fw peeks '{',
                                                    discards non-'{' bytes
host→fw data block    rurp_serial_utils.cpp:44-79   [len_u16 big-endian]
                                                    [xor_checksum][payload]
                                                    2 s timeout
fw→host data block    rurp_serial_utils.cpp:81-93   same [len_u16][xor][payload]
fw→host log/telemetry rurp_serial_utils.cpp:92-224  [0xAA55AA55][len_u16][id]
                                                    [params][crc8][0x0A]
                                                    (magic preamble, CRC8-CCITT)
```

**Note on scope:** The fw→host log/telemetry framing (#4) is explicitly OUT OF SCOPE for
v1.10 (per REQUIREMENTS.md "Out of Scope"). It already self-delimits. Phases 50-51 touch
framings #1 (host→fw JSON command) and #2/#3 (data blocks).

### Current Data-Block Frame Layout

[VERIFIED: `rurp_serial_utils.cpp` lines 44-93, `_firestarter_emit_frame` lines 138-184]

**host→fw data block (read by `rurp_communication_read_data`):**
```
Byte 0    : len_u16 MSB  (big-endian)
Byte 1    : len_u16 LSB
Byte 2    : xor_checksum (XOR of all payload bytes)
Bytes 3…N : payload (N = len_u16 bytes)
```
The firmware loops with a 2-second timeout reading payload bytes until `len` bytes received.
No delimiter byte. Desync on corrupted `len_u16` is the resync motivation.

**fw→host data block (written by `rurp_communication_write`):**
```
Byte 0    : size >> 8 (MSB)
Byte 1    : size & 0xFF (LSB)
Byte 2    : XOR checksum
Bytes 3…N : payload
```
Same structure in the opposite direction.

### Current Log/Telemetry Frame Layout

[VERIFIED: `rurp_serial_utils.cpp` comment block lines 97-104, `_firestarter_emit_frame` lines 138-184]

```
Bytes 0-3  : 0xAA 0x55 0xAA 0x55  (magic preamble)
Bytes 4-5  : len_u16 big-endian    (= 1 + param_count + 1, i.e. id + params + crc)
Byte 6     : id
Bytes 7…N  : params (MSB-first per type)
Byte N+1   : CRC8-CCITT over [id, params]  (poly 0x07, seed 0x00, no refl, no final XOR)
Byte N+2   : 0x0A re-sync anchor (NOT a delimiter; len is authoritative)
```

The `test_messages` Unity suite (`test_rurp_log_id.cpp`) pins this exact byte sequence. Any
Phase 50/52 change to the framing must update these tests.

### SAFE-01 Static Proof Analysis

This is the most load-bearing research finding. The analysis is split into firmware half and
host half.

#### Firmware Half — `com_mode` Gate

[VERIFIED: live code review of `uno_rurp_shield.cpp`]

The firmware gate operates as follows:

```c
// rurp_set_programmer_mode() — called when an EPROM operation begins:
void rurp_set_programmer_mode() {
    com_mode = false;       // FIRST: flag communication is off
    rurp_serial_end();      // THEN: ends Serial (UART disabled, PD0 now available as output)
    DDRD |= 0x01;           // THEN: sets PD0 to output mode (data bus bit 0)
}

// rurp_set_communication_mode() — called when operation completes:
void rurp_set_communication_mode() {
    PORTD |= 0x01;          // Set PD0 HIGH (prevents false UART start bit)
    DDRD &= ~(0x01);        // PD0 back to input
    rurp_serial_begin(MONITOR_SPEED);   // Re-enable UART
    while (SERIAL_PORT.available()) SERIAL_PORT.read();  // drain RX buffer
    com_mode = true;        // LAST: communication mode restored
}

// The strong override gates ALL frame emission:
void rurp_log_id(uint8_t id, const uint8_t* params, uint8_t param_count) {
    if (com_mode) {                          // gate: no emission if com_mode=false
        _firestarter_emit_frame(id, params, param_count);
    }
}
// Same gate for rurp_log_id_wide.
```

**Firmware-half conclusion:** While `com_mode = false`, the firmware emits NO bytes on the
serial line — including any `0x00` COBS frame delimiter. This is architecturally guaranteed,
not probabilistic. The UART is disabled by `rurp_serial_end()` before `DDRD` flips, so the
Uno cannot physically receive serial bytes into the RX ring buffer while in programmer mode.

**Critical observation for the host-half proof:** `rurp_set_communication_mode()` calls
`rurp_serial_begin()` (re-enables UART) and then drains any bytes that leaked into the RX
ring buffer (the spurious-byte defense described in the comment). This drain happens with
`while (SERIAL_PORT.available()) SERIAL_PORT.read()`. If the host emits a `0x00` byte during
the window between `rurp_serial_end()` and `rurp_serial_begin()`, that byte is lost to the
UART (not received). If the host emits `0x00` in the window *after* `rurp_serial_begin()` but
*before* the drain completes, it would land in the RX buffer and be drained as a stale byte —
not parsed as a frame delimiter (the firmware only parses commands when `CMD_IDLE` and peeking
for `{`). This means the key question is sharper than it first appears:

> Can the host emit a `0x00` COBS frame delimiter **that the firmware would then interpret as a
> frame-start byte** while `com_mode` is false or transitioning?

Given the current `{`-peek command path (`firestarter.cpp:162-172`), the firmware discards any
non-`{` byte. A `0x00` byte, even if received, is discarded. Under COBS framing with Phase 51's
command-channel migration, this changes: the firmware would instead parse the incoming byte as
a COBS frame delimiter, triggering frame ingestion. This is why the host-half proof is required
specifically in the context of Phase 51's command-channel framing — it is not a concern today,
but becomes load-bearing when the command channel is framed.

#### Host Half — TX Path Analysis

[VERIFIED: live code review of `serial_comm.py`]

All host-to-firmware transmission goes through one of these methods:

```python
def send_bytes(self, data_bytes: bytes) -> int:
    # Lowest-level — writes raw bytes to serial port

def send_string(self, data_string: str, encoding: str = "ascii") -> int:
    # Encodes string (ASCII by default) → send_bytes

def send_json_command(self, command_dict: dict) -> int:
    # json.dumps(..., separators=(",",":")) → send_string
    # json_data = json.dumps(command_dict, separators=(",", ":"))
    # → send_string(json_data)

def send_ack(self) -> None:
    # send_string("OK")

def send_done(self) -> None:
    # send_string("DONE")
```

**Current state (pre-Phase 51):** `send_json_command` serializes a Python `dict` to compact
JSON using `json.dumps`. JSON output is valid ASCII and contains **zero `0x00` bytes by
construction**. JSON does not emit null bytes; the only bytes in the output are printable ASCII
(0x20-0x7E). `send_ack("OK")` and `send_done("DONE")` are likewise pure ASCII. `send_bytes`
is the only path that could emit arbitrary bytes — and it is only called by `send_string` today.

**Protocol sequence during mode transition:** The host sends a JSON command to start an EPROM
operation. The firmware parses it, calls `rurp_set_programmer_mode()`, performs the operation
(which may be long: a 64 KB read), then calls `rurp_set_communication_mode()`, and sends a
response ("OK: ..." or "ERROR: ..."). The host is **blocked waiting for a response** during the
entire programmer-mode window — it calls `_read_and_parse_lines()` which loops on
`self.connection.read(1)`. The host does NOT transmit any bytes while waiting for a response.

**The SAFE-01 proof structure for COBS:**

After Phase 51 framing migration, `send_json_command` would wrap the JSON payload in a COBS
frame and append a `0x00` delimiter byte. The sequence would be:

1. Host sends COBS-framed JSON command (payload + CRC8 + COBS encoding + `0x00` terminator)
2. Firmware receives frame, decodes, parses JSON, begins operation, calls `rurp_set_programmer_mode()`
3. Firmware executes operation (UART disabled, com_mode=false)
4. Firmware calls `rurp_set_communication_mode()`, drains RX, sends response
5. Host reads response, proceeds

The critical question: **can step 1's `0x00` terminator byte arrive at the firmware after
step 2 has begun?**

Answer from code analysis: `send_json_command` calls `send_bytes` which calls
`self.connection.write(data_bytes)` followed by `self.connection.flush()`. The `flush()` call
blocks until all bytes are physically transmitted. At 250000 baud, a COBS-framed JSON command
of ~200 bytes takes ~8 ms to transmit. The `0x00` frame delimiter is the **last byte** of the
`send_json_command` call. After `flush()` returns, the host enters the response-reading loop
and does NOT transmit again.

The firmware's `init_programmer()` (called from the loop when `CMD_IDLE` and peek=`{`) must
fully receive and parse the JSON command before calling `rurp_set_programmer_mode()`. Under the
current protocol, `rurp_communication_read_data` is called to read subsequent data blocks, not
the command itself. The command is received byte-by-byte via `rurp_communication_peak()` /
`rurp_communication_read()` — so by the time `rurp_set_programmer_mode()` is called, the
command bytes have already been consumed from the RX buffer.

**Where the proof is structurally easy:**
- The `0x00` byte is always the last byte of the host transmission.
- After `flush()`, the host goes silent.
- The firmware does not enter programmer mode until after consuming and parsing the command.
- Therefore the `0x00` delimiter byte is consumed/drained before or at the point programmer
  mode begins — it cannot arrive as a false frame delimiter during programmer mode.

**Where the proof requires care (potential inconclusiveness):**
- The analysis above assumes COBS framing of the command channel (Phase 51). Under Phase 50's
  data-path-only framing, the command channel still sends bare ASCII JSON, which contains no
  `0x00` bytes. SAFE-01 is only load-bearing for the Phase 51 command-channel case.
- The proof depends on pyserial's `flush()` guarantee that bytes are physically written before
  returning. This is a pyserial implementation detail, not a Python language guarantee. It is
  almost certainly correct (pyserial `flush()` is documented to wait for transmission), but the
  executor performing the static analysis should confirm this with the pyserial docs.
- The analysis assumes the COBS frame delimiter (`0x00`) is emitted as part of the same
  `send_bytes` call as the rest of the frame, not in a separate subsequent `write()`. If the
  implementation splits the delimiter into a second write, there is a window. The frame
  contract must specify that the entire framed command including the delimiter is written as a
  single `send_bytes` call.
- The `rurp_set_communication_mode()` drain loop (`while (SERIAL_PORT.available())
  SERIAL_PORT.read()`) runs after `rurp_serial_begin()`. If the host's `0x00` byte somehow
  arrives in the RX buffer during the transition window and is drained rather than parsed,
  it is harmless — but under Phase 51's framing, the firmware will only parse frames from the
  `CMD_IDLE` loop, and the drain discards bytes before the loop can parse them. This is safe.

**Summary of host-half SAFE-01 proof status:**
The static analysis reveals a structurally **provable** case, not an inconclusive one —
but the proof has three specific sub-claims the executor must verify during the Phase 49
execute-time analysis:

| Sub-claim | What to verify | Source |
|-----------|---------------|--------|
| pyserial `flush()` guarantees transmission before return | pyserial docs, or inspection of CPython serial extension | pyserial documentation |
| COBS delimiter is included in same `send_bytes` call as frame body | Confirmed by the Phase 50 implementation design (not yet written; the frame contract must mandate it) | Implementation design decision |
| Firmware consumes command payload from RX buffer before calling `rurp_set_programmer_mode()` | Trace `init_programmer()` call chain in `firestarter.cpp` | `firestarter.cpp` (not shown in detail — read during execute-phase analysis) |

If all three sub-claims are confirmed, the SAFE-01 proof succeeds and COBS is not
disqualified on safety grounds. If any sub-claim cannot be confirmed statically, D-04 applies:
SLIP wins.

### Anti-Patterns to Avoid

- **Separating the `0x00` delimiter into a second serial write call**: would open a timing
  window between frame body and delimiter. The frame contract must mandate atomic write.
- **Designing the matrix with safety as a binary gate rather than a scored criterion**: D-02
  requires scoring all four criteria; safety is one of them, not a pre-filter.
- **Making the ADR a narrative without a scored table**: CONTEXT.md Success Criterion 1
  explicitly rejects a bare assertion. The matrix must be present with all four criteria
  scored and aggregate ranking shown.

---

## The Evidence Matrix — Structure and Inputs

The planner must structure tasks so the ADR executor populates this matrix based on the
SAFE-01 proof outcome. The matrix criteria are fixed (D-02); the scoring scale is Claude's
discretion.

### Recommended Matrix Format

```
Criterion            | COBS (0x00)                     | SLIP (0xC0)
─────────────────────────────────────────────────────────────────────────
Safety / bus-aliasing| [Low risk IF proof passes;       | [No risk — 0xC0 never
risk class           |  Medium-High if inconclusive]    |  appears on data bus]
─────────────────────────────────────────────────────────────────────────
Provable byte-       | [Round-trip: no ambiguity in     | [Round-trip: no ambiguity;
exactness (ease of   |  COBS if no 0x00 in encoded      |  escape-only bytes are 0xC0
round-trip + fault   |  payload by construction;        |  and 0xDB; fault injection
injection proof)     |  fault injection: corrupt a      |  straightforward]
                     |  COBS overhead byte vs data byte]|
─────────────────────────────────────────────────────────────────────────
Implementation       | [~40 fw + ~30 host lines;        | [~20 fw + ~20 host lines;
simplicity (smallest |  run-length scan per frame;      |  pure two-byte escape table;
dual-repo diff)      |  3 local vars on stack]          |  no scan; simpler decode]
─────────────────────────────────────────────────────────────────────────
Overhead             | [+1 byte per 254-byte run;       | [up to 2× expansion on
                     |  max +3 bytes for 512 B frame;   |  all-0xC0 payload; typical
                     |  deterministic]                  |  payloads: ~0% overhead]
─────────────────────────────────────────────────────────────────────────
Aggregate ranking    | [executor fills after scoring]   | [executor fills after scoring]
```

**Scoring guidance for the planner:**

- The **safety** criterion's COBS score is the most uncertain at research time — it depends
  directly on the SAFE-01 proof outcome. The planner must structure Task 1 (SAFE-01 proof)
  as a prerequisite to Task 2 (matrix scoring). The proof result gates the safety score.
- The **overhead** criterion is the least differentiating: both finalists fit 512 B Uno frames
  without re-chunking. COBS's bound of +1/254 bytes per run is actually tighter than SLIP's
  theoretical 2× worst case, but typical EPROM binary payloads have roughly equal `0x00` and
  `0xC0` byte frequencies — treat this as a near-tie unless the executor observes otherwise.
- The **implementation simplicity** criterion slightly favors SLIP: SLIP's two-byte escape
  table has no run-length scan; the decoder is simpler (no run-length state). COBS requires
  tracking the run-start position during encoding. Both are well within the ~70-line estimate
  from COBS-DECISION §4.3.
- The **byte-exactness** criterion slightly favors COBS: a COBS-encoded payload has the
  property that `0x00` cannot appear in the encoded body (by construction), so the frame
  boundary is unambiguous. SLIP's decoded payload can contain any byte, including `0xC0` if
  correctly escaped — but the escape layer is one more transformation that must be proven
  correct for the round-trip test.

### Decision-Time vs Plan-Time

The decision MUST be left to execute-time — the matrix cannot be filled and the SAFE-01
proof cannot be completed at plan-time. The planner should structure Phase 49 tasks to:

1. Perform the SAFE-01 static proof (executor reads `firestarter.cpp` `init_programmer()`,
   checks pyserial `flush()` docs, confirms atomic write design decision).
2. Score the evidence matrix with the proof result.
3. Write the ADR with the full frozen frame contract.

The decision record is the Phase 49 deliverable; the winner is determined by the matrix.

---

## Don't Hand-Roll

This phase is a documentation/analysis phase. The "don't hand-roll" principle applies to
the ADR structure rather than code:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Safety reasoning | Ad-hoc narrative | The 3-column sub-claim table (§SAFE-01 proof above) | Traceability to COBS-DECISION §5 Q2/Q3 requires the proof to mirror those section's phrasing |
| Criteria scoring | Prose opinion | Scored matrix with all 4 criteria present | CONTEXT.md Success Criterion 1 requires the matrix |
| Frame contract | Informal list | Explicit table: field name, byte offset, byte count, encoding, value | Phases 50/52 implement against this; ambiguity = bugs |
| Per-file change map | "update these files" | Explicit table listing file, change type, change description | Phases 50/51/52 executors need unambiguous task inputs |

---

## Per-File Change Map (Frozen Contract Inputs)

The ADR must include a change map for all four files. The research establishes what exists
today and what must change. The ADR executor fills in the column for the chosen mechanism.

| File | Sub-repo | Current State | Change Required (COBS) | Change Required (SLIP) |
|------|----------|---------------|----------------------|----------------------|
| `rurp_serial_utils.cpp` | `firestarter` | `[len_u16 big-endian][xor_checksum][payload]` for data blocks; `_firestarter_emit_frame` for log/telemetry. No delimiter byte in data path. | Replace `rurp_communication_write` and `rurp_communication_read_data` with COBS-encode/decode streaming functions; emit/consume `0x00` frame delimiter; keep `_firestarter_emit_frame` unchanged (log/telemetry out of scope) | Same replacement but emit/consume `0xC0` delimiter with `0xDB 0xDC` / `0xDB 0xDD` escaping; keep `_firestarter_emit_frame` unchanged |
| `serial_comm.py` | `firestarter_app` | `send_json_command` emits bare ASCII JSON. `_read_and_parse_lines` reads by byte; demuxes on MAGIC_PREAMBLE or `0x0A`. Data block read/write in `eprom_operations.py` via `serial_comm`. | Add COBS encode/decode to data block TX/RX path. After Phase 51: wrap JSON commands in COBS frame. `_read_and_parse_lines` must handle COBS frame delimiter to demux data frames from log/telemetry. | Same but add SLIP encode/decode. Escape `0xC0` and `0xDB` bytes. `_read_and_parse_lines` must handle `0xC0` delimiter. |
| `frame_parser.py` | `firestarter_app` | `_build_crc8_table()`, `_crc8_ccitt()`, `_decode_param()`, `Response`, `LogMessage`, `MAGIC_PREAMBLE`. CRC8 poly 0x07 contract. | Add COBS decode helper (or keep in `serial_comm.py`). CRC8 table unchanged. | Add SLIP decode helper. CRC8 table unchanged. |
| `test_rurp_log_id.cpp` | `firestarter` (test_messages) | Asserts exact byte sequence: `[0xAA 0x55 0xAA 0x55][len_u16][id][params][crc8][0x0A]`. Pins CRC8 poly 0x07 seed 0x00. | Add test cases for COBS-encoded data frames; frame boundary byte = `0x00`; existing log/telemetry test cases unchanged (log/telemetry not re-framed in v1.10) | Add test cases for SLIP-encoded data frames; frame boundary byte = `0xC0`; existing log/telemetry test cases unchanged |

**What the change map does NOT capture** (Phase 51 scope, not Phase 50):
`firestarter.cpp` lines 162-172 — the `{`-peek command-ingest loop. Phase 51 replaces this
with a framed-command decoder. The per-file change map for Phase 51 must add this file.

---

## Frame Contract Template

The ADR must lock the following fields. The planner should structure a task that produces
this contract section in the ADR. Research establishes the current state; the ADR executor
fills in the "chosen mechanism" column.

### Data-Block Frame (Phases 50+)

| Field | Position | Width | Current | COBS framing | SLIP framing |
|-------|----------|-------|---------|-------------|-------------|
| Frame delimiter (start) | Before payload | 1 byte | (none) | implicit: absence of `0x00` in body | `0xC0` |
| Payload (data bytes, EPROM content) | variable | N bytes | raw | COBS-encoded (no `0x00` in encoded body by construction) | SLIP-escaped (replace `0xC0`→`0xDB 0xDC`, `0xDB`→`0xDB 0xDD`) |
| CRC8-CCITT byte | After payload | 1 byte | XOR checksum (current) | CRC8 over raw payload, appended before encoding | CRC8 over raw payload, appended before escaping |
| Frame delimiter (end) | After CRC8 | 1 byte | (none) | `0x00` | `0xC0` |
| Length prefix | N/A | — | 2-byte `len_u16` | **removed** (delimiter provides boundary) | **removed** |

**Key design question the ADR must resolve:** Does the new framing include a length prefix
alongside the delimiter, or replace it entirely? The resync motivation argues for removing the
length prefix (the whole point is to not rely on it). The `test_messages` contract must
reflect whichever choice is made.

### Log/Telemetry Frame (UNCHANGED in v1.10)

Current frame unchanged. The ADR must explicitly state this for clarity.

---

## Common Pitfalls

### Pitfall 1: Conflating the Two Framing Targets

**What goes wrong:** Treating "COBS/SLIP framing" as applying to the log/telemetry path
(`_firestarter_emit_frame`), which is explicitly out of scope for v1.10.
**Why it happens:** The log/telemetry path already uses a frame-like structure (magic preamble +
len + CRC8 + `0x0A`). It's tempting to include it in the redesign.
**How to avoid:** The ADR must explicitly state that `_firestarter_emit_frame` and the
`[0xAA55AA55]...` log/telemetry format are unchanged. Only the data-block path (Phases 50, 51)
is re-framed.

### Pitfall 2: SAFE-01 Proof Scope Creep

**What goes wrong:** Attempting to prove the `0x00` bus-aliasing safety for the current
protocol (Phase 50 data path only) rather than for Phase 51's command-channel extension.
**Why it happens:** The aliasing risk exists in the current protocol too (the host already
sends data blocks that could contain `0x00` bytes), but the data-block path's `[xor_checksum]`
scheme does not use `0x00` as a frame delimiter.
**How to avoid:** The ADR must clearly scope SAFE-01 to Phase 51's command-channel framing
(where `0x00` would be an explicit delimiter in the host→fw direction) and state that Phase 50's
data-block framing has a separate, easier proof (the firmware is in `CMD_IDLE` when it receives
data block commands, and `com_mode=true` throughout data block transfers).

### Pitfall 3: Treating the Matrix as a Pre-Decided Conclusion

**What goes wrong:** Writing the ADR with a winner already in mind and constructing the
matrix to support it (confirmation bias).
**Why it happens:** COBS is the "recommended future path" from COBS-DECISION §3; SLIP is the
"simpler" and "no aliasing" option from §4.2/§5 Q3. Both documents have an opinion.
**How to avoid:** D-01 is binding — the posture is neutral. The matrix must be populated from
evidence first; the winner is whoever the aggregate score favors.

### Pitfall 4: Omitting the Length-Prefix Removal Decision from the Contract

**What goes wrong:** The new framing uses a delimiter but also retains the `len_u16` field
"for safety", making the framing a hybrid. This defeats the resync purpose (the desync bug
is caused by relying on `len_u16`).
**Why it happens:** The current log/telemetry path uses both a length field AND an anchor byte.
It's natural to copy that pattern.
**How to avoid:** The frame contract template must explicitly state whether the length prefix is
retained or removed, with rationale. If removed, the decoder relies solely on the delimiter —
which is the point.

### Pitfall 5: XOR Checksum vs CRC8 Confusion

**What goes wrong:** The current data-block path uses XOR checksum (not CRC8). The log/telemetry
path uses CRC8. Phase 50 migrates the data-block path to CRC8 (D-05: CRC8-CCITT kept).
**Why it happens:** Both are in the same file (`rurp_serial_utils.cpp`). The distinction between
`rurp_communication_read_data` (XOR checksum) and `_firestarter_emit_frame` (CRC8) is easy to miss.
**How to avoid:** The ADR frame contract must explicitly state: data-block path uses CRC8 (new,
replacing XOR) per D-05; log/telemetry path already uses CRC8 (unchanged).

---

## Code Examples

These are existing patterns from verified sources — not proposed changes.

### Current Data-Block Write (firmware) — What Phase 50 Replaces

```c
// Source: rurp_serial_utils.cpp lines 81-93
size_t rurp_communication_write(const char* buffer, size_t size) {
    uint8_t checksum = 0;
    for (size_t i = 0; i < size; i++) {
        checksum ^= buffer[i];
    }
    SERIAL_PORT.write(size >> 8);        // len_u16 MSB
    SERIAL_PORT.write(size & 0xFF);      // len_u16 LSB
    SERIAL_PORT.write(checksum);         // XOR checksum
    size_t bytes = SERIAL_PORT.write(buffer, size);  // raw payload
    SERIAL_PORT.flush();
    return bytes;
}
```

### Streaming COBS Encoder Reference (from COBS-DECISION §3)

```c
// Source: .planning/v1.9-COBS-DECISION.md §3
// Zero-extra-buffer streaming COBS encoder for AVR.
// Reads data_buffer[0..N-1], emits COBS-encoded bytes to SERIAL_PORT.
// RAM cost: 3 local variables (~6 bytes stack). Works for any N.
size_t i = 0;
while (i < N) {
    size_t run_start = i;
    uint8_t run_len = 0;
    while (i < N && data_buffer[i] != 0 && run_len < 254) { run_len++; i++; }
    SERIAL_PORT.write((uint8_t)(run_len + 1));
    SERIAL_PORT.write(&data_buffer[run_start], run_len);
    if (i < N && data_buffer[i] == 0) i++;
}
SERIAL_PORT.write((uint8_t)0x00);  /* frame delimiter */
```

### Current `{`-Peek Command Ingest — What Phase 51 Replaces

```cpp
// Source: firestarter.cpp lines 162-172 [VERIFIED]
} else if (handle.cmd == CMD_IDLE) {
    if (rurp_communication_available() > 0) {
        // Look for the start of a JSON object '{' before trying to parse.
        if (rurp_communication_peak() == '{') {
            if (init_programmer(&handle)) {
                return;
            }
        } else {
            rurp_communication_read();  // Discard non-'{' character
        }
    }
    return;
}
```

### Current Host JSON Command Send — What Phase 51 Wraps

```python
# Source: serial_comm.py lines 155-159 [VERIFIED]
def send_json_command(self, command_dict: dict) -> int:
    self._log_command_details(command_dict)
    json_data = json.dumps(command_dict, separators=(",", ":"))
    return self.send_string(json_data)
# Note: json.dumps produces ASCII-only output — zero 0x00 bytes in current implementation
```

### CRC8-CCITT Table (firmware) — What Stays Unchanged

```c
// Source: rurp_serial_utils.cpp lines 109-131 [VERIFIED]
// CRC8-CCITT (poly 0x07, seed 0x00) — precomputed table in PROGMEM
// Sanity: t[0^0x01] = t[1] = 0x07 ✓
static const uint8_t CRC8_TABLE[256] PROGMEM = { /* 256 bytes, verified */ };

static uint8_t crc8_ccitt(uint8_t crc, uint8_t b) {
    return pgm_read_byte(&CRC8_TABLE[crc ^ b]);
}
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `[len_u16][xor_checksum][payload]` for data blocks | Same (no change yet) | Phase 50 will change this | Current: 2 s timeout desync on corrupted len_u16 |
| `{`-peek command ingest with discard-on-non-`{` | Same (no change yet) | Phase 51 will change this | Current: no CRC protection on commands; robustness depends on JSON parser tolerance |
| Text-prefix log (`OK:`, `DATA:`, etc.) | ID-encoded frames with magic preamble + CRC8 (v1.2 / Phase 6) | Phase 6 (v1.2 milestone) | Host demux now byte-streaming via `_read_and_parse_lines` |

**SAFE-01 is only load-bearing for Phase 51 (command-channel framing), not Phase 50 (data-block framing).** During data-block transfers, the firmware is in `com_mode=true` throughout — `rurp_set_programmer_mode()` is called before the data block is requested, and `rurp_set_communication_mode()` is called after the operation completes. The host does not send data blocks while the firmware is in programmer mode. Phase 50's SAFE-01 concern is therefore moot; Phase 51's is not.

---

## Validation Architecture

`workflow.nyquist_validation` is not explicitly set to `false` in `.planning/config.json`
(the key is absent), so validation is enabled.

### Phase 49 Validation Approach — Document Assertion Model

This phase produces NO code. There are no unit tests, no `pytest` runs, no `pio test` runs.
Validation is doc-assertion-based: verify that the ADR (`.planning/v1.10-FRAMING-DECISION.md`)
is structurally complete and internally consistent.

### Test Framework

| Property | Value |
|----------|-------|
| Framework | Document assertion (bash + grep), no test runner |
| Config file | None |
| Quick run command | See assertions below |
| Full suite command | See assertions below |

### Phase Requirements → Validation Map

| Req ID | Behavior | Validation Type | Automated Check | File Exists? |
|--------|----------|-----------------|-----------------|-------------|
| SAFE-01 | ADR contains a resolution of the `0x00` bus-aliasing risk with traceable reference to COBS-DECISION §5 Q2/Q3 | doc-assertion | `grep -q "Q2\|Q3\|bus-aliasing" .planning/v1.10-FRAMING-DECISION.md && echo PASS` | ❌ Wave 0 (ADR written in Phase 49) |
| SAFE-01 | ADR either proves host `0x00`-silence or explicitly selects SLIP under D-04 | doc-assertion | Human review of SAFE-01 resolution section | Manual |
| D-02 | Scored matrix present with all 4 criteria | doc-assertion | `grep -qE "Safety|byte-exact|simplicity|overhead" .planning/v1.10-FRAMING-DECISION.md && echo PASS` | ❌ Wave 0 |
| D-06 | Frame contract includes: delimiter byte, escape scheme, exact frame layout, per-file change map naming all 4 files | doc-assertion | `grep -qE "rurp_serial_utils|serial_comm|frame_parser|test_messages" .planning/v1.10-FRAMING-DECISION.md && echo PASS` | ❌ Wave 0 |
| D-05 | ADR cross-references v1.9-COBS-DECISION.md | doc-assertion | `grep -q "v1.9-COBS-DECISION" .planning/v1.10-FRAMING-DECISION.md && echo PASS` | ❌ Wave 0 |

### Sampling Rate

- **Per task commit:** Human review of the section authored in that task
- **Per wave merge:** Run the automated grep assertions above; human review of SAFE-01 resolution section
- **Phase gate:** All assertions green; SAFE-01 section contains either (a) static proof of host `0x00`-silence with citation of 3 sub-claims, or (b) explicit "inconclusive → SLIP selected per D-04" statement

### Wave 0 Gaps

- [ ] `.planning/v1.10-FRAMING-DECISION.md` — the ADR itself (created by Phase 49 execute)
- [ ] No test files, no framework install, no CI changes required in Phase 49

*(Phase 50 will require updating `test_rurp_log_id.cpp` and adding host-side parser tests — those are Phase 52 gaps, not Phase 49.)*

---

## Open Questions

1. **pyserial `flush()` guarantee**
   - What we know: `self.connection.flush()` is called after `self.connection.write()` in `send_bytes`
   - What's unclear: Whether pyserial's `flush()` guarantees physical transmission before return (vs OS-level buffer flush only)
   - Recommendation: The Phase 49 executor should check pyserial docs during the SAFE-01 static proof. If `flush()` only drains to the OS driver (not physical TX), there is a window where the `0x00` byte is buffered but not sent, and the host proceeds to the read loop without having physically transmitted the delimiter. This would be an edge case but would affect the proof.

2. **`init_programmer()` command-consumption sequence**
   - What we know: `firestarter.cpp` loop peeks for `{`, calls `init_programmer()` when found; `init_programmer()` parses and dispatches the command
   - What's unclear: Whether `init_programmer()` fully consumes the entire JSON byte stream (including trailing bytes) from the RX buffer before returning and before `rurp_set_programmer_mode()` is called
   - Recommendation: The Phase 49 executor should read `init_programmer()` in `firestarter.cpp` to confirm the RX buffer is empty after JSON parsing. If the COBS delimiter `0x00` follows the JSON payload and the RX buffer still contains it when `rurp_set_programmer_mode()` is called, it must be drained by `rurp_set_communication_mode()`'s drain loop, not mistakenly parsed.

3. **Is the length prefix retained alongside the delimiter?**
   - What we know: COBS and SLIP both provide resync via delimiter; the motivation for removing `len_u16` is that length-prefix corruption is the bug being fixed
   - What's unclear: Whether the frame contract retains `len_u16` as a "belt and braces" alongside the delimiter
   - Recommendation: The ADR should explicitly decide. Retaining it is conservative but undermines the resync goal. Removing it makes the framing purely delimiter-based. The research recommends removing it (consistent with the resync motivation) but this must be explicit in the contract.

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | pyserial `flush()` ensures physical transmission before return | SAFE-01 Host-Half Analysis | If wrong, the `0x00` byte timing guarantee is weakened; SAFE-01 proof may become inconclusive → SLIP wins per D-04 |
| A2 | `json.dumps` output contains zero `0x00` bytes on any Python platform | Host TX Path Analysis | If wrong (it can't be — JSON escapes all control characters), any `0x00` in a JSON command would already be unsafe in the current protocol |
| A3 | Typical EPROM binary payloads have roughly equal `0x00` and `0xC0` byte frequency | Overhead criterion in matrix | If wrong (e.g., EPROM payloads are mostly `0x00` = blank bytes), COBS has higher overhead than estimated; overhead criterion might favor SLIP more strongly |

**A2 can be struck immediately** — it is provably correct by JSON specification; `json.dumps` escapes all non-ASCII and control bytes. The remaining two (A1, A3) require verification.

---

## Environment Availability

Step 2.6 SKIPPED — Phase 49 is a pure documentation/analysis phase with no external tool
dependencies beyond reading source files (already done). No CLI tools, no runtimes, no
databases, no packages are required to produce the ADR.

---

## Security Domain

`security_enforcement` is not set to `false` in `.planning/config.json`. The phase is
evaluated for applicable ASVS categories.

| ASVS Category | Applies | Assessment |
|---------------|---------|------------|
| V2 Authentication | No | No auth mechanism involved |
| V3 Session Management | No | No session concept |
| V4 Access Control | No | No access control |
| V5 Input Validation | Indirectly | The frame contract must specify that the firmware validates the CRC8 before handing the decoded payload to the JSON parser (Phase 51). This is a Phase 51 design constraint, not a Phase 49 deliverable — but the ADR must note it in the frame contract. |
| V6 Cryptography | No | CRC8 is an integrity check, not a cryptographic primitive; no change to this |

The relevant security property for this phase: the ADR must mandate that the firmware verify
CRC8 before JSON parsing (Phase 51). A corrupt or maliciously crafted frame that passes the
delimiter check but fails CRC8 must be discarded before reaching `json_parser.c`. The current
`{`-peek path has no such protection. The ADR's frame contract must include this requirement.

---

## Sources

### Primary (HIGH confidence)
- `firestarter/src/boards/uno_rurp_shield.cpp` — live code review; `com_mode` gate, `rurp_set_programmer_mode()`, `rurp_set_communication_mode()` (verified)
- `firestarter/src/boards/rurp_serial_utils.cpp` — live code review; current frame layout, CRC8 table, `_firestarter_emit_frame` (verified)
- `firestarter_app/firestarter/serial_comm.py` — live code review; all TX paths, `_read_and_parse_lines`, `_probe_port` sequence (verified)
- `firestarter_app/firestarter/frame_parser.py` — live code review; CRC8 table, poly 0x07 (verified)
- `firestarter/src/firestarter.cpp` lines 162-172 — live code review; `{`-peek command ingest (verified)
- `firestarter/test/native/avr/test_messages/test_rurp_log_id.cpp` — live code review; frame byte contract pinned in Unity assertions (verified)
- `.planning/v1.9-COBS-DECISION.md` — the binding evaluation document; §1.4, §4.2, §4.3, §5 Q2/Q3 (verified)
- `.planning/phases/49-framing-mechanism-decision-cobs-0x00-vs-slip-0xc0/49-CONTEXT.md` — locked decisions D-01..D-06 (verified)
- `.planning/REQUIREMENTS.md` — SAFE-01 definition, v1.10 binding inputs (verified)

### Secondary (MEDIUM confidence)
- `.planning/STATE.md` — project state and phase sequence (verified)
- `.planning/config.json` — `workflow.nyquist_validation` key absent = validation enabled (verified)

### Tertiary (LOW confidence)
- None — all claims in this research are verified against live source files or the locked planning documents.

---

## Metadata

**Confidence breakdown:**
- SAFE-01 proof structure: HIGH — firmware half fully verified; host half verified with 2 open sub-claims (A1, A3) that are execute-time work
- Current frame layout: HIGH — verified from live source code with byte-level detail
- Per-file change map: HIGH — verified against live file structure; content of changes is execute-time work
- Evidence matrix structure: HIGH — criteria are locked (D-02); scores are execute-time work

**Research date:** 2026-06-01
**Valid until:** Stable until any of: `rurp_serial_utils.cpp`, `serial_comm.py`, `firestarter.cpp`, or `uno_rurp_shield.cpp` changes. These files are ring-fenced (GATE-1.8d for `serial_comm.py`; Phase 50 will change the others). Valid for the duration of v1.10 Phase 49.
