# Phase 196: Adoption Instrument Disposition - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-09-17
**Phase:** 196-adoption-instrument-disposition
**Areas discussed:** Where the reason lives, How far the sweep reaches, What survives the script, The seed's fired trigger

**Pre-decided, not discussed:** the disposition itself. The operator decided RETIRE on 2026-09-17
before planning began. Re-pointing the instrument at stranded-2.0.7 acquisition and deferring to a
post-research checkpoint were offered and declined at that time.

**Area selection:** all four offered areas were selected.

---

## Where the reason lives

### Q1 — primary record venue

| Option | Description | Selected |
|--------|-------------|----------|
| notes/ retirement note | New `.planning/notes/adoption-instrument-retirement.md`, matching five prior retirement notes | ✓ (Claude's call) |
| v1.39/ milestone record | `.planning/v1.39/196-*.md`, matching this milestone's 194/195 record convention | |
| Both, with one primary | Durable note plus a short v1.39 pointer | |

**User's choice:** "You decide."
**Notes:** Claude chose the `.planning/notes/` note as the single record. Rationale: `.planning/v1.39/`
is archived into `.planning/milestones/` at close, and archived `.planning/`→`.planning/` citations are
historical-by-intent in this project — a reason a future reader needs must not land inside an archive.
One record rather than two, because INSTR-02 is a consistency requirement and each extra copy is another
document that can disagree.

### Q2 — CLAUDE.md § Repository Structure after the deletion

| Option | Description | Selected |
|--------|-------------|----------|
| Mirror the wiki precedent | Same treatment CLAUDE.md already gives `tools/wiki/`: one occupant, plus a retirement sentence with date, one-clause reason, and a pointer to the note | ✓ |
| One clause, note carries it | Single trailing clause naming the retirement and the note path, no reason restated | |
| Silent removal | Drop the bullet, restore single-occupant wording, leave no trace | |

**User's choice:** Mirror the wiki precedent.
**Notes:** Surfaced afterwards as an implementation snag, not a decision — the `tools/wiki/` paragraph
cites its own retiring commit by short sha, which a commit cannot do for itself. The precedent resolved
it across two commits. Planner sequences a follow-up commit or cites by date; no placeholder sha.

### Q3 — how plainly the note states causation

| Option | Description | Selected |
|--------|-------------|----------|
| Full causal chain | Name the override and the figures, as `catalog-sync-check-retirement.md` does in its own VERDICT | ✓ (Claude's call) |
| Conclusion plus pointer | State "no consumer", cite the seed's FIRED banner for figures, keep numbers in one place | |
| Neutral framing | Record only that the claim is settled; do not restate how | |

**User's choice:** "You decide."
**Notes:** Claude chose the full causal chain. A reason of "no consumer" without saying why there is no
consumer records a conclusion, not a reason. The drift argument against duplication does not apply:
12.8% / 116 / 90% / 10 is a frozen dated reading from 2026-09-13, not a live value. Register to match
the seed's FIRED banner — flat and factual, no editorial.

### Decided by precedent, not asked

The note records the two alternatives offered and declined. A disposition without its rejected options
is not auditable, and every other retirement note here carries them.

---

## How far the sweep reaches

### Q1 — STATE.md's four references

| Option | Description | Selected |
|--------|-------------|----------|
| Historical — leave them | All four are records of what was true when written; editing a session log to match a later decision destroys the evidence that the decision was later. Declare out of scope in CONTEXT.md | ✓ |
| Recap yes, log no | Amend the two forward-looking recap lines (270/274), freeze the two session rows (3040/3047) | |
| Sweep all four | Correct any live tracked document that reads as present tense | |

**User's choice:** Historical — leave them.

### Q2 — the generated graph surface

| Option | Description | Selected |
|--------|-------------|----------|
| Out of scope, no hand-edit | `GRAPH_REPORT.md` is generated; the messages.h/messages.py rule forbids hand-editing generated files. Exclude it | |
| Rebuild the graph in-phase | Run `/gsd-graphify` after the deletion and sweep so the tracked report regenerates clean; INSTR-02 then needs no exclusion | ✓ |
| Out of scope, filed | Exclude it but file a todo so the stale report is not forgotten | |

**User's choice:** Rebuild the graph in-phase.
**Notes:** Established after the answer — two tracked files regenerate (`GRAPH_REPORT.md`,
`.last-build-status.json`); `graph.json` (~23M) and `graphify-out/` are gitignored. Both tracked files
are already dirty in the working tree. Ordering is load-bearing: a rebuild before the sweep re-encodes
the stale text.

### Q3 — what proves INSTR-02 held

| Option | Description | Selected |
|--------|-------------|----------|
| Gate plus named enumeration | A grep gate proven RED first, plus every site named individually so a fail-open gate cannot pass vacuously | |
| Gate only | One grep expression with an explicit pathspec, returning zero | ✓ |
| Enumeration only | Hand disposition of every site, no automated check | |

**User's choice:** Gate only.
**Notes:** Chosen against an explicitly stated fail-open concern — this repo has been bitten by BRE
escaping, dash-leading patterns exiting 2, OR-greps, and the devcontainer's `grep` being `ugrep`, which
honours `.gitignore` and silently under-scans. Claude carried one property into the gate spec rather
than a second mechanism: the gate must be proven RED against the pre-sweep tree before it is trusted,
since a gate only ever seen green cannot distinguish "swept" from "expression matches nothing". Offered
for the user to drop as well; not dropped.

### Decided by standing rule, not asked

The 17 archived files under `.planning/milestones/v1.38-phases/193-*/` are historical-by-intent and
excluded from the sweep and the gate's pathspec.

---

## What survives the script

### Q1 — the method

| Option | Description | Selected |
|--------|-------------|----------|
| Query verbatim in the note | Embed the SQL and endpoint in a "what is lost with it" section so the measurement stays reconstructible | |
| Pointer to git and archive | State what it did; cite the deleting commit and the archived Phase 193 evidence | |
| Reason only | Record the disposition and its reason; the method is re-derivable from public docs | ✓ (arrived at after clarification) |

**User's choice:** first response — *"I have no idea what it is and what clickhouse is. Don't understand
why we should need it."* After a plain-language explanation of what the ClickHouse public playground is,
why Phase 193 used it (PyPI's own stats service has no per-version endpoint), and what keeping or
dropping the query would cost: *"Delete don't want clickhouse at all."*

**Notes:** Stronger than the "Reason only" option as written. No SQL, no endpoint URL, no version-array
idiom, no fallback list (BigQuery, `pypi_raw`). The note may say in one plain sentence what the
instrument measured, because the reason is unintelligible otherwise, but must not preserve how.
Recorded cost, accepted knowingly: the working query took a phase to establish and is non-obvious —
naive string comparison sorts `2.0.10` below `2.0.9`.

Measured after the decision: deleting the script leaves exactly two live ClickHouse references in the
repository, `STATE.md:3047` and `ROADMAP.md:623`, both already excluded as historical; eleven more sit
in the v1.38 archive.

---

## The seed's fired trigger

### Q1 — disposition of SEED-claim-firestarter-slug.md

| Option | Description | Selected |
|--------|-------------|----------|
| Freeze, annotate the path | Leave `trigger_condition` verbatim; add one line noting the instrument was retired and pointing at the note | ✓ (Claude's call) |
| Rewrite the trigger text | Edit to past tense and strip the script path so no live document names a missing file | |
| Retire the seed file | Move it out of `.planning/seeds/` so it stops matching the `SEED-*.md` glob, text intact | |

**User's choice:** "You decide."
**Notes:** Claude chose freeze-and-annotate. The trigger text is the standard the operator's act was
judged against, and the FIRED banner's force comes from quoting a live standard and showing 12.8%
against it; rewriting it to past tense degrades the banner into a summary of itself. INSTR-02 is
already satisfied there — the seed does not describe the instrument as gating a claim that has already
fired; it says in bold that the claim fired and the trigger was not met. The file stays at its
canonical path as the best single account of the episode.

---

## Claude's Discretion

Three questions were answered "You decide". The calls, and the reasoning, are recorded in CONTEXT.md as
D-01/D-02, D-04/D-05, and D-14/D-15:

- Record venue — `.planning/notes/`, one record, not two.
- Causation — full causal chain, plus the two declined alternatives.
- Seed — freeze and annotate, leave in place.

Left genuinely open to the planner: plan count, task ordering within the constraint that the graph
rebuild runs last, and the exact wording of every edit.

---

## Deferred Ideas

- **A fired seed still matches the `SEED-*.md` glob `/gsd-new-milestone` reads.** GSD tooling
  behaviour, not a Phase 196 deliverable. Worth a todo.
- **`reference_pypi_per_version_downloads_clickhouse`** — a Claude memory outside this repository
  recording the ClickHouse method. Outside the phase's reach and outside INSTR-02's scope, but the
  operator should be asked whether it goes too, given "don't want clickhouse at all".

## Scope creep

None. Discussion stayed inside the phase boundary throughout.

## Todos reviewed, none folded

`todo.match-phase 196` returned 34 of 41 todos, all keyword noise scoring on "phase", "tools",
"nothing", "still", "decision". None concerns the adoption instrument, the slug claim, or PyPI download
measurement. Not presented individually; recorded here for audit.
