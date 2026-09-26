---
phase: 172-policy-one-tracker-protected-main
plan: 09
subsystem: infra
tags: [closing-sweep, requirements, gitlinks, worktrees, wiki-checkers, legacy-01]

# Dependency graph
requires:
  - phase: 172-policy-one-tracker-protected-main
    provides: "plan 172-08's three merged pull requests and live default-branch surfaces — the final state this sweep verifies"
provides:
  - "The three `tools/wiki/` checkers green against fresh clones at the phase's final state, with the eleventh page live"
  - "LEGACY-01 green on the merits across all four surfaces, with the scanner hazard identified and corrected"
  - "Both submodule gitlinks re-pinned and proven equal per submodule; the phase's throwaway worktrees gone and four pre-existing ones intact"
  - "POLICY-01, POLICY-02, POLICY-03 and LEGACY-01 marked complete, each traceable to a named evidence file"
  - "Four explicit non-claims and three carried findings, so Phase 173's honesty ledger inherits them stated rather than having to rediscover them"
affects: [173-policy-04, 173-policy-05]

# Actuals (#2634)
actuals:
  tokens: 3100
  tasks: 3
  commits: 5

tech-stack:
  added: []
  patterns:
    - "scoping a repository-wide grep gate to `git ls-files` so gitignored scratch cannot produce a false RED, while using GNU grep so an ignore-aware scanner cannot produce a false GREEN"
    - "writing the requirement-to-evidence sweep BEFORE flipping any checkbox, and confirming each cited file exists and is non-empty first"
    - "filing a finding as a `todos/pending/` entry when the plan forbids the ROADMAP write that a numbered backlog row would need"

key-files:
  created:
    - .planning/phases/172-policy-one-tracker-protected-main/evidence/172-09-full-suite-final.txt
    - .planning/phases/172-policy-one-tracker-protected-main/evidence/172-09-legacy01-final.txt
    - .planning/phases/172-policy-one-tracker-protected-main/evidence/172-09-gitlink-equality.txt
    - .planning/phases/172-policy-one-tracker-protected-main/evidence/172-09-closing-sweep.txt
    - .planning/todos/pending/2026-09-02-rulesets-block-stable-release-version-bump.md
  modified:
    - .planning/REQUIREMENTS.md

key-decisions:
  - "The LEGACY-01 scanner had to be corrected in TWO opposing directions, both measured. `grep` on PATH in this devcontainer is ugrep 7.8.4, which honours .gitignore: over the same paths with the same exclusions it reports 0 matches where GNU grep reports 38. The plan's bare-grep leg would therefore have gone GREEN by declining to scan — precisely the T-172-04 vacuity failure — and the without-exclusion counter could not have caught it, because ugrep under-scans that leg identically. But a raw GNU-grep directory walk is a false RED: all 38 matches are untracked gitignored scratch (.v1.34-arms, two sibling py32 worktrees, .venv dist-info METADATA of already-published wheels). Resolved by GNU grep scoped to `git ls-files`, plus a plain walk of the fresh wiki clone — exactly the set a consumer clone contains. Zero on all four surfaces."
  - "The plan's Task 1 expectation that the page count would move from 10 to 11 was already stale: 172-03-full-suite.txt already read `OK: 11 pages,` because plan 172-01 published the page before plan 172-03 ran its suite. All three OK lines are byte-identical to the mid-phase run, making this a stability result across the merges and the ruleset recreate rather than a progression one, and the plan's `OK: 10 pages` hard stop never armed because its condition was false when written."
  - "The gitlink re-pin was proven to sweep up nothing from earlier work rather than merely asserted: `git rev-list --count recorded..actual` is exactly 1 per submodule and the single commit in each range is plan 172-04's own. Phase 171 plan 04's re-pin legitimately carried earlier movement and had to say so; this one does not, and says that instead."
  - "This plan's own artifact spec is self-contradictory for the gitlink file — `min_lines: 4` against an acceptance criterion of `exactly two lines`. The two data lines were kept assertion-exact and the line floor met with real content (the worktree inventory), with the contradiction recorded in the file; the `exactly two lines` prose is the clause that yields."
  - "FOUR pre-existing worktrees had to survive, one more than the plan's read_first names. It mentions only `firestarter_py32_ci`; `firestarter_app` also carries `firestarter_app_py32` and the two pinned `.v1.34-arms` host arms, whose loss would invalidate recorded bench rows. All four were recorded by name and all four are still listed."
  - "The plan's instruction for the Actions-bypass non-claim row was WRONG about its own phase and was not followed literally. It asks for a row saying the bypass is 'configured and, unless the probe was run, unproven'. No Actions bypass exists or ever did: Integration:15368 was rejected with HTTP 422 because all three repositories are owned by a personal User account with no owner organization, which made the planned throwaway-repo probe moot rather than merely unrun. The row records what actually happened, the D-09 revision to DeployKey:null:always, the zero-deploy-key measurement that makes it inert today, and the named residual that a null actor_id covers any future deploy key."
  - "An unfulfilled obligation from 172-05 was discharged: its evidence required the release-workflow breakage be carried 'for backlog filing', and it never had been. Filed as a `todos/pending/` entry rather than a 999.x ROADMAP row, because this plan is forbidden from writing ROADMAP.md and its own verify asserts that; promotion to a numbered phase is the orchestrator's write. The workflow facts were re-verified against the live files rather than copied from the earlier write-up, which surfaced an asymmetry that write-up missed."

