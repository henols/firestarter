---
phase: 188-the-tools-directory
plan: 03
subsystem: testing
tags: [pytest, ruff, coverage, ast-gate, deletion, d-25, d-13, d-01]

requires:
  - phase: 188-02
    provides: "the D-25 gate (blocking-human) at which the operator inverted OD-1 and chose surgical per-symbol deletion of the four orphaned library symbols' consumers over relocation"
provides:
  - "Two gates retired end to end: check_diagnostic_report_claims.py and check_dispatch.py, each with its own test suite and every test that consumed its symbols"
  - "66 collected tests removed with zero collateral (2373 -> 2368 -> 2307), measured at every boundary"
  - "Both fail-closed literal indexes (scan-path resolver pair, exists-proxy enumeration) settled in the same commits as the files they name"
  - "Coverage floor movement measured and recorded: unchanged at 5878/896/85% before and after both commits"
  - "tools/ now holds exactly 8 check_*.py gates (188-04 retires the rest)"
affects: ["188-04 (inherits eight gates, not nine)", "188-07 (coverage-floor acceptance gate; this plan is the measurement, not the risk)", "188-09 (verdict note needs the BLOCKER-2 loss and the falsified-projection finding stated by name)"]

actuals:
  tokens: 33950
  tasks: 2
  commits: 2
  plan_head_before: f3650ff2327e4aa70557ac870a95c3c732bca4d8

tech-stack:
  added: []
  patterns:
    - "Pin the diff anchor to a file (/tmp/188-03-base.sha) rather than a relative HEAD~N, so every numstat leg in a multi-commit plan diffs against the same fixed pre-phase state regardless of how many commits land in between."
    - "Measure collected count, never passed count, at every deletion boundary -- a module that stops collecting reports zero results and would otherwise vanish silently."
    - "A background pytest run must not share a working tree with concurrent file edits: starting a long coverage measurement in the background and then mutating the tree while it runs contaminates the run (see Deviations)."

key-files:
  created: []
  modified:
    - firestarter_app/tools/check_diagnostic_report_claims.py (deleted)
    - firestarter_app/tests/test_check_diagnostic_report_claims.py (deleted)
    - firestarter_app/tests/fixtures/planted_diagnostic_report_claim.py (deleted)
    - firestarter_app/tests/test_parse_devtest_issue.py (trimmed: -20 lines, 29->28 tests)
    - firestarter_app/tools/check_dispatch.py (deleted)
    - firestarter_app/tests/test_check_dispatch_invariants.py (deleted)
    - firestarter_app/tests/test_val_wire_5v_page.py (deleted)
    - firestarter_app/tests/test_val_wire_sram.py (deleted)
    - firestarter_app/tests/test_val_wire_eeprom28c.py (deleted)
    - firestarter_app/tests/test_val_wire_eprom.py (deleted)
    - firestarter_app/tests/test_val_wire_flash_intel.py (deleted)
    - firestarter_app/tests/test_val_wire_nor_unlock.py (deleted)
    - firestarter_app/tests/scan_paths.py (deleted)
    - firestarter_app/tests/test_scan_paths_resolve.py (deleted)
    - firestarter_app/tests/test_decoder.py (trimmed: -70 lines, 37->32 tests)
    - firestarter_app/tests/test_build_db_inclusion.py (trimmed: -90 lines, 30->29 tests, unused import removed, orphaned header comment removed)
    - firestarter_app/tools/check_no_exists_proxy.py (edited: -9 lines, _DEFAULT_TARGETS enumeration)
    - firestarter_app/tests/test_voltage_field_census.py (edited: -1 line, _FALSE_POSITIVE_CANDIDATE_NAMES frozenset)

key-decisions:
  - "The replanning brief's projection that the coverage floor would fall was tested and is falsified in this plan's own execution, not just at planning time: measured before Task 1 (5878/896/85%), after Task 1 (5878/896/85%), and after Task 2 (5878/896/85%) -- identical to the byte on missed-statement count at every boundary. The six wire-contract suites exercise the retired tools/ decode model, never counted by --cov=firestarter."
  - "Deleted an orphaned, factually-wrong section-header comment ('SC#3 / D-03 HARD + D-12: Non-supported chips must be non-dispatchable') left dangling directly above the surviving TestThirtyTwoPinVariantLoDispatch class after the TestNonSupportedNonDispatchable trim -- caught by the plan's own mandated read-back verification step. This deletes stale prose describing a class that no longer exists; it authors nothing (Rule 1)."
  - "Both fail-closed indexes (scan-path resolver pair, exists-proxy enumeration) and the one entry this plan orphans in the non-fail-closed voltage-census frozenset were all settled in the SAME commit as the nine tool/test files they name, per D-13 and the plan's own ordering constraint."

