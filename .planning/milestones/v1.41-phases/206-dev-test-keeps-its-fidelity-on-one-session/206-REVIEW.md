---
phase: 206-dev-test-keeps-its-fidelity-on-one-session
reviewed: 2026-09-23T13:02:18Z
depth: standard
files_reviewed: 16
files_reviewed_list:
  - firestarter_app/firestarter/chip_test.py
  - firestarter_app/firestarter/cli_handlers.py
  - firestarter_app/firestarter/diagnostic_report.py
  - firestarter_app/firestarter/eprom_operations.py
  - firestarter_app/firestarter/serial_comm.py
  - firestarter_app/tests/fake_chip.py
  - firestarter_app/tests/test_blast_radius_invariance.py
  - firestarter_app/tests/test_chip_test.py
  - firestarter_app/tests/test_chip_test_cycle.py
  - firestarter_app/tests/test_dev_test_cmd.py
  - firestarter_app/tests/test_diagnostic_report.py
  - firestarter_app/tests/test_hw_revision_gate.py
  - firestarter_app/tests/test_serial_comm.py
  - firestarter_app/tests/test_session_lease.py
  - firestarter_app/tests/test_write_blank_guard.py
  - firestarter_app/tests/test_write_verify.py
findings:
  critical: 0
  warning: 2
  info: 2
  total: 4
status: issues_found
---

# Phase 206: Code Review Report

**Reviewed:** 2026-09-23T13:02:18Z
**Depth:** standard
**Files Reviewed:** 16
**Status:** issues_found

## Summary

Phase 206 adds three things to `firestarter_app`, scoped by the sub-repo's own
range `2756ef0..d723cf7` (commits `5a772eb`, `c22287a`, `555c69d`, `81ff585`,
`fa6c8e8`, `3853b55`, `d723cf7`): (1) a three-way `blank-check`/`verify`
transport-failure verdict (`VERDICT_SKIPPED` + `STATUS_ERROR`, distinct from a
genuine "not blank"/"mismatch" result), threaded through `_dispatch_step`,
`_dispatch_multi_run` and `_aggregate_cycle_results`; (2) an additive
`compare_evidence`/`compare_path` pair on `StepResult`, wired through
`dedup_fingerprint` with a non-re-keying empty-default discipline consistent
with the existing `repeat_policy_tag`/`coverage_tag` pattern; and (3)
`EpromOperator.lease()`, a session-scoped serial-link reuse seam acquired at
exactly one call site (`cli_handlers.dev_test`), with a documented and tested
asymmetric failure policy (a leased mid-plan `SerialError` propagates and is
caught by `_run_step_untimed`; a cold first-connect failure of the same kind
still degrades silently to `(None, 0)`).

I traced every changed hunk against its callers and the functions it calls
into (`_drive_region_compare`, `_setup_operation`, `_operation_context`,
`_aggregate_cycle_results`, `dedup_fingerprint`), checked the `chip_is_blank`
write-context propagation to confirm the new transport-failure `VERDICT_SKIPPED`
does not get misread as "chip is not blank" (it is correctly excluded — the
guard is `result.verdict in (VERDICT_OK, VERDICT_BAD)` at both of the two call
sites that set it), and ran the full affected test subset (605 tests) plus the
whole `firestarter_app` suite (2332 passed; 31 unrelated `ERROR`s are a
pre-existing environment gap — the `snapshot` fixture from `syrupy` is not
installed in this sandbox, unrelated to any file in this phase) and both
`ruff check`/`ruff format --check`, all clean.

I did not find a Critical/BLOCKER-level defect. I did find two Warning-level
gaps worth fixing (a silent value-truncation in the blank-check evidence
capture, and an unbounded-growth list in the verify multi-run path) and two
Info-level documentation/consistency nits.

## Warnings

### WR-01: `_dispatch_step`'s blank-check `on_result` callback silently drops all but the first `CompareResult`

**File:** `firestarter_app/firestarter/chip_test.py:2696-2718` (see also the identical shape at `firestarter_app/firestarter/chip_test.py:3320-3325`, `_capture_compare_result_verify`)
**Issue:** `_capture_compare_result` appends every invocation to `captured_compare`, but `compare_evidence` is then built from `captured_compare[0]` only:

```python
captured_compare: list[CompareResult] = []

def _capture_compare_result(
    result: CompareResult, _captured=captured_compare
) -> None:
    _captured.append(result)

blank_verdict = operator.check_eprom_blank(
    name, eprom_data, on_result=_capture_compare_result
)
compare_evidence: dict[str, Any] | None = None
if captured_compare:
    cr = captured_compare[0]
    ...
```

