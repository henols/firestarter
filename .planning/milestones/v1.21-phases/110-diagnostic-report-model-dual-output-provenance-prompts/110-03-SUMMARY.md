---
phase: 110-diagnostic-report-model-dual-output-provenance-prompts
plan: 03
subsystem: testing
tags: [dataclass, read-only-transform, mock-spec, structural-scan, diagnostic-report, python]

# Dependency graph
requires:
  - phase: 110-diagnostic-report-model-dual-output-provenance-prompts (plans 01, 02)
    provides: DiagnosticReport aggregate, single-source to_dict()/render()/to_json_block() contract, SCHEMA_VERSION/NOT_MEASURED constants, Provenance model
provides:
  - DbDiff dataclass (current_support_status, proposed_disposition)
  - build_db_diff(name, db, results) -- read-only advisory transform (RPT-05)
  - Verdict-to-advisory-string mapping (BAD -> community-fail, PASS-only -> candidate, marginal/indeterminate -> inconclusive N>=2, else no-change)
  - DbDiff composed into DiagnosticReport.to_dict()/render() (append-only, single-source preserved)
  - Read-only-by-construction proof: write-method-less Mock DB + AST/regex structural no-write scan
affects: [112-dev-test-handler-wiring, 113-submission-flow, 114-support-status-taxonomy]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Write-method-less Mock(spec=[...]) DB proves read-only by construction: the mock exposes ONLY read methods, so any accidental write call raises AttributeError rather than silently succeeding"
    - "Positional dataclass construction (DbDiff(current, proposed)) instead of keyword args, to avoid a field name whose text CONTAINS the audited token (current_support_status) tripping the plan's own substring-based grep verification gate"
    - "Advisory descriptive-text constants (module-level _DISPOSITION_* strings) rather than inline strings, so the verdict-to-text mapping is a single readable dispatch table"

key-files:
  created: []
  modified:
    - firestarter_app/firestarter/diagnostic_report.py
    - firestarter_app/tests/test_diagnostic_report.py

key-decisions:
  - "The plan's literal verification grep (`grep -c -E 'support_status[[:space:]]*=|...'`) is substring-based, not word-boundary-aware, so it originally false-flagged the legitimate `current_support_status=current` keyword argument used to construct DbDiff. Fixed by switching to positional construction (`DbDiff(current, proposed)`) rather than renaming the plan-specified `current_support_status` field -- the field name is locked by the plan's `<artifacts_this_phase_produces>` spec, so the call-site shape was adjusted instead of the field name."
  - "The test file's own structural scan (test_module_never_writes_support_status) needed a more precise regex than the plan's shell-grep companion: `(?<![a-zA-Z0-9_])support_status\\s*(?<!=)=(?!=)\\s*\\S` requires a non-identifier character immediately before `support_status` so it does not false-positive on `current_support_status=...` or the `current_support_status: str = ...` dataclass field declaration, while still catching a genuine bare `support_status = ...` write."
  - "build_db_diff's verdict-mapping checks `if 'BAD' in verdicts` first (highest-severity signal wins even alongside other verdicts), then `marginal`/indeterminate-fingerprint (inconclusive), then a strict OK-plus-subset-of-{OK,NA,SKIPPED} check for the PASS-only candidate branch, else the neutral no-change fallback -- mirroring the plan's exact ordering guidance in <artifacts_this_phase_produces>."

patterns-established:
  - "Any future read-only DB transform in this module should follow the same write-method-less Mock(spec=[...]) proof pattern established here for build_db_diff, rather than asserting 'no write happened' via a weaker mechanism (e.g. mock call-count checks alone)."

requirements-completed: [RPT-05]

coverage:
  - id: D1
    description: "build_db_diff reads the chip's current support_status read-only via db.get_eprom_config(name)[0], defensively handling a None/absent config"
    requirement: "RPT-05"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_diagnostic_report.py#test_db_diff_readonly"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_diagnostic_report.py#test_db_diff_real_db_read"
        status: pass
    human_judgment: false
  - id: D2
    description: "proposed_disposition is advisory descriptive text derived purely from sweep verdicts (BAD -> community-fail signal, PASS-only -> candidate for community-reported, marginal/indeterminate -> inconclusive needs N>=2), never a concrete support_status value"
    requirement: "RPT-05"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_diagnostic_report.py#test_db_diff_verdict_mapping"
        status: pass
    human_judgment: false
  - id: D3
    description: "The DB-diff is read-only by construction: a write-method-less Mock DB proves no write is attempted, and the module contains no support_status assignment / .write / set_* call"
    requirement: "RPT-05"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_diagnostic_report.py#test_db_diff_readonly"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_diagnostic_report.py#test_module_never_writes_support_status"
        status: pass
    human_judgment: false
  - id: D4
    description: "DbDiff is composed into DiagnosticReport and surfaces through the same single-source to_dict()/render() from plans 01/02 (RPT-01 contract preserved); the full report demonstrates all four sub-objects in one to_dict() and one render() from a single source"
    requirement: "RPT-05"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_diagnostic_report.py#test_report_composes_db_diff_from_single_source"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_diagnostic_report.py#test_report_without_db_diff_is_null"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_diagnostic_report.py#test_full_report_all_four_sub_objects_single_source"
        status: pass
    human_judgment: false

