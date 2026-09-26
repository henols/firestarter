# Phase 61: List/Search Display Correctness and Table Layout - Context

**Gathered:** 2026-06-10
**Status:** Ready for planning

<domain>
## Phase Boundary

Route the `firestarter list` / search table's **Type** label and **VPP** column through
the database `electrical.type` ground truth — the same source `firestarter info` uses as of
Phase 60 — so the two views **agree per chip** for the EEPROM-family parts reclassified in
Phases 59/60 (W27C512, SST27VF512, SST27SF512, W27C257, …), and SRAM shows **no spurious VPP**
(SRAM carries `vpp_mv=12000` as an infoic.xml decode artifact, not a real programming voltage).
This resolves the **IN-01** follow-up (`info-list-type-vpp-divergence`) raised in the Phase 60
code review.

**Also** adjust the list/search table sizing so it **fits all columns without breaking/wrapping**
and is **never rendered narrower than its current default width** (today's per-column widths are
the floor).

**HOST-ONLY.** Primary surface is `firestarter_app/firestarter/eprom_info.py`
(`print_eprom_list_table`) plus the `database._map_data` / `ic_layout.SpecBuilder` plumbing the
shared label path requires. No firmware changes.

**Root cause this phase fixes (IN-01):** `print_eprom_list_table` derives Type from the int
`mem_type` (`get_chip_type_string(ic.get("type"))` → "EPROM"/"SRAM") and gates VPP on
`ic.get("type") == 1`, while `info` (Phase 60) derives Type from the `_ELECTRICAL_TYPE_LABEL` map
keyed on `electrical.type`. The two views disagree on Type and VPP for the EEPROM-family chips.
`_map_data` does not currently carry the raw `electrical.type` string into mapped/search results,
so the list cannot reach the ground-truth field today.

</domain>

<decisions>
## Implementation Decisions

