---
phase: 128-release-asset-fold
plan: 07
subsystem: infra
tags: [github-actions, release-assets, softprops-action-gh-release, cmake, py32f071]

# Dependency graph
requires:
  - phase: 128-release-asset-fold (128-01, prior wave)
    provides: "scripts/check_release_assets.py — the AVR-assets-present gate this plan's only production call site invokes, and the comment-stripped fail_on_unmatched_files invariant test that constrains this plan's Release-step comment wording"
  - phase: 128-release-asset-fold (128-06, prior wave)
    provides: "the three if: steps.arm.outcome == 'success'-guarded assertion steps sitting between the D-07 report step and Resolve release target SHA, undisturbed by this plan"
  - phase: 128-release-asset-fold (128-05, prior wave)
    provides: "steps.mode.outputs.rehearsal (the normalised boolean draft:/tag_name: now consume) and the arm call site with continue-on-error: true"
provides:
  - "Assert all AVR release assets are present (REL-03) step: unconditional (no if:), immediately before Release, calling scripts/check_release_assets.py with no flags"
  - "Release step's files: as a two-entry block list reaching both the PlatformIO (.pio/build/) and CMake (build/py32f071/) trees (REL-02/D-15)"
  - "A comment pinning the fail_on_unmatched_files omission with the corrected mechanism (research F-1), replacing the superseded glob-vs-literal folklore"
  - "Release step's draft: and tag_name: wired to steps.mode.outputs.rehearsal (D-01/D-03), never to inputs.rehearsal directly"
affects: [128-10]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Pinning a deliberate omission (fail_on_unmatched_files never set) with a comment naming the requirement it protects, enforced by a comment-stripped invariant test from a prior plan"

key-files:
  created: []
  modified:
    - firestarter/.github/workflows/beta-build.yml

key-decisions:
  - "Placed the AVR-assets gate step with zero if: guard, immediately before Release — the whole point per D-11/D-12 is that it still runs when steps.arm was contained"
  - "Corrected REL-02's own stated rationale in the shipped comment rather than repeating it: the release action makes no glob-vs-literal distinction (research F-1); the only knob is fail_on_unmatched_files, default false"
  - "Grouped the D-01/D-03/F-3/F-7 comment directly above draft: and tag_name: (which now sit adjacent to each other, after files:) so one comment block covers both consuming lines coherently"
  - "Did not mark REL-02 or REL-03 complete in REQUIREMENTS.md — both are multi-plan requirements; Plan 128-10 is the sole owner of requirement closure for this phase"

patterns-established: []

requirements-completed: []  # REL-02 and REL-03 are multi-plan; this plan lands the publication
                            # mechanism and the gate's call site only. Plan 128-10 marks completion.

coverage:
  - id: D1
    description: "The AVR-assets gate runs unconditionally (no if: key), and its step index is exactly one less than the Release step's index"
    requirement: "REL-03"
    verification:
      - kind: unit
        ref: "python3 -c YAML-parse assertion (exactly one check_release_assets.py step, no 'if' key, index == Release_index - 1, no --build-root/--baseline flags) -- Task 1 automated verify; also `python3 scripts/check_release_assets.py --build-root tests/fixtures/clean_release_assets_all_three/pio_build` exits 0"
        status: pass
    human_judgment: false
  - id: D2
    description: "files: parses to the exact two-element list ['.pio/build/**/firestarter_*.hex', 'build/py32f071/firestarter_*.hex'], no fail_on_unmatched_files key anywhere (including comment-stripped source), and the pinning comment carries the corrected mechanism without repeating the superseded folklore"
    requirement: "REL-02"
    verification:
      - kind: unit
        ref: "python3 -c YAML-parse + comment-stripped regex assertion -- Task 2 automated verify; python3 -m pytest tests/test_check_release_assets.py -q (10 passed, including the invariant test from Plan 128-01)"
        status: pass
    human_judgment: false
  - id: D3
    description: "draft: and tag_name: both resolve exclusively through steps.mode.outputs.rehearsal, never inputs.rehearsal; prerelease/make_latest unchanged; the comment records D-01, D-03, F-3, run 30199560282, and 3.0.0b11"
    verification:
      - kind: unit
        ref: "python3 -c YAML-parse assertion on rel['with']['draft']/['tag_name'] -- Task 3 automated verify; python3 -m pytest tests/ -q (180 passed); pio test -e native and -e native_nodevtools (141/141 each) unchanged"
        status: pass
    human_judgment: false
  - id: D4
    description: "Whether the AVR gate, the two-entry files: glob, and the rehearsal-wired draft:/tag_name: actually behave correctly on a real GitHub Actions run (a real published release, a real contained ARM failure) is unproven locally — no dispatch may run from this plan (D-04)"
    verification: []
    human_judgment: true
    rationale: "No task in this plan may run git push or gh workflow run (D-04, autonomous: true carried forward under the structural operator gate). First real observation happens on Plan 128-10's rehearsal runs A and B, cited by CI run URL + commit SHA in 128-NONREGRESSION.md. Nothing in this plan claims the published asset runs, boots, or installs."

