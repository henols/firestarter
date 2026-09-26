---
phase: 128-release-asset-fold
plan: 08
subsystem: infra
tags: [github-actions, release-assets, softprops-action-gh-release, cmake, py32f071, documentation]

# Dependency graph
requires:
  - phase: 128-release-asset-fold (128-04, prior wave)
    provides: "the composite action .github/actions/build-py32f071/action.yml and the shipped py32f071.yml LOUD gate this README describes"
  - phase: 128-release-asset-fold (128-07, prior wave)
    provides: "the final shipped beta-build.yml shape: two-entry files: block, the fail_on_unmatched_files omission, and draft:/tag_name: wired to steps.mode.outputs.rehearsal"
provides:
  - "platform/py32f071/README.md `## Release integration` section, added in corrected form: the glob build/py32f071/firestarter_*.hex (never the ad47c3b literal), the real fail_on_unmatched_files mechanism (research F-1) replacing the superseded glob-vs-literal folklore, D-05's continue-on-error removal trigger recorded as a decision, D-13's build.yml graduation trigger, the rehearsal switch, and the claim ceiling"
  - "A repo-wide proof that the README's release-file entries equal the shipped beta-build.yml files: entries (mechanical, non-vacuous parity check)"
  - "A repo-wide proof that the hyphen-to-underscore rename (D-14) is grep-clean across CMakeLists, both workflow files, the composite action, and this README"
  - "Firmware working tree closure: this is the last firmware commit of Phase 128 (D-19) -- git status --porcelain is empty, HEAD recorded for Plan 128-09's precondition"
affects: [128-09, 128-10]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Correcting a superseded rationale in prose alongside a corrected code line, rather than leaving a right answer next to a wrong explanation (the C-5 shape from Phase 122)"

key-files:
  created: []
  modified:
    - firestarter/platform/py32f071/README.md

key-decisions:
  - "Added the `## Release integration` section in corrected form rather than editing in place -- 128-PATTERNS.md MISMATCH-1 confirmed the section did not exist in the shipped tree; it existed only inside the unmerged commit ad47c3b"
  - "Rewrote the glob-vs-literal justification entirely per research F-1: softprops/action-gh-release globs every files: entry alike via glob.sync(), and severity is decided purely by the fail_on_unmatched_files input (default false, never set); there is no glob-vs-literal distinction in the action's own code"
  - "Deleted ad47c3b's false claim that the underscore rename means the existing release glob 'needs no new pattern' -- a second files: entry was required and shipped in Plan 128-07"
  - "Recorded D-05's continue-on-error removal trigger and D-13's build.yml graduation trigger as decisions with stated triggers, not as suggestions"
  - "Did not mark REL-02 or REL-03 complete in REQUIREMENTS.md -- both are multi-plan requirements; Plan 128-10 is the sole owner of requirement closure for this phase"
  - "Task 2 required no README edit -- the parity check passed on first execution (README's two release-file entries already matched the shipped beta-build.yml files: entries exactly)"

patterns-established: []

requirements-completed: []  # REL-02 and REL-03 are multi-plan requirements. This plan documents the
                            # shipped mechanism and closes the D-14 consistency check; Plan 128-10 owns
                            # requirement closure for this phase (per the plan's explicit scope boundary).

coverage:
  - id: D1
    description: "README gains a `## Release integration` section, positioned immediately after `## Build` and before `## Hardware validation still required`, containing the glob (not the literal), the corrected fail_on_unmatched_files mechanism, D-05's and D-13's recorded triggers, the rehearsal switch, and the explicit publication-only claim ceiling"
    requirement: "REL-02"
    verification:
      - kind: unit
        ref: "python3 -c YAML/regex assertion (heading position, forbidden-phrase absence, required-substring presence, zero hyphenated occurrences) -- Task 1 automated verify, PASSED"
        status: pass
    human_judgment: false
  - id: D2
    description: "README's release-file entries provably equal the shipped beta-build.yml Release step's files: entries, with a non-vacuity guard on each parse"
    requirement: "REL-02"
    verification:
      - kind: unit
        ref: "python3 -c YAML-parse + regex-parse parity assertion -- Task 2 automated verify, PASSED (['.pio/build/**/firestarter_*.hex', 'build/py32f071/firestarter_*.hex'])"
        status: pass
    human_judgment: false
  - id: D3
    description: "The hyphen-to-underscore rename (D-14) is grep-clean repo-wide; occurrence counts recorded for the five named files"
    requirement: "REL-03"
    verification:
      - kind: unit
        ref: "grep -r 'firestarter-py32f071' --exclude-dir=.git . | wc -l == 0 -- PASSED"
        status: pass
    human_judgment: false
  - id: D4
    description: "Firmware working tree is clean after this plan's commit (D-19/F-16 precondition for Plan 128-09), with the resulting HEAD SHA recorded; pytest tests/ -q and both native envs pass unchanged"
    verification:
      - kind: unit
        ref: "git status --porcelain (empty); python3 -m pytest tests/ -q (180 passed); pio test -e native (141/141); pio test -e native_nodevtools (141/141)"
        status: pass
    human_judgment: false
  - id: D5
    description: "Whether the documented release mechanism (two-entry glob, AVR gate, rehearsal draft) actually behaves correctly on a real GitHub Actions run is unproven locally -- no dispatch may run from this plan (D-04)"
    verification: []
    human_judgment: true
    rationale: "No task in this plan may run git push or gh workflow run (D-04). First real observation happens on Plan 128-10's rehearsal runs A and B, cited by CI run URL + commit SHA in 128-NONREGRESSION.md. Nothing in this README claims the published image runs, boots, or installs -- no PY32F071 PCB exists."

