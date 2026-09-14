# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Structure

This is a meta-repo / planning repo for the Firestarter EPROM programmer project. The actual code lives in two sub-repos:

- `firestarter_fw/` — Arduino C++ firmware (PlatformIO). See `firestarter_fw/CLAUDE.md`.
- `firestarter_app/` — Python host CLI application (pip package). See `firestarter_app/CLAUDE.md`.

This repo tracks `.planning/` (GSD project management artifacts), `.claude/` (project settings), `tools/` and `.github/` (repo-level tooling and CI). Neither sub-repo is committed here. Documentation lives only in the `firestarter_prom` GitHub wiki — there is no in-repo copy of it. The `tools/wiki/` checkers that used to validate a clone of that wiki were retired on 2026-09-02 (`5426d7ef`); `tools/wiki/` was removed entirely on 2026-09-08, when its last occupant, `MIGRATION-TABLE.md`, moved to `.planning/v1.35/MIGRATION-TABLE.md` as a record of the completed migration — `tools/` now holds two occupants, `tools/catalog/` (messages codegen and sub-repo sync tooling) and `tools/adoption/` (the PyPI per-version download-share instrument) — and **no automated wiki guard exists now**.

`.gitmodules` records a submodule URL per commit. Checking out a pre-rename ref such as `v1.35`, or bisecting firmware history, resurrects the old firmware URL from that commit. **Fixing the live branches does not fix history.** See `.planning/notes/gitmodules-archaeology-trap.md` for both workarounds, their executed transcripts, and the `git submodule sync` hazard that silently undoes one of them. The trap does not bite today, because the old firmware slug still redirects. It arms only if the freed slug is ever claimed for this repository.

## System Overview

Firestarter is a two-part system for programming EPROMs, Flash, and SRAM devices using an Arduino-based RURP (Relatively-Universal-ROM-Programmer) shield:

1. **Python CLI** (`firestarter_app/`) — runs on the host PC; parses user commands, looks up EPROM specs from a JSON database, and orchestrates operations via serial.
2. **Arduino firmware** (`firestarter_fw/`) — runs on the Arduino; receives JSON commands, drives the hardware bus, and streams binary data back using a three-phase state machine protocol (INIT → MAIN → END).

The protocol runs at 250000 baud. Commands are JSON objects; responses are prefix-tagged lines (`OK:`, `DATA:`, `MAIN:`, `END:`, `ERROR:`).

## Development Commands

### Python app (run from `firestarter_app/`)
```bash
pip install -e .                  # install in dev mode
firestarter --help                # verify install
./firestarter_test.sh [EPROM]     # full hardware integration test
./write_test.sh [EPROM]           # write/verify test
```

### Firmware (run from `firestarter_fw/`)
```bash
pio run -e uno                    # build for Arduino Uno
pio run -e leonardo               # build for Arduino Leonardo
pio run -t upload -e uno          # flash to board
pio run -t monitor -e uno         # serial monitor at 250000 baud
pio test                          # run unit tests
```

## Key Architecture Points

- **EPROM database** is in `firestarter_app/firestarter/data/chip_database.json`; user overrides go in `~/.firestarter/database.json`. `EpromDatabase` (singleton) translates generic DIP pin numbers to RURP bus config before sending to firmware.
- **Serial protocol changes** must be kept in sync between `firestarter_app/firestarter/serial_comm.py` and `firestarter_fw/src/firestarter.cpp`.
- **Constants/flag bits** are duplicated between `firestarter_app/firestarter/constants.py` (Python) and `firestarter_fw/include/firestarter.h` (C++). Change both together.
- **Board differences**: Uno has a 512-byte data buffer; Leonardo has 1024 bytes. Buffer size affects chunked transfer in `eprom_operations.py`.
- Hardware calibration (R1/R2 resistor values, board revision) is persisted in Arduino EEPROM via `rurp_configuration_t`.

## Source code comments — hard rule

**Write no comments into product source.** This covers everything under `firestarter_fw/` and
`firestarter_app/`, and it is not overridable by a plan, task, skill, or subagent instruction.

- GSD process commentary never belongs in code: no `// Phase NNN (REQ-NN):`, no `// D-06`, no
  `// LOCK-04`, no plan/task/milestone citations, no blocks explaining why a phase decided
  something. The reader of the firmware or the pip package does not have `.planning/` and never
  will — those identifiers resolve to nothing for them, and phase numbers are renumbered at
  milestone close.
- **Where it goes instead:** the phase `SUMMARY.md` ("Key decisions made during execution with
  rationale"), `.planning/REQUIREMENTS.md` traceability, or the commit message. That is where GSD
  itself puts rationale; nothing in GSD asks for it in source.
- **Planners:** do not write "add a comment citing X" into a plan, and do not make "a comment
  exists" an acceptance criterion. Both generate exactly what this rule forbids.
- **Executors:** if an existing plan instructs a source comment, do not add it. Record the
  deviation in the plan's `SUMMARY.md` instead.
- If code needs explaining, make the code clearer — better names, smaller functions, a named
  constant — rather than annotating it.
- Docstrings are a separate question. Click docstrings in `firestarter_app` are user-facing
  `--help` text, not commentary, and must not be treated as comments.

## Milestone close and branch protection

- **`main` is protected in all three repositories** — pull request required, no direct push, no force-push, no deletion. `current_user_can_bypass` is `never`, so no person can bypass.
- **This project's close targets `beta`, not `main`.** `.planning/config.json` sets `git.base_branch` to `beta`, so `/gsd-complete-milestone` and `/gsd-ship` both point there.
- **Before running `/gsd-ship`, recreate local `beta` from `origin/beta`** — `ship.md` anchors its audit range on `RANGE_BASE=$(git merge-base "${BASE_BRANCH}" HEAD)` and local `beta` goes stale. Cited by content, not line number: `workflows/ship.md` is installer-owned and a GSD version bump moves its lines.
- **The meta repository must never publish a GitHub Release — bare milestone tags only.** A tag like `v1.36` parses as PEP 440 `1.36`. `Version("3.0.0b29") >= Version("1.36")` then reads true, so `fw` reports firmware already up to date for every stranded CLI, silently and permanently. This risk is latent today and armed by a single future action. Cited by content, not line number: see `.planning/notes/999.9-repo-rename-impact-analysis.md` § "Standing rule this must produce" for the full mechanism.
- **The mechanics, the blocked stable-release route and the consumer sites are in `.planning/notes/v135-close-procedure-under-protection.md`.**
