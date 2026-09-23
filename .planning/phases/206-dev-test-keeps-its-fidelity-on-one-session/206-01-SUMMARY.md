---
phase: 206-dev-test-keeps-its-fidelity-on-one-session
plan: 01
subsystem: testing
tags: [dev-test, chip_test, verdict-vocabulary, exit-code, status-axis]

requires:
  - phase: 202-verification-engine-moves-to-the-host
    provides: "check_eprom_blank and verify_eprom's int (0/1/2) return contract, and the two one-line == 0 adapters this plan finishes migrating"
  - phase: 204-firmware-ordinal-retirement
    provides: "ordinals 4 and 6 retired; the two adapters no longer compose them"
provides:
  - "A transport-failed cycle-block step exits 2, not 0, end to end"
  - "check_eprom_blank and verify_eprom verdicts 0/1/2 land on three distinguishable step outcomes, each carrying both a verdict and a status"
affects: [206-02-dedup-fingerprint-schema, 206-03-lease-gate, 206-04-lease-measurement]

actuals:
  tokens: 5258
  tasks: 2
  commits: 2
plan_head_before: 2756ef0

tech-stack:
  added: []
  patterns:
    - "Run-validity status folded any-error-wins over the FULL per-cycle results list, never the ran subset (a SKIPPED cycle is excluded from _RAN_VERDICTS)"
    - "A compare method's int refusal (2) is classified BEFORE any narrower case-specific branch (uv_prewrite, diverged) so a rig fault can never be absorbed into a chip-finding branch"

key-files:
  created: []
  modified:
    - firestarter_app/firestarter/chip_test.py
    - firestarter_app/tests/test_chip_test_cycle.py
    - firestarter_app/tests/test_dev_test_cmd.py
    - firestarter_app/tests/test_chip_test.py

key-decisions:
  - "D-01: verdict 2 lands on VERDICT_SKIPPED + STATUS_ERROR at both the blank-check and verify dispatch arms, never a sixth verdict and never VERDICT_BAD -- the same two-axis vocabulary _run_step_untimed's transport arm already uses."
  - "D-04: the verify fingerprint's source is unchanged (_read_region on failure, _synthesized_match_fingerprint on a clean pass) -- sourcing it from the verify's own CompareResult was rejected for this phase because it requires full=True, forfeiting the abort-path saving DEVTEST-01 does not ask about."
  - "D-09: the FP_TRANSPORT classification bucket stays dead -- _run_cycle_block still calls _run_step with runs=1, so repeat_divergent is permanently False."

patterns-established:
  - "folded_status_error / folded_status naming convention in _aggregate_cycle_results, matching the existing verdict/reason locals above the terminal constructor"

requirements-completed: [DEVTEST-01, DEVTEST-03]

coverage:
  - id: D1
    description: "A dev test run whose cycle-block step transport-fails on one of the default three cycles exits 2, not 0; --fast (one cycle) and the default three-cycle run agree on the folded status"
    requirement: "DEVTEST-03"
    verification:
      - kind: unit
        ref: "tests/test_chip_test_cycle.py#test_a_transport_failed_cycle_keeps_the_run_status_error"
        status: pass
      - kind: unit
        ref: "tests/test_chip_test_cycle.py#test_fast_and_default_runs_agree_on_a_transport_failed_step_status"
        status: pass
      - kind: unit
        ref: "tests/test_dev_test_cmd.py#test_a_transport_failed_cycle_block_step_exits_2_not_0"
        status: pass
    human_judgment: false
  - id: D2
    description: "check_eprom_blank and verify_eprom verdicts 0/1/2 land on three distinguishable step outcomes, each asserted on both the verdict and status axis; no information lost; both in-source phase markers removed; 19 frozen dedup_fingerprint literals unmoved"
    requirement: "DEVTEST-01"
    verification:
      - kind: unit
        ref: "tests/test_chip_test.py#test_blank_check_verdict_2_is_skipped_with_status_error"
        status: pass
      - kind: unit
        ref: "tests/test_chip_test.py#test_blank_check_verdict_1_stays_bad"
        status: pass
      - kind: unit
        ref: "tests/test_chip_test.py#test_blank_check_verdict_1_on_a_uv_prewrite_stays_skipped_complete"
        status: pass
      - kind: unit
        ref: "tests/test_chip_test.py#test_verify_verdict_2_is_skipped_with_status_error"
        status: pass
      - kind: unit
        ref: "tests/test_chip_test.py#test_verify_verdict_1_stays_bad"
        status: pass
      - kind: unit
        ref: "tests/test_chip_test.py#test_verify_verdict_2_performs_no_fingerprint_read_back"
        status: pass
      - kind: unit
        ref: "tests/test_blast_radius_invariance.py#test_dedup_fingerprint_is_frozen"
        status: pass
    human_judgment: false

