---
phase: 110-diagnostic-report-model-dual-output-provenance-prompts
plan: 01
subsystem: testing
tags: [dataclass, rich, json, dual-render, diagnostic-report, python]

# Dependency graph
requires:
  - phase: 108-test-plan-engine-address-derived-pattern-fingerprint
    provides: Plan/StepResult/Fingerprint/BannerCounts dataclasses, derive_plan/run_plan/count_applicable
  - phase: 109-destructiveness-gate-safety
    provides: Plan.locked_destructive advisory field, BannerCounts N-of-M banner data
provides:
  - DiagnosticReport dataclass composing Phase-108/109 engine output
  - Single-source to_dict()/render()/to_json_block() dual-render contract (RPT-01)
  - AutoCapture sub-dataclass (RPT-02) with threaded-in fw_board_identity
  - TransportHealth sub-dataclass with NOT_MEASURED honest fallback (XPORT-01)
  - SCHEMA_VERSION single-sourced constant
affects: [112-dev-test-handler-wiring, 113-submission-flow]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Single-source dual-render: to_dict() is canonical, render() reads the same dict, to_json_block() serializes the same dict"
    - "Honest-fallback sentinel (NOT_MEASURED) substituted in exactly one place"
    - "AST-based structural scan (not raw substring grep) for orchestrator-only source checks"

key-files:
  created:
    - firestarter_app/firestarter/diagnostic_report.py
    - firestarter_app/tests/test_diagnostic_report.py
  modified: []

key-decisions:
  - "test_report_module_is_orchestrator_only rewritten from raw substring grep to AST-based import/literal scan, because the module's own docstrings describe the safety property in prose (e.g. 'imports no SerialCommunicator') and a substring check false-positives on that prose -- mirrors the Phase-109 SAFE-02 ast.walk lesson"
  - "Reworded diagnostic_report.py docstring prose to avoid the literal substrings 'SerialCommunicator'/'HardwareManager' so the plan's shell-grep verification command (which only excludes '#' comment lines, not docstrings) passes cleanly, without changing the documented meaning"
  - "DiagnosticReport, AutoCapture, and TransportHealth were all implemented in one file write (Tasks 2 and 3 land in a single diagnostic_report.py) because to_dict()/render() depend directly on AutoCapture/TransportHealth's shapes -- committed as two separate commits (constants+sub-dataclasses, then the aggregate) to preserve the plan's task-level commit granularity"

patterns-established:
  - "New host modules with a safety-invariant docstring should describe forbidden imports/tokens without spelling them as literal substrings, or their own structural-scan test/verification grep will false-positive on the docstring itself"

requirements-completed: [RPT-01, RPT-02, XPORT-01]

coverage:
  - id: D1
    description: "DiagnosticReport renders two ways (rich table + fenced JSON) from one to_dict() source; JSON carries schema_version"
    requirement: "RPT-01"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_diagnostic_report.py#test_dual_render_single_source"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_diagnostic_report.py#test_json_block_parseable"
        status: pass
    human_judgment: false
  - id: D2
    description: "AutoCapture surfaces host/fw-board/chip/protocol/chip-id fields; each step dict carries error_code + fingerprint classification"
    requirement: "RPT-02"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_diagnostic_report.py#test_auto_capture_fields"
        status: pass
    human_judgment: false
  - id: D3
    description: "Transport-health counters render NOT_MEASURED (never a false 0); transport_suspect is False when counters absent"
    requirement: "XPORT-01"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_diagnostic_report.py#test_transport_not_measured"
        status: pass
    human_judgment: false
  - id: D4
    description: "Module is orchestrator-only: no SerialCommunicator/HardwareManager import, no --force literal"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_diagnostic_report.py#test_report_module_is_orchestrator_only"
        status: pass
    human_judgment: false

duration: 25min
completed: 2026-07-02
status: complete
---

# Phase 110 Plan 1: Diagnostic Report Model Core Summary

