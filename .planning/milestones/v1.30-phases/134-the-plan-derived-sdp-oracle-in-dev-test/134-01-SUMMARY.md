---
phase: 134-the-plan-derived-sdp-oracle-in-dev-test
plan: 01
subsystem: testing
tags: [python, pytest, chip_test.py, sdp, op-registration-parity, mypy]

# Dependency graph
requires:
  - phase: 133-sdp-leg-mechanism
    provides: OP_SDP_LOCK/OP_SDP_UNLOCK, _SDP_OPS, _dispatch_sdp, the op-registration parity gate
    at 9 ops, the cleanup-registry drain
provides:
  - Four engine-local op constants (OP_WRITE_BASELINE_B/A, OP_WRITE_INHIBITED, OP_WRITE_RESTORED)
  - _SDP_LEG_OPS registry frozenset (a subset of _DESTRUCTIVE_OPS)
  - generate_inhibited_pattern(start, length) -- the D-19 pattern-B generator
  - _SDP_BASELINE_GATE_REASON / _SDP_UNLOCK_GATE_REASON module constants for plan 134-04's gate
  - The op-registration parity gate green at 13 ops (7 policed registries), with 8 TEMPORARY
    exemption rows plans 134-02/134-03 must discharge in their own commits
  - LEG-03 fully proven and ticked Complete
affects: [134-02, 134-03, 134-04]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Derive B from A by calling the pure generator exactly once and complementing it, never by
      calling it a second time with any region -- the anti-tautology construction (D-19/P-01)."
    - "Op-registration parity: a new frozenset/registry must be added to _REGISTRY_CONSTANT_NAMES
      AND _POLICED_REGISTRIES in the same commit as the constants it governs, or the module-level
      assert (fires at collection) breaks every test in the file."
    - "TEMPORARY exemption rows with a literal, grep-able 'TEMPORARY — discharged by plan N' marker
      let a later plan prove its own discharge mechanically rather than by inspection."

key-files:
  created:
    - .planning/phases/134-the-plan-derived-sdp-oracle-in-dev-test/134-CI-PARITY.md
  modified:
    - firestarter_app/firestarter/chip_test.py
    - firestarter_app/tests/test_op_registration_parity.py
    - firestarter_app/tests/test_chip_test_sdp_leg.py

key-decisions:
  - "FLAG_SKIP_SDP_UNLOCK import deferred to plan 134-02: ruff F401 flags it as unused at this
    commit (measured, contradicting the plan text's assumption that ruff's F rules never flag
    unused module-level imports); the docstring narrowing is stated in prose only here."
  - "Fixed a real regression in test_shipped_ops_never_reach_sdp_arm (test_chip_test_sdp_leg.py,
    not in this task's declared file list): 'shipped op set' now excludes _SDP_LEG_OPS too, not
    just _SDP_OPS, since this phase's four new op constants are vocabulary-only at this commit."
  - "Reworded one of my own new comments in chip_test.py ('console table' -> 'terminal-facing
    table') to avoid tripping test_chip_test.py's no-print/click/console regex -- a false positive
    from prose, not an actual print/render/CLI introduction."

requirements-completed: [LEG-03]

coverage:
  - id: D1
    description: "Four SDP-leg op constants + _SDP_LEG_OPS registry + generate_inhibited_pattern
      land in chip_test.py, with the op-registration parity gate green at 13 ops in the same commit"
    requirement: LEG-03
    verification:
      - kind: unit
        ref: "tests/test_op_registration_parity.py (7 tests, all passing at 13 ops)"
        status: pass
      - kind: unit
        ref: "tests/test_chip_test_sdp_leg.py::TestInhibitedPattern (pytest -k pattern_b, 5 tests)"
        status: pass
    human_judgment: false
  - id: D2
    description: "Non-vacuity obligation #1 observed RED once (planted P-01's exact failure mode),
      then restored byte-identically"
    verification:
      - kind: unit
        ref: "manual RED-then-restore cycle, verbatim output captured below"
        status: pass
    human_judgment: false

# Metrics
duration: 28min
completed: 2026-08-04
status: complete
---

