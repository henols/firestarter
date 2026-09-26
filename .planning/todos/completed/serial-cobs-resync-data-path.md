---
id: serial-cobs-resync-data-path
title: Evaluate COBS framing/resync on the serial data path (PacketSerial assessed, not adopted)
captured: 2026-05-27
status: pending
type: enhancement
target_milestone: v1.10
priority: medium
related_phase: 50
resolves_phase: 50
requirement: FRAME-01
note: Evaluation half closed by v1.9 Phase 48-01 (verdict ADOPT, see .planning/v1.9-COBS-DECISION.md). Implementation is v1.10 — the custom framing layer lands in Phase 50 (data path) + Phase 51 (command channel); mechanism (COBS vs SLIP) decided in Phase 49.
---

# COBS framing/resync on the serial data path

## The idea

Borrow **COBS-style automatic resync into the existing length-prefixed data-block
path** — do NOT adopt the PacketSerial library wholesale. The goal is a single
robustness win: a garbled byte should corrupt only one packet and re-sync on the
next delimiter, instead of desyncing the stream until the 2 s timeout fires.

Keep the existing CRC8-CCITT integrity layer on top; PacketSerial has no checksum.

## Investigation summary (2026-05-27)

Spawned from a `/gsd-fast` investigation: "what improvements and what cost would a
lib like PacketSerial bring to the firmware." Conclusion: **not worth a drop-in.**

### What the firmware does on the wire today (4 framings, one 250000-baud line)

| Direction | Where | Framing |
|---|---|---|
| host→fw commands | `firestarter/src/firestarter.cpp:162-172` | ASCII JSON, peek for `{`, discard junk |
| host→fw data block | `firestarter/src/boards/rurp_serial_utils.cpp:44-79` | `[len_u16][xor][payload]`, 2 s timeout |
| fw→host data block | `firestarter/src/boards/rurp_serial_utils.cpp:81-93` | same `[len_u16][xor][payload]` |
| fw→host log/telemetry | `firestarter/src/boards/rurp_serial_utils.cpp:135-181` | `[0xAA55AA55][len_u16][id][params][crc8][0x0A]` |

The host decoder at `firestarter_app/firestarter/serial_comm.py:546-660` demuxes all
of these on one stream and is **byte-for-byte synced** with the firmware (magic
preamble, CRC8 table, length semantics). A native test suite (`test_messages`) pins
the frame contract. Root CLAUDE.md mandates these two files change in lockstep.

### What PacketSerial (COBS) would improve
1. One framing instead of four — `0x00` delimiter is unambiguous, no magic preamble / length prefix needed.
2. **Automatic resync** (the genuinely valuable benefit). Today the length-prefixed data path has no resync — a corrupted length byte desyncs until timeout.
3. Callback-driven receive replaces the manual peek/read/timeout loop.

### Why a drop-in is NOT worth it
- **RAM is the blocker (Uno).** Current `pio run -e uno` baseline: **RAM 73.0% = 1495/2048, only 553 bytes free**; Flash 68.6% (22122/32256, ~10 KB free). The handle already owns `char data_buffer[512]` (`firestarter/include/firestarter.h:87`). PacketSerial's `send()` builds a **fully COBS-encoded copy** (~`n + n/254 + 2` ≈ 516 bytes for a 512-byte chunk) before writing, plus its own RX buffer. A second ~512-byte buffer does not fit in 553 free bytes → stack/globals collision → crash. You'd have to write a streaming/in-place COBS encoder anyway, at which point you're not really using the library.
- **Flash is fine** (~1–2 KB for COBS+lib vs ~10 KB free) — not the constraint.
- **Coordinated dual-repo rewrite** of `rurp_serial_utils.cpp` + `serial_comm.py` + the `test_messages` contract. Milestone-sized, not fast-sized.
- **Bench re-validation** required against the Uno `SERIAL_ON_IO` bus-aliasing problem — the magic preamble exists precisely because the UART shares PORTD with the data/address bus. Must prove `0x00` delimiter collisions with bus-driven `0x00` bytes don't create false frame boundaries.

## Does NOT fix v1.8 Bug A / Bug B

Important: the v1.8 RCA seed characterizes Bug A (Modified Rev 0 upper-address
jitter, A15=1 → 1.86× skew) and Bug B (Rev 2.0 /CE-or-/OE timing + VPP=13.1V) as
**hardware** faults, not framing faults. COBS/PacketSerial would not fix either.
This is an independent protocol-quality item — do not fold it into the Bug A/B hunt
as a candidate fix. (See memory `project-v18-rca-seed-bug-a-bug-b`.)

## Existing implementations surveyed (2026-05-27 refinement)

