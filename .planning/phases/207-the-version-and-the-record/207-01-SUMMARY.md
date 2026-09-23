---
phase: 207-the-version-and-the-record
plan: 01
subsystem: release
tags: [version-bump, gitlink, release-process, beta-sync]

# Dependency graph
requires:
  - phase: 206-session-lease-and-devtest-retirement
    provides: closed v1.41 phase with 3.0.0b48/3.0.0b33 base and a green regression gate
provides:
  - "3.1.0b1 in both sub-repos, each bump sitting directly on a merge of origin/beta (D-01)"
  - "a proven conflict-free ship merge, oracle-checked by each sub-repo's own publisher script"
  - "meta gitlinks advanced to both sub-repo HEADs in one commit"
  - "a corrected README upgrade-order sentence that no longer overclaims every mismatched pair fails loudly"
affects: [207-02-wiki-content, 207-03-wiki-push, ship]

# Actuals (#2632)
actuals:
  tokens: 450
  tasks: 3
  commits: 7
  plan_head_before: "N/A - multi-repo plan, no single-repo commit ledger; see per-repo commit table below"

tech-stack:
  added: []
  patterns:
    - "Merge origin/beta into the milestone branch before a version bump, so the bump's direct parent is the merge (D-01) and the eventual ship PR has no version-line conflict"

key-files:
  created:
    - .planning/phases/207-the-version-and-the-record/evidence/207-01-oracles.txt
  modified:
    - firestarter_fw/include/version.h
    - firestarter_app/firestarter/__init__.py
    - firestarter_app/README.md
    - firestarter_fw (gitlink)
    - firestarter_app (gitlink)

key-decisions:
  - "D-01 (operator, locked): merge origin/beta into v1.41-verification-to-host in each sub-repo before bumping, so the bump commit's direct parent is the beta merge"
  - "F6 option A: correct the README's upgrade-order claim in its own commit after the version bump, keeping the version commit single-file"

requirements-completed: [REL-01]

coverage:
  - id: D1
    description: "firestarter_fw/include/version.h and firestarter_app/firestarter/__init__.py both read 3.1.0b1, each moved by one single-file commit sitting on a merge of origin/beta"
    requirement: "REL-01"
    verification:
      - kind: other
        ref: "PASS-207-01-T1 (firmware) — cd firestarter_fw && [task verify leg, see evidence file]"
        status: pass
      - kind: other
        ref: "PASS-207-01-T2 (app) — cd firestarter_app && [task verify leg, see evidence file]"
        status: pass
    human_judgment: false
  - id: D2
    description: "Each sub-repo's publisher (update_version.py --dry-run on GITHUB_REF=refs/heads/beta) prints exactly DRY_RUN: 3.1.0b1, and merge-tree against origin/beta prints exactly one line in both repos"
    requirement: "REL-01"
    verification:
      - kind: other
        ref: "PASS-207-01-ORACLE — evidence/207-01-oracles.txt"
        status: pass
    human_judgment: false
  - id: D3
    description: "Meta gitlinks firestarter_fw and firestarter_app advanced to the sub-repo HEADs in one two-path commit; README upgrade-order sentence corrected"
    requirement: "REL-01"
    verification:
      - kind: other
        ref: "PASS-207-01-PAIR — evidence/207-01-oracles.txt"
        status: pass
    human_judgment: false
  - id: D4
    description: "App gates green on Python 3.11 (ruff check, ruff format --check, 2363 pytest passed) and the firmware tests/ tree green (316 passed) on the bumped tree"
    requirement: "REL-01"
    verification:
      - kind: other
        ref: "pytest tests/ -q -p no:cacheprovider (firestarter_fw): 316 passed in 10.10s"
        status: pass
      - kind: other
        ref: "python -m pytest tests/ -o addopts=\"\" -p no:cacheprovider -q (firestarter_app): 2363 passed in 216.66s"
        status: pass
      - kind: other
        ref: "ruff check / ruff format --check (firestarter_app): both clean"
        status: pass
    human_judgment: false
  - id: D5
    description: "Nothing pushed, tagged or released from this plan; no v1.41 branch or 3.1.0* tag exists on any remote; gh releases count is 0"
    requirement: "REL-01"
    verification:
      - kind: other
        ref: "PASS-207-PROHIBITION — evidence/207-01-oracles.txt"
        status: pass
    human_judgment: false

duration: 16min
completed: 2026-09-23
status: complete
---

