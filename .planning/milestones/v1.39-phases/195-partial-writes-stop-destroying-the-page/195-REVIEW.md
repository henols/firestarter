---
phase: 195-partial-writes-stop-destroying-the-page
reviewed: 2026-09-16T00:00:00Z
depth: standard
files_reviewed: 12
files_reviewed_list:
  - VALIDATED-EPROMS.md
  - firestarter_app/firestarter/cli_handlers.py
  - firestarter_app/firestarter/eprom_operations.py
  - firestarter_app/firestarter/exceptions.py
  - firestarter_app/firestarter/messages.py
  - firestarter_app/firestarter/page_size_gate.py
  - firestarter_app/tests/test_page_size_alignment_refusal.py
  - firestarter_app/tests/test_page_size_write_refusal.py
  - firestarter_app/tests/test_validated_parts_regression_surface.py
  - firestarter_fw/include/messages.h
  - firestarter_fw/src/proms/flash_5v_page.cpp
  - firestarter_fw/test/native/avr/test_val_5v_page/test_val_5v_page.cpp
  - tools/catalog/messages.toml
findings:
  critical: 0
  warning: 3
  info: 1
  total: 4
status: issues_found
---

# Phase 195: Code Review Report

**Reviewed:** 2026-09-16T00:00:00Z
**Depth:** standard
**Files Reviewed:** 12 (excluding the two generated files, `messages.h`/`messages.py`, and the
canonical `messages.toml`, all of which were read for cross-checking only, per this review's
project context)
**Status:** issues_found

## Summary

The two refusal layers this phase adds line up correctly with each other at every boundary I could
check mechanically: the host's `_ACCEPTED_PAGE_SIZES` set (`{1,2,4,8,16,32,64,128,256,512}`) is
byte-for-byte the same set `flash_5v_page_mask` accepts in firmware; the firmware's
`(address & page_mask) != 0 || (data_size & page_mask) != 0` refusal is an `||`, not an `&&` (a test
exists specifically to catch that class of bug, `test_5v_page_write_execute_refuses_unaligned_start_and_partial_length`);
zero-length payloads are accepted on both sides; and the firmware performs zero register writes on
every refusal path I traced. The buffer-size vs. page-size relationship (host chunk size is always
512 or 1024, both multiples of every accepted page size) means a per-chunk firmware refusal can
never fire mid-file for data the host guard already accepted, so the two layers do not disagree in
the cases the test suites exercise.

Three issues did turn up, all at the "boundary" and "test can pass vacuously" seams the task
specifically asked me to look at:

1. `require_page_alignment` computes its modulus using a value it never validates — it can be
   fooled by a negative address string that is an exact negative multiple of the page size.
   Reproduced live below.
2. One of the two "renders through a real CLI invocation" tests does not exercise the code path its
   name and docstring claim to cover — reproduced live below; the mocked `write_eprom` is never
   called.
3. `require_page_alignment`'s own fail-closed guarantee for an invalid (non-power-of-two,
   over-ceiling) page size depends entirely on `require_page_size` having already run first; the
   function does not enforce this itself, and both current call sites happen to get the order
   right.

None of these gave me a way to make firmware actually commit a partial page — the firmware guard is
the backstop in every case I could trace — so I have classified all three as WARNING rather than
BLOCKER. I flag them because they weaken the "not a blanket refusal, and not a leaky one either"
property this phase's own test docstrings claim to establish.

## Warnings

### WR-01: `require_page_alignment`'s modulo check accepts a negative address that is a false "aligned"

**File:** `firestarter_app/firestarter/page_size_gate.py:163-174`
**Issue:**

```python
try:
    start = parse_address(address_str) or 0
except ValueError as e:
    raise PageAlignmentError(...)
...
if start % page_size != 0 or length % page_size != 0:
    raise PageAlignmentError(...)
```

`parse_address` (`firestarter/address_parser.py:11-18`) only special-cases a `"0x"` substring; a
string like `"-256"` contains no `"0x"`, so it falls to `int(s)`, which happily returns `-256` — no
`ValueError`, no refusal. Python's `%` operator then returns a **non-negative** result for a
positive divisor even when the dividend is negative, so `-256 % 128 == 0`, and the guard treats a
negative start address as page-aligned.

Reproduced live against the current tree (no test changes, no source changes):

```
$ firestarter write W29C020 aligned.bin -a -256
# exit 0, no refusal
operator.write_eprom.call_args:
  ('W29C020', {...'page-size': 128...}, '.../aligned.bin',
   address_str='-256', operation_flags=0, pulse_us=0, pin1_hazard_acknowledged=True)
```

