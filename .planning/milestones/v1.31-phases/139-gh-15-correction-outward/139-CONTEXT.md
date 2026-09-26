# Phase 139: gh#15 Correction (outward) - Context

**Gathered:** 2026-08-09
**Status:** Ready for planning

<domain>
## Phase Boundary

One public correction on [gh#15](https://github.com/henols/firestarter_prom/issues/15) — C1 (the
500 µs correction and the ×100 BUG-2 fingerprint), C2 (pulse width is a database datum, with the
PREP-04 distribution), C3 (the safe-delay helper's real purpose), the ~6.25 V program-VCC ceiling
stated plainly, and a specific proposed amendment to gh#15's acceptance criteria — **drafted, frozen,
operator-approved for wording, and posted only on explicit operator authorization**, before any
TABLE/LOOP/VPP/HOST implementation work lands code.

**Requirements:** ISSUE-01, ISSUE-02, ISSUE-03.

**This phase is meta-repo-only.** It writes `.planning/` artifacts and makes `gh` calls. It touches
**no** file in `firestarter/` or `firestarter_app/` — those repos are read-only sources of citations
here. `commits_land_in:` is the meta repo; no submodule commit is expected or permitted.

**This phase writes no firmware design.** It *publishes* a design already locked in
`PROJECT.md` §"Current Milestone: v1.31". Phase 139 does not re-decide C1/C2/C3, the table's columns,
the `0x0B` energy cap, or the evidence ceiling — it renders them for a public reader and proposes the
acceptance-criteria amendment they imply.

</domain>

<decisions>
## Implementation Decisions

**Discussion mode:** the operator delegated all four gray areas — *"you decide, do the best decisions
to finalize the EPROM protocols."* Every decision below is Claude's call, made against the locked
milestone record and the facts measured live during this session. They are **decisions, not
suggestions** — downstream agents implement them rather than re-open them. Where a decision
deliberately leaves latitude, it is listed under Claude's Discretion.

### Comment shape & mechanism

- **D-01: One comment is the deliverable; the issue-body edit is a frozen, named, *optional* second
  action offered at the same gate.** ISSUE-01/02/03 speak of "a gh#15 comment", and the comment alone
  discharges all three. But gh#15 was authored by the operator himself (`author: henols`, created
  2026-07-12, **zero comments** — verified live this session), so amending the body is available here
  in a way it never is on a stranger's issue. The plan therefore **drafts and freezes both**:
  (a) the comment, and (b) a ready-to-apply body amendment — a dated `⚠ AMENDED` block at the **top**
  of the body pointing at the comment, plus the acceptance-criteria list replaced by the corrected
  list, with **gh#15's original list preserved verbatim** in a collapsed `<details>` block.
  Both are presented at the single `checkpoint:human-action` gate; **the body edit is skipped by
  default** and applied only on a separate, explicit yes.
  **Rationale:** a stranger — or an agent — who implements gh#15 reads the *body*, not the comments,
  and stopping exactly that is D-03's stated purpose ("Stops anyone implementing `50000 us`"). But
  rewriting a filed spec without the original visible destroys the public record, and an outward
  action beyond what ISSUE-01…03 ask for must never happen by default.
  *Rejected:* comment-only with no body edit even drafted (leaves the strongest fix unavailable at the
  gate, where improvising it would be unreviewed text); body edit as a default action (adds an
  outward, effectively-irreversible act the requirements do not ask for).

- **D-02: Voice carries forward from `137-GH12-COMMENT.md`** — first person, plain-spoken maintainer,
  no hedging, no corporate register. Framed explicitly as **self-correction**: *I filed this; two
  numbers in it are wrong and one premise is inverted.* That framing is honest and available here in
  a way it is not when correcting someone else, and it forecloses any reading of the comment as a
  rebuttal of a contributor.

### Amendment scope

