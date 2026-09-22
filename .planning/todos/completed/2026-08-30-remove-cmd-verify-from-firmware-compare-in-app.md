---
created: 2026-08-30T20:13:16Z
title: Remove the CMD_VERIFY command surface from firmware — verify by read-back and compare in the app
area: both
resolves_phase: 204
files:
  - firestarter/include/firestarter.h:55
  - firestarter/include/firestarter.h:120
  - firestarter/src/firestarter.cpp:270-272
  - firestarter/src/eprom_operations.cpp:29-32
  - firestarter/include/eprom_operations.h:10
  - firestarter/src/proms/memory.cpp:73-75
  - firestarter/src/proms/memory.cpp:377-397
  - firestarter/include/memory_utils.h:19-22
  - firestarter/src/proms/eprom.cpp:471-472
  - firestarter/test/native/avr/test_dispatch/test_configure_memory.cpp:223-227
  - firestarter/test/native/avr/test_pinmap_provisional/test_pinmap_provisional.cpp:123
  - firestarter_app/firestarter/constants.py:65
  - firestarter_app/firestarter/constants.py:104
  - firestarter_app/firestarter/eprom_operations.py:1940-1973
  - firestarter_app/firestarter/cli_handlers.py:742-770
  - firestarter_app/firestarter/chip_test.py:162
---

## Problem

Verification is currently done **on the Arduino**. The host streams the expected
image to the device over `CMD_VERIFY` (6) and the firmware compares it against
what it reads off the chip, aborting on the first mismatch with
`MSG_ERR_VERIFY` (0xAF) plus a 5-byte `{expected, got, addr[2], addr[1], addr[0]}`
payload.

The idea is to delete that command surface from the firmware and have the app do
`CMD_READ` + compare in Python instead.

Why it is worth doing:

- **Flash budget.** AVR flash is the scarce resource (this is what v1.33 was
  about). The verify command surface is dispatch, a wrapper, a configure-case,
  and a header decl that all exist only to run a byte comparison the host is
  perfectly able to do.
- **Better diagnostics.** Firmware verify aborts at the *first* bad byte, so the
  user learns one address and nothing about the shape of the failure. The host
  already has a far richer comparison primitive — `classify_fingerprint` /
  `_diff_offsets` in `chip_test.py` — which names *why* a verify failed
  (blank/contact vs stuck bits vs pattern never matched) and counts total/bad.
  Routing all verification through it makes `verify` as informative as
  `dev test` already is.
- **One comparison implementation** instead of a firmware one and a host one.
- Wire volume is roughly unchanged: verify currently pushes the whole image to
  the device; read pulls the whole image back. No meaningful throughput loss.

## Solution

**Critical constraint — do NOT remove `memory_verify_execute` itself.** It is
not just the `CMD_VERIFY` handler. `eprom.cpp:471-472` *calls* it for the
`VERIFY_PER_PULSE_PLUS_FINAL` arm (protocols 0x07 / 0x08), and
`memory_utils.h:19-22` documents that it is exposed precisely so `eprom.cpp` can
reuse it instead of carrying a byte-identical copy. Likewise the in-algorithm
verifies are load-bearing and must stay:

- the per-pulse verify inside the EPROM programming loop (`VERIFY_PER_PULSE`) —
  a UV EPROM program loop cannot decide whether to pulse again without it;
- `eeprom28c_verify_page_readback` (`eeprom_28c.cpp:517`);
- `flash_util_verify_operation` (`flash_utils.cpp:30`).

So the scope is the **command surface only**:

1. Firmware: drop `CMD_VERIFY` from the `firestarter.cpp` dispatch switch, from
   `is_memory_cmd` (`firestarter.h:120`), from `configure_memory`'s switch
   (`memory.cpp:73`), and delete the `eprom_verify()` wrapper
   (`eprom_operations.cpp:29-32` + its decl). Keep `memory_verify_execute`, but
   re-comment `memory_utils.h` so it no longer describes itself as "the
   CMD_VERIFY operation_main".
2. Firmware tests: `test_configure_memory.cpp` and `test_pinmap_provisional.cpp`
   both assert over `CMD_VERIFY` and will need re-anchoring.
3. Host: reimplement `verify_eprom` (`eprom_operations.py:1940`) as a read +
   in-Python compare, reusing the `chip_test.py` diff primitives rather than
   growing a third comparison. `COMMAND_VERIFY` in `constants.py` goes away with
   it. The `verify` CLI command (`cli_handlers.py:742`) keeps its signature and
   exit-code contract.
4. `dev test`'s `OP_VERIFY` step goes through `verify_eprom`, so it must keep
   producing an equivalent (ideally richer) fingerprint. Check that verdict
   classification and `dedup_fingerprint` still behave.
5. `MSG_ERR_VERIFY` (0xAF) stays — the in-algorithm verifies still raise it.
   Note `messages.h` is codegen-generated from meta's `messages.toml`; do not
   hand-edit it.

**Open question — protocol compatibility.** Removing a command number is a
breaking protocol change in both directions (new host + old firmware, old host +
new firmware). Decide whether `CMD_VERIFY` is retired outright or kept as a
reserved/rejected opcode for a deprecation window, and whether this rides a
firmware major bump.
