# Phase 180: Read-Step Sampling (conditional on Phase 176) - Research

**Researched:** 2026-09-08
**Domain:** Documentary requirement close + three additive test pins (no product behaviour change)
**Confidence:** HIGH — every load-bearing citation was opened and re-measured this session

## Summary

This was a **verification pass, not a design pass**. CONTEXT.md's decisions are locked (D-01 takes
roadmap criterion 2: PRUNE-08 closes as *measured, not worth doing*; zero sampling code ships), so
the highest-value work was confirming that every citation the closing argument is about to freeze
into acceptance criteria is still true. **Nearly all of them are.** The measurement figures, the
structural premise, the `_dispatch_read` verdict expression, the sibling tests, the AST machinery,
the seed's frontmatter and R3 body, the requirement line numbers, and the seven-leg gate battery
all check out — several of them to the exact line.

Beyond confirming, this pass **proved three things by execution rather than by reading**: the two
D-06 behavioural legs actually hold through the real `run_plan` path (Phase 178's status axis does
*not* intercept a `False` read); D-06 leg 3's AST pin is feasible, has a unique anchor, and reddens
against a planted divergence-fed verdict; and the green tree measures **exactly 2239** with all
seven legs green.

**Seven corrections are reported below.** Two are material to what the closing document may claim
(C-1 the `all supported` over-claim, C-6 the factor-of-2.5 provenance), one is a live trap the
plan must defuse (C-3 the comment gate is blind to trailing comments — and the very test the
planner is told to copy carries two), and one is a scope tension only the planner can resolve
(C-7).

**Primary recommendation:** Plan four deliverables exactly as CONTEXT.md scopes them, take the
model-free connect-count form (10 vs 1) as the load-bearing argument, drop the word "all" from the
corpus sentence, and add a `tokenize`-based comment delta gate because the inherited regex one
cannot see the failure mode this phase is most likely to commit.

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

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

### Deferred Ideas (OUT OF SCOPE)

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
- **Any sampling implementation** — no bit-structured sampler, no block list, no `1 << k` boundary
  computation, no escalate-on-divergence path.
- **Any change to `_dispatch_read`'s behaviour**; any bench/hardware work; R4-01 implementation;
  any new requirement for size-gated sampling.

</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| PRUNE-08 | *"The read step's second full sweep is replaced by a bit-structured sample **only if** MEAS-01 shows the sample is cheaper on the measured board class. If it is not, this requirement closes as measured, not worth doing, with the measurement recorded — that is a success, not a miss."* [VERIFIED: .planning/REQUIREMENTS.md:60] | Closes via roadmap criterion 2. The measurement is verified verbatim in §Measurement Verification; the structural premise in §Structural Premise; the connect arithmetic in §The Arithmetic; criterion 3's three test pins in §D-06 Test Design (all three proven executable this session); criterion 4's N/A precondition in §Criterion 4. |

</phase_requirements>

---

## CORRECTIONS — read these first

This project has a standing rule against silently absorbing a measured disagreement, and a standing
rule that stale `.planning/` `file:LINE` citations are repaired rather than accepted. Seven items did
not check out exactly as written.

### C-1 (MATERIAL) — "all `supported`" is an over-claim

CONTEXT.md `<specifics>` authorises quoting: *"of 746 database rows, 484 are ≤128 KiB, 148 are
256 KiB, and 114 are ≥512 KiB, all `supported`."*

**The three counts are exact and the partition is exhaustive** (484 + 148 + 114 = 746 — there are no
chips strictly between 128 KiB and 256 KiB, nor between 256 KiB and 512 KiB).
**"all `supported`" is false.** [VERIFIED: measured this session against
`firestarter_app/firestarter/data/chip_database.json`, 59 vendors / 746 rows]

| Bucket | Rows | `supported` | Other |
|---|---|---|---|
| ≤128 KiB | 484 | **474** | 9 `adapter-required`, 1 `protocol-not-implemented` |
| ==256 KiB | 148 | **148** | — |
| ≥512 KiB | 114 | **114** | — |
| **total** | **746** | **736** | **10** |

All 10 non-supported rows are ≤8 KiB (`AT28C04`, `AT28C16`, `28C04A`, `28C16A`, `UPD28C04` family —
`adapter-required`; `X88C64P,X88C64S` — `protocol-not-implemented`), so they sit entirely inside the
≤128 KiB bucket.

**Consequence for the plan:** the *load-bearing* half of the sentence survives intact — the size-axis
finding rests on **114 rows ≥512 KiB, and those are all `supported`** (114/114), as are the 148 at
256 KiB. Only the blanket "all" across the whole 746 is wrong. **Write the sentence as: "of 746
database rows, 484 are ≤128 KiB, 148 are 256 KiB and 114 are ≥512 KiB; every row at 256 KiB and above
is `supported`."** This matters more than usual here: `support_status` honesty is a named binding
constraint inherited from v1.35/999.12 (*"Relocation must not upgrade a claim"*), and an over-claim in
a closing document is exactly the failure mode this milestone exists to catch.

### C-2 (CONFIRMED STALE, as MILESTONES.md warned) — eight legs and the 2242 floor

Both stale citations are real and both would break a plan that copied them.

- `179-PATTERNS.md:453` (§"Phase-seal gate set") reads: *"Eight `rc=0` legs — ruff check, ruff format,
  mypy watermark, `snapshot_report_shapes.py --check`, `check_devtest_orchestrator.py`,
  `check_diagnostic_report_claims.py`, `check_rekey_ledger.py` (from `/workspaces`), full suite."*
  [VERIFIED: .planning/phases/179-uv-slot-writes-flag-skip-blank-check-hardware-gated/179-PATTERNS.md:453]
  It also states a `full_suite_passed >= 2241` floor.
- `179-02-PLAN.md:39` reads: *"the full suite floor is `>= 2242` … and `tools/rekey/check_rekey_ledger.py`
  prints `OK: 8 ledger row(s), 8 MILESTONES.md row(s) bound`."*
  [VERIFIED: .planning/phases/179-uv-slot-writes-flag-skip-blank-check-hardware-gated/179-02-PLAN.md:39]

**`tools/rekey/check_rekey_ledger.py` is definitively gone.** `find /workspaces -name "check_rekey_ledger*"`
returns **nothing**; `/workspaces/tools/rekey/` does not exist; `/workspaces/tools/` contains only
`catalog` and `wiki`. [VERIFIED: filesystem, this session]

**The floor is 2239, now confirmed by measurement, not just by MILESTONES.md's assertion** — see
§Gate Battery.

### C-3 (LIVE TRAP — new finding) — the comment gate cannot see trailing comments, and the test you are told to copy has two

The inherited `phase_added_comments=0` gate [VERIFIED:
.planning/phases/179-uv-slot-writes-flag-skip-blank-check-hardware-gated/179-PATTERNS.md:449] ends in
`/usr/bin/grep -cE '^\+[[:space:]]*#'` — it counts only added lines whose **first non-space character**
is `#`. A trailing comment on a code line is invisible to it. Proven by construction this session: a
simulated diff containing one trailing comment and one full-line comment returns a count of **1**.

This is not hypothetical. `test_read_step_disagreement_is_divergence_metric_not_marginal` — the exact
sibling D-06 leg 1 is told to sit beside — carries **four** comments, two of them trailing:

```
2143:    # Two runs of read_eprom write DIFFERENT bytes to output_file --
2144:    # byte-level divergence, never a verdict flip, never marginal (D-06).
2160:    assert read_result.verdict == VERDICT_OK  # never a verdict flip
2161:    assert read_result.verdict != VERDICT_MARGINAL  # never marginal (D-06)
```
[VERIFIED: firestarter_app/tests/test_chip_test.py:2143-2144, 2160-2161]

Two of them cite `(D-06)` — a GSD decision identifier in product source, precisely what
`/workspaces/CLAUDE.md` and `firestarter_app/CLAUDE.md` forbid. **These are pre-existing and must not
be "fixed"** (out of scope, and touching them widens the diff), **but they must not be copied either** —
and an executor copying the sibling's style verbatim would violate the hard rule while the gate reads
green. See §Comment Discipline for the corrected gate.

### C-4 (MINOR, but the closing document restates it) — seed R3's block range is internally inconsistent

Seed R3 says: *"one 256 B block at each `1 << k` boundary for `k` in `8..log2(size)`, plus block 0 and
the top block. For a 64 KiB part that is 10 blocks / 2560 B"*
[VERIFIED: .planning/seeds/dev-test-adaptive-sequencing.md:75-77].

Read inclusively, `k` in `8..16` for a 64 KiB part gives 9 boundaries, and `1 << 16 == 65536` is the
device size itself — one past the end. 9 + block 0 + top block = **11**, contradicting the seed's own
"10 blocks / 2560 B". The self-consistent reading is **boundaries strictly inside the device**
(`k` in `8..log2(size)-1`), which yields exactly 10. [VERIFIED: enumerated this session]

