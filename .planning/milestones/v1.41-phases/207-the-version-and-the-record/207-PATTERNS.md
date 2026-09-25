# Phase 207: The version and the record - Pattern Map

**Mapped:** 2026-09-23
**Files analyzed:** 11 (4 sub-repo/meta commits in Plan 01 scope, 7 wiki files in Plan 02 scope)
**Analogs found:** 11 / 11

All analog paths below are git-tracked in their own repository. They were checked with `git ls-files` inside each submodule and inside the wiki clone. No path is a gitignored mirror.

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `firestarter_fw` merge of `origin/beta` into `v1.41-verification-to-host` (D-01) | merge commit | batch | `firestarter_fw` `5a7c18c` "Merge beta into v1.39-protocol-0x05-write-correctness" | exact |
| `firestarter_app` merge of `origin/beta` into `v1.41-verification-to-host` (D-01) | merge commit | batch | `firestarter_app` `0ef0563` "merge: bring origin/beta (3.0.0b37) into the v1.36 milestone branch" | exact |
| `firestarter_fw/include/version.h` (modify line 11) | config | transform | `firestarter_fw` `31fa175` "chore(09-02): bump firmware version 2.0.11-dev -> 3.0.0-dev" | exact |
| `firestarter_app/firestarter/__init__.py` (modify line 1) | config | transform | `firestarter_app` `cfc0e1c` "chore(v1.4): reconcile __version__ base to 3.0.0_dev …" | exact |
| `firestarter_app/README.md` lines 49-51 (F6 A, separate commit) | docs | n/a | `firestarter_app/README.md:49-51` itself, and commit `862628f` (docs-only README breaking-change commit) | exact |
| `/workspaces` meta gitlink advance (`firestarter_fw`, `firestarter_app`) | gitlink | batch | meta `5e675d35` "chore(204-01): advance firestarter_fw and firestarter_app gitlinks" | exact |
| `firestarter.wiki/Breaking-Changes.md` (rewrite preamble lines 9-19, add a new top section) | docs page | n/a | `Breaking-Changes.md` § `## v1.20` (lines 73-86) and § `## v1.32` (lines 23-69) | exact |
| `firestarter.wiki/Writing-and-Verifying.md` (NEW, F3 A) | docs page | n/a | `Testing-Chips.md` (command-centred page) and `Install-Beta.md` (tables and numbered steps) | role-match |
| `firestarter.wiki/Home.md` (add one line to § Reference) | nav | n/a | wiki `bf787fb` Home.md hunk | exact |
| `firestarter.wiki/_Sidebar.md` (add one line) | nav | n/a | wiki `bf787fb` `_Sidebar.md` hunk | exact |
| `firestarter.wiki/Install-Beta.md:47` and `Testing-Chips.md` (optional: stale example, version-pairing note) | docs page | n/a | same pages | exact |

## Pattern Assignments

### Merge `origin/beta` into each milestone branch (D-01, before the bump)

**Analogs:** `firestarter_fw` `5a7c18c` and `firestarter_app` `0ef0563`. Both are inward merges of `beta` into a milestone branch, made so a later conflict resolves on the milestone branch and not on `beta`.

Precedent message shape (`firestarter_app` `0ef0563`):
```
merge: bring origin/beta (3.0.0b37) into the v1.36 milestone branch

Pre-ship inward merge, per the project's recorded close procedure: resolve
on the milestone branch first, because the same commits can exist on both
sides with different SHAs.
...
Also brings beta's b37 version bump.
```
Precedent message shape (`firestarter_fw` `5a7c18c`):
```
Merge beta into v1.39-protocol-0x05-write-correctness

Brings the documentation-only work that cut 3.0.0b32 onto the milestone branch
before the milestone merges out to beta, so the conflict resolves here rather
than on beta.
```
- The subject names the beta version that the merge brings in. For this phase that is `3.0.0b50` (app) and `3.0.0b35` (fw).
- `git show --stat` of each precedent shows only the version file on the merge diff. RESEARCH Q2 predicts that this merge touches two files per repo: `.planning/codebase/STACK.md` plus `firestarter/__init__.py` in the app, and `.github/CONTRIBUTING.md` plus `include/version.h` in the firmware.
- Commands: RESEARCH § Code Examples "F1(A)" (`fetch origin beta`, `merge-tree --write-tree --name-only` expecting one line, `merge --no-ff origin/beta`).
- After the merge, the pre-bump line must read `#define VERSION "3.0.0b35"` and `__version__ = "3.0.0b50"`. Assert that before running `sed`.

