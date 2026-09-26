---
phase: 74
plan: "02"
subsystem: firmware
tags: [flash4, SDP, page-write, chip-id, dispatch, TDD, flash-budget]
dependency_graph:
  requires: [74-01]
  provides: [FIX-02A, FIX-02B]
  affects: [firestarter/src/proms/flash_type_4.cpp, firestarter/src/proms/flash_type_3.cpp, firestarter/src/proms/flash_utils.cpp, firestarter/include/flash_utils.h]
tech_stack:
  added: []
  patterns: [RED-GREEN-REFACTOR, recording-bus-stub, data-driven-page-size, shared-flash-util]
key_files:
  created: []
  modified:
    - firestarter/src/proms/flash_type_4.cpp
    - firestarter/src/proms/flash_type_3.cpp
    - firestarter/src/proms/flash_utils.cpp
    - firestarter/include/flash_utils.h
    - firestarter/test/native/avr/test_dispatch/test_configure_memory.cpp
    - firestarter/test/native/avr/test_val_flash4/test_val_flash4.cpp
decisions:
  - "Option A (inline mirror) used for initial FIX-02A implementation, then refactored to Option B (shared util) to satisfy the 89.5% flash-ceiling threshold"
  - "flash4_page_size() data-driven: mem_size<=65536→64, <=262144→128, else→256 (W29C040=256)"
  - "SDP unlock called per-page-start (NOT per-byte) per W29C040 page-load protocol"
  - "flash4_erase_execute NOT modified — T-74-VPP-LATENT is dead-code; erase path never triggered for any flash4 DB chip"
  - "delayMicroseconds() mocked in test_val_flash4 setUp to support operation-phase tests"
metrics:
  duration: "10 minutes"
  completed: "2026-06-18"
  tasks_completed: 3
  files_modified: 6
---

# Phase 74 Plan 02: FIX-02A + FIX-02B — flash4 Correctness Fixes Summary

**One-liner:** Flash4 CMD_CHECK_CHIP_ID dispatch mirror + W29C040 SDP/page-write fix, proven VPP-safe by recording-stub tests; flash budget mitigated to 89.5% via shared AMD chip-ID util.

## Tasks Completed

| Task | Name | Commit | Key Files |
|------|------|--------|-----------|
| 1 | FIX-02A RED→GREEN CMD_CHECK_CHIP_ID dispatch | 2699d11 | flash_type_4.cpp, test_configure_memory.cpp |
| 2 | FIX-02B RED→GREEN SDP unlock + page-size fix | 6924349 | flash_type_4.cpp, test_val_flash4.cpp |
| 3 | Option B flash-budget mitigation + non-regression gate | d4a1b74 | flash_utils.h/.cpp, flash_type_3.cpp, flash_type_4.cpp |

## What Was Built

### FIX-02A: CMD_CHECK_CHIP_ID dispatch in configure_flash4

Added `case CMD_CHECK_CHIP_ID:` to `configure_flash4` in `flash_type_4.cpp`, setting `firestarter_operation_init = NULL` and `firestarter_operation_main = flash4_check_chip_id_execute`. This mirrors the existing `configure_flash3` pattern exactly.

Initially implemented as Option A (inline `flash4_check_chip_id_execute` + `flash4_get_chip_id` copied from flash3). After flash-budget mitigation (Task 3), these delegate to shared `flash_util_check_chip_id_execute` / `flash_util_get_chip_id` in `flash_utils.cpp`.

**RED confirmed:** 3 new dispatch tests (0x05/0x35/0x39 CMD_CHECK_CHIP_ID) failed before the fix — `firestarter_operation_main` was NULL (no case in switch). **GREEN:** All 18 dispatch tests pass after adding the case.

### FIX-02B: SDP unlock + data-driven page size in flash4_write_execute

**Two defects fixed:**

1. **Missing SDP unlock:** Added `flash_execute_command(FLASH_ENABLE_WRITE)` at the start of each page load (`is_page_start = (address % page_size) == 0` OR `is_first_byte`). The W29C040 ships with Software Data Protection enabled; bare page-buffer loads are silently rejected without the 3-byte SDP sequence.

