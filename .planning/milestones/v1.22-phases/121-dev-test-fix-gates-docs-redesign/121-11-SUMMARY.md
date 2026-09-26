---
phase: 121-dev-test-fix-gates-docs-redesign
plan: 11
subsystem: cli
tags: [gh-cli, submission-flow, dedup, github-issues, pytest]

# Dependency graph
requires:
  - phase: 121-09
    provides: submit_report reached unconditionally on every dev test run (the call site this plan's internal logic builds on)
provides:
  - "find_prior_report(fingerprint, *, run_fn) -- read-only gh issue list dedup query distinguishing duplicate/no-duplicate/check-could-not-run by parsed JSON payload, never exit code alone"
  - "comment_via_gh(issue_url, body, *, run_fn, console) -- permission-independent gh issue comment with an explicit --repo and --body-file - on stdin"
  - "submit_report's restructured step order: refuse-gate -> sanitize+build -> dedup query (before any ask) -> off-TTY (dedup outcome included) -> the ask (every interactive run, never defaulted to decline) -> dispatch (comment-on-duplicate or create-on-new)"
  - "a deny-set negative-argv suite covering both gh paths' short forms (DEVTEST-06, RESEARCH Pitfall 6), with a live deliberate-break proof"
affects: [121-12, 121-13, 121-14, 122]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Injected keyword-only find_prior_report_fn/comment_via_gh_fn seams defaulted to the real implementations, matching submit.py's existing which_fn/run_fn/browser_open seam style"
    - "Deny-set (membership-absence) negative-argv assertions instead of equality-against-expected-list, so the assertion cannot silently stop protecting when someone edits the expected list"
    - "Three-signal dedup discrimination by parsed JSON payload, never by exit code alone (exit 0 covers both 'found' and 'not found')"

key-files:
  created: []
  modified:
    - firestarter_app/firestarter/submit.py
    - firestarter_app/tests/test_submit.py

key-decisions:
  - "find_prior_report wraps its run_fn call in try/except OSError so a real subprocess.run raising FileNotFoundError (gh entirely absent from PATH) folds into the same check-could-not-run branch as a non-zero returncode or unauthenticated exit -- discovered necessary while wiring the unconditional Step 3 call (Rule 1 fix, not in the plan's original action text)"
  - "submit_report's Step 3 dedup query runs unconditionally before the isatty branch, including off-TTY -- 'the check runs first' holds universally, not merely on an interactive run"
  - "On a duplicate, the ask is worded 'you appear to have already reported this' (hedged), never a certainty, per the eventually-consistent GitHub search-index limitation recorded in find_prior_report's docstring"
  - "A failed dedup check (gh absent/unauthenticated/offline) still asks the normal filing question, with an explicit could-not-run line, and the prompt default stays False (never nudged toward decline) exactly as the existing SUBMIT_REPO confirm already defaults"
  - "Existing TTY-dispatch tests in test_submit.py needed find_prior_report_fn injected as a Mock so their run_fn side_effect lists/call-count assertions stay accurate against the new unconditional dedup call -- without this, run_fn's dedup call would consume the first side_effect list item meant for gh auth status, breaking every fixed-sequence mock"

requirements-completed: [DEVTEST-05, DEVTEST-06]

coverage:
  - id: D1
    description: "find_prior_report distinguishes duplicate-found / no-duplicate / check-could-not-run strictly by parsed JSON payload (never exit code alone), degrades gracefully on malformed stdout or gh entirely absent from PATH, and its argv is a read-only list with no write-gated flag from either deny-set"
    requirement: "DEVTEST-05"
    verification:
      - kind: unit
        ref: "tests/test_submit.py::test_dedup_distinguishes_all_three_signals"
        status: pass
      - kind: unit
        ref: "tests/test_submit.py::test_dedup_query_argv_is_read_only"
        status: pass
    human_judgment: false
  - id: D2
    description: "submit_report runs the dedup query before any ask on every path (TTY or not), asks on every interactive run including when the check failed, and the off-TTY branch names the prior issue or states the check could not run without ever filing"
    requirement: "DEVTEST-05"
    verification:
      - kind: unit
        ref: "tests/test_submit.py::test_dedup_seam_invoked_before_confirm_fn_on_every_ask_path"
        status: pass
      - kind: unit
        ref: "tests/test_submit.py::test_dedup_check_failed_still_asks_and_prints_could_not_run_line"
        status: pass
      - kind: unit
        ref: "tests/test_submit.py::test_every_interactive_run_asks_even_when_the_check_fails"
        status: pass
      - kind: unit
        ref: "tests/test_submit.py::test_off_tty_names_existing_issue_when_duplicate_found"
        status: pass
      - kind: unit
        ref: "tests/test_submit.py::test_off_tty_prints_could_not_run_line_when_dedup_check_failed"
        status: pass
    human_judgment: false
  - id: D3
    description: "On a duplicate, the tester is offered a comment (sanitized body, permission-independent argv) carrying this run's evidence; decline sends nothing; a failed gh comment degrades to the browser tier pointed at the existing issue"
    requirement: "DEVTEST-05"
    verification:
      - kind: unit
        ref: "tests/test_submit.py::test_duplicate_found_asks_comment_question_and_dispatches_to_comment_on_yes"
        status: pass
      - kind: unit
        ref: "tests/test_submit.py::test_duplicate_comment_decline_does_not_comment"
        status: pass
      - kind: unit
        ref: "tests/test_submit.py::test_duplicate_comment_fails_falls_back_to_browser_on_existing_issue"
        status: pass
      - kind: unit
        ref: "tests/test_submit.py::test_comment_body_sent_is_sanitized"
        status: pass
    human_judgment: false
  - id: D4
    description: "Both gh paths' negative argv is asserted as a deny-set (not equality) covering long AND short forms: create-path label/assignee/milestone/project, comment-path delete-last/edit-last/yes/web/editor -- proven non-vacuous by a live deliberate-break test showing the pre-existing single-flag assertion would have missed the short -l form"
    requirement: "DEVTEST-06"
    verification:
      - kind: unit
        ref: "tests/test_submit.py::test_gh_create_argv_carries_no_permission_gated_flag (parametrised, 8 legs)"
        status: pass
      - kind: unit
        ref: "tests/test_submit.py::test_gh_comment_argv_carries_no_mutating_flag (parametrised, 7 legs)"
        status: pass
      - kind: unit
        ref: "tests/test_submit.py::test_gh_comment_argv_targets_the_project_wide_tracker"
        status: pass
      - kind: unit
        ref: "tests/test_submit.py::test_gh_comment_body_arrives_on_stdin"
        status: pass
    human_judgment: false

# Metrics
duration: 30min
completed: 2026-07-29
status: complete
---

# Phase 121 Plan 11: DEVTEST-05/06 -- dedup-first submission with a gh-comment path and a widened deny-set Summary

**`submit_report` now runs a read-only `gh issue list` dedup query before every ask (TTY or not), asks on every interactive run even when the check fails, offers a sanitized `gh issue comment` on a found duplicate, and both `gh` paths' negative argv is asserted as a deny-set covering short flag forms, proven non-vacuous by a live deliberate-break test.**

## Performance

- **Duration:** ~30 min
- **Completed:** 2026-07-29T21:33:00Z
- **Tasks:** 3
- **Files modified:** 2

## Accomplishments
- Added `find_prior_report(fingerprint, *, run_fn)` -- a `gh issue list --repo henols/firestarter_prom --author @me --search <fingerprint> --state all --json number,title,url --limit 5` query that distinguishes duplicate-found / no-duplicate / check-could-not-run strictly by the parsed JSON payload (exit 0 covers both "found" and "not found"), degrades to check-could-not-run on malformed stdout, an unexpected shape, or `gh` entirely absent from PATH (caught `OSError`), and never raises
- Added `comment_via_gh(issue_url, body, *, run_fn, console)` -- `gh issue comment <url> --repo <SUBMIT_REPO> --body-file -`, no mutating/hijacking flag ever sent, degrading with a spoken reason on failure exactly like `submit_via_gh`
- Restructured `submit_report` into refuse-gate -> sanitize+build -> dedup query (runs before any ask, on every path including off-TTY) -> off-TTY print (now naming the prior issue or stating the check could not run) -> the ask (every interactive run, a failed check still asks with an explicit line, never defaulted to decline) -> dispatch (comment-on-duplicate-yes with a browser-tier fallback on the existing issue, or the unchanged create/browser dispatch on a new report)
- Took `find_prior_report`/`comment_via_gh` as injected keyword-only seams (`find_prior_report_fn`/`comment_via_gh_fn`) defaulted to the real implementations, matching the module's existing `which_fn`/`run_fn`/`browser_open` seam style
- Widened the existing single-flag negative-argv idiom to a deny-set on both `gh` paths: create-path `-l`/`--label`, `-a`/`--assignee`, `-m`/`--milestone`, `-p`/`--project` (8 tokens); comment-path `--delete-last`, `--edit-last`, `--yes`, `-w`/`--web`, `-e`/`--editor` (7 tokens); plus a read-only assertion on the dedup query's own argv (no create/edit/comment/close/delete subcommand token, no write-gated flag from either deny-set)
- Executed the deliberate-break proof live: planted the short `-l` form (with a non-`gsd-inbox` label value, isolating exactly the flag-detection gap) into `submit_via_gh`'s argv, confirmed the new parametrized `-l` leg went RED while the pre-existing single-flag assertion (`test_submit_via_gh_argv_carries_nothing_permission_gated`) stayed GREEN -- concretely proving RESEARCH Pitfall 6 was a real hole -- then reverted and confirmed the full suite GREEN again (`git diff --stat` empty on `submit.py` afterward)
- Fixed 8 pre-existing TTY-dispatch tests whose `run_fn` side_effect lists/call-count assertions were broken by the new unconditional dedup call (the dedup query now consumes a `run_fn` call before the `gh auth status`/`gh issue create` sequence), by injecting `find_prior_report_fn=Mock(return_value=(None, True))` so those tests stay focused on their original concern

## Task Commits

Each task was committed atomically:

1. **Task 1: Add the dedup query and the comment path as injected-seam gh functions** - `c15972b` (feat)
2. **Task 2: Restructure submit_report's step order around dedup-first and always-ask** - `3769dc4` (refactor)
3. **Task 3: Widen the negative-argv assertion to a deny-set on both gh paths** - `4dd92d3` (test)

## Files Created/Modified
- `firestarter_app/firestarter/submit.py` - `find_prior_report`, `comment_via_gh`, restructured `submit_report` (dedup-first, always-ask, comment-on-duplicate)
- `firestarter_app/tests/test_submit.py` - 8 existing TTY-dispatch tests updated to inject `find_prior_report_fn`; 9 new Task 2 behavioural legs; 7 new Task 3 deny-set legs (2 parametrised, expanding to 15 collected items); module docstring coverage note

## Decisions Made
- `find_prior_report` catches `OSError` around its `run_fn` call so `gh` truly absent from PATH (as opposed to present-but-unauthenticated) folds into the same check-could-not-run branch as a non-zero returncode -- necessary because a real `subprocess.run(["gh", ...])` raises `FileNotFoundError` rather than returning a returncode when the binary is missing, and D-10 requires "gh absent" to ask-anyway just like the other two failure modes
- The dedup query is called unconditionally at Step 3, before the TTY branch -- so "the check runs first" (DEVTEST-05) holds on the off-TTY path too, not merely on an interactive run
- The duplicate-ask is worded "you appear to have already reported this" (hedged, never a certainty) per `find_prior_report`'s own documented limitation: GitHub's issue-search index is eventually consistent, so a just-filed issue may not yet be returnable by `--search`
- The prompt for a failed dedup check is never defaulted toward decline -- D-10 explicitly forbids nudging a first-time tester away from the report this milestone is asking for
- Deny-set (membership-absence) assertions were used throughout Task 3 rather than equality-against-an-expected-argv-list, per the plan's own instruction that an equality assertion silently stops protecting the moment someone updates the expected value

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] `find_prior_report` did not originally handle `gh` entirely absent from PATH**
- **Found during:** Task 1 (while reasoning through D-10's "gh absent" condition against a real, uninjected `subprocess.run`)
- **Issue:** A real `subprocess.run(["gh", ...])` raises `FileNotFoundError` (an `OSError` subclass) when `gh` is not on PATH at all -- it does not return an object with a non-zero `.returncode`. Without handling this, `find_prior_report` would crash the whole `dev test` sweep on a community tester's machine that never installed `gh`, rather than degrading to "the check could not run" as D-10 requires.
- **Fix:** Wrapped the `run_fn(...)` call in `try/except OSError: return None, False`, folding "gh absent" into the identical branch as "non-zero returncode" and "unauthenticated exit 4" -- the function never raises regardless of which of the three conditions produced the failure.
- **Files modified:** `firestarter_app/firestarter/submit.py`
- **Verification:** Full `tests/test_submit.py` suite green; the existing malformed-stdout/non-zero-returncode legs are unaffected since the new `except` clause sits strictly outside the parsing logic.
- **Committed in:** `c15972b` (Task 1 commit)

**2. [Rule 1 - Non-regression reconciliation] 8 pre-existing TTY-dispatch tests broke when Step 3's dedup call started consuming a `run_fn` invocation**
- **Found during:** Task 2, immediately after restructuring `submit_report`
- **Issue:** Several existing tests configured `run_fn` with a fixed `side_effect=[...]` list representing exactly `[gh auth status, gh issue create]`, and separately asserted `run_fn.call_count == 2` or `run_fn.assert_not_called()`. With the dedup query now calling `run_fn` unconditionally and first, those tests either raised `StopIteration` (the side_effect list exhausted one call early) or failed the `assert_not_called()`/count assertions outright.
- **Fix:** Injected `find_prior_report_fn=Mock(return_value=(None, True))` into each affected test so the dedup step is driven by a controlled stub rather than the real function calling `run_fn` -- exactly the seam-injection pattern the plan itself specifies ("Take `find_prior_report` and `comment_via_gh` as injected keyword-only seams ... so the tests can drive every branch without patching module internals"). This kept each test's original assertion intact and honest rather than passing by accident (one test, `test_tty_confirm_gh_create_fails_falls_back_to_browser`, was passing for the *wrong* reason before this fix -- its `side_effect` list exhaustion happened to make `gh_available()` return `False`, routing to the browser tier for a reason unrelated to what the test claimed to prove; fixed alongside the others even though it was not in the originally-failing set).
- **Files modified:** `firestarter_app/tests/test_submit.py`
- **Verification:** Full `tests/test_submit.py` (93 collected items) and `tests/test_dev_test_cmd.py` green; full host suite (`tests/` -p no:cacheprovider) 0 failed.
- **Committed in:** `3769dc4` (Task 2 commit)

---

**Total deviations:** 2 auto-fixed (1 Rule 1 bug fix, 1 Rule 1 non-regression reconciliation)
**Impact on plan:** Both fixes were necessary for `submit_report`'s new unconditional dedup step to be correct and honestly tested. No scope creep -- no production behavior beyond the plan's own D-09/D-10/D-11 spec was added.

## Issues Encountered
- The plan's Task 3 acceptance criteria literally cite `/tmp/venv311/bin/ruff` and `git -C /workspaces/firestarter status --porcelain` (the **firmware** sub-repo). This plan touches only `firestarter_app` (host CLI) -- no firmware file was read or modified. `/tmp/venv311` does not exist in this session; `ruff`/`ruff format` were run via the devcontainer's directly-installed `ruff 0.16.0` (confirmed CI-parity per `121-RESEARCH.md`'s own finding that CI resolves the unpinned `ruff>=0.15.14` constraint to 0.16.0), both clean. The `/workspaces/firestarter` porcelain check is read as a copy-paste artifact from a firmware-touching plan template in this phase's plan set -- this plan's dispatch prompt (`repo_layout_critical`) explicitly scopes all code/test work to `firestarter_app` only and enumerates the pre-existing dirt to leave untouched there. `firestarter_app status --porcelain` shows only pre-existing, out-of-scope untracked/modified files (`.gitignore`, `.coverage`, `.planning/config.json`, `SECURITY.md`, `doc/lockable-proms.md`, `write_test_port.sh`) that this plan did not create or touch, per the dispatch prompt's own enumeration. `/workspaces/firestarter` (the firmware repo) separately carries pre-existing, unrelated dirt (a nested untracked `firestarter/firestarter/` directory, stale core-dump files) dated before this session started -- also outside this plan's scope and left untouched.
- Two of the plan's cited line-number anchors (`test_submit.py:230-245` for the repo-target pin, `:295-325` for the negative-argv idiom) had drifted slightly by the time this plan executed (actual: `:323-343` and `:301-320` respectively, after 120-12's `test_submit_via_gh_argv_targets_the_project_wide_tracker` addition) -- confirmed by reading the live file rather than trusting the line numbers, consistent with this milestone's established "verify before planning around the text" pattern.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- DEVTEST-05 and DEVTEST-06 are both closed; `submit_report`'s dedup-first/always-ask/comment-on-duplicate contract is fully landed and test-covered (93 collected test items in `tests/test_submit.py`, up from 61 pre-121-11).
- No blockers. Full host suite green (`tests/ -p no:cacheprovider` 0 failed), coverage 81.86% (floor 70%), `check_devtest_orchestrator.py` PASS (submit.py already in its scanned-file list from Phase 113), ruff clean on every touched file (0.16.0, CI-parity).
- Plan 121-12 (GATE-02, meta catalog edit + `sync_to_subrepos.sh`) and 121-13 (GATE-02 close, doc targets) do not depend on this plan's internals; 121-14 (GATE-03 close, full nine-row sweep) will re-run the full suite at the phase's final commit as usual.

---
*Phase: 121-dev-test-fix-gates-docs-redesign*
*Completed: 2026-07-29*

## Self-Check: PASSED

- FOUND: `.planning/phases/121-dev-test-fix-gates-docs-redesign/121-11-SUMMARY.md`
- FOUND: `c15972b` (firestarter_app, Task 1)
- FOUND: `3769dc4` (firestarter_app, Task 2)
- FOUND: `4dd92d3` (firestarter_app, Task 3)
