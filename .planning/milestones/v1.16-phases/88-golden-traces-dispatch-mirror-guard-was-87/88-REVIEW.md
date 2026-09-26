---
phase: 88-golden-traces-dispatch-mirror-guard-was-87
reviewed: 2026-06-26T10:30:00Z
depth: standard
files_reviewed: 7
files_reviewed_list:
  - firestarter/test/native/avr/_shared/golden_trace.h
  - firestarter/test/native/avr/test_val_eprom/test_val_eprom.cpp
  - firestarter/test/native/avr/test_val_eeprom28c/test_val_eeprom28c.cpp
  - firestarter/test/native/avr/test_val_flash_intel/test_val_flash_intel.cpp
  - firestarter/test/native/avr/test_val_flash3/test_val_flash3.cpp
  - firestarter/test/native/avr/test_val_flash4/test_val_flash4.cpp
  - firestarter_app/tests/test_dispatch_mirror.py
findings:
  critical: 0
  warning: 4
  info: 3
  total: 7
status: issues_found
---

# Phase 88: Code Review Report

**Reviewed:** 2026-06-26T10:30:00Z
**Depth:** standard
**Files Reviewed:** 7
**Status:** issues_found

## Summary

Phase 88 delivers: (a) byte-exact golden register-trace tests for five
firmware handler families via a shared `assert_trace_eq` helper in
`golden_trace.h`; and (b) a three-way dispatch-mirror invariant test in Python.

The overall architecture is sound. The golden-trace helper itself (including
the Pitfall 1 low-byte caveat documentation, the Pitfall 2 anti-truncation
guard at 256 entries, and the Pitfall 3 re-assign-after-configure discipline)
is well-designed. The Python dispatch mirror test runs clean against the
current tree (2 passed), and `ruff`/`mypy` both pass.

Four warnings were identified: three for missing post-execute `response_code`
assertions in golden-trace tests (false-pass risk if a mock misconfiguration
causes silent error termination before the trace is fully populated), and one
for unguarded null-pointer dereferences in two legacy FIX-02B tests. Three
informational findings cover a misleading fixture comment, a `KeyError` vs
assertion error failure mode in the Python test, and a GOLDEN_BLESS workflow
hazard when the recording buffer is exactly full.

---

## Warnings

### WR-01: Missing post-execute `response_code` check in eprom golden write tests (false-pass risk)

**Files:**
- `firestarter/test/native/avr/test_val_eprom/test_val_eprom.cpp:512-519` (`test_golden_eprom_0x07_write`)
- `firestarter/test/native/avr/test_val_eprom/test_val_eprom.cpp:527-542` (`test_golden_eprom_0x08_write`)
- `firestarter/test/native/avr/test_val_eprom/test_val_eprom.cpp:549-564` (`test_golden_eprom_0x0B_write`)
- `firestarter/test/native/avr/test_val_eprom/test_val_eprom.cpp:579-601` (`test_golden_eprom_chip_id`)
- `firestarter/test/native/avr/test_val_flash3/test_val_flash3.cpp:221-237` (`test_golden_flash3_write`)

**Issue:** All five of these golden-trace tests assert `response_code != ERROR`
after `configure_memory()` but not after the `operation_init` / `operation_main`
calls. If a mock misconfiguration (e.g. a missing `delayMicroseconds` stub,
wrong `vpp_mv`, or a future mock change) causes the operation to set
`RESPONSE_CODE_ERROR` and return early, the trace will be shorter than the
pinned fixture. `assert_trace_eq` will then trip on the count mismatch — but
the failure message will say "golden trace drift: eprom 0x07 write" with no
indication that the error was a mock failure, not a real algorithm regression.
Worse, if the operation errors out after recording exactly the pinned number
of entries (possible for a partial error path), the count assertion passes
and the element comparison becomes the sole guard.

By contrast, `test_golden_eeprom28c_write`, `test_golden_eeprom28c_chip_id`,
`test_golden_flash_intel_write`, and `test_golden_flash_intel_chip_id` all
correctly add a post-execute `response_code` assertion (e.g.
`test_val_eeprom28c.cpp:207-208`, `test_val_flash_intel.cpp:243-244`).

**Fix:** Add a `TEST_ASSERT_NOT_EQUAL_MESSAGE` for `response_code` after the
`operation_init` + `operation_main` block in each affected golden test, before
the `assert_trace_eq` call:
```cpp
if (h.firestarter_operation_init) h.firestarter_operation_init(&h);
if (h.firestarter_operation_main) h.firestarter_operation_main(&h);
TEST_ASSERT_NOT_EQUAL_MESSAGE(RESPONSE_CODE_ERROR, h.response_code,
    "golden 0x07 write: operation must not error");
#ifndef GOLDEN_BLESS
assert_trace_eq(golden_eprom_0x07_write, golden_eprom_0x07_write_n,
                "golden trace drift: eprom 0x07 write");
#endif
```
Apply the same pattern to the other four affected tests. The `GOLDEN_BLESS`
guard should wrap the response_code assertion too, since bless mode is not
testing correctness — but a post-execute check in both modes is harmless.

