---
phase: 173-close-beta-cut-under-protection-close-procedure-honesty-ledg
plan: 03
subsystem: infra
tags: [github-rulesets, push-probe, gh-api, branch-protection, honesty-ledger]

requires:
  - phase: 172-policy-one-tracker-protected-main
    provides: three active `Protect main` rulesets (ids `22043478` / `4998759` / `22046179`), measured and read back from the API rather than the settings page
provides:
  - "An operator-authorized, on-disk record (evidence/173-03-operator-approval.txt) that gates every outward-facing action in this plan — an auto-approved checkpoint alone cannot produce this file"
  - "Three per-repository push-probe transcripts proving a direct push to protected `main` is rejected by GitHub's own receive stage (a `remote:` GH013 rule-violation line naming the pull-request requirement), each from a true fast-forward of `origin/main`, never a client-side false positive"
  - "The same three transcripts proving the ruleset is scoped to the default branch, not the whole repository, via an accepted-then-deleted push to a throwaway ref"
  - "A before/after ruleset capture proving the probe altered none of the three rulesets, at their original ids"
  - "A verdict record (evidence/173-03-probe-verdict.md) stating plainly what the probe does and does not establish, including that no beta lockstep cut is claimed by this probe"
affects: [173-08-close-record, 173-09-requirements-sweep]

actuals:
  tokens: 4384
  tasks: 3
  commits: 3

tech-stack:
  added: []
  patterns:
    - "Push-probe evidence classified on the rejection text, never the exit code — a client-side non-fast-forward rejection and a server-side GH013 ruleset rejection both exit non-zero, and only the latter proves the ruleset was consulted (RESEARCH.md Pitfall 1)."
    - "checkout -B <probe-branch> origin/main before the empty commit, so the pushed ref is a true descendant of the remote default branch and the receive stage — not git's own client-side check — produces the rejection."
    - "A two-half probe (attack + control) on one branch: the attack half proves the rule blocks a fast-forward push at the protected ref; the control half, same branch pushed to a throwaway ref, proves the rule is scoped to that ref and not the whole repository."
    - "An on-disk approval file, asserted by content before any outward-facing action runs, as the authorization boundary — not the checkpoint UI, which an auto-advance mode can approve without writing anything."

key-files:
  created:
    - .planning/phases/173-close-beta-cut-under-protection-close-procedure-honesty-ledg/evidence/173-03-operator-approval.txt
    - .planning/phases/173-close-beta-cut-under-protection-close-procedure-honesty-ledg/evidence/173-03-rulesets-before.json
    - .planning/phases/173-close-beta-cut-under-protection-close-procedure-honesty-ledg/evidence/173-03-rulesets-after.json
    - .planning/phases/173-close-beta-cut-under-protection-close-procedure-honesty-ledg/evidence/173-03-probe-firestarter_prom.txt
    - .planning/phases/173-close-beta-cut-under-protection-close-procedure-honesty-ledg/evidence/173-03-probe-firestarter.txt
    - .planning/phases/173-close-beta-cut-under-protection-close-procedure-honesty-ledg/evidence/173-03-probe-firestarter_app.txt
    - .planning/phases/173-close-beta-cut-under-protection-close-procedure-honesty-ledg/evidence/173-03-probe-verdict.md
  modified:
    - .planning/STATE.md

key-decisions:
  - "The operator chose 'authorize' from Task 1's two-option checkpoint (D-02's probe as specified) with no added free-text note; the approval file records that as a menu selection rather than inventing a quotation."
  - "D-02's probe shape followed exactly: an empty-commit fast-forward push at each protected `main` (attack half, expected rejected) plus an accepted-then-deleted push to a throwaway ref (control half); no `--dry-run`, no push of any shape at `beta`."
  - "The CI-cost table in RESEARCH.md Pitfall 4 predicted `build.yml`/`py32f071.yml` (firestarter) and `ci.yml` (firestarter_app) would fire on the control push. Measured: no new workflow run registered on any of the three repositories within the observation window before the throwaway ref was deleted (roughly 10 seconds branch-to-delete). Recorded as a measured absence in the verdict record, not claimed as a prediction that held."

patterns-established:
  - "Verdict classification on text content, not process exit status, for any future GitHub-receive-stage probe in this project."

requirements-completed: [POLICY-04]

