---
phase: 147-report-provenance-every-dev-test-report-names-its-firmware
plan: 03
subsystem: infra
tags: [python, pytest, dev-test, provenance, diagnostic-report, ruff]

# Dependency graph
requires:
  - phase: 147-02
    provides: "AutoCapture.fw_board_identity populated end-to-end from a real ProgrammerIdentity; 1595-passed baseline"
provides:
  - "SCHEMA_VERSION = \"1.4\" with a value-population rationale note (D-09)"
  - "NOT_REPORTED = \"not reported\" -- the identity-specific honest-fallback constant (D-11), literal #1 of the 3 the phase creates"
  - "_identity_cell(value) -- render-boundary helper used only inside render(), never in to_dict() (D-10)"
  - "Both fw_board_identity and hw_revision rows in render() route through _identity_cell (D-12)"
  - "4 new render-level oracle tests proving marker present-when-absent, absent-when-populated, and JSON stays typed null"
affects: [147-05, 147-06]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Render-boundary substitution: a helper applied ONLY inside render(), never inside to_dict() -- keeps the machine-readable JSON typed (None-testable) while the human-readable surface gets an explicit marker, so the backward-compatibility story (PROV-04) stays one case instead of two"
    - "Explicit two-clause absence check (`value is None or value == \"\"`) instead of an or-coalescing expression, to avoid silently swallowing arbitrary falsy values with no decision behind it"
    - "Exact-cell assertion (field->value dict from a rich Table's two columns) instead of a whole-rendered-text substring scan, when a deliberately-untouched row in the same table legitimately renders the bare string this test is proving absent elsewhere (chip_id's `None / None`)"

key-files:
  created: []
  modified:
    - firestarter_app/firestarter/diagnostic_report.py
    - firestarter_app/tests/test_diagnostic_report.py

key-decisions:
  - "D-09/D-10/D-11/D-12/D-13(a) (147-CONTEXT.md) applied exactly as specified: value-population rationale note, JSON keeps typed null, marker is a new identity-specific constant (not a reuse of NOT_MEASURED), both identity rows fixed together, and the oracle proves both directions (present-when-absent, absent-when-populated) plus the to_dict()/JSON negative"
  - "Fixed a pre-existing test (Rule 1 auto-fix, not part of the plan's named artifact list): test_schema_version_1_3_single_sourced hardcoded the quoted literal '\"1.3\"' and would have asserted a now-absent string the instant Task 1 bumped SCHEMA_VERSION. Renamed to test_schema_version_1_4_single_sourced and updated the literal it checks for -- this is the SAME single-sourcing invariant the plan's own D-09 note relies on (every existing test imports the constant), just applied to the one site that restates it as a literal"
  - "Used an exact per-row dict (zip of the rich Table's two column cell lists) rather than a whole-rendered-text substring scan for the negative assertions in Task 3's tests -- the deliberately-untouched chip_id (expected/actual) row legitimately renders \"None / None\" on the same minimal report, so a blanket \"no bare None anywhere\" scan would false-positive on a row this plan explicitly leaves alone (D-12)"

requirements-completed: []

coverage:
  - id: T1
    description: "SCHEMA_VERSION bumped 1.3 -> 1.4 with a rationale note stating the value-population distinction (not a key addition), presence-only parser contract, and PROV-04 backward-compatibility; exactly one modified non-comment line in the module"
    requirement: "PROV-04 (advances, not completed by this plan)"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_diagnostic_report.py::test_schema_version_1_4_single_sourced"
        status: pass
      - kind: other
        ref: "python3 -c \"from firestarter.diagnostic_report import SCHEMA_VERSION; print(SCHEMA_VERSION)\" => 1.4"
        status: pass
    human_judgment: false
  - id: T2
    description: "NOT_REPORTED constant + _identity_cell() render-boundary helper added; both identity rows in render() route through it; protocol/host_version/chip_id rows unchanged; marker confined to render() path (AST-verified); no or-coalescing expression introduces it"
    requirement: "PROV-05 (advances, console surface only -- issue-parser surfaces owned by 147-05/147-06)"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_diagnostic_report.py::test_absent_identity_renders_the_explicit_marker_in_both_rows"
        status: pass
      - kind: other
        ref: "AST scan: functions referencing NOT_REPORTED/_identity_cell == {'_identity_cell', 'render'}"
        status: pass
    human_judgment: false
  - id: T3
    description: "Render-level marker oracle proven in both directions (present when absent, absent when populated); to_dict()/to_json_block() proven to stay marker-free and typed null; schema version pinned at 1.4"
    requirement: "PROV-04, PROV-05 (both advanced, neither completed by this plan)"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_diagnostic_report.py::test_absent_identity_stays_typed_null_in_to_dict"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_diagnostic_report.py::test_populated_identity_rows_render_the_value_verbatim"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_diagnostic_report.py::test_schema_version_is_one_four"
        status: pass
      - kind: other
        ref: "cd /workspaces/firestarter_app && python3 -m pytest tests/ -o addopts=\"\" -q => 1599 passed, 1 warning in 242.03s"
        status: pass
    human_judgment: false

