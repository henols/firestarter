---
phase: 51-command-channel-framing-migration-breaking-wire-change
plan: "01"
subsystem: firmware-command-channel
tags: [cobs, crc8, command-channel, framing, serial-transport, security]
dependency_graph:
  requires: [phase-50-data-path-framing]
  provides: [COBS-command-decode, CRC8-before-parse, CMD_FRAME_MAX]
  affects: [firestarter/src/firestarter.cpp, firestarter/include/firestarter.h]
tech_stack:
  added: []
  patterns: [COBS-decode-in-place, CRC8-gate-before-JSON-parse, drain-to-delimiter-recovery]
key_files:
  created:
    - firestarter/test/native/avr/test_cobs_cmd_frame/test_cobs_cmd_frame.cpp
    - firestarter/test/native/avr/test_cobs_cmd_frame/host_stubs.cpp
  modified:
    - firestarter/platformio.ini
    - firestarter/include/firestarter.h
    - firestarter/src/firestarter.cpp
decisions:
  - "Reused MSG_ERR_EMPTY_INPUT for n<=0 COBS decode error in CMD_IDLE — messages.h is codegen from messages.toml; adding MSG_ERR_BAD_FRAME requires a TOML catalog update deferred to a follow-on commit"
metrics:
  duration: "5m"
  completed: "2026-06-02"
  tasks_completed: 2
  files_changed: 5
---

# Phase 51 Plan 01: Command-Channel COBS Framing Migration + CRC8-Before-Parse Summary

COBS+CRC8 command-frame decode replaces the legacy `{`-peek loop on the firmware CMD_IDLE ingest path; CRC8 is verified before `parse_json()` is ever called; bounded recovery via internal drain-to-0x00.

## What Was Built

### Task 1: Wave-0 command-frame Unity scaffold + CMD_FRAME_MAX + platformio registration

- **`test_cobs_cmd_frame/test_cobs_cmd_frame.cpp`** — 4 Unity cases exercising `rurp_communication_read_data()` as the command-channel decode primitive:
  - `test_cobs_decode_valid_json_command`: valid JSON payload (`{"state":13}`) round-trips through COBS+CRC8 decode; returns payload length with correct bytes in `data_buffer`
  - `test_cobs_crc_reject_does_not_reach_parser` (V5 / §4.4 headline): deliberately-flipped CRC byte causes decoder to return < 0; proves CRC mismatch is caught before any parse path (T-51-01 mitigation assurance)
  - `test_cobs_resync_bounded`: garbled frame then valid frame — first call returns < 0, second call decodes correctly (D-06 bounded recovery)
  - `test_cobs_oversized_frame_bounded_recovery`: payload > DATA_BUFFER_SIZE triggers overflow drain (-2) + recovery of next valid frame — no hang (T-51-02 mitigation assurance)
- **`test_cobs_cmd_frame/host_stubs.cpp`** — verbatim copy of `test_cobs_data_frame/` analog; includes `_shared/host_stubs_common.inc`
- **`platformio.ini`** — added `native/avr/test_cobs_cmd_frame` to `test_filter` allowlist (line ~84) and `-I test/native/avr/test_cobs_cmd_frame` to `build_flags` (line ~93)
- **`firestarter.h`** — added `#define CMD_FRAME_MAX DATA_BUFFER_SIZE` after the `DATA_BUFFER_SIZE` block with full FRAME-05 / D-06 comment (firmware half of host/firmware parity pair)

### Task 2: Replace CMD_IDLE {-peek ingest with COBS frame decode + surgery on init_programmer

- **`firestarter.cpp` CMD_IDLE branch** — the legacy `rurp_communication_peak() == '{'` / `rurp_communication_read()` discard loop is deleted outright (D-05). Replaced with:
  ```cpp
  int n = rurp_communication_read_data(handle.data_buffer);
  if (n > 0) {
      handle.data_size = (uint32_t)n;
      handle.data_buffer[n] = '\0';
      if (init_programmer_framed(&handle)) { return; }
  } else {
      LOG_ERROR_ID(MSG_ERR_EMPTY_INPUT);
  }
  ```
  Gated strictly on `n > 0`; on `n <= 0` logs error and stays CMD_IDLE. Internal drain-to-delimiter on any decode failure is handled by the decoder itself (no additional drain in CMD_IDLE).
- **`init_programmer()` → `init_programmer_framed()`** — renamed and forward-declaration updated. The `rurp_communication_read_bytes()` blocking call is deleted (data is pre-filled by CMD_IDLE decode step). The `data_size == 0` empty-frame guard is retained. The `data_buffer[data_size] = '\0'` NUL-terminate is now a no-op (already done in CMD_IDLE) — removed to avoid redundancy.

## Verification Results

```
pio test -e native -f "native/avr/test_cobs_cmd_frame"
  4/4 PASSED (test_cobs_decode_valid_json_command, test_cobs_crc_reject_does_not_reach_parser,
              test_cobs_resync_bounded, test_cobs_oversized_frame_bounded_recovery)

pio test -e native (full regression)
  33/33 PASSED across 6 suites:
    test_dispatch, test_read_timing, test_cobs_cmd_frame, test_cobs_data_frame,
    test_data_input, test_messages
```

