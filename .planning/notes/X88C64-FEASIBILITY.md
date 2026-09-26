# X88C64-FEASIBILITY — XICOR X88C64P RURP Feasibility Verdict

**Phase:** 76 (Spec-Only Gaps — adapter-required + X88C64)
**Status:** VERDICT CLOSED — documented feasible-candidate; handler deferred
**Protocol:** 0x34 (no IC2_ALG constant; see `v1.13-PROTOCOL-ENUMERATION.md` row `0x34`)
**Date:** 2026-06-18

---

## Summary

The XICOR X88C64P is an 8K×8 (64 Kbit) 5V-only parallel EEPROM in a 24-pin DIP package. It
presents an **8051-compatible multiplexed address/data bus** interface (ALE, /WR, /RD, /PSEN,
/CE, WC control signals with A/D0–A/D7 multiplexed address+data pins), not a standard parallel
/WE /OE /CE bus. The RURP can physically drive this chip (correct socket size, correct voltage),
but the bus protocol requires non-trivial firmware adaptation to implement the ALE-latch +
/WR-strobe write cycle. **Overall feasibility: MEDIUM — documented feasible-candidate.**

**Correction to prior classification:** The chip's previous `unsupported_reason` string was
misleading on two points: it called the chip a "serial" or "hybrid" device (wrong — it is
**parallel DIP24**) and it implied STORE/RECALL operations (wrong — the X88C64P has
**NO STORE/RECALL pins**). STORE/RECALL belongs to the older Xicor NOVRAM family (X2210/X2212,
1985), which is a battery-backed SRAM+EEPROM combination product. The X88C64P is a different
product line. This document is the canonical record of the corrected verdict. The DB
`unsupported_reason` (reworded as part of Phase 76, plan 76-01) summarizes this verdict.

**Handler status:** No `0x34` firmware handler is committed this phase (D-01 locked). The chip
remains `support_status: protocol-not-implemented` in `chip_database.json`. The handler is a
deferred future requirement pending ALE routing investigation and bench verification.

---

## 1. Device Identity

| Field | Value | Source |
|-------|-------|--------|
| Part number (DIP variant) | X88C64P | X88C64P datasheet page 1 via alldatasheet.com |
| Part number (SOIC variant) | X88C64S | Same datasheet; SOIC excluded by SMD filter |
| Manufacturer | XICOR Inc. (later acquired by Intersil/Renesas) | Datasheet cover |
| Organization | 8K × 8 (65,536 bits = 64 Kbit) | Datasheet page 1 |
| Package | DIP24 (24-pin plastic DIP, 'P' suffix = DIP) | Datasheet page 1 |
| Technology | CMOS Textured Poly Floating Gate EEPROM | Datasheet page 1 |
| VCC supply | 5V ±10% (4.5V–5.5V) | Datasheet page 8 |
| VPP supply | None — 5V single-supply only | No VPP pin exists on device |
| Dual-plane architecture | Two independent 4K×8 arrays; CONCURRENT READ WRITE™ allows executing from one plane while writing the other | Datasheet pages 1–2 |
| Endurance | 100,000 write cycles | Datasheet page 1 |
| Data retention | 100 years | Datasheet page 1 |
| DB support_status | `protocol-not-implemented` | `chip_database.json` (verified 2026-06-18) |
| DB pinout | `DIP24_6116` | `chip_database.json` (verified 2026-06-18) |
| Protocol ID | `0x34` | `chip_database.json` + `v1.13-PROTOCOL-ENUMERATION.md` row 0x34 |

**Reference to protocol enumeration:** The `0x34` row in `.planning/milestones/v1.13-PROTOCOL-ENUMERATION.md`
classifies this chip as `feasible-gap (Phase 76 scope) — overturn v1.12 implicit infeasibility`.
This verdict document provides the technical backing for that classification.

---

## 2. Interface Architecture

### Critical Finding: 8051 Multiplexed Address/Data Bus

