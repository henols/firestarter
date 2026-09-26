---
phase: 124-firmware-integration-merge
plan: "07"
subsystem: firmware-ci
tags: [firestarter, cmake, py32f071, flash-latency, static_assert, hal, merge08]

# Dependency graph
requires:
  - phase: 124-firmware-integration-merge
    plan: "04"
    provides: "THE LANDING (e2c422d) -- the squashed py32f071 port on v1.23-py32f071-integration this plan edits after, per D-03's forced ordering."
provides:
  - "Deletion of the orphaned platform/py32f071/cmake/write_checksums.cmake (D-01), zero-consumer status re-proven against the landed tree in both firestarter and firestarter_app, not accepted from the research record"
  - "Corrected flash-latency argument (FLASH_LATENCY_1, not the FLASH_ACR_LATENCY_1 ACR bit-mask) in platform/py32f071/src/main.cpp's configure_system_clock(), with a static_assert compile-time regression guard and an honest limitation comment (D-04, C-5, C-6)"
affects: [124-08, 124-09, 124-10, 124-11, 124-12]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Zero-consumer deletion re-proven per-repo with git grep against the landed tree (not the research record) before git rm, quoting both search commands and their (empty) output in the commit message"
    - "static_assert regression guard whose comment explicitly states the preferred compile-time proof shape is unachievable and why, rather than silently downgrading to a weaker guard without saying so"

key-files:
  created: []
  modified:
    - firestarter/platform/py32f071/cmake/write_checksums.cmake (deleted)
    - firestarter/platform/py32f071/src/main.cpp

key-decisions:
  - "Re-ran both zero-consumer git grep searches (firestarter, firestarter_app) against the current landed tree rather than accepting 124-CONTEXT D-01 / 124-RESEARCH C-15's claim -- both returned exit 1 (no matches), confirming the file was safe to delete."
  - "Comment prose in main.cpp paraphrases the ACR mask ('the ACR bit-mask'/'that ACR mask') instead of repeating the literal token FLASH_ACR_LATENCY_1, so the plan's acceptance criterion (grep -c FLASH_ACR_LATENCY_1 == 1, and that one hit inside the static_assert, never the call argument) holds exactly -- this was tightened during execution from an initial draft that repeated the literal token 6 times across the comment."
  - "static_assert and its failure message were kept on a single source line so grep -c (which counts matching lines, not occurrences) reports exactly 1 for FLASH_ACR_LATENCY_1."
  - "No ARM toolchain claim made anywhere in this SUMMARY or the commit messages -- both changes are recorded as source-level only, pending Plan 124-11's CI run URL + head SHA."

requirements-completed: []
# MERGE-08 is NOT ticked here -- per the dispatch prompt's <requirement_ticking_scope>,
# Plan 124-12 is the sole owner of all MERGE-01..MERGE-08 requirement ticks. What this
# plan PROVED: two of MERGE-08's three named in-branch defects (write_checksums.cmake
# orphan, flash-latency constant) are closed in their own attributable commits. The third
# (DEV_TOOLS conversion) was closed by Plan 124-06.

coverage:
  - id: D1
    description: "platform/py32f071/cmake/write_checksums.cmake deleted after re-proving zero consumers against the landed tree in both firestarter and firestarter_app (D-01)"
    requirement: "MERGE-08"
    verification:
      - kind: unit
        ref: "git grep -n write_checksums -- . (firestarter) -- no output, exit 1; git grep -n write_checksums -- . (firestarter_app) -- no output, exit 1; git ls-tree HEAD platform/py32f071/cmake/ post-deletion lists only arm-none-eabi.cmake; python3 scripts/check_cmake_manifest.py -- PASS, exit 0"
        status: pass
    human_judgment: false
  - id: D2
    description: "main.cpp's clock-configuration call passes FLASH_LATENCY_1 (one wait state) instead of the FLASH_ACR_LATENCY_1 ACR mask (two wait states), with a static_assert compile-time regression guard and honest limitation comment (D-04, C-5, C-6)"
    requirement: "MERGE-08"
    verification:
      - kind: unit
        ref: "grep -c FLASH_ACR_LATENCY_1 platform/py32f071/src/main.cpp -- 1 (inside the static_assert line only); grep -c FLASH_LATENCY_1 -- 6 (includes the corrected call argument); grep -c static_assert -- 3; git diff HEAD~1 -- platform/py32f071/src/main.cpp shows only the one changed call argument plus added comment/assert lines"
        status: pass
      - kind: other
        ref: "ARM compilation of this change is NOT verified locally (no arm-none-eabi-gcc/cmake/ninja in this devcontainer) -- pending Plan 124-11's CI run URL + head SHA"
        status: unknown
    human_judgment: true
    rationale: "The guard's actual behavior under the ARM toolchain (does the static_assert compile, does the corrected latency build) cannot be proven in this devcontainer. A human (or Plan 124-11's CI evidence) must confirm the ARM build succeeds before this deliverable is considered fully proven."

