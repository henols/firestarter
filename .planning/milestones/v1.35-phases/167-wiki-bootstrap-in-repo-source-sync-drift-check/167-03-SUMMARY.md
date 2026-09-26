---
phase: 167-wiki-bootstrap-in-repo-source-sync-drift-check
plan: 03
subsystem: testing
tags: [python, bash, argparse, git, wiki, stdlib-only, mirror-publish, drift-check]

requires:
  - phase: 167-wiki-bootstrap-in-repo-source-sync-drift-check
    provides: "tools/wiki/wiki.py links/check subcommands (D-11, offline integrity legs); tools/wiki/selftest.sh fixture harness with new_bare_wiki helper"
provides:
  - "tools/wiki/wiki.py `publish` subcommand — one comparison (`git add -A` + `git diff --cached --quiet`) serving both the dry-run drift check and `--push` (D-08); wipe-and-relay mirror (WIKI-02 authority direction); commit-only-on-staged-diff idempotence (WIKI-03); exit 2 (distinct from 1) for the wiki-absent operator gate, naming WIKI-01 and the operator URL; `--require-wiki` converts exit 2 to a hard exit 1"
  - "five new selftest cases (`wiki_absent_exit_2`, `drift_detected_exit_1`, `hand_edit_overwritten`, `idempotent_head_unchanged`, `deleted_page_removed`) with captured RED-then-GREEN pairs, all run against local bare-repo fixtures via `--wiki-remote`, zero contact with github.com"
  - "a captured localised-mutation negative control proving the mirror wipe is load-bearing, not decorative"
affects: [167-04, 167-05, 167-06]

tech-stack:
  added: []
  patterns:
    - "one code path, two entry points (D-08): the same `git add -A` / `git diff --cached --quiet` result branches on `--push` at the very last step, so the dry-run result IS what `--push` would do"
    - "exit-2-vs-exit-1 operator-gate contract: `_git(\"ls-remote\", ...)` failure is the sole trigger for exit 2, and `--require-wiki` is the only thing that converts it to exit 1 — no second code path"
    - "wipe-target safety assertion before any `shutil.rmtree`: absolute path, `.git` present, `git remote get-url origin` equals the exact `--wiki-remote` string, checked before the first entry is deleted"
    - "branch assertion with an unborn-branch fallback: `git rev-parse --abbrev-ref HEAD` is the primary check (satisfies the plan's literal mechanism), with a `git symbolic-ref --short HEAD` fallback for the state every fixture's first-ever push is actually in (a just-cloned empty bare repo has no commit yet, so `rev-parse HEAD` itself is undefined)"

key-files:
  created: []
  modified:
    - tools/wiki/wiki.py
    - tools/wiki/selftest.sh

key-decisions:
  - "`git rev-parse --abbrev-ref HEAD` fails with `fatal: ambiguous argument 'HEAD'` on a freshly cloned, still-unborn bare repository (verified directly this session) — which is exactly the state of every fixture's very first `publish --push`. Rather than dropping the plan's specified mechanism, added a `git symbolic-ref --short HEAD` fallback used only when the primary probe's exit code is non-zero; both resolve to `master` for an unborn branch, so the assertion still fires correctly against a real branch mismatch."
  - "`case_deleted_page_removed`'s fixture, as literally specified, deletes the source page but leaves `Home.md`'s link to it in place, which `cmd_check` (run unconditionally first inside `cmd_publish`) correctly flags as a newly-broken link — so the very first attempt at this case failed at the offline-check gate before ever reaching the git-mirror behavior the case exists to prove. Fixed by also rewriting `Home.md` to drop the reference when the page is deleted, so the case actually exercises the mirror-deletion property rather than `cmd_check`'s (correct, unrelated) rejection."
  - "`case_hand_edit_overwritten`, as literally specified, only asserts `Page-One.md`'s content after a republish — and a same-filename content restoration is achieved equally by `shutil.copy2` alone or by wipe-then-copy, since overwriting an existing path doesn't require deleting anything first. That assertion alone cannot discriminate the wipe from a plain copy-over, which the plan's own Task 3 threat-model entry (T-167-06) requires it to do. Extended the hand-edit to also add a wiki-only `Stray-Page.md` (a page that only ever existed on the wiki side, modelling what a GitHub web-UI editor could add), and added a second assertion that it does not survive republish — this is the property that genuinely depends on the wipe, and Task 3's mutation run confirms it discriminates correctly."

requirements-completed: []

