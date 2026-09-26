---
phase: 51-command-channel-framing-migration-breaking-wire-change
reviewed: 2026-06-02T12:00:00Z
depth: standard
files_reviewed: 2
files_reviewed_list:
  - firestarter/src/boards/rurp_serial_utils.cpp
  - firestarter/src/firestarter.cpp
findings:
  critical: 0
  warning: 1
  info: 2
  total: 3
status: issues_found
---

# Phase 51: Re-Review Report (Gap-Closure Verification)

**Reviewed:** 2026-06-02
**Depth:** standard
**Files Reviewed:** 2 (gap-closure scope: rurp_serial_utils.cpp + firestarter.cpp)
**Status:** issues_found

## Summary

This is a targeted re-review of the two gap-closure commits (6c3c392 + c523f49) that addressed the two BLOCKER defects found in the prior review:

- **CR-01** (OOB write: `handle.data_buffer[n] = '\0'` with n == DATA_BUFFER_SIZE): **GENUINELY CLOSED**. The PUSH macro cap at `out >= DATA_BUFFER_SIZE - 1` (= 511) ensures the decoder never returns n > 511. The belt-and-suspenders guard in `firestarter.cpp:179` (`if (n < DATA_BUFFER_SIZE)`) is always true for valid n but correctly documents the invariant and protects against future callers.
- **CR-02** (unbounded busy-wait spin): **GENUINELY CLOSED**. Both spin sites (`rurp_serial_utils.cpp:111-117` in `_drain_to_delimiter` and `rurp_serial_utils.cpp:164-172` in `rurp_communication_read_data`) are bounded by `TIMEOUT_MS = 1000 ms` per inter-byte wait. The truly-idle path is unaffected: the decoder is only entered when `loop()` already has `rurp_communication_available() > 0`.

One new WARNING is introduced by the CR-02 fix design: the per-byte timeout bound means total drain time is O(N × TIMEOUT_MS) for N bytes slowly arriving, not a single TIMEOUT_MS cap. Two pre-existing issues (millis-overflow in `op_reset_timeout`, dead-code guard in `_firestarter_emit_frame`) are documented as INFO for completeness.

All COBS decoder edge cases were traced exhaustively: zero-CRC, 254-run boundary, empty payload, all-zeros payload, single-byte frames, and mid-run violation. All cases are correct. No new memory-safety issues or AVR heap allocations were introduced.

## Narrative Findings (AI reviewer)

## Warnings

### WR-01: Drain total hang time is O(N × TIMEOUT_MS), not O(TIMEOUT_MS)

**File:** `firestarter/src/boards/rurp_serial_utils.cpp:92-123` (`_drain_to_delimiter`) and `rurp_serial_utils.cpp:164-172` (main decode timeout path)
**Issue:** The CR-02 fix bounds each individual inter-byte wait to `TIMEOUT_MS` (1 s), but `_drain_to_delimiter` rearms the 1 s timer from scratch for every new byte that arrives. A host that sends one non-zero byte every 999 ms keeps the drain loop running indefinitely — effectively re-establishing an unbounded hang through repeated per-byte deferrals. In the worst case (512-byte max frame, each byte arriving at 999 ms intervals) the drain blocks for approximately 512 seconds before completing. Additionally, when `rurp_communication_read_data` fires its own mid-frame timeout and then calls `_drain_to_delimiter`, the total blocked time is `TIMEOUT_MS` (main decoder) + up to N × `TIMEOUT_MS` (drain). For a truly silent host (no bytes at all) the combined worst case is 2 s (1 s + 1 s), which is acceptable; the dangerous scenario requires an active but slow sender.

This is a remaining weakness in the CR-02 design rather than a regression (the prior code hung forever). The plan documentation acknowledges this is a per-byte timer. It is a WARNING because a crashed host application that trickles bytes slowly — plausible with a USB-CDC driver in a bad state — would block the programmer for minutes with no way to recover short of a physical reset.

**Fix:** Add a total-frame-drain deadline alongside the per-byte deadline. Example:
```cpp
static void _drain_to_delimiter(void) {
    unsigned long frame_start = millis();  // total deadline for entire drain
    while (1) {
        if (rurp_communication_available() <= 0) {
            unsigned long byte_start = millis();
            while (rurp_communication_available() <= 0) {
                if (millis() - byte_start >= TIMEOUT_MS ||
                    millis() - frame_start >= DRAIN_TOTAL_MS) {
                    return;
                }
            }
        }
        if (millis() - frame_start >= DRAIN_TOTAL_MS) {
            return;
        }
        int d = rurp_communication_read();
        if (d < 0 || (uint8_t)d == 0x00) {
            break;
        }
    }
}
```
Where `DRAIN_TOTAL_MS` is a constant (e.g., 3000 ms — large enough to allow a 512-byte frame at 250000 baud to drain completely, but tight enough to prevent indefinite blocking). Alternatively, an iteration counter (max N iterations = DATA_BUFFER_SIZE + headroom) caps the loop without a second timer.

## Info

### IN-01: `op_reset_timeout` uses unsafe millis() + TIMEOUT_MS pattern (pre-existing)

**File:** `firestarter/src/firestarter.cpp:254`
**Issue:** `timeout = millis() + TIMEOUT_MS` overflows when `millis()` is within `TIMEOUT_MS` ms of the 32-bit rollover (~49.7 days uptime). The result wraps to a small value; the next `loop()` iteration evaluates `timeout < millis()` as true and fires `command_done()` immediately, aborting any in-progress operation. The COBS timeout code in `rurp_serial_utils.cpp` correctly uses the safe `millis() - start >= TIMEOUT_MS` pattern; `op_reset_timeout` does not. Pre-existing defect; not introduced by the CR-01/CR-02 gap-closure.

**Fix:**
```cpp
void op_reset_timeout() {
    // Safe: use start + delta comparison, not absolute deadline addition
    timeout_start = millis();  // store start; check as (millis() - timeout_start >= TIMEOUT_MS)
}
// ... in loop():
// if (handle.cmd != CMD_IDLE && millis() - timeout_start >= TIMEOUT_MS) { ... }
```

### IN-02: Dead-code overflow guard in `_firestarter_emit_frame` (pre-existing)

**File:** `firestarter/src/boards/rurp_serial_utils.cpp:377`
**Issue:** `_firestarter_emit_frame` takes `param_count` as `uint8_t` but guards with `if (param_count > 65533)`. A `uint8_t` can never exceed 255, so this condition is always false and the guard is dead code. The check was evidently copied from `_firestarter_emit_frame_wide` (which uses `uint16_t param_count` where the guard is also unreachable, since uint16_t max is 65535 and the check threshold is 65533 — only the values 65534 and 65535 would trigger it, and `len_u16 = 1 + 65534 + 1 = 65536` wraps to 0 causing the same bug the guard tries to prevent, so the wide variant's guard is similarly near-dead). Pre-existing; not introduced by the gap-closure.

**Fix:** For `_firestarter_emit_frame` (uint8_t), remove the dead guard entirely — `len_u16` can never overflow with uint8_t input. For `_firestarter_emit_frame_wide` (uint16_t), lower the threshold to `65533` is correct for intent but `len_u16` wraps at 65536; the guard as written permits 65534 and 65535 which still cause the wrap — tighten to `param_count > 65533` is correct (65534 → len = 65536 → wraps → already excluded). Clarify with a comment that the uint8_t overload needs no guard.

---

_Reviewed: 2026-06-02_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard (gap-closure focused)_
