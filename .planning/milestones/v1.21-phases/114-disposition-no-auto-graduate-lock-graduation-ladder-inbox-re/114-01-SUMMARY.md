---
phase: 114-disposition-no-auto-graduate-lock-graduation-ladder-inbox-re
plan: 01
subsystem: diagnostic-report
tags: [diagnostic-report, graduation-ladder, disposition, community-validation, dataclass, docs]

# Dependency graph
requires:
  - phase: 110-diagnostic-report-model-dual-output-provenance-prompts
    provides: DbDiff / build_db_diff advisory pipeline (RPT-05), single-source to_dict()/render()
  - phase: 113-submission-flow
    provides: dedup_fingerprint as the N>=2 cross-report agreement key
provides:
  - "DbDiff.ladder_state report-side derived field (community-reported / community-fail / '')"
  - "build_db_diff verdict->ladder_state derivation, community-confirmed never auto-emitted"
  - "SCHEMA_VERSION 1.1 (additive db_diff.ladder_state key)"
  - "doc/community-validation.md — four-state taxonomy + N>=2-via-dedup_fingerprint + manual promotion process"
affects: [114-02-inbox-parser, 114-03-disp01-ast-gate]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Single-source report model extended in place (Pattern 3) — ladder_state added once to _db_diff_dict(), inherited by to_dict()/render()/to_json_block()"
    - "Report-side-only state label (D-02) — never a chip_database.json write, mirrors the existing proposed_disposition advisory-text discipline"

key-files:
  created:
    - firestarter_app/doc/community-validation.md
  modified:
    - firestarter_app/firestarter/diagnostic_report.py
    - firestarter_app/tests/test_diagnostic_report.py

key-decisions:
  - "ladder_state derived in the SAME verdict-branch structure as proposed_disposition (BAD/marginal-indeterminate/all-OK/else) rather than a separate pass, keeping the two advisory outputs structurally coupled and easy to audit together"
  - "community-confirmed formalized only as a named-but-unused constant (_LADDER_COMMUNITY_CONFIRMED) plus documentation vocabulary — build_db_diff has no branch that can produce it, satisfying GRAD-01 SC2's human-only-target requirement by construction"
  - "SCHEMA_VERSION bumped 1.0 -> 1.1 as an additive (non-breaking) shape change; existing consumers reading current_support_status/proposed_disposition unaffected"

patterns-established:
  - "Report-side ladder tag pattern: any future graduation-ladder-adjacent field should extend DbDiff + _db_diff_dict() in place, never introduce a parallel field list"

requirements-completed: [GRAD-01]

coverage:
  - id: D1
    description: "build_db_diff derives ladder_state from sweep verdicts: BAD->community-fail, all-OK->community-reported, marginal/indeterminate/no-change->''"
    requirement: GRAD-01
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_diagnostic_report.py#test_ladder_state_verdict_mapping"
        status: pass
    human_judgment: false
  - id: D2
    description: "community-confirmed is never auto-emitted by build_db_diff for any verdict combination"
    requirement: GRAD-01
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_diagnostic_report.py#test_ladder_state_verdict_mapping"
        status: pass
    human_judgment: false
  - id: D3
    description: "ladder_state is single-sourced: to_dict()['db_diff']['ladder_state'] equals report.db_diff.ladder_state"
    requirement: GRAD-01
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_diagnostic_report.py#test_ladder_state_single_source_in_to_dict"
        status: pass
    human_judgment: false
  - id: D4
    description: "doc/community-validation.md documents the four ladder states, auto-tag derivation, N>=2-via-dedup_fingerprint cross-report promotion (distinct from Phase-108 per-run N>=2), and the manual maintainer-only build_db.py promotion path"
    requirement: GRAD-01
    verification:
      - kind: other
        ref: "test -f firestarter_app/doc/community-validation.md && grep -q community-confirmed ... && grep -q dedup_fingerprint ... && grep -q build_db.py ..."
        status: pass
    human_judgment: false

duration: 12min
completed: 2026-07-03
status: complete
---

# Phase 114 Plan 01: Graduation-Ladder Report-Side Tag + Taxonomy Doc Summary

**`DbDiff` gains a report-side `ladder_state` field (community-reported/community-fail/none) derived purely from sweep verdicts, with `community-confirmed` formalized as a documented human-only target that no code path can emit; `doc/community-validation.md` documents the full taxonomy and N>=2 promotion process.**

## Performance

- **Duration:** 12 min
- **Started:** 2026-07-03T18:56:00Z
- **Completed:** 2026-07-03T19:03:00Z
- **Tasks:** 2
- **Files modified:** 3 (2 modified, 1 created)