coverage:
  - id: D1
    description: "wiki.py publish computes one staged diff (git add -A + git diff --cached --quiet) shared by both the dry-run drift check and --push (D-08); dry-run exits 0 on agreement, 1 with the diff printed on drift"
    requirement: WIKI-04
    verification:
      - kind: unit
        ref: "bash tools/wiki/selftest.sh — case_drift_detected_exit_1, RED at commit b66bac59 (observed 2, publish subcommand absent), GREEN at commit e5669680 (control exit 0, mutated dry-run exit 1, diff names Page-One)"
        status: pass
    human_judgment: false
  - id: D2
    description: "wiki-absent state exits 2, distinct from 1, naming WIKI-01 and the operator URL https://github.com/henols/firestarter_prom/wiki; --require-wiki converts it to exit 1"
    requirement: WIKI-01
    verification:
      - kind: unit
        ref: "bash tools/wiki/selftest.sh — case_wiki_absent_exit_2, RED at b66bac59 (WIKI-01/URL assertions fail, subcommand absent), GREEN at e5669680 (exit 2, both literals present, existing-fixture control not 2); manual: publish --require-wiki against the same nonexistent remote exits 1 (see Observed GREEN section)"
        status: pass
    human_judgment: false
  - id: D3
    description: "publish mirrors by wipe-and-relay: a wiki-side hand edit to an existing page is destroyed, and a wiki-only page added out of band does not survive republish (WIKI-02 authority direction)"
    requirement: WIKI-02
    verification:
      - kind: unit
        ref: "bash tools/wiki/selftest.sh — case_hand_edit_overwritten, RED at b66bac59, GREEN at e5669680; Task 3 mutation (copy-over, wipe removed) turns exactly this case red (Stray-Page.md survives), proving the wipe is load-bearing for the deletion half of this property"
        status: pass
    human_judgment: false
  - id: D4
    description: "two consecutive --push runs with no source change leave the remote's rev-parse master identical, and the second run's stdout reports no-change (WIKI-03 idempotence, proved by unchanged HEAD, not absence of error)"
    requirement: WIKI-03
    verification:
      - kind: unit
        ref: "bash tools/wiki/selftest.sh — case_idempotent_head_unchanged, RED at b66bac59, GREEN at e5669680 (rev-parse master identical across both pushes, second run's log matches 'no change')"
        status: pass
    human_judgment: false
  - id: D5
    description: "a source-side page deletion propagates: after deletion and republish, the wiki's committed tree no longer lists the removed page and still lists Home.md, and the tree matches the source directory listing exactly"
    requirement: WIKI-02
    verification:
      - kind: unit
        ref: "bash tools/wiki/selftest.sh — case_deleted_page_removed, RED at b66bac59, GREEN at e5669680 (after fixing the fixture's now-broken Home.md link, see Decisions); Task 3 mutation turns exactly this case red (Page-One.md survives without the wipe)"
        status: pass
    human_judgment: false
  - id: D6
    description: "the mirror wipe is proven load-bearing, not decorative, by a captured localised mutation (wipe step removed, copy-over kept): exactly hand_edit_overwritten and deleted_page_removed go red, all ten other cases stay green, and the file is restored byte-identical afterward"
    requirement: WIKI-02
    verification:
      - kind: unit
        ref: "bash tools/wiki/selftest.sh with the wipe loop removed from cmd_publish — captured non-zero exit, 2 of 12 red (exactly the two named cases); diff -q against the pre-mutation copy after restoration reported no difference"
        status: pass
    human_judgment: false

duration: 14min
completed: 2026-08-30
status: complete
---

# Phase 167 Plan 03: Wiki Mirror Publish and Drift Check Summary

**`wiki.py publish` — one comparison serving both the dry-run drift check and `--push` (D-08), wipe-and-relay mirroring, commit-only-on-staged-diff idempotence, and an exit-2-vs-exit-1 contract that reports the WIKI-01 operator gate instead of working around it — all five remaining negative cases observed RED before GREEN, plus a captured mutation proving the wipe is load-bearing.**

## Performance

- **Duration:** ~14 min
- **Started:** 2026-08-30T12:03:00Z
- **Completed:** 2026-08-30T12:17:00Z
- **Tasks:** 3
- **Files modified:** 2

