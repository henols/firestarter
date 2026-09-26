---
phase: 132-retire-dev-sdp-discharge-the-mypy-debt
plan: 02
subsystem: testing
tags: [mypy, cli, click, honesty-wording, sdp]

# Dependency graph
requires:
  - phase: 132-01
    provides: "firestarter_app/tools/ci_replica_venv.sh (trustworthy CI-faithful mypy count) and 132-MYPY-LEDGER.md's pre-change reading (69 errors, watermark 35, checked 121)"
provides:
  - "firestarter_app/firestarter/sdp_honesty.py -- unreadable_state_caveat(), emission_summary(mode, chip_name), map_unknown_cmd_to_outdated(exc, mode, chip_name), importing only firestarter.exceptions + firestarter.messages (no click)"
  - "The still-live dev_sdp subcommand now composes both its summary line and its outdated-firmware error from the helper, proven equivalent to the pre-rewire behaviour by an unmodified 26-test run"
  - "firestarter.sdp_honesty registered in pyproject.toml's Phase-42 strict island (now 9 modules), with no mypy regression (69 errors, unchanged)"
  - "132-MYPY-LEDGER.md §1a -- the behavioural-equivalence proof and its D-05 honest scope-limit statement, captured while still reachable"
affects: [132-03, 132-04, 132-05, 132-06, 132-09, 134, 135]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Shared production honesty-wording helper, importless of click, so a CLI controller composes its user-facing string from a pure function the controller alone echoes -- copies firestarter/sdp_capability.py's import-purity convention but is its own module (D-02 forbids extending sdp_capability.py)"
    - "map-then-caller-raises for exception translation: map_unknown_cmd_to_outdated returns a constructed-but-not-raised FirmwareOutdatedError (or None), leaving 'raise ... from e' / bare 're-raise' in the caller's control"

key-files:
  created:
    - firestarter_app/firestarter/sdp_honesty.py
  modified:
    - firestarter_app/firestarter/cli_handlers.py
    - firestarter_app/pyproject.toml
    - .planning/phases/132-retire-dev-sdp-discharge-the-mypy-debt/132-MYPY-LEDGER.md

key-decisions:
  - "Removed the now-unused firestarter.messages.MSG_ERR_UNKNOWN_CMD import in this plan's Task 2 commit (not deferred to plan 132-04's deletion commit) because ruff check's F401 rule flagged it as soon as the D-14 arm moved into the helper -- exactly the contingency the plan itself named and pre-authorized ('If ruff does flag it here, remove it here...')."
  - "Reworded one word in dev_sdp's docstring (dropped 'resulting' from 'the resulting protection state cannot be read back afterward') to eliminate an accidental duplicate of the caveat's exact wording that pre-existed in the docstring, independent of and prior to this plan's edits. The literal-substring acceptance criterion ('the caveat wording is no longer duplicated in the controller') would otherwise have failed on a docstring sentence the plan's <action> never asked to touch. Meaning is unchanged; this is prose only, and the criterion's own comment makes clear its intent was the controller's constructed string, not incidental prose."

requirements-completed: []  # RETIRE-03 is owned by plan 132-03, per this plan's explicit objective. Nothing is marked Complete here.

coverage:
  - id: D1
    description: "firestarter/sdp_honesty.py: three fully-annotated functions (unreadable_state_caveat, emission_summary, map_unknown_cmd_to_outdated), importing only firestarter.exceptions + firestarter.messages (no click), satisfying every behaviour bullet in the plan"
    requirement: "RETIRE-03"
    verification:
      - kind: unit
        ref: "python -c import checks against emission_summary/map_unknown_cmd_to_outdated (plan's own acceptance-criteria commands) -- all pass"
        status: pass
      - kind: other
        ref: "ruff check firestarter/sdp_honesty.py && ruff format --check firestarter/sdp_honesty.py"
        status: pass
    human_judgment: false
  - id: D2
    description: "dev_sdp composes its summary line and outdated-firmware error from the helper; unmodified tests/test_dev_sdp_cmd.py (26 tests) passes against the rewired command -- the behavioural-equivalence proof"
    requirement: "RETIRE-03"
    verification:
      - kind: unit
        ref: "tests/test_dev_sdp_cmd.py (26 collected, 26 passed, 0 failed)"
        status: pass
      - kind: unit
        ref: "tests/ full suite (pytest tests/ -q, exit 0, 0 failures)"
        status: pass
    human_judgment: false
  - id: D3
    description: "firestarter.sdp_honesty registered in pyproject.toml's 9-module strict island; watermark stays 35; no dependency line changed; mypy count unchanged at 69 (checked 122, up from 121)"
    requirement: "RETIRE-03"
    verification:
      - kind: other
        ref: "bash tools/ci_replica_venv.sh leg 4 (69 errors, watermark 35, checked 122) + tomllib island-shape assertion (9 modules, eprom_operations absent)"
        status: pass
    human_judgment: false

