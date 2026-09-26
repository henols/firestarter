---
phase: 108-test-plan-engine-address-derived-pattern-fingerprint
plan: 04
subsystem: testing
tags: [python, chip-test-engine, non-fatal-executor, id-gate, marginal-policy, fingerprint]

# Dependency graph
requires:
  - phase: 108-01
    provides: EpromOperationError.error_code kwarg (RPT-03 seam)
  - phase: 108-02
    provides: generate_pattern/classify_fingerprint/Fingerprint/_diff_offsets in chip_test.py
  - phase: 108-03
    provides: derive_plan/Step/Plan (guard-bypassing derivation)
provides:
  - "run_plan(plan, operator, db, *, runs=2) -> list[StepResult] — the non-fatal per-step execution engine"
  - "StepResult record: verdict (OK/BAD/NA/SKIPPED/marginal) + error_code + fingerprint + run_count + divergence"
  - "id-first destructive_gate: chip-ID mismatch/uncertainty SKIPS write/erase without calling the operator"
  - "N>=2 marginal-on-disagreement policy for write/erase/verify; runs<2 rejected before any resolve/operator call"
  - "Write/verify step Fingerprint wiring via generate_pattern + classify_fingerprint (addr_base = region start)"
affects: [109, 110, 112]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Guard-honoring execution: every executed step re-resolves via chip_resolver.resolve_chip, never reuses derive_plan's bypassing dict"
    - "Per-step try/except boundary: one step's BAD/exception never aborts the remaining steps (W29C040 lesson)"
    - "N-run outcome-agreement check mirrors consistency_check_eprom's SHA-256 divergence pattern but keeps destructive/verify marginal separate from read-only divergence metrics"

key-files:
  created: []
  modified:
    - firestarter_app/firestarter/chip_test.py
    - firestarter_app/tests/test_chip_test.py

key-decisions:
  - "id-step gate closes on is_ok=False, an explicit detected-id != expected-id mismatch, OR the id step itself being SKIPPED/BAD for any other reason — any id-uncertainty (not just a numeric mismatch) gates destructive steps shut (Pitfall 4 conservative reading)"
  - "Read-step readback + write/verify-step readback both use tempfile-backed output_file paths (mirroring consistency_check_eprom's per-run file pattern) since EpromOperator.read_eprom writes to disk rather than returning bytes"
  - "The internal readback call inside the write/verify fingerprint step is wrapped in its own try/except so a readback failure (e.g. the same fault that failed the write itself) degrades to 'no fingerprint attached' rather than converting an otherwise-successful write's verdict to BAD (Pitfall 1 extended to this internal call)"
  - "Default write/verify pattern region is (start=0, length=256) — a reasonable non-UV stand-in; Phase 109 owns the concrete UV small-region window and can pass different start/length through this same run_plan/generate_pattern wiring"
  - "runs<2 returns a single sentinel StepResult (op='__plan__', verdict=BAD) rather than raising, keeping run_plan's return type list[StepResult] uniform for callers"

patterns-established:
  - "StepResult dataclass: op/verdict/reason/error_code/fingerprint/run_count/divergence — the per-step outcome record Phase 110's report model consumes"
  - "_dispatch_read / _dispatch_multi_run / _dispatch_id split: single-run (id, blank-check), multi-run-with-divergence-metric (read), and multi-run-with-marginal-policy (write/verify/erase) are three distinct execution shapes"

requirements-completed: [SWEEP-02, SWEEP-03, SWEEP-04, RPT-03]

