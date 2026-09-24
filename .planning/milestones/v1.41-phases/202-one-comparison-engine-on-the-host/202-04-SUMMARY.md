---
phase: 202-one-comparison-engine-on-the-host
plan: 04
subsystem: verification
tags: [python, streaming-compare, eprom, read-abort, wire-protocol]

# Dependency graph
requires:
  - phase: 202-01
    provides: "`verify_eprom` rewritten onto `COMMAND_READ`, driving `_main_phase_read_data` with a D-04 pull callback and the accumulator; the D-10 exit-code contract (0/1/2) this plan's discrimination extends"
  - phase: 202-03
    provides: "`CompareAccumulator.finalise()` always populating `CompareResult.fingerprint`/`render_compare_lines`'s D-14 bucket line, which this plan's abort makes honest on a truncated prefix (D-09)"
provides:
  - "`_main_phase_read_data` gains an additive `abort_predicate: Callable[[], bool] | None = None` keyword -- the read loop stops acking (never raises, keeps draining) once it fires, so the state machine's error-path teardown still runs; the four pre-existing callers are byte-for-byte unchanged"
  - "`verify_eprom`'s default (non-`--full`) path passes `accumulator.has_mismatch` as that predicate, breaking the read at the first mismatching byte instead of draining the rest of the chip (CMP-04, D-06)"
  - "D-08's four-condition abort-vs-fault discrimination (intent flag, recorded stop timestamp, exact `MSG_ERR_TIMEOUT` id, bounded 3.0s window) in `verify_eprom`, plus `READ_ABORT_ACCEPTANCE_WINDOW_S` and `EpromOperator._read_abort_stopped_at`/`_read_abort_intended`"
  - "A zero-length-region false-clean-pass fix: `verify_eprom` now requires `result.total > 0` before ever returning a match (CMP-04 'empty')"
  - "`.planning/phases/202-one-comparison-engine-on-the-host/202-READ-ABORT-ANSWER.md` -- the written, affirmative answer to phase success criterion 5, with the ROADMAP's 'Known open mechanic' paragraph corrected to point at it"
affects: [202-05, 204, 206]

# Actuals (#2632)
actuals:
  tokens: 11600
  tasks: 3
  commits: 8
  plan_head_before: "app 6eed1ed / meta d788d505 (dual-repo plan; see Task Commits for the per-repo ledger)"

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Additive-keyword seam over honouring a callback's return value: `abort_predicate` is a new defaulted parameter rather than reinterpreting `process_data_chunk_callback`'s return, because all four existing callbacks return `None` (falsy) and a truthiness test would have silently broken every one of them."
    - "Drain-don't-raise on abort: the read loop keeps consuming responses after the predicate fires (never raises, never breaks) so the terminating MAIN/ERROR frame is still read and the state machine's own teardown (or the firmware's error-path `command_done()`) still runs -- raising out of the callback would leave unread bytes on the port."
    - "Wire-identical-fault discrimination via a bounded, four-condition acceptance window (intent flag + recorded timestamp + exact error-id match + elapsed-time bound) rather than trusting either side of the ambiguity alone."

key-files:
  created:
    - .planning/phases/202-one-comparison-engine-on-the-host/202-READ-ABORT-ANSWER.md
  modified:
    - firestarter_app/firestarter/eprom_operations.py
    - firestarter_app/tests/test_eprom_operations.py
    - .planning/ROADMAP.md
    - .planning/REQUIREMENTS.md