# Phase 207 Plan 1: The version and the record Summary

**Both sub-repos moved to `3.1.0b1` in one inspectable commit pair, each bump sitting directly on a merge of `origin/beta` (D-01), with the ship merge proven conflict-free by each publisher's own dry-run.**

## Performance

- **Duration:** ~16 min
- **Started:** 2026-09-23 (approx. 15:00 UTC)
- **Completed:** 2026-09-23T15:16:11Z
- **Tasks:** 3
- **Files modified:** 5 (2 version files, 1 README, 2 gitlinks) + 1 evidence file created

## Accomplishments
- Merged `origin/beta` (3.0.0b35) into `firestarter_fw`'s `v1.41-verification-to-host`, then bumped `include/version.h` from `3.0.0b35` to `3.1.0b1` in a single-file commit sitting directly on that merge.
- Merged `origin/beta` (3.0.0b50) into `firestarter_app`'s `v1.41-verification-to-host`, then bumped `firestarter/__init__.py` from `3.0.0b50` to `3.1.0b1` in a single-file commit whose body names the firmware sha, followed by a separate README commit correcting the upgrade-order claim.
- Rebuilt the app's `.venv311` (Python 3.11.16) after the container rebuild left it dangling, and ran the app's CI-parity gates on the bumped tree: `ruff check` clean, `ruff format --check` clean, `pytest` 2363 passed (matching the Phase 206 baseline exactly).
- Ran the firmware's `tests/` tree after its commit (it asserts an empty porcelain): 316 passed, matching the pre-phase baseline.
- Advanced the meta gitlinks for `firestarter_fw` and `firestarter_app` to their new HEADs in one commit, staged by explicit pathspec so none of the unrelated dirty meta files rode along.
- Proved the whole pair with three verify legs: `PASS-207-01-PAIR` (commit shapes, gitlink equality, README wording), `PASS-207-01-ORACLE` (both publishers print `DRY_RUN: 3.1.0b1`, both `merge-tree` checks print one line after a fresh fetch), and `PASS-207-PROHIBITION` (no bump commit reached `beta`/`main`, no `v1.41-verification-to-host` branch or `3.1.0*` tag on either remote, no meta `v1.41` tag, `gh api` release count is 0).

## Task Commits

Each task was committed atomically, across three repositories:

**Task 1 (firmware end to end):**
1. `firestarter_fw` `00c90fc` — `Merge origin/beta (3.0.0b35) into v1.41-verification-to-host before the 3.1.0b1 bump` (merge)
2. `firestarter_fw` `a55f2d8` — `chore(207-01): bump firmware version 3.0.0b35 -> 3.1.0b1` (chore)

**Task 2 (app half):**
3. `firestarter_app` `610fb96` — `merge: bring origin/beta (3.0.0b50) into the v1.41 milestone branch before the 3.1.0b1 bump` (merge)
4. `firestarter_app` `67f93e2` — `chore(207-01): bump app version 3.0.0b50 -> 3.1.0b1` (chore)

**Task 3 (README fix, gitlink advance, whole-pair proof):**
5. `firestarter_app` `2a08c7d` — `docs(207-01): tell readers to upgrade the CLI before the firmware` (docs)
6. `/workspaces` (meta) `d347dd3f` — `chore(207-01): advance firestarter_fw and firestarter_app gitlinks` (chore)

**Plan metadata:** `350bb121` (docs: complete 207-01 plan)

_Note: no TDD tasks in this plan; each commit above is a single production step._

## Files Created/Modified

- `firestarter_fw/include/version.h` — line 11 now `#define VERSION "3.1.0b1"`
- `firestarter_app/firestarter/__init__.py` — line 1 now `__version__ = "3.1.0b1"`
- `firestarter_app/README.md` — replaced the false "every mismatched pair fails loudly" claim with an upgrade-order lead and a pointer to the wiki's Breaking Changes page
- `firestarter_fw` (meta gitlink) — now points at `a55f2d80ed55042f3e81bdbc994c9ab949f386cc`
- `firestarter_app` (meta gitlink) — now points at `2a08c7d9be6ab3229721f2cdaddfa4f939c14a83`
- `.planning/phases/207-the-version-and-the-record/evidence/207-01-oracles.txt` (new) — remote-ref baseline plus every oracle command and its output for both sub-repos

Brought in by the D-01 merges (not authored by this plan, from `origin/beta`):
- `firestarter_fw/.github/CONTRIBUTING.md`
- `firestarter_app/.planning/codebase/STACK.md`

