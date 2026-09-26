---
phase: 55-relocate-buffer-size-advertisement-operation-ok-ack
reviewed: 2026-06-05T00:00:00Z
depth: standard
files_reviewed: 10
files_reviewed_list:
  - firestarter_app/firestarter/serial_comm.py
  - firestarter_app/firestarter/eprom_operations.py
  - firestarter/include/firestarter.h
  - firestarter/src/firestarter.cpp
  - firestarter/src/hardware_operations.cpp
  - firestarter/src/dev_tools.cpp
  - tools/catalog/messages.toml
  - firestarter/test/native/avr/test_messages/test_rurp_log_id.cpp
  - firestarter_app/tests/test_even_block.py
  - firestarter_app/tests/test_serial_comm.py
findings:
  critical: 0
  warning: 4
  info: 3
  total: 7
status: resolved
resolution: "WR-01..04 fixed in firestarter_app@41d80e0 (clamp coverage + stale Phase-54 contract docs). IN-01/02/03 left as documented follow-ups (info-level)."
---

# Phase 55: Code Review Report

**Reviewed:** 2026-06-05
**Depth:** standard
**Files Reviewed:** 10
**Status:** issues_found

## Summary

Phase 55 (CAP-01) relocates the EPROM buffer-size advertisement off the firmware
identity string and onto the `MSG_OK_READY` operation-setup ack as a 2-byte
big-endian u16 param. I traced the full path: firmware emit
(`LOG_OK_ID_U16(MSG_OK_READY, DATA_BUFFER_SIZE)` → `rurp_log_id_u16` MSB-first
packing) → host decode (`_decode_id_frame` override → `struct.unpack(">H")` →
`[1,4096]` clamp → `firmware_max_chunk`) → consumption
(`_calculate_buffer_size` safe-512 default).

The core mechanism is **correct**: big-endian byte order is consistent across
the wire, the codec validates CRC before the override trusts the body, the
`len(params_bytes) == 2` guard handles 0/1/>2-byte param regions gracefully, the
safe-512 default replaces `FirmwareOutdatedError` on every path (no remaining
raise), and the GATE-1.8d ring-fenced `_read_and_parse_lines` body is untouched
(SHA pin test stays green). The MAIN-path data requests use `MSG_OK_REQ_DATA`
(0x02), not `MSG_OK_READY` (0x01), so re-running the override on each setup ack
is idempotent and harmless. All 43 affected pytest cases pass locally.

No blockers found. The issues below are quality/robustness defects: a security
control (the plausibility clamp) ships with zero test coverage, and several test
docstrings now actively contradict the code they document (describing the
reverted Phase 54 contract — `FirmwareOutdatedError` on absent field — that this
phase deliberately removed).

## Narrative Findings (AI reviewer)

## Warnings

### WR-01: Plausibility clamp [1, 4096] has no test coverage

**File:** `firestarter_app/firestarter/serial_comm.py:269-275`
**Issue:** The clamp `if 1 <= value <= 4096:` is the load-bearing defensive
control the phase context calls out (T-55-05 / T-55-06): it is the only thing
preventing a hostile or corrupt `MSG_OK_READY` ack from over-sizing
`firmware_max_chunk` and therefore the write/verify chunk size. Yet the only
override tests in `tests/test_serial_comm.py`
(`test_decode_id_frame_sets_firmware_max_chunk_from_2_byte_param`,
`..._leaves_..._none_for_0_byte_param`) exercise only the happy path (512) and
the 0-byte path. There is no test pinning that `value == 0`, `value == 5000`, or
`value == 0xFFFF` leaves `firmware_max_chunk` unset so the 512 floor applies. A
future refactor could silently widen or drop the clamp and every test would
still pass. Security controls must be regression-pinned.
**Fix:** Add cases to `tests/test_serial_comm.py`:
```python
import pytest
@pytest.mark.parametrize("raw, expect", [
    (b"\x00\x00", None),    # 0 -> rejected
    (b"\x10\x01", 4097),    # 4097 -> rejected (None)
    (b"\xff\xff", None),    # 65535 -> rejected
    (b"\x10\x00", 4096),    # 4096 -> accepted (boundary)
    (b"\x00\x01", 1),       # 1 -> accepted (boundary)
])
def test_decode_id_frame_clamps_max_chunk(make_comm, raw, expect):
    comm = make_comm()
    from firestarter.frame_parser import _crc8_ccitt
    from firestarter.messages import MSG_OK_READY
    body = bytes([MSG_OK_READY]) + raw
    body += bytes([_crc8_ccitt(body)])
    comm._decode_id_frame(len(body), body)
    assert comm.firmware_max_chunk == (expect if expect not in (4097,) else None)
```
(adjust the rejected cases to assert `is None`).

### WR-02: test_even_block.py module docstring documents the reverted Phase 54 contract

