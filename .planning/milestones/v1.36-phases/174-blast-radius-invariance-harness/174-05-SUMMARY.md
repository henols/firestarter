---
phase: 174-blast-radius-invariance-harness
plan: 05
subsystem: testing
tags: [ci, github-actions, rekey-ledger, dedup_fingerprint, phase-closeout, cost-measurement, comment-hygiene]

requires:
  - phase: 174-blast-radius-invariance-harness (plans 01, 03)
    provides: "tools/rekey/check_rekey_ledger.py (D-13), the six-row rekey_ledger.py, the v1.36 Re-Key Ledger MILESTONES.md section"
provides:
  - ".github/workflows/rekey-ledger-check.yml: the registered additional CI leg for the cross-tree ledger check, triggered on beta and gsd/**, proven to fire by local invocation and simulated cross-tree checkout"
  - ".planning/MILESTONES.md: the declared-re-key protocol (behaviour-first, separate-commit re-key, before-hash never overwritten) naming both runners, plus the phase's self-measured cost/hygiene/boundary/pre-existing-RED closing paragraph"
  - "evidence/174-05-checker-fires.txt: parsed trigger lists, clean + fail-closed local invocations, a simulated meta+sibling cross-tree checkout, the resolved gitlink SHA, and an explicit unproven-on-GitHub declaration with the operator's one-line confirmation"
  - "evidence/174-05-phase-closeout.txt: five numbered whole-phase audits (comment sweep, scope boundary, cost, pre-existing RED, dependency set)"
affects: ["175 (read-back gating)", "177", "178", "179", "181"]

actuals:
  tokens: 5200
  tasks: 2
  commits: 2

tech-stack:
  added: []
  patterns:
    - "Gitlink-SHA-resolved cross-tree checkout (git rev-parse HEAD:<submodule> feeding actions/checkout's ref:), never submodules: recursive, extending the catalog-sync-check.yml structural analog"
    - "Workflow reasoning carried entirely in name: fields, zero # comments anywhere in the YAML, per the project's absolute zero-comments rule extended to CI config"
    - "Whole-phase measurement pass distinct from per-file gates -- five numbered audits run once across every file the phase touched, not re-derived task by task"

key-files:
  created:
    - .github/workflows/rekey-ledger-check.yml
    - .planning/phases/174-blast-radius-invariance-harness/evidence/174-05-checker-fires.txt
    - .planning/phases/174-blast-radius-invariance-harness/evidence/174-05-phase-closeout.txt
  modified:
    - .planning/MILESTONES.md

key-decisions:
  - "The workflow resolves the firestarter_app checkout ref via `git rev-parse HEAD:firestarter_app` inside the checked-out meta tree (the gitlink commit), not via catalog-sync-check.yml's same-branch-name-else-beta heuristic -- the ledger check needs the EXACT submodule commit the meta tree under test pins, which is a more precise and more directly falsifiable resolution than a branch-name guess, and it stays inside the plan's 'resolved ref' instruction without ever setting `submodules:` on the checkout action."
  - "On-GitHub scheduling is declared explicitly UNPROVEN rather than asserted. This sandbox cannot cause GitHub Actions to run a workflow; the evidence file states this plainly and names the exact `gh run list --workflow=rekey-ledger-check.yml` command the operator runs to close the gap -- per the plan's own instruction not to represent an unobserved run as observed."
  - "Cost timing used a manual `date +%s.%N` wrapper instead of `/usr/bin/time`, which is not installed in this devcontainer (confirmed: `rc=127`, 'No such file or directory'). This is a Rule 3 blocking-tooling substitution, not a plan defect -- the plan's action text asks to 'time' the modules, not to use a specific binary, and the measured number (7.92s) is what both pytest's own trailer (7.32s) and the wrapper agree on within measurement noise."

patterns-established:
  - "A CI workflow's cross-tree ref is resolved from the gitlink itself (git rev-parse HEAD:<path>), giving a workflow an exact, falsifiable, non-branch-dependent pin to the sub-repo commit the meta tree under test actually records."

requirements-completed: [GATE-06]