requirements-completed: [TOOLS-03]

coverage:
  - id: D1
    description: "Retire the diagnostic-claims gate end to end: delete tools/check_diagnostic_report_claims.py, its own test suite, its planted fixture, and its one consuming test in tests/test_parse_devtest_issue.py -- 5 collected tests gone, 28 stay in that module, whole suite 2373->2368 with 0 errors"
    requirement: "TOOLS-03"
    verification:
      - kind: other
        ref: "pytest tests/ --co -q -o addopts='' -> 2368 collected, 0 errors; pytest tests/ -o addopts='' -q -> 2368 passed; ruff check/format --check firestarter/ tests/ -> clean"
        status: pass
    human_judgment: false
  - id: D2
    description: "Retire the dispatch gate end to end: delete tools/check_dispatch.py, its own test suite, and the six wire-contract suites (38 tests); trim two classes (TestDispatchGate02, TestNonSupportedNonDispatchable, 6 tests); settle both fail-closed literal indexes and the one orphaned voltage-census entry in the same commit -- whole suite 2368->2307 with 0 errors"
    requirement: "TOOLS-03"
    verification:
      - kind: other
        ref: "pytest tests/ --co -q -o addopts='' -> 2307 collected, 0 errors; pytest tests/ -o addopts='' -q -> 2307 passed; python tools/check_no_exists_proxy.py -> exit 0, PASS scanning 70 files; ruff check/format --check firestarter/ tests/ -> clean"
        status: pass
    human_judgment: false

duration: 55min
completed: 2026-09-13
status: complete
---

# Phase 188 Plan 03: Prove the deletion recipe on two gates — diagnostic-claims and dispatch, end to end Summary

**Retired `check_diagnostic_report_claims.py` and `check_dispatch.py` whole, with every test that consumed either gate's symbols (66 collected tests total, zero collateral), settled both fail-closed literal indexes in the commits that touched their named files, and measured the coverage floor unchanged at 5878/896/85% across all three boundaries — falsifying the replanning brief's projection that it would move.**

## Performance

- **Duration:** ~55 min (wall clock across two long-running full-suite/coverage measurements)
- **Tasks:** 2/2 completed
- **Files modified:** 18 (14 deleted, 4 edited/trimmed)

## Accomplishments