- **D-03: Full amendment — including the architecture criterion, not only the two numbers.** The
  comment proposes a **rewritten acceptance-criteria list mapped item-for-item onto gh#15's original
  seven boxes**, each marked *kept* / *corrected* / *replaced*, with the reason. It states plainly
  that gh#15's *"each protocol must own its programming state machine and timing constants"* is
  **replaced**: protocol owns *shape*, the database owns the *pulse* (milestone D-01) — and gives the
  measured reason, that no protocol has a single pulse width (`0x07` n=170 spans 50–1000 µs;
  `0x08` n=127; `0x0B` n=32).
  **Rationale:** leaving the architecture criterion uncontested would force Phase 146's CLOSE-04 to
  mark three or four acceptance boxes "met-as-corrected" against a public spec that was never
  publicly corrected — precisely the shape this milestone's claim gate exists to prevent.
  Half-correcting a spec is worse than not correcting it, because it looks complete.
  *Rejected:* numbers-only (C1/C2/C3), leaving gh#15's separate-handlers architecture standing.

- **D-04: The comment publishes the corrected design's *shape*, not per-value datasheet
  attributions.** It states the parameter table's columns (`max_pulses`, `overprogram_factor`,
  `overprogram_cap_us`, `verify_mode`, `vpp_path`), the **no-pulse-column** rule,
  `handle->pulse_delay` on every write path with protocol constants surviving only as
  `pulse_delay == 0` fallbacks, the `0x0B` 50 ms accumulated-energy cap with no overpulse, and
  hard-fail-on-max-pulses with address + pulse count reported. **Every numeric row is marked
  proposed** — per-value datasheet citation is TABLE-04's job in Phase 140 and does not exist yet.
  Do not present proposed rows as datasheet-attributed. This is what "finalize the EPROM protocols"
  means at this phase: the public spec becomes unambiguous about *shape*, and honest that the
  *numbers* are still earning their citations.

- **D-05: The comment already complies with the Phase 146 claim gate, before that gate exists.** No
  unqualified "datasheet-conformant" / "datasheet-correct" / "algorithm-accurate". The ~6.25 V
  program-VCC ceiling gets **its own paragraph, not a footnote**, naming what the milestone buys
  (timing / pulse-count / verify fidelity) and what it explicitly does not (silicon-margin fidelity),
  and naming which of gh#15's implied criteria are **not reachable on this hardware**. Check it
  mechanically with `check_permitted_claims.py` — **but read the landmine in Code Insights first**:
  its `_HERE` resolves to the *checker's own* phase directory, so naive cross-phase reuse scans
  nothing and exits 0, a false green.

### Evidence & citation