**The X88C64P does NOT present a standard /WE /OE /CE parallel EEPROM interface.**

It presents an **8051-compatible multiplexed-bus interface** designed for direct connection to
Intel 8031/8051 family microcontrollers operating in expanded multiplexed mode.

Source: X88C64P datasheet page 2 (alldatasheet.com html-pdf/34232/XICOR/X88C64P/257/2).

### DIP24 Pin Description

| Pin | Function | Description |
|-----|----------|-------------|
| 1 | NC | No Connect |
| 2 | A12 | Upper address bit 12 |
| 3 | NC | No Connect |
| 4 | NC | No Connect |
| 5 | WC | Write Control (active LOW to enable writes; HIGH aborts write cycle) |
| 6 | /PSEN | Program Store Enable (controls code-fetch reads from EEPROM plane) |
| 7 | A/D0 | Multiplexed Address/Data bit 0 |
| 8 | A/D1 | Multiplexed Address/Data bit 1 |
| 9 | A/D2 | Multiplexed Address/Data bit 2 |
| 10 | A/D3 | Multiplexed Address/Data bit 3 |
| 11 | A/D4 | Multiplexed Address/Data bit 4 |
| 12 | VSS | Ground |
| 13 | A/D5 | Multiplexed Address/Data bit 5 |
| 14 | A/D6 | Multiplexed Address/Data bit 6 |
| 15 | A/D7 | Multiplexed Address/Data bit 7 |
| 16 | /CE | Chip Enable (active LOW) |
| 17 | A10 | Address bit 10 (upper) |
| 18 | /RD | Read strobe (active LOW) |
| 19 | A11 | Address bit 11 (upper) |
| 20 | A9 | Address bit 9 (upper) |
| 21 | A8 | Address bit 8 (upper) |
| 22 | ALE | Address Latch Enable — address is latched on falling edge |
| 23 | /WR | Write strobe (active LOW) |
| 24 | VCC | +5V supply |

### Comparison to Standard RURP Parallel Bus

The RURP firmware drives a standard parallel bus:
- Dedicated address lines (A0–A18) on 74HC573 latches.
- Dedicated data lines (D0–D7) on a separate bidirectional bus.
- Separate /WE, /OE, /CE control register bits.

The X88C64P requires:
- **Multiplexed A/D bus:** The same 8 pins carry address (A0–A7, latched when ALE falls) and
  then data in successive phases. The RURP cannot natively time-multiplex address and data on
  the same bus without firmware logic to sequence ALE, then write data, on the same physical pins.
- **ALE signal:** Requires a dedicated toggling control signal (ALE = Address Latch Enable) that
  the RURP does not currently expose for this purpose. ALE routing to a RURP control bit is an
  open question (see §4 and §5).
- **Separate upper address pins:** A8–A12 are on dedicated pins (not multiplexed) — this portion
  is straightforward to drive via the RURP address bus latches.
- **/WR strobe instead of /WE:** Write timing uses a /WR strobe after address latching (not a
  simple /WE pulse). This is structurally similar to /WE but the sequencing is different.

---

## 3. Write Protocol

### STORE/RECALL Correction

**The X88C64P has NO STORE/RECALL pins.** This is a firm, HIGH-confidence finding.

The STORE/RECALL concept applies to Xicor's older NOVRAM family — specifically the X2210, X2212,
and X2201A series from the 1985 Xicor Data Book (bitsavers.org/components/xicor/1985_Xicor_Data_Book.pdf).
Those chips are battery-backed SRAM combined with an underlying EEPROM, with explicit STORE (SRAM →
EEPROM) and RECALL (EEPROM → SRAM) pin-activated sequences. The X88C64P (manufactured 1994–1996)
is a completely different product: a pure EEPROM with no SRAM plane and no STORE/RECALL pins.

