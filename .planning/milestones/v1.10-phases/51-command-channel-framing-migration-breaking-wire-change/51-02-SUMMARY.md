---
phase: 51-command-channel-framing-migration-breaking-wire-change
plan: "02"
subsystem: host-command-channel
tags: [cobs, crc8, command-channel, framing, serial-transport, atomic-write, security]
dependency_graph:
  requires: [phase-51-plan-01-firmware-cobs-command-decode]
  provides: [COBS-command-emit, CRC8-before-send, CMD_FRAME_MAX-host, atomic-frame-write]
  affects: [firestarter_app/firestarter/serial_comm.py, firestarter_app/firestarter/constants.py, firestarter_app/tests/test_serial_comm.py]
tech_stack:
  added: []
  patterns: [COBS-encode-then-append-delimiter, CRC8-over-raw-payload-before-encode, atomic-single-write-frame]
key_files:
  created: []
  modified:
    - firestarter_app/firestarter/constants.py
    - firestarter_app/firestarter/serial_comm.py
    - firestarter_app/tests/test_serial_comm.py
decisions:
  - "D-04 honored: no plaintext bypass for CMD_FW_VERSION — every command including the version probe goes through the framed path automatically"
  - "D-03 not applied: _validate_firmware_version version floor left unchanged (planner discretion; framed-protocol contract is not affected)"
  - "Encode order locked: CRC8 computed over raw json_bytes BEFORE COBS encode (ADR §4.3) — reversed order would silently break firmware CRC8 verify"
metrics:
  duration: "5m"
  completed: "2026-06-02"
  tasks_completed: 2
  files_changed: 3
---

# Phase 51 Plan 02: Host-Side COBS+CRC8 Command Frame Emission Summary

`send_json_command()` now emits a single atomic COBS+CRC8 frame with a 0x00 delimiter; the version probe is framed automatically; `CMD_FRAME_MAX = 512` added as the host half of the firmware/host parity pair.

## What Was Built

### Task 1: CMD_FRAME_MAX constant + RED COBS-frame emission tests

- **`constants.py`** — added `CMD_FRAME_MAX = 512` in the `# Constants` block alongside `BUFFER_SIZE`. Comment notes it is the host half of the firmware/host parity pair, matching `firestarter.h #define CMD_FRAME_MAX DATA_BUFFER_SIZE` (FRAME-05 / D-06 / CLAUDE.md sync rule).
- **`tests/test_serial_comm.py`** — added three RED tests:
  - `test_send_json_command_emits_cobs_frame`: sends `{"cmd":2,"value":42}`; verifies written bytes end with `b"\x00"`, body contains no `b"\x00"`, `cobs_decode(body)` produces `payload + crc_byte` where `crc_byte == _crc8_ccitt(payload)` and `json.loads(payload)` matches the input dict.
  - `test_send_json_command_atomic_frame`: monkeypatches `fake_serial.write` to count calls; asserts exactly 1 call carrying the full frame including the trailing `b"\x00"` (SAFE-01 sub-claim B).
  - `test_send_json_command_version_probe_is_framed`: sends `{"state": COMMAND_FW_VERSION}`; asserts frame ends with `b"\x00"` and does NOT start with `b"{"` (D-04).
- Tests confirmed RED: current `send_json_command()` emits raw JSON ending with `b"}"`, not a COBS frame.

### Task 2: Wrap send_json_command in a single atomic COBS+CRC8 frame (GREEN)

- **`serial_comm.py`** — extended the existing `from firestarter.frame_parser import (...)` block to also import `cobs_encode`. Replaced `send_json_command()`:
  ```python
  json_bytes = json.dumps(command_dict, separators=(",", ":")).encode("ascii")
  crc = _crc8_ccitt(json_bytes)
  body = cobs_encode(json_bytes + bytes([crc]))
  frame = body + b"\x00"
  return self.send_bytes(frame)
  ```
  Encode order: CRC8 over raw `json_bytes` FIRST, then `cobs_encode(json_bytes + crc_byte)` — matches ADR §4.3. `frame` is one `bytes` object; `send_bytes()` called once (SAFE-01 B).
- **`tests/test_serial_comm.py`** — imports reorganised to top of file (ruff I001 fix from mid-file imports placed in Task 1 RED commit).
- All three FRAME-05 tests pass GREEN; full 413-test suite passes; 70% coverage floor held.

## Verification Results

