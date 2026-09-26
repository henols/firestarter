---
phase: 173-close-beta-cut-under-protection-close-procedure-honesty-ledg
plan: 09
subsystem: infra
tags: [closing-sweep, requirements, gitlinks, beta-cut, honesty-ledger, policy-04, policy-05]

# Dependency graph
requires:
  - phase: 173-close-beta-cut-under-protection-close-procedure-honesty-ledg
    provides: "plan 173-08's completed honesty ledger and backlog filings — the final ledger state Task 1's sweep cites"
provides:
  - "A criterion-by-criterion closing sweep for all five ROADMAP success criteria, written and committed before either requirement checkbox moved"
  - "POLICY-04 and POLICY-05 marked complete in REQUIREMENTS.md, each traceable to named evidence"
  - "Both submodule gitlinks re-pinned and proven equal per submodule, with the milestone tail measured against origin/beta via git cherry"
  - "The full beta lockstep cut performed under operator authorization, verified independently from a clean environment and the release/PyPI APIs, meta tagged v1.35"
  - "CLOSE-RECORD.md SS2 and SS4 finalized: POLICY-04's disposition on both the probe and the performed cut, and the C-4 correction to D-04 now demonstrated directly"
affects: [complete-milestone]

# Actuals (#2632) — this entry covers only the recovery + recording work performed by this
# dispatch (Task 3's verification and evidence-writing); Tasks 1 and 2 were already committed
# by a prior executor and are not re-measured here.
actuals:
  tokens: 9200
  tasks: 1
  commits: 1

tech-stack:
  added: []
  patterns:
    - "verifying a --limit N release-list comparison against the individual gh release view for each entry that appears to differ, rather than trusting a fixed-window pagination diff as proof of an actual change"
    - "recording a session-rate-limit interruption plainly in the evidence file itself, with the recovery pass's own independent re-verification of every figure the interrupted pass had already produced"

key-files:
  created:
    - .planning/phases/173-close-beta-cut-under-protection-close-procedure-honesty-ledg/173-09-SUMMARY.md
  modified:
    - .planning/phases/173-close-beta-cut-under-protection-close-procedure-honesty-ledg/evidence/173-09-beta-cut.txt
    - .planning/v1.35/CLOSE-RECORD.md
  committed_untracked:
    - .planning/phases/173-close-beta-cut-under-protection-close-procedure-honesty-ledg/evidence/173-09-operator-approval.txt

key-decisions:
  - "This dispatch performed NO outward-facing action. A prior executor had already merged the three pull requests to `beta`, tagged and pushed `v1.35`; the orchestrator had already verified both channels. This pass's job was exclusively to independently re-verify every claim with read-only commands and write the record — every figure in evidence/173-09-beta-cut.txt was re-measured directly (fresh gh api / release / PyPI calls, a second independent .hex download, a fresh throwaway venv install), not copied from the dispatch prompt's own wording."
  - "Found and recorded a measurement artefact in the plan's own 'stable release set unchanged' verify leg: a --limit 100 gh release list snapshot silently drops the oldest visible release once a repository's total release count crosses the 100-row window (firestarter: 101 releases; firestarter_app: 180) — each new prerelease shifts the window and pushes one older stable tag out of view even though nothing was deleted. Confirmed directly with gh release view on both affected tags (0.1.3, 1.3.7): both still exist and remain non-prerelease. Recorded as a finding about the comparison method, not smoothed over by widening the limit to make the strings match."
  - "CLOSE-RECORD.md SS2's rewrite states plainly that ledger row L8 (SS5) is left byte-unchanged because this plan's authorization to edit CLOSE-RECORD.md is scoped to SS2 and SS4 only — a named record discrepancy in this project's own convention, rather than silently letting L8's now-stale conditional wording stand as the only word on the cut's outcome."
  - "Confirmed the C-4 correction to D-04 directly rather than by re-stating the earlier measurement: publish.yml's own run history shows no workflow_dispatch run since 2026-08-02, and 3.0.0b36 is on PyPI anyway, fired solely by beta-release.yml's workflow_call chain on the PR #58 merge. This closing cut is itself the fourth piece of evidence, not a fifth restatement."

