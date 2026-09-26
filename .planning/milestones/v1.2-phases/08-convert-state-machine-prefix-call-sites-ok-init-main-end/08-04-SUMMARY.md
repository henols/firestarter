---
phase: 08-convert-state-machine-prefix-call-sites-ok-init-main-end
plan: 04
subsystem: firmware-logging
tags: [logging-migration, macro-families, state-machine-acks, populate-sites, avr]
dependency_graph:
  requires: [08-01, 08-02, 08-03]
  provides: [LOG_OK_ID_*, LOG_INIT_ID_*, LOG_MAIN_ID_*, LOG_END_ID_*, LOG_DATA_ID_*, LOG_DATA_ID_U16_U16, LOG_DATA_ID_U32_U32]
  affects: [firestarter/include/logging_id.h, firestarter/src/operation_utils.cpp, firestarter/src/eprom_operations.cpp, firestarter/src/proms/eprom.cpp, firestarter/src/proms/flash_type_3.cpp, firestarter/src/proms/flash_type_4.cpp, firestarter/src/proms/memory.cpp]
tech_stack:
  added: [LOG_OK_ID_*, LOG_INIT_ID_*, LOG_MAIN_ID_*, LOG_END_ID_*, LOG_DATA_ID_* families, LOG_DATA_ID_U16_U16 composite, LOG_DATA_ID_U32_U32 composite]
  patterns: [one-line alias over LOG_ID_* primitives, do-while composite macro, two-line populate-site pattern (R-02)]
key_files:
  created: []
  modified:
    - firestarter/include/logging_id.h
    - firestarter/src/operation_utils.cpp
    - firestarter/src/eprom_operations.cpp
    - firestarter/src/proms/eprom.cpp
    - firestarter/src/proms/flash_type_3.cpp
    - firestarter/src/proms/flash_type_4.cpp
    - firestarter/src/proms/memory.cpp
decisions:
  - "LOG_DATA_ID_U32_U32 composite packs two u32 values as 8 big-endian bytes via do-while macro — same pattern as existing LOG_ID_U32"
  - "LOG_DATA_ID_U16_U16 composite packs two u16 values as 4 big-endian bytes — declared here for Plan 05 VPP/VPE symmetry"
  - "flash_type_3 and flash_type_4 committed separately (one commit per file) per Phase 7 pattern"
  - "Pre-existing test_flash_intel_vpp and test_eeprom28c_chip_id SIGABRT failures are out-of-scope (pre-dated this plan)"
metrics:
  duration: "~20 min"
  completed_date: "2026-05-18"
  tasks: 6
  files: 7
---

# Phase 08 Plan 04: Wave 4 Simple Call-Site Conversions Summary

Wave 4 simple-conversion complete — all unconditional OK/INIT/MAIN/END/DATA macro families added to logging_id.h and 7 firmware call-sites converted to emit via LOG_*_ID macros, with both AVR builds green continuously.

## Tasks Completed

| Task | Name | Commit | Key Changes |
|------|------|--------|-------------|
| 1 | Add LOG_OK_ID_* / LOG_INIT_ID_* / LOG_MAIN_ID_* / LOG_END_ID_* / LOG_DATA_ID_* families to logging_id.h | `155eb47` | 71 lines added; 5 new 6-macro families + 2 composites |
| 2 | Convert operation_utils.cpp send_main/init/end_done | `68a8021` | 3 call-sites converted |
| 3 | Convert eprom_operations.cpp send_ack_const + log_data_const | `cf403c9` | 2 call-sites converted |
| 4 | Convert proms/eprom.cpp Skipping-erase + Retries | `89f2940` | 2 populate-sites converted |
| 5a | Convert proms/flash_type_3.cpp Skipping-erase-of-memory | `eeb3193` | 1 populate-site converted |
| 5b | Convert proms/flash_type_4.cpp Skipping-erase | `c2c3ffb` | 1 populate-site converted |
| 6 | Convert proms/memory.cpp DATA-progress emit | `330e538` | 1 DATA-path populate-site converted |

## Flash Usage After Each Commit

