# Phase 200: An elevated programming supply is stated - Context

**Gathered:** 2026-09-19
**Status:** Ready for planning

<domain>
## Phase Boundary

A decoded `vdd_mv` that nothing applies stops being invisible. The host states, where the operator
will see it before committing to a write, that a part's programming supply is above the fixed 5.0 V
the shield can deliver.

**In scope:** the `info` surface, one new displayed field, one warning, and the tests that pin both.
**Out of scope:** changing what the shield supplies, refusing any operation, touching `write`,
any firmware change, and retrofitting RAIL-03.

</domain>

<decisions>
## Implementation Decisions

### The scale of the problem, measured before deciding anything

- **D-01:** **284 of 746 rows need more than 5.0 V to program.** Measured from the live
  `firestarter/data/chip_database.json` during this discussion, not estimated. `vdd_mv` histogram:
  3300 ×20, 5000 ×442, 5500 ×164, 6000 ×8, 6250 ×7, 6500 ×105. `vcc_mv` carries only three values
  (3300 ×18, 5000 ×700, 5500 ×28). Every one of the 284 is `support_status: supported`, spanning 34
  vendors and algorithms 7, 8 and 11. `vdd_mv > vcc_mv` selects 285 rows, of which 284 are also
  above 5000 — so "elevated" and "above the shield's rail" are the same set here, bar one row.
  **This number is the reason for D-02.** A condition that holds for 38% of the database cannot be
  surfaced the way a rare fault is, or it becomes noise and gets tuned out.

### Where the statement appears

- **D-02:** **`info` only. NOT `write`.** `info` is the pre-flight surface — it is where someone
  checks a part before committing. Keeping `write` quiet is what preserves the meaning of the
  warnings `write` does emit. Operator decision, against
  the alternative of warning on both. **Accepted cost, recorded rather than hidden:** an operator who
  never runs `info` never sees it. VCC-01's "before the attempt" is satisfied by `info` being the
  surface that precedes the attempt, not by warning during it.
  — **Reversibility:** reversible — adding the same call at the `write` site later is a one-line
  change; nothing about this decision forecloses it.

- **D-03:** **The predicate is `vdd_mv > 5000`**, with 5000 a named constant standing for the
  shield's fixed supply, phrased as VCC-01 phrases it. Not `vdd_mv > vcc_mv` — the shield delivers a
  fixed rail regardless of what a row's `vcc_mv` says, and the 28 rows at `vcc_mv` 5500 are Phase
  198's D-11 set, deliberately untouched here.

### What it says

- **D-04:** **A field row AND a warning line.** The row makes the decoded value visible where every
  other electrical value already lives; the warning names both numbers and states what will happen.
  The row alone is too easy to skim past on a 38%-common condition; the warning alone loses the value
  itself. This wording **establishes** the project's shortfall-statement shape — VCC-02 is satisfied
  by defining it, not by matching RAIL-03, which was adjudicated UNMET at the close of Phase 199.
  Shape agreed with the operator:

  ```
  VCC:                5.0v
  Programming VCC:    6.0v
  VPP:                12.5v

  WARNING: this part programs at 6.0 V; the shield supplies a fixed 5.0 V.
  Programming will be attempted at 5.0 V.
  ```

- **D-05:** **State and proceed; refuse nothing.** Milestone D-4 already settled this shape: the
  operation proceeds with a statement naming both numbers rather than refusing silently or attempting
  silently. All 284 rows are `supported` today and nothing measured says 5.0 V actually fails for
  them; refusing would strand 38% of the database on a value that was never applied before this phase
  either. **Nothing that works today stops working.**

- **D-06:** **Fail open.** An absent, null or zero `vdd_mv` produces no field row and no warning.
  Phase 199 established that absent evidence must never raise a warning; manufacturing one from
  missing data is worse than silence. A row whose `vdd_mv` is at or below 5000 likewise produces
  neither.

### Host, and why that does not contradict D-21

- **D-07:** **This is host-side work.** `vdd_mv` **does not cross the wire** — measured at
  `firestarter/database.py`, whose wire dict carries `vpp_mv` and `vcc_mv` only — so the firmware
  cannot know a part needs an elevated programming supply. Nor is there anything for it to do: the
  shield's VCC is fixed, so unlike the VPP shortfall there is no second rail to route to. Phase 199's
  D-21 moved a *routing decision* the firmware could already make from data it already held; this is
  neither, so the two decisions do not conflict. **Adding `vdd_mv` to the wire is out of scope** — it
  would be a protocol change across both repos in lockstep, and nothing in this phase needs it.

### Claude's Discretion

- Where exactly the field row sits in the `info` table, and the exact renderer used, so long as it
  matches the existing `VCC:` / `VPP:` row style and the snapshot moves only where expected.
- **Which mechanism carries the warning is genuinely open, because there is no precedent to follow.**
  Verified during this discussion: `info` has NO existing warning path. Support-status problems
  surface as a raised `ClickException` through the `map_typed_errors` decorator in
  `firestarter/cli_handlers.py` — that is a **refusal**, which D-05 forbids here. So this phase
  introduces the first advisory statement on `info`, and the planner picks `logger.warning` or
  `click.echo` on its merits. Note the Phase 199 precedent for the analogous choice: a warning meant
  to be visible at default verbosity went through `click.echo`, because `logger.warning` on a
  non-verbose run may not reach the operator. Confirm that against the live `info` path rather than
  inheriting it.