coverage:
  - id: D1
    description: "Operator authorization for the outward-facing ruleset rejection probe recorded on disk before any push"
    requirement: "POLICY-04"
    verification:
      - kind: other
        ref: "evidence/173-03-operator-approval.txt — exact APPROVED-FOR-PROBE literal, operator name, date; Task 1 automated verify leg"
        status: pass
    human_judgment: false
  - id: D2
    description: "Direct push to protected `main` rejected by GitHub's own receive stage (GH013, pull-request clause) in all three repositories, from a true fast-forward of `origin/main`"
    requirement: "POLICY-04"
    verification:
      - kind: other
        ref: "evidence/173-03-probe-firestarter_prom.txt, evidence/173-03-probe-firestarter.txt, evidence/173-03-probe-firestarter_app.txt — Task 2 automated verify legs (both blocks)"
        status: pass
    human_judgment: false
  - id: D3
    description: "Control push to an unprotected throwaway ref accepted and deleted in all three repositories, proving default-branch-only scope; no ruleset-probe branch survives on any remote"
    requirement: "POLICY-04"
    verification:
      - kind: other
        ref: "evidence/173-03-probe-*.txt control-push sections; git ls-remote --heads … 'ruleset-probe*' returns empty on all three, verified after the run"
        status: pass
    human_judgment: false
  - id: D4
    description: "Rulesets proven field-for-field identical before and after the probe at their original ids; corroborating branch-rules reads recorded as context, not the discharge"
    requirement: "POLICY-04"
    verification:
      - kind: other
        ref: "evidence/173-03-rulesets-before.json, evidence/173-03-rulesets-after.json, evidence/173-03-probe-verdict.md — Task 3 automated verify legs (both blocks)"
        status: pass
    human_judgment: false

duration: 12min
completed: 2026-09-02
status: complete
---

# Phase 173 Plan 03: Ruleset Rejection Probe Summary

**Pushed a true-fast-forward empty commit at protected `main` in all three repositories and captured GitHub's own GH013 rule-violation rejection — not a reading of the ruleset configuration — with a paired accepted-then-deleted push proving the rule is scoped to the default branch only.**

## Performance

- **Duration:** 12 min (commit range) — from operator authorization to verdict record
- **Started:** 2026-09-02T14:22:24Z
- **Completed:** 2026-09-02T14:29:06Z
- **Tasks:** 3
- **Files modified:** 8 (7 new evidence files + STATE.md)

## Accomplishments
- Recorded the operator's authorization of the D-02 probe on disk at `evidence/173-03-operator-approval.txt`, with the exact `APPROVED-FOR-PROBE: firestarter_prom firestarter firestarter_app` literal, before any push occurred.
- Pushed an empty commit at each protected `main` from a scratch clone, branched `ruleset-probe` off `origin/main` with `checkout -B` — a true fast-forward, never a non-descendant ref. All three pushes were rejected by GitHub with `remote: error: GH013: Repository rule violations found for refs/heads/main.` and a `Changes must be made through a pull request.` clause. Verdict PASS in all three transcripts.
- Pushed the same branch to a new throwaway ref in each repository; all three were accepted, then deleted immediately. `git ls-remote --heads … 'ruleset-probe*'` returns empty on all three remotes after the run.
- Captured all three rulesets by id before and after the probe and proved them field-for-field identical on `id`, `enforcement`, `current_user_can_bypass`, `conditions` and `bypass_actors`, at their original ids (`22043478` / `4998759` / `22046179`) — no ruleset created, amended, disabled or deleted.
- Read `main` and `beta` branch rules back from the API in all three repositories as corroborating context: `main` still carries `deletion`, `non_fast_forward`, `pull_request`; `beta` carries none. Recorded explicitly in the verdict record as context, never as the discharge.
- Wrote `evidence/173-03-probe-verdict.md` with a per-repository table and a plain statement of what the probe does and does not establish, including that no beta lockstep cut is claimed by this probe.

## Task Commits

Each task was committed atomically:

1. **Task 1: Operator authorizes the ruleset rejection probe and writes the approval file** - `edbda5d0` (docs)
2. **Task 2: Push an empty commit at each protected `main` from a true descendant of `origin/main`, and keep GitHub's own words** - `af32bbfc` (feat)
3. **Task 3: Prove the probe changed nothing, record the corroborating reads as context rather than as the discharge, and write the verdict** - `09a7f6e0` (docs)

**STATE.md update:** included in this SUMMARY's own commit (no separate plan-metadata commit was made because the metadata is folded into the SUMMARY commit for this plan — see the commit list above; the final `docs(173-03): complete...` commit that follows carries SUMMARY.md and STATE.md together).

_Note: no TDD tasks in this plan; no test → feat → refactor sequence applies._

