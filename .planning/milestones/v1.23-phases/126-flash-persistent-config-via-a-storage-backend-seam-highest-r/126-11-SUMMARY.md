---
phase: 126-flash-persistent-config-via-a-storage-backend-seam-highest-r
plan: 11
subsystem: firmware-storage
tags: [py32f071, ci, arm, cmake, linker, gh-actions]

# Dependency graph
requires:
  - phase: 126-08
    provides: "The ARM manifest closed at 26 enforced sources (C-3's py32f071_hal_flash.c entry) and PR #48's config.cpp deleted -- this plan is the sole authoritative link-time proof of both"
  - phase: 126-06
    provides: "The reserved py32 flash map: MEMORY CONFIG region, D-13's zero-length BOOTLOADER seam, four PROVIDEd linker symbols, two structural ASSERTs"
provides:
  - "ARM CI evidence: run 30676982030 (workflow_dispatch, conclusion=success), head SHA 240fb19c50190797ffdc2062d39390e074f8566f string-equal to the local and origin firmware HEAD"
  - "Configure and Build steps independently re-derived as success (not merely an overall green conclusion) with per-step timestamps"
  - "Build-log proof that C-3's py32f071_hal_flash.c.obj was actually compiled ([37/42]) and linked ([42/42], firestarter-py32f071.elf produced, 27344/112/5888 text/data/bss) -- 42 objects vs Phase 125's 39 (the +3 being config_storage_dualslot.cpp, config_storage_flash.cpp, and the promoted rurp_config_utils.cpp)"
  - "Byte-for-byte confirmation that origin/v1.23-py32f071-integration's CMakeLists.txt and PY32F071xB_FLASH.ld match the local tree, and that platform/py32f071/src/config.cpp is absent from the pushed ref"
  - "Attestation that no task in this plan executed git push or gh workflow run -- the operator ran both personally, outside any executor agent"
affects: ["126-12 (the closing plan cites this evidence to tick CFG-05/CFG-06 alongside 126-07/126-08/126-09/126-10)"]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Structural push gate (Plans 124-11/125-05 shape): no task executes an outward-facing command; the plan prints it, stops at a checkpoint, and resumes only on a datum (run id/URL) that Task 3 re-derives read-only rather than trusts."
    - "Re-derivation discipline: every claimed CI fact (run id, head SHA, branch, event, conclusion, per-step outcome) is queried fresh via `gh run view --json` in-session, never transcribed from a relayed message; the pushed ref's file content is fetched and diffed byte-for-byte rather than assumed identical to local."

key-files:
  created: []
  modified: []

key-decisions:
  - "This plan's Task 2 (the operator gate) was already resolved before this executor was spawned: the operator personally ran `git push origin v1.23-py32f071-integration` and `gh workflow run py32f071.yml --ref v1.23-py32f071-integration`, and the orchestrator observed the resulting run. No task in this execution session ran either command -- the structural gate (T-126-11-01) held intact, and this plan's job was purely the read-only re-derivation Task 3 specifies."
  - "The Task 1 pre-push snapshot and Task 2's print-and-stop were executed retrospectively as evidence capture, not as a live gate stop, because the gate had already been satisfied by the time this plan was dispatched -- consistent with the framing given at dispatch time. All facts Task 1 would have recorded were independently re-captured in this session (branch, HEAD, porcelain, manifest counts, MEMORY block, PROVIDE symbols, pytest/native counts) rather than copied from a prior transcript."
  - "The A-7 linker fallback was NOT needed: the `MEMORY` block retains the original two-region shape (zero-length `BOOTLOADER` + `CONFIG`), and the ASSERT-based structural guards in `PY32F071xB_FLASH.ld` passed the ARM link cleanly -- confirmed by the absence of any linker diagnostic in the Build step log and by `[42/42] Linking CXX executable firestarter-py32f071.elf` succeeding. D-13's bootloader seam is unchanged (still zero-length, comment intact)."

requirements-completed: []  # CFG-05 spans 126-07/126-08/126-09; CFG-06 spans 126-06/126-08; this plan supplies the ARM evidence both requirements' claims rest on, but only 126-12 ticks CFG-01..CFG-07

