---
phase: 124-firmware-integration-merge
plan: 01
subsystem: firmware-ci
tags: [firestarter, python, git, pytest, checker, merge-gate]

# Dependency graph
requires:
  - phase: 123-non-regression-baselines-gate-hardening
    provides: "The house checker shape (env-seam + real-subprocess + three-way exit taxonomy + never-vacuous guard), the check_checker_convention.py FLOOR/FIXTURE_FLOOR meta-test, and the recorded fork_point_firmware SHA (5c9160a34b665878b05403ab014b959926feb6bf) this plan's default seam value cites."
provides:
  - "firestarter/scripts/check_landing_range.py — MERGE-01/D-06 Criterion-1 landing-shape gate: exits non-zero if any commit in <fork>..HEAD carries a portability marker without platform/py32f071/ in the same tree"
  - "firestarter/tests/test_check_landing_range.py — 7-case anti-hollow pairing proving the gate discriminates a squashed landing (0 violations) from a replayed landing (exactly 1 violation), built on two synthetic git repos in tmp_path"
  - "firestarter/tests/fixtures/planted_landing_range_replayed_history/README.md — recipe stub satisfying test_every_checker_has_planted_fixture"
  - "firestarter/tests/test_checker_convention.py FLOOR 4->5, FIXTURE_FLOOR 9->10"
affects: [124-02, 124-03, later-124-plans-landing-the-merge, 124-close]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "One violation per violating commit (not per marker) in a git-range scan, naming the first present marker deterministically"
    - "FIRESTARTER_RANGE_ROOT + FIRESTARTER_RANGE_FORK dual env seam, read once at module import, mirroring the single-seam idiom of check_orphan_provisional.py/check_cmake_manifest.py"
    - "Synthetic git repo built from scratch in tmp_path (git init + scripted commits) as the fixture shape for a checker whose subject is history, not a file tree — no in-tree fixture can be a real nested .git"

key-files:
  created:
    - firestarter/scripts/check_landing_range.py
    - firestarter/tests/test_check_landing_range.py
    - firestarter/tests/fixtures/planted_landing_range_replayed_history/README.md
  modified:
    - firestarter/tests/test_checker_convention.py

key-decisions:
  - "Violation counting is per violating COMMIT, not per present marker (deviation from a literal per-marker reading of the plan's task text) — required to match the plan's own acceptance criteria (FAIL: 1 for a single violating commit carrying both markers) and the RESEARCH-measured true-merge case (5 violations for 5 commits, not more)."
  - "ScanError is caught ONLY at the `if __name__ == '__main__':` entry point, never inside main() itself — the plan's explicit instruction, which differs slightly from check_orphan_provisional.py's belt-and-suspenders double-catch."
  - "include/rurp_platform.h is deliberately NOT a portability marker (research correction R-1: it is py32-branch content, not portability-macros content)."

patterns-established:
  - "Git-history-shape checkers get a two-seam (root + fork) env contract and a tmp_path-built synthetic repo fixture, rather than a committed fixture tree."

requirements-completed: [MERGE-01]

