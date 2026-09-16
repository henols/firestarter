---
phase: quick-260916-nba
plan: 01
subsystem: cli
tags: [firestarter_app, dev-test, submit, diagnostic-report, markdown-rendering]

requires:
  - phase: quick-260916-nb9
    provides: "chip_test.resolve_error_name(code) -> str | None, plus an unconditional error_name key on diagnostic_report's serialized steps"
provides:
  - "submit._error_text/_error_cells: a shared Error-cell formatter and column-presence decider consumed by both markdown tables"
  - "The Error column in submit.build_body (filed issue body) and cli_handlers.py's dev-test-<chip>.md handler (saved artifact)"
affects: [devtest-triage, devtest-rootcause]

actuals:
  tokens: 3737
  tasks: 2
  commits: 4
plan_head_before: e4cbfdf5c0c7a5b192367667798d6882ec776e6b

tech-stack:
  added: []
  patterns:
    - "Shared render-layer formatter (_error_cells) decides column presence once and is consumed by two independent table builders, so they cannot disagree on when a column appears"

key-files:
  created: []
  modified:
    - firestarter_app/firestarter/submit.py
    - firestarter_app/firestarter/cli_handlers.py
    - firestarter_app/tests/test_submit.py
    - firestarter_app/tests/test_dev_test_cmd.py

key-decisions:
  - "Scope correction: the render sites are submit.py::build_body and cli_handlers.py's dev test handler, not chip_test.py (which only holds the StepResult.error_code field and renders no table) — the batch item's named scope was wrong; both actual render sites were changed instead"
  - "260916-nb9's chip_test.resolve_error_name(code) was importable live and is used directly (from firestarter.chip_test import resolve_error_name) rather than reading firestarter.messages.CATALOG a second time — it is nb9's own wrapper around that same catalog, so this stays a single source"
  - "NA-versus-SKIPPED asymmetry: an NA step's Error cell is suppressed to '-' by the same verdict-keyed rule _reason_text already applies, while a SKIPPED step's code renders unsuppressed. Authority: chip_test.py's blank-check dispatch docstring (around line 2670, OP_BLANK_CHECK dispatch in _dispatch_step) states a non-blank UV part's pre-write blank-check is adjudicated SKIPPED rather than NA precisely because 'submit._reason_text suppresses the Reason cell to - for NA only, which would destroy the very finding this step exists to surface' and 'SKIPPED preserves reason and error_code verbatim.' _error_text's suppression rule mirrors that same NA-only carve-out for the new column, so the disclosure the SKIPPED verdict exists to protect is not silently re-suppressed by the new column."
  - "Column-position/omission rationale: the Error column sits between Took and Reason (fixed-width cell before the variable-length prose cell, matching the plan's stated shape) and is emitted only when _error_cells returns non-None (at least one row has a real code) — a passing report with no coded step renders byte-identical to today's table, verified by the pre-existing fixture-based tests in both files staying green untouched."
  - "Untrusted-value hardening lives in one place: _sanitize_error_name (module-level helper in submit.py, called from _error_text only) strips pipe/newline/CR and truncates to 64 chars. cli_handlers.py never re-implements this — it consumes the formatter's output via _error_cells, so the two tables cannot diverge on hardening either."

requirements-completed: [260916-nba]

