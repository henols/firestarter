# Phase 148: Numeric Database Values & the AT28C VCC Decode - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-08-18
**Phase:** 148-Numeric Database Values & the AT28C VCC Decode
**Areas discussed:** VCC decode target & condition · Blast-radius proof (diff_db + goldens) ·
Pulse sentinel + 2nd coercion site · Human output contract (firestarter info)

---

## Area Selection

| Option | Description | Selected |
|--------|-------------|----------|
| VCC decode target & condition | Is `"4V"` a defect or a faithful decode of a test rail? Target value, condition shape, requirement hand-correction | ✓ |
| Blast-radius proof (diff_db + goldens) | diff_db classifies by literal field names against a pinned baseline; a key rename makes all 746 chips diff unexplained | ✓ |
| Pulse sentinel + 2nd coercion site | `pulse_duration_us: 0` conflates two states; `audit_coverage_matrix.py` has its own string parser DATA-03 does not name | ✓ |
| Human output contract (firestarter info) | `ic_layout.py:568` renders `"5.0v"` off the coerced float; the characterization snapshot pins it | ✓ |

**User's choice:** all four.

---

## VCC decode target & condition

### Q1 — What value should the AT28C family's VCC decode to, and on what basis?

| Option | Description | Selected |
|--------|-------------|----------|
| 5000 mV (= `vdd`) — extend the SRAM precedent | Treat minipro's `vcc` as the TL866 low-margin verify rail. `vdd` is itself an infoic-decoded value, so nothing is invented. Requires hand-correcting DATA-01 + ROADMAP criterion #1 off "4.5 V". | ✓ |
| 4500 mV — DATA-01 as written | Matches the requirement verbatim, no requirement edit — but AT28C's infoic VCC nibble is `2` (=4V), not `3` (=4.5V), so 4500 is a value infoic does not carry. Also a datasheet *minimum* where every other row reports the applied supply. | |
| Semantic re-derivation — stop surfacing `vcc` as operating VCC | The honest reading applied to all 746 chips. Widest blast radius; UV-EPROM `vdd` is the 6.5 V program rail on 105 chips and must never become the "VCC:" row. | |

**User's choice:** 5000 mV (= `vdd`).
**Notes:** Recorded as CONTEXT D-01/D-02, with D-04 mandating a Phase-147-D-06-style hand-correction
of DATA-01 and ROADMAP criterion #1 before planning.

### Q2 — Where should the condition live?

Presented **after** measuring the candidate conditions against the live database — the measurement
materially changed the option set, since `vcc != vdd` on **358 of 746** chips and every
type/algorithm-keyed rule would set sixteen 5 V Microchip EEPROMs to **3.3 V**.

| Option | Description | Selected |
|--------|-------------|----------|
| Nibble-keyed semantic rule — "4V is never an operating supply" | `vcc_mv == 4000 → vcc_mv = vdd_mv`. Keys on nothing chip-specific. Blast radius exactly **56** chips, all landing on 5000 mV. | ✓ |
| Narrow intersection — EEPROM-class AND 4000 AND vdd 5000 | Blast radius 55; excludes the XICOR X88C64 outlier. Three conditions to cite instead of one. | |
| Fix both anomalies — 4000 AND the 5500-vs-3300 group | ~85 chips, but what 5500/3300 encodes is unproven without infoic research. Beyond DATA-01's target. | |
| Set the ceiling now, let research pick the rule | Lock only the guardrail (≤60 movers, all landing on 5000, no rule may lower a VCC). Slower. | |

**User's choice:** Nibble-keyed semantic rule.
**Notes:** Recorded as CONTEXT D-03, carrying the four-way split table as the load-bearing
measurement. Measured blast radius of the rejected conditions: type-keyed 85, algorithm-keyed 84,
relation-keyed 225.

### Q3 — What happens to the 29 EEPROM-class chips reading `vcc=5500`?

