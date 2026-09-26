# Phase 180: Read-Step Sampling (conditional on Phase 176) - Context

**Gathered:** 2026-09-08
**Status:** Ready for planning

<domain>
## Phase Boundary

This phase **spends** Phase 176's connect-cost measurement on PRUNE-08's go/no-go, and the
go/no-go is **already decided by the operator during this discussion: PRUNE-08 closes as
"measured, not worth doing."**

Roadmap success criterion 2 is the branch taken. Criterion 1 is not taken. Criterion 4 is
conditioned on `If sampling ships` and is therefore Not Applicable — see D-10.

**In scope — exactly four deliverables:**

1. A closing document recording the measured/structural argument that PRUNE-08 is not worth doing.
2. Roadmap criterion 3's discharge: three small tests pinning the read step's verdict source to the
   full read (D-06).
3. An in-place amendment to `.planning/seeds/dev-test-adaptive-sequencing.md` — R3's body and the
   frontmatter `status:` line (D-09).
4. Requirement marking: PRUNE-08 flipped to Complete in `.planning/REQUIREMENTS.md`'s v1 checkbox
   and its traceability row.

**Explicitly out of scope — do not write any of this:**

- **Any sampling implementation.** No bit-structured sampler, no block list, no `1 << k` boundary
  computation, no escalate-on-divergence path. Zero lines of sampling code ship in this phase.
- Any change to `_dispatch_read`'s behaviour. The three tests in D-06 pin what the function
  **already does**; they do not modify it.
- Any bench/hardware work. **This phase is NOT hardware-gated** (D-02) and the roadmap does not
  mark it as such. Do not add a `blocking-human` bench wave.
- R4-01 (session leasing). Named only as the condition that would invalidate the close (D-08);
  never implemented or scoped here.
- Any new requirement for size-gated sampling (D-05).

</domain>

<decisions>
## Implementation Decisions

### The go/no-go verdict

- **D-01:** **PRUNE-08 closes as "measured, not worth doing"** — roadmap criterion 2, holding
  criterion 1's `board class` axis literally. The measurement makes board class a
  non-discriminator (Uno 2.518 s vs Leonardo 2.607 s median, over a shared 2.500 s structural
  floor), and on **both** classes the sample is dearer than the full read it would replace for
  every reference part this milestone actually tests (sst27sf512, w27c512, m27c512 — all 64 KiB).
  The operator was shown the alternative reading (size-gate it) and **declined it**. Do not
  re-litigate. — **Reversibility:** reversible — a document-and-requirement decision; no product
  behaviour changes, so undoing it costs nothing already spent.

- **D-02:** **Evidence standard is MEAS-01 plus code structure only.** The two load-bearing facts
  are (a) every `operator.read_eprom(...)` call pays exactly one full connect, which is
  *structural* — `_operation_context` calls `find_and_connect` on entry and
  `_disconnect_programmer()` in its `finally` block — and (b) MEAS-01's measured per-connect cost.
  The operator declined adding a bench-measured multi-region read, because honest timing would
  need a part in the socket and chip handling is operator-only. **Phase 180 therefore acquires no
  hardware gate.** — **Reversibility:** reversible.

- **D-03:** **The closing argument is stated in connect counts, never second-counts.** This is the
  milestone's own house rule (`ROADMAP.md`: *"Success criteria are stated in operation counts,
  never in seconds"*). Form the argument as: the sample costs **N connects** where the full read
  costs **1**, with N = `log2(size) - 6` ≈ **10 blocks at the 64 KiB reference size**; therefore
  the sample's connect count alone exceeds the whole full-read step's cost. Quoting MEAS-01's
  own measured second-count as the per-connect unit is legitimate (it is a measurement, cited to
  its source); deriving new second-counts is not. — **Reversibility:** reversible.

- **D-04:** **The modelled figures are not published as findings.** The per-operation overhead
  (~0.28 s) and read rates (8.7 KB/s on `0x07`, 7.0 KB/s on `0x08`) come from
  `.planning/notes/dev-test-sequence-cost-model.md`, which states its own ceiling — *"a model built
  on one sample, not a benchmark"* — and already carries a same-day recorded **24% over-prediction
  on `0x08` parts**. Record the *size-dependence* qualitatively (the crossover lies above the
  reference parts, on an axis the measurement exposed and criterion 1 did not name), and do **not**
  print a table of modelled ≥512 KiB second-counts as if measured. The operator was offered
  exactly that table and declined it. — **Reversibility:** reversible.

