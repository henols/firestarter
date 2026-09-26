# Phase 100: NAME — Canonical Protocol Name Set + Operator Approval - Research

**Researched:** 2026-07-01
**Domain:** Protocol vocabulary authoring / naming-decision phase (docs + operator gate; NO executable code)
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01:** Each protocol entry is **structured with 3 fields** so each downstream consumer reads one field with no re-derivation: (1) a **C-identifier-safe constant token** (Phase 101 firmware `#define`/enum), (2) a **short human display name** (Phase 102 host `info`/`list`/`search`), (3) the **behavioral facet prose** (Phase 103 docs) — write algorithm / erase model / VPP behavior / pin roles, datasheet-cited (the existing NAME-01 four-facet content).
- **D-02:** The C-token form is **`PROTO_<NAME>`** (e.g. `PROTO_EPROM_28PIN = 0x07`, `PROTO_FLASH_5V_PAGE = 0x05`). The `PROTO_` prefix namespaces the ids and reads unambiguously at the dispatch site (`handle->protocol == PROTO_EPROM_28PIN`). The label **is** the number — numeric values are unchanged (FW-01 intent; constants are *defined* in Phase 101; Phase 100 only fixes the token strings).
- **D-03:** Names use a **chip-family / behavior axis**, dropping minipro-heritage jargon (`AMD`, `QUICK`, `ALT`). Name by what the chip *is* and how it programs — e.g. 0x05 → `FLASH_5V_PAGE`, 0x08 → `EPROM_32PIN`, 0x0B → `EPROM_24PIN`. Deliberate departure from the v1.16 col-2 tokens the operator flagged as mechanism-jargon.
- **D-04:** Within a many-to-one family, **pin count is the primary discriminator** and **voltage/hazard detail lives in the facet prose (field 3), not the name.** So EPROM → `EPROM_28PIN` (0x07) / `EPROM_32PIN` (0x08) / `EPROM_24PIN` (0x0B); SRAM by pin count.
- **D-05:** **0x0E vs 0x29 collision — MUST-RESOLVE at authoring.** Both are 32-pin SRAM, so pin-count-only names them identically. The draft table at the NAME-02 gate MUST break the tie (candidate: `SRAM_32PIN` for 0x0E battery-backed NVRAM vs `SRAM_32PIN_LARGE` / a size suffix for 0x29's 512K–1M parts). Operator picks the final suffix at approval; this collision is explicitly NOT pre-decided.
- **D-06:** The authoritative source is **`firestarter/doc/PROTOCOLS.md`, revised in place** (col-2 → the new 3-field set). It is already the canonical GitHub-visible protocol vocabulary and **is the artifact the operator approves at the gate**. Phases 101/102/103 cite it by section. No new source file (satisfies NAME-03 "one identifiable source").
- **D-07:** Revised table columns: **hex | frozen `datasheets/<hex>-<NAME>/` slug (col-1, unchanged) | `PROTO_` token | display name | facet.** Keeping the frozen slug column next to the new name **is the DOC-02 divergence record** — old-slug vs new-name at a glance; slugs are NOT renamed (NAME-F1 deferred).
- **D-08:** 0x35/0x39 get **distinct phantom tokens explicitly marked non-real** (e.g. `PROTO_PHANTOM_0x35` / `_0x39`), facet text "phantom — 0 DB chips, dispatch-preserved for forward-compat, routes to the flash-5V-page handler." The firmware dispatch line (`memory.cpp`, `protocol == 0x35 || protocol == 0x39`) then reads honestly in Phase 101. Named but flagged, NOT aliased to the 0x05 family name.
- **D-09:** The canonical set **also defines an operator-approved handler-family name layer** (a small set of family names the many-to-one handlers draw from) so Phase 101's FW-03 file/function renames (`configure_flash3`/`flash_type_3.cpp`, `configure_flash4`/`flash_type_4.cpp`, `configure_eeprom28c`) come from THIS source, not invented mid-refactor. Family groupings fixed by existing many-to-one dispatch: **one EPROM handler** (0x07/0x08/0x0B), **one SRAM handler** (0x0E/0x27/0x28/0x29), plus single-protocol handlers (0x05 flash-5V-page, 0x06 AMD/SST NOR flash, 0x0D parallel EEPROM, 0x10 Intel flash). Represent as a per-entry "handler-family" column or a short companion table.

### Claude's Discretion
- The exact per-bucket final name strings and the 0x0E/0x29 tiebreaker (D-05) are proposed by the executor in the draft table and **settled at the NAME-02 approval gate** — the operator has final say on every name before it becomes authoritative. Downstream phases do not re-open naming; they conform.
- 0x34 (`EEPROM-X88C64`, PCB-blocked FUT-01, `not_implemented.cpp`) still needs a name per NAME-01 (it is present in the DB); executor proposes a behavior-axis name consistent with D-03 (e.g. `EEPROM_X88C64` / `EEPROM_8051BUS`), operator confirms.

### Deferred Ideas (OUT OF SCOPE)
- **NAME-F1** — renaming the `datasheets/<hex>-<NAME>/` folder slugs to match the new vocabulary. Deferred (avoids folder/provenance churn); only on explicit operator instruction.
- **NAME-F2** — accepting a protocol name/alias as CLI input (filter/select by protocol name). Explicitly out of scope for v1.19; chip selection stays by part number (GATE-03).
- **Infeasible-bucket naming (0x11/0x2A/0x2B/0x2C)** — appear in firmware dispatch (`memory.cpp` step 6a → `not_implemented`) but NOT in `chip_database.json`, so outside NAME-01's required scope. If Phase 101 needs constants for that dispatch arm, it may reuse the §2.2 "honest non-protocols" labels; naming them canonically is not a Phase-100 deliverable.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| NAME-01 | A single canonical 3-field entry (`PROTO_<NAME>` token + display name + datasheet-cited 4-facet prose) for every DB protocol (0x05/06/07/08/0B/0D/0E/10/27/28/29/34) + phantoms 0x35/0x39 (flagged non-real); chip-family/behavior axis, pin-count-primary; FM1608 (0x28) + X88C64 (0x34) identity corrections carried forward. | DB protocol set enumerated + confirmed (§Protocol Inventory); existing §1 four-facet prose is the reuse base (field 3 is a re-org, not new research); FM1608/X88C64 corrections already recorded in PROTOCOLS.md §1.10/§1.12. |
| NAME-02 | Operator explicitly approves the name set at a blocking gate; draft table presented; 0x0E-vs-0x29 collision resolved at approval; no silent auto-approval. | §Approval-Gate Structure (single reviewable table shape + blocking `checkpoint:human-verify` gate); §0x0E/0x29 collision analysis with tiebreak candidates. |
| NAME-03 | Recorded in one authoritative source (`firestarter/doc/PROTOCOLS.md`, revised in place) cited by Phases 101/102/103; includes operator-approved handler-family name layer for the many-to-one handlers. | §Revise-in-Place Contract (preserve-vs-change map of the existing doc); §Handler-Family Layer grounded in actual `memory.cpp` dispatch + `configure_*` function names. |
</phase_requirements>

## Summary

Phase 100 is a **pure naming/decision phase** — no executable code, no `chip_database.json` change, no wire/constant *value* change. The deliverable is a revised `firestarter/doc/PROTOCOLS.md` carrying a 3-field canonical name set per protocol, plus a handler-family name layer, approved by the operator at a blocking gate. Every downstream phase (101 firmware, 102 host, 103 docs) cites this one file by section.

The research is entirely codebase-grounded — **no web research is applicable**. Every fact needed is verifiable in-repo: the DB protocol set, the firmware dispatch chain, the two divergent host vocabularies, the frozen datasheet slugs, and the existing four-facet prose. I verified all of these directly. Key confirmations: the DB carries **exactly the 12 protocols in the goal** (0x05/06/07/08/0B/0D/0E/10/27/28/29/34, 746 chips total) with no divergence; **no `PROTO_<NAME>` token or protocol-id enum exists in firmware yet** (protocol ids are raw hex literals in `memory.cpp`) so the proposed tokens are greenfield and Phase 101 defines them cleanly; and **both host vocabularies are already missing 0x34** while `protocol_info_data` additionally carries 0x11 (an infeasible non-protocol) — divergences Phase 102 must reconcile against this canonical set.

**Primary recommendation:** Revise `firestarter/doc/PROTOCOLS.md` in place by (1) replacing the single "algorithm-axis name (col 2)" with three explicit sub-columns/fields (`PROTO_` token · display name · facet-prose pointer) in both the Canonical bucket set table and each §1.x bucket header, (2) adding a handler-family column (or a short companion table) that names the 7 handler groupings from the actual `configure_*` functions, (3) keeping the frozen slug column verbatim as the DOC-02 divergence anchor, and (4) presenting the whole revised Canonical bucket set table as a single reviewable artifact behind a blocking `checkpoint:human-verify` gate where the operator resolves the 0x0E/0x29 tiebreak and approves every name. Preserve §2 (non-protocols) and §3 (INV matrix) unchanged in Phase 100 — §1 prose + INV reconciliation is Phase 103's job (DOC-01), NOT this phase.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Canonical name authoring (3-field set) | Docs (`firestarter/doc/PROTOCOLS.md`) | — | The vocabulary is a documentation artifact; it is the single source of truth all code tiers later cite. |
| C-token feasibility check | Firmware (grounding only) | — | Phase 100 confirms `PROTO_<NAME>` tokens are C-identifier-safe + collision-free for Phase 101's `#define`/enum in `firestarter/include/`; Phase 100 does NOT define them. |
| Display-name reconciliation target | Host CLI (grounding only) | — | Phase 100 supplies the display names that Phase 102 consolidates `ic_layout.proto_display` + `protocol_info_data` onto; Phase 100 does NOT edit host code. |
| Handler-family naming | Docs, grounded in Firmware dispatch | — | Family names derive from the actual `configure_*` functions in `firestarter/src/proms/`; the doc records them for Phase 101's FW-03 renames. |
| Operator approval gate | Process (blocking checkpoint) | — | A human decision, not a tier — a `checkpoint:human-verify` task that blocks all downstream phases. |

## Standard Stack

**Not applicable.** This is a naming/decision phase producing a Markdown document and a human decision. No libraries, packages, frameworks, or runtime dependencies are installed or used. The only tools involved are text editing (the `Edit`/`Write` tools on `PROTOCOLS.md`) and git commit.

- **No package installation** → no Package Legitimacy Audit section required (see below).
- **No external services / runtimes** → Environment Availability section is SKIPPED (Step 2.6: no external dependencies; a Markdown edit needs only the editor + git, both present).

## Package Legitimacy Audit

**Not applicable — this phase installs no external packages.** No npm/PyPI/crates dependency is added, removed, or upgraded. Zero packages to audit.

## Protocol Inventory (verified against `chip_database.json`)

`[VERIFIED: chip_database.json parse, 2026-07-01]` — the DB carries **exactly the 12 protocols named in the goal**, no divergence. 746 chips total.

| hex | dec | DB chip count | handler function | handler file | frozen datasheet slug (col-1) |
|-----|-----|--------------|------------------|--------------|-------------------------------|
| 0x05 | 5 | 27 | `configure_flash4` | `flash_type_4.cpp` | `0x05-FLASH-AMD-STD` |
| 0x06 | 6 | 190 | `configure_flash3` | `flash_type_3.cpp` | `0x06-FLASH-AMD-ALT` |
| 0x07 | 7 | 170 | `configure_eprom` | `eprom.cpp` | `0x07-EPROM-STD` |
| 0x08 | 8 | 127 | `configure_eprom` | `eprom.cpp` | `0x08-EPROM-QUICK` |
| 0x0B | 11 | 32 | `configure_eprom` | `eprom.cpp` | `0x0B-EPROM-LEGACY` |
| 0x0D | 13 | 84 | `configure_eeprom28c` | `eeprom_28c.cpp` | `0x0D-EEPROM-POLL` |
| 0x0E | 14 | 20 | `configure_sram` | `sram.cpp` | `0x0E-SRAM-32PIN` |
| 0x10 | 16 | 39 | `configure_flash_intel` | `flash_intel.cpp` | `0x10-FLASH-INTEL` |
| 0x27 | 39 | 2 | `configure_sram` | `sram.cpp` | `0x27-SRAM-24PIN` |
| 0x28 | 40 | 34 | `configure_sram` | `sram.cpp` | `0x28-SRAM-STD` |
| 0x29 | 41 | 20 | `configure_sram` | `sram.cpp` | `0x29-SRAM-512K-1M` |
| 0x34 | 52 | 1 | `configure_not_implemented` | `not_implemented.cpp` | `0x34-EEPROM-X88C64` |

**Phantoms (0 DB chips, dispatch-only):** `[VERIFIED: memory.cpp dispatch chain]`
- 0x35 / 0x39 — appear ONLY in the `protocol == 0x05 || protocol == 0x35 || protocol == 0x39 → configure_flash4()` dispatch line. Zero chips in the DB. Must be named-but-flagged per D-08.

**Divergence check:** NONE. The DB set == the goal set == the frozen slug set (all 12 slug folders exist under `/workspaces/datasheets/`). `[VERIFIED: ls /workspaces/datasheets/]`

**Datasheet slug set (frozen, DOC-02 anchor):** `[VERIFIED: directory listing]`
`0x05-FLASH-AMD-STD`, `0x06-FLASH-AMD-ALT`, `0x07-EPROM-STD`, `0x08-EPROM-QUICK`, `0x0B-EPROM-LEGACY`, `0x0D-EEPROM-POLL`, `0x0E-SRAM-32PIN`, `0x10-FLASH-INTEL`, `0x27-SRAM-24PIN`, `0x28-SRAM-STD`, `0x29-SRAM-512K-1M`, `0x34-EEPROM-X88C64`. Do NOT rename (NAME-F1).

## Handler-Family Layer (grounded in actual dispatch — D-09)

`[VERIFIED: firestarter/src/proms/memory.cpp dispatch chain + grep of configure_* functions]`

The many-to-one groupings are fixed by the existing dispatch (out-of-scope to split). The family-name layer names these 7 groupings so Phase 101's FW-03 file/function renames draw from the canonical source:

| Handler function (current) | File (current) | Protocols dispatched | Family character | Family-name naming note |
|----------------------------|----------------|----------------------|------------------|-------------------------|
| `configure_eprom` | `eprom.cpp` | 0x07, 0x08, 0x0B | one EPROM handler (many-to-one) | The EPROM family name; individual entries are `EPROM_28PIN`/`EPROM_32PIN`/`EPROM_24PIN`. |
| `configure_sram` | `sram.cpp` | 0x0E, 0x27, 0x28, 0x29 | one SRAM handler (many-to-one) | The SRAM family name; entries by pin count; **0x0E/0x29 collision (D-05) lives here.** |
| `configure_flash4` | `flash_type_4.cpp` | 0x05 (+ phantoms 0x35/0x39) | single real protocol (+ dead arms) | FW-03 renames `flash4`/`flash_type_4.cpp` from the 0x05 family name (5V page flash). |
| `configure_flash3` | `flash_type_3.cpp` | 0x06 | single protocol | FW-03 renames `flash3`/`flash_type_3.cpp` from the 0x06 family name (AMD/SST NOR flash). |
| `configure_eeprom28c` | `eeprom_28c.cpp` | 0x0D | single protocol | FW-03 renames `eeprom28c`/`eeprom_28c.cpp` from the 0x0D family name (parallel 5V EEPROM). |
| `configure_flash_intel` | `flash_intel.cpp` | 0x10 | single protocol | Intel-28F command-register flash. |
| `configure_not_implemented` | `not_implemented.cpp` | 0x34 (+ infeasible 0x11/0x2A/0x2B/0x2C) | fail-closed | 0x34 gets a real name per NAME-01 (executor proposes, e.g. `EEPROM_X88C64`) even though its handler is not-implemented (FUT-01). |

**Critical:** the family layer *names existing groupings*; it does NOT restructure or split handlers (Out of Scope, REQUIREMENTS.md). Phase 101's FW-03 file/function renames are the consumers — Phase 100 only records the family names.

**Companion DBG-code note (informational, not a Phase-100 deliverable):** `firestarter/include/messages.h` carries `DBG_CONFIGURING_EPROM (0x12)`, `DBG_CONFIGURING_FLASH (0x1D)`, `DBG_CONFIGURING_FLASH4 (0x21)`, `DBG_CONFIGURING_SRAM (0x22)`, `DBG_CONFIGURING_INTEL_FLASH (0x1B)`, `DBG_CONFIGURING_EEPROM_28C (0x27)`. These are debug message codes, distinct from protocol ids — Phase 101 may or may not touch them, but Phase 100 does not.

## Downstream Consumer Grounding (name set must serve these)

### Firmware token feasibility (Phase 101 / FW-01, FW-02, FW-03)
`[VERIFIED: grep of firestarter/include/ + firestarter/src/proms/]`
- **No `PROTO_<NAME>` constant or protocol-id enum exists today.** Protocol ids appear only as raw hex literals in `memory.cpp` dispatch (`handle->protocol == 0x07` etc.). This is greenfield for Phase 101 — the `PROTO_` tokens Phase 100 authors do NOT collide with any existing identifier.
- `messages.h` holds `DBG_CONFIGURING_*` and `MSG_ERR_*` codes — a *different* namespace from protocol ids; the `PROTO_` prefix (D-02) keeps them separate.
- **C-identifier-safety check:** proposed tokens like `PROTO_EPROM_28PIN`, `PROTO_FLASH_5V_PAGE`, `PROTO_SRAM_32PIN` are all valid C identifiers (start with letter, `[A-Za-z0-9_]` only). ⚠ **The phantom token form `PROTO_PHANTOM_0x35` in D-08 is NOT a valid C identifier** — `0x35` contains no problem, but a bare `0x35` reads as a hex literal fragment; `PROTO_PHANTOM_0x35` is *lexically* a valid identifier (underscore + alphanumerics: `P-H-A-N-T-O-M-_-0-x-3-5`), so it compiles — but consider `PROTO_PHANTOM_35` / `PROTO_PHANTOM_39` to avoid the visual "hex-in-identifier" ambiguity. Flag for operator preference at the gate. `[VERIFIED: C identifier grammar]`
- The label **is** the number (FW-01): numeric values unchanged. Phase 100 fixes only the *token strings*; Phase 101 writes the `#define PROTO_... = 0x..` lines and dual-repo lockstep with host `constants.py`.

### Host display reconciliation (Phase 102 / HOST-01)
`[VERIFIED: firestarter_app/firestarter/ic_layout.py`, two blocks extracted]
There are **two divergent host vocabularies**, and both are already inconsistent with the DB set:

- **`ic_layout.proto_display`** (a dict, `get_chip_type_string`): covers `0x05,0x06,0x07,0x08,0x0B,0x0D,0x0E,0x10,0x27,0x28,0x29` — **11 entries, MISSING 0x34.** Phantoms intentionally removed (Phase 57 DEC-05).
- **`ic_layout._get_protocol_info_structured.protocol_info_data`** (a list): covers `0x05,0x06,0x07,0x08,0x0B,0x0D,0x0E,0x10,0x11,0x27,0x28,0x29` — **12 entries but includes 0x11 (an INFEASIBLE non-protocol) and MISSING 0x34.**

**Implication for the name set:** the canonical display names Phase 100 authors must include **0x34** (so Phase 102 can add it) and must NOT introduce a real display name for 0x11 (Phase 102 should drop it — it belongs in §2.2 non-protocols). Providing a display name for every DB protocol including 0x34 lets Phase 102 converge both maps onto one consistent set. `eprom_info.py` is the presenter that consumes these `ic_layout` specs (Phase 102 touch point, not Phase 100).

### Docs reconciliation (Phase 103 / DOC-01, DOC-02)
- §1 four-facet prose + §3 INV-01..09 matrix reconciliation to the new names is **Phase 103's job, explicitly NOT Phase 100's.** Phase 100 revises the *name columns* (Canonical bucket set table + §1.x headers' col-2 line); it must leave the INV matrix and §2 intact so Phase 103 can reconcile prose without a merge conflict against a half-renamed doc.
- DOC-02 divergence record = the retained frozen-slug column sitting next to the new name (D-07).

## Revise-in-Place Contract (`firestarter/doc/PROTOCOLS.md`)

`[VERIFIED: full read of firestarter/doc/PROTOCOLS.md]` — the file today has this structure. This is the preserve-vs-change map "revise in place" (D-06) requires:

| Section | Current content | Phase 100 action |
|---------|-----------------|------------------|
| Header intro + reader router | Describes col-1 slug / col-2 algorithm-axis name / four facets / NAME-04 / INV matrix | **CHANGE** — update the intro to describe the new 3-field schema (token + display + facet) and the handler-family layer; keep the router links. |
| **Canonical bucket set** table | `hex \| DB chip count \| handler \| datasheets folder (col 1) \| algorithm-axis name (col 2)` | **CHANGE (primary work surface)** — this is the single reviewable approval table. Expand col-2 into: `PROTO_ token \| display name \| handler-family`, retain the frozen slug column (DOC-02 anchor), keep hex + chip count. Add 0x35/0x39 phantom rows (flagged). |
| §1.1–§1.12 per-bucket sections | Each has "Folder slug (col 1)" + "Algorithm-axis name (col 2)" + Handler + 4 facets (write/erase/VPP/pins) | **PARTIAL CHANGE** — update only the "Algorithm-axis name (col 2)" line per bucket to the new `PROTO_` token + display name. **PRESERVE the four-facet prose verbatim** (it is field 3 and is datasheet-cited; re-org is Phase 103/DOC-01, not here). PRESERVE the NAME-04 call-outs in §1.10 (FM1608) and §1.12 (X88C64). |
| §2 Honest non-protocols (2.1 phantoms 0x35/0x39; 2.2 infeasible 0x11/0x2A/0x2B/0x2C) | Names phantoms `FLASH_EEPROM`/`FLASH_EEPROM2`; infeasible buckets described | **MOSTLY PRESERVE** — Phase 100 gives 0x35/0x39 their flagged `PROTO_PHANTOM_*` tokens (D-08) so §2.1 and the new bucket table agree; leave §2.2 infeasible buckets unchanged (out of scope). |
| §3 INV-01..09 matrix | Behavioral invariants, owning handler, native test names, suite paths — SAFE-02 handoff | **PRESERVE UNCHANGED** — reconciling the matrix to new names is Phase 103/DOC-01. Touching it here risks the grep-intact SAFE-02 contract. |
| Footer | Phase 87 authoring provenance | **CHANGE** — add a Phase-100 revision line noting the name-set revision + operator approval date. |

**Carry-forward (NOT re-litigated):** FM1608 (0x28 → SRAM_STD/FRAM, `variant=0x4126`, algorithm axis 0x28) and X88C64 (0x34 → EEPROM, `flags & 0x10 == 0` overridden by variant decode) identity corrections are already in §1.10/§1.12 and INV-07. Keep them.

## Architecture Patterns

### Data-flow (how the name set is consumed)

```
                         ┌──────────────────────────────────────────┐
   Phase 100 authors ──► │  firestarter/doc/PROTOCOLS.md (REVISED)    │
   + operator approves   │  Canonical bucket set table (3 fields):    │
                         │   hex │ frozen-slug │ PROTO_ token │        │
                         │        display name │ handler-family        │
                         │  §1.x facet prose (unchanged) │ §2 │ §3     │
                         └───────────┬───────────┬───────────┬────────┘
                                     │ field 1   │ field 2   │ field 3 + families
                                     ▼           ▼           ▼
                              ┌────────────┐┌──────────┐┌──────────────┐
                   Phase 101→ │ firmware   ││ Phase 102││ Phase 103    │
                   FW-01/02/03│ PROTO_ =   ││ host     ││ §1 prose +   │
                              │ 0x.. defs; ││ display  ││ INV matrix   │
                              │ memory.cpp ││ names in ││ reconciled;  │
                              │ relabel;   ││ ic_layout││ DOC-02 slug  │
                              │ family     ││ two maps ││ divergence   │
                              │ file/fn    ││ merged   ││ recorded     │
                              │ renames    ││          ││              │
                              └────────────┘└──────────┘└──────────────┘
   Non-regression (GATE-01/02/03): numbers stay the dispatch key; no DB/wire value change;
   CLI grammar unchanged. Names are a legibility layer ON TOP — never a dispatch/lookup key.
```

### Pattern 1: Single reviewable approval table = the deliverable
**What:** The revised "Canonical bucket set" table doubles as the operator-approval artifact. It must render as one Markdown table the operator can scan top-to-bottom and say yes/no.
**When to use:** NAME-02 gate. Every DB protocol + both phantoms in one table; the operator sees old-slug vs new-name side by side and resolves the 0x0E/0x29 tiebreak inline.
**Structure (proposed columns):** `hex | frozen slug | PROTO_ token | display name | handler-family | phantom? |`

### Pattern 2: Blocking human-verify gate (no silent auto-approval)
**What:** A `checkpoint:human-verify` task in the plan that BLOCKS all downstream phases (101/102/103) until the operator explicitly approves the rendered table.
**When to use:** After the draft table is authored, before PROTOCOLS.md is committed as authoritative. The gate task presents the table, captures the operator's name choices + the 0x0E/0x29 tiebreak decision, and only then finalizes the doc.

### Anti-Patterns to Avoid
- **Reconciling §1 prose / INV matrix in Phase 100:** that is DOC-01 (Phase 103). Doing it here creates a half-renamed doc and risks the SAFE-02 grep-intact INV contract. Only touch the *name columns* in Phase 100.
- **Renaming datasheet slug folders:** NAME-F1, deferred. The slug column stays frozen as the divergence anchor.
- **Letting a name become a dispatch/lookup key:** GATE-01. Numbers stay authoritative end to end; names are legibility only.
- **Naming 0x11/0x2A/0x2B/0x2C canonically:** out of scope (not in DB). Leave in §2.2.
- **Auto-approving the name set:** NAME-02 forbids silent approval — the gate must be an explicit operator yes.
- **Aliasing phantoms to the 0x05 family name:** D-08 — phantoms get distinct flagged tokens, not the real family name.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Facet prose per bucket | New datasheet-cited behavioral text from scratch | The existing §1.x four-facet prose in PROTOCOLS.md (verbatim, it is already cited) | It is already datasheet-anchored and Phase-86/87 verified; field 3 is a re-org/relabel, not new research (CONTEXT reusable-assets note). |
| Handler-family groupings | A new grouping scheme | The actual `configure_*` dispatch groupings in `memory.cpp` | Groupings are fixed by real dispatch (out-of-scope to split); inventing groupings would desync from firmware. |
| DB protocol set | A hand-typed list | The parsed `algorithm` field counts from `chip_database.json` | The DB is authoritative; parse it (already done here — 12 protocols confirmed). |
| Divergence record | A separate divergence file | The retained frozen-slug column next to the name (D-07) | One doc, one glance — satisfies DOC-02 and NAME-03 "one source". |

**Key insight:** ~80% of Phase 100's content already exists in PROTOCOLS.md; the phase is a *relabel + restructure of the name columns* plus a *decision* (operator approval), not a from-scratch authoring effort.

## Runtime State Inventory

> This phase is a documentation revision + a human decision. It is NOT a rename/refactor of running code (that is Phases 101/102). The renamed *string tokens* do not yet exist anywhere in code (verified: no `PROTO_` tokens in firmware), so there is no cached/stored/registered runtime state carrying a Phase-100 string.

| Category | Items Found | Action Required |
|----------|-------------|------------------|
| Stored data | None — `chip_database.json` is NOT changed (GATE-02); protocol *numbers* are the DB key and stay identical. Names are not stored in the DB. | None. |
| Live service config | None — no external service embeds these protocol *names* (the firmware/host use *numbers*). | None. |
| OS-registered state | None — no OS registration references protocol names. | None. |
| Secrets/env vars | None — no secret/env var references a protocol name. | None. |
| Build artifacts | None from Phase 100 — the doc edit produces no build artifact. (Phase 101's `PROTO_` `#define`s will land in firmware headers + `constants.py` under dual-repo lockstep, but that is downstream.) | None for Phase 100. |

**Why this is clean:** the whole point of v1.19 (GATE-01/02/03) is that numbers stay the dispatch key; names are a legibility layer added *on top*. Phase 100 adds no state at all — it authors text and records a decision.

## Common Pitfalls

### Pitfall 1: Scope-creeping into Phase 103's prose reconciliation
**What goes wrong:** The executor starts rewriting §1 facet prose and the INV-01..09 matrix to use the new names while "in there anyway."
**Why it happens:** The name columns and the facet prose live in the same §1.x sections.
**How to avoid:** Touch ONLY the "Algorithm-axis name (col 2)" line per bucket + the Canonical bucket set table. Leave facet prose and §3 verbatim. DOC-01 is Phase 103.
**Warning signs:** A diff that touches the INV matrix rows or rewrites facet sentences.

### Pitfall 2: Silent / implied operator approval
**What goes wrong:** The executor authors a "good enough" table and commits PROTOCOLS.md as authoritative without an explicit operator yes.
**Why it happens:** YOLO mode + the table looks complete.
**How to avoid:** A hard `checkpoint:human-verify` task that blocks until the operator approves AND resolves the 0x0E/0x29 tiebreak. NAME-02 explicitly forbids silent auto-approval.
**Warning signs:** No checkpoint task in the plan; downstream phases could start without an approval record.

### Pitfall 3: Forgetting 0x34 in the display-name set
**What goes wrong:** The executor mirrors the existing host `proto_display` map (which omits 0x34) and never authors a display name for 0x34.
**Why it happens:** Both host vocabularies already drop 0x34.
**How to avoid:** NAME-01 requires an entry for *every* DB protocol; 0x34 is in the DB (1 chip). Author its name (executor proposes `EEPROM_X88C64`, operator confirms) even though its handler is not-implemented.
**Warning signs:** Only 11 real entries in the draft table instead of 12 (+2 phantoms = 14 rows).

### Pitfall 4: Phantom token that reads as a hex literal
**What goes wrong:** `PROTO_PHANTOM_0x35` is visually confusing (looks like a hex value spliced into a name).
**Why it happens:** D-08 suggests this exact form.
**How to avoid:** Offer `PROTO_PHANTOM_35`/`_39` as a cleaner alternative at the gate; let the operator choose. Either compiles; the `_35` form avoids the ambiguity.
**Warning signs:** Reviewers double-taking on the token in the draft table.

### Pitfall 5: Renaming the frozen datasheet slugs
**What goes wrong:** The executor "helpfully" renames `0x08-EPROM-QUICK/` to match the new `EPROM_32PIN` name.
**Why it happens:** The mismatch looks like an inconsistency to fix.
**How to avoid:** The mismatch IS the DOC-02 record. Slugs are frozen (NAME-F1). Keep the slug column verbatim.
**Warning signs:** Any `git mv` under `datasheets/`.

## Code Examples

**Not applicable — no code is written in Phase 100.** The nearest thing to a "code example" is the shape of the revised name columns and the sample tokens (illustrative, final at the gate). Below is the *documentation* pattern for the revised Canonical bucket set table (the operator-approval artifact):

```markdown
<!-- Revised Canonical bucket set (Phase 100) — the single reviewable approval table -->
| hex | frozen slug (DOC-02 anchor) | PROTO_ token | display name | handler-family | phantom? |
|-----|----------------------------|--------------|--------------|----------------|----------|
| 0x05 | 0x05-FLASH-AMD-STD | PROTO_FLASH_5V_PAGE | Flash 5V page-write | flash4 (0x05) | no |
| 0x07 | 0x07-EPROM-STD | PROTO_EPROM_28PIN | UV/EE-EPROM 28-pin | eprom (0x07/08/0B) | no |
| 0x08 | 0x08-EPROM-QUICK | PROTO_EPROM_32PIN | UV/EE-EPROM 32-pin | eprom (0x07/08/0B) | no |
| 0x0B | 0x0B-EPROM-LEGACY | PROTO_EPROM_24PIN | Legacy 24-pin EPROM | eprom (0x07/08/0B) | no |
| 0x0E | 0x0E-SRAM-32PIN | PROTO_SRAM_32PIN | 32-pin battery-backed SRAM | sram (0x0E/27/28/29) | no |
| 0x29 | 0x29-SRAM-512K-1M | PROTO_SRAM_32PIN_LARGE ?? | 32-pin large SRAM 512K–1M | sram (0x0E/27/28/29) | no |
| 0x35 | (none) | PROTO_PHANTOM_35 | (phantom — 0 DB chips) | flash4 dispatch arm | YES |
| ... (all 12 real + 0x35/0x39) ... |
```

*(All name strings above are illustrative per CONTEXT §Specific Ideas — final values are settled at the NAME-02 operator gate. The `SRAM_32PIN_LARGE ??` marks the D-05 collision the operator resolves.)*

## State of the Art

| Old Approach (v1.16) | Current Approach (v1.19 Phase 100) | When Changed | Impact |
|----------------------|-------------------------------------|--------------|--------|
| Single "algorithm-axis name (col 2)" per bucket, minipro-heritage jargon (`AMD`, `QUICK`, `ALT`, `STD`) | 3-field entry (`PROTO_` token + display name + facet prose), chip-family/behavior axis, pin-count-primary | Phase 100 (this phase) | One field per downstream consumer; no re-derivation; jargon dropped (D-03). |
| Two divergent host vocabularies (`proto_display` map + `protocol_info_data` list), both missing 0x34, one carrying infeasible 0x11 | One canonical display-name set covering all 12 DB protocols incl. 0x34 | Phase 100 authors; Phase 102 applies | Host renders one consistent name per protocol (HOST-01). |
| Protocol ids as raw hex literals in `memory.cpp` | Named `PROTO_<NAME>` constants (authored here, defined Phase 101) | Phase 100 names; Phase 101 defines | Dispatch site reads by name; numbers unchanged (FW-01). |

**Deprecated/outdated:**
- The v1.16 col-2 mechanism-jargon tokens (`FLASH-AMD-STD`, `EPROM-QUICK`, etc.) — being *revised* (not deleted from history); they survive only as the frozen slug column (provenance/DOC-02 anchor).
- The pre-Phase-86 conflations (FM1608 "algorithm 40 = 0x28" decimal/hex confusion; X88C64 as UV-EPROM) — already retired in the doc; carry the corrected form forward.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | The illustrative name strings (`FLASH_5V_PAGE`, `EPROM_28PIN`, `SRAM_32PIN`, etc.) are acceptable to the operator | Code Examples / Specific Ideas | LOW — all names are explicitly settled at the NAME-02 gate; the operator has final say, so a wrong guess is corrected at approval, not shipped. |
| A2 | `PROTO_PHANTOM_35`/`_39` (numeric-suffix) is preferable to `PROTO_PHANTOM_0x35`/`_0x39` for readability | Firmware token feasibility | LOW — both compile; presented as an operator choice at the gate. |
| A3 | 0x34 should receive a display name even though its handler is not-implemented | Pitfall 3 | LOW — NAME-01 requires an entry for every DB protocol and 0x34 is in the DB; the CONTEXT discretion note confirms 0x34 needs a name. |

**Note:** All three assumptions are LOW-risk because the NAME-02 operator gate is the safety net — every name choice is confirmed by the operator before becoming authoritative. There are no unverified *facts* here (the DB set, dispatch chain, host divergences, and slug set are all `[VERIFIED]`).

## Open Questions

1. **Final 0x0E-vs-0x29 tiebreak suffix**
   - What we know: both are 32-pin SRAM; pin-count-only names them identically (D-05). 0x0E = battery-backed NVRAM (DS1245Y etc., 20 chips); 0x29 = 512K–1M large NVRAM (DS12xx `(TEST)` variants, 20 chips).
   - What's unclear: the exact suffix (`_LARGE`, `_512K_1M`, `_NVRAM` vs `_BBSRAM`, ...).
   - Recommendation: executor proposes `SRAM_32PIN` (0x0E) vs `SRAM_32PIN_LARGE` (0x29) in the draft; operator picks at the gate. Do NOT pre-decide (D-05 explicit).

2. **Phantom token spelling (`_0x35` vs `_35`)**
   - What we know: D-08 suggests `PROTO_PHANTOM_0x35`; both are valid C identifiers.
   - What's unclear: operator preference.
   - Recommendation: present both forms at the gate.

3. **0x34 name (`EEPROM_X88C64` vs `EEPROM_8051BUS`)**
   - What we know: XICOR X88C64P, 8051-multiplexed bus, PCB-blocked (FUT-01), not-implemented handler.
   - What's unclear: whether the operator prefers the part-number-derived name (`X88C64`) or the bus-behavior name (`8051BUS`), given D-03's behavior axis.
   - Recommendation: propose both; the behavior-axis form (`EEPROM_8051BUS`) is more D-03-consistent but `X88C64` matches the frozen slug — flag the tension at the gate.

## Environment Availability

**SKIPPED (Step 2.6): no external dependencies.** Phase 100 is a Markdown edit + git commit + a human decision. Required tools (text editor, git) are present; no runtimes, services, CLIs, databases, or package managers are involved.

## Validation Architecture

> `workflow.nyquist_validation` is absent from `.planning/config.json` → treated as enabled. However, this is a **docs-only + decision phase with no executable code** — there is no behavior to unit/integration test. Validation is verification-of-artifact, not automated tests.

### Test Framework
| Property | Value |
|----------|-------|
| Framework | None applicable — no code produced. (Firmware native suite `pio test -e native` and host `pytest`/`ruff` exist but Phase 100 changes neither codebase.) |
| Config file | n/a for this phase |
| Quick run command | `grep`-based artifact checks (see below) |
| Full suite command | n/a — no code changed; GATE-01/02/03 automated gates (`diff_db.py`, `check_dispatch.py`, constants-parity, golden traces) belong to Phases 101–103 that touch code. |

### Phase Requirements → Verification Map (artifact checks, not code tests)
| Req ID | Behavior | Verification Type | Check |
|--------|----------|-------------------|-------|
| NAME-01 | Every DB protocol + 2 phantoms has a 3-field entry | doc inspection | Revised Canonical bucket set table has 12 real + 2 phantom rows; each has PROTO_ token + display name; each §1.x has facet prose. `grep -c` row count. |
| NAME-02 | Operator explicitly approved; 0x0E/0x29 resolved | process/record | An approval record exists (plan `checkpoint:human-verify` completed; approval noted in commit/STATE); 0x0E and 0x29 have distinct names. |
| NAME-03 | One authoritative source; handler-family layer present | doc inspection | PROTOCOLS.md (revised in place) contains the handler-family column/table; no second source file created; frozen slug column retained. |

### Sampling Rate
- **Per edit:** re-render the Canonical bucket set table; eyeball row count (14) and column completeness.
- **Phase gate:** operator approval captured before commit-as-authoritative.

### Wave 0 Gaps
- None — no test infrastructure is needed for a docs/decision phase. The verification is human review of the rendered table + an approval record. (If the plan wants a mechanical guard, a tiny `grep` assertion that all 12 hex ids + 0x35/0x39 appear in the revised table, and that both 0x0E and 0x29 map to distinct tokens, is sufficient.)

## Security Domain

> `security_enforcement` is not disabled in config → nominally enabled. However, **Phase 100 introduces no attack surface**: no input parsing, no auth, no crypto, no network, no data storage, no code path. It authors human-readable names in a Markdown doc.

### Applicable ASVS Categories
| ASVS Category | Applies | Standard Control |
|---------------|---------|------------------|
| V2 Authentication | no | No auth surface. |
| V3 Session Management | no | No sessions. |
| V4 Access Control | no | No access control surface. |
| V5 Input Validation | no | No runtime input; the "input" is a human naming decision reviewed at a gate. |
| V6 Cryptography | no | No crypto. |

### Known Threat Patterns for this phase
| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| A name silently becomes a dispatch/lookup key, weakening the algorithm-first safety invariant | Tampering / Elevation | GATE-01 (numbers stay the dispatch key) — enforced in Phases 101–103, but Phase 100 must not author names that *invite* keying on strings. The `PROTO_<NAME> = 0x..` form (the label IS the number) preserves this. |
| Mis-naming a hazardous protocol (e.g. dropping the 12V-VPP hazard signal for 0x07/0x08/0x10) so a downstream reader under-estimates danger | Information disclosure / Repudiation | D-04 keeps voltage/hazard detail in the facet prose (field 3); the facet prose is preserved verbatim from the datasheet-cited §1.x, so hazard information is not lost even though the *name* is pin-count-primary. |

**Note:** the real safety-relevant enforcement (12V VPP hazard, fail-closed dispatch) is unchanged code that lives downstream; Phase 100 only ensures the *documentation* does not erase hazard signals from the facet prose.

## Sources

### Primary (HIGH confidence — direct in-repo verification, 2026-07-01)
- `firestarter_app/firestarter/data/chip_database.json` — parsed `algorithm` field: 12 protocols, 746 chips, exact set confirmed.
- `firestarter/src/proms/memory.cpp` (dispatch chain, lines ~106–170) — the many-to-one groupings + phantom 0x35/0x39 dispatch arm.
- `firestarter/src/proms/*.cpp` — `configure_*` function names (grep) grounding the handler-family layer.
- `firestarter/include/` (grep) — confirmed NO existing `PROTO_` token / protocol-id enum; `messages.h` DBG codes are a separate namespace.
- `firestarter_app/firestarter/ic_layout.py` — the two divergent host vocabularies (`proto_display` dict, `protocol_info_data` list); id coverage extracted.
- `firestarter/doc/PROTOCOLS.md` — full read; the preserve-vs-change map.
- `/workspaces/datasheets/` — directory listing confirming all 12 frozen slug folders.
- `firestarter/CLAUDE.md` — authoritative dispatch-order documentation + algorithm-handler table.

### Secondary (MEDIUM confidence)
- `.planning/REQUIREMENTS.md`, `.planning/STATE.md`, phase `100-CONTEXT.md` — requirement + decision provenance.

### Tertiary (LOW confidence)
- None. No web research was applicable to this codebase-internal naming phase.

## Metadata

**Confidence breakdown:**
- Protocol inventory / set: HIGH — parsed directly from the authoritative DB and cross-checked against dispatch code, slug folders, and the goal set (all agree).
- Handler-family layer: HIGH — grounded in the actual `configure_*` functions and `memory.cpp` dispatch.
- Downstream consumer touch points: HIGH — both host vocabularies read and their exact id coverage extracted; firmware token-namespace confirmed greenfield.
- Revise-in-place contract: HIGH — full read of the current doc.
- Final name strings: LOW-by-design — settled at the operator gate (this is a feature, not a gap).

**Research date:** 2026-07-01
**Valid until:** 2026-07-31 (stable — the DB set, dispatch chain, and doc structure are frozen for v1.19; re-verify only if `chip_database.json` or `memory.cpp` dispatch changes, which GATE-01/02 forbid this milestone).
