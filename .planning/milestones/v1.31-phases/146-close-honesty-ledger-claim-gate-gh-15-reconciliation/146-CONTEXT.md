# Phase 146: Close — Honesty Ledger, Claim Gate & gh#15 Reconciliation - Context

**Gathered:** 2026-08-17
**Status:** Ready for planning

<domain>
## Phase Boundary

Close v1.31 with a record that claims exactly what its evidence supports, a machine gate that
enforces that boundary against the real files, sub-repo documentation that describes the behaviour
which actually shipped, gh#15 answered box by box in public, and release notes a stranger can act on.

What it delivers:

1. A **claim gate** (`146-check-claims.py` + fixtures + a real-file plant transcript) armed
   all-or-nothing on this phase's five closing artifacts, seen to fail before being trusted
   (`CLOSE-01`).
2. A **`146-LEDGER.md`** pairing every permitted claim with its explicit non-claim, leading with the
   6.25 V program-VCC ceiling and the asymmetric bench coverage (`CLOSE-02`).
3. **Firmware and host documentation** describing the per-byte loop, the parameter table, the
   database-supplied pulse, `--pulse-us` and the 6.25 V accepted debt — plus a phase-local script
   checking those five topics are present and no forbidden phrase is (`CLOSE-03`).
4. A **`146-GH15-RECONCILIATION.md`**, posted to gh#15 as a second comment, grading the **original**
   nine acceptance boxes item by item (`CLOSE-04`).
5. **Two version-agnostic release-notes drafts** — `146-RELEASE-NOTES-fw.md` and
   `146-RELEASE-NOTES-app.md` — behind a blocking operator wording review (`CLOSE-05`).
6. The **seven inherited corrections** four prior phases routed to "Phase 146 / CLOSE-04", landed as
   labelled `⚠ CORRECTION` blocks plus a `146-CORRECTIONS.md` register (D-04, D-05, D-06).

**Not in this phase:**

- **Any push, merge, beta cut, tag or PyPI dispatch** (D-01). The merge to `beta`, the cut and the
  `v1.31` tag all belong to `/gsd-complete-milestone`. This is the sharpest divergence from v1.23's
  close, where the push *was* CLOSE-04's literal text.
- **Any behaviour change in either sub-repo.** Sub-repo edits are documentation and message **wording**
  only (D-06). The firmware image Phase 145 bench-validated is provably the one that ships.
- **Clamping `extract_long`'s `pulse-delay`** — recorded as a correction, not fixed (D-06).
- **Any bench run.** This phase is docs-and-claims only; Phase 145's ten `no v1.31 owner`
  carry-forwards get ledger rows, never a re-measurement (D-03).
- **Closing gh#15** (D-07) and **editing its body** (D-07) — declined once already at 139-05.
- **New backlog stubs** for Phase 145's residuals (D-03). 999.30 and 999.31 already exist; the rest
  have homes in `REQUIREMENTS.md` §Future Requirements or in BENCH-02's disposition records.
- **Any `support_status` or `chip_database.json` change** — D-07 of the milestone scoping, and
  BENCH-03 proved zero diff at the tip.

**The evidence ceiling is load-bearing and this is the phase that publishes against it.**
`.planning/REQUIREMENTS.md` §"Evidence ceiling" fixes the boundary: v1.31 buys *timing / pulse-count /
verify* fidelity and **not** silicon-margin fidelity, because the ~6.25 V program-VCC rail all four
vendor algorithms assume is unreachable on this shield.

</domain>

<decisions>
## Implementation Decisions

### The publication boundary — CLOSE-05

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

### CLOSE-04's real scope — the inherited correction queue

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

### gh#15's outward act — CLOSE-04

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

### The claim gate — CLOSE-01

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

