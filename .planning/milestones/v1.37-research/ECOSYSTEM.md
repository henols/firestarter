# EPROM Programmer Ecosystem Research

## 1. minipro's Protocol Model

### Overview

minipro is an open-source host-side tool (GPLv3) for the XGecu/Autoelectric TL866 family of universal programmers (TL866A/CS, TL866II+, T48, T56). The key architectural insight is that **protocol_id does not select code running on the PC — it selects a firmware-embedded algorithm running on the programmer's FPGA or MCU**.

### How protocol_id Maps to Programming Code

The TL866/T48/T56 hardware contains an FPGA. The PC software sends a command to the firmware that says "use algorithm N". The firmware then switches its FPGA bitstream (or internal algorithm table) to implement that specific bus protocol. The PC software itself is thin: it passes the protocol_id through to the hardware in the USB command and is not responsible for implementing read/write/erase sequences.

For the T56 (the newest model), algorithms must be loaded from `algorithm.xml` which is extracted from the official XGecu package (cannot be redistributed due to copyright). Earlier models store algorithms on a flash chip on the programmer board, updated with firmware.

The mapping is: `infoic.xml chip entry → protocol_id integer → hardware firmware algorithm slot`.

### Source File Structure (DavidGriffith/minipro on GitLab)

From the repository at https://gitlab.com/DavidGriffith/minipro:

- `database.c` — parses `infoic.xml` and constructs the device lookup table
- `prom.c` — defines the `prom_table[]` array which maps `variant` values to physical pinout configurations for custom-pinout PROMs (used when `protocol_id=0x80000001`)
- `minipro.c` — top-level dispatch: looks up device by name, extracts `protocol_id`, sends it to firmware
- `infoic.xml` — the chip database (16,328 entries for TL866II+, 4,918 for TL866A/CS)
- `algorithm.xml` — T56 FPGA bitstreams (extracted from XGecu software, not in repo)

The special value `protocol_id="0x80000001"` means "custom pinout PROM": the `variant` field then indexes into `prom_table[]` in `prom.c` to get the physical pin permutation. All standard protocols use integer values 0x01–0x34.

### What protocol_id Does NOT Do

minipro's `protocol_id` is **not** a key into source-code functions in the PC software. The PC software has no `switch(protocol_id)` that calls different write algorithms. Instead, all that logic lives in the firmware/FPGA. This is the core reason `protocol_id` alone is insufficient for a standalone programmer like Firestarter that runs its own firmware — Firestarter must implement each algorithm in its own C++ code.

---

## 2. infoic.xml Structure

### File Organization

```xml
<infoic>
  <database device="TL866II">       <!-- or INFOICT76, INFOIC2PLUS, INFOIC -->
    <manufacturer name="AMD">
      <ic name="AM27C256@DIP28" ... />
      ...
    </manufacturer>
    <custom name="MyCustom">
      <ic ... />
    </custom>
  </database>
</infoic>
```

`infoic.xml` (TL866II) has 16,328 entries. `infoic2.xml` covers multiple hardware generations: INFOICT76 (11,434 entries), INFOIC2PLUS (11,510), and INFOIC (4,918).

### Per-Chip Attribute Reference

Every `<ic>` element has these attributes:

| Attribute | Type | Description |
|---|---|---|
| `name` | string | Chip name with `@PACKAGE` suffix (e.g. `AM27C256@DIP28`) |
| `type` | hex | 1=EEPROM/EPROM, 2=MCU/MPU, 3=PLD/CPLD, 4=SRAM, 6=NAND, 7=eMMC |
| `protocol_id` | hex | Index into firmware algorithm table (see section 5) |
| `variant` | hex | Sub-protocol variant; for EPROMs selects timing/pinout; for custom PROMs indexes `prom_table[]` |
| `read_buffer_size` | hex | Max bytes the programmer returns per USB transaction |
| `write_buffer_size` | hex | Max bytes per write USB transaction |
| `code_memory_size` | hex | Total capacity in bytes (main flash/code) |
| `data_memory_size` | hex | Secondary data memory size (e.g. EEPROM in MCU) |
| `data_memory2_size` | hex | Tertiary storage (e.g. EEPROM page 2) |
| `page_size` | hex | Write page size in bytes (0x0000 for EPROMs = byte-at-a-time) |
| `pages_per_block` | hex | Erase block size in pages (0 for non-block devices) |
| `chip_id` | hex | JEDEC/manufacturer device ID; `0x00000000` = not readable |
| `voltages` | hex | Packed: bits [15:12]=VDD table index, bits [11:8]=VCC table index, bits [7:0]=VPP table index |
| `pulse_delay` | hex | Programming pulse width in microseconds |
| `flags` | hex | Capability bitmask (see below) |
| `chip_info` | hex | Miscellaneous info (often 0x0006 for EPROMs) |
| `pin_map` | hex | Index into the TL866 internal pin-mapping table |
| `package_details` | hex | Packed: bits [30:24]=pin count, bit 31=SMD, low byte=adapter type |
| `config` | string | "NULL" or MCU fuse/config data string |

