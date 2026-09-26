---
phase: 153-write-path-erase-policy
plan: 12
subsystem: testing
tags: [pytest, database, ic_layout, chip_test, cli, erase-policy, at28c256]

# Dependency graph
requires:
  - phase: 153-write-path-erase-policy
    provides: "153-07's restored FLAG_CAN_ERASE for algorithm 13 (ERASE-03/ERASE-07); 153-08/153-09/153-10/153-11's inverted flag/wire/plan-shape/warning tests"
provides:
  - "Exhaustive whole-database proof: exactly 84 of 746 rows (algorithm 13) carry the erase capability bit after conversion, and 0 non-algorithm-13 rows moved"
  - "A named, non-empty-population hardware-damage guard for algorithm 5 (flash4), kept separate from the generic scope proof"
  - "Pinned AT28C256 plan shapes at write_scope='full' (12 steps) and write_scope='none' (3 steps, 9 locked-destructive ops) — the second shape had no prior committed assertion"
  - "Both-directions ERASE-06 agreement leg: info's can-be-erased row and the wire FLAG_CAN_ERASE bit assert together for AT28C256 (affirmative) and AM27512 (UV-EPROM negative control), with zero ic_layout.py edits"
  - "ERASE-05 non-regression proof across three layers: CLI registration/help, host call boundary (positive call assertion, both happy-path and not-blank outcomes), and the firmware CMD_BLANK_CHECK/CMD_ERASE dispatch arms (skip-clean via the sibling-presence helper)"
affects: [153-16]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Two-level manufacturer->chip-list selector with an anti-vacuity docstring, reused from test_page_size_invariants.py's precedent, for exhaustive whole-database legs"
    - "Reachability proven via a temporary, reverted mutation of the production tuple/condition rather than trusting a leg's shape alone; legs invariant to one mutation are proven via a second, different mutation"
    - "Cross-repo firmware source assertions scoped to a single case-block substring (not whole-file), via tests.fw_presence's requires_fw / fw_path"

key-files:
  created:
    - firestarter_app/tests/test_erase_flag_invariants.py
    - firestarter_app/tests/test_erase_blank_step_nonregression.py
  modified:
    - firestarter_app/tests/test_ic_layout.py

key-decisions:
  - "ERASE-06 read as 'the two axes must not contradict', not 'info must derive from the wire bit' — per 152-CONTEXT.md D-07's own decomposition, which names the pre-153 state as a contradiction. Zero ic_layout.py edit follows from this reading, confirmed by reading build_specifications' can-be-erased block (lines 578-586) before writing either test."
  - "ERASE-05 treated strictly as non-regression: no implementation task, only assertions against the existing blank -> check_eprom_blank -> CMD_BLANK_CHECK -> mem_util_blank_check chain."
  - "AT28C256 plan-shape figures for legs 5/6 were derived live from derive_plan() in this session, not copied from the plan's prose, then the prose was confirmed to match exactly."

requirements-completed: [ERASE-05, ERASE-06]

coverage:
  - id: D1
    description: "Exactly 84 of 746 database rows (algorithm 13) carry the erase capability bit; 0 non-algorithm-13 rows changed; algorithm-5 rows never carry it (non-empty-population guard)"
    requirement: "ERASE-03"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_erase_flag_invariants.py::test_exactly_84_algorithm_13_rows_across_all_746_rows"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_erase_flag_invariants.py::test_every_algorithm_13_row_carries_the_erase_capability_bit"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_erase_flag_invariants.py::test_no_non_algorithm_13_row_gained_the_erase_capability_bit"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_erase_flag_invariants.py::test_algorithm_5_rows_still_do_not_carry_the_erase_capability_bit"
        status: pass
    human_judgment: false
  - id: D2
    description: "AT28C256 write_scope='full' (12-step) and write_scope='none' (3-step, 9 locked-destructive) plan shapes are pinned by list/set equality, the latter previously unasserted"
    requirement: "ERASE-03"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_erase_flag_invariants.py::test_at28c256_full_plan_shape_is_pinned"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_erase_flag_invariants.py::test_at28c256_write_scope_none_shape_is_pinned"
        status: pass
    human_judgment: false
  - id: D3
    description: "info's can-be-erased row and the wire FLAG_CAN_ERASE bit agree in both directions for algorithm-13 (affirmative) and UV-EPROM (negative control), with zero ic_layout.py edits"
    requirement: "ERASE-06"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_ic_layout.py::test_can_erase_row_and_wire_capability_bit_agree_for_algorithm_13"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_ic_layout.py::test_can_erase_row_and_wire_capability_bit_agree_for_uv_eprom"
        status: pass
    human_judgment: false
  - id: D4
    description: "blank remains its own step at the CLI (registration + help), the host call boundary (positive call assertion, happy-path and not-blank outcomes), and the firmware dispatch arm (CMD_BLANK_CHECK wired, CMD_ERASE assigns no operation_end)"
    requirement: "ERASE-05"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_erase_blank_step_nonregression.py::test_blank_command_is_registered_and_documented"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_erase_blank_step_nonregression.py::test_blank_command_reaches_the_host_blank_check_call"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_erase_blank_step_nonregression.py::test_blank_command_reports_not_blank_correctly"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_erase_blank_step_nonregression.py::test_firmware_still_wires_the_blank_check_arm"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_erase_blank_step_nonregression.py::test_no_post_erase_blank_check_was_wired_on_0x0d"
        status: pass
    human_judgment: false

