# Phase 103: DOCS — Reconcile Prose + Divergence Record - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-07-01
**Phase:** 103-docs-reconcile-prose-divergence-record
**Areas discussed:** §1 heading treatment, jargon-purge boundary (+ reconciliation follow-up), INV matrix reconciliation, divergence record form

---

## §1 heading treatment

| Option | Description | Selected |
|--------|-------------|----------|
| Rename to new name + update anchors | Headings → new display name/token; update all §3 cross-links + TOC anchors; slug stays via existing "Folder slug (col 1)" line | ✓ |
| Rename, keep slug shown inline in heading | Heading shows new name AND frozen slug inline; noisier; still needs anchor updates | |
| Keep slug headings, scrub prose only | Leave headings as-is; reconcile prose + INV only; no anchor churn but headings still read as jargon | |

**User's choice:** Rename to new name + update anchors (D-01)
**Notes:** Drives anchor/TOC/cross-link churn — CONTEXT records "no broken anchors" as a hard completeness constraint (grep `#1` links after rename).

---

## Jargon-purge boundary

| Option | Description | Selected |
|--------|-------------|----------|
| Scrub slug-derived bucket labels ONLY | Remove only heading/prose bucket-label heritage; keep approved name + datasheet terms + §2 provenance | |
| Aggressive purge of all AMD/minipro | Remove every occurrence including manufacturer/datasheet refs and §2 provenance | ✓ (intent refined below) |
| Scrub headings + dead cruft only (conservative) | Headings + genuinely dead labels only; leave accurate behavior-prose refs | |

**User's choice:** Aggressive purge — refined via follow-up (see below).
**Notes:** Raw "aggressive purge of all" collided with three locked/frozen items (approved 0x06 display name, frozen slug column strings, §2 minipro-provenance prose). Surfaced the conflict rather than recording a scope-breaking decision.

### Follow-up — Purge scope reconciliation

| Option | Description | Selected |
|--------|-------------|----------|
| Aggressive everywhere EXCEPT the 3 locked items | Scrub aggressively from headings + facet prose (incl. "Unlike AMD flash" rephrasing); retain verbatim the approved 0x06 name, frozen slug strings, §2 provenance | ✓ |
| Also re-open the 0x06 name / slugs | True total purge — re-opens Phase 100 gate + triggers NAME-F1; expands milestone scope | |
| Scrub headings + dead cruft only (conservative) | Lower churn; leaves technically-accurate AMD/minipro refs | |

**User's choice:** Aggressive everywhere EXCEPT the 3 locked items (D-02)
**Notes:** Maximal purge that stays inside locked v1.19 scope. The three retentions are the traps a naive find/replace would hit.

---

## INV-01..09 matrix reconciliation

| Option | Description | Selected |
|--------|-------------|----------|
| Add token alongside hex | Augment each row's behavior text with the PROTO_ token/name next to the hex; fix §3 cross-link anchors | ✓ |
| Keep hex-precise, fix cross-links only | Leave descriptions keyed by raw hex; only update anchors | |

**User's choice:** Add token alongside hex (D-03)
**Notes:** Hex stays (invariant/dispatch key); name added for legibility. `INV-0N` ids + native-test function names stay byte-identical (SAFE-02 grep-intact).

---

## Divergence record form

| Option | Description | Selected |
|--------|-------------|----------|
| Add a dedicated divergence callout | Short "Name ↔ Slug Divergence" subsection: slugs frozen (NAME-F1), top-table slug column = canonical map, host ASCII-dash deviation (Phase 102 D-02) recorded | ✓ |
| Existing slug column is sufficient | Frozen-slug column already satisfies "explicitly recorded"; add a one-line note only | |

**User's choice:** Add a dedicated divergence callout (D-04)
**Notes:** Makes DOC-02 unambiguous in one place; also captures the host punctuation deviation.

---

## Claude's Discretion

- Exact heading wording (token-first vs. display-name-first vs. both).
- Placement/heading level of the D-04 divergence callout.
- Exact rephrasing of purged behavior-prose sentences.
- Plan/wave decomposition and milestone-close sequencing.

## Deferred Ideas

- NAME-F1 — rename `datasheets/` folder slugs (recorded as divergence, not resolved).
- NAME-F2 — accept protocol name/alias as CLI input (GATE-03 keeps part-number selection).
- Lockstep beta cut `3.0.0b11` + gitlink bump — operator-gated; gitlinks PINNED.
