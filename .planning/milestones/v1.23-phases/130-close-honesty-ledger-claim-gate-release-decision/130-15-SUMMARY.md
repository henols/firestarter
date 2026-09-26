---
phase: 130-close-honesty-ledger-claim-gate-release-decision
plan: 15
subsystem: infra
tags: [release, gh-cli, pypi, ci, verification, honesty-ledger]

# Dependency graph
requires:
  - phase: 130-close-honesty-ledger-claim-gate-release-decision (plan 14)
    provides: 130-HANDOFF.md operator procedure with the pre-hand-off tag ceiling (3.0.0b14)
provides:
  - 130-CHANNELS.md — committed, read-only transcript proving both distribution channels
    (firmware GitHub prerelease with py32 asset; PyPI) are publicly live at 3.0.0b15
affects: [130-16]

# Tech tracking
tech-stack:
  added: []
  patterns: [read-only gh-cli verification transcript, fresh-venv PyPI resolution check]

key-files:
  created:
    - .planning/phases/130-close-honesty-ledger-claim-gate-release-decision/130-CHANNELS.md
  modified: []

key-decisions:
  - "Task 1 (checkpoint:human-verify) treated as pre-approved per orchestrator instruction — operator confirmed 130-HANDOFF.md steps 1-7 complete, resume signal 'pushed and dispatched' recorded verbatim in 130-CHANNELS.md"
  - "Fail-closed precondition (Task 2) independently re-derived rather than trusted: read 3.0.0b15 as newest tag in both repos via gh release list, strictly newer than the 130-HANDOFF.md-recorded 3.0.0b14 ceiling"
  - "D-03 asset gate asserted against the real gh release view output, not the CI run conclusion, per continue-on-error/unset fail_on_unmatched_files caveat"
  - "PyPI resolution verified from a fresh throwaway venv under the scratch dir, never this project's editable-install environment"

patterns-established: []

requirements-completed: []  # This plan ticks NO requirement id per its own held-writes contract; CLOSE-04 is plan 130-16's alone.

coverage: []  # Read-only verification transcript, no shippable deliverable with automated coverage; see human_judgment note below.

# Metrics
duration: ~20min
completed: 2026-08-02
status: complete
---

# Phase 130 Plan 15: Both-Channels-Public Verification Transcript Summary

