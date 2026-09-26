---
phase: 134-the-plan-derived-sdp-oracle-in-dev-test
plan: 04
subsystem: testing
tags: [python, pytest, chip_test.py, sdp, run_plan, baseline-gate, cleanup-registry, mypy]

# Dependency graph
requires:
  - phase: 134-03
    provides: "derive_plan emitting the D-06 six-step SDP leg for all 43 measured ALLOW chips and
      six NA steps for all 41 measured REFUSE chips; _SDP_LEG_STEP_ORDER, _SDP_LOCKED_REASON"
  - phase: 134-02
    provides: "_dispatch_sdp_leg (the read-back-equality oracle), _readback_operator/
      _dead_write_path_operator test doubles"
  - phase: 133-04
    provides: "the cleanup registry (list[Callable[[], None]]) drained in run_plan's bare
      try/finally, and the Phase-133 named LEG-09/10/11 proofs this plan must not touch"
provides:
  - "_baseline_closes_sdp_gate(result) -- the run-time gate that refuses to lock a chip whose
    write path did not transition in both directions (D-08), wider than _id_step_closes_gate's
    (BAD, SKIPPED) tuple: closes on BAD, marginal, SKIPPED and NA"
  - "_SDP_BASELINE_OPS (the gate's inputs) and _SDP_LEG_GATED_OPS (its outputs, including
    OP_SDP_UNLOCK per D-20 -- superseding D-08's measured-wrong 'unlock never attempted' clause)"
  - "run_plan wired at three sites: init (baseline_gate_closed, unlock_cleanup), a guard clause
    ordered AFTER the chip-ID destructive gate, and a sticky set clause"
  - "Cleanup de-registration: a successful explicit sdp-unlock step removes its lock's registered
    handle by value (cleanup.remove), so a completed leg emits exactly one unlock instead of two"
  - "sdp_hold_state(plan, results) -> str and sdp_oracle_applicable(plan) -> bool -- the pure,
    engine-side HELD/NOT-HELD/NOT-RUN(reason) derivation, deliberately NOT inside DiagnosticReport"
  - "SDP_HOLD_HELD/SDP_HOLD_NOT_HELD/SDP_HOLD_NOT_RUN report-value constants"
  - "The seventh route to a non-running oracle (beyond research's R1-R6), named and tested"
affects: [134-05, 134-06, 134-07, 134-10]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "A SECOND, INDEPENDENT gate flag (baseline_gate_closed) alongside the pre-existing
      destructive_gate_closed -- two structurally different mechanisms (chip-ID mismatch vs. a
      baseline write/read-back transition that did not complete), each with its own reason
      constants, never conflated in wording or in code."
    - "Gate widening is expressed as `verdict != VERDICT_OK` rather than enumerating the four
      non-OK verdicts by name -- deliberately wider than the id-gate's narrow 2-verdict tuple,
      because a contact fault is as disqualifying as a proven-dead write path for a lock decision."
    - "A held de-registration handle (unlock_cleanup) lets an explicit plan step reach into the
      registry and remove ONLY its own matching entry by value -- cleanup.remove(handle), never
      cleanup.clear() -- preserving the registry's declared GENERIC nature for any future op."
    - "sdp_hold_state lives in chip_test.py (the engine), not diagnostic_report.py (the renderer),
      because the renderer is a declared non-registry re-measured every run by an AST inversion
      guard to carry ZERO op vocabulary -- three independent reasons pin this, not just one."

key-files:
  created: []
  modified:
    - firestarter_app/firestarter/chip_test.py
    - firestarter_app/tests/test_op_registration_parity.py
    - firestarter_app/tests/test_chip_test_sdp_leg.py

