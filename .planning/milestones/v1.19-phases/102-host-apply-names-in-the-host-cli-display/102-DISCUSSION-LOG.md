# Phase 102: HOST — Apply Names in the Host CLI Display - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-07-01
**Phase:** 102-host-apply-names-in-the-host-cli-display
**Areas discussed:** Consolidation structure, Name string form, Description prose scope, Coverage reconciliation

---

## Consolidation structure

| Option | Description | Selected |
|--------|-------------|----------|
| Single canonical map | One `{proto_id: name}` dict both structures draw from; one edit point, prevents re-divergence | ✓ |
| Align two tables in place | Edit both structures' strings to match; smaller diff, can drift again | |

**User's choice:** Single canonical map
**Notes:** Embodies HOST-01 "consolidate"; same anti-divergence pattern as the existing IN-01 `resolve_type_label` fix.

---

## Name string form

| Option | Description | Selected |
|--------|-------------|----------|
| Verbatim | Col-2 strings exactly, Unicode em/en dashes and all | |
| ASCII-normalized | Same names, `—`/`–` normalized to ASCII `-` in host source | ✓ |

**User's choice:** ASCII-normalized
**Notes:** Safest for terminal/pipe/grep. Recorded as a defined punctuation deviation from PROTOCOLS.md col-2 (relevant to Phase 103's divergence record).

---

## Description prose scope (102 vs 103 boundary)

| Option | Description | Selected |
|--------|-------------|----------|
| Name-only, leave bullets | Fix only the name/type field; leave stale description bullets for Phase 103 | ✓ |
| Replace bullets with facet prose | Also swap bullets for PROTOCOLS.md §1 facet prose now (overlaps 103) | |
| Drop bullets entirely | Remove description_points; name + ID only | |

**User's choice:** Name-only, leave bullets
**Notes:** Tightest scope; HOST-01 is "one consistent name", prose reconciliation is DOC-01 (Phase 103).

---

## Coverage reconciliation

| Option | Description | Selected |
|--------|-------------|----------|
| Full reconcile | Add 0x34, drop stale 0x11, keep phantoms 0x35/0x39 excluded | ✓ |
| Names-only, no coverage change | Only rewrite existing entries' strings; leave gaps/staleness | |

**User's choice:** Full reconcile
**Notes:** Makes host coverage match the canonical 12-protocol DB set. 0x34 (X88C64) has 1 DB chip and can surface in `info`; 0x11 (FWH) is infeasible/not in DB; phantoms already route to `not_implemented` (Phase 57 DEC-05).

---

## Claude's Discretion

- Exact placement/form of the canonical map (module-level dict vs. method) and how the name is threaded through the `Protocol:` line's `type` slot — implementer's call, provided the single-source rule and canonical strings hold.

## Deferred Ideas

- Description-bullet prose reconciliation → Phase 103 (DOC-01).
- Accept protocol name/alias as CLI input → out of scope, NAME-F2 (GATE-03 keeps chip selection by part number).
