---
phase: 183-flash4-erase-refusal-the-ae29f2008-classification
plan: 03
subsystem: cli
tags: [click, safety-gate, host-policy, pyproject-ruff]

# Dependency graph
requires:
  - phase: 183-01
    provides: "M3 (host pre-flight policy gate) chosen as the mechanism, on D-02 grounds"
provides:
  - "firestarter_app/firestarter/flash4_erase_gate.py — the pure, import-pure, fail-open flash4 erase-refusal predicate"
  - "cli_handlers.erase wired to refuse pre-connect on a flash4 (algorithm 5) part"
  - "--ignore-unsupported opt-in exit-0 flag on erase (D-06)"
affects: [183-06]

actuals:
  tokens: 4376
  tasks: 3
  commits: 4
  plan_head_before: a2bf4943530bc679172c327353e2461bf592e7f8

tech-stack:
  added: []
  patterns:
    - "flash4_erase_gate.py: third sibling to jp5_gate.py/sdp_capability.py — pure predicate, import set subset of {__future__, typing}, no #-comments (docstrings only)"
    - "The gate FAILS OPEN — deliberately inverted polarity vs. jp5_gate/sdp_capability, which both fail closed"

key-files:
  created:
    - "firestarter_app/firestarter/flash4_erase_gate.py"
    - "firestarter_app/tests/test_flash4_erase_gate.py"
  modified:
    - "firestarter_app/firestarter/cli_handlers.py"
    - "firestarter_app/tests/__snapshots__/test_characterization.ambr"

key-decisions:
  - "Placed the flash4_erase_gate.is_flash4 check BEFORE the existing jp5_gate.confirm_or_refuse call in cli_handlers.erase — a part refused outright has no reason to also prompt for a JP5 acknowledgement first."
  - "Task 3's database-coupling test iterates every shipped part_number through resolve_chip (not just the algorithm-5 subset), so the assertion proves both directions of the 'exactly the algorithm-5 rows' claim, not just that the 27 known rows fire."
  - "Updated the pre-existing test_help_erase syrupy snapshot (tests/__snapshots__/test_characterization.ambr) for the new --ignore-unsupported line in --help output — a required, intentional consequence of Task 2, not a deviation."

requirements-completed: [SAFE-06]

coverage:
  - id: D1
    description: "An operator running `firestarter erase` on a flash4 (algorithm 5) part gets exactly one refusal line and exit 1, with no serial connection attempted (D-02 pre-connect placement)"
    requirement: "SAFE-06"
    verification:
      - kind: integration
        ref: "tests/test_flash4_erase_gate.py#test_cli_erase_on_flash4_part_refuses_pre_connect_with_one_line"
        status: pass
    human_judgment: false
  - id: D2
    description: "--ignore-unsupported changes the exit code only (1 -> 0), never the message or whether erase is attempted (D-06)"
    requirement: "SAFE-06"
    verification:
      - kind: integration
        ref: "tests/test_flash4_erase_gate.py#test_cli_erase_ignore_unsupported_exits_0_with_byte_identical_output"
        status: pass
    human_judgment: false
  - id: D3
    description: "flash4_erase_gate.py is a pure, import-pure (subset of {__future__, typing}) predicate module, keyed on the same `algorithm` value convert_to_programmer's algo not in (5,) exclusion reads, with no part-number literal anywhere in its source (D-03, D-4)"
    requirement: "SAFE-06"
    verification:
      - kind: unit
        ref: "tests/test_flash4_erase_gate.py#test_is_flash4_true_only_for_algorithm_5_over_shipped_values (parametrized)"
        status: pass
      - kind: unit
        ref: "tests/test_flash4_erase_gate.py#test_predicate_matches_real_database_algorithm_5_rows_exactly"
        status: pass
      - kind: unit
        ref: "tests/test_flash4_erase_gate.py#test_module_source_contains_no_shipped_part_number_literal"
        status: pass
    human_judgment: false
  - id: D4
    description: "The gate FAILS OPEN on a missing/None/empty/key-less wire dict, and a non-flash4 part still reaches EpromOperator.erase_eprom — the gate does not widen past flash4 (D-05)"
    requirement: "SAFE-06"
    verification:
      - kind: unit
        ref: "tests/test_flash4_erase_gate.py#test_is_flash4_fails_open_on_absent_evidence (parametrized)"
        status: pass
      - kind: integration
        ref: "tests/test_flash4_erase_gate.py#test_cli_erase_on_non_flash4_part_still_reaches_operator"
        status: pass
    human_judgment: false
  - id: D5
    description: "The refusal line names the chip and carries none of the forbidden cause/alternative/--force-workaround content (D-07, D-09, D-10)"
    requirement: "SAFE-06"
    verification:
      - kind: unit
        ref: "tests/test_flash4_erase_gate.py#test_refusal_text_is_one_line_and_carries_no_forbidden_content"
        status: pass
    human_judgment: false

