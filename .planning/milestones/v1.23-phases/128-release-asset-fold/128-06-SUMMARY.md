---
phase: 128-release-asset-fold
plan: 06
subsystem: infra
tags: [github-actions, release-assets, cmake, fetchcontent, version-string, py32f071]

# Dependency graph
requires:
  - phase: 128-release-asset-fold (128-05, prior wave)
    provides: "beta-build.yml's arm call site (id: arm, contained), the Report a missing PY32F071 image step, steps.mode.outputs.rehearsal"
  - phase: 128-release-asset-fold (128-02, prior wave)
    provides: "the composite action's hex_path (glob-guarded, exactly-one-match) and sdk_sha (measured FetchContent path) outputs"
  - phase: 128-release-asset-fold (128-03, prior wave)
    provides: "the underscore-form firestarter_py32f071.hex filename and the 40-hex GIT_TAG pin in platform/py32f071/CMakeLists.txt"
provides:
  - "Assert the emitted asset filename (REL-04) step: hex_path basename == firestarter_py32f071.hex, labelled a TRANSCRIPTION (D-08(a))"
  - "Assert and log the resolved SDK commit SHA (REL-04) step: sdk_sha == GIT_TAG parsed from CMakeLists.txt, with the F-15-corrected rationale"
  - "Assert the py32 image carries the bumped VERSION (REL-01) step: strings-over-objcopy'd-image contains <version>:py32f071, keyed on steps.version.outputs.version, never tag_name"
affects: [128-07, 128-10]

# Tech tracking
tech-stack:
  added: []
  patterns: ["exit-code assertion over the published binary's strings output as REL-01 evidence, alongside (not instead of) a YAML step-order read"]

key-files:
  created: []
  modified:
    - firestarter/.github/workflows/beta-build.yml

key-decisions:
  - "Committed each of the three tasks separately (3 commits) by first reverting the whole-file edit with `git checkout -- <file>` and re-applying one step block at a time, since all three insertions land at the identical anchor point (immediately before `Resolve release target SHA`) and a single Edit naturally produces one combined diff. This matches 128-05's precedent of one commit per independently-verifiable step."
  - "Did not touch the Release step in any task, per the plan's explicit scope boundary — Plan 128-07 owns it."
  - "Referenced the actions/cache@v4 block as \"above\" rather than citing specific line numbers in the D-10 comment, since two prior insertions in this same plan already shift line numbers relative to 128-05's summary and a hardcoded number would go stale within this plan's own execution."

patterns-established: []

requirements-completed: []  # REL-01 and REL-04 are partial slices only in this plan; 128-10 is
                            # the sole owner of requirement closure for this phase.

coverage:
  - id: D1
    description: "Emitted asset basename (steps.arm.outputs.hex_path) is asserted string-equal to the transcribed literal firestarter_py32f071.hex, guarded against an empty hex_path, and labelled explicitly as a transcription whose real binding lives in the host repo's own test (D-08(b), Plan 128-09)"
    requirement: "REL-04"
    verification:
      - kind: unit
        ref: "python3 -c YAML-parse assertion (if==steps.arm.outcome=='success', env.HEX_PATH mapping, no ${{ in run body, set -euo pipefail, firestarter_py32f071.hex literal, basename + exit 1, immediately after the report step) -- see Task 1 automated verify"
        status: pass
    human_judgment: false
  - id: D2
    description: "Resolved SDK commit SHA (steps.arm.outputs.sdk_sha) is logged to $GITHUB_STEP_SUMMARY and asserted string-equal to the 40-hex GIT_TAG parsed from platform/py32f071/CMakeLists.txt, with independent non-vacuity guards (exit 2) on both sides before the exit-1 comparison, and the F-15-corrected rationale (no cache covers _deps) in the comment"
    requirement: "REL-04"
    verification:
      - kind: unit
        ref: "python3 -c YAML-parse assertion (if guard, env.SDK_SHA mapping, no ${{ in run body, GIT_TAG + CMakeLists.txt parse, two exit-2 non-vacuity guards, {40} hex quantifier, exit 1 on mismatch, GITHUB_STEP_SUMMARY append) -- see Task 2 automated verify; sed expression run locally against the real CMakeLists.txt yields exactly 0ed2f4b4d3391eccfd4491006a30295fd78e32c2"
        status: pass
    human_judgment: false
  - id: D3
    description: "The published image, converted back to a flat binary with arm-none-eabi-objcopy, is asserted (via strings + grep -Fq, not -Fqx) to contain the bumped VERSION string \"<version>:py32f071\", compared against steps.version.outputs.version and never tag_name, alongside (not replacing) Plan 128-05's YAML step-order evidence"
    requirement: "REL-01"
    verification:
      - kind: unit
        ref: "python3 -c YAML-parse assertion (if guard, env.EXPECTED_VERSION/HEX_PATH mapping, no ${{ in run body, arm-none-eabi-objcopy -I ihex -O binary, strings + grep -Fq present, grep -Fqx absent, ':py32f071' literal, 'tag_name' absent from run body, exit 2 on empty version + exit 1 on mismatch, immediately after Task 2's step) -- see Task 3 automated verify"
        status: pass
    human_judgment: false
  - id: D4
    description: "All three assertions run only on the ARM success path (no ARM toolchain exists in this devcontainer), so whether they actually fire correctly on a real py32f071 build -- including whether the strings/grep match ever finds the version literal in real .rodata layout -- is unproven locally"
    verification: []
    human_judgment: true
    rationale: "No task in this plan may build the ARM target or run CI (no arm-none-eabi toolchain locally, D-04 forbids any dispatch from this plan). First real observation happens on Plan 128-10's rehearsal run A, cited by CI run URL + commit SHA in 128-NONREGRESSION.md. Nothing in this plan claims the image runs, boots, or installs."