**D-03's formula is correct and is the one to use.** Nothing needs re-deciding — but the closing
document should state the block list by its *enumeration*, not by re-quoting the loose range notation.
See §The Arithmetic.

### C-5 (ARCHIVED-BY-INTENT) — `177-READBACK-INVENTORY.md` row 4's line number is stale

Row 4 cites `chip_test.py:2642` for `_dispatch_read`; the current definition is at **2767**.
[VERIFIED: firestarter_app/firestarter/chip_test.py:2767]. Rows 1/2/3 similarly cite `:3108`, `:3338`,
`:2843`, and `_read_region` is now at **2851**.

Per MILESTONES.md's own ruling, archived phase records are *"deliberately left unedited"* and a
`.planning`→`.planning` citation is historical by intent. **No repair is asked for.** The point is
narrower: the planner must cite **2767 / 2851** (CONTEXT.md already does, correctly) and must not
inherit 177's numbers when quoting that inventory as the closing-form precedent.

### C-6 (MATERIAL — provenance) — the "factor of two and a half" is not model-free

CONTEXT.md `<specifics>` says: *"Ten connects at MEAS-01's measured Uno figure exceed the entire
measured full-read step (one connect plus its wire time) by roughly a factor of two and a half."*

The **factor reproduces** — 2.51× on Uno, 2.58× on Leonardo [VERIFIED: computed this session] — but only
by supplying the full read's wire time from the **modelled** 7.51 s / 8.7 KB/s figure in
`dev-test-sequence-cost-model.md`, which D-04 explicitly bounds (*"a model built on one sample, not a
benchmark"*, with a recorded ~24% over-prediction on `0x08`). Calling that step "the entire **measured**
full-read step" overstates it: the connect half is measured, the wire half is modelled.

**This is exactly why `<specifics>` also says "Lead with that robustness"** — and the robust form really
is robust. See §The Arithmetic for the model-free statement, which needs no wire time at all. Present
the 2.5× as a secondary illustration explicitly labelled as resting on a modelled read rate, or omit it.

### C-7 (SCOPE TENSION — planner must resolve) — is the one-connect pin a fourth artifact?

`<domain>` scopes **exactly four deliverables** and D-06 locks **exactly three tests**. But
`<code_context>` says of the one-connect-per-read premise: *"the planner should pin it by test or AST
rather than asserting it in prose, since it is the load-bearing premise of the entire closing
argument."* That pin is neither one of D-06's three tests (all of which are about
`_dispatch_read`'s verdict, not about `_operation_context`) nor one of the four deliverables.

This is a genuine gap between two parts of CONTEXT.md, not an error in either. §Structural Premise
gives the planner a ready-made, non-vacuous pin and states honestly what it can and cannot assert, so
the decision is cheap either way. **Recommendation: include it**, as a fourth additive test in
`test_readback_inventory.py` (same module, same machinery, ~12 lines) — the premise is load-bearing
enough that prose alone is the weakest link in the close, and D-02 names it as one of only two
load-bearing facts. Flag it as a `checkpoint:decision` if the planner prefers the operator to rule.

---

## Measurement Verification (§4a/§4b/§6/§7 confirmed verbatim)

Every figure CONTEXT.md quotes from
`.planning/phases/176-transport-instrumentation-connect-cost-measurement-partially/176-MEASUREMENT.md`
is present and exact. The document is 328 lines; the relevant sections are numbered as CONTEXT.md says.

**§4a — Uno-class (512 B `firmware_max_chunk`, port `/dev/ttyACM1`)**, quoted verbatim
[VERIFIED: 176-MEASUREMENT.md:219-234]:

| Figure | Value |
|---|---|
| Samples collected | 10 |
| Min | 2.517s |
| Median (`statistics.median_low`) | 2.518s |
| Max | 2.519s |
| Structural floor (board-independent) | 2.500s |
| Remainder (median − floor) | 0.018s |
| `probe_timeouts` observed during run | 0 |

**§4b — Leonardo-class (1024 B `firmware_max_chunk`, port `/dev/ttyACM0`)**, quoted verbatim
[VERIFIED: 176-MEASUREMENT.md:236-250]:

| Figure | Value |
|---|---|
| Samples collected | 10 |
| Min | 2.606s |
| Median (`statistics.median_low`) | 2.607s |
| Max | 2.676s |
| Structural floor (board-independent) | 2.500s |
| Remainder (median − floor) | 0.107s |
| `probe_timeouts` observed during run | 0 |

**All four of CONTEXT.md's figures confirmed:** Uno 2.518 s median / 0.018 s remainder; Leonardo
2.607 s median / 0.107 s remainder; shared 2.500 s structural floor. The two classes are **0.089 s
apart** on median — CONTEXT.md's "0.09 s apart" is right.

**A never-blend rule the closing document must honour** [VERIFIED: 176-MEASUREMENT.md:228-231]:
> "**These two per-board-class figures are never blended, and no single per-connect cost number that
> combines both board classes exists or should be quoted anywhere in this document.**"

The closing document must likewise never average 2.518 and 2.607. State each branch of the argument
per board class, or state it in connect counts (which is board-independent and is what D-03 asks for).

**§6 — the validation ceiling.** CONTEXT.md's characterisation is accurate and the section is
stronger than CONTEXT.md's one-line summary suggests. It **falsifies the Uno-dominance hypothesis**
[VERIFIED: 176-MEASUREMENT.md:277-279]:
> "**What §4's data actually shows: the opposite of the stated Uno-dominance hypothesis.** The
> Uno-class remainder (0.018s) is smaller than the Leonardo-class remainder (0.107s), not larger."

and **attributes no mechanism** [VERIFIED: 176-MEASUREMENT.md:284-287]:
> "Neither hypothesis's underlying *mechanism* (DTR assertion, optiboot entry, USB re-enumeration) is
> directly observed anywhere in this document; only the aggregate wall-clock duration is."

It also records that the measurement *cannot distinguish* "no bootloader wait occurred" from "a
bootloader wait occurred and was fully absorbed by the floor." **The closing document may cite §6 as
the reason board class is a non-discriminator, but must not claim to know why.**

**§7 — downstream consumers.** Confirmed to name both PRUNE-08 and R4-01 exactly as CONTEXT.md says
[VERIFIED: 176-MEASUREMENT.md:300-306]:
> "**PRUNE-08 (Phase 180)** consumes MEAS-01's number. This phase records the measurement; it does not
> spend it — no scoping decision for PRUNE-08 is made here."
> "**The R4-01 deferral** … is not acted on here either. Both remainders (0.018s and 0.107s) are small
> relative to the 2.5s floor, which is itself unchanged by this measurement — that observation is left
> for PRUNE-08/R4-01 to weigh, not decided in this document."

That last sentence is a direct hand-off to this phase, and D-08's "conditional close naming R4-01" is
exactly the shape §7 anticipates. **Cite §7 as the licence to spend the measurement.**

**One caution.** §7's phrasing — *"both remainders are small relative to the 2.5s floor"* — is about
the *remainders*, not the connect cost. The connect cost that matters to PRUNE-08 is the **whole**
2.518 s / 2.607 s, floor included, because a sampler pays the entire connect N times, floor and all.
Do not let §7's "small" leak into the closing argument as though connects were cheap.

---

## Structural Premise — one `read_eprom` call == exactly one full connect

**CONTEXT.md's citation `eprom_operations.py:515-550` is exact to the line.** [VERIFIED:
firestarter_app/firestarter/eprom_operations.py:515-550]

| Element | Line | Verbatim |
|---|---|---|
| `def _operation_context(` | **515** | `    def _operation_context(` |
| `_setup_operation(` call | **531** | `        command_dict, buffer_size = self._setup_operation(` |
| `try:` | **545** | `        try:` |
| `yield` | **547** | `            yield command_dict, buffer_size, operation_name` |
| `finally:` | **548** | `        finally:` |
| `self._disconnect_programmer()` | **550** | `            self._disconnect_programmer()` |
| `def _disconnect_programmer` | 552 | `    def _disconnect_programmer(self):` |
| `find_and_connect` (inside `_setup_operation`) | **499** | `            self.comm = SerialCommunicator.find_and_connect(` |
| `def _setup_operation` | 454 | — |

So the chain is: `_operation_context` (515) → `_setup_operation` (531, defined 454) →
`SerialCommunicator.find_and_connect` (499) on entry; `finally:` (548) → `_disconnect_programmer` (550,
defined 552) on exit, which does `self.comm.disconnect(); self.comm = None`.

**And `read_eprom` uses it exactly once.** [VERIFIED: firestarter_app/firestarter/eprom_operations.py:896-943]
`def read_eprom(` is at **896**; its entire body is a single `with self._operation_context(...)` opened
at **905**. There is no loop, no second context, no early re-entry. Its signature already accepts
`address_str` / `size_str` (lines 902-903) — which is precisely what makes an N-block sampler a
sequence of N separate `read_eprom` calls, hence **N connects**.

