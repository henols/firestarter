---
phase: 176-transport-instrumentation-connect-cost-measurement-partially
plan: 05
subsystem: instrumentation
tags: [connect-cost, bench-measurement, meas-01, uno, leonardo, transport-health]

requires:
  - phase: 176-transport-instrumentation-connect-cost-measurement-partially
    provides: "plan 176-04's measure_connect_cost harness and dev fault-inject --mode connect-cost entry point, built and unit-tested with no board attached"
provides:
  - "176-MEASUREMENT.md -- the one bench-measured number this milestone required, recorded as two never-blended per-board-class sections (Uno-class 512B, Leonardo-class 1024B) with full provenance"
  - "The DTR/optiboot and native-USB-CDC mechanisms tested as hypotheses -- the data does NOT support the Uno-dominant-remainder hypothesis MEAS-01's own wording anticipated"
  - "MEAS-01 marked Complete in REQUIREMENTS.md"
  - "dev-test-sequence-cost-model.md's stale 'does not establish' bullets replaced with a citation to the measurement"
  - "probe_timeouts recorded at 0 on both bench runs -- corroborating, not contradicting, MEAS-02's threshold-5 argument"
affects: [180]

actuals:
  tokens: 3700
  tasks: 2
  commits: 2

tech-stack:
  added: []
  patterns:
    - "firmware_max_chunk is transient per-instance SerialCommunicator state discarded on disconnect -- the harness's own log never carries it, so it was read via a supplementary single connect per port using the identical find_and_connect(..., restrict_to_port=True) call, not folded into either board's timed samples"
    - "Port identity re-verified independently two ways before driving further: the fw command's controller: field, and the firmware_max_chunk value itself (512 vs 1024), which happen to double as a second class check"

key-files:
  created:
    - .planning/phases/176-transport-instrumentation-connect-cost-measurement-partially/176-MEASUREMENT.md
  modified:
    - .planning/notes/dev-test-sequence-cost-model.md
    - .planning/REQUIREMENTS.md

key-decisions:
  - "Reported the data honestly even though it contradicts MEAS-01's own stated hypothesis: Uno-class remainder (0.018s) measured SMALLER than Leonardo-class remainder (0.107s), the opposite of 'On Uno-class boards the DTR auto-reset and bootloader wait are likely the dominant term.' Recorded as an observation with no invented causal explanation, per the plan's explicit instruction that a contradicting measurement is new information, not a failure."
  - "No follow-up filed against MEAS-02's _SUSPECT_THRESHOLD=5 argument: both runs measured probe_timeouts=0, which is the expected result of a single pinned port (restrict_to_port=True gives probe_scope() nothing to walk past), not a contradiction of the multi-candidate-port inflation argument the threshold was justified against."
  - "Declined both boards' offered firmware update to 3.0.0b25 (staying on 3.0.0b22) per the orchestrator's instruction, keeping the two board classes on the same build for a fair comparison."

requirements-completed: [MEAS-01]

coverage:
  - id: D1
    description: "176-MEASUREMENT.md exists with two never-blended per-board-class sections (Uno 512B, Leonardo 1024B), each carrying its own sample count/min/median/max/structural-floor/remainder/probe_timeouts, full command-verified provenance, and the DTR/USB mechanisms recorded as tested hypotheses rather than findings"
    requirement: "MEAS-01"
    verification:
      - kind: other
        ref: "shell grep assertions from 176-05-PLAN.md's first <verify> block (never the chip, never blended, >=2 controller:, 512, 1024, uno, leonardo, probe_timeouts, 2.500s, socket, empty, hypothes, PRUNE-08, R4-01, >=7 top-level sections, >=6 three-decimal durations) -- all PASS, transcript in this run"
        status: pass
      - kind: other
        ref: "python3 structural-check script from 176-05-PLAN.md's second <verify> block (uno_section_found, leonardo_section_found, sections_are_separate, mentions_mean=False, app_head_recorded) -- all PASS, transcript in this run"
        status: pass
    human_judgment: false
  - id: D2
    description: "dev-test-sequence-cost-model.md cites 176-MEASUREMENT.md and no longer lists per-connect cost or the Uno-class rate as unestablished (erase-scaling bullet untouched); MEAS-01 ticked and Complete in REQUIREMENTS.md; STATE.md untouched; full app suite still green with both repos byte-unchanged"
    requirement: "MEAS-01"
    verification:
      - kind: other
        ref: "shell grep/git-diff assertions from 176-05-PLAN.md Task 2's first <verify> block (176-MEASUREMENT cited, both superseded bullets gone, erase bullet kept, MEAS-01 checkbox+status, note diff <=8 added lines, STATE.md clean) -- all PASS"
        status: pass
      - kind: unit
        ref: "firestarter_app pytest tests/ -o addopts=\"\" -q -- 2198 passed, 32 snapshots passed, 347.10s, exit 0"
        status: pass
      - kind: other
        ref: "git status --porcelain on firestarter_app/firestarter/ and the firmware submodule -- both clean"
        status: pass
    human_judgment: false