**New `diagnostic_report.py` module: a single-source `DiagnosticReport` dataclass whose `render()` (rich table) and `to_json_block()` (fenced JSON) both read the same `to_dict()` mapping, plus `AutoCapture`/`TransportHealth` sub-objects with an honest `"not measured"` fallback for unreachable transport counters.**

## Performance

- **Duration:** ~25 min
- **Started:** 2026-07-02T21:06:17Z
- **Completed:** 2026-07-02T21:13:01Z
- **Tasks:** 3 (TDD RED → GREEN)
- **Files modified:** 2

## Accomplishments
- `DiagnosticReport` dataclass composing Phase-108/109 `Plan`/`StepResult`/`BannerCounts` output; `to_dict()` is the hand-written canonical mapping (never `dataclasses.asdict()` wholesale), baking in `SCHEMA_VERSION` and substituting `NOT_MEASURED` in exactly one place.
- `render()` builds a `rich.table.Table` by calling `self.to_dict()` and iterating that dict — never a second hand-maintained field list, never re-parsing the JSON string (RPT-01's single-source contract, test-verified via source inspection).
- `AutoCapture` receives `fw_board_identity` as threaded-in input (`str | None`), never fetches it — the module imports no `SerialCommunicator`/`HardwareManager` and opens no serial connection (SAFE-02, Pitfall 1).
- `TransportHealth` defaults every counter to `None`; `_is_transport_suspect()` can only trip `True` from a present-and-elevated counter, never from absence — matching the research finding that zero transport counters are reachable in the codebase today.
- Bench-free test suite (`tests/test_diagnostic_report.py`) reusing the `EpromDatabase(skip_local_override=True)` + `_mock_operator(**returns)` seam from `test_chip_test.py`, driving a real `derive_plan`/`run_plan` cycle so `results` carry genuine `StepResult.error_code`/`.fingerprint`.

## Task Commits

Each task was committed atomically:

1. **Task 1: Failing test scaffolds (RED)** - `92d97c1` (test)
2. **Task 2: Module constants + AutoCapture + TransportHealth** - `721cded` (feat)
3. **Task 3: DiagnosticReport aggregate + single-source render (GREEN)** - `f2d3ce5` (feat)

_Note: Task 3's commit also contains the structural-scan test rewrite (AST-based, see Deviations) since it was needed to reach a true GREEN state without a false-positive._

## Files Created/Modified
- `firestarter_app/firestarter/diagnostic_report.py` - New module: `SCHEMA_VERSION`/`NOT_MEASURED` constants, `AutoCapture`, `TransportHealth`, `_is_transport_suspect`, `DiagnosticReport` with `to_dict()`/`render()`/`to_json_block()`
- `firestarter_app/tests/test_diagnostic_report.py` - Bench-free unit tests: dual-render single-source, JSON round-trip, auto-capture fields, transport not-measured, orchestrator-only AST scan

## Decisions Made
- Rewrote `test_report_module_is_orchestrator_only` from a raw substring check to an AST-based import/string-literal scan. The module's own docstrings describe the SAFE-02 safety property in prose (e.g. "imports no SerialCommunicator") which a literal substring assertion flags as a false violation — the exact trap the state decisions warned about from Phase 109's `ast.walk` precedent. The AST scan checks only actual `import`/`from...import` statements and string-literal constants, which is what the safety property actually constrains.
- Reworded the module's docstring prose (module-level, `AutoCapture`, `TransportHealth`) to avoid the literal substrings `SerialCommunicator`/`HardwareManager` so the plan's own shell-grep verification command (`grep -vE '^\s*#' ... | grep -c -E 'SerialCommunicator|HardwareManager'` → must be 0) passes without weakening the pytest-level guard. Meaning is preserved (e.g. "serial-transport class" / "hardware-manager class").
- Implemented Task 2 (constants + sub-dataclasses) and Task 3 (aggregate + dual-render) in a single file creation since `DiagnosticReport.to_dict()` depends directly on `AutoCapture`/`TransportHealth` field shapes and cannot be meaningfully split mid-file; committed as two separate git commits to preserve per-task traceability, with Task 3's commit noting the additional test-file fix needed to reach GREEN.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Structural-scan test false-positived on its own module's safety-property docstring**
- **Found during:** Task 3 (GREEN verification run)
- **Issue:** The Task-1-authored `test_report_module_is_orchestrator_only` used a raw substring check (`"SerialCommunicator" not in src`) against the full module source via `inspect.getsource`. Once Task 2/3 added a module docstring correctly *describing* the SAFE-02 invariant ("imports no SerialCommunicator/HardwareManager"), the substring check flagged that prose as a violation — a false positive, not a real safety issue.
- **Fix:** Rewrote the test to parse the module's AST and check only `ast.Import`/`ast.ImportFrom` node names and string-literal `ast.Constant` values for the forbidden tokens, ignoring docstring/comment prose. Reworded the module's own docstrings to avoid the literal substrings as a belt-and-suspenders fix for the plan's separate shell-grep verification command.
- **Files modified:** firestarter_app/tests/test_diagnostic_report.py, firestarter_app/firestarter/diagnostic_report.py
- **Verification:** `pytest tests/test_diagnostic_report.py -x -q` green (5/5); `grep -vE '^\s*#' firestarter/diagnostic_report.py | grep -c -E 'SerialCommunicator|HardwareManager'` returns 0.
- **Committed in:** f2d3ce5 (Task 3 commit)

---

**Total deviations:** 1 auto-fixed (1 bug — Rule 1)
**Impact on plan:** Necessary correction to make the plan's own acceptance criteria internally consistent (a docstring correctly documenting a safety invariant should not itself trip that invariant's checker). No scope creep — same safety property, more precise checker.

