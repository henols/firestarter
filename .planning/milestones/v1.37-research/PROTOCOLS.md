# Protocol ID Research: RURP + Firestarter Implementation Guide

This document covers the programming protocols used in minipro's `infoic.xml` chip database,
specifically for DIP 24/28/32 parallel memory devices. It maps protocol IDs to real hardware
behaviour, timing requirements, and the Firestarter firmware architecture.

---

## 1. RURP Hardware Summary

### Physical Architecture
The RURP (Relatively Universal ROM Programmer) is an Arduino shield providing:
- **Data bus**: 8 bits (D0–D7) — Arduino Uno PORTD
- **Address bus**: up to 23 lines (A0–A22) — driven via three 8-bit shift registers
- **Control signals**: CE (Chip Enable), OE (Output Enable), VPE/VPP enable
- **VPP/VPE generation**: Adjustable boost regulator, trimpot-calibrated, 5V–27V range
- **Voltage feedback**: Voltage divider on A2 for reading VPP/VPE in millivolts (Rev 1+)

### Shift Register Layout (3 × 8-bit registers)

| Register      | Firmware Constant       | Content                                       |
|---------------|-------------------------|-----------------------------------------------|
| LSB           | `LEAST_SIGNIFICANT_BYTE`| Address A0–A7                                 |
| MSB           | `MOST_SIGNIFICANT_BYTE` | Address A8–A15 (bit 5 = A13 for 24-pin mode)  |
| Control       | `CONTROL_REGISTER`      | A16–A18, VPP enables, R/W, regulator          |

### Control Register Bit Definitions (Rev 2.x)

| Bit Mask      | Constant          | Function                                              |
|---------------|-------------------|-------------------------------------------------------|
| `0x01`        | `ADDRESS_LINE_16` | A16 address line                                      |
| `0x02`        | `A9_VPP_ENABLE`   | Route VPP to A9 pin (EPROM ID mode or 24-pin erasure) |
| `0x04`        | `VPE_ENABLE`      | Apply VPE (high voltage) to the programming pin       |
| `0x08`        | `P1_VPP_ENABLE`   | Route VPP to pin 1 of the DIP socket                 |
| `0x10`        | `ADDRESS_LINE_17` | A17 address line                                      |
| `0x20`        | `ADDRESS_LINE_18` | A18 address line                                      |
| `0x40`        | `READ_WRITE`      | R/W line (also serves as A16 in some chip variants)   |
| `0x80`        | `REGULATOR`       | Enable VPP boost regulator                            |
| `0x100`       | `VPE_TO_VPP`      | Drop VPE through resistor to produce VPP (Rev 2+)     |

**Note on VPE vs VPP**: The regulator produces VPE (typically ~2 V higher than the required VPP).
Setting `VPE_TO_VPP` (Rev 2+) routes VPE through a resistor divider to drop it to VPP.
Setting `VPE_ENABLE` without `VPE_TO_VPP` applies the full VPE voltage directly.

### VPP Voltage Capability
- **Range**: 5V–27V, manually trimmed with a trimpot
- **Readable**: Via voltage divider + ADC on pin A2 (Rev 1 and later)
- **BJT Drivers**: Handle routing high voltage to the relevant pins without destroying the Arduino

### Pin Routing for Chip Sizes (Rev 2.x)
Rev 2 uses transistor drivers to automatically route VCC or address lines to the physical socket
pins depending on package size (24, 28, 32). The firmware communicates the `pin-count` field and
the hardware performs the routing. No physical jumpers required (except JP4 for VPP on pin 1 of
certain 28-pin chips, which must be removed for 32-pin chips).

---

## 2. Firestarter Firmware Memory Type Dispatch

The Firestarter app (`database.py`) maps protocol IDs to a `mem_type` integer passed to the
firmware. The firmware dispatches on `mem_type` in `memory.cpp`:

| `mem_type` | Firmware Constant    | Handler                  | Description                              |
|------------|----------------------|--------------------------|------------------------------------------|
| 1          | `TYPE_EPROM`         | `configure_eprom()`      | EPROM / EEPROM high-voltage pulse write  |
| 2          | `TYPE_FLASH_TYPE_2`  | *(not implemented)*      | Flash with EEPROM-like write (5V, page)  |
| 3          | `TYPE_FLASH_TYPE_3`  | `configure_flash3()`     | AMD-style flash (unlock + DQ7 poll)      |
| 4          | `TYPE_SRAM`          | `configure_sram()`       | SRAM (simple read/write, no protocol)    |
| 5          | `TYPE_FLASH_TYPE_4`  | `configure_flash4()`     | Flash/EEPROM with page write + DQ7 poll  |

### PROTOCOL_MAP (from `database.py`)

```python
PROTOCOL_MAP = {
    0x05: "FLASH_AMD_STD",
    0x06: "FLASH_AMD_ALT",
    0x07: "EPROM_STD",
    0x08: "EPROM_QUICK",
    0x0B: "EPROM_LEGACY",
    0x0D: "EEPROM_POLL",
    0x10: "FLASH_INTEL",
    0x28: "SRAM_STD",
}
```

The `types` dict maps to `mem_type` values:
- `"memory"` (0x01) → EPROM/EEPROM class; dispatch depends on protocol_id
- `"flash"` (0x03) → Flash class
- `"sram"` (0x04) → always `mem_type=4`

---

## 3. Protocol ID Reference Table (from Firestarter database)