coverage:
  - id: D1
    description: "check_landing_range.py exists, exits 0 with a self-describing PASS line on the pre-landing tree, exits 1 on a zero-commit scan (never-vacuous guard), and exits 2 on an unresolvable/non-ancestor fork"
    requirement: "MERGE-01"
    verification:
      - kind: unit
        ref: "firestarter/tests/test_check_landing_range.py#test_real_tree_with_no_seam_override_passes"
        status: pass
      - kind: unit
        ref: "firestarter/tests/test_check_landing_range.py#test_zero_commits_scanned_is_a_failure_not_a_pass"
        status: pass
      - kind: unit
        ref: "firestarter/tests/test_check_landing_range.py#test_non_ancestor_fork_exits_exactly_2"
        status: pass
    human_judgment: false
  - id: D2
    description: "The gate discriminates a squashed landing (0 violations) from a replayed/true-merge-shaped landing (exactly 1 violation), never naming the completing commit"
    requirement: "MERGE-01"
    verification:
      - kind: unit
        ref: "firestarter/tests/test_check_landing_range.py#test_squashed_landing_passes"
        status: pass
      - kind: unit
        ref: "firestarter/tests/test_check_landing_range.py#test_replayed_landing_fires_exactly_one_violation"
        status: pass
      - kind: unit
        ref: "firestarter/tests/test_check_landing_range.py#test_replayed_landing_never_names_the_completing_commit"
        status: pass
    human_judgment: false
  - id: D3
    description: "BASE-08 convention meta-test recognizes the fifth checker: FLOOR 4->5, FIXTURE_FLOOR 9->10, both raised in the same commit as the new checker/fixture"
    verification:
      - kind: unit
        ref: "firestarter/tests/test_checker_convention.py (all 7 tests)"
        status: pass
    human_judgment: false

duration: 12min
completed: 2026-07-31
status: complete
---

# Phase 124 Plan 01: MERGE-01 Landing-Range Gate Summary

**Authored the Criterion-1 landing-shape checker (`check_landing_range.py`) and its anti-hollow pairing before Phase 124's actual firmware merge lands, per the 123-CONTEXT tie-breaker requiring the git-log claim to be discharged by a script, not a human.**

## Performance

- **Duration:** 12 min
- **Started:** 2026-07-31T08:04:06Z
- **Completed:** 2026-07-31T08:12:57Z
- **Tasks:** 2 completed
- **Files modified:** 4 (3 created, 1 modified)

## Accomplishments

- `firestarter/scripts/check_landing_range.py`: a stdlib-only, no-argv checker that walks the FULL `git rev-list <fork>..HEAD` set (never `--first-parent`) and fails if any commit carries a portability marker (`include/rurp_platform_compat.h`, `include/avr/pgmspace.h`) without `platform/py32f071/` in the same tree. Two env seams (`FIRESTARTER_RANGE_ROOT`, `FIRESTARTER_RANGE_FORK`) read once at import, defaulting to the recorded `123-01-SUMMARY.md:46` fork point `5c9160a34b665878b05403ab014b959926feb6bf`.
- `firestarter/tests/test_check_landing_range.py`: 7 pytest cases, each invoking the checker as a real subprocess against synthetic git repositories built from scratch in `tmp_path` — proving the gate distinguishes a squashed landing from a replayed one, fails on a zero-commit scan, and exits exactly 2 on a non-ancestor fork.
- `firestarter/tests/fixtures/planted_landing_range_replayed_history/README.md`: a recipe-stub fixture (no in-tree fixture can be a real nested `.git`) satisfying `test_checker_convention.py::test_every_checker_has_planted_fixture`.
- `firestarter/tests/test_checker_convention.py`: `FLOOR` 4→5, `FIXTURE_FLOOR` 9→10, docstring updated to name the fifth checker.

## Observed Verification Values

