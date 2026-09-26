# Phase 60: Display-Layer Decode Correctness - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-06-10
**Phase:** 60-display-layer-decode-correctness
**Areas discussed:** Type label, Can-erase line, Plumbing, Tests, + operator-folded scope (NOT-VERIFIED removal, full `info` audit, protocol/flags correctness)

---

## Type label (displayed chip "Type")

| Option | Description | Selected |
|--------|-------------|----------|
| electrical.type drives family + keep protocol detail | family from electrical.type, protocol/voltage appended as supplementary | |
| Curated label map keyed on electrical.type | `{electrical.type → display string}` map is the sole Type source; protocol detail moves to protocol_info block only | ✓ |
| Show raw electrical.type verbatim | display the DB string as-is | |

**User's choice:** Curated label map keyed on electrical.type.
**Notes:** → D-01. Protocol/voltage detail leaves the Type label and lives only in the `protocol_info` block.

---

## "Can be erased" line

| Option | Description | Selected |
|--------|-------------|----------|
| Two facts: erasable=yes + firmware caveat | show physical erasability + "firestarter erase not yet supported" | |
| Single string with inline caveat | one line folding both facts | |
| Erasability + reference the backlog item | state erasability and point to firmware backlog | |
| (free-text) | "Display if it can be erased and don't care about the firmware" | ✓ |

**User's choice:** Free-text — report electrical erasability only; do not tie the line to firmware command support.
**Notes:** → D-02. Intentionally simplifies ROADMAP success-criterion 2 (no inline firmware caveat). Firmware erase gap stays a separate backlog item.

---

## Plumbing (where ic_layout reads electrical.type)

| Option | Description | Selected |
|--------|-------------|----------|
| Thread electrical.type through _map_data + fix flag | add mapped field, fix erasable derivation, precedence/fallback | |
| ic_layout reads the raw electrical block | pass/lookup raw electrical dict into presenter; leave _map_data fields alone except the flag bug | ✓ |

**User's choice:** ic_layout reads the raw electrical block.
**Notes:** → D-03. Still fix the stale `== "Flash/EEPROM"` erasable-flag match in `_map_data` (never fires for real `"EEPROM"` records).

---

## Tests

| Option | Description | Selected |
|--------|-------------|----------|
| Roadmap chips + control, against real DB | real-DB assertions only | |
| Synthetic fixtures (one per electrical.type) | isolated units + one real-DB smoke | |
| Both: synthetic units + real-DB smoke set | synthetic units drive logic; parametrized real-DB smoke for 4 EEPROMs + 3 UV controls | ✓ |

**User's choice:** Both.
**Notes:** → D-04. EEPROM set: W27C512, SST27VF512, SST27SF512, W27C257. UV controls: M27C512, 27C256, 2764 (`M2764` is not a DB part_number).

---

## Operator-folded additions (free-text directives during discussion)

- "the Eprom Info `-- NOT VERIFIED --` shall be removed" → **D-05** (remove the `verified_str` marker).
- "everything that has to do with the eprom info" → **D-06** (scope = the complete `firestarter info` output, audited for correctness/not-misleading; also confirm `info` does not crash for any in-DB chip).
- "Also make sure that the explanation of the protocol and the flags are correct" → **D-07** (audit/fix `protocol_info` + `flags_info`: the 0x10 bit semantic collision, missing erasable property, dead `_interpret_flags` entries, VPP never shown, protocol description accuracy).

## Claude's Discretion

- Exact display strings in the curated label map and the can-erase line wording (within D-01/D-02 rules).
- Whether to drop `verified_str` entirely vs blank it / remove the output row (D-05).
- Fallback label when `electrical.type` is absent/empty (legacy override DBs) — fall back to protocol-based label, don't crash.

## Deferred Ideas

- Firmware electrical-erase support (`firestarter erase W27C512`) — separate firmware backlog item; out of scope.
- Full fix of the `vpp-pin` list-vs-int TypeError (GATE-1.8b / v1.9) — appears already mitigated; only touch if it blocks the D-04 smoke tests.
