---
phase: 194-real-page-size-reaches-the-firmware
reviewed: 2026-09-15T00:00:00Z
depth: standard
files_reviewed: 22
files_reviewed_list:
  - firestarter_app/firestarter/cli_handlers.py
  - firestarter_app/firestarter/constants.py
  - firestarter_app/firestarter/data/chip_database.json
  - firestarter_app/firestarter/database.py
  - firestarter_app/firestarter/eprom_operations.py
  - firestarter_app/firestarter/exceptions.py
  - firestarter_app/firestarter/messages.py
  - firestarter_app/firestarter/page_size_gate.py
  - firestarter_app/tests/golden/chip_database_field_inventory.json
  - firestarter_app/tests/golden/wire_dict_expected_deltas_194.json
  - firestarter_app/tests/test_page_size_invariants.py
  - firestarter_app/tests/test_page_size_write_refusal.py
  - firestarter_app/tests/test_protection_status_catalog.py
  - firestarter_app/tests/test_vcc_margin_rail.py
  - firestarter_app/tests/test_wire_dict_equivalence.py
  - firestarter_app/tools/build_db.py
  - firestarter_fw/include/firestarter.h
  - firestarter_fw/include/messages.h
  - firestarter_fw/src/json_parser.c
  - firestarter_fw/src/proms/flash_5v_page.cpp
  - firestarter_fw/test/native/avr/_shared/host_stubs_common.inc
  - firestarter_fw/test/native/avr/test_val_5v_page/test_val_5v_page.cpp
  - tools/catalog/messages.toml
findings:
  critical: 0
  warning: 2
  info: 2
  total: 4
status: issues_found
---

# Phase 194: Code Review Report

**Reviewed:** 2026-09-15T00:00:00Z
**Depth:** standard
**Files Reviewed:** 22 (chip_database.json and messages.py/messages.h reviewed only as generator evidence, per instruction, not for style)
**Status:** issues_found

## Summary

This phase threads a per-chip page size from `chip_database.json` through
`database.py` / `page_size_gate.py` / `eprom_operations.py` on the host, and
through `json_parser.c` / `flash_5v_page.cpp` on the firmware. It replaces a
capacity-derived page-size guess with the database's real value for protocol
0x05 (`FLASH_AMD_STD`).

The core safety property holds. `flash_5v_page_write_execute` validates
`handle->page_size` with `flash_5v_page_mask()` (power-of-two, 1..512) before
any register write. It refuses with zero bus writes on failure. This is
shown by `test_5v_page_write_execute_refuses_with_no_page_size` and its
siblings `..._refuses_page_size_not_power_of_two`, `..._above_ceiling`, and
`..._transport_saturated`. The page-boundary arithmetic in the write loop is
address-based, not block-index-based, so it correctly handles a page
boundary that falls mid-chunk or an unaligned start address. The host's
`page_size_gate.require_page_size` is a genuinely pure predicate. It imports
no I/O module and reaches no attribute beyond dict `.get`. It runs before
`_operation_context` in both `cli_handlers.write()` and
`EpromOperator.write_eprom()`. `build_db.py` also carries a hard,
whole-database post-construction validator (raises `ValueError`, refuses to
write the JSON) that pins every emitted `page_size` to a power of two in
`[1, 512]`, matching the firmware's own accepted set. `tests/test_page_size_invariants.py`
and `tests/test_wire_dict_equivalence.py` both use exact-count assertions,
never floors, on both the real database and two independent synthetic
non-vacuity legs, so neither gate can silently go vacuous or get loosened to
match whatever the code now emits.

Two robustness gaps are worth fixing (WARNING). Two items are worth noting
for awareness (INFO). None are blockers.

## Warnings

### WR-01: Host-side page_size predicate is weaker than the firmware's accepted set, so an invalid value only fails after a connect

**File:** `firestarter_app/firestarter/page_size_gate.py:80-88`
**Issue:** `require_page_size` validates only that `page-size` is *truthy*:

```python
page_size = (programmer_data or {}).get(JSON_KEY_PAGE_SIZE)
if not page_size:
    raise PageSizeUnavailableError(...)
```

It does not validate that the value is a power of two in `[1, 512]`, which
is exactly the set `flash_5v_page_mask()` in `flash_5v_page.cpp:21-30`
accepts. For data that goes through `build_db.py`, this is safe today
because that generator's post-construction validator (`build_db.py:739-751`)
refuses to write `chip_database.json` at all if any chip's `page_size` is
out of that range. But `EpromDatabase._merge_databases`
(`database.py:188-213`) merges `~/.firestarter/database.json` user overrides
with no such validation, and `_map_data` (`database.py:411-413`) copies a
user-supplied `page_size` through with no range validation
(`int(page_size_val)`) onto the wire as `page-size`. A user override with,
for example, `page_size: 100` (not a power of two) or `page_size: 4096`
(above the 512-byte ceiling) passes this host gate, opens the serial port,
runs the full `INIT` phase, and only fails once the firmware's
`flash_5v_page_write_execute` rejects it in `MAIN`. This is several round
trips later than necessary, and after the state machine has already begun
exchanging data with the board.
**Fix:** Mirror the firmware's exact predicate host-side, for example:
```python
def _is_valid_flash4_page_size(page_size: int) -> bool:
    return 1 <= page_size <= 512 and (page_size & (page_size - 1)) == 0

...
page_size = (programmer_data or {}).get(JSON_KEY_PAGE_SIZE)
if not page_size or not _is_valid_flash4_page_size(page_size):
    raise PageSizeUnavailableError(...)
```
This keeps the two refusal paths from disagreeing on which page sizes are
valid, per this phase's own stated invariant, and gives a fast, pre-connect
refusal for a bad user override instead of a mid-transaction firmware error.

