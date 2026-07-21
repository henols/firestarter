# Firestarter on PY32F071

This target builds the existing Firestarter PROM algorithms and command protocol with a native PY32F071 hardware backend.

## Implemented

- native CMake/Ninja GNU Arm build
- pinned official Puya PY32F071 SDK
- PY32F071 CMSIS startup and interrupt vector
- C and C++ runtime initialization
- 48 MHz clock configuration required by native USB
- CherryUSB CDC transport without `SERIAL_ON_IO`
- SysTick millisecond timing
- TIM3 microsecond delays
- safe active-low `/CE` and `/OE` startup levels
- logical-control-to-physical-GPIO translation
- contiguous eight-bit GPIO data bus
- one-snapshot data reads through `IDR`
- atomic data writes through `BSRR`
- 12-bit ADC voltage measurement using VREFINT compensation
- optional active-low user button support
- unchanged shared PROM algorithms and packet framing

## Provisional example pin map

The implementation guide marks its GPIO values as examples, and no final PY32F071 Firestarter schematic or pin assignment is present in the repository or supplied documents. To allow the target to compile and evolve before the PCB mapping is finalized, the board header now contains this explicitly provisional example:

| Signal | Example PY32F071 pin |
|---|---|
| PROM D0-D7 | PB0-PB7 |
| LSB address-latch strobe | PA0 |
| MSB address-latch strobe | PA1 |
| `/OE` | PA2 |
| Control-register latch strobe | PA3 |
| VPP measurement | PA4 / ADC channel 4 |
| `/CE` | PA5 |
| User button | Not fitted |

PA4 / ADC channel 4 follows the official Puya PY32F071 ADC example. All other assignments are placeholders selected for a simple contiguous bus and must not be treated as verified PCB wiring.

The single physical mapping point is:

```text
include/boards/py32f071_rurp_shield.h
```

The header defines:

```cpp
#define RURP_PY32F071_PINMAP_PROVISIONAL 1
```

Replace the mapping and remove or clear that marker when the final schematic is available.

## Build

```sh
cmake -S platform/py32f071 -B build/py32f071 -G Ninja \
  -DCMAKE_BUILD_TYPE=Release
cmake --build build/py32f071
```

Generated outputs are ELF, BIN, HEX, linker map, size report, and SHA-256 checksums.

## Hardware validation still required

Before connecting a PROM or applying programming voltage, validate the startup levels, complete `0x00`-`0xFF` data mapping, bus direction changes, every logical control signal, USB framing, voltage readings, and all PROM timing with appropriate test equipment. The provisional pin map is for compilation and early bring-up only.
