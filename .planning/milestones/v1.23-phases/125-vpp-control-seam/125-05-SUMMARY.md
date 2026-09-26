---
phase: 125-vpp-control-seam
plan: "05"
subsystem: firmware-ci
tags: [firestarter, py32f071, ci, arm, cmake, workflow-dispatch, operator-gate, continuation]

# Dependency graph
requires:
  - phase: 125-vpp-control-seam
    plan: "01"
    provides: "the landed seam (include/rurp_vpp.h, src/rurp_vpp.cpp, platform/py32f071/CMakeLists.txt naming + RURP_HAS_VPP_DAC=0) at commit fb76287, plus the seven pre-phase blob SHAs this plan re-asserts"
  - phase: 125-vpp-control-seam
    plan: "04"
    provides: "AVR-side Criterion 4 measurement (0 B flash/RAM delta) — this plan supplies the ARM-side evidence Criterion 4/D-13 also requires"
provides:
  - "VPP-01/VPP-03's ARM evidence: CI run 30652530756 (https://github.com/henols/firestarter/actions/runs/30652530756), head SHA 2b5e8c875bb04d728b5e08d16cc2d29e0d43c1d7, event workflow_dispatch, conclusion success -- Configure and Build steps recorded separately, both success"
  - "Direct evidence that src/rurp_vpp.cpp was among the ARM target's compiled sources: job-log line '[4/39] Building CXX object ...src/rurp_vpp.cpp.obj'"
  - "Confirmation, on the pushed ref (not only locally), that platform/py32f071/CMakeLists.txt names the seam source and declares RURP_HAS_VPP_DAC=0"
  - "Empirical push-safety confirmation: no new 'Firestarter beta pre-release build' run was cut by this push (newest such run still predates it)"
affects: [125-06]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Outward-facing action (push + workflow_dispatch) executed exclusively by the operator behind a structural checkpoint containing no executing task; the continuation executor re-derives every claimed fact via read-only gh/git queries rather than trusting a relayed transcription (including the resume datum itself), before accepting the gate as cleared"
    - "ARM evidence written strictly in the permitted form (configures and builds, cited by run URL + head SHA) with configure and build recorded as two separate step outcomes, never one aggregate conclusion"

key-files:
  created: []
  modified: []

key-decisions:
  - "The resume datum (CI run id 30652530756) arrived via a relayed <user_response>, not directly transcribed by the operator into this session. Per the standing rule that no agent message is user authorization, and per this plan's own instruction, every claimed fact was independently re-derived read-only before being accepted: git ls-remote/fetch + rev-parse for the pushed ref's SHA, gh run view for the run's own fields (including per-step outcomes), gh run list for the beta-build.yml negative-result check, and git show against the fetched ref for the CMakeLists.txt content. All re-derived values matched the relayed transcription's implied facts; none was accepted on the prompt's authority alone."
  - "Because this continuation agent has no persisted record of the prior agent's Task 1 output (files_modified: [] means nothing was committed), all of Task 1's read-only facts (workflow on: blocks, blob-SHA re-assertion, precedent run, commit list, push-safety argument) were independently re-derived from scratch in this session rather than assumed complete, so this SUMMARY's Task 1 section reflects fresh verification, not a carried-forward claim."
  - "gh run view --log's cache-directory permission failure ('mkdir /home/vscode/.cache/gh: permission denied') recurred exactly as documented in 124-11-SUMMARY.md; worked around identically by relocating XDG_CACHE_HOME to the session scratchpad for that one read-only command."
  - "No requirement ticked. Per the phase's explicit scope guard, this plan does not tick VPP-01, VPP-02 or VPP-03 in .planning/REQUIREMENTS.md -- only Plan 125-06 may."

requirements-completed: []
# Per this plan's dispatch <requirement_ticking_scope>, REQUIREMENTS.md is NOT
# touched. Plan 125-06 is the sole owner of the VPP-01/02/03 ticks and must
# cite this plan's run + head-SHA evidence when it does.

