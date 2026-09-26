---
phase: 175-structural-sentinel-over-derive-plan
reviewed: 2026-09-04T14:14:40Z
depth: standard
files_reviewed: 8
files_reviewed_list:
  - firestarter_app/tests/plan_corpus.py
  - firestarter_app/tests/test_derive_plan_structural_sentinel.py
  - firestarter_app/tests/test_derive_plan_no_drop_sweep.py
  - firestarter_app/tests/test_plan_shapes_drift.py
  - firestarter_app/tools/measure_plan_shapes.py
  - firestarter_app/tests/fixtures/plan_shapes.json
  - firestarter_app/tests/test_skip_census.py
  - firestarter_app/tests/test_devtest_issue_corpus.py
findings:
  critical: 0
  warning: 3
  info: 0
  total: 3
status: issues_found
---

# Phase 175: Code Review Report

**Reviewed:** 2026-09-04T14:14:40Z
**Depth:** standard
**Files Reviewed:** 8
**Status:** issues_found

## Summary

This is a test-only phase: `tests/plan_corpus.py` (the shared corpus), two structural
sentinels swept over all 1,354 shipped plans (`test_derive_plan_structural_sentinel.py`,
`test_derive_plan_no_drop_sweep.py`), the frozen plan-shape pin
(`tools/measure_plan_shapes.py` + `tests/fixtures/plan_shapes.json` +
`test_plan_shapes_drift.py`), and two pre-existing modules touched only cosmetically
(`test_skip_census.py`'s timeout bump, `test_devtest_issue_corpus.py`'s formatting).

I read every file in full, ran the four new/rewritten test modules locally (all green:
31/31, 6/6, 6/6, 35/35), ran `tools/measure_plan_shapes.py --check` against the live
database (byte-identical, confirming the committed artifact is not stale), and audited
the mutation/aliasing discipline across the module-cached `plan_corpus()` — every
mutated-corpus leg in `test_derive_plan_structural_sentinel.py` and
`test_derive_plan_no_drop_sweep.py` goes through `dataclasses.replace` (new `Plan`/`Step`/
`StepResult` objects) rather than an in-place edit, so the Phase 174 CR-01/WR-01
aliasing-bug shape does not recur here. `ruff check` is clean on all seven Python files.

No BLOCKER-tier defect was found — nothing here would let a broken `derive_plan` ship
green. Three WARNING-tier robustness/quality gaps were found: one file fails the
project's own `ruff format --check` gate, three subprocess calls in the drift test have
no `timeout=` (inconsistent with this same phase's own `test_skip_census.py`
discipline), and the plan-shape generator's family-token derivation can crash with an
unhandled `StopIteration` outside its own documented exit-code contract if a plan's
shape assumptions are ever violated.

## Warnings

### WR-01: `tools/measure_plan_shapes.py` is not `ruff format --check` clean

**File:** `firestarter_app/tools/measure_plan_shapes.py:150-152,219-221`
**Issue:** `firestarter_app/CLAUDE.md` documents that `ruff format --check` is enforced
by `.github/workflows/ci.yml` on every PR. Running it locally against this file fails:

```
$ python3 -m ruff format --check tools/measure_plan_shapes.py
unformatted: File would be reformatted
   --> tools/measure_plan_shapes.py:150:29
    |
149 |                 "full": [_step_token(s.op, s.supported) for s in full_plan.steps],
    -                 "partial": [
    -                     _step_token(s.op, s.supported) for s in partial_plan.steps
    -                 ],
150 +                 "partial": [_step_token(s.op, s.supported) for s in partial_plan.steps],
151 |             }
...
219 |         raise ValidationError(
    -             f"aggregate plans {aggregate['plans']} != 2 * len(chips) "
    -             f"{len(chips) * 2}"
220 +             f"aggregate plans {aggregate['plans']} != 2 * len(chips) {len(chips) * 2}"
221 |         )
```

