---
phase: 201-a-partial-write-is-gated-on-its-own-region
reviewed: 2026-09-20T00:00:00Z
depth: standard
files_reviewed: 15
files_reviewed_list:
  - firestarter_fw/include/firestarter.h
  - firestarter_fw/include/memory_utils.h
  - firestarter_fw/src/eprom_operations.cpp
  - firestarter_fw/src/json_parser.c
  - firestarter_fw/src/proms/eprom.cpp
  - firestarter_fw/src/proms/memory.cpp
  - firestarter_fw/test/native/avr/test_val_eprom/host_stubs.cpp
  - firestarter_fw/test/native/avr/test_val_eprom/test_val_eprom.cpp
  - firestarter_fw/tests/test_blank_check_region_source_contract.py
  - firestarter_fw/tests/test_progress_emission_is_leonardo_only.py
  - firestarter_app/firestarter/constants.py
  - firestarter_app/firestarter/eprom_operations.py
  - firestarter_app/tests/fake_chip.py
  - firestarter_app/tests/test_chip_test_uv_slot_write.py
  - firestarter_app/tests/test_eprom_operations.py
findings:
  critical: 0
  warning: 2
  info: 1
  total: 3
status: issues_found
---

# Phase 201: Code Review Report

**Reviewed:** 2026-09-20T00:00:00Z
**Depth:** standard
**Files Reviewed:** 15
**Status:** issues_found

## Summary

This phase adds an absolute, exclusive `region-end` wire field so the firmware's write-init blank
check (and, more broadly, the write/verify MAIN-phase out-of-range/done bound) can scope to the
operation's own region instead of the whole device. I traced the arithmetic end to end: the
`0 = absent = whole device` fallback and the fail-closed `region_end > mem_size` clamp
(`mem_util_operation_end`, `memory.cpp:456-461`), the chunked re-entry of
`mem_util_blank_check_region` (cursor saved/restored via `blank_check_saved_address`, `start` read
only on the first call), the host's `region_end = addr + region_length` construction
(`eprom_operations.py:513-518`), and the six whole-device callers that must stay untouched (verified
both by reading `flash_intel.cpp`/`flash_nor_unlock.cpp`/`eeprom_28c.cpp`/`flash_5v_page.cpp` and by
running the new `tests/test_blank_check_region_source_contract.py` gate, which passes). I built and
ran the native Unity suite (`pio test -e native -f "*test_val_eprom*"`, 13/13 passed) and the
relevant Python suites (`test_eprom_operations.py -k "region_end or blank_region"`,
`test_chip_test_uv_slot_write.py`) — all green.

I specifically checked whether `start > end` can ever reach `mem_util_blank_check_region` with
`start` derived from a write's target address that is genuinely still writable (i.e., whether the
scoped blank check could silently pass on a region that the MAIN phase then actually programs).
It cannot: `start` and `end` are computed from the exact same `handle->address` /
`mem_util_operation_end(handle)` pair that `_process_incoming_data`'s own
`handle->address >= op_end` guard uses immediately afterward, so any `start > end` case is
necessarily also a case where the MAIN phase writes zero bytes. I did not find a case where a
non-blank byte inside the actually-written region escapes detection, or where the region scoping
regresses the pre-existing whole-device paths (erase-end, standalone blank-check, flash/nor-unlock).

No BLOCKER-level defects found. Two WARNING-level gaps and one INFO-level observation below.

## Warnings

### WR-01: `region-end` has no unit test through the actual JSON parser

**File:** `firestarter_fw/src/json_parser.c:75,158,296`
**Issue:** Every test that exercises `handle->region_end` (the native `test_val_eprom.cpp` D-16.1
cases, and all the Python-side tests) sets the field directly on the C struct or asserts only the
Python-side wire-key string constant. Nothing parses a raw JSON string containing `"region-end":N`
through `json_parse()` and asserts the result lands in `handle->region_end` — the actual mechanism
`key_parsers[]` and `store_field()` implement, and the one place a typo in `key_region_end`'s
PROGMEM string, a copy-paste error in the `FIELD(key_region_end, region_end, 0)` row, or an
`offsetof`/width mismatch would surface. The `_Static_assert`s (`json_parser.c:215-218`) only prove
the offset fits the `uint8_t` column and the width fits a 32-bit store; they do not prove the table
writes the *right* member, and this module's own comment at `json_parser.c:169` says exactly that
("only the native parse tests do" — but no such native parse test exists for this field).

The per-command reset to 0 (`json_parser.c:287-296`) is similarly untested end-to-end: no test
issues two sequential `json_parse()` calls (a write with a `region-end`, then a blank-check with
none) to prove the second command is not narrowed by the first's stale value — the exact fail-open
scenario the reset's own comment warns about.

