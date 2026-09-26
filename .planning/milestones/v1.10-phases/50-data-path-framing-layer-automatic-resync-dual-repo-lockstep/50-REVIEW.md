---
phase: 50-data-path-framing-layer-automatic-resync-dual-repo-lockstep
reviewed: 2026-06-01T00:00:00Z
depth: standard
files_reviewed: 8
files_reviewed_list:
  - firestarter/src/boards/rurp_serial_utils.cpp
  - firestarter/src/operation_utils.cpp
  - firestarter_app/firestarter/frame_parser.py
  - firestarter_app/firestarter/eprom_operations.py
  - firestarter/test/native/avr/test_cobs_data_frame/test_cobs_data_frame.cpp
  - firestarter/test/native/avr/test_messages/serial_read_mock.h
  - firestarter_app/tests/test_cobs.py
  - firestarter/scripts/check_uno_ram.sh
findings:
  critical: 1
  warning: 3
  info: 2
  total: 6
status: resolved
resolution: "5/6 findings fixed post-review (CR-01, IN-01, IN-02, WR-02, WR-03); WR-01 deferred to verification as a design decision. Both full suites green after fixes."
---

# Phase 50: Code Review Report

**Reviewed:** 2026-06-01T00:00:00Z
**Depth:** standard
**Files Reviewed:** 8
**Status:** issues_found

## Summary

Reviewed the dual-repo COBS serial-framing change: the AVR firmware streaming
COBS decoder/encoder in `rurp_serial_utils.cpp`, the Python host encoder/decoder
in `frame_parser.py`, the frame assembly in `eprom_operations.py`, the Unity test
suite in `test_cobs_data_frame.cpp`, and supporting files.

The firmware decoder (lookahead design) and the firmware encoder (CRC-special-case
design) are internally correct across an exhaustive 10,000-trial simulation. The
`_drain_to_delimiter` resync logic is structurally correct but lacks a timeout.

One critical correctness bug was found: the Python `cobs_encode` function contains
a branch-ordering defect that silently drops zero bytes at 254-run boundaries. This
causes data corruption on roughly 0.1% of real write/verify frames and is
undetected by any existing test.

---

## Critical Issues

### CR-01: `cobs_encode` drops zero bytes at 254-run boundaries — silent data corruption

**File:** `firestarter_app/firestarter/frame_parser.py:81-99`

**Issue:** The `cobs_encode` outer loop's post-run branch order is wrong. When the
inner `while` exits because `(i - run_start) == 254` (the 254-byte run limit) and
the byte now at position `i` happens to be `0x00`, the condition:

```python
if i < n and payload[i] == 0x00:
    i += 1          # ← fires and CONSUMES the zero
elif run_len == 254:
    pass            # ← never reached
```

fires before the `elif run_len == 254: pass` branch. The result is that the zero
byte is consumed (i is incremented) but **never encoded**: the `0xFF` run code
(254-run) suppresses the implicit-zero slot that would have carried it, and the
zero disappears from the encoded stream.

This is confirmed by exhaustive simulation: feeding `cobs_encode(payload + bytes([crc]))` to
the firmware decoder fails on ~0.1% of random 512-byte payloads. The failure mode
is one missing zero byte in the decoded payload, yielding a CRC mismatch that the
firmware returns as error code -4 to the host. Because the host retries on `OP_MSG_ERROR`
(not implemented — the caller in `eprom_operations._main_phase_send_data` raises
`EpromOperationError`), the write operation aborts with a false failure. Subsequent
reads of the written EPROM will be wrong in one byte — silent data corruption if no
read-back verify is done.

The smallest reproducer is:
```python
payload = bytes([0x01] * 254 + [0x00] + [0x02])   # zero at position 254
crc = _crc8_ccitt(payload)
body = cobs_encode(payload + bytes([crc]))
# body is missing the 0x00 at logical position 254
```

The same bug manifests for `crc == 0` when the last run in the payload is exactly
254 nonzero bytes: the CRC zero is consumed and becomes the trailing-implicit-zero
that the firmware decoder discards, causing the last payload byte to be misidentified
as the CRC.

**Fix:** Swap the `if`/`elif` branches so the 254-run case takes priority:

```python
        if run_len == 254:
            # 254-run: no implicit zero — loop continues without consuming a zero
            pass
        elif i < n and payload[i] == 0x00:
            # Consumed the zero; move past it
            i += 1
        else:
            # End of payload reached; we're done
            break
```

