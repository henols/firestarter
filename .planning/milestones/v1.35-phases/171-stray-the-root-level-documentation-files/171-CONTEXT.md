# Phase 171: STRAY — The Root-Level Documentation Files - Context

**Gathered:** 2026-09-01
**Status:** Ready for planning

<domain>
## Phase Boundary

Dispose of three loose files at the `firestarter_app` repository root so that nothing at a repo
root reads as maintained documentation, or as a policy the project does not actually have.

**In scope — exactly three files, all in `firestarter_app/`:**

| File | What it actually is (measured 2026-09-01) |
|---|---|
| `things.md` | 5 lines — the logo block, the sentence "Windows help to find avrtools", and one `hackaday.io` link |
| `autocomplete.md` | ~70 lines, accurate and current — Click `_FIRESTARTER_COMPLETE` activation for bash / zsh / fish / PowerShell, a pipx note, and a migration note off `register-python-argcomplete` |
| `SECURITY.md` | The GSD Phase 69 security-audit record dated 2026-06-15, occupying the path GitHub reads as the repository's security policy |

**Requirements:** LEGACY-04 (`things.md`), LEGACY-05 (`SECURITY.md`), LEGACY-07 (`autocomplete.md`).

**Out of scope — settled mechanically during analysis, not open questions:**

- **`firestarter/PINOUTS.md` and `firestarter/PROTOCOLS.md` are not strays.** Phase 168 added both
  deliberately (`bbcdc39`) as developer-facing implementation references. Both are linked from
  `firestarter/README.md`, and `PROTOCOLS.md` carries a claims region machine-read by
  `tools/wiki/dispatch_mirror.py`. Deleting or moving either would break the dispatch-mirror leg of
  `.github/workflows/wiki-check.yml`.
- **`CLAUDE.md` at all three roots** is agent configuration, not reader-facing documentation.
- **No product code.** Nothing in this phase touches firmware or host behaviour.

</domain>

<decisions>
## Implementation Decisions

### SECURITY.md

- **D-01: `firestarter_app/SECURITY.md` is deleted outright.** No replacement policy is written.
  Three measured facts make this free rather than lossy:
  1. The audit record already has a canonical home in this repo at
     `.planning/milestones/v1.12-phases/69-cli-command-surface-robustness-audit/69-SECURITY.md`.
     The two differ only in framing — the meta copy carries GSD frontmatter
     (`phase: 69`, `threats_open: 0`, `asvs_level: 1`) and an `# Phase 69 — Security` heading where
     the app copy has a `# SECURITY.md` heading and prose header lines. The threat table, accepted
     risks log and CI gate table are the same content.
  2. `/gsd-secure-phase` writes to `${PHASE_DIR}/${PADDED_PHASE}-SECURITY.md` and never to a
     repository root (`.claude/gsd-core/workflows/secure-phase.md`, step 6). The file will not
     regenerate at the deleted path, so no guard against recurrence is owed.
  3. Nothing links to it. A repo-wide grep across all three repositories for `SECURITY.md` returns
     only the file's own title line.

- **D-02: Nothing replaces it — silence is the honest answer.** GitHub will show no security policy
  for `firestarter_app`, which is accurate: the project has no private disclosure channel. Rejected
  alternatives and why:
  - *A real policy in the app repo* — would commit the operator to a reporting channel (GitHub
    private vulnerability reporting or an email address) and an implied response, and would still
    leave the other two repos with nothing.
  - *A canonical policy in `firestarter_prom` linked from the sub-repos* — GitHub only surfaces a
    repository's **own** `SECURITY.md`, so the sub-repo Security tabs would stay empty unless a
    `henols/.github` default-community-health repository were created. That is a new repository and
    an operator action, well outside this phase.
  - *One line in the app README pointing security reports at the prom tracker* — declined; it
    touches an artifact Phase 170 already closed, and tracker prose is Phase 172's job (POLICY-01).

  **This phase therefore adds no security-reporting statement anywhere.** Planning must not smuggle
  one in as a convenience.

### The autocompletion guide

- **D-03: `autocomplete.md` becomes a new wiki page `Shell-Completion`**, moved essentially as-is,
  and is deleted from the app repo root. Not folded into the README: Phase 170 just cut that README
  from 779 to 118 lines to be a get-started page, and ~70 lines of shell-by-shell activation would
  undo that. Rejected alternatives: a condensed ~10-line README section (drops the pipx note, the
  fish persistence path, the PowerShell `$PROFILE` path and the migration note — relocation would
  become partial deletion); and a wiki page *plus* a README pointer (the only option that states the
  same fact in two places, which REPO-02 and FRONT-03 both push against).

