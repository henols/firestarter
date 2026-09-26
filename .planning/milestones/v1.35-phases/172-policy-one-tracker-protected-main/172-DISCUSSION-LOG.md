# Phase 172: POLICY — One Tracker, Protected `main` - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-09-01
**Phase:** 172-policy-one-tracker-protected-main
**Areas discussed:** Where the policy lives, Templates vs `dev test --submit`, Ruleset shape + bypass, LEGACY-01 guard or record

All four offered gray areas were selected.

---

## Where the policy lives

### Q1 — Canonical home for gh#9's guide text

| Option | Description | Selected |
|--------|-------------|----------|
| A `Contributing` wiki page | Matches WIKI-02; one copy, reachable from Home + `_Sidebar`, linkable from all three READMEs. Cost: GitHub's native contributing-guidelines affordance never fires, since GitHub reads CONTRIBUTING.md only from a repo. | ✓ |
| `CONTRIBUTING.md` in prom | GitHub-native on prom's New Issue and New PR pages. Cost: an in-repo documentation file, the shape WIKI-02 pushed everything out of; and PRs mostly happen in the sub-repos, where prom's copy is invisible. | |
| Expand prom's README section | The README already says two of the three things. Cost: it is 37 lines and deliberately a front door — Phase 169 kept it thin on purpose. | |

**User's choice:** A `Contributing` wiki page (recommended option).
**Notes:** gh#9 already contains the text in the operator's own words, so this is a relocation under activation decision 4, not new authoring.

### Q2 — Pointer files, given GitHub reads CONTRIBUTING.md only from the repo where a PR opens

| Option | Description | Selected |
|--------|-------------|----------|
| `.github/CONTRIBUTING.md` in all three | A few lines each pointing at the wiki page — a link, not a restatement, so "stated once" holds. Fires the New PR banner in whichever repo the contributor is filing in. Under `.github/`, keeping roots clear as Phase 171 left them. | ✓ |
| Root `CONTRIBUTING.md` in all three | Same files at each root; conventional and more discoverable when browsing. Cost: three new files at roots Phase 171 just finished clearing. | |
| No pointer files | Subtractive, consistent with Phase 171. Cost: a contributor opening a PR sees no banner — the one moment the routing rule is load-bearing. | |

**User's choice:** `.github/CONTRIBUTING.md` in all three (recommended option).

### Q3 — How much of the three README restatements gets trimmed

| Option | Description | Selected |
|--------|-------------|----------|
| Trim to a link; bullets → bug template | Each README keeps a one-line link and nothing more; the firmware README's four "Include:" bullets move into the bug-report template where a filer actually sees them. | ✓ |
| Leave all three READMEs as shipped | Phases 169/170 wrote these deliberately. Cost: "stated once" is met by argument rather than construction. | |
| Trim the sub-repos; keep prom's section | Prom is the front door, so summarising there is its job. Firmware bullets still move. | |

**User's choice:** Trim to a link; bullets → bug template (recommended option).

### Q4 — Security reporting, handed forward by Phase 171 D-02

| Option | Description | Selected |
|--------|-------------|----------|
| One honest sentence on the Contributing page | States the non-claim: no private disclosure channel exists, so security reports go on the public tracker. Commits to nothing; turns 171's silence into a stated non-claim. | ✓ |
| No sentence — silence stays | Exactly as Phase 171 left it, and accurate. Cost: a would-be reporter has no signal and hunts for a channel that does not exist. | |
| Turn on private vulnerability reporting | A one-call repo toggle giving a real private channel. Cost: commits the operator to monitoring and responding — the commitment 171 D-02 declined — and is outside POLICY-01…03. | |

**User's choice:** One honest sentence on the Contributing page (recommended option).

---

## Templates vs `dev test --submit`

### Q1 — Markdown templates or YAML issue forms

| Option | Description | Selected |
|--------|-------------|----------|
| Forms for bug + feature, Markdown for `dev test` | Required fields and dropdowns so a bug report cannot be filed without the versions that always have to be chased; `dev test` stays Markdown because its job is to hand over a command. | ✓ |
| YAML issue forms for all three | Uniform and validated. Cost: a form fights the `dev test` flow — a tester with a complete generated body has no field to paste it into. | |
| Markdown templates for all three | Simplest; matches how existing community issues were written. Cost: nothing is required, so `needs:report` keeps getting applied. | |

