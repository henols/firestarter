---
phase: 127-host-dfu-installer
plan: 06
subsystem: testing
tags: [pytest, ci, pyusb, collect_ignore, github-actions, py32f071, dfu]

# Dependency graph
requires:
  - phase: 127-01
    provides: "firestarter/py32_dfu.py, tests/test_py32_dfu.py landed on the milestone branch via the feature/py32f071-fw-install merge"
provides:
  - "tests/conftest.py: collect_ignore keyed on importlib.util.find_spec(\"usb\") is None -- the first optional-dependency collection gate in this repo"
  - "tests/test_pyusb_gating.py: 6 primary-leg guards proving the gate is armed, keyed correctly, cannot rot, and that no production ctrl_transfer call-site passes its 5th arg by keyword"
  - "tests/test_pyusb_api_surface.py: the ci-py32-only module exercising real usb.core.find and pinning ctrl_transfer's parameter order + timeout default against pyusb 1.3.1"
  - ".github/workflows/ci.yml: workflow_dispatch: trigger + isolated ci-py32 job installing .[test,py32]"
affects: [127-08, 127-11]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "collect_ignore (not a skip marker) is the sanctioned mechanism for gating a test module on an OPTIONAL DEPENDENCY -- produces a non-collection, needs no ALLOWED_SKIP_REASONS entry, and (unlike --ignore= in addopts) does not suppress a path named explicitly on the pytest command line -- which is exactly how ci-py32 invokes the gated module"
    - "Every conditional-collection gate needs its OWN always-running test proving it is armed, keyed correctly, and cannot rot -- a misfired collect_ignore is invisible to the test run it silently excludes"
    - "Pin a real third-party library's call signature with inspect.signature() against an independently-written literal list, not a value derived at import time, so a signature rename/reorder is caught rather than silently re-derived"

key-files:
  created:
    - firestarter_app/tests/test_pyusb_gating.py
    - firestarter_app/tests/test_pyusb_api_surface.py
  modified:
    - firestarter_app/tests/conftest.py
    - firestarter_app/.github/workflows/ci.yml

key-decisions:
  - "Task 1 and Task 2 landed in ONE commit (e20e9e5), not two, per the plan's explicit fallback permission: tests/test_pyusb_gating.py::test_gated_module_exists cannot pass until tests/test_pyusb_api_surface.py (Task 2's deliverable) exists on disk, so there is no green intermediate state between the two tasks as separately-committed units."
  - "collect_ignore is a plain module-level list (`collect_ignore: list = []`), not a set or generator -- matches pytest's documented collect_ignore contract (a list of path strings relative to the conftest's directory) and keeps the .append() call trivially readable."
  - "The find_spec probe is wrapped in a private _pyusb_is_absent() helper that treats ImportError/ValueError as absent, so a broken pyusb installation cannot raise out of conftest import and take down the entire suite."
  - "tests/test_pyusb_api_surface.py's usb.core.find test catches ONLY usb.core.NoBackendError -- verified zero occurrences of a broader except (ValueError|Exception) or bare except anywhere in the file -- because NoBackendError subclasses ValueError and a broad catch would make the either/or assertion vacuous."
  - "The fake-vs-real ctrl_transfer comparison (Plan 127-08's) was deliberately NOT written here. The in-repo fake USB device is referred to only by description in a trailing comment, never by its class name -- verified grep -c '_FakeUsbDevice' tests/test_pyusb_api_surface.py returns 0."
  - "ci-py32 pins python-version: '3.11', matching the primary ci job, so any ci-py32 failure is attributable to pyusb rather than to a Python-version difference. It runs no ruff/ruff-format/mypy/coverage/codegen-drift step -- the primary ci job already gates all of those over the whole tree (planner's stated default)."
  - "workflow_dispatch: was added to ci.yml's on: block and NOTHING else -- the milestone branch v1.23-py32f071-integration was NOT added to push:, verified grep -c 'v1.23-py32f071-integration' .github/workflows/ci.yml returns 0."
  - "No requirement checkbox in .planning/REQUIREMENTS.md was ticked by this plan (verified: HOST-01..HOST-08 all still Pending in the working tree, and REQUIREMENTS.md's traceability table still reads 'HOST-01 … HOST-08 | Phase 127 | Pending'). Only Plan 127-12 may tick these."

requirements-completed: []  # HOST-04 intentionally left unticked -- only Plan 127-12 may tick HOST-01..HOST-08. This plan cites HOST-04 in commit messages for traceability only.