**Therefore: one `read_eprom` call == exactly one full connect. Premise VERIFIED.**

### What an honest, non-vacuous pin would have to assert

A pin that merely greps for the strings `find_and_connect` and `_disconnect_programmer` would fail
open on a rename and prove nothing. An honest pin must assert **structure**, and it must be explicit
about its ceiling. Concretely it should assert all three of:

1. **`read_eprom`'s body contains exactly one `with self._operation_context(...)`** — an `ast` count of
   `ast.With` items whose `context_expr` is a `Call` on `Attribute(attr="_operation_context")` inside
   the `read_eprom` `FunctionDef`. This is the claim that carries the arithmetic.
2. **`_operation_context` connects on entry** — an `ast` assertion that its body calls
   `_setup_operation`, and that `_setup_operation`'s body calls `find_and_connect`.
3. **`_operation_context` disconnects unconditionally** — an `ast` assertion that it has a `Try` node
   with a non-empty `finalbody`, and that `_disconnect_programmer` is called *within that finalbody*
   (not merely somewhere in the function). Asserting the call site is inside `finalbody` is what makes
   it "unconditionally", and is the difference between a real pin and a decorative one.

**Its honest ceiling, which the docstring should state:** this is a *static* pin. It proves the code
is shaped so one call opens one context that connects and disconnects; it does **not** prove at runtime
that exactly one TCP/serial open occurred, and it says nothing about `find_and_connect`'s internal
retry-across-ports walk. That ceiling is fine for the closing argument — the argument needs "N region
reads cost N connects, not 1", which is a statement about *shape*.

**No existing test covers this.** [VERIFIED: searched `firestarter_app/tests/`] `test_readback_inventory.py`
censuses `operator.read_eprom` **call sites in `chip_test.py`** — a different claim (how many places
call it), not what one call costs. The nearest neighbour is
`test_verify_eprom_signature_names_the_replacement_primitive` (:123), which pins an `EpromOperator`
signature by `inspect` — precedent that this module legitimately reaches into `eprom_operations`, and
it already imports `EpromOperator` at :40. **The pin belongs in `test_readback_inventory.py`**, reusing
its existing imports. See C-7 for whether to include it at all.

---

## The Arithmetic (D-03's form, verified and derived)

### N = log2(size) − 6, confirmed against the seed's own block structure

Enumerating the seed's structure — block 0, one 256 B block at each `1 << k` boundary strictly inside
the device, and the top block — reproduces the seed's own stated answer exactly.

**At the 64 KiB reference size**, the block list is 10 blocks / 2560 B [VERIFIED: enumerated this
session; matches .planning/seeds/dev-test-adaptive-sequencing.md:77 *"For a 64 KiB part that is 10
blocks / 2560 B"*]:

```
0x0000  0x0100  0x0200  0x0400  0x0800  0x1000  0x2000  0x4000  0x8000  0xFF00
  ^block 0        ^--------- 1<<k for k in 8..15 ---------^          ^top block
```

That is `(log2(65536) − 8)` interior boundaries `+ 1` (block 0) `+ 1` (top block)
`= 8 + 2 = 10 = log2(size) − 6`. **D-03's N = 10 is correct and falls straight out of the block list.**

Generalising [VERIFIED: enumerated this session]:

| Size | log2 | Block list length | `log2 − 6` | Sample bytes |
|---|---|---|---|---|
| 2 KiB | 11 | 5 | 5 | 1280 |
| 32 KiB | 15 | 9 | 9 | 2304 |
| **64 KiB** | **16** | **10** | **10** | **2560** |
| 128 KiB | 17 | 11 | 11 | 2816 |
| 256 KiB | 18 | 12 | 12 | 3072 |
| 512 KiB | 19 | 13 | 13 | 3328 |

**Write the block list, not the range notation** — see C-4.

### The reference parts really are all 64 KiB

[VERIFIED: `firestarter_app/firestarter/data/chip_database.json`, measured this session]

| Part | Vendor | Size | log2 | N | `support_status` |
|---|---|---|---|---|---|
| SST27SF512 | SST | 65536 B (64 KiB) | 16 | **10** | `supported` |
| W27C512 | WINBOND | 65536 B (64 KiB) | 16 | **10** | `supported` |
| M27C512 | ST *and* SGS-THOMSON | 65536 B (64 KiB) | 16 | **10** | `supported` |

D-01's *"sst27sf512, w27c512, m27c512 — all 64 KiB"* is **exact**. (For context: AT28C256 and W27E257
are 32 KiB → N=9; AM27C020 is 256 KiB → N=12.)

### The statement to write — model-free form (lead with this)

> The read step performs two full device reads. Replacing the **second** of them with the
> bit-structured sample substitutes **N = log2(size) − 6 = 10** whole `read_eprom` calls for **1**.
> Because `EpromOperator._operation_context` connects on entry and disconnects in its `finally`
> block, each of those calls pays one full connect. The sample therefore costs **10 connects where
> the sweep it replaces costs 1** — a net **+9 connects per read step** — before a single byte of its
> 2560 B is transferred.

This needs **no read rate, no wire time, and no second-count at all**. It is immune to D-04's model
ceiling and to the 24% `0x08` over-prediction, and it is stated in operation counts exactly as the
milestone's house rule requires. **This is the load-bearing sentence of the whole close.**

Adding MEAS-01's measured per-connect cost as the unit is legitimate (D-03 permits it — it is a
measurement, cited to its source), stated per board class and never blended:

> Ten connects is **25.18 s on the measured Uno-class board** (10 × 2.518 s) and **26.07 s on the
> measured Leonardo-class board** (10 × 2.607 s) — spent purely on connection overhead, on both
> classes, for a sample that reads 2560 B.

### The 2.5× figure — use with a stated caveat, or omit

2.51× (Uno) and 2.58× (Leonardo) both reproduce, but only via the modelled 7.51 s read. See **C-6**.
If used: *"roughly two and a half times the whole full-read step, taking the step's wire time from the
cost model's modelled 8.7 KB/s `0x07` figure — a modelled number, not a measured one."*

### The size axis, stated without modelled numbers (D-04)

