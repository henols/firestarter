---
phase: 178-fault-attribution-the-two-axis-vocabulary
plan: 02
subsystem: dev-test-diagnostics
tags: [chip_test, diagnostic_report, submit, status-axis, ocp-test-validation, dedup-fingerprint]

# Dependency graph
requires:
  - phase: 178-fault-attribution-the-two-axis-vocabulary
    provides: "plan 178-01's STATUS_COMPLETE/ERROR/SKIP vocabulary, StepResult.status, run_status(results), the re-pointed transport-fault arm, and the three widened consumers -- this plan adds no new production surface, only the tests that prove ATTR-04's confirmation and ATTR-05's non-suppression"
provides:
  - "The positive ATTR-04 leg (Leg B): two reports differing ONLY in the status axis hash equal, plus an anti-vacuity verdict-change sibling, an empty/single-result edge, and an ordering edge with a structural proof over dedup_fingerprint's source"
  - "The ATTR-05 non-suppression proof: is_submittable measured byte-unchanged (T3 recorded void), and a transport-faulted report reaching confirm_fn on both a first and a second submit_report call"
  - "The D-01/D-02 measured non-changes: the destructive-write gate predicate unchanged, an AST proof the transport arm bypasses _skip_result, the run_status fold's two legs, and the op-registry disjointness proof"
  - "The status proof for the three re-pointed SDP precedence rows, added beside the frozen three-tuple matrix rather than by widening it"
affects: [178-03-frozen-shape-registration, 178-04-attr06-rail-reading-disclosure]

# Actuals (#2632) -- pairs with the plan's estimate to calibrate future estimates.
actuals:
  tokens: 4700
  tasks: 3
  commits: 3

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Positive-leg + anti-vacuity-sibling pairing for a hash-exclusion proof: never assert only that a new field's presence doesn't move the hash (vacuous unless verdict is also proved to move it)"
    - "AST-walk proof of a handler's internal call shape (StepResult vs _skip_result), rather than only asserting the resulting verdict/status values, so a future refactor that routes through the wrong helper reddens structurally"

key-files:
  created: []
  modified:
    - firestarter_app/tests/test_diagnostic_report.py
    - firestarter_app/tests/test_submit.py
    - firestarter_app/tests/test_chip_test.py
    - firestarter_app/tests/test_chip_test_sdp_leg.py
    - .planning/phases/178-fault-attribution-the-two-axis-vocabulary/evidence/178-02-confirmation.txt
    - .planning/phases/178-fault-attribution-the-two-axis-vocabulary/evidence/178-02-attr05.txt
    - .planning/phases/178-fault-attribution-the-two-axis-vocabulary/evidence/178-02-nonchange.txt

key-decisions:
  - "Followed the plan's D-01/D-02/D-08/D-10/D-11/D-16 exactly: no source file touched, only tests; each new fact backed by a measured evidence file rather than an assertion."
  - "The empty-results edge (test_status_axis_does_not_perturb_an_empty_results_fingerprint) deliberately does NOT use _minimal_report(step_specs=[]) -- that helper's `step_specs = step_specs or [...]` fallback treats a passed-in empty list as falsy and silently substitutes its two-step default, which would have built a two-step report instead of a genuinely empty one. Constructed the empty-results DiagnosticReport directly instead, mirroring the plan's own verify-script helper."
  - "test_the_transport_precedence_rows_carry_the_error_status (Task 3) asserts status via a fresh run_plan()/StepResult read rather than widening _derive_precedence_row's (escaped, verdict, error_code) 3-tuple or _EXPECTED_PRECEDENCE_MATRIX -- widening either would have forced a rewrite of the frozen Phase-133 before-image, which the plan explicitly forbids."
  - "All new rationale (four docstrings plus one section marker) uses either the function/module docstring or the bare-string-literal-above-the-declaration idiom -- never a `#` comment -- per the project's absolute no-comments rule."

patterns-established: []

requirements-completed: [ATTR-01, ATTR-02, ATTR-04, ATTR-05]

