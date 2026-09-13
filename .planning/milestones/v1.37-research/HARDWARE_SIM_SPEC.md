# RURP Shield + Arduino — Hardware Simulation Spec

A self-contained behavioral spec for simulating the Firestarter EPROM programmer
hardware stack (Arduino Uno or Leonardo + RURP shield + DIP chip socket) at the
fidelity needed for: reasoning about timing / coupling bugs, validating firmware
edits without bench hardware, and cross-referencing pinouts, latch routing, and
the address-bus remapping pipeline end-to-end.

Sources used to build this spec (every claim should be traceable):
- `firestarter/src/boards/uno_rurp_shield.cpp`
- `firestarter/src/boards/leonardo_rurp_shield.cpp`
- `firestarter/src/boards/rurp_common.cpp`
- `firestarter/include/rurp_register_utils.h`
- `firestarter/include/rurp_shield.h`
- `firestarter/src/proms/memory.cpp`
- `firestarter/src/proms/flash_utils.cpp`
- `firestarter/include/firestarter.h`
- `firestarter_app/firestarter/data/pinouts.json`
- `firestarter_app/firestarter/database.py`
- `.planning/phases/04-hardware-validation-rurp-shield/04-HARDWARE-REFERENCE.md`
- Upstream Rev 2.3 schematic (see 04-HARDWARE-REFERENCE.md §SCHEMATIC ADDENDUM)

Things marked **(schematic-pending)** are claims I have not been able to verify
from firmware source alone and need to be cross-checked against the Rev 2.3 PCB
schematic before a simulator commits to them.

---

## 1. Top-level topology

```
  ┌──────────────┐         ┌──────────────────────────────────────────┐
  │              │ shield  │ RURP shield                              │
  │   Arduino    │ pins    │                                          │
  │  Uno or      │◄────────┤  ┌──── 74HC573 ──── ┐                    │
  │  Leonardo    │ D0..D7  │  │  U2  LSB latch  │──── A0..A7    ┌────┐│
  │              │ D8..D13 │  │  U3  MSB latch  │──── A8..A13   │DIP ││
  │  AVR @       │ A0..A5  │  │  U4  CTL latch  │──── ctl bits  │chip││
  │  16 MHz      │         │  └─────────────────┘               │skt ││
  │              │         │  + MIC2288 HV regulator             │    ││
  │              │         │  + BJT cascades (HV to socket)      │    ││
  └──────────────┘         │  + JP4/JP5/JP9 jumpers              └────┘│
                           └──────────────────────────────────────────┘
```

Three components:

1. **Arduino board** — Uno (ATmega328P) or Leonardo (ATmega32U4), both 16 MHz.
   Drives shield via 14 GPIOs (D0–D13) + 6 analog (A0–A5).
2. **RURP shield** — three 74HC573 transparent latches, MIC2288 HV regulator,
   BJT cascades for HV switching, chip socket.
3. **Chip socket** — 24/28/32-pin DIP, accepts EPROM/EEPROM/SRAM/FRAM/Flash.

Host PC ↔ Arduino via UART, 250000 baud, three-phase line-tagged protocol.

---

## 2. Arduino pin map (shield connector ↔ AVR port-bit)

The shield's connector exposes Arduino pins D0–D13 + A0–A5. Routing to the AVR
depends on the board.

### 2.1 Uno (ATmega328P)

| Shield pin | AVR | Role |
|---|---|---|
| D0  | PD0 | data D0 (also UART RX in comm mode) |
| D1  | PD1 | data D1 (also UART TX in comm mode) |
| D2  | PD2 | data D2 |
| D3  | PD3 | data D3 |
| D4  | PD4 | data D4 |
| D5  | PD5 | data D5 |
| D6  | **PD6** | data D6 ← shared with latch D6 inputs and chip socket D6 |
| D7  | PD7 | data D7 |
| D8  | PB0 | LSB latch LE strobe (RLSBLE) |
| D9  | PB1 | MSB latch LE strobe (RMSBLE) |
| D10 | PB2 | OE# direct control (~ROM_OE) |
| D11 | PB3 | CTL latch LE strobe (CTRL_LE) |
| D12 | PB4 | USER_BUTTON (input, pull-up) |
| D13 | PB5 | CE# direct control (~ROM_CE) |
| A0  | PC0 | (spare — SERIAL_DEBUG RX when `SERIAL_DEBUG`) |
| A1  | PC1 | (spare — SERIAL_DEBUG TX) |
| A2  | PC2 | VPP voltage sense (`VOLTAGE_MEASURE_PIN`) |
| A3  | PC3 | hardware revision detect |

