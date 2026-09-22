---
phase: 205-the-pre-flights-leave-the-firmware
reviewed: 2026-09-22T18:47:31Z
depth: standard
files_reviewed: 44
files_reviewed_list:
  - firestarter_app/firestarter/chip_test.py
  - firestarter_app/firestarter/cli_handlers.py
  - firestarter_app/firestarter/constants.py
  - firestarter_app/firestarter/eprom_operations.py
  - firestarter_app/firestarter/serial_comm.py
  - firestarter_app/firestarter/write_blank_guard.py
  - firestarter_app/tests/__snapshots__/test_characterization.ambr
  - firestarter_app/tests/fake_chip.py
  - firestarter_app/tests/fixtures/report_shapes.py
  - firestarter_app/tests/test_chip_test_uv_slot_write.py
  - firestarter_app/tests/test_cli_handlers.py
  - firestarter_app/tests/test_eprom_operations.py
  - firestarter_app/tests/test_uv_mask.py
  - firestarter_app/tests/test_write_blank_guard.py
  - firestarter_app/tests/test_write_blank_guard_pinning.py
  - firestarter_fw/CLAUDE.md
  - firestarter_fw/PROTOCOLS.md
  - firestarter_fw/include/firestarter.h
  - firestarter_fw/include/memory_utils.h
  - firestarter_fw/src/firestarter.cpp
  - firestarter_fw/src/json_parser.c
  - firestarter_fw/src/proms/eeprom_28c.cpp
  - firestarter_fw/src/proms/eprom.cpp
  - firestarter_fw/src/proms/flash_5v_page.cpp
  - firestarter_fw/src/proms/flash_intel.cpp
  - firestarter_fw/src/proms/flash_nor_unlock.cpp
  - firestarter_fw/src/proms/memory.cpp
  - firestarter_fw/test/native/avr/test_eeprom28c_sdp/test_eeprom28c_sdp.cpp
  - firestarter_fw/test/native/avr/test_eprom_params_v131/test_eprom_params_v131.cpp
  - firestarter_fw/test/native/avr/test_flash_intel_vpp/test_flash_intel_vpp.cpp
  - firestarter_fw/test/native/avr/test_read_timing/test_read_timing_params.cpp
  - firestarter_fw/test/native/avr/test_sdp_harness/test_sdp_harness.cpp
  - firestarter_fw/test/native/avr/test_val_5v_page/test_val_5v_page.cpp
  - firestarter_fw/test/native/avr/test_val_eprom/host_stubs.cpp
  - firestarter_fw/test/native/avr/test_val_eprom/test_val_eprom.cpp
  - firestarter_fw/test/native/avr/test_val_flash_intel/test_val_flash_intel.cpp
  - firestarter_fw/test/native/avr/test_verify_error_ids/test_verify_error_ids.cpp
  - firestarter_fw/tests/golden/protocol_branch_inventory.json
  - firestarter_fw/tests/test_config_schema_pinned.py
  - firestarter_fw/tests/test_flash_path_record_sync.py
  - firestarter_fw/tests/test_progress_emission_is_leonardo_only.py
  - firestarter_fw/tests/test_protocol_branch_inventory.py
  - firestarter_fw/tests/test_verify_survival_source_contract.py
  - tools/catalog/messages.toml
findings:
  critical: 1
  warning: 2
  info: 1
  total: 4
status: issues_found
---

# Phase 205: Code Review Report

**Reviewed:** 2026-09-22T18:47:31Z
**Depth:** standard
**Files Reviewed:** 44
**Status:** issues_found

## Summary

Phase 205 removes the firmware's in-algorithm blank-check pre-flights and retires the wire bit
that used to suppress them, moving the capability to the host (`write_blank_guard.py` /
`check_eprom_blank`). This is overwhelmingly a deletion-shaped change, and the deletion itself is
executed carefully: `memory_verify_execute`, `eeprom28c_verify_page_readback`,
`flash_util_verify_operation` and `MSG_ERR_VERIFY` all survive and are still reachable from every
write path that shipped them; `mem_util_operation_end` survives with both its callers (progress
scoping, not blank-check) intact; the negative-address refusal in `json_parser.c` is scoped to the
`key_address` row only (`FIELD_REJECT_NEGATIVE`), and every other `simple_strtoul` call site
(`ctrl_flags`, bus-config address lines, static-high lines) is untouched; `-b`/`--no-blank-check`
on `write` still requires a separate `--skip-erase` to suppress the erase, so the historical
"`-b` silently skips the erase too" defect class does not recur; and the new
`test_verify_survival_source_contract.py` mechanically pins all of this at the source level.

