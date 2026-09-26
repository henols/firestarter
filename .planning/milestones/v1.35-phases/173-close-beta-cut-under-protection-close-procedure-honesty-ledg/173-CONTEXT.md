# Phase 173: CLOSE — Beta Cut Under Protection, Close Procedure & Honesty Ledger - Context

**Gathered:** 2026-09-02
**Status:** Ready for planning

<domain>
## Phase Boundary

v1.35's last phase. Prove that the protection Phase 172 added does not break the way this
project actually ships, fix the GSD close procedure those rulesets broke, and close the
milestone with its non-claims written down as plainly as its claims. Two requirements, five
success criteria:

| Criterion | What it asks | Measured state, 2026-09-02 |
|---|---|---|
| **1 (POLICY-04)** | The `beta` lockstep cut demonstrated working under the new rulesets — an actual cut or an equivalent dry run exercising the same paths, **not a reading of the ruleset configuration**. | All three rulesets scope to `conditions.ref_name.include: ["~DEFAULT_BRANCH"]` and every default branch is `main`, so **`beta` carries no ruleset at all**. Both beta workflows auto-commit their version bump onto `beta`, not `main`. The cut's path is clear — but that is a reading, which is what the criterion forbids. |
| **2 (POLICY-05)** | The GSD close procedure updated for PR-only `main` — a documented PR flow or a documented admin bypass — so the next `/gsd-complete-milestone` does not discover the change by failing. | `gsd_run query git.base-branch` returns **`main`**; `.planning/config.json` has no `git.base_branch` key, so tier 1 of the resolver is empty and it falls through to `origin/HEAD`. `complete-milestone.md:775` then does `git checkout main; git merge --squash`, and `ship.md:373` opens PRs `--base main`. **The admin-bypass branch does not exist:** `current_user_can_bypass` is `"never"` on all three rulesets. |
| **3** | An honesty ledger pairing **every** claim with its explicit non-claim. Minimum: relocation is not verification; FUT-W-01…05 are deferred not delivered; HONEST-02 is point-in-time not continuous. | No ledger exists. Phase 172's closing sweep already handed forward 4 non-claims and 3 findings for it to inherit. |
| **4** | Every unfixed finding filed as a backlog item rather than carried as prose, and the 999.9 rename sweep recorded with the phases needing re-sweeping (169, 170, 172). | Highest backlog row is **999.45**. The ruleset/release-path breakage sits in `todos/pending/` because plan 172-09 was forbidden from writing ROADMAP.md; its own text says promotion is the orchestrator's write. |
| **5** | The upstream replies owed on GitHub sent, or explicitly deferred with a reason: gh#7, gh#5, gh#9. | **All four relevant issues are OPEN with ZERO comments** — gh#5, gh#6, gh#7, gh#9. Nothing has been said upstream about any of this milestone's work. `pinnedIssues` on prom is **empty**, so gh#9 is not pinned and never was. |

**In scope:** a ruleset rejection probe against all three repos; two config keys in
`.planning/config.json` plus a CLAUDE.md pointer and a `.planning/notes/` procedure note;
`.planning/v1.35/CLOSE-RECORD.md`; twelve generated per-page provenance footers on the wiki;
one new `tools/wiki/` checker and a `wiki-check.yml` leg (a fourth PR into a protected `main`);
Backlog 999.46 plus the criterion-4 sweep; four drafted upstream replies behind a blocking
wording review; and — only on explicit operator authorization — the full beta lockstep cut.

**Out of scope — settled, not open questions:**

- **No product code, and no workflow code.** REQUIREMENTS.md's scope note files rather than
  fixes. This binds `firestarter_app/.github/workflows/release.yml` and
  `firestarter/.github/workflows/build.yml` even though they are the files 999.46 is about, and
  it binds `firestarter_app/tools/build_db.py` (Backlog 999.45, still dirty in the tree).
- **No new ruleset, and no amendment to the three that exist.** POLICY-03 is complete and
  scoped to `main`. Adding an admin bypass to reach POLICY-05's second branch would falsify
  Phase 172's claim that "no direct push" is literally true of every person.
- **No new documentation content.** Activation decision 4 is relocate-and-correct-only;
  FUT-W-01…05 stay deferred.
- **`.planning/` historical records are not swept.** `.planning/`→`.planning/` citations are
  historical-by-intent.
- **Backlog 999.9's rename** is not performed here; only recorded.

</domain>

<decisions>
## Implementation Decisions

### POLICY-04 — demonstrating the beta cut