| Protocol ID | Name            | Chip Count | Package | VPP Range     | mem_type | Status in Firestarter |
|-------------|-----------------|------------|---------|---------------|----------|-----------------------|
| `0x05`      | FLASH_AMD_STD   | 27         | 32-pin  | None or 12V   | 5        | Implemented (flash4)  |
| `0x06`      | FLASH_AMD_ALT   | 190        | 32-pin  | None (12V listed) | 3    | Implemented (flash3)  |
| `0x07`      | EPROM_STD       | 237        | 28-pin  | 12–13V        | 1        | Implemented           |
| `0x08`      | EPROM_QUICK     | 127        | 32-pin  | 12–13V        | 1        | Implemented           |
| `0x0B`      | EPROM_LEGACY    | 53         | 24-pin  | 12–18V        | 1        | Implemented           |
| `0x0D`      | EEPROM_POLL     | 18         | 32-pin  | None or 12V   | 1        | Partial (no DQ7 loop) |
| `0x0E`      | SRAM_32PIN      | 20         | 32-pin  | None / 12V    | 4        | Implemented           |
| `0x10`      | FLASH_INTEL     | 39         | 32-pin  | 12V mandatory | 1 (*)    | NOT implemented       |
| `0x27`      | SRAM_24PIN      | 2          | 24-pin  | None          | 4        | Implemented           |
| `0x28`      | SRAM_STD        | 10         | 28-pin  | None / 12V    | 4        | Implemented           |
| `0x29`      | SRAM_512K_1M    | 20         | 32-pin  | None / 12V    | 4        | Implemented           |
| `0x35`      | FLASH_EEPROM_LIKE| ~15       | 28–32pin| None (5V)     | 5        | Implemented (flash4)  |
| `0x39`      | FLASH_INTEL_ALT | ~10        | 32-pin  | 12V           | 3 (*)    | NOT implemented       |

(*) Protocol 0x10 (FLASH_INTEL) uses the `configure_eprom()` path via flags&0x08, but this handler
does NOT issue the Intel command register bytes — it would write garbage. A dedicated handler is
required before these chips can be programmed. Protocol 0x39 similarly needs VPP-aware handling.

---

## 4. Protocol Details

### 0x05 — FLASH_AMD_STD

**Representative chips**: AT29C256, AT29C512, AT29C010A, AT29C020, AT29C040A, W29C010, W29C020,
W29C040, SST29EE010, SST29EE020, W29EE512  
**Pins**: 32-pin DIP  
**VPP**: None (5V-only for most; 12V listed for AE29F series only)  
**Chip count in database**: 27

**Algorithm — 5V Flash with EEPROM-like Page Write**:
These chips (AT29C, W29C, SST29EE series) behave like byte-writable EEPROMs. They have no
conventional sector erase; every write auto-erases the target page first.

**Byte/page write sequence**:
1. Optional Software Data Protection (SDP) unlock (required on chips shipped with SDP enabled):
   - Write 0xAA → 0x5555
   - Write 0x55 → 0x2AAA
   - Write 0xA0 → 0x5555
2. Write data bytes to sequential addresses within the same 64-byte page.
   All bytes must be written within the inter-byte window (tBLC = 100–150 µs).
3. After the last byte (or on a WE high edge), the internal write cycle begins (~10 ms).
4. **DQ7 data polling**: Read target address; if DQ7 matches the data written, write is complete.
   If DQ7 is still inverted, the write cycle is in progress.
5. **DQ6 toggle polling**: DQ6 alternates on each read during a write cycle; stops when done.

**Chip erase sequence (SDP-protected chips)**:
1. Write 0xAA → 0x5555, 0x55 → 0x2AAA, 0x80 → 0x5555
2. Write 0xAA → 0x5555, 0x55 → 0x2AAA, 0x10 → 0x5555

**Key constraint**: All bytes in a page write must complete before the internal write timer fires.
This requires tight timing in the programmer — Arduino direct port writes are needed, not
`digitalWrite()`.

**Firestarter dispatch**: `mem_type = 5` (TYPE_FLASH_TYPE_4) → `configure_flash4()`.
`flash4_write_execute()` writes bytes and polls for page completion using `flash4_wait_for_page_write()`.
The DQ7 poll is implemented as: read back the last byte written; if it equals the expected value,
the write cycle is complete.

**RURP hardware support**: Fully supported. 32-pin socket, 5V operation, no VPP.

---

### 0x06 — FLASH_AMD_ALT

**Representative chips**: AM29F010, AM29F040, SST39SF010A, SST39SF020A, SST39SF040, AM29F002B,
AM29F002NBT, W39F010, A290011T, MX29F010  
**Pins**: 32-pin DIP  
**VPP**: None needed (5V-only operation); 12V listed in database as legacy artifact  
**Chip count in database**: 190

This is the dominant protocol — 190 chips. It covers essentially all AM29Fxxx and SST39SFxxx
parallel NOR flash used in retro systems.

**Algorithm — AMD/SST Unlock Sequence (3+1 cycles)**:
All operations require a 2-byte unlock sequence before the command byte:

**Byte program (4 bus cycles)**:
1. Write 0xAA → 0x5555
2. Write 0x55 → 0x2AAA
3. Write 0xA0 → 0x5555
4. Write data byte → target address PA

After cycle 4, the internal program state machine runs (~10–20 µs for byte program).

**Chip erase (6 bus cycles)**:
1. Write 0xAA → 0x5555
2. Write 0x55 → 0x2AAA
3. Write 0x80 → 0x5555
4. Write 0xAA → 0x5555
5. Write 0x55 → 0x2AAA
6. Write 0x10 → 0x5555

Chip erase time: ~100 ms (SST39SF040: 100 ms max; AM29F040: 32 sectors × ~25 ms).

**Sector erase (6 bus cycles)**:
Same as chip erase but replace cycle 6 with: write 0x30 → sector address SA.
Sector sizes: 4 KB (SST39SF), 64 KB (AM29F040), 16 KB/8 KB (AM29F002).

**Read chip ID (4 bus cycles)**:
1. Write 0xAA → 0x5555
2. Write 0x55 → 0x2AAA
3. Write 0x90 → 0x5555
4. Read manufacturer ID from 0x0000, device ID from 0x0001

