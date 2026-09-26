# Phase 87: Naming + Documentation Pass - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-06-25
**Phase:** 87-naming-documentation-pass
**Areas discussed:** Invariant matrix home, Gap-fill test rigor, Comment + cite format, PROTOCOLS.md depth

---

## Pre-selection: which areas to discuss

Operator selected ALL four open areas. The doc location (`firestarter/doc/PROTOCOLS.md`)
and the two-name scheme (keep `datasheets/` slugs + add descriptive name, no folder
renames) were already locked during the Phase 86 discussion and were NOT re-asked.

---

## Invariant matrix home

| Option | Description | Selected |
|--------|-------------|----------|
| In PROTOCOLS.md + stable IDs | Matrix section in the single canonical PROTOCOLS.md; each invariant gets INV-01..09 IDs referenced in native test names so 88/89 can grep the contract | ✓ |
| Standalone INVARIANTS.md | Dedicated separate doc; cleaner separation but a second doc to sync | |
| Test docstrings only | No prose matrix; derived from grepping test tags; most DRY, least browsable | |

**User's choice:** In PROTOCOLS.md + stable IDs (D-05)
**Notes:** Keeps one source of truth while wiring the SAFE-02 recompose contract to live tests.

---

## Gap-fill test rigor

| Option | Description | Selected |
|--------|-------------|----------|
| Minimal targeted assertion | Pin the one observable behavior per invariant; full golden traces are Phase 88's job | ✓ |
| Behavior + boundary | Assert behavior AND its edge; middle ground, more effort | |
| Full register trace now | Capture full golden traces this phase; pulls Phase 88 work forward, scope-bleed risk | |

**User's choice:** Minimal targeted assertion (D-06)
**Notes:** Explicitly avoids duplicating Phase 88's golden-trace oracle.

---

## Comment + cite format

| Option | Description | Selected |
|--------|-------------|----------|
| File header + anchored cite | One rationale header per handler file, citing datasheet by filename AND section/page | ✓ |
| Per-function comments | Comment at each handler function; finer-grained but scattered/verbose | |
| File header, filename-only | One header per file, filename-only citation; lighter, less verifiable | |

**User's choice:** File header + anchored cite (D-07)
**Notes:** Anchored citations make the "why" verifiable; full prose stays in PROTOCOLS.md.

---

## PROTOCOLS.md depth

| Option | Description | Selected |
|--------|-------------|----------|
| Per-protocol sections + non-proto section | Section per bucket with NAME-01 four facets; phantom/infeasible grouped in "Honest non-protocols" | ✓ |
| Compact master table | One row per bucket; scannable but cramped for prose | |
| Master table + detail sections | Both summary table and detail sections; complete but longest, some duplication | |

**User's choice:** Per-protocol sections + non-proto section (D-08)
**Notes:** —

---

## Claude's Discretion

- Exact INV-0x naming convention (as long as PROTOCOLS.md IDs and test names match + grep).
- Heading/ordering structure within PROTOCOLS.md.
- Which native test files host the gap-fill assertions + assertion mechanics.
- Datasheet anchor precision where a datasheet lacks clean section numbering.

## Deferred Ideas

- Per-family register golden traces + dispatch-mirror invariant test → Phase 88.
- Primitive recompose (P7→P4→P3→P5) → Phase 89.
- Per-protocol bench validation + PROTOCOL-LEDGER → Phase 90.
- 0x34 X88C64 programming handler → still PCB-blocked (FUT-01); only documented here.