- **D-01: a rejection probe runs inside the phase; the real cut waits for explicit operator authorization.** Two separate deliverables. The probe is evidence that costs nothing
  outward-facing and can execute unattended; the cut is the close's terminal step and is
  outward-facing, so it stays gated as every outward-facing step has since v1.21.
  Rejected: the real cut unconditionally (v1.34's CLOSE-04 shows the operator may well
  authorize it, but that was an in-the-moment decision and must not be assumed twice);
  probe only (leaves the milestone closing with no cut at all); a scratch-repo rehearsal
  (proves things about a copy — and Phase 172 already learned these repos behave differently
  from the general case, the Actions bypass 422'ing on personal-account ownership).

- **D-02: the probe's shape is fixed, and it cannot include a beta-shaped push.** Any push to
  `beta` fires `beta-release.yml` / `beta-build.yml` and cuts the pre-release pair — there is
  no rehearsal shape for that path, it either happens or it does not. So the probe is: an
  attempted direct push to each protected `main` (expected rejected), plus an accepted push to
  an unprotected ref, proving the ruleset is scoped to the default branch and not the whole
  repository. All three repositories, following Phase 172's three-way-identical pattern rather
  than one representative.
  **The attempted push uses an empty commit (`git commit --allow-empty`).** If the ruleset
  unexpectedly fails to block it, the damage is a no-op rather than content on a protected
  branch that `non_fast_forward` + `deletion` then make hard to remove.
  **`git push --dry-run` is NOT acceptable evidence** — it negotiates but sends no pack, so
  GitHub's receive-stage ruleset evaluation never fires; it would report success and prove
  nothing. That is precisely the "reading of the ruleset configuration" criterion 1 rejects.

- **D-03: if the cut is not authorized before the close, POLICY-04 is marked complete on the probe, with the missing half stated as a ledger non-claim.** Criterion 1's own words allow
  it — "an actual cut **or** an equivalent dry run that exercises the same paths". The ledger
  row then reads: v1.35 claims the rulesets do not block a push to an unprotected ref and do
  block a direct push to `main`; it does **not** claim a beta lockstep cut was performed under
  them.
  Rejected: leaving POLICY-04 PENDING and closing with an open requirement (v1.34's shape for
  NOT-RUN phases, but heavier than a criterion that already permits the dry run needs);
  recording it as a deviation like v1.34's CLOSE-04 (same objection).

- **D-04: when authorized, the cut is the FULL lockstep — v1.22's recipe with v1.30's PR posture.** Pull requests to `beta` in all three repositories, CI cuts the matched pair, then
  **manually dispatch `publish.yml`** so the app beta actually reaches PyPI, verify both
  channels from a clean venv, and tag meta `v1.35`. The PyPI dispatch is not optional detail:
  it is manual, and 6 of 13 historical app betas never reached PyPI, so skipping it leaves
  `pip install --pre` resolving a stale version — the exact channel drift recorded at the v1.21
  close.
  — **Reversibility:** one-way — a published GitHub prerelease and a PyPI upload cannot be
  unpublished without an outward-facing deletion, and this project has declined that before
  (the stray `3.0.0b12` prereleases stay public by v1.22 D-05).
  Rejected: cut-only without the PyPI dispatch or the meta tag (v1.34's minimal shape, which
  buys the channel disagreement); a direct `--no-ff` merge and push with no PR (faster, avoids
  the v1.30 squash-ancestry trap, but leaves no PR record and diverges from the flow POLICY-05
  is simultaneously documenting).

- **D-05: the rulesets' breakage of the STABLE release path is filed as Backlog 999.46 with a recommended remedy named, not as a menu.** Both sub-repos auto-commit a version bump onto
  `main` from CI using the default `GITHUB_TOKEN`, and a `DeployKey` bypass does not cover a
  `GITHUB_TOKEN`-authenticated push. The recommended remedy is the todo's **option 2** — move
  the version bump off `main` (bump on `beta`, or a tag-triggered release with no push back) —
  because it removes the conflict rather than carving an exception through it. The other two
  candidates are recorded with the reasons they are not recommended: re-enabling the
  commented-out `PERSONAL_ACCESS_TOKEN` does not clearly work (`current_user_can_bypass` is
  `never`, so a PAT pushing as `henols` meets the same `pull_request` rule), and registering a
  deploy key relies on `actor_id: null` conferring bypass on *any* deploy key.
  **No workflow file is edited.**

### POLICY-05 — the close procedure

- **D-06: the procedure is fixed by CONFIGURATION first, prose second.** Two first-class
  tier-1 keys in `.planning/config.json`: `git.base_branch: "beta"` so
  `/gsd-complete-milestone` stops merging onto `main` locally and `/gsd-ship` stops targeting
  it — both then point at `beta`, which is what this project has actually done since v1.30 —
  and `git.protected_branches: ["main"]`, which declares in config what is now true on GitHub.
  Verified by read-back (`git.base-branch` → `beta`, `--is-protected main` → `true`), not
  merely set.
  **Measured, so the cost is known rather than feared:** `baseBranch` is always folded into
  `protectedBranches` (`git-base-branch.cjs:305`), so `beta` becomes protected too — but both
  consumers, `ship.md:78` and `execute-phase/steps/protected-branch.md`, only **warn and
  continue**; neither refuses, and the second applies to `branching_strategy: none` while this
  project is `milestone`. The repoint therefore cannot break the close.
  Rejected: prose only (`git.base-branch` would keep resolving `main`, so POLICY-05 would be
  satisfied by a document the tooling ignores — the "satisfied by argument rather than by
  construction" shape Phase 172 rejected at every turn); config only, with no prose (leaves
  the stable route to `main`, and the `current_user_can_bypass: never` fact, documented
  nowhere); amending the vendored `.claude/gsd-core/` workflows (`/gsd-update` overwrites the
  whole tree, so the fix silently disappears — and it is third-party tooling, not this
  project's code).

- **D-07: a few lines in meta's `CLAUDE.md`, pointing at `.planning/notes/v135-close-procedure-under-protection.md` for the mechanics.** POLICY-05's
  stated purpose is that the next `/gsd-complete-milestone` "does not discover the change by
  failing", so being *read* is the requirement. `CLAUDE.md` is auto-loaded into every session
  in this repo, so the agent running the next close reads it whether or not it goes looking.
  Meta's `CLAUDE.md` only — the close runs here, not in a submodule.
  Rejected: `.planning/notes/` alone (the established convention, but nothing auto-loads it —
  a future close agent finds it only if something points it there, which is the failure mode
  the criterion names); `PROJECT.md` §Context (414 KB, read at budgeted depth, so landing
  there is no guarantee of being seen); the wiki (internal maintainer procedure for an agent
  would be the one wiki page with no human reader, and it fails the read-by-the-tooling
  purpose entirely).

- **D-08: the note covers the stable-release route to `main` and states plainly that it is currently blocked end to end.** A pull request is the only route — `current_user_can_bypass`
  is `never` on all three, so no person including the operator can bypass — and the
  version-bump step then fails per 999.46. Decided from the milestone's established pattern of
  choosing the literally-true statement over the technically-defensible one, not asked.

### The honesty ledger

- **D-09: the full ledger is internal, at `.planning/v1.35/CLOSE-RECORD.md`, and each migrated wiki page carries a generated per-page provenance footer.** One line at the foot of each
  page: relocated from `<repo>/<source path>`, content unchanged, not re-verified.
  `.planning/v1.35/MIGRATION-TABLE.md` already holds every field needed — source repo, source path,
  wiki page, rendered title, pre-deletion SHA, phase — so the footer is **generated from that
  table, not authored twelve times**. This puts the milestone's central non-claim where the
  reader actually is; HONEST-02's stamp reaches only the DB-backed pages, and "relocation is
  not verification" is a claim about all twelve.
  — **Reversibility:** costly — undoing means twelve further wiki edits by clone-commit-push,
  and the footers will be cited by the new checker leg once it is registered.
  Rejected: internal only (v1.34's precedent and the cheapest option, but the milestone's
  central non-claim would be legible only to whoever reads `.planning/` — not the readers the
  wiki was built for); one `Documentation-Status` page (one edit instead of twelve, but it
  owes two navigation edits or `wiki.py links` fails on orphan detection, and a reader on a
  chip page never sees it); a line on `Home.md` alone (`Home` is the page people leave first —
  the disclosure would sit furthest from the pages it qualifies).

- **D-10: the footers get a mechanical guard — a new `tools/wiki/` checker and a `wiki-check.yml` leg, demonstrated RED before it is trusted.** The checker asserts every
  `MIGRATION-TABLE.md` row resolves to a live wiki page whose footer matches its source path
  and pre-deletion SHA. Planted-failure-first, per Phase 172 D-14's bar and REQUIREMENTS.md's
  bar for HONEST-02. `wiki-check.yml` is registered with Actions as of Phase 172 and already
  clones the wiki plus both sub-repos, so this is a leg, not new infrastructure.
  **It will go RED on two rows the moment it runs** — `Protocol-Flags` and `Protocol-ID` are
  carried in the table as current wiki pages and a fresh clone has neither. That defect has
  survived being noticed and deferred in both Phase 171 and Phase 172; unlike 999.45 it is in
  `tools/`, not product code, so this phase may fix it.
  — **Reversibility:** costly — the leg reaches prom's default branch by pull request, and
  removing it later needs another PR into a protected branch.
  Rejected: static text with no guard (nothing would detect a footer removed or drifted by a
  careless wiki edit, and wiki edits have no review of any kind — the shape HONEST-02 exists
  to avoid); guarding only the table's row-to-page resolution (fixes the known defect but
  leaves the thing the reader actually sees as the thing nothing checks).

- **D-11: one consolidated, comprehensive ledger table — not v1.34's curated ten rows.**
  Criterion 3's own words are "pairs **every** claim this milestone makes with its explicit
  non-claim". The table carries criterion 3's three named minimums, the four non-claims and
  three findings Phase 172's closing sweep handed forward, POLICY-04's own non-claim per D-03,
  and what Phases 167–171 left open — including Phase 169's **FRONT-02, which the operator
  declined outright** rather than met. Decided from the criterion's wording, not asked.

### Upstream replies

- **D-12: reply on all four issues; close gh#7 and gh#6; keep gh#5 open; keep gh#9 open and PIN it.** Per issue:
  - **gh#7** — reply and close. Its generated-site premise was rejected at the 2026-07-27
    backlog review, the Wiki was chosen, and its content requirements live on in gh#5. Leaving
    it open presents a rejected premise as a live feature request.
  - **gh#5** — reply, stays open, as the surviving upstream tracker for FUT-W-01…05. Closing
    it would leave the compatibility matrix, family pages, algorithm pages and tutorials
    tracked only in `.planning/`, invisible outside this repo — the opposite of what
    "deferred, not delivered" means.
  - **gh#9** — reply, stays open, and **gets pinned.** Criterion 5 calls it "the pinned
    orientation issue" and 999.13's note says it "stays open on GitHub as the pinned
    orientation issue", but prom's `pinnedIssues` set is **empty**: pinning was always
    intended and never done. One GraphQL call.
  - **gh#6** — reply and close. **A deliberate widening: criterion 5 does not list it.**
    It is the issue this milestone most directly delivered (999.13 promoted "in full"), and
    D-11's two declines — required status checks, required review-thread resolution — must be
    named in the reply rather than left as silent gaps, or they read as quietly skipped.

- **D-13: all four replies are drafted into the phase record, reviewed by the operator, and only then posted.** Exactly v1.22 D-02's precedent — that close recorded a "blocking wording
  review" before its outward-facing step, and it is the only pattern this project has for text
  going out under the operator's name. Criterion 5's "sent" is then met with a record of what
  was approved.
  — **Reversibility:** one-way for the closes and the posts — a comment on a public tracker is
  indexed, and `updatedAt` bumps on creation rather than on a body edit, so a correction reads
  as a second statement rather than a replacement.
  Rejected: posting directly (the content is measured fact, but there is no precedent here for
  unreviewed community-facing text, and a wrong link or mis-stated decline is public before
  the operator sees it); drafting and deferring the posting entirely (criterion 5's own escape
  hatch, but it meets the criterion with a deferral rather than the thing it asks for).

### Mechanical constraints — recorded, not asked

These follow from prior decisions and measured state. Planning must honour them.

- **NO COMMENTS.** The operator's standing hard rule is zero comments in anything written for
  this project, and a plan cannot override it. This binds the new `tools/wiki/` checker, the
  `wiki-check.yml` leg, and the two new `.planning/config.json` keys — **even though the
  surrounding `wiki-check.yml` is dense with comments written by earlier phases.** Do not match
  the local style; match the rule.
- **`grep` on PATH in this devcontainer is ugrep and honours `.gitignore`.** Plan 172-09
  measured 0 matches under ugrep against 38 under GNU grep over identical paths. Any gate
  evidence uses `/usr/bin/grep`, and a repository-wide scan is scoped to `git ls-files` so
  gitignored scratch cannot produce a false RED.
- **`tools/wiki/selftest.sh` mutates Phase 168's evidence files.** `git checkout --` them after
  every run.
- **The wiki is reached by clone-commit-push.** `https://github.com/henols/firestarter_prom.wiki.git`
  is the only working copy; no in-repo source tree, no publish script, no PR, no CI gate on the
  edit.
- **A wiki edit that adds or removes a page owes two navigation edits** — `_Sidebar.md` and
  `Home.md` — or `wiki.py links` fails on orphan detection and sidebar completeness. The
  footers add no pages, so this binds only if a page is added or the two stale rows are
  resolved by deletion.
- **Read GitHub state back from the API, never the settings page.** The standing rule from
  Phase 172, and the reason is on record: `henols/firestarter` had a ruleset called
  `Protect main` whose existence was not compliance.
- **Use `git cherry`, never `--is-ancestor`.** The v1.30 squash-merge made ancestry lie. And
  local `beta` in every repository here is stale enough to poison the check — recreate it from
  `origin/beta` first. Meta's `origin/beta` tip is a PR merge commit, so the close tail cannot
  fast-forward onto it; it must be merged.
- **Sub-repo changes land inside the submodule on
  `gsd/v1.35-documentation-consolidation-wiki-migration`;** meta changes land on the
  same-named branch here. Re-pin both gitlinks before the phase closes, and prove equality per
  submodule — Phase 171 plan 04's and Phase 172 plan 09's pattern.
- **`firestarter_app` is not porcelain-clean** — `tools/build_db.py` carries one unstaged
  modification (Backlog 999.45), product source this milestone may not touch. Any verify leg
  asserting an empty `git status --porcelain` on that submodule will fail; it has already been
  documented as a non-fix twice, by 172-07 and 172-09.
- **`ROADMAP.md` writes belong to the orchestrator.** `roadmap.update-plan-progress`
  overwrites positionally and has clobbered an unrelated phase's dependency table. v1.35's
  ROADMAP was hand-authored and must never be regenerated. This is why the 999.46 promotion is
  the orchestrator's write, not an executor's.
- **`.planning/config.json` is edited by hand**, not through a GSD verb — the requirements and
  roadmap verbs reformat whole files.
- **Backlog 999.9 will invalidate every link this phase writes.** Accepted at activation. The
  criterion-4 record names 169, 170 and 172 as the phases needing re-sweeping; this phase's own
  links (the four upstream replies, the twelve footers, the procedure note) join that set and
  should be kept mechanically greppable.

### Claude's Discretion

- Exact prose of the four upstream replies, subject to D-13's blocking review, provided each
  states what was delivered, what was declined and why, and where the surviving tracker is.
- The provenance footer's exact wording and formatting, provided it names the source repo and
  path, states the content is unchanged, and states it was not re-verified.
- The new checker's implementation language and file name under `tools/wiki/`, and whether it
  becomes a `wiki.py` subcommand or a standalone script beside `honest02_truth.py` and
  `dispatch_mirror.py`.
- Whether the two stale `MIGRATION-TABLE.md` rows are resolved by correcting the table or by
  restoring the pages, and whether that lands as a fix here or a filed row under criterion 4.
- The ledger table's row ordering, row identifiers (v1.34 used `H-1`…`H-10`), and section
  layout within `.planning/v1.35/CLOSE-RECORD.md`.
- Whether the probe, the config repoint, the ledger and the replies land as one commit or
  several, subject to the usual atomic-commit convention.
- Which unfixed findings beyond the named ones warrant their own backlog row under criterion 4
  versus a line in an existing row.

### Folded Todos

- **`.planning/todos/pending/2026-09-02-rulesets-block-stable-release-version-bump.md`** —
  "The v1.35 `Protect main` rulesets block the stable-release version bump in both
  sub-repositories." Filed by plan 172-09 as a todo rather than a `999.x` row because that plan
  was forbidden from writing `ROADMAP.md`, and its own text says promotion is the
  orchestrator's write. Criterion 4 explicitly owes it a backlog row. Folded as **D-05**, to be
  promoted to **Backlog 999.46** with the off-`main` bump named as the recommended remedy. The
  todo file is removed once the row exists.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase and milestone definition

- `.planning/ROADMAP.md` — the "Phase 173 (close): CLOSE — Beta Cut Under Protection, Close
  Procedure & Honesty Ledger" entry under `## Phase Details` (goal, dependency on 167–172, and
  all five success criteria verbatim); the v1.35 milestone section with its seven activation
  decisions, the model reversal, and the accepted Backlog 999.9 sequencing hazard naming
  **169, 170 and 172**; the v1.35 phase checklist, where Phases 169 and 170 record ad-hoc
  execution and **Phase 172's box is still unchecked despite all four of its requirements being
  marked complete** — a discrepancy this phase must resolve. **Hand-authored: never regenerate.**
