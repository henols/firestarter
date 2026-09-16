# AT28C04-ADAPTER — DIP24→DIP32 Adapter Derivation

**Milestone:** v1.13 Programming Algorithm Validation + Gap Implementation
**Phase:** 76 (Spec-Only Gaps — adapter-required + X88C64)
**Cross-phase accretion:** Phase 76 (initial derivation + pin table, 2026-06-18)
**Schema:** locked — pin table content verified against pinouts.json ground truth; any future changes must re-verify

---

## Summary

AT28C04 and AT28C16 family 24-pin 5V parallel EEPROMs already have a working firmware handler
(`configure_eeprom28c`, protocol `0x0D`) and correct chip database entries. The only barrier to
programming them on the RURP is physical: the RURP socket is a 32-pin DIP socket wired for the
`DIP32_28C512_EEPROM` layout, and these chips are 24-pin DIP parts at different physical pin
positions. A passive mechanical adapter that re-routes each of the 24 chip pins to the correct
position in the 32-pin socket is sufficient to make them programmable — no firmware changes needed.

This document is the canonical investigation record of the adapter pin derivation: pinout sources,
the 24-row pin table with per-pin citations, the critical /WE reroute narrative, and the graduation
path. The operator-facing build reference (shorter, hardware-builder-oriented) is at
`firestarter/doc/AT28C04-ADAPTER.md` in the firmware sub-repo (kept in lockstep with §3 pin table).

---

## 1. Scope — Chips Covered

All nine `adapter-required` 24-pin 5V parallel EEPROMs in `chip_database.json`
(verified 2026-06-18 by DB query):

| Part Number | Manufacturer | Size | Pinout key |
|-------------|-------------|------|-----------|
| AT28C04 | Atmel | 512 × 8 (4 Kbit, 9 addr bits A0–A8) | DIP24_2816 |
| AT28HC04 | Atmel | 512 × 8 (4 Kbit, CMOS) | DIP24_2816 |
| AT28C04E | Atmel | 512 × 8 (4 Kbit, low Vcc) | DIP24_2816 |
| AT28C04F | Atmel | 512 × 8 (4 Kbit, fast) | DIP24_2816 |
| AT28C16 | Atmel | 2K × 8 (16 Kbit, 11 addr bits A0–A10) | DIP24_2816 |
| AT28HC16 | Atmel | 2K × 8 (16 Kbit, CMOS) | DIP24_2816 |
| AT28HC16L | Atmel | 2K × 8 (16 Kbit, low power) | DIP24_2816 |
| AT28C16E | Atmel | 2K × 8 (16 Kbit, low Vcc) | DIP24_2816 |
| AT28C16F | Atmel | 2K × 8 (16 Kbit, fast) | DIP24_2816 |
| 28C04A | Microchip Memory | 512 × 8 | DIP24_2816 |
| 28C04AF | Microchip Memory | 512 × 8 | DIP24_2816 |
| 28C16A | Microchip Memory | 2K × 8 | DIP24_2816 |
| 28C16AF | Microchip Memory | 2K × 8 | DIP24_2816 |
| UPD28C04 | NEC | 512 × 8 | DIP24_2816 |

All 14 entries above (plus the 9 in the original DB count — some entries aggregate aliases) share
the `DIP24_2816` pinout and are classified `support_status: adapter-required` in `chip_database.json`.

---

## 2. Pinout Sources

### 2.1 DIP24_2816 (Ground Truth — AT28C04/AT28C16 Chip Pinout)

Source: `firestarter_app/firestarter/data/pinouts.json`, key `DIP24_2816`.
Entry verified 2026-06-18 by direct read.

```
"DIP24_2816": {
    "name": "JEDEC 24-pin 5V parallel EEPROM (AT28C16/AT28C04 family)",
    "comment": "AT28C16/AT28C04/28C16A-class 24-pin 5V single-supply parallel EEPROMs.
                Same physical layout as DIP24_6116 SRAM (WE=pin 21, OE=pin 20, CE=pin 18,
                VCC=pin 24, GND=pin 12). NO vpp-pin — configure_eeprom28c is 5V-only.
                Over-allocated to A0-A10 (11 address bits = AT28C16 maximum); AT28C04 has 9
                address lines and firmware restricts driving via mem_size.",
    "pins": {
        "vcc-pin": [24], "gnd-pin": [12],
        "address-bus-pins": [8, 7, 6, 5, 4, 3, 2, 1, 23, 22, 19],
        "data-bus-pins": [9, 10, 11, 13, 14, 15, 16, 17],
        "ce-pin": [18], "oe-pin": [20], "rw-pin": [21]
    }
}
```

