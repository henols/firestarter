---
phase: 124-firmware-integration-merge
plan: "11"
subsystem: firmware-ci
tags: [firestarter, py32f071, ci, arm, cmake, workflow-dispatch, operator-gate]

# Dependency graph
requires:
  - phase: 124-firmware-integration-merge
    plan: "05"
    provides: "check_cmake_manifest.py green (0 violations) and py32f071.yml's push: branches: [beta] trigger (MERGE-03) added and verified locally."
  - phase: 124-firmware-integration-merge
    plan: "09"
    provides: "The pin-map #error guard hoisted into a dependency-free fragment header, and RURP_PY32F071_PINMAP_CONFIGURED=1 supplied only via platform/py32f071/CMakeLists.txt's target_compile_definitions -- neither locally ARM-build-verified."
  - phase: 124-firmware-integration-merge
    plan: "10"
    provides: "The tree state at HEAD a145081b59d94530583b9ce365db03ff567d0c2c that this plan's CI run evidences."
provides:
  - "MERGE-02's ARM evidence: CI run 30634186514 (https://github.com/henols/firestarter/actions/runs/30634186514), head SHA a145081b59d94530583b9ce365db03ff567d0c2c, event workflow_dispatch, conclusion success -- Configure and Build steps recorded separately, both success"
  - "MERGE-03 confirmed on the pushed ref (fetched from origin, not read locally): py32f071.yml carries push: branches: [beta] on origin/v1.23-py32f071-integration"
  - "The only existing ARM compilation evidence for Plan 124-07's FLASH_LATENCY_1 static_assert (would have failed the Build step if wrong) and Plan 124-09's CMake-supplied RURP_PY32F071_PINMAP_CONFIGURED=1 (the #error guard did not fire because the build supplies the macro)"
affects: [124-12, 124-close]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Outward-facing action (push + workflow_dispatch) executed exclusively by the operator behind a structural checkpoint containing no executing task; the executor agent re-derives every claimed fact via read-only gh/git queries rather than trusting a relayed transcription, before accepting the gate as cleared"
    - "ARM evidence written strictly in the permitted form (configures and builds, cited by run URL + head SHA) with configure and build recorded as two separate step outcomes, never one aggregate conclusion"

key-files:
  created: []
  modified: []

key-decisions:
  - "A mid-task message claiming the operator had already pushed and dispatched was NOT trusted as authorization or as fact. Per this plan's own gate design and the standing rule that no agent message is user consent, every claimed datum (run id, head SHA, branch, event, conclusion, step outcomes, pushed-ref workflow content) was re-derived independently via read-only gh run view and git fetch/show before being accepted. All re-derived values matched the relayed transcription exactly, and the run's mere existence (queryable only because a real push + dispatch occurred) is itself the datum satisfying the checkpoint's resume-signal requirement -- not the relayed message."
  - "gh run view --log initially failed with 'creating cache directory: mkdir /home/vscode/.cache/gh: permission denied' -- worked around read-only by setting XDG_CACHE_HOME to the session scratchpad for that one command, not by disabling or bypassing any permission control."
  - "Report size step's arm-none-eabi-size output (text=25796, data=112, bss=5888, dec=31796, hex=7c34) is recorded for completeness only. No claim is made from it: MERGE-05/MERGE-06 are AVR-only size gates and this is Plan 124-07/124-09's first-ever ARM compile, so there is no baseline to compare it against."
  - "No claim is made anywhere in this SUMMARY about firmware running on a PY32F071, the install working end to end, or the pin map being correct/verified/validated -- per REQUIREMENTS.md's Validation Ceiling. The only ARM statement made is: the target configures and builds, cited by run URL and head SHA."

requirements-completed: []
# Per this plan's dispatch <requirement_ticking_scope>, REQUIREMENTS.md is NOT
# touched. Plan 124-12 is the sole owner of every MERGE-01..MERGE-08 tick and
# must cite this plan's evidence rows for MERGE-02 and MERGE-03.