Follow-up question: "what implementations already exist and which is the best match?"
The survey surfaced a constraint the first pass missed (see CRUX below), then narrowed
the field.

### CRUX — "in-place COBS" and "512 B single frame" are mutually exclusive
COBS must write its output (~`payload + payload/254 + 1` bytes) somewhere. The ONLY
way to avoid a second buffer is **in-place** encoding, and in-place COBS is
mathematically capped at **254-byte runs** (nanocobs' `cobs_encode_tinyframe`
enforces exactly `< 254`). For larger payloads, every COBS lib (nanocobs standard
mode, cobs-c, PacketSerial, COBS-CPP) encodes into a **separate `COBS_ENCODE_MAX(n)`
destination buffer** (~514 B for a 512 B frame).

Uno RAM math: 2048 − 1495 used = **553 B free**, and the 512 B `data_buffer` is
already inside that 1495. A ~514 B COBS dst buffer → ~2009 B used → ~39 B stack left
→ crash. **So on the Uno, no off-the-shelf COBS encoder fits a 512 B single frame.**
(Decode/receive side is fine — in-place decode into `data_buffer` works. It's the
fw→host *encode* path that hits the wall.) This means the prior "streaming/in-place
COBS" phrasing was conflating two incompatible things; the real options are below.

### Candidates scored against our filters (≤512 B frame, 553 B free RAM, reuse CRC8, dual-repo)
| Implementation | Lang pair | CRC built in | 512 B frame on Uno? | Verdict |
|---|---|---|---|---|
| nanocobs (charlesnicholson) | C99 only | no | in-place ≤254 B; std mode needs 2nd buffer | Best embedded C codec, zero-malloc/zero-libc — but ≤254 to stay buffer-free |
| cobs-c + cobs-python (cmcqueen) | **C + Python, same author** | no | needs 2nd buffer → ✗ on Uno | Best host codec; matched pair = byte-identical COBS |
| PacketSerial (bakercp) | C++ only | no | full encoded copy → ✗ on Uno | Rejected (RAM) |
| SerialTransfer + pySerialTransfer (PowerBroker2) | **C++ + Python, same author** | **yes, CRC8 poly 0x9B** | payload capped 1–254 B by design | Turnkey; caps at 254, swaps our CRC poly, replaces ALL framing |
| MIN protocol (min + min-python) | C + Python | yes (CRC32) | 255 B/frame; transport buffers | Overkill + RAM heavy |
| PatrickBaus/COBS-CPP | C++ only | no | separate buffer → ✗ on Uno | Honorable mention |

Two filters do the eliminating: single-byte length fields cap SerialTransfer + MIN at
~254 B, and non-in-place encoders blow the Uno RAM budget at 512 B. Both push to the
same place: **on the Uno, frames effectively must be ≤254 B regardless of library.**

## CORRECTION (2026-05-29) — streaming-to-Serial obsoletes the 254 B re-chunk requirement

The "in-place COBS ≤254 B" CRUX above is real, but it ONLY blocks single-buffer
**in-place** encoding. It does NOT force re-chunking the wire frame to ≤254 B,
because **we don't have to materialize the encoded form anywhere** — we can emit
encoded bytes directly to `SERIAL_PORT.write()` byte-by-byte while reading from
`data_buffer` as the source. Encoded form never lives in memory simultaneously;
zero extra buffer.

### Streaming encode (fw→host), ~15 lines, any payload size
```c
size_t i = 0;
while (i < N) {
    size_t run_start = i;
    uint8_t run_len = 0;
    while (i < N && data_buffer[i] != 0 && run_len < 254) { run_len++; i++; }
    SERIAL_PORT.write((uint8_t)(run_len + 1));               // code byte (or 0xFF if max-run)
    SERIAL_PORT.write(&data_buffer[run_start], run_len);     // run bytes
    if (i < N && data_buffer[i] == 0) i++;                   // consume the 0x00
    // else if run_len == 254: no 0x00 consumed; next group continues without implicit zero
}
SERIAL_PORT.write((uint8_t)0x00);                            // frame delimiter
```
RAM cost: `i`, `run_start`, `run_len` (≤ 6 bytes total on stack). Reads through
`data_buffer` once, sequentially. No second buffer, no malloc. Works for 512 B
(Uno) and 1024 B (Leonardo) single frames — the COBS 254 cap is on each *internal
run*, NOT on the frame.

### Streaming decode (host→fw), symmetric
Read 1 code byte from serial, then `code-1` bytes directly into
`data_buffer[decoded_offset..]`, append the implicit `0x00` separator
(if `code != 0xFF`), and loop until the `0x00` frame delimiter arrives.
`data_buffer` holds the decoded form only; encoded form streams through and is
discarded byte-by-byte.