- **D-04: the "Migrating from a previous Firestarter" section stays on `Shell-Completion`.** It is
  genuinely a change requiring action on upgrade, but the wiki's `Breaking-Changes` page is
  version-anchored and newest-first (`v1.32`, `v1.20`, `v1.10`, all wire-protocol or database
  breaks). The argcomplete → Click swap has no version anchor in the source text, and inventing one
  would be authoring content that activation decision 4 forbids. A reader fixing a broken completion
  line is standing on the completion page, which is where the fix belongs.

  Provenance for the record: that swap landed in `firestarter_app` `3224f7e` (2026-05-28,
  `feat(41-04): swap entry point to Click; drop argcomplete`). Planning may cite it, but must not
  turn it into a `Breaking-Changes` version heading — that is exactly the invented anchor D-04
  refuses.

### things.md

- **D-05: `things.md` is deleted outright.** Its single fact — how a Windows user obtains AVR tools
  — is already answered on the wiki's `Home` page, which after giving `apt` and `brew` lines adds
  that avrdude "also ships inside the Arduino IDE and PlatformIO". LEGACY-04 explicitly permits
  deletion. Rejected alternatives: salvaging the `hackaday.io` link onto `Home` (it resolves
  HTTP 200 today, but it would become an external link the project implicitly vouches for, and
  Phase 167's D-11 already declined external link-liveness checking, so nothing would notice it
  rotting); and a new `Installing-avrdude` page (authoring new content from a five-line source,
  which decision 4 rules out).

### Provenance

- **D-06: all three files get rows in `.planning/v1.35/MIGRATION-TABLE.md`.**
  - `Shell-Completion` joins the **main table** as a Phase 171 row: source repo `firestarter_app`,
    source path `firestarter_app/autocomplete.md`, wiki page `Shell-Completion`, rendered title
    `Shell Completion`, pre-deletion SHA `d56424e1979edf7245cffb9ec3111c0469f5b23f`, moved in `171`.
  - `things.md` and `SECURITY.md` go in a **new short section** for files removed without ever being
    published, sitting alongside the existing "Retired from the wiki after the migration closed"
    section. Each row records what the file was and why it went, so "what happened to this document"
    stays answerable from the table alone.
  - **The SHA is reusable and verified.** All three files are byte-identical at `d56424e` — the
    branch-point commit every existing Phase 168 row already cites — so the recorded oracle
    `git -C firestarter_app show d56424e:<file>` resolves for all three. Measured 2026-09-01:
    `autocomplete.md` sha256-16 `6e3a0116f2a3759f`, `things.md` `637974e9dcab7870`,
    `SECURITY.md` `35077cac80e15a8a`, each matching the working tree exactly. No new SHA-column
    semantics are introduced.

### Mechanical constraints — recorded, not asked

These follow from prior decisions and measured state. Planning must honour them; they were not put
to the operator because precedent settles them.

- **Wiki changes reach the wiki by clone-commit-push.** Documentation lives only in
  `firestarter_prom.wiki.git` (activation decision 5 as reversed, D-19). There is no in-repo `wiki/`
  source tree, no publish script, no PR and no CI gate on the edit. A local clone at
  `https://github.com/henols/firestarter_prom.wiki.git` is the working copy.
- **A new page owes two navigation edits or CI goes red.** `.github/workflows/wiki-check.yml` runs
  `tools/wiki/wiki.py links --source-dir wiki-clone` weekly (`cron: '17 6 * * 1'`) against a fresh
  clone. It asserts orphan-freedom (every page reachable from `Home.md`) **and** that `_Sidebar.md`
  lists every page. `Shell-Completion` must be added to `_Sidebar.md` and linked from `Home.md`'s
  Reference list in the same push that creates the page.
- **Page naming follows D-03 of Phase 167**: `Title-Case-With-Hyphens.md`, flat, no subdirectories.
  `Shell-Completion.md` renders as "Shell Completion".
- **Page opening follows the established shape.** All nine live wiki pages open with the same logo
  `<p align="left">` block followed by `---`. `autocomplete.md` already opens exactly that way, so
  the move is close to byte-for-byte.
