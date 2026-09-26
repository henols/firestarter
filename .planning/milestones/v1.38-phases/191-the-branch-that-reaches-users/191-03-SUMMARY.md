---
phase: 191-the-branch-that-reaches-users
plan: 03
subsystem: testing
tags: [github-releases-api, branch-protection, ci-cd, firestarter_app, main, pypi]

# Dependency graph
requires:
  - phase: 191-02
    provides: "The prepared, unpushed branch v1.38-url-02-main (one commit, three files) off origin/main"
provides:
  - "URL-02 merged onto henols/firestarter_app's protected main via operator-executed PR #66, verified by live contents-API read-back at ref=main rather than by the local clone or the operator's report"
  - "A measured, not assumed, observation of release.yml's real behavior under branch protection: the run fired, failed at the auto-commit push step exactly as D-04 predicted, and produced no tag or release"
  - "The exact operator commands for 191-04's hand-cut release, with the real merge sha substituted, so 191-04 acts on read commands rather than re-deriving them"
affects: [191-04, 191-05]

# Actuals (#2632)
actuals:
  tokens: 2900
  tasks: 2
  commits: 2
  plan_head_before: 17a3b431

tech-stack:
  added: []
  patterns:
    - "The merged state of a protected branch is verified by reading the file back from the GitHub contents API at ref=main, never from the local clone or the operator's report (189-04 precedent, reused unmodified in a second repository)."
    - "A prediction written into the operator handoff BEFORE the gated action, then quoted next to the live observation afterward, converts a plausible guess into a checked measurement — this plan is the second instance of the pattern in this milestone (D-04/D-06)."
    - "A boundary-aware slug sweep (henols/firestarter([^_a-zA-Z0-9]|$)) always runs alongside a non-vacuity positive control (henols/firestarter_app) in the same transcript."

key-files:
  created:
    - .planning/phases/191-the-branch-that-reaches-users/evidence/191-url-02-merged-main.txt
    - .planning/phases/191-the-branch-that-reaches-users/evidence/191-stable-01-release-run.txt
  modified: []

key-decisions:
  - "Verified the operator's report ('merged, app#/66, sha 1d526ea') against the live PR object before trusting it, per this plan's whole discipline — merged: true and merge_commit_sha 1d526ea30f0a00c23ad8198b4679ee9459f31a88 matched the report exactly (full sha superset of the reported short sha), with no discrepancy to escalate."
  - "D-04's prediction was confirmed, not assumed: release.yml run 34784468070 (headSha exact-matched to the merge commit) failed at the git-auto-commit-action@v5 push step with GH013 ('Changes must be made through a pull request'), and the Release step shows conclusion skipped. D-06 Branch A was taken."
  - "No tag or GitHub release for 2.0.9 or 2.0.10 was inferred absent — both were checked directly against the releases and tags APIs and found genuinely absent, per Branch A's explicit checked-not-inferred requirement."
  - "The three exact 191-04 operator commands (tag+push, gh release create --target, gh workflow run publish.yml --field tag=2.0.9) were written into the evidence file with the real merge sha substituted, and none of the three was executed here."
  - "requirements.ready-ids correctly gated the shared-ID URL-02/STABLE-01 pair: URL-02 (declared by both 191-02 and 191-03, both now summarized) was marked Complete; STABLE-01 (declared by both 191-03 and 191-04, the latter not yet run) stayed Pending — computed via the verb, not asserted by hand."
  - "state.advance-plan pruned .planning/config.json's sub_repos from 4 entries to 2 and regressed STATE.md's progress.completed_phases/percent to 0 — both known hazards from prior-phase memory notes. Restored config.json via git checkout and hand-corrected the two STATE.md frontmatter fields back to their pre-call values (completed_phases: 2, percent: 40) before committing."

requirements-completed: [URL-02]

