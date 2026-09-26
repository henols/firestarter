---
created: 2026-09-13T20:45:00Z
corrected: 2026-09-13T23:30:00Z
title: publish.yml's release published trigger is suppressed for bot-created releases — 2.0.8 was cut and never published
area: tooling
resolves_phase: unassigned
source: .planning/milestones/v1.38-phases/191-the-branch-that-reaches-users/191-CONTEXT.md (D-04 / D-05); measurement corrected during 191 verification
files:
  - firestarter_app/.github/workflows/publish.yml (on origin/main — the trigger is fine; it is never delivered when release.yml creates the release)
  - firestarter_app/.github/workflows/release.yml (on origin/main — the actual defect site: creates the release with the default GITHUB_TOKEN, which cannot cascade)
  - firestarter_app/.github/workflows/beta-release.yml (on origin/beta — the proven pattern: a pypi job that calls publish.yml directly with secrets: inherit and target_commitish)
---

> **Corrected 2026-09-13, after filing.** The original version of this item asserted the
> `release: published` trigger "has literally never fired in this repository — 8 of 8 runs are
> `workflow_dispatch`." **That measurement was wrong**, and it was wrong because it was taken with
> `gh run list --limit 10`: eleven runs existed, so the listing cut exactly one row — the oldest,
> which was the single `release`-event counterexample. The trigger fires. The **fix** proposed
> below was correct then and is unchanged now; only the diagnosis has been replaced.

## Problem

`publish.yml` declares two triggers: `release: [published]` and a `workflow_dispatch` taking a
required `tag` input. The `release: published` trigger **works** — but it is silently suppressed
for exactly the releases that matter most: the ones `release.yml` creates automatically.

Measured live 2026-09-13 (`gh run list --workflow publish.yml --limit 30`, 13 runs total), the
correlation is perfect:

| tag | release created by | `publish.yml` run | on PyPI? |
|-----|--------------------|-------------------|----------|
| 2.0.7 | `henols` (User) | `20956549620`, `event: release`, **success** | yes |
| 2.0.8 | `github-actions[bot]` (Bot) | **none — never fired** | **no** |
| 2.0.9 | `henols` (User) | `34785081535`, `event: release` (raced, see below) | yes |

Every **human**-created release triggered a publish. The one created by a **workflow** did not.

The mechanism is documented GitHub behavior, and `publish.yml`'s own comment block already names
it (dated from an earlier recovery, Phase 20 E2E-01): a workflow run authenticated with the
default `GITHUB_TOKEN` does not create new workflow runs, so the `release: published` event it
emits is never delivered. `release.yml` creates its release via `softprops/action-gh-release` with
that token — so the event it raises reaches nothing.

**The consequence is on disk, not hypothetical:** GitHub release `2.0.8` exists (cut 2026-08-07 by
`github-actions[bot]`) while PyPI skips straight from `2.0.7` to `2.0.9`. `2.0.8` was cut and
never published, and nothing reported an error.

**Secondary hazard, observed 2026-09-13:** when the operator hand-creates a release *and* also
hand-dispatches `publish.yml`, the two race. Run `34785081535` (auto, `event: release`) and run
`34785081751` (manual, `workflow_dispatch`) started in the same second for `2.0.9`; the manual one
won the upload and the automatic one failed with a PyPI "File already exists" collision on the
sdist. **For a hand-cut release the manual dispatch is redundant** — create the tag and release,
then watch whether the release-event run publishes on its own before reaching for
`gh workflow run`.

## Why it matters

A tag/release existing on GitHub gives no signal about whether the corresponding artefact is
installable from PyPI — and the gap opens precisely on the automated path, which is the one nobody
is watching. Anyone reading GitHub's releases page (the operator, or an automated check keying off
the latest GitHub release) would believe `2.0.8` was the current stable when PyPI never received
it. The silent-failure shape is identical to the one `publish.yml`'s comment block already
describes for the beta channel ("GitHub reached b17 while PyPI stopped at b15").

## Known-good fix

Unchanged from the original filing — and the corrected diagnosis makes it *more* clearly right,
not less. `beta-release.yml` (`origin/beta`) already solved this exact problem for the beta
channel by adding a second job:

```yaml
pypi:
  needs: github
  uses: ./.github/workflows/publish.yml
  with:
    tag: ${{ needs.github.outputs.version }}
  secrets: inherit
```

This calls `publish.yml` **directly as a reusable workflow** rather than relying on an event
cascade — which is exactly the right shape, because the event cascade is what `GITHUB_TOKEN`
suppresses. A reusable-workflow call is not an event and is not subject to the restriction. The
tag comes from the release job's own `outputs.version` rather than being re-derived, so it cannot
drift. It also passes `target_commitish` on the release step so the tag lands on the commit
containing the version bump rather than the pre-bump trigger SHA.

`main`'s `release.yml` has neither piece.

## Relationship to the sibling defect

Both this and `2026-09-13-release-yml-autocommit-vs-ruleset.md` are the **same root cause**: the
default `GITHUB_TOKEN`'s deliberate limitations. There, it cannot bypass the ruleset's
`pull_request` requirement to push a version bump (observed live: `GH013`, run `34784468070`).
Here, it cannot cascade an event to another workflow. `beta-release.yml`'s pattern addresses both,
which is why both items name it.

## Disposition

**Filed, not fixed, in Phase 191.** Porting the `pypi`-job pattern to `main`'s `release.yml` here
would be inert: this phase's D-04 deliberately does not fix the push-blocker defect filed alongside
this one, so the job that would call `publish.yml` still never runs regardless of whether a `pypi`
job exists to call it. A half-fix that cannot execute is worse evidence than a filed defect — the
next stable cut on `main` should reach for `beta-release.yml`'s pattern in full.
