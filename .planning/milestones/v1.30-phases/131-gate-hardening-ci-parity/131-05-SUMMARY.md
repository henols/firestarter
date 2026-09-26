---
phase: 131-gate-hardening-ci-parity
plan: 05
subsystem: testing
tags: [ci, github-actions, mypy, watermark-gate, gh-cli]

# Dependency graph
requires:
  - phase: 131-gate-hardening-ci-parity (131-01)
    provides: fork-base identification (beta @ 16a313a), the F-01..F-06 corrections table this plan extends
provides:
  - "131-HANDOFF.md — operator dispatch procedure for ci.yml on the fork base (Task 1, prior session)"
  - "131-CI-BASELINE.md — real, current, fork-base CI mypy error count (69), read verbatim from run 30822281624"
  - "Correction F-07 — the (checked K source files) clause is structurally absent from CI at the fork base"
affects: [132-mypy-error-reduction-and-watermark, 137-phase-137-ledger]

# Tech tracking
tech-stack:
  added: []
  patterns: ["gh run view --json for fail-closed precondition checks", "verbatim-quote CI log lines rather than recompute locally"]

key-files:
  created:
    - .planning/phases/131-gate-hardening-ci-parity/131-CI-BASELINE.md
  modified:
    - .planning/phases/131-gate-hardening-ci-parity/131-01-PLAN.md
    - .planning/phases/131-gate-hardening-ci-parity/131-05-PLAN.md

key-decisions:
  - "Amended the plan's own unreachable acceptance criterion (Found N errors in M files (checked K source files)) rather than fabricating a matching line; filed as correction F-07 in the phase's F-NN series"
  - "F-07 added to 131-01-PLAN.md's corrections table (the canonical location F-01..F-06 already live in) so 131-07 and Phase 137's ledger pick it up alongside the other six"
  - "131-05-PLAN.md task 3's automated <verify> grep changed from the unreachable checked-clause pattern to the literal mypy errors: N (watermark: M) pattern the real CI log satisfies"
  - "Measured count (69) agrees exactly with research's 69 — no divergence to record"

patterns-established:
  - "When a plan's acceptance criterion cannot be satisfied by any real, honest input, amend the criterion and file it as a numbered correction rather than fabricating matching output"

requirements-completed: []  # GATE-07 delivered here but tick deferred to 131-07 by design (this plan may mark nothing Complete)

coverage:
  - id: D1
    description: "Real ci.yml dispatch on the fork base (beta @ 16a313a) recorded with run id, URL, event, branch, head SHA, and terminal conclusion"
    requirement: "GATE-07"
    verification:
      - kind: other
        ref: "gh run view 30822281624 --repo henols/firestarter_app --json event,headBranch,headSha,conclusion,url,createdAt (read-only, re-verified independently of orchestrator-supplied values)"
        status: pass
    human_judgment: false
  - id: D2
    description: "Fail-closed precondition (numeric id, resolves, workflow_dispatch, beta, head SHA 16a313a, not the prior run 30708836339, terminal conclusion) checked before any file was written"
    requirement: "GATE-07"
    verification:
      - kind: other
        ref: "gh run view 30822281624 --repo henols/firestarter_app --json ... (all six conditions verified pass, recorded in 131-CI-BASELINE.md section 2)"
        status: pass
    human_judgment: false
  - id: D3
    description: "Verbatim mypy gate-step output (mypy errors: 69 (watermark: 35) / FAIL: ... / exit code 1), mypy version 2.3.0, Python version 3.11.15, all read from the CI log, none computed locally"
    requirement: "GATE-07"
    verification:
      - kind: other
        ref: "gh run view 30822281624 --repo henols/firestarter_app --log, grepped for the mypy step, Install step, and Set up Python step"
        status: pass
    human_judgment: false
  - id: D4
    description: "Correction F-07: the (checked K source files) clause is unreachable in CI output at the fork base — verified structurally via git show 16a313a:tools/check_mypy_watermark.py and zero checked occurrences across the full run log; filed in 131-01-PLAN.md's F-NN table, and 131-05-PLAN.md's task 3 automated block amended accordingly rather than fabricated around"
    verification:
      - kind: other
        ref: "grep -ci checked over full run log (0/635 lines); git show 16a313a:tools/check_mypy_watermark.py showing the regex only captures the error count and main() never prints raw mypy stdout"
        status: pass
    human_judgment: false