duration: ~15min
completed: 2026-07-31
status: complete
---

# Phase 124 Plan 07: MERGE-08 In-Branch Defects (D-01, D-04) Summary

**Deleted the orphaned `write_checksums.cmake` (zero-consumer status re-proven against the landed tree in both repos) and corrected `main.cpp`'s flash-latency argument from the two-wait-state `FLASH_ACR_LATENCY_1` ACR mask to the intended one-wait-state `FLASH_LATENCY_1`, adding a `static_assert` regression guard with an honest comment stating why the preferred compile-time proof shape is unachievable.**

## Performance

- **Duration:** ~15 min
- **Started:** 2026-07-31 (session continuation after 124-06)
- **Completed:** 2026-07-31
- **Tasks:** 2 completed
- **Files modified:** 2 (1 deleted, 1 modified)

## Accomplishments

- **Task 1 (D-01):** Re-proved `write_checksums.cmake`'s zero-consumer status against the *landed* tree — not the research record — with two independent `git grep` searches (firestarter, firestarter_app), both returning zero matches. Deleted the file. `check_cmake_manifest.py` re-run afterward, still exits 0 (the deleted file was never a manifest source-list entry).
- **Task 2 (D-04):** Corrected `configure_system_clock()`'s `HAL_RCC_ClockConfig()` call to pass `FLASH_LATENCY_1` instead of `FLASH_ACR_LATENCY_1`. Added a `static_assert(FLASH_LATENCY_1 != FLASH_ACR_LATENCY_1, ...)` immediately beside the call as a compile-time regression guard, with a comment citing the pinned SDK SHA and header path, naming both the workaround commit (`91c6e45`) and the module-restoring commit (`d76910c`) by SHA, stating the severity framing honestly ("functionally safe... an over-conservative setting, not a correctness fault"), and explaining why the preferred clock-tied `static_assert` is unachievable (`RCC_HSICALIBRATION_24MHz` dereferences a factory-trim address at runtime).

## Observed Verification Values

### Task 1 — zero-consumer re-proof and deletion

```
$ cd /workspaces/firestarter && git grep -n write_checksums -- .
(no output)
$ echo $?
1

$ cd /workspaces/firestarter_app && git grep -n write_checksums -- .
(no output)
$ echo $?
1
```

