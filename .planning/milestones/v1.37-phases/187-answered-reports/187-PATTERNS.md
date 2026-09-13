# Phase 187: Answered Reports - Pattern Map

**Mapped:** 2026-09-12
**Files analyzed:** 14 artifacts (5 reply bodies, 1 review/approval doc, 1 notes record, 5 record repairs, evidence tree, merge record)
**Analogs found:** 14 / 14 — every artifact in this phase has a named, tracked, in-repo precedent
**Tracked-source gate:** all analog paths below verified with `git ls-files` in `/workspaces` (meta repo). No gitignored mirrors cited.

> **This phase produces no product source.** No Python or C++ file is created or modified by these
> patterns. Every artifact is a planning-repo document or a shell/`gh` procedure. Do not go looking for
> `firestarter_app/` or `firestarter/` analogs — the code those repos carry is *described* by the replies,
> not changed by them (the code merges are D-01/D-02 ship work, already-written commits).

---

## File Classification

| New/Modified artifact | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `187-GH23-COMMENT.md`, `-GH28-`, `-GH31-`, `-GH60-`, `-GH62-` (phase dir) | outward-facing reply body | file-I/O → request-response (`gh issue comment --body-file`) | `.../152-GH12-COMMENT.md`, `152-GH11-COMMENT.md`, `152-GH21-COMMENT.md` | **exact** |
| `evidence/bodies/187-gh{23,28,31,60,62}.md` (byte-identical post payloads) | posting payload | file-I/O | `.../173-.../evidence/bodies/173-gh9.md` (+ gh5/6/7) | **exact** |
| `187-UPSTREAM-REPLIES.md` (review doc + dispositions + status line) | operator-gate review record | document / state-machine | `.../173-UPSTREAM-REPLIES.md` | **exact** |
| `evidence/187-operator-approval.txt` (hash-bound approval) | approval gate artifact | file-I/O + sha256 binding | `.../173-.../evidence/173-07-operator-approval.txt` | **exact** |
| `.planning/notes/<name>.md` (D-09 verdict + reply ledger) | durable verdict/ledger record | document | `.planning/notes/ae29f2008-classification-verdict.md` (183), `dispatch-invariant-retirement-verdict.md` (184), `catalog-sync-check-retirement.md` (185), `jumper-display-ground-truth.md` (182) | **exact** |
| `.planning/ROADMAP.md:5409-5411`, `:5424` (stale prose repair) | record repair — factual correction | in-place edit | ROADMAP `:2177` (v1.32 D-05 amendment), `:51` | **exact** |
| `.planning/ROADMAP.md:502` (criterion 4 **amended**) | record repair — criterion amendment | in-place edit | ROADMAP `:321` (183 D-08), `:365` (184 D-03), `:418` (185 D-02) | **exact** |
| `.planning/REQUIREMENTS.md:118` (REPLY-07 **amended** + Complete) | record repair — requirement amendment | in-place edit | REQUIREMENTS `:75-80` (SAFE-06, 183 D-07/D-08), `:148-150` (185 D-02) | **exact** |
| `.planning/REQUIREMENTS.md:217` (traceability row Pending → Complete) | record repair — table row | in-place edit | REQUIREMENTS `:195-200` (SAFE-06…CLAIM-02 rows) | **exact** |
| `evidence/187-issue-state-before.json` / `-after.json` | evidence capture | API read → file | `.../173-.../evidence/173-04-issue-state-before.json`, `173-07-issue-state-after.json` | **exact** |
| `evidence/187-post-transcript.txt` | evidence capture | command transcript | `.../173-.../evidence/173-07-post-transcript.txt` | **exact** |
| `187-MERGE-RECORD.md` (3 PRs, 2 cuts, gitlink handoff) | ship/merge record | document | `.../152-MERGE-RECORD.md` | **exact** |
| `evidence/187-*-operator-approval.txt` (per-merge gate) | approval gate artifact | file-I/O | `.../173-.../evidence/173-03/05/06/09-operator-approval.txt` (one per public act) | **exact** |

---

## Pattern Assignments

### `187-GH{N}-COMMENT.md` — the five reply bodies (outward-facing reply, request-response)

**Analog:** `.planning/milestones/v1.32-phases/152-outward-facing-close-operator-gated/152-GH12-COMMENT.md`
(4,313 B), with `152-GH11-COMMENT.md` (6,789 B) and `152-GH21-COMMENT.md` (4,269 B) as siblings.

