---
phase: 06-logging-infrastructure
reviewed: 2026-05-18T12:34:46Z
depth: standard
files_reviewed: 30
files_reviewed_list:
  - .github/workflows/catalog-sync-check.yml
  - firestarter/.github/workflows/build.yml
  - firestarter/include/logging_id.h
  - firestarter/include/messages.h
  - firestarter/include/rurp_serial_utils.h
  - firestarter/include/rurp_shield.h
  - firestarter/platformio.ini
  - firestarter/src/boards/rurp_serial_utils.cpp
  - firestarter/src/boards/uno_rurp_shield.cpp
  - firestarter/src/messages.c
  - firestarter/test/native/avr/test_dispatch/host_stubs.cpp
  - firestarter/test/native/avr/test_eeprom28c_chip_id/host_stubs.cpp
  - firestarter/test/native/avr/test_flash_intel_vpp/host_stubs.cpp
  - firestarter/test/native/avr/test_messages/avr/pgmspace.h
  - firestarter/test/native/avr/test_messages/host_stubs.cpp
  - firestarter/test/native/avr/test_messages/test_rurp_log_id.cpp
  - firestarter/tools/catalog/codegen.py
  - firestarter/tools/catalog/messages.toml
  - firestarter_app/.github/workflows/ci.yml
  - firestarter_app/firestarter/firmware.py
  - firestarter_app/firestarter/messages.py
  - firestarter_app/firestarter/serial_comm.py
  - firestarter_app/pyproject.toml
  - firestarter_app/tests/__init__.py
  - firestarter_app/tests/conftest.py
  - firestarter_app/tests/test_decoder.py
  - firestarter_app/tests/test_fwguard.py
  - firestarter_app/tools/catalog/codegen.py
  - firestarter_app/tools/catalog/messages.toml
findings:
  critical: 0
  warning: 6
  info: 7
  total: 13
status: issues_found
---

# Phase 6: Code Review Report

**Reviewed:** 2026-05-18T12:34:46Z
**Depth:** standard
**Files Reviewed:** 30
**Status:** issues_found

## Summary

Phase 6 lands the ID-encoded logging frame surface end-to-end: catalog
(`messages.toml`) → codegen (`codegen.py`) → firmware emitter
(`rurp_serial_utils.cpp`) + macros (`logging_id.h`) → host decoder
(`serial_comm.py`) + tests + CI drift gates.

The core invariants check out:

- Wire frame bytes (`AA 55 AA 55 | len | id | params | crc8 | 0A`) emitted
  by `_firestarter_emit_frame` match the host decoder in
  `_read_and_parse_lines` / `_decode_id_frame` byte-for-byte.
- CRC8-CCITT polynomial 0x07, seed 0x00, no reflection, no final XOR is
  consistent across the firmware PROGMEM table, the host's
  `_build_crc8_table`, the firmware Unity test's `ref_crc8`, and the host
  conftest's `_ref_crc8_ccitt`. The first 16 bytes of the firmware
  PROGMEM table were re-derived from the reference algorithm and match.
- Catalog validates (`codegen.py --check` → 68 messages, version 1).
- Codegen drift gate is clean today: regenerating `include/messages.h`,
  `src/messages.c`, and `firestarter/messages.py` from the catalog
  produces zero diff against the committed artifacts.
- Catalog cross-sub-repo identity: meta-repo `.planning/catalog/messages.toml`,
  `firestarter/tools/catalog/messages.toml`, and
  `firestarter_app/tools/catalog/messages.toml` are byte-identical
  (and so are the three `codegen.py` copies).
- LMIG-01 coexistence: `rurp_log` / `rurp_log_P` prototypes remain in
  `rurp_shield.h`; weak defaults still live in `rurp_serial_utils.cpp`;
  `LOG_*_MSG` PROGMEM strings unchanged in `src/logging.c`; legacy
  `log_error_const` / `log_info_const` / `log_info_format` call-sites
  in `firestarter.cpp`, `operation_utils.cpp`, `eprom_operations.cpp`,
  `hardware_operations.cpp` were not touched.