The shape is: **N grows with `log2(size)` while the full read's wire cost grows linearly with `size`.**
Ten connects buys a fixed 2560 B at 64 KiB; at 512 KiB it is thirteen connects for 3328 B against a
device eight times larger. A crossover therefore exists, and it lies **above every reference part this
milestone tests**. Corpus context (per C-1's corrected wording): 484 of 746 rows are ≤128 KiB, 148 are
256 KiB and 114 are ≥512 KiB, and **every row at 256 KiB and above is `supported`**. Record that shape;
print no modelled ≥512 KiB second-count table.

---

## D-06 Test Design — all three legs verified executable

### `_dispatch_read` as it stands today

[VERIFIED: firestarter_app/firestarter/chip_test.py:2767-2812]

- `def _dispatch_read(` at **2767** — CONTEXT.md's citation is exact.
- `last_ok = True` initialised at **2778**.
- `last_ok = operator.read_eprom(name, eprom_data, output_file=out_path)` at **2783**, inside
  `for i in range(runs)`. **No `address_str` / `size_str`** → whole device every run, as CONTEXT.md says.
  `last_ok` is rebound each iteration, so it holds the **last** run's return value.
- `divergence` computed at **2789-2803** from `run_bytes[0]` vs `run_bytes[1]`, guarded by
  `if len(run_bytes) >= 2 and any(run_bytes)`.
- The verdict, verbatim at **2808**: `        verdict=VERDICT_OK if last_ok else VERDICT_BAD,`

**CONTEXT.md's claim confirmed exactly**: the verdict is `VERDICT_OK if last_ok else VERDICT_BAD`,
`last_ok` is the last run's return value, and `divergence` never feeds it. The docstring already
asserts this in prose [VERIFIED: chip_test.py:2770-2776]:
> "The step's own verdict is OK/BAD from the LAST run's return value -- disagreement across runs does
> not change it."

Also confirmed: exactly **two** `operator.read_eprom` call sites in `chip_test.py` (2783 in
`_dispatch_read`, 2869 in `_read_region`) — Phase 177's census is intact and these tests must not
disturb it. And `_read_region` is at **2851**, matching D-11.

### Legs 1 and 2 — PROVEN to hold through the real `run_plan`

This was the one place a locked decision could have been wrong: Phase 178 added a status axis, and if
it intercepted a `False` read, leg 1 would fail through `run_plan` and would have to call
`_dispatch_read` directly. **It does not.** Executed this session against `firestarter_app @ ffb0060`
in `.venv311`:

```
OK LEG1  last read False  (True, False)         -> verdict='BAD'  expected='BAD'  run_count=2 calls=2
OK LEG2  first False last True (False, True)    -> verdict='OK'   expected='OK'   run_count=2 calls=2
OK ctl   both True                              -> verdict='OK'   expected='OK'   run_count=2 calls=2
OK ctl   both False                             -> verdict='BAD'  expected='BAD'  run_count=2 calls=2
```

The reason is structural: `run_plan`'s dispatcher returns `_dispatch_read(...)` directly for `OP_READ`
[VERIFIED: chip_test.py:2683-2684] with no post-processing, and ATTR-02's transport arm keys on
`(SerialError, HardwareOperationError)` **exceptions**, not on a `False` return. **Both legs can be
written against `run_plan`, matching the siblings' style.**

### The exact fixture pattern the new siblings must follow

The two existing tests are at **2141** and **2166** — both CONTEXT.md citations exact.
[VERIFIED: firestarter_app/tests/test_chip_test.py:2141, 2166]

Shared shape, in order:
1. `operator = _mock_operator()` — `Mock(spec=_OPERATOR_METHODS)` with every operator method preset to
   a success return; `read_eprom.return_value = True` by default [:1019-1032]. **To drive a `False`
   return you must set `side_effect`**, since `return_value` alone cannot vary per call.
2. Install a `read_eprom` side effect. Two precedents:
   - `_writes_bytes_to_output_file(data)` [:1428] — a helper returning a side effect that writes `data`
     at the absolute offset and **always returns `True`**. Used by the agreement test. *Not usable as-is
     for legs 1/2*, because it hard-codes `return True`.
   - The inline closure in the disagreement test [:2145-2153] — a `call_results` list plus a
     `call_count = {"n": 0}` counter dict, writing bytes to `output_file` and returning `True`.
     **This is the pattern to adapt**: keep the counter-dict idiom, but make the *return value* the
     per-call variable instead of (or as well as) the bytes.
   - Signature the side effect must accept: `(_name, _eprom_data, output_file=None, **_kwargs)`.
     Write bytes to `output_file` when truthy — a leg that writes no file leaves `run_bytes` empty and
     silently changes what is being tested.
3. `plan = _plan_with_steps(Step(op=OP_READ, supported=True, reason=""))` [:1103 →
   `Plan(name="M8720", steps=list(steps))`].
4. `results = run_plan(plan, operator, _REAL_DB, runs=2)` — `_REAL_DB = EpromDatabase(skip_local_override=True)` [:307].
5. `read_result = _result(results, OP_READ)` [:1107 — linear scan, raises `AssertionError` if absent].
6. Assert on `read_result.verdict`, `.divergence`, `.run_count`.

**Naming convention:** flat module-level `def test_<subject>_<claim>()`, no class, no fixtures, no
parametrize. Names are long and assert the claim, e.g.
`test_read_step_verdict_is_the_last_full_read_not_the_first`. Suggested pair:
`test_read_step_last_run_failure_yields_bad` and
`test_read_step_first_run_failure_with_passing_last_run_yields_ok`.

**Placement:** immediately after `test_read_step_agreement_no_divergence_recorded` (ends :2172), before
`test_write_step_attaches_fingerprint_with_region_start_addr_base` (:2177).

**Do not duplicate the existing tests** — CONTEXT.md is explicit that the disagreement test already
covers criterion 3's negative half. Cite it, do not re-assert it.

### Leg 3 — the AST pin, PROVEN feasible and PROVEN non-vacuous

`test_readback_inventory.py` [VERIFIED: 139 lines, read in full this session] has everything needed.
The machinery to reuse, exactly:

- **Module path resolution** [:95-98] — never from the test's own directory:
  ```python
  def _engine_source() -> str:
      source = pathlib.Path(ct.__file__).read_text(encoding="utf-8")
      assert len(source) > 1000
      return source
  ```
  The `assert len(source) > 1000` is the **non-empty guard** CONTEXT.md refers to: "the census cannot
  pass on a file it never read." Reuse `_engine_source()` verbatim; do not write a second resolver.
- **Imports already present** [:33-40]: `ast`, `inspect`, `pathlib`, `pytest`,
  `from firestarter import chip_test as ct`, `from firestarter.eprom_operations import EpromOperator`.
  The new pin needs **no new import**.
- **Planted-mutation idiom** [:109-115], the one D-07 says to copy:
  ```python
  def test_a_planted_third_call_site_reddens_the_census():
      source = _engine_source()
      assert source.count(_PLANTED_ANCHOR) == 1
      mutated = source.replace(_PLANTED_ANCHOR, _PLANTED_ANCHOR + _PLANTED_ANCHOR, 1)
      count, enclosing = _read_eprom_census(mutated)
      assert count == 3
      assert enclosing == {"_dispatch_read", "_read_region"}
  ```
  Three load-bearing details: the anchor's **uniqueness is asserted first** (`count(...) == 1`) so the
  mutation cannot silently no-op; `replace(..., 1)` bounds the mutation; and everything is **strings in
  memory** — no file is written.

**Feasibility and the discriminating proof, both executed this session:**

```
anchor occurrences in chip_test.py: 1
HEAD      : ['VERDICT_BAD', 'VERDICT_OK', 'last_ok']
PLANTED   : ['VERDICT_BAD', 'VERDICT_OK', 'divergence', 'last_ok']

pin at HEAD    -> GREEN
pin at PLANTED -> RED  <-- gate discriminates
```

- The `verdict=` keyword resolves to a single `ast.IfExp`, unparsing to
  `VERDICT_OK if last_ok else VERDICT_BAD`, referencing exactly `{VERDICT_BAD, VERDICT_OK, last_ok}`.
- There is exactly **one** `StepResult(...)` call in `_dispatch_read`, so extraction is unambiguous.
- The planted anchor `        verdict=VERDICT_OK if last_ok else VERDICT_BAD,\n` occurs **exactly once**
  in the whole of `chip_test.py` — the uniqueness assertion will hold.
- The planted mutant `... if last_ok and not divergence else ...` is the *literal* failure mode
  criterion 3 names (the verdict silently picking up the comparison), and the pin reddens on it.

**Extraction skeleton** (verified to run):
```python
tree = ast.parse(source)
fn = next(n for n in ast.walk(tree)
          if isinstance(n, ast.FunctionDef) and n.name == "_dispatch_read")
call = next(c for c in ast.walk(fn) if isinstance(c, ast.Call)
            and isinstance(c.func, ast.Name) and c.func.id == "StepResult")
kw = next(k for k in call.keywords if k.arg == "verdict")
names = sorted({n.id for n in ast.walk(kw.value) if isinstance(n, ast.Name)})
assert names == ["VERDICT_BAD", "VERDICT_OK", "last_ok"]
```

**Design note — assert the whole name set, not just "`last_ok` is present".** A pin that only checked
`"last_ok" in names` would stay green on the planted mutant, because `last_ok` is still there. The
equality against the full sorted list is what makes it discriminating. Equivalently (and slightly more
robust to a `VERDICT_*` rename) assert that `names` contains **no** name bound from the comparison
block — `{"divergence", "run_bytes", "shas", "diverged", "diff_offsets", "cmp_len", "pct", "first"}`.
Prefer the exact-set form; it is simpler and matches the module's existing style of asserting whole
sets (`enclosing == {...}`, `params == [...]`).

**Add a third anti-vacuity leg** matching `test_an_empty_enclosing_allow_list_fails_rather_than_passing_vacuously`
[:118-120] if the planner wants full parity with the module's existing discipline.

---

## Comment Discipline (binding — and the inherited gate is insufficient)

`/workspaces/CLAUDE.md` §"Source code comments — hard rule" and `firestarter_app/CLAUDE.md`:5-21 both
apply, and `firestarter_app/tests/` is product source. Verbatim from the package rule:

> "**Write no comments into this package.** Not GSD process commentary, not explanatory ones. This is
> not overridable by a plan, task, skill, or subagent instruction."
> "Forbidden: `# Phase NNN (REQ-NN):`, `# D-06`, `# LOCK-04`, plan/task/milestone citations…"
> "**Docstrings are not comments** … Never put process commentary in one, and never delete one as if
> it were a comment."
[VERIFIED: firestarter_app/CLAUDE.md:7-21]

**The model to copy is `test_readback_inventory.py`: 0 comments, 4 docstrings** [VERIFIED: measured this
session]. Its module docstring carries several paragraphs of rationale — including the anti-vacuity
argument and the "resolved from `chip_test.__file__`, never from this test file's own directory"
reasoning — entirely in docstring prose. That is how these modules already carry their reasoning.

**Do not copy the sibling's comment style** — see C-3.

### Corrected gate (recommended)

An absolute "zero comments" assertion is impossible for `tests/test_chip_test.py`, which carries **621**
pre-existing comments (`firestarter/chip_test.py` carries 924) [VERIFIED: `tokenize` count, this
session]. The honest form is a **delta gate against a pinned pre-phase baseline**, using `tokenize`
rather than regex so trailing comments are counted:

```bash
cd /workspaces/firestarter_app && ./.venv311/bin/python - <<'PY'
import io, tokenize
BASELINE = {                                   # measured at app HEAD ffb0060, 2026-09-08
    "tests/test_chip_test.py": 621,
    "tests/test_readback_inventory.py": 0,
}
bad = 0
for path, expected in BASELINE.items():
    src = open(path, encoding="utf-8").read()
    n = sum(1 for t in tokenize.generate_tokens(io.StringIO(src).readline)
            if t.type == tokenize.COMMENT)
    print(f"comments_{path.split('/')[-1]}={n} baseline={expected}")
    bad += (n != expected)
print(f"phase_added_comments={'0' if not bad else 'NONZERO'}")
raise SystemExit(bad)
PY
```

**Baselines to pin: `tests/test_chip_test.py` = 621, `tests/test_readback_inventory.py` = 0, at app
HEAD `ffb0060`.** Keep the inherited regex leg too if desired — it is not wrong, only incomplete — but
do not rely on it alone.

---

## Gate Battery — seven legs, all run green this session

`tools/rekey/check_rekey_ledger.py` is **gone** (C-2). The battery is **seven** legs. Every one was
executed this session from the repo root against `firestarter_app @ ffb0060` in the py3.11 venv, and
**all seven returned rc=0**.

| # | Leg | Command (from `/workspaces`) | Result this session |
|---|---|---|---|
| 1 | ruff check | `cd firestarter_app && ./.venv311/bin/python -m ruff check firestarter/ tests/` | `All checks passed!` rc=0 |
| 2 | ruff format | `cd firestarter_app && ./.venv311/bin/python -m ruff format --check firestarter/ tests/` | `171 files already formatted` rc=0 |
| 3 | mypy watermark | `cd firestarter_app && ./.venv311/bin/python tools/check_mypy_watermark.py` | `mypy errors: 35 (watermark: 35)` / `OK: error count at watermark.` rc=0 |
| 4 | report-shape snapshots | `cd firestarter_app && ./.venv311/bin/python tools/snapshot_report_shapes.py --check` | `OK: 19 snapshot(s) … match a fresh regeneration` rc=0 |
| 5 | devtest orchestrator | `cd firestarter_app && ./.venv311/bin/python tools/check_devtest_orchestrator.py` | `PASS: … 0 VPP-set, 0 raw-wire-dict, 0 --force, 0 broad-except; firmware untouched` rc=0 |
| 6 | diagnostic-report claims | `cd firestarter_app && ./.venv311/bin/python tools/check_diagnostic_report_claims.py` | `PASS: … 216 string literals checked, zero forbidden matches` rc=0 |
| 7 | full suite | `cd firestarter_app && ./.venv311/bin/python -m pytest tests/ -o addopts="" -q` | **`2239 passed, 1 warning in 344.91s`; `32 snapshots passed`** rc=0 |

**The floor is 2239, now measured, not merely asserted.** [VERIFIED: executed this session] This
independently confirms MILESTONES.md and independently refutes `179-02-PLAN.md`'s `>= 2242`, which
would read RED against this healthy tree. Watermark **35**; snapshots **19** (note: leg 4 reports 19
snapshot *files*, leg 7 reports `32 snapshots passed` — different things, both correct, do not
conflate them in a verify block).

**Notes for whoever writes the verify blocks:**
- `mypy` prints "OK" **when it is missing** — leg 3 must match the exact line
  `mypy errors: 35 (watermark: 35)`, as 179's own gate did with `grep -qx`.
- `pytest` `addopts` are `-ra -q`, so a **count line requires `-o addopts=""`**; doubling `-q` hides it.
- `test_flash_path_record_sync` asserts **whole-repo porcelain** — commit before running the suite.
- Suite wall time this session was **344.91 s** without coverage. (MILESTONES.md's 740.92 s baseline was
  a coverage-enabled run; CI applies `--cov-fail-under=70` and measured 84.37%.) Budget accordingly.
- Devcontainer default Python is **3.12**; app CI is **3.11 only** — always `./.venv311/bin/python`
  (confirmed `Python 3.11.16`, resolving `firestarter` to the local tree).
- `grep` here is **ugrep and honours `.gitignore`** — use `/usr/bin/grep` for any evidence-grade scan.

**Cleanliness legs (additional, per `<code_context>`):**
```bash
test -z "$(git -C /workspaces/firestarter status --porcelain)"                              # firmware untouched
test -z "$(git -C /workspaces/firestarter_app status --porcelain firestarter/data/chip_database.json)"  # generated DB untouched
```
Both verified clean this session, along with the meta tree. **Branch state:** meta is on
`gsd/v1.36-dev-test-fidelity-planning`; **both sub-repos are on `gsd/v1.36-dev-test-fidelity`** — a
different name. Do not assume they match.

---

## Seed Amendment (D-09) — exact current text

`.planning/seeds/dev-test-adaptive-sequencing.md` is **177 lines**.

### 1. Frontmatter `status:` — line 5, verbatim

```
status: R1 and R2 realized by Phase 177 (2026-09-05, PRUNE-01/02/03/04); R3 remains for Phase 180 (PRUNE-08); R4 deferred to Future Requirements (R4-01/R4-02)
```
[VERIFIED: .planning/seeds/dev-test-adaptive-sequencing.md:5]

The clause that becomes false is **`R3 remains for Phase 180 (PRUNE-08)`**. The frontmatter has 4
fields (`title`, `trigger_condition`, `planted_date`, `status`) — Phase 177's evidence asserted
`frontmatter_fields=4`, so that count must stay 4.

Note `trigger_condition` (line 3) still reads *"Explicitly NOT v1.35 (documentation-only)"* — stale but
harmless and **out of scope**; do not touch it.

### 2. R3's body — lines 70-93, verbatim

Heading `### R3 — Sample for a rate, sweep for a map` at **line 70**. The body is four paragraphs; the
live instruction D-09 names is the second [VERIFIED: :75-81]:

> "Replace the read step's second full run with a **bit-structured sample**: one 256 B block at each
> `1 << k` boundary for `k` in `8..log2(size)`, plus block 0 and the top block. For a 64 KiB part that
> is 10 blocks / 2560 B, and it toggles **every address line in both polarities** — which is precisely
> the structure `classify_fingerprint` looks for when it clusters mismatch offsets by high address bit.
> A contiguous sample would not do this; the bit-structure is the whole point."

Then the escalation paragraph [:83-85] and the "**Cost, stated:**" paragraph [:87-93].

**The sentence D-09 says must be preserved and answered** sits in **R4**, not R3 [VERIFIED: :105-107]:
> "**Per-connect cost is unmeasured** — the counts are validated, the seconds are not. Anyone planning
> this should measure a connect first and let that decide how much R4 is worth relative to R1–R3."

This is a **small but real refinement of D-09**: D-09 says *"R3's own text instructs a future planner to
'measure a connect first…'"*, but that sentence is in **R4** (lines 105-107), not R3. The substance of
D-09 is untouched — the seed *does* pose the question and Phase 180 *is* the phase that answered it —
but the planner should either amend R4's closing sentence too (it is now false: per-connect cost **is**
measured) or point R3's amendment at it explicitly. **Recommendation: amend both.** Leaving "Per-connect
cost is unmeasured" standing in the seed after Phase 176 measured it recreates exactly the
regenerate-from-the-seed hazard D-09 exists to prevent. Note this widens D-09's stated scope by one
paragraph — worth surfacing as a `checkpoint:decision` if the planner wants it ruled on.

