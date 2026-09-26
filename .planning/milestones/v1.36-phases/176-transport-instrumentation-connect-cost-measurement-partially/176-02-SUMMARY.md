---
phase: 176-transport-instrumentation-connect-cost-measurement-partially
plan: 02
subsystem: instrumentation
tags: [transport-health, dev-test, diagnostic-report, serial-comm, blast-radius-invariance]

requires:
  - phase: 176-transport-instrumentation-connect-cost-measurement-partially
    provides: "plan 176-01's transport_counters.py sink, decode_failures wired end to end, _SUSPECT_SCANNED_FIELDS extraction, Phase 174 pin at six keys"
provides:
  - "record_response_timeout() + probe_scope(): a get_response timeout routes to timeouts on an established connection and to probe_timeouts during port discovery, so an unscoped counter can never inflate transport_suspect on a healthy multi-board rig"
  - "TransportHealth.probe_timeouts, deliberately OUTSIDE the suspicion domain via _SUSPECT_EXCLUDED_FIELDS"
  - "_is_transport_suspect's present-AND-elevated rule proven unchanged in all four assertable senses (None never contributes, 0 is present-not-absent, comparison stays >=, any one counter suffices), plus a dataclasses.fields()-derived closure test so a future counter cannot silently escape the suspicion domain"
  - "_SUSPECT_THRESHOLD = 5's basis recorded and pinned in the _is_transport_suspect docstring (MEAS-02)"
  - "TransportHealth docstring rewritten with MEAS-03's full recorded trace: why cobs_errors, crc_failures and retries stay not measured, each reason pinned by a substring test"
  - "Phase 174 pin moved to seven keys, all 16 snapshots regenerated in the same commit as the production change (Task 1)"
affects: [176-03, 176-04, 176-05]

actuals:
  tokens: 7150
  tasks: 3
  commits: 3

tech-stack:
  added: []
  patterns:
    - "Scope-routing counter: a single increment call (record_response_timeout) resolves its target counter from ambient module state (_in_probe_scope) set by a context manager, rather than the caller passing a counter name -- keeps the call site at get_response a one-line addition"
    - "contextmanager restores the PREVIOUS value in finally, never a hard reset, so a scope entered from inside another scope (or one an exception escapes) cannot leave the sink stuck in the wrong mode"
    - "Domain-closure test: assert set(_SUSPECT_SCANNED_FIELDS) | set(_SUSPECT_EXCLUDED_FIELDS) == the live dataclass counter-field set (via dataclasses.fields), so a counter a later phase adds and forgets to classify fails a test instead of silently escaping the suspicion domain"