---

### `firestarter_fw/include/version.h` (config, one-line transform)

**Analog:** `firestarter_fw` `31fa175`. The whole diff is the define line:
```diff
@@ -8,6 +8,6 @@
 #ifndef __VERSION_H__
 #define __VERSION_H__
 
-#define VERSION "2.0.11-dev"
+#define VERSION "3.0.0-dev"
 
 #endif // __VERSION_H__
\ No newline at end of file
```
**Current file** (`include/version.h:1-13`, read this session): the MIT header is on lines 1-6, the guard on lines 8-9, `#define VERSION "3.0.0b33"` on line 11 (it becomes `3.0.0b35` after the D-01 merge), and `#endif // __VERSION_H__` on line 13. **The file has no trailing newline.** An in-place `sed -i` on line 11 keeps that. Do not rewrite the file with the Write tool, which would add a newline and a spurious hunk.

**Commit message shape** (from `31fa175`): `chore(NN-NN): bump firmware version <old> -> <new>`, then a body giving the reason. For example, `chore(207-01): bump firmware version 3.0.0b35 -> 3.1.0b1`, with a body naming the minor bump (PROJECT.md D-5) and noting that CI discards the source suffix (RESEARCH Q1). **The commit contains only this one file** (V2 asserts `show --name-only` == `include/version.h`).

---

### `firestarter_app/firestarter/__init__.py` (config, one-line transform)

**Analog:** `firestarter_app` `cfc0e1c`. It is a one-line diff on the file's only line:
```diff
@@ -1 +1 @@
-__version__ = "2.0.7_dev"
+__version__ = "3.0.0_dev"
```
The body of `cfc0e1c` says why the base moves "for lockstep with firmware". Copy that framing: name the firmware sha from the previous commit ("Pairs with firestarter_fw <fw-sha>"). The bot commits on `origin/beta` (`c6e48ff` "Apply automatic changes") have the same one-file stat, `firestarter/__init__.py | 2 +-`. **The commit contains only this file.** The F6 README fix goes in its own commit (next section).

---

### `firestarter_app/README.md` lines 49-51 (docs, F6 A)

**Current text** (`README.md:49-51`, read this session):
```markdown
**The CLI and the firmware are upgraded together.** A mismatched pair fails with a timeout or a
decode error — see
[Breaking Changes](https://github.com/henols/firestarter/wiki/Breaking-Changes).
```
- Keep the bold lead sentence plus the absolute wiki URL. README links are absolute `https://github.com/henols/firestarter/wiki/<Page>` (lines 51, 57, 100). Relative page links are for wiki pages only.
- Replace the false "timeout or a decode error" claim with the per-entry wording chosen for the wiki preamble (F5), for example "upgrade the CLI first, then the firmware", and keep the link. The link target can stay the page root. A GitHub wiki anchor to the new `## 3.1.0b1 — …` heading is fragile because of the em dash, so linking the page root is safer.
- The install block above it (lines 41-44: `pip install --pre firestarter` / `firestarter fw -i --pre`) is already in the right order. Leave it.
- **Commit analog:** `862628f` "docs(148-08): state the breaking numeric schema and VCC correction in README", a docs-only README commit that is separate from code. Make this a separate app commit after the version commit, so the V2 check on the version commit uses the recorded sha rather than `HEAD` (RESEARCH V2 note).

---

### Meta gitlink advance (`/workspaces`, gitlink, batch)

