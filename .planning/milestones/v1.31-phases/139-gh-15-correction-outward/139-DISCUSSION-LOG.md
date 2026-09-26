# Phase 139: gh#15 Correction (outward) - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-08-09
**Phase:** 139-gh#15 Correction (outward)
**Areas discussed:** Amendment mechanism, Amendment scope, Evidence depth, Posting gate & unblock,
gh#12 todo folding

---

## Facts measured live during this discussion (not restated from prior artifacts)

These three findings shaped every decision below and were verified in-session:

| Finding | Method | Consequence |
|---|---|---|
| **gh#15 was filed by the operator himself** (`author: henols`, created 2026-07-12, **zero comments**) | `gh issue view 15 --json author,createdAt,comments` | Editing the issue body is available in a way it is not on a stranger's issue → makes D-01 a real choice; also fixes the comment's voice as self-correction (D-02) |
| **`henols/firestarter_prom` is PUBLIC and carries `.planning/`** on `main` and the pushed v1.31 branch | `gh repo view --json visibility`; `git ls-tree origin/main` | `.planning/` evidence is legitimately citable by a stranger → D-06/D-07 can link planning artifacts, not just sub-repo source |
| **Six meta commits are unpushed; `138-BASELINE.md` does not resolve at the pushed tip `b6aa1dcb`** (it landed in `baa131a3`) | `git branch -r --contains`; `git cat-file -e b6aa1dcb:<path>` per citation target | Permalink reachability becomes a hard **posting precondition** (D-07), not a cleanup step |

