# Phase 167: WIKI — Bootstrap, In-Repo Source, Sync & Drift Check - Context

**Gathered:** 2026-08-30
**Status:** Ready for planning

<domain>
## Phase Boundary

Stand up the wiki **publishing pipeline** in `firestarter_prom` — and nothing else. This phase
delivers: an in-repo wiki source tree that is authoritative, a one-command publish that is
idempotent, a drift check that has been *observed failing*, and navigation that cannot silently
orphan a page.

**No documentation content moves in this phase.** The 13 `doc/` files are Phase 168's work; the
front-door README is 169's; the sub-repo READMEs are 170's. 167 exists so that when 168 starts
moving 2,724 lines of documents, it is moving them onto a pipeline that has already been proven.

`WIKI-01` is gated on an operator action outside this repository: GitHub creates
`firestarter_prom.wiki.git` only when the first page is saved through the web UI. Re-verified at
discussion time (2026-08-30) — `git ls-remote https://github.com/henols/firestarter_prom.wiki.git`
still returns `Repository not found`. **No plan in this phase may have a wiki push as its first
action.** Everything except the live-wiki demonstration is buildable and testable against a local
fixture.

`WIKI-06` was verified live during this discussion via the GitHub API: `has_wiki` reads **`true`**
on `henols/firestarter_prom`, **`false`** on `henols/firestarter`, **`false`** on
`henols/firestarter_app`. This is a re-verification, not new work.

</domain>

<decisions>
## Implementation Decisions

### Source layout & page naming

- **D-01:** The in-repo wiki source tree is **`wiki/` at the repository root**. Tooling lives
  separately under `tools/wiki/`. Rationale: content is not tooling — a contributor editing a page
  should never have to open a tooling directory — and a top-level `wiki/` is self-evident to
  anyone landing on the repo once Phase 169 makes `firestarter_prom` the front door.
  Rejected: `docs/` (collides conceptually with the retired generated-site option and sits one
  letter from the `doc/` directories Phase 168 deletes); `tools/wiki/pages/` (buries content under
  a tooling path).

- **D-02:** `wiki/` is **flat — a single directory, no subdirectories**. GitHub addresses wiki
  pages by bare filename regardless of directory, so flat means *source path == published page*
  and the drift check reduces to a plain directory diff. Accepted cost: in-repo browsability
  degrades once ~16 pages accumulate after Phase 168.
  Rejected: nesting with a publish-time flattening step (source path stops equalling the wiki URL,
  two pages in different folders can silently collide on one wiki name, and the drift check would
  have to reverse the mapping); nesting published as-is (collision risk with no navigation
  benefit, since the wiki UI flattens the page list anyway).

- **D-03:** Filenames use **`Title-Case-With-Hyphens.md`**. GitHub renders hyphens as spaces, so
  `Shield-Revisions.md` becomes the page title "Shield Revisions" at URL `/wiki/Shield-Revisions`.
  This produces readable titles *and* readable URLs — and those URLs get written into the READMEs
  Phases 169 and 170 author. Accepted cost: every migrating file is renamed, so Phase 168 must
  produce a real old-path → page mapping, which its own criterion 1 requires regardless.
  Rejected: keeping existing filenames verbatim (would make today's inconsistent casing permanent
  and public — "PROTOCOLS" sitting next to "protocol id" in the sidebar); all-lowercase (titles
  render lowercase and read as unfinished).

- **D-04:** The wiki page name is **derived mechanically from the filename** at publish time.
  There is no manifest for the publish path to consult, so publishing cannot drift from a
  registry. Migration provenance — original repo path → wiki page — lives in a **separate
  checked-in table** that Phase 168 fills in. That table is what makes the move auditable (168
  criterion 1) and what the Backlog 999.9 rename sweep will grep.
  Rejected: a `PAGES.toml` the publish script reads (adding a page would mean editing two files,
  and a stale manifest is a new drift class the drift check does not cover); convention-only with
  the mapping written up in 168's SUMMARY.md (provenance would live in `.planning/` history rather
  than a live artifact, leaving the 999.9 sweep nothing current to grep).