- **D-05:** **The size-gated variant is not re-filed as a requirement.** The operator was offered
  "close now, re-file size-gated" as a distinct option and chose the plain close instead. Record
  the finding as evidence in the closing document; do not create a new requirement, backlog item,
  or todo for it.

### Criterion 3's discharge

- **D-06:** **Three tests, in files that already exist. No new test module.** Operator delegated
  this decision verbatim — *"You decide a simple model, i dont understand the different options"* —
  so it is Claude's call, recorded here as locked:
  1. **Behavioural leg:** the last read returning `False` yields `VERDICT_BAD`. New, beside
     `test_read_step_disagreement_is_divergence_metric_not_marginal` in
     `firestarter_app/tests/test_chip_test.py`.
  2. **Behavioural leg:** the *first* read returning `False` while the last returns `True` yields
     `VERDICT_OK`. Same file. Together (1) and (2) prove the verdict is the **last** full read's
     return value.
  3. **Structural pin:** an `ast` assertion that `_dispatch_read`'s `verdict=` expression reads only
     `last_ok` and nothing derived from the read-vs-read comparison. Added to
     `firestarter_app/tests/test_readback_inventory.py`, which already parses `chip_test.py` with
     `ast` and already holds this class of pin.

  **Why (3) earns its place:** (1) and (2) alone have a hole. If a future change swaps the second
  full read for a spot-check, "the last read" *becomes* the spot-check, and both behavioural legs
  still pass while the verdict comes from a sample — precisely the "**silently** becomes the
  sample's verdict" that criterion 3 names. Only the structural pin closes it.
  — **Reversibility:** reversible — three additive test functions, no product code touched.