| Option | Description | Selected |
|--------|-------------|----------|
| Out of scope, filed as a todo with the measurement | Name it in CONTEXT, file a pending todo with exact counts and part list, state the non-claim in the diff justification. Defer-with-owner shape. | ✓ |
| Out of scope, silent | Smallest artifact surface, but a measured defect found during the phase leaves no record. | |
| Add a regression guard so no rule can lower a VCC | Todo plus a non-vacuous assertion (no `vcc_mv` < 4500; 56 movers pinned; no VCC ever decreases). More work; guard outlives the phase. | |

**User's choice:** Out of scope, filed as a todo with the measurement.
**Notes:** The regression-guard option was captured in CONTEXT `<deferred>` as considered-and-declined,
with the note that it would have caught the rejected type-keyed rule's 3.3 V failure.

### Q4 — Does `vdd` survive the numeric migration?

| Option | Description | Selected |
|--------|-------------|----------|
| Keep as `vdd_mv` — load-bearing generator input | Read by the new 4V rule, the SRAM block, and diff_db's classification. Not the `protect_on_after` dead-data shape. | ✓ |
| Keep `vdd_mv` and surface it in `firestarter info` | Makes the 5500 anomaly visible to any user — but adds a display field DATA-02 does not ask for, and UV-EPROM `vdd` is the 6.5 V program rail. | |
| Collapse it — emit only the resolved `vcc_mv` | DATA-02 read strictly, but destroys diff_db's two-rail classification and the evidence trail for both normalizations. | |

**User's choice:** Keep as `vdd_mv`.
**Notes:** Recorded as CONTEXT D-05.

---

## Blast-radius proof (diff_db + goldens)

### Q1 — How do we keep the proof artifact legible across a key rename?

| Option | Description | Selected |
|--------|-------------|----------|
| Normalizing comparator — the migration shows zero diffs | Canonicalize both sides to mV/µs before comparing, so `"5V" == 5000`. The migration produces literally zero rows; only the 56 VCC movers surface. Baseline stays pinned. | ✓ |
| Two sequential passes with a schema rule label | Conventional diff_db mechanics, but produces a 746-row "explained" artifact a reviewer cannot check, and re-pins the baseline. | |
| Both — comparator AND a re-pinned baseline | Leaves the tool simpler for Phase 149 onward; more work now. | |

**User's choice:** Normalizing comparator.
**Notes:** Recorded as CONTEXT D-11. A `RULE_VCC_MARGIN_RAIL` `_RATIONALES` entry is still required
for exit 0 — noted as mechanical, not a choice.

### Q2 — How is `tests/golden/chip_database_field_inventory.json` re-derived?

| Option | Description | Selected |
|--------|-------------|----------|
| Independent re-derivation + a seen-to-fail transcript | Fresh traversal and fresh AST walk per the golden's own `how_to_update`, plus plant-and-revert RED/GREEN transcripts. Precedent: Phase 140 Plan 03. | ✓ |
| Independent re-derivation, no planted-violation proof | Relies on the Phase 140 fail proof still holding after the key set changed. | |
| Re-derivation + also assert the rename is total | Adds a positive assertion that no unit-suffixed string field survives — DATA-02's exact wording. | |

**User's choice:** Independent re-derivation + a seen-to-fail transcript.
**Notes:** Recorded as CONTEXT D-13.

### Q3 — Where does DATA-05's committed diff artifact live?

| Option | Description | Selected |
|--------|-------------|----------|
| A phase-dir file: `148-DB-DIFF.md` | Run output, 56-chip mover list, justification, explicit non-claim about the 5500 group. Reviewable whole. | ✓ |
| Inside the plan SUMMARY.md that lands the change | No new artifact type, but evidence splits across plan boundaries and SUMMARY.md is not where anyone looks later. | |
| A new committed rule in `diff_db.py` itself | Justification travels with the code and prints on every run — but no home for the mover list or the non-claim. | |

**User's choice:** `148-DB-DIFF.md`.
**Notes:** Recorded as CONTEXT D-12. The `_RATIONALES` entry is required regardless (D-11).

### Q4 — How is criterion 3 (same effective values) proven?