key-decisions:
  - "Both baseline directions (write-baseline-b, write-baseline-a) always run regardless of
    baseline_gate_closed's state -- only the FOUR downstream ops (_SDP_LEG_GATED_OPS: sdp-lock,
    write-inhibited, sdp-unlock, write-restored) are skipped once it closes. This is what makes
    the gate's stickiness meaningful (a failing B followed by a passing A must not reopen it --
    there would be nothing to reopen if A never ran) and is a measured, deliberate reading of the
    plan's own <action> text over an alternative reading that would also gate baseline-a."
  - "MEASURED DISCREPANCY, recorded rather than silently reconciled (same project convention as
    134-02-SUMMARY.md's 'exactly two' finding): 134-CONTEXT.md D-20 and this plan's own
    <behavior>/<action> text state gh#20's shape produces n_ran=5, m_applicable=10. The ACTUAL
    measured value, run live against AT28C256 + _dead_write_path_operator(), is n_ran=6,
    m_applicable=10 -- because write-baseline-a is never itself gated (see above): it runs and
    reports OK (its expected read-back is pattern A; the fixture always returns pattern A), so it
    counts as ran alongside write-baseline-b and the four shipped ops (read/blank-check/write/
    verify) = 6 ran, 4 SKIPPED, out of 10 applicable. The committed test asserts the CORRECT
    measured value (6), with the discrepancy documented in its own docstring rather than silently
    matched to the stated 5."
  - "sdp_hold_state accepts (plan, results) per the plan's own signature, but this revision derives
    everything it returns from results alone -- plan is accepted for signature symmetry with
    count_applicable and so a future NOT-RUN-reason refinement (e.g. distinguishing a REFUSE chip
    from a genuinely-absent step) has it available without a call-site change."
  - "_SDP_BASELINE_OPS/_SDP_LEG_GATED_OPS were added to test_op_registration_parity.py's
    _REGISTRY_CONSTANT_NAMES (per the plan's own instruction to run the parity suite and follow its
    failure output) but this addition is currently INERT -- neither set is referenced inside the
    three AST-scanned functions (_dispatch_step/derive_plan/_dispatch_multi_run), only inside
    run_plan, which _op_names_referenced_in never scans. The parity suite passed unchanged before
    and after; no guard demanded the declaration. Kept anyway (harmless, and matches the module's
    own 'anything resolvable transitively belongs on this list' discipline) and NOT added to
    _POLICED_REGISTRIES per the plan's explicit instruction (policy subsets of the already-policed
    _SDP_LEG_OPS; ~18 no-op exemption rows would follow with zero new omission-catching power)."
  - "Task 2's production code (sdp_hold_state/sdp_oracle_applicable/the three SDP_HOLD_* constants)
    landed in Task 1's commit rather than its own, because both were authored together in
    chip_test.py before the first commit boundary was reached. A minor procedural deviation from
    the plan's exact per-task file lists; Task 2's OWN commit still carries its full test
    obligation (the 8 pytest -k \"hold\" tests + the 2 sdp_oracle_applicable tests) cleanly split
    from Task 3's gate/de-registration/LEG-09 tests via a reconstructed intermediate file state
    (verified ruff-clean and green at each commit point)."

requirements-completed: []
# This plan ticks NOTHING per its own dispatch scope. LEG-06/LEG-12/LEG-17 are all named in this
# plan's frontmatter `requirements:` field as CONTRIBUTES-TO-BUT-MUST-NOT-TICK:
#   - LEG-06: the gate stops a lock at a dead write path, but LEG-06's BAD+exit-1 contract closes
#     in plan 134-05 (the exit-precedence fix, D-14).
#   - LEG-12: sdp_hold_state is the derivation half only; the field lands in 134-06, the two
#     rendered surfaces in 134-07, which closes it.
#   - LEG-17: this gate is the SEVENTH route to a non-running oracle; the six R1-R6 route tests
#     (and this gate's own inclusion in that family) are plan 134-10's to close.
# LEG-09/10/11/15 (already [x], Phase 133) were not re-touched or re-evidenced -- confirmed by
# `git diff -U0` showing zero deletions inside any Phase-133 named proof.
# .planning/REQUIREMENTS.md was not modified by this plan (confirmed: git status/diff show no
# change to that file).

coverage:
  - id: D1
    description: "_baseline_closes_sdp_gate closes on ANY non-OK baseline verdict
      (BAD/marginal/SKIPPED/NA), wider than _id_step_closes_gate's (BAD, SKIPPED) tuple; wired at
      three sites in run_plan, ordered after the chip-ID destructive gate so a write-path closure
      is never misattributed to a chip-ID mismatch"
    verification:
      - kind: unit
        ref: "tests/test_chip_test_sdp_leg.py::test_baseline_gate_closes_dead_write_path_allow_chip_full_leg"
        status: pass
      - kind: unit
        ref: "tests/test_chip_test_sdp_leg.py::test_baseline_gate_closes_on_any_non_ok_verdict"
        status: pass
      - kind: unit
        ref: "tests/test_chip_test_sdp_leg.py::test_baseline_gate_stays_open_on_clean_ok"
        status: pass
    human_judgment: false
  - id: D2
    description: "The gate is STICKY: a failing write-baseline-b followed by a passing
      write-baseline-a leaves sdp-lock SKIPPED (never reopened)"
    verification:
      - kind: unit
        ref: "tests/test_chip_test_sdp_leg.py::test_baseline_gate_sticky_failing_b_then_passing_a_stays_closed"
        status: pass
    human_judgment: false
  - id: D3
    description: "D-20: OP_SDP_UNLOCK joins the baseline-gate set and renders SKIPPED when it
      closed, WITHOUT weakening LEG-09 -- a closed DESTRUCTIVE gate still never skips the explicit
      unlock step, proven as a NEW test beside (never inside) any Phase-133 named proof"
    verification:
      - kind: unit
        ref: "tests/test_chip_test_sdp_leg.py::test_leg09_destructive_gate_never_skips_the_explicit_unlock_step"
        status: pass
      - kind: other
        ref: "git diff -U0 -- tests/test_chip_test_sdp_leg.py | grep '^-' -- zero deletions anywhere"
        status: pass
    human_judgment: false
  - id: D4
    description: "Cleanup de-registration (RESEARCH §4.2's three properties): a completed leg
      unlocks exactly once; an interrupted leg (raises between lock and the explicit unlock step)
      still unlocks exactly once via the drain; a FAILED explicit unlock leaves the handle
      registered so the drain retries (call_count == 2)"
    verification:
      - kind: unit
        ref: "tests/test_chip_test_sdp_leg.py::test_deregistration_completed_leg_unlocks_exactly_once"
        status: pass
      - kind: unit
        ref: "tests/test_chip_test_sdp_leg.py::test_deregistration_interrupted_leg_still_unlocks_exactly_once_via_drain"
        status: pass
      - kind: unit
        ref: "tests/test_chip_test_sdp_leg.py::test_deregistration_failed_explicit_unlock_retries_via_drain_twice"
        status: pass
    human_judgment: false
  - id: D5
    description: "sdp_hold_state: pure engine-side HELD/NOT-HELD/NOT-RUN(reason) derivation, always
      a str, never inside DiagnosticReport (the inversion guard stays green); sdp_oracle_applicable
      True for ALLOW (both write_scope shapes), False for REFUSE (both write_scope shapes)"
    verification:
      - kind: unit
        ref: "tests/test_chip_test_sdp_leg.py -k hold (8 tests, all pass)"
        status: pass
      - kind: unit
        ref: "tests/test_op_registration_parity.py::test_non_registry_still_has_no_ops"
        status: pass
      - kind: unit
        ref: "tests/test_chip_test_sdp_leg.py::test_oracle_applicable_true_for_allow_chip_full_and_none_scope"
        status: pass
      - kind: unit
        ref: "tests/test_chip_test_sdp_leg.py::test_oracle_applicable_false_for_refuse_chip_full_and_none_scope"
        status: pass
    human_judgment: false
  - id: D6
    description: "Non-vacuity obligation #6: OP_SDP_LOCK planted out of _SDP_LEG_GATED_OPS,
      observed RED (a lock genuinely emitted at a dead-write-path part), restored byte-identically,
      re-run green -- verbatim output below"
    verification:
      - kind: other
        ref: "manual RED-then-restore cycle, verbatim output in this SUMMARY's own section below"
        status: pass
    human_judgment: false

# Metrics
duration: 38min
completed: 2026-08-04
status: complete
---

# Phase 134 Plan 04: The Baseline Gate, Cleanup De-registration, and the Hold-State Derivation Summary

**Wired a run-time gate that refuses to emit an SDP lock at a chip whose write path did not
transition in both directions (D-08/D-20), fixed the cleanup registry's now-live double-unlock
risk, added the pure `HELD`/`NOT-HELD`/`NOT-RUN` derivation the report layer will carry, and
observed the gate genuinely absent once before proving it present.**

## Performance

- **Duration:** 38 min
- **Started:** 2026-08-04T16:33:34Z (134-03's last commit; this plan's context-reading began here)
- **Completed:** 2026-08-04T17:11:37Z (last task commit, submodule)
- **Tasks:** 3
- **Files modified:** 3, all inside `firestarter_app` submodule (1 production, 2 test)

## Accomplishments

- Added `_baseline_closes_sdp_gate(result) -> bool` to `chip_test.py`, sited immediately after
  `_id_step_closes_gate` (its structural template) but deliberately WIDER: it closes on BAD,
  `marginal`, `SKIPPED` **and** `NA` -- not `_id_step_closes_gate`'s narrower `(BAD, SKIPPED)`
  tuple -- because a contact fault is as disqualifying as a proven-dead write path for the
  decision to send an irreversible command.
- Added `_SDP_BASELINE_OPS` (the gate's inputs: `write-baseline-b`/`write-baseline-a`) and
  `_SDP_LEG_GATED_OPS` (its outputs: `sdp-lock`, `write-inhibited`, `sdp-unlock`,
  `write-restored`) beside `_SDP_LEG_OPS`. `OP_SDP_UNLOCK`'s membership in the gated set is **D-20**
  (operator decision 2026-08-04), which supersedes D-08's own literally-written clause ("sdp-unlock
  is never attempted because nothing was locked") -- that clause was measured-wrong, since
  `OP_SDP_UNLOCK` is deliberately absent from `_DESTRUCTIVE_OPS` (LEG-09) and would otherwise run
  and report OK at a part that was never locked (the P-06 emission-claim shape).
- Wired three sites in `run_plan`: a `baseline_gate_closed` local (sticky, init `False`) and an
  `unlock_cleanup: Callable[[], None] | None` handle at init; a guard clause immediately AFTER the
  chip-ID destructive gate and BEFORE `_run_step` (order is load-bearing -- the chip-ID gate fires
  first and renders its own wording, so a write-path closure is never misattributed to a chip-ID
  mismatch); a set clause immediately after the id-gate set clause that ORs `baseline_gate_closed`
  from `_baseline_closes_sdp_gate(result)` whenever the just-run step is one of `_SDP_BASELINE_OPS`
  -- sticky by construction, so a failing `write-baseline-b` followed by a passing
  `write-baseline-a` cannot reopen it (both baseline directions always run regardless of the
  gate's own state, since they are what decide it).
- Cleanup de-registration (RESEARCH §4.2): the lock-to-cleanup registration site now also assigns
  `unlock_cleanup = _unlock_cleanup`; a sibling clause, when the explicit `sdp-unlock` step reports
  `VERDICT_OK` and `unlock_cleanup` is not `None`, calls `cleanup.remove(unlock_cleanup)` (by
  VALUE, never by wiping the whole registry) and resets the handle to `None`. A **failed** explicit
  unlock deliberately leaves the handle registered so the `finally` drain still retries it. Neither
  `_dispatch_sdp`'s frozen signature, `count_applicable`, nor the drain loop itself were touched
  (confirmed via `git diff`).
- `test_op_registration_parity.py`: added `_SDP_BASELINE_OPS`/`_SDP_LEG_GATED_OPS` to
  `_REGISTRY_CONSTANT_NAMES` per the plan's own instruction to run the suite and follow its
  failure output -- this addition proved currently INERT (see Decisions below); the suite passed
  unchanged before and after. Deliberately NOT added to `_POLICED_REGISTRIES`, per the plan's
  explicit reasoning (policy subsets of the already-policed `_SDP_LEG_OPS`).
- Added `SDP_HOLD_HELD`/`SDP_HOLD_NOT_HELD`/`SDP_HOLD_NOT_RUN` report-value constants (no `OP_`
  prefix, commented so they are never mistaken for op vocabulary), `sdp_oracle_applicable(plan)`
  (structural: `True` iff the plan carries a runnable `write-inhibited` entry, whether a real step
  or a `locked_destructive` pair), and `sdp_hold_state(plan, results) -> str` -- pure, no logger,
  no I/O, composing `sdp_honesty.unreadable_state_caveat()` for its fixed-prose fallback rather
  than re-authoring a sentence. Deliberately NOT inside `DiagnosticReport`: that class is a declared
  non-registry re-measured every run by `test_non_registry_still_has_no_ops`'s AST inversion guard
  to carry zero op vocabulary; three independent reasons (the inversion guard, P-07's fail-open
  handler allow-list, and the mypy strict-island budget) keep this in the engine.
- Added 8 tests selected by `pytest -k "hold"` covering every branch (OK->HELD, BAD->NOT-HELD,
  each of NA/SKIPPED/marginal->NOT-RUN(reason), the step-absent-from-`results` case -- laundering
  route R6 -- and the empty-reason fallback), each asserting `isinstance(value, str)`, plus 2 tests
  proving `sdp_oracle_applicable`'s ALLOW/REFUSE polarity across both `write_scope` shapes.
- Added the gate's closure proofs (any-non-OK verdict, parametrized over BAD/marginal/SKIPPED/NA,
  plus an OK non-vacuity mirror), the stickiness proof, the gh#20-shape full-leg proof (AT28C256 +
  `_dead_write_path_operator()`, all four SDP-leg-gated steps SKIPPED with `"no lock was emitted"`
  in the reason and never `_DESTRUCTIVE_GATE_REASON`'s wording, `operator.sdp_lock` never called),
  the LEG-09 distinction pin (a NEW test, no Phase-133 proof edited), and the three
  cleanup-de-registration properties (exactly-once on completion, exactly-once via the drain on an
  interrupted leg, twice on a failed explicit unlock).
- Named the baseline gate the **SEVENTH** route to a non-running oracle (beyond research's R1-R6)
  in a module-level comment beside the new tests, recording that it fails closed under D-08+D-15
  and is tested in the same family so plan `134-10`'s six-route test does not read as exhaustive.
- Observed non-vacuity obligation #6 RED once (a lock genuinely emitted against the dead-write-path
  fixture once `OP_SDP_LOCK` was removed from `_SDP_LEG_GATED_OPS`), then restored `chip_test.py`
  byte-identically (verbatim output below) and re-ran green.
- **Ticked NOTHING** in `.planning/REQUIREMENTS.md` -- confirmed by `git status`/`git diff` showing
  no change to that file. LEG-09/10/11/15 (already `[x]`, Phase 133) were re-verified untouched:
  zero deletions inside any Phase-133 named proof (`git diff -U0`).

## Task Commits

Each task was committed atomically, inside the `firestarter_app` submodule on
`gsd/v1.30-sdp-surface-retirement`:

1. **Task 1: `_baseline_closes_sdp_gate`, its three `run_plan` wiring sites, and the cleanup
   de-registration** - `17947f2` (feat) -- this commit also carries Task 2's production code
   (`sdp_hold_state`/`sdp_oracle_applicable`/the three constants), authored together before the
   first commit boundary; see Decisions.
2. **Task 2: `sdp_hold_state`'s three-valued derivation, engine-side only** - `9b416aa` (test) --
   the 8 `pytest -k "hold"` tests plus the 2 `sdp_oracle_applicable` tests.
3. **Task 3: gate + de-registration proofs, the LEG-09 distinction pin, and non-vacuity #6** -
   `4c5d267` (test)

**Plan metadata:** committed with this SUMMARY (docs: complete plan), in the meta repo.

## Files Created/Modified

- `firestarter_app/firestarter/chip_test.py` -- `_SDP_BASELINE_OPS`/`_SDP_LEG_GATED_OPS` module
  frozensets; `_baseline_closes_sdp_gate`; `run_plan`'s three wiring sites plus the
  `unlock_cleanup` de-registration handle; `SDP_HOLD_HELD`/`SDP_HOLD_NOT_HELD`/`SDP_HOLD_NOT_RUN`;
  `sdp_oracle_applicable`; `sdp_hold_state`; the `sdp_honesty` import.
- `firestarter_app/tests/test_op_registration_parity.py` -- `_SDP_BASELINE_OPS`/
  `_SDP_LEG_GATED_OPS` added to `_REGISTRY_CONSTANT_NAMES` (inert but harmless) with a comment
  recording why they are deliberately NOT in `_POLICED_REGISTRIES`.
- `firestarter_app/tests/test_chip_test_sdp_leg.py` -- 8 hold-state tests + 2 oracle-applicable
  tests (Task 2); the gh#20-shape full-leg proof, the parametrized any-non-OK closure test, the
  OK non-vacuity mirror, the stickiness proof, the LEG-09 distinction pin, and the three
  de-registration proofs, plus the module comment naming the seventh route (Task 3).

## Decisions Made

- **Both baseline directions always run regardless of the gate's own state** -- only the four
  `_SDP_LEG_GATED_OPS` members are skipped once it closes. This is a measured, deliberate reading
  of the plan's own action text (the `_SDP_LEG_GATED_OPS` set is explicitly four members, not six)
  over an alternative reading that would also gate `write-baseline-a`; it is also what makes the
  gate's stickiness meaningful at all (nothing to "reopen" if baseline-a never ran).
- **MEASURED DISCREPANCY, recorded rather than silently reconciled** (the same project convention
  134-02-SUMMARY.md set with its "exactly two" finding): 134-CONTEXT.md D-20 and this plan's own
  `<behavior>`/`<action>` text state gh#20's shape produces `n_ran=5, m_applicable=10`. The
  **actual measured value**, run live against AT28C256 driven by `_dead_write_path_operator()`, is
  **`n_ran=6, m_applicable=10`** -- `write-baseline-a` reports OK against this fixture (expected
  read-back A, fixture always returns A) and is never itself gated, so it counts as ran alongside
  `write-baseline-b` and the four shipped ops (read/blank-check/write/verify): 6 ran, 4 SKIPPED,
  out of 10 applicable. The committed test (`test_baseline_gate_closes_dead_write_path_allow_chip_
  full_leg`) asserts the correct measured value of 6, with the discrepancy explained in its own
  docstring rather than weakened or hidden to match the stated 5. This does not affect LEG-13's
  ratio-drop claim (the ratio still drops, from 4-of-4 today to 6-of-10 under this leg) or D-15's
  exit-floor reasoning -- only the specific numeral quoted in 134-CONTEXT.md/this plan's text.
- **`_SDP_BASELINE_OPS`/`_SDP_LEG_GATED_OPS` added to `_REGISTRY_CONSTANT_NAMES` but the addition
  is currently INERT** -- neither set is referenced inside `_dispatch_step`/`derive_plan`/
  `_dispatch_multi_run`, the only three functions `_op_names_referenced_in` ever AST-walks; both
  sets are referenced only inside `run_plan`, which that helper never scans. The parity suite (7
  tests) passed byte-identically before and after this addition -- no guard demanded it, but the
  plan's own instruction ("declare them if a guard demands it, follow the failure output") was
  followed literally: the suite was run, it stayed green, and the declaration was kept anyway as
  harmless and consistent with the module's stated "anything transitively resolvable belongs here"
  discipline. Deliberately NOT added to `_POLICED_REGISTRIES`, exactly as instructed.
- **`sdp_hold_state` accepts `(plan, results)` but derives everything from `results` alone** in
  this revision -- `plan` is accepted for signature symmetry with `count_applicable`'s own
  two-argument shape, so a future NOT-RUN-reason refinement has it available without a call-site
  change across the codebase.
- **Task 2's production code landed inside Task 1's commit** rather than its own: `sdp_hold_state`/
  `sdp_oracle_applicable`/the three `SDP_HOLD_*` constants were authored in the same editing pass
  as Task 1's gate machinery, before the first commit boundary was reached, so `17947f2` (nominally
  "Task 1") also carries all of Task 2's `chip_test.py` changes. This is a minor procedural
  deviation from the plan's literal per-task `<files>` lists -- documented here rather than
  silently absorbed. Task 2's own commit (`9b416aa`) still carries its FULL test obligation (the 8
  `pytest -k "hold"` tests plus the 2 `sdp_oracle_applicable` tests), cleanly separated from Task
  3's gate/de-registration/LEG-09 tests via a reconstructed intermediate file state that was
  independently verified `ruff`-clean, `ruff format`-clean, and green (178 passed) before being
  committed on its own.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Two comments literally spelled the forbidden `cleanup.clear()` substring,