Critical property: **all 8 data lines D0–D7 sit on PORTD as bits 0–7**. A single
`PORTD = value` writes all 8 in one AVR clock cycle.

### 2.2 Leonardo (ATmega32U4)

Data bus is **scattered** to avoid using PD0/PD1 (which are the UART pins on
Leonardo, identical to TX/RX on the connector — but the *USB* CDC is the actual
serial channel, leaving PD0/PD1 free for data). The data mapping
(verified against `rurp_write_data_buffer` body, lines 97–110):

| Chip data line | Shield pin | AVR port-bit |
|---|---|---|
| D0 | Shield D0 | PD2 |
| D1 | Shield D1 | PD3 |
| D2 | Shield D2 | PD1 |
| D3 | Shield D3 | PD0 |
| D4 | Shield D4 | PD4 |
| D5 | Shield D5 | PC6 |
| D6 | Shield D6 | **PD7** ← NOT PD6 |
| D7 | Shield D7 | PE6 |

Masks: `PORTD_DATA_MASK = 0x9F`, `PORTC_DATA_MASK = 0x40`, `PORTE_DATA_MASK = 0x40`.

> Note: the header comment block at `leonardo_rurp_shield.cpp:18` reads
> `D7(PD7)` — this is **misleading**. The authoritative mapping is the code
> body at lines 97–110: chip data D6 → AVR PD7, chip data D7 → AVR PE6.

Control pins on Leonardo (`rurp_set_control_pin` body, lines 48–74):

| Logical control bit | Shield pin | AVR |
|---|---|---|
| LSB strobe (0x01) | D8  | PB4 |
| MSB strobe (0x02) | D9  | PB5 |
| OE# (0x04)        | D10 | PB6 |
| CTL strobe (0x08) | D11 | PB7 |
| (unused 0x10)     | D12 | PD6 |
| CE# (0x20)        | D13 | PC7 |

Leonardo has **no USER_BUTTON** (per `leonardo_rurp_shield.cpp:78`); PD6 on
Leonardo is reserved as an unused control output (`PORTD_CONTROL_MASK = 0x40`).

### 2.3 Why this asymmetry matters

When the firmware does `PORTD = msb` on Uno, **eight bits change in one cycle**,
including PD6 which simultaneously drives:
1. Latch chip's D6 input on all three 74HC573s.
2. Chip socket's D6 data line.

