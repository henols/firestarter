---
phase: 113-submission-flow
plan: 02
subsystem: api
tags: [click, rich, subprocess, urllib, hashlib, gh-cli, submission, pii-scrub]

# Dependency graph
requires:
  - phase: 113-01
    provides: dedup_fingerprint(report) helper + DiagnosticReport.to_dict()["dedup_fingerprint"]
provides:
  - "firestarter/submit.py foundations: SUBMIT_REPO/GSD_INBOX_LABEL/URL byte-threshold constants (D-01, D-05)"
  - "sanitize_dict(d, *, user=None) -- recursive PII/path scrub of every to_dict() string leaf (SUB-02)"
  - "overall_verdict(results) -- FAIL-dominant title verdict (D-02), distinct from the handler's exit-code max()"
  - "build_title(report, chip) -- surfaces the SUB-03 dedup shorthash + verdict in the issue title"
  - "build_body(sanitized_dict, results, *, include_json=True) -- human table + optional fenced JSON, both from the sanitized dict"
  - "build_issue_url(title, body) -- hardcoded-repo issues/new URL, percent-encoded, no labels param (Pitfall 1)"
  - "gh_available(*, which_fn, run_fn) + submit_via_gh(title, body, *, run_fn) -- PATH/auth-gated gh tier, list argv, stdin body (T-113-01)"
affects: [113-03, 113-04]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Seam-injected callables (which_fn=shutil.which, run_fn=subprocess.run) with real defaults, mirroring avr_tool.py's shutil/subprocess precedent -- unit tests never touch PATH/network"
    - "Sanitize the DICT (not a re-render) so the fenced JSON and human table derive from one scrubbed source"

key-files:
  created:
    - firestarter_app/firestarter/submit.py
    - firestarter_app/tests/test_submit.py
  modified: []

key-decisions:
  - "overall_verdict is FAIL-dominant (BAD beats marginal) for title legibility -- deliberately NOT the same ordering as cli_handlers.py's exit-code max() (marginal=2 > BAD=1)"
  - "build_issue_url omits the labels query param entirely (RESEARCH Pitfall 1) -- GitHub drops/404s labels for non-write community testers; triage relies on the [dev test] title marker + fenced-JSON schema_version instead"
  - "build_body sources reason cells from the SANITIZED dict's steps, not the raw StepResult objects, so PII never re-enters the rendered table even though results is accepted for shape/API symmetry"
  - "gh_available never calls run_fn when which_fn('gh') is falsy -- PATH-short-circuited before any subprocess spawn"

patterns-established:
  - "Every submission-flow side-effecting boundary (shutil.which, subprocess.run) is a keyword-injectable seam with a real stdlib default"

requirements-completed: []
# NOTE: SUB-01/SUB-02 are multi-plan requirements (declared in 113-02/03/04's
# frontmatter alike) -- this plan delivers foundational pieces only (builders +
# gh-tier detection); the full tiered flow (TTY gate, preview, --submit wiring,
# oversize escalation) lands in Plan 03/04, so SUB-01/SUB-02 stay Pending in
# REQUIREMENTS.md until the plan that actually closes them. SUB-03 was already
# marked Complete at Plan 01 (dedup_fingerprint) -- no new completion here.

coverage:
  - id: D1
    description: "sanitize_dict deep-scrubs every string leaf (home-dir paths, /dev/tty*, COM*, /tmp, username) on a deep copy, base64-encodes bytes leaves"
    requirement: "SUB-02"
    verification:
      - kind: unit
        ref: "tests/test_submit.py -k sanitize"
        status: pass
    human_judgment: false
  - id: D2
    description: "build_title surfaces the SUB-03 dedup shorthash + FAIL-dominant overall_verdict in the issue title"
    requirement: "SUB-03"
    verification:
      - kind: unit
        ref: "tests/test_submit.py -k title"
        status: pass
    human_judgment: false
  - id: D3
    description: "build_issue_url routes to the hardcoded SUBMIT_REPO with percent-encoded params and no labels param"
    requirement: "SUB-01"
    verification:
      - kind: unit
        ref: "tests/test_submit.py -k build_issue_url"
        status: pass
    human_judgment: false
  - id: D4
    description: "gh_available is PATH-short-circuited + auth-gated; submit_via_gh shells out with a list argv + stdin body"
    requirement: "SUB-01"
    verification:
      - kind: unit
        ref: "tests/test_submit.py -k gh_tier"
        status: pass
    human_judgment: false

# Metrics
duration: 30min
completed: 2026-07-03
status: complete
---

# Phase 113 Plan 02: submit.py foundations Summary

**`submit.py` foundations -- D-01 hardcoded-repo constants, a recursive SUB-02 PII/path sanitizer, title/body/URL builders reading the Plan-01 dedup fingerprint, and a PATH/auth-gated `gh` shell-out tier using list argv + stdin body.**

## Performance

- **Duration:** ~30 min
- **Completed:** 2026-07-03T17:10:48Z
- **Tasks:** 3
- **Files modified:** 2 (both created)

