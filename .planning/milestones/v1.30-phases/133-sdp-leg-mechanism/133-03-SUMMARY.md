---
phase: 133-sdp-leg-mechanism
plan: 03
subsystem: testing
tags: [chip_test, dispatch, sdp, pytest, ruff, mypy]

# Dependency graph
requires:
  - phase: 133-sdp-leg-mechanism (plan 02)
    provides: "_run_step widened to four except clauses in D-08 order; the
      three-constant precedence-matrix mechanism; the operator-double
      harness with sdp_lock/sdp_unlock pre-added"
provides:
  - "OP_SDP_LOCK = \"sdp-lock\" / OP_SDP_UNLOCK = \"sdp-unlock\" -- the
    engine's SDP op vocabulary (exactly two strings, D-02)"
  - "_SDP_OPS frozenset -- the live dispatch allow-list _dispatch_sdp
    refuses outside of, referenced by _dispatch_step's arm 5"
  - "_DESTRUCTIVE_OPS now contains OP_SDP_LOCK (gated by the id-first
    destructive gate) but deliberately excludes OP_SDP_UNLOCK -- the
    asymmetry that IS LEG-09"
  - "_MULTI_RUN_OPS extended with an explicit, reasoned exclusion of both
    SDP ops (D-03) -- one of plan 133-06's future asserted parity
    exemptions"
  - "_dispatch_sdp(op, name, eprom_data, operator) -> StepResult -- clones
    _dispatch_multi_run's guard/branch/terminal-raise shape; forward
    contract for Phase 134 (signature matches _dispatch_multi_run's first
    four positional params)"
  - "_dispatch_step's arm 5: `if step.op in _SDP_OPS: return
    _dispatch_sdp(...)`, positioned LAST immediately above the terminal
    fail-closed return, proven by a mutation-tested sentinel to add zero
    branching cost to the seven shipped ops"
  - "No Step.group field added -- criterion 4's group=None vacuity is
    recorded in-source and in this SUMMARY, not smoothed over"
affects: [133-04, 133-05, 133-06, 133-07, 134]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Guard -> per-op branch -> terminal `else: raise AssertionError`
      dispatch shape, cloned structurally (not imported/reused) for a
      second dispatch family in the same module"
    - "Arm-order sentinel that WIDENS the allow-list under test
      (monkeypatching _SDP_OPS to also match every shipped op) rather than
      merely mocking the dispatch target -- this is what makes a
      behavioural test sensitive to ARM POSITION rather than only to
      op-string disjointness"

key-files:
  created: []
  modified:
    - firestarter_app/firestarter/chip_test.py
    - firestarter_app/tests/test_chip_test_sdp_leg.py

key-decisions:
  - "OP_SDP_LOCK is IN _DESTRUCTIVE_OPS; OP_SDP_UNLOCK is deliberately OUT
    -- LEG-09's asymmetry, both halves carrying their reason in-source"
  - "The as-planned sentinel design (mock _dispatch_sdp, drive shipped ops,
    assert not called) was found to be VACUOUS against the plan's own
    prescribed deliberate-break mutation (moving the arm above OP_ID) --
    disjoint op-string sets make _dispatch_sdp uncallable for shipped ops
    regardless of arm position. Redesigned to also widen _SDP_OPS
    (monkeypatched) to match every shipped op for the test's duration, so
    the sentinel is now sensitive to ARM ORDER, not merely to naming.
    Mutation-proved: see below."
  - "_dispatch_sdp placed physically in the source right after
    _dispatch_multi_run (before the N-of-M banner data section), not
    immediately after _dispatch_step -- groups it with the function whose
    shape it clones"

requirements-completed: []
# LEG-09 is named in this plan's frontmatter because this plan lands the
# _DESTRUCTIVE_OPS asymmetry the requirement describes, but this plan does
# NOT tick LEG-09 -- its two required behavioural tests (gate-closed-from-
# the-start / lock-ran-then-gate-closes) need the cleanup registry plan
# 133-04 builds. .planning/REQUIREMENTS.md was not touched -- verified
# below. Only 133-07 may mark LEG-09 Complete.

coverage:
  - id: D1
    description: "OP_SDP_LOCK/OP_SDP_UNLOCK op strings and the _SDP_OPS
      dispatch allow-list added; _DESTRUCTIVE_OPS asymmetry set
      (OP_SDP_LOCK in, OP_SDP_UNLOCK out); _MULTI_RUN_OPS exclusion
      reasoned (D-03)"
    requirement: "LEG-09"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_chip_test_sdp_leg.py#test_unlock_exempt_from_destructive"
        status: pass
      - kind: other
        ref: "inline python constants check (CONSTANTS_OK) + AST walk over module-level OP_* assigns (9 total)"
        status: pass
    human_judgment: false
  - id: D2
    description: "_dispatch_sdp added: guard refuses foreign ops with a
      caller-visible BAD/run_count=0 StepResult touching the operator not
      at all; per-op branches map sdp_lock/sdp_unlock bool return to
      OK/BAD; terminal else raises AssertionError (fail-closed, not a bare
      else)"
    requirement: "LEG-09"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_chip_test_sdp_leg.py#test_dispatch_sdp_guard_refuses_foreign_op"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_chip_test_sdp_leg.py#test_dispatch_sdp_terminal_assertion_is_reachable_only_by_bypassing_the_guard"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_chip_test_sdp_leg.py#test_dispatch_sdp_maps_bool_to_verdict"
        status: pass
    human_judgment: false
  - id: D3
    description: "_dispatch_sdp wired as arm 5 (LAST) of _dispatch_step,
      immediately above the terminal fail-closed return; proven by a
      mutation-tested sentinel that the seven shipped ops never evaluate
      the new membership test with zero added branching cost; Step
      dataclass gained no new field (D-05 vacuity recorded in-source)"
    requirement: "LEG-09"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_chip_test_sdp_leg.py#test_shipped_ops_never_reach_sdp_arm"
        status: pass
      - kind: other
        ref: "AST inspection: _SDP_OPS test is the last If before the final Return; inspect.signature on _dispatch_sdp (4 positional params); AST body shape (If guard / If-Elif branch / else Raise)"
        status: pass
    human_judgment: false

# Metrics
duration: ~65min
completed: 2026-08-04
status: complete
---

# Phase 133 Plan 03: SDP Leg Mechanism -- Dispatch Arm Summary

**Two new op strings (`sdp-lock`/`sdp-unlock`), the `_SDP_OPS` allow-list, a `_dispatch_sdp` guard/branch/terminal-raise arm cloned structurally from `_dispatch_multi_run`, wired LAST in `_dispatch_step` and mutation-proved (not merely asserted) to add zero branching cost to the seven shipped ops -- plus the `_DESTRUCTIVE_OPS` asymmetry (`OP_SDP_LOCK` in, `OP_SDP_UNLOCK` deliberately out) that is LEG-09 itself.**

## Performance

- **Duration:** ~65 min
- **Completed:** 2026-08-04 (approx)
- **Tasks:** 3
- **Files modified:** 2

## Accomplishments

- Added exactly two op strings (`OP_SDP_LOCK = "sdp-lock"`, `OP_SDP_UNLOCK = "sdp-unlock"`) and the `_SDP_OPS` frozenset allow-list, each with a safety-argument comment (not a description) citing the module's own documented-but-dead-frozenset precedent (`_MULTI_RUN_OPS`).
- Set the `_DESTRUCTIVE_OPS` asymmetry that is LEG-09: `OP_SDP_LOCK` joins the frozenset (gated by the id-first destructive gate -- a lock on a misidentified chip is exactly the harm that gate prevents); `OP_SDP_UNLOCK` is deliberately absent, qualified in-source as forward-protection for Phase 134 and explicitly NOT a live Phase 133 path.
- Extended `_MULTI_RUN_OPS`'s comment with D-03's exclusion reason for both SDP ops (a lock/unlock's result cannot be read back at all on this family, so the marginal-on-disagreement policy is meaningless for it) -- this exclusion is one of plan 133-06's future asserted parity exemptions.
- Added `_dispatch_sdp(op, name, eprom_data, operator)`: structurally clones `_dispatch_multi_run`'s guard/branch/terminal-`AssertionError` shape (not imported/reused); the signature is a forward contract Phase 134 builds four ops on.
- Wired the new arm as arm 5 of `_dispatch_step`, immediately above the terminal fail-closed `return`, so the measured order is `OP_ID -> OP_BLANK_CHECK -> OP_READ -> _MULTI_RUN_OPS -> _SDP_OPS -> terminal`.
- No `Step.group` field added (D-05); the arm keys on `_SDP_OPS` membership of the op string itself. ROADMAP criterion 4's `group=None` clause is recorded in-source as satisfied VACUOUSLY (there is no such field), with the criterion's *intent* met by arm placement + the sentinel test instead.
- Added five new tests to `tests/test_chip_test_sdp_leg.py` (the standing `_DESTRUCTIVE_OPS` invariant, the guard's foreign-op refusal, the terminal-assertion reachability proof, the bool-to-verdict mapping, and D-13b's arm-order sentinel), extended the module docstring's Coverage list, and re-ran the three plans 133-01/02 tests unedited (all green, `_INTENDED_PRECEDENCE_DELTA` unchanged).
- Full suite green: 1314 passed (up from 1306; 8 new tests), 30 snapshots unchanged, `ruff check`/`ruff format --check` clean, mypy 32 errors (watermark 35, checked 123 source files) via `tools/ci_replica_venv.sh` -- unchanged from 133-02's baseline, coverage 81.83% (floor 70%).

## Task Commits

Each task was committed atomically, in the submodule (`firestarter_app`) on `gsd/v1.30-sdp-surface-retirement`:

1. **Task 1: Add OP_SDP_LOCK/OP_SDP_UNLOCK/_SDP_OPS and set the destructive-set asymmetry** -- `ded8e3e` (feat)
2. **Task 2: Add _dispatch_sdp and wire it as the LAST arm of _dispatch_step** -- `9b92b1a` (feat)
3. **Task 3: Prove the arm fails closed, the destructive-set asymmetry holds, and the seven shipped ops never reach it** -- `1761a82` (test)

**Plan metadata:** this SUMMARY's own commit follows this document (meta repo).

## Files Created/Modified

- `firestarter_app/firestarter/chip_test.py` -- two new op constants; `_SDP_OPS` frozenset; `_DESTRUCTIVE_OPS`/`_MULTI_RUN_OPS` comments extended with the D-11/D-03 reasoning; `_dispatch_sdp` added (guard -> branch -> terminal raise); `_dispatch_step` gained arm 5 and an updated docstring. No other function in the module touched (verified: no hunk inside `run_plan`, `_run_step`, `_dispatch_multi_run`, `_sample`, or the `Step` dataclass).
- `firestarter_app/tests/test_chip_test_sdp_leg.py` -- five new tests, `_SHIPPED_OP_STRINGS` list, module docstring Coverage list extended, imports extended (`OP_ID`/`OP_ERASE`/`OP_VERIFY`/`OP_WRITE`/`OP_WRITE_PARTIAL`/`OP_SDP_LOCK`/`OP_SDP_UNLOCK`/`_SDP_OPS`/`_DESTRUCTIVE_OPS`/`_MULTI_RUN_OPS`/`_dispatch_sdp`, `ANY` from `unittest.mock`). No hunk inside `_PRE_EDIT_PRECEDENCE_MATRIX`, `_EXPECTED_PRECEDENCE_MATRIX`, `_INTENDED_PRECEDENCE_DELTA`, or `_SHIPPED_OPS_SEQUENCE`.

## Decisions Made

- **The as-planned sentinel design was vacuous against its own prescribed mutation -- redesigned before committing.** The plan's task 3 action item 5 specifies: monkeypatch `_dispatch_sdp` to raise, drive the seven shipped ops through, assert the sentinel is never called. Implemented verbatim first, then attempted the plan's own required mutation proof (temporarily move the `_SDP_OPS` arm above `OP_ID`) and found the test **still passed** -- because the seven shipped op strings (`"id"`, `"read"`, `"blank-check"`, `"write"`, `"write-partial"`, `"verify"`, `"erase"`) are never members of `_SDP_OPS` (`{"sdp-lock", "sdp-unlock"}`) regardless of where the membership test sits in the arm chain; `_dispatch_sdp` is genuinely uncallable for a shipped op purely by disjoint naming, independent of arm order. Root cause: the as-specified test proves op-string disjointness, not arm placement -- a materially weaker and already-otherwise-proven property. **Fix:** the test now additionally monkeypatches `_SDP_OPS` itself to a widened frozenset containing every shipped op string (in addition to the two real SDP ops) for the test's duration. Under the correct (position-5) placement this changes nothing -- arms 1-4 still return before the widened membership test is ever reached, so the sentinel stays silent. Re-ran the identical arm-reorder mutation against the redesigned test: it now FAILS with the sentinel's own message (see Mutation Proofs below), and passes again once reverted. This is now a genuine mechanical proof of D-04's zero-added-branching-cost claim, not a test that happened to pass for an unrelated reason.
- **`_dispatch_sdp` placed in source immediately after `_dispatch_multi_run`** (before the "Applicable-only N-of-M banner DATA" section comment), grouping it with the function whose guard/branch/terminal-raise shape it clones, rather than immediately after `_dispatch_step`.
- **`_DESTRUCTIVE_OPS`'s comment states plainly that `OP_SDP_UNLOCK`'s absence is forward-protection for Phase 134, not a live Phase 133 path** -- per the plan's explicit instruction not to let the comment imply otherwise.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Corrected `test_shipped_ops_never_reach_sdp_arm`'s design before it was ever committed**
- **Found during:** Task 3, while performing the plan's own mandated mutation proof (acceptance criterion: "the sentinel test has been SEEN to fail" under a deliberate arm reorder)
- **Issue:** the test as literally specified by the plan (mock `_dispatch_sdp`, drive shipped ops, assert not-called) passed both before AND after the deliberate-break mutation, because it only proves op-string disjointness, which holds independent of arm order -- an unproven/vacuous sentinel with respect to the property it claims to mechanically prove (D-04's zero-added-branching-cost claim)
- **Fix:** additionally monkeypatch `_SDP_OPS` to a widened frozenset (shipped ops + real SDP ops) for the test's duration, making the sentinel genuinely sensitive to arm position
- **Files modified:** `firestarter_app/tests/test_chip_test_sdp_leg.py`
- **Verification:** re-ran the identical arm-reorder mutation against the redesigned test -- FAILED with the expected message (verbatim below), reverted, re-passed; full suite still green
- **Committed in:** `1761a82` (Task 3 commit)

---

**Total deviations:** 1 auto-fixed (1 bug in a not-yet-committed test's own design, caught by the plan's own required mutation-proof step before it could ship as a vacuous gate)
**Impact on plan:** No scope creep -- this is exactly the kind of "a pre-authored gate leg proves nothing until it is seen to pass" discipline `133-CONTEXT.md`'s Established Patterns section names, applied to the one leg this plan explicitly required the mutation proof for.

## Issues Encountered

None beyond the sentinel design correction above (documented as a deviation, not an issue, since it was caught and fixed within the same task before any commit).

## Mutation Proofs (verbatim observed failure messages, per plan_specific_warnings)

**1. `test_shipped_ops_never_reach_sdp_arm`, with the `_SDP_OPS` arm temporarily moved above the `OP_ID` arm in `_dispatch_step`** (`if step.op in _SDP_OPS: return _dispatch_sdp(...)` inserted as the first `if`, ahead of `if step.op == OP_ID:`, with the original arm-5 position removed so this was a genuine MOVE, not a duplication):

```
        monkeypatch.setattr(chip_test_mod, "_dispatch_sdp", sentinel)
        # Widen _SDP_OPS to also match every shipped op -- see docstring above
        # for why this is what makes the sentinel sensitive to arm ORDER.
        monkeypatch.setattr(chip_test_mod, "_SDP_OPS", frozenset(shipped_op_set | _SDP_OPS))

        operator = _mock_operator()
        plan = _plan_with_steps(
            *(Step(op=op, supported=True, reason="") for op in _SHIPPED_OP_STRINGS)
        )

