# CLAUDE.md — Firestarter Firmware

Arduino C++ firmware for the Firestarter EPROM programmer. Built with PlatformIO.

## Build Commands

```bash
pio run -e uno          # build for Arduino Uno
pio run -e leonardo     # build for Arduino Leonardo
pio run -t upload -e uno   # flash to board
pio test                # run unit tests
```

## Architecture

### Protocol Dispatch

The firmware dispatches on `handle->protocol` (populated from the `algorithm` JSON field) **before** dispatching on `handle->mem_type`. This is critical: several chip families have `mem_type=1` (TYPE_EPROM) in the database but require dedicated handlers.

Dispatch order in `memory.cpp`:
1. `protocol == 0x10` → `configure_flash_intel()` — Intel 28F command-register flash
2. `protocol == 0x0D` → `configure_eeprom28c()` — AT28C-series 5V EEPROM with page write
3. `mem_type == TYPE_EPROM (1)` → `configure_eprom()` — UV-EPROM (0x07/0x08/0x0B)
4. `mem_type == TYPE_SRAM (4)` → `configure_sram()`
5. `mem_type == TYPE_FLASH_TYPE_3 (3)` → `configure_flash3()` — AMD unlock flash (0x06)
6. `mem_type == TYPE_FLASH_TYPE_4 (5)` → `configure_flash4()` — EEPROM-like flash (0x05, 0x35)

### Algorithm Handlers

| Protocol | Name           | File                  | VPP        | Notes |
|----------|----------------|-----------------------|------------|-------|
| 0x07     | EPROM_STD      | eprom.cpp             | 13V VPE_TO_VPP | 1ms pulse, DQ7 verify |
| 0x08     | EPROM_QUICK    | eprom.cpp             | 13V VPE_TO_VPP | 100µs pulse |
| 0x0B     | EPROM_LEGACY   | eprom.cpp             | 12–18V direct | 500µs pulse, 24-pin |
| 0x0D     | EEPROM_POLL    | eeprom_28c.cpp        | None (5V)  | SDP disable + DQ7 page poll |
| 0x06     | FLASH_AMD_ALT  | flash_type_3.cpp      | None (5V)  | AMD unlock, sector erase |
| 0x05     | FLASH_AMD_STD  | flash_type_4.cpp      | None (5V)  | Page write + DQ7 |
| 0x35     | FLASH_EEPROM   | flash_type_4.cpp      | None (5V)  | Page write + DQ7 |
| 0x10     | FLASH_INTEL    | flash_intel.cpp       | 12V P1_VPP | Command register, SR polling |

### JSON Wire Protocol

The firmware receives JSON commands over serial at 250000 baud. The `algorithm` field (integer, minipro `protocol_id`) is parsed into `handle->protocol` and is the primary dispatch key.

Key fields:
- `algorithm` — integer protocol ID, stored in `handle->protocol`
- `type` — legacy `mem_type` integer (fallback when algorithm is absent)
- `vpp` / `vpp_mv` — VPP voltage for ADC validation
- `memory-size` — chip size in bytes
- `pulse-delay` — write pulse width in µs (0 = use handler default)
- `chip-id` — expected manufacturer+device ID (0 = skip ID check)

### Key Files

- `src/json_parser.c` — parses JSON command into `firestarter_handle_t`; unknown fields silently skipped
- `src/proms/memory.cpp` — top-level dispatch (`configure_memory()`)
- `include/firestarter.h` — `firestarter_handle_t` struct definition
- `include/rurp_shield.h` — control register bit definitions (REGULATOR, VPE_TO_VPP, P1_VPP_ENABLE, etc.)

### Constants

Control register bits (from `rurp_shield.h`):
- `REGULATOR (0x80)` — enable VPP boost regulator
- `VPE_TO_VPP (0x01)` — drop VPE through resistor to VPP level
- `P1_VPP_ENABLE (0x08)` — route VPP to socket pin 1
- `A9_VPP_ENABLE (0x02)` — route VPP to A9 (for EPROM chip ID read)
- `VPE_ENABLE (0x04)` — apply VPE directly to PGM pin

Firmware flags (from `firestarter.h`):
- `FLAG_FORCE (0x01)` — treat ID mismatch as warning, not error
- `FLAG_CAN_ERASE (0x02)` — chip supports erase before write
- `FLAG_SKIP_ERASE (0x04)` — skip auto-erase in write init
- `FLAG_SKIP_BLANK_CHECK (0x08)` — skip blank check
- `FLAG_VPE_AS_VPP (0x10)` — legacy: direct VPE path (backward compat)
