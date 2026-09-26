---
phase: 99-bench-ledger-graduation-gate-evidence-ledger-update
plan: 01
subsystem: testing
tags: [pytest, json-gate, ledger-validation, tdd]

# Dependency graph
requires:
  - phase: 98-fix-correct-the-0x08-32-pin-write-vpp-path
    provides: corrected DIP32_27C020 rw-pin:[31] write/VPP fix (revision-invariant), native 119/119 green, golden traces byte-identical
provides:
  - "check_ledger.py D-09 extension recognizing a v1.18-native 0x08 graduation (self-consistent write/read-back SHA, no v1.15 write baseline)"
  - "3 new tests proving positive graduation, honesty-guard rejection, and FUT-06 retirement-by-removal"
  - "the gate is now CAPABLE of passing a graduated 0x08 PROTOCOL-LEDGER row (plan 99-04 decides whether it actually gets written PASS)"
affects: [99-02, 99-03, 99-04]

# Tech tracking
tech-stack:
  added: []
  patterns: ["evidence-shape branch keyed on a boolean marker (v1_18_writeverify_sha_selfconsistent) rather than a new status enum value"]

key-files:
  created:
    - .planning/phases/99-bench-ledger-graduation-gate-evidence-ledger-update/deferred-items.md
  modified:
    - .planning/v1.16/ledger/tools/check_ledger.py
    - .planning/v1.16/ledger/tools/test_check_ledger.py

key-decisions:
  - "Chose option (a) from 99-RESEARCH.md Schema Tension: extended the existing PASS status's D-09 constraint via an evidence-shape branch, rather than adding a new status enum value (PASS-v1.18-native) — minimal, tested change per the plan's explicit instruction."
  - "Evidence marker v1_18_writeverify_sha_selfconsistent is a boolean recognized ONLY for the branch that skips the v1.15 write-baseline requirement; when absent, original two-flag D-09 behavior is unchanged, so all 11 existing rows and 5 pre-existing tests stay green with zero risk of accidental relaxation."
  - "Did not fix two pre-existing ruff findings (unused pytest import, check_ledger.py formatting debt) — confirmed pre-existing via git show against the pre-Task-1 commit, out of this plan's files_modified scope; logged to deferred-items.md."

requirements-completed: [BENCH-02]

# Metrics
duration: 25min
completed: 2026-07-01
---

# Phase 99 Plan 01: Ledger Graduation Gate Extension Summary

**Extended check_ledger.py's D-09 PASS constraint to admit a v1.18-native 0x08 graduation (self-consistent write/read-back SHA) without fabricating a nonexistent v1.15 write baseline, while keeping the honesty guard and all 11 existing ledger rows green.**

## Performance

- **Duration:** 25 min
- **Started:** 2026-07-01T10:52:34Z
- **Completed:** 2026-07-01T10:56:27Z
- **Tasks:** 3 (TDD: RED / GREEN / REFACTOR)
- **Files modified:** 2 (+ 1 new deferred-items.md)