# Metrics
duration: ~15min
completed: 2026-08-01
status: complete
---

# Phase 128 Plan 06: Release-Job Assertions (Filename, SDK Pin, Bumped Version) Summary

**Added three exit-code assertions to `beta-build.yml`'s ARM success path — emitted-filename equality against a transcribed literal, SDK-pin equality against the declared 40-hex `GIT_TAG`, and a `strings`-over-the-published-image check for the bumped `VERSION` string — turning three of this phase's requirement claims from a human reading YAML/logs into exit codes.**

## Performance

- **Duration:** ~15 min
- **Completed:** 2026-08-01
- **Tasks:** 3/3
- **Files modified:** 1 (`firestarter/.github/workflows/beta-build.yml`)

## Accomplishments

- Added `Assert the emitted asset filename (REL-04)` immediately after `Report a missing PY32F071 image`, guarded `if: steps.arm.outcome == 'success'`. Compares `basename(steps.arm.outputs.hex_path)` against the literal `firestarter_py32f071.hex`, guarding against an empty `hex_path` first (A-7 non-vacuity). The comment labels this step explicitly as a **transcription** of `asset_candidates("py32f071")[0]` (`firestarter_app/firestarter/firmware.py:116-132`) — the real cross-repo binding lives in the host repo's own test (D-08(b), Plan 128-09), which this step does not perform and does not claim to.
- Added `Assert and log the resolved SDK commit SHA (REL-04)` immediately after that, guarded the same way. Parses the 40-hex `GIT_TAG` out of `platform/py32f071/CMakeLists.txt` via a `sed` expression anchored to a `GIT_TAG` line, asserts both the parsed pin and `steps.arm.outputs.sdk_sha` are non-empty 40-hex strings (exit 2 on either failure), then asserts they are equal (exit 1 on mismatch), echoing the resolved SHA to `$GITHUB_STEP_SUMMARY` on success. The comment carries F-15's corrected rationale verbatim: nothing caches `build/py32f071/_deps` (the `actions/cache@v4` block covers only `~/.cache/pip` and `~/.platformio/.cache`), so this is a per-release proof the existing pin was honoured, not a cache-substitution detector — and cites CI run `30676982030` as the measured provenance of the FetchContent source path.
- Added `Assert the py32 image carries the bumped VERSION (REL-01)` immediately after that, same guard. Asserts `steps.version.outputs.version` is non-empty (exit 2), converts the published `.hex` back to a flat binary with `arm-none-eabi-objcopy -I ihex -O binary`, and greps `strings` output for the literal `"<version>:py32f071"` (exit 1 if absent). Uses `grep -Fq`, deliberately not `-Fqx`, per Assumption A2 — `.rodata` packing on this target is unobserved, so a too-strict whole-line match could fail rehearsal run A for a reason unrelated to the property under test. Compares against `steps.version.outputs.version`, never `tag_name` (F-2) — D-03's rehearsal mode overrides `tag_name` by design, so a tag-equality assertion would be red on purpose. This assertion runs alongside Plan 128-05's YAML step-order evidence, not instead of it.
- `git diff HEAD~3 HEAD -- .github/workflows/beta-build.yml` shows insertions only across all three task commits; the `Release` step remains byte-identical to its pre-plan form.

## Task Commits

1. **Task 1: Assert the emitted asset filename equals the transcribed literal** - `3546091` (feat)
2. **Task 2: Assert and log the resolved SDK commit SHA against the declared GIT_TAG** - `0902bb3` (feat)
3. **Task 3: Assert the built image carries the bumped VERSION string (REL-01, mechanically)** - `4362cea` (feat)

All three commits are in the `firestarter` submodule, branch `v1.23-py32f071-integration`.

