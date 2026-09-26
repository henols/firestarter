---
phase: 184-guards-that-exist
plan: 01
subsystem: testing
tags: [pytest, cross-repo-inventory, fail-closed, scan-paths, tdd]

requires:
  - phase: 168-04
    provides: the ScanPathEntry / CROSS_REPO_TEST_PATHS inventory this plan hardens
provides:
  - "A fifth test, test_every_scan_path_resolver_is_an_existing_tests_module, that
    makes a resolved_by value naming a non-existent or non-bare guard file UNWRITABLE"
  - "The rotted ScanPathEntry (test_configure_memory.cpp -> tools/wiki/dispatch_mirror.py)
    removed from CROSS_REPO_TEST_PATHS, proven by an observed RED against the real defect"
  - "_FLOOR re-anchored to a reason instead of a plan-time census; both stale '8 paths'
    docstring/comment figures corrected to the real count of 6"
affects: [184-02, 184-03, 184-04, 184-05]

actuals:
  tokens: 1674
  tasks: 3
  commits: 2

tech-stack:
  added: []
  patterns:
    - "Fail-closed inventory field: a value is validated structurally (bare-filename
      shape) before any filesystem lookup, so an annotated/cross-repo string is
      rejected for what it IS, not merely for happening to be absent"
    - "Collect-then-assert-once, per-entry offender messages naming the fix, not just
      the symptom (mirrors test_all_eleven_tool_resolvers_exist's shape)"

key-files:
  created: []
  modified:
    - firestarter_app/tests/test_scan_paths_resolve.py
    - firestarter_app/tests/scan_paths.py

key-decisions:
  - "D-11: resolved_by restricted to bare tests/ filenames, checked structurally
    (empty -> not-bare -> absent, first-applicable-rule) before any is_file() lookup"
  - "D-13: the guard's RED was observed against the REAL rotted entry, with
    scan_paths.py provably untouched (empty git status), before the entry was removed"
  - "D-14: the entry was deleted outright, not re-pointed or marked -- no escape hatch
    was added to the new check"
  - "D-15: _FLOOR stays 6; its justification changed from a plan-time census to why
    the inventory cannot do its job below that count, plus the deliberate-move rule"

requirements-completed: [CLAIM-09, CLAIM-01]

coverage:
  - id: D1
    description: "A ScanPathEntry whose resolved_by names a guard file that is not
      present as firestarter_app/tests/<name> makes the new test FAIL -- observed RED
      against the real rotted entry with scan_paths.py still unmodified, GREEN only
      after the entry was removed"
    requirement: "CLAIM-09"
    verification:
      - kind: unit
        ref: "tests/test_scan_paths_resolve.py#test_every_scan_path_resolver_is_an_existing_tests_module"
        status: pass
    human_judgment: false
  - id: D2
    description: "tests/scan_paths.py contains dispatch_mirror zero times; the rotted
      entry, its annotated resolved_by value, and its trailing comma are gone"
    requirement: "CLAIM-01"
    verification:
      - kind: other
        ref: "grep -c dispatch_mirror tests/scan_paths.py == 0"
        status: pass
    human_judgment: false
  - id: D3
    description: "An empty resolved_by tuple fails the new check under rule (a)
      rather than passing vacuously (CLAIM-09 edge: empty)"
    requirement: "CLAIM-09"
    verification:
      - kind: unit
        ref: "184-01 Task 2, Plant C (transient, not committed) -- observed RED then GREEN"
        status: pass
    human_judgment: false
  - id: D4
    description: "A resolved_by value with a path separator, or whose Path(value).name
      differs from the value, is rejected as non-bare even when the named file exists
      on disk (CLAIM-09 edge: encoding)"
    requirement: "CLAIM-09"
    verification:
      - kind: unit
        ref: "184-01 Task 2, Plant B (transient, not committed) -- observed RED then GREEN"
        status: pass
    human_judgment: false
  - id: D5
    description: "is_file() is the predicate (never exists()); the new check carries
      no pytest marker, no count assertion, and collects every offender before
      asserting once"
    requirement: "CLAIM-09"
    verification:
      - kind: unit
        ref: "tests/test_scan_paths_resolve.py#test_every_scan_path_resolver_is_an_existing_tests_module"
        status: pass
      - kind: other
        ref: "grep -c '^@requires_fw' tests/test_scan_paths_resolve.py == 1"
        status: pass
    human_judgment: false
  - id: D6
    description: "_FLOOR re-anchored to a reason (not a census); every stale count
      figure in both modules corrected to the true 6"
    requirement: "CLAIM-09"
    verification:
      - kind: unit
        ref: "tests/test_scan_paths_resolve.py#test_inventory_is_non_vacuous"
        status: pass
      - kind: other
        ref: "grep -c '8 paths' tests/scan_paths.py == 0; grep -c 'Four tests\\|measured at plan time' tests/test_scan_paths_resolve.py == 0"
        status: pass
    human_judgment: false

duration: 22min
completed: 2026-09-11
status: complete
---

# Phase 184 Plan 01: Fail-Closed `resolved_by` Guard Summary

**Built the test that makes a `ScanPathEntry` naming a non-existent guard file unwritable, watched it fail on the real 11-day-rotted `dispatch_mirror.py` handoff with the inventory untouched, then let that RED be what removed the entry.**

## Performance

- **Duration:** 22 min
- **Started:** 2026-09-11T13:05:00Z
- **Completed:** 2026-09-11T13:27:00Z
- **Tasks:** 3
- **Files modified:** 2

## Accomplishments
- Added `test_every_scan_path_resolver_is_an_existing_tests_module`, a fifth test in
  `tests/test_scan_paths_resolve.py`, that rejects any `resolved_by` value which is
  empty, not a bare filename, or not present as a file under `firestarter_app/tests/`
  -- reporting the first applicable rule per value, collecting every offender before
  asserting once, unmarked so it can never degrade to a skip in app CI
- Observed the new check FAIL on the real rotted `ScanPathEntry`
  (`test/native/avr/test_dispatch/test_configure_memory.cpp` naming
  `tools/wiki/dispatch_mirror.py (meta repo; relocated by 168-10)`) with
  `tests/scan_paths.py` provably untouched (`git status --porcelain` empty), then
  removed that entry and observed GREEN -- the guard's RED on the real defect is
  what caused the removal, not a hand-delete first
- Proved the check fail-closed against all three of its rules with three transient
  plants (empty tuple, non-bare-but-existing path, bare-but-absent filename), each
  observed RED then removed, with the tree returned byte-identical to the committed
  state after each cycle and after the whole task
- Re-anchored `_FLOOR`'s justification from a plan-time census to why the inventory
  cannot do its job below 6, and corrected both stale "8 paths" docstring/comment
  figures in `scan_paths.py` and the "Four tests" docstring in
  `test_scan_paths_resolve.py` to the real count

## Task Commits

Each task was committed atomically, inside `firestarter_app` (the plan's `files_modified`
are both in the app submodule):

1. **Task 1: TRACER -- fail-closed resolver check, RED on the real rotted entry, GREEN after removal** - `ae92dd1` (test)
2. **Task 2: Three transient planted controls** - no commit (by design -- every plant was applied, observed, and removed inside the task; `git diff HEAD` against Task 1's commit is empty)
3. **Task 3: Re-anchor `_FLOOR`, correct stale count figures** - `c511589` (docs)

**Gitlink + plan metadata:** advanced in the meta repo's own commit (see final commit list below).

_Note: this is a `type="tracer" tdd="true"` Task 1 -- RED then GREEN are both captured verbatim below, per the plan's `<acceptance_criteria>`._

## Files Created/Modified
- `firestarter_app/tests/test_scan_paths_resolve.py` - added `_TESTS_DIR`, the fifth
  test, the re-anchored `_FLOOR` comment, and a five-test module docstring
- `firestarter_app/tests/scan_paths.py` - removed the rotted `ScanPathEntry`; corrected
  both stale "8 paths" figures to 6

## RED/GREEN Evidence (D-13)

### Task 1 -- the real rotted entry

**Step 2, before touching `scan_paths.py`** -- `git status --porcelain -- tests/scan_paths.py` output: **(empty)** -- proves no hand-delete happened before the RED observation.

**Step 2 RED** (`cd firestarter_app && .venv311/bin/python -m pytest tests/test_scan_paths_resolve.py -o addopts="" -q`):

```
....F                                                                    [100%]
=================================== FAILURES ===================================
__________ test_every_scan_path_resolver_is_an_existing_tests_module ___________
...
E       AssertionError: The following resolved_by value(s) are unwritable claims -- each must be a bare filename present as a file under /workspaces/firestarter_app/tests:
E           - test/native/avr/test_dispatch/test_configure_memory.cpp: 'tools/wiki/dispatch_mirror.py (meta repo; relocated by 168-10)' is not a bare filename -- resolved_by must hold bare filenames present as tests/<name>; a genuine cross-repo handoff requires extending the type and stating how it gets checked, not smuggling a path into the string

tests/test_scan_paths_resolve.py:199: AssertionError
=========================== short test summary info ============================
FAILED tests/test_scan_paths_resolve.py::test_every_scan_path_resolver_is_an_existing_tests_module
1 failed, 4 passed in 0.10s
```

Contains all four required elements: the failing test's name, the literal
`tools/wiki/dispatch_mirror.py (meta repo; relocated by 168-10)`, the literal
`test/native/avr/test_dispatch/test_configure_memory.cpp`, and wording ("is not a bare
filename") identifying the value as rejected under rule (b), not as a missing file.
Summary line: **`1 failed, 4 passed`** -- the four pre-existing tests stayed green.

**Step 4 GREEN** (after removing the entry, same command):

```
.....                                                                    [100%]
5 passed in 0.07s
```

**Summary line: `5 passed`.**

### Task 2 -- three transient plants (each `fw_relative_path="include/firestarter.h"`)

**Plant A** (`resolved_by=("test_a_guard_that_does_not_exist.py",)`) -- RED:
```
E           - include/firestarter.h: 'test_a_guard_that_does_not_exist.py' does not exist as a file under /workspaces/firestarter_app/tests -- resolved_by must name a guard file that is present there
1 failed, 4 passed in 0.07s
```
Names `test_a_guard_that_does_not_exist.py` and reports it as absent under `tests/` (rule c). Removed -> GREEN: `5 passed in 0.04s`.

**Plant B** (`resolved_by=("tests/test_scan_paths_resolve.py",)` -- a file that DOES exist) -- RED:
```
E           - include/firestarter.h: 'tests/test_scan_paths_resolve.py' is not a bare filename -- resolved_by must hold bare filenames present as tests/<name>; a genuine cross-repo handoff requires extending the type and stating how it gets checked, not smuggling a path into the string
1 failed, 4 passed in 0.16s
```
Reported under the bare-filename rule (b), explicitly NOT as a missing file -- the only
evidence the structural rule is real rather than a side effect of the existence check.
Removed -> GREEN: `5 passed in 0.09s`.

**Plant C** (`resolved_by=()`) -- RED:
```
E           - include/firestarter.h: resolved_by is empty -- an entry that names no resolver does not belong in this inventory
1 failed, 4 passed in 0.16s
```
Names the `include/firestarter.h` entry with an empty `resolved_by` tuple (rule a).
Removed -> GREEN: `5 passed in 0.09s`.

No plant was committed. `git status --porcelain -- tests/scan_paths.py tests/test_scan_paths_resolve.py` was empty after every removal, and `git diff HEAD -- tests/scan_paths.py` (after all three cycles) was empty -- the tree is byte-identical to Task 1's commit. No file appeared under `tests/fixtures/`.

## Decisions Made
- D-11/D-12/D-13/D-14/D-15 implemented exactly as CONTEXT.md specifies -- no deviation
  was needed from any of the five CLAIM-09 decisions.
- The three plant `fw_relative_path` values all reused `"include/firestarter.h"` (already
  in the inventory) per the plan's instruction, exercising the adjacency case (two
  entries sharing one `fw_relative_path`) as a side effect of each plant.
- Out-of-scope Population-B census assertions (`assert len(CROSS_REPO_TOOL_RESOLVERS) == 11`
  in `scan_paths.py`, and `test_all_eleven_tool_resolvers_exist`'s `assert len(...) == 11`
  arm) were seen, recognised as the same anti-pattern D-15 corrects, and left untouched --
  PATTERNS.md § Scope Guards puts both outside this phase.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- CLAIM-09 is fully satisfied: a `ScanPathEntry` naming a guard file that does not
  exist, or naming it in an unresolvable form, cannot be written without a named
  test failure -- proven against the real 11-day-rotted entry, not only a synthetic.
- The app half of CLAIM-01 (the `scan_paths.py:114` live reference to
  `tools/wiki/dispatch_mirror.py`) is closed as a consequence of this plan. The
  meta-repo half of CLAIM-01 (any other repo reference) is owned by a sibling plan
  in this phase, not this one.
- No blockers for `184-02`..`184-05`.

## Self-Check: PASSED

- `firestarter_app/tests/test_scan_paths_resolve.py` and `firestarter_app/tests/scan_paths.py` exist on disk: FOUND
- Commit `ae92dd1` (Task 1, app repo): FOUND
- Commit `c511589` (Task 3, app repo): FOUND
- Commit `f37b1050` (meta repo, SUMMARY + gitlink): FOUND
- Gitlink `firestarter_app` in meta HEAD points at `c511589a6c45180e51570ede0aa47f0e7e3263a0`: matches
- Final re-run of `tests/test_scan_paths_resolve.py`: `5 passed`

---
*Phase: 184-guards-that-exist*
*Completed: 2026-09-11*