- **PASS line, pre-landing tree (before this plan's own two commits landed):** `PASS: 14 commit(s) scanned in 5c9160a34b665878b05403ab014b959926feb6bf..HEAD, 0 carrying a portability marker, 0 violations`
- **PASS line, post-landing (this plan's own two commits now included in the range, as expected since the checker scans forward from a fixed historical fork point):** `PASS: 16 commit(s) scanned in 5c9160a34b665878b05403ab014b959926feb6bf..HEAD, 0 carrying a portability marker, 0 violations`
- **Pre-landing observed integers:** `scanned=14`, `carrying=0` — matches the plan's stated expectation exactly.
- **`FIRESTARTER_RANGE_FORK=HEAD`:** exit 1, `FAIL: 0 commits scanned in <head-sha>..HEAD -- ...` (never-vacuous guard fires).
- **`FIRESTARTER_RANGE_FORK=0000...0000`:** exit 2, `ERROR: FIRESTARTER_RANGE_FORK='0000...' does not resolve to a commit ...` on stderr.
- **`grep -c 'shell=True' scripts/check_landing_range.py`:** 0.
- **`--first-parent` occurrences:** all three hits are inside the module docstring's "Rejected alternative reading" paragraph (lines 25/28/31, above the docstring's closing `"""` at line 80); zero hits in code.
- **`pytest tests/test_check_landing_range.py -q`:** 7 passed, 0 skipped, 0 failed.
- **`pytest tests/test_checker_convention.py -q`:** 7 passed, 0 failed (unchanged collected count from before this task).
- **`pytest tests/ -q` new total:** **55 passed**, 0 skipped, 0 failed (replacing the 123-01-SUMMARY.md-recorded 48; +7 for the new paired test module).
- **`FLOOR = 5` / `FIXTURE_FLOOR = 10`** — both raised in the same commit as the fifth checker + its fixture.
- **`ls tests/fixtures/ | grep -c '^planted_landing_range'`:** 1.

## Task Commits

Each task was committed atomically, inside the `firestarter` submodule (`/workspaces/firestarter`) on branch `v1.23-py32f071-integration`:

1. **Task 1: Write scripts/check_landing_range.py** - `b71408f` (feat)
2. **Task 2: Write the paired pytest, the planted fixture, and bump the BASE-08 floor** - `bc0ba55` (test)

_No plan-metadata commit is made inside the submodule — the meta-repo's own SUMMARY.md commit (below) is this plan's final commit._

## Files Created/Modified

- `firestarter/scripts/check_landing_range.py` - MERGE-01 Criterion-1 range checker
- `firestarter/tests/test_check_landing_range.py` - its anti-hollow pytest pairing (7 cases)
- `firestarter/tests/fixtures/planted_landing_range_replayed_history/README.md` - planted-fixture recipe stub
- `firestarter/tests/test_checker_convention.py` - FLOOR 4→5, FIXTURE_FLOOR 9→10

## Decisions Made

- **Violation counting is per violating commit, not per marker.** A literal reading of the plan's Task 1 action text ("for each marker ... record the violation") would produce 2 violations for a commit carrying both `include/rurp_platform_compat.h` and `include/avr/pgmspace.h` without the stack. That contradicts the plan's own acceptance criterion for Task 2 (`test_replayed_landing_fires_exactly_one_violation` expects exactly `FAIL: 1 `) and the RESEARCH-measured true-merge figure (5 violations for 5 commits — not doubled for commits carrying both markers). Implemented as: per commit, collect every present marker, and if the stack is absent, record ONE violation naming the first present marker (deterministic, by `PORTABILITY_MARKERS` tuple order).
- **`ScanError` is caught only at the `if __name__ == "__main__":` entry point**, per the plan's explicit line 116 instruction ("caught only at the entry point") — `main()` itself never wraps a `try/except ScanError`, which is a narrower shape than `check_orphan_provisional.py`'s belt-and-suspenders double catch.
- **`include/rurp_platform.h` is deliberately excluded** from `PORTABILITY_MARKERS` per research correction R-1 (it is py32-branch content, not portability-macros content).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed per-marker violation double-counting in `scan_range()`**
- **Found during:** Task 2, while writing `test_replayed_landing_fires_exactly_one_violation`
- **Issue:** The Task 1 implementation iterated `PORTABILITY_MARKERS` and appended a violation for every present marker independently, so a commit carrying both markers without the stack produced `FAIL: 2 ` instead of the plan's own expected `FAIL: 1 `.
- **Fix:** Changed `scan_range()` to collect all present markers per commit once, then append at most one violation per commit (naming the first present marker) if the stack is absent.
- **Files modified:** `firestarter/scripts/check_landing_range.py`
- **Verification:** `test_replayed_landing_fires_exactly_one_violation` and `test_squashed_landing_passes` both pass; full `pytest tests/ -q` is 55 passed, 0 failed.
- **Committed in:** `bc0ba55` (Task 2 commit)

**2. [Rule 1 - Bug] Fixed a hash-collision risk in the non-ancestor-fork test fixture**
- **Found during:** Task 2, while writing `test_non_ancestor_fork_exits_exactly_2`
- **Issue:** Two synthetic repos built back-to-back with identical README content, identical commit message, and identical author config could produce commit objects with the SAME SHA-1 (git commit hashing is a pure function of tree + parent + author/committer + message; with 1-second timestamp resolution these coincided in practice), making the "unrelated" repo's fork commit accidentally already present in the first repo's own object history — defeating the non-ancestor assertion (`assert_ancestor` passed when it should have raised `ScanError`).
- **Fix:** `_init_repo()` now embeds `repo_dir.name` (unique per `tmp_path`) into both the README content and the commit message, guaranteeing distinct tree/commit content across independently-built repos.
- **Files modified:** `firestarter/tests/test_check_landing_range.py`
- **Verification:** `test_non_ancestor_fork_exits_exactly_2` passes deterministically across repeated runs.
- **Committed in:** `bc0ba55` (Task 2 commit)

**3. [Rule 1 - Bug] Fixed a self-matching string assertion in Coverage 7**
- **Found during:** Task 2, while writing `test_checker_module_is_invoked_as_a_subprocess_not_imported`
- **Issue:** The naive assertion `"import check_landing_range" not in this_source` failed against the test module's own docstring and its own failure-message text (both legitimately discuss "importing check_landing_range" in prose), producing a false failure unrelated to any real import statement.
- **Fix:** Narrowed the check to scan for a line whose *stripped start* is exactly the import statement, rather than a raw substring search over the whole module source.
- **Files modified:** `firestarter/tests/test_check_landing_range.py`
- **Verification:** `test_checker_module_is_invoked_as_a_subprocess_not_imported` passes; the module still names `check_landing_range.py` and contains no actual import statement.
- **Committed in:** `bc0ba55` (Task 2 commit)

---

**Total deviations:** 3 auto-fixed (all Rule 1 - bugs found while proving the checker/tests against the plan's own acceptance criteria).
**Impact on plan:** All three fixes were necessary to satisfy this plan's own stated acceptance criteria and produce a genuinely discriminating gate; no scope creep, no architectural change, no file outside the plan's four listed `files_modified` paths was touched.

## Issues Encountered

None beyond the three auto-fixed deviations above, which were caught and resolved during Task 2's own verification loop before any commit was made.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- MERGE-01's Criterion-1 gate exists, is committed, and is proven to fail on a replayed history — before the landing it will judge, preserving the "gates predate the changes they detect" ordering this phase's plans must follow.
- `check_landing_range.py` is ready to be run against the real merge once a later 124 plan lands `agent/portability-macros` + the py32 stack — it will report the exact commit(s), if any, where a portability marker appears without `platform/py32f071/`.
- No blockers for 124-02 onward. The full firmware pytest suite (`tests/ -q`) is green at 55 passed; `124-NONREGRESSION.md` (a later plan's artifact) should re-record this count rather than the 123-01 baseline of 48.

## Self-Check: PASSED

- FOUND: `firestarter/scripts/check_landing_range.py`
- FOUND: `firestarter/tests/test_check_landing_range.py`
- FOUND: `firestarter/tests/fixtures/planted_landing_range_replayed_history/README.md`
- FOUND: `.planning/phases/124-firmware-integration-merge/124-01-SUMMARY.md`
- FOUND commit `b71408f` (firestarter submodule)
- FOUND commit `bc0ba55` (firestarter submodule)
- FOUND commit `5002b98` (meta repo)

---
*Phase: 124-firmware-integration-merge*
*Completed: 2026-07-31*
