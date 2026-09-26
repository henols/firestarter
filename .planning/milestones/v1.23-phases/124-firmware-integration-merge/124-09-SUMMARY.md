---
phase: 124-firmware-integration-merge
plan: "09"
subsystem: firmware-safety
tags: [firestarter, py32f071, pinmap-guard, preprocessor, cmake, pytest, drift-gate]

# Dependency graph
requires:
  - phase: 124-firmware-integration-merge
    plan: "05"
    provides: "The green check_cmake_manifest.py (23 resolved / 14 exempt / 5 allow-listed) this plan edits the same file against and re-confirms."
  - phase: 124-firmware-integration-merge
    plan: "08"
    provides: "The board-header bridging block (RURP_PY32F071_PINMAP_PROVISIONAL -> RURP_PINMAP_PROVISIONAL) this plan sits beside without disturbing, and the fully-green firestarter/tests/ (66 passed) this plan's new suite extends."
provides:
  - "include/boards/py32f071_pinmap_guard.h -- a dependency-free fragment header carrying the pin-map #error guard, evaluable by a host preprocessor standalone"
  - "The board header (include/boards/py32f071_rurp_shield.h) no longer #defines RURP_PY32F071_PINMAP_CONFIGURED; it only #includes the fragment and tests the macro the build supplies"
  - "RURP_PY32F071_PINMAP_CONFIGURED=1 supplied by platform/py32f071/CMakeLists.txt's target_compile_definitions -- the only place that macro is now defined"
  - "tests/test_pinmap_guard_fires.py -- a three-armed g++ -E fire-proof (unset/=1/=0) proving the guard is structurally able to fire, plus regression guards against the hollow shape and silent-skip returning"
affects: [124-11, 124-12, 124-close]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "A dependency-free fragment header hoisted out of a HAL-including board header so a host preprocessor (no ARM toolchain) can evaluate a compile-time guard standalone"
    - "`!defined(X) || !X` stated explicitly (not a bare `!X`) so the unset arm fires deliberately, documented, and survives a later -Wundef"
    - "The configured macro moved from header-resident #define to CMake target_compile_definitions, so the header only tests what the build supplies -- mirrors the DEV_TOOLS value-semantics conversion's shape (source in the build config, tested via #if in shared code)"
    - "Self-referential grep-count acceptance criteria in a test module require needle strings built via concatenation, not written verbatim, or the test's own source trips its own check"

key-files:
  created:
    - firestarter/include/boards/py32f071_pinmap_guard.h
    - firestarter/tests/test_pinmap_guard_fires.py
  modified:
    - firestarter/include/boards/py32f071_rurp_shield.h
    - firestarter/platform/py32f071/CMakeLists.txt

key-decisions:
  - "The include-line and #define-line comments in the board header and CMakeLists.txt were worded to avoid repeating the literal strings '#error', 'py32f071_pinmap_guard.h', and 'RURP_PY32F071_PINMAP_CONFIGURED' a second time within the same file, after the plan's own grep-count acceptance criteria (exact counts of 1) were tripped by otherwise-natural explanatory prose mentioning those same literals. Reworded rather than weakened the acceptance criteria."
  - "Chose `!defined(X) || !X` (not `!X` alone) per RESEARCH.md's explicit recommendation, so the unset arm's fire is a stated design intent (visible to a reader and to a later -Wundef build) rather than an accidental consequence of #if's undefined-identifier-as-0 behavior."
  - "The guard #include was placed immediately after Plan 124-08's bridging block (before the RURP_PY32F071_ENABLE_GPIO_CLOCKS macro and all pin definitions), so it fires before any pin definition it protects, while leaving PROVISIONAL and the bridging block completely untouched per the plan's explicit instruction."
  - "In tests/test_pinmap_guard_fires.py's own self-check test (coverage 6), the 'pytest.skip' and 'mark.skipif' needle strings are built via string concatenation at runtime rather than written as a literal, because a verbatim needle in the assertion message would make the test's own source trip its own check -- a subtlety not called out in the plan and worth recording for the next self-referential test writer."
  - "No fixture translation unit was committed for the fire-proof: _write_tu() builds a fresh minimal TU (a single #include line) in tmp_path on every run, per the plan's explicit instruction that the point of the hoist is proving the fragment stands alone."

requirements-completed: []
# Per this plan's dispatch <requirement_ticking_scope>: .planning/REQUIREMENTS.md is
# NOT touched. Plan 124-12 is the sole owner of every MERGE-01..MERGE-08 tick.
# What is proved here: MERGE-04's second half (the #error guard restructured
# and provably able to fire, three arms measured with a real host compiler)
# and MERGE-08's ARM-side surface (the configured macro as an explicit CMake
# build definition with a recorded rationale).