**User's choice:** Forms for bug + feature, Markdown for `dev test` (recommended option).
**Notes:** Prompted by the measured fact that prom carries a `needs:report` label and issue #21 is a `dev test` report wearing it.

### Q2 — What the hand-filled `dev test` template is for

| Option | Description | Selected |
|--------|-------------|----------|
| Route to the command | Body says to run `firestarter dev test <chip> --submit`; short fallback under a title marker deliberately **not** `[dev test]`, so triage never mistakes a hand-written report for a machine one. | ✓ |
| Mirror the machine body | Reproduce the title format and a fenced-JSON skeleton. Cost: humans get the JSON wrong, and a malformed block is worse than none — it looks parseable and is not. | |
| Route first, manual section below | Most complete. Cost: longest template, and still has to answer the marker question either way. | |

**User's choice:** Route to the command (recommended option).

### Q3 — `blank_issues_enabled`

| Option | Description | Selected |
|--------|-------------|----------|
| Leave blank issues enabled | Templates offered, not forced; `dev test --submit`'s browser tier keeps working as Phase 113 built it. The only option needing no product-code change, which the milestone scope note forbids here. | ✓ |
| Disable, and file the submit.py fix as backlog | Every human goes through a template from day one. Cost: the community fallback path is live-broken until a future milestone fixes the URL. | |
| Disable only if `?template=&body=` still prefills | Research-gated conditional. Cost: a planning dependency on an answer not yet in hand. | |

**User's choice:** Leave blank issues enabled (recommended option).
**Notes:** Driven by `firestarter_app/firestarter/submit.py:283`, whose browser tier builds `issues/new?title=&body=`; `blank_issues_enabled: false` redirects that to `/issues/new/choose` and drops the prefill.

### Q4 — How POLICY-02 actually becomes true, given templates are read from the default branch only

| Option | Description | Selected |
|--------|-------------|----------|
| PR the template files to `main` after enforcement | A small branch carrying only `.github/` files into `main` once the ruleset is active. Templates go live for real, and the merge doubles as the first live proof that PR-only `main` works. | ✓ |
| Push to `main` directly, before enforcement | Fewest moving parts, immediate effect. Cost: an off-branch commit and a hard ordering constraint. | |
| Milestone branch only; record the property | Phase 171's precedent. Cost: POLICY-02 satisfied by construction, not observation, possibly for a long time. | |

**User's choice:** PR the template files to `main` after enforcement (recommended option).
**Notes:** Prompted by the measurement that prom's `main` is 733 commits behind `beta`, and the milestone branch merges to `beta`.

### Q5 — Whether the sub-repo pointers get the same treatment

| Option | Description | Selected |
|--------|-------------|----------|
| All three repos get the same treatment | Three small `.github`-only PRs. The PR-open banner works in every repo where a contributor might file, and PR-only `main` is proven on all three. | ✓ |
| Prom only; sub-repos wait for the beta cut | Only prom's templates get a dedicated PR. Cost: the routing banner stays dark in exactly the two repos where PRs are opened. | |
| All three, but before enforcement | Direct pushes while still allowed. Cost: reverses the prior answer and gives up the free demonstration. | |

**User's choice:** All three repos get the same treatment (recommended option).
**Notes:** Measured alongside: `beta` is 531 ahead of `main` in `firestarter`, 781 ahead in `firestarter_app`.

---

## Ruleset shape + bypass

