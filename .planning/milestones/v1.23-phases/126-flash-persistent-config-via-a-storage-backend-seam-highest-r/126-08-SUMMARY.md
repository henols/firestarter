---
phase: 126-flash-persistent-config-via-a-storage-backend-seam-highest-r
plan: 08
subsystem: firmware-storage
tags: [py32f071, flash, hal, config-storage, manifest, cmake]

# Dependency graph
requires:
  - phase: 126-03
    provides: "include/rurp_config_storage.h seam (D-06/D-07/D-08/D-09); rurp_config_storage.h census pre-sized for a third includer"
  - phase: 126-06
    provides: "linker symbols __config_slot_a_start/__config_slot_b_start/__config_page_size/__config_region_end, PROVIDEd by PY32F071xB_FLASH.ld"
  - phase: 126-07
    provides: "the HAL-free config_storage_dualslot.{h,cpp} core and rurp_flash_primitives_t injection contract this plan's primitives satisfy"
provides:
  - "platform/py32f071/src/config_storage_flash.cpp — the only file in the tree that knows the PY32 HAL exists: three primitives (hal_read/hal_erase_page/hal_program_page) routed exclusively through HAL_FLASH_Unlock/Erase/Program/Lock, slot addresses derived from the three extern linker symbols, and the two rurp_config_storage_load/save seam functions delegating to the core"
  - "platform/py32f071/src/config.cpp deleted (CFG-07) — PR #48's drifted, non-persisting policy, verified absent from the tree"
  - "platform/py32f071/CMakeLists.txt closed at 26 enforced sources / 15 exempt / 5 allow-listed omissions: src/rurp_config_utils.cpp promoted into FIRESTARTER_COMMON_SOURCES, its PY32_EXCLUDED line retired, src/config.cpp swapped for src/config_storage_flash.cpp, and py32f071_hal_flash.c added to PY32_SDK_SOURCES (C-3)"
  - "tests/test_py32_flash_map.py extended with six functions asserting C-3/C-4/CFG-07/D-11 locally, converting the CI-only flash-driver omission into a pytest failure"
affects: ["126-09 (test_config_storage_dualslot.py compiles the same core this plan's primitives back)", "126-10 (schema-pinning gate)", "126-11 (the gated ARM CI run that is the only authoritative proof this plan's manifest edit actually links)", "126-12 (closing plan, only one permitted to tick CFG-05/CFG-06/CFG-07)"]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "HAL glue isolation: exactly one TU (config_storage_flash.cpp) is permitted to include the board header / HAL and carry the RURP_PLATFORM_PY32F071 #error guard; the HAL-free core and the common policy layer never see either."
    - "Comment-stripped textual gates: tests/test_py32_flash_map.py's new HAL-call and register-access scans strip /* */ and // comments before matching, so a prose citation of FLASH->CR (explaining why it is NOT used) is never mistaken for actual register access."

key-files:
  created:
    - firestarter/platform/py32f071/src/config_storage_flash.cpp
  modified:
    - firestarter/platform/py32f071/CMakeLists.txt
    - firestarter/scripts/check_cmake_manifest.py
    - firestarter/tests/test_py32_flash_map.py
  deleted:
    - firestarter/platform/py32f071/src/config.cpp

key-decisions:
  - "config.cpp's four drift points recorded before deletion (see below) — CFG-07 requires deletion verified by absence, not reconciliation, and this record is the only surviving evidence of what was actually removed."
  - "The deletion (config.cpp) and the policy-TU promotion (rurp_config_utils.cpp into FIRESTARTER_COMMON_SOURCES) landed in the SAME commit, closing the only window in this phase where the ARM link could have two definitions of each of the four public config functions. Plan 126-03 deliberately deferred the promotion for exactly this reason; the window was never opened."
  - "C-3's fourth manifest edit (py32f071_hal_flash.c into PY32_SDK_SOURCES) treated as a named, separately-verified checklist item, per the plan and 126-RESEARCH.md Pitfall 3 -- nothing in this devcontainer can otherwise catch its absence."
  - "config_storage_flash.cpp includes the board header (boards/py32f071_rurp_shield.h), not py32f071_hal.h directly -- matching timing.cpp's established convention over 126-RESEARCH.md's illustrative code example, per this plan's own read_first guidance."
  - "hal_read/hal_erase_page/hal_program_page given extern \"C\" linkage, matching the language linkage of rurp_flash_primitives_t's function-pointer members (the struct is declared inside config_storage_dualslot.h's extern \"C\" block) -- not explicitly named in the plan's action text but required for the primitive-table initializer's pointer types to match without relying on a compiler extension."

