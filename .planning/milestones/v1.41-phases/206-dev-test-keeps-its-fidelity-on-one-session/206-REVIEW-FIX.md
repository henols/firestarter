---
phase: 206-dev-test-keeps-its-fidelity-on-one-session
fixed_at: 2026-09-23T20:20:00Z
review_path: /workspaces/.planning/phases/206-dev-test-keeps-its-fidelity-on-one-session/206-REVIEW.md
iteration: 1
findings_in_scope: 2
fixed: 2
skipped: 0
status: all_fixed
---

# Phase 206: Code Review Fix Report

**Fixed at:** 2026-09-23
**Source review:** /workspaces/.planning/phases/206-dev-test-keeps-its-fidelity-on-one-session/206-REVIEW.md
**Iteration:** 1

**Summary:**
- Findings in scope: 2 (WR-01, WR-02 — `fix_scope: critical_warning`; IN-01/IN-02 out of scope)
- Fixed: 2
- Skipped: 0

All work was done directly in the `firestarter_app` submodule checkout (repo config has
`workflow.use_worktrees: false`, so no isolated worktree was created — this matches the meta repo's
own worktree opt-out and the task's explicit instruction to commit inside the submodule on its
current branch). Verification (ruff + pytest) also ran there, in the same checkout used for the
edits — not a separate worktree/environment.

## Fixed Issues

### WR-02: `_dispatch_multi_run`'s verify loop kept calling `operator.verify_eprom` after a transport failure (verdict 2) with no early exit

**Files modified:** `firestarter_app/firestarter/chip_test.py`, `firestarter_app/tests/test_chip_test.py`
**Commits:** `f51e17b`, corrected by `64da8f6`
**Applied fix:** A `break` right after a `verify_eprom` call returns verdict `2`. This is the same
early stop that the `SerialError`/`HardwareOperationError` branch in `_run_step_untimed` already
makes. `write`/`write_partial`/`erase` are not changed.

`f51e17b` also changed `StepResult.run_count` from the nominal `runs` to an executed-run counter.
The orchestrator reverted that part in `64da8f6`. `repeat_policy_tag` keys on `run_count == 1` for
every `_REPEAT_POLICY_OPS` step, and `dedup_fingerprint` appends a non-empty tag. So a default
(`runs=2`) run whose verify faulted on run 1 would get the degraded `runs=1` tag. Its report would
then be re-keyed into the `--fast` group. The fixer's note that the verdict/op pair prevents this
was wrong: the tag is appended whatever the verdicts are. `run_count` stays `runs`, which is the
invariant stated above `_REPEAT_POLICY_OPS` ("EXACTLY `run_plan`'s `runs` kwarg").

`test_verify_verdict_2_stops_the_multi_run_loop_after_the_first_run` uses
`verify_eprom.side_effect = [2, 0]` with `runs=2`. It asserts `call_count == 1` (the break fired),
`run_count == 2` and `repeat_policy_tag(results) == ""` (no re-key).

Open observation, not fixed here: the `SerialError`/`HardwareOperationError` branch of
`_run_step_untimed` hard-sets `run_count=1`. A multi-run step that *raises* in a default run
therefore already gets the `runs=1` tag. That behavior was there before this phase, and changing it
would re-key already-filed reports, so it is left for an operator decision.

### WR-01: `_dispatch_step`'s blank-check `on_result` callback silently dropped all but the first `CompareResult`

**Files modified:** `firestarter_app/firestarter/chip_test.py`, `firestarter_app/tests/test_chip_test.py`
**Commit:** `ab6c2e4`
**Applied fix:** Changed `cr = captured_compare[0]` to `cr = captured_compare[-1]` at the blank-check
`compare_evidence` build site, matching the "most recent/finalised" convention
`_aggregate_cycle_results` already documents for `compare_evidence`/`compare_path`/`fingerprint`/
`write_target`. Not live today (`_drive_region_compare` fires `on_result` at most once per call, so
`[0]` and `[-1]` currently coincide) but now degrades gracefully instead of silently truncating if
that ever changes.

The verify-side `captured_compare_verify` list (`_capture_compare_result_verify`, used at
`chip_test.py:3320-3325`) was left unchanged: its content is checked only for truthiness
(`if (op == OP_VERIFY and captured_compare_verify) else ""` at the `compare_path` field), never
indexed, so the same silent-narrowing risk does not exist there yet — the task instructions scoped
this half of the fix to "if its content is read," and it is not.

Added `test_blank_check_compare_evidence_takes_the_last_captured_result`, which fires `on_result`
twice with two distinguishable `CompareResult`s (`bad=9`/`ff_count=1` then `bad=3`/`ff_count=100`)
and asserts `compare_evidence` reflects the second (final) call, not the first.

## Verification

- `ruff check firestarter tests` — clean.
- `ruff format --check firestarter tests` — clean (153 files already formatted).
- Targeted subset — `pytest -o addopts="" -q tests/test_chip_test.py tests/test_chip_test_cycle.py
  tests/test_dev_test_cmd.py tests/test_diagnostic_report.py tests/test_session_lease.py
  tests/test_write_verify.py` — **414 passed**, 0 failed (re-run after `64da8f6`).
- Full suite — `pytest -o addopts="" -q` — **2334 passed, 31 errors** (re-run after `64da8f6`). All 31 errors are the
  pre-existing `snapshot` (syrupy) fixture-missing gap in `tests/test_characterization.py`, unrelated
  to this fix (same 31 the source REVIEW.md's own audit reported, as `2332 passed`; the +2 is this
  fix's two new regression tests). No `test_no_programmer_found_*` live-board failures were observed
  in this run.

---

_Fixed: 2026-09-23_
_Fixer: Claude (gsd-code-fixer)_
_Iteration: 1_
