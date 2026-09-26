---
phase: 127-host-dfu-installer
plan: 07
subsystem: testing
tags: [pytest, coverage, pyusb, sys.meta_path, subprocess, dfu, py32f071]

# Dependency graph
requires:
  - phase: 127-06
    provides: "tests/conftest.py collect_ignore + tests/test_skip_census.py's subprocess harness idiom, reused verbatim by this plan's Task 2"
provides:
  - "firestarter/py32_dfu.py: _require_usb()'s except-clause no longer carries `# pragma: no cover` -- the branch every plain-install user hits is measured, not excluded"
  - "tests/test_py32_pyusb_absent.py: 11 tests -- 5 in-process (PyusbMissingError's type, 3 message substrings, __cause__ chaining, DfuError subclass relationship, pragma-count source scan) + 6 subprocess (fw --help/--list/--dfu-probe and firestarter --help under a genuine sys.meta_path import blocker, plus a parametrized 'nothing imported usb' check)"
affects: [127-08, 127-09, 127-12]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "A sys.meta_path.MetaPathFinder whose find_spec() RAISES ModuleNotFoundError (never returns None) is the correct shape for a genuine-absence import blocker -- returning None only defers to the next finder and would let a real installed package through, silently making the test vacuous in the leg where that package IS installed"
    - "Two independent test mechanisms for one optional-dependency error branch: an in-process sys.modules monkeypatch to get coverage credit (a subprocess contributes nothing to the parent's --cov-fail-under run), plus a genuine subprocess with a real import blocker to prove the CLI's import graph is actually clean (an in-process poke only simulates absence and cannot catch an eager top-level import that already succeeded before the fixture ran)"
    - "Rehearsing an absence-proving test mechanism in an environment where the target IS present (a throwaway venv with pyusb installed) is what proves the mechanism works, not the ambient environment -- copied from 127-06's collect_ignore rehearsal, applied here to the import blocker"

key-files:
  created:
    - firestarter_app/tests/test_py32_pyusb_absent.py
  modified:
    - firestarter_app/firestarter/py32_dfu.py

key-decisions:
  - "Followed C-3's correction verbatim: the pragma removed is the one on `except ImportError as exc:` inside `_require_usb()` (line 394 in the tree as it exists after Plans 127-05/127-06's edits -- research's `:375` anchor was measured against an earlier tree state and has since drifted by line-number only, not by location; the two other pragmas on the `_dev`/`_index` guards at lines 686/692 are untouched, confirmed by `grep -c 'pragma: no cover'` staying at 2 both before and after -- 3 total pragmas existed, now 2)."
  - "Followed C-4's correction: asserted `pip install 'firestarter[py32]'`, `libusb` and `WinUSB` -- never `Zadig`, which the research measured absent from the file entirely. Written as three independent literal substrings in each test that checks the message, per the plan's instruction."
  - "The subprocess harness copies tests/test_skip_census.py's established idiom (functools.lru_cache, [sys.executable, \"-c\", ...], cwd=_APP_DIR, capture_output=True/text=True, an explicit timeout=) rather than inventing a new one, per the plan's read_first pointer."
  - "The child program purges sys.modules of usb* entries AFTER installing the sys.meta_path blocker (required for correctness in the ci-py32 leg where pyusb is genuinely installed and may already be imported by the time the -c program starts) and pre-asserts `import usb` itself raises BEFORE importing the CLI -- the 'prove the argument took effect' pattern -- so a broken blocker surfaces as an explicit child failure, never a silently-passing test."
  - "The HTTP seam is stubbed by monkeypatching `firestarter.firmware`'s already-imported `requests.get` attribute to raise `requests.RequestException`, which `list_releases()` already catches and handles by returning an empty list -- the real code path, not a bypass of it. No network call is made and the child completes in ~2-3s, well under the 120s timeout."
  - "`_run_blocked_cli` uses `@functools.lru_cache(maxsize=None)` (with a `# noqa: UP033` to keep the explicit idiom named in the plan's read_first, rather than ruff's suggested `@functools.cache` rewrite) -- each distinct argv tuple is cached independently, unlike test_skip_census.py's single maxsize=1 cache for one shared full-suite run."
  - "No requirement checkbox in `.planning/REQUIREMENTS.md` was ticked by this plan. HOST-05 is cited in both commit messages for traceability only -- only Plan 127-12 may tick HOST-01..HOST-08 (the Phase-116 4x premature-tick guard)."