## Accomplishments
- `check_ledger.py`'s `_assert_ledger02_d09` now branches on `evidence.v1_18_writeverify_sha_selfconsistent`: when `True`, only `p90_read_sha_matches_v115` is required (the v1.15 read baseline exists); when absent, the original two-flag requirement (`p90_read_sha_matches_v115` AND `p90_writecycle_sha_matches_v115`) is unchanged.
- Added 3 new tests to `test_check_ledger.py`: a positive v1.18-native graduation (exit 0), a honesty-guard negative (0x08 PASS without the self-consistency marker → exit 1), and a FUT-06-retired-by-removal graduation (exit 0).
- Confirmed the honesty guard (Rule T-99-01 in the plan's threat model) holds: no path admits a bare `0x08` PASS claim without the self-consistency proof.
- Confirmed the shared fixture `ledger_valid.json` is untouched — the graduated-row state exists only inside the three new in-test mutations, so the 5 pre-existing tests keep asserting the pre-Phase-99 status quo.
- Live 11-row `PROTOCOL-LEDGER.json` still exits 0 after the extension — purely additive, no disruption to the current ledger state.

## Task Commits

Each task was committed atomically (TDD gate sequence):

1. **Task 1: RED — add the 0x08 v1.18-native graduation tests** - `1dfa162` (test)
2. **Task 2: GREEN — extend the D-09 constraint** - `d7eb992` (feat)
3. **Task 3: REFACTOR — sync fixture legend + rerun full gate set** - `183c441` (refactor)

**Plan metadata:** committed separately after this summary via the final-commit step.

_TDD gate sequence verified in git log: `test(99-01)` → `feat(99-01)` → `refactor(99-01)`._

## Files Created/Modified
- `.planning/v1.16/ledger/tools/check_ledger.py` - `_assert_ledger02_d09` extended with the v1.18-native graduation branch (one-line comment cites 99-RESEARCH.md Pitfall 2); D-04 no-copy guard and `status_changed` invariant untouched.
- `.planning/v1.16/ledger/tools/test_check_ledger.py` - 3 new tests + 2 helper functions (`_find_0x08_row`, `_graduate_0x08_row`) added; module docstring extended to document tests 6-8.
- `.planning/phases/99-bench-ledger-graduation-gate-evidence-ledger-update/deferred-items.md` - new; logs 2 pre-existing ruff findings confirmed out of scope.

## Decisions Made
- Followed the plan's explicit recommendation: minimal extension (option a), no new status enum value.
- Named the recognized evidence key exactly as specified in the plan/patterns doc: `v1_18_writeverify_sha_selfconsistent`.
- Kept `oracle == "leonardo+Rev2.0"` and non-empty `p90_artifacts` mandatory for every PASS row unconditionally (both branches), matching the plan's action block precisely.

## Deviations from Plan

### Auto-fixed Issues

None requiring code changes. One documentation-only deviation:

**1. [Rule N/A - test-count nuance, not a bug] RED-state test count is 2 failed/6 passed, not the acceptance criterion's literal "3 failures, 5 passed"**
- **Found during:** Task 1 verification
- **Issue:** The plan's Task 1 acceptance criteria state "pytest reports exactly 3 failures, 5 passed." In practice, `test_0x08_pass_without_selfconsistency_exits_1` (the honesty-guard negative test) already passes against the UN-extended gate, because any `0x08` PASS claim unconditionally fails today (fail-closed default, no evidence shape is recognized yet). This is not a stub, not a bug, and not the TDD fail-fast trigger ("test passes unexpectedly ... investigate before proceeding") — the fail-fast rule concerns POSITIVE assertions passing prematurely; here a NEGATIVE assertion (expect exit 1) correctly holds under both the pre- and post-extension gate, since Task 2's extension only ADDS a way to pass, never removes the existing fail-closed default.
- **Resolution:** No code change. Verified via `pytest -v` that exactly 5 pre-existing tests pass, 1 new negative test also passes (correctly, for the right reason), and 2 new positive tests fail (correctly, RED). Documented this nuance here rather than forcing an artificial test-count match.
- **Files modified:** None (verification-only).
- **Verification:** `pytest -v` output showed `test_0x08_pass_without_selfconsistency_exits_1 PASSED` alongside the 5 originals, with `test_0x08_v1_18_native_graduation_exits_0` and `test_0x08_graduation_with_fut06_removed_exits_0` FAILED — exactly the RED state the plan's `<behavior>` block describes ("Assert exit 1" for Test B, satisfied even pre-extension).
- **Committed in:** `1dfa162` (Task 1 commit message documents this explicitly).

**2. [Rule N/A - scope boundary, pre-existing debt] Deferred 2 pre-existing ruff findings**
- **Found during:** Task 3 ruff-clean verification.
- **Issue:** `test_check_ledger.py` has an unused `pytest` import (F401); `check_ledger.py` fails `ruff format --check` due to pre-v1.16-era line-wrapping style.
- **Fix:** Not fixed — confirmed both predate this plan's commits via `git show 1dfa162~1:<file>` and ran ruff against those pre-plan versions, reproducing identical findings. Logged to `deferred-items.md` per the scope-boundary rule (only auto-fix issues directly caused by the current task's changes).
- **Files modified:** `.planning/phases/99-bench-ledger-graduation-gate-evidence-ledger-update/deferred-items.md` (new).
- **Verification:** `ruff format --diff check_ledger.py` shows only hunks outside the `_assert_ledger02_d09` region this plan touched.
- **Committed in:** `183c441` (Task 3 commit).

---

**Total deviations:** 2 documented (0 code changes; both are honest-recording/scope-boundary calls, not auto-fixes).
**Impact on plan:** None — plan's stated acceptance criteria (8 passed, 0 failed; live ledger exit 0; fixture unchanged) are all met exactly. The two items above are transparency notes, not scope creep.

## Issues Encountered
None — plan executed as written; both TDD gates (RED then GREEN) landed cleanly on the first attempt with no debugging iteration needed.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- `check_ledger.py` is now capable of passing a v1.18-native `0x08` graduation row. Plans 99-02/99-03 (bench execution) and 99-04 (ledger update, contingent on the actual bench outcome) can now write either a graduated PASS row or a documented deferral without hitting a structural gate failure or fabricating a v1.15 write baseline.
- No blockers. The gate change is purely additive and does not commit the project to any particular bench outcome — 99-04 still decides graduate-vs-defer based on real silicon results.

---
*Phase: 99-bench-ledger-graduation-gate-evidence-ledger-update*
*Completed: 2026-07-01*

## Self-Check: PASSED

- FOUND: .planning/v1.16/ledger/tools/check_ledger.py
- FOUND: .planning/v1.16/ledger/tools/test_check_ledger.py
- FOUND: .planning/phases/99-bench-ledger-graduation-gate-evidence-ledger-update/deferred-items.md
- FOUND: .planning/phases/99-bench-ledger-graduation-gate-evidence-ledger-update/99-01-SUMMARY.md
- FOUND commit: 1dfa162 (test)
- FOUND commit: d7eb992 (feat)
- FOUND commit: 183c441 (refactor)
