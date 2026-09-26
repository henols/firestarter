---
phase: 123-non-regression-baselines-gate-hardening
plan: 07
subsystem: testing
tags: [pytest, cross-repo-gates, fail-closed, fixtures, subprocess-testing]

requires:
  - phase: 123-01
    provides: "Phase-wide artifact list and D-09/D-11/D-12 decisions this plan builds"
provides:
  - "tests/fw_presence.py — single cross-repo firmware-presence probe (FW_ROOT, FW_REPO_MARKER, FW_REPO_PRESENT, FW_ABSENT_REASON, requires_fw, fw_path, MissingScanTargetError)"
  - "tests/fixtures/fake_firestarter/ — committed, deliberately incomplete fake firmware sibling tree"
  - "tests/test_fw_presence.py — 7 subprocess tests proving the hard-failure/skip split"
affects: [123-08, 123-09, 123-11]

tech-stack:
  added: []
  patterns:
    - "Single presence-probe module replacing N independent file-existence proxies"
    - "Committed-tree + tmp_path-materialised-marker fixture (D-12 Mechanism 1) for un-committable .git paths"
    - "Subprocess-invoked env-seam tests for module-level import-time constants"

key-files:
  created:
    - firestarter_app/tests/fw_presence.py
    - firestarter_app/tests/fixtures/fake_firestarter/README.md
    - firestarter_app/tests/fixtures/fake_firestarter/include/firestarter.h
    - firestarter_app/tests/fixtures/fake_firestarter/doc/PROTOCOLS.md
    - firestarter_app/tests/test_fw_presence.py
  modified: []

key-decisions:
  - "Used RESEARCH's Mechanism 1 (committed tree without .git + runtime-materialised marker in tmp_path), not CONTEXT's suggested .git-gitfile workaround, which RESEARCH measured does not work (git add reports exit 0 while staging nothing)"
  - "Only FIRESTARTER_FW_ROOT is env-overridable; the .git marker name stays hardcoded to avoid a production misconfiguration knob (RESEARCH D-12 Mechanism 2 rejected)"
  - "This plan does not touch the seven proxy-carrying modules or tick BASE-02/BASE-08 — that rekey and closure are 123-08/123-11"

requirements-completed: []

coverage:
  - id: D1
    description: "Single cross-repo presence probe (tests/fw_presence.py) replacing seven independent file-existence proxies, keyed on ../firestarter/.git"
    verification:
      - kind: unit
        ref: "tests/test_fw_presence.py::test_fw_absent_reason_is_one_canonical_string"
        status: pass
      - kind: unit
        ref: "tests/test_fw_presence.py::test_marker_name_is_git_and_not_env_overridable"
        status: pass
    human_judgment: false
  - id: D2
    description: "Missing scan target under a present repo is a hard failure (MissingScanTargetError), never a skip, proven against a real missing file through the production fw_path() resolver via subprocess"
    verification:
      - kind: unit
        ref: "tests/test_fw_presence.py::test_present_repo_missing_target_is_hard_failure"
        status: pass
      - kind: unit
        ref: "tests/test_fw_presence.py::test_present_repo_present_target_resolves"
        status: pass
      - kind: unit
        ref: "tests/test_fw_presence.py::test_absent_repo_is_honest_skip"
        status: pass
    human_judgment: false
  - id: D3
    description: "Committed, deliberately-incomplete fake firmware sibling (tests/fixtures/fake_firestarter/), verified present via git ls-files with no .git path component, README recording the committed-vs-synthesised split"
    verification:
      - kind: unit
        ref: "tests/test_fw_presence.py::test_committed_fixture_is_genuinely_incomplete"
        status: pass
      - kind: unit
        ref: "tests/test_fw_presence.py::test_committed_fixture_has_no_git_path_component"
        status: pass
    human_judgment: false

duration: 45min
completed: 2026-07-30
status: complete
---

# Phase 123 Plan 07: Cross-Repo Firmware-Presence Probe + Hard-Failure Fixture Summary

**One `tests/fw_presence.py` module now decides firmware-repo presence for the whole host suite, keyed on the un-renameable `../firestarter/.git` marker, and turns a present-repo-missing-scan-target into a named `MissingScanTargetError` instead of a silent skip — proven against a committed, deliberately-incomplete fake sibling via 7 subprocess tests.**

