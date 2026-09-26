---
phase: 114-disposition-no-auto-graduate-lock-graduation-ladder-inbox-re
plan: 02
subsystem: tooling
tags: [inbox-triage, dedup-fingerprint, graduation-ladder, community-validation, stdlib-cli]

# Dependency graph
requires:
  - phase: 114-disposition-no-auto-graduate-lock-graduation-ladder-inbox-re (plan 01)
    provides: "DbDiff.ladder_state report-side field + SCHEMA_VERSION 1.1 (the shape this parser tolerates for both 1.0 and 1.1)"
  - phase: 113-submission-flow
    provides: "dedup_fingerprint (SUB-03) as the cross-report agreement key; build_title/build_body fenced-JSON body shape this parser detects"
  - phase: 110-diagnostic-report-model-dual-output-provenance-prompts
    provides: "DiagnosticReport.to_dict()/to_json_block() single-source fenced JSON shape"
provides:
  - "tools/parse_devtest_issue.py — stdlib-only INBOX-01 triage CLI (parse_devtest_body/extract_db_diff/count_agreeing/render_diff/main)"
  - "GRAD-01's cross-report N>=2 signal realized: count_agreeing groups saved issue bodies by embedded dedup_fingerprint"
affects: [114-03-disp01-ast-gate]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Body-only vs title+body detection split (_extract_fenced_report vs parse_devtest_body) — count_agreeing only ever has bodies (no titles), so the schema_version-presence check is factored out of the title-marker check"
    - "Lazy first-party import for an optional read-only DB re-check (_read_live_support_status imports firestarter.database only inside the function body) — keeps the core detection/DB-diff path importable with zero package dependency, matching D-04's stdlib-only mandate"

key-files:
  created:
    - firestarter_app/tools/parse_devtest_issue.py
    - firestarter_app/tests/test_parse_devtest_issue.py

key-decisions:
  - "CLI shape (discretionary, D-04): single-body mode takes --title (from `gh issue view --json title`) and --body-file/stdin separately, rather than encoding title+body into one file — count_agreeing's --dir/--glob mode operates on plain saved body files (title not needed, matching what `gh issue view --json body -q .body` naturally produces)"
  - "schema_version accepted by PRESENCE only (any value), not an exact string match — survives Plan 01's 1.0->1.1 bump and any future schema version without a parser code change"
  - "No rich import anywhere in the module (even though rich is already a project dependency) — plain-text render_diff() only, to satisfy the literal 'no third-party import errors' acceptance criterion and keep --help usable with zero optional-dependency risk"
  - "gh shell-out NOT implemented in this parser — out of scope for INBOX-01's detection/DB-diff/N-agreeing surface; submit.py already owns the gh-argv-list discipline this module would mirror if a future phase adds it"

requirements-completed: [INBOX-01, GRAD-01]

coverage:
  - id: D1
    description: "parse_devtest_body detects a dev test report iff BOTH the [dev test] title marker AND a fenced json block with a schema_version key are present; missing either, malformed JSON, non-dict JSON, or an oversized body all return None without raising"
    requirement: INBOX-01
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_parse_devtest_issue.py -k detect (6 tests) and -k malformed (5 tests)"
        status: pass
    human_judgment: false
  - id: D2
    description: "extract_db_diff surfaces current_support_status/proposed_disposition/ladder_state/dedup_fingerprint from an already-parsed report, defensively defaulting when db_diff or ladder_state is absent (schema 1.0 tolerance)"
    requirement: INBOX-01
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_parse_devtest_issue.py -k db_diff (4 tests)"
        status: pass
    human_judgment: false
  - id: D3
    description: "count_agreeing groups saved issue bodies by their embedded dedup_fingerprint (D-03) — 2 matching + 1 differing yields count 2 for the shared fingerprint; grouping proven to key off the embedded fingerprint, not per-step run counts (RESEARCH Pitfall 5)"
    requirement: GRAD-01
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_parse_devtest_issue.py -k agreeing (4 tests)"
        status: pass
    human_judgment: false
  - id: D4
    description: "the parser is stdlib-only (no third-party import errors on --help), never uses eval/exec/shell=True, and never writes a support_status key anywhere (read-only, DISP-01 scan target)"
    requirement: INBOX-01
    verification:
      - kind: other
        ref: "python tools/parse_devtest_issue.py --help; grep -nE 'eval\\(|exec\\(|shell=True' (no matches); AST scan for support_status assignment targets (no matches)"
        status: pass
    human_judgment: false

