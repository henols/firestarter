---
phase: 50-data-path-framing-layer-automatic-resync-dual-repo-lockstep
plan: 03
subsystem: serial-transport
tags: [cobs, crc8, framing, serial, python, frame_parser, eprom_operations]

# Dependency graph
requires:
  - phase: 50-data-path-framing-layer-automatic-resync-dual-repo-lockstep/50-01
    provides: "RED host pytest test_cobs.py pinning the COBS frame contract"
  - phase: 50-data-path-framing-layer-automatic-resync-dual-repo-lockstep/50-02
    provides: "Firmware COBS decode-in-place rewrite of rurp_communication_read_data"
provides:
  - "cobs_encode / cobs_decode in frame_parser.py (stdlib-only, mypy-strict, no new CRC)"
  - "_main_phase_send_data emits b'#' + COBS(chunk+CRC8) + b'\x00' atomically"
  - "Wave-0 host pytest (test_cobs.py) turned GREEN — all 21 cases pass"
  - "functools/operator unused imports removed; frame_parser import added"
affects:
  - "50-04-PLAN (firmware RAM gate + post-change build verification)"
  - "50-05-PLAN (phase gate: full host+firmware suite verification)"
  - "v1.9 RCA (serial transport hardened before resuming read-bug investigation)"

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "COBS encode: scan runs of <=254 non-zero bytes, emit code+run, handle 254-run phantom-zero edge"
    - "COBS decode: bounded-decode with ValueError on 0x00-in-body or run overrun (T-50-02 control)"
    - "Atomic data-block send: one bytes object assembled, one send_bytes call (T-50-05 SAFE-01)"
    - "CRC8-CCITT reused unchanged from _crc8_ccitt/_build_crc8_table (D-05/CRC-01)"

key-files:
  created: []
  modified:
    - "firestarter_app/firestarter/frame_parser.py (cobs_encode + cobs_decode added)"
    - "firestarter_app/firestarter/eprom_operations.py (_main_phase_send_data COBS frame + import cleanup)"

key-decisions:
  - "Place cobs_encode/cobs_decode in frame_parser.py beside _crc8_ccitt (stdlib-only leaf transforms, testable without serial I/O)"
  - "Use iterator-style cobs_encode that handles the 254-run/phantom-zero edge inline rather than a separate lookup table"
  - "Remove functools and operator imports after verifying they are unused elsewhere (ruff-verified)"

patterns-established:
  - "COBS body helpers: take/return bytes only (no delimiter); caller assembles b'#' + body + b'\x00'"
  - "Atomic write: entire frame including trailing 0x00 is one bytes object in one send_bytes call"

requirements-completed: [FRAME-01, FRAME-02, FRAME-04, CRC-01]

# Metrics
duration: 25min
completed: 2026-06-01
---

# Phase 50 Plan 03: Host COBS Frame Implementation (GREEN) Summary

**COBS encode/decode added to frame_parser.py and _main_phase_send_data switched to b"#"+COBS(chunk+CRC8)+b"\x00" atomic send, turning all 21 Wave-0 host pytest cases GREEN with ruff+mypy+coverage gates passing.**

## Performance

- **Duration:** ~25 min
- **Started:** 2026-06-01T00:00:00Z
- **Completed:** 2026-06-01
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments

- Added `cobs_encode` and `cobs_decode` to `frame_parser.py` (73 lines): streaming COBS encoder handling 254-run phantom-zero edge (Pitfall 2); decoder raises `ValueError` on `0x00`-in-body or run overrun (bounded-decode T-50-02 control); full type hints + docstrings; strict mypy + ruff clean
- Replaced `[len_u16][xor]` header in `_main_phase_send_data` with the locked COBS frame: `crc = _crc8_ccitt(chunk)`, `body = cobs_encode(chunk + bytes([crc]))`, `frame = b"#" + body + b"\x00"`, one `send_bytes(frame)` call (atomic-write mandate ADR §4.1 / T-50-05)
- Removed `functools` and `operator` unused imports; added `from firestarter.frame_parser import _crc8_ccitt, cobs_encode`
- All 21 `test_cobs.py` cases GREEN; full host suite 408 tests passed; coverage floor held; `serial_comm.py` and `_main_phase_read_data`/`_read_and_parse_lines` byte-unchanged (scope guard)

## Task Commits

1. **Task 1: Add cobs_encode / cobs_decode to frame_parser.py** - `8d801a0` (feat)
2. **Task 2: Switch _main_phase_send_data to COBS frame (atomic write)** - `0c33410` (feat)

## Files Created/Modified

- `firestarter_app/firestarter/frame_parser.py` — Added `cobs_encode` and `cobs_decode` beside existing `_crc8_ccitt` leaf functions; no new CRC table or polynomial (D-05/CRC-01); `MAGIC_PREAMBLE`/`_decode_id_frame` regions byte-unchanged
- `firestarter_app/firestarter/eprom_operations.py` — `_main_phase_send_data` frame contents replaced with COBS; `functools`/`operator` imports removed; `frame_parser` import added (sorted by ruff auto-fix)

## Decisions Made

- Placed `cobs_encode`/`cobs_decode` in `frame_parser.py` immediately after `_crc8_ccitt` to keep all pure wire-frame transforms co-located and stdlib-only (testable without serial I/O, matches module role)
- The 254-run edge (emit code 0xFF, no implicit zero consumed) is handled inline in `cobs_encode` with a `pass` branch — straightforward and matches PATTERNS.md decode reference exactly
- `cobs_encode` uses `while i <= n` with a break-on-end-of-payload approach to correctly emit the final run without appending a phantom zero after it
- `functools` and `operator` were confirmed to have no other callers in the file (grep) before removal

## Deviations from Plan

None - plan executed exactly as written. The import ordering deviation (ruff I001) was handled by `ruff --fix`, which is the standard ruff correction workflow, not a scope deviation.

## Issues Encountered

- **ruff import ordering (I001):** Inserting the `from firestarter.frame_parser import` line required isort-correct placement. Initial placement triggered a ruff I001 error; resolved via `ruff check --fix` (ruff auto-sorted the import block to the correct position alphabetically between `exceptions` and `serial_comm`).

## Scope Guard Verification

- `git -C firestarter_app diff --stat firestarter/serial_comm.py` — empty (unchanged)
- `_main_phase_read_data`, `_read_and_parse_lines`, `MSG_DATA_CHUNK` handling — byte-unchanged
- `MAGIC_PREAMBLE`, `_decode_id_frame` regions in `frame_parser.py` — byte-unchanged (only additions, no modifications)
- `grep -c 'to_bytes(2, "big")' eprom_operations.py` — returns 0 (no len_u16 on send path)
- `grep "operator.xor\|functools.reduce" eprom_operations.py` — empty (XOR removed)

## Next Phase Readiness

- Plan 03 host implementation complete — the COBS write-path is now dual-repo-lockstep with the Plan 02 firmware decoder
- Plan 04 (RAM gate + post-change firmware build verification) can proceed immediately
- Plan 05 (full phase gate: both suites green + RAM report) is the final verification wave before v1.9 RCA resumes

---
*Phase: 50-data-path-framing-layer-automatic-resync-dual-repo-lockstep*
*Completed: 2026-06-01*
