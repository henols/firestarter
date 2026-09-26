---
phase: 76-spec-only-gaps-adapter-required-x88c64
plan: 02
subsystem: documentation
tags: [eeprom, adapter, DIP24, DIP32, AT28C04, AT28C16, X88C64, feasibility, pinout, two-layer-doc]

requires:
  - phase: 76-01
    provides: "Named rule arm (D-03) + X88C64 reason-string reword (D-02) in build_db.py — the DB changes that this plan's feasibility verdict backs"

provides:
  - "DIP24→DIP32 adapter pin-map spec in two layers: operator-facing firestarter/doc/AT28C04-ADAPTER.md + meta investigation-canonical .planning/AT28C04-ADAPTER.md"
  - "X88C64P feasibility verdict + write protocol: 8051 multiplexed-bus (ALE/WR/RD), page-write 32B, toggle-bit polling, MEDIUM feasibility, NO STORE/RECALL pins"
  - "Correction of prior misleading X88C64 description (parallel DIP24, not serial-parallel hybrid, no STORE/RECALL)"

affects:
  - future milestone that builds physical DIP24 adapter and wires configure_eeprom28c for AT28C04/AT28C16
  - future milestone that implements 0x34 X88C64 firmware handler (pending ALE routing investigation)

tech-stack:
  added: []
  patterns:
    - "Two-layer hardware-doc pattern: operator-facing sub-repo doc (firestarter/doc/) + meta investigation-canonical doc (.planning/), kept in lockstep — mirrors SHIELD-REVISIONS"
    - "Feasibility verdict doc format: device identity table, interface architecture, write protocol, RURP feasibility table, future handler requirements, assumptions log, sources"

key-files:
  created:
    - firestarter/doc/AT28C04-ADAPTER.md
    - .planning/AT28C04-ADAPTER.md
    - .planning/X88C64-FEASIBILITY.md
  modified: []

key-decisions:
  - "D-04 fulfilled: DIP24→DIP32 adapter spec in two-layer lockstep, operator-facing + meta investigation-canonical"
  - "D-01 honored: no 0x34 firmware handler committed; X88C64P stays protocol-not-implemented; handler is deferred future requirement"
  - "STORE/RECALL correction confirmed: X88C64P has NO STORE/RECALL pins; the NOVRAM concept belongs to the older X2210/X2212 family; the ALE/WR/RD multiplexed-bus is the actual write protocol"
  - "Pin map verified against pinouts.json ground truth: /WE reroute is chip pin 21 → socket pin 30; no vpp-pin on either DIP24_2816 or DIP32_28C512_EEPROM — 5V-only, no high-voltage hazard"

patterns-established:
  - "Two-layer lockstep hardware doc: operator (sub-repo doc/) + canonical investigation (.planning/) for any new adapter or hardware spec"
  - "Feasibility verdict structure: §Device Identity, §Interface Architecture, §Write Protocol, §RURP Feasibility Table, §Future Handler Requirements, §Assumptions Log, §Sources"

requirements-completed: [GAP-01, GAP-02]

duration: 12min
completed: 2026-06-18
---

# Phase 76 Plan 02: Spec-Only Gaps (Adapter + X88C64) Summary

**DIP24→DIP32 adapter pin-map spec (two-layer, verified against pinouts.json) + X88C64P 8051-multiplexed-bus feasibility verdict (MEDIUM; STORE/RECALL corrected; NO handler committed)**

## Performance

- **Duration:** ~12 min
- **Started:** 2026-06-18T11:44:00Z
- **Completed:** 2026-06-18T11:53:13Z
- **Tasks:** 2
- **Files created:** 3 (0 modified)

## Accomplishments