```
python -m pytest tests/test_serial_comm.py -k "cobs_frame or atomic_frame or version_probe_is_framed" -v
  3/3 PASSED (test_send_json_command_emits_cobs_frame,
              test_send_json_command_atomic_frame,
              test_send_json_command_version_probe_is_framed)

python -m pytest tests/test_serial_comm.py tests/test_cobs.py -x
  46/46 PASSED (23 serial_comm + 23 cobs)

python -m pytest --cov-fail-under=70
  413/413 PASSED; 29 snapshots passed
```

## Acceptance Criteria Confirmation

| Criterion | Status |
|-----------|--------|
| `grep "CMD_FRAME_MAX" firestarter_app/firestarter/constants.py` returns `CMD_FRAME_MAX = 512` | PASS |
| `grep -n "cobs_encode" serial_comm.py` shows it imported and used in send_json_command | PASS (lines 53, 173) |
| `send_json_command` contains `cobs_encode(json_bytes + bytes([crc]))` | PASS |
| `send_json_command` contains `frame = body + b"\x00"` and `return self.send_bytes(frame)` | PASS |
| `send_json_command` no longer calls `send_string` | PASS (grep returns nothing for send_string in send_json_command) |
| `python -m pytest tests/test_serial_comm.py -x` exits 0 | PASS |
| `python -m pytest tests/test_cobs.py` exits 0 | PASS |
| `python -m pytest --cov-fail-under=70` exits 0 | PASS |

## Must-Haves Confirmation

| Truth | Status |
|-------|--------|
| `send_json_command()` emits a single COBS+CRC8 frame ending in `0x00` — no `0x00` byte in body | PROVEN by `test_send_json_command_emits_cobs_frame` |
| CRC8 computed over RAW json_bytes BEFORE COBS encode; round-trip decodable | PROVEN by round-trip decode assertion in `test_send_json_command_emits_cobs_frame` |
| Full frame written in exactly one `connection.write()` call (SAFE-01 sub-claim B) | PROVEN by `test_send_json_command_atomic_frame` |
| CMD_FW_VERSION version probe emitted through the framed path (D-04) | PROVEN by `test_send_json_command_version_probe_is_framed` |
| `CMD_FRAME_MAX = 512` exists in constants.py | CONFIRMED — grep returns `CMD_FRAME_MAX = 512` |

## Security (Threat Model)

| Threat | Mitigation Status |
|--------|------------------|
| T-51-04: Timing / Bus-aliasing via split-write | MITIGATED — full frame incl. `0x00` is one `bytes` object, one `send_bytes()` call; proven by `test_send_json_command_atomic_frame` |
| T-51-05: Tampering via wrong CRC order | MITIGATED — CRC8 computed over RAW `json_bytes` before COBS encode (ADR §4.3); round-trip verified in `test_send_json_command_emits_cobs_frame` |
| T-51-06: Spoofing via plaintext escape hatch | MITIGATED — no `send_string` bypass for any command; proven by `test_send_json_command_version_probe_is_framed` (frame does not start with `{`) |
| T-51-SC: pip/cargo installs | ACCEPTED — no new packages; all primitives in-repo |

## Deviations from Plan

None — plan executed exactly as written. Imports were reorganised to the top of the test file (ruff I001 lint fix) as part of Task 2 cleanup, which is in keeping with the project's enforced tooling gate.

## Requirements Closed

- **FRAME-05** (host half): host emits framed COBS+CRC8 commands; version probe framed (D-04)
- **CRC-01** (command channel): CRC8 over raw payload, carried in every command frame

## Commits

| Task | Commit | Description |
|------|--------|-------------|
| Task 1 | 9503832 | test(51-02): add CMD_FRAME_MAX constant + RED COBS-frame emission tests |
| Task 2 | db6a545 | feat(51-02): wrap send_json_command in atomic COBS+CRC8 frame (GREEN) |

## Known Stubs

None — all changes wire directly to production `send_bytes()` with real COBS+CRC8 primitives from `frame_parser.py`. No placeholder data flows to any output path.

## Threat Flags

None — no new network endpoints, auth paths, file access patterns, or schema changes beyond those already in the plan's threat model.

## Self-Check: PASSED

- `firestarter_app/firestarter/constants.py` CMD_FRAME_MAX — FOUND (`CMD_FRAME_MAX = 512`)
- `firestarter_app/firestarter/serial_comm.py` cobs_encode import + use — FOUND (lines 53, 173)
- `firestarter_app/tests/test_serial_comm.py` three COBS tests — FOUND
- Commit 9503832 — FOUND (git log)
- Commit db6a545 — FOUND (git log)
- pytest tests/test_serial_comm.py: 23/23 PASSED
- pytest --cov-fail-under=70: 413/413 PASSED