requirements-completed: [POLICY-01, POLICY-02, POLICY-03, LEGACY-01]

coverage:
  - id: D1
    description: "Three checkers green against fresh clones with the eleventh page present"
    requirement: "POLICY-01"
    verification:
      - kind: other
        ref: "evidence/172-09-full-suite-final.txt (three `OK: ` lines, `OK: 11 pages,`, exit 0, clone shas recorded, zero working-tree paths)"
        status: pass
    human_judgment: false
  - id: D2
    description: "LEGACY-01 green over the final state of every surface the phase touched, non-vacuously"
    requirement: "LEGACY-01"
    verification:
      - kind: other
        ref: "evidence/172-09-legacy01-final.txt (0 matches on all four surfaces; planning_excluded_matches=46 across 17 files; the ugrep-vs-GNU-grep 0-vs-38 measurement)"
        status: pass
    human_judgment: false
  - id: D3
    description: "Both gitlinks equal their submodules' heads, per submodule, with the phase's worktrees cleaned"
    requirement: "POLICY-03"
    verification:
      - kind: other
        ref: "evidence/172-09-gitlink-equality.txt (two OK lines, both on the milestone branch; three throwaways gone, four pre-existing intact)"
        status: pass
    human_judgment: false
  - id: D4
    description: "Each of the four requirements marked complete only against a named, existing evidence file"
    requirement: "POLICY-02"
    verification:
      - kind: other
        ref: "evidence/172-09-closing-sweep.txt (four requirement blocks, nine cited files all confirmed non-empty before any box was flipped) + REQUIREMENTS.md (8-line diff, nothing else touched)"
        status: pass
    human_judgment: false

duration: ~25min active
completed: 2026-09-02
status: complete
---

# Phase 172 Plan 09: Closing sweep Summary

**The three checkers green against fresh clones with all 11 pages live, LEGACY-01 green on the merits across four surfaces after correcting a scanner that would have passed it vacuously, both gitlinks re-pinned and proven equal per submodule, and all four requirements marked complete against named evidence — with four non-claims and three findings written down beside them rather than absorbed into the marks.**

## Performance

- **Duration:** ~25 min active
- **Completed:** 2026-09-02
- **Tasks:** 3, all `auto`
- **Files modified:** 5 created, 1 modified

## Accomplishments
- Ran the full three-checker suite against a fresh wiki clone and fresh `beta` clones of both sub-repositories — never the working trees — green at `exit 0` with `OK: 11 pages`
- Caught and corrected a scanner hazard that would have made the LEGACY-01 phase gate meaningless in either direction, and recorded the measurement both ways
- Re-pinned both gitlinks in a single commit and proved per submodule that each advanced exactly one commit, plan 172-04's own
- Removed the three throwaway PR worktrees while preserving all four pre-existing ones, one of which the plan never named
- Marked POLICY-01, POLICY-02, POLICY-03 and LEGACY-01 complete with an 8-line `REQUIREMENTS.md` diff and `ROADMAP.md` provably untouched
- Discharged an obligation 172-05 left open, and corrected the plan's own instruction where it misdescribed its phase

## Task Commits

1. **Task 1: full suite + LEGACY-01 against the final state** - `a8303978` (docs)
2. **Task 2: gitlink re-pin** - `4ab6b4fa` (chore) — the two gitlinks themselves
3. **Task 2: gitlink equality + worktree record** - `d08c230a` (docs)
4. **Task 3: sweep, requirement marks, and the filed todo** - `7bece05a` (docs)

**Plan metadata:** captured in this SUMMARY's own commit.

## Files Created/Modified
- `evidence/172-09-full-suite-final.txt` - the three OK lines, `exit 0`, fresh clone shas, and the correction to the plan's stale page-count expectation
- `evidence/172-09-legacy01-final.txt` - zero on four surfaces, the 46-match `.planning` exclusion cost, and the two-directional scanner analysis
- `evidence/172-09-gitlink-equality.txt` - two per-submodule equality lines plus the full worktree inventory
- `evidence/172-09-closing-sweep.txt` - four requirement blocks, four non-claims, three carried findings
- `.planning/todos/pending/2026-09-02-rulesets-block-stable-release-version-bump.md` - the release-path breakage, filed
- `.planning/REQUIREMENTS.md` - four checkboxes and four status rows, nothing else

## Decisions Made
See `key-decisions` in frontmatter.

## Deviations from Plan

### Auto-fixed Issues

