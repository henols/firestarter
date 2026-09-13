# Architecture Patterns: Open-Source EPROM Programmer Dispatch

Research conducted: 2026-05-08
Scope: How open-source EPROM programmers handle protocol_id → algorithm dispatch, pinout vs. algorithm separation, and Arduino wire protocols.

---

## 1. How minipro Handles Protocol Dispatch

### The infoic.xml Database Schema

minipro's chip database (`infoic.xml`, ~16,000 entries) encodes every supported device as a flat XML element. The key fields for Firestarter:

```xml
<ic name="AT27C512@DIP28"
    type="1"
    protocol_id="0x07"
    variant="0x10"
    code_memory_size="0x10000"
    voltages="0x4000"
    pulse_delay="0x0064"
    flags="0x00000068"
    chip_id="0x00001e0d"
    pin_map="0x0016"
    package_details="0x1c000000" />
```

- `type`: chip category. 1=EEPROM/EPROM/memory, 4=SRAM, 2=MCU, etc.
- `protocol_id`: numeric ID encoding the programming algorithm family. This is the key dispatch selector.
- `variant`: sub-variant within the protocol (e.g., which address lines are active, pin multiplex mode). Distinct from `pin_map`.
- `pin_map`: raw hardware pin-map index (opaque numeric). Maps to the physical DIP pinout used by the TL866 ZIF socket.
- `package_details`: encodes physical package type (DIP, PLCC, SOIC, TSOP), pin count, and adapter flags.
- `flags`: bitfield. Bit 4 = chip can be electrically erased; bit 5 = has readable chip ID.
- `voltages`: bitfield encoding VPP and VCC levels.
- `pulse_delay`: programming pulse width in hardware units (interpretation varies by protocol).

### Known protocol_id Values (from infoic.xml analysis)

These are the protocol_id values present in the Firestarter project's local copy of infoic.xml, with their frequency and decoded meanings:

| protocol_id | Count | Algorithm Name    | Meaning                                                   |
|-------------|-------|-------------------|-----------------------------------------------------------|
| 0x01        | 2680  | I2C_STD           | I2C serial EEPROM (24Cxx family)                          |
| 0x02        | 2259  | (serial)          | Microwire/SPI serial variants                             |
| 0x03        | 4009  | SPI_STD           | SPI serial Flash (largest group)                          |
| 0x05        | 118   | FLASH_AMD_STD     | AMD/SST Flash, standard command set (Write + Erase unlock)|
| 0x06        | 1052  | FLASH_AMD_ALT     | AMD Flash, alternate command set                          |
| 0x07        | 438   | EPROM_STD         | Standard parallel EPROM (27256, 27512, 27C512): CE-pulse  |
| 0x08        | 490   | EPROM_QUICK       | Quick-Pulse / Intelligent Programming EPROM (27C010+)     |
| 0x0A        | 264   | (PLCC_ADAPTER)    | Parallel EPROM in PLCC32 adapter — same algorithm as 0x07 |
| 0x0B        | 100   | EPROM_LEGACY      | Legacy 24-pin EPROM (2716, 2732): 21V/25V VPP, long pulse |
| 0x0D        | 63    | EEPROM_POLL       | Parallel EEPROM with data polling (28Cxxx)                |
| 0x10        | 122   | FLASH_INTEL       | Intel/Sharp Flash (Write Buffer + Block Erase)            |
| 0x12        | 2019  | (MCU)             | Microcontroller types                                     |
| 0x28        | (few) | SRAM_STD          | Static RAM                                                |

The three most important for Firestarter's EPROM use-cases:
- **0x07 EPROM_STD**: 28-pin JEDEC (2764, 27128, 27256, 27512). CE-pulse programming. ~100µs pulses. Vpp 12.5V or lower.
- **0x08 EPROM_QUICK**: 32-pin larger EPROM (27C010, 27C040, 27C080). Intelligent/quick-pulse algorithm. ~1µs pulses, adaptive retry.
- **0x0B EPROM_LEGACY**: 24-pin vintage EPROM (2716, 2732). Long pulse (50ms), high Vpp (21V or 25V).

### How minipro Dispatches on the Host Side

minipro (the C command-line tool) operates in two tiers:

1. **Database lookup**: Parse `infoic.xml`, find the chip by name, extract `protocol_id`, `variant`, `pin_map`, `voltages`, `flags`, etc.
2. **Programmer command construction**: Encode a binary command packet that includes `protocol_id` (sent verbatim to the TL866 hardware). The TL866 firmware itself contains the algorithm implementations; minipro does NOT implement the programming pulse logic — it sends a command block and the hardware does the work.

For the TL866 series, `protocol_id` is passed directly in the USB command packet and the proprietary firmware on the TL866 FPGA/MCU dispatches to its internal algorithm. This is fundamentally different from the Firestarter architecture where the Arduino firmware implements the algorithms.

### The variant Field

`variant` is a secondary discriminator within a `protocol_id`. For EPROM_STD (0x07), variant encodes the address bus configuration:
- variant=0x10 → 27512 layout (A15 present)
- variant=0x11 → 27256 layout (A14 present, A15=NC)
- variant=0x13 → 2764/27128 layout (13 address lines)

The `pin_map` field (0x0015, 0x0016, etc.) is a separate index into the TL866's internal physical pin-routing table and is distinct from `variant`. On the TL866, one `pin_map` ID can cover multiple logical layouts because the hardware does pin remapping in its shift registers.

---

## 2. How Other Open-Source EPROM Programmers Handle Algorithm Selection

### TommyPROM (tomnisbet/TommyPROM)

**Architecture**: Compile-time single-device selection using a C++ class hierarchy.

**Class hierarchy**:
```
PromDevice (base class — common read/write loop, shift-register addressing)
  PromDevice28C  — 28Cxxx EEPROM (byte write, SDP unlock, block write)
  PromDevice27   — 27-series parallel EPROM (multiple sub-algorithms)
  PromDeviceSST39SF — SST39SF Flash (sector erase, software ID)
  PromDeviceSST28SF — SST28SF Flash
  PromDevice8755A   — Intel 8755A (multiplexed bus)
  PromDevice23      — 23-series ROM (read-only)
```

**Selection mechanism**: `Configure.h` uses `#define PROM_IS_28C` / `#define PROM_IS_27` etc. Only ONE subclass is compiled into the binary. No runtime dispatch — the `PromDevice` instance IS the algorithm. This conserves limited Arduino RAM.

**PromDevice27 sub-algorithms**: The 27-series driver has an internal `E27C_PGM` enum:
- `E27C_PGM_WE` — dedicated active-low WE pin (e.g. SST27SF020 flash)
- `E27C_PGM_CE` — CE-pulse programming (M27256, M27C256)
- `E27C_PGM_D13` — VPP controlled via Arduino pin D13 (W27C512 — 12V on OE pin)

These are set at construction time, not dispatched at runtime. The correct sub-variant is selected by the developer at compile time.

**Wire protocol**: XMODEM-based file transfer over serial. No JSON. The host requires no special client software — any XMODEM-capable terminal works. Commands are single-character prompts.

**Key lesson for Firestarter**: TommyPROM proves that for an embedded-constrained system, compile-time selection is viable, but it limits a single firmware to one chip family. Firestarter's approach of runtime dispatch via `mem_type` from JSON is more flexible but requires the host to carry the dispatch logic.

### open-tl866 (JohnDMcMaster/open-tl866)

**Architecture**: Mode-per-firmware approach. Different chip families are separate firmware images.

- `tl866-bitbang` firmware: generic pin-control via ASCII serial; all logic on the Python host.
- `tl866-at89` firmware: specialized for AT89S Atmel MCU.

**Wire protocol**: ASCII single-letter commands (`z val` for pin write, `Z` for pin read). Voltage selection and pin tristate commands. This is a pure "bit-bang from host" model — the firmware has zero chip knowledge; all sequencing happens in the Python library.

**Key lesson for Firestarter**: The bitbang-from-host approach has maximum flexibility but suffers from serial latency limiting programming speed. Firestarter's pull-based data model (firmware requests chunks) is a better hybrid.

### RURP (AndersBNielsen/Relatively-Universal-ROM-Programmer)