### 3. The precedent to copy — `## Status: Phase 177 amendment`, lines 162-177

[VERIFIED: .planning/seeds/dev-test-adaptive-sequencing.md:162-177] Its shape, which the Phase 180
section should mirror:

1. `## Status: Phase <N> amendment` heading at the **end of the file**, after `## Explicitly out of scope`.
2. Opens `**Phase 177, 2026-09-05.**` — bold phase number and date.
3. States **what was wrong** with the amended text and why (the contradiction, with the technical reason).
4. Names the **deciding authority** (`Decision D-1 (.planning/REQUIREMENTS.md)`).
5. States the **in-place principle** verbatim:
   > "this amendment replaces R1's paragraph **in place** rather than merely annotating it, so the
   > destructive reading is not outvoted but absent — a planner reading only this seed can no longer
   > regenerate it."
6. Closes with an explicit **"Not touched by this amendment:"** list — *"R3, R4, the projected-effect
   table, the per-class characteristics section and the out-of-scope section above."*

**Item 6 is the one to get right.** Phase 177's list explicitly says **R3 is not touched** — Phase 180's
new section must state that it *is* now amended, so the two sections do not contradict each other. Phase
180's own "Not touched" list should read approximately: *R1, R2, the projected-effect table, the
per-class characteristics section, the sequencing note and the out-of-scope section.*