duration: 62min
completed: 2026-09-23
status: complete
---

# Phase 206 Plan 01: Verdict 2 gets an honest landing Summary

**A transport-failed cycle-block step now exits 2 end to end, and `check_eprom_blank`/`verify_eprom`'s verdict 2 lands on `VERDICT_SKIPPED` + `STATUS_ERROR` at both dispatch arms instead of being folded into a chip verdict.**

## Performance

- **Duration:** 62 min
- **Started:** 2026-09-23T00:00:00Z (approximate — session start)
- **Completed:** 2026-09-23T01:02:00Z (approximate)
- **Tasks:** 2
- **Files modified:** 4

## Accomplishments
- Fixed `_aggregate_cycle_results` to fold `STATUS_ERROR` over the full per-cycle `results` list (never the `ran` subset), so a transport fault inside a cycle-block step (write/verify/erase/blank-check) now surfaces at the run level and exits `dev test` with code 2 instead of 0.
- Proved `--fast` (one cycle) and the default three-cycle run agree on a transport-failed step's status.
- Migrated both compare-driven dispatch arms (`_dispatch_step`'s `OP_BLANK_CHECK` arm and `_dispatch_multi_run`'s `OP_VERIFY` branch) off their `== 0` two-way adapters onto the full three-way (0/1/2) verdict, landing verdict 2 on `VERDICT_SKIPPED` + `STATUS_ERROR` and removing both in-source markers that named this phase as the migration's owner.
- Preserved the verify fingerprint's information floor: a verdict-1 verify still attaches a real read-back `Fingerprint`; a clean run still attaches the synthesized one; a verdict-2 verify attaches `None` and performs zero device reads.

## Task Commits

Each task was committed atomically:

1. **Task 1: a transport-failed cycle-block step exits 2, end to end** - `5a772eb` (feat, tracer)
2. **Task 2: the two adapters learn the third verdict** - `c22287a` (feat)

**Plan metadata:** (this commit)

_Both tasks carried `tdd="true"`; each RED transcript is recorded below before the corresponding GREEN commit._

## Files Created/Modified
- `firestarter_app/firestarter/chip_test.py` - `_aggregate_cycle_results` now folds `status` over `results`; `_dispatch_step`'s `OP_BLANK_CHECK` arm and `_dispatch_multi_run`'s `OP_VERIFY` branch both branch on the full 0/1/2 verdict
- `firestarter_app/tests/test_chip_test_cycle.py` - two new direct-fold regression tests for the cycle-block status fold
- `firestarter_app/tests/test_dev_test_cmd.py` - one new end-to-end CLI exit-code regression test
- `firestarter_app/tests/test_chip_test.py` - six new regression tests pinning the blank-check and verify dispatch arms' verdict/status pairs