The RURP is Firestarter's hardware platform. Its original sketch implements:
- Chip ID reading, blank check, erasure (14V), variable-pulse write (1–255ms or 100µs steps)
- 6502 assembly routines for timing-critical pulse sequences
- No formal algorithm dispatch — the original firmware targets one chip family per build variant

Firestarter is a third-party ecosystem layered on top of the RURP hardware that implements proper multi-chip runtime dispatch.

### Matt Millman's HV-EPROM Programmer

For vintage 24-pin high-voltage EPROMs (2704, 2708, TMS2716):
- Separate hardware architecture for 21V/25V Vpp, 12V Vcc chips
- No universal dispatch — dedicated hardware for each chip generation
- Programming algorithm is hard-coded per chip type in firmware

**Key lesson**: Vintage EPROMs (the EPROM_LEGACY group) require distinct hardware support. They cannot be treated as a sub-variant of 28-pin EPROMs.

---

## 3. Standard Approaches to Representing Programming Algorithms

### Approach A: Compile-Time Polymorphism (C++ Subclass Per Chip)

Used by: TommyPROM, open-tl866 (partially).

```cpp
class PromDevice { virtual void burnByte(...) = 0; };
class PromDevice28C : public PromDevice { ... };
class PromDevice27  : public PromDevice { ... };
// Only one is compiled in
```

**Pros**: Zero flash/RAM overhead from unused algorithms; C++ vtable dispatch is well understood.
**Cons**: One chip family per flash. Requires re-flashing to switch chip families.

### Approach B: Runtime Function-Pointer Table (C Strategy Pattern)

Used by: **Firestarter** (current architecture).

```c
typedef struct firestarter_handle {
    void (*firestarter_operation_init)(struct firestarter_handle*);
    void (*firestarter_operation_main)(struct firestarter_handle*);
    void (*firestarter_operation_end)(struct firestarter_handle*);
    void (*firestarter_set_data)(...);
    uint8_t (*firestarter_get_data)(...);
    void (*firestarter_set_address)(...);
    void (*firestarter_set_control_register)(...);
    bool (*firestarter_get_control_register)(...);
} firestarter_handle_t;
```

The `configure_memory()` function acts as the factory/dispatcher:
1. Receives `mem_type` from the host's JSON command.
2. Switches on `mem_type` to call `configure_eprom()`, `configure_flash3()`, `configure_flash4()`, `configure_sram()`.
3. Each `configure_*` function populates the handle's function pointers for that algorithm family.
4. Within each family, a further switch on `cmd` (READ/WRITE/ERASE/etc.) assigns the correct operation function pointers.

**Current mem_type constants** (firestarter/src/proms/memory.cpp):
```c
#define TYPE_EPROM        1  // All parallel EPROM variants (0x07, 0x08, 0x0B)
#define TYPE_FLASH_TYPE_2 2  // (not yet implemented separately)
#define TYPE_FLASH_TYPE_3 3  // AMD/SST-style Flash (0x05, 0x06)
#define TYPE_SRAM         4  // SRAM (0x28)
#define TYPE_FLASH_TYPE_4 5  // Intel-style Flash (0x10)
```

**Observation**: Currently, protocol_ids 0x07, 0x08, and 0x0B are ALL mapped to `TYPE_EPROM=1`. They all run through the same `eprom.cpp` algorithm. The pulse timing differences between EPROM_STD and EPROM_QUICK are absorbed by the `pulse_delay` parameter sent from the host, and the write algorithm adaptively retries.

**Pros**: Universal firmware; all algorithms coexist. Host controls dispatch. RAM overhead is a single handle struct; only one set of function pointers is active at a time.
**Cons**: More complex host-side protocol; host must carry chip knowledge.

### Approach C: Switch-Case Enum Dispatch (Flat)

Used by: Many small/simple Arduino programmers.

```c
switch (chip_type) {
    case CHIP_27C512: program_27C512(data, addr); break;
    case CHIP_28C256: program_28C256(data, addr); break;
    ...
}
```

**Pros**: Simple to read, no indirection.
**Cons**: Monolithic. All chip code compiled in regardless of use. Hard to extend without modifying the switch tree. Not used in any of the reviewed mature projects.

### Approach D: Bitbang-from-Host (All Logic on PC)

Used by: open-tl866 bitbang mode, various simple one-off hackers.