duration: 22min
completed: 2026-09-04
status: complete
---

# Phase 176 Plan 05: Bench-measured per-connect cost, Uno-class and Leonardo-class, never blended Summary

**Measured `EpromOperator.measure_connect_cost` on two real attached boards -- Uno-class median 2.518s (0.018s over the 2.500s floor) and Leonardo-class median 2.607s (0.107s over the same floor) -- recorded in `176-MEASUREMENT.md` as two never-blended sections, contradicting MEAS-01's own stated Uno-dominant-remainder hypothesis, with MEAS-01 now Complete.**

## Performance

- **Duration:** 22 min
- **Started:** 2026-09-04T22:53:00Z (approx)
- **Completed:** 2026-09-04T23:15:00Z (approx)
- **Tasks:** 2 (plus the already-resolved checkpoint)
- **Files modified:** 1 created, 2 modified

## Accomplishments
- Re-verified port identity by command myself before driving either board: `fw` on `/dev/ttyACM0` reported `controller: leonardo` (3.0.0b22), `/dev/ttyACM1` reported `controller: uno` (3.0.0b22) -- matching the orchestrator's pre-checked mapping exactly. Both boards offered an update to `3.0.0b25`; both declined, staying comparable at `3.0.0b22`.
- Ran `dev fault-inject sst27sf512 --mode connect-cost --samples 10` pinned to each port. Uno-class (`/dev/ttyACM1`): 10/10 samples collected, min 2.517s / median 2.518s / max 2.519s, remainder 0.018s, `probe_timeouts: 0`. Leonardo-class (`/dev/ttyACM0`): 10/10 samples collected, min 2.606s / median 2.607s / max 2.676s, remainder 0.107s, `probe_timeouts: 0`.
- Independently confirmed `firmware_max_chunk` from a supplementary connect per port (the harness's own log doesn't carry this transient field): 512 for the Uno-class port, 1024 for the Leonardo-class port -- a second, code-level confirmation of the board-class mapping.
- Wrote `176-MEASUREMENT.md` (328 lines, 8 top-level sections) following the Phase 118 shape: what was measured and what it is not, provenance, raw logs, the numbers (two never-blended per-class subsections), socket state, validation ceiling (hypotheses tested), downstream consumers, disposition.
- Recorded honestly that the data does NOT support MEAS-01's own stated hypothesis that the Uno-class DTR/bootloader wait is the dominant term -- the Uno-class remainder measured smaller than the Leonardo-class remainder, the opposite direction. No causal mechanism is claimed as confirmed; only the wall-clock observation is reported.
- Closed `dev-test-sequence-cost-model.md`'s stale "does not establish" claims for per-connect cost in seconds and the Uno-class rate, citing `176-MEASUREMENT.md`; the still-true erase-scaling and write-rate bullets were left untouched (4-line scoped diff).
- Marked MEAS-01 ticked and `Complete` in `.planning/REQUIREMENTS.md` (2-line scoped diff). `STATE.md` was not touched.
- Re-ran the full `firestarter_app` suite after the bench run: 2198 passed, 32 snapshots passed, 347.10s, exit 0 -- unchanged from the 176-04 baseline. `firestarter_app/firestarter/` and the firmware repository both confirmed byte-unchanged (`git status --porcelain` clean on both), proving the bench run measured and did not modify.

## Task Commits

Committed in `/workspaces` (this plan touches only `.planning` files):

1. **Task 1: Measure per-connect cost on each board class and write `176-MEASUREMENT.md`** - `e328d515` (docs)
2. **Task 2: Close the cost model's stated gap and mark MEAS-01 Complete** - `bc442230` (docs)

No `git commit` was run in `firestarter_app` or `firestarter` -- this plan changed no app or firmware code, and both working trees stayed clean throughout.

