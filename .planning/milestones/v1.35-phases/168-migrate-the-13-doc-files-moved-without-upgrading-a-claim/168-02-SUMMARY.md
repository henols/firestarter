---
phase: 168-migrate-the-13-doc-files-moved-without-upgrading-a-claim
plan: 02
subsystem: docs
tags: [wiki-tooling, retirement, argparse, selftest, sidebar-containment]

requires: []
provides:
  - "wiki.py exposes exactly one subcommand (links), with no code path that can write to a git remote"
  - "wiki.py links --source-dir required argument and check_sidebar_lists_every_page containment leg"
  - "tools/wiki/selftest.sh cut to 6 surviving cases, none invoking a deleted subcommand"
affects: ["168-03 and later 168 plans that push the 12 migrated pages and wire wiki-check.yml"]

tech-stack:
  added: []
  patterns: ["set-containment (not byte-equality) checker leg reusing check_orphans's shape and failure-list return convention"]

key-files:
  created: []
  modified:
    - tools/wiki/wiki.py
    - tools/wiki/selftest.sh
    - wiki/Home.md
    - wiki/How-This-Wiki-Is-Published.md
    - wiki/_Sidebar.md
    - .github/workflows/wiki-publish.yml

key-decisions:
  - "--source-dir attached only to the links subparser, not shared via parents=[] with the top-level parser — a required argument shared with parents=[] breaks when supplied after the subcommand token (argparse tracks 'seen' per parser instance, not per action), which the acceptance criteria's `links --source-dir X` ordering requires"
  - "case_orphan_exit_1 and case_sidebar_link_is_not_evidence repaired by replacing their `wiki.py sidebar` calls with a literal printf writing the exact _Sidebar.md content each case's semantics need, preserving which check (Home-reachability vs sidebar-containment) each case is attributing its RED to"
  - "case_wiki05_unreferenced_page_exit_1 exercises both new/kept legs in one case: a page linked from Home but absent from _Sidebar.md trips the new containment leg (Page-Two); a page listed in _Sidebar.md but not linked from Home trips the pre-existing check_orphans leg (Page-Three)"

patterns-established:
  - "A checker's set-containment leg is written as `check_*(source_dir) -> list[str]`, appended into cmd_links's existing failures accumulator, exactly matching check_orphans's non-vacuity shape (missing-file case appends a failure and returns immediately, never a silent pass)"

requirements-completed: [WIKI-02, WIKI-05]

coverage:
  - id: D1
    description: "wiki.py exposes exactly one subcommand (links); no code path can write to a git remote; --source-dir is required with no default"
    requirement: "WIKI-02"
    verification:
      - kind: automated
        ref: "grep -cE 'def (cmd_publish|cmd_sidebar|cmd_check|generate_sidebar|safe_remote|_git)\\(' tools/wiki/wiki.py (=0); grep -cE '^(import|from) (difflib|shutil|subprocess|tempfile)' tools/wiki/wiki.py (=0); COMMANDS dict has exactly 1 key"
        status: pass
    human_judgment: false
  - id: D2
    description: "wiki/ (3 files) and .github/workflows/wiki-publish.yml deleted from the index; no in-repo mirror of wiki content remains; deletion verified byte-identical to the live wiki before removal"
    requirement: "WIKI-02"
    verification:
      - kind: automated
        ref: "test -d wiki (false); git ls-files wiki/ | wc -l (=0); test -f .github/workflows/wiki-publish.yml (false); git grep -c WIKI_PUSH_TOKEN -- .github (0 matches); diff -r against a fresh clone of firestarter_prom.wiki.git reported no differences before deletion"
        status: pass
    human_judgment: false
  - id: D3
    description: "check_sidebar_lists_every_page implements set containment (not byte equality), fails on a missing page, fails on an absent _Sidebar.md, and is wired into cmd_links's shared failures accumulator"
    requirement: "WIKI-05"
    verification:
      - kind: automated
        ref: "python3 inline script: green control ([] for a fully-listed sidebar), RED naming Page-One when absent from sidebar, RED when _Sidebar.md itself is deleted"
        status: pass
    human_judgment: false
  - id: D4
    description: "selftest.sh cut to exactly 6 cases (orphan_exit_1, sidebar_link_is_not_evidence, broken_link_exit_1, md_suffix_link_exit_1, illegal_filename_exit_1, wiki05_unreferenced_page_exit_1); no case invokes a deleted subcommand; new WIKI-05 case trips both legs by name before being trusted"
    requirement: "WIKI-05"
    verification:
      - kind: automated
        ref: "bash tools/wiki/selftest.sh -> OK: selftest complete (6 cases), exit 0; grep -cE '\\$WIKI_PY\"? (sidebar|publish|check)' tools/wiki/selftest.sh (=0); evidence table shows 6/6 PASS"
        status: pass
    human_judgment: false

