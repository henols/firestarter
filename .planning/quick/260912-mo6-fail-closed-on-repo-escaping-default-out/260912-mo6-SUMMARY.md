---
phase: quick-260912-mo6
plan: 01
subsystem: testing
tags: [python, argparse, path-safety, subprocess-testing, pytest]

requires: []
provides:
  - "audit_coverage_matrix.py fails closed (exit 2) when a default --output/--ledger
    path would be created outside an existing repository checkout"
  - "Regression test proving the guard, the do-not-weaken legs, and the operator's
    unchanged invocation"
affects: [firestarter_app-tools, firestarter_app-tests]

actuals:
  tokens: 2472
  tasks: 3
  commits: 3

tech-stack:
  added: []
  patterns:
    - "subprocess-driven guard test against a disposable __file__ copy (rather than
      monkeypatching module constants) to exercise real path arithmetic"

key-files:
  created:
    - firestarter_app/tests/test_audit_coverage_matrix_default_paths.py
    - .planning/quick/260912-mo6-fail-closed-on-repo-escaping-default-out/evidence/red-before-fix.txt
    - .planning/quick/260912-mo6-fail-closed-on-repo-escaping-default-out/evidence/operator-invocation.txt
  modified:
    - firestarter_app/tools/audit_coverage_matrix.py
    - firestarter_app/tools/check_no_exists_proxy.py

key-decisions:
  - "Restructured the four new tests as module-level functions, not TestClass
    methods — the plan's own verify-block grep patterns anchor on
    `test_audit_coverage_matrix_default_paths.py::test_guard_fails_closed_when_no_planning_dir`
    with no class segment in between; a class-scoped node id would not match."
  - "Pre-fix, the two fails-closed legs go red via an uncaught FileNotFoundError
    (exit 1, raw traceback) rather than the plan's predicted 'exits 0 and writes a
    planning tree' — Path.write_text never mkdir's its parent, so a genuinely
    absent .planning/ crashes rather than silently succeeding. Confirmed this is
    the real, non-accidental failure mode (not an import error, timeout, or missing
    DB) before treating it as valid RED evidence."
  - "mypy watermark gate must run under firestarter_app/.venv311 (Python 3.11), not
    the devcontainer's default 3.12 interpreter — running under 3.12 makes mypy
    abort on a numpy stub with 'Type statement is only supported in Python 3.12
    and greater', an unrelated pre-existing environment issue, confirmed via a
    git-stash control run with no code changes present."

requirements-completed: [QUICK-260912-mo6]

coverage:
  - id: D1
    description: "Standalone-layout invocation (no planning dir) exits 2, names --output and --ledger on stderr, and creates nothing"
    requirement: "QUICK-260912-mo6"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_audit_coverage_matrix_default_paths.py#test_guard_fails_closed_when_no_planning_dir"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_audit_coverage_matrix_default_paths.py#test_guard_fails_closed_when_only_one_path_is_explicit"
        status: pass
    human_judgment: false
  - id: D2
    description: "Operator's own invocation (planning dir already exists) is byte-for-byte unchanged: same default paths, exit 0"
    requirement: "QUICK-260912-mo6"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_audit_coverage_matrix_default_paths.py#test_defaults_resolve_when_planning_dir_exists"
        status: pass
      - kind: integration
        ref: ".planning/quick/260912-mo6-fail-closed-on-repo-escaping-default-out/evidence/operator-invocation.txt"
        status: pass
    human_judgment: false
  - id: D3
    description: "Explicit --output/--ledger paths always bypass the guard, including outside the repo; supplying only ONE of the pair still fails closed"
    requirement: "QUICK-260912-mo6"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_audit_coverage_matrix_default_paths.py#test_explicit_paths_bypass_the_guard"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_audit_coverage_matrix_default_paths.py#test_guard_fails_closed_when_only_one_path_is_explicit"
        status: pass
    human_judgment: false
  - id: D4
    description: "--check and --all-algorithms keep their existing exit-code semantics (unweakened)"
    requirement: "QUICK-260912-mo6"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_audit_coverage_matrix.py#test_exit_codes"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_audit_coverage_matrix_default_paths.py#test_guard_fails_closed_when_no_planning_dir[check]"
        status: pass
    human_judgment: false

duration: 8min
completed: 2026-09-12
status: complete
---

