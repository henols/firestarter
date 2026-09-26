# Phase 171: STRAY — The Root-Level Documentation Files - Pattern Map

**Mapped:** 2026-09-01
**Files analyzed:** 7 (1 created, 3 modified, 3 deleted)
**Analogs found:** 7 / 7

This is a documentation-disposition phase. "Analog" below means *the nearest document of the same
kind*, and every excerpt is markdown structure or a commit shape, not code. Where CONTEXT.md and
RESEARCH.md disagree, RESEARCH.md's measured text is what is reproduced here.

## File Classification

| New/Modified File | Repo | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|---|
| `Shell-Completion.md` (new) | wiki clone | wiki reference page | file-I/O (publish) | `Breaking-Changes.md` (wiki) | exact |
| `_Sidebar.md` (modified) | wiki clone | navigation index | file-I/O | its own state at wiki `7ec9988` | exact |
| `Home.md` (modified) | wiki clone | navigation hub | file-I/O | its own state at wiki `7ec9988` | exact |
| `.planning/v1.35/MIGRATION-TABLE.md` — main table row | meta | provenance record | machine-read table | `MIGRATION-TABLE.md:15` (`Install-Beta` row) | exact |
| `.planning/v1.35/MIGRATION-TABLE.md` — new "removed, never published" section | meta | provenance record | machine-read table | `MIGRATION-TABLE.md:45-58` ("Retired from the wiki…") | exact |
| `firestarter_app/things.md`, `SECURITY.md`, `autocomplete.md` (deleted) | app submodule | repo-root strays | — | `firestarter_app` `50f85b2` | exact |
| gitlink re-pin (meta) | meta | submodule pointer | — | meta `f62021b4` | exact |

---

## Pattern Assignments

### 1. `Shell-Completion.md` (new wiki page)

**Exemplar:** `Breaking-Changes.md` in the wiki clone — the most recently added page, and the one
whose creation commit is the commit-shape analog for this whole task (§4 below).

**The canonical opening, quoted verbatim** (`wiki-clone/Breaking-Changes.md:1-8`):

```markdown
<p align="left"><img src="https://raw.githubusercontent.com/henols/firestarter_app/refs/heads/main/images/firestarter_logo.png" alt="Firestarter EPROM Programmer" width="200"></p>

---

# Breaking Changes

Changes that require action when upgrading. Newest first.

```

Line 1 logo; line 2 blank; line 3 `---`; line 4 blank; line 5 `# <render_title(stem)>`; line 6 blank.
Byte-identical across all 8 non-`Home` pages — independently confirmed here against
`Install-Beta.md:1-8`, `Testing-Chips.md:1-8` and `Shield-Revisions.md:1-8`.

**The source's actual opening** (`firestarter_app/autocomplete.md:1-6`):

```markdown
<p align="left"><img src="https://raw.githubusercontent.com/henols/firestarter_app/refs/heads/main/images/firestarter_logo.png" alt="Firestarter EPROM Programmer" width="200"></p>

---
## Enabling Shell Autocompletion

Firestarter ships shell completion via [Click](https://click.palletsprojects.com/en/stable/shell-completion/)'s built-in `_FIRESTARTER_COMPLETE=<shell>_source firestarter` mechanism. No external dependency is needed — Click is already a Firestarter runtime dependency, so completion is available the moment Firestarter is installed.
```

**Exact target state for lines 1-6 of `Shell-Completion.md`** — three edits, and only three:

```markdown
<p align="left"><img src="https://raw.githubusercontent.com/henols/firestarter_app/refs/heads/main/images/firestarter_logo.png" alt="Firestarter EPROM Programmer" width="200"></p>

---

# Shell Completion

Firestarter ships shell completion via [Click](https://click.palletsprojects.com/en/stable/shell-completion/)'s built-in `_FIRESTARTER_COMPLETE=<shell>_source firestarter` mechanism. No external dependency is needed — Click is already a Firestarter runtime dependency, so completion is available the moment Firestarter is installed.
```

1. insert a blank line after `---`;
2. `##` → `#`;
3. `Enabling Shell Autocompletion` → `Shell Completion` (= `render_title("Shell-Completion")`).

