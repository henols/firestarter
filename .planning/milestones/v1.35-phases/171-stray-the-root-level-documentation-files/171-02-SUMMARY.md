---
phase: 171-stray-the-root-level-documentation-files
plan: 02
subsystem: docs
tags: [repo-hygiene, security-policy, packaging, py311, deletion]

# Dependency graph
requires:
  - phase: 171-stray-the-root-level-documentation-files
    plan: "171-01"
    provides: "Shell-Completion, the live wiki page publishing autocomplete.md's content — the publish half of the publish-then-delete pair"
provides:
  - "One path-scoped firestarter_app commit deleting things.md, SECURITY.md and autocomplete.md from the repo root"
  - "Four evidence files proving recoverability, no smuggled security policy, packaging parity on a clean tree, and a passing CPython 3.11 test suite"
affects: [171-03-plan, 171-04-plan]

# Tech tracking
tech-stack:
  added: []
  patterns: ["clean-tree git-archive sdist build to avoid the working-tree SOURCES.txt false positive", "py3.11 scratch-venv route for CI-floor test signal on markdown-only commits ci.yml skips"]

key-files:
  created:
    - ".planning/phases/171-stray-the-root-level-documentation-files/evidence/171-02-deletion-commit.txt"
    - ".planning/phases/171-stray-the-root-level-documentation-files/evidence/171-02-recoverability-and-sweep.txt"
    - ".planning/phases/171-stray-the-root-level-documentation-files/evidence/171-02-sdist-clean-tree-diff.txt"
    - ".planning/phases/171-stray-the-root-level-documentation-files/evidence/171-02-py311-suite.txt"
  modified:
    - "firestarter_app/things.md (deleted)"
    - "firestarter_app/SECURITY.md (deleted)"
    - "firestarter_app/autocomplete.md (deleted)"

key-decisions:
  - "Re-confirmed the publish-then-delete gate from a fresh independent clone (not the one used in 171-01) before deleting anything — Shell-Completion.md was present at bf787fb"
  - "Deleted all three files in a single path-scoped git rm + commit, explicitly excluding the unrelated pre-existing tools/build_db.py modification (never git add -A / git commit -a)"
  - "Used the clean-tree git archive route for the sdist oracle, not a working-tree build, per RESEARCH C-2 — avoids the 220-entry SOURCES.txt false positive"
  - "Did not assert on gh api community/profile — it reads origin/main, where SECURITY.md has never existed, and would pass a plan that did nothing (RESEARCH C-5)"

requirements-completed: []

