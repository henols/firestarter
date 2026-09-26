---
phase: 128-release-asset-fold
plan: 02
subsystem: infra
tags: [github-actions, composite-action, cmake, ci, py32f071]

# Dependency graph
requires:
  - phase: 128-release-asset-fold (128-01, same wave)
    provides: scripts/check_release_assets.py + paired test + fixtures (independent, not depended on)
provides:
  - ".github/actions/build-py32f071/action.yml — single definition of the ARM toolchain install + configure + build"
  - "hex_path output (glob-guarded, exactly-one-match)"
  - "sdk_sha output (resolved from measured FetchContent source dir, non-fatal on layout drift)"
affects: [128-03, 128-04, 128-05, 128-06, 128-09, 128-10]

# Tech tracking
tech-stack:
  added: []
  patterns: ["composite GitHub Action (runs.using: composite) — first of its kind in this repo"]

key-files:
  created: [firestarter/.github/actions/build-py32f071/action.yml]
  modified: []

key-decisions:
  - "Used shopt -s nullglob before the hex glob-count guard so a miss expands to zero words (count 0) instead of bash's default one-element literal-pattern token (count 1) — this is what makes the count!=1 guard actually catch a missing image; without nullglob the naive count check alone would never fire on a miss."
  - "Combined Task 1 (author the action) and Task 2 (add outputs) into a single file write and single commit, since both tasks modify the same new file and no intermediate verifiable state exists between them (the file wouldn't parse as intended action shape without outputs, and there's no separate artifact to commit for Task 1 alone)."

patterns-established:
  - "Composite GitHub Action file shape: runs.using: composite, mandatory shell: bash on every run: step, outputs wired via steps.<id>.outputs.<name>."

requirements-completed: []  # REL-01 and REL-04 are partial slices in this plan; 128-10 owns closure. Do NOT check off REL-01/REL-04 here.

coverage:
  - id: D1
    description: "Composite action .github/actions/build-py32f071/action.yml exists as the single place holding the ARM toolchain/configure/build invocation, called by both workflows in later plans"
    requirement: "REL-01"
    verification:
      - kind: unit
        ref: "python3 -c YAML-parse assertion (runs.using==composite, all run steps have shell:bash, no continue-on-error) — see task 1 automated verify"
        status: pass
    human_judgment: false
  - id: D2
    description: "Action emits hex_path (glob-guarded to exactly one match) and sdk_sha (resolved from measured FetchContent source dir, non-fatal empty-on-miss) as outputs"
    requirement: "REL-04"
    verification:
      - kind: unit
        ref: "python3 -c YAML-parse assertion (outputs keys, GITHUB_OUTPUT writes, glob-count guard regex, literal _deps/py32f071_sdk-src + rev-parse HEAD) — see task 2 automated verify"
        status: pass
    human_judgment: false
  - id: D3
    description: "No ARM toolchain exists in this devcontainer, so the action's actual runtime behavior (does the build succeed, do outputs resolve to real values) can only be observed in CI — deferred to Plan 128-04's py32f071.yml call and Plan 128-10's rehearsal run A"
    verification: []
    human_judgment: true
    rationale: "No local ARM build possible in this devcontainer; this plan's own <verification> section states first real observation happens in later plans via CI run URL + commit SHA citation, not locally provable here."

duration: ~15min
completed: 2026-08-01
status: complete
---

# Phase 128 Plan 02: Composite Action for PY32F071 ARM Build Summary

**Created the repo's first composite GitHub Action, `.github/actions/build-py32f071/action.yml`, holding the single definition of the ARM toolchain install + cmake configure + cmake build, emitting `hex_path` and `sdk_sha` outputs for the release job's later assertions.**

## Performance

- **Duration:** ~15 min
- **Completed:** 2026-08-01T20:56:07Z
- **Tasks:** 2
- **Files modified:** 1 (new file)