- `.planning/REQUIREMENTS.md` — POLICY-04 and POLICY-05 texts; the constraint block "Branch
  protection changes the close procedure" (lines 118–120), which is why both requirements
  exist; the scope note filing rather than fixing product code; the Out of Scope table's
  `.planning/` exclusion; WIKI-04's withdrawal note and what it says HONEST-02 must therefore
  carry; and the FUT-W-01…05 list, which is what gh#5 stays open to track.
- `.planning/notes/v135-wiki-only-reversal.md` — why there is no in-repo wiki source tree, what
  the reversal voided, and what survives. Read before assuming any Phase 167 publishing tooling
  exists.
- `.planning/notes/v135-phases-169-170-executed-ad-hoc.md` — the criterion-by-criterion re-check
  Phases 169 and 170's requirement marks rest on, including **FRONT-02 being NOT met by operator
  decision**, which D-11's ledger must carry.

### The close precedent this phase follows

- `.planning/v1.34/CLOSE-RECORD.md` — the shape D-09 and D-11 build on. §5 is the claim/non-claim
  ledger (`H-1`…`H-10`), §6 is criterion-4's "filed, not carried as prose" pattern, and §7 is
  the deviation record D-03 explicitly declined to reuse.
- `.planning/MILESTONES.md` — the release-state paragraphs for v1.14, v1.20, v1.21, v1.22 and
  v1.23 define what a "lockstep cut" actually is and what past closes did and did not perform.
  v1.22's is D-04's recipe; v1.23's records the blocking wording review D-13 follows.

