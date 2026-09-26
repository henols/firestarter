---
phase: 125-vpp-control-seam
plan: 01
subsystem: firmware
tags: [c, cpp, cmake, platformio, preprocessor, capability-macro, avr, arm, py32f071]

# Dependency graph
requires:
  - phase: 124-firmware-integration-merge
    provides: "the merged v1.23-py32f071-integration firmware tree (HEAD a145081), the ARM CMake manifest gate (check_cmake_manifest.py), the D-14 build-supplies-the-macro pattern this plan reapplies"
provides:
  - "include/rurp_vpp.h — VPP control capability header: RURP_HAS_VPP_DAC resolved in exactly two arms (__AVR__ -> 0 permanent, else -> #error), two 2-value enums, three extern \"C\" function declarations"
  - "src/rurp_vpp.cpp — dependency-free refusal-shaped implementation, with a second #error guard for the forced-DAC case, scoped to this branch"
  - "platform/py32f071/CMakeLists.txt named the new source (16->17 FIRESTARTER_COMMON_SOURCES entries) and declared RURP_HAS_VPP_DAC=0 (8th target_compile_definitions entry)"
  - "the pre-phase pin: seven blob SHAs, CONFIG_VERSION line, manifest gate count, pytest count, native suite counts — all recorded and matched"
  - "measured, non-vacuous proof that the seam costs 0 B flash / 0 B RAM on all three AVR targets and does not move either pinned native suite"
affects: [125-02, 125-03, 125-04, 125-05, 125-06]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Build-system-supplies-the-macro, header-only-tests (Phase 124 D-14 lesson applied before authoring rather than after a defect): RURP_HAS_VPP_DAC is never defined in include/rurp_vpp.h for a non-AVR target; platform/py32f071/CMakeLists.txt's target_compile_definitions is its only non-AVR source."
    - "Two independently-authored #error guards for one capability macro: the header's !defined arm and the .cpp's forced-value arm are separate directives, because a header-only guard cannot reject an explicitly-forced value (measured, RESEARCH C-4)."

key-files:
  created:
    - firestarter/include/rurp_vpp.h
    - firestarter/src/rurp_vpp.cpp
  modified:
    - firestarter/platform/py32f071/CMakeLists.txt

key-decisions:
  - "Operator Option A on RESEARCH C-1: include/rurp_shield.h is NOT touched by this phase — no #include line anywhere. Confirmed both new native suite counts stay at 141/17 and the pinned #include line described in earlier CONTEXT/ROADMAP prose is superseded."
  - "The header alone cannot satisfy D-03's forced-DAC leg (measured: -DRURP_HAS_VPP_DAC=1 exits 0 with only the header's guard) — a second #error was authored in src/rurp_vpp.cpp, scoped to \"this branch\" per RESEARCH C-17 rather than a universal claim, because origin/feature/py32f071-full-support (PR #47, closed) genuinely implements a DAC with RURP_HAS_VPP_DAC=1."
  - "__AVR__ used as the AVR predicate, not the tree's own RURP_PLATFORM_AVR, because that macro is derived from __AVR__, never defined during an AVR build, and its header carries an unreachable-escape #error (RESEARCH C-13) — recorded in the header comment so a later phase does not \"improve\" the predicate."
  - "Requirement ticking scope: NONE. VPP-01 and VPP-03 appear in this plan's frontmatter as contributing evidence only; per the phase's explicit guard (against the Phase-116 4x premature-tick pattern), no requirement checkbox in .planning/REQUIREMENTS.md was ticked by this plan. Only Plan 125-06 may tick VPP-01/02/03."

requirements-completed: []  # Deliberately empty — this plan contributes evidence toward VPP-01/VPP-03 but does not discharge them; only 125-06 ticks requirement checkboxes (phase-specific guard against premature multi-plan ticking, Phase 116 precedent).