`autocomplete.md:7-69` is copied unchanged. Its `###` section headings
(`### Bash` :10, `### Zsh` :20, `### Fish` :30, `### PowerShell` :46, `### pipx Installations` :57,
`### Migrating from a previous Firestarter` :65) sit one level below an `#` title, matching the
`##`/`###` nesting on every live page. The logo `<img src>` URL is already byte-identical to the
one every live page carries; no URL edit is owed.

**No checker catches any of the three edits** (RESEARCH.md §A.4, §B.5: a naive copy passes
`wiki.py links` with rc=0, and per C-1 there is no CI at all). The plan must assert them directly,
e.g. `sed -n '1,6p' Shell-Completion.md` diffed against the block above.

---

### 2. `_Sidebar.md` (wiki navigation)

**Current full contents** (`wiki-clone/_Sidebar.md:1-9`):

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

**The list is not alphabetical.** It is `Home` → getting-started (`Install-Beta`, `Testing-Chips`)
→ reference, in the order pages were added; `Breaking-Changes` was appended at the end by the
analog commit. Lines 4-9 use the bare page stem as link text; only lines 2-3 use a spaced title.
The recent convention is the stem.

**Insertion:** append as a new line 10, after `- [Breaking-Changes](Breaking-Changes)`:

```markdown
- [Shell-Completion](Shell-Completion)
```

---

### 3. `Home.md` (wiki hub)

**The Reference list as it exists right now** (`wiki-clone/Home.md:42-51`):

```markdown
## Reference

- [Programming-Protocols](Programming-Protocols) — how each protocol works and which chips it is for
- [Chip-Database-Fields](Chip-Database-Fields) — what every field in the chip database means
- [Pin-Maps](Pin-Maps) — pin maps for every chip family, and the DIP24 adapter
- [Lockable-PROMs](Lockable-PROMs) — which flash families can report whether they are write-protected
- [Shield-Revisions](Shield-Revisions) — telling the RURP shield revisions apart
- [Breaking-Changes](Breaking-Changes) — what changed between versions, and what to do about it

---
```

Row shape: `- [<Stem>](<Stem>) — <lowercase clause, no terminating period>`, the separator being an
em dash (U+2014) with a space on each side. Also not alphabetical; appended in addition order.

**Insertion:** a new line 50, between `Breaking-Changes` (:49) and the blank line preceding the
`---` at :51. This satisfies the transitive-BFS orphan leg with the simplest reachable path
(RESEARCH.md §B.5), and it is the placement D-06's discretion clause selects.

Suggested row, matching the shape byte-for-byte:

```markdown
- [Shell-Completion](Shell-Completion) — turning on tab completion for `firestarter` in your shell
```

`Home.md:5` is `# Firestarter`, the one deliberate exception to `render_title` — do not "fix" it.

---

### 4. `.planning/v1.35/MIGRATION-TABLE.md` — the two row shapes

**(a) Main table.** Header and separator, byte-exact
(`.planning/v1.35/MIGRATION-TABLE.md:10-11`):

```markdown
| Source repo | Source path | Wiki page | Rendered title | Pre-deletion SHA | Moved in |
|---|---|---|---|---|---|
```

Exemplar data row (`:15`) — note the source path carries the repo-name prefix and the SHA is full-length:

```markdown
| firestarter_app | firestarter_app/doc/beta-testing-install.md | Install-Beta | Install Beta | d56424e1979edf7245cffb9ec3111c0469f5b23f | 168 |
```

New Phase 171 row, appended after `:19`:

```markdown
| firestarter_app | firestarter_app/autocomplete.md | Shell-Completion | Shell Completion | d56424e1979edf7245cffb9ec3111c0469f5b23f | 171 |
```

**(b) The precedent for D-06's new "removed, never published" section.** Header and separator
(`.planning/v1.35/MIGRATION-TABLE.md:52-53`) — **three** columns, `|---|` separators with no colons:

```markdown
| Source path | Was published as | What happened |
|---|---|---|
```

Exemplar data row (`:55`) — path in backticks, page name in backticks, last cell free prose ending
in a period:

```markdown
| `firestarter_app/doc/pinout-safety-review.md` | `Pinout-Safety-Review` | Superseded by `Pin-Maps`, which is dedicated to pin maps rather than to a review. The 5 V-only guarantee it carried is restated there. |
```