coverage:
  - id: D1
    description: "The pin-map #error guard is hoisted into a dependency-free fragment header (include/boards/py32f071_pinmap_guard.h) that a host preprocessor can evaluate standalone, and proven to discriminate on all three arms: macro unset -> fails, =1 -> succeeds, =0 -> fails"
    requirement: "MERGE-04"
    verification:
      - kind: unit
        ref: "g++ -E -Iinclude/boards {unset,DEFINE=1,DEFINE=0} tu.cpp -o /dev/null -- observed exit 1 (#error, unset), exit 0 (=1), exit 1 (#error, =0), matching RESEARCH.md's hand-executed arms"
        status: pass
      - kind: unit
        ref: "python3 -m pytest tests/test_pinmap_guard_fires.py -q -rs -- 6 passed, 0 skipped, 0 failed"
        status: pass
    human_judgment: false
  - id: D2
    description: "The board header no longer defines what it tests -- RURP_PY32F071_PINMAP_CONFIGURED's #define is removed from include/boards/py32f071_rurp_shield.h with no #ifndef-wrapped fallback left behind, and the duplicated #if !CONFIGURED / #error block is removed (the wrong-platform guard and the data-bus-shift guard survive)"
    requirement: "MERGE-04"
    verification:
      - kind: unit
        ref: "grep -cE '^#define RURP_PY32F071_PINMAP_CONFIGURED' include/boards/py32f071_rurp_shield.h == 0; #error count in board header: 3 (pre-edit) -> 2 (post-edit, minus one); grep -c py32f071_pinmap_guard.h include/boards/py32f071_rurp_shield.h == 1"
        status: pass
      - kind: unit
        ref: "python3 scripts/check_orphan_provisional.py -- PASS: RURP_PINMAP_PROVISIONAL (3 consumer(s)), RURP_PY32F071_PINMAP_PROVISIONAL (1 consumer(s)) -- unchanged from Plan 124-08, Plan 124-08's bridging block undisturbed"
        status: pass
    human_judgment: false
  - id: D3
    description: "The ARM build supplies RURP_PY32F071_PINMAP_CONFIGURED=1 via platform/py32f071/CMakeLists.txt's target_compile_definitions (the only place it is now defined), and check_cmake_manifest.py is re-run (not assumed unaffected) after editing the same file Plan 124-05 greened, reproducing its exact PASS line"
    requirement: "MERGE-08"
    verification:
      - kind: unit
        ref: "grep -c RURP_PY32F071_PINMAP_CONFIGURED platform/py32f071/CMakeLists.txt == 1; python3 scripts/check_cmake_manifest.py -- PASS line textually identical to Plan 124-05's recorded PASS (23 resolved / 14 exempt / 5 allow-listed omissions); git diff HEAD shows only the added definition + comment"
        status: pass
    human_judgment: false
  - id: D4
    description: "The fire-proof pytest fails closed with no host compiler present (fail-closed _resolve_compiler copied from the in-tree analog, no skip decorator or call anywhere in the module), and does not regress the firmware suite, both pinned native envs, or AVR flash/RAM"
    requirement: "MERGE-04"
    verification:
      - kind: unit
        ref: "grep -c 'pytest.skip\\|mark.skipif' tests/test_pinmap_guard_fires.py == 0; grep -c 'shell=True' tests/test_pinmap_guard_fires.py == 0"
        status: pass
      - kind: unit
        ref: "python3 -m pytest tests/ -q -- 72 passed, 0 failed (supersedes Plan 124-08's recorded 66)"
        status: pass
      - kind: unit
        ref: "pio test -e native -- 141 test cases: 141 succeeded (17 suites); pio test -e native_nodevtools -- 141 test cases: 141 succeeded (17 suites); both re-run after all three edits"
        status: pass
      - kind: unit
        ref: "pio run -e uno/-e uno328pb/-e leonardo -- flash/RAM: uno 23954/1573, uno328pb 24004/1579, leonardo 26016/2014 -- all six figures byte-identical to Plan 124-05/124-08's recorded landing figures"
        status: pass
    human_judgment: false

duration: ~40min
completed: 2026-07-31
status: complete
---

# Phase 124 Plan 09: Pin-Map Guard Restructure (MERGE-04, D-14) Summary

**Hoisted the PY32F071 pin-map `#error` guard into a dependency-free fragment header, moved the configured macro's `#define` out of the board header and into the ARM build's CMake compile definitions, and proved the guard fires on all three discriminating arms with a real host compiler.**

## Performance

