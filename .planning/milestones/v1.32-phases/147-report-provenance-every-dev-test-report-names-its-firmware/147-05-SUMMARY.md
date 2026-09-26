---
phase: 147-report-provenance-every-dev-test-report-names-its-firmware
plan: 05
subsystem: infra
tags: [python, pytest, dev-test, provenance, parser, ruff]

# Dependency graph
requires:
  - phase: 147-02
    provides: "AutoCapture.fw_board_identity populated end-to-end from a real ProgrammerIdentity"
  - phase: 147-03
    provides: "NOT_REPORTED = \"not reported\" (literal #1 of three) and SCHEMA_VERSION = \"1.4\" on firestarter/diagnostic_report.py"
provides:
  - "tools/parse_devtest_issue.py: NOT_REPORTED (literal #2 of three) + _NOT_ATTRIBUTABLE module constants"
  - "render_diff() emits labelled host_version and fw_board_identity rows; the identity row folds in the not-attributable clause when the identity is None or empty (D-14/D-17); no hw_revision row (D-15), no attributable boolean (D-14)"
  - "First-ever render_diff tests (W-2): populated identity, absent identity in both null/empty-string forms, deliberate hw_revision omission, non-regression pin on the pre-existing n_agreeing clause"
  - "A second frozen fixture (_NULL_IDENTITY_TITLE/_NULL_IDENTITY_BODY) carrying fw_board_identity: null -- PROV-04's real-world population, distinct from the pre-existing populated _B11_BODY (W-3)"
  - "A value-parity assert pinning the app-side NOT_REPORTED literal equal to the parser-side one -- this test module is the only place that legitimately imports both worlds (D-11 enforcement substitute)"
  - "A claim-pattern assert proving both parser literals clean against check_diagnostic_report_claims.py's 14-pattern vocabulary, which today scans only diagnostic_report.py"
affects: [147-06]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "A stdlib-only module cannot import its sibling's honest-fallback constant, so the value is duplicated with a comment naming the barrier and pointing at the enforcement substitute (a value-parity test) -- three literals, one equality assert, not a compromise (D-11)"
    - "The conditional row folds the marker and the qualifying clause into ONE string (`f\"{NOT_REPORTED} -- {_NOT_ATTRIBUTABLE}\"`) rather than appending a second line, so a triager reading a single row sees both the absence and the action to take"
    - "Explicit two-clause None-or-empty-string substitution, never an or-coalescing expression, mirrored from diagnostic_report.py's own _identity_cell -- an or-expression would also swallow other falsy values with no decision behind them"
    - "A greenfield render function gets its first tests as direct substring/line checks on its returned str, with no _rendered_text indirection and no CLI subprocess, since it is a pure function of (report_obj, diff, n_agreeing=)"

key-files:
  created: []
  modified:
    - firestarter_app/tools/parse_devtest_issue.py
    - firestarter_app/tests/test_parse_devtest_issue.py

key-decisions:
  - "D-11/D-14/D-15/D-16/D-17 applied exactly as specified: NOT_REPORTED and _NOT_ATTRIBUTABLE are local literals (not imports) in tools/parse_devtest_issue.py; render_diff labels host_version and fw_board_identity, folding the not-attributable clause into the identity row when absent; hw_revision is deliberately omitted; no schema-version ordering logic was added anywhere"
  - "Extended the existing _build_realistic_title_body() test helper with an optional fw_board_identity parameter (default None, all existing callers unaffected) instead of hand-building a third fixture, so the populated and empty-string render_diff cases are still built through the real production builders (submit.py/diagnostic_report.py), matching this file's own stated fixture-fidelity discipline"
  - "The null-identity frozen fixture (_NULL_IDENTITY_BODY) models chip at28c256, protocol 0x0D, host_version 3.0.0b15, hw_revision \"Rev 2.0-class, Override HW: Rev 2.3\" -- the exact gh#21/#32 half-answer shape SKILL.md's own transcript documents -- to prove PROV-04 and PROV-06 together on one realistic artifact rather than a synthetic minimal one"
  - "The skill script's third marker literal (.claude/skills/devtest-triage/scripts/devtest_issues.py) is deliberately NOT covered by the marker-parity test -- an app-repo test reaching into /workspaces/.claude/ (a different repo) would fail OPEN in standalone CI. That parity is plan 147-06's human-verify checkpoint, stated in the parity test's own docstring"

requirements-completed: [PROV-04]