The negative string rides unmodified into `command_dict["address"]` in
`eprom_operations.py:_setup_operation` (same `parse_address(...) or 0` idiom), and from there into
the JSON sent to firmware as a negative "address" value. I cannot fully verify how
`firestarter_fw`'s `json_parser.c`/`memory_set_data` treats a negative address once it crosses the
wire (that path is outside this phase's required-reading set), but two outcomes are both plausible
and both bad: (a) it wraps to a huge unsigned value that some *other*, unrelated guard happens to
catch, in which case this guard's own "aligned" verdict was simply wrong and got lucky, or (b) the
low address bits survive truncation/masking and the write lands on a real, page-aligned, in-range
address the operator never asked for and does not expect — silently overwriting existing chip
content. Either way, the alignment guard's job — reject anything it cannot prove safe — is not done
here: a value that is not a valid physical address at all is treated as "provably aligned."

**Fix:** Reject a negative `start` (and, symmetrically, a negative `length`, though
`os.path.getsize` cannot produce one) before the modulo check, e.g.:

```python
if start < 0:
    raise PageAlignmentError(
        f"{chip_name.upper()}: write refused -- address {address_str!r} parses "
        "to a negative offset, which is not a valid chip address."
    )
```

---

### WR-02: `test_page_alignment_error_renders_through_cli_write_command` never invokes the mocked operator it is testing

**File:** `firestarter_app/tests/test_page_size_alignment_refusal.py:332-350`
**Issue:** The test builds a 64-byte payload and passes `-a 0x40` against the real W29C020 database
row (page size 128) specifically so the *rendered message text* matches the exact string the
production `_ALIGNMENT_REFUSAL_FORMAT` would produce for those inputs. But `cli_handlers.write()`
calls `page_size_gate.require_page_alignment(...)` itself (`cli_handlers.py:768-770`) **before** it
ever calls `app.eprom_operator.write_eprom(...)`. Because the chosen address/length combination is
genuinely misaligned against the *real* database entry, that first, CLI-owned call raises
`PageAlignmentError` with the identical text on its own — the mocked
`operator.write_eprom.side_effect` is never reached.

I reproduced this directly against the current tree:

```
result.exit_code: 1
operator.write_eprom.called: False
```

The test's own docstring (property 7: "PageAlignmentError surfaces through map_typed_errors ... both
directly and through a real CLI invocation") claims this test proves the *operator's* raised
exception renders correctly end-to-end through the CLI. It proves nothing of the kind: it is
indistinguishable from a test of the CLI's own duplicate gate call. A regression that broke
`map_typed_errors`' handling of a `PageAlignmentError` raised from deep inside `write_eprom` (or
inside `write_cycle_eprom`, which calls `write_eprom` directly with no CLI-level gate in front of
it) would not be caught by this test. Compare with
`test_page_size_write_refusal.py:223-239`'s equivalent test, which I also reproduced live and
confirmed *does* reach the mock (`operator.write_eprom.called: True`) — that one uses a page-aligned
payload against a chip name (`W29C512`) whose real database page size does not conflict with the
chosen inputs, so the CLI's own gate passes and the mock is the only thing that raises. That is the
right pattern; WR-02's test does not follow it.

**Fix:** Use inputs that pass the CLI's own `page_size_gate` calls (an aligned address/length pair,
as `test_page_size_write_refusal.py` already does), or patch `page_size_gate.require_page_alignment`
to a no-op for this specific test, so the assertions are actually exercising the mocked operator's
exception path rather than the CLI's redundant pre-flight check.

---

### WR-03: `require_page_alignment` trusts an un-validated `page_size` value; its own fail-closed guarantee is not self-contained

**File:** `firestarter_app/firestarter/page_size_gate.py:136-183` (contrast with `require_page_size`
at `:99-133`)
**Issue:** `require_page_size` refuses three classes of bad page size: absent/zero
(`:124-127`), and not-in-`_ACCEPTED_PAGE_SIZES` — i.e. non-power-of-two or above the 512 ceiling
(`:128-133`). `require_page_alignment` only checks for absent/zero (`:160-161`); it never checks
membership in `_ACCEPTED_PAGE_SIZES` before using the value as a modulus at `:174`. Both current
production call sites (`cli_handlers.py:767-770` and `eprom_operations.py:2009-2012`) happen to call
`require_page_size` immediately before `require_page_alignment`, so an invalid recorded value (e.g.
`96`) is always caught by the first call before the second ever runs with a bogus modulus — I
confirmed this ordering holds in both call sites. But `require_page_alignment` is a public,
independently-imported function (the test suite itself calls it standalone, e.g.
`test_page_size_alignment_refusal.py:272-292`, `:295-312`), and its own docstring claims to raise
`PageAlignmentError` "on any input it cannot resolve" — that claim is not true of an invalid-but-truthy
page size on its own. This is a "not a bug today, becomes one on the next caller who doesn't know the
ordering rule" gap, not a live BLOCKER, since the firmware's own `flash_5v_page_mask` independently
re-validates the page size on every chunk and would still refuse a genuinely bad value that somehow
reached it with a "passed" host-side verdict.

**Fix:** Have `require_page_alignment` call (or inline) the same `_ACCEPTED_PAGE_SIZES` membership
check `require_page_size` uses, so the function's own docstring claim is actually true regardless of
call order:

```python
if page_size not in _ACCEPTED_PAGE_SIZES:
    raise PageAlignmentError(_INVALID_PAGE_SIZE_FORMAT.format(...))
```

## Info

### IN-01: `require_page_alignment`'s file-size probe does not verify the path names a regular file

**File:** `firestarter_app/firestarter/page_size_gate.py:168-173`
**Issue:** `os.path.getsize(input_file_path)` succeeds (does not raise `OSError`) for a directory
path, and every accepted page size in `_ACCEPTED_PAGE_SIZES` evenly divides a typical directory
`stat` size (4096), so a directory passed as `input_file` would sail through the alignment check as
"page-exact" rather than being refused here. The user would still get an error later —
`_main_phase_send_data`'s subsequent `open(input_file_path, "rb")` raises `IsADirectoryError`, which
is not one of `_run_state_machine`'s caught exception types (`SerialError`, `SerialTimeoutError`,
`EpromOperationError`) and not one `map_typed_errors` catches either — so the failure mode is an
unhandled Python traceback surfacing to the CLI user instead of a clean, named refusal. This is a
robustness/UX gap, not a data-corruption risk (no register write occurs before the crash), and it
predates this phase's specific alignment logic in spirit (the same crash would occur without this
guard, just one function call later) — recorded as Info rather than Warning for that reason.
**Fix:** Optionally add `if not os.path.isfile(input_file_path): raise PageAlignmentError(...)`
alongside the existing `os.path.getsize` probe, so the failure is named and consistent with this
module's fail-closed style rather than falling through to an unrelated, unhandled exception later.

---

_Reviewed: 2026-09-16T00:00:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