# Phase 134 Plan 01: SDP-Leg Op Vocabulary + Pattern-B Generator Summary

**Landed the four SDP-leg op constants, `_SDP_LEG_OPS`, and the D-19 anti-tautology pattern-B
generator in `chip_test.py`, kept the op-registration parity gate green at 13 ops in the same
commit, and proved LEG-03's five assertions against the live generators with the every-byte
divergence check observed RED once before being restored byte-identically.**

## Performance

- **Duration:** 28 min
- **Started:** 2026-08-04T14:44:42Z (first task commit, meta repo)
- **Completed:** 2026-08-04T15:11:49Z (last task commit, submodule)
- **Tasks:** 3
- **Files modified:** 4 (1 created, 3 modified across meta + submodule)

## Accomplishments

- Recorded the phase's pre-edit CI-parity + CI-replica baseline (`134-CI-PARITY.md`): mypy 33/35
  (headroom 2), 124 source files checked (floor 120, margin 4), 1338 tests passing, 81.84%
  coverage, no board attached -- before any production line moved.
- Added `OP_WRITE_BASELINE_B`/`OP_WRITE_BASELINE_A`/`OP_WRITE_INHIBITED`/`OP_WRITE_RESTORED` (D-06
  leg order), `_SDP_LEG_OPS` (a subset of the widened `_DESTRUCTIVE_OPS`), and
  `_SDP_BASELINE_GATE_REASON`/`_SDP_UNLOCK_GATE_REASON` for plan 134-04's baseline gate.
- Added `generate_inhibited_pattern(start, length)`: calls `generate_pattern` exactly once and
  bitwise-complements it -- A and B are guaranteed to differ at every byte by construction, never
  by chance, directly defusing P-01 (the milestone's headline pitfall: `generate_pattern` is pure
  in `(start, length)`, so a second call over the same region makes A == B and the leg's central
  assertion a tautology).
- Kept `tests/test_op_registration_parity.py`'s module-level `assert len(_ALL_OPS) == 13` (was 9)
  and the parity gate green in the SAME commit as the new constants: `_SDP_LEG_OPS` joins
  `_REGISTRY_CONSTANT_NAMES` and `_POLICED_REGISTRIES` (6 -> 7 policed registries), 29 new
  exemption rows added (21 permanent + 8 TEMPORARY, marked with a grep-able
  `TEMPORARY — discharged by plan 134-02`/`134-03` string plans 134-02/134-03 must remove in their
  own commits or the stale-row guard fails).
- Added `class TestInhibitedPattern` (5 tests, selected by `pytest -k "pattern_b"`) proving LEG-03's
  five assertions against the live generators for the real `(0, 256)` region (derived from
  `chip_test._DEFAULT_REGION`, never hard-coded): equal length, differ at every byte, the direct
  anti-tautology check (`B != a fresh generate_pattern() call`), neither pattern degenerate, and
  D-05's non-laundering leg (B's read-back does not classify `blank/contact`, and its `ff_ratio` is
  strictly below the live `_FF_RATIO_THRESHOLD`).
