# Phase 193: The Deferred Claim, Made Measurable - Pattern Map

**Mapped:** 2026-09-14
**Files analyzed:** 5
**Analogs found:** 5 / 5
**Repo type:** meta/planning repository — there is no application codebase here. Every analog below is
a tracked file in this repo (verified with `git ls-files`), not a mirror and not a sub-repo file.

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `tools/adoption/pypi_version_share.sh` (new) | meta tool (shell) | request-response (HTTP query → stdout verdict) | `tools/catalog/sync_to_subrepos.sh` | role-match (same tier, same shell conventions; different data flow — sync vs query) |
| `CLAUDE.md` §"Milestone close and branch protection" (GATE-02 bullet) | config/instructions | prose rule + cited mechanism | `CLAUDE.md:74-77` (the section itself) | exact — the pattern is in the very section being edited |
| `CLAUDE.md` §"Repository Structure" (GATE-03 pointer) | config/instructions | prose pointer | `CLAUDE.md:12` sentence + `CLAUDE.md:77` bullet | exact |
| `.planning/notes/<gitmodules-trap>.md` (new) | note / record | transcript-carrying analysis | `.planning/notes/v135-close-procedure-under-protection.md` (primary), `.planning/notes/999.9-repo-rename-impact-analysis.md` (secondary) | exact |
| `.planning/seeds/SEED-claim-firestarter-slug.md` (rewrite) | seed | frontmatter + prose | itself (current shape) + the 15 sibling seeds | exact |
| `${phase_dir}/evidence/*.txt` (new transcripts) | evidence | captured command/output log | `189-rename-03-fresh-clone.txt`, `192-02-preserved-history.txt` | exact |
| `${phase_dir}/evidence/193-*-disposition.md` (optional) | evidence | criterion-by-criterion record | `191-stable-disposition.md`, `192-disposition.md` | exact |

---

## Pattern Assignments

### `tools/adoption/pypi_version_share.sh` (meta tool, request-response)

**Analog:** `tools/catalog/sync_to_subrepos.sh` — `tools/`'s only runnable shell precedent. Mode `0755`
(`-rwxr-xr-x`), no CI runs it, no test covers it.

**Header + preamble pattern** (lines 1-25, verbatim shape):

```bash
#!/usr/bin/env bash
#
# Firestarter v1.2 catalog sync.
#
# Generation happens HERE, in the meta repo, and nowhere else. This script
# regenerates messages.h (firmware) and messages.py (host) from the canonical
# catalog and writes them into the sub-repos. The sub-repos receive generated
# ARTIFACTS only -- they do not carry codegen.py or messages.toml, and must
# never regenerate for themselves.
#
# Authoritative source: tools/catalog/{messages.toml,codegen.py}
# Generated firmware artifact: firestarter/include/messages.h
# Generated host artifact:     firestarter_app/firestarter/messages.py
#
# Idempotent: re-running with no upstream change is a no-op.
# Run after every catalog or codegen edit.
#
# Requirements: bash, cp, diff, python3, mktemp; ruff for the host artifact.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
```

Copy exactly these elements:
- `#!/usr/bin/env bash` then a `#`-block naming **purpose**, **authoritative source**, and a
  `Requirements:` line (here: `bash, curl`). Permitted by D-17 — meta `tools/` sits outside the
  no-comments hard rule. Still forbidden: `# Phase 193`, `# GATE-01`, any plan/milestone citation.
- `set -euo pipefail` immediately after the header block.
- `SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"` — only if the script needs self-location.
  The instrument takes no arguments and reads no sibling files (D-01), so it may legitimately omit
  `SCRIPT_DIR`; the analog's other conventions are not optional.
- Mode `0755` on commit (`chmod +x`).

**Precondition-guard pattern** (lines 27-32) — the shape of "fail loudly before doing work":

```bash
for f in messages.toml codegen.py; do
    if [[ ! -f "$META_REPO_CATALOG/$f" ]]; then
        echo "ERROR: canonical source missing: $META_REPO_CATALOG/$f" >&2
        exit 1
    fi
done
```

Adapt to the instrument's **one permitted guard** (D-01, RESEARCH Pitfall 2): branch on the in-query
`count() AS rows` column, plus `curl --fail-with-body` rc. Do **not** grow this into a staleness gate.

