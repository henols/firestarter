---
phase: 134-the-plan-derived-sdp-oracle-in-dev-test
plan: 10
subsystem: testing
tags: [python, pytest, chip_test.py, cli_handlers.py, sdp, laundering, count_applicable, leg-13, leg-17]

# Dependency graph
requires:
  - phase: 134-04
    provides: "_baseline_closes_sdp_gate/_SDP_BASELINE_OPS/_SDP_LEG_GATED_OPS (the
      D-08/D-20 baseline gate -- the seventh route this plan names but does not
      re-prove); sdp_hold_state/sdp_oracle_applicable/SDP_HOLD_* constants"
  - phase: 134-07
    provides: "report.sdp_hold_state assigned at the derive-in-engine /
      assign-in-handler seam (LEG-12, both surfaces); _dev_test_exit_code's
      D-15 ALLOW-only exit floor -- the hold-state seam this plan's NOT-RUN
      assertions read"
  - phase: 134-05
    provides: "make_leaked_lock_operator / make_clean_operator idioms this
      plan's route fixtures follow"
provides:
  - "tests/fixtures/synthetic_nonzero_chip_id.py -- SyntheticNonzeroChipIdDatabase,
    an EpromDatabase subclass overriding get_eprom for ONE chip name with a
    real ALLOW entry's chip-id overridden nonzero (D-17), in-source labelled
    unreachable in production today"
  - "Six laundering-route tests (R1-R6), each asserting BOTH
    operator.sdp_lock.assert_not_called() and a rendered NOT-RUN reason in
    both console and JSON -- R1/R2 (tests/test_dev_test_cmd.py,
    TestLaunderingRoutesR1R2SyntheticChipId), R3/R4 (::TestLaunderingRoutesR3R4),
    R5/R6 (tests/test_chip_test.py, library-level)"
  - "test_all_sdp_allow_chips_have_zero_chip_id_measured_live -- the live
    re-measurement of D-17's vacuousness claim, iterated via
    sdp_capability_for_entry, never restated as a literal count"
  - "LEG-13's pinning test family (tests/test_chip_test.py): the N-of-M ratio
    drop for a gated ALLOW chip (m_applicable=10, n_ran=6 -- a MEASURED
    DISCREPANCY against the design record's stated 5, carried forward
    verbatim from 134-04/134-07's own identical finding), the REFUSE-scope
    exclusion, the unedited shipped count_applicable pins, and the rendered
    banner text"
affects: [134-11, 137]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "A synthetic DB-entry fixture (EpromDatabase subclass overriding
      get_eprom for one name only) to drive a structurally-vacuous gate's
      full causal chain, rather than forcing the gate flag directly --
      proves the ROUTE, not just the gate (D-17)."
    - "Every laundering-route test pairs a negative operator-call assertion
      with a positive NOT-RUN-reason assertion -- an exit-code/verdict-only
      check would pass on a route that silently omits the reason (the
      Phase-114.1 lesson, restated for the SDP oracle)."
    - "A dead-write-path operator double (write_eprom claims success,
      read_eprom always yields pattern A) reproduces gh#20's exact bench
      shape and closes the baseline gate (D-08) after both baseline
      directions genuinely ran -- the minimum achievable 'ran' count for a
      gated ALLOW-chip run, not an arbitrarily-chosen smaller number."

key-files:
  created:
    - firestarter_app/tests/fixtures/synthetic_nonzero_chip_id.py
  modified:
    - firestarter_app/tests/test_dev_test_cmd.py
    - firestarter_app/tests/test_chip_test.py
    - .planning/REQUIREMENTS.md

