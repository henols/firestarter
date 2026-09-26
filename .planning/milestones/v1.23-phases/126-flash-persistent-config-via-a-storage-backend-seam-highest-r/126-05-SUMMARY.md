---
phase: 126-flash-persistent-config-via-a-storage-backend-seam-highest-r
plan: 05
subsystem: firmware
tags: [config-storage, seam, gate, pytest, structural-verification, d-09, includer-census]

# Dependency graph
requires:
  - phase: 126-03
    provides: "include/rurp_config_storage.h (the seam header), src/rurp_config_utils.cpp (policy-only), src/boards/rurp_config_storage_eeprom.cpp (AVR backend) -- the artifacts this plan gates"
provides:
  - "tests/test_config_storage_seam_shape.py -- a committed pytest gate proving CFG-03's structural half: exactly two bool declarations with C linkage in include/rurp_config_storage.h, include-before-extern-C ordering, a repo-bounded reachability walk proving rurp_shield.h never reaches the seam header (direct or transitive), an includer census stable both before and after Plan 126-08, the four public config declarations still above the seam, CONFIG_VERSION unchanged, CONFIG_START below the seam, and no platform conditional in the policy layer"
  - "twelve independent mutation demonstrations (recorded below, never committed) proving every helper the gate calls can genuinely fail"
affects: [126-08, 126-12]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Module-level violation-list helpers shared between positive tests and a planted-copy RED test -- the same pattern test_vpp_seam_manual_on_every_board.py and test_pinmap_guard_fires.py use, extended here to file-tree census helpers (not just single-file textual gates)"
    - "Three-property includer census (every hit sanctioned / every existing sanctioned path a hit / count >= 2) that is provably stable across a future includer's arrival, rather than an == N assertion that goes red the moment the count changes"
    - "git-hash-object-equivalent (hashlib sha1 of 'blob <len>\\0<content>') computed in-process to prove a planted-copy test never mutated a committed file, without invoking git as a subprocess"

key-files:
  created:
    - firestarter/tests/test_config_storage_seam_shape.py
  modified: []

key-decisions:
  - "The plan's own text says 'twelve functions' in two places (the behaviour block's action text and Task 1's acceptance criteria), but the enumerated behaviour block itself names exactly ELEVEN distinct test function names. Implemented all eleven exactly as named (one of them, test_helper_reports_violations_on_planted_copies, is parametrized across the four RED cases the plan's action text specifies, yielding 14 pytest node IDs, still 11 functions). Did not invent a spurious twelfth function to force the count -- the twelve mutation demonstrations Task 2 asks for are a separate, non-pytest evidence table, and that count (12) is correct and fully delivered below. Flagging this discrepancy rather than silently reconciling it."
  - "Both census-shape checks (declaration census and public-declarations check) strip C-style comments before scanning, after test_public_config_declarations_stay_in_rurp_shield_h initially false-failed: the seam header's own FIRE-PROOF comment block mentions rurp_validate_config() in prose, which a naive substring/regex search over raw text matched as a false declaration. Fixed by reusing the same comment-stripping helper the declaration census already used."
  - "The .pio/ non-dependency test's own failure-message text originally contained the literal '.pio/' fragment it was checking for (a second mention alongside the concatenation-built variable), which trips the very assertion it makes. Rephrased the message to describe the property without repeating the literal path fragment."
  - "Task 2's twelve mutation demonstrations were run via a scratch Python script (not a committed file) that imports the committed test module by file path and calls its own module-level helpers directly on tmp-directory copies -- proving the exact same functions the positive tests call can fail on twelve independent inputs, then deleting the scratch tree."

requirements-completed: []  # CFG-03 completes at Plan 126-05 per the ROADMAP's own framing, but per this plan's explicit "Requirement ticking scope for this plan: NONE" instruction, only Plan 126-12 may tick CFG-01..07. Nothing ticked here.