## Performance

- **Duration:** ~45 min
- **Completed:** 2026-07-30
- **Tasks:** 3 (all `type="auto"`)
- **Files modified:** 5 created (fw_presence.py, test_fw_presence.py, fake_firestarter/{README.md, include/firestarter.h, doc/PROTOCOLS.md})

## Accomplishments

- `firestarter_app/tests/fw_presence.py` — the single cross-repo presence probe: `FW_ROOT`, `FW_REPO_MARKER`, `FW_REPO_PRESENT`, `FW_ABSENT_REASON`, `requires_fw`, `fw_path()`, `MissingScanTargetError`. Repo presence keys on `../firestarter/.git`; `fw_path()` raises a named exception (never a skip) when the repo is present but a requested path is not.
- `firestarter_app/tests/fixtures/fake_firestarter/` — a committed, deliberately incomplete fake firmware sibling: `include/firestarter.h` and `doc/PROTOCOLS.md` present as tiny fixture stubs; `src/proms/eeprom_28c.cpp` deliberately absent. No `.git` path component is committed (git refuses it at exit 0 while staging nothing — measured); the marker is materialised only in `tmp_path` at test time.
- `firestarter_app/tests/test_fw_presence.py` — 7 subprocess tests proving: present-target resolution, present-repo-missing-target hard failure (with no skip token in the output), absent-repo honest skip, exactly one canonical reason string, the marker name is pinned to `.git` with no env override, the committed fixture's incompleteness (checked against the real committed tree, not the tmp copy), and the fixture's total absence of any `.git` path component.

## Task Commits

1. **Task 1: Write tests/fw_presence.py** - `14824d4` (test)
2. **Task 2: Commit the fake firmware sibling fixture tree** - `f2e0a90` (test)
3. **Task 3: Write tests/test_fw_presence.py** - `7a279dd` (test) — includes a one-line wording fix to `fw_presence.py`'s `MissingScanTargetError` message (see Deviations)

All three commits are inside the `firestarter_app` submodule, on branch `v1.23-py32f071-integration`.

## Files Created/Modified

