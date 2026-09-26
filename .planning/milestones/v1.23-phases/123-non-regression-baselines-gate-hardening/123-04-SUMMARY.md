---
phase: 123-non-regression-baselines-gate-hardening
plan: 04
subsystem: build-measurement-baselines
tags: [cmake, py32f071, drift-gate, coarse-key-arming, allow-list]

requires:
  - phase: 123-non-regression-baselines-gate-hardening (plan 01)
    provides: firestarter/tests/fixtures/ naming discipline, milestone branch
provides:
  - firestarter/scripts/check_cmake_manifest.py (BASE-04 CMake source-list drift gate)
  - PY32_EXCLUDED allow-list comment format contract (path -- reason, reason mandatory)
  - 4 committed fixture trees proving forward/reverse/arming/unknown-list behaviour
affects:
  - Phase 124 MERGE-01/MERGE-02 (the gate that catches the flash_type_3/4 rename defect)
  - Phase 123 Plan 06 (BASE-08 checker-convention meta-test)
  - Phase 123 Plan 11 (requirement closure for BASE-04/BASE-08)

tech-stack:
  added: []
  patterns:
    - "coarse-key arming on a directory, never a manual flip constant (D-07)"
    - "scope-by-variable set() parsing: enforce two lists, structurally exempt one, reject unknown ones as exit 2"
    - "reasoned allow-list: PY32_EXCLUDED: <path> -- <reason>, reason mandatory"

key-files:
  created:
    - firestarter/scripts/check_cmake_manifest.py
    - firestarter/tests/test_check_cmake_manifest.py
    - firestarter/tests/fixtures/planted_cmake_manifest_missing_source/ (6 files)
    - firestarter/tests/fixtures/planted_cmake_manifest_excluded_no_reason/ (5 files)
    - firestarter/tests/fixtures/clean_cmake_manifest_excluded/ (5 files)
    - firestarter/tests/fixtures/clean_unarmed_tree/ (2 files)
  modified: []

key-decisions:
  - "PATH_RE requires a (?!\\w) boundary after the recognised extension so a greedy backtrack can never misclassify CMAKE_TOOLCHAIN_FILE's '.cmake' as a bogus '.c' source entry — a correction to the naive regex sketched in 123-PATTERNS.md's code example, verified by hand-tracing the backtrack against the real manifest's non-source set() calls (TARGET_NAME, REPOSITORY_ROOT, PY32_SDK_ROOT, LINKER_SCRIPT, CMAKE_TOOLCHAIN_FILE) before committing."
  - "Missing/unparseable manifest under an armed key, and an unrecognised source-list name, both exit 2 (config/parse error class) rather than 1 — consistent with check_size_baseline.py/check_build_warnings.py's three-way exit taxonomy for parsing gates, rather than the two-way ValueError->1 shape check_no_log_in_sdp_window.py uses for its narrower single-anchor case."
  - "Never-vacuous guard folded into the violations list (prepended) rather than a separate early-return branch, so a zero-enforced-sources state can never coincidentally look like a pass even if other logic paths changed."

requirements-completed: []

coverage:
  - id: D1
    description: "check_cmake_manifest.py exists, ships UNARMED (exit 0) on the real tree, and no manual arm-flip constant exists anywhere in it"
    verification:
      - kind: unit
        ref: "tests/test_check_cmake_manifest.py#test_unarmed_on_the_real_tree_with_no_seam_override"
        status: pass
    human_judgment: false
  - id: D2
    description: "Once armed, a mismatched source path is exactly 1 violation, never inflated by the 14 structurally-exempt PY32_SDK_SOURCES entries"
    verification:
      - kind: unit
        ref: "tests/test_check_cmake_manifest.py#test_mismatched_path_fails_with_exactly_one_violation"
        status: pass
    human_judgment: false
  - id: D3
    description: "PY32_EXCLUDED allow-list entries without a stated reason fail; entries with a reason pass and are named on the PASS: line"
    verification:
      - kind: unit
        ref: "tests/test_check_cmake_manifest.py#test_unreasoned_allow_list_entry_fails"
        status: pass
      - kind: unit
        ref: "tests/test_check_cmake_manifest.py#test_reasoned_omission_passes_and_is_named"
        status: pass
    human_judgment: false
  - id: D4
    description: "A rename/deletion of the manifest inside an armed platform/py32f071/ is a hard failure, never a silent reversion to UNARMED (D-07's core guarantee)"
    verification:
      - kind: unit
        ref: "tests/test_check_cmake_manifest.py#test_armed_but_manifest_missing_is_a_hard_failure"
        status: pass
    human_judgment: false
  - id: D5
    description: "An unrecognised set() source list is exit 2, never silently ignored"
    verification:
      - kind: unit
        ref: "tests/test_check_cmake_manifest.py#test_unknown_source_list_is_exit_2"
        status: pass
    human_judgment: false

