---
phase: 127-host-dfu-installer
plan: 02
subsystem: host-cli-packaging
tags: [packaging, pyusb, source-scan, non-vacuity, fail-closed]

# Dependency graph
requires:
  - phase: 127-host-dfu-installer
    plan: "127-01"
    provides: "D-17's accepted-deviation comment at flash_method() in firestarter/firmware.py, the scan target for this plan's second gate"
provides:
  - "[py32] extra's pyusb floor raised to >=1.3.1,<2 (HOST-07/D-19), exit-code-checked rather than reader-checked"
  - "tests/test_py32_packaging.py: two independent non-vacuous textual gates (pyusb floor + D-17 record), each with a proven fail-closed RED path"
affects: [127-06, 127-10, 127-11, 127-12]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Regex source-scan over pyproject.toml instead of a TOML parser, following the tests/test_revision_constants_parity.py idiom, so the py39 floor is never violated by tomllib"
    - "Shared assertion-helper pattern: one function (_read_py32_requirements / _read_d17_record) called by both the real gate leg and a monkeypatched fail-closed planted-file leg, proving the gate can genuinely fail rather than only by inspection"

key-files:
  created:
    - firestarter_app/tests/test_py32_packaging.py
  modified:
    - firestarter_app/pyproject.toml (py32 extra: pyusb>=1.2.1 -> pyusb>=1.3.1,<2, plus a citing comment; nothing else moved)

key-decisions:
  - "Regex block-match anchored with `^py32\\s*=\\s*\\[` (MULTILINE) rather than an unanchored search, so the scan cannot accidentally match a comment mentioning the extra"
  - "_D17_PROXIMITY_PHRASE ('accepted deviation') is checked twice on purpose: once as a member of the five-phrase presence set, once specifically inside the 25-line proximity window preceding def flash_method( -- catches a phrase surviving the file but drifting away from the function it describes"
  - "Both fail-closed RED legs proven empirically during execution (not just by pytest.raises in the committed test): reverted pyproject.toml's floor and firmware.py's D-17 comment in turn, re-ran the relevant test to confirm a real AssertionError, then restored both files and confirmed a clean git diff before committing"

requirements-completed: []  # HOST-07 and HOST-01 intentionally left unticked -- only Plan 127-12 may tick HOST-01..HOST-08 (Phase-116 4x premature-tick guard)

coverage:
  - id: D1
    description: "[py32] extra reads pyusb>=1.3.1,<2 and nothing else in pyproject.toml moved"
    verification:
      - kind: unit
        ref: "grep -c 'pyusb>=1.3.1,<2' pyproject.toml -> 1; grep -c 'pyusb>=1.2.1' pyproject.toml -> 0; git diff pyproject.toml confined to the py32 block"
        status: pass
    human_judgment: false
  - id: D2
    description: "test_py32_packaging.py's floor gate and D-17 gate are each non-vacuous and fail-closed"
    verification:
      - kind: unit
        ref: "pytest tests/test_py32_packaging.py -v -> 6 passed; manual revert of pyproject.toml's floor and firmware.py's D-17 comment each independently reproduced a real AssertionError, then both files restored (git diff clean)"
        status: pass
    human_judgment: false
  - id: D3
    description: "No TOML parser imported, no skip marker added, ruff/skip-census/full-suite all green"
    verification:
      - kind: unit
        ref: "grep -c 'import toml' -> 0; grep -c 'importorskip|skipif|pytest.skip' -> 0; ruff check + ruff format --check -> clean; pytest tests/test_skip_census.py -> 5 passed; pytest tests/ -> 1236 passed, 0 failed"
        status: pass
    human_judgment: false

# Metrics
duration: 25min
completed: 2026-08-01
status: complete
---

# Phase 127 Plan 02: pyusb Floor + D-17 Record Gates Summary

**Raised the `[py32]` extra's `pyusb` floor to `>=1.3.1,<2` and built `tests/test_py32_packaging.py`, a two-gate regex source-scan (no TOML parser) that holds both the floor and D-17's accepted-deviation comment in place — each gate proven, by actually reverting its target mid-execution and re-running, to genuinely fail rather than pass vacuously.**

## Performance

- **Duration:** ~25 min
- **Started:** 2026-08-01 (per plan dispatch)
- **Completed:** 2026-08-01
- **Tasks:** 2/2 executed
- **Files modified:** 1 modified (`pyproject.toml`), 1 created (`tests/test_py32_packaging.py`)

## Accomplishments