coverage:
  - id: D1
    description: "things.md, SECURITY.md, autocomplete.md absent from firestarter_app working tree and HEAD"
    requirement: "LEGACY-04, LEGACY-05, LEGACY-07"
    verification:
      - kind: other
        ref: "evidence/171-02-deletion-commit.txt (git show --stat: 3 files changed, 129 deletions; git status --short shows only the excluded tools/build_db.py)"
        status: pass
    human_judgment: false
  - id: D2
    description: "All three files stay recoverable at d56424e1979edf7245cffb9ec3111c0469f5b23f with matching sha256-16 fingerprints"
    requirement: "LEGACY-04, LEGACY-05, LEGACY-07"
    verification:
      - kind: other
        ref: "evidence/171-02-recoverability-and-sweep.txt (autocomplete.md=6e3a0116f2a3759f, things.md=637974e9dcab7870, SECURITY.md=35077cac80e15a8a — all matched)"
        status: pass
    human_judgment: false
  - id: D3
    description: "Canonical Phase 69 audit record survives in meta, making the SECURITY.md deletion lossless"
    requirement: "LEGACY-05"
    verification:
      - kind: other
        ref: "evidence/171-02-recoverability-and-sweep.txt (PRESENT: 69-SECURITY.md at .planning/milestones/v1.12-phases/69-cli-command-surface-robustness-audit/)"
        status: pass
    human_judgment: false
  - id: D4
    description: "No replacement disclosure-policy language exists anywhere in firestarter_app (D-02 must-NOT guard)"
    requirement: "LEGACY-05"
    verification:
      - kind: other
        ref: "evidence/171-02-recoverability-and-sweep.txt (zero hits for 'report a vulnerability'/'security policy'/'responsible disclosure')"
        status: pass
    human_judgment: false
  - id: D5
    description: "No file in any of the three repositories links to the deleted paths, except one permitted historical hit"
    requirement: "LEGACY-04, LEGACY-05, LEGACY-07"
    verification:
      - kind: other
        ref: "evidence/171-02-recoverability-and-sweep.txt (sweep returns exactly firestarter/test/native/avr/test_eeprom28c_sdp/RED-BASELINE.md:637, a Phase 117 historical record — no action owed)"
        status: pass
    human_judgment: false
  - id: D6
    description: "Clean-tree sdist manifest is byte-identical before and after the deletions, 173 entries a side"
    requirement: "LEGACY-04, LEGACY-05, LEGACY-07"
    verification:
      - kind: other
        ref: "evidence/171-02-sdist-clean-tree-diff.txt (before=173, after=173, diff rc=0, zero matches for the three filenames)"
        status: pass
    human_judgment: false
  - id: D7
    description: "The firestarter_app test suite passes on Python 3.11, the version its CI pins"
    requirement: "LEGACY-04, LEGACY-05, LEGACY-07"
    verification:
      - kind: other
        ref: "evidence/171-02-py311-suite.txt (Python 3.11.16, firestarter.__file__ resolved inside firestarter_app, 1955 passed, 0 failed, 0 error)"
        status: pass
    human_judgment: false

# Metrics
duration: 20min
completed: 2026-09-01
status: complete
---

# Phase 171 Plan 02: Delete the Three Root-Level Stray Documents Summary

**Deleted `things.md`, `SECURITY.md` and `autocomplete.md` from the `firestarter_app` root in one path-scoped commit, and proved recoverability, no-smuggled-policy, packaging parity, and a passing py3.11 suite — LEGACY-04/05/07 deletion legs are discharged, but the requirements themselves stay open pending 171-03/171-04's provenance and gitlink legs.**

## Performance

- **Duration:** ~20 min
- **Started:** 2026-09-01T09:30:00Z
- **Completed:** 2026-09-01T09:42:45Z
- **Tasks:** 3/3 executed, all auto
- **Files modified:** 3 deleted in `firestarter_app`, 4 evidence files created in meta

## Accomplishments

- Re-verified the publish-then-delete gate from a fresh, independent wiki clone before touching anything: `Shell-Completion.md` present at commit `bf787fb`
- Read all three files before deletion: `things.md` is confirmed **7 lines / 265 bytes with no trailing newline** (not the 5 CONTEXT.md claims nor the 6 the ROADMAP claims — `wc -l` undercounts because it counts newline characters, and the file has none after its last line); `SECURITY.md` opens `# SECURITY.md` / `## Phase Security Audit` / `**Phase:** 69`; `autocomplete.md` confirmed as the Click-based `_FIRESTARTER_COMPLETE` text, matching what 171-01 published
- Deleted all three files in one `git rm` + commit (`c1416a6`) on the milestone branch, explicitly excluding the unrelated pre-existing `tools/build_db.py` modification — never used `git add -A` or `git commit -a`
- Proved recoverability at `d56424e1979edf7245cffb9ec3111c0469f5b23f` for all three files against their recorded sha256-16 fingerprints — exact matches
- Confirmed the canonical Phase 69 audit record survives untouched at `.planning/milestones/v1.12-phases/69-cli-command-surface-robustness-audit/69-SECURITY.md`
- Ran the D-02 must-NOT guard (`report a vulnerability` / `security policy` / `responsible disclosure`) across `firestarter_app` excluding `.planning/` — zero hits
- Ran the three-repository link sweep for all three filenames — exactly one hit, the permitted historical `RED-BASELINE.md:637` reference, left untouched
- Built the sdist twice from clean `git archive` extractions (never the live working tree) for `HEAD~1` and `HEAD` — both manifests have exactly 173 entries, the diff is empty, and zero entries match the three deleted filenames
- Ran the app's test suite in a scratch `uv venv --python 3.11` (resolved CPython 3.11.16) with `-o addopts=""` — **1955 passed, 0 failed, 0 error** in 290.27s
- Confirmed `firestarter.__file__` resolved to `/workspaces/firestarter_app/firestarter/__init__.py` (not the firmware namespace package) by running every command with `firestarter_app` as the working directory