## Accomplishments
- `firestarter/submit.py` created with the D-01 hardcoded `SUBMIT_REPO`/`GSD_INBOX_LABEL` constants, D-05 URL byte thresholds, and a `_SCRUBS` regex list covering home-dir paths (Linux/macOS/Windows), serial device names (`/dev/ttyACM*`, `/dev/ttyUSB*`, `/dev/tty.*`, `COM<n>`), and `/tmp` paths
- `sanitize_dict(d, *, user=None)` recursively scrubs every string leaf of a deep copy (never mutates the input), base64-encodes any `bytes` leaf, and whole-word-scrubs the current username when `len(user) >= 3`
- `overall_verdict(results)`, `build_title(report, chip)`, `build_body(sanitized_dict, results, *, include_json=True)`, and `build_issue_url(title, body)` implemented per D-01/D-02 -- the title reads `report.to_dict()["dedup_fingerprint"]` (the Plan-01 field) and the URL deliberately omits `labels` (Pitfall 1)
- `gh_available(*, which_fn, run_fn)` and `submit_via_gh(title, body, *, run_fn)` implemented with injectable seams, list argv (never shell string), and stdin body delivery (T-113-01 command-injection control)
- 33 new unit tests in `tests/test_submit.py`, one per PII leak vector plus title/body/URL/verdict/gh-tier coverage -- zero PATH/network/browser touched

## Task Commits

Each task was committed atomically inside the `firestarter_app` submodule (branch `v1.21-community-chip-validation-command`):

1. **Task 1: submit.py skeleton + constants + sanitize_dict recursive PII scrub** - `94df3fa` (feat)
2. **Task 2: overall_verdict + build_body + build_issue_url + build_title** - `827840a` (feat)
3. **Task 3: gh_available detection + submit_via_gh (list argv, stdin body)** - `7ea550c` (feat)

_No TDD flow used (tdd="true" on the plan tasks refers to test-alongside-implementation discipline, not a strict RED/GREEN/REFACTOR gate; tests were authored and verified green together with each task's implementation, matching the plan's `<verify>` commands.)_

## Files Created/Modified
- `firestarter_app/firestarter/submit.py` - orchestrator-only submission module: constants, `sanitize_dict`, `overall_verdict`, `build_title`, `build_body`, `build_issue_url`, `gh_available`, `submit_via_gh`
- `firestarter_app/tests/test_submit.py` - 33 unit tests (sanitize vectors, title/body/URL builders, gh-tier detection + shell-out)

## Decisions Made
- Kept `shutil`/`subprocess`/`webbrowser`/`urlencode`/`quote` imports at Task 1 per the plan's explicit instruction (some consumed only in later tasks), using targeted `# noqa: F401` on the imports not yet consumed at each intermediate commit so `ruff check` stays green at every atomic commit boundary — the noqa comments were removed as each import became consumed (Task 3 removed the `shutil`/`subprocess` noqa; `webbrowser`'s noqa remains, correctly, since `submit_via_browser` lands in Plan 03)
- `build_body` accepts `results` per the plan's declared signature but sources all rendered content from `sanitized_dict` only, keeping `results` for API shape symmetry with `overall_verdict`/callers — this is intentional, not dead code, per the plan's explicit "rows from the SANITIZED steps" requirement

## Deviations from Plan

None - plan executed exactly as written. All three tasks' `<action>`, `<behavior>`, and `<acceptance_criteria>` blocks were implemented verbatim, including the deliberate `labels` param omission (flagged in the plan itself as an intentional engineering deviation from the CONTEXT.md domain shorthand, not unflagged drift).

## Issues Encountered

None. `ruff check`, `ruff format --check`, `mypy firestarter/submit.py`, and `python tools/check_devtest_orchestrator.py` all passed cleanly at every commit boundary. The full `pytest tests/` suite shows exactly 3 pre-existing failures unrelated to this plan (`test_audit_coverage_matrix.py::test_golden_file_matches` — stale golden fixture predating this phase; `test_characterization.py::test_no_programmer_found_read/erase` — live-board-attached environment artifact) per the standing project memory notes on these two known issues; no new regressions were introduced.

## Known Stubs

None. `submit_via_browser` and `submit_report` (the orchestrating entry point) are explicitly out of scope for this plan per its own header ("`submit_via_browser` and `submit_report` are added in Plan 03") — not a stub, a declared phase boundary.

## User Setup Required

None - no external service configuration required. `gh` remains an optional runtime tool detected via `shutil.which`, never a pip dependency.

## Next Phase Readiness

- `submit.py` foundations (constants, sanitizer, builders, gh-tier) are ready for Plan 03 to compose into `submit_via_browser` + the `submit_report` orchestrator (D-03/D-04 TTY gate, D-05 oversize escalation).
- The Plan-04 SAFE-03 orchestrator-checker leg (adding `submit.py` to the scan set) will find the module already clean of any force-flag literal or wire-dict literal, per the plan's own forward-looking acceptance criterion.
- No blockers.

---
*Phase: 113-submission-flow*
*Completed: 2026-07-03*

## Self-Check: PASSED

- FOUND: firestarter_app/firestarter/submit.py
- FOUND: firestarter_app/tests/test_submit.py
- FOUND: .planning/phases/113-submission-flow/113-02-SUMMARY.md
- FOUND commit: 94df3fa
- FOUND commit: 827840a
- FOUND commit: 7ea550c
