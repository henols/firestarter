---
phase: 127-host-dfu-installer
plan: 01
subsystem: firmware-install
tags: [git-merge, dfu, pyusb, host-cli, ci-gates]

# Dependency graph
requires:
  - phase: 124-firmware-integration-merge
    provides: "Precedent for a large cross-history merge onto a milestone branch (though 124 squashed; this plan deliberately does not)"
provides:
  - "feature/py32f071-fw-install @ 4ee64a1 landed on v1.23-py32f071-integration as a real --no-ff merge commit (63ce44e), parent SHAs verified to include 4ee64a1 literally"
  - "firestarter/py32_dfu.py (832L), firestarter/channel.py (81L), tests/test_py32_dfu.py (654L/58 tests), doc/PY32F071-FIRMWARE-INSTALL.md (273L) now exist on the branch"
  - "D-17 accepted-deviation comment recorded at flash_method() in firestarter/firmware.py (commit 6c621b4), naming HOST-01, D-17, _install_with_avrdude, and avrdude-mcu-detection-fallback"
  - "A measured, on-the-record contradiction of C-1's zero-fixup prediction: tests/test_characterization.py::test_help_fw fails post-merge (pre-existing snapshot doesn't include py32f071 in `fw --help`'s --board choices)"
affects: [127-02, 127-03, 127-04, 127-05, 127-06, 127-07, 127-08, 127-09, 127-10, 127-11, 127-12, 128-release-asset-fold]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Real --no-ff merge (not squash) when ROADMAP criteria require a literal parent-SHA ancestry, contrasted explicitly against Phase 124's squash"
    - "Accepted-deviation comments placed at the code site itself (not only in .planning/), so a reader learns the rationale without opening the planning record"

key-files:
  created: []
  modified:
    - firestarter_app/firestarter/firmware.py (D-17 comment only; asset_candidates() byte-identical)
    - firestarter_app/firestarter/py32_dfu.py (via merge)
    - firestarter_app/firestarter/channel.py (via merge)
    - firestarter_app/firestarter/cli_handlers.py (via merge)
    - firestarter_app/tests/test_py32_dfu.py (via merge)
    - firestarter_app/pyproject.toml (via merge — [py32] extra added, extend-exclude preserved)
    - firestarter_app/doc/PY32F071-FIRMWARE-INSTALL.md (via merge)
    - firestarter_app/CLAUDE.md (via merge)

key-decisions:
  - "Merged with `git merge --no-ff 4ee64a1` rather than squash — ROADMAP Criterion 1 requires 4ee64a1 literally among the merge commit's parent SHAs (D-16, deliberately the opposite of Phase 124 D-05)"
  - "Did not edit tests/test_characterization.py or its snapshot to force test_help_fw green — per plan instruction, a genuine post-merge failure is recorded verbatim as a contradiction of C-1, not silently absorbed"
  - "D-17 comment placed as a comment block (not a docstring change) immediately above flash_method(), in its own commit separate from the merge, so it is independently reviewable"

requirements-completed: []  # HOST-01 intentionally left unticked — only Plan 127-12 may tick HOST-01..HOST-08 (Phase-116 4x premature-tick guard)

coverage:
  - id: D1
    description: "feature/py32f071-fw-install @ 4ee64a1 landed as a real merge commit with 4ee64a1 as a literal parent"
    verification:
      - kind: other
        ref: "git log -1 --format=%P (63ce44e) -> ccbc401e16e2d2298f7376c3086164700bba0278 4ee64a14a8933b60896c8b168bb1c7e34d788fa4"
        status: pass
    human_judgment: false
  - id: D2
    description: "Merged tree passes all CI gates except one pre-existing snapshot test destabilized by the new py32f071 board choice"
    verification:
      - kind: unit
        ref: "pytest tests/ --cov=firestarter --cov-fail-under=70 -> 1215 passed, 1 failed (test_characterization.py::test_help_fw), 81.35% coverage"
        status: fail
    human_judgment: true
    rationale: "A genuine, reproducible contradiction of C-1's 'zero fixups' measurement. Plan explicitly forbids editing the test/snapshot to force green; a human/later-plan decision is needed on whether to regenerate the snapshot."
  - id: D3
    description: "D-17 accepted-deviation comment recorded at flash_method(), comment-only, asset_candidates() untouched"
    verification:
      - kind: unit
        ref: "ruff check firestarter/ tests/ && ruff format --check firestarter/ tests/ && pytest tests/test_firmware_install.py tests/test_py32_dfu.py -q -> 104 passed"
        status: pass
    human_judgment: false

# Metrics
duration: 20min
completed: 2026-08-01
status: complete
---

# Phase 127 Plan 01: Land the Host DFU Installer Merge Summary

**Landed `feature/py32f071-fw-install` @ `4ee64a1` onto `v1.23-py32f071-integration` as a real `--no-ff` merge commit, and recorded HOST-01's accepted deviation at `flash_method()` — but the merged tree is 1215/1216 green, not 1216/1216: one pre-existing CLI-help snapshot test genuinely regresses and C-1's zero-fixup prediction is measurably contradicted.**

