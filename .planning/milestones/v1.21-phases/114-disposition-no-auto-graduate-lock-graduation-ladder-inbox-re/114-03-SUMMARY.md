---
phase: 114-disposition-no-auto-graduate-lock-graduation-ladder-inbox-re
plan: 03
subsystem: testing
tags: [ast, static-analysis, ci-gate, pytest, disposition, no-auto-graduate, dev-test]

# Dependency graph
requires:
  - phase: 114-01
    provides: report-side `ladder_state` derivation on `DbDiff` (`diagnostic_report.py::build_db_diff`) — a scan target of this checker
  - phase: 114-02
    provides: "tools/parse_devtest_issue.py (INBOX-01 triage parser) — the second scan target of this checker"
provides:
  - "tools/check_no_community_support_status_write.py — AST-based CI gate proving no code path in the report/parse path writes a chip's support_status (DISP-01)"
  - "tests/test_check_no_community_support_status_write.py — mandatory anti-hollow paired pytest (7 tests: clean-baseline / 2 planted-violation legs / fail-closed-missing-target / 2 seam-isolation legs / PASS-names-both-files anti-skip)"
affects: []

# Tech tracking
tech-stack:
  added: []
  patterns: ["AST-based CI checker (ast.parse + ast.NodeVisitor) gated by a subprocess-invoking pytest with env-override negative fixtures — the anti-hollow gate pattern, now applied to a WRITE-detection (not call/dict-literal) deny rule"]

key-files:
  created:
    - firestarter_app/tools/check_no_community_support_status_write.py
    - firestarter_app/tests/test_check_no_community_support_status_write.py
  modified: []

key-decisions:
  - "Deny rule: an ast.Assign/AnnAssign/AugAssign whose target is an ast.Attribute with attr==\"support_status\" OR an ast.Subscript with an ast.Constant slice exactly equal to \"support_status\" (exact-string match distinguishes it from the near-name current_support_status field/key)."
  - "Both scan targets (diagnostic_report.py, parse_devtest_issue.py) are MANDATORY — unlike SAFE-03's optional third-leg tolerance, a missing-target check runs BEFORE the scan loop and fails closed immediately if either is absent, rather than only checking 'scanned nothing' after the fact (stronger than the SAFE-03 template because neither leg here is ever legitimately optional)."
  - "eprom_info.py and build_db.py are deliberately excluded from scan targets (not whitelisted by value) — build_db.py is the sole allowed write locus; eprom_info.py:150's combined_data[\"support_status\"] = ss is a display-dict copy of a value already read from the DB, not report-parsing-driven, and is out of scope by construction."
  - "Wired via pytest tests/ only — no .github/workflows/ci.yml edit (mirrors the SAFE-03 convention; CI's existing pytest tests/ --cov-fail-under=70 step picks up the new test file automatically)."

patterns-established:
  - "Write-target AST deny rule (as opposed to SAFE-03's call-site/dict-literal deny rule): visit_Assign/visit_AnnAssign/visit_AugAssign checking the TARGET expression's Attribute.attr or Subscript.slice.value against a single exact-string key — reusable for any future 'no code path may write field X' invariant."

requirements-completed: [DISP-01]

coverage:
  - id: D1
    description: "AST checker tools/check_no_community_support_status_write.py scans diagnostic_report.py + parse_devtest_issue.py and exits 0 (PASS naming both files) when no support_status WRITE exists in either module"
    requirement: "DISP-01"
    verification:
      - kind: unit
        ref: "tests/test_check_no_community_support_status_write.py::test_checker_exits_zero_on_clean_source and ::test_checker_pass_line_names_both_scanned_files"
        status: pass
    human_judgment: false
  - id: D2
    description: "Checker exits non-zero with FAIL: when a support_status write is planted into either scanned target via the FIRESTARTER_DISP01_REPORT / FIRESTARTER_DISP01_PARSER env-override fixtures (anti-hollow)"
    requirement: "DISP-01"
    verification:
      - kind: unit
        ref: "tests/test_check_no_community_support_status_write.py::test_checker_exits_nonzero_on_planted_report_violation and ::test_checker_exits_nonzero_on_planted_parser_violation"
        status: pass
    human_judgment: false
  - id: D3
    description: "Checker fails closed (exit 1) when a scan target is missing/nonexistent, and env-override seam isolation proves a CLEAN fixture through the same seam still passes"
    requirement: "DISP-01"
    verification:
      - kind: unit
        ref: "tests/test_check_no_community_support_status_write.py::test_checker_fails_closed_on_missing_target, ::test_env_override_report_points_at_clean_fixture_still_passes, ::test_env_override_parser_points_at_clean_fixture_still_passes"
        status: pass
    human_judgment: false
  - id: D4
    description: "Checker does not false-positive on the current_support_status near-name field/key or on any read-only support_status access (db.get_eprom_config, .get(...)) in the real, unmodified source"
    requirement: "DISP-01"
    verification:
      - kind: unit
        ref: "tests/test_check_no_community_support_status_write.py::test_checker_exits_zero_on_clean_source (real source contains current_support_status + .get(\"support_status\", ...) reads throughout)"
        status: pass
    human_judgment: false

