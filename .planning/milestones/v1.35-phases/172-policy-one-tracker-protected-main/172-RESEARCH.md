# Phase 172: POLICY — One Tracker, Protected `main` - Research

**Researched:** 2026-09-01
**Domain:** GitHub repository configuration (rulesets, issue templates, community-health files), CI guard authoring, wiki authoring
**Confidence:** MEDIUM-HIGH — every in-repo and live-API fact was measured this session; two GitHub *behavioural* questions (D-07 prefill, D-09 Actions bypass) could not be settled from documentation and are flagged as `[ASSUMED]`

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

Copied verbatim from `172-CONTEXT.md` `## Implementation Decisions`. Rationale for each is in that file; do not re-litigate.

- **D-01: the canonical policy text is a new `Contributing` wiki page.**
- **D-02: `.github/CONTRIBUTING.md` in all three repositories, as pointers.**
- **D-03: all three README tracker sections trim to a single link; the firmware README's four "Include:" bullets move into the bug-report issue template.**
- **D-04: one honest sentence about security reporting goes on the `Contributing` page.**
- **D-05: YAML issue forms for bug report and feature request; a Markdown template for `dev test`.**
- **D-06: the `dev test` template routes to the CLI, and must NOT use the `[dev test]` title marker.**
- **D-07: `blank_issues_enabled` stays TRUE.**
- **D-08: the `.github/` files reach `main` by pull request, in all three repositories, after the rulesets are active.**
- **D-09: GitHub Actions is the sole bypass actor** — `actor_type: "Integration"`, `actor_id: 15368` (resolved from `/apps/github-actions`, not guessed), `bypass_mode: "always"`.
- **D-10: `firestarter`'s existing ruleset `4998759` is DELETED, and all three rulesets are created fresh from one identical body.**
- **D-11: POLICY-03's four clauses only — PR required, no direct push, no force-push, no deletion.**
- **D-12: rulesets are created LAST, all three at once, and only then the three `.github` PRs.**
- **D-13: LEGACY-01 gets a mechanical guard — a grep leg in `.github/workflows/wiki-check.yml`.**
- **D-14: the prom pull request carries `wiki-check.yml` as well, and the new leg is demonstrated failing before it goes in.**
- **D-15: the grep is strict — everywhere outside `.planning/`.**

