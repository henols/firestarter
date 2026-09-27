---
created: 2026-08-27T16:53:09Z
title: "Drive outputs/pins to a safe state ASAP on power-up and on ANY fault — not only via the 1 s command timeout"
area: firmware
files:
  - firestarter/src/firestarter.cpp:37-49
  - firestarter/src/firestarter.cpp:208-217
  - firestarter/src/firestarter.cpp:219-221
  - firestarter/src/firestarter.cpp:349-351
  - firestarter/include/firestarter.h:47
  - firestarter/src/boards/uno_rurp_shield.cpp:42-59
  - firestarter/src/boards/leonardo_rurp_shield.cpp:32-45
---

## Problem

Operator requirement, captured verbatim in intent: **when power is applied, or when
something goes wrong — connection lost or whatever — the state of the outputs and pins
must be reset ASAP.**

A chip is sitting in a ZIF socket while all of this happens. Anything the shield is
still asserting (VPP/VPE, chip enable, output enable, a latched address, a driven data
bus) is being applied to that part. Today the firmware only guarantees that teardown on
the *clean* path, and the timing on the *dirty* path is neither immediate nor uniform
across boards.

What the code actually does today (verified at fw `5759dc8`):

1. **Clean teardown exists and is correct.** `command_done()`
   ([firestarter.cpp:208-217](firestarter/src/firestarter.cpp#L208-L217)) switches to
   programmer mode, calls `rurp_chip_disable()`, and zeroes `CONTROL_REGISTER`,
   `LEAST_SIGNIFICANT_BYTE`, and `MOST_SIGNIFICANT_BYTE`. That is the safe state.

2. **The only dirty-path trigger is a 1 s poll in `loop()`.**
   [firestarter.cpp:219-221](firestarter/src/firestarter.cpp#L219-L221) reaches
   `command_done()` only when `handle.cmd != CMD_IDLE && timeout < millis()`, with
   `TIMEOUT_MS 1000` ([firestarter.h:47](firestarter/include/firestarter.h#L47)) and
   the deadline pushed forward by `op_reset_timeout()`
   ([firestarter.cpp:349](firestarter/src/firestarter.cpp#L349)) on every accepted
   frame. So a host that disappears mid-command leaves the outputs asserted for up to
   a full second — and only if the main loop is actually reached, which it is not while
   a blocking operation is still running inside the op handler.

3. **`rurp_board_setup()` is NOT board-symmetric at power-up.** The Uno path
   ([uno_rurp_shield.cpp:42-59](firestarter/src/boards/uno_rurp_shield.cpp#L42-L59))
   sets `DDRB`/`PORTB`, then `rurp_chip_disable()`, `rurp_chip_input()`, and zeroes all
   three registers. The Leonardo path
   ([leonardo_rurp_shield.cpp:32-45](firestarter/src/boards/leonardo_rurp_shield.cpp#L32-L45))
   sets the three DDR masks and starts serial — **no `rurp_chip_disable()`, no
   `rurp_chip_input()`, no register zeroing.** On Leonardo the shield's latched outputs
   are whatever they happened to be at power-up until the first command writes them.
   This matters more on Leonardo than Uno because closing the serial port does not
   reset a Leonardo (see `chip-out-before-sideload` — Uno-class only), so there is no
   implicit MCU reset to fall back on.

4. **Power-up ordering puts config work ahead of the safe state.** `setup()`
   ([firestarter.cpp:37-49](firestarter/src/firestarter.cpp#L37-L49)) runs
   `rurp_load_config()` and `rurp_detect_hardware_revision()` *before*
   `rurp_board_setup()`. Whatever those cost in time, the pins are unconstrained for
   that whole window.

Weeks-later context: this was captured during the v1.34 bench campaign, on the back of
repeated cell A2 write failures where a chip stayed in the socket across failed connects
and aborted writes.

## Solution

Not yet designed. Directions worth testing, roughly in order of value:

- **Leonardo parity** — make `rurp_board_setup()` assert the same safe state on both
  boards (`chip_disable` + `chip_input` + zero all three registers). Cheapest and most
  clearly correct item here.
- **Safe state first in `setup()`** — hoist the pin/register safing ahead of
  `rurp_load_config()` / `rurp_detect_hardware_revision()`, so the socket is quiet from
  the earliest instruction that can make it so. Needs a check that safing does not
  depend on loaded config (hardware revision affects some register semantics — confirm
  before moving it).
- **Funnel every fault through the teardown** — audit the error exits (frame decode
  failure, `MSG_ERR_EMPTY_INPUT` at the `n <= 0` branch, unknown command, parse
  failure, per-op error returns) and confirm each one either is already `CMD_IDLE` or
  reaches `command_done()`. Log-and-continue paths that leave a command mid-flight are
  the bug class to hunt.
- **Faster / independent dirty-path trigger** — TBD. Options to evaluate: shorten the
  poll, safe the outputs inside the long-running op handlers on serial silence rather
  than only between commands, or arm the AVR watchdog so a hang resets into `setup()`
  (which then must itself safe the pins first — depends on the item above).
- **Host-disconnect detection** — TBD, and board-dependent. Investigate whether a DTR
  drop is observable on each board and whether it is worth acting on.

Explicitly out of scope of the capture: hardware-side pull-downs / power sequencing on
the shield. That is a board-revision question, not firmware.