**Analog:** meta `5e675d35`:
```
chore(204-01): advance firestarter_fw and firestarter_app gitlinks

- firestarter_fw @ 268d844 (feat(204-01): retire ordinal 6 from the firmware)
- firestarter_app @ f6d3724 (feat(204-01): retire ordinal 6 from the host)

 firestarter_app | 2 +-
 firestarter_fw  | 2 +-
```
- The body carries one bullet per sub-repo, in the form `<name> @ <short-sha> (<subject>)`. With F6 A the app HEAD is the README commit, so name both app commits (the version commit and the README commit) or name HEAD and note the pair.
- Stage the two gitlinks by explicit path only (`git add firestarter_fw firestarter_app`). The meta working tree has unrelated dirty files (`.devcontainer/*`, `.vscode/*`, `anything.txt`, `tmp/`, and others) that must not ride along.
- Current gitlinks: `firestarter_app d723cf7`, `firestarter_fw 6e11d05` (`git ls-files -s`). Both equal the sub-repo HEADs before this phase.
- After the commit, run V10 (`rev-parse --abbrev-ref HEAD` == `v1.41-verification-to-host`) and V2's `ls-tree` equality.

---

### `firestarter.wiki/Breaking-Changes.md` (docs page, modify)

**Page skeleton** (lines 1-21, read in full this session):
```markdown
<p align="left"><img src="https://raw.githubusercontent.com/henols/firestarter_app/refs/heads/main/images/firestarter_logo.png" alt="Firestarter EPROM Programmer" width="200"></p>

---

# Breaking Changes

Changes that require action when upgrading. Newest first.

**The firmware and the CLI are upgraded together.** Every wire-protocol change   <- lines 9-12: FALSE for 3.1.0b1 (F5)
below breaks mixed versions — ...

```bash
pip install --pre firestarter && firestarter fw -i --pre
```

All of these are beta-only. Nothing is promoted to stable without operator
authorization.

---

## v1.32 — chip database          <- line 23: the new section goes ABOVE this ("Newest first")
```
- **Where to insert:** directly after the preamble's closing `---` (line 21) and before `## v1.32 — chip database`. Put a `---` rule between sections, as on lines 71 and 88.
- **Heading (F4):** `## 3.1.0b1 — verify and blank check run on the host`. It follows the `## <label> — <topic>` shape of lines 23, 73 and 90, using the product version, never `v1.41`.
- **Sub-entry shape to copy** (§ v1.32, lines 25-37): a `###` sub-heading per change, one plain paragraph stating the change, a **bold sentence** giving the user consequence, then a `**Upgrade:**` paragraph:
  ```markdown
  ### The database stores numbers, not unit-suffixed strings
  ...
  **If you have a `~/.firestarter/database.json` override written against the old
  schema, it will no longer load.** The failure is loud — ...

  **Upgrade:** rewrite your override with the new key names ...
  ```
- **Mixed-version statement shape to copy** (§ v1.20, lines 84-86): a bold lead naming the pairing, then the plain consequence:
  ```markdown
  **A stale host is not harmful to new firmware.** The firmware skips unknown JSON
  fields, so a `type` field simply does nothing.
  ```
  Use the same form for "**An older CLI on 3.1.0b1 firmware …**" / "**A 3.1.0b1 CLI on older firmware …**". Put the compatibility matrix (W2-W6) in a markdown table in the style of `Install-Beta.md:20-24` (`| … | … | … |` with a `|---|---|---|` rule). Lead with the unguarded write (W3, F10).
- **Hedge convention:** § v1.32 lines 62-65 state an unproven effect plainly ("**software-proven and unvalidated on silicon**"). Use the same register for the code-derived rows A1-A3 (old-host `erase -b`, new-host plain `erase`). Do not state them with the confidence of the bench-observed rows.
- **Preamble rewrite (F5):** replace lines 9-12 with a per-entry statement, for example "Each entry says which mixed pairings work. When in doubt, upgrade the CLI first, then the firmware." Keep the bash block on lines 14-16 and lines 18-19 unchanged. V7 greps lines 1-25 for `a new CLI cannot drive old firmware`.
- **Do not touch line 102** (`<!-- firestarter-claim-stamp: … verified=2026-08-31 -->`). Editing it would claim a re-verification that nobody performed (RESEARCH Q4 item 5). It must remain the last line.
- Link to the new page with a relative link, `[Writing and Verifying](Writing-and-Verifying)`, the same form as `[Install Beta](Install-Beta)` in `Home.md:56`.
- Content facts: RESEARCH § Wiki Content Specification W1-W6 and W10. Quote verbatim `ERROR: Unknown command: 6` / `ERROR: Unknown command: 4` in backticks so a search lands on them (F9: no catalog id).