key-decisions:
  - "LEG-13's pinning test asserts n_ran=6, not the 5 stated in
    134-CONTEXT.md/this plan's own text -- MEASURED DISCREPANCY, carried
    forward rather than silently matched to the stale numeral, per the same
    project convention 134-04-SUMMARY.md and 134-07-SUMMARY.md already
    established against this identical computation. Root cause: both
    baseline directions (write-baseline-b, write-baseline-a) always run
    regardless of the gate's own state (only the FOUR _SDP_LEG_GATED_OPS
    members are skipped once it closes, D-08's own design) -- with a
    dead-write-path double, write-baseline-a's own read-back matches pattern
    A and it reports OK, counting as ran alongside the four shipped ops and
    write-baseline-b (BAD). No fixture can make write-baseline-a NOT run
    while AT28C256 remains a real DB entry with real shipped read/blank-check/
    write/verify steps -- 6 is the true minimum achievable ran-count for this
    shape, not merely this fixture's quirk."
  - "R3 is driven by patching firestarter.chip_test.resolve_chip to raise
    ChipNotImplementedError against a GENUINELY ALLOW chip (_CHIP_ALLOW),
    rather than reusing the shipped AT28C16 adapter-required test verbatim --
    AT28C16 is a measured REFUSE chip, so its SDP-leg steps are NA via
    sdp_capability (R4's route) before ever reaching resolve_chip; only a
    genuinely-ALLOW chip's supported=True SDP steps actually traverse
    _resolve_or_none and map to SKIPPED, which is the mechanism R3 names."
  - "R1/R2's synthetic fixture is a real, importable EpromDatabase subclass
    (tests/fixtures/synthetic_nonzero_chip_id.py), unlike the AST-scan-only
    planted-violation fixtures beside it in the same directory -- its module
    docstring says so explicitly to avoid a future reader assuming the same
    never-import convention applies."
  - "sdp-unlock genuinely dispatches (and calls operator.sdp_unlock) in every
    R1/R2 test even though sdp-lock never runs -- OP_SDP_UNLOCK is
    deliberately absent from _DESTRUCTIVE_OPS (LEG-09) and baseline_gate_closed
    stays False when the chip-ID destructive gate closes first (the baseline
    ops never ran to set it). This is 134-04's own proven design
    (test_leg09_destructive_gate_never_skips_the_explicit_unlock_step), not a
    defect this plan needed to fix; R1/R2 assert only sdp_lock.assert_not_called(),
    per the plan's own text, never asserting sdp_unlock was skipped too."

requirements-completed: [LEG-13, LEG-17]
# Both requirements this plan's frontmatter names as MAY-tick. LEG-18 (plan
# 134-11's) and LEG-06/LEG-12/LEG-14 (already closed by 134-05/134-07/134-09)
# were NOT touched or re-ticked -- confirmed by `git diff -- .planning/REQUIREMENTS.md`
# showing exactly two rows (LEG-13, LEG-17) plus their Traceability-table rows
# changed, nothing else.

coverage:
  - id: D1
    description: "R1 -- a detected chip-ID mismatch against the synthetic
      nonzero-chip-id fixture closes the destructive gate before any SDP-leg
      step dispatches; sdp_lock never called; NOT-RUN with a non-empty
      reason rendered in both console and JSON"
    requirement: LEG-17
    verification:
      - kind: unit
        ref: "tests/test_dev_test_cmd.py::TestLaunderingRoutesR1R2SyntheticChipId::test_r1_chip_id_mismatch_closes_gate_and_renders_notrun"
        status: pass
    human_judgment: false
  - id: D2
    description: "R2 -- _id_step_closes_gate fires on ANY id uncertainty:
      is_ok=False alone, and separately a transport error degrading the id
      step to BAD -- both close the gate the same way"
    requirement: LEG-17
    verification:
      - kind: unit
        ref: "tests/test_dev_test_cmd.py::TestLaunderingRoutesR1R2SyntheticChipId::test_r2_id_check_not_ok_closes_gate_and_renders_notrun"
        status: pass
      - kind: unit
        ref: "tests/test_dev_test_cmd.py::TestLaunderingRoutesR1R2SyntheticChipId::test_r2_transport_error_during_id_check_closes_gate_and_renders_notrun"
        status: pass
    human_judgment: false
  - id: D3
    description: "R3 -- a resolve_chip refusal maps the SDP-leg steps
      (supported=True on a genuinely ALLOW chip) to SKIPPED via
      _resolve_or_none; sdp_lock never called; NOT-RUN rendered"
    requirement: LEG-17
    verification:
      - kind: unit
        ref: "tests/test_dev_test_cmd.py::TestLaunderingRoutesR3R4::test_r3_resolve_chip_refusal_maps_baseline_steps_to_skipped_notrun"
        status: pass
    human_judgment: false
  - id: D4
    description: "R4 -- a REFUSE chip's write-inhibited step is NA, carrying
      sdp_capability(name, db)[1] itself as its reason (identity, never a
      re-worded string); sdp_lock never called; NOT-RUN rendered with that
      exact reason"
    requirement: LEG-17
    verification:
      - kind: unit
        ref: "tests/test_dev_test_cmd.py::TestLaunderingRoutesR3R4::test_r4_refuse_chip_na_reason_matches_sdp_capability_identity"
        status: pass
    human_judgment: false
  - id: D5
    description: "R5 -- write_scope=\"none\" structurally omits every SDP-leg
      op from Plan.steps and locks all six into locked_destructive with
      non-empty reasons; run_plan over that plan never dispatches sdp_lock;
      documented as library/test surface only (unreachable from dev test
      since Phase 121's write_scope reversal)"
    requirement: LEG-17
    verification:
      - kind: unit
        ref: "tests/test_chip_test.py::test_r5_laundering_write_scope_none_locks_all_six_and_never_calls_sdp_lock"
        status: pass
    human_judgment: false
  - id: D6
    description: "R6 -- every SDP-ALLOW chip's write_scope=\"full\" plan
      derives a non-empty Plan.steps, so an ALLOW-chip run can never reach
      cli_handlers.py's \"if not results: sys.exit(0)\" guard; sdp_lock is
      never called against a genuinely empty Plan either"
    requirement: LEG-17
    verification:
      - kind: unit
        ref: "tests/test_chip_test.py::test_r6_laundering_allow_plans_never_derive_an_empty_steps_list"
        status: pass
    human_judgment: false
  - id: D7
    description: "D-17 re-measured live: every SDP-ALLOW chip in the shipped
      database still has chip-id == 0 today, iterated via
      sdp_capability_for_entry, never restated as a literal count"
    verification:
      - kind: unit
        ref: "tests/test_dev_test_cmd.py::test_all_sdp_allow_chips_have_zero_chip_id_measured_live"
        status: pass
      - kind: other
        ref: "grep -ci 'gated by chip[- ]id' tests/ firestarter/ -r -- 0 hits"
        status: pass
    human_judgment: false
  - id: D8
    description: "LEG-13 pinning: an NA/SKIPPED oracle drops the headline
      N-of-M ratio for an ALLOW chip (measured m_applicable=10, n_ran=6 --
      MEASURED DISCREPANCY against the stated 5, documented) -- no counting
      logic changed, the REFUSE case recorded explicitly out of scope, and
      the rendered banner text shows the dropped ratio"
    requirement: LEG-13
    verification:
      - kind: unit
        ref: "tests/test_chip_test.py::test_count_applicable_sdp_gated_allow_chip_ratio_drops"
        status: pass
      - kind: unit
        ref: "tests/test_chip_test.py::test_count_applicable_sdp_does_not_change_shipped_non_sdp_counting"
        status: pass
      - kind: unit
        ref: "tests/test_chip_test.py::test_count_applicable_refuse_chip_n_equals_m_is_out_of_leg13_scope"
        status: pass
      - kind: unit
        ref: "tests/test_chip_test.py::test_count_applicable_sdp_banner_row_renders_the_dropped_ratio"
        status: pass
    human_judgment: false

# Metrics
duration: 50min
completed: 2026-08-04
status: complete
---

# Phase 134 Plan 10: The Six Laundering Routes and LEG-13's N-of-M Pin Summary

**Six tests proving `sdp_lock` was never called AND a `NOT-RUN` reason was rendered for every route to a
non-running SDP oracle (R1-R6, LEG-17), plus a pinning test measuring the honest N-of-M drop for a gated
ALLOW chip -- 10 applicable, 6 ran, not the design record's stated 5 (LEG-13).**

## Performance

- **Duration:** 50 min
- **Started:** 2026-08-04T19:33:44Z (134-09's last commit; this plan's context-reading began here)
- **Completed:** 2026-08-04T20:23:42Z (last task commit)
- **Tasks:** 3
- **Files modified:** 3 (1 new fixture, 2 test files), all inside `firestarter_app`; plus
  `.planning/REQUIREMENTS.md` in the meta repo

## Accomplishments

- Created `tests/fixtures/synthetic_nonzero_chip_id.py` (`SyntheticNonzeroChipIdDatabase`): an
  `EpromDatabase` subclass overriding `get_eprom` for exactly one chip name (`AT28C256`) to return a copy
  of that chip's real, shipped DB entry with only `chip-id` overridden to a nonzero synthetic value
  (`0xBEEF`). Every other field -- `algorithm`/`protocol-id`, `memory-size`, `pin-count`, `bus-config`,
  `electrical-type` -- stays real. The module docstring states, in-source: what it is (test input only,
  but unlike its AST-scan-only siblings in the same directory, meant to be imported and run), why it
  exists (D-17: every shipped SDP-ALLOW chip has `chip-id == 0`, making the chip-ID destructive gate
  structurally vacuous for the whole population), and that it is **unreachable in production today**,
  correct if a chip-id is ever added, defence-in-depth and never live protection.
- Added `test_all_sdp_allow_chips_have_zero_chip_id_measured_live` (`tests/test_dev_test_cmd.py`):
  re-measures D-17's vacuousness claim live against the shipped database (via `sdp_capability_for_entry`,
  never a hardcoded 43), so a future DB change that adds a real chip-id to an SDP-ALLOW entry is caught
  rather than silently invalidating the fixture's own "unreachable today" label.
- `TestLaunderingRoutesR1R2SyntheticChipId` (`tests/test_dev_test_cmd.py`): R1 (a detected id mismatch
  against the synthetic fixture) and R2 (two sub-tests: `is_ok=False`, and a `SerialError` raised during
  the id check) each drive the real CLI through `SyntheticNonzeroChipIdDatabase`, asserting
  `operator.sdp_lock.assert_not_called()` and a rendered `NOT-RUN: <reason>` in both `result.output` and
  the JSON artifact. Neither test monkeypatches `destructive_gate_closed` or forces the gate directly --
  both drive the full id-step -> mismatch/uncertainty -> gate-closes -> refusal chain end to end
  (`grep -c 'destructive_gate_closed' tests/test_dev_test_cmd.py` returns 0).
- `TestLaunderingRoutesR3R4` (`tests/test_dev_test_cmd.py`): R3 patches
  `firestarter.chip_test.resolve_chip` to raise `ChipNotImplementedError` against `_CHIP_ALLOW`
  (AT28C256, a genuinely-ALLOW chip whose SDP-leg steps are `supported=True`), proving the
  `resolve_chip`-refusal-to-SKIPPED route for the SDP steps themselves -- distinct from R4's
  `sdp_capability`-refusal-to-NA route, and deliberately NOT reusing the shipped AT28C16
  adapter-required test verbatim, because AT28C16 is REFUSE and its SDP steps are already NA before
  ever reaching `resolve_chip`. R4 drives a REFUSE chip (`_CHIP_NO_ID`/M8720) end to end and asserts
  `write-inhibited`'s NA reason is `sdp_capability(name, db)[1]` **by identity**, never a re-worded
  string.
- `test_r5_laundering_…`/`test_r6_laundering_…` (`tests/test_chip_test.py`, library-level): R5 asserts
  `write_scope="none"` structurally omits every SDP-leg op from `Plan.steps` and locks all six into
  `locked_destructive` with non-empty reasons, and that `run_plan` over that plan never dispatches
  `sdp_lock` -- documented as library/test surface only (unreachable from `dev test` since Phase 121's
  `_resolve_write_scope` reversal). R6 iterates every measured SDP-ALLOW chip's `write_scope="full"`
  plan and asserts `Plan.steps` is never empty, so `cli_handlers.py`'s `if not results: sys.exit(0)`
  guard can never be reached from an ALLOW-chip run; separately proves `sdp_lock` is never called
  against a genuinely empty `Plan`.
- Named the baseline gate (D-08/D-20, `134-04-SUMMARY.md`) as the **seventh** route to a non-running
  oracle in a module comment beside both new test classes, pointing at the CLI-level proofs
  (`TestHoldStateLeg12`/`TestExitFloorD15`) that already discharge it, so a later reader does not mistake
  "six routes here" for exhaustive coverage.
- LEG-13's pinning test family (`tests/test_chip_test.py`): built `_gated_allow_operator` (a
  dead-write-path double: `write_eprom` always reports success, `read_eprom` always yields pattern A
  regardless of what was written) and measured `count_applicable(plan, results)` for AT28C256 at
  `write_scope="full"` against it: `m_applicable == 10`, `n_ran == 6`. Re-ran the two shipped,
  non-SDP `count_applicable` pins (`AM2716`/`M8720`) unedited to prove no counting logic changed.
  Recorded the REFUSE case (`M8720`'s six SDP steps NA, `N == M`) as explicitly out of LEG-13's scope,
  backed by a live assertion rather than left as an unverified claim. Asserted the rendered banner text
  (`diagnostic_report.py`'s own `"{n_ran} of {m_applicable} ran"` row, via a `rich.console.Console(record=True)`
  capture) shows `"6 of 10 ran"`, never the misleading `"4 of 4 ran"`.
- **Ticked LEG-13 and LEG-17** in `.planning/REQUIREMENTS.md`, each with an evidence clause naming the
  discharging commits/tests. Both Traceability-table rows flipped `Pending` -> `Complete`. No other
  requirement row touched (`git diff -- .planning/REQUIREMENTS.md` confirms exactly these two entries
  plus their two Traceability rows changed).

## Task Commits

Each task was committed atomically, inside the `firestarter_app` submodule on
`gsd/v1.30-sdp-surface-retirement`:

1. **Task 1: R1/R2 -- the synthetic nonzero-chip-id fixture and the full causal chain** - `2f75cb9`
   (test)
2. **Task 2: R3/R4/R5/R6 -- resolve_chip refusal, REFUSE-chip NA, write_scope=none, empty results** -
   `2072105` (test)
3. **Task 3: LEG-13's banner pinning test (R7) and the scoping record** - `2b7a702` (test)

**Plan metadata:** committed with this SUMMARY (docs: complete plan), in the meta repo.

## Files Created/Modified

- `firestarter_app/tests/fixtures/synthetic_nonzero_chip_id.py` -- `SyntheticNonzeroChipIdDatabase`,
  `SYNTHETIC_CHIP_NAME`, `SYNTHETIC_CHIP_ID`.
- `firestarter_app/tests/test_dev_test_cmd.py` -- `ChipNotImplementedError`/`SerialError` imports,
  `sdp_capability`/`sdp_capability_for_entry` imports, the fixture import,
  `test_all_sdp_allow_chips_have_zero_chip_id_measured_live`,
  `TestLaunderingRoutesR1R2SyntheticChipId` (3 tests), `TestLaunderingRoutesR3R4` (2 tests).
- `firestarter_app/tests/test_chip_test.py` -- `sdp_capability_for_entry`/`_DEFAULT_REGION` imports,
  `test_r5_laundering_…`, `test_r6_laundering_…`, `_gated_allow_operator`, and the four LEG-13 pinning
  tests.
- `.planning/REQUIREMENTS.md` (meta repo) -- LEG-13/LEG-17 ticked `Complete` with evidence; Traceability
  table updated for both rows.

## Decisions Made

See `key-decisions` in the frontmatter above for the full reasoning; summarized:

- LEG-13's pinning test asserts the **measured** `n_ran=6`, not the design record's stated `5` -- a
  MEASURED DISCREPANCY carried forward from the identical finding already recorded twice in this same
  phase (`134-04-SUMMARY.md`, `134-07-SUMMARY.md`), with the root cause (both baseline directions
  always run; `write-baseline-a` is never itself gated and reports OK against a dead-write-path double)
  explained in the test's own docstring.
- R3 is driven by patching `resolve_chip` directly against a genuinely-ALLOW chip, rather than reusing
  AT28C16 (which is REFUSE and would exercise R4's route, not R3's, for the SDP steps specifically).
- The synthetic fixture is explicitly documented as an importable, run-time-instantiated module --
  unlike its AST-scan-only planted-violation siblings in `tests/fixtures/` -- to prevent a future reader
  from assuming the "never import" convention applies here too.
- `sdp-unlock` genuinely dispatches in every R1/R2 test (even though `sdp-lock` never runs) because
  `OP_SDP_UNLOCK` is deliberately absent from `_DESTRUCTIVE_OPS` (LEG-09) and the baseline gate never
  closes when the chip-ID gate closes first -- this is 134-04's own proven, tested design, not a defect;
  R1/R2 assert only `sdp_lock.assert_not_called()`, exactly as the plan's own text specifies.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] A docstring literally spelled the forbidden `gated by chip ID` phrase, tripping the
acceptance criterion's own grep**
- **Found during:** Task 1, self-check against the plan's own acceptance criterion
  (`grep -ci 'gated by chip[- ]id' tests/ firestarter/ -r` must return 0)
- **Issue:** The first draft of `TestLaunderingRoutesR1R2SyntheticChipId`'s class docstring described the
  overclaim trap by literally writing `"the leg is gated by chip ID"` as prose -- a plain-text grep
  cannot distinguish a comment warning against a phrase from an actual overclaim.
- **Fix:** Reworded to describe the same warning without the literal substring ("evidence that the
  chip-ID mismatch check is what protects an SDP-ALLOW chip today").
- **Files modified:** `tests/test_dev_test_cmd.py`
- **Verification:** `grep -ci 'gated by chip[- ]id' tests/ firestarter/ -r` returns 0 (checked file-by-file,
  all zero); the acceptance-criteria grep is otherwise unaffected.
- **Commit:** `2f75cb9`

**2. [Rule 1 - Bug] An unused `_SDP_OPS` import and an awkward direct test-function invocation, self-caught
before commit**
- **Found during:** Task 3, drafting `test_count_applicable_sdp_does_not_change_shipped_non_sdp_counting`
- **Issue:** An early draft imported `firestarter.chip_test._SDP_OPS` and called
  `tests.test_op_registration_parity.test_non_registry_still_has_no_ops()` directly as an inline
  assertion -- unconventional (invoking another module's test function as a helper) and unnecessary,
  since that gate is already run as its own independent acceptance check.
- **Fix:** Removed the import and the direct invocation, replaced with a comment pointing at the
  independently-run gate.
- **Files modified:** `tests/test_chip_test.py`
- **Verification:** `ruff check` clean (no unused import); `pytest tests/test_op_registration_parity.py::test_non_registry_still_has_no_ops` passes on its own.
- **Commit:** `2b7a702`

---

**Total deviations:** 2 auto-fixed (both Rule 1, self-caught during authoring before the first commit of
each affected task -- neither reached a committed state uncorrected).
**Impact on plan:** Neither affects behavior. No scope creep.

## Issues Encountered

None beyond the deviations documented above.

## User Setup Required

None -- no external service configuration required.

## Threat Flags

None new. This plan's `<threat_model>` (T-134-38/39/40/41) is fully covered by the implementation as
written: T-134-38 (a green run with no oracle reported as PASS) is mitigated by one test per route,
each pairing a negative `sdp_lock` call with a rendered `NOT-RUN` reason; T-134-39 (claiming the leg is
protected by the chip-ID gate) is mitigated by the grep-checked-absent phrase, the fixture's own
unreachable-today label, and the live re-measurement test; T-134-40 (a perfect-looking N-of-M banner
over a non-running oracle) is mitigated by the LEG-13 pinning test's measured `n_ran=6, m_applicable=10`
and the rendered banner text; T-134-41 (an exit-code-only test passing on a laundered run) is mitigated
by every route test pairing the verdict/exit assertion with the negative call assertion.

## Next Phase Readiness

- LEG-13 and LEG-17 are both fully discharged; plan `134-11` (LEG-18, gh#20's triage finding) is the
  phase's last plan and does not depend on anything new from this one.
- The MEASURED DISCREPANCY (`n_ran=6`, not the design record's stated `5`) should be carried into
  Phase 137's ledger alongside 134-02's "exactly two" finding and 134-04/134-07's own identical
  discrepancy against this same computation, so a later reader encountering "5"/"n_ran=5" in
  `134-CONTEXT.md`/ROADMAP prose does not assume this plan's test is wrong instead.
- No blockers. mypy headroom unchanged at 2 (33/35, `checked` 126 source files -- up from 125 at
  134-09's close: one new test module, `tests/fixtures/synthetic_nonzero_chip_id.py`, added; a floor,
  not a ceiling, per D-15). Full suite: 1425 -> 1437 passed (+12 new tests), coverage 82.12%
  (>= 70% floor), 30 snapshots unchanged. `tools/ci_replica_venv.sh`: all 5 legs green.

## Self-Check: PASSED

- `firestarter_app/tests/fixtures/synthetic_nonzero_chip_id.py` -- FOUND, contains
  `class SyntheticNonzeroChipIdDatabase(`, `SYNTHETIC_CHIP_NAME`, `SYNTHETIC_CHIP_ID`.
- `firestarter_app/tests/test_dev_test_cmd.py` -- FOUND, contains
  `class TestLaunderingRoutesR1R2SyntheticChipId`, `class TestLaunderingRoutesR3R4`,
  `def test_all_sdp_allow_chips_have_zero_chip_id_measured_live`; 51/51 tests in this file pass.
- `firestarter_app/tests/test_chip_test.py` -- FOUND, contains `def test_r5_laundering_…`,
  `def test_r6_laundering_…`, `def test_count_applicable_sdp_gated_allow_chip_ratio_drops`; 109/109
  tests in this file pass.
- Commit `2f75cb9` (submodule) -- FOUND in `git -C firestarter_app log --oneline --all`.
- Commit `2072105` (submodule) -- FOUND in `git -C firestarter_app log --oneline --all`.
- Commit `2b7a702` (submodule) -- FOUND in `git -C firestarter_app log --oneline --all`.
- `.planning/REQUIREMENTS.md` -- LEG-13 and LEG-17 are the ONLY two requirement rows changed (confirmed
  via `git diff`); LEG-01…12/14/15/16/18 all untouched.

---
*Phase: 134-the-plan-derived-sdp-oracle-in-dev-test*
*Completed: 2026-08-04*