Survey of X88C64P datasheet pages 1–10: no mention of STORE, RECALL, or NOVRAM terminology.
All references to STORE/RECALL in the project planning documents (ROADMAP/CONTEXT) were based on
the X88C64P's DB entry labeling it "XICOR NovRAM" — that label was applied by the minipro
infoic.xml source database and is misleading for this specific chip. **This verdict corrects
the record.** The ALE/WR/RD protocol is the actual interface.

### Address Latching

From X88C64P datasheet page 3:

> "When ALE is HIGH, the A/D0–A/D7 and A8–A12 addresses flow into the device. The addresses,
> both low and high order, are latched when ALE transitions LOW."

Sequence:
1. Assert /CE LOW.
2. Place lower address (A0–A7) on A/D0–A/D7 pins.
3. ALE goes HIGH → address flows into device.
4. ALE transitions LOW → address is latched.

### Write Cycle

From X88C64P datasheet page 4:

> "A write is performed by latching the addresses on the falling edge of ALE. Then WR is strobed
> LOW followed by valid data being presented at the A/D0–A/D7 pins."

Full write sequence:
1. Assert /CE LOW.
2. Set A8–A12 on upper address pins.
3. Place A0–A7 on A/D0–A/D7 pins; pulse ALE HIGH→LOW to latch address.
4. Place D0–D7 data on A/D0–A/D7 pins.
5. Strobe /WR LOW then HIGH — data is latched on the rising edge of /WR.
6. Keep WC LOW during the write cycle; assert WC HIGH before tBLC-Max to abort.

### Page Write (up to 32 bytes)

The X88C64P supports **page-write mode**: up to 32 bytes can be written in a single internal
write cycle. The host firmware repeatedly cycles through steps 3–5 (address latch → data write)
for each byte in the page, then the internal write cycle executes once for all bytes.

Source: X88C64P datasheet page 1 feature list (alldatasheet.com page 1 via html proxy).

### Write Cycle Completion: Toggle-Bit Polling

Write cycle completion is determined via toggle-bit polling (I/O6):

> "I/O6 will toggle from HIGH to LOW and LOW to HIGH on subsequent attempts to read the device
> during the internal write cycle."

The A12 address state must match between the initiating write and the polling reads. This
is functionally similar to the DQ7 polling used by `configure_eeprom28c`, but toggles on I/O6.

Write cycle time: approximately 100 µs [ASSUMED — indirect page-5 reference; see Assumptions §6].
Power-up timings: tPUR = 1 ms (read recovery), tPUW = 5 ms (write ready). Source: datasheet page 8.

### Write Abort

> "WC is driven HIGH (before tBLC Max) after Write (WR) goes HIGH" to abort a write cycle.

WC is a dedicated control pin (pin 5) used to enable and abort write cycles.

### Block Protect

A Software Block Protect Register allows individual write-lock capability for each of the eight
1K-byte blocks within the 8K address space. Source: X88C64P datasheet page 1.

---

## 4. RURP Feasibility Assessment

| Dimension | Assessment | Notes |
|-----------|-----------|-------|
| Package | Compatible | DIP24 fits in the RURP socket with a DIP24→DIP32 adapter (same adapter pattern as AT28C04/AT28C16) |
| Voltage | Compatible | 5V-only, no VPP required; RURP_VPP_CEILING_MV=22000 is irrelevant for a 5V device |
| Upper address pins (A8–A12) | Compatible | Dedicated pins; directly driven by RURP address bus latches |
| /CE, /RD signals | Compatible | Standard active-LOW enables; map to RURP /CE and /OE controls |
| A/D bus (lower 8 address + data) | Non-trivial | Requires firmware to time-multiplex address and data on the same 8 pins, sequenced by ALE |
| ALE signal routing | Open question | Needs RURP control-register investigation: is there an available bit in `rurp_pinout.h` that can be routed to toggle ALE? If not, new control-bit plumbing needed. |
| /WR strobe timing | Non-trivial (manageable) | /WR is similar to /WE in structure; the ALE-latch precondition is the non-trivial part |
| Toggle-bit polling | Non-trivial (manageable) | I/O6 toggle polling differs from DQ7 `configure_eeprom28c` polling but same concept |
| WC (Write Control) | Non-trivial (manageable) | Additional control pin; needs a RURP control-register bit or direct GPIO |
| Overall | **MEDIUM — feasible-candidate** | Handler not implemented this phase (D-01) |