duration: 24min
completed: 2026-09-11
status: complete
---

# Phase 183 Plan 03: Pre-Connect Flash4 Erase Refusal (M3) Summary

**A new `flash4_erase_gate.py` policy module refuses `firestarter erase` on any algorithm-5 (flash4) part with one line and exit 1 — before the serial port opens — with `--ignore-unsupported` as the sole opt-in that flips the exit code to 0, and 22 tests proving the predicate, its fail-open polarity, its exact 27-row database coupling, its comment-free import-pure source, its cause-free message shape, and that it never widens past flash4.**

## Performance

- **Duration:** 24 min
- **Started:** 2026-09-11T08:29:00Z (approx)
- **Completed:** 2026-09-11T08:53:00Z (approx)
- **Tasks:** 3
- **Files modified:** 4 (2 created, 2 modified) in `firestarter_app`; the meta-repo `firestarter_app` gitlink advanced 3 times, once per task

## Accomplishments
- `flash4_erase_gate.py` created as a third sibling to `jp5_gate.py`/`sdp_capability.py`: import-pure (subset of `{__future__, typing}`), no I/O, no `#`-comments, exporting `FLASH4_PROTOCOL_ID`, `is_flash4`, and `refusal_text`.
- `cli_handlers.erase` wired to call the gate between `resolve_chip` and `app.eprom_operator.erase_eprom`, refusing before any serial connection is attempted (D-02).
- `--ignore-unsupported` added as a long-form-only Click flag: changes the exit code from 1 to 0 and nothing else — the printed line is byte-identical on both legs, proven by a test that compares the two invocations to each other rather than to a re-stated literal (D-06).
- `tests/test_flash4_erase_gate.py` grew to 22 tests across six proof groups: the pure predicate over every shipped algorithm value, fail-open on absent evidence, exact coupling to the real database's 27 algorithm-5 rows (checked bidirectionally against every shipped part number, not just the known 27), no part-number literal anywhere in the module source, the one-line cause-free message shape (negative substring assertion), and proof a non-flash4 part still reaches `erase_eprom`.

## Task Commits

Each task was committed atomically, once inside the `firestarter_app` submodule and once as a meta-repo gitlink advance:

1. **Task 1: End-to-end flash4 erase refusal — one path only (TRACER)** - `244ff7e` (feat, in `firestarter_app`) / `8432a606` (chore, gitlink advance)
2. **Task 2: The --ignore-unsupported opt-in exit-0 flag (D-06)** - `e0ea5ee` (feat, in `firestarter_app`) / `b926b0fe` (chore, gitlink advance)
3. **Task 3: Prove the predicate, the database coupling and the message shape** - `7446059` (test, in `firestarter_app`) / `1beff619` (chore, gitlink advance)

**Plan metadata:** commit for this SUMMARY.md follows immediately after this file is written (see `git_commit_metadata` step).

## Files Created/Modified
- `firestarter_app/firestarter/flash4_erase_gate.py` — new module: `FLASH4_PROTOCOL_ID`, `is_flash4`, `refusal_text`
- `firestarter_app/firestarter/cli_handlers.py` — `erase` handler: gate call + `--ignore-unsupported` option
- `firestarter_app/tests/test_flash4_erase_gate.py` — new test file, 22 tests across 6 proof groups
- `firestarter_app/tests/__snapshots__/test_characterization.ambr` — `test_help_erase` snapshot updated for the new `--help` line
- `firestarter_app` (gitlink, meta repo) — advanced 3 times, once per task

