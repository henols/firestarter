---
phase: 185-records-and-checks-that-are-current
plan: 04
subsystem: testing
tags: [pytest, ruff, mypy, dead-code-removal, docstring-hygiene, ast-scan]

requires:
  - phase: 185-03
    provides: "test_dev_test_cmd.py with zero references to _is_interactive/_off_tty()"
provides:
  - "firestarter_app repo (tracked files) with zero references to _is_interactive anywhere"
  - "test_numeric_schema_source_scan.py with zero file-plus-line-number docstring citations"
affects: [185-06]

actuals:
  tokens: 9800
  tasks: 3
  commits: 2

tech-stack:
  added: []
  patterns:
    - "Absence gate paired with a non-vacuity control search (git grep for a deleted symbol, plus a grep for a sibling symbol known to survive) so a search that read nothing cannot be mistaken for one that found nothing"
    - "Computed-set-difference substitution: pick a docstring's replacement example by evaluating the two live literals in-session (_HANDLER_FUNCTION_NAMES minus _EXPECTED_DEV_TEST_REFERENCED_HELPERS) rather than trusting a name proposed in research/patterns docs"

key-files:
  modified:
    - firestarter_app/firestarter/cli_handlers.py
    - firestarter_app/tools/check_devtest_orchestrator.py
    - firestarter_app/tests/test_check_devtest_orchestrator.py
    - firestarter_app/tests/test_numeric_schema_source_scan.py

key-decisions:
  - "Chose _verdict_code as the subset-vs-equality rationale's replacement example over _overall_exit_code or dev_test -- it is a private helper called only indirectly (via _dev_test_exit_code), matching the property the rationale needs, and the file's own adjacent comment block (lines 544-552) already narrates its indirection history, so the substitution reads as a natural continuation of the existing prose rather than an arbitrary pick."
  - "Did NOT add a third supersession sentence naming the deleted symbol '_is_interactive' in prose (unlike the two existing supersession sentences that name their retired predecessors by name) -- Task 1's own absence gate requires git grep for the literal string '_is_interactive' to return zero tracked matches repo-wide, and a supersession sentence following the file's established pattern would have named it and self-failed the gate. First attempt did add such a sentence; caught by re-running the gate before committing (see Deviations)."
  - "Repaired the D-13 citation by deleting the '(build_db.py:594)' parenthetical outright rather than substituting the explicit 'a local variable nested inside a for loop deep in main()' phrase -- the very next clause in the same sentence already states the set literal is 'a LOCAL variable nested inside a for loop several indent levels deep', so inserting the longer form would have duplicated that statement moments later in the same sentence. Step 3 of the task explicitly names both forms as satisfying the requirement and asks for a choice with reasoning; this is that reasoning."

patterns-established: []

requirements-completed: [CLAIM-06, CLAIM-07]