requirements-completed: []  # HOST-05 intentionally left unticked -- only Plan 127-12 may tick HOST-01..HOST-08. This plan cites HOST-05 in commit messages for traceability only.

coverage:
  - id: D1
    description: "`# pragma: no cover` removed from `_require_usb()`'s except-clause; the two statements it hid are now measured by an in-process monkeypatch test, with PyusbMissingError's concrete type, its three C-4-measured message substrings, __cause__ chaining and DfuError subclass relationship all pinned"
    requirement: "HOST-05"
    verification:
      - kind: unit
        ref: "tests/test_py32_pyusb_absent.py::test_require_usb_raises_pyusb_missing_error"
        status: pass
      - kind: unit
        ref: "tests/test_py32_pyusb_absent.py::test_pyusb_missing_error_message_substrings"
        status: pass
      - kind: unit
        ref: "tests/test_py32_pyusb_absent.py::test_pyusb_missing_error_chains_the_import_error"
        status: pass
      - kind: unit
        ref: "tests/test_py32_pyusb_absent.py::test_pyusb_missing_error_is_a_dfu_error"
        status: pass
      - kind: unit
        ref: "tests/test_py32_pyusb_absent.py::test_require_usb_pragma_is_gone_and_the_other_two_remain"
        status: pass
    human_judgment: false
  - id: D2
    description: "A genuine sys.meta_path import blocker (find_spec raises, never returns None) proves fw --help, fw --list and firestarter --help all exit 0 with usb truly unreachable, and that no invocation leaves any usb* entry in sys.modules afterward -- rehearsed both in the pyusb-absent devcontainer and in a throwaway pyusb-present venv"
    requirement: "HOST-05"
    verification:
      - kind: unit
        ref: "tests/test_py32_pyusb_absent.py::test_fw_help_exits_zero_with_py32_options_advertised"
        status: pass
      - kind: unit
        ref: "tests/test_py32_pyusb_absent.py::test_fw_list_exits_zero_with_header_row"
        status: pass
      - kind: unit
        ref: "tests/test_py32_pyusb_absent.py::test_nothing_imported_usb[argv0]"
        status: pass
      - kind: unit
        ref: "tests/test_py32_pyusb_absent.py::test_nothing_imported_usb[argv1]"
        status: pass
      - kind: unit
        ref: "tests/test_py32_pyusb_absent.py::test_firestarter_help_exits_zero_under_the_blocker"
        status: pass
    human_judgment: false
  - id: D3
    description: "fw --dfu-probe under the blocker exits non-zero and surfaces all three C-4 message substrings at the CLI surface, proving PyusbMissingError reaches the operator through DfuError -> FirmwareOperationError -> ClickException, not only the library API"
    requirement: "HOST-05"
    verification:
      - kind: unit
        ref: "tests/test_py32_pyusb_absent.py::test_fw_dfu_probe_surfaces_the_install_hint_at_the_cli"
        status: pass
    human_judgment: false
  - id: D4
    description: "No task ran git push, gh workflow run, or any outward-facing command; no requirement checkbox was ticked in REQUIREMENTS.md"
    verification: []
    human_judgment: true
    rationale: "Absence of a command cannot be proven by a unit test; confirmed by review of every Bash invocation in this session (none contains git push, gh workflow run, git stash, or git add -f) and by re-reading REQUIREMENTS.md's HOST-01..HOST-08 rows unchanged."

# Metrics
duration: ~30min
completed: 2026-08-01
status: complete
---

# Phase 127 Plan 07: PyusbMissingError Coverage + Subprocess Import-Blocker Summary

**Removed the last-remaining `_require_usb()` `# pragma: no cover`, covered its two hidden statements with an in-process monkeypatch, and proved in a subprocess with a genuine `sys.meta_path` import blocker (rehearsed with pyusb actually installed) that `fw --help`, `fw --list`, `firestarter --help` all exit 0 and never leave a trace of `usb` in `sys.modules` — while `fw --dfu-probe` still surfaces the install hint at the CLI surface.**

## Performance