## Performance

- **Duration:** ~20 min
- **Started:** 2026-08-01T11:13Z (approx, per STATE.md phase-start timestamp)
- **Completed:** 2026-08-01T11:29Z
- **Tasks:** 2/2 executed
- **Files modified:** 8 (merge) + 1 (D-17 comment)

## Accomplishments

- Pinned the pre-merge baseline in `/workspaces/firestarter_app` on `v1.23-py32f071-integration` at `ccbc401e16e2d2298f7376c3086164700bba0278`: 1158 collected, 5 pre-existing porcelain lines (` M .gitignore`, `?? .coverage`, `?? .planning/config.json`, `?? SECURITY.md`, `?? write_test_port.sh`), sibling layout confirmed (`firestarter_app` basename, `../firestarter/.git` present), no `/dev/ttyACM*`/`/dev/ttyUSB*` attached, and `/workspaces/firestarter` clean.
- Performed `git merge --no-ff 4ee64a14a8933b60896c8b168bb1c7e34d788fa4`, landing as commit `63ce44e`. Diffstat matches exactly: 8 files, +2125/-33. `git log -1 --format=%P` prints two parents, the second literally `4ee64a14a8933b60896c8b168bb1c7e34d788fa4` — satisfying ROADMAP Criterion 1.
- Verified the four headline files at their exact predicted line counts: `firestarter/py32_dfu.py` 832, `firestarter/channel.py` 81, `tests/test_py32_dfu.py` 654, `doc/PY32F071-FIRMWARE-INSTALL.md` 273.
- Confirmed `pyproject.toml` retains `[tool.ruff] extend-exclude = ["tests/golden", "tests/fixtures"]` and the branch's original `pyusb>=1.2.1` pin (Plan 127-02 raises it later — not touched here).
- Post-merge collected count is exactly **1216** as predicted.
- Ran all eight `ci.yml` gate commands locally: catalog validity ✓, `messages.py` codegen drift + `git diff --exit-code` ✓, vector catalog validity ✓, `frame_vectors.py` codegen drift + `git diff --exit-code` ✓, `ruff check firestarter/ tests/` ✓, `ruff format --check firestarter/ tests/` ✓, `python tools/check_mypy_watermark.py` → 1 error against watermark 35 (matches expectation) ✓, `pip install -e . && firestarter --help` ✓.
- Coverage measured at **81.35%**, exactly matching research's C-1 figure, well above the 70% floor.
- Added the D-17 accepted-deviation comment block immediately above `flash_method()` in `firestarter/firmware.py`, naming `accepted deviation`, `D-17`, `HOST-01`, `_install_with_avrdude`, and `avrdude-mcu-detection-fallback`, pointing at `127-NONREGRESSION.md`. Committed separately (`6c621b4`) from the merge. `asset_candidates()` body confirmed byte-identical; diff is comment-only.
- `/workspaces/firestarter` (firmware repo) `git status --porcelain` unchanged throughout — nothing written there.
- No requirement checkbox in `.planning/REQUIREMENTS.md` was ticked (verified: HOST-01..HOST-08 all still `[ ]` Pending).

## Task Commits

1. **Task 1: Pin the pre-merge baseline, then land 4ee64a1 as a real merge commit** — `63ce44e` (merge)
2. **Task 2: Record D-17's accepted deviation at flash_method() in a commit of its own** — `6c621b4` (docs)

**Meta-repo tracking commit:** pending (this SUMMARY + gitlink bump, committed next per `<final_commit>`)

## Files Created/Modified

- `firestarter_app/firestarter/py32_dfu.py` — pure-Python DFU 1.1 + DfuSe client over pyusb (landed via merge)
- `firestarter_app/firestarter/channel.py` — beta-only board gating (`BETA_ONLY_BOARDS`, `is_board_available`) (landed via merge)
- `firestarter_app/firestarter/cli_handlers.py` — `--usb-id`/`--dfu-probe` options, `py32f071` added to `_ALL_BOARDS` (landed via merge)
- `firestarter_app/firestarter/firmware.py` — `flash_method()` router + D-17 comment (comment added this plan, router landed via merge)
- `firestarter_app/tests/test_py32_dfu.py` — 58 new tests (landed via merge)
- `firestarter_app/pyproject.toml` — `[py32]` extra added at `pyusb>=1.2.1` (landed via merge; not raised here)
- `firestarter_app/doc/PY32F071-FIRMWARE-INSTALL.md` — new doc (landed via merge)
- `firestarter_app/CLAUDE.md` — landed via merge (minor addition)

## Decisions Made