## Task Commits

Each task was committed atomically:

1. **Task 1: Re-assert the page is live, then delete the three strays** - `c1416a6` (firestarter_app submodule, `chore(171-02)`) — deletion commit; `b72816ea` (meta, `docs(171-02)`) — evidence commit
2. **Task 2: Prove recoverability, sweep, and no smuggled policy** - `0a3cfba1` (meta, `docs(171-02)`) — evidence commit
3. **Task 3: Prove packaging is unaffected and the suite passes on py3.11** - `45469386` (meta, `docs(171-02)`) — evidence commit

## Files Created/Modified

- `firestarter_app/things.md` - deleted (7 lines, 265 bytes; single fact already on wiki `Home`)
- `firestarter_app/SECURITY.md` - deleted (Phase 69 audit record; canonical copy stays in meta, no replacement written)
- `firestarter_app/autocomplete.md` - deleted (content now live at wiki page `Shell-Completion`)
- `.planning/phases/171-stray-the-root-level-documentation-files/evidence/171-02-deletion-commit.txt` - the deletion commit's `git show --stat` plus the surviving `tools/build_db.py` exclusion
- `.planning/phases/171-stray-the-root-level-documentation-files/evidence/171-02-recoverability-and-sweep.txt` - three sha256-16 checks, the canonical-record assertion, the D-02 guard, and the full sweep output
- `.planning/phases/171-stray-the-root-level-documentation-files/evidence/171-02-sdist-clean-tree-diff.txt` - clean-tree before/after sdist manifest counts and diff, with the 220-entry false-positive cause named
- `.planning/phases/171-stray-the-root-level-documentation-files/evidence/171-02-py311-suite.txt` - interpreter version, `__file__` resolution, and the full pytest tail with the count line

## Decisions Made

None beyond the plan's own — Tasks 1-3 executed exactly as specified, with the RESEARCH.md corrections (C-2, C-4, C-5, C-7) honored throughout: the clean-tree sdist route was used instead of a working-tree build, `RED-BASELINE.md:637` was left untouched as historical-by-intent, `gh api community/profile` was never called, and `things.md`'s line count is reported as seven with the byte count and no-trailing-newline caveat.

## Deviations from Plan

### Auto-fixed Issues

None — plan executed exactly as written.

### Environment note (not a Rule 1-4 deviation)

The pytest run under the py3.11 scratch venv took longer than the harness's default 2-minute Bash timeout (it completed in 290.27s). The first two attempts were killed by the harness timeout mid-run; the third attempt reused the same venv (`uv pip install` did not need to repeat) with an explicit 480s timeout and completed cleanly with `1955 passed, 1 warning in 290.27s`. No test code, fixture, or configuration was touched — this was purely a tool-invocation timeout, not a defect in the suite or the app.

---

**Total deviations:** 0 auto-fixed. One tooling note (pytest runtime exceeded the default harness timeout; resolved by re-invoking with a longer timeout, no code changed).
**Impact on plan:** None. All evidence content is identical to what a single successful run would have produced.

## Issues Encountered

None beyond the timeout note above.