coverage:
  - id: D1
    description: "ARM CI run independently re-derived read-only: run id, URL, head SHA, head branch, event, status, conclusion all queried fresh via `gh run view --json` and recorded as observations, not transcribed from a report"
    verification:
      - kind: other
        ref: "gh run view 30676982030 --repo henols/firestarter --json databaseId,headSha,headBranch,event,status,conclusion,jobs (this session)"
        status: pass
    human_judgment: false
  - id: D2
    description: "Configure and Build steps recorded BY NAME as independently success (not inferred from the overall conclusion); the one skipped step (Upload failed build diagnostics) explained as expected on a green run"
    verification:
      - kind: other
        ref: "gh run view --json jobs -> steps[4]=Configure(success), steps[5]=Build(success), steps[6]=Upload failed build diagnostics(skipped, if:failure())"
        status: pass
    human_judgment: false
  - id: D3
    description: "Head SHA compared string-equal against a freshly re-derived local HEAD and origin/v1.23-py32f071-integration, with both repos' branches recorded immediately before and after"
    verification:
      - kind: other
        ref: "git rev-parse HEAD == git rev-parse origin/v1.23-py32f071-integration == run.headSha == 240fb19c50190797ffdc2062d39390e074f8566f"
        status: pass
    human_judgment: false
  - id: D4
    description: "Pushed ref's CMakeLists.txt and linker script verified byte-for-byte against the local tree; config.cpp confirmed absent from the pushed ref"
    verification:
      - kind: other
        ref: "git diff origin/v1.23-py32f071-integration -- platform/py32f071/CMakeLists.txt (0 lines); git diff origin/v1.23-py32f071-integration -- platform/py32f071/linker/PY32F071xB_FLASH.ld (0 lines); git ls-tree origin/... -- platform/py32f071/src/config.cpp (empty)"
        status: pass
    human_judgment: false
  - id: D5
    description: "Build log proves the C-3 flash-driver entry and the two new ARM-only TUs actually reached the compiler and linker (42 objects, py32f071_hal_flash.c.obj at [37/42], link success at [42/42])"
    verification:
      - kind: other
        ref: "gh run view 30676982030 --log (Build step lines 344-486): [1/42]..[42/42] Linking CXX executable firestarter-py32f071.elf; text=27344 data=112 bss=5888"
        status: pass
    human_judgment: false
  - id: D6
    description: "Structural push gate held: no task in this plan executed git push or gh workflow run -- the operator ran both personally, outside any executor agent, before this plan was dispatched"
    verification: []
    human_judgment: true
    rationale: "Whether the structural separation genuinely held is an attestation about process (who ran which command, in which session) rather than something a single automated check can prove from artifacts alone; recorded here as a claim for a human/orchestrator to corroborate against the dispatch transcript, per this plan's own acceptance criteria."

duration: 30min
completed: 2026-08-01
status: complete
---

# Phase 126 Plan 11: ARM CI Evidence Behind the Structural Operator Gate Summary

**ARM CI run `30676982030` re-derived read-only end to end: Configure and Build each independently `success`, head SHA string-equal across run/local/origin, `py32f071_hal_flash.c.obj` proven compiled and linked at object 37 of 42, and the pushed CMakeLists.txt + linker script byte-for-byte identical to the local tree -- with the structural push gate intact (no task here ran `git push` or `gh workflow run`).**

## Performance

- **Duration:** ~30 min
- **Completed:** 2026-08-01
- **Tasks:** 3 (Task 1 pre-push snapshot, Task 2 operator gate, Task 3 re-derivation) -- all executed as read-only evidence capture; zero files modified
- **Files modified:** 0

## Context: the operator gate was already satisfied at dispatch time

This plan's design (Plans 124-11 / 125-05 shape) is: Task 1 records the pre-push state and prints the two outward-facing commands without running them; Task 2 is a `checkpoint:human-action` that stops for the operator to run them personally; Task 3 re-derives every fact about the resulting run read-only, accepting nothing on report.