**Do not edit the Phase 177 section.** Append a sibling `## Status: Phase 180 amendment`.

### Evidence file the plan should produce

Phase 177's `evidence/177-03-seed-amendment.txt` is the template [VERIFIED: read this session] — flat
`key=value` scalars:
```
destructive_sentence_present=0    affirmative_exclusion=1    names_both_exclusions=5
states_the_seam=1                 r2_cross_cycle=2           r2_synthesized=1
dated_block=1                     frontmatter_fields=4       status_still_dormant=0
r3_intact=1                       r4_intact=1                projection_table_intact=1
```
**Phase 180 inverts `r3_intact=1` → `r3_intact=0` / `r3_amended=1`**, and (if R4's sentence is amended)
`r4_intact=1` → `r4_amended=1`. Keep `frontmatter_fields=4` and `projection_table_intact=1`.

---

## Requirement Edits — exact current text and lines

All three of CONTEXT.md's line citations are **correct as written**. [VERIFIED:
.planning/REQUIREMENTS.md, read in full this session — 203 lines]

| Item | Line | Status | Current text (verbatim, abbreviated where noted) |
|---|---|---|---|
| **PRUNE-08 v1 checkbox** | **60** ✓ | to flip | `- [ ] **PRUNE-08**: The read step's second full sweep is replaced by a bit-structured sample **only if** MEAS-01 shows the sample is cheaper on the measured board class. If it is not, this requirement closes as *measured, not worth doing*, with the measurement recorded — that is a success, not a miss.` |
| **PRUNE-08 traceability row** | **175** | to flip | `| PRUNE-08 | Phase 180 | Pending |` |
| **MEAS-01** | **103** ✓ | already Complete, do not touch | `- [x] **MEAS-01**: Per-connect cost is measured **per board class** (Uno 512 B, Leonardo 1024 B), not as one number. On Uno-class boards the DTR auto-reset and bootloader wait are likely the dominant term. **This gates PRUNE-08 and the R4 deferral.**` |
| **R4-01** | **122** ✓ | reference only, do not touch | `- **R4-01**: `EpromOperator` leases one validated link per plan rather than tearing `self.comm` down after every call (32 connects for one at28c256 run). **Deferred**: its payoff is unmeasured, MEAS-01 gates whether it is worth scoping, and `run_plan`'s non-fatal-step guarantee means a shared link poisons every later step unless the lease is invalidated on any `SerialError`.` |

**Exactly two edits:** `- [ ]` → `- [x]` at line 60, and `Pending` → `Complete` at line 175. CONTEXT.md
did not give the traceability row's line number — **it is 175**.

**Scope-verification counts to pin** (measured this session, so a verify block can assert them
absolutely):
- Unchecked `- [ ]` v1 boxes **before**: 19 → **after: 18**.
- Checked `- [x]` v1 boxes **before**: 27 → **after: 28**. (Total 46, matching the file's own
  "v1 requirements: 46 total" at :197.)
- Traceability rows reading `| Pending |` **before**: 19 → **after: 18**.
- Every other row byte-unchanged — assert via `git diff --numstat` showing `2` changed lines in
  `.planning/REQUIREMENTS.md`, nothing else.