**Section-banner pattern** (lines 34-37) — used to separate the two artifacts; the instrument uses the
same banner to separate the verdict block from the caveat block:

```bash
# ---------------------------------------------------------------------------
# Firmware artifact: firestarter/include/messages.h
# ---------------------------------------------------------------------------
echo "Regenerating firestarter/include/messages.h ..."
```

**Outcome-reporting pattern** (lines 45-51, 68-75) — three severities, all to the right stream:

```bash
if diff -q "$tmp_h" "$FS_ROOT/include/messages.h" >/dev/null 2>&1; then
    echo "  OK: firestarter/include/messages.h regenerated."
else
    echo "ERROR: regenerated messages.h did not land at $FS_ROOT/include/messages.h" >&2
    exit 1
fi
...
    echo "WARNING: ruff not found -- messages.py written WITHOUT normalization." >&2
    echo "         Install ruff and re-run, or the committed file will show formatting drift." >&2
...
echo "OK: catalog synced to both sub-repos."
```

`OK:` / `WARNING:` / `ERROR:` prefixes, two-space indent for sub-lines, errors and warnings to `>&2`,
a final single-line `OK:` summary on stdout. The instrument's verdict line and caveat block go to
**stdout** (they are the product), query failures to **stderr**.

**Cleanup pattern** (line 39-40) — if any temp file is used:

```bash
tmp_h="$(mktemp)"
trap 'rm -f "$tmp_h" "${tmp_py:-}"' EXIT
```

**No analog for:** the `curl -G` / ClickHouse call itself. `tools/catalog/` makes no network calls.
Take the query verbatim from `193-RESEARCH.md` §Code Examples 2 (verdict) and 3 (window probe) — they
were executed and reproduce D-09's baseline exactly. Do not re-derive them.

---

### `CLAUDE.md` — GATE-02 bullet (config, prose rule)

**Analog:** the target section itself, `CLAUDE.md:72-77`. This *is* the template D-13 names. Verbatim:

```markdown
## Milestone close and branch protection

- **`main` is protected in all three repositories** — pull request required, no direct push, no force-push, no deletion. `current_user_can_bypass` is `never`, so no person can bypass.
- **This project's close targets `beta`, not `main`.** `.planning/config.json` sets `git.base_branch` to `beta`, so `/gsd-complete-milestone` and `/gsd-ship` both point there.
- **Before running `/gsd-ship`, recreate local `beta` from `origin/beta`** — `ship.md` anchors its audit range on `RANGE_BASE=$(git merge-base "${BASE_BRANCH}" HEAD)` and local `beta` goes stale. Cited by content, not line number: `workflows/ship.md` is installer-owned and a GSD version bump moves its lines.
- **The mechanics, the blocked stable-release route and the consumer sites are in `.planning/notes/v135-close-procedure-under-protection.md`.**
```

Structural rules to copy, in order:
1. **Bold imperative opener, then an em-dash clause giving the reason.** `- **<rule>** — <why>.`
2. **One rule per bullet, single line, no wrapping.** (Wrapped bold labels break GSD's
   decision-coverage gate; the whole file holds this convention.)
3. **Mechanism cited, never restated.** Line 76 is the in-file precedent for the *"Cited by content,
   not line number"* idiom — use that exact idiom when citing
   `.planning/notes/999.9-repo-rename-impact-analysis.md` §"Standing rule this must produce", because
   F-6 proved that note's own `firmware.py:272-288` range is already stale.
4. **The "see the note" bullet stays last.** Insert the GATE-02 bullet between current lines 76 and 77.
5. Backticks around every path, branch, command and version token.