Firmware is a dumb pin controller. Python/host sends individual pin-set commands and implements the entire algorithm in software.

**Pros**: Maximum flexibility; no reflash needed for new chips.
**Cons**: Serial round-trip latency per pin change. Unacceptable speed for large EPROMs. ~50–500x slower than on-device sequencing.

---

## 4. Pinout vs. Algorithm Separation

This is the central design question for Firestarter's architecture.

### The Problem

Two chips may share the same programming algorithm but have different physical pin layouts, OR they may share a physical package but use different algorithms. Examples:

- AT27C512@DIP28 and AM27512@DIP28 → same algorithm (EPROM_STD), same physical pinout → same `pinout_key = "DIP28_27512"`
- W27C512@DIP28 → different algorithm (VPP on OE pin, not PGM pin) but identical physical DIP28 package → needs different `pinout_key` or additional flag
- 27256@DIP28 vs 27512@DIP28 → same algorithm family, but A15 is present on 27512 and NC on 27256 → different `pinout_key`

### How minipro Separates Them

minipro uses THREE independent axes:
1. `protocol_id` — the algorithm family
2. `variant` — sub-variant of the algorithm (often encodes address bus width)
3. `pin_map` (index) — physical pin routing on the TL866 ZIF adapter hardware

For EPROM_STD (0x07) with DIP28:
- variant=0x10 → 27512 (16 address lines, A15 on pin 1/Vpp shared with OE/CE)
- variant=0x11 → 27256 (15 address lines)
- variant=0x13 → 2764/27128 (13-14 address lines)
- variant=0x00 for 2764

### How Firestarter Currently Separates Them

Firestarter uses a two-axis system:

**Axis 1: `mem_type` (sent in JSON) → selects firmware algorithm family**
Derived from `protocol_id` by the Python host via `PROTOCOL_MAP`:
```python
PROTOCOL_MAP = {
    0x07: "EPROM_STD",
    0x08: "EPROM_QUICK",
    0x0B: "EPROM_LEGACY",
    0x05: "FLASH_AMD_STD",
    0x06: "FLASH_AMD_ALT",
    0x10: "FLASH_INTEL",
    0x28: "SRAM_STD",
    ...
}
```
Then `determined_type` maps algorithm names to type integers sent to firmware:
```python
if "Flash" in type_str:
    determined_type = 2  # generic Flash → will route to flash3 or flash4
elif "SRAM" in type_str:
    determined_type = 4
# else default 1 (EPROM)
```
**Current gap**: EPROM_STD, EPROM_QUICK, and EPROM_LEGACY all map to `determined_type=1`. The firmware cannot currently distinguish them.

**Axis 2: `bus-config` (sent in JSON) → hardware pin routing**
The Python host translates a named `pinout_key` (e.g., `"DIP28_27512"`) into a hardware-specific `bus-config` object by:
1. Looking up the pinout in `pinouts.json` → gets the list of JEDEC physical pin numbers for address/data/CE/OE/VPP lines.
2. Converting JEDEC pin numbers to RURP hardware bus lines using `pin_conversions` (a hardcoded table in `database.py`).
3. Sending the resulting `bus-config` dict in the JSON command.

The firmware's `mem_util_remap_address_bus()` function uses `bus_config_t.address_lines[]` to reorder address bits to match the physical DIP layout.

**Pinout library** (`firestarter_app/firestarter/data/pinouts.json`):
```json
{
  "DIP28_27512": {
    "name": "JEDEC 27512",
    "pins": {
      "address-bus-pins": [10,9,8,7,6,5,4,3,25,24,21,23,2,26,27,1],
      "data-bus-pins":    [11,12,13,15,16,17,18,19],
      "ce-pin": [20],
      "oe-pin": [22],
      "vpp-pin": [22]
    }
  }
}
```

Note: For 27512, OE and VPP share pin 22 — VPP is applied to the OE pin during programming. This is physically distinct from 27256 where VPP is on pin 1.

**Pinout inference from variant** (in `parse_db_2.py`):
```python
def resolve_pinout_key(pin_count, variant, flags_int):
    if pin_count == 28:
        if variant == 16:   return "DIP28_27512"
        if variant == 17:   return "DIP28_27256"
        return "DIP28_2764"
    if pin_count == 24:
        if variant == 1:    return "DIP24_2732"
        return "DIP24_2716"
    if pin_count == 32:
        return "DIP32_STD"
```