# Quick Task 260912-mo6: Fail Closed on Repo-Escaping Default Output Paths Summary

**`audit_coverage_matrix.py` now exits 2 (naming `--output`/`--ledger`) instead of
writing a planning tree outside the repo when its `__file__`-derived default paths
land somewhere a planning directory doesn't already exist — the operator's own
invocation stays byte-for-byte unchanged.**

## Performance

- **Duration:** 8 min
- **Started:** 2026-09-12T16:29:55Z
- **Completed:** 2026-09-12T16:38:45Z
- **Tasks:** 3
- **Files modified:** 5 (2 tool/checker files, 1 new test module, 2 evidence files)

## Accomplishments

- Landed a subprocess-driven guard test (`test_audit_coverage_matrix_default_paths.py`)
  that copies the real tool into a scratch tree so `__file__`-derived path
  arithmetic runs unmodified, and observed it RED against the unfixed tool before
  writing the fix.
- Added `PLANNING_DIR` + `resolve_default_paths(all_algorithms)` to
  `audit_coverage_matrix.py`: refuses to invent a planning directory outside an
  existing checkout, exits 2 with an actionable stderr message naming
  `--output`/`--ledger`, and never touches the filesystem when refusing.
  `main()` consults the resolver exactly once, only for whichever of
  `--output`/`--ledger` is unset — an explicitly-passed path (even just one of
  the pair) always wins.
- Proved the operator's own invocation is unchanged: ran the fixed tool from
  `/workspaces/firestarter_app` with defaults, discovered PRE-EXISTING drift
  between the committed coverage-matrix/ledger and the current
  `chip_database.json` (unrelated to this fix — see Deviations), and restored
  the meta tree to clean afterward.

## Task Commits

Each task was committed atomically, inside the `firestarter_app` submodule
(code) or the meta repo (evidence docs):

1. **Task 1: Land the guard test and OBSERVE it red against the unfixed tool** -
   `0dd517b` (test) — `firestarter_app`
2. **Task 2: Add the invocation-time guard and turn the suite green** -
   `f3650ff` (fix) — `firestarter_app`
3. **Task 3: Prove the operator's invocation is unchanged and leave no state
   behind** - `6a839527` (docs) — meta repo (`/workspaces`)

No separate plan-metadata commit: this is a quick task, and the SUMMARY/STATE
docs commit is handled by the orchestrator per the constraints in this task's
brief. The submodule gitlink bump is likewise left for the orchestrator.

## Files Created/Modified

- `firestarter_app/tests/test_audit_coverage_matrix_default_paths.py` - new guard
  test module: 4 test functions (2 parametrized), driving the real tool via
  subprocess against a disposable copy planted in a scratch tree
- `firestarter_app/tools/check_no_exists_proxy.py` - registered the new test
  module in the literal `_DEFAULT_TARGETS` enumeration
- `firestarter_app/tools/audit_coverage_matrix.py` - added `PLANNING_DIR` +
  `resolve_default_paths()`, rewired `main()`'s default-selection block through
  it, updated two docstring passages (default-path description, exit-code list),
  removed the now-superseded "Pitfall 6 defense" comment block (not replaced,
  per the no-comments rule)
- `.planning/quick/260912-mo6-fail-closed-on-repo-escaping-default-out/evidence/red-before-fix.txt` -
  captured red run against the unfixed tool
- `.planning/quick/260912-mo6-fail-closed-on-repo-escaping-default-out/evidence/operator-invocation.txt` -
  captured the operator's own invocation, the pre-existing drift finding, and
  its restoration

## Decisions Made

- **Test functions, not a TestClass:** the plan's own `<verify>` grep patterns
  anchor on `test_audit_coverage_matrix_default_paths.py::test_guard_fails_closed_when_no_planning_dir`
  with no intervening class segment. The neighboring `test_audit_coverage_matrix.py`
  uses a `TestAuditCoverageMatrix` class, but matching that convention here would
  have broken the plan's own verify commands (pytest node IDs would read
  `...::TestAuditCoverageMatrixDefaultPaths::test_guard_...`, not a substring of
  the expected pattern). Used plain module-level functions instead.
- **`resolve_default_paths()` checks `PLANNING_DIR` existence inside the function
  body only** — never at module level — so importing the module has no side
  effect and never exits, matching the interface contract and confirmed via a
  direct `importlib` exec in Task 2's verify.
