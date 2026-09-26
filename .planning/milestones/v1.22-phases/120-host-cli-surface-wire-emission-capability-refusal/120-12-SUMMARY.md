---
phase: 120-host-cli-surface-wire-emission-capability-refusal
plan: 12
subsystem: testing
tags: [non-regression, ci-gates, cross-repo, pytest, mypy, ruff, submit, github-issues]

# Dependency graph
requires:
  - phase: 120 (Plans 01-11)
    provides: "sdp_capability.py, dev sdp CLI, --skip-sdp-unlock, rebuilt constants parity gate, D-09..D-16 wire/CLI behaviour, the D-20 dev-test-redesign amendment"
  - phase: 119
    provides: "firmware CMD_SDP_UNLOCK/CMD_SDP_LOCK, MSG_WARN_SDP_UNLOCK_SKIPPED (0x86), the nine-row CORRECTION-4 gate table, tip 0048b3d"
provides:
  - "120-NONREGRESSION.md: the phase's closing non-regression record — nine-row gate re-run, both frozen-artifact fences, both carried-forward findings, no silicon claim"
  - "120-VALIDATION.md settled: nyquist_compliant/wave_0_complete flipped true after individually re-verifying every Wave-0 row against the real, landed test names"
  - "submit.py --submit repo-target verified (not re-fixed) with one new negative-argv test"
affects: [121-devtest-and-gates, 122-close]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Non-vacuous frozen-artifact proof: empty `git status --porcelain` over a path-scoped `git diff`, per PROJECT.md FOURTH CORRECTION item 5"
    - "Verify-don't-reimplement discharge of an operator ask that was already fixed upstream, recording the released-artifact gap explicitly rather than re-touching the source"

key-files:
  created:
    - .planning/phases/120-host-cli-surface-wire-emission-capability-refusal/120-NONREGRESSION.md
  modified:
    - .planning/phases/120-host-cli-surface-wire-emission-capability-refusal/120-VALIDATION.md
    - firestarter_app/tests/test_submit.py

key-decisions:
  - "Row 7 (test_revision_constants_parity.py) recorded as CHANGED BY DESIGN, not unchanged — 13 tests post-120-07 rebuild vs 6 pre-phase"
  - "Row 9 (check_devtest_orchestrator.py, scans cli_handlers.py) named as the one host-side row at real risk this phase and confirmed it held"
  - "--submit repo-target ask discharged as verification only: SUBMIT_REPO already henols/firestarter_prom at e615b4c/2b9e8dd; one new negative-argv test added; submit.py byte-unchanged"
  - "120-VALIDATION.md's Wave-0 rows corrected in place where the originally-authored -k substring or file path did not match the landed test (3 rows: HOST-02 D-18, HOST-04 D-04 auto-set, HOST-03 fail-closed) rather than silently left pointing at a dead command"

requirements-completed: []

coverage:
  - id: D1
    description: "All nine CORRECTION-4 cross-repo gate rows re-run at the phase's final commit, with row 7 recorded CHANGED and row 9's at-risk status resolved"
    verification:
      - kind: other
        ref: "120-NONREGRESSION.md §4 (nine-row table) — each command individually re-executed this session"
        status: pass
    human_judgment: false
  - id: D2
    description: "Both frozen-artifact fences verified non-vacuously: firmware tree byte-untouched (status --porcelain empty, tip 0048b3d), app-repo DB/catalog/build_db.py untouched"
    verification:
      - kind: other
        ref: "git -C /workspaces/firestarter status --porcelain (empty) + rev-parse --short HEAD (0048b3d); git -C /workspaces/firestarter_app diff --stat -- firestarter/data/ firestarter/messages.py tools/build_db.py tools/catalog/ (empty)"
        status: pass
    human_judgment: false
  - id: D3
    description: "--submit repo-target verified (not re-fixed): SUBMIT_REPO == henols/firestarter_prom pinned by existing + one new negative-argv test; submit.py byte-unchanged"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_submit.py#test_submit_via_gh_argv_targets_the_project_wide_tracker"
        status: pass
    human_judgment: false
  - id: D4
    description: "120-NONREGRESSION.md written covering all eight sections, quoting the Validation Ceiling verbatim, making no silicon claim"
    verification:
      - kind: other
        ref: ".planning/phases/120-host-cli-surface-wire-emission-capability-refusal/120-NONREGRESSION.md (self-check below)"
        status: pass
    human_judgment: false
  - id: D5
    description: "120-VALIDATION.md settled: nyquist_compliant/wave_0_complete true only after every Wave-0 row individually re-verified reachable"
    verification:
      - kind: other
        ref: "120-VALIDATION.md front-matter + per-row corrections"
        status: pass
    human_judgment: false

# Metrics
duration: 55min
completed: 2026-07-29
status: complete
---

# Phase 120 Plan 12: Non-Regression Capstone Summary

**Re-ran all nine CORRECTION-4 cross-repo gates plus the full host suite at the phase's final commit, verified both frozen-artifact fences non-vacuously, discharged the `dev test --submit` repo-target ask as a verification (not a re-fix), and settled `120-VALIDATION.md` after individually re-checking every Wave-0 row against the tests that actually landed.**

