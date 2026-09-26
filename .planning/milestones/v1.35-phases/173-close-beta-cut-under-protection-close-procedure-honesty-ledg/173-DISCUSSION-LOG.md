# Phase 173: CLOSE — Beta Cut Under Protection, Close Procedure & Honesty Ledger - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-09-02
**Phase:** 173-close-beta-cut-under-protection-close-procedure-honesty-ledger
**Areas discussed:** Beta cut demonstration (POLICY-04), Close procedure under protection (POLICY-05), Honesty ledger placement, Upstream reply dispositions

---

## Area selection

Four gray areas were offered. Rather than selecting, the operator asked which ones Claude
thought needed discussion. Claude recommended three that genuinely required an operator
decision — the beta-cut demonstration (outward-facing), the ledger's reader-facing surface (a
scope judgment under "relocate and correct only"), and the upstream replies (public posts in
the operator's name) — plus one narrow question out of POLICY-05 (whether GSD's `base_branch`
gets repointed, which changes behaviour for every future milestone). Claude stated it would
decide the rest of POLICY-05 itself, because `current_user_can_bypass: never` on all three
rulesets makes the "documented admin bypass" branch factually unavailable, settling it by
evidence rather than preference. The operator approved that selection.

---

## Beta cut demonstration (POLICY-04)

### Q1 — What shape should the POLICY-04 demonstration take?

| Option | Description | Selected |
|--------|-------------|----------|
| Probe now, real cut on your word | Rejection probe against the real repos inside the phase; real cut only on explicit authorization | ✓ |
| Real lockstep cut, full stop | Merge to `beta` ×3 and let CI cut the pair — the close's normal terminal step | |
| Rejection probe only | No cut at all; the criterion permits an equivalent dry run | |
| Scratch-repo rehearsal | Throwaway repo with an identical ruleset, whole sequence rehearsed | |

**User's choice:** Probe now, real cut on your word.
**Notes:** Claude flagged before the question that `beta` appears in no ruleset condition and
both beta workflows auto-commit onto `beta` — so a real cut would likely prove only that
nothing was ever in its way, at full outward-facing cost, while a probe can produce an actual
rejection. The scratch-repo option was argued against on the grounds that Phase 172 had already
found these repositories behave differently from the general case (the Actions bypass returning
HTTP 422 on personal-account ownership).

### Q2 — If the real cut is not authorized before the close, how is POLICY-04 marked?

| Option | Description | Selected |
|--------|-------------|----------|
| Complete on the probe, non-claim in the ledger | Criterion 1's own wording permits the dry run; the missing half is stated | ✓ |
| Stays PENDING — close with one open requirement | v1.34's shape for NOT-RUN phases | |
| Recorded as a deviation, like v1.34's CLOSE-04 | Purpose satisfied, letter not | |

**User's choice:** Complete on the probe, non-claim in the ledger.
**Notes:** Claude then stated two mechanical calls rather than asking: the probe uses an empty
commit so an unexpected success is a no-op rather than content stuck on a protected branch, and
`git push --dry-run` is rejected as evidence because it sends no pack and therefore never
reaches GitHub's receive-stage ruleset evaluation — the exact "reading of the configuration"
the criterion forbids.

### Q3 — How deep should the phase go on the rulesets breaking the stable-release path?

| Option | Description | Selected |
|--------|-------------|----------|
| File 999.46 with a recommended remedy named | Pick the off-`main` version bump as the recommendation | ✓ |
| File 999.46 flat — three candidates, no recommendation | Record the menu, let the promoter choose | |
| Fix the workflows now | Out of scope by the milestone's scope note, offered as an override | |

**User's choice:** File 999.46 with a recommended remedy named.
**Notes:** No workflow file is edited. The two non-recommended candidates are recorded with
their objections — a PAT push meets the same `pull_request` rule since bypass is `never`, and a
deploy key relies on `actor_id: null` conferring bypass on any key.

### Q4 — When authorized, what does the cut include?

| Option | Description | Selected |
|--------|-------------|----------|
| Full lockstep: PR to beta ×3, pair, PyPI dispatch, meta tag | v1.22's recipe with v1.30's PR posture | ✓ |
| Cut only — no PyPI dispatch, no meta tag | v1.34's minimal shape | |
| Direct `--no-ff` merge + push ×3, no PR | Pre-v1.30 practice | |
| Decide it when I authorize | Leave the recipe open | |

