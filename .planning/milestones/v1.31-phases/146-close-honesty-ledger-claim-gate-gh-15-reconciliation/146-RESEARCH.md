# Phase 146: Close — Honesty Ledger, Claim Gate & gh#15 Reconciliation - Research

**Researched:** 2026-08-17
**Domain:** Closing-artifact authorship, machine claim gating over `.planning` prose, dual-repo
documentation reconciliation, read-only GitHub issue reconciliation
**Confidence:** HIGH (every figure below was measured live in this session against the tip; the
few inherited figures that did NOT hold are flagged explicitly)

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

Copied verbatim from `146-CONTEXT.md` `<decisions>`. Fourteen decisions, D-01…D-14, plus the ten
hard sequencing constraints they imply.

- **D-01: Draft only — nothing is pushed, merged, cut or published in this phase.** `CLOSE-01…CLOSE-05`
  name no push, no merge and no cut; `CLOSE-05` asks only that release notes *describe* the change.
  Both release bodies are committed drafts behind the blocking operator wording review, and the merge
  to `beta`, the CI-triggered cut, any PyPI dispatch and the `v1.31` tag all belong to
  `/gsd-complete-milestone`. This keeps the phase inside its requirement text and avoids the known
  trap that an outbound `beta` push auto-fires CI and cuts a beta as a side effect — which has already
  fired twice in this project. **Rejected:** a PR into `beta` in both sub-repos (v1.30's shape) — makes
  a docs-and-claims phase outward-facing in a second way, adds a PR round-trip, and the squash merge
  leaves `--is-ancestor` a permanent false negative. **Rejected:** a full v1.23-style cut with PyPI —
  the largest possible scope for something no requirement asks for.

- **D-02: Both release bodies are version-agnostic.** The tag is filled in at cut time, never
  computed here. Each body carries an explicit placeholder rather than any `3.0.0bNN` literal. Both repos'
  CI auto-increments from a git-tag scan on push to `beta`, so the real tag is only knowable after the
  cut — v1.23's close made "read the observed tag from `gh release list`, never compute it" a hard
  sequencing constraint, and a body drafted in this phase cannot be wrong about a tag it never saw.
  **Rejected:** writing the predicted next beta into the drafts — bakes a computed tag into an
  outward-facing body, and a stray CI fire between now and the cut silently invalidates it.
  **Rejected:** never naming a version at all — a release body that cannot identify itself reads
  oddly to the stranger `CLOSE-05` is written for.

- **D-03: Phase 145's remaining carry-forwards get ledger rows only.** No new backlog stubs and no
  STATE.md block for the eight `no v1.31 owner` items. Each appears as a negative-space row in `146-LEDGER.md` naming
  what was not proven and why, **citing `145-BENCH-LOG.md` rather than re-deriving it**. Two of the
  twelve are already filed (999.30, 999.31) and six of the remaining eight already have a home — FUT-08,
  FUT-VCC, FUT-PRESTO and FUT-MAXPULSE in `REQUIREMENTS.md` §Future Requirements, and the `0x08`/`0x0B`
  bench skips in BENCH-02's own disposition records — so filing stubs would duplicate them. Precedent
  is 130 D-10: negative space covers deferrals *and* every owned residual. **Rejected:** filing stubs
  for the genuinely homeless ones — an extra triage pass onto a backlog already at 999.31 for items the
  ledger already names. **Rejected:** a consolidated residuals block in STATE.md — a third place the
  same facts live, which is how drift starts.

- **D-04: All seven inherited corrections are discharged here.** `CLOSE-04`'s own text names only
  gh#15, but four prior phases routed non-gh#15 corrections to "Phase 146 / CLOSE-04" **in writing**,
  each declining to make the correction itself on the stated grounds that 146 would. The seven:
  (1) 143 D-01's `ROADMAP.md`/`PROJECT.md` prose — Phase 143 is factually **not** independent of
  Phases 140–142 and **is** dual-repo; (2) the milestone's matching sequencing-spine sentence;
  (3) 141 H3 / milestone C3 — `pulse-delay` is parsed by `extract_long` into an **unclamped**
  `uint32_t` (`json_parser.c:503`), so an over-ceiling `delayMicroseconds` value is reachable
  **today**, before `--pulse-us` ships; (4) 141 H4 — the honest energy-cap ceiling is exactly **50 ms**
  on every shipped `0x0B` width and **99998 µs** worst case for an arbitrary width, not
  `141-CONTEXT.md` D-01's larger figure; (5) **F-140-05** — `PROJECT.md`'s throughput table implies
  `overprogram_factor = 3` for `0x07` while the shipped value is `0`; (6) **F-140-07** — the
  justification sentence **published on gh#15** and carried in `PROJECT.md` is factually wrong;
  (7) **F-141-07** plus **F-144-01** — `DBG_PULSE_DELAY_MISMATCH`'s stale wording, `MSG_INFO_RETRIES`'s
  orphan status, and `firestarter/CLAUDE.md`'s stale `native_loop_v131` total against the measured 79.
  **Rejected:** gh#15's nine boxes only — closes the milestone with its own roadmap asserting something
  its own records disprove. **Rejected:** the planning-record half only, re-filing the two source-text
  items — F-141-07 is wording, not behaviour, and deferring it leaves the firmware emitting a debug
  message describing an algorithm it no longer runs.

- **D-05: Corrections land as labelled correction blocks plus a register.** Each lands as a
  `⚠ CORRECTION` block at the false statement's own site, alongside a consolidated
  `146-CORRECTIONS.md`. The block warns `/gsd-new-milestone`'s scoping pass
  *in situ*, which is exactly how v1.23's stale prior-art paragraph was going to propagate; the register
  gives "reconciled item by item" a single readable surface and gives the claim gate one file to scan.
  Each register row carries the origin finding id, the false text, the corrected text and the owning
  file. **Rejected:** blocks only (v1.23 D-05 exactly) — leaves the item-by-item claim with nowhere a
  reviewer can read it down. **Rejected:** folding corrections into `146-LEDGER.md` — mixes "what may
  be claimed" with "what we previously got wrong", two different questions, and leaves `ROADMAP.md`'s
  false prose uncorrected at its own site.

- **D-06: Sub-repo edits are wording and documentation only — no behaviour change anywhere.**
  F-141-07's message text is corrected through `tools/catalog/messages.toml`, which exists in **three
  copies** (meta `./tools/catalog/`, `firestarter/tools/catalog/`, `firestarter_app/tools/catalog/`)
  and regenerates `messages.h` and `messages.py`; note that `messages.h` is **ID-only**, so a
  wording-only change produces a **zero diff** there and the real diff is the toml plus
  `firestarter_app/firestarter/messages.py`. `MSG_INFO_RETRIES`'s orphan status is recorded, not
  removed. **C3/H3's unclamped `extract_long` is RECORDED as a correction and not clamped** — adding a
  clamp is a behaviour change on a wire field, landing after the bench evidence was taken, and backlog
  999.31 already owns the adjacent "no firmware-side upper bound on `--pulse-us`" decision.
  **Rejected:** record everything and edit nothing — leaves a shipped debug message describing the
  deleted adaptive loop. **Rejected:** wording plus the clamp — a post-bench behaviour change at close,
  pre-empting a decision 999.31 owns.

- **D-07: A second gh#15 comment is posted and the issue stays OPEN; the body is not edited.**
  Measured at discussion time: gh#15 is **OPEN**, carries exactly **one** comment (139's correction,
  `#5233463320`), and its body is **unedited** — `lastEditedAt = null`, all nine acceptance boxes
  still unticked. The reconciliation is posted because **F-140-07's error is already public in our own
  comment** and this is the only honest chance to correct it. The issue stays open: the operator filed
  it themselves, three-plus boxes are answered as narrower-than-they-read rather than met, and closing
  an issue whose acceptance criteria the implementer amended reads as self-certification.
  **Rejected:** posting and closing. **Rejected:** an internal artifact with nothing posted — leaves
  F-140-07's wrong justification public and uncorrected, and puts the reconciliation only in a
  planning repo strangers do not read. **Rejected:** amending the body's nine boxes — declined once
  at 139-05 (the operator selected "Comment only"), and re-editing the body would make it no longer
  the text readers were corrected *against*.

- **D-08: The reconciliation grades the ORIGINAL nine boxes, with every 139 correction named inline.**
  `CLOSE-04`'s wording — *met, met-as-corrected (naming the correction), or
  not-reachable-on-this-hardware (naming the reason)* — only makes sense against the text as filed.
  139's comment **replaced** box 1 (separate handlers → one shared loop plus a `const` table) and
  **corrected** boxes 3, 4 and 5 (the pulse constants); those become `met-as-corrected` with the
  correction quoted, not silently `met`. A reader who never saw comment `#5233463320` still gets the
  whole story from the reconciliation alone. **Rejected:** grading the corrected set with a pointer
  back — a stranger sees nine unticked boxes in the body and a reconciliation grading different
  criteria. **Rejected:** both columns side by side — duplicates 139's own disposition column for a
  wider table.

- **D-09: The comment carries the boxes, F-140-07's correction and a bench boundary.** It stops
  there — the nine dispositions, the public correction, and one short paragraph. That paragraph states: `0x07` bench-proven on
  **one part, one controller, one shield revision** (W27C512 `0xda08`, `leonardo`, Rev 2.0); `0x08` and
  `0x0B` **skipped-with-reason** naming the missing parts; the 6.25 V ceiling restated; and **no
  comparative claim** — v1.31 claims fidelity, not improvement, and no control run exists (145 D-08).
  That answers the obvious "does it work?" follow-up without the comment becoming release notes.
  **Rejected:** strictly the boxes plus F-140-07 — states the bench asymmetry only where strangers do
  not look. **Rejected:** adding a user-facing "what changed" section — duplicates `CLOSE-05` and
  creates two public texts that must not drift.

- **D-10: Posting follows 139's mechanics exactly.** Freeze the artifact, record its blob SHA and byte
  count, run the claim gate green against it, obtain explicit operator authorization at a blocking
  gate, post, then byte-verify the posted comment against the frozen text. Two recorded gotchas apply:
  `updatedAt` **bumps on comment creation**, so it is *not* a body-edit oracle (use `lastEditedAt`), and
  `sed -e '$a\'` cannot cancel GitHub's appended trailing newline when comparing bytes.

- **D-11: The gate arms all-or-nothing on five artifacts, with per-file caveat rules.** The five are
  this phase's own `.planning` closing artifacts — `146-LEDGER.md`, `146-CORRECTIONS.md`, `146-GH15-RECONCILIATION.md`,
  `146-RELEASE-NOTES-fw.md`, `146-RELEASE-NOTES-app.md`. Forbidden phrases are scanned in **all
  five**; the 6.25 V caveat is **required only where it belongs** — the ledger, the reconciliation and
  both release bodies — rather than blanket-required everywhere, so a register of factual corrections
  is not failed by a rule written for a release body. Producing four of five stays a hard failure by
  design (v1.23 D-15's arming contract). **Rejected:** one gate over the sub-repo docs too — forces a
  6.25 V paragraph into `firestarter/doc/PROTOCOLS.md` and the app README under a rule written for
  release bodies. **Rejected:** 139's shape unchanged at a larger target list (uniform caveat rules
  everywhere) — mechanically simplest, but leaves the outward-facing sub-repo docs with no machine
  check at all.

- **D-12: CLOSE-01 is proven by fixtures AND a real-file plant-and-revert transcript.** `CLOSE-01`
  makes two distinct claims — *armed against the real files* and *seen to fail on a planted violation* —
  and neither proof covers both. A pytest suite over a `fixtures/` directory (the 122/130/137 shape,
  BASE-08 discipline) proves every forbidden pattern and every caveat rule fires; a recorded
  plant-and-revert against a **real** closing artifact proves `_DEFAULT_TARGETS` is genuinely wired to
  the files that ship, exits 1 naming the file, then exits 0 after revert with byte-identity asserted.
  Phase 145 found **three** acceptance locators that were false GREENs — one passed against a record
  with no content in it at all — which is why a fixture alone is not accepted here. **Rejected:**
  fixtures only. **Rejected:** plants only — leaves no standing regression test for the pattern table.

- **D-13: A separate phase-local script checks the CLOSE-03 sub-repo docs.** It covers forbidden
  phrases plus the five required topics: it reads the changed documentation files and asserts (a) zero forbidden-phrase
  matches and (b) the presence of each of `CLOSE-03`'s five topics: the per-byte algorithm, the
  parameter table, the database-supplied pulse, `--pulse-us`, and the 6.25 V accepted debt. No blanket
  caveat rule. One-shot and phase-local, matching the docs-and-claims boundary, and it turns
  `CLOSE-03`'s five topics from a prose promise into a machine-checkable list. **Rejected:** committed
  tests in both sub-repos — strongest against drift (and `doc/PROTOCOLS.md` genuinely did go stale) but
  adds brittle doc-content assertions to two repos at close. **Rejected:** relying on the operator
  wording review alone — drops the mechanizable half of a discipline this project has repeatedly said
  is only half mechanizable.

- **D-14: Forbidden claims are cited by location and finding id, never reproduced.** Citation is by
  file and line number, never by quoting the phrase. The
  self-reference trap is real and has bitten this project: a ledger quoting a forbidden phrase in
  order to disclaim it trips its own gate — it caught all six `125-0N-SUMMARY.md` files, and v1.22
  solved it exactly this way. This preserves 139's deliberate **no-proximity-window** design, which was
  chosen after measuring that a windowed scanner passed a file carrying four planted overclaims.
  **Consequence a plan must carry:** 139's table forbids `\bproven\b` unqualified, and the phase
  records use that word honestly throughout — so the closing artifacts must be **written** around it
  rather than the pattern loosened. **Rejected:** narrowing the pattern table for the ledger's
  convenience. **Rejected:** an exclusion-by-heading quarantine block — every exclusion is a hole, and
  145-08 caught a check that self-matched its own quoted negative-control literal.

#### Hard sequencing constraints these decisions imply

Not preferences. A plan that reorders any of these breaks a requirement or publishes an unreviewed
artifact.

1. **`146-LEDGER.md` exists before either release body is written** — the ledger is the single source
   of the permitted wording both bodies must match (D-02, D-11; v1.23 constraint 3).
2. **The claim gate is written, fixtured, and seen to fail before any artifact is called final**
   (D-12). RED proves nothing until it has been seen to pass for the right reason.
3. **The gate runs green against all five artifacts before the gh#15 comment is frozen** (D-10, D-11).
4. **The blocking operator wording review precedes the gh#15 post and covers both release bodies**
   (D-01, D-07, D-10).
5. **Nothing in this phase pushes, merges, tags or dispatches a workflow** (D-01). No task may run
   `git push` or `gh workflow run` — a standing structural gate in this project.
6. **The sub-repo doc edits and the `messages.toml` regen precede the doc-topic check** (D-06, D-13).
7. **`messages.toml` is edited in all three copies and regenerated — never hand-edit `messages.h` or
   `messages.py`** (D-06).
8. **Only the closing plan may tick CLOSE-01…CLOSE-05.** Executors have marked multi-plan requirements
   Complete prematurely 4× in Phase 116 and 4× in Phase 117 — name the allowed ids in every dispatch
   prompt and re-check `REQUIREMENTS.md` after each plan.
9. **Commit before running either sub-repo's suite** — `firestarter/tests/test_flash_path_record_sync.py`
   asserts the **whole** firmware repo's `git status --porcelain`, and the host's
   `test_py32_flash_map_host.py` asserts the same for the sibling firmware repo.
10. **This phase must not run under `--auto` or `--chain`** — both auto-approve `human-verify` gates,
    and `autonomous: false` is not self-protecting. D-07's posting gate and D-01's wording review are
    real.

### Claude's Discretion

An index of discretionary items, not a second definition site. The IDs are deliberately unbolded here:
a `- **D-NN**` bullet without a `:` or ` — ` inside the bold makes the decision-coverage gate fail
closed with `reason: could-not-parse`.

- **Every word of `146-LEDGER.md`, both release bodies, `146-CORRECTIONS.md` and the gh#15
  reconciliation** — subject to D-14's citation discipline, the 6.25 V ceiling and the bench boundary
  being present, and nothing being phrased as *verified*, *validated* or *works end to end*.
- **The ledger's row count, column set and section order.** `CLOSE-02` fixes only that it leads with
  the 6.25 V ceiling and the asymmetric bench coverage; the evidence-tier grouping from 130 D-09 is
  available and probably right, but the layout is open.
- **Whether the ledger leads with the 6.25 V ceiling or the MERGE-05 +96 B exemption inside that
  opening section** — the exemption's verbatim quotable wording is already staged in `STATE.md` from
  commit `d02a88a0` and must be used rather than re-derived.
- **Which of the nine gh#15 boxes gets which of the three dispositions**, and the wording of each
  reason — derived from the shipped evidence, not from this discussion. Note boxes 7 and 9 are the
  interesting ones: the VPP-disable guarantee is proven at the operation level via `command_done()` as
  a **source contract**, not behaviourally, and a successful block deliberately stays energised; and
  "all targets build" is true carrying MERGE-05's admitted +96 B exemption.
- **The correction register's layout** — D-05 fixes the four fields per row, not the table shape.
- **Which files CLOSE-03 touches and how much lands in each.** The candidates are named in
  `<code_context>`; the split between `firestarter/CLAUDE.md` (already updated 4× this milestone) and
  `firestarter/doc/PROTOCOLS.md` (stale since 140-06) is Claude's, as is whether the host half is a
  README edit, a new `firestarter_app/doc/` chapter, or both.
- **Whether the two scripts (D-11's claim gate, D-13's doc check) are one file with two modes or two
  files** — provided each carries its own `_assert_default_targets_are_local()`-style self-check and
  neither can pass vacuously.
- **Plan decomposition and wave structure**, subject to the ten constraints above.
- **Whether the phase asserts the meta gitlinks match the sub-repo tips at phase end** — v1.23 D-04
  asserted rather than re-pinned; this phase's own sub-repo commits will move both tips, so some
  assertion is wanted, but its form is open.

### Deferred Ideas (OUT OF SCOPE)

#### Raised during this discussion, declined with a reason
- **A PR into `beta` in both sub-repos, or a full v1.23-style cut with PyPI.** Declined at D-01 — no
  requirement asks for it, and publication belongs to `/gsd-complete-milestone`.
- **Naming the predicted next beta tag in the release bodies.** Declined at D-02 — computing an
  outward-facing tag is exactly what v1.23's close forbade.
- **Filing backlog stubs for Phase 145's homeless carry-forwards, or a residuals block in STATE.md.**
  Declined at D-03 — ledger rows only; six of eight already have a home.
- **Clamping `extract_long`'s `pulse-delay` (C3/H3).** Declined at D-06 — a behaviour change on a wire
  field after the bench evidence was taken. Recorded as a correction; backlog **999.31** owns the
  adjacent firmware-ceiling decision.
- **Closing gh#15, and amending its nine body boxes.** Both declined at D-07. The body amendment was
  already declined once at 139-05 and is not revived.
- **One gate over the sub-repo docs as well as the `.planning` artifacts.** Declined at D-11 — would
  force a blanket 6.25 V caveat rule into a public README under a rule written for release bodies.
- **Committed doc-content tests in both sub-repos.** Declined at D-13 — strongest against drift, but
  brittle standing assertions added to two repos at close.
- **Loosening the gate's `\bproven\b` pattern for the ledger's convenience, or an
  exclusion-by-heading quarantine block.** Both declined at D-14.

#### Carried forward, still not taken — the `no v1.31 owner` set
Every item below gets a **ledger row** (D-03) and nothing more. None is actioned.
- **A1's per-pulse overhead inside a multi-pulse retry loop** — 145-07 derived a per-**byte** upper
  bound (~1.44 ms), which is a different quantity. No owner.
- **Row 27's "smoothly moving bar, not an end-burst" discriminator** — the operator's four words
  ("It looked ok") contain neither term. No owner.
- **The MAIN write bar never reaching 100 %** — backlog **999.30**.
- **No firmware-side upper bound on `--pulse-us` for `0x07`/`0x08`, plus T-145-45's overstated
  mitigation** — backlog **999.31**. D-06 leaves the code alone; the ledger may judge T-145-45's wording.
