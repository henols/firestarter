# Assessment: CRC-16 for programming data frames (issue #126)

Status: assessment only, no protocol change. Date: 2026-11-28.

## Current behaviour (verified in source)

- Wire format, both directions: `COBS(payload || CRC8(payload)) || 0x00`.
  CRC-8 is CCITT (poly 0x07, seed 0). Firmware: `firestarter_fw/src/boards/rurp_serial_utils.cpp`
  (streaming decode + verify, `crc8_ccitt`). Host: `firestarter_app/firestarter/frame_parser.py`
  (`encode_crc_frame`, `_crc8_ccitt`).
- Data frames are exactly `DATA_BUFFER_SIZE` bytes: 1024 (AVR boards in `platformio.ini`),
  1536 (one env), 512 (PY32). A 1 MiB image is therefore 1024-2048 frames.
- The decoder checks CRC before the command/JSON layer and drains to `0x00` on any
  COBS/CRC/overflow error. These properties are independent of CRC width.
- Firmware verification during write (`VERIFY_PER_PULSE`, optional final pass in
  `src/proms/eprom.cpp`) reads the chip back against the bytes the firmware
  *received*. A frame corrupted undetected in transit is programmed and then "verifies".
  Only host `write --verify` (read-back, compared against the source image) catches it.

## Quantified risk

CRC-8 over frames >= ~15 bytes has Hamming distance 2: some 2-bit errors escape and a
random corruption escapes with probability 2^-8 = 0.39%. CRC-16/CCITT (0x1021) has
HD 4 up to ~4 KiB (all 1-3 bit errors caught at our frame sizes), detects all bursts
<= 16 bits, and random escape probability 2^-16 = 1.5e-5. COBS adds no protection but
does not weaken it (the CRC covers decoded bytes).

Undetected-corruption probability for a 1 MiB write (1024 frames of 1024 B, ~8.2 kbit/frame),
assuming independent bit errors at rate BER, escape = P(frame corrupted) x 2^-w:

| Link BER | Expected corrupted frames | P(undetected) CRC-8 | P(undetected) CRC-16 |
|----------|---------------------------|---------------------|----------------------|
| 1e-9 (good wire/USB) | 0.008 | ~3e-5 | ~1e-7 |
| 1e-7 | 0.8 | ~3e-3 | ~1.2e-5 |
| 1e-6 (poor/noisy UART) | 8 | ~3% | ~1.2e-4 |

(Upper bound for random corruption; real errors are often bursts <= 8 bits, which both CRCs detect.)

Realistic exposure is small: every supported host link is USB (CDC or a USB-serial
bridge), and USB packets carry their own CRC-16, so only the on-board UART hop of
AVR boards (short trace, no parity) is unprotected beyond CRC-8. No observed failure
is attributable to this. The risk is real only for noisy wiring and when
`--verify` is not used.

## Recommendation

Worthwhile as low-priority hardening; not urgent. Cheapest effective mitigation today is
cost-free: encourage/default `write --verify` (already catches 100% of escapes
at the cost of a read pass). CRC-16 is the right upgrade if the protocol is touched anyway.

## Proposed design (not implemented)

1. **Negotiation, no silent break.** Gate on firmware version via the existing
   feature-version mechanism (`CF_MIN_FEATURE`) plus an explicit opt-in bit in the
   CONFIGURE command-frame flags (`CF_FLAGS_MASK` currently 0x03F7; add e.g.
   `FLAG_CRC16`). Old firmware rejects unknown flag bits, so a new host falls back to
   CRC-8 on rejection or when the reported firmware version is below the feature
   version. Old host never sets the flag, so new firmware stays on CRC-8.
2. **Scope.** CRC-16 applies to data frames only (both directions) after a successful
   CONFIGURE with the flag; command/log frames stay CRC-8 so bootstrap and version
   discovery are unchanged. The mode resets with the session/command state.
3. **Framing.** `COBS(payload || CRC16_hi || CRC16_lo) || 0x00`; keep CRC-before-JSON,
   bounded drain-to-0x00 resync, and the existing 1-byte lookahead (becomes 2 bytes;
   +1 B RAM on AVR, check the RAM budget of the 1536 B build). CPU cost: table-less
   bitwise CRC-16 would slow AVR; a 512 B PROGMEM table or nibble-table (32 B) is needed.
4. **Tests.** Shared golden frames (fw `test/native/avr/test_cobs_data_frame`, app
   `tests`), single-bit/burst/length corruption injection, version-fallback matrix
   (old/new host x old/new fw), max-frame (1536 B) and resync tests.

## Acceptance criteria status

- Quantify risk: done above.
- Version-negotiated design: proposed above; implementation deferred.
- Golden/corruption/fallback/max-frame tests: deferred with implementation.
- Retain bounded resync and CRC-before-JSON: part of the design constraints.
