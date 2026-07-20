# PY32F071 Firestarter port

This directory tracks the PY32F071-only implementation of the work described by:

- `henols/firestarter_prom#16` — generic HAL/platform cleanup
- `henols/firestarter_prom#17` — native PY32F071 backend

RP2040/RP2350 and STM32 Black Pill targets are explicitly out of scope for this port.

## Target

- PY32F071xB
- Cortex-M0+
- 128 KiB flash
- 16 KiB SRAM
- Native, non-Arduino firmware
- Native USB CDC
- Internal 12-bit ADC and 12-bit DAC

## Architecture

Common Firestarter code must depend only on the logical HAL. The PY32F071 backend owns all Puya CMSIS, LL, HAL and CherryUSB dependencies.

```text
PROM algorithms and command processing
                |
        Firestarter logical HAL
                |
          PY32F071 backend
                |
     CMSIS / LL / CherryUSB / registers
```

## Required common abstractions

### Platform identification and AVR compatibility

Add a common platform header that:

- defines `RURP_PLATFORM_PY32F071`
- keeps Uno, ATmega328PB, Leonardo and native-test identifiers
- prevents common headers from unconditionally including `<avr/pgmspace.h>`
- maps flash-string helpers to ordinary memory-mapped constants on PY32F071
- keeps physical pin definitions out of common headers

### Timing

Common code must use:

```cpp
uint32_t rurp_millis();
void rurp_delay_ms(uint32_t milliseconds);
void rurp_delay_us(uint32_t microseconds);
```

PY32F071 implementation:

- SysTick at 1 kHz for milliseconds
- hardware timer for microseconds
- timer one-pulse mode where programming pulse accuracy requires it
- no long global interrupt masking because USB must continue to run

### Communication

Provide transport-neutral implementations for the existing communication API.

The PY32F071 implementation uses the official Puya CherryUSB device port and CDC class. It must preserve the current Firestarter framing protocol.

`SERIAL_ON_IO` must not be defined. Uno UART/data-bus switching and the Uno deferred-log queue are not part of this backend.

### Configuration storage

AVR continues to use EEPROM. PY32F071 uses internal flash with two independently validated records:

```cpp
struct StoredConfiguration {
    uint32_t magic;
    uint16_t version;
    uint16_t length;
    rurp_configuration_t configuration;
    uint32_t sequence;
    uint32_t crc32;
};
```

The newest valid sequence is loaded. A failed or interrupted write must leave the previous record usable.

## PY32F071 backend modules

```text
platform/py32f071/
  include/
    py32f071_board.h
    py32f071_pins.h
  src/
    main.cpp
    board.cpp
    gpio.cpp
    timing.cpp
    usb.cpp
    adc.cpp
    dac.cpp
    storage.cpp
```

### Board setup

Startup order:

1. Initialize clocks and SysTick.
2. Configure the data bus as high-impedance input.
3. Set all control outputs to safe inactive states.
4. Disable the target chip and output enable.
5. Clear address and control registers.
6. Initialize ADC and DAC with VPP disabled.
7. Load validated flash configuration.
8. Start native USB CDC.

### GPIO data bus

Prefer one contiguous eight-bit GPIO port region.

- one `IDR` snapshot per data read
- one atomic `BSRR` operation per data write
- `MODER` changes preserve unrelated pins
- no pull-up or pull-down while the PROM drives the bus

Logical control identifiers remain common and are translated to physical PY32 pins only in `gpio.cpp`.

### ADC measurement

The backend must:

1. sample VREFINT
2. estimate actual analog supply voltage
3. sample the external VPP divider
4. calculate uncalibrated VPP
5. apply the common two-point board calibration
6. average/filter enough samples to reject boost-converter ripple

The complete divider and ADC path is calibrated against an external meter. AVR and PY32F071 share the same calibration model.

### DAC VPP control

PY32F071 defines the compile-time DAC capability and implements the common VPP control hooks.

The DAC supplies a feed-forward starting value. The calibrated ADC closes the loop and adjusts the DAC until VPP is within the algorithm-specific tolerance.

Required protection:

- regulator enable defaults off
- DAC resets to zero
- maximum target and separate overvoltage safety threshold
- timeout
- saturated DAC code rather than integer wraparound
- independent hardware shutdown where practical

## Build and dependency policy

The build uses native CMake and `arm-none-eabi-gcc`.

The official Puya SDK must be pinned to a known commit. Required SDK areas include:

- `Drivers/CMSIS`
- `Drivers/CMSIS/Device/PY32F071`
- selected PY32F071 HAL/LL headers and sources
- CherryUSB core, CDC class and `usb_dc_py32.c`

The SDK should be fetched reproducibly by CMake or CI rather than copied without version tracking.

Build products:

- `firestarter-py32f071.elf`
- `firestarter-py32f071.bin`
- `firestarter-py32f071.hex`
- linker map
- size report
- SHA-256 checksums

## Acceptance checklist

- [ ] Official PY32F071 interrupt vector layout is used.
- [ ] The native smoke target compiles and links.
- [ ] CI uploads ELF, BIN and HEX files.
- [ ] Common headers compile without AVR headers on PY32F071.
- [ ] Existing PROM algorithms compile unchanged.
- [ ] GPIO bus backend uses one read snapshot and atomic writes.
- [ ] Native CherryUSB CDC passes Firestarter framing tests.
- [ ] Arduino timing calls are removed from common code.
- [ ] VREFINT-compensated ADC measurement works.
- [ ] Common two-point voltage calibration works on AVR and PY32F071.
- [ ] Closed-loop DAC VPP regulation works.
- [ ] Flash-backed configuration survives interrupted writes.
- [ ] Uno, ATmega328PB, Leonardo and native tests remain green.
- [ ] Real hardware reads and programs a representative device.
