# Phase 173: CLOSE — Beta Cut Under Protection, Close Procedure & Honesty Ledger - Research

**Researched:** 2026-09-02
**Domain:** GSD close machinery, GitHub repository rulesets + push semantics, `tools/wiki/` checker conventions, milestone close records
**Confidence:** HIGH

> **Research posture:** every GitHub call in this session was a READ (`gh api` GET, `gh pr view`,
> `gh release list`, `git clone`, `git fetch`). Nothing was pushed, posted, closed, pinned, created
> or deleted. Two write-shaped probes were run **entirely inside `/tmp` scratch repositories** and
> against a **throwaway copy** of the wiki clone; neither touched `/workspaces`, either sub-repo, or
> any remote. The one `git fetch -q origin beta` in meta updated only remote-tracking refs.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**POLICY-04 — demonstrating the beta cut**

- **D-01: a rejection probe runs inside the phase; the real cut waits for explicit operator
  authorization.** Two separate deliverables. The probe is evidence that costs nothing
  outward-facing and can execute unattended; the cut is the close's terminal step and is
  outward-facing, so it stays gated as every outward-facing step has since v1.21.
  Rejected: the real cut unconditionally; probe only; a scratch-repo rehearsal.

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

- **D-03: if the cut is not authorized before the close, POLICY-04 is marked complete on the
  probe, with the missing half stated as a ledger non-claim.** Criterion 1's own words allow
  it — "an actual cut **or** an equivalent dry run that exercises the same paths". The ledger
  row then reads: v1.35 claims the rulesets do not block a push to an unprotected ref and do
  block a direct push to `main`; it does **not** claim a beta lockstep cut was performed under
  them.

