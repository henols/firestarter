# Phase 140: Parameter Table - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-08-09
**Phase:** 140-parameter-table
**Areas discussed:** Column set & the 0x0B energy cap; Row values & the 0x08 overprogram
contradiction; Consumption seam with Phase 141; Proof machinery (TABLE-03/04/05)

**Areas offered and selected:** all four presented gray areas were selected. A fifth candidate —
table storage form (PROGMEM vs RAM) and unknown-protocol behavior — was folded into area 1 rather
than presented separately, because the MERGE-05 RAM-delta-zero constraint forces PROGMEM regardless.

---

## Column set & the 0x0B energy cap

### Q1 — Where should 0x0B's 50 ms per-byte accumulated-energy cap live?

| Option | Description | Selected |
|--------|-------------|----------|
| Sixth column: `energy_cap_us` | 0 = uncapped on 0x07/0x08, 50000 on 0x0B. TABLE-01 says the table "carries rows with" five columns, not "only" five, so a sixth is additive. Self-documenting; one cell for TABLE-04 to cite. ~4 B PROGMEM/row. | ✓ |
| Derive `max_pulses = 50000 / pulse_delay` | No new column, but `max_pulses` then means a count on two rows and a derived budget on the third, and reintroduces pulse into the table's semantics. | |
| Overload `overprogram_cap_us` | Meaning flips with `overprogram_factor`. Zero new flash — but a field that means two things is the unattributable number TABLE-04 exists to stop. | |
| Keep it in the Phase 141 loop | Table stays literally five columns; loop carries `if (protocol == PROTO_EPROM_24PIN)`. Plants a second protocol test in the write path. | |

**User's choice:** Sixth column: `energy_cap_us`
**Notes:** → CONTEXT D-01.

### Q2 — What does `verify_mode` actually select for these three protocols?

| Option | Description | Selected |
|--------|-------------|----------|
| When to verify: per-pulse vs per-pulse + final pass | `VERIFY_PER_PULSE` vs `VERIFY_PER_PULSE_PLUS_FINAL`. Matches how Intel Intelligent / Quick-Pulse datasheets are written. | ✓ |
| Single value today — honest placeholder | All three rows identical; TABLE-04 would cite "no datasheet basis". Dead PROGMEM on all three rows. | |
| Verify VCC margin (5.0 V vs 6.0 V) | What the datasheets specify — but the RURP has no VCC-raise path, so the column could only record an inert value. | |
| You decide | Defer to Phase 140 research under TABLE-04 and the 6.25 V ceiling. | |

**User's choice:** When to verify (two values)
**Notes:** Constraint attached during the exchange: this column may **never** encode verify VCC —
the ~6.25 V ceiling makes the datasheets' margin verify unreachable, and the citation must say so.
→ CONTEXT D-02.

### Q3 — Where do the `pulse_delay == 0` fallback constants (1000 / 100 / 500 µs) live after this phase?

| Option | Description | Selected |
|--------|-------------|----------|
| Leave the switch in `configure_eprom` | `eprom.cpp:71-76` stays as-is; no pulse number enters the table. Literal TABLE-02 compliance; the fallback stays visibly a fallback. | ✓ |
| `fallback_pulse_us` column + amend TABLE-02 | One row = one protocol's complete story — but that IS a pulse-width column, and gh#15's posted correction just told the world there isn't one. | |
| Named `#define`s beside the table, not in it | Kills three magic numbers without putting a pulse in a row — but two structures then describe one protocol. | |
| You decide | Pick whichever reads most honestly to a stranger implementing from gh#15 and the table together. | |

**User's choice:** Leave the switch in `configure_eprom`
**Notes:** → CONTEXT D-03.

### Q4 — What happens when the table lookup finds no row for `handle->protocol`?

Framing supplied before the question: MERGE-05 requires AVR RAM delta **exactly 0**, so a `const`
struct array without `PROGMEM` lands in `.data` and fails the gate on arrival — PROGMEM is forced,
following `key_parsers[]` at `json_parser.c:164`. Uno-class flash headroom is 42 B / 36 B against the
64 B band at the fork base.

| Option | Description | Selected |
|--------|-------------|----------|
| Return NULL → fail closed, zero hardware side effects | Matches `memory.cpp` steps 6a/6b/7 (Phase 64 / v1.20). Guard survives a future dispatch edit the compiler cannot catch. | ✓ |
| Fall back to the 0x07 row | Mirrors today's `default: 1000`; lowest flash. But an unrecognized protocol would silently get 13 V through the drop resistor. | |
| Compile-time only (`static_assert` + comment) | No runtime cost — but proves nothing at runtime and the gate would have nothing to assert against. | |
| You decide | Weigh the fail-closed house rule against the tight flash band. | |