- **D-06: Condensed evidence inline; full evidence one permalinked click away; every claim carrying
  `file:line` or a commit SHA (ISSUE-01's literal requirement).** Inline: the three per-protocol
  histogram lines and each one's disagreement with gh#15's constant — that is the actual payload.
  **Not** inline: the full `138-02-PULSE-DISTRIBUTION.md` dump, hundreds of lines including the
  planted-failure non-vacuity run, which would bury the correction it exists to support. Citations,
  each resolved before posting:
  - **C1** → `firestarter_app/doc/infoic-field-dictionary.md:210-217` (the adjudication) **plus the
    commits**, found live this session: `8de307f` *"feat(57-01): remove interpret_timing x100
    multiplier and fix bare excepts (DEC-03)"* and `12286df` *"feat(57-03): regenerate
    chip_database.json from corrected build_db.py"*. The ×100 BUG-2 fingerprint cited by commit, not
    by assertion.
  - **C2** → `138-02-PULSE-DISTRIBUTION.md` + the **runnable** `138-pulse-distribution.py` +
    `firestarter_app/firestarter/database.py:128` (`_parse_pulse_duration` — the `pulse_duration`
    string → `pulse-delay` int-µs layer, D-11 of Phase 138) + minipro `t48.c:250-267` for the
    two-orthogonal-wire-fields claim.
  - **C3** → `firestarter/src/proms/eprom.cpp` anchors (`:20` `NUMBER_OF_RETRIES`, `:69-77` the
    `pulse_delay == 0` fallback, `:177` the adaptive growth formula, `:283` the pulse) and
    `delayMicroseconds()`'s 16383 µs ceiling against the `3 × 25 × 1000 µs = 75 ms` overprogram pulse.

- **D-07: Citations pin to commit SHAs, never branch names — and permalink reachability is a hard
  posting precondition, measured rather than assumed.** Verified live this session:
  `henols/firestarter_prom` is **PUBLIC** and carries `.planning/`, so planning artifacts are
  legitimately citable by a stranger. At the currently pushed meta tip **`b6aa1dcb`**,
  `138-02-PULSE-DISTRIBUTION.md` ✓, `138-pulse-distribution.py` ✓ and `PROJECT.md`'s C1/C2/C3 table ✓
  all resolve — but **`138-BASELINE.md` does not**: it landed in `baa131a3`, and six meta commits
  (`baa131a3` … `78904a0e`) are **unpushed at the time of this discussion**. The plan must push the
  v1.31 meta branch (or pin every link to a newer *pushed* SHA), then **fetch each permalink back and
  confirm it resolves** before posting. A correction whose evidence 404s is worse than no correction —
  it reads as fabricated.

### Posting gate & what unblocks Phase 140

- **D-08: The gate is the operator's *wording review*, not the network call.** Phase 140 must never
  start against an **unreviewed** draft — that is the guarantee worth enforcing, and the one the
  sequencing spine actually protects. Posting is the default and expected outcome of the same gate.
  If the operator approves the wording but explicitly says *hold the post*, Phase 140 **may proceed
  under a recorded, named exception** written into both the phase record and the ROADMAP entry, so
  Phase 146's CLOSE-04 reconciles against what actually happened. ISSUE-03 stays **open** in that
  branch, with the exact one-command follow-up recorded in the `.planning/v1.30-OPERATOR-BATCH.md`
  A-1 shape. What must never happen: silently posting, silently skipping, or starting implementation
  against a draft nobody read.
  *Rejected:* hard-blocking the whole milestone on a network call the operator may simply be away
  from. v1.30's CLOSE-06 was held open for a *shipping* event outside anyone's control; this blocker
  is a single authorization, which is a different situation and does not justify a deadlock.

- **D-09: `checkpoint:human-action`, never `checkpoint:human-verify`.** `--auto`/`--chain`
  auto-approve every `human-verify` gate but never `human-action`; the `autonomous: false` frontmatter
  flag alone is **not** self-protecting. Copy `137-05-PLAN.md`'s task shape wholesale — it is a worked,
  proven instance of exactly this gate. **Phase 139 must not be run under `--auto`/`--chain`.**

- **D-10: Posting re-verifies the "before implementation" claim mechanically.** Confirm
  `firestarter/src/proms/eprom.cpp` is untouched at posting time via `git status --porcelain` on the
  file (empty today — verified this session) rather than inferring it from phase order. After any
  post: fetch the comment back and byte-diff it against the frozen file, and confirm gh#15 is still
  `OPEN`. If the body edit was also authorized, read the body back and confirm the original list
  survives verbatim in its `<details>` block.

### Community ask

- **D-11: One short, specific ask — and only one.** The `0x0B` one-shot-vs-looped question is **not
  answerable from source**: minipro never runs the algorithm, it packs `pulse_delay` into a
  `BEGIN_TRANS` message and hands it to closed TL866/T48/T56/T76 firmware — so D-02's 50 ms energy cap
  is *reasoned*, not *derived*, and the comment must say so. Invite a datasheet or logic-analyzer
  correction, and name the parts this milestone cannot guarantee bench coverage for (M2716/M2732 for
  `0x0B`, AM27C020 for `0x08` — opportunistic per the operator's inventory, D-08 of the milestone).
  Four lines, at the end, matching 137's close. A correction that solicits nothing wastes the one
  moment a reader is actually looking at this issue.

### Claude's Discretion

- Exact comment prose, section order, and headings within the decisions above.
- Whether the corrected acceptance-criteria list renders as a markdown checklist or a table.
- Whether the frozen comment gets a byte-identity gate of its own, or relies on the blob-SHA +
  byte-length freeze that `137-05-PLAN.md` used — that freeze plus the post-hoc byte-diff already
  supplies two independent mechanisms.
- Plan and wave structure. The natural shape is three tasks mapping 1:1 onto `137-05-PLAN.md`:
  draft + freeze + verify every permalink resolves → blocking operator gate → conditional
  post-or-hold, each branch recorded.
- Where the frozen artifacts live, subject to the naming precedent (`139-GH15-COMMENT.md` mirrors
  `137-GH12-COMMENT.md`; the body amendment wants its own file so the freeze covers each separately).

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Milestone decision record (locked — do not re-litigate)
- `.planning/PROJECT.md` §"Current Milestone: v1.31 27C Programming-Algorithm Fidelity (gh#15)" —
  lines 69–73 carry the **C1/C2/C3 correction table verbatim**, which is this comment's entire
  substance; also D-01 (protocol owns shape, DB owns pulse), D-02 (`0x0B` energy cap), the 6.25 V
  evidence ceiling, the expected-throughput table, and the asymmetric bench coverage.
- `.planning/ROADMAP.md` §"v1.31 — 27C Programming-Algorithm Fidelity (gh#15)" and §"Phase 139: gh#15
  Correction (outward)" — the four success criteria, the sequencing spine, and the binding
  must-not-do list.
- `.planning/REQUIREMENTS.md` §"gh#15 Correction" lines 111–118 — ISSUE-01, ISSUE-02, ISSUE-03
  verbatim.
- `.planning/seeds/27c-algorithm-fidelity-param-table-refactor.md` — the `/gsd-explore` correction
  pass (commit `c60543c5`) that produced C1/C2/C3.
- https://github.com/henols/firestarter_prom/issues/15 — gh#15 itself. **Author: `henols`
  (the operator). Created 2026-07-12. Zero comments.** Read its seven acceptance-criteria boxes
  before drafting the amendment — four of them conflict with the corrected design.

### The outward-facing precedent to copy (do not reinvent)
- `.planning/phases/137-close-honesty-ledger-claim-gate-gh12-followup/137-05-PLAN.md` — **the worked
  instance of this exact gate.** Three tasks: assemble + freeze; blocking `checkpoint:human-action`
  wording review *and* posting authorization; apply-named-corrections + freeze + conditionally post
  with byte-diff verification. Its threat table (T-137-16 repudiation via `--auto`, T-137-18 a
  dropped follow-up) applies here unchanged.
- `.planning/phases/137-close-honesty-ledger-claim-gate-gh12-followup/137-GH12-COMMENT.md` — the
  **voice** D-02 carries forward, and the community-ask shape D-11 mirrors.
- `.planning/v1.30-OPERATOR-BATCH.md` §A-1 — the record shape for a frozen-but-not-yet-posted
  follow-up, including the exact one-command line to leave behind.

### Evidence being cited (verify each permalink resolves before posting — D-07)
- `.planning/phases/138-preconditions-baseline/138-02-PULSE-DISTRIBUTION.md` — **C2's evidence**,
  deliberately formatted in Phase 138 to be quoted into this comment. Present at pushed tip
  `b6aa1dcb` ✓.
- `.planning/phases/138-preconditions-baseline/138-pulse-distribution.py` — the reproducible script
  a stranger can re-run. Present at `b6aa1dcb` ✓.
- `.planning/phases/138-preconditions-baseline/138-BASELINE.md` — **NOT present at `b6aa1dcb`**
  (landed in unpushed `baa131a3`). Push or re-pin before citing.
- `firestarter_app/doc/infoic-field-dictionary.md:210-217` — where C1's 500 µs adjudication lives.
- `firestarter_app/firestarter/database.py:128` — `_parse_pulse_duration`, the string→int-µs layer
  the comment must not blur (Phase 138 D-11).
- `firestarter/src/proms/eprom.cpp` — C3's anchors: `:20` `NUMBER_OF_RETRIES`, `:69-77` the
  `pulse_delay == 0` fallback, `:177` the adaptive growth formula, `:283` the pulse.
  **Read-only in this phase; `git status --porcelain` on it must stay empty (D-10).**
- Commits `8de307f` and `12286df` in `firestarter_app` — the Phase 57 ×100 BUG-2 removal and the DB
  regeneration that followed it. C1's commit-level citation.

### Claim-gate machinery (reuse with care)
- `.planning/phases/137-close-honesty-ledger-claim-gate-gh12-followup/check_permitted_claims.py` —
  the forbidden-claim checker. **`_HERE` resolves to the checker's own phase directory**: pointing it
  at Phase 139 without repointing `_DEFAULT_TARGETS` scans nothing and exits 0. Repoint or copy;
  never trust an un-exercised pass.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **`137-05-PLAN.md`'s three-task shape** — draft/freeze/verify → blocking `human-action` gate →
  conditional post + byte-diff. It maps onto Phase 139 essentially 1:1, including the branch where
  posting is deferred and recorded as a named follow-up rather than a gap. This phase should copy it,
  not re-derive it.
- **`137-GH12-COMMENT.md`** — a shipped example of the register this project uses in public: states
  what is gone, what survives, what the user asked for and did not get, what genuinely improved, and
  one concrete ask. D-02 and D-11 both derive from it.
- **`138-02-PULSE-DISTRIBUTION.md` + `138-pulse-distribution.py`** — C2's evidence *already exists,
  already proved its own capacity to fail (the planted-failure Run 1), and was already formatted for
  this audience.* Phase 139 quotes and links; it does not re-measure.
- **`.planning/v1.30-OPERATOR-BATCH.md`** — the established place a frozen-but-unposted outward action
  is parked with its exact command, so it cannot silently evaporate.

### Established Patterns
- **Outward-facing acts are operator-gated, and the gate type is load-bearing.** `human-action`, not
  `human-verify` — auto-modes approve the latter and never the former.
- **Freeze, then post, then prove they matched.** Blob SHA + byte length recorded before the gate;
  a fetch-back byte-diff after any post. Two independent mechanisms, the project's standing rule for
  anything frozen.
- **A gate that has only ever passed is untrusted.** Phase 138's Run 1 planted-failure discipline is
  this milestone's house style; any checker this phase leans on (the claim gate) must be seen to fail
  before its pass is believed.
- **Cite by commit or `file:line`, never by recollection.** Every number in the correction traces to
  a SHA or a line anchor — that is what makes this comment different from the issue it corrects.

### Integration Points
- `gh issue comment 15 --repo henols/firestarter_prom --body-file <frozen file>` — the single posting
  call, guarded by D-08/D-09/D-10.
- `gh issue edit 15 --repo henols/firestarter_prom --body-file <frozen body>` — the **optional**
  second call from D-01, default-skipped, separately authorized.
- The meta repo's v1.31 branch push — a **precondition** of posting (D-07), not a cleanup step
  afterwards.
- ROADMAP.md §"Phase 140" `Depends on:` — the line D-08's named exception must amend if the
  approve-but-hold branch is taken.

</code_context>

<specifics>
## Specific Ideas

- **The comment's job is to make the issue safe to implement from.** The test to write against, and
  the one D-03 and D-04 both serve: *if a stranger — or an agent — read only gh#15 and its comments
  and started coding tomorrow, would they build the corrected design?* Anything in the draft that
  does not move that answer toward yes is decoration.
- **Lead with the self-correction, not with the evidence.** First person, one short paragraph: I
  filed this, two numbers are wrong, one premise is inverted, here is what changes. Evidence follows
  the claim; it does not precede it. `137-GH12-COMMENT.md` opens exactly this way.
- **The `50000 us` number is the single most important thing to kill**, because it is the one a reader
  would copy straight into code. It deserves its own named correction with the commit that created
  the artifact (`8de307f`), not a line in a table.
- **State the 6.25 V ceiling as a limit on what *any* implementation of this issue can claim on this
  hardware** — not as an excuse for this implementation. gh#15 omits it entirely, which is precisely
  why its acceptance criteria imply a fidelity that is unreachable here.
- **The original acceptance-criteria list must survive verbatim** wherever the amendment lands
  (`<details>` in the body edit, or quoted in the comment). Correcting a public spec by making the
  original unreadable is the failure mode to design against.

</specifics>

<deferred>
## Deferred Ideas

- **Per-value datasheet attribution for the parameter table** — TABLE-04, Phase 140. Phase 139
  publishes the table's *shape* and marks every numeric row **proposed** (D-04).
- **Item-by-item reconciliation of gh#15's acceptance criteria as met / met-as-corrected /
  not-reachable** — CLOSE-04, Phase 146. Phase 139 *proposes* the amendment; Phase 146 *reports*
  against it. D-03 exists so that report has something honest to reconcile against.
- **Release notes describing the programming-behavior change** — CLOSE-05, Phase 146.
- **The claim gate itself** (`check_permitted_claims.py`, armed and seen to fail on a planted
  violation) — CLOSE-01, Phase 146. Phase 139 *complies* with its forbidden-claim list (D-05) but does
  not build or arm the gate.

### Reviewed Todos (not folded)

- **"Reply on gh#12 (and correct the b14 app release notes) after `dev sdp` is retired"**
  (`gh12-followup-after-dev-sdp-retirement.md`, score 0.6) — **reviewed, explicitly not folded**
  (operator decision, this discussion). It is v1.30's **CLOSE-06**, a different issue and a different
  milestone's requirement; folding it would put a v1.30 deliverable inside a v1.31 phase's
  requirement set. Its blocker is nonetheless **now satisfied** — the `dev sdp` removal shipped with
  the v1.30 merge (app `beta` at `3.0.0b20`) — and its text is frozen at
  `.planning/phases/137-close-honesty-ledger-claim-gate-gh12-followup/137-GH12-COMMENT.md`, awaiting
  the single command recorded in `.planning/v1.30-OPERATOR-BATCH.md` §A-1. **Not this phase's to
  discharge; recorded here so it is not lost a second time.**
- **"Skip VPP error/warning checks when VPP is unused (reads/blank-checks)"**
  (`2026-06-24-skip-vpp-error-and-warning-checks-when-vpp-unused-on-reads.md`, score 0.6) — a firmware
  behavior change in VPP territory. Overlaps **Phase 142**, not 139, and 139 writes no firmware.
- **"AT28C256 write-path failure (gh#20)"** (`at28c256-write-path-failure-gh20.md`, score 0.6) — a
  live defect on a 28C part, protocol `0x0D`. Different family, different milestone's problem.
- **"Photograph operator's Modified Rev 0 board"** / **"Write full MODIFICATIONS.md rework trace"**
  (both score 0.6) — Phase 31 follow-ups, matched on the bare word "phase".
- **"v1.30 close — run /gsd-complete-milestone then /gsd-pr-branch targeting beta"** (score 0.6) —
  already discharged; PR #44 merged 2026-08-05 as squash `568e58b`. **Never re-merge**
  (`--is-ancestor` exits 1 as a false negative because of the squash).
- **"Skill: triage `dev test` issues"** (`2026-08-05-dev-test-issue-triage-diagnosis-skill.md`,
  score 0.4) — tooling, unrelated to this milestone.

</deferred>

---

*Phase: 139-gh#15 Correction (outward)*
*Context gathered: 2026-08-09*
