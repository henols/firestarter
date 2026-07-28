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

Generated outputs are ELF, BIN, HEX, linker map and size report, all under
`build/py32f071/`. Only `firestarter_py32f071.hex` is ever published — the rest
are dev-environment artefacts, reproducible with the two commands above, and CI
does not upload them.

The underscore in `firestarter_py32f071.*` is load-bearing. The host installer
resolves release assets by the name `firestarter_<board>.hex`, where `<board>` is
the `RURP_BOARD_NAME` the firmware reports over the wire (`py32f071`), so the
CMake `TARGET_NAME` matches the convention `name_firmware.py` applies to the AVR
targets. It also means `beta-build.yml`'s existing `firestarter_*.hex` release
glob needs no new pattern.

## Release integration

`py32f071.yml` builds and validates this target on pull requests but does **not**
cut releases, for one hard reason: `beta-build.yml` runs
`.github/scripts/update_version.py`, which rewrites `include/version.h` and
auto-commits it, *before* building. An image built in any other job compiles a
stale `VERSION` string, and the host's whole update decision is a comparison of
that string against the release tag. So the PY32F071 image has to be built in the
same job as the AVR images, after the version bump.

Folding it in is three steps and one line. In `beta-build.yml`, after
`Build PlatformIO Project`:

```yaml
      - name: Install GNU Arm toolchain
        run: |
          sudo apt-get update
          sudo apt-get install -y cmake ninja-build gcc-arm-none-eabi binutils-arm-none-eabi

      - name: Configure PY32F071
        run: cmake -S platform/py32f071 -B build/py32f071 -G Ninja -DCMAKE_BUILD_TYPE=Release

      - name: Build PY32F071
        run: cmake --build build/py32f071
```

and in the existing `Release` step, extend `files:` with a **glob**, not a literal
path:

```yaml
          files: |
            .pio/build/**/firestarter_*.hex
            build/py32f071/firestarter_py32f071.hex
```

Two deliberate choices worth keeping when that fold happens:

- **A glob, not a literal filename.** `softprops/action-gh-release` warns on a
  glob that matches nothing but fails on a missing literal file. While this port
  is unproven, a broken ARM build must not block the AVR beta release — the
  py32 asset should simply be absent.
- For the same reason, consider `continue-on-error: true` on the three ARM steps
  until the target has been validated on real silicon. Remove it once it has.

## Hardware validation still required

Before connecting a PROM or applying programming voltage, validate the startup levels, complete `0x00`-`0xFF` data mapping, bus direction changes, every logical control signal, USB framing, voltage readings, and all PROM timing with appropriate test equipment. The provisional pin map is for compilation and early bring-up only.
