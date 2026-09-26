---
phase: 131-gate-hardening-ci-parity
plan: 01
subsystem: testing
tags: [mypy, ci, gate-hardening, pyproject, python-version, backlog]

requires: []
provides:
  - "v1.30 milestone branch `gsd/v1.30-sdp-surface-retirement` forked in `firestarter_app` off `beta` @ 16a313a"
  - "Fail-closed `tools/check_mypy_watermark.py` — classify_mypy_result()/run_mypy()/mypy_argv()/enforce_watermark() split (D-01), returncode-before-regex ordering, completion-clause requirement, MIN_CHECKED_SOURCE_FILES=120 floor, sys.executable -m mypy invocation"
  - "Honest `[tool.mypy] python_version = \"3.10\"` in pyproject.toml with the silent-discard history recorded in-line"
  - "mypy pin bounded `>=2.1.0,<3`"
  - "ROADMAP backlog stubs 999.26 (py3.9 type-checking floor) and 999.27 (mypy minimum-target treadmill)"
  - "REQUIREMENTS.md Out-of-Scope row superseded (F-03); GATE-05 ticked with evidence"
affects: [131-02, 132]

tech-stack:
  added: []
  patterns:
    - "Pure classifier + thin runner split for a CI checker (D-01) — no env-var argv seam, unlike the other five check_*.py tools whose env seams override scan targets rather than the program invoked"
    - "Never-vacuous guard ordering (returncode -> config-rejection -> completion-clause -> coverage-floor) mirroring check_no_exists_proxy.py's never-vacuous-before-missing-target discipline"

key-files:
  created: []
  modified:
    - firestarter_app/tools/check_mypy_watermark.py
    - firestarter_app/pyproject.toml
    - .planning/ROADMAP.md
    - .planning/REQUIREMENTS.md

key-decisions:
  - "D-01: no env-var seam overriding mypy's argv — the one gate whose entire sin was being bypassable gets no bypass seam"
  - "D-05: MIN_CHECKED_SOURCE_FILES = 120 is a literal, not derived from a glob (a derived count is vacuously always satisfied)"
  - "D-13: keep requires-python >=3.9 and the 3.9 classifier; file the py3.9 type-checking gap as backlog 999.26 instead of silently absorbing it"
  - "D-14: mypy pin gets an upper bound <3, since the gate's discriminator is now a regex over mypy's summary-line format"
  - "F-03: REQUIREMENTS.md's 'Filing the py3.9-drop backlog item' Out-of-Scope row is superseded (not deleted) by D-13, which was decided later the same day"

requirements-completed: [GATE-05]

coverage:
  - id: D1
    description: "v1.30 milestone branch forked in firestarter_app at the stated base (16a313a on beta), with no pre-existing untracked file swept into it"
    verification:
      - kind: unit
        ref: "git -C firestarter_app rev-parse --abbrev-ref HEAD == gsd/v1.30-sdp-surface-retirement; git -C firestarter_app rev-parse HEAD starts 16a313a"
        status: pass
    human_judgment: false
  - id: D2
    description: "check_mypy_watermark.py fails closed: returncode-before-regex, completion-clause required, 120-file coverage floor, sys.executable -m mypy"
    requirement: "GATE-01"
    verification:
      - kind: unit
        ref: "in-process classify_mypy_result()/enforce_watermark() acceptance checks (truncated-run exit 2, coverage-floor exit 2, config-rejection exit 2, over-watermark exit 1) — all run and confirmed this session"
        status: pass
      - kind: integration
        ref: "python3 tools/check_mypy_watermark.py in this devcontainer now exits 2 (was 0)"
        status: pass
    human_judgment: false
  - id: D3
    description: "pyproject.toml python_version is honest (3.10) with the discard history, py3.9 cost, and 2026-10-31 treadmill in the comment; requires-python/classifier/watermark untouched"
    requirement: "GATE-05"
    verification:
      - kind: unit
        ref: "python3 -c \"import tomllib; ...\" prints 3.10; git diff scoped to exactly the two commented lines"
        status: pass
    human_judgment: false
  - id: D4
    description: "Full firestarter_app suite (1303 tests) and ruff (firestarter/ tests/) stay green after the gate hardening and pyproject edits"
    verification:
      - kind: unit
        ref: "python3 -m pytest tests/ -q -> 1303 passed in 136.42s; ruff check/format --check firestarter/ tests/ -> clean"
        status: pass
    human_judgment: false
  - id: D5
    description: "ROADMAP backlog 999.26/999.27 filed and REQUIREMENTS.md Out-of-Scope row superseded, not rewritten"
    verification:
      - kind: unit
        ref: "grep counts for '### Phase 999.26:'/'### Phase 999.27:' == 1 each; grep 'py3.9-drop backlog item' shows both 'deliberately not filed' and 'SUPERSEDED'"
        status: pass
    human_judgment: false