coverage:
  - id: D1
    description: "Conditional collect_ignore in tests/conftest.py keeps tests/test_pyusb_api_surface.py out of the primary (pyusb-absent) leg via non-collection, not a skip -- no new ALLOWED_SKIP_REASONS entry needed"
    requirement: "HOST-04"
    verification:
      - kind: unit
        ref: "tests/test_pyusb_gating.py::test_gate_armed_correctly_for_this_environment"
        status: pass
      - kind: unit
        ref: "tests/test_pyusb_gating.py::test_gate_is_keyed_on_find_spec_usb"
        status: pass
      - kind: unit
        ref: "tests/test_pyusb_gating.py::test_every_collect_ignore_entry_names_a_real_file"
        status: pass
      - kind: unit
        ref: "tests/test_skip_census.py (ALLOWED_SKIP_REASONS unchanged at 4 entries)"
        status: pass
    human_judgment: false
  - id: D2
    description: "tests/test_pyusb_api_surface.py genuinely imports pyusb, calls usb.core.find(find_all=True) for real with an explicit either/or outcome (never a bare pass), and pins ctrl_transfer's parameter order + timeout default against an independent literal (pyusb 1.3.1)"
    requirement: "HOST-04"
    verification:
      - kind: unit
        ref: "tests/test_pyusb_api_surface.py (5 tests, run in a throwaway .[test,py32] venv)"
        status: pass
      - kind: unit
        ref: "tests/test_pyusb_gating.py::test_gated_module_exists"
        status: pass
    human_judgment: false
  - id: D3
    description: "ci.yml gains workflow_dispatch: (and only that) plus a separate ci-py32 job installing .[test,py32], running only the pyusb-API-surface tests by explicit path, with no branch literal added to push:"
    requirement: "HOST-04"
    verification:
      - kind: unit
        ref: "tests/test_pyusb_gating.py::test_ci_yml_references_the_gated_module_and_the_ci_py32_job"
        status: pass
      - kind: other
        ref: "grep -c 'v1.23-py32f071-integration' .github/workflows/ci.yml == 0; python3 -c 'yaml.safe_load(...)' structural check"
        status: pass
    human_judgment: false
  - id: D4
    description: "No task ran git push or gh workflow run -- the operator-gated CI dispatch remains Plan 127-11's action"
    verification: []
    human_judgment: true
    rationale: "Absence of a command cannot be proven by a unit test; confirmed by review of every Bash invocation in this session (none contains git push or gh workflow run) and recorded here for the closing plan to audit."

# Metrics
duration: ~35min
completed: 2026-08-01
status: complete
---

# Phase 127 Plan 06: Optional-Dependency Collection Gate + Real-pyusb CI Leg Summary

**A conditional `collect_ignore` in `tests/conftest.py` (the first optional-dependency test gate in this repo) keeps a genuine `usb.core`/`ctrl_transfer` API-surface test out of the primary suite without a skip, backed by six always-running guard tests and a new `ci-py32` job in `ci.yml` that installs `.[test,py32]` and runs it by explicit path.**

## Performance

- **Duration:** ~35 min
- **Started:** 2026-08-01 (approx)
- **Completed:** 2026-08-01T13:09:17Z
- **Tasks:** 3/3 executed (Tasks 1+2 landed in one commit per the plan's explicit fallback; see Decisions)
- **Files modified:** 4 (2 new, 2 modified)

## Accomplishments

- **Task 1 + Task 2 (one commit, `e20e9e5`):** `tests/conftest.py` gained a module-scope `collect_ignore` list, populated with `"test_pyusb_api_surface.py"` only when `importlib.util.find_spec("usb")` is `None` (wrapped against a raising `find_spec`), documented with the non-collection-not-skip rationale, the fail-closed explicit-path property, and both rejected alternatives (`pytest.importorskip`, `--ignore=` in `addopts`). `tests/test_pyusb_gating.py` (new) landed with five always-running guards: the gated module exists, every `collect_ignore` entry resolves to a real file, the gate's biconditional inverts correctly with the environment, the gate is keyed on `find_spec`/`"usb"` by source scan, and an `ast` scan proving every one of the 5 production `ctrl_transfer` call-sites in `firestarter/py32_dfu.py` passes all arguments positionally (0 keywords). `tests/test_pyusb_api_surface.py` (new) genuinely imports `usb.core`, calls `usb.core.find(find_all=True)` for real behind an either/or outcome sentinel (only `usb.core.NoBackendError` caught, no device-count assertion), asserts `NoBackendError` subclasses `ValueError` as a live check, and pins `ctrl_transfer`'s first six parameter names plus `timeout`'s optionality against an independent literal measured from pyusb 1.3.1.
- **Task 3 (`5052568`):** `.github/workflows/ci.yml` gained `workflow_dispatch:` in its `on:` block (and nothing else — no branch literal added to `push:`) plus a new `ci-py32` job: checkout → `setup-python@v5` pinned to `'3.11'` → `pip install -e .[test,py32]` → a step proving pyusb imports and printing its resolved version → `pytest tests/test_pyusb_api_surface.py -q` naming the file explicitly. No lint/type/coverage/codegen step. `tests/test_pyusb_gating.py` gained a sixth test asserting `ci.yml` names the gated module, declares `ci-py32`, and installs `.[test,py32]` — closing the three-place rename triangle (`collect_ignore` entry, module existence, workflow reference).

## Task Commits

1. **Task 1 + Task 2: conditional collect_ignore gate + real-pyusb API surface module** — `e20e9e5` (test)
2. **Task 3: ci.yml workflow_dispatch + isolated ci-py32 job** — `5052568` (ci)

**Meta-repo tracking commit:** pending (this SUMMARY + gitlink bump, committed next per `<final_commit>`)

Both commits are on `firestarter_app`'s `v1.23-py32f071-integration` branch.

## Files Created/Modified

- `firestarter_app/tests/conftest.py` — `collect_ignore` added at module scope, keyed on `importlib.util.find_spec("usb")`; docstring's "it exposes" list extended
- `firestarter_app/tests/test_pyusb_gating.py` — new module, 6 always-running guard tests (5 from Task 1, 1 appended in Task 3)
- `firestarter_app/tests/test_pyusb_api_surface.py` — new module, 5 tests, `ci-py32`-only via `collect_ignore`
- `firestarter_app/.github/workflows/ci.yml` — `workflow_dispatch:` added; new `ci-py32` job

## Decisions Made

- **Tasks 1 and 2 committed together.** The plan's own acceptance criteria for Task 1 acknowledge that `tests/test_pyusb_gating.py::test_gated_module_exists` cannot pass until the Task 2 module exists on disk, and explicitly permits landing both in one commit "and say so" — done here, recorded in the commit message and this SUMMARY.
- Kept `collect_ignore` as a plain `list` (not a set) to match pytest's documented contract exactly, and wrapped the `find_spec` probe in a private helper so a broken pyusb install cannot raise out of conftest import.
- `tests/test_pyusb_api_surface.py`'s `usb.core.find` test never asserts a device count (measured: this devcontainer enumerates 8, a CI runner may enumerate 0) and catches only `usb.core.NoBackendError`, verified via a grep gate returning 0 for any broader `except` clause in the file.
- Deferred the fake-vs-real `ctrl_transfer` comparison to Plan 127-08 exactly as instructed — the in-repo fake USB device is named only by description in a trailing comment, with a grep gate confirming its class name occurs zero times in the new module.
- `ci-py32` pins Python 3.11 (matching the primary `ci` job) and runs no lint/type/coverage/codegen step, per the plan's stated default.

## Deviations from Plan

None (Rule 1/2/3 sense) — plan executed exactly as written, including its explicit permission to combine Tasks 1 and 2 into one commit. No scope creep: only the four files named in the plan's `files_modified` were touched. `/workspaces/firestarter` is unmodified (verified `git status --short` clean both before this plan's first read and after its last commit). No requirement checkbox in `.planning/REQUIREMENTS.md` was ticked. No task ran `git push` or `gh workflow run`.