Also confirmed in-session and reused as citations: `firestarter/src/proms/eprom.cpp` is untouched
(`git status --porcelain` empty — D-10's baseline), and C1's ×100 BUG-2 removal is commit `8de307f`
with the DB regeneration at `12286df` in `firestarter_app`.

---

## Amendment mechanism

| Option | Description | Selected |
|--------|-------------|----------|
| Comment only | Satisfies ISSUE-01/02/03 literally; a stranger reading only the issue body never sees it | |
| Comment + optional frozen body edit | Both drafted and frozen; body edit offered at the same gate, **skipped by default**, original acceptance list preserved verbatim in `<details>` | ✓ |
| Comment + body edit by default | Strongest visibility, but adds an outward act beyond what ISSUE-01…03 ask for | |

**User's choice:** Delegated — *"you decide, do the best decisions to finalize the EPROM protocols."*
**Notes:** Decided as **D-01**. The deciding argument: a stranger or an agent implements from the
*body*, not the comments, and stopping exactly that is D-03's stated purpose ("Stops anyone
implementing `50000 us`"). But rewriting a filed spec without the original visible destroys the public
record, and an outward action beyond the requirements must not happen by default — hence drafted and
frozen (so it can never be improvised at the gate), offered, and default-skipped.

---

## Amendment scope

| Option | Description | Selected |
|--------|-------------|----------|
| Numbers only | C1/C2/C3 + the delay-helper premise; leave gh#15's separate-handlers architecture standing | |
| Full amendment | Rewritten acceptance-criteria list mapped item-for-item onto gh#15's original seven boxes, incl. **replacing** "each protocol must own its state machine and timing constants" | ✓ |

**User's choice:** Delegated.
**Notes:** Decided as **D-03**, reinforced by the operator's framing *"finalize the EPROM protocols."*
Four of gh#15's seven acceptance boxes conflict with the corrected design, not two. Leaving the
architecture criterion uncontested would force Phase 146's CLOSE-04 to mark three or four boxes
"met-as-corrected" against a spec that was never publicly corrected — the exact overclaim shape this
milestone's claim gate exists to prevent. Half-correcting is worse than not correcting, because it
looks complete. Paired with **D-04**: publish the table's *shape*, mark every numeric row **proposed**,
because per-value datasheet attribution is TABLE-04's job and does not exist yet.

---

## Evidence depth & citation form

| Option | Description | Selected |
|--------|-------------|----------|
| Full verbatim PREP-04 dump inline | Maximum reproducibility; hundreds of lines incl. the planted-failure run — buries the correction | |
| Condensed histogram inline + permalinked artifact and runnable script | The payload inline, full evidence one click away, every claim carrying `file:line` or a commit SHA | ✓ |
| Link-only | Shortest; fails ISSUE-01's "each claim cited" test for a reader who does not click | |

**User's choice:** Delegated.
**Notes:** Decided as **D-06**. Citation form settled separately as **D-07**: pin to commit SHAs,
never branch names, and *verify each permalink resolves before posting* — driven by the measured
finding that `138-BASELINE.md` currently 404s at the pushed tip. A correction whose evidence 404s
reads as fabricated.

---

## Posting gate & what unblocks Phase 140

| Option | Description | Selected |
|--------|-------------|----------|
| Hard block on the post landing | Literal roadmap reading; risks deadlocking the milestone on one authorization the operator may be away from | |
| Gate is the wording review; posting is the default outcome | Phase 140 never starts against an *unreviewed* draft; approve-but-hold allows 140 to proceed under a **recorded, named exception**, ISSUE-03 stays open | ✓ |
| Frozen draft alone is enough | Weakest — allows implementation against text nobody read | |

**User's choice:** Delegated.
**Notes:** Decided as **D-08**. The guarantee worth enforcing is *reviewed*, not *transmitted*.
v1.30's CLOSE-06 was held open for a **shipping event** outside anyone's control; this blocker is a
single authorization, which does not justify a deadlock. Supported by **D-09** (`checkpoint:human-action`,
never `human-verify` — auto-modes approve the latter and never the former; the `autonomous: false`
frontmatter flag alone is not self-protecting) and **D-10** (mechanically re-verify `eprom.cpp` is
untouched at posting time; byte-diff the posted comment back against the frozen file).

---

## Community ask (raised by Claude, not offered as a menu option)

Not presented as a gray area — added during analysis and decided as **D-11**. The `0x0B`
one-shot-vs-looped question is *not answerable from source* (minipro never runs the algorithm; it
hands `pulse_delay` to closed TL866/T48/T56/T76 firmware), so the milestone's 50 ms energy cap is
**reasoned, not derived** — and the comment must say so and invite correction. Bounded to four lines,
mirroring `137-GH12-COMMENT.md`'s close, so a correction does not turn into a solicitation.

---

## gh#12 todo folding

| Option | Description | Selected |
|--------|-------------|----------|
| No — reviewed, not folded | Different issue, different milestone's requirement (v1.30 CLOSE-06); folding puts a v1.30 deliverable in a v1.31 requirement set | ✓ |
| Yes — same-sitting operator batch | Same machinery, same gate, genuinely unblocked now | |

**User's choice:** *No — reviewed, not folded (Recommended).*
**Notes:** Its blocker **is** now satisfied (the `dev sdp` removal shipped with the v1.30 merge; app
`beta` at `3.0.0b20`) and its frozen text sits at `137-GH12-COMMENT.md` awaiting the single command in
`.planning/v1.30-OPERATOR-BATCH.md` §A-1. Recorded in CONTEXT.md's deferred section so it is not lost
a second time.

---

## Claude's Discretion

The operator delegated **all four** gray areas — *"you decide, do the best decisions to finalize the
EPROM protocols."* Every decision D-01…D-11 in CONTEXT.md is therefore Claude's call, made against the
locked milestone record in `PROJECT.md` §v1.31 and the facts measured above. They are recorded as
decisions, not suggestions: downstream agents implement them rather than re-open them.

Latitude deliberately left to the planner and executor:

- Exact comment prose, section order, and headings.
- Checklist vs. table rendering for the corrected acceptance-criteria list.
- Whether the frozen comment gets a byte-identity gate of its own, or relies on the blob-SHA +
  byte-length freeze plus the post-hoc byte-diff (already two independent mechanisms).
- Plan and wave structure — the natural shape maps 1:1 onto `137-05-PLAN.md`'s three tasks.
- Artifact file names and locations, subject to the `137-GH12-COMMENT.md` naming precedent.

## Deferred Ideas

- Per-value datasheet attribution for the parameter table → **TABLE-04, Phase 140**.
- Item-by-item reconciliation of gh#15's acceptance criteria → **CLOSE-04, Phase 146**.
- Release notes for the programming-behavior change → **CLOSE-05, Phase 146**.
- Building and arming the claim gate → **CLOSE-01, Phase 146**. Phase 139 *complies* with its
  forbidden-claim list but does not build it.
- The gh#12 reply and the five other reviewed-but-unfolded todos → itemized in CONTEXT.md
  `<deferred>`.

**No checkpoint file was written.** The discussion completed in a single turn with full delegation,
so an incremental checkpoint would have been created and deleted in the same breath with no
interruption-recovery value. CONTEXT.md is the canonical record.
