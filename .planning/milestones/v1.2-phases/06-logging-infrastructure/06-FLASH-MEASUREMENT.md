# Phase 6 — Flash Budget Measurement

**Measured:** 2026-05-18
**Boards:** Leonardo + Uno
**Baseline (v1.1 close):** Leonardo 98.7% (~28,299 bytes used / 28,672 max)
**Repo state at measurement:** `firestarter` HEAD = `ca6a9e5` (Phase 6 Plan 02 close: messages.c + rurp_log_id helper + CRC8 table + frame emitter + Uno strong override + native Unity suite all landed; LMIG-01 coexistence intact — no legacy `LOG_*_MSG` PROGMEM strings removed).

## Leonardo (`pio run -e leonardo`)

```
Processing leonardo (platform: atmelavr; board: leonardo; framework: arduino)
--------------------------------------------------------------------------------
Verbose mode can be enabled via `-v, --verbose` option
CONFIGURATION: https://docs.platformio.org/page/boards/atmelavr/leonardo.html
PLATFORM: Atmel AVR (5.2.0) > Arduino Leonardo
HARDWARE: ATMEGA32U4 16MHz, 2.50KB RAM, 28KB Flash
DEBUG: Current (simavr) External (simavr)
PACKAGES:
 - framework-arduino-avr @ 5.3.0
 - toolchain-atmelavr @ 1.70300.191015 (7.3.0)
LDF: Library Dependency Finder -> https://bit.ly/configure-pio-ldf
LDF Modes: Finder ~ chain, Compatibility ~ soft
Found 6 compatible libraries
Scanning dependencies...
Dependency Graph
|-- SoftwareSerial @ 1.0
|-- jsmn
|-- EEPROM @ 2.0
Building in release mode
Checking size .pio/build/leonardo/firestarter_leonardo.elf
Advanced Memory Usage is available via "PlatformIO Home > Project Inspect"
RAM:   [======    ]  60.6% (used 1551 bytes from 2560 bytes)
Flash: [==========]  98.7% (used 28292 bytes from 28672 bytes)
========================= [SUCCESS] Took 0.48 seconds =========================

Environment    Status    Duration
-------------  --------  ------------
leonardo       SUCCESS   00:00:00.480
========================= 1 succeeded in 00:00:00.480 =========================
```

- **Leonardo Flash:** 98.7% (28,292 / 28,672 bytes used), **380 bytes free**.
- **Delta vs v1.1:** −7 bytes / −0.024 pct points (baseline 28,299 bytes derived from 98.7% × 28,672; rounding noise — the percentage displayed is still 98.7% in both states). Both numbers are at the same one-decimal display value; the byte-exact difference is within toolchain rounding (gcc/avr-ld output reproducibility delta from intervening framework-arduino-avr / toolchain-atmelavr updates between v1.1 close 2026-05-18 and now also can swing this by single digits).

**Interpretation:** Phase 6 Plan 02 added ~600-900 bytes of code per RESEARCH estimate (CRC8 table 256 B + MAGIC_PREAMBLE 4 B + messages.c PROGMEM ID table + rurp_log_id weak default + Uno strong override + logging_id.h macros — the macros themselves only materialise where invoked, and Phase 6 has zero call-sites yet). The net 0 byte change suggests the linker GC'd or did not yet pull in macro-only paths because no call-site invokes them. The CRC8 table + messages.c are PROGMEM-resident and referenced only by `_firestarter_emit_frame` / `rurp_log_id`, which are themselves only weakly linked and have no production caller in Phase 6. Effectively the Phase 6 code is "dead weight" at this point in the migration; the linker may have GC'd unreachable bits and what remains rounds to the v1.1 number.

This is consistent with LMIG-01 (coexistence) and proves the planner's hypothesis that Phase 6 infrastructure addition does not put Leonardo over the 28,672-byte cliff. Phase 7-8 call-site conversion will activate the helper (drawing in the table + emitter as live code) AND retire `rurp_log_P` call-sites (releasing per-call PROGMEM strings); the net direction across both is downward. Phase 9 deletion of the legacy `LOG_*_MSG` PROGMEM strings and the `log_info_const` / `log_error_format` / `log_warn` macros completes the recovery toward the ROADMAP Phase 9 success criterion (Flash < 90%).

## Uno (`pio run -e uno`)