**File:** `firestarter_app/tests/test_even_block.py:14-21`
**Issue:** The module docstring states: *"absent field raises
FirmwareOutdatedError (D-05 lockstep, no fallback)."* This is the exact behavior
Phase 55 CAP-01 **reverses**. The test bodies were correctly updated to assert
`== 512` (e.g. `test_calculate_buffer_size_raises_without_max_chunk` now asserts
512 despite its name), but the docstring was not. A reader trusting the
docstring will believe absent-field raises — the opposite of shipped behavior.
This is a correctness-of-documentation defect in a contract-pinning test file,
where the docstring is the stated source of truth for the contract.
**Fix:** Update lines 15-17 to:
```
2. firmware_max_chunk parse contract (CAP-01): _calculate_buffer_size() returns
   firmware_max_chunk directly (no -2 arithmetic); absent field returns 512
   (Uno-floor safe default — Phase 54 D-05 reversed, NO FirmwareOutdatedError).
```

### WR-03: TestFirmwareMaxChunkParse class docstring contradicts its own tests

**File:** `firestarter_app/tests/test_even_block.py:71-74`
**Issue:** The class docstring says *"raises FirmwareOutdatedError when the field
is absent (D-05 no fallback)"*, but the class's own
`test_calculate_buffer_size_raises_without_max_chunk` (lines 89-102) asserts the
result is 512 and explicitly comments *"CAP-01: absent firmware_max_chunk must
NOT raise FirmwareOutdatedError."* The docstring directly contradicts the test
it heads. Additionally the method name `test_calculate_buffer_size_raises_...`
is now a misnomer — it verifies the opposite (no raise).
**Fix:** Rewrite the class docstring to state the 512 safe-default contract and
rename the method to `test_calculate_buffer_size_returns_512_without_max_chunk`.

### WR-04: Misleading test method name `test_calculate_buffer_size_raises_without_max_chunk`

**File:** `firestarter_app/tests/test_even_block.py:89`
**Issue:** The method asserts `result == 512` and that NO exception is raised,
but the name says `..._raises_...`. A grep for "raises" in the suite to audit
exception behavior will surface this as a false positive; a maintainer skimming
test names will mis-read the contract. Tracks with WR-03 but is independently a
naming defect.
**Fix:** Rename to `test_calculate_buffer_size_returns_512_without_max_chunk`
(it duplicates `TestCapSafeDefault.test_absent_firmware_max_chunk_returns_512` —
consider deleting one as redundant).

## Info

### IN-01: firmware_max_chunk extraction recomputes params already parsed by the codec

**File:** `firestarter_app/firestarter/serial_comm.py:263-269`
**Issue:** `codec.decode_id_frame` already extracts `params_bytes = body[1:-1]`
and validates CRC. The override re-derives `msg_id = body[0]` and
`params_bytes = body[1:-1]` independently. The two derivations are byte-identical
today, but they are not coupled — if the codec's body framing ever changed (e.g.
a length-prefixed param region), this override would silently read the wrong
bytes. Low risk because both live in the same repo and codec is itself
ring-fenced, but the duplication is a latent coupling hazard.
**Fix:** Prefer threading the already-decoded `bytes` param value out of the
`LogMessage` returned by `codec.decode_id_frame` (MSG_OK_READY's catalog param
is `bytes`, so the decoded payload is available) rather than re-slicing `body`.
Non-blocking; document the coupling if left as-is.

### IN-02: Deprecated firmware_buffer_size attribute retained but dead

**File:** `firestarter_app/firestarter/serial_comm.py:115-119`
**Issue:** `self.firmware_buffer_size` is declared "DEPRECATED (Phase 55)" and
is never read anywhere in `firestarter/` production code (only set to None here
and in `conftest.py:146`, and name-referenced in a test docstring). It is dead
state kept only so `conftest`'s `make_comm` factory mirrors `__init__`. Carrying
a deprecated attribute indefinitely invites confusion with the live
`firmware_max_chunk`.
**Fix:** Remove `firmware_buffer_size` from `__init__` and from
`conftest.py:146` together in a follow-up cleanup; the comment already documents
the rationale for the eventual removal.

### IN-03: Three near-identical override tests across two files

**File:** `firestarter_app/tests/test_even_block.py:77-81,187-191`
**Issue:** `TestFirmwareMaxChunkParse.test_calculate_buffer_size_uses_max_chunk_512`,
`TestCapSafeDefault.test_512_ok_ready_ack_sets_firmware_max_chunk`, and
`test_max_chunk_replaces_fw_buf_minus_2` all build an `EpromOperator` with
`comm = SimpleNamespace(firmware_max_chunk=512)` and assert
`_calculate_buffer_size() == 512`. The 1024 case is likewise duplicated. This is
benign duplication but inflates the suite and increases maintenance churn when
the contract changes (as just demonstrated by the stale docstrings).
**Fix:** Consolidate into a single parametrized test
`(512->512, 1024->1024, None->512)`; the "not buf-2" assertion can be folded in
as an extra assert.

---

_Reviewed: 2026-06-05_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
