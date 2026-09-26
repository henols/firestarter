---
phase: 54-even-block-data-transfers-full-buffer-aligned-host-fw-chunks
plan: "02"
subsystem: serial-transport
tags: [cobs, even-block, serial-transport, EVEN-01, firmware-max-chunk, eprom-operations]
dependency_graph:
  requires:
    - phase: 54-plan-01-firmware-nul-skip
      provides: firmware advertises 4-field identity string with maxchunk == DATA_BUFFER_SIZE
  provides:
    - host parses firmware_max_chunk from fw_fields[3] with .isdigit() guard (V5)
    - _calculate_buffer_size() returns firmware_max_chunk directly (no -2 arithmetic)
    - FirmwareOutdatedError raised on absent maxchunk field (D-05 no fallback)
    - test_even_block.py suite pinning no-remainder + frame cap boundary regressions
  affects:
    - firestarter_app/firestarter/serial_comm.py
    - firestarter_app/firestarter/eprom_operations.py
    - firestarter_app/firestarter/constants.py
    - firestarter_app/tests/test_even_block.py
    - firestarter_app/tests/test_frame_vectors.py
    - firestarter_app/tests/test_serial_comm.py
tech-stack:
  added: []
  patterns:
    - isdigit-guarded fw_fields[N] parse for firmware identity integer fields
    - getattr guard on communicator attribute with FirmwareOutdatedError on None (D-05 lockstep)
    - SimpleNamespace fake communicator injection for _calculate_buffer_size tests

key-files:
  created:
    - firestarter_app/tests/test_even_block.py
  modified:
    - firestarter_app/firestarter/serial_comm.py
    - firestarter_app/firestarter/eprom_operations.py
    - firestarter_app/firestarter/constants.py
    - firestarter_app/tests/test_frame_vectors.py
    - firestarter_app/tests/test_serial_comm.py
    - firestarter_app/tests/conftest.py

key-decisions:
  - "D-04: host reads firmware_max_chunk directly from fw_fields[3]; no -2 arithmetic remains"
  - "D-05: FirmwareOutdatedError raised on absent maxchunk (no buf-2 fallback); lockstep only"
  - "D-06: both write and verify legs go through _calculate_buffer_size() single seam"
  - "conftest make_comm factory extended with firmware_buffer_size + firmware_max_chunk = None defaults"
  - "Rule 2 deviation: FirmwareOutdatedError import added to eprom_operations.py (was missing despite plan claim)"
  - "Rule 1 deviation: MAX_DATA_CHUNK unused import removed from eprom_operations.py per ruff F401 gate"

patterns-established:
  - "isdigit-guarded fw_fields[N] integer parse is the canonical pattern for all future identity-string fields"
  - "make_comm conftest factory must be kept in sync with SerialCommunicator.__init__ attributes"

requirements-completed: [EVEN-01]

duration: ~20min
completed: 2026-06-04
---

# Phase 54 Plan 02: Host Consumes maxchunk — _calculate_buffer_size Summary

**Host parses firmware-advertised `<maxchunk>` (fw_fields[3], .isdigit()-guarded) and returns it directly from `_calculate_buffer_size()`, eliminating the `buf-2` arithmetic and pinning the no-remainder regression with a new test suite.**

## Performance

- **Duration:** ~20 min
- **Started:** 2026-06-04T00:00:00Z
- **Completed:** 2026-06-04
- **Tasks:** 2
- **Files modified:** 6 (3 production + 3 test)

## Accomplishments

- `serial_comm.py` now declares `firmware_max_chunk: Optional[int] = None` and parses `fw_fields[3]` with the existing `.isdigit()` guard pattern (V5 integer-only input validation, T-54-03 mitigated)
- `_calculate_buffer_size()` reads `firmware_max_chunk` directly — 512 stays 512, 1024 stays 1024, absent raises `FirmwareOutdatedError` (D-05 lockstep, no fallback)
- `test_even_block.py` created with `TestEvenBlockNoRemainder` (no-remainder arithmetic for 65536-byte chips and power-of-two sizes), `TestFirmwareMaxChunkParse` (maxchunk contract + -2 removal pin), `TestEvenBlockFrameVectorsCapBoundary` (512-byte COBS round-trip at MAIN-path cap)
- `test_frame_vectors.py` `TestHostChunkFitsFirmwareDecodeCap` and `TestPerBoardBufferNegotiation` updated to the new maxchunk contract — no test asserts `1022`/`510`/`MAX_DATA_CHUNK` for `_calculate_buffer_size()` anymore
- Full test suite: 456 tests green (14 new tests added)

## Task Commits

1. **Task 1: Parse firmware_max_chunk + replace _calculate_buffer_size** - `95b5979` (feat)
2. **Task 2: Add test_even_block.py + update breaking test classes** - `af7e48e` (test)

## Files Created/Modified