coverage:
  - id: D1
    description: "Delete the dead _is_interactive TTY-check helper from cli_handlers.py together with all three dependents (allow-list entry, module-docstring enumeration, subset-vs-equality rationale) in one commit, leaving zero tracked references to the symbol anywhere in the app repo"
    requirement: CLAIM-07
    verification:
      - kind: other
        ref: "git grep -n _is_interactive (firestarter_app repo) -- exit 1, no output"
        status: pass
      - kind: other
        ref: "git grep -c _make_sampler -- firestarter/cli_handlers.py tools/check_devtest_orchestrator.py -- non-vacuity control, 2 and 4"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_check_devtest_orchestrator.py (.venv311, py3.11) -- 26 passed"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_dev_test_cmd.py (.venv311, py3.11) -- 63 passed"
        status: pass
      - kind: other
        ref: "ruff check firestarter/ tests/ && ruff format --check firestarter/ tests/"
        status: pass
      - kind: other
        ref: "check_mypy_watermark.py -- 35 errors, at watermark"
        status: pass
    human_judgment: false
  - id: D2
    description: "Replace the file-plus-line-number citation of _AT28C_DIP24_NAMES in test_numeric_schema_source_scan.py (build_db.py:594, stale -- the symbol has moved twice) with the symbol-and-scope form the same file already uses correctly, writing no replacement line number"
    requirement: CLAIM-06
    verification:
      - kind: other
        ref: "grep -cE '\\.py:[0-9]+' tests/test_numeric_schema_source_scan.py -- 0 (boundary: was 1, moves to exactly 0)"
        status: pass
      - kind: other
        ref: "grep -c _AT28C_DIP24_NAMES tests/test_numeric_schema_source_scan.py -- 2 (non-vacuity control)"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_numeric_schema_source_scan.py (.venv311, py3.11) -- 8 passed"
        status: pass
      - kind: other
        ref: "git diff --stat -- tests/test_numeric_schema_source_scan.py -- 1 insertion, 1 deletion"
        status: pass
    human_judgment: false
  - id: D3
    description: "App-repo gate sweep on the three touched test modules plus a whole-suite collection check, all run on the Python 3.11 venv app CI uses"
    verification:
      - kind: unit
        ref: "pytest tests/test_dev_test_cmd.py tests/test_check_devtest_orchestrator.py tests/test_numeric_schema_source_scan.py (.venv311) -- 97 passed"
        status: pass
      - kind: other
        ref: "pytest tests/ --collect-only -q -- 2359 tests collected, no ERROR"
        status: pass
      - kind: other
        ref: "ruff check + ruff format --check (firestarter/ tests/) -- clean; mypy watermark -- 35/35, mypy binary confirmed present"
        status: pass
    human_judgment: false

duration: 35min
completed: 2026-09-11
status: complete
---

# Phase 185 Plan 04: Dead-Symbol Deletion and Stale-Citation Repair Summary

**Deleted the `_is_interactive` TTY-check helper and all three of its dependents from `firestarter_app` in one commit, then replaced the one surviving file-plus-line-number docstring citation in `test_numeric_schema_source_scan.py` with the symbol-and-scope form the same file already uses correctly -- both proven by `git grep`/`grep` absence gates run on the app CI's Python 3.11 venv, with zero regressions across 2359 collected tests.**

## Performance

- **Duration:** 35 min
- **Started:** 2026-09-11T18:05:00Z
- **Completed:** 2026-09-11T18:40:00Z
- **Tasks:** 3 completed (2 code tasks + 1 verification-only sweep)
- **Files modified:** 4 (all inside `firestarter_app`)

## Accomplishments

- Deleted `_is_interactive()` -- its `def`, docstring and `return sys.stdin.isatty()` body -- from `firestarter/cli_handlers.py`. Confirmed `sys` remains used elsewhere in the module (14+ other `sys.exit(...)` call sites), so the import stays; `ruff check` confirms no unused-import diagnostic.
- Removed the symbol's entry from the `_HANDLER_FUNCTION_NAMES` frozenset in `tools/check_devtest_orchestrator.py`, and separately removed it from that same file's module-docstring prose enumeration (line 66) -- a site CONTEXT.md's D-07 does not name, found during research, and one that no CI gate would have caught since `tools/` sits outside `ruff`/`mypy`/`pytest --cov` entirely.
- Repaired the subset-vs-equality rationale in `tests/test_check_devtest_orchestrator.py` by computing the true set difference in-session (`_HANDLER_FUNCTION_NAMES` minus `_EXPECTED_DEV_TEST_REFERENCED_HELPERS`, both read live via `importlib`) and substituting `_verdict_code` for the deleted symbol as the listed-but-only-indirectly-referenced example.
- Replaced the stale `(build_db.py:594)` citation in `tests/test_numeric_schema_source_scan.py` with no replacement number, confirming from source (not from any document) that `_AT28C_DIP24_NAMES` is a set literal, a local variable nested inside a `for` loop deep inside `main()` at `tools/build_db.py:538`.
- Ran the full app gate sweep (pytest on the three touched modules, whole-suite `--collect-only`, `ruff check`, `ruff format --check`, mypy watermark) on `.venv311` (Python 3.11.16) -- the version app CI actually uses, never the devcontainer's default 3.12.
- `git grep -n _is_interactive` over the whole `firestarter_app` tracked tree returns nothing (exit 1) -- the symbol has zero tracked references anywhere in the repo.