- Confirmed the pre-task baseline: `python3 -m pytest tests/ -q` → **1230 passed, 0 failed** (not the plan's stated 1216 — Plan 127-04 landed additional tests on this branch since 127-01's SUMMARY was written; this is expected drift, recorded per D-04, never gated).
- Task 1: changed `firestarter_app/pyproject.toml`'s `[py32]` extra from `pyusb>=1.2.1` to `pyusb>=1.3.1,<2`, with a citing comment naming HOST-07/D-19 and explaining both bounds (1.3.1 is the current release satisfiable on the py39 floor; `<2` refuses a future major that could reorder `ctrl_transfer`'s parameters, which Plan 127-06's API-surface test pins). `requires-python`, `extend-exclude`, the `dev`/`test` extras, and `[tool.pytest.ini_options]` all confirmed unchanged. `test` extra confirmed to still contain zero `pyusb` entries. Full suite re-ran green: 1230 passed, 0 failed.
- Task 2: created `firestarter_app/tests/test_py32_packaging.py` with two independent gates, each built on a shared assertion-helper (`_read_py32_requirements` / `_read_d17_record`) called by both the real leg and a fail-closed planted-file leg — the same pattern `tests/test_revision_constants_parity.py` uses for its `FIRMWARE_HEADER` monkeypatch:
  1. **Non-vacuity** — `_py32_extra_requirements` over the real `pyproject.toml` must return a non-empty list.
  2. **Floor equality** — the extracted list must equal exactly `["pyusb>=1.3.1,<2"]` (`_EXPECTED_PYUSB_SPEC`, written as an independent literal, never derived from the file under test).
  3. **pyusb absent from `test`** — asserts no requirement in the `test` extra's block starts with `pyusb` (case-insensitive), the D-02 two-leg-design assertion.
  4. **Packaging fail-closed RED** — monkeypatches `_PYPROJECT` to a `tmp_path` file with no `py32` block; `_read_py32_requirements()` raises `AssertionError`.
  5. **D-17 record** — asserts firmware.py contains all five phrases (`accepted deviation`, `D-17`, `HOST-01`, `_install_with_avrdude`, `avrdude-mcu-detection-fallback`) and that `accepted deviation` occurs within 25 lines preceding `def flash_method(`, with a non-vacuity guard that `def flash_method(` was located at all.
  6. **D-17 fail-closed RED** — monkeypatches `_FIRMWARE_PY` to a planted file defining `flash_method` but carrying none of the five phrases; `_read_d17_record()` raises `AssertionError`.