Today's shipped `_drive_region_compare` calls `on_result` at most once per
`check_eprom_blank`/`verify_eprom` call, so `captured_compare[0]` is currently
always also the last (and only) entry — this is not live today. But the list
accumulates unboundedly with no cap and no assertion that it holds at most one
element, so a future change to `_drive_region_compare` (e.g. one that reports
per-chunk partial results, or a retry-internally-and-report-both-attempts
change) would silently start discarding every result after the first with no
test failure to catch it — the `[0]` index quietly picks the wrong (stale)
evidence instead of the final one. Given how carefully every other seam in
this phase pins its "exactly one" assumption structurally (see
`test_check_eprom_blank_forwards_on_result_structurally`, the AST-based
proof), this one spot relies on an unstated invariant about the callee it
does not itself enforce.
**Fix:** Either assert the invariant explicitly (`assert len(captured_compare) <= 1`) so a future violation fails loudly instead of silently truncating, or take the last entry (`captured_compare[-1]`) to match the "most recent/finalised" semantics the rest of this phase uses (e.g. `_aggregate_cycle_results` explicitly takes the LAST value for `compare_evidence`/`compare_path`/`fingerprint`/`write_target`). The same fix applies to `_capture_compare_result_verify`'s `captured_compare_verify`, which is checked only for truthiness today but would have the identical silent-narrowing risk the moment any code start reads its content instead of just its emptiness.

### WR-02: `_dispatch_multi_run`'s verify loop keeps calling `operator.verify_eprom` after a transport failure (verdict 2) with no early exit

**File:** `firestarter_app/firestarter/chip_test.py:3410-3452`
**Issue:**

```python
for _ in range(runs):
    ...
    elif op == OP_VERIFY:
        verify_verdict = operator.verify_eprom(
            name, eprom_data, tmp_source_path,
            address_str=_address_arg(region_start),
            on_result=_capture_compare_result_verify,
        )
        verify_verdicts.append(verify_verdict)
        outcomes.append(verify_verdict == 0)
```

If run 1 of `runs` (2 by default) returns verdict `2` (compare did not
complete — a setup, transport or hardware failure), the loop still executes
run 2 unconditionally, issuing a second full verify pass against a link the
first pass just reported as faulted. This is not a correctness bug — the
result is still classified correctly as `VERDICT_SKIPPED`/`STATUS_ERROR`
regardless of what run 2 returns (`verify_transport_failed = any(v == 2 for v
in verify_verdicts)` fires on run 1 alone) — but it means a hard transport
fault (e.g. an unplugged board) that raises inside run 1's own
`_operation_context` on the *next* leased setup would surface as an unhandled
`SerialError` from run 2 rather than the cleaner verdict-2 path run 1 already
established, and every genuinely-faulted run pays a second full
read/compare's worth of device I/O and wall-clock time for no additional
information (the "read repeat measures rig health" rationale documented
elsewhere in this file explicitly does not apply once the first run already
failed to complete).
**Fix:** Break out of the `for _ in range(runs)` loop as soon as a verify run
returns `2`, the same way a raised `SerialError` would already terminate the
step early (via the exception path in `_run_step_untimed`). This also removes
the need to reason about whether a second `on_result` firing after the first
faulted run could ever legitimately disagree with it.

## Info

### IN-01: `EpromOperator.lease()`'s docstring reference to "roughly thirty calls" is unverified against the shipped op count

**File:** `firestarter_app/firestarter/eprom_operations.py:759-778`
**Issue:** The docstring states "A lease holding one link across roughly thirty calls removes roughly thirty board resets," extrapolating from the SDP-leg-inclusive full step count (`derive_plan`'s docstring elsewhere counts the SDP leg alone as 6 steps, plus id/read/blank-check/write/verify/erase at up to 2-3 cycles each). This is a comment, not executable code, so it cannot desync silently in a way that breaks a test, but it is exactly the kind of specific numeric claim this codebase's own convention (extensive load-bearing docstrings) treats as something a future reader will cite as fact.
**Fix:** Either derive the count from `len(_SDP_LEG_STEP_ORDER)` plus the plan's live step count in the comment (as `derive_plan`'s own docstring does for the SDP leg), or soften the wording to "on the order of thirty" / drop the specific number, consistent with how other approximate figures in this codebase are phrased when not measured (contrast with `206-SESSION-COST.md`'s measured 15.1%, which is exact and dated).

### IN-02: `setup_command`'s docstring "two production callers" claim is only true for the two call sites visible in `serial_comm.py`/`eprom_operations.py`

**File:** `firestarter_app/firestarter/serial_comm.py:838-844`
**Issue:** The docstring for `setup_command` asserts "Both production callers only ever invoke this on a link they have just confirmed is open." This is true for `_probe_port` and the leased branch of `_setup_operation` as reviewed, but the claim is stated as an invariant the method itself relies on (it does not re-check `is_connected()` before calling `send_bytes`) rather than something enforced by a type or a runtime assertion. A future third caller (e.g. a future `fw --install` refactor reusing this method directly) that forgets the `is_connected()` precondition would get `SerialError("Not connected.")` from deep inside `send_bytes` rather than a clearer message naming `setup_command`'s own precondition.
**Fix:** Not a functional defect given the current two call sites (confirmed via `grep -rn "\.setup_command("`), but worth a lightweight `assert self.is_connected()` at the top of `setup_command` (cheap, and turns a future violation into an assertion at the right call frame instead of a generic "Not connected." several frames down) if this method is ever expected to gain a third caller.

---

_Reviewed: 2026-09-23T13:02:18Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