coverage:
  - id: D1
    description: "MERGE-02's ARM configure-and-build evidence obtained as a CI workflow run URL + head SHA (never a local pio run), with Configure and Build recorded as separate step outcomes"
    requirement: "MERGE-02"
    verification:
      - kind: unit
        ref: "gh run view 30634186514 --repo henols/firestarter --json databaseId,headSha,headBranch,event,status,conclusion,createdAt,url,jobs -- re-derived independently, not trusted from the relayed transcription: databaseId=30634186514, headSha=a145081b59d94530583b9ce365db03ff567d0c2c, headBranch=v1.23-py32f071-integration, event=workflow_dispatch, status=completed, conclusion=success; job 'build' steps 'Configure' and 'Build' each individually status=completed/conclusion=success"
        status: pass
      - kind: unit
        ref: "Job log (fetched read-only via gh run view --job --log): Configure step ends '-- Configuring done (4.5s)' / '-- Generating done (0.0s)' / 'Build files have been written to: .../build/py32f071'; Build step ends '[38/38] Linking CXX executable firestarter-py32f071.elf' with only compiler warnings (no errors) before the linker completes -- both steps' own reported conclusion is success, corroborated by reading the actual log text, not inferred from conclusion alone"
        status: pass
    human_judgment: false
  - id: D2
    description: "The recorded head SHA is string-equal to the local firmware HEAD SHA recorded in Task 1 (a145081b59d94530583b9ce365db03ff567d0c2c) -- the run describes the landed tree, not a different one"
    requirement: "MERGE-02"
    verification:
      - kind: unit
        ref: "Task 1 recorded local HEAD via git rev-parse HEAD: a145081b59d94530583b9ce365db03ff567d0c2c. Task 3's independently re-derived gh run view headSha: a145081b59d94530583b9ce365db03ff567d0c2c. String-equal -- confirmed by direct comparison, not assumed."
        status: pass
    human_judgment: false
  - id: D3
    description: "MERGE-03 confirmed on the PUSHED ref (origin), not only in the local working tree"
    requirement: "MERGE-03"
    verification:
      - kind: unit
        ref: "git -C /workspaces/firestarter fetch origin v1.23-py32f071-integration && git show origin/v1.23-py32f071-integration:.github/workflows/py32f071.yml -- on: block read back from the fetched remote ref shows 'push: branches: [beta]' present, byte-identical to the local file Plan 124-05 committed"
        status: pass
    human_judgment: false
  - id: D4
    description: "No forbidden claim entered the record; the ARM statement is limited to 'configures and builds, cited by run URL + head SHA'"
    requirement: "MERGE-02"
    verification:
      - kind: other
        ref: "This SUMMARY reread against REQUIREMENTS.md's Validation Ceiling forbidden-claim list before writing -- no statement made about firmware running on PY32F071, the install working end to end, or pin-map correctness/verification/validation"
        status: pass
    human_judgment: true
    rationale: "Absence of a forbidden phrase is a textual property best confirmed by a human or a later automated scanner (Plan 124-12 runs one over the closing artifact); this plan's own re-read is the first check, not the last."

duration: ~20min (Task 1 + Task 3; Task 2 was the operator's own action, outside this agent's execution time)
completed: 2026-07-31
status: complete
---

# Phase 124 Plan 11: MERGE-02 ARM CI Evidence + MERGE-03 Confirmation Summary

**Obtained MERGE-02's ARM configure-and-build evidence by having the operator push the firmware milestone branch and dispatch `py32f071.yml`'s `workflow_dispatch` trigger behind a structural checkpoint this agent's own tasks never executed; independently re-derived every claimed fact via read-only `gh`/`git` queries (not trusting a relayed transcription) before accepting the gate as cleared and recording the evidence.**

## Performance