## Accomplishments
- Authored `case_wiki_absent_exit_2`, `case_drift_detected_exit_1`, `case_hand_edit_overwritten`, `case_idempotent_head_unchanged`, `case_deleted_page_removed` in `tools/wiki/selftest.sh`, observed all five RED against a `wiki.py` with no `publish` subcommand
- Implemented `wiki.py publish` (`cmd_publish`, `_git`) — the single mirror/drift/idempotence mechanism behind WIKI-01, WIKI-02, WIKI-03 and D-08; all five new cases turned GREEN with the seven wave-1/2 cases still passing (twelve green total)
- Proved the mirror wipe is load-bearing: temporarily replaced the wipe-and-relay with a plain copy-over, observed exactly `hand_edit_overwritten` and `deleted_page_removed` go red while the other ten cases (including `drift_detected_exit_1` and `idempotent_head_unchanged`) stayed green, then restored the file byte-identical
- Zero contact with `github.com` anywhere in this plan — every case uses `new_bare_wiki` (a local `git init --bare`) reached through `--wiki-remote`

## Task Commits

Each task was committed atomically:

1. **Task 1: Author the five publish and drift negative cases and observe them RED** - `b66bac59` (test)
2. **Task 2: Implement the mirror publish, the drift dry-run and the exit-2 wiki-absent contract** - `e5669680` (feat)
3. **Task 3: Prove the mirror wipe is load-bearing by a captured localised mutation** - no commit (see below)

_Note: Task 1 and Task 2 form the TDD RED/GREEN pair for the five new cases._

**Task 3 produced no commit.** Its mutation (removing the deletion loop from `cmd_publish`'s wipe-and-relay step, keeping only the copy) was applied, run, and then restored via a byte-for-byte copy of the pre-mutation file (`diff -q` confirmed zero difference against the Task 2 committed state). Since the working tree after restoration is identical to the last commit, there is nothing to commit — the evidence for this task lives entirely in the "Negative control" section below and in the `deferred-items.md`-style discipline of never leaving a residue from a throwaway mutation.

## Files Created/Modified
- `tools/wiki/wiki.py` - added `_git` (list-form `subprocess.run` wrapper, never `shell=True`), `cmd_publish` (cmd_check-first validation, ls-remote probe with exit-2/require-wiki branching, clone, branch assertion with unborn-branch fallback, wipe-target safety assertion, wipe-and-relay, single `git diff --cached --quiet` comparison branching to dry-run-report or commit+push), `--push`/`--require-wiki` flags and `publish` registration in `COMMANDS` and the argparser; added `shutil`/`tempfile` to the stdlib import list
- `tools/wiki/selftest.sh` - added `case_wiki_absent_exit_2`, `case_drift_detected_exit_1`, `case_hand_edit_overwritten`, `case_idempotent_head_unchanged`, `case_deleted_page_removed`, registered in `CASES` (now 12 total)

## Decisions Made
- Added a `git symbolic-ref --short HEAD` fallback to the plan-specified `git rev-parse --abbrev-ref HEAD` branch check, because the literal command fails outright (`fatal: ambiguous argument 'HEAD'`) on a freshly cloned, still-unborn bare repository — exactly the state of every fixture's first-ever `publish --push`. Verified directly this session before writing the fix (see Deviations).
- Extended `case_hand_edit_overwritten`'s hand edit to add a wiki-only `Stray-Page.md` in addition to modifying `Page-One.md`, and added an assertion that it does not survive republish — the content-only assertion the plan literally specifies is satisfied equally by a copy-over as by a full wipe, so it cannot discriminate the two; the added assertion is what Task 3's mutation actually needs to turn red, and it does (see Negative control below).
- Fixed `case_deleted_page_removed`'s fixture to also rewrite `Home.md` when the source page is deleted, since leaving the stale link in place made `cmd_publish`'s unconditional `cmd_check` gate (correctly) reject the fixture before the mirror-deletion behavior under test was ever reached.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] `git rev-parse --abbrev-ref HEAD` fails on an unborn branch**
- **Found during:** Task 2, first full selftest run after implementing `cmd_publish`
- **Issue:** The plan's literal mechanism for asserting the wiki worktree is on `master` (`_git("rev-parse", "--abbrev-ref", "HEAD", cwd=wt)`) fails with `fatal: ambiguous argument 'HEAD': unknown revision or path not in the working tree` when the worktree has just been cloned from a bare repository with zero commits — verified directly with a standalone `git init --bare --initial-branch=master` + `git clone` + `git rev-parse --abbrev-ref HEAD` sequence before writing any fix. Every one of this plan's fixtures performs exactly this sequence on its very first `publish --push`, so the literal mechanism would have made the very first push of every case fail.
- **Fix:** Kept `rev-parse --abbrev-ref HEAD` as the primary probe (run with `check=False`); on non-zero exit, fall back to `git symbolic-ref --short HEAD`, which correctly resolves the branch name (`master`) even before any commit exists. Both paths compare the resolved name against `WIKI_BRANCH` with the same equality check, so a genuine branch mismatch (a wiki whose default branch is something other than `master`) is still refused identically either way.
- **Files modified:** tools/wiki/wiki.py
- **Verification:** `bash tools/wiki/selftest.sh` — all fixtures' first pushes (`wiki_absent_exit_2_control`, `drift_detected_exit_1_seed`, `hand_edit_overwritten_push1`, `idempotent_head_unchanged_push1`, `deleted_page_removed_push1`) succeed against freshly created empty bare repos; `grep -c 'abbrev-ref' tools/wiki/wiki.py` still returns exactly 1, satisfying the plan's own acceptance grep
- **Committed in:** e5669680 (Task 2 commit — fixed before the task was committed, so no separate fix commit exists)

