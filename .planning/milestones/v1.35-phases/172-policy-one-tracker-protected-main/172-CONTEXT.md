# Phase 172: POLICY — One Tracker, Protected `main` - Context

**Gathered:** 2026-09-01
**Status:** Ready for planning

<domain>
## Phase Boundary

State the repository policy where contributors will actually read it, and make the GitHub
configuration enforce what the documentation claims. Four requirements, three of them
configuration and one of them already true:

| Req | What it asks | Measured state, 2026-09-01 |
|---|---|---|
| **POLICY-01** | Documentation states plainly: `firestarter_prom` is the only issue tracker, the two sub-repos have Issues disabled, and pull requests go to the repository containing the changed code. Stated **once**, canonically, and **linked** from the other two rather than restated in each. | Two of the three statements exist; the **PR-routing statement exists nowhere**. The tracker fact is currently restated in **all three** READMEs. |
| **POLICY-02** | `firestarter_prom` offers issue templates covering at least a bug report, a feature request, and a `dev test` chip-validation report. | **No `.github/ISSUE_TEMPLATE/` in any of the three repos.** |
| **POLICY-03** | `main` in all three repositories behind a ruleset with `enforcement: active` requiring a PR and forbidding direct push, force-push and deletion. Read back from the API. | prom `[]`, app `[]`, fw one ruleset (id `4998759`, `Protect main`) with the right rules but `enforcement: disabled`. |
| **LEGACY-01** | No documentation page sends a reader to `henols/firestarter/issues` or `henols/firestarter_app/issues`. | **Already zero.** All 21 grep hits sit inside `.planning/`. |

**In scope:** one new wiki page; `.github/CONTRIBUTING.md` in all three repos; `.github/ISSUE_TEMPLATE/`
in `firestarter_prom`; three GitHub rulesets created via API; a grep leg added to
`.github/workflows/wiki-check.yml`; trimming three README sections; three small `.github`-only
pull requests into the three `main` branches.

**Out of scope — settled, not open questions:**

- **No product code.** REQUIREMENTS.md's scope note: *"Any product-code change found necessary is
  filed, not fixed here."* `firestarter_app/firestarter/submit.py` is **not** edited by this phase
  (D-07 exists specifically to avoid needing to).
- **`.planning/` historical records are not swept.** REQUIREMENTS.md lists `.planning/`→`.planning/`
  citations as out of scope, historical-by-intent. All 21 surviving dead-tracker strings live there
  and stay.
- **gh#9's own disposition** (close it, or keep it pinned) belongs to **Phase 173 criterion 5**,
  which owns the upstream replies. This phase relocates its text; it does not answer it.
- **POLICY-04 and POLICY-05** — the `beta` lockstep cut under protection, and the GSD close
  procedure — are **Phase 173**. This phase creates the condition they respond to.
- **The compatibility matrix, family pages, algorithm pages and tutorials** stay deferred as
  FUT-W-01…05.

</domain>

<decisions>
## Implementation Decisions

### Where the policy lives

- **D-01: the canonical policy text is a new `Contributing` wiki page.** gh#9
  ("Repository Structure and Contribution Guide") already contains, in the operator's own words,
  exactly POLICY-01's three statements plus a cross-repository-change protocol. This is a
  **relocation**, not an authoring exercise — which keeps it inside activation decision 4
  ("relocate and correct only"). The page is the single copy; everything else links to it.
  Rejected: `CONTRIBUTING.md` in prom as the canonical copy (an in-repo documentation file is the
  shape WIKI-02 pushed everything out of, and PRs mostly happen in the sub-repos where prom's copy
  is invisible anyway); expanding prom's README (Phase 169 deliberately kept it to 37 lines as a
  front door).

- **D-02: `.github/CONTRIBUTING.md` in all three repositories, as pointers.** GitHub reads
  CONTRIBUTING.md only from the repo where a PR is opened, so a wiki page alone fires no native
  affordance in the two repos where PRs actually land. Each file is a few lines pointing at the
  wiki page — **a link, not a restatement**, so POLICY-01's "stated once" holds by construction.
  Under `.github/` rather than the repository root, keeping the roots as clear as Phase 171 left
  them.