- Test structure, provided the 284-row count is asserted as an equality derived from the live
  database and not hand-transcribed, and provided the non-vacuity of that count is proved.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### This phase's scope and its amendment
- `.planning/ROADMAP.md` § "Phase 200: An elevated programming supply is stated" — the goal, the
  amended success criterion 2, and the scope facts settled before planning.
- `.planning/REQUIREMENTS.md` — VCC-01 and VCC-02. **VCC-02's text still says "the same warning shape
  as RAIL-03"; read it together with the ROADMAP amendment, which supersedes that clause.**

### Why RAIL-03 is not the reference
- `.planning/phases/199-what-the-rails-can-actually-deliver/199-05-SUMMARY.md` — the RAIL-03
  adjudication and its arithmetic.
- `.planning/phases/199-what-the-rails-can-actually-deliver/199-VERIFICATION.md` — the verifier's
  concurrence with that adjudication.

### The host/firmware boundary this phase sits on
- `.planning/phases/199-what-the-rails-can-actually-deliver/199-CONTEXT.md` §§ D-21, D-22, D-23 —
  the reversal that moved VPE routing to firmware, and why it does not reach this phase.
- `firestarter_app/tools/DECODE-NOTES.md` § 10 — the voice and limit-naming register this phase's
  own record should match if it writes one.

### What the two voltage fields mean
- `firestarter_app/tools/DECODE-NOTES.md` § 9 — the voltage word's two nibbles; `vdd_mv` and
  `vcc_mv` decode and what they were found to select.
- `.planning/phases/198-the-two-voltage-nibbles/198-VOLT03-DISPOSITION.md` — the 28-row `vdd < vcc`
  set, deliberately untouched, which this phase must not disturb.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- The `info` surface renders an aligned field table (`VCC:`, `VPP:`, `Pulse delay:`) — the row style
  exists and should be matched. **The warning mechanism does NOT exist and must be chosen**; see
  Claude's Discretion above. Measured: `grep support_status` across `cli_handlers.py` and
  `eprom_presenter.py` returns one hit, a comment in the `ChipNotImplementedError` arm of
  `map_typed_errors`, which raises rather than warns.
- `firestarter_app/tests/__snapshots__/test_characterization.ambr` pins rendered output; this phase
  will move it, and Phase 199 established the discipline of a scoped re-record proved by `--numstat`
  rather than a blanket regeneration.

### Established Patterns
- Exact counts asserted as equalities, never floors, and proved non-vacuous by a planted mutation —
  the shape `tests/test_vpp_rail_classification.py` established in Phase 199.
- Values derived from the live generated database rather than hand-kept lists.
- `firestarter/data/chip_database.json` is GENERATED. It is never hand-edited, and this phase
  regenerates nothing — it reads.

### Integration Points
- `firestarter/cli_handlers.py` — the `info` handler.
- `firestarter/database.py` — where the wire dict is built; **read-only for this phase**, cited only
  to show `vdd_mv` is absent from it.

</code_context>

<specifics>
## Specific Ideas

- Worked example agreed during discussion: `FUJITSU/MBM27C1000P,MBM27C1000` — `vcc_mv` 5000,
  `vdd_mv` 6000, `vpp_mv` 12500. It is also gh#70's part, so a reporter would recognise it.
- The 5500 tier (164 rows, +10% over the rail) versus the 6000–6500 tier (120 rows, +20–30%) was
  raised and **deliberately not acted on**: tiering would need a threshold nobody has measured, which
  is the trap Phase 199 spent an attended bench session avoiding. All 284 rows are treated alike.

</specifics>

<deferred>
## Deferred Ideas

- **Warning on `write` as well as `info`.** Considered and declined for now (D-02). Revisit only with
  evidence about how operators actually use the two surfaces.
- **Tiering by how far above 5.0 V a part sits.** Needs a measurement that does not exist. If ever
  taken up, it needs a bench session, not a guess.
- **Putting `vdd_mv` on the wire** so the firmware could act on it. Out of scope; a protocol change
  in lockstep across both repos, and nothing here needs it.
- **Retrofitting RAIL-03** with this phase's wording once it exists. Explicitly left as a separate
  decision — a host-side VPP warning would require the host to carry the 17380 drop-path ceiling
  again, which is the stale-figure exposure D-21 moved away from. Milder for a warning than for
  routing, but not free.

### Reviewed Todos (not folded)
- `2026-06-24-skip-vpp-error-and-warning-checks-when-vpp-unused-on-reads.md` — "Skip VPP
  error/warning checks when VPP is unused (reads/blank-checks)". Matched on keywords, but it is a
  firmware VPP concern and this phase is a host-side VCC one. Not folded.
- `2026-08-27-strip-gsd-provenance-comments-from-source.md` — "Strip residual GSD provenance comments
  from product source (operator hard rule)". **OBSOLETE.** The operator removed the source-comment
  rule outright on 2026-09-19 (meta `41a34c6a`, `firestarter_fw` `abfc2ec`, `firestarter_app`
  `029208c`). The todo's premise no longer exists. Flagged for retirement rather than folded.

</deferred>