duration: 25min
completed: 2026-07-02
status: complete
---

# Phase 110 Plan 3: Read-Only Advisory DB-Diff Summary

**`DbDiff` dataclass + `build_db_diff()` read-only transform added to `diagnostic_report.py`, composed into `DiagnosticReport`'s single-source `to_dict()`/`render()`, proven read-only-by-construction with a write-method-less Mock DB and a structural no-write scan.**

## Performance

- **Duration:** ~25 min
- **Started:** 2026-07-02T21:29:00Z
- **Completed:** 2026-07-02T21:37:49Z
- **Tasks:** 3 (TDD RED -> GREEN per task)
- **Files modified:** 2 (1 test file, 1 source module)

## Accomplishments
- `DbDiff` dataclass (`current_support_status: str = "supported"`, `proposed_disposition: str = ""`) — a plainly-advisory, read-only sub-object.
- `build_db_diff(name, db, results) -> DbDiff` — reads `support_status` via `db.get_eprom_config(name)[0]` (mirroring the exact `chip_resolver.py:54` read site, `.get("support_status", "supported")` with defensive `None`-config handling), and maps `{r.verdict for r in results}` (+ any StepResult `fingerprint.classification == "indeterminate"`) to one of four ADVISORY descriptive-text strings: any `BAD` -> `"suggests: community-fail signal (advisory -- human triage required)"`; `marginal`/indeterminate -> `"inconclusive -- needs N>=2 agreement (advisory)"`; PASS-only (`OK` plus a subset of `{OK, NA, SKIPPED}`) -> `"suggests: candidate for community-reported (advisory)"`; otherwise -> `"no change suggested (advisory)"`. Never writes any `support_status` field.
- `DbDiff` composed into `DiagnosticReport`: `to_dict()` appends a `"db_diff"` key (`current_support_status` + `proposed_disposition`, or `null` when `db_diff` is `None`); `render()` reads that same dict to add two `db_diff` rows — no restructuring of plan-01/02's existing keys, no second field list, no re-parsing of the JSON string.
- Read-only proven BY CONSTRUCTION: `test_db_diff_readonly` drives `build_db_diff` against a `Mock(spec=["get_eprom", "get_eprom_config", "convert_to_programmer"])` — a spec with NO write/set method at all — so any accidental write attempt would raise `AttributeError`. `test_module_never_writes_support_status` additionally asserts the module source contains no bare `support_status = ...` assignment, no `.write(`, and no `set_*(` call via a word-boundary-aware regex (precise enough to not false-positive on the legitimate `current_support_status` field/kwarg name).
- End-to-end phase-gate test (`test_full_report_all_four_sub_objects_single_source`) assembles a full `DiagnosticReport` with `auto_capture` + `provenance` + `transport` + `db_diff` + real plan/results/banner and asserts all four sub-object sections appear in one `to_dict()`, the JSON round-trips via `json.loads`, and `render()` returns a rich `Table` without raising.

## Task Commits

Each task was committed atomically (submodule `v1.21-community-chip-validation-command` branch):

1. **Task 1: Failing tests for read-only DB-diff, verdict-mapping, no-write proof (RED)** - `90a65ad` (test)
2. **Task 2: DbDiff dataclass + read-only build_db_diff verdict-mapping transform (GREEN)** - `0788ffc` (feat)
3. **Task 3a: Failing end-to-end test for DbDiff composed into DiagnosticReport (RED)** - `21ff05e` (test)
3. **Task 3b: Compose DbDiff into DiagnosticReport, single-source preserved (GREEN)** - `8a38f13` (feat)

**Plan metadata:** committed separately in the meta repo (see below).