- Host fw-guard: `except FirmwareOutdatedError: raise` (line 92) sits
  *before* `except (ProgrammerNotFoundError, SerialError)` (line 94) in
  `firmware.py:check_current_firmware`. Because `FirmwareOutdatedError`
  subclasses `SerialError`, the order matters and is correct.

The findings below are non-blocking. They cover real-but-narrow gaps in
CI coverage, hardening opportunities in the wire-frame emit / decode
paths, and a small amount of test-code maintenance.

## Warnings

### WR-01: CI `paths-ignore` excludes `.github/**` and `test/**` — drift-gate / native-test changes can land unverified

**File:** `firestarter/.github/workflows/build.yml:6-16`, `firestarter/.github/workflows/build.yml:20-30`
**Issue:** The firmware CI workflow ignores both `.github/**` and
`test/**` for push and pull_request triggers. The new drift-gate steps
(lines 64-82) and the new native Unity suite (`test/native/avr/test_messages/`)
live under those paths. A PR that only edits the workflow itself, or
only edits the native test suite, will NOT trigger CI to validate the
change. The drift gate is the entire point of LCI-01; landing a broken
gate (e.g., a typo in the codegen invocation) wouldn't be caught
because the gate doesn't run on the change that broke it.

Additionally, the firmware CI runs only `pio run` (build), never
`pio test`. The new `test_messages` Unity suite that pins the CRC8
polynomial and the exact frame byte sequence (`test_rurp_log_id.cpp`)
is therefore never executed in CI — only on developer machines.

**Fix:** Either narrow `paths-ignore` (drop `.github/**` and
`test/**`), or add an explicit `paths:` include for `.github/workflows/**`
and `test/native/avr/test_messages/**` on a dedicated job. Add a
`pio test -e native` step (or at minimum `pio test -e native -f "*test_messages*"`)
to the build matrix so the locked frame contract is regression-guarded
in CI. The host-side CI (`firestarter_app/.github/workflows/ci.yml`)
already runs `pytest tests/ -v` and does NOT ignore `.github/**` — use
that as the template.

### WR-02: `_firestarter_emit_frame` accepts arbitrary `param_count` with no overflow guard

**File:** `firestarter/src/boards/rurp_serial_utils.cpp:153-185`
**Issue:** The emitter computes `uint8_t len = (uint8_t)(1 + param_count + 1)`
without bounds-checking `param_count`. If a caller (current or future,
via `LOG_ID_BYTES`) passes `param_count >= 254`, the length byte wraps
silently and the host decoder will read a body shorter than what the
firmware actually writes — desync. The catalog enforces a 24-byte cap
(`PARAM_BUDGET_BYTES`), but `_firestarter_emit_frame` is the wire boundary
and shouldn't trust catalog discipline for safety. The macro
`LOG_ID_BYTES` at `logging_id.h:74-75` makes the caller-supplied
`count` reach this path with no compile-time check.

**Fix:** Add a defensive early-return:
```c
void _firestarter_emit_frame(uint8_t id, const uint8_t* params, uint8_t param_count) {
    // Wire-frame budget: 1 (id) + param_count + 1 (crc) must fit in a uint8_t len byte.
    if (param_count > 253) {
        return;  // refuse oversize frame; alternative: emit MSG_NONE
    }
    ...
}
```
Or, since `param_count` is already `uint8_t` so it cannot exceed 255 at
the type level, document the contract and assert in tests. The current
code is silent on what happens at the boundary.

### WR-03: Host decoder accepts id-frame payload for `wire_format="text"` catalog entries

