---
phase: 143-host-timeout-progress-pulse-override
plan: 04
subsystem: host-protocol
tags: [python, pytest, serial-protocol, timeout, mock-autospec, cap-03, host-04, pulse-override]

# Dependency graph
requires:
  - phase: 143-02
    provides: "write_block_budget_s: Optional[int] on SerialCommunicator, decoded from MSG_OK_READY's CAP-03 field, plus WRITE_BUDGET_MAX_S"
provides:
  - "WRITE_BLOCK_TIMEOUT_FALLBACK_S = 120.0 and EpromOperator._write_block_timeout() -- the write path's MAIN-phase get_response timeout, read verbatim from write_block_budget_s inside write_eprom's _operation_context with-block, falling back to 120.0 when absent or implausible"
  - "_main_phase_send_data's response_timeout: Optional[float] = None kwarg -- write_eprom passes it, verify_eprom does not, so verify stays on DEFAULT_RESPONSE_TIMEOUT"
  - "write_eprom's pulse_us: int = 0 parameter -- HOST-04's transport half, riding the existing 'pulse-delay' DB-dict key on a shallow copy, no new wire field"
  - "tests/test_write_response_budget.py (6 tests) and tests/test_pulse_us_override.py (4 tests), both with real-27C-chip drivers reusable by plans 143-07 and 143-10"
affects: [143-07, 143-09, 143-10, 144]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Call-argument oracle for timeout proofs: wrap SerialCommunicator.get_response with an autospec=True, delegating (never stub) side_effect, and assert the (self-already-excluded) args/kwargs it was called with -- deterministic, millisecond-fast, never waits out a real timeout (Pitfall 6)"
    - "Second line of defence: a consumer-side plausibility range check that mirrors a wire-decoder's own clamp, so a value that somehow bypassed the decoder is still refused by the consumer"
    - "DB-dict per-run override: rebind eprom_data_dict to a shallow copy and set an already-emitted key BEFORE _operation_context, so no new wire field or command is needed (consistency_check_eprom's read_settling_us/read_strobe_us shape, now also used for write_eprom's pulse_us)"

key-files:
  created:
    - firestarter_app/tests/test_write_response_budget.py
    - firestarter_app/tests/test_pulse_us_override.py
  modified:
    - firestarter_app/firestarter/eprom_operations.py

key-decisions:
  - "_write_block_timeout implements a SYMMETRIC [1, WRITE_BUDGET_MAX_S] range check (WRITE_BUDGET_MAX_S imported from serial_comm), not the lower-bound-only test the plan's Task 2 action prose and threat-model row literally describe -- required so Test 3's mandated 999999 sub-case (not just 0) falls back to 120.0. See 'Plan-Internal Tension Resolved' below."
  - "Strengthened Test 4 and Test 5 beyond a literal reading of the plan's per-test spec to guarantee genuine RED before Task 2 landed (D-25) -- a weaker assertion would have passed vacuously on the pre-Task-2 code, for the wrong reason. See 'D-25 Evidence' below."
  - "Test 6 (fake-clock oracle) legitimately PASSES both before and after Task 2 -- it proves a pre-existing serial_comm mechanism (get_response's own arbitrary-timeout handling), not new behaviour this plan adds. Recorded as an honest characterization, not forced to a false RED."
  - "Real chip used in both new test modules: w27c512 (W27C512,W27E512; algorithm 7 / protocol 0x07 EPROM_STD) -- already the shared canonical non-0x0D fixture chip in tests/test_write_skip_sdp_unlock.py."

patterns-established:
  - "Pattern: a driver that patches SerialCommunicator.find_and_connect to inject a comm instance with a pre-set attribute (here, write_block_budget_s) lets a test simulate any CAP-03 advertisement without needing a real multi-field ack -- reusable by plan 143-10's cross-repo evidence pass."

requirements-completed: []