- Used a real `--no-ff` merge, never squash/rebase, per D-16 — the opposite of Phase 124's squash, because this phase's ROADMAP Criterion 1 requires `4ee64a1` literally among the merge commit's parents.
- Did **not** edit `tests/test_characterization.py` or its snapshot to force `test_help_fw` green. The plan's explicit instruction ("record the verbatim failure and stop — do not edit a test") takes precedence over the general auto-fix deviation rules for this specific, plan-scoped prohibition.
- D-17 comment is a plain comment block (not a docstring edit) so `flash_method()`'s existing one-line docstring is untouched, and it lives in its own commit for independent review.

## Deviations from Plan

### Genuine, Recorded (NOT Auto-Fixed) — C-1 Contradicted

**1. `tests/test_characterization.py::test_help_fw` fails post-merge**
- **Found during:** Task 1 verification (`python3 -m pytest -q --no-cov -o addopts=`)
- **Issue:** The merge adds `"py32f071"` to `firestarter/cli_handlers.py`'s `_ALL_BOARDS` tuple. Because `firestarter/__init__.py`'s `__version__` is the hardcoded literal `"3.0.0b14"` (a PEP 440 pre-release), `channel.is_prerelease_build()` returns `True` in this checkout regardless of how the package is pip-installed, so `_BOARD_CHOICES` includes `py32f071` and `fw --help`'s rendered `-b, --board` choice list now reads `[uno|uno328pb|leonardo|py32f071]`. The pre-existing snapshot fixture (`tests/__snapshots__/test_characterization.ambr`, last touched in Phase 120, not touched by this merge) still reads `[uno|uno328pb|leonardo]`, so the snapshot assertion fails.
- **Verbatim result:** `pytest tests/ --cov=firestarter --cov-report=term-missing --cov-fail-under=70` → **1215 passed, 1 failed** (`FAILED tests/test_characterization.py::test_help_fw`), coverage `81.35%` (coverage floor passes; the pytest exit code is nonetheless 1 because of the failing test, which means the real `ci.yml` "Run pytest with coverage" step would go **red**, not green).
- **Why not fixed:** The plan states explicitly, twice: "If anything is red, record the verbatim failure and stop — do not edit a test, do not author a speculative fixup," and lists as a success criterion "C-1's zero-fixup prediction is confirmed or contradicted on the record — never quietly absorbed." This is exactly that case. Regenerating the snapshot would be editing a test to make the merge pass, which the plan prohibits outright, even though the change is plausibly a legitimate reflection of new CLI surface.
- **Confirmed merge-induced, not pre-existing:** `py32f071` cannot appear in `_ALL_BOARDS` before this merge (the tuple is part of the merge's `cli_handlers.py` diff), so this test necessarily passed pre-merge and fails only post-merge.
- **Verification the rest of C-1 held:** collected count (1216), coverage (81.35%), `extend-exclude` preservation, and all diffstat/line-count figures all matched the research prediction exactly. Only the "0 failed, all eight ci.yml gates green" portion of C-1 is contradicted.
- **Not fixed. Carried forward as an open finding** — see "Next Phase Readiness" below.

---

**Total deviations:** 1 genuine (recorded, not fixed) — contradicts C-1's zero-fixup prediction on the specific claim that the merged tree is 1216/1216 green with all eight `ci.yml` gates passing.
**Impact on plan:** The merge itself, D-17 comment, `asset_candidates()` byte-identity, firmware-repo isolation, and requirement-ticking guard are all satisfied exactly as planned. The one open item is a real CI-gate-red finding that needs a decision (regenerate the snapshot vs. some other resolution) in a later plan or by the operator — it does not block Task 2 or this plan's other deliverables, none of which depend on `tests/test_characterization.py`.

## Issues Encountered

None beyond the C-1 contradiction documented above.

## User Setup Required

None — no external service configuration required.

## Claim Ceiling

This plan proves the py32 DFU host code (`py32_dfu.py`, `channel.py`, the 58 new tests, the doc) is on the milestone branch and that 1215 of 1216 tests pass with 81.35% coverage. It proves **nothing** about a PY32F071 board: no PCB exists, no install has run against silicon, and HOST-03's readback proof (landed via the merge) is asserted against a mock only. No sentence in this SUMMARY should be read as claiming the install works end to end.

## Next Phase Readiness

- Every later plan in Phase 127 that reads or edits a file under `firestarter/py32_dfu.py`, `channel.py`, or `firmware.py` is now unblocked — those files exist on the branch.
- **Open finding to resolve, not yet assigned to a specific plan:** `tests/test_characterization.py::test_help_fw`'s snapshot needs a decision — regenerate it to include `py32f071` in the `fw --help` board-choice list (the behaviorally correct outcome, since the board is real and gated by channel, not by help text), or some other resolution. This is a real CI-gate-red item on the milestone branch right now and should be triaged before Phase 127 closes (127-12) or before any `git push`/CI dispatch (127-11).
- `firestarter/firmware.py`'s `asset_candidates()` is confirmed untouched — Phase 128's Criterion 4 dependency is intact.

## Self-Check: PASSED
