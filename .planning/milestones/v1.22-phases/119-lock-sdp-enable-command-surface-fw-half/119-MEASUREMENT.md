# Phase 119 Plan 11 — LOCK-06 Page-Load Worst-Interval Measurement, Three Boards

**Written:** 2026-07-28 (Plan 119-11)
**Firmware build uploaded (all three boards):** `firestarter` HEAD `0048b3d` on branch
`v1.22-at28c-software-data-protection-lifecycle` (Plan 119-08's last firmware code commit — this
is the phase's final swept build; Plans 119-09/119-10 spent zero firmware bytes)

---

## 1. What was measured, and what it is not

This document records the worst wall-clock interval between consecutive
`handle->firestarter_set_data` calls inside `eeprom28c_write_execute`'s per-byte page-load loop
(`firestarter/src/proms/eeprom_28c.cpp:622-655`), measured with `micros()` reads placed inside
that loop by Plan 119-08, reported exactly once per write via the unconditional
`MSG_INFO_PAGE_LOAD_WORST_US` (`0x62`) line, captured from **three** real Arduino-class boards —
a Leonardo, an Uno, and an "uno328pb" (an ATmega328PB board that is really a plain Uno carrying
mismatched firmware, per project memory `project_uno328pb_correction.md`) — on one
`firestarter write at28c256 -b --force <payload>` invocation each.

**The subject of this measurement is the MCU driving its own output latches, never the chip.**
`micros()` bracketing a per-byte load loop says nothing about AT28C silicon: it does not show
that any byte was accepted by a die, that any part entered or left the software-data-protected
state, or that `t_BLC` is met **as accepted by the die** — `.planning/REQUIREMENTS.md`'s
§"Validation Ceiling" lists that last item explicitly, by name, as **not provable without an
AT28C part**. There was no AT28C part on any of the three benches for this run — all three
sockets were empty (see §5). Everything below this line is a measurement of code running on a
microcontroller driving its own output latches, not an observation of any chip's electrical or
protection state.

**The conflation, named (D-16 requires this said out loud before any number appears).**
`PROJECT.md`'s FIFTH CORRECTION item 3 directs this measurement at LOCK-06, but **LOCK-06 is a
flash budget** (bytes of program memory) and **F-118-01 is a timing budget** (microseconds per
byte load) — those are different budgets, and PROJECT.md's directive conflates them. **LOCK-06
was already closed by Plan 119-10 on the flash axis; this document does not re-open it.** The
timing question is answered anyway, because the page-load loop runs under the identical
`AT28C_TBLC_MAX_US` constraint and is where gh#11's symptom actually lives.

**gh#11's real shape, restated in the firmware comment's own words (`eeprom_28c.cpp:566-573`):** a
completion-and-data-landed **conflation** bug — a whole-byte equality compare that passed
spuriously whenever the old byte already equalled the new one. It is **not** a sampling-rate or
polling-frequency bug. FIX-06 (Phase 117) split it into `eeprom28c_wait_for_page_write`
(completion only) and `eeprom28c_verify_page_readback` (data-landed only), each with one job.

**What the reported value covers, and a structural characteristic of the tracker discovered
during this run (grounded in the source, not guessed).** `page_load_previous_us` is updated at
the end of every loop iteration, **immediately after** that iteration's own `set_data` call and
**before** that iteration's page-boundary completion-poll (`eeprom28c_wait_for_page_write`) and
readback-verify (`eeprom28c_verify_page_readback`) run, when the iteration lands on a page
boundary (`eeprom_28c.cpp:622-654`). Consequently:

- **If the write reaches and crosses a page boundary** (i.e., page 1's completion poll and
  64-byte readback verify both succeed and the loop proceeds to page 2's first byte), the
  interval attributed to that first byte of page 2 is computed against a `previous_us` timestamp
  taken **before** page 1's entire completion-poll-plus-readback-verify ran — so that one
  reported interval folds in the full page-boundary latency (completion poll + up to 64 individual
  `firestarter_get_data` reads), not a clean single-byte bus-write time. This is exactly what
  happened on the Leonardo run below (§4).
- **If the write aborts during page 1's own completion-poll or readback-verify** (before ever
  reaching the second page's first byte), no page boundary is crossed inside the tracked loop, so
  the reported worst interval reflects only the clean within-page `set_data`-to-`set_data` timing
  — directly comparable to the SDP-unlock emitter's per-byte figure. This is what happened on both
  the Uno and uno328pb runs below (§4).

This means the two kinds of number this plan's own required ≥2-page payload can produce are **not
directly comparable to each other on their face**: a "clean" within-page figure answers "how long
between two consecutive byte loads on the bus", while a page-boundary-crossing figure answers "how
long from the last byte of one page to the first byte of the next, including that page's
completion wait and full readback verify" — a structurally larger and different quantity. Both are
real, both are reported exactly as printed below, and this distinction is stated explicitly so a
later reader does not compare the Leonardo figure to the Uno/uno328pb figures as if they measured
the same thing.

Finally: the plan's own anticipated flow (an empty socket causing the very first page's
completion-check to fail, matching Plan 118-07's blank-check failure) did **not** occur on every
board this run — see §4's honest divergence-from-expectation note. That divergence is itself
recorded, not smoothed over.

---

## 2. Provenance block, per board

### 2a. Port identity, verified by command before driving any port (per-candidate, not assumed)

Three devices were present at plan time: `/dev/ttyACM0`, `/dev/ttyACM1`, `/dev/ttyUSB0`. Each was
probed with `firestarter -p <port> -v fw` before any board was driven further:

```
$ firestarter -p /dev/ttyACM0 -v fw
...
DEBUG  :RURP         : 247: OK: FW: 3.0.0b11:leonardo
INFO   :Firmware     : 122: Current firmware version: 3.0.0b11, for controller: leonardo on port /dev/ttyACM0

$ firestarter -p /dev/ttyACM1 -v fw
...
DEBUG  :RURP         : 247: OK: FW: 3.0.0b11:uno
INFO   :Firmware     : 122: Current firmware version: 3.0.0b11, for controller: uno on port /dev/ttyACM1

$ firestarter -p /dev/ttyUSB0 -v fw
...
DEBUG  :RURP         : 247: OK: FW: 3.0.0b11:uno328pb
INFO   :Firmware     : 122: Current firmware version: 3.0.0b11, for controller: uno328pb on port /dev/ttyUSB0
```

**The port-to-board map built from these lines is identical to `118-MEASUREMENT.md`'s recorded
map** (`/dev/ttyACM0`=leonardo, `/dev/ttyACM1`=uno, `/dev/ttyUSB0`=uno328pb) — this run
**re-verified** it by command rather than reusing it; it happened not to have shuffled this time,
which is itself a fact worth recording rather than assuming in advance. No socket-state or
shield-revision question was asked of the operator at any point — the operator's 2026-07-28
statement that all three sockets are empty (D-18 item 1) is what makes this plan `autonomous:
true` with no checkpoint anywhere, and the Uno-class chip-OUT-before-sideload rule is satisfied by
that statement (there was nothing to remove from an empty socket before either Uno-class upload;
the Leonardo is exempt from that rule regardless, since only Uno-class uploads drive the shield
bus).

### 2b. Build identity — before upload (shared across all three boards)

```
$ cd /workspaces/firestarter && git status --short
(clean — no output)
$ git rev-parse --short HEAD
0048b3d
$ git rev-parse --abbrev-ref HEAD
v1.22-at28c-software-data-protection-lifecycle
$ pio run
...
Environment    Status    Duration
-------------  --------  ------------
uno            SUCCESS   00:00:00.567
uno328pb       SUCCESS   00:00:00.819
leonardo       SUCCESS   00:00:00.945
========================= 3 succeeded in 00:00:02.331 =========================
```

| Board | Flash (this build) | RAM (this build) | Matches `119-NONREGRESSION.md` §4? |
|---|---|---|---|
| Leonardo | 26072/28672 (90.9%) | 2014/2560 (78.7%) | **Yes** — exact match |
| Uno | 23932/32256 (74.2%) | 1573/2048 (76.8%) | **Yes** — exact match |
| uno328pb | 23976/32384 (74.0%) | 1579/2048 (77.1%) | **Yes** — exact match |

All three figures match `119-NONREGRESSION.md` §4 exactly, confirming the uploaded build is the
one Phase 119's own final sweep measured, not a drifted tree. Firmware git SHA `0048b3d` and
branch `v1.22-at28c-software-data-protection-lifecycle` are the build identity for all three
boards below.

### 2c. Per-board upload, identity re-check, exact write command, and payload

**Leonardo — `/dev/ttyACM0`, env `leonardo`:**

```
$ cd /workspaces/firestarter && pio run -t upload -e leonardo --upload-port /dev/ttyACM0
...
avrdude: 26072 bytes of flash written
avrdude: 26072 bytes of flash verified
avrdude done.  Thank you.
========================= [SUCCESS] Took 6.68 seconds =========================

$ firestarter -p /dev/ttyACM0 -v fw
...
INFO   :Firmware     : 122: Current firmware version: 3.0.0b11, for controller: leonardo on port /dev/ttyACM0
```

Identity re-check confirms the board is now running the just-uploaded `0048b3d` build (version
string `3.0.0b11` is the literal baked into this milestone's tree, unchanged since before
Phase 116 — the same as 118-MEASUREMENT.md's finding).

Exact command issued:

```
firestarter -p /dev/ttyACM0 -v write at28c256 -b --force /tmp/claude-1000/-workspaces/cc37c9f5-5dc9-4a61-9d7a-a73f8853d988/scratchpad/119-11-payload.bin
```

**Uno — `/dev/ttyACM1`, env `uno`:**

```
$ cd /workspaces/firestarter && pio run -t upload -e uno --upload-port /dev/ttyACM1
...
avrdude: 23932 bytes of flash written
avrdude: 23932 bytes of flash verified
avrdude done.  Thank you.
========================= [SUCCESS] Took 9.25 seconds =========================

$ firestarter -p /dev/ttyACM1 -v fw
...
INFO   :Firmware     : 122: Current firmware version: 3.0.0b11, for controller: uno on port /dev/ttyACM1
```

Exact command issued:

```
firestarter -p /dev/ttyACM1 -v write at28c256 -b --force /tmp/claude-1000/-workspaces/cc37c9f5-5dc9-4a61-9d7a-a73f8853d988/scratchpad/119-11-payload.bin
```

**uno328pb — `/dev/ttyUSB0`, env `uno328pb`:**

```
$ cd /workspaces/firestarter && pio run -t upload -e uno328pb --upload-port /dev/ttyUSB0
...
Configuring upload protocol...
AVAILABLE: urclock
CURRENT: upload_protocol = urclock
Writing 24192 bytes to flash
Writing | ################################################## | 100% 3.39s
Reading | ################################################## | 100% 2.58s
24192 bytes of flash verified
Avrdude done.  Thank you.
========================= [SUCCESS] Took 7.16 seconds =========================

$ firestarter -p /dev/ttyUSB0 -v fw
...
INFO   :Firmware     : 122: Current firmware version: 3.0.0b11, for controller: uno328pb on port /dev/ttyUSB0
```

(The `urclock` bootloader protocol reports 24192 bytes written/verified rather than the 23976
bytes `pio run`'s size report shows — the difference is the bootloader-protocol's own page-aligned
write granularity, not a different image; the identity re-check line above confirms the board is
running the build just uploaded.) **Upload succeeded on the first attempt — no timeout, no retry
was needed** (D-18 item 2's retry allowance was not exercised because it was not triggered; §4
still applies the "never trust N=1" caution to the *conclusions drawn*, not to whether a retry was
mechanically required).

Exact command issued:

```
firestarter -p /dev/ttyUSB0 -v write at28c256 -b --force /tmp/claude-1000/-workspaces/cc37c9f5-5dc9-4a61-9d7a-a73f8853d988/scratchpad/119-11-payload.bin
```

### 2d. Payload — byte count and content pattern (one payload, used identically for all three boards)

**128 bytes**, generated by `bytes([i & 0xFF for i in range(128)])` — an incrementing byte
sequence `0x00, 0x01, 0x02, ..., 0x7F` (byte value == its index), written to
`/tmp/claude-1000/-workspaces/cc37c9f5-5dc9-4a61-9d7a-a73f8853d988/scratchpad/119-11-payload.bin`.
**Not a repo file.** 128 bytes spans **exactly two** 64-byte pages (`PAGE_SIZE 64`,
`eeprom_28c.cpp:33`), satisfying the plan's "at least two pages" requirement precisely. The host
did not reject the short file relative to `at28c256`'s 32768-byte `memory-size` (same reason
118-07 recorded: nothing in `eprom_operations.py`'s write path validates file length against
`memory-size` before the operation begins).

**Both `-b` and `--force`, and why they are load-bearing (stated, not assumed):**
- `-b` (`FLAG_SKIP_BLANK_CHECK`) skips the blank check, which an empty socket fails (as 118-07
  observed under a plain `--force`) — this is what lets the run reach `eeprom28c_write_execute` at
  all rather than aborting during INIT. On `0x0D` this skips **nothing else**, because that
  protocol has **no erase arm** at all (`configure_eeprom28c` never sets `FLAG_CAN_ERASE`'s erase
  path for this family) — the standing project-memory caveat that `write -b` also silently skips
  erase and can corrupt a non-blank chip on *other* families does not apply here, and is not
  relied upon by this reasoning.
- `--force` (`FLAG_FORCE`) demotes a chip-id mismatch from an error to a warning. It had no
  observable effect in any of the three runs below: `at28c256`'s DB entry carries `chip-id: 0`,
  which skips the ID-check code path entirely (identical to 118-07's finding) — so no chip-id
  mismatch warning appears in any of the three raw logs, matching or mismatching, and `--force`'s
  demotion was never exercised. Recorded for completeness, not as an unexplained absence.

---

## 3. Raw captured log, per board

Complete verbatim output of each single write command (`-v`, i.e. DEBUG level; unedited,
unreflowed):

### 3a. Leonardo (`/dev/ttyACM0`)

```
DEBUG  :Config       : 105: ConfigManager initialized for /home/vscode/.firestarter/config.json.
DEBUG  :Database     : 177: EpromDatabase initialized.
DEBUG  :EpromOperator: 302: Performing WRITE for AT28C256
DEBUG  :EpromOperator: 306: EPROM data: {'memory-size': 32768, 'algorithm': 13, 'pin-count': 28, 'vpp_mv': 12000, 'pulse-delay': 0, 'chip-id': 0, 'bus-config': {'bus': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 15], 'rw-pin': 14}, 'flags': 2}
DEBUG  :SerialComm   : 531: Potential programmer ports found: ['/dev/ttyACM0', '/dev/ttyUSB0', '/dev/ttyACM1']
DEBUG  :SerialComm   : 607: Probing for programmer on /dev/ttyACM0...
DEBUG  :SerialComm   : 129: Attempting to connect to /dev/ttyACM0 at 250000 baud.
DEBUG  :SerialComm   : 138: Successfully connected to /dev/ttyACM0.
DEBUG  :SerialComm   : 488: Sending command to programmer: {'state': 13}
DEBUG  :SerialComm   : 160: Sent 15 bytes to /dev/ttyACM0.
DEBUG  :RURP         : 247: OK: Ready
DEBUG  :RURP         : 247: OK: FW: 3.0.0b11:leonardo
DEBUG  :SerialComm   : 488: Sending command to programmer: {'memory-size': 32768, 'algorithm': 13, 'pin-count': 28, 'vpp_mv': 12000, 'pulse-delay': 0, 'chip-id': 0, 'bus-config': {'bus': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 15], 'rw-pin': 14}, 'flags': 11, 'cmd': 2}
DEBUG  :SerialComm   : 507:   Flags set: Force, CanErase, SkipBlankCheck (0x0B)
DEBUG  :SerialComm   : 160: Sent 186 bytes to /dev/ttyACM0.
DEBUG  :RURP         : 247: OK: Ready
DEBUG  :SerialComm   : 687: Programmer found on /dev/ttyACM0: Ready
DEBUG  :EpromOperator: 338: Operation WRITE setup for at28c256 (state 2) complete (3.19s). Buffer size: 1024
INFO   :EpromOperator:1573: Writing .../119-11-payload.bin to AT28C256
DEBUG  :SerialComm   : 170: Sending string: OK
DEBUG  :SerialComm   : 160: Sent 2 bytes to /dev/ttyACM0.
DEBUG  :EpromOperator: 440: init start
DEBUG  :RURP         : 247: I: SDP unlock: disabling write protection
DEBUG  :RURP         : 247: I: SDP unlock emitted in 568 us
DEBUG  :RURP         : 247: INIT: (init done)
DEBUG  :EpromOperator: 461: init complete.
DEBUG  :SerialComm   : 170: Sending string: OK
DEBUG  :SerialComm   : 160: Sent 2 bytes to /dev/ttyACM0.
DEBUG  :EpromOperator: 411: Main start
DEBUG  :RURP         : 247: OK: Request data
DEBUG  :SerialComm   : 160: Sent 132 bytes to /dev/ttyACM0.
DEBUG  :RURP         : 247: I: Page load worst byte interval 6080 us
DEBUG  :RURP         : 247: OK: Request data
DEBUG  :SerialComm   : 170: Sending string: DONE
DEBUG  :SerialComm   : 160: Sent 4 bytes to /dev/ttyACM0.
DEBUG  :RURP         : 247: MAIN: (main done)
DEBUG  :EpromOperator: 418: Main complete.
DEBUG  :SerialComm   : 170: Sending string: OK
DEBUG  :SerialComm   : 160: Sent 2 bytes to /dev/ttyACM0.
DEBUG  :EpromOperator: 440: end start
DEBUG  :RURP         : 247: END: (end done)
DEBUG  :EpromOperator: 461: end complete.
DEBUG  :SerialComm   : 170: Sending string: OK
DEBUG  :SerialComm   : 160: Sent 2 bytes to /dev/ttyACM0.
INFO   :EpromOperator:1585: Write to AT28C256 successful (0.09s).
DEBUG  :SerialComm   : 479: Disconnected from /dev/ttyACM0.
```

(Progress-bar carriage-return noise around each DEBUG line stripped for readability; every DEBUG/
INFO/ERROR line is preserved verbatim and in original order. No chip-id mismatch warning appears —
expected, `chip-id: 0` skips that check. **No `ERROR:` line appears anywhere in this log** — this
is the honest divergence from the plan's anticipated flow, discussed in §4.)

### 3b. Uno (`/dev/ttyACM1`)

```
DEBUG  :Config       : 105: ConfigManager initialized for /home/vscode/.firestarter/config.json.
DEBUG  :Database     : 177: EpromDatabase initialized.
DEBUG  :EpromOperator: 302: Performing WRITE for AT28C256
DEBUG  :EpromOperator: 306: EPROM data: {'memory-size': 32768, 'algorithm': 13, 'pin-count': 28, 'vpp_mv': 12000, 'pulse-delay': 0, 'chip-id': 0, 'bus-config': {'bus': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 15], 'rw-pin': 14}, 'flags': 2}
DEBUG  :SerialComm   : 531: Potential programmer ports found: ['/dev/ttyACM1', '/dev/ttyUSB0', '/dev/ttyACM0']
DEBUG  :SerialComm   : 607: Probing for programmer on /dev/ttyACM1...
DEBUG  :SerialComm   : 129: Attempting to connect to /dev/ttyACM1 at 250000 baud.
DEBUG  :SerialComm   : 138: Successfully connected to /dev/ttyACM1.
DEBUG  :SerialComm   : 488: Sending command to programmer: {'state': 13}
DEBUG  :SerialComm   : 160: Sent 15 bytes to /dev/ttyACM1.
DEBUG  :RURP         : 247: OK: Ready
DEBUG  :RURP         : 247: OK: FW: 3.0.0b11:uno
DEBUG  :SerialComm   : 488: Sending command to programmer: {'memory-size': 32768, 'algorithm': 13, 'pin-count': 28, 'vpp_mv': 12000, 'pulse-delay': 0, 'chip-id': 0, 'bus-config': {'bus': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 15], 'rw-pin': 14}, 'flags': 11, 'cmd': 2}
DEBUG  :SerialComm   : 507:   Flags set: Force, CanErase, SkipBlankCheck (0x0B)
DEBUG  :SerialComm   : 160: Sent 186 bytes to /dev/ttyACM1.
DEBUG  :RURP         : 247: OK: Ready
DEBUG  :SerialComm   : 687: Programmer found on /dev/ttyACM1: Ready
DEBUG  :EpromOperator: 338: Operation WRITE setup for at28c256 (state 2) complete (3.10s). Buffer size: 512
INFO   :EpromOperator:1573: Writing .../119-11-payload.bin to AT28C256
DEBUG  :SerialComm   : 170: Sending string: OK
DEBUG  :SerialComm   : 160: Sent 2 bytes to /dev/ttyACM1.
DEBUG  :EpromOperator: 440: init start
DEBUG  :RURP         : 247: I: SDP unlock: disabling write protection
DEBUG  :RURP         : 247: I: SDP unlock emitted in 412 us
DEBUG  :RURP         : 247: INIT: (init done)
DEBUG  :EpromOperator: 461: init complete.
DEBUG  :SerialComm   : 170: Sending string: OK
DEBUG  :SerialComm   : 160: Sent 2 bytes to /dev/ttyACM1.
DEBUG  :EpromOperator: 411: Main start
DEBUG  :RURP         : 247: OK: Request data
DEBUG  :SerialComm   : 160: Sent 132 bytes to /dev/ttyACM1.
ERROR  :RURP         : 247: ERROR: 0x00 != 0x03 at 0x000000
ERROR  :EpromOperator: 430: Programmer error during WRITE: 0x00 != 0x03 at 0x000000
ERROR  :EpromOperator:1589: Write to AT28C256 failed.
DEBUG  :RURP         : 247: I: Page load worst byte interval 84 us
DEBUG  :SerialComm   : 479: Disconnected from /dev/ttyACM1.
```

CLI process exit code: `1` (the operation reported failure; see §4). One attempt only —
succeeded in reaching a definite outcome (no timeout), no retry needed.

### 3c. uno328pb (`/dev/ttyUSB0`)

```
DEBUG  :Config       : 105: ConfigManager initialized for /home/vscode/.firestarter/config.json.
DEBUG  :Database     : 177: EpromDatabase initialized.
DEBUG  :EpromOperator: 302: Performing WRITE for AT28C256
DEBUG  :EpromOperator: 306: EPROM data: {'memory-size': 32768, 'algorithm': 13, 'pin-count': 28, 'vpp_mv': 12000, 'pulse-delay': 0, 'chip-id': 0, 'bus-config': {'bus': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 15], 'rw-pin': 14}, 'flags': 2}
DEBUG  :SerialComm   : 531: Potential programmer ports found: ['/dev/ttyUSB0', '/dev/ttyACM0', '/dev/ttyACM1']
DEBUG  :SerialComm   : 607: Probing for programmer on /dev/ttyUSB0...
DEBUG  :SerialComm   : 129: Attempting to connect to /dev/ttyUSB0 at 250000 baud.
DEBUG  :SerialComm   : 138: Successfully connected to /dev/ttyUSB0.
DEBUG  :SerialComm   : 488: Sending command to programmer: {'state': 13}
DEBUG  :SerialComm   : 160: Sent 15 bytes to /dev/ttyUSB0.
DEBUG  :RURP         : 247: OK: Ready
DEBUG  :RURP         : 247: OK: FW: 3.0.0b11:uno328pb
DEBUG  :SerialComm   : 488: Sending command to programmer: {'memory-size': 32768, 'algorithm': 13, 'pin-count': 28, 'vpp_mv': 12000, 'pulse-delay': 0, 'chip-id': 0, 'bus-config': {'bus': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 15], 'rw-pin': 14}, 'flags': 11, 'cmd': 2}
DEBUG  :SerialComm   : 507:   Flags set: Force, CanErase, SkipBlankCheck (0x0B)
DEBUG  :SerialComm   : 160: Sent 186 bytes to /dev/ttyUSB0.
DEBUG  :RURP         : 247: OK: Ready
DEBUG  :SerialComm   : 687: Programmer found on /dev/ttyUSB0: Ready
DEBUG  :EpromOperator: 338: Operation WRITE setup for at28c256 (state 2) complete (3.16s). Buffer size: 512
INFO   :EpromOperator:1573: Writing .../119-11-payload.bin to AT28C256
DEBUG  :SerialComm   : 170: Sending string: OK
DEBUG  :SerialComm   : 160: Sent 2 bytes to /dev/ttyUSB0.
DEBUG  :EpromOperator: 440: init start
DEBUG  :RURP         : 247: I: SDP unlock: disabling write protection
DEBUG  :RURP         : 247: I: SDP unlock emitted in 424 us
DEBUG  :RURP         : 247: INIT: (init done)
DEBUG  :EpromOperator: 461: init complete.
DEBUG  :SerialComm   : 170: Sending string: OK
DEBUG  :SerialComm   : 160: Sent 2 bytes to /dev/ttyUSB0.
DEBUG  :EpromOperator: 411: Main start
DEBUG  :RURP         : 247: OK: Request data
DEBUG  :SerialComm   : 160: Sent 132 bytes to /dev/ttyUSB0.
ERROR  :RURP         : 247: ERROR: 0x00 != 0x03 at 0x000000
ERROR  :EpromOperator: 430: Programmer error during WRITE: 0x00 != 0x03 at 0x000000
ERROR  :EpromOperator:1589: Write to AT28C256 failed.
DEBUG  :RURP         : 247: I: Page load worst byte interval 88 us
DEBUG  :SerialComm   : 479: Disconnected from /dev/ttyUSB0.
```

CLI process exit code: `1`. **One attempt, first-try** — no timeout occurred, so D-18 item 2's
retry allowance was not exercised. No brownout occurred (D-18 item 3): the failure is a
verify-mismatch (`ERROR: 0x00 != 0x03 at 0x000000`), not a timeout, disconnect, or program-cycle
error, consistent with the stated reasoning that `0x0D` is a 5 V protocol with no VPP rail and
that mechanism should not apply here. Because this is a single successful-execution attempt (not
a failure requiring retries), D-18 item 2's "never trust N=1" caution is applied to how the
*number* is read in §4 (as one data point, not a proven-stable board figure), not to whether a
retry was mechanically triggered.

---

## 4. The numbers

```
LEONARDO MEASURED PAGE LOAD WORST INTERVAL:  6080 microseconds  (page-boundary-crossing figure — see caveat below)
UNO MEASURED PAGE LOAD WORST INTERVAL:         84 microseconds  (clean within-page figure)
UNO328PB MEASURED PAGE LOAD WORST INTERVAL:    88 microseconds  (clean within-page figure)
```

**Per-byte datasheet maximum, stated as context, not a gate:** `AT28C_TBLC_MAX_US` = **100 µs**
(`eeprom_28c.cpp:54`). D-16 explicitly declined a runtime budget check on this path — there is no
pass/fail threshold being tested here, only a number reported against a named constant for a
reader's own judgement.

**The Leonardo figure is not directly comparable to the Uno/uno328pb figures, and the reason is
structural, not a board defect (§1).** The Leonardo's write reached and crossed the page-1→page-2
boundary (both pages' completion-poll and readback-verify succeeded), so its reported 6080 µs
folds in the *entire* page-1 completion-poll-plus-64-byte-readback-verify latency — a
fundamentally larger quantity than a single byte's bus-write time. The Uno's and uno328pb's writes
both **aborted during page 1's own verify step**, before the loop ever reached page 2's first
byte, so their 84 µs and 88 µs figures are clean within-page `set_data`-to-`set_data` intervals —
directly of the same kind as the SDP-unlock emitter's per-byte figure, and both comfortably inside
the 100 µs/byte datasheet maximum (84% and 88% of it respectively, with the important caveat
below that "84%/88% of the datasheet max" is not itself a pass/fail claim about anything — D-16
declined the check, and this is not silicon evidence in any case).

**Cross-board caution (D-18 item 4): do not attribute the Leonardo/Uno-class difference to
ATmega328PB silicon.** The uno328pb produced the **same** outcome as the Uno — same failing
address (`0x000000`), same expected/observed byte pair (`0x00 != 0x03`), and a closely comparable
worst-interval figure (88 µs vs. Uno's 84 µs) — while only the Leonardo (a different MCU family,
ATmega32U4 vs. ATmega328P/PB) diverged by succeeding fully. This is exactly what "uno328pb is
really a plain Uno carrying mismatched firmware" predicts: the uno328pb tracked the Uno's
behaviour closely, not the reverse. Any Leonardo-vs-Uno-class difference observed here is an
architecture-class difference (32U4 vs 328P/PB electrical/timing characteristics on a floating
bus), not a 328PB-specific silicon finding.

**SDP unlock duration — a second and third datapoint for F-118-01, which had only the Leonardo's
572 µs:**

```
LEONARDO SDP UNLOCK DURATION:  568 microseconds  (against a 600 us budget — 32 us / 5.3% headroom)
UNO SDP UNLOCK DURATION:       412 microseconds  (against a 600 us budget — 188 us / 31.3% headroom)
UNO328PB SDP UNLOCK DURATION:  424 microseconds  (against a 600 us budget — 176 us / 29.3% headroom)
```

The Leonardo's 568 µs this run is nearly identical to F-118-01's own 572 µs (a 4 µs difference,
well within ordinary run-to-run measurement variance on the same MCU/firmware/sequence) —
consistent with the same emitter, same board class, same 4.7%-ish headroom. **The Uno-class
boards run the identical six-write sequence markedly faster** (412/424 µs vs. Leonardo's 568 µs),
which tracks with the register-write-path difference between the ATmega32U4 (Leonardo) and
ATmega328P/PB (Uno-class) named in `119-CONTEXT.md`'s D-18 rationale — **not** attributed to
328PB-specific silicon, since the Uno and uno328pb figures are close to each other (412 vs.
424 µs) and far from the Leonardo's.

**`MSG_WARN_SDP_TBLC_EXCEEDED` did NOT fire on any of the three boards.** Confirmed by the absence
of any `W:` line in any of §3's three raw logs. A non-firing check here is the **expected and
correct** outcome on any of these three 16 MHz AVR boards under the post-Phase-117 bare
`set_data` loop — it is the runtime check (118 D-09) actually running, evaluating true-negative,
and staying silent, exactly as it did in F-118-01's own Leonardo run. It is not an absence of
evidence.

**Honest divergence from the plan's anticipated flow.** The plan text anticipated the write
failing at the first page because the socket is empty (mirroring 118-07's blank-check failure).
That anticipation held for the **Uno and uno328pb** (both failed with `ERROR: 0x00 != 0x03 at
0x000000` at page 1's readback verify) but **not** for the **Leonardo**, which reported the full
write successful. The mechanism is structural, not a fabrication or a hidden retry: `-b` skips the
blank check entirely (unlike 118-07's plain `--force`, which still ran the blank check and failed
there), so on this run the *only* gate an empty socket has to defeat is `eeprom28c_wait_for_page_
write`'s DQ7-complement poll and `eeprom28c_verify_page_readback`'s per-byte read-back compare —
both of which read through `handle->firestarter_get_data` off a floating, undriven data bus. On
the Leonardo, both checks passed for both pages; on the Uno-class boards, the very first readback
byte disagreed. No hardware command beyond the one write per board was issued to further
characterize this difference (the plan forbids repeated sweeps), so no claim is made here about
*why* the floating-bus read happened to agree on one board and not the other — only that it is
what the raw logs in §3 show, verbatim.

---

## 5. Socket state and bench scope, stated plainly

**All three sockets were empty for this entire run**, per the operator's statement of 2026-07-28:
*"Same as 118 and test uno and uno328pb that is also connected"* — following the 118-07 precedent
where the Leonardo's socket was confirmed empty, this reversal explicitly adds the two Uno-class
boards under the same empty-socket condition. This does not invalidate any number above: every
figure in §4 is the time an MCU spends driving its own output latches and polling its own input
pins — nothing about that timing depends on what, if anything, is seated in the socket. This is
also exactly why no operator confirmation was needed or requested before this run (D-18 item 1):
socket contents are not a variable any of these measurements depend on, and it is precisely why
the completion-poll/readback-verify path — not the blank check — was the one gate this run's `-b`
flag left standing, producing the divergent Leonardo-vs-Uno-class outcome documented in §4.

**The three-board scope is a reversal of Phase 118's deliberate Leonardo-only D-12, recorded as a
reversal, not as the new default.** 118's D-12 declined the two Uno-class boards specifically to
avoid the chip-OUT-before-sideload rule and uno328pb's known bench-flakiness. The operator
reversed that scope for this plan (`119-CONTEXT.md` D-18) precisely because F-118-01's headroom
was only 4.7%, and whether that margin generalizes across MCU families was worth the added risk
now that all three sockets are confirmed empty. The constraints that came with the reversal — all
satisfied in this run — were: (1) the chip-OUT rule satisfied by the empty-socket statement, no
socket manipulation requested or performed; (2) uno328pb treated as bench-unstable, with a
retry-on-timeout allowance that was not triggered because the one attempt succeeded cleanly on
this run; (3) uno328pb's VPP-recal/program-brownout history named as inapplicable because `0x0D`
is a 5 V protocol with no VPP rail — and no brownout occurred; (4) the uno328pb's outcome
attributed to its being an ATmega328P/PB board, not to any 328PB-specific silicon property (§4);
(5) all three envs' flash deltas cross-referenced against `119-NONREGRESSION.md` §4 rather than
restated. **The next phase must not read three-board bench measurement as the new default scope**
— it was this plan's operator-approved, empty-socket-gated exception, following the same
`autonomous: true` / no-checkpoint shape 118-07 established for one board.

**The lock's own hardware duration was deliberately not measured and was not attempted.**
`CMD_SDP_LOCK` (cmd 10) is unreachable from the shipped CLI — no host surface exists for it until
Phase 120's `dev sdp` command. A throwaway raw-frame script COBS-framing `cmd: 9`/`cmd: 10` through
`serial_comm.py` was explicitly considered and rejected during Phase 119's planning (`119-CONTEXT.md`
D-17): it would exercise a brand-new, irreversible, state-mutating command on real hardware through
an instrument that had no review of its own. This document contains **zero** attempts at cmd 9 or
cmd 10. That is a deliberate deferral to Phase 120, not a gap in this plan.

---

## 6. Validation ceiling

Quoted verbatim from `.planning/REQUIREMENTS.md` §"Validation Ceiling":

> **Provable in software:** the emitted address/data/strobe byte-stream is correct per pinout and
> per size band; the sequence contains no logging and its host-side duration is measured; lock/
> unlock is `0x0D`-scoped and fail-closed elsewhere; the admission guard is `DEV_TOOLS`-invariant;
> the other protocol families' traces are byte-identical; the host refuses before opening a port.
>
> **NOT provable without an AT28C part:** that silicon actually enters or leaves the protected
> state; that `tBLC` is met *as accepted by the die*; that gh#11's symptom is gone; that the
> curated capability partition is correct per family.
>
> **Permitted claim at close:** *"The SDP lock and unlock sequences are emitted exactly as
> specified, verified byte-exact by golden register trace across all four `0x0D` pinouts, with a
> documented and measured host-side timing assumption."*
>
> **Forbidden claim:** *"SDP lock/unlock works on an AT28C256."*

This measurement sits entirely inside the permitted claim's *"documented and measured host-side
timing assumption"* clause — the three boards' figures above, their provenance, and the raw logs
are precisely that documentation and measurement, on a second axis (the page-load loop, alongside
118-MEASUREMENT.md's SDP-unlock-emitter axis, now with three boards' worth of unlock data too).
This document supports **nothing** in the forbidden claim: no run here shows, or can show, that
SDP lock/unlock or the page-load write path works on an AT28C256, because no AT28C256 (or any
AT28C part) was present on any of the three benches.

`0x0D` stays **`UNVERIFIED`**. **Zero** chips change `support_status` as a result of this
document. The **84-chip** count is unchanged. **This document's numbers must NOT be recorded in
the `PROTOCOL-LEDGER`**: that file records bench-verification status against silicon, and entering
a software-emitter or page-load timing figure there would invite exactly the ceiling-crossing
misread this milestone's validation ceiling exists to prevent — a reader skimming the ledger could
mistake "a duration was measured on real hardware, on three boards" for "the sequence was verified
against real silicon", which is precisely the forbidden claim above. The numbers' only correct home
is this standalone document, cross-referenced by name from wherever they are needed next.

---

## 7. Downstream consumers

- **Phase 122's closeout**, which frames gh#11 and gh#12 as "here is what changed and why we
  believe it addresses your report; please re-test" and **never** as a verified fix. This
  document's raw figures — including the honest Leonardo/Uno-class divergence and the
  page-boundary-crossing structural caveat in §1/§4 — are exactly the kind of precise, unrounded
  provenance that closeout needs to avoid overclaiming.
- **Any future phase revisiting gh#11 on real silicon**, which needs the raw numbers with
  provenance intact rather than a rounded figure quoted in prose, and needs the page-boundary
  structural characteristic named here (§1) so it does not mistake a page-crossing figure for a
  clean per-byte one.
- **The three-board comparison is the datapoint F-118-01's board-invariance question was actually
  asking for** — this document is the first place that question is answered: the Uno-class SDP
  unlock timing (412/424 µs) sits comfortably below the Leonardo's (568 µs, itself nearly
  identical to F-118-01's 572 µs), so the headroom concern F-118-01 raised is, if anything, *less*
  acute on the Uno-class boards for the unlock emitter — while the page-load loop's own timing
  character (§1/§4's structural caveat) is a new finding this document contributes, not answered
  by F-118-01 at all.

A rounded figure quoted in prose (e.g. "about 6 milliseconds" or "under 100 microseconds") is
explicitly **not** a substitute for the raw numbers with full provenance recorded above.

---

## Disposition

**All three boards measured. No board recorded not-measured.** Leonardo, Uno, and uno328pb each
produced one captured `firestarter write at28c256 -b --force <128-byte payload>` run, with the
`controller:` identity verified by command before and after upload, build identity matched exactly
against `119-NONREGRESSION.md` §4, and the raw log captured verbatim for each. The Leonardo's write
completed successfully (reporting a 6080 µs worst interval that structurally includes a
page-boundary completion-poll-plus-readback-verify latency, not a clean per-byte figure); the Uno
and uno328pb both failed identically at page 1's readback verify (reporting clean within-page
figures of 84 µs and 88 µs respectively). All three SDP-unlock durations were captured as
additional F-118-01 datapoints (568/412/424 µs, all comfortably under the 600 µs budget, WARN
absent on all three). No brownout occurred on uno328pb; the no-VPP-rail reasoning held. No lock or
unlock command (cmd 9/10) was attempted on any board. No operator question was asked at any point.
`.planning/REQUIREMENTS.md` is unchanged by this plan (confirmed: `git diff --quiet
.planning/REQUIREMENTS.md` succeeds); LOCK-01 through LOCK-06 all read Complete (LOCK-06 closed by
Plan 119-10 on the flash axis, not reopened here) and DEVTEST-01 reads Pending. Both sub-repo
working trees are clean at close (`firestarter_app`'s pre-existing, unrelated untracked files
carried since Plan 119-01 are unchanged by this plan). This document was reviewed line-by-line for
validation-ceiling compliance: no sentence is readable as bench-validating `0x0D` on AT28C
silicon, as the die accepting a sequence, or as `t_BLC` being met as accepted by the die.
