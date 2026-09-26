# Phase 100: NAME — Canonical Protocol Name Set + Operator Approval - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-07-01
**Phase:** 100-name-canonical-protocol-name-set-operator-approval
**Areas discussed:** Name schema, Naming style, Source location, Phantoms & family

---

## Name schema (entry structure)

| Option | Description | Selected |
|--------|-------------|----------|
| Structured (3 fields) | C-safe constant token + short human display name + behavioral facet prose; one field per downstream consumer | ✓ |
| Single canonical name | One token both C-safe and readable, used verbatim everywhere | |
| Two fields (token + display) | C-token + display name; facet prose left in §1 body | |

**User's choice:** Structured (3 fields).
**Notes:** Each protocol row serves Phase 101 (field 1 = C token), Phase 102 (field 2 = display), Phase 103 (field 3 = facet prose) with no re-derivation.

## Name schema (C-token form)

| Option | Description | Selected |
|--------|-------------|----------|
| `PROTO_<NAME>` | e.g. `PROTO_EPROM_STD = 0x07` — prefix namespaces protocol ids | ✓ |
| `PROTOCOL_<NAME>` | Fully-spelled prefix; more verbose | |
| Bare `<NAME>` | Matches datasheets/ slug tokens exactly; collision risk | |

**User's choice:** `PROTO_<NAME>`.
**Notes:** Prefix reads clearly at the dispatch site (`handle->protocol == PROTO_...`).

---

## Naming style (axis)

| Option | Description | Selected |
|--------|-------------|----------|
| Chip-family / behavior | Name by what the chip is + how it programs; drop AMD/QUICK jargon | ✓ |
| Keep v1.16 tokens, fix wrong ones | Preserve slug tokens as canonical names, correct only misleading ones | |
| Discuss per-bucket | Walk all 12+2 buckets individually | |

**User's choice:** Chip-family / behavior.
**Notes:** Deliberate departure from the minipro-heritage jargon (`FLASH-AMD-STD`, `EPROM-QUICK`). Diverges from frozen datasheets/ slugs → documented per DOC-02.

## Naming style (family discriminator)

| Option | Description | Selected |
|--------|-------------|----------|
| Pin count + voltage | e.g. `EPROM_28PIN_13V` | |
| Pin count only | e.g. `EPROM_28PIN`; voltage → facet prose | ✓ |
| Decide during authoring | Lock axis, defer exact discriminator | |

**User's choice:** Pin count only.
**Notes:** Voltage/hazard detail moves to facet prose (field 3). Surfaced a collision: 0x0E and 0x29 are both 32-pin SRAM → pin-count-only names them identically.

## Naming style (0x0E vs 0x29 collision tiebreaker)

| Option | Description | Selected |
|--------|-------------|----------|
| Size suffix on 0x29 | `SRAM_32PIN` vs `SRAM_32PIN_LARGE` | |
| Role words | `SRAM_NVRAM` vs `SRAM_LARGE` | |
| Decide during authoring | Note collision as must-resolve; settle in draft table at gate | ✓ |

**User's choice:** Decide during authoring.
**Notes:** Captured as a must-resolve (CONTEXT D-05); operator settles the final suffix at the NAME-02 approval gate.

---

## Source location

| Option | Description | Selected |
|--------|-------------|----------|
| Revise PROTOCOLS.md in place | Update col-2 to 3-field set; it is the approval artifact | ✓ |
| New dedicated doc | Fresh PROTOCOL-NAMES.md as source of truth | |
| Machine-readable data file | protocol_names.json/yaml both repos consume | |

**User's choice:** Revise `firestarter/doc/PROTOCOLS.md` in place.
**Notes:** Already the canonical GitHub-visible vocabulary; matches NAME-03's "one identifiable source" and is what the operator approves.

## Source location (divergence recording)

| Option | Description | Selected |
|--------|-------------|----------|
| Keep slug column, add new columns | hex \| frozen slug \| `PROTO_` token \| display \| facet | ✓ |
| Replace col-2, note divergence separately | Swap col-2, add a divergence subsection | |
| Decide during authoring | Lock approach, defer layout | |

**User's choice:** Keep slug column + add new columns.
**Notes:** Retained frozen-slug column IS the DOC-02 divergence record (old-slug vs new-name visible at a glance).

---

## Phantoms & family (phantom naming)

| Option | Description | Selected |
|--------|-------------|----------|
| Distinct phantom tokens | `PROTO_PHANTOM_0x35`/`_0x39`, flagged non-real/dispatch-preserved | ✓ |
| Alias to flash4 family name | Reuse 0x05's family name for the phantom arm | |
| Decide during authoring | Note must-be-marked-non-real, defer token | |

**User's choice:** Distinct phantom tokens.
**Notes:** Firmware dispatch line (`memory.cpp:122`) reads honestly; no mistaking phantoms for real protocols.

## Phantoms & family (handler-family layer)

| Option | Description | Selected |
|--------|-------------|----------|
| Yes — define family names here | Small handler-family layer for Phase 101 FW-03 renames, from this source | ✓ |
| No — derive in Phase 101 | Phase 100 defines per-number names only | |
| Decide during authoring | Include family column for approve/strike at gate | |

**User's choice:** Yes — define family names here.
**Notes:** FW-03 handler renames (`configure_flash3`/`flash4`/`eeprom28c`) draw from the operator-approved source, not invented mid-refactor. Family groupings fixed by existing many-to-one dispatch.

---

## Claude's Discretion

- Exact per-bucket final name strings + the 0x0E/0x29 tiebreaker (D-05): proposed by executor in the draft table, settled at the NAME-02 approval gate.
- 0x34 (X88C64) name: executor proposes a behavior-axis name consistent with D-03; operator confirms.

## Deferred Ideas

- **NAME-F1** — rename `datasheets/` folder slugs to match new vocabulary (out of scope; only on operator instruction).
- **NAME-F2** — accept protocol name/alias as CLI input (out of scope; chip selection stays by part number, GATE-03).
- **Infeasible-bucket naming (0x11/0x2A/0x2B/0x2C)** — not in `chip_database.json`, outside NAME-01 scope; Phase 101 may reuse §2.2 "honest non-protocols" labels if it needs constants for that dispatch arm.