**User's choice:** Full lockstep.
**Notes:** The PyPI dispatch was argued as load-bearing rather than ceremony — it is manual,
and 6 of 13 historical app betas never reached PyPI, so skipping it reproduces the v1.21
channel drift. The "decide later" option was argued against on the grounds that the standing
gotchas (stale local `beta` poisoning `git cherry`, meta's beta tip being a merge commit that
cannot fast-forward) would then be rediscovered under time pressure.

---

## Close procedure under protection (POLICY-05)

### Q1 — How should the close procedure be fixed for PR-only `main`?

| Option | Description | Selected |
|--------|-------------|----------|
| Both config keys, plus a short note | `git.base_branch: beta` + `git.protected_branches: [main]`, then prose for what config cannot express | ✓ |
| Config keys only, no prose | Strongest "by construction", nothing to go stale | |
| Prose only — leave config alone | A document the tooling would ignore | |
| Amend the vendored gsd-core workflows | Most direct, silently lost on `/gsd-update` | |

**User's choice:** Both config keys, plus a short note.
**Notes:** This option only became available mid-discussion. Claude found while reading
`git-base-branch.cjs` that GSD exposes `git.base_branch` as tier 1 of its precedence ladder and
`git.protected_branches` alongside it — so POLICY-05 could be met declaratively rather than by
prose. Claude had warned that folding `beta` into `protectedBranches` was "a real behaviour
change" and corrected that immediately after: both consumers only warn and continue, and the
second applies to `branching_strategy: none` while this project is `milestone`, so the repoint
cannot break the close.

### Q2 — Where does the close-procedure note live?

| Option | Description | Selected |
|--------|-------------|----------|
| CLAUDE.md, with the detail in `.planning/notes/` | Auto-loaded every session, so it is read whether or not anyone looks | ✓ |
| `.planning/notes/` only | The established convention, but nothing auto-loads it | |
| `.planning/PROJECT.md` §Context | Locked-decisions section, but 414 KB read at budgeted depth | |
| The wiki | Consistent with the milestone's thesis, but no human reader and fails the purpose | |

**User's choice:** CLAUDE.md, with the detail in `.planning/notes/`.
**Notes:** The question was framed on POLICY-05's own stated purpose — that the next
`/gsd-complete-milestone` "does not discover the change by failing" — which makes being *read*
the requirement rather than being written.

### Decided by precedent rather than asked

Claude declined to ask three further questions in this area, on the grounds that the operator
had chosen the literally-true option in every prior turn:

- `git.protected_branches: ["main"]` — declares in config what is now true on GitHub.
- The note covers the stable-release route to `main` and states plainly that it is blocked end
  to end: a PR is the only route, and the version bump then fails per 999.46.
- Meta's `CLAUDE.md` only, since the close runs in meta rather than a submodule.

---

## Honesty ledger placement

### Q1 — Where does the ledger land?

| Option | Description | Selected |
|--------|-------------|----------|
| Internal record + a per-page provenance line on the wiki | Full ledger in `.planning/v1.35/CLOSE-RECORD.md`, footers generated from MIGRATION-TABLE.md | ✓ |
| Internal record only | v1.34's precedent, cheapest, invisible externally | |
| Internal record + one wiki page stating it once | One edit, but owes two navigation edits and a chip-page reader never sees it | |
| Internal record + a line on Home only | Minimal footprint, furthest from the pages it qualifies | |

**User's choice:** Internal record + a per-page provenance line on the wiki.
**Notes:** The question was grounded on a gap: HONEST-02's stamp reaches only the DB-backed
pages, while "relocation is not verification" is a claim about all twelve. Claude noted before
asking that `MIGRATION-TABLE.md` carries two rows naming wiki pages a fresh clone does not have
(`Protocol-Flags`, `Protocol-ID`) — deferred through Phases 171 and 172, and fixable here
because the table lives in `tools/` rather than product source.

### Q2 — Does the provenance footer get a mechanical guard?

