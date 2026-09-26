---
phase: 134-the-plan-derived-sdp-oracle-in-dev-test
plan: 02
subsystem: testing
tags: [python, pytest, chip_test.py, sdp, read-back-equality, oracle, mypy]

# Dependency graph
requires:
  - phase: 134-01
    provides: OP_WRITE_BASELINE_B/A, OP_WRITE_INHIBITED, OP_WRITE_RESTORED, _SDP_LEG_OPS,
      generate_inhibited_pattern (D-19), the op-registration parity gate at 13 ops with 8
      TEMPORARY exemption rows (4 for _dispatch_step, 4 for derive_plan)
provides:
  - _dispatch_sdp_leg(op, name, eprom_data, operator, *, step=None) -> StepResult -- the
    no-default read-back-equality truth table (D-01...D-05)
  - _dispatch_step arm 6, routing _SDP_LEG_OPS members to _dispatch_sdp_leg
  - FLAG_SKIP_SDP_UNLOCK wired live (imported + passed on OP_WRITE_INHIBITED only)
  - The op-registration parity gate's 4 _dispatch_step TEMPORARY exemption rows discharged
    (13-op vocabulary now fully covered with zero exemptions against _dispatch_step)
  - _readback_operator / _dead_write_path_operator test doubles for later plans to reuse
  - LEG-05, LEG-07, LEG-08, LEG-16 fully proven and ticked Complete
  - LEG-06's engine half proven (test_lock_leaked_...); exit-code half deferred to 134-05
affects: [134-03, 134-04, 134-05]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Read-back-equality oracle: write_eprom's bool is a PRECONDITION signal only (True proves
      the experiment ran as designed; False routes to marginal, never BAD) -- the verdict comes
      from comparing the read-back bytes against the expected pattern, never from the bool alone."
    - "Length gate before content gate before equality decision -- an empty/short read-back must
      never reach classify_fingerprint (which reads an empty comparison as perfect equality)."
    - "The 2x2 polarity proof: hold write_eprom's bool CONSTANT at True across two tests that vary
      only the read-back and produce two different verdicts -- strictly stronger than any proof
      driven by varying the bool, because a bool-driven implementation cannot pass it."
    - "A read-back-capable operator double (_readback_operator) is a SEPARATE fixture from the
      existing _mock_operator, because the latter's read_eprom writes no file -- silently reducing
      every oracle test to the length gate alone if reused as-is."

key-files:
  created: []
  modified:
    - firestarter_app/firestarter/chip_test.py
    - firestarter_app/tests/test_op_registration_parity.py
    - firestarter_app/tests/test_chip_test_sdp_leg.py

