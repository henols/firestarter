---
phase: 167-wiki-bootstrap-in-repo-source-sync-drift-check
plan: 01
subsystem: testing
tags: [python, bash, argparse, cli, wiki, stdlib-only, determinism]

requires: []
provides:
  - "tools/wiki/wiki.py — stdlib-only CLI skeleton with 0/1/2 exit-code contract, --source-dir and --wiki-remote parameterisation, and a deterministic sidebar generator"
  - "tools/wiki/selftest.sh — fixture-driven bash test harness with an evidence table, proven capable of failing before any capability existed"
  - "sidebar subcommand with a non-self-repairing --check leg (returns before any write)"
affects: [167-02, 167-03, 167-04, 167-05, 167-06]

tech-stack:
  added: []
  patterns:
    - "argparse common-parent-parser pattern so --source-dir/--wiki-remote work both before and after the subcommand name"
    - "bash fixture harness: rc_of captures exit code without tripping set -e, record/print_evidence_table build a case|expected|observed|control|note|verdict table"
    - "checker returns before any write on --check, mirroring tools/catalog/codegen.py's control flow"

key-files:
  created:
    - tools/wiki/wiki.py
    - tools/wiki/selftest.sh
  modified: []

key-decisions:
  - "argparse global flags (--source-dir, --wiki-remote) needed a shared parent parser added to both the top-level parser and the sidebar subparser, because argparse does not propagate top-level-only options to args typed after the subcommand name — discovered when the first green run attempt failed with 'unrecognized arguments'"
  - "rc_of takes an explicit <outfile> argument (rc_of <outfile> <command...>) rather than an implicit single shared file, so each case can grep its own captured output without collisions"
  - "docstring wording avoids embedding a literal backslash-n escape sequence in prose (Python interprets it as an actual newline in a normal triple-quoted string, which produced an ugly mid-sentence line break in --help output); reworded to describe the LF-forcing behavior without the literal escape"

requirements-completed: []

coverage:
  - id: D1
    description: "tools/wiki/selftest.sh harness exists, runs green with zero cases, and its own failure branch was observed red before any case was added"
    verification:
      - kind: unit
        ref: "bash tools/wiki/selftest.sh (zero cases: exit 0); throwaway case_throwaway_test (temporary, removed before commit): observed exit 1, ERROR: throwaway_test: expected exit 7, observed 0"
        status: pass
    human_judgment: false
  - id: D2
    description: "stale_sidebar_exit_1 and sidebar_deterministic negative cases authored, observed RED before wiki.py existed, then observed GREEN after wiki.py was implemented"
    requirement: WIKI-04
    verification:
      - kind: unit
        ref: "bash tools/wiki/selftest.sh — RED at commit 8921d5f5 (exit 1, both cases FAIL with observed exit 2), GREEN at commit 01757d7b (exit 0, both cases PASS)"
        status: pass
    human_judgment: false
  - id: D3
    description: "wiki.py sidebar --check returns before any write — a checker cannot repair what it checks"
    requirement: WIKI-04
    verification:
      - kind: unit
        ref: "case_stale_sidebar_exit_1 third assertion: cmp -s of _Sidebar.md before/after a failing --check run"
        status: pass
    human_judgment: false

duration: 8min
completed: 2026-08-30
status: complete
---

# Phase 167 Plan 01: Wiki Harness and Sidebar Generation Summary

**Stdlib-only `tools/wiki/wiki.py` CLI (argparse, 0/1/2 exit contract, deterministic `_Sidebar.md` generation) plus `tools/wiki/selftest.sh`, a fixture-driven bash test harness proven capable of failing before any capability existed.**

## Performance

- **Duration:** ~8 min
- **Started:** 2026-08-30T11:40:30Z
- **Completed:** 2026-08-30T11:48:06Z
- **Tasks:** 3
- **Files modified:** 2 (both new)

## Accomplishments
- Built `tools/wiki/selftest.sh` from scratch — no test harness of any kind existed in this repo before this plan
- Proved the harness's own failure branch is reachable with a throwaway case before registering any real case
- Authored `stale_sidebar_exit_1` and `sidebar_deterministic`, observed both RED (wiki.py did not exist) then GREEN (after implementation) — the red-then-green pair is the phase's evidentiary requirement
- Built `tools/wiki/wiki.py` with the CLI skeleton, `--source-dir`/`--wiki-remote` parameterisation, and a byte-stable, non-self-repairing `sidebar` generator

