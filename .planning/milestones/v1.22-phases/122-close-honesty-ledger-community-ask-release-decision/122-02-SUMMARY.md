---
phase: 122-close-honesty-ledger-community-ask-release-decision
plan: 02
subsystem: infra
tags: [git, github-actions, release-decision, ci-cd, merge-tree, beta-release]

requires:
  - phase: 122-close-honesty-ledger-community-ask-release-decision
    provides: "122-RESEARCH.md's Merge Ground Truth and Release Mechanics sections — the recorded pre-flight values this plan re-measured"
provides:
  - "122-DECISION.md — CLOSE-03's committed accept/avoid/cleanup decision (ACCEPT the auto-fire, D-05) with both declined options named"
  - "Live-measured pre-flight evidence (branch tips, origin/beta tips, ahead/behind, merge-base, version strings, tag ceiling, merge-tree conflict sets, --ours superset proof, gitlink baseline, working-tree dirt) with an explicit zero-divergence verdict against 122-RESEARCH.md"
  - "The eight-step accepted merge/publish/verify/comment sequence mapped to owning plans (122-03/04/07/08/11/12) and CONTEXT constraint numbers"
  - "A commit timestamp (d5c49d4, 2026-07-30T13:03:38Z) that provably precedes any push to beta — the ordering proof plan 122-13 will re-cite"
affects: [122-03, 122-04, 122-07, 122-08, 122-11, 122-12, 122-13]

tech-stack:
  added: []
  patterns:
    - "git merge-tree --write-tree --messages as a non-mutating dry-run conflict probe, run against origin/beta immediately before trusting a multi-day-old research document"
    - "comm -23 name-set-subtraction as a mechanical (not narrative) proof that a whole-file --ours resolution loses no test coverage"

key-files:
  created:
    - .planning/phases/122-close-honesty-ledger-community-ask-release-decision/122-DECISION.md
  modified: []

key-decisions:
  - "D-05 ACCEPT the auto-fire recorded as the chosen option; AVOID (workflow-trigger surgery) and CLEANUP (deleting the stray b12) both recorded declined, in writing, with their reasons"
  - "Every live pre-flight measurement (10 categories) matched 122-RESEARCH.md's recorded value exactly — zero divergence, so the wave-2 merge plan's foundation is confirmed unchanged rather than assumed"
  - "The observed-tag rule (A3) restated explicitly: 3.0.0b14 appears only in explanatory prose about what the auto-increment is expected to derive, never as a literal inside a command to be run verbatim"

requirements-completed: []

coverage:
  - id: D1
    description: "122-DECISION.md records CLOSE-03's accept/avoid/cleanup decision (ACCEPT chosen, AVOID and CLEANUP declined with reasons) plus the live pre-flight evidence it rests on, committed before any push"
    verification:
      - kind: other
        ref: "manual git invocation — 10 categories of live git/gh measurements (branch tips, origin/beta tips, ahead/behind, merge-base coincidence, version strings, tag ceiling, merge-tree conflict probes in both repos, comm -23 superset proof, gitlink ls-tree baseline, git status --porcelain in all three repos) all recorded verbatim in 122-DECISION.md and cross-checked against 122-RESEARCH.md with zero divergence found"
        status: pass
      - kind: other
        ref: "post-write assertion — git -C firestarter/firestarter_app rev-parse HEAD unchanged, origin/beta unchanged, git log -1 -- 122-DECISION.md returns a real commit hash (d5c49d4)"
        status: pass
    human_judgment: false

duration: ~20min
completed: 2026-07-30
status: complete
---

# Phase 122 Plan 02: CLOSE-03 Beta-Push Decision + Pre-flight Evidence Summary

**One committed meta-repo artifact recording D-05's ACCEPT-the-auto-fire verdict for the `beta` push, backed by ten categories of live-remeasured pre-flight evidence that agreed with `122-RESEARCH.md` on every point (zero divergence) — and nothing was pushed, merged, or published.**

## Performance

- **Duration:** ~20 min
- **Started:** 2026-07-30T13:00:20Z
- **Completed:** 2026-07-30T13:03:38Z
- **Tasks:** 2 completed (both wrote into the same artifact; committed once as a unit)
- **Files modified:** 1 created

