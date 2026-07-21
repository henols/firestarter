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

## Required board wiring

The implementation guide marks its GPIO values as examples. No actual PY32F071 Firestarter schematic or pin assignment is present in the repository or supplied documents, so this target deliberately does not substitute guessed pins.

Set the actual mapping in:

```text
include/boards/py32f071_rurp_shield.h
```

The header lists every required definition and keeps the build disabled until:

```cpp
#define RURP_PY32F071_PINMAP_CONFIGURED 1
```

is set with the real values.

Required wiring information:

- one contiguous GPIO region for PROM D0-D7
- LSB address-latch strobe GPIO
- MSB address-latch strobe GPIO
- output-enable GPIO
- control-register latch strobe GPIO
- chip-enable GPIO
- VPP measurement ADC GPIO and channel
- optional user-button GPIO
- GPIO peripheral clocks used by those pins

## Build

```sh
cmake -S platform/py32f071 -B build/py32f071 -G Ninja \
  -DCMAKE_BUILD_TYPE=Release
cmake --build build/py32f071
```

Generated outputs are ELF, BIN, HEX, linker map, size report, and SHA-256 checksums.

## Hardware validation still required

After the real pin map is entered, validate the startup levels, complete `0x00`-`0xFF` data mapping, bus direction changes, every logical control signal, USB framing, voltage readings, and all PROM timing with appropriate test equipment before applying programming voltage to a device.