Both searches ran against the landed tree at the time of execution (`firestarter` HEAD `edc73e2` before this plan's commits), not against the research record. `CMakeLists.txt` was also read directly and confirmed to contain no `include()` of the file. `git ls-tree HEAD platform/py32f071/cmake/` after deletion:

```
100644 blob 512fc63c247cce99b6d144b19ce6aeede081b58b	platform/py32f071/cmake/arm-none-eabi.cmake
```

`write_checksums.cmake` is absent (`test ! -e ...` succeeds). `python3 scripts/check_cmake_manifest.py` after deletion: `PASS: ... 23 enforced source(s) resolved ...` — exit 0, unaffected.

The inline `sha256sum`-based checksum capability already exists in `.github/workflows/py32f071.yml` (verified by reading lines 82-104: "Create and verify firmware checksums" + "Create artifact checksum manifest" steps), which is why the orphan was deleted rather than wired up.

### Task 2 — flash-latency correction and guard

`git diff HEAD~1 -- platform/py32f071/src/main.cpp` (the actual diff produced by this plan's Task 2 commit):

```diff
-    if (HAL_RCC_ClockConfig(&clocks, FLASH_ACR_LATENCY_1) != HAL_OK)
+    /* FLASH_LATENCY_1 (one wait state, 24 MHz < SYSCLK <= 48 MHz) and FLASH_LATENCY_2 (two wait
+     * states, 48 MHz < SYSCLK <= 72 MHz) are the SDK's named flash-latency constants. The ACR
+     * bit-mask this call used to pass numerically equals FLASH_LATENCY_2. SDK
+     * 0ed2f4b4d3391eccfd4491006a30295fd78e32c2,
+     * Drivers/PY32F071_HAL_Driver/Inc/py32f071_hal_flash.h:133-135.
+     *
+     * Commit 91c6e45 ("Use PY32 flash latency constant", 2026-07-21) swapped this call's
+     * argument from FLASH_LATENCY_1 to that ACR mask as a deliberate workaround: at that commit,
+     * py32f071_hal_conf.h did not define HAL_FLASH_MODULE_ENABLED and did not include
+     * py32f071_hal_flash.h, so FLASH_LATENCY_1 was not yet in scope and the CMSIS device-header
+     * mask was the only thing that compiled. Commit d76910c ("Complete PY32 HAL module
+     * configuration"), three minutes later, added both the #define and the #include -- but the
+     * workaround was never reverted. FLASH_LATENCY_1 is in scope on this tree. This is not a
+     * typo: it is a superseded workaround left in place.
+     *
+     * Severity: the previous argument selected two wait states at 48 MHz instead of the required
+     * one. More wait states than required is functionally safe -- an over-conservative setting,
+     * not a correctness fault.
+     *
+     * The preferred proof shape (a static_assert tying the chosen latency to the configured
+     * clock) is not achievable: RCC_HSICALIBRATION_24MHz expands to a runtime dereference of a
+     * factory-trim address (((0x4<<13) | ((*(uint32_t *)(0x1FFF3220)) & 0x1FFF))), so it can
+     * never appear in a static_assert; RCC_PLL_MUL2 is a register-field value, not a multiplier.
+     * The SDK does not expose the configured system clock as a compile-time constant. The guard
+     * below is the honest maximum: it can only be evaluated by the ARM toolchain in CI, since no
+     * local ARM compiler exists here. */
+    static_assert(FLASH_LATENCY_1 != FLASH_ACR_LATENCY_1, "the ACR mask equals FLASH_LATENCY_2 (two wait states) - do not reintroduce it");
+
+    if (HAL_RCC_ClockConfig(&clocks, FLASH_LATENCY_1) != HAL_OK)
     {
         error_handler();
     }
```

Exactly one changed argument (the call now reads `FLASH_LATENCY_1`) plus added comment and `static_assert` lines. Nothing else in `configure_system_clock()` changed — the 48 MHz oscillator/PLL setup above the flash-latency block is untouched.

Grep confirmation:

```
$ grep -c 'FLASH_ACR_LATENCY_1' platform/py32f071/src/main.cpp
1
```
(single hit: line `static_assert(FLASH_LATENCY_1 != FLASH_ACR_LATENCY_1, "the ACR mask equals FLASH_LATENCY_2 (two wait states) - do not reintroduce it");` — inside the guard, never the call argument.)

```
$ grep -c 'FLASH_LATENCY_1' platform/py32f071/src/main.cpp
6
```
(includes the corrected call argument line `if (HAL_RCC_ClockConfig(&clocks, FLASH_LATENCY_1) != HAL_OK)`.)

```
$ grep -c 'static_assert' platform/py32f071/src/main.cpp
3
```

The pinned SDK commit SHA `0ed2f4b4d3391eccfd4491006a30295fd78e32c2` was read live from `platform/py32f071/CMakeLists.txt`'s `GIT_TAG` field (not transcribed from a planning document) and cited in the comment. Both `91c6e45` and `d76910c` were independently confirmed as real commits in the repo's history (`git cat-file -t`, `git show --stat`) before being cited: `91c6e45` (`Use PY32 flash latency constant`, 2026-07-21 12:46:16) changed the argument *from* `FLASH_LATENCY_1` *to* `FLASH_ACR_LATENCY_1`; `d76910c` (`Complete PY32 HAL module configuration`, 2026-07-21 12:49:02, three minutes later) added `HAL_FLASH_MODULE_ENABLED` + the `py32f071_hal_flash.h` include to `py32f071_hal_conf.h`. `py32f071_hal_conf.h` was also read directly and confirmed both are present on the landed tree, so `FLASH_LATENCY_1` is in scope.

**ARM compilation is NOT verified here.** `arm-none-eabi-gcc`, `cmake`, and `ninja` are absent from this devcontainer; nothing in this plan was locally compiled. Whether the corrected constant and the `static_assert` guard actually compile under the ARM toolchain is evidenced only by Plan 124-11's CI run URL and head SHA — no claim of local build/verify/validate is made anywhere in this SUMMARY or in either task's commit message.

### AVR / native non-regression check (both changed files are ARM-only: `platform/py32f071/`)

| Env | Flash used | RAM used | Matches 124-04/06 baseline |
|---|---|---|---|
| uno | 23954 / 32256 | 1573 / 2048 | exact |
| uno328pb | 24004 / 32384 | 1579 / 2048 | exact |
| leonardo | 26016 / 28672 | 2014 / 2560 | exact |

Native: `pio test -e native` → 141 test cases, 141 succeeded, 17 suites. `pio test -e native_nodevtools` → 141 test cases, 141 succeeded, 17 suites. Both unchanged from the 124-04 landing baseline.

`python3 -m pytest tests/ -q` → **65 passed, 1 failed** (`tests/test_check_orphan_provisional.py::test_unarmed_on_the_real_tree_with_no_seam_override` — still fails as expected; `RURP_PY32F071_PINMAP_PROVISIONAL: zero consumers` remains unresolved, owned by Plan 124-08, deliberately left red).

`git status --porcelain` in `/workspaces/firestarter`: empty after both task commits.

## Task Commits

Each task was committed atomically inside the `firestarter` submodule on branch `v1.23-py32f071-integration`:

1. **Task 1: Re-prove zero consumers, then delete write_checksums.cmake (D-01)** — `7a61531` (fix)
2. **Task 2: Correct the flash-latency constant and add a compile-time regression guard (D-04)** — `5bbfaac` (fix)

**Plan metadata:** committed in the meta-repo (this SUMMARY.md + STATE.md + ROADMAP.md commit, below).

## Files Created/Modified

- `firestarter/platform/py32f071/cmake/write_checksums.cmake` — deleted (D-01); zero-consumer status re-proven, not accepted from the research record
- `firestarter/platform/py32f071/src/main.cpp` — corrected flash-latency argument + `static_assert` regression guard + cited comment (D-04)

## Decisions Made

- Re-ran both zero-consumer `git grep` searches against the current landed tree instead of trusting `124-CONTEXT.md` D-01 / `124-RESEARCH.md` C-15's prior claim. Both confirmed zero matches independently.
- Tightened the `main.cpp` comment during execution: an initial draft repeated the literal token `FLASH_ACR_LATENCY_1` six times across the comment block, which would have violated the plan's acceptance criterion (`grep -c FLASH_ACR_LATENCY_1` must equal exactly 1, and that one hit must be inside the `static_assert`, never the call argument). Rewrote the comment to paraphrase the mask descriptively ("the ACR bit-mask", "that ACR mask") everywhere except the single `static_assert` line, and kept the `static_assert` and its failure message on one physical line so `grep -c` (line-counting, not occurrence-counting) reports exactly 1.
- No local-verification claim made for either change; framing throughout routes ARM evidence to Plan 124-11's CI run.

## Deviations from Plan

None — plan executed exactly as written. The comment-wording tightening above was a self-correction made before any commit was finalized (to satisfy the plan's own literal acceptance criterion), not a deviation from plan scope, and is recorded above for transparency rather than as a Rule 1-3 auto-fix (no bug, missing functionality, or blocker was involved — it was an authoring-precision correction to my own draft).

## Issues Encountered

None.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- Two of MERGE-08's three named in-branch defects are now closed in their own attributable commits (`7a61531` D-01, `5bbfaac` D-04), following Plan 124-06's `DEV_TOOLS` conversion (the third). MERGE-08 is not ticked in `REQUIREMENTS.md` by this plan — per the dispatch prompt's requirement-ticking scope, Plan 124-12 owns all MERGE-01..MERGE-08 ticks.
- Neither change is locally build-verified (no ARM toolchain in this devcontainer). Plan 124-11 must supply the CI run URL + head SHA covering commits `7a61531` and `5bbfaac` (and any later commits) as the mechanical proof that both the deletion and the `static_assert` guard compile cleanly under `arm-none-eabi-gcc`.
- AVR flash/RAM (uno 23954/1573, uno328pb 24004/1579, leonardo 26016/2014) and native case/suite counts (141/17 both envs) are unchanged from the 124-04/124-06 baseline, as expected for two ARM-only source edits.
- `tests/test_check_orphan_provisional.py::test_unarmed_on_the_real_tree_with_no_seam_override` is still red (65 passed, 1 failed) — this is Plan 124-08's defect to close, left untouched here as instructed.
- No blockers for 124-08 onward.

## Self-Check: PASSED

- FOUND: `.planning/phases/124-firmware-integration-merge/124-07-SUMMARY.md`
- FOUND commit `7a61531` (firestarter submodule)
- FOUND commit `5bbfaac` (firestarter submodule)
- MISSING (expected): `firestarter/platform/py32f071/cmake/write_checksums.cmake` (deleted by design)
- FOUND: `firestarter/platform/py32f071/src/main.cpp`

---
*Phase: 124-firmware-integration-merge*
*Completed: 2026-07-31*