duration: 35min
completed: 2026-07-31
status: complete
---

# Phase 123 Plan 04: BASE-04 CMake Source-List Drift Gate Summary

**`check_cmake_manifest.py` — coarse-key-armed on `platform/py32f071/`, scopes CMake `set()` parsing by variable (enforce 2 lists, structurally exempt the FetchContent-backed SDK list, reject unknown lists as exit 2), and defines the `PY32_EXCLUDED: <path> -- <reason>` allow-list contract Phase 124 will populate.**

## Performance

- **Duration:** ~35 min
- **Tasks:** 3/3 complete
- **Files created:** 20 (1 checker, 1 pytest, 18 fixture files across 4 trees)

## Accomplishments

- `firestarter/scripts/check_cmake_manifest.py` — parses the three real `set()` source
  lists read off `/workspaces/firestarter_py32_ci/platform/py32f071/CMakeLists.txt`
  (`FIRESTARTER_COMMON_SOURCES`, `PY32_PLATFORM_SOURCES`, `PY32_SDK_SOURCES`), enforces
  the first two, structurally exempts the third with a stated FetchContent reason, and
  ships UNARMED + exit 0 on today's tree (no `platform/py32f071/` yet).
- The gate arms itself on the `platform/py32f071/` **directory**, never a manual flip
  constant — a rename inside the port cannot disarm it; only deleting the whole
  directory can, and that reports UNARMED honestly rather than silently.
- `PY32_EXCLUDED: <path> -- <reason>` allow-list format defined and enforced (reason
  mandatory) — a new contract this phase authors, Phase 124 populates with the five
  measured omissions.
- Four committed fixture trees prove: exactly-1-violation with SDK entries exempt,
  unreasoned-entry failure, reasoned-omission pass (named on `PASS:`), and the D-07
  hard-failure (armed + manifest deleted ≠ UNARMED).
- 8 subprocess-driven pytest tests; firmware suite now **33 passed, 0 skipped** (was 25
  going in — this plan added 8).

## Exact `UNARMED:` line the real tree produces

```
UNARMED: /workspaces/firestarter/platform/py32f071 absent -- this gate arms itself the moment Phase 124 lands the py32f071 port (no manual flip needed; a rename inside the port cannot disarm it either).
```

## Observed violation count and message per planted tree

- **`planted_cmake_manifest_missing_source/`** — exit 1, exactly 1 violation:
  ```
  FAIL: 1 violation(s) in .../planted_cmake_manifest_missing_source/platform/py32f071/CMakeLists.txt:
    FIRESTARTER_COMMON_SOURCES: '${REPOSITORY_ROOT}/src/proms/flash_type_3.cpp' -> .../src/proms/flash_type_3.cpp (not found)
  ```
  No `PY32_SDK_ROOT` string appears anywhere in the output — the two deliberately
  unresolvable SDK entries in this fixture are never counted (proves Pitfall 6 avoided).

- **`planted_cmake_manifest_excluded_no_reason/`** — exit 1, 2 violations (the malformed
  entry itself, plus the resulting uncovered tree omission):
  ```
  FAIL: 2 violation(s) in .../planted_cmake_manifest_excluded_no_reason/platform/py32f071/CMakeLists.txt:
    PY32_EXCLUDED entry missing its mandatory reason segment: 'src/boards/uno_rurp_shield.cpp' (required format is 'PY32_EXCLUDED: <path> -- <reason>')
    src/boards/uno_rurp_shield.cpp: present in tree, not named in FIRESTARTER_COMMON_SOURCES, and not covered by a reasoned PY32_EXCLUDED entry
  ```

- **`clean_cmake_manifest_excluded/`** — exit 0:
  ```
  PASS: .../clean_cmake_manifest_excluded/platform/py32f071/CMakeLists.txt -- 2 enforced source(s) resolved across ['FIRESTARTER_COMMON_SOURCES', 'PY32_PLATFORM_SOURCES']; 1 PY32_SDK_SOURCES entries structurally exempt (FetchContent -- PY32_SDK_ROOT resolves only after a networked cmake configure); allow-listed omission(s): src/boards/uno_rurp_shield.cpp
  ```