## Acceptance Criteria Confirmation

| Criterion | Status |
|-----------|--------|
| `test_cobs_cmd_frame/test_cobs_cmd_frame.cpp` exists and contains `test_cobs_crc_reject_does_not_reach_parser` | PASS |
| `test_cobs_cmd_frame/host_stubs.cpp` exists and contains `host_stubs_common.inc` | PASS |
| `grep -c "native/avr/test_cobs_cmd_frame" platformio.ini` returns 2 | PASS (2) |
| `grep "CMD_FRAME_MAX" firestarter/include/firestarter.h` | PASS |
| `grep -n "rurp_communication_peak"` returns nothing | PASS (empty) |
| `grep -n "rurp_communication_read_bytes"` returns nothing (code) | PASS (comment only) |
| `grep -n "== '{'"` returns nothing | PASS (empty) |
| CMD_IDLE branch contains `rurp_communication_read_data` gated by `if (n > 0)` | PASS |
| `init_programmer_framed` — forward declaration + definition + call site all present; no bare `init_programmer(` definition | PASS |
| `pio test -e native -f "native/avr/test_cobs_cmd_frame"` exits 0 | PASS |
| `pio test -e native` exits 0 (no regression) | PASS |

## Must-Haves Confirmation

| Truth | Status |
|-------|--------|
| Corrupted command frame (CRC8 mismatch) → `rurp_communication_read_data()` returns < 0 → `parse_json()` never invoked | PROVEN by `test_cobs_crc_reject_does_not_reach_parser` |
| Valid COBS+CRC8 command frame decodes into `handle.data_buffer` and reaches `parse_json()` with exact JSON payload | PROVEN by `test_cobs_decode_valid_json_command` + Task 2 wiring |
| Oversized command frame (delimiter never arrives) recovers bounded — drain-to-0x00 + negative return, no hang | PROVEN by `test_cobs_oversized_frame_bounded_recovery` |
| Legacy `{`-peek / discard-non-`{` command-ingest loop no longer exists in firestarter.cpp | CONFIRMED — grep returns empty |
| `init_programmer` no longer calls `rurp_communication_read_bytes` — it consumes data already in `handle.data_buffer` | CONFIRMED — call removed, renamed to `init_programmer_framed` |

## Security (Threat Model)

| Threat | Mitigation Status |
|--------|------------------|
| T-51-01: Tampering via CRC bypass | MITIGATED — `rurp_communication_read_data()` verifies CRC8 before returning; CMD_IDLE gates on `n > 0`; proven by Unity case |
| T-51-02: DoS via frame accumulation | MITIGATED — `DATA_BUFFER_SIZE`/`CMD_FRAME_MAX` overflow guard returns -2 + internal drain; proven by Unity case |
| T-51-03: Mode-transition window | MITIGATED — decoder consumes full frame including 0x00 before `init_programmer_framed()` is called |

## Deviations from Plan

### Auto-resolved Issues

**1. [Rule 2 - Missing functionality] MSG_ERR_EMPTY_INPUT reused for bad-frame error path**
- **Found during:** Task 2
- **Issue:** Plan preferred `MSG_ERR_BAD_FRAME` for the `n <= 0` branch. `messages.h` is generated by `tools/catalog/codegen.py` from `messages.toml` (per file header "DO NOT EDIT"). Adding a new message ID requires editing the TOML catalog and re-running codegen, which is out of scope for this plan.
- **Fix:** Reused `MSG_ERR_EMPTY_INPUT` (0xA4) per the plan's explicit fallback: "otherwise reuse MSG_ERR_EMPTY_INPUT and note the reuse in the SUMMARY."
- **Impact:** Minor — the error ID is advisory only (the decode failure already drains and recovers). A follow-on commit can add `MSG_ERR_BAD_FRAME` to the catalog.
- **Files modified:** None (no new ID added)
- **Commit:** N/A (design choice, not a code change)

## Requirements Closed

- **FRAME-05** (firmware half): host→fw command frames decode → CRC8-verify → parse; legacy `{`-peek deleted
- **CRC-01** (command channel): CRC8 verified before parse on every command frame

## Commits

| Task | Commit | Description |
|------|--------|-------------|
| Task 1 | d882865 | feat(51-01): add test_cobs_cmd_frame Unity suite + CMD_FRAME_MAX + pio registration |
| Task 2 | 0550431 | feat(51-01): replace CMD_IDLE {-peek ingest with COBS frame decode + CRC8-before-parse |

## Known Stubs

None — all test cases exercise real decode primitive and the production CMD_IDLE path is fully wired.

## Threat Flags

None — no new network endpoints, auth paths, file access patterns, or schema changes introduced beyond those already in the plan's threat model.

## Self-Check: PASSED

- firestarter/test/native/avr/test_cobs_cmd_frame/test_cobs_cmd_frame.cpp — FOUND
- firestarter/test/native/avr/test_cobs_cmd_frame/host_stubs.cpp — FOUND
- firestarter/include/firestarter.h CMD_FRAME_MAX — FOUND
- Commit d882865 — FOUND (git log)
- Commit 0550431 — FOUND (git log)
- pio test -e native: 33/33 PASSED