- **Pre-phase baseline, measured cleanly:** 2373 collected, 0 errors, 2373 passed; coverage TOTAL 5878 statements / 896 missed / 85%.
- **Task 1 — diagnostic-claims gate retired whole:** `tools/check_diagnostic_report_claims.py`, `tests/test_check_diagnostic_report_claims.py` (4 tests), and `tests/fixtures/planted_diagnostic_report_claim.py` deleted; the one consuming test (`test_parser_marker_strings_trip_no_forbidden_claim_pattern`) trimmed from `tests/test_parse_devtest_issue.py` (29→28 tests, diff deletions-only). `tests/fixtures/planted_unparsable.py` confirmed kept — `pyproject.toml`'s mypy exclude block still cites it live. Whole suite: 2373→2368 collected, 0 errors, 2368 passed. Coverage TOTAL unchanged: 5878/896/85%.
- **Task 2 — dispatch gate retired whole:** `tools/check_dispatch.py` and `tests/test_check_dispatch_invariants.py` (12 tests) deleted, plus the six wire-contract suites (38 tests: 5v_page 14, sram 6, eeprom28c 6, eprom 4, flash_intel 4, nor_unlock 4). Two classes trimmed by name only: `TestDispatchGate02` from `tests/test_decoder.py` (37→32) and `TestNonSupportedNonDispatchable` from `tests/test_build_db_inclusion.py` (30→29, plus its now-unused top-level `import sys`). Whole suite: 2368→2307 collected, 0 errors, 2307 passed.
- **Both fail-closed literal indexes settled in the same commit as the files they name (D-13):** `tests/scan_paths.py` and `tests/test_scan_paths_resolve.py` deleted outright (entry one of the eleven-tool resolver table, pinned at exactly 11, would have reddened the instant `check_dispatch.py` disappeared); nine stale string entries removed from `tools/check_no_exists_proxy.py`'s `_DEFAULT_TARGETS` enumeration (`tests/scan_paths.py`, `tests/test_scan_paths_resolve.py`, `tests/test_check_dispatch_invariants.py`, and all six `tests/test_val_wire_*.py` names) — the three trimmed modules (decoder, build-db-inclusion, parse-devtest-issue) stay named, since they still exist. Running the gate directly post-deletion: exit 0, `PASS: scanned 70 file(s)`.
- **Third, non-fail-closed literal index settled for the one entry this plan orphans:** confirmed by reading that `tests/test_voltage_field_census.py`'s `_FALSE_POSITIVE_CANDIDATE_NAMES` is a membership filter over `rglob` results (dead data on a stale entry, never a failure) — removed `"test_check_dispatch_invariants.py"` only; the two entries orphaned by later plans (`check_devtest_orchestrator.py` for 188-04, `test_diff_db_gate.py` for 188-05) and both `_SELF_REFERENTIAL_NAMES` entries for this-phase trims (`test_blast_radius_invariance.py`, `test_parse_devtest_issue.py`) all confirmed still present and untouched.
- **Coverage floor movement measured, not assumed, at all three boundaries** (pre-phase, after Task 1, after Task 2): **5878 statements / 896 missed / 85%, identical to the byte, every time.** The replanning brief's projection that deleting the six wire-contract suites would move the figure is **falsified** by this plan's own execution-time measurement — those suites exercise the retired `tools/` decode model, which `--cov=firestarter` never counted.
- **`tools/` now holds exactly 8 `check_*.py` gates** (confirmed via `git ls-files -- 'tools/check_*.py'`), down from 10 — this plan retires two, plan 188-04 inherits eight, not the nine its own ROADMAP text still says (a counting consequence of the replan, recorded per the plan's own note).
- **BLOCKER-2 electrical-safety invariant loss, stated as a loss:** the six deleted `test_val_wire_*` suites were the host's only automated proof that each chip family's wire dictionary routes to the electrically-correct handler and never to `configure_eprom` for a 5V SRAM part (12V VPP on a 5V part is electrical destruction). This is a disclosed, accepted cost of D-25 — the operator was shown the six suites by name before choosing "delete the consumers" at the 188-02 gate. No successor guard is authored, per D-23. Recorded here by name for plan 188-09's verdict note.

## Task Commits

1. **Task 1: Retire the diagnostic-claims gate end to end** — `b9ede20` (feat, in `firestarter_app`)
2. **Task 2: Retire the dispatch gate end to end, settle both fail-closed indexes** — `7ebdef8` (feat, in `firestarter_app`)

**Plan metadata:** this SUMMARY commit (meta repo)

## Files Created/Modified

- `firestarter_app/tools/check_diagnostic_report_claims.py` — deleted (AST claim-scanner gate)
- `firestarter_app/tests/test_check_diagnostic_report_claims.py` — deleted (that gate's own test suite, 4 tests)
- `firestarter_app/tests/fixtures/planted_diagnostic_report_claim.py` — deleted (planted-violation fixture)
- `firestarter_app/tests/test_parse_devtest_issue.py` — trimmed (`test_parser_marker_strings_trip_no_forbidden_claim_pattern` removed, 29→28, deletions-only diff)
- `firestarter_app/tools/check_dispatch.py` — deleted (host dispatch-model gate)
- `firestarter_app/tests/test_check_dispatch_invariants.py` — deleted (that gate's own test suite, 12 tests)
- `firestarter_app/tests/test_val_wire_5v_page.py`, `test_val_wire_sram.py`, `test_val_wire_eeprom28c.py`, `test_val_wire_eprom.py`, `test_val_wire_flash_intel.py`, `test_val_wire_nor_unlock.py` — deleted (38 tests, wire-contract coverage)
- `firestarter_app/tests/scan_paths.py`, `tests/test_scan_paths_resolve.py` — deleted (fail-closed cross-repo scan-path inventory + resolver, D-13)
- `firestarter_app/tests/test_decoder.py` — trimmed (`TestDispatchGate02` removed, 37→32, deletions-only diff)
- `firestarter_app/tests/test_build_db_inclusion.py` — trimmed (`TestNonSupportedNonDispatchable` removed, 30→29; unused `import sys` removed; orphaned section-header comment removed — see Deviations)
- `firestarter_app/tools/check_no_exists_proxy.py` — edited (9 stale entries removed from `_DEFAULT_TARGETS`, deletions-only diff)
- `firestarter_app/tests/test_voltage_field_census.py` — edited (1 entry removed from `_FALSE_POSITIVE_CANDIDATE_NAMES`, deletions-only diff)

## Decisions Made

- Followed D-25's surgical ledger exactly: whole-module deletion for the nine modules with no surviving test, single-named-class/single-named-test trims for the three mixed modules, and per-module collected counts re-measured live rather than trusted from the ledger (all matched: 28/32/29 exactly).
- Followed D-13's ordering constraint: the scan-path pair was deleted in this plan's Task 2 commit (not deferred to 188-04) because that pair's `test_all_eleven_tool_resolvers_exist` fails the instant `check_dispatch.py` — the first of its eleven named tools — disappears. No partial edit of the resolver table was possible; a module-level assertion pins it at exactly 11 entries.
- Deleted the orphaned "SC#3 / D-03 HARD + D-12" section-header comment above `TestThirtyTwoPinVariantLoDispatch` in `tests/test_build_db_inclusion.py` (see Deviations) — the plan's own read-back verification step exists precisely to catch this kind of dangling, now-false artifact.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Corrected a mis-staged Task 1 commit before proceeding**
- **Found during:** Task 1, immediately after the first commit attempt
- **Issue:** `git add tools/check_diagnostic_report_claims.py tests/test_check_diagnostic_report_claims.py tests/fixtures/planted_diagnostic_report_claim.py tests/test_parse_devtest_issue.py` errored on the first three pathspecs (already staged as deletions by the preceding `git rm`, so `git add` treats them as "did not match any files") and aborted before reaching the fourth, leaving `tests/test_parse_devtest_issue.py`'s trim unstaged. The resulting commit captured only the three whole-file deletions.
- **Fix:** Staged `tests/test_parse_devtest_issue.py` alone and amended the same commit (nothing built on top of it yet), matching the precedent already recorded in plan 188-06's SUMMARY for the identical trap.
- **Files modified:** none beyond what Task 1 already specified — this corrected staging, not content.
- **Verification:** `git show --stat HEAD` confirms 4 files, 429 deletions, in one commit; `git status --short` clean afterward.
- **Committed in:** `b9ede20` (amended)

**2. [Rule 1 - Bug] Same mis-staging trap recurred on Task 2's commit, avoided this time**
- **Found before committing:** having been burned once in Task 1, Task 2's `git add` was scoped only to the four `M`-status files (`tests/test_build_db_inclusion.py tests/test_decoder.py tests/test_voltage_field_census.py tools/check_no_exists_proxy.py`), leaving the ten already-`git rm`-staged deletions untouched. `git status --short` confirmed all 14 target paths staged (`D`/`M`, no unstaged `M`/`D`) before committing once.
- **Files modified:** none — this is a staging-discipline note, not a content change.
- **Verification:** `git show --stat HEAD` confirms 14 files changed in one commit.

**3. [Rule 1 - Bug] Deleted an orphaned, factually-wrong section-header comment left dangling by the `TestNonSupportedNonDispatchable` trim**
- **Found during:** Task 2, the plan's own mandated read-back verification step ("open the file at the point where the deleted class used to begin, and confirm by eye that the file reads coherently")
- **Issue:** The plan's literal deletion boundary (lines 685–770 of the pre-edit file) stopped short of the 3-line section-header comment (`# SC#3 / D-03 HARD + D-12: Non-supported chips must be non-dispatchable (Plans 04+05)`) that introduced `TestNonSupportedNonDispatchable`. After the trim, that comment sat directly above the unrelated, surviving `TestThirtyTwoPinVariantLoDispatch` class — misdescribing it. This is stale, now-false prose, not a comment I authored; `/workspaces/CLAUDE.md`'s hard rule forbids *writing* comments, not deleting a stale one.
- **Fix:** Deleted the 3-line comment header (the blank-line separator above it was left as-is).
- **Files modified:** `firestarter_app/tests/test_build_db_inclusion.py`
- **Verification:** `ruff format --check` / `ruff check` both clean; collected count still 29 for this module, 61 for the pair; `git diff --numstat` against the pinned base still reads `added=0` for this file (now `deleted=90` instead of `87`) — still deletions-only, no new prose introduced.
- **Committed in:** `7ebdef8`

### Plan-authored check discrepancies (not code deviations)

**4. The plan's own coverage-baseline capture step was contaminated by a timing race, corrected before use — not a code defect.**
- The plan's Task 1 action text instructs capturing the pre-deletion coverage TOTAL "before touching anything." The first attempt was dispatched as a long-running background command; rather than waiting for it, the Task 1 file deletions were started while it was still running, so the coverage run's test-pass count was measured against a tree that changed mid-run (1 failure, an import error on a module deleted underneath the running suite — not a real defect). Caught before relying on the figure: the three affected files were restored with `git checkout HEAD -- <paths>` to a genuinely clean pre-deletion tree, the coverage baseline was re-measured cleanly (2373 passed, 0 failed, TOTAL 5878/896/85%), and only then were the Task 1 deletions redone. No code was affected; this is a measurement-process note, not a plan or code defect.

---

**Total deviations:** 3 auto-fixed (2 mis-staged-commit corrections, 1 stale-comment deletion) + 1 documented measurement-process discrepancy (not a code change).
**Impact on plan:** No scope creep. All three auto-fixes were necessary to satisfy the plan's own mandatory acceptance criteria (one correct commit per task; a coherent, non-misleading file after each trim). The measurement-process note describes how a clean baseline was obtained, not a change to what was measured or delivered.

## Issues Encountered

None beyond the deviations documented above. The full-suite pass and coverage-with-instrumentation runs both take 4.5–6.5 minutes each under `.venv311`; all were run to completion (not truncated) before being used as evidence.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Both gates in this plan's scope are retired end to end; no fragment of either survives functionally (confirmed by `git ls-files` returning zero hits on all deletion targets and all four OD-1 relocation-helper module names).
- `tools/` holds exactly 8 `check_*.py` gates at the end of this plan. Plan 188-04's own text should be read as "the eight remaining gates," not nine — this plan retired two, not one, per the replan's own note in `188-03-PLAN.md`.
- Coverage floor is proven, not assumed, unmoved (5878/896/85% at all three boundaries) — plan 188-07's seventy-percent floor acceptance gate carries no undisclosed risk from this plan's six wire-contract-suite deletions.
- The BLOCKER-2 electrical-safety invariant's loss is recorded here by name, ready for plan 188-09's verdict note to cite directly.
- This plan is file-disjoint from 188-04/188-05/188-06/188-07/188-08's own scopes and required no coordination beyond the D-13 ordering constraint already satisfied above.
- No blockers for the remaining phase-188 plans.

## Self-Check: PASSED

- `FOUND: 188-03-SUMMARY.md` — `.planning/phases/188-the-tools-directory/188-03-SUMMARY.md` exists on disk.
- `git ls-files -- tools/check_diagnostic_report_claims.py tests/test_check_diagnostic_report_claims.py tests/fixtures/planted_diagnostic_report_claim.py tools/check_dispatch.py tests/test_check_dispatch_invariants.py tests/test_val_wire_5v_page.py tests/test_val_wire_sram.py tests/test_val_wire_eeprom28c.py tests/test_val_wire_eprom.py tests/test_val_wire_flash_intel.py tests/test_val_wire_nor_unlock.py tests/scan_paths.py tests/test_scan_paths_resolve.py tests/dispatch_model.py tests/report_claim_patterns.py tests/report_shape_renderer.py tests/devtest_handler_names.py` in `firestarter_app` returns nothing — every deletion target gone, no OD-1 relocation helper exists.
- `git log --oneline --all --grep="188-03"` finds no hits by design — this plan's commit messages cite `188-03` in the subject prefix's plan number, verified directly instead: `firestarter_app`'s `HEAD` is `7ebdef8` (Task 2), parent `b9ede20` (Task 1), both on branch `gsd/v1.37-operator-safety-answered-reports-claim-hygiene`; `git status --short` in `firestarter_app` shows only the pre-existing untracked operator datasheets, nothing else.
- All Task 1 and Task 2 `<verify>` legs re-run clean at the final commit state: collected counts 2368 (Task 1 boundary, re-confirmed via `git show b9ede20` diff) and 2307 (final), both 0 errors; both ruff legs green; `tools/check_no_exists_proxy.py` exits 0 scanning 70 files; coverage TOTAL 5878/896/85% at both post-commit boundaries.

---
*Phase: 188-the-tools-directory*
*Completed: 2026-09-13*