coverage:
  - id: D1
    description: "include/rurp_vpp.h and src/rurp_vpp.cpp exist as two hand-authored files (nothing cherry-picked from PR #45), with RURP_HAS_VPP_DAC resolved by exactly two arms and no blanket default"
    verification:
      - kind: manual_procedural
        ref: "grep -n '^\\s*#\\s*error\\s' include/rurp_vpp.h src/rurp_vpp.cpp (one directive per file); manual g++ compile-and-run across 4 legs (see Manual Compile Legs below)"
        status: pass
    human_judgment: false
  - id: D2
    description: "platform/py32f071/CMakeLists.txt names the seam in FIRESTARTER_COMMON_SOURCES (16->17) and declares RURP_HAS_VPP_DAC=0; check_cmake_manifest.py exits 0 at 24 enforced sources"
    verification:
      - kind: other
        ref: "python3 scripts/check_cmake_manifest.py (PASS, 24 enforced sources)"
        status: pass
    human_judgment: false
  - id: D3
    description: "Both pinned native environments (native, native_nodevtools) still report 141 test cases / 17 suites, all succeeded; native_pinmap_provisional stays 10/1; all three AVR targets rebuild at exactly their pre-phase flash/RAM figures (0 B delta)"
    verification:
      - kind: integration
        ref: "pio test -e native / -e native_nodevtools / -e native_pinmap_provisional; pio run -e uno/-e uno328pb/-e leonardo + avr-size + avr-nm symbol-absence check"
        status: pass
    human_judgment: false
  - id: D4
    description: "Every file this phase must not touch (src/boards/rurp_common.cpp, include/rurp_types.h, src/rurp_config_utils.cpp, include/rurp_shield.h, platformio.ini, include/messages.h, scripts/baseline/size_baseline_base01.json) still hashes to its pre-phase blob SHA"
    verification:
      - kind: unit
        ref: "git hash-object <7 paths>, pre- and post-commit"
        status: pass
    human_judgment: false

duration: 55min
completed: 2026-07-31
status: complete
---

# Phase 125 Plan 01: VPP Control Seam — Atomic Landing Summary

**Hand-authored `include/rurp_vpp.h` + `src/rurp_vpp.cpp` capability seam (RURP_HAS_VPP_DAC, two enums, three functions) landed in the ARM manifest in one firmware commit, with the C-1 native tripwire fired in-task and measured at 0 B flash/RAM delta on all three AVR targets.**

## Performance

- **Duration:** ~55 min
- **Completed:** 2026-07-31
- **Tasks:** 2 (Task 1 read-only pin recording; Task 2 authoring + landing)
- **Files modified:** 3 (2 new, 1 modified) in the firmware submodule; 1 new (this SUMMARY) in the meta repo

## Accomplishments

