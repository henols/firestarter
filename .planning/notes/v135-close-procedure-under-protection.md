# v1.35 — The GSD close procedure under branch protection

**Date:** 2026-09-02
**Raised during:** Phase 173 (POLICY-05)
**Status:** Decided and applied — `.planning/config.json` now sets `git.base_branch` to `beta` and `git.protected_branches` to `["main"]`

## The decision

`git.base_branch` is `beta` and `git.protected_branches` is `["main"]`, set as tier-1 configuration
rather than prose, because prose alone leaves the resolver returning `main` — POLICY-05 satisfied by
a document the tooling ignores (D-06). Verified by read-back, not merely set:

```
base-branch before: main
is-protected beta before: false
is-protected main before: true
is-protected gsd/v1.35-documentation-consolidation-wiki-migration before: false

base-branch after: beta
is-protected beta after: true
is-protected main after: true
is-protected gsd/v1.35-documentation-consolidation-wiki-migration after: false
```

The two distinguishing flips are `git.base-branch` moving from `main` to `beta`, and
`--is-protected beta` moving from `false` to `true`. `--is-protected main` reads `true` both before
and after — tier 2 already resolved `main` as the base branch before this edit, and the base branch
is always folded into the protected list, so that read-back alone would prove nothing. The `false` on
the current milestone branch, both before and after, is what shows the resolver actually verified
against the repository rather than falling back to the fail-closed path, which renders `true` for
every branch.

## What this changes

| Consumer site | Effect of the repoint |
|---|---|
| `complete-milestone.md:734` | `BASE_BRANCH=$(gsd_run query git.base-branch)` now resolves `beta`. |
| `complete-milestone.md:775` | The squash-merge arm's `git checkout ${BASE_BRANCH}` checks out `beta`, not `main`. |
| `complete-milestone.md:789` | `git merge --squash "$MILESTONE_BRANCH"` merges onto the checked-out `beta`. |
| `complete-milestone.md:804` | The history-merge arm's `git checkout ${BASE_BRANCH}` also checks out `beta`. |
| `ship.md:46` | `BASE_BRANCH=$(gsd_run query git.base-branch)` now resolves `beta`. |
| `ship.md:78` | `IS_PROTECTED=$(gsd_run query git.base-branch --is-protected "$CURRENT_BRANCH")` — advisory only; warns and continues. |
| `ship.md:316` | `RANGE_BASE=$(git merge-base "${BASE_BRANCH}" HEAD)` anchors the TDD audit range on `merge-base beta HEAD`. |
| `ship.md:373` | `gh pr create --base "${BASE_BRANCH}"` opens pull requests against `beta`. |
| `execute-phase.md:290` | `DEFAULT_BRANCH=$(gsd_run query git.base-branch ...)` decides what a new phase branch forks off. |
| `quick.md:197` | Same resolver call decides what a new quick branch forks off. |
| `pr-branch.md:28` | `TARGET=${1:-$(gsd_run query git.base-branch)}` — the default PR-branch target becomes `beta`. |
| `execute-phase/steps/protected-branch.md:10-15` | Warns if the current branch is protected; unreachable here because this project is `branching_strategy: milestone`, not `none`. |

`ship.md:316` anchoring on `merge-base beta HEAD` means a **stale local `beta`** silently mis-anchors
the audit range — local `beta` measured 205 commits behind `origin/beta` at the time this note was
written. Local `beta` must be recreated from `origin/beta` before `/gsd-ship` runs. Meta's
`origin/beta` tip is a merge commit with two parents, so the close tail must be **merged**, not
fast-forwarded, and any ancestry check must use `git cherry` rather than `--is-ancestor` — the v1.30
squash-merge made ancestry lie.

## The route into main, and where it stops

A pull request is the **only** route into any of the three repositories' `main`:
`current_user_can_bypass` is `never` on all three rulesets, so no person, the operator included, can
bypass. This is why POLICY-05's "documented admin bypass" branch cannot be written — there is no
bypass to document.

The route is blocked end to end anyway. Once a pull request merges to `main`, both sub-repositories'
release workflows auto-commit a version-bump commit back onto `main` from CI using the default
`GITHUB_TOKEN`, which the `pull_request` rule refuses, and the lone bypass actor
(`DeployKey:null:always`) does not cover a `GITHUB_TOKEN`-authenticated push. The next stable release
in both repositories fails at that version-bump step. See Backlog 999.46 for the full analysis and
the recommended remedy — moving the version bump off `main` — which is not restated here.

## Banked evidence — the pull-request route already works

`prom#54`, `firestarter#58` and `firestarter_app#57` all merged into a protected `main` on
2026-09-02, between 08:56:58Z and 08:57:06Z — **after** the rulesets were created. The
pull-request-only route into `main` is demonstrated three times already; the `wiki-check.yml`
workflow-leg pull request in plan 173-06 is a fourth instance, not the first.

## A premise this requirement rests on that is not true

`REQUIREMENTS.md:119` says `/gsd-complete-milestone` pushes `main` directly today. It does not: the
only `git push` in the whole `complete-milestone` tree is a **tag** push, at `git-tag.md:26`
(`git push origin v[X.Y]`), and all three rulesets are `target: branch`, so a tag push is ungoverned
by them. The real failure surface is threefold, and none of the three is a blocked push:

1. A purely local `git checkout main` + `git merge --squash` at `complete-milestone.md:775` that
   **succeeds** and leaves a local `main` that can never be pushed, with nothing warning that it
   happened.
2. `ship.md:373` opening pull requests `--base main`.
3. Three fork-point consumers — `execute-phase.md:290`, `quick.md:197` and `pr-branch.md:28` — which
   decide what every new phase branch and quick branch forks off, today `origin/main`, the opposite
   of the operator's standing branching instruction.

The repoint in this plan fixes all three at once. The third is a pre-existing correctness win this
phase gets for free — new branches were forking off the wrong ref before POLICY-05 was ever written.
This correction is carried into the honesty ledger rather than quietly absorbed.

## What this costs

`git-base-branch.cjs:305` folds the resolved base branch into `protectedBranches`, so GSD now treats
`beta` as protected while GitHub does not — `beta` appears in no ruleset condition in any of the three
repositories. Both consumers of the protected-branch check, `ship.md:78` and
`execute-phase/steps/protected-branch.md:10-15`, only warn and continue rather than refuse, and the
second applies only to `branching_strategy: none`, which this project is not (`milestone`), so the
repoint cannot break the close. The asymmetry is recorded here as something to resolve whenever
someone revisits the rulesets, not as a defect this plan fixes.

## A note on link stability

Backlog 999.9 will rename all three repositories and invalidate every `henols/firestarter*` URL this
note or any other v1.35 artifact writes. This note joins the set of phase 173 outputs needing
re-sweeping once that rename lands, alongside the procedure note, the twelve wiki footers and the
four upstream replies. Every citation above is a file path and line number rather than a URL, so it
stays mechanically greppable in the meantime.