duration: ~30min
completed: 2026-08-18
status: complete
---

# Phase 147 Plan 03: Report schema 1.4 + explicit unknown identity marker Summary

**Bumped `SCHEMA_VERSION` to `"1.4"` with a documented value-population rationale, and made an absent `fw_board_identity`/`hw_revision` render as an explicit `"not reported"` marker in the `rich` console table — while the fenced report JSON keeps typed `null` throughout.**

## Performance

- **Duration:** ~30 min
- **Completed:** 2026-08-18
- **Tasks:** 3
- **Files modified:** 2 (`firestarter/diagnostic_report.py`, `tests/test_diagnostic_report.py`)

## Accomplishments

- Bumped `SCHEMA_VERSION` from `"1.3"` to `"1.4"` and appended a fourth per-bump rationale block (D-09) beside the existing 1.1/1.2/1.3 notes: states this is a **value-population** change (a key that was unconditionally `null` now carries data) rather than a key addition, cites the 1.3 note's own rejection of "a field-plus-JSON change with no version bump" as the precedent that makes this the same class of change, records that both `[dev test]` parsers accept `schema_version` by presence only (no ordering logic introduced, D-17), and names PROV-04's frozen-fixture backward-compatibility guarantee. `git diff` against `diagnostic_report.py` shows exactly one modified non-comment line — the schema constant assignment.
- Added `NOT_REPORTED = "not reported"` immediately beside the existing `NOT_MEASURED` honest-fallback constant (D-11), with a trailing rationale naming the "asked and got nothing" vs. "never asked" distinction PROV-05 exists to remove. Pre-checked clean against `check_diagnostic_report_claims.py`'s 14 forbidden patterns (164 → 167 string literals scanned, zero matches both before and after).
- Added module-private `_identity_cell(value: object) -> str` as an explicit two-clause condition (`value is None or value == ""` → `NOT_REPORTED`, else `str(value)`) — never an `or`-coalescing expression. Routed the `fw_board_identity` and `hw_revision` rows in `render()` through it (D-12: both rows fixed together, since they share an origin and the same honest-best-effort semantics). Left `host_version`, `protocol`, and the `chip_id_expected`/`chip_id_actual` pair exactly as they were.
- Confirmed by AST scan that `NOT_REPORTED`/`_identity_cell` are referenced by exactly `{_identity_cell, render}` — never `to_dict()` or `_auto_capture_dict()` — so the marker is structurally confined to the render path and the JSON path stays clean (D-10).
- Added four new tests in `tests/test_diagnostic_report.py`: `test_absent_identity_renders_the_explicit_marker_in_both_rows` (exact per-row cell assertion, not a whole-table substring scan, because the deliberately-untouched `chip_id (expected/actual)` row legitimately renders `None / None` on the same minimal report and would false-positive a blanket scan), `test_absent_identity_stays_typed_null_in_to_dict` (D-10: both `to_dict()` and `to_json_block()` stay marker-free and typed `None`), `test_populated_identity_rows_render_the_value_verbatim` (the leg proving `_identity_cell` doesn't over-fire on a genuinely-present value), and `test_schema_version_is_one_four` (PROV-04, the sole literal-restating assertion for this version, mirroring the existing single-sourcing test's own convention).

## Task Commits

1. **Task 1: Bump SCHEMA_VERSION to 1.4 with a value-population rationale note** - `2260291` (feat)
2. **Task 2: Render an explicit unknown marker for both identity rows, keeping the JSON typed null** - `a0de674` (feat)
3. **Task 3: Prove the marker reaches the table while the JSON stays null (D-13(a))** - `e83e269` (test)

**Plan metadata:** committed via this SUMMARY + STATE.md + ROADMAP.md docs commit (see below), plus a `chore(147-03)` gitlink bump in the meta repo.

## Files Created/Modified