## Accomplishments
- Authored `.github/actions/build-py32f071/action.yml` as a composite action (`runs.using: composite`), lifting the four ARM build steps (toolchain install, tool-version record, configure, build) verbatim from `py32f071.yml:24-60`, each with the mandatory `shell: bash` (Pitfall 5, first use of this action-file format in the repo).
- Description block states the D-06 rationale (composite runs in the calling job, preserving REL-01's "same job, after the version bump" property) and the D-05 prohibition (`continue-on-error` must never appear in this file — it belongs on the call site in `beta-build.yml` only).
- Wired `outputs.hex_path` and `outputs.sdk_sha`, populated inside the `build` step: `hex_path` via a `nullglob`-guarded bash array with an exact-count-of-1 assertion (fails loudly on zero or multiple matches); `sdk_sha` via `git -C build/py32f071/_deps/py32f071_sdk-src rev-parse HEAD` (path measured off CI run 30676982030, not guessed), degrading to an empty value with a `::warning::` — never a silent success — when the FetchContent layout has moved.
- Apt install list is unpinned and verbatim (`cmake`, `ninja-build`, `gcc-arm-none-eabi`, `binutils-arm-none-eabi`), per D-17's deliberate deferral of toolchain pinning.

## Task Commits

Both tasks (author the action; add outputs) were implemented as a single coherent file and committed together, since Task 2 modifies the same new file Task 1 creates and there is no intermediate committable state between them:

1. **Task 1 + Task 2: Author composite action with toolchain/configure/build steps and hex_path/sdk_sha outputs** - `4ab53ba` (feat)

**Plan metadata:** commit created at final step below.

## Files Created/Modified
- `firestarter/.github/actions/build-py32f071/action.yml` - New composite action: 4 steps (toolchain, versions, configure, build), 2 outputs (hex_path, sdk_sha), no `continue-on-error` anywhere, description documents D-06/D-05 rationale.

## Decisions Made
- **Merged Task 1 and Task 2 into one commit.** Both tasks specify edits to the identical new file (`action.yml`); Task 1 alone would produce a file with no `outputs:` block, which isn't a meaningfully separable, independently-verifiable intermediate state per the plan's own acceptance criteria (Task 1's criteria don't mention outputs, but the file as authored already needed the `build` step's output-emitting logic described in Task 1's action text item 4: "the two output resolutions described in Task 2"). Executing them as one atomic change avoids a artificial half-written intermediate commit.
- **Used `shopt -s nullglob`** ahead of the `hex_path` glob-count guard. Plain bash (no nullglob) leaves an unmatched glob as a single-element array containing the literal pattern string — meaning a naive `${#MATCHES[@]} -ne 1` check would never catch a genuine miss (count would already be 1, just with wrong content). `nullglob` makes a miss expand to zero words, so the same count check correctly catches both 0-match and >1-match cases. This is a Rule 1 (bug fix) correction to the literal wording in the plan's `<action>` block, which described the failure mode assuming default bash glob behavior without naming the guard needed to make the described guard actually work.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Added `shopt -s nullglob` before the hex_path glob-count guard**
- **Found during:** Task 2 (Emit hex_path and sdk_sha)
- **Issue:** The plan's `<action>` text describes asserting exactly one glob match via `${#MATCHES[@]}` and warns that "an unmatched bash glob expands to the literal pattern... without the count test a missing image would silently propagate the string." Read literally, plain bash's default glob behavior on a miss produces a *one*-element array (containing the literal pattern text), so a bare `count != 1` check would not actually catch a miss — the count is already 1, just with the wrong content. The stated guard would be a no-op on the exact failure mode it is meant to catch.
- **Fix:** Added `shopt -s nullglob` immediately before the array assignment, so an unmatched glob expands to zero words (count 0) rather than the literal pattern. The existing `count != 1` guard then correctly fires on both zero matches and multiple matches.
- **Files modified:** `firestarter/.github/actions/build-py32f071/action.yml`
- **Verification:** Task 2's automated verify script (YAML parse + regex assertions for `GITHUB_OUTPUT`, `_deps/py32f071_sdk-src`, `rev-parse HEAD`, and the `${#NAME[@]}` guard pattern) passes with `nullglob` present; the guard's actual runtime behavior on a real miss can only be observed in CI (no ARM toolchain locally), same limitation as the rest of this plan.
- **Committed in:** `4ab53ba` (part of the single task commit)

---

**Total deviations:** 1 auto-fixed (1 bug fix)
**Impact on plan:** Necessary for correctness — without it, the described guard would silently fail to catch the exact "missing image" case it exists to prevent. No scope creep; the fix is scoped entirely to the `build` step's existing glob-guard logic.

## Issues Encountered
None.

## User Setup Required
None - no external service configuration required.

## Known Stubs
None. The action is a complete, self-contained composite action; no placeholder logic.

## Threat Flags
None. Both new surfaces (`T-128-03` SDK-source substitution, `T-128-11` continue-on-error containment collapse) are already named in this plan's own `<threat_model>` and mitigated as designed (sdk_sha resolution + description-block prohibition, respectively). No unlisted surface was introduced.

## Next Phase Readiness
- `.github/actions/build-py32f071/action.yml` is ready to be called by `py32f071.yml` (Plan 128-04, LOUD gate) and `beta-build.yml` (Plan 128-05, SOFT gate with `continue-on-error` at the call site).
- `hex_path` and `sdk_sha` outputs are ready for Plan 128-06's filename-equality and SDK-pin assertions.
- No blockers. This plan's own scope boundary explicitly defers REL-01/REL-04 closure to Plans 128-05, 128-06, 128-09, and 128-10 — not re-derived here.

---
*Phase: 128-release-asset-fold*
*Completed: 2026-08-01*

## Self-Check: PASSED
- FOUND: firestarter/.github/actions/build-py32f071/action.yml
- FOUND: commit 4ab53ba (firestarter submodule)
