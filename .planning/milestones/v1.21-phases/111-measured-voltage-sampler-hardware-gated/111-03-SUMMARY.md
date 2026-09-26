---
phase: 111-measured-voltage-sampler-hardware-gated
plan: 03
subsystem: diagnostics
tags: [python, dataclass, diagnostic-report, voltage, tdd]

# Dependency graph
requires:
  - phase: 111-01
    provides: "RED test test_voltage_split_fields_serialize in test_diagnostic_report.py asserting the split voltage field shapes"
  - phase: 111-02
    provides: "sample_vpp_mv/sample_vpe_mv wrappers on HardwareManager (VOLT-01 sampler half)"
provides:
  - "DiagnosticReport six-field voltage split: vpp_before_mv/vpp_after_mv/vpe_before_mv/vpe_after_mv (destructive) + vpp_mv/vpe_mv (standalone)"
  - "_voltage_dict() helper — single place NOT_MEASURED substitutes for an absent voltage reading"
  - "to_dict()['voltage'] nested sub-dict consumed by both render() and to_json_block()"
  - "render() voltage row sourced exclusively from to_dict()['voltage'] (single-source contract preserved)"
affects: [112-dev-test-handler-wiring]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Sentinel-substitution helper pattern (_voltage_dict mirrors _transport_dict) — one method per field-group owns NOT_MEASURED substitution, to_dict() only composes"

key-files:
  created: []
  modified:
    - firestarter_app/firestarter/diagnostic_report.py

key-decisions:
  - "Old combined vpp_vpe_mv slot fully removed (0 occurrences) rather than kept as a deprecated alias — the plan's negative-grep acceptance criterion and the D-01 split both require a clean removal"
  - "_voltage_dict modeled byte-for-byte on the existing _transport_dict pattern (six explicit NOT_MEASURED-if-None branches) rather than a generic loop, matching the file's established idiom over a DRY micro-optimization"
  - "Voltage render() row placed after banner, before provenance, as a single add_row with a compact one-line summary string — never a second per-field row list, preserving the single-source render contract (Phase 110 D-01)"

patterns-established:
  - "Voltage-field honest-fallback: absent readings always serialize to NOT_MEASURED, never a false 0 (D-04), following the same discipline already established for transport_health counters"

requirements-completed: [VOLT-01]

coverage:
  - id: D1
    description: "DiagnosticReport exposes six split voltage fields (destructive before/after per rail + standalone) instead of the single combined vpp_vpe_mv slot"
    requirement: "VOLT-01"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_diagnostic_report.py#test_voltage_split_fields_serialize"
        status: pass
    human_judgment: false
  - id: D2
    description: "Absent voltage readings always serialize to NOT_MEASURED, never a fabricated 0 (honest fallback)"
    requirement: "VOLT-01"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_diagnostic_report.py#test_voltage_split_fields_serialize"
        status: pass
    human_judgment: false
  - id: D3
    description: "render() sources the voltage row only from to_dict()['voltage'] — single-source contract (Phase 110 D-01) preserved, SAFE-02 orchestrator-only structural scan stays green"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_diagnostic_report.py#test_voltage_split_fields_serialize (part c) and #test_dual_render_single_source, #test_report_module_is_orchestrator_only"
        status: pass
    human_judgment: false

duration: 12min
completed: 2026-07-03
status: complete
---

# Phase 111 Plan 03: Voltage Field Split + Report Render Summary

**Split `DiagnosticReport`'s combined `vpp_vpe_mv` slot into six D-01/D-03/D-04 voltage fields (destructive before/after per rail + standalone), surfaced through a new `_voltage_dict()` helper and a single `render()` table row — turning the Plan-01 RED test GREEN.**

## Performance

- **Duration:** 12 min
- **Started:** 2026-07-03T07:29:30Z
- **Completed:** 2026-07-03T07:33:20Z
- **Tasks:** 2
- **Files modified:** 1

