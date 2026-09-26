# Phase 167: WIKI — Bootstrap, In-Repo Source, Sync & Drift Check - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-08-30
**Phase:** 167-WIKI — Bootstrap, In-Repo Source, Sync & Drift Check
**Areas offered:** Source layout & page naming; Publish trigger & who runs it; Home & sidebar — generated or hand-authored; Proof strategy & where tests live
**Areas discussed:** Source layout & page naming; Publish trigger & who runs it; Home & sidebar — generated or hand-authored
**Area left to Claude:** Proof strategy & where tests live (not selected)

---

## Source layout & page naming

### Q1 — Where should the in-repo wiki source tree live in `firestarter_prom`?

| Option | Description | Selected |
|--------|-------------|----------|
| `wiki/` at repo root | Pages at `wiki/`, tooling separately at `tools/wiki/`. Content is not tooling — a contributor editing a page never opens `tools/`. Top-level and obvious to anyone landing on the repo, which matters when prom becomes the front door in 169. | ✓ |
| `docs/` at repo root | Conventional name, but "docs" is the name of the generated-site option this project retired, and sits one letter from the `doc/` directories 168 deletes. Invites exactly the confusion this milestone is trying to end. | |
| `tools/wiki/pages/` | Everything wiki-related under one directory, mirroring `tools/catalog/` where source and tooling already live together. Consistent with existing precedent, but buries content under a tooling path. | |

**User's choice:** `wiki/` at repo root (the recommended option).

### Q2 — Should `wiki/` be flat, or organized into subdirectories by topic?

| Option | Description | Selected |
|--------|-------------|----------|
| Flat — one directory | `wiki/Page-Name.md`, 1:1 with what lands in the wiki. GitHub addresses wiki pages by filename alone regardless of directory, so flat means source path == published page, and the drift check is a plain directory diff. Costs in-repo browsability once ~16 pages accumulate. | ✓ |
| Nested by topic, flattened at publish | Reads better in the repo, but source path no longer equals wiki URL — the publish step becomes a translation, two pages in different folders can silently collide on one wiki name, and the drift check has to reverse the mapping. | |
| Nested and published nested | GitHub's wiki git repo does accept subdirectories, but the web UI still addresses pages by bare filename and the page list flattens them anyway — collision risk with none of the navigation benefit. | |

**User's choice:** Flat — one directory (the recommended option).

### Q3 — What filename convention should wiki pages use?

| Option | Description | Selected |
|--------|-------------|----------|
| `Title-Case-With-Hyphens.md` | `Shield-Revisions.md` → title "Shield Revisions", URL `/wiki/Shield-Revisions`. GitHub-native, readable titles and readable URLs in the READMEs 169/170 will write. Cost: every migrating file is renamed, so 168 must produce a real old-path→page mapping — which its criterion 1 asks for anyway. | ✓ |
| Keep existing filenames verbatim | Zero-translation move and the most trivially auditable diff, but the wiki gets page titles reading "PROTOCOLS" next to "protocol id" — the existing inconsistent casing becomes permanent, public navigation. | |
| `all-lower-case-hyphens.md` | Uniform and matches most of today's app `doc/` files, but GitHub renders the title lowercase too — a sidebar of "shield revisions", "protocol id", "lockable proms" reads as unfinished. | |

**User's choice:** `Title-Case-With-Hyphens.md` (the recommended option).

### Q4 — How should the source-file → wiki-page mapping be established?

| Option | Description | Selected |
|--------|-------------|----------|
| Derive mechanically + separate migration table | Publish derives the page name from the filename — nothing to keep in sync, so publishing cannot drift from a manifest. Provenance (old repo path → wiki page) lives in its own checked-in table that 168 fills in, greppable for the rename sweep and satisfying 168's "auditable rather than asserted". | ✓ |
| A manifest file the publish script reads | `wiki/PAGES.toml` lists source → page → old path; publish consults it. One authoritative place, and unlisted files can be hard-failed as a bonus orphan check. Cost: adding a page means editing two files, and a stale manifest is a new drift class the drift check does not cover. | |
| Convention only — mapping recorded in the phase summary | Lightest touch, but the mapping then lives in `.planning/` history rather than a live artifact, so the 999.9 sweep has nothing current to grep. | |