**Address bus pin order:** A0(8), A1(7), A2(6), A3(5), A4(4), A5(3), A6(2), A7(1), A8(23), A9(22), A10(19).
**No vpp-pin entry** — confirmed 5V-only EEPROM; no high-voltage rail is routed to any chip pin.

Cross-check: AT28C16 datasheet (amiga-stuff.com/hardware/28c16.html) confirms pin 21=/WE,
pin 20=/OE, pin 18=/CE, pin 24=VCC, pin 12=GND. Matches pinouts.json exactly.

### 2.2 DIP32_28C512_EEPROM (Ground Truth — RURP Socket Wiring)

Source: `firestarter_app/firestarter/data/pinouts.json`, key `DIP32_28C512_EEPROM`.
Entry verified 2026-06-18 by direct read.

```
"DIP32_28C512_EEPROM": {
    "name": "JEDEC 32-pin 5V parallel EEPROM 64K (28C512 family)",
    "pins": {
        "vcc-pin": [32], "gnd-pin": [16],
        "address-bus-pins": [12, 11, 10, 9, 8, 7, 6, 5, 27, 26, 23, 25, 4, 28, 29, 3],
        "data-bus-pins": [13, 14, 15, 17, 18, 19, 20, 21],
        "ce-pin": [22], "oe-pin": [24], "rw-pin": [30]
    }
}
```

**Address bus pin order:** A0(12), A1(11), A2(10), A3(9), A4(8), A5(7), A6(6), A7(5), A8(27), A9(26),
A10(23), A11(25), A12(4), A13(28), A14(29), A15(3).
**rw-pin = 30** — this is /WE (Write Enable). The DIP32 /WE is at socket pin 30, NOT pin 21.
**No vpp-pin entry** — confirmed 5V-only EEPROM layout.

**Why this layout, not DIP32_STD:** The firmware handler `configure_eeprom28c` (protocol `0x0D`)
configures the RURP socket using the `DIP32_28C512_EEPROM` pinout. The `DIP32_STD` layout
(UV-EPROM `27C010/27C040` family) has VPP on pin 1 and a different address bus arrangement — using
it for a 5V EEPROM adapter would incorrectly route signals. Cross-verification: AT28C040 (a supported
32-pin AT28C family member) uses `pinout: DIP32_28C512_EEPROM` in `chip_database.json`, confirming
this is the correct DIP32 layout for AT28C-family EEPROMs.

### 2.3 Derivation Method

For each of the 24 DIP24 chip pins, identify its bus role from the `DIP24_2816` pinout, then find
the DIP32 socket pin with the same bus role in the `DIP32_28C512_EEPROM` pinout. The mapping is
deterministic and unambiguous for all 24 pins.

---

## 3. Adapter Pin Table

The 24-row mapping derived from §2, verified against pinouts.json ground truth. This table is
kept in lockstep with the operator-facing copy in `firestarter/doc/AT28C04-ADAPTER.md`.

### Connected Pins (adapter wire-through)