duration: 40min
completed: 2026-08-03
status: complete
---

# Phase 131 Plan 01: Fork milestone branch, harden mypy gate, honest python_version Summary

**Fail-closed mypy watermark gate (returncode-before-regex, 120-file coverage floor, `sys.executable -m mypy`) plus an honest `python_version = "3.10"` in `firestarter_app` — no watermark set, no mypy errors fixed.**

## Performance

- **Duration:** ~40 min
- **Tasks:** 3 (Task 1 fork+backlog+supersede; Tasks 2+3 committed together per the plan's explicit instruction)
- **Files modified:** 4 (`tools/check_mypy_watermark.py`, `pyproject.toml`, `ROADMAP.md`, `REQUIREMENTS.md`)

## Accomplishments

- Forked `gsd/v1.30-sdp-surface-retirement` in `firestarter_app` off `beta` @ `16a313a`, with none of the five pre-existing untracked/modified paths (`.coverage`, `.planning/config.json`, `SECURITY.md`, `write_test_port.sh`, the modified `.gitignore`) swept into it.
- Split `count_mypy_errors()` into `mypy_argv()` / `run_mypy()` / `classify_mypy_result()` / `enforce_watermark()`. The classifier now consults `result.returncode` before any error-count regex, requires mypy's `(checked N source files)` completion clause, rejects a config-diagnostic line as its own guard, and enforces a literal `MIN_CHECKED_SOURCE_FILES = 120` floor. `mypy_argv()` returns `[sys.executable, "-m", "mypy", "firestarter/", "tests/"]` — no bare `mypy` off `PATH` survives.
- **Measured before/after in this devcontainer:** `python3 tools/check_mypy_watermark.py` previously printed `mypy errors: 1 (watermark: 35)` and exited **0** on a run that checked 1 of 120 files and mypy itself exited 2. After this plan it exits **2** and names the mypy exit code — the fail-open is closed.
- Reworded the below-watermark `INFO:` message: lowering the watermark is now stated as conditional on a verified-complete run (`only if this run is complete`), never an unconditional bypass suggestion.
- `pyproject.toml`: `[tool.mypy] python_version` changed `"3.9"` → `"3.10"` — a zero-behaviour change (3.10 was mypy's already-measured effective target) — with a comment recording the silent-discard history since 2026-05-27, the honest py3.9 type-checking gap this creates, and the 2026-10-31 Python 3.10 EOL treadmill. The `test` extra's mypy pin gained an upper bound: `mypy>=2.1.0,<3`, commented with the exact regexes (`_FOUND_RE`, `_CLEAN_RE`) that depend on the summary-line format staying stable.
- Filed ROADMAP backlog stubs **999.26** (restore type-level enforcement of the advertised py3.9 floor) and **999.27** (the mypy minimum-target treadmill, Python 3.10 EOLs 2026-10-31), cross-linked from `FUT-MYPY-01`.
- Superseded (not deleted) REQUIREMENTS.md's "Filing the py3.9-drop backlog item" Out-of-Scope row — the original sentence is preserved verbatim, with a `[⚠ SUPERSEDED 2026-08-03 ...]` block naming D-13 and the two backlog stub numbers (correction F-03).
- Ticked `GATE-05` in REQUIREMENTS.md with an evidence clause naming the file, line range, commit, and the measured `tomllib` check. `GATE-01`/`GATE-02`/`GATE-03`/`GATE-04` remain unticked — they span into 131-02, which owns the fail-provable proof.

## Task Commits

1. **Task 1: Fork the milestone branch, file backlog 999.26 and 999.27, supersede the Out-of-Scope row** — meta repo commit `228e783` (`docs(131-01): fork v1.30 milestone branch, file backlog 999.26/999.27, supersede Out-of-Scope row`); submodule branch created at `16a313a` (no commit — a branch pointer only).
2. **Tasks 2+3: Make the mypy watermark gate fail closed; make python_version honest** — `firestarter_app` commit `9465c4c` (`fix(131-01): fail-closed mypy watermark gate; honest python_version (GATE-01..05)`), on branch `gsd/v1.30-sdp-surface-retirement`. The plan's own instructions direct these two tasks to land in one commit ("commit the submodule changes from tasks 2 and 3 together").

**Plan metadata:** captured in this SUMMARY's own commit (final metadata commit, meta repo) — includes the GATE-05 tick in `.planning/REQUIREMENTS.md`.

## Files Created/Modified

- `firestarter_app/tools/check_mypy_watermark.py` — fail-closed classifier/runner split (GATE-01/02/03/04).
- `firestarter_app/pyproject.toml` — `python_version = "3.10"` (GATE-05), `mypy>=2.1.0,<3` (D-14).
- `.planning/ROADMAP.md` — backlog stubs 999.26, 999.27.
- `.planning/REQUIREMENTS.md` — Out-of-Scope row superseded; `FUT-MYPY-01` cross-link; `GATE-05` ticked with evidence.

## Decisions Made

- **D-01 (no env-var argv seam):** followed exactly as specified — the classifier is pure and tested against canned output; no production code path reads the environment for this gate.
- **D-05 (literal `MIN_CHECKED_SOURCE_FILES = 120`):** followed exactly — not derived from a glob, per the plan's explicit reasoning that a derived count is vacuously satisfied by whatever tree exists.
- **D-13/D-14:** followed exactly — `requires-python` and the 3.9 classifier are byte-unchanged; the honest gap is filed as backlog 999.26/999.27 rather than silently absorbed.
- **F-03 correction applied as directed:** the Out-of-Scope row is superseded in-place with its original text preserved, in the same commit as the backlog filing, per the plan's stated instruction.

## Deviations from Plan

None — plan executed exactly as written. One clarification, not a deviation: `enforce_watermark(count, watermark)`'s signature (fixed by the plan) has no `checked`-count parameter, so its below-watermark `INFO:` message states the completeness criterion generically ("this run's mypy invocation passed both the completion-clause guard and the MIN_CHECKED_SOURCE_FILES coverage floor") rather than repeating a specific checked-file number — that number is already printed separately by `classify_mypy_result`'s own coverage line (guard 7) before `enforce_watermark` is ever called. This satisfies every acceptance criterion for `enforce_watermark` (exact first line, `only if this run is complete` substring, exit 1 above watermark) without adding a parameter the plan's own signature contract excludes.

Ran `ruff format` after the initial `check_mypy_watermark.py` write, which reformatted two lines (a wrapped `re.search` call and a wrapped `.format()` call) to satisfy `ruff format --check`; no logic changed and both acceptance-criteria re-runs after the reformat still pass.

## Issues Encountered

One self-caught authoring mistake, fixed before commit: the first draft of the `python_version` comment repeated the literal string `python_version = "3.10"` inside its own prose, which double-counted against the acceptance criterion `grep -c 'python_version = "3.10"' == 1`. Reworded the comment's opening clause to reference the change by decision ID only; re-verified the grep count is exactly 1 and the file still parses as valid TOML with `python_version == "3.10"`.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- **GATE-01/02/03/04 mechanism is in place; 131-02 owns the fail-provable proof** (the paired pytest suite, the RED-preserving revert-and-reobserve, and ticking those four requirements Complete).
- **`firestarter_app`'s primary `ci` job stays RED by design.** This plan set no watermark, deleted nothing, and fixed none of the 69 inherited mypy errors — it hardened the mechanism only. Any artifact implying CI is green after this plan, or reporting an error count as a Phase 131 achievement, would be the v1.22 C-5 overclaim class; none exists here.
- `firestarter` (firmware) remains completely untouched — `git -C /workspaces/firestarter status --short` is empty and its HEAD is unchanged throughout this plan.
- No push, tag, merge, or `gh workflow run` was performed by this plan; the milestone branch exists only locally in `firestarter_app`.

---
*Phase: 131-gate-hardening-ci-parity*
*Completed: 2026-08-03*

## Self-Check: PASSED

- FOUND: `.planning/phases/131-gate-hardening-ci-parity/131-01-SUMMARY.md`
- FOUND: `firestarter_app/tools/check_mypy_watermark.py`
- FOUND commit `228e783` (meta: fork + backlog + supersede)
- FOUND commit `9465c4c` (firestarter_app: gate hardening + python_version)
- FOUND commit `060e64f` (meta: SUMMARY + GATE-05 tick)