coverage:
  - id: D1
    description: "HOST-01 write-path timeout: the advertised write_block_budget_s is used verbatim as the MAIN-phase get_response timeout, falls back to a derived 120.0 s when absent/zero/implausibly-large, and never leaks onto verify/blank-check/erase or the write's own INIT/END phases"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_write_response_budget.py::test_write_uses_advertised_budget"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_write_response_budget.py::test_absent_budget_falls_back_to_120s"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_write_response_budget.py::test_implausible_budget_is_clamped_away"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_write_response_budget.py::test_non_write_paths_keep_default_timeout"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_write_response_budget.py::test_init_and_end_phases_keep_default_timeout"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_write_response_budget.py::test_long_gap_within_budget_does_not_time_out"
        status: pass
    human_judgment: false
  - id: D2
    description: "HOST-04 transport half: write_eprom's pulse_us rides the existing 'pulse-delay' wire key on a shallow copy, adding no key and mutating no caller dict, and leaving the database value alone when absent -- CLI flag/bounds/report line deliberately out of scope (plan 143-07)"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_pulse_us_override.py::test_override_rides_the_db_dict"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_pulse_us_override.py::test_override_does_not_mutate_the_caller_dict"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_pulse_us_override.py::test_no_new_wire_field_is_added"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_pulse_us_override.py::test_absent_flag_leaves_db_pulse"
        status: pass
    human_judgment: false

duration: ~40min
completed: 2026-08-13
status: complete
---

# Phase 143 Plan 04: Write-Path Response Timeout + Pulse Override (Transport Half) Summary

**`write_eprom`'s MAIN-phase wait now uses the firmware-advertised per-block budget verbatim (falling back to a derived 120 s when absent or implausible), every other operation still waits exactly 10 s, and `write_eprom` accepts a `pulse_us` override that rides the existing `pulse-delay` wire key -- all proven by a call-argument oracle that never waits out a real timeout.**

## Performance

- **Duration:** ~40 min
- **Started:** ~2026-08-13T00:44Z (STATE.md hand-off from 143-03)
- **Completed:** 2026-08-13T01:23Z
- **Tasks:** 3 completed (all `type="auto"`, no checkpoints)
- **Files touched:** 3 (2 created, 1 modified)

## Accomplishments

