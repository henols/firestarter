# Phase 196: Adoption Instrument Disposition - Pattern Map

**Mapped:** 2026-09-17
**Files analyzed:** 6 (1 created, 5 edited)
**Analogs found:** 5 / 6 (the D-06 forbidden-token list has no analog — see §4)

This is a documentation phase in a meta/planning repository. There is no source code, no data flow
and no test file, so the frame used throughout is **prose artifact + its precedent document**, not
role + data flow + module.

RESEARCH.md §R1 owns the reference measurement and §R2 owns the gate. Neither is re-derived here.
Every line number below was **re-verified this session** against the working tree at HEAD `5d188fc2`.

## File Classification

| File | Disposition | Artifact kind | Closest analog | Match quality |
|---|---|---|---|---|
| `.planning/notes/adoption-instrument-retirement.md` | **create** | post-deletion retirement record | `.planning/notes/catalog-sync-check-retirement.md` | exact (D-01 names it) |
| `CLAUDE.md` §Repository Structure (`:16-19`) | edit — replace 2 lines, delete 1 bullet, append 1 paragraph | in-file tools-inventory + retirement paragraph | `CLAUDE.md:14` (wiki) and `CLAUDE.md:21-25` (citation gate) — **same file** | exact |
| `.planning/PROJECT.md:68-71` | edit — reword 2 sentences | live milestone-framing prose | none needed (self-contained paragraph) | n/a |
| `.planning/REQUIREMENTS.md:74`, `:76-77`, `:101-102` | edit — reword heading, reword requirement, flip 2 traceability cells | requirement text + traceability table | `:95-99` (completed rows in the same table) | exact |
| `.planning/ROADMAP.md:321-323` (and `:331`) | edit — reword criterion 1; criterion 3 becomes vacuous | phase success criterion | `ROADMAP.md:236`, `:286` (`**Plans:** N/N plans complete`) | exact |
| `.planning/seeds/SEED-claim-firestarter-slug.md` | edit — **append one annotation line only** (D-14 freeze) | frozen seed with a banner | the FIRED banner's own closing line `:38-39` | partial |

**Not edit targets.** `.planning/STATE.md` (D-08) and the 17 files under
`.planning/milestones/v1.38-phases/193-the-deferred-claim-made-measurable/` (D-09). Read for context
only. `.planning/graphs/GRAPH_REPORT.md` and `.last-build-status.json` change only by rebuild
(D-11), never by hand.

---

## 1. The retirement-note template

**Analog:** `.planning/notes/catalog-sync-check-retirement.md` (230 lines, read in full this
session). Skeleton below; `<…>` are placeholders for the executor to fill. Length figures in
parentheses are the analogue's, given so the executor knows the expected register, not as a target.

```markdown
---
title: <Thing> retirement — <why it has no consumer> and what is lost with it
date: 2026-09-17
context: v1.39 Phase 196, INSTR-01 / INSTR-02 (D-01…D-06, D-14) — read from the live script before deletion
---

# Adoption instrument retirement (INSTR-01)

## VERDICT

<Para 1 (~15 lines). Decision in bold in the FIRST sentence. Then the causal chain as fact. Then the
 operator's grounds quoted verbatim. Then one sentence on why it is recorded here.>

<Para 2 (~4 lines). A checklist sentence naming everything this note is required to carry.>

## 1. What the instrument measured, and what it reported
<~8 lines. ONE plain sentence on what was measured (D-06's allowance), plus the eight-line stdout
 shape. NO method — see §4 of PATTERNS.md.>

## 2. The two alternatives offered and declined
<~12 lines. D-05. One short subsection or bolded sentence per alternative, each with why it was
 declined.>

## 3. What is lost with it — stated, not hidden
<~20 lines. D-06's accepted cost, plus the epistemic loss: installed base was never observable and
 download share was only a proxy for it. Phrase as a loss.>

## 4. The residual gap, named explicitly
<~15 lines. What is no longer measurable at all, in bold. Whether anything is filed. Close in the
 analogue's voice: naming a gap and filing a gap are different acts.>
```

### Where each decision lands in the skeleton