# Metrics
duration: ~20min
completed: 2026-08-01
status: complete
---

# Phase 128 Plan 07: Release-Path Closure (AVR Gate Call Site, Two-Entry files:, Rehearsal-Wired draft:/tag_name:) Summary

**Wired the AVR-assets-present gate as an unconditional step immediately before `Release`, converted `files:` to a two-entry block list so the CMake-built py32f071 image is actually reachable, pinned the `fail_on_unmatched_files` omission with the research-corrected mechanism instead of the superseded glob-vs-literal folklore, and wired `draft:`/`tag_name:` to the single normalised rehearsal switch.**

## Performance

- **Duration:** ~20 min
- **Completed:** 2026-08-01
- **Tasks:** 3/3
- **Files modified:** 1 (`firestarter/.github/workflows/beta-build.yml`)

## Accomplishments

- Added `Assert all AVR release assets are present (REL-03)` immediately before `Release`, calling `python3 scripts/check_release_assets.py` with no flags. The step carries no `if:` key at all — the requirement is that it still runs when `steps.arm` above was contained, since that is the only path where "a broken ARM build still publishes all three AVR assets" is actually provable.
- Converted the `Release` step's `files:` from the single-line scalar `.pio/build/**/firestarter_*.hex` to a two-entry block list, adding `build/py32f071/firestarter_*.hex` (a glob, not a literal, per D-15) so the CMake-built image is inside the publication glob for the first time in this phase.
- Pinned the `fail_on_unmatched_files` omission with a comment naming REL-03 and carrying research finding F-1's corrected mechanism: `softprops/action-gh-release`'s `unmatchedPatterns()` globs every `files:` entry — literal or glob alike — via `glob.sync()`, and `run.ts` decides severity purely from the `fail_on_unmatched_files` input (default `false`). The comment explicitly does not repeat the superseded "warns on glob, fails on literal" folklore anywhere in the file.
- Wired `draft:` to `${{ steps.mode.outputs.rehearsal == 'true' }}` and replaced `tag_name:` with the rehearsal-aware ternary form, both reading exclusively through Plan 128-05's `mode` step output — never `inputs.rehearsal` directly (which is absent on a `push` event and would leak an unresolved comparison onto every real beta push). The comment records D-01, D-03, F-3 (a draft release creates no git tag), and F-7's precedent (run `30199560282` published the real public prerelease `3.0.0b11` with a real tag from a non-default branch before draft mode existed), plus the requirement that every rehearsal dispatch supply `beta_version` explicitly.
- Re-read the complete `Release` step after all three tasks landed; it reads coherently top to bottom.

## Task Commits

Each task was committed atomically inside `/workspaces/firestarter` on branch `v1.23-py32f071-integration`:

1. **Task 1: Call the AVR-assets gate unconditionally, immediately before Release** - `542a25c` (feat)
2. **Task 2: Convert files: to a two-entry block list and pin the unmatched-files omission** - `c49955e` (feat)
3. **Task 3: Wire draft: and tag_name: to the rehearsal switch** - `88386db` (feat)

**Plan metadata:** committed in the meta-repo (`.planning/phases/128-release-asset-fold/128-07-SUMMARY.md`, `STATE.md`, `ROADMAP.md`).

## Files Created/Modified

- `firestarter/.github/workflows/beta-build.yml` — gained one new unguarded step (the AVR-assets gate), a two-entry `files:` block list with a corrected-mechanism comment, and rehearsal-wired `draft:`/`tag_name:` values. No existing step reordered, modified, or deleted; the `env:`/`GITHUB_TOKEN` block and its Phase 20 E2E-05 comment are byte-identical to their pre-plan form; `jobs.build.permissions` unchanged (`{contents: write}`).

## Decisions Made

- Followed D-11/D-12/D-15/D-01/D-03 exactly as specified in the plan, with research finding F-1's correction applied verbatim to the `files:` comment (never repeating REL-02's own superseded rationale).
- Grouped the D-01/D-03/F-3/F-7 comment directly above the now-adjacent `draft:`/`tag_name:` lines (placed after `files:` in the `with:` mapping) so one comment block covers both consuming expressions coherently, rather than splitting the explanation across two separate locations in the mapping.
- Did not mark REL-02 or REL-03 complete in `REQUIREMENTS.md` per the plan's explicit scope boundary — both are multi-plan requirements; Plan 128-10 additionally needs run A's observed asset list (REL-02) and run B's observed cascade plus the LOUD gate (REL-03) before either can close.
- Left `build.yml` (stable/`main`) untouched, per D-13 — confirmed via `git diff HEAD~3 --name-only` listing only `beta-build.yml`.