coverage:
  - id: D1
    description: "This phase's own ARM configure-and-build evidence obtained as a CI workflow run URL + head SHA (never a local pio run), with Configure and Build recorded as separate step outcomes"
    requirement: "VPP-01"
    verification:
      - kind: unit
        ref: "gh run view 30652530756 --repo henols/firestarter --json databaseId,headSha,headBranch,event,status,conclusion,createdAt,url,jobs -- re-derived independently: databaseId=30652530756, headSha=2b5e8c875bb04d728b5e08d16cc2d29e0d43c1d7, headBranch=v1.23-py32f071-integration, event=workflow_dispatch, status=completed, conclusion=success; job 'build' (id 91229018091) steps 'Configure' (#5) and 'Build' (#6) each individually status=completed/conclusion=success"
        status: pass
      - kind: unit
        ref: "Job log (fetched read-only via gh run view --job --log, XDG_CACHE_HOME workaround applied): Configure ends '-- Configuring done (34.7s)' / '-- Generating done (0.0s)' / 'Build files have been written to: .../build/py32f071'; Build ends '[39/39] Linking CXX executable firestarter-py32f071.elf' preceded only by compiler warnings (unused-parameter in third-party SDK files) and one linker note (missing .note.GNU-stack, deprecated), no errors"
        status: pass
    human_judgment: false
  - id: D2
    description: "The recorded head SHA is string-equal to the local firmware HEAD SHA and to the pushed ref origin/v1.23-py32f071-integration -- the run describes the landed tree, not a different one"
    requirement: "VPP-01"
    verification:
      - kind: unit
        ref: "git -C /workspaces/firestarter rev-parse HEAD = 2b5e8c875bb04d728b5e08d16cc2d29e0d43c1d7. git fetch origin v1.23-py32f071-integration:refs/remotes/origin/v1.23-py32f071-integration then git rev-parse origin/v1.23-py32f071-integration = 2b5e8c875bb04d728b5e08d16cc2d29e0d43c1d7. gh run view's headSha = 2b5e8c875bb04d728b5e08d16cc2d29e0d43c1d7. All three string-equal -- confirmed by direct comparison, not assumed."
        status: pass
    human_judgment: false
  - id: D3
    description: "src/rurp_vpp.cpp was among the ARM target's compiled sources, and the seam entry + capability define are present in platform/py32f071/CMakeLists.txt on the PUSHED ref"
    requirement: "VPP-01"
    verification:
      - kind: unit
        ref: "Job log line 354: '[4/39] Building CXX object CMakeFiles/firestarter-py32f071.elf.dir/home/runner/work/firestarter/firestarter/src/rurp_vpp.cpp.obj' -- direct evidence the new translation unit was compiled (39 total objects vs. Phase 124's 38, consistent with the one added source). git show origin/v1.23-py32f071-integration:platform/py32f071/CMakeLists.txt (fetched ref, not local working tree) shows line 42 '\"${REPOSITORY_ROOT}/src/rurp_vpp.cpp\"' in FIRESTARTER_COMMON_SOURCES and line 140 'RURP_HAS_VPP_DAC=0' in target_compile_definitions."
        status: pass
    human_judgment: false
  - id: D4
    description: "Push safety held empirically: the push created no new 'Firestarter beta pre-release build' run"
    requirement: "VPP-01"
    verification:
      - kind: unit
        ref: "gh run list --repo henols/firestarter --workflow beta-build.yml --limit 5 -- newest run is databaseId=30551682616, createdAt=2026-07-30T14:26:12Z, event=push, headBranch=beta -- predates this plan's push/dispatch (createdAt=2026-07-31T17:47:12Z on the py32f071.yml run). No beta-build.yml run exists at or after that timestamp."
        status: pass
    human_judgment: false
  - id: D5
    description: "No forbidden claim entered the record; the ARM statement is limited to 'configures and builds, cited by run URL + head SHA'"
    requirement: "VPP-01"
    verification:
      - kind: other
        ref: "This SUMMARY reread against REQUIREMENTS.md's Validation Ceiling forbidden-claim list before writing -- no statement made about firmware running on a PY32F071, any install working end to end, closed-loop VPP working, or pin-map correctness/verification/validation. ARM flash/RAM remain stated as not measured (no ARM size baseline exists; this run is not one)."
        status: pass
    human_judgment: true
    rationale: "Absence of a forbidden phrase is a textual property best confirmed by a human or a later automated scanner (Plan 125-06 runs one over the closing artifact); this plan's own re-read is the first check, not the last."