**User's choice:** Return NULL → fail closed
**Notes:** → CONTEXT D-05. PROGMEM storage → D-04.

**Continue check:** "Next area" — declined further questions on C types/widths, `vpp_path`
encoding, and table file layout; those fell to Claude's discretion.

---

## Row values & the 0x08 overprogram contradiction

Framing supplied: `PROJECT.md`'s prose excludes Quick-Pulse from overprogram while its own throughput
table gives `0x08` a `3 × N × pulse` overpulse. `0x08` is `EPROM_QUICK` in firmware, modal DB pulse
100 µs (n=127).

### Q1 — Is 0x08's `overprogram_factor` 3 or 0?

| Option | Description | Selected |
|--------|-------------|----------|
| Let research settle it, prose wins on a tie | Resolve from primary AM27C020 / 27C010-class datasheets; on ambiguity factor 0 ships, because an unneeded overpulse damages silicon while a missing one only under-programs and is caught by verify. Contradiction named explicitly either way. | ✓ |
| Factor 0 now | Treat the throughput table as the erroneous copy. Fast and safe — but decides a silicon question from a planning document. | |
| Factor 3 now | Treat the prose as over-general. But contradicts the explicit gating rule with no datasheet behind it. | |
| Split it — 0x08 needs more than one row | If the family genuinely spans both, flag it for Phase 146 — a second row keyed on anything but `protocol_id` would be a second dispatch key. | |

**User's choice:** Let research settle it, prose wins on a tie
**Notes:** → CONTEXT D-06. The family-split possibility survives as a Phase 146 finding, not a
Phase 140 action.

### Q2 — On 0x0B, which limit binds — `max_pulses` or `energy_cap_us`?

Worked example supplied: at 500 µs the two agree exactly (100 × 500 µs = 50 ms); at 200 µs the count
cuts the byte off at 40% of its budget; at 1000 µs the cap cuts it off at 50 pulses.

| Option | Description | Selected |
|--------|-------------|----------|
| Both, whichever trips first | Cap is the intended budget and normally binds; `max_pulses` is a termination backstop against a pathological pulse width. Same LOOP-05 hard-fail; the error reports which tripped. | ✓ |
| Energy cap only — `max_pulses = 0` unbounded | One budget, no ambiguity — but the sentinel makes the column mean two things, and termination depends on `pulse_delay` being sane, which `--pulse-us` can violate. | |
| Count only — `max_pulses = 100`, drop the cap | All three rows read identically — but silently under-programs every 0x0B chip below 500 µs and discards milestone D-02's rationale. | |
| You decide | Pick the pairing that survives Phase 143's `--pulse-us` override. | |

**User's choice:** Both, whichever trips first
**Notes:** → CONTEXT D-07.

### Q3 — What counts as a valid TABLE-04 citation for a row spanning 170 chips?

| Option | Description | Selected |
|--------|-------------|----------|
| Named representative part + bench-inventory tie | One named part per row, chosen to be benchable in Phase 145, with a "representative of the row" scope clause. | |
| Cite the algorithm family, not a part | Cites what `protocol_id` actually names — but those specs live inside part datasheets anyway. | |
| Cite every distinct value observed across the row's chips | Exhaustive and maximally honest — but a survey over 329 chips, and TABLE-04 asks for attribution. | |
| You decide | Set the standard so a stranger can tell what the citation does and does not claim. | ✓ |

**User's choice:** You decide
**Claude's decision:** **Two-part citation with an explicit scope clause** — (a) the vendor algorithm
family by name, plus (b) one named representative part (manufacturer, part number, datasheet
revision) chosen to be benchable in Phase 145, plus the literal sentence *"representative of this
row; not asserted true of all N chips carrying this `protocol_id`."* Family-alone is unverifiable at
the bench; part-alone overclaims across 170 chips. → CONTEXT D-09.

### Q4 — What is `overprogram_cap_us`, and what happens when `3 × N × pulse` exceeds it?

| Option | Description | Selected |
|--------|-------------|----------|
| 75000 uniform; the cap clamps | `3 × 25 × 1000 µs`, the Intelligent worst case and the exact figure C3 was publicly stated against on gh#15. Overpulse = `min(3 × N × pulse, cap)`. Cited as reasoned, not datasheet-derived. | ✓ |
| 75000 uniform; exceeding it hard-fails | No byte silently under-receives — but turns a legal 3000 µs chip into a refusal, and LOOP-03 says "capped at". | |
| Per-row (0x07 → 75000, 0x08 → 7500) | Tightest ceiling per algorithm — but 7500 would routinely clamp 23 of the 127 measured 0x08 chips. | |
| You decide | Choose value and exceed-behavior together, keeping C3's public statement true. | |

