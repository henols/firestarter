<p align="left"><img src="https://raw.githubusercontent.com/henols/firestarter/main/images/branding/firestarter_logo_horizontal.png" alt="Firestarter EPROM Programmer" width="400"></p>

# Changelog

This file records the changes to the Firestarter CLI (`firestarter_app`) and the Firestarter
firmware (`firestarter_fw`). It is the only change log for the project.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Each line starts
with **CLI** or **Firmware** to show the part that changed.

**The CLI and the firmware must have the same first two version numbers.** A 3.1 CLI operates
3.1 firmware. When you upgrade, upgrade the CLI first and then the firmware.

A version with a `b` and a number, for example `3.1.0b5`, is a pre-release on the beta channel.
`pip install firestarter` does not install a pre-release. Refer to
[Beta Channel](https://github.com/henols/firestarter/wiki/Beta-Channel).

## [3.1.0b6] - 2026-09-27 (pre-release)

### Fixed

- **CLI:** the 24-pin 5 V EEPROMs on the `DIP24_2816` pin map (AT28C04, AT28C16, X2816A,
  CAT28C16A, 28C16A and their siblings, 19 database entries) now write one byte at a time.
  Before, each write failed verification, because the tool sent 64-byte pages to parts that
  accept one byte for each write cycle.
- **CLI:** `erase` refuses the `DIP24_2816` chips. They have no erase command. Before, the erase
  stored bytes in the chip as data and reported success. To clear such a chip, write a file of
  `0xFF` bytes to it.
- **CLI:** `config --rev` accepts only the revision codes -1 to 5. Before, `--rev 2.2` set code 2
  (Rev 2.0) with no message. Use `--rev 4` for Rev 2.2.
- **CLI:** `info -c` prints the chip's real database entry and pin map. Before, it printed an
  "Unknown" entry in the 2.x format.
- **CLI:** an entry in `~/.firestarter/database.json` now replaces the shipped entry with the same
  `part_number`. Before, the tool added it as a second entry and continued to use the shipped one.
- **CLI:** `firestarter list | head` and `search` stop without a traceback when the reader closes
  the pipe.

### Changed

- **CLI:** the nine chips AT28C04, AT28C04E/F, AT28C16, AT28C16E/F, 28C04A, 28C04AF, 28C16A,
  28C16AF and UPD28C04 changed from `adapter-required` to `supported`. No chip of the
  `DIP24_2816` family is validated on real hardware yet.
- **CLI:** Click 8.5 or later is necessary. It adds PowerShell completion.

### Removed

- **CLI:** `list -v` (`--verified`). It always showed nothing. The validated chips are in
  [VALIDATED-EPROMS.md](VALIDATED-EPROMS.md).

## [3.1.0b5] - 2026-09-27 (pre-release)

### Added

- **CLI:** `firestarter cal --vcc <volts>` calibrates the voltage readings of one board. Measure
  the 5 V pin with a multimeter and give the value. `firestarter cal` without an option shows the
  stored calibration. `firestarter cal --reset` sets the nominal value again. It needs firmware
  3.1.0b4 or later, but it does not need the beta-only `dev` tools.
- **CLI:** `firestarter dev adc` shows the raw ADC counts for the rails off, VPP and VPE. It is a
  beta-only tool.

### Fixed

- **CLI:** `vpp` and `vpe` no longer stop at the first sample when the firmware sends a VCC
  warning.

## [3.1.0b4] - 2026-09-27 (pre-release)

### Added

- **Firmware:** each board stores a measured reference voltage (bandgap). The voltage readings of
  VCC, VPP and VPE use it. A board without a calibration uses the nominal 1100 mV, as before.
- **Firmware:** the firmware sends one warning for each command when the measured VCC is not
  plausible. This usually shows a board that needs `firestarter cal`.
- **Firmware:** a raw ADC readout command for `dev adc`. Only beta images have it.

### Changed

- **Firmware:** the VPP acceptance window. The high limit is now the target plus 3 % or plus
  500 mV, whichever is larger. The low limit stays at the target minus 5 %. Only chips with a VPP
  of 18 V or more get a different limit.
- **Firmware:** when the firmware finds a stored configuration from an older firmware, it keeps
  each field that is in range. It always keeps the shield-revision override.

### Fixed

- **Firmware:** on the Leonardo (ATmega32U4), the firmware now writes the MUX5 channel bit
  explicitly. The readings of this release do not change.

## [3.1.0] - 2026-09-26

The first stable release of the 3.x line. The previous stable release was CLI 2.0.9 with
firmware 2.0.6. This entry gives the changes since 2.0.9. The pre-release entries below give the
detail.

### Upgrading from 2.0.x

1. Upgrade the CLI: `pip install --upgrade firestarter`.
2. Make sure that `firestarter --version` shows 3.1.0 or later.
3. Install the firmware: `firestarter fw -i -b <board>`.

**Do not let a 2.0.x CLI install 3.x firmware.** A 2.0.x CLI offers the new firmware, but after
the install it cannot connect to the board. Each command then stops with
`No compatible programmer found on any port`. No chip is damaged. Upgrade the CLI to make the
pair work again.

If you have a chip-database override in `~/.firestarter/database.json`, write it again with the
new field names (refer to 3.0.0 pre-releases below).

### Added

- **CLI:** `verify` compares a chip with a file. `search` finds chips by part number.
- **CLI:** `dev test <chip>` runs a write-read-verify test on a chip. `--submit` sends the report
  as a GitHub issue.
- **CLI:** `info` shows the jumper settings for each shield revision and the pin layout of the
  chip.
- **CLI:** `write --verify` reads the chip again after the write and compares it with the file.
- **CLI:** `fw --list` shows the firmware releases. `fw` refuses firmware that is newer than the
  CLI. `--allow-newer-firmware` installs it anyway, but that pair is not tested.
- **CLI:** a new generated chip database: 746 chips from 59 manufacturers. Each chip has an
  explicit programming algorithm.

### Changed

- **CLI:** Python 3.11 or later is necessary. 2.0.x worked with Python 3.9.
- **CLI:** the command line uses Click. The shell-completion setup changed. Refer to
  [Shell Completion](https://github.com/henols/firestarter/wiki/Shell-Completion).
- **CLI + Firmware:** the CLI does the verify and the blank check. The firmware only reads the
  chip.
- **CLI + Firmware:** the commands from the CLI to the firmware use COBS framing and a CRC8
  checksum.
- Report issues at [henols/firestarter](https://github.com/henols/firestarter/issues). The
  sub-repositories do not accept issues.

## [3.1.0b3] - 2026-09-26 (pre-release)

### Added

- **CLI:** `fw` refuses to install firmware whose first two version numbers are higher than the
  CLI's. The patch number and the `bN` suffix are not compared. `--allow-newer-firmware` installs
  anyway, but that pair is not tested. `--force` does not skip this check. `fw --list` still shows
  all releases, so you can find a version for `--firmware-version`.

## [3.1.0b2] - 2026-09-25 (pre-release)

### Added

- **CLI:** `info` draws the jumper headers for the pin map of the chip. It marks the jumper that
  the chip needs.

### Changed

- **CLI:** `info` gets the VPP and erase lines from the measured shield behaviour.

## [3.1.0b1] - 2026-09-24 (pre-release)

### Changed

- **CLI + Firmware:** `verify` and `blank` read the chip and compare the data on the computer.
- **CLI:** the blank check before a write moved from the firmware to the CLI. `write -b` still
  skips that check. The erase still occurs.

### Removed

- **Firmware:** the verify command and the blank-check command. Their command numbers (6 and 4)
  will not be used again.
- **Firmware:** the skip-blank-check control flag (`0x08`).

### Compatibility

- An older CLI with 3.1.0b1 firmware: `verify` and `blank` stop with
  `ERROR: Unknown command`. `write` does not refuse a UV EPROM that is not blank.
- A 3.1.0b1 CLI with older firmware: `verify` and `blank` work. Install the matching firmware
  with `firestarter fw -i`.

## 3.0.0 pre-releases

The 3.0.0 line had pre-releases only. These are the changes that affect users.

### Changed

- **CLI:** the chip database stores numbers without units. `vcc`, `vdd`, `vpp` and
  `pulse_duration` became `vcc_mv`, `vdd_mv`, `vpp_mv` and `pulse_duration_us`. An override file
  with the old names does not load.
- **CLI + Firmware:** the `algorithm` field of a chip is the only value that selects the
  programming method. The CLI refuses a chip that has no `algorithm` before it sends a command.
- **CLI + Firmware:** COBS framing and a CRC8 checksum on each command. There is no fallback to
  the old plain-text commands. An old CLI cannot operate new firmware, and a new CLI cannot
  operate old firmware.

### Fixed

- **CLI:** `info` shows VCC 5.0 V for the AT28C family and 55 other EEPROMs. Before, it showed
  the 4.0 V verify voltage.

## 2.0.x and older

Refer to the GitHub releases of
[firestarter_app](https://github.com/henols/firestarter_app/releases) and
[firestarter_fw](https://github.com/henols/firestarter_fw/releases).
