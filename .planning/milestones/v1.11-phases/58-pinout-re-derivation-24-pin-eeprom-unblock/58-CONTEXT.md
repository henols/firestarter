# Phase 58: Pinout Re-derivation + 24-pin EEPROM Unblock - Context

**Gathered:** 2026-06-08
**Status:** Ready for planning

<domain>
## Phase Boundary

Rebuild `resolve_pinout_key` in `firestarter_app/tools/build_db.py` so chip→pinout assignment is a **principled, fully data-driven function of decoded minipro fields** — retiring the survey-built `PIN_MAP_TO_PINOUT` / `PIN_MAP_PROTO_TO_PINOUT` / `DIP28_VARIANT_MAP` guess tables — and safely unblock the 9 AT28C04/AT28C16 24-pin EEPROMs via a dedicated `DIP24_2816` pinout + `algorithm=0x0D`, with a completed SR-1 safety review.

**HOST-only.** Firmware sub-repo untouched (`configure_eeprom28c` already handles these chips — see code insights). Correctness is proven by minipro-source cross-check; bench validation is deferred to v2 (BENCH-01). Live XML fetch + frozen-output baseline philosophy from Phase 56 (D-01/D-03) carries forward unchanged.

**Requirements:** PIN-01, PIN-02, PIN-03.

**The defining principle (operator, this session):** *the pin maps must be easily found and mapped without any special code for any IC when the database is built.* No per-IC names, no per-family lookup tables, no hardcoded override patches anywhere in `build_db.py`. A chip lands on its pinout because its decoded fields say so. The **only** allowed per-chip override seam is the user config folder (`~/.firestarter/database.json`).
</domain>

<decisions>
## Implementation Decisions

### Re-derivation posture vs. the frozen baseline (PIN-01)
- **D-01: Correctness-first (unconstrained).** Apply the principled rules wherever they are better-grounded, **even if they reassign existing chips' pinouts/algorithms**. Accept a larger Phase 59 GATE-02 diff in exchange for a maximally source-correct DB. Every reassignment must carry a cited rationale into the Phase 59 per-chip diff. (Chosen over diff-minimal and hybrid.)
- **D-02: Delete the guess tables entirely.** `PIN_MAP_TO_PINOUT`, `PIN_MAP_PROTO_TO_PINOUT`, and `DIP28_VARIANT_MAP` are removed — not kept as a fallback. The principled function is the **sole** pinout-selection path; no dual lookup.

### No special code — data-driven mapping (operator directive, this session)
- **D-03: Zero per-IC / per-family special-casing in `build_db.py`.** The pinout-KEY selection is a general function of decoded fields only (`pin_count`, `proto_id`, `mem_size`, and the minipro `pin_map` / gnd / vcc mask signals). No `if name == "AT28C16"`, no chip-name lists, no family tables. The derivation must be easy to follow and verify.
- **D-04: Derive the physical pin layout from minipro masks too (ambitious target).** Go beyond key-selection: build the physical address/data/control pin layout itself from minipro's `pin_map` / gnd / vcc bitmasks at build time, so `pinouts.json` shrinks toward only the firestarter-specific DIP→RURP-bus routing minipro doesn't carry. ⚠ **Feasibility is the #1 research question** (see code_context): minipro's `pin_map` is an *index* into source-side tables, so "derive from minipro" likely means decoding/porting minipro's pin-map **data tables** (cited, not special code), not reading a self-contained XML bitmask. If full layout derivation proves infeasible for some family, fall back to selection-only for that family with curated `pinouts.json` rows — never per-IC code.
- **D-05: Overrides become rule OUTCOMES, not patches (reframes PIN-02).** The three load-bearing safety behaviors must emerge naturally from the principled rules:
  - WARNING-5 (`0x07→0x0D` for 5V 28C EEPROMs) → expressed as a rule like "5V part with the electrically-erasable flag → `0x0D`, never `0x07`".
  - fm1608 (`type=4` → SRAM/FRAM family) → a rule keyed on decoded `type`.
  - 24-pin EEPROM skip → obsolete; these chips now route to `DIP24_2816` + `0x0D` (the unblock).
  The hardcoded conditional blocks in `build_db.py` (current lines ~419-432 skip, ~461+ WARNING-5) are **removed**. `check_dispatch.py` (GATE-03) remains the independent proof gate: **0 VPP-routing violations across the full regenerated set** satisfies PIN-02's intent (no chip gets a VPP-on-wrong-pin damage path). *(Confirmed explicitly: "Yes, exactly.")*