**Why MEDIUM (not infeasible):**
- The chip is DIP24, 5V — physically compatible with the RURP socket (with adapter) and voltage rail.
- The bus is parallel (not serial); all signals are standard digital I/O — no special analog circuits.
- The ALE/WR/RD multiplexed-bus protocol is well-understood and used by 8051-class firmware.
- The RURP Arduino can bit-bang ALE timing in firmware (no dedicated hardware required).

**Why MEDIUM (not immediate/easy):**
- ALE routing is the critical open question: the RURP control register drives the address latch
  enables via 74HC573 OE signals, not a freely-available GPIO. A free control bit may or may not
  exist for ALE without PCB changes.
- The firmware must implement a new write sequencing pattern (address-phase → data-phase on same pins)
  rather than the standard parallel address+data simultaneous-drive model.
- No existing RURP firmware handler provides a reference ALE multiplexed-bus implementation.

---

## 5. What is Needed for a Future Handler

A future milestone implementing the 0x34 handler needs:

1. **ALE routing investigation** — Read `firestarter/include/rurp_pinout.h` control-register bit
   definitions. Determine if any currently-unused CTRL_* bit can be used to toggle ALE via the
   74HC573 address latch or a direct GPIO line. If no bit is available without PCB changes,
   document the constraint (may require a new shield revision or a minor PCB mod).

2. **Firmware ALE/WR/RD sequence** — Implement a new `configure_eeprom_x88c64()` handler in
   a new `eeprom_x88c64.cpp` source file:
   - Address-phase: set upper address (A8–A12), pulse ALE (HIGH→LOW) while driving lower address
     (A0–A7) on the A/D bus.
   - Data-phase: place data byte on A/D bus, strobe /WR (LOW→HIGH).
   - Page-write loop: repeat for up to 32 bytes before releasing the write cycle.
   - Completion polling: read I/O6 via /RD strobe and check toggle-bit state.
   - WC handling: assert WC LOW for write enable; HIGH to abort if needed.

3. **Dispatch wiring** — Add a `0x34` dispatch arm to `memory.cpp:configure_memory`, calling
   the new handler. Update `KNOWN_PROTOCOLS` in `firestarter_app/tools/build_db.py`.

4. **Bench verification** — Write a known pattern to a physical X88C64P chip, read it back,
   and verify byte-for-byte correctness. Run N≥5 trials. Check I/O6 polling behavior with a
   logic analyzer or scope if toggling is not observed.

5. **Gate checks** — Run `check_dispatch.py` and `diff_db.py` to confirm the chip is classified
   correctly after the handler is wired.

6. **Flash ceiling check** — Verify `pio run -e leonardo` stays under the ~88% flash ceiling
   (Leonardo = 28,672 bytes; each new handler adds ~1–3 KB). Phase 74's ceiling carry-forward
   applies.

---

## 6. Assumptions Log