coverage:
  - id: D1
    description: "rekey-ledger-check.yml is registered with push/pull_request triggers naming beta and the gsd/** milestone-branch glob (never main-only), path filters covering MILESTONES.md/tools/rekey/the firestarter_app gitlink/its own filename, an explicit gitlink-resolved sub-repo checkout with no recursive submodule fetching, and a run step invoking check_rekey_ledger.py whose non-zero exit fails the job"
    requirement: "GATE-06"
    verification:
      - kind: integration
        ref: "evidence/174-05-checker-fires.txt (trigger parse: has_beta=True, has_gsd_glob=True, recursive_submodules=False, comment_lines=0, push_and_pr=True)"
        status: pass
      - kind: integration
        ref: "evidence/174-05-checker-fires.txt (clean local invocation, rc=0, OK: line; fail-closed invocation against a nonexistent checkout, rc=2, ERROR: line; simulated meta+sibling checkout, rc=0)"
        status: pass
    human_judgment: true
    rationale: "The trigger configuration, checkout shape and local invocation are all mechanically proven in this environment, but GitHub Actions has never actually scheduled a run of this workflow from here -- that half of D1 (the on-GitHub fire) requires the operator's `gh run list --workflow=rekey-ledger-check.yml` after this commit reaches GitHub, named explicitly in the evidence file."
  - id: D2
    description: "The declared-re-key protocol (behaviour change first turns the gate RED, a separate commit touching only after_hash + the matching MILESTONES.md row turns it green, before_hash never overwritten) is stated in the v1.36 Re-Key Ledger section naming both runners, for Phases 175 through 181 to read"
    requirement: "GATE-06"
    verification:
      - kind: unit
        ref: "grep -q 'separate commit' .planning/MILESTONES.md; grep -q 'rekey-ledger-check.yml' .planning/MILESTONES.md"
        status: pass
    human_judgment: false
  - id: D3
    description: "The phase's own cost, comment hygiene, scope boundary and pre-existing-RED claims are measured once across the whole phase (not per-file) and transcribed: seven zero-comment files, four shebang-only files, zero HTML comment openers, zero YAML comments, empty production/firmware porcelain, the five new modules' 110 tests at 7.92s against the measured 740.92s baseline, and tests/test_skip_census.py's three pre-existing failures re-confirmed unchanged"
    requirement: "GATE-06"
    verification:
      - kind: unit
        ref: "evidence/174-05-phase-closeout.txt (all five numbered audits; 110 passed in firestarter_app tests/test_blast_radius_invariance.py + test_rekey_ledger.py + test_devtest_issue_corpus.py + test_part_number_delta_drift.py)"
        status: pass
      - kind: integration
        ref: "firestarter_app/tests/test_skip_census.py standalone run: 3 failed, 2 passed in 548.83s, all three TimeoutExpired, file porcelain empty"
        status: pass
    human_judgment: false

duration: 50min
completed: 2026-09-03
status: complete
---

# Phase 174 Plan 05: Register the Ledger Check Where It Fires, Close the Phase Summary

**`rekey-ledger-check.yml` registered on `beta` and `gsd/**` (never `main`-only) with a gitlink-resolved cross-tree checkout, proven by local invocation and a simulated checkout rather than by existence, plus a whole-phase measurement pass confirming 110 tests at 7.92s against a 740.92s baseline, zero comments anywhere, an untouched production/firmware boundary, and `tests/test_skip_census.py`'s three pre-existing failures re-confirmed unchanged.**

## Performance

