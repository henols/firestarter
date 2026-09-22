---
created: 2026-08-30T00:00:00Z
title: Write-init blank check scans the whole device — non-blank UV EPROMs cannot be written at all
area: firmware + host app
resolves_phase: 205
files:
  - firestarter/src/proms/memory.cpp (:450-459 mem_util_blank_check resets address to 0)
  - firestarter/src/proms/eprom.cpp (:144-146 write-init calls it as the pre-flight)
  - firestarter_app/firestarter/eprom_operations.py (:485 memory-size narrowing is READ-only)
  - firestarter_app/firestarter/chip_test.py (uv-slot write dispatch, _resolve_write_target)
  - .planning/ROADMAP.md (Backlog 999.44)
---

## Problem

A partial write's pre-flight blank check applies to the **whole device**, not to
the region being written.

[`mem_util_blank_check`](../../../firestarter/src/proms/memory.cpp#L450-L459)
saves the caller's cursor, **hard-resets `handle->address` to 0**, and scans to
`handle->mem_size`. It has no region concept:

```c
if (!is_operation_in_progress(handle)) {
    set_operation_in_progress(handle);
    blank_check_saved_address = handle->address;
    handle->address = 0;                          // <-- reset to 0
} else {
    if (handle->address >= handle->mem_size) {    // <-- scan to mem_size
```

[`eprom_internal_write_init_body`](../../../firestarter/src/proms/eprom.cpp#L144-L146)
calls that same function as the write pre-flight. The host does not narrow it
either — the `memory-size` narrowing at
[`eprom_operations.py:485`](../../../firestarter_app/firestarter/eprom_operations.py#L485)
is guarded by `cmd == COMMAND_READ`.

**Result: a 256-byte slot write is gated on the whole 256 KiB device being
blank.**

## Why it stayed hidden

Non-UV parts carry `FLAG_CAN_ERASE`, so `eprom_internal_erase` runs immediately
above the check and leaves the device blank — the check passes trivially on
every EEPROM/flash part ever swept. **UV parts have `can_erase == false`**, so
nothing erases and the check refuses. The defect has been latent behind the
erase step for its whole life.

## Bench evidence

Operator, 2026-08-30, `firestarter dev test AM27C020`, Leonardo, fw `3.0.0b22`,
host `3.0.0b33`:

```
blank-check   BAD  Not blank, at 0x000000, v: 0x02
write-partial BAD  Programmer error during init: Not blank, at 0x000000, v: 0x02
verify        BAD  0xfe != 0xff at 0x03ff00
write coverage: slot 0x3FF00 (256 bytes), 510 bits cleared; 1024 of 1024 slots left
```

**The verify error proves the target slot was blank** — actual `0xFF` at
`0x03FF00`, the slot start. The write was refused on account of a byte at
`0x000000`, 262 KB away.

## Three consequences, none confined to `dev test`

1. **Product bug.** `firestarter write foo.bin -a 0x3FF00` on the same part hits
   the identical firmware init. Any partial write to a non-erasable part holding
   data is refused today.
2. **The UV slot design is defeated.** Slots exist so one part yields ~1024 runs
   (`_resolve_write_target`'s `slots_remaining`). Run 1 leaves the part
   non-blank, so run 2 is refused even though it targets a different, blank
   slot. **A UV part is testable at most once, and only if it arrives blank.**
3. **The report blames the chip.** One tool defect produces three BAD steps, and
   the submit prompt offers to file `[dev test] AM27C020 — FAIL` against the chip
   in `firestarter_prom`.

## Fix — both halves (operator decision 2026-08-30)

**(a) Firmware — region-scope the write-init check** to
`[address, address + data_size)` instead of `[0, mem_size)`.
`mem_util_blank_check`'s whole-device behaviour is **correct** for its two other
callers (standalone `CMD_BLANK_CHECK`, and the erase-end check), so this needs a
region-scoped variant or a start/end parameter — **not** an edit in place. The
multi-call chunking threads state through `blank_check_saved_address` and
`BLANK_CHECK_CHUNK_SIZE`; a region-scoped form must preserve that resumption
contract.

**(b) Host — pass `FLAG_SKIP_BLANK_CHECK` on `uv-slot` writes** in
`chip_test.py`. Semantically right, not a workaround: `_resolve_write_target`
has already probe-read the slot and computed
`mask_write_pattern(current, desired)`, which is **monotone — it only clears
1→0 and never asks for a 0→1 transition** — so it cannot corrupt, and the verify
step immediately behind it validates. Flags are decoupled (`-b` no longer
implies skip-erase) and `FLAG_CAN_ERASE` is false on UV parts anyway, so no
erase is skipped.

**(a) alone is insufficient:** slot acceptance is on the `cleared`/`retained`
floors, not on blankness, so a masked write into a partially-programmed slot
would still be refused. **(b) alone is insufficient:** it leaves the
product-level `firestarter write -a` bug untouched.

## The regression test that does not exist

**A UV part with data outside the target slot must accept a slot write.**
Nothing in the suite covers a non-blank, non-erasable part — which is precisely
why this shipped. Add it before the fix, so it is seen to go RED first.

Firmware-touching → dual-repo lockstep; golden register traces and the size
baseline are in play. Note the native trace stubs record no time and miss
register-write elision, so a trace diff cannot carry this change on its own.
