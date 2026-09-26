---
phase: 113-submission-flow
plan: 01
subsystem: reporting
tags: [python, dataclasses, hashlib, diagnostic-report, dedup]

# Dependency graph
requires:
  - phase: 110-diagnostic-report-model-dual-output-provenance-prompts
    provides: DiagnosticReport / AutoCapture / to_dict() single-source serialization
  - phase: 108-test-plan-engine-address-derived-pattern-fingerprint
    provides: StepResult.op/.verdict/.fingerprint.classification (Fingerprint four-bucket classifier)
provides:
  - "dedup_fingerprint(report) -> str module-level helper in diagnostic_report.py"
  - "to_dict()['dedup_fingerprint'] key, propagated automatically to render() and to_json_block()"
affects: [113-02, 113-03, 113-04, submit.py]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Module-level sibling helper pattern (mirrors is_submittable) for a report-derived pure function"
    - "to_dict() single-source field-add (no second field list in render()/to_json_block())"

key-files:
  created: []
  modified:
    - firestarter_app/firestarter/diagnostic_report.py
    - firestarter_app/tests/test_diagnostic_report.py

key-decisions:
  - "Canonical hash join is chip|protocol|per-step(op=verdict:classification), sha256 truncated to 12 hex chars (D-02, research Open Question 3)"
  - "dedup_fingerprint reads report.results directly (StepResult.op/.verdict/.fingerprint.classification), never report.to_dict()['steps'], to avoid a circular self-reference inside to_dict()"
  - "Non-destructive graceful degradation is a natural consequence of the design (fingerprint=None -> empty classification token), not a special-cased branch"

patterns-established:
  - "Dedup/identity helpers live as module-level siblings of is_submittable in diagnostic_report.py, not as DiagnosticReport methods"

requirements-completed: [SUB-03]

coverage:
  - id: D1
    description: "dedup_fingerprint(report) returns a deterministic 12-char lowercase hex hash, excluding all volatile fields (generated, host_version, measured vpp/vpe mV, error_code, reason)"
    requirement: "SUB-03"
    verification:
      - kind: unit
        ref: "tests/test_diagnostic_report.py#test_dedup_fingerprint_is_12_char_lowercase_hex"
        status: pass
      - kind: unit
        ref: "tests/test_diagnostic_report.py#test_dedup_fingerprint_deterministic_same_shape"
        status: pass
      - kind: unit
        ref: "tests/test_diagnostic_report.py#test_dedup_fingerprint_excludes_volatile_fields"
        status: pass
      - kind: unit
        ref: "tests/test_diagnostic_report.py#test_dedup_fingerprint_excludes_reason_and_error_code"
        status: pass
      - kind: unit
        ref: "tests/test_diagnostic_report.py#test_dedup_fingerprint_sensitive_to_verdict_change"
        status: pass
      - kind: unit
        ref: "tests/test_diagnostic_report.py#test_dedup_fingerprint_sensitive_to_classification_change"
        status: pass
      - kind: unit
        ref: "tests/test_diagnostic_report.py#test_dedup_fingerprint_non_destructive_graceful_degradation"
        status: pass
    human_judgment: false
  - id: D2
    description: "to_dict() carries 'dedup_fingerprint' from the single source; render() and to_json_block() inherit it automatically"
    requirement: "SUB-03"
    verification:
      - kind: unit
        ref: "tests/test_diagnostic_report.py#test_dedup_fingerprint_in_to_dict_single_source"
        status: pass
      - kind: unit
        ref: "tests/test_diagnostic_report.py#test_dedup_fingerprint_graceful_degradation_via_to_dict"
        status: pass
      - kind: unit
        ref: "tests/test_diagnostic_report.py#test_dedup_fingerprint_in_json_block"
        status: pass
    human_judgment: false

duration: 20min
completed: 2026-07-03
status: complete
---

# Phase 113 Plan 01: Dedup Fingerprint Summary

**Deterministic 12-char SHA-256-derived dedup id (chip + protocol + ordered step verdict/fingerprint shape) landed in `diagnostic_report.py`'s single-source `to_dict()`, so both renders and Plan 02's submission flow can read `dedup_fingerprint` for free.**