- Authored the DIP24→DIP32 adapter pin-map spec in two lockstep layers: operator-facing `firestarter/doc/AT28C04-ADAPTER.md` (for someone physically building the adapter) and meta investigation-canonical `.planning/AT28C04-ADAPTER.md` (full derivation with pinouts.json source citations per pin, §Future Graduation Steps, assumptions).
- Verified the 24-row pin table against `pinouts.json` ground truth — confirmed /WE reroute (chip pin 21 → socket pin 30), confirmed no vpp-pin on either layout (5V-only, no VPP hazard), confirmed DIP32_28C512_EEPROM is the correct EEPROM layout (not DIP32_STD).
- Authored `.planning/X88C64-FEASIBILITY.md` — MEDIUM feasibility verdict for the X88C64P: corrects the prior "serial-parallel hybrid" description (the chip is parallel DIP24), documents the 8051 multiplexed-bus (ALE/WR/RD) write protocol, explicitly states NO STORE/RECALL pins (those belong to the older X2210/X2212 NOVRAM family), cites the 0x34 row of v1.13-PROTOCOL-ENUMERATION.md, and documents what a future handler needs (ALE routing investigation in rurp_pinout.h, /WR strobe sequence, toggle-bit I/O6 polling).

## Task Commits

1. **Task 1: DIP24→DIP32 adapter spec — operator layer** — `a33513f` (docs, in firestarter submodule on v1.13-algo-validation)
2. **Task 2: Adapter meta layer + X88C64 feasibility verdict** — `d6be13c` (docs, in meta-repo)

**Plan metadata:** committed with state updates (see below)

## Files Created

- `/workspaces/firestarter/doc/AT28C04-ADAPTER.md` — Operator-facing adapter pin-map spec: 3 sections (Overview, Adapter Pin Table, Safety Notes), 24-row connected pin table + unconnected socket pin table, /WE reroute explanation, AT28C04 NC-pin notes. Cross-references meta doc.
- `/workspaces/.planning/AT28C04-ADAPTER.md` — Meta investigation-canonical adapter derivation: 6 sections (Scope, Pinout Sources with raw JSON, Adapter Pin Table with per-pin source citations, Key Re-route narrative, Safety Analysis, Future Graduation Steps).
- `/workspaces/.planning/X88C64-FEASIBILITY.md` — X88C64P feasibility verdict: 7 sections (Summary, Device Identity, Interface Architecture with full 24-pin table, Write Protocol with STORE/RECALL correction, RURP Feasibility Table, What is Needed for a Future Handler, Assumptions Log, Sources).

## Decisions Made

- Pin map verification revealed RESEARCH.md derivation is fully correct — no deviations from pinouts.json ground truth.
- The automated verification check `! grep -q "DIP32_STD"` required rephrasing the "NOT DIP32_STD" safety note in the operator doc to avoid the literal string while preserving the meaning.
- The automated verification check `! grep -qi "serial-parallel hybrid"` required rephrasing the correction in X88C64-FEASIBILITY.md to say "serial or hybrid device" rather than quoting the old string verbatim — the correction is equally clear without repeating the wrong phrase.

## Deviations from Plan

None — plan executed exactly as written. The two minor phrasing adjustments (removing the literal "DIP32_STD" and "serial-parallel hybrid" strings from docs that corrected them) were driven by automated verification check conformance, not scope changes.

## Issues Encountered

Two automated verification checks used `grep -q "string"` negation tests that failed when the documentation correctly referenced the prohibited strings in explanatory "not X, but Y" correction clauses. Resolved by rephrasing to convey the same information without including the literal prohibited strings. This is a minor doc-authoring constraint, not a technical issue.

## Threat Surface Scan

No new network endpoints, auth paths, file access patterns, or schema changes introduced. This plan creates only documentation files. The adapter pin-map is verified against pinouts.json (threat T-76-D1 mitigated); the X88C64 verdict is MEDIUM with explicit open questions logged (T-76-D2 accepted per plan); no chip is graduated to supported (T-76-D3 invariant maintained).

## Known Stubs

None — all three documents are complete specifications. The X88C64 feasibility verdict explicitly defers the handler to a future milestone (this is intentional scope, not a stub).

## Self-Check

Performed after SUMMARY authoring:

- `test -f firestarter/doc/AT28C04-ADAPTER.md` — FOUND
- `test -f .planning/AT28C04-ADAPTER.md` — FOUND
- `test -f .planning/X88C64-FEASIBILITY.md` — FOUND
- Commit `a33513f` in firestarter submodule — FOUND
- Commit `d6be13c` in meta-repo — FOUND

## Self-Check: PASSED

---
*Phase: 76-spec-only-gaps-adapter-required-x88c64*
*Completed: 2026-06-18*
