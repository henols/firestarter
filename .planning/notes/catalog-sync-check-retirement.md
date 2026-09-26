---
title: Catalog sync check retirement — why it never asserted what it claimed, and what is lost with it
date: 2026-09-11
context: v1.37 Phase 185, CLAIM-08 (D-01, D-02, D-03) — read from the live workflow file before deletion
---

# Catalog sync check retirement (CLAIM-08)

## VERDICT

**`Catalog sync check` is retired outright — the workflow file is deleted, on the operator's own
decision, taken against the orchestrator's recommendation to re-point its trigger at `beta`.** The
check has run eight times since 2026-07-11: six failures, two successes. Both of its runs on
`main` failed. It has never once asserted the property it exists to assert on the one branch its
requirement and its own trigger name — `main`. Its two successes were on a milestone branch, hours
after a fix that could not, by construction, help on `main`. The operator's grounds, in their own
words: the catalog *"has no value to the main branch and shall not be executed by the CI — it's a
tool that is used when a new message is created while developing and must be generated there and
then. If it's not executed before fw is committed the fw will not compile."* That is recorded here
so a later reader does not read the deletion as an oversight or as evidence the property stopped
mattering — it never mattered on `main`, and the operator chose to stop pretending otherwise.

This note carries all five things CLAIM-08's amendment requires it to carry: the cause of the
standing failure, why the 2026-08-18 fix did not reach it, the correction of the workflow's own
now-false comment, the counterfactual that a naive `beta` fallback would not have worked either,
and the residual gap the retirement leaves — named plainly, and left unfiled on the operator's
explicit instruction (D-04).

## 1. The cause

`tools/catalog/**` has never existed on either sub-repo's `main` branch. The vendored catalog
landed on `beta`; `main` lags `beta` by roughly 224 commits in the firmware repo, and as of this
session `firestarter@main` carries no `tools/catalog/` directory at all. The workflow's failing
step, quoted verbatim from the file before its deletion:

```
- name: Assert cross-sub-repo vendored catalog identity
  run: |
    cmp firestarter/tools/catalog/messages.toml firestarter_app/tools/catalog/messages.toml
    diff firestarter/tools/catalog/messages.toml firestarter_app/tools/catalog/messages.toml
    echo "OK: vendored messages.toml byte-identical across sub-repos"
```

On every `main` run this `cmp` exits **2** — operand missing, not operand differing — with:

```
cmp: firestarter/tools/catalog/messages.toml: No such file or directory
```