## Task Commits

Each code task was committed atomically, inside the `firestarter_app` submodule (branch `gsd/v1.37-operator-safety-answered-reports-claim-hygiene`):

1. **Task 1: Delete the dead TTY-check helper and all three of its dependents, in one commit** - `c40e4af` (fix) -- `firestarter/cli_handlers.py`, `tools/check_devtest_orchestrator.py`, `tests/test_check_devtest_orchestrator.py`
2. **Task 2: Replace the file-plus-line-number citation with the symbol-and-scope form** - `bffbba8` (docs) -- `tests/test_numeric_schema_source_scan.py`

Task 3 (app-repo gate sweep) modified no file and produced no commit -- it is a verification-only pass; `git status --short` inside `firestarter_app` after Task 3 shows only two pre-existing, unrelated untracked operator PDFs (`datasheets/MBM27C1001.pdf`, `datasheets/MX27C4000.pdf`), confirmed not to be part of this plan's scope.

**Plan metadata:** this SUMMARY commit (meta repo, `.planning/` only -- the `firestarter_app` gitlink is intentionally NOT staged; plan 185-06 advances it by name)

## Files Created/Modified

- `firestarter_app/firestarter/cli_handlers.py` - `_is_interactive()` (def, docstring, body) deleted; `sys` import retained (still used elsewhere)
- `firestarter_app/tools/check_devtest_orchestrator.py` - `_HANDLER_FUNCTION_NAMES` frozenset entry and module-docstring enumeration both no longer name the deleted symbol
- `firestarter_app/tests/test_check_devtest_orchestrator.py` - subset-vs-equality rationale repaired by name substitution (`_verdict_code` replaces `_is_interactive`), no new paragraph authored
- `firestarter_app/tests/test_numeric_schema_source_scan.py` - stale `(build_db.py:594)` parenthetical deleted; the surrounding sentence's existing scope clause stands unchanged

## Step 0 — `git grep` enumeration (Task 1, before any edit)

```
$ git grep -n _is_interactive   # inside firestarter_app
firestarter/cli_handlers.py:2328:def _is_interactive() -> bool:
firestarter/cli_handlers.py:2333:    survive; patching `firestarter.cli_handlers._is_interactive` does.
tests/test_check_devtest_orchestrator.py:585:    `_is_interactive` is legitimately listed but not referenced from
tools/check_devtest_orchestrator.py:66:`_is_interactive`, `_make_sampler` -- `_HANDLER_FUNCTION_NAMES` below), i.e.
tools/check_devtest_orchestrator.py:163:        "_is_interactive",
```

Exactly the three files the plan names (`cli_handlers.py`, `check_devtest_orchestrator.py` twice, `test_check_devtest_orchestrator.py`) -- **`tests/test_dev_test_cmd.py` is ABSENT from this list**, confirming plan 185-03's severance was complete and this deletion is safe.

`git grep` was used rather than a bare `grep`, because this devcontainer's `grep` is ugrep and honors `.gitignore` (silently under-scanning), and because `firestarter_app/build/lib/firestarter/cli_handlers.py` is a gitignored, untracked stale sdist artefact that still contains the symbol three times (`git check-ignore -v` confirms `.gitignore:3:build/`). `git grep` scans tracked files only and is immune to both traps at once. That build artefact was not touched, not deleted, and is not reported as a surviving reference.

Pre-edit comment-line (`^\s*#`) counts, matching the plan's recorded baseline exactly: `firestarter/cli_handlers.py` 324, `tools/check_devtest_orchestrator.py` 91, `tests/test_check_devtest_orchestrator.py` 98. All three counts are unchanged after the edit (confirmed post-edit, see Verification below).