## Issues Encountered

- `ruff format` reformatted two lines across the new/modified files (a blank-line-after-import-block fix in `tests/conftest.py`, and a quote-style/line-wrap fix in `tests/test_pyusb_api_surface.py` and `tests/test_pyusb_gating.py`) — applied via `ruff format` before each commit; re-verified with `ruff format --check` afterward. Purely mechanical formatting, not a deviation from plan content.
- The devcontainer's `pytest tests/ -q` invocation runs for ~166–168 s (well past the default 120 s Bash timeout) due to the full 1264-1265-test suite; each run was launched in the background and its completion awaited rather than truncated.

## User Setup Required

None — no external service configuration required. The operator-gated CI dispatch (pushing the branch and running `gh workflow run`) remains Plan 127-11's action; this plan only wrote the workflow file.

## Next Phase Readiness

- The optional-dependency collection gate exists, is armed, keyed correctly, and proven non-vacuous — Plan 127-08 (which reconciles `_FakeUsbDevice.ctrl_transfer`'s signature and adds the fake-vs-real comparison to `tests/test_pyusb_api_surface.py`) can build directly on this module without re-deriving the gating mechanism.
- `ci.yml` is ready for Plan 127-11's operator-gated push + `gh workflow run` dispatch — the `ci-py32` job will run automatically once the branch reaches `origin` and the workflow is dispatched.
- Full app suite in the devcontainer (pyusb absent): **1265 collected / 1265 passed / 0 failed / 0 skipped** (1259 baseline + 6 new gating tests; `test_pyusb_api_surface.py`'s 5 tests correctly NOT collected). `ruff check`, `ruff format --check` both clean. `tools/check_mypy_watermark.py` unaffected (1 error, watermark 35).
- Rehearsed in a throwaway `.[test,py32]` venv (deleted afterward): `tests/test_pyusb_api_surface.py` — **5/5 passed**. Devcontainer confirmed still pyusb-absent afterward.
- HOST-01..HOST-08 all remain `[ ]` Pending in `.planning/REQUIREMENTS.md` — unaffected by this plan, as instructed.
- `/workspaces/firestarter` remains untouched (read-only input), confirmed clean before and after this plan's execution.

## Self-Check: PASSED

- FOUND: `firestarter_app/tests/conftest.py` (modified)
- FOUND: `firestarter_app/tests/test_pyusb_gating.py`
- FOUND: `firestarter_app/tests/test_pyusb_api_surface.py`
- FOUND: `firestarter_app/.github/workflows/ci.yml` (modified)
- FOUND: commit `e20e9e5` in `firestarter_app` git log
- FOUND: commit `5052568` in `firestarter_app` git log
- FOUND: `.planning/phases/127-host-dfu-installer/127-06-SUMMARY.md`
