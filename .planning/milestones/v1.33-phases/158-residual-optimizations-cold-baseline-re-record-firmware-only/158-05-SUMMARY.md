---
phase: 158-residual-optimizations-cold-baseline-re-record-firmware-only
plan: "05"
subsystem: testing
tags: [size-baseline, ci-gate, merge05, checker-convention, docstring-correction, pytest]

# Dependency graph
requires:
  - phase: 158-01
    provides: "158-before-figures.md -- LAND-04's two clauses, the BASE-01/native RED shape, the pre-phase FLOOR/FIXTURE_FLOOR figures (7/16) against the shipped counts (8/30)"
  - phase: 158-04
    provides: "size_baseline.json re-recorded to 184/184/17 on both native envs; the *_v158* fixture severance including the new planted_size_baseline_flash_regression_v158.log plant that raises the fixture count to 31; BASE-01 and check_size_baseline.py confirmed byte-unchanged"
provides:
  - "BASE-01's native_envs.{native,native_nodevtools}.{cases,succeeded} re-anchored 141 -> 184 (suites stays 17); avr_targets byte-unchanged; new meta.native_inventory_axis_phase158 note carries the axis-split argument and named cause in the file itself"
  - "The canonical --policy merge05 --baseline size_baseline_base01.json --rebuild invocation flipped from exit 1 (two native cases-mismatch lines) to exit 0 with a full PASS: line"
  - "tests/test_checker_convention.py FLOOR 7->8, FIXTURE_FLOOR 16->31, both counted on the tree at this commit; docstring carry-forward paragraph closed, non-vacuity probe recorded"
  - "tests/test_check_size_baseline.py and tests/meta_presence.py module docstrings corrected: both now state the checker is a size gate invoked by no workflow, while the checker's OWN pytest suite runs in CI via build.yml:161 on every branch except beta"
affects: ["158-06 (after-figures, cites this plan's PASS/FAIL flip and the corrected floor values)", "158-07 (ROADMAP/REQUIREMENTS scope-correction, cites C-1/C-9/C-10 as closed here)"]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Axis-split doctrine extended to three axes: growth (frozen), board-identity (licensed to move with cause), test-inventory (licensed to move because tests only accumulate) -- all three now recorded in BASE-01's own meta rather than only in the not-re-anchored leg's docstring"
    - "Non-vacuity probe as a committed verification step: temporarily set a floor one above the measured count, capture the failing diagnostic verbatim, then restore -- proves a >= gate can actually fail before trusting it"

key-files:
  created: []
  modified:
    - firestarter/scripts/baseline/size_baseline_base01.json
    - firestarter/tests/test_checker_convention.py
    - firestarter/tests/test_check_size_baseline.py
    - firestarter/tests/meta_presence.py

key-decisions:
  - "OD-3 executed: LAND-03 FIXED, not carried. The measured count (184, read from the just-committed live baseline, both native envs agreeing) was written into BASE-01's four native_envs integers, never transcribed from prose. The declined floor-semantics alternative (a monotonic floor under --policy merge05) is recorded in the new meta note with its cost: gate-behaviour change, a new fixture pair, a planted negative, and a widened landing phase."
  - "OD-5 executed: the test_checker_convention.py floor carry-forward is CLOSED as a tightening of a loose >= gate, not a repair of a red one -- both counts (8 checkers, 31 fixtures) were counted on the tree at this commit, after plan 04's own new plant, never transcribed."
  - "OD-4 executed: both false CI-coverage docstrings corrected, comment-only. Verified mechanically (AST-diff with docstrings stripped) to change zero assertions, imports, constants or function definitions in either file."
  - "Correction C-12 recorded precisely: the AVR comparison in check_size_baseline.py's main() always ran FIRST and PASSED; it is the report line carrying the flash figures (built inside the AVR loop, printed only by _print_pass) that never gets reached once the later native loop appends a failure and the early `if all_failures: return 1` fires -- the comparison itself is not what's suppressed."

requirements-completed: [LAND-03, LAND-04]

