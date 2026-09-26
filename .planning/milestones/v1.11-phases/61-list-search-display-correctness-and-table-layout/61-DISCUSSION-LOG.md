# Phase 61: List/Search Display Correctness and Table Layout - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-06-10
**Phase:** 61-list-search-display-correctness-and-table-layout
**Areas discussed:** Name column sizing, VPP column width + semantics, Type-label parity mechanism

---

## Gray-area selection

Offered 4 areas; user selected 3 (Test coverage left out — settled by ROADMAP mandate).

| Area | Discussed |
|------|-----------|
| Name column sizing | ✓ |
| VPP column width + semantics | ✓ |
| Type-label parity mechanism | ✓ |
| Test coverage shape | (captured as locked-by-roadmap, not discussed) |

---

## Name column sizing

| Option | Description | Selected |
|--------|-------------|----------|
| Hybrid: grow to a cap, ellipsis beyond | Auto-size to widest name in result set, capped, ellipsis past cap | ✓ |
| Auto-grow to widest (no cap) | Expand to longest name, no truncation; risks terminal wrap on 73-char alias rows | |
| Keep fixed 13, truncate + ellipsis | Unchanged width, truncate any name >13 | |

**User's choice:** Hybrid: grow to a cap, ellipsis beyond.

Follow-ups:

| Sub-decision | Options | Selected |
|--------------|---------|----------|
| Cap behavior | Dynamic within [13, cap] ✓ / Fixed at cap always | Dynamic within [13, cap] |
| Cap value | 24 / **20** ✓ / 32 | 20 |

**Notes:** 242/743 names exceed today's 13-wide column; widest is a 73-char comma-joined alias
row. Floor = 13 (today's default). Width adapts per query within [13, 20]; names >20 clip with
ellipsis.

---

## VPP column width + semantics

| Option | Description | Selected |
|--------|-------------|----------|
| Dynamic, floor 4 (same rule as Name) | clamp(widest VPP string, 4, —) | |
| Fixed at 5 | Always render VPP at 5 chars | ✓ |

**User's choice (width):** Fixed at 5 (every voltage string is 5 chars; today's 4 overflows).

| Option | Description | Selected |
|--------|-------------|----------|
| Yes — parity with info (WR-01) | Show vpp_mv-derived voltage when vpp_mv>0 AND not SRAM; else `-` | ✓ |
| Discuss a different rule | Tune the gate | |

**User's choice (rule):** Yes — parity with info (WR-01). SRAM always shows `-`; 12V EEPROM-family
shows voltage; 5V parts (vpp_mv=0) show `-`.

**Notes:** Same gate `info` uses, so list/info can never disagree on VPP.

---

## Type-label parity mechanism

| Option | Description | Selected |
|--------|-------------|----------|
| Single source of truth (shared helper) | Add electrical.type to _map_data; both list and info resolve label through one shared SpecBuilder helper | ✓ |
| Targeted change (list reads electrical.type inline) | Smaller diff, but keeps two copies of the map | |

**User's choice:** Single source of truth — structurally prevents a future IN-01 recurrence.

| Option | Description | Selected |
|--------|-------------|----------|
| Yes — same fallback as info | Protocol-based label via get_chip_type_string when electrical.type absent | ✓ |
| Discuss a different fallback | | |

**User's choice (fallback):** Yes — same fallback as info (`build_specifications` L502–508).

**Notes:** `_map_data` does not emit the raw `electrical.type` string today; this phase adds it so
list/search results expose the ground-truth field.

---

## Claude's Discretion

- Exact ellipsis rendering for the Name cap and whether the ellipsis counts toward the 20 cap.
- Precise signature/name/location of the shared label helper and the mapped-dict key for
  `electrical.type`.
- Whether the width-floor/no-break test is dedicated or folded into the parametrized test.
- Column order / divider style / header text stay as-is unless a sizing change forces a minimal
  adjustment (not a redesign).

## Deferred Ideas

- Reworking how alias-row names are stored/split (DB-content artifact from build_db.py/infoic.xml)
  — separate database-pipeline concern, not this host-display phase.
- Firmware electrical-erase support — separate firmware backlog item (carried from Phase 60).