## Files Created/Modified
- `.planning/phases/176-transport-instrumentation-connect-cost-measurement-partially/176-MEASUREMENT.md` - the two-board-class bench measurement, provenance, and hypothesis-vs-data record (new)
- `.planning/notes/dev-test-sequence-cost-model.md` - "does not establish" list closed for per-connect cost and Uno-class rate, citing the new measurement
- `.planning/REQUIREMENTS.md` - MEAS-01 ticked and `Complete`

## Decisions Made
- Reported the Uno-vs-Leonardo remainder contradiction plainly rather than reconciling it with the stated hypothesis -- the plan's own honesty rule treats a contradicting measurement as new information, not a plan failure.
- Left MEAS-02's `_SUSPECT_THRESHOLD = 5` untouched: both runs' `probe_timeouts: 0` is the expected result of a single pinned port, not evidence against the multi-candidate-port inflation argument that threshold was justified on. No follow-up filed.
- Declined the firmware update offered on both boards, keeping both at `3.0.0b22` for a fair cross-class comparison, per the orchestrator's explicit instruction.

## Deviations from Plan

None in the Rule 1-4 sense -- plan executed exactly as written for both tasks, and every `<acceptance_criteria>` and `<verify>` block passed on first attempt. One addition, not a deviation: the plan's action text asked for `firmware_max_chunk` to be "read from the run rather than assumed," but `measure_connect_cost`'s own log doesn't carry that field (it lives on the transient `SerialCommunicator` instance, discarded before the log is written). Rather than assume 512/1024 from board-class name alone, a supplementary single connect per port was run using the identical `find_and_connect(..., restrict_to_port=True)` call, and its `firmware_max_chunk` was transcribed into the provenance section -- satisfying the "read from the run" requirement literally rather than by inference from the `controller:` name.

---

**Total deviations:** 0. **Impact on plan:** None -- the supplementary connect above is an execution detail in service of an explicit plan requirement, not a change in scope.

## Issues Encountered

None. Both boards answered every command on the first attempt; no auth gate, no port shuffle between the pre-checkpoint verification and the timed runs, no firmware update was accepted.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- MEAS-01 is Complete -- the milestone's one genuinely unmeasured number now exists, per board class, with full provenance.
- PRUNE-08 (Phase 180) and the R4-01 deferral both have a real number to weigh (0.018s and 0.107s remainders, both small relative to the unchanged 2.5s structural floor) but neither is acted on here, per this plan's explicit scope boundary.
- RPT-C1, RPT-C2, MEAS-01, MEAS-02 and MEAS-03 are all Complete -- Phase 176 has no open requirement left.
- No blockers for Phase 177.

## Self-Check: PASSED

- `.planning/phases/176-transport-instrumentation-connect-cost-measurement-partially/176-MEASUREMENT.md` exists, 328 lines, 8 top-level sections: confirmed (`wc -l`, `grep -cE '^## '`).
- All 21 assertions in the plan's first `<verify>` block (never the chip, never blended, `controller:` x4, `512`, `1024`, `uno`, `leonardo`, `probe_timeouts`, `2.500s`, `socket`, `empty`, `hypothes`, `PRUNE-08`, `R4-01`, 8 sections, 54 three-decimal durations) PASS: confirmed.
- The python3 structural-check script (`uno_section_found=True`, `leonardo_section_found=True`, `sections_are_separate=True`, `mentions_mean=False`, `app_head_recorded=True`) PASS: confirmed.
- `dev-test-sequence-cost-model.md` cites `176-MEASUREMENT`, both superseded bullets gone, erase-scaling bullet kept, diff is 4 added / 2 removed lines: confirmed.
- `.planning/REQUIREMENTS.md`: MEAS-01 `- [x]` and `| MEAS-01 | Phase 176 | Complete |`, diff is 2 added / 2 removed lines: confirmed.
- `.planning/STATE.md` diff is empty: confirmed (`git diff --quiet`).
- Commits `e328d515` and `bc442230` exist in `git log --oneline` on this branch: confirmed.
- Full `firestarter_app` suite: `2198 passed, 1 warning in 347.10s`, exit code 0: confirmed.
- `git -C firestarter_app status --porcelain firestarter/` and `git -C firestarter status --porcelain` both empty: confirmed.

---
*Phase: 176-transport-instrumentation-connect-cost-measurement-partially*
*Completed: 2026-09-04*