### Phase 172's handoff — the inputs this phase inherits

- `.planning/phases/172-policy-one-tracker-protected-main/evidence/172-09-closing-sweep.txt` —
  **the single most important input.** Four explicit non-claims and three carried findings,
  written so this phase's ledger inherits them stated rather than rediscovered. NON-CLAIM 1 is
  the Actions-bypass 422 and the `actor_id: null` residual; NON-CLAIM 2 is D-11's two declines;
  NON-CLAIM 3 is `Wiki check` registered with zero runs; FINDING A is what becomes 999.46.
- `.planning/phases/172-policy-one-tracker-protected-main/172-09-SUMMARY.md` — the ugrep-vs-GNU-grep
  scanner hazard measured both ways, the gitlink per-submodule equality pattern, and the four
  pre-existing worktrees that must survive any cleanup.
- `.planning/phases/172-policy-one-tracker-protected-main/evidence/172-05-actions-bypass-probe.txt` —
  the D-09 revision to `DeployKey:null:always` and the release-path breakage recorded **as
  breakage** at the moment the decision was taken, not discovered afterwards.
- `.planning/phases/172-policy-one-tracker-protected-main/evidence/172-06-ruleset-readback.txt` —
  the three-way normalised ruleset equality, and id `4998759` proven amended rather than
  recreated.
