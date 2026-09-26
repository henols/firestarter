---
phase: 132-retire-dev-sdp-discharge-the-mypy-debt
plan: 08
subsystem: cli
tags: [sdp, retirement, dereference-test, stale-anchor, d-11, d-12, mypy]

# Dependency graph
requires:
  - phase: 132-07
    provides: "measured mypy baseline of 32 (checked 122 source files, watermark 35), and constants.py's FLAG_SKIP_SDP_UNLOCK block (:112-131) left undisturbed so this plan's stale-anchor block near :66-73 stayed untouched territory"
provides:
  - "test_command_names_dereferences_both_sdp_commands in tests/test_revision_constants_parity.py -- an unconditional (no requires_fw skip) dereference test proving both COMMAND_SDP_UNLOCK and COMMAND_SDP_LOCK still resolve through COMMAND_NAMES, proven non-vacuous by two separate RED demonstrations (one per entry removed)"
  - "All five stale eprom_operations.py:301/:377 COMMAND_NAMES dereference citations corrected to name _setup_operation (:329) and _operation_context (:405) first, with the line number alongside (D-11) -- one in firestarter/constants.py, four in tests/test_revision_constants_parity.py"
  - "RETIRE-04 and RETIRE-08 marked Complete in REQUIREMENTS.md, with RETIRE-08's own text corrected from the wrong count of three to the measured five, across two files, enumerated (D-12)"
  - "The D-12 cross-repository 'same commit' binding honoured as adjacent, cross-citing commits with the impossibility stated explicitly, rather than silently worked around"
affects: [132-09]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Unconditional dereference test as the antidote to a requires_fw-skipped gate: test_missing_command_names_entry_is_detected (pre-existing) proves the same fact but only when the firmware checkout is present; the new test proves it in every CI run including host-only, by dereferencing the mapping directly rather than parsing a firmware header"
    - "Two-plant, two-revert RED demonstration for a two-key dereference test: proving a test that asserts on both of two keys actually depends on both requires removing each key independently and observing a distinct failure naming that key, not just removing one and calling it proven"
    - "Function-name-first stale-anchor correction (D-11): every corrected citation states the dereferencing function's name before its line number, so a future insertion that re-staples the line number still leaves the anchor legible by name"

key-files:
  created: []
  modified:
    - firestarter_app/tests/test_revision_constants_parity.py
    - firestarter_app/firestarter/constants.py
    - .planning/REQUIREMENTS.md

key-decisions:
  - "The new dereference test was placed immediately after the pre-existing test_missing_command_names_entry_is_detected (both SDP-related, both dereference-shaped), not appended at the file's end -- matching the plan's own placement instruction and keeping the module's two dereference-proving tests adjacent for a future reader."
  - "The dereference test asserts entry PRESENCE ('constant in COMMAND_NAMES') before entry VALUE ('COMMAND_NAMES[constant]'), each with its own descriptive failure message. A bare dict-index lookup on a dropped key would raise a raw KeyError with no custom message and no stated setup consequence -- failing this plan's own acceptance bar that failure text name the missing constant and the setup consequence. The membership check first is what makes the RED demonstrations' failure text legible rather than a traceback."
  - "D-12's 'same commit' requirement is honoured as adjacent cross-repository commits, each naming the other, with the impossibility stated plainly in both commit messages and here -- not silently worked around, and not claimed as met. Task 2's submodule commit (42a1971) could not cite task 3's meta-repo commit's SHA at authorship time (it did not exist yet), so it names the file and requirement task 3 closes instead; task 3's commit (88a521e) names 42a1971 (and 831c95f for task 1) by SHA, closing the loop from the other side."
  - "REQUIREMENTS.md's evidence lines for RETIRE-04 and RETIRE-08 cite commit SHAs directly rather than plan numbers alone, consistent with this file's existing evidence convention for other RETIRE/GATE rows (e.g. RETIRE-07's citation of 5ec3a89/1fdb455/cc5d223)."

requirements-completed: [RETIRE-04, RETIRE-08]

