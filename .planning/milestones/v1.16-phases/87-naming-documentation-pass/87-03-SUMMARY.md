---
phase: 87-naming-documentation-pass
plan: 03
subsystem: testing
tags: [native-tests, unity, recording-bus, invariant-traceability, eprom, flash, sram]

# Dependency graph
requires:
  - phase: 87-naming-documentation-pass/87-01
    provides: "PROTOCOLS.md with INV-01..INV-09 matrix (suite paths + planned test function names)"
  - phase: 87-naming-documentation-pass/87-02
    provides: "INV ids greppable in handler header blocks (SAFE-02 second target)"
provides:
  - "INV-01..INV-09 live native test assertions in their matrix-assigned suite paths"
  - "SAFE-02 three-target contract complete: doc + handler + test for every INV"
  - "test_val_eprom: INV-01/02/03/05/06/08 gap-fill assertions"
  - "test_val_flash4: INV-04 256B page boundary proof (data-driven page-size)"
  - "test_val_sram: INV-07 FM1608 SRAM/FRAM routing assertion"
  - "test_val_flash3: INV-09 SST39SF040 keep-Flash/EEPROM assertion"
affects: [88-golden-traces, 89-recompose]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "INV-id embedded in test function names: test_inv0N_family_behavior()"
    - "Recording-bus assertion with is_page_start/is_first_byte logic for page-boundary detection"
    - "Pulse-delay default verification via handle->pulse_delay post-configure_memory"
    - "VPP routing bit distinction: assert REGULATOR_ENABLE present AND P1_ENABLE absent for 0x0B"

key-files:
  created: []
  modified:
    - firestarter/test/native/avr/test_val_eprom/test_val_eprom.cpp
    - firestarter/test/native/avr/test_val_flash4/test_val_flash4.cpp
    - firestarter/test/native/avr/test_val_sram/test_val_sram.cpp
    - firestarter/test/native/avr/test_val_flash3/test_val_flash3.cpp

key-decisions:
  - "INV-04 page-boundary test: 65-byte write from addr 0 with 512KB chip asserts count=1 SDP (not 2); page_size=64 would give 2, proving data-driven 256B selection"
  - "INV-03 test: requires pins=32 + vpp_line=VPP_P1_32_DIP on handle to activate using_p1_as_vpp(), then calls execute phase to observe CTRL_VPP_P1_ENABLE in recording"
  - "Recording buffer overflow (256 entries) prevented a 257-byte write test; switched to 65-byte probe that still discriminates 64B vs 256B pages"
  - "delayMicroseconds() mock added to test_val_eprom setUp (harmless for existing tests, required for INV-03 execute-phase test)"

patterns-established:
  - "SAFE-02 contract: grep -rn INV-0x hits doc (PROTOCOLS.md) + handler (src/proms/*.cpp) + test (test/native/avr/test_val_*/*.cpp)"
  - "Frozen-world compliance: no handler executable code changed to satisfy any test"

requirements-completed: [NAME-03, SAFE-06]

# Metrics
duration: 10min
completed: 2026-06-26
---

# Phase 87 Plan 03: INV-01..INV-09 Native Test Traceability Matrix Summary

**Nine live Unity assertions across 4 native test suites complete the SAFE-02 doc+handler+test traceability contract for every firmware behavioral invariant**

## Performance

- **Duration:** ~10 min
- **Started:** 2026-06-26T06:35:41Z
- **Completed:** 2026-06-26T06:46:00Z
- **Tasks:** 2 (Task 1: write gap-fill assertions; Task 2: verify native suite green)
- **Files modified:** 4

## Accomplishments

- Added 9 INV-id-bearing test functions (INV-01 through INV-09) in their PROTOCOLS.md matrix-assigned suite paths, completing the SAFE-02 three-target grep contract
- All 91 native tests pass (82 prior + 9 new INV assertions); no handler executable code changed (frozen-world preserved)
- Resolved a recording-buffer overflow issue in INV-04 by switching from a 257-byte write (overflow at entry 256) to a 65-byte probe that discriminates 64B vs 256B pages via SDP-count

## Task Commits

1. **Task 1: Map/annotate INV-01..09 gap-fill assertions** — `b67acde` (feat)
2. **Task 2: Run native suites — exit 0, 91/91** — (no file changes; verified in task 1 commit)

## Files Created/Modified