**2. [Rule 1 - Bug] `case_deleted_page_removed`'s fixture created a newly-broken link by deleting only the page, not its inbound link**
- **Found during:** Task 2, first run of the full selftest after implementing `cmd_publish`
- **Issue:** The case deleted `Page-One.md` from the source and regenerated `_Sidebar.md`, but left `Home.md`'s `[Page One](Page-One)` link in place. `cmd_publish` runs `cmd_check` unconditionally first (by design — Pattern 3 / T-167-01's mitigation), and `cmd_check` correctly detected the now-dangling link and rejected the publish with exit 1 before the mirror-deletion behavior the case exists to prove was ever exercised. The case failed for a reason unrelated to the property under test — the exact shape Pitfall 1 warns against.
- **Fix:** `case_deleted_page_removed` now also rewrites `Home.md` to a version with no internal links when it deletes `Page-One.md`, alongside regenerating `_Sidebar.md`, so the fixture stays offline-check-clean and the case actually exercises the wiki-tree-mirrors-source-after-deletion property.
- **Files modified:** tools/wiki/selftest.sh
- **Verification:** `bash tools/wiki/selftest.sh` — `case_deleted_page_removed` went from `expected exit 0, observed 1` (mismatched, offline check rejected the fixture) to `PASS` with the wiki tree listing matching the source directory listing exactly
- **Committed in:** e5669680 (Task 2 commit — fixed before the task was committed, so no separate fix commit exists)

---

**Total deviations:** 2 auto-fixed (both Rule 1 — bugs discovered while making Task 1's authored cases pass against the real implementation, before Task 2's commit)
**Impact on plan:** Both fixes were necessary for the plan's own acceptance criteria to be met at all (a passing selftest with twelve green cases). No scope creep, no architectural change, no files beyond the two the plan specified.

## Issues Encountered
None beyond the two auto-fixed bugs documented above.

## Observed RED: wiki_absent_exit_2, drift_detected_exit_1, hand_edit_overwritten, idempotent_head_unchanged, deleted_page_removed

Captured at commit `b66bac59`, before `tools/wiki/wiki.py` had a `publish` subcommand. Observed selftest exit code: `1`.

