# Phase 100: NAME — Canonical Protocol Name Set + Operator Approval - Context

**Gathered:** 2026-07-01
**Status:** Ready for planning

<domain>
## Phase Boundary

Author the **single canonical, human-readable, behavior/datasheet-correct name** for every
protocol number present in `chip_database.json` (0x05, 0x06, 0x07, 0x08, 0x0B, 0x0D, 0x0E,
0x10, 0x27, 0x28, 0x29, 0x34, plus the phantom IDs 0x35/0x39), get the operator to explicitly
approve it (blocking gate — no silent auto-approval), and record it as the ONE authoritative
source that Phase 101 (firmware labels), Phase 102 (host display), and Phase 103 (docs) all
cite as their single source of truth.

This is a **naming/decision phase** — the deliverable is a vocabulary, not code. Its output
gates every other phase in v1.19; no firmware/host/doc work begins before it closes.

**In scope:** the name set + its authoritative recording in `firestarter/doc/PROTOCOLS.md` +
the operator-approval gate. **Out of scope (this phase):** applying the names to firmware
(Phase 101), host display (Phase 102), or doc prose/INV-matrix reconciliation (Phase 103); any
`chip_database.json` change; any wire/lockstep-constant change; new CLI grammar (see
`.planning/REQUIREMENTS.md` §Out of Scope). Requirements covered: NAME-01, NAME-02, NAME-03.

</domain>

<decisions>
## Implementation Decisions

### Entry Schema (per protocol)
- **D-01:** Each protocol entry is **structured with 3 fields**, so each downstream consumer
  reads one field with no re-derivation:
  1. a **C-identifier-safe constant token** (Phase 101 firmware `#define`/enum),
  2. a **short human display name** (Phase 102 host `info`/`list`/`search`),
  3. the **behavioral facet prose** (Phase 103 docs) — write algorithm / erase model / VPP
     behavior / pin roles, datasheet-cited (the existing NAME-01 four-facet content).
- **D-02:** The C-token form is **`PROTO_<NAME>`** (e.g. `PROTO_EPROM_28PIN = 0x07`,
  `PROTO_FLASH_5V_PAGE = 0x05`). The `PROTO_` prefix namespaces the ids and reads
  unambiguously at the dispatch site (`handle->protocol == PROTO_EPROM_28PIN`). The label
  **is** the number — numeric values are unchanged (FW-01 intent, though the constants are
  *defined* in Phase 101; Phase 100 only fixes the token strings).

### Naming Style / Axis
- **D-03:** Names use a **chip-family / behavior axis**, dropping minipro-heritage jargon
  (`AMD`, `QUICK`, `ALT`). Name by what the chip *is* and how it programs — e.g. 0x05 →
  `FLASH_5V_PAGE`, 0x08 → `EPROM_32PIN`, 0x0B → `EPROM_24PIN`. This is a deliberate departure
  from the v1.16 col-2 tokens the operator flagged as mechanism-jargon.
- **D-04:** Within a many-to-one family, **pin count is the primary discriminator** and
  **voltage/hazard detail lives in the facet prose (field 3), not the name.** So EPROM →
  `EPROM_28PIN` (0x07) / `EPROM_32PIN` (0x08) / `EPROM_24PIN` (0x0B); SRAM by pin count.