- `/workspaces/firestarter/test/native/avr/test_val_eprom/test_val_eprom.cpp` — added INV-01/02/03/05/06/08 gap-fill assertions; added delayMicroseconds mock to setUp; added rurp_shield.h + memory_utils.h includes
- `/workspaces/firestarter/test/native/avr/test_val_flash4/test_val_flash4.cpp` — added INV-04 256B page boundary proof via SDP-count probe
- `/workspaces/firestarter/test/native/avr/test_val_sram/test_val_sram.cpp` — added INV-07 FM1608 SRAM/FRAM routing assertion
- `/workspaces/firestarter/test/native/avr/test_val_flash3/test_val_flash3.cpp` — added INV-09 SST39SF040 Flash/EEPROM classification assertion

## Decisions Made

- **INV-04 probe method**: 65-byte write starting at address 0 asserts exactly 1 SDP sequence for a 512KB (W29C040) chip. If page_size were 64B (the old bug), address 64 would be a page boundary triggering a second SDP (count=2). The single SDP proves page_size=256B. This avoids the recording-buffer overflow that a 257-byte write would cause (recording buffer holds 256 entries; 257 bytes × 3 writes/byte = 771 entries needed).
- **INV-03 execute phase**: Configure + init + execute is the correct path to observe CTRL_VPP_P1_ENABLE in the recording. The init phase (eprom_check_vpp) fires REGULATOR_ENABLE; the execute phase (program_mismatched_bytes) fires CTRL_VPE_ENABLE which eprom_internal_set_control_register flips to CTRL_VPP_P1_ENABLE when using_p1_as_vpp is true. A clear_bus_recording() between init and execute isolates the P1 bit in the execute-phase recording.
- **INV-02 scope**: Scoped to configure-only phase (no init call for CMD_READ). The "read skip" is implemented by the production path not calling firestarter_operation_init during reads — the test documents this by asserting no VPP bits appear in the configure-only recording.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Recording-buffer overflow in INV-04 initial design**
- **Found during:** Task 2 (native test run)
- **Issue:** Initial test used data_size=257 starting at address 0. With 3 register writes per byte (LSB + MSB + CONTROL from mem_util_set_address), 257 bytes × 3 = 771 writes, which overflows the 256-entry recording buffer. The second SDP sequence at byte 256 was never captured, giving count=1 when 2 was expected.
- **Fix:** Switched to data_size=65 from address 0. For page_size=256: only 1 SDP fires (addr 0 is first_byte + page_start; addr 64 is NOT a 256B boundary). For page_size=64: 2 SDPs fire (addr 0 and addr 64). The assert becomes count==1 (not 2), which PROVES 256B pages. Total recording entries: ~206, well within 256.
- **Files modified:** firestarter/test/native/avr/test_val_flash4/test_val_flash4.cpp
- **Verification:** pio test -e native exits 0, INV-04 passes
- **Committed in:** b67acde (Task 1 commit)

---

**Total deviations:** 1 auto-fixed (Rule 1 — test assertion logic bug caught during first run)
**Impact on plan:** Fix required to make INV-04 test correctly discriminate 64B vs 256B pages. No scope creep; the invariant being tested and the test function name are unchanged.

## Issues Encountered

None — all other tests passed on first run. The recording-buffer overflow was diagnosed and fixed within Task 2 before committing.

## Unity Result (pio test -e native)

```
================= 91 test cases: 91 succeeded in 00:00:15.962 =================
```

All suites green:
- test_val_eprom PASSED (includes INV-01/02/03/05/06/08)
- test_val_flash4 PASSED (includes INV-04)
- test_val_sram PASSED (includes INV-07)
- test_val_flash3 PASSED (includes INV-09)
- All 10 other suites PASSED

## Known Stubs

None — all 9 INV assertions exercise live handler code via the recording-bus stub. No placeholder assertions or TODO comments.

## Threat Flags

None — test-only change. No handler executable code touched; no wire/protocol/DB surface introduced.

## Next Phase Readiness

- SAFE-02 three-target grep contract fully satisfied: `grep -rn INV-0x` hits doc + handler + test for every INV
- Phase 87 Plan 04 can run its check_dispatch.py / diff_db.py gates and Leonardo flash delta check (Plan 03 touches only test files — zero flash impact)
- Phase 88 golden-trace suite can extend the existing test_val_* harnesses without changing these minimal INV assertions

## Self-Check: PASSED

- FOUND: firestarter/test/native/avr/test_val_eprom/test_val_eprom.cpp
- FOUND: firestarter/test/native/avr/test_val_flash4/test_val_flash4.cpp
- FOUND: firestarter/test/native/avr/test_val_sram/test_val_sram.cpp
- FOUND: firestarter/test/native/avr/test_val_flash3/test_val_flash3.cpp
- FOUND: commit b67acde (feat(87-03): add INV-01..INV-09 live native test assertions)

---
*Phase: 87-naming-documentation-pass*
*Completed: 2026-06-26*
