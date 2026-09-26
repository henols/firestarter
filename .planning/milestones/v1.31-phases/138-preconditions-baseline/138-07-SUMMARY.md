---
phase: 138-preconditions-baseline
plan: 07
subsystem: infra
tags: [github-actions, gh-cli, ci-evidence, baseline, requirements-traceability, honesty-ledger]

# Dependency graph
requires:
  - phase: 138-01
    provides: "Three verified v1.31 branch bases (meta d0f0c6a0, firmware 3085084, app 4d18b64) and F-138-01/02/03"
  - phase: 138-02
    provides: "138-02-PULSE-DISTRIBUTION.md — the live per-protocol pulse-width distribution, self-checking script proven to fail before trusted"
  - phase: 138-03
    provides: "138-03-TRACE-CAPTURE.md — measured entry counts, derived bus_config provenance, F-138-06/07/08"
  - phase: 138-04
    provides: "138-04-HOST-BASELINE.md — host suite count (1539/0/0) at CI parity, the unreconciled 1493/46 divergence vs research"
  - phase: 138-05
    provides: "138-03-TRACE-CAPTURE.md §8 Freeze record — frozen golden-trace arrays, blob SHA, two-mechanism identity gate"
  - phase: 138-06
    provides: "138-06-FIRMWARE-MEASUREMENT.md + size_baseline_v131.json — cold AVR/native/warning figures, F-138-04/05"
provides:
  - "138-BASELINE.md — the ten-section (nine plus Hand-off) whole-phase pre-change baseline narrative, every figure cited to its owning per-plan artifact"
  - "Operator-gated CI evidence recorded read-only for all three runs, re-verified independently by this plan via gh run view/gh run list/git ls-remote"
  - "Two empirical corrections to 138-RESEARCH.md's CI trigger table (F-138-10 firmware fires two workflows, F-138-11 app push fires zero for a zero-diff branch), recorded without editing the research artifact"
  - "Consolidated findings register, F-138-01 through F-138-11, each with an owner and a recorded-not-fixed disposition"
  - "PREP-03 and PREP-04 ticked in REQUIREMENTS.md with dated evidence citations"
  - "138-VALIDATION.md completed: all ten per-task rows measured green, nyquist_compliant/wave_0_complete set true"
affects: ["Phase 139 ISSUE-01 (pulse distribution)", "Phase 143/144 (MERGE-05 headroom, F-138-02)", "Phase 144 TEST-06 (frozen trace)", "Phase 144 TEST-08 (size_baseline_v131.json)", "Phase 146 (findings register)"]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Six fail-closed CI-run preconditions read from one gh run view --json call per run, keyed on conclusion never outcome, re-run independently by the executor rather than trusted from the orchestrator's gate-clearance evidence"
    - "Corrections to a prior research artifact are recorded in the citing downstream document, never by editing the research artifact in place"
    - "Measured-number-wins divergence rule applied a third time this phase (host-suite pass/skip split, now also the CI trigger-table completeness gaps)"

key-files:
  created:
    - .planning/phases/138-preconditions-baseline/138-BASELINE.md
  modified:
    - .planning/REQUIREMENTS.md
    - .planning/phases/138-preconditions-baseline/138-VALIDATION.md

key-decisions:
  - "Re-verified all three CI runs independently via fresh gh run view/gh run list/git ls-remote calls rather than accepting the orchestrator's gate-clearance evidence on trust — all figures matched exactly"
  - "Recorded the two empirical CI-trigger-table corrections (F-138-10, F-138-11) as new findings in 138-BASELINE.md rather than editing 138-RESEARCH.md in place, per this project's standing convention for prior research artifacts"
  - "Preserved the 138-04 host-suite divergence (1539/0 vs 1493/46) unreconciled in 138-BASELINE.md §8, per the plan's explicit instruction not to smooth it over"
  - "Set nyquist_compliant: true and wave_0_complete: true in 138-VALIDATION.md because every one of the ten per-task verification map rows measured green with no red row"