coverage:
  - id: D1
    description: "ATTR-04's confirmation carries a positive leg: two reports differing only in the status axis hash equal, with an anti-vacuity sibling proving a verdict change still moves the hash"
    requirement: "ATTR-04"
    verification:
      - kind: unit
        ref: "tests/test_diagnostic_report.py#test_status_axis_does_not_perturb_dedup_fingerprint"
        status: pass
      - kind: unit
        ref: "tests/test_diagnostic_report.py#test_a_verdict_change_still_perturbs_dedup_fingerprint"
        status: pass
      - kind: e2e
        ref: ".planning/phases/178-fault-attribution-the-two-axis-vocabulary/evidence/178-02-confirmation.txt (legB_equal=True, antivacuity_differs=True)"
        status: pass
    human_judgment: false
  - id: D2
    description: "ATTR-04's empty/single-result and ordering edges, plus a structural proof that dedup_fingerprint carries exactly three parts.append sites and no reference to status"
    requirement: "ATTR-04"
    verification:
      - kind: unit
        ref: "tests/test_diagnostic_report.py#test_status_axis_does_not_perturb_an_empty_results_fingerprint"
        status: pass
      - kind: unit
        ref: "tests/test_diagnostic_report.py#test_status_axis_does_not_reorder_the_fingerprint_pre_image"
        status: pass
      - kind: e2e
        ref: ".planning/phases/178-fault-attribution-the-two-axis-vocabulary/evidence/178-02-confirmation.txt (empty_equal=True, single_equal=True, ordering_invariant=True, parts_append_count=3, hash_reads_status=False, empty_shape_value=8d6208d00be7)"
        status: pass
    human_judgment: false
  - id: D3
    description: "is_submittable is measured byte-unchanged (D-11) -- the milestone research's run-validity term (T3) is recorded void"
    requirement: "ATTR-05"
    verification:
      - kind: unit
        ref: "tests/test_submit.py#test_is_submittable_is_unchanged_by_the_status_axis"
        status: pass
      - kind: e2e
        ref: ".planning/phases/178-fault-attribution-the-two-axis-vocabulary/evidence/178-02-attr05.txt (mentions_status=False, mentions_run_status=False, mentions_STATUS_ERROR=False, mentions_run_valid=False)"
        status: pass
    human_judgment: false
  - id: D4
    description: "A transport-faulted report still reaches confirm_fn on a first AND a second submit_report call, with a title reading INCONCLUSIVE (harness) -- the offer to file is never suppressed"
    requirement: "ATTR-05"
    verification:
      - kind: unit
        ref: "tests/test_submit.py#test_a_transport_faulted_report_still_reaches_the_confirm_prompt"
        status: pass
      - kind: e2e
        ref: ".planning/phases/178-fault-attribution-the-two-axis-vocabulary/evidence/178-02-attr05.txt (108 passed)"
        status: pass
    human_judgment: false
  - id: D5
    description: "The destructive-write gate predicate stays measured unchanged for a transport-faulted StepResult, and the transport arm is proved (by AST) to construct StepResult directly rather than through _skip_result"
    requirement: "ATTR-01"
    verification:
      - kind: unit
        ref: "tests/test_chip_test.py#test_id_step_closes_gate_predicate_is_unchanged_by_the_status_axis"
        status: pass
      - kind: unit
        ref: "tests/test_chip_test.py#test_the_transport_arm_does_not_route_through_skip_result"
        status: pass
      - kind: unit
        ref: "tests/test_chip_test.py#test_transport_fault_carries_skipped_verdict_and_error_status"
        status: pass
      - kind: e2e
        ref: ".planning/phases/178-fault-attribution-the-two-axis-vocabulary/evidence/178-02-nonchange.txt (gate_closes=True, gate_tuple_intact=True, transport_handlers=1, handler_stepresult_calls=1, handler_skipresult_calls=0)"
        status: pass
    human_judgment: false
  - id: D6
    description: "The run_status fold's two legs, the op-registry disjointness proof, and the status proof for the three re-pointed SDP precedence rows -- added beside the frozen Phase-133 matrix rather than by widening it"
    requirement: "ATTR-02"
    verification:
      - kind: unit
        ref: "tests/test_chip_test.py#test_run_status_folds_error_when_any_step_errored"
        status: pass
      - kind: unit
        ref: "tests/test_chip_test.py#test_run_status_is_complete_when_no_step_errored"
        status: pass
      - kind: unit
        ref: "tests/test_chip_test_sdp_leg.py#test_the_transport_precedence_rows_carry_the_error_status"
        status: pass
      - kind: e2e
        ref: ".planning/phases/178-fault-attribution-the-two-axis-vocabulary/evidence/178-02-nonchange.txt (fold_empty=COMPLETE, fold_error=ERROR, fold_complete=COMPLETE, status_in_all_ops=False, status_in_multiword=False)"
        status: pass
    human_judgment: false

duration: 25min
completed: 2026-09-06
status: complete
---