coverage:
  - id: D1
    description: "The dereference test dereferences both COMMAND_SDP_UNLOCK and COMMAND_SDP_LOCK through COMMAND_NAMES, unconditionally, and asserts both constants' integer values so a removed constant also fails the test."
    verification:
      - kind: unit
        ref: "grep -c 'def test_command_names_dereferences_both_sdp_commands' tests/test_revision_constants_parity.py -- 1; python -m pytest tests/test_revision_constants_parity.py::test_command_names_dereferences_both_sdp_commands -q -- 1 passed"
        status: pass
      - kind: unit
        ref: "grep -c COMMAND_SDP_UNLOCK tests/test_revision_constants_parity.py -- 9 (>= 2 required); grep -c COMMAND_SDP_LOCK -- 8 (>= 2 required); grep -c _setup_operation -- 9 (>= 1); grep -c _operation_context -- 9 (>= 1)"
        status: pass
    human_judgment: false
  - id: D2
    description: "The test is proven a real gate, not an unreachable green, by two separate RED demonstrations -- one per entry removed -- each recorded verbatim with a failure message naming the missing constant and the operation-setup consequence."
    verification:
      - kind: integration
        ref: "Removed COMMAND_NAMES[COMMAND_SDP_UNLOCK] -> test failed naming COMMAND_SDP_UNLOCK and the setup consequence (verbatim below). Restored, removed COMMAND_NAMES[COMMAND_SDP_LOCK] -> test failed naming COMMAND_SDP_LOCK instead (verbatim below), proving both keys are load-bearing to the test, not one. Reverted; git status --porcelain showed only this plan's own modified files plus pre-existing tree dirt."
        status: pass
    human_judgment: false
  - id: D3
    description: "All five stale eprom_operations.py:301/:377 citations (one in constants.py, four in test_revision_constants_parity.py) are corrected to name _setup_operation (:329) and _operation_context (:405) first, with the number alongside; the load-bearing 'not a cosmetic display gap' reasoning survives; the ring-fenced eprom_operations.py's diff stays empty; plan 132-07's D-14 note survives."
    verification:
      - kind: unit
        ref: "grep -rn 'eprom_operations.py:301' . -- 0 hits; grep -rn ':377' --include='*.py' . -- 0 hits; grep -c 329 firestarter/constants.py -- 1, grep -c 405 -- 1; grep -c 329 tests/test_revision_constants_parity.py -- 9, grep -c 405 -- 9 (>= 4 required in each file); grep -c _setup_operation firestarter/constants.py -- 1, in test file -- 9 (>= 4 required); grep -ci 'not a cosmetic' constants.py -- 1; grep -c test_command_names_dereferences_both_sdp_commands constants.py -- 1; grep -c D-14 constants.py -- 1 (132-07's note undisturbed)"
        status: pass
      - kind: unit
        ref: "git diff --stat firestarter/eprom_operations.py -- empty (both after task 1 and after task 2)"
        status: pass
    human_judgment: false
  - id: D4
    description: "Full suite stays green, ruff stays clean, and the mypy count holds at no higher than plan 132-06's recorded 32 after both submodule tasks."
    verification:
      - kind: unit
        ref: "python -m pytest tests/ -q -- 1297 passed, 30 snapshots passed (after task 1: same; after task 2: same); ruff check firestarter/ tests/ and ruff format --check firestarter/ tests/ -- both exit 0 after each task"
        status: pass
      - kind: integration
        ref: "bash tools/ci_replica_venv.sh -- all 5 legs PASS; Leg 4: 'Found 32 errors in 12 files (checked 122 source files)', 'mypy errors: 32 (watermark: 35)' -- unchanged from plan 132-07/132-06"
        status: pass
    human_judgment: false
  - id: D5
    description: "RETIRE-08's own text is corrected in-phase with the measured evidence clause (five references, two files, enumerated, function-name-first), rather than ticked while known wrong; RETIRE-04 and RETIRE-08 are the only checkboxes that moved; the Evidence Ceiling and the FUT-MYPY-02 out-of-scope row are untouched; D-12's cross-repository 'same commit' impossibility is stated explicitly rather than silently worked around."
    verification:
      - kind: unit
        ref: "grep -c 'three in-tree stale' REQUIREMENTS.md -- 0; grep -A4 RETIRE-08 REQUIREMENTS.md shows 'five', '329', '405'; grep -A6 shows _setup_operation and _operation_context; git diff -- REQUIREMENTS.md | grep -cE '^\\+.*\\[x\\].*\\*\\*RETIRE-(04|08)\\*\\*' -- 2; same for RETIRE-06 -- 0; Evidence Ceiling lines removed -- 0; FUT-MYPY-02 row lines removed -- 0; git log -1 --name-only lists only .planning/REQUIREMENTS.md"
        status: pass
    human_judgment: false