coverage:
  - id: D1
    description: "submit.build_body renders an Error column between Took and Reason for a step carrying error_code, and omits the column entirely when no step has one"
    requirement: "260916-nba"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_submit.py#test_build_body_emits_the_error_column_when_a_step_carries_a_code"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_submit.py#test_build_body_table_from_sanitized_steps"
        status: pass
    human_judgment: false
  - id: D2
    description: "The saved dev-test-<chip>.md artifact renders the identical Error cell for the identical step as the filed issue body, via the same shared formatter"
    requirement: "260916-nba"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_dev_test_cmd.py#TestReportDestination::test_md_artifact_carries_the_firmware_error_name_on_a_failing_step"
        status: pass
    human_judgment: false
  - id: D3
    description: "NA rows render '-'; SKIPPED rows keep their code; unknown and malformed codes degrade without raising; an explicit error_name wins over catalog resolution; a hostile error_name cannot break out of its cell or add a row"
    requirement: "260916-nba"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_submit.py#test_error_text_verdict_policy"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_submit.py#test_error_text_unknown_code_degrades_to_the_bare_decimal"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_submit.py#test_error_text_malformed_code_degrades_without_raising"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_submit.py#test_error_text_hostile_name_cannot_add_a_table_row"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_submit.py#test_error_text_truncates_a_name_longer_than_the_cap"
        status: pass
    human_judgment: false

duration: 55min
completed: 2026-09-16
status: complete
---

# Quick 260916-nba: Firmware error code + symbolic name on the dev-test markdown tables Summary

**`submit._error_text`/`_error_cells` add a shared, NA-suppressed, hostile-input-hardened Error column (`MSG_ERR_OP_TIMEOUT (183)` style) between Took and Reason on both `submit.build_body` and the `dev-test-<chip>.md` handler, resolved via 260916-nb9's `chip_test.resolve_error_name`.**

## Performance

- **Duration:** ~55 min
- **Tasks:** 2
- **Files modified:** 4 (`firestarter/submit.py`, `firestarter/cli_handlers.py`, `tests/test_submit.py`, `tests/test_dev_test_cmd.py`)

## Scope correction

The batch item named `firestarter_app/firestarter/chip_test.py` as the scope. That file holds only the `StepResult.error_code` dataclass field — it renders no table. Per the plan's own scope correction, the two actual render sites were changed instead: `submit.py::build_body` (the filed/pasted issue body) and `cli_handlers.py`'s `dev test` handler (the saved `.md` artifact).

## Accomplishments

- `submit._error_text(verdict, error_code, error_name=None)` — the single Error-cell formatter, keyed on `VERDICT_NA` for suppression, tolerant of any non-coercible `error_code` (returns `-` without raising), preferring a caller-supplied `error_name` over catalog resolution via `chip_test.resolve_error_name`, and hardened against a hostile name via `_sanitize_error_name`.
- `submit._error_cells(rows)` — maps a `(verdict, error_code, error_name)` iterable through `_error_text` and returns `None` when every cell is the placeholder, the single signal both tables key their column-presence branch on.
- `build_body` and `cli_handlers.py`'s `dev test` handler both call `_error_cells` once and branch header/separator/row identically, so the filed issue body and the saved artifact can never disagree on whether the column appears or what it contains.
- A real end-to-end path proven: a mocked `EpromOperator` with `check_eprom_blank.return_value = False` and `last_firmware_error_code = 0xB0` produces a saved `dev-test-<chip>.md` whose `blank-check` row carries `MSG_ERR_NOT_BLANK (176)`.

## Task Commits

Each task followed the RED -> GREEN TDD cycle (tasks were `tdd="true"`), producing two commits each:

1. **Task 1: One failing step's code and name reach BOTH markdown tables, end to end**
   - `d5033b1` — `test(260916-nba): pin the Error column shape on both markdown tables` (RED)
   - `e051266` — `feat(260916-nba): render the firmware error code and name in both markdown tables` (GREEN)
2. **Task 2: Pin the verdict policy, the degradation paths, and the untrusted-value hardening**
   - `0376fa2` — `test(260916-nba): pin verdict policy, degradation, and hostile-name hardening` (RED — only the two hostile-name hardening assertions were genuinely RED; every verdict-policy/degradation/name-preference assertion already passed against Task 1's implementation, since Task 1's `<action>` already specified that full behavior)
   - `7bbaf3c` — `feat(260916-nba): strip and cap a hostile error_name before it reaches a cell` (GREEN)