**User's choice:** 75000 uniform; the cap clamps
**Notes:** → CONTEXT D-08.

**Continue check:** "Next area" — declined further questions on 0x07/0x08 `max_pulses`, 0x0B's
backstop figure, and `vpp_path` value naming.

---

## Consumption seam with Phase 141

Framing supplied: `eprom.cpp` has two protocol switches the table subsumes (`:71-76`, already settled
as staying; and the duplicated `0x0B || FLAG_VPE_AS_VPP` branch at `:145` / `:218`), and
`native_trace_v131` asserts full ordered positional equality against Phase 138's frozen trace.

### Q1 — Does Phase 140 wire the table into `eprom.cpp`, or ship it as data only?

| Option | Description | Selected |
|--------|-------------|----------|
| Data + gate + test only — nothing reads it yet | `eprom.cpp` byte-unchanged; `native_trace_v131` stays GREEN; first legitimate trace movement is Phase 141's. Risk: an unreferenced PROGMEM const can be elided. | ✓ |
| Wire the `vpp_path` branch now (`:145`, `:218`) | Removes real duplication and proves the table load-bearing — but any non-bit-identical mask emission turns the trace gate RED for three phases. | |
| Wire it, and re-baseline the trace inside Phase 140 | Nothing left RED — but a fixture re-frozen by whichever phase breaks it stops being evidence, and it moves the diff out of Phase 144 / TEST-06. | |
| You decide | Weigh proving load-bearing against a three-phase RED. | |

**User's choice:** Data + gate + test only
**Notes:** → CONTEXT D-10.

### Q2 — How do we prove the table is real and reachable rather than linker-elided?

| Option | Description | Selected |
|--------|-------------|----------|
| Accessor + native test as the only consumer; record AVR delta ~0 | `eprom_params_for()` shipped; garbage-collected on AVR, so Phase 140's flash delta is expected ~0 and the real cost lands in Phase 141. State the expectation so TEST-08 reconciles rather than reports a surprise. | ✓ |
| Assert the values from a committed data file, not from C | Reachability stops mattering — but adds a generated-artifact seam to firmware that has none, and codegen drift is a known hazard here. | |
| Force a reference with `__attribute__((used))` or a size assertion | Makes the delta real and measurable — but burns 42 B / 36 B of headroom on code nothing calls. | |
| You decide | Keep Phase 144's reconciliation honest without burning headroom. | |

**User's choice:** Accessor + native test only; record AVR delta ~0
**Notes:** → CONTEXT D-10 (consequence paragraph).

### Q3 — Where does the TABLE-03 fallback test run, given both pinned native envs are frozen at 141 cases / 17 suites?

Verified during the exchange: the live `scripts/baseline/size_baseline.json` asserts exactly
141 cases / 17 suites on both pinned envs, and `check_size_baseline.py`'s default mode is strict
byte-identity.

| Option | Description | Selected |
|--------|-------------|----------|
| A fifth dedicated env, on the `native_trace_v131` precedent | Names only its own suite; never folded into a pinned env; never in `default_envs`. Known cost F-138-05: both live gates are blind to it, so the suite must be run explicitly by name in this phase's verification. | ✓ |
| Add to an existing suite and re-baseline `size_baseline.json` | Real gate coverage under both DEV_TOOLS configurations — but mutates the live baseline mid-milestone, which Phase 138 went to deliberate lengths to avoid. | |
| Fold it into `native_trace_v131`'s existing suite | Zero new plumbing — but muddies what a RED there means in Phase 144. | |
| You decide | Balance real gate coverage against disturbing frozen baselines. | |

**User's choice:** A fifth dedicated env
**Notes:** → CONTEXT D-11.

**Continue check:** "Next area" — declined further questions on table file layout, accessor return
convention (PROGMEM pointer vs copied struct), and whether the accessor signature is frozen for
Phase 141.

---

## Proof machinery (TABLE-03/04/05)

Framing supplied: TABLE-05 forbids a new `chip_database.json` field, but that file lives in the other
repo. Two prior burns cited — app-side gates scanning firmware source fail open on renames (4× in
Phase 117), and `check_permitted_claims.py`'s `_HERE` resolved to the checker's own phase dir,
scanning nothing and exiting 0.

### Q1 — Where does the TABLE-05 gate live, and how does it reach across the repo boundary?