- Ran all 6 tests: **6 passed**. `grep -c 'import toml'` → 0; `grep -c 'importorskip\|skipif\|pytest.skip'` → 0.
- **Proved both gates fail against a live revert, not just against `pytest.raises` in the committed test:** backed up `pyproject.toml`, changed the floor back to `pyusb>=1.2.1`, re-ran `test_py32_floor_is_exactly_the_expected_spec` → genuine `AssertionError` diffing `'pyusb>=1.2.1' != 'pyusb>=1.3.1,<2'`; restored the file, confirmed `git diff --stat pyproject.toml` empty. Backed up `firestarter/firmware.py`, stripped the D-17 comment block via a scripted regex substitution, re-ran `test_d17_record_phrases_present_and_proximate_to_flash_method` → genuine `AssertionError` naming the four missing phrases; restored the file, confirmed `git diff --stat firestarter/firmware.py` empty.
- `ruff check firestarter/ tests/` and `ruff format --check firestarter/ tests/` both exit 0 (one auto-format pass applied to the new test file's long assert message before committing).
- `pytest tests/test_skip_census.py -q` → **5 passed** — no new `ALLOWED_SKIP_REASONS` entry.
- Full suite: `pytest tests/ -q` → **1236 passed, 0 failed** (1230 baseline + 6 new — the count is recorded as an observation per D-04, never asserted in code).
- No `pip install` was run against the shared devcontainer environment at any point in this plan.
- `/workspaces/firestarter` (firmware sibling repo) `git status --porcelain` confirmed empty before and after — nothing written there.
- The app repo's 5 known pre-existing porcelain lines (` M .gitignore`, `?? .coverage`, `?? .planning/config.json`, `?? SECURITY.md`, `?? write_test_port.sh`) are unchanged throughout.
- No requirement checkbox in `.planning/REQUIREMENTS.md` was ticked (HOST-01 and HOST-07 remain whatever status they were prior to this plan).

## Task Commits

1. **Task 1: Raise the `[py32]` extra to `pyusb>=1.3.1,<2`** — `e08a01d` (feat, inside `firestarter_app`)
2. **Task 2: `tests/test_py32_packaging.py` — non-vacuous floor gate plus the D-17 record gate** — `d36b53f` (test, inside `firestarter_app`)

**Meta-repo tracking commit:** pending (this SUMMARY + gitlink bump, committed next per `<final_commit>`)

## Files Created/Modified

- `firestarter_app/pyproject.toml` — `[py32]` extra floor raised, citing comment added; nothing else changed
- `firestarter_app/tests/test_py32_packaging.py` — new: two non-vacuous, fail-closed-proven textual gates

## Decisions Made

- Anchored the `py32 = [` and `test = [` block regexes with `^...$` (MULTILINE) rather than an unanchored search, so a comment merely mentioning either extra's name can never be mistaken for the block itself.
- Checked the `"accepted deviation"` phrase twice deliberately: once as a member of the five-phrase whole-file presence set, once specifically inside the 25-line proximity window preceding `def flash_method(` — this is what would catch the phrase surviving somewhere in the file while drifting away from the function it is meant to describe.
- Went beyond the plan's `pytest.raises` proof and additionally reverted each gate's real target file on disk mid-execution to confirm a live `AssertionError`, then restored both files and verified a clean `git diff` before committing — the plan's own success criterion ("prove each FAILS when its target is reverted, then restore") is stronger than an in-test monkeypatch alone would demonstrate, since the monkeypatch approach never touches the actual tracked files.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] `ruff format` reflowed one long assert message in the new test file**
- **Found during:** Task 2 verification (`ruff format --check`)
- **Issue:** `test_py32_floor_is_exactly_the_expected_spec`'s f-string assert message was written across two lines that ruff's formatter collapses to one.
- **Fix:** Ran `ruff format tests/test_py32_packaging.py`; re-verified `ruff format --check` exits 0 and the 6 tests still pass.
- **Files modified:** `firestarter_app/tests/test_py32_packaging.py`
- **Commit:** folded into `d36b53f` (pre-commit, no separate commit needed)

### Informational — pre-existing plan-text imprecision (not a defect introduced by this plan)

**2. The plan's Task 1 acceptance criterion `grep -c 'extend-exclude' pyproject.toml` returning `1` does not hold against the real file**
- **Found during:** Task 1 verification
- **Detail:** `pyproject.toml` contains `extend-exclude` twice: once in the actual `[tool.ruff] extend-exclude = [...]` line, and once inside a pre-existing explanatory comment above it ("`extend-exclude` (not exclude, to keep ruff's built-in defaults)"). This was true before this plan's edit and is unchanged by it — `git diff pyproject.toml` for both tasks touches only the `py32` block.
- **Not fixed — not in scope:** the comment predates this plan and is not part of the `py32` block this plan owns; correcting the plan's own literal grep count is out of scope for an executor and is recorded here as an observation only.

**Total deviations:** 1 auto-fixed (formatting), 1 informational (pre-existing plan-text imprecision, no code change needed).
**Impact on plan:** None — both gates, the floor change, and the full verification chain are satisfied exactly as the plan's substantive acceptance criteria require.

## Issues Encountered

None beyond the two items documented above.

## User Setup Required

None — no external service configuration required. No `pip install` was run against the shared devcontainer environment; `pyusb` is not installed there, matching Plan 127-07's characterization requirement.

## Claim Ceiling

This plan proves a `pyproject.toml` declaration and two source-scan gates over already-committed files. It proves nothing about dependency resolution against a real package index (that is Plan 127-11's operator-dispatched `ci-py32` CI run) and nothing about a PY32F071 board.

## Next Phase Readiness

- Plan 127-06's `ci-py32` job will resolve `.[test,py32]` against the raised floor; the local gate here catches a silent regression to the old floor before that CI run ever executes.
- Plan 127-10's `doc/PY32F071-FIRMWARE-INSTALL.md` §Dependencies documentation should cite `pyusb>=1.3.1,<2` — this file is the source of truth for that figure.
- D-17's in-code deviation record is now held in place by a gate proven (both via `pytest.raises` and via a live on-disk revert) to fail if a future refactor deletes it.

## Self-Check: PASSED

- `firestarter_app/pyproject.toml` — FOUND, contains `pyusb>=1.3.1,<2`
- `firestarter_app/tests/test_py32_packaging.py` — FOUND, 6 tests collected and passing
- Commit `e08a01d` — FOUND in `firestarter_app` git log
- Commit `d36b53f` — FOUND in `firestarter_app` git log