### Publish trigger & who runs it

- **D-05:** Publishing happens **two ways**: a local one-command script *and* a CI publish on
  merge. The local path satisfies WIKI-03 literally and is required for the criterion 2
  overwrite demonstration; the CI path stops the wiki drifting behind the integration branch.

- **D-06:** The CI publish is keyed to **`beta`, not `main`**. Measured during this discussion:
  `origin/beta` is **2,842 commits ahead of `origin/main`** on this meta repo (`main` @ `8c586d44`,
  `beta` @ `7132aea3`). `main` is GitHub's default branch but is drastically stale, and stable
  promotion is operator-gated — a publish keyed to `main` would fire approximately never, while
  Phase 169's front-door README linked into an empty wiki.
  **Accepted cost, and it must be stated on the wiki rather than left implicit:** the wiki tracks
  `beta`, so it can describe behaviour that `main` has not shipped.

- **D-07:** The drift check runs as a **path-filtered PR check on `wiki/`** (plus its own workflow
  file) into `beta`, with `workflow_dispatch` for on-demand runs — the same shape as the existing
  [`catalog-sync-check.yml`](../../../.github/workflows/catalog-sync-check.yml). The identical
  command is runnable locally.
  Rejected: a scheduled cron against the live wiki (it would sit red from the moment the operator
  hand-creates the first page until Phase 168 publishes over it, and red-by-default checks get
  ignored); local-only with no CI (a check nobody is prompted to run does not run, and this
  project already decided sync assertions belong in CI).

- **D-08:** The publish command is **dry-run by default; `--push` publishes**. Critically, **the
  dry-run *is* the drift check** — one code path with two entry points, so the check can never
  diverge from what publish actually does. Publishing is destructive by design (criterion 2
  requires that an in-wiki edit is overwritten), and the CI path pushes unattended, so the local
  default is the only place a human is in the loop.
  Rejected: push-by-default (an accidental run silently destroys a wiki-side edit with no preview);
  push-by-default-refusing-on-hand-edits-without-`--force` (it would put the in-repo copy *second*
  in a conflict, contradicting WIKI-02's authority rule, and criterion 2's plain
  re-publish-overwrites demonstration would then need `--force` to pass).

### Home & sidebar

