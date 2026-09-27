---
title: "FM1608 byte 0 write never lands — register cache-skip elides all three shift-register strobes"
date: 2026-08-09
status: pending
priority: medium
area: firmware
source: .planning/debug/resolved/fm1608-fresh-chip-baseline.md (parked 2026-05-18, hardware-gated)
files:
  - firestarter/include/rurp_register_utils.h
  - firestarter/src/proms/memory.cpp
hardware_gated: true
needs_chip: "FM1608 (or any 0x28 SRAM/FRAM part) — a fresh sample is what the session was parked waiting for"
---

# FM1608 byte 0 never programs — cache-skip elides the shift-register strobes

Carried out of the `fm1608-fresh-chip-baseline` debug session, parked since 2026-05-18
awaiting hardware. Keeping it as a debug session made it a permanent milestone-close
blocker; it is a tracked defect with a strong hypothesis, so it belongs here.

## Symptom

On FM1608, byte 0 retains its factory `0xFF` across every write attempt while bytes
1..N-1 program correctly.

## Hypothesis H1 (well-supported, not yet confirmed on silicon)

`rurp_write_to_register` in `firestarter/include/rurp_register_utils.h` early-returns when
the cached value equals the value being written. On the **first** `memory_set_data(0, byte0)`
call, all three shift-register writes (LSB, MSB, CONTROL) are cache hits, so **no clock
strobe fires at all**:

- After `command_done`, cache == HW == `LSB=0, MSB=0, CONTROL=0`.
- `configure_memory` calls `mem_util_set_address(handle, 0)` → LSB=0 (skip), MSB=0 (skip),
  CONTROL=`0x10` from `ADDRESS_LINE_17` (cache `0 → 0x10`, strobes).
- First `memory_set_data(0, byte0)` recomputes the same targets — LSB=0, MSB=0,
  CONTROL=`0x10` — **all three skipped, zero strobes**.

On paper the shift register should still be holding `0/0/0x10` from the previous strobes, so
the write ought to land. Empirically it does not, which points at a timing/state dependency
requiring a strobe immediately before the data CE pulse.

**Why bytes 1..N work:** for byte 1 the LSB goes `0 → 1`, so a strobe always fires; every
later address differs in LSB too.

## Already falsified

- Three uniform writes (`0x00`, `0xAA`, `0x5A`) — byte 0 stays `0xFF`, bytes 1..8191 take
  each pattern. Refutes "byte 0 holds a stale value from a prior write".
- Triple-read after a single write — byte-identical across reads, so reads are deterministic
  and not the source of variance.
- Single-byte write with `-a 0` — byte 0 still `0xFF`; the path triggers even for a 1-byte chunk.

## Note on test coverage

This is the same register-write-elision mechanism that the native trace stubs are known to
miss unless `rurp_register_utils.h` is included in the host stubs. A native trace test that
does not model the elision **cannot** reproduce this bug — any test written for it must
assert on strobe counts, not just final register values.

## Next step when a chip is available

Instrument strobe counts around the first `memory_set_data` on a seated FM1608 and confirm
zero strobes fire; then test the candidate fix (force a strobe on the first data write of a
block, or dirty the cache at block start) and confirm byte 0 programs.