- `firestarter/eprom_operations.py`: `WRITE_BLOCK_TIMEOUT_FALLBACK_S = 120.0` added to the module constant block, with the full derivation in its comment (51.2 s worst shipped `0x0B`, 25.6 s `0x07`/`0x08`, the every-reachable-`0x0B`-width fact via the 99998 us per-byte ceiling, and the residual non-claim naming the Leonardo/Uno gap and the corrected realistic absent-advertisement case). `_write_block_timeout()` added on `EpromOperator`, reading `write_block_budget_s` verbatim (D-09) with a `[1, WRITE_BUDGET_MAX_S]` range test as a second line of defence (D-10). `_main_phase_send_data` gained `response_timeout: Optional[float] = None` and now calls `self.comm.get_response(timeout)`; `write_eprom` passes `response_timeout=self._write_block_timeout()` from inside its `_operation_context` `with` block; `verify_eprom` is byte-unchanged.
- `write_eprom` gained `pulse_us: int = 0` (last parameter). When truthy, it rebinds `eprom_data_dict` to a shallow copy and sets `["pulse-delay"] = pulse_us` **before** `_operation_context`, so `_setup_operation`'s own `command_dict = eprom_data_dict.copy()` carries it onto the wire -- no new wire field, no new command (HOST-04 structural satisfaction).
- `tests/test_write_response_budget.py`: six tests (call-argument oracle via an `autospec=True`, delegating `SerialCommunicator.get_response` wrapper, plus one fake-clock oracle) pinning the verbatim budget, the 120 s fallback on absent/zero/implausibly-large advertisement, D-12's negative proof for `verify_eprom`/`check_eprom_blank`/`erase_eprom`, D-13's INIT/END default, and a sub-second proof that the read loop survives a simulated >10 s gap.
- `tests/test_pulse_us_override.py`: four tests proving the override rides the DB dict verbatim, mutates no caller dict, adds zero wire keys (rejecting both `"pulse-us"` and `"pulse_us"` literal spellings), and leaves the database value alone when `pulse_us` is absent.
- Full host suite: **1562 passed** (1552 after plan 143-02, plus 6 + 4 = 10 from this plan), coverage **82.80%** (>= 70% floor). `ruff check`/`ruff format --check` clean. mypy watermark exit 0 (33 errors, 2 below the 35 watermark -- pre-existing, unmoved). `git diff` confirms zero hunks in `serial_comm.py`, `cli_handlers.py`, `constants.py`, `messages.py` across all three commits (D-13, GATE-1.8d; HOST-04's no-new-wire-field claim).
- `firestarter` (firmware) repo porcelain was clean before the coverage leg -- no L-6 deselection was needed, and this is recorded per the plan's instruction even though the empty case "needs no note" (recorded anyway, for completeness: `git -C /workspaces/firestarter status --porcelain` returned nothing).

## Task Commits

Each task was committed atomically, inside `/workspaces/firestarter_app` on branch `gsd/v1.31-27c-programming-algorithm-fidelity`:

1. **Task 1: Author `tests/test_write_response_budget.py` -- five HOST-01 oracles plus D-12's negative proof, all RED** - `628e5ac` (test)
2. **Task 2: Thread the write-path timeout through `eprom_operations.py` and turn the module GREEN** - `0def706` (feat)
3. **Task 3: Add `write_eprom`'s `pulse_us` parameter and create `tests/test_pulse_us_override.py`'s transport half** - `a3fc955` (feat)

**Plan metadata:** committed in the meta repo (`/workspaces`), see below.

## Files Created/Modified

- `firestarter_app/firestarter/eprom_operations.py` - `WRITE_BLOCK_TIMEOUT_FALLBACK_S` constant; `EpromOperator._write_block_timeout()`; `response_timeout` kwarg + docstring on `_main_phase_send_data`; `write_eprom`'s `response_timeout=self._write_block_timeout()` call-site addition and its new `pulse_us` parameter + DB-dict override block. Seven hunks total, all inside the import block, the module constant block, and `EpromOperator`'s `_write_block_timeout`/`_main_phase_send_data`/`write_eprom` -- `git diff` confirms zero hunks in `_execute_phase`, `_handle_progress_response`, `ClassProgressHandler`, `_run_state_machine`'s signature, `_calculate_buffer_size`, `_boot_block_hint_message`, `_setup_operation`, `consistency_check_eprom`, or `verify_eprom`.
- `firestarter_app/tests/test_write_response_budget.py` (new, 6 tests) - HOST-01 call-argument + fake-clock oracles, D-12's negative proof.
- `firestarter_app/tests/test_pulse_us_override.py` (new, 4 tests) - HOST-04's `write_eprom`-transport half; module docstring states it is authored in two halves by two plans and that HOST-04 spans both.

## Decisions Made

- **`_write_block_timeout`'s range test is symmetric (`[1, WRITE_BUDGET_MAX_S]`), not lower-bound-only.** See "Plan-Internal Tension Resolved" below -- this is the one place this plan's own text disagreed with itself, and the resolution favors the tests (the acceptance contract) over the action prose.
- **Test 4 and Test 5 needed a "contrast" assertion to be genuinely RED before Task 2 (D-25).** See "D-25 Evidence" below.
- **Test 6 stays a permanently-passing (before AND after Task 2) proof, by design.** It is testing a capability `serial_comm.py` already had (an arbitrary caller-supplied `timeout` surviving a long gap) rather than anything Task 2 adds; forcing an artificial pre-Task-2 failure here would misrepresent what the test actually verifies.
- **`w27c512` reused as the one real 27C part across both new test modules.** Already the shared "non-0x0D" fixture chip in `tests/test_write_skip_sdp_unlock.py`'s `_NON_0X0D_CHIP`; reusing it (rather than picking a second identity) keeps the module set's fixture surface smaller.
- **`_fresh_serial_and_comm()` duplicated locally in both new test modules** (not added to `tests/conftest.py`) -- the plan's `files_modified` list for this task does not include `conftest.py`, and the existing precedent (`tests/test_write_skip_sdp_unlock.py`'s own copy) already establishes local duplication over a shared fixture for this specific need.

## Plan-Internal Tension Resolved (recorded honestly, not glossed over)

Task 2's action text describes `_write_block_timeout`'s guard as: *"returns `float(budget)` when it is not `None` and at least `1`, and otherwise returns `WRITE_BLOCK_TIMEOUT_FALLBACK_S`"* -- a **lower-bound-only** test, and the acceptance criteria repeat this ("applies a `>= 1` lower bound"). The threat-model row `T-143-WEDGE` also names the mitigation as *"consumer-side `>= 1` lower bound"*.

But Task 1's Test 3 (`test_implausible_budget_is_clamped_away`) explicitly requires **both** `0` **and** `999999` to fall back to `120.0`. A lower-bound-only implementation (`budget is not None and budget >= 1`) makes `999999` pass the guard and return `999999.0`, not `120.0` -- directly contradicting Test 3's mandated acceptance behaviour, which the plan's own words describe as: *"Both must produce the `120.0` fallback... the consumer must still refuse it."*