coverage:
  - id: D1
    description: "Operator's merge report (PR #66, sha 1d526ea) verified against the live PR object: merged: true, merge_commit_sha 1d526ea30f0a00c23ad8198b4679ee9459f31a88, matching the report with no discrepancy."
    requirement: URL-02
    verification:
      - kind: other
        ref: "gh api repos/henols/firestarter_app/pulls/66 -- read directly, recorded in 191-url-02-merged-main.txt"
        status: pass
    human_judgment: false
  - id: D2
    description: "All three files read back live from the GitHub contents API at ref=main: constants.py's repointed endpoint (count 1, bare-slug sweep 0), README.md's repointed link (count 1, bare-slug sweep 0, non-vacuity control 4), and __init__.py reading 2.0.9."
    requirement: URL-02
    verification:
      - kind: other
        ref: "Task 2's 9 automated <verify> legs (endpoint count, bare-slug sweep x2, firmware-link count, positive control, version string, ref=main mention, merge_commit_sha mention, porcelain check) -- all run directly, all pass"
        status: pass
    human_judgment: false
  - id: D3
    description: "release.yml run for the merge commit read live: matched by exact headSha equality, conclusion failure, failing step ('Commit updated version') named from job-step JSON, GH013 rejection confirmed from the step log, and Branch A stated explicitly. No tag or release exists for 2.0.9/2.0.10, checked directly rather than inferred."
    requirement: STABLE-01
    verification:
      - kind: other
        ref: "Task 3's 5 automated <verify> legs (run-list newer-than-baseline, conclusion mention, run-URL mention, branch-a/branch-b mention, porcelain check) plus direct releases/tags API checks -- all run directly, all pass"
        status: pass
    human_judgment: false
  - id: D4
    description: "URL-02 marked Complete via requirements.ready-ids (both declaring plans now summarized); STABLE-01 correctly left Pending (191-04 has not yet run) -- computed, not asserted."
    requirement: URL-02
    verification:
      - kind: other
        ref: "node gsd-tools.cjs query requirements.ready-ids 191-03-PLAN.md URL-02 STABLE-01 --raw -> {ready:[URL-02], blocked:[STABLE-01]}"
        status: pass
    human_judgment: false

duration: 8min
completed: 2026-09-13
status: complete
---

# Phase 191 Plan 03: Merging URL-02 and Measuring release.yml Under Protection Summary

**Operator merged PR #66 onto `henols/firestarter_app`'s protected `main` (sha `1d526ea3`); live contents-API read-back confirms all three URL-02 changes landed, and the live `release.yml` run for that merge confirms D-04's prediction exactly — the auto-commit push was rejected by ruleset 22046179, no tag or release exists, and the three exact hand-cut commands for 191-04 are recorded with the real sha filled in.**

## Performance