---

### WR-02: Unguarded null-pointer dereference for `firestarter_operation_main` in FIX-02B tests

**File:** `firestarter/test/native/avr/test_val_flash4/test_val_flash4.cpp:260` and `:278`

**Issue:** `test_flash4_write_execute_emits_sdp` and
`test_flash4_write_execute_no_vpp` call `h.firestarter_operation_main(&h)`
directly (no null guard) without first asserting that `configure_memory()`
succeeded. The pattern is:
```cpp
configure_memory(&h);
clear_bus_recording();
h.firestarter_operation_main(&h);   // line 260 / 278 — no null check, no pre-assert
```
If `configure_memory()` fails to wire `operation_main` (e.g. due to a future
dispatch refactor that silently leaves the pointer null for an unexpected
reason), the test process crashes with a segfault rather than producing a
clean Unity `FAIL`. This makes CI output unreadable and obscures the real cause.

Note: `test_inv04_flash4_256b_page_boundary` (line 361) makes the same
unguarded call but does have a `TEST_ASSERT_NOT_EQUAL` for `response_code`
immediately before the call, which is a partial mitigation (it won't prevent
a crash if `configure_memory` sets `RESPONSE_CODE_OK` but leaves the pointer
null — an unlikely but possible state). The golden trace tests in the same
file and in all other suites use the `if (h.firestarter_operation_main)`
guard pattern.

**Fix:** Add a null guard (consistent with all other operation_main call sites):
```cpp
configure_memory(&h);
TEST_ASSERT_NOT_EQUAL_MESSAGE(RESPONSE_CODE_ERROR, h.response_code,
    "test_flash4_write_execute_emits_sdp: configure_memory must not error");
clear_bus_recording();
TEST_ASSERT_NOT_NULL_MESSAGE(h.firestarter_operation_main,
    "test_flash4_write_execute_emits_sdp: operation_main must be wired");
h.firestarter_operation_main(&h);
```

---

### WR-03: `DOC_FILE_TO_FUNC` lookup raises `KeyError` (not assertion error) when an unknown handler appears

**File:** `firestarter_app/tests/test_dispatch_mirror.py:106`

**Issue:** In `test_dispatch_mirror_doc_matches_tool()`:
```python
expected_func = DOC_FILE_TO_FUNC[handler_file]   # line 106 — KeyError if unknown
```
If a future PROTOCOLS.md §0 table row introduces a new handler `.cpp` file
that is not yet in `DOC_FILE_TO_FUNC`, the test raises `KeyError` (a test
error) rather than failing with a meaningful assertion message. Test errors
are displayed differently in pytest output and CI summaries from test
failures; some CI configurations suppress error details. The dict contains
the current seven handlers and is not documented as requiring maintenance
when a new handler is added.

**Fix:** Replace the bare dict lookup with a `.get()` call that surfaces the
issue as an assertion failure:
```python
expected_func = DOC_FILE_TO_FUNC.get(handler_file)
assert expected_func is not None, (
    f"0x{hex_id:02X}: handler file '{handler_file}' appears in §0 table "
    "but is not in DOC_FILE_TO_FUNC — add it and its function name mapping"
)
got_func = check_dispatch.dispatch(hex_id, mem_type)
assert got_func == expected_func, ...
```

---

### WR-04: `GOLDEN_BLESS` `print_trace_inc()` does not guard against a full recording buffer before printing

**File:** `firestarter/test/native/avr/_shared/golden_trace.h:87-91`

**Issue:** `print_trace_inc()` prints whatever is in the recording buffer with
no check for truncation:
```cpp
static inline void print_trace_inc(void) {
    for (int i = 0; i < bus_recording_count(); i++) {
        printf("    { 0x%02X, 0x%02X },\n", recorded_reg(i), recorded_data(i));
    }
}
```
When `bus_recording_count() == 256` (the cap), the buffer is truncated.
`assert_trace_eq` in verify mode correctly catches this (the `< 256` guard
fires). However, if a developer runs bless mode to re-generate a fixture for
a test whose trace is at exactly 256 entries, `print_trace_inc()` prints the
truncated 256-entry data without any warning. If that output is redirected
to the fixture `.inc` file, the fixture is silently corrupted. The subsequent
verify run will immediately fail (guard fires), but the developer may not
realise the bless output itself was the problem — they may attempt to bless
again in a loop.