key-files:
  created: []
  modified:
    - firestarter_app/firestarter/transport_counters.py
    - firestarter_app/firestarter/serial_comm.py
    - firestarter_app/firestarter/diagnostic_report.py
    - firestarter_app/firestarter/cli_handlers.py
    - firestarter_app/tests/test_transport_counters.py
    - firestarter_app/tests/test_diagnostic_report.py
    - firestarter_app/tests/test_blast_radius_invariance.py
    - firestarter_app/tests/fixtures/reports/*.json (16 files, one added line each)

key-decisions:
  - "Split the diagnostic_report.py docstring work strictly by task, even though I initially drafted it all in one pass: Task 1 gets only the one-sentence probe_timeouts exclusion note, Task 2 gets the MEAS-02 threshold-basis paragraph, Task 3 gets the full per-counter MEAS-03 rewrite. Caught before the Task 1 commit and re-split so each commit's diff matches its own task's <action> exactly -- the atomic-close-out invariant requires this, and bundling would have made Task 2/3's own anti-vacuity gates test content that didn't originate in their own commit."
  - "Deleted the module-level comment above _SUSPECT_THRESHOLD (\"dormant today -- no transport counter is reachable\") in Task 3, per that task's explicit instruction -- the claim is now false for five counters. Left untouched during Tasks 1 and 2 per their own instruction not to edit it."
  - "Added test_find_and_connect_wraps_probe_port_call_in_probe_scope (monkeypatching _probe_port, mirroring the existing test_find_and_connect_threads_fault_inject_outgoing pattern) because the plan's six named behaviors all exercise probe_scope()/record_response_timeout() directly -- none of them would go red if the with transport_counters.probe_scope(): wrapper were deleted from find_and_connect itself. This closed a real anti-vacuity gap for weakening w2."
  - "Added test_nested_probe_scope_restores_previous_value_not_hard_false after discovering the plan's own w3 weakening (hard False instead of restoring the previous value) did NOT go red under the originally-planned test set -- a single-level scope with previous=False looks identical to a hard reset. Nesting is required to distinguish them."
  - "TransportHealth(**dict) constructor calls in the four/five/six-boundary and any-one-suffices tests hit a mypy arg-type error (the dataclass's __init__ mixes int|None fields with one bool field, so **dict[str, int] fails signature matching). Added a _health_with(**counters: int | None) -> TransportHealth helper that builds via setattr instead of the constructor, which satisfies the mypy watermark without weakening what the tests assert."

requirements-completed: []

coverage:
  - id: D1
    description: "A get_response timeout on an established connection raises timeouts by exactly one and moves nothing else in the whole snapshot; the same timeout inside probe_scope() raises probe_timeouts instead and leaves timeouts at zero"
    requirement: "RPT-C1"
    verification:
      - kind: unit
        ref: "tests/test_transport_counters.py#test_established_timeout_raises_timeouts_and_nothing_else"
        status: pass
      - kind: unit
        ref: "tests/test_transport_counters.py#test_probe_scoped_timeout_raises_probe_timeouts_and_nothing_else"
        status: pass
      - kind: unit
        ref: "tests/test_transport_counters.py#test_find_and_connect_wraps_probe_port_call_in_probe_scope"
        status: pass
    human_judgment: false
  - id: D2
    description: "probe_scope() is strictly bounded: a timeout after the with block exits counts as an established timeout, and the scope restores the PREVIOUS state (not a hard reset) even when the body raises or is nested"
    requirement: "RPT-C1"
    verification:
      - kind: unit
        ref: "tests/test_transport_counters.py#test_timeout_after_scope_exit_counts_as_established_timeout"
        status: pass
      - kind: unit
        ref: "tests/test_transport_counters.py#test_probe_scope_restores_previous_state_when_body_raises"
        status: pass
      - kind: unit
        ref: "tests/test_transport_counters.py#test_nested_probe_scope_restores_previous_value_not_hard_false"
        status: pass
    human_judgment: false
  - id: D3
    description: "_is_transport_suspect's present-AND-elevated rule is unchanged in all four assertable senses, and probe_timeouts is provably excluded from the suspicion domain"
    requirement: "RPT-C2"
    verification:
      - kind: unit
        ref: "tests/test_transport_counters.py#test_none_field_never_contributes_to_suspicion"
        status: pass
      - kind: unit
        ref: "tests/test_transport_counters.py#test_zero_is_present_and_not_elevated_while_threshold_is"
        status: pass
      - kind: unit
        ref: "tests/test_transport_counters.py#test_threshold_boundary_stays_greater_or_equal"
        status: pass
      - kind: unit
        ref: "tests/test_transport_counters.py#test_any_single_scanned_field_alone_at_threshold_suffices"
        status: pass
      - kind: unit
        ref: "tests/test_transport_counters.py#test_probe_timeouts_excluded_from_suspicion_domain"
        status: pass
    human_judgment: false
  - id: D4
    description: "The suspicion domain is closed against silent escape: every TransportHealth counter field is in either _SUSPECT_SCANNED_FIELDS or _SUSPECT_EXCLUDED_FIELDS, computed from the live dataclass"
    requirement: "RPT-C2"
    verification:
      - kind: unit
        ref: "tests/test_transport_counters.py#test_suspicion_domain_is_closed_against_a_silently_added_counter"
        status: pass
    human_judgment: false
  - id: D5
    description: "_SUSPECT_THRESHOLD stays 5, with its basis recorded and pinned in the _is_transport_suspect docstring (the 32-connect / sixth-wrong-port-probe argument, and the rejected per-counter-threshold alternative)"
    requirement: "MEAS-02"
    verification:
      - kind: unit
        ref: "tests/test_transport_counters.py#test_meas02_basis_is_recorded_and_pinned_in_docstring"
        status: pass
    human_judgment: false
  - id: D6
    description: "cobs_errors, crc_failures and retries keep NOT_MEASURED, each with a durable, test-pinned reason recorded in the TransportHealth docstring; the stale Transport-Counter-Survey claim is gone; neither report-consuming skill script references transport_health"
    requirement: "MEAS-03"
    verification:
      - kind: unit
        ref: "tests/test_transport_counters.py#test_unwired_counter_reasons_are_recorded_and_pinned_in_docstring"
        status: pass
      - kind: other
        ref: "evidence/176-02-meas03-trace.txt (skill_transport_refs=0)"
        status: pass
    human_judgment: false
  - id: D7
    description: "The Phase 174 oracle is green before and after this plan at 114 passed, with the pin at seven keys and all 16 snapshots moved deliberately in the same commit as the production change"
    verification:
      - kind: unit
        ref: "tests/test_blast_radius_invariance.py + tests/test_rekey_ledger.py (114 passed)"
        status: pass
      - kind: other
        ref: "tools/snapshot_report_shapes.py --check (exit 0, 16 files, one insertion each)"
        status: pass
    human_judgment: false
  - id: D8
    description: "Full app suite green (2183 passed, up from 2158 at wave 1 close), ruff clean, mypy watermark unmoved at 35, zero comment lines added to any file this plan touched"
    verification:
      - kind: unit
        ref: "pytest tests/ (2183 passed, 32 snapshots passed)"
        status: pass
      - kind: other
        ref: "ruff check / ruff format --check / tools/check_mypy_watermark.py"
        status: pass
    human_judgment: false

duration: 35min
completed: 2026-09-04
status: complete
---

# Phase 176 Plan 02: get_response timeout wired and scoped, unchanged-rule proven, MEAS-02/03 recorded Summary

**`get_response`'s timeout now lands in `timeouts` on an established connection and in `probe_timeouts` during port discovery via a `probe_scope()` context manager, `_is_transport_suspect`'s present-AND-elevated rule is proven unchanged in all four assertable senses with a closure test against future counters, `_SUSPECT_THRESHOLD = 5`'s basis is recorded and pinned, and the three permanently-unwired counters (`cobs_errors`, `crc_failures`, `retries`) each carry a durable, test-pinned reason in the `TransportHealth` docstring.**

## Performance

- **Duration:** ~35 min
- **Started:** 2026-09-04T20:58:00Z (approx, immediately after 176-01 closed)
- **Completed:** 2026-09-04T21:33:00Z
- **Tasks:** 3
- **Files modified:** 4 production files + 3 test files + 16 snapshot fixtures (across the 3 commits)

## Accomplishments

- `transport_counters.py` gained `timeouts`/`probe_timeouts` counters, `record_response_timeout()` (routes by ambient `_in_probe_scope` state) and `probe_scope()` (a `contextmanager` that restores the PREVIOUS state in `finally`, never a hard reset).
- `serial_comm.py`'s `get_response` increments before its existing `logger.warning`/`raise SerialTimeoutError`; `find_and_connect` wraps ONLY the single `cls._probe_port(...)` call in `probe_scope()` -- confirmed the sole occurrence in the file, so the scope exits the instant probing succeeds.
- `diagnostic_report.py`: `TransportHealth` gained `probe_timeouts`, a new `_SUSPECT_EXCLUDED_FIELDS = ("probe_timeouts",)` keeps it out of `_SUSPECT_SCANNED_FIELDS`, `_is_transport_suspect`'s docstring now records MEAS-02's basis (the 32-connect / sixth-wrong-port-probe argument, and the rejected per-counter-threshold alternative), and `TransportHealth`'s own docstring records MEAS-03's full per-counter trace (why `cobs_errors`/`crc_failures`/`retries` stay `not measured`). The stale module comment claiming a survey verified no counter was reachable is deleted (false for five counters now).
- `cli_handlers.py`'s `dev_test` assigns `report.transport.timeouts` and `.probe_timeouts` from the existing post-`run_plan` snapshot, alongside the pre-existing `decode_failures` assignment.
- `tests/test_transport_counters.py` grew from 9 to 31 tests: the routing/scoping behaviors (established vs. probe-scoped vs. after-scope-exit vs. nested vs. exception-escaping), the four unchanged-rule propositions plus a `dataclasses.fields()`-derived domain-closure test, and the MEAS-02/MEAS-03 docstring-pin tests.
- Phase 174's `_TRANSPORT_HEALTH_KEYS` pin moved from six keys to seven (sorted, `probe_timeouts` fourth), the next-key guard now names `resync_body_truncated` (plan 176-03's key), and all 16 committed report snapshots were regenerated in the SAME commit as the production change -- one added line each, zero deletions, `--check` confirms zero drift.
- Two anti-vacuity rounds recorded in `evidence/176-02-anti-vacuity-red-green.txt`: Task 1's w1 (deleted increment), w2 (deleted the `probe_scope()` wrapper from `find_and_connect`), w3 (hard-`False` scope restore, caught only after adding a nesting test); Task 2's w5 (`>` instead of `>=`), w6 (reordered conjuncts, raises on `None`), w7 (`probe_timeouts` added to `_SUSPECT_SCANNED_FIELDS`). All six weakenings were SEEN red, then restored to green.

## Task Commits

Each task was committed atomically inside the `firestarter_app` submodule (on `gsd/v1.36-dev-test-fidelity`):

1. **Task 1: Site D wired and scoped -- timeouts for established connections, probe_timeouts for the discovery walk** - `7850175` (feat)
2. **Task 2: The unchanged rule, proven in four senses, and MEAS-02's recorded basis** - `613cbaf` (test)
3. **Task 3: MEAS-03's recorded trace -- why cobs_errors, crc_failures and retries stay not measured** - `801dba3` (docs)

**Plan metadata:** not committed in `/workspaces` -- see Deviations below (this run's execution-context instructions override the plan's own `<output>` section).

## Files Created/Modified

- `firestarter_app/firestarter/transport_counters.py` - `timeouts`/`probe_timeouts` counters, `record_response_timeout()`, `probe_scope()`
- `firestarter_app/firestarter/serial_comm.py` - `get_response` increments before its timeout raise; `find_and_connect` scopes the single `_probe_port` call
- `firestarter_app/firestarter/diagnostic_report.py` - `probe_timeouts` field, `_SUSPECT_EXCLUDED_FIELDS`, MEAS-02 basis + MEAS-03 trace recorded in docstrings, stale survey comment deleted
- `firestarter_app/firestarter/cli_handlers.py` - `dev_test` assigns `timeouts`/`probe_timeouts` from the snapshot
- `firestarter_app/tests/test_transport_counters.py` - grew to 31 tests across all three tasks
- `firestarter_app/tests/test_diagnostic_report.py` - `test_transport_not_measured` extended with `probe_timeouts`
- `firestarter_app/tests/test_blast_radius_invariance.py` - `_TRANSPORT_HEALTH_KEYS` pin moved to seven keys, next-key guard renamed to `resync_body_truncated`
- `firestarter_app/tests/fixtures/reports/*.json` (16 files) - regenerated snapshots carrying `probe_timeouts`

## Decisions Made

- Split the `diagnostic_report.py` docstring work strictly by task after an initial draft bundled all three tasks' content into one edit (see Deviations).
- Deleted the stale `_SUSPECT_THRESHOLD` module comment in Task 3 only, per that task's explicit instruction; left untouched in Tasks 1/2 per their own instruction not to edit it.
- Added `_health_with()` test helper (builds `TransportHealth` via `setattr` rather than the constructor) to keep the mypy watermark at 35 when constructing counters from a dict without tripping the dataclass's mixed `int | None` / `bool` field typing.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug, self-caught] Over-scoped Task 1's diagnostic_report.py edit to include Task 2 and Task 3 content**
- **Found during:** Reviewing the diff before Task 1's commit
- **Issue:** The first draft of the `TransportHealth`/`_is_transport_suspect` docstring edit wrote the FULL MEAS-02 basis paragraph and the FULL MEAS-03 per-counter trace in one pass, even though those belong to Tasks 2 and 3 respectively per their own `<action>` text. This would have made Task 1's commit carry content its own task never asked for, and left Tasks 2/3 with nothing new to add (breaking the atomic-close-out invariant of one task = one commit = that task's own diff).
- **Fix:** Reverted the docstrings to a minimal Task-1-only version (field addition, `_SUSPECT_EXCLUDED_FIELDS`, and the one-sentence exclusion note Task 1's own `<action>` explicitly calls for) before committing Task 1. Re-applied the MEAS-02 basis paragraph in Task 2's commit and the MEAS-03 trace rewrite in Task 3's commit, each verified independently against that task's own `<verify>` block.
- **Files modified:** `firestarter_app/firestarter/diagnostic_report.py`
- **Verification:** Each task's own automated `<verify>` script re-run and confirmed passing against the commit boundary that actually introduced its content (`git diff` against the immediately-preceding commit, not the plan start).
- **Committed in:** `7850175` (Task 1, trimmed), `613cbaf` (Task 2, MEAS-02 basis), `801dba3` (Task 3, MEAS-03 trace)

**2. [Rule 2 - Missing critical] Added an integration-level test proving find_and_connect actually wraps _probe_port in probe_scope()**
- **Found during:** Task 1, anti-vacuity weakening w2
- **Issue:** The plan's five named `<behavior>` items for Task 1 all exercise `transport_counters.probe_scope()`/`record_response_timeout()` directly. None of them call `find_and_connect`, so deleting the `with transport_counters.probe_scope():` wrapper from `find_and_connect` (weakening w2) would NOT have been caught by any test as originally scoped -- the production wiring itself was untested.
- **Fix:** Added `test_find_and_connect_wraps_probe_port_call_in_probe_scope`, monkeypatching `_probe_port` (mirroring the existing `test_find_and_connect_threads_fault_inject_outgoing` pattern) to call `record_response_timeout()` itself and asserting the increment lands in `probe_timeouts`, not `timeouts`.
- **Files modified:** `firestarter_app/tests/test_transport_counters.py`
- **Verification:** Anti-vacuity transcript shows this test going red under w2 (`assert snap["probe_timeouts"] == 1` fails with `0 == 1`) and green after restore.
- **Committed in:** `7850175` (Task 1 commit)

**3. [Rule 2 - Missing critical] Added a nested-scope test to actually catch the hard-False weakening**
- **Found during:** Task 1, anti-vacuity weakening w3 (first attempt)
- **Issue:** The originally-planned test set (single-level `probe_scope()` with an escaping exception) did NOT go red when `probe_scope()`'s `finally` clause was changed to restore a hard `False` instead of the previous value -- at the top level, `previous` is always `False` anyway, so the weakening is indistinguishable from the correct implementation under a single-level test.
- **Fix:** Added `test_nested_probe_scope_restores_previous_value_not_hard_false`: an outer `probe_scope()` containing an inner `probe_scope()` that exits cleanly, then a `record_response_timeout()` call inside the outer scope -- this only lands in `probe_timeouts` (not `timeouts`) if the inner scope's exit restored `True` (the outer scope's own state) rather than clearing to `False`.
- **Files modified:** `firestarter_app/tests/test_transport_counters.py`
- **Verification:** Re-ran w3 against the new test; it went red (`assert snap["probe_timeouts"] == 1` fails with `0 == 1`), then green after restore. Both the original (non-catching) and redone (catching) w3 runs are preserved in the evidence transcript for the record.
- **Committed in:** `7850175` (Task 1 commit)

**4. [Rule 3 - Blocking] mypy arg-type errors from `TransportHealth(**dict)` constructor calls**
- **Found during:** Task 2, after adding the four/five/six-boundary and any-one-suffices tests
- **Issue:** `TransportHealth`'s generated `__init__` mixes `int | None` counter fields with one `bool` field (`transport_suspect`). Calling it with `**{name: value}` from a dict typed `dict[str, int]` or `dict[str, None]` fails mypy's `arg-type` check because a uniform-value dict splat cannot be verified against a mixed-type signature, pushing the watermark from 35 to 39.
- **Fix:** Added a `_health_with(**counters: int | None) -> TransportHealth` test helper that constructs a default `TransportHealth()` then sets fields via `setattr`, which mypy does not check against the specific per-field type. Used it only where a dynamic dict of field names was genuinely needed (`test_none_field_never_contributes_to_suspicion`, `test_any_single_scanned_field_alone_at_threshold_suffices`); left the fixed-field-name tests (`test_zero_is_present_and_not_elevated_while_threshold_is`, boundary test, `test_probe_timeouts_excluded_from_suspicion_domain`) on the plain constructor, which mypy accepts natively.
- **Files modified:** `firestarter_app/tests/test_transport_counters.py`
- **Verification:** `tools/check_mypy_watermark.py` back to `mypy errors: 35 (watermark: 35)`; all affected tests re-run green; re-ran the w5/w6/w7 anti-vacuity weakenings against this finalized test file to confirm they still go red (they do).
- **Committed in:** `613cbaf` (Task 2 commit)

---

**Total deviations:** 4 (1 self-caught scope-splitting fix, 2 anti-vacuity test-coverage strengthenings, 1 typing fix). **Impact on plan:** None affect production behavior. Deviation 1 restores the plan's own intended one-task-one-commit structure; deviations 2 and 3 close real anti-vacuity gaps the plan's own gate exists to catch; deviation 4 is a mechanical typing fix with no test-semantics change. No scope creep.

## Issues Encountered

None beyond the four items above.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- `timeouts` and `probe_timeouts` are wired and scoped end to end; plan 176-03 adds the two re-sync counters (`resync_length_missing`, `resync_body_truncated`) along the same proven path, moving the Phase 174 pin from seven keys to nine.
- `_is_transport_suspect`'s domain-closure test means 176-03's two new counters MUST be explicitly placed in `_SUSPECT_SCANNED_FIELDS` or a future exclusion set, or the closure test will fail loudly rather than silently passing them through.
- The Phase 174 oracle is green at 114 passed, matching the precondition measured before this plan touched anything. Full app suite: 2183 passed (up from 2158 at wave 1 close), 32 snapshot checks passed; `ruff check`, `ruff format --check` and the mypy watermark (`35 (watermark: 35)`) all hold.
- RPT-C1, RPT-C2, MEAS-02 and MEAS-03 remain Pending per this plan's own `<output>` instruction -- plan 176-04 marks them Complete once the whole software half (176-03's re-sync counters) is sealed.
- No blockers for 176-03.

## Self-Check: PASSED

- `firestarter_app/firestarter/transport_counters.py` exists and contains `def probe_scope`: confirmed.
- `firestarter_app/tests/test_transport_counters.py` exists and references `probe_scope`: confirmed.
- Commit `7850175` exists in `firestarter_app`'s `git log`: confirmed.
- Commit `613cbaf` exists in `firestarter_app`'s `git log`: confirmed.
- Commit `801dba3` exists in `firestarter_app`'s `git log`: confirmed.
- `tests/test_blast_radius_invariance.py` + `tests/test_rekey_ledger.py` at 114 passed both before and after this plan: confirmed.
- Full `firestarter_app` suite at 2183 passed, 32 snapshots passed, exit code 0: confirmed.
- `ruff check`, `ruff format --check`, mypy watermark (`35 (watermark: 35)`): confirmed.
- `evidence/176-02-timeout-scoping.txt`, `evidence/176-02-unchanged-rule.txt`, `evidence/176-02-meas03-trace.txt` and `evidence/176-02-anti-vacuity-red-green.txt` all exist with the required markers: confirmed.
- Zero comment lines added to any file created or edited (`transport_counters.py`, `serial_comm.py`, `diagnostic_report.py`, `cli_handlers.py`, `test_transport_counters.py` all checked with `/usr/bin/grep`): confirmed.

---
*Phase: 176-transport-instrumentation-connect-cost-measurement-partially*
*Completed: 2026-09-04*