---

### `firestarter.wiki/Writing-and-Verifying.md` (NEW docs page, F3 A)

**Analog 1:** `Testing-Chips.md` (107 lines). It is the only page centred on one command. Copy its structure:
- Lines 1-5: logo `<p>` line, blank line, `---`, blank line, `# Title`. **Every page starts with that exact logo line** (wiki commit `ddcddcc` "put the logo on every page").
- Lines 7-15: a short intro paragraph, a prerequisite link ("You need the beta — see [Install Beta](Install-Beta)."), then a `bash` code block showing the command form (`firestarter dev test <chip>`).
- Lines 17-31: a `---` rule between each `##` section. A **bold safety sentence** opens the dangerous section ("**`dev test` writes to the chip.** There is no prompt…"). Use the same form for `--skip-erase` ("WARNING: skipping erase on a non-blank electrically-erasable chip…").
- Lines 46-58: a bullet list with **bold family names** ("**UV-erasable EPROMs** — …", "**SRAM and FRAM** — …"). Use it for W7's "which parts get the pre-write check" (UV EPROMs checked; erasable parts only with `--skip-erase`, NOR flash also at a non-zero address; never `0x0D`, `0x05`, SRAM, FRAM).
- Lines 60-65: a paragraph on a flag that opens with the flag in backticks and states a weaker or stronger contract (`dev test --fast`). Copy it for `--verify` and `--full`.

**Analog 2:** `Install-Beta.md` (101 lines), for tables and numbered `## 1. …` sections:
```markdown
| Your board | Board flag | How to tell |
|---|---|---|
| Arduino Uno | `-b uno` | Says "UNO" on the board. ... |
```
Use a table like this for the exit-code contracts: `write` without `--verify` (0/1), `write --verify` (0/1/2), `verify` (0/1/2), `blank` (0/1/2), and `erase -b` (0/1/2). Also tabulate the four `write --verify` verdict lines (RESEARCH Q5).

**Footer:** pages migrated from the repos end with `*Relocated from … not re-verified against the code.*` (`Testing-Chips.md:107`, `Shell-Completion.md:74`). **A new wiki-native page carries no such footer.** `Contributing.md`, which was authored on the wiki, has none. Do not add a claim-stamp comment either, because its checker is retired.

**Sections to cover** (W7-W10): `write` (`-b`/`--no-blank-check`, `--skip-erase`, the region-scoped host check, the refusal line `Refusing write to <chip>: not blank at 0x…, v: 0x….`), `write --verify` / `--full`, `verify` and `blank` (`-a`/`-s`, `--full` with at most 64 ranges plus a summary line, the classification labels), and `erase -b` (the inverse of `write -b`; `-s` plus `-b` is refused with exit 2). Label every new statement "from 3.1.0b1" (D-03). **No `Phase NNN`, `D-NN`, `.planning/` or `v1.41` text** (V7 negative grep).

---

### `firestarter.wiki/Home.md` and `_Sidebar.md` (nav, one line each)

**Analog:** wiki `bf787fb` (Shell-Completion added). That one commit carried the new page and both navigation hunks:
```diff
--- a/Home.md
@@ -47,6 +47,7 @@ read and write chips.
 - [Breaking-Changes](Breaking-Changes) — what changed between versions, and what to do about it
+- [Shell-Completion](Shell-Completion) — turning on tab completion for `firestarter` in your shell
--- a/_Sidebar.md
@@ -7,3 +7,4 @@
 - [Breaking-Changes](Breaking-Changes)
+- [Shell-Completion](Shell-Completion)
```
- `Home.md` § Reference (lines 42-51): the form is `- [Page-Name](Page-Name) — <what it tells a user, lower-case clause>`. A sensible position for a command reference is the top of the list (above `Programming-Protocols`, line 44) or next to `Breaking-Changes` (line 49). It is the executor's choice, and the operator reviews it at the checkpoint.
- `_Sidebar.md` (11 lines): the form is `- [Page-Name](Page-Name)`. Link text is either hyphenated (`Breaking-Changes`) or spaced (`Install Beta`, `Testing Chips`, lines 2-3). The user-workflow pages at the top use spaces, so `- [Writing and Verifying](Writing-and-Verifying)` next to `Testing Chips` fits.
- The same precedent (`7ec9988`, `dc07042`, `bf787fb`) puts the new page plus both navigation lines in **one** commit.