>       results = run_plan(plan, operator, _REAL_DB)

firestarter/chip_test.py:836: in run_plan
    result = _run_step(plan.name, step, operator, db, runs=runs, sampler=sampler)
firestarter/chip_test.py:939: in _run_step
    return _dispatch_step(
firestarter/chip_test.py:1015: in _dispatch_step
    return _dispatch_sdp(step.op, name, eprom_data, operator)
/usr/local/lib/python3.12/unittest/mock.py:1139: in __call__
    return self._mock_call(*args, **kwargs)
/usr/local/lib/python3.12/unittest/mock.py:1143: in _mock_call
    return self._execute_mock_call(*args, **kwargs)

self = <Mock id='140206399795088'>
args = ('id', 'M8720', {'memory-size': 262144, 'algorithm': 8, 'pin-count': 32, 'vpp_mv': 12000, ...}, <Mock id='140206399795712'>)

    def _execute_mock_call(self, /, *args, **kwargs):
        effect = self.side_effect
        if effect is not None:
            if _is_exception(effect):
>               raise effect
E               AssertionError: sentinel: a shipped op reached _dispatch_sdp -- D-04's zero-added-branching-cost claim is false (arm 5 placed wrongly)

/usr/local/lib/python3.12/unittest/mock.py:1198: AssertionError
FAILED tests/test_chip_test_sdp_leg.py::test_shipped_ops_never_reach_sdp_arm
1 failed, 16 deselected in 0.40s
```

Reverted (`diff` against the pre-mutation copy of `chip_test.py` showed zero difference); `pytest -k shipped_ops_never_reach_sdp_arm` passed again (1 passed), then the full precision suite (`pytest tests/ -q`) re-ran green (1314 passed, 30 snapshots).

## Measured Values (quoted verbatim per plan `<output>` requirement)

**`_DESTRUCTIVE_OPS` post-edit:** `frozenset({"write", "write-partial", "erase", "sdp-lock"})` -- `OP_SDP_LOCK` in, `OP_SDP_UNLOCK` absent.

**`_MULTI_RUN_OPS` unchanged:** `frozenset({"write", "write-partial", "erase", "verify"})` -- neither SDP op added.

**`_SDP_OPS`:** `frozenset({"sdp-lock", "sdp-unlock"})`.

**AST-verified `_dispatch_step` arm order:** `OP_ID -> OP_BLANK_CHECK -> OP_READ -> (op in _MULTI_RUN_OPS) -> (op in _SDP_OPS) -> terminal Return` -- the `_SDP_OPS` test is the last `If` before the function's final `Return`, confirmed by AST walk (last-If-index == len(body) - 2, final statement is the pre-existing terminal `Return`, unchanged text).

**`inspect.signature(_dispatch_sdp)`:** `(op: 'str', name: 'str', eprom_data: 'dict[str, Any]', operator: 'Any')` -- all four positional-or-keyword, no keyword-only params.

**Suite state at finish:** `pytest tests/ -q` -- 1314 passed (133-02's baseline was 1306; +8 new tests: 5 dispatch-arm tests plus the 3 already-existing regression tests re-verified unedited), 30 snapshots passed (unchanged). `ruff check firestarter/ tests/` and `ruff format --check firestarter/ tests/` both exit 0. `tools/ci_replica_venv.sh`'s full 5-leg run: Leg 1 (venv reuse) exit 0, Leg 2 (numpy absent) exit 0, Leg 3 (ruff) exit 0, Leg 4 (mypy watermark) `Found 32 errors in 12 files (checked 123 source files)` -- `mypy errors: 32 (watermark: 35)`, unchanged from 133-02's baseline, watermark not moved, Leg 5 (`pytest --cov --cov-fail-under=70`) exit 0, `Required test coverage of 70% reached. Total coverage: 81.83%`. `CI-REPLICA: PASS`.

## User Setup Required

None -- no external service configuration required.

## Next Phase Readiness

- `OP_SDP_LOCK`/`OP_SDP_UNLOCK`/`_SDP_OPS`/`_dispatch_sdp` are the vocabulary and dispatch arm Phase 134's four-step leg is built on (ROADMAP Phase 134's "Depends on" line names this arm verbatim); the signature `(op, name, eprom_data, operator)` is the forward contract to build against.
- Plan 133-04's cleanup registry can now register a real `sdp_lock` step's cleanup, since `_dispatch_sdp`'s `OP_SDP_LOCK` branch is live and callable through `run_plan`.
- `.planning/REQUIREMENTS.md` was not touched by this plan (verified: `git diff --name-only HEAD -- .planning/REQUIREMENTS.md` in the meta repo shows no change). LEG-09 remains open pending 133-04's cleanup registry and its two behavioural proofs, before 133-07 ticks it.
- No blockers.

---
*Phase: 133-sdp-leg-mechanism*
*Completed: 2026-08-04*

## Self-Check: PASSED

- FOUND: `firestarter_app/firestarter/chip_test.py`
- FOUND: `firestarter_app/tests/test_chip_test_sdp_leg.py`
- FOUND: `.planning/phases/133-sdp-leg-mechanism/133-03-SUMMARY.md`
- FOUND commit: `ded8e3e` (submodule `firestarter_app`)
- FOUND commit: `9b92b1a` (submodule `firestarter_app`)
- FOUND commit: `1761a82` (submodule `firestarter_app`)
- FOUND commit: `eaa79b4` (meta repo)