## Accomplishments
- Re-measured, live in `/workspaces/firestarter` and `/workspaces/firestarter_app`, every pre-flight fact `122-RESEARCH.md` recorded: branch tips (`48c36e5`/`c3c9424`), fresh `origin/beta` tips (`6611fba`/`1bb5599`, unmoved since RESEARCH was written), ahead/behind counts (42/2, 75/7), the merge-base/`v1.21^{commit}` coincidence in both repos (confirming C-9 — v1.22 forked off `beta`, not off a prior tag), the four version strings (`beta`=b13, branch=b11 in both repos), the `3.0.0b*` tag ceiling (b13 highest, b14 absent, identical list in both repos), the dry-run `merge-tree` conflict probe (firmware zero conflicts / app exactly two — `firestarter/submit.py`, `tests/test_submit.py`, with `version.h` and `__init__.py` both confirmed auto-merged not conflicted), the `--ours` superset proof (`comm -23` empty, 60 beta test names vs 77 on HEAD, all five hotfix behaviours grep-confirmed present), the A5 gitlink baseline (`0048b3d`/`96e0622`, unchanged), and the working-tree dirt snapshot in all three repos.
- Every one of those ten categories **agreed exactly** with `122-RESEARCH.md`'s recorded value — no `⚠ Divergence` section was needed, and the artifact says so explicitly rather than silently omitting the check.
- Wrote CLOSE-03's decision itself: verdict **ACCEPT the auto-fire — the merge IS the b14 cut** (D-05), with a three-row table naming ACCEPT (chosen), AVOID (workflow-trigger surgery, declined), and CLEANUP (deleting the stray b12, declined) plus their reasons.
- Recorded the eight-step accepted sequence, each step naming its owning plan (122-03/04/07/08/11/12) and the CONTEXT constraint it satisfies, plus the four dependent facts: the A3 observed-tag rule, the C-3 PyPI-manual-dispatch-is-the-norm finding (46% historical miss rate), the C-8 `ci.yml`-never-runs-on-beta fact, and the post-cut local/remote divergence mechanism.
- Recorded the D-07 out-of-scope items (the `v1.22` tag and meta gitlink bump, both left to `/gsd-complete-milestone`) and the D-01 owned trade-off (no bench smoke-test of the b14 install path before the community is pointed at it).

## Task Commits

Both tasks wrote into the same file (`122-DECISION.md`) per the plan's design — one artifact, one commit:

1. **Task 1 (pre-flight evidence) + Task 2 (the decision itself)** — `d5c49d4` (docs)

**Plan metadata:** (this commit, following SUMMARY write)

## Files Created/Modified
- `.planning/phases/122-close-honesty-ledger-community-ask-release-decision/122-DECISION.md` — 325 lines: ten-category live pre-flight evidence table (all AGREES, zero divergence) followed by the CLOSE-03 accept/avoid/cleanup decision, the eight-step accepted sequence, four dependent facts, and the D-07/D-01 out-of-scope records.

## Decisions Made
- **D-05 recorded as ACCEPT** — the outbound merge to `beta` (plan 122-07) is itself the `3.0.0b14` cut; no separate workflow-dispatch cut is used, no workflow trigger is edited in either repo, and the stray `3.0.0b12` prereleases stay public (no `--force`, no history rewrite, no artifact deletion).
- **Live-measurement discipline honored**: every RESEARCH number was re-derived from a fresh `git fetch` + read-only inspection rather than copied, and the artifact states the zero-divergence result explicitly (RESEARCH's ~2026-08-02 validity window is intact — `origin/beta` has not moved).
- **A3 discipline enforced in the artifact's own text**: every `3.0.0b14` string in `122-DECISION.md` sits inside explanatory prose about what the auto-increment is expected to derive (or inside the AVOID option's description of a declined command), never inside an instruction meant to be run verbatim — verified by reading each of the 8 occurrences individually.

## Deviations from Plan

None - plan executed exactly as written. Both tasks' acceptance criteria were verified directly (grep counts, git state assertions, line-by-line review of every `3.0.0b14` occurrence) before the single commit.

## Issues Encountered

None. No auth gates, no blocking issues, no rule-1/2/3 auto-fixes were needed — this plan is read-only against both sub-repos by design and the live evidence matched the research exactly.

## User Setup Required

None - no external service configuration required.

## Requirement Ticking Scope

**No requirement checkbox was ticked.** This plan's frontmatter lists `requirements: [CLOSE-03]`, which spans seven plans (122-02, 03, 07, 08, 09, 12, 13); only plan 122-13 is authorized to tick it. `requirements-completed: []` above reflects this — this plan discharges CLOSE-03's literal "decision made and recorded before any push" clause, but the requirement as a whole (which also covers the actual push, both channel verifications, and the community comments) is not complete until 122-13.

## Ordering proof for plan 122-13

`122-DECISION.md`'s commit: **`d5c49d4`**, timestamp **`2026-07-30T13:03:38Z`** (`git log -1 --format='%H %ad' --date=iso-strict -- .planning/phases/122-close-honesty-ledger-community-ask-release-decision/122-DECISION.md`). Plan 122-13 should re-cite this hash/timestamp and confirm it is strictly earlier than either sub-repo's outbound merge-push commit (landed in plan 122-07).

## Next Phase Readiness

- Plan 122-03 (inbound `beta` → branch merge with the two-file `--ours` resolution) can proceed on an unchanged foundation — this plan proved the merge-tree conflict set is still exactly `firestarter/submit.py` + `tests/test_submit.py` in the app repo and zero in firmware, and `origin/beta` has not moved.
- Both sub-repos are provably unmutated: `firestarter` HEAD still `48c36e5…`, `firestarter_app` HEAD still `c3c9424…`, `origin/beta` in both repos still at the fetched tips, both gitlinks in the meta repo still pinned at `0048b3d…`/`96e0622…`.
- No blockers.

---
*Phase: 122-close-honesty-ledger-community-ask-release-decision*
*Completed: 2026-07-30*

## Self-Check: PASSED

`122-DECISION.md` confirmed present on disk at the stated path (325 lines). Commit `d5c49d4` confirmed present via `git log --oneline --all | grep d5c49d4`. Both sub-repo HEADs and `origin/beta` re-confirmed unchanged after the write.