**By the time this executor was dispatched, the operator had already personally run both commands, and the orchestrator had already observed the resulting CI run.** Per the dispatch instructions and the standing policy that no agent message is the operator's authorization or evidence, every fact the orchestrator reported was treated as a claim to be **independently re-derived, not accepted** -- exactly the discipline Task 3 specifies. This session performed that re-derivation from scratch: no cached values from the dispatch message were used as evidence; every figure below was queried fresh via `gh run view`, `git fetch`, `git diff`, and `git ls-tree` in this session.

**No task in this session executed `git push` or `gh workflow run`.** The structural gate (T-126-11-01) is unaffected by the fact that the underlying push/dispatch already happened prior to this session -- this executor did not perform them, and could not have, since the plan's tasks explicitly stop rather than run them.

## Accomplishments

- **Pre-push / current-state snapshot re-derived** (Task 1's content, captured live rather than from a prior transcript):
  - Firmware branch: `v1.23-py32f071-integration`; `HEAD` = `240fb19c50190797ffdc2062d39390e074f8566f`
  - `git status --porcelain` in `/workspaces/firestarter`: **0 lines**
  - Meta repo branch: `gsd/v1.23-py32f071-integration`; meta `git status --porcelain`: 1 pre-existing line (` M firestarter_app` gitlink pointer diff, unrelated to this plan)
  - This phase's 17 commits listed in order via `git log --oneline 2b5e8c8..240fb19` (fd84820 docs(126-01) through 240fb19 test(126-10)) -- full list recorded below
  - Manifest counts: `FIRESTARTER_COMMON_SOURCES` = **18**, `PY32_PLATFORM_SOURCES` = **8**, `PY32_SDK_SOURCES` = **15**, `PY32_EXCLUDED` = **5**; `grep -c hal_flash platform/py32f071/CMakeLists.txt` = **1**
  - `MEMORY` block and the four `PROVIDE`d symbols quoted verbatim (below); **A-7 fallback NOT in use** -- the original two-region shape (zero-length `BOOTLOADER` + `CONFIG`) is unchanged
  - `python3 scripts/check_cmake_manifest.py`: **PASS**, exit 0, "26 enforced source(s) resolved ... 15 PY32_SDK_SOURCES entries structurally exempt ... allow-listed omission(s): 5"
  - `python3 -m pytest tests/ -q`: **170 passed**
  - `pio test -e native` and `pio test -e native_nodevtools`: **141 test cases: 141 succeeded** each, **17 suites** each (re-counted via `grep -c` on the per-suite PASSED rows, not just the summary line)
  - `py32f071.yml`'s `on:` block confirmed: `push: branches: [beta]` (no `paths:` filter -- a push to `v1.23-py32f071-integration` does **not** trigger it), `pull_request` with a `paths:` filter over `platform/py32f071/**`/`include/**`/`src/**`/`lib/jsmn/**`/the workflow file itself, and `workflow_dispatch`. Job `build`'s step order: Check out repository -> Install GNU Arm toolchain and build tools -> Record tool versions -> **Configure** -> **Build** -> Upload failed build diagnostics (`if: failure()`) -> Report size -> Create and verify firmware checksums -> Create artifact checksum manifest -> Upload firmware artifacts.

- **The two outward-facing commands were already run by the operator, not by any task in this plan.** Their fully-expanded form (as they would have been printed by Task 1, and as the orchestrator confirmed were actually executed):
  ```
  git push origin v1.23-py32f071-integration
  gh workflow run py32f071.yml --ref v1.23-py32f071-integration
  ```
  Both ran in `/workspaces/firestarter` prior to this session. **No task in this plan's execution ran either command** -- confirmed by this session performing only read-only `gh run view`, `git fetch`, `git diff`, `git ls-tree`, `git status`, `git rev-parse` calls throughout.

- **The two anticipated failure modes (recorded per Task 1, neither of which occurred):**
  1. `undefined reference to HAL_FLASH_Unlock` (or `_Erase`/`_Program`/`_Lock`) -- C-3's manifest entry missing or misspelled. **Did not occur**: the build log shows `py32f071_hal_flash.c.obj` compiled cleanly at `[37/42]` and linked without any undefined-reference diagnostic.
  2. A diagnostic naming a line of `PY32F071xB_FLASH.ld` -- RESEARCH A-6 (the `ASSERT` forms) or A-7 (the two `MEMORY` regions sharing `ORIGIN = 0x08000000`). **Did not occur**: the link step (`[42/42] Linking CXX executable firestarter-py32f071.elf`) produced only a benign, pre-existing `sbrk.o: missing .note.GNU-stack section` warning from libc, and the size report printed cleanly. A-7's fallback (`PROVIDE(__bootloader_region_start ...)`/`PROVIDE(__bootloader_region_size ...)`) was **not needed** and was **not applied** -- D-13's named zero-length `BOOTLOADER` region is unchanged.

- **Run re-derived independently, read-only, in this session:**
  - Run id: **30676982030**; URL: `https://github.com/henols/firestarter/actions/runs/30676982030`
  - `event` = `workflow_dispatch`; `headBranch` = `v1.23-py32f071-integration`; `status` = `completed`; `conclusion` = `success`
  - `headSha` = `240fb19c50190797ffdc2062d39390e074f8566f`
  - Job `build`: `conclusion` = `success`. Per-step, **by name**, from the `jobs[].steps` array (not merely the overall conclusion): Set up job (success), Check out repository (success), Install GNU Arm toolchain and build tools (success), Record tool versions (success), **Configure (success)**, **Build (success)**, Upload failed build diagnostics (**skipped** -- expected: this step's condition is `if: failure()`, so a skip on a green run is corroborating, not concerning), Report size (success), Create and verify firmware checksums (success), Create artifact checksum manifest (success), Upload firmware artifacts (success), Post Check out repository (success), Complete job (success).

- **Head SHA comparison, performed fresh in this session (Task 1's value was not reused):**
  - `git rev-parse --abbrev-ref HEAD` (firmware, before fetch): `v1.23-py32f071-integration`
  - `git fetch origin v1.23-py32f071-integration` (read-only)
  - `git rev-parse origin/v1.23-py32f071-integration` = `240fb19c50190797ffdc2062d39390e074f8566f`
  - `git rev-parse HEAD` (firmware, re-derived, not Task 1's cached value) = `240fb19c50190797ffdc2062d39390e074f8566f`
  - `git rev-parse --abbrev-ref HEAD` (firmware, after fetch): `v1.23-py32f071-integration` -- unchanged
  - `git -C /workspaces rev-parse --abbrev-ref HEAD`: `gsd/v1.23-py32f071-integration` -- unchanged, checked both before and after
  - **Verdict: all three values (local `HEAD`, `origin/v1.23-py32f071-integration`, run's `headSha`) are string-equal.**

- **Pushed ref's content verified, not assumed, byte-for-byte:**
  - `git diff origin/v1.23-py32f071-integration -- platform/py32f071/CMakeLists.txt` -> **0 lines of diff** (identical)
  - `git diff origin/v1.23-py32f071-integration -- platform/py32f071/linker/PY32F071xB_FLASH.ld` -> **0 lines of diff** (identical)
  - `git ls-tree origin/v1.23-py32f071-integration -- platform/py32f071/src/config.cpp` -> **empty output** -- confirmed **absent** from the pushed ref (checked by inspecting command output, not exit code, since `git ls-tree` on a missing path still exits 0)

- **Build-log object-count and link proof** (fetched via `gh run view 30676982030 --log`, filtered to the `Build` step, lines 344-486 of the retrieved log):
  - `[1/42]` through `[42/42]` -- **42 total objects**, up from Phase 125's 39 (the +3: `config_storage_dualslot.cpp`, `config_storage_flash.cpp`, and the promoted `rurp_config_utils.cpp`)
  - `[37/42] Building C object .../py32f071_hal_flash.c.obj` -- **C-3's flash driver was actually compiled**, with one benign `unused parameter 'TypeProgram'` warning inside `HAL_FLASH_Program`, no errors
  - `[23/42]` and `[25/42]` show `src/config_storage_flash.cpp.obj` and `src/config_storage_dualslot.cpp.obj` compiling cleanly
  - `[42/42] Linking CXX executable firestarter-py32f071.elf` -- link succeeded; only warning is the pre-existing, benign `sbrk.o: missing .note.GNU-stack section implies executable stack` linker note (unrelated to this phase's changes)
  - Size report: `text=27344 data=112 bss=5888 dec=33344 hex=8240` for `firestarter-py32f071.elf`

## Task Commits

No files were modified by any task in this plan (`files_modified: []` per plan frontmatter, matched exactly -- `git status --porcelain` in `/workspaces/firestarter` is 0 lines throughout). There are no per-task commits in the firmware repo for this plan.

**Plan metadata:** this SUMMARY commit (docs, meta repo).

## Files Created/Modified

None. This plan is evidence-recording only, as specified (`files_modified: []`).

## Decisions Made

- **The operator gate (Task 2) was resolved prior to this session, by the operator personally, not by any executor agent.** This SUMMARY documents that as an observed fact rather than re-litigating the checkpoint: the structural separation this plan protects (no task runs `git push`/`gh workflow run`) held throughout this session, and every fact about the resulting run was independently re-derived rather than trusted.
- **The A-7 linker fallback was not needed and was not applied.** The `MEMORY` block, the four `PROVIDE`d symbols, and the two structural `ASSERT`s all passed the real ARM link cleanly. D-13's zero-length `BOOTLOADER` seam is unchanged.
- **No requirement checkbox was ticked.** `CFG-01`...`CFG-07` in `.planning/REQUIREMENTS.md` remain `[ ]` (verified via `grep -n "CFG-0[1-7]"` after this session's work) -- only Plan 126-12 may tick them.

## Deviations from Plan

None -- plan executed as specified, adapted only for the fact that the operator gate had already been satisfied at dispatch time (see "Context" section above), which the plan's own dispatch instructions anticipated and directed.

## Issues Encountered

- `gh run view --log` initially failed with `creating cache directory: mkdir /home/vscode/.cache/gh: permission denied`. Worked around read-only by setting `XDG_CACHE_HOME` to the session scratchpad directory for that single invocation -- no state was written outside the scratchpad, and no mutating command was involved.

## Non-Claims (Claim Ceiling, explicit)

A successful ARM CI run proves the ARM target **configures, compiles and links**, and that the two ARM-only constructs this phase introduced (C-3's flash-driver manifest entry and the linker script's new `MEMORY` regions/`PROVIDE`d symbols/`ASSERT`s) are accepted by the real toolchain. **It proves nothing about silicon**: no PY32F071 PCB exists, the pin map remains an explicitly provisional placeholder, config surviving a real DFU install is unverified, and first-boot flash-write timing (D-14) remains **not measured**, never *acceptable*. The **pytest** dual-slot harness (`tests/test_config_storage_dualslot.py` etc.) runs in **zero CI legs on this branch** -- `py32f071.yml` has no pytest step -- so it is discharged entirely by the in-phase local runs recorded in Plans 126-09/126-10 and re-confirmed here (170 passed); this ARM CI run proves the **build**, not the pytest suite, and the two claims are kept separate throughout this document.

## User Setup Required

None -- the operator had already performed the two outward-facing actions (push + workflow dispatch) prior to this session; no further external configuration is required for this plan.

## Next Phase Readiness

- The ARM evidence Plan 126-12 needs is now on the record: run `30676982030`, head SHA `240fb19c50190797ffdc2062d39390e074f8566f`, Configure and Build each independently `success`, the pushed ref verified byte-for-byte identical to the local tree, and C-3's flash driver proven compiled and linked via the build log's object list.
- No blockers, no unresolved gate, no A-7 fallback pending. Plan 126-12 can cite this SUMMARY directly for CFG-05/CFG-06's ARM-side evidence.
- `.planning/REQUIREMENTS.md` CFG-01...CFG-07 remain untouched (`[ ]`), as required -- Plan 126-12 owns ticking them.

---
*Phase: 126-flash-persistent-config-via-a-storage-backend-seam-highest-r*
*Completed: 2026-08-01*

## Self-Check: PASSED
- FOUND: /workspaces/.planning/phases/126-flash-persistent-config-via-a-storage-backend-seam-highest-r/126-11-SUMMARY.md
- No task commits to verify (plan is read-only evidence capture, files_modified: [])

