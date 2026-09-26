---
phase: 110-diagnostic-report-model-dual-output-provenance-prompts
plan: 02
subsystem: testing
tags: [dataclass, rich-prompt, provenance, injectable-seam, diagnostic-report, python]

# Dependency graph
requires:
  - phase: 110-diagnostic-report-model-dual-output-provenance-prompts (plan 01)
    provides: DiagnosticReport aggregate, single-source to_dict()/render()/to_json_block() contract, SCHEMA_VERSION/NOT_MEASURED constants
provides:
  - Provenance dataclass (shield_rev, chip_origin, owns_eraser, pot_touched, pot_note)
  - SHIELD_REV_CHOICES enumerated + community-tolerant list ("other"/"not sure" escapes)
  - prompt_provenance(is_uv, *, ask, confirm) injectable prompt component (RPT-04)
  - is_submittable(p) predicate ("not sure" = filled; blank/None required field = not submittable)
  - Provenance composed into DiagnosticReport.to_dict()/render() (append-only, single-source preserved)
affects: [112-dev-test-handler-wiring, 113-submission-flow]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Injectable ask/confirm callables (default to rich.prompt.Prompt.ask/Confirm.ask) so a prompt-collecting function is unit-testable via Mock(side_effect=[...]) without a TTY"
    - "Conditional prompt fields (owns_eraser only when is_uv, pot_note only when pot_touched) driven by plain caller-supplied booleans, never internally derived from hardware state"
    - "Append-only to_dict()/render() extension: new provenance section + derived is_submittable key added without restructuring plan-01's existing keys"

key-files:
  created:
    - firestarter_app/tests/test_provenance.py
  modified:
    - firestarter_app/firestarter/diagnostic_report.py
    - firestarter_app/tests/test_diagnostic_report.py

key-decisions:
  - "is_submittable's boolean expression line exceeded ruff's line-length after being written across two lines by hand; ran `ruff format` on diagnostic_report.py after each implementation task rather than hand-wrapping, so formatting stayed byte-identical to what CI's ruff format --check expects"
  - "The provenance rows in render() are five separate table.add_row() calls (one per field) rather than one combined string, mirroring the existing per-field rows for auto_capture (host_version/fw_board_identity/protocol are already separate rows) rather than the single combined-string style used for transport_health/banner -- kept consistent with the more granular precedent since each provenance field is independently actionable triage data"
  - "is_submittable is called from inside DiagnosticReport.to_dict() (imported at module scope, not re-implemented) -- to_dict() derives the is_submittable key by calling the standalone predicate directly on self.provenance, so there is exactly one implementation of the submittability rule (D-05) shared by both the standalone caller (Phase 112, before the sweep) and the report's own dict"

patterns-established:
  - "Prompt-collecting functions in this module take ask/confirm as keyword-only parameters defaulting to the real rich.prompt callables, never invoked at import time -- any future prompt component in diagnostic_report.py should follow the same injectable-seam shape"

requirements-completed: [RPT-04]

coverage:
  - id: D1
    description: "prompt_provenance() collects shield revision, chip origin, UV-eraser (only when is_uv), and pot-touched+note through injectable ask/confirm callables that never touch a TTY"
    requirement: "RPT-04"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_provenance.py#test_provenance_submittable"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_provenance.py#test_uv_eraser_prompt_only_when_uv"
        status: pass
    human_judgment: false
  - id: D2
    description: "'not sure' is a filled/submittable shield-revision answer; only a truly blank/None required field fails is_submittable"
    requirement: "RPT-04"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_provenance.py#test_not_sure_is_submittable"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_provenance.py#test_blank_shield_not_submittable"
        status: pass
    human_judgment: false
  - id: D3
    description: "Shield revision is never auto-derived from a hardware-revision byte; module reads no hw_revision and imports no HardwareManager/SerialCommunicator"
    requirement: "RPT-04"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_provenance.py#test_shield_rev_not_autoderived"
        status: pass
    human_judgment: false
  - id: D4
    description: "Provenance is composed into DiagnosticReport and surfaces in both to_dict() and render() from the same single-source accessors; is_submittable flips on a blank required field"
    requirement: "RPT-04"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_diagnostic_report.py#test_report_with_provenance_surfaces_in_both_renders"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_diagnostic_report.py#test_report_provenance_blank_field_flips_is_submittable"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_diagnostic_report.py#test_report_without_provenance_dict_is_null"
        status: pass
    human_judgment: false

duration: 20min
completed: 2026-07-02
status: complete
---

# Phase 110 Plan 2: Provenance Model + Injectable Prompt Component Summary

**`Provenance` dataclass + `prompt_provenance()` (injectable `rich.prompt` component) + `is_submittable()` predicate added to `diagnostic_report.py`, composed into `DiagnosticReport`'s existing single-source `to_dict()`/`render()` without restructuring plan-01's contract.**

## Performance

- **Duration:** ~20 min
- **Started:** 2026-07-02T21:15:00Z
- **Completed:** 2026-07-02T21:22:46Z
- **Tasks:** 3 (TDD RED → GREEN per task)
- **Files modified:** 3 (2 test files, 1 source module)

