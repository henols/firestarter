# Phase 196: Adoption Instrument Disposition - Context

**Gathered:** 2026-09-17
**Status:** Ready for planning

<domain>
## Phase Boundary

This phase disposes of `tools/adoption/pypi_version_share.sh` — the instrument Phase 193 built to
gate the `henols/firestarter` slug claim — and brings every live document into agreement with the
disposition.

**The disposition was decided by the operator on 2026-09-17, before planning: RETIRE. The script is
deleted.** Planning does not re-open that choice. Re-pointing the instrument at stranded-2.0.7
acquisition, and deferring the call to a post-research checkpoint, were both offered and declined.

The phase delivers two things and nothing else:

1. The deletion, plus the reason recorded where a reader meets the decision (INSTR-01).
2. A doc sweep such that no live document describes the instrument as gating a claim that has
   already fired (INSTR-02).

It does not touch firmware, the host app, protocol `0x05`, or anything either sub-repo owns. It is a
meta-repo bookkeeping phase and needs no bench and no board.

</domain>

<decisions>
## Implementation Decisions

### Record venue

- **D-01:** The single primary record is a new `.planning/notes/adoption-instrument-retirement.md`,
  following the shape of the five prior retirement notes in that directory — frontmatter
  (`title` / `date` / `context`), a `## VERDICT` section, and a "what is lost with it" section.
  `catalog-sync-check-retirement.md` is the closest analogue and should be read before writing.
  **Not** a `.planning/v1.39/196-*.md` milestone record: `.planning/v1.39/` is archived into
  `.planning/milestones/` at close, and this project treats archived `.planning/`→`.planning/`
  citations as historical-by-intent. A reason a future reader needs — "where did `tools/adoption/`
  go?" — must not end up inside an archive. — **Reversibility:** reversible — a note can be moved.

- **D-02:** **One record, not two.** No second copy in `.planning/v1.39/`. INSTR-02 is a consistency
  requirement, so every additional copy of the reason is another document that can disagree with the
  others.

- **D-03:** `CLAUDE.md` § Repository Structure mirrors the `tools/wiki/` retirement paragraph that
  already sits in that same file — `tools/` reduced to one directory (`tools/catalog/`), plus a
  sentence stating the instrument was retired, when, why in one clause, and pointing at
  `.planning/notes/adoption-instrument-retirement.md`. Not a silent removal.

### What the record says

- **D-04:** The `## VERDICT` states the **full causal chain**, as fact, in the same register as the
  seed's FIRED banner: the operator fired the claim on 2026-09-14 with the trigger **not** met —
  fixed share **12.8%** against a 90% threshold, **116** at-risk `2.0.7` downloads against a ceiling
  of 10, over the 90-day window ending 2026-09-13 — was shown those figures and the consequence, and
  directed the act regardless. The instrument has no consumer *because of that act*, not because it
  stopped working. A retirement note whose reason is "no consumer" without saying why there is no
  consumer records a conclusion, not a reason. `catalog-sync-check-retirement.md` sets the precedent
  of naming the operator's own decision in its VERDICT rather than delegating it to another file.
  Restating the figures alongside the seed cannot drift: they are a frozen dated reading, not a live
  value. No editorializing.

- **D-05:** The record names the two alternatives offered and declined — re-pointing the instrument
  at stranded-2.0.7 acquisition, and deferring the call to a post-research checkpoint. A disposition
  without its rejected options is not auditable.

- **D-06:** **Nothing of the method survives. No ClickHouse, anywhere.** The note carries no SQL, no
  endpoint URL, no `splitByChar`/`toUInt32OrZero` version-array idiom, and no fallback list
  (BigQuery, `pypi_raw`). Operator instruction, verbatim: *"Delete don't want clickhouse at all."*
  The note may describe in one plain sentence what the instrument measured, because the reason is
  unintelligible otherwise; it must not preserve how. Recovery, if it is ever wanted, is the deleting
  commit and the archived Phase 193 evidence — neither of which this phase needs to advertise.
  — **Reversibility:** costly — the working query took a phase to establish and is non-obvious
  (naive string comparison sorts `2.0.10` below `2.0.9`); re-deriving it means redoing that research.
  Accepted knowingly.