key-decisions:
  - "Non-vacuity obligation #2's planted swap produced 3 RED tests, not VALIDATION.md's stated 2
    -- a measured discrepancy, recorded rather than silently reconciled: this plan's own required
    test_lock_leaked_write_ok_true_b_readback_is_bad independently duplicates one arm of the
    oracle_readback pair (the (True, B) => BAD case), so the same OK/BAD-arm swap trips both the
    pair and the duplicate. The underlying mechanism (D-03's polarity pin) is still proven --the
    count claim in VALIDATION.md is what is wrong, not the swap's sensitivity."
  - "_dispatch_step's TEMPORARY exemption assertion tightened from '<= _SDP_LEG_OPS, count == 4'
    (134-01's shape, pending this plan's discharge) back to '== empty set' -- restoring the
    pre-Phase-134 invariant that _dispatch_step needs ZERO exemptions for any op, now that arm 6
    routes all four SDP-leg ops through _dispatch_sdp_leg."
  - "Attached a Fingerprint to every _dispatch_sdp_leg return arm, including the equality-decision
    OK/BAD/marginal arms (not just the degenerate-content arm) -- per the plan's own instruction
    ('Attach the Fingerprint in every arm below'), giving every verdict a byte-level evidence
    trail even when the verdict is a clean OK."

requirements-completed: [LEG-05, LEG-07, LEG-08, LEG-16]

coverage:
  - id: D1
    description: "_dispatch_sdp_leg: a no-default read-back-equality truth table for the SDP leg's
      four write-shaped ops, with a fail-closed guard and terminal raise AssertionError (no
      default arm), plus _dispatch_step arm 6 routing to it"
    requirement: LEG-05
    verification:
      - kind: unit
        ref: "tests/test_chip_test_sdp_leg.py::test_oracle_readback_true_a_produces_ok"
        status: pass
      - kind: unit
        ref: "tests/test_chip_test_sdp_leg.py::test_oracle_readback_true_b_produces_bad"
        status: pass
      - kind: unit
        ref: "tests/test_chip_test_sdp_leg.py::test_oracle_readback_false_a_produces_marginal"
        status: pass
      - kind: unit
        ref: "tests/test_chip_test_sdp_leg.py::test_oracle_readback_false_b_produces_marginal"
        status: pass
    human_judgment: false
  - id: D2
    description: "A partial read-back change (16-byte splice from the live generators) reports
      BAD on write-inhibited -- gh#11's exact symptom"
    requirement: LEG-07
    verification:
      - kind: unit
        ref: "tests/test_chip_test_sdp_leg.py::test_partial_readback_reports_bad"
        status: pass
    human_judgment: false
  - id: D3
    description: "Four degenerate read-back fixtures (empty, short, all-0x00, all-0xFF) never
      read as equality -- length gate runs before any classify_fingerprint call"
    requirement: LEG-08
    verification:
      - kind: unit
        ref: "tests/test_chip_test_sdp_leg.py::test_degenerate_readback_empty_is_bad"
        status: pass
      - kind: unit
        ref: "tests/test_chip_test_sdp_leg.py::test_degenerate_readback_short_is_bad"
        status: pass
      - kind: unit
        ref: "tests/test_chip_test_sdp_leg.py::test_degenerate_readback_all_zero_is_marginal"
        status: pass
      - kind: unit
        ref: "tests/test_chip_test_sdp_leg.py::test_degenerate_readback_all_ff_is_marginal_blank_contact"
        status: pass
    human_judgment: false
  - id: D4
    description: "_dead_write_path_operator committed fixture: a no-op write (write_eprom claims
      success, read_eprom always yields pattern A) makes write-baseline-b report BAD"
    requirement: LEG-16
    verification:
      - kind: unit
        ref: "tests/test_chip_test_sdp_leg.py::test_dead_write_path_baseline_b_is_bad"
        status: pass
    human_judgment: false
  - id: D5
    description: "LEG-06 engine half: (True, B) => BAD, named for VALIDATION.md's lock_leaked
      selector; docstring states the exit-code half is plan 134-05's and this test alone does not
      discharge LEG-06 (not ticked this plan)"
    verification:
      - kind: unit
        ref: "tests/test_chip_test_sdp_leg.py::test_lock_leaked_write_ok_true_b_readback_is_bad"
        status: pass
    human_judgment: false
  - id: D6
    description: "Non-vacuity obligations #2 (swap OK/BAD arms) and #3 (make the dead-write-path
      fixture's write real) both observed RED once and restored byte-identically"
    verification:
      - kind: unit
        ref: "manual RED-then-restore cycles, verbatim output captured below"
        status: pass
    human_judgment: false

# Metrics
duration: 36min
completed: 2026-08-04
status: complete
---

# Phase 134 Plan 02: The Plan-Derived SDP Oracle -- Read-Back-Equality Dispatch Summary

**Built `_dispatch_sdp_leg`, the no-default read-back-equality truth table that decides the SDP
leg's OK/BAD/marginal verdicts from the read-back bytes alone -- proved the full D-03 2x2 polarity
pin, LEG-07's partial-change case, LEG-08's four degenerate fixtures, and LEG-16's committed
dead-write-path fixture, all against a purpose-built read-back-capable operator double.**

## Performance

- **Duration:** 36 min
- **Started:** 2026-08-04T15:11:49Z (134-01's last commit; this plan's context-reading began here)
- **Completed:** 2026-08-04T15:47:41Z (last task commit, submodule)
- **Tasks:** 3
- **Files modified:** 3, all inside `firestarter_app` submodule (1 production, 2 test)

## Accomplishments