requirements-completed: []  # CFG-05 spans 126-07/126-08/126-09; CFG-06 spans 126-06/126-08; CFG-07 spans 126-03/126-08/126-10's gate; only 126-12 ticks CFG-01..CFG-07

coverage:
  - id: D1
    description: "config.cpp's four PR #48 drift points recorded before deletion, then the file deleted and verified absent from the tree"
    requirement: "CFG-07"
    verification:
      - kind: unit
        ref: "tests/test_py32_flash_map.py::test_pr48_config_cpp_is_absent_from_the_tree"
        status: pass
    human_judgment: false
  - id: D2
    description: "config_storage_flash.cpp supplies three HAL-routed primitives (read/erase_page/program_page) and the two seam functions, calling only HAL_FLASH_Unlock/Erase/Program/Lock with no direct register access"
    requirement: "CFG-05"
    verification:
      - kind: unit
        ref: "tests/test_py32_flash_map.py::test_the_flash_glue_uses_only_hal_entry_points"
        status: pass
      - kind: unit
        ref: "tests/test_py32_flash_map.py::test_slot_addresses_come_from_linker_symbols"
        status: pass
    human_judgment: false
  - id: D3
    description: "CMake manifest closed at 26 enforced sources / 15 exempt / 5 allow-listed omissions, with py32f071_hal_flash.c named (C-3) and a local pytest detector proving a nonzero HAL_FLASH_ call-site antecedent before checking the manifest"
    requirement: "CFG-06"
    verification:
      - kind: unit
        ref: "python3 scripts/check_cmake_manifest.py (exit 0, PASS at 26 enforced)"
        status: pass
      - kind: unit
        ref: "tests/test_py32_flash_map.py::test_manifest_names_the_flash_driver"
        status: pass
    human_judgment: false
  - id: D4
    description: "No AVR-visible regression: pytest tests/ grew by exactly 6, both pinned native envs unchanged at 141/141 across 17 suites, all three AVR flash/RAM figures byte-identical to the Plan 124 baseline"
    verification:
      - kind: unit
        ref: "python3 -m pytest tests/ -q (144 passed); pio test -e native and -e native_nodevtools (141 test cases: 141 succeeded, 17 suites, each); pio run -e uno/-e uno328pb/-e leonardo compared against scripts/baseline/size_baseline.json"
        status: pass
    human_judgment: false
  - id: D5
    description: "ARM link is NOT proven here (arm-none-eabi-gcc/cmake/ninja absent) -- explicitly deferred to Plan 126-11's gated CI run"
    verification: []
    human_judgment: true
    rationale: "No compiler/linker exists in this environment to prove the ARM target actually links against the new manifest entries; this is a claim-ceiling statement a human/CI run must confirm, not something a local test can assert."

duration: 70min
completed: 2026-08-01
status: complete
---

# Phase 126 Plan 08: The PY32 HAL flash primitives, config.cpp deletion, and manifest close Summary

**`config_storage_flash.cpp` supplies three HAL-routed flash primitives on top of the HAL-free dual-slot core; PR #48's non-persisting `config.cpp` is deleted and verified absent; the ARM manifest closes at 26 enforced sources with the previously-missing `py32f071_hal_flash.c` now named and a local pytest detector (proven-antecedent) that converts that CI-only link failure into a local one — all four manifest edits and the deletion landed in one commit, so the duplicate-symbol ARM link window was never opened.**

## Performance

- **Duration:** ~70 min
- **Completed:** 2026-08-01T00:15:00Z (approx.)
- **Tasks:** 2
- **Files modified:** 5 (1 created, 3 modified, 1 deleted)

## Accomplishments