Opened with a finding that reshaped the area: both sub-repos auto-commit a version bump back onto `main` from CI (`firestarter_app/.github/workflows/release.yml:31`, and the guarded block below `firestarter/.github/workflows/build.yml`'s "PUBLISH BOUNDARY"), pushing as `github-actions[bot]` on the default `GITHUB_TOKEN` — which a repository-admin bypass would not cover.

### Q1 — Who bypasses

| Option | Description | Selected |
|--------|-------------|----------|
| GitHub Actions only | Sole bypass actor. Every human, operator included, goes through a PR, so "no direct push" is literally true of every person; the bot keeps the release path. The one bypass is narrow, named, and belongs to a robot. | ✓ |
| No bypass at all | Strictest reading of POLICY-03 and gh#6. Cost: the next stable release in either sub-repo fails at its auto-commit step, forcing release-workflow rework the scope note files rather than fixes. | |
| Actions + repository admin | Also keeps an emergency hatch. Cost: with one maintainer, an always-on admin bypass makes "no direct push" true of nobody — a ruleset claiming protection it does not provide. | |

**User's choice:** GitHub Actions only (recommended option).
**Notes:** Framed with the fact that an admin can always flip `enforcement` back to `disabled` via the API, so "no bypass" is never a lock-out.

### Q2 — What happens to `firestarter`'s existing ruleset 4998759

| Option | Description | Selected |
|--------|-------------|----------|
| One spec, PATCHed into fw, POSTed to the other two | Preserves fw's ruleset id and its 2025 history; three-way read-back equality apart from ids and timestamps. *(This was the recommended option and was not chosen.)* | |
| Delete fw's and create all three fresh | Three rulesets born from one call with nothing inherited. Cost: throws away the existing ruleset's identity and creation history, and a delete is the one irreversible step in an otherwise reversible phase. | ✓ |
| PATCH fw in place, keep its DeployKey bypass | Least disturbance. Cost: fw's bypass list would differ forever, so read-back could never be an equality check. | |

**User's choice:** Delete fw's and create all three fresh — the operator declined the recommendation.
**Notes:** Measured first: all three repos have **zero** deploy keys, so the existing `DeployKey` bypass grants nothing to anyone. CONTEXT.md D-10 records this as the phase's only `one-way` decision and requires capturing 4998759's full JSON into evidence before the DELETE.

### Q3 — gh#6's two extras

| Option | Description | Selected |
|--------|-------------|----------|
| POLICY-03's four clauses only | Exactly the requirement; gh#6's status-check and conversation-resolution bullets recorded as knowingly not implemented, for Phase 173's ledger to state as non-claims. | ✓ |
| Add conversation resolution too | A one-field addition that cannot deadlock anything. Cost: outside POLICY-03, and changes nothing for a single maintainer. | |
| Both extras, with status checks pinned per repo | Closes gh#6 fully. Cost: a wrongly pinned check name deadlocks `main` behind a check that will never report. | |

**User's choice:** POLICY-03's four clauses only (recommended option).
**Notes:** Prom has only `catalog-sync-check.yml` registered with Actions, which is what makes status-check pinning hazardous there.

### Q4 — Sequencing

| Option | Description | Selected |
|--------|-------------|----------|
| Rulesets last, all three at once, then the PRs | Everything else lands on the milestone branch first, so no step in the phase ever needs a direct push and there is no lock-out window. | ✓ |
| Prom first as a canary, then fw + app | Cost: two extra rounds for a canary that cannot test the risky part — the bot bypass is untouched by a `.github`-only merge in any repo. | |
| Rulesets first, everything else after | Protection on from the start. Cost: fixing a wrong ruleset would itself be behind the ruleset. | |

**User's choice:** Rulesets last, all three at once, then the PRs (recommended option).
**Notes:** Raised before the question and accepted: the Actions bypass **cannot be demonstrated in this phase** — nothing pushes to `main` from CI until a stable release, and `release.yml`'s `paths-ignore` includes `.github/**`, so the chosen PRs will not exercise it.

*The workflow's end-of-area continuation prompt was declined by the operator, who instructed the discussion to continue directly to the final area.*

---

## LEGACY-01: guard or record

Opened with a re-measurement: zero dead-tracker links in any live artifact; all 21 grep hits sit inside `.planning/`, which REQUIREMENTS.md puts out of scope as historical-by-intent. LEGACY-01 is already true, made so by Phases 168 and 170.

### Q1 — Guard, or recorded measurement

| Option | Description | Selected |
|--------|-------------|----------|
| A grep leg in `wiki-check.yml` | That job already checks out meta, both sub-repos and a wiki clone, so one leg covers every surface with no new tooling — and it is the only option covering the wiki, now edited with no PR or review. | ✓ |
| A rule in `tools/wiki/wiki.py links` | Fires at the moment a bad link is introduced. Cost: `links` takes one `--source-dir`, so the three READMEs stay unguarded. | |
| Record the measurement, no guard | Phase 171's precedent for a criterion that prevents rather than remediates. Cost: nothing stops the six links returning. | |

**User's choice:** A grep leg in `wiki-check.yml` (recommended option).

### Q2 — Whether the prom PR also carries the workflow

| Option | Description | Selected |
|--------|-------------|----------|
| Yes — and demonstrate the leg failing first | Guard live from merge; plant a bad link, watch RED, remove it, watch GREEN — the bar REQUIREMENTS.md set for HONEST-02. Verify the three existing legs pass locally first. | ✓ |
| Yes — carry it as-is | Simpler. Cost: an unproven guard registered as a live gate is the false-PASS shape the honesty constraint exists to catch. | |
| No — keep the PR minimal | Smallest change to the default branch. Cost: the guard is inert, and HONEST-02 and WIKI-05's checks stay dark too. | |

**User's choice:** Yes — and demonstrate the leg failing first (recommended option).
**Notes:** `wiki-check.yml` returns 404 on prom's `main`; `catalog-sync-check.yml` is the only registered workflow. Registering it brings HONEST-02's and WIKI-05's checks to life for the first time — both shipped inert in Phase 168.

### Q3 — What the leg asserts

| Option | Description | Selected |
|--------|-------------|----------|
| Strict — everywhere outside `.planning/` | One pattern over all three checkouts plus the wiki clone, excluding only `.planning/` and `.git/`. Catches a dead link in a Click docstring, which is user-facing `--help` text. Zero hits today, nothing to grandfather. | ✓ |
| Documentation surfaces only | Narrower, no false positives from test fixtures. Cost: a dead link in a docstring or help string goes uncaught. | |
| Strict, plus an allowlist file | Same coverage with an escape hatch. Cost: machinery for a problem that does not exist, and an allowlist can silently swallow a real regression. | |

**User's choice:** Strict — everywhere outside `.planning/` (recommended option).

---

## Claude's Discretion

Recorded in CONTEXT.md `<decisions>` → "Claude's Discretion":

- Exact prose of the `Contributing` page, provided gh#9's three statements and its cross-repository-change protocol are relocated intact, plus the security sentence.
- Field lists, dropdown options and `validations: required` choices in the two issue forms.
- Which labels each template pre-applies, from prom's existing label set.
- Whether `config.yml` also carries `contact_links`.
- The title marker for the hand-filled `dev test` fallback, provided it is not `[dev test]`.
- Ruleset naming, `~DEFAULT_BRANCH` vs literal `main`, and `required_approving_review_count: 0` — all following the measured incumbent.
- Commit granularity, subject to the atomic-commit convention.

## Deferred Ideas

- Required status checks on `main` (gh#6) — declined by D-11.
- Required review-thread resolution (gh#6) — declined by D-11.
- GitHub private vulnerability reporting — declined by D-04 and Phase 171 D-02.
- A `henols/.github` default community-health repository — would replace the three pointer files.
- `MIGRATION-TABLE.md` lists two pages that no longer exist (`Protocol-Flags`, `Protocol-ID`) — carried forward from Phase 171, still unfixed.
- Backlog 999.9's rename sweep will invalidate this phase's links; the roadmap names 169, 170 and 172 as needing re-sweeping.

### Reviewed Todos (not folded)

`todo.match-phase 172` returned 36 todos, 35 matched, topping out at 0.9 — all on generic keywords, none on subject. **None folded.** Two were read closely before being set aside: *"Add a `dev test` flag that files the issue automatically when the run finishes"* and *"Report the chip's exact database name in `dev test` issues, artifacts, and tests"* — both brush this phase's surface but are product-code changes to `submit.py`, which the milestone scope note excludes.