## Computed Set Difference (Task 1, Step 4)

Read live via `importlib` after Step 2's deletion:

```
_HANDLER_FUNCTION_NAMES (10, after deletion):
  _canonical_part_number, _chip_id_fields, _cli_start_time, _dev_test_exit_code,
  _is_uv_eprom, _make_sampler, _overall_exit_code, _sanitize_chip_token,
  _verdict_code, dev_test

_EXPECTED_DEV_TEST_REFERENCED_HELPERS (7):
  _canonical_part_number, _chip_id_fields, _cli_start_time, _dev_test_exit_code,
  _is_uv_eprom, _make_sampler, _sanitize_chip_token

listed-but-not-body-referenced (the difference, 3 members):
  _overall_exit_code, _verdict_code, dev_test
```

This matches 185-RESEARCH.md §B.5's independently-computed "after the deletion" set exactly. **Chosen replacement: `_verdict_code`.** It keeps the subset direction correct because it is a private helper (`dev_test` is the public entry point itself, not a private co-located helper, so a weaker fit for "helper" in the rationale's own wording) that is listed in `_HANDLER_FUNCTION_NAMES` and called only *indirectly* -- from `_dev_test_exit_code`'s body, per the file's own adjacent comment block (lines 544-552) narrating the `_verdict_code` -> `_overall_exit_code` -> `_dev_test_exit_code` indirection history. An equality assertion between the two sets would still be red on day one because of this member (and the other two), so the subset assertion's reason for existing is unchanged.

## Before/After of the Repaired Rationale Sentence (Task 1, Step 4)

**Before:**
> The assertion here is a SUBSET, never an equality, because `_is_interactive` is legitimately listed but not referenced from `dev_test`'s body -- an equality assertion would be red for the opposite reason on day one.

**After:**
> The assertion here is a SUBSET, never an equality, because `_verdict_code` is legitimately listed but not referenced from `dev_test`'s body directly -- `_dev_test_exit_code` calls it internally instead, mirroring `_overall_exit_code`'s own shape above -- an equality assertion would be red for the opposite reason on day one.

No new paragraph was authored; this is a name substitution inside the existing sentence, with a short indirection clause added inline (matching the file's own established practice of stating *why* an example is only-indirectly-referenced, as the two prior supersession sentences already do for `_default_uv_write_confirm` and `_is_uv_eprom`).

## Task 2 — Step 1/Step 2 Evidence

**Step 1 (grep before edit):**
```
$ /usr/bin/grep -nE "\.py:[0-9]+" tests/test_numeric_schema_source_scan.py
40:     on `_AT28C_DIP24_NAMES` (build_db.py:594) -- that set literal (not
```
Exactly one matching line, as the plan's boundary states.

**Step 2 (source lookup, this session, not from any document):**
```
$ /usr/bin/grep -n "_AT28C_DIP24_NAMES" tools/build_db.py
538:                _AT28C_DIP24_NAMES = {
557:                if _chip_aliases & _AT28C_DIP24_NAMES:
$ /usr/bin/grep -n "^def " tools/build_db.py
185:def resolve_pinout_key(
285:def classify(...)
368:def interpret_timing(...)
398:def main():
```
Read `tools/build_db.py:525-560` directly: `_AT28C_DIP24_NAMES` is a **set literal** (`{...}` of string names, not a dict), assigned at 16-space indentation, inside a `for` loop, inside `def main():` (line 398) -- confirming it is exactly the local-variable/`for`-loop/`main()` scope the file's other correct citation (`_top_level_dict_constant_names`'s docstring, lines 122-134) already describes. The line the symbol currently sits at (538) was deliberately NOT transcribed into the file, matching D-13's point: the citation has staled three times (from three different prior figures, none reproduced here) and the requirement's own figure staled within a day of being authored, so writing any number -- including today's correct one -- would stale again on the next edit.