**Exit autoselect**:
1. Write 0xAA → 0x5555
2. Write 0x55 → 0x2AAA
3. Write 0xF0 → 0x5555
(or write 0xF0 to any address on most devices)

**Data polling (DQ7)**:
During byte program or erase, reading the target address returns the complement of DQ7 (bit 7)
of the data written. When DQ7 matches the written data, the operation is complete.
Timeout indication: DQ5 goes high if the operation exceeds its time limit.

**DQ6 toggle bit**:
DQ6 alternates with each successive read during an embedded operation. When it stops toggling,
the operation is complete.

**FLASH_AMD_ALT vs FLASH_AMD_STD name disambiguation**:
The "STD" vs "ALT" naming in minipro refers to the unlock address choice:
- **FLASH_AMD_ALT (0x06)**: Unlock addresses are **0x5555 / 0x2AAA** (original AM29F040 and most chips)
- **FLASH_AMD_STD (0x05)**: The AT29C / W29C / SST29EE family uses the **same address pattern**
  (0x5555/0x2AAA) but writes to a page buffer, not individual bytes. The "STD" name in minipro
  denotes Atmel/Winbond's early 5V-only flash that behaves like an EEPROM (page write model).

The command addresses (0x5555/0x2AAA) are identical between the two. What differs is the
programming model: byte-at-a-time with DQ7 polling (0x06) vs. page buffer with timed window (0x05).

Note: The Am29F040B (revision B) changed unlock addresses to 0x555/0x2AA vs the original
Am29F040's 0x5555/0x2AAA. Since the address bits above A14 are don't-cares for these unlock
cycles in the 512KB address space, both address ranges are functionally equivalent on the chip —
the programmer can use either. Firestarter uses 0x5555/0x2AAA consistently.

**Firestarter dispatch**: `mem_type = 3` → `configure_flash3()` in `flash_type_3.cpp`.
Command tables are defined in `flash_utils.h`:
```c
FLASH_ENABLE_WRITE[]  = {0x5555/AA, 0x2AAA/55, 0x5555/A0}
FLASH_ERASE[]         = {0x5555/AA, 0x2AAA/55, 0x5555/80, 0x5555/AA, 0x2AAA/55, 0x5555/10}
FLASH_ENABLE_ID[]     = {0x5555/AA, 0x2AAA/55, 0x5555/90}
FLASH_DISABLE_ID[]    = {0x5555/AA, 0x2AAA/55, 0x5555/F0}
```
After each program byte, `flash_util_verify_operation()` polls DQ7 for up to 150 ms.

**RURP hardware support**: Fully supported. 32-pin socket, 5V operation, no VPP needed.

---

### 0x07 — EPROM_STD

**Representative chips**: AM2764A, AM27128A, AM27256, AM27512, AM27C64, AM27C128, AM27C256,
AM27C512, AT27256, M27C256, M27C512, 27C256, 27C512, W27C512, W27E257  
**Pins**: 28-pin DIP  
**VPP**: 12.5–13V (most CMOS variants = 13V; Atmel/Winbond = 12V; early NMOS = 12.5V)  
**Chip count**: 237

This is the largest protocol group — the classic 27-series UV-EPROM family for 64K–512K devices.

**Algorithm — JEDEC Standard EPROM (Intelligent Programming)**:

**VPP application**:
- VPP (12.5V or 13V) is applied to pin 1 of the 28-pin DIP (Vpp pin on the IC).
- VCC is raised to 6.0–6.5V during programming on CMOS variants (reduces write time).
  Note: RURP operates at standard 5V VCC; most modern CMOS chips tolerate 5V for programming
  with additional retries.
- VPP must be stable before asserting CE/PGM.

**Standard program pulse (original "50 ms" algorithm)**:
Used on chips made before ~1982 (early 2764 variants):
1. Set address bus to target address.
2. Set data bus to data byte.
3. Assert CE (Chip Enable) low — this is the "PGM" input on most 27xx chips.
4. Hold CE low for 50 ms.
5. De-assert CE.
6. Read back and verify.

**Intelligent Programming (1 ms × N + 3× overpulse)**:
Standard algorithm for most modern 27xx EPROMs (from ~1983 onwards):
1. Set address and data.
2. Assert CE (PGM) low for 1 ms.
3. De-assert CE.
4. Read back and verify.
5. If mismatch: increment retry counter, repeat step 2.
6. After successful program: apply overprogram pulse = 3× number_of_1ms_pulses (max ~25 ms).
7. Maximum 25 × 1 ms pulses before declaring failure.

M27C512 "PRESTO IIB" algorithm (STMicro variant):
- Uses 100 µs initial pulses (not 1 ms).
- Verifies in "margin mode" (tightened sense amplifier threshold) rather than overprogramming.
- Reduces total programming time to ~6.5 seconds for a 512K chip.
- Compatible with standard equipment; RURP pulse_delay field sets the microsecond pulse width.

**OE/PGM distinction**:
On 27Cxxx (CMOS) chips: PGM = pin 22 (active low). OE (pin 20) and PGM are separate.
On older NMOS chips: CE = pin 18 (active low) is the program enable; OE = pin 20.
The Firestarter firmware drives the program via CE assertion in `memory_set_data()`:
```c
rurp_chip_enable();
delayMicroseconds(handle->pulse_delay);
rurp_chip_disable();
```

**Chip ID read (Electronic Signature)**:
- Raise A9 to VPP (~12V) to enter autoselect mode.
- Read 0x0000 = manufacturer ID.
- Read 0x0001 = device ID.
- Implemented via `A9_VPP_ENABLE` bit in CONTROL_REGISTER.