## Deviations from Plan

None — plan executed exactly as written. All three tasks' automated verify scripts passed on first implementation; no auto-fixes were needed.

## Issues Encountered

None. One observation, not a deviation: the plan's Task 3 acceptance criteria states "the whole file still contains zero occurrences of `steps.arm.conclusion` and zero occurrences of `always()`." The literal substring `always()` already appears twice in the file, in Plan 128-05's D-07 report-step comment (explanatory prose stating *why* `if: always()` is deliberately absent, e.g. "There is no `if: always()` here"), landed in a prior wave before this plan started. This plan's own diff (all three tasks) introduces neither `steps.arm.conclusion` nor `always()` anywhere; the pre-existing occurrences are prose, not a functional `if: always()` directive, and are out of this plan's scope to alter (128-05's file, not 128-07's).

## User Setup Required

None - no external service configuration required. No CI dispatch occurred in this plan (that is Plan 128-10's scope, structurally gated per D-04).

## Known Stubs

None. All three changes are complete, functioning workflow steps/values with real logic — no placeholder logic. Whether they behave correctly on a real GitHub Actions run (the gate actually failing a contained-ARM release, the two-entry glob actually publishing the py32 asset, a rehearsal dispatch actually producing an unmistakably-named draft with no tag) is unproven locally — no dispatch may run from this plan (D-04) — but this is a stated, plan-scoped limitation, not a stub. First real observation is Plan 128-10's rehearsal runs A and B.

## Threat Flags

None. All new surface introduced here is already named in this plan's own `<threat_model>` and mitigated exactly as designed: T-128-02 (rehearsal publishing a real public prerelease/tag) by `draft:` from the normalised switch plus D-03's tag override plus D-04's structural gate; T-128-04 (a broken build silently shipping an incomplete release) by the unconditional AVR gate; T-128-18 (`fail_on_unmatched_files: true` added later "for stricter CI") by the pinning comment plus Plan 128-01's comment-stripped invariant test; T-128-15 (`draft: true` leaking onto a real beta push) by resolution going exclusively through `steps.mode.outputs.rehearsal`; T-128-19 (a zero-byte hex published as a real asset) by the assets gate's `st_size > 0` check (Plan 128-01), proven by the zero-byte planted fixture.

## Next Phase Readiness

- This is the last change to `beta-build.yml` in this phase (per the plan's own objective) — `.github/actions/build-py32f071/action.yml`, `platform/py32f071/CMakeLists.txt`, `platform/py32f071/README.md`, and the app-repo cross-repo binding remain other plans' scope.
- Plan 128-08 (Wave 5) can now write the `## Release integration` README section, including D-13's record that `build.yml` is deliberately untouched — confirmed here that `build.yml` was not modified by this plan (`git diff HEAD~3 --name-only` in `firestarter` lists only `.github/workflows/beta-build.yml`).
- Plan 128-10 must cite rehearsal run A's log for: the AVR gate passing on a healthy run, the two-entry `files:` actually publishing both the AVR and py32 assets, and the resolved `rehearsal` value echoing `false`/`true` correctly per dispatch — none of this is proven here. Run B must show the gate cascade holding (Configure fails → contained → Build fails → contained → the py32 glob matches nothing → the three AVR assets still publish, with the AVR gate itself passing throughout since it never depended on ARM).
- No blockers. `firestarter`'s working tree is clean (`git status --porcelain` empty) after the three task commits; `python3 -m pytest tests/ -q` is 180 passed; `pio test -e native` and `pio test -e native_nodevtools` are 141/141 passed each, unchanged by this plan.
- REL-02 and REL-03 remain open as a whole — only the publication-mechanism and gate-call-site slices are advanced here. Plan 128-10 must not skip re-verifying these slices when it ticks REL-02/REL-03.

---
*Phase: 128-release-asset-fold*
*Completed: 2026-08-01*

## Self-Check: PASSED

- FOUND: `/workspaces/firestarter/.github/workflows/beta-build.yml`
- FOUND: `/workspaces/.planning/phases/128-release-asset-fold/128-07-SUMMARY.md`
- FOUND commit `542a25c` (Task 1) in `firestarter`
- FOUND commit `c49955e` (Task 2) in `firestarter`
- FOUND commit `88386db` (Task 3) in `firestarter`
- FOUND commit `8ad7107` (SUMMARY.md) in the meta-repo