This is a real gap given how load-bearing the field is (every write/verify's out-of-range and
blank-check bound now derives from it) and how cheap the fix is: `read_settling_us`/`read_strobe_us`
already have exactly this kind of test, in the same pinned native environment.

**Fix:** Add cases to `firestarter_fw/test/native/avr/test_read_timing/test_read_timing_params.cpp`
(or a new sibling suite, already wired into both `native` and `native_nodevtools` via `[native_base]`
if placed under an existing `test_filter` entry — otherwise add the two new lines per
`CLAUDE.md`'s "Adding a native test suite" section), following the existing `T1`/`T3` pattern:

```cpp
void test_region_end_parsed_from_json(void) {
    const char* json = "{\"cmd\":2,\"region-end\":12288}";
    firestarter_handle_t h = make_handle(CMD_WRITE);
    int rc = parse_json(json, &h);
    TEST_ASSERT_EQUAL_INT(0, rc);
    TEST_ASSERT_EQUAL_UINT32(12288, h.region_end);
}

void test_region_end_resets_between_commands(void) {
    firestarter_handle_t h = make_handle(CMD_WRITE);
    TEST_ASSERT_EQUAL_INT(0, parse_json("{\"cmd\":2,\"region-end\":12288}", &h));
    TEST_ASSERT_EQUAL_UINT32(12288, h.region_end);
    TEST_ASSERT_EQUAL_INT(0, parse_json("{\"cmd\":4}", &h));
    TEST_ASSERT_EQUAL_UINT32(0, h.region_end);
}
```

### WR-02: `mem_util_blank_check_region` fail-opens silently on a malformed `start > end`

**File:** `firestarter_fw/src/proms/memory.cpp:470-485`
**Issue:** When `start > end` (e.g. `handle->address` is greater than the resolved operation end),
the function's first-call branch sets `handle->address = start` unconditionally, and the scan loop's
bound `for (i = handle->address; i < end_address && i < end; i++)` never executes because
`i (== start) < end` is false from the first iteration. The function then reports "blank" (no error)
having scanned zero bytes, and on the next call immediately completes (`handle->address >= end` is
true) — there is no explicit refusal, log, or assertion for this state anywhere in the function.

I confirmed this can never cause an actual out-of-range write today, because `start` and `end` are
always derived from the same `handle->address` / `mem_util_operation_end(handle)` pair that
`_process_incoming_data`'s own `handle->address >= op_end` guard (`eprom_operations.cpp:100`) checks
immediately afterward — so `start > end` at blank-check time necessarily implies the MAIN phase
writes zero bytes for that operation. That safety property, however, lives entirely in a *different*
function in a *different* file, and nothing in `mem_util_blank_check_region` itself documents or
enforces it. A future caller of this function (it already has one call site outside the wrapper,
`eprom.cpp:145`, and the source-contract gate only pins the *count* of call sites, not their argument
invariants) that does not happen to share that same downstream guard would silently treat an
unscanned region as blank.

**Fix:** Make the function locally defensive instead of relying on the caller's downstream guard,
e.g.:

```c
void mem_util_blank_check_region(firestarter_handle_t* handle, uint32_t start, uint32_t end) {
    if (!is_operation_in_progress(handle)) {
        set_operation_in_progress(handle);
        blank_check_saved_address = handle->address;
        handle->address = start < end ? start : end;  // fail closed: a malformed
                                                        // start>end scans nothing but
                                                        // completes immediately, never
                                                        // silently "passes" a real span
    } else {
        ...
```

or add an explicit `LOG_ERROR_ID`/assert path if `start > end` should be treated as a protocol
error rather than a silent no-scan.

## Info

### IN-01: TOCTOU window between `os.path.getsize()` and the later file read

**File:** `firestarter_app/firestarter/eprom_operations.py:2045-2048,2157-2160`
**Issue:** `write_eprom`/`verify_eprom` compute `region_length = os.path.getsize(input_file_path)`
before entering `_operation_context`, and the file is opened again later in
`_main_phase_send_data` (`eprom_operations.py:788`). If the file's size changed between these two
reads (e.g. another process truncated or extended it), the `region-end` sent to the firmware would
no longer match the bytes actually transferred, and the firmware's out-of-range guard would be
checking against a stale bound. This is a theoretical local-file race, not remotely triggerable, and
consistent with how the file is already read twice elsewhere in this module (e.g.
`require_page_alignment`) — noted for completeness, not blocking.

---

_Reviewed: 2026-09-20T00:00:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