- Authored `platform/py32f071/src/config_storage_flash.cpp`: the sole HAL-aware TU. `hal_read` memcpy's from the memory-mapped slot address; `hal_erase_page` unlocks, erases via `FLASH_TYPEERASE_PAGEERASE`/`NbPages=1`, locks, and returns false on any non-`HAL_OK` result (with citations to RM V0.2 §4.2.3.6 for the timing-register prerequisite and §4.5.3/§4.2.3.3 for the silently-skipped write-protected erase); `hal_program_page` unlocks, programs the caller's full 64-word buffer via `FLASH_TYPEPROGRAM_PAGE`, locks, and returns false on non-`HAL_OK` (citing C-2's 64-word-unconditional read and C-8's erase-first requirement). Slot addresses derive from three `extern uint32_t` linker symbols, never a duplicated literal. The two seam functions (`rurp_config_storage_load`/`save`) delegate to `rurp_dualslot_load`/`save` over a file-local primitive table.
- Deleted `platform/py32f071/src/config.cpp` (CFG-07) after recording its four drift points (below), verified absent by `git ls-files` / `test ! -e`.
- Closed `platform/py32f071/CMakeLists.txt`: retired the `PY32_EXCLUDED: src/rurp_config_utils.cpp` line, promoted `"${REPOSITORY_ROOT}/src/rurp_config_utils.cpp"` into `FIRESTARTER_COMMON_SOURCES` (17→18), swapped `src/config.cpp` for `src/config_storage_flash.cpp` in `PY32_PLATFORM_SOURCES` (stays at 8), and added `"${PY32_SDK_ROOT}/Drivers/PY32F071_HAL_Driver/Src/py32f071_hal_flash.c"` to `PY32_SDK_SOURCES` (14→15) — the C-3 fix. Manifest gate now PASSes at **26 enforced sources**, **15 exempt**, **5 allow-listed omissions**.
- Updated `scripts/check_cmake_manifest.py`'s docstring only: exclusion enumeration back to five lines, Plan 126-03's deferral note replaced with a record that the promotion happened, in the same commit as the deletion.
- Extended `tests/test_py32_flash_map.py` with six functions (20 total in the module): the C-3 proven-antecedent flash-driver assertion, the HAL-only-entry-points assertion, the HAL-free-core assertion, the CFG-07 absence check, the linker-symbol assertion, and their shared RED demonstration.
- Both atomicity demonstrations performed as scratch manipulations (never committed): deleting `config.cpp` while its manifest entry remained produced exit 1 with a not-found violation; creating `config_storage_flash.cpp` while unnamed in `PY32_PLATFORM_SOURCES` left the checker at exit 0 (the reverse check only scans `<root>/src`, never `platform/py32f071/src`) — recorded explicitly as the reason edit (c) is a deliberate act the gate does not enforce.

## Task Commits

Each task was committed atomically (firmware submodule, `/workspaces/firestarter`, branch `v1.23-py32f071-integration`):

1. **Task 1: The HAL glue, the config.cpp deletion and the manifest close — ONE commit** — `5b08495` (feat) — `platform/py32f071/CMakeLists.txt`, `platform/py32f071/src/config.cpp` (deleted), `platform/py32f071/src/config_storage_flash.cpp` (created), `scripts/check_cmake_manifest.py`
2. **Task 2: Turn C-3's CI-only link failure into a local pytest failure** — `1d2c7f8` (test) — `tests/test_py32_flash_map.py`

**Plan metadata:** this SUMMARY commit (docs, meta repo)

## Files Created/Modified

- `firestarter/platform/py32f071/src/config_storage_flash.cpp` — new (166 lines). Platform guard `#if !defined(RURP_PLATFORM_PY32F071) / #error`; includes `"boards/py32f071_rurp_shield.h"`, `<string.h>`, `"config_storage_dualslot.h"`, `"rurp_config_storage.h"` (the third sanctioned includer of the seam header); three `extern "C" { extern uint32_t __config_slot_a_start, __config_slot_b_start, __config_page_size; }` declarations; `hal_read`/`hal_erase_page`/`hal_program_page` (all `extern "C"`); a file-local `const rurp_flash_primitives_t primitives` in an unnamed namespace; `rurp_config_storage_load`/`rurp_config_storage_save` (`extern "C"`) delegating to the core.
- `firestarter/platform/py32f071/src/config.cpp` — **deleted** (47 lines removed). Its four drift points, recorded before deletion:
  1. A **private static** `configuration` in an unnamed namespace (`:5-7`), instead of the shared `rurp_config` global the AVR side uses.
  2. A **second, drifted `rurp_validate_config`** (`:15-30`) whose condition is `strcmp(value->version, CONFIG_VERSION) != 0 || value->r2 == 0` — an extra `r2 == 0` disjunct the AVR version does not have — and whose body opens with a `memset(value, 0, sizeof(*value))` the AVR version also lacks.
  3. **No write-back call at all**: `rurp_load_config()` here just `memset`s the local static to zero and calls `rurp_validate_config` — it never calls anything analogous to `src/rurp_config_utils.cpp:38`'s `rurp_save_config(config)` write-back inside `rurp_validate_config`, so a virgin part's defaults are computed but never persisted.
  4. `rurp_save_config` (`:38-47`) calls `rurp_validate_config(value)` then **assigns to the local static** (`configuration = *value;`) and returns — there is no call to any storage backend at all. The function's name promises persistence and delivers none, matching the plan's framing exactly.