- `firestarter_app/firestarter/serial_comm.py` — added `firmware_max_chunk: Optional[int] = None` attribute; parse logic in `_probe_port` for fw_fields[3]
- `firestarter_app/firestarter/eprom_operations.py` — replaced `_calculate_buffer_size()` body; added `FirmwareOutdatedError` import; removed unused `MAX_DATA_CHUNK` import
- `firestarter_app/firestarter/constants.py` — added OBSOLETE marker comment on `MAX_DATA_CHUNK`
- `firestarter_app/tests/test_even_block.py` — new test suite (CREATED)
- `firestarter_app/tests/test_frame_vectors.py` — updated two breaking test classes to new maxchunk contract
- `firestarter_app/tests/test_serial_comm.py` — added 3 firmware_max_chunk parse tests (-k max_chunk)
- `firestarter_app/tests/conftest.py` — added `firmware_buffer_size` and `firmware_max_chunk` defaults to make_comm factory

## Decisions Made

- `FirmwareOutdatedError` import added to `eprom_operations.py` (plan stated it was "already imported" but it was absent — deviation Rule 2/blocking)
- `MAX_DATA_CHUNK` import removed from `eprom_operations.py` when ruff F401 flagged it as unused (plan explicitly says "remove it only if ruff/the unused-import gate flags it" — done)
- conftest `make_comm` factory extended with both `firmware_buffer_size = None` and `firmware_max_chunk = None` to mirror `__init__` (needed for test correctness; the existing factory used `__new__` bypass)

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Missing Critical] FirmwareOutdatedError import was absent from eprom_operations.py**
- **Found during:** Task 1 (replace _calculate_buffer_size)
- **Issue:** Plan stated `FirmwareOutdatedError` is "already imported (Phase 38 STRUCT-04)" but inspection of the actual file showed it was NOT in the imports block
- **Fix:** Added `FirmwareOutdatedError` to the `from firestarter.exceptions import (...)` block
- **Files modified:** `firestarter_app/firestarter/eprom_operations.py`
- **Verification:** `ruff check` clean; exception raised correctly in tests
- **Committed in:** 95b5979 (Task 1)

**2. [Rule 1 - Bug] Unused MAX_DATA_CHUNK import removed**
- **Found during:** Task 1 post-edit ruff check
- **Issue:** `MAX_DATA_CHUNK` was imported in `eprom_operations.py` but became unused after `_calculate_buffer_size()` replacement; ruff F401 flagged it
- **Fix:** Removed the `MAX_DATA_CHUNK` import per plan instruction ("remove it only if ruff/the unused-import gate flags it")
- **Files modified:** `firestarter_app/firestarter/eprom_operations.py`
- **Verification:** `ruff check` clean
- **Committed in:** 95b5979 (Task 1)

---

**Total deviations:** 2 auto-fixed (1 missing import, 1 unused import)
**Impact on plan:** Both were correctness fixes; no scope creep. The plan's claim about FirmwareOutdatedError being pre-imported was incorrect for the current codebase state.

## Issues Encountered

- `make_comm` conftest fixture uses `__new__` to bypass `__init__`, so `firmware_max_chunk` was not set as an instance attribute. Tests accessing `comm.firmware_max_chunk` raised `AttributeError`. Fixed by adding both `firmware_buffer_size` and `firmware_max_chunk` defaults to the factory (Rule 3 — blocking issue).

## Known Stubs

None — no stub patterns introduced.

## Threat Flags

None — no new network endpoints, auth paths, file access patterns, or schema changes. T-54-03 mitigated: `fw_fields[3]` parse uses `.isdigit()` guard (integer-only, V5 input validation). T-54-04 accepted: `FirmwareOutdatedError` on absent field is the intended fail-fast for lockstep beta.

## Next Phase Readiness

- EVEN-01 host half complete; combined with Plan 01 firmware half, the full even-block data transfer is implemented
- Both write and verify legs covered by the single `_calculate_buffer_size()` seam (D-06 confirmed)
- No-remainder regression pinned in `test_even_block.py`
- Ready for Phase 54 Plan 03 (bench verification / RAM gate D-08) or wave close

## Self-Check: PASSED

- `firestarter_app/firestarter/serial_comm.py` — FOUND (firmware_max_chunk attribute declared, fw_fields[3] parse present)
- `firestarter_app/firestarter/eprom_operations.py` — FOUND (_calculate_buffer_size reads firmware_max_chunk, no fw_buf-2, FirmwareOutdatedError on None)
- `firestarter_app/firestarter/constants.py` — FOUND (MAX_DATA_CHUNK has OBSOLETE marker)
- `firestarter_app/tests/test_even_block.py` — FOUND (created, 10 tests)
- `firestarter_app/tests/test_frame_vectors.py` — FOUND (updated, no 1022/510/MAX_DATA_CHUNK assertions)
- `firestarter_app/tests/test_serial_comm.py` — FOUND (3 new max_chunk tests)
- Commit 95b5979 — FOUND (Task 1)
- Commit af7e48e — FOUND (Task 2)
- 456 tests green

---
*Phase: 54-even-block-data-transfers-full-buffer-aligned-host-fw-chunks*
*Completed: 2026-06-04*
