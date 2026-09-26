---
phase: 178-fault-attribution-the-two-axis-vocabulary
plan: 01
subsystem: dev-test-diagnostics
tags: [chip_test, diagnostic_report, submit, cli_handlers, status-axis, ocp-test-validation]

# Dependency graph
requires:
  - phase: 177-evidence-gated-fingerprint-read-back
    provides: the fingerprint gate this phase's fault-mode reasoning consumes, and the frozen report-shape corpus / dedup_fingerprint invariance oracle (Phase 174) this plan re-verifies unmoved
provides:
  - "STATUS_COMPLETE/STATUS_ERROR/STATUS_SKIP vocabulary and StepResult.status field in firestarter/chip_test.py"
  - "run_status(results) run-level fold, and DiagnosticReport.run_status carried + exported at schema 1.8"
  - "the transport-fault exception arm re-pointed to verdict=SKIPPED/status=ERROR instead of a chip BAD"
  - "three widened consumers: submit.overall_verdict (title), build_db_diff (ladder), _dev_test_exit_code (exit code), all status-axis-first"
affects: [178-02-attr03-attr04-ordering-and-concurrency-edges, 178-03-frozen-shape-registration, 178-04-attr06-rail-reading-disclosure]

# Actuals (#2632) -- pairs with the plan's estimate to calibrate future estimates.
actuals:
  tokens: 18800
  tasks: 2
  commits: 3

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "OCP Test & Validation two-axis vocabulary: a run-validity `status` axis (COMPLETE/ERROR/SKIP) held separately from the existing chip-verdict `verdict` axis, additive and excluded from dedup_fingerprint by construction"
    - "bare triple-quoted string-literal-above-the-constant/field idiom for new rationale, in place of `#` comments (project hard rule)"