**Firestarter dispatch**: `mem_type = 1` → `configure_eprom()`.
`eprom_write_execute()` implements adaptive retry with up to 20 attempts per data chunk,
increasing `pulse_delay` by (original × retries / 20) on each retry.

**RURP hardware support**:
- 28-pin socket; JP4 controls VPP routing to pin 1.
- VPP range covers 12.5–13V.
- 5V VCC operation adequate for modern CMOS 27Cxxx with extra retries.

---

### 0x08 — EPROM_QUICK

**Representative chips**: AM27C010, AM27C020, AM27C040, AM27C080, AT27C010, AT27C020, AT27C040,
M27C1001, M27C2001, W27C010, W27C020  
**Pins**: 32-pin DIP  
**VPP**: 12–13V (AMD/TI = 13V; Atmel = 12V or 13V; Winbond = 12V)  
**Chip count**: 127

Same algorithm as EPROM_STD (0x07), but for **32-pin parts** with capacities from 1 Mbit (27C010)
to 8 Mbit (27C080). The "QUICK" name in minipro refers to the Quick Pulse Programming algorithm
being the default for these larger 32-pin EPROMs.

**Key differences from 0x07**:
- 32-pin DIP; address lines A16–A18 used (via CONTROL_REGISTER bits).
- VPP pin location varies: most use pin 1 (P1_VPP_ENABLE); some use pin 31 or A9.
- Capacities: 128KB (27C010), 256KB (27C020), 512KB (27C040), 1MB (27C080).

The "quick pulse" name derives from the 100 µs pulse mode used by PRESTO/PRESTO IIB on
larger ST chips, but the standard Intel Intelligent Programming (1 ms with overpulse) is still
the most common algorithm. Firestarter uses the same `configure_eprom()` handler.

**RURP hardware support**: 32-pin socket, all address lines accessible. P1_VPP_ENABLE routes
VPP to pin 1. Same firmware path as 0x07.

---

### 0x0B — EPROM_LEGACY

**Representative chips**: AM2716, AM2716B, AM2732, AM2732B, AM2732A, Intel 2716, 2732, NMC27C16,
NMC27C32, TMS2716, TMS2732A, MBM2716, MBM2732, ETC2716, CAT27C16  
Also includes some small EEPROMs: AT28C04, AT28C16, 2816, 2816A, 28C04A  
**Pins**: 24-pin DIP  
**VPP**: 12V–18V (and occasionally 25V for very old chips)  
**Chip count**: 53

These are the oldest UV-EPROMs (pre-1983) plus small 24-pin EEPROMs that share the same socket.

**VPP voltage history**:
- **2716 (original ~1977)**: VPP = 25V; chip also required +12V and –5V rails for read operation.
- **2716 (later versions)**: VPP reduced to 21V, then 18V; single 5V supply for reads.
- **2732**: VPP started at 25V, most variants settled at 21V or 18V; pin 18 = VPP.
- **2732A**: VPP = 21V (common) or 18V; improved programming algorithm.
- **B variants (AM2716B, AM2732B)**: VPP = 13V; compatible with modern programmers.
- **Early 27C16 (CMOS)**: VPP = 18V or 13V depending on manufacturer.
- **28C04/28C16 (small EEPROM)**: VPP = 12V; electrically erasable.

**Algorithm**: Same pulse algorithm as 0x07 (50 ms or Intelligent Programming), but:
- Pin 21 on 24-pin DIP = PGM/VPP (varies by chip revision — check datasheet carefully).
- On 2716: CE = pin 18, OE = pin 20, VPP = pin 21 (called "E2" on original Intel spec).
- On 2732: CE = pin 18 (active low = program), A10 doubles as OE/VPP.
- The 24-pin socket in RURP forces A13 high via MSB register bit 5 (special 24-pin mode logic
  in `mem_util_calculate_msb_register()`).

**Chip erase**: UV light only for UV-EPROM variants. Electrically erasable 28C variants use
`eprom_internal_erase()` which applies VPE via A9_VPP_ENABLE + VPE_ENABLE.

**RURP hardware support**:
- 24-pin socket.
- VPP up to 27V supported (RURP spec); must set trimpot appropriately for each chip.
- For 25V chips (ancient originals): RURP physically capable. Trimpot range covers this.
- VPP pin routing is via `bus-config.vpp-pin` field in database, mapped through `pin_conversions`.

---

### 0x0D — EEPROM_POLL

**Representative chips**: AT28C010, AT28C040, X28C010, CAT28C010, CAT28C020, CAT28C040,
M28010, WE128K8, WE256K8, 28C010, 28C011  
**Pins**: 32-pin DIP  
**VPP**: None (internal charge pump) or 12V for older parts  
**Chip count**: 18

These are large-capacity (128KB–512KB) 32-pin parallel EEPROMs. They are the 32-pin evolution
of the 28C64/28C256 family, using the same AT28C programming protocol.

**Note on 28C64 and 28C256** (28-pin): These are classified as EPROM_STD (0x07) in the database,
not EEPROM_POLL. They use the same DQ7/DQ6 polling and SDP unlock, but through the 28-pin EPROM_STD
dispatch path. The split is a database classification choice, not a hardware protocol difference.

**Algorithm — Parallel EEPROM Byte and Page Write**:

**Byte write cycle**:
1. Assert address bus.
2. Assert CE (Chip Enable) low.
3. Assert WE (Write Enable) low — address latches on falling WE edge, data latches on rising edge.
4. Hold WE low for at least tWP (100–200 ns minimum; the chip's timing).
5. De-assert WE high — this triggers the internal write cycle (~5–10 ms max).
6. CE should remain low throughout or go high after WE high.

**Page write (up to 64–128 bytes)**:
All bytes in the same page (defined by upper address bits) must be written within tBLC:
- AT28C256: 64-byte page, tBLC = 150 µs (Atmel), 100 µs (Xicor/ON Semi).
- AT28C010: 128-byte page, tBLC = 150 µs.
- Successive bytes must be written within tBLC of each other.
- The device latches all bytes and commits them together in one ~10 ms internal cycle.

**DQ7 data polling (completion detection)**:
During the internal write cycle, reading DQ7 at the last programmed address returns the complement
of the written data. When DQ7 matches the written bit, the write cycle is complete.
Implementation: read → check (data & 0x80) == (expected & 0x80) → if match, done.

**DQ6 toggle polling**:
DQ6 alternates on every read during an internal write cycle. When it stops toggling, done.

**Software Data Protection (SDP)**:
Unlock sequence to write with SDP enabled:
1. Write 0xAA → 0x5555
2. Write 0x55 → 0x2AAA
3. Write 0xA0 → 0x5555
4. Then write data byte(s) within tBLC.

Disable SDP permanently:
1. Write 0xAA → 0x5555, 0x55 → 0x2AAA, 0x80 → 0x5555
2. Write 0xAA → 0x5555, 0x55 → 0x2AAA, 0x20 → 0x5555

Enable SDP:
1. Write 0xAA → 0x5555, 0x55 → 0x2AAA, 0xA0 → 0x5555

Note: chips often ship with SDP disabled; some may ship enabled depending on batch.

**Firestarter dispatch**: `mem_type = 1` → `configure_eprom()` via the EPROM path.
The EPROM handler uses `memory_set_data()` with `pulse_delay`, then `memory_get_data()` to
read back. There is NO dedicated DQ7 polling loop — the firmware relies on `pulse_delay` being
long enough (set from database `pulse-delay` field). A dedicated handler with a proper DQ7 poll
loop (like `flash_util_verify_operation()`) would be more reliable, especially for page writes.

**RURP hardware support**: Fully supported. 32-pin socket, standard 5V operation, no VPP.

---

### 0x0E — SRAM_32PIN

**Representative chips**: DS1245Y, DS1245AB, DS1249Y, DS1249AB, DS1250Y, DS1250AB,
M48T128Y, M48T128V, M48T512Y, M48T512V, BQ4013YMA, BQ4014YMA, BQ4015YMA  
**Pins**: 32-pin DIP  
**VPP**: 12V listed (Dallas battery override) or None  
**Chip count**: 20

These are battery-backed non-volatile SRAMs (Dallas/Maxim DS12xx series, SGS-Thomson M48Txx
timekeeping RAM, TI BQ40xx series). From the programmer's perspective they are standard SRAMs.

**Algorithm — Standard SRAM Read/Write**:
No programming protocol. The device is static RAM:
1. **Read**: Assert address, assert CE low, assert OE low. Read data within tACC (access time).
   De-assert OE and CE.
2. **Write**: Assert address, assert CE low, assert WE low. Present data. De-assert WE high
   (data latches on rising WE edge). De-assert CE.
3. No VPP, no programming pulses, no polling required.

**12V VPP significance**:
Dallas NVRAM chips (DS12xx, DS1225, DS1230) have a write-protect circuit powered by the
internal battery. Applying 12V to the VPP pin (pin 1 or pin 31 depending on device) bypasses
the write-protect logic and allows the programmer to write. Without this, writes may be blocked.
The M48Txx chips do not have this requirement.

**SRAM_(32PIN) vs SRAM_(512K_1M) distinction**:
Both protocols appear in the database as RW (read-write) vs TEST modes:
- `SRAM_32PIN` (0x0E): Direct read/write mode — programmer writes then reads back to verify.
- `SRAM_512K_1M` (0x29): Same chips but listed with "(TEST)" name suffix — test mode using
  built-in memory test patterns rather than externally loaded data.
Same chips appear twice: once as RW entries and once as TEST entries.
At the programmer hardware level, both use identical read/write cycles; the difference is
purely the test pattern source.

**Firestarter dispatch**: `mem_type = 4` → `configure_sram()` → falls through to
`memory_get_data()` / `memory_set_data()` for standard bus read/write.

**RURP hardware support**: Fully supported. 32-pin socket, 5V operation.

---

### 0x10 — FLASH_INTEL

**Representative chips**: AM28F010, AM28F020, AM28F512, AM28F256, Intel 28F010, Intel 28F256,
P28F010, P28F020, M28F101, M28F201, CAT28F010, CAT28F020, MX28F1000P, TMS28F010, IS28F010,
SST28SF040, SST28LF040  
**Pins**: 32-pin DIP  
**VPP**: 12V mandatory. VPP ≤ 6.5V → all program/erase operations inhibited.  
**Chip count**: 39

This is the original Intel 28F-series NOR flash (ETOX technology), licensed to AMD, STMicro,
Catalyst, Micron, TI, and others. Uses a **Command Register Architecture** — commands are
written to any address to switch operating modes.

**Command set (Intel 28F010)**:

| Write Value | Mode                  | Notes                                              |
|-------------|-----------------------|----------------------------------------------------|
| 0x00        | Read Array            | Default read mode (reset command)                  |
| 0xFF        | Read Array (alt)      | Alternative reset; write twice to ensure reset     |
| 0x40        | Write Setup           | Arms the byte-write latch                          |
| followed by data write | Byte Program | Write data to target address; ~10 µs typical |
| 0xC0        | Program Verify        | Read mode for verifying last programmed byte       |
| 0x20        | Erase Setup           | Arms the chip erase                                |
| 0x20 again  | Erase Confirm         | Second 0x20 triggers chip erase; ~1 s typical      |
| 0xA0        | Erase Verify          | Read mode for verifying erased state (0xFF)        |

**Byte write sequence (Quick-Pulse Programming Algorithm)**:
1. Apply 12V VPP (wait ≥ 100 ns for VPP to stabilize).
2. Write 0x40 to any address.
3. Write data byte to target address PA.
4. Wait 10 µs (typical byte program time).
5. Write 0xC0 to any address.
6. Read PA; compare against expected data.
7. If mismatch: write 0x00 (reset), repeat from step 2, increment counter.
8. Maximum 25 write-verify cycles per byte. After success, write 0x00.

**Chip erase sequence (Quick-Erase Algorithm)**:
1. **Pre-condition**: Program all bytes in the device to 0x00 (mandatory before erase).
   This ensures all cells are in a known state before the high-field erase.
2. Apply 12V VPP.
3. Write 0x20 to any address.
4. Write 0x20 again to any address.
5. Wait ~12 ms (typical erase pulse).
6. Write 0xA0 to any address.
7. Read all bytes; verify all = 0xFF.
8. If any byte ≠ 0xFF: write 0x00, repeat from step 3. Maximum 1000 iterations.

**Key differences from AMD flash (0x06)**:
- **No unlock sequence** — commands go directly to a command register; no address-based unlock.
- **VPP = 12V is mandatory** — AMD/SST 29F flash requires no VPP.
- **Bulk chip erase only** — no sector erase on 28F010/256/512.
- **Pre-program-to-zero** required before erase (AMD flash erases all cells to 1 without this).
- **Verify phase** uses a dedicated verify command (0xC0 / 0xA0), not simple readback.

**Firestarter status**: NOT implemented as a distinct handler.
These chips currently fall into `configure_eprom()` via `flags&0x08`, but the EPROM handler
issues no command register writes — it would perform raw CE pulses on the data bus, which
will NOT program the chip (the device ignores data writes without the 0x40 setup command).
A dedicated `configure_flash_intel()` handler is required.

**RURP hardware support**:
- 32-pin socket; VPP = 12V via P1_VPP_ENABLE.
- 10 µs pulse timing achievable with `delayMicroseconds()`.
- All command write cycles possible via `memory_set_data()` / `fu_flash_flip_data()`.

---

### 0x27 — SRAM_24PIN

**Representative chips**: 6116 (2K×8 SRAM), DS1220(TEST) (Dallas NVRAM)  
**Pins**: 24-pin DIP  
**VPP**: None  
**Chip count**: 2

Standard 24-pin SRAM. The 6116 is a 2K×8 asynchronous SRAM with the following 24-pin JEDEC
pinout: A0–A10 on pins 8–1 and 19–23, D0–D7 on pins 9–11, 13–17, /WE on pin 21, /OE on pin
20, /CS on pin 18, VCC on pin 24, GND on pin 12.

**Algorithm**: Same SRAM read/write as 0x0E. Write: CE + WE low, data present, WE high.
Read: CE + OE low, read data.

The 24-pin socket requires special address routing: A13 is hardwired to VCC in 24-pin mode
(controlled by MSB register bit 5 = `ADDRESS_LINE_13` in firmware).

**Firestarter dispatch**: `mem_type = 4` → `configure_sram()`.

---

### 0x28 — SRAM_STD

**Representative chips**: W24256, W2464, W2465, DS1225(TEST), DS1230W, BQ4011YMA, 6264, 62256  
**Pins**: 28-pin DIP  
**VPP**: None or 12V (Dallas battery override only)  
**Chip count**: 10

Standard 28-pin SRAM chips (8K×8 = 6264/W2464, 32K×8 = 62256/W24256). Same read/write
algorithm as 0x0E. The 28-pin socket covers A0–A14, full 32KB address space without any
address line remapping.

**Firestarter dispatch**: `mem_type = 4` → `configure_sram()`.

---

### 0x29 — SRAM_512K_1M

**Representative chips**: DS1245AB(TEST), DS1249AB(TEST), DS1250AB(TEST), BQ4013YMA(TEST),
BQ4014YMA(TEST), BQ4015YMA(TEST), M48T128Y(TEST), M48T512Y(TEST)  
**Pins**: 32-pin DIP  
**VPP**: None or 12V (battery override)  
**Chip count**: 20

Same physical chips as SRAM_32PIN (0x0E) but with "(TEST)" name suffix in the database.
These are large-capacity (128KB–512KB) battery-backed SRAMs from Dallas/Maxim and TI.
The TEST mode variant likely uses built-in memory test patterns (March test, checkerboard)
rather than externally provided data.

At the hardware level, read/write cycles are identical to 0x0E. No protocol difference.

**Firestarter dispatch**: `mem_type = 4` → `configure_sram()`.

---

### 0x35 — FLASH_EEPROM_LIKE

**Representative chips**: AT29C256, AT29C512, AT29BV010A, AT29LV010A, AT29LV256, AT29LV512  
**Pins**: 28–32-pin DIP  
**VPP**: None (5V-only internal charge pump)  
**Chip count**: ~15 (filtered from current Firestarter DB build)

Atmel AT29C series 5V-only flash — essentially the same algorithm as 0x05 (FLASH_AMD_STD).
These chips were designed as drop-in EPROM replacements:
- 28-pin package for AT29C256/512 (matches 27C256/512 pinout).
- Electrically erased — no UV lamp needed.
- Page write: up to 64 bytes per cycle, tBLC = 150 µs.
- SDP unlock identical to AT28C series.

**Distinction from 0x05**: The minipro classification uses 0x35 for Atmel 29C-only chips
and 0x05 for the broader Atmel/Winbond/SST family. At the programming algorithm level they
are effectively identical — both use the 5V page-write model with optional SDP unlock.

**Firestarter dispatch**: Would use `mem_type = 5` → `configure_flash4()` (same as 0x05).

---

### 0x39 — FLASH_INTEL_ALT

**Representative chips**: AT49F010, AT49F020, AT49F040, AT49F001N, AT49F002N  
**Pins**: 32-pin DIP  
**VPP**: 12V for erase on older AT49F series; 5V-only on AT49LF series  
**Chip count**: ~10 (filtered from current Firestarter DB build)

Atmel AT49F series — these use the AMD-style unlock command sequence (identical to 0x06)
but require 12V VPP on some operations. The "INTEL_ALT" name in minipro likely refers to the
combination of Intel-class 28F-like VPP requirement with AMD-style software unlock.

**Algorithm**: Identical to FLASH_AMD_ALT (0x06):
- Byte program: unlock 0x5555/AA, 0x2AAA/55, 0x5555/A0, then data to PA.
- Chip erase: 6-cycle sequence with 0x10 to 0x5555.
- Sector erase: 6-cycle sequence with 0x30 to sector address.

The only difference from 0x06: VPP = 12V required on pin 1 for erase on AT49F010/020/040.
AT49LF variants dropped this requirement.

**Firestarter dispatch**: Would use `mem_type = 3` → `configure_flash3()` (same handler as 0x06)
with VPP enabled via P1_VPP_ENABLE. The flash3 handler would work directly if VPP is applied.

---

## 5. Data Polling Reference

All flash/EEPROM programming completion is detected via data polling. Summary:

| Chip type           | Polling method                                   | Timeout    |
|---------------------|--------------------------------------------------|------------|
| AMD/SST 29F (0x06)  | DQ7: read PA, (data & 0x80) == (expected & 0x80) | 150 ms     |
| AT29C/W29C (0x05)   | DQ7: same as above (last byte of page)           | 10 ms      |
| AT28C/28C series    | DQ7: same + DQ6 toggle stops when done           | 10 ms      |
| Intel 28F (0x10)    | Write 0xC0, then read PA and compare             | 25 retries |
| UV-EPROM (0x07/08)  | Direct readback compare (no dedicated polling)   | N/A        |

**Firestarter's DQ7 implementation** (in `flash_util_verify_operation()`):
```c
while (millis() < timeout) {
    if ((fu_flash_data_poll() & 0x80) == (expected_data & 0x80)) {
        if ((fu_flash_data_poll() & 0x80) == (expected_data & 0x80)) {
            return;  // Complete
        }
    }
}
// Timeout error
```
Reading twice before declaring success guards against false positive during DQ6 toggle.

---

## 6. VPP Voltage Requirements Summary

| Protocol | VPP Voltage(s)    | RURP Delivery Method                          | Notes                          |
|----------|-------------------|-----------------------------------------------|--------------------------------|
| 0x05     | None              | N/A (5V-only chips)                           | No VPP required                |
| 0x06     | None              | N/A (5V-only; 12V in DB = legacy artifact)    | No VPP required                |
| 0x07     | 12–13V            | REGULATOR + VPE_TO_VPP + P1_VPP_ENABLE (JP4)  | Precise VPP via R1/R2 divider |
| 0x08     | 12–13V            | REGULATOR + VPE_TO_VPP + P1_VPP_ENABLE (32p)  | Same as 0x07                  |
| 0x0B     | 12–18V (or 25V)   | REGULATOR + VPE_ENABLE (direct), trimpot set  | Oldest chips need 25V          |
| 0x0D     | None / 12V        | No VPP; 12V via P1_VPP_ENABLE for SDP unlock  | SDP bypass only                |
| 0x0E     | None / 12V        | 12V via P1_VPP_ENABLE for Dallas write-protect| Optional                       |
| 0x10     | 12V mandatory     | REGULATOR + P1_VPP_ENABLE (mandatory)         | ≤6.5V → writes inhibited       |
| 0x27     | None              | N/A                                           | 5V SRAM                        |
| 0x28     | None / 12V        | 12V via P1_VPP_ENABLE for Dallas chips        | Optional                       |
| 0x29     | None / 12V        | 12V via P1_VPP_ENABLE for Dallas chips        | Optional                       |
| 0x35     | None              | N/A (5V-only flash)                           | No VPP required                |
| 0x39     | None / 12V        | REGULATOR + P1_VPP_ENABLE (older AT49F)       | AT49LF needs no VPP            |

**VPP routing on RURP**:
- **P1_VPP_ENABLE** (`0x08`): Routes VPP to pin 1 of the DIP socket.
- **A9_VPP_ENABLE** (`0x02`): Routes VPP to address line A9 (EPROM chip-ID, 24-pin erasure).
- **VPE_ENABLE** (`0x04`): Applies full VPE voltage to the programming pin.
- **VPE_TO_VPP** (`0x100`, Rev 2): Drops VPE through resistor to produce lower VPP voltage.

---

## 7. Protocol Groupings for Implementation

### Group A: SRAM (simple read/write, no protocol)
**Protocols**: 0x27, 0x28, 0x29, 0x0E  
**Implementation**: Assert address, toggle CE+WE for write, CE+OE for read. No VPP.  
**Shared code**: `configure_sram()` → `memory_get_data()` / `memory_set_data()`.  
**Status**: Implemented in Firestarter (minimal but functional). The Dallas 12V VPP override
is handled by applying VPP before write via P1_VPP_ENABLE in the chip's bus-config.

### Group B: UV-EPROM (high-voltage pulse program)
**Protocols**: 0x07, 0x08, 0x0B  
**Implementation**: VPP ramp-up (REGULATOR), pulse CE for tWP (µs range), verify, retry with
increasing pulse width, optional chip ID via A9 VPP.  
**Key differences**:
- 0x07 = 28-pin (JP4 jumper for VPP on pin 1); VPP = 12.5–13V
- 0x08 = 32-pin (P1_VPP_ENABLE); VPP = 12–13V; extended address bus
- 0x0B = 24-pin; VPP = 12–18V; A13 hardwired; VPP on varied pins
**Shared code**: `configure_eprom()` handles all three.  
**Status**: Implemented.

### Group C: Parallel EEPROM (data polling, byte/page write)
**Protocols**: 0x0D  
**Implementation**: Byte write (CE + WE pulse), page write within tBLC window, DQ7/DQ6 polling.  
**Current issue**: Uses `configure_eprom()` path with fixed `pulse_delay`; no DQ7 poll loop.
A dedicated handler like `configure_flash4()` (which already has `flash4_wait_for_page_write()`)
would be a better fit and is likely what the TYPE_FLASH_TYPE_4 was designed for.  
**Status**: Partially functional. Reliable for byte writes with adequate `pulse_delay`. Page
write support would require tighter timing control.

### Group D: AMD-Style Flash (5V unlock sequence, DQ7 poll)
**Protocols**: 0x05, 0x06, 0x35, 0x39  
**Implementation**:
- 0x06 / 0x39: 3-byte unlock before each program byte, sector/chip erase, DQ7 poll.
- 0x05 / 0x35: Page buffer write, optional SDP unlock, DQ7 poll at page boundary.
**Key differences**:
- 0x06: Byte-level unlock on every write; sector granularity erase; most common.
- 0x39: Same as 0x06 but older AT49F parts need 12V VPP for erase (apply P1_VPP_ENABLE).
- 0x05: EEPROM-like page buffer; unlock once per page write; no explicit sector erase.
- 0x35: Same algorithm as 0x05 (Atmel AT29C family); 28-pin variants also supported.
**Shared code**: 0x06 → `configure_flash3()`. 0x05/0x35 → `configure_flash4()`.
0x39 → could reuse `configure_flash3()` with conditional VPP application.  
**Status**: 0x06 fully implemented. 0x05/0x35 → `configure_flash4()` implemented.
0x39 requires VPP integration into flash3 path.

### Group E: Intel-Style Flash (command register, 12V VPP mandatory)
**Protocol**: 0x10  
**Implementation**: 0x40 setup + data write + 0xC0 verify per byte. 0x20+0x20 for erase.
Pre-program all bytes to 0x00 before erase. 12V VPP always required.  
**Commands**: 0x00/0xFF (read), 0x40 (setup program), 0xC0 (program verify), 0x20 (erase setup),
0xA0 (erase verify).  
**Shared code**: Needs dedicated `configure_flash_intel()`. Cannot share with other groups.  
**Status**: NOT implemented. Currently falls into eprom path, which does not work for these chips.

---

## 8. Implementation Gaps and Priority

| Protocol | Gap                              | Priority | Effort  | Chip count |
|----------|----------------------------------|----------|---------|------------|
| 0x10     | Intel 28F command register       | High     | Medium  | 39         |
| 0x0D     | DQ7 poll loop for EEPROM         | Medium   | Low     | 18         |
| 0x39     | AT49F with VPP + flash3 handler  | Low      | Low     | ~10        |
| 0x35     | Same as 0x05 (if not already)    | Low      | Trivial | ~15        |

Notes:
- 0x10 (FLASH_INTEL) is the most impactful gap: 39 chips including popular AM28F010, TMS28F010,
  Intel 28F256/512/010 — all completely non-functional with the current EPROM handler.
- 0x0D chips may work with current pulse_delay approach for byte writes, but page write
  reliability depends on pulse_delay being ≥ the write cycle time (not a real DQ7 poll).
- 0x39 chips work if the flash3 handler is invoked AND VPP is applied before the erase command.

---

## 9. Key Firmware Flags Reference

The `ctrl_flags` field (set from the database `flags` attribute) encodes chip capabilities
sent from the Python app to the firmware:

| Bit mask (app)  | Constant           | Firmware Behaviour                              |
|-----------------|--------------------|-------------------------------------------------|
| `FLAG_FORCE`    | 0x01               | Override chip ID mismatch warnings              |
| `FLAG_CAN_ERASE`| 0x02               | Chip supports electrical erase; run erase step |
| `FLAG_SKIP_ERASE`| 0x04              | Skip erase even if FLAG_CAN_ERASE is set        |
| `FLAG_SKIP_BLANK_CHECK`| 0x08       | Skip blank check after erase                    |
| `FLAG_VPE_AS_VPP`| 0x10              | Use full VPE voltage directly (no voltage drop) |
| `FLAG_OUTPUT_ENABLE`| 0x20           | Force OE low during write (chip-specific)       |
| `FLAG_CHIP_ENABLE`| 0x40             | Force CE mode (chip-specific)                   |
| `FLAG_VERBOSE`  | 0x80               | Verbose output mode                             |

The `FLAG_CAN_ERASE` flag is set in `database.py` when `info-flags & 0x00000010` is true
(the "electrically erasable" bit). This determines whether the erase step runs before writing.

---

## 10. Sources

- RURP hardware: https://github.com/AndersBNielsen/Relatively-Universal-ROM-Programmer
- Firestarter firmware source: `/firestarter/src/proms/` (eprom.cpp, flash_type_3.cpp,
  flash_type_4.cpp, flash_utils.cpp, sram.cpp, memory.cpp)
- Firestarter app source: `/firestarter_app/firestarter/database.py` (PROTOCOL_MAP, types)
- Database: `/firestarter_app/firestarter/data/minipro_complete_db.json`
- AMD Am29F040 programming command table: datasheet revision G, command definitions table 4
- SST39SF040 software driver reference: Microchip/SST application note (SST39SF040.txt)
- AT28C256 SDP and page write: Microchip/Atmel AT28C256 datasheet + bread80.com analysis
- Intel 28F010 command register: Intel 28F010 datasheet (yumpu.com scanned version)
- EPROM voltage history (2708–2764): applefritter.com EPROM voltage survey
- M27C512 PRESTO IIB algorithm: archive.org 27C512 data sheet djvu.txt
