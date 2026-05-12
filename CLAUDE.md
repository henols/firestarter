# CLAUDE.md — Firestarter Firmware

Arduino C++ firmware for the Firestarter EPROM programmer. Built with PlatformIO.

## Build Commands

```bash
pio run -e uno          # build for Arduino Uno
pio run -e leonardo     # build for Arduino Leonardo
pio run -t upload -e uno   # flash to board
pio test                # run unit tests (all envs)
pio test -e native      # run host-side dispatch tests (no hardware needed)
pio test -e native -f "*test_dispatch*"   # run only the configure_memory dispatch suite
```

## Architecture

### Protocol Dispatch

The firmware dispatches on `handle->protocol` (populated from the `algorithm`
JSON field) **before** dispatching on `handle->mem_type`. This is critical:
many chip families have `mem_type=1` (TYPE_EPROM) in the database but require
dedicated handlers (e.g. SRAM chips with `mem_type=1` MUST NOT reach
`configure_eprom` — that would enable the 12V VPP boost regulator on a 5V part).

The protocol-prefix chain covers every entry in `KNOWN_PROTOCOLS` (`0x05, 0x06,
0x07, 0x08, 0x0B, 0x0D, 0x0E, 0x10, 0x27, 0x28, 0x29, 0x35, 0x39`). The
`mem_type` chain is retained as a backward-compatibility fallback for
hand-crafted JSON commands or older host versions that omit `algorithm`; for any
chip emitted by the regenerated `chip_database.json` the protocol-prefix
chain always fires first.

Dispatch order in `memory.cpp:configure_memory` (source-of-truth — must match
`firestarter/src/proms/memory.cpp` line-for-line):

1. `protocol == 0x10` → `configure_flash_intel()` — Intel 28F command-register flash
2. `protocol == 0x0D` → `configure_eeprom28c()` — AT28C-series 5V EEPROM with page write
3. `protocol == 0x06` → `configure_flash3()` — AMD unlock flash (sector erase)
4. `protocol ∈ {0x05, 0x35, 0x39}` → `configure_flash4()` — page-write flash (0x39 future-proofed, no chips in current DB)
5. `protocol ∈ {0x07, 0x08, 0x0B}` → `configure_eprom()` — UV-EPROM family
6. `protocol ∈ {0x0E, 0x27, 0x28, 0x29}` → `configure_sram()` — SRAM/NVRAM (BLOCKER-2 mitigation: never reaches VPP regulator)
7. `mem_type == TYPE_EPROM (1)` → `configure_eprom()` — fallback for backward compatibility with hand-crafted JSON
8. `mem_type == TYPE_SRAM (4)` → `configure_sram()` — fallback
9. `mem_type == TYPE_FLASH_TYPE_3 (3)` → `configure_flash3()` — fallback
10. `mem_type == TYPE_FLASH_TYPE_4 (5)` → `configure_flash4()` — fallback
11. error: `firestarter_error_response_format("Memory type 0x%02x not supported", handle->mem_type)`

There is no `mem_type == 2` dispatch case (the orphan `#define` was removed
from `memory.cpp` during Phase 12). Any chip with `algorithm == 0` and an
unrecognized `mem_type` reaches step 11.

### Algorithm Handlers