- `firestarter/platform/py32f071/CMakeLists.txt` — 4 edits: `PY32_EXCLUDED` 6→**5** lines (the `src/rurp_config_utils.cpp` line removed); `FIRESTARTER_COMMON_SOURCES` 17→**18** (added `"${REPOSITORY_ROOT}/src/rurp_config_utils.cpp"`, placed among the top-level `src/*.cpp` entries before the `src/proms/` group); `PY32_PLATFORM_SOURCES` stays at **8** (swapped `src/config.cpp` → `src/config_storage_flash.cpp`); `PY32_SDK_SOURCES` 14→**15** (added the `${PY32_SDK_ROOT}`-rooted `py32f071_hal_flash.c`).
- `firestarter/scripts/check_cmake_manifest.py` — docstring-only diff: exclusion enumeration back to five lines, deferral note replaced with a one-line record that the promotion and deletion happened together in the same commit.
- `firestarter/tests/test_py32_flash_map.py` — +311/-7 lines. Six new functions plus their module-level `_violations_*`/scan helpers, new path constants, and docstring updates (Requirements line now names CFG-05/CFG-06/CFG-07; Decisions-covered line adds C-3/C-4/D-02; Coverage list extended to 20 items; the old "Plan 126-08 EXTENDS this module... do NOT add that function here" note replaced with a record that it did, plus a rationale paragraph naming `py32f071_hal_conf.h:10`/`:53`, the compile-vs-link distinction, and the absent toolchain).

## Verification Detail (for the record)

**Manifest gate, before and after Task 1:**
```
Before: PASS -- 25 enforced source(s) resolved; 14 PY32_SDK_SOURCES exempt; allow-listed: 6 entries (incl. src/rurp_config_utils.cpp)
After:  PASS -- 26 enforced source(s) resolved; 15 PY32_SDK_SOURCES exempt; allow-listed: 5 entries (src/rurp_config_utils.cpp no longer among them)
```
`grep -c hal_flash platform/py32f071/CMakeLists.txt`: **0 before** (confirmed independently at pattern-map time and re-confirmed via scratch deletion above) → **1 after**.
`grep -c PY32_EXCLUDED platform/py32f071/CMakeLists.txt`: 6 → **5**.

**Both atomicity demonstrations (scratch, reverted, never committed):**
1. `config.cpp` deleted, its `PY32_PLATFORM_SOURCES` entry left in place → `python3 scripts/check_cmake_manifest.py` exit **1**: `FAIL: 1 violation(s) ... PY32_PLATFORM_SOURCES: 'src/config.cpp' -> .../config.cpp (not found)`.
2. `config_storage_flash.cpp` created but **unnamed** in `PY32_PLATFORM_SOURCES` → checker still exits **0** at 25 enforced sources — confirmed the reverse-omission check only walks `<root>/src`, never `platform/py32f071/src`, so this asymmetry is real and edit (c) (naming the new file in the manifest) is a deliberate authoring act, not something the gate enforces.

**Seam-header includer census:** moved from 2 to **3** hits, all sanctioned: `platform/py32f071/src/config_storage_flash.cpp`, `src/boards/rurp_config_storage_eeprom.cpp`, `src/rurp_config_utils.cpp`. `tests/test_config_storage_seam_shape.py` (14 tests) still passes unchanged.

**C-3 detector, observed counts:** `test_manifest_names_the_flash_driver` scanned **8 files** under `platform/py32f071/src/` and found **6 HAL_FLASH_ call sites**, all in `config_storage_flash.cpp` (`HAL_FLASH_Unlock` ×2, `HAL_FLASH_Erase` ×1, `HAL_FLASH_Program` ×1, `HAL_FLASH_Lock` ×2). The antecedent is real and nonzero, so the implication is non-vacuous.