- `firestarter_app/tests/fw_presence.py` - the single presence probe (created; one wording fix in Task 3's commit)
- `firestarter_app/tests/fixtures/fake_firestarter/README.md` - records what is committed vs. synthesised, and the `git ls-files` verification rule
- `firestarter_app/tests/fixtures/fake_firestarter/include/firestarter.h` - present fixture stub
- `firestarter_app/tests/fixtures/fake_firestarter/doc/PROTOCOLS.md` - present fixture stub
- `firestarter_app/tests/test_fw_presence.py` - 7 subprocess tests

## Decisions Made

- Followed RESEARCH's measured Mechanism 1 verbatim: commit the fake sibling tree *without* the `.git` marker; materialise the marker only in `tmp_path` at test time via `_materialise_fake_sibling()`. CONTEXT's suggested `.git`-gitfile workaround was confirmed (by RESEARCH, and not re-tested here) to fail identically — `git add`/`git add -f` on any `.git` path component reports exit 0 while staging nothing.
- Kept the marker name (`.git`) hardcoded; only `FIRESTARTER_FW_ROOT` (the root path) is env-overridable, per RESEARCH's recommendation against Mechanism 2 (an overridable marker name would be a production misconfiguration knob).
- Scoped strictly to this plan's boundary: did not touch any of the seven existing proxy-carrying modules (that rekey is 123-08), and ticked no requirements (BASE-02/BASE-08 close only in 123-11), per the plan's explicit `requirement_closure` note.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] `MissingScanTargetError` message tripped its own paired test's no-skip-token assertion**
- **Found during:** Task 3 (writing `test_present_repo_missing_target_is_hard_failure`)
- **Issue:** The Task-1 exception message said "...rather than deleting or **skipping** this gate." Test 2 asserts the combined subprocess output contains no `"SKIP"` token (case-insensitive) — the word "skipping" in the message's own prose tripped that assertion, since `"SKIP"` is a substring of `"SKIPPING"`.
- **Fix:** Reworded to "...rather than removing or bypassing this gate." — same meaning, no `skip`-shaped substring.
- **Files modified:** `firestarter_app/tests/fw_presence.py`
- **Verification:** `test_present_repo_missing_target_is_hard_failure` passes; full `tests/test_fw_presence.py` 7/7 green.
- **Committed in:** `7a279dd` (part of Task 3's commit)

**2. [Rule 1 - Bug] Docstring literal `monkeypatch.setenv` tripped a plan acceptance grep**
- **Found during:** Self-check before finalizing Task 3
- **Issue:** The module docstring mentioned the literal string `monkeypatch.setenv` in prose (explaining why it is inert here). The plan's acceptance criterion is a literal `grep -c 'monkeypatch.setenv'` count of zero across the whole file, so the prose mention — though never actually calling `monkeypatch.setenv` — tripped the grep.
- **Fix:** Reworded the docstring to describe the same fact ("an in-process pytest environment-variable fixture patch...") without the literal string.
- **Files modified:** `firestarter_app/tests/test_fw_presence.py`
- **Verification:** `grep -c 'monkeypatch.setenv' tests/test_fw_presence.py` → `0`; `ruff format --check` clean.
- **Committed in:** `7a279dd` (part of Task 3's commit)

---

**Total deviations:** 2 auto-fixed (both Rule 1, both self-referential wording collisions with the plan's own literal-substring acceptance checks, no scope creep).
**Impact on plan:** Both fixes are one-line wording changes; no behavioral or architectural impact.

## Issues Encountered

- **Verify-block quiet-flag stacking (environment quirk, not a code defect):** the plan's literal verification command `python3 -m pytest tests/ -q 2>&1 | grep -qE '1141 passed'` does not match, because `pyproject.toml`'s `addopts = "-ra -q"` already applies `-q`; stacking a second explicit `-q` on the CLI raises pytest's quiet level to `-qq`, which additionally suppresses the final `"N passed in Xs"` summary line (verified: `-qq` behaves identically to `-q -q`; plain `pytest tests/` or `pytest tests/ -v` both correctly print `"1141 passed in ...s"`). The underlying fact the criterion checks — 1141 passed, 0 skipped — is independently confirmed via `python3 -m pytest tests/` (no extra `-q`) and via `-ra`, both showing `1141 passed in ...s` with no `skipped` anywhere in the output. Recorded here rather than "fixed" because it is a pre-existing `pyproject.toml` configuration interacting with the plan's verify command, not a defect in the module or test file this plan produced.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- `tests/fw_presence.py` is built, standalone-tested, and exports exactly the names 123-08 and 123-09 need to import (`FW_ROOT`, `FW_REPO_MARKER`, `FW_REPO_PRESENT`, `FW_ABSENT_REASON`, `requires_fw`, `fw_path`, `MissingScanTargetError`).
- `tests/fixtures/fake_firestarter/` is committed and available for 123-08's and 123-09's own subprocess tests to reuse via `_materialise_fake_sibling`-shaped helpers.
- 123-08 can now do a mechanical rekey of the seven proxy-carrying modules against something already tested, rather than seven parallel from-scratch rewrites — including the one non-decorator inline guard (`test_sdp_table_parity.py:299`) and the one compound two-path proxy (`test_dispatch_mirror.py`) that RESEARCH flagged as easy to miss.
- No blockers. Host suite is at 1141 passed / 0 skipped; ruff/format/mypy trio green; meta repo remains on `gsd/v1.23-py32f071-integration` with no branch switch.

---
*Phase: 123-non-regression-baselines-gate-hardening*
*Completed: 2026-07-30*

## Self-Check: PASSED

- FOUND: `firestarter_app/tests/fw_presence.py`
- FOUND: `firestarter_app/tests/fixtures/fake_firestarter/README.md`
- FOUND: `firestarter_app/tests/fixtures/fake_firestarter/include/firestarter.h`
- FOUND: `firestarter_app/tests/fixtures/fake_firestarter/doc/PROTOCOLS.md`
- FOUND: `firestarter_app/tests/test_fw_presence.py`
- FOUND commit `14824d4` (Task 1)
- FOUND commit `f2e0a90` (Task 2)
- FOUND commit `7a279dd` (Task 3)