Use `3.0.0b29` (the requirement's value), not the note's `3.0.0b28` — both evaluate `True`, but
criterion 3 should match literally.

---

### `CLAUDE.md` — GATE-03 pointer (config, prose pointer)

**Analog:** `CLAUDE.md:12`, the single long Repository Structure paragraph. Verbatim tail:

```markdown
This repo tracks `.planning/` (GSD project management artifacts), `.claude/` (project settings), `tools/` and `.github/` (repo-level tooling and CI). Neither sub-repo is committed here. ... `tools/` now holds `catalog/` alone — and **no automated wiki guard exists now**.
```

Patterns:
- **One dense paragraph, one line in the file, no hard wrapping.** Facts are chained with `;` and `—`,
  each carrying its retirement/creation date and often a short sha (`5426d7ef`).
- **Bold only on the load-bearing negative** (`**no automated wiki guard exists now**`). The GATE-03
  pointer's bolded clause should be the equivalent trap statement.
- The same sentence carries the `tools/` inventory, so the D-15 pointer edit must also correct
  "`tools/` now holds `catalog/` alone" in the same edit (RESEARCH Open Question 1). Adding
  `tools/adoption/` falsifies it.
- The note citation follows line 77's form: `.planning/notes/<file>.md`, by path and section heading,
  never by line number.

---

### `.planning/notes/<gitmodules-trap>.md` (note, transcript-carrying)

**Analog (primary):** `.planning/notes/v135-close-procedure-under-protection.md` — the note `CLAUDE.md`
already cites, i.e. the exact relationship D-13/D-15 recreate.

**Header pattern** (lines 1-5):

```markdown
# v1.35 — The GSD close procedure under branch protection

**Date:** 2026-09-02
**Raised during:** Phase 173 (POLICY-05)
**Status:** Decided and applied — `.planning/config.json` now sets `git.base_branch` to `beta` and `git.protected_branches` to `["main"]`
```

`999.9-repo-rename-impact-analysis.md:1-5` adds a fourth key the new note should carry, because its
claims are executed:

```markdown
**Method:** Direct inspection of the three working trees and the live GitHub / PyPI APIs on 2026-09-13. No research subagent was involved and no claim here is second-hand; every figure below is reproducible with the command noted beside it.
```

**No YAML frontmatter.** Neither note has any — bold key/value lines only.

**Section-heading pattern** (`##`, sentence-case, plain-spoken, no numbering):

| v1.35 note | 999.9 note |
|---|---|
| `## The decision` | `## The proposal` |
| `## What this changes` | `## The single destructive act` |
| `## The route into main, and where it stops` | `## Blast radius` (+ `###` sub-sections) |
| `## Banked evidence — the pull-request route already works` | `## Standing rule this must produce` |
| `## A premise this requirement rests on that is not true` | `## The `.gitmodules` archaeology trap` |
| `## What this costs` | `## Ordered procedure` |
| `## A note on link stability` | `## Honest limits` |

Two headings the new note should reuse by name: **`## Honest limits`** (999.9) carries what is not
known — the right home for A3's "the post-claim failure shape is a projection, not an observation"
(D-16 forbids claiming a breakage that has not happened), and for F-5's "the trap does not bite today".
**`## Banked evidence — …`** (v1.35) is the heading form for pointing at the committed transcripts.

**Transcript-embedding pattern** (v1.35 note, lines 13-22): a fenced block of raw captured output,
followed immediately by prose explaining *which line is the discriminator and why the others prove
nothing*:

```markdown
```
base-branch before: main
is-protected beta before: false
...
```

The two distinguishing flips are `git.base-branch` moving from `main` to `beta`, and
`--is-protected beta` moving from `false` to `true`. `--is-protected main` reads `true` both before
and after — ... so that read-back alone would prove nothing.
```

Apply this directly to F-4's `submodule sync` transcript: show the before/after `git config --get`
readings, then state that the child's `origin` was rewritten too, so the repair needs **both** commands.

**Ordered-procedure pattern** (999.9, lines 102-118): `**Phase A — …**` bold phase label, then a
numbered list of literal commands with the consequence stated inline. Use this shape for the
workaround + repair sequences.

---

### `.planning/seeds/SEED-claim-firestarter-slug.md` (seed, frontmatter + prose)

**Analog:** itself. Current frontmatter, verbatim (lines 1-6) — four keys, single-line plain scalars,
the shape all 16 seeds in `.planning/seeds/` use:

```yaml
---
title: Claim henols/firestarter for the meta repo (the destructive half of 999.9)
trigger_condition: A stable release of the app carrying the firestarter_fw firmware URLs has shipped AND has displaced 2.0.7 as the dominant PyPI version
planted_date: 2026-09-13
status: dormant
---
```

Preserve all four key names and their order. `planted_date` does **not** change (it records when it was
planted, not when it was edited). `status: dormant` must survive — RESEARCH F-7 proved a
`trigger_condition` value **starting** with a backtick makes `extractFrontmatter` return `{}`, dropping
every key including `status`, after which `audit.cjs` `scanSeeds` fails open and the seed silently
vanishes. **Start the scalar with a word**; RESEARCH F-7 gives a verified `>-` folded form.

`.planning/seeds/phase-gate-expiry-discipline.md` is the only sibling adding keys (`resolved`,
`resolved_by`) — that is the resolved-seed shape, not applicable here (this seed stays dormant).

**Body section headings, unchanged** (lines 8-53):

```markdown
# Claim `henols/firestarter` for the meta repo
## Why it is separable
## Why the trigger is what it is          <- D-12 rewrite target (lines 25-30)
## Do not fire this while any of these is untrue   <- 3 bullets, lines 34-38
## Carry this rule forward when it fires
## Known residual, accepted
Full analysis: `.planning/notes/999.9-repo-rename-impact-analysis.md`.
```

Prose patterns to hold while rewriting:
- **Short paragraphs, bold on the operative word only** (`**deletes**`, `**stable**`, `**2.0.7**`).
- The trailing bare `Full analysis: …` line, unheaded, stays last.
- The `## Known residual, accepted` section already carries the never-upgrade residual — D-02's caveat
  language must not contradict it.
- Line 30 — *"Gate on that stable having shipped and having displaced 2.0.7 — not on a calendar date."*
  — is what D-11's re-examination date must not contradict. Keep the sentence's force; add the review
  point as a separate clause, not as a replacement.
- The checklist's third leg (`.gitmodules` points at `firestarter_fw` …) is **false on `origin/beta`
  today** (F-2). Scope it to `main` or annotate, per RESEARCH Open Question 2.

---

### `${phase_dir}/evidence/*.txt` (evidence, captured transcript)

**Analogs:** `.planning/phases/189-free-the-name/evidence/189-rename-03-fresh-clone.txt` (closest — a
fresh-clone submodule transcript, the very act D-16 repeats) and
`.planning/phases/192-live-references-only/evidence/192-02-preserved-history.txt`.

**Naming convention:** `<phase>-<plan-or-req-id>-<subject>.txt`, all lowercase, hyphenated —
`189-rename-03-fresh-clone.txt`, `191-url-02-merged-main.txt`, `192-02-enumeration.txt`. The GATE-03
transcripts follow as e.g. `193-gate-03-existing-clone.txt`, `193-gate-03-fresh-clone.txt`,
`193-gate-03-submodule-sync-hazard.txt`.

**Transcript shape** — *not* a raw `script(1)` capture. It is a hand-structured, key/value-plus-banner
log. From `189-rename-03-fresh-clone.txt` (lines 1-14):

```
FRESH CLONE FIXTURE (RENAME-03)
================================
meta_source: file:///workspaces
meta_ref: v1.38-repository-rename
meta_commit: 5aba9dbc8d760e530638931d19ede0a227dd1a60
gitmodules_url(firestarter): git@github.com:henols/firestarter_fw.git
config_url(firestarter): git@github.com:henols/firestarter_fw.git
remote_origin(firestarter): git@github.com:henols/firestarter_fw.git
remote_origin(firestarter_app): git@github.com:henols/firestarter_app.git
firestarter_head: 10ec1b0e24d98f04c3b4aa076b9d84231ac5da04
firestarter_app_head: f926e36262c368633b50245a225478ef36aed885

FRESH CLONE OK
```

Copy:
- ALL-CAPS title line + `=====` underline; a terminal verdict line (`FRESH CLONE OK`).
- `snake_case_key(qualifier): value` for every observable; full 40-char shas, never abbreviated.
- Multiple readings in one file, separated by a `====` banner and a labelled heading
  (`READING 2 -- after the gitlink advance (189-03, Task 3)`), each with a `capture_date:`.
- **Prose annotation is expected and load-bearing.** Both analogs explain in-file why a reading means
  what it claims, and 189's second reading explicitly labels an expected-not-a-regression failure
  (`note: expected between this phase's gitlink advance and the milestone push -- not a URL regression`).
  That is exactly the register D-16 demands for "the trap does not bite today".
- `192-02-preserved-history.txt:5-9` shows the method line convention — name the exact command used and
  the `/usr/bin/grep` caveat:

```
Captured by: `git -C /workspaces rev-parse HEAD`, then `/usr/bin/grep -n -F` (never PATH
`grep`, which is ugrep here and honours `.gitignore`) locating each anchor by content in
the pre-remap tree at the SHA above.
```

**Optional companion `.md`:** `191-stable-disposition.md` / `192-disposition.md` — a criterion-by-
criterion record, one `## Criterion N — <verbatim criterion>` section each, every claim naming the
evidence file that supports it (`— evidence/191-url-02-merged-main.txt`). Use it if the phase wants a
single artefact answering the ROADMAP's four criteria.

---

## Shared Patterns

### Notes are cited by path + section heading, never by line number
**Source:** `CLAUDE.md:76` — *"Cited by content, not line number: `workflows/ship.md` is installer-owned
and a GSD version bump moves its lines."*
**Apply to:** both `CLAUDE.md` additions, the new note, the seed.
F-6 proves the need: the 999.9 note's own `firmware.py:272-288` citation is already stale (the symbol
is at :282 / :271 / :132 on three different refs).