The other six files under review (including the rest of this same file) are
format-clean; only these two spots drifted. As shipped, this file would fail the CI
format gate on the PR that lands it.
**Fix:** Run the formatter and commit the result:
```bash
cd firestarter_app && python3 -m ruff format tools/measure_plan_shapes.py
```

### WR-02: Drift-test subprocess calls carry no `timeout=`, unlike this same phase's other subprocess-driving module

**File:** `firestarter_app/tests/test_plan_shapes_drift.py:86-91,120-125,138-149`
**Issue:** All three `subprocess.run(...)` call sites in
`test_codegen_produces_byte_identical_output` and
`test_planted_faults_exit_non_zero_and_write_nothing` omit `timeout=`. If the generator
subprocess ever hangs (a genuine bug in `derive()`/`validate()` causing an infinite
loop, an unexpected stdin wait, or a runaway database read), these tests block
indefinitely rather than failing with a diagnosable timeout error — the exact failure
mode `test_skip_census.py`'s own docstring (in this same phase's diff) calls out by
name: "a silently-failed deselect would otherwise recurse until the process died, and
the failure mode here is a clear assertion message instead of a hung/killed process,"
which is why every one of that module's three `subprocess.run` calls sets an explicit
`timeout=` (60/420/30). `test_plan_shapes_drift.py` does not apply the same discipline
to its own three call sites, so a hang here reads as a stuck CI job rather than a clean
red test.
**Fix:** Add a generous but bounded timeout to each call, e.g.:
```python
result = subprocess.run(
    [sys.executable, str(_GEN_SCRIPT), "--target", str(tmp_path)],
    capture_output=True,
    text=True,
    cwd=str(_APP_DIR),
    timeout=60,
)
```
(and similarly for the two `subprocess.run` calls in
`test_planted_faults_exit_non_zero_and_write_nothing`).

### WR-03: `_family_token`'s bare `next()` calls can raise an unhandled `StopIteration`, outside the module's own documented exit-code contract

**File:** `firestarter_app/tools/measure_plan_shapes.py:88,91-93`
**Issue:** The module's docstring promises three exit codes (0 success, 1 validation
failure, 2 "the corpus could not be derived"), and `main()` implements that contract by
wrapping the `plan_corpus()` call in `derive()` with `try/except Exception as exc: raise
DerivationError(...)`. But `_family_token` — called later in the same `derive()` loop,
*outside* that try/except — does:
```python
id_step = next(s for s in steps if s.op == OP_ID)
...
write_idx = next(
    i for i, s in enumerate(steps) if s.op in (OP_WRITE, OP_WRITE_PARTIAL)
)
```
Both use `next()` with no default. If a future plan shape ever lacks an `OP_ID` step or
a write step (the corpus is currently restricted to `SWEEP_SCOPES = ("full",
"partial")`, which always carries a write step per `tests/plan_corpus.py`'s own
docstring, so this is unreachable on the shipped database today), `derive()` propagates
a bare `StopIteration` that `main()` does not catch at all — not as a `DerivationError`
(exit 2) nor a `ValidationError` (exit 1), but as an unhandled exception producing a
default Python traceback and exit code 1, coincidentally overlapping with
`ValidationError`'s exit code for an unrelated reason. A caller scripting against the
documented exit-code contract (e.g., "exit 2 means re-run the derivation, exit 1 means
inspect the payload") would misdiagnose this case.
**Fix:** Either widen the `try/except` in `derive()` to cover the whole per-name loop
(so any shape assumption violation surfaces as a `DerivationError`), or give both
`next()` calls explicit failure messages, e.g.:
```python
id_step = next(
    (s for s in steps if s.op == OP_ID),
    None,
)
if id_step is None:
    raise DerivationError(f"plan {plan.name!r} carries no OP_ID step")
```

---

_Reviewed: 2026-09-04T14:14:40Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