On Leonardo, the chip's D6 line is driven via PD7 (different AVR pin), and the
update happens via read-modify-write to PORTD (multi-instruction). The latch
LE strobe sits on PORTB (or PORTC for CE#) — physically and temporally
separated from the data-bus transitions. **This natural separation makes
Leonardo behave like an always-on "Variant B" w.r.t. PD6/CE coupling** — and
may be the reason the FM1608 corruption bug is Uno-only.

---

## 3. The three 74HC573 latches

All three latches share the shield connector pins D0–D7 as their D-input bus.
Different LE strobes select which latch captures.

### 3.1 74HC573 behavior (datasheet summary)

- LE = HIGH: latch is **transparent** — Q outputs follow D inputs after a
  small propagation delay (~10–20 ns).
- LE = LOW: latch **holds** — Q outputs stay at the value sampled at the most
  recent LE falling edge.
- D-input changes while LE = LOW do **not** affect Q outputs (this is the
  datasheet-stated behavior; if there's an undocumented LE-rising glitch,
  it's a candidate for the bug-mechanism theory list).

### 3.2 Latch identity and routing

| Latch | LE strobe | Q outputs → chip socket |
|---|---|---|
| **U2 LSB** | shield D8 (Uno PB0, Leo PB4) | A0–A7 (via pinout-specific routing) |
| **U3 MSB** | shield D9 (Uno PB1, Leo PB5) | A8–A13, Q6 = **R/W to socket pin 27** for 28-pin JEDEC SRAM/EEPROM/FRAM, Q7 = A15 or unused |
| **U4 CTL** | shield D11 (Uno PB3, Leo PB7) | control signals (see §4 CTL Q layout) |

(MSB Q6 → socket pin 27 routing is the load-bearing fact behind the FM1608
bug; see §10. **schematic-pending** for whether socket pin 27 has any other
driver path.)

### 3.3 Strobe sequence (timing)

`rurp_internal_write_to_register(reg, data)` in `rurp_register_utils.h:62–87`:

```
1. PORTD = data                                  [Uno: 1 cycle, 62.5 ns]
   (Leonardo: 3-port RMW, ~10 cycles, ~625 ns)
2. PORTB |= reg  (LE rises)                      [2 cycles, ~125 ns after step 1 on Uno]
3. delayMicroseconds(1)                          [16 cycles, 1 µs]
4. PORTB &= ~reg (LE falls — latch captures)     [2 cycles, ~125 ns]
```

On Uno the PORTD update and LE-rise are spaced by only ~125 ns. On Leonardo the
spacing is naturally ~625 ns + the RMW overhead. **Variant B of the FM1608
fix** explicitly inserts `delayMicroseconds(N)` between step 1 and step 2 on
Uno to make its timing more Leonardo-like.

### 3.4 Cache layer

File-scope statics in `rurp_register_utils.h:11–13`:
```c
uint8_t lsb_address = 0xff;
uint8_t msb_address = 0xff;
rurp_register_t control_register = 0xff;
```

`rurp_write_to_register(reg, data)` (lines 23–59): if `data == cache[reg]`,
skip the strobe entirely. The cache is **never reset** across commands within
one Arduino session — it persists from session boot to power-off.

Initial values are `0xFF` per latch — see §10 for why this matters for
read-after-write transitions.

---

## 4. CTL latch Q-output semantics

Each of CTL's 8 Q outputs controls a specific shield function (mapping per
`rurp_shield.h:25–33`, `04-HARDWARE-REFERENCE.md` §2.1):

| CTL bit | Mask | Q output controls |
|---|---|---|
| 0 | 0x01 `VPE_TO_VPP` | Switches HV regulator feedback divider (22.5 V → 12 V) |
| 1 | 0x02 `A9_VPP_ENABLE` | Routes HV to socket pin 26 (A9) via BJT + D34 |
| 2 | 0x04 `VPE_ENABLE` | Routes HV to socket pin 31 (PGM/VPE) via BJT + D11 |
| 3 | 0x08 `P1_VPP_ENABLE` | Routes HV to socket pin 1 (when JP4 closed) |
| 4 | 0x10 `ADDRESS_LINE_17` | Address line A17 (28-pin chips) |
| 5 | 0x20 `ADDRESS_LINE_18` | Address line A18 (32-pin chips, Rev 0/1) |
| 6 | 0x40 `READ_WRITE` | **R/W control line** for flash chips that toggle via CTL — **schematic-pending: where does CTL Q6 physically connect on the socket?** |
| 7 | 0x80 `REGULATOR` | Enables MIC2288 HV regulator (active-high; gated via JP9) |

**Hardware Rev 2.x remapping** (`rurp_hw_rev_utils.h:14–36`):
- `VPE_TO_VPP` moves to a separate "9th bit" (extended CTL register width).
- `ADDRESS_LINE_16` and `ADDRESS_LINE_18` swap bit positions vs Rev 0/1.
- Firmware translates logical bits → physical bits before writing.

**Status of `READ_WRITE` (CTL bit 6)**: it is defined as a CTL bit and
`flash_utils.cpp:22,26,31` toggles it via `firestarter_set_control_register`,
but the destination chip-socket pin is **not documented in firmware comments
or the reference doc**. If CTL Q6 reaches socket pin 27 on the same physical
trace as MSB Q6, then both latches can drive the same wire (a hazard). If CTL
Q6 has its own trace to a different socket pin, then fix #2 for the FM1608 bug
(re-route 28-pin R/W from MSB-bit-6 to CTL-bit-6) needs additional shield
wiring. **Resolve this from the Rev 2.3 PCB schematic before committing to
fix #2.**

---

## 5. MSB latch Q-output semantics

Reconstructed from `mem_util_remap_address_bus` + pinouts.json + database.py
pin_conversions (`04-HARDWARE-REFERENCE.md` §1.2):

| MSB bit | Q output → |
|---|---|
| 0 | A8 |
| 1 | A9 (merges with `A9_VPP_ENABLE` for chip-ID — convergence point **schematic-pending**) |
| 2 | A10 |
| 3 | A11 |
| 4 | A12 |
| 5 | A13 |
| 6 | **R/W on chip socket pin 27** (used by DIP28_JEDEC_SRAM_8K, DIP28_28C64, DIP28_28C256 pinouts) |
| 7 | A15 (or unused on 28-pin) |

Critical: PORTD bit 6 directly drives MSB latch D6 input AND chip socket data
line D6 (via the shared shield D6 connector pin). When the firmware writes
`PORTD = 0x40` for an MSB strobe in read mode, PD6 carries logic 1 on
**both** wires simultaneously.

---

## 6. LSB latch Q-output semantics

LSB Q0–Q7 map to chip socket A0–A7 directly (modulo pinout-specific
reordering via `bus_config.address_lines[]`).

---

## 7. Direct AVR-driven control signals

CE# and OE# are driven directly by AVR GPIO via a buffer chain — they do
**not** pass through any of the three latches.

| Signal | Uno AVR | Leonardo AVR | Direction | Function |
|---|---|---|---|---|
| `CHIP_ENABLE` (0x20) | PB5 | PC7 | AVR → shield | CE# active-low |
| `OUTPUT_ENABLE` (0x04) | PB2 | PB6 | AVR → shield | OE# active-low |

Convenience macros (`rurp_shield.h:129–141`):
- `rurp_chip_enable()` → `rurp_set_control_pin(CHIP_ENABLE, 0)` → CE# LOW
- `rurp_chip_disable()` → CE# HIGH
- `rurp_chip_output()` → OE# LOW (chip drives bus)
- `rurp_chip_input()` → OE# HIGH (chip releases bus)

---

## 8. Address-bus remapping pipeline (host → reorg_address → latches)

### 8.1 Host side (Python)

Each chip's pinout (`pinouts.json`) lists physical chip-socket-pin numbers for
each role: `address-bus-pins`, `data-bus-pins`, `ce-pin`, `oe-pin`, `rw-pin`,
`vpp-pin`, `vcc-pin`, `gnd-pin`, `nc-pin`, `static-high-pins`.

`database.py:pin_conversions` table maps `(pin_count, chip_pin)` →
`bus_index` (= reorg_address bit position). Per pin count the table has the
shield-static wiring of socket-pin to bus-index.

The host emits a `bus-config` JSON object with computed bus indices for each
role, plus an `address_lines` array describing the chip's logical-bit-to-
physical-bus-bit remapping.

### 8.2 Firmware side (memory.cpp:230–249)

```c
uint32_t mem_util_remap_address_bus(handle, address, read_write):
    reorg_address = config.address_mask & address           // strip out-of-range bits
    for each address_line in config.address_lines[]:        // per-pinout bit reorder
        if address & (1 << i): reorg_address |= (1 << config.address_lines[i])
    if config.rw_line != 0xFF:                              // R/W routing
        reorg_address |= (read_write << config.rw_line)
    if config.vpp_line != 0xFF and not using_p1_as_vpp(handle):  // VPP routing
        reorg_address |= (1 << config.vpp_line)
    reorg_address |= config.static_high_mask                // forced-HIGH lines
    return reorg_address
```

Where `read_write = 0` for `WRITE_FLAG`, `read_write = 1` for `READ_FLAG`.

### 8.3 Bit decoding

The 32-bit `reorg_address` decodes into the three latches:

| reorg_address bits | latch |
|---|---|
| 0–7 | LSB latch D-input |
| 8–15 | MSB latch D-input |
| 16–23 | CTL latch D-input (masked to bits 16,17,18,22 per `mem_util_calculate_top_address_register`) |

`mem_util_calculate_top_address_register` (memory.cpp:137–151):
```c
top_address = (address >> 16) & (ADDRESS_LINE_16 | ADDRESS_LINE_17 | ADDRESS_LINE_18 | READ_WRITE)
top_address |= cached_control_register & preservation_mask   // keep VPP enables across
top_address |= (handle->pins == 28 ? ADDRESS_LINE_17 : 0)    // 28-pin chips force A17
```

Concretely, for a 28-pin SRAM/FRAM with `rw_line=14` (MSB bit 6) reading at
address 0:
- `reorg_address = 0 | (1 << 14) = 0x4000`
- LSB byte = 0x00 ; MSB byte = 0x40 (bit 6 HIGH for read) ; CTL byte = 0x10 (`ADDRESS_LINE_17`).

For the same address in write mode (`read_write = 0`):
- `reorg_address = 0`
- LSB byte = 0 ; MSB byte = 0 ; CTL byte = 0x10.

---

## 9. Per-operation behavior

### 9.1 `memory_get_data(address)` — read one byte (memory.cpp:185–194)

```
rurp_chip_output()                          # OE# LOW (chip drives data bus when CE# also LOW)
reorg = mem_util_remap_address_bus(address, READ_FLAG)
firestarter_set_address(reorg):             # mem_util_set_address by default
    rurp_write_to_register(LSB, lsb byte)   # strobe if cache miss
    rurp_write_to_register(MSB, msb byte)   # strobe if cache miss
    rurp_write_to_register(CTL, ctl byte)   # strobe if cache miss
rurp_set_data_input()                       # PORTD = 0, DDRD = 0 (Uno); DDR-only (Leonardo)
rurp_chip_enable()                          # CE# LOW
delayMicroseconds(3)
data = rurp_read_data_buffer()              # read PIND (Uno) or assembled scatter (Leonardo)
rurp_chip_disable()                         # CE# HIGH
return data
```

### 9.2 `memory_set_data(address, data)` — write one byte (memory.cpp:206–212)

```
rurp_chip_input()                           # OE# HIGH (chip releases bus)
reorg = mem_util_remap_address_bus(address, WRITE_FLAG)
firestarter_set_address(reorg)
rurp_write_data_buffer(data)                # DDRD = 0xff, PORTD = data (Uno) or scatter (Leonardo)
delayMicroseconds(3)                        # address settle for "Power through address" pinouts
rurp_chip_enable()                          # CE# LOW
delayMicroseconds(handle->pulse_delay)      # 0 µs for SRAM/FRAM, hundreds for EPROM
rurp_chip_disable()                         # CE# HIGH (chip captures address+data on CE rising for SRAM)
```

### 9.3 Bulk read/write loop

`memory_read_execute` and `memory_write_execute` iterate `memory_get_data` /
`memory_set_data` over a chunk of bytes (512 Uno, 1024 Leonardo per chunk).
Each byte's address-strobe sequence is cache-aware — only LSB strobes on every
byte; MSB strobes only every 256 bytes; CTL strobes only when one of its bits
changes (which is rare during a flat sweep).

---

## 10. Cache state and read-after-write transitions

After a write session of an 8 KB chip, the cache holds:
- `lsb_address` = lsb of last byte written (e.g., 0xFF for last byte at 0x1FFF)
- `msb_address` = msb of last byte written with rw_line=14 in WRITE mode (bit 6 LOW), e.g., 0x1F
- `control_register` = whatever CTL was set to (e.g., 0x10 for 28-pin)

When a new READ command starts:
1. `configure_memory` calls `mem_util_set_address(handle, 0)`:
   - LSB write 0: cache miss (was 0xFF) → strobe (PORTD bit 6 may transition either way depending on prior lsb).
   - MSB write 0: cache miss (was 0x1F) → strobe with PORTD = 0 (bit 6 LOW).
   - CTL write 0x10: cache hit (assuming same pinout) → no strobe.
2. `memory_read_execute` starts iterating addresses 0, 1, 2, ...
3. For byte 0: reorg = 0x4000 → msb byte = 0x40.
   - LSB write 0: cache hit → no strobe.
   - MSB write 0x40: cache miss (was 0) → **strobe**, PORTD goes 0 → 0x40, **PD6 rises**.
   - CTL hit.
4. For bytes 1–255: only LSB strobes; MSB stays cached at 0x40.
5. For byte 256: LSB transitions 0xFF → 0x00 (strobe); MSB transitions 0x40 →
   0x41 (strobe, **but PD6 stays HIGH because both have bit 6 set**).

**However**: `rurp_set_data_input` between byte reads sets `PORTD = 0` on Uno
(per `uno_rurp_shield.cpp:130`). So **the next strobe sequence starts with
PORTD = 0 every time**. For byte 256:
- LSB strobe sets PORTD = 0 (cache miss from 0xFF, but new value also 0): if
  bit 6 of the **prior** PORTD (0xFF) was HIGH, then PORTD = 0 produces a PD6
  falling edge.
- MSB strobe sets PORTD = 0x41: **PD6 rises LOW → HIGH** (because PORTD was
  just reset to 0 by the LSB strobe, even though PD6 = 1 in the latched MSB
  value).

→ **Every 256-byte boundary in a read sweep has a fresh PD6 rising edge during
the MSB strobe.** This is what makes the FM1608 corruption pattern have 32
events for an 8 KB chip, not just 1.

(On Leonardo, the same logic applies but PD7 — not PD6 — sees the rising edge,
and PD7 doesn't share an AVR-side environment with the latch LE strobes.)

---

## 11. Three-phase serial protocol

UART @ 250000 baud. Commands are JSON; responses are line-tagged ASCII with
binary payloads for data transfer.

| Phase | Direction | Content |
|---|---|---|
| **INIT** | host → fw  | `{cmd: N, type, algorithm, pin-count, vpp_mv, pulse-delay, chip-id, bus-config, flags}` JSON |
|       | fw → host    | `OK: <message>` after `configure_memory` succeeds; `ERROR: ...` otherwise |
| **MAIN** | (push for READ; pull for WRITE) | |
|       | READ fw → host | `DATA: <length>\n<binary>` per chunk; host ACKs each |
|       | WRITE fw → host | `OK: Req data` per chunk; host sends `{cmd: N, data: "<base64>"}` JSON |
|       | terminator | fw sends `MAIN:` line to signal end-of-main-phase |
| **END** | fw → host | `END:` + cleanup messages |

Tagged prefixes: `OK:`, `DATA:`, `MAIN:`, `END:`, `ERROR:`, `WARNING:`, `INFO:`, `DEBUG:`.

Command codes (`firestarter.h`):
- `CMD_READ = 1`, `CMD_WRITE = 2`, `CMD_VERIFY = 3`, `CMD_ERASE = 4`,
  `CMD_BLANK_CHECK = 5`, `CMD_CHECK_CHIP_ID = 6`, `CMD_CONFIG = 7`, ...

`configure_memory()` runs **exactly once per command** at the top of the INIT
phase. The latch cache persists across commands within a single Arduino
session (i.e., between successive `firestarter write` then `firestarter read`
invocations the cache survives — the Arduino doesn't reboot).

---

## 12. Algorithm dispatch (`memory.cpp:44–117`)

`configure_memory` switches on `handle->protocol`:

| Protocol | Handler | VPP | Notes |
|---|---|---|---|
| 0x10 | `configure_flash_intel` | 12 V | Intel 28F command-register flash |
| 0x0D | `configure_eeprom28c` | none | AT28C-series 5V EEPROM with page write |
| 0x06 | `configure_flash3` | none | AMD unlock flash (sector erase) |
| 0x05/0x35/0x39 | `configure_flash4` | none | page-write flash |
| 0x07/0x08/0x0B | `configure_eprom` | 13–18 V | UV EPROM |
| 0x0E/0x27/0x28/0x29 | `configure_sram` | none | SRAM/NVRAM (defaults only) |
| else | `mem_type` fallback chain | | backward-compat |

Each handler may override `firestarter_operation_init`, `_main`, `_end`,
`firestarter_set_data`, `firestarter_get_data`. SRAM uses unmodified defaults
from `memory.cpp`.

---

## 13. Timing constants in the firmware

| Location | Delay | Purpose |
|---|---|---|
| `rurp_internal_write_to_register` LE pulse | 1 µs (`delayMicroseconds(1)`) | Latch capture window |
| `memory_set_data` post-strobe | 3 µs | Address-line settle (e.g., Power-through-address) |
| `memory_get_data` post-CE-enable | 3 µs | Chip access time (FM1608 = 120 ns; UV EPROM = 200–450 ns) |
| `rurp_write_to_register` CTL settle (when clearing P1_VPP_ENABLE) | 4 µs | VPP voltage discharge |
| `pulse_delay` per chip | 0–1000 µs | Write pulse width (0 for SRAM, 100–1000 for EPROM) |
| `rurp_serial_end` (Uno) | 5 ms | UART teardown before programmer mode |

---

## 14. Known electrical anomalies (Uno-specific)

### 14.1 FM1608 / 28-pin JEDEC SRAM byte-0 + 256-byte-boundary corruption

See `.planning/debug/fm1608-fresh-chip-baseline.md`. Symptom: writing an 8 KB
random pattern to an FM1608 then reading it back on Uno yields:
- Byte 0 reads as `0xFF` regardless of the value written (Uno self-read).
- 32 bytes at every 256-byte boundary (0, 256, …, 7936) hold `0x40 | i` for
  i ∈ 0..31 (confirmed via cross-board Leonardo cross-read).

Mechanism (provisional): some coupling path between PORTD bit 6 transitions
(during MSB strobes for read mode) and the chip's /CE pin causes the chip to
capture AVR's PORTD value at the LSB-latched address. PD6 shares with the
chip's D6 data line on Uno; on Leonardo the chip D6 is on PD7 and the bug
doesn't manifest.

Two firmware-side mitigations are currently coded (`rurp_register_utils.h`):
- **Variant A** (always-on for Uno): pre-clear `PORTD = 0` + 4 NOPs before the
  MSB-strobe data write — moves PD6's rising edge to a quieter window before
  the LE strobe.
- **Variant B** (opt-in via `-D FM1608_FIX_LE_DELAY_US=N` in `platformio.ini`):
  also insert `delayMicroseconds(N)` between the PORTD update and LE rising.

Both await bench validation. If neither works, fix #2 is to route R/W via
CTL Q6 instead of MSB Q6 (resolves PD6/D6 coincidence by removing R/W from
the MSB strobe path), pending schematic confirmation that CTL Q6 reaches a
socket pin that can serve as R/W for 28-pin chips.

### 14.2 UART RX false-start glitch

PD0 doubles as UART RX. Transitioning programmer-mode → comm-mode
(`Serial.begin → RXEN0=1`) with PD0 LOW makes the UART hardware sample a
false start bit, queuing spurious bytes that corrupt the host's `OK:`
response. Fix: drive PD0 HIGH before clearing DDRD bit 0; drain any RX bytes
after `Serial.begin`. See `uno_rurp_shield.cpp:51–73`.

### 14.3 Data-input pull-up bias

`rurp_set_data_input` on Uno explicitly sets `PORTD = 0` before `DDRD = 0` to
disable the internal pull-up bias that would otherwise weakly drive HIGH
against the chip's drive. Defensive but does **not** fix the FM1608 bug on
its own. See `uno_rurp_shield.cpp:123–140`.

---

## 15. Simulation guidance

For a software simulator (Python, SimAVR + custom shield model, or any
discrete-event sim):

### 15.1 Modeling building blocks

- **AVR ports**: PORTA/B/C/D/E with `DDR`, `PORT`, `PIN` registers per AVR
  model. PORTD on Uno is 8-bit; same on Leonardo. Operations:
  - `PORT = value` ← single-write, all 8 bits update simultaneously.
  - `PORT |= mask`, `PORT &= ~mask` ← read-modify-write, multi-cycle.
  - `DDR = 0xff` → output; `DDR = 0x00` → input (Hi-Z + optional pull-up via PORT).
- **74HC573 latch**: ports `D[7:0]`, `LE`, `OE'`, `Q[7:0]`. State = last-
  latched value, updated on LE falling edge OR following D when LE = HIGH.
- **Multi-driver nodes**: shield D0–D7 wires have three drivers — AVR (when
  in output mode), chip (when CE# LOW and OE# LOW), and the latch D-inputs
  (always sampling). For coupling/contention analysis, model each
  driver's output state per simulation step.
- **Chip socket**: per-chip behavioral model. For SRAM/FRAM: respond to
  CE# falling edge by reading address-latched location into the data bus
  (read mode, /WE HIGH) or capturing the data bus to address-latched
  location (write mode, /WE LOW). For EPROM: similar but read-only with
  per-chip access time.
- **HV regulator**: state machine on REGULATOR + VPE_TO_VPP bits; output
  voltage profile per the MIC2288 datasheet (rise/fall time, ripple).

### 15.2 Cycle-accuracy

For the FM1608 mechanism investigation, the simulator needs to model AVR
instructions at single-cycle (62.5 ns) granularity. Critical timing:
- `PORTD = data` is 1 cycle (1 µs/16 = 62.5 ns) on Uno.
- `PORTB |= reg` is 2 cycles (in/or/out sequence) = 125 ns on Uno.
- LE pulse width = 1 µs (16 cycles).
- LSB+MSB+CTL strobe block takes ~3 µs minimum per address.

For Leonardo, the data-bus write is a 3-port read-modify-write sequence
totaling ~10 cycles (625 ns).

### 15.3 Coupling model (for FM1608 hypothesis testing)

Add a configurable coupling parameter between PD6 and the chip's /CE pin:
- **dV/dt threshold**: AVR pin rising edge faster than ~2 V/ns triggers a
  coupling event.
- **Pulse width**: how long /CE is held LOW by the coupling event (model
  parameter; ~5–20 ns is plausible for capacitive coupling between adjacent
  PCB traces).
- **Trigger criteria**: PD6 rising edge AND (LE strobe within ±X ns OR
  arbitrary).

The simulator then predicts whether each MSB strobe in a read sweep induces
a spurious write at the LSB-latched address. Compare predicted corruption
pattern against bench observation (`chip[i*256] = 0x40 | i` for i=0..31).

### 15.4 Boundary conditions to model

- Cache state at session boot: `lsb=0xFF, msb=0xFF, ctl=0xFF`.
- Cache state mid-session: whatever last strobed value was.
- Cache state after `configure_memory`: lsb/msb forced to 0, ctl forced to
  pinout-specific value (e.g., 0x10 for 28-pin chips).

### 15.5 Validation harness

Once the simulator runs, a useful regression suite:
- Match the bench observation for FM1608 byte-0 + 256-byte-boundary corruption
  (32 corrupted bytes with pattern `0x40 | i`).
- Predict corruption for other 28-pin chips with `rw_line=14`: DIP28_28C64,
  DIP28_28C256. (Bench-untested; should exhibit similar symptoms on Uno.)
- Confirm Leonardo simulation predicts no corruption.
- Confirm Variant A and Variant B firmware predict no corruption.

---

## 16. Open questions for the simulator author

1. **Where does CTL Q6 (`READ_WRITE`) physically connect on the chip socket?**
   This determines whether fix #2 (route R/W via CTL) is firmware-only or
   needs shield wiring. (§4)
2. **What's the actual PD6→/CE coupling pathway?** Is it PCB-trace
   capacitance on the shield, AVR-internal ground bounce, or LE-strobe-
   induced rail disturbance? Each implies a different mitigation. (§14.1)
3. **Does the 74HC573 have an undocumented LE-rising glitch?** If Q output
   briefly drops on LE-rising (even when D=Q already), that would create
   the WE-LOW window needed for the FM1608 mechanism on the 31 follow-up
   strobes (where the latch's bit 6 was already HIGH from prior reads).
4. **Is the MSB Q6 trace physically adjacent to the CE# trace on the shield
   PCB?** If yes, the coupling story holds. If not, the mechanism is
   somewhere else.
5. **What's the actual rise/fall time of AVR PORTD pins driving 5 V CMOS
   loads?** This bounds the maximum di/dt and constrains the coupling
   model in §15.3.

---

## 17. Reference: pinouts with `rw-pin` (active R/W routing)

| Pinout | Pin count | R/W chip pin | rw_line (bus index) | Affected chips |
|---|---|---|---|---|
| `DIP28_JEDEC_SRAM_8K` | 28 | 27 | 14 (MSB Q6) | FM1608 (8 KB FRAM), 6264 family |
| `DIP28_28C64` | 28 | 27 | 14 (MSB Q6) | AT28C64, HN58C256, etc. |
| `DIP28_28C256` | 28 | 27 | 14 (MSB Q6) | AT28C256, HN58C256AP, etc. |
| `DIP24_6116` | 24 | 21 | (different — 24-pin alignment) | 6116-class 2 KB SRAM |
| `DIP32_28C512_EEPROM` | 32 | 30 | (32-pin alignment) | 28C512 family |
| `DIP32_SST39SF040` | 32 | 31 | (32-pin alignment) | SST39SF040 flash |

The first three (28-pin with rw_line=14, i.e., MSB Q6) are all candidates for
the FM1608-style corruption bug on Uno. Bench-validating only one (FM1608) is
sufficient to confirm the family is affected, but a regression test sweep is
recommended after either fix lands.

---

*End of spec.* When the shield schematic clarifies the **schematic-pending**
points, update §4, §5.1 (the A9 merge convergence point), and §16.