- **`clean_unarmed_tree/`** — exit 0, `UNARMED:` (no `platform/` directory at all;
  shared with plan 123-05).

## `PY32_EXCLUDED` comment format, as shipped verbatim (for Phase 124 to copy)

```cmake
# PY32_EXCLUDED: <path> -- <reason>
```
matched by `EXCLUDED_LINE_RE` (any `PY32_EXCLUDED:` comment line) then validated by
`EXCLUDED_RE` (`^(?P<path>\S+)\s*--\s*(?P<reason>.+?)\s*$`), where the reason group is
mandatory — an entry with a path but no `--` reason (or an empty reason after `--`)
fails validation and is reported as its own violation.

## The five expected initial exclusion paths (Phase 124 to write into the real manifest)

```cmake
# PY32_EXCLUDED: src/boards/uno_rurp_shield.cpp      -- AVR board impl, no ARM analogue
# PY32_EXCLUDED: src/boards/leonardo_rurp_shield.cpp  -- AVR board impl, no ARM analogue
# PY32_EXCLUDED: src/boards/rurp_common.cpp           -- AVR-specific common
# PY32_EXCLUDED: src/dev_tools.cpp                    -- DEV_TOOLS deliberately off on ARM (MERGE-08)
# PY32_EXCLUDED: src/rurp_config_utils.cpp            -- Phase 126 per-platform config
#                                                         backend split; THIS EXCLUSION
#                                                         WILL NEED REVISITING in Phase 126,
#                                                         it is not a permanent exclusion.
```

## Firmware suite count

