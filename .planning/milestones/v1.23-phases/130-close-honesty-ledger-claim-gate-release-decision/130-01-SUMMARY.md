---
phase: 130-close-honesty-ledger-claim-gate-release-decision
plan: 01
subsystem: testing
tags: [python, pytest, claim-gate, honesty-ledger, tooling]

requires: []
provides:
  - "check_permitted_claims.py default-mode target resolution repointed at the Phase 130 directory"
  - "test_check_permitted_claims.py green at 11 passed / 0 failed, with a differential + reachability-proven side-effect guard"
  - "130-CONTEXT.md decision parse re-asserted at 16/16 (regression check, no fix)"
affects: [130-02, 130-03, 130-04, 130-05, 130-06, 130-07, 130-08, 130-09, 130-10, 130-11, 130-12, 130-13, 130-14, 130-15, 130-16]

tech-stack:
  added: []
  patterns:
    - "Differential before/after snapshot guard instead of absolute-absence assertion, for a test whose own phase legitimately produces the artifacts it must not accidentally create as a side effect"
    - "Dedicated reachability test (mutation-demonstrated) proving a guard fires for the right reason, rather than trusting an unreached RED"

key-files:
  created: []
  modified:
    - .planning/phases/123-non-regression-baselines-gate-hardening/check_permitted_claims.py
    - .planning/phases/123-non-regression-baselines-gate-hardening/test_check_permitted_claims.py

key-decisions:
  - "Repointed _DEFAULT_TARGETS via new _PHASE_130_DIRNAME + _CONTRACTED_ARTIFACT_NAMES constants and os.pardir + normpath, not argv or FIRESTARTER_CLAIMSCAN_TARGETS, preserving D-15's all-or-nothing arming guarantee on the default target set"
  - "Converted the side-effect guard in test_d15_arming_both_directions to a differential snapshot (before/after over the four contracted basenames), because an absolute-absence assertion is self-invalidating once those four artifacts legitimately exist in the real Phase 130 directory"
  - "Rebuilt test_d15_arming_both_directions' tmp_path mechanism to mirror the real sibling-directory layout (fake 123-dir next to fake 130-dir), a consequence of the _DEFAULT_TARGETS repoint that the original copy-into-tmp_path-directly trick no longer matched"
  - "This plan ticks NO requirement ids -- CLOSE-02 is discharged by plan 130-16 alone"

requirements-completed: []

coverage:
  - id: D1
    description: "check_permitted_claims.py _DEFAULT_TARGETS repointed to resolve inside the sibling Phase 130 directory instead of _HERE (Phase 123's own directory) -- fixes RESEARCH C-2's UNARMED+exit-0 false-green"
    verification:
      - kind: unit
        ref: "manual verify command: python3 check_permitted_claims.py -> UNARMED: exit 0, naming the Phase 130 dir"
        status: pass
    human_judgment: false
  - id: D2
    description: "test_check_permitted_claims.py green at 11 passed / 0 failed (was 1 failed, 9 passed) via a differential side-effect guard plus a dedicated, mutation-demonstrated reachability test"
    verification:
      - kind: unit
        ref: "test_check_permitted_claims.py (full suite, 11 passed)"
        status: pass
      - kind: unit
        ref: "test_check_permitted_claims.py::test_side_effect_guard_fires_on_a_new_contracted_artifact"
        status: pass
    human_judgment: false
  - id: D3
    description: "130-CONTEXT.md decision parse re-asserted: outcome=parsed, count=16, ids D-01..D-16, file untouched"
    verification:
      - kind: unit
        ref: "node -e invocation of extractDecisions against 130-CONTEXT.md"
        status: pass
    human_judgment: false

duration: 25min
completed: 2026-08-02
status: complete
---

# Phase 130 Plan 01: Claim-Gate Repair Summary

**Repointed the milestone's only outward-facing overclaim gate at the real Phase 130 directory and made its own test suite green and provably reachable, before any closing artifact exists.**

## Performance

- **Duration:** ~25 min
- **Completed:** 2026-08-02
- **Tasks:** 3
- **Files modified:** 2 (plus this SUMMARY.md)

## Accomplishments