# Coverage metadata
coverage:
  - id: D1
    description: "BASE-01's native inventory axis re-anchored to the measured count (184/184/17), growth axis byte-unchanged, axis-split argument and named cause recorded in the file's own meta -- LAND-03 fixed, not carried"
    requirement: "LAND-03"
    verification:
      - kind: unit
        ref: "tests/test_check_size_baseline.py::test_base01_is_not_re_anchored_by_the_new_exemption"
        status: pass
      - kind: unit
        ref: "tests/test_check_size_baseline.py -q -o addopts=\"\" (14 passed)"
        status: pass
      - kind: other
        ref: "python3 scripts/check_size_baseline.py --policy merge05 --baseline scripts/baseline/size_baseline_base01.json --rebuild -> exit 0, PASS: line, zero 'cases baseline=' lines (flipped from plan 01's recorded exit 1)"
        status: pass
    human_judgment: false
  - id: D2
    description: "test_checker_convention.py's named Phase 158 floor carry-forward closed: FLOOR 7->8, FIXTURE_FLOOR 16->31, both counted on the tree, docstring repaired, non-vacuity probe recorded"
    verification:
      - kind: unit
        ref: "tests/test_checker_convention.py -q -o addopts=\"\" (7 passed)"
        status: pass
      - kind: other
        ref: "non-vacuity probe: FIXTURE_FLOOR=32 (one above measured 31) makes test_fixture_directory_is_non_vacuous FAIL with 'assert 31 >= 32'; file restored, git diff clean before commit"
        status: pass
    human_judgment: false
  - id: D3
    description: "Two false CI-coverage docstrings corrected in tests/test_check_size_baseline.py and tests/meta_presence.py, comment-only, LAND-04's second clause honoured in source"
    requirement: "LAND-04"
    verification:
      - kind: unit
        ref: "tests/test_check_size_baseline.py -q -o addopts=\"\" (14 passed); tests/test_flash_path_record_sync.py -q -o addopts=\"\" (41 passed, 0 skipped, proving the meta-presence seam prose survives intact)"
        status: pass
      - kind: other
        ref: "AST-diff with docstrings stripped: both files' trees identical across the commit -- zero assertion/import/constant/def changes"
        status: pass
    human_judgment: false

# Metrics
duration: ~35min
completed: 2026-08-24
status: complete
---

# Phase 158 Plan 05: BASE-01/checker-convention close-out Summary

**BASE-01's frozen native test-inventory axis re-anchored to the measured count (141 -> 184), flipping the canonical `--policy merge05 --rebuild` invocation from exit 1 to exit 0; the named `test_checker_convention.py` floor carry-forward closed (7/16 -> 8/31, both counted on the tree); and the two in-tree docstrings that asserted the inverse of LAND-04's second clause corrected, comment-only.**

## Performance

- **Duration:** ~35 min
- **Completed:** 2026-08-24
- **Tasks:** 3 (all produced a commit)
- **Files modified:** 4 across 3 commits (1 + 1 + 2)

## Accomplishments