## Accomplishments
- Removed the single combined `vpp_vpe_mv: int | None` slot and replaced it with `vpp_before_mv`, `vpp_after_mv`, `vpe_before_mv`, `vpe_after_mv` (destructive-run before/after per rail) plus `vpp_mv`, `vpe_mv` (non-destructive standalone) — all `int | None = None`
- Added `_voltage_dict()`, modeled exactly on the existing `_transport_dict()` pattern, as the single place `NOT_MEASURED` substitutes for any `None` voltage field
- `to_dict()` now emits a nested `"voltage"` sub-dict via `_voltage_dict()`, replacing the old flat `vpp_vpe_mv` key
- Added exactly one `render()` table row reading `d["voltage"]` (placed after the banner row, before the provenance block) — no dataclass field is read directly inside `render()`
- Confirmed the module still imports no transport/hardware class and introduces no `--force` token (SAFE-02 stays green)

## Task Commits

Each task was committed atomically inside the `firestarter_app` submodule:

1. **Task 1: Split the combined slot into the D-01/D-03/D-04 field set + `_voltage_dict` helper** - `58b0670` (feat)
2. **Task 2: Render the voltage block + confirm single-source and SAFE-02 stay green** - `84c26cf` (feat)

_Note: this plan's two tasks are the GREEN half of a prior TDD RED (111-01 commit `1b591dc test(111-01): add Wave-0 RED voltage-split test`); no separate test-commit was created here since the RED test already exists and was not modified._

## Files Created/Modified
- `firestarter_app/firestarter/diagnostic_report.py` - Split `vpp_vpe_mv` into six voltage fields, added `_voltage_dict()`, updated `to_dict()`, added the `render()` voltage row

## Decisions Made
- Old combined `vpp_vpe_mv` slot fully removed (0 grep occurrences) rather than aliased — matches the plan's explicit deletion instruction and the negative-grep acceptance criterion
- `_voltage_dict()` mirrors `_transport_dict()`'s explicit per-field `NOT_MEASURED if ... is None else ...` idiom rather than a generic dict-comprehension loop, for consistency with the file's established pattern
- Single `render()` row summarizing all six voltage values in one compact string (`vpp before/after=... vpe before/after=... vpp=... vpe=...`), reading only from `d["voltage"]`, preserving the single-source render contract

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
None. The RED test (`test_voltage_split_fields_serialize`) failed as expected (`KeyError: 'voltage'`) before Task 1, turned partially green after Task 1 (parts a/b), and fully green after Task 2 (part c, the render single-source assertion).

## TDD Gate Compliance

RED gate: `1b591dc test(111-01): add Wave-0 RED voltage-split test to test_diagnostic_report.py` (prior plan, confirmed still failing at this plan's start: `KeyError: 'voltage'`).
GREEN gate: `58b0670 feat(111-03): split vpp_vpe_mv into D-01/D-03/D-04 voltage field set` + `84c26cf feat(111-03): render voltage row from to_dict()['voltage'] (single-source)`.
No REFACTOR commit needed — code required no post-GREEN cleanup.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- `DiagnosticReport` now has a place for Phase 112's orchestrator to land sampled `vpp_before_mv`/`vpp_after_mv`/`vpe_before_mv`/`vpe_after_mv` (destructive) or `vpp_mv`/`vpe_mv` (non-destructive) values around `run_plan`, using the `sample_vpp_mv`/`sample_vpe_mv` wrappers Plan 02 added to `HardwareManager`.
- Full `test_diagnostic_report.py` suite (16 tests) is green; `ruff check` and `ruff format --check` are clean on the modified file.
- No blockers for Phase 112.

---
*Phase: 111-measured-voltage-sampler-hardware-gated*
*Completed: 2026-07-03*

## Self-Check: PASSED

- FOUND: commit 58b0670 (feat(111-03): split vpp_vpe_mv into D-01/D-03/D-04 voltage field set)
- FOUND: commit 84c26cf (feat(111-03): render voltage row from to_dict()['voltage'] (single-source))
- FOUND: firestarter_app/firestarter/diagnostic_report.py
- FOUND: .planning/phases/111-measured-voltage-sampler-hardware-gated/111-03-SUMMARY.md