duration: ~55min
completed: 2026-08-03
status: complete
---

# Phase 132 Plan 08: The Dereference Test and the Five-Not-Three Correction (RETIRE-04, RETIRE-08) Summary

**Added an unconditional dereference test proving both SDP command-name entries still resolve at operation setup, corrected all five stale `eprom_operations.py:301`/`:377` citations across two files to name the two dereferencing functions with their true line numbers alongside, and corrected RETIRE-08's own requirement text from a wrong count of three to the measured five — honouring D-12's impossible "same commit" binding as adjacent, cross-citing commits between the submodule and the meta-repo instead of silently working around it.**

## Performance

- **Duration:** ~55 min
- **Started:** 2026-08-03 (STATE.md's prior session marker, 132-07 complete)
- **Completed:** 2026-08-03
- **Tasks:** 3
- **Files modified:** 3 (`test_revision_constants_parity.py`, `constants.py`, `REQUIREMENTS.md`)

## Accomplishments

- **Task 1 (RETIRE-04):** Added `test_command_names_dereferences_both_sdp_commands` to `tests/test_revision_constants_parity.py`, placed immediately after the pre-existing `test_missing_command_names_entry_is_detected` (both SDP-dereference-shaped, both belong together). Unlike that pre-existing test, the new one carries **no `requires_fw` skip** — it dereferences `constants.COMMAND_NAMES` directly with both `COMMAND_SDP_UNLOCK` and `COMMAND_SDP_LOCK`, so it runs in every CI configuration including host-only CI, where the firmware checkout (and therefore the header-parsing gate) is absent. Asserts both constants' integer values first (so a removed constant, not just a removed entry, also fails), then asserts entry presence with a message naming the missing constant and the setup consequence, then asserts the mapped value is non-empty. Committed as `831c95f`.
  - **RED demonstration 1** (`COMMAND_SDP_UNLOCK` entry removed from `COMMAND_NAMES`):
    ```
    E       AssertionError: COMMAND_NAMES has no entry for COMMAND_SDP_UNLOCK (9) -- _setup_operation (eprom_operations.py:329) and _operation_context (eprom_operations.py:405) both dereference COMMAND_NAMES[cmd] at operation setup, so a dropped entry is a KeyError there, not a cosmetic display gap.
    E       assert 9 in {1: 'READ', 2: 'WRITE', 3: 'ERASE', 4: 'BLANK_CHECK', ...}
    E        +  where 9 = constants.COMMAND_SDP_UNLOCK
    E        +  and   {1: 'READ', 2: 'WRITE', 3: 'ERASE', 4: 'BLANK_CHECK', ...} = constants.COMMAND_NAMES
    ```
  - **RED demonstration 2** (entry restored, then `COMMAND_SDP_LOCK` entry removed instead) — a *different* failure naming the *other* constant, proving the test depends on both keys rather than passing on the strength of one:
    ```
    E       AssertionError: COMMAND_NAMES has no entry for COMMAND_SDP_LOCK (10) -- _setup_operation (eprom_operations.py:329) and _operation_context (eprom_operations.py:405) both dereference COMMAND_NAMES[cmd] at operation setup, so a dropped entry is a KeyError there, not a cosmetic display gap.
    E       assert 10 in {1: 'READ', 2: 'WRITE', 3: 'ERASE', 4: 'BLANK_CHECK', ...}
    E        +  where 10 = constants.COMMAND_SDP_LOCK
    E        +  and   {1: 'READ', 2: 'WRITE', 3: 'ERASE', 4: 'BLANK_CHECK', ...} = constants.COMMAND_NAMES
    ```
  - Reverted both plants via `git checkout -- firestarter/constants.py`; confirmed the test passes again and `git status --porcelain` showed only this plan's own modified test file plus the pre-existing tree dirt.
- **Task 2 (RETIRE-08, D-11):** Corrected all five stale references, measured (not the "three" the requirement's own text claimed):
  1. `firestarter/constants.py:69-70` — the two-line comment above `COMMAND_SDP_UNLOCK`/`COMMAND_SDP_LOCK`. Corrected to name `_setup_operation` (`:329`) and `_operation_context` (`:405`), preserved the load-bearing "not a cosmetic display gap" reasoning verbatim, and added a pointer to `test_command_names_dereferences_both_sdp_commands` by name so the two halves cross-reference each other.
  2. `tests/test_revision_constants_parity.py:71-72` — the module-docstring citation near the top (in the D-13 bullet describing `test_every_firmware_cmd_has_a_command_names_entry`).
  3. `tests/test_revision_constants_parity.py:526-532` — the `_check_command_names_coverage` docstring's inline citation.
  4. `tests/test_revision_constants_parity.py:548-553` — the citation **inside an assertion message string** (the `errors.append(...)` f-string in `_check_command_names_coverage`). Correcting this line changes that check's failure text only — it has no effect on pass/fail behaviour, confirmed by the full suite staying green afterward.
  5. `tests/test_revision_constants_parity.py:586-593` — the final citation, in `test_every_firmware_cmd_has_a_command_names_entry`'s own docstring, naming both functions.
  Every corrected site names the function first with the corrected line number alongside (D-11), per this milestone's own receipt that a prior insertion staled 11 of 12 such anchors when only numbers were cited. Verified `git diff --stat firestarter/eprom_operations.py` stayed empty — the ring-fenced module carries zero stale tokens and needed no edit at all — and that plan 132-07's `D-14` flag-block note in `constants.py` (`:112-131`) survived undisturbed. Committed as `42a1971`.
- **Task 3 (RETIRE-08, D-12):** Corrected RETIRE-08's own text in `.planning/REQUIREMENTS.md` (meta-repo) from "The three in-tree stale `301`/`377` `COMMAND_NAMES` comment references are corrected to `329`/`405`" to a text stating the measured evidence clause: **five** stale references across **two files** — one in `constants.py`, four in `test_revision_constants_parity.py` (naming which one sits inside an assertion message) — with both dereferencing function names and their corrected line numbers, and the fact that the ring-fenced `eprom_operations.py` itself carries zero stale tokens. RETIRE-04's own text was also given an evidence clause. Both checkboxes ticked Complete, in both the requirement line and the Traceability table row; no other RETIRE id touched (`RETIRE-06` confirmed still Pending). The Evidence Ceiling and the `FUT-MYPY-02` ring-fence out-of-scope row are byte-unchanged (confirmed by diff greps). Committed as `88a521e`.

## D-12's Impossible "Same Commit" Binding — Stated, Not Worked Around

D-12 requires RETIRE-08's requirement-text correction land "in the same commit as the fixes." The fixes (task 2) are in the `firestarter_app` submodule; the requirement text (task 3) is in the meta-repo. **Two git repositories cannot share a commit — this binding cannot be met as literally worded, and this summary states that plainly rather than claiming it was met.**

Honoured instead as **adjacent, cross-citing commits, same plan, same task sequence**:
- Task 2's commit (`42a1971`, submodule) could not cite task 3's meta-repo commit's SHA at authorship time — that commit did not exist yet — so its message names the target file (`.planning/REQUIREMENTS.md`) and requirement (`RETIRE-08`) task 3 closes the loop with instead.
- Task 3's commit (`88a521e`, meta-repo) names both `42a1971` (task 2's fix commit) and `831c95f` (task 1's test commit) by SHA, closing the loop from the meta-repo side.

D-03's same-commit binding (the `git mv` + `check_no_exists_proxy.py` target-list edit from an earlier plan) is unaffected by this — it was always submodule-only and stays one real commit; only D-12's cross-repository case is structurally impossible.

## Task Commits

Each task was committed atomically, in the repo that owns the file:

1. **Task 1: dereference test (RETIRE-04)** — `831c95f` (test, `firestarter_app` submodule)
2. **Task 2: five stale-reference corrections (RETIRE-08, D-11)** — `42a1971` (fix, `firestarter_app` submodule)
3. **Task 3: RETIRE-08 text correction + checkbox ticks (RETIRE-08/RETIRE-04, D-12)** — `88a521e` (docs, meta-repo)

**Plan metadata:** this summary + STATE.md/ROADMAP.md updates (meta-repo, separate commit per `<final_commit>`).

## Files Created/Modified

- `firestarter_app/tests/test_revision_constants_parity.py` — new test `test_command_names_dereferences_both_sdp_commands` (54 lines, placed after `test_missing_command_names_entry_is_detected`); four stale-reference corrections (module docstring, `_check_command_names_coverage` docstring, its assertion message, and `test_every_firmware_cmd_has_a_command_names_entry`'s docstring).
- `firestarter_app/firestarter/constants.py` — corrected the two-line stale comment above `COMMAND_SDP_UNLOCK`/`COMMAND_SDP_LOCK` to name `_setup_operation`/`_operation_context` with `:329`/`:405`, preserved the load-bearing reasoning verbatim, added a pointer to the new test.
- `.planning/REQUIREMENTS.md` — RETIRE-04 and RETIRE-08 checkboxes and evidence text corrected/added; both Traceability rows moved from Pending to Complete; no other row touched.

## Decisions Made

- **New test placed adjacent to the existing SDP-dereference test**, not appended at file end, per the plan's own instruction and to keep the module's two dereference-proving tests together for a future reader.
- **Entry-presence asserted before entry-value**, each with its own descriptive message — a bare `dict[key]` lookup on a missing key raises an undecorated `KeyError`, which would fail this plan's own bar that the RED demonstration's failure text name the missing constant and the setup consequence.
- **D-12's impossibility stated explicitly** in both task commit messages and this summary, rather than claiming the binding was met, per the plan's own instruction.
- **REQUIREMENTS.md evidence lines cite commit SHAs directly**, matching this file's existing convention (e.g. RETIRE-07's citation of `5ec3a89`/`1fdb455`/`cc5d223`).

## Deviations from Plan

None. The plan's own measured-anchors table (five sites, exact lines) matched what this plan found on re-reading the files live; no re-measurement surprises occurred, and no rule 1/2/3/4 deviation was needed.

## Issues Encountered

None. The full test suite (1297 passed, 30 snapshots), ruff, and `tools/ci_replica_venv.sh`'s five legs (mypy holding at 32, unchanged) all stayed green across both submodule tasks.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- `test_command_names_dereferences_both_sdp_commands` exists, dereferences both SDP command constants unconditionally, and has been proven to fail once per entry removed with a legible failure message each time.
- All five stale `eprom_operations.py:301`/`:377` references are corrected, function-name-first, with the true `:329`/`:405` anchors, across both files that carried them.
- RETIRE-08 reads five, enumerated, with both function names; RETIRE-04 and RETIRE-08 are the only checkboxes that moved.
- `mypy` count holds at **32** (checked 122 source files, watermark 35) — unchanged from plan 132-07/132-06.
- Full suite green: **1297 passed** (1296 + this plan's one new test), 30/30 snapshots passed, coverage 81.72% (floor 70%). `ruff check` + `ruff format --check` both exit 0.
- `git diff --stat firestarter/eprom_operations.py` is empty across both submodule commits — the ring-fence held throughout.
- Plan 132-09 (RETIRE-06, the certifying CI dispatch) can proceed against `firestarter_app` @ `42a1971` and `.planning/REQUIREMENTS.md` @ `88a521e` as they now stand.

---
*Phase: 132-retire-dev-sdp-discharge-the-mypy-debt*
*Completed: 2026-08-03*

## Self-Check: PASSED

Created/modified files verified present on disk:
- `.planning/phases/132-retire-dev-sdp-discharge-the-mypy-debt/132-08-SUMMARY.md` — FOUND
- `firestarter_app/tests/test_revision_constants_parity.py` — FOUND (new test + 4 corrections confirmed present)
- `firestarter_app/firestarter/constants.py` — FOUND (corrected comment confirmed present)
- `.planning/REQUIREMENTS.md` — FOUND (RETIRE-04/08 corrections confirmed present)

Commits verified present in the owning repo's history:
- `831c95f` (`firestarter_app` submodule) — FOUND
- `42a1971` (`firestarter_app` submodule) — FOUND
- `88a521e` (meta-repo `/workspaces`) — FOUND
