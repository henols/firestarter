# Phase 207: The version and the record - Context

**Gathered:** 2026-09-23
**Status:** Ready for planning
**Source:** No `/gsd-discuss-phase` run. The operator answered the three operator-marked forks (F1, F7, F8) from `207-RESEARCH.md` at plan time. All other forks are Claude's discretion, and the research recommendations are the default.

<domain>
## Phase Boundary

Both sub-repos carry `3.1.0b1` in one commit pair (REL-01). The wiki documents the breaking change (ordinals 4 and 6 retired), the mixed-version pairings and what a user does about them, and the `write --verify` / `--full` / host-side `-b` surfaces (REL-04). No GitHub Release is cut from the meta repository, and no tag is created in this phase.
</domain>

<decisions>
## Implementation Decisions

### Locked by the operator (2026-09-23)
- **D-01:** In each sub-repo, merge `origin/beta` into `v1.41-verification-to-host` BEFORE the version bump (research F1 option A), then bump from `3.0.0b50` / `3.0.0b35` to `3.1.0b1`, so the ship PR merges with no conflict on the version line.
- **D-02:** Do the wiki work in the existing `/workspaces/firestarter.wiki` clone on top of the unpushed `f967398` and publish that commit together with the 3.1.0b1 docs (research F7 option A); the push checkpoint must show the full `git log origin/master..HEAD` with `f967398` named.
- **D-03:** Push the wiki in-phase, behind a `checkpoint:human-action` the operator approves, with every new statement labelled "from 3.1.0b1" (research F8 option A).

### Claude's Discretion
Forks F2–F6, F9 and F10 follow the `207-RESEARCH.md` recommendations unless the planner finds evidence against one. Record any departure in the plan.
</decisions>

<canonical_refs>
## Canonical References

- `.planning/phases/207-the-version-and-the-record/207-RESEARCH.md`: forks F1–F10, the compatibility matrix, the pitfalls, and the V0 venv rebuild recipe.
- `.planning/phases/204-the-command-surfaces-leave-the-firmware/204-BENCH-MATRIX.md`: REL-02/REL-03 bench evidence, including the verbatim `Unknown command: 6` / `Unknown command: 4`.
- `/workspaces/CLAUDE.md` § Milestone close and branch protection: a `beta` push publishes; no meta GitHub Release; bare tags only.
</canonical_refs>

<deferred>
## Deferred Ideas

- Teaching the `devtest-triage` skill that `Unknown command: 6/4` means a CLI/firmware version mismatch (research open question 5). This is outside Phase 207 scope.
- Correcting stale v1.40 lines in STATE.md (research open question 4). This is orchestrator housekeeping, not phase work.
</deferred>
