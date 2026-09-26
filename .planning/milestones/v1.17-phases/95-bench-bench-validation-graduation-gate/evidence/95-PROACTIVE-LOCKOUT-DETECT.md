# Phase 95: Proactive W29C040 §6.6 Boot-Block Lockout Detection

**Date:** 2026-06-29
**Type:** Operator-requested enhancement (dual-repo)
**Commits:** fw `bccd995` / app `e0bdea4` / meta `9ea029e`

## What Changed

### Firmware (`firestarter/src/proms/flash_type_4.cpp`)

Added a **proactive** §6.6 boot-block lockout check in `flash4_write_init`, running
BEFORE any page writes when the write targets a boot-block region (first or last 16K):

```
in_first_bb = (handle->address < 0x4000)
in_last_bb  = (handle->mem_size > 0x4000 && handle->address >= handle->mem_size - 0x4000)
```

If the region gate fires and `flash4_detect_boot_block_lockout(handle, handle->address)`
returns true (locked, reads 0xFF at 0x00002 / 0x7FFF2):

- **No FLAG_FORCE:** `LOG_ERROR_ID_U24(MSG_ERR_FL4_BOOT_BLOCK_LOCKED, address)` +
  `RESPONSE_CODE_ERROR` + `return` — aborts before any page writes.
- **FLAG_FORCE set:** `LOG_WARN_ID_U24(MSG_WARN_FL4_BOOT_BLOCK_LOCKED, address)` +
  `RESPONSE_CODE_WARNING` — falls through; write proceeds into the locked region
  (operator has explicitly forced it; the subsequent page poll will fail on the locked
  region, which is expected/acceptable).

The existing **reactive** detect (on `flash4_wait_for_page_write` timeout path) is kept
as-is — complementary fallback for partial-range writes that start outside but cross
into a boot-block boundary mid-write.

### Message Catalog — both repos

New message added at **0x85 (WARN)**:

```
MSG_WARN_FL4_BOOT_BLOCK_LOCKED = 0x85
"boot block locked -- 0x%06lx not programmable (W29C040 section 6.6 irreversible lockout, write forced)"
```

Existing message **0xBC (ERROR)** text fixed — "ss6.6" corrected to "section 6.6":

```
MSG_ERR_FL4_BOOT_BLOCK_LOCKED = 0xBC
"boot block locked -- 0x%06lx not programmable (W29C040 section 6.6 irreversible lockout)"
```

Both messages regenerated via `tools/catalog/codegen.py` from `messages.toml` into
`include/messages.h` (firmware) and `firestarter/messages.py` (host). Ruff-clean.
Total catalog: 67 messages (was 66).

### Host (`firestarter_app`)

- `--force` flag on the `write` command already correctly flows to `FLAG_FORCE` via
  `_build_op_flags(force=True)` → `build_flags(force=True)` → `FLAG_FORCE` in wire flags.
  No code changes needed; the path was already wired correctly.
- WARN messages during write (including the new 0x85) surface via
  `_handle_progress_response` → `logger.warning()` and do NOT raise `EpromOperationError`.
  The write proceeds after the warning (firmware forced path).
- The existing `_boot_block_hint_message` reactive heuristic is preserved as-is;
  no double-messaging risk (the proactive error/warning fires BEFORE the timeout, so the
  reactive heuristic's `MSG_ERR_FL4_VERIFY_TIMEOUT` pattern never triggers on the proactive
  abort path).

## Test Results

### Firmware native tests (`pio test -e native`)

**114/114 PASSED** (was 110/111 — added 4 new proactive detect tests, fixed 1 ERRORED)

New tests in `test/native/avr/test_val_flash4/test_val_flash4.cpp`:
| Test | Result |
|------|--------|
| `test_proactive_locked_no_force_sets_error` | PASSED |
| `test_proactive_locked_with_force_sets_warning` | PASSED |
| `test_proactive_unlocked_no_error_or_warning` | PASSED |
| `test_proactive_mid_chip_no_detect_invoked` | PASSED |

**Golden write trace: byte-identical** — 206 entries, unchanged. The proactive detect
(FLASH_ENABLE_ID + read + FLASH_DISABLE_ID) adds bus emissions during init, but the golden
trace test now calls `clear_bus_recording()` after `firestarter_operation_init` and before
`firestarter_operation_main`, isolating the execute-phase trace from init-phase detect
emissions. The `.inc` file was NOT re-pinned.

### Host tests (`pytest`)

**706/706 PASSED** — ruff check + format --check clean.

New tests in `tests/test_val_wire_flash4.py`:
| Test | Result |
|------|--------|
| `test_write_force_flag_sets_flag_force_in_wire_flags` | PASSED |
| `test_warn_fl4_boot_block_locked_in_catalog` | PASSED |
| `test_err_fl4_boot_block_locked_section_6_6_text` | PASSED |

### Codegen drift gate

Messages.py matches messages.toml exactly — drift-gate clean.

## Design Notes

- **Region gate**: Proactive detect only fires for addresses in the first 16K
  (`< 0x4000`) or last 16K (`>= mem_size - 0x4000`) of the chip. Mid-chip writes
  are never gated by a boot-block lock.
- **Force semantics**: Mirrors `eeprom_28c.cpp` / `flash_intel.cpp` / `primitives.h`
  patterns — FORCE converts ERROR to WARNING and falls through.
- **Phase 93 RCA connection**: This fix directly addresses the pre-Phase-95 STATE.md
  note "Minor polish: host diagnostic renders § as ss (ss6.6) — cosmetic message-string
  fix when convenient." Both the cosmetic fix and the proactive detect are implemented
  together since they touch the same message catalog infrastructure.
- **Locked chip note**: The seated W29C040 (permanently locked boot block per
  Phase 93 RCA) will trigger this proactive detect immediately on write at address 0,
  giving the operator a clean error before any doomed page writes. With `--force`, the
  write proceeds and fails at the poll step as expected.

---

## Bench confirmation (live, 2026-06-29 — Leonardo + Rev 2.0, locked W29C040 on /dev/ttyACM0)

New firmware flashed (`pio run -e leonardo -t upload`, chip stayed seated). Demonstrated on the real locked chip:

**No `--force`** — proactive ERROR *during init* (before any page write):
```
firestarter -p /dev/ttyACM0 write W29C040 <img> -a 0 -b
→ ERROR: boot block locked -- 0x000000 not programmable (W29C040 section 6.6 irreversible lockout)
→ Programmer error during init: ...
```
Failed at 0x000000 (write start) in write_init — the §6.6 detect read fired up front; no doomed page-write cycle attempted.

**With `--force`** — WARNING + proceed:
```
firestarter -p /dev/ttyACM0 write W29C040 <img> -a 0 -b --force
→ WARN: boot block locked -- 0x000000 ... section 6.6 irreversible lockout, write forced
→ (write proceeds 0%→100%) → ERROR: boot block locked -- 0x00003f not programmable ...
```
Warned up front (RESPONSE_CODE_WARNING / MSG_WARN_FL4_BOOT_BLOCK_LOCKED 0x85), proceeded as forced, then the locked silicon rejected the write at 0x00003f. Exactly the requested behavior. No 12V asserted in either case (CANERASE fix holds).