| Protocol               | Name           | File              | VPP             | Notes                                                        |
|------------------------|----------------|-------------------|-----------------|--------------------------------------------------------------|
| 0x07                   | EPROM_STD      | eprom.cpp         | 13V VPE_TO_VPP  | 1ms pulse, DQ7 verify                                        |
| 0x08                   | EPROM_QUICK    | eprom.cpp         | 13V VPE_TO_VPP  | 100µs pulse                                                  |
| 0x0B                   | EPROM_LEGACY   | eprom.cpp         | 12–18V direct   | 500µs pulse, 24-pin                                          |
| 0x0D                   | EEPROM_POLL    | eeprom_28c.cpp    | None (5V)       | SDP disable + DQ7 page poll                                  |
| 0x0E / 0x27 / 0x28 / 0x29 | SRAM_*       | sram.cpp          | None (5V)       | Generic read/write; no VPP regulator (BLOCKER-2 mitigation)  |
| 0x06                   | FLASH_AMD_ALT  | flash_type_3.cpp  | None (5V)       | AMD unlock, sector erase                                     |
| 0x05                   | FLASH_AMD_STD  | flash_type_4.cpp  | None (5V)       | Page write + DQ7                                             |
| 0x35                   | FLASH_EEPROM   | flash_type_4.cpp  | None (5V)       | Page write + DQ7                                             |
| 0x39                   | FLASH_EEPROM2  | flash_type_4.cpp  | None (5V)       | Future-proofed (0 chips in current DB; dispatched by analogy with 0x35) |
| 0x10                   | FLASH_INTEL    | flash_intel.cpp   | 12V P1_VPP      | Command register, SR polling                                 |

### JSON Wire Protocol

The firmware receives JSON commands over serial at 250000 baud. The `algorithm` field (integer, upstream `protocol_id`) is parsed into `handle->protocol` and is the primary dispatch key.

Key fields:
- `algorithm` — integer protocol ID, stored in `handle->protocol`
- `type` — legacy `mem_type` integer (fallback when algorithm is absent)
- `vpp_mv` — VPP voltage in millivolts (used by SAF-04 ADC validation)
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

## Native (Host) Test Environment

The dispatch logic in `configure_memory` is exercised by Unity tests that run
on the host via PlatformIO's `platform = native`. No AVR board is needed.

### Invocation

```bash
pio test -e native                          # run every native suite
pio test -e native -f "*test_dispatch*"     # run only configure_memory dispatch tests
```

### Layout

```
firestarter/
├── platformio.ini                          # [env:native] section: platform=native, test_framework=unity,
│                                           # src_filter = +<proms/>, test_build_src = yes,
│                                           # -D RURP_BOARD_NAME=\"native\"
└── test/
    └── native/
        └── avr/
            └── test_dispatch/
                ├── test_configure_memory.cpp   # Unity RUN_TEST cases — one per KNOWN_PROTOCOLS entry
                ├── host_stubs.cpp              # no-op replacements for rurp_* symbols + LOG_*_MSG PROGMEM strings
                └── avr/
                    └── pgmspace.h              # host shim for AVR PROGMEM macros (incl. PGM_P)
```

### Why a host stub TU?

`[env:native]` cross-compiles `src/proms/*.cpp` (the dispatch + handler TUs)
against host libc + ArduinoFake. The AVR-only TUs (`src/boards/*.cpp`,
`src/dev_tools.cpp`, `src/eprom_operations.cpp`, `src/logging.c`) are excluded
by `src_filter = +<proms/>`. The handlers still reference `rurp_*` hardware
symbols (register writes, ADC reads, chip enable/disable) and the eight
`LOG_*_MSG` PROGMEM strings, so `host_stubs.cpp` provides minimal no-op
implementations that resolve the linker without touching real hardware. The
dispatch tests assert on `handle->firestarter_operation_main` and
`handle->response_code` only — never on register side effects — so the no-op
stubs are functionally complete for this test class.

The host shim at `test/native/avr/test_dispatch/avr/pgmspace.h` defines
`PROGMEM`, `PSTR`, `PGM_P`, and `pgm_read_*` as host-memory equivalents so
that headers including `<avr/pgmspace.h>` compile on a non-Harvard host.

### Reuse pattern for future native tests

To add a new host-side Unity suite, drop `test_*.cpp` files under
`test/native/avr/<dirname>/`. Extend `host_stubs.cpp` only if the new test
references additional `rurp_*` symbols. The `[env:native]` configuration in
`platformio.ini` does not need changes for new suites.