| # | Claim | Confidence | Source | Risk if Wrong |
|---|-------|-----------|--------|---------------|
| A4 | X88C64P write cycle time is ~100 µs | LOW | X88C64P datasheet page 5 indirect text reference; power-up timings (tPUR=1ms, tPUW=5ms) on page 8 don't directly state tWC | For feasibility purposes, "EEPROM-class timing" is sufficient — even if tWC is 1–10 ms (typical EE timing), it is compatible with firmware capability. The exact value does not affect the MEDIUM verdict. |
| A5 | X88C64P has NO STORE/RECALL pins | HIGH | Surveyed 10 of 14 datasheet pages; no STORE/RECALL mention anywhere in the X88C64P document; confirmed STORE/RECALL exists in X2210/X2212 NOVRAM family (1985 Xicor Data Book via bitsavers); X88C64P is a different product era and product line | HIGH confidence — absence is clearly confirmed across multiple pages. If wrong, the write protocol above would need to incorporate STORE/RECALL sequencing, but the physical pin description (§2) does not show any STORE/RECALL pins on the 24-pin package. |
| A6 | ALE routing is available via an existing RURP control-register bit | LOW | Not yet investigated; based on general knowledge that the 74HC573 OE line could in principle be used to sequence address latching | If wrong (no available bit), implementing the handler may require adding a new control bit (possible PCB change) or a creative multiplex approach using existing bits. This is the primary feasibility uncertainty. |
| A7 | DIP24_6116 pinout is an acceptable initial socket layout for X88C64P | MEDIUM | X88C64P is DIP24 5V; `DIP24_6116` is also DIP24 5V; both have GND=pin 12, VCC=pin 24 (matches X88C64P datasheet). The X88C64P's unique signals (ALE, WR, RD, WC, PSEN, A/D bus) will need custom firmware sequencing regardless of pinout entry | The pinout entry controls how the host builds the bus-config JSON; since the 0x34 handler is custom-sequenced, the specific pinout entry may be overridden or supplemented by handler-level logic. A dedicated `DIP24_X88C64` pinout entry may be cleaner. |

---

## A6 ALE-Routing Verdict (Phase 78)

A6 VERDICT: PCB-BLOCKED

**Confidence:** HIGH. Resolved by a source/schematic trace by Claude (D-01) — NOT an
operator bench trace — of the RURP control-register bit map (`rurp_pinout.h`), the
register-write path (`rurp_register_utils.h`), and the 74HC573 strobe inventory
(`rurp_shield.h`). This closes Assumption A6 (§6), which was LOW confidence.

### Why PCB-BLOCKED

The X88C64 needs a dedicated ALE (Address Latch Enable) signal at DIP socket pin 22 to
sequence its 8051 multiplexed A/D bus (§2). The trace shows there is **no free `CTRL_*`
bit and no free 74HC573 strobe** to drive ALE without a physical board change, and there
is **no control line provably idle during an X88C64 write** that could be safely reused.

### CTRL_* Bit Allocation — Every Bit Accounted For

**8-bit layout** (`#ifndef HARDWARE_REVISION`, `rurp_pinout.h:74–83`):

| Bit | CTRL_* function | Line | Free for ALE? |
|-----|-----------------|------|---------------|
| 0x01 | `CTRL_VPP_VPE_DROP_ENABLE` (aliased `CTRL_ADDRESS_LINE_16`) | rurp_pinout.h:75–76 | No — VPE drop / A16 |
| 0x02 | `CTRL_VPP_A9_ENABLE` | rurp_pinout.h:77 | No — A9 VPP (chip-ID reads) |
| 0x04 | `CTRL_VPE_ENABLE` | rurp_pinout.h:78 | No — VPE direct path |
| 0x08 | `CTRL_VPP_P1_ENABLE` | rurp_pinout.h:79 | No — VPP to socket pin 1 (Intel flash) |
| 0x10 | `CTRL_ADDRESS_LINE_17` | rurp_pinout.h:80 | No — address bit 17 |
| 0x20 | `CTRL_ADDRESS_LINE_18` | rurp_pinout.h:81 | No — address bit 18 |
| 0x40 | `CTRL_READ_WRITE` | rurp_pinout.h:82 | No — R/W direction, toggled on every bus access |
| 0x80 | `CTRL_VPP_REGULATOR_ENABLE` | rurp_pinout.h:83 | No — VPP boost regulator |

**Wide layout** (`#else` / `HARDWARE_REVISION`, `rurp_pinout.h:85–97`; production builds
use `-D HARDWARE_REVISION` per `platformio.ini`):

