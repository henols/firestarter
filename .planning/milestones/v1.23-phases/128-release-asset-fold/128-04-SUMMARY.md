---
phase: 128-release-asset-fold
plan: 04
subsystem: infra
tags: [github-actions, composite-action, py32f071, ci, release-assets]

# Dependency graph
requires:
  - phase: 128-release-asset-fold (128-02, prior wave)
    provides: ".github/actions/build-py32f071/action.yml composite action (hex_path, sdk_sha outputs)"
  - phase: 128-release-asset-fold (128-03, prior wave)
    provides: "underscore-renamed CMake output literals + measured 21-occurrence hyphenated-literal baseline confined to py32f071.yml"
provides:
  - "py32f071.yml calls the composite action (uses: ./.github/actions/build-py32f071, id: arm) instead of inlining toolchain/configure/build"
  - "py32f071.yml carries zero continue-on-error anywhere -- remains the LOUD gate"
  - "MERGE-03's header comment rewritten to record the D-05 resolution instead of pointing at Phase 128 as an open question"
  - "every remaining hyphenated firestarter-py32f071 literal in the file renamed to the underscore form"
  - "post-build artifact upload collapsed to the single install image (firestarter_py32f071.hex), diagnostics upload retained on failure"
affects: [128-05, 128-06, 128-08, 128-09, 128-10]

# Tech tracking
tech-stack:
  added: []
  patterns: ["LOUD/SOFT workflow split verified by YAML-parsing both files for a continue-on-error key, never by grepping raw text (a grep would self-invalidate against the explanatory comment naming the key)"]

key-files:
  created: []
  modified:
    - firestarter/.github/workflows/py32f071.yml

key-decisions:
  - "Named the composite call step 'Build PY32F071 firmware' with id: arm per the plan's literal text; no continue-on-error added, per D-05."
  - "Repeated the continue-on-error removal trigger sentence in both the on: header comment and the call-site comment, since Task 1's acceptance criteria required the substring 'real silicon' inside the header comment specifically (the trigger comment at lines 4-8), not only at the call site."
  - "Kept step names matching the plan's literal wording ('Report firmware size', 'Verify the install image exists and is non-empty', 'Upload firmware install image') even though the pre-existing names differed ('Report size', 'Create and verify firmware checksums', 'Upload firmware artifacts') -- the plan's acceptance criteria reference these exact names."

patterns-established: []

requirements-completed: []  # REL-03 (loud-half slice only) and REL-04 (workflow-rename slice only) are advanced,
                            # NOT closed, by this plan. Plan 128-10 is the sole owner of REL-03/REL-04 closure.

coverage:
  - id: D1
    description: "py32f071.yml's four inlined ARM build steps replaced by a single call to the composite action (id: arm), carrying no continue-on-error; MERGE-03's header comment rewritten to record the D-05 resolution"
    requirement: "REL-03"
    verification:
      - kind: unit
        ref: "python3 -c YAML-parse assertion (single id==arm step, uses==./.github/actions/build-py32f071, no continue-on-error anywhere, trigger blocks unchanged, no apt-get/cmake in any run body) -- see Task 1 automated verify"
        status: pass
      - kind: unit
        ref: "python3 -c header-comment substring assertion (MERGE-03, D-05, RESOLVED, LOUD, real silicon present; 'is recorded for Phase 128 to resolve' absent)"
        status: pass
    human_judgment: false
  - id: D2
    description: "Every remaining hyphenated firestarter-py32f071 literal renamed to the underscore form; post-build artifact upload collapsed to the single install image with the diagnostics upload retained on failure"
    requirement: "REL-04"
    verification:
      - kind: unit
        ref: "grep -c 'firestarter-py32f071' .github/workflows/py32f071.yml == 0, plus python3 -c YAML-parse assertion (exactly 2 upload-artifact steps with the expected names/paths/if-no-files-found, no sha256sum/SHA256SUMS, no 'release' in any step name) -- see Task 2 automated verify"
        status: pass
    human_judgment: false
  - id: D3
    description: "LOUD/SOFT invariant proven by YAML-parsing both py32f071.yml and the composite action for a continue-on-error key (none in either); repo-wide hyphenated-literal count confirmed zero (was 21 per 128-03's baseline); pytest and git status clean"
    verification:
      - kind: unit
        ref: "python3 -c YAML-parse continue-on-error absence check across both files -> 'LOUD/SOFT INVARIANT OK'; grep -rl 'firestarter-py32f071' --include={*.yml,*.txt,*.md,*.cmake} /workspaces/firestarter -> empty; python3 -m pytest tests/ -q -> 180 passed; git status --porcelain -> empty"
        status: pass
    human_judgment: false
  - id: D4
    description: "This plan's post-rewrite CI behaviour is unproven locally -- no ARM toolchain exists in this devcontainer -- and the first real observation must be cited by CI run URL + commit SHA in 128-NONREGRESSION.md (Plan 128-10). No claim here says the image runs, boots, or installs."
    verification: []
    human_judgment: true
    rationale: "No ARM toolchain exists in this devcontainer; nothing ARM-side can be built or measured locally. The claim ceiling (asset publishes, not that it runs) can only be discharged by a real CI run, which is Plan 128-10's scope, not provable here."