# Metrics
duration: ~25min
completed: 2026-08-01
status: complete
---

# Phase 128 Plan 08: README Release-Integration Section (Corrected Form) + Rename Consistency Summary

**Added `platform/py32f071/README.md`'s `## Release integration` section in corrected form -- the shipped two-entry glob, the real `fail_on_unmatched_files` mechanism replacing superseded glob-vs-literal folklore, D-05/D-13's recorded decision triggers -- then mechanically proved README-to-workflow parity and repo-wide hyphen-to-underscore rename consistency, closing the firmware half of this phase.**

## Performance

- **Duration:** ~25 min
- **Completed:** 2026-08-01
- **Tasks:** 2/2
- **Files modified:** 1 (`firestarter/platform/py32f071/README.md`)

## Accomplishments

- **Task 1 — Added the `## Release integration` section in corrected form.** Verified live (as 128-PATTERNS.md MISMATCH-1 flagged) that the shipped README had no such section at all -- it existed only inside the unmerged commit `ad47c3b` -- so this was an addition, not an edit-in-place. Replaced the old outputs sentence (the sole existing line the section supersedes) with `ad47c3b`'s corrected version (ELF/BIN/HEX/map/size report, `.hex` the only published artifact) minus its final sentence, which falsely claimed the underscore rename meant the existing release glob "needs no new pattern" (MISMATCH-2). Wrote the new section describing what actually shipped: the composite-action rationale (a `workflow_call` reusable workflow would break REL-01's same-job ordering; a composite action does not), the exact two-entry `files:` block as shipped in Plan 128-07, the corrected `fail_on_unmatched_files` mechanism per research F-1 (the action globs every entry alike; severity comes solely from that input's default-`false` value, never from a glob-vs-literal distinction), D-05's `continue-on-error` removal trigger recorded as a decision (comes off when validated on real silicon; unreachable this milestone since no PCB exists), the AVR-assets gate in one sentence, the rehearsal switch with its `beta_version` requirement, D-13's `build.yml` graduation trigger, and the claim ceiling closing the section.
- **Task 2 — Proved README-to-workflow parity and rename consistency; no further edit needed.** Parsed the shipped `beta-build.yml`'s `Release` step `files:` block and the README's fenced release-file block independently, with a non-vacuity guard on each parse (asserting exactly two non-empty entries before comparing). Both resolved to the identical two-element sorted list `['.pio/build/**/firestarter_*.hex', 'build/py32f071/firestarter_*.hex']` -- the parity check passed on first execution, so no README correction was required by Task 2 itself. Ran the repo-wide grep for the hyphenated `firestarter-py32f071`: zero occurrences. Recorded the positive counterpart (underscored-form occurrence counts) in the table below.

## Task Commits

1. **Task 1: Add the Release integration section in corrected form** - `0de57da` (docs)
2. **Task 2: Prove README-to-workflow parity and repo-wide rename consistency** - no commit (verification-only; parity check passed on first execution, no README edit was triggered)

**Plan metadata:** committed in the meta-repo (`.planning/phases/128-release-asset-fold/128-08-SUMMARY.md`, `STATE.md`, `ROADMAP.md`).

## Files Created/Modified

- `firestarter/platform/py32f071/README.md` -- gained the `## Release integration` section (78 lines inserted, 1 line replaced), positioned immediately after `## Build` and before `## Hardware validation still required`. All other existing sections (`## Implemented`, `## Provisional example pin map`, `## Build`, `## Hardware validation still required`) are byte-identical to their pre-plan form -- `git diff` confirms it touches only the old outputs sentence's region and the new section.

## Rename-consistency occurrence table (D-14)

Repo-wide grep for the hyphenated form `firestarter-py32f071`: **0 occurrences** (was previously non-zero before Phase 128 landed; confirmed clean at this plan's HEAD).

| File | Underscored-form (`firestarter_py32f071`) occurrence count |
|------|---|
| `platform/py32f071/CMakeLists.txt` | 5 (`TARGET_NAME`, `-Wl,-Map=`, `BIN_FILE`, `HEX_FILE`, plus one more literal reference) |
| `.github/workflows/beta-build.yml` | 1 (the REL-04 filename-equality transcription's `EXPECTED=firestarter_py32f071.hex`) |
| `.github/workflows/py32f071.yml` | 5 (diagnostics artifact name, size report, non-empty check, artifact name, artifact path) |
| `.github/actions/build-py32f071/action.yml` | 0 -- **expected, not a gap**: the composite action resolves the emitted image via the glob `build/py32f071/firestarter_*.hex` (D-06's rename-resilience design), never a hardcoded literal, so it has no occurrence of the literal underscored board name to count |
| `platform/py32f071/README.md` | 2 (the load-bearing-underscore paragraph and the `## Release integration` section's prose) |

`ad47c3b`'s commit message claimed the rename was "grep-verified consistent" but was never built locally to confirm it; this table and the zero-hyphenated-occurrence grep are what make that claim real rather than asserted (D-14).

## Decisions Made

- Followed D-14/D-15's plan instructions exactly: re-applied `ad47c3b`'s README prose by hand in corrected form (not cherry-picked), with all three named defects fixed -- the literal-under-glob-prose slip (MISMATCH-3), the false "needs no new pattern" claim (MISMATCH-2), and the "consider `continue-on-error`" suggestion promoted to D-05's recorded decision with a stated trigger.
- Did not mark REL-02 or REL-03 complete in `REQUIREMENTS.md`, per the plan's explicit scope boundary. Both are multi-plan requirements; Plan 128-10 additionally needs run A's observed asset list (REL-02) and run B's observed cascade plus the LOUD gate (REL-03) before either can close.
- Task 2 made no README edit: the parity check between the README's documented release-file entries and the shipped `beta-build.yml`'s actual `files:` entries passed cleanly on first execution, because Task 1 had already transcribed the shipped block verbatim.

## Deviations from Plan

None -- plan executed exactly as written. Both tasks' automated verify scripts passed on first implementation; no auto-fixes were needed.

## Issues Encountered

None.

## Claim discipline (verbatim, per the plan's Task 2 instruction)

No ARM build was performed locally -- no ARM toolchain exists in this devcontainer -- so nothing in this plan or the README claims the published image runs, boots, or installs. The permitted claim is exactly one sentence wide: **the asset publishes.** Every ARM figure this milestone cites carries a CI run URL plus a commit SHA (see `128-06-SUMMARY.md` and `128-07-SUMMARY.md` for the cited runs).

## User Setup Required

None -- no external service configuration required. No CI dispatch occurred in this plan (that is Plan 128-10's scope, structurally gated per D-04).

## Known Stubs

None. The README section describes real, already-shipped mechanism (Plans 128-01 through 128-07) -- no placeholder prose, no forward-reference to unshipped behavior.

## Threat Flags

None. This plan's surface is documentation-only; all threats in its own `<threat_model>` (T-128-18, T-128-20, T-128-21, T-128-22) are mitigated exactly as designed -- the false `fail_on_unmatched_files` rationale is deleted and replaced with the correct mechanism (T-128-18), D-05's removal trigger is recorded as a decision alongside the no-PCB fact (T-128-20), D-13 keeps `build.yml` out of scope with its graduation trigger recorded, confirmed untouched by this plan's `git diff` (T-128-21), and the section ends with an explicit non-claim, present and verified by the automated check (T-128-22).

## Firmware-tree closure (D-19 / F-16)

This is the last firmware commit of Phase 128. After Task 1's commit:

- `git -C /workspaces/firestarter status --porcelain` -- **empty**.
- **HEAD SHA:** `0de57da3c9edfb40f86eee8b0964e0f1bcdd8559` (branch `v1.23-py32f071-integration`).
- `python3 -m pytest tests/ -q` -- **180 passed**, unchanged.
- `pio test -e native` -- **141/141 succeeded**, unchanged.
- `pio test -e native_nodevtools` -- **141/141 succeeded**, unchanged.

Plan 128-09's app-side test asserts this same tree is clean (`_git_porcelain(FW_ROOT) == ""`, research finding F-16) -- this precondition now holds.

## Next Phase Readiness

- Plan 128-09 (Wave 6) can now add the single app-repo commit -- the cross-repo test binding the emitted filename to the host's `asset_candidates()` -- against a clean, closed firmware tree at HEAD `0de57da`.
- Plan 128-10 (Wave 7) must cite this plan's README section when writing `128-NONREGRESSION.md`'s evidence, and must not skip re-verifying REL-02/REL-03's publication-mechanism and gate-call-site slices (already advanced across Plans 128-01, 128-04, 128-07, 128-08) when it ticks those requirements after its own rehearsal runs A and B.
- No blockers.

---
*Phase: 128-release-asset-fold*
*Completed: 2026-08-01*

## Self-Check: PASSED

- FOUND: `/workspaces/firestarter/platform/py32f071/README.md`
- FOUND: `/workspaces/.planning/phases/128-release-asset-fold/128-08-SUMMARY.md`
- FOUND commit `0de57da` (Task 1) in `firestarter`
- FOUND commit `bacf300` (SUMMARY.md) in the meta-repo
