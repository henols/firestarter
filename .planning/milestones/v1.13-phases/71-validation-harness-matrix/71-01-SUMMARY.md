---
phase: 71-validation-harness-matrix
plan: 01
subsystem: testing
tags: [unity, platformio, native-tests, host-stubs, recording-buffer, c++, firmware]

# Dependency graph
requires: []
provides:
  - "Define-guarded register-write recording buffer in host_stubs_common.inc (HOST_STUBS_RECORD_BUS opt-IN)"
  - "Four C-linkage recording API symbols: clear_bus_recording, bus_recording_count, recorded_reg, recorded_data"
  - "Bound-checked recording (HOST_STUBS_MAX_RECORDING=256) mitigating T-71-02 buffer overflow"
  - "Byte-identical flag-off no-op path for existing suites (test_dispatch, test_cobs_*, test_read_timing, test_messages, test_data_input, test_not_implemented, test_frame_vectors)"
affects:
  - "71-02 (test_val_eprom Tier-1 suite — consumes HOST_STUBS_RECORD_BUS)"
  - "71-03 through 71-06 (remaining Tier-1 per-family suites)"

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "opt-IN define-guard pattern for host stub behavior extensions (inverse of existing HOST_STUBS_CUSTOM_* opt-OUT guards)"
    - "static recording buffer with bound-checked append, reset, and indexed accessor API"

key-files:
  created: []
  modified:
    - "firestarter/test/native/avr/_shared/host_stubs_common.inc"

key-decisions:
  - "D-04 honored: recording buffer added to the EXISTING shared stub in-place (no second forked .inc file) — single edit point per WR-06"
  - "opt-IN guard (#ifdef HOST_STUBS_RECORD_BUS) is inverse of the existing opt-OUT guards (HOST_STUBS_CUSTOM_VOLTAGE_MV / HOST_STUBS_CUSTOM_HW_REVISION) — flag absent = today's behavior byte-identical"
  - "Bound check (if count < 256) enforced before each store — T-71-02 mitigation; firmware configure_* makes <20 register writes so no reachable overflow"

patterns-established:
  - "HOST_STUBS_RECORD_BUS: opt-IN flag per-family validation suite defines BEFORE including host_stubs_common.inc; existing suites define nothing and get the unchanged no-op"
  - "Recording API: clear_bus_recording() / bus_recording_count() / recorded_reg(int) / recorded_data(int) — extern C linkage, call from C++ test bodies"

requirements-completed: [HARN-01]

# Metrics
duration: 22min
completed: 2026-06-16
---

# Phase 71 Plan 01: Recording Bus Stub Foundation Summary

**Define-guarded `HOST_STUBS_RECORD_BUS` opt-IN recording buffer in `host_stubs_common.inc`: four extern-C API symbols, 256-entry bound-checked array, byte-identical no-op fallback for all existing native suites.**

## Performance

- **Duration:** 22 min
- **Started:** 2026-06-16T12:16:25Z
- **Completed:** 2026-06-16T12:38:47Z
- **Tasks:** 2 (Task 1: implementation + commit; Task 2: regression verification)
- **Files modified:** 1 (submodule)

## Accomplishments

- Extended `host_stubs_common.inc` in-place with the `#ifdef HOST_STUBS_RECORD_BUS` opt-IN recording block — no second stub file, WR-06 single-edit-point preserved.
- All four recording API symbols (`clear_bus_recording`, `bus_recording_count`, `recorded_reg`, `recorded_data`) declared `extern "C"` inside the `#ifdef` branch, with a `HOST_STUBS_MAX_RECORDING=256` bound-checked write path (T-71-02 mitigation).
- `#else` branch preserves the byte-identical original no-op (`(void)reg; (void)data;`) for all existing suites.
- Full regression suite green with flag off: `test_dispatch` 15/15 PASSED, `test_cobs_data_frame` + `test_cobs_cmd_frame` 11/11 PASSED, `test_read_timing` 4/4 PASSED. Zero linker "undefined reference" errors.
- Production flash unchanged: Uno 72.4% (23344 B / 32256 B), Leonardo 88.9% (25482 B / 28672 B) — the `.inc` file lives under `test/` and is excluded from the production `src_filter`.

## Task Commits

1. **Task 1: Add define-guarded recording buffer to host_stubs_common.inc** - `f4e2040` (test) — committed inside `firestarter/` submodule on `v1.13-algo-validation`
2. **Task 2: Prove flag-off regression** — verification only, no new files; existing suites passed without modification.

## Files Created/Modified

- `firestarter/test/native/avr/_shared/host_stubs_common.inc` — replaced the plain no-op `rurp_write_to_register` with an `#ifdef HOST_STUBS_RECORD_BUS` ... `#else` ... `#endif` block; net +35 lines, -3 lines.

## Decisions Made

- **D-04 honored:** recording buffer added to the EXISTING shared stub in-place — no second forked `.inc` file, single edit point per WR-06.
- **opt-IN (not opt-OUT) pattern:** flag absent = unchanged no-op. Existing suites that include this file without defining the flag compile identically to before.
- **Bound check before every store** (`if (s_bus_recording_count < HOST_STUBS_MAX_RECORDING)`) — T-71-02 mitigation per plan threat model. Firmware configure_* makes <20 register writes per init; overflow is not reachable in practice but the cap is defensive.

## Deviations from Plan

None — plan executed exactly as written. The recording buffer structure, API names, bound-check pattern, and banner comment all match the spec in 71-PATTERNS.md verbatim.

## Issues Encountered

None. No linker errors, no guard-ordering issues, no unexpected failures.

## Known Stubs

None. This plan only adds a test-infrastructure extension that activates when `HOST_STUBS_RECORD_BUS` is defined. No stub data flows to UI or production paths.

## Threat Flags

None. The only threat surface introduced is the recording buffer in the native test process (T-71-02), which is mitigated by the bound check. The production firmware flash byte-count is verified unchanged.

## Next Phase Readiness

- `host_stubs_common.inc` is ready for consumption by the per-family Tier-1 suites (Plans 71-02 through 71-06).
- Each new suite's `host_stubs.cpp` must `#define HOST_STUBS_RECORD_BUS` BEFORE `#include "../_shared/host_stubs_common.inc"` to activate the recording path.
- No new platform dependencies; existing `[env:native]` + Unity + ArduinoFake substrate is unchanged.
- Production builds are confirmed flash-byte-count stable (delta == 0).

## Self-Check

- [x] `firestarter/test/native/avr/_shared/host_stubs_common.inc` exists and contains `HOST_STUBS_RECORD_BUS`
- [x] Commit `f4e2040` exists in `firestarter/` submodule on `v1.13-algo-validation`
- [x] No new files created under `test/native/avr/_shared/`
- [x] Existing native suites: 30/30 tests PASSED (test_dispatch 15 + test_cobs 11 + test_read_timing 4)
- [x] Production flash unchanged: Uno 72.4%, Leonardo 88.9%

## Self-Check: PASSED

---
*Phase: 71-validation-harness-matrix*
*Completed: 2026-06-16*
