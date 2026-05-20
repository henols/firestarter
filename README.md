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
   `firestarter_leonardo.hex`) for the target board and flash it manually with `avrdude`.

### Stability guarantee

> **⚠ No stability guarantees.** Beta builds are intended for testing pre-release features. They may contain bugs, may change without notice, or may be withdrawn. For production / hardware-bench use, install the stable release.

### Reporting issues against a beta build

When reporting a bug against a beta firmware build, please include:

- **Firmware beta version:** the `X.Y.ZbN` string from `include/version.h` in the released source,
  OR the firmware handshake string printed on `firestarter hw` startup,
  OR the row in `firestarter fw --list` matching the installed version
- **Commit SHA:** from the GitHub Release page's commit reference
- **Board:** `uno` or `leonardo` (or other configured board)
- **Chip part number + manufacturer** (for hardware-specific issues)
- **Repro steps**

Report firmware issues at: https://github.com/henols/firestarter/issues

## License
[MIT](https://raw.githubusercontent.com/henols/firestarter/main/LICENSE)


