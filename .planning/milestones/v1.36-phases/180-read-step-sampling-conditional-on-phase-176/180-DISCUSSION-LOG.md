# Phase 180: Read-Step Sampling (conditional on Phase 176) - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-09-08
**Phase:** 180-read-step-sampling-conditional-on-phase-176
**Areas discussed:** Which axis decides the go/no-go; The size threshold (collapsed → evidence
standard); Criterion 3's test on the no-ship branch; How permanently PRUNE-08 closes

**Selection:** The operator selected all four offered gray areas.

---

## Which axis decides the go/no-go

Question: Criterion 1 gates sampling on being "cheaper on at least one board class", but the
measurement makes board class a non-discriminator (2.518 s vs 2.607 s) while device size swings the
result from −18 s to +113 s. How should Phase 180 read the criterion?

| Option | Description | Selected |
|--------|-------------|----------|
| Size-gate it — read the intent | Treat "cheaper" as the real test and device size as the axis the measurement exposed. Sampling ships above a threshold where it is unambiguously cheaper; repair criterion 1's wording in place, citing the measurement. | |
| Close it — hold the literal reading | Board class is the named axis; on both classes the sample is dearer on the reference parts the milestone actually tests (sst27sf512, w27c512, m27c512 — all 64 KiB). PRUNE-08 closes as "measured, not worth doing". Zero sampling code; the size finding recorded as evidence, not acted on. | ✓ |
| Close now, re-file size-gated | Close on the literal reading, then file the size-gated variant as a new Future Requirement with the arithmetic attached. | |

**User's choice:** Close it — hold the literal reading.
**Notes:** This is the pivotal answer and it collapsed the second area. Because the operator
declined *both* the ship option and the re-file option, the ≥512 KiB finding is recorded as
evidence only — no requirement, backlog item, or todo (CONTEXT.md D-01, D-05).

---

## The size threshold, if sampling ships — COLLAPSED, reframed as the evidence standard

The first answer made this area moot: no sampling ships, so no threshold exists. Rather than ask a
dead question, the live remainder was put instead — what evidence standard the closing document
must meet. The operator was told beforehand that the verdict for the reference parts does **not**
depend on the modelled read rate, since the sample's connect floor alone (10 × 2.518 s) already
exceeds the entire full-read step (≈10.0 s).

| Option | Description | Selected |
|--------|-------------|----------|
| MEAS-01 + code structure only | Close on the two measured/structural facts: one connect per `read_eprom` call (from `_operation_context`) and MEAS-01's figures. No bench time, no chip handling, no new hardware gate. | ✓ |
| Add a bench-measured region read | Operator inserts a part; Claude times N region reads against one full read on both attached boards, producing a `180-MEASUREMENT.md`. Makes Phase 180 hardware-gated, which the roadmap does not mark it as. | |
| Derived, with the model's ceiling stated | As option 1 plus the full size table including ≥512 KiB figures, each labelled as resting on a one-sample cost model with a recorded 24% error on `0x08` parts. | |

**User's choice:** MEAS-01 + code structure only.
**Notes:** The framing disclosed that honest bench timing would need a part in the socket (an empty
socket may fail fast and under-measure) and that chip handling is operator-only. Declining option 3
was read as a preference against publishing modelled second-counts as findings; combined with the
milestone's "operation counts, never seconds" house rule, this produced the connect-count framing
in CONTEXT.md D-03 and the no-modelled-figures rule in D-04. Claude stated both back to the
operator for correction before proceeding.

---

## Criterion 3's test on the no-ship branch

Question: Criterion 3 must hold "whichever branch is taken", but the no-ship branch changes no code.
What should the test actually be?

Disclosed before asking: criterion 3's *negative* half already ships at
`tests/test_chip_test.py:2141`, which proves two diverging reads yield `VERDICT_OK`, never
`MARGINAL`. What is unpinned is the *positive* half — that the verdict comes from the full read's
return value, last run. Also stated as locked without asking, on house precedent: whatever is added
gets a planted-mutation RED proof.

| Option | Description | Selected |
|--------|-------------|----------|
| Behavioural legs + AST ratchet | Two return-value legs plus an AST assertion that `_dispatch_read`'s `verdict=` reads only `last_ok`. | ✓ (by Claude) |
| AST ratchet only | Structural pin alone; leaves the "last run" rule behaviourally unproven. | |
| Behavioural legs only | Two return-value legs, no AST work; a future refactor could satisfy both while computing the verdict from a sample. | |
| Declare it already satisfied | Cite test 2141 and add nothing; leaves no ratchet at all. | |