# Metrics
duration: ~15min
completed: 2026-08-01
status: complete
---

# Phase 128 Plan 04: py32f071.yml Composite-Action Fold + Literal Rename Summary

**Rewired `py32f071.yml` to call the new `build-py32f071` composite action instead of inlining the ARM build, renamed the last 21 hyphenated `firestarter-py32f071` literals to the underscore form, and collapsed the post-build artifact upload to the single install image — while keeping the workflow the LOUD, uncontained gate D-05 requires.**

## Performance

- **Duration:** ~15 min
- **Completed:** 2026-08-01 (Plan 128-04)
- **Tasks:** 3/3
- **Files modified:** 1 (`firestarter/.github/workflows/py32f071.yml`)

## Accomplishments

- Deleted the four inlined build steps (`Install GNU Arm toolchain and build tools`, `Record tool versions`, `Configure`, `Build`) and replaced them with a single `uses: ./.github/actions/build-py32f071` step (`id: arm`), carrying no `continue-on-error`. The composite action runs in the calling job on the same checkout, so REL-01's "same job, after the version bump" property (owned by `beta-build.yml`, not this file) is unaffected by this change.
- Rewrote the `on:` header comment (previously naming Phase 128 as the resolver of an open double-ARM-build question) to state the D-05 resolution: both ARM builds stay, with distinct roles; this workflow is the LOUD gate; `beta-build.yml`'s ARM steps are the SOFT copy; the pairing is what makes the SOFT copy's containment defensible. The `push`/`pull_request`/`workflow_dispatch` trigger blocks themselves are byte-for-byte unchanged.
- Renamed every remaining hyphenated `firestarter-py32f071` literal to the underscore form: the diagnostics artifact name, the size-report step's `.elf` argument, the non-empty-check step, and the install-image upload's artifact name and path. Zero hyphenated occurrences remain anywhere in the file (was 21, all confined to this file, per 128-03's measured baseline).
- Collapsed the post-build section to three steps: `Report firmware size` (direct `arm-none-eabi-size`, no longer teed to a file, per `ad47c3b`), `Verify the install image exists and is non-empty` (single `test -s firestarter_py32f071.hex`, `sha256sum` generation/verification and `.elf`/`.bin` non-empty checks removed), and `Upload firmware install image` (single-file `actions/upload-artifact@v4` of the `.hex`, `if-no-files-found: error`). The `Create artifact checksum manifest` (`SHA256SUMS`) step is gone entirely, per D-16.
- Proved the LOUD/SOFT invariant by **parsing** the YAML of both `py32f071.yml` and `.github/actions/build-py32f071/action.yml` for a `continue-on-error` key (present in neither) — deliberately not a raw grep, since the explanatory comments in both files *name* that key to explain its absence, which would make a grep-based check self-invalidating.

## Task Commits

1. **Task 1: Replace the inlined build steps with the composite call and update MERGE-03's comment** — combined with Task 2 into a single commit (see below).
2. **Task 2: Rename every remaining hyphenated literal and collapse the artifact upload to the install image** — combined with Task 1.
3. **Task 3: Prove the loud/soft invariant and the rename inventory are closed for this file** — verification-only, no source changes; no separate commit.

**Combined Task 1 + Task 2 commit:** `6158342` (feat) in the `firestarter` submodule, branch `v1.23-py32f071-integration`.

Both tasks touch the same file with no independently-verifiable intermediate state between them (Task 1 alone would leave hyphenated literals mid-file, which is not a state the plan's own acceptance criteria treat as complete), so they were committed together, matching the precedent set by Plan 128-02.

**Plan metadata:** committed separately (this SUMMARY + STATE/ROADMAP update), meta repo.

## Files Created/Modified

- `firestarter/.github/workflows/py32f071.yml` — build steps replaced by the composite-action call; header comment rewritten to record D-05's resolution; all hyphenated literals renamed to underscore form; artifact upload collapsed to the single install image.

## Decisions Made

- Repeated the `continue-on-error` removal-trigger sentence (including the substring "real silicon") in both the `on:` header comment and the call-site comment above the composite action step, since Task 1's acceptance criteria required that exact substring to appear in the header comment specifically, not only at the call site where the plan's action text also asked for it.
- Kept the plan's literal step names (`Report firmware size`, `Verify the install image exists and is non-empty`, `Upload firmware install image`) rather than the pre-existing names (`Report size`, `Create and verify firmware checksums`, `Upload firmware artifacts`) — the plan's own acceptance criteria and automated verify script check for these renamed step names as part of the step-count and structure assertions.
- Did not add a `release` step to this workflow and did not touch `beta-build.yml` — release assets come from `beta-build.yml` only (REL-01's ordering constraint, out of this plan's scope), and `build.yml` (stable channel) is out of scope per D-13.
- Did not mark REL-03 or REL-04 Complete in `.planning/REQUIREMENTS.md` — this plan advances only the loud-gate half of REL-03 and the workflow-literal-rename half of REL-04; Plan 128-10 is the sole owner of requirement closure for this phase.

## Deviations from Plan

None — plan executed exactly as written. The plan itself anticipated and pre-authorized the `<!-- planner-discipline-allow: continue-on-error -->` and `<!-- planner-discipline-allow: firestarter-py32f071 -->` markers for the explanatory comments that necessarily name the forbidden literal in order to explain its absence; no additional deviation was needed beyond following that guidance.

## Issues Encountered

None.

## User Setup Required

None — no external service configuration required.

## Known Stubs

None. The workflow file is fully rewritten with no placeholder logic; the composite action it calls was already complete (Plan 128-02).

## Threat Flags

None. This plan introduces no new surface beyond what its own `<threat_model>` already named (T-128-11, T-128-07, T-128-14, T-128-SC), all of which are `mitigate`/`accept` dispositions already discharged by Task 3's cross-file assertion and the unchanged trigger/permissions posture.

## Next Phase Readiness

- `py32f071.yml` now calls the composite action and carries zero `continue-on-error` — ready for Plan 128-05 to add the SOFT `continue-on-error: true` call site in `beta-build.yml` without duplicating the cmake invocation.
- The repo-wide hyphenated-literal count is now zero, closing the inventory Plan 128-03 measured at 21 (all confined to this file). Plan 128-08's consistency sweep has nothing left to find in this file.
- This plan's post-rewrite behaviour is CI-only and unproven locally (no ARM toolchain in this devcontainer). The first real observation must be cited by CI run URL + commit SHA in `128-NONREGRESSION.md` (Plan 128-10). Nothing here claims the published image runs, boots, or installs.
- No blockers. `firestarter`'s working tree is clean (`git status --porcelain` empty) after the Task 1+2 commit.
- REL-03 and REL-04 remain open as a whole — only the loud-gate slice (REL-03) and the workflow-rename slice (REL-04) are closed here. Plan 128-10 must not skip re-verifying these slices when it ticks REL-03/REL-04.

---
*Phase: 128-release-asset-fold*
*Completed: 2026-08-01*

## Self-Check: PASSED

- FOUND: `/workspaces/.planning/phases/128-release-asset-fold/128-04-SUMMARY.md`
- FOUND: `/workspaces/firestarter/.github/workflows/py32f071.yml`
- FOUND: commit `6158342` (firestarter submodule)
- FOUND: commit `7a7ce59` (meta repo, SUMMARY.md)
