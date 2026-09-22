---
phase: 205-the-pre-flights-leave-the-firmware
reviewed: 2026-09-22T21:37:41Z
depth: standard
files_reviewed: 4
files_reviewed_list:
  - firestarter_app/firestarter/write_blank_guard.py
  - firestarter_app/firestarter/eprom_operations.py
  - firestarter_app/tests/test_write_blank_guard.py
  - firestarter_app/tests/test_write_blank_guard_pinning.py
findings:
  critical: 0
  warning: 0
  info: 1
  total: 1
status: issues_found
---

# Phase 205: Code Review Report (incremental — plan 205-08 / CR-01 gap closure)

**Reviewed:** 2026-09-22T21:37:41Z
**Depth:** standard
**Files Reviewed:** 4
**Status:** issues_found

## Summary

This is an incremental review of plan 205-08 only, which closes finding CR-01 from the phase's
prior review: `is_erase_exempt` was address-blind, so a `write -a <non-zero>` on protocol `0x06`
(AMD/JEDEC NOR-unlock) was wrongly exempted from the host blank guard even though the firmware only
runs a whole-chip erase at address 0 and a single-sector erase otherwise.

The fix adds a keyword-only `address: int = 0` to `is_erase_exempt` / `requires_blank_check`,
narrows the exemption to withdraw only on `NOR_UNLOCK_PROTOCOL_ID` (0x06) at a non-zero address, and
has `write_eprom` resolve its own start address once (`guard_address`) to thread through.

I traced this claim against the actual firmware sources rather than trusting the docstrings:

- `flash_nor_unlock_erase_execute` (`firestarter_fw/src/proms/flash_nor_unlock.cpp:111-119`) —
  confirmed: sector erase unless `handle->address == 0`, and `handle->address` there is set once at
  `flash_nor_unlock_write_init` from the write command's own `address` field (the same field the
  host resolves from `-a`).
- `flash_intel_erase_execute` (`flash_intel.cpp:105-114`) — confirmed: erase setup/confirm bytes go
  to hard-coded address `0`, `handle->address` is never read for scope.
- `eprom_internal_erase` (`eprom.cpp:558-576`, backing protocols `0x07`/`0x08`/`0x0B`) — confirmed:
  `handle->firestarter_set_address(handle, 0x0000)` is hard-coded, `handle->address` is never read.

So the `0x06`-only narrowing is exactly right — no other guarded protocol's erase scope depends on
the address.

I also checked address agreement between the guard's own resolution and the write's real connect.
Both `write_eprom`'s `guard_address` computation and `_setup_operation`'s own `addr` computation call
the identical `parse_address(address_str) or 0` expression against the identical `address_str`; a
negative address is already refused earlier by `require_non_negative_address` (same parser, same
input) before either computation is reached, and an unparseable address resolves to `0` in the guard
(deliberately, per its own comment) while `_setup_operation` independently re-parses and fails the
connect through the pre-existing `ValueError` → `(None, 0)` path, before `find_and_connect` is ever
called. I confirmed there is exactly one call site of `requires_blank_check` in the package
(`eprom_operations.py:2403`), so no other caller can bypass the new address threading with a stale
default.

I also verified the new tests are not tautological: reverting only the address-narrowing branch in
`is_erase_exempt` (while keeping `NOR_UNLOCK_PROTOCOL_ID` and the `address` parameter in place, so
this isn't just an import-error false failure) makes exactly the CR-01-relevant tests fail —
`test_is_erase_exempt_is_false_for_nor_unlock_at_a_non_zero_address`,
`test_requires_blank_check_is_true_for_nor_unlock_at_a_non_zero_address`,
`test_write_at_a_non_zero_address_on_an_erase_capable_nor_unlock_part_pays_a_guard_read`,
`test_address_aware_exemption_fires_against_real_resolve_chip_dicts`, and
`test_write_at_a_non_zero_address_on_a_non_blank_nor_unlock_region_is_refused` — while the rest of
the suite stays green. With the fix restored, the full `test_write_blank_guard*.py` suite (108
tests) passes on the CI-pinned Python 3.11 venv, and `ruff check`/`ruff format --check` are clean on
all four files.

No BLOCKER or WARNING findings. This gap-closure plan does what it claims, the safety property it
restores is real (traced against firmware source, not assumed from the docstring), and the address
resolution agrees between the guard and the actual write connect at every code path I could find.

## Info

### IN-01: `test_every_shipped_nor_unlock_row_resolves_erase_capable` doesn't narrow its exception catch to match its own stated idiom

**File:** `firestarter_app/tests/test_write_blank_guard_pinning.py:263-266`
**Issue:** The new census test catches only `(ChipNotFoundError, ChipNotImplementedError)` around
`resolve_chip(name, db=db)` when building `erase_capable_rows`. That mirrors the precedent function
the docstring cites, so it's a deliberate, consistent choice — but it means any *other* exception a
future malformed protocol-0x06 row could raise out of `resolve_chip` (e.g. a `KeyError` from a
missing pinout field) would fail this test with an unrelated traceback rather than being folded into
the `nor_unlock_rows ^ erase_capable_rows` diagnostic the test is designed to print. Low value given
it mirrors existing precedent in the same file, but worth a one-line note for whoever debugs a future
red run here.
**Fix:** Optional — no action required now. If this test ever goes red on an exception type outside
the caught pair, that's the signal to either broaden the catch or (better) treat it as a real defect
in the affected row rather than assuming the test itself is wrong.

---

_Reviewed: 2026-09-22T21:37:41Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