This is not a silent false-pass risk (verify mode will always fail), but it
is a workflow hazard that could waste time. The `flash4_write.inc` fixture at
206 entries is closest to the cap and provides limited headroom.

**Fix:** Add an anti-truncation stderr warning in bless mode:
```cpp
#ifdef GOLDEN_BLESS
static inline void print_trace_inc(void) {
    if (bus_recording_count() >= 256) {
        fprintf(stderr,
            "GOLDEN_BLESS WARNING: recording at cap (256 entries) — "
            "output is TRUNCATED; resize fixture input before blessing (D-04, Pitfall 2)\n");
    }
    for (int i = 0; i < bus_recording_count(); i++) {
        printf("    { 0x%02X, 0x%02X },\n", recorded_reg(i), recorded_data(i));
    }
}
#endif
```

---

## Info

### IN-01: Misleading `"6 entries"` claim in `golden_eeprom28c_write.inc` header comment

**File:** `firestarter/test/native/avr/test_val_eeprom28c/golden_eeprom28c_write.inc:4`
**Also:** `firestarter/test/native/avr/test_val_eeprom28c/test_val_eeprom28c.cpp:179`

**Issue:** The fixture header says `"SDP unlock (P7, flash_util_byte_flipping 6 entries)"`.
The actual fixture contains 13 entries before the data-write phase (1 CTL
write + 6 LSB/MSB pairs for the 3-command SDP sequence, repeated twice = 13
entries total). Counting the fixture confirms 17 entries total. The claim
of `"6 entries"` does not correspond to any accurate count. The `.cpp` at
line 179 repeats the claim: `"6-write sequence via flash_util_byte_flipping"`.

The fixture data itself is correct (it is the authoritative oracle); only the
comment is wrong. A developer re-blessing the fixture or tracing through a
failure would be misled about the expected structure.

**Fix:** Update the fixture comment and the `.cpp` comment to reflect the
actual entry counts (e.g., `"SDP unlock: 13 entries (1 CTL + 6×(LSB+MSB)
pairs across 3 SDP writes)"` or similar accurate description).

---

### IN-02: Firmware-leg check in `test_dispatch_mirror.py` is purely lexical (hex-literal anywhere in file)

**File:** `firestarter_app/tests/test_dispatch_mirror.py:138-157`

**Issue:** `test_dispatch_mirror_firmware_leg_enumerates_all_protocols()` checks
that every §0 protocol hex appears somewhere in `test_configure_memory.cpp`
by scanning for any `0x[hex]+` token in the entire file. A protocol hex
that appears only in a comment, a data constant, or an unrelated chip_id
constant (e.g., `0x1F00` or `0xBFB7` contain sub-byte values that could
hypothetically match small protocol IDs) would satisfy the check.

In practice, with the current 12 §0 protocols ranging from `0x05` to `0x34`,
none of the chip_id values in the file map to these protocol IDs, so there
is no actual false-pass today. The check is appropriately documented as
intentionally weak ("a missing protocol in the firmware test means a routing
arm lacks a native test"). This is worth noting for future maintenance when
new protocol IDs are added.

**Fix:** No immediate code change required. Document the intentional weakness
explicitly in the test (it is already partially documented). If a protocol ID
ever clashes with an incidental constant in the file, the assertion-message
text is clear enough to diagnose.

---

### IN-03: `_PROTOCOLS_MD` and `_FW_DISPATCH_TEST` path construction is silently no-op if sub-repos are not present

**File:** `firestarter_app/tests/test_dispatch_mirror.py:34-43`

**Issue:** Both cross-repo path constants are constructed at module import time
using `pathlib.Path(__file__).parent.parent / "firestarter" / ...`. If the
`firestarter/` sub-repo is not checked out (e.g. in a shallow CI clone of
`firestarter_app` only), `Path.read_text()` raises `FileNotFoundError` inside
the test function body, surfacing as a test error rather than a skip. This is
acceptable given that the test is specifically designed to guard cross-repo
drift and should fail (not skip) when the sibling sub-repo is absent.

The existing comment block at lines 1-17 documents the three-way bind intent.
No file-missing guard or `pytest.skip` is present or expected.

**Fix:** No code change required. Consider adding a module-level guard if CI
is ever run in a firestarter_app-only context:
```python
if not _PROTOCOLS_MD.exists():
    pytest.skip("firestarter sub-repo not present — cross-repo test skipped")
```
But only add this if a firestarter_app-only CI environment is ever introduced;
today both sub-repos are always co-present in `/workspaces/`.

---

_Reviewed: 2026-06-26T10:30:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