**User's choice:** Derive mechanically + separate migration table (the recommended option).

**Notes:** No follow-up questions requested for this area.

---

## Publish trigger & who runs it

### Q1 — What actually publishes `wiki/` to the GitHub wiki?

| Option | Description | Selected |
|--------|-------------|----------|
| Local one-command script only | `tools/wiki/publish.sh`, run by a maintainer. Exactly satisfies WIKI-03, mirrors `sync_to_subrepos.sh`, needs no secrets or CI wiki-push permissions. Publishing stays a deliberate act. | |
| Script + CI publish on merge to `main` | Same script, also invoked by an Action so the wiki can never sit stale behind the integration branch. Concern raised at ask time: `main` is about to go behind an enforcing ruleset (172), and an auto-publish could push half-migrated content during 168. | ✓ |
| CI-only, no local path | Rejected on its face — WIKI-03 says a maintainer publishes with one command, and there would be no way to run the criterion 2 overwrite demonstration. | |

**User's choice:** Script + CI publish on merge.

**Notes:** Choosing the CI option exposed a follow-up the original options had assumed away — see Q2. The presented option said "merge to `main`"; the branch was then corrected to `beta` on measured evidence, so the operative decision is *script + CI publish on merge to `beta`*.

### Q2 — Which branch triggers the CI publish? *(follow-up, raised on measured evidence)*

Measured and presented before asking: `origin/beta` is **2,842 commits ahead of `origin/main`** on this meta repo (`main` @ `8c586d44`, `beta` @ `7132aea3`). `main` is GitHub's default branch but is drastically stale; this project's convention pushes `beta`, and v1.34 reached `beta` via PR #44 with `main` never following. A publish keyed to `main` would fire approximately never.

| Option | Description | Selected |
|--------|-------------|----------|
| `beta` | Matches how this project actually integrates — milestone branches fork `beta` and return to it by PR at close. The wiki then tracks integrated documentation. Cost: the wiki reflects `beta`, so it can show a page describing behaviour `main` has not shipped; that has to be stated somewhere on the wiki, not left implicit. | ✓ |
| `main` | The wiki only ever shows released state. Honest in principle, but `main` is 2,842 commits behind and stable promotion is operator-gated — the wiki would sit empty or stale indefinitely, and 169's front-door README would link into it. | |
| Both, `beta` publishing and `main` as a no-op guard | Current docs plus a released-state assertion, at the cost of a second workflow and a check that reports drift by design whenever `beta` is ahead. | |

**User's choice:** `beta` (the recommended option).

### Q3 — Where should the drift check run, and against what?

| Option | Description | Selected |
|--------|-------------|----------|
| PR check on `wiki/` changes + on demand | Mirrors `catalog-sync-check.yml`: path-filtered to `wiki/` and its own workflow file, runs on PRs into `beta` and via `workflow_dispatch`, and is runnable locally as the same command. Catches a page edited in the wiki UI before the next publish overwrites it, without a scheduled job. | ✓ |
| Scheduled cron against the live wiki | Catches out-of-band wiki edits even when nobody opens a PR — the actual failure mode WIKI-02 guards against. Cost: a job that sits red from the operator's first hand-created page until 168 publishes over it, and red-by-default checks get ignored. | |
| Local command only, no CI | Simplest and always runnable, but a check nobody is prompted to run is a check that does not run. `catalog-sync-check.yml` exists because this project already decided sync assertions belong in CI. | |

**User's choice:** PR check on `wiki/` changes + on demand (the recommended option).

### Q4 — What should the publish command do by default, given publishing is destructive by design?