- **Duration:** ~40 min
- **Tasks:** 3 completed
- **Files modified:** 4 (2 created, 2 modified)

## Accomplishments

- **Task 1:** Created `include/boards/py32f071_pinmap_guard.h` — a `#pragma once`, zero-`#include` fragment header carrying `#if !defined(RURP_PY32F071_PINMAP_CONFIGURED) || !RURP_PY32F071_PINMAP_CONFIGURED` → `#error`, with a comment block recording why the hoist is mandatory (the full board header includes `py32f0xx_hal.h`, unresolvable locally). Removed `#define RURP_PY32F071_PINMAP_CONFIGURED 1` from the board header (no `#ifndef`-wrapped fallback left behind), inserted `#include "py32f071_pinmap_guard.h"` immediately after Plan 124-08's bridging block (before the pin definitions it protects), and removed the now-duplicated `#if !RURP_PY32F071_PINMAP_CONFIGURED` / `#error` block. The wrong-platform guard (line 9-11) and the data-bus-shift guard (unchanged, now further down the file) both survive intact. `check_orphan_provisional.py` re-confirmed PASS — Plan 124-08's consumers undisturbed.
- **Task 2:** Added `RURP_PY32F071_PINMAP_CONFIGURED=1` to the ARM target's `target_compile_definitions` in `platform/py32f071/CMakeLists.txt`, with a comment recording D-14's mechanism and why the ARM target is the only place it needs to be supplied. Re-ran `check_cmake_manifest.py` (this plan edits the same file Plan 124-05 greened) — PASS line textually identical to Plan 124-05's recorded PASS.
- **Task 3:** Created `tests/test_pinmap_guard_fires.py` (6 test cases), copying `_resolve_compiler()`'s fail-closed shape verbatim in spirit from `test_check_build_warnings.py`. Preprocesses the fragment header standalone across three arms with `g++ -E`, deriving the expected `#error` text from the fragment at test time (never hardcoded twice). Added two regression-guard tests (fragment is dependency-free; board header no longer defines what it tests) and one self-check test (the module itself contains no skip construct). Full firmware suite re-run: 72 passed, 0 failed.

## Task Commits

Each task committed atomically, inside the `firestarter` submodule on branch `v1.23-py32f071-integration`.

1. **Task 1: Hoist the guard into a dependency-free fragment header** - `fc299bf` (feat)
2. **Task 2: Supply the configured macro from the ARM build definitions** - `f67f6b8` (feat)
3. **Task 3: The three-armed g++ -E fire-proof** - `2bd7187` (test)

## Files Created/Modified

- `firestarter/include/boards/py32f071_pinmap_guard.h` (created) — dependency-free fragment header carrying the `#error` guard
- `firestarter/include/boards/py32f071_rurp_shield.h` (modified) — removed the header-resident `#define`, added the `#include`, removed the duplicated guard block
- `firestarter/platform/py32f071/CMakeLists.txt` (modified) — added `RURP_PY32F071_PINMAP_CONFIGURED=1` to `target_compile_definitions` with a rationale comment
- `firestarter/tests/test_pinmap_guard_fires.py` (created) — 6-case fire-proof pytest

## Observed Verification Values

### Task 1 — the fragment header and board-header edit

- `test -f include/boards/py32f071_pinmap_guard.h` → succeeds.
- `grep -c '#include' include/boards/py32f071_pinmap_guard.h` → **0** (dependency-free).
- `grep -cE '^#define RURP_PY32F071_PINMAP_CONFIGURED' include/boards/py32f071_rurp_shield.h` → **0**.
- `grep -c 'PINMAP_CONFIGURED' include/boards/py32f071_pinmap_guard.h` → **3** (comment prose + the `#if` condition, which tests both defined-ness and value).
- `grep -c '#error' include/boards/py32f071_pinmap_guard.h` → **1**. The message, quoted in full:
  ```
  "RURP_PY32F071_PINMAP_CONFIGURED is not set: the PY32F071 Firestarter wiring
  is not configured for this build. This macro must be supplied by the build
  system (platform/py32f071/CMakeLists.txt's target_compile_definitions), not
  by this header."
  ```