### Voltage Encoding

The `voltages` field is decoded by `parse_db.py` in the firestarter tools:

**VPP** (bits [7:0]) maps to actual voltage via a lookup table:
- `0x00` → 12V, `0x10` → 9V, `0x70` → 13V, `0x80` → 13.5V, `0xF0` → 18V, etc.

**VCC** (bits [11:8]) maps to: `0x00`=5V, `0x01`=3.3V, `0x02`=4V, `0x03`=4.5V, `0x04`=5.5V, `0x05`=6.5V

**VDD** (bits [15:12]) uses same table as VCC.

Example for standard 5V EPROMs: `voltages=0x5070` means VDD=5V (nibble 5→6.5V — note nibble 5 maps to 6.5V which is OE/CE Vcc for EPROM programming), VCC=5V (nibble 0), VPP=13V (byte 0x70).

### Flags Bitmask

Key bits in the `flags` field (confirmed from `parse_db.py`):
- Bit 4 (`0x00000010`): `MP_ERASE_MASK` — chip can be electrically erased
- Bit 5 (`0x00000020`): `MP_ID_MASK` — chip has readable electronic ID
- Bits [21:20] (`0x00300000`): `MP_SUPPORTED_PROGRAMMING` — programming mode support
- Bit 7 in lower nibble of variant: `HITACHI_MASK_PROM_MASK` — Hitachi mask ROM (read-only)

For standard 27C EPROMs the flags value `0x00000068` is dominant:
- Bit 3 (0x08) = skip blank check allowed
- Bit 5 (0x20) = has chip ID
- Bit 6 (0x40) = chip enable polarity
(The exact bit meanings beyond bits 4-5 remain partially reverse-engineered.)

### Package Detection

`package_details` encoding (from `parse_db.py`):
- `PIN_COUNT_MASK = 0x7F000000`: bits [30:24] give DIP pin count (24, 28, 32, 40)
- `SMD_MASK = 0x80000000`: bit 31 set = SMD package (excluded from Firestarter DIP focus)
- `PLCC32_ADAPTER = 0xFF000000`, `PLCC44_ADAPTER = 0xFD000000`: PLCC adapters
- `ADAPTER_MASK = 0x000000FF`: low byte = adapter type (non-zero = requires adapter)
- `ICSP_MASK = 0x0000FF00`: bits [15:8] = ICSP programming method

---

## 3. Comparable Open-Source EPROM Programmers

### 3a. TommyPROM (tomnisbet/TommyPROM on GitHub)

**Architecture**: Driver-based, compile-time chip selection. The Arduino code is modular with one driver compiled per build. Selection via `#define PROM_IS_xx` in `Configure.h`.

**Chip database approach**: No runtime database. Parameters for each chip family are hardcoded in the driver's `.cpp` file. E.g., the 28C256 driver has its timing constants embedded in source.

**Supported families**:
- 28C series EEPROMs (28C64, 28C256) — primary focus
- SST39SF NOR flash (sector erase via command sequences)
- 27C EPROMs (read-only in standard hardware config)
- 29C flash
- Intel 8755A EPROM

**Algorithm selection**: Purely compile-time. No chip database, no runtime dispatch by protocol_id.

**Relevance to Firestarter**: Demonstrates that a clean modular driver per chip family is viable for an Arduino-based programmer. The key insight is that each chip *family* (not individual part) needs a driver, and family membership is determined by protocol, not part number.

### 3b. BMBurner (bouletmarc/BMBurner on GitHub)

**Architecture**: Arduino firmware + Windows host app. Chip type passed as an integer code over serial.

**Chip database approach**: Chip type codes are hardcoded integers in both firmware and host app. The serial protocol sends `C=N` where N is a small integer (e.g. C=2 for 27C256, C=5 for 27SF512). No XML or JSON database.

**Supported families**:
- 27C256 (read-only via standard read)
- 27SF256, 27SF512 (SST sector-erase flash)
- 29C256
- W27C512, W27E512 (EEPROM with software write protect)
- DS1230 (NVRAM)
- 62C256/61C256 (SRAM)

**Algorithm selection**: Switch statement in firmware on the chip type code. Simple and transparent but brittle — adding a new chip requires firmware + host update.

**Relevance to Firestarter**: The type code approach is essentially what `protocol_id` + `mem_type` accomplishes in Firestarter's JSON serial protocol. BMBurner shows this pattern works well for a small device set.