```
=== stale_sidebar_exit_1 ===
OK: stale_sidebar_exit_1_control exit 0
OK: stale_sidebar_exit_1 exit 1
=== sidebar_deterministic ===
OK: sidebar_deterministic_run1 exit 0
OK: sidebar_deterministic exit 0
=== orphan_exit_1 ===
OK: orphan_exit_1_control exit 0
OK: orphan_exit_1 exit 1
=== sidebar_link_is_not_evidence ===
OK: sidebar_link_is_not_evidence_control exit 0
OK: sidebar_link_is_not_evidence_sidebar_check exit 0
OK: sidebar_link_is_not_evidence exit 1
=== broken_link_exit_1 ===
OK: broken_link_exit_1_control exit 0
OK: broken_link_exit_1 exit 1
=== md_suffix_link_exit_1 ===
OK: md_suffix_link_exit_1_control exit 0
OK: md_suffix_link_exit_1 exit 1
=== illegal_filename_exit_1 ===
OK: illegal_filename_exit_1_control exit 0
OK: illegal_filename_exit_1 exit 1
=== wiki_absent_exit_2 ===
OK: wiki_absent_exit_2 exit 2
ERROR: wiki_absent_exit_2: stderr missing WIKI-01
ERROR: wiki_absent_exit_2: stderr missing operator URL
ERROR: wiki_absent_exit_2_control: existing remote must not exit 2, observed 2
=== drift_detected_exit_1 ===
ERROR: drift_detected_exit_1_seed: expected exit 0, observed 2
ERROR: drift_detected_exit_1_control: expected exit 0, observed 2
warning: You appear to have cloned an empty repository.
ERROR: drift_detected_exit_1: expected exit 1, observed 2
ERROR: drift_detected_exit_1: diff output missing Page-One
=== hand_edit_overwritten ===
ERROR: hand_edit_overwritten_push1: expected exit 0, observed 2
ERROR: hand_edit_overwritten_control: fixture page does not match source immediately after push
warning: You appear to have cloned an empty repository.
ERROR: hand_edit_overwritten: expected exit 0, observed 2
ERROR: hand_edit_overwritten: fixture page not overwritten back to source content
ERROR: hand_edit_overwritten: wiki-only stray page survived republish
=== idempotent_head_unchanged ===
ERROR: idempotent_head_unchanged_push1: expected exit 0, observed 2
fatal: ambiguous argument 'master': unknown revision or path not in the working tree.
Use '--' to separate paths from revisions, like this:
'git <command> [<revision>...] -- [<file>...]'
ERROR: idempotent_head_unchanged: expected exit 0, observed 2
fatal: ambiguous argument 'master': unknown revision or path not in the working tree.
Use '--' to separate paths from revisions, like this:
'git <command> [<revision>...] -- [<file>...]'
ERROR: idempotent_head_unchanged: second run stdout does not report no-change
=== deleted_page_removed ===
ERROR: deleted_page_removed_push1: expected exit 0, observed 2
fatal: Not a valid object name master
ERROR: deleted_page_removed_control: fixture tree does not match source directory immediately after push
ERROR: deleted_page_removed: expected exit 0, observed 2
fatal: Not a valid object name master
ERROR: deleted_page_removed: fixture tree does not match source directory after deletion
ERROR: deleted_page_removed: Home.md missing from fixture after deletion
case | expected | observed | control | note | verdict
stale_sidebar_exit_1 | 1 | 1 | 0 | a failing --check must not rewrite the file it checks | PASS
sidebar_deterministic | 0 | 0 | 0 | two runs over an unchanged source must be byte-identical | PASS
orphan_exit_1 | 1 | 1 | 0 | orphan absent from Home.md | PASS
sidebar_link_is_not_evidence | 1 | 1 | 0 | home-only evidence | PASS
broken_link_exit_1 | 1 | 1 | 0 | unresolved internal link target | PASS
md_suffix_link_exit_1 | 1 | 1 | 0 | md-suffixed internal link rejected | PASS
illegal_filename_exit_1 | 1 | 1 | 0 | illegal filename character | PASS
wiki_absent_exit_2 | 2 | 2 | 2 | nonexistent remote vs existing bare fixture | PASS
drift_detected_exit_1 | 1 | 2 | 2 | wiki-side edit pushed then dry-run detects drift | FAIL
hand_edit_overwritten | 0 | 2 | 1 | wiki-side hand edit and stray page both destroyed by republish | FAIL
idempotent_head_unchanged | 0 | 2 | 2 | two pushes with no source change: HEAD identical | FAIL
deleted_page_removed | 0 | 2 | 1 | source page deleted then republished; wiki tree matches source exactly | FAIL
ERROR: selftest failed (5 of 12 cases red)
```

Note: `wiki_absent_exit_2`'s evidence-table row shows `PASS` even in this RED run, because its exit code (`2`, from argparse's "invalid choice: 'publish'") happens to coincidentally match the expected `2` for a different reason (the operator-gate contract, not yet implemented). The row's `verdict` column only compares expected-vs-observed exit code; the case function's real pass/fail (which also checks for the `WIKI-01` and URL literals) correctly returned failure, which is why it is counted among the "5 of 12 cases red" in the final tally and not treated as proven at this commit.

## Observed GREEN: wiki_absent_exit_2, drift_detected_exit_1, hand_edit_overwritten, idempotent_head_unchanged, deleted_page_removed

Captured at commit `e5669680`, after `wiki.py publish` was implemented (including both auto-fixes documented above). Observed selftest exit code: `0`.

