<p align="left"><img src="https://raw.githubusercontent.com/henols/firestarter_app/refs/heads/main/images/firestarter_logo.png" alt="Firestarter EPROM Programmer" width="200"></p>

---
# Firestarter Firmware

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)


[![ko-fi](https://raw.githubusercontent.com/henols/firestarter_app/refs/heads/main/images/ko-fi.png)](https://ko-fi.com/E1E21I2WWW)

----
The Firestarter Firmaware is intedend to be used with the [Firestarter application](https://github.com/henols/firestarter_app) and the [Relatively-Universal-ROM-Programmer](https://github.com/AndersBNielsen/Relatively-Universal-ROM-Programmer) RURP shield.


For more information, see the [Firestarter README](https://github.com/henols/firestarter_app/blob/main/README.md).

## Beta / Pre-release Channel

Pre-release firmware `.hex` builds are published as GitHub Pre-releases — tagged `X.Y.ZbN`
(PEP 440 beta) or `X.Y.ZrcN` (release candidate), marked "Pre-release", NOT marked "Latest".
The "Latest" filter on `api.github.com` automatically excludes them, so stable-installed apps
never accidentally pull beta firmware.

### Install paths

1. **Via the app (recommended):**
   ```bash
   firestarter fw -i --pre
   ```
   See the [firestarter_app README beta section](https://github.com/henols/firestarter_app/blob/main/README.md#beta--pre-release-channel) for the full set of install flags (`--pre`, `--firmware-version`, `--list`, `--stable`).

2. **Direct download:** Visit https://github.com/henols/firestarter/releases, filter the page by
   selecting the "Pre-release" tag (the GitHub Releases page has a built-in pre-release filter
   dropdown), then download `firestarter_{board}.hex` (e.g. `firestarter_uno.hex`,
   `firestarter_uno328pb.hex`, `firestarter_leonardo.hex`) for the target board and flash it
   manually with `avrdude`.

### Supported boards

Since v1.5, three firmware build targets are emitted per release:

| Board | PlatformIO env | MCU | Bootloader | Notes |
|-------|----------------|-----|------------|-------|
| `uno` | `[env:uno]` | ATmega328P | optiboot (stk500v1 `arduino`) | Arduino Uno R3 + RURP shield |
| `uno328pb` | `[env:uno328pb]` | ATmega328PB | Urclock (MiniCore default) | Arduino Uno R3 carrier board re-MCU'd with ATmega328PB; pin-compatible with `uno` |
| `leonardo` | `[env:leonardo]` | ATmega32U4 | Caterina (avr109) | Arduino Leonardo + RURP shield (1024-byte data buffer) |

The firmware reports its board name in the handshake response (`board:` field of `MSG_OK_FW_HANDSHAKE`), and the host CLI's `firestarter fw -i` uses that string to resolve the matching `.hex` asset from the GitHub Release.

### Stability guarantee

> **⚠ No stability guarantees.** Beta builds are intended for testing pre-release features. They may contain bugs, may change without notice, or may be withdrawn. For production / hardware-bench use, install the stable release.

### Reporting issues against a beta build

When reporting a bug against a beta firmware build, please include:

- **Firmware beta version:** the `X.Y.ZbN` string from `include/version.h` in the released source,
  OR the firmware handshake string printed on `firestarter hw` startup,
  OR the row in `firestarter fw --list` matching the installed version
- **Commit SHA:** from the GitHub Release page's commit reference
- **Board:** `uno`, `uno328pb`, or `leonardo` (or other configured board)
- **Chip part number + manufacturer** (for hardware-specific issues)
- **Repro steps**

Report firmware issues at: https://github.com/henols/firestarter/issues

## Shield Revision Support

The firmware detects the connected RURP shield's silkscreen revision at boot via an ADC voltage-band lookup on pin A3. Rev 2.0+ shields carry the R41 detect divider; pre-detect-resistor boards (Rev 0 / Rev 1) and any board landing in the guard gap fall through to `rev_unknown` and honor the EEPROM `hw_revision` byte override. The detected silkscreen string surfaces on the firmware handshake (`MSG_OK_REV`).

For the per-revision capability matrix, the silkscreen → code alias table, and the per-rev expected ADC band table, see [`doc/SHIELD-REVISIONS.md`](./doc/SHIELD-REVISIONS.md).

If detection lands in the guard gap (`rev_unknown`) on a board where you know the revision, set the EEPROM override byte via the host CLI: `firestarter rev <N>` (see the `firestarter_app` README for the byte values).

## License
[MIT](https://raw.githubusercontent.com/henols/firestarter/main/LICENSE)


