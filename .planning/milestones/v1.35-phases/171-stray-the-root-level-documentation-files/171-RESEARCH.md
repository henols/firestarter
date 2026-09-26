# Phase 171: STRAY — The Root-Level Documentation Files - Research

**Researched:** 2026-09-01
**Domain:** Documentation disposition — repo-root file removal, GitHub wiki page publication, provenance recording
**Confidence:** HIGH (every claim below was measured this session; the two unmeasurable items are named explicitly in Open Questions)

---

## ⚠️ CONTEXT.md CORRECTIONS — READ FIRST

Seven measured facts contradict `171-CONTEXT.md`. Four of them change what the plan must do.

| # | CONTEXT.md says | Measured truth | Impact |
|---|---|---|---|
| **C-1** | "`.github/workflows/wiki-check.yml` runs `wiki.py links` weekly (`cron: '17 6 * * 1'`)" (171-CONTEXT.md:128-131) | **The workflow does not run at all.** It is absent from `origin/main`, the default branch of `henols/firestarter_prom`. GitHub schedules `cron` and offers `workflow_dispatch` **only from the default branch**. `gh workflow list --all` returns exactly one workflow: `Catalog sync check`. `gh api repos/henols/firestarter_prom/contents/.github/workflows/wiki-check.yml` → HTTP 404. `git cat-file -e origin/main:.github/workflows/wiki-check.yml` → ABSENT; `origin/beta` → PRESENT. | **HIGH.** There is no CI safety net. A forgotten `_Sidebar.md` entry would not "go red a week later on the cron" — it would go unnoticed indefinitely. The **only** oracle available to this phase is the local `wiki.py links` run, so the plan must make that a mandatory, evidenced pre-push AND post-push step, not a nicety. It also means the executor cannot discharge anything with `gh workflow run`. |
| **C-2** | Packaging check: build an sdist (171-CONTEXT.md:142-145) | **A build run in `/workspaces/firestarter_app` gives a FALSE POSITIVE.** It emits a **220-entry** sdist containing `firestarter-3.0.0b33/autocomplete.md` and `firestarter-3.0.0b33/things.md`. A build from a pristine `git archive` tree emits **173 entries** and none of the three. Cause proven below (§B.7). | **HIGH.** If the plan says "build an sdist and grep", the executor will measure that two files *were* packaged and conclude the phase changed packaging. The oracle must be a **clean-tree** build. |
| **C-3** | "`autocomplete.md` already opens exactly that way, so the move is close to byte-for-byte" (171-CONTEXT.md:135-137) | It shares the logo block and `---`, but diverges in **three** measurable ways from all 8 non-`Home` pages: no blank line after `---`; heading is `##` not `#`; heading text is `Enabling Shell Autocompletion`, not `Shell Completion` (= `render_title("Shell-Completion")`). | **MEDIUM.** And `wiki.py links` does **not** check page shape (proved in §B.5) — nothing automated will catch a mis-shaped page. The plan must specify the three shape edits explicitly. |
| **C-4** | "A repo-wide grep across all three repositories for `SECURITY.md` returns only the file's own title line" (171-CONTEXT.md:50-51) | There is a **second** hit: `firestarter/test/native/avr/test_eeprom28c_sdp/RED-BASELINE.md:637`. | **LOW.** It is a historical phase record listing untracked files, not a link. Disposition: **no action** (it is historical-by-intent). But the claim as stated is false and a plan that re-asserts it verbatim asserts a falsehood. |
| **C-5** | (implied) `SECURITY.md` today "occupies the path GitHub surfaces as the repository's security policy" (ROADMAP criterion 2 / LEGACY-05) | **It does not, yet.** `SECURITY.md` is **ABSENT from `origin/main`** (the app's default branch) and present only on `origin/beta` and the milestone branch. `gh api repos/henols/firestarter_app/community/profile -q .files.security_policy` → `null`. It was first committed by `43d1a93 refactor(v1.33): sweep the app package's provenance residue`; before that it was an untracked file (corroborated by the RED-BASELINE.md hit in C-4). | **MEDIUM.** The misrepresentation is **latent**, not live: it becomes live the moment the branch reaches `main`. This is good news — the phase is *prevention*, not *remediation* — but it changes the verification: the community-profile API reads `main` and returns `null` **both before and after**, so it proves nothing. The branch-level `git` check is the only real oracle. |
| **C-6** | "the app submodule … currently at `767079a`" (171-CONTEXT.md:138-141) | True of the submodule **working tree**. But **the meta gitlink is already one commit stale**: meta `HEAD` records `firestarter_app 50f85b20…` and `firestarter bbcdc39f…`, while the checked-out submodules are at `767079a` and `c26562a` (Phase 170's two README commits were never pinned). `git status` in meta shows `M firestarter` / `M firestarter_app` today, before this phase touches anything. | **MEDIUM.** The gitlink-bump commit for this phase will sweep up Phase 170's un-pinned commits too. The executor must expect that and not read the pre-existing `M` entries as their own uncommitted work. |
| **C-7** | "`things.md` \| 5 lines" (171-CONTEXT.md:16); ROADMAP says "six lines" | **7 lines, 265 bytes, no trailing newline.** `wc -l` reports 6 because it counts newline characters. | **LOW / cosmetic**, but any new prose (a MIGRATION-TABLE row) that repeats a line count should say "seven lines" or avoid the count. |

**Also confirmed correct** (verified, not assumed): the wiki holds exactly 9 pages + `_Sidebar.md` with exactly the names listed; the `d56424e` SHA resolves for all three files and all three sha256-16 figures in D-06 match byte-for-byte; the `Protocol-Flags`/`Protocol-ID` drift in the migration table is real; `MANIFEST.in` and `pyproject.toml` name none of the three; `3224f7e` is the correct provenance for the argcomplete→Click swap.

**Pre-existing defect discovered, explicitly OUT OF SCOPE:** `.github/workflows/wiki-check.yml:104-107` invokes `dispatch_mirror.py --wiki-dir wiki-clone`, but `dispatch_mirror.py` accepts only `--app-dir` and `--fw-dir` (`tools/wiki/dispatch_mirror.py:157-158`). Running it as the workflow does exits **2** with `unrecognized arguments: --wiki-dir`. Introduced by `4b14a5a2 feat(wiki): move the dispatch gate onto the firmware protocol doc` (2026-08-31), which edited `dispatch_mirror.py` and `selftest.sh` but not the workflow. Present on `origin/beta` too. **Do not fix it in this phase** — but the plan should record it so a future red workflow is not blamed on Phase 171.

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

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
     only the file's own title line. *(→ see correction C-4)*

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

- **D-05: `things.md` is deleted outright.** Its single fact — how a Windows user obtains AVR tools
  — is already answered on the wiki's `Home` page, which after giving `apt` and `brew` lines adds
  that avrdude "also ships inside the Arduino IDE and PlatformIO". LEGACY-04 explicitly permits
  deletion. Rejected alternatives: salvaging the `hackaday.io` link onto `Home` (it resolves
  HTTP 200 today, but it would become an external link the project implicitly vouches for, and
  Phase 167's D-11 already declined external link-liveness checking, so nothing would notice it
  rotting); and a new `Installing-avrdude` page (authoring new content from a five-line source,
  which decision 4 rules out).

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

### Mechanical constraints (recorded, not asked)

- Wiki changes reach the wiki by **clone-commit-push**. No in-repo `wiki/` source tree, no publish
  script, no PR, no CI gate on the edit.
- A new page owes **two navigation edits**: `_Sidebar.md` and a link path from `Home.md`.
  *(→ see refinement in §B.5: the orphan check is a transitive BFS, so any reachable path works;
  the Home Reference list is the simplest satisfying choice, and is what D-06 discretion selects.)*
- Page naming follows Phase 167 D-03: `Title-Case-With-Hyphens.md`, flat, no subdirectories.
- Page opening follows the established shape. *(→ see correction C-3: three deltas to apply.)*
- App-repo changes land on `gsd/v1.35-documentation-consolidation-wiki-migration` inside the
  `firestarter_app` submodule. Meta-repo changes land on the same-named branch in `/workspaces`.
- Packaging must be **checked, not assumed**. *(→ see correction C-2 for the correct method.)*

### Claude's Discretion

- Exact wording of the two new `MIGRATION-TABLE.md` deletion rows, and the heading of the new
  section, provided each row names the file, its disposition and its recoverable SHA.
- Placement of `Shell-Completion` within `Home.md`'s Reference list and within `_Sidebar.md`,
  provided both are updated in the same push.
- Whether the deletions and the wiki page land as one commit or several, subject to the usual
  atomic-commit convention.

### Deferred Ideas (OUT OF SCOPE)

- `MIGRATION-TABLE.md` lists two pages that no longer exist (`Protocol-Flags`, `Protocol-ID`).
  **Confirmed true this session** — belongs to whoever owns the table, not to this phase.
- A real security disclosure policy (needs a reporting channel and a `henols/.github` repo).
- A security-reporting statement in the app README — Phase 172 (POLICY-01) territory.
- An `Installing-avrdude` wiki page.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description (`.planning/REQUIREMENTS.md`) | Research Support |
|----|-------------|------------------|
| **LEGACY-04** | `firestarter_app/things.md` — a six-line scratch note about finding avrtools on Windows — is either a real wiki page or deleted. (REQUIREMENTS.md:58) | D-05 selects deletion. §C.8 verifies the recoverable SHA. §F gives the runnable proof. Note the file is actually 7 lines / 265 bytes (C-7). |
| **LEGACY-05** | `firestarter_app/SECURITY.md` is a genuine security policy or is removed; a GSD Phase 69 audit record no longer occupies the path GitHub reads as the repository's security policy. (REQUIREMENTS.md:59) | D-01/D-02 select deletion with no replacement. C-5 establishes the misrepresentation is **latent** (absent from `main`), so the requirement is satisfied by preventing it reaching `main`. §F distinguishes the branch-level automated check from the `main`-level API check that proves nothing. |
| **LEGACY-07** | `firestarter_app/autocomplete.md` is folded into the app README or the wiki rather than sitting loose at the repository root. (REQUIREMENTS.md:61) | D-03 selects the wiki. §A.4 gives the byte-level shape deltas; §B.5 gives the exact `wiki.py links` contract and both negative legs; §F gives the clone-and-assert proof. |

Traceability table (REQUIREMENTS.md:174-176) maps all three to Phase 171, all currently `Pending`.
</phase_requirements>

---

## Summary

This is a subtractive documentation phase across three repositories and one non-submodule wiki
repository. The work itself is small — three `git rm`s, one new wiki page, two navigation edits,
three provenance rows — but the **verification surface is unusually treacherous**, and that is where
this research concentrated.

Three traps were measured and defused. First, the CI job everyone assumes is watching the wiki
**is not running** (C-1): it lives on `beta` but not on the default branch, so GitHub neither
schedules it nor exposes it to `workflow_dispatch`. The local `wiki.py links` run is not a
convenience check before a CI gate catches you — it is the *only* gate. Second, the obvious
packaging oracle **lies** (C-2): built in the working tree, the sdist reports `autocomplete.md` and
`things.md` as packaged, because setuptools' `manifest_maker` re-reads a pre-existing
`firestarter.egg-info/SOURCES.txt` when no revision-control file-finder plugin is installed. Built
from a pristine tree, the sdist manifest is **byte-identical before and after the deletions**.
Third, the security misrepresentation is **latent, not live** (C-5): `SECURITY.md` never reached
`main`, so GitHub reports no security policy today; the phase prevents a future harm rather than
removing a present one, and any verification pointed at `main` will pass vacuously.

The wiki working copy is fully accessible from this environment: an anonymous clone succeeds, the
token in `gh auth status` carries `admin`/`push` on `henols/firestarter_prom`, and the VS Code
credential helper is configured globally. The page shape is uniform across all 8 non-`Home` pages
and `autocomplete.md` diverges from it in three specific ways that no checker will catch.

**Primary recommendation:** structure the phase as **four commit destinations** following Phase 168's
precedent — one plan per destination, each with a `commits_land_in:` frontmatter naming exactly one
repository — and gate every one of them on a *measured* oracle rather than an assumed CI run:
`wiki.py links` against a fresh clone for the wiki, a **clean-tree** `git archive` + `uv build` for
packaging, and a py3.11 venv for the app suite. Publish the wiki page **first**, verify it, and only
then delete the source file, so the phase is never in a state where the content exists nowhere.

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Publishing `Shell-Completion` | `firestarter_prom.wiki.git` (third repo, clone-commit-push) | — | Activation decision 5 as reversed (D-19): documentation lives only in the wiki. No in-repo source tree exists. `.planning/notes/v135-wiki-only-reversal.md:9-11` |
| Wiki navigation (`_Sidebar.md`, `Home.md`) | `firestarter_prom.wiki.git` | — | Hand-maintained since `wiki.py sidebar` was retired. Same push as the page or the orphan/sidebar legs fail. |
| Deleting the three root files | `firestarter_app` submodule, milestone branch | — | The files are app-repo artifacts. `commits_land_in: firestarter_app`, per 168-03/04/06/09-PLAN.md precedent. |
| Provenance rows | Meta repo (`/workspaces`), `.planning/v1.35/MIGRATION-TABLE.md` | — | The table lives under `tools/`, survived the reversal intact (`v135-wiki-only-reversal.md:38-40`). `commits_land_in: meta (/workspaces)`. |
| Gitlink re-pin | Meta repo | — | Separate `chore(171): advance submodule pointers` commit; precedent `f62021b4 chore(168): advance submodule pointers and refresh gate evidence`. |
| Packaging verification | Scratch directory (`git archive` extraction) | — | **Never** the live working tree — see C-2 / §B.7. |
| Security-policy surface | GitHub (`henols/firestarter_app` default branch) | — | Not writable by this phase; observable via `gh api …/community/profile` but reads `main` only. |

---

## Standard Stack

No packages are installed by this phase. Everything needed is already in the repository or the
devcontainer. Versions measured 2026-09-01.

### Core (already present)

| Tool | Version / location | Purpose | Why standard |
|------|---------|---------|--------------|
| `tools/wiki/wiki.py links` | `/workspaces/tools/wiki/wiki.py` (330 lines) | The reachability / sidebar / link-form / filename oracle | Purpose-built for exactly this; already repointable via `--source-dir`. `[VERIFIED: run this session, rc=0]` |
| `git` | 2.x, devcontainer | Clone/commit/push the wiki; `git rm` in the app | Only route to the wiki (no REST publish path). `[VERIFIED]` |
| `gh` | authenticated as `henols`, scopes `gist, read:org, repo, workflow` | API observation of the security-policy surface | `[VERIFIED: gh auth status]` |
| `python3` | **3.12.14** (`/usr/local/bin/python3`) | Runs `wiki.py` (stdlib-only) | `wiki.py` is stdlib-only and version-insensitive. `[VERIFIED]` |
| `uv` | **0.12.6** | `uv build --sdist`; `uv venv --python 3.11` | Phase 168's established build route. `[VERIFIED]` |
| `build` / `setuptools` | `build` 1.6.0, `setuptools` 82.0.1 | sdist backend | `[VERIFIED]` |

### Supporting

| Tool | Purpose | When to use |
|------|---------|-------------|
| `tools/wiki/honest02_truth.py` | Claims-vs-database gate over wiki pages | Regression check only — the new page adds no claims (§B.6). |
| `tools/wiki/honest01_claims.py` | Parses `MIGRATION-TABLE.md` | **Retired one-shot, not in CI** — but it *does* machine-read the table (§C.9). Constrains the new section's shape. |
| `tools/wiki/dispatch_mirror.py` | Dispatch-order mirror | Untouched by this phase; already broken as the workflow invokes it (see the out-of-scope note). |

### Alternatives Considered

| Instead of | Could use | Tradeoff |
|------------|-----------|----------|
| `uv build --sdist` from a `git archive` tree | `python -m build` in `firestarter_app` | **Rejected — gives a false positive** (C-2 / §B.7). `python -m build` hits the identical `SOURCES.txt` accretion. |
| Local `wiki.py links` | `gh workflow run wiki-check.yml` | **Not available** — the workflow is not on the default branch (C-1). `gh` returns HTTP 404. |
| `gh api …/community/profile` for LEGACY-05 | branch-level `git cat-file -e` | The API reads `main`, where `SECURITY.md` never existed → passes vacuously (C-5). Use the git check. |

**Installation:** none. This phase installs nothing.

---

## Package Legitimacy Audit

**Not applicable.** This phase installs zero external packages in any ecosystem. `MANIFEST.in`,
`pyproject.toml`, `requirements.txt` and every lockfile are untouched. The `## Package Legitimacy
Audit` gate is therefore vacuous here, and is recorded as such rather than omitted.

Packages removed due to `[SLOP]` verdict: **none — no packages considered.**
Packages flagged `[SUS]`: **none.**

---

## A. The Wiki Working Copy

### A.1 — Cloneability and push expectation `[VERIFIED: run this session]`

```bash
git clone https://github.com/henols/firestarter_prom.wiki.git \
  /tmp/claude-1000/-workspaces/d4de2010-fc66-4b48-92c4-eb08304900bc/scratchpad/wiki-clone
```

**Result: SUCCESS, rc=0.** Anonymous clone, no token prompt. Wiki `HEAD` =
`7ec9988787e92a45c44c3d47dbc27a5127b402c3` (`docs: add Breaking Changes, the destination for the
README version history`, 2026-08-31, Henrik Olsson). Default ref is `refs/heads/master` (not `main`)
— `git ls-remote` returns `7ec99887… refs/heads/master` and nothing else.

**Push expectation: HIGH confidence it will work, but not provable without pushing.**
- `gh auth status` → logged in as `henols`, git protocol `https`, token scopes `gist, read:org, repo, workflow`.
- `gh api repos/henols/firestarter_prom -q .permissions` → `{"admin":true,"maintain":true,"pull":true,"push":true,"triage":true}`. A GitHub wiki inherits its parent repository's push permission.
- Credential path: `credential.helper` is set **globally** to the VS Code devcontainer helper
  (`!f() { …/node /tmp/vscode-remote-containers-….js git-credential-helper $*; }; f`) — the same
  helper that services `origin` in all three repos.

Phase 168 executed the same clone-commit-push twice (`168-05-PLAN.md`, `168-08-PLAN.md`, both
`commits_land_in: firestarter_prom.wiki.git (live public wiki)`), which is direct precedent that
push works from this environment.

**What the executor must check at execution time** (this research is read-only and did not push):
the first `git push` in the wiki clone. If the helper fails, fall back to
`git remote set-url origin https://$(gh auth token)@github.com/henols/firestarter_prom.wiki.git`
— but never commit that URL anywhere.

### A.2 — Complete file listing `[VERIFIED]`

`git ls-files` in the clone returns exactly 10 files, all at the root, no subdirectories:

```
Breaking-Changes.md      4469 B
Chip-Database-Fields.md  3370 B
Home.md                  1950 B
Install-Beta.md          3125 B
Lockable-PROMs.md       34006 B
Pin-Maps.md              9141 B
Programming-Protocols.md 4793 B
Shield-Revisions.md      2148 B
Testing-Chips.md         4429 B
_Sidebar.md               311 B
```

### A.3 — CONTEXT.md's "9 pages plus `_Sidebar.md`" — **CONFIRMED EXACTLY** `[VERIFIED]`

Nine pages, named exactly as CONTEXT.md:241-244 lists them: `Home`, `Install-Beta`, `Testing-Chips`,
`Programming-Protocols`, `Chip-Database-Fields`, `Pin-Maps`, `Lockable-PROMs`, `Shield-Revisions`,
`Breaking-Changes`. `Shell-Completion` would be the tenth.

**Exact current `_Sidebar.md`** (9 lines, ends with a single `\n`, no trailing blank line — trailing
bytes measured as `…]  (  B  r  e  a  k  i  n  g  -  C  h  a  n  g  e  s  )  \n`):

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
```

Note the inconsistent link-text convention already present: lines 1-3 use spaced text
(`[Install Beta]`), lines 4-9 use the hyphenated stem (`[Programming-Protocols]`). Both forms pass
the checker. The planner should pick one and say which; the hyphenated form matches the 6-line
majority and matches `Home.md`'s Reference list.

**Exact current `Home.md` Reference region** (`Home.md:42-54`, verbatim — this is the text the
planner must anchor the edit against):

```markdown
## Reference

- [Programming-Protocols](Programming-Protocols) — how each protocol works and which chips it is for
- [Chip-Database-Fields](Chip-Database-Fields) — what every field in the chip database means
- [Pin-Maps](Pin-Maps) — pin maps for every chip family, and the DIP24 adapter
- [Lockable-PROMs](Lockable-PROMs) — which flash families can report whether they are write-protected
- [Shield-Revisions](Shield-Revisions) — telling the RURP shield revisions apart
- [Breaking-Changes](Breaking-Changes) — what changed between versions, and what to do about it

---

Newer chip support lands in the beta first. If you want to run it — and help
check chips against real hardware — see [Install Beta](Install-Beta).
```

`Home.md` ends `…[Install Beta](Install-Beta).\n`. The em dash separator in every Reference bullet is
U+2014 (` — `). A new bullet must use the same character to read consistently.

Note `Testing-Chips` is **not** in `Home.md`'s Reference list — it is reachable transitively via
`Install-Beta.md:82` and `Chip-Database-Fields.md:49`. This is what proves the orphan check is a BFS
(§B.5), not a Home-list-membership check.

### A.4 — Page shape: the established block vs `autocomplete.md` `[VERIFIED — CONTEXT.md C-3 is imprecise]`

**Established shape, byte-exact, identical on all 9 pages:**

```
line 1: <p align="left"><img src="https://raw.githubusercontent.com/henols/firestarter_app/refs/heads/main/images/firestarter_logo.png" alt="Firestarter EPROM Programmer" width="200"></p>
line 2: (empty)
line 3: ---
line 4: (empty)
line 5: # <Title>
line 6: (empty)
```

On all 8 non-`Home` pages, line 5's title is **exactly** `render_title(stem)` — i.e.
`stem.replace("-", " ")` (`tools/wiki/wiki.py:50-51`):

| Page stem | `render_title` | Actual H1 | Match |
|---|---|---|---|
| Breaking-Changes | Breaking Changes | `# Breaking Changes` | ✓ |
| Chip-Database-Fields | Chip Database Fields | `# Chip Database Fields` | ✓ |
| Install-Beta | Install Beta | `# Install Beta` | ✓ |
| Lockable-PROMs | Lockable PROMs | `# Lockable PROMs` | ✓ |
| Pin-Maps | Pin Maps | `# Pin Maps` | ✓ |
| Programming-Protocols | Programming Protocols | `# Programming Protocols` | ✓ |
| Shield-Revisions | Shield Revisions | `# Shield Revisions` | ✓ |
| Testing-Chips | Testing Chips | `# Testing Chips` | ✓ |
| **Home** | Home | `# Firestarter` | **deliberate exception** |

**`firestarter_app/autocomplete.md` head, byte-exact** (`autocomplete.md:1-6`):

```
line 1: <p align="left"><img src="…firestarter_logo.png" alt="Firestarter EPROM Programmer" width="200"></p>
line 2: (empty)
line 3: ---
line 4: ## Enabling Shell Autocompletion
line 5: (empty)
line 6: Firestarter ships shell completion via [Click](…)'s built-in …
```

**The move is NOT near-byte-identical. Three deltas the executor must apply:**

1. **Insert a blank line after `---`** (line 3 → line 4). Every live page has one; `autocomplete.md` does not.
2. **Promote `##` → `#`.** Every live page's title is an H1. An H2 title renders visibly smaller on the wiki, and the page would be the only one out of ten with no H1.
3. **Retitle `Enabling Shell Autocompletion` → `Shell Completion`** so it equals `render_title("Shell-Completion")`, matching all 8 non-`Home` pages.

The logo `<img src>` URL is byte-identical to the one every live page uses (it points at
`firestarter_app/refs/heads/main`), so no URL edit is owed.

The file is 69 lines, ends `…shell-completion/).\n` (trailing newline present), sha256
`6e3a0116f2a3759f9d377b0f3ce0e4c5071048f9349eb86c6b83ee7a846db97e`.

The rest of the body needs **no** edit: its only links are two external `https://click.…` markdown
links (lines 6 and 69), which `wiki.py`'s `EXTERNAL_LINK_PREFIXES` skips
(`tools/wiki/wiki.py:40,102-103`); all shell one-liners live in fenced code blocks, which
`strip_code_spans` blanks before link extraction (`tools/wiki/wiki.py:62-67`). **Verified empirically**
— see §B.5, where a naive copy passed `wiki.py links` cleanly.

⚠️ **`wiki.py links` does NOT check any of the three shape deltas.** A naively copied page passes
with `rc=0`. There is no automated leg that will catch a mis-shaped page, and (per C-1) no CI at
all. The plan must state the three edits as explicit task actions and verify them with a targeted
`sed -n '1,6p'` assertion, not lean on the checker.

---

## B. The Verification Oracles

### B.5 — `tools/wiki/wiki.py links` `[VERIFIED: source read + 4 runs this session]`

**Exact invocation** (run from `/workspaces`):

```bash
python3 tools/wiki/wiki.py links --source-dir <ABSOLUTE-PATH-TO-WIKI-CLONE>
```

`--source-dir` is `required=True` with **no default** — deliberately, so it can never silently check
the wrong tree (`tools/wiki/wiki.py:276-284`).

**Exit-code contract** (`tools/wiki/wiki.py:7-11`, confirmed by run):

| rc | Meaning | Observed |
|----|---------|----------|
| 0 | Every asserted property holds | ✓ |
| 1 | A property is false; each failure printed to **stderr** as `ERROR: …` | ✓ |
| 2 | Precondition unmet (source dir missing) | ✓ — `ERROR: source directory not found: /nonexistent` |

**What it asserts** — four independent checks, all failures accumulated then reported together
(`cmd_links`, `tools/wiki/wiki.py:245-266`):

1. `check_page_names` (`:108`) — no subdirectories, `.md` suffix only, no `\/:*?"<>|`, no `..`.
2. `check_link_forms` (`:138`) — the only legal internal link form is `[Text](Page-Name)` or
   `[Text](Page-Name#anchor)`. Rejects `.md`-suffixed, `[[Page]]`, reference-style `[Text][ref]`,
   and **case-mismatched** targets. **`_Sidebar.md` and `_Footer.md` are skipped** (`NAV_EXCLUDED_PAGES`, `:37`, `:143`).
3. `check_orphans` (`:205`) — every page reachable from `Home.md`.
4. `check_sidebar_lists_every_page` (`:225`) — every page stem appears as a link target in `_Sidebar.md`.

**Is `_Sidebar.md` sufficient, or is `Home.md` required? BOTH ARE REQUIRED, and they are independent.**
This is the single most important detail for the plan:

- Reachability is a **transitive BFS from `Home.md`** (`pages_reachable_from_home`, `:190-202`), *not*
  membership in Home's Reference list. Any chain of links from `Home` reaches the page. Proof: the
  live wiki passes today even though `Testing-Chips` is absent from `Home.md`'s list — it is reached
  via `Install-Beta.md:82`.
- `_Sidebar.md` links **do not count as reachability evidence** (the BFS frontier starts only at
  `Home`; `_Sidebar` is in `NAV_EXCLUDED_PAGES` and is never traversed) — stated explicitly in the
  subparser help at `tools/wiki/wiki.py:308-310`.
- Sidebar completeness is a **separate** check that requires the page's stem to be a link target in
  `_Sidebar.md`.

So CONTEXT.md's "must be added to `_Sidebar.md` and linked from `Home.md`'s Reference list" is a
correct *sufficient* recipe; it is stronger than strictly necessary on the Home side. Since D-06
discretion already picks the Home Reference list, adopt it — it is the clearest.

**Exact passing output — BEFORE (measured against the live clone, rc=0):**

```
Breaking-Changes -> "Breaking Changes"
Chip-Database-Fields -> "Chip Database Fields"
Home -> "Home"
Install-Beta -> "Install Beta"
Lockable-PROMs -> "Lockable PROMs"
Pin-Maps -> "Pin Maps"
Programming-Protocols -> "Programming Protocols"
Shield-Revisions -> "Shield Revisions"
Testing-Chips -> "Testing Chips"
OK: 9 pages, all reachable from Home.md by some link path, all internal links resolve, all filenames legal, and all listed in _Sidebar.md.
```

**Exact passing output — AFTER (measured against a simulated add, rc=0):**

```
Breaking-Changes -> "Breaking Changes"
Chip-Database-Fields -> "Chip Database Fields"
Home -> "Home"
Install-Beta -> "Install Beta"
Lockable-PROMs -> "Lockable PROMs"
Pin-Maps -> "Pin Maps"
Programming-Protocols -> "Programming Protocols"
Shell-Completion -> "Shell Completion"
Shield-Revisions -> "Shield Revisions"
Testing-Chips -> "Testing Chips"
OK: 10 pages, all reachable from Home.md by some link path, all internal links resolve, all filenames legal, and all listed in _Sidebar.md.
```

The single most useful grep-able assertion for a `<verify>` block is therefore:
`grep -q '^OK: 10 pages,'` combined with `grep -q '^Shell-Completion -> "Shell Completion"$'`.

**Both negative legs measured this session** (this is what makes the oracle trustworthy):

| Simulation | Output | rc |
|---|---|---|
| Page added, `Home.md` updated, **`_Sidebar.md` forgotten** | `ERROR: page missing from _Sidebar.md: Shell-Completion` | **1** |
| Page added, `_Sidebar.md` updated, **`Home.md` forgotten** | `ERROR: orphan page not reachable from Home.md by any link path: Shell-Completion` | **1** |
| Naive copy with **no shape fix**, both nav edits done | full `OK: 10 pages` | **0** ← shape is unchecked |
| `--source-dir /nonexistent` | `ERROR: source directory not found: /nonexistent` | **2** |

### B.6 — `.github/workflows/wiki-check.yml` `[VERIFIED — CONTEXT.md C-1 is WRONG]`

**File content is as CONTEXT.md describes.** `cron: '17 6 * * 1'` (`wiki-check.yml:3-4`), plus
`workflow_dispatch` (`:5`), `permissions: contents: read` (`:7-8`). Steps
(`wiki-check.yml:51-108`): check out meta → resolve sub-repo ref (same branch name, else `beta`) →
check out `firestarter` → check out `firestarter_app` → `git clone --depth 1` the live wiki → three
assertion legs:

| Leg | Command | Status |
|---|---|---|
| WIKI-05 reachability | `python3 meta/tools/wiki/wiki.py links --source-dir wiki-clone` (`:91`) | Would pass |
| HONEST-02 truth | `honest02_truth.py --wiki-dir wiki-clone --db firestarter_app/firestarter/data/chip_database.json --allowlist meta/tools/wiki/claim-allowlist.json` (`:96-99`) | Would pass |
| Dispatch-mirror | `dispatch_mirror.py --wiki-dir wiki-clone --app-dir firestarter_app --fw-dir firestarter` (`:104-107`) | **Would exit 2** — see below |

**But none of it runs.** `wiki-check.yml` is present on `origin/beta` and this milestone branch and
**ABSENT from `origin/main`**, which is `henols/firestarter_prom`'s default branch. GitHub registers
`schedule` and `workflow_dispatch` triggers only from the default branch. Measured:

```
$ gh workflow list --all
Catalog sync check    active    280427776          ← the only registered workflow

$ gh api repos/henols/firestarter_prom/contents/.github/workflows/wiki-check.yml
{"message":"Not Found", "status":"404"}

$ gh api repos/henols/firestarter_prom/contents/.github/workflows
["catalog-sync-check.yml"]

$ git cat-file -e origin/main:.github/workflows/wiki-check.yml   → ABSENT
$ git cat-file -e origin/beta:.github/workflows/wiki-check.yml   → PRESENT
```

Consistent with `ROADMAP.md:236`, which records that the Phase 168 `workflow_dispatch` human item was
"withdrawn the same day by operator decision, the workflow relying on its weekly `schedule` trigger"
— a trigger that, measurably, is not registered.

**Pre-existing defect (OUT OF SCOPE, record only):** `dispatch_mirror.py`'s parser declares only
`--app-dir` and `--fw-dir` (`tools/wiki/dispatch_mirror.py:157-158`). Run as the workflow runs it:

```
$ python3 tools/wiki/dispatch_mirror.py --wiki-dir <dir> --app-dir firestarter_app --fw-dir firestarter
usage: dispatch_mirror.py [-h] --app-dir APP_DIR --fw-dir FW_DIR
dispatch_mirror.py: error: unrecognized arguments: --wiki-dir <dir>
rc=2
```

Run correctly it is green: `OK: 12 protocols compared across firmware doc, host tool and firmware.`
rc=0. The `--wiki-dir` flag was removed by `4b14a5a2` (2026-08-31), which touched
`tools/wiki/dispatch_mirror.py` and `tools/wiki/selftest.sh` only — `git show --stat 4b14a5a2`
confirms the workflow was not updated.

**Does this phase's change surface touch `honest02_truth.py` or `dispatch_mirror.py`? NO.**
- `dispatch_mirror.py` reads `PROTOCOLS_DOC = "PROTOCOLS.md"` from `--fw-dir`
  (`tools/wiki/dispatch_mirror.py:31`) — the *firmware repo's* file, not a wiki page. It never reads
  the wiki. Untouched.
- `honest02_truth.py` — measured before and after the simulated add, output identical except the
  page-scan count:

  ```
  BEFORE: LEG 1 -- stamp present: 8 pages scanned, 5 matched the claim signature, 0 missing stamp
  AFTER:  LEG 1 -- stamp present: 9 pages scanned, 5 matched the claim signature, 0 missing stamp
  … LEG 3 -- stamp freshness: 6 stamps checked against db-sha256-16=ccbc8d2c4866a5af, 0 stale
  OK: leg1 stamp-present 5 matched/0 missing, leg2 claims-resolve 1 regions/39 claims/5 unchecked, leg3 stamp-freshness 6 checked/0 stale.
  rc=0 (both)
  ```

  `Shell-Completion` carries no chip claims, so it does not match the claim signature and owes no
  stamp. **No claims stamp is needed on the new page.**

### B.7 — The sdist oracle `[VERIFIED — CONTEXT.md's METHOD would give a FALSE POSITIVE]`

**The established Phase 168 command** (`.planning/phases/168-…/evidence/migrate03-sdist-doc-delta.txt:19,29`):

```bash
uv build --sdist -o <scratch>/build-<label>
```

run **from the extracted clean tree**, not from the live working directory. That evidence file
explicitly built the "before" side from `git archive d56424e… extracted to a clean scratch
directory` (`:10-12`), and its "The source of the false premise" section (`:50-62`) already
diagnoses `firestarter.egg-info/SOURCES.txt` as a lying artifact — but that warning was about a
*stale* copy, and this session shows a *freshly regenerated* copy lies exactly as badly.

**Measured this session, four builds:**

| Build | Tree | egg-info present? | Entries | Contains the three? |
|---|---|---|---|---|
| B1 | `/workspaces/firestarter_app` (live) | yes | **220** | **`autocomplete.md` ✗ `things.md` ✗** (`SECURITY.md` absent) |
| B2 | `git archive HEAD` → scratch (pristine) | no | **173** | none |
| B3 | pristine + only `firestarter.egg-info/SOURCES.txt` copied in | yes | **220** | `autocomplete.md`, `things.md` reappear |
| B4 | pristine with the three files **deleted** (simulated Phase 171) | no | **173** | none |

`diff <(tar tzf B2) <(tar tzf B4)` → **empty. The sdist manifests are byte-identical before and
after the deletions.**

**Root cause, proven by B2 vs B3** (the only variable is the presence of `SOURCES.txt`):
setuptools' `manifest_maker.add_defaults()` calls `walk_revctrl()`; with no `setuptools.file_finders`
entry-point plugin installed it finds nothing and falls through to
`elif os.path.exists(self.manifest): self.read_manifest()` — re-absorbing the previous
`SOURCES.txt` into the new file list. That file lists `CLAUDE.md`, `README.md`, `autocomplete.md`,
`things.md` (`firestarter.egg-info/SOURCES.txt:2,5,6,10`) but **not** `SECURITY.md`, because it was
generated before `SECURITY.md` was ever tracked. The directory is gitignored
(`.gitignore:6: firestarter.egg-info/`), so it never gets cleaned by a checkout.

**Correct, copy-pasteable oracle** (run from `/workspaces`):

```bash
SCRATCH=$(mktemp -d)
export UV_CACHE_DIR="$SCRATCH/uv-cache"          # ~/.cache/uv is NOT writable in this devcontainer
mkdir -p "$SCRATCH/tree"
git -C /workspaces/firestarter_app archive HEAD | tar -x -C "$SCRATCH/tree"
( cd "$SCRATCH/tree" && uv build --sdist -o "$SCRATCH/dist" )
tar tzf "$SCRATCH"/dist/*.tar.gz | wc -l                                    # expect 173
tar tzf "$SCRATCH"/dist/*.tar.gz | grep -cE 'things\.md|autocomplete\.md|SECURITY\.md'   # expect 0
```

`UV_CACHE_DIR` is mandatory — without it `uv build` dies with
`Failed to initialize cache at /home/vscode/.cache/uv: Permission denied (os error 13)`.

**Independent confirmation from PyPI** — published sdists carry none of the three:

| Release | Entries | Root files | Any of the three? |
|---|---|---|---|
| `3.0.0b8` | 70 | LICENSE, MANIFEST.in, PKG-INFO, README.md, pyproject.toml, setup.cfg | none |
| `3.0.0b33` | 174 | same six | none |
| `3.0.0b35` (latest beta) | 173 | same six | none |

**`MANIFEST.in` and `pyproject.toml` verified — neither names any of the three.**
`MANIFEST.in` (11 lines) names four `firestarter/data/*` files, five `firestarter/*.py` files,
`README.md` and `LICENSE`. `pyproject.toml:10` sets
`readme = { file = "README.md", content-type = "text/markdown" }`; `:94` `packages = ["firestarter"]`;
`:95-100` `package-data` limited to three JSON files.

**Can an sdist be built in this devcontainer? YES.** `uv 0.12.6`, `build 1.6.0`, `setuptools 82.0.1`,
`python3 3.12.14`. The **build** is version-insensitive (the backend runs in uv's isolated env).
The **test suite** is not: `firestarter_app/.github/workflows/ci.yml:50-53` pins Python **3.11**, and
`.planning/notes/…devcontainer py3.12 masks app CI…` records that the 3.12 devcontainer has
demonstrably hidden breakage. Phase 168's route
(`evidence/migrate03-py311-suite.txt:5-10`):

```bash
export UV_CACHE_DIR=<scratch>/uvcache
uv venv --python 3.11 <scratch>/venv311            # resolves CPython 3.11.16
VIRTUAL_ENV=<scratch>/venv311 uv pip install -e '.[test]'
export FIRESTARTER_CONFIG_DIR=<scratch>/fsconfig   # app writes to ~/.firestarter regardless
cd /workspaces/firestarter_app && <scratch>/venv311/bin/python3 -m pytest tests/ -o addopts="" -q
```

Two traps the same evidence file records and the plan must carry forward:
- **Run every command with `cwd=/workspaces/firestarter_app`, never `cwd=/workspaces`.** From the
  meta root, `python3 -c "import firestarter"` resolves to the *firmware* directory
  `/workspaces/firestarter` via PEP 420 namespace-package resolution before the editable install's
  finder runs. Confirm with `python3 -c "import firestarter; print(firestarter.__file__)"` →
  must print `/workspaces/firestarter_app/firestarter/__init__.py`.
- `-o addopts=""` is required — `pyproject.toml:107` sets `addopts = "-ra -q"`, and doubling `-q`
  suppresses the pass/fail count line.

⚠️ **App CI will not run on this change.** `firestarter_app/.github/workflows/ci.yml:20-32` sets
`paths-ignore: ['**.md', …]` on **both** `push` and `pull_request`. A commit that deletes only three
`.md` files triggers **zero** CI runs. The local py3.11 suite is the only signal.

---

## C. Provenance and the Migration Table

### C.8 — The three SHA claims — **ALL THREE VERIFIED EXACTLY** `[VERIFIED]`

`d56424e1979edf7245cffb9ec3111c0469f5b23f` is a real commit in `firestarter_app`
(`refactor: strip GSD provenance from tools/`, 2026-08-30 08:29:59 +0000) and **is an ancestor of
HEAD** (`git merge-base --is-ancestor` → true).

`git show d56424e:<file>` resolves for all three, and each is **byte-identical to the working tree**
(`git show d56424e:$f | diff -q - $f` → no output, for all three):

| File | sha256 (full) | sha256-16 measured | D-06 claims | Match |
|---|---|---|---|---|
| `autocomplete.md` | `6e3a0116f2a3759f9d377b0f3ce0e4c5071048f9349eb86c6b83ee7a846db97e` | `6e3a0116f2a3759f` | `6e3a0116f2a3759f` | ✅ |
| `things.md` | `637974e9dcab787043e8795a51018dca1ee12a3e6987934f8ea1577b51efc05c` | `637974e9dcab7870` | `637974e9dcab7870` | ✅ |
| `SECURITY.md` | `35077cac80e15a8a473ef699769b69542d676a3c5d293d30b349a15ef477e7ff` | `35077cac80e15a8a` | `35077cac80e15a8a` | ✅ |

Reproduce with (from `/workspaces`):

```bash
for f in autocomplete.md things.md SECURITY.md; do
  printf "%-18s " "$f"
  git -C firestarter_app show d56424e1979edf7245cffb9ec3111c0469f5b23f:$f | sha256sum | cut -c1-16
done
```

**A branch caveat worth recording in the table row.** `origin/main` still carries an **older,
argcomplete-era** `autocomplete.md` (blob `6536efc1…`); `origin/beta` and the milestone branch carry
the current Click-based version (blob `d840857394…`). The `d56424e` SHA captures the **current**
version, which is the correct provenance for what is being published. Confirms D-04's citation:
`git log -- autocomplete.md` shows the most recent change is
`3224f7e feat(41-04): swap entry point to Click; drop argcomplete; main.py 932->35 (CLI-01, CLI-02, CLI-04)`.

### C.9 — `MIGRATION-TABLE.md` — column headers and the machine reader `[VERIFIED]`

**Main table header** (`.planning/v1.35/MIGRATION-TABLE.md:10-11`) — 6 columns:

```
| Source repo | Source path | Wiki page | Rendered title | Pre-deletion SHA | Moved in |
|---|---|---|---|---|---|
```

Existing `firestarter_app` rows use source paths **prefixed with the repo name**
(`firestarter_app/doc/beta-testing-install.md`, `:15`) and cite `d56424e197…` in full. A Phase 171
row must follow that shape exactly:

```
| firestarter_app | firestarter_app/autocomplete.md | Shell-Completion | Shell Completion | d56424e1979edf7245cffb9ec3111c0469f5b23f | 171 |
```

**"Retired from the wiki after the migration closed" header** (`:52-53`) — 3 columns:

```
| Source path | Was published as | What happened |
|---|---|---|
```

Its cells wrap the path in backticks (`` `firestarter/doc/AT28C04-ADAPTER.md` ``, `:54`) and the
`What happened` cell is free prose ending in a period.

**Is the table machine-read? YES — by `tools/wiki/honest01_claims.py`.**
`parse_migration_table(table_path)` at `tools/wiki/honest01_claims.py:74-93`, invoked from
`:234 rows = parse_migration_table(args.table)`. It is the **only** reader (`grep -rn MIGRATION-TABLE`
over `tools/`, `.github/`, and both sub-repos returns exactly one hit, a docstring reference at
`honest01_claims.py:21`; every other hit is `.planning/` prose). `honest01_claims.py` is **not** in
`wiki-check.yml`, and `MIGRATION-TABLE.md:104-105` records it as "a retired one-shot (D-03), not a
standing gate". So a malformed row is **not** a CI break — but it would break a tool the repo ships,
and the parser has a trap worth designing around:

```python
TABLE_ROW_RE = re.compile(r"^\|(.+)\|\s*$")     # :47
NO_SHA_MARKER = "—"                              # :49  (U+2014)
```

The parser sets `header` **once**, from the first table-shaped line in the whole file, and **never
resets it**. Every later table's data rows are zipped against that same 6-column header. Rows are
then filtered by `row.get("Pre-deletion SHA", NO_SHA_MARKER) != NO_SHA_MARKER` (`:93`).

Consequence, and the design rule it implies:

- The existing 3-column retired section is **harmlessly absorbed**: `zip` truncates at 3 cells, so
  those rows get keys `Source repo`/`Source path`/`Wiki page` and **no** `Pre-deletion SHA` key →
  filtered out. Confirmed by reading the parser against the live file.
- **A new section whose table has ≥5 columns would NOT be harmless.** Its 5th cell would be keyed
  `Pre-deletion SHA`, the row would survive the filter, and `honest01` would try to resolve it as a
  migration row against a wiki page named by its 3rd cell — and fail.

> **Design rule for D-06's new section:** give it **at most 4 columns** — ideally mirror the existing
> retired section's 3 (`| Source path | What it was | What happened |`) and carry the recoverable SHA
> as inline code inside the last cell, e.g.
> `` recoverable at `git -C firestarter_app show d56424e:things.md`. ``
> That keeps `honest01`'s parse byte-for-byte what it is today. A 6-column table with `—`
> (U+2014, matching `NO_SHA_MARKER` exactly) in the SHA column would also be filtered out, but it
> loses the SHA, which D-06 requires each row to carry.

**Verification that the new rows parse safely** (add to a `<verify>` block):

```bash
cd /workspaces && python3 -c "
import sys; sys.path.insert(0,'tools/wiki')
from pathlib import Path
from honest01_claims import parse_migration_table
rows = parse_migration_table(Path('.planning/v1.35/MIGRATION-TABLE.md'))
print('rows with a SHA:', len(rows))
for r in rows: print(' ', r['Source path'], '->', r['Wiki page'], r['Moved in'])
"
```
Expect **8** rows after the phase (7 today + the `Shell-Completion` row), and no row whose
`Wiki page` is `things.md`, `SECURITY.md`, or a prose fragment.

**CONTEXT.md's deferred `Protocol-Flags`/`Protocol-ID` drift — CONFIRMED REAL.**
`MIGRATION-TABLE.md:18-19` lists both as current wiki pages; the fresh clone has neither, and
neither appears in the "Retired from the wiki" section. Out of scope; do not fix.

### C.10 — Independent link sweep `[VERIFIED — one hit CONTEXT.md missed]`

Ran across all three repos' tracked files (`git grep`) **and** the wiki clone:

| Target | meta (excl. `.planning/`) | `firestarter_app` | `firestarter` | wiki clone |
|---|---|---|---|---|
| `things.md` | 0 | 0 | 0 | 0 |
| `autocomplete.md` | 0 | 0 | 0 | 0 |
| `SECURITY.md` | 0 | 1 — `SECURITY.md:1` (`# SECURITY.md`, its own title) | **1 — `test/native/avr/test_eeprom28c_sdp/RED-BASELINE.md:637`** | 0 |

**The `firestarter` hit CONTEXT.md missed** (`RED-BASELINE.md:635-638`):

> …plus five pre-existing untracked files
> (`.coverage`, `.planning/config.json`, `SECURITY.md`, `doc/lockable-proms.md`,
> `write_test_port.sh`). None of these was touched…

This is a Phase 117 record naming files that were **untracked at that time** — not a link, not a
path reference a reader could follow. It corroborates C-5 (`SECURITY.md` was untracked until
`43d1a93`). **Disposition: NO ACTION.** It is a historical `.planning`-class record inside the
firmware repo and is historical-by-intent; editing it would destroy evidence.

**Conclusion: CONTEXT.md's "no link sweep is owed" stands.** Zero *links* exist to any of the three.

Reproducible sweep (from `/workspaces`):

```bash
for f in things.md autocomplete.md SECURITY.md; do
  echo "== $f"
  git -C /workspaces           grep -n -- "$f" -- . ':(exclude).planning'
  git -C /workspaces/firestarter_app grep -n -- "$f"
  git -C /workspaces/firestarter     grep -n -- "$f"
done
```

---

## D. Branch and Commit Mechanics

### D.11 — Current state, measured `[VERIFIED]`

| Repo | Branch | HEAD | Working tree |
|---|---|---|---|
| meta `/workspaces` | `gsd/v1.35-documentation-consolidation-wiki-migration` | `c8e7e269` | `M .planning/notes/dev-test-sequence-cost-model.md`, `M firestarter`, `M firestarter_app` |
| `firestarter_app` | `gsd/v1.35-documentation-consolidation-wiki-migration` | **`767079a0f74f2f7661ee0b6c625120d5c46a1a1e`** ✅ matches CONTEXT.md | **NOT clean** — `M tools/build_db.py` |
| `firestarter` | `gsd/v1.35-documentation-consolidation-wiki-migration` | `c26562ae` | clean |
| wiki | `master` | `7ec99887` | clean (fresh clone) |

**Two findings the plan must absorb:**

1. **`firestarter_app` is NOT clean.** `tools/build_db.py` is modified and uncommitted. It predates
   this phase. The plan must decide explicitly whether to stash it, leave it, or record it as an
   exclusion — it must not be swept into a Phase 171 commit, and it must not be silently claimed as
   a clean tree.
2. **The meta gitlinks are already one commit stale each** (C-6):

   ```
   $ git ls-tree HEAD firestarter firestarter_app
   160000 commit bbcdc39f292dfad378f84124bc5a4c7fbc3244ad    firestarter
   160000 commit 50f85b20b2948e31d2db77f1cf685e306ab01705    firestarter_app
   ```
   vs checked-out `c26562a` / `767079a`. Both gaps are exactly Phase 170's ad-hoc README commits
   (`docs(170): cut the README to firmware scope`, `docs(170): cut the README to app scope and fix
   the table of contents`), never pinned. `git rev-list --count` → 1 for each.

### D.12 — Correct commit mechanic for a 3-destination change `[VERIFIED: Phase 168 precedent]`

Phase 168 used **one plan per commit destination**, declared in plan frontmatter. Measured across
all 13 plans:

| Destination | `commits_land_in:` value | Plans |
|---|---|---|
| Meta repo | `meta (/workspaces)` | 168-02, -10, -11, -12, -13 |
| App submodule | `firestarter_app` | 168-03, -04, -06, -09 |
| Firmware submodule | `firestarter` | 168-07 |
| **The wiki** | `firestarter_prom.wiki.git (live public wiki) — no meta or sub-repo source commits except evidence` | 168-05, 168-08 |

Wiki plans additionally declare the working copy as an out-of-tree path:
`<files>working clone of firestarter_prom.wiki.git (scratch path, outside all three repositories)</files>`
(`168-05-PLAN.md:81,162`).

The gitlink is re-pinned by a **separate meta commit** after the sub-repo commits land — precedent
`f62021b4 chore(168): advance submodule pointers and refresh gate evidence`; the same pattern
appears at `e57ecb50`, `f5142e84`, `42a46889`, `8445b9bb`.

**Recommended shape for Phase 171 — four destinations, in this order:**

| # | Destination | Content | Why this order |
|---|---|---|---|
| 1 | wiki clone (scratch) | Add `Shell-Completion.md` (shape-corrected), edit `_Sidebar.md` + `Home.md`, run `wiki.py links`, push | Publish **before** deleting, so the content never exists nowhere |
| 2 | `firestarter_app` | `git rm things.md autocomplete.md SECURITY.md` | Only after the wiki page is live and verified |
| 3 | meta | `MIGRATION-TABLE.md` rows + phase records | Provenance records the completed disposition |
| 4 | meta | `chore(171): advance submodule pointers` | Sweeps up Phase 170's stale pins too (C-6) |

---

## E. Failure Modes

### E.13 — How this phase silently half-completes

| # | Failure mode | Why it is silent | Catch it at execution time with |
|---|---|---|---|
| **F1** | Page pushed, **`_Sidebar.md` forgotten** | CONTEXT.md expects the weekly cron to catch it. **It will not** (C-1) — the workflow is not registered. It would be caught *never*. | Re-clone to a **fresh** dir after the push and run `wiki.py links`. Expect `ERROR: page missing from _Sidebar.md: Shell-Completion` / rc=1 if forgotten. |
| **F2** | Page pushed, **`Home.md` link forgotten** | Same — no CI. | Same command. Expect `ERROR: orphan page not reachable from Home.md by any link path: Shell-Completion` / rc=1. |
| **F3** | Page pushed with the **wrong shape** (`##` title, no blank after `---`, "Enabling Shell Autocompletion") | **`wiki.py links` returns rc=0 anyway** — proved by simulation. Nothing automated catches it. | Explicit byte assertion: `sed -n '1,6p' <clone>/Shell-Completion.md` must show blank/`---`/blank/`# Shell Completion`. Plus an operator eyeball of the rendered page. |
| **F4** | App deletions committed, **meta gitlink never bumped** | Meta already shows `M firestarter_app` **before** the phase starts (C-6), so the executor sees the "expected" dirty marker and assumes it is their own pending bump. | After the app commit: `git -C /workspaces ls-tree HEAD firestarter_app` must equal `git -C /workspaces/firestarter_app rev-parse HEAD`. Assert equality, not "there is an `M`". |
| **F5** | Deletions land, **nothing published** — content lost | If task order is deletion-first and the wiki push then fails (auth), the guide exists only in git history. | Order the plans wiki-first (§D.12). Gate the deletion task on a fresh-clone assertion that `Shell-Completion.md` exists on `origin/master`. |
| **F6** | `tools/build_db.py`'s pre-existing modification swept into a Phase 171 commit | `git commit -a` or a broad `git add -A` in the app repo would take it. | Use explicit paths: `git -C firestarter_app rm things.md autocomplete.md SECURITY.md` then `git -C firestarter_app commit` naming only those. Verify with `git show --stat` → exactly 3 files, all `D`. |
| **F7** | Packaging declared "changed" on the strength of a working-tree sdist build | The build genuinely reports `autocomplete.md` and `things.md` as packaged (C-2). An honest executor would record a false regression. | Mandate the `git archive` → scratch → `uv build` route (§B.7). Assert `173` entries and a byte-identical `diff` of the two manifests. |
| **F8** | New `MIGRATION-TABLE.md` section written with ≥5 columns | `honest01_claims.py` is not in CI, so nothing goes red — the breakage surfaces only when someone runs the retired checker. | Run the `parse_migration_table` snippet in §C.9. Expect 8 SHA-bearing rows, none of them a deletion row. |
| **F9** | Phase declares LEGACY-05 met by checking `gh api …/community/profile` | It returns `null` **before and after** (C-5), because `SECURITY.md` never reached `main`. A vacuous pass. | Assert at branch level: `! git -C firestarter_app cat-file -e HEAD:SECURITY.md`. Treat the API call as context, never as the oracle. |
| **F10** | Expecting Host CI to confirm the app change | `ci.yml` `paths-ignore: '**.md'` → an md-only commit triggers **zero** runs. | Run the py3.11 suite locally (§B.7) and record its output as evidence. |

### E.14 — Can a reader still reach a deleted file afterwards?

| Route | Reachable after the phase? | Does it matter for the success criteria? |
|---|---|---|
| PyPI sdist / wheel | **No — and never was.** Published `3.0.0b8`, `3.0.0b33`, `3.0.0b35` sdists carry none of the three (measured, §B.7). | No. |
| GitHub release tarballs | Generated from tags; tags predating the deletion still contain the files. | **No.** The criteria are about "sitting at a repository root" and what "GitHub surfaces as the security policy" — both are properties of a branch tip, not of frozen history. |
| Git history / permalink blob URLs | **Yes, permanently** — and deliberately: D-06's whole point is that `git -C firestarter_app show d56424e:<file>` stays resolvable. | **No — this is the intent, not a leak.** |
| `github.com/henols/firestarter_app/blob/main/autocomplete.md` | **Yes, until the milestone branch merges to `main`** — and it currently serves the *stale argcomplete* version (§C.8). | **Sequencing note, not a criterion failure.** The criteria are branch-scoped; they become true on `main` at merge. Worth one sentence in the phase record so nobody reads a live `main` URL as a phase failure. |
| Search-engine cache | Transient. | No. |

**Plainly: no, it does not matter.** Nothing here weakens any of the three success criteria. The one
thing worth recording is the `main`-lag sentence.

---

## Architecture Patterns

### System flow

```
                        ┌──────────────────────────────────────────┐
                        │ firestarter_app @ gsd/v1.35… (767079a)   │
                        │   autocomplete.md ──┐                    │
                        │   things.md      ───┼── git rm (step 2)  │
                        │   SECURITY.md    ───┘                    │
                        └────────┬─────────────────────────────────┘
                                 │ read at d56424e (frozen oracle)
                                 ▼
   ┌─────────────────────────────────────────────────────────────────────┐
   │ STEP 1 — wiki clone (scratch, outside all three repos)              │
   │   cp autocomplete.md → Shell-Completion.md                          │
   │   apply 3 shape edits: blank line after ---, ## → #, retitle        │
   │   edit _Sidebar.md   (sidebar-completeness leg)                     │
   │   edit Home.md       (orphan/reachability leg)                      │
   │            │                                                        │
   │            ├──► wiki.py links --source-dir .   ── rc must be 0 ─────┼──► GATE
   │            └──► git commit && git push origin master                │
   └─────────────────────────────────┬───────────────────────────────────┘
                                     │ fresh re-clone
                                     ▼
                        ┌───────────────────────────┐
                        │ live wiki: 10 pages       │  ← operator eyeballs the render
                        └───────────────────────────┘
                                     │
              ┌──────────────────────┴──────────────────────┐
              ▼                                             ▼
   ┌────────────────────────┐               ┌──────────────────────────────┐
   │ STEP 3 — meta repo     │               │ STEP 4 — meta repo           │
   │ MIGRATION-TABLE.md:    │               │ chore(171): advance          │
   │  • main table +1 row   │               │ submodule pointers           │
   │  • NEW ≤4-col section  │               │ (also sweeps Phase 170's     │
   │    for the 2 deletions │               │  stale pins — see C-6)       │
   └────────────────────────┘               └──────────────────────────────┘

   OUT-OF-BAND ORACLE (never in the live tree):
     git archive HEAD → scratch → uv build --sdist → 173 entries, identical before/after
```

### Recommended task structure

```
Plan 171-01  commits_land_in: firestarter_prom.wiki.git (live public wiki)
             clone → author Shell-Completion.md → nav edits → wiki.py links → push → re-clone verify
Plan 171-02  commits_land_in: firestarter_app
             clean-tree sdist BEFORE → git rm x3 → clean-tree sdist AFTER → diff → py3.11 suite
Plan 171-03  commits_land_in: meta (/workspaces)
             MIGRATION-TABLE.md rows → honest01 parse check → phase records
Plan 171-04  commits_land_in: meta (/workspaces)
             gitlink re-pin + gitlink equality assertion
```

### Pattern: publish-then-delete, never delete-then-publish

**What:** the wiki page must be live and verified from a *fresh clone* before the source file is removed.
**When to use:** any relocation where the destination is a repository the source repo cannot reference.
**Why:** there is no transaction across the two repositories. A failed push after a completed deletion
leaves the content only in git history (F5).

### Pattern: fresh-clone verification, not working-copy verification

```bash
# NOT this — the working copy is what you just edited; it proves nothing about the push
python3 tools/wiki/wiki.py links --source-dir "$MY_EDIT_DIR"

# THIS — a second, independent clone proves the push actually landed
VERIFY=$(mktemp -d)
git clone --depth 1 https://github.com/henols/firestarter_prom.wiki.git "$VERIFY/wiki"
python3 /workspaces/tools/wiki/wiki.py links --source-dir "$VERIFY/wiki"
```

Phase 168 used exactly this (`168-12-PLAN.md:242` "run the checker once against a **fresh** clone of
the live wiki").

### Anti-patterns to avoid

- **Trusting a working-tree sdist build.** Gives a documented false positive (C-2).
- **Citing `wiki-check.yml` as a safety net.** It is not registered (C-1).
- **Asserting `gh api …/community/profile` for LEGACY-05.** Vacuous (C-5, F9).
- **A ≥5-column table in the new MIGRATION-TABLE section.** Breaks `honest01`'s parse (C.9).
- **`git commit -a` in `firestarter_app`.** Would sweep up `tools/build_db.py` (F6).
- **Writing comments into any source file.** Hard project rule. `Shell-Completion.md` is prose, not
  source, but no `<!-- -->` provenance markers belong in it either — no live wiki page carries one
  except the machine-read `firestarter-claims-*` stamps, which this page does not need (§B.6).
- **Adding a claims stamp to `Shell-Completion.md`.** Measured unnecessary: `honest02` reports
  `0 missing stamp` with the page present.

---

## Don't Hand-Roll

| Problem | Don't build | Use instead | Why |
|---|---|---|---|
| Verify the new page is reachable and listed | A grep for `Shell-Completion` in `Home.md`/`_Sidebar.md` | `python3 tools/wiki/wiki.py links --source-dir <clone>` | A grep cannot see transitive reachability, case-mismatched targets, or illegal link forms. The tool does all four checks and both negative legs are proven (§B.5). |
| Verify packaging is unaffected | Reading `MANIFEST.in` and reasoning | Clean-tree `git archive` + `uv build --sdist`, diff the two manifests | Reasoning from `MANIFEST.in` gives the right answer for the wrong reason and would not have caught the `SOURCES.txt` accretion (§B.7). |
| Freeze the pre-deletion content | Copying the files into `.planning/` | `git -C firestarter_app show d56424e:<file>` | Already the table's established convention; verified byte-exact for all three (§C.8). A copy is a second source of truth that can drift. |
| Confirm the wiki push landed | `git log` in the local clone | A second, independent `git clone --depth 1` | The local clone shows your own commit whether or not the push succeeded. |
| Check the migration rows parse | Eyeballing pipes | Import `parse_migration_table` and print the rows (§C.9) | The parser's single-header behaviour is non-obvious; eyeballing cannot see it. |

**Key insight:** every oracle this phase needs already exists in `tools/wiki/` or in Phase 168's
recorded evidence route. The failure mode in this domain is not missing tooling — it is *using the
right tool against the wrong tree* (working copy instead of fresh clone; live tree instead of clean
tree; `main` instead of the branch).

---

## Runtime State Inventory

This is a deletion/relocation phase, so the inventory applies.

| Category | Items found | Action required |
|---|---|---|
| **Stored data** | **None.** No database, cache or datastore keys the three filenames. Verified: `git grep` across all three repos returns zero references beyond the two documented in §C.10, and the wiki clone has zero. | None |
| **Live service config** | **One, and it is the whole point of the phase.** `firestarter_prom.wiki.git` is a live service repository whose content is not mirrored in git anywhere. The new page exists only after a push. Additionally, GitHub's own "Security policy" surface for `henols/firestarter_app` is service-side state derived from the default branch — measured `null` today (C-5). | Push the wiki page; verify by fresh clone. No action for the security surface (already `null`). |
| **OS-registered state** | **None.** No scheduler task, service unit or process manager references these files. | None |
| **Secrets / env vars** | **None.** No secret or env var names these files. The only credential involved is the existing GitHub token used to push the wiki (`gh auth status`, unchanged). | None |
| **Build artifacts / installed packages** | **One, and it is actively misleading.** `firestarter_app/firestarter.egg-info/SOURCES.txt` (201 lines, gitignored via `.gitignore:6`) lists `autocomplete.md:6` and `things.md:10` and is re-absorbed into every subsequent sdist build (§B.7). It will keep listing them after the deletion until it is regenerated in a tree without them. | **No repo change** (it is gitignored, and deleting it in the working tree is not this phase's business). Instead: never build the packaging oracle in that tree. Record the artifact as the known cause in the evidence file. |

---

## Common Pitfalls

### Pitfall 1: "the weekly cron will catch it"

**What goes wrong:** a navigation edit is forgotten and nobody learns for months.
**Why it happens:** `wiki-check.yml` exists in the working tree and on `beta`, reads exactly like a
live gate, and CONTEXT.md describes it as running weekly. It is not registered with GitHub Actions
because it is absent from the default branch.
**How to avoid:** run `wiki.py links` against a **fresh** clone as an explicit post-push step.
**Warning signs:** any plan text containing "weekly", "cron", or "wiki-check will verify".

### Pitfall 2: the honest packaging check that reports a dishonest result

**What goes wrong:** the executor builds an sdist in `firestarter_app`, sees `autocomplete.md` and
`things.md` inside, and records that the phase removed two files from the package.
**Why it happens:** setuptools re-reads a gitignored, never-cleaned `SOURCES.txt`.
**How to avoid:** always `git archive` into a scratch tree first; always compare *two* builds.
**Warning signs:** an sdist entry count of **220** instead of **173**; `.gitignore`, `CLAUDE.md`,
`requirements.txt` or `*_test.sh` appearing at the archive root.

### Pitfall 3: proving LEGACY-05 against `main`

**What goes wrong:** the check passes before the work is done.
**Why it happens:** `SECURITY.md` never reached `main`; the API reports `security_policy: null` today.
**How to avoid:** assert `! git -C firestarter_app cat-file -e HEAD:SECURITY.md` at branch level.
**Warning signs:** a verify leg citing `community/profile` or a Security-tab screenshot as *the* proof.

### Pitfall 4: a shape-wrong page that every checker approves

**What goes wrong:** `Shell-Completion` ships with an H2 title reading "Enabling Shell
Autocompletion", visibly inconsistent with the other nine pages.
**Why it happens:** CONTEXT.md says the move is "close to byte-for-byte", and `wiki.py links`
returns rc=0 for the naive copy.
**How to avoid:** a literal 6-line head assertion in the verify block.
**Warning signs:** `head -6 Shell-Completion.md` showing `---` immediately followed by `##`.

### Pitfall 5: the gitlink that was already stale

**What goes wrong:** the executor sees `M firestarter_app` in meta, assumes it reflects their own
work, commits it, and unknowingly ships Phase 170's un-pinned README commit in a Phase 171 commit.
**Why it happens:** the marker is present before the phase begins.
**How to avoid:** snapshot `git ls-tree HEAD firestarter firestarter_app` before starting; assert
equality with the submodule HEADs after; state in the commit message that Phase 170's pins are
included.
**Warning signs:** a bump commit whose diff moves the gitlink by more than the phase's own commits.

### Pitfall 6: running python from `/workspaces`

**What goes wrong:** `import firestarter` resolves to `/workspaces/firestarter` (the **firmware**
directory) via PEP 420 namespace packages, and `firestarter.__file__` prints `None`.
**Why it happens:** `python3 -c` puts cwd on `sys.path`, and `PathFinder` beats the editable
install's finder.
**How to avoid:** every command in the app-verification plan runs with `cwd=/workspaces/firestarter_app`.
**Warning signs:** `firestarter.__file__` is `None` or `__path__` is `['/workspaces/firestarter']`.
Recorded verbatim at `evidence/migrate03-py311-suite.txt:22-33`.

---

## Code Examples

### Publish the page (wiki clone, scratch path)

```bash
WIKI=$(mktemp -d)/wiki
git clone https://github.com/henols/firestarter_prom.wiki.git "$WIKI"

# 1. copy, then apply the three shape deltas (§A.4)
cp /workspaces/firestarter_app/autocomplete.md "$WIKI/Shell-Completion.md"
python3 - "$WIKI/Shell-Completion.md" <<'PY'
import sys, pathlib
p = pathlib.Path(sys.argv[1])
lines = p.read_text(encoding="utf-8").split("\n")
assert lines[2] == "---" and lines[3] == "## Enabling Shell Autocompletion", lines[:4]
lines[3:4] = ["", "# Shell Completion"]
p.write_text("\n".join(lines), encoding="utf-8")
PY
sed -n '1,6p' "$WIKI/Shell-Completion.md"     # must be: logo / blank / --- / blank / # Shell Completion / blank

# 2. navigation — BOTH edits, same push
printf -- '- [Shell-Completion](Shell-Completion)\n' >> "$WIKI/_Sidebar.md"
# Home.md: insert after the Breaking-Changes bullet at Home.md:49
```

### The pre-push gate

```bash
python3 /workspaces/tools/wiki/wiki.py links --source-dir "$WIKI"
# expect rc=0 and: OK: 10 pages, all reachable from Home.md by some link path, …
```

### The post-push gate (fresh clone — this is the one that counts)

```bash
V=$(mktemp -d)
git clone --depth 1 https://github.com/henols/firestarter_prom.wiki.git "$V/wiki"
test -f "$V/wiki/Shell-Completion.md"
python3 /workspaces/tools/wiki/wiki.py links --source-dir "$V/wiki" | tee /dev/stderr | grep -q '^OK: 10 pages,'
grep -q 'Shell-Completion' "$V/wiki/_Sidebar.md"
grep -q '(Shell-Completion)' "$V/wiki/Home.md"
sed -n '1,6p' "$V/wiki/Shell-Completion.md"
```

### The deletion

```bash
cd /workspaces/firestarter_app
git rm things.md autocomplete.md SECURITY.md
git commit -m "docs(171): remove three stray root-level documentation files"
git show --stat --format="" HEAD    # expect exactly 3 lines, all deletions
```

### The clean-tree packaging oracle (before AND after)

```bash
S=$(mktemp -d); export UV_CACHE_DIR="$S/uvcache"
for label in before after; do
  ref=$([ "$label" = before ] && echo "HEAD~1" || echo "HEAD")
  mkdir -p "$S/$label"
  git -C /workspaces/firestarter_app archive "$ref" | tar -x -C "$S/$label"
  ( cd "$S/$label" && uv build --sdist -o "$S/dist-$label" >/dev/null )
  tar tzf "$S/dist-$label"/*.tar.gz | sed 's|^[^/]*/||' | sort > "$S/manifest-$label.txt"
done
diff "$S/manifest-before.txt" "$S/manifest-after.txt" && echo "PACKAGING UNAFFECTED"
wc -l "$S/manifest-before.txt" "$S/manifest-after.txt"   # expect 173 and 173
```

### The gitlink equality assertion

```bash
cd /workspaces
for m in firestarter firestarter_app; do
  rec=$(git ls-tree HEAD "$m" | awk '{print $3}')
  act=$(git -C "$m" rev-parse HEAD)
  printf "%-16s recorded=%s actual=%s %s\n" "$m" "${rec:0:8}" "${act:0:8}" \
    "$([ "$rec" = "$act" ] && echo OK || echo STALE)"
done
```

---

## State of the Art

| Old approach | Current approach | When changed | Impact on this phase |
|---|---|---|---|
| In-repo `wiki/` source tree + `wiki.py publish`/`sidebar` + `wiki-publish.yml` | Wiki-only; clone-commit-push; `_Sidebar.md` hand-maintained | 2026-08-30 (D-19 reversal, `.planning/notes/v135-wiki-only-reversal.md`) | No publish script exists. Do not look for one. |
| `wiki.py links` had a default `--source-dir` | `required=True`, no default | Same reversal (`tools/wiki/wiki.py:18-25`) | Every invocation must name the tree. |
| `HONEST-01` as a standing gate | Retired one-shot; `HONEST-02` is the standing guard | `MIGRATION-TABLE.md:104-105` | A malformed migration row is not a CI break — but still breaks `honest01`. |
| `dispatch_mirror.py --wiki-dir` | Reads the firmware's `PROTOCOLS.md`; no wiki input | `4b14a5a2`, 2026-08-31 | The workflow was not updated → pre-existing exit-2 (out of scope). |
| `register-python-argcomplete` completion | Click `_FIRESTARTER_COMPLETE=<shell>_source` | `3224f7e`, 2026-05-28 | The content being published is the current one. `origin/main` still serves the stale version. |

**Deprecated / outdated:**
- The `activate-global-python-argcomplete` instructions still live on `origin/main`'s
  `autocomplete.md`. Not this phase's problem — the branch version is already correct.
- `MIGRATION-TABLE.md:18-19`'s `Protocol-Flags` and `Protocol-ID` rows point at pages that no longer
  exist. Deferred by CONTEXT.md; confirmed real.

---

## Project Constraints (from CLAUDE.md)

From `/workspaces/CLAUDE.md`:
- Meta-repo tracks `.planning/`, `.claude/`, `tools/`, `.github/`. **The sub-repos are not committed
  here** — hence the separate-destination commit model (§D.12).
- **"Documentation lives only in the `firestarter_prom` GitHub wiki — there is no in-repo copy of
  it. `tools/wiki/` holds the checkers that run against a clone of that wiki."** Directly governs
  this phase: no in-repo mirror of `Shell-Completion.md` may be created.

From the operator's standing rules (memory, treated as binding):
- **HARD RULE: no comments in source, at all.** A plan cannot override it. Applies to any script the
  phase writes.
- `.planning/` `file:LINE` citations must be repaired, never left stale — relevant if any plan cites
  `MIGRATION-TABLE.md` line numbers, which shift when rows are appended.
- GSD pushes at ship time; the wiki push is an exception already established by Phase 168 (the wiki
  is not a GSD-managed repo and has no PR flow).

No `.claude/CLAUDE.md` exists. `firestarter_app/CLAUDE.md` carries no constraint bearing on
documentation disposition. `.claude/skills/` holds `devtest-rootcause`, `devtest-triage`,
`find-skills`, `skill-creator` — none applies to this phase; no `rules/*.md` directory exists in
either skills root.

---

## Environment Availability

| Dependency | Required by | Available | Version | Fallback |
|---|---|---|---|---|
| `git` | all four destinations | ✓ | 2.x | — |
| Network to `github.com` | wiki clone/push | ✓ | — | none; phase blocks |
| `firestarter_prom.wiki.git` clone | LEGACY-07 | ✓ | HEAD `7ec99887` | none |
| Push rights on the wiki | LEGACY-07 | ✓ (permission) / **unproven** (mechanism) | `admin:true, push:true` | `https://$(gh auth token)@…` URL, never committed |
| `gh` (authenticated) | API observation | ✓ | as `henols`, scopes `gist, read:org, repo, workflow` | — |
| `python3` | `wiki.py`, `honest0*` | ✓ | 3.12.14 | — |
| `python3.11` | app test suite on the CI floor | ✗ **not on PATH** | — | `uv venv --python 3.11` (Phase 168 route, resolves CPython 3.11.16) |
| `uv` | sdist build + py3.11 venv | ✓ | 0.12.6 | `python -m build` (works, but see the `UV_CACHE_DIR` note; same `SOURCES.txt` trap applies) |
| `build` / `setuptools` | sdist backend | ✓ | 1.6.0 / 82.0.1 | — |
| Writable uv cache | any `uv` command | ✗ at `~/.cache/uv` (**Permission denied**) | — | **`export UV_CACHE_DIR=<scratch>/uvcache` — mandatory** |
| `.github/workflows/wiki-check.yml` as a live gate | CI safety net | ✗ **not registered** | — | Local `wiki.py links` against a fresh clone |
| Host CI on the app change | app-side signal | ✗ **`paths-ignore: '**.md'`** | — | Local py3.11 suite |

**Missing dependencies with no fallback:** none — nothing blocks execution.
**Missing dependencies with fallback:** `python3.11` → `uv venv --python 3.11`; writable uv cache →
`UV_CACHE_DIR`; the CI wiki gate → local `wiki.py links`; Host CI → local suite.

---

## Validation Architecture

`.planning/config.json` has no `workflow.nyquist_validation` key → **treated as enabled**, so this
section is mandatory.

### Test Framework

| Property | Value |
|---|---|
| Primary oracle | `tools/wiki/wiki.py links` (stdlib argparse CLI, exit-code contract 0/1/2) |
| App test framework | pytest (`firestarter_app/pyproject.toml:105-107`, `testpaths = ["tests"]`, `addopts = "-ra -q"`) |
| Config file | `firestarter_app/pyproject.toml` `[tool.pytest.ini_options]` |
| Quick run command | `python3 /workspaces/tools/wiki/wiki.py links --source-dir <clone>` (< 1 s) |
| Full suite command | `cd /workspaces/firestarter_app && <venv311>/bin/python3 -m pytest tests/ -o addopts="" -q` |
| **CI reality** | **No CI covers this phase.** `wiki-check.yml` is unregistered (C-1); app `ci.yml` skips `**.md` commits. Every check below must run locally and be recorded as evidence. |

### Phase Requirements → Test Map

| Req | Behaviour to prove | Type | Runnable command (cwd shown) | Where it runs |
|---|---|---|---|---|
| **LEGACY-04** | `things.md` is gone from the app repo root | automated | `cd /workspaces/firestarter_app && ! test -e things.md && ! git cat-file -e HEAD:things.md` | **this repo** |
| **LEGACY-04** | the deletion is committed, not merely unstaged | automated | `cd /workspaces/firestarter_app && git log -1 --diff-filter=D --name-only --format="" HEAD -- things.md \| grep -qx things.md` | **this repo** |
| **LEGACY-04** | content stays recoverable at the recorded SHA | automated | `cd /workspaces && git -C firestarter_app show d56424e1979edf7245cffb9ec3111c0469f5b23f:things.md \| sha256sum \| cut -c1-16` → `637974e9dcab7870` | **this repo** |
| **LEGACY-05** | `SECURITY.md` is gone from the branch tip | automated | `cd /workspaces/firestarter_app && ! test -e SECURITY.md && ! git cat-file -e HEAD:SECURITY.md` | **this repo** |
| **LEGACY-05** | no replacement policy was smuggled in anywhere (D-02) | automated | `cd /workspaces && ! git -C firestarter_app grep -riq "report a vulnerability\|security policy\|responsible disclosure" -- ':(exclude).planning'` | **this repo** |
| **LEGACY-05** | recoverable at the recorded SHA | automated | `git -C /workspaces/firestarter_app show d56424e…:SECURITY.md \| sha256sum \| cut -c1-16` → `35077cac80e15a8a` | **this repo** |
| **LEGACY-05** | canonical audit record still exists in meta | automated | `test -f /workspaces/.planning/milestones/v1.12-phases/69-cli-command-surface-robustness-audit/69-SECURITY.md` | **this repo** |
| **LEGACY-07** | `autocomplete.md` is gone from the app repo root | automated | `cd /workspaces/firestarter_app && ! test -e autocomplete.md && ! git cat-file -e HEAD:autocomplete.md` | **this repo** |
| **LEGACY-07** | the page exists on the **live** wiki | automated | `git clone --depth 1 https://github.com/henols/firestarter_prom.wiki.git "$V" && test -f "$V/Shell-Completion.md"` | **live wiki** |
| **LEGACY-07** | reachable + sidebar-listed + links legal | automated | `python3 /workspaces/tools/wiki/wiki.py links --source-dir "$V"` → rc=0, stdout contains `OK: 10 pages,` and `Shell-Completion -> "Shell Completion"` | **live wiki** |
| **LEGACY-07** | page shape matches the other nine (§A.4) | automated | `sed -n '3,5p' "$V/Shell-Completion.md" \| tr '\n' '\|'` → `---\|\|# Shell Completion\|` | **live wiki** |
| **LEGACY-07** | content preserved — the four shell sections and the migration note survived | automated | `for s in Bash Zsh Fish PowerShell "pipx Installations" "Migrating from a previous Firestarter"; do grep -qF "### $s" "$V/Shell-Completion.md" \|\| { echo "MISSING: $s"; exit 1; }; done` | **live wiki** |
| **LEGACY-04/05/07** | nothing anywhere links to the three old paths | automated | the §C.10 sweep; expect only `firestarter/test/native/avr/test_eeprom28c_sdp/RED-BASELINE.md:637` (documented historical, no action) | **this repo** |
| **D-06** | all three rows present and the SHA cited | automated | `grep -c 'd56424e1979edf7245cffb9ec3111c0469f5b23f' /workspaces/.planning/v1.35/MIGRATION-TABLE.md` → ≥ 8; plus `grep -q '| firestarter_app | firestarter_app/autocomplete.md | Shell-Completion |' …` | **this repo** |
| **D-06** | the new section does not corrupt `honest01`'s parse | automated | the §C.9 `parse_migration_table` snippet → 8 SHA-bearing rows, none of them a deletion row | **this repo** |
| **packaging** | the sdist manifest is unchanged | automated | the §B.7 clean-tree before/after `diff` → empty; `173` entries each side | **this repo** |
| **app health** | the suite still passes on the CI Python floor | automated | the §B.7 py3.11 route → `N passed` and zero `failed`/`error` | **this repo** |
| **gitlink** | meta records the app's new tip | automated | the §D.12 equality assertion → `OK` for both submodules | **this repo** |

### Checks that are OPERATOR / GITHUB-SIDE ONLY — these MUST be `checkpoint:human-verify`, not `<verify>`

| Check | Why it cannot be automated |
|---|---|
| **The `git push` to the wiki succeeds** | The push is a state-changing network operation this research could not exercise. It is the first action of plan 171-01 and its failure is a hard stop. Follow it immediately with the automated fresh-clone assertion — but the push itself is an executor action, not a verify leg. |
| **The rendered `Shell-Completion` page looks right on github.com** | Markdown rendering, the logo image resolving, sidebar placement and the title reading "Shell Completion" are visual properties of GitHub's renderer. `wiki.py links` never renders anything. Phase 168 used exactly this checkpoint (`ROADMAP.md:236`: "visual inspection of the 14 rendered wiki pages … performed and passed by the operator"). |
| **`henols/firestarter_app`'s Security tab is empty after the branch merges** | The tab is derived from the **default branch**. This phase does not merge to `main`, so the property cannot be observed now. Today the API already reports `security_policy: null` (C-5) — recording that as a pass would be **vacuous**, and must be labelled as such. Defer the real observation to the milestone merge. |
| **Confirming the phase did not make `wiki-check.yml` red** | The workflow is not registered (C-1); there is no run to inspect. If a plan wants CI evidence it must first put the workflow on the default branch — which is Phase 172/173 territory, not this phase. |

**Mislabelling warning for the planner:** the three items above cannot pass as `<automated>` legs. In
particular, do **not** write a verify leg asserting `gh api repos/henols/firestarter_app/community/profile
-q .files.security_policy` is `null` — it is `null` right now, before any work, and would pass a plan
that did nothing.

### Sampling Rate

- **Per task commit:** `python3 tools/wiki/wiki.py links --source-dir <clone>` (wiki tasks);
  `git show --stat --format="" HEAD` (deletion task).
- **Per wave merge:** fresh-clone wiki verification + clean-tree sdist diff.
- **Phase gate:** all automated rows in the map above green, plus the py3.11 suite, before
  `/gsd-verify-work`.

### Wave 0 Gaps

**None.** Every oracle already exists:
- `tools/wiki/wiki.py links` — present, exercised 4× this session including both negative legs.
- `tools/wiki/honest01_claims.py:74` `parse_migration_table` — present, importable.
- The clean-tree sdist route — established by Phase 168's `evidence/migrate03-sdist-doc-delta.txt`.
- The py3.11 venv route — established by `evidence/migrate03-py311-suite.txt`.

No test file, fixture or framework install is owed before implementation.

---

## Security Domain

`.planning/config.json` has no `security_enforcement` key → treated as enabled.

### Applicable ASVS Categories

| ASVS category | Applies | Standard control |
|---|---|---|
| V2 Authentication | no | No authentication surface is touched. The GitHub token used for the wiki push is pre-existing and unchanged. |
| V3 Session Management | no | No sessions. |
| V4 Access Control | **partly** | The phase writes to a public wiki using an `admin`-scoped token. Control: push only the four intended files; never widen the remote URL to an embedded-token form in a committed file. |
| V5 Input Validation | no | No user input is processed. `wiki.py` parses only repo-controlled markdown. |
| V6 Cryptography | no | SHA-256 is used only as a content fingerprint for provenance, never as a security control. |
| V7 Error Handling / Logging | no | — |
| V14 Configuration | **yes** | The phase changes what GitHub surfaces as a repository's security policy. Control: D-02's deliberate silence — accurate, since no private disclosure channel exists. |

### Known Threat Patterns

| Pattern | STRIDE | Mitigation in this phase |
|---|---|---|
| An internal audit artifact read as a public disclosure policy | **Information disclosure / Repudiation** | The core of LEGACY-05. `SECURITY.md` is removed before it can reach `main` (C-5 shows it has not yet). |
| A published security policy promising a channel that does not exist | **Repudiation** | D-02 forbids writing one. Verified by the "no replacement policy" grep leg above. |
| A credential leaked into a committed remote URL during the wiki push | **Information disclosure** | Use the configured credential helper. If the token-in-URL fallback is needed, apply it with `git remote set-url` in the **scratch** clone only, and never commit `.git/config`. |
| Content lost in a relocation | **Denial of service (to readers)** | Publish-then-delete ordering (F5) plus the frozen `d56424e` oracle. |

**Threat explicitly NOT introduced:** removing `SECURITY.md` does not remove a working disclosure
channel, because there is none — `gh api …/community/profile` reports `security_policy: null` today.
The removal is a reduction in *false* assurance, not in real assurance.

---

## Assumptions Log

| # | Claim | Section | Risk if wrong |
|---|---|---|---|
| A1 | `git push` to `firestarter_prom.wiki.git` will succeed from this devcontainer | §A.1, Environment | Phase 171-01 blocks at its first action. Mitigated: `admin`/`push` permission verified via API, global credential helper configured, and Phase 168 pushed successfully twice by the same route. Executor confirms on first push. `[ASSUMED — permission VERIFIED, mechanism not exercised]` |
| A2 | GitHub schedules `cron`/`workflow_dispatch` only from the default branch | C-1, §B.6 | If wrong, `wiki-check.yml` might run after all — which would only *add* a safety net, never remove one. The observation that `gh workflow list --all` returns one workflow and the API 404s on the file is direct evidence regardless of the mechanism. `[CITED: docs.github.com — Events that trigger workflows; corroborated by measurement]` |
| A3 | The setuptools mechanism behind the `SOURCES.txt` accretion is `manifest_maker.add_defaults()` falling through `walk_revctrl()` to `read_manifest()` | §B.7 | Only the *explanation* would be wrong; the **behaviour** is measured (B2 vs B3 differ by that one file alone) and the remedy (clean-tree build) is unaffected. `[ASSUMED — behaviour VERIFIED, mechanism inferred]` |
| A4 | The operator will accept `# Shell Completion` as the page's H1 | §A.4 | Cosmetic. It is what `render_title("Shell-Completion")` produces and what 8 of 9 pages already do. Low risk. `[ASSUMED]` |
| A5 | `tools/build_db.py`'s pending modification is unrelated to Phase 171 | §D.11, F6 | If it were related, excluding it would drop work. It is unstaged and predates the phase; the executor should confirm with `git -C firestarter_app diff tools/build_db.py` before deciding. `[ASSUMED]` |

---

## Open Questions

1. **Will the wiki push actually authenticate?**
   - Known: the token has `admin`/`push` on `firestarter_prom`; the wiki inherits that; a global
     credential helper is configured; Phase 168 pushed twice by this route; the anonymous clone works.
   - Unclear: the push itself was deliberately not exercised (read-only research constraint).
   - Recommendation: make it the first action of plan 171-01 with an explicit failure branch to the
     `https://$(gh auth token)@…` remote form applied in the scratch clone only.

2. **What is the disposition of `tools/build_db.py`'s uncommitted modification in `firestarter_app`?**
   - Known: it is unstaged, predates this phase, and is unrelated to documentation.
   - Unclear: whether it is abandoned work or in flight.
   - Recommendation: record it as an explicit exclusion in the phase record (Phase 117's
     `RED-BASELINE.md:632-641` is the precedent for how to state one honestly), and use path-scoped
     `git rm` / `git commit` so it cannot be swept in.

3. **Should the meta gitlink bump be framed as also completing Phase 170?**
   - Known: both gitlinks are one commit behind, and both gaps are Phase 170's ad-hoc README commits.
   - Unclear: whether Phase 170's record should be amended to note that its pins landed in 171.
   - Recommendation: say so plainly in the bump commit message; do not amend Phase 170's record
     (it is already reconciled at `.planning/notes/v135-phases-169-170-executed-ad-hoc.md`).

4. **Does the operator want the `_Sidebar.md` entry as `[Shell-Completion]` or `[Shell Completion]`?**
   - Known: the live sidebar mixes both conventions (lines 1-3 spaced, lines 4-9 hyphenated); both pass.
   - Recommendation: use `[Shell-Completion](Shell-Completion)` — matches the 6-line majority and
     `Home.md`'s Reference list. Falls under D-06's discretion; no operator question needed.

---

## Sources

### Primary (HIGH confidence — measured this session)

- `tools/wiki/wiki.py` (330 lines, read in full) — link/orphan/sidebar/filename contract; 4 runs incl. 2 negative legs
- `tools/wiki/honest01_claims.py:47,49,74-93,234` — `parse_migration_table` semantics
- `tools/wiki/honest02_truth.py` — 2 runs (before/after simulated add), rc=0 both
- `tools/wiki/dispatch_mirror.py:31,151-158` — argparse surface; 2 runs (workflow form rc=2, correct form rc=0)
- `.planning/v1.35/MIGRATION-TABLE.md` (145 lines, read in full) — column headers, retired-section shape, hyphen hazard
- `.github/workflows/wiki-check.yml` (108 lines, read in full) — legs, triggers, and its absence from `origin/main`
- `firestarter_app/MANIFEST.in`, `firestarter_app/pyproject.toml`, `firestarter_app/.github/workflows/ci.yml`
- `firestarter_app/autocomplete.md`, `things.md`, `SECURITY.md` — byte-level inspection + sha256
- Fresh clone of `firestarter_prom.wiki.git` @ `7ec99887` — all 10 files, `Home.md` and `_Sidebar.md` verbatim
- 4 sdist builds (live tree / pristine / pristine+SOURCES.txt / pristine-minus-3) + 3 PyPI sdists
- `gh api` — repo permissions, community profile, workflow list, contents endpoints
- `git` — branch/HEAD/gitlink state across all three repos, `d56424e` resolution, branch presence of all three files

### Secondary (MEDIUM confidence)

- `.planning/phases/168-…/evidence/migrate03-sdist-doc-delta.txt` — the pre-existing `SOURCES.txt` warning
- `.planning/phases/168-…/evidence/migrate03-py311-suite.txt:5-33` — py3.11 route and the sibling-install trap
- `.planning/phases/168-…/168-0*-PLAN.md` frontmatter — `commits_land_in:` precedent across 13 plans
- `.planning/notes/v135-wiki-only-reversal.md` — what the reversal voided and what survived
- `.planning/phases/167-…/167-CONTEXT.md:44,53,62,129` — D-02/D-03/D-04/D-11 naming and check scope
- `.planning/ROADMAP.md:236,238,371-378`; `.planning/REQUIREMENTS.md:58-61,174-176`; `.planning/STATE.md:236-241`

### Tertiary (LOW confidence)

- GitHub's default-branch-only scheduling rule for `cron`/`workflow_dispatch` (A2) — corroborated by
  measurement rather than taken on authority.

---

## Metadata

**Confidence breakdown:**

| Area | Level | Reason |
|---|---|---|
| Wiki working copy and its contents | **HIGH** | Cloned and read byte-exactly this session |
| `wiki.py links` contract | **HIGH** | Source read in full; 4 runs including both negative legs |
| CI status (C-1) | **HIGH** | Four independent measurements agree (`gh workflow list`, two `gh api` 404s, `git cat-file` on both branches) |
| Packaging (C-2) | **HIGH** | 4 controlled builds isolating a single variable, plus 3 published sdists |
| SHA provenance (C-8) | **HIGH** | All three sha256 figures reproduced exactly; byte-diff against working tree clean |
| Page shape deltas (C-3) | **HIGH** | Byte-level comparison against all 9 live pages |
| Security-policy surface (C-5) | **HIGH** | Branch presence measured 3 ways + community-profile API |
| Migration-table parser behaviour | **HIGH** | Source read; behaviour on the live 2-table file traced line by line |
| Wiki push mechanism | **MEDIUM** | Permission verified, mechanism not exercised (A1) — deliberately, per the read-only constraint |
| `tools/build_db.py` disposition | **LOW** | Out-of-band; needs an executor decision (Open Question 2) |

**Research date:** 2026-09-01
**Valid until:** 2026-10-01 for the tooling contracts; **7 days** for the live wiki state
(`7ec99887`, 9 pages) and the branch/gitlink positions — the operator edits the wiki directly and
out of band, so re-clone and re-run `wiki.py links` at execution time rather than trusting the
"9 pages" figure recorded here.
