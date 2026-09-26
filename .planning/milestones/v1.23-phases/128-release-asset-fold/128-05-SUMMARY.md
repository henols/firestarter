---
phase: 128-release-asset-fold
plan: 05
subsystem: infra
tags: [github-actions, composite-action, release, py32f071, rehearsal]

# Dependency graph
requires:
  - phase: 128-release-asset-fold (128-02, prior wave)
    provides: ".github/actions/build-py32f071/action.yml composite action (hex_path, sdk_sha outputs, no continue-on-error)"
  - phase: 128-release-asset-fold (128-04, prior wave)
    provides: "py32f071.yml LOUD gate calling the same composite action, id: arm, zero continue-on-error, underscore literals repo-wide"
provides:
  - "beta-build.yml gains a permanent, boolean, default-false rehearsal workflow_dispatch input (D-01/D-03)"
  - "Resolve rehearsal mode step (id: mode) normalises the input once, exposing steps.mode.outputs.rehearsal, echoed to $GITHUB_STEP_SUMMARY on every run"
  - "Build PY32F071 firmware step (id: arm) calls ./.github/actions/build-py32f071, strictly after stefanzweifel/git-auto-commit-action@v5 and before Resolve release target SHA, with continue-on-error: true on this call site only (D-05/D-06/REL-01)"
  - "Report a missing PY32F071 image step, keyed on steps.arm.outcome == 'failure' (never .conclusion), emits a ::warning:: annotation and a $GITHUB_STEP_SUMMARY line, fails nothing (D-07)"
affects: [128-06, 128-07, 128-10]

# Tech tracking
tech-stack:
  added: []
  patterns: ["step-output normalisation of a workflow_dispatch input (id: mode) so an absent-on-push input never reaches a downstream draft:/tag_name: expression as an unresolved value"]

key-files:
  created: []
  modified:
    - firestarter/.github/workflows/beta-build.yml

key-decisions:
  - "Combined only the literal-text mechanism explanation for D-07's outcome-vs-conclusion note: wrote 'the step's `outcome`, never its `conclusion`' instead of the plan read_first's literal phrase `steps.arm.conclusion`, because the plan's own automated verify script asserts the whole file contains zero occurrences of that exact dotted substring (a Rule 1 self-consistency fix: writing the forbidden string in a comment explaining why it's forbidden would fail the plan's own check)."
  - "Did not touch the Release step in any task, per the plan's explicit scope boundary — Plan 128-07 owns it."
  - "Committed each task separately (3 commits) rather than combining, since each task's YAML verify script targets a distinct, independently-checkable state (input+step, call site, report step) with no shared-uncommittable-intermediate issue like 128-02/128-04 had."

patterns-established: []

requirements-completed: []  # REL-01 (ordering slice) and REL-03 (containment slice) are advanced, NOT closed,
                            # by this plan. Plan 128-10 is the sole owner of requirement closure for this phase.

coverage:
  - id: D1
    description: "Permanent, boolean, default-false rehearsal workflow_dispatch input added beside beta_version; resolved once by the mode step and echoed to $GITHUB_STEP_SUMMARY on every run, including real beta pushes where the input is absent"
    requirement: "REL-01"
    verification:
      - kind: unit
        ref: "python3 -c YAML-parse assertion (workflow_dispatch.inputs keys, rehearsal.type==boolean, rehearsal.default is False, mode step at index 1, env-only input passthrough, no ${{ in run body) -- see Task 1 automated verify"
        status: pass
    human_judgment: false
  - id: D2
    description: "Build PY32F071 firmware step (id: arm) calls the composite action strictly after the version-bump auto-commit and before Resolve release target SHA, with continue-on-error: true on this call site only"
    requirement: "REL-01"
    verification:
      - kind: unit
        ref: "python3 -c YAML-parse assertion (version < git-auto-commit-action < arm < Release ordering, arm.uses==./.github/actions/build-py32f071, arm.continue-on-error is True, composite action still carries zero continue-on-error) -- see Task 2 automated verify"
        status: pass
    human_judgment: false
  - id: D3
    description: "A broken ARM build is contained at this call site and cannot block the three AVR assets published by the unchanged Release step"
    requirement: "REL-03"
    verification:
      - kind: unit
        ref: "git diff HEAD~3 HEAD -- beta-build.yml shows insertions only, Release step byte-identical; python3 -m pytest tests/ -q -> 180 passed"
        status: pass
    human_judgment: false
  - id: D4
    description: "D-07's report step is keyed on steps.arm.outcome (never .conclusion), emits both a ::warning:: annotation and a $GITHUB_STEP_SUMMARY line with the verbatim message, and fails nothing"
    verification:
      - kind: unit
        ref: "python3 -c YAML-parse assertion (if expression exact match, ::warning:: and GITHUB_STEP_SUMMARY present, verbatim message text present, step immediately after arm, zero occurrences of 'steps.arm.conclusion' in the whole file) -- see Task 3 automated verify"
        status: pass
    human_judgment: false
  - id: D5
    description: "The resolved rehearsal value's observable correctness on a real push (visibly false) and the report step's actual firing on a broken ARM build are unproven locally -- no ARM toolchain exists in this devcontainer and no dispatch may run from this plan"
    verification: []
    human_judgment: true
    rationale: "No task in this plan may run git push or gh workflow run (operator-gated, D-04); the mode step's resolved value and the report step's firing condition can only be observed on rehearsal runs A and B in Plan 128-10, cited by CI run URL + commit SHA in 128-NONREGRESSION.md."