tripping the acceptance criterion's own grep**
- **Found during:** Task 1, self-check against the plan's own acceptance criteria
  (`grep -c 'cleanup.clear()' firestarter/chip_test.py` must return 0)
- **Issue:** Two explanatory comments (in the `unlock_cleanup` handle's own comment and the
  de-registration sibling clause) used the literal phrase `` `cleanup.clear()` `` to describe what
  NOT to do -- a plain-text `grep` cannot distinguish a comment from code, so the acceptance
  criterion's own check would have failed on prose, not on a real `.clear()` call.
- **Fix:** Reworded both comments to describe the same discipline ("never by wiping the whole
  registry") without spelling out the literal `cleanup.clear()` call syntax.
- **Files modified:** `firestarter/chip_test.py`
- **Verification:** `grep -c 'cleanup.clear()' firestarter/chip_test.py` returns 0; the code itself
  never called `.clear()` at any point (this was a documentation-only fix).
- **Commit:** `17947f2`

**2. [Rule 1 - Bug] `_SDP_BASELINE_OPS`/`_SDP_LEG_GATED_OPS` needed for the tests were not yet
importable from the intermediate (Task-2-only) file state**
- **Found during:** the manual split of Task 2/Task 3 test commits
- **Issue:** splitting the single authored block of new tests into two commits required
  temporarily removing the `_baseline_closes_sdp_gate` import (unused in the Task-2-only slice,
  which `ruff` correctly flagged as F401) before that intermediate commit, then restoring it for
  the full Task-3 commit.
- **Fix:** verified both intermediate and final states independently with `ruff check`,
  `ruff format --check`, and a full targeted pytest run before each commit.
- **Files modified:** `tests/test_chip_test_sdp_leg.py` (import list only, no test logic affected)
- **Commit:** `9b416aa` (intermediate), `4c5d267` (final)

---

**Total deviations:** 2 auto-fixed (1 documentation-only Rule 1 fix caught by the plan's own
acceptance-criteria grep; 1 mechanical import-list adjustment required by the manual commit split,
itself documented as a procedural deviation above).
**Impact on plan:** Neither affects behavior. No scope creep.

## Non-Vacuity Obligation #6 (RED output, verbatim)

Removed `OP_SDP_LOCK` from `_SDP_LEG_GATED_OPS` in `firestarter/chip_test.py` (the frozenset became
`{OP_WRITE_INHIBITED, OP_SDP_UNLOCK, OP_WRITE_RESTORED}`), then ran
`pytest tests/test_chip_test_sdp_leg.py -k "test_baseline_gate_closes_dead_write_path_allow_chip_full_leg" -o addopts="" -q`:

```
FAILED tests/test_chip_test_sdp_leg.py::test_baseline_gate_closes_dead_write_path_allow_chip_full_leg
AssertionError: 'sdp-lock' verdict was 'OK', expected SKIPPED once the baseline gate closed
assert 'OK' == 'SKIPPED'
  - SKIPPED
  + OK
1 failed, 78 deselected in 0.10s
```

Followed by a direct measurement of the operator double, confirming the lock was genuinely
**emitted** (not merely mis-reported):

```
sdp_lock.called = True
sdp_lock.call_args = call('AT28C256', {'memory-size': 32768, 'algorithm': 13, 'pin-count': 28,
'vpp_mv': 12000, 'pulse-delay': 0, 'chip-id': 0,
'bus-config': {'bus': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 15], 'rw-pin': 14}, 'flags': 0})
```

This is gh#20's exact hazard, reproduced live: with `OP_SDP_LOCK` outside the gated set, a
dead-write-path run on an ALLOW chip genuinely calls `operator.sdp_lock` -- exactly the "lock a
part that cannot be rewritten" outcome T-134-14 exists to prevent. Restored `chip_test.py`
byte-identically (`diff` against the pre-break copy showed zero differences; `git diff --stat
firestarter/chip_test.py` against the committed state was empty); re-ran the full quick set --
`215 passed` (`tests/test_chip_test_sdp_leg.py tests/test_chip_test.py tests/test_dev_test_cmd.py
tests/test_op_registration_parity.py`).

## Issues Encountered

None beyond the deviations documented above.

## User Setup Required

None -- no external service configuration required.

## Threat Flags

None new. This plan's `<threat_model>` (T-134-14/15/16/17/18) is fully covered by the
implementation as written: T-134-14 (a lock emitted at an unrewritable part) is mitigated by
`_baseline_closes_sdp_gate` and proven absent-then-present by non-vacuity obligation #6, above;
T-134-15 (`sdp-unlock OK` as a false last word) is mitigated by D-20's gated-set membership,
proven by the gh#20-shape test's four-SKIPPED assertion; T-134-16 (wrong-cause wording) is
mitigated by asserting against the imported `_DESTRUCTIVE_GATE_REASON` constant directly (never a
hardcoded string copy) in the same test; T-134-17 (double unlock emission) is mitigated by the
three de-registration property tests; T-134-18 (a boolean read as ground truth) is mitigated by
`sdp_hold_state` returning `str` in every branch, asserted directly.

## Next Phase Readiness

- `_baseline_closes_sdp_gate`, `_SDP_BASELINE_OPS`, `_SDP_LEG_GATED_OPS`, and the de-registration
  handle are the mechanism plan `134-05` (LEG-06's exit-code half, D-14's precedence fix) and plan
  `134-10` (the six R1-R6 laundering-route tests, now joined by this plan's seventh route) both
  depend on.
- `sdp_hold_state`/`sdp_oracle_applicable`/the three `SDP_HOLD_*` constants are the derivation half
  plan `134-06` (the `DiagnosticReport` field + `SCHEMA_VERSION` bump) and `134-07` (the two
  rendered surfaces) close LEG-12 against.
- **Contributes to but does NOT tick:** LEG-06 (134-05's to close), LEG-12 (134-06/134-07's to
  close), LEG-17 (134-10's to close), LEG-13 (134-10's pinning test, though the ratio-drop
  mechanism itself needed no new counting logic here, per D-15).
- The MEASURED DISCREPANCY (n_ran=6, not the stated 5) should be carried into plan 134-10's own
  record and Phase 137's ledger, alongside 134-02's "exactly two" finding, so a later reader does
  not encounter the "5"/"six SKIPPED" figures in 134-CONTEXT.md/ROADMAP prose and assume this
  plan's test is wrong instead.
- No blockers. mypy headroom unchanged at 2 (33/35, `checked` unchanged at 124 -- no new source
  modules added this plan, only additions to two existing test files and one existing production
  module). Full suite: 1391 passed (up from 1370 at 134-03's close; 21 new tests), coverage
  82.09% (>= 70% floor), 30 snapshots unchanged. `tools/ci_replica_venv.sh`: all 5 legs green.

## Self-Check: PASSED

- `firestarter_app/firestarter/chip_test.py` -- FOUND, contains `def _baseline_closes_sdp_gate(`,
  `_SDP_BASELINE_OPS`, `_SDP_LEG_GATED_OPS`, `baseline_gate_closed`, `unlock_cleanup`,
  `def sdp_hold_state(`, `def sdp_oracle_applicable(`, `SDP_HOLD_HELD`.
- `firestarter_app/tests/test_op_registration_parity.py` -- FOUND, 7/7 tests pass.
- `firestarter_app/tests/test_chip_test_sdp_leg.py` -- FOUND, 79/79 tests in this file pass.
- Commit `17947f2` (submodule) -- FOUND in `git -C firestarter_app log --oneline --all`.
- Commit `9b416aa` (submodule) -- FOUND in `git -C firestarter_app log --oneline --all`.
- Commit `4c5d267` (submodule) -- FOUND in `git -C firestarter_app log --oneline --all`.

---
*Phase: 134-the-plan-derived-sdp-oracle-in-dev-test*
*Completed: 2026-08-04*