## Decisions Made
- The flash4 gate call is placed BEFORE the existing `jp5_gate.confirm_or_refuse` call in `erase` — a part refused outright by the flash4 gate has no reason to also prompt for a JP5 acknowledgement.
- Task 3's database-coupling test iterates every shipped `part_number` (not only the 27 known algorithm-5 rows) through `resolve_chip`, so the assertion proves the predicate fires on EXACTLY the algorithm-5 set — both that all 27 fire and that nothing else does — rather than only confirming the known 27.
- The forbidden-substring list in the message-shape test (`force`, `write`, `workaround`, `route around`, `because`, `reason`, `cause`, `alternative`, `instead`, `try`) was hand-picked to cover D-07/D-09/D-10's prohibitions while never colliding with the refusal text's own wording ("Erase not supported for `<chip>`").

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Updated the pre-existing `test_help_erase` syrupy snapshot**
- **Found during:** Task 2 (adding the `--ignore-unsupported` flag)
- **Issue:** `tests/test_characterization.py::test_help_erase` snapshot-asserts the exact `firestarter erase --help` output. Adding the new option and its docstring sentence necessarily changed that output, failing the pre-existing snapshot test — a direct, in-scope consequence of Task 2's own required change, not an unrelated pre-existing failure.
- **Fix:** Ran `pytest tests/test_characterization.py::test_help_erase --snapshot-update`, which updated only the `erase` entry in `tests/__snapshots__/test_characterization.ambr` (5 lines added, nothing else touched).
- **Files modified:** `tests/__snapshots__/test_characterization.ambr`
- **Verification:** Re-ran the full `-k "eprom_operations or cli or erase or jp5 or sdp or flash4"` filtered suite (446 tests) — all pass, including the updated snapshot.
- **Committed in:** `7446059` (Task 3 commit — the snapshot update was verified and committed alongside Task 3's test additions, since Task 2's own commit predates the snapshot regression's discovery during Task 3's full-suite run)

---

**Total deviations:** 1 auto-fixed (1 blocking — a snapshot regression that was a direct, required consequence of Task 2's plan-specified change, not new scope)
**Impact on plan:** No scope creep; the snapshot update makes the test suite reflect the `--help` text the plan itself specifies.

## Issues Encountered
None beyond the snapshot deviation documented above.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- `flash4_erase_gate.py` exists, is wired, and is tested; SAFE-06's must-haves (pre-connect firing, byte-identical exit-code-only opt-in, import-pure sibling module, database-keyed predicate, fail-open polarity, non-widening scope, no `--force` mention) are all satisfied and pinned by tests.
- `183-06` (the SAFE-06 requirement-text amendment referenced in this plan's `<flagged_assumptions>`) can now cite this module and its behavior as the ground truth for what the amended requirement text should say.
- No blockers.

---
*Phase: 183-flash4-erase-refusal-the-ae29f2008-classification*
*Completed: 2026-09-11*

## Self-Check: PASSED

- FOUND: `firestarter_app/firestarter/flash4_erase_gate.py`
- FOUND: `firestarter_app/tests/test_flash4_erase_gate.py`
- FOUND: `.planning/phases/183-flash4-erase-refusal-the-ae29f2008-classification/183-03-SUMMARY.md`
- FOUND (submodule log): commit `244ff7e` (Task 1)
- FOUND (submodule log): commit `e0ea5ee` (Task 2)
- FOUND (submodule log): commit `7446059` (Task 3)
- FOUND (meta repo log): commits `8432a606`, `b926b0fe`, `1beff619` (per-task gitlink advances), `a1aa3995` (this SUMMARY)
- Meta gitlink (`git ls-tree HEAD -- firestarter_app`) matches `git -C firestarter_app rev-parse HEAD` exactly (`7446059c...`)
- Re-ran all plan-level `<verification>` commands: `pytest tests/test_flash4_erase_gate.py` (22 passed), `pytest tests/test_jp5_gate.py tests/test_sdp_capability.py` (53 passed), `firestarter erase --help` lists `--ignore-unsupported`, import-purity AST check reports `IMPORT_PURE`, `ruff check`/`ruff format --check` clean on all three touched files, no `#` comment lines in either new file or in the `cli_handlers.py` diff (directive lines excepted)
- **Recovered from a `gsd-tools query commit` branch-switch during the metadata commit** — it created and switched to an errant `-activated-202` milestone branch and pruned two `sub_repos` entries from `.planning/config.json`. Fast-forwarded the correct branch onto the SUMMARY commit, deleted the errant branch, and reverted `config.json`; verified HEAD, gitlink, and working-tree state below.
- `git rev-parse --abbrev-ref HEAD` → `gsd/v1.37-operator-safety-answered-reports-claim-hygiene`
- `git status --short` → only pre-existing dirt (`.planning/VALIDATED-EPROMS.md`, `anything.txt`, `tmp/`, two untracked `firestarter_app/datasheets/*.pdf`), all out of this plan's scope per the executor prompt's `<project_mechanics>` §7