- `grep -c '#error' include/boards/py32f071_rurp_shield.h` → **2** (pre-edit was 3: the wrong-platform guard, the removed CONFIGURED guard, and the data-bus-shift guard — post-edit is the pre-edit count minus one). The surviving two: the wrong-platform guard (`"py32f071_rurp_shield.h included for the wrong platform"`) and the data-bus-shift guard (`"The contiguous PY32F071 D0-D7 bus must fit within one 16-pin GPIO port"`).
- `grep -c 'py32f071_pinmap_guard.h' include/boards/py32f071_rurp_shield.h` → **1**.
- `python3 scripts/check_orphan_provisional.py` → `PASS: RURP_PINMAP_PROVISIONAL (3 consumer(s)), RURP_PY32F071_PINMAP_PROVISIONAL (1 consumer(s))` — exit 0, unchanged from Plan 124-08.
- **The three arms, run directly with `g++ -E` before writing the pytest** (confirming the fragment behaves correctly before it was ever wrapped in a test):
  ```
  unset:  exit=1  include/boards/py32f071_pinmap_guard.h:42:2: error: #error "RURP_PY32F071_PINMAP_CONFIGURED is not set: ..."
  =1:     exit=0  (no error)
  =0:     exit=1  include/boards/py32f071_pinmap_guard.h:42:2: error: #error "RURP_PY32F071_PINMAP_CONFIGURED is not set: ..."
  ```

### Task 2 — the CMake definition and manifest re-confirmation

- `grep -c 'RURP_PY32F071_PINMAP_CONFIGURED' platform/py32f071/CMakeLists.txt` → **1**, inside `target_compile_definitions`, value `1`.
- `python3 scripts/check_cmake_manifest.py` (before this task's edit): `PASS: /workspaces/firestarter/platform/py32f071/CMakeLists.txt -- 23 enforced source(s) resolved across ['FIRESTARTER_COMMON_SOURCES', 'PY32_PLATFORM_SOURCES']; 14 PY32_SDK_SOURCES entries structurally exempt (FetchContent -- PY32_SDK_ROOT resolves only after a networked cmake configure); allow-listed omission(s): src/boards/leonardo_rurp_shield.cpp, src/boards/rurp_common.cpp, src/boards/uno_rurp_shield.cpp, src/dev_tools.cpp, src/rurp_config_utils.cpp`
- **After** this task's edit: identical PASS line (byte-for-byte), exit 0 — the new definition does not change resolved/exempt/allow-listed counts because it adds nothing to any source list.
- `git diff HEAD -- platform/py32f071/CMakeLists.txt` (pre-commit): shows only the added `RURP_PY32F071_PINMAP_CONFIGURED=1` line plus its 8-line rationale comment above `target_compile_definitions`.
- **ARM configure/build is NOT verified locally** — no ARM toolchain exists in this devcontainer. Plan 124-11's CI run URL and head SHA is the evidence route for whether the ARM target still configures and builds with this definition present.

### Task 3 — the fire-proof pytest

- `python3 -m pytest tests/test_pinmap_guard_fires.py -q -rs` → **6 passed, 0 skipped, 0 failed** (no `SKIPPED` lines).
- Return codes recorded per arm: unset → **1**, `=1` → **0**, `=0` → **1**. Both firing arms (unset, `=0`) quote the compiler's own error line verbatim in the assertion failure message path (captured in `result.stderr`, matched against the fragment's own `#error` text read at test time via `_expected_error_text()`).
- `grep -c 'pytest.skip\|mark.skipif' tests/test_pinmap_guard_fires.py` → **0**.
- `grep -c 'shell=True' tests/test_pinmap_guard_fires.py` → **0**.
- The expected error text literal (`"RURP_PY32F071_PINMAP_CONFIGURED is not set: ..."`) does **not** appear anywhere in the test module's source — verified by grep; it is derived from the fragment header at runtime via `_expected_error_text()`.
- `python3 -m pytest tests/ -q` → **72 passed, 0 failed** — supersedes Plan 124-08's recorded 66.
- `pio test -e native` → **141 test cases: 141 succeeded** (17 suites). `pio test -e native_nodevtools` → **141 test cases: 141 succeeded** (17 suites). Both re-run after all three edits in this plan.
- AVR clean builds, re-measured: `uno` flash **23954**/RAM **1573**; `uno328pb` flash **24004**/RAM **1579**; `leonardo` flash **26016**/RAM **2014** — all six figures byte-identical to Plan 124-05/124-08's recorded landing figures. This plan touches only a py32-only header and the py32 CMakeLists.txt, neither compiled into any AVR env, so zero AVR delta was expected and confirmed.
- `git status --porcelain` (firestarter submodule, end of plan): empty after the Task 3 commit.

## Decisions Made