**Do not** touch MEAS-01, R4-01, the Coverage block (:195-199), or any RPT/HYG row (Phase 181's).

**Standing hazards** (from project memory, both apply here): GSD's requirements/roadmap verbs reformat
the whole file — **prefer hand edits**; and executors have a recorded habit of prematurely marking
multi-plan requirements Complete — here the requirement is genuinely single-plan-able, but the marking
must still be the **last** task, after the closing document exists.

---

## Criterion 4 — the N/A verdict, verified

Roadmap criterion 4 reads, verbatim [VERIFIED: .planning/ROADMAP.md:445]:
> "4. **If sampling ships**, block-wise `(offset, block)` comparison is used, never a whole-file
> compare, proven by a test using a hole-padded region fixture that a whole-file compare would
> misreport as a false divergence."

The precondition is `If sampling ships`. D-01 takes criterion 2, so sampling does not ship, so the
precondition is false. **D-10's N/A verdict is correct on the criterion's own text.** The closing
document must state the verdict **and** the unmet precondition explicitly — a silently unaddressed
criterion is what D-10 exists to prevent.

Worth recording alongside it (D-11's forward note, verified): the hole-padding hazard criterion 4 names
is **real and already solved** in `_read_region` [VERIFIED: chip_test.py:2851-2885, docstring verbatim]:
> "A region read produces a hole-padded file whose real bytes sit at the ABSOLUTE offset `start`
> (`eprom_operations._write_to_file`'s `file_handle.seek(address)`), never at offset 0 -- slicing
> anywhere else would silently read zero-padding instead of the requested bytes."

So a future attempt inherits the fix rather than the bug. Record that; build nothing.

---

## Closing-Document Form — mirror `177-READBACK-INVENTORY.md`

`.planning/phases/177-evidence-gated-read-back/177-READBACK-INVENTORY.md` is 77 lines with six sections
[VERIFIED: read this session]. Its `## PRUNE-04's closure` section (:66-77) is the house style, and it
**explicitly grants PRUNE-08 the same standing**:

> "PRUNE-04 therefore closes as **measured-empty, with the named-and-excluded reason recorded** — the
> same standing this milestone grants PRUNE-08 for closing as *measured, not worth doing*. The census
> gate reddens if a third `operator.read_eprom` site ever appears in `chip_test.py`."

Its four moves, in order — **the template**:
1. **State the verdict** in the requirement's own vocabulary ("measured-empty" / here, "measured, not
   worth doing").
2. **Name the excluded thing** and give its reason, rather than leaving it implicit.
3. **State the standing** the milestone grants the close.
4. **Name the gate that would redden** if the situation changed.

For Phase 180 those map to: (1) PRUNE-08 closes as *measured, not worth doing*, criterion 2, citing
MEAS-01 §4a/§4b and §7; (2) the excluded thing is the bit-structured sample, excluded because 10
connects > 1 connect on both board classes at every reference size — plus criterion 4 named N/A with
its unmet precondition (D-10) and the size-gated variant named-and-declined (D-05); (3) the standing is
the one 177 already granted it; (4) the gates are D-06's three tests — and **the condition that would
invalidate the close is R4-01** (D-08), which is a stronger, more honest version of move 4 than a
reddening gate, because no test can detect a design change that has not happened yet.

Also worth mirroring: 177's inventory leads with a **`## Search method`** section (:12-32) stating how
the population was enumerated, so a reader can re-run it. Phase 180's analogue is the connect
arithmetic and the block enumeration — state them so they can be recomputed, not just believed.

**Suggested filename:** `180-PRUNE-08-CLOSURE.md`, matching the `NNN-TOPIC.md` convention of
`176-MEASUREMENT.md`, `177-READBACK-INVENTORY.md`, `177-REKEY-MAPPING.md`, `179-MEASUREMENT.md`.

---

## Evidence Directory Convention (D-07)

Phases 175-179 each carry `.planning/phases/<phase-dir>/evidence/` with files named
`<phase>-<plan>-<topic>.txt` [VERIFIED: listed this session] — e.g. `177-03-readback-census.txt`,
`179-04-phase-seal.txt`. Phase 180 must create its own; the directory does not exist yet.

Transcript form, from `177-03-readback-census.txt` [VERIFIED: read this session]:
```
== 1 the census itself
source_nonempty=True
engine_read_sites=2
enclosing=_dispatch_read,_read_region
rc=0
== 2 the census module
......                                                                   [100%]
6 passed in 0.33s
rc=0
comments_test_readback_inventory=0
```
Numbered `== N label` sections; flat `key=value` scalars; verbatim pytest tail; explicit `rc=0` after
each command. **Every claim is a scalar a reader can diff**, never prose.

**Files Phase 180 should produce** (one per D-07 gate, plus the seal):
- `180-01-verdict-pin-red.txt` — the AST pin GREEN at HEAD and RED against the planted
  `and not divergence` mutant, with both `verdict_names` lists printed.
- `180-01-behavioural-legs.txt` — the four-row leg1/leg2/control matrix (already produced this session;
  re-run at execution time against the committed tests).
- `180-02-seed-amendment.txt` — Phase 177's key set with `r3_intact` inverted.
- `180-02-requirement-marking.txt` — the before/after checkbox and `Pending` counts.
- `180-0N-phase-seal.txt` — all seven legs plus the cleanliness legs and the comment delta gate.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---|---|---|---|
| Locating `chip_test.py` from a test | `Path(__file__).parent.parent / "firestarter"` | `_engine_source()` [test_readback_inventory.py:95] | Recorded project failure: a checker resolving directory-relative scanned nothing and **exited 0**. Also the app-CI-vs-devcontainer divergence that sent app CI `13 failed, 13 passed`. |
| Proving a gate works | Asserting it in the plan or a docstring | The planted in-memory string mutation [:109-115] | D-07, and the recorded "fixture-passing selftests ≠ working tooling" lesson (~20 rig defects, all selftest-green). A pre-authored gate leg can be **unreachable**; RED proves nothing until seen to pass. |
| Counting comments | `grep -cE '^\+[[:space:]]*#'` | `tokenize` COMMENT tokens | C-3 — the regex is blind to trailing comments, which is the exact form the sibling test would teach an executor to write. |
| Finding call sites / verifying structure | `grep` | `ast` | `test_readback_inventory.py`'s own docstring: *"A grep census fails open on a rename or a reformatted call."* Also: devcontainer `grep` is ugrep and honours `.gitignore`. |
| A test double for the read path | A new fake | `_mock_operator()` + a `side_effect` closure [tests/test_chip_test.py:1019, 2145-2153] | `_mock_operator` is `Mock(spec=_OPERATOR_METHODS)`; a hand-rolled double drifts from the spec and silently stops constraining the call signature. |
| Deciding the block count | Re-reading the seed's `8..log2(size)` range | The enumerated block list / `log2(size) − 6` | C-4 — the range notation read literally contradicts the seed's own stated answer. |
| Requirement/roadmap edits | `gsd-tools` requirements/roadmap verbs | Hand edits | Recorded: those verbs reformat the whole file; `roadmap.update-plan-progress` additionally clobbers the dependency table. |

---

## Common Pitfalls

### Pitfall 1: Copying `179`'s eight-leg gate set or its 2242 floor
**What goes wrong:** the plan invokes `tools/rekey/check_rekey_ledger.py`, which does not exist
(rc≠0, or worse a `python3`-on-missing-file exit 2 that a fail-closed check mistakes for a real
verdict — a tautology this project has already recorded); and a `>= 2242` assertion reads RED against
a healthy 2239 tree.
**How to avoid:** seven legs, floor **2239** (both measured this session). MILESTONES.md aims this
warning by name at *"a phase 180/181 plan"*.
**Warning sign:** any verify block mentioning `rekey`, `ledger`, `2241` or `2242`.

### Pitfall 2: Writing a `#` comment into the new tests
**What goes wrong:** violates a hard rule that a plan cannot override — and the inherited gate will not
catch a trailing one (C-3), so it ships green.
**How to avoid:** docstrings only; `tokenize` delta gate with baselines 621 / 0.
**Warning sign:** the plan says "add a comment explaining…", or makes a comment an acceptance criterion.

### Pitfall 3: An AST pin that only checks `last_ok` is present
**What goes wrong:** stays green on `VERDICT_OK if last_ok and not divergence else VERDICT_BAD` — the
exact failure criterion 3 names. The pin looks rigorous and proves nothing.
**How to avoid:** assert the **exact name set**; prove RED against the planted mutant.
**Warning sign:** the assertion uses `in` rather than `==`.

### Pitfall 4: Publishing modelled second-counts as findings
**What goes wrong:** breaches D-04 and the milestone's own Out-of-Scope row (*"Quoting the cost model's
second-counts as acceptance criteria"* — REQUIREMENTS.md:140), and over-claims on a model with a
recorded 24% error.
**How to avoid:** the model-free connect-count form; MEAS-01's measured figure as the per-connect unit
only, per board class, never blended; the 2.5× labelled as modelled or dropped (C-6).
**Warning sign:** any ≥512 KiB second-count, or any single blended per-connect number.

### Pitfall 5: Running the suite with a dirty tree
**What goes wrong:** `test_flash_path_record_sync` asserts whole-repo porcelain; a red result that looks
like a real failure is actually an uncommitted file.
**How to avoid:** commit first, then run.

### Pitfall 6: Marking PRUNE-08 Complete before the closing document exists
**What goes wrong:** a recorded, repeated executor failure mode in this project.
**How to avoid:** requirement marking is the **last** task, gated on the document being committed.

### Pitfall 7: Amending the seed's R3 but leaving R4's "Per-connect cost is unmeasured"
**What goes wrong:** the seed still tells a future planner the thing is unmeasured, recreating the
regenerate-from-the-seed hazard D-09 exists to prevent.
**How to avoid:** amend both, or have R3's amendment point at R4's sentence explicitly (see §Seed
Amendment item 2).

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|---|---|---|---|
| PRUNE-08 go/no-go verdict + rationale | Planning record (`.planning/phases/180-.../`) | — | Documentary. No code path expresses a "we decided not to sample" state. |
| Criterion 3 behavioural pins | Host test suite (`firestarter_app/tests/test_chip_test.py`) | — | Behaviour of `_dispatch_read` through `run_plan`; unit-testable, no board. |
| Criterion 3 structural pin | Host test suite (`tests/test_readback_inventory.py`) | — | Source-shape claim about `chip_test.py`; `ast`, no execution. |
| One-connect-per-read premise (C-7) | Host test suite (`tests/test_readback_inventory.py`) | — | Source-shape claim about `eprom_operations.py`; the module already imports `EpromOperator`. |
| Design-record amendment | Seed (`.planning/seeds/dev-test-adaptive-sequencing.md`) | — | The seed is what a future planner reads first; D-09. |
| Requirement state | `.planning/REQUIREMENTS.md` | `.planning/ROADMAP.md` (phase checkbox) | Two-line edit; the roadmap's Phase 180 `**Plans**: TBD` also becomes the plan list at close. |
| Read step execution | **Unchanged** (`chip_test.py:_dispatch_read`) | — | Explicitly out of scope. Zero product-source edits this phase. |

---

## Project Constraints (from CLAUDE.md)

| Directive | Source | Binding on this phase |
|---|---|---|
| **No comments in product source, at all** — not overridable by a plan, task, skill or subagent | `/workspaces/CLAUDE.md`; `firestarter_app/CLAUDE.md:5-21` | **Yes.** `tests/` is product source. Docstrings only. Must not be an acceptance criterion that "a comment exists". |
| Rationale goes in `SUMMARY.md`, `REQUIREMENTS.md` traceability, or the commit message | both | Yes — the closing document and SUMMARY.md are the homes. |
| Docstrings are not comments; Click docstrings are `--help` text | `firestarter_app/CLAUDE.md:17-19` | Yes — the new tests carry rationale in docstrings. |
| `chip_database.json` is **generated**; never hand-edit | `/workspaces/CLAUDE.md` | Yes — read-only here (corpus counts). Assert byte-unchanged. |
| Constants duplicated Python↔C++ must change together | `/workspaces/CLAUDE.md` | N/A — no constants change. |
| Serial protocol must stay in sync across repos | `/workspaces/CLAUDE.md` | N/A — no protocol change. |
| `main` protected in all three repos; base branch is `beta` | `/workspaces/CLAUDE.md`; `.planning/config.json` `git.base_branch: "beta"` | Yes at ship time, not during the phase. |
| No firmware change | phase scope + `<code_context>` | Yes — `git -C firestarter status --porcelain` must stay clean (verified clean now). |
| Tooling gate: ruff + ruff format + mypy + `pytest --cov-fail-under=70` on every PR | `firestarter_app/CLAUDE.md:132` | Yes — legs 1/2/3/7; coverage floor 70, currently 84.37%. |

**Project skills** (`.claude/skills/`): `devtest-rootcause`, `devtest-triage`, `find-skills`,
`skill-creator`. None is triggered by this phase — there is no chip failure to triage or root-cause.
`devtest-triage`'s SKILL.md is named by RPT-F2 as a **Phase 181** edit; **do not touch it here**. No
`.claude/rules/` directory exists.

---

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|---|---|---|---|---|
| Python 3.11 venv (`firestarter_app/.venv311`) | every gate leg, both test legs | ✓ | 3.11.16 | none needed — **required**, devcontainer default 3.12 diverges from CI |
| `ruff` (in venv) | legs 1-2 | ✓ | — | — |
| `mypy` + `tools/check_mypy_watermark.py` | leg 3 | ✓ | watermark 35/35 | — |
| `tools/snapshot_report_shapes.py` | leg 4 | ✓ | 19 snapshots | — |
| `tools/check_devtest_orchestrator.py` | leg 5 | ✓ | — | — |
| `tools/check_diagnostic_report_claims.py` | leg 6 | ✓ | 216 literals | — |
| `pytest` + `syrupy` | leg 7 | ✓ | 2239 passed / 32 snapshots | — |
| `/usr/bin/grep` (real GNU grep) | evidence scans | ✓ | — | none — shell `grep` is ugrep, honours `.gitignore` |
| `tools/rekey/check_rekey_ledger.py` | *nothing* | ✗ **deleted** | — | **n/a — leg retired (C-2)** |
| Arduino board / EPROM part | *nothing* | n/a | — | **Not hardware-gated (D-02).** No `blocking-human` bench wave. |

**Missing dependencies with no fallback:** none.
**Missing dependencies with fallback:** none. `check_rekey_ledger.py` is absent **by design**, not
missing — the leg it served was retired, not replaced.

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|---|---|---|
| A1 | The plan will place the one-connect structural pin in `test_readback_inventory.py` rather than treating it as out of scope. | C-7, Structural Premise | Low. Either resolution is defensible; the premise is verified regardless, only its *pinning* is at stake. Surface as a `checkpoint:decision`. |
| A2 | Amending R4's "Per-connect cost is unmeasured" sentence is within D-09's intent. | Seed Amendment | Low-medium. D-09 names R3; extending to one R4 sentence widens scope by a paragraph. If declined, the seed keeps a statement Phase 176 falsified. |
| A3 | `180-PRUNE-08-CLOSURE.md` is the right filename. | Closing-Document Form | Trivial — naming only; follows the `NNN-TOPIC.md` convention. |
| A4 | The suite count stays at 2239 + 3 (or +4) once the new tests land. | Gate Battery | Low. Additive test functions each add exactly one instance; the executor should re-measure rather than assume, per the recompute-never-transcribe rule. |
| A5 | Comment baselines 621 / 0 remain valid at execution time. | Comment Discipline | Low, but **anchor them to app HEAD `ffb0060`** — if any other work lands in `test_chip_test.py` first, re-measure. |

**Everything else in this document was verified by reading the source-of-truth file or by executing a
command this session.** No claim about a measurement figure, line number, verdict expression, gate
result or corpus count rests on training memory.

---

## Open Questions

1. **Does the one-connect premise get a pin? (C-7)**
   - What we know: `<code_context>` asks for one; `<domain>` scopes four deliverables and D-06 locks
     three tests; the pin is feasible and its honest ceiling is known.
   - What's unclear: whether the operator considers it a fifth artifact or part of deliverable 2.
   - Recommendation: **include it** as a fourth additive test in `test_readback_inventory.py`. It is
     ~12 lines, reuses existing imports, and D-02 names the premise as one of only two load-bearing
     facts — prose is the weakest link in the close without it. Gate on a `checkpoint:decision` if the
     planner wants it ruled on.

2. **Does the seed's R4 paragraph get amended too? (A2, Pitfall 7)**
   - What we know: R4:105-107 says "Per-connect cost is unmeasured", which Phase 176 falsified; D-09
     attributes that sentence to R3, where it does not appear.
   - What's unclear: whether D-09's author intended R4's sentence or misremembered its location.
   - Recommendation: amend both, and note the widening in the plan. The cost of leaving it is exactly
     the hazard D-09 was written to prevent.

3. **Does the closing document quote the 2.5× factor? (C-6)**
   - What we know: it reproduces (2.51× / 2.58×) but only via a D-04-bounded modelled read rate.
   - Recommendation: lead with the model-free connect-count form; include 2.5× only with an explicit
     "modelled, not measured" label, or omit it. The close is strictly stronger without it.

---

## Security Domain

`security_enforcement` is not set in `.planning/config.json` (treated as enabled). **No ASVS category
applies to this phase.** It ships zero product-source changes, adds no dependency, opens no network or
serial path, parses no untrusted input, and touches no credential, secret or user data. The only
executable artifacts are three-to-four additive pytest functions that parse a first-party source file
with `ast` in-memory.

| ASVS Category | Applies | Reason |
|---|---|---|
| V2 Authentication | no | No auth surface. |
| V3 Session Management | no | No sessions. (R4-01's "session leasing" is a serial-link lease, named only, never implemented.) |
| V4 Access Control | no | No access-control surface. |
| V5 Input Validation | no | No new input is parsed. `ast.parse` is applied to a first-party file resolved from `chip_test.__file__`. |
| V6 Cryptography | no | No crypto. (`hashlib.sha256` in `_dispatch_read` is a pre-existing divergence check, unmodified.) |
| V12 Files & Resources | no | The new tests write **no files** — D-07 mandates in-memory string mutation only. |

**One supply-chain-adjacent note, in scope for this project's own honesty discipline rather than for
ASVS:** the `phase_added_comments` regex gate (C-3) is a control that reads green while the condition
it guards is violated. That is a fail-open check of the same family as the tautological fail-closed
proofs MILESTONES.md records condemning the re-key checker. Replacing it with the `tokenize` gate is the
mitigation.

**Package Legitimacy Audit: not applicable.** This phase installs **no** external package. HYG-02
(*"No new runtime dependency is added"*) is a Phase 181 requirement and is respected here vacuously.
The `tokenize`, `ast`, `io` and `pathlib` modules proposed above are all Python standard library.

---

## Validation Architecture

**Omitted deliberately.** `.planning/config.json` sets `workflow.nyquist_validation: false`
[VERIFIED: read this session].

---

## Sources

### Primary (HIGH confidence — opened and/or executed this session)
- `.planning/phases/180-.../180-CONTEXT.md` — read in full (339 lines); all decisions transcribed verbatim.
- `.planning/REQUIREMENTS.md` — read in full (203 lines); lines 60/103/122/175 quoted verbatim.
- `.planning/phases/176-.../176-MEASUREMENT.md` — §1, §4a, §4b, §5, §6, §7, Disposition read verbatim.
- `.planning/seeds/dev-test-adaptive-sequencing.md` — read in full (177 lines).
- `.planning/notes/dev-test-sequence-cost-model.md` — §Provenance, §Measured primitives, §Connect counts, §What this note does not establish.
- `.planning/MILESTONES.md:1-41`; `.planning/ROADMAP.md:300-350, 425-460`; `.planning/STATE.md:1-295`.
- `.planning/phases/177-.../177-READBACK-INVENTORY.md` — §The eight-row inventory, §PRUNE-04's closure.
- `.planning/phases/177-.../evidence/177-03-readback-census.txt`, `177-03-seed-amendment.txt`.
- `.planning/phases/179-.../179-PATTERNS.md:448-455`, `179-02-PLAN.md:35-45`.
- `firestarter_app/firestarter/eprom_operations.py:454-560, 896-960`.
- `firestarter_app/firestarter/chip_test.py:2660-2700, 2767-2900`.
- `firestarter_app/tests/test_readback_inventory.py` — read in full (139 lines).
- `firestarter_app/tests/test_chip_test.py:1019-1115, 1428-1445, 2110-2195`.
- `/workspaces/CLAUDE.md`; `firestarter_app/CLAUDE.md:5-21, 132`; `.planning/config.json`.
- **Executed:** all seven gate legs (rc=0, suite `2239 passed`); the D-06 leg1/leg2 behavioural probe
  (4/4 as predicted); the leg-3 AST pin GREEN-at-HEAD / RED-at-planted-mutant proof; the block-list
  enumeration; the `chip_database.json` corpus counts; the `tokenize` comment counts; the
  trailing-comment gate-blindness demonstration; `find` for `check_rekey_ledger*`.

### Secondary (MEDIUM confidence)
- `.planning/graphs/graph.json` — present; not queried, direct source reading was more precise for a
  verification pass over named files.

### Tertiary (LOW confidence)
- None. No web search was performed and none was warranted: every question in this pass was answerable
  from the repository, and every answer was.

---

## Metadata

**Confidence breakdown:**
- Measurement figures — **HIGH.** Quoted verbatim from `176-MEASUREMENT.md`; all four figures, the floor, and §6/§7's roles confirmed.
- Structural premise — **HIGH.** `_operation_context` at 515-550 exactly; `read_eprom` at 896-943 with a single context. Read, not inferred.
- `_dispatch_read` / verdict — **HIGH.** Verdict expression quoted verbatim at :2808; both behavioural legs executed and passing.
- AST pin feasibility — **HIGH.** Prototyped, run, and proven to discriminate against a planted mutant with a unique anchor.
- Gate battery — **HIGH.** All seven legs executed this session; floor 2239 measured, not transcribed.
- Corpus counts — **HIGH** for the three bucket counts and the `support_status` distribution (computed from the shipped database). The **"all supported"** wording is **refuted** (C-1).
- Arithmetic (N = log2−6) — **HIGH.** Enumerated and cross-checked against the seed's own stated answer.
- The 2.5× factor — **MEDIUM.** Reproduces, but depends on a D-04-bounded modelled read rate (C-6).
- Seed / requirement line numbers — **HIGH.** All read this session.

**Research date:** 2026-09-08
**Measured against:** `firestarter_app @ ffb0060`, `firestarter` clean, meta `@ f031be81`, branch
`gsd/v1.36-dev-test-fidelity-planning` (sub-repos on `gsd/v1.36-dev-test-fidelity`).
**Valid until:** the next commit touching `chip_test.py`, `eprom_operations.py`, `test_chip_test.py`,
`test_readback_inventory.py`, `REQUIREMENTS.md` or the seed. Line numbers are the perishable part;
re-verify them at plan time if any of those files moves. The measurement figures and the corpus counts
are stable.
