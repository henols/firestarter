---
phase: 74-per-family-correctness-fixes-flash-gated
reviewed: 2026-06-18T00:00:00Z
depth: standard
files_reviewed: 8
files_reviewed_list:
  - firestarter/src/proms/flash_type_4.cpp
  - firestarter/src/proms/flash_utils.cpp
  - firestarter/include/flash_utils.h
  - firestarter/src/proms/flash_type_3.cpp
  - firestarter/test/native/avr/test_dispatch/test_configure_memory.cpp
  - firestarter/test/native/avr/test_val_flash4/test_val_flash4.cpp
  - firestarter_app/firestarter/database.py
  - firestarter_app/firestarter/ic_layout.py
findings:
  critical: 1
  warning: 4
  info: 3
  total: 8
status: issues_found
---

# Phase 74: Code Review Report

**Reviewed:** 2026-06-18
**Depth:** standard
**Files Reviewed:** 8
**Status:** issues_found

## Summary

Reviewed the Phase 74 Wave 1 changes: the flash4 page-write fix (SDP unlock +
data-driven page size), the new `flash_utils` shared AMD chip-ID helper, the
flash3 refactor to use it, two native test suites, and two comment-only Python
changes.

Positive verifications:
- The `flash_utils` chip-ID extraction (commit `d4a1b74`) is a faithful 1:1
  move of identical code out of flash3 and flash4 — no behavioral change in the
  ID-read or mismatch-handling path. Bus-state side effects are preserved.
- VPP-safety holds on the write path: `flash4_write_execute` and the SDP
  `flash_util_byte_flipping` only ever set `CTRL_READ_WRITE`; no
  `CTRL_VPP_REGULATOR_ENABLE` / `CTRL_VPP_P1_ENABLE` / `CTRL_VPP_VPE_DROP_ENABLE`
  bit is touched during write. The 12V VPP path remains confined to
  `flash4_erase_execute` (erase phase only), unchanged by this phase.
- Both Python files (`database.py`, `ic_layout.py`) are confirmed comment-only
  (commit `7769a42`); the only changed lines are inside `#` comment blocks.
  No constants/flag-bit edits, so no firmware/`constants.py` sync is required.
- The page-end poll-boundary rewrite `((address+1) % page_size) == 0` is
  correct and is a genuine fix over the old relative `== PAGE_SIZE - 1` form.

The dominant concern is **CR-01**: the `flash4_page_size()` capacity→page-size
heuristic produces the *wrong* page size for two whole flash4 families (the 64KB
and 256KB groups), reintroducing the exact mid-page-poll failure mode that this
phase set out to eliminate — just on different chips than the W29C040 it fixed.

## Critical Issues

### CR-01: `flash4_page_size()` derives an under-sized page for the 64KB and 256KB flash4 families — reintroduces the mid-page-poll write-failure bug

**File:** `firestarter/src/proms/flash_type_4.cpp:27-31`
**Issue:**
Page-buffer size on these chips is a *datasheet-fixed* property, **not** a
function of total capacity. The heuristic assumes capacity correlates with page
size, but it does not:

| Family (algorithm 0x05)            | mem_size | Real page | Derived (`flash4_page_size`) | Correct? |
|------------------------------------|----------|-----------|------------------------------|----------|
| AT29C256 / AT29C257 / AT29LV256    | 32768    | 64        | 64                           | yes      |
| AT29C512 / W29C512 / SST29EE512    | 65536    | **128**   | **64** (`<=65536`)           | **NO — under-sized** |
| SST29EE010 / AT29C010A / W29C010   | 131072   | 128       | 128                          | yes      |
| AT29C020 / W29C020 / SST29EE020    | 262144   | **256**   | **128** (`<=262144`)         | **NO — under-sized** |
| W29C040 / AT29C040 / AE29F4008     | 524288   | 256       | 256                          | yes      |

The phase's own root-cause analysis (file header comment, lines 19-26) states
the original W29C040 bug was that a *too-small* page size caused
`flash4_wait_for_page_write` to poll **mid-page** before the page had committed.
Deriving 64 for a 128-byte-page chip (AT29C512/W29C512/SST29EE512 — 5 of the 27
DB chips) and 128 for a 256-byte-page chip (AT29C020/W29C020/SST29EE020 — 5 more
DB chips) re-creates that *identical* failure mode. At address 63 (resp. 127)
the loop calls `flash4_wait_for_page_write` while the chip is still mid-page-load
on a 128-byte (resp. 256-byte) page; the DQ7/data poll then reads an
indeterminate value, producing either a `MSG_ERR_FL4_VERIFY_TIMEOUT` failure or
a silently corrupt write. 10 of 27 flash4 chips (~37%) are mis-sized.