duration: unknown (continuation agent; Task 1 was authored in a prior session, Task 2 was operator-executed outside this agent's control, Task 3 completed in this session in well under 10 minutes)
completed: 2026-08-03
status: complete
---

# Phase 131 Plan 05: Real Fork-Base CI Baseline (GATE-07) Summary

**Operator-dispatched `ci.yml` run on `beta` @ `16a313a` (run `30822281624`) measured 69 mypy errors — exactly matching research — recorded verbatim in `131-CI-BASELINE.md` as an input to Phase 132's watermark, with the plan's unreachable `(checked K source files)` acceptance criterion amended and filed as correction F-07 rather than satisfied by fabrication.**

## Performance

- **Duration:** Task 1 (authoring `131-HANDOFF.md`) completed in a prior session and committed as `c89cb800`. Task 2 (the operator dispatch) was executed entirely by the operator, outside this agent's control. This continuation session performed Task 3 (verification + `131-CI-BASELINE.md` + the F-07 correction) in a single pass.
- **Tasks:** 3/3 complete (1 auto, 1 human-action checkpoint resolved by the operator, 1 auto)
- **Files modified:** 3 (1 created, 2 amended)

## Accomplishments

- Independently re-verified, via read-only `gh run view --json`, every fact the orchestrator supplied about run `30822281624` before writing anything: numeric id, resolves, `workflow_dispatch` event, `beta` branch, head SHA `16a313a…`, not the stale `30708836339`, terminal `conclusion: failure`.
- Recorded the run's full per-step status table for the `ci` job — every step through `ruff format check` green, `mypy type check (watermark gate)` red, `pytest`/smoke test skipped — and the verbatim three-line gate-step output (`mypy errors: 69 (watermark: 35)` / `FAIL: …` / exit code 1), mypy `2.3.0`, Python `3.11.15`, all read from the log, none computed locally.
- Confirmed the measured 69 agrees exactly with research's number — no divergence to reconcile or record.
- Discovered and resolved the plan's unreachable acceptance criterion: the `Found N errors in M files (checked K source files)` line the plan's automated block greps for does not exist anywhere in this run's log (0 occurrences of "checked" across 635 log lines), because the fork-base (pre-Phase-131) `tools/check_mypy_watermark.py` extracts only the error count via `re.search(r"Found (\d+) errors?", output)` and never prints mypy's raw stdout. Verified this structurally via `git show 16a313a:tools/check_mypy_watermark.py`, not just by absence.
- Filed this as **correction F-07** in `131-01-PLAN.md`'s corrections table (extending F-01…F-06 in place) and amended `131-05-PLAN.md` task 3's automated `<verify>` grep to key on the literal, satisfiable `mypy errors: [0-9]+ \(watermark: [0-9]+\)` pattern instead — an acceptance gate that can only pass on fabricated input is worse than no gate.
- Wrote `131-CI-BASELINE.md` stating explicitly, in its own section, that the number is an input to Phase 132's watermark and not a Phase 131 claim, and that the `ci` job is RED before and after this phase by design.

## Task Commits

1. **Task 1: Author `131-HANDOFF.md`** — `c89cb800` (docs, prior session)
2. **Task 2: Operator runs the `ci.yml` dispatch** — no commit (human-action checkpoint; the operator dispatched the workflow outside this agent's execution)
3. **Task 3: Fail-closed precondition, read the run, write `131-CI-BASELINE.md`, file F-07** — `b26d370f` (docs)

## Files Created/Modified

- `.planning/phases/131-gate-hardening-ci-parity/131-CI-BASELINE.md` — created. Run id/URL/event/branch/SHA/conclusion, the fail-closed precondition trace, the `ci` job's per-step statuses, the verbatim gate-step output, the F-07 correction (with its structural proof), mypy/Python versions, the "input to Phase 132, not a Phase 131 claim" statement, and the divergence check (agreement, no divergence).
- `.planning/phases/131-gate-hardening-ci-parity/131-01-PLAN.md` — modified. Added row **F-07** to the "Corrections that amend locked decisions" table, alongside the existing F-01…F-06, so 131-07 and Phase 137's ledger pick it up from the same canonical location.
- `.planning/phases/131-gate-hardening-ci-parity/131-05-PLAN.md` — modified. Task 3's `acceptance_criteria` and `<verify><automated>` block amended: replaced the unreachable `Found [0-9]+ errors? in [0-9]+ files? (checked [0-9]+ source files?)` grep with `mypy errors: [0-9]+ \(watermark: [0-9]+\)`, plus a `grep -q 'F-07'` check, with the reason documented inline.

## Decisions Made

- **Amend, don't fabricate.** The plan's task-3 acceptance criterion (a `(checked K source files)` line) is structurally unreachable against real CI output at the fork base. Rather than synthesizing a line CI never emitted, or running mypy locally (which would also violate D-12's "read, never compute" rule and is separately impossible in this devcontainer), the criterion itself was amended and the change filed as a numbered correction (F-07), matching the pattern the plan itself anticipated ("File this as a new numbered plan-time correction").
- **F-07 lives in `131-01-PLAN.md`'s corrections table**, not only in `131-CI-BASELINE.md` prose, so it is discoverable in the same canonical location 131-07's plan already reads for F-01…F-06 (per `131-07-PLAN.md`'s own read_first pointing at that table).
- **No divergence to record.** The measured count (69) agrees exactly with research's 69, so the "measured number wins on divergence" rule was checked and found not to apply.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 4-adjacent, but resolved per explicit orchestrator instruction — not a unilateral architectural change] Amended an unreachable acceptance criterion in 131-05-PLAN.md and filed correction F-07**
- **Found during:** Task 3, before writing any file (fail-closed precondition and initial read of the real CI log)
- **Issue:** The plan's task-3 acceptance criteria and automated `<verify>` block required a verbatim line matching `Found [0-9]+ errors? in [0-9]+ files? \(checked [0-9]+ source files?\)`. That line is structurally absent from the fork-base CI run — the pre-Phase-131 `tools/check_mypy_watermark.py` only extracts the error count via regex and never surfaces mypy's completion clause to CI's log.
- **Fix:** Recorded the verbatim lines CI actually printed; stated the absence and its structural cause explicitly; filed the correction as F-07 in `131-01-PLAN.md`'s table (extending the existing F-01…F-06 series); amended `131-05-PLAN.md` task 3's automated grep to the literal `mypy errors: N (watermark: M)` pattern the real log satisfies.
- **Files modified:** `.planning/phases/131-gate-hardening-ci-parity/131-CI-BASELINE.md`, `131-01-PLAN.md`, `131-05-PLAN.md`
- **Verification:** Re-ran the amended automated `<verify>` block manually against the written `131-CI-BASELINE.md` — `GATE-OK`. Confirmed zero `checked` occurrences across the full 635-line run log and confirmed the structural cause by reading the fork-base source directly via `git show 16a313a:tools/check_mypy_watermark.py`.
- **Committed in:** `b26d370f` (Task 3 commit)

---

**Total deviations:** 1 (a plan-file correction, explicitly required and scoped by this continuation's own instructions — not a spontaneous architectural change)
**Impact on plan:** Necessary for correctness — an acceptance gate that only passes on fabricated CI output would be worse than no gate. No scope creep: only the two plan files this correction touches were modified, and both firmware/submodule trees remain untouched.

## Issues Encountered

None beyond the unreachable-criterion handling documented above, which was anticipated and directed by this continuation's own instructions.

## User Setup Required

None — no external service configuration required. The one privileged action (the `ci.yml` dispatch) was performed entirely by the operator in Task 2, per `131-HANDOFF.md`'s procedure; no further operator action is needed for this plan.

## Next Phase Readiness

- `131-CI-BASELINE.md` is ready for 131-07 to re-read and use as evidence when it ticks `GATE-07`.
- Correction F-07 is filed alongside F-01…F-06 in `131-01-PLAN.md`'s table, ready for 131-07's record and Phase 137's ledger to carry forward.
- Phase 132's watermark work has its input number: 69, read verbatim from a real, current, fork-base CI run — not computed, not a devcontainer measurement.
- No blockers. `git -C /workspaces/firestarter status --short` remained empty throughout; no workflow file was edited; no dispatch, push, merge, tag, or publish was performed by this agent.

---
*Phase: 131-gate-hardening-ci-parity*
*Completed: 2026-08-03*

## Self-Check: PASSED

- FOUND: `.planning/phases/131-gate-hardening-ci-parity/131-CI-BASELINE.md`
- FOUND: `.planning/phases/131-gate-hardening-ci-parity/131-05-SUMMARY.md`
- FOUND: `.planning/phases/131-gate-hardening-ci-parity/131-HANDOFF.md`
- FOUND commit `c89cb800` (Task 1)
- FOUND commit `b26d370f` (Task 3)
- FOUND commit `cf6d904` (SUMMARY)
</content>