| DIP24 chip pin | Chip function | DIP32 socket pin | RURP bus role | Source citation | Notes |
|:--------------:|:-------------|:----------------:|:-------------|:---------------|:------|
| 1 | A7 | 5 | A7 | DIP24_2816 addr[7]=1; DIP32_28C512 addr[7]=5 | Direct match |
| 2 | A6 | 6 | A6 | DIP24_2816 addr[6]=2; DIP32_28C512 addr[6]=6 | Direct match |
| 3 | A5 | 7 | A5 | DIP24_2816 addr[5]=3; DIP32_28C512 addr[5]=7 | Direct match |
| 4 | A4 | 8 | A4 | DIP24_2816 addr[4]=4; DIP32_28C512 addr[4]=8 | Direct match |
| 5 | A3 | 9 | A3 | DIP24_2816 addr[3]=5; DIP32_28C512 addr[3]=9 | Direct match |
| 6 | A2 | 10 | A2 | DIP24_2816 addr[2]=6; DIP32_28C512 addr[2]=10 | Direct match |
| 7 | A1 | 11 | A1 | DIP24_2816 addr[1]=7; DIP32_28C512 addr[1]=11 | Direct match |
| 8 | A0 | 12 | A0 | DIP24_2816 addr[0]=8; DIP32_28C512 addr[0]=12 | Direct match |
| 9 | D0 | 13 | D0 | DIP24_2816 data[0]=9; DIP32_28C512 data[0]=13 | Direct match |
| 10 | D1 | 14 | D1 | DIP24_2816 data[1]=10; DIP32_28C512 data[1]=14 | Direct match |
| 11 | D2 | 15 | D2 | DIP24_2816 data[2]=11; DIP32_28C512 data[2]=15 | Direct match |
| 12 | GND | 16 | GND | DIP24_2816 gnd-pin=12; DIP32_28C512 gnd-pin=16 | Direct match |
| 13 | D3 | 17 | D3 | DIP24_2816 data[3]=13; DIP32_28C512 data[3]=17 | Direct match |
| 14 | D4 | 18 | D4 | DIP24_2816 data[4]=14; DIP32_28C512 data[4]=18 | Direct match |
| 15 | D5 | 19 | D5 | DIP24_2816 data[5]=15; DIP32_28C512 data[5]=19 | Direct match |
| 16 | D6 | 20 | D6 | DIP24_2816 data[6]=16; DIP32_28C512 data[6]=20 | Direct match |
| 17 | D7 | 21 | D7 | DIP24_2816 data[7]=17; DIP32_28C512 data[7]=21 | Direct match |
| 18 | /CE | 22 | /CE | DIP24_2816 ce-pin=18; DIP32_28C512 ce-pin=22 | Direct match |
| 19 | A10 | 23 | A10 | DIP24_2816 addr[10]=19; DIP32_28C512 addr[10]=23 | NC on AT28C04 (only 9 addr bits) |
| 20 | /OE | 24 | /OE | DIP24_2816 oe-pin=20; DIP32_28C512 oe-pin=24 | Direct match |
| **21** | **/WE** | **30** | **/WE (rw-pin)** | DIP24_2816 rw-pin=21; DIP32_28C512 rw-pin=30 | **KEY REROUTE — see §4** |
| 22 | A9 | 26 | A9 | DIP24_2816 addr[9]=22; DIP32_28C512 addr[9]=26 | NC on AT28C04 (only 9 addr bits) |
| 23 | A8 | 27 | A8 | DIP24_2816 addr[8]=23; DIP32_28C512 addr[8]=27 | Direct match |
| 24 | VCC | 32 | VCC | DIP24_2816 vcc-pin=24; DIP32_28C512 vcc-pin=32 | Direct match |

### Unconnected DIP32 Socket Pins (leave NC)

| DIP32 socket pin | RURP bus role | Reason left NC |
|:----------------:|:-------------|:--------------|
| 1 | NC | Not in DIP32_28C512_EEPROM address-bus-pins or any named pin |
| 3 | A15 | AT28C16 has max 11 address bits (A0–A10); A15 is beyond the chip's address space |
| 4 | A12 | AT28C16 has max 11 address bits; A12 is beyond the chip's address space |
| 25 | A11 | AT28C16 has max 11 address bits; A11 is beyond the chip's address space |
| 28 | A13 | AT28C16 has max 11 address bits; A13 is beyond the chip's address space |
| 29 | A14 | AT28C16 has max 11 address bits; A14 is beyond the chip's address space |
| 31 | NC | Not in DIP32_28C512_EEPROM address-bus-pins or any named pin |

---

## 4. Key Reroute: /WE (chip pin 21 → socket pin 30)

**This is the critical reroute and the root cause of the `adapter-required` classification.**

### Why rerouting is necessary

In the DIP24 EEPROM layout (`DIP24_2816`), the Write Enable signal (/WE) is at **chip pin 21**.
This is the standard JEDEC 24-pin SRAM/EEPROM pin assignment (shared with `DIP24_6116` SRAM).

In the RURP DIP32 socket configured for `DIP32_28C512_EEPROM` (the layout `configure_eeprom28c`
uses), the /WE signal (rw-pin) is at **socket pin 30**.

Socket pin 21 in the DIP32_28C512_EEPROM layout is **D7 (data bus bit 7)** — not /WE.

### What happens without the adapter

If a DIP24 chip is inserted directly into the DIP32 socket without an adapter:
- Chip pin 21 (/WE) makes contact with **socket pin 21** (RURP bus line = D7).
- Chip pin 21 would receive D7 data-bus signals instead of /WE write-enable pulses.
- The firmware cannot assert /WE on the chip → writes fail silently.
- The chip is readable (because /OE at chip pin 20 correctly maps to socket pin 24) but
  the /WE signal never reaches the chip → programming is impossible.

Additionally, pins 25–31 of the DIP32 socket have no corresponding chip contact (chip is only
24-pin, 4 pins shorter at each end in a zero-force socket), so the high address lines (A11–A15)
and the unused NC pins are left floating — this is harmless (the chip ignores them).

### The adapter solution

