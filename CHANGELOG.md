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

## [Unreleased]

### Changed

- **CLI, Firmware:** the CLI sends each command as a fixed-layout binary frame, not as JSON. The
  COBS framing, the CRC8 and the data transfer do not change. This CLI cannot operate a board
  with older firmware, and older CLIs cannot operate this firmware. Upgrade the CLI first, then
  run `firestarter fw --install`. `fw` can still read the version of the older firmware so that
  it can replace it.
- **CLI, Firmware:** the binary command frame starts at version 3.3. The CLI refuses to install
  firmware older than 3.3, because it cannot operate that firmware.
- **Firmware:** the JSON parser and the jsmn library are removed. With the changes below, the
  firmware is about 3.9 KB smaller than 3.2.x on `uno`, `uno328pb` and `leonardo`.
- **Firmware:** the data buffer is 1024 B on `uno` and `uno328pb` (was 512 B) and 1536 B on
  `leonardo` (was 1024 B). The CLI sends bigger data chunks, so a read or write needs fewer
  round trips.
- **CLI, Firmware:** the firmware sends voltages in millivolts, and the CLI formats them. The
  CLI shows the VPP to the millivolt. Before, it showed the VPP on a 100 mV grid, so a 12.449 V
  rail showed as 12.4 V.
- **CLI, Firmware:** `dev reg` and `dev addr` get the raw register values from the firmware, and
  the CLI draws the table. Before, `dev reg` showed no table at all.
- **CLI:** the CLI calculates the write time for each block. The firmware no longer sends it.
- **CLI, Firmware:** `write --verify` tells the firmware to skip its final verify pass on the
  `0x07` and `0x08` EPROMs, because the CLI reads the region back itself. This saves about 0.7 s
  for each 64 KiB.
- **Firmware:** a stable image no longer measures the 28C page-load time. A pre-release image
  still measures it.
- **Firmware:** the overprogram pulse is removed. No chip used it.
- **Firmware:** a read timing above 1000 µs is refused. The JSON parser reduced it to 1000 µs.
  `firestarter dev consistency-check` refuses `--read-settling` and `--read-strobe` above 1000
  as a usage error, before it creates the output directory.
- **CLI, Firmware:** firmware that reads another version of the binary command frame answers
  with the version that it reads. The CLI then tells you to upgrade the CLI or the firmware,
  whichever is older.