**File:** `firestarter_app/firestarter/serial_comm.py:287-362`
**Issue:** `_decode_id_frame` looks up `entry = CATALOG.get(msg_id)` but
never checks `entry.wire_format`. Two catalog entries are flagged as
`wire_format="text"` (`MSG_OK_FW_VERSION` 0x03, `MSG_OK_FW_HANDSHAKE`
0x06) and are expected to arrive over the legacy text channel only
(LFW-05). If a buggy firmware (or a malicious peer) emits an id-frame
with `id=0x03` and `params=b""`, the decoder will gladly produce
`LogMessage(severity="OK", text="FW_VERSION", id=3)` and route it
through `_log_rurp_feedback`. The host's pre-v1.2 guard in
`_probe_port` runs against the `OK:` text path; this leak path
bypasses that guard.

**Fix:** Add a defensive check after the catalog lookup:
```python
entry = CATALOG.get(msg_id)
if entry is None or entry.wire_format != "id_frame":
    logger.warning(
        f"Rejected id-frame with non-id_frame catalog wire_format: "
        f"id=0x{msg_id:02x} ({entry.name if entry else '?'})"
    )
    return None
```

### WR-04: `_decode_param` ascii_str overruns `params_bytes` without explicit bounds check

**File:** `firestarter_app/firestarter/serial_comm.py:98-103`
**Issue:** For `ptype == "ascii_str"` the decoder reads `length = buf[cursor]`,
then `return buf[start:end].decode(...), end`. If `start + length > len(buf)`,
Python slicing silently returns a truncated string and the cursor
advances to a position past the end of the buffer. The subsequent
catalog params (if any) then try to decode from past-the-end. The outer
`try` at line 340-348 catches `IndexError` / `struct.error`, so the
frame is eventually rejected — but the rejection happens via the
*next* param's failed read, which is fragile. If `ascii_str` is the
*last* param in a catalog entry, the truncation is silent and a
mangled string is rendered.

The catalog's CRC check at line 311-317 should have caught a
truncated wire frame upstream, but a malformed length-prefix byte in a
correctly-CRC'd ascii_str payload (e.g., emitter bug, attacker on
the serial line) would slip through.

**Fix:** Bounds-check the ascii_str length prefix against the remaining
buffer before slicing:
```python
if ptype == "ascii_str":
    length = buf[cursor]
    start = cursor + 1
    end = start + length
    if end > len(buf):
        raise ValueError(
            f"ascii_str length {length} exceeds remaining buffer "
            f"({len(buf) - start} bytes available at cursor={cursor})"
        )
    return buf[start:end].decode("ascii", errors="replace"), end
```

### WR-05: `update_version.py` auto-commit in firmware CI runs *before* the codegen drift gate

**File:** `firestarter/.github/workflows/build.yml:53-82`
**Issue:** The steps are ordered: (1) run `update_version.py` to bump the
version string, (2) `git-auto-commit-action` commits the bump to the
branch, (3) set up Python and run the codegen drift gate. If codegen
output happens to drift on the branch (e.g., a developer edited
`messages.toml` without re-running codegen), the version-bump commit
has *already been pushed* by the time the drift gate fails. The
operator now has a published commit they may need to revert or
overwrite, and the CI failure is harder to interpret because it's
post-commit. On `main`, this is particularly bad: the auto-commit
lands directly on the protected branch before the gate has a chance to
veto it.

**Fix:** Move the drift gate (steps "Set up Python 3.11 for codegen",
"Catalog validity check", "Codegen drift gate") to BEFORE the
`stefanzweifel/git-auto-commit-action@v5` step. The drift gate is a
read-only check and can run on a fresh checkout without side effects.
If it fails, the version bump and the auto-commit don't happen.

### WR-06: Three `host_stubs.cpp` files duplicate ~120 lines of stub code each