---

### Optional: `Install-Beta.md:47` and `Testing-Chips.md`

- `Install-Beta.md:47`: "`--version` must print a beta version such as `3.0.0b34`". The example is stale and the rule is not wrong. Updating it to `3.1.0b1` is a single-token edit.
- `Testing-Chips.md` § "How to report it" (lines 83-103): a place for one sentence saying that CLI and firmware must both be 3.1.0b1 or later (or both older) for a report to be valid (W4, RESEARCH Q4 item 4). Copy the plain-sentence tone of lines 102-103.

## Shared Patterns

### Wiki commit and push (applies to all wiki files)
**Source:** v1.35 Phase 171-01 (RESEARCH Q4) and wiki history.
- Author and commit in `/workspaces/firestarter.wiki` on `master`, on top of the unpushed `f967398` (D-02). Run `git fetch` first and confirm `origin/master` is still `81229d8`.
- Commit subjects: recent wiki commits use a plain imperative subject with no GSD ids (`f967398` "Repoint the tracker at …", `bf787fb` "docs: add Shell Completion, …"). The wiki history is public, so keep phase and `D-NN` ids out of wiki commit messages as well as page text.
- Wiki commit author on the clone is `Henrik Olsson` (the last three commits are all his). Use the clone's configured identity; do not override it.
- Before the push, run the `checkpoint:human-action` (D-03). It shows the full `git log --oneline origin/master..HEAD` with `f967398` named, the commit `--stat`, and the navigation hunks. After the push, run V7 and V8 against a fresh clone in scratch.
- Link form inside the wiki is relative (`[Text](Page-Name)`). V8 checks that every `](Page-Name)` has a matching `Page-Name.md`.

### Sub-repo commit mechanics (applies to the version, README and merge commits)
**Source:** memory `project_v18_phase_execution_mechanics` and the 204 precedent (`204-01-SUMMARY.md:153`).
- Commit inside each submodule on `v1.41-verification-to-host`. Never on `beta`, never pushed in this phase.
- Order: firmware version commit, then app version commit (its body names the firmware sha), then the app README commit, then the meta gitlink.
- Record the commit sha trio in the SUMMARY, in the form "firmware `<sha>`, host `<sha>`, meta gitlink advance `<sha>`" (`204-01-SUMMARY.md:153`).

### Verification idioms (applies to every verify block)
**Source:** RESEARCH § Verification Commands V0-V10 and Pitfall 6.
- Use `/usr/bin/grep -F -e '<pattern>'`, never bare `grep` (the shell `grep` is ugrep with `--ignore-files`). Assert with `[ "$x" = "expected" ]` or `|| { echo FAIL; exit 1; }`.
- The REL-01 oracle is `GITHUB_REF=refs/heads/beta python3 .github/scripts/update_version.py --dry-run`, which prints `DRY_RUN: 3.1.0b1` in both repos (V3).
- The clean-merge oracle is `git merge-tree --write-tree --name-only HEAD origin/beta | wc -l` == 1 (V4).

## No Analog Found

None. Every file has an in-repo precedent. The page name `Writing-and-Verifying` itself is a judgement call (RESEARCH A6). There is no existing command-reference page, so the page structure comes from `Testing-Chips.md` and `Install-Beta.md`.

## Metadata

**Analog search scope:** `firestarter_fw` and `firestarter_app` git history (`--merges --grep=beta`, `log -- README.md`, `include/version.h`, `firestarter/__init__.py`), the meta repo history (gitlink commits 5e675d35 and 85e49226), and all wiki pages plus the wiki history (`bf787fb`, `7ec9988`, `dc07042`, `f967398`).
**Files scanned:** 14 (version.h, __init__.py, README.md, Breaking-Changes.md, Home.md, _Sidebar.md, Shell-Completion.md, Install-Beta.md, Testing-Chips.md, Contributing.md, plus 10 commits shown).
**Pattern extraction date:** 2026-09-23