**Shape on disk:** a *bare markdown body only* — no frontmatter, no title, no phase metadata, no `#` heading.
The first line is the first sentence a reporter reads. This is the file handed to `--body-file` unmodified.

**Opening-move pattern** (`152-GH21-COMMENT.md:1-3`, `152-GH11-COMMENT.md:1-6`) — address the reporter by
handle, name the exchange being resumed, concede in the first two sentences (D-13):

```
Hi @AndersBNielsen — following up on your `dev test` report for at28c256.

**What your report already told us**
```

```
Following up on the 2026-08-03 exchange further up this thread, @datapaganism. You'd hacked a
`CMD_ERASE` command into `configure_eeprom28c` yourself and asked how to trigger it from
`firestarter` proper. The answer that day was "It's not probably implemented yet, I will soon get
it pushed and I will keep you posted." That took a lot longer than "soon" — the push landed 18 days
later, in this milestone's work — but this comment is that promise being kept, not a silence being
broken.
```

**Bolded-section-label pattern** — the bodies are organised by short bolded labels, not `##` headings
(headings render huge in a GitHub comment). Observed labels across the three 152 bodies:
`**What changed**`, `**What did get better**`, `**What remains unproven**`,
`**This is where I need help, and it's the honest reason `dev test` exists**`,
`**What your report already told us**`. Phase 173 used the same convention: `**Delivered.**`,
`**Deferred, not delivered.**`, `**Declined, deliberately, and named here rather than left implicit:**`,
`**Nothing else is outstanding against this issue.**`, `**Where the surviving tracker is.**`
(`173-UPSTREAM-REPLIES.md`, gh#5/gh#6/gh#7/gh#9 bodies).

**Concede-then-hold pattern (D-10/D-11's exact shape)** — 152-GH12 concedes the ask was only
half-answered *and* refuses to let the release notes imply otherwise:

```
`dev sdp <chip> enable|disable` is gone. The two halves don't survive equally, and I'd rather be
plain about that than let the release notes imply otherwise:

- **`disable`'s behaviour survives, and you no longer need a command for it.** …
- **`enable` is withdrawn, with no replacement — for a second release now.** If you want a part
  deliberately left protected, there is still no supported way to do it. The ask is half-answered
  for a second release: deliberate protection stays tracked as Backlog 999.28, and I'm not going to
  promise a version for it.

This isn't the "enable/disable" you asked for. You asked for both, and what you get is one of them
automatically and none of the other.
```

**This is the template for D-10** (concede attribution fully; the three datasheet defects stay stated as
unfixed, with their measured values) and for **D-11's honest limit** on gh#23 (v1.36 did not and cannot make
the tool see an unhooked VPP).

**The re-run ask + install block** (`152-GH12-COMMENT.md`, tail) — the literal shape REPLY-05/D-17 attaches to:

```
I know this is the second time in a row I'm asking you to install a fresh pre-release and run
`dev test` on this thread — the last time pointed at a build whose reports couldn't say which
firmware they'd run on … I'd rather say that plainly than pretend this is the first ask.

```
pip install --pre firestarter
firestarter fw --install
firestarter dev test <chip>
```
```

Note 152 also carried a `152-GH{N}-COMMENT.diff` beside the body (`152-GH11-COMMENT.diff`, 1,181 B) —
a unified diff of the operator's amendment against the pre-approval draft, generated with `diff` against a
scratchpad copy. **Use this when an operator amends a body at the D-16 gate**; it is how 152 proved the
amendment's exact scope. Example (`152-GH11-COMMENT.diff:1-3`):

```
--- /tmp/.../scratchpad/GH11.pre.md	2026-08-21 18:32:16 +0000
+++ 152-GH11-COMMENT.md	2026-08-21 18:32:16 +0000
@@ -68,9 +68,10 @@
```

---

### `187-UPSTREAM-REPLIES.md` — the review/approval document (state-machine document)

**Analog:** `.planning/milestones/v1.35-phases/173-close-beta-cut-under-protection-close-procedure-honesty-ledg/173-UPSTREAM-REPLIES.md` (12,839 B)

**Header block, verbatim shape** (`:1-16`) — note the **`**D-13 review status:**` literal is the gate**:

```markdown
# Phase 173 Plan 04: Upstream Replies — Drafted for Operator Review

**Date:** 2026-09-02
**Requirement / criterion:** POLICY-04's home phase is Phase 173; this record serves Phase 173's
criterion 5 — "…" — widened per Context D-12 to include gh#6 as well.
**D-13 review status:** APPROVED AND POSTED
**Approved by:** Henrik Olsson, 2026-09-02 (see `evidence/173-07-operator-approval.txt`)

Per D-13 …: these four bodies are drafted here for a blocking
operator wording review before a word of them is public. Plan 173-07 is the only plan permitted
to post them, and only after this status line reads something other than the pending-review
literal it started at. Each body below is stored a second time, byte-identical, as its own file
under `evidence/bodies/173-gh<n>.md` — that is the file plan 173-07 passes to `gh issue comment
--body-file` unmodified, so what the operator approves here is exactly what gets posted.
```

**Section order (copy exactly):**
1. `## Operator Review (D-13 blocking wording review)` — records the verdict **and explicitly flags that it
   is the orchestrator's rendering of a menu selection, not a verbatim operator quotation.**
2. `## Dispositions` — a three-column table, written *before* any body:

```markdown
| Issue | Title | Disposition |
|---|---|---|
| [gh#5](https://github.com/henols/firestarter_prom/issues/5) | Move documentation | Reply, stays open — surviving tracker for FUT-W-01 through FUT-W-05 |
| [gh#6](…/issues/6) | Protect main branches … | Reply, then close |
| [gh#9](…/issues/9) | Repository Structure and Contribution Guide | Reply, stays open, gets pinned |
```

3. `## Pre-post state (before-half; see `evidence/173-04-issue-state-before.json`)` — prose stating what was
   confirmed from the API before drafting **and that it was re-read a second time after drafting**.
4. One `## gh#N — <title>` section per issue, each carrying:

```markdown
## gh#5 — Move documentation

**Body file:** `evidence/bodies/173-gh5.md`
**Posted:** https://github.com/henols/firestarter_prom/issues/5#issuecomment-5511486703

```
<the body, inline, byte-identical to the file>
```
```

(For a closed issue the Posted line carries the close stamp too:
`…#issuecomment-5511486995 (issue closed 2026-09-02T14:50:52Z)` — this is gh#60's shape under D-15.)

**187 variance from the analog:** 173 approved four bodies in one approval. **D-16 requires a per-issue
blocking gate**, so the status line must be per-issue (a row or a line per issue), not a single document-level
literal. 152's D-03 is the precedent for the per-artifact split; 173 supplies the document shape.

---

### `evidence/187-operator-approval.txt` — the hash-bound approval gate (file-I/O + sha256)

**Analog:** `.../173-.../evidence/173-07-operator-approval.txt` — **yes, the bodies were hash-bound in an
approval file before posting.** Full shape:

```
APPROVED-FOR-POST: gh5 gh6 gh7 gh9

Operator: Henrik Olsson
Date: 2026-09-02

Decision (D-13 blocking wording review): the orchestrator presented all four drafted bodies
(evidence/bodies/173-gh5.md, …) to the operator in full and verbatim, together with the disposition
each implies (…). This sentence is the orchestrator's rendering of the operator's menu selection plus
its option description, not a verbatim quotation: the operator selected "Approve, strengthen gh#6" —
approve all four for posting exactly as drafted, on the condition that gh#6's third "Delivered" bullet
is amended first to cite the performed push rejected by GH013 …, with every other byte of all four
bodies left unchanged.

The amendment described above has already been applied to evidence/bodies/173-gh6.md and to the
gh#6 body copy inside 173-UPSTREAM-REPLIES.md before this approval file was written, so the four
sha256 hashes below are computed over the bodies exactly as approved and exactly as they will be posted.

sha256(evidence/bodies/173-gh5.md) = ea0b21158729b9c1c45d7b0dde320c8efdb0181a318b2c45a7f5725d55618c50
sha256(evidence/bodies/173-gh6.md) = 49f4a2a645d95ccfde0d13d883f609a7989b99cfa2b4b2969c2527900ce873d3
sha256(evidence/bodies/173-gh7.md) = c6ae994f0bbd71f20c3c05c88fc57df2babe60a507514bcb7d8bec7e9120b2c3
sha256(evidence/bodies/173-gh9.md) = 0db65fe80d52497b0f78fcb281bd96d8ae5d62e47947fdb6cd5d4789b0c6fe95
```

**Four load-bearing properties a plan must reproduce:**
1. An **approval literal on line 1** (`APPROVED-FOR-POST: …`) that the posting plan's gate asserts.
2. Operator name + date.
3. The decision prose explicitly labelled as a **rendering of a menu selection, not a quotation.**
4. **One `sha256(...) = ...` line per body, computed after any amendment**, with a sentence stating the
   hashes cover the bodies as approved and as they will be posted.

Under D-16 this becomes **five approval files** (or five stanzas each with their own literal), one per
issue, plus separate ones per merge — 173 already had five distinct approval files in the same phase
(`173-03`, `173-05`, `173-06`, `173-07`, `173-09`), one per public act.

Generation command (RESEARCH § Code Examples):

```bash
cd /workspaces/.planning/phases/187-answered-reports
for F in evidence/bodies/187-gh*.md; do
  printf 'sha256(%s) = %s\n' "$F" "$(sha256sum "$F" | cut -d' ' -f1)"
done >> evidence/187-operator-approval.txt
```

---

### `.planning/notes/<name>.md` — the D-09 verdict + reply-ledger record (document)

**Analogs (four consecutive phases, all tracked):**
- 182 — `.planning/notes/jumper-display-ground-truth.md` (279 lines)
- 183 — `.planning/notes/ae29f2008-classification-verdict.md` (13,552 B)
- 184 — `.planning/notes/dispatch-invariant-retirement-verdict.md` (18,553 B)
- 185 — `.planning/notes/catalog-sync-check-retirement.md` (15,056 B)
- 186 — `.planning/notes/python-floor-decision.md` (9,790 B)

**YAML frontmatter — three keys, always** (`ae29f2008-classification-verdict.md:1-5`):

```markdown
---
title: AE29F2008 classification verdict — algorithm 5 is correct, and gh#62 is correct too
date: 2026-09-11
context: v1.37 Phase 183, SAFE-09 — re-verified in this session against 183-RESEARCH.md §B
---

# AE29F2008 classification verdict (SAFE-09)
```

`dispatch-invariant-retirement-verdict.md:1-9` shows the multi-line `context:` form (phase, requirement ID,
what was measured and against what). **The `title:` states the verdict itself**, not a topic.

**Section skeleton — the recurring spine across 183/184/185:**

```
## THE VERDICT      ← bolded one-paragraph answer first; 186 uses "## VERDICT"
## THE GROUNDS      ← 184 only
## THE EVIDENCE CHAIN
## <a named sub-verdict, SHOUTED>   e.g. "WHY THE REPORTER'S `--force` ERASE WORKED, AND WHY THAT IS NOT A LICENCE"
## <decision ID>, SETTLED / ## <decision ID>, RECORDED
## WHAT THIS PHASE DID NOT DO, AND WHY (D-NN)
## WHAT THE DELETED FIXTURES PROVED / ## THE DRIFT, MEASURED AND NOT ADJUDICATED
## <backlogged-but-not-built item> — recorded, backlogged, not built (D-NN)
## Summary of backlog items this verdict generates
```

186's variant numbers its middle sections (`## 1. The decision, and the three rejected alternatives`,
`## 2. The evidence`, `## 3. The standing rule`, `## 4. The successor: …`, `## 5. The residual gap, named
explicitly`) — the better fit if 187's document is more ledger than verdict.

**187's document must carry both halves** (D-09): the gh#9 staleness finding (comment URL
`#issuecomment-5511487546`, the eight-day window, what was false and where) **and** a per-issue reply ledger
— body posted, permalink, app + firmware versions named, label moved, closed vs. deliberately left open.
Use `dispatch-invariant-retirement-verdict.md`'s `## THE DRIFT, MEASURED AND NOT ADJUDICATED` as the model
for the staleness finding, and a table for the ledger.