## Accomplishments
- `SHIELD_REV_CHOICES` (community-tolerant enumerated list with `"other"` free-text escape and explicit `"not sure"`) and the `Provenance` dataclass (`shield_rev`, `chip_origin`, `owns_eraser`, `pot_touched`, `pot_note`), every field defaulting blank/`None`.
- `prompt_provenance(is_uv, *, ask=Prompt.ask, confirm=Confirm.ask) -> Provenance` — collects provenance BEFORE the sweep via injectable callables mirroring `firmware.py`'s `Confirm.ask(..., default=...)` style; `"other"` triggers a free-text follow-up (blank follow-up stays `""`, never silently becomes `"other"`); `owns_eraser` asked only when `is_uv`; `pot_note` asked only when `pot_touched`.
- `is_submittable(p)` — `True` iff `shield_rev` and `chip_origin` are non-blank and `pot_touched is not None`; `"not sure"` counts as filled (D-05), `""`/`None` on a required field fails.
- `Provenance` composed into `DiagnosticReport`: `to_dict()` appends a `"provenance"` key (or `None`) and a derived `"is_submittable"` boolean key; `render()` reads that same dict to add five provenance rows plus an `is_submittable` row — no restructuring of plan-01's existing keys, no second field list, no re-parsing of the JSON string.
- Structural test (`test_shield_rev_not_autoderived`) asserts the module source contains no `"hw_revision"` substring and imports neither `HardwareManager` nor `SerialCommunicator` — enforced both at the pytest level and via the plan's shell-grep verification command (both return 0/clean).

## Task Commits

Each task was committed atomically (submodule `v1.21-community-chip-validation-command` branch):

1. **Task 1: Failing tests for the injectable provenance seam (RED)** - `2e05918` (test)
2. **Task 2: Provenance dataclass + prompt_provenance + is_submittable (GREEN)** - `fb49e02` (feat)
3. **Task 3a: Failing tests for Provenance composition into DiagnosticReport (RED)** - `3aa9752` (test)
3. **Task 3b: Compose Provenance into DiagnosticReport, single-source preserved (GREEN)** - `ad197f3` (feat)

**Plan metadata:** committed separately in the meta repo (see below).

## Files Created/Modified
- `firestarter_app/tests/test_provenance.py` - New bench-free test file: injectable ask/confirm seam, "not sure"/blank submittability, UV-eraser-only-when-UV conditional, structural no-auto-derive scan.
- `firestarter_app/firestarter/diagnostic_report.py` - Added `from rich.prompt import Confirm, Prompt`; `SHIELD_REV_CHOICES`; `Provenance` dataclass; `prompt_provenance()`; `is_submittable()`; `DiagnosticReport.provenance` field; `_provenance_dict()` helper; `to_dict()` gains `"provenance"`/`"is_submittable"` keys; `render()` gains provenance + is_submittable rows.
- `firestarter_app/tests/test_diagnostic_report.py` - Added three tests proving the provenance section surfaces in both renders from the same `to_dict()` source, and that a blank required field flips `is_submittable` to `False`.

## Decisions Made
- Ran `ruff format` on `diagnostic_report.py` after each implementation task rather than hand-wrapping long lines, keeping formatting byte-identical to what CI's `ruff format --check` expects (the `is_submittable` boolean expression and the `render()` provenance block both needed a pass).
- Kept provenance rows in `render()` as five separate `table.add_row()` calls (per-field), matching the existing per-field style used for `auto_capture` rows rather than the combined-string style used for `transport_health`/`banner`, since each provenance field is independently actionable triage data for a human reviewer.
- `to_dict()` calls the standalone `is_submittable()` predicate directly (imported at module scope) rather than reimplementing the rule inline, so there is exactly one submittability implementation shared by the report's own dict and any future direct caller (Phase 112, before the sweep).

## Deviations from Plan

None - plan executed exactly as written. All `must_haves` (injectable seam, "not sure" = filled, no hw_revision auto-derive, single-source composition) were implemented as specified; no architectural changes, no missing-critical-functionality gaps, no blocking issues beyond routine `ruff format` line-wrapping.

## Issues Encountered
- Pre-existing `tests/test_audit_coverage_matrix.py::TestAuditCoverageMatrix::test_golden_file_matches` failure remains on this branch, independent of this plan's changes (same carry-forward documented in the 110-01 SUMMARY and STATE.md, originating from Phase 106-01). Not touched; full suite (`pytest tests/ -q`) is green apart from this one pre-existing, unrelated failure.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- `Provenance`/`prompt_provenance`/`is_submittable` are ready for Phase 112 to invoke `prompt_provenance()` before the sweep and check `is_submittable()` before offering `--submit`; this plan built the model/component/predicate only (D-04) and does not wire the invocation.
- `DiagnosticReport.to_dict()`/`render()` remain structured for append-only extension — Plan 110-03's `db_diff` sub-object can add its own key/rows the same way, without restructuring the `provenance` or plan-01 keys.
- `owns_eraser` staying `None` for non-UV chips and the `is_uv` boolean itself are both caller-supplied inputs (per `chip_test.py`'s UV-EPROM detection via `electrical-type == "UV-EPROM"` OR `algorithm == 0x0B`) — Phase 112's handler is responsible for deriving `is_uv` before calling `prompt_provenance`.

---
*Phase: 110-diagnostic-report-model-dual-output-provenance-prompts*
*Completed: 2026-07-02*

## Self-Check: PASSED

- FOUND: firestarter_app/tests/test_provenance.py
- FOUND: firestarter_app/firestarter/diagnostic_report.py
- FOUND: .planning/phases/110-diagnostic-report-model-dual-output-provenance-prompts/110-02-SUMMARY.md
- FOUND commit (submodule v1.21-community-chip-validation-command branch): 2e05918 (test RED, injectable seam)
- FOUND commit (submodule): fb49e02 (feat GREEN, Provenance model + prompt_provenance + is_submittable)
- FOUND commit (submodule): 3aa9752 (test RED, composition into DiagnosticReport)
- FOUND commit (submodule): ad197f3 (feat GREEN, composition into DiagnosticReport)
- FOUND commit (meta repo): dcfbbd0 (docs SUMMARY)