requirements-completed: [PREP-03, PREP-04]

coverage:
  - id: D1
    description: "Operator-gated CI evidence recorded read-only for all three runs (two firmware push-produced, one app dispatch-produced), each independently re-verified against the six fail-closed preconditions"
    requirement: "PREP-03"
    verification:
      - kind: other
        ref: "gh run view 31299694430/31299694466 --repo henols/firestarter and gh run view 31300205900 --repo henols/firestarter_app -- all three conclusion=success, headBranch/headSha match §1's table exactly"
        status: pass
    human_judgment: false
  - id: D2
    description: "138-BASELINE.md assembles the whole pre-change baseline in ten sections (nine plus Hand-off), every figure cited to its owning per-plan artifact, with the consolidated findings register F-138-01 through F-138-11"
    requirement: "PREP-03"
    verification:
      - kind: other
        ref: "138-BASELINE.md, 415 lines; grep -c F-138-0[1-7] each == 1; grep -q conclusion; grep -qi 'is not'; 24 citations to the five per-plan artifacts"
        status: pass
    human_judgment: false
  - id: D3
    description: "PREP-03 and PREP-04 ticked in REQUIREMENTS.md with dated evidence citations; traceability rows updated Pending -> Complete; no requirement outside this phase's scope changed"
    requirement: "PREP-04"
    verification:
      - kind: other
        ref: "REQUIREMENTS.md -- grep '^- \\[x\\] \\*\\*PREP-0[1-4]\\*\\*' each count 1; git diff shows only PREP-03/PREP-04 checkbox lines changed"
        status: pass
    human_judgment: false
  - id: D4
    description: "138-VALIDATION.md's per-task verification map completed with measured Task ID/Plan/Wave/Status for all ten rows (all green), Wave 0 checklist fully ticked, and nyquist_compliant/wave_0_complete set true"
    requirement: "PREP-03"
    verification:
      - kind: other
        ref: "138-VALIDATION.md -- no remaining TBD in Task ID/Plan/Wave columns; frontmatter nyquist_compliant: true, wave_0_complete: true"
        status: pass
    human_judgment: false