- `.planning/phases/172-policy-one-tracker-protected-main/172-CONTEXT.md` — D-09, D-11 and D-12
  (bypass actor, four clauses only, rulesets created last) are the decisions POLICY-04 and
  POLICY-05 respond to. Its "Mechanical constraints" block still binds.
- `.planning/todos/pending/2026-09-02-rulesets-block-stable-release-version-bump.md` — folded as
  D-05. Carries the three candidate remedies and the reason the obvious one is not obviously
  right.

### The GSD machinery POLICY-05 fixes

- `.claude/gsd-core/bin/lib/git-base-branch.cjs` — the precedence ladder in the header comment
  (tier 1 is `git.base_branch` from `.planning/config.json`); `resolveProtectedBranchStatus` at
  **:302**, where `:305` folds `baseBranch` into `protectedBranches`.
- `.claude/gsd-core/workflows/complete-milestone.md` — **:734** resolves `BASE_BRANCH`; **:775**
  and **:804** do `git checkout ${BASE_BRANCH}` before the squash or history merge. This is the
  step POLICY-05 exists for.
- `.claude/gsd-core/workflows/complete-milestone/steps/git-tag.md` — **:26**, `git push origin
  v[X.Y]`. The only push `complete-milestone` performs.
- `.claude/gsd-core/workflows/ship.md` — **:78** the advisory `--is-protected` check; **:316**
  `RANGE_BASE` anchored on `merge-base ${BASE_BRANCH} HEAD`; **:373** `gh pr create --base
  ${BASE_BRANCH}`.
