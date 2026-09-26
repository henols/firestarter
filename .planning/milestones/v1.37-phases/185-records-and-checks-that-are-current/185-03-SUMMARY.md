---
phase: 185-records-and-checks-that-are-current
plan: 03
subsystem: testing
tags: [pytest, click, cli-testing, tty-gating, dead-code-removal]

requires: []
provides:
  - "test_dev_test_cmd.py with zero references to the _off_tty() forcing helper or the _is_interactive symbol"
  - "no test name in the module claiming an on-TTY/off-TTY behavioural distinction that the test does not perform"
affects: [185-04]

actuals:
  tokens: 7562
  tasks: 2
  commits: 2

tech-stack:
  added: []
  patterns:
    - "Scripted line-range transform (not sed, not hand edits) for a 46-site block-dedent, verified by a count gate plus a manual read-back of 6+ transformed sites, because a mis-dedent leaves the test suite green"

key-files:
  modified:
    - firestarter_app/tests/test_dev_test_cmd.py

key-decisions:
  - "Handled the 5 multi-context ('with (...)') sites by direct, individually-verified text edits (not the generic script), since there are only 5 and each has a distinct shape; the generic scripted transform was reserved for the 46 uniform sole-context-manager sites, which is where a hand-edit mistake is both likely and undetectable by a green suite."
  - "Chose test_no_uv_write_prompt_surface_exists and test_uv_part_writes_one_slot as the two renamed/merged names, per the plan's own flagged_assumptions that the exact wording is the planner's/executor's call, not a measured constraint -- the binding property (no surviving name claims TTY gating) is what was verified."
  - "Left test_submit_off_tty_end_to_end_never_opens_browser_or_runs_gh (TestSubmitReport, pre-existing, out of scope) untouched: its name contains the substring '_off_tty' but not the '_on_a_tty'/'_off_a_tty' pattern CLAIM-07's git-grep gate checks, it makes no TTY vs non-TTY behavioural claim (CliRunner is always off-TTY), and it is not named anywhere in CONTEXT.md/RESEARCH.md's scope for this plan."
  - "Left the 'Coverage (post-121-09)' docstring bullet ('a UV part on a TTY is asked... a UV part off a TTY never asks') untouched: it predates this plan (the prompt itself, Confirm/_default_uv_write_confirm, was already retired in an earlier phase per test_no_uv_write_prompt_surface_exists's own assertion), so its staleness is pre-existing and out of this plan's declared scope (module docstring lines 8-14 only)."

patterns-established:
  - "Pattern: when a plan's own <verify> grep gate encodes an assumption about file structure (e.g. 1 test-def-line per collected test item), re-derive the gate's true baseline in Step 0 before trusting the plan's asserted expected count, and use the pytest-collected count (not a def-line grep) as the authoritative non-vacuity proof when the two diverge."

requirements-completed: [CLAIM-07]