All four commits landed in the `firestarter_app` submodule on branch `v1.39-protocol-0x05-write-correctness`. No plan-metadata commit was made in the meta repo per this executor's constraints (no STATE.md/ROADMAP.md updates, no gitlink staged — orchestrator owns those).

## Files Created/Modified

- `firestarter_app/firestarter/submit.py` — added `_ERROR_NAME_MAX_LEN`, `_sanitize_error_name`, `_error_text`, `_error_cells`; extended the `chip_test` import with `resolve_error_name`; `build_body` now branches its header/rows on `_error_cells`' return.
- `firestarter_app/firestarter/cli_handlers.py` — the `dev test` handler's local `from firestarter.submit import ...` group gained `_error_cells`; `md_lines` construction now branches identically to `build_body`.
- `firestarter_app/tests/test_submit.py` — RED/GREEN pairs for `_error_text`/`_error_cells`, `build_body`'s column emission and omission, verdict policy, degradation, name-preference, and hostile-name hardening.
- `firestarter_app/tests/test_dev_test_cmd.py` — one end-to-end test: a real `dev test` CLI invocation whose blank-check fails with a recorded firmware error code writes a `dev-test-<chip>.md` carrying the resolved name.

## Decisions Made

See `key-decisions` in frontmatter for the full rationale on: the scope correction, why `resolve_error_name` was used directly instead of reading `messages.CATALOG` a second time, the NA-versus-SKIPPED asymmetry (cited to `chip_test.py`'s `OP_BLANK_CHECK` dispatch docstring around line 2670-2684), the column-position/omission rule, and where the untrusted-value hardening lives.

**260916-nb9's resolver was importable** — `firestarter.chip_test.resolve_error_name` existed live at the anchor commit (`e4cbfdf5`) and was used directly rather than falling back to a raw `firestarter.messages.CATALOG.get(code)` call, per the plan's stated preference order.

## Deviations from Plan

None affecting behavior. Two minor test-authoring corrections made during RED verification, both caught before the corresponding GREEN commit:

1. A first draft of the end-to-end `test_dev_test_cmd.py` test asserted `result.exception is None`, which is wrong for a CLI path that legitimately exits 1 (Click's `CliRunner` surfaces a `sys.exit(1)` as a `SystemExit` exception object, not `None`). Corrected to `assert result.exit_code in (0, 1)` before the RED run was captured — not a behavior change, a test-correctness fix caught during the same RED cycle.
2. A first draft of `test_build_body_column_omission_still_carries_error_code_in_the_json_block` used a report shape where the Error column would NOT actually be suppressed (a `write`/`BAD` step with a real code alongside an `id`/`OK`/`None` step), making the test self-contradictory. Corrected to use an `NA` step carrying a code (cell suppressed to `-` by the NA rule, but the JSON block still carries `error_code` verbatim) — this is what the plan's "table suppression is render-layer only" behavior actually describes.

Both corrections were made during test authoring, before any implementation code existed for the behavior under test, and are documented here for completeness rather than as Rule 1-4 auto-fixes (no product code was affected).

## Issues Encountered

None. `Mock(spec=EpromOperator)` (used by the pre-existing `make_clean_operator()` test builder) permits setting `last_firmware_error_code`/`last_firmware_error_message` even though those are instance-only attributes assigned in `__init__` (verified interactively before relying on it) — `spec` restricts unlisted attribute *access*, not assignment, so no test-double change was needed.

## RED evidence (Task 1)

- Command: `./.venv311/bin/python -m pytest tests/test_submit.py -q -o addopts="" -k "error_text or error_cells or emits_the_error_column"`
- Result before implementation: 5 failed — `AttributeError: module 'firestarter.submit' has no attribute '_error_text'` / `'_error_cells'` (2x each) and one `AssertionError` on the missing Error header in `build_body`'s output. All five failures were on the intended assertion for the planned behavior; no collection errors, no unrelated failures.
- Command: `./.venv311/bin/python -m pytest tests/test_dev_test_cmd.py -q -o addopts="" -k "carries_the_firmware_error_name"`
- Result before implementation: 1 failed — `AssertionError: assert '| Step | Verdict | Runs | Took | Error | Reason |' in '...| Step | Verdict | Runs | Took | Reason |...'` (today's Reason-only header, as expected before the wiring existed).

## RED evidence (Task 2)

- Command: `./.venv311/bin/python -m pytest tests/test_submit.py -q -o addopts="" -k "error_text or error_cells or column_omission"`
- Result before hardening: 2 failed, 17 passed. The 17 passes are expected overlap — Task 1's `<action>` already specified NA suppression, tolerant coercion, and name preference, so those assertions were already satisfied by Task 1's implementation. The 2 genuine RED failures: `test_error_text_strips_pipe_and_newline_characters_from_a_hostile_name` (pipe survived unstripped: `'EVIL | injected\r\nrow (183)'`) and `test_error_text_truncates_a_name_longer_than_the_cap` (`len(name_part) == 100`, not `64`) — both failing on the exact assertion the hardening behavior specifies, nothing else.

## New-column verify leg — what it actually printed

Confirmed by eye, per the plan's `<verification>` instruction, that the Error column sits between `Took` and `Reason` and the separator row has the same cell count as the header:

```
canonical part number: W27C512

| Step | Verdict | Runs | Took | Error | Reason |
| ---- | ------- | ---- | ---- | ----- | ------ |
| id | OK | 1 | 0.03s | - | - |
| write | BAD | 2 | 41.9s | MSG_ERR_OP_TIMEOUT (183) | op timed out |
```

Both the two pre-existing table assertions (`test_build_body_table_from_sanitized_steps` in `test_submit.py`, `test_md_artifact_contains_fenced_json_block` in `test_dev_test_cmd.py`) stayed green throughout, unmodified — their fixtures carry no `error_code`, so they never exercise the new column, which is exactly why the plan called for a leg that DOES exercise it. That leg is `test_build_body_emits_the_error_column_when_a_step_carries_a_code` (submit.py) and `test_md_artifact_carries_the_firmware_error_name_on_a_failing_step` (cli_handlers.py, real CLI invocation through a mocked failing operator) — both pass and both assert the actual rendered header/row text, not merely that the run exited 0.

## Full verification run

- `./.venv311/bin/python -m pytest tests/ -q -o addopts=""` — **1970 passed**, 32 snapshot checks passed, exit code 0 (~199s).
- `./.venv311/bin/python -m pytest tests/test_parse_devtest_issue.py -q -o addopts=""` — **28 passed** (this parser reads only the fenced JSON block, never the step table, confirming the column addition left it unaffected).
- `./.venv311/bin/ruff check firestarter tests` — **All checks passed.**
- `./.venv311/bin/ruff format --check firestarter tests` — **137 files already formatted.**

## Known Stubs

None.

## Threat Flags

None — the threat model's own three `mitigate` items (T-nba-01 information disclosure, T-nba-02 tampering via a hostile `error_name`, T-nba-03 DoS via a malformed `error_code`) are addressed directly by `_error_text`'s coercion/suppression logic and `_sanitize_error_name`, and are pinned by the Task 2 tests above. No new surface beyond what the threat model already enumerated was introduced.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- The Error column is live on both the filed issue body and the saved `.md` artifact; a triager reading a filed `dev test` issue now sees the firmware error name and code without unfolding the JSON block.
- `diagnostic_report.py` was left untouched per the plan (no schema field, no `SCHEMA_VERSION` change, no console-table change) — this remains true; only render-layer code changed.
- No blockers for downstream work (e.g. `devtest-triage` skill consumers now see richer markdown tables in filed issues, with no change to the underlying JSON schema they might also parse).

---
*Phase: quick-260916-nba*
*Completed: 2026-09-16*