requirements-completed: [POLICY-04, POLICY-05]

coverage:
  - id: D1
    description: "Closing sweep written and committed before POLICY-04/POLICY-05 were marked; both flipped correctly (already complete from Tasks 1-2, verified again here)"
    requirement: "POLICY-04"
    verification:
      - kind: other
        ref: "evidence/173-09-closing-sweep.txt (five criteria, four+ non-claims, four wiki checkers green); git log commit-order check (b23aba19 sweep before REQUIREMENTS.md edit)"
        status: pass
    human_judgment: false
  - id: D2
    description: "Both submodule gitlinks re-pinned and proven equal per submodule"
    requirement: null
    verification:
      - kind: other
        ref: "evidence/173-09-gitlink-equality.txt; independently re-confirmed this session (firestarter HEAD=gitlink=4f73c80c…, firestarter_app HEAD=gitlink=0a939995…)"
        status: pass
    human_judgment: false
  - id: D3
    description: "Full beta lockstep cut performed, both channels independently verified from a clean environment and the release/PyPI APIs"
    requirement: "POLICY-04"
    verification:
      - kind: other
        ref: "evidence/173-09-beta-cut.txt SS1-SS7 — three merged PRs (gh api pulls), git cherry equivalence, observed tags read from gh release list, firmware hex re-downloaded and hashed, app resolved from a fresh venv via pip install --pre, v1.35 tag on origin, all three main SHAs unchanged"
        status: pass
    human_judgment: false
  - id: D4
    description: "No unauthorized stable release; the one apparent stable-set change is a --limit 100 pagination artefact, not a real change"
    requirement: null
    verification:
      - kind: other
        ref: "evidence/173-09-beta-cut.txt SS8 — gh release view 0.1.3 (firestarter) and 1.3.7 (firestarter_app) both confirmed still present and non-prerelease"
        status: pass
    human_judgment: false
  - id: D5
    description: "CLOSE-RECORD.md SS2 and SS4 finalized with the performed cut and the C-4 correction"
    requirement: null
    verification: []
    human_judgment: true
    rationale: "Prose-record correctness (does the ledger discipline hold, is no claim stronger than its evidence) is a judgment call about narrative accuracy, not something a test asserts."

# Metrics
duration: recovery pass — not separately timed from Tasks 1-2's original execution; this session's
  own work (verification + evidence writing + one commit) ran without interruption
completed: 2026-09-02
status: complete
---

# Phase 173 Plan 09: Beta Lockstep Cut, Recorded — Recovery + Recording Summary

**The `beta` lockstep cut for the Phases 171-173 remainder was performed, interrupted mid-flight by a session rate limit, completed by the orchestrator, and independently re-verified and recorded by this dispatch — three PRs merged to `beta`, firmware `3.0.0b25` and app `3.0.0b36` cut and confirmed from a clean environment, meta tagged `v1.35`, no stable release, `main` untouched.**

## Performance

- **Scope:** RECOVERY + RECORDING dispatch for Task 3 of 173-09 only. Tasks 1 (`b23aba19`) and 2
  (`0fdc10eb`) were already committed by a prior executor before this dispatch began, along with the
  merge of `beta` into the milestone branch (`26523510`, local).
- **This dispatch performed zero outward-facing actions** — no push, merge, tag, release, or PyPI
  action. Every fact recorded was independently re-measured with read-only commands.
- **Commits this dispatch:** 1 (`741c8dd5`)
- **Completed:** 2026-09-02

## Accomplishments

- **Independently re-verified the entire performed cut**, not trusted from the dispatch prompt's
  own wording: re-fetched `origin/beta` and re-ran `git cherry` in both directions (0 in each);
  re-read `origin/beta`'s parent list (two parents, a genuine merge); re-queried the GitHub API for
  all three merged pull requests (`firestarter_prom#56`, `firestarter#59`, `firestarter_app#58`)
  directly rather than trusting the search API (whose `is:merged` filter returned a stale
  `merged_at: null` for these same PRs — noted and worked around by querying `pulls?base=beta&state=closed`
  instead); re-downloaded the `firestarter_uno.hex` release asset from a fresh temp dir and
  re-hashed it, matching byte-for-byte; installed `firestarter==3.0.0b36` into a brand-new venv with
  `pip install --pre --no-cache-dir` and confirmed `__file__` resolved inside that venv's own
  `site-packages`, `importlib.metadata.version` and the console script both reporting `3.0.0b36`;
  re-read all three `main` SHAs directly from the GitHub API, matching exactly.