**File:** `firestarter/test/native/avr/test_dispatch/host_stubs.cpp`,
`firestarter/test/native/avr/test_eeprom28c_chip_id/host_stubs.cpp`,
`firestarter/test/native/avr/test_flash_intel_vpp/host_stubs.cpp`,
`firestarter/test/native/avr/test_messages/host_stubs.cpp`
**Issue:** Each test suite carries its own near-duplicate copy of the
`rurp_*` no-op stubs, `LOG_*_MSG` PROGMEM strings, and the
`Serial_::operator bool()` definition. `test_dispatch` and
`test_eeprom28c_chip_id` differ by only 23 lines (header comment
delta); `test_flash_intel_vpp` adds 48 lines of mock-injection state
on top. When a new `rurp_*` symbol is added, four files must be edited
in lockstep — and the reviewer cannot tell at a glance which file is
the canonical source.

There's a concrete bug risk: if a future `rurp_*` symbol is added but
only three of the four `host_stubs.cpp` files get updated, the fourth
test suite fails to link with a confusing "undefined reference"
error rather than a clear signal pointing at the missed stub.

**Fix:** Hoist the common stubs into a shared TU
(`test/native/avr/_common/host_stubs.cpp`) and let each suite's
`host_stubs.cpp` shrink to just its suite-specific extensions (e.g.,
the `s_mock_vpp_mv` state in `test_flash_intel_vpp`). Update
`platformio.ini`'s `[env:native]` `src_filter` to include the shared
TU. PlatformIO's automatic discovery of files under `test/` will
co-link the shared TU with each suite's binary. (Phase-6 scope didn't
formally require dedup, but the duplication is a maintenance debt
that will get worse with each future native suite.)

## Info

### IN-01: `LOG_ID_*` macros use bare identifiers `_b`, `_v` that can shadow caller variables

**File:** `firestarter/include/logging_id.h:31-71`
**Issue:** The do-while block in `LOG_ID_U16`, `LOG_ID_U24`, `LOG_ID_U32`
introduces local `uint16_t _v` / `uint32_t _v` / `uint8_t _b[N]`. If a
caller writes `LOG_ID_U16(MSG_FOO, _v)`, the macro expands to
`uint16_t _v = (uint16_t)(_v);` — self-initialization with the inner
`_v` (undefined). Single-underscore lower-case names are not strictly
reserved at function scope, but the collision is silent on the few
compilers that don't warn. The leading-underscore convention is
unusual at call-site temporaries.
**Fix:** Rename to e.g. `_log_id_v`, `_log_id_buf` to make collision
vanishingly unlikely:
```c
#define LOG_ID_U16(id, p1) \
    do { \
        uint16_t _log_id_v = (uint16_t)(p1); \
        uint8_t _log_id_b[2] = { ... }; \
        rurp_log_id((id), _log_id_b, 2); \
    } while (0)
```

### IN-02: `MSG_NONE` (id=0x00) is reachable via id-frame decode but renders "(reserved sentinel)"

**File:** `firestarter/tools/catalog/messages.toml:21-27`, `firestarter_app/firestarter/messages.py:126`
**Issue:** A frame with `id=0x00` and matching CRC will pass
`CATALOG.get(0)` and render the string `"(reserved sentinel)"` into a
visible log line. This is documented behaviour (the catalog comment
calls it a "reserved sentinel") but the rendering is operator-facing.
Consider whether MSG_NONE should be treated specially by the decoder
(silently dropped, or surfaced with a more diagnostic label).
**Fix:** Either drop MSG_NONE from `CATALOG` (it then takes the unknown-id
warning path), or render it as e.g. `"<sentinel>"` so an operator
reading the log understands the frame was a no-op.

### IN-03: Two messages have `text` wire_format and 0 params but format strings contain printf specifiers

**File:** `firestarter/tools/catalog/messages.toml:51-57`, `firestarter/tools/catalog/messages.toml:84-90`
**Issue:** `MSG_OK_FW_VERSION` (id=0x03) carries `format = "FW_VERSION"`
with `params = []` and `wire_format = "text"`. `MSG_OK_FW_HANDSHAKE`
(id=0x06) carries `format = "FW: %s, HW: Rev%d, Cmd: 0x%02x"` with
`params = []` and `wire_format = "text"`. Rule 9 in codegen
(`format-vs-param-count mismatch`) is skipped for `wire_format=text`
entries (line 275: `if wf == "id_frame":`). So `MSG_OK_FW_HANDSHAKE`'s
format string declares 3 specifiers but has 0 params — fine for the
text path (the firmware emits the string itself) but unobvious.
**Fix:** Either add a comment in the catalog clarifying that text-format
`format` is the *firmware-side template* (not a host-render template),
or store the literal emitted string as `format = "FW: <fw>, HW: Rev<hw>, Cmd: 0x<cmd>"`
to make the difference between text-format and id_frame templates
explicit.