**D-08 constraint, and its precedent in these same files:** 183/184/185 all end with a
`## Summary of backlog items this verdict generates` section. **187's equivalent must state that it
generates zero** — say so explicitly, per 184 D-05/D-06 and 185 D-04's "name it, file nothing" branch, so no
later reader reads the absent section as an omission.

**Anchor caution (RESEARCH §7.2):** these headings contain backticks, em-dashes and `#` inside `gh#60`.
Do not hand-derive GitHub anchor slugs. After the meta merge, confirm the file at the pinned SHA with
`gh api ".../contents/<path>?ref=$SHA"` and copy the anchor GitHub actually renders.

---

### Record repairs 1–2 — stale ROADMAP prose (in-place factual correction)

**Targets:** `.planning/ROADMAP.md:5409-5411` (*"what it needs is a closing reply or a close-as-done"*) and
`:5424` (*"gh#9 still owes a closing reply"*).

**Analog:** `.planning/ROADMAP.md:51` (v1.32 evidence-ceiling sentence) — the pattern is **do not silently
rewrite; append a dated AMENDED clause naming the source decision, the measured truth, and why the original
was already false when written:**

```markdown
**AMENDED 2026-08-21 (152-CONTEXT.md D-05):** this sentence previously also listed gh#32 as OPEN.
gh#32 was CLOSED 2026-08-08, `stateReason: COMPLETED`, folded into gh#21 by the operator's own
comment — "…" — ten days before v1.32 opened, so the sentence was already false when written.
```