- **Found and ran down a discrepancy the dispatch prompt did not mention**: comparing the
  phase-start stable-release baseline against a fresh `gh release list --limit 100` read showed
  `0.1.3` (firestarter) and `1.3.7` (firestarter_app) as apparently missing. Traced this to
  pagination, not tampering — both repositories crossed the 100-release mark during this phase's
  own two new prereleases, and a fixed `--limit 100` window silently drops the oldest visible entry
  each time a new one is added at the top. Confirmed both tags still exist and remain non-prerelease
  via individual `gh release view` calls, then recorded the finding as a measurement-method
  limitation in `evidence/173-09-beta-cut.txt` §8 rather than silently widening the limit to make
  the strings match or ignoring the apparent mismatch.
- **Confirmed the C-4 correction to D-04 (the dropped manual PyPI dispatch) directly**: `publish.yml`'s
  own run history on `firestarter_app` shows no `workflow_dispatch` run since 2026-08-02 — none
  fired for this cut — while `beta-release.yml` ran once (`event: push`, triggered by the PR #58
  merge) and PyPI carries `3.0.0b36` regardless, via the `workflow_call` chain. This is now a
  demonstrated fact of the actual cut, not an inference from the workflow YAML alone.
- **Completed `evidence/173-09-beta-cut.txt`**, which previously held only the pre-cut stable-release
  baseline. It now records, in order: the interruption itself; local `beta` recreation and `git
  cherry` ancestry (never `--is-ancestor`); all three merged pull requests with their merge SHAs;
  the observed prerelease pair read from the release API; both channels independently verified;
  the non-performed manual dispatch and why PyPI got the artefact anyway; the pushed `v1.35` tag;
  the three unchanged `main` SHAs; the stable-release-set pagination finding; and an explicit
  non-claims summary.
- **Finalized `CLOSE-RECORD.md` §2** — replaced POLICY-04's provisional "the cut has not yet run"
  language with the performed-and-verified disposition, and named the resulting record discrepancy
  in ledger row L8 (still stale-worded, since this plan's authorization to edit the close record is
  scoped to §2 and §4 only) rather than silently leaving the reader to reconcile it.
- **Finalized `CLOSE-RECORD.md` §4** — extended the existing C-4 correction item to record that this
  cut is itself a fourth, direct confirmation that the manual `publish.yml` dispatch is unnecessary,
  citing the workflow-run evidence above.

## Task Commits

Tasks 1 and 2 were committed by a prior executor before this dispatch began:

1. **Task 1: Write the closing sweep, mark POLICY-04/POLICY-05** — `b23aba19` (docs)
2. **Task 2: Re-pin gitlinks, prove equality, measure the beta tail** — `0fdc10eb` (docs)
   - Merge of `beta` into the milestone branch — `26523510` (local, not pushed)

This dispatch's own commit (Task 3's recording half — the cut itself was performed and its
outward-facing actions completed before this dispatch began):

3. **Task 3 (recording only): Record the performed beta lockstep cut, finalize CLOSE-RECORD §2/§4** -
   `741c8dd5` (docs)

## Files Created/Modified

- `.planning/phases/173-close-beta-cut-under-protection-close-procedure-honesty-ledg/evidence/173-09-beta-cut.txt` -
  completed from a baseline-only file to the full performed-cut record
- `.planning/phases/173-close-beta-cut-under-protection-close-procedure-honesty-ledg/evidence/173-09-operator-approval.txt` -
  committed (was on disk, untracked, from the interrupted executor)
- `.planning/v1.35/CLOSE-RECORD.md` - §2 (POLICY-04 disposition) and §4 (C-4 correction) finalized
- `.planning/phases/173-close-beta-cut-under-protection-close-procedure-honesty-ledg/173-09-SUMMARY.md` - this file
- `.planning/STATE.md` - hand-updated (frontmatter + Current Position), not via `state.advance-plan`
  or `state.begin-phase`, per this project's own recorded finding that both verbs corrupted this
  file's `progress.completed_phases` earlier in this same phase