duration: 25min
completed: 2026-08-31
status: complete
---

# Phase 168 Plan 02: Retire the Publish Path, Add the Sidebar Containment Leg Summary

**Deleted `wiki.py`'s `publish`/`sidebar`/`check` subcommands and their helpers, deleted the in-repo `wiki/` mirror and its publish workflow, made `--source-dir` required on the surviving `links` subcommand, added a hand-maintained-sidebar containment leg, and cut `selftest.sh` from 12 fixture-driven cases to 6 — all green, none invoking a deleted subcommand.**

## Performance

- **Duration:** ~25 min
- **Started:** 2026-08-31T07:53Z (approx.)
- **Completed:** 2026-08-31
- **Tasks:** 3 completed (Task 2's code landed inside Task 1's commit — see Deviations)
- **Files modified:** 6 (3 deleted outright: `wiki/Home.md`, `wiki/How-This-Wiki-Is-Published.md`, `wiki/_Sidebar.md`, plus `.github/workflows/wiki-publish.yml`; 2 rewritten: `tools/wiki/wiki.py`, `tools/wiki/selftest.sh`)

## Accomplishments

- Confirmed all three `wiki/` files were byte-identical to the live `firestarter_prom.wiki.git` clone (`diff -r`, no differences) before deleting them, so the deletion lost nothing not already published
- Deleted `cmd_publish`, `cmd_sidebar`, `cmd_check`, `generate_sidebar`, `_git`, `safe_remote` and their argparse entries (`sidebar_parser`, `check` subparser, `publish_parser` with `--push`/`--require-wiki`); `COMMANDS` now has exactly one key, `"links"`
- Deleted `DEFAULT_WIKI_REMOTE`, `WIKI_BRANCH`, `DEFAULT_SOURCE_DIR`, the `--wiki-remote` argument, and the now-unused `difflib`/`shutil`/`subprocess`/`tempfile` imports
- Made `--source-dir` a required argument on the `links` subparser only (not shared with the top-level parser via `parents=[]`) — this was necessary to keep `wiki.py links --source-dir X` (source-dir supplied *after* the subcommand) working; sharing a required argument via `parents=[]` across the top-level and sub-parser breaks that ordering because argparse's required-argument bookkeeping is per-parser-instance, not per-action
- Deleted `wiki/` (all 3 files) and `.github/workflows/wiki-publish.yml`, orphaning the `WIKI_PUSH_TOKEN` secret name (no repository change needed for that; noted here for a reviewer)
- Added `check_sidebar_lists_every_page`, copying `check_orphans`'s shape exactly: set containment (`{page stems} ⊆ {stems linked from _Sidebar.md}`), non-vacuous on an absent sidebar, wired into `cmd_links`'s shared `failures` accumulator, and named in the extended `OK:` success line
- Cut `tools/wiki/selftest.sh` from 12 cases to 6, deleting the 7 that exercised `publish`/`sidebar`/`check`, repairing the 2 keeper cases (`orphan_exit_1`, `sidebar_link_is_not_evidence`) that previously called the now-deleted `sidebar` subcommand to refresh their fixture, and adding `wiki05_unreferenced_page_exit_1`, which trips both the new containment leg and the pre-existing `check_orphans` leg in one case with two distinctly-named mutations
- Retained `new_bare_wiki` per the plan's instruction — it has no caller in this plan's surviving cases but is reserved for plan 168-10's HONEST-02 fixture clone

## Task Commits