See `key-decisions` in frontmatter for the full list. Highlights: the `!defined(X) || !X` condition form (not a bare `!X`) per RESEARCH.md's explicit recommendation; comments in the board header and CMakeLists.txt reworded (not weakened acceptance criteria) to avoid tripping the plan's own exact-count grep assertions on `#error`, the fragment filename, and the macro name; the fire-proof's self-check test builds its "pytest.skip"/"mark.skipif" needle strings via concatenation so the test's own source does not trip its own check; no fixture translation unit committed — `_write_tu()` builds a fresh minimal TU per run, proving the fragment stands alone.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Self-tripping grep-count acceptance criteria in initial draft**
- **Found during:** Task 1 and Task 3 verification
- **Issue:** The plan's acceptance criteria require exact `grep -c` counts of 1 for `'#error'` (fragment header), `'py32f071_pinmap_guard.h'` (board header), and `'RURP_PY32F071_PINMAP_CONFIGURED'` (CMakeLists.txt) — but the first-draft explanatory comments naturally repeated those same literal strings in prose, inflating each count to 2. Similarly, the plan's own acceptance criteria for `'pytest.skip\|mark.skipif'` and `'shell=True'` returning 0 in the new test module were tripped by the test module's own comments/assertion-message text describing what it checks for.
- **Fix:** Reworded the comment prose in the fragment header, the board header, and CMakeLists.txt to avoid repeating the literal grep targets a second time (e.g. "error text" instead of "#error text", "the fragment header included directly below" instead of the filename, "the pin-map ... macro" instead of the full macro name). In the test module, built the `"pytest.skip"` and `"mark.skipif"` needle strings via runtime string concatenation rather than writing them verbatim, and reworded the docstring's mention of `shell=True` to "the shell is never invoked".
- **Verification:** Every grep-count acceptance criterion in the plan now returns the exact value specified; `python3 -m pytest tests/test_pinmap_guard_fires.py -q -rs` still reports 6 passed with no behavioral change to the tests themselves.
- **Committed in:** `fc299bf`, `f67f6b8`, `2bd7187` (part of each task's own commit — the wording was corrected before committing, not as a separate fix commit)

---

**Total deviations:** 1 auto-fixed (self-tripping grep-count acceptance criteria, a wording issue caught during the plan's own verification step, not a functional defect).
**Impact on plan:** None on scope or correctness — purely comment/prose wording adjusted to satisfy the plan's own literal acceptance-criteria greps without weakening any assertion.

## Issues Encountered

- The self-tripping grep-count issue described above under Deviations. No other issues.

## User Setup Required

None — no external service configuration required.

## Requirement Ticking Scope

Per this plan's dispatch `<requirement_ticking_scope>`, `.planning/REQUIREMENTS.md` was **not** touched. What was proved: MERGE-04's second half (the `#error` guard restructured into a dependency-free fragment, provably able to fire on all three discriminating arms with a real host compiler, plus a regression guard against the hollow shape returning) and MERGE-08's ARM-side surface (`RURP_PY32F071_PINMAP_CONFIGURED=1` as an explicit CMake build definition with a recorded rationale). Plan 124-12 owns citing this evidence when it ticks MERGE-04/MERGE-08.

## Next Phase Readiness

- The pin-map guard is structurally able to fire: proven with `g++ -E` directly and with a permanent 6-case pytest, `tests/test_pinmap_guard_fires.py`.
- `check_cmake_manifest.py` and `check_orphan_provisional.py` both re-confirmed PASS after this plan's edits.
- `firestarter/tests/` is now **72 passed, 0 failed** (supersedes Plan 124-08's recorded 66).
- Both pinned native envs remain at exactly 141 cases / 17 suites.
- AVR flash/RAM figures unchanged from Plan 124-05/124-08's recorded landing figures: uno 23954/1573, uno328pb 24004/1579, leonardo 26016/2014.
- ARM configure/build with the new `RURP_PY32F071_PINMAP_CONFIGURED=1` definition present is **explicitly unclaimed** here — no ARM toolchain exists in this devcontainer. Plan 124-11's CI run URL and head SHA is the evidence route.
- No blockers for Plan 124-11 or 124-12.

## Self-Check: PASSED

- FOUND: `firestarter/include/boards/py32f071_pinmap_guard.h`
- FOUND: `firestarter/include/boards/py32f071_rurp_shield.h` (modified)
- FOUND: `firestarter/platform/py32f071/CMakeLists.txt` (modified)
- FOUND: `firestarter/tests/test_pinmap_guard_fires.py`
- FOUND commit `fc299bf` (firestarter submodule) — `git log --oneline --all | grep fc299bf` matches
- FOUND commit `f67f6b8` (firestarter submodule) — `git log --oneline --all | grep f67f6b8` matches
- FOUND commit `2bd7187` (firestarter submodule) — `git log --oneline --all | grep 2bd7187` matches

---
*Phase: 124-firmware-integration-merge*
*Completed: 2026-07-31*