| Option | Description | Selected |
|--------|-------------|----------|
| Full 746-chip wire-dict equivalence, before vs after | `convert_to_programmer` is the single seam and has five keys. Total proof in one assertion, and cheap. | ✓ |
| Per-protocol representative sample | Readable in review, but a decode change moving only chips outside the sample passes silently. | |
| Rely on the existing suite plus GATE-03 | GATE-03 only checks `vpp_mv` against family bands; a `pulse-delay` regression passes it. | |

**User's choice:** Full 746-chip wire-dict equivalence.
**Notes:** Recorded as CONTEXT D-14. Confirmed during discussion that `vcc` and `vpp_volts` never
reach the wire and `dispatch_baseline.json` carries no voltage or timing field — so GATE-03 needs
no edit, satisfying criterion 4's "without any edit to the gate itself".

---

## Pulse sentinel + 2nd coercion site

### Q1 — How is the algorithm-controlled pulse sentinel represented?

| Option | Description | Selected |
|--------|-------------|----------|
| `0`, and make the decode fault impossible to land silently | Keep the seed's `0`, but make `interpret_timing`'s unparseable branch fatal instead of defaulting to `0`. Then `0` has one meaning by construction. | ✓ |
| `0`, exactly as the seed decided — nothing else | Smallest change, but a build emitting a wrong `0` still succeeds and the WARN scrolls past in CI. | |
| Omit the key entirely for algorithm-controlled chips | Typed absence rather than a magic `0` — but creates a 329/746 sparse key, the hard case the field-inventory golden warns about. | |

**User's choice:** `0` + fatal decode fault.
**Notes:** Recorded as CONTEXT D-08. Confirmed during discussion that `ic_layout.py:603-607`
**already** omits the "Pulse delay:" row on `0`, so no display work is needed for the sentinel.

### Q2 — What happens to `audit_coverage_matrix.py`'s `parse_pulse_us`?

| Option | Description | Selected |
|--------|-------------|----------|
| Delete it too — same discipline as `database.py` | ~8 call sites read `pulse_duration_us` directly; the `:1718` `endswith(" us")` filter becomes `!= 0`; golden regenerated. | ✓ |
| Keep it, widen it to accept ints | Smaller diff — but precisely the "bypassed, not gone" shape DATA-03 forbids. | |
| Out of scope — do not touch the audit tool | Not a deferral: its test suite imports it and runs it against the live regenerated database, so it would be a red suite at the end of the phase. | |

**User's choice:** Delete `parse_pulse_us` too.
**Notes:** Recorded as CONTEXT D-09. Discovered during discussion that the tool's `_REPO_ROOT`
resolves to `/workspaces` (the **meta** repo), so `DEFAULT_OUTPUT` and `DEFAULT_LEDGER` are tracked
meta-repo files the tool mutates. Captured as an execution-mechanics landmine in CONTEXT.

### Q3 — What does the user see when a stale `~/.firestarter/database.json` override stops loading?

| Option | Description | Selected |
|--------|-------------|----------|
| Detect the old shape and fail with a named migration error | A detect-and-refuse path is not a coercion layer — it reads only to reject. Names file, field, and new schema. | |
| Silent clean break — whatever error falls out | Exactly the seed's design, nothing more. Smallest surface. Beta is explicitly unstable. | ✓ |
| Detect, warn loudly, and ignore the override | User keeps working but silently without the override they wrote. | |

**User's choice:** Silent clean break.
**Notes:** Recorded as CONTEXT D-10. Refined by Q4 below.

### Q4 — Which way should the break land: raise, or silently yield `0`?

| Option | Description | Selected |
|--------|-------------|----------|
| Direct indexing — the break raises, no message added | `chip["electrical"]["vcc_mv"]` rather than `.get(k, 0)`, so a stale override raises rather than resolving `pulse_duration_us` to `0` (= algorithm-controlled) and programming a 0x07 chip with no pulse. | ✓ |
| Whatever the natural implementation does | Truly minimal instruction, but leaves the silent-wrong-value case open. | |

**User's choice:** Direct indexing.
**Notes:** Folded into CONTEXT D-10. Adds no surface and is not a coercion layer — absent key ⇒
exception, never a valid-looking value.