1. **Task 1 (+ Task 2's code): Retire the publish path, delete the in-repo mirror, add the sidebar containment leg** - `f7d1b9c5` (feat)
2. **Task 3: Cut selftest.sh to the 6 surviving cases and add the WIKI-05 case** - `e7e8766b` (test)
3. **Incidental fix: restore selftest.sh's file mode** - `7105917e` (chore)

## Files Created/Modified

- `tools/wiki/wiki.py` - rewritten: one subcommand (`links`), required `--source-dir`, new `check_sidebar_lists_every_page`, publish/sidebar/check machinery and their constants/imports deleted, docstring rewritten to describe the surviving subcommand and the required-argument rationale
- `tools/wiki/selftest.sh` - cut from 12 to 6 cases; two keeper cases repaired to stop invoking the deleted `sidebar` subcommand; one new WIKI-05 case added
- `wiki/Home.md`, `wiki/How-This-Wiki-Is-Published.md`, `wiki/_Sidebar.md` - deleted (confirmed byte-identical to the live wiki first)
- `.github/workflows/wiki-publish.yml` - deleted

## Decisions Made

- **`--source-dir` lives only on the `links` subparser, not shared with the top-level parser.** The original code shared `--wiki-remote`/`--source-dir` between the top-level parser and every subparser via a common `parents=[]` list, which worked while the argument was optional with a default. Making it `required=True` while still sharing it via `parents=[]` breaks `wiki.py links --source-dir X` (source-dir after the subcommand token): the top-level parser's own copy of the argument is never "seen" in that token order and raises its own required-argument error before the subparser gets a chance to parse it. Removing `common` as a parent of the top-level parser (keeping it only on the `links` subparser) fixes this and matches how the CLI is actually invoked. Verified interactively for both orderings.
- **Task 1 and Task 2 landed in one commit.** The plan structured them as separate tasks, but Task 2's new function slots into the same file Task 1 rewrites wholesale (deleting most of the module in the same pass), so writing them as two sequential edits to the same regions would have meant writing `check_sidebar_lists_every_page` once in Task 1's edit and then finding nothing left to add in Task 2's edit. I wrote the complete post-surgery file once (Task 1's deletions plus Task 2's new function and its wiring into `cmd_links`) and committed it as a single `feat` commit. Both tasks' acceptance criteria were verified independently against the resulting file before commit (Task 1's grep/exit-code checks; Task 2's containment-leg green/RED/absent-sidebar script), so no criterion was skipped — only the commit boundary shifted.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking issue] The plan's Task 1 packed automated `<verify>` one-liner cannot pass for any correct implementation**
- **Found during:** Task 1 verification
- **Issue:** The verify line begins `python3 tools/wiki/wiki.py --help >/dev/null 2>&1; test $? -ne 0 && ...`, which requires the bare `--help` invocation to exit non-zero. Standard Python `argparse` always processes `-h`/`--help` immediately when encountered and exits 0 before any required-argument check runs — this is unconditional CPython `argparse` behavior, not implementation-specific, and there is no way to make `--source-dir` "required" in a way that also makes `--help` fail without removing `--help` entirely (which would break normal CLI usability and contradicts nothing else in the plan).
- **Fix:** Verified every acceptance criterion listed under Task 1's `<acceptance_criteria>` individually instead of the packed one-liner (all pass — see coverage D1/D2 above), since those bullets are unambiguous and don't depend on this quirk. No product-code change was made to work around it; this is a defect in the plan's verify script, not in `wiki.py`.
- **Files modified:** none (verification-only finding)
- **Commit:** n/a

### Not Auto-fixed

None — no issue required user input or crossed into architectural-change territory (Rule 4).

## Issues Encountered

Incidentally set `tools/wiki/selftest.sh` executable (`chmod +x`) while iterating; the file's pre-existing mode was `100644` (non-executable, invoked via `bash tools/wiki/selftest.sh` per the plan's own verification commands, not directly). Restored to `100644` in a follow-up commit (`7105917e`) rather than folding the mode change into the test commit, keeping that commit's diff to content only.

## User Setup Required

None. No push to any remote was made or attempted; `wiki-publish.yml`'s deletion orphans the `WIKI_PUSH_TOKEN` secret name only — no repository setting needs to change as a result (stated per the plan's instruction, for reviewer visibility).

## Next Phase Readiness

- `wiki.py links --source-dir <clone>` is the sole surviving subcommand and is ready for later plans in this phase to point at the real `firestarter_prom.wiki.git` clone once the 12 migrated pages are pushed (plan 168-05 and later).
- `.github/workflows/wiki-check.yml` was left untouched, as instructed — it is repointed by plan 168-13, not deleted here.
- `.planning/v1.35/MIGRATION-TABLE.md` (filled by plan 168-01) and `wiki.py links` are the only two artifacts this plan keeps from the retired tooling generation; both are load-bearing for later plans.
- No blockers identified for subsequent plans in this phase.

---
*Phase: 168-migrate-the-13-doc-files-moved-without-upgrading-a-claim*
*Completed: 2026-08-31*

## Self-Check: PASSED

- FOUND: tools/wiki/wiki.py
- FOUND: tools/wiki/selftest.sh
- FOUND: .planning/phases/168-migrate-the-13-doc-files-moved-without-upgrading-a-claim/168-02-SUMMARY.md
- FOUND commit: f7d1b9c5
- FOUND commit: e7e8766b
- FOUND commit: 7105917e
- FOUND: wiki/ deleted from working tree and index
- FOUND: .github/workflows/wiki-publish.yml deleted