`:5424` is a checklist line (`- [x] Shipped as **v1.35 Phases 172–173** … gh#9 still owes a closing reply.`)
— the trailing clause is what is false; replace it with the discharged state and the comment URL, carrying
the same AMENDED-with-reason form.

**Scope gate (D-07), restate in the plan:** `ROADMAP.md:967` and `:1224` are **NOT** repaired (both now
literally true), and every hit under `.planning/milestones/` (10 files) is historical-by-intent and never
repaired. Precedent for stopping: Phase 184's D-01.

---

### Record repair 3 — `.planning/ROADMAP.md:502`, Phase 187 success criterion 4 (**amended**)

**Current text** (`ROADMAP.md:502`): `4. gh#9 carries a closing reply or is closed as done.`

**Analogs — what an amended success criterion actually looks like on disk:**

`ROADMAP.md:321-325` (Phase 183 D-08) — amendment appended *inside the numbered item*, in bold, naming the
phase and decision, then the measured reason, then what is preserved:

```markdown
2. All three candidate mechanisms carry a firmware-flash figure … and the record states the grounds the
   choice was actually made on. **AMENDED by Phase 183 alongside criterion 1 (D-08):** the original wording
   said "both" of two mechanisms and that the choice cites those figures. Pricing found no flash cliff (M1
   is +12 B on every target), so the figures did not decide it; M3 was chosen on D-02 grounds … The
   measurement is not dropped, it is simply not the deciding evidence, and `183-01-SUMMARY.md` says so on
   the record.
```