## Decisions Made

- No outward-facing action was taken by this dispatch — every git-level action (three PR merges, the
  meta `v1.35` tag) was already complete before this dispatch began. This dispatch's only job was
  independent re-verification and recording.
- The stable-release-set `--limit 100` pagination finding is recorded as a limitation of the
  comparison method, not treated as evidence of an unauthorized release — both apparently-missing
  tags were confirmed present and unchanged by direct lookup.
- `CLOSE-RECORD.md`'s ledger row L8 (§5) is left byte-unchanged, and that is stated explicitly in
  §2, because this plan's write authorization for the close record is scoped to §2 and §4 — not a
  silent gap.

## Deviations from Plan

None beyond what the dispatch prompt itself authorized (a recovery + recording pass in place of a
fresh Task 3 execution, because the outward-facing half was already performed by a prior executor
and completed by the orchestrator before this dispatch began). No Rule 1-4 auto-fixes were needed;
this dispatch's entire scope was verification and evidence-writing, and every acceptance criterion
in the plan's approved-path verify block was checked and passes (see evidence file for the exact
commands and outputs).

**Total deviations:** 0.
**Impact on plan:** None — the plan's Task 3 acceptance criteria are fully satisfied by the
combination of the prior executor's outward-facing actions and this dispatch's recording.

## Issues Encountered

- The prior executor performing Task 3's outward-facing actions was killed mid-flight by a session
  rate limit, leaving both evidence files on disk but uncommitted and `173-09-beta-cut.txt` holding
  only its pre-cut baseline. Recorded plainly in the evidence file's own "INTERRUPTION" section
  rather than treated as if the cut had proceeded cleanly start to finish.
- The GitHub search API's `is:merged` filter returned `merged_at: null` for the two sub-repository
  PRs when queried by `sort:created-desc` shortly after merge — likely search-index lag. Worked
  around by querying `pulls?base=beta&state=closed&sort=updated` directly, which returned the
  correct merge data immediately. Noted in case a future close hits the same lag.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- POLICY-04 and POLICY-05 are complete against named evidence, POLICY-04 resting on both the probe
  and the now-performed cut.
- The `beta` lockstep cut is performed and independently verified; `v1.35` is tagged and pushed on
  meta. No stable release exists in any repository beyond the phase-start baseline.
- `CLOSE-RECORD.md` §2 and §4 are finalized. The Phase 173 ROADMAP checklist box remains the
  orchestrator's write, not performed by this dispatch.
- `firestarter_app`'s one Backlog-999.45-owned unstaged modification (`tools/build_db.py`) remains
  carried, untouched, exactly as Task 2 recorded it.

## Self-Check: PASSED

- `evidence/173-09-beta-cut.txt` — FOUND on disk
- `evidence/173-09-operator-approval.txt` — FOUND on disk
- `.planning/v1.35/CLOSE-RECORD.md` — FOUND on disk
- `173-09-SUMMARY.md` — FOUND on disk
- Commit `741c8dd5` (this dispatch's recording commit) — FOUND in `git log --oneline --all`
- Commit `b23aba19` (Task 1, prior executor) — FOUND in `git log --oneline --all`
- Commit `0fdc10eb` (Task 2, prior executor) — FOUND in `git log --oneline --all`
- Plan's approved-path automated `<verify>` for Task 3 re-run against the final evidence file:
  all clauses pass (3 merged-PR lines, observed tag lines, `gh release list`/`pypi.org/pypi/firestarter/json`/`pip install --pre`/`clean venv resolved` literals present, `v1.35` tag count = 1, `APP` = `VENV` = `3.0.0b36`, PyPI JSON confirms `3.0.0b36` in `releases`)
- `git status --porcelain` on the main worktree shows only the pre-existing `firestarter_app` submodule dirty state (Backlog 999.45, untouched by this dispatch) — no other uncommitted changes from this dispatch's work

---
*Phase: 173-close-beta-cut-under-protection-close-procedure-honesty-ledg*
*Completed: 2026-09-02*
