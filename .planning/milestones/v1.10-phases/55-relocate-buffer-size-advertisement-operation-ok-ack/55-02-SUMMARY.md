---
phase: 55-relocate-buffer-size-advertisement-operation-ok-ack
plan: 02
subsystem: firmware
tags: [firmware, cap-01, fw-version, msg-ok-ready, unity-test, cobs]

# Dependency graph
requires:
  - phase: 55-01
    provides: "MSG_OK_READY bytes param declaration in catalog; messages.h regenerated"
provides:
  - "FW_VERSION reverted to <version>:<board> only (no buffer-size suffix)"
  - "All 4 MSG_OK_READY emit sites carry DATA_BUFFER_SIZE as u16 param via LOG_OK_ID_U16"
  - "Unity test_ok_ready_u16_param_frame pins SC2 byte-exact contract (6/6 PASS)"
affects: [55-03]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "LOG_OK_ID_U16(MSG_OK_READY, (uint16_t)DATA_BUFFER_SIZE) — capacity advertised per-operation rather than in identity string"
    - "rurp_log_id_u16 big-endian packing pinned by Unity test: MSB=0x02, LSB=0x00 for 512"

key-files:
  created: []
  modified:
    - firestarter/include/firestarter.h
    - firestarter/src/firestarter.cpp
    - firestarter/src/hardware_operations.cpp
    - firestarter/src/dev_tools.cpp
    - firestarter/test/native/avr/test_messages/test_rurp_log_id.cpp

key-decisions:
  - "FW_VERSION stripped to VERSION \":\" RURP_BOARD_NAME only — the Phase 54 FS_STRINGIFY(DATA_BUFFER_SIZE) suffixes removed; host now reads capacity from the ack param, not the identity string"
  - "No new global buffer introduced — rurp_log_id_u16 uses its existing 2-byte stack array"
  - "Uno RAM 504 B free post-change (baseline 496 B post-Phase-54; no regression)"

requirements-completed: [CAP-01]

# Metrics
duration: 10min
completed: 2026-06-05
---

# Phase 55 Plan 02: Revert FW_VERSION macro + update MSG_OK_READY emit sites (CAP-01 firmware side)

**FW_VERSION is now `<version>:<board>` only; all 4 MSG_OK_READY emit sites carry DATA_BUFFER_SIZE as a big-endian u16 param; Unity test pins the 11-byte frame contract**

## Performance

- **Duration:** ~10 min
- **Started:** 2026-06-05
- **Completed:** 2026-06-05
- **Tasks:** 2
- **Files modified:** 5 (all in firestarter submodule)

## Accomplishments

- `firestarter/include/firestarter.h`: FW_VERSION macro changed from `VERSION ":" RURP_BOARD_NAME ":" FS_STRINGIFY(DATA_BUFFER_SIZE) ":" FS_STRINGIFY(DATA_BUFFER_SIZE)` to `VERSION ":" RURP_BOARD_NAME`; the Phase 54 comment block documenting the `<maxchunk>` field replaced with a CAP-01 note (capacity now advertised per-operation on MSG_OK_READY ack)
- `FS_STRINGIFY`/`FS_STRINGIFY2` helper macros retained (used elsewhere); only the FW_VERSION trailing fields removed
- 4 emit sites updated: `firestarter.cpp:138`, `hardware_operations.cpp:43`, `dev_tools.cpp:107`, `dev_tools.cpp:153` — all changed from `LOG_OK_ID(MSG_OK_READY)` to `LOG_OK_ID_U16(MSG_OK_READY, (uint16_t)DATA_BUFFER_SIZE)`
- Trailing comments on the two dev_tools.cpp sites preserved verbatim
- Uno build: SUCCESS; RAM 504 B free (2048 − 1544), above 496 B post-Phase-54 baseline
- Unity test `test_ok_ready_u16_param_frame` added — calls `rurp_log_id_u16(MSG_OK_READY, 512)`, asserts the exact 11-byte frame sequence (magic, len=4, id=0x01, params 0x02/0x00, CRC8 over body, anchor 0x0A), registered in RUN_TEST block; suite 6/6 PASSED

## Uno RAM Line (Acceptance Gate)

```
RAM:   [========  ]  75.4% (used 1544 bytes from 2048 bytes)
```

**Free RAM: 504 B** — above the 480 B floor and above the 496 B post-Phase-54 baseline. No regression.

## Task Commits

Each task committed atomically inside the firestarter submodule + meta pointer bump:

1. **Task 1: Revert FW_VERSION + update 4 MSG_OK_READY emit sites**
   - firestarter submodule: `3df0153` (feat)
   - meta-repo pointer: `9434d5a` (feat)

2. **Task 2: Unity test_ok_ready_u16_param_frame**
   - firestarter submodule: `ba1558d` (test)
   - meta-repo pointer: `8a84b5d` (test)

## Files Created/Modified

- `/workspaces/firestarter/include/firestarter.h` — FW_VERSION reverted; comment block updated for CAP-01
- `/workspaces/firestarter/src/firestarter.cpp` — LOG_OK_ID → LOG_OK_ID_U16 at init_programmer ack
- `/workspaces/firestarter/src/hardware_operations.cpp` — LOG_OK_ID → LOG_OK_ID_U16 at VPP/VPE probe ack
- `/workspaces/firestarter/src/dev_tools.cpp` — LOG_OK_ID → LOG_OK_ID_U16 at both dev-tool acks (lines 107+153)
- `/workspaces/firestarter/test/native/avr/test_messages/test_rurp_log_id.cpp` — test_ok_ready_u16_param_frame added + registered

## Decisions Made

- **No FS_STRINGIFY macros removed:** FS_STRINGIFY and FS_STRINGIFY2 are still defined in firestarter.h; they may be used by other future consumers. Only the FW_VERSION string concatenation that referenced them was changed. This avoids any risk of breaking dependents that might reference these macros indirectly.

## Deviations from Plan

None — plan executed exactly as written.

## Known Stubs

None.

## Threat Flags

None. No new security-relevant surface introduced. T-55-03 (byte-order tampering) is mitigated by the new Unity test pinning the exact 0x02/0x00 sequence and CRC8 for 512.

## Self-Check: PASSED

- `firestarter/include/firestarter.h` — exists, FW_VERSION line is `#define FW_VERSION VERSION ":" RURP_BOARD_NAME`
- `firestarter/src/firestarter.cpp` — LOG_OK_ID_U16(MSG_OK_READY present
- `firestarter/src/hardware_operations.cpp` — LOG_OK_ID_U16(MSG_OK_READY present
- `firestarter/src/dev_tools.cpp` — 2x LOG_OK_ID_U16(MSG_OK_READY present
- `firestarter/test/native/avr/test_messages/test_rurp_log_id.cpp` — test_ok_ready_u16_param_frame present + registered
- Submodule commits: 3df0153 (feat T1), ba1558d (test T2)
- Meta pointer commits: 9434d5a (T1), 8a84b5d (T2)
- `pio run -e uno`: SUCCESS, 504 B free
- `pio test -e native -f "*test_messages*"`: 6/6 PASSED

---
*Phase: 55-relocate-buffer-size-advertisement-operation-ok-ack*
*Completed: 2026-06-05*
