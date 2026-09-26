# Phase 6: Logging Infrastructure (catalog + codegen + helper + decoder) - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in `06-CONTEXT.md` — this log preserves the alternatives considered.

**Date:** 2026-05-18
**Phase:** 6-logging-infrastructure
**Areas discussed:** Wire frame format
**Areas declined (deferred to Claude's discretion):** Catalog format + meta→sub-repo distribution, Param shape + render-hint schema, Coexistence + host-decoder smoke test

---

## Gray-Area Selection

| Area | Description | Selected |
|------|-------------|----------|
| Wire frame format | Binary frame discrimination, layout, integrity, parser integration | ✓ |
| Catalog format + meta→sub-repo distribution | YAML/TOML/JSON; submodule vs vendored vs subtree | (deferred) |
| Param shape + render-hint schema | Types only vs per-param render hints | (deferred) |
| Coexistence + host-decoder smoke test | Always-on vs feature-flag; LHOST-01 fixture shape | (deferred) |

**User's choice:** Wire frame format only — the other three were deferred to researcher/planner discretion.

---

## Wire Frame Format

### Question 1 — Frame discriminator

| Option | Description | Selected |
|--------|-------------|----------|
| Sentinel byte (e.g. 0xFE) at frame start | One reserved byte; host peeks byte 0, switches parser mode | |
| Length-prefixed COBS / SLIP-style framing | Length byte + byte-stuffing so no in-band 0x00 / 0x0A collisions | |
| Text prefix carrying hex-encoded payload | `ID: HH HH HH\r\n` — reuses existing line discipline, ~2× wire size | |
| Reserved high-bit byte 0x80–0xFF as preamble | Single high-bit byte marks binary frame | |

**User's choice:** None of the listed options as-given. The operator surfaced a load-bearing constraint:

> "This a little bit tricky since in the UNO setup the serial pins and the d register is of dual purpose and during programming/reading it can produce ghost bytes on the serial line. so we must come up with a foulprofe methotd that can handle this"

**Notes:** This rules out any single-byte sentinel. Question 2 was rephrased to focus on multi-byte-magic foolproof options.

---

### Question 2 — Framing approach (ghost-byte resilient)

| Option | Description | Selected |
|--------|-------------|----------|
| Binary frame: 2-byte magic + len + ID + params + CRC8 + 0x0A | Smallest robust binary frame; ~30% bigger than option 2 but catches single-byte corruption | |
| Text-encoded ID frame, reuses existing line discipline | `ID: 12 03 1A 2B 3F\r\n` — survives ghost bytes via existing rightmost-prefix regex; loses ~half wire savings | |
| Binary frame with longer 4-byte magic + length + checksum | Maximum collision resistance — 4-byte preamble essentially impossible from random PORTD noise | ✓ |
| Binary frame, COBS-encoded (no in-band 0x0A) | SLIP/PPP-style byte stuffing; ~3% wire overhead, ~120 bytes firmware code | |

**User's choice:** 4-byte magic + length + checksum.

**Notes:** Operator prioritized collision resistance over wire-byte economy. The 2 extra magic bytes vs option 1 trade away minimal wire savings for near-zero false-positive rate against PORTD bus aliasing.

---

### Question 3 — Frame layout (length byte, terminator, checksum algorithm)

| Option | Description | Selected |
|--------|-------------|----------|
| MAGIC4 + len + ID + params + CRC8 + 0x0A | Belt + suspenders. Length authoritative; trailing 0x0A is re-sync anchor; CRC8 catches single-byte corruption | ✓ |
| MAGIC4 + len + ID + params + CRC8 (no terminator) | Smaller; resync via magic scan only | |
| MAGIC4 + ID + params + CRC8 + 0x0A | No length — host consults catalog for byte count; loses forward-compat for unknown IDs | |
| MAGIC4 + len + ID + params + XOR8 + 0x0A | XOR8 instead of CRC8; ~10 bytes firmware vs ~80 for CRC8; weaker error detection | |

**User's choice:** MAGIC4 + len + ID + params + CRC8 + 0x0A.

**Notes:** Length-authoritative gives forward-compat: an unknown future ID can be skipped cleanly without catalog consultation. Trailing 0x0A provides a second re-sync anchor and makes frames look line-buffered to debug capture tools.

---

### Question 4a — Magic-byte value

| Option | Description | Selected |
|--------|-------------|----------|
| 0xAA 0x55 0xAA 0x55 (alternating-bit preamble) | Maximum bit transitions; least likely to alias to any single bus-line pattern; classic UART preamble | ✓ |
| 0xFC 0xFE 0xFD 0xFF (high-end reserved range) | Reserves high-bit bytes for control; vulnerable near end of 512KB address space | |
| 0xDE 0xAD 0xBE 0xEF (debug-friendly) | Recognizable in hex dumps; bit pattern less optimal than 0xAA 0x55 | |
| 0x00 0xFF 0x00 0xFF (rail-flip preamble) | Maximal byte transitions; vulnerable if a bus line is stuck-high | |

**User's choice:** 0xAA 0x55 0xAA 0x55.

**Notes:** Bit pattern `10101010 01010101 10101010 01010101` — maximum transitions. Operator confirmed this is the textbook UART-preamble choice and matches what would be expected in a synchronous protocol's framing layer.

---

### Question 4b — Host parser integration

| Option | Description | Selected |
|--------|-------------|----------|
| Always-on byte-stream reader, magic scan, line fallback | Unified read loop. Bytes accumulate until either magic-prefix detected (binary path) or 0x0A seen (text path). One implementation, no firmware-version branching | ✓ |
| Dual-mode reader switched by firmware version handshake | Phase 6 lands v3 reader; switches after FW version check identifies v3 firmware | |
| Two parallel readers feeding one queue | Concurrent text + binary readers feeding a single queue; only useful if firmware mixes modes within a session, which lockstep upgrade rules out | |

**User's choice:** Always-on byte-stream reader, magic scan, line fallback.

**Notes:** Single unified loop. The existing rightmost-prefix regex continues to handle text lines; binary frames are dispatched on magic detection. No firmware-version branching in the read path — the catalog itself is the protocol contract, and at Phase 6 close no firmware call-site emits frames yet (decoder is exercised only via LHOST-01 hand-crafted fixture test).

---

## Claude's Discretion

The operator deliberately skipped three of the four identified gray areas. The researcher / planner is empowered to recommend concrete choices for each, presenting trade-offs in RESEARCH.md / PLAN.md:

- **Catalog file format** — YAML / TOML / JSON / hand-rolled DSL. Constraint: human-editable, diff-friendly, deterministic to parse.
- **Catalog file path** — REQUIREMENTS suggests `.planning/catalog/messages.yaml` as a default; planner may propose alternatives.
- **Meta-repo → sub-repo distribution** — vendored copy, git submodule, or subtree. Both sub-repos are independent git repos and currently don't track the meta-repo.
- **Param shape + render hints** — types only with per-type default render rules, OR explicit per-param render fields.
- **Codegen language + invocation** — Python is the obvious default given `tools/build_db.py` precedent.
- **`MSG_PARAM_COUNT(id)` implementation** — `constexpr` lookup vs `switch` inline vs PROGMEM table.
- **`rurp_log_id` integration with `com_mode` + `SERIAL_DEBUG`** — must preserve today's behavior.

## Deferred Ideas

None. Discussion stayed entirely within the wire-frame design space; no scope creep, no out-of-phase capabilities surfaced.