key-decisions:
  - "abort_predicate is a defaulted keyword, not a reinterpreted callback return value -- RESEARCH.md's own recommendation, confirmed: honouring `is False` would still have worked, but the defaulted keyword leaves the callback contract completely untouched and matches read_eprom's own additive-default precedent."
  - "On abort, the loop drains to the terminating frame instead of raising -- raising would unwind without consuming the firmware's ERROR frame, leaving bytes on the port; draining is what lets the error-path teardown (command_done(), per D-06/D-07) still run."
  - "A mismatch in the final chunk is a COMPLETE compare, not an abort, with no special-case code: the chunk callback always runs before the predicate is checked, so `compared` naturally equals `total` when MAIN arrives right after the last chunk."
  - "Progress bar on an abort simply stops advancing at the compared count and is closed there by _run_state_machine's existing `finally` -- never advanced to the region total, matching D-09's 'a truncated sample must not read as complete' principle. CONTEXT.md left this to discretion."
  - "Zero-length region fix scoped as `result.total > 0` alongside the existing 'compared == total' guard, not a separate D-17-style CLI refusal -- that full region-validation refusal is 202-05's job; this plan only had to stop an empty region from silently returning a clean pass."

requirements-completed: [CMP-04]

coverage:
  - id: D1
    description: "_main_phase_read_data gains an additive abort_predicate keyword; the four pre-existing callers (read_eprom, both consistency_check_eprom drives, the hexdump drive) are unchanged"
    requirement: "CMP-04"
    verification:
      - kind: unit
        ref: "tests/test_eprom_operations.py, tests/test_consistency_check.py (full modules, 62 passed) -- pre-existing tests exercising all non-abort callers unchanged"
        status: pass
      - kind: other
        ref: "inspect.signature(EpromOperator._main_phase_read_data).parameters['abort_predicate'].default is None"
        status: pass
    human_judgment: false
  - id: D2
    description: "Default-mode verify stops acking after the mismatching chunk (proven by absent ack writes, not by the verdict), the chunk callback fires exactly twice, and a second operation on the same operator succeeds afterward (port left clean)"
    requirement: "CMP-04"
    verification:
      - kind: unit
        ref: "tests/test_eprom_operations.py#TestVerifyEpromReadAbort::test_default_abort_stops_acking_after_the_mismatching_chunk"
        status: pass
    human_judgment: false
  - id: D3
    description: "D-08 discrimination: a non-timeout error id, a timeout on the --full path (no abort requested), and a timeout outside the acceptance window all take the exit-2 fault path despite superficially resembling an abort"
    verification:
      - kind: unit
        ref: "tests/test_eprom_operations.py#TestVerifyEpromReadAbort::test_non_timeout_error_after_intended_abort_returns_two"
        status: pass
      - kind: unit
        ref: "tests/test_eprom_operations.py#TestVerifyEpromReadAbort::test_timeout_on_full_path_with_no_abort_requested_returns_two"
        status: pass
      - kind: unit
        ref: "tests/test_eprom_operations.py#TestVerifyEpromReadAbort::test_timeout_outside_the_acceptance_window_returns_two"
        status: pass
    human_judgment: false
  - id: D4
    description: "CMP-04 edges: first-byte and last-byte mismatch (both a range, both exit 1; last-byte completes without aborting), 16 consecutive differences as one range, a zero-length region never a clean pass, two mismatches in one chunk resolving to the lower address, and exact-int precision on an aborted run's counts"
    requirement: "CMP-04"
    verification:
      - kind: unit
        ref: "tests/test_eprom_operations.py#TestVerifyEpromReadAbort (test_first_byte_mismatch_..., test_last_byte_mismatch_..., test_sixteen_consecutive_differences_..., test_zero_length_region_..., test_two_mismatches_in_one_chunk_..., test_aborted_run_counts_are_exact_integers_...)"
        status: pass
    human_judgment: false
  - id: D5
    description: "Phase success criterion 5 is answered in writing at 202-READ-ABORT-ANSWER.md, stating the saving is temporal not merely diagnostic, and the ROADMAP paragraph that assumed otherwise points at it"
    verification:
      - kind: other
        ref: "test -s .planning/phases/202-one-comparison-engine-on-the-host/202-READ-ABORT-ANSWER.md && grep -q temporal ... && grep -q 202-READ-ABORT-ANSWER.md .planning/ROADMAP.md"
        status: pass
    human_judgment: false

