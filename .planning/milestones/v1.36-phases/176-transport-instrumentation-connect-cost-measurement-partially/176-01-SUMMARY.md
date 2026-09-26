---
phase: 176-transport-instrumentation-connect-cost-measurement-partially
plan: 01
subsystem: instrumentation
tags: [transport-health, dev-test, diagnostic-report, serial-comm, blast-radius-invariance]

requires:
  - phase: 174-blast-radius-invariance-harness
    provides: "_TRANSPORT_HEALTH_KEYS pin, the 16-shape committed report-snapshot corpus, and the FROZEN_HASHES / rekey_ledger machinery this plan must move without breaking"
provides:
  - "firestarter/transport_counters.py -- the process-lifetime, explicitly resettable counter sink, the only mutable module-level state in the package"
  - "decode_failures: a real, report-reachable counter wired end to end from _decode_id_frame's CRC-mismatch/shape-mismatch path to transport_health in the filed JSON report"
  - "_SUSPECT_SCANNED_FIELDS: a named, extensible domain for _is_transport_suspect, replacing the hard-coded four-field tuple"
  - "Phase 174 pin and all 16 committed report snapshots moved deliberately in the same commit as the production change, with a next-key guard for plan 176-02's probe_timeouts"
affects: [176-02, 176-03, 176-04, 176-05]

actuals:
  tokens: 6047
  tasks: 2
  commits: 2

tech-stack:
  added: []
  patterns:
    - "Process-lifetime module-level counter sink, reset explicitly by the caller that owns a measurement window (analog: ConfigManager's process-lifetime singleton, not its disk persistence)"
    - "Threaded-in-never-fetched: transport counts join fw_board_identity/hw_revision as values cli_handlers.py reads and assigns onto the report, never values diagnostic_report.py fetches itself"
    - "Named, extensible suspicion domain (_SUSPECT_SCANNED_FIELDS) instead of a hard-coded scanned-field tuple, so future counters opt in by joining a list, not by rewriting a rule"