`cd firestarter && python3 -m pytest tests/ -q` → **33 passed, 0 skipped** (25 going in
per 123-03-SUMMARY.md's baseline; this plan adds `test_check_cmake_manifest.py`'s 8
tests: 25 + 8 = 33, byte-exact against the plan's expected figure).

## Task Commits

1. **Task 1: Write scripts/check_cmake_manifest.py** — `13b1c28` (feat) —
   `firestarter/scripts/check_cmake_manifest.py`
2. **Task 2: Build the four fixture trees** — `d775036` (test) — 16 files across
   `firestarter/tests/fixtures/{planted_cmake_manifest_missing_source,planted_cmake_manifest_excluded_no_reason,clean_cmake_manifest_excluded,clean_unarmed_tree}/`
3. **Task 3: Write tests/test_check_cmake_manifest.py** — `8d5ecba` (test) —
   `firestarter/tests/test_check_cmake_manifest.py`

All three commits are inside the `firestarter` submodule on branch
`v1.23-py32f071-integration`. No plan-metadata doc commit was made in the meta repo for
this plan (per the `<sequential_execution>` protocol for this executor run — STATE.md /
ROADMAP.md updates and the final docs commit follow immediately after this SUMMARY).

## Files Created/Modified

- `firestarter/scripts/check_cmake_manifest.py` — the BASE-04 gate (360 lines)
- `firestarter/tests/test_check_cmake_manifest.py` — 8 subprocess-driven tests (240 lines)
- `firestarter/tests/fixtures/planted_cmake_manifest_missing_source/` — README + manifest +
  `platform/py32f071/src/main.cpp` + `src/firestarter.cpp` + `src/proms/eeprom_28c.cpp`
- `firestarter/tests/fixtures/planted_cmake_manifest_excluded_no_reason/` — README +
  manifest + `platform/py32f071/src/main.cpp` + `src/firestarter.cpp` +
  `src/boards/uno_rurp_shield.cpp`
- `firestarter/tests/fixtures/clean_cmake_manifest_excluded/` — README + manifest +
  `platform/py32f071/src/main.cpp` + `src/firestarter.cpp` + `src/boards/uno_rurp_shield.cpp`
- `firestarter/tests/fixtures/clean_unarmed_tree/` — README + `src/placeholder.cpp`

## Decisions Made

See `key-decisions` in frontmatter. In brief: fixed a real regex-boundary bug found while
hand-verifying `PATH_RE` against the actual manifest (the naive pattern sketched in
123-PATTERNS.md would have misclassified `CMAKE_TOOLCHAIN_FILE`'s `.cmake` extension as a
bogus `.c` source on backtrack); chose exit 2 for missing-manifest and unknown-list
(config/parse-error class, consistent with this phase's other two checkers) rather than
the narrower `ValueError`→1 shape of the single-anchor precedent; folded the
never-vacuous guard into the violations list rather than a separate branch.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] `PATH_RE` needed a trailing boundary assertion to avoid a false match**
- **Found during:** Task 1, while hand-tracing the regex against the real
  `CMakeLists.txt`'s non-source `set()` calls before committing.
- **Issue:** The naive `PATH_RE` sketched in 123-PATTERNS.md's code example
  (`"?(?P<path>[$\w{}/.\-]+\.(?:cpp|c|s|S))"?`) has no boundary after the extension
  alternation. Regex backtracking on a greedy `+` quantifier would let it match a bogus
  `...arm-none-eabi.c` fragment inside `CMAKE_TOOLCHAIN_FILE`'s real value
  (`.../cmake/arm-none-eabi.cmake`), because `\.c` alone is a valid alternative and
  nothing stops the match from landing mid-word. That would misclassify
  `CMAKE_TOOLCHAIN_FILE`'s `set()` block as an unrecognised "source list" → spurious
  exit 2 the moment Phase 124's real manifest (which does have this exact `set()` call)
  is read.
- **Fix:** Added a `(?!\w)` negative-lookahead boundary immediately after the extension
  alternation, so `.cmake`/`.ld`/other non-source extensions that merely start with a
  matched letter can never falsely satisfy the pattern. Verified by hand-tracing the
  backtrack against every non-source `set()` call in the real manifest
  (`TARGET_NAME`, `REPOSITORY_ROOT`, `PY32_SDK_ROOT`, `LINKER_SCRIPT`,
  `CMAKE_TOOLCHAIN_FILE`) — none now match `PATH_RE`.
- **Files affected:** `firestarter/scripts/check_cmake_manifest.py`.
- **Commit:** `13b1c28` (part of the initial Task 1 commit — caught before commit, not a
  follow-up fix).
- **Verification:** `python3 scripts/check_cmake_manifest.py` on the real tree still
  exits 0 UNARMED; all four fixtures behave exactly as specified; the full pytest suite
  (Task 3) exercises the parser end to end via subprocess against all four trees.

No other deviations. Every acceptance criterion (the exact UNARMED line, the
exactly-1-violation count with zero SDK-path leakage, the unreasoned/reasoned exclusion
pair, the D-07 hard-failure test, the exit-2 unknown-list test, the 33-passed firmware
suite total, the unchanged py32 worktree, the unchanged `src`/`include`/
`platformio.ini`/`.github`/`test` paths since the fork point) passed exactly as
specified.

## Issues Encountered

None beyond the regex boundary bug documented above, caught and fixed before the Task 1
commit landed.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- `check_cmake_manifest.py` exists and is armed-ready for the moment Phase 124 lands
  `platform/py32f071/CMakeLists.txt` — it will immediately catch the confirmed
  `flash_type_3.cpp`/`flash_type_4.cpp` rename defect (MERGE-02) the first time it runs
  against the real manifest.
- The `PY32_EXCLUDED` comment format is now a committed contract; Phase 124 can copy the
  five-line block verbatim from this SUMMARY (or from the checker's own docstring)
  rather than re-deriving it.
- BASE-04 and BASE-08 remain untucked per plan (`requirement_closure: None` — both close
  only in 123-11).
- Firmware suite at 33 passed / 0 skipped, ready for 123-05/123-06 to add their own
  gates and meta-test on top.

## Self-Check: PASSED

- FOUND: `firestarter/scripts/check_cmake_manifest.py`
- FOUND: `firestarter/tests/test_check_cmake_manifest.py`
- FOUND: `firestarter/tests/fixtures/planted_cmake_manifest_missing_source/README.md`
- FOUND: `firestarter/tests/fixtures/planted_cmake_manifest_excluded_no_reason/README.md`
- FOUND: `firestarter/tests/fixtures/clean_cmake_manifest_excluded/README.md`
- FOUND: `firestarter/tests/fixtures/clean_unarmed_tree/README.md`
- FOUND commit `13b1c28` (Task 1: check_cmake_manifest.py)
- FOUND commit `d775036` (Task 2: four fixture trees)
- FOUND commit `8d5ecba` (Task 3: test_check_cmake_manifest.py)
- Verified: `firestarter` on `v1.23-py32f071-integration`, `git status --porcelain` clean
- Verified: `firestarter/tests/` pytest → 33 passed, 0 skipped
- Verified: `git -C /workspaces/firestarter_py32_ci status --porcelain` empty (read-only reference respected)
- Verified: cumulative `"$FORK"..HEAD` diff over `src include platformio.ini .github test` is empty

---
*Phase: 123-non-regression-baselines-gate-hardening*
*Plan: 04*
*Completed: 2026-07-31*