# Metrics
duration: ~35min (continuation from Task 1's cleared operator gate)
completed: 2026-08-09
status: complete
---

# Phase 138 Plan 07: Preconditions & Baseline — Close-Out Summary

**Ten-section `138-BASELINE.md` narrative assembling the whole v1.31 pre-change baseline (branch bases, frozen golden trace, per-target flash/RAM, four native env counts, host suite count, pulse distribution) with operator-gated CI evidence re-verified read-only across two repos and three runs, an 11-entry findings register, and PREP-03/PREP-04 ticked with citations.**

## Performance

- **Duration:** ~35 min (continuation agent; Task 1's operator gate was cleared before this session
  started)
- **Started:** 2026-08-09 (session start; exact task-1 gate timestamp predates this agent)
- **Completed:** 2026-08-09T07:56:47Z
- **Tasks:** 3 (Task 1 pre-cleared with no file output; Tasks 2-3 executed this session)
- **Files modified:** 3 (1 created, 2 modified)

## Accomplishments

- **Re-verified Task 1's gate-clearance evidence independently**, not on trust: three fresh
  `gh run view` calls (firmware `31299694430`/`31299694466`, app `31300205900`) plus `git ls-remote`
  on all three v1.31 branch refs and both `beta` refs in both submodules — every id, SHA, branch, and
  `conclusion` matched the orchestrator's supplied evidence exactly, and both `beta` tips were
  confirmed unmoved against `138-BRANCH-BASES.md` §3's recorded values.
- **Discovered and recorded two empirical corrections** to `138-RESEARCH.md`'s CI trigger table via
  `gh run list` and reading the two workflow YAMLs live: the firmware push fires **two** workflows
  (`build.yml` + the previously-uncounted `py32f071.yml`, both `push: branches: ['**']`, no path
  filter on push), and the app's push fired **zero** runs for this branch (confirmed both
  pre-dispatch, empty, and post-dispatch, still only the one dispatch-produced run) because the
  branch was created pointing at the existing `beta` tip with zero new commits, leaving no
  changed-files list for `paths-ignore` to evaluate. Filed as **F-138-10**/**F-138-11**, recorded in
  the citing document rather than by editing `138-RESEARCH.md`.
- **Assembled `138-BASELINE.md`**: the runs and their six-item fail-closed preconditions (§§1-2),
  the three verified branch bases and PREP-01's content-equivalence verdict (§3), the frozen golden
  trace with blob SHA and per-protocol entry counts (§4), the AVR/native/warning/host suite counts
  with every verbatim gate verdict (§5), the pulse distribution (§6), the consolidated findings
  register spanning **F-138-01 through F-138-11** with owners and recorded-not-fixed dispositions
  (§7), the divergence check against `138-RESEARCH.md` preserving the 1539/0-vs-1493/46 host-suite
  split unreconciled (§8), an explicit "is / is not" section with a five-item "not established" list
  (§9), and a Hand-off section naming five downstream consumers by exact artifact path (§10).
- **Ticked PREP-03 and PREP-04** in `REQUIREMENTS.md` with dated, cited annotations naming both the
  fork-base and measured-tree SHAs (and why they differ) for PREP-03, and the imported-parser plus
  observed-failure facts for PREP-04. Only these two checkboxes changed (confirmed by `git diff`);
  PREP-01/PREP-02 (already ticked by Plan 138-01) were left untouched.
- **Completed `138-VALIDATION.md`**: filled the per-task verification map's Task ID/Plan/Wave/Status
  columns from the six plans' actual execution (all ten rows green), ticked all nine Wave 0 items as
  delivered, marked both Manual-Only Verifications "Done" with citations, and set
  `nyquist_compliant: true` / `wave_0_complete: true` since no map row is red.

## Task Commits

1. **Task 1: Operator gate — push the three v1.31 branches and dispatch the app CI run** — no
   commit (gate cleared by the orchestrator's operator-authorized actions before this session; this
   plan writes no file for Task 1, only re-verifies and records the evidence inside Task 2's commit)
2. **Task 2: Record the CI evidence read-only and assemble the phase baseline narrative** -
   `baa131a3` (docs)
3. **Task 3: Tick PREP-03/PREP-04, complete the validation map, and hand off** - `385bdca7` (docs)

**Plan metadata:** (this SUMMARY's own commit, immediately following)

_No sub-repo commit was made — this plan's `commits_land_in` is meta-only. Both submodules were
inspected read-only (`gh run view`/`gh run list`/`git ls-remote`/`git status`) and left exactly as
found: `firestarter` clean on `gsd/v1.31-27c-programming-algorithm-fidelity` at `fb7949c0` (already
carrying Plan 138-06's `size_baseline_v131.json` commit from before this session); `firestarter_app`
on the same branch at `4d18b645`, with only the same 8 pre-existing untracked files
`138-04-HOST-BASELINE.md` already documented — no new work left behind._

## Files Created/Modified

- `.planning/phases/138-preconditions-baseline/138-BASELINE.md` (created, 415 lines) — the ten-section
  whole-phase baseline narrative, every figure cited by filename and section
- `.planning/REQUIREMENTS.md` (modified) — PREP-03/PREP-04 checkboxes ticked with dated citation
  annotations; traceability rows changed `Pending` → `Complete`
- `.planning/phases/138-preconditions-baseline/138-VALIDATION.md` (modified) — per-task verification
  map completed (all ten rows green), Wave 0 checklist ticked, sign-off block completed,
  `nyquist_compliant`/`wave_0_complete` set `true`

## Decisions Made

- **Independent re-verification over trust-and-restate.** Even though the orchestrator supplied
  complete, apparently-correct gate-clearance evidence, this plan re-ran every `gh`/`git` check itself
  before writing a single figure into `138-BASELINE.md` — consistent with the plan's own
  `<gate_outcome_evidence>` instruction to "RE-VERIFY it yourself with read-only `gh` calls" and with
  T-138-35's mitigation (spoofed/stale-run provenance).
- **New findings for the two empirical corrections, not silent absorption.** F-138-10/F-138-11 give
  the two CI-trigger-table gaps an owner and a citation rather than treating them as incidental
  narration; `138-RESEARCH.md` itself is left byte-unchanged, per the project's established pattern of
  correcting-by-citation rather than correcting-by-rewrite for closed research artifacts.
- **`nyquist_compliant`/`wave_0_complete` set `true` unconditionally** (not conditionally-false with a
  named red row) because every one of the ten per-task verification map rows is independently
  confirmed green by this plan's own re-measurement plus the six prior plans' own passing gates — no
  row required the "leave false, name the row" branch the plan's acceptance criteria describe for a
  red result.

## Deviations from Plan

None — plan executed exactly as written. Task 1's gate was already cleared with evidence supplied by
the orchestrator; this plan's own re-verification (a superset of what the plan requires, since the
plan permits citing the orchestrator's evidence directly) found zero discrepancies. All automated
`<verify>` blocks for Tasks 2 and 3 passed on the first run; no bug, missing functionality, blocking
issue, or architectural question arose that required a Rule 1-4 classification.

## Issues Encountered

None. The two "empirical corrections" (F-138-10/F-138-11) are not issues encountered during this
plan's own execution — they are the phase's *product*: exactly the kind of measured, previously-unrecorded
mechanism the plan's `<gate_outcome_evidence>` instructed this plan to surface and record.

## User Setup Required

None — no external service configuration required. `gh` CLI was already authenticated as `henols`
with no setup needed; all three CI runs read this session were already `conclusion: success` before
this agent began.

## Next Phase Readiness

- **Phase 138 is now fully discharged.** All four PREP requirements (PREP-01 through PREP-04) are
  ticked with cited evidence; `138-VALIDATION.md` is `nyquist_compliant: true` /
  `wave_0_complete: true`.
- **Phase 139 / ISSUE-01** can quote `138-02-PULSE-DISTRIBUTION.md`'s verbatim output directly (§6 of
  `138-BASELINE.md` names the exact figures and the citation).
- **Phase 144 / TEST-06 and TEST-08** have their exact comparison artifacts named in `138-BASELINE.md`
  §10's Hand-off: the frozen trace fixture + blob SHA + identity gate for TEST-06,
  `firestarter/scripts/baseline/size_baseline_v131.json` (read via the `--baseline` seam, never the
  default) for TEST-08.
- **Phase 143/144** inherit F-138-02's MERGE-05 headroom warning (8 B/2 B remaining on `uno`/`uno328pb`
  at the live `beta` tip).
- **Phase 146** inherits the whole 11-entry findings register (F-138-01 through F-138-11) as an
  already-owned, already-dispositioned starting point for its honesty ledger.
- **The 1539/0-vs-1493/46 host-suite divergence stands unreconciled** — a future phase that wants to
  understand it should re-open the `app_beta_live` checkout directory `138-RESEARCH.md` used, not
  assume either figure is wrong.
- No push, no `gh workflow run`/dispatch, no PR, no merge, and no submodule commit occurred anywhere
  in this plan — confirmed by `git status --porcelain` in both submodules immediately before writing
  this summary (firmware clean; app shows only the same 8 pre-existing untracked files
  `138-04-HOST-BASELINE.md` already documented).

## Self-Check: PASSED

- FOUND: `.planning/phases/138-preconditions-baseline/138-BASELINE.md`
- FOUND: `.planning/REQUIREMENTS.md`
- FOUND: `.planning/phases/138-preconditions-baseline/138-VALIDATION.md`
- FOUND commit: `baa131a3`
- FOUND commit: `385bdca7`

No missing items.

---
*Phase: 138-preconditions-baseline*
*Completed: 2026-08-09*