# Phase 178 Plan 02: Fault Attribution -- the Two-Axis Vocabulary Summary

**Made ATTR-04's confirmation non-vacuous (a positive Leg B plus its anti-vacuity sibling) and ATTR-05's non-suppression measured rather than assumed (`is_submittable` proved byte-unchanged, T3 recorded void, and a transport-faulted report proved to reach `confirm_fn` twice) -- twelve new tests, zero source-file edits, zero added comment lines.**

## Performance

- **Duration:** ~25 min
- **Completed:** 2026-09-06T12:25:01Z
- **Tasks:** 3
- **Files modified:** 7 (4 test modules, 3 evidence files)

## Accomplishments

- **Task 1 (D-10 Leg B + ATTR-04 edges):** Added four tests to `test_diagnostic_report.py` -- the positive leg proving two reports differing only in the status axis hash equal, its anti-vacuity sibling proving a verdict change still perturbs the hash, the empty/single-result edge (cross-checked against the frozen `synthetic-arm4-empty-results` hash `8d6208d00be7`), and the ordering edge with a structural proof that `dedup_fingerprint`'s source carries exactly three `parts.append` sites and no reference to `status`.
- **Task 2 (ATTR-05, D-11/T3-void):** Added two tests to `test_submit.py` -- `is_submittable` measured to carry none of the four run-validity tokens the milestone research's T3 would have added, and a transport-faulted report proved to reach `confirm_fn` on both a first and a second `submit_report` call, with its title reading `INCONCLUSIVE (harness)`.
- **Task 3 (D-01/D-02 non-changes):** Added five tests across `test_chip_test.py` and `test_chip_test_sdp_leg.py` -- the destructive-write gate predicate (`_id_step_closes_gate`) measured unchanged, an AST proof the `(SerialError, HardwareOperationError)` handler constructs `StepResult` directly (zero `_skip_result` calls), the `run_status` fold's two legs plus an op-registry disjointness proof, and the status proof for the three re-pointed SDP precedence rows added beside (never into) the frozen Phase-133 three-tuple matrix.
- All three evidence files (`178-02-confirmation.txt`, `178-02-attr05.txt`, `178-02-nonchange.txt`) record every named assertion's actual measured output, matching the plan's `<verify>` blocks byte-for-byte.

## Task Commits

1. **Task 1: Leg B -- prove the status axis is out of the hash, and prove the proof is not vacuous** - `8867e60` (test)
2. **Task 2: ATTR-05 -- the offer to file always stands, and T3 is recorded void** - `014a446` (test)
3. **Task 3: The measured non-changes -- the safety gate, the helper bypass, and the dead bucket** - `70aa490` (test)

**Plan metadata:** committed separately in the meta-repo (`.planning/`).

## Files Created/Modified

- `firestarter_app/tests/test_diagnostic_report.py` - Leg B, its anti-vacuity sibling, the empty/single-result edge, and the ordering edge with the `dedup_fingerprint` structural proof
- `firestarter_app/tests/test_submit.py` - `is_submittable`'s byte-unchanged proof (T3 void) and the transport-faulted-report confirm-prompt idempotency proof
- `firestarter_app/tests/test_chip_test.py` - the destructive-gate non-change proof, the `_skip_result`-bypass AST proof, the transport-fault verdict/status shape, and the `run_status` fold's two legs plus the op-registry disjointness proof
- `firestarter_app/tests/test_chip_test_sdp_leg.py` - the status proof for the three re-pointed SDP precedence rows, added beside the frozen three-tuple matrix
- `.planning/phases/178-fault-attribution-the-two-axis-vocabulary/evidence/178-02-confirmation.txt` - Task 1's measured evidence
- `.planning/phases/178-fault-attribution-the-two-axis-vocabulary/evidence/178-02-attr05.txt` - Task 2's measured evidence
- `.planning/phases/178-fault-attribution-the-two-axis-vocabulary/evidence/178-02-nonchange.txt` - Task 3's measured evidence

## Decisions Made