coverage:
  - id: D1
    description: "Delete the _off_tty() helper and unwrap all 51 of its call sites in test_dev_test_cmd.py (46 sole-context-manager dedents, 5 multi-context collapses/trims), behaviour-neutral because CliRunner.invoke already forces a non-TTY stdin"
    requirement: CLAIM-07
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_dev_test_cmd.py (full module, .venv311/bin/python -m pytest -o addopts=\"\" -q) -- 64 passed, run twice"
        status: pass
      - kind: other
        ref: "ruff format --check firestarter/ tests/ && ruff check firestarter/ tests/ (py3.11 venv)"
        status: pass
    human_judgment: false
  - id: D2
    description: "Merge the redundant UV slot-write test pair into one survivor, rename the structural misnomer, and drop the last direct _is_interactive patch + its stale docstring clause -- no test name in the module claims TTY gating, and the module has zero remaining references to _is_interactive"
    requirement: CLAIM-07
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_dev_test_cmd.py (full module, .venv311/bin/python -m pytest -o addopts=\"\" -q) -- 63 passed"
        status: pass
      - kind: other
        ref: "git grep -nE 'def test_.*_(on|off)_a_tty' -- tests/ (exit 1, no match); git grep -n _is_interactive -- tests/test_dev_test_cmd.py (no match)"
        status: pass
    human_judgment: false

duration: 45min
completed: 2026-09-11
status: complete
---

# Phase 185 Plan 03: Off-TTY Unwrap and UV Slot-Write Test Merge Summary

**Removed the `_off_tty()` forcing helper and all 51 of its call sites from `test_dev_test_cmd.py`, merged the redundant on/off-TTY UV slot-write test pair into one honestly-named survivor, and dropped the module's last two false TTY-gating claims -- the suite count moved 64 -> 64 -> 63, exactly as predicted, with zero references to the symbol Plan 185-04 deletes.**

## Performance

- **Duration:** 45 min
- **Started:** 2026-09-11T17:14:00Z
- **Completed:** 2026-09-11T17:59:00Z
- **Tasks:** 2 completed
- **Files modified:** 1 (`firestarter_app/tests/test_dev_test_cmd.py`)

## Accomplishments

- Deleted the `_off_tty()` context-manager helper and unwrapped all 51 of its call sites (46 sole-context-manager dedents via a scripted transform, 5 multi-context sites collapsed/trimmed by individually-verified hand edits) -- `64 passed` before and after, proving the change is behaviour-neutral (D-05).
- Deleted the module docstring's false clause claiming TTY-gating is controlled by patching `_is_interactive` directly -- the surrounding sentence reads correctly with no replacement prose added.
- Renamed `test_no_prompt_on_a_uv_part_even_on_a_tty` (a pure misnomer -- it performs zero TTY work) to `test_no_uv_write_prompt_surface_exists`, body and assertions unchanged.
- Merged `test_uv_part_writes_one_slot_on_a_tty` and `test_uv_part_writes_one_slot_off_a_tty_too` -- byte-identical assertions once the `_is_interactive` patch was inert -- into one survivor, `test_uv_part_writes_one_slot`, carrying the `write-partial` membership assertion.
- Dropped the last direct `patch("firestarter.cli_handlers._is_interactive", ...)` from `test_non_uv_part_is_still_written_in_full_without_a_prompt` and its docstring's "TTY or not" clause -- the test's own name carried no TTY claim, so it keeps its name.
- Confirmed the module now has zero references to `_is_interactive` (verified with `git grep`, immune to the ugrep `.gitignore` under-scan and the untracked `build/lib/` decoy) -- the precondition Plan 185-04 needs before it can delete the symbol.

## Task Commits

Each task was committed atomically, inside the `firestarter_app` submodule (branch `gsd/v1.37-operator-safety-answered-reports-claim-hygiene`):

1. **Task 1: Unwrap all 51 off-TTY sites, delete the helper, delete the false docstring clause** - `acc864f` (test)
2. **Task 2: Merge the UV slot-write pair, rename the misnomer, drop the last patch** - `6ad671c` (test)

**Plan metadata:** this SUMMARY commit (meta repo, `.planning/` only -- the `firestarter_app` gitlink is intentionally NOT staged; Plan 185-06 advances it by name)

## Files Created/Modified

- `firestarter_app/tests/test_dev_test_cmd.py` - `_off_tty()` helper and all 51 uses removed; module docstring's TTY-gating clause removed; `TestUVWriteHasNoPrompt` now has 3 members (was 4) with no TTY-claiming names; zero remaining `_is_interactive` references

## Decisions Made

- **Hybrid transform strategy.** The 5 multi-context sites (2 collapse-to-single-CM "shape B", 1 keep-parenthesized "shape C", 2 collapse "shape D") were handled by direct, individually-read-and-verified text edits rather than folding them into the generic script -- there are only 5, each shape is distinct, and hand-verifying 5 sites against their exact surrounding text is safer than adding shape-detection branches to a script that only needs to handle 46 uniform cases. The 46 sole-context-manager sites went through a single scripted transform (Python, operating on the line list, dedenting by exactly 4 spaces until a line at or below the `with` line's own indentation) -- never `sed`, never hand edits.
- **Chosen names.** Per the plan's own `flagged_assumptions`, the exact wording of the rename/merge survivor names was left to executor discretion, with only the "no TTY claim" property binding. Used `test_no_uv_write_prompt_surface_exists` and `test_uv_part_writes_one_slot`.
- **Two docstring passages left deliberately untouched**, both out of this plan's declared scope:
  - `TestUVWriteHasNoPrompt`'s class docstring -- a past-tense historical account of the retired UV write prompt, not a live claim (kept byte-for-byte identical, confirmed by diff).
  - The module's "Coverage (post-121-09)" bullet describing a TTY-gated ask/no-ask UV write distinction that no longer exists in the code (the ask itself, `Confirm`/`_default_uv_write_confirm`, was retired in an earlier phase, predating this plan) -- its staleness predates this plan and the plan's Step 2 named only the module docstring's lines 8-14, not this bullet.
- **`test_submit_off_tty_end_to_end_never_opens_browser_or_runs_gh` left unrenamed.** Its name contains the substring `_off_tty` (colliding with the Task 1 verify gate's unfiltered grep, see Deviations) but not the `_(on|off)_a_tty` pattern CLAIM-07's success criterion targets, and it makes no TTY-vs-non-TTY behavioural claim -- CliRunner is always off-TTY, so there is no distinction to misname. Not flagged by CONTEXT.md, RESEARCH.md, or this plan's task list.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - plan verify-gate defect] `def test_` grep count assumed a 1:1 test-def-to-collected mapping that this file does not have**
- **Found during:** Task 1, Step 0 baseline capture
- **Issue:** The plan's Task 1 and Task 2 `<verify>` blocks include `grep -c 'def test_' tests/test_dev_test_cmd.py` with `fails_when the printed count is not 64` (Task 1) / `not 63` (Task 2), presented as "the non-vacuity control ... the same figure as before this task." The file has 3 `@pytest.mark.parametrize`-decorated test functions (with 3, 2, and 3 parameter sets respectively), so pytest's collected/passed count (64, matching the plan's and RESEARCH's own baseline) and the raw `def test_` line count are NOT the same number: measured baseline (before any edit in this plan) was **59**, not 64.
- **Fix:** Treated the plan's Step 0 collected-test-count (64, from `--collect-only`) as the authoritative baseline per the plan's own text (it is what Step 0 explicitly lists), and used the `def test_` grep only as a secondary, correctly-scoped control against its own true baseline: 59 after Task 1 (unchanged -- no function added or removed), 58 after Task 2 (exactly -1, matching the merge that removes one function definition). Both are consistent with the plan's intended proof (unchanged through Task 1, exactly one function removed through Task 2); only the absolute numbers in the plan's `fails_when` clauses were wrong.
- **Files modified:** None (test-authoring behavior unaffected; this is a reading/interpretation adjustment of the plan's own verify gate, not a code change)
- **Verification:** `--collect-only -q -o addopts=""` = 64 (pre-task and post-Task-1) / 63 (post-Task-2), matching every acceptance criterion that cites the pytest-collected figure; `grep -c 'def test_'` = 59 (pre-task, post-Task-1) / 58 (post-Task-2), self-consistent with the -1 merge delta
- **Recorded in ledger:** `.planning/WINDOWS.md` entry #4 (kind: deviation)

**2. [Rule 1 - plan verify-gate defect] `grep -c '_off_tty'` (unfiltered, no parens) collides with an unrelated pre-existing test name**
- **Found during:** Task 1, final verify pass
- **Issue:** The plan's Task 1 `<verify>` block runs `grep -c '_off_tty' tests/test_dev_test_cmd.py` expecting exactly `0`. After the full unwrap and helper deletion, this grep returns `1`, not `0` -- but the one surviving match is `test_submit_off_tty_end_to_end_never_opens_browser_or_runs_gh` (line 1252 post-transform), a pre-existing test name (confirmed present, at line 1283, in the pre-transform backup taken before any edit in this plan) that has nothing to do with the deleted `_off_tty()` helper or any of its 51 call sites -- it is a substring collision only. RESEARCH.md's own baseline measurement for this exact property used the parenthesized pattern `_off_tty()` (52 -> 0), not the bare substring.
- **Fix:** Verified the true zero-survivor gate with `grep -c '_off_tty()'` (parenthesized, matching RESEARCH §B.1's own baseline pattern), which reads `0`. Confirmed via diff against the pre-transform backup that `test_submit_off_tty_end_to_end_never_opens_browser_or_runs_gh` is unmodified and pre-existing -- not a survivor of this plan's deletion, and not in scope to rename (its name matches neither the `_(on|off)_a_tty` pattern nor makes a TTY-vs-non-TTY claim).
- **Files modified:** None
- **Verification:** `grep -c '_off_tty()' tests/test_dev_test_cmd.py` = 0; `grep -n '_off_tty' tests/test_dev_test_cmd.py` shows only the one pre-existing test name, confirmed present at a different line number in the pre-transform backup
- **Recorded in ledger:** `.planning/WINDOWS.md` entry #5 (kind: deviation)

---

**Total deviations:** 2 auto-resolved (both Rule 1, both about the plan's own `<verify>` gate wording, neither about the code under test).
**Impact on plan:** No scope creep, no code behavior affected. Both are documented so a future re-run of this plan's literal verify commands is not misread as a regression -- the underlying properties (behaviour-neutral 64 -> 64, exactly one function removed in the merge, zero references to `_off_tty()`/`_is_interactive`) were all independently confirmed correct.

## Baseline Counts (Step 0, before any edit in this plan)

| Metric | Value |
|---|---|
| Collected/passed test count (`--collect-only`/`pytest`) | 64 |
| `_off_tty()` call-line count (51 uses + 1 `def` line) | 52 |
| Sole-context-manager `with _off_tty():` sites | 46 |
| Bare multi-context `_off_tty(),` lines | 5 |
| `#` comment lines | 216 |
| `def test_` line count (informational; not 1:1 with collected count -- see Deviation 1) | 59 |

## Counts After Task 1

| Metric | Value |
|---|---|
| Collected/passed (run twice) | 64 passed, 64 passed |
| `_off_tty()` (parenthesized) | 0 |
| `_off_tty` (bare substring; 1 pre-existing unrelated test name, see Deviation 2) | 1 |
| Residual single-item parenthesized `with (X,):` | 0 |
| `ruff format --check` / `ruff check` | clean / clean |
| `#` comment lines | 216 (unchanged) |
| `def test_` line count | 59 (unchanged) |

## Counts After Task 2

| Metric | Value |
|---|---|
| Collected/passed | 63 passed |
| `_is_interactive` (in this file) | 0 |
| `write-partial` string occurrences | 4 |
| `git grep -nE 'def test_.*_(on\|off)_a_tty' -- tests/` | no match, exit 1 |
| `ruff format --check` / `ruff check` | clean / clean |
| `#` comment lines | 216 (unchanged) |
| `def test_` line count | 58 (-1, the merge) |

## Transform Script (Task 1, scratchpad-only, never committed)

Written to `/tmp/claude-1000/-workspaces/fe4749e7-556c-429b-96c8-5ffb2f76695b/scratchpad/unwrap_off_tty.py`, run once against the working copy after the 5 multi-context sites were hand-fixed:

```python
import re
import sys

path = "tests/test_dev_test_cmd.py"
with open(path) as f:
    lines = f.readlines()

out = []
i = 0
n = len(lines)
unwrapped_sites = []

while i < n:
    line = lines[i]
    m = re.match(r"^(\s*)with _off_tty\(\):\s*$", line)
    if m:
        indent = m.group(1)
        with_line_no = i + 1  # 1-based, pre-transform
        i += 1
        body_start = i
        body_end = i
        # Body: consecutive lines that are either blank or indented MORE than `indent`
        while body_end < n:
            candidate = lines[body_end]
            if candidate.strip() == "":
                body_end += 1
                continue
            candidate_indent = candidate[: len(candidate) - len(candidate.lstrip(" "))]
            if len(candidate_indent) > len(indent):
                body_end += 1
                continue
            break
        block = lines[body_start:body_end]
        dedented = []
        for bline in block:
            if bline.strip() == "":
                dedented.append(bline)
            else:
                if not bline.startswith(indent + "    "):
                    raise SystemExit(
                        f"UNEXPECTED INDENT at pre-transform line {body_start + 1}: {bline!r}"
                    )
                dedented.append(bline[4:])
        out.extend(dedented)
        unwrapped_sites.append((with_line_no, body_start + 1, body_end))
        i = body_end
        continue
    out.append(line)
    i += 1

with open(path, "w") as f:
    f.writelines(out)

print(f"Unwrapped {len(unwrapped_sites)} sole 'with _off_tty():' sites")
for s in unwrapped_sites:
    print(s)
```

Result: **46 sites unwrapped**, one with a 3-line body (pre-transform lines 764-767), the rest single-line bodies. Combined with the 5 hand-fixed multi-context sites, the shape counts sum to the measured **51**:

| Shape | Count | Handling |
|---|---|---|
| A (sole CM, dedent block) | 46 | scripted transform |
| B (first of two, collapses) | 2 | hand edit (pre-transform lines 950, 1275) |
| C (first of three, keeps parenthesized form) | 1 | hand edit (pre-transform line 1302) |
| D (not first, survivor collapses) | 2 | hand edit (pre-transform lines 1966, 2183) |
| **Total** | **51** | |

## Read-Back Sites (Step 4 spot-check)

Six sites read back after the transform and `ruff format`, confirming the assertions that followed each `with` block remained inside the same test function at the correct indentation:

1. **Line 928** (shape B collapse, `patch.dict(os.environ, ...)`) -- `result = runner.invoke(...)` and the following 3 asserts remain inside `test_report_goes_to_the_config_dir_reports_directory`.
2. **Line 1240** (shape B collapse, `patch("firestarter.submit.submit_report")`) -- `result = runner.invoke(...)` and the following 5 lines remain inside `test_every_run_calls_submit_report_once`.
3. **Line 1906** (shape D collapse, `patch("firestarter.cli_handlers.run_plan", ...)`) -- `runner.invoke(...)` and the following report-absence assert remain inside `test_keyboard_interrupt_mid_run_plan_leaves_no_report`.
4. **Line 2111** (shape D collapse, multi-line `patch("firestarter.chip_test.resolve_chip", ...)`) -- `result = runner.invoke(...)` and the following step-verdict asserts remain inside the R3 laundering-route test.
5. **Line 561** (shape A, near top of file) -- `result = runner.invoke(...)` at module-function indentation (4 spaces) with the following URL-exclusion assertions intact, inside `test_dev_test_output_trim_console_shrunk_payload_intact`.
6. **Line 2216** (shape A, near bottom of file) -- `result = runner.invoke(...)` at class-method indentation (8 spaces) with the following step-lookup assertions intact, inside `test_erasable_chip_blank_only_after_erase_exits_0`.

Both full-module runs (`-x -q`, run twice) reported `64 passed` identically.

## Merged Pair -- Side-by-Side (Task 2)

Both bodies, after Task 1's unwrap made the `_is_interactive` patch inert, were byte-identical except for the patch wrapper and docstring:

```python
# test_uv_part_writes_one_slot_on_a_tty (deleted)      # test_uv_part_writes_one_slot_off_a_tty_too (survivor, renamed)
operator = make_clean_operator()                        operator = make_clean_operator()
app = make_app_context(                                  app = make_app_context(
    eprom_operator=operator, hardware_manager=make_hardware_manager()
)                                                          )
result = runner.invoke(cli, ["dev", "test", _CHIP_UV], obj=app)   result = runner.invoke(cli, ["dev", "test", _CHIP_UV], obj=app)
assert result.exit_code in (0, 1, 2), result.output       assert result.exit_code in (0, 1, 2), result.output
data = _load_report(_CHIP_UV)                             data = _load_report(_CHIP_UV)
assert "write-partial" in {s["op"] for s in data["steps"]}   assert "write-partial" in {s["op"] for s in data["steps"]}
```

Identical bodies confirm this is a genuine merge, not a deletion -- no assertion was lost, and the `write-partial` grep count (4) confirms the survivor still carries the membership assertion.

## Issues Encountered

None beyond the two plan verify-gate deviations documented above.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- `test_dev_test_cmd.py` now has zero references to `_off_tty()`/`_is_interactive` -- Plan 185-04's deletion of the `_is_interactive` symbol from `firestarter/cli_handlers.py` is unblocked on the test side.
- No blockers. This plan shared no file with 185-01/185-02 (firmware) and ran independently.
- The `firestarter_app` gitlink was intentionally left unstaged in the meta repo per this plan's orchestrator constraints; Plan 185-06 advances it by name.

---
*Phase: 185-records-and-checks-that-are-current*
*Completed: 2026-09-11*