## Accomplishments
- `DbDiff.ladder_state` added as a plain report-side string attribute (default `""`), computed by `build_db_diff` in the same verdict-branch structure already used for `proposed_disposition` — BAD verdict → `community-fail`; all-OK candidate (subset of `{OK,NA,SKIPPED}` with ≥1 `OK`) → `community-reported`; marginal/indeterminate-fingerprint/no-change → `""`.
- `community-confirmed` formalized as a named constant (`_LADDER_COMMUNITY_CONFIRMED`) that is referenced only in documentation and test assertions proving it is unreachable from `build_db_diff` — it remains strictly the human-gated target (GRAD-01 SC2).
- `ladder_state` exposed exactly once via `_db_diff_dict()` → `to_dict()['db_diff']['ladder_state']`, inherited automatically by both `render()` (new table row) and `to_json_block()` (fenced JSON) — no second field list.
- `SCHEMA_VERSION` bumped `"1.0"` → `"1.1"` (additive shape change; documented inline).
- `firestarter_app/doc/community-validation.md` authored: four ladder states, the auto-tag derivation, the `dedup_fingerprint`-keyed cross-report N≥2 rule explicitly distinguished from Phase 108's internal per-run N≥2, and the manual `tools/build_db.py`-only promotion path (no code performs or gates the write).

## Task Commits

Each task was committed atomically inside the `firestarter_app` submodule (branch `v1.21-community-chip-validation-command`):

1. **Task 1 (TDD RED): failing ladder_state derivation tests** - `355981a` (test)
2. **Task 1 (TDD GREEN): ladder_state derivation + single-source wiring** - `3cb68ab` (feat)
3. **Task 2: doc/community-validation.md taxonomy doc** - `e6e55bb` (docs)

**Plan metadata:** meta-repo commit for STATE/ROADMAP/SUMMARY (this commit).

## Files Created/Modified
- `firestarter_app/firestarter/diagnostic_report.py` - `_LADDER_*` constants, `DbDiff.ladder_state` field, `build_db_diff` verdict→ladder_state derivation, `_db_diff_dict`/`render()` single-source additions, `SCHEMA_VERSION` bump to `1.1`
- `firestarter_app/tests/test_diagnostic_report.py` - `test_ladder_state_verdict_mapping`, `test_ladder_state_single_source_in_to_dict`
- `firestarter_app/doc/community-validation.md` (new) - four-state ladder taxonomy + N≥2 + manual promotion doc

## Decisions Made
- Kept `ladder_state` derivation branch-for-branch aligned with the existing `proposed_disposition` mapping in `build_db_diff` rather than a separate helper function, so the two advisory outputs can never drift apart under future edits.
- Left `_LADDER_COMMUNITY_CONFIRMED` as a defined-but-never-assigned constant (documentation/vocabulary anchor only) instead of omitting it entirely, so the taxonomy is complete and grep/AST-discoverable for the Plan 03 DISP-01 gate.

## Deviations from Plan

None - plan executed exactly as written. `ruff format` reformatted two lines inside the newly-added test (line-length wrapping) as part of the plan's own `<verify>` ruff pass; no logic change.

## Issues Encountered
None. Full suite run confirmed only the 3 pre-existing, previously-documented environment-artifact failures (`test_audit_coverage_matrix::test_golden_file_matches`, `test_no_programmer_found_read`, `test_no_programmer_found_erase` — the latter two are live-board-session artifacts, not present in this bench-free run's environment either, so they failed for the documented reason, not a new regression).

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Plan 02 (INBOX-01 parser) can now consume `to_dict()['db_diff']['ladder_state']` alongside `dedup_fingerprint` when computing the DB-diff + N-agreeing surface for `gsd-inbox` triage.
- Plan 03 (DISP-01 AST gate) has a concrete, documented allow/deny surface to scan: `diagnostic_report.py`'s `build_db_diff`/`DbDiff` never write `support_status`, only read it via `db.get_eprom_config`.
- No blockers.

---
*Phase: 114-disposition-no-auto-graduate-lock-graduation-ladder-inbox-re*
*Completed: 2026-07-03*

## Self-Check: PASSED

- FOUND: firestarter_app/firestarter/diagnostic_report.py
- FOUND: firestarter_app/doc/community-validation.md
- FOUND: .planning/phases/114-disposition-no-auto-graduate-lock-graduation-ladder-inbox-re/114-01-SUMMARY.md
- FOUND commit: 355981a (test RED)
- FOUND commit: 3cb68ab (feat GREEN)
- FOUND commit: e6e55bb (docs taxonomy)
