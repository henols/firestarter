# Phase 50: Data-Path Framing Layer + Automatic Resync (dual-repo lockstep) - Context

**Gathered:** 2026-06-01
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 50 makes the **host↔firmware data-block path** use the Phase-49 frozen COBS framing
contract end to end, in **lockstep across the firmware and host sub-repos**. The bare
`[len_u16][xor][payload]` data-block boundary is replaced (both directions) by
`[COBS(payload + CRC8)][0x00]`; the firmware encoder/decoder streams with no second
~512 B buffer; CRC8-CCITT is computed/verified on every framed payload; and the receiver
**auto-resyncs to the next `0x00` delimiter** after any framing or integrity error —
eliminating the 2 s `len_u16`-corruption timeout-desync cascade.

**In scope:**
- Framing 2 (host→fw data block) + Framing 3 (fw→host data block) only.
- Replace `rurp_communication_write()` / `rurp_communication_read_data()` with COBS streaming
  encode/decode; remove the `len_u16` prefix; migrate the data-path XOR checksum → CRC8-CCITT.
- Host data-block TX/RX path in `serial_comm.py` + COBS decode helper for `frame_parser.py`.
- A Phase-50 resync proof in both repos (minimal), plus a post-change `pio run -e uno` RAM report.

**Out of scope (later phases — do NOT pull forward):**
- Command-channel framing (FRAME-05) + CRC8-before-parse + version/handshake guard → **Phase 51**.
- Full byte-compat round-trip / lockstep contract tests (incl. pathological all-delimiter cases) → **Phase 52**.
- Bench verification across Uno/Leonardo/uno328pb → **Phase 53**.
- The fw→host log/telemetry framing (`[0xAA55AA55]…[0x0A]`) — **UNCHANGED in v1.10**.

</domain>

<decisions>
## Implementation Decisions

### Carried forward — LOCKED by Phase 49 (`.planning/v1.10-FRAMING-DECISION.md`; do NOT re-litigate)
- **Mechanism = streaming COBS, `0x00` delimiter.** SLIP rejected (scored matrix 11/12 vs 10/12).
- **Frame layout = `[COBS-encoded(payload bytes + CRC8 byte)][0x00 delimiter]`.** The CRC8 byte is
  appended to the raw payload *before* COBS encoding and is itself COBS-encoded (§4.3).
- **`len_u16` length prefix REMOVED** — the delimiter provides unambiguous boundaries; retaining a
  length count would undermine the resync goal.
- **XOR checksum → CRC8-CCITT** on the data path (poly 0x07, seed 0x00, no reflection, no final XOR;
  computed over the raw payload). The existing CRC8 tables are reused unchanged in both repos (D-05):
  `rurp_serial_utils.cpp` PROGMEM table (~lines 109-131) + `frame_parser.py` `_build_crc8_table()` (~lines 28-44).
- **Streaming encode, no second ~512 B buffer**, ~6 B stack; fits the ~545 B Uno free-RAM ceiling (D-04) —
  already proven in the ADR (1503/2048 B used at decision time). A post-change RAM report re-confirms it.
- **Atomic-write mandate:** the full frame incl. trailing `0x00` is assembled as one `bytes` object and
  passed to `send_bytes()` in a single call (no split-write of the delimiter).
- **Dual-repo lockstep mandate:** `rurp_serial_utils.cpp` (fw) ↔ `serial_comm.py`/`frame_parser.py` (host)
  change together; commits land inside each sub-repo on branch `v1.10-serial-transport-hardening`.

### Recovery behavior after resync (FRAME-02)
- **D-01:** **Resync + fail-fast.** On a CRC8 or COBS-decode failure, the receiver discards bytes up to
  the next `0x00` (desync bounded to one frame) and surfaces a clean error **immediately** — no 2 s hang.
  The existing op-level error path fires (firmware: `LOG_ERROR_ID_U16(MSG_ERR_DATA_ERR_N, …)` →
  `OP_MSG_ERROR` at `operation_utils.cpp:173-176`); the user re-runs the operation.
  **No block-level retransmit/ACK is added** — that is a separate future capability (see Deferred), not
  Phase 50. The win is bounded desync + immediate failure, not transparent auto-recovery.

### Resync proof — test level & fault form (Phase 50 SC2)
- **D-02:** **Both repos, minimal.** Phase 50 ships:
  - **Host pytest** — inject a corrupted-CRC frame AND a flipped/missing `0x00` delimiter; assert the
    decoder discards to the next delimiter and recovers within a single frame (no cascade).
  - **Firmware Unity decoder case** — feed the COBS decoder a corrupted/garbled frame followed by a valid
    one; assert it re-anchors on the next `0x00` and decodes the following frame correctly.
  - The **full byte-compat round-trip matrix** (host-encode↔fw-decode both directions, pathological
    delimiter-laden / all-delimiter payloads) stays in **Phase 52** — Phase 50 proves *recovery*, Phase 52
    proves *byte-exactness*.