- **D-06: Fail-safe for unclassifiable chips (planner's call on mechanism).** When the rules genuinely can't classify a chip, `build_db.py` must NOT re-introduce a hardcoded override. Planner chooses the fail-safe behavior (skip-with-loud-warning vs. emit-with-safest-handler), under the **hard constraint that no uncertain chip ever emits a VPP-asserting dispatch.** Operator can then add a correct entry via `~/.firestarter/database.json`.

### 24-pin EEPROM unblock (PIN-03)
- **D-07: Add a dedicated `DIP24_2816` pinout entry** (chosen over reusing/re-commenting `DIP24_6116`). It is electrically identical to the existing `DIP24_6116` (rw-pin=21=WE, oe=20, ce=18, vcc=24, gnd=12, **no vpp-pin**) but named/commented as a 5V EEPROM so the DB self-documents that these are EEPROMs, not SRAM, and SR-1 traceability is clean. The 9 chips select it via a **general rule** (e.g. `pin_count==24` ∧ erasable-flag ∧ `0x0D` → `DIP24_2816`), never by name.
- **D-08: Family coverage — planner decides one-entry-vs-split from datasheets.** AT28C16 (2KB, 11 addr lines) and AT28C04 (smaller) share the 24-pin body. Default expectation: one over-allocated entry (full A0-A10 bus, firmware restricts driving by `mem_size` — the proven 32-pin-flash pattern). Researcher confirms against the AT28C04/16 datasheets; split only if physical pin **assignment** (not just count) genuinely diverges.

### Citations (PIN-01 / SC#1)
- **D-09: Remove the "one-rom verified" list entirely — not needed.** Those annotations die with the guess tables. The minipro mask decode in `build_db.py` **is** the citation, recorded via the Phase 56 D-05/D-06 convention (GitLab commit-permalink URLs pinned to one recorded SHA, pointing at the minipro source the derivation reads). No separate local-verification list is maintained; one-rom/datasheet refs are corroborating only. SC#1 ("no evidence-free entries remain") is then satisfied **by construction** — the table-based entries that carried those annotations no longer exist.

### SR-1 safety checklist (PIN-03 / SC#4)
- **D-10: Document in BOTH layers.** Author the SR-1 review as a planning artifact (`.planning/.../58-SR-1-CHECKLIST.md` or equivalent — audit trail) AND surface the resulting safety guarantees in a shipped sub-repo doc (e.g. `firestarter_app/doc/`), mirroring the two-layer shield-revision doc pattern (meta investigation-canonical + sub-repo operator/GitHub-visible). Keep them in lockstep.
- **D-11: SR-1 scope = every pinout the re-derivation changes.** Covers `DIP24_2816` PLUS any existing pinout whose selection or layout changes under the new data-driven derivation — so no reassigned chip escapes a VPP-safety review. GATE-03 (`check_dispatch.py`) is the mechanical backstop across the full set. Checklist per pinout: `vpp-pin` absent on 5V parts, `rw-pin` = datasheet WE pin, `oe-pin`/`ce-pin` correct, all DIP pins accounted for.

### Claude's Discretion (planner / researcher)
- D-06 fail-safe mechanism (skip vs. safest-emit), subject to the no-VPP-on-uncertain constraint.
- D-08 one-entry-vs-split for the AT28C04/16 family, from datasheet evidence.
- Exact filenames/paths for the SR-1 artifacts (D-10).
- Exact internal structure of the principled rule function and how far D-04 layout-derivation reaches before falling back to curated `pinouts.json` rows.
</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### v1.11 framing & prior decisions (read first)
- `.planning/research/SUMMARY.md` — premise-overturned milestone summary; decode-correctness not expansion; build order. **Read first.**
- `.planning/phases/56-snapshot-field-dictionary-corrected-docs/56-CONTEXT.md` — prior locked decisions D-01..D-11: live XML fetch (D-01), frozen-output baseline = regression anchor (D-03), minipro citation convention permalink+SHA (D-05/D-06), host-only/no-vendoring.
- `.planning/REQUIREMENTS.md` — PIN-01/02/03 text, out-of-scope table (BENCH-01 deferred to v2).
- `.planning/ROADMAP.md` §"Phase 58" — goal + 4 success criteria (note: PIN-02 mechanism is reframed here by D-05 — outcomes-not-patches; the *intent* "no VPP-on-wrong-pin" is preserved and enforced by GATE-03).

### Field-decode authority & safety model
- `firestarter_app/doc/infoic-field-dictionary.md` — Phase 56 authoritative source-grounded decode of every infoic.xml field; the principled rules cite this, not re-invent decode.
- `.planning/research/PITFALLS.md` — hazard model (wrong decode → VPP on wrong pin → dead 5V chip); SR-1..SR-6 checklist source for D-10/D-11.
- `.planning/research/STACK.md` — minipro `database.c`/`.h` field decode source material (mask semantics the derivation must read).
- `.planning/research/FEATURES.md` — protocol catalog + per-ID feasibility.

### Code under change (HOST-only — `firestarter_app`)
- `firestarter_app/tools/build_db.py` — **primary change target.** `resolve_pinout_key` (lines ~266-330), guess tables to DELETE (`PIN_MAP_TO_PINOUT` ~149, `PIN_MAP_PROTO_TO_PINOUT` ~198, `DIP28_VARIANT_MAP` ~125), 24-pin skip block to REMOVE (~419-432), WARNING-5 override block to convert-to-rule (~461+), `_etype` derivation (~452-459).
- `firestarter_app/tools/check_dispatch.py` — GATE-03 VPP-safety guard; the proof gate (0 violations) that replaces hardcoded overrides as the safety net. Already keyed on `electrical.type` + dynamic `pinouts.json` load (Phase 57), so it auto-covers `DIP24_2816`.
- `firestarter_app/firestarter/data/pinouts.json` — add `DIP24_2816` (D-07); may shrink under D-04. Existing `DIP24_6116` (SRAM 0x27) for reference: rw-pin=21, oe=20, ce=18, no vpp-pin.
- `firestarter_app/firestarter/data/chip_database.json` — regenerated output; diffed against the Phase 56 frozen baseline in Phase 59 (GATE-02).
- `firestarter_app/firestarter/database.py` — `skip_local_override` seam / `~/.firestarter/database.json` is the ONLY allowed per-chip override location (D-03/D-05).

### Firmware (read-only context — confirms PIN-03 "no firmware change")
- `firestarter/src/proms/eeprom_28c.cpp` — `configure_eeprom28c` is **pin-count-agnostic**: dispatches on `protocol==0x0D`, derives ID/addresses from `mem_size`, no hardcoded 28-pin assumption. The build_db.py skip-comment claiming "28-pin only" is **outdated**.
- `firestarter/src/proms/memory.cpp` — dispatch order: `0x0D → configure_eeprom28c` (5V, no VPP); confirms the unblocked 24-pin EEPROMs route safely with no firmware edit.

### Upstream source (cited, NOT vendored — Phase 56 D-05)
- minipro `src/database.h`, `src/database.c` (`pin_map` / gnd / vcc masks, `IC2_ALG_*`) — referenced via commit-permalink URLs pinned to one recorded SHA. The mask decode the derivation reads IS the citation (D-09).
</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **`DIP24_6116` pinout** is the electrical template for the new `DIP24_2816` — same layout (rw-pin=21=WE, oe=20, ce=18, vcc=24, gnd=12, no vpp-pin), already SR-1-clean.
- **`configure_eeprom28c` (firmware)** already handles the 24-pin EEPROMs unmodified — pin-count-agnostic dispatch on `0x0D`. PIN-03's "no firmware change" holds.
- **GATE-03 (`check_dispatch.py`)** already loads `pinouts.json` dynamically and keys on `electrical.type` (Phase 57 CR-01 fix), so it auto-covers new pinouts and is the ready-made safety proof gate for D-05/D-11.
- **32-pin over-allocation pattern** (over-allocate address bus, firmware restricts by `mem_size`) is the precedent for the one-entry `DIP24_2816` family-coverage option (D-08).

### Established Patterns
- **Algorithm-first dispatch:** wire `algorithm` int = upstream `protocol_id`, flowing XML → DB → wire → firmware handler. The new rules must produce the correct `algorithm`/`pinout` from this flow's decoded inputs, not invent a parallel taxonomy.
- **Live input, frozen output, URL-pinned citations** (Phase 56 through-line) — unchanged here.
- **Reframed-requirement precedent:** Phase 56 D-02 reinterpreted GATE-01 (anchor moved input→output) with explicit operator sign-off. D-05 here reinterprets PIN-02's *mechanism* (overrides→rules) the same way; the *intent* is preserved and GATE-03-enforced.

### Integration Points & Risks
- ⚠ **D-04 feasibility is the top research priority.** minipro's `pin_map` is an index into source-side tables, not a self-contained XML bitmask — "derive layout from minipro" most likely means decoding/porting minipro's pin-map data tables (cited per D-09), not reading the XML alone. Researcher must establish how much layout signal is actually recoverable before the planner sizes the work; D-06 fail-safe covers any gap.
- **Diff blast radius:** correctness-first (D-01) + delete-tables (D-02) + derive-layout (D-04) can move many existing chips. Every change must be explainable in Phase 59 GATE-02 — keep the rule logic auditable enough that each reassignment has a clear, cited cause.
</code_context>

<specifics>
## Specific Ideas

- The operator's controlling principle is *zero special code per IC* — repeated and sharpened across the session ("only allowed to add overrides in the user config folder"; "pin maps must be easily found and mapped without special code for any IC"; "remove the local verified list, not needed"). The whole phase is a move from curated/surveyed tables to a general, source-grounded derivation. When a tradeoff arises, bias toward the more general, data-driven, self-documenting option — and push genuine one-offs out to `~/.firestarter/database.json`.
</specifics>

<deferred>
## Deferred Ideas

- **BENCH-01 (real-hardware write/program validation of the unblocked AT28C04/16 EEPROMs)** — already deferred to v2 per REQUIREMENTS.md; this milestone closes on source-correctness. Recorded so the bench gap isn't mistaken for completeness.
- **Full pinouts.json generation / elimination** — if D-04 layout-derivation succeeds broadly, a future cleanup could regenerate `pinouts.json` entirely from minipro + a small RURP-routing overlay. Out of scope for closing Phase 58; note for a later refactor.

</deferred>

---

*Phase: 58-pinout-re-derivation-24-pin-eeprom-unblock*
*Context gathered: 2026-06-08*