**Plan metadata:** committed separately (this SUMMARY + STATE/ROADMAP update), meta repo.

## Files Created/Modified

- `firestarter/.github/workflows/beta-build.yml` — gained three new steps between `Report a missing PY32F071 image` and `Resolve release target SHA`: the D-08(a) filename transcription check, the D-10 SDK-pin equality (with F-15's corrected rationale), and the F-9 mechanical VERSION-string check. No existing step reordered, modified, or deleted.

## Decisions Made

- **Committed each task separately by reverting and re-applying incrementally.** All three step insertions share the identical anchor point (immediately before `Resolve release target SHA`), so a single whole-file edit naturally produces one combined diff spanning all three. To preserve one-commit-per-independently-verifiable-task (matching 128-05's precedent), the file was reverted to its pre-plan state with `git checkout -- .github/workflows/beta-build.yml` (a sanctioned, file-scoped revert of only the change made in this same task, not a blanket reset) and each task's step block was re-applied and committed one at a time.
- **Referenced the `actions/cache@v4` block as "above" rather than by line number** in the D-10 comment, since Tasks 1 and 2 in this same plan shift the file's line numbers relative to each other; a hardcoded line reference would go stale within this plan's own execution.
- Did not touch the `Release` step in any task — Plan 128-07 owns it.
- Did not mark REL-01 or REL-04 Complete in `.planning/REQUIREMENTS.md` — this plan advances only the mechanical-assertion slice of each; Plan 128-10 is the sole owner of requirement closure for this phase, and REL-04 additionally needs the cross-repo binding (Plan 128-09).

## Deviations from Plan

None - plan executed exactly as written. All three tasks' automated verify scripts passed on the first implementation; no auto-fixes were needed beyond the plan's own prescribed content.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Known Stubs

None. All three steps are complete, functioning workflow steps with real assertion logic — no placeholder logic. Their actual runtime behavior on a real ARM build (does the filename really match, does the SDK SHA really resolve and match, does `strings` really find the version literal in real `.rodata` layout) is unproven locally — no ARM toolchain exists in this devcontainer and no dispatch may run from this plan (D-04) — but this is a stated, plan-scoped limitation, not a stub: the code paths are real and complete, and their live observation is deferred to Plan 128-10's rehearsal run A.

## Threat Flags

None. All new surface introduced here is already named in this plan's own `<threat_model>` and mitigated exactly as designed: T-128-03 (SDK-source substitution) by Task 2's equality + 40-hex non-vacuity guards, T-128-12 (unbound emitted-filename spoofing) by Task 1's transcription check, T-128-16 (stale-VERSION image under a fresh tag) by Task 3's `strings` assertion, T-128-17 (vacuous empty-equals-empty comparison) by every step's non-vacuity guard preceding its comparison, and T-128-01 (expression-into-shell injection) by exclusive `env:`-only passthrough with a `no ${{ in run body` assertion on every step.

## Next Phase Readiness

- All three ARM-success-path assertions are in place, immediately following Plan 128-05's report step and immediately preceding `Resolve release target SHA`.
- Plan 128-07 can now add the `check_release_assets.py` gate call, the two-entry `files:` block, and wire `draft:`/`tag_name:` to `steps.mode.outputs.rehearsal` in the `Release` step, which remains untouched here.
- Plan 128-09 still owns the actual cross-repo binding (the app-side three-way equality test) — Task 1's filename check here is explicitly only the firmware-side transcription half of D-08.
- Plan 128-10 must cite rehearsal run A's log for: the filename match actually firing, the SDK SHA actually resolving to `0ed2f4b4d3391eccfd4491006a30295fd78e32c2`, and the `strings`/`grep` match actually finding the version literal in real `.rodata` layout — none of this is proven here.
- No blockers. `firestarter`'s working tree is clean (`git status --porcelain` empty) after the three task commits; `python3 -m pytest tests/ -q` is 180 passed; `git diff HEAD~3 HEAD -- .github/workflows/beta-build.yml` shows insertions only.
- REL-01 and REL-04 remain open as a whole — only the mechanical-assertion slices are advanced here. Plan 128-10 must not skip re-verifying these slices when it ticks REL-01/REL-04, and must not close REL-04 without Plan 128-09's cross-repo binding also landing.

---
*Phase: 128-release-asset-fold*
*Completed: 2026-08-01*

## Self-Check: PASSED
- FOUND: `/workspaces/firestarter/.github/workflows/beta-build.yml`
- FOUND: commit `3546091` (firestarter submodule)
- FOUND: commit `0902bb3` (firestarter submodule)
- FOUND: commit `4362cea` (firestarter submodule)
- FOUND: `/workspaces/.planning/phases/128-release-asset-fold/128-06-SUMMARY.md`