- `.claude/gsd-core/workflows/execute-phase/steps/protected-branch.md` — the second
  `--is-protected` consumer. Warns and continues, and applies to `branching_strategy: none`
  only.
- `.claude/gsd-core/references/planning-config.md` — the documented config surface for
  `git.base_branch` and `git.protected_branches`.
- `.planning/config.json` — currently has `git.branching_strategy: "milestone"` and **no**
  `base_branch` or `protected_branches`. D-06's edit target.

### The wiki surface D-09 and D-10 touch

- `.planning/v1.35/MIGRATION-TABLE.md` — the provenance table the footers are generated from, and
  what the 999.9 rename sweep greps. Its header documents the pre-deletion-SHA convention and
  the clone-commit-push model. **Carries two stale rows** (`Protocol-Flags`, `Protocol-ID`).
- `.github/workflows/wiki-check.yml` — D-10's carrier. Registered with Actions as of Phase 172
  and **has zero runs**; already checks out meta, both sub-repos and a fresh wiki clone, and
  runs `wiki.py links`, `honest02_truth.py` and `dispatch_mirror.py`. Reaching it needs a pull
  request into a now-protected `main`.
- `tools/wiki/wiki.py` — the `links` subcommand: orphan detection, sidebar completeness,
  internal link form, filename legality. The pre-push check for any wiki edit.
- `tools/wiki/selftest.sh` — mutates Phase 168's evidence; `git checkout --` after every run.

### Upstream issues criterion 5 owes