**Reversibility flags carried with the decisions:** D-06 costly; D-08 costly; D-10 **one-way** (capture ruleset `4998759`'s full JSON into evidence before the DELETE); D-14 costly.

### Mechanical constraints — recorded, not asked

- **NO COMMENTS.** Zero comments in anything written for this project; a plan cannot override it. Binds the new `wiki-check.yml` grep leg, the YAML issue forms, `config.yml` and the `.github/CONTRIBUTING.md` files — **even though the surrounding `wiki-check.yml` is dense with comments written by earlier phases.** Do not match the local style here; match the rule.
- **The wiki is reached by clone-commit-push** (`https://github.com/henols/firestarter_prom.wiki.git`). No in-repo `wiki/` source tree, no publish script, no PR, no CI gate on the edit.
- **A new wiki page owes two navigation edits or CI goes red** — `Contributing` in `_Sidebar.md` **and** linked from `Home.md` in the same push.
- **Page naming:** `Title-Case-With-Hyphens.md`, flat, no subdirectories.
- **Page opening:** logo `<p align="left">` block, then `---`, then `# Title`.
- **`Contributing` owes a `MIGRATION-TABLE.md` row** if the table's conventions apply to an authored page.
- **Sub-repo changes land inside the submodule on `gsd/v1.35-documentation-consolidation-wiki-migration`;** meta changes on the same-named branch here. Re-pin both gitlinks before the phase closes.
- **Read the ruleset back from the API, never from the settings page.**

### Claude's Discretion

- Exact prose of the `Contributing` page, provided it carries gh#9's three statements and its cross-repository-change protocol relocated intact, plus D-04's security sentence.
- Exact field lists, dropdown options and `validations: required` choices in the two issue forms.
- Which labels each template pre-applies, drawn from the labels prom already carries (`bug`, `enhancement`, `feature`, `dev-test`, `needs:report`).
- Whether `config.yml` also carries `contact_links` (e.g. to the wiki), given `blank_issues_enabled` stays true.
- The title marker chosen for D-06's hand-filled fallback, provided it is not `[dev test]`.
- Ruleset naming, `~DEFAULT_BRANCH` vs a literal `main`, and `required_approving_review_count: 0` — all follow the measured incumbent.
- Whether the deletions, the wiki push and the ruleset calls land as one commit or several.

### Deferred Ideas (OUT OF SCOPE)

- Required status checks on `main` (gh#6) — declined by D-11.
- Required review-thread resolution (gh#6) — declined by D-11.
- GitHub private vulnerability reporting — declined by D-04 and Phase 171 D-02.
- A `henols/.github` default community-health repository.
- `MIGRATION-TABLE.md` lists two pages that no longer exist (`Protocol-Flags`, `Protocol-ID`) — carried forward, still unfixed.
- Backlog 999.9's rename sweep will invalidate this phase's links — accepted at activation.
- Product code: `firestarter_app/firestarter/submit.py` is not edited. `.planning/` is not swept. gh#9's own disposition belongs to Phase 173.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| POLICY-01 | Documentation states plainly that `firestarter_prom` is the only issue tracker, that the sub-repos have Issues disabled, and that PRs go to the repository containing the changed code | gh#9's full text captured verbatim below (the relocation source, D-01); community-health file placement and precedence confirmed (`.github` > root > `docs`); three README sections located with exact line ranges for the D-03 trim |
| POLICY-02 | `firestarter_prom` offers issue templates covering a bug report, a feature request, and a `dev test` chip-validation report | Issue-form YAML schema confirmed against GitHub docs; `.md` + `.yml` coexistence confirmed; `config.yml` keys confirmed; an offline validator (`check-jsonschema --builtin-schema vendor.github-issue-forms`) proven to accept a valid form and reject a bad `type` |
| POLICY-03 | `main` in all three repos behind an `enforcement: active` ruleset — PR required, no direct push, no force-push, no deletion, read back from the API | Exact `POST` body, the read-back normalizer, and a three-way equality recipe below; live pre-state re-measured this session; the `Integration`/15368 bypass carries an unresolved behavioural risk (Pitfall 3) |
| LEGACY-01 | No documentation page sends a reader to `henols/firestarter/issues` or `henols/firestarter_app/issues` | Grep leg authored and proven three ways this session: green today, RED on a planted link, and no false positive on `henols/firestarter_prom/issues` |
</phase_requirements>

## Project Constraints (from CLAUDE.md)

`/workspaces/CLAUDE.md` is a repository-orientation file rather than a rulebook; the actionable directives it carries and that bind this phase are:

- **Documentation lives only in the `firestarter_prom` GitHub wiki — there is no in-repo copy.** `tools/wiki/` holds the checkers that run against a clone of that wiki. `[VERIFIED: /workspaces/CLAUDE.md:12]`
- **The meta repo tracks `.planning/`, `.claude/`, `tools/` and `.github/`; neither sub-repo is committed here.** Sub-repo edits are made inside the submodule working tree. `[VERIFIED: /workspaces/CLAUDE.md:12]`
- **Serial-protocol constants and flag bits are duplicated across the two sub-repos and must change together** — not touched by this phase (no product code), but it is why "config only" must stay config only. `[VERIFIED: /workspaces/CLAUDE.md:45-46]`

The operator's standing **no-comments** rule (global memory, restated in CONTEXT.md's mechanical constraints) is the binding style directive for every file this phase writes.

## Summary

This phase is almost entirely *configuration* — three GitHub rulesets, one wiki page, one issue-template directory, three pointer files, three README trims and one CI leg — and its research risk is not "which library" but "which GitHub behaviours can actually be relied on". Three of the ten questions the orchestrator posed resolved to hard, measured answers this session; two resolved to *blocking defects in existing tooling* that the phase must fix before it can do what D-14 asks; and two could not be settled from documentation and must be carried as assumptions with a proposed falsification.

The two blocking defects both live in `.github/workflows/wiki-check.yml`, the workflow D-13 wants to extend and D-14 wants to register. **First: the dispatch-mirror step passes `--wiki-dir wiki-clone` to a script that does not accept it** — `dispatch_mirror.py` declares exactly two arguments — so that step exits 2 unconditionally, on every branch, forever. **Second: the resolver step lands both sub-repos on `main`, not on `beta` as its own comment claims**, because the scheduled run's `github.ref_name` is `main` and `main` exists in both sub-repos; and against main-era trees the other two legs also fail (`firestarter_app@main` has no `firestarter/data/chip_database.json` at all — it still ships `database_generated.json`; `firestarter@main` has no `PROTOCOLS.md`). Against `beta` all three legs pass, which was measured directly. D-14's precondition ("verify the workflow's three existing legs pass locally first") is therefore *not* satisfied today, and registering the workflow unchanged would produce a red run on its first schedule.

The remaining findings are mostly good news. The LEGACY-01 grep leg was authored and proven green/red/no-false-positive against the real four-directory layout. An authored `MIGRATION-TABLE.md` row using the em-dash `—` in the SHA column provably leaves `parse_migration_table` returning the same 8 rows, so Phase 171's count assertion survives. Issue forms can be validated offline before they ever reach GitHub. The ruleset `POST` body and a volatile-field-stripping read-back comparison are both worked out and the normalizer was exercised against the live incumbent. Two things stay unproven: whether `/issues/new?title=&body=` still prefills once templates exist (D-07's premise) and whether the default `GITHUB_TOKEN` is covered by an `Integration`/15368 bypass (D-09's premise). The second is the more consequential: if it is wrong, the next stable release in *both* sub-repos breaks.

**Primary recommendation:** plan the phase in D-12's order but insert two prerequisites — fix `wiki-check.yml`'s two defects (drop `--wiki-dir`, make the resolver actually land on `beta`) before adding the grep leg, and create **prom's** ruleset first as a canary so the `Integration` bypass is proven acceptable to the API *before* the one-way DELETE of `4998759`.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Canonical policy prose | Wiki repository (`firestarter_prom.wiki.git`) | — | D-01; the wiki is the project's documentation home and the only place a statement can be made once |
| Native contribution affordance at PR time | Repository (`.github/CONTRIBUTING.md` per repo) | Wiki (link target) | GitHub reads CONTRIBUTING.md only from the repo where the PR is opened `[CITED: docs.github.com/communities/…/creating-a-default-community-health-file]` |
| Structured issue intake | Repository (`firestarter_prom/.github/ISSUE_TEMPLATE/`) | — | Templates are a per-repository, default-branch surface `[CITED: docs.github.com/…/about-issue-and-pull-request-templates]` |
| Branch protection | GitHub control plane (repository rulesets, REST API) | — | Not expressible in the repository tree at all; only the API is authoritative |
| Dead-link enforcement | Meta CI (`.github/workflows/wiki-check.yml`) | — | D-13; it is the only job with all three checkouts plus the wiki clone on one disk |
| Front-door pointers | Three READMEs | Wiki | D-03; each README links, none restates |
| Provenance of the new page | `.planning/v1.35/MIGRATION-TABLE.md` | — | Phase 171 D-06; the Backlog 999.9 rename sweep greps this table |

## Standard Stack

### Core

| Tool | Version | Purpose | Why Standard |
|------|---------|---------|--------------|
| `gh` (GitHub CLI) | 2.98.0 | Ruleset create/read/delete, PR creation, label and issue reads | Already installed and authenticated as `henols` with `admin: true` on all three repos `[VERIFIED: gh auth status, gh api /repos/henols/* --jq .permissions.admin, this session]` |
| `jq` | present | Normalising ruleset read-backs for three-way equality | Only practical way to strip volatile fields and canonicalise key order |
| `git` | present | Wiki clone-commit-push; sub-repo branch work | The wiki has no API `[VERIFIED: .planning/REQUIREMENTS.md:111-116]` |
| `grep` (GNU) | present | The LEGACY-01 leg | D-13; runs on the runner with no install |
| `python3` 3.11 via `uv venv --python 3.11` | uv present | Running `tools/wiki/*.py` checkers the way CI will | Devcontainer 3.12 masks app CI `[VERIFIED: memory reference_devcontainer_py312_masks_ci_py39; uv venv --python 3.11 succeeded this session]` |

### Supporting

| Tool | Version | Purpose | When to Use |
|------|---------|---------|-------------|
| `check-jsonschema` | 0.38.0 | Offline validation of issue forms and `config.yml` against the SchemaStore GitHub schemas | Before every push of a `.github/ISSUE_TEMPLATE/*.yml`; see Pitfall 7 and the audit below |
| `uv` | present | Ephemeral 3.11 venvs; `uv run --with check-jsonschema` avoids adding any project dependency | Local checks only — nothing in CI needs it |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `check-jsonschema --builtin-schema vendor.github-issue-forms` | `curl https://www.schemastore.org/github-issue-forms.json` + a `jsonschema` script | Same schema, more moving parts, needs the network; the builtin ships the schema offline |
| `check-jsonschema` at all | An inline Python assertion of required keys and the `type` enum | Weaker (misses `additionalProperties: false`, per-type attribute rules) but zero install; the honest fallback if the SUS verdict below is judged disqualifying |
| `gh api` | `curl` with a PAT | `gh` already holds the token, handles the API version header, and `--input -` takes a JSON body from stdin `[VERIFIED: gh help api — "The file to use as body for the HTTP request (use \"-\" to read from standard input)"]` |
| A grep leg in CI | A rule inside `tools/wiki/wiki.py links` | Rejected by D-13 — `wiki.py` takes a single `--source-dir` and would see only the wiki clone |

**Installation (local checks only):**

```bash
uv venv --python 3.11 /tmp/v311 && VIRTUAL_ENV=/tmp/v311 uv pip install check-jsonschema
```

**Version verification:** `python3 -m pip index versions check-jsonschema` → `check-jsonschema (0.38.0)`, 95 released versions from 0.1.0 to 0.38.0 `[VERIFIED: pip index versions, this session]`.

## Package Legitimacy Audit

Only one external package is recommended, and only for a *local* pre-push check. Nothing this phase ships installs anything — the CI leg is `grep`, and the runner already has `python3` and `git`.

| Package | Registry | Age | Downloads | Source Repo | Verdict | Disposition |
|---------|----------|-----|-----------|-------------|---------|-------------|
| `check-jsonschema` | PyPI | latest release 2026-08-09; 95 versions on the index, earliest `0.1.0` | seam reports `null` (unknown) | `https://github.com/python-jsonschema/check-jsonschema` | **SUS** (`too-new`, `unknown-downloads`) | Flagged — planner must add a `checkpoint:human-verify` before installing, or take the zero-install fallback |

Raw seam output `[VERIFIED: gsd-tools query package-legitimacy check --ecosystem pypi check-jsonschema, this session]`:

```json
{ "name": "check-jsonschema", "verdict": "SUS",
  "signals": { "exists": true, "publishedAt": "2026-08-09T04:31:05.412695Z", "weeklyDownloads": null,
               "repoUrl": "https://github.com/python-jsonschema/check-jsonschema", "deprecated": false,
               "postinstall": null, "ecosystem": "pypi" },
  "reasons": ["too-new", "unknown-downloads"] }
```

`check-jsonschema` [WARNING: flagged as suspicious — verify before using.] The `too-new` signal is keyed on the *latest release date*, not on first publication, and the index shows a long release history under the `python-jsonschema` organisation — but the verdict is the verdict and is not overridden here. The planner has two compliant routes: (a) a `checkpoint:human-verify` task before the install, or (b) drop the package and use the inline-assertion fallback in "Alternatives Considered", which costs schema depth but installs nothing.

**Packages removed due to [SLOP] verdict:** none.
**Packages flagged as suspicious [SUS]:** `check-jsonschema`.

## Architecture Patterns

### System Architecture Diagram

```
                     ┌──────────────────────── the policy statement ────────────────────────┐
   gh#9 issue text ──▶ Contributing.md ──push──▶ firestarter_prom.wiki.git
   (operator's own      + _Sidebar.md row              │
    words, D-01)        + Home.md link                 │  wiki.py links (pre-push, local)
                                                       ▼
                                            ┌─── linked from, never restated ───┐
                                            │                                   │
   README.md (prom, 37 ln) ─────trim D-03───┤                                   │
   firestarter/README.md:73-81 ─trim D-03───┤                                   │
   firestarter_app/README.md:104-108 ─D-03──┤                                   │
                                            │                                   │
   .github/CONTRIBUTING.md × 3 ─pointer D-02┘                                   │
              │                                                                 │
              │  (each file is authored on gsd/v1.35-…, then cherry-picked      │
              │   onto a fresh branch cut from that repo's main)                │
              ▼                                                                 │
   ┌──── three pull requests, base = main ────┐                                 │
   │  prom   : .github/CONTRIBUTING.md        │                                 │
   │           .github/ISSUE_TEMPLATE/*       │◀── POLICY-02 becomes observable │
   │           .github/workflows/wiki-check.yml │◀─ D-14: guard goes live       │
   │  firestarter     : .github/CONTRIBUTING.md │                               │
   │  firestarter_app : .github/CONTRIBUTING.md │                               │
   └────────────────┬─────────────────────────┘                                 │
                    │ merge (allowed: PR route)                                 │
                    ▼                                                           │
   ┌──── GitHub control plane ────────────────────────────────┐                 │
   │  DELETE /repos/henols/firestarter/rulesets/4998759       │                 │
   │  POST   /repos/{owner}/{repo}/rulesets  × 3, one body    │                 │
   │  GET    × 3 → normalise → three-way equality             │                 │
   │  bypass: Integration/15368 only (no person can push)     │                 │
   └──────────────────────────────────────────────────────────┘                 │
                                                                                │
   weekly cron ─▶ .github/workflows/wiki-check.yml ──────────────────────────────┘
                    ├── checkout meta, firestarter, firestarter_app
                    ├── clone wiki
                    ├── wiki.py links            (WIKI-05, inert until now)
                    ├── honest02_truth.py        (HONEST-02, inert until now)
                    ├── dispatch_mirror.py       (BROKEN today — see Pitfall 1)
                    └── grep leg                 (LEGACY-01, new — D-13)
```

### Recommended Order of Work

Follows D-12 (rulesets last) with two prerequisites inserted from this session's findings.

```
Wave A  wiki page + navigation + MIGRATION-TABLE row      (no main access needed)
Wave A  three README trims                                 (milestone branches)
Wave A  three .github/CONTRIBUTING.md pointers             (milestone branches)
Wave A  prom .github/ISSUE_TEMPLATE/{bug,feature,dev-test,config}
Wave B  FIX wiki-check.yml: drop --wiki-dir; fix the ref resolver
Wave B  ADD the LEGACY-01 grep leg; demonstrate RED then GREEN
Wave C  capture ruleset 4998759 JSON to evidence
Wave C  POST prom ruleset FIRST (canary: proves Integration/15368 is accepted)
Wave C  DELETE 4998759; POST firestarter + firestarter_app from the same body
Wave C  GET × 3, normalise, assert three-way equality + enforcement=active
Wave D  cut three branches from each repo's main; cherry-pick the .github files
Wave D  open three PRs; check the PR's own check list before merging (Pitfall 5)
Wave D  merge; re-pin both gitlinks
```

### Pattern 1: Ruleset creation from one canonical body

**What:** a single JSON file is the source for all three `POST`s, so a three-way read-back equality is meaningful.
**When to use:** D-10 requires it.

```bash
cat > /tmp/ruleset.json <<'JSON'
{
  "name": "Protect main",
  "target": "branch",
  "enforcement": "active",
  "conditions": { "ref_name": { "include": ["~DEFAULT_BRANCH"], "exclude": [] } },
  "rules": [
    { "type": "deletion" },
    { "type": "non_fast_forward" },
    { "type": "pull_request",
      "parameters": {
        "required_approving_review_count": 0,
        "dismiss_stale_reviews_on_push": false,
        "require_code_owner_review": false,
        "require_last_push_approval": false,
        "required_review_thread_resolution": false,
        "allowed_merge_methods": ["merge", "squash", "rebase"]
      } }
  ],
  "bypass_actors": [
    { "actor_id": 15368, "actor_type": "Integration", "bypass_mode": "always" }
  ]
}
JSON
gh api --method POST /repos/henols/firestarter_prom/rulesets --input /tmp/ruleset.json
```

Field-by-field justification:

- `enforcement` ∈ `disabled | active | evaluate`; `target` ∈ `branch | tag | push` (default `branch`) `[CITED: docs.github.com/en/rest/repos/rules]`
- `bypass_actors[].actor_type` ∈ `Integration | OrganizationAdmin | RepositoryRole | Team | DeployKey | User`; `actor_id` is required for `Integration`; `bypass_mode` ∈ `always | pull_request | exempt`, default `always` `[CITED: docs.github.com/en/rest/repos/rules]`
- `actor_id: 15368` — re-resolved this session, not guessed: `gh api /apps/github-actions --jq '{id,slug}'` → `{"id":15368,"slug":"github-actions"}` `[VERIFIED: gh api /apps/github-actions, this session]`
- GitHub Apps are explicitly eligible bypass actors; the docs list "GitHub Apps" among the entities that can be granted bypass, and describe the two modes as "Always allow" and "For pull requests only" `[CITED: docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/creating-rulesets-for-a-repository]`. The same page says **nothing** about user-owned versus organization repositories, so "`Integration` is valid on a personal repo" is `[ASSUMED]` — hence the prom-first canary.
- **Two fields are deliberately omitted** from the body even though the incumbent returns them: `required_reviewers: []` and `require_extra_approval_for_unattributed_changes: true`. Neither appears in the documented `pull_request` parameter list `[CITED: docs.github.com/en/rest/repos/rules]`; omitting them lets GitHub apply its own defaults, and because all three rulesets are born from one body the defaults land identically — which is exactly what the three-way equality asserts. `require_extra_approval_for_unattributed_changes` exists to demand one extra approval on unattributed Copilot pull requests and is on by default for new and existing rulesets `[CITED: docs.github.com/en/repositories/…/managing-rulesets/available-rules-for-rulesets, via search]`; human-authored PRs are unaffected.

### Pattern 2: Read-back normalisation for a three-way equality

**What:** strip everything that cannot be equal across three repositories, canonicalise ordering, then `diff`.
**Volatile / per-repo fields that MUST be excluded:** `id`, `node_id`, `created_at`, `updated_at`, `_links`, `source` (it is the `owner/repo` string). `current_user_can_bypass` is expected to be `"never"` for all three but is a *derived* field, not part of the body — exclude it from the equality and assert it separately.

```bash
norm() { jq -S 'del(.id,.node_id,.created_at,.updated_at,._links,.source,.current_user_can_bypass)
                | .rules |= sort_by(.type)
                | .bypass_actors |= sort_by(.actor_type, (.actor_id // 0))' ; }
```

Exercised this session against the live incumbent: `gh api /repos/henols/firestarter/rulesets/4998759 | jq 'del(...)' | jq -S -c .` produced a stable canonical object whose sha256 is `6ddac2877fb509df98694af41392ae70a3bd4a966fd9952f0eeaf9e8e216c6aa` `[VERIFIED: run this session]`. `source_type` (`"Repository"`) is identical across repos and stays in the comparison.

### Pattern 3: The LEGACY-01 grep leg (D-13/D-15)

Authored to run after "Clone the live wiki", over the four directories that job already has on disk. **No comments**, per the standing rule, even though the surrounding file is comment-dense.

```yaml
      - name: LEGACY-01 dead tracker link check
        run: |
          if grep -rInE 'henols/firestarter(_app)?/issues' meta firestarter firestarter_app wiki-clone --exclude-dir=.git --exclude-dir=.planning; then
            echo "FAIL: a page links to an issue tracker that is disabled"
            exit 1
          fi
          echo "OK: no page links to henols/firestarter/issues or henols/firestarter_app/issues"
```

Three properties, each proven this session against the real trees (`meta` = `/workspaces`, plus both sub-repo working trees and a fresh wiki clone) `[VERIFIED: run this session]`:

1. **Green today** — the `if` does not fire; zero hits outside `.planning/`.
2. **Reaches the files** — dropping `--exclude-dir=.planning` yields 24 matching lines, every one of them under a `.planning/` path (`meta/.planning/REQUIREMENTS.md`, `…/ROADMAP.md`, `…/phases/113-submission-flow/*`, `…/phases/172-…/172-CONTEXT.md`, and others). The leg is not vacuous.
3. **No false positive on the live tracker** — a planted `https://github.com/henols/firestarter_prom/issues` does **not** match, while a planted `henols/firestarter/issues` and a planted `henols/firestarter_app/issues` both do. The anchor that makes this work is the `/` immediately after the alternation: in `henols/firestarter_prom/issues` the character following `henols/firestarter` is `_`, so neither branch of `(_app)?` can be followed by `/issues`.

Do **not** write this as `! grep …` followed by an `echo`: under the runner's `bash -e`, a command whose status is inverted with `!` does not trigger the errexit, and the trailing `echo` would then set the step's exit status to 0 — the leg would report success on a real hit. The explicit `if … exit 1` form has no such hole.

`-I` skips binary files; `-n` gives the reviewer a line number in the failure output.

### Pattern 4: Verify-command house style

Phase 171's plans use a single-line `&&`-chained shell command that writes an evidence file under `${PHASE_DIR}/evidence/` and then asserts on it — for example `171-02-PLAN.md:342-343`. Match that. Two hard rules:

- **Literal `&&`** inside `<automated>`, never `&amp;&amp;` — that defect has previously made 30 of 37 legs unrunnable in this project.
- Evidence path pattern: `/workspaces/.planning/phases/172-policy-one-tracker-protected-main/evidence/172-NN-<slug>.txt`.

### Anti-Patterns to Avoid

- **Asserting a ruleset merely exists.** The roadmap names this trap and the incumbent is the proof: `henols/firestarter` has had a ruleset called `Protect main` since 2025-04-22 with `"enforcement": "disabled"`. Every assertion must read `enforcement` and the rule set, not the name.
- **Branching the `.github` PRs off the milestone branch.** See Pitfall 4 — it would drag the entire unreleased milestone into `main`.
- **Copying the surrounding comment style into `wiki-check.yml`.** The no-comments rule binds what this phase writes.
- **Treating the settings page as evidence.** Only `gh api` output goes in evidence.
- **Adding a required status check "while we are in there".** D-11 declines it; prom has exactly one registered workflow and pinning a name that never reports deadlocks `main`.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Validating an issue form before it reaches GitHub | A hand-written key checker | `check-jsonschema --builtin-schema vendor.github-issue-forms` | The SchemaStore schema is `additionalProperties: false` and enumerates the `type` values; a hand-rolled check will not catch a misplaced attribute |
| Comparing three rulesets | Eyeballing three JSON blobs, or a naive `diff` of raw responses | `jq -S 'del(volatile) \| sort_by' \| diff` | Raw responses differ in `id`, `node_id`, timestamps, `_links` and `source`; a naive diff is always non-empty and therefore always ignored |
| Checking the wiki page is reachable | A bespoke link scan | `python3 tools/wiki/wiki.py links --source-dir wiki-clone` | Already does orphan detection, sidebar completeness, internal-link form and filename legality; ran green on the live wiki this session |
| Proving the pre-migration text of a page | Re-deriving from history | `MIGRATION-TABLE.md` + `honest01_claims.py` | The table is the project's provenance oracle and the Backlog 999.9 sweep's input |
| Detecting dead tracker links | A markdown-aware parser | `grep -rInE` over the four checkouts | D-15 explicitly wants non-markdown surfaces covered (a Click docstring is user-facing `--help` text) |

**Key insight:** every capability this phase needs already exists in the repo or in `gh`; the risk is not missing tooling, it is *broken* tooling that has never been run (Pitfalls 1 and 2).

## Runtime State Inventory

This is a configuration phase — the "runtime state" is GitHub's control plane and a third git repository, none of which follows from a file edit.

| Category | Items Found | Action Required |
|----------|-------------|------------------|
| Stored data | None in any datastore. No database, no cache, no chip database change. Verified by scope: no product code is touched. | none |
| Live service config | **Three rulesets** (prom `[]`, `firestarter_app` `[]`, `firestarter` one — id `4998759`, `enforcement: "disabled"`) `[VERIFIED: gh api /repos/henols/*/rulesets, this session]`. **The wiki repository** — 10 pages plus `_Sidebar.md`, edited only by clone-commit-push, no CI on the edit `[VERIFIED: fresh clone this session — Breaking-Changes, Chip-Database-Fields, Home, Install-Beta, Lockable-PROMs, Pin-Maps, Programming-Protocols, Shell-Completion, Shield-Revisions, Testing-Chips, _Sidebar.md]`. **Registered Actions workflows:** prom has `catalog-sync-check.yml` and `wiki-check.yml` in the working tree, but only the former is on the default branch. | API create/delete ×3; wiki push; one PR to register the workflow |
| OS-registered state | None. Nothing in this phase registers a task, service or daemon. | none |
| Secrets/env vars | None created or renamed. Two existing secrets are *relevant but untouched*: `secrets.PERSONAL_ACCESS_TOKEN` (used by `firestarter_app/.github/workflows/release.yml:43` and `beta-release.yml:112` for the release upload) and the default `GITHUB_TOKEN` (used by `firestarter/.github/workflows/beta-build.yml:411` and, implicitly, by both `stefanzweifel/git-auto-commit-action` steps whose `env: GITHUB_TOKEN: ${{ secrets.PERSONAL_ACCESS_TOKEN }}` lines are **commented out**) `[VERIFIED: grep over both sub-repos' workflows, this session]`. Which of these two identities performs the version-bump push is the whole of Pitfall 3. | none — but the ruleset must not assume the wrong identity |
| Build artifacts | None. No package is rebuilt; no sdist, no `.hex`. The one risk is the *accidental* production of a build artifact — a spurious stable firmware release if the `.github` merge triggers `build.yml` (Pitfall 5). | prevent, do not remediate |

**Nothing found in category:** stored data, OS-registered state and build artifacts are all "None — verified by scope; this phase writes no product code and runs no build."

## Common Pitfalls

### Pitfall 1: `wiki-check.yml`'s dispatch-mirror step cannot pass — it passes an argument the script rejects

**What goes wrong:** the step fails with exit code 2 on every run, on every branch, forever. D-14's precondition ("verify the workflow's three existing legs pass locally first, so registration does not immediately produce a red weekly run") is unmet today.

**The evidence.** The workflow step, verbatim `[VERIFIED: /workspaces/.github/workflows/wiki-check.yml:102-108]`:

```yaml
      - name: Dispatch-mirror check
        run: |
          python3 meta/tools/wiki/dispatch_mirror.py \
            --wiki-dir wiki-clone \
            --app-dir firestarter_app \
            --fw-dir firestarter
          echo "OK: the wiki's dispatch table still mirrors the host tool and the firmware test"
```

The script's entire argument surface, verbatim `[VERIFIED: /workspaces/tools/wiki/dispatch_mirror.py:157-158]`:

```python
    parser.add_argument("--app-dir", type=Path, required=True, default=None)
    parser.add_argument("--fw-dir", type=Path, required=True, default=None)
```

Run this session with the workflow's exact arguments:

```
usage: dispatch_mirror.py [-h] --app-dir APP_DIR --fw-dir FW_DIR
dispatch_mirror.py: error: unrecognized arguments: --wiki-dir wiki-clone
rc3=2
```

Run without `--wiki-dir` against the milestone-branch working trees: `OK: 12 protocols compared across firmware doc, host tool and firmware.` rc=0 `[VERIFIED: both runs this session]`.

**How to avoid:** delete the `--wiki-dir wiki-clone` line from the step in the same PR that adds the grep leg. Add nothing else — the fix is a deletion, so the no-comments rule is trivially satisfied.

**Warning signs:** any claim that "the three existing legs pass" that is not backed by a pasted rc=0 for all three.

### Pitfall 2: the resolver lands the sub-repos on `main`, and both other legs fail there

**What goes wrong:** on a scheduled run — the only trigger that will fire once the workflow is registered — the two sub-repos are checked out at `main`, not `beta`, and the wiki's claim-stamps do not describe `main`.

**Why it happens.** The resolver, verbatim `[VERIFIED: /workspaces/.github/workflows/wiki-check.yml:59,64,66]`:

```
          CAND="${{ github.head_ref || github.ref_name }}"
              RESOLVED="$CAND"
              RESOLVED="beta"
```

For a `schedule` event `github.head_ref` is empty and `github.ref_name` is the workflow's own branch — `main` once the D-14 PR merges. `main` **exists** in both sub-repos, so the `git ls-remote --exit-code --heads` probe succeeds and `RESOLVED="$CAND"` = `main`. The step's own comment asserts the opposite ("the resolver step below lands both sub-repos on their integration branch (`beta`) whenever this fires on its own schedule") — that comment is false as written.

Measured consequences of resolving to `main` `[VERIFIED: all four runs this session]`:

- `firestarter_app@main` has no `firestarter/data/chip_database.json` at all. A fresh `--depth 1 -b main` clone contains `firestarter/data/{database_generated.json, database_overrides.json, pin-maps.json}`. The HONEST-02 step's `--db firestarter_app/firestarter/data/chip_database.json` therefore points at nothing; feeding the raw 404 body to the checker produced `ERROR: cannot load database …: Extra data: line 1 column 4` and rc=2.
- `firestarter@main` has no `PROTOCOLS.md` (the script looks for it at `args.fw_dir / "PROTOCOLS.md"`; the milestone branch has it at the repo root). Result: `ERROR: PROTOCOLS.md not found under fw-main`, rc=2.
- Every wiki stamp records `db-sha256-16=ccbc8d2c4866a5af`, which is the hash of the database on **`beta`** and on the milestone branch, not on `main`.

Against `beta` clones of both sub-repos, all three legs are green `[VERIFIED: this session]`:

```
LEG 3 -- stamp freshness: 6 stamps checked against db-sha256-16=ccbc8d2c4866a5af, 0 stale
OK: leg1 stamp-present 5 matched/0 missing, leg2 claims-resolve 1 regions/39 claims/5 unchecked, leg3 stamp-freshness 6 checked/0 stale.
OK: 12 protocols compared across firmware doc, host tool and firmware.
OK: 10 pages, all reachable from Home.md by some link path, all internal links resolve, all filenames legal, and all listed in _Sidebar.md.
```

**How to avoid:** make the resolver's behaviour match its stated intent — treat `main` as not-a-candidate, so the scheduled and dispatch runs fall through to `beta`. The minimal change is to gate the candidate on the event or on the name, e.g. resolve `CAND` to the empty string when it equals the meta default branch before the `ls-remote` probe. Either way the existing comment becomes true rather than being left as a false claim in a milestone whose whole point is that nothing claims more than the code backs.

**Warning signs:** a plan that adds the grep leg without touching the resolver, or evidence that runs the checkers against `/workspaces/firestarter*` (the milestone working trees) and calls that "as CI would".

### Pitfall 3: D-09's premise — the default `GITHUB_TOKEN` may not be covered by the `Integration` bypass

**What goes wrong:** if the Actions bypass does not cover a push made with the workflow's default `GITHUB_TOKEN`, then the next stable release in **both** sub-repos fails at the `stefanzweifel/git-auto-commit-action` step, and in `firestarter` the `softprops/action-gh-release` step that follows never runs. That is precisely the outcome D-09 exists to prevent, and it would be discovered at the next release rather than in this phase.

**What is actually established:**

- The `GITHUB_TOKEN` is "a GitHub App installation access token … to authenticate on behalf of the GitHub App installed on your repository" `[CITED: docs.github.com/en/enterprise-cloud@latest/actions/concepts/security/github_token]`. That page names no app and says nothing about rulesets.
- GitHub Apps are eligible bypass actors, in `always` or `pull request only` mode `[CITED: docs.github.com/en/repositories/…/managing-rulesets/creating-rulesets-for-a-repository]`.
- Whether the *default* token is treated as the GitHub Actions app (id 15368) for bypass evaluation is stated **nowhere** in the documentation I could reach. Community material consistently reports the opposite for classic branch protection and recommends a custom GitHub App with `actions/create-github-app-token`, a PAT, or a bot account; the most authoritative reply in the canonical thread is a GitHub staff comment from 2022 arguing such a bypass would be insecure, and the 2024 replies all use a custom app `[CITED: github.com/orgs/community/discussions/25305]`.
- The 2025-09-10 changelog adds an `exempt` bypass type "useful for trusted, high-volume automation", which the REST schema exposes as `bypass_mode: "exempt"` — a lever available if `always` proves insufficient `[CITED: github.blog/changelog/2025-09-10-github-ruleset-exemptions-and-repository-insights-updates/]`.

This is `[ASSUMED]`, and it is the assumption with the highest blast radius in the phase. CONTEXT.md already records that the bypass "ships configured and unproven"; this research raises that from *unproven* to *contradicted by the available secondary evidence*.

**How to avoid / what to plan:**

1. **Cheap decisive probe, outside the three repos:** create a throwaway repository, apply the identical ruleset body, add a `workflow_dispatch` workflow that commits an empty change and pushes to `main` with the default `GITHUB_TOKEN`, dispatch it, record the result, delete the repository. This falsifies or confirms D-09 in minutes and touches nothing real. Repository creation is an account mutation — gate it as a `checkpoint:human-verify`.
2. If the probe fails, the honest options are: leave the rulesets as designed and record in Phase 173's ledger that the next stable release in both sub-repos will need a release-workflow change (this milestone's scope note files such changes rather than fixing them); or add a second bypass actor, which weakens "no direct push is true of every person" only if that actor is a person — a dedicated GitHub App is not.
3. Either way, the read-back must confirm what the API actually stored: if GitHub silently drops an `Integration` bypass on a user-owned repository, the three-way equality still passes (all three drop it identically) while the intent is lost. **Assert the bypass list explicitly**, not just equality.

### Pitfall 4: the three `.github` PRs must be branched from `main`, not from the milestone branch

**What goes wrong:** a PR whose head is `gsd/v1.35-documentation-consolidation-wiki-migration` and whose base is `main` carries the entire unreleased milestone — 733 commits in prom, 531 in `firestarter`, 781 in `firestarter_app` `[VERIFIED: CONTEXT.md live-state block; re-confirmed this session that `main`, `beta` and `gsd/v1.35-…` are three distinct heads in both sub-repos]`. D-08 asks for "three small PRs — each carrying only that repo's `.github/` files". Nothing about the milestone branch satisfies that.

**How to avoid:** author on the milestone branch (per the standing submodule constraint), then for each repo cut a fresh branch from `origin/main`, take just the wanted paths onto it, push, and open the PR:

```bash
git -C firestarter fetch origin main
git -C firestarter switch -c policy/contributing-pointer origin/main
git -C firestarter checkout gsd/v1.35-documentation-consolidation-wiki-migration -- .github/CONTRIBUTING.md
git -C firestarter commit -m "docs: point contributors at the project wiki" && git -C firestarter push -u origin HEAD
gh pr create --repo henols/firestarter --base main --head policy/contributing-pointer --title "..." --body "..."
```

**Warning signs:** a `gh pr create` whose `--head` is the milestone branch; a PR diff with more than one or four files; a PR "Files changed" count in the hundreds.

### Pitfall 5: merging the firmware PR could cut a stable firmware release

**What goes wrong:** `firestarter/.github/workflows/build.yml` fires on push to any branch except `beta`, and its three publish steps are gated only by `if: github.event_name == 'push' && github.ref == 'refs/heads/main'` — a version bump, a `stefanzweifel/git-auto-commit-action` push back onto `main`, and a `softprops/action-gh-release` with `make_latest: true` `[VERIFIED: /workspaces/firestarter/.github/workflows/build.yml:173-204]`. A merge into `main` is a push to `main`.

**The measured difference between the two sub-repos.** `firestarter_app/.github/workflows/release.yml` ignores `.github/**` outright `[VERIFIED: /workspaces/firestarter_app/.github/workflows/release.yml:6-14]`:

```yaml
    paths-ignore:
    - '**.md'
    - '**.sh'
    - '.gitignore'
    - 'docs/**'
    - 'images/**'
    - '.github/**'
    - '.vscode/**'
    - 'tools/**'
```

`firestarter`'s `build.yml` does **not** `[VERIFIED: /workspaces/firestarter/.github/workflows/build.yml:35-43]`:

```yaml
    paths-ignore:
    - '**.md'
    - '**.sh'
    - '.gitignore'
    - 'docs/**'
    - 'documents/**'
    - 'images/**'
    - '.vscode/**'
    - '.editorconfig/**'
```

So the firmware merge is skipped **only** if `.github/CONTRIBUTING.md` matches `'**.md'`. GitHub's docs state that "when all the path names match patterns in `paths-ignore`, the workflow will not run" but say nothing about whether these globs match inside dot-prefixed directories `[CITED: docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax]`. Neither sub-repo has ever committed a file under `.github/**.md`, so there is no historical run to read the answer off `[VERIFIED: git log --all -- '.github/**.md' in both sub-repos returns nothing, this session]`. That `'**.md'` covers `.github/CONTRIBUTING.md` is therefore `[ASSUMED]`.

**How to avoid — a free, decisive oracle:** the `pull_request` trigger carries the *same* `paths-ignore` list, and the head branch push is filtered by the same rules. So the answer is visible before any merge:

- push the branch, then read the checks on the PR head commit: `gh api /repos/henols/firestarter/commits/<sha>/check-runs --jq '[.check_runs[].name]'`.
- If `Firestarter CI` is absent, the filter excluded the file and the merge to `main` will be skipped identically. If it is present, **do not merge** until either the file is moved to the repository root (community-health precedence is `.github` > root > `docs`, so root still works `[CITED: docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/creating-a-default-community-health-file]`) or `.github/**` is added to `build.yml`'s `paths-ignore` in the same PR.

Note separately that `firestarter/.github/workflows/py32f071.yml` triggers on `push: branches: ['**']` with no `paths-ignore`, so it **will** run on the merge — but it publishes nothing; its own text says "This workflow publishes nothing. Its two upload-artifact steps attach ephemeral build output to the run itself" `[VERIFIED: /workspaces/firestarter/.github/workflows/py32f071.yml:20-23]`. Expect one green build, no release.

### Pitfall 6: an authored `MIGRATION-TABLE.md` row can silently change what the provenance checker counts

**What goes wrong:** `honest01_claims.py` filters the table to rows that carry a real SHA; Phase 171's verify asserted "rows with a SHA: 8". A new row with anything other than the marker in that column changes the count and invalidates that assertion.

**The mechanism, read this session.** The filter is `return [row for row in rows if row.get("Pre-deletion SHA", NO_SHA_MARKER) != NO_SHA_MARKER]` `[VERIFIED: /workspaces/tools/wiki/honest01_claims.py:93]`, and `NO_SHA_MARKER = "—"` — an em dash, U+2014 `[VERIFIED: /workspaces/tools/wiki/honest01_claims.py:49]`.

**Proven fix.** Add the authored page to the **main** table with `—` in both `Source path` and `Pre-deletion SHA`, exactly as the existing `Home` row does (`| firestarter_prom | — | Home | Home | — | 167 |`). Simulated this session:

```
baseline rows with SHA: 8
['Programming-Protocols', 'Shield-Revisions', 'Install-Beta', 'Testing-Chips', 'Lockable-PROMs', 'Protocol-Flags', 'Protocol-ID', 'Shell-Completion']
with authored Contributing row, rows with SHA: 8
['Programming-Protocols', 'Shield-Revisions', 'Install-Beta', 'Testing-Chips', 'Lockable-PROMs', 'Protocol-Flags', 'Protocol-ID', 'Shell-Completion']
```

The proposed row: `| firestarter_prom | — | Contributing | Contributing | — | 172 |` `[VERIFIED: parse_migration_table run against the modified table, this session]`.

A prose note beneath the table (like the ones already there for `How-To-Edit-This-Wiki` and the two renames) should record that the page was **authored from gh#9**, not migrated, so provenance stays answerable from the table alone per Phase 171 D-06. Note the parser quirk that makes this safe: `header` is captured from the *first* table only, so the later three-column tables' rows are zipped against six keys, lack a `Pre-deletion SHA` entry, and are filtered out by the `.get(...)` default.

### Pitfall 7: "it parses as YAML" is not validation for an issue form

**What goes wrong:** a form with a mistyped `type` or a misplaced attribute parses fine and then renders wrong — or not at all — on GitHub, after it has already merged into the default branch, which is the only place it takes effect.

**How to avoid:** `check-jsonschema` ships the SchemaStore schemas offline; the builtin list includes `vendor.github-issue-forms`, `vendor.github-issue-config`, `vendor.github-discussion`, `vendor.github-workflows` and `vendor.github-actions` `[VERIFIED: check-jsonschema --help, this session]`. Both a valid form and a valid `config.yml` were accepted, and a form with `type: texarea` was rejected with:

```
Schema validation errors were encountered.
  sample/broken.yml::$.body[0].type: 'texarea' is not one of ['checkboxes', 'dropdown', 'input', 'markdown', 'textarea', 'upload']
```

`[VERIFIED: three runs this session]`. The schema's top-level properties are `['name', 'description', 'title', 'labels', 'projects', 'assignees', 'type', 'body']` with `additionalProperties: false` `[VERIFIED: json.schemastore.org/github-issue-forms.json fetched and inspected this session]`, which matches the documented key list `[CITED: docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/syntax-for-issue-forms]`.

### Pitfall 8: D-07's premise is undocumented

**What goes wrong:** if adding templates changes what `https://github.com/henols/firestarter_prom/issues/new?title=…&body=…` does, the browser tier of `dev test --submit` degrades — and product code may not be edited to compensate.

**What is established:** `config.yml` lives in `.github/ISSUE_TEMPLATE`, takes the keys `blank_issues_enabled` and `contact_links[].{name,url,about}`, and "will customize the template chooser when the file is merged into the repository's default branch" `[CITED: docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/configuring-issue-templates-for-your-repository]`. Note the scope of that sentence: the setting is described as customising **the chooser**, not as rewriting `/issues/new`.

**What is not:** no GitHub documentation page I could reach states whether `/issues/new` with `title`/`body` query parameters still opens a prefilled blank form once templates exist. The query-parameter page documents `title`, `body`, `labels`, `milestone`, `assignees`, `projects` and `template`, and notes that "Query parameters for issue form fields can also be passed to the issue template chooser", without addressing the redirect `[CITED: docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/creating-an-issue]`. An unauthenticated probe of `/issues/new?title=x&body=y` on four repositories (including two that already have templates) returned `302 → /login?return_to=…` with the full query preserved in every case — consistent with, but not proof of, the prefill surviving `[VERIFIED: curl probes this session]`.

So "the prefill still works with templates present and `blank_issues_enabled: true`" is `[ASSUMED]`. It is a *soft* failure if wrong (the tester sees the chooser and picks a template) and the milestone forbids the product-code fix, so it should not block the phase — but it must be **checked after the prom PR merges**, from a logged-in browser, with the exact URL `submit.py` builds: `f"https://github.com/{SUBMIT_REPO}/issues/new?{query}"` where `SUBMIT_REPO = "henols/firestarter_prom"` `[VERIFIED: /workspaces/firestarter_app/firestarter/submit.py:62,283]`. If it turns out to redirect, the finding is filed, not fixed.

Two real-world configurations confirm the shape is at least common: `cli/cli` ships `bug_report.md`, `submit-a-design-proposal.md`, `submit-a-request.md` and a `config.yml` with `blank_issues_enabled: true`; `astral-sh/uv` ships three `.yaml` forms and a `config.yml` with `blank_issues_enabled: true` and two `contact_links` `[VERIFIED: gh api /repos/*/contents/.github/ISSUE_TEMPLATE, this session]`.

### Pitfall 9: registering the workflow turns on two checks that have never run

D-14 already names this. Concretely: `wiki.py links` (WIKI-05) and `honest02_truth.py` (HONEST-02) were written in Phase 168 and have never executed in CI, because `wiki-check.yml` is absent from prom's default branch. Once registered they run weekly, against whatever the resolver picks. Combined with Pitfall 2, that is how a green-looking phase produces a red repository seven days later. The record should credit Phase 168 for writing them and Phase 172 for making them run.

## Code Examples

### The one canonical ruleset body, and the three calls

```bash
gh api /repos/henols/firestarter/rulesets/4998759 > "${PHASE_DIR}/evidence/172-ruleset-4998759-pre-delete.json"