This matches the intent expressed in the comment ("254-run: no implicit zero — loop
continues without consuming a zero") and is consistent with the firmware encoder's
handling of the same boundary.

---

## Warnings

### WR-01: `_drain_to_delimiter` has no timeout — firmware hangs on truncated frame

**File:** `firestarter/src/boards/rurp_serial_utils.cpp:88-98`

**Issue:** The inner spin `while (rurp_communication_available() <= 0) {}` has no
timeout. If the host crashes, disconnects, or sends `'#'` without completing the
COBS frame, the firmware will spin here indefinitely. There is no watchdog reset
in this path and no `op_reset_timeout()` call that would interact with the global
timeout machinery.

The same unbounded spin appears in the decoder's main loop (line 125) and in the
`b < 0` underrun path (line 129 calls `_drain_to_delimiter`). The result is a
permanently hung firmware that requires a board reset.

**Fix:** Add a byte-level timeout. A simple approach:

```cpp
static void _drain_to_delimiter(void) {
    unsigned long deadline = millis() + 3000UL;   /* 3 s generous bound */
    while (1) {
        while (rurp_communication_available() <= 0) {
            if ((long)(millis() - deadline) >= 0) return;   /* give up */
        }
        int d = rurp_communication_read();
        if (d < 0 || (uint8_t)d == 0x00) break;
    }
}
```

Apply the same pattern to the main decoder spin at line 125. Callers already treat
any negative return as `OP_MSG_ERROR` which propagates an error to the host; a
timeout return of -5 (new code) fits cleanly into this contract.

---

### WR-02: Dead pre-flight check in `op_get_message` `'#'` case

**File:** `firestarter/src/operation_utils.cpp:171-173`

**Issue:** The check `if (rurp_communication_available() <= 0) return OP_MSG_INCOMPLETE;`
inside the `case '#':` block (lines 163–165) can never be true. Execution reaches
this point only after `rurp_communication_peak()` returned `'#'`, which means
`available() >= 1`. The guard is dead code.

More importantly, the intent (per the comment: "Only gate on 1+ bytes available")
is already satisfied by the outer `while (rurp_communication_available() > 0)` loop
at line 132. The inner check adds confusion without protection: after consuming `'#'`
on line 166 the decoder immediately enters an unbounded blocking loop regardless.

**Fix:** Remove the inner dead check entirely:

```cpp
case '#': {
    rurp_communication_read();  // consume '#'
    int res = rurp_communication_read_data(handle->data_buffer);
    if (res < 0) {
        LOG_ERROR_ID_U16(MSG_ERR_DATA_ERR_N, (uint16_t)res);
        return OP_MSG_ERROR;
    }
    handle->data_size = res;
    return OP_MSG_DATA;
}
```

---

### WR-03: Dead `else if (run_len == 254)` branch in firmware COBS encoder

**File:** `firestarter/src/boards/rurp_serial_utils.cpp:257-262`

**Issue:** In `rurp_communication_write`, the post-loop CRC-handling block has three
cases: `if (crc == 0x00)`, `else if (run_len == 254)`, and `else`. The middle branch
is unreachable: `run_len` can only be `0..253` when the main loop exits, because any
time `run_len` reaches 254 inside the loop the 254-run block immediately resets it to
0. A static analyser or careful reader will correctly flag this as dead code, creating
maintainability risk: a future author might believe the `run_len == 254` post-loop
case is exercised and tested when it is not.

If the branch were somehow reached (say, a future refactor changes the loop
invariant), it would emit `0xFF` + 254 bytes from `buffer + run_start` which would
write out-of-bounds if `run_start + 254 > size` — but as established, this is
unreachable with the current code.

**Fix:** Remove the dead branch and add a comment documenting the invariant:

```cpp
    /* Post-loop invariant: run_len is 0..253 (never 254; the loop resets it
     * when the 254-run boundary fires).  Only two cases remain. */
    if (crc == 0x00) {
        SERIAL_PORT.write((uint8_t)(run_len + 1));
        if (run_len > 0) {
            SERIAL_PORT.write((const uint8_t*)buffer + run_start, run_len);
        }
        SERIAL_PORT.write((uint8_t)0x01);
    } else {
        SERIAL_PORT.write((uint8_t)(run_len + 2));
        if (run_len > 0) {
            SERIAL_PORT.write((const uint8_t*)buffer + run_start, run_len);
        }
        SERIAL_PORT.write(crc);
    }
```

---

## Info

### IN-01: `test_cobs.py` has no test that exercises the 254-run boundary with a zero byte immediately after it

**File:** `firestarter_app/tests/test_cobs.py:112-121`

**Issue:** `test_mixed_300_bytes` uses `bytes(i % 17 for i in range(300))` which
produces a maximum nonzero run of 16 bytes — far below the 254-boundary. The
`test_512_random_roundtrip` test uses pseudo-random seeds that happen not to place
a zero byte at the 254th position in any nonzero run, so the critical branch in
`cobs_encode` is never triggered.

No test checks the exact failure case identified in CR-01:
`payload = bytes([nonzero]*254 + [0x00] + ...)`.

**Fix:** Add a dedicated test:

```python
def test_254_run_boundary_followed_by_zero(self) -> None:
    """254 consecutive nonzero bytes immediately followed by 0x00 round-trips."""
    payload = bytes([0x01] * 254 + [0x00] + [0x02, 0x03])
    assert cobs_decode(cobs_encode(payload)) == payload

def test_254_run_boundary_followed_by_zero_in_frame(self) -> None:
    """Host-encoded frame with 254-run+zero round-trips through firmware decoder."""
    payload = bytes([0x01] * 254 + [0x00] + [0x02, 0x03])
    crc = _crc8_ccitt(payload)
    body = cobs_encode(payload + bytes([crc]))
    # Verify no zero in body, then verify CRC survives decoding
    assert b"\x00" not in body
    decoded_logical = cobs_decode(body)
    assert decoded_logical[:-1] == payload
    assert decoded_logical[-1] == crc
```

---

### IN-02: Firmware Unity test suite has no 254-run + zero-byte test case

**File:** `firestarter/test/native/avr/test_cobs_data_frame/test_cobs_data_frame.cpp`

**Issue:** The three test cases cover: a 3-byte all-nonzero payload (FRAME-01), a
4-byte all-nonzero bad-CRC garbled frame (FRAME-02), and a 512-byte all-zero payload
(FRAME-04). None of these exercises the 254-run boundary. The all-zero test is
valuable, but a payload of 254 nonzero bytes followed immediately by a zero byte
(which triggers the COBS implicit-zero logic in the decoder's `was_254_run` path)
is not tested.

**Fix:** Add a test case:

```cpp
void test_cobs_254_run_then_zero(void) {
    /* 254 nonzero bytes + one zero byte + a few more bytes. */
    uint8_t payload[258];
    memset(payload, 0x01, 254);
    payload[254] = 0x00;
    payload[255] = 0x02;
    payload[256] = 0x03;
    payload[257] = 0x04;

    build_cobs_frame_bytes(payload, sizeof(payload), rx_queue);
    setup_serial_read_mock(rx_queue, rx_pos);

    int res = rurp_communication_read_data(data_buffer);
    TEST_ASSERT_GREATER_OR_EQUAL_INT(0, res);
    TEST_ASSERT_EQUAL_size_t(sizeof(payload), (size_t)res);
    TEST_ASSERT_EQUAL_MEMORY(payload, data_buffer, sizeof(payload));
}
```

---

_Reviewed: 2026-06-01T00:00:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_

---

## Resolution (post-review fixes, 2026-06-01)

Applied before phase verification, as the byte-exactness of the transport is the milestone goal.

| Finding | Disposition | Detail |
|---------|-------------|--------|
| CR-01 (BLOCKER) | **Fixed** | `cobs_encode` branch order swapped (254-run check first) — zero at a 254-run boundary is no longer dropped. `firestarter_app` `df9cd2c`. |
| IN-01 | **Fixed** | Added `test_254_run_boundary_followed_by_zero` (+ in-frame variant) to `test_cobs.py` — the exact CR-01 trigger; RED before, GREEN after. `df9cd2c`/`44fe538`. |
| IN-02 | **Fixed** | Added `test_cobs_254_run_then_zero` to the firmware Unity suite. It **passed immediately** — the firmware decoder's `was_254_run`/implicit-zero deferral already handles the boundary correctly (no decoder bug; only the host encoder was wrong). `firestarter` `976dea9`. |
| WR-02 | **Fixed** | Removed the unreachable `available()<=0` guard in `op_get_message` `case '#'`. `976dea9`. |
| WR-03 | **Fixed** | Removed the unreachable `else if (run_len == 254)` dead branch in the firmware encoder post-loop; invariant documented. `976dea9`. |
| WR-01 | **Deferred** | Unbounded byte-wait spin (`while (available() <= 0) {}`) in the decoder/`_drain_to_delimiter`. Intersects the plan's deliberate removal of the 2 s `timeout_ms` loop (D-01/D-03), whose stated mitigation is "incomplete frame → op-level timeout machinery." Whether a frame-level deadline (not a per-byte loop) should be reintroduced is a design call for verification/operator, not an auto-fix. |

Post-fix suites: host **410 passed** (coverage floor held, ruff+mypy clean); firmware **29/29** (incl. new 254-run test); Uno RAM **545 B free** (gate exits 0).