**Planted-copy RED demonstration (Task 2), all three variants produced a non-empty violation list:**
1. Manifest text with the `py32f071_hal_flash.c` entry removed, antecedent forced to 1 → `_violations_manifest_names_flash_driver` reported the missing-entry violation.
2. Glue TU text with an appended `FLASH->CR = 0;` line → `_violations_hal_entry_points_only` reported the direct-register-access violation. (Comment-stripping was required here: the real file's own explanatory comment `"...never pokes FLASH->CR directly (C-4)."` initially tripped a naive regex on the first run; the helper strips `/* */` and `//` comments before matching, exactly like `test_config_storage_seam_shape.py`'s established idiom, so a prose citation is never mistaken for real register access.)
3. Core TU text with `#include "py32f071_hal.h"` prepended → `_violations_core_hal_free` reported the unsanctioned-local-include violation.

Blob SHAs of `CMakeLists.txt`, `config_storage_flash.cpp` and `config_storage_dualslot.cpp` confirmed unchanged before/after the planted-copy test.

**Regression counts:**
- `python3 -m pytest tests/ -q`: **138 → 144 passed** (+6, exactly the new functions; zero regressions).
- `pio test -e native`: **141 test cases: 141 succeeded**, 17 suites.
- `pio test -e native_nodevtools`: **141 test cases: 141 succeeded**, 17 suites.
- AVR builds, compared against `scripts/baseline/size_baseline.json` (Plan 124's recorded post-landing figures): `uno` flash 23954/32256, RAM 1573/2048 — unchanged; `uno328pb` flash 24004/32384, RAM 1579/2048 — unchanged; `leonardo` flash 26016/28672, RAM 2014/2560 — unchanged. **Zero movement on all three**, as expected — this commit touches no AVR-compiled source file.

**Hash checks (hard constraints), all unchanged:**
- `include/rurp_shield.h` = `602fe6f326a042ab71efd111e4dfcf3a6e41dd46`
- `include/rurp_types.h` = `d3fe5203a91527bdb7b20a33843c81065e21c613`
- `include/rurp_config_storage.h` = `1d74d0ede91853c2ce2bcc0bda1eb8fe8a07e5b2`
- `platformio.ini` = `f4e720ba75a8c618cc23bac045ab65084d41a0a4`
- `platform/py32f071/linker/PY32F071xB_FLASH.ld` = `571a588b0521e9602d98f735e3166a9869dab3aa`
- `CONFIG_VERSION` in `include/rurp_shield.h` is still the literal `"VER06"`.

**Commit SHAs and changed paths:**
- `5b08495` (feat) — `platform/py32f071/CMakeLists.txt`, `platform/py32f071/src/config.cpp` (deleted), `platform/py32f071/src/config_storage_flash.cpp` (created), `scripts/check_cmake_manifest.py` — exactly 4 paths, one a deletion.
- `1d2c7f8` (test) — `tests/test_py32_flash_map.py` — exactly 1 path.

**Gitignored py32 worktrees:** `git -C /workspaces/firestarter_py32_ci status --porcelain` and `git -C /workspaces/firestarter_app_py32 status --porcelain` both produced no output (untouched).

**Branch re-check (both repos, RESEARCH Pitfall 7):** `git -C /workspaces/firestarter rev-parse --abbrev-ref HEAD` → `v1.23-py32f071-integration` after both commits. Meta repo (`/workspaces`) SUMMARY commit lands separately per this plan's protocol.

**No requirement checkbox ticked:** confirmed by re-reading `.planning/REQUIREMENTS.md` after both commits — CFG-05, CFG-06, CFG-07 all still `[ ]`. CFG-05 spans this plan + 126-07 + 126-09; CFG-06 spans 126-06 + this plan; CFG-07 spans 126-03 + this plan + 126-10's gate. Only Plan 126-12 may tick any of them.

## Decisions Made

- Included the board header (`boards/py32f071_rurp_shield.h`) rather than `py32f071_hal.h` directly, matching `timing.cpp`'s established convention (and this plan's own `read_first` guidance) over `126-RESEARCH.md`'s illustrative code snippet, which used the direct include as a simplification for exposition.
- Gave `hal_read`/`hal_erase_page`/`hal_program_page` `extern "C"` linkage. The plan's action text names this explicitly only for the two seam functions, but `rurp_flash_primitives_t` is declared inside `config_storage_dualslot.h`'s `extern "C" { ... }` block, so its function-pointer members carry C language linkage in C++ — matching the primitive functions' own linkage to that type is what makes the file-local primitive-table initializer well-typed without relying on a compiler-specific relaxation.
- Comment-stripped the two new HAL-scanning regexes in `tests/test_py32_flash_map.py` (discovered mid-task: a first run of `test_the_flash_glue_uses_only_hal_entry_points` false-failed on the glue TU's own explanatory comment naming `FLASH->CR` in prose). Fixed by adopting the same `_COMMENT_RE` idiom `test_config_storage_seam_shape.py` already uses, rather than rewording the source comment to dodge the regex — the regex was the thing insufficiently robust, not the comment.
- Kept the manifest edit ordering exactly as specified: deletion + all four `CMakeLists.txt`/docstring changes in one commit, so the duplicate-symbol ARM-link window (promoting `rurp_config_utils.cpp` while `config.cpp` still defined the same four functions) was never opened, per Plan 126-03's deferral and this plan's own threat-model row T-126-08-07.

## Deviations from Plan

**1. [Rule 1 - Bug] Comment-stripping added to two new textual-gate helpers in `tests/test_py32_flash_map.py`**
- **Found during:** Task 2, first run of `test_the_flash_glue_uses_only_hal_entry_points`.
- **Issue:** The naive regex `_DIRECT_REGISTER_RE` matched the literal text `FLASH->CR` inside `config_storage_flash.cpp`'s own explanatory comment (`"...never pokes FLASH->CR directly (C-4)."`), producing a false-positive violation despite the source containing zero actual register access.
- **Fix:** Added a `_COMMENT_RE` (`/\* ... \*/` and `// ...`) strip, applied before both the HAL-call scan and the register-access scan, following the identical idiom already established in `tests/test_config_storage_seam_shape.py`. No source comment was reworded.
- **Files modified:** `firestarter/tests/test_py32_flash_map.py` (within the same Task 2 commit, before it landed — not a separate fix commit).
- **Verification:** `pytest tests/test_py32_flash_map.py -v` — all 20 functions pass; the RED demonstration (`test_manifest_helper_reports_violations_on_planted_copies`) still produces a real violation for a genuinely planted `FLASH->CR = 0;` line, confirming the fix did not blunt the gate.
- **Commit:** `1d2c7f8` (the fix was made before the task's single commit, per this being a within-task bug caught during self-verification, not a post-commit patch).

---

**Total deviations:** 1 auto-fixed (Rule 1 - bug in a test helper's own regex, caught before commit).
**Impact on plan:** No scope creep — the fix is confined to the two new helper functions' comment-handling and does not change any assertion's intent or any acceptance criterion.

## Issues Encountered

None beyond the deviation above.

## User Setup Required

None — no external service configuration required.

## Non-Claims (Claim Ceiling, explicit)

- **The ARM link is NOT proven here.** `arm-none-eabi-gcc`, `cmake` and `ninja` are absent from this environment. The manifest names `py32f071_hal_flash.c` and the local `pytest` detector proves the antecedent is real and checks the manifest text, but neither compiles nor links anything. **Plan 126-11's gated CI run is the sole authoritative evidence** that the ARM target actually links against these new sources.
- No PY32F071 silicon exists, and nothing here claims behaviour observed on real hardware.
- No claim about first-boot write timing or DFU preservation — out of scope for this plan.

## Next Phase Readiness

- `config_storage_flash.cpp`'s primitives and seam functions are ready for Plan 126-09 to exercise the shared core (`config_storage_dualslot.cpp`, compiled by path, unchanged by this plan) against its own RAM fake — this plan did not modify that core.
- The manifest is closed at 26/15/5; Plan 126-10's schema-pinning gate and Plan 126-11's gated ARM CI run are the remaining consumers of this plan's C-3 fix.
- No blockers. Both native envs remain at 141/141 across 17 suites; `pytest tests/` is now at 144; all three AVR builds byte-identical to the Plan 124 baseline; the manifest gate is green at 26 enforced sources.

---
*Phase: 126-flash-persistent-config-via-a-storage-backend-seam-highest-r*
*Completed: 2026-08-01*
