# CLAUDE.md

This file gives guidance to Claude Code (claude.ai/code) for work in this repository.

## Repository Structure

This is the meta repository for the Firestarter EPROM programmer project. The code is in two
submodules:

- `firestarter_fw/` — Arduino C++ firmware (PlatformIO). Read `firestarter_fw/CLAUDE.md`.
- `firestarter_app/` — Python host CLI application (pip package). Read `firestarter_app/CLAUDE.md`.

User documentation is only in the `firestarter` GitHub wiki. `README.md` links to it.

## System Overview

Firestarter programs EPROM, Flash and SRAM devices. It uses an Arduino and the RURP
(Relatively-Universal-ROM-Programmer) shield. The system has two parts:

1. **Python CLI** (`firestarter_app/`)
2. **Arduino firmware** (`firestarter_fw/`)

## Writing Style (ASD-STE100)

Use the `asd-ste100` skill when it is relevant.