### Interim version/interop guard
- **D-03:** **No interim guard in Phase 50.** This is a breaking data-path wire change; accept it as a
  beta lockstep upgrade (no mixed-version interop, cf. v1.2 Message-ID rework). Document the breaking
  nature. The proper version/handshake guard lands in **Phase 51 (SC3)** once the command channel is
  framed — an interim guard now would be throwaway work since Phase 51 reworks command ingest anyway.
  Beta-only; nothing promoted to stable without operator authorization.

### `#` marker & MAIN-state demux
- **D-04:** **Keep the `#` data-packet marker; the COBS frame follows it.** `read_command_in_main`
  (`operation_utils.cpp` ~line 159) still dispatches on the single-char marker (`#`, `DONE`, …); only the
  bytes *after* `#` change from `[len_u16][xor][payload]` to `[COBS(payload+CRC8)][0x00]`. Smallest, safest
  diff; preserves the existing MAIN-state message demux.
  - **Open for research/planner:** confirm the resync path handles a **corrupted `#` marker itself**
    (a flipped marker byte must still re-anchor cleanly on the next `0x00`, not strand the parser). This
    is the one residual edge in keeping the marker — research should validate it before the planner locks
    the read loop.

### Framing-3 scope resolution (operator-locked 2026-06-01 — resolves D-04 open item via RESEARCH.md deep trace)
- **D-06:** **Option A.** A live-code trace (RESEARCH.md "Framing-3 Scope Deep Trace") proved the fw→host
  EPROM **read** data block does NOT flow through `rurp_communication_write()` — reads emit over the
  UNCHANGED `MSG_DATA_CHUNK` magic-preamble frame (`eprom_operations.cpp:114-116`), and
  `rurp_communication_write()` is dormant (only caller behind the undefined `#ifdef RAW_DATA_PROGRESS`).
  Therefore Phase 50:
  - **Rewrites `rurp_communication_read_data()`** (the host→fw write-receive path — the literal 2 s
    `timeout_ms` cascade source) to COBS streaming decode + CRC8 + resync.
  - **Rewrites the dormant `rurp_communication_write()`** as its COBS streaming-encode mirror (contract
    symmetry + Unity-testable), even though no live caller exercises it in v1.10.
  - **Leaves EPROM reads on `MSG_DATA_CHUNK`** — the log/telemetry magic-preamble framing stays UNCHANGED
    (consistent with the ADR §4.2 freeze; ADR §4.6 function-name errata recorded in `v1.10-FRAMING-DECISION.md`).
  - Host counterpart: change frame *contents* in `eprom_operations.py:_main_phase_send_data` (write send
    path) + add `cobs_encode`/`cobs_decode` to `frame_parser.py`; the read RX path (`_main_phase_read_data`
    / `_read_and_parse_lines`) keeps consuming `MSG_DATA_CHUNK` unchanged.
  - **Corrupted-`#`-marker directive (resolves the D-04 open edge):** the rewritten reader MUST, on any
    COBS-decode or CRC8 failure, drain bytes up to **and including** the next `0x00` before returning the
    error — a flipped marker re-anchors on the next delimiter and never strands the parser.

### Claude's Discretion
- Exact placement of the COBS decode helper (co-located in `serial_comm.py` vs `frame_parser.py`) — per the
  ADR change map, planner's call.
- Internal naming of the new encoder/decoder functions and the precise streaming-decoder buffer strategy
  (decode in place into `data_buffer` vs incremental), provided the no-second-buffer / Uno-RAM constraint holds.
- Exact fault-injection fixtures and assertion style for the D-02 tests.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### The frozen contract (read FIRST — this is the binding spec)
- `.planning/v1.10-FRAMING-DECISION.md` — the Phase-49 decision ADR. **Specifically:**
  - §3 — Decision statement (COBS `0x00` selected).
  - §4.1 — Delimiter + streaming-COBS encoding scheme + atomic-write mandate.
  - §4.2 — Scope of framing (Framing 2/3 = Phase 50; Framing 1 = Phase 51; Framing 4 unchanged).
  - §4.3 — Data-block frame layout table (`[COBS(payload+CRC8)][0x00]`; `len_u16` removed; XOR→CRC8).
  - §4.5 — Streaming-encodable / Uno RAM confirmation (~6 B stack, ~545 B ceiling).
  - §4.6 — **Per-file change map** (the four lockstep files + which phase touches each).

### Upstream evaluation (immutable input)
- `.planning/v1.9-COBS-DECISION.md` — survey + constraints record; §3 streaming COBS reference snippet;
  D-04 (Uno-fit) / D-05 (keep CRC8). The v1.10 ADR supersedes only its DEFER line for the mechanism.

### Requirements & roadmap
- `.planning/REQUIREMENTS.md` — **FRAME-01, FRAME-02, FRAME-03, FRAME-04, CRC-01** (the five this phase
  satisfies); SAFE-01 already ✅ (Phase 49). v1.10 Non-Goals.