### IN-04: Test_decoder.py uses `next(gen)` without `pytest.raises(StopIteration)` guard

**File:** `firestarter_app/tests/test_decoder.py:184-185`, `firestarter_app/tests/test_decoder.py:50`
**Issue:** `_drive_one_response` swallows `StopIteration` and returns
None. The test `test_text_then_binary_in_one_read` calls `next(gen)`
twice raw at lines 184-185. If the generator yields one value and
then exhausts (regression in the read loop), pytest reports
`StopIteration` as an error, not as a clean assertion failure pointing
at the missing second response.
**Fix:** Use the existing helper or a try/except wrapper that converts
StopIteration to a clear assertion:
```python
gen = comm._read_and_parse_lines(timeout=1.0)
results = list(itertools.islice(gen, 2))
assert len(results) == 2, f"expected 2 responses, got {len(results)}: {results}"
first, second = results
```

### IN-05: `.editorconfig/**` in firmware CI `paths-ignore` is a typo for `.editorconfig`

**File:** `firestarter/.github/workflows/build.yml:16`, `firestarter/.github/workflows/build.yml:30`
**Issue:** `.editorconfig` is a file, not a directory. The pattern
`.editorconfig/**` only matches paths beneath a non-existent directory
named `.editorconfig`. The intended exclusion (skip CI when only
`.editorconfig` changed) is silently broken. Pre-existing; not new in
phase 6, but flagged because the surrounding lines were edited.
**Fix:** `- '.editorconfig'` (no trailing `/**`). Matches the existing
correct form in `firestarter_app/.github/workflows/ci.yml:11`.

### IN-06: `consume_remaining_input` swallows generator exceptions silently

**File:** `firestarter_app/firestarter/serial_comm.py:524-537`
**Issue:** The `for _ in self._read_and_parse_lines(timeout): pass` loop
discards every yielded response. If a malformed frame causes a
`SerialError` from inside the generator (lines 396-398, 426-430,
441-445, 455-460), the exception propagates out of `consume_remaining_input`
and into the `disconnect()` finally. `disconnect()` doesn't wrap the
call, so the connection is left half-closed. Pre-existing routing,
but the new id-frame path adds three new `read(1)` / `read(n)` sites
that can each raise.
**Fix:** Wrap the loop in a try/except SerialError that logs and
continues — `consume_remaining_input` is best-effort cleanup and
shouldn't escalate transient stream errors during disconnect.

### IN-07: Reserved identifier `__MESSAGES_H__` violates C standard (double-underscore prefix)

**File:** `firestarter/include/messages.h:17-18`, `firestarter/include/logging_id.h:18-19`
**Issue:** ISO C reserves identifiers beginning with two underscores
(and `_<uppercase>`) for the implementation. Header guards like
`__MESSAGES_H__` and `__LOGGING_ID_H__` formally invoke undefined
behaviour, even though every real-world compiler tolerates them. The
firmware code base uses this convention throughout (`__RURP_SHIELD_H__`
etc.) so this is pre-existing and consistent, not phase-6-introduced.
The codegen template hardcodes `__MESSAGES_H__` — if the convention is
ever cleaned up, codegen must be updated in lockstep.
**Fix:** Lower priority. If addressed, change codegen.py:350-351 to
emit `FIRESTARTER_MESSAGES_H` style guards and update the matching
manual headers across the firmware tree in one sweep.

---

_Reviewed: 2026-05-18T12:34:46Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