### WR-02: `build_db.py`'s page_size emit arm aborts the ENTIRE database build on one bad upstream record, instead of warning and skipping that record

**File:** `firestarter_app/tools/build_db.py:739-751`
**Issue:** Every other upstream-data problem in this file is handled by
printing a `WARN:`/`INFO:` line to stderr and `continue`-ing past just that
one chip. See the unknown-protocol gate at line 440-445 and the
unclassifiable-pinout skip at line 548-556. `interpret_timing` makes a
similar fatal-vs-warn split for `pulse-delay` at line 339-361, though that
one is a per-chip `raise` caught nowhere, so it too aborts the whole run.
This new page_size validator generalizes that same fail-loud choice to a
second field. The page_size emit arm (`build_db.py:667-677`) unconditionally
attaches `programming.page_size = raw_page_size` for every chip whose own
upstream `protocol_id` is `0x0D` or `0x05`, including a `raw_page_size` of
`0` (the default when the upstream `<ic>` tag has no `page_size` attribute
at all). The whole-database validator added by this phase
(`build_db.py:739-751`) then raises `ValueError` and refuses to write
`chip_database.json` for any chip carrying an invalid `page_size`,
including `0`. Every currently-shipped 0x05/0x0D chip in the real
`infoic.xml` happens to avoid that value, but a single new upstream chip
added in a future re-pin (protocol 0x05 or 0x0D, no `page_size` attribute)
would hit it, taking down generation for the entire 746-row database rather
than being skipped with a `WARN:` like every other unclassifiable chip in
this file.
**Fix:** Either (a) skip emitting `page_size` (leave the key absent, falling
back to firmware's AT28C floor) when `raw_page_size == 0` for a 0x0D/0x05
upstream chip and print a `WARN:` naming the chip, or (b) keep the hard
failure but explicitly document in a comment that this is a deliberate
departure from the file's warn-and-skip norm, because a wrong or absent page
size on this protocol is unsafe to guess at generation time too.

## Info

### IN-01: `flash_5v_page_write_execute`'s per-block "last byte" poll can fire mid-page on an unaligned chunk boundary

**File:** `firestarter_fw/src/proms/flash_5v_page.cpp:104-110`
**Issue:** `reached_page_end || is_last_byte` triggers
`flash_5v_page_wait_for_page_write` at the end of every host-supplied block,
even when the block's last byte does not fall on a real page boundary. This
can happen when a page size does not evenly divide the transport chunk size,
or when a write starts at an `--address` offset that is not page-aligned and
the block width is not itself a multiple of the page size. For every
currently-shipped combination this is harmless: host chunk sizes are
512/1024, both powers of two at least as large as the largest legal page
size of 512, so alignment holds for a whole-chip write starting at address
0. But the property is not enforced anywhere for an `--address`-offset
write, and is not covered by a native test with a non-page-size-multiple
`data_size`. This is pre-existing loop structure — only the mask computation
changed in this phase — so it is not a regression, but it is now more
reachable given the write path legitimately varies its page size per chip.
**Fix:** No code change is required for this phase's scope. Consider adding
a native test that drives `flash_5v_page_write_execute` with a `data_size`
that is not a multiple of `page_size`, simulating an unaligned `--address`
write, to pin the polling behavior. Alternatively, document the alignment
assumption as a precondition in a comment near the mask computation.

### IN-02: `page_size_gate.py`'s scope is protocol-0x05-only — the 18 native 0x0D page-size carriers ride the wire unconsumed by this phase's guard

**File:** `firestarter_app/firestarter/page_size_gate.py:49-60`, `firestarter_app/firestarter/database.py:543-551`
**Issue:** `convert_to_programmer` emits the `page-size` wire key whenever
`full_eprom_data.get("page_size")` is truthy, regardless of protocol, so the
18 upstream-native protocol-0x0D (`EEPROM_POLL`) rows established in Phase
149 also emit `page-size` on the wire. `page_size_gate.requires_page_size`
is deliberately scoped to `algorithm == FLASH4_PROTOCOL_ID` (0x05) only, per
its own docstring, so a 0x0D chip with an absent page_size is never refused
by this gate. This is consistent with the stated phase scope (0x05 only,
D-08) and not a defect of this phase, but it means the 0x0D emission's
actual firmware consumer, if any, was not verified here —
`eeprom_28c.cpp` was not in this review's scope. A future phase should show
that `eeprom_28c.cpp` either consumes `handle->page_size` correctly or that
the 0x0D emission is an intentional forward-compat placeholder, so the wire
field is not silently doing nothing for those 18 chips.
**Fix:** No action is required in this phase. Flagged for the next phase
that touches the 0x0D write path.

---

_Reviewed: 2026-09-15T00:00:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
