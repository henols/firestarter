# Phase 196: Adoption Instrument Disposition - Research

**Researched:** 2026-09-17
**Domain:** Meta-repo document consistency — artifact deletion, retirement-record precedent, and one grep gate proving a doc sweep landed
**Confidence:** HIGH (every claim below is a command run this session or a file read this session, with line ranges)

## Summary

The disposition is settled (RETIRE, delete the script) and this research does not touch it. Research
output is mechanical: the true live reference set, an authored-and-proven-RED gate, the precedent
skeleton for the retirement note, and the execution mechanics.

Three CONTEXT.md measurements are **falsified by re-measurement this session**, and each one, left
uncorrected, makes INSTR-02 fail or makes the gate unable to ever go green:

1. **D-07 is wrong.** It claims the only surviving live ClickHouse references after the deletion are
   `STATE.md:3047` and `ROADMAP.md:623`. There are also 8 in this phase's own `196-CONTEXT.md` and 7
   in `196-DISCUSSION-LOG.md` — both tracked, both live, neither in any bucket D-08/D-09/D-10 names.
2. **D-11's premise is wrong.** The graph rebuild does *not* clear `GRAPH_REPORT.md`. Its surviving
   ClickHouse node is sourced from a **D-09-frozen archived file**, so the rebuild re-emits it.
3. **D-12/D-13's three exclusion classes are insufficient.** D-14 freezes two seed lines that name the
   script by path. A path-term gate over the seed can never go green. The gate needs a fourth
   exclusion class, recorded with D-14 as its reason.

**Primary recommendation:** plan the sweep against the 4-site SWEEP list in R1 (not CONTEXT.md's
7-site list — three of those are not gate-visible and one is frozen), and adopt the gate in R2
verbatim: it is **proven RED at 11 residual references** against the pre-sweep tree, and its
exclusion set has five auditable classes, not three.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Artifact deletion (`tools/adoption/`) | Meta-repo working tree / git | — | Neither sub-repo, no CI, no consumer — verified zero references repo-wide |
| Retirement reason record | `.planning/notes/` (prose) | — | D-01; five prior notes establish the venue and shape |
| Live-document consistency (INSTR-02) | `.planning/` + root `CLAUDE.md` | — | 4 tracked files carry gate-visible references |
| Proof that the sweep landed | Shell gate over `git ls-files` | — | D-12: one expression, tracked files, historical paths excluded |
| Generated-artifact consistency | graphify rebuild (`graphify update .`) | gate exclusion | D-11 rebuild removes the file-node; the community node is archive-sourced and needs an exclusion |

## R1 — The true live reference set, measured

**Method** [VERIFIED: command run this session]

```bash
cd /workspaces
git ls-files -z | xargs -0 /usr/bin/grep -nIE -e '<term>'
```
5207 tracked files in the meta repo. `/usr/bin/grep` by absolute path throughout — the devcontainer
`grep` is `ugrep` and honours `.gitignore`.

### Bucket counts (narrow identifier term set)

Term set measured: `tools/adoption|pypi_version_share|[Cc]lick[Hh]ouse|splitByChar|toUInt32OrZero|pypi_raw|pypistats`

| Bucket | Files | Hits | Notes |
|---|---|---|---|
| **SWEEP** (live, must change) | 4 | 4 | see table below |
| **THE ARTIFACT** (deleted whole) | 1 | 7 | `tools/adoption/pypi_version_share.sh` |
| **FROZEN by D-14** (seed) | 1 | 2 | `.planning/seeds/SEED-claim-firestarter-slug.md:7,88` |
| **HISTORICAL — D-08** (`STATE.md`) | 1 | 4 | not edited |
| **HISTORICAL — D-09** (193 archive) | 15 | 178 | not edited |
| **HISTORICAL — archived v1.38, outside D-09** | 2 | 2 | **not named by any decision** — see below |
| **HISTORICAL — D-10** (closed v1.38 ROADMAP section) | 1 | 1 | `ROADMAP.md:623` |
| **GENERATED** (`.planning/graphs/`) | 1 | 2 | `GRAPH_REPORT.md:2799,12253` — partially regenerable, see R2.4 |
| **THIS PHASE'S OWN RECORDS** | 2 | 23 | `196-CONTEXT.md` (15), `196-DISCUSSION-LOG.md` (8) — **not named by any decision** |
| **UNRELATED FALSE POSITIVE** | 1 | 1 | `.claude/gsd-core/references/ai-frameworks.md:110` |
| **UNTRACKED / out of reach** | 1 | 2 | `.planning/graphs/graph.html` — untracked *and unignored* |

### The SWEEP list — 4 sites, with line numbers