- **D-05:** **0x0E vs 0x29 collision — MUST-RESOLVE at authoring.** Both are 32-pin SRAM, so
  pin-count-only names them identically. The draft table presented at the NAME-02 gate MUST
  break the tie (candidate: `SRAM_32PIN` for 0x0E battery-backed NVRAM vs
  `SRAM_32PIN_LARGE` / a size suffix for 0x29's 512K–1M parts). Operator picks the final
  suffix at approval; this collision is explicitly NOT pre-decided.

### Authoritative Source & Table Shape
- **D-06:** The authoritative source is **`firestarter/doc/PROTOCOLS.md`, revised in place**
  (col-2 → the new 3-field set). It is already "the canonical GitHub-visible protocol
  vocabulary" and **is the artifact the operator approves at the gate**. Phases 101/102/103
  cite it by section. No new source file (satisfies NAME-03 "one identifiable source").
- **D-07:** Revised table columns: **hex | frozen `datasheets/<hex>-<NAME>/` slug (col-1,
  unchanged) | `PROTO_` token | display name | facet.** Keeping the frozen slug column
  visible next to the new name **is the DOC-02 divergence record** — anyone sees old-slug vs
  new-name at a glance; slugs are NOT renamed (NAME-F1 deferred).

### Phantoms & Family Layer
- **D-08:** 0x35/0x39 get **distinct phantom tokens explicitly marked non-real** (e.g.
  `PROTO_PHANTOM_0x35` / `_0x39`), facet text "phantom — 0 DB chips, dispatch-preserved for
  forward-compat, routes to the flash-5V-page handler." The firmware dispatch line
  (`memory.cpp:122`, currently `protocol == 0x35 || protocol == 0x39`) then reads honestly in
  Phase 101; nobody mistakes them for real protocols. They are named but flagged, NOT aliased
  to the 0x05 family name.
- **D-09:** The canonical set **also defines an operator-approved handler-family name layer**
  (a small set of family names the many-to-one handlers draw from) so Phase 101's FW-03 file/
  function renames (`configure_flash3`/`flash_type_3.cpp`, `configure_flash4`/
  `flash_type_4.cpp`, `configure_eeprom28c`) come from THIS source, not invented mid-refactor.
  Family groupings are fixed by the existing many-to-one dispatch: **one EPROM handler**
  (0x07/0x08/0x0B), **one SRAM handler** (0x0E/0x27/0x28/0x29), plus the single-protocol
  handlers (0x05 flash-5V-page, 0x06 AMD/SST NOR flash, 0x0D parallel EEPROM, 0x10 Intel
  flash). Represent as a per-entry "handler-family" column or a short companion table.

### Claude's Discretion
- The exact per-bucket final name strings and the 0x0E/0x29 tiebreaker (D-05) are proposed by
  the executor in the draft table and **settled at the NAME-02 approval gate** — the operator
  has final say on every name before it becomes authoritative. Downstream phases do not
  re-open naming; they conform.
- 0x34 (`EEPROM-X88C64`, PCB-blocked FUT-01, `not_implemented.cpp`) still needs a name per
  NAME-01 (it is present in the DB); executor proposes a behavior-axis name consistent with
  D-03 (e.g. `EEPROM_X88C64` / `EEPROM_8051BUS`), operator confirms.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### The vocabulary being revised (the primary work surface)
- `firestarter/doc/PROTOCOLS.md` — the current v1.16 canonical vocabulary; §Canonical bucket
  set (the hex→handler→slug→col-2 table), §1 (real buckets, 4-facet prose per bucket), §2
  (phantom 0x35/0x39 + infeasible 0x11/0x2A/0x2B/0x2C non-protocols), §3 (INV-01..09 matrix).
  **This is the file Phase 100 revises in place and the operator approves.**

### Requirements & roadmap
- `.planning/REQUIREMENTS.md` — v1.19 requirements; NAME-01/02/03 (this phase), FW-03
  (family-name consumer), DOC-02 (slug-divergence rule), GATE-01/02/03 (non-regression),
  §Out of Scope (NAME-F1 slug rename deferred, NAME-F2 CLI-alias deferred).
- `.planning/ROADMAP.md` §Phase 100 — goal + 3 success criteria; §Phase 101/102/103 for how
  the name set is consumed downstream.

### Downstream consumers (name set must serve these — read to sanity-check names)
- `firestarter/src/proms/memory.cpp` §dispatch (lines ~107–165) — the raw-hex dispatch chain
  Phase 101 relabels; shows the many-to-one groupings that fix the family layer (D-09).
- `firestarter/include/` headers — where Phase 101 will define the `PROTO_<NAME>` constants
  (no protocol-id enum exists yet; `messages.h` holds the `DBG_CONFIGURING_*` + `MSG_ERR_*`
  codes, distinct from protocol ids).
- `firestarter_app/firestarter/ic_layout.py` — the divergent host maps Phase 102 consolidates:
  `proto_display` (lines ~216–234) and `protocol_info_data` (line ~261+). Two of the three
  vocabularies the canonical set reconciles.
- `firestarter_app/firestarter/eprom_info.py` — host presenter consuming `ic_layout` specs.
- `datasheets/` (top-level) folder slugs `<hex>-<NAME>/` — **frozen**; the col-1 divergence
  anchor. Do NOT rename (NAME-F1).

### Datasheet grounding (behavior-correctness of names/facets)
- `datasheets/<hex>-<NAME>/*.pdf` — per-bucket datasheets already cited inline in PROTOCOLS.md
  §1 facets; the source of truth for "behavior/datasheet-correct" (NAME-01).

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **PROTOCOLS.md §1 four-facet prose** already exists and is datasheet-cited — field 3 (facet
  prose) of the new schema is largely a re-org/relabel of existing content, not new research.
- **The v1.16 col-2 tokens** are the starting point being *revised* (not authored from
  scratch) — every bucket already has a name; the work is correcting the jargon per D-03.
- **FM1608 (0x28 SRAM→FRAM) and X88C64 (0x34 EEPROM) identity corrections (NAME-04)** are
  already recorded in PROTOCOLS.md §1.10/§1.12 — carry them forward, do not re-litigate.

### Established Patterns
- **Algorithm-first dispatch is authoritative** — protocol numbers flow upstream XML → DB →
  wire → firmware unchanged. Names are a *legibility layer on top*; internal logic keeps
  operating on numbers (GATE-01/02/03). Names must never become the dispatch key.
- **Frozen-slug convention (DOC-02 / NAME-F1)** — `datasheets/` folder slugs are provenance
  and stay put; name↔slug divergence is documented, never silently applied.
- **Many-to-one dispatch is preserved** (out-of-scope to split, per REQUIREMENTS §Out of
  Scope) — the family layer (D-09) names those existing groupings, it does not restructure.

### Integration Points
- Phase 101 reads field-1 tokens + the family layer; Phase 102 reads field-2 display names;
  Phase 103 reconciles field-3 prose + the INV matrix. All three cite the revised
  PROTOCOLS.md. The name set is the contract between this phase and all downstream phases.

</code_context>

<specifics>
## Specific Ideas

- Concrete name direction agreed (illustrative, final at gate): 0x05 → `FLASH_5V_PAGE`,
  0x07 → `EPROM_28PIN`, 0x08 → `EPROM_32PIN`, 0x0B → `EPROM_24PIN`, phantom 0x35/0x39 →
  `PROTO_PHANTOM_0x35`/`_0x39`. Voltage/VPP detail → facet prose, not the name.
- The revised PROTOCOLS.md table doubles as the operator-approval artifact — it must be
  render-able and reviewable as a single table so the NAME-02 gate is a clean yes/no on names.

</specifics>

<deferred>
## Deferred Ideas

- **NAME-F1** — renaming the `datasheets/<hex>-<NAME>/` folder slugs to match the new
  vocabulary. Deferred (avoids folder/provenance churn); only on explicit operator instruction.
- **NAME-F2** — accepting a protocol name/alias as CLI input (filter/select by protocol name).
  Explicitly out of scope for v1.19; chip selection stays by part number (GATE-03).
- **Infeasible-bucket naming (0x11/0x2A/0x2B/0x2C)** — these appear in firmware dispatch
  (`memory.cpp` step 6a → `not_implemented`) but are NOT in `chip_database.json`, so they are
  outside NAME-01's required scope. If Phase 101 needs constants for that dispatch arm, it may
  reuse the §2.2 "honest non-protocols" labels; naming them canonically is not a Phase-100
  deliverable.

</deferred>

---

*Phase: 100-name-canonical-protocol-name-set-operator-approval*
*Context gathered: 2026-07-01*
