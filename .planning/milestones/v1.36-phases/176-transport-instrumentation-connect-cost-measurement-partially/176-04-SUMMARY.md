---
phase: 176-transport-instrumentation-connect-cost-measurement-partially
plan: 04
subsystem: instrumentation
tags: [connect-cost, measurement-harness, dev-fault-inject, transport-health, seal, click-cli]

requires:
  - phase: 176-transport-instrumentation-connect-cost-measurement-partially
    provides: "plans 176-01 through 176-03's nine-key transport_health pin and all four RPT-C1 sites wired end to end, including probe_timeouts"
provides:
  - "EpromOperator.measure_connect_cost / _summarize_connect_samples / _write_connect_cost_log -- the MEAS-01 bench harness, built and unit-tested with zero board access"
  - "dev fault-inject --mode connect-cost (plus a --samples option, default 10) dispatching to the harness -- no new dev subcommand registered, channel.py byte-unchanged"
  - "The MEAS-01 numeric contract settled and tested: three-decimal seconds, statistics.median_low (lower-median on ties, never an interpolated average), no mean anywhere, a separately reported 2.500s structural floor and remainder, and an honest `unmeasured` on zero samples"
  - "COVERAGE.md's reasoned no-external-API declaration for the whole phase"
  - "The software half of the phase sealed by measurement: 2198 passed (up from 2190 at wave 3 close, above the 2151 baseline), ruff clean, mypy watermark unmoved at 35, zero comment lines in every file this phase created, Phase 174 oracle at 114 passed, firmware repo and chip_database.json byte-unchanged"
  - "RPT-C1, RPT-C2, MEAS-02 and MEAS-03 recorded Complete in REQUIREMENTS.md; MEAS-01 left visibly Pending"
affects: [176-05]

actuals:
  tokens: 4600
  tasks: 3
  commits: 1

tech-stack:
  added: []
  patterns:
    - "Pin ONE port explicitly (`restrict_to_port=True` passed to `find_and_connect`, overriding the config's transient-port inference) rather than trusting default discovery -- the same inflation trap `measure_command_nak_latency`'s own docstring already documents about `fault_inject_cycle`"
    - "Aggregation kept pure and separate from the I/O harness: `_summarize_connect_samples` takes no clock reading and does no file I/O, so the entire numeric contract (rounding, tie-break, no-mean, empty-list honesty) is unit-tested with hand-built sample lists and zero board access"
    - "Structural floor reported as its own artifact line (`CONNECT_COST_STRUCTURAL_FLOOR_S = CONNECTION_STABILIZE_DELAY + 0.5`) alongside a `remainder` (median minus floor), so a reader sees whether the floor dominates rather than inferring it"
    - "A third `--mode` value on an existing Click option, not a new `dev` subcommand -- keeps `channel.BETA_ONLY_DEV_COMMANDS` and its pinning test untouched, matching the precedent `--mode latency` already set"

key-files:
  created:
    - firestarter_app/tests/test_connect_cost_harness.py
    - .planning/phases/176-transport-instrumentation-connect-cost-measurement-partially/COVERAGE.md
    - .planning/phases/176-transport-instrumentation-connect-cost-measurement-partially/evidence/176-04-harness-contract.txt
    - .planning/phases/176-transport-instrumentation-connect-cost-measurement-partially/evidence/176-04-anti-vacuity-red-green.txt
    - .planning/phases/176-transport-instrumentation-connect-cost-measurement-partially/evidence/176-04-phase-seal.txt
  modified:
    - firestarter_app/firestarter/eprom_operations.py
    - firestarter_app/firestarter/cli_handlers.py
    - .planning/REQUIREMENTS.md

key-decisions:
  - "Used `SerialCommunicator.find_and_connect(fw_cmd, self.config, preferred_port=port, restrict_to_port=True)` rather than the plain `SerialCommunicator(port=port)` constructor `measure_command_nak_latency` uses -- the plan's own action text names `find_and_connect` explicitly, and `restrict_to_port=True` closes the exact inflation gap that method's docstring warns about, regardless of the config's ambient transient-port state."
  - "`{'state': COMMAND_FW_VERSION}` reused as the lightweight setup/handshake command for `find_and_connect`, matching the one other caller that connects without a chip operation (`FirmwareManager.check_current_firmware`)."
  - "`_summarize_connect_samples` reports `samples` as a bare count (int-valued string, not a duration), while every other field is a three-decimal duration string or the literal `unmeasured` -- keeps the count field from ever being mistaken for a measured figure."
  - "Removed an early draft's explanatory `#`-comment block above the new module constants in favor of bare names plus docstring coverage on the two methods that use them, per this project's zero-comments-I-write rule."