- `check_permitted_claims.py`'s `_DEFAULT_TARGETS` now resolves the four contracted artifact names (`130-LEDGER.md`, `130-DECISION.md`, `130-RELEASE-NOTES-fw.md`, `130-RELEASE-NOTES-app.md`) into the sibling `130-close-honesty-ledger-claim-gate-release-decision` directory via new `_PHASE_130_DIRNAME` and `_CONTRACTED_ARTIFACT_NAMES` module constants and `os.pardir` + `os.path.normpath`, closing RESEARCH C-2 (previously resolved against `_HERE`, the Phase 123 directory, producing a false-green `UNARMED:` + exit 0 on every run).
- `test_check_permitted_claims.py`'s side-effect guard in `test_d15_arming_both_directions` is now differential (`_snapshot_contracted_artifacts` / `_assert_no_new_contracted_artifacts`, before/after over the four names imported from the scanner) instead of an absolute-absence glob assertion, closing RESEARCH C-3's pre-existing RED (`1 failed, 9 passed` -> `11 passed, 0 failed`).
- Added `test_side_effect_guard_fires_on_a_new_contracted_artifact`, a dedicated reachability proof for the new guard, and confirmed by mutation: temporarily stubbing `_assert_no_new_contracted_artifacts` to `return` unconditionally made the new test fail with `Failed: DID NOT RAISE AssertionError`; the helper was then restored and the full suite re-verified at 11 passed.
- Re-asserted the `130-CONTEXT.md` decision parse as a measured regression check: `extractDecisions` returns `outcome=parsed`, `count=16`, ids exactly `D-01` through `D-16` with no gaps. `130-CONTEXT.md` was not edited (`git diff --stat` on it is empty).

## Task Commits

1. **Task 1: Repoint `_DEFAULT_TARGETS` at the Phase 130 directory and update the docstring's resolved paths** - `335e639` (fix)
2. **Task 2: Make the side-effect guard differential and prove it can still fire** - `8f08258` (test)
3. **Task 3: Re-assert the `130-CONTEXT.md` decision parse as a regression check** - recorded below (this SUMMARY is the deliverable; no source file changed)

**Plan metadata:** recorded in the final phase-level commit alongside this SUMMARY.

## Files Created/Modified

- `.planning/phases/123-non-regression-baselines-gate-hardening/check_permitted_claims.py` - `_DEFAULT_TARGETS` repointed at the sibling Phase 130 directory via new `_PHASE_130_DIRNAME` / `_CONTRACTED_ARTIFACT_NAMES` constants; module docstring's "Phase 130 coupling" paragraph amended to record the relocation and why it is a repoint, not an `argv`/env-seam switch.
- `.planning/phases/123-non-regression-baselines-gate-hardening/test_check_permitted_claims.py` - added `_snapshot_contracted_artifacts` / `_assert_no_new_contracted_artifacts` helpers (imported `_CONTRACTED_ARTIFACT_NAMES` and `_PHASE_130_DIRNAME` from the scanner), rewrote `test_d15_arming_both_directions`'s side-effect guard to be differential and its tmp_path mechanism to mirror the real sibling-directory layout, added `test_side_effect_guard_fires_on_a_new_contracted_artifact`, extended the module docstring's `Coverage:` list (entries for tests 8 and 11).

## Decisions Made

- **Repoint, not reroute (per plan prohibition).** `_DEFAULT_TARGETS` was rebuilt to resolve into the sibling Phase 130 directory rather than switched to `argv` or `FIRESTARTER_CLAIMSCAN_TARGETS` — `main()`'s `used_defaults` branch means D-15's all-or-nothing arming guarantee applies only to the default target set, so an explicit-seam fix would have silently lost that guarantee for the one call site that matters (an unqualified `python3 check_permitted_claims.py`).
- **Differential guard, not a narrowed glob.** The side-effect guard now compares a before/after snapshot of the four contracted basenames rather than asserting absolute absence of any `130-*.md` file — narrowing the glob alone would have fixed today's RED and re-planted the identical RED the moment `130-LEDGER.md` and its three siblings legitimately land in a later wave.
- **`_PHASE_130_DIRNAME` appears exactly once as a literal** in `check_permitted_claims.py` (the constant definition); the docstring amendment refers to it by name rather than repeating the literal string, per the plan's acceptance criterion.
- **D-17 accounting (Task 3):** the decision extractor's expected count for `130-CONTEXT.md` is 16, not 17. D-17 (the operator's locked ship-gate decision) was made during planning rather than recorded in `130-CONTEXT.md`'s `<decisions>` block, and is carried in the plan set's `must_haves` instead. A later reader must not read `16` as a missing decision.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] `test_d15_arming_both_directions`' tmp_path mechanism broken by Task 1's repoint**
- **Found during:** Task 2, while verifying the suite reached 11 passed / 0 failed
- **Issue:** The test's original mechanism copied `check_permitted_claims.py` directly into `tmp_path` and created `130-LEDGER.md` directly alongside it, relying on `_DEFAULT_TARGETS` resolving inside `_HERE` (the copy's own directory). Task 1's repoint made `_DEFAULT_TARGETS` resolve into a *sibling* of `_HERE` instead, so the copied scanner's target resolution now pointed at a directory next to `tmp_path`, not inside it — the "armed" direction of the test (`Direction 2`) silently stayed `UNARMED` because the created file never matched a resolved target path. Ran the test in isolation to confirm: it failed with `assert 0 != 0` (expected non-zero, got the `UNARMED:` exit 0 again).
- **Fix:** Rebuilt the test's isolation mechanism to mirror the real sibling-directory layout entirely inside `tmp_path` — a fake `123-non-regression-baselines-gate-hardening/` directory holds the scanner copy, and a fake `130-close-honesty-ledger-claim-gate-release-decision/` directory (named via the imported `_PHASE_130_DIRNAME`, not re-typed) holds the artifact file. This exactly reproduces the real directory relationship the scanner now depends on, entirely inside `tmp_path`, with no change to the guard's intent (never touching the real Phase 130 directory).
- **Files modified:** `.planning/phases/123-non-regression-baselines-gate-hardening/test_check_permitted_claims.py` (same file Task 2 already modifies; no separate task or commit)
- **Verification:** `python3 -m pytest test_check_permitted_claims.py::test_d15_arming_both_directions -q` -> `1 passed`; full suite -> `11 passed`.
- **Committed in:** `8f08258` (Task 2 commit)