```
=== stale_sidebar_exit_1 ===
OK: stale_sidebar_exit_1_control exit 0
OK: stale_sidebar_exit_1 exit 1
=== sidebar_deterministic ===
OK: sidebar_deterministic_run1 exit 0
OK: sidebar_deterministic exit 0
=== orphan_exit_1 ===
OK: orphan_exit_1_control exit 0
OK: orphan_exit_1 exit 1
=== sidebar_link_is_not_evidence ===
OK: sidebar_link_is_not_evidence_control exit 0
OK: sidebar_link_is_not_evidence_sidebar_check exit 0
OK: sidebar_link_is_not_evidence exit 1
=== broken_link_exit_1 ===
OK: broken_link_exit_1_control exit 0
OK: broken_link_exit_1 exit 1
=== md_suffix_link_exit_1 ===
OK: md_suffix_link_exit_1_control exit 0
OK: md_suffix_link_exit_1 exit 1
=== illegal_filename_exit_1 ===
OK: illegal_filename_exit_1_control exit 0
OK: illegal_filename_exit_1 exit 1
=== wiki_absent_exit_2 ===
OK: wiki_absent_exit_2 exit 2
=== drift_detected_exit_1 ===
OK: drift_detected_exit_1_seed exit 0
OK: drift_detected_exit_1_control exit 0
OK: drift_detected_exit_1 exit 1
=== hand_edit_overwritten ===
OK: hand_edit_overwritten_push1 exit 0
OK: hand_edit_overwritten exit 0
=== idempotent_head_unchanged ===
OK: idempotent_head_unchanged_push1 exit 0
OK: idempotent_head_unchanged exit 0
=== deleted_page_removed ===
OK: deleted_page_removed_push1 exit 0
OK: deleted_page_removed exit 0
case | expected | observed | control | note | verdict
stale_sidebar_exit_1 | 1 | 1 | 0 | a failing --check must not rewrite the file it checks | PASS
sidebar_deterministic | 0 | 0 | 0 | two runs over an unchanged source must be byte-identical | PASS
orphan_exit_1 | 1 | 1 | 0 | orphan absent from Home.md | PASS
sidebar_link_is_not_evidence | 1 | 1 | 0 | home-only evidence | PASS
broken_link_exit_1 | 1 | 1 | 0 | unresolved internal link target | PASS
md_suffix_link_exit_1 | 1 | 1 | 0 | md-suffixed internal link rejected | PASS
illegal_filename_exit_1 | 1 | 1 | 0 | illegal filename character | PASS
wiki_absent_exit_2 | 2 | 2 | 1 | nonexistent remote vs existing bare fixture | PASS
drift_detected_exit_1 | 1 | 1 | 0 | wiki-side edit pushed then dry-run detects drift | PASS
hand_edit_overwritten | 0 | 0 | 0 | wiki-side hand edit and stray page both destroyed by republish | PASS
idempotent_head_unchanged | 0 | 0 | 0 | two pushes with no source change: HEAD identical | PASS
deleted_page_removed | 0 | 0 | 0 | source page deleted then republished; wiki tree matches source exactly | PASS
OK: selftest complete (12 cases)
```

Additional acceptance-criteria checks run manually at this commit (not part of the persistent `CASES` array):

```
$ python3 tools/wiki/wiki.py publish --help
... --push  Write the computed diff to the wiki remote. Without this flag
            publish only computes and reports the diff; nothing is sent
            to the remote.
(exit 0)

$ python3 tools/wiki/wiki.py publish --push --source-dir <fixture with Page-Orphan.md not linked from Home.md> --wiki-remote <valid empty bare fixture>
ERROR: orphan page not linked from Home.md: Page-Orphan
ERROR: offline legs failed (1 of 2).
ERROR: offline legs failed; nothing was sent to the wiki.
(exit 1)
$ git --git-dir <that bare fixture> rev-parse --verify master
fatal: Needed a single revision
(exit 128 -- remote was never written)

$ python3 tools/wiki/wiki.py publish --source-dir <valid fixture> --wiki-remote <nonexistent path>
(exit 2, stderr contains WIKI-01 and https://github.com/henols/firestarter_prom/wiki)
$ python3 tools/wiki/wiki.py publish --require-wiki --source-dir <valid fixture> --wiki-remote <same nonexistent path>
ERROR: wiki remote not reachable: <path>
(exit 1)
```

## Negative control: mirror wipe replaced by copy-over

`cmd_publish`'s wipe loop (`for entry in wt.iterdir(): ... shutil.rmtree(entry) / entry.unlink()`) was temporarily deleted, keeping only the subsequent copy loop that writes every source file into the worktree — a plain copy-over with no prior deletion. Selftest run captured, then the exact pre-mutation file was restored and re-verified byte-identical with `diff -q` before proceeding.