`ROADMAP.md:363-368` (Phase 184 D-03) — same form, for an unrunnable command:

```markdown
1. `git grep -n 'dispatch_mirror' -- . ':(exclude).planning'` returns nothing in all three repositories.
   **AMENDED by Phase 184 alongside the code (D-03):** the operative check is that no file in any of the
   three repositories names `tools/wiki/dispatch_mirror.py` as a live guard, verified by
   `git grep -n 'tools/wiki/dispatch_mirror' -- . ':(exclude).planning'` returning nothing in all three. The
   original bare-substring command could not be used as written: `dispatch_mirror` collides across two …
```

`ROADMAP.md:2176` (v1.32) — the fullest form, which additionally retains the pre-amendment wording as the
negative case a gate must catch, and names the rejected alternatives:

```markdown
1. **AMENDED 2026-08-20 (Phase 150 deferral).** … *(This criterion previously read "…". That was written
   when Phase 150 was in scope; it is now the exact overclaim v1.30 Phase 137 had to amend CLOSE-05/CLOSE-06
   to avoid, and it is retained here only as the negative case the gate in criterion 5 must catch.)*
```

**Four elements every one of these carries — reproduce all four:**
(a) the original wording **kept** or quoted, never deleted; (b) `**AMENDED by Phase NNN … (D-NN):**` naming
phase and decision; (c) the measured reason the original is wrong; (d) where the substance went instead.

**⚠ Write these by hand.** `roadmap.update-plan-progress` clobbers the dependency table (positional
overwrite kills phase name + req IDs), and the requirements/roadmap verbs reformat the whole file.

---

### Record repair 4 — `.planning/REQUIREMENTS.md:118`, REPLY-07 (**amended**, marked Complete)

**Current text** (`REQUIREMENTS.md:118-119`):

```markdown
- [ ] **REPLY-07**: gh#9 (`Repository Structure and Contribution Guide`) receives a closing reply or a
      close-as-done — the end-state it describes has been configured since v1.35 Phase 172.
```

**Analog — `REQUIREMENTS.md:74-80` (SAFE-06, Phase 183 D-07/D-08).** This is the canonical amended-requirement
shape: checkbox flipped to `[x]`, original text intact, then a bold AMENDED clause carrying the conflict,
the fact the conflict was stated *before* the choice, where the substance moved, and a trace:

```markdown
- [x] **SAFE-06**: A refusal to erase a flash4 (`0x05`) part names the part — instead of a bare `Not
      supported` — and does not carry a cause or an alternative in the CLI text. **AMENDED by Phase 183
      under D-07/D-08:** the operator chose this one-line shape knowingly, with the conflict against this
      requirement's original wording — which had promised the refusal state its cause and its alternative —
      stated on the record before the choice was made. The cause and the alternative are not dropped; they
      move to Phase 187's REPLY-03 (D-09), which answers gh#62 directly instead of printing the answer into
      a tool every operator sees. Trace: `183-03-SUMMARY.md`; shipped …
```

