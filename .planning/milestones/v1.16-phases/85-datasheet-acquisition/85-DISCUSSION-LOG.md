# Phase 85: Datasheet Acquisition - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-06-25
**Phase:** 85-datasheet-acquisition
**Areas discussed:** Sourcing method, Folder keying + names, No-silicon representatives, Provenance policy

---

## Sourcing method

### Q1 — How should the datasheet PDFs be acquired?

| Option | Description | Selected |
|--------|-------------|----------|
| Claude fetches, you fill gaps | Claude curls obtainable PDFs, reports a gap list, operator supplies the rest | |
| Claude fetches everything | Claude attempts all PDFs autonomously, substituting compatible parts where exact unobtainable | ✓ |
| You supply all PDFs | Operator downloads all PDFs, Claude only organizes/indexes | |

**User's choice:** Claude fetches everything (→ D-01, D-02)
**Notes:** Network egress confirmed in devcontainer (curl of binary PDFs from archive.org works), so full autonomy is feasible.

### Q2 — If a datasheet genuinely can't be sourced?

| Option | Description | Selected |
|--------|-------------|----------|
| Document as gap, don't block | Record MISSING/UNSOURCED row with what was tried; phase still completes | ✓ |
| Hard requirement, escalate to you | Stop and ask operator to supply before close | |

**User's choice:** Document as gap, don't block (→ D-03)

---

## Folder keying + names

### Q3 — How should the folder tree be keyed?

| Option | Description | Selected |
|--------|-------------|----------|
| Per protocol bucket | One folder per hex bucket; shared buckets hold multiple chip PDFs; mirrors dispatch axis | (Claude's choice) |
| Per chip family | One folder per chip (17 total), 1 PDF each | |

**User's choice:** "You decide" → Claude chose **per protocol bucket** (→ D-04), as it's the format the success criteria already imply and it matches the Phase 86 vocabulary / Phase 89 ledger axis.

### Q4 — What name should the folders use (Phase 86 owns canonical naming)?

| Option | Description | Selected |
|--------|-------------|----------|
| Research's proposed names | Use names from research/SUMMARY.md (EPROM-STD, FLASH-AMD-STD, …); rename trivial if Phase 86 changes one | ✓ |
| Pure hex only | Folders are bare 0x05/, 0x06/, … | |

**User's choice:** Research's proposed names (→ D-05)

---

## No-silicon representatives

### Q5 — What should drive the choice of representative part for the 6 no-silicon buckets?

| Option | Description | Selected |
|--------|-------------|----------|
| Best-documented exemplar | Pick the part with the clearest datasheet for the bucket's algorithm; Claude picks, operator reviews | ✓ |
| Parts you'd actually acquire | Bias toward buyable parts for future bench validation | |
| DB-member-driven | Pick from actual chip_database.json members of the protocol_id | |

**User's choice:** Best-documented exemplar (→ D-06). DB-membership retained as a soft tie-breaker.

---

## Provenance policy

### Q6 — How should compatible/substitute datasheets be recorded?

| Option | Description | Selected |
|--------|-------------|----------|
| Flag substitutions explicitly | README marks non-exact matches as representative/substitute, names the original | ✓ |
| Treat substitute as equivalent | File compatible parts with no special flag | |

**User's choice:** Flag substitutions explicitly (→ D-07)

### Q7 — What provenance metadata beyond the DSHEET-03 index columns?

| Option | Description | Selected |
|--------|-------------|----------|
| Source URL + retrieval date | URL + fetch date + substitute flag | (Claude's choice) |
| Minimal — filename + flag only | Just filename and substitute flag | |
| Full — URL, date, revision, vendor | Full archival record per row | |

**User's choice:** "You decide" → Claude chose **Source URL + retrieval date + substitute flag** (→ D-08), the middle ground that pairs with the explicit-substitution flag without bloating 17 rows.

---

## Claude's Discretion

- Folder keying (Q3) — resolved to per-protocol-bucket (D-04).
- Provenance depth (Q7) — resolved to URL + retrieval date + substitute flag (D-08).
- Exact README column layout and PDF filename convention left to planner/executor within the recorded constraints.

## Deferred Ideas

- Canonical protocol naming → Phase 86.
- DB decode corrections (FM1608 0x40→0x28, 0x34 type) → Phase 86.
- Per-protocol bench validation / ledger → Phase 89.
- "Parts I'd actually acquire" representative bias → considered, not chosen; revisit only if a future milestone scopes acquiring no-silicon parts.