coverage:
  - id: D1
    description: "tests/test_config_storage_seam_shape.py gates the seam header's declaration shape (exactly two bool prototypes, D-06 signatures, no enum/typedef/non-guard macro) and C linkage (extern \"C\" wrapper, includes before it)"
    requirement: "CFG-03"
    verification:
      - kind: unit
        ref: "tests/test_config_storage_seam_shape.py::test_seam_header_declares_exactly_two_functions, ::test_seam_header_has_c_linkage_with_includes_outside_the_wrapper"
        status: pass
    human_judgment: false
  - id: D2
    description: "The gate proves rurp_shield.h never reaches the seam header, directly or transitively, via a repo-bounded reachability walk that visits at least one header (D-09)"
    requirement: "CFG-03"
    verification:
      - kind: unit
        ref: "tests/test_config_storage_seam_shape.py::test_seam_header_is_not_included_by_rurp_shield_h"
        status: pass
    human_judgment: false
  - id: D3
    description: "The includer census enforces all three D-09 properties (every hit sanctioned, every existing sanctioned path a hit, count >= 2), correct both today (2 includers) and after Plan 126-08 (3 includers) without needing an edit"
    requirement: "CFG-03"
    verification:
      - kind: unit
        ref: "tests/test_config_storage_seam_shape.py::test_seam_header_includers_are_exactly_the_sanctioned_set"
        status: pass
    human_judgment: false
  - id: D4
    description: "The four public config declarations stay asserted in rurp_shield.h and absent from the seam header; CONFIG_VERSION asserted VER06; CONFIG_START asserted 48 in the AVR backend and absent from the policy layer; the policy layer asserted free of preprocessor conditionals (D-07, D-08)"
    requirement: "CFG-03"
    verification:
      - kind: unit
        ref: "tests/test_config_storage_seam_shape.py::test_public_config_declarations_stay_in_rurp_shield_h, ::test_config_version_literal_is_unchanged, ::test_config_start_lives_below_the_seam, ::test_policy_layer_has_no_platform_conditional"
        status: pass
    human_judgment: false
  - id: D5
    description: "Every assertion the gate makes is demonstrated able to FAIL: four RED demonstrations committed inside the module (parametrized, tmp_path only) plus twelve independent mutation demonstrations run via a scratch script against the module's own helpers, all producing genuine violations, none touching a committed file"
    requirement: "CFG-03"
    verification:
      - kind: unit
        ref: "tests/test_config_storage_seam_shape.py::test_helper_reports_violations_on_planted_copies[third_declaration|includes_inside_wrapper|forbidden_include|unsanctioned_includer]; twelve-mutation evidence table below"
        status: pass
    human_judgment: false

duration: ~40min
completed: 2026-07-31
status: complete
---

# Phase 126 Plan 05: Config Storage Seam Structural Gate Summary

**A pytest module (`tests/test_config_storage_seam_shape.py`, 11 functions / 14 node IDs) turns CFG-03's shape requirements into exit codes -- declaration shape, C linkage, includer census stable across Plan 126-08, D-07 placement invariants, D-08's no-conditional-policy-layer invariant -- with every assertion proven able to fail across sixteen total independent mutations (4 committed in-module + 12 in a scratch demonstration), none touching a committed file.**

## Performance

- **Duration:** ~40 min
- **Completed:** 2026-07-31T23:27:53Z
- **Tasks:** 2
- **Files modified:** 1 (created)

## Accomplishments