key-files:
  created: []
  modified:
    - firestarter_app/firestarter/chip_test.py
    - firestarter_app/firestarter/diagnostic_report.py
    - firestarter_app/firestarter/submit.py
    - firestarter_app/firestarter/cli_handlers.py
    - firestarter_app/tests/test_dev_test_cmd.py
    - firestarter_app/tests/test_chip_test_sdp_leg.py
    - firestarter_app/tests/test_blast_radius_invariance.py
    - firestarter_app/tests/test_diagnostic_report.py
    - firestarter_app/tests/test_submit.py
    - firestarter_app/tests/fixtures/reports/*.json (17 regenerated snapshots)

key-decisions:
  - "Followed the plan's D-01..D-16 exactly: SKIPPED/ERROR (not marginal/NA/OK) for a transport fault, status excluded from dedup_fingerprint by writing no parts.append line, and the three consumers widened status-axis-first ahead of their verdict folds."
  - "Deleted (rather than edited) the pre-existing `#` comment on the transport-arm exception handler instead of leaving it stale about the old BAD verdict -- editing it in place would have added `#`-prefixed diff lines and violated the plan's zero-added-comment gate."
  - "All new rationale (the STATUS_* vocabulary block, the run_status field docstring, the build_db_diff ladder guard, submit._TITLE_VERDICT_HARNESS, and test_chip_test_sdp_leg.py's _EXPECTED_PRECEDENCE_MATRIX note) uses the bare-string-literal-above-the-declaration idiom already shipped in this tree, never a `#` comment."
  - "Included the two SCHEMA_VERSION-pin test repairs (test_diagnostic_report.py) and one call-site repair (test_dev_test_cmd.py's _dev_test_exit_code signature widening) in Task 1's own commit as Rule-1 auto-fixes, since Task 1's own edits broke them immediately and leaving them red would have made the commit self-inconsistent."
  - "Proved Task 2's four status-axis-dependent new tests non-vacuous by running them against a scratch git worktree checked out at the pre-Task-1 commit (removed afterward) and confirming each fails there (ImportError or AssertionError) before confirming green against the current tree."

patterns-established:
  - "Pattern: status-axis-first guard ahead of a verdict fold, read via `getattr(r, \"status\", STATUS_COMPLETE)` so duck-typed/legacy result objects without the field default safely to COMPLETE."

requirements-completed: [ATTR-01, ATTR-02, ATTR-03, ATTR-04]

coverage:
  - id: D1
    description: "A transport-faulted step reports a status-axis value (ERROR) distinct from the chip-verdict axis (SKIPPED) -- never a chip BAD -- and the destructive-write gate still closes"
    requirement: "ATTR-01"
    verification:
      - kind: unit
        ref: "tests/test_dev_test_cmd.py#TestLaunderingRoutesR1R2SyntheticChipId::test_r2_transport_error_during_id_check_closes_gate_and_renders_notrun"
        status: pass
      - kind: unit
        ref: "tests/test_chip_test_sdp_leg.py#test_serial_timeout_degrades_one_step"
        status: pass
      - kind: unit
        ref: "tests/test_chip_test_sdp_leg.py#test_hardware_error_degrades_one_step"
        status: pass
      - kind: e2e
        ref: ".planning/phases/178-fault-attribution-the-two-axis-vocabulary/evidence/178-01-tracer-end-to-end.txt (id_verdict=SKIPPED, id_status=ERROR, gate_closes=True, sdp_lock_calls=0)"
        status: pass
    human_judgment: false
  - id: D2
    description: "The overall verdict and the auto-generated issue title reflect the status-axis outcome (titles INCONCLUSIVE (harness), never FAIL), and the exit code is floored at 2 for a status-ERROR run"
    requirement: "ATTR-01"
    verification:
      - kind: unit
        ref: "tests/test_submit.py#test_overall_verdict_error_status_is_inconclusive_harness"
        status: pass
      - kind: unit
        ref: "tests/test_submit.py#test_build_title_for_a_transport_fault_is_not_fail"
        status: pass
      - kind: e2e
        ref: "tests/test_dev_test_cmd.py#TestLaunderingRoutesR1R2SyntheticChipId::test_transport_fault_exits_two_and_titles_inconclusive_harness"
        status: pass
    human_judgment: false
  - id: D3
    description: "The status axis is additive, excluded from dedup_fingerprint's hash input by construction, and introduces no sixth verdict value -- all 17 frozen report-shape hashes stay unmoved"
    requirement: "ATTR-04"
    verification:
      - kind: unit
        ref: "tests/test_blast_radius_invariance.py (17-shape FROZEN_HASHES suite + test_committed_snapshot_matches_a_fresh_regeneration x17)"
        status: pass
      - kind: e2e
        ref: ".planning/phases/178-fault-attribution-the-two-axis-vocabulary/evidence/178-01-tracer-end-to-end.txt (hash_unmoved_across_status=True, stale_frozen=, parts_append_count=3)"
        status: pass
    human_judgment: false
  - id: D4
    description: "A status-ERROR run's ladder lands on the inconclusive disposition (never community-reported), and the run still offers the submit/filing prompt -- is_submittable and the confirm flow are untouched"
    requirement: "ATTR-03"
    verification:
      - kind: unit
        ref: "tests/test_diagnostic_report.py#test_error_run_status_routes_the_ladder_to_inconclusive"
        status: pass
      - kind: e2e
        ref: ".planning/phases/178-fault-attribution-the-two-axis-vocabulary/evidence/178-01-tracer-end-to-end.txt (ladder_state_empty=True, ladder_inconclusive=True, still_submittable=True)"
        status: pass
    human_judgment: false

duration: 45min
completed: 2026-09-06
status: complete
---

# Phase 178 Plan 01: Fault Attribution -- the Two-Axis Vocabulary Summary

**A transport-faulted `dev test` step now reports `verdict: SKIPPED` / `status: ERROR` instead of spending a chip's `BAD` on a half-seated cable, folding to `run_status: ERROR`, an `INCONCLUSIVE (harness)` title, and exit code 2 -- with all 17 frozen dedup-fingerprint hashes measured unmoved.**

## Performance

- **Duration:** ~45 min
- **Completed:** 2026-09-06T12:08:11Z
- **Tasks:** 2 (Task 1: tracer, Task 2: consumer-widening behaviour tests)
- **Files modified:** 26 (4 production modules, 5 test modules, 17 regenerated snapshot fixtures)

## Accomplishments

- Added the `STATUS_COMPLETE`/`STATUS_ERROR`/`STATUS_SKIP` vocabulary (OCP Test & Validation's own field name, adopted by name only -- no `ocptv` package, no new runtime dependency) and an additive `StepResult.status` field, kept out of `dedup_fingerprint` by construction.
- Re-pointed the `(SerialError, HardwareOperationError)` transport-fault arm in `chip_test.py` from `verdict=VERDICT_BAD` to `verdict=VERDICT_SKIPPED, status=STATUS_ERROR` -- the destructive-write gate (`_id_step_closes_gate`) still closes, unchanged, and the fault reason still renders on every surface.
- Added `run_status(results)` (module-level fold) and `DiagnosticReport.run_status` (carried, exported at schema 1.8), and widened the three D-04 consumers -- `submit.overall_verdict` (titles `INCONCLUSIVE (harness)`), `build_db_diff` (ladder guard lands on inconclusive, never community-reported), and `_dev_test_exit_code` (a second non-verdict precedence candidate, exit 2) -- all status-axis-first, ahead of their existing verdict folds.
- Repaired the three pre-existing tests that pinned `BAD` on the transport path forward to `SKIPPED`/`ERROR`, regenerated all 17 committed report snapshots, and added six new behaviour tests (Task 2) proving each widened consumer, confirmed non-vacuous against a scratch pre-Task-1 worktree.

## Task Commits

1. **Task 1: One transport-faulted run, through every layer** - `ec1db5c` (feat)
2. **Task 2: The three consumer widenings, proved one at a time** - `7a2f2a6` (test)

**Plan metadata:** committed separately in the meta-repo (`.planning/`).

## Files Created/Modified

- `firestarter_app/firestarter/chip_test.py` - `STATUS_*` vocabulary, `StepResult.status`, `_skip_result`/two bare-SKIPPED sites stamp `STATUS_SKIP`, transport arm re-pointed, `run_status(results)` fold
- `firestarter_app/firestarter/diagnostic_report.py` - `SCHEMA_VERSION` 1.7->1.8, `DiagnosticReport.run_status` field, `"status"`/`"run_status"` export keys, `build_db_diff`'s ERROR ladder guard
- `firestarter_app/firestarter/submit.py` - `_TITLE_VERDICT_HARNESS`, `overall_verdict`'s status-axis-first guard
- `firestarter_app/firestarter/cli_handlers.py` - `report.run_status` assignment seam, `_dev_test_exit_code`'s `run_status_error` parameter and call-site wiring
- `firestarter_app/tests/test_dev_test_cmd.py` - R2b repaired forward (SKIPPED/ERROR), new end-to-end exit-code/title test, exit-code-signature call-site repair
- `firestarter_app/tests/test_chip_test_sdp_leg.py` - two degrade tests repaired forward, `_EXPECTED_PRECEDENCE_MATRIX`'s three rows moved to SKIPPED
- `firestarter_app/tests/test_blast_radius_invariance.py` - `_TO_DICT_KEYS`/`_STEPS_ELEMENT_0_KEYS` widened (11->12, 13->14), `SCHEMA_VERSION` pin moved to 1.8
- `firestarter_app/tests/test_diagnostic_report.py` - new ladder-guard test with anti-vacuity sibling, two SCHEMA_VERSION-pin tests repaired forward
- `firestarter_app/tests/test_submit.py` - `_step` helper widened with an optional `status` kwarg, four new `overall_verdict`/`build_title`/`_reason_text` behaviour tests
- `firestarter_app/tests/fixtures/reports/*.json` - all 17 committed snapshots regenerated (adds `status`/`run_status` keys, schema 1.8; hashes unmoved)

## Decisions Made

- Followed the plan's D-01..D-16 decisions exactly (see CONTEXT.md); no architectural deviation.
- Deleted rather than edited the pre-existing `#` comment on the transport-arm exception handler (it had gone stale describing the old BAD verdict), since editing it in place would have produced added `#`-prefixed diff lines and violated the plan's zero-added-comment acceptance criterion.
- Used the bare-string-literal-above-the-declaration idiom (already shipped in this tree) for every piece of new rationale instead of a `#` comment, per the project's absolute no-comments rule and the plan's own carrier instruction.
- Proved Task 2's status-axis-dependent tests non-vacuous via a disposable `git worktree add --detach <path> HEAD~1` checkout (removed after use, never touching the working tree) rather than asserting non-vacuity by inspection alone.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Repaired two SCHEMA_VERSION-pin tests broken by this plan's own 1.7->1.8 bump**
- **Found during:** Task 1 (post-implementation full-suite check)
- **Issue:** `tests/test_diagnostic_report.py::test_schema_version_1_7_single_sourced` and `::test_schema_version_is_one_seven` both hard-pin the literal `"1.7"`; Task 1's D-07 schema bump left both failing immediately.
- **Fix:** Renamed and repaired both to pin `"1.8"` (`test_schema_version_1_8_single_sourced`, `test_schema_version_is_one_eight`), matching the file's own established rename-on-bump convention (it had already been renamed twice before, for 1.5->1.6 and 1.6->1.7).
- **Files modified:** `firestarter_app/tests/test_diagnostic_report.py`
- **Verification:** both tests pass; full `test_diagnostic_report.py` suite green (70 passed)
- **Committed in:** `ec1db5c` (Task 1 commit)

**2. [Rule 1 - Bug] Repaired `test_dev_test_cmd.py::test_identical_verdict_multiset_differing_exit_code`'s two `_dev_test_exit_code` call sites**
- **Found during:** Task 1 (post-implementation full-suite check)
- **Issue:** Task 1 widened `_dev_test_exit_code` with a new required keyword-only `run_status_error: bool` parameter; this test's two existing calls omitted it and failed with `TypeError`.
- **Fix:** Added `run_status_error=False` to both calls -- this test is specifically about the pre-existing `sdp_oracle_not_run` composition rule and is unrelated to the status axis, so `False` is the correct neutral value.
- **Files modified:** `firestarter_app/tests/test_dev_test_cmd.py`
- **Verification:** test passes; full `test_dev_test_cmd.py` suite green
- **Committed in:** `ec1db5c` (Task 1 commit)

**3. [Rule 1 - Bug, self-caught] Removed accidentally-added `#` comments before committing**
- **Found during:** Task 1 (self-review against the plan's own "zero added comment lines" acceptance criterion, before the commit)
- **Issue:** While implementing, I initially added several NEW `#`-comment blocks (in `cli_handlers.py`'s `run_status` assignment, `diagnostic_report.py`'s `build_db_diff` guard and `run_status` field, `submit.py`'s `_TITLE_VERDICT_HARNESS`, and `test_chip_test_sdp_leg.py`'s `_EXPECTED_PRECEDENCE_MATRIX` note), and edited the transport-arm's pre-existing `#` comment in place -- all of which would have shown as added `^\+\s*#` diff lines, violating both the plan's explicit acceptance criterion and the project's standing "no comments in source" rule.
- **Fix:** Converted each new rationale block to the bare-string-literal-above-the-declaration idiom (or removed it where redundant with an existing docstring), and reverted the transport-arm's pre-existing comment to its original byte-identical text by deleting it entirely (rather than leaving it edited-and-stale) since the code path it described had changed.
- **Files modified:** `firestarter_app/firestarter/chip_test.py`, `firestarter_app/firestarter/diagnostic_report.py`, `firestarter_app/firestarter/submit.py`, `firestarter_app/firestarter/cli_handlers.py`, `firestarter_app/tests/test_chip_test_sdp_leg.py`
- **Verification:** re-ran the plan's own `git diff HEAD~1 ... | grep -cE '^\+[[:space:]]*#'` check -- 0, both commits
- **Committed in:** `ec1db5c` and `7a2f2a6` (both commits, corrected before either was made)

---

**Total deviations:** 3 auto-fixed (2 blocking test-signature/pin repairs, 1 self-caught comment-rule violation).
**Impact on plan:** All three are direct, necessary consequences of the plan's own edits (the schema bump and the exit-code signature widening) or a self-correction against the plan's own explicit gate. No scope creep; nothing outside the two tasks' stated files was touched.

## Issues Encountered

None -- both tasks' `<verify>` blocks passed on the corrected tree, and the plan-level `<verification>` (all six pinned test modules, snapshot `--check`, rekey ledger, ruff, mypy watermark, both AST gates, firmware/database porcelain) all passed.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- The status vocabulary, the additive field, the fold, and all three consumer widenings are in place and proven end-to-end on the transport-fault path.
- Ready for plan `178-02` (ATTR-03/ATTR-04 concurrency/ordering/idempotency edges) and `178-03` (frozen-shape registration for `attr01-status-axis-transport-fault`), both of which build on this plan's `StepResult.status`/`run_status`/`STATUS_ERROR` surface without further changes to it.
- No blockers.

---
*Phase: 178-fault-attribution-the-two-axis-vocabulary*
*Completed: 2026-09-06*

## Self-Check: PASSED
- FOUND: firestarter_app/firestarter/chip_test.py, diagnostic_report.py, submit.py, cli_handlers.py
- FOUND: commit ec1db5c (Task 1, firestarter_app)
- FOUND: commit 7a2f2a6 (Task 2, firestarter_app)
- FOUND: commit 572b7773 (SUMMARY.md, meta-repo)