- **D-07:** **Every new gate gets a planted-mutation RED proof**, per this repository's universal
  practice (`test_readback_inventory.py`'s two planted legs;
  `test_blast_radius_invariance.py`'s recorded RED transcripts). Reuse the **in-memory string
  mutation** pattern of `test_a_planted_third_call_site_reddens_the_census` — operate on strings
  only, write no fixture files. This was locked without asking because house precedent settles it.

### How permanently the close holds

- **D-08:** **Conditional close, naming R4-01 explicitly.** Operator delegated — *"You decide."*
  The entire "not worth doing" verdict is a consequence of one design fact: one connect per read.
  **R4-01** (`.planning/REQUIREMENTS.md` §Future Requirements — `EpromOperator` leasing one
  validated link per plan) would make a single connection serve a whole plan and **invert the
  arithmetic completely** — N region reads would then cost roughly one connect plus N small
  transfers. The closing document must state the verdict as resting on today's
  one-connect-per-read design and name R4-01 as the specific change that would require redoing it.
  No new requirement is filed — this is an honest condition on the close, not a deferral.
  — **Reversibility:** reversible.

- **D-09:** **Amend seed R3 in place, following Phase 177's R1 precedent.** Operator delegated.
  Two parts, and the first is not optional:
  1. The seed's frontmatter `status:` line currently reads `... R3 remains for Phase 180
     (PRUNE-08) ...`. Once this phase closes PRUNE-08 that statement is **false** and must change.
  2. R3's body currently reads as a live instruction (*"Replace the read step's second full run
     with a bit-structured sample"*). Amend it **in place**, exactly as Phase 177's amendment
     handled R1, whose stated reasoning applies unchanged here: *"this amendment replaces R1's
     paragraph in place rather than merely annotating it, so the destructive reading is not
     outvoted but absent — a planner reading only this seed can no longer regenerate it."*

  A second reason the seed is the right home: R3's own text instructs a future planner to
  *"measure a connect first and let that decide how much R4 is worth relative to R1–R3."* Phase 180
  is the phase that measured it; the answer belongs where the question was asked. Preserve the
  connect-count objection in the amended text so the design cannot be regenerated without meeting
  it. — **Reversibility:** costly — the seed is the artifact a future planner reads first; if the
  amendment is skipped or later reverted, a subsequent milestone can regenerate the rejected
  sampling design from the seed alone, with no trace of this phase's measurement.

### Claude's Discretion

The operator delegated D-06 and D-08/D-09 outright ("You decide"), and declined to open two further
areas Claude raised at the closing gate. Claude disposed of both:

- **D-10:** **Criterion 4 is Not Applicable, recorded with its reason.** Its own text is conditioned
  — *"If sampling ships, block-wise `(offset, block)` comparison is used..."* — and sampling does
  not ship. State the N/A verdict and the unmet precondition explicitly in the closing document
  rather than leaving the criterion silently unaddressed. Do **not** build a hole-padded fixture or
  a block-wise comparator to satisfy a criterion whose precondition is false.

- **D-11:** **Record `_read_region` as the primitive a future attempt would use.** A short
  forward-looking note beside D-08's R4-01 condition, so a later size-gated or post-R4-01 attempt
  does not re-derive it: `firestarter_app/firestarter/chip_test.py:2851` already provides exactly
  what R3 needs — a region read whose result is sliced at the **absolute** offset (region reads
  produce a hole-padded file whose real bytes sit at offset `start`, never at 0), returning `b""`
  rather than raising on any failure. It is also the choice that keeps Phase 177's census at
  exactly two `read_eprom` call sites, so a future sampler routed through it would not redden
  `test_readback_inventory.py`. This is a note, not a licence to implement.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### The measurement this phase spends (read first)
- `.planning/phases/176-transport-instrumentation-connect-cost-measurement-partially/176-MEASUREMENT.md`
  — MEAS-01's per-board-class per-connect cost. §4a/§4b carry the numbers (Uno 2.518 s median,
  remainder 0.018 s; Leonardo 2.607 s median, remainder 0.107 s; shared 2.500 s structural floor).
  §7 states that Phase 176 *records* the measurement and does not spend it, naming PRUNE-08 and
  R4-01 as the consumers. §6 is the validation ceiling — it explicitly **falsified** the
  Uno-dominance hypothesis and attributes no mechanism. **This is the closing evidence D-01 cites.**

### The design being closed
- `.planning/seeds/dev-test-adaptive-sequencing.md` — R3 is the rule this phase closes; §R3 carries
  the block-structure design (`1 << k` for k in `8..log2(size)`, plus block 0 and the top block).
  Its `status:` frontmatter and R3's body are both **edited by this phase** (D-09). The
  `## Status: Phase 177 amendment` section at the end is the in-place-amendment precedent to copy.
- `.planning/notes/dev-test-sequence-cost-model.md` — the primitive costs and the validated connect
  model. **Read its "Provenance of the numbers" section before quoting any figure from it**: one
  log, one Leonardo, one 64 KiB `0x07` part, with a recorded 24% over-prediction on `0x08`. D-04
  bounds what may be published from it.

### Requirements and milestone record
- `.planning/REQUIREMENTS.md` — PRUNE-08's text (line 60), MEAS-01 (line 103, already Complete),
  **R4-01 in §Future Requirements (line 122)** which D-08 names, the traceability table row
  `PRUNE-08 | Phase 180 | Pending`, and §Decisions D-1…D-8 (none of which settles PRUNE-08's
  branch; D-1 is already applied by Phase 177).
- `.planning/ROADMAP.md` §"Phase 180: Read-Step Sampling (conditional on Phase 176)" — the four
  success criteria. Also §"The one hard ordering constraint" and the "operation counts, never
  seconds" house rule that D-03 applies.
- `.planning/MILESTONES.md` — **read the first section before writing any verify block.** It
  carries three corrections aimed by name at *"a phase 180/181 plan"*: the re-key ledger protocol
  is **retired** (no ledger row is needed for this phase), the green-tree ritual is **seven** legs
  not eight (`check_rekey_ledger.py` is deleted — a plan copying 179's eight-leg version invokes a
  script that no longer exists), and the app suite floor is **2239**, not the 2242 recorded in
  179's plans.

### Prior-phase records that bound this phase
- `.planning/phases/177-evidence-gated-read-back/177-READBACK-INVENTORY.md` — row 4 of its table
  names `_dispatch_read` as *"PRUNE-08 / seed R3's territory, Phase 180"* and states the census
  reddens if a third `read_eprom` site appears. Its "PRUNE-04's closure" section is the
  *measured-empty / named-and-excluded* closing form this phase's document should mirror, and it
  states that this milestone grants PRUNE-08 the same standing.

### Project rules (non-negotiable)
- `/workspaces/CLAUDE.md` §"Source code comments — hard rule" — **no comments in product source,
  and `firestarter_app/tests/` is product source.** Phase 177 verified
  `comments_test_readback_inventory=0` as a gate. Put every rationale in **docstrings** (which are
  permitted and are how these test modules already carry their reasoning), never in `#` lines. A
  plan may not override this rule and must not make "a comment exists" an acceptance criterion.
- `/workspaces/CLAUDE.md` §"Milestone close and branch protection" — `main` is protected in all
  three repos; this project's base branch is `beta`.

</canonical_refs>

<code_context>
## Existing Code Insights

### The structural fact the whole close rests on
- **`firestarter_app/firestarter/eprom_operations.py:515-550`** — `_operation_context` calls
  `SerialCommunicator.find_and_connect(...)` via `_setup_operation` on entry and
  `self._disconnect_programmer()` in its `finally` block. **Therefore every `read_eprom` call pays
  exactly one full connect**, and an N-block sample pays N connects. This is D-02's structural
  half; the planner should pin it by test or AST rather than asserting it in prose, since it is the
  load-bearing premise of the entire closing argument.

### Reusable assets
- **`firestarter_app/firestarter/chip_test.py:2851` `_read_region`** — the region-read primitive
  (absolute-offset slice off a hole-padded file, `b""` on any failure). Referenced by D-11 as a
  forward-looking note only; **not used by this phase**.
- **`firestarter_app/tests/test_readback_inventory.py`** — already parses `chip_test.py` with `ast`,
  already resolves the module path from `chip_test.__file__` (never from the test's own directory,
  a recorded failure mode in this project), already asserts the parsed source is non-empty so the
  census cannot pass on a file it never read, and already carries a planted-mutation leg. **This is
  where D-06's structural pin goes** — the machinery is all present.
- **`firestarter_app/tests/test_chip_test.py:2141`
  `test_read_step_disagreement_is_divergence_metric_not_marginal`** — already proves criterion 3's
  *negative* half: two diverging reads yield `VERDICT_OK`, never `VERDICT_MARGINAL`, with
  `divergence["bad"] > 0` recorded. **Cite it; do not duplicate it.** Its sibling
  `test_read_step_agreement_no_divergence_recorded` (2166) covers the agreeing case. D-06's two
  behavioural legs are the *positive* half neither one covers.

### Established patterns that constrain this phase
- **`_dispatch_read` (`chip_test.py:2767`)** reads the **whole device** every run —
  `operator.read_eprom(name, eprom_data, output_file=out_path)` passes no `address_str`/`size_str`.
  Note for the researcher: the read step is whole-device even for UV parts whose *write* is a 256 B
  slot, so "device size" in D-03's N calculation is the full `electrical.size_bytes`.
- **`_dispatch_read`'s verdict** is `VERDICT_OK if last_ok else VERDICT_BAD`, where `last_ok` is the
  **last** run's return value; `divergence` is computed from `run_bytes[0]` vs `run_bytes[1]` and
  never feeds the verdict. Its docstring already asserts this in prose — D-06 is what makes it
  testable.
- **Anti-vacuity discipline** — a gate is not trusted here until it has been observed RED against a
  planted counter-example, with the transcript recorded in the phase's `evidence/` directory. D-07
  applies it.

### Integration points
- `.planning/REQUIREMENTS.md` — PRUNE-08's v1 checkbox and its traceability row are the only two
  requirement edits. **Touch no other requirement row.** Phase 177's plan verified this class of
  scope by counting rows; expect the same.
- `.planning/seeds/dev-test-adaptive-sequencing.md` — edited in place per D-09.
- No firmware change. `git -C firestarter status --porcelain` must stay clean.
- No `chip_database.json` change. It is **generated**; never hand-edit it.

### Environment notes for whoever runs the gates
- Use `firestarter_app/.venv311/bin/python` — the devcontainer's default is 3.12 and app CI runs
  **3.11 only**, a divergence that has already broken beta CI once.
- The green-tree battery is **seven** legs (per `MILESTONES.md`): `ruff check` and
  `ruff format --check` on `firestarter/ tests/`, `tools/check_mypy_watermark.py` (watermark 35),
  `tools/snapshot_report_shapes.py --check`, `tools/check_devtest_orchestrator.py`,
  `tools/check_diagnostic_report_claims.py`, and the full suite (floor **2239**).
- `grep` in this devcontainer is `ugrep` and honours `.gitignore`, silently under-scanning. Use
  `/usr/bin/grep` for any gate evidence.

</code_context>

<specifics>
## Specific Ideas

- **The arithmetic the closing document argues, in the form D-03 requires.** At the 64 KiB
  reference size the sample is N ≈ 10 blocks, so it pays **10 connects** where the full read pays
  **1**. Ten connects at MEAS-01's measured Uno figure exceed the *entire* measured full-read step
  (one connect plus its wire time) by roughly a factor of two and a half. The verdict does not
  depend on the modelled read rate at all — even a badly wrong rate leaves ten connects dearer than
  one. **Lead with that robustness**, because it is what makes the close honest under D-02's
  evidence standard.

- **The axis finding, stated without modelled numbers (D-04).** Criterion 1 named board class; the
  measurement showed the two classes 0.09 s apart and therefore non-discriminating. The axis that
  does discriminate is device size, because N grows with `log2(size)` while the full read's wire
  cost grows linearly — so a crossover exists, and it lies **above** every reference part this
  milestone tests. Record that shape as the finding. The corpus context is factual and may be
  quoted: of 746 database rows, 484 are ≤128 KiB, 148 are 256 KiB, and 114 are ≥512 KiB, all
  `supported`.

- **Mirror Phase 177's closing form.** `177-READBACK-INVENTORY.md`'s "PRUNE-04's closure" section is
  the house style for exactly this move: state the verdict, name the excluded thing, give the
  reason, and say what the gate is that would redden if the situation changed. It also records that
  this milestone grants PRUNE-08 the same standing, which makes it the natural template.

</specifics>

<deferred>
## Deferred Ideas

- **Size-gated sampling for parts ≥512 KiB.** The arithmetic suggests a real win on 114 supported
  database rows. The operator was offered this as both a ship option and a re-file option and
  **declined both** (D-01, D-05). It is recorded as evidence inside this phase's closing document
  and is **deliberately not** a requirement, backlog item, or todo. A future milestone that wants
  it starts from the closing document and D-11's `_read_region` note.
- **R4-01 — `EpromOperator` leasing one validated link per plan.** Already filed in
  `.planning/REQUIREMENTS.md` §Future Requirements. Phase 180 adds nothing to it and only names it
  as the change that would invalidate this close (D-08). MEAS-01 was also meant to gate whether
  R4-01 is worth scoping; **Phase 180 does not make that call either** — the roadmap gives Phase 180
  PRUNE-08 only.

### Reviewed Todos (not folded)
`todo.match-phase 180` returned **41 matches, all keyword artefacts** — none is within a
single-requirement documentary close. None folded. The highest-scoring, recorded so a future phase
knows they were considered and rejected here:
- *Strip residual GSD provenance comments from product source* (0.9) — matched on "source"/"phase".
  A repo-wide comment sweep, unrelated to PRUNE-08. Note the standing rule it encodes **does**
  apply to this phase's new tests (see canonical refs).
- *Remove the CMD_VERIFY command surface from firmware* (0.7) — matched on "read"/"compare". A
  firmware surface change; touches neither the read step nor PRUNE-08.
- *Write-init blank check scans the whole device* (0.6) — matched on "whole"/"device". A UV
  write-path defect; Phase 179's territory, not the read step's.
- *Skip VPP error/warning checks when VPP is unused on reads* (0.6) — matched on "reads". Firmware
  voltage-check logic, unrelated to read repeatability.

</deferred>

---

*Phase: 180-read-step-sampling-conditional-on-phase-176*
*Context gathered: 2026-09-08*