This is the bridge between minipro's `variant` field and Firestarter's named pinout keys.

### Architectural Assessment

The current pinout/algorithm separation is clean for the common cases but has a latent gap: **all three EPROM algorithm variants (EPROM_STD, EPROM_QUICK, EPROM_LEGACY) arrive at the firmware as `type=1`**. The firmware's `eprom.cpp` must handle all of them with a single code path, relying entirely on `pulse_delay` and `vpp_mv` from the host to drive correct behavior.

This works for most chips because:
- EPROM_QUICK uses shorter pulses (adaptive retry compensates)
- EPROM_STD uses medium pulses (200µs typical)
- EPROM_LEGACY (2716/2732) uses very long pulses (50ms) — this is sent as `pulse_delay`

The implicit assumption is that the timing parameters fully specify the algorithm. This is fragile for edge cases like:
- Chips requiring specific VPP sequencing (VPP before CE, etc.)
- Chips requiring the PGM pin pulsed vs. CE pulsed
- The 2716 which requires VCC=5V but VPP=25V with OE held low during programming

---

## 5. Wire Protocol Formats for Arduino-Based Programmers

### Firestarter's Current Protocol

JSON-over-serial at 250000 baud. Two distinct protocol layers:

**Layer 1 — Command/Init phase**: Host sends a JSON object; firmware responds with an `OK:` line.
```json
{
  "cmd": 2,
  "type": 1,
  "memory-size": 65536,
  "pin-count": 28,
  "vpp": 12500,
  "pulse-delay": 100,
  "chip-id": 7693,
  "flags": 0,
  "bus-config": {
    "bus": [10,9,8,7,6,5,4,3,25,24,21,23,2,26,27,1],
    "oe-pin": 257,
    "vpp-pin": 257
  }
}
```

**Layer 2 — Data phase** (pull model): Firmware requests data chunks via `OK: Req data`. Host sends raw binary chunk. Firmware acknowledges `OK:` and requests next. This provides flow control without hardware RTS/CTS.

Response prefix scheme:
- `OK: ...` — acknowledgment
- `DATA: ...` — progress data (e.g., blank-check progress)
- `ERROR: ...` — error with message
- `WARN: ...` — non-fatal warning
- Raw binary — data payload for read operations

**Design rationale vs. alternatives**:
- JSON allows the host to send rich chip configuration without firmware-side parsing tables
- The pull model is essential because Arduino RAM (512 bytes on Uno) cannot buffer a full EPROM image
- 250000 baud was chosen for ~25KB/s throughput — at 100µs programming pulse, this is close to maximum useful speed

### Comparison with Other Protocols

| Project        | Protocol      | Direction    | Chip Knowledge Location |
|---------------|---------------|--------------|------------------------|
| TommyPROM      | XMODEM binary | Push (host→device) | Firmware (compile-time) |
| open-tl866     | ASCII pin-cmds| Push (host→device) | Python host (all logic) |
| minipro/TL866  | Binary USB HID| Push (host→device) | TL866 proprietary FW   |
| Firestarter    | JSON + binary | Pull (device requests) | Split: type on host, algorithm on firmware |
| Erik van Zijst | ASCII commands| Push | Firmware (fixed chip)  |

### Key Design Tradeoffs

**JSON overhead**: Parsing JSON on Arduino with `jsmn` adds ~200–400 bytes RAM and ~2ms latency per command. This is paid once per operation, not per byte programmed. Acceptable.

**Protocol type encoding**: Firestarter currently sends `type` (integer 1–5) not `protocol_id`. This means the firmware cannot distinguish EPROM_STD from EPROM_QUICK — it must rely on timing parameters. If future algorithm divergence is needed (e.g., 2716 needs special VPP sequencing), either a new `type` value or a sub-type field would be needed.

**Bus config in wire protocol**: Sending the full address bus remapping as a JSON array per command is verbose (~100 bytes) but allows the single firmware to support any physical pinout without a firmware-side pinout table. This is the correct architecture for a "relatively universal" programmer.

---

