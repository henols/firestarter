# Phase 133 — Deferred Items (out of scope, discovered during execution)

## From plan 133-06

- **Pre-existing `ruff check` failures in three unrelated files**, discovered while
  running the plan's phase-wide verification command
  (`ruff check firestarter/ tools/ tests/`):
  - `tools/audit_coverage_matrix.py:37` — I001 unsorted/unformatted import block
  - `tools/catalog/codegen.py:36` — I001 unsorted/unformatted import block
  - `tools/catalog/codegen_vectors.py:32` — I001 unsorted/unformatted import block
  - `tools/catalog/codegen_vectors.py:189` — UP031 percent-format instead of format
    specifier

  Confirmed pre-existing and unrelated to this phase's changes: `git log` shows
  these files were last touched in Phase 63/70 (commits `9cbcf1e`, `e9dc01f`,
  `e8132b3`), long before Phase 133. Reproduced with `git stash -u` (this plan's
  new file removed from the working tree) — the same 4 errors appear, proving
  they are not introduced by `tests/test_op_registration_parity.py`.

  Out of scope per the executor's scope-boundary rule (only auto-fix issues
  directly caused by the current task's changes). `tests/test_op_registration_parity.py`
  itself is ruff-clean (`ruff check tests/test_op_registration_parity.py` /
  `ruff format --check tests/test_op_registration_parity.py` both exit 0), and
  `ruff check tests/` / `ruff format --check tests/` (the task-scoped commands)
  both exit 0. Not fixed here. A future phase touching these three files should
  clean them up incidentally, or a dedicated lint-debt phase should sweep them.

  Also confirmed: CI's own ruff scope (`tools/ci_replica_venv.sh` Leg 3) is
  `ruff check firestarter/ tests/` -- it does NOT include `tools/` at all, so
  these four pre-existing errors are outside the CI-enforced surface entirely,
  not merely out of this plan's task scope.

- **mypy error count rose from 32 to 33 (still 2 under the 35 watermark)**,
  caused by an INCIDENTAL side effect of this plan's own import, not a bug
  this plan introduced by editing anything: `tests/test_op_registration_parity.py`
  imports `tools.check_devtest_orchestrator` (to read its
  `_HANDLER_FUNCTION_NAMES` constant as a declared non-registry locator),
  which makes mypy transitively type-check that module for the first time --
  it was never reachable from `firestarter/`'s or `tests/`'s import graph
  before (its own paired test, `tests/test_check_devtest_orchestrator.py`,
  only shells out via `subprocess`, never imports it). That surfaced one
  PRE-EXISTING type error in code plan 133-05 shipped, invisible until now:

  ```
  tools/check_devtest_orchestrator.py:442: error: Incompatible types in
  assignment (expression has type "str | None", variable has type "str")  [assignment]
  ```

  (`visit_ExceptHandler`'s `label` variable is inferred `str` from its first
  assignment `label = "bare except:"`, then reassigned `str | None` from
  `self._classify_broad_except(node.type)`.)

  Confirmed via `git stash -u` (this plan's file removed): mypy reports 32
  errors / 123 checked files without it, 33 errors / 124 checked files with
  it -- the file itself contributes ZERO mypy errors
  (`mypy ... 2>&1 | grep test_op_registration_parity` is empty both with and
  without); the sole diff is the newly-reachable `check_devtest_orchestrator.py`
  line. Not fixed here: `tools/check_devtest_orchestrator.py` is not a file
  this plan's task list touches (`git diff --name-only HEAD~1` for this plan
  is scoped to `tests/test_op_registration_parity.py` only), and the count
  remains safely under the watermark (33 <= 35, headroom 3 -> 2). Watermark
  itself is unmoved, per the plan's explicit constraint. A future plan
  touching `check_devtest_orchestrator.py` should fix this one-line type
  narrowing (`label: str | None = None` at declaration, or an explicit cast)
  in the same commit as any other edit there.