- **D-09:** `_Sidebar.md` is **generated** from `wiki/`; `Home.md` is **hand-authored**.
  Generating the sidebar makes navigational completeness mechanical — no page can be missing from
  it. Hand-authoring Home keeps curated ordering, a sentence of context per page, and an honest
  place to state the beta-vs-released caveat from D-06. The combination also leaves the
  reachability check something real to catch: a page present in the generated sidebar but absent
  from the hand-written Home.
  Rejected: generating both (WIKI-05 would be satisfied by construction, making criterion 5's
  link-walk a tautology — a check that can only ever be green, which this project has explicitly
  ruled proves nothing); hand-authoring both (hand-maintained navigation is exactly the silent
  drift the milestone's honesty note calls out, and Phase 168 adds 13 pages at once).

- **D-10:** The generated `_Sidebar.md` is **committed to `wiki/`**, regenerated by the publish
  command, with a **CI freshness leg** asserting it is up to date. This matches the strongest
  precedent in this repo — `messages.h` and `messages.py` are generated artifacts that *are*
  committed, regenerated by [`tools/catalog/sync_to_subrepos.sh`](../../../tools/catalog/sync_to_subrepos.sh).
  It also keeps the drift check **exclusion-free**: every exclusion is a hole in an integrity check.
  Accepted cost: a committed generated artifact can go stale, hence the freshness leg.
  Rejected: generate-at-publish-only (the wiki would hold a file with no in-repo counterpart, so
  the drift check would need to special-case `_Sidebar.md` — the first hole in the check WIKI-04
  exists to make trustworthy); generate-and-reconstruct-in-the-checker (the drift check would then
  contain generation logic, so a generator bug would read as "no drift" instead of as a failure).

- **D-11:** The reachability check asserts **orphan detection + internal link resolution**: every
  page in `wiki/` is linked from `Home.md` or `_Sidebar.md`, and every internal wiki link in every
  page points at a page that exists. Deterministic and offline. It also hands Phase 168 a
  ready-made tool for its own "no file links to a path beneath `doc/`" criterion, which matters
  because 168 imports 2,724 lines of documents whose relative links were written for a different
  directory layout.
  Rejected: orphan-check-only (a page reachable from Home whose own links are all broken would
  pass); adding external link liveness (network-dependent and flaky in CI — and a check that goes
  red for reasons unrelated to the change gets ignored, which is precisely the failure mode
  `catalog-sync-check.yml` demonstrated here across 5 runs and 5 failures).

- **D-12:** At the end of this phase the wiki holds **`Home.md` plus a "How this wiki is
  published" page**. Home names the pages Phase 168 will bring; the second page states the
  in-repo-is-authoritative rule and warns that edits made in the wiki web UI are overwritten on
  the next publish.
  **Tension named and accepted:** activation decision 4 says *relocate and correct only — no new
  content authored*. This page is justified as **pipeline scaffolding, not documentation** — it
  describes the wiki's own mechanics, not the product. It is also the only place a drive-by wiki
  editor would ever learn WIKI-02's authority rule before losing their edit.
  Rejected: Home-only (the authority rule would live solely in `.planning/`); Home + a placeholder
  deleted in 168 (a placeholder would be briefly public on the front-door repo's wiki, and 168
  would carry a deletion it must not forget).

### Claude's Discretion

The operator did not select the "Proof strategy & where tests live" gray area, leaving it to
Claude. The following are therefore **defaults for the planner to refine, not operator-locked
decisions** — but they are constrained by the criteria and by recorded project scars:

- **Fixture-based proof now, live re-run gated.** Criteria 2 and 4 both require something to be
  *observed* (an in-wiki edit being overwritten; the drift check failing against a deliberately
  divergent wiki). The real wiki does not exist, so both are demonstrated against a **local bare
  git repository standing in for `.wiki.git`**. This must be recorded explicitly as **not proving
  the live path** — v1.34's rig phase produced ~20 latent tooling defects that all had passing
  fixture selftests and all failed on first contact with hardware. The phase therefore carries a
  **gated re-run against the real wiki** once the operator creates it.
- **Where the tooling's tests live.** The meta repo has **no test harness at all** today — no
  `pyproject.toml`, no `pytest.ini`, no `tests/` (verified: tracked top-level paths are
  `.claude/`, `.devcontainer/`, `.github/`, `.gitignore`, `.gitmodules`, `.planning/`, `.vscode/`,
  `CLAUDE.md`, `tools/`, and the two submodule gitlinks). The existing tooling precedent is a
  standalone `python3` script plus a `bash` driver, tested only through CI assertions. Standing up
  a minimal pytest harness in the meta repo is a real structural addition and the planner should
  price it explicitly rather than assume it.
- **Wiki push authentication** (HTTPS token vs SSH; whether the default `GITHUB_TOKEN` with
  `contents: write` suffices for a wiki push, or a PAT secret is required) is a technical
  implementation detail for research to settle. `gh` is authenticated locally as `henols` with
  `repo` and `workflow` scopes.

### Folded Todos

None. `todo.match-phase 167` returned 29 matches, all keyword noise from other domains (firmware
defects, chip database decoding, GSD workflow tooling). None are in this phase's domain. See
Reviewed Todos below.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Milestone scope and constraints (authoritative)
- `.planning/ROADMAP.md` §"v1.35 — Documentation Consolidation & Wiki Migration" — the seven
  activation decisions with their accepted costs, the operator-gated wiki blocker, the honesty
  constraint, the 999.9 sequencing hazard.
- `.planning/ROADMAP.md` §"Phase 167: WIKI — Bootstrap, In-Repo Source, Sync & Drift Check" — the
  six success criteria this phase must make true. Criteria 2 and 4 both demand *observed* behaviour,
  not asserted behaviour.
- `.planning/ROADMAP.md` §"Phase 168: MIGRATE" — read for downstream impact only; 168's criterion 1
  (per-file old-path → wiki-page mapping) is what D-04's migration table serves, and 168's criterion 5
  is the **truth** check that WIKI-04 explicitly does not cover.
- `.planning/REQUIREMENTS.md` §"Wiki — the single documentation home" (WIKI-01…06) — the six
  requirements mapped to this phase.
- `.planning/REQUIREMENTS.md` §"Constraints and Hazards" — the operator-gated blocker, the branch
  protection consequence, the 999.9 sequencing hazard, the honesty constraint.

### Existing tooling precedent in this repository
- `tools/catalog/sync_to_subrepos.sh` — the closest analog to the publish command: an authoritative
  in-repo source copied to published targets, documented as idempotent, re-runnable as a no-op.
  Read it for the shape of the command, the `set -euo pipefail` convention, and the verify-after-copy
  pattern.
- `tools/catalog/codegen.py` — the generated-artifact precedent behind D-10. Generated files in this
  project are committed, not produced at consumption time.
- `.github/workflows/catalog-sync-check.yml` — the drift-check-in-CI shape D-07 mirrors (path
  filters, `workflow_dispatch`, explicit checkout of the compared refs). **Also read its comment
  block as a cautionary record:** it ran 5 times, failed 5 times, and never once asserted the
  property it existed to assert, because it compared against a branch where the file had never
  existed. A CI check is not evidence until it has been seen to pass for the right reason.

### Project conventions
- `CLAUDE.md` (repo root) — repository structure; the meta repo tracks `.planning/` and `.claude/`,
  with `tools/` and `.github/` as the existing exceptions.
- `.planning/codebase/STRUCTURE.md`, `.planning/codebase/CONVENTIONS.md` — established layout and
  naming conventions.

### Content that Phase 168 will migrate (context only — do not move it in 167)
- `firestarter/doc/` — `AT28C04-ADAPTER.md` (160 lines), `PROTOCOLS.md` (556), `SHIELD-REVISIONS.md` (128).
- `firestarter_app/doc/` — `PY32F071-FIRMWARE-INSTALL.md` (299), `beta-testing-install.md` (213),
  `community-validation.md` (265), `infoic-field-dictionary.md` (325), `lockable-proms.md` (399),
  `package-details.md` (70), `pinout-safety-review.md` (88), `protocol-flags.md` (54),
  `protocol-id.md` (53), `sram-nvram-behavior.md` (114).
- Measured total: **13 files, 2,724 lines**. Relevant to 167 only for sizing the flat `wiki/`
  directory (D-02) and the sidebar it will generate.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- **`tools/catalog/sync_to_subrepos.sh`** — a working, idempotent source→target sync script already
  living in this repo at exactly the path family D-01 assigns to `tools/wiki/`. Its structure
  (resolve source dir from `BASH_SOURCE`, copy, verify with `diff`, assert invariants, exit non-zero
  on mismatch) is directly transferable to the publish command.
- **`.github/workflows/catalog-sync-check.yml`** — a working path-filtered sync-assertion workflow
  with `workflow_dispatch`, explicit multi-repo checkout, and a resolved-ref step. The drift-check
  workflow can be modelled on it directly.
- **`gh` CLI, authenticated** as `henols` with `repo` and `workflow` scopes — sufficient for reading
  `has_wiki` back from the API (criterion 6) and, subject to research, for wiki push over HTTPS.

### Established Patterns

- **Generated artifacts are committed.** `messages.h` (firmware) and `messages.py` (host) are
  generated by `codegen.py` and checked in, regenerated by the sync script. D-10 follows this for
  `_Sidebar.md` rather than inventing a publish-time-only convention.
- **Sync assertions belong in CI, path-filtered to what they guard.** Established by
  `catalog-sync-check.yml`; D-07 follows it.
- **Tooling is standalone scripts under `tools/<name>/`** — a `python3` script plus a `bash` driver,
  no package, no import path. There is no shared library to hook into.
- **`beta` is the integration branch; `main` lags badly.** Measured: 2,842 commits. Any workflow
  keyed to `main` in this repo is effectively dormant. This is the fact behind D-06 and it should be
  re-measured rather than assumed if the planner needs it.

### Integration Points

- **New:** `wiki/` at repo root (page sources + the committed generated `_Sidebar.md`).
- **New:** `tools/wiki/` (publish command, drift check sharing its code path, sidebar generator,
  link/orphan walker).
- **New:** a `.github/workflows/` entry for publish-on-`beta` and a drift check on `wiki/` PRs —
  the second workflow this repo will have.
- **New:** the migration provenance table (D-04), created here and filled by Phase 168.
- **External, operator-gated:** `https://github.com/henols/firestarter_prom.wiki.git` — does not
  exist yet.

### Gaps the planner must price

- **No test harness exists in the meta repo.** No `pyproject.toml`, no `pytest.ini`, no `tests/`.
  Any tested tooling either introduces one or is verified purely through CI assertions and fixture
  runs.
- **`.github/` currently holds exactly one workflow.** There is no CI convention here beyond that
  single file — no shared actions, no reusable workflows, no linting of workflow files.

</code_context>

<specifics>
## Specific Ideas

- **"The dry-run *is* the drift check."** (D-08) This is the sharpest structural idea from the
  discussion and should survive into implementation intact: publish and drift-check are one code
  path with two entry points, so the check cannot report agreement while publish would do something
  different. A separate check reimplementing publish's comparison would be a second thing to keep in
  sync — the exact failure class this milestone is trying to eliminate.

- **"Every exclusion is a hole in an integrity check."** (D-10) The preference for a committed
  `_Sidebar.md` is driven by keeping the drift comparison a whole-directory diff with zero
  special cases.

- **A check seen only green proves nothing.** Stated twice, independently: in the ROADMAP's own
  criterion 4 (citing v1.34's ~20 fixture-green tooling defects) and in the rejection of
  generate-both-navigation-files (D-09), which would make criterion 5 a tautology. Both the drift
  check and the reachability check must be demonstrated failing on a real negative case before they
  are relied upon.

- **The beta-vs-released gap gets stated, not elided.** D-06 accepts that the wiki tracks `beta`;
  the accompanying obligation is that the wiki says so on a page a reader will see, not only in
  `.planning/`.

</specifics>

<deferred>
## Deferred Ideas

- **External link liveness checking** — raised while scoping the reachability check (D-11) and
  declined for CI flakiness. It would catch the 6 dead `henols/firestarter/issues` and
  `henols/firestarter_app/issues` links the milestone already inventoried, but those are **Phase
  172's** work (POLICY-02 requires a repository-wide grep returning none), and a grep is
  deterministic where an HTTP check is not.

- **A `PAGES.toml` manifest that the publish path consults** — rejected as a publishing mechanism
  (D-04) because it introduces a drift class the drift check does not cover. If a future need
  appears for per-page metadata (ordering, categories, a `noindex` flag), this is the shape it would
  take, and it would need its own staleness assertion.

- **Nested `wiki/` subdirectories for in-repo browsability** — rejected now (D-02) because flatness
  is what makes the drift check a plain diff. Worth revisiting only if the page count grows well
  beyond the ~16 pages Phase 168 produces, and only with a mapping the drift check can invert.

- **Scheduled drift detection against the live wiki** — rejected (D-07) because it would sit red
  between the operator's hand-creation of the first page and Phase 168's first publish. Reasonable
  to reconsider *after* v1.35 closes, when a red result would mean something.

### Reviewed Todos (not folded)

`todo.match-phase 167` surfaced 29 pending todos, all matched on generic keyword overlap
(`phase`, `check`, `read`, `firestarter`, `source`) rather than domain relevance. Every one belongs
to firmware behaviour, chip-database decoding, bench hardware, or GSD workflow tooling — none touch
documentation, the wiki, or repository configuration. Reviewed as a set and deferred wholesale; no
individual item was judged a candidate for this phase.

</deferred>

---

*Phase: 167-WIKI — Bootstrap, In-Repo Source, Sync & Drift Check*
*Context gathered: 2026-08-30*
