# Product Mission

## Problem

Owners of old parallel memory chips (UV-EPROM, EEPROM, flash, SRAM) need a low-cost way to read,
write, verify and erase them. The RURP shield (Relatively-Universal-ROM-Programmer) on an Arduino is
low-cost hardware, but each chip family needs a different programming algorithm, VPP rail, pin map
and jumper setting. A wrong choice can silently corrupt data or damage an irreplaceable chip.

## Target Users

- Hobbyists in retro computing and retro consoles (C64, Atari, Apple, NES) who program ROMs with a
  RURP shield.
- Community testers who run `firestarter dev test` on their own chips and send the reports as
  GitHub issues.
- The maintainer (Henrik Olsson), who does the bench validation with his own boards, shields and
  chips.

## Solution

Firestarter is a Python CLI (`pip install firestarter`) with Arduino firmware for the RURP shield.

- **Algorithm-first dispatch.** Each chip in the database has an explicit `algorithm`, which is the
  minipro `protocol_id` taken from `infoic.xml`. The host sends it over the wire. The firmware
  dispatches on that value only. There is no guessing from chip type or pin count.
- **Generated, reproducible chip database.** `build_db.py` builds the database from `infoic.xml`,
  plus datasheet overrides that each carry a citation. Nobody edits the generated file by hand.
- **Fail closed.** The host refuses a chip that is not `supported` before it sends a serial byte.
  The firmware refuses an unknown protocol with no hardware side effects.
- **Honest claims.** A chip counts as validated only after a real write→read→verify on silicon. A
  report states the shield revision, the board and the measured voltages. Limits that the hardware
  cannot meet are stated, not hidden.

## Scope

- In scope: DIP 24, 28 and 32-pin parallel memories. 8-bit data bus. 19-bit address bus (512 KiB
  maximum). Fixed 5 V VCC.
- Out of scope: SMD, PLCC and ICSP/serial devices. MCUs, PLDs and logic devices. A GUI or web
  interface. 6.25–6.5 V program VCC (no shield revision can raise VCC). Reading jumper state from the
  board (no shield revision senses JP4 or JP5).
