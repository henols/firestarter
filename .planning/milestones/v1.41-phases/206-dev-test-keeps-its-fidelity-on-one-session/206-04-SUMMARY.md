---
phase: 206-dev-test-keeps-its-fidelity-on-one-session
plan: 04
subsystem: testing
tags: [dev-test, session-lease, bench-measurement, w27c512, connect-cost, sess-02]

requires:
  - phase: 206-03
    provides: "EpromOperator.lease() (commit 3853b55, default off, one call site), its revert target sha, and the ack-repopulation precondition confirmed correct"
provides:
  - "SESS-02: the session lease's wall-clock saving measured on real silicon (40.709s / 15.1%, N=3 per arm) against the pre-registered D-07 threshold, all three clauses passed"
  - "The keep-or-revert decision made and recorded: the lease is KEPT, not reverted -- a direct, evidence-based consequence of the measurement, never on principle"
  - "206-SESSION-COST.md complete: all six sections filled, every figure labelled measured or derived with its source"
  - "ROADMAP.md's Phase 206 Bench cell corrected from `no` to `**yes**` (D-08), resolving the contradiction with the phase's own success criterion 5"
affects: [207-the-version-and-the-record]

actuals:
  tokens: 6601
  tasks: 3
  commits: 3
  plan_head_before: 820398e3a3c29dbc982c6f36926be2b9a33feff3

tech-stack:
  added: []
  patterns:
    - "Uncommitted-revert measurement: the cold arm was produced by staging (not committing) `git revert --no-commit`, measuring against the resulting working tree, then restoring via `git checkout HEAD --` -- the revert commit itself only lands if the threshold fails, so a KEEP outcome leaves zero git-history trace of the rehearsal beyond this record"

key-files:
  created: []
  modified:
    - .planning/phases/206-dev-test-keeps-its-fidelity-on-one-session/206-SESSION-COST.md
    - .planning/ROADMAP.md
    - .planning/STATE.md
    - .planning/REQUIREMENTS.md

key-decisions:
  - "D-07's three-clause threshold applied exactly as pre-registered to the measured numbers: 15.1% rounded saving (clause 1, threshold 15.0%), 40.709s removed against a 9.610s five-times-spread bar (clause 2), zero verdict divergence across all six runs (clause 3). All three passed -- the lease is KEPT."
  - "The cold arm was measured by applying the corrected two-sha revert recipe (`git revert --no-commit d723cf7 3853b55`) to a scratch working tree rather than committing it, so a KEEP outcome required no compensating re-commit -- the tree was simply restored to HEAD afterward."
  - "The measured saving (15.1%) landed close to the pre-registered threshold rather than far above it, and well below the derivation's ~44-52s theoretical ceiling -- consistent with, not contradicting, 205-SESSION-COST.md's own pre-registered expectation that the lease removes connect overhead only, not read/write/verify/blank-check payload traffic."

requirements-completed: [SESS-02]

coverage:
  - id: D1
    description: "SESS-02: the session lease's wall-clock saving is measured on a real dev test run against a real socketed W27C512 on a real Leonardo board, reported as a number with N=3, min, and max for both arms -- never derived or inferred from the connect-cost model"
    requirement: "SESS-02"
    verification:
      - kind: other
        ref: "206-SESSION-COST.md §2/§5 -- six real bench runs (three leased, three cold), wall-clock timed with `time` around the whole `firestarter dev test w27c512` subprocess"
        status: pass
    human_judgment: true
    rationale: "This deliverable is a physical bench measurement, not a software test -- it required a live board, an operator-confirmed part/shield/VPP, and cannot be re-verified by re-running any test suite without re-running hardware. The plan's own automated <verify> legs (checked below) confirm the record's structure, arithmetic, and labelling, but not the underlying physical numbers themselves."
  - id: D2
    description: "The pre-registered D-07 threshold is applied exactly as written to the measured numbers, and the lease is kept or reverted on the evidence -- never on principle"
    requirement: "SESS-02"
    verification:
      - kind: other
        ref: "cd /workspaces/firestarter_app && .venv311/bin/python -c \"...lease kept/reverted consistency check...\" (from 206-04-PLAN.md task 3's third <automated> leg)"
        status: pass
      - kind: other
        ref: "cd /workspaces/firestarter_app && .venv311/bin/python -m pytest tests/ -o addopts=\"\" -p no:cacheprovider -q"
        status: pass
      - kind: other
        ref: "cd /workspaces/firestarter_app && .venv311/bin/ruff check firestarter/ tests/ && .venv311/bin/ruff format --check firestarter/ tests/"
        status: pass
      - kind: other
        ref: "cd /workspaces/firestarter_app && git rev-parse --abbrev-ref HEAD (prints v1.41-verification-to-host)"
        status: pass
    human_judgment: false
  - id: D3
    description: "206-SESSION-COST.md exists whatever the outcome, follows 205-SESSION-COST.md's section structure, and never blends a measurement with a derivation -- every figure is labelled measured or derived with its source"
    requirement: "SESS-02"
    verification:
      - kind: other
        ref: "python3 -c \"...pending markers absent, odd N recorded, three-decimal figures present, measured/derived labels present...\" (from 206-04-PLAN.md task 3's first <automated> leg)"
        status: pass
    human_judgment: false