| Bit | CTRL_* function | Line | Free for ALE? |
|-----|-----------------|------|---------------|
| 0x01 | `CTRL_ADDRESS_LINE_16` | rurp_pinout.h:88 | No — A16 (split off from VPE_DROP) |
| 0x02 | `CTRL_VPP_A9_ENABLE` | rurp_pinout.h:89 | No |
| 0x04 | `CTRL_VPE_ENABLE` | rurp_pinout.h:90 | No |
| 0x08 | `CTRL_VPP_P1_ENABLE` | rurp_pinout.h:91 | No |
| 0x10 | `CTRL_ADDRESS_LINE_17` | rurp_pinout.h:92 | No |
| 0x20 | `CTRL_ADDRESS_LINE_18` | rurp_pinout.h:93 | No |
| 0x40 | `CTRL_READ_WRITE` | rurp_pinout.h:94 | No |
| 0x80 | `CTRL_VPP_REGULATOR_ENABLE` | rurp_pinout.h:95 | No |
| 0x100 | `CTRL_VPP_VPE_DROP_ENABLE` | rurp_pinout.h:96 | **Non-transmissible** (see below) |

Both layouts allocate every bit position **0x01 through 0x80** to a named, actively-used
`CTRL_*` function. There is no spare bit in the 8-bit-wide control register.

The `#define CTRL_ADDRESS_LINE_13 0x20` at `rurp_pinout.h:99` is annotated "reserved — no
current call-site" but it **collides** with `CTRL_ADDRESS_LINE_18` (also 0x20). It is a
documentation artifact, not a free bit — setting 0x20 drives A18, so it cannot be
repurposed for ALE.

### The 0x100 Bit Cannot Reach the 74HC573 (uint8_t-truncation argument)

The wide layout defines `CTRL_VPP_VPE_DROP_ENABLE = 0x100` (`rurp_pinout.h:96`). This looks
like a 9th control bit, but it can never be physically transmitted:

- `rurp_internal_write_to_register` (`rurp_register_utils.h:63–89`) pushes control data onto
  the shared bus via `rurp_write_data_buffer(data)` at `rurp_register_utils.h:83`.
- `rurp_write_data_buffer` is declared `void rurp_write_data_buffer(uint8_t data)`
  (`rurp_shield.h:113`). The parameter is `uint8_t`, so any value `> 0xFF` is truncated to
  8 bits before it ever reaches the 74HC573 — `0x100 & 0xFF == 0x00`.

So the "9th bit" is a logical flag the firmware special-cases elsewhere; it is **not** a
real, drivable hardware line that could be repurposed for ALE. A genuine 9th control bit
would require a second 74HC573 control latch and a new strobe — a PCB change. (See §6 A6
and the v1.7 Phase-33 0x01→0x100 relocation in the RESEARCH State-of-the-Art table.)

### 74HC573 Strobe Inventory — No Free Strobe for ALE

The RURP latches are strobed by the bit masks in `rurp_shield.h:53–57`:

| Strobe constant | Value | Function | Line |
|-----------------|-------|----------|------|
| `LEAST_SIGNIFICANT_BYTE` | 0x01 | LSB address latch | rurp_shield.h:53 |
| `MOST_SIGNIFICANT_BYTE` | 0x02 | MSB address latch | rurp_shield.h:54 |
| `OUTPUT_ENABLE` | 0x04 | Chip /OE | rurp_shield.h:55 |
| `CONTROL_REGISTER` | 0x08 | Control register latch | rurp_shield.h:56 |
| `CHIP_ENABLE` | 0x20 | Chip /CE | rurp_shield.h:57 |

`rurp_internal_write_to_register` (`rurp_register_utils.h:83–88`) writes by putting data on
the shared 8-bit data bus then pulsing exactly one strobe (`rurp_set_control_pin(reg, 1)`
HIGH, then LOW). This is a **shared-bus** architecture — only one latch is addressable at a
time, and all five strobes above are already assigned to existing functions. There is **no
unconnected strobe pin** available to clock an ALE latch without modifying the PCB.