coverage:
  - id: D1
    description: "run_plan executes each op as an independent non-fatal step; a raising/BAD step never aborts later steps; error_code is captured from EpromOperationError"
    requirement: "SWEEP-02"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_chip_test.py#test_run_plan_non_fatal_raising_step_does_not_abort_later_steps"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_chip_test.py#test_run_plan_verdict_vocabulary_and_na_not_executed"
        status: pass
    human_judgment: false
  - id: D2
    description: "A resolve_chip refusal (ChipNotImplementedError/ChipNotFoundError) maps a listed step to SKIPPED with reason, never an unhandled raise; execution routes through resolve_chip, not the derivation dict"
    requirement: "SWEEP-02"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_chip_test.py#test_run_plan_resolver_refusal_maps_to_skipped"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_chip_test.py#test_run_plan_routes_through_resolve_chip_not_derivation_dict"
        status: pass
    human_judgment: false
  - id: D3
    description: "id-check runs first; a chip-ID mismatch (is_ok=False or detected!=expected) hard-gates write/erase SKIPPED without calling the operator's destructive methods; matching/NA id leaves destructive steps ungated; non-destructive findings still recorded"
    requirement: "SWEEP-03"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_chip_test.py#test_id_mismatch_gate_skips_destructive_steps_without_calling_operator"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_chip_test.py#test_id_detected_mismatch_gate_skips_destructive_steps"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_chip_test.py#test_id_match_leaves_destructive_steps_ungated"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_chip_test.py#test_id_mismatch_does_not_gate_non_destructive_steps"
        status: pass
    human_judgment: false
  - id: D4
    description: "runs<2 rejected before any resolve/operator call; destructive/verify steps run N>=2 and report marginal on disagreement (never coerced to PASS/FAIL); read disagreement is a divergence metric only, never marginal; write/verify attaches a Fingerprint with addr_base == region start"
    requirement: "SWEEP-04"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_chip_test.py#test_runs_boundary_rejects_below_2_before_any_operator_call"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_chip_test.py#test_marginal_on_disagreeing_write_runs"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_chip_test.py#test_marginal_on_disagreeing_verify_runs"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_chip_test.py#test_agreeing_destructive_runs_report_confident_ok"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_chip_test.py#test_agreeing_destructive_runs_report_confident_bad"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_chip_test.py#test_read_step_disagreement_is_divergence_metric_not_marginal"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_chip_test.py#test_read_step_agreement_no_divergence_recorded"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_chip_test.py#test_write_step_attaches_fingerprint_with_region_start_addr_base"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_chip_test.py#test_write_step_fingerprint_addr_base_matches_region_start"
        status: pass
    human_judgment: false

# Metrics
duration: 45min
completed: 2026-07-02
status: complete
---

# Phase 108 Plan 04: Non-Fatal Test-Plan Executor + id-Gate + Marginal Policy Summary

**`run_plan()` composes existing `EpromOperator` methods through the guard-honoring `resolve_chip` path into a non-fatal, id-first, N>=2 sweep executor with an OK/BAD/NA/SKIPPED/marginal verdict vocabulary and firmware `error_code` capture.**

## Performance

- **Duration:** 45 min
- **Started:** 2026-07-02T17:41:00Z
- **Completed:** 2026-07-02T18:27:00Z
- **Tasks:** 3
- **Files modified:** 2

