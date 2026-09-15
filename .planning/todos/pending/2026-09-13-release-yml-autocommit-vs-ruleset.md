---
created: 2026-09-13T20:45:00Z
title: release.yml's git-auto-commit-action push to main is rejected by the Protect main ruleset
area: tooling
resolves_phase: unassigned
source: .planning/milestones/v1.38-phases/191-the-branch-that-reaches-users/191-CONTEXT.md (D-04 / D-05)
files:
  - firestarter_app/.github/workflows/release.yml (on origin/main — the defect: pushes to main with the default GITHUB_TOKEN)
  - firestarter_app/.github/workflows/beta-release.yml (on origin/beta — the proven pattern this repository already uses on its beta channel)
---

## Problem

`release.yml` runs `on: push: branches: [main]`, with a `paths-ignore` list covering `**.md`,
`**.sh`, `.gitignore`, `docs/**`, `images/**`, `.github/**`, `.vscode/**` and `tools/**` — but
**not** `firestarter/**`. Any merge touching `firestarter/constants.py` (URL-02's own change,
among others) fires it.

Its `update_version.py` step bumps the patch version, and
`stefanzweifel/git-auto-commit-action@v5` then pushes the bump **directly to `main`** using the
default `GITHUB_TOKEN` — the step's `PERSONAL_ACCESS_TOKEN` env line is commented out.

`main`'s branch protection is ruleset **`22046179`** ("Protect main"), `enforcement: active`,
scope `~DEFAULT_BRANCH`, created **2026-09-01**. It enforces `pull_request` (among
`deletion`/`non_fast_forward`), its only bypass actor is `DeployKey`, and
`current_user_can_bypass` is `never` — no person, and no `GITHUB_TOKEN`, can push past a
`pull_request` rule. GitHub's own documentation and community guidance are explicit that the
default `GITHUB_TOKEN` cannot bypass a `pull_request` rule even when actors are listed.

**Consequence:** the auto-commit push is rejected, the step fails, the job aborts, and the
`Release` step never runs — no tag, no GitHub release, nothing reaches PyPI from this workflow.

**This has never been exercised under protection.** `release.yml`'s last recorded run was
`2026-08-07` on `e4112ef` — **25 days before** the ruleset was created on `2026-09-01`. The
collision is real but has not yet been observed failing in CI; Phase 191 predicts it and hands the
operator a manual tag/release/`workflow_dispatch` sequence instead of relying on this workflow.

## Why it matters

`main` is the branch every default `pip install firestarter` resolves against. Its own automatic
release pipeline cannot complete a single cut without manual intervention, and nothing in the
workflow surfaces that failure other than a red run in the Actions tab — the same silent-failure
shape as the `publish.yml` defect filed alongside this one.

## Known-good fix

This repository already solved the equivalent problem on its `beta` channel.
`beta-release.yml` (`origin/beta`) commits its own version bump with
`git-auto-commit-action` and pushes to `beta`, which is **not** under a `pull_request`-enforcing
ruleset — so the direct push succeeds there. Porting that exact shape to `main` is not possible
while `main` requires a pull request for every change; the fix here is either:

1. a credential change — a `PERSONAL_ACCESS_TOKEN` (or a `DeployKey`-based bypass) with the
   authority to push past the ruleset, wired into the commented-out `env:` line, or
2. a redesign that stops `release.yml` pushing to `main` at all — e.g. opening a bot-authored
   pull request for the version bump instead of pushing directly, mirroring how this milestone's
   own `main`-facing changes are prepared and merged.

Either direction changes how `main`'s protection interacts with automation and is out of scope for
a rename milestone.

## Disposition

**Filed, not fixed, in Phase 191.** URL-02 repoints one constant and bumps the version by hand in
the same commit specifically so the stable release does not depend on this workflow completing.
No ruleset change and no redesign of the stable release flow was made as part of this phase.