## Performance

- **Duration:** ~55 min
- **Completed:** 2026-07-29T13:20Z (approx)
- **Tasks:** 3
- **Files modified:** 3 (1 created, 2 modified)

## Accomplishments

- **All nine gate rows re-run from `/workspaces/firestarter_app`, verbatim, at this plan's final commit** — not trusted from any prior plan's SUMMARY. Row 5's generator (`gen_sdp_bus_config.py`) was actually executed and the firmware tree confirmed empty **afterward**, proving idempotence rather than a bare exit code. Row 7 (`test_revision_constants_parity.py`) recorded honestly as **CHANGED BY DESIGN** — 13 tests now, not the prior 6, since Plan 120-07 rebuilt it into a real two-way header-parsing gate with planted-violation and fail-closed legs. Row 9 (`check_dispatch.py` + `check_devtest_orchestrator.py`, which scans `cli_handlers.py`) is named as the one host-side row genuinely at risk this phase — Plans 120-08/09 both edited that file — and it held green.
- **Full host suite: 1050 passed, 1 failed** (the pre-existing `test_audit_coverage_matrix.py::test_golden_file_matches` stale golden, reproduced and named, not silently tolerated), coverage **82.47%** against the 70% floor. `tests/test_no_programmer_found_*` did **not** reproduce despite three live boards attached (`/dev/ttyACM0`, `/dev/ttyACM1`, `/dev/ttyUSB0`), consistent with Phase 118/119's own sweeps.
- **`python3 tools/check_mypy_watermark.py` reports error count 1** (the pre-existing `submit.py:446` assignment error), watermark 35 — the 34-slack caveat is recorded explicitly so a bare pass is never read as proof that `cli_handlers.py`/`serial_comm.py` (both edited this phase) gained no new type error.
- **Both frozen-artifact fences confirmed non-vacuously**: `git -C /workspaces/firestarter status --porcelain` empty, tip `0048b3d`, `version.h` still `3.0.0b11`; `git -C /workspaces/firestarter_app diff --stat -- firestarter/data/ firestarter/messages.py tools/build_db.py tools/catalog/` empty. PROJECT.md FOURTH CORRECTION item 5's vacuous-path warning is restated in `120-NONREGRESSION.md` §3, with the empty `status --porcelain` as the proof that cannot pass vacuously.
- **`--submit` repo-target verified, not re-fixed**: `submit.SUBMIT_REPO == "henols/firestarter_prom"` confirmed by direct import; the fix is present at commit `e615b4c` on this branch and `2b9e8dd` on `beta` (both confirmed via `git branch --contains`); `firestarter/submit.py` is byte-unchanged by this plan. One new test, `test_submit_via_gh_argv_targets_the_project_wide_tracker`, pins the create-path argv carrying `--repo henols/firestarter_prom` immediately adjacent, never `henols/firestarter_app`, with no `shell=True` escape hatch — the load-bearing negative leg, since `gh issue create --label` aborts before creating unless the label pre-exists **and** the caller has write access, which community testers generally have neither of. **The released-artifact caveat is recorded**: shipped `3.0.0b11` still misfiles because the `v1.21` tag predates the fix; the fix reaches users only at the next beta cut.
- **Both carried-forward findings recorded in `120-NONREGRESSION.md`, neither fixed** (out of this plan's file scope, as instructed): (1) the double-swallowed `MSG_ERR_UNKNOWN_CMD` — an `EpromOperationError` carrying that code cannot propagate from wire to CLI in production, swallowed once in `_probe_port`'s `expect_ack()` and again in `_run_state_machine`'s except clause, leaving D-14's CLI mapping unit-proven only via a mocked operator; (2) the pre-existing stale `test_audit_coverage_matrix` golden, reproduced this run and named with its cause (186034 vs 184631 bytes, first diff at index 1178).
- **`120-VALIDATION.md` settled**: `status: complete`, `nyquist_compliant: true`, `wave_0_complete: true` — flipped only after individually re-verifying every originally-`❌ W0` row exists on disk and is reachable by a real, passing pytest invocation. Three rows needed their file/command reference corrected in place rather than silently left pointing at a dead `-k` substring or wrong file: HOST-02's D-18 non-`0x0D` warn-and-proceed test and HOST-04's D-04 auto-set test both actually landed in `tests/test_write_skip_sdp_unlock.py` (not `tests/test_dev_sdp_cmd.py` as originally authored), and HOST-03's fail-closed test's actual name (`test_gate_fails_closed_on_an_unreadable_header_path`) is matched by `-k fails_closed`, not the literal `fail_closed` substring originally written. The Planted-Violation Fixtures table was also corrected: Plan 120-07 shipped three separate fixture headers (`planted_constants_value_drift.h`, `planted_constants_fw_missing.h`, `planted_constants_host_missing.h`), not one combined `planted_constants_drift.h`.
- **Zero requirement rows changed.** All six HOST-01..HOST-06 re-verified `[x]` Complete with their existing traceability rows; `DEVTEST-01..06` re-verified `[ ]` Pending. Nothing newly ticked by this plan.

## Task Commits

Each task was committed atomically:

1. **Task 2: Verify — not change — dev test --submit's repo target and argv assertion idiom** - `96e0622` (test, in `firestarter_app` submodule) — added `test_submit_via_gh_argv_targets_the_project_wide_tracker`.
2. **Task 1 + Task 3: Re-run the nine-row gate table, write 120-NONREGRESSION.md, settle 120-VALIDATION.md** - `1979bca` (docs, in the meta repo) — Task 1 produced no code change (pure gate re-run + raw-notes capture), so its results are recorded directly in the Task 3 commit alongside the new NONREGRESSION artifact and the VALIDATION.md edits.

**Plan metadata:** committed separately via the meta-repo's final docs commit (this SUMMARY.md, STATE.md, ROADMAP.md).

_Note: Task order in commits differs slightly from the plan's numbering because Task 1 produced no file changes of its own (a pure verification task) — its output feeds directly into Task 3's commit, per the plan's own instruction to "capture all of it as raw notes for Task 3; do not write 120-NONREGRESSION.md yet."_

## Files Created/Modified

- `.planning/phases/120-host-cli-surface-wire-emission-capability-refusal/120-NONREGRESSION.md` - new; the phase's closing non-regression record, eight sections mirroring `119-NONREGRESSION.md`'s shape
- `.planning/phases/120-host-cli-surface-wire-emission-capability-refusal/120-VALIDATION.md` - settled: front-matter flags flipped, Wave-0 checkboxes ticked, per-row corrections recorded, Validation Sign-Off completed, Approval line filled
- `firestarter_app/tests/test_submit.py` - one new test, `test_submit_via_gh_argv_targets_the_project_wide_tracker` (Idiom B negative-argv leg for the repo target)

## Decisions Made

- **Row 7 recorded as CHANGED, not unchanged** — the plan's prohibitions explicitly forbid the "unchanged" verdict here since Plan 120-07 deliberately rebuilt the gate; the new shape (two-way header-parsing gate, 4 planted-violation legs, 1 fail-closed leg, `COMMAND_NAMES`-coverage leg) is described in full in `120-NONREGRESSION.md` §4.
- **`--submit` discharged as verification only** — re-touching `firestarter/submit.py` would have re-opened a claim that is already true (the fix landed at `e615b4c`) and risked masking the actual, honest finding that the released `3.0.0b11` artifact still misfiles until the next beta cut. The one code change made is a test addition, not a production change.
- **Wave-0 row corrections applied in place, not silently accepted** — three of `120-VALIDATION.md`'s originally-`❌ W0` rows named a file or `-k` substring that does not literally match what the executing plans (120-08, 120-09, 120-10) actually built. Rather than flip `wave_0_complete: true` while those rows still point at commands that would collect zero tests, each was corrected to the real file and test name, verified to pass, and only then ticked.

## Deviations from Plan

None - plan executed exactly as written. No Rule 1/2/3 auto-fixes were needed: every gate row passed on first run, both frozen-artifact fences were already clean, and `submit.py`'s fix was already correctly in place from a prior quick-task commit (`e615b4c`).

## Issues Encountered

None beyond the two carried-forward findings this plan was instructed to record (not fix) — see the Accomplishments section above and `120-NONREGRESSION.md` §2 (double-swallowed `MSG_ERR_UNKNOWN_CMD`) and §5 (stale audit-matrix golden). Both are explicitly out of this plan's file scope per the plan's own prohibitions.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Phase 120 (HOST-01 through HOST-06) is fully verified non-regressed at its final commit. The nine-row CORRECTION-4 gate table, the frozen-artifact fence proof, and the known-and-explained-conditions register are all handed forward to Phase 121 and Phase 122, exactly as Phase 119 handed them to Phase 120.
- Phase 121 inherits: the `dev test` redesign implementation (DEVTEST-02..06, per Plan 120-11's amendment), GATE-01's AST capability gate over `sdp_capability.py`, GATE-02's `doc/lockable-proms.md` §17 correction, and the nine residual-risk watch-list entries in `120-WATCHLIST.md`.
- Firmware repo remains byte-untouched at tip `0048b3d`, `version.h` still `3.0.0b11` — reconfirmed one more time by this plan, the last phase-120 plan to touch the tree state at all.
- The double-swallowed `MSG_ERR_UNKNOWN_CMD` propagation path (carried forward from 120-10) remains an open, named, actionable follow-up for a future phase — not blocking, not silent.

## Self-Check: PASSED

- FOUND: .planning/phases/120-host-cli-surface-wire-emission-capability-refusal/120-NONREGRESSION.md
- FOUND: .planning/phases/120-host-cli-surface-wire-emission-capability-refusal/120-VALIDATION.md
- FOUND: firestarter_app/tests/test_submit.py
- FOUND commit 96e0622 (firestarter_app)
- FOUND commit 1979bca (meta repo)

---
*Phase: 120-host-cli-surface-wire-emission-capability-refusal*
*Completed: 2026-07-29*