| Option | Description | Selected |
|--------|-------------|----------|
| Dry-run by default, `--push` to publish | The dry-run IS the drift check — one code path, two entry points, so the check can never diverge from what publish actually does. A maintainer sees what will be destroyed before it is. "One command" in WIKI-03 becomes one command plus one flag. | ✓ |
| Push by default, `--dry-run` available | Literal one-command publish, matching `sync_to_subrepos.sh`. Cost: an accidental run silently destroys any wiki-side edit with no preview — and the CI path pushes unattended anyway, so the local default is the only place a human is in the loop. | |
| Push by default, refuse on detected hand-edits without `--force` | Protects a contributor's wiki edit while keeping one-command publishing. But it puts the in-repo source second in a conflict, contradicting WIKI-02's authority rule — and criterion 2's plain re-publish-overwrites demonstration would then need `--force` to pass. | |

**User's choice:** Dry-run by default, `--push` to publish (the recommended option).

**Notes:** This area ran five questions rather than four — Q2 was inserted after Q1's answer surfaced a branch-topology fact that invalidated the premise of the option as worded.

---

## Home & sidebar — generated or hand-authored

### Q1 — How should `Home.md` and `_Sidebar.md` be produced?

| Option | Description | Selected |
|--------|-------------|----------|
| Generated sidebar, hand-authored Home | `_Sidebar.md` generated from `wiki/` so completeness is mechanical and no page can be missing from navigation. `Home.md` written by hand — curated ordering, a sentence per page, and an honest place to state the beta-vs-released caveat. The reachability check then has something real to catch: a page in the sidebar but absent from Home. | ✓ |
| Both generated from `wiki/` | Orphaning becomes impossible by construction and WIKI-05 is satisfied trivially. That is also the problem — criterion 5's link-walk becomes a tautology, a check that can only ever be green. This project has explicitly ruled that a check seen only green proves nothing. | |
| Both hand-authored | Maximum curation and the reachability check is genuinely load-bearing. But hand-maintained navigation is exactly the silent-drift failure mode the milestone's honesty note calls out, and 168 adds 13 pages at once — the first omission would ship. | |

**User's choice:** Generated sidebar, hand-authored Home (the recommended option).

### Q2 — Is the generated `_Sidebar.md` committed, or produced only at publish time?

| Option | Description | Selected |
|--------|-------------|----------|
| Committed, regenerated by the command, freshness checked in CI | Matches this repo's strongest precedent: `messages.h` and `messages.py` are generated artifacts that ARE committed, regenerated by `sync_to_subrepos.sh`. Keeps the drift check a plain directory diff with zero exclusions — every exclusion is a hole in an integrity check. Cost: a stale committed artifact needs its own CI freshness leg. | ✓ |
| Generated at publish time, never committed | No stale artifact possible and nothing to regenerate by hand. But the wiki then holds a file with no in-repo counterpart, so the drift check must special-case `_Sidebar.md` — punching the first hole in the check WIKI-04 exists to make trustworthy. | |
| Generated at publish time, drift check reconstructs it to compare | No committed artifact and no exclusion — the check regenerates the sidebar in memory and compares. Clean in principle, but the drift check now contains generation logic, so a generator bug reads as "no drift" rather than as a failure. | |

**User's choice:** Committed, regenerated by the command, freshness checked in CI (the recommended option).

### Q3 — What exactly should the reachability check assert (criterion 5)?

| Option | Description | Selected |
|--------|-------------|----------|
| Orphan check + internal links resolve | Every page in `wiki/` is linked from Home or `_Sidebar`, and every internal wiki link points at a page that exists. Deterministic, offline, and it hands 168 a ready-made tool for its own "no file links beneath `doc/`" criterion — which it will need for 13 files of cross-references. | ✓ |
| Orphan check only | Strictly what criterion 5 asks. Smallest honest scope. But a page reachable from Home whose own links are all broken passes — and 168 is about to import 2,724 lines of documents full of relative links written for a different directory layout. | |
| The above plus external link liveness | Also HTTP-checks outbound links, catching the 6 dead issue links the milestone inventoried. Cost: network-dependent and flaky in CI, and a check that goes red for unrelated reasons gets ignored — the failure mode `catalog-sync-check.yml` already demonstrated here. | |