## Files Created/Modified
- `firestarter_app/firestarter/diagnostic_report.py` - Added `DbDiff` dataclass, `_DISPOSITION_*` advisory-string constants, `build_db_diff()` read-only transform; `DiagnosticReport.db_diff` field; `_db_diff_dict()` helper; `to_dict()` gains a `"db_diff"` key; `render()` gains two `db_diff` rows (or a "not computed" fallback row).
- `firestarter_app/tests/test_diagnostic_report.py` - Added seven tests: `test_db_diff_readonly`, `test_db_diff_verdict_mapping`, `test_db_diff_real_db_read`, `test_module_never_writes_support_status`, `test_report_composes_db_diff_from_single_source`, `test_report_without_db_diff_is_null`, `test_full_report_all_four_sub_objects_single_source` (phase-gate e2e).

## Decisions Made
- The plan's literal verification grep (`grep -c -E 'support_status[[:space:]]*=|...'` — a substring match, not word-boundary-aware) initially false-flagged the legitimate keyword construction `DbDiff(current_support_status=current, ...)` because `current_support_status=` textually contains `support_status=`. Rather than rename the plan-specified `current_support_status` field (locked by `<artifacts_this_phase_produces>`), switched `build_db_diff`'s return statement to positional construction (`DbDiff(current, proposed)`), which sidesteps the substring collision entirely while keeping the field name and dataclass shape exactly as specified. Verified the plan's own grep command now returns 0.
- Wrote a more precise structural-scan regex in the test (`(?<![a-zA-Z0-9_])support_status\s*(?<!=)=(?!=)\s*\S`) than the plan's shell-grep companion, requiring a non-identifier boundary before `support_status` so the test does not false-positive on `current_support_status=...` (kwarg) or `current_support_status: str = ...` (dataclass field declaration) while still catching a genuine bare `support_status = ...` write.
- Verdict-mapping precedence in `build_db_diff`: `BAD` (highest severity, checked first regardless of what else is present) -> `marginal`/indeterminate-fingerprint (inconclusive) -> strict PASS-only subset check (candidate) -> no-change fallback, matching the exact ordering implied by the plan's mapping table.

## Deviations from Plan

None architecturally - plan executed exactly as written (`DbDiff`, `build_db_diff`, composition into `DiagnosticReport`, all `must_haves` satisfied). One minor implementation-detail adjustment (Rule 3 - blocking, self-resolved): the DbDiff construction call site uses positional args instead of keyword args to avoid a false-positive on the plan's own literal grep verification command, as documented in Decisions Made above. No architectural change, no missing-critical-functionality gap.

## Issues Encountered
- Pre-existing `tests/test_audit_coverage_matrix.py::TestAuditCoverageMatrix::test_golden_file_matches` failure remains on this branch, independent of this plan's changes (same carry-forward documented in the 110-01 and 110-02 SUMMARYs, originating from Phase 106-01). Not touched; full suite (`pytest tests/ -q`) is green apart from this one pre-existing, unrelated failure. `diagnostic_report.py` module coverage is 97% (148 stmts, 5 missed — well above the repo's 70% floor).

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- This plan closes Phase 110: `DiagnosticReport` now composes all four sub-objects (`AutoCapture`, `Provenance`, `TransportHealth`, `DbDiff`) from a single source, dual-rendered without duplicated logic (RPT-01 preserved across all three plans).
- Phase 112 (dev-test-handler-wiring) can now: invoke `prompt_provenance()` before the sweep, thread `AutoCapture.fw_board_identity` in from the transient per-op `comm`, call `build_db_diff(chip_name, db, results)` after the sweep completes, and render/write the completed `DiagnosticReport`.
- Phase 113/114 (submission-flow / support_status taxonomy) can rely on `db_diff.proposed_disposition` as read-only advisory text for maintainer triage — it is never a concrete `support_status` value and this module never writes the database, honoring the milestone's founding no-auto-graduate constraint (D-07).
- `vpp_vpe_mv` remains the one open `None` slot, explicitly deferred to Phase 111's measured-voltage sampler (unchanged by this plan).

---
*Phase: 110-diagnostic-report-model-dual-output-provenance-prompts*
*Completed: 2026-07-02*

## Self-Check: PASSED

- FOUND: firestarter_app/firestarter/diagnostic_report.py
- FOUND: firestarter_app/tests/test_diagnostic_report.py
- FOUND: .planning/phases/110-diagnostic-report-model-dual-output-provenance-prompts/110-03-SUMMARY.md
- FOUND commit (submodule v1.21-community-chip-validation-command branch): 90a65ad (test RED, DB-diff tests)
- FOUND commit (submodule): 0788ffc (feat GREEN, DbDiff + build_db_diff)
- FOUND commit (submodule): 21ff05e (test RED, composition into DiagnosticReport)
- FOUND commit (submodule): 8a38f13 (feat GREEN, composition into DiagnosticReport)