## Performance

- **Duration:** ~20 min
- **Completed:** 2026-07-03T16:57:23Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments
- `dedup_fingerprint(report) -> str` module-level helper added to `diagnostic_report.py` as a sibling of `is_submittable`: joins `AutoCapture.chip`/`.protocol` with each step's `op=verdict:classification` token, sha256-hashes the UTF-8 canonical string, truncates to 12 lowercase hex chars.
- Hash is proven deterministic across identical-shaped reports, proven to exclude every volatile field (`generated`, `host_version`, measured `vpp_before_mv`/`vpe_before_mv`, `error_code`, free-text `reason`), and proven sensitive to a verdict change or a fingerprint-classification change.
- Non-destructive runs (steps with no attached `Fingerprint`) gracefully collapse to chip + protocol + ordered verdicts and still hash stably.
- `to_dict()["dedup_fingerprint"]` added next to `is_submittable` — `render()` and `to_json_block()` inherit the field automatically with zero second field list, preserving the RPT-01 single-source invariant.

## Task Commits

Each task was committed atomically inside the `firestarter_app` submodule on branch `v1.21-community-chip-validation-command`:

1. **Task 1: dedup_fingerprint helper (deterministic, volatile-field-free)** - `0062e78` (feat)
2. **Task 2: wire dedup_fingerprint into to_dict() (single-source) + graceful degradation** - `1b7a47d` (feat)

_TDD tasks combined behavior+action per the plan's single-action wording; tests and implementation landed together in each commit (not split RED/GREEN commits) since the plan's `<action>` block specified both the helper and its tests as one deliverable per task._

## Files Created/Modified
- `firestarter_app/firestarter/diagnostic_report.py` - added `hashlib` import, `dedup_fingerprint(report) -> str` module-level helper, and the `"dedup_fingerprint"` key in `to_dict()`
- `firestarter_app/tests/test_diagnostic_report.py` - added a `_minimal_report()` test helper (direct `DiagnosticReport` construction with a `step_specs` list, for precise per-step control) and 10 `test_dedup_*` tests covering determinism, volatile exclusion, reason/error_code exclusion, verdict/classification sensitivity, graceful degradation, `to_dict()` single-source wiring, and `to_json_block()` propagation

## Decisions Made
- Canonical join order is `[chip, protocol] + ["{op}={verdict}:{cls}" for each step in order]`, joined with `"|"` — matches the plan's action block exactly (no deviation).
- `dedup_fingerprint` reads `report.results` (the `list[StepResult]`) directly rather than `report.to_dict()["steps"]`, avoiding a circular call back into `to_dict()` (which itself now calls `dedup_fingerprint(self)`).
- Placed `dedup_fingerprint` as a standalone module-level function directly after `is_submittable`, matching the plan's explicit "sibling" placement instruction.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None. `ruff format --check` flagged one pre-existing, out-of-scope formatting issue in `tests/test_validate_family_cmd.py` (not touched by this plan, not introduced by this work) — left untouched per the deviation-rules scope boundary.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- `dedup_fingerprint` is available on every `DiagnosticReport.to_dict()` output. Plan 02 (submission flow / `submit.py`) can read `report.to_dict()["dedup_fingerprint"]` directly for the issue title, per the plan's stated dependency.
- No blockers. `pytest tests/test_diagnostic_report.py -x` (24/24), `ruff check`/`ruff format --check` on `firestarter/` + `tests/`, and `tools/check_mypy_watermark.py` (1 error, 34 below the 35-error watermark) all green.

---
*Phase: 113-submission-flow*
*Completed: 2026-07-03*

## Self-Check: PASSED

- FOUND: commit 0062e78 (Task 1)
- FOUND: commit 1b7a47d (Task 2)
- FOUND: firestarter_app/firestarter/diagnostic_report.py
- FOUND: firestarter_app/tests/test_diagnostic_report.py
- FOUND: .planning/phases/113-submission-flow/113-01-SUMMARY.md