duration: ~95min
completed: 2026-09-20
status: complete
---

# Phase 202 Plan 04: Break the Read in Flight, Honestly Summary

**`verify_eprom`'s default path now stops the programmer at the first mismatching byte via an additive `abort_predicate` seam in `_main_phase_read_data`, discriminates the deliberate stop from a genuine timeout with four required conditions, and phase success criterion 5 is answered in writing with the ROADMAP's wrong premise corrected.**

## Performance

- **Duration:** ~95 min
- **Completed:** 2026-09-20
- **Tasks:** 3 (all `type="auto"`)
- **Files modified:** 4 (2 in `firestarter_app`, 2 in the meta repo `.planning/`), plus 1 new file (the answer doc); across 3 app commits + 5 meta commits (4 for this plan's own artifacts, 1 already covered by the per-task gitlink advances)

## Accomplishments

- `_main_phase_read_data` gained a defaulted `abort_predicate: Callable[[], bool] | None = None` keyword. Once it fires, the loop stops acking but keeps draining responses (never raises, never breaks) until the terminating `MAIN` or `ERROR` frame arrives -- the four pre-existing callers (`read_eprom`, both `consistency_check_eprom` drives, the hexdump drive) are byte-for-byte unchanged.
- `verify_eprom`'s default (non-`--full`) path passes `accumulator.has_mismatch` as that predicate: the host now stops the programmer sending more bytes the instant the first mismatch is fed, instead of draining the rest of the chip. `--full` passes no predicate and always reads (and reports) the whole region.
- D-08's abort-vs-fault discrimination: an error is accepted as this host's own deliberate stop only when all four hold -- the default path actually requested a stop, the read loop actually recorded one, the firmware's own error id is exactly `MSG_ERR_TIMEOUT`, and the elapsed time since the stop is within a derived 3.0-second window (`READ_ABORT_ACCEPTANCE_WINDOW_S`). Any single condition failing takes the pre-existing exit-2 fault path.
- Found and fixed a genuine bug named by this plan's own `must_haves.truths` (CMP-04 "empty"): a zero-length region's `compared` trivially equals `total` at 0, so the existing "incomplete compare never matches" guard didn't catch it and `verify_eprom` reported a false clean pass for an empty input file.
- `TestVerifyEpromReadAbort` (10 new tests) proves the abort by absent ack writes and chunk-callback call counts (never by the verdict alone), the three D-08 negatives, and all five CMP-04 edges (boundary, adjacency, empty, ordering, precision).
- `.planning/phases/202-one-comparison-engine-on-the-host/202-READ-ABORT-ANSWER.md` answers phase success criterion 5 affirmatively: the saving is temporal, not merely diagnostic, because the firmware's `command_done()` teardown runs on the error path the abort produces too. The ROADMAP's "Known open mechanic" paragraph is corrected to point at it instead of asserting the old (wrong) premise that the END phase itself had to run.

## Task Commits

1. **Task 1: An additive abort seam in the read loop** -- app `8d90e5c`, meta `838b166d`
2. **Task 2: Break the read at the first mismatch, and never mistake it for a fault** -- app `9e5481b`, meta `d40bac75`
3. **Task 3: Prove the stop, cover the mismatch boundaries, and write the answer down** -- app `b210dea` (tests + the zero-length fix), meta `87b97b2c` (gitlink advance) + `abb80ecf` (answer file + ROADMAP amendment)

**Plan metadata:** *(this commit, immediately following)*

## Files Created/Modified

- `firestarter_app/firestarter/eprom_operations.py` -- `abort_predicate` seam in `_main_phase_read_data`; `READ_ABORT_ACCEPTANCE_WINDOW_S`; `EpromOperator._read_abort_stopped_at`/`_read_abort_intended`; `verify_eprom` wired to abort and discriminate; zero-length-region fix
- `firestarter_app/tests/test_eprom_operations.py` -- `TestVerifyEpromReadAbort` (10 tests): abort proof, 3 D-08 negatives, 6 CMP-04 edge tests
- `.planning/phases/202-one-comparison-engine-on-the-host/202-READ-ABORT-ANSWER.md` -- the written answer to phase success criterion 5 (new)
- `.planning/ROADMAP.md` -- "Known open mechanic" paragraph corrected; 202-04-PLAN.md checkbox flipped
- `.planning/REQUIREMENTS.md` -- CMP-04 marked Complete (checklist + traceability table)

## Decisions Made

See `key-decisions` in frontmatter. In short: an additive keyword over a reinterpreted callback return; drain-don't-raise on abort so the terminating frame is still consumed; the final-chunk mismatch case needs no special code because feeding the callback always precedes the predicate check; the progress bar simply stops advancing on abort; the zero-length fix is scoped narrowly (`total > 0`) rather than a full D-17 refusal.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] `has_mismatch` is a property, not a method**

- **Found during:** Task 2 implementation, first test run.
- **Issue:** `abort_kwargs["abort_predicate"] = accumulator.has_mismatch` passed the property's current *value* (a `bool`), not a callable -- `_main_phase_read_data` immediately raised `TypeError: 'bool' object is not callable` the moment it tried to invoke the predicate.
- **Fix:** Wrapped it in a lambda: `lambda: accumulator.has_mismatch`.
- **Files modified:** `firestarter_app/firestarter/eprom_operations.py`.
- **Verification:** `TestVerifyEpromHostSideRead` (pre-existing, 4 tests) passed cleanly afterward; caught and fixed before any commit landed.
- **Committed in:** `9e5481b` (no broken intermediate state was ever committed).

**2. [Rule 1/2 - Bug / Missing Critical] Zero-length region reported a false clean pass (CMP-04 "empty")**

- **Found during:** Task 3, while designing the CMP-04 "empty" edge test this plan's own `must_haves.truths` names explicitly.
- **Issue:** `verify_eprom`'s existing "incomplete compare never matches" guard (`result.bad == 0 and result.compared == result.total`) is vacuously true when the region is 0 bytes long (`compared` trivially equals `total` at 0) -- an empty input file's `verify` therefore returned 0 (a clean pass) despite comparing nothing.
- **Fix:** Added `result.total > 0` to the guard, so a zero-length region can never report a match.
- **Files modified:** `firestarter_app/firestarter/eprom_operations.py` -- **outside Task 3's declared `<files>` list** (which named only the test file, the answer doc, and the ROADMAP). Fixing it here is justified because this exact behavior is one of this plan's own `must_haves.truths` (not an out-of-scope discovery); the file-list omission reads as an authoring oversight rather than a deliberate scope boundary.
- **Verification:** `TestVerifyEpromReadAbort::test_zero_length_region_never_reports_a_clean_pass` (new); full targeted suite (`test_eprom_operations.py` + `test_consistency_check.py`) 63/63 passed; full suite 2190/2190 passed.
- **Committed in:** `b210dea`.

### Process notes (no code impact)

- Tasks 1 and 2 both touch `firestarter_app/firestarter/eprom_operations.py`. To avoid the exact "commit-boundary smear" 202-01's SUMMARY documented (a pathspec-form `git commit` takes a file's FULL working-tree content, not just staged hunks), each task's edits were applied, verified, and committed in isolation by reverting the file to HEAD (`git checkout --`) between tasks and reapplying only that task's edits -- rather than attempting to split one combined diff via `git add -p`.