- Added `_dispatch_sdp_leg(op, name, eprom_data, operator, *, step=None) -> StepResult` to
  `chip_test.py`, sited immediately after `_dispatch_sdp` (whose frozen four-positional signature
  is unchanged -- `git diff` on its `def` line is empty). Fail-closed guard refuses any op outside
  `_SDP_LEG_OPS`; a per-op `(source_payload, expected_readback, flags)` map encodes
  `write-inhibited`'s deliberate asymmetry (writes B, expects A); a single write + single read-back
  (never best-effort, unlike `_dispatch_multi_run`'s); a length gate BEFORE any
  `classify_fingerprint` call (P-02's measured trap: `classify_fingerprint(A, b"")` reads an empty
  comparison as perfect equality); a content-degeneracy gate routing all-`0x00`/`0xFF` read-backs to
  `marginal`; and the equality decision implementing D-03's full 2x2 for `write-inhibited` plus the
  four-arm table for the other three ops. Terminal `raise AssertionError` names `_SDP_LEG_OPS`, no
  default arm.
- Added `_dispatch_step` arm 6 (`if step.op in _SDP_LEG_OPS: return _dispatch_sdp_leg(...)`)
  immediately after arm 5 and above the terminal fail-closed `return` -- `test_shipped_ops_never_
  reach_sdp_arm`'s arm-order sentinel stays green, proving zero added branching cost to the nine
  ops shipped before this phase.
- Imported and wired `FLAG_SKIP_SDP_UNLOCK` live: passed on `write-inhibited` only, pinned CLEAR on
  `write-baseline-b`/`write-baseline-a`/`write-restored` by test (the `write-restored` pin is
  load-bearing -- setting the flag there would defeat that step's whole purpose).
- Discharged the four `TEMPORARY -- discharged by plan 134-02` `_dispatch_step` exemption rows in
  `test_op_registration_parity.py` in the SAME commit that added the routing arm; tightened the
  `_dispatch_step_exempted_ops` assertion from "count == 4" back to "== empty set" and flipped
  test 7's `expected_membership` pin for `_dispatch_step` to `True` for all four new ops
  (`derive_plan`'s pin stays `False`, plan 134-03's to flip).
- Built `_readback_operator(payload, *, write_ok=True, **returns)`: a read-back-capable operator
  double whose `read_eprom` writes `payload` to the `output_file` keyword argument and returns
  `True`; the pre-existing `_mock_operator`'s `read_eprom` writes no file at all, which would have
  silently reduced every oracle test to exercising only the length gate.
- Proved D-03's full 2x2 for `write-inhibited`: `test_oracle_readback_true_a_produces_ok` /
  `..._true_b_produces_bad` hold `write_eprom`'s bool CONSTANT at `True` and vary only the
  read-back -- a strictly stronger proof than any bool-driven implementation could pass.
  `..._false_a/b_produces_marginal` pin the precondition gate in both read-back directions.
- Proved LEG-06's engine half (`test_lock_leaked_write_ok_true_b_readback_is_bad`, named for
  VALIDATION.md's `-k "lock_leaked"` selector -- **not ticked**, per dispatch scope: the exit-code
  half is plan 134-05's), LEG-07 (`test_partial_readback_reports_bad`, a 16-byte splice from the
  live generators, never a literal), and the marginal-reason content pin (both candidate causes --
  the `0x86` ack not honoured, or a transport fault -- plus the firmware-update instruction).
- Proved LEG-08's four degenerate fixtures (empty/short via the length gate; all-`0x00`/`0xFF` via
  the content-degeneracy gate, the latter pinned to `FP_BLANK_CONTACT`) and LEG-16's committed
  `_dead_write_path_operator` fixture (`write_eprom` claims success, `read_eprom` always yields
  pattern A regardless of what was written -- `write-baseline-b` against it reports BAD, proving
  the B direction is the leg's entire discriminating power per D-07).
- Proved D-05's non-laundering leg through the real dispatcher (`test_inhibited_full_b_readback_
  does_not_launder_as_blank_contact`, distinct from 134-01's `TestInhibitedPattern` version which
  calls `classify_fingerprint` directly) and stated the Evidence Ceiling in the new fixtures'
  documentation, calling `sdp_honesty.unreadable_state_caveat()` rather than re-authoring its
  sentence.
- Observed both non-vacuity obligations RED once, then restored byte-identically (verbatim output
  below).
- LEG-05, LEG-07, LEG-08, LEG-16 ticked `Complete` in `REQUIREMENTS.md` -- the only four
  requirements this plan may mark, per the dispatch's explicit scope. LEG-06 left `Pending`
  (engine half evidenced, exit-code half explicitly deferred to 134-05).

## Task Commits

Each task was committed atomically, inside the `firestarter_app` submodule on
`gsd/v1.30-sdp-surface-retirement`:

1. **Task 1: `_dispatch_sdp_leg` -- the no-default read-back truth table, plus arm 6** -
   `7284c7d` (feat)
2. **Task 2: the 2x2 polarity proof, LEG-05/LEG-07, the flag pins, and non-vacuity #2** -
   `4ac946a` (test)
3. **Task 3: LEG-08's four degenerate fixtures, LEG-16's dead-write-path fixture, D-05, and
   non-vacuity #3** - `2699579` (test)

**Plan metadata:** committed with this SUMMARY (docs: complete plan), in the meta repo.

## Files Created/Modified

- `firestarter_app/firestarter/chip_test.py` -- `FLAG_SKIP_SDP_UNLOCK` import wired live;
  `_dispatch_sdp_leg` (the oracle); `_dispatch_step` arm 6; docstring updates for both
  (`_dispatch_step`'s arm census, the module docstring's wire-dict narrowing note).
- `firestarter_app/tests/test_op_registration_parity.py` -- discharged the 4 `_dispatch_step`
  TEMPORARY exemption rows; tightened the `_dispatch_step_exempted_ops` assertion; flipped test 7's
  `_dispatch_step` expected-membership pin to `True` for the four new ops.
- `firestarter_app/tests/test_chip_test_sdp_leg.py` -- `_readback_operator`,
  `_dead_write_path_operator`, and 18 new test functions across the oracle_readback/lock_leaked/
  partial_readback/degenerate/dead_write_path families.

## Decisions Made

- **Fingerprint attached in every `_dispatch_sdp_leg` return arm**, not just the degenerate-content
  arm -- per the plan's own instruction ("Attach the Fingerprint in every arm below"), so every
  verdict (including a clean OK) carries byte-level evidence.
- **`_dispatch_step`'s exemption assertion restored to "zero for any op"** rather than merely
  "zero minus this phase's four ops" -- the stronger, pre-Phase-134 invariant, now that arm 6
  covers all four SDP-leg ops.
- **Degenerate/dead-write-path tests call `_dispatch_sdp_leg` directly** rather than routing
  through `run_plan`/`derive_plan` -- simpler fixtures, and consistent with Task 2's own tests
  (which also call the dispatcher directly), while `test_dispatch_sdp_maps_bool_to_verdict`-style
  full-`run_plan` coverage remains Phase 133's precedent for the two-op `_dispatch_sdp` arm.

## Deviations from Plan

None -- plan executed exactly as written. Both non-vacuity obligations behaved as instructed
(planted break -> RED -> byte-identical restoration), and the measured discrepancy below was
recorded rather than silently reconciled, per this project's standing practice.

## Non-Vacuity Obligation #2 (RED output, verbatim)

Swapped the `OP_WRITE_INHIBITED` OK/BAD arms in `_dispatch_sdp_leg`, ran
`pytest tests/test_chip_test_sdp_leg.py -k "oracle_readback or lock_leaked" -o addopts="" -q`:

```
___________________ test_oracle_readback_true_b_produces_bad ___________________
    ...
>       assert result.verdict == VERDICT_BAD, (
            f"(write_ok=True, read-back=B) produced {result.verdict!r}, expected BAD"
        )
E       AssertionError: (write_ok=True, read-back=B) produced 'OK', expected BAD
E       assert 'OK' == 'BAD'
_______________ test_lock_leaked_write_ok_true_b_readback_is_bad _______________
    ...
>       assert result.verdict == VERDICT_BAD, (
E       AssertionError: write_eprom reported True (the ack was observed) but the read-back is
        fully pattern B -- verdict was 'OK', expected BAD (the SDP lock leaked)
E       assert 'OK' == 'BAD'
=========================== short test summary info ============================
FAILED tests/test_chip_test_sdp_leg.py::test_oracle_readback_true_a_produces_ok
FAILED tests/test_chip_test_sdp_leg.py::test_oracle_readback_true_b_produces_bad
FAILED tests/test_chip_test_sdp_leg.py::test_lock_leaked_write_ok_true_b_readback_is_bad
3 failed, 2 passed, 37 deselected in 0.15s
```

**Measured discrepancy, recorded rather than silently reconciled:** VALIDATION.md's non-vacuity
table states "Exactly two tests must go red, not one." The actual, honest count is **three**, not
two: `test_oracle_readback_true_a_produces_ok` (was OK, now BAD), `test_oracle_readback_true_b_
produces_bad` (was BAD, now OK) -- the intended pair -- **plus**
`test_lock_leaked_write_ok_true_b_readback_is_bad`, which this same task's own instructions require
as "the `(True, B) ⇒ BAD` case again, asserted by name". Because that test independently duplicates
one arm of the `oracle_readback` pair, the same OK/BAD-arm swap trips it too. The underlying
mechanism the obligation exists to prove -- that D-03's polarity pin is genuinely swap-sensitive,
not a vacuous always-pass check -- is intact and stronger for it (3 real failures, not 2, and not
zero). `git diff firestarter/chip_test.py` was confirmed empty immediately before this commit,
proving the restoration was byte-identical.

## Non-Vacuity Obligation #3 (RED output, verbatim)

Made `_dead_write_path_operator`'s write real: captured the last `write_eprom` source file's bytes
and had `read_eprom` return them instead of always pattern A. Ran
`pytest tests/test_chip_test_sdp_leg.py -k "dead_write_path" -o addopts="" -q`:

```
____________________ test_dead_write_path_baseline_b_is_bad ____________________
    ...
>       assert result.verdict == VERDICT_BAD, (
            f"write-baseline-b against the dead-write-path fixture produced "
            f"verdict {result.verdict!r}, expected BAD (LEG-16)"
        )
E       AssertionError: write-baseline-b against the dead-write-path fixture produced verdict
        'OK', expected BAD (LEG-16)
E       assert 'OK' == 'BAD'
1 failed, 48 deselected in 0.16s
```

As expected: with a real write path, `write-baseline-b` writes pattern B, the read-back equals
pattern B, `wrote_ok=True`, so the verdict is `OK` -- and the fixture's own test (which asserts BAD)
fails. Restored byte-identically; `git diff tests/test_chip_test_sdp_leg.py` before this commit
showed only net-new insertions (the Task 3 additions), with the `_dead_write_path_operator`
function body itself confirmed line-for-line identical to its pre-break form.

## Issues Encountered

None beyond the one measured discrepancy documented above (VALIDATION.md's "exactly two" claim).

## User Setup Required

None -- no external service configuration required.

## Threat Flags

None. No new network endpoints, auth paths, or trust-boundary schema changes were introduced --
`_dispatch_sdp_leg` calls only the existing `EpromOperator.write_eprom`/`read_eprom` methods, and
the one new wire surface (`FLAG_SKIP_SDP_UNLOCK` on one op) is already named in this plan's own
`<threat_model>` (T-134-09) and mitigated by the flag-pin tests above.

## Next Phase Readiness

- LEG-05, LEG-07, LEG-08, LEG-16 are fully discharged; nothing later in the phase adds to them.
- LEG-06's engine half is proven; plan 134-05 has its exact starting point: fix the exit-code
  precedence (D-14, `marginal` currently outranks `BAD` via a naive `max`) so a run containing this
  plan's `(True, B) => BAD` result exits 1, then tick LEG-06.
- Plan 134-03 has its exact starting point: teach `derive_plan` to emit the SDP leg's six steps
  (D-06), discharging the 4 remaining `TEMPORARY — discharged by plan 134-03` exemption rows
  (all against `derive_plan`, none against `_dispatch_step` -- this plan already discharged those)
  and flipping the two `("derive_plan", OP_SDP_LOCK/OP_SDP_UNLOCK): False` pins in the SAME commit.
- `_readback_operator` and `_dead_write_path_operator` are available in
  `tests/test_chip_test_sdp_leg.py` for any later plan needing a read-back-capable double.
- No blockers. mypy headroom unchanged at 2 (33/35, `checked` unchanged at 124 -- no new source
  modules added this plan, only additions to two existing test files and one existing production
  module). Full suite: 1361 passed, coverage 81.85% (>= 70% floor).

## Self-Check: PASSED

- `firestarter_app/firestarter/chip_test.py` -- FOUND, contains `def _dispatch_sdp_leg(` and
  `if step.op in _SDP_LEG_OPS:`.
- `firestarter_app/tests/test_op_registration_parity.py` -- FOUND, `grep -c 'TEMPORARY — discharged
  by plan 134-02'` returns 0, `grep -c 'TEMPORARY — discharged by plan 134-03'` returns 4.
- `firestarter_app/tests/test_chip_test_sdp_leg.py` -- FOUND, `def _readback_operator(` and
  `def _dead_write_path_operator(` both present; 49/49 tests in this file pass.
- Commit `7284c7d` (submodule) -- FOUND in `git -C firestarter_app log --oneline --all`.
- Commit `4ac946a` (submodule) -- FOUND in `git -C firestarter_app log --oneline --all`.
- Commit `2699579` (submodule) -- FOUND in `git -C firestarter_app log --oneline --all`.

---
*Phase: 134-the-plan-derived-sdp-oracle-in-dev-test*
*Completed: 2026-08-04*