**Resolution:** implemented `1 <= budget <= WRITE_BUDGET_MAX_S` (importing `WRITE_BUDGET_MAX_S` from `serial_comm.py`, which already defines it -- no second definition site, no drift risk). This satisfies Test 3 exactly as written, and Task 2's own overriding instruction settles which side wins: *"The implementation exists to satisfy exactly these six tests; read them before writing code."* The tests are the contract; the prose describing the guard was under-specified in three places (Task 2's action, its acceptance criteria, and the threat-model row) but the acceptance behaviour asked for (both sub-cases falling back) is unambiguous and was verified against the real, running code -- not assumed. No test value, fixture, or expected number was altered to accommodate this; the code was written to match the plan's stated test requirements.

## D-25 Evidence: RED before, GREEN after, for both new test modules

### `tests/test_write_response_budget.py` (Task 1 to Task 2)

**RED** (`pytest tests/test_write_response_budget.py -o addopts="" -v`, run against the code as committed at the end of Task 1, before any Task 2 edit):

```
tests/test_write_response_budget.py::test_write_uses_advertised_budget FAILED
tests/test_write_response_budget.py::test_absent_budget_falls_back_to_120s FAILED
tests/test_write_response_budget.py::test_implausible_budget_is_clamped_away FAILED
tests/test_write_response_budget.py::test_non_write_paths_keep_default_timeout FAILED
tests/test_write_response_budget.py::test_init_and_end_phases_keep_default_timeout FAILED
tests/test_write_response_budget.py::test_long_gap_within_budget_does_not_time_out PASSED

5 failed, 1 passed in 2.76s
```

Representative failure (`test_write_uses_advertised_budget`):
```
E       AssertionError: HOST-01/D-09: expected a MAIN-phase get_response call with timeout=250.0 (the advertised budget, used verbatim); got [None, None]
E       assert 250.0 in [None, None]
```