- [`henols/firestarter_prom#5`](https://github.com/henols/firestarter_prom/issues/5) "Move
  documentation" — Backlog 999.12's source. Stays open as the FUT-W-01…05 tracker.
- [`henols/firestarter_prom#6`](https://github.com/henols/firestarter_prom/issues/6) "Protect
  main branches and centralize issue tracking" — Backlog 999.13's source; the authoritative
  list of what "one tracker, protected main" means, **including the two extras D-11 declined**.
  Not named by criterion 5; D-12 widens to include it.
- [`henols/firestarter_prom#7`](https://github.com/henols/firestarter_prom/issues/7) "Improve
  Firestarter discoverability with generated documentation" — the retired 999.14. Premise
  rejected at the 2026-07-27 backlog review.
- [`henols/firestarter_prom#9`](https://github.com/henols/firestarter_prom/issues/9)
  "Repository Structure and Contribution Guide" — Phase 172 D-01's source text, relocated to
  the wiki `Contributing` page. **Not pinned, contrary to both criterion 5 and 999.13's note.**

### Artifacts this phase must not break

- `firestarter_app/.github/workflows/release.yml` — `:2-5` trigger on push to `main`; `:32-35`
  `git-auto-commit-action` with its PAT override **commented out**; `:37-43` the `Release` step
  which *does* pass the PAT. 999.46's subject. **Not edited.**
- `firestarter/.github/workflows/build.yml` — `:34` trigger `['**', '!beta']`; `:182-183` the
  same auto-commit gated to push-to-`main` below the `PUBLISH BOUNDARY`; `:199-200` the
  `action-gh-release` publish depending on that push. **Not edited.**
- `firestarter_app/.github/workflows/beta-release.yml` and
  `firestarter/.github/workflows/beta-build.yml` — the beta cut's carriers. Their `on:` comments
  state the design intent outright: **every merge to beta cuts a pre-release**, and the
  `paths-ignore` lists were deliberately deleted. Their auto-commit targets `beta`. **Not
  edited** — read to confirm the cut's path, never modified.
- `firestarter_app/.github/workflows/publish.yml` — the manual dispatch D-04 requires for PyPI.
- `firestarter_app/tools/build_db.py` — one unstaged modification, Backlog 999.45. Product
  source. **Not touched, not reverted, not committed.**

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- **`wiki-check.yml`'s existing checkout block** — meta, `firestarter`, `firestarter_app` and a
  fresh wiki clone are all already on disk in that job. D-10's leg needs no new checkout, no new
  tooling and no new dependency. Registration already happened in Phase 172; this is the first
  change to a live, registered workflow.
- **`MIGRATION-TABLE.md` as a data source, not just a record** — every field the footer needs is
  already there and already machine-read (`honest02_truth.py`'s checker reads the source side
  with `git -C <subrepo> show <sha>:doc/<file>`). D-09's footers are a projection of existing
  data, which is why generating them beats authoring twelve.
- **`honest02_truth.py` and `dispatch_mirror.py` as templates** — the new checker's shape,
  argument convention and exit-code contract are already established beside it.
- **`git.base_branch` / `git.protected_branches`** — POLICY-05's fix is two lines of existing,
  documented, tier-1 configuration rather than any new mechanism. This is the phase's biggest
  reuse win and the reason D-06 chose construction over prose.
- **v1.34's `CLOSE-RECORD.md`** — a working ledger structure to copy rather than invent:
  numbered claim/non-claim rows, a filed-not-carried table, and a deviation section.
- **Plan 172-09's GNU-grep-scoped-to-`git ls-files` pattern** — the scanner shape that survives
  the ugrep hazard in both directions. Reuse verbatim for any criterion-4 sweep.

### Established Patterns

- **Demonstrated failing before it is trusted** — HONEST-02's bar in REQUIREMENTS.md, Phase 172
  D-14's for the LEGACY-01 leg, and now D-10's for the footer checker. A check never seen to
  fail is not evidence.
- **Read GitHub state back from the API, never the UI** — and Phase 172 supplies the reason: a
  ruleset named `Protect main` existed whose existence was not compliance.
- **The evidence sweep is written BEFORE any checkbox is flipped** — plan 172-09's T-172-35
  discharge, and this project's known failure mode of executors marking multi-plan requirements
  complete ahead of their evidence.
- **Non-claims are recorded beside the marks, not absorbed into them** — Phase 172's closing
  sweep is the model, and D-11 is its continuation at milestone scale.
- **"Observable only after merge" is recorded as prevention, not remediation** — Phase 171's
  criterion 2. Relevant to D-10's leg, whose behaviour in CI cannot be observed from a feature
  branch.
- **Outward-facing steps are operator-gated** — standing since v1.21, and the reason D-01 splits
  the probe from the cut and D-13 puts a blocking review before four public comments.
- **Provenance is recorded, never silent** — every page added, moved or removed gets a
  `MIGRATION-TABLE.md` row (Phase 171 D-06). D-09 extends the same principle onto the page
  itself.

### Integration Points

- **The GitHub REST API** — `POST /repos/{owner}/{repo}/rulesets` read-backs for the probe's
  before/after, and the push attempts themselves go over git, not the API.
- **The GitHub GraphQL API** — `pinnedIssues` for the D-12 read-back, and the mutation that pins
  gh#9. REST has no pinned-issue endpoint.
- **`firestarter_prom.wiki.git`** — clone, add twelve footers, push. A third repository, not a
  submodule; no CI gates the push.
- **A fourth pull request into a protected `main`** — carrying `wiki-check.yml`'s new leg. Both
  a cost and, per D-10, a second live exercise of the flow POLICY-05 documents; record it as
  POLICY-05 evidence rather than as overhead.
- **`.planning/config.json`** — hand-edited, then read back through
  `gsd_run query git.base-branch`.

### Live state measured 2026-09-02

- **Rulesets:** all three `enforcement: active`, `current_user_can_bypass: "never"`, conditions
  `ref_name.include: ["~DEFAULT_BRANCH"]` / `exclude: []`, rules `deletion` +
  `non_fast_forward` + `pull_request`, one bypass actor `{actor_id: null, actor_type:
  "DeployKey", bypass_mode: "always"}`. Ids: prom `22043478`, `firestarter` `4998759`,
  `firestarter_app` `22046179`.
- **`beta` is unprotected in all three repositories** — it appears in no ruleset condition.
- **Both beta workflows auto-commit onto `beta`**, not `main`, so the cut's own CI is clear of
  the rulesets too.
- **`gsd_run query git.base-branch`** → `main`. `origin/HEAD` → `refs/remotes/origin/main`.
  `.planning/config.json` has no `git.base_branch`.
- **prom `pinnedIssues`** → empty. gh#5, gh#6, gh#7, gh#9 all OPEN, all **zero comments**.
- **Highest backlog row** → 999.45. Next free → **999.46**.
- **`todo.match-phase 173`** → 35 matches of 37 pending todos; 34 on generic keywords only.
- **`MIGRATION-TABLE.md`** → 21 data rows; two (`Protocol-Flags`, `Protocol-ID`) name wiki pages
  a fresh clone does not have.
- **`Wiki check`** → registered with Actions, **zero runs**; first fire is the weekly cron or a
  manual `workflow_dispatch`.
- **Current branch** → `gsd/v1.35-documentation-consolidation-wiki-migration` in meta;
  `firestarter_app` working tree carries one unstaged `tools/build_db.py` modification.

</code_context>

<specifics>
## Specific Ideas

- **The operator asked what *I* wanted to discuss before choosing any area.** That is worth
  recording as a working instruction, not a pleasantry: the useful contribution here was
  separating what genuinely needed a decision from what precedent already settled, and then
  deciding the latter rather than asking. Six items in this discussion were decided that way
  and are marked as such. Downstream agents should do the same — where a prior phase, a measured
  fact, or the criterion's own wording settles a question, settle it and say so.
- **Every one of the six offered choices went to the option that makes the claim literally
  true rather than technically defensible** — construction over prose for POLICY-05, an
  auto-loaded `CLAUDE.md` over a convention-correct note nobody reads, per-page footers over one
  internal record, a guarded footer over static text, a widening to gh#6 over criterion-5
  literalism, and a blocking review over convenience. This is the same pattern Phase 172
  recorded. **Treat any option that satisfies a criterion by argument rather than by
  construction as the wrong one**, and expect to be asked why an easier route was taken.
- **Three things the roadmap asserts turned out not to be true, and all three were found by
  measuring rather than reading.** POLICY-05's "documented admin bypass" branch cannot be
  written because no bypass exists. Criterion 5 and 999.13 both call gh#9 "pinned" and nothing
  on prom is pinned. `MIGRATION-TABLE.md` lists two pages that do not exist. A close phase's job
  includes checking its own criteria against reality before satisfying them — the criteria are
  not themselves evidence.
- **`--dry-run` is the shape of trap this criterion is about.** It would have produced a green
  line, no rejection, and a false claim that the rulesets were exercised. The general form:
  when the criterion says "demonstrated, not read", check that the mechanism under test is
  actually reached, not merely addressed. The same reasoning is why the empty-commit choice
  matters and why the probe cannot include a beta push.

</specifics>

<deferred>
## Deferred Ideas

- **A ruleset on `beta`.** POLICY-03 is complete and scoped to `main`; protecting `beta` is a
  new capability and its own decision. Note that D-06 makes GSD *treat* `beta` as protected
  locally while GitHub does not — an asymmetry worth resolving whenever someone revisits the
  rulesets.
- **Required status checks on `main`** (gh#6). Declined by Phase 172 D-11, carried here.
  Revisit once `wiki-check.yml` and the sub-repo CI are stably registered on the default
  branches — D-10 moves that slightly closer by touching the workflow again.
- **Required review-thread resolution on `main`** (gh#6). Declined by Phase 172 D-11. A
  one-field addition that changes nothing for a single maintainer.
- **GitHub private vulnerability reporting.** Declined by Phase 172 D-04 and Phase 171 D-02. A
  one-call toggle that commits the operator to monitoring and responding; the natural trigger is
  the first request for a private channel.
- **A `henols/.github` default community-health repository.** Would let one `CONTRIBUTING.md`,
  `SECURITY.md` and issue-template set cover all three repos, replacing Phase 172 D-02's three
  pointer files. A new repository and an operator action.
- **Fixing the release path itself** — the workflow rework 999.46 describes. Out of scope by the
  milestone's scope note; D-05 files it with a recommendation instead.
- **FUT-W-01…05** — the compatibility matrix, per-family pages, algorithm and command-set pages,
  task-oriented tutorials, and repository metadata keywords. Deferred at activation by decision
  4, tracked against Backlog 999.12 and, per D-12, upstream on gh#5.
- **Backlog 999.9's rename sweep.** Accepted at activation as an unsolved sequencing hazard.
  This phase records it with 169/170/172 named, and adds its own outputs to the set needing
  re-sweeping.

### Reviewed Todos (not folded)

`todo.match-phase 173` returned **35 matches out of 37 pending todos**, every one but one
scoring on generic keywords (`gsd`, `phase`, `main`, `check`, `state`) rather than on subject —
firmware, host-app, bench-hardware and GSD-tooling items. **One folded** (see Folded Todos);
the other 34 set aside, the same disposition Phase 172 reached on the same scanner behaviour.
Two were read closely before being set aside because their titles brush this phase's surface:

- *"Strip residual GSD provenance comments from product source (operator hard rule)"* — matched
  on `gsd` and `phase`. Product source, which this milestone may not touch; and the standing
  no-comments rule is already carried here as a mechanical constraint rather than as work.
- *"Record gate superlinear on STATE.md single line"* — GSD tooling, and relevant to any record
  gate this phase writes, but a tooling defect rather than phase scope. Carried as a known
  hazard: the record gate needs 300s against STATE.md's 52k-character line, and an rc=124 reads
  like a RED.

</deferred>

---

*Phase: 173-CLOSE — Beta Cut Under Protection, Close Procedure & Honesty Ledger*
*Context gathered: 2026-09-02*