| Decision | Lands in | What it contributes |
|---|---|---|
| **D-04** (full causal chain) | `## VERDICT` para 1 | operator fired the claim **2026-09-14** with the trigger **not** met — fixed share **12.8%** against a 90% threshold, **116** at-risk `2.0.7` downloads against a ceiling of **10**, over the 90-day window ending **2026-09-13**; shown the figures and the consequence and directed the act regardless. The instrument has no consumer *because of that act*, not because it stopped working. |
| **D-04** (register) | `## VERDICT` para 1, closing | Flat and factual, the seed banner's register: *"It was not a threshold breach and it was not an accident."* No hedging, no editorial. |
| **D-05** (declined alternatives) | `## 2.` | re-pointing the instrument at stranded-`2.0.7` acquisition; deferring the call to a post-research checkpoint. |
| **D-06** (method is gone) | constrains `## 1.` and `## 3.` | one plain sentence on *what*, nothing on *how*. Operator verbatim: *"Delete don't want clickhouse at all."* |
| **D-06** (accepted cost) | `## 3.` | reversibility is costly and accepted knowingly; recovery route is the deleting commit and the Phase 193 archive, which this note need not advertise. |
| **RESEARCH §R3 / OQ-1** | `## 3.` | the recommended resolution of the caveat-block question: one sentence on what was measured **plus** a what-is-lost section, not the caveat block itself. |

### Convention vs. one note's choice

Measured across all five notes (frontmatter + headings read this session).

| Element | Status |
|---|---|
| `title` / `date` / `context` frontmatter, **in that key order** | **convention** (4 of 5; `sdp-surface-…` has none and is the weakest analogue) |
| `context` names milestone, phase, requirement/decision ids, **and how the facts were obtained** | **convention** (all 4 with frontmatter) |
| A VERDICT-or-ruling section **first** | **convention** (5 of 5) |
| Operator's grounds **quoted verbatim, in their own words** | **convention** (5 of 5) |
| A what-is-lost / what-is-now-unguarded section, stated plainly | **convention** (5 of 5) |
| Numbered `## N.` sections | **convention** (3 of 5) |
| H1 restating the title, tagged | convention, but the **tag is free**: `(CLAIM-08)` a requirement id vs `(Phase 188)` a phase number |
| All-caps headings (`## THE VERDICT`, `## THE GROUNDS`) | **one note's choice** — `dispatch-invariant-retirement-verdict.md` only. Free to vary. |
| `## Two questions a reader will ask next` | **one note's choice** — `catalog-sync-check-retirement.md` only |
| `## Backlog items this verdict generates` | **one note's choice** — and `catalog-sync-check-retirement.md` deliberately files nothing (D-04 there). Files no backlog by default. |
| No H1 at all, terse unnumbered sections | **one note's choice** — `test-suite-source-introspection-removal.md` (87 lines, the shortest) |

**The D-04 model, verbatim from the analogue** (`catalog-sync-check-retirement.md:11-23`) — this is
the exact move to imitate: decision in bold → *"on the operator's own decision, taken against the
orchestrator's recommendation to <declined alternative>"* → measured figures → operator's grounds
quoted → closing sentence:

> **`Catalog sync check` is retired outright — the workflow file is deleted, on the operator's own
> decision, taken against the orchestrator's recommendation to re-point its trigger at `beta`.**
> […] The operator's grounds, in their own words: the catalog *"has no value to the main branch
> […]"*. That is recorded here so a later reader does not read the deletion as an oversight or as
> evidence the property stopped mattering […]

And the para-2 checklist move (`:25-30`):

> This note carries all five things CLAIM-08's amendment requires it to carry: the cause of the
> standing failure, why the 2026-08-18 fix did not reach it, […] and the residual gap the
> retirement leaves — named plainly, and left unfiled on the operator's explicit instruction (D-04).

And the closing move for the residual-gap section (`:211`):

> Naming a gap and filing a gap are different acts; this note performs only the first.

---

## 2. Per-edit-site excerpts

Exact current text, quoted. **No replacement prose is authored here** — CONTEXT.md reserves the
exact wording of every edit for the planner.

### S1 — `CLAUDE.md:16-19` — replace the count sentence, delete one bullet

```
16: `tools/` holds two directories:
17:
18: - `tools/catalog/` — messages codegen and sub-repo sync tooling.
19: - `tools/adoption/` — the PyPI per-version download-share instrument.
```

**Shape:** delete `:19`; reword `:16` so the count is no longer "two" (the established pattern — a
phase repairs the sentence its own change falsifies, in the same edit); **append** a new retirement
paragraph modelled on §3 below. Cite **by date, not by sha** (RESEARCH §R4).

### S2 — `.planning/PROJECT.md:68-71` — reword the last two sentences

```
68: The third item is bookkeeping the v1.38 close left behind: `tools/adoption/pypi_version_share.sh`
69: was built to measure whether it was safe to claim `henols/firestarter`. The operator claimed it on
70: 2026-09-14 with the trigger unmet, and the seed is `status: fired`. The instrument still runs and still
71: reports, but it now answers a question with no consumer.
```