# Metrics
duration: 30min
completed: 2026-07-03
status: complete
---

# Phase 114 Plan 03: DISP-01 No-Auto-Graduate Machine Lock Summary

**AST-based CI gate (`tools/check_no_community_support_status_write.py`) proves no code path in the report/parse path writes a chip's `support_status`, mirroring SAFE-03's anti-hollow checker+pytest pairing with a write-target deny rule instead of a call-site/dict-literal deny rule.**

## Performance

- **Duration:** ~30 min
- **Started:** 2026-07-03T19:20:00Z (approx)
- **Completed:** 2026-07-03T19:33:41Z
- **Tasks:** 2 (Task 1 `tdd="true"`, Task 2 `type="auto"`)
- **Files modified:** 2 (both new files, submodule `firestarter_app/`)

## Accomplishments

- Created `firestarter_app/tools/check_no_community_support_status_write.py`: an `ast.NodeVisitor`-based checker (fresh AST walk, mirroring `check_devtest_orchestrator.py`'s tool shape) that denies any `ast.Assign`/`ast.AnnAssign`/`ast.AugAssign` whose target resolves to `support_status` — an `ast.Attribute` with `attr == "support_status"` or an `ast.Subscript` with an `ast.Constant` slice exactly equal to `"support_status"`. Scans `firestarter/diagnostic_report.py` and `tools/parse_devtest_issue.py` (the report/parse path) via `FIRESTARTER_DISP01_REPORT` / `FIRESTARTER_DISP01_PARSER` env-override seams; deliberately excludes `eprom_info.py` (display-dict copy, Pitfall 1) and `tools/build_db.py` (the sole allowed write locus).
- Fail-closed design stronger than the SAFE-03 template: both scan targets are mandatory (neither is ever legitimately absent in production), so a missing-target check runs BEFORE the AST walk and fails closed immediately if either is absent — catching both the "empty scan" case and the "one target silently skipped" tampering case (T-114-07) in a single guard.
- Verified the checker exits 0 with a `PASS:` line naming both `../firestarter/diagnostic_report.py` and `parse_devtest_issue.py` on the real, post-114-01/114-02 source — confirming zero `support_status` writes today and no false positive on `build_db_diff`'s `db.get_eprom_config` read or the `current_support_status` dataclass field / dict key (exact-string match against `"support_status"` excludes the 4-character-longer near-name by construction).
- Created `firestarter_app/tests/test_check_no_community_support_status_write.py`: 7 tests mirroring `test_check_devtest_orchestrator.py`'s `_FA_DIR = Path(__file__).parent.parent` cwd-independence idiom and subprocess-driving `_run_checker` helper. Test 1 is the clean-pass baseline. Tests 2–3 are the anti-hollow planted-violation proofs (a real `chip["support_status"] = "community-reported"` write injected via `FIRESTARTER_DISP01_REPORT`, and a `diff["support_status"] = "community-confirmed"` write injected via `FIRESTARTER_DISP01_PARSER`) — both real subprocess-level violations, never in-process synthetics. Test 4 proves fail-closed behavior on a missing scan target. Tests 5–6 are env-override seam-isolation sanity checks (a CLEAN fixture through each seam still passes). Test 7 asserts the clean-baseline PASS line names both scanned files (anti-skip, the v1.12 hollow-GATE-03 lesson).
- Ran `ruff check` + `ruff format --check` on both new files (one auto-format pass applied and re-verified).
- Ran the full `firestarter_app` test suite: 3 pre-existing failures unrelated to this plan (`test_audit_coverage_matrix.py::test_golden_file_matches` — documented stale golden per project memory; `test_characterization.py::test_no_programmer_found_read`/`_erase` — documented live-board-attached env artifact per project memory), all other tests pass including the new 7.
- Confirmed `grep -rn "check_no_community_support_status_write" firestarter_app/.github/workflows/` returns nothing — the gate is wired ONLY through `pytest tests/`, no dedicated CI YAML step (Pitfall 2).

## Task Commits

Both tasks committed atomically inside the `firestarter_app` submodule (branch `v1.21-community-chip-validation-command`):

1. **Task 1 — RED: failing anti-hollow tests** — `4e6a6d7` (test) — all 7 tests fail because the checker module does not exist yet.
2. **Task 1 — GREEN: AST checker implementation** — `dcd2986` (feat) — `tools/check_no_community_support_status_write.py`; all 7 tests now pass.

**Plan metadata:** this commit (docs: complete plan) — committed in the meta repo, not the submodule.

_Note: Task 2 ("Anti-hollow paired subprocess test for the DISP-01 checker") specified the exact same test-file deliverable and acceptance criteria (clean-baseline, planted-violation via `tmp_path`, PASS-line-names-both-files anti-skip, clean-fixture-through-seam) that Task 1's TDD `tdd="true"` RED phase already had to satisfy in full to drive the checker's implementation — the full 7-test suite (including both seam-isolation legs and the anti-skip assertion) was written in the RED commit and never needed a second, separate commit. This mirrors the 109-03 precedent ("a checker without its negative-fixture test is an incomplete deliverable; there is no meaningful intermediate state to commit between them") — see `109-03-SUMMARY.md` §Decisions Made. Task 2 is therefore verified-complete by the two Task-1 commits above; no additional commit was made._

## TDD Gate Compliance

- RED gate: `4e6a6d7` (`test(114-03): add failing anti-hollow tests for DISP-01 checker (RED)`) — confirmed all 7 tests failed (subprocess `FileNotFoundError` on the not-yet-existing checker module) before implementation.
- GREEN gate: `dcd2986` (`feat(114-03): add DISP-01 AST checker for support_status writes (GREEN)`) — confirmed all 7 tests pass after implementation.
- No REFACTOR commit was needed (implementation required no post-GREEN cleanup beyond the `ruff format` auto-fix, applied before the GREEN commit).

## Files Created/Modified

- `firestarter_app/tools/check_no_community_support_status_write.py` — AST-based DISP-01 write-detector checker (new, ~230 lines)
- `firestarter_app/tests/test_check_no_community_support_status_write.py` — paired anti-hollow pytest, 7 tests (new, ~232 lines)

## Decisions Made

- **Combined Task 1 (tdd) + Task 2 (test-suite) into a single RED/GREEN pairing**: since a checker without its full anti-hollow test suite is an incomplete deliverable (D-05 non-negotiable), the RED phase wrote the complete 7-test suite (covering both Task 1's and Task 2's acceptance criteria) rather than a partial subset later extended by a separate Task 2 commit. See Task Commits note above.
- **Mandatory-both-targets fail-closed design**: rather than mirroring SAFE-03's "if not scanned at all → FAIL" (which tolerates an optional third leg), this checker explicitly checks each of the two MANDATORY targets for existence before scanning, failing closed if either alone is missing — a stronger anti-hollow guarantee appropriate to this checker's shape (both legs are always-present in production, unlike SAFE-03's discretionary handler leg).
- **Exact-string match (not substring/prefix) for the deny target**: `target.slice.value == "support_status"` (not `"support_status" in target.slice.value`) so `current_support_status` can never accidentally match — verified directly against the real `diagnostic_report.py`/`parse_devtest_issue.py` source, which both use `current_support_status` extensively.

## Deviations from Plan

None — plan executed exactly as written, with one process consolidation (documented above under Decisions Made / Task Commits note): Task 2's deliverable and acceptance criteria were satisfied entirely within Task 1's TDD RED/GREEN cycle rather than via a separate subsequent commit, mirroring the 109-03 SAFE-03 precedent for checker+test pairings.

## Known Stubs

None.

## Threat Flags

None — this plan adds a static-analysis CI gate only; it introduces no new network endpoint, auth path, file-access pattern, or schema change at a trust boundary.

## Issues Encountered

None. `ruff format` required one auto-reformat pass on `check_no_community_support_status_write.py` (line-wrapping of a long `os.path.join` call); re-verified clean and re-ran the checker + pytest suite to confirm the reformat did not change behavior.

## User Setup Required

None — no external service configuration required. No `ci.yml` changes were made (per D-05/Pitfall 2, the existing `pytest tests/ --cov-fail-under=70` step already picks up the new test file automatically).

## Next Phase Readiness

- DISP-01's machine-enforced contract is now live and build-failing: any future edit adding a `support_status` write to `diagnostic_report.py` or `parse_devtest_issue.py` will fail `pytest tests/` in CI.
- This closes Phase 114 Plan 03 and, with 114-01 (GRAD-01) and 114-02 (INBOX-01) already complete, closes all of Phase 114's three requirements (DISP-01, GRAD-01, INBOX-01).
- Phase 114 is the last phase in the v1.21 roadmap (108→114); milestone-close activities (beta cut, tag) remain operator-gated per standing policy.

---
*Phase: 114-disposition-no-auto-graduate-lock-graduation-ladder-inbox-re*
*Completed: 2026-07-03*

## Self-Check: PASSED