| Commit | Description | Uno Flash | Leonardo Flash |
|--------|-------------|-----------|----------------|
| pre-plan (08-03 close) | baseline | 24,856 B (77.1%) | 27,042 B (94.3%) |
| `155eb47` | logging_id.h macros (header-only) | 24,856 B (77.1%) | 27,042 B (94.3%) |
| `68a8021` | operation_utils conversions | 24,832 B (77.0%) | 27,018 B (94.2%) |
| `cf403c9` | eprom_operations conversions | 24,812 B (76.9%) | 26,992 B (94.1%) |
| `89f2940` | proms/eprom conversions | 24,774 B (76.8%) | 26,954 B (94.0%) |
| `eeb3193` | flash_type_3 conversion | — | — |
| `c2c3ffb` | flash_type_4 conversion | — | — |
| `330e538` | memory.cpp DATA-progress | 24,712 B (76.6%) | 26,892 B (93.8%) |

**Net flash reduction: Uno −144 B, Leonardo −150 B** (24,856 → 24,712 / 27,042 → 26,892)

## Call-Site Conversion Summary

**State-machine ack sites converted (operation_utils.cpp):** 3
- `send_main_done()` → `LOG_MAIN_ID(MSG_MAIN_DONE)`
- `send_init_done()` → `LOG_INIT_ID(MSG_INIT_DONE)`
- `send_end_done()` → `LOG_END_ID(MSG_END_DONE)`

**Trivial OK/DATA acks converted (eprom_operations.cpp):** 2
- `send_ack_const("Req data")` → `LOG_OK_ID(MSG_OK_REQ_DATA)`
- `log_data_const("Sending data")` → `LOG_DATA_ID(MSG_DATA_SENDING)` (rurp_communication_write preserved)

**R-02 populate-sites converted:** 5
- eprom.cpp:104 `copy_to_buffer(response_msg, "Skipping erase.")` → `LOG_INFO_ID(MSG_INFO_SKIPPING_ERASE)`
- eprom.cpp:171 `format(response_msg, "Number of retries: %d", retries)` → `LOG_INFO_ID_U8(MSG_INFO_RETRIES, retries)`
- flash_type_3.cpp:88 `copy_to_buffer(response_msg, "Skipping erase of memory")` → `LOG_INFO_ID(MSG_INFO_SKIPPING_ERASE_MEM)`
- flash_type_4.cpp:52 `copy_to_buffer(response_msg, "Skipping erase.")` → `LOG_INFO_ID(MSG_INFO_SKIPPING_ERASE)`
- memory.cpp:397 `firestarter_data_response_format("%lu/%lu", addr, mem_size)` → `LOG_DATA_ID_U32_U32(MSG_DATA_PROGRESS, addr, mem_size)`

**Total call-sites converted: 10**

## Verification Results

- Both AVR builds (Uno + Leonardo) green after every commit
- `pio test -e native -f "*test_dispatch*"` — 15 tests PASSED
- `pio test -e native -f "*test_messages*"` — 5 tests PASSED
- `grep -c "send_main_done|send_init_done|send_end_done" src/operation_utils.cpp` = 0
- `grep -rn "copy_to_buffer(handle->response_msg" src/proms/` = 0 hits
- `grep -c "firestarter_data_response_format" src/proms/memory.cpp` = 0

## Deviations from Plan

None — plan executed exactly as written. The pre-existing SIGABRT failures in `test_flash_intel_vpp` and `test_eeprom28c_chip_id` native suites are out-of-scope (pre-dated this plan; test_dispatch and test_messages the targets specified in the plan both pass).

## Known Stubs

None — all conversions wire to real catalog IDs; no placeholder text or empty data flows.

## Threat Flags

None — no new network endpoints, auth paths, file access patterns, or schema changes introduced.

## Self-Check: PASSED

- `firestarter/include/logging_id.h` — exists and contains `#define LOG_MAIN_ID`
- `firestarter/src/operation_utils.cpp` — contains `LOG_MAIN_ID(MSG_MAIN_DONE)`
- `firestarter/src/eprom_operations.cpp` — contains `LOG_OK_ID(MSG_OK_REQ_DATA)`
- `firestarter/src/proms/memory.cpp` — contains `LOG_DATA_ID_U32_U32(MSG_DATA_PROGRESS`
- All 7 firestarter commits present in git log (155eb47..330e538)