- **Duration:** ~30 min
- **Started:** 2026-08-01 (approx, following STATE.md's 13:11:12Z checkpoint)
- **Completed:** 2026-08-01T13:53:51Z
- **Tasks:** 2/2 executed
- **Files modified:** 2 (1 modified, 1 new)

## Accomplishments

- **Task 1 (`dde0e32`):** Deleted the `# pragma: no cover` comment from the `except ImportError as exc:` line inside `firestarter/py32_dfu.py`'s `_require_usb()` — a single-line diff (`git diff` for this task touches exactly one line). The two other pragmas, on the `_dev`/`_index` property guards, are untouched — `grep -c 'pragma: no cover'` in `py32_dfu.py` went from 3 to 2. Landed `tests/test_py32_pyusb_absent.py`'s in-process half: 5 tests that monkeypatch `sys.modules["usb"]`/`sys.modules["usb.core"]` to `None` (forcing `import usb.core` to raise `ImportError`), then assert `_require_usb()` raises the concrete `PyusbMissingError` subclass (not a bare `ImportError`, not `DfuError` generically), that its message contains all three of `pip install 'firestarter[py32]'`, `libusb` and `WinUSB` (C-4, MEASURED — not `Zadig`, which appears nowhere in the file), that `__cause__` is the original `ImportError` (the `raise ... from exc` chain survived), and that `PyusbMissingError` is a `DfuError` subclass (keeping `_install_with_dfu`'s `except DfuError` catch honest). A fifth test source-scans the file: the `except ImportError` line inside `_require_usb()` carries no coverage-exclusion comment, while the file still carries exactly two such comments in total — behind a non-vacuity guard that `_require_usb` was actually located.
- **Task 2 (`8bdc253`):** Added the subprocess half to the same module. `_run_blocked_cli(argv)`, a `functools.lru_cache`-wrapped harness copying `tests/test_skip_census.py`'s established idiom, runs `[sys.executable, "-c", <program>]` with `cwd=_APP_DIR`, `capture_output=True, text=True, timeout=120`. The child program installs a `sys.meta_path` finder whose `find_spec` **raises** `ModuleNotFoundError` for `usb`/`usb.*` (never returns `None`, which would defer to the next finder and let a genuinely installed pyusb through), purges any pre-existing `usb*` entries from `sys.modules`, then pre-asserts `import usb` itself raises **before** importing the CLI — a broken blocker is a child failure, never a silently-passing test. The HTTP seam (`firestarter.firmware`'s already-imported `requests.get`) is monkeypatched to raise `requests.RequestException`, which `list_releases()` already handles by returning an empty list — no network call, no timeout risk. Five new tests: `fw --help` exits 0 with `--board`/`--usb-id` present in the output; `fw --list` exits 0 with the `Version`/`Channel`/`Published`/`Asset URL` header row (no row-count assertion); a parametrized test over both invocations asserts the child's post-run `usb*` `sys.modules` list is **empty** — the sharpest assertion in the module, since an eager top-level `import usb` anywhere would have had to raise; `firestarter --help` (the top-level group) exits 0 under the same blocker; `fw --dfu-probe` exits non-zero and surfaces all three C-4 message substrings at the CLI surface, proving the operator-facing path (`DfuError` → `FirmwareOperationError` → `ClickException`) is intact, not only the library API.

## Task Commits

1. **Task 1: Remove the `_require_usb()` pragma and cover its two statements in-process** — `dde0e32` (test)
2. **Task 2: The subprocess `meta_path` blocker — `fw --list`/`fw --help` under genuine pyusb absence** — `8bdc253` (test)

Both commits are on `firestarter_app`'s `v1.23-py32f071-integration` branch.

**Meta-repo tracking commit:** pending (this SUMMARY + gitlink bump, committed next per `<final_commit>`)

## Files Created/Modified

- `firestarter_app/firestarter/py32_dfu.py` — one line changed: `# pragma: no cover` deleted from `_require_usb()`'s `except ImportError as exc:` line. Nothing else in the file moved; the two `_dev`/`_index` pragmas and the `raise PyusbMissingError(...)` body are byte-identical to before.
- `firestarter_app/tests/test_py32_pyusb_absent.py` — new module, 11 tests (5 in-process, 6 subprocess).

## Decisions Made

- **Line-number drift, not location drift.** Research's C-3 anchored the pragma at `py32_dfu.py:375` against the tree state at research time. By the time this plan executed (after Plans 127-05/127-06 had already landed their own edits to `py32_dfu.py`), the same line had shifted to `:394` — confirmed by reading the file directly rather than trusting the recorded line number. The *logical* anchor (the `except ImportError` line inside `_require_usb()`, distinct from the two out-of-scope `_dev`/`_index` pragmas) is what the plan actually required, and that identification was unambiguous by content, not by line number.
- **C-3/C-4 followed verbatim** — see key-decisions above.
- **`@functools.lru_cache(maxsize=None)` kept over ruff's suggested `@functools.cache`** with an explicit `# noqa: UP033`, to keep the plan's named idiom (`functools.lru_cache`) literally present in the source, since the plan's own verification script greps for it.
- Coverage measured directly rather than inferred: **before** removing the pragma, `_require_usb()`'s `except`/`raise` lines were excluded from `py32_dfu.py`'s statement count entirely (coverage.py drops pragma-excluded lines from `Stmts`, not just from `Miss`); **after**, `py32_dfu.py` reports `Stmts=417, Miss=95, Cover=77%` with the two previously-excluded lines now counted as **covered** (they do not appear in the `Missing` list: `177, 186-187, 203, 205, 208-209, 213, 223, 236, 238-245, 290, 293-294, 301, 309, 393, 402, 407-419, 423-424, 438-498, 601, 613-629, 637, 701-702, 710, 749-750, 756, 815-816, 820-822, 828-835, 847-848, 858-859`). Full-suite coverage moved from the prior-wave baseline **81.44%** to **81.45%** (1270 tests after Task 1, 1276 after Task 2) — consistent with C-3's claim that removing the pragma "cannot lower coverage."

## Deviations from Plan

None — plan executed exactly as written, including both corrections (C-3, C-4) it was told to apply. No scope creep: only the two files named in the plan's `files_modified` were touched. `/workspaces/firestarter` remains untouched (verified `git status --short` clean both before this plan's first read and after its last commit). The five known pre-existing working-tree lines in `firestarter_app` (`.gitignore`, `.coverage`, `.planning/config.json`, `SECURITY.md`, `write_test_port.sh`) were left untouched throughout. No task ran `git push`, `gh workflow run`, or any `git stash` subcommand. No requirement checkbox in `.planning/REQUIREMENTS.md` was ticked.