## Decisions Made

- **D-01 (operator, locked):** merged `origin/beta` into each milestone branch before bumping. Verified: in both repos, the bump commit's first parent is the merge commit, whose own first parent is the pre-phase tip and whose second parent is `origin/beta`.
- **F6 option A (research recommendation, taken):** the README fix landed in its own commit after the version bump, keeping the version commit single-file and inspectable by `git show --stat`.
- Both `origin/beta` values matched the plan's recorded expectation exactly (`3.0.0b35` firmware, `3.0.0b50` app) — no deviation from the recorded beta baseline was needed.

## Deviations from Plan

### Auto-fixed Issues

None required — no Rule 1/2/3 auto-fixes were needed. Both `origin/beta` versions matched the plan's expected values, and every gate passed on the first implementation attempt.

### Environmental Note (not a deviation from plan content)

**Transient SSH flake during the Task 3 ORACLE verify leg.** The first attempt at the combined `for r in firestarter_app firestarter_fw; do git fetch ... && git fetch origin beta main ...` loop failed with `git@github.com: Permission denied (publickey)` on the very first SSH call in that shell invocation. Individual `git fetch` calls immediately before and after this failure succeeded without incident, and re-running the exact same combined command succeeded cleanly (`PASS-207-01-ORACLE`). This reads as a transient SSH-agent connection race under back-to-back `git fetch` calls in this container, not a defect in the plan, the publisher scripts, or the repository state. No production commit or verification result was affected — the leg was re-run and passed before being recorded. Logged here per the operator's "re-check COMMITS after any interrupt" standing practice, even though nothing here needed recovery.

---

**Total deviations:** 0 auto-fixed content deviations. 1 environmental flake noted (transient SSH failure, resolved by retry, no impact on results).
**Impact on plan:** None. All three PASS markers were captured from a clean, successful run.

## Issues Encountered

None, aside from the transient SSH flake documented above (resolved by retry, no lasting effect).

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- REL-01 is satisfied: both repos carry `3.1.0b1`, each bump sitting on a proven-clean merge of `origin/beta`, oracle-verified by each publisher's own dry-run.
- Nothing was pushed, tagged, or released. `v1.41-verification-to-host` remains local-only and unpublished in all three repositories, confirmed after this plan's own commits.
- Plan 207-02 (wiki content, local) and Plan 207-03 (wiki push, operator-gated) are next; neither is blocked by anything in this plan.
- The orchestrator owns `.planning/STATE.md`, `.planning/ROADMAP.md`, and `.planning/REQUIREMENTS.md` per this plan's dispatch instructions — none of them were touched by this executor. The orchestrator should hand-mark REL-01 in REQUIREMENTS.md after reviewing this SUMMARY; every REL-01 must-have truth listed in the plan's frontmatter holds as verified above.

## Self-Check: PASSED

- `[ -f /workspaces/firestarter_fw/include/version.h ]` → FOUND, line 11 reads `#define VERSION "3.1.0b1"`.
- `[ -f /workspaces/firestarter_app/firestarter/__init__.py ]` → FOUND, line 1 reads `__version__ = "3.1.0b1"`.
- `[ -f /workspaces/firestarter_app/README.md ]` → FOUND, carries the corrected upgrade-order sentence.
- `[ -f /workspaces/.planning/phases/207-the-version-and-the-record/evidence/207-01-oracles.txt ]` → FOUND, carries both `DRY_RUN: 3.1.0b1` lines and all three PASS markers.
- `git -C /workspaces/firestarter_fw log --oneline --all | grep -q a55f2d8` → FOUND.
- `git -C /workspaces/firestarter_app log --oneline --all | grep -q 2a08c7d` → FOUND.
- `git -C /workspaces log --oneline --all | grep -q d347dd3f` → FOUND.
- All task-level `<acceptance_criteria>` re-verified: PASS-207-01-T1, PASS-207-01-T2, PASS-207-01-PAIR, PASS-207-01-ORACLE, PASS-207-PROHIBITION all printed.
- Plan-level `<verification>` re-run: all five checks pass (see coverage block above).
- `git rev-parse --abbrev-ref HEAD` prints `v1.41-verification-to-host` in `/workspaces`, `/workspaces/firestarter_app`, and `/workspaces/firestarter_fw`.

---
*Phase: 207-the-version-and-the-record*
*Completed: 2026-09-23*
