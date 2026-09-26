---
phase: 133-sdp-leg-mechanism
verified: 2026-08-04T00:00:00Z
status: passed
score: 5/5 must-haves verified
behavior_unverified: 0
overrides_applied: 0
---

# Phase 133: SDP Leg Mechanism Verification Report

**Phase Goal:** `dev test`'s step-execution engine can never strand a locked chip or lose a report to a
transport error, and adding a new op to its vocabulary is machine-verified to touch every registry it
must — all of it provably inert for the ops that already ship today.

**Verified:** 2026-08-04
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths (ROADMAP's five success criteria)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | A mid-leg step that raises still leaves `run_plan`'s cleanup registry to drain in a `finally`, including on `KeyboardInterrupt`/`SystemExit` | ✓ VERIFIED | `run_plan` (`chip_test.py:875-971`) wraps the whole step loop in a bare `try/finally` with **zero** `except` clauses. Confirmed live: `test_finally_drains_on_exception`, `test_keyboard_interrupt_drains_and_propagates`, `test_system_exit_drains_and_propagates` all pass (independently re-run). Honest caveat present and accurate: on the propagating path, `cli_handlers.py:2161`'s `results = run_plan(...)` never completes, so the report is forfeited — this is stated plainly in RECORD §3 Criterion 1, not smoothed over. |
| 2 | A `SerialError`/`HardwareOperationError` mid-step degrades that one step to BAD rather than killing the whole report; no bare/broad except used | ✓ VERIFIED | `_run_step` (`chip_test.py:1040-1115`) has four ordered `except` clauses: `(ProgrammerNotFoundError, FirmwareOutdatedError)` re-raised first, then `(SerialError, HardwareOperationError)` degrade to BAD, then `EpromOperationError`, then `(ChipNotImplementedError, ChipNotFoundError)`. Independently re-ran `test_serial_timeout_degrades_one_step`, `test_hardware_error_degrades_one_step`, `test_run_fatal_escapes`, `test_assertion_error_propagates` — all pass. Independently re-ran the build-time gate (`tools/check_devtest_orchestrator.py`), confirmed real `except Exception:`/`BaseException`/tuple/bare forms are all rejected via 4 subprocess-level planted-fault tests. |
| 3 | `sdp_unlock` absent from `_DESTRUCTIVE_OPS`; two behavioral cases (gate-closed-from-start skips both; lock-ran-then-gate-closes still unlocks) | ✓ VERIFIED | `_DESTRUCTIVE_OPS = frozenset({OP_WRITE, OP_WRITE_PARTIAL, OP_ERASE, OP_SDP_LOCK})` (`chip_test.py:663`) — `OP_SDP_UNLOCK` genuinely absent. Independently re-ran `test_gate_closed_from_start` and `test_lock_ran_then_gate_closes`, both pass. Qualifier (D-11) honestly recorded: this is forward-protection for Phase 134 since 133 derives no SDP step of its own. |
| 4 | Every shipped op is behaviorally byte-identical after this phase; `group=None` takes the pre-existing path at zero added cost | ✓ VERIFIED (intent met by a different, honestly-recorded mechanism) | Confirmed **no `Step.group` field exists anywhere** in `chip_test.py` (grep across the file; the `Step` dataclass at `:314-339` has `op/supported/reason/destructive/write_region` only). The record states plainly this criterion's literal `group=None` clause is satisfied VACUOUSLY and does not restate it as tested — this is the correct, honest disposition, not a quiet pass-as-written. The *intent* (zero added branching cost) is independently proven: I performed my own mutation test, moving the `_SDP_OPS` dispatch arm to the FRONT of `_dispatch_step` — `test_shipped_ops_never_reach_sdp_arm` failed immediately with the exact sentinel message ("a shipped op reached `_dispatch_sdp`... arm 5 placed wrongly"), then reverted cleanly (verified `git diff` empty afterward, full targeted suite green again: 33/33 passed). This proves the sentinel is genuinely sensitive to arm position, not merely to op-string disjointness. |
| 5 | An op-registration parity test fails if a new op is left out of any required registry — "eight" fail-open registries → one fail-closed gate | ✓ VERIFIED (count corrected, mechanism real) | `tests/test_op_registration_parity.py` (822 lines) implements `_POLICED_REGISTRIES` (6: `_DESTRUCTIVE_OPS`, `_MULTI_RUN_OPS`, `_SDP_OPS`, `_dispatch_step`, `derive_plan`, `_dispatch_multi_run` — the last one AST-derived and a genuine addition P-23's original table missed) and `_DECLARED_NON_REGISTRIES` (6, each re-measured every run by an inversion guard, including the correctly-identified `tools/parse_devtest_issue.py` zero-op-vocabulary case). All 6 tests pass. The RECORD's correction of ROADMAP's "eight" to "6 policed + 6 declared non-registries" is stated plainly as a measured correction, not smoothed into a false "eight" restatement. |

**Score:** 5/5 truths verified (0 present-but-behavior-unverified)

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `firestarter_app/firestarter/chip_test.py` | `OP_SDP_LOCK`/`OP_SDP_UNLOCK`, `_SDP_OPS`, `_dispatch_sdp`, cleanup registry, widened `_run_step` | ✓ VERIFIED | All present, wired, and exercised (1544 lines total; all constructs found at their claimed locations). |
| `firestarter_app/tests/test_chip_test_sdp_leg.py` | LEG-09/10/11 + D-13 behavioral proofs, precedence-matrix triple | ✓ VERIFIED | 1257 lines, 25 tests, all pass. Precedence-matrix triple (`_PRE_EDIT_PRECEDENCE_MATRIX`/`_EXPECTED_PRECEDENCE_MATRIX`/`_INTENDED_PRECEDENCE_DELTA`) confirmed present and functioning; git history confirms `_PRE_EDIT_PRECEDENCE_MATRIX`'s dict body untouched since commit `7f62cf5` (only comments changed in later diffs). |
| `firestarter_app/tests/test_op_registration_parity.py` | LEG-15 parity gate | ✓ VERIFIED | 822 lines, 8 tests, all pass. Registry census (6 policed + 6 non-registry) matches the RECORD's claim exactly. |
| `firestarter_app/tools/check_devtest_orchestrator.py` | broad-except deny bucket + D-14 exemption table | ✓ VERIFIED | `visit_ExceptHandler` (:438) implements the deny bucket; `_BROAD_EXCEPT_EXEMPTIONS` (:244) carries exactly one row (`_sample`), guarded two ways. Ran the checker directly: exit 0, clean. |

### Key Link Verification

| From | To | Via | Status | Details |
|------|-----|-----|--------|---------|
| `run_plan`'s `finally` | cleanup registry | drains `cleanup: list[Callable[[], None]]` in registration order | ✓ WIRED | Confirmed no reference to `results` anywhere in the `finally`'s AST (`test_drain_does_not_mutate_results`, AST-level, non-vacuous by construction — it walks real parsed source). |
| `_dispatch_step` | `_dispatch_sdp` | arm 5, last, above terminal fail-closed `return` | ✓ WIRED, mutation-proved | Independently confirmed via my own arm-reorder mutation (see Criterion 4 row above) that this ordering is load-bearing, not incidental. |
| `_run_step` | `_run_step`'s exception clauses | four ordered `except` clauses | ✓ WIRED | Order confirmed correct (narrow-before-broad, `SerialError` subclasses re-raised before the sibling-class catch). |
| `tests/test_op_registration_parity.py` | `chip_test.py`'s real frozensets/functions | direct import + AST introspection of live source (`_op_names_referenced_in`) | ✓ WIRED | Registries are read from the imported module's real values, not hardcoded copies that could drift. |

### Behavioral Spot-Checks (independent, run by this verifier)

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Targeted test file suite green | `pytest tests/test_chip_test_sdp_leg.py tests/test_op_registration_parity.py -o addopts="-ra" -q` | 33 passed | ✓ PASS |
| Sentinel non-vacuity (arm-order mutation) | moved `_SDP_OPS` arm to front of `_dispatch_step`, re-ran `test_shipped_ops_never_reach_sdp_arm` | FAILED with expected sentinel message; reverted, `git diff` clean, suite green again | ✓ PASS |
| Broad-except gate (independent run) | `python3 tools/check_devtest_orchestrator.py` | `PASS: ... 0 broad-except; firmware untouched` exit 0 | ✓ PASS |
| No new skips | `pytest tests/test_skip_census.py -o addopts="-ra" -q` | 5 passed | ✓ PASS |
| mypy delta attribution (`chip_test.py:442` narrative) | `git blame -L 438,443 tools/check_devtest_orchestrator.py` | confirms commit `feb90f6` (133-05) introduced the line the RECORD attributes the mypy +1 to | ✓ PASS |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|---|---|---|---|---|
| LEG-09 | 133-03, 133-04 | `sdp_unlock` exempt from destructive-op set | ✓ SATISFIED | `_DESTRUCTIVE_OPS` asymmetry confirmed; `test_unlock_exempt_from_destructive`, `test_gate_closed_from_start`, `test_lock_ran_then_gate_closes` all pass. Evidence commits `ded8e3e`/`35d4571`/`23f895c`/`5c8fb09` all exist in submodule history. |
| LEG-10 | 133-04 | `run_plan` drains cleanup registry in `finally` | ✓ SATISFIED | Confirmed bare `try/finally`, no `except`; drain never touches `results` (independently confirmed via reading the AST-check code). Commit `35d4571` exists. |
| LEG-11 | 133-02, 133-05 | `_run_step` catches `SerialError`/`HardwareOperationError` | ✓ SATISFIED | Confirmed four-clause chain, correct ordering, independent build-time gate. Commits `9d7c0cc`/`feb90f6` exist. |
| LEG-15 | 133-06 | op-registration parity test | ✓ SATISFIED | Confirmed 6 policed + 6 non-registry census, all guards present and functioning. Commit `57e8eb5` exists. |

No orphaned requirements: REQUIREMENTS.md's traceability table maps exactly these four rows to Phase 133; `git show bd589464` confirms the tick-commit touched only these four entries plus the traceability-table status column (checked via `git show` diff).

### Anti-Patterns Found

None. Searched `chip_test.py`, `tests/test_chip_test_sdp_leg.py`, `tests/test_op_registration_parity.py`, `tools/check_devtest_orchestrator.py`, `tests/test_check_devtest_orchestrator.py` for `TBD|FIXME|XXX` — zero matches. No placeholder/stub patterns found; all dispatch arms and exception clauses have real, non-trivial bodies.

### Scrutiny Items (from dispatch instructions) — all resolved clean

1. **Criterion 4's `group=None` vacuity** — confirmed genuinely vacuous (no `Step.group` field exists), and confirmed the record does NOT restate the literal criterion words as tested; it explicitly says the intent was met by a different mechanism (arm position + sentinel). This is the correct honest disposition, not a soft-pedaled pass.
2. **Criterion 5's registry census** — spot-checked against actual code: `_POLICED_REGISTRIES` (6) and `_DECLARED_NON_REGISTRIES` (6) match the RECORD's breakdown exactly, including the correctly-verified `tools/parse_devtest_issue.py` zero-op-vocabulary claim (confirmed no `OP_*` references in that file) and the correctly-added `_dispatch_multi_run` inner-branch registry P-23 missed.
3. **Precedence-matrix triple** — confirmed real: git history shows `_PRE_EDIT_PRECEDENCE_MATRIX`'s dict body has been untouched since commit `7f62cf5` (only comments/context changed in subsequent diffs); `_INTENDED_PRECEDENCE_DELTA` names exactly `SerialError`/`SerialTimeoutError`/`HardwareOperationError`; the delta gate's non-vacuity test (`test_precedence_matrix_deriver_is_non_vacuous`) genuinely alters a row and asserts the gate catches it — confirmed by reading the assertion logic.
4. **`results` prohibition** — confirmed real and AST-enforced (`test_drain_does_not_mutate_results`), and confirmed non-vacuous via the phase's own documented mutation proof (133-04-SUMMARY.md: planting `results.append(...)` made both this test and `test_empty_registry_noop` fail with named messages, then reverted) — consistent with what the AST logic in the test file actually does.
5. **Pre-authored gate legs proving vacuous twice** — independently reproduced one of the two (the arm-position sentinel, criterion 4) myself via a live mutation and confirmed the test fails as expected when the arm is misplaced, and passes when correctly placed. The second (the `lambda` type-mismatch, D-06/mypy) is corroborated by `133-04-SUMMARY.md`'s "Decisions Made"/"Deviations from Plan" section and the mypy count evidence in `133-CI-PARITY.md`/`deferred-items.md`, which is internally consistent (mypy 32→33 attribution to `check_devtest_orchestrator.py:442`, confirmed via `git blame` to commit `feb90f6`).
6. **Evidence Ceiling** — confirmed stated plainly in `133-RECORD.md` §6, `133-CONTEXT.md`, `133-07-PLAN.md`, `133-04-SUMMARY.md`, and `133-VALIDATION.md`, all consistently: "proves the mechanism... proves NOTHING about SDP behaviour on silicon." No artifact scanned makes a claim that exceeds this ceiling — searched all phase `.md` files for silicon/hardware-validation language and found only correctly-scoped denials, never an overclaim.

### Human Verification Required

None. This phase is host-only, produces no user-visible surface (explicitly out of scope — no report rendering, no `derive_plan` SDP emission), and every mechanism claim was independently verifiable via source reading, git history, and live mutation testing rather than requiring visual/UX/hardware judgment. The Evidence Ceiling correctly scopes what this phase does NOT and cannot prove (SDP behavior on real silicon) — that is expected non-coverage for this phase, not a gap.

### Gaps Summary

No gaps. All five ROADMAP success criteria are genuinely discharged, with the two criteria most likely to be quietly mis-satisfied (4 and 5, per the dispatch's own flag) independently confirmed to be honestly and non-vacuously handled rather than rubber-stamped. Independent mutation testing (arm-reorder for criterion 4's sentinel) reproduced the phase's own claimed RED-then-revert result, confirming the test suite's fail-closed properties are real rather than merely narrated. Requirement traceability (LEG-09/10/11/15), commit existence, and REQUIREMENTS.md tick-scope are all confirmed exact matches to the RECORD's claims. mypy (33/124 vs watermark 35), full suite (1338 passed), ruff, and the devtest orchestrator gate are all independently reproduced clean.

---

*Verified: 2026-08-04*
*Verifier: Claude (gsd-verifier)*