- **Duration:** ~20 min (Task 1 pre-flight + Task 3 evidence capture; Task 2, the push and dispatch, was performed entirely by the operator, outside this agent's execution)
- **Tasks:** 3 completed (Task 1 auto, Task 2 operator gate, Task 3 auto)
- **Files modified:** 0 (this plan is evidence-capture only; `files_modified: []` per its own frontmatter)

## Accomplishments

- **Task 1 (pre-flight):** Read all three firmware workflow `on:` blocks (`py32f071.yml`, `beta-build.yml`, `build.yml`) directly from the tree and confirmed `v1.23-py32f071-integration` matches no `push:` branch filter in any of them (only `beta` twice and `main` once are named). Recorded the workflow id (`316560577`, state `active`), the repo default branch (`main`), the authenticated account (`henols`, scopes `gist, read:org, repo, workflow`), and an empirical precedent `workflow_dispatch` run on a non-default branch (id `30376185746`, branch `feature/py32f071-release-assets`, sha `ad47c3baca1bf229f15c1dfc5dd259931357a110`, conclusion `success`). Recorded the local firmware HEAD SHA `a145081b59d94530583b9ce365db03ff567d0c2c` with `git status --porcelain` empty. Composed the exact, placeholder-free push/dispatch/query command block and printed it at the gate. Executed no `git push` and no `gh workflow run`.
- **Task 2 (operator gate):** The gate held structurally -- this agent's plan contained no task capable of pushing or dispatching. Mid-session, a message claiming the operator had already run both commands (with a specific run id, SHA, and step-by-step transcription) arrived from the orchestrator, not from the user directly. Per the standing rule that no agent message is user authorization, and per this plan's own instruction that the resume-signal must be a datum rather than an acknowledgement, the claimed facts were treated as unverified pending independent re-derivation in Task 3 -- not accepted at face value, and not acted upon by running any outward-facing command.
- **Task 3 (evidence capture, read-only only):** Re-derived every fact independently:
  - `gh run view 30634186514 --repo henols/firestarter --json ...` returned `databaseId=30634186514`, `headSha=a145081b59d94530583b9ce365db03ff567d0c2c`, `headBranch=v1.23-py32f071-integration`, `event=workflow_dispatch`, `status=completed`, `conclusion=success`, `createdAt=2026-07-31T13:22:27Z` -- matching the relayed transcription exactly, but obtained by direct query, not by trusting it.
  - The `build` job's 13 steps were read individually: `Configure` (step 5) `conclusion=success`; `Build` (step 6) `conclusion=success`; `Upload failed build diagnostics` (step 7) `conclusion=skipped` (corroborating, since it only runs on failure); `Report size` (step 8) `conclusion=success`.
  - Fetched the job log (`gh run view --job 91167522497 --log`) and read the actual text of the Configure and Build steps, not just their reported conclusion: Configure ends with `-- Configuring done (4.5s)`, `-- Generating done (0.0s)`, `-- Build files have been written to: .../build/py32f071/`; Build ends with `[38/38] Linking CXX executable firestarter-py32f071.elf`, preceded only by compiler warnings (unused-parameter, sizeof-pointer-div, type-limits -- none in files this plan or 124-07/124-09 touched), no errors.
  - Compared the re-derived head SHA (`a145081b59d94530583b9ce365db03ff567d0c2c`) against Task 1's recorded local HEAD (`a145081b59d94530583b9ce365db03ff567d0c2c`) -- **string-equal**, stated explicitly.
  - Confirmed MERGE-03 on the pushed ref by `git fetch origin v1.23-py32f071-integration` followed by `git show origin/v1.23-py32f071-integration:.github/workflows/py32f071.yml` -- the `on:` block read back from the **remote** ref (not the local working copy) shows `push: branches: [beta]` present.
  - Read the `Report size` step's output for completeness: `arm-none-eabi-size` reports `text=25796, data=112, bss=5888, dec=31796, hex=7c34` for `firestarter-py32f071.elf`. Recorded, not compared against any baseline -- MERGE-05/MERGE-06 are AVR-only and this is the ARM target's first-ever compile.

## Observed Verification Values

**Independently re-derived run metadata (read-only `gh run view`):**

```json
{
  "conclusion": "success",
  "createdAt": "2026-07-31T13:22:27Z",
  "databaseId": 30634186514,
  "event": "workflow_dispatch",
  "headBranch": "v1.23-py32f071-integration",
  "headSha": "a145081b59d94530583b9ce365db03ff567d0c2c",
  "status": "completed",
  "url": "https://github.com/henols/firestarter/actions/runs/30634186514"
}
```

**Head SHA equality (explicit statement):** Task 1 recorded local firmware HEAD = `a145081b59d94530583b9ce365db03ff567d0c2c`. Task 3 independently re-derived run headSha = `a145081b59d94530583b9ce365db03ff567d0c2c`. **These two strings are equal.** The run describes the landed tree at HEAD, not a different one.

**Per-step outcomes (job `build`, id `91167522497`), read separately by name:**

| Step # | Name | Conclusion |
|---|---|---|
| 5 | Configure | success |
| 6 | Build | success |
| 7 | Upload failed build diagnostics | skipped (corroborating -- only runs on failure) |
| 8 | Report size | success |
| 9 | Create and verify firmware checksums | success |
| 10 | Create artifact checksum manifest | success |
| 11 | Upload firmware artifacts | success |

**Configure step log (tail):**
```
-- Configuring done (4.5s)
-- Generating done (0.0s)
-- Build files have been written to: /home/runner/work/firestarter/firestarter/build/py32f071
```

**Build step log (tail):**
```
[38/38] Linking CXX executable firestarter-py32f071.elf
/usr/lib/gcc/arm-none-eabi/13.2.1/.../ld: warning: sbrk.o: missing .note.GNU-stack section implies executable stack
   text	   data	    bss	    dec	    hex	filename
  25796	    112	   5888	  31796	   7c34	.../build/py32f071/firestarter-py32f071.elf
```
No compile or link errors anywhere in the Build step's log -- only pre-existing `-Wunused-parameter`, `-Wsizeof-pointer-div`, and `-Wtype-limits` warnings in files unrelated to this milestone's changes.

**Report size step output:** `text=25796  data=112  bss=5888  dec=31796  hex=7c34  filename=build/py32f071/firestarter-py32f071.elf`. Recorded for completeness; not compared to any baseline (none exists -- this is the ARM target's first CI compile since the merge).

**MERGE-03 confirmed on the pushed ref (not locally):**
```
$ git -C /workspaces/firestarter fetch origin v1.23-py32f071-integration
$ git -C /workspaces/firestarter show origin/v1.23-py32f071-integration:.github/workflows/py32f071.yml
...
  push:
    branches: [beta]
  pull_request:
    ...
  workflow_dispatch:
```
Read back from the fetched `origin/v1.23-py32f071-integration` ref, byte-for-byte matching the local file Plan 124-05 committed.

**Operational note:** `gh run view --job --log` initially failed with `creating cache directory: mkdir /home/vscode/.cache/gh: permission denied`; retried with `XDG_CACHE_HOME` pointed at the session scratchpad for that one read-only command, which succeeded. No permission was bypassed -- this only relocated `gh`'s local cache directory for a read operation.

## Cross-references to Plans 124-07 and 124-09

- **Plan 124-07 (D-04, flash-latency correction):** `platform/py32f071/src/main.cpp` contains `static_assert(FLASH_LATENCY_1 != FLASH_ACR_LATENCY_1, ...)` immediately beside the corrected `HAL_RCC_ClockConfig(&clocks, FLASH_LATENCY_1)` call. Run `30634186514`'s Build step succeeding is the **only existing compilation evidence** that this `static_assert` and the corrected constant compile under the real ARM toolchain -- had the assertion's condition been false (i.e., had the correction been wrong or the constants collided), the Build step would have failed with a `static_assert` diagnostic. It did not. No ARM toolchain exists in this devcontainer, so this CI run is the sole mechanical check available, exactly as 124-07-SUMMARY.md's "Next Phase Readiness" anticipated.
- **Plan 124-09 (D-14, pin-map guard restructure):** `platform/py32f071/CMakeLists.txt`'s `target_compile_definitions` supplies `RURP_PY32F071_PINMAP_CONFIGURED=1`, the only place that macro is now defined. `include/boards/py32f071_pinmap_guard.h`'s `#error` guard, proven able to fire on all three arms by 124-09's host-preprocessor pytest, did **not** fire in this build -- exactly the expected behavior when the build supplies the macro. This run is the first ARM-toolchain confirmation that the CMake-supplied definition reaches the guard as intended; 124-09-SUMMARY.md's "Next Phase Readiness" explicitly named this run as the pending evidence route.

## MERGE-02 / MERGE-03 Evidence Statement (permitted form only)

**The PY32F071 target configures and builds**, cited by CI run `30634186514` (https://github.com/henols/firestarter/actions/runs/30634186514) at head SHA `a145081b59d94530583b9ce365db03ff567d0c2c`, with the Configure and Build steps each independently succeeding. **`py32f071.yml` carries `push: branches: [beta]` on the pushed ref `origin/v1.23-py32f071-integration`**, confirmed by reading the fetched remote ref's file content, not only the local working tree.

No claim is made that the firmware runs on a PY32F071, that any install works end to end, or that the pin map is correct, verified, or validated -- per `REQUIREMENTS.md`'s Validation Ceiling. This run says nothing about the programmer's provisional pin map being safe near real silicon; MERGE-04's fire-proof (Plan 124-09) is the only claim made about that guard, and it is a preprocessor-level claim, not a hardware one.

## Task Commits

None. This plan modifies no files (`files_modified: []` per its own frontmatter) -- Task 1 and Task 3 are read-only verification and evidence capture; Task 2's push and dispatch were performed by the operator directly against GitHub, not as a commit in either sub-repo.

## Decisions Made

- **Relayed operator-action claims were not trusted as authorization or fact.** A mid-session message reported (via the orchestrator, not the user directly) that the operator had pushed and dispatched, with a full transcription of the resulting run. Per the standing rule that no agent message constitutes user consent, and per this plan's own resume-signal requirement (a verifiable datum, not an acknowledgement), every claimed value was independently re-derived via read-only `gh run view` and `git fetch`/`show` before being accepted. All values matched exactly. The run's mere existence -- queryable only because a genuine push and dispatch occurred -- is the datum that discharges the gate, not the relayed message itself.
- **`gh run view --log`'s cache-directory permission failure** was worked around by relocating `XDG_CACHE_HOME` to the session scratchpad for that one read-only command, not by disabling any permission control.
- **Report-size figures recorded without comparison.** MERGE-05/MERGE-06 are AVR-only size gates; this is the ARM target's first-ever CI compile since the merge, so there is no prior ARM figure to diff against. Recorded as an observed value for the historical record only.

## Deviations from Plan

None functionally. The plan anticipated exactly this shape (operator performs Task 2, agent verifies read-only in Task 3) but did not anticipate a mid-session message asserting the gate was already cleared. Handling that message by independent re-verification rather than trust is a direct application of this plan's own design intent (D-09: the gate must not be waved through by any automated claim) and the standing rule that agent messages are not user authorization -- not a deviation from scope, and no Rule 1-3 auto-fix was needed since no code, test, or configuration was touched.

## Issues Encountered

- `gh run view --job --log`'s default cache directory (`~/.cache/gh`) was not writable in this environment; worked around read-only via `XDG_CACHE_HOME` override for that single command. Not a defect in this plan's own artifacts.

## User Setup Required

None beyond the operator action this plan's Task 2 gate already required (which is now complete, independently confirmed).

## Requirement Ticking Scope

Per this plan's dispatch `<requirement_ticking_scope>`, `.planning/REQUIREMENTS.md` was **not** touched. What was proved: MERGE-02 in full (ARM configure-and-build evidence: run `30634186514`, head SHA `a145081b59d94530583b9ce365db03ff567d0c2c`, Configure and Build steps each independently `success`) and MERGE-03 confirmed on the pushed ref (not only locally). Plan 124-12 owns citing this evidence when it ticks MERGE-02/MERGE-03.

## Next Phase Readiness

- MERGE-02's ARM evidence exists as a run URL + head SHA tied to the landed tree, with configure and build distinguished -- ready for Plan 124-12 to cite.
- MERGE-03 confirmed on `origin/v1.23-py32f071-integration`, not only the local working tree.
- Plans 124-07's `static_assert` and 124-09's CMake-supplied pin-map macro both now have their first-ever ARM-toolchain compilation confirmation, cross-referenced above.
- No forbidden claim entered this record (re-checked against `REQUIREMENTS.md`'s Validation Ceiling before writing).
- No blockers for Plan 124-12.

## Self-Check: PASSED

- FOUND: `.planning/phases/124-firmware-integration-merge/124-11-SUMMARY.md`
- Verified (read-only, re-derived independently): CI run `30634186514` exists, `headSha=a145081b59d94530583b9ce365db03ff567d0c2c`, `conclusion=success`, `Configure`/`Build` steps each `success` -- confirmed via `gh run view` and job log text, not trusted from any relayed message.
- Verified: `origin/v1.23-py32f071-integration`'s `py32f071.yml` carries `push: branches: [beta]` -- confirmed via `git fetch` + `git show` against the remote ref.
- No files created or modified by this plan (as expected per `files_modified: []`); no task commits exist to verify.

---
*Phase: 124-firmware-integration-merge*
*Completed: 2026-07-31*