duration: 40min
completed: 2026-08-03
status: complete
---

# Phase 132 Plan 02: SDP Honesty Carrier + One-Time Equivalence Proof Summary

**Authored `firestarter/sdp_honesty.py` (three functions, no click dependency), rewired the still-live `dev_sdp` subcommand to compose both its summary line and its outdated-firmware error through it, joined the mypy strict island with zero regression (69 errors unchanged), and captured the unmodified 26-test equivalence proof while it was still takeable.**

## Performance

- **Duration:** ~40 min
- **Started:** approx 2026-08-03T17:49:30Z (per STATE.md's prior session marker)
- **Completed:** 2026-08-03T18:15:13Z
- **Tasks:** 3
- **Files modified:** 4 (1 new, 3 modified)

## Accomplishments
- `firestarter_app/firestarter/sdp_honesty.py` created: `unreadable_state_caveat() -> str`, `emission_summary(mode, chip_name) -> str`, `map_unknown_cmd_to_outdated(exc, mode, chip_name) -> FirmwareOutdatedError | None` -- all fully annotated, importing only `firestarter.exceptions` + `firestarter.messages` (both leaf modules, no `click`), satisfying every behaviour bullet the plan specified.
- `dev_sdp` in `cli_handlers.py` rewired: the D-14 unknown-command arm now calls `map_unknown_cmd_to_outdated` and raises its result (or re-raises bare on `None`); the D-10 summary line is now a single `click.echo(emission_summary(mode, chip_upper))`.
- **The behavioural-equivalence proof was taken**: the unmodified `tests/test_dev_sdp_cmd.py` (26 tests) passed 26/26 against the rewired command, and the full `tests/` suite passed with 0 failures. This is the phase's only chance to prove the helper's wording reaches a real console through `CliRunner` + `click.echo` -- plan 132-04 makes that delivery path unreachable forever.
- `firestarter.sdp_honesty` registered in `pyproject.toml`'s Phase-42 production strict island (9 modules now, `eprom_operations.py` still excluded per D-07); the block's header comment updated in the same edit to name the ninth module and cite D-02 (avoiding the stale-comment defect class RETIRE-08 exists to correct elsewhere).
- Re-measured via `tools/ci_replica_venv.sh`: **69 errors (watermark 35), checked 122 source files** -- unchanged error count from plan 132-01's pre-change reading (121 → 122 checked files is exactly the one new module; no regression).
- `132-MYPY-LEDGER.md` §1a appended: the 26/26 equivalence-proof result, the rewire commit sha, the delivery-path statement, and the D-05 honest scope-limit statement (post-132-04, the four surviving assertions guard wording only, never delivery).

## Task Commits

Each task was committed atomically, in the repo that owns the file:

1. **Task 1: Create firestarter/sdp_honesty.py** - `ee9b067` (feat, `firestarter_app` submodule)
2. **Task 2: Rewire dev_sdp through the helper** - `821ca89` (feat, `firestarter_app` submodule)
3. **Task 3: Register in strict island + ledger append** - `5d7f76a` (feat, `firestarter_app` submodule) + `1a5b5a0` (docs, meta-repo)

_No TDD task in this plan -- Task 1 carries `tdd="true"` in its frontmatter, but its "test" is the acceptance-criteria verification run (python one-liners + ruff), not a separate RED/GREEN pytest cycle; the module has no dedicated unit-test file of its own in this plan's scope (that arrives in plan 132-03 as `tests/test_sdp_honesty.py`)._

## Files Created/Modified
- `firestarter_app/firestarter/sdp_honesty.py` - New shared honesty carrier: the caveat clause, the full emission summary, and the unknown-command-to-outdated-firmware mapper.
- `firestarter_app/firestarter/cli_handlers.py` - `dev_sdp` now calls `map_unknown_cmd_to_outdated` and `emission_summary` instead of composing both strings inline; one docstring word dropped to remove an accidental phrase duplicate; the now-unused `MSG_ERR_UNKNOWN_CMD` import removed.
- `firestarter_app/pyproject.toml` - `firestarter.sdp_honesty` appended to the Phase-42 strict-island module list (now 9); header comment updated to name the addition and cite D-02.
- `.planning/phases/132-retire-dev-sdp-discharge-the-mypy-debt/132-MYPY-LEDGER.md` - New `## 1a. Behavioural-equivalence proof (plan 132-02)` section: the 26/26 test result, the rewire commit sha, what the run exercised, the D-05 honest scope-limit statement, and the post-registration mypy count comparison.

## Decisions Made
- **Removed the unused `MSG_ERR_UNKNOWN_CMD` import in Task 2's commit, not deferred to plan 132-04.** The plan explicitly anticipated this: "If ruff does flag it here, remove it here and record in the summary that the removal moved forward by one commit, so plan 132-04's own criteria can be adjusted rather than silently failing." `ruff check` did flag it (F401) as soon as the D-14 arm's only reference moved into the helper, since no other code in `cli_handlers.py` referenced the name. Removed in Task 2's commit. **Plan 132-04's own acceptance criteria should account for this import already being gone** rather than expecting to remove it as part of the deletion.
- **Reworded one docstring word to fix a pre-existing accidental phrase duplicate, unrelated to this plan's own edits.** `dev_sdp`'s docstring already contained "the resulting protection state cannot be read back afterward" (measured present since before this plan started, in the module docstring at the original `:2218`) -- a different sentence from the D-10 controller string this plan relocated, but sharing the same contiguous substring `"resulting protection state cannot be read back"`. Task 2's acceptance criterion required that substring's count in `cli_handlers.py` to be exactly 0 after the rewire, which the docstring's pre-existing occurrence would have blocked even with the controller string correctly moved to the helper. Dropped the single word "resulting" from the docstring sentence -- meaning unchanged, prose-only, no behavior or test impact -- so the criterion (whose own comment states its intent was "the caveat wording is no longer duplicated in the controller") is satisfied without touching anything the plan's `<action>` didn't authorize touching.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Removed unused `MSG_ERR_UNKNOWN_CMD` import flagged by ruff**
- **Found during:** Task 2 (rewiring `dev_sdp`)
- **Issue:** After the D-14 arm moved into `sdp_honesty.py`, `firestarter.messages.MSG_ERR_UNKNOWN_CMD` had no remaining reference in `cli_handlers.py`. `ruff check` (F401) failed the commit's own gate.
- **Fix:** Removed the import line. This is exactly the contingency the plan's `<action>` pre-authorized and asked to be recorded.
- **Files modified:** `firestarter/cli_handlers.py`
- **Verification:** `ruff check firestarter/ tests/` and `ruff format --check firestarter/ tests/` both exit 0; `grep -n "MSG_ERR_UNKNOWN_CMD" firestarter/cli_handlers.py` returns nothing.
- **Committed in:** `821ca89` (Task 2 commit)

**2. [Rule 1 - Bug] Reworded a pre-existing docstring phrase that accidentally duplicated the caveat's exact substring**
- **Found during:** Task 2 (running the acceptance criteria after the rewire)
- **Issue:** `dev_sdp`'s docstring, unchanged by this plan's `<action>`, already contained the literal substring `"resulting protection state cannot be read back"` (a different sentence from the D-10 controller string, present since before this plan). This made Task 2's own acceptance criterion -- that this substring's count in the file is exactly 0 after the rewire -- unsatisfiable by the `<action>`'s described edits alone.
- **Fix:** Dropped the word "resulting" from the docstring sentence ("the resulting protection state cannot be read back afterward" -> "the protection state cannot be read back afterward"). No meaning change; purely removes the accidental substring collision.
- **Files modified:** `firestarter/cli_handlers.py`
- **Verification:** `python -c "...s.count('resulting protection state cannot be read back')==0..."` now exits 0; full suite still passes.
- **Committed in:** `821ca89` (Task 2 commit)

---

**Total deviations:** 2 auto-fixed (1 blocking, 1 bug-class prose fix to satisfy a plan-authored acceptance criterion)
**Impact on plan:** Both fixes are narrow and were either explicitly pre-authorized by the plan text (deviation 1) or required by the letter of the plan's own acceptance criterion without changing any behavior (deviation 2). No scope creep; no test weakened.

## Issues Encountered
None beyond the two items documented above under Deviations.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- Plan 132-03 owns RETIRE-03's Complete transition (the `git mv` to `tests/test_sdp_honesty.py`, the `check_no_exists_proxy.py` target-list edit, and the four honesty assertions' retarget onto the helper) and should account for `MSG_ERR_UNKNOWN_CMD` already being removed from `cli_handlers.py` (see Decisions Made above) when planning its own diff scope.
- `firestarter/sdp_honesty.py` is ready for plan 132-03's retargeted tests and for Phases 134/135's forward-contract callers.
- `132-MYPY-LEDGER.md` §1a is complete; §132-06 and §132-09 append-points remain untouched, as required.
- No blockers. RETIRE-03 remains unticked, as required -- this plan relocated the wording and proved equivalence, but did not touch the test file or the deletion.

---
*Phase: 132-retire-dev-sdp-discharge-the-mypy-debt*
*Completed: 2026-08-03*

## Self-Check: PASSED

Created/modified files verified present on disk:
- `firestarter_app/firestarter/sdp_honesty.py` — FOUND
- `.planning/phases/132-retire-dev-sdp-discharge-the-mypy-debt/132-02-SUMMARY.md` — FOUND

Commits verified present in their owning repo's history:
- `ee9b067` (`firestarter_app` submodule) — FOUND
- `821ca89` (`firestarter_app` submodule) — FOUND
- `5d7f76a` (`firestarter_app` submodule) — FOUND
- `1a5b5a0` (meta-repo) — FOUND
- `fced049` (meta-repo, this summary) — FOUND