## Known Facts for the Record

- **`things.md` is seven lines, 265 bytes, no trailing newline** — both CONTEXT.md ("5 lines") and the ROADMAP ("six lines") are wrong; `wc -l` reports 6 because it counts newline characters and the file's last line has none.
- **`tools/build_db.py` is an explicit, unresolved exclusion.** It carries an unrelated uncommitted modification that predates Phase 171. It was not staged, not committed, not reverted, and not stashed by this plan — `git -C firestarter_app status --short` still reports ` M tools/build_db.py` after every task commit in this plan.
- **`SECURITY.md` never reached `origin/main`.** It exists only on `origin/beta` and the milestone branch, so `gh api repos/henols/firestarter_app/community/profile -q .files.security_policy` returned `null` before this plan ran and would still return `null` after, regardless of this work — that check is vacuous and was correctly never used as a verification leg (RESEARCH C-5). This plan therefore **prevents** a misrepresentation from becoming live at the milestone merge; it does not remediate a live one. The Security-tab-is-empty observation is deferred to the milestone merge.
- **`github.com/henols/firestarter_app/blob/main/autocomplete.md` still resolves (HTTP 200)** until the milestone branch merges to `main`, and still serves the stale argcomplete-era text that predates the Click swap. This is a sequencing fact, not a criterion failure — measured directly: `curl -s -o /dev/null -w "%{http_code}" https://raw.githubusercontent.com/henols/firestarter_app/main/autocomplete.md` returned `200`.
- **LEGACY-04, LEGACY-05 and LEGACY-07 are NOT complete at this plan's close.** Each spans plans 171-02 through 171-04. This plan discharges the deletion leg of all three (D-01, D-05 for the outright deletions; the delete half of D-03's publish-then-delete pair for LEGACY-07). Their provenance rows (`MIGRATION-TABLE.md`) land in 171-03, and the meta gitlink re-pin lands in 171-04. No requirement checkbox was flipped by this plan.

## User Setup Required

None — no external service configuration required. This plan made no live public writes (the wiki write already landed in 171-01).

## Next Phase Readiness

- 171-03 is unblocked: all three files are deleted, all three are proven recoverable at `d56424e`, and their sha256-16 fingerprints are the exact values 171-03's `MIGRATION-TABLE.md` rows will cite.
- 171-04 is unblocked for its gitlink re-pin: `firestarter_app` HEAD is now `c1416a6` on `gsd/v1.35-documentation-consolidation-wiki-migration`, one commit ahead of the pre-existing stale meta gitlink (which recorded `50f85b2`, already two commits behind before this plan even started — Phase 170's un-pinned commits plus this plan's deletion commit are both still pending re-pin).
- No blockers. Pre-existing meta drift (`M .planning/config.json`, `M .planning/notes/dev-test-sequence-cost-model.md`, `M firestarter`, `M firestarter_app` gitlinks) was present before this plan started, is not this plan's work, and was left untouched throughout — confirmed by `git status --short` after every commit in this plan showing only the intended path staged.

---
*Phase: 171-stray-the-root-level-documentation-files*
*Completed: 2026-09-01*

## Self-Check: PASSED

- FOUND: `.planning/phases/171-stray-the-root-level-documentation-files/evidence/171-02-deletion-commit.txt`
- FOUND: `.planning/phases/171-stray-the-root-level-documentation-files/evidence/171-02-recoverability-and-sweep.txt`
- FOUND: `.planning/phases/171-stray-the-root-level-documentation-files/evidence/171-02-sdist-clean-tree-diff.txt`
- FOUND: `.planning/phases/171-stray-the-root-level-documentation-files/evidence/171-02-py311-suite.txt`
- FOUND: commit `c1416a6` (firestarter_app submodule)
- FOUND: commit `b72816ea` (meta)
- FOUND: commit `0a3cfba1` (meta)
- FOUND: commit `45469386` (meta)