**Shape:** `:68-70` are still true as history. Only `:70-71` — *"The instrument still runs and still
reports"* — is falsified. Reword to past tense and point at the retirement note.
(CONTEXT.md's `PROJECT.md:144` is **not** a site: zero hits, confirmed.)

### S3 — `.planning/REQUIREMENTS.md:74`, `:76-77`, `:101-102`

```
74: ### INSTR — the adoption instrument answers a live question, or is retired (v1.38 carry-over)
...
76: - [ ] **INSTR-01**: `tools/adoption/pypi_version_share.sh` either measures a question with a named
77:       consumer, or is removed. Either way the disposition is recorded with its reason.
78: - [ ] **INSTR-02**: No document describes the instrument as gating a claim that has already fired. The
79:       seed, `CLAUDE.md` and any note pointing at it agree with the chosen disposition.
...
101: | INSTR-01 | Phase 196 | Pending |
102: | INSTR-02 | Phase 196 | Pending |
```

**Shape:** reword `:74` (the heading's *"or is retired"* is the only live phrase-level residue the
gate cannot see — RESEARCH OQ-2 recommends rewording it in the same edit as `:76`); reword `:76-77`
so the "either … or" closed choice reads as the settled disposition; `:78-79` (INSTR-02) needs no
change; flip `:101-102` `Pending` → `Complete`. **Analog for the flip:** `:95-99` in the same table
already read `| WRITE-01 | Phase 195 | Complete |`.
**Hand-edit.** Do not use the GSD `requirements` verb — it reformats the whole file.

### S4 — `.planning/ROADMAP.md:321-323` (and `:331`)

```
319: **Success criteria**:
320:
321: 1. `tools/adoption/pypi_version_share.sh` is either re-pointed at a question with a named consumer, or
322:    removed. The disposition and its reason are recorded where a reader meets the decision, not only in
323:    a commit message.
324: 2. No document describes the instrument as gating a claim that has already fired — the seed,
325:    `CLAUDE.md` and any note pointing at it agree with the chosen disposition.
326: 3. If the instrument is retained, the record names who reads its output and when. "It might be useful"
327:    is not a consumer.
...
331: **Plans:** TBD
```

**Shape:** reword criterion 1 (`:321-323`) to the settled disposition. Criterion 2 is unchanged.
**Criterion 3 (`:326-327`) is now vacuously satisfied** — its antecedent ("if the instrument is
retained") is false; the planner should decide whether to say so or leave it. `:331` `**Plans:**
TBD` → `N/N plans complete`, matching `:236` and `:286`.
**Hand-edit.** Do not run `roadmap.update-plan-progress` — the v1.39 section has no table for it to
anchor on, which is exactly the shape in which a positional writer overwrites adjacent prose.

### S5 — `.planning/seeds/SEED-claim-firestarter-slug.md` — **append one line, rewrite nothing**

Both term sites are **frozen verbatim** by D-14:

```
 3: trigger_condition: >-
 ...
 7:   `tools/adoption/pypi_version_share.sh` is the evidence. No second consecutive
...
88: The instrument that produces the reading is `tools/adoption/pypi_version_share.sh`. One
89: reading over the 90-day window is the evidence.
```

**Shape:** add **one** line noting the instrument was retired on 2026-09-17 and pointing at
`.planning/notes/adoption-instrument-retirement.md`. Nothing else changes — not the
`trigger_condition`, not § "Why the trigger is what it is" (`:55`).

**Placement analog, in the same file.** The FIRED banner already ends with two annotation lines that
do exactly this job — point outward, then explain why the text below is retained unchanged
(`:37-39`):

> Evidence: `.planning/phases/193-the-deferred-claim-made-measurable/evidence/`.
> The trigger text below is retained unchanged as the record of the bar that was set and
> not cleared — it is history now, not a gate.

The new line belongs alongside these, inside the banner block, in the same voice. Note the banner's
register at `:24` — *"It was not a threshold breach and it was not an accident."* — which D-04 also
names as the model for the note's VERDICT.

---

## 3. The two in-file `CLAUDE.md` precedents, verbatim

Both live in the same section the edit touches. **The executor imitates these twice: once for the
paragraph's structure, once for its citation style.**

### 3a. The structural model D-03 mirrors — `CLAUDE.md:14`

```
The `tools/wiki/` checkers validated a clone of that wiki. Commit `5426d7ef` retired them on
2026-09-02. A later commit deleted `tools/wiki/` on 2026-09-08. Its last occupant,
`MIGRATION-TABLE.md`, moved to `.planning/milestones/v1.35-MIGRATION-TABLE.md` as a record of the
completed migration. **No automated wiki guard exists now.**
```

**Structural moves, in order:** (1) name the thing and what it did, in one clause; (2) name the
retiring act with a date; (3) name the deleting act with a date; (4) say where the durable record
went, by path; (5) close with a **bolded standing consequence** in the present tense.

Move (3) is the direct precedent for this phase's situation: *"A later commit deleted `tools/wiki/`
on 2026-09-08"* — **the deleting act is cited by date, with no sha at all.** The sha `5426d7ef` in
move (2) was citable only because that commit already existed and was independent; the paragraph
naming it was written far later.

### 3b. The date-citation precedent — `CLAUDE.md:21-25`, three days old

```
**Nothing mechanically enforces the source-comment rule.** Each sub-repo used to run a
`planning_citation_gate.py` in CI. Both scripts and all three CI steps were removed by operator
decision on 2026-09-17. The rule now rests entirely on the per-repo `CLAUDE.md` text and the
pre-commit check it carries. Restore points, if the gate is ever wanted back:
`firestarter_fw` `876a223`, `firestarter_app` `c77ff2e`.
```

**Structural moves, in order:** (1) **bolded standing consequence first**; (2) what used to exist;
(3) *"removed by operator decision on <date>"* — **a date for the act the commit itself performs**;
(4) what the rule rests on now; (5) shas **only** as restore points in other repositories, which
existed independently.

**This is the citation pattern to follow.** A short sha written into tracked prose does not survive
a rebase or squash — this branch has already absorbed a merge from `origin/beta` (`1c3afec9`). Do
not write a placeholder sha and do not write "commit TBD". The durable pointer is the note path,
which D-03 requires anyway.

---

## 4. The D-06 negative pattern — what must NOT appear

**This is a negative pattern and it has no analog. None of the five precedent notes has an
equivalent section, because none of them deleted a method the operator asked to be gone.** The
executor cannot copy this from anywhere; it is a constraint to check against, not a shape to fill.

Checkable forbidden-token list for `.planning/notes/adoption-instrument-retirement.md`. Presence of
any of these in that file means the method was preserved and D-06 failed.

| # | Forbidden token / class | Named by |
|---|---|---|
| F1 | `ClickHouse` / `clickhouse` in any casing | D-06 (operator verbatim: *"Delete don't want clickhouse at all."*) |
| F2 | `splitByChar` | D-06 |
| F3 | `toUInt32OrZero` | D-06 |
| F4 | `pypi_raw` | D-06 |
| F5 | `BigQuery` | D-06 (fallback list) |
| F6 | `pypistats` | D-06 (fallback list) |
| F7 | Any `http://` or `https://` literal pointing at a query endpoint | D-06 (endpoint URL) |
| F8 | Any SQL keyword — `SELECT`, `WHERE`, `FORMAT`, `GROUP BY` — or any fenced block containing one | D-06 (no SQL) |
| F9 | The dataset **table name** — the long dotted identifier naming the per-day/per-version/per-installer aggregate | **RESEARCH §R3 — not named by D-06** |
| F10 | `user=`, or any description of the credential-less anonymous auth query parameter | **RESEARCH §R3 — not named by D-06** |
| F11 | The output-format directive appended to the query | **RESEARCH §R3 — not named by D-06** |
| F12 | The filter predicates — the installer allow-list, the 90-day window expression, the prerelease-exclusion regex | **RESEARCH §R3 — not named by D-06** |

**The tokens are named, not reproduced.** No SQL, no endpoint URL, no dotted table name and no query
idiom is transcribed into this file or into RESEARCH.md — reproducing them in a document this phase
commits is exactly the failure D-06 exists to prevent.

**What is permitted, and is not method:** one plain sentence on what the instrument measured (the
split between downloads of a fixed stable version and downloads of the single at-risk stable
version, over a rolling 90-day window on the stable channel), and the shape of its eight-line
stdout. Neither carries a query, a host or an idiom.

**Note the asymmetry with the gate.** F1–F6 are all in the RESEARCH §R2 gate term set, but the gate
**excludes** `.planning/phases/196-adoption-instrument-disposition/` and so cannot see this new
note's directory either way — the note lives in `.planning/notes/`, which the gate *does* scan, so
F1–F6 are gate-visible there. F7–F12 are **not** in the term set and are not mechanically checked
by anything. This list is the only check on them.

## Metadata

**Analog search scope:** `.planning/notes/` (5 retirement notes), `CLAUDE.md` §Repository Structure,
`.planning/REQUIREMENTS.md` Traceability table, `.planning/ROADMAP.md` sibling phase blocks,
`.planning/seeds/SEED-claim-firestarter-slug.md` FIRED banner.
**Files read this session:** 6 full, 5 by bounded window.
**Line numbers re-verified:** 2026-09-17 at HEAD `5d188fc2`, branch
`v1.39-protocol-0x05-write-correctness`. They drift on any commit to `.planning/`.
**Pattern extraction date:** 2026-09-17
