---
phase: 111-measured-voltage-sampler-hardware-gated
plan: 01
subsystem: testing
tags: [tdd, pytest, hardware, voltage-sampler, diagnostic-report]

# Dependency graph
requires:
  - phase: 110-diagnostic-report-model-dual-output-provenance-prompts
    provides: DiagnosticReport dataclass with the vpp_vpe_mv placeholder slot and single-source to_dict()/render() contract
provides:
  - "Wave-0 RED test scaffold for the VOLT-01 measured-voltage sampler contract"
  - "Six named unit tests in test_hardware.py pinning _parse_voltage_frame/sample_vpp_mv/sample_vpe_mv semantics before implementation exists"
  - "One named test in test_diagnostic_report.py pinning the DiagnosticReport voltage-split (vpp/vpe before/after + standalone) serialization contract"
affects: [111-02-PLAN, 111-03-PLAN]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Bench-free sampler testing: conftest.build_frame(0xE4|0xE5, struct.pack(\">HHHH\", ...)) synthetic DATA frames fed to a patched find_and_connect() comm"
    - "Wave-0 RED-before-implementation scaffold: tests reference not-yet-existing production symbols and are expected to fail with AttributeError/KeyError, never stubbed to pass"

key-files:
  created: []
  modified:
    - firestarter_app/tests/test_hardware.py
    - firestarter_app/tests/test_diagnostic_report.py

key-decisions:
  - "Named the honest-fallback test test_sample_none_returns_none_on_error (not test_sample_returns_none_on_error) so the -k sample_none selector required by 111-VALIDATION.md actually matches"
  - "Asserted the render() single-source contract for the voltage split by scanning table.columns/cells for the rendered '20900' value rather than inspecting render() source text, since Plan 03 has not yet decided the exact voltage row wording"

patterns-established:
  - "RED-state test additions to a submodule are committed with `test(...)` type and documented as intentionally failing until named future plans land"

requirements-completed: [VOLT-01]

coverage:
  - id: D1
    description: "Six new unit tests pin the HardwareManager sampler contract (parse_voltage KAT, sample_vpp median, sample_vpe state-12 routing, honest None fallback, even-N median, format-string drift guard) — all bind to real not-yet-existing symbols and are RED except format_pin (which exercises an already-existing CATALOG regression guard)"
    requirement: VOLT-01
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_hardware.py::test_parse_voltage_frame_reconstructs_mv (collects, RED/AttributeError)"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_hardware.py::test_sample_vpp_mv_returns_median (collects, RED/AttributeError)"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_hardware.py::test_sample_vpe_mv_uses_state_12 (collects, RED/AttributeError)"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_hardware.py::test_sample_none_returns_none_on_error (collects, RED/AttributeError)"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_hardware.py::test_sample_median_of_even_n_off_grid (collects, RED/AttributeError)"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_hardware.py::test_voltage_format_pin (collects, GREEN today — pins existing CATALOG format strings)"
        status: pass
    human_judgment: false
  - id: D2
    description: "New DiagnosticReport voltage-split serialization test pins the destructive before/after shape, the standalone vpp_mv/vpe_mv shape, and the render()-sources-from-to_dict() single-source contract, all with NOT_MEASURED honest fallback"
    requirement: VOLT-01
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_diagnostic_report.py::test_voltage_split_fields_serialize (collects, RED/KeyError on to_dict()['voltage'])"
        status: pass
    human_judgment: false

duration: 20min
completed: 2026-07-03
status: complete
---

# Phase 111 Plan 01: Wave-0 RED Sampler Test Scaffold Summary

**Seven named pytest functions across test_hardware.py and test_diagnostic_report.py pin the VOLT-01 measured-voltage sampler contract (units, median, state routing, honest-fallback, format-drift guard, and report voltage-split) as intentional RED state ahead of Plans 02/03's implementation.**

## Performance

- **Duration:** 20 min
- **Started:** 2026-07-03T07:11:57Z
- **Completed:** 2026-07-03T07:19:03Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments
- Six new unit tests in `firestarter_app/tests/test_hardware.py` covering every VOLT-01 sampler behavior from 111-VALIDATION.md: KAT unit reconstruction (`_parse_voltage_frame`), median-of-N sampling (`sample_vpp_mv`), state-12 VPE routing (`sample_vpe_mv`), honest `None` fallback on transport error and in-band `ERROR` frames, even-N off-grid median rounding, and a format-string drift guard against the `0xE4`/`0xE5` `CATALOG` entries.
- One new unit test in `firestarter_app/tests/test_diagnostic_report.py` (`test_voltage_split_fields_serialize`) pinning the D-01 voltage-split contract: destructive-run before/after pairs, non-destructive standalone `vpp_mv`/`vpe_mv`, `NOT_MEASURED` honest fallback for absent readings in both shapes, and a single-source assertion that `render()` reflects the same `to_dict()["voltage"]` data.
- Confirmed the full seven-test set collects with zero collection errors and that six of seven are genuinely RED (bind to real not-yet-existing production symbols/keys — `AttributeError` on `HardwareManager._parse_voltage_frame`/`sample_vpp_mv`/`sample_vpe_mv`, `KeyError` on `to_dict()["voltage"]`); the seventh (`format_pin`) correctly passes today since it exercises the already-existing `CATALOG` format strings as a drift guard, not a not-yet-existing symbol.
- Verified `git diff --stat` on both files shows additions only; all pre-existing tests (including the SC3 `read_vpp_voltage`/`read_vpe_voltage` regression set) remain byte-identical and green.

## Task Commits

Each task was committed atomically inside the `firestarter_app` submodule (branch `v1.21-community-chip-validation-command`):

1. **Task 1: Wave-0 sampler unit-test scaffold in test_hardware.py** - `510a699` (test)
2. **Task 2: Wave-0 report voltage-split test scaffold in test_diagnostic_report.py** - `1b591dc` (test)

_No production code was touched; no plan-metadata commit was made in the submodule (SUMMARY.md lives in the meta-repo only, per this plan's routing instructions)._

## Files Created/Modified
- `firestarter_app/tests/test_hardware.py` - Added 6 new sampler tests (parse_voltage, sample_vpp, sample_vpe, sample_none, median, format_pin) + `re`/`struct`/`COMMAND_READ_VPE`/`build_frame` imports; no existing test body changed.
- `firestarter_app/tests/test_diagnostic_report.py` - Added `test_voltage_split_fields_serialize` covering the voltage-split serialization + single-source render contract; no existing test body changed.

## Decisions Made
- Named the honest-fallback test `test_sample_none_returns_none_on_error` (not the initially-drafted `test_sample_returns_none_on_error`) so the plan's required `-k sample_none` selector (111-VALIDATION.md row) actually matches it — verified via `--co -q -v` before committing.
- For the render() single-source assertion in the voltage-split test, scanned the rendered `rich.Table`'s `columns`/`cells` for the expected `"20900"` value rather than asserting on `render()`'s source text (as `test_dual_render_single_source` does for the steps contract) — Plan 03 has not yet decided the exact voltage row wording/key names, so asserting on rendered *content* is the more robust RED-to-GREEN pin without over-constraining Plan 03's implementation choice.

## Deviations from Plan

None - plan executed exactly as written. Both tasks matched their specified action/verify/acceptance criteria with no Rule 1-4 fixes needed to production code (none was touched, per the plan's explicit instruction).

## Issues Encountered

**Ruff formatting on new code:** the render()-inspection list comprehension in `test_voltage_split_fields_serialize` initially spanned multiple lines and `ruff format --check` wanted it collapsed to one line; reformatted before committing (no functional change).

**Pre-existing latent ruff F841 unmasked (out of scope, not fixed):** `firestarter_app/tests/test_diagnostic_report.py:519` (`table = report.render()  # must not raise`, inside the pre-existing `test_full_report_all_four_sub_objects_single_source`) is flagged as an unused-variable by `ruff check` once new code follows it in the file — it appears ruff does not flag an assigned-but-unused variable when it is the very last statement in the module, and my addition after it in the same file exposed the pre-existing issue. This line is untouched by my diff (`git diff` confirms only additions after it) and modifying an existing test's body was explicitly out of scope for this plan (no existing test may be modified). Logged to `deferred-items.md` in the phase directory rather than fixed, per the scope-boundary rule (only auto-fix issues directly caused by this plan's changes).

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Plan 02 can now implement `HardwareManager._parse_voltage_frame` / `_sample_one_voltage` / `sample_vpp_mv` / `sample_vpe_mv` against a pinned, already-collecting RED test suite (`pytest tests/test_hardware.py -k "parse_voltage or sample_vpp or sample_vpe or sample_none or median" -x` currently fails with `AttributeError` on the missing symbols — the expected GREEN target).
- Plan 03 can implement the `DiagnosticReport` voltage-split fields (`vpp_before_mv`/`vpp_after_mv`/`vpe_before_mv`/`vpe_after_mv`/`vpp_mv`/`vpe_mv`) and the nested `to_dict()["voltage"]` sub-dict against `test_voltage_split_fields_serialize` (currently `KeyError: 'voltage'` — the expected GREEN target), replacing the current `vpp_vpe_mv` slot.
- No blockers. The submodule remains on `v1.21-community-chip-validation-command`, forked off `v1.20` per the milestone's branch-base decision; both new commits are local to that branch.

---
*Phase: 111-measured-voltage-sampler-hardware-gated*
*Completed: 2026-07-03*

## Self-Check: PASSED

- FOUND: `.planning/phases/111-measured-voltage-sampler-hardware-gated/111-01-SUMMARY.md`
- FOUND: `.planning/phases/111-measured-voltage-sampler-hardware-gated/deferred-items.md`
- FOUND (submodule `firestarter_app` git log): `510a699` (Task 1 commit)
- FOUND (submodule `firestarter_app` git log): `1b591dc` (Task 2 commit)