- **Duration:** ~8 min (this continuation; Task 1's operator wait is excluded)
- **Started:** 2026-09-13T21:39:00Z (approx, resume)
- **Completed:** 2026-09-13T21:44:45Z
- **Tasks:** 2 (Task 2, Task 3 — Task 1 was the operator gate itself, already completed with no artifact/commit before this continuation began)
- **Files modified:** 2 new evidence files, plus REQUIREMENTS.md and STATE.md metadata

## Accomplishments
- Verified the operator's merge report against the live PR object rather than trusting it: `gh api repos/henols/firestarter_app/pulls/66` shows `merged: true` and `merge_commit_sha: 1d526ea30f0a00c23ad8198b4679ee9459f31a88` — an exact match to the operator's reported short sha, with `head.sha` matching the branch 191-02 prepared. No discrepancy found.
- Read all three files back from the GitHub contents API at `ref=main`: `constants.py`'s repointed endpoint (count 1, boundary-aware bare-slug sweep 0), `README.md`'s repointed firmware link (count 1, bare-slug sweep 0, non-vacuity control `henols/firestarter_app` count 4), and `firestarter/__init__.py` reading `2.0.9` — the value the PR carried directly, not a bot-bumped value.
- Read the `release.yml` run for the merge live and matched it to the merge commit sha by exact `headSha` equality (run `34784468070`): conclusion `failure`, failing step `Commit updated version` (the `git-auto-commit-action@v5` push), which the step log shows rejected with `GH013: Repository rule violations found for refs/heads/main` / `Changes must be made through a pull request`. The `Release` step shows conclusion `skipped`. D-04's prediction is **confirmed**, not merely consistent with the outcome — D-06 Branch A was taken.
- Checked, not inferred, that no `2.0.9` or `2.0.10` tag or GitHub release exists: both the releases and tags APIs were queried directly and returned no match.
- Wrote the three exact operator commands for 191-04 (tag creation + push, `gh release create --target` for the merge sha, `gh workflow run publish.yml --field tag=2.0.9`) into the evidence file with the real merge sha substituted; none of the three was executed.
- Marked `URL-02` Complete via `requirements.ready-ids` (both declaring plans, 191-02 and 191-03, now have summaries); left `STABLE-01` Pending because 191-04, the other plan declaring it, has not yet run — computed by the shared-ID gate, not hand-asserted.
- Caught and reverted two known GSD-verb hazards from prior-phase memory: `state.advance-plan` pruned `.planning/config.json`'s `sub_repos` from 4 entries to 2 (restored via `git checkout --`) and regressed `STATE.md`'s `progress.completed_phases`/`percent` to 0 (hand-corrected back to 2/40 before committing).

## Task Commits

Each task was committed atomically:

1. **Task 1: Operator pushes, opens PR, merges** — no commit (pure handoff; completed by the operator before this continuation began, per the resume state).
2. **Task 2: Read all three files back from ref=main** — `ea7af9f8` (test): the merged-main read-back evidence file.
3. **Task 3: Read the release.yml run live** — `d007a63f` (test): the release-run observation evidence file.

**Plan metadata:** commit pending (this SUMMARY + STATE/ROADMAP/REQUIREMENTS)

## Files Created/Modified
- `.planning/phases/191-the-branch-that-reaches-users/evidence/191-url-02-merged-main.txt` — live contents-API + PR-object read-back transcript
- `.planning/phases/191-the-branch-that-reaches-users/evidence/191-stable-01-release-run.txt` — live release.yml run observation, D-06 branch determination, and 191-04's exact commands
- `.planning/REQUIREMENTS.md` — `URL-02` checkbox and traceability row flipped to Complete
- `.planning/STATE.md` — position advanced to Plan 4 of 5; `progress.completed_phases`/`percent` hand-corrected after a verb regression (see Decisions)

## Decisions Made
See frontmatter `key-decisions` for the full list: operator-report verification against the live PR object; D-04/D-06 Branch A confirmation; checked-not-inferred absence of tag/release; the three exact 191-04 commands recorded verbatim; the shared-ID requirements gate computed rather than hand-asserted; and the two GSD-verb hazards caught and corrected (config.json sub_repos prune, STATE.md progress regression).

## Deviations from Plan

None — plan executed exactly as written. The `state.advance-plan` config-prune and progress-regression corrections are standing operational hygiene documented in prior-phase memory (not new discoveries), applied here as instructed by the environment notes rather than as ad hoc deviations from this plan's task content.

## Issues Encountered
None beyond the known GSD-verb hazards noted above, both caught and corrected before committing.

## User Setup Required
None — no external service configuration required in this continuation (Task 1's operator gate was already satisfied before this continuation began).

## Next Phase Readiness
- `main` now carries URL-02's three changes, verified live; `STABLE-01` is still Pending, correctly, because 191-04 has not yet cut a release.
- 191-04 has its exact hand-cut commands pre-written in `191-stable-01-release-run.txt` with the real merge sha (`1d526ea30f0a00c23ad8198b4679ee9459f31a88`) already substituted — it can act on the observation directly rather than re-deriving the commands or the D-06 branch.
- No blockers. 191-04 remains `autonomous: false` — a second operator gate (tag + release + `publish.yml` dispatch) — and must not run under `--auto`/`--chain`.

---
*Phase: 191-the-branch-that-reaches-users*
*Completed: 2026-09-13*

## Self-Check: PASSED
- FOUND: .planning/phases/191-the-branch-that-reaches-users/evidence/191-url-02-merged-main.txt
- FOUND: .planning/phases/191-the-branch-that-reaches-users/evidence/191-stable-01-release-run.txt
- FOUND: .planning/phases/191-the-branch-that-reaches-users/191-03-SUMMARY.md
- FOUND: commit ea7af9f8 (Task 2 evidence)
- FOUND: commit d007a63f (Task 3 evidence)