- `firestarter/tests/test_config_storage_seam_shape.py` created: 11 named test functions (14 pytest node IDs with parametrization), stdlib + pytest only, self-contained path resolution (no `conftest.py`), no blob SHA literal anywhere, no skip call or conditional-skip marker, no `.pio/` path reference.
- Every check factored into a module-level helper taking text or a filesystem tree and returning a violation list, shared identically between the positive tests and the RED demonstration test -- no parallel second implementation exists anywhere in the module.
- The includer census (`_includer_census_violations`) implements the three-property formulation the plan specifies: every hit sanctioned, every existing sanctioned path a hit, count >= 2 -- verified correct at today's state (2 includers) without hardcoding either `== 2` or `== 3`.
- The reachability walk (`_seam_reachability_violations`) is a real repo-bounded BFS (not a depth-1 direct-include check): confirmed against the live tree it visits 5 headers from `rurp_shield.h` (itself, `rurp_platform_compat.h`, `rurp_types.h`, `rurp_pinout.h`, plus one more resolved via the include-dir search) and reports zero violations; demonstration 6 below proves it also fires when the forbidden include is planted two hops deep.
- Sixteen total mutation demonstrations across this plan (4 inside the committed module's parametrized RED test, 12 in Task 2's scratch evidence run) each produced a genuine, non-empty violation from an independent input -- none constructed by feeding a helper its own expected output (Phase 124 D-14 guard against a hollow gate).
- `pytest tests/` total raised from 102 (Plan 126-04's end state) to **116 passed** (+14 node IDs from this module's 11 functions, one parametrized four ways).
- Both pinned native environments re-measured at exactly **141 cases / 141 succeeded / 17 suites** (`native` and `native_nodevtools`), unchanged from Plan 126-03/126-04.
- The D-09 blob pin for `include/rurp_shield.h` recorded at plan level (not in the committed gate): `602fe6f326a042ab71efd111e4dfcf3a6e41dd46`, with `git log --oneline -1 -- include/rurp_shield.h` showing no commit from this phase (last touch: Phase 124's `e2c422d`).

## Task Commits

Each task was committed atomically:

1. **Task 1: Author `tests/test_config_storage_seam_shape.py` -- the CFG-03 structural gate** -- `34a67ec` (test) -- 1 file: `tests/test_config_storage_seam_shape.py`.
2. **Task 2: Prove every assertion able to fail, and record the D-09 blob pin at plan level** -- no file changes (evidence capture only via a scratch script, recorded below; script itself was deleted from `/tmp` after the run, never committed).

**Plan metadata:** (this SUMMARY commit, to follow)

## Files Created/Modified

- `firestarter/tests/test_config_storage_seam_shape.py` (new) -- the CFG-03 structural gate.

## Decisions Made

- **The "eleven vs. twelve" function-count discrepancy is a plan-authoring artifact, not an implementation gap.** The behaviour block enumerates exactly 11 distinct `test_*` names; the surrounding prose (action text, acceptance criteria) says "twelve" in two places. All 11 named functions are implemented exactly as specified, with `test_helper_reports_violations_on_planted_copies` parametrized across the plan's own four named RED cases (14 total pytest node IDs). No 12th function was fabricated to force the number -- doing so would have meant inventing a test the plan never actually specified the name or behaviour of. Task 2's "twelve mutation demonstrations" are a wholly separate deliverable (a non-pytest evidence table) and that count of 12 is exactly and fully satisfied below.
- **Comment-stripping applied uniformly before any name-presence check.** `_public_declarations_violations` initially false-failed because the seam header's own FIRE-PROOF prose comment mentions `rurp_validate_config()` by name; fixed by stripping C-style comments (the same helper the declaration census already used) before searching for declaration syntax.
- **The `.pio/` non-dependency test's message text was itself briefly self-tripping.** Its assertion message repeated the literal `.pio/` fragment a second time (outside the concatenation-built variable) to describe the property in prose; rewritten to avoid the literal entirely.
- **Task 2's twelve mutations were executed via an ephemeral scratch script**, never a committed file, that imports `tests/test_config_storage_seam_shape.py` by file path (`importlib.util.spec_from_file_location`) and invokes its module-level helpers directly against `tmp`-directory-scoped mutated copies -- proving the exact functions the positive tests call, not a re-implementation. The script and its scratch tree were deleted after the run; `git status --porcelain` in `/workspaces/firestarter` is 0 lines before and after.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] `test_public_config_declarations_stay_in_rurp_shield_h` false-failed on the seam header's own prose comment**
- **Found during:** Task 1, first `pytest -v` run.
- **Issue:** `_public_declarations_violations` searched raw (non-comment-stripped) header text for `rurp_validate_config(`; the seam header's FIRE-PROOF comment block (lines 27-30 of `include/rurp_config_storage.h`) mentions `rurp_validate_config()` in prose ("the common policy layer calls rurp_validate_config() either way"), which matched and produced a false "unexpectedly declared in the seam header" violation.
- **Fix:** Strip C-style comments (`_COMMENT_RE`) from both `shield_text` and `seam_text` before the presence/absence checks, reusing the exact stripping helper `_declaration_census_violations` already applied.
- **Files modified:** `firestarter/tests/test_config_storage_seam_shape.py` (pre-commit; not a separate commit -- caught and fixed during authoring, before Task 1's single commit).
- **Verification:** `pytest tests/test_config_storage_seam_shape.py -v` -- all 14 node IDs pass.
- **Committed in:** `34a67ec` (part of Task 1's single commit; the fix predates the commit, so no separate commit exists for it).

**2. [Rule 1 - Bug] `test_module_has_no_pio_libdeps_dependency`'s own failure message self-tripped its check**
- **Found during:** Task 1, first `pytest -v` run.
- **Issue:** The assertion's failure message built the primary needle via concatenation (`"." + "pio" + "/"`, correct per house convention) but then repeated the literal path fragment `.pio/libdeps` a second time in the explanatory clause, which the assertion (checking the module's own full text) matched against itself.
- **Fix:** Rephrased the explanatory clause to describe the property ("a gitignored per-env libdeps dependency") without repeating the literal `.pio/` fragment.
- **Files modified:** `firestarter/tests/test_config_storage_seam_shape.py` (pre-commit fix, same commit as above).
- **Verification:** `pytest tests/test_config_storage_seam_shape.py -v` -- passes; `grep -n '\.pio/' tests/test_config_storage_seam_shape.py` finds zero occurrences in the committed file.
- **Committed in:** `34a67ec`.

---

**Total deviations:** 2, both caught and fixed during authoring before the single Task 1 commit landed (no separate fix-up commit exists, unlike Plan 126-03's two-commit D-04 fallback shape -- these were found and corrected within the same execution pass, before anything was staged).
**Impact on plan:** Both fixes are internal to the gate's own correctness (a false-positive violation and a self-tripping assertion message); neither touches any file outside `tests/test_config_storage_seam_shape.py`, and neither changes any acceptance criterion's intent.

## Issues Encountered

None beyond the two self-contained authoring-time fixes documented above.

## Twelve Mutation Demonstrations (Task 2)

Run via an ephemeral scratch script (`importlib.util.spec_from_file_location` against the committed module, never a committed file itself), all mutations built in a `tempfile.mkdtemp()` scratch tree, deleted after the run. Every mutation is an independent input; none was constructed by feeding a helper its own expected output.

| # | Mutation | Helper exercised | Expected violation | Observed violation message |
|---|---|---|---|---|
| 1 | Third declaration added to a seam-header copy | `_declaration_census_violations` | Reports the extra prototype | `expected exactly 2 function prototypes, found 3: [...]` + `unexpected/extra function prototype declared: 'rurp_config_storage_extra' ...` |
| 2 | `rurp_config_storage_load`'s return type changed `bool` -> `void` | `_declaration_census_violations` | Reports the return-type mismatch | `rurp_config_storage_load returns 'void', expected 'bool'` |
| 3 | `<stdbool.h>`/`<stddef.h>` moved inside the `extern "C"` block | `_linkage_violations` | Reports include-ordering violation | `'#include <stdbool.h>' at line 76 does not precede the extern "C" wrapper opening at line 74` (+ same for `<stddef.h>`) |
| 4 | Both `#ifdef __cplusplus` / `extern "C"` guard pairs deleted entirely | `_linkage_violations` | Reports the missing wrapper | `expected two '#ifdef __cplusplus' guards (open + close) wrapping extern "C", found 0` |
| 5 | Forbidden include added directly to a `rurp_shield.h` copy | `_seam_reachability_violations` | Reports the direct forbidden include, message carries the measured blast radius | `.../rurp_shield.h includes 'rurp_config_storage.h' ... forbidden by D-09: the seam header is reachable from 46 translation units (14 of them native host_stubs.cpp files) ... Phase 125 C-1 measured that ONE such line collapses pio test -e native from 141 cases / 141 succeeded to 17 suites / 0 succeeded` (1 header visited) |
| 6 | Forbidden include planted in `rurp_platform_compat.h` (an intermediate header `rurp_shield.h` includes, two hops from the walk's entry point) | `_seam_reachability_violations` | Reports the violation at depth 2, proving the walk is not depth-1 only | `.../rurp_platform_compat.h includes 'rurp_config_storage.h' ... forbidden by D-09: ...` (4 headers visited) |
| 7 | A file outside the sanctioned set (`src/rogue_includer.cpp`) added, including the seam header | `_includer_census_violations` | Reports the unsanctioned hit | `unsanctioned includer(s) of 'rurp_config_storage.h': ['src/rogue_includer.cpp']` |
| 8 | The include removed from a copy of `src/boards/rurp_config_storage_eeprom.cpp` (a sanctioned path present in the scratch tree) | `_includer_census_violations` | Reports the missing hit -- proves property (b) independently of (a) | `sanctioned path(s) exist in the tree but do not include 'rurp_config_storage.h': ['src/boards/rurp_config_storage_eeprom.cpp']` |
| 9 | Census pointed at a tree with zero includer hits | `_includer_census_violations` | Reports the non-vacuity violation -- proves property (c) independently | `includer census is vacuous or below the non-vacuity floor: only 0 hit(s): []` |
| 10 | `#define CONFIG_START 48` added to a copy of `src/rurp_config_utils.cpp` | `_config_start_violations` | Reports `CONFIG_START` found above the seam | `CONFIG_START #define found in the policy layer (src/rurp_config_utils.cpp) -- it is an EEPROM address and must live below the seam (D-07)` |
| 11 | A `#ifdef __AVR__` conditional added around a copy of the policy layer's include | `_platform_conditional_violations` | Reports the conditional | `src/rurp_config_utils.cpp contains 1 preprocessor conditional directive(s) (['ifdef']) -- the per-platform split must be structural, not declared (D-08)` |
| 12 | `CONFIG_VERSION` changed `"VER06"` -> `"VER07"` in a copy of `rurp_shield.h` | `_config_version_violations` | Reports the literal mismatch | `CONFIG_VERSION is 'VER07', expected 'VER06'` |

**All twelve produced genuine violations from independent inputs -- zero passes, zero skips.**

### Post-demonstration invariant re-check

After all twelve demonstrations (run entirely against scratch-tree copies), the four blob SHAs re-hash identical to their pre-demonstration values:

| File | SHA (before and after, unchanged) |
|---|---|
| `include/rurp_config_storage.h` | `1d74d0ede91853c2ce2bcc0bda1eb8fe8a07e5b2` |
| `include/rurp_shield.h` | `602fe6f326a042ab71efd111e4dfcf3a6e41dd46` |
| `src/rurp_config_utils.cpp` | `4c54f4af1d1f9c0effeffd24770fe58c8c3f2b8a` |
| `src/boards/rurp_config_storage_eeprom.cpp` | `f63ca7ae6b81e87ec390149139ac2a65f0fa29b5` |

`git status --porcelain` for `/workspaces/firestarter`: **0 lines** after the demonstrations and after the scratch tree/script were deleted.

The unmutated module was re-run immediately after and is green: `pytest tests/test_config_storage_seam_shape.py -q` -> **14 passed**.

## D-09 Blob Pin (recorded at plan level, per the prohibition against pinning a shared header in the committed gate)

- `git hash-object include/rurp_shield.h` -> `602fe6f326a042ab71efd111e4dfcf3a6e41dd46` (unchanged since before this phase).
- `git log --oneline -1 -- include/rurp_shield.h` -> `e2c422d feat(124-04): land portability-macros + py32f071 toolchain stack (squashed)` -- no commit from Phase 126 touches this path.
- **Why this pin lives here, not in the committed gate:** a test hardcoding a shared header's blob SHA breaks the first time a later milestone legitimately edits that header. The committed gate (`tests/test_config_storage_seam_shape.py`) instead uses textual anchors that actually exist in the file (the direct-include check plus the transitive reachability walk) -- the Phase-125 drift-leg discipline. The exact-bytes claim recorded here is a phase-scoped, point-in-time record; `126-NONREGRESSION.md` (Plan 126-12) re-executes it as part of the phase's final non-regression pass.

## Native Environments and Full Suite (re-measured, this plan's own run)

- `pio test -e native` -> **141 test cases: 141 succeeded**, **17 suites**.
- `pio test -e native_nodevtools` -> **141 test cases: 141 succeeded**, **17 suites**.
- `python3 -m pytest tests/ -q` -> **116 passed** (was 102 at Plan 126-04's end state; +14 node IDs from this module's 11 functions).
- `ls scripts/check_*.py | wc -l` -> **5** (unchanged); `tests/test_checker_convention.py` not modified by this plan.

## Branch Re-Check

- `firestarter` (submodule): `git rev-parse --abbrev-ref HEAD` -> `v1.23-py32f071-integration` (checked after Task 1's commit and again after Task 2's evidence run).
- Meta repo (`/workspaces`): `gsd/v1.23-py32f071-integration` (unchanged by this plan's firmware work; only this SUMMARY/STATE/ROADMAP land here).
- The two gitignored py32 worktrees (`firestarter_py32_ci`, `firestarter_app_py32`) were not written to.

## Claim Ceiling

No PY32F071 PCB exists; `arm-none-eabi-gcc`, `cmake` and `ninja` are absent from this environment (per `.planning/REQUIREMENTS.md` §"Validation Ceiling"). This gate reads source text and compiles nothing for ARM -- every assertion is a textual check over committed (or scratch-copied) source, never a compile or link step, and no ARM build or runtime claim is made anywhere in this plan or its SUMMARY.

## Next Phase Readiness

- CFG-03's structural half is now an exit code, locally, ahead of any gated ARM CI run: a third seam function, a widened signature, a dropped `extern "C"` wrapper, the one forbidden `#include` line, a moved public declaration, a changed `CONFIG_VERSION`, a relocated `CONFIG_START`, or a reintroduced platform conditional in the policy layer would each fail this gate today.
- Plan 126-08 can land `platform/py32f071/src/config_storage_flash.cpp` with the includer census already correct for its arrival: `test_seam_header_includers_are_exactly_the_sanctioned_set` requires no edit when that plan's third includer appears -- the census will simply report 3 hits instead of 2, all three properties still holding.
- No blockers.

---
*Phase: 126-flash-persistent-config-via-a-storage-backend-seam-highest-r*
*Completed: 2026-07-31*

## Self-Check: PASSED

- FOUND: `firestarter/tests/test_config_storage_seam_shape.py`
- FOUND: commit `34a67ec` in `firestarter` repo history
- FOUND: `.planning/phases/126-flash-persistent-config-via-a-storage-backend-seam-highest-r/126-05-SUMMARY.md`
- FOUND: commit `47aba4f` in meta repo history
- Branch re-check: `firestarter` on `v1.23-py32f071-integration`; meta on `gsd/v1.23-py32f071-integration`