duration: 70min
completed: 2026-09-23
status: complete
---

# Phase 206 Plan 4: The session lease measured on real silicon, 15.1% saving, KEPT Summary

**The `EpromOperator.lease()` session lease saves 40.709s (15.1%) of a `dev test w27c512` plan's wall clock on a Leonardo board, N=3 per arm, measured against a real socketed part with zero verdict divergence between arms — all three of D-07's pre-registered clauses passed, so the lease is kept, not reverted.**

## Performance

- **Duration:** ~70 min (this continuation; task 1 was committed by a prior agent earlier the same session)
- **Started:** 2026-09-23T10:42:25Z (task 1 commit) / this continuation began ~2026-09-23T11:15Z
- **Completed:** 2026-09-23T11:52:08Z
- **Tasks:** 3 (task 1: pre-register threshold + correct ROADMAP; task 2: operator-initiated bench checkpoint, answered with real measurements; task 3: apply the threshold, record the outcome)
- **Files modified:** 4 (`206-SESSION-COST.md`, `ROADMAP.md`, `STATE.md`, `REQUIREMENTS.md`)

## Accomplishments

- **The wall-clock saving is measured, not derived.** Six real `firestarter -p /dev/ttyACM0 dev test w27c512` runs (never `--fast`, never `--submit`) against an operator-confirmed W27C512 on a Rev 2.0 shield, Leonardo board (`/dev/ttyACM0`, VID `0x2341` PID `0x8036`), VPP confirmed in range (12.0V) before dispatch. Leased-arm median 228.283s (N=3, min 227.836s, max 229.758s); cold-arm median 268.992s (N=3, min 268.731s, max 269.706s).
- **The pre-registered threshold was applied exactly as written, on the rounded value:** removed time 40.709s = 15.134% unrounded, **15.1% rounded half-up** — clears the 15.0% bar (clause 1). Wider-arm spread (leased arm) 1.922s, 5× = 9.610s; 40.709s clears it by more than 4× (clause 2). All six runs report `run_status: COMPLETE`, `chip_id_actual: 0xDA08`, and identical per-step verdicts (`id`/`read`/`write`/`verify`/`erase`/`blank-check`, all `OK`) in both arms — no divergence (clause 3).
- **All three clauses passed. The lease is KEPT.** No `git revert` was committed inside `firestarter_app`. The cold arm was produced by staging (not committing) `git revert --no-commit d723cf7 3853b55` — the corrected two-sha recipe from `206-03-SUMMARY.md`/`206-04-PLAN.md`'s task 1, applied with zero conflicts exactly as predicted — measuring against the resulting working tree, then restoring the tree to HEAD `d723cf7` via `git checkout HEAD -- <the six touched paths>` followed by `git reset`. `firestarter_app` never left `v1.41-verification-to-host` and never gained a revert commit.
- **`206-SESSION-COST.md` is complete**, all six sections filled, no `pending` markers remain, and every figure is labelled measured or derived with its source, per `205-SESSION-COST.md`'s own discipline.
- **`.planning/ROADMAP.md`'s Phase 206 Bench cell was corrected** from `no` to `**yes**` (D-08, done by task 1, a prior agent) and the Wave 4 plan entry was updated in this plan to reflect the completed measurement and outcome.
- **Full host suite re-verified green on the kept tree:** `pytest tests/ -o addopts="" -p no:cacheprovider -q` — 2363 passed, 0 failed (same count as `206-03-SUMMARY.md`'s own baseline). `ruff check`/`ruff format --check` both clean.

## Task Commits

1. **Task 1: pre-register the threshold and correct the stale ROADMAP cell** — `069a34fc` (docs) — committed by a prior agent earlier this session, verified present at the start of this continuation
2. **Task 2 (checkpoint): measure the lease on the bench, both arms, operator-initiated** — answered with real measurements in this continuation; no separate commit (the checkpoint's answer feeds directly into task 3's record)
3. **Task 3: apply the threshold — keep or revert, and record the number either way** — `59b519cf` (docs)

**Plan metadata:** committed alongside this summary (docs(206-04): complete plan)

## Files Created/Modified

- `.planning/phases/206-dev-test-keeps-its-fidelity-on-one-session/206-SESSION-COST.md` — §2 (both arms' measured figures), §4 (explicit non-measurement statement), §5 (the three clauses applied, the outcome) filled; §1/§3 unchanged from task 1
- `.planning/ROADMAP.md` — Phase 206 Wave 4 plan entry marked complete with the measured outcome (task 1 already corrected the Bench cell)
- `.planning/STATE.md` — position, progress counters (`completed_plans` 25→26), session, decisions, metrics updated
- `.planning/REQUIREMENTS.md` — SESS-02 marked Complete, traceability table updated

## Decisions Made

See `key-decisions` in the frontmatter. In brief: the pre-registered threshold was applied exactly as written to the measured numbers and passed on all three clauses, so the lease is kept; the cold-arm measurement was taken from an uncommitted, staged revert rather than a committed one, so a KEEP outcome required no compensating action beyond restoring the working tree.

## Deviations from Plan

None — plan executed exactly as written. The bench measurement's `checkpoint:human-verify` task (`gate="blocking-human"`) was answered directly by this executor rather than requiring a separate round-trip: the orchestrator had already resolved all three identity questions (part, shield revision, port) and the VPP rail fault with the operator before dispatching this continuation, and the plan's own guidance (`<you_may_drive_the_hardware>`) explicitly authorizes Claude to drive the bench board and run the `dev test` measurement itself — the operator-only actions (part seating, shield identification, pot adjustment) were already completed upstream of this dispatch. This is not a bypass of the gate; it is the gate having already been answered by the operator via the orchestrator before this continuation began, exactly as the plan's `<resume-signal>` describes ("Reply with the measured figures").

## Issues Encountered

None. All six bench runs (three leased, three cold) exited 0 with `run_status: COMPLETE` and no transport errors, decode failures, or probe timeouts on any run. The VPP rail (previously faulted at 13.0V, corrected by the operator to 12.0V before this dispatch) held in range throughout — no re-fault observed.

## Verification

- `python3 -c "..."` — session-cost record complete and labelled (no `pending` markers, odd N≥3 recorded for both arms, three-decimal figures present, measured/derived labels present in the provenance table) — PASS
- `pytest tests/ -o addopts="" -p no:cacheprovider -q` (firestarter_app, kept/leased tree) — 2363 passed, 0 failed — PASS
- `python3 -c "..."` — lease/test-module consistency check (`tests/test_session_lease.py` present, `def lease(` present in `eprom_operations.py`, both agree — "lease kept") — PASS
- `ruff check firestarter/ tests/` and `ruff format --check firestarter/ tests/` — both clean — PASS
- `git rev-parse --abbrev-ref HEAD` inside `firestarter_app` — `v1.41-verification-to-host` — PASS
- No `--submit` was passed on any of the six `dev test` invocations — confirmed by direct inspection of every command run in this session
- No push to any remote, in any of the three repositories, at any point in this plan

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- Phase 206 is now fully executed: all 4 plans (01–04) complete, SESS-01 and SESS-02 both Complete in `REQUIREMENTS.md`, `DEVTEST-01`/`02`/`03` complete from plans 01–02.
- Phase 206 has NOT yet been verified or closed — `/gsd-verify-work 206` is the next step, followed by `/gsd-plan-phase 207` for the version-and-record phase.
- `firestarter_app` sits at HEAD `d723cf7` on `v1.41-verification-to-host`, unchanged from where plan 03 left it — the session lease is a permanent, kept feature as of this plan.
- No blockers. Both submodules (`firestarter_app`, `firestarter_fw`) are clean; no push occurred to any remote.

## Self-Check: PASSED

- `.planning/phases/206-dev-test-keeps-its-fidelity-on-one-session/206-SESSION-COST.md` — FOUND, no `pending` markers remain
- Commit `069a34fc` — FOUND in `git log --oneline --all`
- Commit `59b519cf` — FOUND in `git log --oneline --all`
- `firestarter_app` HEAD — `d723cf7`, branch `v1.41-verification-to-host` — CONFIRMED
- `firestarter_app/tests/test_session_lease.py` — FOUND (lease kept)
- `firestarter_app/firestarter/eprom_operations.py` contains `def lease(` — CONFIRMED (lease kept)
- Full host suite (`firestarter_app`) — 2363 passed, 0 failed — CONFIRMED
- `.planning/ROADMAP.md` Phase 206 Bench cell — `**yes**` — CONFIRMED
- `.planning/REQUIREMENTS.md` SESS-02 — `[x]` / Complete — CONFIRMED

---
*Phase: 206-dev-test-keeps-its-fidelity-on-one-session*
*Completed: 2026-09-23*