- `firestarter_app/firestarter/diagnostic_report.py` - `SCHEMA_VERSION` bumped to `"1.4"` + rationale note; `NOT_REPORTED` constant; `_identity_cell()` render-boundary helper; both identity rows in `render()` routed through it
- `firestarter_app/tests/test_diagnostic_report.py` - `test_schema_version_1_3_single_sourced` renamed/updated to `test_schema_version_1_4_single_sourced` (Rule 1 fix for Task 1's own breakage); 4 new tests for the D-13(a) render-level marker oracle

## Decisions Made

- Placed `_identity_cell` in its own new module section immediately before the `DiagnosticReport` class (rather than beside the `NOT_REPORTED`/`NOT_MEASURED` constants block or inside the class body), since it is conceptually a render-boundary helper and the plan's own framing groups it with `render()`, not with the constants.
- Used an exact per-row `dict(zip(field_col.cells, value_col.cells))` assertion for the new tests' negative checks instead of a whole-rendered-text substring scan for "no bare None" — the plan's suggested pattern (scan `_rendered_text(table)` for a standalone occurrence) would false-positive against the deliberately-untouched `chip_id (expected/actual)` row, which legitimately renders `None / None` on the same `_minimal_report()` fixture (chip_id fields are never set there). The exact-cell approach is strictly more precise than the suggested whitespace-boundary substring check and avoids this false positive entirely; the marker-count assertion (`rendered.count(NOT_REPORTED) == 2`) is still run over the whole table text as the plan specifies, for the positive case.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Renamed and updated `test_schema_version_1_3_single_sourced`**
- **Found during:** Task 1
- **Issue:** This pre-existing test asserted `inspect.getsource(dr_mod).count('"1.3"') == 1` as its single-sourcing invariant. Bumping `SCHEMA_VERSION` to `"1.4"` (Task 1's own required change) makes the quoted `"1.3"` literal disappear from the module entirely, so the count becomes `0` and the assertion fails — a test breakage directly caused by, and blocking completion of, this task's own acceptance criteria (`pytest ... -k schema` must exit 0).
- **Fix:** Renamed the test to `test_schema_version_1_4_single_sourced` and changed the counted literal to `'"1.4"'`, keeping the same single-sourcing invariant (the constant is restated as a literal in exactly one place in the production module) against the new value.
- **Files modified:** `firestarter_app/tests/test_diagnostic_report.py`
- **Verification:** `pytest tests/test_diagnostic_report.py -o addopts="" -q -k schema` exits 0; full suite green.
- **Committed in:** `2260291` (Task 1 commit)

---

**Total deviations:** 1 auto-fixed (1 bug)
**Impact on plan:** Necessary for Task 1's own stated acceptance criteria. No scope creep — same invariant, same file, just the literal the pre-existing test restates.

## Issues Encountered

None beyond the deviation above. `ci_parity.sh` and the full-suite run each exceed the 120s default Bash timeout and were run in the background; results read directly from the background log files.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- `firestarter_app/firestarter/diagnostic_report.py` now exposes `NOT_REPORTED` and `_identity_cell` for plans 147-05 (`tools/parse_devtest_issue.py`, literal #2 of 3) and 147-06 (the devtest-triage skill script, literal #3 of 3) to define their own equal-value marker constants against (the plan's own key-link: the marker literal defined here is literal #1 of 3, and 147-05 pins their equality).
- `SCHEMA_VERSION = "1.4"` is live; `tests/test_parse_devtest_issue.py`'s frozen fixtures (1.1-era null identity, `"9.9-future"` fixture) continue to prove presence-only parsing — no change needed there by this plan, and none made.
- PROV-04 is **advanced, not completed**, by this plan: the schema bump and its rationale landed, but the frozen-fixture backward-compatibility proof (`test_legacy_null_identity_body_still_parses_and_groups`) is owned by plan 147-05, per the plan's own objective text.
- PROV-05 is **advanced, not completed**, by this plan: the console (`rich` table) surface is fixed, but the issue-parser surfaces are owned by 147-05/147-06, per the plan's own objective text.
- Full-suite count: **1599 passed, 1 warning** (baseline 1595 + 4 new tests) — the new Phase 147 regression floor for the next plan.
- `bash tools/ci_parity.sh`: legs 1-3 exit 0; leg 4 exits 2 as documented design (ambient numpy PEP-695 stub truncating mypy in this devcontainer) — recorded as expected per the plan's explicit instruction, no `|| true` added.
- No blockers for 147-05/147-06.

## Self-Check: PASSED

- FOUND: `firestarter_app/firestarter/diagnostic_report.py` contains `SCHEMA_VERSION = "1.4"`, `NOT_REPORTED`, `_identity_cell`
- FOUND: `firestarter_app/tests/test_diagnostic_report.py` contains `test_absent_identity_renders_the_explicit_marker_in_both_rows`
- FOUND: commit `2260291` in `firestarter_app` (`git log --oneline --all | grep 2260291`)
- FOUND: commit `a0de674` in `firestarter_app` (`git log --oneline --all | grep a0de674`)
- FOUND: commit `e83e269` in `firestarter_app` (`git log --oneline --all | grep e83e269`)

---
*Phase: 147-report-provenance-every-dev-test-report-names-its-firmware*
*Completed: 2026-08-18*