## Task Commits

Each task was committed atomically:

1. **Task 1: Create the fixture selftest harness and prove it can fail** - `b51025fc` (test)
2. **Task 2: Author the two sidebar negative cases and observe them RED** - `8921d5f5` (test)
3. **Task 3: Create wiki.py with the CLI skeleton, exit-code contract and sidebar generation** - `01757d7b` (feat)

_Note: Task 2 and Task 3 form the TDD RED/GREEN pair for `stale_sidebar_exit_1` and `sidebar_deterministic`._

## Files Created/Modified
- `tools/wiki/selftest.sh` - fixture-driven bash test driver: `banner`, `new_source_dir`, `new_bare_wiki`, `rc_of`, `record`, `assert_rc`, `print_evidence_table`, `CASES`, `EVIDENCE`, plus `case_stale_sidebar_exit_1` and `case_sidebar_deterministic`
- `tools/wiki/wiki.py` - stdlib-only CLI: `render_title`, `page_files`, `generate_sidebar`, `cmd_sidebar`, `_build_common_parser`, `_build_argparser`, `main`, `COMMANDS = {"sidebar": cmd_sidebar}`

## Decisions Made
- Shared parent parser for `--source-dir`/`--wiki-remote` so both flags parse correctly whether given before or after the `sidebar` subcommand name (argparse does not propagate top-level-only options past a subcommand boundary) — discovered as a genuine bug during Task 3's first green-run attempt, fixed under Rule 1 (see Deviations)
- `rc_of <outfile> <command...>` signature (explicit named capture file under `$WORK`) rather than a single implicit shared file, so each case's captured stdout/stderr can be grepped independently without collision between cases
- Reworded the module docstring to avoid a literal `\n` escape sequence rendering as an actual embedded newline in `--help` output; the LF-forcing behavior of `write_text(..., newline="\n")` is still documented, just not via a raw escape sequence in prose

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] `--source-dir`/`--wiki-remote` unrecognized when placed after the subcommand**
- **Found during:** Task 3, first attempt to run `bash tools/wiki/selftest.sh` after writing `wiki.py`
- **Issue:** `_build_argparser` originally defined `--source-dir` and `--wiki-remote` only on the top-level `ArgumentParser`, before `add_subparsers`. Both selftest cases invoke `wiki.py sidebar --check --source-dir <fixture>` — subcommand name first, flags after. Argparse does not forward top-level-only flags to args following the subcommand token, so every case failed with `wiki.py: error: unrecognized arguments: --source-dir ...` and exit code 2, even though `wiki.py` itself was otherwise correct.
- **Fix:** Extracted `--source-dir`/`--wiki-remote` into a shared `_build_common_parser()` (an `add_help=False` parent parser), and passed `parents=[common]` to both the top-level parser and the `sidebar` subparser, so the flags are accepted in either position.
- **Files modified:** tools/wiki/wiki.py
- **Verification:** `bash tools/wiki/selftest.sh` went from exit 1 (both cases red with `observed 2`) to exit 0 (both cases `PASS`)
- **Committed in:** 01757d7b (Task 3 commit — fixed before the task was committed, so no separate fix commit exists)

**2. [Rule 1 - Bug] Docstring `\n` literal rendered as an actual line break in `--help`**
- **Found during:** Task 3, manual inspection of `python3 tools/wiki/wiki.py --help` output
- **Issue:** The module docstring (a normal, non-raw triple-quoted string) originally contained the prose fragment `Path.write_text(..., newline="\n")`. Python interprets `\n` inside a normal string literal as an actual newline character, so `--help` rendered the sentence split across two lines mid-word (`newline="` / `") so line endings are LF`), which is confusing to a human reading the CLI's own help text.
- **Fix:** Reworded the sentence to describe the LF-forcing behavior without embedding a literal escape sequence in the docstring (`"every write forces LF line endings via Path.write_text's newline argument"`). The runtime `newline="\n"` call in `cmd_sidebar` (the actual code, not prose) is unaffected and still satisfies the `newline="\n"` acceptance check.
- **Files modified:** tools/wiki/wiki.py
- **Verification:** `python3 tools/wiki/wiki.py --help` now renders the sentence on contiguous lines; `grep -c 'newline="\\n"' tools/wiki/wiki.py` still returns 1 (from the real `write_text` call)
- **Committed in:** 01757d7b (Task 3 commit)

---