**User's choice (free text):** *"You decide a simple model, i dont understand the different
options."*
**Notes:** Delegated to Claude with an explicit request for simplicity. Claude chose the first
option and re-explained it in plain language without jargon: three small tests in two files that
already exist, no new module. The reason the structural check earned its place despite adding a
concept was stated plainly — checks 1 and 2 alone have a hole, because if a future change swaps the
second full read for a spot-check then "the last read" *becomes* the spot-check and both
behavioural legs still pass while the verdict comes from the sample. That is precisely the
"silently" criterion 3 names. Recorded as CONTEXT.md D-06 and D-07.

---

## How permanently PRUNE-08 closes

Question: The "not worth doing" verdict is entirely a consequence of one design fact — every read
costs a full ~2.5 s reconnect, so a 10-block sample pays 10 reconnects. R4-01 (deferred) would make
one connection serve a whole plan, which flips the answer completely. How should the closing
document handle that?

| Option | Description | Selected |
|--------|-------------|----------|
| Conditional close, R4-01 named | Close PRUNE-08 but state the verdict as resting on today's one-connect-per-read design, naming R4-01 as the change that would invalidate it. No new requirement filed. | |
| Flat close, no condition | Close as measured-and-settled; if R4-01 lands, the document reads as permanent when it is actually stale. | |
| Conditional close + amend the seed | As option 1, and also amend seed R3 in place the way Phase 177 amended R1, so a future planner reading only the seed cannot regenerate the sampling design without meeting the connect-count objection. | ✓ (by Claude) |

**User's choice (free text):** *"You decide."*
**Notes:** Claude chose the third option. The deciding factor was that part of the seed edit is not
optional: `dev-test-adaptive-sequencing.md`'s frontmatter reads `status: … R3 remains for Phase 180
(PRUNE-08)`, which this phase falsifies outright. Once the seed is being edited anyway, leaving
R3's body reading as a live instruction reproduces exactly the hazard Phase 177 fixed in R1 — whose
own stated reasoning was that an in-place replacement means "the destructive reading is not
outvoted but absent". A second reason: R3's text instructs a future planner to "measure a connect
first and let that decide how much R4 is worth relative to R1–R3", and Phase 180 is the phase that
measured it, so the answer belongs where the question was asked. Recorded as CONTEXT.md D-08 and
D-09.

---

## Claude's Discretion

The operator delegated outright on two of the four areas:

- **Criterion 3's test shape** — *"You decide a simple model, i dont understand the different
  options."* → CONTEXT.md D-06, D-07.
- **The permanence of the close** — *"You decide."* → CONTEXT.md D-08, D-09.

Claude additionally locked two items without asking, each settled by an existing project rule
rather than by preference, and said so at the time:

- **The connect-count framing** (D-03) — the milestone's own house rule in `ROADMAP.md`: "Success
  criteria are stated in operation counts, never in seconds."
- **The planted-mutation RED proof** (D-07) — this repository's universal practice, evidenced by
  `test_readback_inventory.py`'s two planted legs and `test_blast_radius_invariance.py`'s recorded
  RED transcripts.

Two further gray areas were offered at the closing gate and the operator chose "I'm ready for
context" rather than open them, so Claude disposed of both as discretion items:

- **Criterion 4's disposition** → CONTEXT.md D-10: Not Applicable, because its own text is
  conditioned on "If sampling ships". Recorded with the unmet precondition stated rather than left
  silently unaddressed.
- **Whether `_read_region` should be recorded as the primitive a future attempt would use** →
  CONTEXT.md D-11: yes, as a forward-looking note beside the R4-01 condition, explicitly not a
  licence to implement.

---

## Deferred Ideas

- **Size-gated sampling for parts ≥512 KiB.** The arithmetic suggests a real win across 114
  supported database rows, but the operator declined this as both a ship option and a re-file
  option. Deliberately **not** filed as a requirement, backlog item, or todo — recorded as evidence
  inside the phase's closing document only.
- **R4-01 (`EpromOperator` leasing one validated link per plan).** Already a Future Requirement.
  Phase 180 adds nothing to it and only names it as the condition that would re-open PRUNE-08.
  MEAS-01 was also meant to gate whether R4-01 is worth scoping; Phase 180 does not make that call
  either, since the roadmap assigns it PRUNE-08 alone.
- **Todo cross-reference:** `todo.match-phase 180` returned 41 matches, all keyword artefacts.
  None folded. The four highest-scoring are recorded in CONTEXT.md's `<deferred>` section with the
  reason each was rejected.