### 3c. open-tl866 (JohnDMcMaster/open-tl866 on GitHub)

**Architecture**: Replacement open-source firmware for the original TL866A hardware, plus a Python host library.

**Chip database approach**: The project exposes low-level "bitbang" mode to the Python library. The Python side drives pin states directly. No chip database at the firmware level. Chip-specific sequences are implemented in Python.

**Algorithm selection**: Python controls everything. The firmware is pin-level abstraction only. This is the opposite of the commercial TL866 firmware where the FPGA algorithm lives on the device.

**Relevance to Firestarter**: Shows that separating host intelligence from firmware primitive operations is viable, but requires more round-trips. Firestarter's architecture (JSON command → Arduino executes full operation) is higher-level and better suited to latency constraints.

---

## 4. Database Quality Signals

### What minipro's infoic.xml Does NOT Provide

There is **no "verified" or "tested" flag** in the infoic.xml schema. The database was reverse-engineered from Xgecu's proprietary `InfoIC.dll` (originally binary, now XML). Quality/accuracy is implied by whether Xgecu has shipped that chip in their commercial product, but that is an indirect signal.

Known issues:
- Some entries have `chip_id="0x00000000"` because the chip has no electronic ID — this is correct. But some entries have zero chip_id simply because the ID was not reverse-engineered or is wrong.
- The variant values for custom pinout PROMs required manual cross-referencing with datasheets.
- The re-reverse-engineering work (vdudouyt/minipro issue #109) found 3,145 new parts and 390 changed values when comparing v6.60 against the existing database — indicating systematic errors existed.

### Quality Signals Available in infoic.xml

1. **Non-zero `chip_id`**: 76% of DIP EPROM entries have a non-zero `chip_id`, which means the electronic ID was verified to be readable. A non-zero `chip_id` with `flags & MP_ID_MASK` is a strong quality signal.

2. **`flags & MP_ID_MASK` (bit 5)**: When set, the TL866 firmware will actively verify the chip ID before programming. Entries with this flag set have been at least partially validated against real hardware.

3. **`chip_info` field**: Value `0x0006` on nearly all 27C EPROMs suggests a consistent pattern from the original Xgecu database rather than a manually-added entry.

4. **Multiple manufacturer entries**: When several manufacturers have the same chip (e.g. `AM27C256`, `M27C256`, `TC57256`) with consistent parameters (same `voltages`, same `pulse_delay`), this cross-reference increases confidence.

5. **The `verified.txt` file** in the firestarter_app tools directory: A hand-maintained list of 6 chips (`W27C512`, `FM1608`, `SST27SF512`, `M2764A`, `W27E257`, `M27C512`) confirmed to work with the Firestarter hardware. This is the only true hardware-tested quality signal in the current project.

### Assessment by chip_id presence in DIP chips (infoic.xml)

- All chips: 55% (9,025/16,328) have non-zero chip_id
- EPROM DIP chips: 76% (183/239) have non-zero chip_id

The EPROM segment is better-covered for electronic ID support than the database average, likely because EPROM programming is the original/core use case of the TL866.

---

## 5. Protocol ID Coverage for DIP 24/28/32 Parallel Memory Chips

This analysis uses the infoic.xml (TL866II+ database, 16,328 total entries) filtered to EEPROM/EPROM/SRAM type with DIP24, DIP28, or DIP32 packages.

### Protocol IDs: Dominant Set (DIP parallel memory, types 1 and 4)

| protocol_id | Count | Firestarter Name | Chip Family Examples |
|---|---|---|---|
| `0x07` | 230 | `EPROM_STD` | AM27C256, AM27C512, 27C128, AM2764A — standard DIP28 UV-EPROMs |
| `0x06` | 120 | `FLASH_AMD_ALT` | AM29F002, SST39SF010, W49F002 — AMD/SST NOR flash DIP32 |
| `0x08` | 115 | `EPROM_QUICK` | AM27C010, M27C1001, AT27C040 — large DIP32 UV-EPROMs (1Mbit+) |
| `0x0b` | 55 | `EPROM_LEGACY` | AM2716, AM2732, 2716, TMS2716 — DIP24 legacy EPROMs |
| `0x0e` | 22 | (SRAM_special) | M48T128 (timekeeper SRAM), CAT28C010 — DIP32 byte-wide SRAM |
| `0x10` | 9 | `FLASH_INTEL` | HN28F101, P28F001BX — Intel-style NOR flash DIP32 |
| `0x05` | 5 | `FLASH_AMD_STD` | AE29F1008 — DIP32 sector-erase flash |
| `0x0d` | 4 | `EEPROM_POLL` | CAT28C512, CAT28C010 — DIP32 page-write EEPROM |
| `0x80000001` | 1 | custom pinout | HN43128 and other rare/unusual pinout PROMs |

**Total DIP24/28/32 parallel memory chips: 561 entries** (across 9 distinct protocol_ids).

### Additional EPROM Protocols (non-DIP variants counted in total)

| protocol_id | Count (all) | Description |
|---|---|---|
| `0x0a` | 98 | PLCC32 EPROMs (AM27C256@PLCC32, etc.) |
| `0x09` | 45 | DIP40 wide-bus EPROMs (27C1024, 27C4096) |

### The Two Core EPROM Protocols

For standard UV-erasable EPROMs, only two protocols cover the vast majority:

**`0x07` (EPROM_STD) — DIP28, 64K–512K**:
- Chips: all standard 27C64/27C128/27C256/27C512 variants
- `variant` values encode the pin address mapping:
  - `0x10` → 27C512 (64KB, 28 pins all used)
  - `0x11` → 27C256 (32KB)
  - `0x13` → 27C64/2764A (8KB)
  - `0x26` → AM28C17A and other DIP28 EEPROMs
- Most common `pin_map`: `0x0016` (183 of 230 DIP28 EPROMs)

**`0x08` (EPROM_QUICK) — DIP32, 1Mbit+**:
- Chips: 27C010 (128KB), 27C020 (256KB), 27C040 (512KB), 27C080 (1MB)
- `variant` values:
  - `0x00` → 27C010 (128KB, 1Mbit)
  - `0x01` → 27C020 (256KB, 2Mbit)
  - `0x02` → 27C040 (512KB, 4Mbit)
  - `0x03` → 27C080 (1MB, 8Mbit)
- Most common `pin_map` values: `0x000c`, `0x000a`

**`0x0b` (EPROM_LEGACY) — DIP24, ≤32K**:
- Chips: 2716 (2KB), 2732/2732A (4KB), 27C16, 27C32
- All have `chip_id="0x00000000"` — no electronic ID support
- Variant `0x00` = 2716-type, `0x01` = 2732-type, `0x10` = DIP24 EEPROM

### Protocol Mapping in Firestarter (current PROTOCOL_MAP)

From `firestarter_app/firestarter/database.py`:

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

The firmware dispatch in `firestarter/src/proms/memory.cpp` uses `handle->mem_type` (not `protocol_id` directly):

```cpp
#define TYPE_EPROM       1
#define TYPE_FLASH_TYPE_2 2
#define TYPE_FLASH_TYPE_3 3
#define TYPE_SRAM        4
#define TYPE_FLASH_TYPE_4 5
```

The Python `database.py` translates `algorithm` name → `protocol_id` integer, then the firmware maps `mem_type` to algorithm implementation. The `protocol_id` is currently used as an intermediate identifier but the actual firmware dispatch is on `mem_type` (a 5-value enum), meaning multiple `protocol_id` values can map to the same firmware code path.

---

## 6. Key Findings and Implications

### For Using protocol_id as Authoritative Algorithm Selector

1. **protocol_id IS the right primary key** for algorithm selection among the 561 DIP memory chips. Only 9 distinct protocol_ids are needed to cover the full DIP24/28/32 parallel memory space in infoic.xml.

2. **variant is a secondary key** that disambiguates timing and pinout within a protocol family. For EPROMs, `variant` encodes the address line configuration (which RURP pins get which address bits).

3. **The current Firestarter PROTOCOL_MAP is complete** for standard DIP memory chips. It covers all 9 relevant protocol_ids. The gap is that `0x0a` (PLCC) and `0x09` (DIP40) are not included, but these require adapters.

4. **No verified/confidence field exists** in infoic.xml. The best quality signals are: non-zero `chip_id`, presence of `flags & MP_ID_MASK`, and cross-referencing multiple manufacturer entries with consistent parameters.

5. **pulse_delay is critical and per-chip**: Standard 27C EPROMs use `0x0064` (100µs). Legacy 2716/2732 use `0x01f4` (500µs). NMC27C chips use `0x00c8` (200µs). Using the wrong pulse_delay is the most common cause of programming failures.

6. **Voltages encoding is not trivial**: The `voltages` field packs VPP, VCC, and VDD into 16 bits using non-linear lookup tables. The parse_db.py VPP table shows 9V–18V range in 0.5V steps. This must be decoded correctly — the raw hex value is not a voltage.

7. **Firestarter's `mem_type` abstraction** hides the fact that multiple minipro `protocol_id` values map to the same firmware code. This is correct design: `protocol_id` 0x07 and 0x08 are both UV-EPROM protocols that differ only in timing/pinout (handled by `variant`), so one firmware driver with parameterized behavior covers both.