**Total deviations:** 2 auto-fixed (both Rule 1 — bugs found and fixed during Task 3 before that task's commit)
**Impact on plan:** Both fixes were necessary for `wiki.py` to work at all against the cases authored in Task 2; no scope creep, no architectural change, no files beyond the two the plan specified.

## Issues Encountered
None beyond the two auto-fixed bugs documented above.

## Harness negative control

Captured while `tools/wiki/selftest.sh` temporarily carried a throwaway case (`case_throwaway_test`, running `true` and asserting an expected exit of `7`), during Task 1, before any real case existed. The throwaway case and its `CASES` registration were removed before the Task 1 commit; `git grep -n 'expected exit 7' -- tools/wiki/selftest.sh` returns nothing in the committed file.

Observed exit code: `1`

```
=== throwaway_test ===
ERROR: throwaway_test: expected exit 7, observed 0
case | expected | observed | control | note | verdict
ERROR: selftest failed (1 of 1 cases red)
```

## Observed RED: stale_sidebar_exit_1, sidebar_deterministic

Captured at commit `8921d5f5`, before `tools/wiki/wiki.py` existed. Observed exit code: `1`.

```
=== stale_sidebar_exit_1 ===
ERROR: stale_sidebar_exit_1_control: expected exit 0, observed 2
ERROR: stale_sidebar_exit_1: expected exit 1, observed 2
ERROR: stale_sidebar_exit_1: delta output missing Page-Two
=== sidebar_deterministic ===
ERROR: sidebar_deterministic_run1: expected exit 0, observed 2
ERROR: sidebar_deterministic: expected exit 0, observed 2
case | expected | observed | control | note | verdict
stale_sidebar_exit_1 | 1 | 2 | 2 | a failing --check must not rewrite the file it checks | FAIL
sidebar_deterministic | 0 | 2 | 2 | two runs over an unchanged source must be byte-identical | FAIL
ERROR: selftest failed (2 of 2 cases red)
```

(Both cases fail with `observed 2` here rather than a mismatched `0`/`1` because `python3 "$WIKI_PY" ...` could not even be invoked — `tools/wiki/wiki.py` did not exist yet at this commit, so `python3` exits 2 for "can't open file". This is the expected RED shape for a case whose capability has not been built yet.)

## Observed GREEN: stale_sidebar_exit_1, sidebar_deterministic

Captured at commit `01757d7b`, after `tools/wiki/wiki.py` was implemented (including the argparse parent-parser fix documented above). Observed exit code: `0`.

```
=== stale_sidebar_exit_1 ===
OK: stale_sidebar_exit_1_control exit 0
OK: stale_sidebar_exit_1 exit 1
=== sidebar_deterministic ===
OK: sidebar_deterministic_run1 exit 0
OK: sidebar_deterministic exit 0
case | expected | observed | control | note | verdict
stale_sidebar_exit_1 | 1 | 1 | 0 | a failing --check must not rewrite the file it checks | PASS
sidebar_deterministic | 0 | 0 | 0 | two runs over an unchanged source must be byte-identical | PASS
OK: selftest complete (2 cases)
```

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- `tools/wiki/wiki.py`'s `COMMANDS` dispatch map and `_build_common_parser`/`_build_argparser` structure are ready for plan 167-02 to add `links`/`check` subcommands and plan 167-03 to add `publish`, without touching the flag-parsing fix made here.
- `tools/wiki/selftest.sh`'s helper set (`new_bare_wiki` in particular, unused by this plan) is ready for the git-mirror cases in plans 167-02 and 167-03.
- **WIKI-04 is only partially delivered.** This plan carries the `stale_sidebar_exit_1` and `sidebar_deterministic` legs of WIKI-04; the remaining legs (`drift_detected_exit_1`, `hand_edit_overwritten`, `idempotent_head_unchanged`, `deleted_page_removed`) are delivered in plans 167-02, 167-03, 167-05 and 167-06. Do not mark WIKI-04 complete in REQUIREMENTS.md until all of those plans have a SUMMARY.md.
- No blockers for wave 2 (167-02).

## Self-Check: PASSED

- FOUND: tools/wiki/wiki.py
- FOUND: tools/wiki/selftest.sh
- FOUND: b51025fc
- FOUND: 8921d5f5
- FOUND: 01757d7b

---
*Phase: 167-wiki-bootstrap-in-repo-source-sync-drift-check*
*Completed: 2026-08-30*