- **Kept the four `DEFAULT_*` constants and `_REPO_ROOT` exactly as they were**
  (still import-time, still unconditional) since nothing besides `main()` reads
  them and `tests/test_audit_coverage_matrix.py`'s imports must keep working
  unmodified.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug in the plan's own verify tooling] Test functions restructured
as module-level, not class methods**
- **Found during:** Task 1 (writing the test module)
- **Issue:** The plan's `<action>` prose didn't specify class vs. function
  shape, but its `<verify>` block's grep patterns assume a bare function node ID
  with no class prefix. A `TestClass`-wrapped version (matching the neighboring
  test module's convention) would silently fail the plan's own verify grep.
- **Fix:** Wrote all four tests as plain module-level functions.
- **Files modified:** `firestarter_app/tests/test_audit_coverage_matrix_default_paths.py`
- **Verification:** Ran the exact grep commands from the plan's `<verify>` block
  against the red-before-fix evidence; both matched.
- **Committed in:** `0dd517b` (Task 1 commit)

**2. [Rule 1 - Environment quirk, not a code bug] mypy watermark gate run under
the wrong Python interpreter**
- **Found during:** Task 2 (running the wider gate set)
- **Issue:** `python tools/check_mypy_watermark.py` under the devcontainer's
  default Python 3.12 aborts with "Type statement is only supported in Python
  3.12 and greater" against a numpy stub, unrelated to this change (confirmed via
  a `git stash` control run showing the identical failure with none of this
  task's edits present).
- **Fix:** Ran the gate through the repo's existing `.venv311` (Python 3.11)
  virtualenv instead, per this project's own documented convention for this
  exact class of masking. No code change — a run-environment correction only.
- **Files modified:** none
- **Verification:** `source .venv311/bin/activate && python tools/check_mypy_watermark.py`
  reports "checked 183 source files / mypy errors: 35 (watermark: 35) / OK" —
  i.e. this change added zero new mypy errors.
- **Committed in:** n/a (no code change; verification-only correction)

---

**Total deviations:** 2 auto-fixed (1 verify-tooling bug, 1 environment quirk).
**Impact on plan:** Neither touched product behavior or scope; both were
verification-mechanics corrections needed to actually run the plan's own gates
as written.

## Issues Encountered

- **Pre-existing drift in tracked meta artifacts (out of scope, documented, not
  fixed here):** Task 3's operator-invocation run found
  `.planning/v1.3-COVERAGE-MATRIX.md` and `.planning/v1.3-defect-coverage-ids.json`
  are stale relative to the current `chip_database.json` — regenerating with
  defaults produced ~479 changed lines in the matrix and 19 new
  `DEFECT-COV-NN` ledger entries (`DEFECT-COV-81`, `-82`, `-90`..`-96`, plus
  renumbered ranges). This is unrelated to this task's change (which touches
  only default-path resolution, never `generate_matrix`'s rendering — confirmed
  by inspecting the diff, which contains zero touched lines in any `_emit_*` /
  `detect_*` function) and predates it. Restored both files to their committed
  state with `git -C /workspaces checkout --` per the plan's instructions; the
  meta tree is clean. This drift is a separate, pre-existing finding for a
  future task, not addressed here.
- The plan's `<behavior>` prose predicted the unfixed tool's fails-closed legs
  would go red via "exits 0 and writes a planning tree into the scratch root."
  In practice `Path.write_text` never creates missing parent directories, so
  the unfixed tool crashes with an uncaught `FileNotFoundError` (exit 1, raw
  traceback) instead. Verified this is a legitimate, non-accidental RED (not an
  import error, timeout, or missing-database failure) before proceeding —
  documented under Decisions above.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- The guard is in place, tested, and proven not to change the operator's own
  workflow.
- The pre-existing coverage-matrix/ledger drift found in Task 3 (see Issues
  Encountered) is unresolved and may warrant its own follow-up task to
  regenerate and commit the current matrix/ledger — flagged here, not actioned.

---
*Phase: quick-260912-mo6*
*Completed: 2026-09-12*

## Self-Check: PASSED

All created files exist on disk (test module, tool + checker changes, both
evidence files, this SUMMARY). All three task commits (`0dd517b`, `f3650ff` in
`firestarter_app`; `6a839527` in the meta repo) are present in their respective
`git log`.