## Issues Encountered

- `ruff check` initially flagged `@functools.lru_cache(maxsize=None)` as UP033 (suggesting `@functools.cache`); resolved by adding `# noqa: UP033` to keep the plan's named idiom literally present in the source (the plan's own verification greps for `lru_cache`), rather than adopting the rewrite. `ruff format` reformatted one line in the new module (wrapping the `_run_blocked_cli` call construction) — applied and re-verified clean. Neither is a deviation from plan content, purely mechanical.

## User Setup Required

None — no external service configuration required. The operator-gated CI dispatch remains a later plan's action; this plan only ran local test suites and rehearsals.

## Next Phase Readiness

- `PyusbMissingError`'s branch is measured rather than excluded, with its type, message, chaining and subclass relationship all pinned against the code that actually exists — Plans 127-08 (which hoists `_finish()` into `flash()`) and 127-09 (which adds readback/verify) can both touch `py32_dfu.py` without re-deriving this module's coverage story; this plan's scope discipline note (only the `PyusbMissingError` pragma, not `_finish()` hoisting or readback) was honored — `git diff` for `py32_dfu.py` shows exactly the one-line pragma removal, nothing else.
- Full app suite in the devcontainer (pyusb absent): **1276 collected / 1276 passed / 0 failed / 0 skipped** (1265 baseline + 5 Task-1 tests + 6 Task-2 tests). Coverage gate: `--cov-fail-under=70` passes at **81.45%** total. `ruff check`, `ruff format --check` both clean. `tools/check_mypy_watermark.py`: 1 error vs watermark 35 (unaffected, passes).
- Rehearsed the subprocess mechanism in a throwaway `.[test,py32]` venv with pyusb genuinely installed (deleted afterward): **11/11 passed** — the run that tests the mechanism rather than the ambient environment. Devcontainer confirmed still pyusb-absent afterward (`importlib.util.find_spec("usb")` → `None`).
- `tests/test_skip_census.py`: **5/5 passed** — no new skip reason was added; `grep -c 'importorskip\|skipif\|pytest.skip' tests/test_py32_pyusb_absent.py` returns 0. `ALLOWED_SKIP_REASONS` still holds its original four entries.
- HOST-01..HOST-08 all remain `[ ]` Pending in `.planning/REQUIREMENTS.md` — unaffected by this plan, as instructed. Only Plan 127-12 may tick them.
- `/workspaces/firestarter` remains untouched (read-only input), confirmed clean before and after this plan's execution.

## Self-Check: PASSED

- FOUND: `firestarter_app/firestarter/py32_dfu.py` (modified, one line)
- FOUND: `firestarter_app/tests/test_py32_pyusb_absent.py`
- FOUND: commit `dde0e32` in `firestarter_app` git log
- FOUND: commit `8bdc253` in `firestarter_app` git log
- FOUND: `.planning/phases/127-host-dfu-installer/127-07-SUMMARY.md`