The distinction matters and is easy to blur: an exit 2 says the check never ran at all, not that
the two catalogs disagreed. The workflow's own comment (quoted in full under §3) names this
directly: *"The step below used to fail with `cmp: firestarter/tools/catalog/messages.toml: No
such file or directory`."* The most recent failing run on `main` is
**run `33447867312`**, 2026-08-31T22:47:56Z, `push` event, 20 s duration. Its "Resolve sub-repo
ref" step output read `meta ref under test: main`, `firestarter -> main`,
`firestarter_app -> main` — both sub-repos correctly resolved to `main`, and both then hit the
identical missing-file error the workflow's comment describes, because `main` is exactly the
branch on which the file being compared has never existed.

## 2. Why the 2026-08-18 fix did not fix it

Commit `57e63429` replaced a hardcoded `ref: main` on both sub-repo checkouts with a
same-branch-name-else-`beta` resolution step (quoted in full under §3, "Resolve sub-repo ref").
Its fallback logic is: try the meta ref's own branch name on each sub-repo; if that branch is
**missing**, fall back to `beta`. That fallback fires only when the named branch does not exist on
the sub-repo — and `main` exists on both sub-repos, so on a `main` run the fallback can never fire.
The resolution step correctly finds `main` on both sub-repos and correctly checks it out; the
catalog directory simply is not there, because it never has been.

Run `33447867312` (2026-08-31, `main`, push) is the direct proof: its resolve step printed
`firestarter -> main` and `firestarter_app -> main` — the fix worked exactly as designed and
still failed, because `main` is the one branch where no fallback the fix could express would have
helped.

The fix's other half worked, and worked immediately. The full eight-run history:

| Date | Conclusion | Branch | Event | Run |
|---|---|---|---|---|
| 2026-07-11 | failure | `main` | push | 29147915116 |
| 2026-08-09 | failure | `gsd/v1.31-27c-…` | pull_request | 31316652539 |
| 2026-08-18 | failure | `gsd/v1.31-27c-…` | pull_request | 32110106709 |
| 2026-08-18 | failure | `gsd/v1.31-27c-…` | pull_request | 32110732140 |
| 2026-08-18 | failure | `gsd/v1.31-27c-…` | pull_request | 32118301480 |
| 2026-08-18 | **success** | `gsd/v1.31-27c-…` | pull_request | 32118599666 |
| 2026-08-18 | **success** | `gsd/v1.31-27c-…` | pull_request | 32122444857 |
| 2026-08-31 | failure | `main` | push | 33447867312 |

Both successes landed hours after `57e63429`, on the same `gsd/v1.31-27c-…` milestone branch,
where the sub-repos genuinely carry a same-named branch with the catalog on it — so the
same-branch-name resolution found a real file and the assertion passed for the first and only
times in the workflow's history. Both `main` runs — the one before the fix and the one after —
failed. The fix repaired the workflow for milestone branches and left `main` exactly as broken as
it started, because `main`'s problem was never a wrong ref; it was that the compared file has never
existed there.

## 3. That the workflow's own comment is now false

The workflow's "Resolve sub-repo ref" step carried this comment block, quoted verbatim from the
live file before deletion:

```
# Resolve which sub-repo ref to compare against, instead of hardcoding `main`.
#
# `ref: main` could never work: `tools/catalog/**` has NEVER existed on
# either sub-repo's `main` branch -- the vendored catalog landed on `beta`,
# and `main` lags `beta` by ~224 commits in the firmware repo. The step
# below used to fail with `cmp: firestarter/tools/catalog/messages.toml:
# No such file or directory`, and this workflow had never once succeeded
# (5 runs, 5 failures, 2026-07-11 through 2026-08-18) -- so it has never
# actually asserted the authority property it exists to assert.
#
# The assertion is about LOCKSTEP, and lockstep is per-branch: a
# firmware-touching milestone changes meta's authoritative catalog and both
# vendored copies on its own three same-named branches, and they only reach
# `beta` together at close. So compare against the same branch name as the
# meta ref under test, falling back to `beta` when the sub-repos have no
# such branch (e.g. a meta-only docs branch). Meta stays the authority
# within whichever branch is resolved -- the two assertions below are
# unchanged.
```

The claim *"this workflow had never once succeeded (5 runs, 5 failures, 2026-07-11 through
2026-08-18) — so it has never actually asserted the authority property it exists to assert"* was
true at the moment it was written. It was overtaken within hours, by the same day's runs
`32118599666` and `32122444857` — the two successes in the table above, both dated 2026-08-18, both
after `57e63429` landed. **Correction, in place, since the comment's own source file is being
deleted and this note is the only place the correction can land:** the workflow did, in fact, once
assert the authority property it exists to assert — twice, both times on a milestone branch, never
on `main`. The corrected, complete claim is the one this whole note exists to state: 8 runs total,
6 failures, 2 successes, and both runs on `main` — the branch the requirement and the workflow's
own trigger name — failed.

## 4. That a naive `beta` fallback would not have worked either

A reader's next question is whether simply always falling back to `beta` — rather than the
same-branch-name-else-`beta` logic the fix actually implemented — would have made the check pass
on `main`. Measured this session, before the deletion:

| Path | Size | sha256 (first 16) | Snapshot |
|---|---|---|---|
| `meta@main` | 27 867 B | `cd5a0bb99a74d4f7` | `main` snapshot |
| `firestarter@beta` | 28 658 B | `260066039d07ab5c` | `beta` snapshot |
| `firestarter_app@beta` | 28 658 B | `260066039d07ab5c` | `beta` snapshot |
| `firestarter@main` | absent | — | `main` snapshot |

A `beta` fallback would have let the workflow's first assertion —
*"Assert cross-sub-repo vendored catalog identity"* — pass: both sub-repos' `beta` copies are
byte-identical to each other (`260066039d07ab5c`, both 28 658 B). But the workflow's second
assertion, *"Assert vendored catalog matches meta-repo authoritative copy"*, compares those same
sub-repo copies against `meta`'s own checked-out ref — and on a `main` run that ref is
`meta@main`, which is 27 867 B, `cd5a0bb99a74d4f7`, **791 bytes behind** the `beta` copies both
sub-repos would be compared against. The second `cmp` would exit non-zero for a real content
difference this time, not a missing file. **The failure would only have changed its reason** —
from "operand missing" to "operand differing" — not its outcome. A naive `beta` fallback is not a
route past this failure; it only changes which of the workflow's two assertions is the one that
fails.

(For clarity to a future reader: the working-tree figures measured live during this same session
on this milestone branch — `tools/catalog/messages.toml` at 28 658 B, sha `260066039d07ab5c`,
identical across meta and both sub-repos — are **not** the `main`-snapshot figures in the table
above. They confirm the property is real and in lockstep on development branches; they say
nothing about `main`, where the meta figure above is the one that applies.)

## 5. The residual gap, named explicitly

With the workflow deleted, **nothing in either repository, on any branch, at any point after this
phase, compares the two sub-repos' vendored `messages.toml` copies against each other or against
meta's authoritative copy — except at the moment `tools/catalog/sync_to_subrepos.sh` is run.**

Four gates survive the retirement, each proving only its own half:

| Gate | Location | Property proved |
|---|---|---|
| Catalog validity | `firestarter/.github/workflows/build.yml` → `codegen.py --check` | firmware's own vendored toml is well-formed |
| Codegen drift (`messages.h`) | same workflow → regenerate, `git diff --exit-code include/messages.h` | firmware's own toml generates firmware's own committed artifact |
| Catalog validity | `firestarter_app/.github/workflows/ci.yml` → `codegen.py --check` | host's own vendored toml is well-formed |
| Codegen drift (`messages.py`) | same workflow → regenerate, `git diff --exit-code firestarter/messages.py` | host's own toml generates host's own committed artifact |

**None of the four compares the two vendored copies with each other.** That asymmetry is the gap:
each sub-repo's CI proves its own toml is internally consistent with its own generated file, and
proves nothing about whether the other sub-repo's toml agrees with it. The concrete failure this
admits: a hand-edit to `firestarter/tools/catalog/messages.toml` that bypasses both meta and
`sync_to_subrepos.sh` would regenerate `firestarter/include/messages.h` cleanly, pass its own
drift gate, compile fine — and diverge silently from `firestarter_app`'s vendored copy of the same
catalog, which is precisely the silent cross-repo misreport the catalog mechanism exists to
prevent.

Why that is accepted rather than closed: the per-sub-repo compile and drift gate is the practical
check during day-to-day development, and `tools/catalog/sync_to_subrepos.sh` — repaired in this
phase's plan 185-05 so its two previously self-comparing verifications can now genuinely fail —
is the sole remaining mechanism that asserts cross-sub-repo byte-identity, and it does so at sync
time: its "Assert cross-sub-repo vendored catalog identity" step (lines 65-70) runs a real
two-operand `diff` between the two sub-repos' vendored copies, with an `else` branch that prints
an `ERROR:` line and exits non-zero, proven in 185-05 by planting a divergence, observing that
`ERROR:` line and the non-zero exit, and then restoring and re-observing green. That assertion
only fires when someone runs the script — it is not a standing CI gate, and this note does not
claim it is one.

**This workflow is the meta repository's only workflow.** `.github/workflows/` currently contains
exactly one file. After this deletion, `.github/workflows/` is empty and **the meta repository runs
no CI at all** — not "nothing checks cross-repo catalog identity," but nothing in this repository
runs, on any push or pull request, for any reason. That is the sharper, correct statement of what
is lost, and it is stated here so a later reader does not have to rediscover it from an empty
directory.

**No successor guard and no backlog item are filed for this gap.** This is deliberate, on the
operator's own decision (D-04), not an oversight and not something this note argues against. The
gap is real, it is named above in full, and a differently-scoped guard (a sub-repo CI step, or a
pre-commit hook, rather than a meta-repo workflow that can only see all three repos by checking
each of them out) could close it properly — but the operator was presented with that option and
declined it. Naming a gap and filing a gap are different acts; this note performs only the first.

## Two questions a reader will ask next

**Can this deletion leave a pull request permanently pending?** No. Measured via the GitHub API
during this milestone: no `main` branch in any of the three repositories (`firestarter_prom`,
`firestarter`, `firestarter_app`) has any **required status checks** configured
(`required_status_checks: NONE` on all three). This workflow was never a required check on any
branch, so removing it cannot leave a PR stuck waiting on a check that no longer reports.

**Does GitHub stop showing the workflow immediately?** No, and that is expected, not a defect in
this retirement. GitHub de-registers a workflow only once the deletion reaches the repository's
default branch — a post-merge event on a protected `main` this phase does not touch (`main` is
protected in all three repositories, and this project's base branch is `beta`). Until that merge,
`gh workflow list` will continue to show `Catalog sync check`, and `workflow_dispatch` will remain
invocable from `main`. `gh run list` after this deletion is used only to confirm that no *new* run
has appeared since run `33447867312` — it is not, and cannot be, proof that the amended
requirement (the check is retired, and the cause of its failure is recorded) has been satisfied,
because the workflow's registration on GitHub has not yet changed and will not change until this
branch merges.