duration: 75min
completed: 2026-08-21
status: complete
---

# Phase 153 Plan 12: Positive coverage for ERASE-03 / ERASE-05 / ERASE-06 Summary

**Exhaustive 84-of-746 database scope proof, both-directions info/wire agreement for ERASE-06 with zero source edits, and three-layer ERASE-05 non-regression coverage for `blank` — closing the scope gap the inversions in plans 08-11 left open.**

## Performance

- **Duration:** ~75 min
- **Tasks:** 3
- **Files modified:** 3 (2 new test modules, 1 extended test module)
- **Host suite (this session, Python 3.11 per app CI):** 1825 passed, 0 failed, 1 warning, 83.61% coverage (`pytest tests/ --cov=firestarter --cov-report=term-missing --cov-fail-under=70 -o addopts=""`) — up from the inherited 1812 by exactly the 13 tests this plan adds (6 + 2 + 5)

## Accomplishments

- Added `test_erase_flag_invariants.py`: 6 legs proving the FLAG_CAN_ERASE restoration is scoped — exactly 84/746 rows gained the bit, 0 non-13 rows moved, algorithm-5 rows (27, non-empty) are hardware-damage-guarded separately, and both AT28C256 plan shapes (`write_scope="full"` 12-step, `write_scope="none"` 3-step/9-locked) are pinned by equality.
- Added two legs to `test_ic_layout.py` proving ERASE-06's info-row/wire-bit agreement in both directions (AT28C256 affirmative, AM27512 UV-EPROM negative control), confirming zero `ic_layout.py` source edit was owed.
- Added `test_erase_blank_step_nonregression.py`: 5 legs proving `blank` still works as its own step at the CLI, the host call boundary, and the firmware dispatch arm, complementing (not duplicating) the pre-existing coverage in `test_characterization.py` and `test_eprom_operations.py`.
- Flipped ERASE-05 and ERASE-06 to complete in REQUIREMENTS.md (both claimed only by this plan); left ERASE-03 `In Progress` (still claimed by plan 13, not yet run).

## Task Commits