**Chosen repair form:** outright deletion of the `(build_db.py:594)` parenthetical, not the explicit `"a local variable nested inside a for loop deep in main()"` substitution. Reason: the very next clause in the same sentence already states *"that set literal (not even a Dict) is a LOCAL variable nested inside a `for` loop several indent levels deep"* -- inserting the longer explicit form immediately before that clause would have stated the same fact twice in one sentence. Deletion reads cleanly and Step 3 of the task names this as an equally-valid option.

## Decisions Made

See `key-decisions` in the frontmatter for the three substantive decisions (replacement-example choice, omitting a supersession sentence naming the deleted symbol, and the citation-repair form choice). All three are also captured inline above with full reasoning.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug in own first-draft edit] Initial repair of the subset-vs-equality rationale added a third supersession sentence that itself named the literal string `_is_interactive`, self-failing Task 1's own absence gate**
- **Found during:** Task 1, Step 4, before the first commit (re-running the plan's `<verify>` gates prior to committing)
- **Issue:** The task's Step 4 text explicitly permits "a third such sentence" matching the file's established supersession pattern (the existing sentences name their retired predecessors, e.g. "`_default_uv_write_confirm` used to be the other such entry..."). Following that pattern literally, the first draft added: "`_is_interactive` used to be the fourth such entry; Phase 185 plan 04 deleted it along with the dead TTY-check helper it named." This is textually consistent with the file's own style, but it writes the literal string `_is_interactive` into a tracked file -- directly contradicting Task 1's `<verify>` gate 1 (`git grep -n _is_interactive` must print nothing) and the plan's core must_have ("no tracked reference anywhere").
- **Fix:** Removed the added supersession sentence entirely, leaving only the direct name substitution in the primary sentence (which uses `_verdict_code`, not the deleted name). Re-ran `git grep -n _is_interactive` -- confirmed exit 1, no output -- before proceeding to any other verification or the commit.
- **Files modified:** `firestarter_app/tests/test_check_devtest_orchestrator.py` (same file, corrected before commit -- no separate commit for this correction; the committed version already reflects the fix)
- **Verification:** `git grep -n _is_interactive` (firestarter_app) -- exit 1, zero output, confirmed both before and after `ruff format`
- **Committed in:** `c40e4af` (the correction was made before the task's single commit, not as a follow-up commit)

---

**Total deviations:** 1 auto-fixed (Rule 1, caught by the plan's own verify gate before committing, not shipped).
**Impact on plan:** None on the shipped state -- the error was caught and corrected within the same task, before any commit. It is documented here because a plan or executor following the same textual pattern ("name the retired predecessor") on a *different* deleted symbol, without also checking that deletion's own absence gate, would reproduce this exact self-inflicted failure. The general lesson: when a docstring pattern says "name what used to be here," and a plan's own gate demands the removed name have zero tracked occurrences, the pattern and the gate are in direct tension -- the gate wins, and the supersession-sentence convention must be skipped for that specific symbol.

## Issues Encountered

None beyond the one self-caught deviation documented above.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- `firestarter_app` (tracked files) now has zero references to `_is_interactive` anywhere -- CLAIM-07 is fully satisfied across both 185-03 (test side) and 185-04 (source side).
- `tests/test_numeric_schema_source_scan.py` now has zero file-plus-line-number citations -- CLAIM-06's boundary criterion (exactly zero, not "fewer") is met.
- All app gates (`pytest` on the three touched modules at 97 passed, whole-suite `--collect-only` at 2359 collected with no ERROR, `ruff check`, `ruff format --check`, mypy watermark at 35/35) are green on `.venv311` (Python 3.11.16), the exact version app CI uses.
- `firestarter/submit.py` and `firestarter/jp5_gate.py` do not appear in either task's diff -- the two real TTY readers were not touched.
- The `firestarter_app` gitlink was intentionally left unstaged in the meta repo per this plan's orchestrator constraints; plan 185-06 advances it by name.
- No blockers for plan 185-06.

---
*Phase: 185-records-and-checks-that-are-current*
*Completed: 2026-09-11*