### `/usr/bin/grep`, never PATH `grep`
**Source:** `192-02-preserved-history.txt:5-9` (quoted above).
**Apply to:** every sweep this phase runs and every command reproduced in a transcript. The
devcontainer's `grep` is ugrep and honours `.gitignore`, silently under-scanning.

### Every figure carries the command that produced it
**Source:** `999.9-repo-rename-impact-analysis.md:5` (`**Method:** … every figure below is reproducible
with the command noted beside it`) and `191-stable-disposition.md`'s per-claim evidence citations.
**Apply to:** the new note, the evidence transcripts, and the SUMMARY. Also covers D-02's caveat —
the instrument prints its realised window rather than claiming "the last 90 days" (Pitfall 3).

### Bold marks the load-bearing negative
**Source:** `CLAUDE.md:12` (`**no automated wiki guard exists now**`),
`999.9:…` (`**deletes**`), seed body.
**Apply to:** all prose artefacts. The caveat block's "**necessary condition, never a sufficient one**"
and "the pre-2.0.7 population is **outside the instrument's reach entirely**" are the instances here.

### No GSD process commentary in `tools/`
**Source:** `CLAUDE.md:50-70` (scoped to `firestarter/` and `firestarter_app/`) + D-17.
**Apply to:** `tools/adoption/`. The SQL and the endpoint mechanics **may** be explained — that is what
`sync_to_subrepos.sh`'s 18-line header does. `# Phase 193`, `# GATE-01`, `# D-09` and any plan or
milestone citation may not appear. Rationale goes in `SUMMARY.md`.

---

## No Analog Found

| File | Role | Data Flow | Reason |
|------|------|-----------|--------|
| the `curl -G` / ClickHouse call inside `tools/adoption/*.sh` | network query | request-response | **Nothing in this repository makes an HTTP call.** `tools/catalog/` is a local codegen/copy tool; the meta repo has no `.github/workflows/` and no other executable. The script's *shell conventions* come from `sync_to_subrepos.sh`; its *query and error handling* have no in-repo precedent and must be taken verbatim from `193-RESEARCH.md` §Code Examples 2-3 and §Common Pitfalls 1-3, which were executed. Do not invent a pattern here. |

Everything else has a real, tracked analog in this repository.

## Metadata

**Analog search scope:** `/workspaces/tools/`, `/workspaces/CLAUDE.md`, `/workspaces/.planning/notes/`,
`/workspaces/.planning/seeds/`, `/workspaces/.planning/phases/{189,190,191,192}-*/evidence/`
**Files scanned:** 7 read in full or in targeted ranges; 3 directory listings
**Tracked-source gate:** all 7 analog paths confirmed via `git ls-files` — no gitignored mirrors
**Pattern extraction date:** 2026-09-14