## Decisions Made
- D-01, D-04, D-09 as recorded in the PLAN's Decisions section — no new decisions introduced during execution.
- Implementation choice: `folded_status` in `_aggregate_cycle_results` is computed as `folded_status_error = any(r.status == STATUS_ERROR for r in results)` followed by `folded_status = STATUS_ERROR if folded_status_error else STATUS_COMPLETE`, split across two short lines rather than one long ternary, so the line `ruff format` keeps intact still carries the `STATUS_ERROR`/`in results` substrings the plan's own source-assertion `<verify>` leg keys on. A single-line ternary long enough to include both substrings exceeded the project's 88-column `ruff format` width and would have been silently rewrapped, breaking that assertion's first-line scan.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Moved the Task 1 end-to-end test to module level, not a class method**
- **Found during:** Task 1, authoring the RED legs
- **Issue:** The plan's own `<verify>` command invokes `tests/test_dev_test_cmd.py::test_a_transport_failed_cycle_block_step_exits_2_not_0` as a bare (non-class-qualified) node id. Authoring the test as a method on `TestExitCodeMapping` (the class holding the most directly analogous existing tests) produces the node id `TestExitCodeMapping::test_a_transport_failed_cycle_block_step_exits_2_not_0`, which does not match and collects 0 items under the plan's literal invocation ("not found... no match in any of").
- **Fix:** Wrote the test as a plain module-level function (using the module's `runner` fixture, which is itself module-level and available regardless of class nesting), placed directly after `TestExitCodeMapping`'s closing line so it stays adjacent to its analogous tests in reading order.
- **Files modified:** `firestarter_app/tests/test_dev_test_cmd.py`
- **Verification:** `pytest tests/test_dev_test_cmd.py::test_a_transport_failed_cycle_block_step_exits_2_not_0 -v` collects and passes.
- **Committed in:** `5a772eb` (Task 1 commit)

---

**Total deviations:** 1 auto-fixed (1 blocking).
**Impact on plan:** Cosmetic authoring correction only — no behavior change, no scope creep. The plan's own verify command now runs exactly as written.

## Issues Encountered
None.

## Baseline (recorded before the first edit)

Full host suite, run through `/workspaces/firestarter_app/.venv311/bin/python`, `-o addopts="" -p no:cacheprovider -q`:

```
2333 passed in 180.48s (0:03:00)
```

Failing-node-id set: **empty** (no board was attached to this machine for this session; `test_no_programmer_found_*` and similar hardware-gated legs were not part of the observed failing set — the RESEARCH-cited expectation of `test_no_programmer_found_*` failing did not apply here). Every later suite-wide claim in this phase diffs against this empty set, not against "all green" as an assumption.

Per-module baselines also recorded before any edit:
- `tests/test_chip_test_cycle.py` + `tests/test_dev_test_cmd.py`: 103 passed
- `tests/test_chip_test.py`: 162 passed
- `tests/test_blast_radius_invariance.py`: 67 passed
- `tests/test_compare.py` + `tests/test_devtest_firmware_error_propagation.py` + `tests/test_chip_test_blank_check_order.py`: 84 passed

## Task 1 RED transcript

Before any implementation edit, `test_a_transport_failed_cycle_keeps_the_run_status_error`, `test_fast_and_default_runs_agree_on_a_transport_failed_step_status`, and `test_a_transport_failed_cycle_block_step_exits_2_not_0` were run against the unmodified source:

```
FAILED tests/test_chip_test_cycle.py::test_a_transport_failed_cycle_keeps_the_run_status_error
  AssertionError: assert 'COMPLETE' == 'ERROR'
FAILED tests/test_chip_test_cycle.py::test_fast_and_default_runs_agree_on_a_transport_failed_step_status
  AssertionError: assert 'COMPLETE' == 'ERROR'
FAILED tests/test_dev_test_cmd.py::test_a_transport_failed_cycle_block_step_exits_2_not_0
  assert 0 == 2
   +  where 0 = <Result okay>.exit_code
3 failed in 1.33s
```

All three failed on the intended assertion (a status/exit-code mismatch) — none failed on a collection, fixture, or import error. After the fix, all three pass; the full suite (2336 passed) is a superset of the empty baseline failing set.

## Task 2 RED transcript

Before the Task 2 implementation edit, the six new legs in `tests/test_chip_test.py` were run against the Task-1-fixed-but-not-yet-Task-2 source:

```
FAILED tests/test_chip_test.py::test_blank_check_verdict_2_is_skipped_with_status_error
  AssertionError: assert 'BAD' == 'SKIPPED'
FAILED tests/test_chip_test.py::test_verify_verdict_2_is_skipped_with_status_error
  AssertionError: assert 'BAD' == 'SKIPPED'
FAILED tests/test_chip_test.py::test_verify_verdict_2_performs_no_fingerprint_read_back
  AssertionError: assert 1 == 0
   +  where 1 = <Mock name='mock.read_eprom' ...>.call_count
3 failed, 6 passed in 0.30s
```

The other three legs (`test_blank_check_verdict_1_stays_bad`, `test_blank_check_verdict_1_on_a_uv_prewrite_stays_skipped_complete`, `test_verify_verdict_1_stays_bad`) passed immediately against the unmodified dispatch arms — this is expected and not a defect in the RED proof: the plan's own `<behavior>` list marks those three outcomes "Unchanged", i.e. they pin already-correct pre-existing behavior on both axes rather than exercising a bug. The three that DID fail failed for the intended reason (a verdict or read-back-count mismatch), never a collection error. After the fix, all nine (six new plus three pre-existing legs matched by the same `-k` filter) pass, and the full suite (2342 passed) is a superset of the empty baseline failing set.

## SRAM/FRAM pre-wire short-circuit finding (Task 2 acceptance criterion)

`check_eprom_blank`'s pre-wire SRAM/FRAM short-circuit (`eprom_operations.py:3045-3053`) returns 2 for a reason that is **not** a transport fault — the part has no factory-blank state at all. Evidence that a `dev test` plan cannot reach it through the arm this task rewrote: `derive_plan` (`chip_test.py:586-591`) marks the `OP_BLANK_CHECK` step `supported=False` for any chip whose `electrical-type` is `SRAM`/`FRAM` (or whose `protocol-id` is in `_SRAM_PROTO_IDS`), with the reason text `"blank-check not applicable to {etype} (volatile/byte-rewritable, no factory-blank state)"`. `run_plan`'s per-step loop (`chip_test.py:1734-1736`) skips any `not step.supported` step entirely, recording it as `_skip_result(..., verdict=VERDICT_NA)` **without ever calling `_dispatch_step`** — so `operator.check_eprom_blank` is never invoked for these chips via `dev test`, and this task's new verdict-2 branch is unreachable from that path. `check_eprom_blank`'s own docstring already states this design intent ("`derive_plan` (chip_test.py) marks these parts' blank-check step unsupported up front and never dispatches to this method for them, so `dev test` is unaffected by this change") — this task's finding confirms that claim by tracing the actual `supported=False` gate rather than assuming the docstring. No wording in the new verdict-2 branch claims a transport failure for this population, because the population never reaches that branch.

## DEVTEST-03 statement

The classification that changes meaning: a `check_eprom_blank` or `verify_eprom` compare returning **2** — the compare itself did not complete, a setup/transport/hardware refusal — used to be folded into the same branch as verdict 1 (a genuine chip finding: not blank, or a byte mismatch), reporting `VERDICT_BAD` with `STATUS_COMPLETE` (implicitly, via the dataclass default, since neither dispatch arm passed `status=` before this plan). It now reports `VERDICT_SKIPPED` with `STATUS_ERROR` at both the blank-check and verify dispatch sites. The physical outcome this describes is a rig fault — a half-seated cable, a firmware refusal, or any condition that stops the compare engine from completing its comparison — never a finding about the chip under test. The justification: `VERDICT_BAD` misreports a cable problem as a "chip is not blank" or "chip failed verify" finding, which is exactly the false-green/false-attribution hazard T-206-06 and T-206-07 name; the two-axis `SKIPPED`+`ERROR` vocabulary already exists (`_run_step_untimed`'s `SerialError`/`HardwareOperationError` arm has used it since before this phase) and needed no new verdict, which the ROADMAP's own constraint against a sixth verdict forbids anyway. The report population that stops grouping with its pre-206 self as a consequence: any run where a blank-check or verify step's compare returned 2 — its `dedup_fingerprint` per-step triple moves from a `blank-check=BAD:...` (or `verify=BAD:...`) key to a `blank-check=SKIPPED:...` (or `verify=SKIPPED:...`) key. That population is, by construction, rig faults only — never a chip finding — so the re-keying separates community-filed cable/hardware noise from genuine chip-behavior reports, which is DEVTEST-02's stated goal, not a regression.

## Threat Flags

None beyond what the PLAN's `<threat_model>` already declared and this plan's tasks mitigated (T-206-06, T-206-07, T-206-08) — no new report field, no new free-text source, and `submit.sanitize_dict` is untouched.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Plan 02 (dedup_fingerprint schema) can proceed: this plan's verdict/status pairs are the ones plan 02 will key its schema fields on, and the frozen 19-case corpus is proven unmoved by this plan's own commits.
- No blockers. Both dispatch arms tested end-to-end, the full host suite is a superset of the recorded empty baseline, and `tests/test_compare.py` (Phase 202's D-03 behavioural corpus) re-ran green.

## Self-Check: PASSED

- `firestarter_app/firestarter/chip_test.py` — FOUND (modified, both commits present)
- `firestarter_app/tests/test_chip_test_cycle.py` — FOUND
- `firestarter_app/tests/test_dev_test_cmd.py` — FOUND
- `firestarter_app/tests/test_chip_test.py` — FOUND
- Commit `5a772eb` — FOUND in `git log --oneline --all`
- Commit `c22287a` — FOUND in `git log --oneline --all`

---
*Phase: 206-dev-test-keeps-its-fidelity-on-one-session*
*Completed: 2026-09-23*