## Issues Encountered
- Pre-existing `tests/test_audit_coverage_matrix.py::TestAuditCoverageMatrix::test_golden_file_matches` failure exists on this branch independent of this plan's changes (confirmed via `git stash` + re-run before any diagnostic_report.py code existed). Documented in STATE.md as a carry-forward from Phase 106-01 ("Logged pre-existing test_audit_coverage_matrix.py golden-fixture drift ... explicitly out of scope"). Not touched; full suite is green apart from this one pre-existing, unrelated failure.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- `DiagnosticReport`/`AutoCapture`/`TransportHealth` are ready for Plan 110-02 to add the `Provenance` sub-object + prompt component + `is_submittable` predicate, and Plan 110-03 to add the read-only `DbDiff` sub-object — both plans append new `to_dict()` keys and new `render()` rows without restructuring either method (the aggregate was deliberately shaped for this).
- `vpp_vpe_mv` slot is present and `None`; Phase 111's measured-voltage sampler fills it later.
- Phase 112's handler must capture `operator.comm.programmer_info` (or equivalent) at sweep start and thread it into `AutoCapture(fw_board_identity=...)` — this plan's module never fetches it itself (by design, SAFE-02/Pitfall 1).

---
*Phase: 110-diagnostic-report-model-dual-output-provenance-prompts*
*Completed: 2026-07-02*

## Self-Check: PASSED

- FOUND: firestarter_app/firestarter/diagnostic_report.py
- FOUND: firestarter_app/tests/test_diagnostic_report.py
- FOUND: .planning/phases/110-diagnostic-report-model-dual-output-provenance-prompts/110-01-SUMMARY.md
- FOUND commit (submodule v1.21-community-chip-validation-command branch): 92d97c1 (test RED)
- FOUND commit (submodule): 721cded (feat constants+sub-dataclasses)
- FOUND commit (submodule): f2d3ce5 (feat aggregate GREEN)
- FOUND commit (meta repo): 94ca3a7 (docs SUMMARY)