gh api --method POST /repos/henols/firestarter_prom/rulesets   --input /tmp/ruleset.json
gh api --method DELETE /repos/henols/firestarter/rulesets/4998759
gh api --method POST /repos/henols/firestarter/rulesets        --input /tmp/ruleset.json
gh api --method POST /repos/henols/firestarter_app/rulesets    --input /tmp/ruleset.json
```

The pre-delete capture is not optional: D-10 is one-way. Its measured content, for the record `[VERIFIED: gh api /repos/henols/firestarter/rulesets/4998759, this session]`:

```json
{"id":4998759,"name":"Protect main","target":"branch","source_type":"Repository","source":"henols/firestarter","enforcement":"disabled","conditions":{"ref_name":{"exclude":[],"include":["~DEFAULT_BRANCH"]}},"rules":[{"type":"deletion"},{"type":"non_fast_forward"},{"type":"pull_request","parameters":{"required_approving_review_count":0,"dismiss_stale_reviews_on_push":false,"required_reviewers":[],"require_code_owner_review":false,"require_last_push_approval":false,"required_review_thread_resolution":false,"require_extra_approval_for_unattributed_changes":true,"allowed_merge_methods":["merge","squash","rebase"]}}],"node_id":"RRS_lACqUmVwb3NpdG9yec4wS9fMzgBMRmc","created_at":"2025-04-22T11:42:12.549Z","updated_at":"2025-06-05T19:56:05.571Z","bypass_actors":[{"actor_id":null,"actor_type":"DeployKey","bypass_mode":"always"}],"current_user_can_bypass":"never","_links":{"self":{"href":"https://api.github.com/repos/henols/firestarter/rulesets/4998759"},"html":{"href":"https://github.com/henols/firestarter/rules/4998759"}}}
```

### POLICY-03 verify leg (house style, literal `&&`)

```
EV=/workspaces/.planning/phases/172-policy-one-tracker-protected-main/evidence/172-XX-ruleset-readback.txt && D=$(mktemp -d) && : > "$EV" && for r in firestarter_prom firestarter firestarter_app; do gh api "/repos/henols/$r/rulesets" > "$D/$r-list.json"; test "$(jq length "$D/$r-list.json")" -eq 1 || exit 1; ID=$(jq -r '.[0].id' "$D/$r-list.json"); gh api "/repos/henols/$r/rulesets/$ID" > "$D/$r-raw.json"; jq -S 'del(.id,.node_id,.created_at,.updated_at,._links,.source,.current_user_can_bypass) | .rules |= sort_by(.type) | .bypass_actors |= sort_by(.actor_type)' "$D/$r-raw.json" > "$D/$r-norm.json"; { echo "== $r id=$ID"; cat "$D/$r-raw.json"; echo; } >> "$EV"; done && diff "$D/firestarter_prom-norm.json" "$D/firestarter-norm.json" && diff "$D/firestarter_prom-norm.json" "$D/firestarter_app-norm.json" && test "$(jq -r .enforcement "$D/firestarter_prom-norm.json")" = active && test "$(jq -r '[.rules[].type]|sort|join(",")' "$D/firestarter_prom-norm.json")" = "deletion,non_fast_forward,pull_request" && test "$(jq -r '[.bypass_actors[]|"\(.actor_type):\(.actor_id):\(.bypass_mode)"]|join(",")' "$D/firestarter_prom-norm.json")" = "Integration:15368:always" && test "$(jq -r '.conditions.ref_name.include|join(",")' "$D/firestarter_prom-norm.json")" = "~DEFAULT_BRANCH" && test -s "$EV"
```

Assertions this makes that a naive existence check would not: exactly one ruleset per repo (so the incumbent is really gone), `enforcement` is `active` (the roadmap's named trap), the rule *set* is exactly the three POLICY-03 rules, and the bypass list is exactly the Actions app — which also catches the silent-drop case in Pitfall 3.

### The `dev test` template's routing problem (D-06)

`devtest-triage` keys on the `[dev test]` title marker **plus** a fenced-JSON `schema_version` block that only the CLI emits, and the host deliberately omits the `labels` query parameter because GitHub drops it for filers without write access — the docstring records this verbatim `[VERIFIED: /workspaces/firestarter_app/firestarter/submit.py:272-283]`:

```python
def build_issue_url(title: str, body: str) -> str:
    """`https://github.com/<SUBMIT_REPO>/issues/new?...`.

    Percent-encodes `title`/`body` via `urllib.parse.urlencode(quote_via=quote)`.
    Deliberately OMITS the `labels` query param (RESEARCH Pitfall 1): GitHub
    silently drops or 404s the `labels` param for community testers without
    write access on the target repo -- triage relies on the `[dev test]` title
    marker plus the fenced-JSON `schema_version` instead. ...
```

Template-declared `labels:` are a different mechanism from the query parameter and are applied server-side regardless of the filer's permissions, so the templates *can* pre-apply labels where the URL could not. The Markdown `dev test` template must set a `title:` prefix that is **not** `[dev test]`.

Markdown template front matter keys `[CITED: docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/configuring-issue-templates-for-your-repository]`: `name`, `about`, `title`, `labels`, `assignees`. File extension `.md`; YAML forms use `.yml`/`.yaml`; both live in `.github/ISSUE_TEMPLATE` and coexist — "Issue template filenames … need a *.md* extension. Issue templates created with issue forms need a *.yml* extension" `[CITED: docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/about-issue-and-pull-request-templates]`.

### An issue form that validates (shape only — field choices are Claude's discretion)

```yaml
name: Bug report
description: Something in the CLI or firmware behaves incorrectly
title: "[BUG] "
labels: ["bug", "needs:report"]
body:
  - type: input
    id: app-version
    attributes:
      label: firestarter version
      placeholder: 3.0.0b22
    validations:
      required: true
  - type: dropdown
    id: board
    attributes:
      label: Board
      options:
        - uno
        - uno328pb
        - leonardo
    validations:
      required: true
  - type: textarea
    id: steps
    attributes:
      label: Steps to reproduce
    validations:
      required: true
```

Validated this session: `check-jsonschema --builtin-schema vendor.github-issue-forms` → `ok -- validation done`, rc=0. The board options come from D-05's own list; the four fields the firmware README asks for today are, verbatim `[VERIFIED: /workspaces/firestarter/README.md:73-81]`:

```
- the firmware version, from `firestarter fw` or `include/version.h`
- your board: `uno`, `uno328pb` or `leonardo`
- the chip's part number and manufacturer, for hardware-specific issues
- steps to reproduce
```

Labels available to pre-apply, live `[VERIFIED: gh api /repos/henols/firestarter_prom/labels, this session]`: `bug, cause:database, cause:firmware, cause:harness, cause:rig, chip:validated, dev-test, documentation, duplicate, enhancement, feature, fix:committed, fix:released, fixed:superseded, good first issue, help wanted, intermittent, invalid, needs:report, question, wontfix`.

### `config.yml` (D-07 keeps blank issues on)

```yaml
blank_issues_enabled: true
contact_links:
  - name: Firestarter wiki
    url: https://github.com/henols/firestarter_prom/wiki
    about: Installation, chip testing, protocols and pin maps.
```

Validated this session against `vendor.github-issue-config` → `ok -- validation done`, rc=0.

### The `Contributing` wiki page — shape and navigation

Page opening, copied from the live wiki `[VERIFIED: fresh clone, Shell-Completion.md:1-5 and Home.md:1-5]`:

```markdown
<p align="left"><img src="https://raw.githubusercontent.com/henols/firestarter_app/refs/heads/main/images/firestarter_logo.png" alt="Firestarter EPROM Programmer" width="200"></p>

---

# Contributing
```

`_Sidebar.md` today, verbatim `[VERIFIED: fresh clone, _Sidebar.md:1-10]`:

```markdown
- [Home](Home)
- [Install Beta](Install-Beta)
- [Testing Chips](Testing-Chips)
- [Programming-Protocols](Programming-Protocols)
- [Chip-Database-Fields](Chip-Database-Fields)
- [Pin-Maps](Pin-Maps)
- [Lockable-PROMs](Lockable-PROMs)
- [Shield-Revisions](Shield-Revisions)
- [Breaking-Changes](Breaking-Changes)
- [Shell-Completion](Shell-Completion)
```

Add `- [Contributing](Contributing)`. `Home.md` ends with a `## Reference` bullet list of the same form (`- [Shell-Completion](Shell-Completion) — turning on tab completion…`); one more bullet there satisfies the orphan check. Only links of the form `[text](Page-Name)` count — `wiki.py`'s matcher is `LEGAL_LINK_RE = re.compile(r"\[([^\]]*)\]\(([A-Za-z0-9][A-Za-z0-9-]*)(?:#([A-Za-z0-9_-]*))?\)")` `[VERIFIED: /workspaces/tools/wiki/wiki.py:39]`, so an absolute `https://github.com/…/wiki/Contributing` URL in `Home.md` would **not** satisfy the reachability check.

Pre-push gate, green on the current wiki this session:

```
python3 /workspaces/tools/wiki/wiki.py links --source-dir wiki-clone
OK: 10 pages, all reachable from Home.md by some link path, all internal links resolve, all filenames legal, and all listed in _Sidebar.md.
```

Do **not** run `tools/wiki/selftest.sh` — it mutates Phase 168 evidence.

### D-01's source text (gh#9), fetched this session

The relocation source, for the planner to work from without a second API call `[VERIFIED: gh issue view 9 --repo henols/firestarter_prom, this session]`. Its three POLICY-01 statements are: "This is the **only repository** where GitHub Issues are maintained"; "GitHub Issues are disabled" under both sub-repos; and under `## Pull Requests`, "Submit pull requests to the repository containing the code you are changing. — Application → firestarter_app — Firmware → firestarter — Project documentation or planning → firestarter_prom". Its cross-repository protocol is four numbered steps: create one issue in `firestarter_prom`; reference it from each implementation PR; keep design discussion in the issue; keep implementation discussion in the PRs.

### The three README sections D-03 trims

`README.md:33-37` (prom, 37 lines) `[VERIFIED: /workspaces/README.md:33-37]`:

```markdown
## Reporting a problem

**[Open an issue here](https://github.com/henols/firestarter_prom/issues)**,
whichever part it concerns. The firmware and CLI repositories do not have their
own trackers.
```

`firestarter/README.md:73-81` — heading, one sentence and the four "Include:" bullets quoted above. `firestarter_app/README.md:104-108` `[VERIFIED: /workspaces/firestarter_app/README.md:104-108]`:

```markdown
## Contributing

Issues and pull requests are welcome.
**[Report a problem here](https://github.com/henols/firestarter_prom/issues)** — the tracker for
all three Firestarter repositories.
```

All three already point at the correct tracker — LEGACY-01 is met before the phase starts. What D-03 changes is the *duplication*, not the destination.

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Classic branch protection rules | Repository rulesets (layered, API-first, with bypass actors) | Rulesets GA 2023; still both exist | Almost all community guidance found this session predates rulesets and describes the classic model — read every "GitHub Actions cannot push to a protected branch" claim with that date in mind |
| Markdown-only issue templates | YAML issue forms with typed inputs and `validations.required` | Forms GA 2021 | D-05's split is current practice: forms where fields matter, Markdown where the job is to hand over a command |
| `always` / `pull_request` bypass modes | plus `exempt` — "silently skips enforcement … useful for trusted, high-volume automation" | 2025-09-10 changelog | A third lever if `always` proves not to cover the default token |
| Repository-level bypass actors limited to roles/teams/apps | Individual users can now be added as bypass actors via UI, REST and GraphQL | 2026-05-07 changelog | Not wanted here — D-09 rejects a person-shaped bypass by design |

**Deprecated/outdated:**
- The `labels=` issue URL query parameter for filers without write access: GitHub drops it — already handled in `submit.py` and superseded by template-declared labels.
- Any guidance to solve Actions-push-to-protected-branch with a PAT stored as a secret: it works, but it makes "no direct push is true of every person" false, which D-09 rejects.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | A push authenticated by the workflow's default `GITHUB_TOKEN` is covered by a `bypass_actors` entry of `{actor_type: "Integration", actor_id: 15368, bypass_mode: "always"}` | Pitfall 3, Pattern 1 | **High.** The next stable release in both sub-repos fails at the version-bump auto-commit. Available secondary evidence points the other way; falsifiable in minutes with a throwaway-repo probe |
| A2 | `actor_type: "Integration"` is accepted on a **user-owned** repository | Pattern 1 | Medium. The `POST` 422s or the bypass is silently dropped; mitigated by creating prom's ruleset first and asserting the bypass list on read-back |
| A3 | `https://github.com/henols/firestarter_prom/issues/new?title=…&body=…` still opens a prefilled blank issue once templates exist and `blank_issues_enabled: true` | Pitfall 8, D-07 | Medium. The browser tier of `dev test --submit` degrades to the chooser; no product-code fix is permitted this milestone, so the finding is filed |
| A4 | `'**.md'` in `paths-ignore` matches `.github/CONTRIBUTING.md` | Pitfall 5 | **High if unchecked, zero if checked.** A spurious `make_latest` firmware release. The PR's own check list resolves it before the merge |
| A5 | Omitting `require_extra_approval_for_unattributed_changes` and `required_reviewers` from the `POST` body yields identical GitHub-applied defaults on all three repos | Pattern 1 | Low. The three-way equality catches it immediately if not |
| A6 | For a `schedule` event `github.ref_name` is the workflow's own branch (`main` after the D-14 merge), and `github.head_ref` is empty | Pitfall 2 | Low. If wrong, the resolver picks `beta` and the legs pass — the recommended fix is harmless either way |
| A7 | A ruleset scoped to `~DEFAULT_BRANCH` on `main` does not affect the wiki repository or the `beta` lockstep cut | Runtime State Inventory | Low for this phase (POLICY-04 is Phase 173's job to demonstrate); the wiki is a separate repository with no rulesets |

## Open Questions

1. **Does the Actions bypass cover the default `GITHUB_TOKEN`?**
   - What we know: the token is a GitHub App installation access token; GitHub Apps are eligible bypass actors; the docs never connect the two.
   - What's unclear: whether bypass evaluation attributes the default token to app 15368.
   - Recommendation: throwaway-repo probe gated as `checkpoint:human-verify`, before the one-way DELETE. If it cannot be run, ship as designed and put the risk in Phase 173's ledger explicitly — "configured, unproven, and the secondary evidence is against us" rather than "configured, unproven".

2. **Should `wiki-check.yml`'s false resolver comment be corrected or removed?**
   - What we know: the comment claims scheduled runs land on `beta`; they land on `main`. The no-comments rule binds what this phase *writes*; it does not obviously compel deleting what earlier phases wrote.
   - Recommendation: fix the behaviour so the comment becomes true. That satisfies both the honesty constraint and the no-comments rule without the phase authoring a single comment.

3. **Does the `Contributing` page belong in `Home.md`'s `## Reference` list, or in its own line near the beta/testing call-to-action?**
   - What we know: only an internal `[text](Page)` link satisfies the orphan check; placement is otherwise free.
   - Recommendation: Claude's discretion under D-01; the closing paragraph of `Home.md` already addresses would-be contributors ("help check chips against real hardware"), which reads as the natural neighbour.

4. **Does the firmware `.github` PR need `build.yml` edited at all?**
   - What we know: it depends entirely on A4, and the PR's check list answers it for free.
   - Recommendation: plan the check as a gate with two named branches — merge, or move the file to the repository root — rather than pre-emptively editing a publishing workflow.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| `gh` CLI, authenticated | rulesets, PRs, label/issue reads | ✓ | 2.98.0, account `henols`, scopes `gist, read:org, repo, workflow`, `admin: true` on all three repos | none needed |
| Network to `github.com` / `raw.githubusercontent.com` | wiki clone, API, docs | ✓ | wiki cloned, four repos cloned this session | none |
| `git` | wiki push, sub-repo branches | ✓ | present | none |
| `jq` | ruleset normalisation | ✓ | present | `python3 -c 'import json…'` |
| `python3` | `tools/wiki/*.py` | ✓ | system 3.12; **use `uv venv --python 3.11`** for anything that must mirror app CI | none |
| `uv` | 3.11 venvs, `--with` runs | ✓ | present (used this session) | `python3 -m venv` |
| `check-jsonschema` | issue-form validation | ✗ (installable) | 0.38.0 on PyPI | inline required-key + `type`-enum assertion |
| Wiki repository | D-01 | ✓ | `firestarter_prom.wiki.git`, 10 pages + `_Sidebar.md` | none — it cannot be created by automation, but it already exists |
| A browser session on github.com | A3's post-merge prefill check; any rendered-page inspection | operator-only | — | record as an unverified property, as Phase 171 did |

**Missing dependencies with no fallback:** none.
**Missing dependencies with fallback:** `check-jsonschema` (SUS verdict; inline assertion is the fallback).

## Validation Architecture

`workflow.nyquist_validation` is absent from `.planning/config.json` `[VERIFIED: /workspaces/.planning/config.json — workflow block is `_auto_chain_active`, `research`, `plan_check`, `verifier`, `code_review`]`, so this section is included.

### Test Framework

| Property | Value |
|----------|-------|
| Framework | None — this phase writes no product code. Validation is assertion scripts in `<automated>` verify blocks plus the three existing `tools/wiki/` checkers |
| Config file | none |
| Quick run command | `python3 /workspaces/tools/wiki/wiki.py links --source-dir <wiki-clone>` |
| Full suite command | the three checkers run in sequence against a fresh wiki clone plus `beta` clones of both sub-repos (recipe below) |

The "full suite" for this phase, exactly as it must be run to mirror a fixed CI:

```bash
D=$(mktemp -d) && git clone --depth 1 https://github.com/henols/firestarter_prom.wiki.git "$D/wiki-clone" \
 && git clone --depth 1 -b beta https://github.com/henols/firestarter.git "$D/firestarter" \
 && git clone --depth 1 -b beta https://github.com/henols/firestarter_app.git "$D/firestarter_app" \
 && python3 /workspaces/tools/wiki/wiki.py links --source-dir "$D/wiki-clone" \
 && python3 /workspaces/tools/wiki/honest02_truth.py --wiki-dir "$D/wiki-clone" --db "$D/firestarter_app/firestarter/data/chip_database.json" --allowlist /workspaces/tools/wiki/claim-allowlist.json \
 && python3 /workspaces/tools/wiki/dispatch_mirror.py --app-dir "$D/firestarter_app" --fw-dir "$D/firestarter"
```

All three legs were green under this recipe this session. Note it deliberately does **not** pass `--wiki-dir` to `dispatch_mirror.py`, and deliberately uses `beta` rather than the local working trees.

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| POLICY-01 | Policy stated once on the wiki; three READMEs and three `.github/CONTRIBUTING.md` link rather than restate | integration | fresh wiki clone contains `Contributing.md` carrying all three statements; `grep -c` of the tracker sentence across the three READMEs shows a link and no restatement; `wiki.py links` green | ✅ (`wiki.py`) |
| POLICY-01 | The new page is reachable and listed | unit | `python3 tools/wiki/wiki.py links --source-dir <fresh clone>` | ✅ |
| POLICY-02 | Three templates + config exist, are schema-valid, and are on prom's default branch | unit + integration | `check-jsonschema --builtin-schema vendor.github-issue-forms .github/ISSUE_TEMPLATE/*.yml`; `gh api /repos/henols/firestarter_prom/contents/.github/ISSUE_TEMPLATE?ref=main --jq '[.[].name]'` after merge | ❌ Wave 0 (templates do not exist yet) |
| POLICY-02 | The `dev test` template does not carry the `[dev test]` marker | unit | `! grep -q '\[dev test\]' .github/ISSUE_TEMPLATE/<devtest>.md` | ❌ Wave 0 |
| POLICY-03 | Three rulesets, `enforcement: active`, identical modulo volatile fields, Actions-only bypass | integration | the read-back leg in "Code Examples" | ✅ (`gh` + `jq`) |
| POLICY-03 | Ruleset `4998759` captured before deletion | unit | `test -s evidence/172-*-ruleset-4998759-pre-delete.json && jq -e '.id == 4998759' <that file>` | ❌ Wave 0 |
| LEGACY-01 | Zero dead-tracker links outside `.planning/` | unit | the grep leg, run locally over the four directories | ✅ (proven this session) |
| LEGACY-01 | The guard is real, not vacuous | unit | plant `henols/firestarter/issues` in the wiki clone → leg exits 1; remove → exits 0 | ✅ (proven this session) |
| LEGACY-01 | The guard is live | integration | `gh api /repos/henols/firestarter_prom/contents/.github/workflows/wiki-check.yml?ref=main --jq .name` after merge; `gh workflow list --repo henols/firestarter_prom` includes it | ❌ Wave 0 |
| D-14 precondition | The three pre-existing legs pass | integration | the "full suite" recipe above | ✅ — but **currently RED** as the workflow invokes them (Pitfalls 1 and 2) |

### Sampling Rate

- **Per task commit:** the single assertion for that task's artifact (`wiki.py links` for the wiki task; `check-jsonschema` for a template task; the read-back leg for a ruleset task).
- **Per wave merge:** the full three-checker recipe plus the grep leg.
- **Phase gate:** full recipe green against a *fresh* wiki clone and *fresh* `beta` clones — not the local working trees — plus the three-way ruleset equality, before `/gsd-verify-work`.

### Wave 0 Gaps

- [ ] `.github/workflows/wiki-check.yml` — remove `--wiki-dir wiki-clone` from the dispatch-mirror step; covers D-14's precondition
- [ ] `.github/workflows/wiki-check.yml` — resolver must land scheduled runs on `beta`; covers D-14's precondition
- [ ] `.github/workflows/wiki-check.yml` — the LEGACY-01 grep leg; covers LEGACY-01/D-13
- [ ] `firestarter_prom/.github/ISSUE_TEMPLATE/` — three templates + `config.yml`; covers POLICY-02
- [ ] `evidence/172-*-ruleset-4998759-pre-delete.json` — one-way-operation capture; covers D-10
- [ ] Local validator install or the inline fallback; covers Pitfall 7

## Security Domain

`security_enforcement` is absent from `.planning/config.json`, so this section is included. The phase writes no application code; its security surface is repository access control and the integrity of what contributors are told.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | No authentication code; the only credential is the operator's existing `gh` token |
| V3 Session Management | no | — |
| V4 Access Control | **yes** | This *is* the phase. Repository rulesets with `enforcement: active`; a bypass list containing exactly one non-human actor; `current_user_can_bypass` asserted on read-back |
| V5 Input Validation | **yes (tooling)** | Issue forms validated against the SchemaStore schema before push; the grep pattern anchored so it cannot match the live tracker |
| V6 Cryptography | no | Nothing is signed or encrypted by this phase |
| V14 Configuration | **yes** | Least-privilege bypass; no secret added or changed; `permissions: contents: read` already set on `wiki-check.yml` and must stay that way when the grep leg is added |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| A ruleset that exists but does not enforce | Repudiation / false assurance | Assert `enforcement == "active"` and the rule set, never mere existence — the incumbent `4998759` is the live example |
| An over-broad bypass making "no direct push" vacuous | Elevation of privilege | D-09's single non-human actor; assert the bypass list verbatim on read-back |
| A dead `DeployKey` bypass carried forward | Elevation of privilege (latent) | D-10 deletes and recreates; zero deploy keys exist on all three repos today |
| A guard that fails open | Tampering (undetected) | The grep leg proven RED on a planted link before it is trusted; the `if … exit 1` form avoids the `! cmd` errexit hole |
| A workflow granted write to push to `main` | Elevation of privilege | `wiki-check.yml` keeps `permissions: contents: read`; nothing this phase adds needs write |
| A contributor pointed at a tracker that cannot receive their report | Denial of service (social) | LEGACY-01 and its new mechanical guard |

## Sources

### Primary (HIGH confidence)

- Live GitHub REST API via authenticated `gh` (this session): `/apps/github-actions`, `/repos/henols/{firestarter_prom,firestarter,firestarter_app}`, `/repos/*/rulesets`, `/repos/henols/firestarter/rulesets/4998759`, `/repos/henols/firestarter_prom/labels`, `gh issue view 9`
- Repository sources read this session with line ranges: `/workspaces/.github/workflows/wiki-check.yml`, `/workspaces/tools/wiki/{dispatch_mirror.py,honest01_claims.py,honest02_truth.py,wiki.py,MIGRATION-TABLE.md}`, `/workspaces/firestarter/.github/workflows/{build.yml,py32f071.yml,beta-build.yml}`, `/workspaces/firestarter_app/.github/workflows/{release.yml,ci.yml,publish.yml,beta-release.yml}`, `/workspaces/firestarter_app/firestarter/submit.py`, the three READMEs, `/workspaces/CLAUDE.md`, `/workspaces/.planning/{REQUIREMENTS.md,STATE.md,config.json}`
- Executions this session: all three wiki checkers against a fresh wiki clone and against `main` and `beta` clones of both sub-repos; the grep leg green/red/false-positive trials; `parse_migration_table` before and after an authored row; `check-jsonschema` accept and reject trials; `jq` ruleset normalisation

### Secondary (MEDIUM confidence)

- `docs.github.com/en/rest/repos/rules` — ruleset create/read schema
- `docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/creating-rulesets-for-a-repository` — bypass eligibility and modes
- `docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/{syntax-for-issue-forms,configuring-issue-templates-for-your-repository,about-issue-and-pull-request-templates}`
- `docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/creating-a-default-community-health-file`
- `docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/creating-an-issue` — issue URL query parameters
- `docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax` — `paths`/`paths-ignore` semantics
- `docs.github.com/en/enterprise-cloud@latest/actions/concepts/security/github_token`
- `github.blog/changelog/2025-09-10-github-ruleset-exemptions-and-repository-insights-updates/`; `github.blog/changelog/2026-05-07-repository-rulesets-user-bypass-and-branch-renaming/`
- `json.schemastore.org/github-issue-forms.json` (fetched and inspected)

### Tertiary (LOW confidence)

- `github.com/orgs/community/discussions/25305` and `/13836` — GitHub Actions pushing to protected branches; useful as counter-evidence for A1, not as proof
- Third-party write-ups on GitHub App tokens vs `GITHUB_TOKEN` (Medium, Mercari engineering) — all pre-date or ignore rulesets

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — everything except `check-jsonschema` is already installed and was exercised; `check-jsonschema` was installed and exercised, with a SUS verdict recorded
- Architecture / ordering: HIGH — derived from D-12 plus two measured defects; the ruleset body is docs-backed field by field
- Pitfalls 1, 2, 6: HIGH — reproduced with pasted output this session
- Pitfalls 3, 8 (A1, A3): LOW — undocumented GitHub behaviour; falsification proposed for A1, post-merge check for A3
- Pitfall 5 (A4): MEDIUM — mechanism fully measured, the one glob question resolved for free by the PR's own check list

**Research date:** 2026-09-01
**Valid until:** 2026-10-01 for the in-repo findings; **7 days** for the GitHub control-plane findings — rulesets and issue-form features are actively changing (two changelog entries inside twelve months touch bypass semantics alone), so re-run the read-backs rather than trusting this file's snapshots.