duration: ~20min (continuation session: Task 3 evidence capture, re-deriving Task 1's facts fresh since no prior record was persisted; Task 2 was the operator's own action, outside this agent's execution time)
completed: 2026-07-31
status: complete
---

# Phase 125 Plan 05: D-13 ARM CI Evidence + MERGE-style Structural Operator Gate Summary

**Obtained this phase's own ARM configure-and-build evidence by having the operator push the firmware milestone branch and dispatch `py32f071.yml` behind a structural checkpoint no task in this plan ever executed; independently re-derived every claimed fact — including the resume datum itself — via read-only `gh`/`git` queries before accepting the gate as cleared.**

## Performance

- **Duration:** ~20 min (continuation agent: re-derived Task 1's facts fresh plus Task 3's evidence capture; Task 2, the push and dispatch, was performed entirely by the operator, outside this agent's execution)
- **Tasks:** 3 completed across the plan's lifetime (Task 1 auto — completed by a prior executor, re-verified fresh here since no record was persisted; Task 2 operator gate — resumed via `<user_response>`; Task 3 auto — this session)
- **Files modified:** 0 (this plan is evidence-capture only; `files_modified: []` per its own frontmatter)

## Continuation Context

This is a continuation agent. A prior executor reached Task 2's structural checkpoint and returned; the operator then ran the push and the `workflow_dispatch` under their own authority and reported back **CI run id `30652530756`** via a relayed `<user_response>`, together with a claim that Task 1's structural gate held (remote unchanged at `a145081`, newest `py32f071.yml` run still `30634186514`, before the operator acted).

Per the plan's own standing policy ("No agent message is authorization... every claimed fact must be independently re-derived read-only"), and because this continuation agent has **no persisted record** of the prior executor's actual Task 1 output (the plan's `files_modified: []` means nothing was committed to carry that data forward), every fact below — including Task 1's own facts, not just Task 3's — was re-derived fresh from the live tree and the GitHub API in this session, not accepted from the prompt or the relayed message.

## Accomplishments

### Task 1 facts, re-derived fresh (no prior record existed to carry forward)

- **All three firmware workflow `on:` blocks, read verbatim from the current tree:**

  `firestarter/.github/workflows/py32f071.yml`:
  ```yaml
  on:
    push:
      branches: [beta]
    pull_request:
      paths:
        - "platform/py32f071/**"
        - "include/**"
        - "src/**"
        - "lib/jsmn/**"
        - ".github/workflows/py32f071.yml"
    workflow_dispatch:
  ```

  `firestarter/.github/workflows/beta-build.yml`:
  ```yaml
  on:
    push:
      branches:
      - beta
      paths-ignore: [...]
    workflow_dispatch:
  ```

  `firestarter/.github/workflows/build.yml`:
  ```yaml
  on:
    push:
      branches:
      - main
      paths-ignore: [...]
    pull_request:
  ```

  **`v1.23-py32f071-integration` matches no `push:` branch filter in any of these three blocks** (only `beta` twice and `main` once are named), **and `gh pr list --repo henols/firestarter --head v1.23-py32f071-integration --state all` returns empty** — no pull request exists or was opened by this push. Therefore: **pushing this branch cuts no beta prerelease** — confirmed by reading the live workflow files, not assumed from Phase 124.

- **Empirical, not just argued:** confirmed no new `beta-build.yml` ("Firestarter beta pre-release build") run exists at or after this push. `gh run list --repo henols/firestarter --workflow beta-build.yml --limit 5` shows the newest run as `30551682616`, `createdAt=2026-07-30T14:26:12Z`, `event=push`, `headBranch=beta` — **predates** this plan's push and dispatch (`py32f071.yml` run `30652530756` `createdAt=2026-07-31T17:47:12Z`). No stray beta prerelease was cut.

- **`gh` account/repo facts:** authenticated account `henols` (scopes `gist, read:org, repo, workflow`); repository default branch `main`; ARM workflow "PY32F071 firmware" id `316560577`, state `active` (from `gh workflow list`).

- **Phase 124's precedent run, explicitly distinguished:** `gh run view 30634186514` returns `headSha=a145081b59d94530583b9ce365db03ff567d0c2c`, `headBranch=v1.23-py32f071-integration`, `event=workflow_dispatch`, `conclusion=success`. This run describes the tree **before** this phase's seam landed — it is the empirical precedent for the dispatch mechanism working on this branch, but it is **not** evidence for VPP-01/VPP-03; this phase needed, and obtained, its own run.

- **Local firmware HEAD and commit list:** `git -C /workspaces/firestarter rev-parse HEAD` = `2b5e8c875bb04d728b5e08d16cc2d29e0d43c1d7`, branch `v1.23-py32f071-integration`, `git status --porcelain` = **0 lines** (firmware repo named explicitly — `firestarter_app`'s porcelain is separately non-empty at 5 lines, expected and out of scope, not chased). `git log --oneline a145081b59d94530583b9ce365db03ff567d0c2c..HEAD` lists the five commits this push fast-forwards:
  ```
  2b5e8c8 test(125-03): assert the seam diverges from PR #45's blobs and the gate cannot skip
  27b2f17 test(125-03): prove no PR #45 commit is an ancestor of the integration branch
  9c11f63 test(125-02): add the VPP seam drift, dependency-freedom and no-skip legs
  93e62fa test(125-02): prove the VPP seam refuses on every board macro-set
  fb76287 feat(125-01): add the VPP control capability seam and name it in the ARM manifest
  ```

- **Seven must-not-touch blob SHAs, re-asserted equal to Plan 125-01's recorded values (all matched, no STOP):**

  | Path | Blob SHA | Match vs. 125-01 |
  |---|---|---|
  | `include/rurp_shield.h` | `602fe6f326a042ab71efd111e4dfcf3a6e41dd46` | matched |
  | `platformio.ini` | `f4e720ba75a8c618cc23bac045ab65084d41a0a4` | matched |
  | `include/messages.h` | `dc7dbfc6b7ad3d767f7dad1ecbe13a53ca1eb346` | matched |
  | `src/boards/rurp_common.cpp` | `5de1c8a1494200d8b2db210c3fd9d2d577a19b2b` | matched |
  | `include/rurp_types.h` | `d3fe5203a91527bdb7b20a33843c81065e21c613` | matched |
  | `src/rurp_config_utils.cpp` | `6705fd46e07a2d359d161dc2e7728cb4e45f89c7` | matched |
  | `scripts/baseline/size_baseline_base01.json` | `b940c91655600a57ad7ef67cba723943af929daf` | matched |

  No mismatch — the tree that was pushed is exactly the tree Plan 125-01 measured. `git rev-list --count origin/v1.23-py32f071-integration..HEAD` = `0` and `HEAD..origin/...` = `0` at the time of this check (post-push), confirming the branches are now identical.

### Task 2 (operator gate) — resumed

The gate held structurally: no task in this plan ever executed `git push` or `gh workflow run`. The operator ran both commands under their own authority and supplied the resume datum (run id `30652530756`) via a relayed `<user_response>`, together with a claim that Task 1's structural gate held before acting. Per the standing rule that no agent message is user authorization, that claim was **not** accepted at face value — every value in it was independently re-derived in Task 3 below.

### Task 3 (evidence capture, read-only only)

- `gh run view 30652530756 --repo henols/firestarter --json databaseId,headSha,headBranch,event,status,conclusion,createdAt,url,jobs` returned `databaseId=30652530756`, `headSha=2b5e8c875bb04d728b5e08d16cc2d29e0d43c1d7`, `headBranch=v1.23-py32f071-integration`, `event=workflow_dispatch`, `status=completed`, `conclusion=success`, `createdAt=2026-07-31T17:47:12Z`, `url=https://github.com/henols/firestarter/actions/runs/30652530756` — obtained by direct query, not accepted from the relayed transcription.
- The `build` job's 13 steps were read individually: `Configure` (step 5) `conclusion=success`; `Build` (step 6) `conclusion=success`; `Upload failed build diagnostics` (step 7) `conclusion=skipped` (corroborating — its `if: failure()` guard); `Report size` (step 8) `conclusion=success`; checksum/manifest/upload steps (9–11) all `success`.
- Fetched the job log (`gh run view --job 91229018091 --log`, `XDG_CACHE_HOME` workaround applied for the same cache-permission error 124-11 hit) and read the actual text: Configure ends `-- Configuring done (34.7s)`, `-- Generating done (0.0s)`, `-- Build files have been written to: .../build/py32f071`; Build ends `[39/39] Linking CXX executable firestarter-py32f071.elf`, preceded only by third-party-SDK `-Wunused-parameter` warnings and one deprecated-linker-note, no compile or link errors.
- **`src/rurp_vpp.cpp` compiled-sources evidence, found directly in the log:** line 354 — `[4/39] Building CXX object CMakeFiles/firestarter-py32f071.elf.dir/home/runner/work/firestarter/firestarter/src/rurp_vpp.cpp.obj`. The ARM target's object count is **39**, one more than Phase 124's precedent run's **38** — consistent with exactly one new source being added since that tree. This is the fact assumption A1 needed measured, not reasoned: **confirmed present**, not absent.
- Compared the re-derived head SHA (`2b5e8c875bb04d728b5e08d16cc2d29e0d43c1d7`) against the independently re-derived local firmware HEAD (`2b5e8c875bb04d728b5e08d16cc2d29e0d43c1d7`) and against the independently fetched `origin/v1.23-py32f071-integration` (`2b5e8c875bb04d728b5e08d16cc2d29e0d43c1d7`) — **all three string-equal**, stated explicitly.
- Confirmed the seam entry and capability define on the **pushed ref**, not only locally: `git fetch origin v1.23-py32f071-integration:refs/remotes/origin/v1.23-py32f071-integration` followed by `git show origin/v1.23-py32f071-integration:platform/py32f071/CMakeLists.txt` shows `"${REPOSITORY_ROOT}/src/rurp_vpp.cpp"` in `FIRESTARTER_COMMON_SOURCES` (line 42) and `RURP_HAS_VPP_DAC=0` in `target_compile_definitions` (line 140), read back from the remote ref's fetched content.
- Confirmed empirically (not just by trigger-block argument) that this push cut no beta prerelease: newest `beta-build.yml` run (`30551682616`, `2026-07-30T14:26:12Z`, `push`, `beta`) predates this plan's push/dispatch timestamp.

## Observed Verification Values

**Independently re-derived run metadata (read-only `gh run view`):**

```json
{
  "conclusion": "success",
  "createdAt": "2026-07-31T17:47:12Z",
  "databaseId": 30652530756,
  "event": "workflow_dispatch",
  "headBranch": "v1.23-py32f071-integration",
  "headSha": "2b5e8c875bb04d728b5e08d16cc2d29e0d43c1d7",
  "status": "completed",
  "url": "https://github.com/henols/firestarter/actions/runs/30652530756"
}
```

**Head SHA equality (explicit statement):** local firmware HEAD = `2b5e8c875bb04d728b5e08d16cc2d29e0d43c1d7`. Independently fetched `origin/v1.23-py32f071-integration` = `2b5e8c875bb04d728b5e08d16cc2d29e0d43c1d7`. Independently re-derived run `headSha` = `2b5e8c875bb04d728b5e08d16cc2d29e0d43c1d7`. **All three strings are equal.** The run describes the tree that was actually pushed, carrying the seam — not Phase 124's earlier tree.

**Per-step outcomes (job `build`, id `91229018091`), read separately by name:**

| Step # | Name | Conclusion |
|---|---|---|
| 3 | Install GNU Arm toolchain and build tools | success |
| 5 | Configure | success |
| 6 | Build | success |
| 7 | Upload failed build diagnostics | skipped (corroborating — only runs on failure) |
| 8 | Report size | success |
| 9 | Create and verify firmware checksums | success |
| 10 | Create artifact checksum manifest | success |
| 11 | Upload firmware artifacts | success |

**Configure step log (tail):**
```
-- Configuring done (34.7s)
-- Generating done (0.0s)
-- Build files have been written to: /home/runner/work/firestarter/firestarter/build/py32f071
```

**Build step log (tail):**
```
[39/39] Linking CXX executable firestarter-py32f071.elf
/usr/lib/gcc/arm-none-eabi/13.2.1/.../ld: warning: sbrk.o: missing .note.GNU-stack section implies executable stack
/usr/lib/gcc/arm-none-eabi/13.2.1/.../ld: NOTE: This behaviour is deprecated ...
   text	   data	    bss	    dec	    hex	filename
  25796	    112	   5888	  31796	   7c34	.../build/py32f071/firestarter-py32f071.elf
```
No compile or link errors anywhere in the Build step's log — only third-party-SDK `-Wunused-parameter` warnings and one deprecated-linker-behavior note, neither in any file this phase touched.

**`src/rurp_vpp.cpp` compiled-sources evidence:**
```
[4/39] Building CXX object CMakeFiles/firestarter-py32f071.elf.dir/home/runner/work/firestarter/firestarter/src/rurp_vpp.cpp.obj
```
39 objects total, one more than Phase 124's 38 — consistent with the one new source this phase added. Recorded present, not assumed.

**Seam confirmed on the PUSHED ref (not locally):**
```
$ git -C /workspaces/firestarter fetch origin v1.23-py32f071-integration:refs/remotes/origin/v1.23-py32f071-integration
$ git -C /workspaces/firestarter show origin/v1.23-py32f071-integration:platform/py32f071/CMakeLists.txt
...
    "${REPOSITORY_ROOT}/src/rurp_vpp.cpp"      # (line 42, FIRESTARTER_COMMON_SOURCES)
...
        RURP_HAS_VPP_DAC=0                      # (line 140, target_compile_definitions)
```
Read back from the fetched **remote** ref, not the local working copy.

**Push-safety empirical confirmation (no new beta prerelease cut):**
```
$ gh run list --repo henols/firestarter --workflow beta-build.yml --limit 5 --json databaseId,headSha,headBranch,event,conclusion,createdAt
[{"databaseId":30551682616,"createdAt":"2026-07-30T14:26:12Z","event":"push","headBranch":"beta", ...}, ...]
```
Newest `beta-build.yml` run predates this plan's push/dispatch (`2026-07-31T17:47:12Z`). No new row exists at or after that timestamp.

**Seven blob SHAs, re-asserted equal to Plan 125-01's recorded pre-phase values (all matched):**
```
$ git -C /workspaces/firestarter hash-object include/rurp_shield.h platformio.ini include/messages.h \
    src/boards/rurp_common.cpp include/rurp_types.h src/rurp_config_utils.cpp \
    scripts/baseline/size_baseline_base01.json
602fe6f326a042ab71efd111e4dfcf3a6e41dd46
f4e720ba75a8c618cc23bac045ab65084d41a0a4
dc7dbfc6b7ad3d767f7dad1ecbe13a53ca1eb346
5de1c8a1494200d8b2db210c3fd9d2d577a19b2b
d3fe5203a91527bdb7b20a33843c81065e21c613
6705fd46e07a2d359d161dc2e7728cb4e45f89c7
b940c91655600a57ad7ef67cba723943af929daf
```

**Operational note:** `gh run view --job --log`'s default cache directory (`~/.cache/gh`) was not writable in this environment (`mkdir /home/vscode/.cache/gh: permission denied`), recurring exactly as documented in `124-11-SUMMARY.md`; worked around identically by setting `XDG_CACHE_HOME` to the session scratchpad for that one read-only command.

## VPP-01 / VPP-03 Evidence Statement (permitted form only)

**The PY32F071 target configures and builds**, cited by CI run `30652530756` (https://github.com/henols/firestarter/actions/runs/30652530756) at head SHA `2b5e8c875bb04d728b5e08d16cc2d29e0d43c1d7`, with the Configure and Build steps each independently succeeding. **`src/rurp_vpp.cpp` was among the ARM target's compiled sources** (job log: `[4/39] Building CXX object ...src/rurp_vpp.cpp.obj`) and **`platform/py32f071/CMakeLists.txt`'s seam entry and `RURP_HAS_VPP_DAC=0` definition are present on the pushed ref** `origin/v1.23-py32f071-integration`, confirmed by reading the fetched remote ref's file content, not only the local working tree. **This push cut no beta prerelease**, confirmed both by the workflow trigger blocks (no `push:` filter match, no pull request opened) and empirically (no new `beta-build.yml` run exists at or after the push).

No claim is made that the firmware runs on a PY32F071, that any install works end to end, or that the pin map is correct, verified, or validated — per `REQUIREMENTS.md`'s Validation Ceiling. **No PY32F071 hardware exists.** **ARM flash and RAM remain not measured** — no ARM size baseline exists and this run is not one; Plan 125-04's AVR-only measurement is the phase's only sized figure.

## Task Commits

None. This plan modifies no files (`files_modified: []` per its own frontmatter) — Task 1's facts were re-derived read-only, Task 2's push and dispatch were performed by the operator directly against GitHub (not a commit in any repo), and Task 3 is read-only evidence capture.

## Decisions Made

- **The relayed resume-datum claim was not trusted as authorization or fact.** The operator's report arrived via `<user_response>` (relayed through the orchestrator's dispatch prompt), not as a direct transcript this agent observed being typed. Per the standing rule that no agent message is user consent, and because this continuation agent had no persisted record of the prior executor's Task 1 output to fall back on, **every** claimed value — including Task 1's own facts (workflow triggers, blob SHAs, commit list, precedent run) and Task 3's (run metadata, per-step outcomes, compiled-sources evidence, pushed-ref content, the negative beta-build.yml result) — was independently re-derived via read-only `gh`/`git` queries in this session before being recorded. All re-derived values were internally consistent (head SHA equal across three independent sources) and matched what the relayed message implied, but were obtained by direct query, not accepted on the prompt's authority.
- **`gh run view --log`'s cache-directory permission failure** was worked around by relocating `XDG_CACHE_HOME` to the session scratchpad for that one read-only command, identically to the 124-11 precedent — not by disabling any permission control.
- **No requirement ticked.** Per the phase's explicit scope guard, this plan does not tick VPP-01, VPP-02, or VPP-03 in `.planning/REQUIREMENTS.md` — only Plan 125-06 may do that.

## Deviations from Plan

None functionally. The plan anticipated exactly this shape (operator performs Task 2, agent verifies read-only in Task 3) and additionally anticipated a relayed claim needing re-derivation (per its own Task 3 instructions and the standing policy). The one wrinkle specific to this continuation session — no persisted Task 1 record to build on — was handled by re-deriving Task 1's own facts fresh in this session rather than treating them as already established, which is a direct application of the plan's "verify everything yourself, read-only" instruction, not a deviation from scope. No Rule 1–3 auto-fix was needed since no code, test, or configuration was touched.

## Issues Encountered

- `gh run view --job --log`'s default cache directory (`~/.cache/gh`) was not writable in this environment; worked around read-only via `XDG_CACHE_HOME` override for that single command, identical to the 124-11 precedent. Not a defect in this plan's own artifacts.
- No persisted record of the prior (interrupted) executor's Task 1 output existed to consume, since `files_modified: []` meant nothing was committed to carry it forward. Resolved by re-deriving every Task 1 fact fresh in this session — see Deviations above.

## User Setup Required

None beyond the operator action this plan's Task 2 gate already required (which is now complete, independently confirmed).

## Requirement Ticking Scope

Per this plan's dispatch `<requirement_ticking_scope>`, `.planning/REQUIREMENTS.md` was **not** touched. What was proved: this phase's own ARM configure-and-build evidence (run `30652530756`, head SHA `2b5e8c875bb04d728b5e08d16cc2d29e0d43c1d7`, Configure and Build steps each independently `success`, `src/rurp_vpp.cpp` confirmed among the compiled sources) and the seam confirmed present on the pushed ref. Plan 125-06 owns citing this evidence when it ticks VPP-01/VPP-03.

## Claim Ceiling Compliance

This SUMMARY makes no claim that the firmware runs on a PY32F071, that closed-loop VPP works, that the pin map is correct/verified/validated, or an unqualified bench-validated/hardware-validated/silicon-verified claim. **No PY32F071 hardware exists.** The only ARM statement made is: the target configures and builds, cited by run URL and head SHA, with `src/rurp_vpp.cpp` confirmed compiled. ARM flash and RAM are stated as **not measured** — no ARM size baseline exists and this run is not one.

## Next Phase Readiness

- This phase's ARM evidence exists as a run URL + head SHA tied to the landed tree carrying the seam, with configure and build distinguished, and the new translation unit's compilation directly confirmed in the log — ready for Plan 125-06 to cite for VPP-01/VPP-03.
- The seam entry and `RURP_HAS_VPP_DAC=0` are confirmed present on `origin/v1.23-py32f071-integration`, not only the local working tree.
- The push cut no beta prerelease, confirmed both by trigger-block reading and by the empirical absence of any new `beta-build.yml` run.
- No forbidden claim entered this record (re-checked against `REQUIREMENTS.md`'s Validation Ceiling before writing).
- No blockers for Plan 125-06. Plan 125-05 is the last plan that could affect the firmware HEAD — 125-06 writes meta-repo artifacts only, so the head SHA cited here stays the branch tip.

---
*Phase: 125-vpp-control-seam*
*Completed: 2026-07-31*

## Self-Check: PASSED

- FOUND: `.planning/phases/125-vpp-control-seam/125-05-SUMMARY.md`
- Verified (read-only, re-derived independently): CI run `30652530756` exists, `headSha=2b5e8c875bb04d728b5e08d16cc2d29e0d43c1d7`, `conclusion=success`, `Configure`/`Build` steps each `success` — confirmed via `gh run view` and job log text, not trusted from the relayed `<user_response>`.
- Verified: `origin/v1.23-py32f071-integration`'s `platform/py32f071/CMakeLists.txt` carries the seam entry and `RURP_HAS_VPP_DAC=0` — confirmed via `git fetch` + `git show` against the remote ref.
- Verified: no new `beta-build.yml` run was cut by this push — confirmed via `gh run list`.
- No files created or modified by this plan (as expected per `files_modified: []`); no task commits exist to verify.
