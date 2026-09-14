<p align="left"><img src="https://raw.githubusercontent.com/henols/firestarter_app/refs/heads/main/images/firestarter_logo.png" alt="Firestarter EPROM Programmer" width="200"></p>

# Firestarter

**An EPROM programmer built from an Arduino and the RURP shield.**

It reads, writes, erases and verifies EPROM, EEPROM, Flash and SRAM chips —
the 24, 28 and 32-pin parallel DIP parts found in arcade boards, home
computers, synthesisers and industrial equipment from the 1980s and 1990s.
746 chips across 59 manufacturers are in its database.

If you have a vintage board with a socketed ROM on it, this is a way to read
that chip, keep a copy, and put a new one back.

## Documentation

**→ [The Firestarter wiki](https://github.com/henols/firestarter/wiki)**

How to install it, how to read your first chip, and the reference material for
every supported chip family.

## The repositories

| Repository | What it is |
|---|---|
| **firestarter** (this one) | The project hub — the wiki, and the shared issue tracker |
| [firestarter_fw](https://github.com/henols/firestarter_fw) | The AVR firmware that runs on the Arduino and drives the chip |
| [firestarter_app](https://github.com/henols/firestarter_app) | The `firestarter` command you run on your computer |

The firmware and the CLI are used together, and the CLI installs the matching
firmware for you.

## Reporting a problem

See the [Contributing](https://github.com/henols/firestarter/wiki/Contributing) wiki page for where to report a problem and where to open a pull request.