- Recorded the pre-phase pin: firmware branch `v1.23-py32f071-integration` at HEAD `a145081b59d94530583b9ce365db03ff567d0c2c`, zero-line porcelain (named explicitly to the firmware repo), seven blob SHAs (all matched RESEARCH's recorded expectations exactly), `CONFIG_VERSION "VER06"` at line 46, manifest gate PASS at 23 enforced sources, `pytest tests/` at 72 passed, and native envs at their recorded 141/17, 141/17, 10/1.
- Authored `include/rurp_vpp.h`: `#pragma once`, one `<stdint.h>` include, a capability guard resolving `RURP_HAS_VPP_DAC` in exactly two arms (`__AVR__` defined → `0`, permanent per operator fact D-05; else → a single named `#error`), two 2-enumerator enums, three `extern "C"` function declarations, and no fourth declaration.
- Authored `src/rurp_vpp.cpp`: MIT banner byte-identical to `src/proms/not_implemented.cpp`'s, only include is `"rurp_vpp.h"`, a second separately-authored `#error` scoped to "this branch" (not a universal claim — `origin/feature/py32f071-full-support` genuinely implements a DAC), and three trivial refusal bodies.
- Edited `platform/py32f071/CMakeLists.txt`: named `src/rurp_vpp.cpp` in `FIRESTARTER_COMMON_SOURCES` (16→17 entries, placed among the top-level `src/*.cpp` entries before the `src/proms/` group) and added `RURP_HAS_VPP_DAC=0` as the eighth `target_compile_definitions` entry, extending the existing comment block in place rather than writing a second one.
- Did **not** touch `include/rurp_shield.h` or `platformio.ini` — operator Option A on RESEARCH C-1. Fired the tripwire in this task: both pinned native environments report exactly `141 test cases: 141 succeeded` across 17 suites, and `native_pinmap_provisional` reports `10 test cases: 10 succeeded` across 1 suite.
- Landed all three edits as **one** firmware commit (`fb76287`) — `git show --stat` lists exactly three changed paths.
- Hand-proved the five specified compile/run behaviours before committing (see below), including a real `pio run -e uno` build proving the seam's `.o` compiles and its symbols are absent from the linked ELF while five unrelated pre-existing `vpp` symbols remain (proving the absence grep is not vacuous).

## Task Commits

Task 1 was read-only (evidence capture) — no files modified, no commit in the firmware repo.

1. **Task 2: Author the seam and name it in the ARM manifest** — `fb76287` (feat, firmware repo `/workspaces/firestarter`)

**Plan metadata:** meta-repo commit for this SUMMARY + STATE.md + ROADMAP.md (see final commit below).

## Files Created/Modified

- `firestarter/include/rurp_vpp.h` — VPP control capability header (new)
- `firestarter/src/rurp_vpp.cpp` — VPP control capability implementation (new)
- `firestarter/platform/py32f071/CMakeLists.txt` — named the seam source + added the `RURP_HAS_VPP_DAC=0` compile definition (modified, 2 logical edits)

## Pre-Phase Pin (Task 1, recorded before any file moved)

- **Firmware repo, named explicitly:** branch `v1.23-py32f071-integration`, HEAD `a145081b59d94530583b9ce365db03ff567d0c2c`, `git status --porcelain` = **0 lines**.
- **Seven blob SHAs — all matched RESEARCH's recorded pre-phase values exactly:**

| Path | Blob SHA | Match |
|---|---|---|
| `src/boards/rurp_common.cpp` | `5de1c8a1494200d8b2db210c3fd9d2d577a19b2b` | ✅ matched |
| `include/rurp_types.h` | `d3fe5203a91527bdb7b20a33843c81065e21c613` | ✅ matched |
| `src/rurp_config_utils.cpp` | `6705fd46e07a2d359d161dc2e7728cb4e45f89c7` | ✅ matched |
| `include/rurp_shield.h` | `602fe6f326a042ab71efd111e4dfcf3a6e41dd46` | ✅ matched |
| `platformio.ini` | `f4e720ba75a8c618cc23bac045ab65084d41a0a4` | ✅ matched |
| `include/messages.h` | `dc7dbfc6b7ad3d767f7dad1ecbe13a53ca1eb346` | ✅ matched |
| `scripts/baseline/size_baseline_base01.json` | `b940c91655600a57ad7ef67cba723943af929daf` | ✅ matched |

No STOP finding — the tree is exactly the tree RESEARCH measured.

- **`CONFIG_VERSION`** — `include/rurp_shield.h:46`: `#define CONFIG_VERSION "VER06"` (verbatim, literal `VER06`).
- **Manifest gate (pre-phase):** `python3 scripts/check_cmake_manifest.py` → PASS, **23** enforced sources, exit 0.
- **`pytest tests/` (pre-phase):** **72 passed** in 3.39s.
- **Native envs (recorded baseline, from `scripts/baseline/size_baseline.json`, not a fresh measurement at this point):** `native` 141 cases / 17 suites / all_passed; `native_nodevtools` 141 cases / 17 suites / all_passed; `native_pinmap_provisional` 10 cases / 1 suite / all_passed.

## The Two `#error` Messages, As They Appear In The Two Files

- `include/rurp_vpp.h:66` — `"RURP_HAS_VPP_DAC must be supplied by the board/platform build (for py32f071: platform/py32f071/CMakeLists.txt's target_compile_definitions), not by this header."`
- `src/rurp_vpp.cpp:21` — `"RURP_HAS_VPP_DAC=1 selects a closed-loop VPP DAC implementation that this branch does not provide"`

Each file contains exactly one `#error` directive (verified with `grep -n '^\s*#\s*error\s'`); the mentions of the bare word "#error" inside the header's prose comment (describing `rurp_platform.h`'s own unrelated terminal `#error`) are never followed by a quoted string, so a `#error\s+"([^"]*)"` regex reader (the mechanism Plan 125-02 uses) matches only the two real directives above.

## Manual Compile Legs (hand-proved before committing, per the task's mandatory step)

