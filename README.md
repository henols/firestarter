<p align="left"><img src="https://raw.githubusercontent.com/henols/firestarter/main/images/branding/firestarter_logo_horizontal.png" alt="Firestarter EPROM Programmer" width="400"></p>

# Firestarter

[![Buy me a coffee](https://img.shields.io/badge/Ko--fi-Buy%20me%20a%20coffee-FF5E5B?logo=ko-fi&logoColor=white)](https://ko-fi.com/E1E21I2WWW)

**An EPROM programmer made from an Arduino and the RURP shield.**

Firestarter reads, writes, erases and verifies EPROM, EEPROM, Flash and SRAM chips. It works with
the 24, 28 and 32-pin parallel DIP parts from arcade boards, home computers, synthesizers and
industrial equipment of the 1980s and 1990s. Its database has 746 chips from 59 manufacturers.

If you have an old board with a socketed ROM, you can use Firestarter to read that chip, keep a
copy, and program a new one.

## Documentation

**→ [The Firestarter wiki](https://github.com/henols/firestarter/wiki)**

The wiki tells you how to install Firestarter, how to read and program a chip, and how to set the
shield jumpers. It also has the reference pages for pin maps and programming protocols.

## The repositories

| Repository | Contents |
|---|---|
| **firestarter** (this one) | The project hub: the wiki, the issue tracker, the change log and the validated-chip list |
| [firestarter_app](https://github.com/henols/firestarter_app#readme) | The `firestarter` command-line tool that you run on your computer |
| [firestarter_fw](https://github.com/henols/firestarter_fw#readme) | The firmware that runs on the Arduino and operates the chip |

You use the command-line tool and the firmware together. The tool installs the correct firmware
on your board.

## Releases and chips

- [CHANGELOG.md](CHANGELOG.md): the changes in each release of the tool and the firmware.
- [VALIDATED-EPROMS.md](VALIDATED-EPROMS.md): the chips that passed a test on real hardware.

## Report a problem

Report problems in the [issue tracker of this repository](https://github.com/henols/firestarter/issues).
The [Contributing](https://github.com/henols/firestarter/wiki/Contributing) wiki page tells you
what to include, and where to send a pull request.

## Support

Firestarter is free. If it helps you, you can
[buy me a coffee on Ko-fi](https://ko-fi.com/E1E21I2WWW).