---

## Human output contract (firestarter info)

### Q1 — What format does the mV→string render helper emit?

| Option | Description | Selected |
|--------|-------------|----------|
| Byte-identical to today — `"5.0v"`, `"12.0v"`, `"4.5v"` | The characterization snapshot then changes on exactly the AT28C lines, and that diff *is* the proof. | ✓ |
| Datasheet style — `"5V"`, `"12.5V"`, `"4.5V"` | Nicer output, but re-baselines every voltage line and buries the one line that matters. | |
| Byte-identical now, file the format change as a todo | Same as the first, plus a recorded intent. | |

**User's choice:** Byte-identical to today.
**Notes:** Recorded as CONTEXT D-15. The follow-up-todo variant was **not** taken — the format
change is recorded in `<deferred>` as considered-and-declined, not deferred.

### Q2 — Where does the helper live?

| Option | Description | Selected |
|--------|-------------|----------|
| One shared helper in `database.py` | Beside the code that owns the millivolt convention, in the file the coercion layer is deleted from. One clean reversal. | ✓ |
| In `ic_layout.py`, imported by `eprom_info.py` | Next to two of three call sites, but puts a display convention in a pin-diagram module. | |
| A small dedicated formatting module | Cleanest separation, but a new file for one function. | |

**User's choice:** One shared helper in `database.py`.
**Notes:** Recorded as CONTEXT D-16. Three call sites: `ic_layout.py:568`, `ic_layout.py:597`,
`eprom_info.py:401`.

### Q3 — Does anything need to say why VCC changed on an AT28C part?

| Option | Description | Selected |
|--------|-------------|----------|
| Nothing in the CLI — record it in `148-DB-DIFF.md` and the changelog | The output just becomes correct. Nothing in the CLI acquires a note that would need removing later. | ✓ |
| Changelog only — no phase artifact note | Separates the user-facing statement from the evidence that justifies it. | |
| Also surface the correction in `dev test` report output | Strongest traceability — but a new report field with no consumer, the dead-data shape Phase 147 explicitly rejected, and it is Phase 147's file. | |

**User's choice:** Nothing in the CLI.
**Notes:** Recorded as CONTEXT D-17. The changelog entry must cover both the AT28C VCC correction
and the **breaking** numeric schema.

---

## Claude's Discretion

- Exact name of the D-03 margin-rail constant and the D-16 render helper (`_VCC_MARGIN_RAIL_MV`,
  `format_mv` are suggestions).
- Exact failure mechanism for D-08's fatal branch (`SystemExit` vs a raised exception).
- Whether the migration and the D-03 rule land in one plan or two.
- Fixture format and location for D-14's wire-dict capture.
- Deleting the now-dead `vpp_volts` fallback in `convert_to_programmer` (`database.py:544-546`).

## Deferred Ideas

- The `vcc = 5500` EEPROM-class group — 29 chips (16 Microchip at `vcc 5500 / vdd 3300`,
  13 EXEL+ST at `vcc 5500 / vdd 5000`). Same category error inverted. File as a pending todo with
  the exact counts and part list; state the non-claim in `148-DB-DIFF.md`.
- A regression guard over the regenerated database (no `vcc_mv` < 4500; 56 movers pinned; no VCC
  ever decreases). Considered and declined; revisit with the 5500 group.
- Datasheet-style voltage rendering. Declined, not deferred.
- Surfacing `vdd` in `firestarter info`. Rejected.

## Deferred / Reviewed Todos

20 pending todos cross-referenced; **none folded**. Closest matches were
*Decode infoic.xml flags bits 14/15* (→ DATA-06, **Phase 150**), *`build_db_diff`'s `ladder_state`*
(actually `diagnostic_report.py`, defer-with-owner from v1.30 C-1), *AT28C256 write-path failure
gh#20* (Backlog 999.29, blocked by the Evidence Ceiling), *Reply on gh#12* (→ **Phase 152**), and
*Land `write --sdp-relock`* (→ **Phase 150**). Full list in CONTEXT.md `<deferred>`.