**2. [Rule 1 - Bug] Stale duplicate absolute-absence assertion left behind mid-edit**
- **Found during:** Task 2, first full-suite verification pass after adding the differential guard
- **Issue:** An intermediate edit left both the new differential guard call and the old absolute-absence assertion block present in the same test body, causing a spurious failure against the real (populated with non-contracted `130-*.md` files) Phase 130 directory.
- **Fix:** Removed the leftover absolute-absence block, keeping only the single differential `_assert_no_new_contracted_artifacts` call as the final statement.
- **Files modified:** `.planning/phases/123-non-regression-baselines-gate-hardening/test_check_permitted_claims.py`
- **Verification:** Full suite re-run -> `11 passed, 0 failed`.
- **Committed in:** `8f08258` (Task 2 commit)

---

**Total deviations:** 2 auto-fixed (both Rule 1 - bugs introduced/exposed mid-task by the plan's own required Task 1 change, fixed within the same task's scope before commit).
**Impact on plan:** Both fixes were necessary to reach the plan's own stated acceptance criterion (11 passed / 0 failed) and touch only the file Task 2 already modifies. No scope creep; no requirement ticked; no architectural change.

## Issues Encountered

None beyond the two auto-fixed deviations above.

## Reachability Mutation Demonstration (Task 2 acceptance criterion)

Command: temporarily replaced `_assert_no_new_contracted_artifacts`'s body with `return` (unconditional no-op), then ran the new reachability test in isolation.

Observed failure:
```
>       with pytest.raises(AssertionError, match="130-LEDGER.md"):
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       Failed: DID NOT RAISE AssertionError

test_check_permitted_claims.py:423: Failed
=========================== short test summary info ============================
FAILED test_check_permitted_claims.py::test_side_effect_guard_fires_on_a_new_contracted_artifact
1 failed in 0.05s
```

The helper was then restored verbatim (`git diff` against the committed version showed no residual change) and the full suite re-verified at `11 passed`.

## Measured Decision Parse (Task 3)

Command:
```
node -e 'const fs=require("fs");const {extractDecisions}=require("./.claude/gsd-core/bin/lib/decisions.cjs");const r=extractDecisions(fs.readFileSync(".planning/phases/130-close-honesty-ledger-claim-gate-release-decision/130-CONTEXT.md","utf8"));...'
```

Result: `PASS outcome=parsed count=16 ids=D-01,D-02,D-03,D-04,D-05,D-06,D-07,D-08,D-09,D-10,D-11,D-12,D-13,D-14,D-15,D-16`

`130-CONTEXT.md` was not edited — `git -C /workspaces diff --stat -- .planning/phases/130-close-honesty-ledger-claim-gate-release-decision/130-CONTEXT.md` is empty. D-17 (the operator's locked ship-gate decision, made during planning) is deliberately **not** in this extractor's id set and is carried in the plan set's `must_haves` instead, so `16` — not `17` — is the correct expected count for this file.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- The claim gate (`check_permitted_claims.py`) is armed correctly against the real Phase 130 directory and will fire as intended the moment any of the four contracted artifacts land in a later wave.
- The paired test suite is green (11 passed) and has a positively-proven-reachable side-effect guard, so it will not silently mask a real side effect from a later plan's work in this directory.
- No requirement id ticked by this plan; CLOSE-02 remains open for plan 130-16.
- No blockers for downstream plans in this phase.

---
*Phase: 130-close-honesty-ledger-claim-gate-release-decision*
*Plan: 01*
*Completed: 2026-08-02*