- Observed non-vacuity obligation #1 RED: temporarily changed `generate_inhibited_pattern` to
  `return generate_pattern(start, length)`, confirmed both the every-byte assertion and the
  anti-tautology assertion failed, then restored byte-identically (confirmed via `git diff --stat`
  empty for `chip_test.py` before the task's commit).
- Confirmed non-vacuity obligation #7: `test_altered_registry_copy_fails_parity_non_vacuous` still
  passes now that `_ALL_OPS` has grown to 13.
- LEG-03 ticked `Complete` in `REQUIREMENTS.md` -- the only requirement this plan may mark, per the
  dispatch's explicit scope.

## Task Commits

Each task was committed atomically:

1. **Task 1: Record the pre-edit CI-parity + CI-replica baseline** - `3db1099` (docs, meta repo)
2. **Task 2: Op vocabulary + `_SDP_LEG_OPS` + pattern-B generator, parity gate in the same commit**
   - `de08037` (feat, `firestarter_app` submodule)
3. **Task 3: LEG-03 proofs against the live generators + non-vacuity obligations 1 and 7**
   - `4395c8a` (test, `firestarter_app` submodule)

**Plan metadata:** committed with this SUMMARY (docs: complete plan)

## Files Created/Modified

- `.planning/phases/134-the-plan-derived-sdp-oracle-in-dev-test/134-CI-PARITY.md` (meta) - pre-edit
  CI-parity + CI-replica baseline record
- `firestarter_app/firestarter/chip_test.py` - four op constants, `_SDP_LEG_OPS`, widened
  `_DESTRUCTIVE_OPS`, two gate-reason constants, `generate_inhibited_pattern`, narrowed module
  docstring contract line
- `firestarter_app/tests/test_op_registration_parity.py` - six coupled edits (assert 9->13,
  `_REGISTRY_CONSTANT_NAMES`, `_POLICED_REGISTRIES`/count 6->7, 29 exemption rows, extended
  `expected_membership` matrix, docstring census update) plus a narrowed `_dispatch_step`
  zero-exemptions assertion (see Deviations)
- `firestarter_app/tests/test_chip_test_sdp_leg.py` - `class TestInhibitedPattern` (5 tests) plus a
  regression fix to `test_shipped_ops_never_reach_sdp_arm` (see Deviations)

## Decisions Made

- **FLAG_SKIP_SDP_UNLOCK import deferred to 134-02.** The plan's action item said "ruff's `F`
  rules do not flag unused module-level constants" and instructed verifying with `ruff check`. That
  check found `F401 imported but unused` for this specific name-import (constants, not defined
  locally) -- the plan's own contingency ("if it does flag it, move the import into plan 134-02
  instead and say so in the SUMMARY") applies. Only the module docstring's prose narrowing landed
  here; the import + its live use is 134-02's.
- **`_dispatch_step`'s "zero exemptions" assertion narrowed, not removed.** Adding 4 TEMPORARY
  exemption rows against `_dispatch_step` (for this phase's own new ops, pending 134-02's routing)
  would otherwise trip the pre-existing assertion that no exemption row may reference
  `_dispatch_step` at all. Narrowed it to "zero exemptions for the 9 pre-existing ops, exactly 4
  TEMPORARY exemptions for this phase's own SDP-leg ops" -- preserving the original guard's intent
  (catch an accidental omission among the 9 shipped ops) while permitting the deliberate, tracked,
  temporary gap this plan introduces.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed a regression in `test_shipped_ops_never_reach_sdp_arm`**
- **Found during:** Task 2 (running the full regression floor: `tests/test_chip_test.py
  tests/test_chip_test_sdp_leg.py tests/test_dev_test_cmd.py`)
- **Issue:** This pre-existing Phase-133 test computes "the module's shipped op set" as
  `module_op_constants - _SDP_OPS`. Adding this phase's four new `OP_*` constants (which are not
  members of `_SDP_OPS`) made that computed set include them, breaking the test's equality assertion
  against the frozen 7-string `_SHIPPED_OP_STRINGS` literal -- even though the four new ops are
  vocabulary-only at this commit and are not actually dispatched anywhere yet.
- **Fix:** Changed the computation to `module_op_constants - _SDP_OPS - _SDP_LEG_OPS`, and updated
  the docstring to explain why. `_SDP_LEG_OPS` was imported for this purpose.
- **Files modified:** `firestarter_app/tests/test_chip_test_sdp_leg.py`
- **Verification:** `pytest tests/test_chip_test.py tests/test_chip_test_sdp_leg.py
  tests/test_dev_test_cmd.py tests/test_op_registration_parity.py -o addopts="" -q` -- 162 passed.