- **D-04: when authorized, the cut is the FULL lockstep — v1.22's recipe with v1.30's PR
  posture.** Pull requests to `beta` in all three repositories, CI cuts the matched pair, then
  **manually dispatch `publish.yml`** so the app beta actually reaches PyPI, verify both
  channels from a clean venv, and tag meta `v1.35`. The PyPI dispatch is not optional detail:
  it is manual, and 6 of 13 historical app betas never reached PyPI, so skipping it leaves
  `pip install --pre` resolving a stale version.
  — **Reversibility:** one-way.
  Rejected: cut-only without the PyPI dispatch or the meta tag; a direct `--no-ff` merge and
  push with no PR.
  > ⚠ **Superseded in part by measured state — see [Correction C-4](#c-4--d-04s-manual-pypi-dispatch-premise-is-stale-the-upload-is-now-automatic).**
  > The manual dispatch is no longer required; the verification discipline still is.

- **D-05: the rulesets' breakage of the STABLE release path is filed as Backlog 999.46 with a
  recommended remedy named, not as a menu.** The recommended remedy is the todo's **option 2** —
  move the version bump off `main` (bump on `beta`, or a tag-triggered release with no push
  back) — because it removes the conflict rather than carving an exception through it. The other
  two candidates are recorded with the reasons they are not recommended.
  **No workflow file is edited.**

**POLICY-05 — the close procedure**

- **D-06: the procedure is fixed by CONFIGURATION first, prose second.** Two first-class
  tier-1 keys in `.planning/config.json`: `git.base_branch: "beta"` and
  `git.protected_branches: ["main"]`. Verified by read-back (`git.base-branch` → `beta`,
  `--is-protected main` → `true`), not merely set.
  **Measured:** `baseBranch` is always folded into `protectedBranches`
  (`git-base-branch.cjs:305`), so `beta` becomes protected too — but both consumers,
  `ship.md:78` and `execute-phase/steps/protected-branch.md`, only **warn and continue**.
  Rejected: prose only; config only with no prose; amending the vendored `.claude/gsd-core/`
  workflows.

- **D-07: a few lines in meta's `CLAUDE.md`, pointing at
  `.planning/notes/v135-close-procedure-under-protection.md` for the mechanics.** Meta's
  `CLAUDE.md` only — the close runs here, not in a submodule.
  Rejected: `.planning/notes/` alone; `PROJECT.md` §Context; the wiki.

- **D-08: the note covers the stable-release route to `main` and states plainly that it is
  currently blocked end to end.** A pull request is the only route — `current_user_can_bypass`
  is `never` on all three — and the version-bump step then fails per 999.46.

**The honesty ledger**

- **D-09: the full ledger is internal, at `.planning/v1.35/CLOSE-RECORD.md`, and each migrated
  wiki page carries a generated per-page provenance footer.** One line at the foot of each
  page: relocated from `<repo>/<source path>`, content unchanged, not re-verified.
  `.planning/v1.35/MIGRATION-TABLE.md` already holds every field needed, so the footer is
  **generated from that table, not authored twelve times**.
  — **Reversibility:** costly.
  Rejected: internal only; one `Documentation-Status` page; a line on `Home.md` alone.
  > ⚠ **"twelve" is not the measured count — see [Correction C-1](#c-1--the-footer-set-is-6-pages-not-12-and-migration-tablemd-has-17-data-rows-not-21).**

- **D-10: the footers get a mechanical guard — a new `tools/wiki/` checker and a
  `wiki-check.yml` leg, demonstrated RED before it is trusted.** The checker asserts every
  `MIGRATION-TABLE.md` row resolves to a live wiki page whose footer matches its source path
  and pre-deletion SHA. Planted-failure-first.
  **It will go RED on two rows the moment it runs** — `Protocol-Flags` and `Protocol-ID`.
  Unlike 999.45 it is in `tools/`, not product code, so this phase may fix it.
  — **Reversibility:** costly.
  Rejected: static text with no guard; guarding only the table's row-to-page resolution.
  > ⚠ **A second, unrecorded direction of the same defect exists — see [Correction C-2](#c-2--three-live-wiki-pages-have-no-migration-tablemd-row-at-all).**

- **D-11: one consolidated, comprehensive ledger table — not v1.34's curated ten rows.** The
  table carries criterion 3's three named minimums, the four non-claims and three findings Phase
  172's closing sweep handed forward, POLICY-04's own non-claim per D-03, and what Phases
  167–171 left open — including Phase 169's **FRONT-02, which the operator declined outright**.

**Upstream replies**

- **D-12: reply on all four issues; close gh#7 and gh#6; keep gh#5 open; keep gh#9 open and
  PIN it.** Per issue:
  - **gh#7** — reply and close.
  - **gh#5** — reply, stays open, as the surviving upstream tracker for FUT-W-01…05.
  - **gh#9** — reply, stays open, and **gets pinned.** One GraphQL call.
  - **gh#6** — reply and close. **A deliberate widening: criterion 5 does not list it.**
    D-11's two declines — required status checks, required review-thread resolution — must be
    named in the reply.

- **D-13: all four replies are drafted into the phase record, reviewed by the operator, and
  only then posted.** Exactly v1.22 D-02's precedent.
  — **Reversibility:** one-way for the closes and the posts.
  Rejected: posting directly; drafting and deferring the posting entirely.

**Mechanical constraints — recorded, not asked**

- **NO COMMENTS.** Zero comments in anything written for this project; a plan cannot override
  it. Binds the new `tools/wiki/` checker, the `wiki-check.yml` leg, and the two new
  `.planning/config.json` keys — **even though the surrounding `wiki-check.yml` is dense with
  comments written by earlier phases.** Do not match the local style; match the rule.
- **`grep` on PATH in this devcontainer is ugrep and honours `.gitignore`.** Any gate evidence
  uses `/usr/bin/grep`, and a repository-wide scan is scoped to `git ls-files`.
- **`tools/wiki/selftest.sh` mutates Phase 168's evidence files.** `git checkout --` them after
  every run.
- **The wiki is reached by clone-commit-push.** `https://github.com/henols/firestarter_prom.wiki.git`
  is the only working copy; no in-repo source tree, no publish script, no PR, no CI gate.
- **A wiki edit that adds or removes a page owes two navigation edits** — `_Sidebar.md` and
  `Home.md` — or `wiki.py links` fails on orphan detection and sidebar completeness.
- **Read GitHub state back from the API, never the settings page.**
- **Use `git cherry`, never `--is-ancestor`.** Local `beta` in every repository here is stale
  enough to poison the check — recreate it from `origin/beta` first. Meta's `origin/beta` tip is
  a PR merge commit, so the close tail cannot fast-forward onto it; it must be merged.
- **Sub-repo changes land inside the submodule on
  `gsd/v1.35-documentation-consolidation-wiki-migration`;** meta changes land on the same-named
  branch here. Re-pin both gitlinks before the phase closes, and prove equality per submodule.
- **`firestarter_app` is not porcelain-clean** — `tools/build_db.py` carries one unstaged
  modification (Backlog 999.45). Any verify leg asserting an empty `git status --porcelain` on
  that submodule will fail.
- **`ROADMAP.md` writes belong to the orchestrator.** v1.35's ROADMAP was hand-authored and must
  never be regenerated. This is why the 999.46 promotion is the orchestrator's write.
- **`.planning/config.json` is edited by hand**, not through a GSD verb.
- **Backlog 999.9 will invalidate every link this phase writes.** The criterion-4 record names
  169, 170 and 172; this phase's own links join that set and should be kept mechanically
  greppable.

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

### Deferred Ideas (OUT OF SCOPE)

- **A ruleset on `beta`.** POLICY-03 is complete and scoped to `main`. Note that D-06 makes GSD
  *treat* `beta` as protected locally while GitHub does not.
- **Required status checks on `main`** (gh#6). Declined by Phase 172 D-11, carried here.
- **Required review-thread resolution on `main`** (gh#6). Declined by Phase 172 D-11.
- **GitHub private vulnerability reporting.** Declined by Phase 172 D-04 and Phase 171 D-02.
- **A `henols/.github` default community-health repository.**
- **Fixing the release path itself** — the workflow rework 999.46 describes.
- **FUT-W-01…05** — compatibility matrix, per-family pages, algorithm and command-set pages,
  task-oriented tutorials, repository metadata keywords.
- **Backlog 999.9's rename sweep.** Recorded here with 169/170/172 named; not performed.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| POLICY-04 | "The `beta` lockstep cut still works under those rulesets, demonstrated rather than assumed — this project's milestone convention pushes `beta`, not `main`." `[VERIFIED: .planning/REQUIREMENTS.md:68]` | §"The push probe: what actually reaches GitHub's ruleset engine" gives a probe recipe proven to reach the receive stage, plus the [demonstrated client-side false positive](#pitfall-1-a-non-fast-forward-probe-push-is-rejected-client-side-and-proves-nothing) the naïve shape produces. §"Live GitHub state" gives the three-way-identical ruleset read-back and the `beta`-carries-no-rule read-back. §"The beta lockstep cut recipe" gives v1.22's recipe with the [C-4 correction](#c-4--d-04s-manual-pypi-dispatch-premise-is-stale-the-upload-is-now-automatic). |
| POLICY-05 | "The GSD close procedure is updated for PR-only `main`, either as a PR flow or a documented admin bypass, so `/gsd-complete-milestone` does not break at the next close." `[VERIFIED: .planning/REQUIREMENTS.md:69]` | §"The GSD close machinery" gives every consumer of `git.base-branch` with verified line numbers, the [C-3 correction](#c-3--no-gsd-workflow-pushes-main-at-all-requirementsmd119s-premise-is-false) to the requirement's own premise, and a **proven** read-back of the D-06 config edit run against a scratch repo. |
</phase_requirements>

## Summary

This is a records-and-procedure close phase with exactly one piece of new mechanical code (D-10's
footer checker) and one two-key configuration edit (D-06). Nothing here installs a dependency,
touches product source, or needs a new tool. The research risk is not "what library" — it is
**whether the phase's own premises survive measurement**, because CONTEXT.md's §Specifics already
records three roadmap assertions that did not, and this session found **four more**.

The four corrections are load-bearing and are stated up front, each with the tool output that
established it: the footer set is **6 pages, not 12**; **three live wiki pages have no
`MIGRATION-TABLE.md` row at all**, a mirror-image of the two stale rows D-10 already knows about;
**no GSD workflow pushes `main`**, so POLICY-05's stated failure mode is not the real one (the real
ones are worse and D-06 fixes all three); and **the PyPI upload D-04 calls manual is now
automatic**, wired by `beta-release.yml`'s `workflow_call` into `publish.yml`.

Two further findings are the difference between a probe that proves something and one that does
not. First, a direct push to `main` from a non-descendant ref is rejected **client-side** with
`(non-fast-forward)` and never reaches GitHub's receive stage — the identical trap D-02 identifies
in `--dry-run`, in a different costume; the probe must branch off `origin/main` first, and that is
demonstrated below with pasted output. Second, a provenance footer whose source path contains a
part-number token flips `honest02_truth.py` leg 1 to `MISSING STAMP` on any unstamped page — also
demonstrated below, RED, with the exact error text.

**Primary recommendation:** plan the phase around the corrected measurements, not CONTEXT.md's
counts; build the footer checker as a standalone stdlib-only script beside `dispatch_mirror.py`
using its exact `0/1/2` exit-code contract and its zero-`#`-comment convention; make it
**bidirectional** so it catches C-2 as well as D-10's named two; and make the push probe branch off
`origin/main` so the rejection it records is GitHub's, not git's.

---

## Corrections to CONTEXT.md's measured state

Four claims in CONTEXT.md's "Live state measured 2026-09-02" block, or in the decisions resting on
it, do not survive re-measurement. Each is stated with the command and the output.

### C-1 — the footer set is **6 pages, not 12**, and `MIGRATION-TABLE.md` has **17 data rows, not 21**

CONTEXT.md §In-scope says "twelve generated per-page provenance footers on the wiki" and §Live state
says "`MIGRATION-TABLE.md` → 21 data rows". Measured:

`[VERIFIED: .planning/v1.35/MIGRATION-TABLE.md:10-21, :59-65, :82-85]` — the file has **three** tables.
`/usr/bin/grep -c '^|'` returns **23** pipe-leading lines; 3 header rows + 3 separator rows = 6, so
**17 data rows**. The main provenance table (`:12-21`) carries exactly **10** rows, verbatim:

```
| firestarter_prom | — | Home | Home | — | 167 |
| firestarter | firestarter/doc/PROTOCOLS.md | Programming-Protocols | Programming Protocols | a218b4f5273d14f0abd796b21ac104792de01603 | 168 |
| firestarter | firestarter/doc/SHIELD-REVISIONS.md | Shield-Revisions | Shield Revisions | a218b4f5273d14f0abd796b21ac104792de01603 | 168 |
| firestarter_app | firestarter_app/doc/beta-testing-install.md | Install-Beta | Install Beta | d56424e1979edf7245cffb9ec3111c0469f5b23f | 168 |
| firestarter_app | firestarter_app/doc/community-validation.md | Testing-Chips | Testing Chips | d56424e1979edf7245cffb9ec3111c0469f5b23f | 168 |
| firestarter_app | firestarter_app/doc/lockable-proms.md | Lockable-PROMs | Lockable PROMs | d56424e1979edf7245cffb9ec3111c0469f5b23f | 168 |
| firestarter_app | firestarter_app/doc/protocol-flags.md | Protocol-Flags | Protocol Flags | d56424e1979edf7245cffb9ec3111c0469f5b23f | 168 |
| firestarter_app | firestarter_app/doc/protocol-id.md | Protocol-ID | Protocol ID | d56424e1979edf7245cffb9ec3111c0469f5b23f | 168 |
| firestarter_app | firestarter_app/autocomplete.md | Shell-Completion | Shell Completion | d56424e1979edf7245cffb9ec3111c0469f5b23f | 171 |
| firestarter_prom | — | Contributing | Contributing | — | 172 |
```

Of those 10: **2** (`Home`, `Contributing`) have `—` for both source path and pre-deletion SHA, so
there is no provenance for a footer to state. **2** (`Protocol-Flags`, `Protocol-ID`) name pages a
fresh wiki clone does not have. That leaves **6** rows that are both provenance-bearing and live:
`Programming-Protocols`, `Shield-Revisions`, `Install-Beta`, `Testing-Chips`, `Lockable-PROMs`,
`Shell-Completion`.

The live wiki carries **11 content pages** (12 `.md` files less `_Sidebar.md`)
`[VERIFIED: git clone of firestarter_prom.wiki.git @ dc07042c, 2026-09-02]`:

```
Breaking-Changes.md  Chip-Database-Fields.md  Contributing.md  Home.md
Install-Beta.md  Lockable-PROMs.md  Pin-Maps.md  Programming-Protocols.md
Shell-Completion.md  Shield-Revisions.md  Testing-Chips.md  _Sidebar.md
```

**There is no set of size 12 anywhere in this data.** The planner must pick a footer scope
deliberately — 6 (provenance-bearing and live) is the only set D-09's wording ("relocated from
`<repo>/<source path>`, content unchanged, not re-verified") can actually be generated for.

### C-2 — three live wiki pages have no `MIGRATION-TABLE.md` row at all

D-10 knows about the table→page failures (`Protocol-Flags`, `Protocol-ID`). The page→table direction
fails on **three** pages, and CONTEXT.md does not mention it.
`[VERIFIED: /usr/bin/grep against .planning/v1.35/MIGRATION-TABLE.md, 2026-09-02]`

| Live wiki page | Appears in `MIGRATION-TABLE.md`? |
|---|---|
| `Breaking-Changes` | **Not mentioned anywhere in the file** |
| `Chip-Database-Fields` | Only as prose inside a *retired* row (`:63`), never as a row of its own |
| `Pin-Maps` | Only as prose inside two *retired* rows (`:61`, `:62`), never as a row of its own |

This violates Phase 171 D-06's own stated principle, quoted in CONTEXT.md §Established Patterns:
*"every page added, moved or removed gets a `MIGRATION-TABLE.md` row"*. It is also directly material
to D-10's design: a checker written in the table→page direction only would pass over all three.

**Recommendation:** make the checker **bidirectional** (every provenance row resolves to a live page
*and* every live page is accounted for by the table, with an explicit exclusion list for
navigation pages). That converts C-2 from an undiscovered defect into a named, guarded one at no
extra structural cost, and it is the shape that makes the checker worth registering at all.

### C-3 — **no GSD workflow pushes `main` at all**; `REQUIREMENTS.md:119`'s premise is false

`.planning/REQUIREMENTS.md:119` reads *"`/gsd-complete-milestone` pushes `main` directly today."*
That is the stated reason POLICY-05 exists. It is not true of the vendored workflows.

`[VERIFIED: /usr/bin/grep -rn "git push" .claude/gsd-core/workflows/complete-milestone.md .claude/gsd-core/workflows/complete-milestone/ — single hit]`

```
.claude/gsd-core/workflows/complete-milestone/steps/git-tag.md:26:git push origin v[X.Y]
```

That is a **tag** push, and all three rulesets are `target: branch`, so a tag push is not governed
by them at all. `[VERIFIED: gh api repos/henols/{repo}/rulesets → "target":"branch", 2026-09-02]`

`ship.md`'s four pushes are all `${CURRENT_BRANCH}` — never `${BASE_BRANCH}`.
`[VERIFIED: .claude/gsd-core/workflows/ship.md:194, :199, :491, :521]`

**The real failure surface is three-fold, and it is worse than a blocked push:**

1. `complete-milestone.md:775` and `:804` run `git checkout ${BASE_BRANCH}` and then
   `git merge --squash "$MILESTONE_BRANCH"` + `git commit` — a purely **local** merge onto `main`.
   It succeeds. It leaves a local `main` that has diverged from `origin/main` and can never be
   pushed (`pull_request` + `non_fast_forward`). Nothing warns. The next `git pull` on `main`
   produces a merge commit on top of an un-pushable history.
   `[VERIFIED: .claude/gsd-core/workflows/complete-milestone.md:775-795]`
2. `ship.md:373` opens PRs with `--base "${BASE_BRANCH}"` → `main`, which is the wrong target for a
   project whose convention ships from `beta`.
   `[VERIFIED: .claude/gsd-core/workflows/ship.md:373]`
3. **Two consumers CONTEXT.md does not name:** `execute-phase.md:290` and `quick.md:197` both use
   `gsd_run query git.base-branch` to decide which remote branch the next phase/quick branch
   **forks off**. `pr-branch.md:28` uses it as the default filter target. With `base_branch` at
   `main`, every new milestone branch forks off `origin/main` — the opposite of the operator's
   standing branching instruction.
   `[VERIFIED: .claude/gsd-core/workflows/execute-phase.md:290; quick.md:197; pr-branch.md:28]`

**This strengthens D-06 rather than weakening it.** The config repoint fixes all three at once,
and item 3 is a pre-existing correctness win the phase gets for free. The plan should record the
correction to `REQUIREMENTS.md:119`'s premise in the ledger — a requirement whose stated rationale
is factually wrong, satisfied anyway by a better mechanism, is exactly the kind of thing D-11's
"every claim paired with its non-claim" table exists to carry.

### C-4 — D-04's "manual PyPI dispatch" premise is stale; the upload is now **automatic**

D-04 states the PyPI dispatch "is not optional detail: **it is manual**". Measured:

`[VERIFIED: firestarter_app/.github/workflows/beta-release.yml:129-134]` —

```yaml
  pypi:
    needs: github
    uses: ./.github/workflows/publish.yml
    with:
      tag: ${{ needs.github.outputs.version }}
    secrets: inherit
```

`publish.yml` gained a `workflow_call` entry point precisely to close this hole; its own header
records the symptom D-04 is quoting: *"GitHub had betas through b17 while PyPI stopped at b15, with
b16/b17 never uploaded and nothing anywhere reporting a failure."*
`[VERIFIED: firestarter_app/.github/workflows/publish.yml:8-21]` The `workflow_dispatch` trigger is
now explicitly *"Retained as the operator escape hatch"*.
`[VERIFIED: firestarter_app/.github/workflows/publish.yml:31-33]`

Corroborated live: `[VERIFIED: pypi.org/pypi/firestarter/json, 2026-09-02]` PyPI carries
`3.0.0b33`, `3.0.0b34`, `3.0.0b35`; the app's latest GitHub prerelease is `3.0.0b35`
(2026-08-31T22:39:03Z) `[VERIFIED: gh release list --repo henols/firestarter_app]`. The channels
agree with no manual dispatch having been performed for those three.

**What survives:** the *verification* discipline (clean-venv resolution of both channels, read from
`gh release list` and the PyPI JSON API, never predicted). **What changes:** a manual dispatch is
redundant. It is also harmless — `publish.yml` sets `skip-existing: true`
`[VERIFIED: firestarter_app/.github/workflows/publish.yml:60-68]` — so if the operator wants it kept
as belt-and-braces, that costs nothing. The plan should state which posture it takes rather than
inheriting D-04's wording unexamined.

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Ruleset rejection probe (POLICY-04) | GitHub receive-stage (server) | local git client | Only the server evaluates rulesets; the client can reject first and mask the result entirely — see Pitfall 1 |
| Beta lockstep cut (POLICY-04, gated) | GitHub Actions (`beta-*.yml`) | operator | The cut is fired by CI on a push to `beta`; no local step produces it |
| Close-procedure repoint (POLICY-05) | `.planning/config.json` (tier‑1 config) | `.planning/notes/` + `CLAUDE.md` prose | `git-base-branch.cjs` reads config at tier 1; prose alone changes no behaviour |
| Provenance footers (D-09) | live wiki repo (`firestarter_prom.wiki.git`) | `.planning/v1.35/MIGRATION-TABLE.md` as the data source | The wiki is the only working copy; the table is the generator input |
| Footer guard (D-10) | `tools/wiki/<checker>.py` in meta | `.github/workflows/wiki-check.yml` leg | Checker logic in meta `tools/`; CI only invokes it, exactly as the three existing legs do |
| Honesty ledger (D-11) | `.planning/v1.35/CLOSE-RECORD.md` | per-page footers | Internal record is the full ledger; footers carry the one non-claim the wiki reader needs |
| Backlog 999.46 + criterion‑4 sweep | `.planning/ROADMAP.md` | `.planning/todos/pending/` | ROADMAP writes are the orchestrator's; the todo file is the input |
| Upstream replies (D-12/D-13) | GitHub Issues REST + GraphQL | phase record (drafts) | REST for comment/close; **GraphQL only** for pinning — REST has no pinned-issue endpoint |

---

## Project Constraints (from CLAUDE.md)

`/workspaces/CLAUDE.md` exists (3014 bytes). `/workspaces/.claude/CLAUDE.md` does **not** exist.
`[VERIFIED: ls, 2026-09-02]` Directives extracted:

| Directive | Binding on this phase |
|---|---|
| Meta-repo tracks `.planning/`, `.claude/`, `tools/`, `.github/`; neither sub-repo is committed here | Yes — the checker and the workflow leg land in meta; footers land in the wiki repo |
| "Documentation lives only in the `firestarter_prom` GitHub wiki — there is no in-repo copy of it. `tools/wiki/` holds the checkers that run against a clone of that wiki." | Yes — confirms D-09/D-10's placement |
| Serial-protocol / constants-parity rules (`serial_comm.py` ↔ `firestarter.cpp`, `constants.py` ↔ `firestarter.h`) | Not applicable — this phase touches no product code |
| Board buffer sizes, EEPROM calibration | Not applicable |

**Standing operator rule that overrides local style (from CONTEXT.md, not CLAUDE.md):** zero
comments in any source this phase writes. This is measurably already the convention in
`tools/wiki/` — see the Don't-Hand-Roll table.

---

## Standard Stack

Nothing is installed. Every tool this phase needs is already present and was version-checked in
this session.

### Core

| Tool | Version | Purpose | Why standard |
|---|---|---|---|
| `python3` (stdlib only) | 3.12.14 `[VERIFIED: python3 --version]` | The new `tools/wiki/` checker | All four existing checkers are stdlib-only single-file scripts; ubuntu-latest supplies python3 in `wiki-check.yml` with no setup step |
| `git` | 2.55.0 `[VERIFIED: git --version]` | Push probe, wiki clone-commit-push, `git cherry`, gitlink re-pin | The wiki has no API; clone-commit-push is the only route |
| `gh` | 2.98.0 `[VERIFIED: gh --version]`, authed as `henols` | Ruleset read-back, issue comments/closes, release reads | Already the project's standing tool for GitHub state |
| `gh api graphql` | same | **Pinning gh#9 only** | REST has no pinned-issue endpoint; the `pinIssue` mutation is GraphQL-only |
| `/usr/bin/grep` | GNU grep 3.11 `[VERIFIED: /usr/bin/grep --version]` | All gate evidence | `grep` on PATH is **ugrep 7.8.4** `[VERIFIED: grep --version]` and honours `.gitignore` |
| `node` + `gsd-tools.cjs` | node v22.23.2 | `git.base-branch` read-back | The D-06 verification mechanism |

### Supporting

| Tool | Purpose | When to use |
|---|---|---|
| `curl` + `pypi.org/pypi/firestarter/json` | Channel verification for a beta cut | Only if D-04's cut is authorized |
| `python3 -m venv` in `$(mktemp -d)` | Clean-venv `pip install --pre` proof | Only if D-04's cut is authorized; v1.22's discipline — never the editable install |

### Alternatives Considered

| Instead of | Could use | Tradeoff |
|---|---|---|
| A standalone script beside `dispatch_mirror.py` | A `wiki.py links`-style subcommand | `wiki.py` is scoped to *reachability/link/filename legality of a wiki clone alone*; the footer check needs a second input (`MIGRATION-TABLE.md` in meta), which is the shape `honest02_truth.py` and `dispatch_mirror.py` already take as standalone scripts. **Recommend standalone.** |
| A throwaway **branch** as the unprotected-ref probe half | A throwaway **tag** | A tag fires zero CI in the app repo by explicit design (`branches: ['**']` "matches every BRANCH but no tags" `[VERIFIED: firestarter_app/.github/workflows/ci.yml:17-19]`) — but the rulesets are `target: branch`, so a tag push does not test branch scoping. **Recommend a branch**, accepting the CI cost quantified in Pitfall 4. |

**Installation:** none. No package is added to any ecosystem by this phase.

## Package Legitimacy Audit

**Not applicable — this phase installs no external packages.** The new checker is stdlib-only
Python, matching all four existing `tools/wiki/` scripts, whose entire third-party import surface
is empty (`argparse`, `hashlib`, `importlib`, `json`, `re`, `sys`, `pathlib` only)
`[VERIFIED: tools/wiki/dispatch_mirror.py:25-29; tools/wiki/honest02_truth.py:70-76; tools/wiki/wiki.py:29-32]`.
The `wiki-check.yml` leg adds no `uses:` action beyond the checkout/clone steps already present.

**Packages removed due to [SLOP] verdict:** none.
**Packages flagged as suspicious [SUS]:** none.

---

## Architecture Patterns

### System architecture — how the phase's five deliverables reach their surfaces

```
                        ┌──────────────────────────────────────┐
   OPERATOR ──gate──────▶│ D-04 beta lockstep cut (CONDITIONAL) │
      │                  └───────────────┬──────────────────────┘
      │                                  │ PR → beta (×3 repos)
      │                                  ▼
      │                    ┌─────────────────────────────┐
      │                    │ beta-release.yml (app)      │──needs:github──▶ publish.yml
      │                    │ beta-build.yml   (fw)       │   (workflow_call)      │
      │                    └──────────┬──────────────────┘                       ▼
      │                               │ auto-commit bump → beta               PyPI (auto)
      │                               ▼
      │                        GitHub prereleases  ──▶ clean-venv verification
      │
      │ D-13 blocking wording review
      ▼
 ┌──────────────┐   gh api REST     ┌──────────────────────────┐
 │ 4 drafted    │──────────────────▶│ gh#5 open · gh#6 close   │
 │ replies in   │   gh api graphql  │ gh#7 close · gh#9 open+PIN│
 │ phase record │──────────────────▶└──────────────────────────┘
 └──────────────┘

 ┌────────────────────┐  read   ┌──────────────────────────┐
 │ MIGRATION-TABLE.md │────────▶│ footer generator (D-09)  │
 │  (6 usable rows)   │         └────────────┬─────────────┘
 └─────────┬──────────┘                      │ clone-commit-push
           │                                 ▼
           │                     firestarter_prom.wiki.git  (no PR, no CI on the edit)
           │                                 │
           │  read (both directions)         │ fresh clone
           ▼                                 ▼
 ┌───────────────────────────┐      ┌──────────────────────┐
 │ tools/wiki/<checker>.py   │◀─────│ wiki-check.yml leg   │──PR #4 into protected main
 │ exit 0 / 1 / 2            │      │ (registered, 0 runs) │   ← itself POLICY-05 evidence
 └───────────────────────────┘      └──────────────────────┘

 ┌──────────────────────┐  hand edit  ┌─────────────────────────────────────┐
 │ .planning/config.json│────────────▶│ git.base_branch: "beta"             │
 └──────────────────────┘             │ git.protected_branches: ["main"]    │
                                      └───────────────┬─────────────────────┘
                                                      │ read-back
                                                      ▼
                    git-base-branch.cjs ──▶ complete-milestone:734 · ship:46/78/316/373
                                            execute-phase:290 · quick:197 · pr-branch:28

 probe: git fetch → checkout -B probe origin/main → commit --allow-empty → push origin HEAD:main
        expected: GH013 rule violation (server)      ×3 repos
        control:  push probe-branch (unprotected)    accepted, then deleted
```

### The push probe: what actually reaches GitHub's ruleset engine

D-02 correctly rejects `--dry-run` because the pack is never sent. There is a **second** way to get
a rejection that proves nothing, and it is the shape a naïve probe takes. Demonstrated in a
scratch bare repo with no rules at all `[VERIFIED: local probe, /tmp scratch, 2026-09-02]`:

```
=== CASE A: push a NON-DESCENDANT ref to main (the false-positive trap) ===
 ! [rejected]        HEAD -> main (non-fast-forward)
error: failed to push some refs to '../remote.git'
hint: Updates were rejected because a pushed branch tip is behind its remote
hint: counterpart. If you want to integrate the remote changes, use 'git pull'

=== CASE B: push a TRUE fast-forward of origin/main (reaches server-side rules) ===
To ../remote.git
   4f6ce9e..16e90d5  HEAD -> main
```

Case A's remote has **no ruleset whatsoever** and still rejected the push — because git computed
the rejection locally. A probe built that way would record a rejection on all three repositories
and attribute it to the ruleset, which would be false.

**The probe recipe that reaches the receive stage:**

```bash
git fetch origin main
git checkout -B ruleset-probe origin/main
git commit --allow-empty -m "ruleset rejection probe (POLICY-04)"
git push origin HEAD:main
```

**Acceptance is the rejection text, not the exit code.** The evidence must show GitHub's own
message — `remote: error: GH013: Repository rule violations found` and a
`Changes must be made through a pull request` clause naming the ruleset. A rejection whose text
says `non-fast-forward`, `fetch first`, or `Permission denied` is **not** a POLICY-04 pass and must
be recorded as an inconclusive probe, not a green one.

**Corroborating (not primary) evidence** — cheap, and it pairs with the probe as a before/after:

```bash
gh api repos/henols/<repo>/rules/branches/main   # → three rules, ruleset_id
gh api repos/henols/<repo>/rules/branches/beta   # → []
```

Measured 2026-09-02 `[VERIFIED: gh api repos/henols/{prom,firestarter,firestarter_app}/rules/branches/{main,beta}]`:
all three `main` return `deletion` + `non_fast_forward` + `pull_request` under ids `22043478` /
`4998759` / `22046179`; **all three `beta` return `[]`**. This is exactly the "reading of the
ruleset configuration" criterion 1 refuses to accept on its own — include it as context, never as
the discharge.

### Pattern: the `tools/wiki/` checker contract

All four existing checkers implement one contract. The new one must too.

**Exit codes** `[VERIFIED: tools/wiki/dispatch_mirror.py:8-12; tools/wiki/wiki.py:6-11; tools/wiki/honest02_truth.py:13-22]`:

```
0 = the asserted property holds
1 = the asserted property is false
2 = a precondition was not met (source directory missing, or missing on the command line at all)
```

**Structure**, taken from `dispatch_mirror.py`:

- `#!/usr/bin/env python3`, then a module docstring that **states the exit-code contract explicitly**
  and names the failure vocabularies.
- `from __future__ import annotations`, stdlib imports only.
- Module-level `UPPER_CASE` constants for every path, delimiter and regex.
- Pure parse/compare functions returning `list[str]` of failure messages.
- `_build_argparser() -> argparse.ArgumentParser` with `prog=`, `description=__doc__`,
  `formatter_class=argparse.RawDescriptionHelpFormatter`, and `required=True` `Path`-typed args.
  `[VERIFIED: tools/wiki/dispatch_mirror.py:151-159]`
- `main() -> int` doing precondition checks first (each `return 2` with an `ERROR:` line to
  **stderr**), then the comparison, then `for message in failures: print(f"ERROR: {message}",
  file=sys.stderr); return 1`, then a single `print(f"OK: …")` **with a count** to stdout and
  `return 0`. `[VERIFIED: tools/wiki/dispatch_mirror.py:173-251]`
- `if __name__ == "__main__": sys.exit(main())`.

**Argument naming precedent:** `--wiki-dir`, `--db`, `--allowlist`
`[VERIFIED: tools/wiki/honest02_truth.py:329-331]`; `--app-dir`, `--fw-dir`
`[VERIFIED: tools/wiki/dispatch_mirror.py:157-158]`; `--source-dir`
`[VERIFIED: tools/wiki/wiki.py:276]`. The footer checker needs two inputs and should follow the
same shape, e.g. `--wiki-dir` and `--migration-table`.

**The zero-comment convention is already mechanically true.** Every one of the four scripts contains
exactly **one** line matching `^\s*#` — the shebang `[VERIFIED: /usr/bin/grep -cE '^\s*#' on all four files → 1, 1, 1, 1]`.
Prose lives in module docstrings only. This is a fact the plan can assert as a verify leg, and it
means the operator's no-comments rule and the file's own precedent agree.

### Pattern: how `wiki-check.yml` invokes a checker

Every existing leg is the same three lines `[VERIFIED: .github/workflows/wiki-check.yml:107-125]`:

```yaml
      - name: <REQ-ID> <what it asserts> check
        run: |
          python3 meta/tools/wiki/<script>.py \
            --<arg> <path> \
            --<arg> <path>
          echo "OK: <the property, in plain words>"
```

The job already has `meta`, `firestarter`, `firestarter_app` and `wiki-clone` on disk at
`[VERIFIED: .github/workflows/wiki-check.yml:51-97]`, so **no new checkout or clone step is
required**. The workflow has `permissions: contents: read` `[VERIFIED: :7-8]` and triggers only on
`schedule: cron '17 6 * * 1'` and `workflow_dispatch` `[VERIFIED: :2-5]`.

> **NO-COMMENTS warning, restated because the file argues against itself:** `wiki-check.yml` is
> dense with `#` comment blocks written by earlier phases (`:14-50` is a 37-line comment). The new
> leg must carry **none**. Do not match the local style.

### Pattern: planted-failure-first, in this repo

Phase 172's LEGACY-01 leg is the worked example `[VERIFIED: .planning/phases/172-policy-one-tracker-protected-main/evidence/172-03-legacy01-redgreen.txt exists]`,
cited in the closing sweep as *"The guard demonstrated RED before being trusted — a check never
seen to fail is not evidence."* The shape:

1. Run the checker against the real, correct inputs → record GREEN.
2. Plant a specific, named violation in a **copy** of the input (never the live wiki) → record RED
   with the exact `ERROR:` line.
3. Restore byte-identically and re-run → record GREEN again.
4. Commit all three observations to `evidence/`.

For the footer checker the natural planted failures are: a footer whose SHA is altered by one
character (leg: SHA mismatch), a footer deleted from one page (leg: footer absent), and a table row
naming a page that does not exist (leg: unresolvable row — **this one is already RED on the real
inputs**, per C-1/C-2).

### Anti-patterns to avoid

- **`git push --dry-run` as ruleset evidence.** Named by D-02; the pack is never sent.
- **Pushing a non-descendant ref to test a ruleset.** Rejected client-side; see Pitfall 1.
- **A one-directional table↔page checker.** Misses C-2's three pages entirely.
- **`grep` (unqualified) in any gate.** It is ugrep and honours `.gitignore`.
- **Asserting `git status --porcelain` is empty on `firestarter_app`.** It carries one unstaged
  `tools/build_db.py` modification `[VERIFIED: git -C firestarter_app status --porcelain → " M tools/build_db.py", 2026-09-02]`.
- **Regenerating `ROADMAP.md` via a GSD verb.** Hand-authored; `roadmap.update-plan-progress`
  overwrites positionally.
- **Running `tools/wiki/selftest.sh` without cleaning up.** It mutates Phase 168 evidence files.

---

## Don't Hand-Roll

| Problem | Don't build | Use instead | Why |
|---|---|---|---|
| Reading pre-migration source content | A bespoke file-history walker | `git -C <subrepo> show <sha>:<path>` | The convention `MIGRATION-TABLE.md:27-28` documents and `honest02_truth.py` already uses `[VERIFIED: .planning/v1.35/MIGRATION-TABLE.md:26-29]` |
| A CI harness for the new checker | A new workflow file | A fourth `run:` leg in `wiki-check.yml` | Meta, both sub-repos and a fresh wiki clone are already on disk in that job |
| Exit-code / output conventions | A new vocabulary | `dispatch_mirror.py`'s `0/1/2` + `ERROR:`→stderr / `OK: <count>`→stdout | Three checkers and three CI legs already depend on this contract |
| Determining "is this branch protected" | A `gh api` call in a workflow | `gsd_run query git.base-branch --is-protected <branch>` | Already the single resolver; and the two consumers only warn |
| Pinning an issue | A REST call | `gh api graphql` `pinIssue` mutation | **REST has no pinned-issue endpoint.** Node IDs measured below |
| Argument parsing / path handling in the checker | Hand-rolled `sys.argv` | `argparse` + `pathlib.Path` typed args | Every existing checker; `type=Path` + `required=True` |
| Footer text per page | Twelve hand-authored strings | Generation from `MIGRATION-TABLE.md` | D-09's own reasoning, and the only way the checker can compare against a single source of truth |

**Key insight:** every mechanism this phase needs already exists and is already registered. The
phase's real difficulty is arithmetic and premise-checking, not construction — which is why the
four corrections above are the highest-value output of this research.

---

## Runtime State Inventory

This phase changes configuration and outward-facing state, so the inventory applies.

| Category | Items found | Action required |
|---|---|---|
| **Stored data** | None in a database sense. The **live wiki repo** is the only mutable content store: `firestarter_prom.wiki.git` @ `dc07042c` (2026-09-01, "docs: add Contributing page…"), 12 `.md` files `[VERIFIED: git clone, 2026-09-02]` | Footers land here by clone-commit-push; there is **no PR, no review and no CI gate** on the edit |
| **Live service config** | Three GitHub rulesets, all `active`, all three-way identical: prom `22043478` (created 2026-09-01T20:12:43Z), firestarter `4998759` (created **2025-04-22T11:42:12Z**, updated 2026-09-01T21:04:49Z — proving *amended*, not recreated), firestarter_app `22046179` (created 2026-09-01T21:04:58Z). Each: `conditions.ref_name.include: ["~DEFAULT_BRANCH"]`, `exclude: []`; rules `deletion`, `non_fast_forward`, `pull_request`; one bypass actor `{actor_id: null, actor_type: "DeployKey", bypass_mode: "always"}`; `current_user_can_bypass: "never"` `[VERIFIED: gh api repos/henols/{repo}/rulesets/{id}, 2026-09-02]` | **Not amended by this phase.** Read back before and after the probe as the before/after pair |
| | `pinnedIssues` on prom: `totalCount: 0`, `nodes: []` `[VERIFIED: gh api graphql, 2026-09-02]`. Repo node id `R_kgDOSX4ERw`; gh#9 issue node id `I_kwDOSX4ER88AAAABId5Qdw` | D-12's pin is a GraphQL `pinIssue` mutation using those two ids |
| | `Wiki check` workflow id `348256804`, `state: active` on prom; `gh run list` shows **zero** `Wiki check` runs `[VERIFIED: gh api .../actions/workflows + gh run list, 2026-09-02]` | Registered, never run — NON-CLAIM 3 stands and must be carried into the ledger |
| | Four upstream issues, all `state: open`, all `comments: 0`: gh#5 "Move documentation" (`enhancement`), gh#6 "Protect main branches and centralize issue tracking in firestarter_prom" (`enhancement`), gh#7 "Feature: Improve Firestarter discoverability with generated documentation" (`feature`), gh#9 "Repository Structure and Contribution Guide" (no labels) `[VERIFIED: gh api repos/henols/firestarter_prom/issues/{5,6,7,9}, 2026-09-02]` | D-12/D-13: four comments, two closes, one pin — after the blocking review |
| **OS-registered state** | None. No scheduler entries, no daemons, no pm2/systemd units in scope | None |
| **Secrets / env vars** | `secrets.PERSONAL_ACCESS_TOKEN` (app `release.yml:43`, `beta-release.yml:112`), `secrets.PYPI_API_TOKEN` (`publish.yml:27-29`, `:60`). Read-only interest; the phase edits no workflow | None — 999.46 records that a PAT does not solve the bump problem because `current_user_can_bypass` is `never` |
| **Build artifacts** | Both submodule gitlinks in meta must be re-pinned before close (Phase 171 plan 04 / Phase 172 plan 09 pattern). `firestarter` is porcelain-clean; `firestarter_app` carries ` M tools/build_db.py` `[VERIFIED: git -C <sub> status --porcelain, 2026-09-02]`. Both submodules are on `gsd/v1.35-documentation-consolidation-wiki-migration` | Re-pin + prove equality per submodule; **do not** assert an empty porcelain on `firestarter_app` |

**Milestone-branch state, measured:** meta `origin/beta` tip is `c0d66295`, a **merge commit with two
parents** (`7132aea3 788e3b2a`, "Merge pull request #53 from henols/pr/v1.35-wiki-and-front-door")
`[VERIFIED: git log -1 origin/beta, 2026-09-02]` — confirming CONTEXT.md's "cannot fast-forward; it
must be merged". `git cherry origin/beta HEAD` reports **205** commits ahead. A local `beta` branch
exists and is stale; recreate it from `origin/beta` before any `git cherry`.

**Material to D-04 — part of v1.35 has already reached `beta`:**
`[VERIFIED: gh pr view, 2026-09-02]`

| PR | Merged | Target |
|---|---|---|
| `firestarter#57` "Phase 168: MIGRATE — The 13 doc/ Files (firmware)" → `59270c4e` | 2026-08-31T22:35:40Z | `beta` |
| `firestarter_app#56` "Phase 168: MIGRATE … (host CLI)" → `2d8ed903` | 2026-08-31T22:35:59Z | `beta` |
| `firestarter_prom#53` "Phases 168–169: MIGRATE and FRONT (meta)" → `c0d66295` | 2026-08-31T22:36:05Z | `beta` |

Those three fired the current prerelease pair — fw `3.0.0b24` (2026-08-31T22:47:23Z) and app
`3.0.0b35` (2026-08-31T22:39:03Z) `[VERIFIED: gh release list]`. **They predate the rulesets by
roughly 22 hours**, so they are *not* evidence for criterion 1. The authorized cut, if it happens,
is a **remainder** cut carrying Phases 171–173, not the whole milestone.

**Material to POLICY-05 — three PRs into a protected `main` have already succeeded:**
`prom#54` (`71148eda`), `firestarter#58` and `firestarter_app#57`, all merged 2026-09-02T08:56:58Z–
08:57:06Z `[VERIFIED: gh pr view, 2026-09-02]` — i.e. **after** the rulesets were created. The PR
route into a protected `main` is already demonstrated live, three times. D-10's workflow-leg PR
would be the fourth. The plan should cite the existing three as banked POLICY-05 evidence rather
than treating the fourth as the only instance.

---

## Common Pitfalls

### Pitfall 1: a non-fast-forward probe push is rejected **client-side** and proves nothing

**What goes wrong:** `git push origin HEAD:main` from the milestone branch is rejected before a
single byte of pack data is sent. The probe records a rejection and attributes it to the ruleset.
**Why it happens:** the milestone branch is not a descendant of `origin/main`, so git's own
fast-forward check fires first. **Demonstrated above** against a bare repo with no rules at all,
which still produced `! [rejected] HEAD -> main (non-fast-forward)`.
**How to avoid:** `git fetch origin main && git checkout -B ruleset-probe origin/main` before the
empty commit.
**Warning signs:** the rejection text says `non-fast-forward`, `fetch first`, `Updates were
rejected because…`, or `Permission denied` instead of `GH013: Repository rule violations found`.
**Verify leg:** assert the captured stderr **contains** `GH013` (or `Repository rule violations`),
not merely that the push exited non-zero.

### Pitfall 2: a provenance footer can turn `honest02_truth.py` RED

**What goes wrong:** the footer's source path contains a token that resolves in the chip database,
and leg 1's claim signature is *"the page carries at least one token that actually resolves against
the current database"* `[VERIFIED: tools/wiki/honest02_truth.py:41-46]`. An unstamped page acquiring
such a token becomes a `MISSING STAMP` failure.

**Demonstrated RED** — footer added to `Shell-Completion.md` (unstamped) in a throwaway copy of the
wiki clone, using a real retired row's source path:

```
=== honest02 with a part-number-bearing source path in an UNSTAMPED page's footer ===
ERROR: MISSING STAMP: Shell-Completion.md matches the claim signature (names a part number or
  algorithm value that resolves in the database) but carries no firestarter-claim-stamp
LEG 1 -- stamp present: 10 pages scanned, 6 matched the claim signature, 1 missing stamp
rc=1
```

**Baseline for comparison**, live clone, unmodified `[VERIFIED: 2026-09-02]`:
`LEG 1 … 10 pages scanned, 5 matched the claim signature, 0 missing stamp` … `rc=0`, with
`leg3 stamp-freshness 6 checked/0 stale` against `db-sha256-16=ccbc8d2c4866a5af`.

**The footer shape D-09 actually needs is safe** — proven, not assumed. Footers matching D-09's
wording were added to all six provenance-bearing pages in a throwaway copy and **both** existing
checkers stayed green `[VERIFIED: probe, 2026-09-02]`:

```
=== wiki.py links ===  OK: 11 pages, all reachable from Home.md by some link path, all internal
                       links resolve, all filenames legal, and all listed in _Sidebar.md.   rc=0
=== honest02      ===  OK: leg1 stamp-present 5 matched/0 missing, leg2 claims-resolve 1 regions/
                       39 claims/5 unchecked, leg3 stamp-freshness 6 checked/0 stale.        rc=0
```

None of the six source paths (`PROTOCOLS.md`, `SHIELD-REVISIONS.md`, `beta-testing-install.md`,
`community-validation.md`, `lockable-proms.md`, `autocomplete.md`) contains a part number.
**How to avoid:** re-run `honest02_truth.py` and `wiki.py links` against a **fresh clone** after
pushing footers, and treat any new `MISSING STAMP` as a footer-wording defect, not a page defect.
**Warning signs:** leg 1's "matched the claim signature" count rising above 5.

### Pitfall 3: `_Footer.md` is a real, reserved wiki page and is **not** what D-09 means

**What goes wrong:** "provenance footer" is read as GitHub's global wiki `_Footer.md`.
**Why it matters:** `_Footer.md` renders identically on every page and cannot carry per-page source
paths or SHAs — it can express none of D-09's three required fields. It is also already special-
cased: `wiki.py`'s `NAV_EXCLUDED_PAGES = ("_Sidebar.md", "_Footer.md")`
`[VERIFIED: tools/wiki/wiki.py:38]` and `honest02_truth.py`'s
`NAV_PAGES = frozenset({"Home.md", "How-To-Edit-This-Wiki.md", "_Sidebar.md", "_Footer.md"})`
`[VERIFIED: tools/wiki/honest02_truth.py:78-80]`. The live wiki has **no** `_Footer.md`.
**How to avoid:** name the artifact something other than "footer" in the checker and the plan, or
state explicitly that it is an in-page trailing block, not `_Footer.md`.

### Pitfall 4: the "accepted push to an unprotected ref" costs CI runs, and they are not all silent

**What goes wrong:** the control half of D-02's probe pushes a throwaway branch and triggers
workflows. Measured triggers `[VERIFIED: workflow `on:` blocks, 2026-09-02]`:

| Repo | Fires on a throwaway branch push | Publishes? |
|---|---|---|
| `firestarter_prom` (meta) | **nothing** — `catalog-sync-check.yml` is `branches: [main]` + `paths:` scoped `[:4-15]`; `wiki-check.yml` is schedule/dispatch only `[:2-5]` | — |
| `firestarter` | `build.yml` (`branches: ['**', '!beta']` `[:34]`) and `py32f071.yml` (`push: branches: ['**']`, no paths filter) | **No** — both publish steps are gated `github.ref == 'refs/heads/main'` `[build.yml:183, :199]` |
| `firestarter_app` | `ci.yml` (`branches: ['**']` `[:19]`) | **No** — `ci.yml` publishes nothing by design `[:7-13]` |

**How to avoid:** accept the cost (it is small and non-publishing), and delete the throwaway branch
afterwards — deletion is permitted because the `deletion` rule is scoped to `~DEFAULT_BRANCH` only.
**Warning signs:** if a control push were ever aimed at `beta`, it would fire the real cut. D-02
already forbids this; the plan must not soften it.

### Pitfall 5: the record gate needs 300 s and an rc=124 reads like a RED

`STATE.md` carries a ~52 000-character single line; the GSD record gate goes superlinear on it and
a timeout returns 124, which is easily misread as a genuine failure. Budget 300 s on any record
gate this phase runs. (Carried in CONTEXT.md §Reviewed Todos as a known hazard.) `[ASSUMED]`

### Pitfall 6: `git.base_branch: "beta"` also makes `beta` locally "protected"

`git-base-branch.cjs:305` is `const protectedBranches = [...new Set([baseBranch, ...effectiveConfig.protectedBranches])];`
`[VERIFIED: .claude/gsd-core/bin/lib/git-base-branch.cjs:305]`. Confirmed by read-back below:
`--is-protected beta` → `true`. Both consumers warn and continue
`[VERIFIED: ship.md:78-84 — `echo "⚠ …" >&2`, no exit; execute-phase/steps/protected-branch.md:11-15 — same]`,
and the second applies to `branching_strategy: none` while this project is `milestone`
`[VERIFIED: .planning/config.json → "git": {"branching_strategy": "milestone"}]`. This is the
asymmetry CONTEXT.md's Deferred Ideas already names; the ledger should carry it as a non-claim.

### Pitfall 7: `MIGRATION-TABLE.md` main-table rows are not all footer-eligible

Two rows have `—` for both source path and SHA (`Home`, `Contributing` — the latter *authored* from
gh#9, not migrated `[VERIFIED: .planning/v1.35/MIGRATION-TABLE.md:47-50]`). A generator that iterates
every main-table row will emit a footer saying "relocated from —". Filter on a non-`—` source path.

---

## Code Examples

### D-06 config read-back — **proven**, not predicted

The exact edit D-06 prescribes was applied to a **copy** of `/workspaces/.planning/config.json`
inside a scratch git repository and the resolver run against it.
`[VERIFIED: local probe against .claude/gsd-core/bin/gsd-tools.cjs, 2026-09-02]`

Edit (both keys nested under the existing `git` section; `git.protected_branches` is
nested-only — a top-level spelling is deliberately **not** honoured
`[VERIFIED: .claude/gsd-core/bin/lib/git-base-branch.cjs:84-87]`):

```json
  "git": {
    "branching_strategy": "milestone",
    "base_branch": "beta",
    "protected_branches": ["main"]
  }
```

Read-back, verbatim output:

```
--- base-branch ---           beta
--- is-protected main ---     true
--- is-protected beta ---     true
--- is-protected feature/x ---false
```

`feature/x` returning `false` also proves the resolver was **verified** rather than fail-closed —
the fail-closed path renders `true` for everything `[VERIFIED: git-base-branch.cjs:477-484]`.

Current, unmodified state of the real repo for the before-half of the pair
`[VERIFIED: run in /workspaces, 2026-09-02]`:

```
gsd_run query git.base-branch                      → main
gsd_run query git.base-branch --is-protected main  → true
git symbolic-ref refs/remotes/origin/HEAD          → refs/remotes/origin/main
```

Note that `--is-protected main` is **already** `true` today, because tier‑2 resolves `main` as the
base branch and the base branch is always folded in. The *distinguishing* read-back is
`git.base-branch` flipping `main` → `beta`, and `--is-protected beta` flipping `false` → `true`.
A verify leg that only asserts `--is-protected main == true` would pass before the edit.

**Documented surface** `[VERIFIED: .claude/gsd-core/references/planning-config.md:35-36]`:

```
| `git.base_branch`        | `null` (auto-detect) | Target branch for PRs and merges … |
| `git.protected_branches` | (none) | Optional array of non-empty strings naming additional shared
                                      branches that should trigger protected-branch warnings |
```

### The GSD close machinery — every consumer, with verified line numbers

| File:line | Code | Effect once `base_branch` = `beta` |
|---|---|---|
| `.claude/gsd-core/bin/lib/git-base-branch.cjs:302` | `function resolveProtectedBranchStatus(cwd, currentBranch, deps)` | entry point for `--is-protected` |
| `…:305` | `const protectedBranches = [...new Set([baseBranch, ...effectiveConfig.protectedBranches])];` | `beta` folded in |
| `…:137-138` | `const rawBaseBranch = config.base_branch;` | tier‑1 override |
| `…:147-164` | per-entry validation of `protected_branches`; bad entries **dropped and reported**, never fail-open | one malformed entry does not void the list |
| `complete-milestone.md:734` | `BASE_BRANCH=$(gsd_run query git.base-branch)` | resolves `beta` |
| `complete-milestone.md:775` | `git checkout ${BASE_BRANCH}` (squash arm) | checks out `beta`, not `main` |
| `complete-milestone.md:789` | `git merge --squash "$MILESTONE_BRANCH"` | **local only — no push follows** |
| `complete-milestone.md:804` | `git checkout ${BASE_BRANCH}` (history arm) | same |
| `complete-milestone/steps/git-tag.md:26` | `git push origin v[X.Y]` | **the only push; a tag, ungoverned by a `target: branch` ruleset** |
| `ship.md:46` | `BASE_BRANCH=$(gsd_run query git.base-branch)` | resolves `beta` |
| `ship.md:78` | `IS_PROTECTED=$(gsd_run query git.base-branch --is-protected "$CURRENT_BRANCH") \|\| IS_PROTECTED=""` | warns only |
| `ship.md:316` | `RANGE_BASE=$(git merge-base "${BASE_BRANCH}" HEAD)` | TDD-audit range anchors on `beta` — **needs a non-stale local `beta`** |
| `ship.md:373` | `--base "${BASE_BRANCH}"` | PRs target `beta` |
| `execute-phase.md:290` | `DEFAULT_BRANCH=$(gsd_run query git.base-branch …)` | **next phase branch forks off `origin/beta`** |
| `quick.md:197` | same | quick-task branches fork off `origin/beta` |
| `pr-branch.md:28` | `TARGET=${1:-$(gsd_run query git.base-branch)}` | default filter target becomes `beta` |
| `execute-phase/steps/protected-branch.md:10-15` | second `--is-protected` consumer | warns only; `branching_strategy: none` arm — **unreachable here** |

`ship.md:316` is worth flagging in the plan: with `BASE_BRANCH=beta`, a stale local `beta` (205
commits behind, measured) silently mis-anchors the TDD audit range. Recreate local `beta` from
`origin/beta` before running `/gsd-ship`.

### The beta lockstep cut recipe (D-04, operator-gated)

v1.22's recorded recipe, verbatim `[VERIFIED: .planning/MILESTONES.md:840]`:

> "dual-repo lockstep merged to `beta` and pushed (firmware `953f748` → CI auto-cut, app `4001396`
> → CI auto-cut); observed cut tag **`3.0.0b14`** in both repos — *derived from `gh release list`,
> never hardcoded* — with `publish.yml` manually dispatched (run 30555530238) because 6 of 13
> historical app betas never reached PyPI. Both community channels independently verified public:
> PyPI JSON API + clean-env `pip index`/`pip download` from `$(mktemp -d)`, and the firmware GitHub
> prerelease's three `.hex` assets via `gh release view`. Never via a green CI tick, never via the
> editable install. **No stable release** — PyPI `info.version` remains `2.0.7`."

The PR posture (v1.33's three PRs merged to `beta` at the v1.34 close) `[VERIFIED: .planning/MILESTONES.md:10]`:

> "The three v1.33 PRs merged to `beta`: `firestarter_prom#43` (`ee562a03`), `firestarter#56`
> (`01be7885`), `firestarter_app#54` (`db262331`), each firing its own beta pre-release cut; meta
> followed via PR **#44** (`eb87413e`). … **No sub-repo tag, no meta `v1.34` tag, and no stable
> release**."

**Adapted to measured 2026-09-02 state:**

1. Recreate local `beta` from `origin/beta` in all three repos; use `git cherry`, never `--is-ancestor`.
2. Open a PR to `beta` in each of `firestarter`, `firestarter_app`, `firestarter_prom` carrying the
   Phase 171–173 remainder (168/169 already landed — see the Runtime State Inventory).
3. Merge. `beta-build.yml` / `beta-release.yml` fire on the push to `beta`
   `[VERIFIED: firestarter/.github/workflows/beta-build.yml:25-27; firestarter_app/.github/workflows/beta-release.yml:23-25]`;
   each auto-commits its version bump **onto `beta`**, which carries no ruleset.
4. **PyPI arrives automatically** via `beta-release.yml`'s `pypi` job — see C-4. A manual
   `publish.yml` dispatch is optional and idempotent (`skip-existing: true`).
5. Verify both channels: `gh release list` for the observed tags (never predicted), the PyPI JSON
   API, and `pip install --pre` from a clean venv in `$(mktemp -d)`.
6. Meta's `origin/beta` tip is a merge commit, so meta's close tail **must be merged, not
   fast-forwarded**.
7. Tag meta `v1.35`. `git push origin v1.35` is a tag push and is ungoverned by the rulesets.
8. **No stable release.** Stable remains operator-gated, and per 999.46 the stable path is broken
   end to end anyway.

### Pinning gh#9 (D-12) — GraphQL only

Node ids measured this session `[VERIFIED: gh api graphql, 2026-09-02]`:

```
repository id : R_kgDOSX4ERw
issue #9 id   : I_kwDOSX4ER88AAAABId5Qdw
```

Current state: `pinnedIssues { totalCount: 0, nodes: [] }`. The read-back after pinning is the same
query; a `totalCount` of 1 naming issue 9 is the evidence.

### Backlog 999.46 — insertion shape

`[VERIFIED: .planning/ROADMAP.md:5097]` the highest existing row is
`### Phase 999.45: Unattributed \`_AT28C_DIP24_NAMES\` rename in \`build_db.py\` …`, and its body
uses the pattern: `**Goal:**`, a bolded framing paragraph (`**Filed, not fixed, on purpose.**`),
measured evidence with `file#Lnnn` links, `**Chosen fix**`, `**Test surface.**`, then `---`.
999.46 should follow that shape and be inserted immediately after 999.45's `---`, before the
`### v1.14 — Feasible-Gap Implementation (✅ PROMOTED …)` divider. **The orchestrator writes this,
not an executor.** The source content is `.planning/todos/pending/2026-09-02-rulesets-block-stable-release-version-bump.md`,
whose every workflow citation was re-verified this session:

| Citation | Verified content |
|---|---|
| `firestarter_app/.github/workflows/release.yml:2-5` | `on: push: branches: - main` ✓ |
| `…release.yml:32-35` | `git-auto-commit-action@v5` with `# env: # GITHUB_TOKEN: ${{ secrets.PERSONAL_ACCESS_TOKEN }}` **commented out** ✓ |
| `…release.yml:37-43` | `Release` step `softprops/action-gh-release@v2` **does** pass the PAT ✓ |
| `firestarter/.github/workflows/build.yml:34` | `branches: ['**', '!beta']` ✓ |
| `…build.yml:182-183` | `git-auto-commit-action@v5` gated `if: github.event_name == 'push' && github.ref == 'refs/heads/main'` ✓ |
| `…build.yml:199-200` | `Release` gated on the same condition ✓ |

The todo file is removed once the row exists.

### v1.34 `CLOSE-RECORD.md` — the structure D-09/D-11 build on

`[VERIFIED: .planning/v1.34/CLOSE-RECORD.md, 245 lines]` Section map:

```
# v1.34 — Close Record: Evidence Table, Merge Recommendation & Honesty Ledger
   header block: Milestone / Closed / Discharges / Status of this close
1. Scope — what ran, and what did not          (:11)   table: Phase | Planned | Actually executed | Status
2. CLOSE-01 — Evidence table                   (:32)
3. RCA — regression triage                     (:76)
4. CLOSE-02 — Merge recommendation             (:155)
5. CLOSE-03 — Honesty ledger                   (:192)  table: # | What v1.34 claims | What v1.34 explicitly does NOT claim   (H-1…H-10)
6. CLOSE-05 — Filed, not carried as prose      (:211)  table: Finding | Filing
7. CLOSE-04 — Deviation, recorded rather than hidden (:229)
```

The ledger table header is verbatim `| # | What v1.34 claims | What v1.34 explicitly does NOT claim |`
`[VERIFIED: :196]`, and §6's is `| Finding | Filing |` `[VERIFIED: :215]`. §7 is the deviation
section D-03 explicitly declined to reuse. `.planning/v1.35/` **does not exist yet**
`[VERIFIED: ls → No such file or directory]` and must be created.

### The inherited non-claims (D-11's mandatory inputs)

`[VERIFIED: .planning/phases/172-policy-one-tracker-protected-main/evidence/172-09-closing-sweep.txt]`
Four non-claims and three findings, each already stated so the ledger inherits rather than
rediscovers them:

- **NON-CLAIM 1** — the Actions bypass was **rejected at creation with HTTP 422** ("Actor GitHub
  Actions integration must be part of the ruleset source or owner organization") because all three
  repos are owned by the personal User account `henols`. D-09 was revised to
  `DeployKey:null:always`. All three repos measure **zero** deploy keys, so the bypass grants
  nothing today. **Named residual:** `actor_id: null` means *any* deploy key, present or future.
- **NON-CLAIM 2** — gh#6's required status checks and required review-thread resolution are
  knowingly not implemented, per D-11. The sweep says explicitly: *"Phase 173's ledger should state
  them as non-claims rather than let them read as quietly delivered."*
- **NON-CLAIM 3** — `Wiki check` is registered but has **never run**; "registered" and "observed
  green in CI" are different facts and only the first is true.
- **NON-CLAIM 4** — the prefill check came back PREFILLED, so no regression and no backlog item.
- **FINDING A** — the rulesets break the stable-release version bump in both sub-repos → 999.46.
- **FINDING B** — prom's default branch was **already red before Phase 172's merges**: a failing
  `Catalog sync check` on `ad08a06`, PR #34, dated 2026-08-31. Independently re-confirmed this
  session: `gh run list --repo henols/firestarter_prom` shows `completed / failure / Catalog sync
  check / main / push / 33447867312` at 2026-08-31T22:47:56Z `[VERIFIED: 2026-09-02]`.
- **FINDING C** — the unattributed `build_db.py` rename → Backlog 999.45.

All five evidence files the sweep cites were confirmed present, including the two it references
forward (`172-09-full-suite-final.txt`, `172-09-legacy01-final.txt`) `[VERIFIED: ls, 2026-09-02]`.

---

## State of the Art

| Old approach | Current approach | When changed | Impact on this phase |
|---|---|---|---|
| App beta PyPI upload depended on `release.published` event delivery, suppressed by the PAT's missing `workflow` scope | `beta-release.yml` calls `publish.yml` directly via `workflow_call` with `needs: github` and `secrets: inherit` | before 2026-08-22 (b32 onward on PyPI) | **D-04's manual dispatch is redundant** — see C-4 |
| In-repo `wiki/` source tree + `wiki-publish.yml` + `wiki.py publish`/`sidebar`/`check` | Wiki-only authoring: clone-commit-push, no PR, no CI on the edit; `wiki.py links` repointed at a clone | 2026-08-30 (model reversal) `[VERIFIED: .planning/ROADMAP.md:199]` | No publishing tooling exists to reuse; footers go by clone-commit-push |
| HONEST-01 as a live property of every migrated page | HONEST-01 is a **retired one-shot**; HONEST-02 is the only standing guard | 2026-08-31 editorial rewrites `[VERIFIED: .planning/v1.35/MIGRATION-TABLE.md:122-125]` | Do **not** re-baseline `MIGRATION-TABLE.md` SHAs to make anything green |
| `firestarter` beta cut only proved ARM at `beta` | `py32f071.yml` push filter removed; the loud ARM gate runs on every branch | recorded at `firestarter/.github/workflows/py32f071.yml:13-18` | The unprotected-ref control push fires it; non-publishing |
| `firestarter` `Protect main` ruleset present but `enforcement: disabled` | All three `active`, three-way identical | 2026-09-01T20:12–21:04 | `4998759`'s `created_at` of 2025-04-22 proves amendment, not recreation |

**Deprecated / outdated in this phase's inputs:**

- CONTEXT.md's "21 data rows" and "twelve footers" — superseded by C-1.
- D-04's "manually dispatch `publish.yml` … it is manual" — superseded by C-4.
- `REQUIREMENTS.md:119`'s "`/gsd-complete-milestone` pushes `main` directly today" — false; see C-3.
- `wiki.py`'s retired `publish` / `sidebar` / `check` subcommands — only `links` remains
  `[VERIFIED: tools/wiki/wiki.py:13-15, :297 — one `add_parser`]`.

---

## Assumptions Log

| # | Claim | Section | Risk if wrong |
|---|---|---|---|
| A1 | GitHub's rejection message for a `pull_request`-rule violation on a direct push is `remote: error: GH013: Repository rule violations found` with a `Changes must be made through a pull request` clause. Not observed this session — observing it requires performing the probe, which is the plan's job, not research's. | Push probe | A verify leg grepping for `GH013` could fail on a differently-worded rejection. **Mitigation: assert on the presence of a server-side `remote:` prefixed rule-violation line, and capture the full stderr verbatim rather than pattern-matching a single token.** |
| A2 | An empty commit produces no changed paths, so `paths-ignore`-filtered workflows are skipped on the control push. | Pitfall 4 | Only affects the CI-cost estimate, not correctness. `py32f071.yml` and `ci.yml` have no push-side path filter and would run regardless. |
| A3 | The record gate needs ~300 s against `STATE.md`'s long line and an rc=124 reads like a RED. Carried from the project's own todo, not re-measured here. | Pitfall 5 | A timed-out gate misread as a genuine failure. |
| A4 | `ubuntu-latest`'s bundled `python3` runs the existing checkers, so a new stdlib-only checker needs no `setup-python` step. Inferred from `wiki-check.yml` having no such step while three python legs already run there. | wiki-check.yml leg | If wrong, the leg fails at the first `python3` invocation — but so would the three existing legs, so this is low risk. |
| A5 | Deleting the throwaway control branch from each remote is permitted, because the `deletion` rule is scoped to `~DEFAULT_BRANCH`. Read from the ruleset conditions, not exercised. | Pitfall 4 | A blocked deletion leaves a stray branch on a public repo. |

## Open Questions

1. **How many pages get footers — 6, 8, or 11?**
   - What we know: 6 rows are provenance-bearing *and* live; 8 rows carry a source path + SHA (2 of
     those name dead pages); 11 pages exist on the wiki; **12 exists nowhere**.
   - What's unclear: whether D-09's intent extends to `Home` and `Contributing` (which have no
     provenance to state) or to the three unrecorded pages of C-2.
   - Recommendation: footer the **6**, and resolve C-1/C-2 as a `MIGRATION-TABLE.md` correction so
     the checker's bidirectional assertion is green on real inputs. State the count and the
     exclusions explicitly in `CLOSE-RECORD.md` so no reader infers "all pages are provenanced".

2. **Are `Protocol-Flags` and `Protocol-ID` corrected in the table, or restored to the wiki?**
   - What we know: a fresh clone has neither; both were carried in the main table as current pages;
     the defect survived being noticed in Phases 171 and 172. It is in `tools/`, so this phase may
     fix it.
   - What's unclear: whether their content was deliberately retired (like the five in the "Retired"
     table) or lost.
   - Recommendation: move them to the existing "Retired from the wiki after the migration closed"
     table with a stated reason, which is the table's own established mechanism, and record the
     move in the ledger. Restoring pages would be new content, which activation decision 4 forbids.

3. **Does the plan keep D-04's manual `publish.yml` dispatch as belt-and-braces?**
   - What we know: it is redundant (C-4) and harmless (`skip-existing: true`).
   - Recommendation: drop the dispatch, keep the channel *verification*, and record the change of
     posture as a correction in `CLOSE-RECORD.md` rather than silently deviating from D-04.

4. **Does POLICY-05's evidence cite the three already-merged `main` PRs?**
   - What we know: `prom#54`, `firestarter#58`, `firestarter_app#57` all merged into a protected
     `main` on 2026-09-02, after the rulesets existed.
   - Recommendation: cite them. The PR flow POLICY-05 documents is already demonstrated three
     times; D-10's leg PR is a fourth instance, not the first.

---

## Environment Availability

| Dependency | Required by | Available | Version | Fallback |
|---|---|---|---|---|
| `python3` (stdlib) | new `tools/wiki/` checker | ✓ | 3.12.14 | — |
| `git` | probe, wiki push, gitlink re-pin | ✓ | 2.55.0 | — |
| `gh` (authed `henols`) | issue replies, ruleset read-back, releases | ✓ | 2.98.0 | — |
| `gh api graphql` | pin gh#9 | ✓ | same binary | none — REST has no equivalent |
| `/usr/bin/grep` (GNU) | all gate evidence | ✓ | 3.11 | — |
| `node` + `.claude/gsd-core/bin/gsd-tools.cjs` | `git.base-branch` read-back | ✓ | v22.23.2 / 249 521 B | — |
| Network to `github.com` + `pypi.org` | clone, probe, channel verification | ✓ | — | — |
| `firestarter_prom.wiki.git` clone access | footers | ✓ (cloned this session @ `dc07042c`) | — | — |
| `curl` | PyPI JSON API | ✓ | — | `gh api` cannot reach PyPI |

**Missing dependencies with no fallback:** none.
**Missing dependencies with fallback:** none.

**Environment cautions:**
- `grep` on PATH is **ugrep 7.8.4** and honours `.gitignore`. Every gate uses `/usr/bin/grep`, and
  repository-wide scans are scoped to `git ls-files`.
- Devcontainer python is 3.12; app CI is 3.11. Irrelevant here (the checker is stdlib-only and runs
  under meta's workflow on `ubuntu-latest`), but do not import the app's test environment.

---

## Validation Architecture

`workflow.nyquist_validation` is absent from `.planning/config.json`
`[VERIFIED: .planning/config.json, 2026-09-02]`; the documented default is `true`
`[VERIFIED: .claude/gsd-core/references/planning-config.md:281]`, so this section applies.

### Test framework

| Property | Value |
|---|---|
| Framework | **None for this phase.** No pytest/jest suite covers `.planning/`, `tools/wiki/` checkers, `.planning/config.json`, or the wiki. Verification is by direct command invocation with captured output, exactly as Phases 171–172 did. |
| Config file | none — `tools/wiki/` has no `pytest.ini`, `conftest.py` or test directory `[VERIFIED: ls tools/wiki/]` |
| Quick run command | `python3 tools/wiki/<checker>.py --wiki-dir <clone> --migration-table .planning/v1.35/MIGRATION-TABLE.md; echo rc=$?` |
| Full suite command | `python3 tools/wiki/wiki.py links --source-dir <clone>` + `python3 tools/wiki/honest02_truth.py --wiki-dir <clone> --db firestarter_app/firestarter/data/chip_database.json --allowlist tools/wiki/claim-allowlist.json` + `python3 tools/wiki/dispatch_mirror.py --app-dir firestarter_app --fw-dir firestarter` + the new checker |

> `tools/wiki/selftest.sh` exists (28 368 B) and is the nearest thing to a suite, but it **mutates
> Phase 168's evidence files**. If used, `git checkout --` them immediately afterwards and assert
> the restoration.

### Phase requirements → test map

| Req | Behavior | Test type | Automated command | Exists? |
|---|---|---|---|---|
| POLICY-04 | Direct push to each protected `main` is rejected **by GitHub** | integration (network, one-shot) | `git fetch origin main && git checkout -B ruleset-probe origin/main && git commit --allow-empty -m probe && git push origin HEAD:main 2>&1 \| tee evidence/173-probe-<repo>.txt` — assert stderr carries a `remote:` rule-violation line | ❌ new |
| POLICY-04 | Push to an **unprotected** ref is accepted (proving default-branch scoping) | integration | `git push origin ruleset-probe:refs/heads/probe-<ts>` then `git push origin :refs/heads/probe-<ts>` | ❌ new |
| POLICY-04 | Ruleset state unchanged by the probe | integration | `gh api repos/henols/<r>/rulesets/<id> --jq '{id,enforcement,current_user_can_bypass,conditions,bypass_actors}'` before **and** after; assert byte-equal | ❌ new |
| POLICY-04 (cut, gated) | Both channels carry the observed tag | manual + integration | `gh release list`; PyPI JSON API; `pip install --pre` in `$(mktemp -d)` venv. **Never** predicted, never the editable install | ❌ new, conditional |
| POLICY-05 | `git.base-branch` resolves `beta` | unit-ish | `node .claude/gsd-core/bin/gsd-tools.cjs query git.base-branch` → `beta` | ❌ new (recipe proven above) |
| POLICY-05 | `main` and `beta` both read protected; a feature branch does not | unit-ish | `… --is-protected main` → `true`; `… --is-protected beta` → `true`; `… --is-protected gsd/v1.35-…` → `false` | ❌ new |
| POLICY-05 | The note and the `CLAUDE.md` pointer exist and resolve | file assertion | `test -f .planning/notes/v135-close-procedure-under-protection.md` + `/usr/bin/grep -F 'v135-close-procedure-under-protection.md' CLAUDE.md` | ❌ new |
| D-10 | Footer checker RED on a planted defect, GREEN on real inputs | integration, planted-first | run against a mutated copy (RED, capture `ERROR:`), restore, re-run (GREEN) | ❌ new |
| D-10 | The new leg does not break the three existing legs | integration | run all four against one fresh clone | partially exists |
| D-09 | Footers do not turn `honest02` or `wiki.py links` RED | integration | both checkers against a **fresh** post-push clone | exists (commands) |
| D-12 | gh#9 pinned; gh#7 and gh#6 closed; gh#5 and gh#9 open; 4 comments present | integration | `gh api graphql` `pinnedIssues`; `gh api repos/henols/firestarter_prom/issues/{5,6,7,9} --jq '{state,comments}'` | ❌ new |
| Criterion 4 | 999.46 exists; the todo file is gone | file assertion | `/usr/bin/grep -c '^### Phase 999.46' .planning/ROADMAP.md` = 1; `test ! -e .planning/todos/pending/2026-09-02-rulesets-block-stable-release-version-bump.md` | ❌ new |
| NO-COMMENTS | The new checker carries zero `#` lines but the shebang | source scan | `[ "$(/usr/bin/grep -cE '^\s*#' tools/wiki/<checker>.py)" = 1 ]` | ❌ new (pattern proven on all four existing files) |
| Gitlinks | Both submodules re-pinned and equal | integration | per-submodule `git -C <sub> rev-parse HEAD` vs `git ls-tree HEAD <sub>` | pattern exists (172-09) |

### Sampling rate

- **Per task commit:** the checker's own quick run + the NO-COMMENTS source scan (< 5 s).
- **Per wave merge:** all four `tools/wiki/` checkers against one fresh wiki clone.
- **Phase gate:** the full closing sweep — written **before** any checkbox is flipped, per plan
  172-09's T-172-35 pattern and this project's recorded failure mode of executors marking
  multi-plan requirements complete ahead of their evidence.

### Wave 0 gaps

- [ ] `tools/wiki/<checker>.py` — the footer/provenance guard (D-10); no test file, verified by
      direct invocation with planted-failure evidence
- [ ] `.github/workflows/wiki-check.yml` — a fourth `run:` leg, **comment-free**
- [ ] `.planning/v1.35/` — the directory does not exist and must be created before
      `CLOSE-RECORD.md`
- [ ] `.planning/notes/v135-close-procedure-under-protection.md` — does not exist
      `[VERIFIED: ls .planning/notes/ — 23 files, not this one]`
- [ ] `evidence/` for phase 173 — the directory does not exist yet
- [ ] Framework install: **none required**

---

## Security Domain

`security_enforcement` is not set in `.planning/config.json`, so it is enabled by default.

### Applicable ASVS categories

| ASVS category | Applies | Standard control |
|---|---|---|
| V2 Authentication | no | No auth surface; `gh` uses an existing OAuth token |
| V3 Session Management | no | — |
| V4 Access Control | **yes** | The rulesets **are** the access control. `current_user_can_bypass: never` on all three; the only bypass actor is `DeployKey:null:always` with **zero** deploy keys registered. The `actor_id: null` residual (any deploy key, present or future) is a named, carried risk — NON-CLAIM 1 |
| V5 Input Validation | **yes** | The new checker parses `MIGRATION-TABLE.md` (a Markdown table) and wiki page text. Use anchored `re` patterns and `pathlib`; never `eval`, never a shell interpolation of a parsed field. `dispatch_mirror.py`'s anchored `^\|\s*…` row regexes are the precedent `[VERIFIED: tools/wiki/dispatch_mirror.py:38-43]` |
| V6 Cryptography | no | SHAs are compared as opaque strings; nothing is hashed or signed here. `honest02_truth.py`'s `db-sha256-16` is not touched by this phase |
| V12 File/Path handling | **yes** | The checker must not follow a `MIGRATION-TABLE.md` source path outside the wiki clone or the named sub-repo. Resolve and confirm containment before opening |
| V14 Configuration | **yes** | `wiki-check.yml` keeps `permissions: contents: read` `[VERIFIED: :7-8]`; the new leg must not widen it. Pin no new action versions — the leg adds no `uses:` |

### Known threat patterns for this stack

| Pattern | STRIDE | Standard mitigation |
|---|---|---|
| A green checker that never fails (vacuous gate) | Repudiation | Planted-failure-first: RED observed and recorded before the leg is trusted (D-10, Phase 172 D-14) |
| An unreviewed wiki edit silently removing a footer | Tampering | The D-10 checker is the only guard — the wiki has no PR, no diff, no CI on the edit |
| A push probe that is rejected for the wrong reason | Repudiation | Assert the **server's** rule-violation text, not the exit code (Pitfall 1) |
| `actor_id: null` deploy-key bypass silently activated by adding any deploy key | Elevation of Privilege | Carried as NON-CLAIM 1; **do not** add a deploy key as 999.46's remedy without re-stating this |
| Path traversal via a crafted `MIGRATION-TABLE.md` row | Tampering | Containment check on every resolved path (V12) |
| A public comment posted without review | Repudiation | D-13's blocking wording review; `updatedAt` bumps on creation, not on a body edit, so a correction reads as a second statement |
| Widening `PERSONAL_ACCESS_TOKEN`'s scope to fix the release path | Elevation of Privilege | Explicitly rejected in `publish.yml:15-20`; 999.46's recommended remedy (option 2) avoids it |

---

## Sources

### Primary (HIGH confidence — read this session, with line citations)

- `.planning/phases/173-…/173-CONTEXT.md` — all 13 decisions, mechanical constraints, discretion
- `.planning/REQUIREMENTS.md:68-69, :110-130, :181-182` — POLICY-04/05 texts and the constraint block
- `.planning/ROADMAP.md:29, :199, :231, :235-241, :452, :5097-5115` — milestone, checklist, 999.45
- `.planning/MILESTONES.md:10, :795, :826-845` — v1.34 close posture, v1.23 and v1.22 release states
- `.planning/v1.34/CLOSE-RECORD.md` (245 lines) — §1/§5/§6/§7 structure
- `.planning/phases/172-…/evidence/172-09-closing-sweep.txt` — 4 non-claims + 3 findings
- `.planning/todos/pending/2026-09-02-rulesets-block-stable-release-version-bump.md` — 999.46 source
- `.claude/gsd-core/bin/lib/git-base-branch.cjs:13, :79-92, :113-164, :302-311, :440-500`
- `.claude/gsd-core/bin/lib/config-loader.cjs:832-833` — both keys flattened by `loadConfigResolved`
- `.claude/gsd-core/workflows/complete-milestone.md:734, :775, :789, :804`
- `.claude/gsd-core/workflows/complete-milestone/steps/git-tag.md:26`
- `.claude/gsd-core/workflows/ship.md:46, :78, :194, :199, :316, :373, :491, :521`
- `.claude/gsd-core/workflows/execute-phase.md:290`; `quick.md:197`; `pr-branch.md:28`
- `.claude/gsd-core/workflows/execute-phase/steps/protected-branch.md:9-15`
- `.claude/gsd-core/references/planning-config.md:35-36, :281, :330-331`
- `.planning/v1.35/MIGRATION-TABLE.md` (165 lines, all three tables)
- `tools/wiki/dispatch_mirror.py`, `honest02_truth.py`, `wiki.py`, `honest01_claims.py`
- `.github/workflows/wiki-check.yml` (125 lines), `.github/workflows/catalog-sync-check.yml:1-20`
- `firestarter_app/.github/workflows/{release,beta-release,publish,ci}.yml`
- `firestarter/.github/workflows/{build,beta-build,py32f071}.yml`
- `/workspaces/CLAUDE.md`, `/workspaces/.planning/config.json`

### Primary (HIGH confidence — live API/tool reads this session, 2026-09-02)

- `gh api repos/henols/{firestarter_prom,firestarter,firestarter_app}/rulesets[/{id}]`
- `gh api repos/henols/{…}/rules/branches/{main,beta}`
- `gh api repos/henols/firestarter_prom/issues/{5,6,7,9}`
- `gh api graphql` — `pinnedIssues`, repository and issue node ids
- `gh api repos/henols/firestarter_prom/actions/workflows`; `gh run list`
- `gh pr list` / `gh pr view` across all three repos; `gh release list`
- `git clone --depth 1 https://github.com/henols/firestarter_prom.wiki.git` @ `dc07042c`
- `curl https://pypi.org/pypi/firestarter/json`
- Local probes: `git.base-branch` read-back in a scratch repo; footer impact on `honest02_truth.py`
  and `wiki.py links` in a throwaway clone copy; non-fast-forward push in a `/tmp` bare repo

### Secondary (MEDIUM confidence)

- `.planning/notes/v135-wiki-only-reversal.md`, `.planning/notes/v135-phases-169-170-executed-ad-hoc.md`
  — existence confirmed; content cited only through ROADMAP's summaries of them

### Tertiary (LOW confidence)

- A1 (GitHub's exact `GH013` rejection wording) — training knowledge, unobservable without pushing
- A3 (record-gate timeout behaviour) — carried from the project's own todo, not re-measured

---

## Metadata

**Confidence breakdown:**

- **Standard stack:** HIGH — nothing is installed; every tool version was read from the tool itself.
- **Architecture / checker conventions:** HIGH — the `0/1/2` contract, the argparse shape, the
  `ERROR:`/`OK:` split and the zero-comment convention were each read out of all four existing
  scripts, and the zero-comment claim was counted mechanically.
- **GSD close machinery:** HIGH — every line number cited in CONTEXT.md was reopened and confirmed,
  three further consumers were found that CONTEXT.md does not name, and the D-06 edit's read-back
  was **executed** against a scratch copy rather than predicted.
- **Live GitHub state:** HIGH — read from the API, never the UI, per the standing rule.
- **Wiki counts:** HIGH — clone, `ls`, and a mechanical row count; this is where CONTEXT.md's
  numbers were found wrong.
- **Pitfalls:** HIGH for 1, 2, 3, 4, 6, 7 (each demonstrated or read from source); LOW for 5.
- **Push-probe rejection text:** LOW (A1) — the only material fact this research could not observe
  without performing an outward-facing action it is forbidden to perform.

**Research date:** 2026-09-02
**Valid until:** 2026-09-09 — short deliberately. The live wiki, the four upstream issues, the
release channels and the ruleset state are all mutable, and three of the four corrections above
exist precisely because a previously-measured state had moved.