2. **Wrong PAGE_SIZE 64:** Replaced the compile-time `#define PAGE_SIZE 64` with a data-driven helper `flash4_page_size(handle->mem_size)` that derives page size at runtime.

**RED confirmed:** `test_flash4_write_execute_emits_sdp` failed before fix — the recording scan for MSB pattern {0x55, 0x2A, 0x55} (addresses 0x5555/0x2AAA/0x5555) found nothing. **GREEN:** All 8 val_flash4 tests pass after fix.

**SDP timing (no-interleave confirmation):** The SDP sequence calls `flash_util_byte_flipping` which terminates with `handle->firestarter_set_control_register(handle, CTRL_READ_WRITE, 0)` immediately before the loop exits. The next call in `flash4_write_execute` is `handle->firestarter_set_data(handle, address, expected)` directly — no Serial, no delay, no complex operation between the SDP 3rd byte and the first data write. At 16 MHz AVR the transition time is ~10-20µs, well within the W29C040's 150µs inactivity timeout.

### Data-Driven Page Size — No-Regression Argument

The derivation `flash4_page_size(mem_size)`:
- `mem_size <= 65536` → 64 bytes (AT29C256, 32K; W29C512 neighbors)
- `mem_size <= 262144` → 128 bytes (SST29EE010, AT29C010A, 128K chips)
- else → 256 bytes (W29C040, AT29C040, SST29EE040, 512K chips)

The 27 flash4 0x05 chips in the DB span 32KB–512KB. The W29C040 (the failing chip, 512K → 256) now gets the correct page size. For chips with smaller native pages (e.g., AT29C256 at 64B), using page_size=256 spans multiple physical 64B pages. The W29C040 has a 150µs WE# inactivity timer that auto-commits each physical sub-page when the inter-byte gap exceeds the timeout. At AVR 16 MHz with the production `memory_set_data` path (3µs delayMicroseconds per byte), inter-byte time is well under 150µs, so the firmware polls at the 256-byte boundary only after all sub-pages have been committed. The old fixed `64` polled mid-page on the W29C040 (DQ7 from an uncommitted page buffer is undefined). Data-driven sizing resolves both: W29C040 gets exact boundary polling; smaller chips get conservative but functionally correct polling at their full capacity.

### Flash-Budget Mitigation (Option B)

Post-Tasks 1+2 Leonardo flash: **90.2% (25868/28672)** — exceeded the 89.5% threshold by 0.7%.

Applied Option B: moved the shared AMD/JEDEC chip-ID read (`FLASH_ENABLE_ID → get_data(0) → get_data(1) → FLASH_DISABLE_ID`) and mismatch-check logic into `flash_utils.cpp` as `flash_util_get_chip_id()` and `flash_util_check_chip_id_execute()`. Both `flash3_check_chip_id_execute/get_chip_id` and `flash4_check_chip_id_execute/get_chip_id` now delegate to the shared functions.

Post-mitigation Leonardo flash: **89.5% (25654/28672)** — exactly at threshold, headroom = 3018 bytes.

## Test Results

### Native Test Suite (full run after all tasks)
```
82 test cases: 82 succeeded
```
(77 pre-existing + 5 new: 3 dispatch + 2 val_flash4)

### Dispatch Suite (test_dispatch)
- 15 pre-existing tests: all PASS
- 3 new FIX-02A tests (0x05/0x35/0x39 CMD_CHECK_CHIP_ID): PASS

### Val Flash4 Suite (test_val_flash4)
- 6 pre-existing configure-phase VPP-safety tests: PASS
- `test_flash4_write_execute_emits_sdp`: PASS (RED before fix, GREEN after)
- `test_flash4_write_execute_no_vpp`: PASS (was GREEN before fix, stays GREEN after)

### Host Gates
- `python3 tools/check_dispatch.py`: PASS (744 chips, 730 supported, 0 regressions)
- `python3 tools/diff_db.py`: PASS (0 changed chips)

### Build
- `pio run -e leonardo`: SUCCESS — 89.5% flash (post-mitigation)
- `git status -- "*.toml"`: clean — no messages.toml changes

## Leonardo Flash Percentage (VERBATIM)

**Pre-mitigation (after Tasks 1+2):**
```
Flash: [========= ]  90.2% (used 25868 bytes from 28672 bytes)
```