### Name column sizing
- **D-01:** Name column uses a **dynamic width clamped to `[13, 20]`** — width =
  `clamp(widest name in the current result set, 13, 20)`. Names longer than 20 are **truncated
  with an ellipsis**. Rationale: 242/743 names exceed today's 13-wide column (widest is a 73-char
  comma-joined alias row like `M48T08,M48T08Y,…`); an uncapped grow-to-content column would push
  the table past terminal width and wrap. `13` is the floor (today's default — never narrower);
  `20` fits virtually all single-part names, only the multi-alias rows clip. Width adapts
  per-query: a search returning only short names stays tight at 13.

### VPP column (width + display rule)
- **D-02:** VPP column width is **fixed at 5** (every voltage string — `12.0v`, `13.0v`, `12.5v`,
  `18.0v` — is 5 chars; today's 4-wide column overflows). Stable alignment, one char wider than
  today even for all-`-` result sets. (Floor honoured: 4 → 5 is wider, never narrower.)
- **D-03:** VPP **display rule is parity with the Phase 60 `info` WR-01 fix**: show the
  `vpp_mv`-derived voltage when `vpp_mv > 0` **AND** `electrical.type != "SRAM"`; otherwise show
  `-`. Consequence: 12V EEPROM-family chips (W27C512, SST27VF512, …) show their voltage; **SRAM
  always shows `-`** (kills the spurious-12V defect the ROADMAP calls out); 5V parts with
  `vpp_mv=0` show `-`. Use the **same gate** `info` uses so the two views can never disagree on VPP.

### Type-label parity path (single source of truth)
- **D-04:** Achieve parity via a **single source of truth**, not a parallel implementation:
  1. `database._map_data` carries the raw **`electrical.type` string** through into the mapped
     dict (so `search_eprom` / list results expose it — it is not emitted today; see code_context).
  2. **Extract the `_ELECTRICAL_TYPE_LABEL` lookup + protocol fallback into one shared helper**
     (a method on `SpecBuilder` in `ic_layout.py`) that **both** `info` (`build_specifications`)
     and the list (`print_eprom_list_table`) call. This structurally prevents a future IN-01
     recurrence — the label can only be computed in one place.
- **D-05:** **Fallback is identical to `info`** (`build_specifications` L502–508): when
  `electrical.type` is absent/empty (legacy user-override DB entries), fall back to the
  protocol-based label via `get_chip_type_string(type_int, protocol_id)`. Never crash on legacy
  entries; keep list/info parity even for override chips.

### Test coverage (locked by ROADMAP mandate — not separately discussed)
- **D-06:** Add a **parametrized list-view test** (reuse the Phase 60 fixture sets):
  - **EEPROM display set** (must show EEPROM / correct Type + voltage): W27C512, SST27VF512,
    SST27SF512, W27C257.
  - **UV-EPROM control set** (must still show UV-EPROM): M27C512, 27C256, 2764.
  - **SRAM control** (must show Type=SRAM and VPP=`-`, no spurious 12V).
  Assert list Type/VPP **equal** what `info` produces for the same chip (the parity guarantee).
- **D-07:** Add a **no-break / width-floor assertion**: the rendered table neither breaks
  (no column overflow past its width; rows align to the divider) nor shrinks any column below
  today's default width (Name ≥ 13, Manufacturer 17, Pins 5, Chip ID 11, Type 12, VPP ≥ 5).

### Claude's Discretion
- The exact ellipsis rendering for the Name cap (e.g. `M48T08,M48T08Y,M4…` vs `...`) and whether
  the ellipsis byte counts toward the 20 cap or sits outside it.
- The precise mechanism/signature of the shared label helper (D-04) — name, where it lives on
  `SpecBuilder`, and how the raw `electrical.type` field is keyed in the mapped dict (e.g.
  `electrical-type`).
- Whether the width-floor/no-break test (D-07) is a dedicated test or assertions folded into the
  parametrized test (D-06).
- Column order, divider style, and header text stay **as today** unless a sizing change forces a
  minimal adjustment — this is not a table redesign.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase scope
- `.planning/ROADMAP.md` §"Phase 61: List/Search Display Correctness and Table Layout" (Phase
  Details, ~L618) and the Active-Milestone one-liner (~L181) — goal, the IN-01 resolution, the
  table-sizing requirement (fit-without-breaking + never-narrower-than-today floor), and the
  mandated parametrized list test.

### The divergence being resolved + the carried-forward decisions
- `.planning/phases/60-display-layer-decode-correctness/60-REVIEW.md` §IN-01 (the
  `info` vs `list` Type/VPP divergence this phase fixes) and §WR-01 (the spurious-SRAM-VPP fix
  whose gate D-03 reuses).
- `.planning/phases/60-display-layer-decode-correctness/60-CONTEXT.md` — D-01 (curated
  `electrical.type → label` map, the Type-label source of truth), D-07 (VPP sourced from
  `vpp_mv`, not `flags`). Phase 61 applies these same decisions to the list view.

### The code to change (host, `firestarter_app/`)
- `firestarter_app/firestarter/eprom_info.py` — `print_eprom_list_table` (L320–344): the divider/
  header/row f-strings with fixed column widths, the `vpp_str` gate (`ic.get("type") == 1`, L334–
  336), and the `get_chip_type_string(ic.get("type"))` Type derivation (L337). `EpromSpecBuilder`
  is passed in as `spec_builder`.
- `firestarter_app/firestarter/ic_layout.py` — `_ELECTRICAL_TYPE_LABEL` (L470–475),
  `build_specifications` (L477; the label resolution at L500–508 to extract into a shared helper),
  `get_chip_type_string` (L203, the protocol/int fallback).
- `firestarter_app/firestarter/database.py` — `_map_data` (emits `type` int, `vpp_volts`,
  `vpp_mv`, `protocol-id`, `info_flags`; **does NOT emit the raw `electrical.type` string today** —
  D-04 adds it) and `search_eprom` (returns `_map_data(...)` results — the list data source).
- `firestarter_app/firestarter/data/chip_database.json` — decode ground truth; each record's
  `electrical.type` (`EEPROM` / `Flash/EEPROM` / `UV-EPROM` / `SRAM`) and `electrical.vpp_mv`.

### Tests
- `firestarter_app/tests/test_eprom_info.py` — existing presenter test patterns + the
  `EpromDatabase(skip_local_override=True)` DB fixture and the Phase 60 EEPROM/UV-EPROM/SRAM
  parametrized sets to reuse for D-06/D-07.

### Background / data-flow + tooling gate
- `firestarter_app/CLAUDE.md` — canonical data flow (`build_db.py → chip_database.json →
  _map_data → display`) and the tooling gate. **`ic_layout.py` and `eprom_info.py` are NOT in the
  strict-mypy set** (8 modules) — changes there need ruff-clean + non-strict mypy + `pytest
  --cov-fail-under=70`, not strict annotations.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `EpromSpecBuilder` (`ic_layout.py`) is already passed into `print_eprom_list_table` as
  `spec_builder` — the shared label helper (D-04) lives here and the list already has a handle to
  it. No new wiring to reach it.
- The Phase 60 `_ELECTRICAL_TYPE_LABEL` map + `info`'s fallback chain are the exact logic to
  share — extract, don't reinvent.
- `tests/test_eprom_info.py` already has `db` / `presenter` fixtures and Phase 60's
  EEPROM/UV-EPROM/SRAM parametrized sets.

### Established Patterns
- Data flow: `search_eprom` → `_map_data(ic_config, manufacturer)` → list rows. The list consumes
  **mapped** data (same shape as `get_eprom`), so the cleanest plumbing for D-04 is to have
  `_map_data` carry `electrical.type` into the mapped dict — both list and `info` then read one
  field uniformly.
- `info`'s VPP/erasable derivation already reads `electrical.type` + `vpp_mv`; D-03 mirrors that
  gate exactly.

### Integration Points
- CLI: `firestarter list` / `firestarter search <q>` → `db.search_eprom(...)` →
  `print_eprom_list_table(results, presenter.spec_builder)`.
- Concrete width facts (from `chip_database.json`, 743 chips): Name 4–73 chars (242 > 13, widest
  is a 73-char alias row); Manufacturer max 16 (fits 17); every VPP string is 5 chars; the four
  electrical Type labels max at `Flash/EEPROM` = 12 (exactly the current 12-wide Type column).

### Risk / landmine (FLAG for planner — verify, don't assume)
- The list uses `logger.info(...)` for output. The mandated no-break/width-floor test (D-07) must
  capture that output (caplog / capsys) the way `test_eprom_info.py` already does for the `info`
  snapshot tests — confirm the capture mechanism rather than assuming `print`.

</code_context>

<specifics>
## Specific Ideas

- EEPROM display set (list must show EEPROM, correct VPP): **W27C512, SST27VF512, SST27SF512,
  W27C257**.
- UV-EPROM control set (must still show UV-EPROM): **M27C512, 27C256, 2764**.
- SRAM control: must show **Type=SRAM, VPP=`-`** (no spurious 12V), despite `vpp_mv=12000`.
- Name cap = **20** chars, floor **13**; VPP fixed **5**.
- Parity is the acceptance bar: list Type/VPP must **equal** `info` Type/VPP for the same chip.

</specifics>

<deferred>
## Deferred Ideas

- **How alias-row names are stored/displayed** (the 73-char comma-joined `M48T08,M48T08Y,…`
  entries are a DB-content artifact from `build_db.py`/infoic.xml). D-01 handles them by clip +
  ellipsis in the list; reworking how aliases are split into separate DB rows is a separate
  database-pipeline concern, not this host-display phase.
- **Firmware electrical-erase support** — still the separate firmware backlog item from Phase 60;
  untouched here.

None other — discussion stayed within phase scope.

</deferred>

---

*Phase: 61-list-search-display-correctness-and-table-layout*
*Context gathered: 2026-06-10*
