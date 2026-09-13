---
created: 2026-09-13T20:45:00Z
title: publish.yml's release published trigger has never fired — 8 of 8 runs are workflow_dispatch
area: tooling
resolves_phase: unassigned
source: .planning/phases/191-the-branch-that-reaches-users/191-CONTEXT.md (D-04 / D-05)
files:
  - firestarter_app/.github/workflows/publish.yml (on origin/main — the defect: release published never fires; workflow_dispatch is the only path ever exercised)
  - firestarter_app/.github/workflows/beta-release.yml (on origin/beta — the proven pattern: a pypi job that calls publish.yml directly with secrets: inherit and target_commitish)
---

## Problem

`publish.yml` declares two triggers: `release: [published]` and a `workflow_dispatch` taking a
required `tag` input. Measured against this repository's entire run history: it has run **8
times, every one `event=workflow_dispatch`. Zero `release` events, ever.** The `release: published`
trigger has literally never fired in this repository.

The workflow's own comment block already documents why, dated from an earlier recovery
(Phase 20 E2E-01): "when a release is created by another workflow (e.g. `beta-release.yml`) using
a PAT that lacks `workflow` scope, GitHub suppresses the `release.published` event from triggering
downstream workflows." The `workflow_dispatch` input was added as a manual escape hatch, but
nothing in `release.yml` or `publish.yml` actually invokes it automatically — a human has to
remember to run it, tag by tag.

**The consequence is already on disk, not hypothetical:** GitHub release `2.0.8` exists
(cut 2026-08-07) while PyPI's latest published stable is `2.0.7` — `2.0.8` was cut and never
published, and nothing reported an error. The silent-failure shape is identical to the one this
same comment block describes for the beta channel ("GitHub reached b17 while PyPI stopped at
b15").

## Why it matters

A tag/release existing on GitHub gives no signal about whether the corresponding artefact is
actually installable from PyPI. Anyone reading GitHub's releases page (including the operator, or
an automated check keying off the latest GitHub release) would believe `2.0.8` was the current
stable when PyPI never received it. This is the second half of the same reachability gap
`release.yml`'s ruleset collision creates: even if that push succeeded, this trigger still would
not fire, and PyPI would still not receive the artefact.

## Known-good fix

`beta-release.yml` (`origin/beta`) already solved this exact problem for the beta channel, and the
fix generalizes directly. It adds a second job:

```yaml
pypi:
  needs: github
  uses: ./.github/workflows/publish.yml
  with:
    tag: ${{ needs.github.outputs.version }}
  secrets: inherit
```

This calls `publish.yml` **directly** as a reusable workflow immediately after the release job,
removing the dependency on the `release.published` event ever being delivered — the tag comes
from the release job's own `outputs.version` rather than being re-derived, so it cannot drift. It
also passes `target_commitish` on the release step itself (not shown above, but present in the
`github` job) so the tag lands on the commit containing the version bump, not the pre-bump
trigger SHA — the second half of the same fix.

`main`'s `release.yml` has **neither** piece: no `pypi` job calling `publish.yml` directly, and
(per the sibling defect filed alongside this one) its version-bump push is itself rejected by
`main`'s branch protection before a release would even exist to publish.

## Disposition

**Filed, not fixed, in Phase 191.** Porting the `pypi`-job pattern to `main`'s `release.yml` here
would be inert: this phase's D-04 deliberately does not fix the push-blocker defect filed
alongside this one, so the job that would call `publish.yml` still never runs regardless of
whether a `pypi` job exists to call it. A half-fix that cannot execute is worse evidence than a
filed defect — the next stable cut on `main` should reach for `beta-release.yml`'s pattern in full,
not have half of it already present and inert.
