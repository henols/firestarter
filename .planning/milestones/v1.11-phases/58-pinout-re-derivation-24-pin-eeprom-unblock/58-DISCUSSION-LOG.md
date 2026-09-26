# Phase 58: Pinout Re-derivation + 24-pin EEPROM Unblock - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-06-08
**Phase:** 58-pinout-re-derivation-24-pin-eeprom-unblock
**Areas discussed:** Re-derivation diff posture, Pinout derivation (data-driven from minipro masks), DIP24_2816 EEPROM pinout, Citations, SR-1 checklist

---

## Re-derivation diff posture

| Option | Description | Selected |
|--------|-------------|----------|
| Diff-minimal (constrained) | Reproduce every existing chip exactly; only the 9 new chips change; flag would-be reassignments for sign-off | |
| Correctness-first (unconstrained) | Apply principled rules even where they reassign existing chips; each change cited for Phase 59 | ✓ |
| Hybrid: minimal + flagged corrections | Diff-minimal except auto-apply safety-relevant reassignments | |

**User's choice:** Correctness-first (unconstrained).
**Notes:** Accept a larger Phase 59 GATE-02 diff for a maximally source-correct DB.

## Guess tables disposition

| Option | Description | Selected |
|--------|-------------|----------|
| Delete entirely | Principled function is sole source; no dual lookup | ✓ |
| Keep as cited fallback | Tables survive only for irregular chips, each upgraded to a citation | |
| You decide at plan time | Per-table planner call | |

**User's choice:** Delete entirely.

## Safety overrides relationship

| Option | Description | Selected |
|--------|-------------|----------|
| Keep as explicit override layer | WARNING-5/fm1608/skip stay as named, separately-tested guards | |
| Fold into principled rules | Express safety logic inside the dispatch | |
| You decide at plan time | Per-override planner call | |
| Other (freeform) | — | ✓ |

**User's choice (freeform):** "it shall only be allowed to add overrides in the user config folder the rest shall be removed."
**Notes:** Reframed as: overrides become natural rule OUTCOMES (no hardcoded patches in build_db.py); the only per-chip override seam is `~/.firestarter/database.json`; GATE-03 (check_dispatch.py) = 0 violations is the safety proof gate. Confirmed "Yes, exactly."

## Unclassifiable-chip fail-safe

| Option | Description | Selected |
|--------|-------------|----------|
| Skip with a loud warning | Drop the chip from the DB with a WARN naming it | |
| Emit with safest dispatch | Emit but force a non-VPP/safe handler when uncertain | |
| You decide at plan time | Planner picks, no uncertain chip emits a VPP-asserting dispatch | ✓ |

**User's choice:** You decide at plan time (hard constraint: no VPP-on-uncertain).

## Pinout derivation scope (operator steer)

| Option | Description | Selected |
|--------|-------------|----------|
| Selection only (rules data-driven) | General key-selection function; pinouts.json stays curated | |
| Derive layout from minipro too | Build physical layout from minipro pin_map/gnd/vcc masks; pinouts.json shrinks | ✓ |
| You decide from feasibility | Researcher determines | |

**User's choice:** Derive layout from minipro too.
**Notes:** Triggered by freeform steer "the pin maps must be easily found and mapped without any special code for any IC when the database is built." Maximally data-driven; D-04 feasibility flagged as top research question; skip-with-warning fail-safe covers gaps.

## DIP24 pinout for the AT28C04/16 family

| Option | Description | Selected |
|--------|-------------|----------|
| Add dedicated DIP24_2816 EEPROM pinout | New pinouts.json entry, EEPROM-named, SR-1 comment | ✓ |
| Reuse DIP24_6116 as-is | Point chips at existing SRAM-named entry | |
| Reuse + re-comment DIP24_6116 | Broaden one entry to cover SRAM + EEPROM | |

**User's choice:** Add dedicated DIP24_2816 EEPROM pinout.

## Family coverage (one entry vs split)

| Option | Description | Selected |
|--------|-------------|----------|
| One entry, over-allocated + mem_size | Full 11-line bus, firmware restricts by mem_size (32-pin precedent) | |
| Split per address width | Separate entries if datasheets diverge on pin assignment | |
| You decide at plan time | Researcher checks datasheets | ✓ |

**User's choice:** You decide at plan time.

## Citation standard

| Option | Description | Selected |
|--------|-------------|----------|
| minipro mask = primary citation | Mask the derivation reads is the citation (D-05/D-06 convention) | |
| minipro mask + datasheet cross-check | Require both, tagged CONFIRMED/INFERRED | |
| You decide at plan time | Mask primary, datasheet where ambiguous | |
| Other (freeform) | — | ✓ |

**User's choice (freeform):** "remove the local verified list, not needed."
**Notes:** The "one-rom verified" annotations die with the tables; minipro mask decode is the sole grounding; SC#1 satisfied by construction.

## SR-1 checklist home

| Option | Description | Selected |
|--------|-------------|----------|
| Phase artifact (.planning) | Audit trail in the phase folder | |
| Committed doc in firestarter_app/doc/ | GitHub-visible shipped doc | |
| Both: doc + planning record | Two-layer pattern (shield-revision precedent) | ✓ |

**User's choice:** Both: doc + planning record.

## SR-1 scope

| Option | Description | Selected |
|--------|-------------|----------|
| Every pinout the re-derivation changes | DIP24_2816 + any reassigned existing pinout | ✓ |
| New/unblocked pinouts only | DIP24_2816 + genuinely new entries; GATE-03 covers rest | |
| You decide at plan time | Planner scopes to VPP-decision points | |

**User's choice:** Every pinout the re-derivation changes.

---

## Claude's Discretion

- Unclassifiable-chip fail-safe mechanism (skip vs. safest-emit), subject to no-VPP-on-uncertain.
- AT28C04/16 family coverage: one over-allocated entry vs. split, from datasheet evidence.
- SR-1 artifact filenames/paths; internal structure of the principled rule function; reach of D-04 layout-derivation before falling back to curated rows.

## Deferred Ideas

- BENCH-01 real-hardware validation of the unblocked EEPROMs — deferred to v2 per REQUIREMENTS.md.
- Full pinouts.json generation/elimination if D-04 succeeds broadly — future refactor, out of scope for Phase 58.