The validation suite only exercises `mem_size = 524288` (W29C040), which lands
on a *correct* heuristic row, so the test green-light does not cover the broken
64KB/256KB rows. This is a test blind spot, not a proof of correctness.

**Fix:**
Do not infer page size from capacity. Carry the true page size from the chip
database (it is a per-chip datasheet constant) and pass it through the handle,
or encode an explicit per-family table. Minimal interim correction that at least
matches the known datasheet page sizes for the present DB:

```cpp
/* Page-buffer size is a per-chip datasheet constant, NOT a function of
 * capacity. Atmel/Winbond/SST AMD-page-write families:
 *   32K parts  -> 64-byte page
 *   64K parts  -> 128-byte page   (AT29C512, W29C512, SST29EE512)
 *   128K parts -> 128-byte page
 *   256K parts -> 256-byte page   (AT29C020, W29C020, SST29EE020)
 *   512K parts -> 256-byte page
 * Prefer threading an explicit page_size field from the DB through the
 * handle rather than this lookup. */
static uint32_t flash4_page_size(uint32_t mem_size) {
    if (mem_size <= 32768)  return 64;
    if (mem_size <= 131072) return 128;
    return 256;
}
```

Note the 64KB row flips from 64→128 and the 256KB row flips from 128→256.
Confirm each family's page size against its datasheet before shipping; the
robust fix is a DB-sourced `page-size` field so the firmware never guesses.

## Warnings

### WR-01: Page write assumes `handle->address` is page-aligned; a non-page-aligned start address misaligns SDP/page-commit boundaries

**File:** `firestarter/src/proms/flash_type_4.cpp:80-106`
**Issue:**
Correct page grouping depends on (a) `data_size` being an exact multiple of
`page_size` (currently true: 512/1024 buffers vs 64/128/256 pages) and (b) each
chunk's `handle->address` being page-aligned. For a non-page-aligned start
(e.g. `firestarter write <chip> -a 0x64`), `is_first_byte` forces an SDP unlock
mid-page and the first `flash4_wait_for_page_write` fires at the next
`(address+1)%page_size==0` boundary — i.e. after a *partial* leading page. The
AMD page-write protocol tolerates partial pages, so this is unlikely to corrupt,
but the loaded-then-committed grouping no longer matches the chip's natural page
boundaries and is not covered by any test.
**Fix:** Document the page-aligned-start precondition explicitly, and either
reject non-page-aligned write offsets in the host (`eprom_operations.py`) or add
a firmware guard that snaps page boundaries to `address & ~(page_size-1)`. At
minimum add a comment stating the alignment assumption the loop relies on.

### WR-02: `const byte_flip_t FLASH_*[]` arrays defined in `flash_utils.h` are duplicated into every including TU

**File:** `firestarter/include/flash_utils.h:24-60`
**Issue:**
The command-sequence arrays (`FLASH_ENABLE_ID`, `FLASH_DISABLE_ID`,
`FLASH_ERASE`, `FLASH_ENABLE_WRITE`, `FLASH_ENABLE_WRITE_PROTECTION`,
`FLASH_DISABLE_WRITE_PROTECTION`) are file-scope `const` definitions in a
header. In C++ file-scope `const` has internal linkage, so this is not an ODR
violation, but each of the 4 TUs that include `flash_utils.h`
(`flash_type_3.cpp`, `flash_type_4.cpp`, `flash_utils.cpp`, `eeprom_28c.cpp`)
gets its own private copy in `.rodata`. On a phase whose entire premise is
clawing back flash budget (89.5% Leonardo ceiling), emitting 4 copies of these
arrays works against that goal — and two of the six arrays
(`FLASH_ENABLE_WRITE_PROTECTION`, `FLASH_DISABLE_WRITE_PROTECTION`) appear
unused entirely (see IN-01). Note also `extern "C"` does not give C linkage to
these C++ `const` objects.
**Fix:** Declare the arrays `extern const byte_flip_t FLASH_*[]` in the header
and define them once in `flash_utils.cpp` (ideally in PROGMEM). This yields a
single shared copy and reclaims budget — directly serving the phase goal.