**Post-mitigation (after Task 3 Option B):**
```
Flash: [========= ]  89.5% (used 25654 bytes from 28672 bytes)
```
Baseline: 88.9% (25482/28672). Total delta: +172 bytes (pre-mitigation: +386 bytes, mitigation saved 214 bytes).

## Deviations from Plan

### Auto-applied

**1. [Rule 1 - Bug] ArduinoFake delayMicroseconds not mocked — SIGABRT in operation-phase test**
- **Found during:** Task 2 initial RED run
- **Issue:** `flash4_wait_for_page_write` calls `delayMicroseconds(10)`. ArduinoFake aborts on unmocked virtual calls. The SIGABRT crashed the test binary after 6 tests, before the new tests could run.
- **Fix:** Added `When(Method(ArduinoFake(), delayMicroseconds)).AlwaysReturn();` to `setUp` in `test_val_flash4.cpp`.
- **Files modified:** `firestarter/test/native/avr/test_val_flash4/test_val_flash4.cpp`
- **Commit:** 6924349

**2. [Rule 2 - Option B mitigation] Flash ceiling exceeded 89.5% threshold — applied shared util**
- **Found during:** Task 3 non-regression gate
- **Issue:** Post-Tasks 1+2 Leonardo flash = 90.2%, exceeding the 89.5% plan threshold.
- **Fix:** Applied Option B per plan's conditional mitigation: moved shared AMD chip-ID logic to `flash_util_get_chip_id` + `flash_util_check_chip_id_execute` in `flash_utils.cpp/.h`; flash3 and flash4 delegate to the shared functions.
- **Files modified:** `flash_utils.h`, `flash_utils.cpp`, `flash_type_3.cpp`, `flash_type_4.cpp`
- **Result:** 89.5% (25654/28672) — at threshold, 3018 bytes headroom.
- **Commit:** d4a1b74

### VPP Test 2 Was GREEN Before Fix (as designed)

Per plan: "`test_flash4_write_execute_no_vpp` passes for the bare loop today but MUST keep passing after the SDP fix." The test was intentionally designed as a "won't regress" proof (not a true RED test). It verified before the fix that the bare write loop had no VPP bits, and verified after that adding `flash_execute_command(FLASH_ENABLE_WRITE)` doesn't introduce VPP bits (confirmed: `flash_util_byte_flipping` only sets CTRL_READ_WRITE).

## Threat Mitigation Results

| Threat | Status |
|--------|--------|
| T-74-VPP: flash4_write_execute VPP-safety | MITIGATED — `test_flash4_write_execute_no_vpp` PASS: no CTRL_VPP_REGULATOR_ENABLE (0x80) or CTRL_VPP_P1_ENABLE (0x08) in any CONTROL_REGISTER write |
| T-74-VPP-LATENT: flash4_erase_execute dead VPP path | ACCEPTED — unchanged per plan; no flash4 DB chip has FLAG_CAN_ERASE |
| T-74-DISPATCH: CMD_CHECK_CHIP_ID dispatch | MITIGATED — dispatch tests prove non-NULL operation_main for 0x05/0x35/0x39 |

## Self-Check: PASSED

- `firestarter/src/proms/flash_type_4.cpp` contains `case CMD_CHECK_CHIP_ID:` — FOUND
- `firestarter/src/proms/flash_type_4.cpp` contains `FLASH_ENABLE_WRITE` — FOUND
- `firestarter/src/proms/flash_type_4.cpp` contains `flash4_page_size` — FOUND
- Thresholds 65536/262144/256 in flash_type_4.cpp — FOUND (lines 28-30)
- `grep -c "test_flash4_check_chip_id" test_configure_memory.cpp` = 6 (>= 3) — FOUND
- Commits: 2699d11, 6924349, d4a1b74 — all in git log
- Leonardo build: 89.5% SUCCESS — FOUND
- 82/82 native tests — FOUND
- check_dispatch.py PASS — FOUND
- diff_db.py PASS (0 changed chips) — FOUND
- No messages.toml changes — FOUND
- flash4_erase_execute NOT modified — FOUND (git diff shows no changes inside that function)