### D-02 Deferral Bar Honored — No Speculative Reuse Adopted

No speculative reuse of a busy bit was adopted. The only superficially-tempting candidate is
`CTRL_VPP_REGULATOR_ENABLE` (0x80, `rurp_pinout.h:83/95`) — it is "idle" for a 5V chip in the
sense that the X88C64 uses no VPP. But pulsing it during an X88C64 write would briefly enable
the VPP boost regulator, producing an **undamped VPP spike at the socket** — a chip-damage
path on a 5V part. D-02 explicitly prohibits this class of creative multiplexing of a busy
line, and the address-line and R/W bits are actively used on every bus access. Per the D-02
bar, the verdict is therefore PCB-BLOCKED, not FREE-BIT-FOUND.

### Verdict Consequence

X88C64 stays `support_status: protocol-not-implemented` and host-refused. No `0x34` handler
is written this phase (Plan 02 reads this verdict and no-ops on the handler-write branch).
The future-unblock path is recorded in the FUT-01 spec below.

### FUT-01 Future-Unblock Spec (D-03)

`FUT-01` (REQUIREMENTS.md) stays OPEN. A future milestone that wants to drive the X88C64
ALE line needs **ONE** of the following hardware paths (the control register is full and the
strobe inventory is exhausted — see the verdict trace above):

1. **New shield revision (≥ Rev 2.4) with a 9th control bit.** Add a second 74HC573 control
   latch plus a dedicated Arduino GPIO strobe line so a genuine 9th control bit becomes
   physically drivable (the current `0x100` define is non-transmissible through the 8-bit
   `rurp_write_data_buffer` path). ALE would then be one bit on the new latch. This is the
   cleanest path and aligns with the existing `CTRL_*` model.

2. **Dedicated Arduino GPIO routed directly to socket pin 22 (ALE), bypassing the 74HC573.**
   Pick an Arduino GPIO that is currently unused on the shield and wire it straight to the
   X88C64 ALE pin (DIP socket pin 22), bit-banging ALE timing in firmware. Requires a board
   trace/mod to confirm a free GPIO reaches the socket without colliding with an existing
   signal.
   - `TODO:` Check the Leonardo ATmega32u4 GPIO-to-RURP-socket map (RESEARCH Open-Question 2)
     for a pin routed to the shield but currently unused, that could direct-drive ALE. This
     schematic review is out of scope for Phase 78's software trace and belongs to the future
     unblock milestone. The Uno (ATmega328P) socket map should be checked the same way if the
     unblock targets Uno-class boards.

3. **(NOT recommended) Idle-window reuse of `OUTPUT_ENABLE` or `CHIP_ENABLE` timing as a
   pseudo-ALE.** This is speculative multiplexing of a busy strobe and is barred by D-02
   absent a rigorous proof that the borrowed line is provably idle across the entire X88C64
   write window. Documented here only for completeness; do NOT pursue without that proof.

Once a hardware path exists and the A6 verdict can be re-opened as FREE/BIT-AVAILABLE, the
handler-write branch (D-05) delivers `configure_x88c64` (8051 multiplexed bus: ALE-latch →
/WR strobe, page write ≤ 32 B, I/O6 toggle-bit polling), modeled on `eeprom_28c.cpp`, plus a
Tier-1 native recording-stub test and the Leonardo flash-budget gate.

### Graduation Pending Hardware (SC#4 / XIC-04, D-04)

**Graduation pending hardware.** SC#4 / XIC-04 (graduate X88C64P to `supported` after an
N≥5 write + read-back SHA-match with a non-vacuous negative control) is **hardware-blocked
this phase** and is satisfied as a deferral-with-evidence, tracked under FUT-01.

- **Why blocked (D-04):** The operator has neither a physical X88C64P chip nor a DIP24→DIP32
  adapter, so no bench write/read-back cycle is possible regardless of the ALE verdict. (The
  PCB-BLOCKED A6 verdict is a second, independent blocker: with no ALE path, no handler can
  be written to bench at all.)