### WR-03: `FLASH_ENABLE_WRITE` and `FLASH_ENABLE_WRITE_PROTECTION` are byte-for-byte identical, inviting future divergence/confusion

**File:** `firestarter/include/flash_utils.h:42-52`
**Issue:**
`FLASH_ENABLE_WRITE` (`0xAA,0x55,0xA0`) and `FLASH_ENABLE_WRITE_PROTECTION`
(`0xAA,0x55,0xA0`) are identical sequences with contradictory names. A reader
fixing SDP behavior could edit the wrong one believing they differ, and the
duplicate copy is dead weight in the budget-constrained build. If the SDP/
write-protect-enable command genuinely shares the `0xA0` opcode, that should be
stated; if not, one of them is wrong.
**Fix:** Remove the unused `FLASH_ENABLE_WRITE_PROTECTION` (and the unused
`FLASH_DISABLE_WRITE_PROTECTION`) if no caller needs them, or add a comment
documenting why the enable-write and enable-write-protection opcodes coincide.

### WR-04: Validation suite does not cover the page sizes that CR-01 breaks

**File:** `firestarter/test/native/avr/test_val_flash4/test_val_flash4.cpp:61-69,177-191`
**Issue:**
Every handle in the suite hard-codes `mem_size = 524288`, the one capacity where
`flash4_page_size` happens to be correct. The SDP-emission test
(`test_flash4_write_execute_emits_sdp`) and the page-size logic are therefore
never exercised at 65536 or 262144 — exactly the inputs where the heuristic
mis-sizes the page (CR-01). The suite reports green while the bug is live.
**Fix:** Add `mem_size`-parameterized cases at 32768, 65536, 131072, 262144, and
524288 asserting the page-end poll fires at the correct datasheet page boundary
(e.g. that `flash4_wait_for_page_write` is invoked at address `page-1`, not
earlier). These cases will fail today and guard CR-01's fix.

## Info

### IN-01: Dead command-sequence constants

**File:** `firestarter/include/flash_utils.h:48-60`
**Issue:** `FLASH_ENABLE_WRITE_PROTECTION` and `FLASH_DISABLE_WRITE_PROTECTION`
have no callers anywhere in `src/`. They consume `.rodata` in a flash-tight
build.
**Fix:** Remove them, or guard behind a feature `#define` if reserved for a
planned write-protect command.

### IN-02: Hard-coded magic numbers in `flash4_page_size` and the poll loop

**File:** `firestarter/src/proms/flash_type_4.cpp:28-30,112`
**Issue:** The page-size thresholds (`65536`, `262144`) and page sizes
(`64`/`128`/`256`), plus the `1024`-iteration / `10`µs poll budget in
`flash4_wait_for_page_write`, are bare literals. The effective ~10ms commit
timeout is undocumented and not tied to any datasheet `tWC`.
**Fix:** Name them (`FLASH4_PAGE_POLL_MAX_ITERS`, `FLASH4_POLL_DELAY_US`) and add
a comment stating the resulting worst-case commit timeout, mirroring the
`FLASH_ERASE_DELAY_MS` style already used in `flash_type_3.cpp:29`.

### IN-03: Inconsistent erase-settle handling between flash3 and flash4 write-init

**File:** `firestarter/src/proms/flash_type_4.cpp:61-78` vs `firestarter/src/proms/flash_type_3.cpp:80-90`
**Issue:** `flash3_write_init` adds an explicit `delay(FLASH_ERASE_DELAY_MS)`
(105ms) after `flash3_erase_execute`, whereas `flash4_write_init` relies on the
inline `delay()`s inside `flash4_erase_execute` (~26ms total) with no post-erase
settle. This is pre-existing (not introduced this phase) and the two erase
mechanisms differ (flash4 uses a hardware OE=12V pulse, flash3 a command), so it
is likely intentional — flagged only so the divergence is a conscious decision
rather than an oversight.
**Fix:** Add a one-line comment in `flash4_write_init` noting that the erase
settle is absorbed by the inline delays in `flash4_erase_execute`, so a future
maintainer does not "fix" it by adding a redundant 105ms delay.

---

_Reviewed: 2026-06-18_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