- **Task 1 (`7894dec`, fix):** Read `native_envs.native.cases` / `native_nodevtools.cases` from the just-committed live `size_baseline.json` (184, both envs agreeing) rather than from any prose, and wrote that measured count into BASE-01's four `native_envs` integers (`cases`/`succeeded` on both `native` and `native_nodevtools`). `avr_targets` left byte-unchanged (confirmed by direct read: `flash_used` 24824/24874/26906, `ram_used` 1573/1579/2014). Appended a new `meta.native_inventory_axis_phase158` note stating: the four integers' old/new values; that this is a third, test-inventory axis distinct from the frozen growth axis and the already-licensed board-identity axis; that a frozen inventory count is monotonically invalid because tests only accumulate; the named cause (BASE-01's native block frozen at its Phase 124 genesis, never updated across Phases 124-157); that this milestone's own diff touches zero files under `test/native/avr/`; and the declined floor-semantics alternative with its cost. `test_base01_is_not_re_anchored_by_the_new_exemption` and the whole checker suite (14 passed) stayed green, proving the fix cost zero legs. The canonical `--policy merge05 --baseline size_baseline_base01.json --rebuild` invocation flipped from plan 01's recorded exit 1 (`native: cases baseline=141 observed=184`, `native_nodevtools: cases baseline=141 observed=184`) to exit 0 with a full `PASS:` line covering all three AVR targets plus both native envs. Exit-1 mechanism recorded correctly (correction C-12): the AVR comparison in `main()` always runs first and passes, appending its decomposition to `compared`; the native loop runs next and appends its failures to `all_failures`; the early `if all_failures: _print_fail(...); return 1` fires before `_print_pass` is ever reached -- the flash figures ARE compared and DO pass, only the report line carrying them is suppressed.
- **Task 2 (`5dca69d`, test):** Counted `check_*.py` under `scripts/` (`ls scripts/check_*.py | wc -l` -> 8) and `planted_*` entries under `tests/fixtures/` (`ls tests/fixtures | grep -c '^planted_'` -> 31, one higher than the pre-phase 30 recorded in `158-before-figures.md`, because plan 04's own new plant `planted_size_baseline_flash_regression_v158.log` landed first) on the tree at this commit, never transcribed. Raised `FLOOR` 7 -> 8 and `FIXTURE_FLOOR` 16 -> 31. Rewrote the docstring's carry-forward paragraph to read as closed, naming this phase and plan as the closer, both counted values and their commands, the one-more-than-pre-phase fixture note, and removed the now-false "FLOOR's own wording is off by one" claim -- explicitly stated this is a **tightening of a loose `>=` gate**, not a repair of a red one (neither test was failing before the edit). Non-vacuity probe: temporarily set `FIXTURE_FLOOR = 32` (one above the measured 31), confirmed `test_fixture_directory_is_non_vacuous` FAILS with `AssertionError: expected at least FIXTURE_FLOOR=32 planted_* entries ... got 31 ... assert 31 >= 32` (diagnostic captured verbatim in the commit body), then restored the file to `31` before committing. Zero assertion or test-definition lines changed (mechanically confirmed via a diff line-pattern count of 0).
- **Task 3 (`2ccda8d`, docs):** Corrected `tests/test_check_size_baseline.py`'s two-sentence paragraph claiming "no CI leg exercises it in either repository" to the accurate framing: the checker itself remains a size gate invoked by NO workflow (unchanged, local-run obligation), but this suite DOES run in CI via `build.yml:161`'s `pytest tests/ -v`, ungated by any `if:`, on a trigger (`build.yml:34`, `push: branches: ['**','!beta']`) that fires on every branch except `beta`; named the `beta-build.yml:134` sibling leg; added the practical-consequence sentence this phase leans on (moving the live baseline without severing fixtures in the same commit turns the suite red in CI). The following Evidence Ceiling paragraph is byte-unchanged. Corrected `tests/meta_presence.py`'s bolded "CI coverage, stated honestly" paragraph the same way, extending the standing prohibition to forbid implying absence of coverage too, while leaving the import-time seam prose, the `FIRESTARTER_META_ROOT` seam, the marker-probe prose and the subprocess requirement verbatim. Verified via an AST-diff with docstrings stripped that both files' trees are identical across the commit -- zero assertion/import/constant/function-definition changes, and `def test_` count in `test_check_size_baseline.py` unchanged at 14. `tests/test_check_size_baseline.py` (14 passed) and `tests/test_flash_path_record_sync.py` (41 passed, 0 skipped -- the only consumer of the meta-presence skip marker) both green on the committed, clean tree, proving the seam prose survived intact.
- `python3 -m pytest tests/ -q -o addopts=""` from `/workspaces/firestarter`: **360 passed**, zero `skipped`, run fresh after each of the three commits.

## Task Commits

Each task was committed atomically, inside `firestarter/` on branch `gsd/v1.33-source-hygiene-firmware-size-reduction`:

1. **Task 1: Fix BASE-01's native inventory axis and prove the canonical invocation goes green** - `7894dec` (fix)
2. **Task 2: Close the named Phase 158 floor carry-forward in test_checker_convention.py** - `5dca69d` (test)
3. **Task 3: Correct the two in-tree docstrings that get the CI automation boundary backwards** - `2ccda8d` (docs)

## Files Created/Modified

- `firestarter/scripts/baseline/size_baseline_base01.json` -- four `native_envs` integers moved 141 -> 184; new `meta.native_inventory_axis_phase158` note; `avr_targets` byte-unchanged.
- `firestarter/tests/test_checker_convention.py` -- `FLOOR` 7 -> 8, `FIXTURE_FLOOR` 16 -> 31, carry-forward docstring paragraph closed.
- `firestarter/tests/test_check_size_baseline.py` -- module docstring CI-coverage paragraph corrected (comment-only).
- `firestarter/tests/meta_presence.py` -- module docstring CI-coverage paragraph corrected (comment-only).

## Decisions Made

- OD-3 executed: BASE-01's mismatch fixed by measurement, not carried; the declined floor-semantics alternative recorded with its cost inside the file itself.
- OD-5 executed: the floor carry-forward closed as a tightening, with the non-vacuity probe as the proof a `>=` gate can actually fail.
- OD-4 executed: both false CI-coverage claims corrected, comment-only, verified by AST-diff to touch prose only.
- `--rebuild`'s new exit-0 result was used strictly as a **check** (per Pitfall 6 / this phase's own convention) -- no figure in this SUMMARY or in BASE-01 was transcribed from a `--rebuild` run; all figures trace to the committed `size_baseline.json` or to direct `ls`/`grep` counts on the tree.

## Deviations from Plan

None in the Rule 1-3 sense -- no bug, missing functionality, or blocker was found. One expected, documented interaction with a pre-characterized test class:

**Recorded interaction (not a deviation): the porcelain-check test class fires on a dirty tree mid-task.** Plan Task 3's Step 3 instructed running `tests/test_check_size_baseline.py` and `tests/test_flash_path_record_sync.py` before committing. `test_flash_path_record_sync.py::TestFlashPathRecordSync::test_planted_mutation_of_the_real_subset_is_detected` asserts `_git_porcelain(_FW_REPO_ROOT)` is empty at its end -- this is exactly the porcelain-check test class `158-before-figures.md` §6 names as reddening "for ANY dirty file in the firmware working tree," unrelated to this plan's own edit. With Task 3's docstring edits staged-but-uncommitted, the tree was legitimately dirty, so this leg failed on that unrelated axis. Resolved by committing Task 3 first (matching the plan's own automated `<verify>` block, which assumes a post-commit state throughout), then re-running both required legs on the clean, committed tree: `test_check_size_baseline.py` (14 passed) and `test_flash_path_record_sync.py` (41 passed, 0 skipped). No code or assertion changed as a result; the reordering only affected when the confirming pytest run was taken, not what it proved.