- **Firmware:** an undefined flag bit and a command frame with the wrong length are refused.
- **CLI, Firmware:** a VPP above 25000 mV, a calibration supply voltage above 10000 mV and a
  hardware revision that is not 0–5 or 255 are refused. The 3.2.x firmware refused them too
  (issue #140).

## [3.2.6] - 2026-10-27 (CLI)

### Added

- **CLI:** `erase` erases the protocol-0x05 flash parts (AE29F2008, W29C010/020/040, AT29C and
  similar) when the board has firmware 3.2.2 or later (issue #62). On older firmware the CLI
  refuses the erase before the board starts it: some 3.0.0 pre-releases erased these parts with
  VPP on. `info` shows "Can be erased: yes (needs firmware 3.2.2 or later)".

### Changed

- **CLI:** with a hardware-revision override, `hw` shows the revision that the board detected as
  "Detected HW". Before, it showed it as "Override HW", which is the override itself. `config`
  still shows the override as "Override HW".

### Fixed

- **CLI:** a pre-release CLI offers the highest firmware release, stable or pre-release. Before,
  it chose only among pre-releases, and with firmware 3.2.2 published it offered 3.1.1b2.
- **CLI:** the CLI operates a board with a development build of the firmware (a version such as
  `3.2.2.dev48`). Before, it refused the board as outdated.

## [3.2.5] - 2026-10-27 (CLI)

### Fixed

- **CLI:** `fw --install --force` gives `-F` to avrdude, so that it installs on a board whose
  bootloader reports a different device signature, for example an ATmega328PB clone (issue #95).
- **CLI:** the MBM27C1000, MBM27C2000, HN27C301 and M27C1000 (SGS-Thomson) parts use their own
  pin map, with OE on pin 2 and A16 on pin 24. The shield drives pin 24 as OE, so these parts are
  refused as "adapter required", with the reason (issue #70).
- **CLI:** the TI 2532 is refused as "adapter required". The shield drives its pin 18 (A11) as CE,
  so only the lower 2 KB could be addressed.
- **CLI:** the AT27C011, D27011 and D27C011 are refused as "protocol not implemented", with the
  reason. The pin map reaches only 16 KB of their 128 KB (issue #136).
- **CLI:** the W27E257 programs at 12 V, from its datasheet. Before, the CLI used 13.5 V, the erase
  voltage.

### Added

- **CLI:** the Toshiba TMM27128AD.

## [3.2.4] - 2026-10-25 (CLI)

### Fixed

- **CLI:** the NEC uPD27128 and uPD27256 use the programming values from their datasheets.
- **CLI:** a chip whose pin map cannot reach all of its memory is refused.
- **CLI:** the 8 KB SRAM parts hold pin 26 high, and the 28-pin SRAM map is chosen by the address
  width.
- **CLI:** the 32-pin 28C EEPROMs strobe WE on pin 31.

### Added

- **CLI:** the Hitachi HN482764 / HN482764G and the Mitsubishi M5L2764K / M5L2764K-2.

## [3.2.3] - 2026-10-25 (CLI)

### Fixed

- **CLI:** the 2764 and 27128 parts hold PGM high during a read. Before, PGM was low, and the
  read and the verify of these parts were wrong.

## [3.2.2] - 2026-10-25 (CLI), 2026-10-27 (firmware)

The CLI 3.2.2 and the firmware 3.2.2 are two different releases with the same number.

### Fixed

- **CLI:** a chip name that selects rows that program differently (the same part number from two
  manufacturers, for example) is refused, and the CLI lists a qualified name for each row. Use
  `PART@MANUFACTURER` to select one row.
- **Firmware:** a NOR flash erase (protocol 0x06) waits until the part is ready, and reports a
  timeout or a part that is not blank after the erase. Before, the erase returned before the part
  had finished, and a read after it could show the chip ID as 0xFFFF (issues #86, #122).
- **Firmware:** a NOR flash sector erase above 64 KiB erases the correct sector (issue #117).
  The same fault prevented the software data protection cycles on the 28-pin AT29C256.
- **Firmware:** a NOR flash write at an address that is not 0 no longer erases a sector. Before,
  it erased the sector at the start address, and so the bytes below the start in that sector.
- **Firmware:** a 5 V page write (protocol 0x05) ends on the DQ7 data poll, confirmed by a second
  read.
- **Firmware:** the Intel 28F status register is decoded correctly, and a failed erase is no longer
  reported as a success (issue #116). VPP is measured before it goes to pin 1.
- **Firmware:** a command with a bus line that is not on the bus, a duplicate address line or a
  number that does not fit in 32 bits is refused (issues #115, #124, #130).
- **Firmware:** a write that ends with DONE before the end of its region is refused, and a stray
  frame during a write or a read is refused (issues #121, #129).
- **Firmware:** on the Uno, an error frame is no longer lost when the log buffer is full
  (issue #125).
- **Firmware:** the control pins start in the safe state (CE and OE high) before they become
  outputs, and the hardware revision is detected after the serial port is ready.
- **Firmware:** a VPP target above 25 V, a program pulse above 65535 µs, a calibration supply
  voltage above 10 V and an out-of-range revision value are refused.
- **Firmware:** a dev command that waits for the button stops after 30 s.

### Added

- **Firmware:** a software chip erase for the protocol-0x05 flash parts (issue #62). It needs the
  CLI 3.2.6 or later.

### Compatibility

- The firmware 3.2.2 operates with the CLI 3.2.0 and later. Only the TI 2532 changes: the
  firmware refuses its bus map. Its reads were already wrong. The CLI 3.2.5 refuses it with the
  reason.

## [3.2.1] - 2026-10-25

### Changed

- **CLI:** each timestamp that the CLI writes is ISO 8601 in Central European Time: CET
  (`+01:00`) in winter and CEST (`+02:00`) in summer. This applies to the `generated` field of a
  `dev test` report and of `validation-matrix.json`, and to the "Published" column of
  `fw --list`. Before, these timestamps were in UTC (`...Z`).
- **CLI:** the default output directory of `dev consistency-check`, `dev write-cycle` and
  `dev fault-inject` ends in an ISO 8601 basic-format time, for example
  `20261009T143056+0200`. Before, the name ended in `2026-10-09-143056`, in the local time of
  the computer, with no time zone.

### Fixed

- **Firmware:** a read, a write or a verify whose address range goes past the end of the device
  is refused before the bus is used, also when the range wraps around 32 bits (issue #120).

## [3.2.0] - 2026-10-25

3.2.0 contains all the changes after 3.1.0: the changes in this section, and the changes in
3.1.0b4 to 3.1.0b7. The most important new function is `firestarter cal`, which calibrates the
voltage readings of a board.

Upgrade the CLI first, then the firmware. A 3.1 CLI refuses to install 3.2 firmware.

### Fixed

- **CLI:** `blank` on a chip that is not blank, and `verify` on a chip that does not agree with
  the file, no longer show `ERROR: Timeout` and `Programmer error during READ`. The CLI stops the
  read at the first chunk that is different, and the firmware then stops the read with a
  timeout. This timeout is expected, so the CLI now shows only the result of the compare. A
  timeout that the CLI did not cause is still an error.
- **Firmware:** each command starts with default parameters. Before, a parameter that a command
  did not send kept its value from the previous command, for example the protocol, the VPP
  target or the bus map of the previous chip (issue #118).
- **Firmware:** a memory command with a missing parameter is refused, and the outputs go off
  immediately (issue #118).
- **Firmware:** the timeouts operate correctly when the millisecond counter of the board wraps
  around. This occurs after approximately 49.7 days without a reset (issue #123).
- **CLI:** `config` operates again with the 3.1.0 firmware. The CLI did not accept the shorter
  configuration answer that this firmware sends.
- **CLI:** `read`, `verify` and `blank` refuse a negative address, a size of 0 and an empty
  input file before they open the port. Before, the firmware refused the command, and the CLI
  then reported that it found no programmer. When the CLI finds no programmer, it now also
  shows the answer of the firmware.
- **CLI and firmware:** `config` refuses a value of R1, R2, the hardware revision or the
  bandgap that is out of range, and shows the permitted range. Before, the firmware replaced
  such a value with the default value and the CLI reported success. A refused command no
  longer changes the configuration in the memory of the board.
- **Firmware:** a configuration memory that holds data from a different program no longer sets
  a hardware-revision override. The firmware resets all such data to the default values. An
  override that you set yourself stays after a firmware update.
- **Firmware:** on the py32f071 board, the firmware no longer shows the "not calibrated"
  warning, and it refuses `cal`. This board does not use the bandgap calibration.
- **CLI:** when the firmware refuses a command, `dev test` disconnects and connects again for
  the next step.

### Version numbers

- The CLI 3.2.0b1 on PyPI was released by mistake on 2026-10-10. It has the same code as
  3.1.1b1. 3.2.0b2 and later releases replace it. The firmware has no 3.2.0b1.
- The CLI pre-releases 3.1.0b8 and 3.1.1b1, and the firmware pre-release 3.1.1b1, have no
  changes for users. The firmware pre-release 3.1.1b2 has the firmware fixes in this section.

## [3.1.0b7] - 2026-09-27 (pre-release)

### Fixed

- **CLI:** an entry in `~/.firestarter/database.json` that names the shipped chip in `name`
  replaces the shipped entry again. In 3.1.0b6, only `part_number` matched, so such an entry
  was added as a second entry and the shipped entry stayed in use. 3.1.0 is not affected.

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
- **CLI:** an entry in `~/.firestarter/database.json` can name the shipped chip in `part_number`,
  as `info -c` prints it. Before, only a `name` field matched the shipped chip.
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