- Followed the plan's D-01/D-02/D-08/D-10/D-11/D-16 decisions exactly (see 178-CONTEXT.md); no architectural deviation, and no `firestarter/` source file or `tests/fixtures/` file was touched -- this plan is tests-only, as required.
- Built the empty-results edge test via a direct `DiagnosticReport(...)` construction rather than `_minimal_report(step_specs=[])`, because that helper's `step_specs = step_specs or [...]` fallback treats an empty list as falsy and silently substitutes its two-step default -- using it as written would have built a two-step report instead of a genuinely empty one, defeating the edge case's own point.
- Proved the three re-pointed SDP precedence rows' status by running a fresh `run_plan()`/`StepResult` read for each exception class, rather than widening `_derive_precedence_row`'s `(escaped, verdict, error_code)` 3-tuple or `_EXPECTED_PRECEDENCE_MATRIX` -- either would have forced touching the frozen Phase-133 before-image the plan explicitly protects.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug, self-caught] Removed an added `#`-comment section header and a matrix-constant-naming docstring line before committing**
- **Found during:** Task 3 (post-implementation gate check, before committing)
- **Issue:** The Task 3 edit to `test_chip_test.py` initially added a `#`-comment section-header block (mirroring the file's own pre-existing convention) ahead of the new tests, which would have shown up as added `^\+\s*#` diff lines -- violating both the plan's explicit "zero added comment lines" acceptance criterion and the project's standing no-comments rule. Separately, the new SDP-leg test's docstring in `test_chip_test_sdp_leg.py` named `_PRE_EDIT_PRECEDENCE_MATRIX` by identifier, which the plan's own automated gate flags as a byte-level touch to the frozen Phase-133 before-image regardless of context (a docstring mention counts the same as an edit under a literal `grep` for the name).
- **Fix:** Converted the section header to a bare triple-quoted string-literal expression (the project's established comment-free carrier, per `178-PATTERNS.md`), and reworded the docstring to describe the frozen matrix without naming its identifier.
- **Files modified:** `firestarter_app/tests/test_chip_test.py`, `firestarter_app/tests/test_chip_test_sdp_leg.py`
- **Verification:** re-ran the plan's own `git diff | grep -cE '^\+[[:space:]]*#'` (0) and `git diff -- test_chip_test_sdp_leg.py | grep -c '_PRE_EDIT_PRECEDENCE_MATRIX\|_INTENDED_PRECEDENCE_DELTA'` (0) checks before committing
- **Committed in:** `70aa490` (corrected before the commit was made)

**2. [Rule 3 - Blocking] Removed an unused `HardwareOperationError` import**
- **Found during:** Task 3 (ruff check, before committing)
- **Issue:** `test_chip_test.py`'s import block added `HardwareOperationError` alongside `SerialError`, but only `SerialError` is actually used by the new transport-fault test (the AST test names the class as a string, not an import); `ruff check` flagged `F401`.
- **Fix:** Removed the unused import.
- **Files modified:** `firestarter_app/tests/test_chip_test.py`
- **Verification:** `ruff check tests/` and `ruff format --check tests/` both green; full module re-run still 250 passed
- **Committed in:** `70aa490` (corrected before the commit was made)

---

**Total deviations:** 2 auto-fixed (1 self-caught comment/gate-naming violation, 1 blocking lint fix).
**Impact on plan:** Both are direct, necessary consequences of self-review against the plan's own explicit gates. No scope creep; nothing outside the three tasks' stated files was touched.

## Issues Encountered

None -- all three tasks' `<verify>` blocks passed on the corrected tree, and the plan-level `<verification>` (all five test modules green, zero comment lines, zero `firestarter/`/`tests/fixtures/` diff, frozen-matrix identifiers untouched) all passed.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- ATTR-04's confirmation now carries the positive leg it was missing, and ATTR-05's non-suppression is measured rather than assumed, with `is_submittable` proved byte-unchanged and T3 recorded void.
- The destructive-write gate, the `_skip_result` bypass, and the `FP_TRANSPORT` dead bucket are all confirmed unmoved by this phase's status-axis work.
- Plan `178-03` (frozen-shape registration for `attr01-status-axis-transport-fault`) can proceed against this plan's proven surface without further changes to `chip_test.py`, `diagnostic_report.py`, or `submit.py`.
- No blockers.

---
*Phase: 178-fault-attribution-the-two-axis-vocabulary*
*Completed: 2026-09-06*

## Self-Check: PASSED
- FOUND: firestarter_app/tests/test_diagnostic_report.py, test_submit.py, test_chip_test.py, test_chip_test_sdp_leg.py
- FOUND: .planning/phases/178-fault-attribution-the-two-axis-vocabulary/178-02-SUMMARY.md + 3 evidence files
- FOUND: commit 8867e60 (Task 1, firestarter_app)
- FOUND: commit 014a446 (Task 2, firestarter_app)
- FOUND: commit 70aa490 (Task 3, firestarter_app)
- FOUND: commit c4ebc7c1 (SUMMARY.md + evidence, meta-repo)