requirements-completed: [RPT-C1, RPT-C2, MEAS-02, MEAS-03]

coverage:
  - id: D1
    description: "The connect-cost harness (measure_connect_cost, _summarize_connect_samples, _write_connect_cost_log) exists, its numeric contract is settled, and it is fully unit-tested with zero board access"
    requirement: "MEAS-01"
    verification:
      - kind: unit
        ref: "tests/test_connect_cost_harness.py::TestSummarizeConnectSamples (4 tests: odd/even/empty/structural-floor)"
        status: pass
      - kind: unit
        ref: "tests/test_connect_cost_harness.py::TestMeasureConnectCostRefusesWithoutAPort::test_no_port_returns_false_and_opens_nothing"
        status: pass
      - kind: other
        ref: "evidence/176-04-harness-contract.txt (odd/even/empty aggregation values, structural_floor=2.500s, has_mean=False)"
        status: pass
    human_judgment: false
  - id: D2
    description: "dev fault-inject --mode connect-cost dispatches to the harness and exits 0/1 on its boolean; no new dev subcommand registered, channel.py byte-unchanged, BETA_ONLY_DEV_COMMANDS still 7 entries"
    requirement: "RPT-C1, RPT-C2"
    verification:
      - kind: unit
        ref: "tests/test_connect_cost_harness.py::TestDevFaultInjectConnectCostDispatch (pass/fail exit codes)"
        status: pass
      - kind: unit
        ref: "tests/test_connect_cost_harness.py::TestNoNewDevSubcommandRegistered::test_beta_only_dev_commands_tuple_is_byte_identical_to_its_pin"
        status: pass
      - kind: other
        ref: "evidence/176-04-harness-contract.txt (gated_count=7, gated=<pinned tuple>); git diff --quiet -- firestarter/channel.py"
        status: pass
    human_judgment: false
  - id: D3
    description: "Anti-vacuity: four independent weakenings (median_low->median, 3->2 decimals, empty-path fabricates 0.000s, an added mean figure) each SEEN red, then restored to a clean, all-green working tree"
    verification:
      - kind: other
        ref: "evidence/176-04-anti-vacuity-red-green.txt (rc_w1..rc_w4=1, rc_clean=0, 4 distinct '_ failed' blocks, final 8 passed)"
        status: pass
    human_judgment: false
  - id: D4
    description: "The software half of the phase sealed by measurement: full suite 2198 passed (up from 2190, above the 2151 baseline), ruff clean, mypy watermark unmoved at 35, zero comment lines in every file this phase created, Phase 174 oracle at 114 passed with the re-key ledger and 16 snapshots byte-unchanged, HYG-04's devtest-orchestrator checker green with nothing new to register, firmware repo and generated chip database byte-unchanged"
    verification:
      - kind: unit
        ref: "pytest tests/ (2198 passed, 32 snapshots passed, 319.72s)"
        status: pass
      - kind: unit
        ref: "tests/test_blast_radius_invariance.py + tests/test_rekey_ledger.py (114 passed)"
        status: pass
      - kind: other
        ref: "evidence/176-04-phase-seal.txt (firmware_diff=clean, chip_database_diff=clean, comments_*=0 x3, rc_ruff=0, rc_ruff_format=0, rc_watermark=0, mypy errors: 35 (watermark: 35), rc_snapcheck=0, rc_oracle=0, rc_ledger_bytes=0, rc_devtest_orch=0, PASS: scanned ..., full_suite_passed=2198)"
        status: pass
    human_judgment: false
  - id: D5
    description: "REQUIREMENTS.md: RPT-C1, RPT-C2, MEAS-02 and MEAS-03 ticked and Complete in the status table; MEAS-01 explicitly left unticked and Pending; STATE.md untouched; the diff is a scoped edit (well under 12 lines), not a regeneration"
    verification:
      - kind: other
        ref: "grep assertions on .planning/REQUIREMENTS.md checkboxes and status-table rows; git diff --numstat (4 changed lines); git diff --quiet -- .planning/STATE.md"
        status: pass
    human_judgment: false