| # | File:line | Current text (verbatim) | Why it must change |
|---|---|---|---|
| S1 | `CLAUDE.md:19` | ``- `tools/adoption/` — the PyPI per-version download-share instrument.`` | D-03. The two-occupant sentence at `:16` (``\`tools/\` holds two directories:``) is falsified with it |
| S2 | `.planning/PROJECT.md:68` | ``The third item is bookkeeping the v1.38 close left behind: `tools/adoption/pypi_version_share.sh` `` | Describes the instrument as still running |
| S3 | `.planning/REQUIREMENTS.md:76` | ``- [ ] **INSTR-01**: `tools/adoption/pypi_version_share.sh` either measures a question with a named`` (continues `:77` ``consumer, or is removed. Either way the disposition is recorded with its reason.``) | D-10. The "either … or" is now a closed choice |
| S4 | `.planning/ROADMAP.md:321` | ``1. `tools/adoption/pypi_version_share.sh` is either re-pointed at a question with a named consumer, or`` (continues `:322-323`) | D-10. Phase 196's own criterion 1 |

[VERIFIED: /workspaces/CLAUDE.md:16-19, /workspaces/.planning/PROJECT.md:68, /workspaces/.planning/REQUIREMENTS.md:74-79, /workspaces/.planning/ROADMAP.md:312-332 — all read this session]

**CONTEXT.md's `<code_context>` list is longer than this and is wrong in three places:**
- `PROJECT.md:144` (the "D-1 row") — **zero hits** at or near line 144 for any term. Not a site.
- `SEED:7` and `SEED:88` — real, but **frozen by D-14**, so not sweep sites. They are gate sites.
- `REQUIREMENTS.md:76` → correct. `ROADMAP.md:321` → correct. `CLAUDE.md:19` → correct.

Also in scope but not a *term* hit: `.planning/REQUIREMENTS.md:74`, the section heading
``### INSTR — the adoption instrument answers a live question, or is retired (v1.38 carry-over)``
[VERIFIED: /workspaces/.planning/REQUIREMENTS.md:74] — it states the same live open choice. The
planner should decide whether it is reworded; it is **not** matched by the recommended gate term set,
so leaving it will not turn the gate red.

Traceability rows to flip: `.planning/REQUIREMENTS.md:101` ``| INSTR-01 | Phase 196 | Pending |``
and `:102` ``| INSTR-02 | Phase 196 | Pending |`` [VERIFIED: /workspaces/.planning/REQUIREMENTS.md:101-102].

### Directories CONTEXT.md does not cover — all verified

| Location | Result |
|---|---|
| `.planning/notes/` (40 files, incl. `999.9-repo-rename-impact-analysis.md`, `disposable-artifact-inventory.md`) | **ZERO** |
| `.planning/seeds/` (16 files) | 2 hits, both in `SEED-claim-firestarter-slug.md` — every other seed zero |
| `.planning/todos/` (71 files) | **ZERO** |
| `.planning/research/` (1), `.planning/codebase/` (7), `.planning/v1.39/` (4) | **ZERO** each |
| `.planning/quick/` (57), `.planning/quick-batches/` (2), `.planning/reports/` (1), `.planning/debug/` (20) | **ZERO** each |
| `.planning/MILESTONES.md`, `RETROSPECTIVE.md`, `state.json`, `config.json`, `estimation-calibration.json` | **ZERO** |
| `.planning/intel/` | directory absent (`intel.enabled: false` in config) |
| Repo root: `README.md`, `VALIDATED-EPROMS.md`, `.gitmodules`, `.gitignore` | **ZERO** |
| `.github/` | **ZERO**. Contains only `CONTRIBUTING.md` + `ISSUE_TEMPLATE/`. **No `.github/workflows/` at all** |
| `tools/catalog/` | **ZERO** (4 files: `codegen.py`, `messages.toml`, `sync_to_subrepos.sh`, a `.pyc`) |
| `.claude/` | 1 hit, unrelated: `ai-frameworks.md:110` matches `BigQuery` in "Google Search / BigQuery" — an installer-owned GSD reference file |
| `firestarter_fw` (245 tracked files) | **ZERO** matching files |
| `firestarter_app` (248 tracked files) | **ZERO** matching files |
| Untracked: `anything.txt`, `setup-claude-pr-policy.sh`, `firestarter.wiki/`, `tmp/` | **ZERO** |
| Untracked: `.planning/graphs/graph.html` | **2 hits** — untracked *and not gitignored* |

### Unbucketed hits — the two classes no decision names

These are the INSTR-02 failure candidates. Both are handled by the R2 gate's exclusion set, but the
plan should name them so a verifier does not read them as misses.

**Class A — archived v1.38 material outside the 193 directory.** D-09 excludes only
`.planning/milestones/v1.38-phases/193-the-deferred-claim-made-measurable/`. These sit elsewhere in
the same archive:
- `.planning/milestones/v1.38-research/questions.md:19,21` — ``What does \`pypistats\` (or the PyPI BigQuery dataset) expose for per-version download`` / ``available without BigQuery credentials?``
- `.planning/milestones/v1.38-phases/191-the-branch-that-reaches-users/COVERAGE.md:70` — ``| Download-statistics APIs (BigQuery / pypistats) | OPT-OUT | …``
- Phrase-level only (no narrow-term hit): `191-CONTEXT.md:25`, `192-CONTEXT.md:25` — both say "the adoption instrument".

[VERIFIED: grep over tracked files, this session]

*Recommendation:* extend the exclusion from the 193 directory to **`.planning/milestones/` wholesale**.
Every archived milestone is historical-by-intent under the same standing rule D-09 rests on, so this
is a broadening of D-09's stated reason, not a new policy.

**Class B — this phase's own records.** `196-CONTEXT.md` (15 hits) and `196-DISCUSSION-LOG.md` (8
hits) are tracked, live, in `.planning/phases/`, and quote the operator's words about ClickHouse
deliberately. `196-PLAN.md`, `196-SUMMARY.md`, `196-VERIFICATION.md` and this `196-RESEARCH.md` will
add more. **Every one of them is required to contain the terms.**

*Recommendation:* exclude `.planning/phases/196-adoption-instrument-disposition/` from the gate
pathspec, with the reason recorded: a phase's own decision record is the evidence *for* the sweep, not
a subject of it. Without this, the gate is unable to go green at any point in the phase's life.

## R2 — The INSTR-02 gate, authored and proven RED

### R2.1 The expression

[VERIFIED: run this session against the pre-sweep tree at HEAD `5d188fc2`, branch `v1.39-protocol-0x05-write-correctness`]

```bash
cd /workspaces
GATE_TERMS='tools/adoption|pypi_version_share|[Cc]lick[Hh]ouse|splitByChar|toUInt32OrZero|pypi_raw|pypistats'
RM=.planning/ROADMAP.md
V138="$(/usr/bin/grep -nE '^## v1\.38 ' "$RM" | head -1 | cut -d: -f1)"
[ -n "$V138" ] || { echo "INSTR02_GATE: ABORT — v1.38 ROADMAP boundary not found"; exit 3; }
HITS="$(git ls-files -z -- \
      ':!:.planning/STATE.md' \
      ':!:.planning/milestones' \
      ':!:.planning/phases/196-adoption-instrument-disposition' \
      ':!:.planning/seeds/SEED-claim-firestarter-slug.md' \
      ':!:.planning/graphs' \
      ':!:.claude' \
  | xargs -0 /usr/bin/grep -nIE -d skip -e "$GATE_TERMS" \
  | awk -F: -v f="$RM" -v n="$V138" '!($1 == f && $2 + 0 >= n)')"
if [ -n "$HITS" ]; then
  printf '%s\n' "$HITS"
  printf 'INSTR02_GATE: RED (%s residual reference(s)) boundary=%s\n' "$(printf '%s\n' "$HITS" | wc -l)" "$V138"
  exit 1
else
  printf 'INSTR02_GATE: GREEN — zero residual references (boundary=%s)\n' "$V138"
fi
```

### R2.2 Why each mechanic is what it is

| Choice | Reason |
|---|---|
| `/usr/bin/grep` absolute | devcontainer `grep` is `ugrep`; it honours `.gitignore` and silently under-scans |
| `git ls-files -z … \| xargs -0` | explicit, auditable pathspec over **tracked** files only; cannot fail open by scanning nothing (5207 files enumerated) and is NUL-safe |
| `-E` with a single `-e "$GATE_TERMS"` | `-e` is used even though the pattern starts with `t`: it makes a future term that starts with `-` safe. A dash-leading pattern without `-e` exits 2 and the gate fails open |
| `-I` | skips binary files; prevents a stray binary from producing unreadable output |
| `-d skip` | without it, the two submodule gitlinks (`firestarter_fw`, `firestarter_app`) emit `Is a directory` on stderr. Cosmetic, but a clean gate is an auditable gate |
| Capture into `$HITS`, test `-n` | **This is the fix for the whole exit-code family.** `xargs` returns 123 when any grep batch exits 1, and 5207 files span several batches, so the pipeline's exit code is meaningless. `grep -c` is worse: it prints `0` and exits 1 per file. Emptiness of the captured text is the only honest signal |
| single pipeline, no `;`-chains, no OR-grep | both have failed open in this repo |
| `awk` boundary filter on the *output* | keeps it to **one** grep invocation and one term set, while still excluding D-10's historical ROADMAP section by line. A whole-file `':!:.planning/ROADMAP.md'` exclusion would blind the gate to S4 (`:321`), which is the point of the sweep |
| boundary by anchor (`^## v1\.38 `), not literal `623` | line numbers drift; the section header does not. Measured this session: boundary = **line 333** |
| `[ -n "$V138" ] \|\| exit 3` precondition | **fail-closed guard.** With `V138` empty, `awk`'s test becomes `$2+0 >= 0` — true for every line — and *all* ROADMAP hits would be silently dropped. That is a fail-open, so the gate aborts loudly instead |
| `INSTR02_GATE: GREEN` echoed token | success is **positively observable**, not inferred from absence of output |

### R2.3 The RED proof (D-13)

Run against the pre-sweep tree, this session:

```
INSTR02_GATE: RED (11 residual reference(s)) boundary=333
```

The 11, by file:

| File:line | Shown |
|---|---|
| `.planning/PROJECT.md:68` | verbatim (S2 above) |
| `.planning/REQUIREMENTS.md:76` | verbatim (S3 above) |
| `.planning/ROADMAP.md:321` | verbatim (S4 above) |
| `CLAUDE.md:19` | verbatim (S1 above) |
| `tools/adoption/pypi_version_share.sh:11,13,20,29,37,54,63` | 7 hits, **text deliberately not transcribed here** — these are the endpoint, table name and version-array idiom D-06 deletes |

**RED count: 11, across 4 files.** Predicted post-sweep: **0** — 7 vanish with the file deletion, 4
with the four doc edits. The gate has teeth: it names four distinct live documents that the sweep must
touch, so a green reading cannot be confused with an expression that matches nothing.

Two additional falsification properties worth recording in the plan: the gate goes RED if the script
is deleted but any of the 4 docs is missed (4, 3, 2 or 1 residual), and it **aborts with exit 3**
rather than passing if the ROADMAP boundary anchor is ever renamed.

### R2.4 `GRAPH_REPORT.md` — D-11's premise does not hold

D-11 reasons: rebuild the graph in-phase so `GRAPH_REPORT.md` regenerates clean and no
generated-file exclusion is needed. **Measured, this is false for one of its two hits.**

| Hit | Source | Survives the rebuild? |
|---|---|---|
| `GRAPH_REPORT.md:2799` — ``- pypi_version_share.sh`` | a **file node** for the script itself | **No** — goes when the file goes |
| `GRAPH_REPORT.md:12253` — community 3827, node ``ClickHouse HTTP interface — as consumed by \`tools/adoption/pypi_version_share.sh\`` | **`.planning/milestones/v1.38-phases/193-the-deferred-claim-made-measurable/COVERAGE.md:23`**, whose heading is that exact string | **Yes** — the source file is D-09-frozen, so the rebuild re-encodes it |

[VERIFIED: `/usr/bin/grep -rn "ClickHouse HTTP interface" .planning/` returned the graph artifacts plus
exactly one source — `…/193-the-deferred-claim-made-measurable/COVERAGE.md:23`, run this session]

**Recommendation:** keep the D-11 rebuild — it is still correct and still removes hit 1, and it honours
the project's "generated artifacts are regenerated, never hand-edited" rule — but **exclude
`.planning/graphs/` from the gate pathspec**, recorded as a fifth class: *generated distillation of
the whole tree, including the frozen archive*. Without the exclusion the gate is permanently RED on a
file no one is allowed to fix, because fixing it means editing the D-09 archive.

**Ordering, confirmed:** because the rebuild reads the working tree (see R5.2), the sweep edits must be
**saved** before the rebuild runs. D-11's "a rebuild run before the sweep re-encodes the stale text" is
correct. If the rebuild is skipped entirely: the gate still passes (`.planning/graphs/` is excluded),
but `GRAPH_REPORT.md` keeps its stale `pypi_version_share.sh` file-node and the working tree keeps two
dirty tracked files — so skipping it is a recorded-consistency miss, not a gate failure. Say so in the
acceptance criteria rather than relying on the gate to catch it.

### R2.5 The gate's honest blind spots

D-12 was chosen against a stated fail-open concern. What this gate does **not** catch:

1. **Semantics.** It matches identifiers, not meaning. A live document could say "the instrument that
   gated the slug claim is still running" without naming the path, and pass. INSTR-02's actual property
   — "no document describes the instrument as gating a claim that has already fired" — is not
   mechanically checkable; the gate is a proxy for it.
2. **Six exclusion classes are six holes.** Anything the plan puts inside `.planning/STATE.md`,
   `.planning/milestones/`, the 196 phase directory, the seed, `.planning/graphs/` or `.claude/` is
   invisible to it. The seed exclusion is the sharpest: D-14 requires an added annotation line there,
   and the gate cannot verify it exists.
3. **Untracked files.** `git ls-files` is tracked-only by design. `.planning/graphs/graph.html` is
   untracked, unignored, and carries 2 hits.
4. **Phrase-level residue.** "adoption instrument", "download share", "at-risk", "fixed share" are
   deliberately *not* in the term set — they produce unrelated hits across five archived milestones
   (`v1.22`, `v1.35`, `v1.36`, `v1.38`) and would make the gate permanently RED for reasons that have
   nothing to do with this phase. `REQUIREMENTS.md:74`'s heading is the one live phrase-level site, and
   it is listed in R1 so the planner can handle it by hand.
5. **`BigQuery` is not in the term set** on purpose: it hits the installer-owned
   `.claude/gsd-core/references/ai-frameworks.md:110`. Either the term or `.claude/` must go; dropping
   the term is cheaper, since `BigQuery` appears in the script only as a named fallback and the script
   is deleted whole.

## R3 — The artifact, and what D-06 must forbid

### What it measured, and what it output

[VERIFIED: /workspaces/tools/adoption/pypi_version_share.sh — 125 lines, 4788 bytes, read this session]

- **What it measured:** for the `firestarter` PyPI package, the split between downloads of a fixed
  stable version (`>= 2.0.9`) and downloads of the single at-risk stable version (`2.0.7` exactly),
  restricted to the `pip` and `uv` installers over a rolling 90-day window on the stable channel.
- **What it output:** eight stdout lines — the window bounds, the two download counts, the fixed-share
  percentage, the threshold it was judged against, a one-line `TRIGGER: MET` / `TRIGGER: NOT MET`
  verdict — followed unconditionally by a six-bullet `WHAT THIS DOES NOT MEASURE` caveat block.

It takes no arguments, reads no other file, and writes nothing to disk (its own header says so at
`:23`). Requirements: `bash`, `curl`. Three error paths exit 1 and one exits 2.

### Method residue — D-06's list is incomplete

D-06 forbids the note from carrying: the SQL, the endpoint URL, the `splitByChar`/`toUInt32OrZero`
version-array idiom, and the fallback list (BigQuery, `pypi_raw`). All four exist in the script.
**Four further pieces of method residue exist that D-06 does not name**, and the planner should extend
the forbidden list to cover them explicitly, because "no SQL" does not obviously cover a bare
identifier:

| Residue | Where | Why it is method, not reason |
|---|---|---|
| The dataset **table name** — a long dotted identifier naming the per-day, per-version, per-installer aggregate | script header and query | Names the exact source; a reader could re-derive the query from it. Deliberately not transcribed here |
| The **anonymous auth mechanism** — a `user=` query parameter with a fixed public value | the curl invocation | This is *how* it queried without credentials |
| The **output-format directive** appended to the query | end of the query heredoc | Pure transport detail |
| The **filter predicates** — the installer allow-list, the 90-day window expression, and the prerelease-exclusion regex | the query's `WHERE` clause | These are the measurement's definition, i.e. the method |

Also present and *not* method: the `WHAT THIS DOES NOT MEASURE` caveat block (`:113-125`). It contains
no query, no host and no idiom — it is the epistemics of the reading. D-06 permits the note "one plain
sentence" on what the instrument measured and is silent on the caveat. **Planner's call**, flagged
rather than decided: the strict reading of D-06 keeps the note to one sentence, which loses the caveat.
The block is preserved regardless in the D-09 archive at
`…/193-the-deferred-claim-made-measurable/evidence/193-gate-01-instrument-run.txt`.

**Nothing from the script is transcribed into this file.** Doing so would recreate exactly what D-06
deletes, inside a document this phase commits.

### The precedent note skeleton

`.planning/notes/catalog-sync-check-retirement.md` — 230 lines, 15056 bytes
[VERIFIED: read in full this session]

| Element | Content |
|---|---|
| Frontmatter, keys **in this order** | `title`, `date`, `context` |
| `title` shape | `<Thing> retirement — <why it failed> and what is lost with it` |
| `context` shape | `v1.37 Phase 185, CLAIM-08 (D-01, D-02, D-03) — read from the live workflow file before deletion` — milestone, phase, requirement, decision ids, and *how the facts were obtained* |
| `# <Title> (CLAIM-08)` | H1 restates the title, tagged with the requirement id |
| `## VERDICT` (lines 9–27, ~19 lines) | Two paragraphs. Para 1: the decision **in bold in its first sentence**, naming that it was *"on the operator's own decision, taken against the orchestrator's recommendation to …"*, then the measured record (8 runs, 6 failures, 2 successes), then the operator's grounds **quoted verbatim in their own words**, then one sentence stating why it is recorded here. Para 2: a checklist sentence naming everything the note is required to carry |
| `## 1. The cause` (29–58) | ~30 lines, one fenced verbatim quote of the deleted artifact, one measured exit code, one named run id |
| `## 2. Why the <date> fix did not fix it` (60–94) | ~35 lines, includes an 8-row evidence table |
| `## 3. That the workflow's own comment is now false` (96–131) | ~36 lines, quotes the now-false text in a fence, then **"Correction, in place"** in bold |
| `## 4. That a naive <alternative> would not have worked either` (133–162) | ~30 lines, a 4-row measured table, plus a parenthetical disambiguating two similar figure sets |
| `## 5. The residual gap, named explicitly` (164–211) | ~48 lines. What is no longer proved, in bold. A 4-row surviving-gates table. The concrete failure the gap admits. Why it is accepted. Closes: *"Naming a gap and filing a gap are different acts; this note performs only the first."* |
| `## Two questions a reader will ask next` (213–230) | ~18 lines, two bolded questions each answered `No.` then evidence |

**How the VERDICT names the operator's own decision** (the D-04 model): decision in bold → *"on the
operator's own decision, taken against the orchestrator's recommendation to <the declined
alternative>"* → measured figures → operator's grounds quoted verbatim → *"That is recorded here so a
later reader does not read the deletion as an oversight or as evidence the property stopped
mattering."* D-04 and D-05 map onto this exactly.

### Where the other four notes diverge

[VERIFIED: frontmatter and headings read this session for all five]

| Note | Lines | Divergence from the analogue |
|---|---|---|
| `host-tools-retirement.md` | 269 | Same 3-key frontmatter; `context` wraps to a second line. Title states the outcome numerically (*"twenty-six scripts to six, on the operator's own decision, no successor"*). H1 tagged with the **phase** (`(Phase 188)`) rather than a requirement id. Has `## 2. The eight disclosed costs, each stated as a loss` — the closest structural match to D-06's "what is lost". Final section is explicitly *"stated in the form the analog note uses"* |
| `dispatch-invariant-retirement-verdict.md` | 351 | **`## THE VERDICT` in caps**, followed by all-caps section names (`THE GROUNDS`, `THE EVIDENCE CHAIN`, `WHAT THE DELETED FIXTURES PROVED`). Title carries the outcome in caps: *"RETIRED OUTRIGHT, no successor"*. Ends with `## Backlog items this verdict generates` — the analogue deliberately files nothing |
| `test-suite-source-introspection-removal.md` | 87 | Shortest. 3-key frontmatter, but **no H1 at all** — starts at `## The ruling`. Sections are terse and unnumbered (`## What went`, `## What is now unguarded — stated, not hidden`). Ends `## Standing rule this produces` |
| `sdp-surface-retirement-and-behavioral-proof.md` | 182 | **No YAML frontmatter.** H1 then bold `**Date:** / **Context:** / **Status:**` lines. A design/decision note, not a post-deletion record — the weakest analogue for this phase |

**Convention (all five, or four of five):** a `title`/`date`/`context` frontmatter block (4 of 5); a
VERDICT-or-ruling section first (5 of 5); the operator's grounds quoted verbatim (5 of 5); a
what-is-lost / what-is-now-unguarded section stated plainly and not hidden (5 of 5); numbered `## N.`
sections (3 of 5).

**One note's choice, not convention:** all-caps headings; a "questions a reader will ask next"
section; filing backlog items; the H1 tag being a requirement id vs a phase number.

### `CLAUDE.md` § Repository Structure — the two paragraphs D-03 mirrors and falsifies

[VERIFIED: /workspaces/CLAUDE.md:14-19, read this session]

The `tools/wiki/` retirement paragraph, verbatim (line 14):

> The `tools/wiki/` checkers validated a clone of that wiki. Commit `5426d7ef` retired them on 2026-09-02. A later commit deleted `tools/wiki/` on 2026-09-08. Its last occupant, `MIGRATION-TABLE.md`, moved to `.planning/milestones/v1.35-MIGRATION-TABLE.md` as a record of the completed migration. **No automated wiki guard exists now.**

The two-occupant sentence the deletion falsifies, verbatim (lines 16–19):

> `tools/` holds two directories:
>
> - `tools/catalog/` — messages codegen and sub-repo sync tooling.
> - `tools/adoption/` — the PyPI per-version download-share instrument.

Note the shape: a count sentence plus a bullet per occupant. Deleting one bullet leaves "holds two
directories" false, so the count sentence changes in the same edit — the established pattern
CONTEXT.md names, which Phase 193 hit in reverse.

## R4 — The self-citation snag: cite by date

**Recommendation: cite by date, in one commit. Do not sequence a second commit, and do not use a sha.**

### What the repository actually does

[VERIFIED: `git log -L 14,14:CLAUDE.md` and `git log -L 21,25:CLAUDE.md`, run this session]

1. **The `tools/wiki/` paragraph is not a self-citation at all.** `5426d7ef` is an independent, earlier
   commit — ``5426d7ef chore: retire wiki-check.yml and the tools/wiki checkers``. The paragraph naming
   it was written far later, by ``95738516 docs(260917-co5): correct tools/ inventory, add the branching
   rule and close the comment-rule loophole`` (and in an earlier prose form by `d9f5434b` and
   `c1ad0e3e`). The sha was citable because the commit already existed.
2. **The *deleting* act in that same sentence is cited by date with no sha:** *"A later commit deleted
   `tools/wiki/` on 2026-09-08."* That is precisely this phase's situation, and the precedent already
   chose the date route for it.
3. **A second, same-file precedent, three days old.** The source-comment paragraph
   [VERIFIED: /workspaces/CLAUDE.md:21-25] reads: *"Both scripts and all three CI steps were removed by
   operator decision on **2026-09-17**."* — a **date** for the act the commit itself performs — while
   shas appear only for *restore points in other repositories* (`876a223`, `c77ff2e`), which existed
   independently. Added by ``509106b1 docs: record that the planning-citation gates were dropped``.

### Why the date route wins

- **Cheaper:** one commit instead of two. The two-commit wiki sequence was an artifact of two genuinely
  separate acts eleven days apart (retire, then delete), not a chosen citation strategy.
- **Survives rebase:** a short sha does not. This branch has already absorbed a merge from `origin/beta`
  (`1c3afec9`), and `/gsd-ship` may squash or rebase — any of which invalidates a short sha written into
  tracked prose, silently. A date cannot be invalidated.
- **Consistent with both in-file precedents**, one of which is three days old.
- **The stable pointer already exists:** D-03 requires the paragraph to point at
  `.planning/notes/adoption-instrument-retirement.md`, which is a path, not a sha, and is the durable
  route to the full reason. Recovery of the method, per D-06, is via the deleting commit — findable
  from the path and the date by `git log --diff-filter=D -- tools/adoption/`, which needs no sha.

Do not write a placeholder sha, and do not write "commit TBD".

## R5 — Execution mechanics

### R5.1 Working-tree state

[VERIFIED: `git status --porcelain`, run this session]

```
 M .devcontainer/devcontainer.json
 M .gitignore
 M .planning/graphs/.last-build-status.json
 M .planning/graphs/GRAPH_REPORT.md
 M .vscode/c_cpp_properties.json
 M .vscode/extensions.json
 M .vscode/launch.json
 M firestarter_app
?? .planning/graphs/graph.html
?? anything.txt
?? firestarter.wiki/
?? setup-claude-pr-policy.sh
?? tmp/
```

**The baseline is not clean. Eight tracked files are dirty and five paths are untracked.** Acceptance
criteria must not assert a clean tree, and no task may use `git add -A` or `git commit -a`.

| Path | Status | In this phase's way? |
|---|---|---|
| `.planning/graphs/GRAPH_REPORT.md` | dirty, +3686/−14284 | **Yes** — D-11 rebuilds and commits it. Already dirty as D-11 says; the diff is pre-existing, not this phase's |
| `.planning/graphs/.last-build-status.json` | dirty, 3/3 | **Yes** — same; last build was `2026-09-17T12:28:29Z` at `head_at_build: 1c3afec9`, two commits behind HEAD |
| `.planning/graphs/graph.html` | untracked, **and not gitignored** | **Yes — active hazard.** Carries 2 term hits, and the rebuild *rewrites* it (see R5.2). A `git add -A` would track a 3 MB file and turn the gate RED on a generated artifact. Either add it to `.gitignore` or commit only by explicit path |
| `.gitignore` | dirty | No — the uncommitted diff adds `.claude/skills/asd-ste100`, unrelated. Note the collision risk if the plan also edits `.gitignore` for `graph.html` |
| `firestarter_app` (gitlink) | dirty | **No — leave it.** No sub-repo work in this phase; do not advance the gitlink |
| `.devcontainer/devcontainer.json`, 3 × `.vscode/*` | dirty | No — pre-existing local environment edits |
| `anything.txt`, `setup-claude-pr-policy.sh`, `firestarter.wiki/`, `tmp/` | untracked | No — zero term hits each. Only a hazard if a task stages broadly |

### R5.2 The graph rebuild

[VERIFIED: /workspaces/.claude/hooks/lib/gsd-graphify-rebuild.sh:15-36 and
/workspaces/.claude/commands/gsd-graphify.md:160-168, read this session]

**Command** — the documented chain, run in the **foreground** from `/workspaces`:

```bash
graphify update . \
  && cp graphify-out/graph.json .planning/graphs/graph.json \
  && { [ -f graphify-out/graph.html ] && cp graphify-out/graph.html .planning/graphs/graph.html || true; } \
  && cp graphify-out/GRAPH_REPORT.md .planning/graphs/GRAPH_REPORT.md \
  && gsd_run graphify build snapshot \
  && gsd_run graphify status
```

`/gsd-graphify build` wraps this. Its own anti-patterns section says: **do not spawn an agent** for it
and **do not run it in the background** — sub-agent isolation has previously truncated builds
mid-write.

**Does it read the working tree or git?** — **The working tree.** `graphify update .` is given the
filesystem path `.`; the `HEAD_SHA` in `.last-build-status.json` is passed in by the caller as metadata
only and is never used to select content [VERIFIED: gsd-graphify-rebuild.sh:27 runs
`"$GRAPHIFY_BIN" update .`, and lines 48-66 write `head_at_build` from the `$3` argument]. **So the
sweep edits need only be saved, not committed, before the rebuild runs.** D-11's ordering constraint
holds and is satisfiable inside one plan.

**Does it need a clean tree?** No. There is no cleanliness check anywhere in the rebuild path. Its only
concurrency control is `.planning/graphs/.rebuild.lock`.

**Duration:** the last real build took **212,316 ms ≈ 3.5 minutes**
[VERIFIED: /workspaces/.planning/graphs/.last-build-status.json — `"duration_ms": 212316`]. The command
doc's *"typical builds complete in 15-60 seconds"* is wrong for this repo. Use a `timeout` of
`600000` ms as the doc instructs.

**What it writes, tracked vs ignored** [VERIFIED: `git ls-files .planning/graphs`, `ls -la .planning/graphs/`, `/usr/bin/grep -n graph .gitignore:50-56`]:

| File | Size now | Tracked? | Ignored? |
|---|---|---|---|
| `.planning/graphs/GRAPH_REPORT.md` | 1.1 MB | **tracked** | no |
| `.planning/graphs/.last-build-status.json` | 187 B | **tracked** | no |
| `.planning/graphs/graph.json` | **105 MB** | no | **yes** (`.gitignore:54`) |
| `.planning/graphs/.last-build-snapshot.json` | **105 MB** | no | **yes** (`.gitignore:55`) |
| `.planning/graphs/graph.html` | 3.0 MB | no | **NO — unignored** |
| `graphify-out/` (repo root) | — | no | **yes** (`.gitignore:56`) |

D-11 is right that exactly two tracked files regenerate. **D-11 is wrong on two details:** `graph.json`
is **105 MB, not ~23 MB**, and D-11 does not mention `graph.html`, which the rebuild also writes and
which is neither tracked nor ignored.

**No spontaneous rebuild will race the plan.** `graphify.auto_update` is `true` in
`.planning/config.json:62` and the `PostToolUse` hook is registered at
`.claude/settings.local.json:111`, but the hook exits 0 unless the current branch equals the repository
default branch [VERIFIED: /workspaces/.claude/hooks/gsd-graphify-update.sh:105-106 —
`[ "$CURRENT_BRANCH" = "$DEFAULT_BRANCH" ] || exit 0`]. HEAD is on
`v1.39-protocol-0x05-write-correctness`, so the hook is inert for the whole phase. The D-11 rebuild is
the only rebuild.

### R5.3 The requirements / traceability flip

| Target | Current text (verbatim) |
|---|---|
| `.planning/REQUIREMENTS.md:76-77` | ``- [ ] **INSTR-01**: `tools/adoption/pypi_version_share.sh` either measures a question with a named`` / ``      consumer, or is removed. Either way the disposition is recorded with its reason.`` |
| `.planning/REQUIREMENTS.md:78-79` | ``- [ ] **INSTR-02**: No document describes the instrument as gating a claim that has already fired. The`` / ``      seed, `CLAUDE.md` and any note pointing at it agree with the chosen disposition.`` |
| `.planning/REQUIREMENTS.md:101` | ``\| INSTR-01 \| Phase 196 \| Pending \|`` |
| `.planning/REQUIREMENTS.md:102` | ``\| INSTR-02 \| Phase 196 \| Pending \|`` |
| `.planning/REQUIREMENTS.md:74` | ``### INSTR — the adoption instrument answers a live question, or is retired (v1.38 carry-over)`` |

[VERIFIED: /workspaces/.planning/REQUIREMENTS.md:74-79 and :101-102, read this session]

**Edit these by hand. Do not use the GSD `requirements` or `roadmap` verbs.** Two documented hazards:
the `requirements`/`roadmap` verbs **reformat the whole file**, and `roadmap.update-plan-progress`
**overwrites this repo's ROADMAP phase block positionally**, which destroys the phase name and the
requirement-ID line.

**Shape check on the positional hazard** [VERIFIED: /workspaces/.planning/ROADMAP.md:173-207, 312-332,
and `/usr/bin/grep -nE '^\*\*Plans:\*\*|^\*\*Depends on:\*\*'`]: the v1.39 milestone section carries
**no Progress or dependency table at all** — it is free prose (goal, "Why now", two issue paragraphs,
an explicit "Ordering, stated because it inverts severity" paragraph, then a `**Requirements:**` line).
Per-phase metadata lives in bold inline lines: `**Requirements**:` at `:317`, `**Depends on:**` at
`:329`, `**Plans:** TBD` at `:331`. Sibling phases read `**Plans:** 7/7 plans complete` (`:236`) and
`**Plans:** 5/5 plans complete` (`:286`). A verb that assumes a fixed-offset table has no table to
anchor on here, which is exactly the shape in which a positional writer overwrites adjacent prose.
The hazard is structurally real. Hand-edit `:321-323` and `:331`; the orchestrator owns ROADMAP writes.

`.planning/STATE.md` is **not** edited (D-08), which also sidesteps this project's separate STATE.md
writer-corruption hazard — do not run `state.sync`.

### R5.4 Branch and commit reality

[VERIFIED: `git rev-parse --abbrev-ref HEAD`, `git log --oneline -15`, run this session]

- Branch: **`v1.39-protocol-0x05-write-correctness`** — the expected `v1.X-slug` milestone branch. HEAD
  `5d188fc2`. `git.base_branch` is `beta` [VERIFIED: /workspaces/.planning/config.json:54].
- Commit subject convention, from the last 15: Conventional Commits, lower-case, no trailing period.
  Scopes seen: `docs(state):`, `docs(196):`, `docs:`, `chore:`, `docs(quick-260917-8pj):`. The
  phase-scoped form `docs(196): <subject>` is the fit here.
- **The meta repository publishes nothing on push.** `.github/` contains only `CONTRIBUTING.md` and
  `ISSUE_TEMPLATE/` — **there is no `.github/workflows/` directory at all** [VERIFIED: `ls -la .github/`
  this session]. The publish-on-push consequence in `CLAUDE.md` § Milestone close applies to the two
  **sub-repos**, neither of which this phase touches. Separately: the meta repo must never publish a
  GitHub Release — bare milestone tags only.

### R5.5 Gate idioms in this repo that fail open

Inherit the corrected form into every acceptance criterion.

| Idiom | Failure | Fix |
|---|---|---|
| bare `grep` | devcontainer `grep` is `ugrep`; honours `.gitignore`, silently under-scans | `/usr/bin/grep` by absolute path |
| BRE `\+\+\+` | escaping differs between BRE and ERE; the pattern does not match what it looks like | `-E` with an explicitly-written pattern, or `-F` for a literal |
| `;`-chains (`cmd1; cmd2`) | only the last exit code survives; earlier failures vanish | one pipeline, or `&&`, or capture output and test it |
| OR-grep (`grep -e a -e b` used as a *pass* condition) | one term matching masks another term's absence | one gate, one expression, and a count |
| `grep -c` | prints `0` **and** exits 1 per non-matching file; a `-c` reading is not a pass signal | capture matches into a variable, test `-n`, count with `wc -l` |
| `--stat` / `--numstat` as a gate | prints nothing and exits 0 when there is no diff — identical to success | `git diff --exit-code`, or capture and test emptiness |
| `grep -qF` with a dash-leading pattern | exits **2** (usage error), which a `\|\|` guard reads as "not found" → fails open | `grep -qFe '<pattern>'` — always `-e` |
| exit code of a `git ls-files \| xargs grep` pipeline | `xargs` returns 123 when any batch's grep exits 1; with 5207 files there are several batches | capture into `$HITS`, test `-n "$HITS"` |
| absence of output as the success signal | indistinguishable from a gate that scanned nothing | echo a positive token (`INSTR02_GATE: GREEN`) |

## R6 — Scope fences

State these in the plan rather than rediscovering them.

1. **Nothing consumes the script — verified independently this session.** Zero references in
   `.github/` (which has no `workflows/` at all), zero in `tools/catalog/`, zero matching files in
   `firestarter_fw` (245 tracked) and zero in `firestarter_app` (248 tracked). Deletion breaks no
   automation. `tools/adoption/` disappears on its own; git does not track empty directories.
2. **No sub-repo work.** No gitlink advance, no submodule touched, no firmware, no host app, no
   protocol `0x05`, no bench, no board. `firestarter_app`'s gitlink is currently dirty — leave it.
3. **`.planning/STATE.md` is not edited** (D-08). This also sidesteps the STATE.md writer-corruption
   hazard; do not run `state.sync`.
4. **The 17 archived `193-*` files are not edited** (D-09) — and, per R2.4, one of them is the *source*
   of the surviving `GRAPH_REPORT.md` node. Editing it to make the gate green is forbidden; excluding
   `.planning/graphs/` is the sanctioned route.
5. **All of `.planning/milestones/` is historical-by-intent** — extend D-09's reason to cover the two
   Class-A hits outside the 193 directory (`v1.38-research/questions.md`,
   `191-…/COVERAGE.md`).
6. **The `reference_pypi_per_version_downloads_clickhouse` Claude memory lives outside this
   repository.** Out of scope for INSTR-02 (not a document in this repo) and out of the phase's reach.
   **Surfaced, not actioned:** the operator should be asked whether it goes too, since the instruction
   was "don't want clickhouse at all". Route it as a question at close, not as a task.
7. **A fired seed still matches `/gsd-new-milestone`'s `SEED-*.md` glob.** Deferred in CONTEXT.md;
   worth a todo, not a deliverable. D-15 keeps the file in place.
8. **No `## Validation Architecture` section.** `workflow.nyquist_validation` is `false`
   [VERIFIED: /workspaces/.planning/config.json:11].

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---|---|---|---|
| Proving the sweep landed | a per-site checklist as the *proof* | the single R2 gate | D-12's explicit choice. R1's site list is planning input, not the gate |
| Refreshing `GRAPH_REPORT.md` | hand-editing the generated file | `graphify update .` + the documented copy chain | project rule: generated artifacts are regenerated, never hand-edited |
| Enumerating the file set for the gate | a hardcoded path list | `git ls-files -z -- <pathspec>` | a hardcoded list silently misses a file added later; a pathspec cannot scan nothing without saying so |
| Excluding the closed v1.38 ROADMAP section | a literal line number (`623`) | the `^## v1\.38 ` anchor, computed into `$V138` | line numbers drift; the header does not. Measured 333 this session |
| Structuring the retirement note | a new format | `catalog-sync-check-retirement.md`'s skeleton (R3) | four of five prior notes already agree on it |
| Citing the deleting commit | a sha, or a two-commit sequence | the date | R4: two in-file precedents, and a sha does not survive a rebase |

## Common Pitfalls

### Pitfall 1: The gate can never go green as D-12/D-13 specify it
**What goes wrong:** the gate is built with only the three stated exclusion classes
(D-08/D-09/D-10) and stays permanently RED.
**Why:** D-14 freezes `SEED-…:7` and `:88`, which name the script by path; `GRAPH_REPORT.md:12253`
regenerates from a D-09-frozen file; and this phase's own `196-CONTEXT.md` / `196-DISCUSSION-LOG.md`
quote the terms deliberately. None is in a stated class.
**How to avoid:** use the R2 exclusion set — six classes, each with its reason recorded in the plan.
**Warning signs:** a gate that is RED on a file no decision permits editing.

### Pitfall 2: Broad phrase terms make the gate structurally RED
**What goes wrong:** the term set includes "adoption instrument", "at-risk", "fixed share",
"download share" or `BigQuery`, and matches unrelated archived phases and an installer-owned
`.claude/` file.
**Why:** measured this session — `at-risk` alone hits v1.22, v1.35 and v1.36 archives; `BigQuery` hits
`.claude/gsd-core/references/ai-frameworks.md:110`.
**How to avoid:** keep the narrow identifier set in R2.1. Handle `REQUIREMENTS.md:74`'s phrase by hand.

### Pitfall 3: The rebuild runs before the sweep, or is skipped
**What goes wrong:** `GRAPH_REPORT.md` is committed still naming the instrument.
**Why:** `graphify update .` reads the **working tree**, so it faithfully encodes whatever text is on
disk at the moment it runs.
**How to avoid:** save every sweep edit and delete the script first; rebuild last, in the foreground,
from `/workspaces`, never inside a sub-agent, with a 600000 ms timeout. Because `.planning/graphs/` is
excluded from the gate, **the gate will not catch this** — make it an explicit acceptance criterion.

### Pitfall 4: A broad `git add` tracks `graph.html`
**What goes wrong:** the rebuild writes `.planning/graphs/graph.html` (3 MB, 2 term hits); it is
untracked and **not** gitignored, so `git add -A` tracks it and the gate turns RED on a generated file.
**How to avoid:** commit only by explicit path, and/or add `.planning/graphs/graph.html` to
`.gitignore` — noting `.gitignore` already has an unrelated uncommitted edit.

### Pitfall 5: A sha citation in `CLAUDE.md`
**What goes wrong:** a placeholder sha, or a real short sha invalidated by a later rebase or squash,
leaving tracked prose pointing at nothing.
**How to avoid:** R4 — cite the date and the note path.

### Pitfall 6: Using a GSD verb to flip the requirement boxes
**What goes wrong:** the whole of `REQUIREMENTS.md` is reformatted, or the ROADMAP Phase 196 block is
positionally overwritten and loses its name and requirement IDs.
**How to avoid:** hand-edit `REQUIREMENTS.md:76-79`, `:101-102` and `ROADMAP.md:321-323`, `:331`.

## State of the Art

| Old (CONTEXT.md, at discussion time) | Current (measured 2026-09-17) | Impact |
|---|---|---|
| D-07: two surviving live ClickHouse refs (`STATE.md:3047`, `ROADMAP.md:623`) | plus 8 in `196-CONTEXT.md`, 7 in `196-DISCUSSION-LOG.md`, 2 in `.planning/milestones/v1.38-research/questions.md` + `191-…/COVERAGE.md` | the gate needs two more exclusion classes |
| D-11: the rebuild clears `GRAPH_REPORT.md`, no exclusion needed | one of its two hits is sourced from a D-09-frozen archived file and regenerates | `.planning/graphs/` must be excluded |
| D-11: `graph.json` ~23 MB | **105 MB**; `graph.html` (3 MB) also written, untracked **and unignored** | commit by explicit path |
| D-10: exclude `ROADMAP.md:623` | the closed v1.38 section is lines **333–634**; `:389`, `:605`, `:607`, `:615` also carry terms | exclude by anchor-computed boundary, not one line |
| CONTEXT.md sweep list includes `PROJECT.md:144` | **zero hits** there | 4 sweep sites, not 7 |
| `/gsd-graphify` doc: builds take 15–60 s | last real build **212 s** | use the 600000 ms timeout |

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|---|---|---|
| A1 | The strict reading of D-06 excludes the script's `WHAT THIS DOES NOT MEASURE` caveat block from the note, since D-06 permits only one plain sentence on what was measured | R3 | The note loses the epistemic caveat. Low — the block survives verbatim in the D-09 archive at `…/evidence/193-gate-01-instrument-run.txt`. Flagged as planner's call, not decided |
| A2 | `REQUIREMENTS.md:74`'s heading is acceptable to leave unchanged because the gate term set does not match it | R1 | A verifier could read the "or is retired" heading as an INSTR-02 miss. Cheap to reword; surfaced so the planner chooses deliberately |
| A3 | Extending D-09's exclusion from the 193 directory to all of `.planning/milestones/` is within D-09's stated reason (historical-by-intent) rather than a new decision | R1, R6.5 | If the operator reads it as a new decision, the two Class-A hits need their own disposition. The alternative — three more path exclusions — is equivalent in effect and uglier to audit |
| A4 | `roadmap.update-plan-progress`'s positional overwrite would damage the Phase 196 block | R5.3 | Untested here (running it would edit files, which this research may not do). Mitigation is free: hand-edit. The structural precondition — no table to anchor on — is verified |

## Open Questions

1. **Does the note carry the caveat block, or only one sentence on what was measured?**
   - Known: D-06 permits "one plain sentence" on what the instrument measured; the caveat block
     contains no method residue; four of five precedent notes carry a substantial
     what-is-lost / what-is-now-unguarded section.
   - Unclear: whether D-06's "one plain sentence" governs the caveat too.
   - Recommendation: one plain sentence on what was measured, plus a short "what is lost with it"
     section stating that installed base was never observable and download share was only a proxy —
     phrased as a loss, in the precedent's voice, carrying no method. That satisfies both D-06's letter
     and the precedent's shape.

2. **Does `REQUIREMENTS.md:74`'s heading get reworded?**
   - Known: it states the same live open choice as `:76`, which D-10 puts in scope. It is not matched by
     the recommended gate term set.
   - Recommendation: reword it in the same edit as `:76`. It costs one line and removes the only live
     phrase-level residue the gate cannot see.

3. **Is `.planning/graphs/graph.html` gitignored in this phase, or just avoided?**
   - Known: untracked, unignored, 3 MB, 2 term hits, rewritten by the rebuild; `.gitignore` already
     carries an unrelated uncommitted edit.
   - Recommendation: add it to `.gitignore` in the same commit as the rebuild. Avoidance-by-discipline
     relies on every future commit being careful; the ignore rule is permanent. If the planner prefers
     the minimal diff, commit graph artifacts by explicit path only and say so as a criterion.

## Environment Availability

| Dependency | Required By | Available | Version / evidence | Fallback |
|---|---|---|---|---|
| `git` | deletion, gate file enumeration, commits | ✓ | 5207 tracked files enumerated this session | — |
| `/usr/bin/grep` (GNU) | the gate | ✓ | `-E -I -n -d skip -e` all accepted this session | none — `ugrep` is not a substitute |
| `awk` | the gate's ROADMAP boundary filter | ✓ | ran this session | a second grep leg (worse — D-12 wants one expression) |
| `graphify` | D-11 rebuild | assumed present | `graphify.enabled: true`, and a real build completed `2026-09-17T12:28:29Z` with `"status": "ok"`, `"exit_code": 0` | none — the rebuild is the only sanctioned way to refresh `GRAPH_REPORT.md` |
| `node` | `gsd_run` shim, `graphify build snapshot` | assumed present | the rebuild script and the snapshot verb both require it | none |
| `bash`, `curl` | the *deleted* script only | n/a | — | irrelevant; nothing will run it again |

**Missing dependencies with no fallback:** none identified.
**Not verified this session:** `graphify --version` and `node --version` were not probed — running them
was unnecessary given the recorded successful build, and no version-sensitive claim rests on them.

## Security Domain

`security_enforcement` is absent from `.planning/config.json`, so it is treated as enabled. The
assessment is short because the phase's surface is genuinely nil.

| ASVS Category | Applies | Reason |
|---|---|---|
| V2 Authentication | no | no auth surface; the phase deletes a script and edits four markdown files |
| V3 Session Management | no | no sessions |
| V4 Access Control | no | no access-control code |
| V5 Input Validation | no | no input is parsed; the gate consumes `git ls-files` output only |
| V6 Cryptography | no | no crypto |
| V7 Error Handling / Logging | no | no product code changes |
| V12 Files & Resources | no | file deletion is within the repository, by the operator, under git |
| V14 Configuration | marginal | the only config change under consideration is a `.gitignore` line |

**Net security effect: a reduction.** The deleted script was the meta repository's only artifact that
made an outbound, credential-less HTTP request to a third-party public endpoint. Removing it removes
that egress path and the third-party dependency behind it. No mitigation is required and no threat is
introduced.

## Sources

### Primary (HIGH confidence) — all read or run in this session, 2026-09-17
- `/workspaces/.planning/phases/196-adoption-instrument-disposition/196-CONTEXT.md` — full read (D-01…D-15)
- `/workspaces/tools/adoption/pypi_version_share.sh` — full read (125 lines, 4788 B)
- `/workspaces/.planning/notes/catalog-sync-check-retirement.md` — full read (230 lines)
- `/workspaces/.planning/notes/{host-tools-retirement,dispatch-invariant-retirement-verdict,sdp-surface-retirement-and-behavioral-proof,test-suite-source-introspection-removal}.md` — frontmatter + headings
- `/workspaces/CLAUDE.md:1-40` — § Repository Structure
- `/workspaces/.planning/REQUIREMENTS.md:70-102` — INSTR block and Traceability rows
- `/workspaces/.planning/ROADMAP.md:173-207, 312-332` and section-header index
- `/workspaces/.planning/seeds/SEED-claim-firestarter-slug.md:1-20, 80-95` + heading index
- `/workspaces/.planning/config.json` — full read
- `/workspaces/.claude/hooks/lib/gsd-graphify-rebuild.sh` — full read
- `/workspaces/.claude/hooks/gsd-graphify-update.sh:95-112` — branch gate
- `/workspaces/.claude/commands/gsd-graphify.md:155-200` — build chain and anti-patterns
- `/workspaces/.planning/graphs/.last-build-status.json` — full read
- Commands run: `git status --porcelain`, `git log --oneline -15`, `git rev-parse --abbrev-ref HEAD`,
  `git ls-files` (meta + both sub-repos), `git ls-files -z | xargs -0 /usr/bin/grep` across 12 term
  sets, `git log -L 14,14:CLAUDE.md`, `git log -L 21,25:CLAUDE.md`, `git check-ignore -v`,
  `git diff --numstat -- .planning/graphs`, the full R2 gate

### Secondary (MEDIUM confidence)
- none — no external source was needed. This phase's domain is entirely in-repo.

### Tertiary (LOW confidence)
- none.

## Metadata

**Confidence breakdown:**
- Reference set (R1): **HIGH** — 12 term sets over 5207 tracked files plus both sub-repos' trees, every
  hit bucketed, per-file counts recorded
- Gate (R2): **HIGH** — authored and run; **RED at 11** against the pre-sweep tree, with named blind
  spots and a verified fail-closed precondition
- Artifact and precedent (R3): **HIGH** — both read in full this session
- Citation route (R4): **HIGH** — two in-file precedents traced with `git log -L`
- Mechanics (R5): **HIGH** — working tree, rebuild path, hook gate and commit convention all measured.
  One item is **MEDIUM**: the GSD-verb reformat hazard is inherited from project knowledge, not
  re-tested here (testing it would mutate files); its structural precondition is verified
- Fences (R6): **HIGH** — every zero-reference claim independently re-measured

**Research date:** 2026-09-17
**Valid until:** 2026-09-24 — line numbers in the SWEEP table and the `V138` boundary drift on any
commit to `.planning/`. The gate expression itself does not expire: it computes its boundary from an
anchor and enumerates files from `git ls-files`.