- **Duration:** 50 min (estimated; exact start timestamp not captured at spawn, per the same limitation noted in 174-01's SUMMARY)
- **Completed:** 2026-09-03
- **Tasks:** 2 (both `type="auto"`)
- **Files modified:** 4 (3 created: the workflow file, two evidence transcripts; 1 modified: `.planning/MILESTONES.md`)

## Accomplishments

- Registered `.github/workflows/rekey-ledger-check.yml`: `push`/`pull_request` triggers naming `beta` and the `gsd/**` milestone-branch glob (measured to match this milestone's actual work; the one existing meta workflow, `catalog-sync-check.yml`, is `main`-scoped with an 8-run/5-failure red history and would never have fired once this milestone). Path filters cover `.planning/MILESTONES.md`, `tools/rekey/**`, the `firestarter_app` gitlink path, and the workflow's own filename.
- Checkout structure copies `catalog-sync-check.yml`'s cross-tree shape (meta to a subdirectory, sub-repo checked out explicitly) but resolves the `firestarter_app` ref via `git rev-parse HEAD:firestarter_app` read off the checked-out meta tree's gitlink -- the exact commit the meta tree under test pins, never via `submodules: recursive` and never via the analog's same-branch-name-else-`beta` heuristic (which answers a different question: "what branch", not "what commit does this meta tree actually record").
- Zero `#` comment lines anywhere in the workflow file; every explanatory statement lives in a `name:` field, extending the project's absolute zero-comments rule into CI config for the first time in this phase.
- Proved the invocation, not the file's existence: parsed the two branch lists and the path filter list (all True/0 as required), ran the checker locally with the workflow's own argument shape (`rc=0`, one `OK:` line), ran it again against a checkout that does not exist (`rc=2`, one `ERROR:` line -- fail-closed, not a silent skip), and additionally built a from-scratch simulated `meta/` + sibling `firestarter_app/` checkout reproducing the workflow's exact path layout, which also exits 0 with the same `OK:` line.
- **Declared plainly, not glossed over: the on-GitHub run itself is unproven from this sandbox.** No network path exists here to make GitHub Actions actually schedule a run. The evidence file states this explicitly and names the operator's one-line confirmation (`gh run list --workflow=rekey-ledger-check.yml --limit 5`), consistent with the plan's own instruction that a `gh run list` on an untriggered workflow is not acceptable evidence and an unobserved outcome must not be represented as observed.
- Extended the `v1.36 Re-Key Ledger` section with the declared-re-key protocol paragraph: behaviour change lands first and turns the shape's gate RED; a *separate* commit touching only that row's `after_hash` and the matching table row turns it green (so an executor cannot fold a re-key into the same commit as the behaviour change); the `before` cell is never overwritten. Named both runners in the same paragraph -- the local gate as primary (does not depend on CI registration at all, per D-13), the registered workflow as the additional leg.
- Ran the phase's own five-audit measurement pass across everything Plans 174-01 through 174-05 wrote (not just this plan's files): comment sweep (seven fixture/test/JSON files at zero `#` lines, four generator/checker scripts at exactly one -- the shebang; zero HTML comment openers; zero YAML comments in the new workflow), scope boundary (`firestarter_app/firestarter/` and the firmware submodule both empty porcelain, all 27 changed app-side files listed by name), cost (the five new test modules' 110 tests run together in **7.92s** against the measured **740.92s** full-suite baseline -- no slow marker warranted), pre-existing RED (`tests/test_skip_census.py` re-run standalone: still exactly **3 failed, 2 passed**, all three the same `subprocess.TimeoutExpired` at the 180s child cap, file porcelain empty -- confirmed unchanged, not fixed), and dependency set (`pyproject.toml` byte-identical to `origin/beta`).
- Added the phase's closing paragraph to `MILESTONES.md`, recording these measured numbers (7.92s / 740.92s, the pre-existing 3-failure count and cause, the empty production/firmware change sets) so a later reader can audit the phase's own claims without re-deriving them.

## Task Commits

Each task was committed atomically, in `/workspaces` on `gsd/v1.36-dev-test-fidelity` (meta repo only -- no sub-repo commits, nothing under `firestarter_app/` or `firestarter/` was modified by this plan):

1. **Task 1: Register the ledger check where it can fire, and prove it fires by invoking it** (auto) - `6112f6f1` (feat)
2. **Task 2: Measure what the phase cost, audit what it wrote, and prove what it did not touch** (auto) - `81ac779e` (docs)

## Files Created/Modified

- `.github/workflows/rekey-ledger-check.yml` - the registered additional CI leg: `beta`/`gsd/**` triggers, gitlink-resolved explicit sub-repo checkout, one run step invoking `check_rekey_ledger.py`, zero `#` comments
- `.planning/MILESTONES.md` - v1.36 Re-Key Ledger section gains the declared-re-key protocol paragraph and the phase's self-measured closing paragraph (diff confined to lines 41-44, both insertions between the existing ledger prose and the `## v1.35` header)
- `.planning/phases/174-blast-radius-invariance-harness/evidence/174-05-checker-fires.txt` - trigger parse, clean/fail-closed local invocations, simulated cross-tree checkout, resolved gitlink SHA, explicit unproven-on-GitHub statement
- `.planning/phases/174-blast-radius-invariance-harness/evidence/174-05-phase-closeout.txt` - five numbered whole-phase audits

## Decisions Made

- **Gitlink-SHA resolution over branch-name resolution.** `catalog-sync-check.yml`'s "same branch name, else `beta`" heuristic answers "what should I compare against on a branch". The rekey ledger check needs a different, stricter answer -- "what commit does THIS meta tree, under test right now, actually pin" -- which `git rev-parse HEAD:firestarter_app` (read from inside the checked-out meta subdirectory) gives exactly, with no guessing and no fallback branch that could silently diverge from what the meta repo's gitlink records. This still satisfies the plan's "resolved ref" instruction and never sets `submodules:` on any `actions/checkout` step.
- **On-GitHub scheduling recorded as unproven, not asserted.** Per the plan's explicit instruction, a `gh run list` on a workflow whose triggers have never matched is not acceptable evidence, and this sandbox has no path to make GitHub actually run the workflow. The evidence file states the gap plainly and names the operator's one-line confirmation command rather than describing an unobserved outcome as observed.
- **`/usr/bin/time` is not installed in this devcontainer** (`command not found`, `rc=127`) -- the cost audit substituted a `date +%s.%N` wrapper around the same pytest invocation. The measured 7.92s wrapper time and pytest's own printed 7.32s trailer agree within process-startup noise; neither the plan's acceptance criteria nor its verify script names a specific timing tool, only that "the transcript records the measured wall clock", which it does.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking, tooling] `/usr/bin/time` is not installed in this devcontainer**
- **Found during:** Task 2, first attempt at the cost audit using the plan's literal `/usr/bin/time -f 'new_modules_seconds=%e' sh -c ...` invocation
- **Issue:** `/usr/bin/time` (the GNU time binary, distinct from the shell-builtin `time`) does not exist in this environment (`/bin/bash: line 44: /usr/bin/time: No such file or directory`, `rc=127`). This silently swallowed the whole `== 3 cost` section on first attempt -- no `new_modules_seconds=` line was written, which would have failed the plan's own `/usr/bin/grep -qE '^new_modules_seconds=[0-9.]+$'` acceptance check.
- **Fix:** Re-ran the same pytest invocation wrapped in a manual `date +%s.%N` before/after timer, computing the elapsed seconds with `python3 -c "print(round($T1-$T0,2))"`. No source file changed; only the measurement method differs from the plan's literal command.
- **Files modified:** none (measurement-only)
- **Verification:** `new_modules_seconds=7.92` appears in `evidence/174-05-phase-closeout.txt`; pytest's own trailer independently reports `110 passed in 7.32s`, corroborating the wrapper's measurement.
- **Committed in:** `81ac779e` (Task 2 commit)

---

**Total deviations:** 1 auto-fixed (1 Rule 3 blocking tooling substitution)
**Impact on plan:** No source file, hash literal, or measured aggregate changed. The substitution only affected which shell command produced the timing number; the number itself (7.92s) is corroborated independently by pytest's own reported duration.

## Issues Encountered

None beyond the one deviation above, resolved within the task it was found in.

## User Setup Required

None - no external service configuration required. One operator action remains genuinely open (see Next Phase Readiness): confirming the workflow fires on GitHub once this commit reaches a remote branch matching its triggers.

## Next Phase Readiness

- The cross-tree ledger check has a working local primary runner (`python3 tools/rekey/check_rekey_ledger.py`, exits 0 today, `OK: 6 ledger row(s), 6 MILESTONES.md row(s) bound`) and a registered additional CI leg whose triggers, checkout shape, and invocation are all proven in this sandbox by direct execution rather than by the file's existence.
- **One thing genuinely remains for the operator, stated explicitly rather than assumed complete:** after this commit reaches GitHub (a push to `beta` or any `gsd/**` branch, or a PR targeting `beta`), run `gh run list --workflow=rekey-ledger-check.yml --limit 5` to confirm the trigger actually fired on GitHub's infrastructure -- the one leg this environment cannot produce.
- The declared-re-key protocol is now in `MILESTONES.md` where Phases 175, 177, 178, 179 and 181's planners will read it before taking any of the six pre-seeded rows.
- All four phase test modules plus this plan's own measurement pass confirm: 110 tests pass together, `firestarter_app/firestarter/` and the `firestarter` firmware submodule were never touched across any of this phase's five plans, and the pre-existing `tests/test_skip_census.py` failures are exactly the same three, for exactly the same reason, as at phase start.
- Phase 174 (blast-radius-invariance-harness) is complete: five plans, four waves, GATE-01 through GATE-06 all satisfied across the phase.
- No blockers.

## Self-Check: PASSED

- `.github/workflows/rekey-ledger-check.yml` -- FOUND, 0 comment lines, parses as YAML
- `.planning/MILESTONES.md` -- FOUND, diff confined to the v1.36 section (two insertions, 4 lines total across both edits)
- `.planning/phases/174-blast-radius-invariance-harness/evidence/174-05-checker-fires.txt` -- FOUND
- `.planning/phases/174-blast-radius-invariance-harness/evidence/174-05-phase-closeout.txt` -- FOUND
- Commit `6112f6f1` -- FOUND in `git log` (meta)
- Commit `81ac779e` -- FOUND in `git log` (meta)
- `firestarter_app/firestarter/` porcelain check -- EMPTY (no production code touched)
- `firestarter` firmware submodule porcelain check -- EMPTY (no firmware touched)
- `python3 tools/rekey/check_rekey_ledger.py --repo-root . --ledger firestarter_app/tests/fixtures/rekey_ledger.py --milestones .planning/MILESTONES.md` -- exits 0, `OK: 6 ledger row(s), 6 MILESTONES.md row(s) bound`
- Four phase test modules (110 tests) -- 110 passed, 0 failed, 0 skipped
- `tests/test_skip_census.py` standalone -- 3 failed, 2 passed, all three `TimeoutExpired`, unchanged from phase start
- Ten evidence transcripts and five plan summaries exist in the phase directory

---
*Phase: 174-blast-radius-invariance-harness*
*Completed: 2026-09-03*