## 6. Key Findings Summary for Firestarter Design

### What minipro teaches us

1. `protocol_id` in infoic.xml is an algorithm family identifier, NOT a full algorithm specification. Additional parameters (variant, voltages, pulse_delay, flags) complete the algorithm.
2. The `pin_map` / physical pinout is a SEPARATE concern from `protocol_id`. Same algorithm can have multiple physical pin layouts (DIP vs PLCC, 27256 vs 27512).
3. There are approximately 6–8 distinct algorithm families relevant to Firestarter's target chips (EPROM_STD, EPROM_QUICK, EPROM_LEGACY, FLASH_AMD_STD, FLASH_AMD_ALT, FLASH_INTEL, SRAM_STD, EEPROM_POLL).

### What TommyPROM teaches us

1. For memory-constrained firmware, compile-time selection of a single chip family is viable but limits universality.
2. Even within one EPROM family (27-series), there are 3 distinct sub-algorithms that benefit from separate code paths (CE-pulse, WE-pulse, OE-voltage).
3. The strategy pattern (one class = one algorithm variant) is cleaner than a large switch-case.

### What the current Firestarter architecture does well

1. **Function-pointer handle struct** is the right pattern for C-based runtime algorithm dispatch on Arduino.
2. **JSON commands** correctly separate chip knowledge (host) from timing-critical operations (firmware).
3. **Pull-based data protocol** correctly handles Arduino RAM limitations.
4. **Pinout-as-bus-config** correctly separates physical pin layout from algorithm.

### Current architectural gaps

1. **EPROM sub-algorithm not conveyed to firmware**: EPROM_STD (0x07), EPROM_QUICK (0x08), and EPROM_LEGACY (0x0B) all send `type=1`. The firmware has no way to know if a chip needs 25V VPP (2716) vs 12.5V (27C512). Currently this relies on `vpp` in the JSON and the `FLAG_VPE_AS_VPP` flag.
2. **VPP pin location not always in bus-config**: For 27512, VPP is on pin 22 (shared OE/VPP). For 27256, VPP is on pin 1. The firmware's `using_p1_as_vpp()` check handles this implicitly, but the mechanism is not obvious.
3. **EPROM_LEGACY timing**: The 2716/2732 require 50ms pulses. The `pulse_delay` field handles this, but the database parser currently sets `pulse-delay: 0` for the new DB format — these chips would fail to program.

### Recommended direction

If the goal is to add explicit algorithm dispatch on the firmware side:
1. Add a new `protocol` field to the JSON wire protocol (a small integer, distinct from `mem_type`).
2. Map: `EPROM_STD=0x07`, `EPROM_QUICK=0x08`, `EPROM_LEGACY=0x0B` as separate constants.
3. In `configure_eprom()`, switch on `handle->protocol` to select between `eprom_std_write`, `eprom_quick_write`, `eprom_legacy_write` function implementations.
4. `mem_type` stays as the coarse dispatcher (EPROM vs Flash vs SRAM); `protocol` becomes the fine-grained algorithm selector within a mem_type group.

This mirrors how minipro itself works: `type` selects the hardware interface category; `protocol_id` selects the exact algorithm within that category.

---

## References

- minipro source: https://gitlab.com/DavidGriffith/minipro
- infoic.xml (local copy): `firestarter_app/tools/infoic.xml`
- TommyPROM: https://github.com/TomNisbet/TommyPROM / https://tomnisbet.github.io/TommyPROM
- open-tl866: https://github.com/JohnDMcMaster/open-tl866
- RURP hardware: https://github.com/AndersBNielsen/Relatively-Universal-ROM-Programmer
- Firestarter app (Python): `firestarter_app/firestarter/database.py` — PROTOCOL_MAP, pin_conversions, EpromDatabase
- Firestarter firmware (C++): `firestarter/src/proms/memory.cpp` — configure_memory(), mem_type constants
- Firestarter firmware (C++): `firestarter/src/proms/eprom.cpp` — configure_eprom(), write algorithm
- DB parser (protocol_id → algorithm name): `firestarter_app/tools/parse_db_2.py` — PROTOCOL_MAP, resolve_pinout_key()
- Pinout library: `firestarter_app/firestarter/data/pinouts.json`