Observed selftest exit code with the wipe removed: `1`.

```
=== stale_sidebar_exit_1 ===
OK: stale_sidebar_exit_1_control exit 0
OK: stale_sidebar_exit_1 exit 1
=== sidebar_deterministic ===
OK: sidebar_deterministic_run1 exit 0
OK: sidebar_deterministic exit 0
=== orphan_exit_1 ===
OK: orphan_exit_1_control exit 0
OK: orphan_exit_1 exit 1
=== sidebar_link_is_not_evidence ===
OK: sidebar_link_is_not_evidence_control exit 0
OK: sidebar_link_is_not_evidence_sidebar_check exit 0
OK: sidebar_link_is_not_evidence exit 1
=== broken_link_exit_1 ===
OK: broken_link_exit_1_control exit 0
OK: broken_link_exit_1 exit 1
=== md_suffix_link_exit_1 ===
OK: md_suffix_link_exit_1_control exit 0
OK: md_suffix_link_exit_1 exit 1
=== illegal_filename_exit_1 ===
OK: illegal_filename_exit_1_control exit 0
OK: illegal_filename_exit_1 exit 1
=== wiki_absent_exit_2 ===
OK: wiki_absent_exit_2 exit 2
=== drift_detected_exit_1 ===
OK: drift_detected_exit_1_seed exit 0
OK: drift_detected_exit_1_control exit 0
OK: drift_detected_exit_1 exit 1
=== hand_edit_overwritten ===
OK: hand_edit_overwritten_push1 exit 0
OK: hand_edit_overwritten exit 0
ERROR: hand_edit_overwritten: wiki-only stray page survived republish
=== idempotent_head_unchanged ===
OK: idempotent_head_unchanged_push1 exit 0
OK: idempotent_head_unchanged exit 0
=== deleted_page_removed ===
OK: deleted_page_removed_push1 exit 0
OK: deleted_page_removed exit 0
ERROR: deleted_page_removed: fixture tree does not match source directory after deletion
ERROR: deleted_page_removed: Page-One.md still present in fixture after deletion
case | expected | observed | control | note | verdict
stale_sidebar_exit_1 | 1 | 1 | 0 | a failing --check must not rewrite the file it checks | PASS
sidebar_deterministic | 0 | 0 | 0 | two runs over an unchanged source must be byte-identical | PASS
orphan_exit_1 | 1 | 1 | 0 | orphan absent from Home.md | PASS
sidebar_link_is_not_evidence | 1 | 1 | 0 | home-only evidence | PASS
broken_link_exit_1 | 1 | 1 | 0 | unresolved internal link target | PASS
md_suffix_link_exit_1 | 1 | 1 | 0 | md-suffixed internal link rejected | PASS
illegal_filename_exit_1 | 1 | 1 | 0 | illegal filename character | PASS
wiki_absent_exit_2 | 2 | 2 | 1 | nonexistent remote vs existing bare fixture | PASS
drift_detected_exit_1 | 1 | 1 | 0 | wiki-side edit pushed then dry-run detects drift | PASS
hand_edit_overwritten | 0 | 0 | 0 | wiki-side hand edit and stray page both destroyed by republish | PASS
idempotent_head_unchanged | 0 | 0 | 0 | two pushes with no source change: HEAD identical | PASS
deleted_page_removed | 0 | 0 | 0 | source page deleted then republished; wiki tree matches source exactly | PASS
ERROR: selftest failed (2 of 12 cases red)
```