Built a scratch `main.cpp` (`printf("mode=%d result=%d\n", ...)`, matching RESEARCH's prototype shim) in the scratchpad directory and compiled it together with `src/rurp_vpp.cpp` via `g++ -std=gnu++17 -Wall -Wextra -I include`:

| Leg | Defines | Compile exit | Warning bytes | Run exit | stdout / stderr |
|---|---|---:|---:|---:|---|
| 1 — AVR, no explicit macro | `-D__AVR__` | 0 | 0 | 0 | `mode=0 result=1` |
| 2 — non-AVR, explicit 0 | `-DRURP_HAS_VPP_DAC=0` | 0 | 0 | 0 | `mode=0 result=1` |
| 3 — forced-DAC (compiling `.cpp`) | `-D__AVR__ -DRURP_HAS_VPP_DAC=1` | **1** | n/a | n/a | stderr: `src/rurp_vpp.cpp:21:2: error: #error "RURP_HAS_VPP_DAC=1 selects a closed-loop VPP DAC implementation that this branch does not provide"` |
| 4 — unset, non-AVR | (none) | **1** | n/a | n/a | stderr: `include/rurp_vpp.h:66:6: error: #error "RURP_HAS_VPP_DAC must be supplied by the board/platform build (for py32f071: platform/py32f071/CMakeLists.txt's target_compile_definitions), not by this header."` |

The `-Wall -Wextra` warning byte count for legs 1 and 2 (the two legs that produce a linked binary) was **0 bytes** in both cases. The plan's fifth behaviour ("`-Wall -Wextra`: zero bytes of warning output" across the board) is discharged by legs 1 and 2 together with the real AVR builds below, all of which produced 0 bytes of compiler warning output.

## Real Cross-Compiler Proof (pio run, no figures claimed beyond this plan's own zero-delta measurement)

- `pio run -e uno`: SUCCESS. Flash **23954/32256** (74.3%), RAM **1573/2048** (76.8%) — **0 B delta** vs. the pre-phase baseline. `.pio/build/uno/src/rurp_vpp.cpp.o` exists (compiled).
- `pio run -e uno328pb`: SUCCESS. `text+data = 24004`, `data+bss = 1579` — **0 B delta**. `.o` exists.
- `pio run -e leonardo`: SUCCESS. `text+data = 26016`, `data+bss = 2014` — **0 B delta**. `.o` exists.
- Non-vacuity of the zero, both directions: `avr-nm` on `firestarter_uno.elf` finds **0** of the three seam symbols (`rurp_vpp_control_mode`, `rurp_set_vpp_target_mv`, `rurp_disable_vpp_control`) while **5 unrelated pre-existing `vpp` symbols remain** (`eprom_check_vpp`, `get_vpp_mv`, `key_vpp_mv`, two `using_p1_as_vpp` LTO clones), confirmed identically on `uno328pb` and `leonardo`'s ELFs — proving the grep is not matching nothing by accident.
- No flash or RAM figure beyond this zero-delta measurement is claimed here — Plan 125-04 owns the full two-directional non-vacuity write-up.

## Native Tripwire (fired in this task, not deferred)

| Env | Cases | Suites | Result |
|---|---:|---:|---|
| `native` | 141/141 succeeded | 17 | PASS |
| `native_nodevtools` | 141/141 succeeded | 17 | PASS |
| `native_pinmap_provisional` | 10/10 succeeded | 1 | PASS |

Confirmed as **counts**, not "tests pass": suite count stated explicitly for each. `include/rurp_shield.h` and `platformio.ini` were never touched — the operator's Option A on RESEARCH C-1 — so the tripwire's mechanism (a new `#error` fired in every native TU that includes `rurp_shield.h`) never triggers, because the seam has no includer outside `src/rurp_vpp.cpp` itself.

## Manifest Gate: Before / After

- Before (Task 1): `PASS: ... -- 23 enforced source(s) resolved ...`, exit 0.
- After (Task 2): `PASS: ... -- 24 enforced source(s) resolved ...`, exit 0. `# PY32_EXCLUDED:` count unchanged at **5** — no exclusion added for the seam (D-12 satisfied by naming, not excluding).

## `pytest tests/` Before / After

- Before: **72 passed** in 3.39s.
- After: **72 passed** in 3.11s. Unchanged — this plan adds no test module (that is Plan 125-02/125-03's job).

## Single Commit, Three Changed Paths

Commit `fb76287` (`v1.23-py32f071-integration`, `/workspaces/firestarter`):

```
feat(125-01): add the VPP control capability seam and name it in the ARM manifest

 include/rurp_vpp.h               | 90 ++++++++++++++++++++++++++++++++++++++++
 platform/py32f071/CMakeLists.txt | 14 +++++++
 src/rurp_vpp.cpp                 | 36 ++++++++++++++++
 3 files changed, 140 insertions(+)
```

Exactly three paths — `git show --stat` confirms it. No `git push` or `gh workflow run` was executed by this plan (D-14's structural gate is untouched; that push is Plan 125-05's job, operator-gated).

## Untouched-File Re-Hash (post-commit)

All seven blob SHAs re-hashed after the commit, identical to the pre-phase values recorded in Task 1 (table above) — `git status --porcelain` in `/workspaces/firestarter` is **0 lines** post-commit (corroboration only, per RESEARCH C-15; the primary proof is the blob-SHA re-hash). No deletions detected (`git diff --diff-filter=D --name-only HEAD~1 HEAD` is empty).

## Decisions Made

- **Operator Option A (RESEARCH C-1):** `include/rurp_shield.h` is not touched by this plan. Both new files land; there is no `#include "rurp_vpp.h"` anywhere. This is what keeps the tripwire green — verified, not merely followed on faith.
- **Second `#error` in the `.cpp` (RESEARCH C-4):** the header's `#if !defined(RURP_HAS_VPP_DAC)` guard cannot reject an explicitly-forced `RURP_HAS_VPP_DAC=1` (it exits 0), so a second, separately-authored `#error` was placed in `src/rurp_vpp.cpp`, scoped to "this branch" per C-17 because `origin/feature/py32f071-full-support` (PR #47, closed, Out of Scope) genuinely sets the macro to 1 and implements a DAC.
- **`__AVR__` over `RURP_PLATFORM_AVR` (RESEARCH C-13):** recorded in the header comment with the full reasoning (derived-from, never-defined-during-AVR-build, unreachable-escape-arm) so a later phase does not "improve" the predicate.
- **CMake placement:** the new source entry was placed among the top-level `src/*.cpp` entries (after `src/boards/rurp_serial_utils.cpp`, before `src/proms/memory.cpp`), and `RURP_HAS_VPP_DAC=0` was added as the eighth `target_compile_definitions` entry directly after `RURP_PY32F071_PINMAP_CONFIGURED=1`, extending the existing comment block in place rather than duplicating it.
- **No requirement ticked.** Per the phase's explicit scope guard, this plan does not tick VPP-01, VPP-02, or VPP-03 in `.planning/REQUIREMENTS.md` — only Plan 125-06 may do that.

## Deviations from Plan

None — plan executed exactly as written. All acceptance criteria in the plan's Task 2 were independently re-checked against the live tree (grep counts, hash re-checks, manifest gate output, pytest output, native suite counts, single-commit path count) rather than assumed from the plan's prose.

## Known Stubs

None. `rurp_vpp.cpp`'s three trivial refusal bodies are the intentional, fully-specified deliverable of this phase (D-09/D-10/D-11) — not stubs standing in for missing functionality. There are deliberately zero production callers this phase (D-11); no UI or downstream consumer renders anything from these functions, so there is no stub-pattern risk of the kind this section exists to catch.

## Threat Flags

None. This plan's threat model (see `125-01-PLAN.md` `<threat_model>`) is fully addressed by the changes above: T-125-01/02/03/04/05 are all `mitigate`-dispositioned and their mitigations are exactly what was implemented (deny-by-default capability macro, second forced-value guard, the C-1 tripwire fired in-task, the VPP-03 file pin). T-125-06 and T-125-07 are `accept`/deferred-to-later-plan by the plan's own disposition and are not re-opened here. No new security-relevant surface (network endpoint, auth path, file access pattern, schema change) was introduced beyond what the plan's threat model already accounts for.

## Issues Encountered

None.

## User Setup Required

None — no external service configuration required.

## Claim Ceiling Compliance

This SUMMARY makes no claim that the firmware runs on a PY32F071, that closed-loop VPP works, that the pin map is correct/verified/validated, or an unqualified bench-validated/hardware-validated/silicon-verified claim. AVR manual VPP control is stated as permanent, not provisional. No PY32F071 hardware exists; every ARM-side statement here is scoped to compile-time evidence (`check_cmake_manifest.py`'s PASS, the manifest's declared `target_compile_definitions`) — no ARM CI run or ARM build figure is claimed in this plan (that is Plan 125-05's job).

## Next Phase Readiness

- The seam is landed and named in the ARM manifest at 24 enforced sources; Plan 125-02 (four-board pytest harness) and Plan 125-03 (PR #45 non-ancestry gate) can both build against a stable, committed `include/rurp_vpp.h` / `src/rurp_vpp.cpp`.
- No blockers. The C-1 tripwire fired clean; there is no pending `include/rurp_shield.h` edit to worry about landing later — Option A closed that question for the rest of the phase.
- Plan 125-04 (flash/RAM measurement + comparator) can cite this plan's zero-delta figures as its starting pin.
- Plan 125-05 (ARM CI evidence) still needs its own operator-gated push + `workflow_dispatch` — nothing in this plan executed either command.

---
*Phase: 125-vpp-control-seam*
*Completed: 2026-07-31*

## Self-Check: PASSED

- FOUND: `/workspaces/firestarter/include/rurp_vpp.h`
- FOUND: `/workspaces/firestarter/src/rurp_vpp.cpp`
- FOUND: `/workspaces/.planning/phases/125-vpp-control-seam/125-01-SUMMARY.md`
- FOUND: firmware commit `fb76287` (`git log --oneline --all` in `/workspaces/firestarter`)
- FOUND: meta commit `e2bc8d4` (`git log --oneline --all` in `/workspaces`)