## Files Created/Modified
- `evidence/173-03-operator-approval.txt` - Operator authorization, written by a human act, asserted by content before Task 2 runs
- `evidence/173-03-rulesets-before.json` - Three rulesets captured by id before the probe, restricted to the defining fields
- `evidence/173-03-rulesets-after.json` - Same capture after the probe, proven field-for-field equal
- `evidence/173-03-probe-firestarter_prom.txt` - Full transcript: clone, fast-forward branch, empty commit, rejected push, accepted-then-deleted control push
- `evidence/173-03-probe-firestarter.txt` - Same, for `firestarter`
- `evidence/173-03-probe-firestarter_app.txt` - Same, for `firestarter_app`
- `evidence/173-03-probe-verdict.md` - Per-repository verdict table, corroborating reads demoted to context, and the explicit does/does-not-establish statement
- `.planning/STATE.md` - Frontmatter and body `Current Position`/`Session` updated together to record plan 03 complete

## Decisions Made
- The operator selected "authorize" from Task 1's checkpoint menu with no added free-text sentence; the approval file states this honestly as a menu selection rather than attributing invented words to the operator.
- Followed D-02's probe shape exactly: empty-commit fast-forward push at protected `main` (attack half) plus an accepted-then-deleted push to a throwaway ref (control half), all three repositories, no representative sampling.
- Classified each result on the captured `remote:` text per RESEARCH.md Pitfall 1 and T-173-01, not on the process exit code — a client-side `non-fast-forward` rejection and a server-side `GH013` ruleset rejection both exit non-zero, and only the latter is evidence about the ruleset.

## Deviations from Plan

None — plan executed exactly as written. One measured observation worth recording plainly: RESEARCH.md Pitfall 4 predicted the control-push half would fire `build.yml`/`py32f071.yml` on `firestarter` and `ci.yml` on `firestarter_app`. Measured across all three repositories, no new workflow run registered within the observation window (an 8-second pause inside each probe run, plus a follow-up `gh run list` check against `firestarter`) — the throwaway branch was deleted roughly 10 seconds after being pushed, which appears to have outrun GitHub Actions' run-queuing for that push event. This is not a deviation from the plan's required behavior (the acceptance criteria do not require CI to fire, only that the control push be accepted and the ref deleted, both of which happened) — it is a measured correction to a RESEARCH.md prediction, recorded in `evidence/173-03-probe-verdict.md` rather than left as an unstated discrepancy.

## Issues Encountered
None.

## User Setup Required
None - no external service configuration required.

## Requirements Note

This plan's frontmatter names `POLICY-04`, and its four coverage deliverables (D1–D4) are this
plan's own contribution toward it — the demonstration half of D-01's split. Per the orchestrator's
explicit instruction for this plan, **POLICY-04 is a multi-plan requirement and its
`.planning/REQUIREMENTS.md` checkbox is flipped only by plan 173-09, after the closing sweep**,
which per D-03 decides whether the missing half (a real beta lockstep cut, gated on separate
operator authorization) was performed or is recorded as a ledger non-claim. This SUMMARY does not
call any `requirements.*` verb and does not modify `REQUIREMENTS.md` — confirmed below.

## Orchestrator-owned artifacts — provably untouched

`.planning/ROADMAP.md` and `.planning/REQUIREMENTS.md` are byte-identical across this plan's full
commit range and across the final HEAD~1..HEAD step:

```
git diff 1a3ab298..HEAD -- .planning/ROADMAP.md        → (empty)
git diff 1a3ab298..HEAD -- .planning/REQUIREMENTS.md   → (empty)
git diff HEAD~1..HEAD   -- .planning/ROADMAP.md        → (empty)
git diff HEAD~1..HEAD   -- .planning/REQUIREMENTS.md   → (empty)
```

`1a3ab298` is the commit immediately preceding this plan's first task commit (`edbda5d0`).

## Next Phase Readiness
- `evidence/173-03-probe-verdict.md` is ready for plan 173-08 to draw the POLICY-04 ledger rows from directly — it already states the does/does-not-establish boundary in the register the ledger will inherit.
- The beta lockstep cut itself (D-01's second deliverable) remains unauthorized and unperformed; whether it happens is a separate operator gate, expected in plan 173-09 per D-04, not this plan.
- No blockers. Plans 05-09 remain in Phase 173.

---
*Phase: 173-close-beta-cut-under-protection-close-procedure-honesty-ledg*
*Completed: 2026-09-02*

## Self-Check: PASSED

- All 8 files (7 evidence files + this SUMMARY) verified present on disk with `[ -f ]`.
- All 4 commit hashes (`edbda5d0`, `af32bbfc`, `09a7f6e0`, `e88bd55b`) verified present in `git log --oneline --all`.
- All plan-level `<verification>` and per-task `<acceptance_criteria>` re-run and passing (see Task 1/2/3 verify blocks above).
- No `ruleset-probe`-prefixed branch remains on any of the three remotes, re-checked after the SUMMARY commit.
- `.planning/ROADMAP.md` and `.planning/REQUIREMENTS.md` confirmed byte-identical across the full plan commit range and the final commit step.