# Metrics
duration: ~15min
completed: 2026-08-01
status: complete
---

# Phase 128 Plan 05: Fold ARM Build Into beta-build.yml Summary

**Added a permanent boolean `rehearsal` dispatch input to `beta-build.yml`, normalised it into one observable step output, called the ARM composite action strictly after the version-bump auto-commit with `continue-on-error: true` at the call site only, and added an `outcome`-keyed report step that surfaces a soft ARM failure without blocking any AVR asset.**

## Performance

- **Duration:** ~15 min
- **Completed:** 2026-08-01
- **Tasks:** 3/3
- **Files modified:** 1 (`firestarter/.github/workflows/beta-build.yml`)

## Accomplishments

- Added the `rehearsal` `workflow_dispatch` input (boolean, `default: false`, `required: false`) beside the existing `beta_version` string input, commented with D-01/D-03's permanence rationale.
- Added a `Resolve rehearsal mode` step (`id: mode`) as the second step in the job (immediately after `actions/checkout@v4`), which reads `inputs.rehearsal` only through an `env: REHEARSAL_INPUT` mapping — never interpolated into the `run:` body (Security V5) — resolves it to exactly `true` or `false`, writes `steps.mode.outputs.rehearsal`, and echoes the resolved value to both the job log and `$GITHUB_STEP_SUMMARY` on every run, including real `beta` pushes where the input is absent and must resolve `false` (Assumption A1).
- Added a `Build PY32F071 firmware` step (`id: arm`) calling `./.github/actions/build-py32f071`, positioned strictly between `stefanzweifel/git-auto-commit-action@v5` and `Resolve release target SHA` — asserted mechanically by step-index comparison, not read by eye. `continue-on-error: true` lives on this call site only (D-05); the composite action itself still carries none, so the loud/soft split with `py32f071.yml` (128-04's LOUD gate) cannot drift apart unnoticed.
- Added a `Report a missing PY32F071 image` step immediately after `arm`, gated on `steps.arm.outcome == 'failure'` (never `.conclusion` — the hollow-gate shape Phases 118 and 124 both had to unwind). It emits a `::warning::` annotation and a `$GITHUB_STEP_SUMMARY` line with the exact D-07 wording, and fails nothing (no `continue-on-error`, no `exit` on any path). `if: always()` is deliberately omitted, with the reason recorded in-file.
- The `Release` step is byte-identical to its pre-plan form; `git diff HEAD~3 HEAD -- beta-build.yml` shows insertions only across all three task commits.

## Task Commits

1. **Task 1: Add the permanent rehearsal boolean input and normalise it into one observable output** - `45d2bce` (feat)
2. **Task 2: Call the composite action after the version-bump auto-commit, contained** - `db8b258` (feat)
3. **Task 3: Add D-07's report step, keyed on outcome, failing nothing** - `0aed689` (feat)

All three commits are in the `firestarter` submodule, branch `v1.23-py32f071-integration`.

**Plan metadata:** committed separately (this SUMMARY + STATE/ROADMAP update), meta repo.

## Files Created/Modified

- `firestarter/.github/workflows/beta-build.yml` — gained the `rehearsal` dispatch input, the `mode` normalisation step, the `arm` composite call site (contained), and the `outcome`-keyed report step. No existing step reordered, modified, or deleted.

## Decisions Made

- **Reworded the D-07 mechanism comment to avoid the literal substring `steps.arm.conclusion`.** The plan's own read_first text and rationale use that exact phrase, but its own automated verify script for Task 3 asserts the entire file contains zero occurrences of it (`assert 'steps.arm.conclusion' not in t`). Writing the phrase in the explanatory comment would have made the plan's own check fail. Reworded to "the step's `outcome`, never its `conclusion`" — same mechanism, same D-07/F-4 citation, without the forbidden concatenated substring. This is a Rule 1 (bug) self-consistency fix scoped entirely to comment wording; no behavioral or structural change.
- **Committed each task separately** (3 commits, not combined) — unlike 128-02 and 128-04, each of this plan's three tasks produces an independently meaningful and independently verifiable YAML state (new input+step, call site, report step), with no shared-file "can't verify until both land" situation.
- Did not touch the `Release` step in any task — Plan 128-07 owns it.
- Did not mark REL-01 or REL-03 Complete in `.planning/REQUIREMENTS.md` — this plan advances only the ordering slice of REL-01 and the containment slice of REL-03; Plan 128-10 is the sole owner of requirement closure for this phase.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Reworded D-07 comment to avoid the literal `steps.arm.conclusion` substring**
- **Found during:** Task 3 (Add D-07's report step)
- **Issue:** My first draft of the comment above the report step used the plan's own read_first wording verbatim — "the condition reads `steps.arm.outcome`, never `steps.arm.conclusion`" — which contains the exact dotted substring the plan's own Task 3 automated verify script forbids anywhere in the file (`assert 'steps.arm.conclusion' not in t`). Running that verify script against my first draft failed with `AssertionError: conclusion-keyed condition present (F-4 / Pitfall 4)`.
- **Fix:** Reworded the comment to "the step's `outcome`, never its `conclusion`" — preserving the D-07/F-4 citation and the full mechanism explanation (outcome:failure vs conclusion:success under continue-on-error, the Phase 118/124 hollow-gate precedent) without writing the two words concatenated by a dot.
- **Files modified:** `firestarter/.github/workflows/beta-build.yml`
- **Verification:** Task 3's automated verify script passes after the reword; `python3 -m pytest tests/ -q` remains 180 passed.
- **Committed in:** `0aed689` (Task 3 commit)

---

**Total deviations:** 1 auto-fixed (1 bug fix, comment wording only)
**Impact on plan:** No behavioral or structural change. Necessary so the plan's own acceptance check doesn't fail on the literal text it prescribes; the mechanism explanation (D-07/F-4) is fully preserved in substance.

## Issues Encountered

None beyond the deviation above.

## User Setup Required

None - no external service configuration required.

## Known Stubs

None. All three steps are complete, functioning workflow steps with no placeholder logic. Their actual runtime behavior (does the mode step resolve correctly on a real push, does the report step actually fire on a broken ARM build) is unproven locally — no ARM toolchain exists in this devcontainer and no dispatch may run from this plan (D-04) — but this is a stated, plan-scoped limitation, not a stub: the code paths are real and complete, only their live observation is deferred to Plan 128-10's rehearsal runs A and B.

## Threat Flags

None. All new surface (the `rehearsal` input reaching shell, the `continue-on-error` containment boundary, the `outcome`-keyed report) is already named in this plan's own `<threat_model>` (T-128-01, T-128-08, T-128-11, T-128-15, T-128-04) and mitigated exactly as designed: boolean typing + env-only passthrough for T-128-01/T-128-15, call-site-only `continue-on-error` cross-checked against the composite action for T-128-11/T-128-04, and the outcome-not-conclusion condition for T-128-08.

## Next Phase Readiness

- `beta-build.yml` now exposes `steps.mode.outputs.rehearsal`, ready for Plan 128-07 to consume in the `Release` step's `draft:` and `tag_name:` expressions.
- `steps.arm.outputs.hex_path` / `.sdk_sha` are ready for Plan 128-06's filename-equality and SDK-pin assertions, to be inserted after the report step and before `Resolve release target SHA`.
- Plan 128-07 still needs to add the AVR-assets gate call, the two-entry `files:` block, and wire `draft:`/`tag_name:` to `steps.mode.outputs.rehearsal` — none of that was done here, per this plan's explicit scope boundary.
- This plan's actual CI behavior (does `rehearsal` resolve `false` on a push, does the report step fire on a broken build) is unproven locally and must be cited by CI run URL + commit SHA in `128-NONREGRESSION.md` (Plan 128-10). No claim here says the image runs, boots, or installs.
- No blockers. `firestarter`'s working tree is clean (`git status --porcelain` empty) after the three task commits; `python3 -m pytest tests/ -q` is 180 passed.
- REL-01 and REL-03 remain open as a whole — only the ordering slice (REL-01) and the containment slice (REL-03) are advanced here. Plan 128-10 must not skip re-verifying these slices when it ticks REL-01/REL-03.

---
*Phase: 128-release-asset-fold*
*Completed: 2026-08-01*

## Self-Check: PASSED
- FOUND: `/workspaces/.planning/phases/128-release-asset-fold/128-05-SUMMARY.md`
- FOUND: `/workspaces/firestarter/.github/workflows/beta-build.yml`
- FOUND: commit `45d2bce` (firestarter submodule)
- FOUND: commit `db8b258` (firestarter submodule)
- FOUND: commit `0aed689` (firestarter submodule)
- FOUND: commit `11b0d40` (meta repo, SUMMARY.md)