- **Status unchanged:** X88C64 stays `support_status: protocol-not-implemented` in
  `chip_database.json` and remains **host-refused** by `chip_resolver.resolve_chip`. No DB
  entry changes this phase.
- **Eventual bench graduation (tracked under FUT-01):** N≥5 write + read-back SHA-match +
  a non-vacuous negative control, **Leonardo only** (the v1.9 read bug corrupts the verify
  oracle on Rev-0/Rev-2.0; uno328pb is N/A for program/write per 999.2). Standing bench
  precondition: chip-OUT VPP multimeter dry-run first; ASK which silkscreen shield rev is
  mounted; live `r1 ≈ 270000` readback; verify the `controller:` port identity per task.
  Also requires the DIP24→DIP32 adapter (same adapter pattern as the AT28C04/AT28C16 work,
  Phase 80) and — per the A6 verdict — a hardware ALE path from the FUT-01 spec above.

### SAFE Invariants (SAFE-01/02/03) — Hold Trivially This Plan

This is a documentation-only plan; the safety invariants hold without action:

- **SAFE-01:** The `chip_resolver.resolve_chip` host-guard refusal is **NOT removed** this
  phase. Guard removal is the FINAL graduation step (D-04/D-05) and stays deferred under
  FUT-01.
- **SAFE-02:** No DB entry changes and no dispatch changes → `check_dispatch.py` is unaffected
  and stays green. 0x34 remains non-dispatchable.
- **SAFE-03:** No `FLAG_*` or protocol constant was touched, so the `constants.py` ↔
  `firestarter.h` parity is untouched — no lockstep change required.

### Plan 02 Branch Decision (Phase 78)

Plan 02's leading BLOCKING gate read the `A6 VERDICT: PCB-BLOCKED` line above and took the
DEFER branch (Branch A) — no `configure_x88c64` handler, no 0x34 dispatch arm, no
`test_val_x88c64` suite, no `DIP24_X88C64` pinout. X88C64 stays `protocol-not-implemented`
and host-refused; the host-guard is intact; graduation stays open under FUT-01.

Branch A — ALE PCB-blocked, no handler code; graduation deferred FUT-01.

## 7. Sources

| Source | Confidence | Notes |
|--------|-----------|-------|
| X88C64P datasheet pages 1–10 via alldatasheet.com/html-pdf/34232/XICOR/X88C64P | HIGH | Multiplexed-bus architecture confirmed across multiple pages; write protocol explicitly described; STORE/RECALL absent from all surveyed pages |
| Xicor 1985 Data Book via bitsavers.org/components/xicor/1985_Xicor_Data_Book.pdf | HIGH | Confirms NOVRAM family X2210/X2212 has STORE/RECALL; X88C64P not in this 1985 book (different product era) |
| `firestarter_app/firestarter/data/chip_database.json` — X88C64P entry | HIGH | Verified 2026-06-18: support_status=protocol-not-implemented, algorithm=0x34, pinout=DIP24_6116, unsupported_reason was the old misleading text [reworded by plan 76-01 to reflect parallel DIP24, 8051 multiplexed-bus, feasible-candidate] |
| `firestarter/src/proms/memory.cpp` lines 74–119 | HIGH | 0x34 has no dispatch arm; generic fail-closed guard at protocol!=0 catches it and returns MSG_ERR_PROTOCOL_NOT_IMPLEMENTED (0xBB) |
| `.planning/milestones/v1.13-PROTOCOL-ENUMERATION.md` row 0x34 | HIGH | Classification: feasible-gap (Phase 76 scope); DB support_status = protocol-not-implemented |
| `.planning/phases/76-spec-only-gaps-adapter-required-x88c64/76-CONTEXT.md` | HIGH | Locked decisions D-01 (no handler this phase), D-02 (unsupported_reason reword) |
