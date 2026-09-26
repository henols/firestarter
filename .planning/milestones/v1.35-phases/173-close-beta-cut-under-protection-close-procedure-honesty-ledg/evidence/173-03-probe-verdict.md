# Phase 173 Plan 03: Ruleset Rejection Probe — Verdict Record

Measured 2026-09-02. Ruleset ids per `.planning/phases/172-policy-one-tracker-protected-main/evidence/172-06-ruleset-readback.txt`.

## Per-repository result

| repository | ruleset id | pushed from | exit code | first `remote:` line | control push | verdict |
|---|---|---|---|---|---|---|
| firestarter_prom | 22043478 | `checkout -B ruleset-probe origin/main` | 1 | `remote: error: GH013: Repository rule violations found for refs/heads/main.` | accepted, then deleted | PASS |
| firestarter | 4998759 | `checkout -B ruleset-probe origin/main` | 1 | `remote: error: GH013: Repository rule violations found for refs/heads/main.` | accepted, then deleted | PASS |
| firestarter_app | 22046179 | `checkout -B ruleset-probe origin/main` | 1 | `remote: error: GH013: Repository rule violations found for refs/heads/main.` | accepted, then deleted | PASS |

Full verbatim transcripts, both push halves, per repository:
- `173-03-probe-firestarter_prom.txt`
- `173-03-probe-firestarter.txt`
- `173-03-probe-firestarter_app.txt`

Each branch was created with `git checkout -B ruleset-probe origin/main`, a true fast-forward of
`origin/main`, so the rejection above came from GitHub's receive stage rather than from git's own
client-side non-fast-forward check (RESEARCH.md Pitfall 1). Each rejection also carries a
`- Changes must be made through a pull request.` clause, satisfying the pull-request-requirement
half of the acceptance rule. No `ruleset-probe`-prefixed branch remains on any of the three
remotes after the run (`git ls-remote --heads … 'ruleset-probe*'` returns empty on all three).

The CI-cost check on the control push registered no new workflow runs on any of the three
repositories within the observation window (an 8-second pause plus a follow-up `gh run list`
poll on `firestarter`) — the throwaway branch was deleted within roughly ten seconds of being
pushed, which appears to have been fast enough that GitHub Actions never queued a run against it
before the ref was gone. This is a measured absence, not an assumed one: it means the probe's CI
cost was smaller than RESEARCH.md Pitfall 4 estimated (`build.yml`/`py32f071.yml` on
`firestarter`, `ci.yml` on `firestarter_app`), not larger, and nothing published either way — the
observation neither strengthens nor weakens the PASS verdicts above, which rest solely on the
`remote:` rejection text.

## Rulesets unchanged before/after

`173-03-rulesets-before.json` and `173-03-rulesets-after.json` are field-for-field equal on `id`,
`enforcement`, `current_user_can_bypass`, `conditions` and `bypass_actors`, after normalizing
`bypass_actors` list order. All three ids are unchanged from Phase 172's measured values:
`firestarter_prom` `22043478`, `firestarter` `4998759`, `firestarter_app` `22046179`. No ruleset
was created, amended, disabled or deleted by this probe.

## Corroborating reads (context, not the discharge)

`gh api repos/henols/<repo>/rules/branches/main` and `.../beta`, all three repositories, read
after the probe:

| repository | `main` rules | `beta` rules |
|---|---|---|
| firestarter_prom | deletion, non_fast_forward, pull_request | (none) |
| firestarter | deletion, non_fast_forward, pull_request | (none) |
| firestarter_app | deletion, non_fast_forward, pull_request | (none) |

**This table is a reading of the ruleset configuration.** ROADMAP criterion 1 explicitly refuses
a reading of the ruleset configuration as the discharge of POLICY-04's demonstration half. It is
included here only so the probe's push-and-observe result above can be read next to the
configuration state it was taken against — never as a substitute for the push-and-observe result
itself.

## What this probe does and does not establish

- It **does** establish that a direct push to `main` is rejected by GitHub in all three
  repositories, from a true descendant of `origin/main`, with the rejection attributed to the
  ruleset by GitHub's own text (`GH013: Repository rule violations found`, naming the
  pull-request requirement).
- It **does** establish that the same branch pushes cleanly to an unprotected ref in all three
  repositories, so the rules are scoped to the default branch and not to the repository as a
  whole.
- It **does not** establish that a beta lockstep cut was performed under the rulesets.
  **No beta lockstep cut is claimed by this probe.** That is D-01's second deliverable, it is
  operator-gated, and if it is not separately authorized before the close, per D-03 POLICY-04 is
  marked complete on this probe with the missing half stated as a ledger non-claim. Criterion 1's
  own wording permits it: "an actual cut **or** an equivalent dry run that exercises the same
  paths."
- It **does not** establish anything about `beta` protection: `beta` carries no ruleset in any of
  the three repositories, per the corroborating read above, which is why the control half of the
  probe works at all.

This record is handed forward to plan 173-08 as the source for the POLICY-04 ledger rows.
References to `henols/firestarter_prom`, `henols/firestarter` and `henols/firestarter_app` in
this record and its evidence siblings will be invalidated by Backlog 999.9's rename sweep, which
is why every reference here is a mechanically greppable literal repository name rather than a
paraphrase.