- **D-07:** After the deletion, the only surviving live ClickHouse references in the repository are
  `.planning/STATE.md:3047` and `.planning/ROADMAP.md:623` — both frozen historical records inside
  classes D-08 and D-09 already exclude. Eleven more sit in the v1.38 archive. This was measured, not
  assumed; the planner should re-measure rather than trust these line numbers.

### Sweep boundary (INSTR-02)

- **D-08:** **`.planning/STATE.md` is not edited.** All four references (lines 270, 274, 3040, 3047 at
  the time of discussion) are records of what was true when written — a v1.38 dependency rationale and
  two Phase 193 session-log rows. Editing a session log to match a later decision destroys the
  evidence that the decision was later. Declared out of scope here so a verifier does not read them as
  INSTR-02 misses. This also avoids hand-editing `STATE.md`, which this project's tooling notes warn
  against independently.

- **D-09:** The 17 archived files under `.planning/milestones/v1.38-phases/193-the-deferred-claim-made-measurable/`
  are historical-by-intent and excluded from the sweep and from the gate's pathspec. Standing project
  rule; repairing them destroys the evidence.

- **D-10:** `.planning/ROADMAP.md:623` — the completed `193-01-PLAN.md` checkbox line inside the
  **closed** v1.38 section — is historical and not swept. `.planning/ROADMAP.md:321` (Phase 196's own
  success criterion 1, which still reads "either re-pointed … or removed") **is** in scope, as is
  `.planning/REQUIREMENTS.md:76` (INSTR-01's "either … or" wording). Both describe a live open choice
  that is now closed.

- **D-11:** **The graph is rebuilt in-phase.** `/gsd-graphify` runs *after* the deletion and the doc
  sweep, so the tracked `.planning/graphs/GRAPH_REPORT.md` regenerates without the instrument and
  INSTR-02 holds over every tracked document with no generated-file exclusion. Two tracked files
  regenerate — `GRAPH_REPORT.md` and `.last-build-status.json`. `graph.json` (~23M) and
  `graphify-out/` are gitignored and stay out of the commit. **Both tracked graph files are already
  dirty in the working tree at discussion time** — the plan must account for that rather than assume a
  clean baseline. Ordering is load-bearing: a rebuild run before the sweep re-encodes the stale text.

### Proof that INSTR-02 held

- **D-12:** **One grep gate, no hand enumeration of sites.** Operator's explicit choice, made against
  a stated fail-open concern. The gate is a single expression over tracked files with the D-08/D-09/D-10
  historical paths excluded, expected to return zero.

- **D-13:** **The gate must be proven RED against the pre-sweep tree before it is trusted.** A gate
  only ever seen green cannot distinguish "swept" from "expression matches nothing". This is a
  property of the single gate, not a second mechanism, and does not reintroduce the enumeration D-12
  declined. Known local failure modes to avoid, each of which has bitten this repo: BRE escaping,
  dash-leading patterns exiting 2, `;`-chains and OR-greps that fail open, and the devcontainer's
  `grep` being `ugrep`, which honours `.gitignore` and silently under-scans. Use `/usr/bin/grep` with
  an explicit pathspec.

### Seed disposition

- **D-14:** `.planning/seeds/SEED-claim-firestarter-slug.md` is **frozen, with the dead path
  annotated**. `trigger_condition` and § "Why the trigger is what it is" are left verbatim; one line
  is added noting the instrument was retired on 2026-09-17 and pointing at the retirement note.
  The trigger text is the standard the operator's act was judged against, and the FIRED banner's force
  comes from quoting a live standard and showing 12.8% against it — rewriting it to past tense
  degrades the banner into a summary of itself. INSTR-02 is already satisfied there: the seed does not
  describe the instrument as gating a claim that *has already fired*; it says in bold at the top that
  the claim fired and the trigger was not met. What was missing is only that the instrument itself is
  now gone.

- **D-15:** The seed file **stays at its canonical path** in `.planning/seeds/`. It is the single best
  account of the whole episode and must stay findable. Not moved to the archive.

### Claude's Discretion

The operator answered "You decide" on three questions. The calls above are mine, and the planner
should treat them as settled, not re-open them:

- D-01 / D-02 (record venue) — `.planning/notes/`, one record.
- D-04 / D-05 (how plainly to state causation) — full causal chain, plus the declined alternatives.
- D-14 / D-15 (seed) — freeze and annotate, leave in place.

Genuinely open to the planner: how many plans this phase takes, task ordering within the constraint
that the graph rebuild runs last, and the exact wording of every edit.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### The artifact being retired
- `tools/adoption/pypi_version_share.sh` — the instrument itself, 125 lines. Read it before deleting
  it; the retirement note describes what it did.

### Requirements and scope
- `.planning/ROADMAP.md` § "Phase 196: Adoption Instrument Disposition" — goal, three success
  criteria, `Requirements: INSTR-01, INSTR-02`. Criterion 1's "either re-pointed … or removed"
  wording is itself in scope for the sweep (D-10).
- `.planning/REQUIREMENTS.md` § "INSTR — the adoption instrument answers a live question, or is
  retired (v1.38 carry-over)" — INSTR-01 and INSTR-02 verbatim, plus the Traceability rows to flip.
- `.planning/PROJECT.md` — the "third item is bookkeeping" paragraph (near line 68) describing the
  instrument as still running and answering a question with no consumer; and the D-1 row (near line
  144) recording that the claim was made with the adoption trigger unmet.

### The decision this instrument was built to gate
- `.planning/seeds/SEED-claim-firestarter-slug.md` — `status: fired`, `fired_date: 2026-09-14`. The
  FIRED banner carries the 12.8% / 116 figures and the consequence. Cites the script by path in
  `trigger_condition` and again in § "Why the trigger is what it is".
- `.planning/notes/999.9-repo-rename-impact-analysis.md` — the blast-radius analysis behind the claim,
  including § "Standing rule this must produce".

### Precedent for the record's shape (read at least the first)
- `.planning/notes/catalog-sync-check-retirement.md` — closest analogue. Frontmatter, `## VERDICT`
  naming the operator's own decision, and a "what is lost with it" framing in its own title.
- `.planning/notes/host-tools-retirement.md`
- `.planning/notes/dispatch-invariant-retirement-verdict.md`
- `.planning/notes/sdp-surface-retirement-and-behavioral-proof.md`
- `.planning/notes/test-suite-source-introspection-removal.md`

### The sentence the deletion falsifies
- `CLAUDE.md` § Repository Structure — line 19 names `tools/adoption/` as one of two `tools/`
  occupants. The same section's `tools/wiki/` retirement paragraph is the model D-03 mirrors.

### Historical-by-intent — read for context, do NOT edit
- `.planning/milestones/v1.38-phases/193-the-deferred-claim-made-measurable/` — 17 files, including
  `193-01-PLAN.md`, `193-01-SUMMARY.md`, `193-CONTEXT.md`, `193-RESEARCH.md`, `193-PATTERNS.md` and
  `evidence/193-gate-01-instrument-run.txt` (the live reading). Excluded by D-09.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **Five prior retirement notes** in `.planning/notes/` — an established frontmatter + `## VERDICT`
  shape to copy rather than invent.
- **The `tools/wiki/` retirement paragraph already in `CLAUDE.md`** — an in-file model for how this
  project words a tools-directory retirement, including naming the retiring commit and where the last
  occupant went.
- **`.planning/notes/disposable-artifact-inventory.md`** — the existing inventory of what can be
  removed from the meta repo. It does **not** mention the adoption instrument (measured: zero hits),
  so it is not a sweep site, but it is the right neighbour for the new note.

### Established Patterns
- **A phase repairs the sentence its own change falsifies, in the same edit.** Phase 193 hit this in
  reverse: adding `tools/adoption/` falsified CLAUDE.md's single-occupant claim, and 193 corrected it
  in the same edit that added the pointer depending on it. Deleting the directory falsifies the
  two-occupant sentence the same way.
- **Generated artifacts are regenerated, never hand-edited** (the `messages.h` / `messages.py` rule).
  D-11 honours this by rebuilding the graph rather than editing `GRAPH_REPORT.md`.
- **Archived `.planning/` records are evidence, not documents to repair.** D-08, D-09 and D-10 all
  rest on this standing rule.

### Integration Points
- **Nothing consumes the script.** Measured: zero references in `.github/`, zero in `tools/`, zero in
  either sub-repo, zero in any CI workflow. The meta repository has no `.github/workflows/` at all.
  Deletion is mechanically safe and breaks no automation.
- `tools/adoption/` becomes empty and disappears on its own — git does not track empty directories.
- Live reference sites measured at discussion time (re-measure before editing; line numbers drift):
  `CLAUDE.md:19`, `.planning/PROJECT.md:68` and `:144`,
  `.planning/seeds/SEED-claim-firestarter-slug.md:7` and `:88`, `.planning/REQUIREMENTS.md:76`,
  `.planning/ROADMAP.md:321`. Historical, excluded: `.planning/STATE.md:270,274,3040,3047`,
  `.planning/ROADMAP.md:623`, and the 17 archived `193-*` files.

</code_context>

<specifics>
## Specific Ideas

- **Operator's words on the method, quoted so no agent softens them:** *"Delete don't want clickhouse
  at all."* Preceded by *"I have no idea what it is and what clickhouse is. Don't understand why we
  should need it."* The retirement note must not read as a place where the technique was quietly
  preserved.

- **Register for the VERDICT:** the seed's FIRED banner is the model — *"It was not a threshold breach
  and it was not an accident."* Flat, factual, no hedging and no editorial.

- **A known sequencing snag for the planner, not a decision.** The `tools/wiki/` paragraph that D-03
  mirrors cites its own retiring commit by short sha, which a commit cannot do for itself. The wiki
  precedent resolved this across two commits (`5426d7ef` retired, a later commit deleted and cited).
  Either sequence the CLAUDE.md citation into a follow-up commit, or cite by date instead of sha.
  Do not write a placeholder sha.

</specifics>

<deferred>
## Deferred Ideas

- **A fired seed still matches the `SEED-*.md` glob `/gsd-new-milestone` reads.**
  `SEED-claim-firestarter-slug.md` is `status: fired` and cannot fire again, yet it will keep
  surfacing to milestone creation. That is GSD tooling behaviour, not a Phase 196 deliverable, and
  D-15 keeps the file where it is. Worth a todo; not fixed here.

- **`reference_pypi_per_version_downloads_clickhouse`** exists as a Claude memory outside this
  repository, recording the ClickHouse method D-06 deletes. It is outside the phase's reach and
  outside INSTR-02's scope (not a document in this repo), but the operator should be asked whether it
  goes too, since the instruction was "don't want clickhouse at all".

### Reviewed Todos (not folded)

`todo.match-phase 196` returned 34 of 41 todos. **None were folded.** Every match is keyword noise —
they scored on the tokens "phase", "tools", "nothing", "still" and "decision" — and not one concerns
the adoption instrument, the slug claim, or PyPI download measurement. Highest scorers for the record:
"Strip residual GSD provenance comments from product source", "sync_to_subrepos.sh runs `diff -q $X
$X` twice", "Close the six stale enforcement claims WR-01..WR-06". All out of scope.

</deferred>

---

*Phase: 196-adoption-instrument-disposition*
*Context gathered: 2026-09-17*