**Independently re-verified (not trusted from the orchestrator's report) that `3.0.0b15` is live on both PyPI and GitHub in both `henols/firestarter` and `henols/firestarter_app`, that `firestarter_py32f071.hex` shipped as a real release asset for the first time, and recorded the first CI attempt's failure and fix as a genuine finding.**

## Performance

- **Duration:** ~20 min
- **Tasks:** 3 (Task 1 treated as pre-approved hand-off boundary; Tasks 2-3 executed)
- **Files modified:** 1 (`130-CHANNELS.md`, created)

## Accomplishments
- Independently read `gh release list` in both repos and confirmed `3.0.0b15` is strictly newer than the `3.0.0b14` ceiling recorded in `130-HANDOFF.md` line 121 — the fail-closed precondition passed on freshly-read data, not on the orchestrator's narration.
- Asserted `firestarter_py32f071.hex` present on the real `3.0.0b15` firmware release (D-03 hard gate), contrasted against the b14 before-state (zero py32 assets), alongside all three AVR hexes (REL-03 containment).
- Verified PyPI resolution of `firestarter==3.0.0b15` from a fresh `python3 -m venv` under the scratch directory (never this project's editable install), resolved on the first attempt with no retry needed; confirmed PyPI's `info.version` unchanged at `2.0.7` (no stable release).
- Recorded, with independently re-derived `gh run list` evidence, that the first CI attempt failed in both repos (`beta-build.yml` run `30766766233`, `beta-release.yml` run `30766774000`) on three pre-existing CI-only sibling-checkout test defects, fixed via commits `1c511e8` and `5934a54`, both confirmed present and ancestors of `origin/beta` in this session.
- Recorded explicitly that a green workflow tick was not accepted as evidence for either channel, the no-stable-release state (including GitHub's `/releases/latest` still resolving to `2.0.6`/`2.0.7`), `main` untouched in all three repos, and the non-empty inbox (gh#18, gh#20).

## Task Commits

1. **Task 1: Fail-closed precondition hand-off boundary** — no commit (checkpoint; no command executed against any remote; treated as pre-approved per orchestrator instruction)
2. **Task 2: Read observed tag and confirm fail-closed precondition** — `8cc6136` (docs)
3. **Task 3: Assert py32 asset and verify PyPI from clean venv** — `bfd881a` (docs)

**Plan metadata:** this plan intentionally makes **no** final metadata commit touching `STATE.md`/`ROADMAP.md`/`REQUIREMENTS.md`/`PROJECT.md` — the orchestrator's held-writes contract for this plan forbids editing any of those four files or ticking any requirement id; that is plan 130-16's job alone.

_Note: this is a read-only verification plan — no TDD tasks, no source-code changes._

## Files Created/Modified
- `.planning/phases/130-close-honesty-ledger-claim-gate-release-decision/130-CHANNELS.md` - the committed both-channels-public verification transcript: fail-closed precondition read, the two-attempt-cut CI defects, the D-03 py32 asset gate, the CONSTRAINT-7 clean-venv PyPI check, the not-accepted-as-evidence section, no-stable/main-untouched/inbox sections, summary verdict, and self-verifying facts for plan 130-16.

## Decisions Made
- Treated Task 1 as approved per the orchestrator's explicit instruction that the operator authorized the publish and the hand-off procedure was performed in full — but still independently re-derived Task 2's precondition from fresh `gh` reads rather than trusting the orchestrator's report of the observed tag, per the plan's own CONSTRAINT 5 (read, never trust/compute).
- Did not touch either sub-repo's gitlink in the meta repo, did not tick any `CLOSE-*` requirement id, and made no privileged (`gh`-write or git-remote-write) command — confirmed by re-reading `origin/beta` in both repos at the end of execution and finding it unchanged from the values read at the start.

## Deviations from Plan

None — plan executed exactly as written. Task 1's checkpoint was resolved per explicit orchestrator instruction (the operator had already authorized and the hand-off procedure was already performed), not by this executor approving its own checkpoint.

## Issues Encountered

None beyond what the plan itself anticipated and instructed how to record: the first CI attempt of the cut failed in both repos (expected to be possible, per the plan's own read_first material and the orchestrator's prompt), and the fix commits (`1c511e8`, `5934a54`) were independently confirmed present and ancestors of `origin/beta` rather than merely asserted from the prompt.

## User Setup Required

None - no external service configuration required. This plan performed no privileged action; the publish itself was completed by the operator before this plan ran.

## Next Phase Readiness
- `130-CHANNELS.md` is committed and ready for plan 130-16 to lift its self-verifying facts (observed tag, asset presence, PyPI verification, main-untouched, gitlink-bump-not-done-here, no-requirement-ticked-here) without re-deriving them.
- Plan 130-16 owns: re-bumping the `firestarter` gitlink in the meta repo (per `130-HANDOFF.md` §1.9), ticking CLOSE-01 through CLOSE-04, and the closing sweep (`130-NONREGRESSION.md`).
- No blockers. `origin/beta` in both sub-repos ends this plan exactly where it started it: `firestarter` `0933bd7d602efb30e4a666e8231ecf724e90ab09`, `firestarter_app` `16a313a040389aa7c88a98b85f79a7d667ca2f6f`.

---
*Phase: 130-close-honesty-ledger-claim-gate-release-decision*
*Completed: 2026-08-02*

## Self-Check: PASSED

- FOUND: `.planning/phases/130-close-honesty-ledger-claim-gate-release-decision/130-CHANNELS.md`
- FOUND: `.planning/phases/130-close-honesty-ledger-claim-gate-release-decision/130-15-SUMMARY.md`
- FOUND commit: `8cc6136` (task 2)
- FOUND commit: `bfd881a` (task 3)
- FOUND commit: `0755ff3` (plan completion)
- Branch unchanged: `gsd/v1.23-py32f071-integration`
- `origin/beta` unchanged across this plan's execution: `firestarter` `0933bd7d602efb30e4a666e8231ecf724e90ab09`, `firestarter_app` `16a313a040389aa7c88a98b85f79a7d667ca2f6f`
- Neither gitlink staged or committed by this plan (still the pre-existing ` M firestarter` / ` M firestarter_app` working-tree deltas from before this plan started)