duration: 15min
completed: 2026-07-03
status: complete
---

# Phase 114 Plan 02: INBOX-01 Stdlib Triage Parser Summary

**`tools/parse_devtest_issue.py` — a stdlib-only CLI that detects a community `dev test` GitHub issue via its `[dev test]` title marker plus fenced-JSON `schema_version`, surfaces the current-vs-proposed DB-diff (including Plan 01's `ladder_state`), and counts matching `dedup_fingerprint`s across saved issue bodies to realize GRAD-01's cross-report N>=2 signal.**

## Performance

- **Duration:** 15 min
- **Started:** 2026-07-03T19:06:00Z
- **Completed:** 2026-07-03T19:21:00Z
- **Tasks:** 2
- **Files modified:** 2 (both created)

## Accomplishments
- `parse_devtest_body(title, body)` detects a dev test report by requiring BOTH markers (defensive against a stray fenced block): the `[dev test]` title marker and a fenced ```` ```json ```` block whose parsed object carries `schema_version` (accepted by presence, not exact-version match — survives Plan 01's 1.0→1.1 bump and any future schema change).
- `extract_db_diff(report_obj)` surfaces `current_support_status` / `proposed_disposition` / `ladder_state` / `dedup_fingerprint` from the embedded JSON, defensively defaulting when `db_diff` is absent/`None` or `ladder_state` is missing (an older schema-1.0-shaped report).
- `count_agreeing(bodies)` groups saved issue bodies by their ALREADY-EMBEDDED `dedup_fingerprint` (never re-hashed) — the cross-report N≥2 human-decision signal (D-03), explicitly distinct from Phase-108's internal per-run N≥2. A non-dev-test body is silently skipped.
- `render_diff(...)` produces a plain-text current-vs-proposed diff render (no third-party dependency), explicitly labeling any `n_agreeing` count "a maintainer decision input — NEVER an auto-promotion trigger" (D-01).
- `main()` argparse CLI: single-body mode (`--title` + `--body-file`/stdin) prints detection + DB-diff; `--dir`/`--glob` mode computes N-agreeing counts across saved bodies; optional `--live-db` re-reads `current_support_status` live via `EpromDatabase.get_eprom_config` (read-only, lazily imported so the core stdlib path never needs the package installed).
- Fail-soft throughout: oversized (`_MAX_BODY_BYTES` = 128 KiB) bodies, truncated/malformed JSON, non-dict JSON payloads, and missing fences/markers all return `None` / are skipped — never an exception (T-114-03/T-114-04).
- `tests/test_parse_devtest_issue.py` (19 tests): fixtures built from the REAL `submit.py`/`diagnostic_report.py` production builders (`build_title`/`build_body`/`build_db_diff`/`to_dict`) so detection and DB-diff tests exercise the exact shape a community tester's issue actually carries, plus hand-built negative-path fixtures for the malformed/oversized cases.

## Task Commits

Each task was committed atomically inside the `firestarter_app` submodule (branch `v1.21-community-chip-validation-command`):

1. **Task 1: Implement stdlib parse_devtest_issue.py (detect + DB-diff + N-agreeing)** - `50b07c4` (feat)
2. **Task 2: Unit tests for parse_devtest_issue.py (detect / db_diff / N-agreeing / malformed)** - `8b6962d` (test)

**Plan metadata:** meta-repo commit for STATE/ROADMAP/SUMMARY (this commit).

## Files Created/Modified
- `firestarter_app/tools/parse_devtest_issue.py` (new) - stdlib-only INBOX-01 triage CLI: `parse_devtest_body`, `extract_db_diff`, `count_agreeing`, `render_diff`, `main`, plus `_FENCE`/`_DEV_TEST_MARKER`/`_MAX_BODY_BYTES` module constants
- `firestarter_app/tests/test_parse_devtest_issue.py` (new) - 19 tests across DETECT (6), DB-DIFF (4), AGREEING (4), MALFORMED (5) taxonomy groups

## Decisions Made
- CLI shape (discretionary per D-04): single-body mode takes `--title` and `--body-file`/stdin as SEPARATE inputs (matching two separate `gh issue view --json title`/`--json body` invocations) rather than one combined file — keeps `--dir`/`--glob` N-agreeing mode operating on plain saved-body files with no title-encoding convention needed.
- `schema_version` matched by presence only, never an exact-version string comparison, so a future schema bump never requires a parser change.
- Deliberately omitted `rich` from this module (even though it is already a project dependency used by `submit.py`/`diagnostic_report.py`) — `render_diff` is plain-text-only, satisfying the plan's literal "no third-party import errors" acceptance criterion with zero optional-dependency risk.
- `gh` shell-out was NOT implemented — out of scope for the parse/detect/DB-diff/N-agreeing surface this plan defines; if a future phase wires `gh issue list` fetching directly into this tool, it should mirror `submit.py`'s argv-list (never `shell=True`) discipline.

## Deviations from Plan

None - plan executed exactly as written. Task 1 (marked `tdd="true"` in frontmatter) was implemented and manually verified functionally correct before Task 2 authored the formal pytest suite, per the plan's own two-task decomposition (Task 1 = implementation with a `<behavior>` spec + `ast.parse`/`--help` verify; Task 2 = the dedicated unit-test task) rather than a strict RED-before-GREEN split — the plan itself organizes the work this way, not a generic TDD RED/GREEN cycle within Task 1 alone.

## Issues Encountered
None. `ruff format` reformatted both new files (line-length wrapping) as part of the plan's own `<verify>`/`<verification>` ruff pass; no logic change. Full suite run (`pytest tests/ -q`) confirmed only the 3 pre-existing, previously-documented environment-artifact failures (`test_audit_coverage_matrix::test_golden_file_matches` — stale golden fixture; `test_no_programmer_found_read`/`test_no_programmer_found_erase` — live-board-session artifacts), unrelated to this plan's changes.

## User Setup Required
None - no external service configuration required. The parser is invoked manually by the maintainer during `gsd-inbox` triage (documentation-only integration, D-04) — the installed `.claude/gsd-core/workflows/inbox.md` was NOT edited.

## Next Phase Readiness
- Plan 03 (DISP-01 AST gate) has a concrete second scan target: `tools/parse_devtest_issue.py` reads `support_status` only via `.get(...)` on already-parsed dicts and never assigns it — verified inline in this plan (grep + AST-scan for assignment targets, both clean) and ready for the formal DISP-01 checker to confirm structurally.
- The parser is a self-contained CLI a maintainer can run today (`python tools/parse_devtest_issue.py --title "..." --body-file body.txt` or `--dir saved_bodies/ --glob '*.txt'`) — no `gh` dependency, no bench required.
- No blockers.

---
*Phase: 114-disposition-no-auto-graduate-lock-graduation-ladder-inbox-re*
*Completed: 2026-07-03*

## Self-Check: PASSED

- FOUND: firestarter_app/tools/parse_devtest_issue.py
- FOUND: firestarter_app/tests/test_parse_devtest_issue.py
- FOUND: .planning/phases/114-disposition-no-auto-graduate-lock-graduation-ladder-inbox-re/114-02-SUMMARY.md
- FOUND commit: 50b07c4 (feat, firestarter_app)
- FOUND commit: 8b6962d (test, firestarter_app)
- FOUND commit: 71b8d8f (docs, meta)