---

**Total deviations:** 2 auto-fixed (1 Rule 1, 1 Rule 1/2) + 1 process note (no code impact).
**Impact on plan:** Both auto-fixes were necessary for correctness (one caught before any commit; the other is a genuine gap the plan's own must-have truths required closing). No scope creep beyond what CMP-04 "empty" already demanded.

## Issues Encountered

None beyond what is documented above under Deviations.

## User Setup Required

None -- no external service configuration required.

## Next Phase Readiness

- `verify`'s default path now genuinely breaks the read in flight; `--full` is unaffected (no predicate, no discrimination path exercised).
- `abort_predicate` is available on `_main_phase_read_data` for 202-05's `blank` (once it joins the engine) to reuse identically, if a future decision wants `blank` to abort too -- CONTEXT.md left that open and it was not exercised here (only `verify` was in this plan's scope).
- `READ_ABORT_ACCEPTANCE_WINDOW_S`, `_read_abort_stopped_at`, and `_read_abort_intended` are operator-level state, reset per-call/per-`_run_state_machine`-entry -- available for `blank` or any future abort-capable operation to reuse without redefining the discrimination.
- The deferred one-line firmware `DONE`-based clean stop (named in `202-READ-ABORT-ANSWER.md` and CONTEXT.md's `<deferred>` section) remains filed for phase 204, which is already dual-repo and bench-gated -- not brought forward here.
- Both `firestarter_app` and the meta repo remain on `v1.41-verification-to-host`; no stray branch. `firestarter_app` HEAD before this plan: `6eed1ed`; meta HEAD before this plan: `d788d505`.
- Full suite: 2190 tests passed (up from 2180), 189.93s, coverage 85.83% (`Required test coverage of 70% reached`), 36/36 snapshots. `ruff check`/`ruff format --check` clean over `firestarter/ tests/`. `mypy firestarter/cli_handlers.py firestarter/main.py firestarter/compare.py`: no issues. `mypy firestarter/ tests/` (full CI scope): 32 errors in 12 files, unchanged from the 202-01/202-03 baseline.
- 202-05 remains: `blank` joins the engine, `--size`/`-a` region options, exit-code closure.

---
*Phase: 202-one-comparison-engine-on-the-host*
*Completed: 2026-09-20*

## Self-Check: PASSED

- `firestarter_app/firestarter/eprom_operations.py` -- FOUND, modified (`abort_predicate` seam, discrimination, zero-length fix)
- `firestarter_app/tests/test_eprom_operations.py` -- FOUND, modified (`TestVerifyEpromReadAbort`, 10 tests)
- `.planning/phases/202-one-comparison-engine-on-the-host/202-READ-ABORT-ANSWER.md` -- FOUND (new, 135 lines, contains "temporal")
- `.planning/ROADMAP.md` -- FOUND, modified (points at the answer file; 202-04-PLAN.md checkbox flipped)
- `.planning/REQUIREMENTS.md` -- FOUND, modified (CMP-04 Complete)
- App commits `8d90e5c`, `9e5481b`, `b210dea` -- FOUND in `git -C firestarter_app log --oneline --all`
- Meta commits `838b166d`, `d40bac75`, `87b97b2c`, `abb80ecf` -- FOUND in `git log --oneline --all`
- Both repos on `v1.41-verification-to-host`, no stray branch
- `tests/test_eprom_operations.py::TestVerifyEpromReadAbort`: 10/10 passed
- `tests/test_eprom_operations.py tests/test_consistency_check.py`: 63/63 passed
- Full suite (`pytest tests/ --cov=firestarter --cov-report=term-missing --cov-fail-under=70 -q`): green, `Required test coverage of 70% reached. Total coverage: 85.83%`, 36/36 snapshots, exit 0; a second run with `-o addopts=""` (to see the count line, per the project's own doubled-`-q` quirk) reported `2190 passed in 189.93s`
- `ruff check firestarter/ tests/` and `ruff format --check firestarter/ tests/`: clean
- `mypy firestarter/cli_handlers.py firestarter/main.py firestarter/compare.py`: no issues
- `mypy firestarter/ tests/` (full CI scope): 32 errors in 12 files -- unchanged from the 202-01/202-03 baseline
