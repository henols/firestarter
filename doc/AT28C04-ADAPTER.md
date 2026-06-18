# AT28C04 / AT28C16 DIP24 → DIP32 Adapter Spec

This document is the operator-facing pin-map reference for a physical DIP24-to-DIP32 adapter
that allows AT28C04 and AT28C16 family 24-pin 5V parallel EEPROMs to be programmed in the
RURP DIP32 socket. The adapter physically re-routes each DIP24 chip pin to the correct
DIP32 socket position, so the firmware handler `configure_eeprom28c` (protocol `0x0D`)
sees the correct address, data, and control signals on the RURP bus.

If you have a DIP24 EEPROM chip and want to build a physical adapter, read
[§2 (pin table)](#2-adapter-pin-table) and [§3 (safety notes)](#3-safety-notes).
If you want to understand which chips are covered and why they are classified
`adapter-required`, read [§1 (overview)](#1-overview).

Full derivation, pinout-source citations, and future graduation steps: see
`.planning/AT28C04-ADAPTER.md` in the Firestarter meta-repo.

---

## 1. Overview

### Chips Covered

This adapter covers all nine `adapter-required` 24-pin 5V parallel EEPROMs in the Firestarter
chip database. These chips share the `DIP24_2816` pinout (verified in `pinouts.json`):

| Part Number | Manufacturer | Size |
|-------------|-------------|------|
| AT28C04 | Atmel | 512 × 8 (4 Kbit) |
| AT28HC04 | Atmel | 512 × 8 (4 Kbit, CMOS) |
| AT28C04E | Atmel | 512 × 8 (4 Kbit, low Vcc) |
| AT28C04F | Atmel | 512 × 8 (4 Kbit, fast) |
| AT28C16 | Atmel | 2K × 8 (16 Kbit) |
| AT28HC16 | Atmel | 2K × 8 (16 Kbit, CMOS) |
| AT28HC16L | Atmel | 2K × 8 (16 Kbit, low power) |
| AT28C16E | Atmel | 2K × 8 (16 Kbit, low Vcc) |
| AT28C16F | Atmel | 2K × 8 (16 Kbit, fast) |

Additionally, the following compatible chips share the same adapter:
- 28C04A, 28C04AF (Microchip Memory)
- 28C16A, 28C16AF (Microchip Memory)
- UPD28C04 (NEC)

### Firmware Handler

The firmware handler for these chips is `configure_eeprom28c`, dispatched via
protocol `0x0D` (`EEPROM_POLL`). This handler:
- Runs at 5V only — no VPP voltage regulator is engaged.
- Issues an SDP-disable sequence before programming.
- Uses DQ7 page-write polling for write-cycle completion.
- Configures the RURP socket per the `DIP32_28C512_EEPROM` pinout.

**The firmware handler is working and correct.** The `adapter-required` classification exists
solely because the RURP socket is a 32-pin DIP socket wired for the `DIP32_28C512_EEPROM`
layout, and these chips have only 24 pins at a different physical position.

### Status

These chips remain `support_status: adapter-required` until:
1. A physical DIP24-to-DIP32 adapter is built per this spec.
2. A golden write+read-back round-trip is verified on real hardware.

Graduation to `supported` is explicitly out of v1.13 scope.

---

## 2. Adapter Pin Table

The adapter maps every DIP24 chip pin to its corresponding DIP32 socket pin. The DIP32 socket
is wired to RURP bus lines per the `DIP32_28C512_EEPROM` pinout (the layout that
`configure_eeprom28c` uses). The 5V EEPROM-specific layout — not the UV-EPROM layout — must
be used; the UV-EPROM layout has VPP on pin 1 and a different address bus routing and is
incompatible with these 5V-only chips.

Ground truth source: `firestarter_app/firestarter/data/pinouts.json` —
`DIP24_2816` and `DIP32_28C512_EEPROM` entries.

### Connected Pins (adapter wire-through)

| DIP24 chip pin | Chip function | DIP32 socket pin | RURP bus role | Notes |
|:--------------:|:-------------|:----------------:|:-------------|:------|
| 1 | A7 | 5 | A7 | Direct signal match |
| 2 | A6 | 6 | A6 | Direct signal match |
| 3 | A5 | 7 | A5 | Direct signal match |
| 4 | A4 | 8 | A4 | Direct signal match |
| 5 | A3 | 9 | A3 | Direct signal match |
| 6 | A2 | 10 | A2 | Direct signal match |
| 7 | A1 | 11 | A1 | Direct signal match |
| 8 | A0 | 12 | A0 | Direct signal match |
| 9 | D0 | 13 | D0 | Direct signal match |
| 10 | D1 | 14 | D1 | Direct signal match |
| 11 | D2 | 15 | D2 | Direct signal match |
| 12 | GND | 16 | GND | Direct signal match |
| 13 | D3 | 17 | D3 | Direct signal match |
| 14 | D4 | 18 | D4 | Direct signal match |
| 15 | D5 | 19 | D5 | Direct signal match |
| 16 | D6 | 20 | D6 | Direct signal match |
| 17 | D7 | 21 | D7 | Direct signal match |
| 18 | /CE | 22 | /CE | Direct signal match |
| 19 | A10 | 23 | A10 | NC on AT28C04 (9 addr bits only) |
| 20 | /OE | 24 | /OE | Direct signal match |
| **21** | **/WE** | **30** | **/WE (rw-pin)** | **Key reroute — see §3** |
| 22 | A9 | 26 | A9 | NC on AT28C04 (9 addr bits only) |
| 23 | A8 | 27 | A8 | Direct signal match |
| 24 | VCC | 32 | VCC | Direct signal match |

### Unconnected DIP32 Socket Pins (leave NC — no connection)

| DIP32 socket pin | RURP bus role | Reason left NC |
|:----------------:|:-------------|:--------------|
| 1 | NC / A18 | Not used in DIP32_28C512_EEPROM layout |
| 3 | A15 | AT28C16 max is 11 address bits (A0–A10); A15 unused |
| 4 | A12 | AT28C16 max is 11 address bits; A12 unused |
| 25 | A11 | AT28C16 max is 11 address bits; A11 unused |
| 28 | A13 | AT28C16 max is 11 address bits; A13 unused |
| 29 | A14 | AT28C16 max is 11 address bits; A14 unused |
| 31 | NC | Not used in DIP32_28C512_EEPROM layout |

---

## 3. Safety Notes

### Key Reroute: /WE (chip pin 21 → socket pin 30)

**This is the critical reroute that makes the adapter necessary.**

In the DIP24 EEPROM layout (`DIP24_2816` / `DIP24_6116`), the Write Enable signal (/WE)
is at **chip pin 21**. In the RURP DIP32 socket configured for `DIP32_28C512_EEPROM`,
the /WE signal (rw-pin) is at **socket pin 30**.

Without the adapter, inserting a DIP24 chip directly into the DIP32 socket would connect:
- **Chip pin 21 (/WE) → socket pin 21 → RURP bus line for D7 (data bit 7)**

This is electrically harmless (D7 is a 5V logic signal, not 12V VPP), but it means
the firmware cannot assert /WE on the chip — the write path would not function.
The chip would be readable but not writable.

With the adapter, chip pin 21 (/WE) is routed to DIP32 socket pin 30 (/WE), so the
firmware can correctly assert write-enable pulses to the chip.

### No VPP Rail — 5V-Only Operation

**Neither the DIP24_2816 pinout nor the DIP32_28C512_EEPROM pinout has a `vpp-pin` entry**
(verified in `pinouts.json`). These chips are 5V single-supply EEPROMs. The RURP VPP
boost regulator is never asserted during `configure_eeprom28c` operation.

There is no high-voltage hazard from an incorrectly-built adapter (unlike UV-EPROM adapters
where a miswired VPP line at 12V–18V would damage the chip). The worst case for a wiring
error is a non-functioning read or write — not chip destruction.

### AT28C04 Differences (NC Pins)

The AT28C04 has 9 address bits (A0–A8) versus the AT28C16's 11 address bits (A0–A10).
On AT28C04:
- **Chip pin 22 (A9)** — No Connect on the chip. The adapter still connects it to
  socket pin 26, but firmware restricts address driving to 9 bits via `mem_size`.
  The chip simply ignores the A9 signal.
- **Chip pin 19 (A10)** — Same: NC on AT28C04; adapter connects to socket pin 23 (A10).

This is electrically safe — the chip's NC pins float high internally and the over-driven
address signals have no effect on a chip with fewer address bits.