### Why this changes the recommendation
Once streaming-to-Serial is on the table, the off-the-shelf libraries' main
attraction (avoiding hand-rolled code) costs *more* than the custom path,
because each adopted lib forces a 254 B re-chunk OR a second-buffer RAM hit
neither of which streaming requires. ~40 lines of custom C + matching Python is
smaller than the diff to adopt nanocobs+chunk or SerialTransfer.

Credit: operator caught the "consumed bytes can be reused" framing, which
generalizes to "don't materialize the encoded form at all" — the same insight
in stronger form.

## Recommended path (REVISED for Phase 48 / COBS-01)

**Preferred — custom streaming COBS encoder/decoder, reuse CRC8 + u16-len header:**
- Firmware: ~40 lines in `firestarter/src/boards/rurp_serial_utils.cpp`. Streaming
  encode (above) for fw→host; streaming decode for host→fw into `data_buffer`.
  Zero extra RAM, no 254 B chunking, no library dependency.
- Host: ~30 lines in `firestarter_app/firestarter/serial_comm.py` matching the
  same wire format. Optionally cross-check against PyPI `cobs.cobs` (plain
  COBS, NOT `cobs.cobsr`) in a unit test to prove byte-identical encoding.
- Keep existing CRC8-CCITT (poly 0x07) and u16 big-endian length header
  unchanged. Both repos already implement + unit-test these.
- Single frame stays 512 B (Uno) / 1024 B (Leonardo) — no eprom_operations
  loop restructure, no JSON command path change.

**Runner-up A — nanocobs (firmware) + cobs-python (host), if "use a library"
trumps "minimize LOC":** still works, but requires re-chunking the data path to
≤254 B frames to use `cobs_encode_tinyframe` (the only zero-extra-buffer mode).
More LOC than the custom streaming path, not less, once the chunking loop and
new test contract are counted.

**Runner-up B — SerialTransfer/pySerialTransfer, if "batteries-included" trumps
everything else:** turnkey C++/Python pair, but replaces ALL framing (incl. JSON
command path), swaps CRC8-CCITT for poly 0x9B, rewrites `test_messages`
wholesale, AND still caps at 254 B. Largest dual-repo diff.

**Disqualified — PacketSerial drop-in on Uno:** second-buffer RAM hit, no
streaming-to-Stream API.

## The decisive decision (pick before implementing)
**Library boundary, or ~40 lines of custom code?**
- Custom (smallest diff, no chunking, reuse CRC8) → **streaming encoder/decoder pair** ← *recommended*
- Library + chunking to ≤254 B → nanocobs + cobs-python
- Turnkey + accept replacing all framing → SerialTransfer / pySerialTransfer

## Open questions
- Is the 2 s-timeout desync actually observed in the field, or only theoretical? If it never bites, priority stays low.
- Does the host `serial_comm.py` demux already recover gracefully enough that COBS adds little? Measure before investing.
- uno328pb shares the Uno's 2048 B RAM ceiling — same constraint as Uno.
- Per-frame overhead of ≤254 B chunking (extra CRC + delimiter per chunk) on a 512/1024 B block — quantify vs the current single-frame cost.

## Cross-references
- `firestarter/src/boards/rurp_serial_utils.cpp:44-93` (data block) + `:138-184` (log frames)
- `firestarter/src/firestarter.cpp:109` (`init_programmer` read) + `:162-172` (command peek loop)
- `firestarter_app/firestarter/serial_comm.py:546-660` (host stream demux) + `:967-983` (data-block checksum read)
- `firestarter/include/firestarter.h:87` (`data_buffer[512]`)
- Root `CLAUDE.md`: serial protocol must stay in sync across `serial_comm.py` ↔ `firestarter.cpp`
- Memory `project-v18-rca-seed-bug-a-bug-b`: confirms Bug A/B are hardware, not framing

## Surveyed implementations (links)
- nanocobs (C99, in-place, no malloc): https://github.com/charlesnicholson/nanocobs
- cobs-python (PyPI `cobs`, use `cobs.cobs` plain): https://github.com/cmcqueen/cobs-python · https://pypi.org/project/cobs/
- cobs-c (matched-author C codec): https://github.com/cmcqueen/cobs-c
- SerialTransfer (Arduino, COBS+CRC8 poly 0x9B, ≤254 B): https://github.com/PowerBroker2/SerialTransfer
- pySerialTransfer (matching Python): https://github.com/PowerBroker2/pySerialTransfer · https://pypi.org/project/pySerialTransfer/
- COBS/R variant caveat (do NOT use for cross-impl compat): https://pythonhosted.org/cobs/cobsr-intro.html