coverage:
  - id: D1
    description: "render_diff() emits a labelled fw_board_identity row carrying the exact value when populated, and no not-attributable clause in that case; a labelled host_version row is present in the same render (PROV-06)"
    requirement: "PROV-06 (advances, not completed by this plan -- the skill-parser half is 147-06's)"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_parse_devtest_issue.py::test_render_diff_labels_a_populated_firmware_identity"
        status: pass
    human_judgment: false
  - id: D2
    description: "A None fw_board_identity AND an empty-string one both render NOT_REPORTED plus the not-attributable clause -- never a blank (D-14/D-17/PROV-05)"
    requirement: "PROV-06"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_parse_devtest_issue.py::test_render_diff_marks_an_absent_identity_not_attributable"
        status: pass
    human_judgment: false
  - id: D3
    description: "No hw_revision label appears anywhere in render_diff's output -- a deliberate omission (D-15), not an oversight"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_parse_devtest_issue.py::test_render_diff_omits_hw_revision"
        status: pass
      - kind: other
        ref: "grep -c 'hw_revision' tools/parse_devtest_issue.py => 0"
        status: pass
    human_judgment: false
  - id: D4
    description: "The pre-existing n_agreeing labelled-clause block (zero tests before this plan) is pinned as a non-regression leg in the same pass that adds to render_diff"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_parse_devtest_issue.py::test_render_diff_still_labels_n_agreeing_as_a_maintainer_decision_input"
        status: pass
    human_judgment: false
  - id: D5
    description: "A frozen fw_board_identity: null report body (schema_version 1.2, chip at28c256, protocol 0x0D, host_version 3.0.0b15) still parses, its schema_version is readable, its identity reads None, extract_db_diff's grouping is unchanged, and render_diff over it carries the marker plus the not-attributable clause -- PROV-04's real-world population, proved together with PROV-06 on one artifact (W-3)"
    requirement: "PROV-04"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_parse_devtest_issue.py::test_legacy_null_identity_body_still_parses_and_groups"
        status: pass
    human_judgment: false
  - id: D6
    description: "The app-side NOT_REPORTED literal in firestarter/diagnostic_report.py equals the one duplicated in tools/parse_devtest_issue.py -- the D-11 enforcement substitute for an import architecture forbids"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_parse_devtest_issue.py::test_unknown_marker_string_matches_the_report_model"
        status: pass
    human_judgment: false
  - id: D7
    description: "Neither NOT_REPORTED nor _NOT_ATTRIBUTABLE (this module's copies) trips any of check_diagnostic_report_claims.py's 14 forbidden-phrase patterns; the imported pattern list is asserted non-empty (>=14) so the test cannot pass on a silently-empty import"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_parse_devtest_issue.py::test_parser_marker_strings_trip_no_forbidden_claim_pattern"
        status: pass
    human_judgment: false
  - id: D8
    description: "Full app test suite green with 7 new tests over the 147-04 baseline (1609 -> 1616 passed, 1 warning); the module-level stdlib-only contract of tools/parse_devtest_issue.py holds (module-level imports unchanged: __future__, argparse, json, pathlib, re, sys, typing; exactly one pre-existing function-local firestarter import, unchanged); ci_parity.sh legs 1-3 green, leg 4 exits 2 as documented design"
    verification:
      - kind: other
        ref: "cd /workspaces/firestarter_app && python3 -m pytest tests/ -o addopts=\"\" -q  =>  1616 passed, 1 warning in ~284-288s (run twice, identical count)"
        status: pass
      - kind: other
        ref: "cd /workspaces/firestarter_app && bash tools/ci_parity.sh  =>  legs 1/2/3 exit 0, leg 4 exit 2 (expected: 'Type statement is only supported in Python 3.12 and greater' from the ambient numpy PEP-695 stub)"
        status: pass
      - kind: other
        ref: "python3 tools/check_diagnostic_report_claims.py && python3 tools/check_devtest_orchestrator.py  =>  both PASS"
        status: pass
    human_judgment: false

duration: ~27min
completed: 2026-08-18
status: complete
---

# Phase 147 Plan 05: Triage render provenance -- render_diff, W-2, W-3 Summary

**`render_diff` now labels `host_version`/`fw_board_identity` and folds a not-attributable clause into the identity row when absent, tested for the first time ever (0 -> 7 tests), with a second frozen fixture proving PROV-04's null-identity real-world case and a value-parity assert pinning the app-side and parser-side `NOT_REPORTED` literals equal.**

## Performance

- **Duration:** ~27 min
- **Completed:** 2026-08-18
- **Tasks:** 3
- **Files modified:** 2 (`firestarter_app/tools/parse_devtest_issue.py`, `firestarter_app/tests/test_parse_devtest_issue.py`)

## Accomplishments

