---
phase: 111-measured-voltage-sampler-hardware-gated
plan: 02
subsystem: hardware
tags: [python, serial-protocol, voltage-sampling, regex, statistics]

# Dependency graph
requires:
  - phase: 111-01
    provides: Wave-0 RED sampler tests in tests/test_hardware.py + voltage-split RED test in tests/test_diagnostic_report.py
provides:
  - "HardwareManager._parse_voltage_frame(message) -> int|None (100 mV grid reconstruction from Response.message)"
  - "HardwareManager._sample_one_voltage(state, n=3, flags=0) -> int|None (bounded N-frame median sampler)"
  - "HardwareManager.sample_vpp_mv(n=3) / sample_vpe_mv(n=3) -> int|None (value-returning siblings of read_vpp_voltage/read_vpe_voltage)"
affects: [111-03, 112-dev-test-handler-wiring]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Pattern A: re-parse Response.message via tolerant regex instead of touching Response.payload (which is None for 0xE4/0xE5 voltage frames)"
    - "Additive-sibling method pairing: value-returning sample_*_mv() sits beside pre-existing bool-returning read_*_voltage(), sharing the connect/handshake shape without modifying it"
    - "Honest fallback: None on any transport/parse failure, never a fabricated 0"

key-files:
  created: []
  modified:
    - firestarter_app/firestarter/hardware.py

key-decisions:
  - "Used RESEARCH Pattern A (regex re-parse of Response.message) per plan's explicit directive -- Response.payload is None for 0xE4/0xE5 frames, so CONTEXT D-05's raw-payload premise is superseded"
  - "Placed _parse_voltage_frame/_sample_one_voltage/sample_vpp_mv/sample_vpe_mv strictly after _read_voltage_loop/read_vpp_voltage/read_vpe_voltage; zero lines changed in those three methods (SC3 verified via git diff)"
  - "flags=0 default confirmed correct per RESEARCH A3 -- firmware read path consults no flag"

patterns-established:
  - "Sampler methods return Optional[int] mV and never print; monitor methods remain untouched and print-only"

requirements-completed: [VOLT-01]

coverage:
  - id: D1
    description: "_parse_voltage_frame reconstructs mV as v_int*1000 + v_dec*100 from the 100 mV-grid wire string, returning None on no-match/garbage/absent message"
    requirement: "VOLT-01"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_hardware.py#test_parse_voltage_frame_reconstructs_mv"
        status: pass
    human_judgment: false
  - id: D2
    description: "_sample_one_voltage / sample_vpp_mv / sample_vpe_mv read N synthetic DATA frames and return the median mV, using the correct state (COMMAND_READ_VPP=11 / COMMAND_READ_VPE=12)"
    requirement: "VOLT-01"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_hardware.py#test_sample_vpp_mv_returns_median"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_hardware.py#test_sample_vpe_mv_uses_state_12"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_hardware.py#test_sample_median_of_even_n_off_grid"
        status: pass
    human_judgment: false
  - id: D3
    description: "Sampler returns None (never a fabricated 0) on transport error or an in-band ERROR frame instead of DATA"
    requirement: "VOLT-01"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_hardware.py#test_sample_none_returns_none_on_error"
        status: pass
    human_judgment: false
  - id: D4
    description: "_read_voltage_loop / read_vpp_voltage / read_vpe_voltage bodies remain byte-unchanged (SC3); pre-existing monitor regression tests still pass"
    requirement: "VOLT-01"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_hardware.py (full file, 12/12 pass including pre-existing read_vpp/vpe tests)"
        status: pass
      - kind: other
        ref: "git diff HEAD~2 HEAD -- firestarter/hardware.py shows zero removed/changed lines, purely additive"
        status: pass
    human_judgment: false

duration: 12min
completed: 2026-07-03
status: complete
---

# Phase 111 Plan 02: Measured-Voltage Sampler Implementation Summary

**Value-returning `sample_vpp_mv()`/`sample_vpe_mv()` on `HardwareManager` reconstruct median millivolt readings from 0xE4/0xE5 DATA frames by regexing `Response.message` (Pattern A), turning the print-only VPP/VPE monitor into a report-ready numeric value.**

## Performance

- **Duration:** 12 min
- **Started:** 2026-07-03T07:16:00Z (approx, per STATE.md session start)
- **Completed:** 2026-07-03T07:27:55Z
- **Tasks:** 2
- **Files modified:** 1 (`firestarter_app/firestarter/hardware.py`)

