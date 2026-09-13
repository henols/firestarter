---
phase: 185-records-and-checks-that-are-current
reviewed: 2026-09-11T00:00:00Z
depth: standard
files_reviewed: 14
files_reviewed_list:
  - firestarter/scripts/baseline/size_baseline.json
  - firestarter/tests/fixtures/captured_build_v185_leonardo.log
  - firestarter/tests/fixtures/captured_build_v185_uno.log
  - firestarter/tests/fixtures/captured_build_v185_uno328pb.log
  - firestarter/tests/fixtures/captured_test_native_nodevtools_summary.log
  - firestarter/tests/fixtures/captured_test_native_summary.log
  - firestarter/tests/fixtures/planted_size_baseline_flash_regression_v185.log
  - firestarter/tests/test_check_size_baseline.py
  - firestarter_app/firestarter/cli_handlers.py
  - firestarter_app/tests/test_check_devtest_orchestrator.py
  - firestarter_app/tests/test_dev_test_cmd.py
  - firestarter_app/tests/test_numeric_schema_source_scan.py
  - firestarter_app/tools/check_devtest_orchestrator.py
  - tools/catalog/sync_to_subrepos.sh
findings:
  critical: 0
  warning: 1
  info: 1
  total: 2
status: issues_found
---

# Phase 185: Code Review Report

**Reviewed:** 2026-09-11T00:00:00Z
**Depth:** standard
**Files Reviewed:** 14
**Status:** issues_found

## Summary

This phase's actual work is entirely inside the two submodules (`firestarter/`, `firestarter_app/`);
the meta-repo `git diff` shows nothing for them, so all analysis here used
`git -C firestarter diff ec7c1bbd..HEAD` and `git -C firestarter_app diff a745cb64..HEAD` per the
scope notes, plus running the affected test suites for real rather than trusting the (very long)
prose docstrings.

Four independent changes were reviewed:

1. **Firmware size-baseline fixture severance** (`size_baseline.json` + `captured_build_v185_*`,
   `captured_test_native*`, `planted_size_baseline_flash_regression_v185.log`,
   `test_check_size_baseline.py`). Verified by hand: every fixture's `Flash:`/`RAM:` figure matches
   the JSON's new `avr_targets`/`native_envs` values exactly, `flash_free = flash_total - flash_used`
   arithmetic is correct on all three targets, the planted-regression fixture differs from its clean
   sibling by exactly one line (`diff` confirms), and `pytest tests/test_check_size_baseline.py`
   passes 14/14 for real. No test was found that passes vacuously or asserts something other than
   its name claims. One drift was found in `size_baseline.json`'s own prose (see Warning below).

2. **`test_dev_test_cmd.py` de-scaffolding** (51 `_off_tty()` context-manager removals, one
   renamed test, one merged test pair). Confirmed `_is_interactive` had zero production call sites
   even before this phase (only referenced in its own docstring), so removing the context manager
   that monkeypatched it changes no test's exercised code path. The merged pair
   (`test_uv_part_writes_one_slot_on_a_tty` / `..._off_a_tty_too` → `test_uv_part_writes_one_slot`)
   is a legitimate dedup once TTY state has zero effect on the code under test. Full suite passes
   (97/97 across the three touched `firestarter_app` test files).

3. **Dead-code deletion** (`_is_interactive` and its three dependents, across `cli_handlers.py`,
   `check_devtest_orchestrator.py`'s allow-list, and its own paired test's docstring). `grep -r
   "_is_interactive"` across both repos returns nothing after the change — no orphaned reference,
   no stale allow-list entry, `tools/check_devtest_orchestrator.py` still runs and PASSes for real.

4. **`sync_to_subrepos.sh` self-diff fix**. The prior code diffed the just-copied destination file
   against itself (`diff -q "$DST" "$DST"`), a tautology that could never fail. The fix generates
   into `mktemp`, installs with `cp`, and diffs the temp file against the installed one. I exercised
   this directly: a clean re-run exits 0 and changes nothing; a genuinely hand-diverged + read-only
   `messages.h` makes the fix correctly print `ERROR: ... did not land ...` and exit 1 (then
   restored the file — working tree is clean). This is a real, working fix, not another vacuous
   check.

## Warnings

### WR-01: `size_baseline.json`'s `envs_agree_note` now contradicts its own claim

**File:** `firestarter/scripts/baseline/size_baseline.json:88`
**Issue:** Plan 185-01 bumped `native_envs.native.cases`/`.succeeded` (and the `nodevtools` sibling)
from 184 to 185, and added a new `cold_rerecord_plan185_01` meta note correctly describing the
184→185 move. It did not update `envs_agree_note`, which still reads:

```
"native and native_nodevtools still report byte-identical {cases: 184, suites: 17,
all_passed: true} pairs (count corrected Phase 158 Plan 04, C-8 -- ... the CURRENT figure is
what this note quotes, never a copy held in prose): ..."
```

That note's own text asserts it is never a stale copy — a claim that was true when Phase 158
wrote it (184 was current then) but has been false since this phase's edit landed 185, without the
note being touched. This is exactly the failure mode this file's own convention exists to catch (see
`meta.native_case_count_revision_260822`'s explicit callout of the *previous* instance of this same
drift, `{cases: 151, ...}` vs the true 172/184). No checker consumes `envs_agree_note` or
`envs_agree` (`grep -n "envs_agree" scripts/check_size_baseline.py` returns nothing), so this is
prose-only and not gate-breaking, but it is a documentation regression in a file whose entire value
proposition is being the single, byte-verified source of truth other phases cite by number.

**Fix:** Update the embedded figure in `envs_agree_note` from `{cases: 184, ...}` to
`{cases: 185, ...}` in the same commit that moves `native_envs`, or drop the embedded number from
the note entirely and point it at the live `native_envs` block instead of quoting a value that will
recur-drift on every future case-count change.

## Info

### IN-01: `sync_to_subrepos.sh`'s failure-path `rm -f "$tmp_h"` (and `$tmp_py`) is unreachable dead code

**File:** `tools/catalog/sync_to_subrepos.sh:90-93` (and the mirrored `109-112` for `$tmp_py`)
**Issue:** The `else` branch of the freshly-fixed diff check already does `rm -f "$tmp_h"; exit 1`
before the `fi`. The unconditional `rm -f "$tmp_h"` immediately after the `fi` therefore only ever
executes on the success path (where the file is also already fine to remove) — on the failure path
it is unreachable because the script has already exited. Harmless (no double-rm error, since `-f`
suppresses it, and it never actually runs post-exit), but it reads as if it exists to guarantee
cleanup on both paths when it only ever runs on one.
**Fix:** Either remove the redundant `rm -f "$tmp_h"` from inside the `else` branch (the trailing
one after `fi` is unreachable there anyway... actually the reverse: keep the one inside `else` since
it's the only one that runs before `exit 1`, and note that the one after `fi` is what actually
covers the success path) — no functional change needed, purely a readability nit if touched again.

---

_Reviewed: 2026-09-11T00:00:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