Went red: exactly `hand_edit_overwritten` (the wiki-only `Stray-Page.md` survives republish without the wipe) and `deleted_page_removed` (the deleted `Page-One.md` survives republish without the wipe, and the wiki tree no longer matches the source directory listing). Stayed green: all other ten cases, including `drift_detected_exit_1` (a same-filename content mutation is restored equally by copy-over, since overwriting doesn't require a prior deletion) and `idempotent_head_unchanged` (the very first push into an empty repository has nothing extra to wipe). Note as with the RED/GREEN captures above: the evidence-table `verdict` column for these two rows still prints `PASS` because it only compares exit codes (both cases still exit `0`); the actual red signal is the two `ERROR:` lines and the final `(2 of 12 cases red)` tally, which the harness's per-case return code (checked by the driver loop, not by the printed table) correctly reflects.

The mutation was localised as intended: exactly the two cases named in the plan's Task 3 threat-model entry (T-167-06) went red, nothing else moved. After restoration, `bash tools/wiki/selftest.sh` returned to exit `0` with all twelve cases green (see "Confirm restored file passes all 12 cases" run, same output as the Observed GREEN section above), and `diff -q` against the pre-mutation copy of `tools/wiki/wiki.py` reported zero difference before the restored state was left in the working tree (no commit needed — `git status --short` shows no change to either wiki file after restoration).

## Fixture faithfulness

Criteria 2 (WIKI-02 authority direction), 3 (WIKI-03 idempotence) and 4 (WIKI-04 drift detection) are proved in this plan **against a local bare-repository fixture only** (`git init --bare` reached through `--wiki-remote`), never against `https://github.com/henols/firestarter_prom.wiki.git`, which does not exist as of this session (re-verified 2026-08-30, consistent with `167-RESEARCH.md`'s `git ls-remote` probe recorded the same session). The fixture proves the **local git mechanism** — that `git clone` / `git add -A` / `git diff --cached --quiet` / `git commit` / `git push` behave as this plan's design requires, that `rev-parse --abbrev-ref HEAD` (with the symbolic-ref fallback) resolves `master` correctly, and that a bare repository's tree can be read back with `ls-tree`/`show`. It proves **nothing** about the GitHub service tier: real wiki push authentication (Pitfall 3's `GITHUB_TOKEN` 403 risk), whether the live wiki actually serves `master` after a push, whether Gollum renders the mirrored pages as expected, or whether `_Sidebar.md` displays correctly in the GitHub UI. v1.34's rig phase (Phase 160) is the standing precedent for why this distinction is stated explicitly rather than assumed away: its ~20 latent tooling defects all had passing fixture selftests and all surfaced only on first contact with real hardware. The live re-run against the real wiki is Plan 167-06's operator-gated work, and WIKI-01 remains open until the operator performs the one web-UI page save that GitHub requires before any wiki repository exists.

## User Setup Required
None - no external service configuration required. (The operator's one required action — creating the wiki via a web-UI page save — is WIKI-01, scoped to plan 167-06, not this plan.)

## Next Phase Readiness
- `wiki.py`'s `COMMANDS` dispatch map now carries `sidebar`, `links`, `check`, `publish` — the full CLI surface this phase's ROADMAP criteria require. No further subcommands are anticipated before 167-06's live demonstration.
- `tools/wiki/selftest.sh` carries all eleven of `167-RESEARCH.md`'s enumerated OBSERVED-RED negative cases (`stale_sidebar_exit_1`, `sidebar_deterministic`, `orphan_exit_1`, `sidebar_link_is_not_evidence`, `broken_link_exit_1`, `md_suffix_link_exit_1`, `illegal_filename_exit_1`, `wiki_absent_exit_2`, `drift_detected_exit_1`, `hand_edit_overwritten`, `idempotent_head_unchanged`, `deleted_page_removed` — twelve ids; `sidebar_deterministic` is a positive/determinism case rather than a negative case, matching the eleven-negative-plus-one-positive count in the research doc), each with a captured RED-then-GREEN pair.
- **WIKI-01, WIKI-02, WIKI-03 and WIKI-04 remain `Pending` in REQUIREMENTS.md, deliberately not marked complete.** Every one of them spans further plans: WIKI-01 cannot be satisfied by construction until the operator creates the live wiki (167-06); WIKI-02/03/04's local-fixture halves are now fully delivered across plans 167-01/02/03, but their live-demonstration halves are still 167-06's work per the phase's own must-haves.
- `.planning/v1.35/MIGRATION-TABLE.md`, `wiki/Home.md`, `wiki/How-This-Wiki-Is-Published.md`, `.github/workflows/wiki-check.yml` and `.github/workflows/wiki-publish.yml` are still unbuilt — the phase's `<artifacts_this_phase_produces>` lists them for plans 167-04/167-05/167-06, not this plan.
- No blockers for the next wave. `cmd_publish`'s `_git` helper and exit-code contract are stable for `.github/workflows/wiki-check.yml`/`wiki-publish.yml` (plan 167-05) to invoke directly.

## Self-Check: PASSED

- FOUND: tools/wiki/wiki.py
- FOUND: tools/wiki/selftest.sh
- FOUND: b66bac59
- FOUND: e5669680

---
*Phase: 167-wiki-bootstrap-in-repo-source-sync-drift-check*
*Completed: 2026-08-30*