- **App-repo changes land on the milestone branch inside the submodule** —
  `gsd/v1.35-documentation-consolidation-wiki-migration` in `firestarter_app`, currently at
  `767079a`. Meta-repo changes (`MIGRATION-TABLE.md`, planning records) land on the same-named
  branch here.
- **Packaging is expected to be unaffected, and this must be checked rather than assumed.**
  `firestarter_app/MANIFEST.in` names `README.md` and `LICENSE` explicitly and none of the three
  files; `pyproject.toml` sets `readme = { file = "README.md" }`. A built sdist is the honest oracle,
  and Phase 170 already established building one as the check (REPO-04).

### Claude's Discretion

- Exact wording of the two new `MIGRATION-TABLE.md` deletion rows, and the heading of the new
  section, provided each row names the file, its disposition and its recoverable SHA.
- Placement of `Shell-Completion` within `Home.md`'s Reference list and within `_Sidebar.md`,
  provided both are updated in the same push.
- Whether the deletions and the wiki page land as one commit or several, subject to the usual
  atomic-commit convention.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase and milestone definition

- `.planning/ROADMAP.md` — the v1.35 milestone section, the seven activation decisions, and the
  "Phase 171: STRAY — The Root-Level Documentation Files" entry under `## Phase Details` carrying
  the goal and the three success criteria.
- `.planning/REQUIREMENTS.md` — LEGACY-04, LEGACY-05 and LEGACY-07 texts, and the requirement →
  phase mapping table.
- `.planning/notes/v135-wiki-only-reversal.md` — why there is no in-repo wiki source tree, what the
  reversal voided, and what survives. Read before assuming any Phase 167 publishing tooling exists.
- `.planning/notes/v135-phases-169-170-executed-ad-hoc.md` — records that Phases 169 and 170 were
  executed outside the phase machinery, and the criterion-by-criterion re-check their requirement
  marks rest on.

### The files being disposed of

- `firestarter_app/things.md` — LEGACY-04's subject.
- `firestarter_app/autocomplete.md` — LEGACY-07's subject; the source text for `Shell-Completion`.
- `firestarter_app/SECURITY.md` — LEGACY-05's subject.
- `.planning/milestones/v1.12-phases/69-cli-command-surface-robustness-audit/69-SECURITY.md` — the
  canonical Phase 69 audit record that makes D-01's deletion lossless. Do not delete this one.

### Wiki mechanics and checks

- `.planning/v1.35/MIGRATION-TABLE.md` — the provenance table D-06 appends to; also documents the
  clone-commit-push model and the pre-deletion-SHA convention.
- `tools/wiki/wiki.py` — the `links` subcommand implementing the WIKI-05 reachability, orphan,
  link-form and filename-legality checks. Run it against a wiki clone before pushing.
- `.github/workflows/wiki-check.yml` — the weekly job that runs `wiki.py links`,
  `honest02_truth.py` and `dispatch_mirror.py` against a fresh wiki clone.
- `.planning/phases/167-wiki-bootstrap-in-repo-source-sync-drift-check/167-CONTEXT.md` — D-02
  (flat page tree), D-03 (`Title-Case-With-Hyphens.md`), D-04 (page name derived from filename),
  D-11 (external link-liveness checking declined). D-01 and D-05 through D-10 describe the retired
  in-repo publishing model and no longer apply.

### Artifacts the phase must not break

- `firestarter_app/MANIFEST.in` and `firestarter_app/pyproject.toml` — the sdist contents and the
  PyPI `long_description` source.
- `firestarter_app/README.md` — Phase 170's output. This phase does not edit it (D-02, D-03).
- `firestarter/PINOUTS.md`, `firestarter/PROTOCOLS.md` — deliberate implementation references, not
  strays; `PROTOCOLS.md` is machine-read by `tools/wiki/dispatch_mirror.py`.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- **`tools/wiki/wiki.py links`** — already repointable at a wiki clone via `--source-dir`. It is the
  ready-made pre-push check for the new page: orphan detection, sidebar completeness, internal link
  form, filename legality. No new tooling is needed for this phase.
- **`.planning/v1.35/MIGRATION-TABLE.md`'s existing "Retired from the wiki" section** — the precedent
  shape for D-06's new "removed, never published" section. Same columns, same purpose.