**Analog — `REQUIREMENTS.md:144-150` (CLAIM-08, Phase 185 D-02).** The nearest match to REPLY-07's situation
(a requirement unsatisfiable/already-discharged as written), including an **explicit precedent citation**:

```markdown
      … Unsatisfiable as written, for two independent reasons: (1) Phase
      185 deletes the workflow on the operator's own decision (D-01), and once it is deleted no run on `main`
      can exist at all; (2) `main` is protected in all three repositories and nothing this phase does lands
      there. AMENDED (D-02) to: the check is retired, and the cause of its standing failure is recorded in
      `.planning/notes/catalog-sync-check-retirement.md`. Precedent for amending in the same phase as the
      work: Phase 183's D-08 (SAFE-06 amended alongside the code) and Phase 184's D-03 (criterion 1 amended).
```

**REPLY-07's amendment copies CLAIM-08 most closely:** state that it was discharged by
`#issuecomment-5511487546` on 2026-09-02 (eight days before REPLY-07 was filed 2026-09-10), that gh#9 stays
open and pinned as the deliberate configured end state, cite the byte-identical body at
`.planning/milestones/v1.35-phases/173-…/evidence/bodies/173-gh9.md` and `173-07-SUMMARY.md:115-118`, and
name the 183/184/185 precedent chain by phase number exactly as CLAIM-08 does.

**D-11 also uses this pattern** for REPLY-01's wording (the `chip_test.py:2599` / `diagnostic_report.py:55-68`
measurement makes the literal wording an overclaim) — same four elements, same file.

---

### Record repair 5 — `.planning/REQUIREMENTS.md:217`, the REPLY-07 traceability row

**Current:** `| REPLY-07 | Phase 187 | Pending |`

**Analog — `REQUIREMENTS.md:195-200`.** The Status cell is never bare `Complete`; it carries the disposition,
the amendment if any, and a plan-number trace in parentheses:

```markdown
| SAFE-06 | Phase 183 | Complete — amended to D-07's one-line refusal (183-06); trace 183-03 |
| SAFE-09 | Phase 183 | Complete — equivalence-based verdict recorded (183-02) |
| CLAIM-01 | Phase 184 | Complete — repaired in all three repos; criterion 1 amended by D-03 (184-05), three D-02 citations kept and re-dated (184-04) |
| CLAIM-02 | Phase 184 | Complete — both fixtures deleted (184-04); their fail-open finding preserved in notes/dispatch-invariant-retirement-verdict.md first (184-03) |
```

REPLY-07's cell should read in that register: `Complete — discharged by #issuecomment-5511487546 (2026-09-02,
Phase 173-07); amended by D-06/D-07 (187-NN)`. The other six REPLY rows (`:211-216`) follow the same form as
they complete.

---

### `evidence/` — the phase evidence tree (evidence capture)

**Analog:** `.planning/milestones/v1.35-phases/173-…/evidence/` — 32 files + `bodies/`. Layout, verbatim:

```
evidence/
  bodies/173-gh5.md  173-gh6.md  173-gh7.md  173-gh9.md     ← the --body-file payloads
  173-04-issue-state-before.json                            ← API read, before drafting
  173-07-operator-approval.txt                              ← literal + name + date + sha256 per body
  173-07-post-transcript.txt                                ← one block per issue
  173-07-issue-state-after.json                             ← reconciled field-by-field vs. before
  173-04-draft-link-check.txt                               ← every link in every draft, resolved
  173-03-operator-approval.txt  173-05-… 173-06-… 173-09-…  ← one approval file per public act
  173-03-rulesets-before.json / -after.json                 ← before/after for a config change
  173-09-beta-cut.txt  173-05-push-transcript.txt  173-09-gitlink-equality.txt
```

**Naming rule:** `<phase>-<plan##>-<what>.<ext>`, and bodies live one level down in `bodies/` named
`<phase>-gh<n>.md` (lowercase `gh`, no dash before the number).

**Transcript shape** (`173-07-post-transcript.txt`, one block per issue):

```
Command: gh issue comment 9 --repo henols/firestarter_prom --body-file .planning/phases/173-…/evidence/bodies/173-gh9.md
Exit code: 0
Returned URL: https://github.com/henols/firestarter_prom/issues/9#issuecomment-5511487546
```