The section is introduced by an `##` heading and a prose paragraph (`:45-50`); mirror that.

**Machine-reader constraint — this is a real break, not cosmetics.**
`parse_migration_table` (`tools/wiki/honest01_claims.py:74-93`) is the only reader
(`honest01_claims.py:234`). Its assumptions:

```python
TABLE_ROW_RE = re.compile(r"^\|(.+)\|\s*$")     # honest01_claims.py:47
NO_SHA_MARKER = "—"                              # honest01_claims.py:49  (U+2014)
```

- It sets `header` **once**, from the first table-shaped line in the whole file (`:84-86`), and
  never resets it. Every later table's rows are `zip`ped against that same 6-column header
  (`:92`).
- Rows survive only if `row.get("Pre-deletion SHA", NO_SHA_MARKER) != NO_SHA_MARKER` (`:93`).
- The existing 3-column retired table is therefore harmlessly absorbed: `zip` truncates at 3 cells,
  the rows get no `Pre-deletion SHA` key, and they are filtered out.

**Design rule the planner must carry into the task:** the new section's table must have **at most
4 columns**. Mirror the existing three and carry the recoverable SHA as inline code inside the last
cell (e.g. ``recoverable at `git -C firestarter_app show d56424e:things.md`.``). A ≥5-column table
would key its 5th cell as `Pre-deletion SHA`, survive the filter, and make `honest01` try to
resolve a non-migration row against a wiki page named by its 3rd cell.

Post-change expectation: `parse_migration_table` returns **8** rows (7 today + `Shell-Completion`),
and no row whose `Wiki page` is `things.md` or `SECURITY.md`.

Two facts for the row prose: `things.md` is **7 lines / 265 bytes, no trailing newline** (C-7 — do
not repeat CONTEXT.md's "5 lines" or the ROADMAP's "six lines"), and `SECURITY.md` opens
`# SECURITY.md` / `## Phase Security Audit` / `**Phase:** 69 — cli-command-surface-robustness-audit`
(`firestarter_app/SECURITY.md:1-5`).

---

### 5. The commit-shape analog

**(a) Wiki: add a page + both navigation edits in ONE commit.** Wiki repo `7ec9988`
`docs: add Breaking Changes, the destination for the README version history`:

```
 Breaking-Changes.md | 102 ++++++++++++++++++++++++++++++++++++++++++++++++++++
 Home.md             |   1 +
 _Sidebar.md         |   1 +
 3 files changed, 104 insertions(+)
```

Its two navigation hunks are exactly the shape Phase 171 must mirror — a single appended line at
the tail of each list:

```diff
--- a/Home.md
+++ b/Home.md
@@ -46,6 +46,7 @@ read and write chips.
  - [Shield-Revisions](Shield-Revisions) — telling the RURP shield revisions apart
 +- [Breaking-Changes](Breaking-Changes) — what changed between versions, and what to do about it

--- a/_Sidebar.md
+++ b/_Sidebar.md
@@ -6,3 +6,4 @@
  - [Shield-Revisions](Shield-Revisions)
 +- [Breaking-Changes](Breaking-Changes)
```

Subject line form: `docs: <what the page is for>`, no phase scope — the wiki repo carries no GSD
scoping. Body explains what the page carries and what hedges survived.

**(b) App submodule: deletions in one `chore` commit.** `firestarter_app` `50f85b2`
`chore(168-09): delete firestarter_app/doc/ (MIGRATE-02)` — 10 files, `1880 deletions(-)`, pure
removal, no other change in the commit. Phase 171's analog is a single
`chore(171-NN): delete the three root-level stray documents` removing `things.md`,
`autocomplete.md`, `SECURITY.md`.
Plan frontmatter precedent (`168-09-PLAN.md:7`): `commits_land_in: firestarter_app`.

**(c) Meta: MIGRATION-TABLE rows in their own commit.** `d10bd4b7`
`feat(168-01): fill 12 page names, titles and pre-deletion SHAs` —
`.planning/v1.35/MIGRATION-TABLE.md | 80 ++++…`, 1 file changed. The table is always touched alone.

**(d) Meta: gitlink re-pin last, as a separate commit.** `f62021b4`
`chore(168): advance submodule pointers and refresh gate evidence`:

```
 .../evidence/dispatch-mirror-planted-RED.txt | 2 +-
 .../evidence/honest01-weakened-claim-RED.txt | 2 +-
 firestarter                                  | 2 +-
 firestarter_app                              | 2 +-
```

Per C-6 this commit will also sweep up Phase 170's unpinned `firestarter_app 767079a` and
`firestarter c26562a`; the pre-existing `M firestarter` / `M firestarter_app` in `git status` is
not the executor's own uncommitted work.

**Ordering (RESEARCH.md §D.12):** wiki push → app deletions → meta table rows → meta gitlink.
Publish before deleting, so the content never exists nowhere.

**Wiki plan frontmatter precedent** (`168-05-PLAN.md:7`):

```yaml
commits_land_in: firestarter_prom.wiki.git (live public wiki) — no meta or sub-repo source commits except evidence
```

with the working copy declared as an out-of-tree path
(`<files>working clone of firestarter_prom.wiki.git (scratch path, outside all three repositories)</files>`,
`168-05-PLAN.md:81,162`).

---

## Shared Patterns

### Page-name legality and link form
**Source:** `tools/wiki/wiki.py:50-52` (`render_title` = `stem.replace("-", " ")`; `_LEGAL_TARGET_RE`
admits only `[A-Za-z0-9-]`). **Apply to:** the new page and both navigation edits.
`Shell-Completion` is legal, flat, and renders "Shell Completion". Internal links are bare stems —
`[Shell-Completion](Shell-Completion)` — never `.md`, never a path.

### The only available gate
**Source:** RESEARCH.md C-1 / §B.6. **Apply to:** every wiki task.
`.github/workflows/wiki-check.yml` is absent from `origin/main` and therefore does not run at all.
`tools/wiki/wiki.py links --source-dir <clone>` executed locally — once pre-push against the working
clone and once post-push against a **fresh** clone — is the only oracle. Do not write a verification
leg that invokes `gh workflow run`.

### Deletion is recorded, never silent
**Source:** `.planning/v1.35/MIGRATION-TABLE.md:45-58`. **Apply to:** all three deletions.
Every removal names the file, its disposition, and a recoverable SHA, so "what happened to this
document" stays answerable from the table alone.

### Relocate and correct only
**Source:** activation decision 4 (ROADMAP), reinforced by D-02/D-04/D-05. **Apply to:** the new
page and the table prose. The three shape edits are corrections; nothing else may be added. No
security-reporting statement anywhere; no `Breaking-Changes` entry for the argcomplete→Click swap.

### No comments in source
**Source:** project hard rule. **Apply to:** everything. No provenance comments, and no plan may
override this.

---

## No Analog Found

None. Every file in this phase's change surface has a close, recent, same-kind precedent.

---

## Out of the Change Surface (do not touch)

| File | Why |
|---|---|
| `firestarter_app/README.md` | Phase 170's closed output; D-02 and D-03 forbid editing it |
| `firestarter/PINOUTS.md`, `firestarter/PROTOCOLS.md` | Deliberate implementation references; `PROTOCOLS.md` is machine-read by `tools/wiki/dispatch_mirror.py` |
| `MIGRATION-TABLE.md:18-19` (`Protocol-Flags`, `Protocol-ID`) | Confirmed-real drift, explicitly deferred; this phase only appends |
| `.github/workflows/wiki-check.yml:104-107` | Pre-existing `--wiki-dir` defect (RESEARCH.md p.25); out of scope, but record it so a future red is not blamed on 171 |
| `firestarter/test/native/avr/test_eeprom28c_sdp/RED-BASELINE.md:637` | The second `SECURITY.md` grep hit (C-4); historical-by-intent, no action |

## Metadata

**Analog search scope:** `firestarter_prom.wiki.git` clone at
`/tmp/claude-1000/-workspaces/d4de2010-fc66-4b48-92c4-eb08304900bc/scratchpad/wiki-clone`
(HEAD `7ec9988`), `/workspaces/tools/wiki/`, `/workspaces/.planning/phases/168-*/`,
`/workspaces/firestarter_app` git history.
**Files read:** 12. **Pattern extraction date:** 2026-09-01.