## Accomplishments
- Added `_parse_voltage_frame(message)` — tolerant `(\d+)\.(\d+)\s*V` regex reconstructs `v_int*1000 + v_dec*100` mV from `Response.message`; returns `None` (never `0`) on no-match/garbage/absent input.
- Added `_sample_one_voltage(state, n=3, flags=0)` — mirrors the `_read_voltage_loop` handshake (`find_and_connect` → `expect_ack` → `send_ack` → `get_response`) but bounded to `n` frames via `for _ in range(n)`, returning `int(statistics.median(samples))` or `None`.
- Added thin public wrappers `sample_vpp_mv(n=3)` / `sample_vpe_mv(n=3)` reusing the already-imported `COMMAND_READ_VPP`/`COMMAND_READ_VPE` constants — zero new command constants, zero new firmware dispatch entries.
- Turned all 5 of Plan-01's RED sampler tests in `test_hardware.py` GREEN, plus confirmed the pre-existing `test_voltage_format_pin` catalog-format-drift guard passes.
- Confirmed SC3 by construction and by `git diff`: `_read_voltage_loop`, `read_vpp_voltage`, `read_vpe_voltage` have zero changed lines; the full 12-test `test_hardware.py` suite (6 new sampler tests + 6 pre-existing monitor tests) is green.

## Task Commits

Each task was committed atomically inside the `firestarter_app` submodule:

1. **Task 1: Add `_parse_voltage_frame` + `_sample_one_voltage` to HardwareManager** - `61f7f9f` (feat)
2. **Task 2: Add `sample_vpp_mv`/`sample_vpe_mv` wrappers + confirm SC3 regression** - `aa36d0b` (feat)

_No TDD RED commits in this plan — the RED tests were committed in Plan 111-01; this plan is the GREEN half._

## Files Created/Modified
- `firestarter_app/firestarter/hardware.py` — added `_VOLTAGE_RE` module constant, `_parse_voltage_frame`, `_sample_one_voltage`, `sample_vpp_mv`, `sample_vpe_mv` on `HardwareManager`; added `import re` and `import statistics` to the module imports. All additions placed after the existing `_read_voltage_loop`/`read_vpp_voltage`/`read_vpe_voltage` methods, which are byte-unchanged.

## Decisions Made
- Followed RESEARCH Pattern A exactly (re-parse `Response.message`) per the plan's explicit override of CONTEXT §D-05 — `Response.payload` is `None` for 0xE4/0xE5 frames, so no raw-payload/`_decode_param` path was implemented. Verified via `grep -nE "Response\.payload|_decode_param" firestarter/hardware.py` returning no match.
- Kept `flags=0` as the sampler default (RESEARCH A3: the firmware voltage-read path consults no flag).
- Used `logger.debug` (not `logger.error`) inside the sampler's except-tuple, matching the plan's "silent — no `print`, no `logger.error` required" guidance, distinguishing it from the print-loop's louder `logger.error` handling.

## Deviations from Plan

None - plan executed exactly as written. Both tasks matched their `<action>` specifications precisely (method signatures, placement, error-tuple copied verbatim, regex pattern, median/int casting).

## Issues Encountered

None. Running the broader `firestarter_app` test suite (`pytest tests/ -q`, not part of this plan's required verification) surfaces 2 pre-existing failures unrelated to this plan's file:
- `tests/test_diagnostic_report.py::test_voltage_split_fields_serialize` — Plan 111-01's RED test for the voltage-split fields on `DiagnosticReport`; this is Plan 111-03's GREEN target (`diagnostic_report.py`), out of this plan's scope (`files_modified: firestarter_app/firestarter/hardware.py` only).
- `tests/test_audit_coverage_matrix.py::test_golden_file_matches` — a pre-existing golden-fixture drift unrelated to voltage sampling (see STATE.md Phase 104 history), untouched by this plan.

Neither failure involves `hardware.py`; `git diff --stat HEAD~2 HEAD` confirms only `firestarter/hardware.py` was modified across both task commits.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- `HardwareManager.sample_vpp_mv()`/`sample_vpe_mv()` are ready for Plan 111-03 to wire into `DiagnosticReport`'s voltage-split fields, and for Phase 112's orchestrator to call before/after the write step.
- No blockers. The live hardware-gated bench check (Leonardo + Rev 2.0) remains deferred per D-05 as originally scoped — this plan ships software-complete + synthetic-frame-tested.

---
*Phase: 111-measured-voltage-sampler-hardware-gated*
*Completed: 2026-07-03*

## Self-Check: PASSED