**187 additions the analog does not have:** cut-version reads (`gh release list` after
`beta-release.yml` / `beta-build.yml`) and the pinned-permalink SHA record. Both belong in
`187-MERGE-RECORD.md` (below), whose analog does carry them.

---

### `187-MERGE-RECORD.md` — the three PRs and two cuts (ship record)

**Analog:** `.planning/milestones/v1.32-phases/152-…/152-MERGE-RECORD.md` (13,674 B). Section list, verbatim:

```
# 152-MERGE-RECORD.md — the beta-merge handoff record for `/gsd-complete-milestone`
## 1. The three pull requests
## 2. `git cherry`, per sub-repo, captured AFTER the merge
## 3. The two observed cut tags
## 4. The registry confirmation, read directly from the registry
## 5. The post-merge published-branch SHA per sub-repo, and the intended future gitlink
## 6. The instruction
## Notes for the milestone close
## ⚠ TAIL — commits made to the meta repository AFTER PR #38 merged, which are NOT on `beta`
```

Sections 2–4 are exactly D-05's "read, never predict" discipline (`git cherry` after the merge; cut tags
observed; PyPI registry read independently of GitHub). **Section 5 is where 187 records the 40-char meta
merge SHA every D-13 permalink pins** — RESEARCH §7.3 makes that SHA a correctness precondition, not
bookkeeping. **The `⚠ TAIL` section is D-03's disclosure** (187's own tail lands on the milestone branch,
not `beta`).

Optional sibling: `152-LEDGER.md`'s `## The amendment register` (`:194`) is the model if the planner wants
the five D-07 repairs registered in one place rather than only inline.

---

## Shared Patterns

### Posting — the command, and the read-back that does not false-alarm
**Source:** `.../173-…/evidence/173-07-post-transcript.txt`; `.claude/skills/devtest-triage/SKILL.md:345-349`;
`.claude/skills/devtest-rootcause/SKILL.md:336`
**Apply to:** all five reply bodies

```bash
N=23; F=evidence/bodies/187-gh23.md
URL=$(gh issue comment "$N" --repo henols/firestarter_prom --body-file "$F")
ID=${URL##*-}
gh api "repos/henols/firestarter_prom/issues/comments/$ID" > /tmp/c.json
python3 -c "
import json,hashlib,sys
b=json.load(open('/tmp/c.json'))['body'].encode(); d=open(sys.argv[1],'rb').read()
print('api ',len(b),hashlib.sha256(b).hexdigest())
print('disk',len(d),hashlib.sha256(d).hexdigest())
print('BYTE-IDENTICAL' if b==d else 'MISMATCH'); sys.exit(0 if b==d else 1)" "$F"
```

**⚠ Never write the naive `gh api --jq '.body' | diff` leg.** `jq` appends its own trailing newline and the
diff reports a spurious extra blank line on a perfectly correct post — the most expensive possible false
alarm in an operator-gated phase (RESEARCH §6.4). Never interpolate body text onto the command line.

### No-collateral-post proof
**Source:** RESEARCH §6.5 (Phase 173's *corrected* leg — 173's own plan shipped a version of this that
asserted zero comments on every non-target issue, which was never true of a repo where 39 of 53 issues
already carried comments)
**Apply to:** the posting plan's verify block

```bash
WINDOW_START=$(date -u +%Y-%m-%dT%H:%M:%SZ)   # capture BEFORE the first post
gh api repos/henols/firestarter_prom/issues/comments --paginate \
  --jq ".[] | select(.created_at >= \"$WINDOW_START\") | {issue:(.issue_url|split(\"/\")|last),created_at,id}"
# expect exactly one row per targeted issue, and nothing else
```

### Before/after issue-state capture
**Source:** `.../173-…/evidence/173-04-issue-state-before.json`, `173-07-issue-state-after.json`
**Apply to:** the drafting plan (before) and the posting plan (after); reconcile field-by-field

```bash
for N in 9 23 28 31 60 62; do
  gh issue view $N --repo henols/firestarter_prom \
    --json number,title,state,stateReason,labels,comments \
    --jq '{n:.number,state:.state,reason:.stateReason,labels:[.labels[].name],ncomments:(.comments|length)}'
done > evidence/187-issue-state-before.json
gh api graphql -f query='{repository(owner:"henols",name:"firestarter_prom"){
  pinnedIssues(first:10){totalCount nodes{issue{number}}}}}' >> evidence/187-issue-state-before.json
```

The `pinnedIssues` leg is D-06's verification only — 187 does **not** call `pinIssue`.

