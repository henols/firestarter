# Requirements: Firestarter — v1.19 Protocol Naming & Labels

**Defined:** 2026-07-01
**Core Value:** Algorithm-first dispatch — minipro `protocol_id` flows authoritative from upstream XML → DB → wire JSON → firmware handler. v1.19 keeps that contract byte-for-byte (numbers unchanged) and layers a correct, human-readable **name** on top of every protocol so the firmware code and the host display are legible without a hex lookup.

## Milestone Framing

Readability milestone. **No `chip_database.json` change, no wire-protocol change, no lockstep-constant change, no new CLI input grammar.** Raw protocol numbers are preserved everywhere (DB `programming.algorithm`, wire JSON, host internal logic). Names/labels are added on top. Host display translation and firmware labeling are two **independent** refactors sharing one operator-approved name set (not a lockstep milestone). Golden register traces + the dispatch-mirror guard stay byte-identical.

## v1 Requirements

Requirements for this milestone. Each maps to exactly one roadmap phase.

### NAME — Canonical Protocol Name Set

- [ ] **NAME-01**: A single canonical protocol name set is authored covering every protocol number present in `chip_database.json` (0x05, 0x06, 0x07, 0x08, 0x0B, 0x0D, 0x0E, 0x10, 0x27, 0x28, 0x29, 0x34, plus the phantom IDs 0x35/0x39), each name human-readable and behavior/datasheet-correct, revisiting the v1.16 `PROTOCOLS.md` col-2 vocabulary.
- [ ] **NAME-02**: The final name set is presented to and approved by the operator before it is applied to firmware, host, or docs (blocking approval gate).
- [ ] **NAME-03**: The approved names are recorded in one authoritative source that firmware labels, host display, and doc prose all conform to (single source of truth for the vocabulary).

### FW — Firmware Labels & Handler Renames

- [ ] **FW-01**: Every protocol number is defined as a named constant (or enum) in the firmware headers; the numeric values are unchanged (the label *is* the number).
- [ ] **FW-02**: `memory.cpp` dispatch and the handler bodies reference protocols by the named labels instead of magic hex literals, so it is obvious at a glance which protocol is in play; firmware still works with the numbers.
- [ ] **FW-03**: The mechanism-jargon handlers/files (`configure_flash3`/`flash_type_3.cpp`, `configure_flash4`/`flash_type_4.cpp`, `configure_eeprom28c`) are renamed to readable family names from the approved vocabulary, keeping the existing many-to-one dispatch (0x07/0x08/0x0B → one EPROM handler; 0x0E/0x27/0x28/0x29 → one SRAM handler).
- [ ] **FW-04**: Firmware behavior is unchanged — the per-family golden register traces and the dispatch-mirror guard are byte-identical pre/post, the native Unity suite is green, and the Leonardo flash delta is near-zero (no regression against the ~88% ceiling).

### HOST — Display Translation

- [ ] **HOST-01**: The host translates protocol numbers → the approved human-readable names at display time in `info`/`list`/`search`.
- [ ] **HOST-02**: The scattered in-code protocol maps (`ic_layout.py` `proto_display` / `protocol_info_data`, `eprom_info.py`) are consolidated and corrected to the single approved name set.
- [ ] **HOST-03**: Host internal logic continues to operate on the plain protocol numbers (no per-protocol special-case handling added); the host test suite and ruff/mypy CI (py3.11 target) stay green.

### DOC — Documentation Reconciliation

- [ ] **DOC-01**: `firestarter/doc/PROTOCOLS.md` prose and the INV traceability matrix are reconciled to the final approved names.
- [ ] **DOC-02**: `datasheets/<hex>-<NAME>/` folder slugs are left unchanged (renamed only on explicit operator instruction); any name↔slug divergence is documented rather than silently applied.

### GATE — Non-Regression Invariants

- [ ] **GATE-01**: No `chip_database.json` schema or value change — protocol numbers preserved; `diff_db.py` reports IDENTITY and `check_dispatch.py` reports 0 violations.
- [ ] **GATE-02**: No wire-protocol or lockstep-constant change (this is not a lockstep milestone); `constants.py` ↔ `firestarter.h` parity is unaffected.
- [ ] **GATE-03**: No new user-facing CLI input grammar — users still select chips by part number, not by protocol name/alias.

## v2 Requirements

Deferred / acknowledged, not in this milestone's roadmap.

### NAME (future)

- **NAME-F1**: Rename the `datasheets/<hex>-<NAME>/` folder slugs to match a revised vocabulary (deferred — avoids folder/provenance churn; only if operator later requests it).
- **NAME-F2**: Accept the protocol name/alias as CLI input (filter/select by protocol name) — explicitly out of scope for v1.19 (see Out of Scope); revisit if operator UX demand emerges.

## Out of Scope

Explicitly excluded. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| Any `chip_database.json` schema or value change (alias field, renumbering) | Operator directive: "the database stays the same, the protocol numbers are preserved there." Numbers remain authoritative. |
| Wire-protocol / lockstep-constant change | Names are code-and-display only; nothing crosses the wire. Keeps this a non-lockstep milestone. |
| New CLI input grammar (select/filter chips by protocol name) | Operator scoped this to display + code readability only; chip selection stays by part number. |
| Splitting the many-to-one handlers into one function per protocol | Larger refactor, flash cost on the ~88% Leonardo ceiling, changes golden traces. Keep the family structure. |
| `datasheets/` folder-slug renames | Provenance/index churn; left as-is unless operator instructs otherwise (tracked as NAME-F1). |
| Domain research | Internal naming/refactor on the already-researched, datasheet-verified v1.16 vocabulary. |

## Traceability

Which phases cover which requirements. Populated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| NAME-01 | 100 | Pending |
| NAME-02 | 100 | Pending |
| NAME-03 | 100 | Pending |
| FW-01 | 101 | Pending |
| FW-02 | 101 | Pending |
| FW-03 | 101 | Pending |
| FW-04 | 101 | Pending |
| HOST-01 | 102 | Pending |
| HOST-02 | 102 | Pending |
| HOST-03 | 102 | Pending |
| DOC-01 | 103 | Pending |
| DOC-02 | 103 | Pending |
| GATE-01 | 103 | Pending |
| GATE-02 | 103 | Pending |
| GATE-03 | 103 | Pending |

**Coverage:**
- v1 requirements: 15 total
- Mapped to phases: 15 (Phase 100: NAME-01..03; Phase 101: FW-01..04; Phase 102: HOST-01..03; Phase 103: DOC-01/02, GATE-01..03)
- Unmapped: 0 ✓

---
*Requirements defined: 2026-07-01*
*Last updated: 2026-07-01 at milestone v1.19 start*