- Added `NOT_REPORTED` (literal #2 of three, D-11) and `_NOT_ATTRIBUTABLE` module constants to `tools/parse_devtest_issue.py`, each with a comment naming why it is a local literal (the module's stdlib-only contract) rather than an import, and pointing at the value-parity test as the enforcement substitute.
- `render_diff` now inserts a labelled `host_version` row and a labelled `fw_board_identity` row immediately after `schema_version` and before `dedup_fingerprint`. The identity row folds `NOT_REPORTED -- <clause>` into itself (one row, not two) when the identity is `None` or `""`, using an explicit two-clause condition rather than an `or`-coalescing expression. No `hw_revision` row (D-15) and no derived `attributable` boolean (D-14).
- `render_diff` had zero tests anywhere in the repo before this plan. Four new tests (W-2) prove the populated case, the absent case in both `None` and empty-string forms, the deliberate `hw_revision` omission, and a non-regression pin on the pre-existing `n_agreeing` clause. Extended `_build_realistic_title_body()` with an optional `fw_board_identity` parameter (default `None`, existing callers unaffected) so these cases are built through the real production builders rather than a hand-approximated stand-in.
- A second frozen fixture (`_NULL_IDENTITY_TITLE`/`_NULL_IDENTITY_BODY`, W-3) models a realistic `at28c256`/`0x0D`/`3.0.0b15` report carrying `fw_board_identity: null` -- the existing `_B11_BODY` fixture carries a *populated* identity, so it could not stand in for PROV-04's real-world population. `test_legacy_null_identity_body_still_parses_and_groups` proves it still parses, still groups, and renders the marker plus the not-attributable clause through `render_diff`.
- `test_unknown_marker_string_matches_the_report_model` pins the two app-side `NOT_REPORTED` literals equal, and `test_parser_marker_strings_trip_no_forbidden_claim_pattern` proves both parser literals clean against the live 14-pattern `FORBIDDEN_PATTERNS` table (imported, not reproduced), with a non-vacuity floor (`len(...) >= 14`).
- Full suite: 1609 -> 1616 passed, 1 warning (7 new tests: 4 from W-2 + 3 from W-3). `ci_parity.sh` legs 1-3 exit 0; leg 4 exits 2 as documented design (ambient numpy PEP-695 stub truncating mypy in this devcontainer) -- recorded as expected, no `|| true` added.

## Task Commits

1. **Task 1: Add the labelled identity line and the not-attributable clause to render_diff** - `ddd787a` (feat)
2. **Task 2: W-2 -- create the first-ever render_diff tests** - `ec6182f` (test)
3. **Task 3: W-3 -- a null-identity frozen fixture, the marker-parity assert, and a claim-pattern assert** - `9701209` (test)

**Plan metadata:** committed via this SUMMARY + STATE.md + ROADMAP.md + REQUIREMENTS.md docs commit (see below), plus a `chore(147-05)` gitlink bump in the meta repo.

## Files Created/Modified

- `firestarter_app/tools/parse_devtest_issue.py` - `NOT_REPORTED`/`_NOT_ATTRIBUTABLE` module constants; `render_diff` now carries labelled `host_version`/`fw_board_identity` rows, the latter folding in the not-attributable clause when absent
- `firestarter_app/tests/test_parse_devtest_issue.py` - `render_diff` added to the import block; `_build_realistic_title_body()` extended with an optional `fw_board_identity` param; 7 new tests (4 render_diff, 3 W-3/parity/claim-pattern); `_NULL_IDENTITY_TITLE`/`_NULL_IDENTITY_BODY` frozen fixture constants

## Decisions Made

- Folded the not-attributable clause into the SAME row as the marker (`f"{NOT_REPORTED} -- {_NOT_ATTRIBUTABLE}"`) rather than appending a second line the way the existing `n_agreeing` block appends its own optional row -- the plan's own wording ("the row must carry the marker and `_NOT_ATTRIBUTABLE`") reads as one row carrying both, and this keeps `host_version`/`fw_board_identity` as two rows always present (matching "insert two rows... immediately after schema_version"), with only their *content* varying by presence.
- Extended the existing `_build_realistic_title_body()` helper with a `fw_board_identity` keyword-only parameter (default `None`) instead of hand-building a third body-construction path, keeping the populated/empty-string `render_diff` fixtures faithful to the real `submit.py`/`diagnostic_report.py` builders per this test file's own stated fidelity discipline.
- Modeled `_NULL_IDENTITY_BODY`'s `hw_revision` field (`"Rev 2.0-class, Override HW: Rev 2.3"`) and chip/protocol (`at28c256`/`0x0D`) on `SKILL.md`'s own documented `#32 at28c256 -- FAIL` transcript, so the fixture is the same realistic gh#21/#32 half-answer shape this milestone exists to fix, not a synthetic minimal stand-in.

## Deviations from Plan

None functionally -- plan executed exactly as written, with one documentation-accuracy note (not a deviation; no plan text was altered and no code changed as a result):

- **Acceptance-criteria self-contradiction (Task 3):** the plan's artifact list mandates the exact test name `test_parser_marker_strings_trip_no_forbidden_claim_pattern`, but a separate acceptance-criteria row for the same task states `pytest ... -k marker_string` must report "exactly 1 passed". Because pytest's `-k` does substring matching against the nodeid, `"marker_string"` is a substring of the mandated test name's `"marker_strings"`, so `-k marker_string` necessarily also selects `test_unknown_marker_string_matches_the_report_model` -- 2 tests, not 1, both passing (confirmed: `pytest tests/test_parse_devtest_issue.py -o addopts="" -q -k marker_string` -> `2 passed`). The mandated test name was kept verbatim (it is the more specific, explicitly-named requirement); the count-based row is unreachable as literally worded given that name. The `<verify>` block's own automated command only checks exit code (0), which holds either way -- this is a wording imprecision in the plan's own acceptance criteria, not a functional gap.

## Issues Encountered

- Two comments I first wrote in `tools/parse_devtest_issue.py` accidentally contained the literal grep targets the acceptance criteria scan for (`from firestarter` and `or NOT_REPORTED`, inside prose explaining why those patterns are avoided) -- caught immediately by running the criteria's own grep commands before committing, and reworded without changing any code logic.
- `ruff check --fix`/`ruff format` reorganized the test file's `firestarter.diagnostic_report` imports (merging two `from ... import` lines into a de-duplicated block) and reflowed one long assert line -- both formatting-only, applied and verified before commit.
- The full-suite `pytest` run and `bash tools/ci_parity.sh` each exceed the 120s default Bash timeout and were run in the background; results read directly from the background output files (confirmed twice for the full-suite count, both times 1616 passed).

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- PROV-04 is now complete: a report written by an earlier-shaped body (`fw_board_identity: null`) parses without error against the bumped schema, on both the null-identity fixture added here and the pre-existing `_B11_BODY`.
- PROV-06 is advanced, not completed, by this plan: the app-side parser (`tools/parse_devtest_issue.py`) is done and tested. The devtest-triage skill script's `show` render (`.claude/skills/devtest-triage/scripts/devtest_issues.py`, a different repo) and its own copy of the marker literal (literal #3 of three) remain for 147-06, including the two offline `show --body-file` runs and the `SKILL.md` transcript update that plan's human-verify checkpoint covers.
- The marker-parity test explicitly documents, in its own docstring, that literal #3's parity is NOT covered here and IS covered by 147-06's checkpoint -- so 147-06 should not skip that verification leg believing it is already proven.
- `tests/test_parse_devtest_issue.py` pre-plan count was 22; post-plan count is 29 (7 new tests).
- Full-suite count: **1616 passed, 1 warning** (147-04 baseline 1609 + 7 new test cases) -- the new Phase 147 regression floor for 147-06.
- `bash tools/ci_parity.sh`: legs 1-3 exit 0; leg 4 exits 2 as documented design (ambient numpy PEP-695 stub truncating mypy in this devcontainer) -- recorded as expected, no `|| true` added.
- No blockers for 147-06.

## Self-Check: PASSED

- FOUND: `firestarter_app/tools/parse_devtest_issue.py` defines `NOT_REPORTED` and `_NOT_ATTRIBUTABLE`
- FOUND: `firestarter_app/tests/test_parse_devtest_issue.py` contains `test_render_diff_labels_a_populated_firmware_identity`, `test_render_diff_marks_an_absent_identity_not_attributable`, `test_render_diff_omits_hw_revision`, `test_render_diff_still_labels_n_agreeing_as_a_maintainer_decision_input`, `test_legacy_null_identity_body_still_parses_and_groups`, `test_unknown_marker_string_matches_the_report_model`, `test_parser_marker_strings_trip_no_forbidden_claim_pattern`
- FOUND: commit `ddd787a` in `firestarter_app` (`git log --oneline --all | grep ddd787a`)
- FOUND: commit `ec6182f` in `firestarter_app` (`git log --oneline --all | grep ec6182f`)
- FOUND: commit `9701209` in `firestarter_app` (`git log --oneline --all | grep 9701209`)

---
*Phase: 147-report-provenance-every-dev-test-report-names-its-firmware*
*Completed: 2026-08-18*