### Hard sequencing constraints these decisions imply

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

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### The requirements, the ceiling and the phase's own criteria (read first)
- `.planning/REQUIREMENTS.md` — §"Evidence ceiling — fixed before any code moves" (the ~6.25 V
  program-VCC statement, verbatim, and the explicit "not behavior-preserving" clause); **CLOSE-01…
  CLOSE-05 verbatim**; §"Decisions taken at scoping" **D-01…D-08**; §"Future Requirements"
  (FUT-PRESTO, FUT-VCC, FUT-MAXPULSE, FUT-OVERPROG-MAP — D-03's homes); §"Out of Scope".
- `.planning/ROADMAP.md` §"Phase 146: Close — Honesty Ledger, Claim Gate & gh#15 Reconciliation" —
  the goal, the dependency on Phases 145 and 139, and the five success criteria.
- `.planning/ROADMAP.md` **line 392** — the dual-repo correction paragraph that names *"amending this
  prose and the milestone's matching sequencing sentence is Phase 146 / CLOSE-04's, alongside C3,
  F-140-05, F-140-07 and H3."* This is D-04's own charter.
- `.planning/ROADMAP.md` §"Sequencing spine" (line 167) — the second sentence D-04 corrects.
- `.planning/PROJECT.md` §"Current Milestone: v1.31" — the per-phase closing summaries, the throughput
  table F-140-05 corrects, and the `0x0B` energy-cap justification F-140-07 corrects.

### The evidence this close reports on
- `.planning/phases/145-bench-validation/145-BENCH-LOG.md` — the phase `VERDICT`, the `Gate 3 verdict
  (resumed session — FINAL)` line, §"Not measured", and §"Carry-forward hand-offs with no v1.31 owner".
  **D-03 cites this record; it does not re-derive it.**
- `.planning/phases/145-bench-validation/145-08-SUMMARY.md` — the complete 12-row carry-forward table
  with owners, the never-reaches-100% finding table, the D-10 contradiction stated-not-reconciled, the
  suite results with the +2 divergence explained, and the "What this plan did NOT prove" list. This is
  the densest single input to `146-LEDGER.md`.
- `.planning/phases/145-bench-validation/145-CONTEXT.md` — D-08 (no comparative claim), D-14 (two
  states only: validated or skipped-with-reason), D-16 (no source change), D-02 (the `0x08`/`0x0B`
  disposition records the ledger cites rather than re-deriving).
- `.planning/phases/144-tests-build-verification/144-TEST-RECORD.md` §10 — **H1** (CLOSE-02), **H2**
  (CLOSE-01), **H3** (CLOSE-04's gh#15 half), **H4** (143 D-01's prose correction), **H5** (F-144-01's
  stale `native_loop_v131` total), **H7** (the Leonardo headroom armed against this phase).
- `.planning/phases/143-host-timeout-progress-pulse-override/143-HOST-RECORD.md` — §1 the honest
  headline; §4 the padding rule and the `[ASSUMED]` A1 figure; §5 items 1/5/6/7 (`leonardo`-only
  emission, the 4687 µs residual-gap threshold, `--pulse-us`'s bound provenance); §6 D-01's prose
  correction; §10 **H5** (`--pulse-us` documentation is CLOSE-03's) and **H6** (the CLOSE-04 queue);
  §11 the deferred list with each item's owner.
- `.planning/phases/141-per-byte-program-loop/141-LOOP-RECORD.md` §12 — **H3** (C3, the unclamped
  `extract_long` at `json_parser.c:503`) and **H4** (the honest 50 ms / 99998 µs energy-cap ceiling),
  both routed to CLOSE-04; §"Findings" **F-141-01** (MERGE-05 RED, operator-owned) and **F-141-07**.
- `.planning/phases/140-parameter-table/140-PARAM-TABLE-RECORD.md` — §3 and §10 for **F-140-05** and
  **F-140-07** verbatim (F-140-07: the TI TMS 2516 datasheet states total programming time of **100
  seconds**; 50 ms is `t_w(PR)` TYP per-location, so the *value* is right and the *published reason* is
  wrong); §11's hand-off row naming exactly what CLOSE-04 owes; **F-140-09** (what 140-06 already
  corrected in `doc/PROTOCOLS.md`, so this phase does not redo it).
- `.planning/STATE.md` `## Decisions` — the last five entries (commit `d02a88a0`) carry the **MERGE-05
  +96 B adjudication with the wording CLOSE-02 should quote verbatim**, the three rejected
  alternatives, the archived-v1.23-untouched assertion, the flash-only scope, and the fixture
  re-derivation. Do not re-derive any of it.

### gh#15 — the reconciliation's subject
- `.planning/phases/139-gh-15-correction-outward/139-GH15-ORIGINAL-CRITERIA.md` — **the nine boxes as
  filed.** D-08 grades against exactly this file.
- `.planning/phases/139-gh-15-correction-outward/139-GH15-COMMENT.md` — the posted correction
  (comment `#5233463320`, frozen blob `d77a639c`, 12193 bytes), including its own original-box
  disposition table and the sentence F-140-07 corrects.
- `.planning/phases/139-gh-15-correction-outward/139-GH15-BODY-AMENDMENT.md` — drafted, **declined**,
  never applied. D-07 does not revive it.
- `.planning/phases/139-gh-15-correction-outward/139-05-SUMMARY.md` — the posting mechanics D-10
  follows, and the two recorded oracle gotchas (`updatedAt` bumps on comment creation and is not a
  body-edit oracle; `lastEditedAt = null` is).
- `.planning/phases/139-gh-15-correction-outward/139-CITATIONS.md` — the citation register pattern.

### The claim gate's donor and its predecessors
- `.planning/phases/139-gh-15-correction-outward/139-check-claims.py` — **read the module docstring in
  full.** This milestone's own forbidden vocabulary (12 patterns, including `\bproven\b`), the two
  required caveat patterns, **no proximity window by design** and the measured reason why, the
  `_HERE` construction, `_assert_default_targets_are_local()`, `resolve_targets`' argv/env/defaults
  precedence with the `is not None` env check, the hoisted never-vacuous guard, the fail-closed
  missing-target branch, and its explicit non-claim #2 stating it is *compliance with the spirit of*
  CLOSE-01 and **not a build of it**. D-11's gate is its 146-scoped sibling.
- `.planning/phases/137-close-honesty-ledger-claim-gate-gh12-followup/check_permitted_claims.py`,
  `test_check_permitted_claims_v130.py` and `fixtures/` — the v1.30 instance and the fixture-plus-pytest
  shape D-12 mirrors.
- `.planning/phases/123-non-regression-baselines-gate-hardening/check_permitted_claims.py` — v1.23's,
  for the all-or-nothing arming contract and the env-seam naming convention.
- `.planning/phases/122-close-honesty-ledger-community-ask-release-decision/check_permitted_claims.py`
  — v1.22's original, and the source of D-14's cite-by-`file:line` solution to the self-reference trap.

### The closing-artifact shapes
- `.planning/phases/122-.../122-LEDGER.md` — the structural precedent: identity header, status key,
  claim classes with explicit non-claims, mechanism corrections, "what this milestone chose not to
  prove", "what no test can close", and the scanner-status paragraph.
- `.planning/phases/130-.../130-LEDGER.md` and `.planning/phases/130-.../130-CONTEXT.md` — 130 D-09's
  evidence-tier grouping, D-10's negative-space rule (D-03's precedent), D-12's two-axis rows.
- `.planning/phases/137-.../137-LEDGER.md` and `137-RELEASE-NOTES-app.md` — the most recent instance.
- `.planning/phases/122-.../122-RELEASE-NOTES-fw.md` and `122-RELEASE-NOTES-app.md`,
  `.planning/phases/130-.../130-RELEASE-NOTES-fw.md` and `130-RELEASE-NOTES-app.md` — the four
  release-body precedents D-02's drafts follow.

### CLOSE-03's documentation targets
- `firestarter/doc/PROTOCOLS.md` §§1.3–1.5 (`0x07`, `0x08`, `0x0B`) — **stale since 140-06.** §1.3
  still says *"The firmware's present loop (`eprom.cpp:159-179`) is retry escalation of `pulse_delay`
  … Phase 141 replaces it"* — Phase 141 landed five phases ago. §1.3 also already carries F-140-05's
  named divergence and points at Phase 146 as the follow-up.
- `firestarter/CLAUDE.md` — the living per-protocol reference, updated at 140-06, 141-05, 142-07 and
  143-10. Its `0x0B` row already documents the energy cap, the 99998 µs worst case and the
  `--pulse-us` interaction (lines 66, 136–137). Carries F-144-01's stale `native_loop_v131` total.
- `firestarter/README.md` §"Protocol Notes" — the user-facing firmware surface.
- `firestarter_app/README.md` — **zero v1.31 doc commits.** The `write` options list (`:311-317`) has
  `-b/--ignore-blank-check` and `-f/--force` and **no `--pulse-us`**; §"Eprom Configuration"
  (`:531+`) documents the `pulse-delay` DB field and the `~/.firestarter/database.json` override path.
- `firestarter_app/doc/protocol-id.md` and `firestarter_app/doc/protocol-flags.md` — the host-side
  protocol reference pair.
- `firestarter_app/CLAUDE.md` and `firestarter/CLAUDE.md` — command surface and the tooling gate
  (validated against the **py3.9/3.11 CI targets**, not the devcontainer's 3.12).

### The message-wording change (D-06)
- `./tools/catalog/messages.toml`, `firestarter/tools/catalog/messages.toml`,
  `firestarter_app/tools/catalog/messages.toml` — **three copies, lockstep.**
  `MSG_INFO_RETRIES` at `:163`, `DBG_PULSE_DELAY_MISMATCH` at `:922` in each.
- `firestarter/include/messages.h` (`:51`, `:137`) — **ID-only and codegen-generated.** A
  wording-only change produces a zero diff here.
- `firestarter_app/firestarter/messages.py` (`:66`, `:252`, `:842`, `:1070`) — codegen-generated and
  format-stable; never hand-normalize the emitter's output.

### The shipped code the docs must describe accurately
- `firestarter/src/proms/eprom.cpp` — the per-byte pulse→verify loop, `eprom_internal_program_pulse()`,
  `eprom_hv_route_mask()`, the `energy_cap_us > 0` guard, and the `MSG_DATA_PROGRESS` emit.
- `firestarter/src/proms/eprom_params.{h,cpp}` — the six-column parameter table and `eprom_params_for()`.
  `energy_cap_us = 0` on `0x07` and `0x08` (999.31's subject); `50000` on `0x0B`.
- `firestarter/src/proms/eprom_budget.{h,cpp}` — CAP-03's advertised per-block budget arithmetic.
- `firestarter_app/firestarter/cli_handlers.py` — `write --pulse-us` (`click.IntRange(1, 65535)`,
  `default=None`, `write`-only) and its provenance line.
- `firestarter_app/firestarter/eprom_operations.py` — the `pulse_us` transport, the CAP-03 timeout
  decode, and the progress rendering.
- `firestarter/scripts/check_size_baseline.py` — `MERGE05_DEFECT_FIX_EXEMPTION_BYTES = 96`,
  `_merge05_flash_allowance()`, and the decomposed PASS/FAIL text the ledger quotes.

### Backlog items this close hands to
- `.planning/ROADMAP.md` §"Phase 999.30" — the MAIN write bar never reaching 100 %, with the six-run
  table and the proven mechanism.
- `.planning/ROADMAP.md` §"Phase 999.31" — no firmware-side upper bound on `--pulse-us` for
  `0x07`/`0x08`, and **the T-145-45 documentation defect** (a threat-register entry asserting a
  firmware mitigation that does not exist). D-06 leaves the code alone; the ledger may judge the wording.

</canonical_refs>

<code_context>
## Existing Code Insights

### Measured live during this discussion (2026-08-17) — re-verify at plan time, do NOT inherit
- **gh#15 is OPEN**, `comment_count: 1`, title *"Implement protocol-specific EPROM programming
  algorithms in firmware"*, body **unedited** (all nine boxes unticked).
- **`firestarter`** is on `gsd/v1.31-27c-programming-algorithm-fidelity` at **`fa6c9c7`**,
  **66 ahead / 2 behind** `origin/beta`. **`firestarter_app`** is on the same branch at **`68820a6`**,
  **16 ahead / 0 behind**. D-01 pushes neither, but the "2 behind" on the firmware side is a fact
  `/gsd-complete-milestone` will have to resolve.
- **`firestarter_app` has ZERO v1.31 commits touching `doc/`, `README.md` or `CLAUDE.md`.** The
  firmware has six, five of them to `CLAUDE.md` and one to `doc/PROTOCOLS.md` (at 140-06).
- **`--pulse-us` appears nowhere** in `firestarter_app/README.md` or `firestarter_app/doc/*.md`.
- **Working-tree dirt to expect** so a cleanliness assertion does not read pre-existing dirt as its
  own damage: meta has modified `.gitignore`, modified `.planning/ROADMAP.md`, both gitlinks modified,
  and untracked `.claude/`, `.planning/VALIDATED-EPROMS.md`, `package.json`, `package-lock.json`;
  `firestarter_app` has untracked `.planning/config.json`, `SECURITY.md`, four `datasheets/*.pdf` and
  `write_test_port.sh`.
- **`.planning/ROADMAP.md` is uncommitted** at discussion time — snapshot before any edit. The
  change is small and pre-existing (not this discussion's): a **2-line** heading rename,
  `### Phase 146 (close): Honesty Ledger…` → `### Phase 146: Close — Honesty Ledger…`, plus the
  matching phase-list line. Committed by whoever owns it, or folded into the first 146 plan — but a
  porcelain assertion written against a clean tree will read it as its own damage.
- **⚠ `STATE.md`'s `last_activity_desc` hands Phase 146 a job that is ALREADY DONE. Do not re-do it.**
  It says *"CARRIED FORWARD TO PHASE 146: ROADMAP's v1.31 Coverage table is STALE for 12 rows —
  PREP-01..04, ISSUE-01..03, HOST-01..05 read Pending … Phase 146 OWNS it."* That drift was discharged
  by commit **`6822ee2d`** (`docs(146-PRE): sync ROADMAP v1.31 Coverage with REQUIREMENTS.md -- 12
  stale rows`), which landed **after** the 145-09 state write. Verified at discussion time: all twelve
  rows read `Complete` in `ROADMAP.md` (`:592-598`, `:616-620`) and match `REQUIREMENTS.md`. The only
  `Pending` rows left in either table are `CLOSE-01…CLOSE-05`, which are this phase's to flip. **Verify
  before flipping anything, and treat the STATE.md sentence as stale rather than as an instruction.**
- **No `CHANGELOG.md` exists in either sub-repo.** Release notes are GitHub release bodies, drafted as
  `.planning` artifacts; there is no in-repo changelog to update.
- **`.planning/config.json`'s `planning.sub_repos` lists FOUR repos** — `firestarter`,
  `firestarter_app`, `firestarter_app_py32`, `firestarter_py32_ci`. Any close step that iterates it
  reaches into two py32 scratch worktrees that are **not** part of this deliverable. Iterate the two
  named sub-repos explicitly.
- **`firestarter_py32_ci` and `firestarter_app_py32` also carry `tools/catalog/messages.toml`** — five
  copies exist on disk. D-06's lockstep is the **three** real ones only.

### Reusable Assets
- **`139-check-claims.py`** — this milestone's vocabulary, already written and already correct in the
  ways that matter: no proximity window, a startup self-check that fails loudly if copied into another
  phase's directory, a fail-closed missing-target branch, and no exit-0-on-nothing-scanned path.
  D-11's gate is a 146-scoped sibling of it, not a copy: the self-check's `139-` prefix assertion must
  become `146-`, and the caveat rule becomes per-file (D-11).
- **`137-check_permitted_claims.py` + `test_check_permitted_claims_v130.py` + `fixtures/`** — the
  pytest-plus-fixtures shape D-12's first half mirrors, already three milestones old.
- **`122-LEDGER.md` / `130-LEDGER.md` / `137-LEDGER.md`** — three prior instances of exactly this
  artifact. Do not re-derive the structure.
- **`145-BENCH-LOG.md` and `145-08-SUMMARY.md`** — the ledger's raw material is already written,
  hashed and committed. The ledger cites; it does not re-measure (D-03).
- **The MERGE-05 adjudication wording in `STATE.md`** (commit `d02a88a0`) — explicitly authored as
  *"Wording for Phase 146 / CLOSE-02's honesty ledger, quotable verbatim."* Quote it.
- **`139-GH15-ORIGINAL-CRITERIA.md`** — the nine boxes already extracted to a file, so D-08 does not
  have to re-scrape the issue body.

### Established Patterns
- **Honesty lives in the message text, never in a status code** (117 D-05, 118 D-02, 119 D-12, 120 D-11).
- **A reversal is recorded *as* a reversal, with its constraints named** (119 D-18, 120 D-20).
- **Every claim is judged against the live measured figure, never a predicted one.**
- **`- **D-NN: text**` must close its bold run on ONE line**, carry at most one colon before the
  closing `**`, and never open with a glyph — otherwise plan-phase's decision-coverage gate fails
  closed with `reason: could-not-parse`.
- **A pre-authored gate leg can be UNREACHABLE.** RED proves nothing until it has been seen to pass
  for the right reason; read failure reasons, fix locators only, and keep a RED-preserving proof.
  Phase 145 caught three false-GREEN locators, one passing against an empty record.
- **A check that agrees with what you want is the one to re-derive** — 145-08's own stated lesson,
  after a `git diff | grep -c '^[+-][^+-]'` sweep reported zero changed lines over a file that had
  genuinely changed (the `-` marker collides with the markdown list bullet; use `--numstat`).
- **GSD `requirements`/`roadmap` verbs reformat the WHOLE file** (`_normalizeMd` blast radius) and
  `phase.complete` can clobber an unrelated phase's `**Plans:**` line. Prefer hand edits with
  snapshot-and-diff; `roadmap.update-plan-progress` was deliberately not used in 145-08 for this reason.
- **`gsd-tools` state verbs clobber `last_activity_desc`** — observed twice in 145-08, replacing it
  with truncated garbage. Call the verbs, then hand-repair with a diff proving only intended lines moved.
- **Archived milestone requirements are never edited.** The v1.23 MERGE-05 row and `v1.23-ROADMAP.md`
  were asserted byte-identical by SHA256 rather than annotated; the archived v1.2/v1.3 `BENCH-01/02/03`
  rows were likewise asserted byte-identical in 145-09 because they are different requirements sharing
  ids. Any correction this phase makes stays in **live** documents.
- **Doubling pytest `-q` hides the count line** — `addopts` is `-ra -q`; run with `-o addopts=""` when
  a count is needed as evidence.

### Integration Points
- `.planning/phases/146-close-honesty-ledger-claim-gate-gh-15-reconciliation/` — `146-LEDGER.md`,
  `146-CORRECTIONS.md`, `146-GH15-RECONCILIATION.md`, `146-RELEASE-NOTES-fw.md`,
  `146-RELEASE-NOTES-app.md`, `146-check-claims.py`, the doc-topic checker, `fixtures/`, and the
  plant-and-revert transcript.
- `.planning/ROADMAP.md`, `.planning/PROJECT.md`, `.planning/STATE.md` — D-05's `⚠ CORRECTION` blocks
  and the in-place STATE.md edits.
- `.planning/REQUIREMENTS.md` — CLOSE-01…CLOSE-05's checkboxes and Traceability rows. Note 145-09's
  measured lesson: this file carries its **own** Traceability table, so a requirement flip is **four**
  lines per requirement (checkbox plus row), not one — the "exactly six lines" figure in 145-09's plan
  was computed without noticing that, and Variant B (12 lines for three requirements) was the correct
  edit. Budget accordingly for five requirements.
- `firestarter/doc/PROTOCOLS.md`, `firestarter/CLAUDE.md`, `firestarter/README.md` — CLOSE-03,
  firmware half.
- `firestarter_app/README.md`, `firestarter_app/doc/` — CLOSE-03, host half.
- Three copies of `tools/catalog/messages.toml` plus the regenerated `messages.h` / `messages.py` — D-06.
- gh#15 — one posted comment (D-07), issue left open, body untouched.
- **Every plan must declare `commits_land_in:`** — a worktree leaves submodules empty and
  `files_modified` alone under-detects a submodule target.

</code_context>

<specifics>
## Specific Ideas

- **F-140-07's error is already public in our own comment.** The gh#15 correction states `0x0B`'s 50 ms
  cap is *"the classic 2716 total programming time"*; the TI TMS 2516 datasheet gives total programming
  time as **100 seconds** and 50 ms as the per-location `t_w(PR)` TYP. The value is right, the published
  reason is wrong, and correcting it in public is the single strongest argument for D-07's post.
- **"Met-as-corrected, naming the correction" only parses against the original nine boxes** — which is
  why D-08 grades the text as filed rather than the amended set.
- **The gate's own vocabulary is a writing constraint, not just a check.** `\bproven\b` is forbidden
  unqualified, and the phase records use it honestly throughout ("the mechanism is proven, not
  guessed"). The closing artifacts must be written around it (D-14), never the pattern loosened.
- **`145-08-SUMMARY.md`'s "What this plan did NOT prove" list is nearly a ready-made non-claim column**
  — no comparative claim, no datasheet conformance in either direction, scope of one part / one
  controller / one shield revision, `0x08`/`0x0B` fixed in the golden trace only and never on a part,
  Gate 2 and Gate 3 both run on a build carrying MERGE-05's then-open breach, the single-byte margin
  failure mitigated rather than explained.
- **MERGE-05's +96 B is ADMITTED, not remediated, and the record says so in three ways** — a named
  SHA-attributed exemption constant, a decomposed PASS/FAIL string that keeps the growth visible rather
  than laundering it into a moved anchor, and a negative control one byte past the exemption. The
  ledger's job is to state that plainly, including that F-141-01 was never remediated and that Phase
  144's earlier green came from **the anchor moving**, not from growth shrinking.
- **The progress bar never reaching 100 % is cosmetic and every write verified byte-exact** — the
  ledger must not let a 91.8 % bar read as a 91.8 % write.
- **`--force used? No` and `D-09's re-seat allowance: UNCONSUMED`** are load-bearing lines in the bench
  record. If the ledger summarises the bench posture, those two facts belong in it.

</specifics>

<deferred>
## Deferred Ideas

### Raised during this discussion, declined with a reason
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

### Carried forward, still not taken — the `no v1.31 owner` set
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

### Reviewed Todos (not folded)
`todo.match-phase 146` returned matches; **none folded.** Every one is other-family firmware or
hardware work in a phase that changes no behaviour (D-06). Named matches: "Skip VPP error/warning
checks when VPP is unused (reads/blank-checks)" (0.9, firmware — declined at Phases 118–122, 130, 142
and again here), "CONFIG_VERSION is not bumped when a calibration default changes" (0.9, firmware),
"FM1608 byte 0 write never lands" (0.9, a different write path), "AT28C256 write-path failure (gh#20)"
(0.6, `0x0D` EEPROM, not 27C). The scores come from bare-word overlap — "vpp", "phase", "gate",
"status", "firmware" — not scope overlap. **`gh12-followup-after-dev-sdp-retirement.md` is v1.30's
outward-facing debt and is not v1.31's** — no community thread other than gh#15 gets a comment this
milestone.

</deferred>

---

*Phase: 146-close-honesty-ledger-claim-gate-gh-15-reconciliation*
*Context gathered: 2026-08-17*