**1. [Gate defect] The plan's LEGACY-01 verify leg would have passed vacuously**
- **Found during:** Task 1
- **Issue:** The leg runs a bare `grep -rInE`. On PATH here that is ugrep 7.8.4, which honours `.gitignore`.
- **Root cause:** Measured — 0 matches under ugrep against 38 under GNU grep, same pattern and exclusions. The leg's own without-exclusion guard could not have caught it, since ugrep under-scans that half identically.
- **Fix:** Ran the scan with `/usr/bin/grep` scoped to `git ls-files` per repository, plus a plain recursive walk of the fresh wiki clone. Also established that a raw GNU-grep walk is a false RED, all 38 being untracked gitignored scratch.
- **Verification:** both counts recorded in `evidence/172-09-legacy01-final.txt`; result is 0 on all four surfaces on the merits
- **Committed in:** `a8303978`

### Documented Non-Fixes (out of scope, not auto-fixed)

**1. [Spec conflict] `firestarter_app` is not porcelain-clean**
- **Issue:** Task 2's second verify leg asserts an empty `git -C firestarter_app status --porcelain`. It is not empty: `tools/build_db.py` carries one unstaged modification.
- **Root cause:** The unattributed rename filed as Backlog 999.45. Product source, which this milestone's scope note forbids editing.
- **Fix:** None. The same assertion was documented as a non-fix by 172-07 for the same line. The gitlink equality is unaffected — a gitlink records a commit sha and the file is unstaged.
- **Committed in:** not committed, by design

**2. [Spec conflict] The gitlink evidence file cannot satisfy both of its own requirements**
- **Issue:** `min_lines: 4` in the artifact block against `exactly two lines` in the acceptance criteria.
- **Fix:** Two assertion-exact data lines, floor met with the worktree inventory, contradiction recorded in the file itself.
- **Committed in:** `d08c230a`

**3. [Stale plan instruction] The Actions-bypass non-claim row as specified describes a state that never existed**
- **Issue:** Task 3 asks for a row saying the bypass is "configured and, unless the probe was run, unproven".
- **Root cause:** `Integration:15368` was rejected with HTTP 422 — personal-account ownership, no owner organization — so the probe was moot, not merely unrun. D-09 was revised to `DeployKey:null:always`.
- **Fix:** Recorded what actually happened, with the zero-deploy-key measurement and the null-actor residual. Not followed literally, because doing so would have recorded a fiction.
- **Committed in:** `7bece05a`

**Total deviations:** 1 auto-fixed, 3 documented non-fixes.

## Authentication Gates

None. `gh` already authenticated; three anonymous `--depth 1` clones needed none.

## Known Stubs

`Wiki check` is registered with Actions but has **zero runs** — its first fire is the weekly cron or a manual `workflow_dispatch`. Its three legs are green against fresh clones twice over (172-03 and this plan), so the confidence is real, but "registered" and "observed green in CI" are different facts and only the first is true today. Recorded as NON-CLAIM 3 in the sweep.

## Threat Flags

None new. T-172-35 (a mark ahead of its evidence) discharged by writing the sweep first and confirming all nine cited files non-empty before flipping anything; T-172-36 (a green run against working trees) by fresh clones and zero `/workspaces/firestarter*` checker arguments; T-172-04 (a vacuous green) discharged twice — by the 46-match non-vacuity counter and by catching the ugrep under-scan the counter could not have caught; T-172-37 (a stale gitlink) by per-submodule equality; T-172-38 (a roadmap write) by asserting `ROADMAP.md` unchanged against both HEAD and HEAD~1; T-172-39 (marks absorbing non-claims) by the four explicit non-claim rows.

## Self-Check: PASSED

- All five created files present and non-empty → FOUND
- Task 1 leg 1: `exit 0` ✓, exactly three `^OK: ` lines ✓, `OK: 11 pages,` ✓, `Contributing.md` in the fresh clone ✓, zero working-tree paths ✓
- Task 1 leg 2: `rc=0` ✓, `OK: no page links` ✓, `planning_excluded_matches=46` > 0 ✓
- Task 2 leg 1: two ` OK$` lines ✓, no `STALE` ✓, two milestone-branch lines ✓
- Task 2 leg 2: three throwaway dirs gone ✓, no worktree list names them ✓, `firestarter_py32_ci` intact ✓, `firestarter` clean ✓, `firestarter_app` clean ✗ (the one documented non-fix above)
- Task 3 leg 1: all four ids present ✓, all nine cited files exist, are non-empty and are cited ✓, bypass disposition carried ✓
- Task 3 leg 2: three `[x]` POLICY ✓, `[x]` LEGACY-01 ✓, three `Complete` rows ✓, LEGACY-01 row ✓, zero `Phase 172 | Pending` ✓, `ROADMAP.md` unchanged vs HEAD~1 ✓

Next: **Phase 172 is complete — all 9 plans done and all 4 requirements marked.** Phase 173 (CLOSE — Beta Cut Under Protection, Close Procedure & Honesty Ledger) is the milestone's last phase, and inherits three carried findings plus four stated non-claims from the sweep.