| Option | Description | Selected |
|--------|-------------|----------|
| New checker + a `wiki-check.yml` leg, demonstrated RED first | Planted-failure-first, per Phase 172 D-14's bar | ✓ |
| No guard — static text | Nothing detects a footer removed by a careless wiki edit | |
| Guard the table, not the footers | Fixes the known defect, leaves the reader-visible part unchecked | |

**User's choice:** New checker + a `wiki-check.yml` leg, demonstrated RED first.
**Notes:** Claude then recorded two consequences rather than asking about them — the leg needs a
fourth PR into a now-protected `main`, which doubles as POLICY-05 evidence rather than being
pure overhead; and `tools/wiki/selftest.sh` mutates Phase 168's evidence and needs a
`git checkout --` after every run.

### Decided from the criterion's wording rather than asked

The ledger is **one consolidated, comprehensive table**, not v1.34's curated ten rows, because
criterion 3 says "pairs **every** claim this milestone makes with its explicit non-claim". It
absorbs criterion 3's three minimums, Phase 172's four non-claims and three findings,
POLICY-04's own non-claim, and Phase 169's declined FRONT-02.

---

## Upstream reply dispositions

### Q1 — What is the disposition set?

| Option | Description | Selected |
|--------|-------------|----------|
| Reply on all four; close #7 and #6; keep + pin #9; keep #5 | Widens deliberately past criterion 5's three | ✓ |
| Reply on all four, close none | Say everything, decide nothing | |
| Only the three criterion 5 names — leave #6 silent | Stay inside the criterion | |
| Reply and close all four | Clean tracker, but FUT-W loses its upstream home | |

**User's choice:** Reply on all four; close #7 and #6; keep + pin #9; keep #5.
**Notes:** Claude checked prom's `pinnedIssues` before asking and found it **empty** — so
criterion 5's phrase "the pinned orientation issue" and 999.13's "gh#9 stays open as the pinned
orientation issue" both describe an end state never actually configured. Pinning it was argued
to be part of what criterion 5 asks for. The widening to gh#6 was argued on the grounds that it
is the issue the milestone most directly delivered and that D-11's two declines would otherwise
read as quietly skipped.

### Q2 — How do the replies get from draft to posted?

| Option | Description | Selected |
|--------|-------------|----------|
| Draft all four, blocking wording review, then post | v1.22 D-02's precedent for outward-facing text | ✓ |
| Post directly — they are factual statements | Saves a round trip; no precedent for unreviewed community text | |
| Draft only — defer posting entirely | Criterion 5's escape hatch; meets it by deferral | |

**User's choice:** Draft all four, blocking wording review, then post.
**Notes:** Reversibility was flagged as one-way — a comment on a public tracker is indexed, and
`updatedAt` bumps on creation rather than on a body edit, so a correction reads as a second
statement rather than a replacement.

---

## Claude's Discretion

The operator said "you decide" to nothing explicitly, but delegated the whole of POLICY-05
beyond the config-repoint question, and accepted six items Claude decided by precedent or by
criterion wording rather than asking. The discretion list carried into CONTEXT.md covers: the
four reply drafts' prose (subject to the blocking review), the footer's exact wording, the new
checker's language and file name, whether the two stale MIGRATION-TABLE rows are fixed or
filed, the ledger's row ordering and identifiers, commit granularity, and which further findings
earn their own backlog row.

## Deferred Ideas

A ruleset on `beta` (and the asymmetry D-06 creates, where GSD treats `beta` as protected while
GitHub does not); required status checks on `main` (gh#6, declined by Phase 172 D-11); required
review-thread resolution (same); GitHub private vulnerability reporting (declined twice, by
Phase 171 D-02 and Phase 172 D-04); a `henols/.github` default community-health repository;
fixing the release path itself, which 999.46 describes and the scope note forbids;
FUT-W-01…05; and Backlog 999.9's rename sweep, to which this phase's own outputs are added.

Thirty-five of thirty-seven pending todos matched the phase, thirty-four on generic keywords
only. One was folded — the rulesets-block-stable-release finding, which criterion 4 explicitly
owes a backlog row. Two more were read closely before being set aside: the GSD-provenance
comment sweep (product source, out of scope) and the record-gate superlinearity on STATE.md's
single long line (tooling defect, carried as a known hazard rather than as work).