The one substantive gap found is in `write_blank_guard.is_erase_exempt`, which this phase's own
docstring promotes to "the whole safety net": it treats `FLAG_CAN_ERASE && !FLAG_SKIP_ERASE` as
proof that the *entire target write region* was just erased, for protocol `0x06` (AMD/JEDEC NOR
unlock, 190 shipped chips) exactly as it does for `0x10` (Intel flash, whole-device only). But
`flash_nor_unlock_erase_execute` branches on `handle->address`: a non-zero address (i.e. any
`write -a <addr>` on an erase-capable `0x06` chip) erases only the addressed *sector*, not the
whole device. Before this phase, the firmware's own now-deleted write-init blank check scanned the
whole device after that erase and would have caught an unerased remainder as a refusal (safe,
if occasionally over-conservative); after this phase, nothing does. See CR-01.

## Critical Issues

### CR-01: `write_blank_guard.is_erase_exempt` treats a protocol-0x06 sector erase as a whole-device erase, and nothing else catches it post-205

**File:** `firestarter_app/firestarter/write_blank_guard.py:156-170` (`is_erase_exempt`), and
`firestarter_app/firestarter/eprom_operations.py:2385-2401` (`write_eprom`'s guard-skip branch)
**Firmware:** `firestarter_fw/src/proms/flash_nor_unlock.cpp:69-97` (`flash_nor_unlock_write_init`),
`firestarter_fw/src/proms/flash_nor_unlock.cpp:111-119` (`flash_nor_unlock_erase_execute`)

**Issue:** `GUARDED_PROTOCOL_IDS` (`write_blank_guard.py:58`) documents protocol `0x06` as
"whole-device, after an erase" — the same category as `0x10` (Intel flash). `is_erase_exempt`
implements that as a pure flag test: `FLAG_CAN_ERASE` set and `FLAG_SKIP_ERASE` clear means "skip
the host's own blank-check read; the erase already proved the region blank." For `0x10`
(`flash_intel_erase_execute`, `flash_intel.cpp:105-114`) that assumption holds structurally: the
erase always hits hard-coded address `0` and is unconditionally chip-wide.

For `0x06` it does not. `flash_nor_unlock_write_init` (`flash_nor_unlock.cpp:69-97`) calls
`flash_nor_unlock_erase_execute(handle)` using the **write's own** `handle->address` — the value
the host's `-a`/`--address` option sets. `flash_nor_unlock_erase_execute` (`flash_nor_unlock.cpp:
111-119`) branches on that address: `address == 0` does a whole-chip erase, but any non-zero
address does a **sector** erase (`flash_nor_unlock_sector_erase`) instead. So `firestarter write
<chip> <file> -a 0x10000` on any `FLAG_CAN_ERASE`-set `0x06` chip (190 shipped rows, e.g. every
AMD/ALLIANCE AM29F*/AS29F* row in the database) erases only the sector containing `0x10000`, not
the device, and not necessarily the whole of the write's own target region if that region spans a
sector boundary or the region size differs from the sector size.

`is_erase_exempt` has no address-awareness at all — it cannot distinguish "erase just ran, whole
device" from "erase just ran, one sector, possibly not even the one this write targets." Under the
default `blank_check_requested=True`, `write_eprom` reads this exemption as `True` and skips its
own host-side blank-check read entirely (`eprom_operations.py:2385-2401`), so **no check of any
kind** runs against the target region before the write proceeds.

This exact hazard class is explicitly recognised elsewhere in this same phase:
`cli_handlers.py`'s `_erase_sector_blank_refusal_exit_code` (`cli_handlers.py:1084-1123`) refuses
`erase -s <addr> -b` for precisely this reason ("a non-zero `handle->address` selects a SECTOR
erase in `flash_nor_unlock_erase_execute`, not the whole-device erase D-01's post-erase check
assumes"). That refusal protects only the standalone `erase` command's own post-erase check. It
does nothing for `write`'s pre-write guard, which reaches the identical firmware branch through
the identical field (`handle->address`, sourced from `write`'s `-a`) and has no equivalent
refusal or region-awareness.

Before Phase 205, the firmware's own write-init blank check (now deleted) scanned the whole
device after this same erase call and would have refused a write into a region the sector erase
missed — a safety net that happened to catch this specific gap as a side effect. Phase 205's own
stated premise is that the host guard is "the whole safety net" now (`write_blank_guard.py:27-38`).
For this one protocol/address combination, there is no net at all.

**Fix:** Make `is_erase_exempt` (or its caller) address-aware for protocol `0x06`, mirroring the
CLI's own sector/whole-device distinction instead of leaving it unaddressed for `write`:

```python
# write_blank_guard.py
_NOR_UNLOCK_PROTOCOL_ID = 0x06

def is_erase_exempt(
    programmer_data: Mapping[str, Any] | None,
    operation_flags: int,
    *,
    address: int = 0,
) -> bool:
    flags = effective_flags(programmer_data, operation_flags)
    erase_claimed = bool(flags & FLAG_CAN_ERASE) and not bool(flags & FLAG_SKIP_ERASE)
    if not erase_claimed:
        return False
    algorithm = (programmer_data or {}).get("algorithm")
    if algorithm == _NOR_UNLOCK_PROTOCOL_ID and address != 0:
        # flash_nor_unlock_erase_execute erases only the addressed SECTOR
        # when handle->address != 0 -- never treat that as proof the whole
        # target region is blank.
        return False
    return True
```

and thread the write's resolved start address into the `is_erase_exempt` / `requires_blank_check`
call in `write_eprom` (`eprom_operations.py:2385-2391`), the same address already parsed a few
lines above for `require_non_negative_address`. At minimum, until a full fix lands, refuse (or
warn loudly on) a non-zero `-a` write to a `FLAG_CAN_ERASE` protocol-`0x06` chip the same way
`erase -s -b` is refused today.

## Warnings

### WR-01: `firestarter_fw/CLAUDE.md`'s `MSG_DATA_PROGRESS` payload description contradicts the code it was edited alongside

**File:** `firestarter_fw/CLAUDE.md` (the "Intra-block progress" bullet in the 27C section)
**Firmware:** `firestarter_fw/src/proms/eprom.cpp:385-406`

**Issue:** This paragraph was itself edited in this phase (it now says "`0xE0` has exactly one
emitter in the firmware now... its payload contract is no longer shared with a second site (v1.41
phase 205 retired the firmware's own blank-check machinery...)"), and it states: "The payload is
the absolute chip address plus `handle->mem_size`." The actual emitter,
`LOG_DATA_ID_U32_U32(MSG_DATA_PROGRESS, handle->address + i, op_end)` (`eprom.cpp:405`), sends
`op_end = mem_util_operation_end(handle)` — which is `handle->mem_size` only for a whole-device
operation, and the (clamped) `handle->region_end` for a bounded one. `eprom.cpp`'s own comment at
the emit site explicitly calls itself "the sole definition of its payload contract: 'the end of
the operation's range', not merely 'the device size'" (`eprom.cpp:387-390`) — i.e. it already
disagrees with the CLAUDE.md wording it was edited next to.

**Fix:** Update the CLAUDE.md bullet to match the code's own stated contract, e.g. "The payload is
the absolute chip address plus the operation's end address (`mem_util_operation_end`) — the whole
device for an unscoped operation, the region end for a bounded one," instead of hard-coding
`handle->mem_size`.

### WR-02: `write_blank_guard.is_erase_exempt`'s only test coverage never exercises the address dimension CR-01 depends on

**File:** `firestarter_app/tests/test_write_blank_guard.py:133-143`

**Issue:** `test_is_erase_exempt_true_when_can_erase_set_and_skip_erase_clear`,
`test_is_erase_exempt_false_when_skip_erase_re_arms_the_guard` and
`test_is_erase_exempt_false_when_can_erase_not_set` are the entire direct test surface for
`is_erase_exempt`, and none of them pass an `algorithm`/protocol id or a non-zero address. The
function's real-world correctness for protocol `0x06` depends entirely on the firmware's
address-dependent erase-scope branch (CR-01), and no test in this module — or in
`test_write_blank_guard_pinning.py` — pins that dependency at all. A regression here would ship
silently.

**Fix:** Once CR-01 is fixed, add a case asserting `is_erase_exempt` (or its caller) returns
`False` for `algorithm=0x06` with a non-zero write address even when `FLAG_CAN_ERASE` is set and
`FLAG_SKIP_ERASE` is clear, alongside a companion case confirming the exemption still holds at
address `0` (whole-chip erase) and for `algorithm=0x10` regardless of address.

## Info

### IN-01: `_setup_operation`'s `JSON_KEY_REGION_END` comment describes a premise that no longer matches the field's current purpose

**File:** `firestarter_app/firestarter/eprom_operations.py:619-636`

**Issue:** The comment introducing the `region-end` emission still frames it purely as scoping
"the write-init blank check on the firmware side," and ends with "This block's own premise expires
in Phase 205, which removes the firmware-side write-init blank check this key exists to scope."
Phase 205 has now landed, and the code was *not* removed — correctly, because `region-end` is
still consumed by `mem_util_operation_end` for the write-path's intra-block progress payload
(`eprom.cpp:317`, `memory.cpp:424-432`). The comment reads as a stale prediction rather than a
description of the field's current (still load-bearing, just for a different reason) purpose, and
could mislead a future reader into deleting a still-needed block on the assumption that its stated
"premise" already expired.

**Fix:** Update the comment to state the field's current purpose (bounding the write-path progress
payload / `mem_util_operation_end`, not blank-check scoping) rather than leaving the pre-205
framing and its now-resolved "expires in Phase 205" prediction in place.

---

_Reviewed: 2026-09-22T18:47:31Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