- **Committed in:** `de08037` (part of Task 2's commit, since the regression was caused by that
  task's vocabulary widening)

**2. [Rule 1 - Bug] Reworded a comment that false-positived a regression-floor test**
- **Found during:** Task 2 (same regression-floor run)
- **Issue:** `test_count_applicable_no_print_or_render_introduced` (`tests/test_chip_test.py`) greps
  `chip_test.py`'s source for `\bprint\(|\bclick\.|\bconsole` to prove no print/render/CLI output
  was introduced. My own new comment justifying D-07's two-baseline-ops design used the phrase
  "console table", tripping the `\bconsole` branch of that regex -- a prose false positive, not an
  actual print/console/click introduction.
- **Fix:** Reworded "console table" to "terminal-facing table" in the comment -- same meaning, no
  trigger substring.
- **Files modified:** `firestarter_app/firestarter/chip_test.py`
- **Verification:** `pytest tests/test_chip_test.py -o addopts="" -q` passes;
  `test_count_applicable_no_print_or_render_introduced` specifically re-run green.
- **Committed in:** `de08037` (part of Task 2's commit)

---

**Total deviations:** 2 auto-fixed (both Rule 1 -- bugs surfaced by this task's own vocabulary
widening, fixed inline before proceeding). No scope creep: both fixes are directly caused by, and
necessary to keep green because of, this task's own edits.

## Measured Discrepancy (recorded, not silently resolved)

**Task 3's acceptance criterion `grep -c '0\.98' tests/test_chip_test_sdp_leg.py` returns 0** is in
literal tension with the same task's `<action>` instruction to "add a comment recording the
measured values at this commit (B's ff_ratio is ~0.0039 against a 0.98 threshold) as context, not
as the assertion" -- which explicitly requires the string `0.98` to appear in a comment. Measured:
the literal grep command returns **1** (the one permitted context comment), not 0. Per this
project's standing practice (133-RECORD.md and others) of recording such measured tensions rather
than silently picking one side, this SUMMARY states both readings: **the assertion code itself
contains zero `0.98` literals** (the threshold is read from the live `_FF_RATIO_THRESHOLD` import in
every assertion) -- which is what "the threshold is imported, not literal" actually protects against
-- while the one permitted context comment (required by the same task's own action item) makes the
raw `grep -c` command return 1. No code change was made to force the raw count to 0, since doing so
would mean dropping the explicitly-required context comment.

## Issues Encountered

None beyond the two auto-fixed regressions and the one measured discrepancy documented above.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- LEG-03 is fully discharged; nothing later in the phase adds to it.
- Plan 134-02 has its exact starting point: import `FLAG_SKIP_SDP_UNLOCK` and wire the four new
  ops' `_dispatch_step` routing arm, discharging the 4 `TEMPORARY — discharged by plan 134-02`
  exemption rows in the SAME commit that adds the routing (or the stale-row guard fails).
- Plan 134-03 has its exact starting point: teach `derive_plan` to emit the SDP leg's six steps
  (D-06), discharging the 4 `TEMPORARY — discharged by plan 134-03` exemption rows and flipping
  the two `("derive_plan", OP_SDP_LOCK/OP_SDP_UNLOCK): False` pins in the SAME commit.
- Plan 134-04 has `_SDP_BASELINE_GATE_REASON`/`_SDP_UNLOCK_GATE_REASON` ready to consume for its
  baseline gate (`_baseline_closes_sdp_gate`).
- No blockers. mypy headroom unchanged at 2 (33/35); `checked` unchanged at 124 (no new source
  files added this plan -- both modified test files already existed).

## Self-Check: PASSED

- `firestarter_app/firestarter/chip_test.py` -- FOUND, contains `generate_inhibited_pattern` and
  `_SDP_LEG_OPS = frozenset(`.
- `firestarter_app/tests/test_op_registration_parity.py` -- FOUND, 7/7 tests pass at 13 ops.
- `firestarter_app/tests/test_chip_test_sdp_leg.py` -- FOUND, `class TestInhibitedPattern` present,
  5/5 `pattern_b`-selected tests pass.
- `.planning/phases/134-the-plan-derived-sdp-oracle-in-dev-test/134-CI-PARITY.md` -- FOUND.
- Commit `3db1099` (meta) -- FOUND in `git log --oneline --all`.
- Commit `de08037` (submodule) -- FOUND in `git -C firestarter_app log --oneline --all`.
- Commit `4395c8a` (submodule) -- FOUND in `git -C firestarter_app log --oneline --all`.

---
*Phase: 134-the-plan-derived-sdp-oracle-in-dev-test*
*Completed: 2026-08-04*