duration: 35min
completed: 2026-09-04
status: complete
---

# Phase 176 Plan 04: The MEAS-01 connect-cost harness, built and sealed with no board attached Summary

**`EpromOperator.measure_connect_cost` now exists as a pinned-port, three-decimal, no-mean-ever timing harness reachable from `dev fault-inject --mode connect-cost`, unit-tested end to end without a board, and the whole software half of Phase 176 is sealed at 2198 passed with RPT-C1, RPT-C2, MEAS-02 and MEAS-03 recorded Complete -- MEAS-01 itself stays visibly Pending until 176-05's bench run.**

## Performance

- **Duration:** ~35 min (includes a ~5.3 min full-suite run)
- **Started:** 2026-09-04T22:23:00Z (approx, immediately after 176-03 closed)
- **Completed:** 2026-09-04T22:58:00Z (approx)
- **Tasks:** 3
- **Files modified:** 2 production files + 1 new test file + 1 requirements doc + 1 new phase-scoped COVERAGE.md + 3 evidence files

## Accomplishments

- `EpromOperator` gained `_summarize_connect_samples` (pure staticmethod: three-decimal min/median/max/structural_floor/remainder, `statistics.median_low` never `statistics.median`, no mean, an honest `unmeasured` on an empty list), `measure_connect_cost` (the bench harness: resolves one pinned port, refuses without opening anything if none resolves, runs N `find_and_connect(..., restrict_to_port=True)` / `disconnect()` cycles timed with `time.monotonic()`, resets and snapshots `transport_counters` around the run), and `_write_connect_cost_log` (the artifact writer, following `_write_nak_latency_log`'s shape).
- `dev fault-inject` gained a third `--mode` value, `connect-cost`, and a `--samples` integer option (default 10) -- dispatching to `measure_connect_cost` and exiting `0`/`1` on its boolean, exactly like the existing `--mode latency` branch. No new `dev` subcommand was registered; `firestarter/channel.py` and `BETA_ONLY_DEV_COMMANDS` (still 7 entries) are byte-unchanged.
- `tests/test_connect_cost_harness.py` (new): the aggregation contract on hand-built sample lists (odd count, even count with the lower-median tie-break, empty list, structural floor + remainder), the no-port refusal (asserting `find_and_connect` is never called), the CLI dispatch pass/fail exit codes through a mocked operator, and the `BETA_ONLY_DEV_COMMANDS` pin -- 8 tests, zero comment lines, all green.
- Anti-vacuity: four weakenings applied to a scratch copy and restored in place -- (w1) `median_low` swapped for `median` broke the even-count test; (w2) three decimals dropped to two broke both the odd-count and even-count assertions; (w3) the empty-path fabricated `0.000s` instead of `unmeasured`, breaking the honesty test; (w4) an added `mean` key broke the no-mean assertion. All four SEEN red in `evidence/176-04-anti-vacuity-red-green.txt`, then the file was restored byte-identical to its post-Task-1 state (`diff -q` confirmed) before the transcript's final green run.
- `COVERAGE.md` written for the whole phase: the reasoned no-external-API declaration, covering all four plans' surface (local serial port only, stdlib-only dependencies, no package installs, no auth surface).
- The software half sealed by measurement: whole app suite `2198 passed` (up from 2190 at wave 3 close, well above the 2151 pre-phase baseline), 32 snapshot checks passed; `ruff check` and `ruff format --check` both clean; mypy watermark unmoved at `35 (watermark: 35)`; the comment census at `0` for every file this phase created; the Phase 174 oracle at `114 passed` with `snapshot_report_shapes.py --check` clean and the re-key ledger byte-unchanged; `tools/check_devtest_orchestrator.py` green with nothing new to register (this phase added no `dev_test` helper); the firmware repository and `firestarter/data/chip_database.json` both byte-unchanged, confirming the host-only scope boundary held.
- `REQUIREMENTS.md`: RPT-C1, RPT-C2, MEAS-02 and MEAS-03 ticked and set to `Complete` in the per-requirement status table, by hand, a 4-line scoped edit. MEAS-01 is deliberately left unticked and `Pending` -- its harness exists and is tested, but no board has been attached, so the measurement it names has not been taken. `STATE.md` was not touched by this task.

## Task Commits

Committed atomically inside the `firestarter_app` submodule (on `gsd/v1.36-dev-test-fidelity`):

1. **Task 1: The connect-cost harness and its `dev fault-inject --mode connect-cost` entry point** - `df2978e` (feat)

Task 2 (seal by measurement) produced no app-repo commit -- it wrote `COVERAGE.md` (a meta-repo file, left uncommitted per this run's execution context) and ran every gate, recording numbers into `evidence/176-04-phase-seal.txt` rather than changing production code. Task 3 (mark requirements) edited `.planning/REQUIREMENTS.md` only, also left uncommitted per this run's execution context -- the orchestrator commits meta-repo files after the wave.

**Plan metadata:** not committed in `/workspaces` -- see Deviations below (this run's execution-context instructions override the plan's own `<output>` section, which called for a second `/workspaces` commit).

## Files Created/Modified

- `firestarter_app/firestarter/eprom_operations.py` - `measure_connect_cost`, `_summarize_connect_samples`, `_write_connect_cost_log`, `CONNECT_COST_STRUCTURAL_FLOOR_S`
- `firestarter_app/firestarter/cli_handlers.py` - `dev fault-inject --mode connect-cost` dispatch branch, `--samples` option, extended docstring/help text
- `firestarter_app/tests/test_connect_cost_harness.py` - the 8-test aggregation/refusal/dispatch/pin suite (new)
- `.planning/phases/176-transport-instrumentation-connect-cost-measurement-partially/COVERAGE.md` - the phase-wide reasoned no-external-API declaration (new)
- `.planning/REQUIREMENTS.md` - RPT-C1/RPT-C2/MEAS-02/MEAS-03 marked Complete; MEAS-01 left Pending
- `.planning/phases/176-transport-instrumentation-connect-cost-measurement-partially/evidence/176-04-harness-contract.txt` - Task 1's first verify block transcript (new)
- `.planning/phases/176-transport-instrumentation-connect-cost-measurement-partially/evidence/176-04-anti-vacuity-red-green.txt` - the 4-weakening red/green transcript (new)
- `.planning/phases/176-transport-instrumentation-connect-cost-measurement-partially/evidence/176-04-phase-seal.txt` - Task 2's seal-by-measurement transcript (new)

## Decisions Made

- `find_and_connect(..., restrict_to_port=True)` chosen over the plain `SerialCommunicator(port=port)` constructor `measure_command_nak_latency` uses, per the plan's own action text and to close the port-discovery inflation gap explicitly rather than relying on the config's ambient transient-port state.
- `{'state': COMMAND_FW_VERSION}` reused as the lightweight connect-time command, matching `FirmwareManager.check_current_firmware`'s existing no-chip-needed pattern.
- `samples` reported as a bare count string (not a duration), keeping it visually distinct from the five duration fields.
- Removed an early draft's explanatory comment block above the new module constants (a rule violation caught during self-review) in favor of docstring coverage only, per this project's zero-comments-I-write rule.

## Deviations from Plan

None in the Rule 1-4 sense -- plan executed exactly as written for all three tasks and every `<acceptance_criteria>` passed on first attempt.

**[Execution-context override] Second `/workspaces` commit not made**
- **Found during:** reading this run's execution-context instructions before Task 1
- **Issue:** `176-04-PLAN.md`'s own `<output>` section calls for a second plain `git commit` in `/workspaces` carrying the gitlink, `REQUIREMENTS.md`, `COVERAGE.md` and the evidence.
- **Fix:** Per this run's explicit override ("Write `176-04-SUMMARY.md`, `COVERAGE.md`, `REQUIREMENTS.md` and evidence left UNCOMMITTED in `/workspaces` -- the orchestrator commits meta-repo files after the wave"), all of these are left uncommitted. The `firestarter_app` gitlink is also left dirty, as instructed. This is the same override 176-03 applied.
- **Files affected:** `176-04-SUMMARY.md`, `COVERAGE.md`, `.planning/REQUIREMENTS.md`, all three `evidence/176-04-*.txt` files.
- **Verification:** `git status --short` at `/workspaces` shows exactly the gitlink diff plus these untracked/modified meta files; no other drift.
- **Committed in:** N/A (deliberately left uncommitted per this run's instructions)

---

**Total deviations:** 1 (execution-context override, not a plan deviation in the Rule 1-4 sense). **Impact on plan:** None on production behavior; purely a commit-boundary instruction from this run's dispatch context.

## Issues Encountered

An initial draft of the two new module-level constants (`_CONSUME_REMAINING_INPUT_WINDOW_S`, `CONNECT_COST_STRUCTURAL_FLOOR_S`) carried a multi-line `#`-comment explaining the structural-floor rationale. Caught during self-review against this project's hard zero-comments-I-write rule before any commit was made; replaced with bare constant declarations, with the same rationale already carried in full by the docstrings on `_summarize_connect_samples` and `measure_connect_cost`. No functional impact; the fix landed inside Task 1's single commit.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- The MEAS-01 instrument is built, reachable from the CLI, and fully proven by unit test with no board attached. Plan `176-05` has nothing left to do but attach two boards (Uno-class, Leonardo-class) and run `dev fault-inject <chip> --mode connect-cost` against each, then record the per-board-class figures and mark MEAS-01 Complete.
- The software half of the phase is sealed by measured numbers: 2198 passed, ruff clean, mypy watermark at 35, zero new comment lines anywhere in this phase, Phase 174 oracle at 114 passed, firmware and chip database untouched.
- RPT-C1, RPT-C2, MEAS-02 and MEAS-03 are Complete. MEAS-01 is visibly and correctly still Pending -- the one requirement 176-05 exists to close.
- No blockers for 176-05.

## Self-Check: PASSED

- `firestarter_app/firestarter/eprom_operations.py` contains `def measure_connect_cost`, `def _summarize_connect_samples`, `def _write_connect_cost_log`: confirmed.
- `firestarter_app/firestarter/cli_handlers.py` contains `connect-cost` and a `samples` option: confirmed.
- `firestarter_app/tests/test_connect_cost_harness.py` exists, 8 tests, all pass, zero comment lines: confirmed.
- Commit `df2978e` exists in `firestarter_app`'s `git log`: confirmed.
- `firestarter/channel.py` byte-unchanged, `BETA_ONLY_DEV_COMMANDS` still 7 entries: confirmed.
- Full `firestarter_app` suite at 2198 passed, 32 snapshots passed, exit code 0: confirmed.
- `ruff check`, `ruff format --check`, mypy watermark (`35 (watermark: 35)`): confirmed.
- Phase 174 oracle (`test_blast_radius_invariance.py` + `test_rekey_ledger.py`) at 114 passed, re-key ledger byte-unchanged, `snapshot_report_shapes.py --check` clean: confirmed.
- `tools/check_devtest_orchestrator.py` exits 0 with a `PASS: scanned ` line: confirmed.
- Firmware repository (`git -C firestarter status --porcelain`) and `firestarter/data/chip_database.json` both byte-unchanged: confirmed.
- `evidence/176-04-harness-contract.txt`, `evidence/176-04-anti-vacuity-red-green.txt` (4x `rc_wN=1`, `rc_clean=0`, >=4 failed blocks) and `evidence/176-04-phase-seal.txt` all exist with every required marker: confirmed.
- `.planning/REQUIREMENTS.md`: RPT-C1/RPT-C2/MEAS-02/MEAS-03 ticked and `Complete`; MEAS-01 unticked and `Pending`; diff is 4 changed lines; `.planning/STATE.md` untouched: confirmed.
- `firestarter_app` working tree matches the single Task 1 commit exactly (`diff -q` against the pre-anti-vacuity snapshot): confirmed.

---
*Phase: 176-transport-instrumentation-connect-cost-measurement-partially*
*Completed: 2026-09-04*
