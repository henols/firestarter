# PY32F071 native toolchain

This directory contains the native, non-Arduino build foundation for the PY32F071 Firestarter target.

## Current scope

The current target is a minimal Cortex-M0+ smoke firmware used to validate:

- `arm-none-eabi-gcc`
- CMake and Ninja integration
- the PY32F071 flash/RAM memory layout
- vector-table and reset startup
- ELF, BIN and HEX generation
- GitHub Actions artifact publishing

It does not yet include the full PY32F071 Firestarter board backend or the Puya peripheral SDK. Those sources can replace `src/main.c` and extend the CMake source list without changing the CI artifact contract.

## Build locally

```sh
cmake -S platform/py32f071 -B build/py32f071 -G Ninja \
  -DCMAKE_BUILD_TYPE=Release
cmake --build build/py32f071
```

Generated files:

```text
build/py32f071/firestarter-py32f071.elf
build/py32f071/firestarter-py32f071.bin
build/py32f071/firestarter-py32f071.hex
build/py32f071/firestarter-py32f071.map
```

## CI artifact

The `PY32F071 firmware` workflow publishes a GitHub Actions artifact containing:

- ELF
- raw BIN
- Intel HEX
- size report
- SHA-256 checksums

The workflow intentionally uploads an Actions artifact rather than committing generated binaries into Git history.

## Device assumption

The included linker script currently assumes a PY32F071 variant with:

- 128 KiB flash at `0x08000000`
- 16 KiB SRAM at `0x20000000`

Confirm and select the exact PY32F071 order code before using the output on hardware. The startup vector list must also be replaced or verified against the official Puya CMSIS device package before the target is treated as production firmware.