| Option | Description | Selected |
|--------|-------------|----------|
| Split: firmware half in `firestarter`, DB half in `firestarter_app` | Each gate commits in the repo it can see; no cross-repo path seam, so neither can fail open. Cost: Phase 140 becomes dual-repo and the DB half is scheduled here. | ✓ |
| One gate in `firestarter_app` reaching into firmware | Reuses `FIRESTARTER_FW_ROOT` / `meta_presence.py` — but this is the exact shape that failed open four times in Phase 117. | |
| One gate in the meta repo scanning both submodules | Simplest to reason about — but runs in no CI leg of either sub-repo, so it is a local-run obligation, not a gate. | |
| You decide | Pick the arrangement least able to fail open. | |

**User's choice:** Split across both repos
**Notes:** → CONTEXT D-12. Planner consequence recorded: `commits_land_in:` must name both
submodules; never inferred from `files_modified`.

### Q2 — What does the firmware half of the TABLE-05 gate actually assert?

| Option | Description | Selected |
|--------|-------------|----------|
| Pinned inventory of protocol-branch sites with an allowlist | Enumerates every site branching on `handle->protocol` in the EPROM path and pins it; a new site, or a branch on any other handle field, fails. Makes Phases 141/142's removals visible as inventory shrinkage. | ✓ |
| Assert the table is the only protocol-keyed data structure | Matches TABLE-05's words — but says nothing about a plain `if`/`switch`, which is how every existing selector is written. | |
| Assert `memory.cpp`'s dispatch chain is unchanged | Cheap and stable — but upstream of this phase; it would pass even if 140 added a selector inside `eprom.cpp`. | |
| You decide | Pick the assertion that catches a second selector in Phases 141-142, not just 140. | |

**User's choice:** Pinned inventory with an allowlist
**Notes:** → CONTEXT D-13.

### Q3 — Where do TABLE-04's per-value citations live, and is "no unattributed number ships" enforced or reviewed?

| Option | Description | Selected |
|--------|-------------|----------|
| Machine-readable sidecar, gate-enforced, C comments point at it | One entry per (row, column); a gate asserts the entry set exactly covers the table's cells. Turns TABLE-04 into an exit code. | ✓ |
| Inline C comments only, reviewed not gated | Zero drift by construction — but rests on inspection, which TABLE-05's own wording rejects. | |
| Prose markdown doc, reviewed not gated | Human-readable and matches this milestone's other evidence artifacts — but nothing detects a value changing without its citation following. | |
| You decide | Pick the arrangement where a number and its provenance cannot silently diverge. | |

**User's choice:** Machine-readable sidecar, gate-enforced
**Notes:** → CONTEXT D-14.

---

## Todo cross-reference

`todo.match-phase 140` returned 6 keyword matches. Presented with the assessment that none can be
folded, because Phase 140 wires nothing and changes no behavior, so a behavioral todo has no code
seam to land in.

| Option | Selected |
|--------|----------|
| None — record as reviewed | ✓ |
| Fold: skip VPP checks when VPP is unused (score 0.9) | |
| Fold: FM1608 byte-0 write / register cache elision (score 0.9) | |

**User's choice:** None — record as reviewed
**Notes:** All six recorded in CONTEXT `<deferred>` § "Reviewed Todos (not folded)" with the reason
each was declined.

---

## Claude's Discretion

Explicitly delegated during discussion:

- **The TABLE-04 citation standard** (Row values Q3, answered "You decide") — resolved as CONTEXT
  D-09: two-part citation with an explicit scope clause.

Left to Claude by omission (the operator declined the offered follow-up questions in all four
"more questions / next area" checks), recorded in CONTEXT § "Claude's Discretion":

- C types and widths per column, and struct field order.
- Table file layout (`include/` + `src/proms/` pair vs header-only) and the fifth native env's
  `-I` / `test_filter` naming.
- Whether `vpp_path` names abstract enum values or raw control-register masks.
- `eprom_params_for()`'s exact signature and return convention.
- `max_pulses` for 0x07 / 0x08 and 0x0B's backstop figure — research-settled under TABLE-04.
- The sidecar citation file's format and path; the DB-half gate's key-inventory form.
- Plan and wave structure.

## Deferred Ideas

Recorded in CONTEXT `<deferred>`: wiring the table into `eprom.cpp` (Phases 141/142); removing
`program_mismatched_bytes()` / `verify_and_update_mask()` / `NUMBER_OF_RETRIES` / the adaptive growth
formula (LOOP-02, Phase 141); the 32-bit-safe delay helper (LOOP-07, Phase 141); `--pulse-us` bounds
(HOST-01…05, Phase 143); trace re-baselining and flash-delta reconciliation (TEST-06 / TEST-08,
Phase 144); a possible 0x08 family split (finding for Phase 146); fixing F-138-05
(`check_size_baseline.py`'s uncaught KeyError on an unknown native env) — inherited, accepted, not
fixed, owner `henols`.

**No scope creep was raised during this discussion** — every area stayed inside TABLE-01…05.