- **D-03: all three README tracker sections trim to a single link, and the firmware README's four report-content bullets move into the bug-report issue template.**
  The four are the ones under its `Include:` heading. Today the tracker fact is stated
  three times in three different framings, which is the thing POLICY-01 says not to do. The
  firmware bullets (firmware version, board, chip part number, steps to reproduce) are genuinely
  useful and genuinely repo-scoped — they are not deleted, they move to where a filer sees them
  without having had to read a README first.
  Rejected: leaving Phases 169/170's text untouched (POLICY-01's "stated once" would then be met by
  argument rather than by construction).

- **D-04: one honest sentence about security reporting goes on the `Contributing` page.** Phase 171
  D-02 deleted `firestarter_app/SECURITY.md` on "silence is honest" and explicitly handed this
  forward. The sentence states the **non-claim**: Firestarter has no private disclosure channel, so
  security reports go on the public tracker with everything else. It commits the operator to
  nothing, it lands on a page being written anyway, and it is the same move Phase 173's honesty
  ledger makes.
  Rejected: silence (a would-be reporter gets no signal and hunts for a channel that does not
  exist); turning on GitHub private vulnerability reporting (a new capability outside POLICY-01…03,
  and the response commitment Phase 171 D-02 declined to make on the operator's behalf).

### Issue templates, and not breaking `dev test --submit`

- **D-05: YAML issue forms for bug report and feature request; a Markdown template for `dev test`.**
  Forms give required fields and dropdowns (board: `uno` / `uno328pb` / `leonardo`;
  shield revision; firmware and app versions) so a report cannot be filed without the information
  that currently has to be chased — prom carries a `needs:report` label and issue **#21** is a
  `dev test` report wearing it, so the cost is real and recurring. The `dev test` one stays Markdown
  because its job is to hand over a command, not to collect fields.

- **D-06: the `dev test` template routes to the CLI, and must NOT use the `[dev test]` title marker.**
  `devtest-triage` keys on the `[dev test]` title marker **plus** a fenced-JSON
  `schema_version` block that only `firestarter dev test <chip> --submit` produces. A hand-written
  report carrying the marker but no parseable JSON would be picked up by triage and then found
  unparseable — worse than not being picked up. The template therefore tells the reader to run the
  command, and its fallback section for people who cannot run it uses a **different** title marker.
  — **Reversibility:** costly — changing the marker later means reconciling it against issues
  already filed under the old one and against `devtest-triage`'s detection, which lives in a skill
  outside this repo.

- **D-07: `blank_issues_enabled` stays TRUE.** `.github/ISSUE_TEMPLATE/config.yml` with
  `blank_issues_enabled: false` redirects `/issues/new` to `/issues/new/choose` and drops the
  prefill — which would break the browser tier of `dev test --submit`, built at
  `firestarter_app/firestarter/submit.py:283` for exactly the testers who do not have `gh`
  installed. The `gh issue create` tier is REST and unaffected either way. Leaving blank issues
  enabled is also the only option that needs no product-code change, which the milestone scope note
  forbids here.

- **D-08: the `.github/` files reach `main` by pull request, in all three repositories, after the rulesets are active.**
  GitHub reads issue templates and community-health files from the **default
  branch only**, and `main` is **733 commits behind `beta`** in prom, **531** in `firestarter` and
  **781** in `firestarter_app`. Files landing only on `gsd/v1.35-…` would not be offered on the New
  Issue page within this milestone, possibly not for a long time. Three small PRs — each carrying
  only that repo's `.github/` files — make POLICY-02 observable rather than merely constructed, and
  the merges double as the first live exercise of PR-only `main`, which is what Phase 173's
  POLICY-05 has to document.
  — **Reversibility:** costly — undoing means three further pull requests into now-protected
  default branches; there is no direct-push path back.
  **Note for planning:** `firestarter_app/.github/workflows/release.yml` has `paths-ignore:
  '.github/**'`, so a `.github`-only merge to app's `main` does **not** cut a release. Confirm the
  equivalent for `firestarter`'s `build.yml` before merging.

### Rulesets

- **D-09: GitHub Actions is the sole bypass actor** — `actor_type: "Integration"`,
  `actor_id: 15368` (resolved from `/apps/github-actions`, not guessed), `bypass_mode: "always"`.
  This is load-bearing, not a convenience: **both sub-repos auto-commit a version bump back onto
  `main` from CI.** `firestarter_app/.github/workflows/release.yml:31` runs
  `stefanzweifel/git-auto-commit-action` on push-to-`main`, and `firestarter/.github/workflows/build.yml`
  does the same below its "PUBLISH BOUNDARY" comment — whose own text records that the auto-commit
  "landed on the protected branch". Both push as `github-actions[bot]` on the default
  `GITHUB_TOKEN`, which a repository-admin bypass would **not** cover. With Actions bypassing and
  nobody else, POLICY-03's "no direct push" is literally true of every **person**, including the
  operator.
  Rejected: no bypass at all (breaks the next stable release in both sub-repos, forcing release-
  workflow rework this milestone's scope note files rather than fixes); Actions + repository admin
  (with one maintainer, an always-on admin bypass makes "no direct push" true of nobody — a ruleset
  claiming protection it does not provide, which is the exact false-claim shape this milestone's
  honesty constraint exists to catch).

- **D-10: `firestarter`'s existing ruleset `4998759` is DELETED, and all three rulesets are created fresh from one identical body.**
  Three rulesets born from one call, with nothing inherited and no
  dead `DeployKey` bypass to reconcile. (That bypass grants nothing today: all three repos have
  **zero** deploy keys, measured.) Verification is a three-way API read-back that must be identical
  apart from `id`, `node_id`, timestamps and `_links` — which is the check the roadmap warns a mere
  existence assertion would fail to be.
  — **Reversibility:** one-way — deleting ruleset `4998759` destroys its identity and its
  2025-04-22 creation history permanently; the GitHub API has no undelete, so the only recovery is
  a new ruleset with a new id. **Capture the full JSON of `4998759` into the phase's evidence
  before issuing the DELETE.** Its measured pre-state: `target: branch`, conditions
  `ref_name.include: ["~DEFAULT_BRANCH"]`, rules `deletion` + `non_fast_forward` +
  `pull_request(required_approving_review_count: 0)`, `bypass_actors: [{actor_id: null,
  actor_type: "DeployKey", bypass_mode: "always"}]`, `enforcement: "disabled"`.

- **D-11: POLICY-03's four clauses only — PR required, no direct push, no force-push, no deletion.**
  gh#6 additionally asks for required status checks "where checks exist" and resolved
  review conversations "where applicable"; **neither goes in**, and both are recorded as knowingly
  not implemented so Phase 173's honesty ledger can state them as non-claims rather than have them
  read as quietly delivered. Status checks in particular are a trap: pinning a check name that
  never reports deadlocks that repo's `main` behind a check that will never go green, and prom has
  only `catalog-sync-check` registered with Actions.

- **D-12: rulesets are created LAST, all three at once, and only then the three `.github` PRs.**
  Everything else in the phase — the wiki page, the templates, the pointer files, the README trims,
  the grep leg — lands on the milestone branch and needs no access to `main`. Flipping enforcement
  last means no step in the phase ever requires a direct push, so there is no window in which a
  mis-ordered step locks the operator out of its own fix.

### LEGACY-01

- **D-13: LEGACY-01 gets a mechanical guard — a grep leg in `.github/workflows/wiki-check.yml`.**
  That job already checks out `meta`, `firestarter` and
  `firestarter_app` **and** clones the live wiki, so every surface LEGACY-01 covers is on disk in
  one place; one leg covers all of them with no new tooling. It is also the only option that covers
  the wiki, where pages are now edited with no pull request, no review and no CI gate on the edit.
  Rejected: a rule inside `tools/wiki/wiki.py links` (single `--source-dir`, so it sees the wiki
  clone and nothing else, leaving the three READMEs unguarded); recording the measurement with no
  guard (nothing would stop the six links returning).

- **D-14: the prom pull request carries `wiki-check.yml` as well, and the new leg is demonstrated failing before it goes in.**
  The workflow is **not registered with Actions** — it is absent from
  prom's default branch, so `catalog-sync-check.yml` is the only registered workflow and the leg
  would otherwise be inert. Carrying it in the same PR makes the guard live from merge. Before it
  goes in: plant a `henols/firestarter/issues` link, watch the leg go RED, remove it, watch it go
  GREEN — the same bar REQUIREMENTS.md set for HONEST-02 ("demonstrated failing before it is
  trusted"). Also verify the workflow's three existing legs pass locally first, so registration
  does not immediately produce a red weekly run.
  — **Reversibility:** costly — once registered, unregistering needs another PR into a protected
  default branch. Registration also brings **HONEST-02's** and **WIKI-05's** checks to life for the
  first time; they were shipped inert in Phase 168. Record that plainly: Phase 168 wrote them,
  Phase 172 is what makes them run.

- **D-15: the grep is strict — everywhere outside `.planning/`.** One pattern matching
  `henols/firestarter/issues` and `henols/firestarter_app/issues` across all three checkouts plus
  the wiki clone, excluding only `.planning/` and `.git/`. A markdown-only check would miss a dead
  link in a Click docstring, which is **user-facing `--help` text**. There are zero hits today, so
  it starts green with nothing to grandfather and needs no allowlist.

### Mechanical constraints — recorded, not asked

These follow from prior decisions and measured state. Planning must honour them.

- **NO COMMENTS.** The operator's standing hard rule is zero comments in anything written for this
  project, and a plan cannot override it. This binds the new `wiki-check.yml` grep leg, the YAML
  issue forms, `config.yml` and the `.github/CONTRIBUTING.md` files — **even though the surrounding
  `wiki-check.yml` is dense with comments written by earlier phases.** Do not match the local style
  here; match the rule.
- **The wiki is reached by clone-commit-push.** `https://github.com/henols/firestarter_prom.wiki.git`
  is a real git repository and the only working copy. There is no in-repo `wiki/` source tree, no
  publish script, no PR and no CI gate on the edit (activation decision 5 as reversed).
- **A new wiki page owes two navigation edits or CI goes red.** `Contributing` must be added to
  `_Sidebar.md` **and** linked from `Home.md` in the same push, or `wiki.py links` fails on orphan
  detection and sidebar completeness.
- **Page naming follows Phase 167 D-03:** `Title-Case-With-Hyphens.md`, flat, no subdirectories.
  `Contributing.md` renders as "Contributing".
- **Page opening follows the established shape:** the logo `<p align="left">` block, then `---`,
  then `# Title`. Uniform across all ten live pages.
- **`Contributing` owes a `MIGRATION-TABLE.md` row** if the table's conventions apply to a page
  authored rather than migrated — the table is what the Backlog 999.9 rename sweep greps, and
  Phase 171 D-06 set the precedent that every page's provenance stays answerable from the table
  alone.
- **Sub-repo changes land inside the submodule on
  `gsd/v1.35-documentation-consolidation-wiki-migration`;** meta changes land on the same-named
  branch here. Re-pin both gitlinks before the phase closes — Phase 171 plan 04's pattern.
- **Read the ruleset back from the API, never from the settings page.** The roadmap names this
  explicitly, and names the trap it guards: `henols/firestarter` has a ruleset called `Protect main`
  today whose existence is not compliance.

### Claude's Discretion

- Exact prose of the `Contributing` page, provided it carries gh#9's three statements and its
  cross-repository-change protocol relocated intact, plus D-04's security sentence.
- Exact field lists, dropdown options and `validations: required` choices in the two issue forms.
- Which labels each template pre-applies, drawn from the labels prom already carries
  (`bug`, `enhancement`, `feature`, `dev-test`, `needs:report`).
- Whether `config.yml` also carries `contact_links` (e.g. to the wiki), given `blank_issues_enabled`
  stays true.
- The title marker chosen for D-06's hand-filled fallback, provided it is not `[dev test]`.
- Ruleset naming (`Protect main` is the incumbent and reads correctly), `~DEFAULT_BRANCH` vs a
  literal `main` in `conditions.ref_name.include`, and `required_approving_review_count: 0` — all
  follow the measured incumbent.
- Whether the deletions, the wiki push and the ruleset calls land as one commit or several, subject
  to the usual atomic-commit convention.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase and milestone definition

- `.planning/ROADMAP.md` — the "Phase 172: POLICY — One Tracker, Protected `main`" entry under
  `## Phase Details` (goal, dependency on Phase 170, four success criteria, and the explicit
  ruleset trap in criterion 4); the v1.35 milestone section with its seven activation decisions;
  and the accepted Backlog 999.9 sequencing hazard, which names **169, 170 and 172** as the phases
  whose links will need re-sweeping.
- `.planning/REQUIREMENTS.md` — POLICY-01, POLICY-02, POLICY-03 and LEGACY-01 texts; the scope note
  ("Any product-code change found necessary is filed, not fixed here"); the Out of Scope table's
  `.planning/` exclusion; and the constraint block "Branch protection changes the close procedure".
- `.planning/notes/v135-wiki-only-reversal.md` — why there is no in-repo wiki source tree, what the
  reversal voided, and what survives. Read before assuming any Phase 167 publishing tooling exists.
- `.planning/notes/v135-phases-169-170-executed-ad-hoc.md` — Phases 169 and 170 were executed
  outside the phase machinery; this is the criterion-by-criterion re-check their requirement marks
  rest on, and the provenance of the README text D-03 trims.

### Upstream issues being satisfied

- [`henols/firestarter_prom#6`](https://github.com/henols/firestarter_prom/issues/6) — Backlog
  999.13's source. The authoritative list of what "one tracker, protected main" means, including
  the two extras D-11 declines.
- [`henols/firestarter_prom#9`](https://github.com/henols/firestarter_prom/issues/9) — the
  operator-written "Repository Structure and Contribution Guide". **This is D-01's source text.**
  Its disposition belongs to Phase 173.

### Prior phase decisions still binding

- `.planning/phases/171-stray-the-root-level-documentation-files/171-CONTEXT.md` — D-02 (no security
  statement anywhere, handed forward to this phase — see D-04), D-06 (`MIGRATION-TABLE.md`
  provenance rows), and the "Mechanical constraints" block on wiki push mechanics, page naming and
  submodule branch targets.
- `.planning/phases/167-wiki-bootstrap-in-repo-source-sync-drift-check/167-CONTEXT.md` — D-02 (flat
  page tree), D-03 (`Title-Case-With-Hyphens.md`), D-04 (page name derived from filename), D-11
  (external link-liveness checking declined). D-01 and D-05…D-10 describe the retired in-repo
  publishing model and no longer apply.

### The artifacts this phase edits or creates

- `README.md` — prom's front door, 37 lines. Its "Reporting a problem" section is D-03's subject.
- `firestarter/README.md:73-81` — "Reporting a problem" plus the four "Include:" bullets D-03 moves
  into the bug-report template.
- `firestarter_app/README.md:104-108` — the "Contributing" section D-03 trims.
- `.github/workflows/wiki-check.yml` — D-13's carrier. Already checks out meta, both sub-repos and
  a fresh wiki clone; runs `wiki.py links`, `honest02_truth.py` and `dispatch_mirror.py`.
  **Not registered with Actions** — absent from prom's default branch.
- `.planning/v1.35/MIGRATION-TABLE.md` — the provenance table; also documents the clone-commit-push
  model and the pre-deletion-SHA convention.
- `tools/wiki/wiki.py` — the `links` subcommand: orphan detection, sidebar completeness, internal
  link form, filename legality. Run against the wiki clone before pushing.

### Artifacts this phase must not break

- `firestarter_app/firestarter/submit.py` — `SUBMIT_REPO = "henols/firestarter_prom"` (line 62);
  `build_issue_url` at line 273 constructs the `issues/new?title=&body=` prefill that D-07 protects.
  **Not edited by this phase.**
- `firestarter_app/.github/workflows/release.yml` — fires on push to `main`, auto-commits a version
  bump back to `main` as `github-actions[bot]`. `paths-ignore` includes `.github/**`.
- `firestarter/.github/workflows/build.yml` — same auto-commit pattern below its "PUBLISH BOUNDARY"
  comment, guarded by `if:` conditions naming push-to-main.
- `.github/workflows/catalog-sync-check.yml` — prom's only registered workflow.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- **`.github/workflows/wiki-check.yml`'s existing checkout block** — meta, `firestarter`,
  `firestarter_app` and a fresh wiki clone are all already on disk in that job. D-13's leg is a
  `grep -r` over paths that already exist; no new checkout, no new tooling, no new dependency.
- **prom's existing label set** — `bug`, `enhancement`, `feature`, `dev-test`, `needs:report`,
  `cause:database`, `cause:firmware`, `cause:harness`, `cause:rig`, `chip:validated`,
  `fix:committed`, `fix:released`, `fixed:superseded`, `intermittent`. Templates can pre-apply
  these; unlike the `labels=` query param (which Phase 113 found GitHub drops for filers without
  write access), template-declared labels work for everyone.
- **The community's own title conventions** — real issues already read `[BUG] …`,
  `[Feature Request] …` and `[dev test] <chip> — FAIL (<fingerprint>)`. The templates should adopt
  what people are already typing rather than invent new prefixes.
- **`tools/wiki/wiki.py links --source-dir wiki-clone`** — the ready-made pre-push check for the
  new `Contributing` page: orphan detection, sidebar completeness, link form, filename legality.

### Established Patterns

- **Wiki page shape** — logo block, `---`, `# Title`, body. Uniform across all ten live pages.
- **Navigation is hand-maintained** — `_Sidebar.md` is no longer generated; it is edited by hand and
  checked by `wiki.py links`.
- **Provenance is recorded, never silent** — every page added, moved or removed gets a row in
  `MIGRATION-TABLE.md` (Phase 171 D-06).
- **"Observable only after merge" is recorded as prevention, not remediation** — Phase 171's
  criterion 2 set this precedent for a GitHub surface that cannot be seen from a feature branch.
  D-08 chooses instead to *make* the surfaces observable, which is a departure worth naming.
- **Read GitHub state back from the API, never the UI** — the roadmap mandates it for POLICY-03 and
  supplies the reason.

### Integration Points

- **`firestarter_prom.wiki.git`** — clone, add `Contributing.md`, edit `_Sidebar.md` and `Home.md`,
  push. A third repository, not a submodule; no CI gates the push.
- **The GitHub REST API** — `DELETE /repos/henols/firestarter/rulesets/4998759`, then
  `POST /repos/{owner}/{repo}/rulesets` ×3 from one body, then `GET` ×3 to read back. The
  authenticated token has `admin: true` on all three repos and scopes `gist, read:org, repo, workflow`.
- **Three pull requests into three `main` branches** — each carrying only that repo's `.github/`
  files, opened after the rulesets are active.

### Live state measured 2026-09-01

- **Rulesets:** prom `[]`; `firestarter_app` `[]`; `firestarter` one — id `4998759`, `Protect main`,
  `enforcement: disabled`, `current_user_can_bypass: "never"`, rules `deletion` +
  `non_fast_forward` + `pull_request(0 approvals)`, one `DeployKey` bypass.
- **Deploy keys:** `0` on all three repos, so that bypass grants nothing to anyone.
- **`admin: true`** on all three; GitHub Actions app id **15368**.
- **Repo flags:** all three `default_branch: main`, all public; `has_issues` — prom `true`, both
  sub-repos `false`; `has_wiki` — prom `true`, both sub-repos `false`. All three descriptions set
  and distinct (Phase 169's FRONT-04).
- **Default-branch lag:** `beta` is **733** commits ahead of `main` in prom, **531** in
  `firestarter`, **781** in `firestarter_app`.
- **Registered workflows in prom:** `catalog-sync-check.yml` only. `wiki-check.yml` returns 404 on
  `main`.
- **Dead-tracker links:** 21 total, **all** inside `.planning/`. Zero in the three READMEs, zero in
  the ten wiki pages, zero anywhere else in the three working trees.
- **The wiki holds ten pages plus `_Sidebar.md`:** `Home`, `Install-Beta`, `Testing-Chips`,
  `Programming-Protocols`, `Chip-Database-Fields`, `Pin-Maps`, `Lockable-PROMs`, `Shield-Revisions`,
  `Breaking-Changes`, `Shell-Completion`. `Contributing` would be the eleventh.
- **README lengths:** prom 37, `firestarter` 91, `firestarter_app` 118.
- **No `.github/ISSUE_TEMPLATE/`, no `CONTRIBUTING.md` and no `CODE_OF_CONDUCT.md`** anywhere in the
  three repositories.

</code_context>

<specifics>
## Specific Ideas

- **The operator kept choosing the option that makes the claim literally true rather than
  technically defensible.** Actions-only bypass over an admin bypass, because "no direct push"
  should be true of every person and not just of people who do not exist. Four clauses only, with
  gh#6's extras recorded as non-claims rather than quietly skipped. A guard for LEGACY-01 that is
  demonstrated failing before it is trusted. Read the phase as *make the configuration mean what the
  page says*, and treat any option that satisfies a criterion by argument rather than by
  construction as the wrong one.
- **Two things in this phase are not verifiable inside it, and both must be said rather than
  glossed.** The `github-actions[bot]` bypass is exercised only by a stable release, and a
  `.github`-only merge triggers none — so the bypass ships configured and unproven. And the
  templates only become visible on the New Issue page once the prom PR merges. D-08 buys the second
  one; nothing buys the first, and Phase 173's ledger should carry it.
- **`wiki-check.yml` going live is a bigger event than the leg that prompted it.** Registering the
  workflow makes HONEST-02's clone-and-check and WIKI-05's reachability check run for the first
  time — both shipped inert in Phase 168. The record should credit Phase 168 for writing them and
  Phase 172 for making them run, and the phase should confirm they pass before registering rather
  than discovering it on the first weekly cron.

</specifics>

<deferred>
## Deferred Ideas

- **Required status checks on `main` (gh#6).** Declined by D-11. Needs per-repo check-name pinning
  kept in sync as workflows change, and prom has only one registered workflow to pin. Revisit once
  `wiki-check.yml` and the sub-repo CI are stably registered on the default branches.
- **Required review-thread resolution (gh#6).** Declined by D-11. A one-field addition
  (`required_review_thread_resolution: true`) that changes nothing for a single maintainer, but it
  is outside POLICY-03 and belongs to whoever revisits the ruleset next.
- **GitHub private vulnerability reporting.** Declined by D-04 and, before it, by Phase 171 D-02.
  It is a one-call repo toggle, but it commits the operator to monitoring and responding. The
  natural trigger is the first time someone asks for a private channel.
- **A `henols/.github` default community-health repository.** Would let one `CONTRIBUTING.md`,
  `SECURITY.md` and issue-template set cover all three repos from a single place, replacing D-02's
  three pointer files. Phase 171 D-02 already noted it as a new repository and an operator action.
- **`MIGRATION-TABLE.md` lists two pages that no longer exist** — `Protocol-Flags` and `Protocol-ID`
  are carried as current wiki pages and a fresh clone has neither. Carried forward from Phase 171's
  deferred list, still unfixed, and still worth fixing before the Backlog 999.9 rename sweep greps
  the table.
- **Backlog 999.9's rename sweep will invalidate this phase's links.** Accepted at activation. The
  roadmap names 169, 170 and **172** as the phases needing re-sweeping; keeping every cross-repo
  link in the `Contributing` page and the three `.github/CONTRIBUTING.md` pointers mechanically
  greppable is therefore worth more here than usual.

### Reviewed Todos (not folded)

`todo.match-phase 172` returned **36 todos, 35 matched**, topping out at 0.9 — every one of them on
generic keywords (`firestarter`, `app`, `phase`, `read`, `check`) rather than on subject. Not one
concerns repository policy, issue tracking, templates or branch protection; they are firmware,
host-app, bench-hardware and GSD-tooling items. **None folded.** Two were read closely before being
set aside, because their titles brush this phase's surface without touching its scope:

- *"Add a `dev test` flag that files the issue automatically when the run finishes"* — a host-app
  change to `submit.py`'s flow. Adjacent to D-06's template, but product code, which the milestone
  scope note excludes.
- *"Report the chip's exact database name in `dev test` issues, artifacts, and tests"* — changes the
  body `submit.py` generates, not the template a human fills. Also product code.

</deferred>

---

*Phase: 172-POLICY — One Tracker, Protected `main`*
*Context gathered: 2026-09-01*