- **The branch-point SHA `d56424e1979edf7245cffb9ec3111c0469f5b23f`** — already cited by every
  Phase 168 `firestarter_app` row, and verified above to be exact for all three of this phase's
  files.

### Established Patterns

- **Wiki page shape** — logo block, `---`, `# Title`, body. Uniform across all nine live pages.
- **Navigation is hand-maintained** — `_Sidebar.md` is no longer generated (the reversal retired
  `wiki.py sidebar`), so it is edited by hand and checked by `wiki.py links`.
- **Deletion is a legitimate disposition, recorded rather than silent** — the operator's post-168
  wiki reorganisation removed six pages, and each is recorded in `MIGRATION-TABLE.md` with what
  happened to it. D-05 and D-06 follow that precedent exactly.
- **Relocate and correct only** (activation decision 4) — the move may fix a wrong claim; it may not
  add a topic.

### Integration Points

- **`firestarter_prom.wiki.git`** — clone, add `Shell-Completion.md`, edit `_Sidebar.md` and
  `Home.md`, push. This is a third repository, not a submodule, and no CI gates the push.
- **`firestarter_app` submodule at `gsd/v1.35-documentation-consolidation-wiki-migration`** — where
  the three deletions commit.
- **Meta repo, same branch** — where the `MIGRATION-TABLE.md` rows and the phase records commit.

### Live state measured 2026-09-01

- The wiki holds **9 pages plus `_Sidebar.md`**: `Home`, `Install-Beta`, `Testing-Chips`,
  `Programming-Protocols`, `Chip-Database-Fields`, `Pin-Maps`, `Lockable-PROMs`, `Shield-Revisions`,
  `Breaking-Changes`. `Shell-Completion` would be the tenth.
- The `hackaday.io` link in `things.md` resolves HTTP 200.
- No file in any of the three repositories links to `things.md`, `autocomplete.md` or `SECURITY.md`,
  so **no link sweep is owed** by this phase.

</code_context>

<specifics>
## Specific Ideas

- The operator's stated preference throughout was the subtractive option: delete `SECURITY.md`
  rather than write a policy, replace it with nothing rather than a pointer, delete `things.md`
  rather than salvage its link. The one thing kept — the autocompletion guide — was kept whole and
  moved off the repo root rather than trimmed into the README. Read the phase as "remove three
  things, publish one page", not as a documentation-writing exercise.
- **"Silence is honest."** The reason `SECURITY.md` gets no replacement is that the project has no
  private disclosure channel, and a page claiming otherwise would be the same class of false claim
  the honesty constraint exists to prevent — an internal audit artifact silently presented as a
  disclosure policy is precisely what is being removed.

</specifics>

<deferred>
## Deferred Ideas

- **`MIGRATION-TABLE.md` lists two pages that no longer exist.** Its main table carries
  `Protocol-Flags` and `Protocol-ID` rows as current wiki pages; a fresh clone of the live wiki has
  neither. This is drift from the operator's post-168 reorganisation and belongs to whoever owns the
  table — not to this phase, which only appends. Worth fixing before the Backlog 999.9 rename sweep
  greps the table, since those two rows would send it after pages that are not there.
- **A real security disclosure policy**, if the project ever wants one. It would need a reporting
  channel decided first (GitHub private vulnerability reporting, or an email address), and to cover
  all three repositories it would need a `henols/.github` default-community-health repository, which
  does not exist. Explicitly not this phase (D-02).
- **A security-reporting statement in the app README** — declined here as Phase 172 (POLICY-01)
  territory, where tracker policy is stated canonically. Noted so 172 can decide whether security
  reports get their own sentence alongside the one-tracker statement.
- **An `Installing-avrdude` wiki page** covering all three platforms — rejected under D-05 as new
  content, but it is the natural home if Windows install support is ever asked for.

### Reviewed Todos (not folded)

`todo.match-phase 171` returned **36 matches, 35 of them scored 0.6 and one 0.4**, every one of them
matched on generic keywords (`firestarter`, `app`, `phase`, `gsd`, `files`) rather than on subject.
Not one concerns root-level documentation files. All 36 were reviewed and **none folded** — they are
firmware, host-app, bench-hardware and GSD-tooling items with no relationship to this phase's scope.
No individual triage is recorded because the match set contains no true positive.

</deferred>

---

*Phase: 171-STRAY — The Root-Level Documentation Files*
*Context gathered: 2026-09-01*