Each task was committed atomically, inside `firestarter_app` (this phase's `commits_land_in` target):

1. **Task 1: `test_erase_flag_invariants.py` — exhaustive 84-of-746 + plan-shape pins** - `16d9845` (test)
2. **Task 2: ERASE-06 both-directions agreement leg in `test_ic_layout.py`** - `a6efeae` (test)
3. **Task 3: ERASE-05 non-regression across CLI/host/firmware** - `a78ccd5` (test)

**Submodule pointer update (meta repo):** `4e8b22d2` (chore: bump `firestarter_app` gitlink to `a78ccd5`)

**Plan metadata:** committed after this summary.

## Files Created/Modified

- `firestarter_app/tests/test_erase_flag_invariants.py` - new module; 6 legs, exhaustive whole-database scope proof plus the two AT28C256 plan-shape pins
- `firestarter_app/tests/test_ic_layout.py` - +2 legs (13 tests total, up from 11); ERASE-06 both-directions agreement
- `firestarter_app/tests/test_erase_blank_step_nonregression.py` - new module; 5 legs across CLI, host, and firmware layers
- `firestarter_app` (gitlink in meta repo) - bumped to `a78ccd5`

No `ic_layout.py`, `database.py`, `cli_handlers.py`, `eprom_operations.py`, or any `firestarter/` (firmware) source file was modified. `git diff --stat -- firestarter/ic_layout.py` and `git status --porcelain firestarter/` were both confirmed empty at the end of this plan.

## Decisions Made

- **ERASE-06 reading (D-07 decomposition, not derivation):** adopted the "must not contradict" reading over "must derive from", per `152-CONTEXT.md` D-07's own decomposition table entry ("info's can be erased row | ic_layout.py:579 | contradicts the wire flag"). This licenses zero `ic_layout.py` edit; both new legs' docstrings record this explicitly, including the out-of-scope third value `_interpret_flags` reads.
- **ERASE-05 stayed pure assertion:** no implementation task was added anywhere in this plan; all five legs in Task 3 assert an already-working chain.
- **Plan-shape figures derived live, not from prose:** legs 5/6 in Task 1 and the reachability mutations for all six legs were measured directly against this session's `derive_plan()` and `convert_to_programmer()` output before being written into the test file, then cross-checked against the plan's prose (which matched exactly).

## Deviations from Plan

None — plan executed exactly as written. All three tasks match their specified action, legs, and acceptance criteria; no auto-fixes (Rules 1-3) or architectural changes (Rule 4) were needed, because this plan is assertion-only by design and no source defect was found while reading the code it asserts against.

## Reachability Evidence (acceptance criterion: every leg observed to fail before being trusted)

Two temporary, reverted mutations of `firestarter_app/firestarter/database.py` line 638 were used (both confirmed removed via `git diff --quiet -- firestarter_app/firestarter/database.py` before continuing):

**Mutation A — revert plan 07's tuple edit** (`if algo not in (5,):` -> `if algo not in (5, 13):`, reproducing the pre-Phase-153 state):
- `test_erase_flag_invariants.py::test_every_algorithm_13_row_carries_the_erase_capability_bit` — FAILED (0/84 rows carried the bit)
- `test_erase_flag_invariants.py::test_at28c256_full_plan_shape_is_pinned` — FAILED (erase step became NA, blank-check moved back to index 2, op order collapsed to 8 steps)
- `test_erase_flag_invariants.py::test_at28c256_write_scope_none_shape_is_pinned` — FAILED (erase appeared as a 4th `steps` entry instead of being locked, and the locked-op set dropped `erase`)
- `test_ic_layout.py::test_can_erase_row_and_wire_capability_bit_agree_for_algorithm_13` — FAILED (`wire["flags"] & FLAG_CAN_ERASE` was 0, reproducing exactly the gh#20 contradiction: `can_erase_str` said "yes" while the wire bit was clear)
- Legs invariant to Mutation A (unaffected, as expected, because they scan non-algorithm-13 rows or measure UV-EPROM which never touches this branch): `test_exactly_84_algorithm_13_rows_across_all_746_rows`, `test_no_non_algorithm_13_row_gained_the_erase_capability_bit`, `test_algorithm_5_rows_still_do_not_carry_the_erase_capability_bit`, `test_can_erase_row_and_wire_capability_bit_agree_for_uv_eprom`

**Mutation B — drop the algorithm-5 exclusion entirely** (`if algo not in (5,):` -> `if True:`):
- `test_erase_flag_invariants.py::test_no_non_algorithm_13_row_gained_the_erase_capability_bit` — FAILED (all 27 algorithm-5 rows flipped to bit=True)
- `test_erase_flag_invariants.py::test_algorithm_5_rows_still_do_not_carry_the_erase_capability_bit` — FAILED (same 27 rows named as offenders)
- The other four `test_erase_flag_invariants.py` legs and both `test_ic_layout.py` legs stayed green under Mutation B, as expected (algorithm 13 and UV-EPROM chips are untouched by this exclusion).

`test_erase_flag_invariants.py::test_exactly_84_algorithm_13_rows_across_all_746_rows` does not depend on `FLAG_CAN_ERASE` at all (it only counts rows by `programming.algorithm`), so neither mutation touches it. Its anti-vacuity reachability was instead confirmed by hand: a top-level-only scan (`for row in db.proms: ...`, never descending into the per-manufacturer chip list) returns 0 pairs where the real two-level `_select_algorithm_13_rows` helper returns 84 — exactly the vacuous-pass failure mode the module's docstring warns about.

For `test_erase_blank_step_nonregression.py`'s 5 legs and `test_ic_layout.py`'s UV-EPROM negative control, reachability was established by construction rather than mutation: legs 1-3 exercise a real CLI dispatch path (a broken `blank` registration or a broken `check_eprom_blank` call/return-value handling would fail them immediately, as verified by temporarily inspecting `result.exit_code` against both `True` and `False` operator doubles), and legs 4-5 assert against real, unmutated firmware source text whose absence of the asserted string would fail the `in` check directly.

## Issues Encountered

- Mid-task, a `git stash` command was run by mistake while trying to compare test-file state before/after an edit (intending a read-only inspection, not a destructive operation). It stashed the then-uncommitted `test_ic_layout.py` edits. This was caught immediately: `git stash pop` was run before any other repository operation, and the diff was confirmed intact (108 insertions, matching the pre-stash state) before proceeding. No work was lost and no other stash entries were touched. Recorded here per the destructive-git-prohibition guidance so it is on the record rather than silently corrected.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- ERASE-05 and ERASE-06 are fully closed; ERASE-03 remains `In Progress` pending plan 13's documentation flip (`PROTOCOLS.md` §1.6, `protocol-id.md`), which is the only other plan still claiming it.
- Host suite is fully green at 1825 passed (up from 1812), 83.61% coverage, ruff and mypy watermark (35==35) both clean, `firestarter/` (firmware) untouched.
- Plan 13 (wave 8, ERASE-01/02/03 documentation) is still pending; plans 14-16 (waves 10-12, ERASE-08/09 and the phase record) follow after wave 9 completes.

---
*Phase: 153-write-path-erase-policy*
*Completed: 2026-08-21*

## Self-Check: PASSED

- `firestarter_app/tests/test_erase_flag_invariants.py` — FOUND
- `firestarter_app/tests/test_erase_blank_step_nonregression.py` — FOUND
- `firestarter_app/tests/test_ic_layout.py` — FOUND
- `.planning/phases/153-write-path-erase-policy/153-12-SUMMARY.md` — FOUND
- Commit `16d9845` (firestarter_app) — FOUND
- Commit `a6efeae` (firestarter_app) — FOUND
- Commit `a78ccd5` (firestarter_app) — FOUND
- Commit `4e8b22d2` (meta repo, gitlink bump) — FOUND