**User's choice:** Orphan check + internal links resolve (the recommended option).

### Q4 — What should the wiki hold at the end of this phase?

Tension named before asking: activation decision 4 says *relocate and correct only — no new content authored*. Anything 167 writes must be justifiable as pipeline scaffolding rather than documentation.

| Option | Description | Selected |
|--------|-------------|----------|
| Home + a "How this wiki is published" page | Home names the pages 168 will bring; the second page states the in-repo-is-authoritative rule and that wiki-UI edits get overwritten. Defensible under decision 4 as pipeline scaffolding, not documentation — and the only place a drive-by wiki editor would learn WIKI-02's rule before losing their edit. | ✓ |
| Home only | Strictest reading of decision 4 — not one page beyond what the pipeline structurally requires. Cost: the authority rule lives only in `.planning/`, so the first outside contributor to edit a page in the web UI has no warning before publish destroys it. | |
| Home + a placeholder page deleted in 168 | Gives the pipeline a second page to prove multi-page publish, sidebar generation and link-walking against, then removes it. Nothing survives to contradict decision 4, but a placeholder is briefly public on the front-door repo's wiki, and 168 carries a deletion it must not forget. | |

**User's choice:** Home + a "How this wiki is published" page (the recommended option).

**Notes:** No follow-up questions requested for this area. At the closing gate the user selected "I'm ready for context" rather than exploring further gray areas.

---

## Claude's Discretion

The **"Proof strategy & where tests live"** gray area was offered and not selected, leaving it to Claude. Recorded in CONTEXT.md as defaults for the planner to refine rather than operator-locked decisions:

- Criteria 2 and 4 are demonstrated against a **local bare git repository** standing in for `.wiki.git`, explicitly recorded as **not proving the live path**, with a gated re-run against the real wiki once the operator creates it. Driven by v1.34's recorded scar: ~20 latent tooling defects, all fixture-green, all failing on first contact with hardware.
- **Where the tooling's tests live** — the meta repo has no test harness at all today (no `pyproject.toml`, no `pytest.ini`, no `tests/`). Standing one up is a real structural addition the planner must price rather than assume. This was surfaced to the user in the closing summary with an explicit offer to take the decision back; they declined.
- **Wiki push authentication** (HTTPS token vs SSH; default `GITHUB_TOKEN` with `contents: write` vs a PAT secret) — a technical implementation detail routed to research, not asked. `gh` is authenticated locally as `henols` with `repo` and `workflow` scopes.

## Deferred Ideas

- **External link liveness checking** — declined for CI flakiness; the dead-issue-link problem it would catch is Phase 172's POLICY-02, which uses a deterministic repository-wide grep instead.
- **A `PAGES.toml` manifest consulted by the publish path** — rejected as a publishing mechanism; noted as the shape a future per-page-metadata need would take, with its own staleness assertion required.
- **Nested `wiki/` subdirectories for in-repo browsability** — rejected now; revisitable only well beyond the ~16 pages 168 produces, and only with a mapping the drift check can invert.
- **Scheduled drift detection against the live wiki** — rejected because it would sit red between the operator's hand-creation of the first page and 168's first publish; reasonable to reconsider after v1.35 closes.

## Cross-Reference: Todos

`todo.match-phase 167` returned **29 matches**, all matched on generic keyword overlap (`phase`, `check`, `read`, `firestarter`, `source`) rather than domain relevance — firmware behaviour, chip-database decoding, bench hardware, GSD workflow tooling. None touch documentation, the wiki, or repository configuration. Reviewed as a set and deferred wholesale without presenting them individually; none folded.