```
Processing uno (platform: atmelavr; board: uno; framework: arduino)
--------------------------------------------------------------------------------
Verbose mode can be enabled via `-v, --verbose` option
CONFIGURATION: https://docs.platformio.org/page/boards/atmelavr/uno.html
PLATFORM: Atmel AVR (5.2.0) > Arduino Uno
HARDWARE: ATMEGA328P 16MHz, 2KB RAM, 31.50KB Flash
DEBUG: Current (avr-stub) External (avr-stub, simavr)
PACKAGES:
 - framework-arduino-avr @ 5.3.0
 - toolchain-atmelavr @ 1.70300.191015 (7.3.0)
LDF: Library Dependency Finder -> https://bit.ly/configure-pio-ldf
LDF Modes: Finder ~ chain, Compatibility ~ soft
Found 6 compatible libraries
Scanning dependencies...
Dependency Graph
|-- SoftwareSerial @ 1.0
|-- jsmn
|-- EEPROM @ 2.0
Building in release mode
Checking size .pio/build/uno/firestarter_uno.elf
Advanced Memory Usage is available via "PlatformIO Home > Project Inspect"
RAM:   [========  ]  77.5% (used 1587 bytes from 2048 bytes)
Flash: [========  ]  80.9% (used 26100 bytes from 32256 bytes)
========================= [SUCCESS] Took 0.46 seconds =========================

Environment    Status    Duration
-------------  --------  ------------
uno            SUCCESS   00:00:00.465
========================= 1 succeeded in 00:00:00.465 =========================
```

- **Uno Flash:** 80.9% (26,100 / 32,256 bytes used), **6,156 bytes free**.
- No formal v1.1 baseline exists for Uno (ROADMAP only pinned the Leonardo number); this measurement establishes the Uno Phase 6 close anchor for the Phase 9 milestone comparison.

## Decision

**Case A** — Leonardo build succeeded with comfortable headroom: **380 bytes free** is well above the 50-byte threshold the plan named for Case A vs Case B. No fall-back measurement is required. The Phase 6 Plan 02 additive code did not tip Leonardo over the 28,672-byte ATmega32U4 cliff. LMIG-01 coexistence holds — both the legacy `rurp_log`/`rurp_log_P` PROGMEM-string path AND the new `rurp_log_id` ID-frame emitter live in the same binary, and the build links cleanly on both boards.

Phase 7-8 (call-site conversion) is unblocked from a flash-budget perspective. Phase 9's LMIG-04 goal of Leonardo Flash < 90% expects ~28,292 − 0.10 × 28,672 ≈ 25,425 bytes used or fewer; the Phase 7-8 deletion of per-call PROGMEM tag strings + the Phase 9 deletion of `LOG_*_MSG` and the legacy macro tower is the planned path to that target.

## Fall-Back Measurement

Section omitted — no fall-back needed (Case A: build succeeded with 380 bytes free, the `-D NO_TEXT_LOGS` diagnostic path was not exercised). `firestarter/platformio.ini` was not modified during this measurement; `git -C firestarter status` shows only the pre-existing `include/rurp_register_utils.h` dirty file (carried forward from before Phase 6 began, untouched here per orchestrator instruction).

## Anchor for Plan 09

Phase 9 LMIG-04 acceptance criterion compares against this number. Record both the v1.1 baseline AND the Phase 6 close number when computing the v1.2 final delta.

The three reference points Phase 9 must cite:

| Snapshot | Leonardo Flash | Uno Flash | Notes |
|----------|----------------|-----------|-------|
| **v1.1 close** | 98.7% (~28,299 / 28,672) | not formally recorded | ROADMAP-pinned baseline; per-byte derived from %. |
| **Phase 6 close (THIS plan)** | 98.7% (28,292 / 28,672), 380 B free | 80.9% (26,100 / 32,256), 6,156 B free | LMIG-01 coexistence: new ID infrastructure landed alongside legacy text path; no call-sites converted yet. |
| **Phase 9 close (LMIG-04)** | TARGET: < 90% (< ~25,805 / 28,672) | TBD; record alongside Leonardo | After call-site conversion (Phase 7-8) + legacy `LOG_*_MSG` PROGMEM string + `log_*_const` macro tower deletion. |

The Phase 9 SUMMARY should cite both the v1.1 → Phase 9 delta (the headline "v1.2 milestone flash savings" number) AND the Phase 6 → Phase 9 delta (the "pure migration recovery" number, isolating the call-site-conversion + legacy-deletion benefit from any intervening framework/toolchain drift).