key-files:
  created:
    - firestarter_app/firestarter/transport_counters.py
    - firestarter_app/tests/test_transport_counters.py
  modified:
    - firestarter_app/firestarter/serial_comm.py
    - firestarter_app/firestarter/diagnostic_report.py
    - firestarter_app/firestarter/cli_handlers.py
    - firestarter_app/tests/test_diagnostic_report.py
    - firestarter_app/tests/test_blast_radius_invariance.py
    - firestarter_app/tests/fixtures/reports/*.json (16 files, one added line each)

key-decisions:
  - "Checkpoint (gate=blocking-human) resolved by the orchestrator before this executor ran: operator answered \"as-proposed\". Verbatim transcription and the five locked names are recorded in the dedicated section below."
  - "Added a seventh test assertion (folded into Task 1's CRC-flip test rather than a separate function) proving a SUCCESSFUL decode leaves decode_failures at 0, before the corrupt-frame call proves the +1 -- the plan's six named behaviors alone do not distinguish \"increments only on failure\" from \"increments unconditionally\"; the anti-vacuity weakening w2 (unconditional increment) would not have gone red without it."
  - "No second commit was made in /workspaces for the gitlink or evidence files, contrary to this PLAN.md's own <output> instruction. The orchestrator's execution-context instructions for this run were explicit and more specific: leave the meta-repo firestarter_app gitlink alone, do not commit it, and the orchestrator commits meta-repo files (SUMMARY.md, evidence/) after the wave. Both evidence transcripts and this SUMMARY are left uncommitted in /workspaces for the orchestrator."

requirements-completed: [RPT-C1, RPT-C2]

coverage:
  - id: D1
    description: "decode_failures reports a real integer (0 when nothing failed, never NOT_MEASURED once wired) and a default-constructed TransportHealth still reports it as \"not measured\", never 0"
    requirement: "RPT-C2"
    verification:
      - kind: unit
        ref: "tests/test_transport_counters.py#test_snapshot_after_reset_returns_wired_keys_sorted_zeroed"
        status: pass
      - kind: unit
        ref: "tests/test_transport_counters.py#test_default_transport_health_decode_failures_not_measured"
        status: pass
      - kind: unit
        ref: "tests/test_transport_counters.py#test_to_dict_decode_failures_reflects_assigned_integer"
        status: pass
    human_judgment: false
  - id: D2
    description: "snapshot() returns a fresh dict, keys in fixed sorted order, deterministic across calls"
    requirement: "RPT-C1"
    verification:
      - kind: unit
        ref: "tests/test_transport_counters.py#test_snapshot_after_reset_returns_wired_keys_sorted_zeroed"
        status: pass
      - kind: unit
        ref: "tests/test_transport_counters.py#test_snapshot_returns_a_fresh_copy"
        status: pass
    human_judgment: false
  - id: D3
    description: "One triggered decode failure raises decode_failures by exactly one and leaves every other key in snapshot() unchanged, both via direct _decode_id_frame call and via the _read_and_parse_lines generator's silent drop path"
    requirement: "RPT-C1"
    verification:
      - kind: unit
        ref: "tests/test_transport_counters.py#test_decode_id_frame_corrupt_crc_raises_decode_failures_by_one_and_nothing_else"
        status: pass
      - kind: unit
        ref: "tests/test_transport_counters.py#test_corrupt_frame_through_read_and_parse_lines_raises_decode_failures_by_one"
        status: pass
    human_judgment: false
  - id: D4
    description: "The counter survives teardown of the SerialCommunicator that incremented it"
    requirement: "RPT-C1"
    verification:
      - kind: unit
        ref: "tests/test_transport_counters.py#test_counter_survives_communicator_teardown"
        status: pass
    human_judgment: false
  - id: D5
    description: "The Phase 174 oracle is green before and after this plan at 114 passed, with the pin and all 16 snapshots moved deliberately in the same commit and no re-key ledger row"
    verification:
      - kind: unit
        ref: "tests/test_blast_radius_invariance.py + tests/test_rekey_ledger.py (114 passed)"
        status: pass
      - kind: other
        ref: "tools/snapshot_report_shapes.py --check (exit 0, zero drift)"
        status: pass
    human_judgment: false
  - id: D6
    description: "diagnostic_report.py still imports no transport or hardware class -- counts threaded in from cli_handlers.py"
    verification:
      - kind: unit
        ref: "tests/test_diagnostic_report.py#test_report_module_is_orchestrator_only"
        status: pass
    human_judgment: false

duration: 90min
completed: 2026-09-04
status: complete
---

# Phase 176 Plan 01: Transport instrumentation tracer -- decode_failures end to end Summary

**A single new counter, `decode_failures`, travels the whole architecture in one plan: `firestarter/transport_counters.py` (a new process-lifetime sink), an increment inside `_decode_id_frame` on a CRC-mismatch/shape-mismatch, a reset-and-read pair in `cli_handlers.py`'s `dev_test`, a new honest `int | None` field on `TransportHealth`, and the Phase 174 pin plus all 16 committed report snapshots moved deliberately in the same commit.**

## Checkpoint Resolution (Task 1: lock the five new transport-counter key names)

This checkpoint (`gate="blocking-human"`) was already put to the human operator by the orchestrator before this executor ran, per this run's `<checkpoint_already_resolved>` instructions. It is recorded here as resolved-by-orchestrator, not re-asked.

**Operator's answer, verbatim:** `as-proposed`

**The five locked names** (binding on every later task in this plan and every later plan in Phase 176):

1. `decode_failures` -- inbound id frames `codec.decode_id_frame` refused (NOT `crc_failures`)
2. `resync_length_missing` -- magic preamble seen, length bytes never arrived
3. `resync_body_truncated` -- declared frame length exceeded the bytes that arrived
4. `timeouts` -- EXISTING field, wired for the first time, scoped to `get_response` on an ESTABLISHED connection
5. `probe_timeouts` -- NEW sibling for `get_response` timeouts inside port discovery

`cobs_errors`, `crc_failures` and `retries` keep `NOT_MEASURED` with a recorded reason (MEAS-03, a later plan's deliverable).

Only name 1 (`decode_failures`) is wired by this plan (176-01). Names 2-5 are wired by later plans in this phase.

## Performance

- **Duration:** ~90 min
- **Started:** 2026-09-04T20:32:00Z (approx, precondition oracle run)
- **Completed:** 2026-09-04T21:00:45Z
- **Tasks:** 2 code tasks (Task 1 checkpoint resolved by orchestrator, no code)
- **Files modified:** 6 modified + 2 created (Task 1) + 17 modified (Task 2, 16 snapshots + 1 pin file)

## Accomplishments

- `firestarter/transport_counters.py` created: the only mutable module-level state in the package, with `record_decode_failure()`, `reset()` and `snapshot()`, zero comment lines, fully annotated but deliberately NOT added to the mypy strict island.
- `serial_comm.py`'s `_decode_id_frame` increments `decode_failures` immediately after the existing `codec.decode_id_frame` call, at the same override seam CAP-01/02/03 used; the ring-fenced `_read_and_parse_lines` body is untouched, confirmed by `test_read_and_parse_lines_ringfence_unchanged` staying green.
- `diagnostic_report.py`'s `TransportHealth` gains `decode_failures: int | None = None`; `_is_transport_suspect` now scans a named `_SUSPECT_SCANNED_FIELDS` tuple instead of a hard-coded four-field tuple, extending the suspicion domain without changing the guard clause's two conjuncts or their order.
- `cli_handlers.py`'s `dev_test` resets the sink immediately before `read_programmer_identity()` (whole-command scope, PA-1) and assigns `report.transport.decode_failures` from a post-`run_plan` snapshot.
- `tests/test_transport_counters.py` created: 9 tests covering the sink contract, the plus-one-and-nothing-else-moved leg (extended with a successful-decode-does-not-move leg), the lifetime property, and the report surface.
- Phase 174's `_TRANSPORT_HEALTH_KEYS` pin moved from five keys to six (sorted, `decode_failures` third), a next-key guard added for `probe_timeouts` (plan 176-02), and all 16 committed report snapshots regenerated via `tools/snapshot_report_shapes.py` -- exactly one added line each, zero deletions, `--check` confirms zero drift.
- Anti-vacuity transcript recorded at `evidence/176-01-anti-vacuity-red-green.txt`: three deliberate weakenings (delete the increment; make it unconditional; change the dataclass default from `None` to `0`) each SEEN red, then restored to green.

## Task Commits

Each task was committed atomically inside the `firestarter_app` submodule (on `gsd/v1.36-dev-test-fidelity`):

1. **Task 1: End to end -- one decode failure, from the byte stream to `transport_health`** - `e57262f` (feat)
2. **Task 2: Move the Phase 174 pin and re-baseline all 16 snapshots** - `e5d76b4` (test)

_The checkpoint task (lock the five key names) produced no code and no commit -- resolved by the orchestrator before this executor started, per this run's instructions._

**Plan metadata:** not committed in `/workspaces` -- see Deviations below.

## Files Created/Modified

- `firestarter_app/firestarter/transport_counters.py` - new process-lifetime counter sink
- `firestarter_app/firestarter/serial_comm.py` - `_decode_id_frame` increments `decode_failures` on decode failure
- `firestarter_app/firestarter/diagnostic_report.py` - new `decode_failures` field, `_SUSPECT_SCANNED_FIELDS`, corrected docstring
- `firestarter_app/firestarter/cli_handlers.py` - resets the sink before the identity read, assigns the snapshot onto the report
- `firestarter_app/tests/test_transport_counters.py` - new test module, 9 tests
- `firestarter_app/tests/test_diagnostic_report.py` - `test_transport_not_measured` extended with `decode_failures`
- `firestarter_app/tests/test_blast_radius_invariance.py` - `_TRANSPORT_HEALTH_KEYS` pin moved to six keys, next-key guard added
- `firestarter_app/tests/fixtures/reports/*.json` (16 files) - regenerated snapshots carrying the new `decode_failures` key

## Decisions Made

- Checkpoint answer `as-proposed` recorded verbatim (see Checkpoint Resolution section above); no rename, no `single-resync` collapse.
- Extended Task 1's CRC-flip test with a preceding successful decode call so the test proves BOTH "a successful decode does not move `decode_failures`" AND "a failing decode moves it by exactly one" -- required to make anti-vacuity weakening w2 (unconditional increment) actually go red. The plan's six named `<behavior>` items alone did not include a successful-decode leg; this is a Rule 2 (missing critical) style strengthening of the test, not a change to production code.
- Did not make the second `/workspaces` commit this PLAN.md's `<output>` section calls for (gitlink + evidence). This run's execution-context instructions explicitly override that: leave the meta-repo `firestarter_app` gitlink alone and do not commit it, and let the orchestrator commit meta-repo files (this SUMMARY, the evidence transcripts) after the wave.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Missing Critical] Strengthened Task 1's CRC-flip test to also prove a successful decode does not move the counter**
- **Found during:** Task 1, anti-vacuity weakening w2 (unconditional increment)
- **Issue:** The plan's six named `<behavior>` items test the failure path only. An unconditional-increment weakening (fires on every `_decode_id_frame` call, success or failure) would NOT be caught by any of the six tests as originally scoped, since every scenario they exercise already ends in a decode failure -- the weakening is indistinguishable from the correct implementation under those tests alone.
- **Fix:** Extended `test_decode_id_frame_corrupt_crc_raises_decode_failures_by_one_and_nothing_else` to first perform a genuinely successful `_decode_id_frame` call (valid CRC) and assert `decode_failures` stays at `0`, before performing the corrupt-CRC call and asserting the `+1`.
- **Files modified:** `firestarter_app/tests/test_transport_counters.py`
- **Verification:** Anti-vacuity transcript (`evidence/176-01-anti-vacuity-red-green.txt`) shows this exact test going red under weakening w2 (`assert unmoved["decode_failures"] == 0` fails with `1 == 0`).
- **Committed in:** `e57262f` (Task 1 commit)

**2. [Rule 4-adjacent, but decided per explicit run-level instruction, not asked] Skipped the second `/workspaces` commit this PLAN.md's own `<output>` section specifies**
- **Found during:** End of Task 2, before the output step
- **Issue:** PLAN.md's `<output>` section instructs a second plain `git commit` in `/workspaces` recording the gitlink and the `.planning` evidence. This run's own execution-context instructions (given directly to this executor, more specific than the PLAN.md text) explicitly state: leave the meta-repo `firestarter_app` gitlink alone, do not commit it; the orchestrator commits meta-repo files (SUMMARY.md, evidence) after the wave.
- **Fix:** No commit was made in `/workspaces`. The `evidence/` directory and this `176-01-SUMMARY.md` are left uncommitted for the orchestrator.
- **Files affected:** none (no commit made)
- **Verification:** `git status --short` in `/workspaces` after this plan shows the evidence files and this SUMMARY as untracked/modified, and the `firestarter_app` gitlink as the pre-existing dirty `M` it already was.
- **Committed in:** n/a -- this is the point of the deviation

---

**Total deviations:** 2 (1 auto-fixed test strengthening, 1 run-instruction-driven commit-scope adjustment).
**Impact on plan:** The test strengthening closes a real anti-vacuity gap the plan's own gate demanded be provably closed. The commit-scope adjustment changes only which repo holds which commit -- no production code or test behavior is affected, and it follows the more specific, more current instruction given directly for this execution.

## Issues Encountered

None beyond the two items above.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- `transport_counters.py` exists and is proven end to end for one counter; plans 176-02 through 176-05 add `resync_length_missing`, `resync_body_truncated`, `timeouts`, `probe_timeouts` and `measure_connect_cost` along the same proven path.
- The Phase 174 oracle is green at 114 passed, matching the precondition measured before this plan touched anything.
- The full `firestarter_app` test suite (2158 tests, 32 snapshot checks) passes; `ruff check`, `ruff format --check` and the mypy watermark (`35 (watermark: 35)`) all hold.
- No blockers for 176-02.

## Self-Check: PASSED

- `firestarter_app/firestarter/transport_counters.py` exists: confirmed.
- `firestarter_app/tests/test_transport_counters.py` exists: confirmed.
- Commit `e57262f` exists in `firestarter_app`'s `git log`: confirmed.
- Commit `e5d76b4` exists in `firestarter_app`'s `git log`: confirmed.
- `tests/test_blast_radius_invariance.py` + `tests/test_rekey_ledger.py` at 114 passed both before and after this plan: confirmed.
- `evidence/176-01-tracer-end-to-end.txt`, `evidence/176-01-oracle-rebaseline.txt` and `evidence/176-01-anti-vacuity-red-green.txt` all exist with the required markers: confirmed.

---
*Phase: 176-transport-instrumentation-connect-cost-measurement-partially*
*Completed: 2026-09-04*