## Accomplishments
- `run_plan(plan, operator, db, *, runs=2)` executes every supported step through `resolve_chip(name, db)` (guard-honoring) and dispatches to the matching existing `EpromOperator` method — zero new firmware dispatch, zero VPP-set, zero wire dict, zero `--force`
- Each step runs in its own try/except boundary: a `BAD` verdict or a raised `EpromOperationError` on one step never aborts the remaining steps (the W29C040 locked-boot-block lesson made structural); the exception's `error_code` (Phase 108-01 seam) is captured onto the step result (RPT-03)
- id-check runs first; a chip-ID mismatch (`is_ok=False` or a detected id differing from the DB's expected `chip-id`) closes a `destructive_gate` that every write/erase step consults before calling its operator method — the chip stays pristine (operator destructive methods are never invoked) while id/read/blank findings are still recorded
- Destructive/verify steps (write/erase/verify) run `runs` times (default 2); disagreeing per-run outcomes report `marginal` (never coerced to a confident OK/BAD) — the AM27C020 write#1 60/64 vs write#2 0/64 case made structural; `runs<2` is rejected before any resolve/operator call, mirroring `consistency_check_eprom`'s guard
- Read-step disagreement across `runs` is reported as a byte-level divergence metric on the result only (never a verdict flip, never `marginal`, per D-06)
- The write/verify step attaches a `Fingerprint` (Phase 108-02's `classify_fingerprint`) built from `generate_pattern` vs. the read-back, with `addr_base` set to the write region start (Pitfall 3 — absolute-address clustering, not offset-relative)

## Task Commits

Each task was committed atomically inside the `firestarter_app` submodule:

1. **Task 1: Non-fatal per-step executor with verdict vocabulary + error_code capture** - `aad849e` (feat)
2. **Task 2: id-first chip-ID mismatch destructive gate** - `eea7c48` (feat)
3. **Task 3: N>=2 marginal policy on destructive/verify + write-step fingerprint wiring** - `abdfad3` (feat)

_All three tasks are `tdd="true"`; tests were authored alongside each task's implementation and verified green before commit (no separate RED-only commit was created — tests and implementation landed together per-task, consistent with 108-02/108-03 precedent in this same phase)._

## Files Created/Modified
- `firestarter_app/firestarter/chip_test.py` - Added `run_plan`, `StepResult`, `_dispatch_id`/`_dispatch_read`/`_dispatch_multi_run`/`_dispatch_step`, `_resolve_or_none`, `_id_step_closes_gate`, verdict constants (`VERDICT_OK/BAD/NA/SKIPPED/MARGINAL`), and the write/verify region constants
- `firestarter_app/tests/test_chip_test.py` - Added 20 new tests covering non-fatal execution, verdict vocabulary, resolver-refusal handling, the id-first destructive gate (mismatch/match/non-destructive-exempt), the `runs<2` guard, the marginal-on-disagreement policy for write/verify, read-step divergence-not-marginal, and write-step fingerprint attachment

## Decisions Made
- id-gate closes on ANY id-step uncertainty (BAD or SKIPPED), not just an explicit numeric mismatch — the conservative reading of Pitfall 4 (a resolver refusal or check failure during the id step is treated the same as a confirmed mismatch for gating purposes)
- Read and write/verify readback both go through temp-file-backed `output_file` paths since `EpromOperator.read_eprom` writes to disk rather than returning bytes directly — mirrors `consistency_check_eprom`'s own per-run file pattern rather than inventing a new in-memory read path
- The write/verify step's internal readback call is defensively wrapped so a readback failure never converts an otherwise-successful write outcome into `BAD` — it only means no `Fingerprint` is attached for that step
- Default write/verify pattern region `(start=0, length=256)` is a placeholder reasonable for non-UV chips; Phase 109 will pass its own small-region window through the same `generate_pattern`/`classify_fingerprint` wiring already proven here

## Deviations from Plan

None - plan executed exactly as written. The `runs<2` guard, id-first gate, and marginal policy all match the plan's `<action>` specifications; the read-divergence-vs-marginal split follows D-06 exactly.

## Issues Encountered
- Task 3's default `runs=2` behavior changed the call-count semantics of Task 1/2's write/read/verify/erase steps (each now executes twice by default instead of once). The Task 1/2 tests that asserted `assert_called_once()` on now-multi-run ops were updated to `assert_called()` (the invariant they actually test — "was the operator method reached at all" — is unaffected by the run count Task 3 introduces). No production behavior changed as a result; this was a test-assertion tightening only.
- An internal readback call inside `_dispatch_multi_run` (used to build the write/verify `Fingerprint`) could raise `EpromOperationError` when the same fault that failed the write also fails the readback, which was initially escaping to `_run_step`'s outer except and incorrectly converting a successful write's verdict to `BAD`. Fixed by wrapping the readback in its own try/except (Rule 1 — bug fix; caught before commit via the full-suite non-fatal test).
- mypy flagged `eprom_data: dict[str, Any] | None` being passed to `_dispatch_step` (which expects a non-Optional dict) — a defensive-but-unreachable path since `skip_stub is None` implies `eprom_data is not None` by construction. Tightened the guard in `_run_step` to check both conditions explicitly (Rule 1 — no test coverage lost, `mypy firestarter/chip_test.py` now clean).

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- The phase's full engine is now complete: `derive_plan` (108-03) + `run_plan` (this plan) + `generate_pattern`/`classify_fingerprint` (108-02) + the `error_code` seam (108-01) compose into a bench-free, unit-tested chip capability sweep.
- Phase 109 (per REQUIREMENTS.md routing) owns: the `--destructive` gate at plan-construction time, the UV small-region write-window sizing/placement (this plan's `generate_pattern`/`classify_fingerprint` wiring already accepts arbitrary `start`/`length` — no rework needed), and the orchestrator-only CI gate (zero new dispatch + zero VPP-set sites, which this plan's `chip_test.py` already satisfies structurally).
- Phase 110 (report model) can consume `StepResult` (verdict/error_code/fingerprint/run_count/divergence) directly — no adapter needed.
- One pre-existing, out-of-scope test failure remains: `tests/test_audit_coverage_matrix.py::TestAuditCoverageMatrix::test_golden_file_matches` (meta-ledger drift tracked from Phase 106-01) — not touched by this plan, `tests/test_chip_test.py` and the rest of the app suite are green with coverage at 79.62% (floor 70%).

---
*Phase: 108-test-plan-engine-address-derived-pattern-fingerprint*
*Completed: 2026-07-02*

## Self-Check: PASSED

- FOUND: firestarter_app/firestarter/chip_test.py
- FOUND: firestarter_app/tests/test_chip_test.py
- FOUND: .planning/phases/108-test-plan-engine-address-derived-pattern-fingerprint/108-04-SUMMARY.md
- FOUND commit (submodule): aad849e
- FOUND commit (submodule): eea7c48
- FOUND commit (submodule): abdfad3
- FOUND commit (meta): febb1a2