- **Program-window VPP / internal VCC under load (FUT-08's hypothesis)** — never instrumented; the
  held-rail DMM proxy is defeated by DTR-reset-on-close. `REQUIREMENTS.md` FUT-08 / §Future Requirements.
- **Root cause of the intermittent single-byte margin failure** — mitigated by ~17 clean cycles, not
  explained. No owner.
- **`0x08` (AM27C020) bench validation** — BENCH-02's disposition record; FUT-08.
- **`0x0B` (M2716/M2732) bench validation** — a real parked successor exists (Phase 79 plan `79-03`),
  but not in v1.31.
- **A true-UV `0x07` data point (TMS27C512)** — deliberately not spent; needs a UV eraser.
- **The 6.25 V program-VCC ceiling** — the milestone's accepted debt, `FUT-VCC`. Leads the ledger.
- **F-140-05's `0x07` Intel-family split** — needs a second dispatch key, forbidden by TABLE-05.
  Corrected in the record here; the split itself is future work.
- **`FUT-PRESTO`, `FUT-MAXPULSE`, `FUT-OVERPROG-MAP`** — `REQUIREMENTS.md` §Future Requirements.
- **F-141-11 / F-143-02 / F-143-03** — `test_flash_path_record_sync.py` and its host analog asserting
  whole-repo porcelain. Still unassigned; sequenced around, not fixed.
- **F-138-05 / F-143-04** — `check_size_baseline.py`'s uncaught `KeyError` on an unknown native env.
  Owner `henols`; not fixed.

#### Reviewed Todos (not folded)
`todo.match-phase 146` returned matches; **none folded.** Every one is other-family firmware or
hardware work in a phase that changes no behaviour (D-06).
**`gh12-followup-after-dev-sdp-retirement.md` is v1.30's outward-facing debt and is not v1.31's** —
no community thread other than gh#15 gets a comment this milestone.
</user_constraints>

<phase_requirements>
## Phase Requirements

Quoted verbatim from `.planning/REQUIREMENTS.md` §Close (lines 256–266). **Only the closing plan may
tick these** (constraint 8).

| ID | Description (verbatim) | Research Support |
|----|-----------------------|------------------|
| **CLOSE-01** | A committed claim gate forbids unqualified "datasheet-conformant" / "datasheet-correct" / "algorithm-accurate" across all closing artifacts, is **armed against the real files**, and has been **seen to fail** on a planted violation. | §"The Claim Gate" — the 139 donor read in full with its pattern table transcribed and empirically probed; the 137 fixture-plus-pytest suite mapped leg by leg; both recorded traps answered with file:line; measured hit counts over every candidate target file. |
| **CLOSE-02** | An honesty ledger pairs every permitted claim with its explicit non-claim, leading with the 6.25 V ceiling and the asymmetric bench coverage. | §"Closing-Artifact Shapes" (three prior ledger skeletons, most recent read in full) + §"The Evidence This Close Reports On" (the 12-row carry-forward table, the 16-row not-measured table, the nine boundaries, the verbatim MERGE-05 wording, and three counting discrepancies the ledger must settle). |
| **CLOSE-03** | Firmware and host documentation describe the new per-byte algorithm, the parameter table, the database-supplied pulse, `--pulse-us`, and the 6.25 V accepted debt. | §"CLOSE-03 Documentation Targets" — a measured five-topic × six-file coverage matrix, the exact stale sentence in `doc/PROTOCOLS.md`, and two doc defects neither CONTEXT nor any prior record names. |
| **CLOSE-04** | gh#15's acceptance criteria are reconciled **item by item** — each marked met, met-as-corrected (naming the correction), or not-reachable-on-this-hardware (naming the reason). | §"gh#15 Live State" (re-measured read-only, five oracles) + §"The Seven Inherited Corrections" (every site located with file:line, every figure re-verified against shipped code, three that do NOT hold flagged). |
| **CLOSE-05** | Release notes describe the programming-behaviour change and the `--pulse-us` addition in terms a stranger can act on. | §"Closing-Artifact Shapes" (four release-body precedents, one read in full) + §"The `--pulse-us` Surface as Shipped" (the complete 7-option `write` surface, measured). |
</phase_requirements>

## Summary

This is a docs-and-claims phase with **zero new dependencies, zero behaviour change, and one
outward-facing act** (a single `gh issue comment` on gh#15). Almost all of the work is authorship
constrained by a machine gate the phase also writes. The mechanical parts are unusually well
precedented: this project has shipped a claim gate at every milestone close since v1.22, and the
139 donor sitting in a sibling phase directory already carries **this milestone's own vocabulary**,
already has no proximity window, and already carries a startup self-check that fails loudly when
copied. The 146 gate is a rename-and-retarget of that file plus a per-file caveat rule, not a new
design — and the 137 pair (`check_permitted_claims.py` + `test_check_permitted_claims_v130.py` +
`fixtures/`) supplies the eleven-leg pytest shape D-12's first half mirrors, verbatim.

What research changes about the plan is mostly the **evidence** side, and three findings are
load-bearing enough to name up front. **(1) Neither repository's CI has ever run against any v1.31
code.** Both remote milestone branches are stale — `origin/gsd/v1.31-…` in `firestarter` sits at
`fb7949c` (end of Phase 138) and in `firestarter_app` at `4d18b645` (the branch point) — so the last
CI runs on those refs, both green, exercised nothing from Phases 140–145, and the ARM/`py32f071`
build has **never** compiled the parameter table, the per-byte loop, `eprom_budget.cpp` or the two
Phase-145 debug fixes. gh#15 box 9 ("All firmware targets build successfully") and both release
bodies must be written against that fact. **(2) Three of the seven inherited corrections do not hold
as CONTEXT states them** — the `PROJECT.md` half of correction (1) has no false-statement site (only
a routing note), F-140-05's misleading throughput row is **two** rows not one, and F-140-07 is
*already corrected in place* in `firestarter/doc/PROTOCOLS.md` §1.5, leaving only the public and
`.planning` halves owed. **(3) The gate and the ledger are in direct mechanical tension over
`145-BENCH-LOG.md`.** That record's own boundary 2 (line 2709) contains `datasheet-correct`, and the
record carries five forbidden-phrase hits total — so D-03's "the ledger cites this record" and D-14's
"never reproduce the phrase" are the same instruction, and quoting boundary 2 verbatim would trip the
phase's own gate. Both `139-GH15-COMMENT.md` and `139-GH15-ORIGINAL-CRITERIA.md`, by contrast, are
measured **clean**, so D-08's verbatim grading of the nine original boxes is gate-compatible.

One asset CONTEXT does not name matters a great deal: **`.planning/phases/130-…/check_record_corrections.py`
is a live, currently-GREEN gate over `PROJECT.md`, `STATE.md` and `ROADMAP.md`** — three of the four
files D-05's `⚠ CORRECTION` blocks land in — and it already defines `⚠ CORRECTION` as a machine-recognized
block opener with defined exemption semantics. Phase 146 must re-run it after the corrections land, and
must use that exact opener token.

**Primary recommendation:** Author `146-check-claims.py` as a 146-scoped sibling of
`139-check-claims.py` (same twelve patterns, same no-window design, `139-`→`146-` prefix assertion,
`_V131`→a fresh suffixed env seam, plus a per-file caveat map), pair it with a `test_check_claims_v131.py`
suite modelled leg-for-leg on 137's eleven, prove arming with a plant-and-revert against the real
`146-LEDGER.md`, and write every closing artifact to cite forbidden phrases **only** by `file:line`
and finding id — never by quotation — because the gate's own targets, the bench record it cites, and
this milestone's own success criteria all contain the literals it forbids.

## Architectural Responsibility Map

No runtime tiers exist in this phase — nothing ships to a device or a user's shell. The equivalent
axis is **which artifact owns which claim**, and getting it wrong is the failure mode D-05 and D-11
were written against.

| Capability | Primary owner | Secondary owner | Rationale |
|------------|---------------|-----------------|-----------|
| What may be claimed, paired with its non-claim | `146-LEDGER.md` | — | CLOSE-02's literal subject. Written first (constraint 1) because both release bodies must match its permitted wording. |
| What we previously got wrong, and the corrected text | `146-CORRECTIONS.md` + in-situ `⚠ CORRECTION` blocks | `.planning/{ROADMAP,PROJECT,STATE}.md`, `firestarter/CLAUDE.md` | D-05 splits these deliberately from the ledger: "what may be claimed" and "what we got wrong" are different questions, and a block at the false statement's own site is what warns the next milestone's scoping pass. |
| Public reconciliation of gh#15's nine boxes | `146-GH15-RECONCILIATION.md` → one comment | — | CLOSE-04. Frozen, gated, operator-authorized, byte-verified (D-10). The only outward-facing act in the phase. |
| Stranger-actionable "what changed" | `146-RELEASE-NOTES-{fw,app}.md` | — | CLOSE-05. Drafts only (D-01). Version-agnostic (D-02). |
| Machine enforcement of the claim boundary over `.planning` artifacts | `146-check-claims.py` + fixtures + plant transcript | — | CLOSE-01, all-or-nothing over exactly five files (D-11). |
| Machine enforcement over sub-repo docs (5 topics present, 0 forbidden phrases) | the D-13 phase-local doc checker | — | Deliberately a *second*, differently-shaped script: the sub-repo docs must not inherit a caveat rule written for a release body (D-11's rejection). |
| Describing the shipped algorithm to a firmware developer | `firestarter/doc/PROTOCOLS.md` §§1.3–1.5 | `firestarter/CLAUDE.md` §Algorithm Handlers | PROTOCOLS.md is the per-protocol reference and is the stale one; CLAUDE.md is the living agent-facing reference and is already current on 4 of 5 topics. |
| Describing the change to a CLI user | `firestarter_app/README.md` §Write / §Eprom Configuration | `firestarter/README.md` §Protocol Notes | The host README is where a user meets `--pulse-us`; it has **zero** v1.31 doc commits. |
| Message wording | `tools/catalog/messages.toml` ×3 → codegen | — | Constraint 7. `messages.h`/`messages.py` are generated; hand-editing either is the defect this constraint exists to prevent. |

## Standard Stack

Nothing is installed. Every tool this phase needs is already on the box and already in use by prior
closes.

### Core

| Tool | Version (measured) | Purpose | Why standard |
|------|--------------------|---------|--------------|
| Python 3 stdlib (`os`, `re`, `sys`) | 3.12.x devcontainer ambient | The claim gate and the doc checker | All four prior claim gates (122/123/137/139) are stdlib-only single files with no imports beyond these three. `[VERIFIED: read all four files this session]` |
| `pytest` | present in both sub-repo venvs; firmware suite ran 314 passed in 19.17 s this session | The D-12 fixture suite | 137's `test_check_permitted_claims_v130.py` is the shape; it drives the checker as a **subprocess**, never an in-process import, for the nine behavioural legs. `[VERIFIED: ran both suites this session]` |
| `gh` CLI | authenticated; read-only calls all succeeded this session | gh#15 measurement and the single post | 139 used exactly four `gh` calls for the whole post. `[VERIFIED: re-ran three of them this session]` |
| `python3 tools/catalog/codegen.py` | in-tree, `--catalog/--target/--language/--check` | Regenerating `messages.h` and `messages.py` | Constraint 7's only sanctioned mechanism. `[VERIFIED: ran --check and both emitters this session]` |
| `bash tools/catalog/sync_to_subrepos.sh` | in-tree | One command that copies the canonical toml into both sub-repos and regenerates both artifacts | Read in full this session; see the trap noted under Pitfalls. `[VERIFIED]` |

### Supporting

| Tool | Purpose | When to use |
|------|---------|-------------|
| `git hash-object <file>` | Freeze a blob SHA for D-10 | Once per frozen artifact, recorded in the register alongside `wc -c`. |
| `wc -c` | Byte length of a frozen artifact and of a fetched body | The **correct** byte oracle. `jq '.body \| length'` counts codepoints, not bytes — 139-CITATIONS §0 measured a 14-byte gap on the issue body from exactly this confusion. `[VERIFIED: reproduced this session — comment body is 12130 codepoints / 12194 bytes]` |
| `git diff --numstat` | Prove a doc edit's blast radius | 145-08's substitution #5: `git diff \| grep -c '^[+-][^+-]'` reported **zero** changed lines over a genuinely changed markdown file, because the diff `-` marker collides with the list bullet. Use `--numstat`. |
| `.planning/phases/130-…/check_record_corrections.py` | Re-verify the record gate after the `⚠ CORRECTION` blocks land | Ran GREEN this session; see §"The Unnamed Live Gate". |

### Alternatives considered

| Instead of | Could use | Tradeoff |
|------------|-----------|----------|
| A 146-scoped sibling of `139-check-claims.py` | Importing/subclassing/env-seaming the 139 or 137 checker | Every prior instance rejected this in writing, and 139's docstring records five executed probes proving why: the donor's defaults resolve to filenames that do not exist in the new phase, so an unmodified copy **scans nothing and reports success**. A sibling file is the established answer. |
| Two scripts (claim gate, doc checker) | One script with two modes | Explicitly Claude's discretion. Two files is the lower-risk read: each gets its own `_DEFAULT_TARGETS`, its own self-check, and its own never-vacuous guard, and a mode flag is one more thing that can silently select the empty target set. |
| Quoting the MERGE-05 wording from `STATE.md` | Re-deriving the byte figures from `check_size_baseline.py` | Discretion says quote it, and the wording was authored for exactly this purpose. Re-deriving would additionally require a cold rebuild the phase otherwise does not need. |

**Installation:** none. No `pip install`, no `npm install`, no new tool.

## Package Legitimacy Audit

**This phase installs no external packages.** No `pip install`, `npm install`, or `cargo add` appears
anywhere in its scope: the claim gate and the doc checker are Python-stdlib single files, the fixture
suite uses the `pytest` already present in both sub-repos, and every other tool (`git`, `gh`, `wc`,
`sha256sum`) is pre-existing. There is therefore no ecosystem registry to verify and no `[SLOP]`/`[SUS]`
verdict to record.

| Package | Registry | Verdict | Disposition |
|---------|----------|---------|-------------|
| *(none)* | — | — | Phase installs nothing |

**Packages removed due to `[SLOP]` verdict:** none.
**Packages flagged as suspicious `[SUS]`:** none.

If a plan finds itself wanting a dependency (a markdown linter, a diff library, a TOML writer), that
is a signal the plan has drifted out of the docs-and-claims boundary — every prior close did all of
this with the stdlib.

## Architecture Patterns

### Artifact and gate flow

```
                     ┌──────────────────────── INPUTS (read-only, cited never re-derived) ────────────────────────┐
                     │ 145-BENCH-LOG.md  145-08-SUMMARY.md  144-TEST-RECORD.md §10  143-HOST-RECORD.md §5/§6/§10   │
                     │ 141-LOOP-RECORD.md §6/§12  140-PARAM-TABLE-RECORD.md §3/§10/§11  STATE.md (d02a88a0)        │
                     │ 139-GH15-ORIGINAL-CRITERIA.md  139-GH15-COMMENT.md  shipped src/ in both sub-repos          │
                     └───────────────┬──────────────────────────────────────────────────────┬────────────────────┘
                                     │                                                      │
              (D-03: cite by file:line, never quote a forbidden phrase — D-14)               │
                                     v                                                      v
   ┌─────────────────────────────────────────────────┐              ┌──────────────────────────────────────────┐
   │ WAVE A — the gate, before any artifact is final │              │ WAVE B — the seven corrections (D-04/05) │
   │  146-check-claims.py   (12 patterns, no window) │              │  ⚠ CORRECTION blocks at each false site: │
   │  + fixtures/           (clean + planted)        │              │    ROADMAP.md:167, ROADMAP.md:380,       │
   │  + test_…_v131.py      (11 legs, subprocess)    │              │    ROADMAP.md/PROJECT.md throughput,     │
   │  self-check: _DEFAULT_TARGETS local AND "146-"  │              │    firestarter/CLAUDE.md:277-279         │
   └───────────────┬─────────────────────────────────┘              │  + 146-CORRECTIONS.md register           │
                   │  (constraint 2: seen RED for the right reason) │  + messages.toml ×3 → codegen (D-06)     │
                   │                                               └──────────────┬───────────────────────────┘
                   v                                                              │
   ┌─────────────────────────────────────────────────────────────────┐            │
   │ WAVE C — 146-LEDGER.md  (constraint 1: BEFORE both bodies)      │<───────────┘
   │   leads with 6.25 V ceiling + asymmetric bench coverage         │
   │   every permitted claim ↔ its explicit non-claim                │
   │   negative-space rows for all 12 carry-forwards (D-03)          │
   └───────────────┬─────────────────────────────────────────────────┘
                   │
        ┌──────────┴───────────────────────────────┐
        v                                          v
   ┌──────────────────────────────┐   ┌──────────────────────────────────────────┐
   │ WAVE D — release bodies      │   │ WAVE D — 146-GH15-RECONCILIATION.md      │
   │  fw + app, version-agnostic  │   │  9 original boxes × 3 dispositions       │
   │  wording matches the ledger  │   │  + F-140-07 public correction            │
   └──────────────┬───────────────┘   │  + one bench-boundary paragraph (D-09)   │
                  │                   └──────────────┬───────────────────────────┘
                  └──────────────┬───────────────────┘
                                 v
              ┌────────────────────────────────────────────────┐
              │ GATE: 146-check-claims.py green on ALL FIVE     │  (constraint 3)
              │ GATE: D-13 doc checker green on CLOSE-03 docs   │  (constraint 6)
              │ GATE: 130 check_record_corrections.py still 0   │  (see §Unnamed Live Gate)
              │ GATE: both sub-repo suites, AFTER commit        │  (constraint 9)
              └──────────────┬─────────────────────────────────┘
                             v
              ┌────────────────────────────────────────────────┐
              │ BLOCKING OPERATOR WORDING REVIEW  (constraint 4)│  autonomous: false
              │   covers both release bodies + the comment      │  NOT under --auto/--chain (10)
              └──────────────┬─────────────────────────────────┘
                             v
              ┌────────────────────────────────────────────────┐
              │ freeze (blob SHA + wc -c) → BLOCKING AUTH →     │
              │ gh issue comment 15 --body-file <frozen>  ← the ONLY write call in the phase
              │ → fetch-back byte-verify → state assertion      │
              └──────────────┬─────────────────────────────────┘
                             v
              ┌────────────────────────────────────────────────┐
              │ CLOSING PLAN ONLY — tick CLOSE-01…05 (const. 8) │
              │  REQUIREMENTS.md :256,259,261,263,265 + :337-341 │
              │  ROADMAP.md      :632-636  (+ :183 phase box)   │
              └────────────────────────────────────────────────┘

   NEVER, at any point: git push · git merge · git tag · gh workflow run · gh release · gh issue edit
                        · gh issue close · hand-edit messages.h/messages.py · edit an archived milestone
```

### Recommended file layout

```
.planning/phases/146-close-honesty-ledger-claim-gate-gh-15-reconciliation/
├── 146-check-claims.py            # D-11 gate. _DEFAULT_TARGETS = the five below, built from _HERE
├── test_check_claims_v131.py      # D-12 fixture suite, 11 legs, subprocess-driven
├── fixtures/                      # NEVER reachable from _DEFAULT_TARGETS (no glob, no walk)
│   ├── clean_control.md
│   ├── clean_control_second.md
│   ├── planted_forbidden_claim.md
│   ├── planted_proven_unqualified.md
│   └── planted_missing_caveat.md
├── 146-check-close03-docs.py      # D-13, separate script, separate target list, no caveat rule
├── 146-LEDGER.md                  # CLOSE-02  (gate target 1)  — written FIRST
├── 146-CORRECTIONS.md             # D-05      (gate target 2)  — no caveat rule (D-11)
├── 146-GH15-RECONCILIATION.md     # CLOSE-04  (gate target 3)
├── 146-RELEASE-NOTES-fw.md        # CLOSE-05  (gate target 4)
├── 146-RELEASE-NOTES-app.md       # CLOSE-05  (gate target 5)
├── 146-CITATIONS.md               # the 139 pattern: freeze values + every command as run
└── 146-0N-PLAN.md / -SUMMARY.md   # NOT gate targets — see the glob warning below
```

### Pattern 1: `_HERE`-built, explicitly enumerated default targets

**What:** `_DEFAULT_TARGETS` is a literal list of `os.path.join(_HERE, "146-….md")` entries, where
`_HERE = os.path.dirname(os.path.abspath(__file__))`.
**When:** always, for both scripts.
**Why this exact shape:** it is the answer to two different recorded defects at once, and the
distinction matters because the planner may be tempted to "simplify" to a glob.

```python
# Source: .planning/phases/139-gh-15-correction-outward/139-check-claims.py:68-81 (verbatim shape)
_HERE = os.path.dirname(os.path.abspath(__file__))

_DEFAULT_TARGETS = [
    os.path.join(_HERE, "146-LEDGER.md"),
    os.path.join(_HERE, "146-CORRECTIONS.md"),
    os.path.join(_HERE, "146-GH15-RECONCILIATION.md"),
    os.path.join(_HERE, "146-RELEASE-NOTES-fw.md"),
    os.path.join(_HERE, "146-RELEASE-NOTES-app.md"),
]
```

**Never a glob or a walk.** Measured this session with the 139 pattern table: a `146-*.md` default
set would immediately catch `146-CONTEXT.md` (**6** `proven-unqualified` hits, lines 81, 162, 191,
268, 418, 539) and `146-DISCUSSION-LOG.md` (**1** hit, line 94), plus this RESEARCH.md and every
PLAN and SUMMARY the phase writes. The gate would be red from its first run for reasons that have
nothing to do with the closing artifacts. 122's and 137's docstrings both warn about exactly this for
their `fixtures/` directory; the 146 case is worse because the phase's own planning prose is in the
same directory.

### Pattern 2: the startup self-check, and what a 146 copy must change

**What:** `_assert_default_targets_are_local()` runs *first thing* in `main()`, before target
resolution, and fails loudly per offending entry on two conditions: the entry does not resolve inside
`_HERE`, or its basename does not carry this phase's own number prefix.

```python
# Source: 139-check-claims.py:148-181, with the two 146 edits marked
def _assert_default_targets_are_local():
    all_local = True
    for entry in _DEFAULT_TARGETS:
        if os.path.dirname(entry) != _HERE:
            print(f"FAIL: _DEFAULT_TARGETS entry {entry!r} does not resolve "
                  "inside this phase's own directory -- this is the exact "
                  "cross-phase-copy defect this self-check exists to catch")
            all_local = False
        if not os.path.basename(entry).startswith("146-"):   # <<< 139- -> 146-
            print(f"FAIL: _DEFAULT_TARGETS entry {entry!r} does not carry "
                  "this phase's own 146- prefix -- this is the exact "        # <<< 139 -> 146
                  "stale-name defect this self-check exists to catch")
            all_local = False
    return all_local
```

**The `_HERE` trap, answered concretely.** The recorded defect is that v1.23's copy (hosted in
`.planning/phases/123-…/check_permitted_claims.py`) named its targets against a **sibling** phase
directory via a hardcoded string constant `_PHASE_130_DIRNAME`; a naive copy of that pattern into
another phase directory resolves its targets somewhere else entirely, scans nothing, and exits 0.
137's docstring (lines 51-67) documents this at length. **What a Phase 146 copy must change, exactly
and exhaustively:**

1. `_DEFAULT_TARGETS` — five new basenames, all `146-` prefixed, all built from `_HERE`, no sibling
   string constant anywhere in the file. **(mandatory)**
2. The self-check's prefix literal — `"139-"` → `"146-"`, in **both** the `startswith` call and the
   printed message. Leaving the message stale while fixing the call is a silent documentation defect
   the fixture suite will not catch. **(mandatory)**
3. The env seam name — `FIRESTARTER_CLAIMSCAN_TARGETS_V131` is **already taken by 139** in this same
   milestone. Reusing it lets one phase's test suite aim two live checkers at once, which is the exact
   collision the `_V130`/`_V131` suffix convention was introduced to prevent (137's docstring, PITFALLS
   P-11 point 5). Pick a fresh, distinct name — e.g. `FIRESTARTER_CLAIMSCAN_TARGETS_146`. **(mandatory,
   and easy to miss because a bare copy "works")**
4. The paired test module filename — `test_check_permitted_claims.py` already exists **twice** on disk
   (122's and 123's) and `test_check_permitted_claims_v130.py` once (137's). Under pytest's default
   `prepend` import mode, running pytest from `/workspaces` collides on same-named modules. Name the
   146 one distinctly. **(mandatory)**
5. The docstring's exit-code contract, non-claims, and the `PASS:` line prose — 139's names ISSUE-02 /
   D-05 / plan 139-05; 146's must name CLOSE-01 and the blocking operator wording review. **(mandatory
   for honesty, not for mechanics)**
6. The caveat rule — 139 requires **both** caveats in **every** scanned file. D-11 makes this per-file:
   required in the ledger, the reconciliation and both release bodies; **not** required in
   `146-CORRECTIONS.md`. This is the one genuinely new mechanism in the 146 gate. **(new)**

**What must NOT change:** the twelve patterns (D-14 forbids loosening), the absence of any proximity
window (D-14), the hoisted never-vacuous guard, the fail-closed missing-target branch, the `is not None`
env check that distinguishes "absent → defaults" from "present but empty → zero targets", and the
deliberate absence of any exit-0-on-nothing-scanned path.

### Pattern 3: the all-or-nothing arming branch, and whether 146 wants it

139 **omits** the UNARMED branch entirely and says so in its `main()` docstring: Phase 139 authored its
two artifacts in the same task that wrote the gate, so there was no pre-authored window to protect.
137 **keeps** it, with v1.23 D-15's mechanics: `if used_defaults and len(missing) == len(targets)` →
print `UNARMED:` and exit 0; a **partial** set (1–4 of 5 present) falls through to the ordinary
fail-closed branch and is a hard failure.

```python
# Source: 137/check_permitted_claims.py:299-319
if used_defaults and len(missing) == len(targets):
    print("UNARMED: none of Phase 137's 4 named closing artifacts exist yet (…) "
          "-- this is expected before they are authored, not a failure.")
    return 0
if missing:
    print("FAIL: scan target(s) not found on disk -- the gate cannot "
          f"vacuously pass with a target silently skipped: {missing}")
    return 1
```

**Recommendation:** keep the partial-set hard failure (D-11 names it explicitly: "Producing four of
five stays a hard failure by design"), and **drop the UNARMED branch**, following 139. The reason is
constraint 2 read together with the recorded "a pre-authored gate leg can be UNREACHABLE" pattern: an
UNARMED exit-0 path is a green that proves nothing, and this phase's wave order already guarantees the
gate is exercised against real files (constraint 3) rather than against an empty directory. If a plan
does keep UNARMED, its fixture suite must carry a leg that asserts UNARMED is **not** reachable once
any one artifact exists — 137's own leg 6 exists precisely because a fall-back to absent defaults would
*also* have exited 0 via UNARMED and masked the real failure mode.

### Pattern 4: the eleven-leg fixture suite (D-12's first half)

137's suite is the template. Every leg drives the checker as a real `subprocess.run([sys.executable,
str(_SCANNER), *argv])` with `cwd=_HERE` and a mutated env — **never** an in-process import — for legs
1–9; legs 10–11 import the module by file path solely to introspect `_DEFAULT_TARGETS`.

| Leg | Asserts | 146 adaptation |
|-----|---------|----------------|
| 1 | clean fixture via the env seam → exit 0, `PASS:` in stdout | the clean control must carry both caveats, or leg 1 fails for the wrong reason |
| 2 | planted forbidden phrase → non-zero, `FAIL:`, **and the specific label** | plant this milestone's real overclaim shape; assert the label, not just non-zero |
| 3 | planted missing caveat → non-zero, names the caveat bucket | with D-11's per-file rule, this leg needs a target the rule applies to |
| 4 | planted relational-rule violation → non-zero, names the label | 139 has **no** relational rule; 146 inherits none. Replace this leg with a second forbidden-pattern plant (recommended: `proven-unqualified`, the pattern most likely to bite the ledger) |
| 5 | nonexistent target → non-zero, "not found on disk" | unchanged |
| 6 | env seam set to `""` → non-zero, "no scan targets resolved", **and neither `PASS:` nor `UNARMED:` in stdout** | unchanged; this is the never-vacuous leg |
| 7 | two clean controls at once → one `PASS:` naming **both** basenames | anti-skip; unchanged |
| 8 | positional argv beats the env seam (seam→planted, argv→clean, expect 0) | precedence pin; unchanged |
| 9 | **no argv, no env** → exit 0, `PASS:` naming **all five** real basenames | this is the literal mechanical discharge of "armed against the real files". It can only pass once all five artifacts exist — schedule it accordingly (constraint 3) |
| 10 | every `_DEFAULT_TARGETS` entry's `dirname` == this directory | the cross-phase-copy leg |
| 11 | every basename `startswith("146-")` | the stale-name leg |

**The unreachable-leg trap, answered.** Leg 9 is pre-authored against artifacts that do not exist when
the gate is written. Until all five exist it fails — and 137's own docstring records that its leg 9
replaced an earlier UNARMED-expecting leg whose docstring "anticipated exactly this edit." The
recorded rule is: **RED proves nothing until the leg has been seen to pass for the right reason.**
Concretely, for Phase 146 that means three recorded observations per leg, not one:

1. The leg fails **before** the content exists, and the failure message names the *missing artifact* —
   not a syntax error, not a collection error, not a missing fixture.
2. The leg passes **after** the content exists.
3. The leg fails **again** when the content is perturbed (the plant-and-revert of D-12's second half
   supplies this for leg 9 for free).

Phase 145 caught **three** acceptance locators that were false GREENs, one passing against a record
with no content in it at all (145-08's substitution table, rows 1–3) — which is why (1) is not
optional. A leg that has only ever been seen red, or only ever green, is not evidence.

### Pattern 5: the plant-and-revert transcript (D-12's second half)

Fixtures prove the pattern table. They do **not** prove `_DEFAULT_TARGETS` points at the files that
ship — a checker with perfect fixtures and a stale default list is exactly the v1.23 defect. The
recorded sequence:

```bash
# 0. baseline: gate green on the real five, record the PASS line verbatim
python3 146-check-claims.py; echo "exit=$?"          # expect 0

# 1. record byte-identity BEFORE the plant
git hash-object 146-LEDGER.md                        # record; also `wc -c`

# 2. plant ONE forbidden phrase in a REAL artifact (not a fixture)
#    then run with NO argv and NO env override -- the real defaults path
python3 146-check-claims.py; echo "exit=$?"          # expect 1
#    assert: stdout names 146-LEDGER.md AND the line number AND the label

# 3. revert, and PROVE the revert by blob identity, not by eye
git checkout -- 146-LEDGER.md
git hash-object 146-LEDGER.md                        # must equal step 1's SHA

# 4. gate green again
python3 146-check-claims.py; echo "exit=$?"          # expect 0
```

Two cautions measured this session. **First**, `echo "exit=$?"` after a **pipe** reports the last
command in the pipeline, not the script: `python3 scripts/check_size_baseline.py 2>&1 | tail -6; echo
"EXIT=$?"` printed `EXIT=0` for a script that had just printed `FAIL:`. Capture the status of the
script itself. **Second**, `git checkout --` is the correct revert only if the artifact is committed;
if the plant happens before the commit, the revert must be a recorded content restore with the blob
SHA asserted either way.

### Anti-patterns to avoid

- **A glob or recursive walk for `_DEFAULT_TARGETS`.** Measured: catches `146-CONTEXT.md` (6 hits) and
  every PLAN/SUMMARY/RESEARCH file in the directory.
- **Reusing `FIRESTARTER_CLAIMSCAN_TARGETS_V131`.** Already 139's, same milestone.
- **A proximity window.** 139's docstring records the measurement: a windowed scanner passed a file
  carrying **four** planted overclaims because its context tokens never appear in `0x07`/`0x08`/`0x0B`
  vocabulary. D-14 forbids reintroducing one.
- **An exclusion-by-heading quarantine block, or an inline allow-marker, in the claim gate.** D-14
  rejects both. Note that a third mechanism exists in-tree and could be mistaken for precedent:
  `check_record_corrections.py` carries `<!-- recordscan:allow … -->`, `<!-- recordscan:history … -->`
  and `<!-- recordscan:supersedes needle=… lines=… -->`. Those belong to the **record** gate, whose job
  is different (needle staleness over historical prose), and D-14 declines them for the **claim** gate.
- **Quoting a forbidden phrase in order to disclaim it.** The 125 incident: all six `125-0N-SUMMARY.md`
  files trip the claim-ceiling gate because they quote the forbidden phrases inside their own
  compliance paragraphs. v1.22 solved it by citing by `file:line`; D-14 mandates that.
- **Hand-editing `messages.h` or `messages.py`.** Both are codegen output; `messages.py` is
  format-stable and must never be hand-normalized.
- **`roadmap.update-plan-progress` / `phase.complete` / `requirements` verbs for the flips.** `_normalizeMd`
  reformats the whole file, and `phase.complete` is recorded clobbering an unrelated phase's `**Plans:**`
  line. 145-08 hand-edited a single checkbox for exactly this reason and proved it with `--numstat`.

## Don't Hand-Roll

| Problem | Don't build | Use instead | Why |
|---------|-------------|-------------|-----|
| A forbidden-phrase scanner for this milestone's vocabulary | a new pattern table | the twelve patterns in `139-check-claims.py:98-128`, transcribed verbatim | They are *this milestone's* vocabulary, authored against `REQUIREMENTS.md`'s Evidence ceiling, and D-14 forbids loosening them. Re-deriving invites accidental narrowing. |
| A required-caveat check | a new regex | `139-check-claims.py:134-145` — `6\.25\s*V` and `silicon[-\s]margin` | Measured this session: `6\.25\s*V` matches both "6.25 V" and "6.25V"; the pair is already tuned. |
| A fixture-suite skeleton | new test scaffolding | `137/test_check_permitted_claims_v130.py`, leg for leg | Eleven legs, subprocess-driven, with the two mandatory introspection legs. Three milestones old. |
| A ledger structure | a fresh document design | `137-LEDGER.md` → `130-LEDGER.md` → `122-LEDGER.md` | Identity header, "the ceiling quoted verbatim", status/claim key, claim classes as a 4-column table (`Class \| Permitted wording \| Evidence \| Explicitly does NOT prove`), mechanism corrections, negative space, "what no test can close", scanner status. |
| A release-body structure | a fresh outline | `137-RELEASE-NOTES-app.md` (read in full), `130-RELEASE-NOTES-{fw,app}.md`, `122-RELEASE-NOTES-{fw,app}.md` | 137's shape: install line → Removed/Changed → "What is proven, and what is not" → "The ask". 130's fw body adds "State the boundary immediately". |
| The nine gh#15 acceptance boxes | re-scraping the issue body | `139-GH15-ORIGINAL-CRITERIA.md` | **Verified this session:** the file byte-matches the live body's `## Acceptance criteria` tail exactly (`awk '/^## Acceptance criteria/,0' <live body> \| diff - 139-GH15-ORIGINAL-CRITERIA.md` → empty). And it is measured **clean** under the pattern table. |
| The MERGE-05 flash statement | recomputing byte deltas | the verbatim quotable block in `STATE.md` (commit `d02a88a0`) | Authored as *"Wording for Phase 146 / CLOSE-02's honesty ledger, quotable verbatim."* Re-deriving needs a cold rebuild. |
| A `messages.h`/`messages.py` regen | a hand edit or a bespoke script | `bash tools/catalog/sync_to_subrepos.sh` from the meta repo | One command: copies the canonical toml into both sub-repos, asserts they are byte-identical to each other, then regenerates both artifacts. |
| A corrections-register/staleness gate over `.planning` prose | a new checker | `.planning/phases/130-…/check_record_corrections.py` — **already live and green** | See §"The Unnamed Live Gate". It already owns `PROJECT.md`, `STATE.md`, `ROADMAP.md`. |
| Byte-verification of a posted comment | a bespoke normalizer | 139-05's recorded sequence + the named GitHub signature | See §"Posting Mechanics". `sed -e '$a\'` does **not** cancel the residual for this file pair, and 139 says so explicitly. |

**Key insight:** every mechanical artifact this phase needs already exists, one or two milestones back,
in a sibling phase directory, with its own docstring explaining which parts are safe to reuse and which
parts previously failed. The only genuinely new mechanism is D-11's per-file caveat map. The risk in
this phase is not building the wrong tool — it is *writing prose that trips the tool it just built*,
which is why the measured pattern probes below matter more than any design choice.

## The Claim Gate — donor, pattern table, and measured behaviour

### The donor's structure, as it actually is

`.planning/phases/139-gh-15-correction-outward/139-check-claims.py` — 331 lines, stdlib only, read in
full this session. `[VERIFIED: file read 2026-08-17]`

| Element | Location | Notes |
|---------|----------|-------|
| Module docstring | `:1-62` | Records *why* it is a replacement not a copy, with five executed probes; exit-code contract; two explicit non-claims |
| `_HERE` | `:73` | `os.path.dirname(os.path.abspath(__file__))` |
| `_DEFAULT_TARGETS` | `:78-81` | Two entries, both `os.path.join(_HERE, …)` |
| Env seam | `:90-92` | `FIRESTARTER_CLAIMSCAN_TARGETS_V131 = os.environ.get("FIRESTARTER_CLAIMSCAN_TARGETS_V131")` — **no default**, deliberately, so `None` ≠ `""` |
| `FORBIDDEN_PATTERNS` | `:98-128` | Twelve `(label, compiled_regex)` tuples, all `re.IGNORECASE` |
| `REQUIRED_CAVEAT_PATTERNS` | `:134-145` | Two `(label, prose, regex)` tuples |
| `_assert_default_targets_are_local()` | `:148-181` | Prints **every** offending entry, not just the first; returns bool |
| `resolve_targets(argv)` | `:184-202` | argv → env (`is not None`) → defaults; returns `(targets, used_defaults)` |
| `scan_text(text, path)` | `:205-238` | **No window, no context condition**; returns `(forbidden_hits, missing_caveat_labels)` |
| `_print_bucket()` | `:241-246` | Caps display at 20 with an "… and N more" tail |
| `main(argv)` | `:249-326` | self-check → resolve → never-vacuous → partition → fail-closed → scan → report |

**Proximity window: absent, deliberately.** `scan_text`'s own docstring (`:209-212`): *"Carries NO
proximity window and NO context condition of any kind: every regex match in FORBIDDEN_PATTERNS anywhere
in `text` is recorded as a violation, full stop."* The measured justification is in the module docstring
(`:14-20`): the v1.30 checker's window was keyed on tokens (an AT28C part-family name, `SDP`, `0x0D`)
that never appear in `0x07`/`0x08`/`0x0B` vocabulary, so *"a file carrying four planted overclaims was
measured to scan clean under that window."* For contrast, 137's window is at
`137/check_permitted_claims.py:208-219` — lines `[i-1, i, i+1]`, clamped — with a relational
`self-verifying` rule at `:228-241`. **146 inherits 139's design (D-14), not 137's.**

**Explicit non-claim #2, worth carrying forward as a fact about scope** (`139-check-claims.py:57-61`):
the 139 gate *"is **compliance** with the spirit of Phase 146's CLOSE-01 claim gate, and is **not a build
of it** — CLOSE-01 is a Deferred Idea for this phase."* So CLOSE-01 is genuinely unstarted; nothing in
139 discharges any part of it.

### The forbidden-pattern table, verbatim

Transcribed from `139-check-claims.py:98-128`. D-14 forbids loosening any of these.

| # | Label | Regex (all `re.IGNORECASE`) |
|---|-------|------------------------------|
| 1 | `datasheet-conformant` | `datasheet[-\s]conformant` |
| 2 | `datasheet-correct` | `datasheet[-\s]correct` |
| 3 | `algorithm-accurate` | `algorithm[-\s]accurate` |
| 4 | `datasheet-compound-unqualified` | `datasheet[-\s](?:conforming\|compliant\|faithful\|exact\|perfect\|true)` |
| 5 | `verified-on-silicon` | `verified\s+(?:on\|against)\s+(?:real\s+)?silicon` |
| 6 | `silicon-verified` | `silicon[-\s]verified` |
| 7 | `confirmed-working` | `confirmed\s+working` |
| 8 | `works-on-silicon` | `works?\s+on\s+(?:\w+\s+){0,2}silicon` |
| 9 | `proven-on-silicon` | `proven\s+on\s+(?:\w+\s+){0,2}silicon` |
| 10 | `proven-unqualified` | `\bproven\b` |
| 11 | `now-works` | `now\s+works?\b` |
| 12 | `should-now-work` | `should\s+now\s+work` |

Required caveats (`:134-145`), each of which must match at least once in each scanned file under 139's
uniform rule — D-11 makes this per-file for 146:

| Label | Prose | Regex |
|-------|-------|-------|
| `ceiling-voltage` | "the ~6.25 V program-VCC ceiling" | `6\.25\s*V` (no `IGNORECASE` flag needed) |
| `ceiling-narrowing` | "the silicon-margin narrowing that ceiling implies" | `silicon[-\s]margin`, `IGNORECASE` |

### Measured probes — the writing constraints the table actually imposes

Executed this session by importing `139-check-claims.py` by file path and calling `scan_text` on
candidate sentences. `[VERIFIED: probes run 2026-08-17]`

| Candidate text | Verdict | Label(s) |
|----------------|---------|----------|
| `the mechanism is proven, not guessed` | **HIT** | `proven-unqualified` |
| `not proven` | **HIT** | `proven-unqualified` |
| `the proven mechanism` | **HIT** | `proven-unqualified` |
| `bench-proven on one part` | **HIT** | `proven-unqualified` — a hyphen is a non-word char, so `\b` holds after it |
| `unproven on silicon` | **HIT** | `proven-on-silicon` — pattern 9 has **no** leading `\b`, so it matches *inside* "unproven" |
| `unproven` / `remains unproven` / `remain unproven on hardware` | clean | pattern 10's `\b` is not satisfied inside "unproven"; pattern 9 needs the literal word "silicon" |
| `proves the mechanism` | clean | |
| `Nothing here says the algorithm is datasheet-correct` | **HIT** | `datasheet-correct` — **this is `145-BENCH-LOG.md:2709` verbatim** |
| `No datasheet-conformance claim, in either direction.` | clean | "conformance" ≠ "conformant"; safe to reuse |
| `it now works` | **HIT** | `now-works` |
| `should now work` | **HIT** | `now-works` + `should-now-work` |
| `confirmed working` | **HIT** | `confirmed-working` |
| `works on this shield's silicon` | **clean** | pattern 8's `\w+` cannot match `shield's` (apostrophe) — a genuine false negative |
| `verified byte-exact` / `all six writes verified byte-exact` | clean | pattern 5 needs "on/against silicon" |
| `0x07 is bench-validated on one part` | clean | |
| `this milestone claims fidelity, not improvement` | clean | |
| `not-reachable-on-this-hardware` / `met-as-corrected` | clean | CLOSE-04's own disposition vocabulary is safe |
| `the 6.25V ceiling` | satisfies `ceiling-voltage` | `\s*` permits zero space |
| `silicon-margin fidelity is not bought…` | satisfies `ceiling-narrowing` | |

**The single most consequential result: `\bproven\b` matches after a hyphen.** D-09's own phrasing in
CONTEXT — *"`0x07` bench-proven on one part, one controller, one shield revision"* — **would trip the
gate**. So would the bench record's honest "the mechanism is proven, not guessed". D-14 anticipates this
("the closing artifacts must be **written** around it") but does not say what to write. Measured-safe
substitutes: *bench-validated*, *established*, *demonstrated*, *measured*, *evidenced*, *shown*,
*attested*. The 145 record's own D-14 taxonomy already supplies the pair the ledger should use
throughout: **`validated`** and **`skipped-with-reason`**.

**The second consequential result: `works on this shield's silicon` scans clean.** Pattern 8's
`(?:\w+\s+){0,2}` cannot cross an apostrophe. This is a false negative, not a false positive, so it
does not block anything — but a plan may legitimately *add* a pattern (D-14 forbids only loosening).
If it does, the fixture suite must gain a leg for it, and the addition must be recorded as a
strengthening in `146-CITATIONS.md`.

### Measured forbidden-phrase inventory across every candidate file

Run this session with the 139 table over each file, reporting hit count and labels with line numbers.
`[VERIFIED: measured 2026-08-17]`

| File | Hits | Labels (first line numbers) | Relevance |
|------|------|------------------------------|-----------|
| `146-CONTEXT.md` | **6** | `proven-unqualified` @ 81, 162, 191, 268, 418, 539 | **Not** a gate target. Proves a `146-*.md` glob is unusable. |
| `146-DISCUSSION-LOG.md` | **1** | `proven-unqualified` @ 94 | Same. |
| `.planning/ROADMAP.md` | **50** | `datasheet-conformant` @157,580 · `datasheet-correct` @24,32,580,1678,1700 · `algorithm-accurate` @580 · `works-on-silicon` @27 · `proven-on-silicon` @487 · `proven-unqualified` @19,21,25,28,35… | Not a gate target. Line **580** is Phase 146's **own success criterion 1**, which quotes all three headline phrases — the self-reference case in its live form. |
| `.planning/REQUIREMENTS.md` | **4** | `datasheet-conformant` @256 · `datasheet-correct` @257 · `algorithm-accurate` @257 · `proven-unqualified` @141 | Not a gate target. `:256-257` is CLOSE-01's own text. |
| `.planning/PROJECT.md` | **66** | incl. all three headline phrases @204, `now-works`+`should-now-work` @1077, `silicon-verified` @477,487 | Not a gate target. |
| `.planning/STATE.md` | **29** | `datasheet-conformant` @81 · `works-on-silicon` @1630 · `proven-unqualified` @11,387,395,516,613… | Not a gate target. Note `@11` is `last_activity_desc`. |
| `145-BENCH-LOG.md` | **5** | `datasheet-correct` @**2709** · `proven-unqualified` @582, 994, 2952, 3002 | **The record D-03 says the ledger cites.** Quoting boundary 2 (line 2709) verbatim trips the gate. |
| `145-08-SUMMARY.md` | **0** | — | Safe to quote verbatim. |
| `139-GH15-COMMENT.md` | **0** | — | **Safe to quote verbatim** — the reconciliation may reproduce 139's disposition table. |
| `139-GH15-ORIGINAL-CRITERIA.md` | **0** | — | **Safe to quote verbatim** — D-08's nine boxes are gate-compatible. |

**What the planner must take from this table.** (a) The gate's five targets are the only files it may
ever resolve; four of the project's own core planning documents would fail it instantly and correctly
are not in scope. (b) D-03 and D-14 collide over exactly one line, `145-BENCH-LOG.md:2709`, and the
resolution is D-14's: cite it as *"`145-BENCH-LOG.md:2707-2709`, boundary 2"* and paraphrase its content
("no datasheet-conformance claim is made in either direction") rather than quoting the sentence.
(c) D-08's central requirement — grading the original nine boxes with 139's corrections named inline —
carries **zero** gate risk, because both source files are clean.

## The Unnamed Live Gate — `check_record_corrections.py`

CONTEXT names 122/123/137/139's claim gates and the three prior ledgers. It does **not** name a fifth
in-tree checker that Phase 146 will run straight into.

`.planning/phases/130-close-honesty-ledger-claim-gate-release-decision/check_record_corrections.py` is
a planning-record staleness scanner. Run read-only this session:

```
PASS: scanned .planning/PROJECT.md, .planning/STATE.md, .planning/ROADMAP.md,
      .planning/milestones/v1.23-REQUIREMENTS.md, .planning/notes/py32f071-port-branch-state.md;
      exempt hits by verdict: {'block': 23, 'line-label': 4, 'inline-history': 6,
                               'inline-allow': 10, 'superseded': 12}
exit 0
```
`[VERIFIED: executed 2026-08-17]`

Why it matters to this phase, concretely:

1. **It owns three of the four files D-05's `⚠ CORRECTION` blocks land in** — `PROJECT.md`, `STATE.md`,
   `ROADMAP.md`. Its `_DEFAULT_TARGETS` are **absolute** `/workspaces/.planning/…` paths (a *third*
   default-target idiom, distinct from both the `_HERE`-relative and the sibling-string-constant forms).
2. **`⚠ CORRECTION` is already a machine-recognized opener.** The block-label regex is
   `⚠\s*(?:CORRECTION|RESEARCH CORRECTIONS|SUPERSEDED|DESIGN)\b|^SUPERSEDED\b` (`:291`). Using that exact
   glyph-plus-word opener means a 146 correction block is treated as an *exempt region* rather than as
   unlabeled prose. D-05's chosen token is therefore not arbitrary — it is the in-tree contract.
3. **Its needles are all v1.23/py32-specific**, so the risk of a v1.31 correction block tripping it is
   low but non-zero. The twelve needle labels: `py32-buffer-1024`, `branches-27-behind`,
   `host-head-311eacf`, `leonardo-headroom-2992`, `porting-md-dual-slot`,
   `portability-macros-provides`, `host-44-unit-tests`, `cli-handlers-821`, `hex-extension-hardcoded`,
   `third-stack-2c2ed10`, `arm-toolchain-absent`, `part-with-no-vtor`. Note `leonardo-headroom-2992`
   matches a bare `2992` — and Phase 142's summary in `PROJECT.md:87` legitimately contains
   "**92.6% (2130 B headroom)**", not 2992, so no collision today; but any 146 prose that quotes a v1.23
   headroom figure would trip it.
4. **The observed re-pointing confirms the recorded "milestone close breaks its own record gates"
   pattern**: the docstring says it scans `.planning/REQUIREMENTS.md`, but the live target is
   `.planning/milestones/v1.23-REQUIREMENTS.md` — the file was archived and the checker re-pointed.
   A plan that archives or moves anything under `.planning/` must re-run this gate.

**Recommendation:** add one verification leg to whichever plan lands the `⚠ CORRECTION` blocks:
`python3 .planning/phases/130-…/check_record_corrections.py` must still exit 0, with the exempt-hit
tally recorded before and after. It costs one instant command and it is the only standing machine check
over the files D-05 edits.

## gh#15 Live State — re-measured, read-only

Every value below was re-measured in this session with read-only calls. **All five of D-07's measured
premises still hold.** `[VERIFIED: 2026-08-17]`

| Field | Command as run | Result | Matches CONTEXT? |
|-------|----------------|--------|------------------|
| state | `gh issue view 15 --repo henols/firestarter_prom --json state` | `OPEN` | yes |
| title | same, `--json title` | `Implement protocol-specific EPROM programming algorithms in firmware` | yes |
| createdAt | `--json createdAt` | `2026-07-12T09:15:27Z` | — |
| updatedAt | `--json updatedAt` | `2026-08-09T19:32:04Z` | yes — equals the comment's `createdAt`, confirming the bump-on-comment behaviour |
| **`lastEditedAt`** | **GraphQL only** (see below) | **`null`** | yes — the body is unedited |
| comment count | `--json comments`, `\| length` | **1** | yes |
| comment id | GraphQL `databaseId` | **`5233463320`** | yes |
| comment `lastEditedAt` | GraphQL | `null` | the posted correction has never been edited either |
| labels | `--json labels -q .labels` | `[]` | still unlabelled |
| body byte length | `--json body -q .body \| wc -c` | **5964** | byte-identical to 139-CITATIONS §0's measurement |
| unticked boxes | `grep -c '^- \[ \]'` over the body | **9** | all nine still unticked |
| box text identity | `awk '/^## Acceptance criteria/,0' <body> \| diff - 139-GH15-ORIGINAL-CRITERIA.md` | **empty diff** | the extracted-criteria file is still an exact copy of the live tail |

**`lastEditedAt` is not exposed by `gh issue view --json`.** Measured: the field is rejected with
`Unknown JSON field: "lastEditedAt"` and the available-field list does not include it. The body-edit
oracle therefore requires GraphQL:

```bash
gh api graphql -f query='
{ repository(owner:"henols", name:"firestarter_prom") { issue(number:15) {
  number state title createdAt updatedAt lastEditedAt
  comments(first:10){ totalCount nodes { databaseId url createdAt updatedAt lastEditedAt author{login} } }
} } }'
```

This is a correction to any plan that expects `gh issue view --json lastEditedAt` to work — it does not,
and a plan that writes that command will fail at the gate rather than at review.

**The `updatedAt` trap, restated with the live numbers.** `createdAt` is `2026-07-12T09:15:27Z`;
`updatedAt` is `2026-08-09T19:32:04Z`, identical to the comment's `createdAt`. GitHub bumped `updatedAt`
when 139 posted its comment, **not** because the body was edited. 139-05-SUMMARY records that its own
plan's expectation ("`updatedAt` stays `2026-07-12T09:15:27Z`") "rested on a wrong model of GitHub
semantics", and that an earlier draft of the summary falsely claimed the old value had been
re-confirmed. **Posting the 146 comment will bump `updatedAt` a second time.** Any acceptance criterion
written against `updatedAt` will therefore fail for the wrong reason; use `lastEditedAt is null`.

### The original nine acceptance boxes, verbatim

From `139-GH15-ORIGINAL-CRITERIA.md`, confirmed byte-identical to the live body tail. This is the text
D-08 grades. Measured **clean** under the pattern table, so it may be reproduced in
`146-GH15-RECONCILIATION.md` as-is.

```
## Acceptance criteria

- [ ] `0x07`, `0x08`, and `0x0B` use separate write handlers.
- [ ] No new database algorithm flags are introduced.
- [ ] `EPROM_STD` uses per-byte fixed 1 ms pulse/verify cycles and a final overprogram pulse.
- [ ] `EPROM_QUICK` uses its own fixed short-pulse handler.
- [ ] `EPROM_LEGACY` uses a long fixed programming pulse rather than the current adaptive loop.
- [ ] The current block mismatch/adaptive pulse-growth algorithm is removed from EPROM writing.
- [ ] VPP routing remains protocol-correct and is disabled on all exits.
- [ ] Native tests cover dispatch, pulse behavior, verification, failure, and cleanup.
- [ ] All firmware targets build successfully.
```

Live body line numbers, for citation: boxes 1–9 are body lines **155–163**.

### 139's own disposition column, verbatim

From `139-GH15-COMMENT.md` (comment `#5233463320`), §"The acceptance criteria need the same correction,
not just the numbers". This is what D-08 means by "naming the correction". Also measured **clean**.

| Original box | 139's disposition | 139's stated reason (condensed; the comment's own wording is quotable verbatim) |
|---|---|---|
| 1 — separate write handlers | **Replaced** | Protocol owns *shape*; the database owns the *pulse*. One shared per-byte loop driven by a `const` table keyed by `protocol_id` replaces three handlers, on a device with a hard AVR flash budget. |
| 2 — no new DB algorithm flags | **Kept** | Unchanged. |
| 3 — `EPROM_STD` 1 ms + final overprogram | **Corrected** | Per-byte loop and final overprogram kept as the issue's central insight; the `1 ms` is wrong — `0x07`'s modal value is `100 us`, spanning `50`–`1000 us`. |
| 4 — `EPROM_QUICK` own fixed handler | **Corrected** | "Its own handler" falls with box 1; "fixed" falls with the evidence — `0x08` spans `10`–`1000 us` over 6 values, 23 of 127 chips are not `100 us`. |
| 5 — `EPROM_LEGACY` long fixed pulse | **Corrected** | Dropping the adaptive loop kept; "long" is the `50000 us` ×100 bug — the true value is `500 us`. |
| 6 — remove block mismatch/adaptive growth | **Kept** | The issue's core diagnosis; pulse count and overprogram duration belong to the byte. |
| 7 — VPP protocol-correct, disabled on all exits | **Kept** | Unchanged. |
| 8 — native tests cover dispatch/pulse/verify/failure/cleanup | **Kept** | With "dispatch" now meaning table-row selection. |
| 9 — all firmware targets build | **Kept** | Unchanged. |

Plus two body sentences outside the checkbox list that 139 also corrected: *"each protocol must own its
programming state machine and timing constants"* → **replaced**; *"Do not retain the current generic
500 us legacy default."* → **reversed** (500 µs *is* correct; `50000 us` is the bug).

**D-08's mapping falls out directly:** boxes 1, 3, 4, 5 are `met-as-corrected` with 139's own wording
as the named correction; boxes 2, 6, 8 are candidates for plain `met`; boxes 7 and 9 are the two
CONTEXT flags as the interesting ones, and the evidence for both is below.

### Box 7 and box 9 — the evidence, measured

**Box 7 — "VPP routing remains protocol-correct and is disabled on all exits."** Shipped state, read
this session:
- Route resolution is one exposed function, `eprom_hv_route_mask()` (`firestarter/src/proms/eprom.cpp:284-299`),
  driven by the table's `vpp_path` column via `pgm_read_byte`, with `FLAG_VPE_AS_VPP` checked first and
  two fail-closed arms (`row == NULL` → `EPROM_HV_ROUTE_MASK`, unrecognised value → same). Called from
  both `eprom_check_vpp()` and the write path.
- Every **error** exit disables every route through a single-exit wrapper; a **successful** block
  **deliberately stays energised** so the once-per-block settle is not re-paid (`firestarter/CLAUDE.md`
  rows for `0x07`/`0x08`/`0x0B`, all three).
- `command_done()` is the operation-level disable, and its guarantee is asserted as a **source
  contract**, not behaviourally, because `firestarter.cpp` sits outside every native `build_src_filter`
  — a behavioural oracle would need a seventh env (`PROJECT.md:90-93`).
- 144's TEST-04 is explicitly *"bounded to the emitted control-register stream"* (`PROJECT.md:1181`).

So box 7 is honestly `met-as-corrected` **or** `met` with a stated narrowing, and the narrowing has two
independent halves that must both appear: *disabled on all **error** exits, per block; disabled at the
**operation** level by `command_done()`, proven as source not behaviour; and a **successful** block is
left energised by design.* Grading it a bare `met` would assert something the record explicitly declines.

**Box 9 — "All firmware targets build successfully."** This one is materially narrower than CONTEXT's
note suggests, and the reason is new. See §"Neither Repository's CI Has Run Any v1.31 Code" below. The
short form: the three AVR targets are measured building at the tip (`uno` 24920, `uno328pb` 24970,
`leonardo` 27002 B, from the `STATE.md` adjudication), and the fourth target — the ARM `py32f071` CMake
build, which has its own CI workflow and into which `eprom_params.cpp` and `eprom_budget.cpp` were
*registered* by commits `3207632` and `e9f6a92` — has **never been compiled against any v1.31 code**.
Box 9 also carries MERGE-05's admitted +96 B exemption on all three AVR targets.

## Posting Mechanics (D-10) — 139's sequence, exactly

From `139-05-SUMMARY.md`, read in full this session. The whole post was **four** `gh` calls.

**Step 0 — freeze.** Record blob SHA and byte length per artifact, in the citation register:

| File | Frozen blob SHA | Byte length |
|------|-----------------|-------------|
| `139-GH15-COMMENT.md` | `d77a639c62751c197e465ec637f24f330dab35ef` | 12193 |

`[VERIFIED this session: git hash-object on that file still returns d77a639c62751c197e465ec637f24f330dab35ef]`

**Step 1 — fail-closed preconditions, re-measured *in the posting task*, never carried forward.** 139
used four: the verdict string verbatim; `eprom.cpp` one unique blob SHA across `HEAD`/`origin/beta`/base;
`memory.cpp` likewise; both frozen artifacts clean and blob-matching; comment count still at its
expected value. **For 146 the analogous set is:** the typed authorization string verbatim; the frozen
artifact clean (`git status --porcelain` empty for it) and blob-matching the register; the gate green on
all five (constraint 3); and **comment count still exactly 1** (not 0 — 139's comment is there).

**Step 2 — the post.** One call, `--body-file` only, never an inline `--body` or a heredoc:

```bash
gh issue comment 15 --repo henols/firestarter_prom \
  --body-file .planning/phases/146-.../146-GH15-RECONCILIATION.md
```

**Step 3 — fetch-back byte-verify.** 139's measurement: frozen file **12193** bytes, retrieved body
**12194** bytes — a delta of exactly 1, one added blank line at EOF, zero other differences.
`[VERIFIED this session: the live comment still fetches back at 12194 bytes; the frozen file is still 12193]`

The two recorded oracle gotchas, both confirmed:
- **`sed -e '$a\'` does not cancel the residual for this pair.** The frozen file already ends in exactly
  one `\n`, so the idiom is a no-op on it (12193 → 12193). 139-05 states this explicitly: *"the honest
  basis for calling it a pass is the signature match against the precedent, not literal diff emptiness."*
  A 146 plan must write the criterion as *"exactly one added trailing blank line, a +1 byte delta in the
  direction of the retrieved copy, and zero other diff lines"* — **not** as "the diff is empty".
- **`jq '.body | length'` counts codepoints, not bytes.** Measured this session: the live comment is
  **12130** codepoints and **12194** bytes. 139-CITATIONS §0 recorded the same 14-byte discrepancy on the
  issue body (5950 vs 5964) and named `wc -c` as the correct oracle.

**Step 4 — exact-increment state assertion.**
```bash
gh issue view 15 --repo henols/firestarter_prom --json state,comments,labels \
  -q '{state:.state,n:(.comments|length),labels:.labels}'
```
139 asserted `0 → 1`. **146 asserts `1 → 2`, state still `OPEN`, labels still `[]`.**

**Step 5 — the negative-flag audit.** 139 tabulated the literal argv of every `gh` call against a
forbidden-flag list and recorded each as absent: `--label`/`--add-label`/`-l`, `--assignee`,
`--milestone`, `--project`, `--web`, `--editor`, `--edit-last`/`--delete-last`, inline `--body`,
heredoc body construction, `gh issue close`, `gh auth token`, `gh issue edit`. **146 should reproduce
this table verbatim, adding `gh workflow run`, `gh release`, `git push`, `git merge` and `git tag` per
D-01/constraint 5.** Asserting a *negative* argv is the recorded discipline (a `--label` that needs a
pre-existing label is a known failure mode in this project).

**Permission-layer note, measured.** `.claude/settings.local.json`'s allowlist contains
`Bash(gh run:*)`, `Bash(gh release:*)`, `Bash(gh workflow:*)`, `Bash(git push:*)` and per-sub-repo push
entries — but **no** entry for `gh issue comment`. So the post will surface a permission prompt, which
is an extra human checkpoint and is fine. Two consequences the planner should carry: (a) 139 recorded
that its post *"was not refused by the permission layer… no permission-grant negotiation, no settings
edit, no `gh api --method POST` workaround"* — the same standard applies, and a plan must **not** add an
allowlist entry to make the call smoother; (b) conversely, `git push` **is** allowlisted, so D-01's
no-push rule has **no mechanical enforcement** — it is plan discipline only. Recommend an explicit
structural gate: a task-level assertion that `git rev-list --count @{u}..HEAD` is unchanged in all three
repos between phase start and phase end, and a negative-argv audit naming `push`/`merge`/`tag`.

## The Seven Inherited Corrections — every site located, every figure re-verified

D-04 names seven. Below, each with its false-statement site at `file:line`, the shipped fact re-measured
against source, and a verdict on whether the correction holds **as CONTEXT states it**. Three do not.

### (1) 143 D-01's `ROADMAP.md` / `PROJECT.md` prose — **HOLDS for ROADMAP, does NOT hold for PROJECT**

**Site:** `.planning/ROADMAP.md:380` —
> `**Depends on**: Phase 138 (PREP's verified app branch base). Independent of Phases 140–142 (different repo); converges with them at Phase 144's cross-repo constants-parity leg.`

**Why false:** HOST-02's mechanism is a **firmware** emission from inside Phase 141's per-byte loop
(`firestarter/src/proms/eprom.cpp:428-432`, the `#ifndef SERIAL_ON_IO` `MSG_DATA_PROGRESS` emit), and
HOST-01's budget is computed from Phase 140's table (`include/eprom_budget.h`, reading
`max_pulses`/`energy_cap_us`/`overprogram_factor`/`overprogram_cap_us`). 140/141/142 are landed
prerequisites, not parallel peers, and the phase is dual-repo. `[VERIFIED against source]`

**The charter:** `.planning/ROADMAP.md:392` already carries the recorded correction and names its owner
verbatim — *"Recording the correction is Phase 143's obligation; amending this prose and the milestone's
matching sequencing sentence is Phase 146 / CLOSE-04's, alongside C3, F-140-05, F-140-07 and H3."*

**⚠ The `PROJECT.md` half has no false-statement site.** `grep -n "Independent of Phases 140"
.planning/PROJECT.md` returns **nothing**. What `PROJECT.md` actually carries is the *routing note*, at
`:130-131` (live milestone section) and again at `:1183` (the Phase 143 footer): *"D-01's ROADMAP-prose
correction (this phase is not independent of 140–142) is deferred to Phase 146 / CLOSE-04 by design."*
That statement is **true**, and a `⚠ CORRECTION` block on it would be a correction of a correct
sentence. **Recommendation:** correct `ROADMAP.md:380`; update `PROJECT.md:131`'s deferral note from
"deferred to Phase 146" to "discharged at Phase 146" (a status update, not a correction block); leave
the dated footer at `:1183` alone as history. `[VERIFIED: grep returned zero hits in PROJECT.md]`

### (2) The milestone's matching sequencing-spine sentence — **HOLDS**

**Site:** `.planning/ROADMAP.md:167`, §"Sequencing spine (hard, not preference)". The false clause,
verbatim:
> `HOST (143) is independent of 140–142 (different repo) and can run in parallel with them;`

Same falsification as (1). Note the sentence is one long paragraph covering the whole spine — the
correction must surgically address that clause without disturbing the PREP/ISSUE/TABLE/LOOP/VPP/BENCH/CLOSE
statements around it, which are all correct.

### (3) C3 / 141 H3 — the unclamped `extract_long` — **HOLDS, and is narrower than it reads**

**Site of the mechanism:** `firestarter/src/json_parser.c:503`:
```c
bool get_delay(const char* json, jsmntok_t* tokens, int pos, firestarter_handle_t* handle) {
    extract_long("pulse-delay", handle->pulse_delay);
}
```
with the macro chain at `:272-282` — `extract_long` → `extract_num(…, simple_strtoul)` — and
`handle->pulse_delay` declared `uint32_t` at `include/firestarter.h:197`. **No clamp anywhere.**
`[VERIFIED: all four sites read this session]`

**Site of the false claim:** `.planning/PROJECT.md:155`, the C3 row of the corrections table:
> `| **C3** | Need a 32-bit-safe delay because of the 50 ms pulse | Helper is still needed, **for the overprogram pulse** — 3 × 25 × 1000 µs = 75 ms exceeds delayMicroseconds()'s 16383 µs ceiling. With C1 applied, no *pulse* comes near it. |`

The clause *"no pulse comes near it"* is true of `chip_database.json` data (whose full pulse set is
10/20/50/100/200/500/1000 µs) and **false of the wire**. `143-HOST-RECORD.md` §5 non-claim 6 states this
in the same terms.

**Two narrowings the correction must carry, both measured this session and neither stated in CONTEXT:**

- **The over-ceiling value is no longer routed through a bare `delayMicroseconds`.** Phase 141 added
  `mem_util_delay_us` (`firestarter/src/proms/memory.cpp:315-323`, with `MEM_UTIL_DELAY_US_MAX 16383UL`
  at `:34`), and the program pulse now goes through it: `memory.cpp:409` is
  `mem_util_delay_us(handle->pulse_delay);`. So the honest statement is *"an arbitrarily large
  `pulse-delay` is accepted from the wire and will be **delivered** as a delay of that length"* —
  **not** *"it will silently truncate"*. The 16-bit truncation hazard C3 describes was real
  pre-Phase-141 and is now mitigated by the split-delay helper.
- **`0x0B` refuses over-cap pulses; `0x07`/`0x08` do not.** `eprom.cpp:105-110` refuses pre-flight with
  `MSG_ERR_PULSE_TOO_WIDE` — but only `if (energy_cap_us > 0 && handle->pulse_delay > energy_cap_us)`,
  and `energy_cap_us` ships **`0`** on `0x07` and `0x08` (`eprom_params.cpp:46-48`). So the unbounded
  path is live on `0x07`/`0x08` only. That is exactly backlog **999.31**'s subject and exactly
  T-145-45's overstatement (145-BENCH-LOG carry-forward row 11).

So the correction's honest content is: *the wire field is unclamped and an over-ceiling value is
reachable today; it is delivered rather than truncated because of `mem_util_delay_us`; the only
firmware-side refusal is `0x0B`'s, gated on `energy_cap_us > 0`, which is `0` on `0x07`/`0x08`.*

### (4) 141 H4 — the honest energy-cap ceiling — **HOLDS, and is fully derivable from source**

The correct figures: **exactly 50 ms** on every shipped `0x0B` width, and **99998 µs** worst case for an
arbitrary width. Re-derived from source this session:

- `energy_cap_us = 50000UL` on the `0x0B` row (`eprom_params.cpp:48`), `0UL` on `0x07`/`0x08`.
- The loop adds *before* testing: `accumulated += org_delay;` then, after a failed verify,
  `if (energy_cap_us && accumulated >= energy_cap_us)` (`eprom.cpp:463, 474`). So the last pulse can
  overshoot the cap by up to `pulse − 1`.
- Shipped `0x0B` widths are 200/500/1000 µs (139's own histogram: `500 ×21, 1000 ×6, 200 ×5`, n=32).
  50000 divides evenly by all three → 250/100/50 pulses, `accumulated` landing on exactly 50000. Hence
  "capped at 50 ms" is **exact** for shipped data.
- Worst case for an arbitrary width, under the pre-flight refusal: `w = energy_cap_us` permits only one
  pulse (a second needs `(i−1)·w < energy_cap_us`, which fails at `w == energy_cap_us`), so the largest
  achievable is two pulses at `w = 49999` → **99998 µs**, not 99999.

`[VERIFIED: source arithmetic re-derived; the same derivation is already written out in
firestarter/CLAUDE.md's 0x0B row, line 66]`

**Site of the false figure:** `141-CONTEXT.md` D-01's larger figure (`50000 + 65535` µs). Note
`141-LOOP-RECORD.md` §12 H4 says it *"deliberately does not restate that figure's numeral"* — so a 146
correction block naming the number would be the first place it is restated. **Recommendation:** cite it
as *"`141-CONTEXT.md` D-01's figure"* by location, consistent with D-14's citation discipline, rather
than reproducing the arithmetic.

### (5) F-140-05 — the throughput table — **HOLDS, but it is TWO rows, not one**

**Site:** `.planning/PROJECT.md:208-214`:

| algorithm | pulse | max pulses | overpulse | typical | worst case |
|---|---|---|---|---|---|
| `0x07` | `handle->pulse_delay` | 25 | `3 × N × pulse`, cap 75 ms | ~0.25 s @100 µs; ~2.05 s @1000 µs | ~51 s |
| `0x08` | `handle->pulse_delay` | 25 | `3 × N × pulse` | ~0.2 s | ~13 s |
| `0x0B` | `handle->pulse_delay` | 50 ms energy cap | none | ~0.8 s | ~25.6 s |

**Shipped table, measured** (`firestarter/src/proms/eprom_params.cpp:45-49`, columns per
`include/eprom_params.h:51-58` — `overprogram_cap_us, energy_cap_us, max_pulses, overprogram_factor,
verify_mode, vpp_path`):

| row | overprogram_cap_us | energy_cap_us | max_pulses | **overprogram_factor** | verify_mode | vpp_path |
|---|---|---|---|---|---|---|
| `0x07` | 75000 | **0** | 25 | **0** | `VERIFY_PER_PULSE_PLUS_FINAL` | `VPP_PATH_DROP_RESISTOR` |
| `0x08` | 75000 | **0** | 25 | **0** | `VERIFY_PER_PULSE_PLUS_FINAL` | `VPP_PATH_DROP_RESISTOR` |
| `0x0B` | 75000 | **50000** | 255 | **0** | `VERIFY_PER_PULSE` | `VPP_PATH_DIRECT_VPE` |

**⚠ CONTEXT names only the `0x07` row; the `0x08` row carries the same false implication.** Both give an
overpulse of `3 × N × pulse` while both ship `overprogram_factor = 0`. This is not an inference — the
shipped source says so in its own comment (`eprom_params.cpp:41-43`): *"0x08 overprogram_factor = 0
resolves D-06 from primary datasheets, agreeing with PROJECT.md's prose and CONTRADICTING PROJECT.md's
own throughput table — the contradiction is named here, not smoothed."* And `140-PARAM-TABLE-RECORD.md`
§11's hand-off row owes CLOSE-04 **three** things, not two: *"F-140-05 (§3, the 0x07 Intel-family split
candidate), the 0x08 contradiction (§4, D-06), and F-140-07."*

Two further notes. `PROJECT.md:173`'s prose — *"Overprogram pulse — `3 × N × pulse` capped at 75 ms
**where `overprogram_factor > 0`**"* — is correctly conditional and needs no correction. And the
`0x0B` row's `max pulses` cell reads "50 ms energy cap", conflating two columns: the shipped
`max_pulses` on that row is **255**. Whether to fix that too is discretion; it is a third defect in the
same table.

Also worth surfacing for the ledger: the `0x07` row's *"worst case ~51 s"* and `0x08`'s *"~13 s"* are
computed **with** the overpulse. With `overprogram_factor = 0` they are wrong in the conservative
direction. And `PROJECT.md:216` — *"Faster than today in the typical case"* — is a **comparative
claim**, which 145 D-08 and boundary 1 explicitly forbid this milestone from making (no control run
exists). That sentence is a candidate eighth correction; flagging it, not deciding it.

### (6) F-140-07 — the public justification — **HOLDS for the public and `.planning` halves; ALREADY DONE in `doc/PROTOCOLS.md`**

**The false statement, verbatim, in three live places:**

| Site | Text |
|------|------|
| **gh#15 comment `#5233463320`, line 39** (public) | ``- `0x0B` loops pulse-then-verify with a 50 ms accumulated-energy cap per byte (`100 × 500 us`, which is the classic 2716 total programming time) and no overpulse row at all.`` |
| `.planning/REQUIREMENTS.md:20` (D-02 rationale) | ``…`100 × 500 µs = 50 ms` is exactly the classic 2716 total programming time, so both readings are satisfied.`` |
| `.planning/PROJECT.md:176-181` (target-features bullet) | ``…**cap accumulated program time per byte at 50 ms**, since `100 × 500 µs = 50 ms` is exactly the classic 2716 total programming time.`` |
| `.planning/PROJECT.md:1187` (v1.31-start footer) | same clause, inside the dated footer |
| `.planning/STATE.md:67` | ``(`100 × 500 µs` = the classic 2716 total programming time), satisfying both readings. No overpulse.`` |

**The fact:** `140-PARAM-TABLE-RECORD.md:259` — the TI TMS 2516 datasheet states total programming time
for all bits as **100 seconds**; 50 ms is the per-location `t_w(PR)` TYP (45/**50**/55 ms). The **value**
(50000 µs) has a genuine primary datasheet basis; the published **reason** does not.

**⚠ Already corrected in `firestarter/doc/PROTOCOLS.md` §1.5.** Measured this session — the shipped
doc already carries, in place, a labelled correction:
> *"**Recorded, not applied here (F-140-07):** the justification published for the 50 ms figure — "100 x 500 µs is the classic 2716 total programming time" — is factually wrong: this same TI TMS 2516 datasheet states its own total programming time for all bits is **100 seconds**, and 50 ms is the per-location pulse width, not a total. … Phase 146 / CLOSE-04 reconciles the posted text; this phase records the correction without editing it."*

So the doc half of F-140-07 is **discharged** (by 140-06). What Phase 146 owes is: the **public**
correction on gh#15 (D-07's decisive argument), and `⚠ CORRECTION` blocks at the four `.planning` sites
above. Note the doc's own paragraph is itself a usable template for the block's wording.

**Also worth noting for the reconciliation's honesty:** the doc's §1.5 additionally records that TI's
TMS 2516 specifies a **single 50 ms pulse per location**, permits verification immediately after each
location, and specifies **no final full-array pass and no overprogram** — while the firmware ships a
*looped* pulse-verify with a 50 ms accumulated cap. The record's position is that this satisfies both
readings (milestone D-02). That nuance belongs in the box-5 grading.

### (7) F-141-07 + F-144-01 — the message wording and the stale env total — **BOTH HOLD**

**F-141-07 — the two orphaned catalog ids.** Measured this session:

| Id | Catalog site (all three copies) | Current text | Generated artifacts |
|----|-------------------------------|--------------|---------------------|
| `MSG_INFO_RETRIES` (`0x51`) | `tools/catalog/messages.toml:163-167` | `format = "Number of retries: %d"`, `severity = "INFO"`, `params = [{ type = "u8" }]`, `wire_format = "id_frame"` | `firestarter/include/messages.h:51`; `firestarter_app/firestarter/messages.py:66` and `:252` |
| `DBG_PULSE_DELAY_MISMATCH` (`0x15`) | `tools/catalog/messages.toml:922-924` | `format = "Mismatch, retrying with increased pulse delay from %d to %d"`, `params = [{ type = "u8" }, { type = "u8" }]` | `firestarter/include/messages.h:137`; `firestarter_app/firestarter/messages.py:842` and `:1070` |

`141-LOOP-RECORD.md` §6: both ids are unreferenced by firmware (whole-tree grep of `src/`/`include/`,
zero call sites outside their own `#define`), the decision is to **leave both assigned and unedited**
(no orphan-id gate exists; deleting an id risks a later reuse collision), and
`DBG_PULSE_DELAY_MISMATCH`'s wording *"actively contradicts shipped behaviour — the new loop never
increases pulse delay; every pulse is fixed-width."* D-06 corrects the **wording** and **records**
`MSG_INFO_RETRIES`'s orphan status without removing it.

**F-144-01 — the stale `native_loop_v131` total.** Site: `firestarter/CLAUDE.md:277-279`:
> *"**Phase 142 addition:** `[env:native_loop_v131]` now runs **two** suites -- the pre-existing `test_loop_eprom_v131` (**39 cases**) plus the new `test_vpp_eprom_v131` (32 cases), **71 cases total**…"*

Measured truth: `144-TEST-RECORD.md:139` — `native_loop_v131` **79**, 2 suites (`test_loop_eprom_v131`
**47** + `test_vpp_eprom_v131` 32); `:145` confirms 47 + 32 = 79; `:518` is F-144-01 itself, routed to
"Phase 146 / CLOSE-04", *"Named, not fixed here."* So **two** numerals are stale in that sentence: `39`
→ `47`, and `71` → `79`. `PROJECT.md:82` also carries the historical `71/71` in the Phase 142 summary —
that one was correct when written and is history, not a defect.

### Correction-site summary table (for the register)

| # | Origin finding | False-statement site(s) | Verdict |
|---|----------------|-------------------------|---------|
| 1 | 143 D-01 | `ROADMAP.md:380` | holds |
| 1b | 143 D-01 (`PROJECT.md` half) | **none — no false site exists**; `PROJECT.md:131` / `:1183` carry a true routing note | **does not hold as stated** |
| 2 | 143 D-01 (spine) | `ROADMAP.md:167` | holds |
| 3 | C3 / 141 H3 | `PROJECT.md:155` (C3 row); mechanism at `json_parser.c:503` | holds, with two measured narrowings |
| 4 | 141 H4 | `141-CONTEXT.md` D-01's figure (cite by location) | holds |
| 5 | F-140-05 | `PROJECT.md:212` **and `:213`** (two rows); `:214` conflates a third cell | holds, **broader than stated** |
| 6 | F-140-07 | gh#15 comment line 39 (public); `REQUIREMENTS.md:20`; `PROJECT.md:176-181`, `:1187`; `STATE.md:67` | holds; **`doc/PROTOCOLS.md` §1.5 already done** |
| 7a | F-141-07 | `messages.toml:922-924` ×3 (wording); `:163-167` ×3 (orphan, record only) | holds |
| 7b | F-144-01 | `firestarter/CLAUDE.md:277-279` (**two** stale numerals) | holds |
| — | candidate 8th | `PROJECT.md:216` — "Faster than today in the typical case" is a comparative claim 145 D-08/boundary 1 forbids | **surfaced, not decided** |

## CLOSE-03 Documentation Targets — measured coverage at the tip

### The five-topic × six-file matrix

Measured this session by keyword count per file (ERE, case-insensitive) plus reading each hit in
context. `✓` = present and correct; `~` = present but incomplete or stale; `✗` = absent.
`[VERIFIED: 2026-08-17, firestarter @ fa6c9c7 / firestarter_app @ 68820a6]`

| CLOSE-03 topic | `firestarter/CLAUDE.md` (282 ln) | `firestarter/doc/PROTOCOLS.md` (496 ln) | `firestarter/README.md` (129 ln) | `firestarter_app/README.md` (711 ln) | `firestarter_app/CLAUDE.md` (114 ln) | `firestarter_app/doc/protocol-{id,flags}.md` |
|---|---|---|---|---|---|---|
| 1. the per-byte algorithm | **✓** (4 hits; rows 64/65/66 describe pulse→verify, `verify_mode`, budgets) | **~** (1 hit; §1.3 still says Phase 141 *will* replace the loop) | ✗ | ✗ | ✗ | ✗ |
| 2. the parameter table | **✓** (3 × `eprom_params`) | **✓** (5 × `eprom_params`) | ✗ | ✗ | ✗ | ✗ |
| 3. the database-supplied pulse | **✓** (5 × `pulse.delay`) | **✓** (7 × `pulse.delay`, incl. INV-06 at `:474`) | ✗ | **~** (6 × `pulse-delay`, all in §Eprom Configuration as a DB field; nothing about the firmware reading it per byte) | **~** (1 hit) | ✗ |
| 4. `--pulse-us` | **✓** (3 hits; `:136-137` is a dedicated interaction paragraph) | **✗ (0 hits)** | ✗ | **✗ (0 hits)** — the §Write options list at `:315-318` omits it | ✗ | ✗ |
| 5. the 6.25 V accepted debt | **✗ (0 hits)** — `6\.25` = 0, `silicon.margin` = 0 | **✗ (0 hits)** | ✗ | **✗ (0 hits)** | ✗ | ✗ |

**Headline: topic 5 appears in NO sub-repo document at all.** `grep -c '6\.25'` returns 0 in every one
of the six files. The 6.25 V ceiling lives entirely in `.planning/REQUIREMENTS.md` §"Evidence ceiling",
in the gh#15 comment, and in `include/eprom_params.h:38-40`'s code comment (*"The datasheets' raised-VCC
verify margin is unreachable on this shield's ~6.25V ceiling, so no value in this column may ever encode
a verify VCC"*) — never in a document a user or a firmware developer reads. That is the single largest
CLOSE-03 gap and the one D-13's checker will be most valuable against.

**Second gap: `--pulse-us` is invisible on the host side**, which is where a user meets it. Zero hits in
`firestarter_app/README.md` and zero in `firestarter_app/doc/*.md`. This is 143 H5, routed to
CLOSE-03 verbatim: *"The `--pulse-us` documentation entry. This phase ships the flag; the doc chapter is
Phase 146's."*

### `firestarter/doc/PROTOCOLS.md` — the exact stale sentence, and what is already fine

**Structure:** §1.3 `0x07` at lines **129-167**; §1.4 `0x08` at **168-201**; §1.5 `0x0B` at **202-235**.
Each has the same five sub-headings: **Write algorithm**, **Erase model**, **VPP behavior**, **Pin
roles**, plus per-item `Citation:` lines. §3 is an Invariant Traceability Matrix (INV-06 at `:474` pins
the pulse-delay fallbacks).

**The stale sentence, verbatim, §1.3 (within lines 147-149):**
> *"The firmware's present loop (`eprom.cpp:159-179`) is **retry escalation of `pulse_delay`**, not an Intel 3N margin pulse; **Phase 141 replaces it.**"*

Phase 141 landed five phases ago (commit `3504e50`, *"rewrite eprom_write_execute as a per-byte pulse-to-verify
loop"*). Both halves are now wrong: the present loop is **not** retry escalation, and the line reference
`eprom.cpp:159-179` no longer points at a write loop (the per-byte loop's inner `for(;;)` is at
`eprom.cpp:449-478` at this tip). `[VERIFIED: read both the doc and the source this session]`

**What §1.3 already gets right** and must not be re-derived: pulse width as a database datum with the
1000 µs `pulse_delay == 0` fallback and the 100 µs modal value across 113 of 170 chips; `max_pulses = 25`
with the three-datasheet basis (Winbond W27C512 Rev A4, ST M27C512 Rev 3 §2.6, Microchip 27C512A
DS11173G §1.6) and the note that Microchip specifies 10; **no overprogram on this row**
(`overprogram_factor = 0`) with all three datasheet citations; and F-140-05's named, scoped divergence
(the 22 Intel-family 1 ms parts) already pointing at Phase 146 as the follow-up.

**What §1.4 already gets right:** the Quick-Pulse/Flashrite/PRESTO family, the 100 µs modal value
(104 of 127), `max_pulses = 25`, `overprogram_factor = 0` resolved from three vendors — **and it already
names PROJECT.md's throughput-table contradiction in place** (*"contradicts `PROJECT.md`'s own
throughput table, which gives 0x08 a `3 x N x pulse` overpulse (D-06, named in the Phase 140 record; not
edited here)"*). So F-140-05's `0x08` half is already recorded doc-side; only `PROJECT.md` needs the
block.

**What §1.5 already gets right:** the TI TMS 2516 basis, the 50 ms `energy_cap_us`, the 500 µs fallback,
and F-140-07's full in-place correction (quoted above). **F-140-09 was already fixed by 140-06** — the
false "JEDEC Intelligent Programming (1 ms pulse × N + 3× overpulse)" claim and its nonexistent
`W27C512.pdf p.7 §6.2` citation were removed. Phase 146 does not redo any of that.

**Not covered anywhere in §§1.3-1.5:** `--pulse-us`, the 6.25 V ceiling, the intra-block
`MSG_DATA_PROGRESS` emission and its `leonardo`-only boundary, the CAP-03 advertised budget, and the two
VPP settle constants the debug session raised.

### `firestarter/CLAUDE.md` — already carries four of five topics

**Structure:** §Algorithm Handlers at `:57-75` (a wide table, one row per protocol — the `0x07` row is
`:64`, `0x08` is `:65`, `0x0B` is `:66`, each a single very long line); §Operation-Setup Ack
(CAP-01/02/03) at `:103-146`, with the `--pulse-us` interaction paragraph at `:136-137`; §Constants at
`:154`; §Native (Host) Test Environment at `:198-282`, with the pinned-env exception at `:260-275` and
the Phase 142 addition (carrying F-144-01's two stale numerals) at `:277-282`.

The `0x0B` row (`:66`) is remarkably complete already: it documents the 50 ms `energy_cap_us`, the
exact-divisibility argument for shipped widths, the full 99998-vs-99999 derivation, `max_pulses` 255,
all three budget/refusal message ids and which are reachable, the shared `eprom_hv_route_mask()`
resolution, the error-exit/successful-block disable asymmetry, `command_done()` as a source contract,
and the `MSG_DATA_PROGRESS` emission with its EPROM-path-only / `leonardo`-only boundary.

**So the firmware half of CLOSE-03 is mostly a `doc/PROTOCOLS.md` job plus one 6.25 V paragraph.** The
discretionary split CONTEXT flags resolves naturally: `CLAUDE.md` needs (a) the F-144-01 numeral fix and
(b) a 6.25 V sentence; `doc/PROTOCOLS.md` needs (c) the stale §1.3 sentence replaced with the shipped
loop, (d) `--pulse-us`, and (e) the 6.25 V debt — it is the per-protocol reference a firmware developer
reads, and it is the one that went stale.

### `firestarter/README.md` §Protocol Notes — a natural home, currently 27C-silent

Lines **111-116**, six lines, entirely about `0x0D` (no erase op, page auto-erase, unreadable SDP state)
with a pointer to `doc/PROTOCOLS.md` §1.6. Nothing about 27C at all. A short 27C paragraph here — "how
programming works now, and the one thing this shield cannot do" — is the user-facing firmware surface
CONTEXT names, and it costs 5-8 lines.

### `firestarter_app/README.md` — and two defects beyond the missing flag

**Structure:** §Write at `:308-326`, with `##### Options` at `:315-318` and `##### Description` at
`:319-326`; §Override and adding to the database → §Eprom Configuration at `:530-571`, documenting the
`pulse-delay` DB field and the `~/.firestarter/database.json` override path (the W27C512 example JSON
carries `"pulse-delay": "0x0064"`).

**The README's `write` options list, verbatim (`:316-318`):**
```
* `-b, --ignore-blank-check`: Ignore blank check before write (and skip erase).
* `-f, --force`: Force write, even if the VPP or chip ID don't match.
* `-a, --address <address>`: Write start address in decimal or hexadecimal.
```

**The shipped `write` surface, measured from `firestarter/cli_handlers.py:546-610`:** seven options —
`-b/--no-blank-check`, `--skip-erase`, `-f/--force`, `-a/--address`, `--vpe-as-vpp`, `--pulse-us`,
`--skip-sdp-unlock`. `[VERIFIED: extracted programmatically from the decorator block]`

So the README is stale in **three** ways, only one of which CONTEXT names:

1. **`--pulse-us` is absent.** (143 H5, CLOSE-03's.)
2. **`-b`'s long name is wrong.** Shipped is `--no-blank-check`; the README says `--ignore-blank-check`.
3. **`-b`'s described behaviour is wrong.** The README says it skips erase too; shipped `-b` is
   `blank_check` only, and skipping erase is now a **separate** `--skip-erase` flag whose own help text
   carries a WARNING (*"skipping erase on a non-blank electrically-erasable chip leaves un-erased bits
   that cannot be reprogrammed"*). The README documents neither `--skip-erase`, `--vpe-as-vpp`, nor
   `--skip-sdp-unlock`.

Items 2 and 3 are outside CLOSE-03's five topics and are a judgement call — but they sit in the exact
lines a `--pulse-us` entry must be inserted into, and leaving a known-wrong safety-relevant line
untouched while editing its immediate neighbours is the kind of thing the operator wording review will
catch. **Recommendation:** fix all three in one edit and record items 2/3 in `146-CORRECTIONS.md` as
in-scope-by-adjacency, with `--skip-erase`'s warning carried over verbatim.

**The shipped `--pulse-us` help text, quotable verbatim** (`cli_handlers.py:590-593`):
> *"Override the database program-pulse width for this run (microseconds, 1-65535). This bound is minipro parity (`-o pulse=N` is a uint16), NOT a wire-type or hardware limit -- see `write()`'s docstring."*

That sentence already states the provenance narrowing 143 non-claim 6 requires, and it is the right
basis for both the README entry and the release-notes paragraph.

### The recorded "host gates that scan firmware source fail OPEN" trap

Relevant to D-13's checker if it is written host-side or made cross-repo. The recorded pattern: gates in
`firestarter_app` that scan `firestarter` source break on firmware renames and **fail open** — 4× in
Phase 117. Confirmed live: `firestarter_app/tests/test_py32_flash_map_host.py` imports
`FW_ROOT, fw_path, requires_fw` from `tests/fw_presence` and is `requires_fw`-gated; 144's own record
(`PROJECT.md:1181`, disclosure 4) states *"the app's CI does not exercise the cross-repo parity gates;
those `requires_fw` gates fail **OPEN** across the repo boundary by design."*

**Mitigation for D-13:** host the checker in the **phase directory** (`.planning/phases/146-…/`), give
it an explicit `_DEFAULT_TARGETS` list of absolute-or-`_HERE`-relative doc paths spanning both sub-repos,
and give it a **fail-closed missing-target branch** so a renamed or moved doc is a hard failure rather
than a skip. That is the 139 shape and it is immune to the fail-open pattern because nothing about it is
`requires_fw`-conditional. It must also carry a **non-vacuity** leg: an emptied or repointed target list
must exit 1, not 0 — 144 built exactly such a leg for its mapping gate (*"a non-vacuity leg so an emptied
scan root fails instead of passing over an empty set"*).

## The `messages.toml` Wording Path (D-06, constraint 7)

### Five copies exist; exactly three are in scope

Measured by size and SHA this session:

| Path | Bytes | SHA-256 (first 12) | In D-06's lockstep? |
|------|-------|--------------------|---------------------|
| `./tools/catalog/messages.toml` (meta, canonical) | 27885 | `cae8f4eaf26d` | **yes** |
| `firestarter/tools/catalog/messages.toml` | 27885 | `cae8f4eaf26d` | **yes** |
| `firestarter_app/tools/catalog/messages.toml` | 27885 | `cae8f4eaf26d` | **yes** |
| `firestarter_py32_ci/tools/catalog/messages.toml` | 23933 | `cfdcd61d3a95` | **no** — scratch worktree, already divergent |
| `firestarter_app_py32/tools/catalog/messages.toml` | 24290 | `f0cccce8562e` | **no** — same |

The three real copies are **byte-identical to each other right now**, which is the invariant the sync
script asserts. The two py32 copies are already different files (older catalogs) — consistent with
CONTEXT's warning that `.planning/config.json`'s `planning.sub_repos` lists four repos and a naive
iteration reaches two scratch worktrees. **Iterate the two named sub-repos explicitly.**
`[VERIFIED: 2026-08-17]`

### The regen command — one command, from the meta repo

`tools/catalog/sync_to_subrepos.sh`, read in full. It does three things: (1) copies `messages.toml` **and**
`codegen.py` from `./tools/catalog/` into both sub-repos' `tools/catalog/`, diffing each copy; (2) asserts
the two sub-repo tomls are byte-identical to each other; (3) regenerates both artifacts:

```bash
# from /workspaces (the meta repo root)
bash tools/catalog/sync_to_subrepos.sh
```

which internally runs:
```bash
python3 tools/catalog/codegen.py --catalog tools/catalog/messages.toml \
        --language cpp    --target firestarter/include/messages.h
python3 tools/catalog/codegen.py --catalog tools/catalog/messages.toml \
        --language python --target firestarter_app/firestarter/messages.py
```

**The edit therefore lands in ONE place** — `./tools/catalog/messages.toml` — and the script propagates
it. A plan that hand-edits all three tomls is doing the script's job and risks divergence; a plan that
edits only a sub-repo copy will have it **overwritten** by the next sync. Edit the canonical copy.

### ⚠ Two traps in the sync script itself

**Trap 1 — the script's own verification steps are vacuous.** Steps 2 and 3 each print an "OK:
regenerated" line gated on a **self-comparison**:
```bash
if diff -q "$FS_ROOT/include/messages.h" "$FS_ROOT/include/messages.h" >/dev/null 2>&1; then
    echo "  OK: firestarter/include/messages.h regenerated."
fi
```
A file always equals itself, so that line proves nothing. The copy diffs in step 1 and the cross-sub-repo
diff are real; the two regen confirmations are not. **A plan must not cite those lines as evidence.**

**Trap 2 — `codegen.py --check` does NOT check the target.** Measured: it validates the *catalog* and
returns, before any target comparison (`codegen.py:704-713` — `if args.check: print("OK: catalog valid
(…)"); return 0`). Both invocations printed `OK: catalog valid (76 messages, version 1).` and exit 0 at
the tip. **There is no drift-detection mode.** The only way to prove regen happened is to run the
emitters and inspect `git diff` / `git status --porcelain` in each sub-repo.

### The zero-diff claim, proved empirically

Constraint 7 and D-06 assert that a wording-only change produces a **zero diff** in `messages.h` and the
real diff in `messages.py`. Verified this session by planting a wording change in a **temp copy** of the
catalog and re-emitting both artifacts to temp paths (no tracked file touched):

```
plant: DBG_PULSE_DELAY_MISMATCH format -> "PLANTED WORDING CHANGE %d %d"

diff firestarter/include/messages.h <emitted>              -> IDENTICAL  (zero diff CONFIRMED)
diff firestarter_app/firestarter/messages.py <emitted>     -> exactly 1 changed line:
  @@ -1072 +1072 @@
  -        format="Mismatch, retrying with increased pulse delay from %d to %d",
  +        format="PLANTED WORDING CHANGE %d %d",
```
`[VERIFIED: executed 2026-08-17; changed-line count measured at 2 diff lines = 1 changed line]`

So the expected diff for D-06's wording fix is precisely: **`tools/catalog/messages.toml` ×3 (one edited
canonically, two propagated) + `firestarter_app/firestarter/messages.py` line 1072 + zero bytes in
`firestarter/include/messages.h`.** A plan can assert that shape as an acceptance criterion with
confidence, and a nonzero `messages.h` diff is a stop-and-report signal (it would mean an id changed).

### The two ids' current text and generated sites

| Id | Catalog | `messages.h` | `messages.py` |
|----|---------|--------------|---------------|
| `MSG_INFO_RETRIES` `0x51` | `:163-167` — `"Number of retries: %d"` | `:51` `#define MSG_INFO_RETRIES 0x51` | `:66` constant, `:252` `name=` entry |
| `DBG_PULSE_DELAY_MISMATCH` `0x15` | `:922-924` — `"Mismatch, retrying with increased pulse delay from %d to %d"` | `:137` `#define DBG_PULSE_DELAY_MISMATCH 0x15` | `:842` constant, `:1070` entry, `:1072` the `format=` line |

Note the `format=` line in `messages.py` is at **`:1072`**, one line below the `name=` entry at `:1070`
that CONTEXT cites. Both matter: `:1070` is the anchor, `:1072` is what changes.

**A wording constraint on the new text.** Whatever replaces `"Mismatch, retrying with increased pulse
delay from %d to %d"` must keep `params = [{ type = "u8" }, { type = "u8" }]` — two `u8` params — or the
change stops being wording-only and becomes a wire-format change. The id is orphaned (zero firmware call
sites), so nothing emits it; the text is documentation of an id that is held in reserve. A phrasing that
says so plainly is the honest one.

## Neither Repository's CI Has Run Any v1.31 Code

This was not in CONTEXT, was not in any prior phase record I read, and it changes how box 9 and both
release bodies must be written. All figures read-only this session. `[VERIFIED: 2026-08-17]`

| Measurement | firmware (`firestarter`) | host (`firestarter_app`) |
|-------------|--------------------------|--------------------------|
| local branch | `gsd/v1.31-27c-programming-algorithm-fidelity` | same |
| local HEAD | `fa6c9c7` | `68820a6` |
| ahead / behind `origin/beta` | **66 ahead / 2 behind** | **16 ahead / 0 behind** |
| `origin` tip of the same branch | **`fb7949c`** = `feat(138-06): freeze size_baseline_v131.json — cold PREP-03 firmware baseline` | **`4d18b645`** = the branch point / merge-base |
| last CI run on that ref | 2026-08-09 06:48 — *PY32F071 firmware* **success**, *Firestarter CI* **success** | 2026-08-09 07:01 — *Host CI* **success** (`workflow_dispatch`) |
| v1.31 commits ever seen by CI | **Phase 138 only** | **none** |

So every commit from Phase 140 onward — the parameter table, the per-byte loop, the VPP consolidation,
`eprom_budget.{h,cpp}`, the CAP-02 port and CAP-03 append, the two Phase-145 debug fixes — exists only
locally and on nobody's CI. The consequences worth naming:

1. **The ARM `py32f071` target has never compiled any v1.31 code.** `firestarter/platformio.ini` has
   **no** py32 env (`[env:]` list measured: `uno`, `uno328pb`, `leonardo`, `native`, `native_nodevtools`,
   `native_pinmap_provisional`, `native_trace_v131`, `native_params_v131`, `native_loop_v131`;
   `default_envs = uno, uno328pb, leonardo`) — the py32 build is CMake, driven by
   `.github/workflows/py32f071.yml` and a composite action. Two v1.31 commits *registered* new
   translation units into that manifest blind: `3207632` (*"register eprom_params.cpp in the PY32F071
   CMake manifest"*) and `e9f6a92` (*"register eprom_budget.cpp as a py32f071 common source"*). Neither
   registration has been compile-verified for ARM.
2. **`py32f071.yml` fires on `push: branches: ['**']`** — it is the LOUD ARM gate with no
   `continue-on-error`, deliberately un-filtered by branch since Phase 128. So the *first* push of the
   firmware branch will run it, and it may go red on 66 commits at once. That is `/gsd-complete-milestone`'s
   problem, not Phase 146's (D-01) — but the ledger and the fw release body should say plainly that the
   ARM target is unverified against this milestone's code.
3. **The "green CI" claims in the records are local replications.** 144's *"all four CI-scoped legs green
   on the 3.11 CI-replica interpreter"* is exactly that — a local venv reproducing CI's interpreter, not
   a CI run. Honest, and already stated that way; the ledger should keep the distinction.
4. **The firmware is 2 behind `origin/beta`** — a fact `/gsd-complete-milestone` must resolve, already
   noted in CONTEXT.

**What the AVR side *does* support.** All three AVR targets are measured building at the tip: the
`STATE.md` adjudication gives `uno` 24824→**24920**, `uno328pb` 24874→**24970**, `leonardo`
26906→**27002** B with RAM unchanged at 1573/1579/2014, and leonardo at **27002/28672 B, 94.2% full,
1670 B free**. Note this **supersedes** the 93.8% / 1766 B figure that appears in `PROJECT.md:1181`,
`PROJECT.md:128` and 144's record — those predate the debug session's `ebe9cb3`.

**`check_size_baseline.py` cannot be run without a build.** Measured: both `python3
scripts/check_size_baseline.py` and `--policy merge05` print *"FAIL: no envs compared -- supply
--avr-log/--native-log or --rebuild (never-vacuous guard: a comparator that compares nothing must not
pass)"*. So any plan asserting the MERGE-05 verdict must either pass `--rebuild` (a real build, in a
docs-only phase) or cite Phase 145's recorded verdict. **Recommendation:** cite; do not rebuild. D-06
forbids behaviour change and nothing in CLOSE-01…05 asks for a fresh build.

## The Evidence This Close Reports On

### `145-BENCH-LOG.md` — the record D-03 cites

3,180+ lines. The sections a ledger row will cite, with line anchors:

| Section | Lines | Content |
|---------|-------|---------|
| Gate 2 verdict | 1763-1800 | `VALIDATED`, with "What this verdict does NOT cover — stated at the point of closure" at 1777 |
| Gate 3 (resumed) | 1801-2211 | `--pulse-us 4688`; D-10 Claim B **HOLDS** at 1890; `--pulse-us` on silicon at 1944; the above-4687 µs budget proof at 1957; A1 derived at 2030; T-145-45 at 2125; "What Gate 3 does NOT establish" at 2189 |
| Operator eyes-on (D-10) | 2212-2286 | the verbatim four words at 2247; the disposition split at 2272 |
| NEW FINDING — bar never reaches 100 % | 2287-2343 | the six-run table and the proven mechanism |
| the D-10 contradiction | 2344-2361 | stated, not reconciled |
| Gate 3 verdict | 2382-2422 | the FINAL line |
| **Not measured (phase close)** | **2497-2521** | **16 rows**, each with its blocking reason |
| **Carry-forward hand-offs** | **2522-2565** | **12 rows** with owners |
| the four ROADMAP criteria | 2566-2665 | each quoted verbatim then answered |
| Positive findings | 2666-2695 | |
| **Boundaries — stated, not implied** | **2696-2735** | **9 numbered boundaries** |
| Phase verdict | 2736-2764 | |
| RQ-9 tripwire + suites | 2765-2814 | |
| BENCH-03 re-confirmed at the tip | 2815-2835 | |
| Artifact inventory | 2836-2935 | 51 files / 1300110 bytes; `sha256sum -c` 50 OK |
| D-16 closing assertion | 2936-2962 | |

### What `0x07` was proven on

`145-BENCH-LOG.md` boundary 3, verbatim (quotable — measured clean of forbidden phrases):
> *"The evidence scope is exactly one part, one controller, one shield revision: the Winbond **W27C512**, chip-id **`0xda08`**; controller **`leonardo`**; shield **Rev 2.0**, read off the silkscreen by the operator because the EEPROM `hw_revision` byte cannot distinguish 2.0 from 2.2 from the modified Rev 0. **Nothing here extrapolates to another protocol, another part, another board revision or another controller.**"*

Gate 3's own headline figure: `Write to W27C512 successful (30.94s).`, exit 0.

### Which protocols were skipped, and why

Both `skipped-with-reason` under BENCH-02 and 145 D-02/D-14, with the missing part named and an explicit
"NOT inferred from the `0x07` result" sentence in each disposition record:

| Protocol | Missing part | Last known state, cited not re-derived |
|---|---|---|
| `0x08` | **AM27C020** — none on the bench | Phase 99: write #1 60/64, then write #2 **0/64** at stable idle VPP. A **fail** under D-14's taxonomy. Carries **FUT-08** (program-window VPP-under-load droop, never instrumented). |
| `0x0B` | **M2716 / M2732** — neither on the bench | Phase 79: rail-corrected 22.4 V DMM / 23.9 V firmware VPE at max pot; graduation parked at plan `79-03` "when a part is on hand"; the four NMOS chips sit at `supported` **best-effort** under operator override 79-CONTEXT D-07. |

Plus a third deliberate non-spend: **a true-UV `0x07` data point (TMS27C512)** was *"deliberately not
spent (D-01)"* — one-shot part, no eraser on hand, identical algorithm.

### ⚠ Three counting discrepancies the ledger must settle

D-03 says "the eight `no v1.31 owner` items"; 145-08-SUMMARY's own prose says *"12 carry-forwards, 10 of
them with `no v1.31 owner`"*; the BENCH-LOG's section **title** calls all twelve "Carry-forward hand-offs
with no v1.31 owner" and its phase verdict says *"**Twelve items** carry forward with no v1.31 owner"*.
Counted directly from the authoritative 12-row table's Owner column:

| Rows whose owner is literally `no v1.31 owner` | 1, 2, 3, 4, 5, 6, 8, 11 (fix only), 12 → **9 rows** |
|---|---|
| Rows naming a real owner | 7 (**Phase 79 plan `79-03`**), 9 (**the milestone's accepted debt**), 10 (**the operator**) → **3 rows** |

So the honest count is **12 carry-forwards, 9 of which name no v1.31 owner, 3 of which name one.**
CONTEXT's "eight" and 145-08's "ten" are both wrong against the table, in opposite directions.
**Recommendation:** the ledger's negative-space section carries **all twelve rows** with the Owner column
reproduced verbatim from the BENCH-LOG table, and states the count as twelve — which sidesteps the
discrepancy entirely and matches both the section title and the phase verdict. Add one sentence recording
that 145-08-SUMMARY's "10" and 146-CONTEXT's "eight" disagree with the table, and that the table wins.
`[VERIFIED: counted from the source table this session]`

### The twelve carry-forwards and their homes

| # | Item | Owner (verbatim) | Home per D-03 |
|---|------|------------------|---------------|
| 1 | A1's per-pulse overhead inside a multi-pulse retry loop | `no v1.31 owner` | **homeless** — ledger row only |
| 2 | Verification-map row 27's smooth-vs-end-burst discriminator | `no v1.31 owner` | **homeless** — ledger row only |
| 3 | MAIN write bar never reaching 100 % | `no v1.31 owner` | **filed: ROADMAP 999.30** (`:2808`) |
| 4 | Program-window VPP / internal VCC under load | `no v1.31 owner` | **FUT-08** / §Future Requirements |
| 5 | Root cause of the intermittent single-byte margin failure | `no v1.31 owner` | **homeless** — ledger row only |
| 6 | `0x08` (AM27C020) bench validation | `no v1.31 owner` | BENCH-02 disposition record + **FUT-08** |
| 7 | `0x0B` (M2716/M2732) bench validation | **Phase 79 plan `79-03`** | BENCH-02 disposition record |
| 8 | A true-UV `0x07` data point (TMS27C512) | `no v1.31 owner` | **homeless** — ledger row only |
| 9 | The 6.25 V program-VCC evidence ceiling | **the milestone's accepted debt** | **FUT-VCC**; *leads* the ledger (CLOSE-02) |
| 10 | MERGE-05's +96 B leonardo band breach — adjudication | **the operator** | **adjudicated 2026-08-17**, `STATE.md` @ `d02a88a0` |
| 11 | T-145-45 — threat-register entry asserting a nonexistent firmware mitigation | `no v1.31 owner for the fix; Phase 146 may judge the wording` | **ROADMAP 999.31** (`:2835`) |
| 12 | RQ-4's superseded frames-per-block table | superseded, `no v1.31 owner` | **homeless** — ledger row only |

Plus `FUT-PRESTO`, `FUT-MAXPULSE`, `FUT-OVERPROG-MAP` in §Future Requirements, and F-140-05's `0x07`
Intel-family split (blocked by TABLE-05). **Genuinely homeless: rows 1, 2, 5, 8, 12** — five items, not
"two of eight". D-03's instruction ("ledger rows only, no new stubs") applies uniformly regardless.

Row **10 is now discharged**, not carried — the operator adjudicated it on 2026-08-17 and the wording is
staged. Row **9's** disposition per the BENCH-LOG is exact and worth quoting: *"Phase 146's honesty
ledger is where it is **stated**, not where it is **discharged**."*

### The nine boundaries, and the MERGE-05 posture

Boundaries 1-9 at `145-BENCH-LOG.md:2696-2735` are the ledger's non-claim column in near-final form.
Boundary 7 is the one most likely to be under-read:

> *"**The firmware changed mid-phase and D-16 still holds on its own terms.** No *plan* in this phase created, edited, renamed or deleted a file under either sub-repo. But a **debug session — which is not a plan** — changed eleven files under `firestarter/` (`eb563d2` + `ebe9cb3`, +96 B). **Every bench measurement from 2026-08-17 onward was produced by `ebe9cb3` (27002 B), not the `a594173d` (26906 B) image Gate 1 recorded**, and Gate 1's firmware-identity rows were superseded in `145-05`."*

Confirmed against the firmware log: the three commits after 144's baseline re-anchor are
`eb563d2 fix(eprom): assert the program-voltage route around every program pulse`,
`ebe9cb3 fix(eprom): raise the VPP settles to 1000us/100us on bench evidence`, and
`fa6c9c7 test(145): admit the +96 B MERGE-05 flash breach as a named defect-fix exemption`. The fix is
visible in source: `eprom_internal_program_pulse()` (`eprom.cpp:247-253`) now asserts `CTRL_VPE_ENABLE`,
waits `EPROM_VPP_SETUP_US`, sets data, waits `EPROM_VPP_HOLD_US`, then releases — with
`EPROM_VPP_SETUP_US 1000` / `EPROM_VPP_HOLD_US 100` at `include/eprom.h:166-167`, and the in-source
comment naming the debug session and the defect (*"Calling `firestarter_set_data` bare here — what Phase
141 shipped — strobes CE with the 12 V rail generated but never switched onto the part, so no cell can
change and every byte exhausts `max_pulses`"*). `[VERIFIED: source + git log]`

**This is a load-bearing fact for the release bodies and for box 3/5 grading:** the per-byte loop as
bench-validated includes a *defect fix to Phase 141's own shipped code*, and the shipped image is
`fa6c9c7`. It is also why the +96 B exists, and why boundary 1 accounts **58.9 s** of the timing
difference against the 22.84 s historical figure to the settle increase alone.

**The MERGE-05 wording, staged for verbatim quotation** (`STATE.md`, commit `d02a88a0`, first of five
appended `## Decisions` entries, explicitly labelled *"Wording for Phase 146 / CLOSE-02's honesty ledger,
quotable verbatim"*):

> *"v1.31 ships +96 B of AVR flash over the v1.23-era MERGE-05 band on all three AVR targets (uno 24824→24920, uno328pb 24874→24970, leonardo 26906→27002; RAM unchanged at 1573/1579/2014), admitted under a named, SHA-attributed defect-fix exemption — `MERGE05_DEFECT_FIX_EXEMPTION_BYTES = 96`, firmware commits `eb563d2` (assert the program-voltage route around every program pulse) and `ebe9cb3` (raise the VPP settles to 1000us/100us on bench evidence) — rather than by moving the BASE-01 anchor or widening the band literal. The bytes are `eprom_internal_program_pulse()` plus its two VPP settle constants: a defect fix restoring behaviour the pre-v1.31 firmware had, not new feature surface. Leonardo ships at 27002/28672 B, 94.2% full, 1670 B free."*

The other four entries carry: the three rejected alternatives (third re-anchor / widened band / shrunk
fix) with the band literals asserted unchanged; the archived-v1.23-untouched assertion with both SHA256s;
the flash-only scope with the decomposed PASS/FAIL text (`+96<=96=band0+exempt96`; *"allowance of 160 B
(band 64 B + defect-fix exemption 96 B)"*) and the one-byte-past negative control; and the collateral
fixture re-derivation (+65→+161 uno, +1→+97 leonardo). The exemption constant lives at
`firestarter/scripts/check_size_baseline.py:167`, with `_merge05_flash_allowance()` at `:274-296` as its
**sole** consumer alongside `MERGE05_UNO_CLASS_FLASH_BAND = 64` at `:123`. `[VERIFIED: all sites read]`

The three-ways-of-saying-it CONTEXT flags are exactly those: a named SHA-attributed constant, a
decomposed PASS/FAIL string that keeps growth visible, and a negative control one byte past. Plus the
sentence the ledger must not omit: **F-141-01 was never remediated, and Phase 144's earlier green came
from the anchor moving, not from growth shrinking** (`PROJECT.md:1181`, D-14's own disclosure).

### Live suite counts, re-measured

Both suites run this session, `-o addopts=""` to keep the count line visible (the host's `addopts` is
`-ra -q`; doubling `-q` hides it — the firmware repo has **no** pytest config file at all, so the flag
is harmless there but unnecessary):

| Suite | Invocation | Result | Baseline |
|---|---|---|---|
| firmware | `cd /workspaces/firestarter && python3 -m pytest tests -o addopts="" -q` | **314 passed**, 0 failed, **19.17 s** | 314 (145-08) — **match** |
| host | `cd /workspaces/firestarter_app && python3 -m pytest tests -o addopts="" -q` | **1590 passed**, 0 failed, **30 snapshots**, 1 warning, **258.92 s** | 1590 (145-08) — **match** |

Porcelain after both runs: `firestarter` **0** lines (clean); `firestarter_app` **7** lines (all
pre-existing untracked: `.planning/config.json`, `SECURITY.md`, four `datasheets/*.pdf`,
`write_test_port.sh`). Neither suite left dirt. `[VERIFIED: 2026-08-17]`

Constraint 9's mechanism, confirmed at source: `firestarter/tests/test_flash_path_record_sync.py:1247`
asserts `_git_porcelain(_FW_REPO_ROOT) == ""`, and `firestarter_app/tests/test_py32_flash_map_host.py:391`
asserts `_git_porcelain(FW_ROOT) == ""` — the **firmware** repo's porcelain, from the host suite. So the
firmware repo must be committed-clean before **either** suite runs. The host repo's own 7 untracked files
do not trip either assertion (neither test checks the host repo's porcelain), which is why the host suite
passes today.

## Closing-Artifact Shapes — the templates

### The ledger, three prior instances

| Section | `122-LEDGER.md` (23.6 KB) | `130-LEDGER.md` (29.5 KB) | `137-LEDGER.md` (26.8 KB) — most recent |
|---|---|---|---|
| identity header | `:1-21` | `:1-23` | `:1-42` — milestone, phase list, repo scope, **submodule commit measured live**, oracle, generated-date, "Composes with (cross-reference only — no data copied)" |
| the ceiling, quoted verbatim | `:22` | `:24` | `:44` — plus "both named narrowings, verbatim, never smoothed over" |
| status / claim key | `:34` | `:36` | `:84` |
| sourcing key | — | `:42` | — |
| **evidence tiers, weakest→strongest** | — | **`:53-102`** (CI-compile-only, AVR-measured, native-simulated, mock-only, real-published-artifact, decision-only-unverified) | — |
| the claim classes | `:43` (nine) | — | `:98` (eleven) |
| mechanism corrections | `:81` | `:103` | `:120` |
| **process failures, not only technical** | — | — | **`:165`** |
| what this milestone chose not to prove / negative space | `:97-122` | `:115-148` | `:195-233` |
| what no test/gate/review can close | `:123` | `:149` | `:234` |
| community inbox — not implied clear | — | `:167` | — |
| scanner status | `:133` | `:173` | (folded into the header's oracle line) |

**The claim-class table is a 4-column shape**, identical across all three:
`| Class | Permitted wording | Evidence (measured, source) | Explicitly does NOT prove |`, with a status
token (`PERMITTED` / `CONTEXT-ONLY` / `COMMUNITY-CORROBORATED` / `FORBIDDEN`) bolded into the Class cell.
That is literally CLOSE-02's "pairs every permitted claim with its explicit non-claim" — the non-claim is
column 4. **Do not re-derive it.**

The `FORBIDDEN` key entry is the D-14 discipline in the ledger's own words (`122-LEDGER.md:39`):
> *"**`FORBIDDEN`** — the ceiling's forbidden claim. It appears in this ledger only as a citation of what is *not* claimed, never as prose asserting it."*

Two further reusable moves from 137: every figure *"re-measured live this plan … not copied from a
citation. Where a figure agrees with a prior document, that agreement is stated as a re-confirmation, not
assumed"*; and where two readings of a number exist, **both are stated rather than silently reconciled**
(137's four-vs-six step-count note). Both apply directly to the three carry-forward counting
discrepancies above.

**For 146 specifically**, the evidence-tier grouping from 130 D-09 (discretion says "available and
probably right") maps cleanly onto this milestone's actual tiers:

| Tier | v1.31 content |
|---|---|
| **bench-measured, one part** | `0x07` write→read→verify on W27C512 `0xda08` / `leonardo` / Rev 2.0; `--pulse-us` on silicon; Claim B on 4/4 blocks |
| **AVR-measured** | flash/RAM per target at the tip; the +96 B exemption; leonardo 27002/28672 |
| **native-simulated** | `native_loop_v131` 79, `native_params_v131` 9, `native_trace_v131` 5/5, pinned envs 141/141 |
| **source-contract only** | `command_done()`'s disable guarantee; the `SERIAL_ON_IO` progress guard; CAP-03 byte-layout parity |
| **cited, not re-derived** | `0x08` (Phase 99), `0x0B` (Phase 79), the 22.84 s historical figure |
| **structurally unreachable** | 6.25 V program-VCC; program-window VPP/VCC under load; Uno-class progress delivery |
| **never run** | either repository's CI against any v1.31 code; the ARM `py32f071` build |

### The release bodies, four prior instances

`122-RELEASE-NOTES-fw.md` (5.3 KB), `122-RELEASE-NOTES-app.md` (4.5 KB),
`130-RELEASE-NOTES-fw.md` (8.9 KB), `130-RELEASE-NOTES-app.md` (4.9 KB),
`137-RELEASE-NOTES-app.md` (3.3 KB — read in full).

**137's app-body skeleton**, the most recent and the leanest:
1. `# Host app prerelease — <one-line headline>`
2. the install line (`pip install --pre --upgrade firestarter`) + a sentence on what the release page
   does and does not carry, and where the matching firmware lives
3. `## Removed` / `## <what changed>` — per change, *what* then *why*, in a user's terms
4. `## Also in this release`
5. `## What is proven, and what is not` — the honest asymmetry, with the ceiling sentence restated
6. `## The ask`

**130's fw-body skeleton** adds two moves worth copying: `## The headline: …` as a named section, and
the discipline of stating the boundary **immediately inside** the headline section rather than saving it
for the end —
> *"State the boundary immediately, because it is the whole point of this section: **no PY32F071 circuit board exists anywhere in this project** … Publishing the file is the entire event described above — nothing here is a claim about that file running on anything."*

That is the exact shape v1.31's fw body needs for the ARM/py32 and Uno-class boundaries.

**Version-agnosticism (D-02), mechanically.** None of the four precedents hardcodes a `3.0.0bNN`
literal; 137's body identifies itself as *"Host app prerelease"* and points at `pip install --pre`.
Recommended placeholder convention: a single bracketed token such as `<TAG — filled in at cut time from
`gh release list`, never computed>` appearing once near the top, so a grep for `3.0.0b` over both bodies
returns zero and a grep for the token returns exactly one hit per file. Both are cheap acceptance
criteria. Note also **no `CHANGELOG.md` exists in either sub-repo** (confirmed), so these bodies are the
only "what changed" surface.

### `146-CITATIONS.md` — the register pattern

`139-CITATIONS.md` (45 KB) is the template. Its properties worth copying:
- an explicit statement that **nothing is copied from RESEARCH** — every command was re-run in the
  authoring session, and *"any divergence from research's recorded figures is stated explicitly rather
  than reconciled by editing"* the earlier documents.
- §0 a before-state table: `| Field | Command (as run) | Result |`, one row per measured field.
- §1 a pinning strategy: *"Citations pin to commit SHAs, never branch names (D-07)."*
- §5 the freeze values: `| File | Frozen blob SHA | Byte length | Committing commit |`.
- measurement-precision notes recorded as **notes, not divergences** (the codepoints-vs-bytes case).

For 146 this register is where the gate's `PASS:` lines, the plant-and-revert transcript, the gh#15
before/after state, the freeze values, and the negative-flag audit all live. It is not required by any
CLOSE requirement, but every prior close produced one and D-10's "record its blob SHA and byte count"
needs somewhere to land.

### The two record-gate traps at milestone close

Both recorded, both confirmed live this session, both relevant because Phase 146 is the last phase before
`/gsd-complete-milestone` archives things:

1. **Archived sections orphan `lines=N` exemptions.** `check_record_corrections.py`'s mechanism 3 is
   `<!-- recordscan:supersedes needle=<label> lines=<n,n,…> reason: … -->` — an **explicit enumerated
   list of 1-based line numbers** in the same file. Any edit that shifts line numbers in
   `PROJECT.md`/`STATE.md`/`ROADMAP.md` above such a marker silently breaks it: the named lines no longer
   hold the needle, and the real needle line becomes `unlabeled`. The live run reports
   `'superseded': 12` — twelve such exemptions are active. **Phase 146 inserts prose into all three
   files.** Re-run the gate after every insertion, and prefer **appending** correction blocks at the end
   of the relevant section over inserting above existing content where the choice exists.
2. **A `git rm` of `REQUIREMENTS.md` trips fail-closed target lists.** The same checker's docstring names
   `.planning/REQUIREMENTS.md` while its live target is `.planning/milestones/v1.23-REQUIREMENTS.md` — it
   was re-pointed after v1.23's archive. Phase 146 archives nothing (D-01), so this is a warning for the
   *next* command, not this phase — but the phase should not leave a new checker whose target list will
   break on the archive. **Recommendation:** the D-13 doc checker's targets are sub-repo doc paths, which
   are not archived; the D-11 claim gate's targets are `146-*` phase artifacts, which are archived
   wholesale with the phase directory and therefore move together. Neither creates a new instance of this
   trap, provided neither points at `.planning/REQUIREMENTS.md`.

### The requirement flip — measured line budget

145-09's lesson was that `REQUIREMENTS.md` carries its **own** Traceability table, so a flip is more than
one line per requirement. Measured exactly:

| File | Sites | Lines changed |
|---|---|---|
| `.planning/REQUIREMENTS.md` | checkboxes at `:256`, `:259`, `:261`, `:263`, `:265` (`- [ ]` → `- [x]`, first line of each wrapped bullet) | **5** |
| `.planning/REQUIREMENTS.md` | Traceability rows `:337-341` (`Pending` → `Complete`) | **5** |
| `.planning/ROADMAP.md` | v1.31 Coverage rows `:632-636` (`Pending` → `Complete`) | **5** |
| `.planning/ROADMAP.md` | phase checkbox `:183` (`- [ ]` → `- [x]`, plus a `(completed <date>)` suffix per the Phase 138-145 convention) | **1** |
| `.planning/ROADMAP.md` | `**Plans**: TBD` at `:586` → the real plan count | **1** |

**Total: 17 changed lines across two files** = 34 diff lines. 145-09's "12 lines for three requirements"
was counting *diff* lines for two tables only (3 × 2 × 2); the equivalent figure here is 20 for the ten
`Pending`/checkbox pairs plus 14 for ROADMAP's coverage rows and headers. Budget in **changed lines**, and
prove the blast radius with `git diff --numstat`, never `git diff | grep -c '^[+-][^+-]'`.

**Confirmed: the 12-row coverage drift STATE.md hands Phase 146 is ALREADY DISCHARGED.** Commit
`6822ee2d` (*"docs(146-PRE): sync ROADMAP v1.31 Coverage with REQUIREMENTS.md -- 12 stale rows"*) exists,
and `grep -n Pending .planning/ROADMAP.md` returns **only** `:632-636` (CLOSE-01…05) within the v1.31
table — every one of PREP-01…04, ISSUE-01…03, TABLE-*, LOOP-*, VPP-*, HOST-01…05, TEST-01…08,
BENCH-01…03 reads `Complete` and matches `REQUIREMENTS.md`. The other `Pending` rows in `ROADMAP.md`
(`:2389` onward) belong to older, unstarted milestones and are out of scope. **Treat `STATE.md`'s
`last_activity_desc` sentence as stale, exactly as CONTEXT says.** `[VERIFIED: 2026-08-17]`

### The uncommitted ROADMAP change — measured

`git diff --numstat -- .planning/ROADMAP.md` → **`2 2`**. The change is a heading rename only:
`:183` `### Phase 146 (close): Honesty Ledger…` → `- [ ] **Phase 146: Close — Honesty Ledger…` (the
phase-list line) and `:573` the matching `### Phase 146: Close — …` detail heading. Pre-existing, not
this phase's, and small. Also uncommitted: `.gitignore` (**8 insertions / 1 deletion** — a `.claude/*`
allowlist rework plus `node_modules`), and both gitlinks. Untracked in the meta repo: `.claude/`,
`.planning/VALIDATED-EPROMS.md`, `package.json`, `package-lock.json`.

**A porcelain assertion written against a clean meta tree will read all of this as its own damage.**
Either commit the ROADMAP rename into the first 146 plan (recommended — it is 2 lines and it is this
phase's own heading) or snapshot the porcelain at phase start and assert *delta*, not emptiness.

## Runtime State Inventory

Included because this phase edits records that describe runtime state and posts to a live service; it is
not a rename phase, so several categories are legitimately empty and are stated as such rather than left
blank.

| Category | Items found | Action required |
|----------|-------------|------------------|
| **Stored data** | **None.** No database, collection name, key or user_id is touched. `chip_database.json` is **byte-unchanged** at the tip — BENCH-03 re-confirmed all seven legs identical to Gate 0 (0-byte DB diff, 0-byte generator-inputs diff, AST write-locus checker exit 0, digest `3befbaad7bbb…e913479`, histogram 746/736/9/1), and `tools/build_db.py` was not invoked. D-07 of scoping forbids any `support_status` change. | none — assert byte-identity, do not touch |
| **Live service config** | **gh#15 on `henols/firestarter_prom`** — state `OPEN`, 1 comment (`#5233463320`), body unedited (`lastEditedAt: null`), labels `[]`, nine boxes unticked. This is the only live external state the phase mutates, by exactly one `gh issue comment` call. | one post, behind a blocking gate, byte-verified; issue stays OPEN, body untouched, labels untouched (D-07) |
| **OS-registered state** | **None.** No Task Scheduler entry, pm2 process, launchd plist or systemd unit is involved. No firmware is flashed (D-06 forbids behaviour change; Phase 145 owned the flash). | none |
| **Secrets / env vars** | **One new env-var *name* is introduced**: the claim gate's target-override seam. `FIRESTARTER_CLAIMSCAN_TARGETS_V131` is **already taken by 139** in this same milestone; `…_V130` by 137; the bare name by 122 and 123. A fresh distinct name is required or one test suite can aim two live checkers. No secret is read or written; no SOPS key, no `.env`. | pick a fresh seam name and record it |
| **Build artifacts / installed packages** | **Two generated artifacts are regenerated**: `firestarter/include/messages.h` (expected **zero** diff — measured) and `firestarter_app/firestarter/messages.py` (expected **exactly one** changed line, `:1072` — measured). No `pip install -e` re-run is needed because no package metadata changes. **`__pycache__` and `.pytest_cache` directories will appear** in the phase directory from the fixture suite — 122/130/137 all have them on disk; confirm they are gitignored before asserting porcelain. | run the sync script; assert the two-artifact diff shape; check `git check-ignore` on the cache dirs |
| **Stale record state (extra category, and the one that matters here)** | The meta repo's **tracked gitlinks are stale by the whole milestone**: `git ls-tree HEAD` gives `firestarter → 0933bd7d` and `firestarter_app → cc036e8d`, while live HEADs are `fa6c9c7` and `68820a6`. `cc036e8d` is v1.30's close commit (it is the exact SHA `137-LEDGER.md` records). Both gitlinks have shown as ` M` for the entire milestone. | see the discretionary note below |

**On the gitlink discretion.** CONTEXT leaves open "whether the phase asserts the meta gitlinks match the
sub-repo tips at phase end", noting v1.23 D-04 *asserted* rather than re-pinned. Measured, the premise
has changed: the gitlinks do **not** match now and have not matched at any point in v1.31 — they still
point at v1.30's tips. So a plain "assert they match" criterion would fail. The three coherent options:
(a) **assert the delta and record it** — the honest minimum, one table naming tracked vs live SHAs for
both sub-repos, handing the re-pin to `/gsd-complete-milestone`; (b) **re-pin** — commit both gitlinks in
the closing plan, which is not a push and not a merge and so does not violate D-01, but does mean the
meta commit that ships the ledger also advances the submodule pointers by 66 and 16 commits; (c) **stay
silent** — rejected, since the phase's own sub-repo commits will move both tips again and an unrecorded
divergence at close is exactly what a ledger exists to prevent. Recommend (a), with (b) available if the
planner wants the meta repo self-consistent at close; either way the SHAs belong in the ledger.

## Common Pitfalls

### Pitfall 1: the phase's own prose trips the phase's own gate

**What goes wrong:** an artifact quotes a forbidden phrase in order to disclaim it, and the gate — which
has no proximity window and no exclusion mechanism by design — flags it.
**Why it happens:** the honest thing to write ("we do not claim X") contains X. Measured live instances:
`145-BENCH-LOG.md:2709` contains `datasheet-correct`; `ROADMAP.md:580` and `REQUIREMENTS.md:256-257`
contain all three headline phrases because they *define* them; `146-CONTEXT.md` contains six
`proven-unqualified` hits.
**How to avoid:** D-14's rule, applied mechanically — cite by `file:line` plus finding id and paraphrase.
Concretely: *"the boundary at `145-BENCH-LOG.md:2707-2709` states that no datasheet-conformance claim is
made in either direction (F-140-07's value/reason split is at `140-PARAM-TABLE-RECORD.md:259`)"*.
**Warning signs:** any sentence in a closing artifact containing the words *proven*, *conformant*,
*correct* adjacent to *datasheet*, or *works*/*confirmed* adjacent to *silicon*. Run the gate against a
draft early and often — it is instant.

### Pitfall 2: `\bproven\b` after a hyphen

**What goes wrong:** `bench-proven`, `field-proven`, `now-proven` all match. D-09's own CONTEXT phrasing
("`0x07` bench-proven on one part") would fail the gate.
**Why:** `\b` is a word/non-word transition and `-` is non-word.
**How to avoid:** use the 145 taxonomy — `validated` / `skipped-with-reason` — throughout, or
*bench-validated* / *established* / *measured* / *demonstrated* / *attested*. Measured safe.
**Warning signs:** any hyphenated compound ending in *proven*.

### Pitfall 3: a glob or walk for the gate's default targets

**What goes wrong:** the gate goes red on the phase's own planning prose, or (worse) green over
`fixtures/`.
**Why:** the phase directory holds CONTEXT, DISCUSSION-LOG, RESEARCH, PLANs, SUMMARYs and a `fixtures/`
directory of deliberately-violating text, all matching `146-*.md` or a recursive walk.
**How to avoid:** an explicit five-element list built from `_HERE`. Both 122's and 137's docstrings warn
about the `fixtures/` half in writing.
**Warning signs:** `glob`, `os.walk`, `Path.rglob`, or `*` anywhere near `_DEFAULT_TARGETS`.

### Pitfall 4: a pre-authored gate leg that has never been seen to pass for the right reason

**What goes wrong:** leg 9 ("armed and green against all five real targets") is written before the
artifacts exist. A red leg proves nothing about the leg; it might be red for a missing fixture, a
collection error, or a typo in a basename.
**Why it happens:** wave order forces authorship before content.
**How to avoid:** three recorded observations per leg — red for the *named missing artifact*, green once
content exists, red again under the plant. Phase 145 found **three** false GREENs; substitution #1
*"passed against a record with no eyes-on statement in it."*
**Warning signs:** an acceptance criterion of the shape `grep -qv "<sentinel>"` — `grep -qv` succeeds on
any non-matching line and is the exact false-GREEN shape 145-08 caught.

### Pitfall 5: `$?` after a pipe

**What goes wrong:** `python3 checker.py 2>&1 | tail -6; echo "EXIT=$?"` reports `tail`'s status.
Reproduced this session: it printed `EXIT=0` for a script that had just printed `FAIL:`.
**How to avoid:** capture the script's own status (`rc=$?` immediately after, or run without a pipe and
inspect output separately, or `set -o pipefail`).
**Warning signs:** any acceptance criterion combining a pipe with `$?`.

### Pitfall 6: `git diff | grep -c '^[+-][^+-]'` over markdown

**What goes wrong:** reports **zero** changed lines over a genuinely changed file, because a changed
`- [ ] …` list item renders as `-- [ ] …` and `[^+-]` rejects it. 145-08 hit this in its own final sweep
and caught it only because the answer contradicted an edit it knew it had made.
**How to avoid:** `git diff --numstat`, plus reading the committed line back with `git show HEAD:<path>`.
**Warning signs:** a zero that agrees with what you wanted. *"A check that agrees with what you want is
the one to re-derive."*

### Pitfall 7: the GSD verbs' blast radius

**What goes wrong:** `requirements`/`roadmap` verbs run `_normalizeMd` over the whole file;
`phase.complete` is recorded clobbering an unrelated phase's `**Plans:**` line and jumping to `(close)`
when the next phase has no directory; `state.*` verbs clobber `last_activity_desc` — observed **twice** in
145-08 (replaced with the truncated garbage `145-05 complete. See`) and a **seventh** occurrence recorded
in the current `STATE.md` (`state.record-session` reported updating three fields while mutating six).
**How to avoid:** hand-edit the flips with snapshot-and-diff, exactly as 145-08 and 145-09 did; if a verb
must run, snapshot first and hand-repair after with a diff proving only intended lines moved.
**Warning signs:** any plan step that calls a state/roadmap/requirements verb without a paired snapshot.

### Pitfall 8: treating `sync_to_subrepos.sh`'s output as verification

**What goes wrong:** the script prints "OK: … regenerated" from a `diff file file` self-comparison, and
`codegen.py --check` validates only the catalog. Both can print OK while nothing was regenerated.
**How to avoid:** verify with `git status --porcelain` / `git diff --numstat` in each sub-repo, against
the measured expected shape (zero lines in `messages.h`, one line in `messages.py`).

### Pitfall 9: `gh issue view --json lastEditedAt` does not exist

**What goes wrong:** the command fails with `Unknown JSON field`. A plan written against it fails at
execution.
**How to avoid:** use the GraphQL query given above. `updatedAt` is **not** a substitute — it bumps on
comment creation and will bump again when 146 posts.

### Pitfall 10: byte-verifying the posted comment against literal diff emptiness

**What goes wrong:** GitHub appends a trailing newline; the frozen file already ends in one; `sed -e '$a\'`
is a no-op on it, so the normalized and raw diffs are identical and both show one added blank line.
A criterion demanding an empty diff fails on a correct post.
**How to avoid:** the criterion is the **named signature** — exactly one added blank line at EOF, +1 byte
in the retrieved direction, zero other diff lines — matched against 122-DELIVERY's four executed
precedents and 139's own. And use `wc -c`, not `jq length`.

### Pitfall 11: D-01 has no mechanical enforcement

**What goes wrong:** `git push`, `git merge`, `git checkout`, `gh workflow`, `gh release` and `gh run` are
**all** in `.claude/settings.local.json`'s allowlist. Nothing stops a task from pushing. And a push of the
firmware branch fires `py32f071.yml` (`branches: ['**']`) and, on `beta`, fires a beta cut — which has
already happened twice in this project.
**How to avoid:** an explicit structural gate — assert `git rev-list --count @{u}..HEAD` unchanged in all
three repos across the phase, plus a negative-argv audit naming `push`/`merge`/`tag`/`workflow run`/
`release`. Do not edit the allowlist.

### Pitfall 12: running under `--auto` or `--chain`

**What goes wrong:** both auto-approve `human-verify` gates. `autonomous: false` is **not**
self-protecting. This phase has two real gates: D-01's wording review and D-07's posting authorization.
**How to avoid:** constraint 10. Mark both gates `autonomous: false` **and** state the no-auto
requirement in prose in the plan, as 145's record did at its own close (*"this phase was dispatched with
no `--auto` flag and no `--chain` flag, and `check auto-mode` resolved `false`"*). Record the resolved
value, not the intent.

### Pitfall 13: running a sub-repo suite before committing

**What goes wrong:** `test_flash_path_record_sync.py` and `test_py32_flash_map_host.py` both assert the
**firmware** repo's whole-repo porcelain is empty. Any uncommitted firmware edit — including the
`messages.h` regen, even at zero diff, if anything else moved — turns both suites red for a reason
unrelated to the change.
**How to avoid:** constraint 9 — commit, then run. Exact invocations measured above.

## Code Examples

All verified against in-tree sources this session.

### The per-file caveat map (D-11's one new mechanism)

139 requires both caveats in every file. D-11 requires them only in four of five. The minimal change to
`scan_text`'s contract is to pass the file's rule set in, keeping the pattern scan itself untouched:

```python
# NEW for 146 (D-11). 139 has no analog -- its REQUIRED_CAVEAT_PATTERNS apply uniformly.
# Keys are BASENAMES so the map cannot drift from _DEFAULT_TARGETS' directory construction.
_CAVEAT_RULES = {
    "146-LEDGER.md":              {"ceiling-voltage", "ceiling-narrowing"},
    "146-GH15-RECONCILIATION.md": {"ceiling-voltage", "ceiling-narrowing"},
    "146-RELEASE-NOTES-fw.md":    {"ceiling-voltage", "ceiling-narrowing"},
    "146-RELEASE-NOTES-app.md":   {"ceiling-voltage", "ceiling-narrowing"},
    "146-CORRECTIONS.md":         frozenset(),   # D-11: a register of factual corrections is not
                                                 # failed by a rule written for a release body
}

def _required_caveats_for(path):
    """Fail CLOSED on an unknown basename: a target with no rule entry gets the
    FULL caveat set, never the empty set. An empty-set default would let a future
    edit disable the caveat check for a real artifact by renaming it."""
    return _CAVEAT_RULES.get(os.path.basename(path), _ALL_CAVEAT_LABELS)
```

Two properties worth pinning with fixture legs: **every basename in `_DEFAULT_TARGETS` has an entry in
`_CAVEAT_RULES`** (a missing entry is a typo, not a policy), and **an unknown basename gets the full
set** (fail closed). Both are cheap introspection legs alongside legs 10 and 11.

### The `⚠ CORRECTION` block, using the in-tree recognized opener

```markdown
**⚠ CORRECTION (Phase 146 / CLOSE-04, origin F-144-01):** the sentence above states
`native_loop_v131`'s suite counts as 39 + 32 = 71. The measured counts at this
milestone's tip are **47 + 32 = 79** (`144-TEST-RECORD.md` §2.2 row 3, §1 TEST-07,
and F-144-01 at `:518`). Phase 142's own `test_vpp_eprom_v131` growth was never
folded back into this paragraph. The env still runs in no CI leg of either
repository; only the numerals were wrong.
```

The opener must be the glyph `⚠` followed by `CORRECTION` — that is what
`check_record_corrections.py:291`'s `⚠\s*(?:CORRECTION|RESEARCH CORRECTIONS|SUPERSEDED|DESIGN)\b`
recognizes as a block-label exemption opener. Blocks extend **forward** from the opener, so the block must
sit *after* the text it corrects, not before it.

### The `146-CORRECTIONS.md` register row (D-05's four fields)

```markdown
| # | Origin finding | Owning file:line | False text (cited, never re-quoted if it carries a forbidden phrase) | Corrected text |
|---|---|---|---|---|
| C-1 | 143 D-01 | `.planning/ROADMAP.md:380` | the "Independent of Phases 140–142 (different repo)" clause | Phase 143 depends on Phases 140 and 141 as landed prerequisites and is dual-repo: HOST-02's emission is firmware, HOST-01's budget reads Phase 140's table |
| C-6 | F-140-07 | gh#15 comment `#5233463320`, body line 39; `.planning/PROJECT.md:176-181`; `.planning/REQUIREMENTS.md:20`; `.planning/STATE.md:67` | the "classic 2716 total programming time" justification for the 50 ms cap | TI TMS 2516 gives total programming time for all bits as 100 seconds; 50 ms is the per-location `t_w(PR)` TYP (45/**50**/55 ms). The value has a primary datasheet basis; the published reason does not. Already corrected in place at `firestarter/doc/PROTOCOLS.md` §1.5. |
```

### The plant-and-revert transcript, capturing the script's own status

```bash
set -o pipefail
cd .planning/phases/146-close-honesty-ledger-claim-gate-gh-15-reconciliation

before=$(git hash-object 146-LEDGER.md); bytes_before=$(wc -c < 146-LEDGER.md)
python3 146-check-claims.py > /tmp/gate_before.txt; rc_before=$?      # expect 0

printf '\n<!-- PLANT -->\nThis run is confirmed working on silicon.\n' >> 146-LEDGER.md
python3 146-check-claims.py > /tmp/gate_planted.txt; rc_planted=$?    # expect 1
grep -q '146-LEDGER.md:' /tmp/gate_planted.txt                       # names the FILE
grep -q 'confirmed-working'  /tmp/gate_planted.txt                   # names the LABEL

git checkout -- 146-LEDGER.md
after=$(git hash-object 146-LEDGER.md); bytes_after=$(wc -c < 146-LEDGER.md)
[ "$before" = "$after" ] && [ "$bytes_before" = "$bytes_after" ]      # byte-identity

python3 146-check-claims.py > /tmp/gate_after.txt; rc_after=$?        # expect 0
printf 'rc_before=%s rc_planted=%s rc_after=%s blob=%s\n' \
       "$rc_before" "$rc_planted" "$rc_after" "$after"
```

Note the plant uses `confirmed working on silicon` deliberately: it hits **two** patterns
(`confirmed-working`, and `works-on-silicon` does *not* fire here since the verb is "confirmed"), which
makes the label assertion specific rather than "some label fired". Verify the chosen plant's labels with
a probe before writing the criterion.

### The gh#15 read-only measurement block (safe to run any number of times)

```bash
gh api graphql -f query='
{ repository(owner:"henols", name:"firestarter_prom") { issue(number:15) {
  state updatedAt lastEditedAt
  comments(first:10){ totalCount nodes { databaseId createdAt lastEditedAt author{login} } }
} } }'

gh issue view 15 --repo henols/firestarter_prom --json body -q .body | wc -c     # expect 5964
gh issue view 15 --repo henols/firestarter_prom --json body -q .body \
  | grep -c '^- \[ \]'                                                          # expect 9
gh issue view 15 --repo henols/firestarter_prom --json body -q .body \
  | awk '/^## Acceptance criteria/,0' \
  | diff - .planning/phases/139-gh-15-correction-outward/139-GH15-ORIGINAL-CRITERIA.md
                                                                                # expect empty
gh issue view 15 --repo henols/firestarter_prom --json labels -q .labels         # expect []
```

All four ran clean this session and are the recommended precondition block for the posting task.

### Regenerating the catalog artifacts and asserting the measured diff shape

```bash
# 1. edit ONE file: ./tools/catalog/messages.toml  (DBG_PULSE_DELAY_MISMATCH's `format`, line 924)
# 2. propagate + regenerate, from the meta repo root
bash tools/catalog/sync_to_subrepos.sh

# 3. verify the measured shape -- NOT the script's own self-comparing "OK" lines
git -C firestarter      diff --numstat -- include/messages.h            # expect NO OUTPUT (zero diff)
git -C firestarter_app  diff --numstat -- firestarter/messages.py       # expect "1  1  firestarter/messages.py"
git -C firestarter_app  diff -- firestarter/messages.py | grep '^[+-]format' -c   # sanity
git                     diff --numstat -- tools/catalog/messages.toml   # expect "1  1  ..."
sha256sum tools/catalog/messages.toml firestarter/tools/catalog/messages.toml \
          firestarter_app/tools/catalog/messages.toml | awk '{print $1}' | sort -u | wc -l   # expect 1
```

## State of the Art

Not a technology-currency question — nothing external moves here. The relevant "what changed" axis is
**how this project's own close discipline has evolved**, because Phase 146 inherits the current state and
CONTEXT's decisions are each a step on this ladder.

| Older approach | Current approach | When it changed | Impact on this phase |
|---|---|---|---|
| Claim gate with a proximity window keyed on domain tokens | **No window at all** — every match anywhere is a violation | v1.31 Phase 139, after measuring that a windowed scanner passed a file with four planted overclaims | D-14 locks it; the ledger must be written around the vocabulary |
| Default targets named via a sibling-directory string constant | **Built from `_HERE` alone**, plus a runtime self-check on locality *and* prefix | v1.30 Phase 137 (construction), v1.31 Phase 139 (the self-check moved *inside* the script) | the 146 copy changes two prefix literals and the target list |
| Bare / `_V130`-suffixed env seam shared across checkers | **Per-milestone suffixed seam**, distinct per instance | v1.30 P-11 point 5 | `…_V131` is taken; pick a fresh name |
| Fixtures only, or plants only | **Both** — a pytest suite for the pattern table, a real-file plant-and-revert for the arming | v1.31 D-12, prompted by Phase 145's three false-GREEN locators | two proofs, not one |
| Corrections as in-situ blocks only (v1.23 D-05) | **Blocks plus a consolidated register** | v1.31 D-05 | `146-CORRECTIONS.md` is new in shape |
| Close performs the push / cut / tag (v1.22, v1.23) | **Close drafts; `/gsd-complete-milestone` publishes** | v1.31 D-01 | the sharpest divergence from precedent; no outward act except one comment |
| Release body names the computed next tag | **Version-agnostic, tag read from `gh release list` at cut time** | v1.23's close | D-02 |
| Ledger = claim classes + negative space | **+ evidence tiers (130 D-09), + process failures as first-class (137)** | v1.23 → v1.30 | both available and recommended for v1.31 |

**Deprecated / superseded figures a plan must not reuse:**
- **leonardo 26906 B / 93.8% / 1766 B headroom** — superseded by **27002 B / 94.2% / 1670 B free** after
  `ebe9cb3`. The stale figure still appears in `PROJECT.md:128` and `PROJECT.md:1181` (both dated footers/
  summaries) and in 143/144's records.
- **`native_loop_v131` 71 (39+32)** — superseded by **79 (47+32)**. Stale in `firestarter/CLAUDE.md:277-279`.
- **`native_trace_v131` counts 91/115/59 as "RED by design"** — retired; 5/5 since 144's re-freeze.
- **MERGE-05 "reads green"** (144's statement) — superseded: green then, +96 B breach now, adjudicated as
  an exemption.
- **The 22.84 s pre-v1.31 write figure** — a *recorded historical number, not a control measurement*
  (boundary 1). Not usable for any comparison.
- **RQ-4's frames-per-block table** — predicted zero intra-block frames at the DB pulse; 64 measured.
  Carry-forward row 12.

## Project Constraints (from CLAUDE.md)

Extracted from `/workspaces/CLAUDE.md` (meta), `firestarter/CLAUDE.md` and `firestarter_app/CLAUDE.md`.
Treat with the same authority as CONTEXT's locked decisions.

| Directive | Source | Bearing on Phase 146 |
|---|---|---|
| This repo tracks only `.planning/` and `.claude/`; neither sub-repo is committed here | meta `CLAUDE.md` §Repository Structure | the gitlink question above; sub-repo commits land **inside** the sub-repos, on the milestone branch |
| Serial-protocol changes must be kept in sync between `serial_comm.py` and `firestarter.cpp` | meta §Key Architecture Points | **not triggered** — D-06 forbids behaviour change; no wire change |
| Constants/flag bits are duplicated between `constants.py` and `firestarter.h` — change both together | meta §Key Architecture Points | **not triggered** — no constant changes |
| The EPROM database is generated; user overrides go in `~/.firestarter/database.json` | meta §Key Architecture Points | `chip_database.json` is byte-unchanged (BENCH-03); never hand-edit it |
| Board differences: Uno 512-byte buffer, Leonardo 1024 — buffer size affects chunked transfer | meta §Key Architecture Points | the residual-gap thresholds the docs cite are board-specific (4687 µs Leonardo / 9375 µs Uno) — do not state one as universal |
| `include/messages.h` is codegen-generated and **id-only** | `firestarter/CLAUDE.md:133-134` | constraint 7; the measured zero-diff |
| `native_params_v131`/`native_loop_v131`/`native_trace_v131` are in **no CI leg**, are excluded from both pinned envs, and must never be passed to `check_size_baseline.py` or `check_build_warnings.py` | `firestarter/CLAUDE.md:260-282` | an unrecognized env name raises an uncaught `KeyError` (F-138-05) — do not name a `*_v131` env to either script |
| The pinned native envs are asserted at exactly **141 cases / 17 suites** | `firestarter/CLAUDE.md:263-264` | adding a case to either turns a live gate RED; this phase adds none |
| The AVR warning watermark is **exactly zero**; the native watermark is 1166 with **zero headroom** | `firestarter/CLAUDE.md` §Native env; 144's record | this phase compiles nothing, so neither is at risk — but a plan that adds `--rebuild` re-enters that constraint |
| Tooling gates are validated against the **py3.9 / 3.11 CI targets**, not the devcontainer's 3.12 | `firestarter_app/CLAUDE.md` | any host-side lint/type claim must name the interpreter; the devcontainer's 3.12 masks CI |
| `firestarter_app` tracks its own `.planning/codebase/` — never `rm -rf` it | recorded project rule | no plan should clean anything under the app's `.planning/` |

**Project skills** (`.claude/skills/`): `devtest-triage`, `devtest-rootcause`, `find-skills`,
`skill-writer`. All four read and none applies — the two `devtest-*` skills are chip-datasheet triage
workflows for community `dev test` issues (and `devtest-triage` posts to `henols/firestarter_prom`, which
this phase must **not** do beyond its one authorized comment); the other two are skill-authoring tooling.
No skill rule constrains this phase's work. Recorded so the planner does not re-check.

**Knowledge graph:** `.planning/graphs/graph.json` exists but `graphify status` reports
`stale: true, age_hours: 1125, commits_behind: 1272`, built at `f4150b8` against a current HEAD of
`c5ee569`. Every artifact this phase reasons about was created in the last nine days, so the graph's
semantic relationships predate all of it. **Deliberately not queried** — a 1272-commit-stale graph would
return v1.21-era relationships and present them as current. Recorded rather than silently skipped.

## Assumptions Log

Every claim in this document is either measured this session or cited to a specific record. The
following are the residual `[ASSUMED]` items — none is a package name, and none is a compliance,
retention or security requirement.

| # | Claim | Section | Risk if wrong |
|---|-------|---------|---------------|
| A1 | Dropping the `UNARMED:` branch (following 139) is the better choice for the 146 gate than keeping it (following 137). | Architecture Patterns 3 | Low. If kept, the fixture suite needs one extra leg asserting UNARMED is unreachable once any artifact exists. Either choice is defensible; the recommendation is a judgement, not a measurement. |
| A2 | The measured-safe substitutes for `proven` (*bench-validated*, *established*, *demonstrated*, *measured*, *evidenced*, *shown*, *attested*) are also acceptable **to the operator's wording review**, not merely to the gate. | Pitfall 2 | Low-moderate. The gate is mechanical and these were probed clean; whether the ledger's tone survives the human half is exactly what constraint 4's review exists to decide. |
| A3 | `PROJECT.md:216` ("Faster than today in the typical case") is a genuine eighth correction rather than acceptable historical prose. | Corrections §5 | Moderate. It is a comparative claim and 145 boundary 1 forbids the milestone from making one — but it sits in a "Target features" section written at scoping, which is arguably a statement of *intent* rather than of result. Surfaced for decision, not decided. |
| A4 | Fixing the host README's two stale `-b` defects (wrong long name, wrong described behaviour) is in scope by adjacency to the `--pulse-us` insertion. | CLOSE-03 §host README | Low. CLOSE-03 does not ask for them. If the planner scopes them out, they should still be recorded in `146-CORRECTIONS.md` as found-and-deferred rather than left silent, because the phase demonstrably read those lines. |
| A5 | Option (a) — assert the gitlink delta and hand the re-pin to `/gsd-complete-milestone` — is preferable to re-pinning in the closing plan. | Runtime State Inventory | Low. Both are D-01-compliant (a gitlink commit is not a push). The risk of (b) is that one meta commit advances both pointers by 66 and 16 commits, which is a large silent change inside a docs phase. |
| A6 | The five `homeless` carry-forwards (rows 1, 2, 5, 8, 12) are correctly identified as having no home anywhere in `REQUIREMENTS.md` §Future Requirements or a backlog stub. | Evidence §twelve carry-forwards | Low-moderate. Derived by cross-referencing the BENCH-LOG's Owner column against §Future Requirements' four FUT ids and ROADMAP 999.30/999.31; a fifth home could exist in an older backlog entry I did not enumerate. |
| A7 | `146-CITATIONS.md` is worth producing even though no CLOSE requirement names it. | Closing-Artifact Shapes | Very low. Every prior close produced one, and D-10's freeze values need a home. |

**Everything else in this document is `[VERIFIED]` or `[CITED]`.** In particular, the three findings that
contradict CONTEXT — the `PROJECT.md` half of correction (1) having no false site, F-140-05 spanning two
rows, and F-140-07 already being corrected in `doc/PROTOCOLS.md` — are each measured, not assumed, and are
tagged with the command or file:line that establishes them.

## Open Questions

1. **Does box 9's grading need the ARM target named, and if so as what?**
   - What we know: three AVR targets build at the tip (measured sizes); the ARM `py32f071` CMake target
     has never compiled any v1.31 code; two commits registered new TUs into its manifest blind; its CI
     workflow fires on every branch push, so `/gsd-complete-milestone`'s push will exercise it for the
     first time on 66 commits.
   - What's unclear: whether gh#15's "all firmware targets" — written 2026-07-12, before the py32 work
     was a v1.31 concern — means the three AVR targets or all four build targets.
   - Recommendation: grade box 9 `met-as-corrected`, with the correction being the target set: *"met for
     the three AVR targets, measured at this tip, carrying MERGE-05's admitted +96 B exemption; the ARM
     `py32f071` build target — which did not exist when this issue was filed — has not been compiled
     against this milestone's code."* That is honest and needs no build. **The alternative** (install the
     ARM toolchain locally and build) is possible but is a build in a docs-only phase and is not asked for
     by any requirement.

2. **Should the ledger state that neither repository's CI has run any v1.31 code?**
   - What we know: measured true for both repos; the "green CI" statements in 143/144's records are
     honest local CI-replica runs and already say so.
   - What's unclear: whether this belongs in the ledger's negative space (a non-claim), in a boundary, or
     is out of scope as a `/gsd-complete-milestone` concern.
   - Recommendation: a ledger row. It is precisely a permitted-claim/non-claim pair ("both suites pass
     locally, at measured counts" / "no CI run has exercised any of it"), and it is the kind of thing a
     reader of a release body would want to know. It also protects the next command from a surprise.

3. **Which of the four `.planning` sites for F-140-07 get a `⚠ CORRECTION` block, and which are history?**
   - What we know: `REQUIREMENTS.md:20` (a D-02 rationale cell), `PROJECT.md:176-181` (live target-features
     prose), `PROJECT.md:1187` (a **dated** v1.31-start footer), `STATE.md:67` (a decision record).
   - What's unclear: dated footers and decision-log entries were true-as-written in the sense that they
     faithfully record what was believed; the project's own precedent has an `inline-history` mechanism for
     exactly that case, and the archived-milestone rule says never edit history.
   - Recommendation: blocks on the two live prose sites (`PROJECT.md:176-181`, `REQUIREMENTS.md:20`);
     leave the dated footer and the decision-log entry as history and name them in the register as
     *"historical, deliberately unedited"*. This mirrors `check_record_corrections.py`'s own
     block-vs-history distinction and the archived-milestone discipline.

4. **Does `146-CORRECTIONS.md` need the 6.25 V caveat after all?**
   - What we know: D-11 says no, on the stated ground that a register of factual corrections should not be
     failed by a rule written for a release body.
   - What's unclear: two of the seven corrections (C3's ceiling, F-140-07's datasheet reason) are
     *about* the physics the 6.25 V ceiling bounds, so the register will likely mention it anyway.
   - Recommendation: keep D-11's rule as written (the gate must not *require* it there), and let the prose
     mention it if it naturally does. A rule that is satisfied incidentally is fine; a rule that forces
     wording is what D-11 rejected.

5. **How many plans, and where do the two blocking gates sit?**
   - Recommendation (discretion, offered not decided): five plans in four waves — (1) the gate + fixtures
     + plant transcript; (2) the seven corrections + register + `messages.toml` regen, in parallel with
     (3) the CLOSE-03 doc edits + the D-13 checker; (4) the ledger, then both release bodies and the
     reconciliation; (5) the closing plan: blocking wording review → blocking posting authorization →
     post → byte-verify → tick CLOSE-01…05 → state/roadmap updates. Both gates land in plan 5, in that
     order (constraint 4). Every plan declares `commits_land_in:` (a worktree leaves submodules empty and
     `files_modified` alone under-detects a submodule target); plans 2 and 3 declare both sub-repos, plans
     1, 4 and 5 declare the meta repo only.

## Environment Availability

| Dependency | Required by | Available | Version / value | Fallback |
|---|---|---|---|---|
| `python3` | both checkers, both suites | ✓ | devcontainer ambient 3.12 (note: CI targets are 3.9/3.11) | — |
| `pytest` (firmware repo) | — | ✓ | ran 314 passed / 19.17 s | — |
| `pytest` (host repo) | D-12 suite pattern reference | ✓ | ran 1590 passed / 258.92 s | — |
| `gh` CLI, authenticated | gh#15 measurement + one post | ✓ | all read-only calls succeeded; GraphQL works | none — CLOSE-04's post has no fallback |
| `gh api graphql` | `lastEditedAt` (not exposed by `--json`) | ✓ | verified | none |
| `git` | freeze SHAs, diffs, porcelain | ✓ | — | — |
| `tools/catalog/codegen.py` + `sync_to_subrepos.sh` | D-06 regen | ✓ | `--check` OK, 76 messages, version 1; both emitters ran | — |
| `.planning/phases/130-…/check_record_corrections.py` | record-gate re-verification | ✓ | ran, exit 0 | — |
| `sha256sum` | catalog-copy identity, archived-file identity | ✓ | — | — |
| `pio` (PlatformIO) | **not needed** — no build in scope | ✓ present | — | n/a |
| `check_size_baseline.py` | only if a plan asserts a fresh MERGE-05 verdict | ✓ present, **but unusable without a build** | prints the never-vacuous FAIL without `--avr-log`/`--native-log`/`--rebuild` | cite Phase 145's recorded verdict |
| ARM toolchain (`arm-none-eabi-gcc`) | only if a plan chooses to close the py32 build gap | **✗ not verified this session** | recorded as installable in this devcontainer with two extra newlib packages CI omits | grade box 9 `met-as-corrected` naming the AVR target set — no toolchain needed |
| Bench hardware (W27C512, Leonardo, Rev 2.0 shield) | **not needed** — no bench run (D-03) | n/a | Phase 145 owned it | cite `145-BENCH-LOG.md` |
| Permission allowlist entry for `gh issue comment` | the post | **✗ absent** | `.claude/settings.local.json` has `gh run`/`gh release`/`gh workflow`/`git push` but not `gh issue comment` | operator approves the prompt at the blocking gate — do **not** add an allowlist entry |

**Missing dependencies with no fallback:** none that block the phase.
**Missing dependencies with a fallback:** the ARM toolchain (fallback: grade box 9 as corrected); a
fresh MERGE-05 verdict (fallback: cite 145's).
**Missing but benign:** the `gh issue comment` allowlist entry — its absence is an *additional* human
checkpoint on the phase's only outward act, which is aligned with D-07 rather than against it.

## Validation Architecture

### Test Framework

| Property | Value |
|---|---|
| Framework | `pytest` (both sub-repos); the phase's own new suite is plain `pytest`, hosted in the phase directory |
| Config file | firmware: **none** (no `pytest.ini`/`pyproject.toml`/`setup.cfg`/`tox.ini`/`conftest.py` at the repo root — measured). host: `pyproject.toml` `[tool.pytest.ini_options]`, `testpaths = ["tests"]`, `addopts = "-ra -q"`. Phase-local suite: none — invoked by path |
| Quick run command | `python3 -m pytest .planning/phases/146-close-honesty-ledger-claim-gate-gh-15-reconciliation/test_check_claims_v131.py -o addopts="" -q` (< 5 s: eleven subprocess legs over small fixtures) |
| Full suite command (firmware) | `cd /workspaces/firestarter && python3 -m pytest tests -o addopts="" -q` — measured **314 passed / 19.17 s** |
| Full suite command (host) | `cd /workspaces/firestarter_app && python3 -m pytest tests -o addopts="" -q` — measured **1590 passed / 30 snapshots / 258.92 s** |
| Hard precondition | **Commit first.** `firestarter/tests/test_flash_path_record_sync.py:1247` and `firestarter_app/tests/test_py32_flash_map_host.py:391` both assert the firmware repo's whole-repo `git status --porcelain == ""` |
| `-o addopts=""` rationale | the host's `addopts` is `-ra -q`; a second `-q` suppresses the count line, and the count is the evidence |

### Phase Requirements → Test Map

| Req | Behavior | Test type | Automated command | Exists? |
|---|---|---|---|---|
| CLOSE-01 | every forbidden pattern fires on a planted fixture | unit (subprocess) | `pytest …/test_check_claims_v131.py -k planted -x` | ❌ Wave 0 |
| CLOSE-01 | every per-file caveat rule fires; unknown basename gets the full set | unit | `pytest …/test_check_claims_v131.py -k caveat -x` | ❌ Wave 0 |
| CLOSE-01 | fail-closed on a missing target; never-vacuous on an empty seam; argv beats env | unit | `pytest …/test_check_claims_v131.py -k "closed or vacuous or precedence" -x` | ❌ Wave 0 |
| CLOSE-01 | `_DEFAULT_TARGETS` resolve inside this directory and all carry the `146-` prefix | unit (introspection) | `pytest …/test_check_claims_v131.py -k default_targets -x` | ❌ Wave 0 |
| CLOSE-01 | **armed and green against all five real artifacts** | integration | `python3 …/146-check-claims.py` (no argv, no env) → exit 0, `PASS:` naming all five basenames | ❌ Wave 0 |
| CLOSE-01 | **seen to fail on a planted violation in a real artifact**, then byte-identical after revert | manual-recorded transcript | the plant-and-revert block above; recorded in `146-CITATIONS.md` with `rc_before/rc_planted/rc_after` and the blob SHA | ❌ Wave 0 |
| CLOSE-02 | the ledger leads with the 6.25 V ceiling and the asymmetric bench coverage | automated locator | `awk` from the first `##` heading, assert `6\.25` and both `skipped-with-reason` protocol names appear before the second `##` — with a negative control (deleting the lead section → 0) | ❌ Wave 0 |
| CLOSE-02 | every permitted claim has a non-claim (no empty column-4 cell) | automated locator | a row-wise check over the claim-class table asserting column 4 is non-empty on every row; non-vacuity leg: an emptied table → exit 1 | ❌ Wave 0 |
| CLOSE-02 | all twelve carry-forwards appear with their Owner text | automated locator | count rows matching the twelve item names → **12**; negative control: delete one → 11 | ❌ Wave 0 |
| CLOSE-03 | all five topics present in the changed docs, zero forbidden phrases | unit (the D-13 checker) | `python3 …/146-check-close03-docs.py` → exit 0, naming every scanned file | ❌ Wave 0 |
| CLOSE-03 | the D-13 checker cannot pass vacuously | unit | empty/repointed target list → exit 1 (never-vacuous); a missing doc → exit 1 (fail-closed) | ❌ Wave 0 |
| CLOSE-03 | the `messages.toml` change produced the measured diff shape | integration | zero-line diff in `messages.h`; one-line diff in `messages.py`; three tomls share one SHA | ❌ Wave 0 |
| CLOSE-03 | the stale `doc/PROTOCOLS.md` §1.3 sentence is gone | automated locator | `grep -c 'Phase 141 replaces it' firestarter/doc/PROTOCOLS.md` → **0**; and `grep -c 'eprom.cpp:159-179'` → **0** | ✅ runnable today (currently returns 1 and 1 — a true RED) |
| CLOSE-03 | `firestarter/CLAUDE.md`'s env total is corrected | automated locator | `grep -c '71 cases' firestarter/CLAUDE.md` → **0** and `grep -c '79 cases' …` → **≥1** | ✅ runnable today (currently 1 and 0 — a true RED) |
| CLOSE-04 | all nine original boxes appear, each with exactly one of the three dispositions | automated locator | per-box count over `146-GH15-RECONCILIATION.md` → 9 rows; disposition vocabulary constrained to the three literals; negative control: a tenth row → fail | ❌ Wave 0 |
| CLOSE-04 | F-140-07's correction is present in the posted text | automated locator | assert both `100 seconds` and `t_w(PR)` appear | ❌ Wave 0 |
| CLOSE-04 | the posted comment byte-equals the frozen text under the named signature | integration | fetch-back: `wc -c` delta == +1, one added blank line at EOF, zero other diff lines | ❌ Wave 0 |
| CLOSE-04 | gh#15 state after the post | integration | `state == OPEN`, comments `1 → 2`, `labels == []`, `lastEditedAt == null` | ❌ Wave 0 |
| CLOSE-04 | the seven corrections all landed, and the record gate still passes | integration | `146-CORRECTIONS.md` row count; `python3 .planning/phases/130-…/check_record_corrections.py` → exit 0 | ✅ the 130 gate exists and passes today (baseline recorded) |
| CLOSE-05 | both bodies are version-agnostic | automated locator | `grep -c '3\.0\.0b' <both bodies>` → **0**; the placeholder token appears exactly once per file | ❌ Wave 0 |
| CLOSE-05 | both bodies describe the behaviour change and `--pulse-us` | automated locator | assert `--pulse-us` and a per-byte-loop phrase in each; negative control on a stripped copy | ❌ Wave 0 |
| CLOSE-05 | the wording review actually happened | manual, blocking | operator's typed authorization recorded verbatim; `autonomous: false`; the resolved `check auto-mode` value recorded | ❌ Wave 0 — manual by nature |
| all | no push / merge / tag / workflow dispatch occurred | integration | `git rev-list --count @{u}..HEAD` unchanged in all three repos across the phase; negative-argv audit table | ❌ Wave 0 |

### Sampling Rate

- **Per task commit:** the phase-local suite (`< 5 s`) plus whichever locators that task's content
  affects. The claim gate itself is instant and should run on every artifact edit.
- **Per wave merge:** the claim gate against every artifact that exists so far (expecting the
  all-or-nothing failure until wave 4 completes — recorded as expected, not as a red), the D-13 checker
  once the doc edits land, and the 130 record gate once the correction blocks land.
- **Phase gate:** commit, then **both** sub-repo suites at their measured baselines (314 / 1590), the
  claim gate green on all five, the D-13 checker green, the 130 record gate green, and the full
  plant-and-revert transcript recorded — all before `/gsd-verify-work`.

### Wave 0 Gaps

- [ ] `146-check-claims.py` — the D-11 gate (CLOSE-01)
- [ ] `test_check_claims_v131.py` — the eleven-leg suite (CLOSE-01, D-12 first half)
- [ ] `fixtures/clean_control.md`, `fixtures/clean_control_second.md` — both must carry the caveats the
      rule set demands, or leg 1 fails for the wrong reason
- [ ] `fixtures/planted_forbidden_claim.md`, `fixtures/planted_proven_unqualified.md`,
      `fixtures/planted_missing_caveat.md` — label-specific plants, probed before the criterion is written
- [ ] `146-check-close03-docs.py` — the D-13 five-topic checker (CLOSE-03)
- [ ] the plant-and-revert transcript in `146-CITATIONS.md` (CLOSE-01, D-12 second half)
- [ ] the ledger/reconciliation/release-body content locators listed above, **each with a negative
      control**, per the recorded rule that a locator which cannot fail proves nothing
- [ ] Framework install: **none required** — `pytest` is present in both sub-repos and the phase-local
      suite needs no config file

**Two locators are runnable today and are true REDs** (`Phase 141 replaces it` → 1; `71 cases` → 1),
which is unusually good news: they can be recorded RED *before* any edit, then GREEN after, satisfying the
"seen to fail for the right reason" discipline without a plant.

## Security Domain

`security_enforcement` is absent from `.planning/config.json`, so it is treated as enabled. This phase
writes no code and changes no behaviour, so most categories are structurally inapplicable — stated
explicitly rather than omitted.

### Applicable ASVS Categories

| ASVS category | Applies | Standard control / disposition |
|---|---|---|
| V2 Authentication | no | no auth surface; `gh` uses the operator's existing credential, unchanged |
| V3 Session Management | no | none |
| V4 Access Control | **partially** | the phase's only privileged action is one `gh issue comment` to a public repo. The control is procedural and already designed: a blocking operator authorization gate (D-10), a negative-argv audit forbidding `--label`/`--assignee`/`gh issue close`/`gh issue edit`, and the absence of an allowlist entry for the call. **Do not add one.** Note `git push`, `gh workflow`, `gh release` and `gh run` **are** allowlisted, so D-01's boundary is procedural, not enforced — hence the recommended structural gate |
| V5 Input Validation | **yes, as a documented finding, not a fix** | `firestarter/src/json_parser.c:503` parses the `pulse-delay` wire field via `extract_long`/`simple_strtoul` into an **unclamped** `uint32_t`. The only firmware-side bound is `0x0B`'s pre-flight `MSG_ERR_PULSE_TOO_WIDE`, gated on `energy_cap_us > 0`, which ships `0` on `0x07`/`0x08`. Host-side `click.IntRange(1, 65535)` is the *only* bound on those two protocols, and it is host-side. **D-06 records this and does not clamp it**; backlog **999.31** owns the decision. The security-relevant framing for the ledger: an unbounded duration on a high-voltage rail is bounded today only by a client-side check |
| V6 Cryptography | no | no crypto. `sha256sum` and `git hash-object` are used as **integrity oracles** only (freeze verification, archived-file identity), which is the correct use |
| V7 Error Handling & Logging | **yes, weakly** | both new checkers must fail closed and must never exit 0 on nothing scanned. That is the never-vacuous guard, and it is a security property of a gate: a gate that passes vacuously is worse than no gate because it is believed |
| V12 Files & Resources | **yes** | the plant-and-revert writes to a **tracked, committed** artifact and must restore it byte-exactly, proven by blob SHA. The fixture suite must write only under its own `fixtures/` or `tmp_path`. Both sub-repo tests already enforce the analogous property (`test_flash_path_record_sync.py:1244-1250` asserts a planted mutation never touched the real record and the repo is clean after) |
| V14 Configuration | **yes** | `.claude/settings.local.json` must not be edited by any plan. An agent message is not consent to change permission settings |

### Known Threat Patterns

| Pattern | STRIDE | Mitigation in this phase |
|---|---|---|
| A gate that passes vacuously and is therefore believed | Repudiation / Tampering | hoisted never-vacuous guard, fail-closed missing-target branch, no exit-0-on-nothing-scanned path, plus fixture legs for each — and the D-12 plant proving the *real* target list |
| A copied checker silently scanning the wrong directory | Tampering | `_HERE`-built targets + the runtime self-check on locality **and** prefix, + two introspection test legs |
| An unreviewed text reaching a public issue | Information disclosure | freeze → blob SHA + byte count → gate green → blocking operator authorization → post → byte-verify. Five steps, all recorded, one call |
| An accidental outward side effect (push fires CI, fires a beta cut) | Elevation of privilege / Tampering | D-01 + constraint 5 + the negative-argv audit + the recommended `@{u}..HEAD` assertion. This has fired **twice** in this project's history |
| Auto-mode auto-approving a human gate | Elevation of privilege | constraint 10; record the **resolved** `check auto-mode` value, not the intent; `autonomous: false` on both gates and stated in prose |
| An unbounded duration on a high-voltage rail, bounded only client-side | Denial of service (to hardware) | **recorded, not fixed** (D-06); T-145-45's threat-register entry claiming a firmware mitigation that does not exist is itself corrected in the ledger's judgement of its wording |
| A correction block silently breaking an existing exemption | Tampering | re-run `check_record_corrections.py` after every insertion; prefer appending over inserting above existing content (twelve `lines=N` exemptions are live) |

**Explicit non-claim for this section:** nothing here is a claim that the shipped firmware is secure
against a hostile host. The wire protocol has no authentication and never has; the `pulse-delay` finding
is a robustness and hardware-safety issue recorded as such, and this phase neither widens nor narrows it.

## Sources

### Primary (HIGH confidence — read or executed in this session)

**Gate donors and their suites**
- `.planning/phases/139-gh-15-correction-outward/139-check-claims.py` — read in full (331 lines)
- `.planning/phases/137-…/check_permitted_claims.py` (361 lines) and
  `test_check_permitted_claims_v130.py` (350 lines) — both read in full; `fixtures/` listed (5 files)
- `.planning/phases/122-…/check_permitted_claims.py` — docstring + `_DEFAULT_TARGETS` (five targets)
- `.planning/phases/130-…/check_record_corrections.py` — docstring, needle table, targets; **executed**, exit 0
- Live probes: the 139 pattern table imported by file path and run against 37 candidate sentences and
  10 whole files

**Shipped source (firmware @ `fa6c9c7`)**
- `src/proms/eprom_params.cpp:22-58` (the table), `include/eprom_params.h:38-83` (columns, enums, PROGMEM contract)
- `src/proms/eprom.cpp` — `:90-110` (the pre-flight refusals), `:247-253` (`eprom_internal_program_pulse`),
  `:284-299` (`eprom_hv_route_mask`), `:400-500` (the per-byte loop, the progress emit, the budget checks)
- `include/eprom.h:166-167` (`EPROM_VPP_SETUP_US 1000` / `EPROM_VPP_HOLD_US 100`)
- `src/json_parser.c:459-497` (the `extract_long` macro chain and `get_delay`), `include/firestarter.h:197`
- `src/proms/memory.cpp:32-34, 243-251, 337` (`mem_util_delay_us` and the pulse call site)
- `include/eprom_budget.h:1-39`, `scripts/check_size_baseline.py:21-167, 274-296`
- `platformio.ini` (env list, `default_envs`), `.github/workflows/py32f071.yml:1-60`, `beta-build.yml` (py32 asset steps)
- `tests/test_flash_path_record_sync.py:252-261, 1244-1250`
- `CLAUDE.md:57-75, 103-146, 260-282`; `doc/PROTOCOLS.md:1-235, 474`; `README.md:111-116`

**Shipped source (host @ `68820a6`)**
- `firestarter/cli_handlers.py:546-610` (the complete `write` option surface), `:684-693` (the provenance line)
- `firestarter/eprom_operations.py:1869-1894` (the `pulse_us` transport)
- `README.md:308-326, 530-571`; `CLAUDE.md`; `doc/` listing (10 files); `pyproject.toml:105-107`
- `tests/test_py32_flash_map_host.py:217-239, 380-395`

**Catalog**
- `tools/catalog/messages.toml:163-167, 922-924` (all three copies SHA-compared)
- `tools/catalog/codegen.py:671-734`; `tools/catalog/sync_to_subrepos.sh` (read in full)
- `firestarter/include/messages.h:51, 137`; `firestarter_app/firestarter/messages.py:66, 252, 842, 1070, 1072`
- Live emitter probe proving the zero-diff / one-line-diff shape

**Records**
- `.planning/REQUIREMENTS.md:1-45, 245-350`; `.planning/ROADMAP.md:160-200, 373-400, 573-640, 2808, 2835`
- `.planning/PROJECT.md:78-231, 1181-1187`; `.planning/STATE.md:2004-2010` (the `d02a88a0` block), `:11, :67, :1121`
- `.planning/phases/145-bench-validation/145-BENCH-LOG.md` — §§2497-2565, 2696-2764 read in full; full heading map
- `145-08-SUMMARY.md` (read in full), `145-CONTEXT.md` D-02/D-08/D-13/D-14/D-16
- `144-TEST-RECORD.md:75, 139-154, 434-476, 514-540`
- `143-HOST-RECORD.md:112-212, 499-511`
- `141-LOOP-RECORD.md:270-295, 443-444, 489-495`
- `140-PARAM-TABLE-RECORD.md:99, 258-272`
- `139-05-SUMMARY.md` (read in full), `139-CITATIONS.md:1-50`, `139-GH15-COMMENT.md` (read in full),
  `139-GH15-ORIGINAL-CRITERIA.md`
- `122-LEDGER.md:1-60`, `130-LEDGER.md` heading map, `137-LEDGER.md:1-120`,
  `137-RELEASE-NOTES-app.md` (read in full), `130-RELEASE-NOTES-fw.md:1-25` + heading map

**Live measurements (read-only)**
- `gh api graphql` on issue 15; `gh issue view 15 --json {state,title,createdAt,updatedAt,body,labels,comments}`
- `gh run list` on `henols/firestarter` (12 rows) and `henols/firestarter_app` (6 rows)
- `git ls-remote --heads origin 'gsd/v1.31*'` in both sub-repos; `git rev-list --left-right --count`
- `git ls-tree HEAD firestarter firestarter_app` vs both live HEADs
- both pytest suites; `codegen.py --check` ×2; `check_record_corrections.py`; `check_size_baseline.py` ×2
- `gsd-tools graphify status`

### Secondary (MEDIUM confidence)

- `.planning/phases/146-…/146-CONTEXT.md` and `146-DISCUSSION-LOG.md` — the locked decisions; treated as
  authoritative for *intent*, and every factual claim in them re-verified rather than inherited (three
  did not hold; all three flagged)
- `/workspaces/CLAUDE.md`, `firestarter/CLAUDE.md`, `firestarter_app/CLAUDE.md` — project directives
- `.claude/settings.json` / `settings.local.json` — permission allowlist inspection
- `.claude/skills/*/SKILL.md` ×4 — read, none applicable

### Tertiary (LOW confidence)

- None. **No web search, no Context7 lookup, and no external documentation fetch was performed**, and
  none was warranted: this phase has zero external dependencies, and every question it raises is
  answerable from this repository's own source, records and live service state. Recorded so the absence
  reads as a decision rather than an omission.

## Metadata

**Confidence breakdown:**
- **Standard stack: HIGH** — nothing is installed; every tool was executed this session.
- **The claim gate's donor and mechanics: HIGH** — the donor read in full, its pattern table transcribed
  and empirically probed against 37 candidate sentences and 10 real files, both recorded traps answered
  with file:line, and the fixture suite mapped leg by leg.
- **The seven corrections: HIGH for six, and the three deviations are themselves HIGH** — every site
  located by grep and read in context; every figure re-derived from shipped source rather than inherited.
  The `PROJECT.md`-has-no-false-site finding rests on a grep returning zero hits, which is a negative
  claim verified by the tool rather than by absence of memory.
- **gh#15 state: HIGH** — five independent oracles, all matching 139's recorded values, including a
  byte-level diff of the extracted criteria file against the live body.
- **CLOSE-03 coverage: HIGH** — measured per file per topic, with the first (wrong) grep re-run after
  noticing that `\|` inside a `-E` pattern is a literal pipe; the corrected counts are the reported ones.
- **The CI-never-ran finding: HIGH** — remote tips, run lists and workflow triggers all measured.
- **Ledger/release-body shapes: HIGH** — three ledgers and four release bodies on disk; the most recent
  of each read in full.
- **Carry-forward accounting: MEDIUM-HIGH** — counted directly from the authoritative table; the
  three-way disagreement between that table, 145-08-SUMMARY and CONTEXT is reported rather than resolved
  by preference, with a recommendation that sidesteps it.
- **Plan decomposition: MEDIUM** — offered as a recommendation under explicit discretion, not measured.

**What might I have missed?** Three candidates, named rather than papered over. (1) I did not enumerate
every backlog entry in `ROADMAP.md`'s 999.x range, so a home for one of the five "homeless"
carry-forwards could exist that I did not find (A6). (2) I did not attempt an ARM build, so the py32
registration commits' correctness is unknown rather than known-bad — the finding is "never compiled",
not "does not compile". (3) I read `130-LEDGER.md` and `122-LEDGER.md` by heading map plus targeted
sections rather than in full, so a structural move present only in their middles could be missing from
the template summary; 137's was read in full and is the most recent.

**Research date:** 2026-08-17
**Measured against:** meta `c5ee5692` (+ uncommitted `.gitignore`, `.planning/ROADMAP.md`, both
gitlinks); `firestarter` `fa6c9c7` (clean); `firestarter_app` `68820a6` (7 untracked, pre-existing)
**Valid until:** ~7 days for the live gh#15 state and the two remote-branch tips (either could move,
and a second gh#15 comment from anyone invalidates the `1 → 2` assertion); ~30 days for everything
source-derived, since D-06 forbids source change in this phase. **Re-measure the gh#15 block and both
`git ls-remote` values at plan time and again in the posting task** — 139's own discipline was to
re-measure every precondition inside the posting task rather than carry it forward, and that discipline
is the reason its post is trustworthy.