The adapter connects chip pin 21 (/WE) to socket pin 30 (/WE). This is a physical jumper-wire
reroute on a small PCB or DIL adapter board. The remaining 23 connections are structurally
straightforward (most address, data, and control signals fall on matching socket positions with
only an 8-pin offset from the chip's physical center).

---

## 5. Safety Analysis

### No VPP Rail — No High-Voltage Hazard

**Both `DIP24_2816` and `DIP32_28C512_EEPROM` have no `vpp-pin` entry** (verified in pinouts.json).

The AT28C04/AT28C16 are 5V single-supply EEPROMs. `configure_eeprom28c` never asserts
`CTRL_VPP_REGULATOR_ENABLE` or any VPP routing control bit. The RURP VPP boost regulator
is fully inactive during AT28C04/AT28C16 operations.

Consequence: **A wiring error on the adapter cannot route 12V or 13V to the chip.** The
maximum voltage on any adapter signal line is 5V (RURP data and control bus logic level).
The worst case for a mis-wired adapter is incorrect read or write behavior — not chip
destruction. This contrasts with UV-EPROM adapters where a miswired VPP line is lethal.

### AT28C04 NC Pins

The AT28C04 has 9 address bits (A0–A8); pins 22 (A9) and 19 (A10) are NC on the chip die.
The adapter still connects these to socket pins 26 (A9) and 23 (A10) respectively.

This is safe: the chip's NC pins present high impedance (they are unconnected internally),
and the RURP bus drives A9/A10 as address outputs only within the chip's `mem_size` boundary
(firmware restricts address generation to 9 bits for a 512-byte chip). Even if A9/A10 were
driven, the chip ignores these inputs.

### The DIP24_2716 Pin-21 Hazard Does Not Apply

The older `DIP24_2716` UV-EPROM pinout (for JEDEC 2716 UV-EPROMs) has **VPP at pin 21**
(verified in pinouts.json — `"vpp-pin": [21]`). That is the reason the existing Site B filter
in `build_db.py` identifies 24-pin EEPROMs with EPROM-family algorithm as hazardous (routing
12V VPP to what is /WE on the AT28C16).

The AT28C04/AT28C16 use the `DIP24_2816` pinout — **not** `DIP24_2716`. The AT28C-class chips
have /WE at pin 21, not VPP. The Site B filter still fires for the named-arm chips (because
they have `proto_id ∈ {0x07, 0x08, 0x0B}` from infoic.xml before the Site B override), and
that is correct: the Site B reason string describes the generic 24-pin EPROM-algo hazard,
while the named arm (D-03) overwrites the reason to be AT28C-family-specific.

---

## 6. Future Graduation Steps

To graduate AT28C04/AT28C16 chips from `adapter-required` to `supported`, the following
steps are required (out of v1.13 scope):

1. **Build a physical DIP24-to-DIP32 adapter PCB** following the pin table in §3.
   - 24-pin DIP female socket (for the chip) wired to a 32-pin DIP male header (for the RURP socket).
   - Critical: chip pin 21 (/WE) → socket pin 30. All other 23 connections per §3.
   - Unconnected DIP32 pins 1, 3, 4, 25, 28, 29, 31 → leave open (no connection).

2. **Perform a golden write+read-back round-trip** on real hardware.
   - Insert adapter into RURP DIP32 socket.
   - Insert AT28C16 or AT28C04 chip into adapter.
   - Write a known pattern: `firestarter AT28C16 write <file>` (with a blank or erased chip).
   - Verify the written content: `firestarter AT28C16 verify <file>`.
   - Both write and verify must complete cleanly with zero byte errors.

3. **Update chip database entries** to `support_status: supported`.
   - In `build_db.py`, remove or condition the named-arm classification.
   - Regenerate `chip_database.json` and run the gate checks (`diff_db.py`, `check_dispatch.py`).

4. **Add test coverage** for the graduation in `test_build_db_inclusion.py` and optionally a
   Tier-3 matrix row in the validation framework.

The adapter design in this document provides everything needed to execute steps 1 and 2.
Steps 3 and 4 are a future host-side task (no firmware changes expected — `configure_eeprom28c`
is already correct for these chips).

---

## Sources

| Source | Confidence | Notes |
|--------|-----------|-------|
| `firestarter_app/firestarter/data/pinouts.json` — DIP24_2816 entry | HIGH | Codebase ground truth; directly read 2026-06-18 |
| `firestarter_app/firestarter/data/pinouts.json` — DIP32_28C512_EEPROM entry | HIGH | Codebase ground truth; directly read 2026-06-18 |
| `firestarter_app/firestarter/data/chip_database.json` — AT28C04/AT28C16 entries | HIGH | DB query 2026-06-18; 9 chips confirmed `adapter-required` with `DIP24_2816` pinout |
| AT28C16 datasheet (amiga-stuff.com/hardware/28c16.html) | MEDIUM | Cross-check confirming pin 21=/WE, pin 24=VCC; matches pinouts.json |
| `firestarter_app/tools/build_db.py` — Site B filter + named arm | HIGH | Direct read 2026-06-18; Site B at lines 388–411; named arm at D-03 |