**Test 6 (`test_long_gap_within_budget_does_not_time_out`) PASSED at RED time, by design** -- it exercises `SerialCommunicator.get_response` directly with an explicit literal `timeout=60.0`, a call form that already worked before this plan (only the write-path's own internal *default* changes; the mechanism that lets an arbitrary caller-supplied timeout survive a long gap is untouched). Recorded here as an honest characterization rather than forced into a false RED, matching this phase's own precedent (143-02's SUMMARY records an analogous "actual result diverges from the stated prediction" finding without altering evidence to match a prediction).

**Two of the five initially-failing tests needed strengthening to be genuinely RED for the right reason**, discovered by actually running the suite rather than assuming: `test_non_write_paths_keep_default_timeout` (D-12) and `test_init_and_end_phases_keep_default_timeout` (D-13) as first drafted asserted only negative properties ("`120.0` never appears" / "INIT and END stay bare") that were **already true on the pre-Task-2 code**, since nothing was threaded anywhere yet -- both passed vacuously on the first RED run (a genuine `3 failed, 3 passed` result, captured and then corrected rather than silently reported as "RED"). Both tests were strengthened with a same-drive **contrast** assertion (proving the *shared* code path a function change would reach was actually exercised, e.g. requiring `verify_eprom`'s MAIN-phase calls to resolve to an *explicit* `DEFAULT_RESPONSE_TIMEOUT` rather than merely "bare or 10"), which made both genuinely fail pre-Task-2 and pass post-Task-2. This is a strengthening of the test, not a weakening -- the final assertions are strictly more precise than the plan's literal per-test description.

**GREEN** (`pytest tests/test_write_response_budget.py -x -o addopts="" -v`, after Task 2's production edit):

```
tests/test_write_response_budget.py::test_write_uses_advertised_budget PASSED
tests/test_write_response_budget.py::test_absent_budget_falls_back_to_120s PASSED
tests/test_write_response_budget.py::test_implausible_budget_is_clamped_away PASSED
tests/test_write_response_budget.py::test_non_write_paths_keep_default_timeout PASSED
tests/test_write_response_budget.py::test_init_and_end_phases_keep_default_timeout PASSED
tests/test_write_response_budget.py::test_long_gap_within_budget_does_not_time_out PASSED

6 passed in 4.24s
```

`test_long_gap_within_budget_does_not_time_out --durations=1`: **0.02s** (Pitfall 6 guard satisfied, far under the 2 s bar).

**A second, unrelated bug was found and fixed while confirming GREEN** (Rule 1): the call recorder in `_recording_get_response_patch` was declared as `def _recording_get_response(self, *args, **kwargs)`. Because `self` is a *named* parameter, ordinary Python argument binding consumes the first positional value into it -- so `args` inside the wrapper was **already** self-free. The first draft nonetheless assumed (from an earlier, different sandbox check of `mock.call_args`, which is a different object) that `args[0]` would be `self`, and indexed `args[1]` for the timeout -- silently reading past the real value and always landing on `None`/an `IndexError`-avoiding empty slice, which is why the very first full run showed every MAIN-phase timeout as `None` even immediately after Task 2's edit landed. Root-caused with a standalone repro script (captured, not guessed), fixed by reading `args[0]` directly and correcting the module docstring's claim about the recorded shape to match the *verified* behaviour, and confirmed by re-running the full module GREEN. This fix is bundled into Task 2's commit (`0def706`) since it corrects test-authoring code, not production behaviour, and is exactly the kind of finding this task's own "turn the module GREEN" verification step exists to catch.

### `tests/test_pulse_us_override.py` (Task 3)

**Process note (self-corrected, recorded under "Issues Encountered" below):** Part A (`write_eprom`'s `pulse_us` parameter) was accidentally implemented before this test module was authored, inverting the plan's required RED-before-GREEN order for Task 3. Caught before committing: the uncommitted Part A diff was saved (`git diff -- firestarter/eprom_operations.py > .../part-a-pulse-us.patch`), the file was reverted to its Task-2-committed state (`git checkout -- firestarter/eprom_operations.py`), the test module was authored and run against the reverted (pre-Part-A) code to capture a genuine RED, and Part A was then reapplied (`git apply .../part-a-pulse-us.patch`) and reformatted.

**RED** (`pytest tests/test_pulse_us_override.py -o addopts="" -v`, run against the code with Part A reverted):

```
tests/test_pulse_us_override.py::test_override_rides_the_db_dict FAILED
tests/test_pulse_us_override.py::test_override_does_not_mutate_the_caller_dict FAILED
tests/test_pulse_us_override.py::test_no_new_wire_field_is_added FAILED
tests/test_pulse_us_override.py::test_absent_flag_leaves_db_pulse FAILED

E           TypeError: EpromOperator.write_eprom() got an unexpected keyword argument 'pulse_us'

4 failed in 0.17s
```

Exactly the failure shape the plan predicted ("they fail with a `TypeError` on the unknown keyword before Part A lands").

**GREEN** (`pytest tests/test_pulse_us_override.py -x -o addopts="" -v`, after Part A was reapplied):

```
tests/test_pulse_us_override.py::test_override_rides_the_db_dict PASSED
tests/test_pulse_us_override.py::test_override_does_not_mutate_the_caller_dict PASSED
tests/test_pulse_us_override.py::test_no_new_wire_field_is_added PASSED
tests/test_pulse_us_override.py::test_absent_flag_leaves_db_pulse PASSED

4 passed in 2.69s
```

## Verification Results (final state)

| Check | Result |
|---|---|
| `pytest tests/test_write_response_budget.py -x -o addopts=""` | 6 passed |
| `pytest tests/test_write_response_budget.py::test_long_gap_within_budget_does_not_time_out --durations=1` | 0.02s |
| `pytest tests/test_pulse_us_override.py -x -o addopts=""` | 4 passed |
| `pytest tests/test_eprom_operations.py tests/test_write_skip_sdp_unlock.py -x -o addopts=""` | 51 passed |
| `pytest tests/ --cov=firestarter --cov-fail-under=70 -o addopts=""` | **1562 passed** (1552 + 10), coverage **82.80%** |
| `ruff check firestarter/ tests/` | All checks passed |
| `ruff format --check firestarter/ tests/` | 132 files already formatted |
| `tools/check_mypy_watermark.py` | exit 0; 33 errors, 2 below the 35 watermark (pre-existing, unmoved) |
| `git diff --exit-code -- firestarter/serial_comm.py firestarter/cli_handlers.py firestarter/constants.py firestarter/messages.py` (vs pre-plan HEAD) | clean |
| `git diff` hunks in `firestarter/eprom_operations.py` | 7 hunks, all inside the import block / constant block / `_write_block_timeout` / `_main_phase_send_data` / `write_eprom` |
| `git -C /workspaces/firestarter status --porcelain` (L-6 check, before the coverage leg) | clean -- no deselection needed |
| `grep response_timeout` inside `verify_eprom`'s body | no matches (confirmed via `awk` range extraction) |

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Test recorder mis-indexed `self` out of its own already-self-free `args`**
- **Found during:** Task 2 (confirming GREEN for `test_write_response_budget.py`)
- **Issue:** `_timeout_of` read `args[1]` on the assumption that `autospec=True` includes `self` inside the wrapper's own `*args` -- verified false by a standalone repro: a wrapper declared `def f(self, *args, **kwargs)` already has `self` consumed by its named parameter, so `args` is self-free. The bug produced `[None, None]` for every MAIN-phase call even with the correct production code in place.
- **Fix:** `_timeout_of` reads `args[0]`; the module docstring's claim was corrected to describe the verified (not assumed) shape.
- **Files modified:** `firestarter_app/tests/test_write_response_budget.py`
- **Verification:** all 6 tests pass; the standalone repro script's output is quoted in the commit's reasoning.
- **Committed in:** `0def706` (bundled with Task 2's production commit, since it corrects test-authoring code discovered while turning that same task's target module GREEN)

---

**Total deviations:** 1 auto-fixed (1 Rule-1 bug, in test code authored by this same plan).
**Impact on plan:** No production-code defect was found. The fix corrects a test-authoring error discovered during this plan's own verification step; no scope creep.

## Issues Encountered

- **Task 3 ordering slip (self-corrected, not a deviation from the plan's CONTENT, but from its stated PROCESS):** implemented `write_eprom`'s `pulse_us` parameter (Part A) before authoring `tests/test_pulse_us_override.py`, inverting the plan's required RED-before-GREEN sequence. Caught before any commit: saved the uncommitted diff, reverted the file to its Task-2-committed state, authored and ran the four tests against the reverted code to capture a genuine `TypeError` RED, then reapplied the saved diff and reformatted. No functional impact -- the final code and tests are identical to what a strictly-ordered execution would have produced -- but recorded here for honesty, since the RED transcript in this SUMMARY would otherwise misrepresent when it was actually captured relative to the implementation.
- **Plan-internal tension** between Task 2's "lower-bound-only" guard description and Task 1's Test 3's "both 0 and 999999 fall back" requirement -- resolved in favour of the tests; see "Plan-Internal Tension Resolved" above.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- HOST-01's write-path timeout threading and D-12's negative proof are complete and verified independently of firmware evidence (all software-only, per this plan's own scope).
- HOST-04 is **NOT** complete after this plan -- `requirements: []` stays empty, as instructed. `write_eprom`'s `pulse_us` transport half is done; plan 143-07 owns the `--pulse-us` CLI flag, Click's `IntRange(1, 65535)` bound (D-15), and the D-17 default-visible report line, extending `tests/test_pulse_us_override.py` with `CliRunner` cases in the same module (its docstring already states this two-plan authorship).
- `_fresh_serial_and_comm()` (both new test modules) and `_drive_write_and_record_timeouts` / `_drive_data_operation_and_record_timeouts` (`test_write_response_budget.py`) are reusable analogs for any later plan needing a hardware-free full write/verify drive with a controllable `write_block_budget_s`.
- No blockers. Ring-fence (D-13), catalog/codegen files (D-08 family: `messages.py`/`constants.py`), and `DEFAULT_RESPONSE_TIMEOUT`'s own value (D-12) are all confirmed untouched by `git diff`.
- Plan **143-10** is the one that flips the `HOST-01`/`HOST-04` checkboxes in `REQUIREMENTS.md`, after every piece of evidence (including firmware-side plans) exists -- this plan deliberately marks neither.

## Self-Check: PASSED

- FOUND: `firestarter_app/firestarter/eprom_operations.py` (modified)
- FOUND: `firestarter_app/tests/test_write_response_budget.py` (created)
- FOUND: `firestarter_app/tests/test_pulse_us_override.py` (created)
- FOUND commit `628e5ac` (Task 1)
- FOUND commit `0def706` (Task 2)
- FOUND commit `a3fc955` (Task 3)

---
*Phase: 143-host-timeout-progress-pulse-override*
*Completed: 2026-08-13*