---

**Total deviations:** 0 auto-fixed; 1 recorded interaction with a pre-characterized, unrelated test class (no code change).
**Impact on plan:** None -- both required legs pass green with zero skips on the final committed tree, which is what the plan's acceptance criteria require.

## Issues Encountered

None beyond the recorded porcelain-check interaction above.

## User Setup Required

None -- no external service configuration required.

## Next Phase Readiness

- Plan 06 (after-figures) can cite: BASE-01's flip from exit 1 to exit 0 on the canonical `--policy merge05 --rebuild` invocation; both floors now counted true at 8/31; both docstrings now correctly framing the CI automation boundary.
- Plan 07 (ROADMAP/REQUIREMENTS scope-correction) can cite this plan's commits (`7894dec`, `5dca69d`, `2ccda8d`) as further confirmation that C-1 (`172` -> `184`, already recorded in `158-before-figures.md`), C-9 (the two false CI-coverage docstrings) and C-10 (the `7`/`16` floors against `8`/`31`) are all closed as of this plan.
- `python3 -m pytest tests/ -q -o addopts=""` from `/workspaces/firestarter` is green at 360 passed, zero skipped, on the tree left by this plan (HEAD `2ccda8d`).
- No blockers.

---
*Phase: 158-residual-optimizations-cold-baseline-re-record-firmware-only*
*Completed: 2026-08-24*

## Self-Check: PASSED

- FOUND: firestarter/scripts/baseline/size_baseline_base01.json
- FOUND: firestarter/tests/test_checker_convention.py
- FOUND: firestarter/tests/test_check_size_baseline.py
- FOUND: firestarter/tests/meta_presence.py
- FOUND commit (firestarter): 7894dec (fix(158-05): re-anchor BASE-01's native inventory axis to the measured count)
- FOUND commit (firestarter): 5dca69d (test(158-05): close the named Phase 158 checker and fixture floor carry-forward)
- FOUND commit (firestarter): 2ccda8d (docs(158-05): correct two false CI-coverage claims in the gate test modules)