- `.planning/ROADMAP.md` — Phase 50 entry (Goal + 4 Success Criteria + Depends-on); Phases 51-53 as the
  downstream consumers of this framing layer.

### Code to change — firmware (`v1.10-serial-transport-hardening` branch in `firestarter/`)
- `firestarter/src/boards/rurp_serial_utils.cpp` — `rurp_communication_read_data()` (~lines 44-82) and
  `rurp_communication_write()` (~lines 84-99): the current `[len_u16][xor][payload]` + 2 s timeout to
  replace with COBS streaming encode/decode + CRC8. CRC8 PROGMEM table (~lines 109-131) reused unchanged.
  `_firestarter_emit_frame` (log/telemetry) **untouched**.
- `firestarter/src/operation_utils.cpp` — `read_command_in_main` data-packet `case '#'` (~lines 159-170);
  the `res < 0` → `OP_MSG_ERROR` recovery path (D-01).
- `firestarter/test/native/avr/test_messages/` (e.g. `test_rurp_log_id.cpp`) — home for the Phase-50
  firmware Unity resync decoder case (D-02). Existing log/telemetry assertions stay unchanged.

### Code to change — host (`v1.10-serial-transport-hardening` branch in `firestarter_app/`)
- `firestarter_app/firestarter/serial_comm.py` — data-block TX/RX path; `send_bytes()`/`flush()` (~line 140);
  `_read_and_parse_lines()` (~lines 224-330) which must demux COBS `0x00` data frames while still handling
  the magic-preamble log/telemetry frames.
- `firestarter_app/firestarter/frame_parser.py` — add the COBS decode helper; `_build_crc8_table()` /
  `_crc8_ccitt()` (~lines 28-44) reused unchanged (D-05).

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **CRC8-CCITT tables (both repos)** — already present and byte-compatible; reused unchanged. The frame
  contract appends the existing CRC8 byte (now over the data payload) instead of the XOR checksum.
- **`data_buffer[DATA_BUFFER_SIZE]`** (firmware handle) — already on-stack/handle during EPROM ops; the
  streaming COBS encoder reads from it and the decoder writes into it, so no second ~512 B buffer is needed.
- **`_read_and_parse_lines()` magic-preamble demux** (host) — the established pattern for distinguishing
  framed (length-authoritative) log/telemetry from text lines; the COBS data-frame demux slots alongside it.

### Established Patterns
- **Marker-dispatched MAIN-state loop** (`operation_utils.cpp`): single-char markers (`#`, `DONE`) select
  message type before the payload. Phase 50 keeps this (D-04); only the post-`#` payload framing changes.
- **Single-byte writes + `.flush()` at end** — the existing serial line discipline; the COBS frame body +
  delimiter follow it under the atomic-write mandate.
- **Breaking lockstep upgrade, no mixed-version interop** — v1.2 Message-ID rework precedent; this phase
  follows it (D-03).

### Integration Points
- Firmware decode failure → `LOG_ERROR_ID_U16(MSG_ERR_DATA_ERR_N, (uint16_t)res)` → `OP_MSG_ERROR`
  (`operation_utils.cpp:173-176`) is the existing error surface the fail-fast recovery (D-01) reuses.
- The framing layer built here is the direct input to Phase 51 (command channel reuses it) and Phase 52
  (round-trip tests pin it).

</code_context>

<specifics>
## Specific Ideas

- The 2 s timeout in `rurp_communication_read_data()` (the literal `timeout_ms = 2000` loop) is the
  cascade source SC1 targets — its removal/replacement by delimiter-driven framing is the concrete win.
- For a blank-EPROM (all-`0x00`) payload, COBS overhead is bounded (each `0x00` → a 1-byte run code);
  the encoder must handle this without materializing a second buffer — confirm on the Uno RAM report.
- The Phase-50 resync test should assert recovery is bounded to **one frame** (the next valid frame
  decodes correctly), not merely "an error was raised" — SC2 is about bounded desync, not just detection.

</specifics>

<deferred>
## Deferred Ideas

- **Block-level retransmit / ACK on the data path** — would let a single corrupted block auto-recover
  mid-transfer instead of failing the operation (D-01 chose fail-fast). A new capability; its own phase
  if ever wanted, not Phase 50.
- **Command-channel framing + CRC8-before-parse + version/handshake guard** → Phase 51 (FRAME-05; the
  interim-guard decision D-03 explicitly defers the guard here).
- **Full byte-compat round-trip / lockstep contract tests** (pathological delimiter-laden + all-delimiter
  payloads, both encode directions) → Phase 52.
- **Bench verification** (Uno/Leonardo/uno328pb, operator-gated, shield-rev confirmed) → Phase 53.

None — discussion stayed within phase scope (no todos matched Phase 50).

</deferred>

---

*Phase: 50-data-path-framing-layer-automatic-resync-dual-repo-lockstep*
*Context gathered: 2026-06-01*