### Permalinks
**Source:** RESEARCH §7.2/§7.3
**Apply to:** every `.planning/notes/` link in every body

```
https://github.com/henols/firestarter_prom/blob/<40-char-commit-sha>/<path>#<anchor>
```

Never `blob/beta/…` (moves on every merge *and* every CI version bump), never `main` (lags). Get the SHA
after the meta merge: `git fetch origin && git rev-parse origin/beta`, or
`gh pr view <N> --json mergeCommit`. **DRIFT-3 makes this a correctness gate, not style:**
`jumper-display-ground-truth.md` exists on `beta` today as a 76-line stub *without* REPLY-04's section, so a
pre-merge SHA yields a link that silently resolves to the wrong content.

### Reading the cut, never predicting it
**Source:** `152-MERGE-RECORD.md` §§2-4; RESEARCH § Code Examples
**Apply to:** the merge plan and every reply naming a version

```bash
export XDG_CACHE_HOME=/tmp/gh-cache; mkdir -p "$XDG_CACHE_HOME"   # gh run/log needs this
gh release list --repo henols/firestarter_app --limit 3
gh release list --repo henols/firestarter    --limit 3
curl -s https://pypi.org/pypi/firestarter/json \
 | python3 -c "import json,sys;d=json.load(sys.stdin);print(sorted(d['releases'])[-3:])"
```

**⚠ Workflow filenames differ (DRIFT-1):** app = `beta-release.yml`, **firmware = `beta-build.yml`.** A verify
leg grepping for `beta-release.yml` in the firmware repo fails open or wastes a cycle.

### Operator-gate literals (D-16)
**Source:** `173-07-operator-approval.txt`; `152-CONTEXT.md` D-03
**Apply to:** every plan touching a public act — five posts, three merges

One approval file per act, each with its own approval literal on line 1, so approval for one issue cannot
carry to another. Every such plan carries `autonomous: false`, **and** the phase is never dispatched under
`--auto`/`--chain` — those modes auto-approve human-verify gates and `autonomous: false` is not
self-protecting. 152 shipped `152-check-not-auto.py` (8,004 B) as a machine check of exactly this; it is
available as a starting point if the planner wants criterion 5 mechanically provable.

### Never-do list for the record repairs
- **No `<!--` bare HTML comment anywhere in a PLAN.md** — it swallows the frontmatter's closing `---` and
  breaks the decision-coverage gate.
- **D-NN decision labels must be single-line bullets** or the decision-coverage gate fails closed.
- `grep` in this devcontainer is ugrep and honors `.gitignore` — use `/usr/bin/grep` for any evidence leg.
- `ROADMAP.md` (930 KB) and `STATE.md` (510 KB) are never bare-read; `sed -n` a range or grep a heading.
- Revert the `.planning/config.json` `sub_repos` prune (DRIFT-4) with `git checkout --`; never
  `git clean -Xdf` (destroys `.planning/state.json` and bench `.bin` files).
- `.planning/config.json` sets `git.create_tag: true`, which contradicts D-04 — the tag step must be
  explicitly skipped.

---

## No Analog Found

None. Every artifact in this phase has a named in-repo precedent.

The two places where the analog needs **adaptation** rather than copying:

| Artifact | Adaptation required |
|---|---|
| `187-UPSTREAM-REPLIES.md` review-status line | 173 used one document-level status literal for four bodies. D-16 requires a **per-issue** blocking gate; split the literal per issue (152 D-03's per-artifact shape applied to 173's document). |
| The `.planning/notes/` document | 182–186 are all single-subject *verdicts*. 187's carries a verdict (gh#9 staleness) **plus** a per-issue posting ledger. Use 186's numbered-section variant, and state explicitly that it generates **zero** backlog items (D-08) where its predecessors carry `## Summary of backlog items this verdict generates`. |

---

## Metadata

**Analog search scope:** `/workspaces/.planning/milestones/v1.32-phases/152-outward-facing-close-operator-gated/`,
`/workspaces/.planning/milestones/v1.35-phases/173-close-beta-cut-under-protection-close-procedure-honesty-ledg/`
(incl. `evidence/`), `/workspaces/.planning/notes/` (31 entries), `/workspaces/.planning/ROADMAP.md`
(targeted `sed -n` ranges only), `/workspaces/.planning/REQUIREMENTS.md`
**Files scanned:** ~30 (7 read in substance)
**Tracked-source verification:** `git ls-files` over all six primary analog paths → 6/6 tracked
**Pattern extraction date:** 2026-09-12
