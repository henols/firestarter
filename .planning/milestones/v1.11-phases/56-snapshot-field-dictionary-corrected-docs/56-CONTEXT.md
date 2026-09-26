# Phase 56: Snapshot + Field Dictionary + Corrected Docs - Context

**Gathered:** 2026-06-08
**Status:** Ready for planning

<domain>
## Phase Boundary

Lay the **immutable decode foundation** for v1.11. This phase delivers three artifacts and the regression anchor everything downstream compares against:

1. **A committed pre-milestone baseline** of the generated `chip_database.json` (the regression anchor — see D-01/D-03).
2. **An authoritative, minipro-source-cited field dictionary** (`firestarter_app/doc/infoic-field-dictionary.md`) documenting every Firestarter-relevant `infoic.xml` attribute — `package_details`, `type`, `variant`, `protocol_id`, `flags`, `voltages`, `pin_map`, `pulse_delay`, `chip_id`, `code_memory_size`, `page_size`, `chip_info`, `blank_value` — each marked CONFIRMED / INFERRED / UNKNOWN (DEC-01).
3. **Three corrected decode docs** — `protocol-id.md`, `protocol-flags.md`, `package-details.md` (DOC-01/02/03), rewritten fresh and derived from the dictionary.

This phase produces the **authority** Phase 57 codes against. It does **NOT** change `build_db.py` decode behavior — the actual bug-fix code (BUG-1..4) lands in Phase 57. HOST-only; firmware sub-repo untouched.

**Requirements:** DEC-01, DEC-03, DEC-04, DEC-05 (dictionary side), DOC-01, DOC-02, DOC-03, GATE-01.
</domain>

<decisions>
## Implementation Decisions

### Snapshot vehicle & regression baseline (GATE-01)
- **D-01:** **No vendored `infoic.xml` in the repo.** `build_db.py` keeps fetching the XML **live from upstream `master` on every rebuild** (current `build_db.py:10` behavior is preserved — `MINIPRO_XML_URL = ".../-/raw/master/infoic.xml"`). The XML input is deliberately **not pinned**. *(Operator decision, made explicitly twice.)*
- **D-02:** **GATE-01 re-derived.** The literal requirement ("pin a specific upstream `infoic.xml` commit and commit it in-repo") is **overridden** by D-01. The immutable decode anchor moves from the **input (XML)** to the **output (generated DB)**.
- **D-03:** **The regression baseline is a committed snapshot of the CURRENT generated `chip_database.json`** (pre-milestone baseline). Phase 59's GATE-02 per-chip diff compares the regenerated DB against this frozen DB, so our decode changes are isolated from any upstream `master` drift. Suggested location to confirm at plan time: `firestarter_app/tools/baseline/chip_database.baseline.json` or a `.planning/v1.11/` artifact.
- **D-04:** ⚠ **GATE-04 weakened (FLAG for Phase 59 planner).** Its literal text — "byte-identical across two runs; no runtime upstream fetch" — cannot hold under live fetch. Re-read it as **"deterministic given a stable upstream `master`."** Byte-identity holds only if upstream `master` is unchanged between the two runs. Phase 59 must plan GATE-04 against this weakened guarantee, not the original offline-determinism wording.

### Citation grounding (DEC-01)
- **D-05:** Field-dictionary citations use **GitLab commit-permalink URLs** to minipro source (`database.c` / `database.h` / `interpret_timing()` / `IC2_ALG_*` constants) — e.g. `minipro/src/database.h#L120 @ <sha>`. **No minipro source vendored** in the repo (consistent with D-01). The linked commit is immutable, so citations don't rot even though the XML data fetch is unpinned. The citation-commit SHA is **independent** of the live-`master` XML fetch.
- **D-06:** **One recorded "minipro citation commit" SHA** documented at the top of `infoic-field-dictionary.md`; all permalinks share it (single place to bump), rather than per-line independent SHAs.

### Dictionary home (DEC-01)
- **D-07:** The authoritative field dictionary lives as a **companion markdown file: `firestarter_app/doc/infoic-field-dictionary.md`** — alongside the three docs being corrected. `build_db.py` constants stay code-only (no dictionary prose embedded in the 537-line module). This file is the **canonical authority** Phase 57's bug fixes cite.

### Doc correction style (DOC-01/02/03)
- **D-08:** **Rewrite all three docs fresh, derived from the field dictionary** (not surgical in-place edits). Build order within the phase is therefore **dictionary first → docs regenerated from it**, giving a single source of truth with the docs as derived topic-level views.
- **D-09:** Preserve the existing **logo-header convention** (each doc opens with the `firestarter_logo.png` `<p align="left">` block — see current line 1 of all three).
- **D-10:** Specific corrections the rewrites must land (from research, HIGH confidence):
  - `protocol-id.md` (DOC-03): canonical `IC2_ALG_*` names; fix the `0x39` error; feasibility/exclusion notes for non-memory + infeasible IDs (`0x2A`/`0x2C`/`0x2E` GAL/PIC/MCU, `0x35` ITE, `0x11` FWH, phantom `0x39`).
  - `protocol-flags.md` (DOC-02): canonical protocol names; flag-bit fix — **bit 4 = `can_erase`**, not "requires write-enable sequence".
  - `package-details.md` (DOC-01): **re-titled to describe `flags`**; bit meanings source-grounded; inferred bits **3/6/7 explicitly marked not source-confirmed**.

### Dictionary content correctness (DEC-03/04/05 — dictionary side only; code lands Phase 57)
- **D-11:** The dictionary must state the **correct** decode semantics for the four confirmed bugs, even though the `build_db.py` code fix is Phase 57:
  - BUG-2 / DEC-03: `pulse_delay` is **microseconds** for all protocols; the `interpret_timing` ×100 multiplier (0x07/0x0B) is wrong (W27C512 → 100µs, not 10000µs). *(Open: confirm against minipro `interpret_timing()` it isn't an intentional per-protocol unit before stating CONFIRMED.)*
  - BUG-1 / DEC-04: `VCC_VOLTAGES` is missing nibble `0x02` (4V) and `0x03` (4.5V); AT28C256/AT28C64-class default to 5V wrongly. *(Open: re-verify the 4V/4.5V values against `tl866ii_vcc_voltages[]`.)*
  - BUG-3 / DEC-04: `vcc` = bits 11-8, `vdd` = bits 15-12 — current labels are swapped.
  - BUG-4 / DEC-05: `PROTOCOL_MAP` names are wrong (`0x2A`/`0x2C`/`0x2E`/`0x35`), `0x3C` is invented, `0x39` is phantom — dictionary records canonical names + exclusion rationale.

### Claude's Discretion
- Exact path/filename of the baseline DB snapshot (D-03) and the per-attribute table layout of the dictionary are left to the planner/executor.
- Whether the citation-commit SHA (D-06) is also mirrored as a comment in `build_db.py` is discretionary (low value, no objection either way).
</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### v1.11 milestone framing (source-grounded — overturned the original premise)
- `.planning/research/SUMMARY.md` — **read first.** Premise-overturned summary: hardware-feasible set already covered; v1.11 is decode-correctness + docs, not expansion. Confirmed-bug table (BUG-1..4), exclusion set, build order.
- `.planning/research/STACK.md` — field dictionary source material (per-attribute decode from minipro `database.c`/`.h`).
- `.planning/research/FEATURES.md` — protocol catalog + per-ID feasibility (drives `protocol-id.md` exclusion notes).
- `.planning/research/PITFALLS.md` — hazard model (wrong decode → VPP on wrong pin → dead 5V chip); SR-1..SR-6 safety checklist (relevant downstream, but the two-pass `_etype` warning matters context-wide).
- `.planning/research/ARCHITECTURE.md` — integration map; confirms interventions are host-side only.
- `.planning/REQUIREMENTS.md` — v1.11 requirements (DEC/PIN/DOC/GATE), out-of-scope table, v2 deferrals.
- `.planning/ROADMAP.md` §"Phase 56" — goal + success criteria (note: SC#1 GATE-01 wording is superseded by D-02/D-03 here).

### Code under change (HOST-only — `firestarter_app`)
- `firestarter_app/tools/build_db.py` — pipeline; `MINIPRO_XML_URL` (line 10, stays live per D-01), `PROTOCOL_MAP` (25-44), `VCC_VOLTAGES` (85), `VPP_MV`/`VPP_VOLTAGES`, `KNOWN_PROTOCOLS` (83), `PIN_MAP_TO_PINOUT`/`DIP28_VARIANT_MAP`. **Phase 56 reads it for dictionary authority; does NOT change decode behavior.**
- `firestarter_app/tools/check_dispatch.py` — VPP-safety guard (extended in Phase 57, referenced for context).
- `firestarter_app/doc/protocol-id.md` (360L) — rewrite target (DOC-03).
- `firestarter_app/doc/protocol-flags.md` (64L) — rewrite target (DOC-02).
- `firestarter_app/doc/package-details.md` (118L) — rewrite target (DOC-01).
- `firestarter_app/firestarter/data/chip_database.json` — the generated DB; snapshot its current state as the baseline (D-03).
- `firestarter_app/doc/infoic-field-dictionary.md` — **NEW** file to create (D-07).

### Upstream source (cited, NOT vendored — D-05)
- minipro `src/database.h`, `src/database.c`, `interpret_timing()`, `IC2_ALG_*` constants — referenced via commit-permalink URLs pinned to one recorded SHA (D-06).
</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **`build_db.py` decode constants** (`PROTOCOL_MAP`, `VCC_VOLTAGES`, `VPP_MV`, `KNOWN_PROTOCOLS`, `DIP28_VARIANT_MAP`, `PIN_MAP_TO_PINOUT`) are the raw material the dictionary documents — the dictionary is essentially the source-grounded annotation layer over these.
- **The three `doc/*.md` files** share a logo-header convention (line 1) to preserve on rewrite (D-09).
- **WARNING-5 override** documented in `firestarter_app/CLAUDE.md` (DIP28_2764 + 0x07 + Flash/EEPROM → 0x0D) — the dictionary's `protocol_id` / `flags` entries must be consistent with this load-bearing safety logic (full re-derivation is Phase 57/58).

### Established Patterns
- **Algorithm-first dispatch (core value):** the wire `algorithm` integer = upstream `protocol_id`, flowing XML → DB → wire JSON → firmware handler. The dictionary documents the decode of that flow's inputs; it must not invent a parallel taxonomy.
- **v1.8 precedent:** host-only milestone, firmware untouched — same model here.

### Integration Points
- The dictionary (D-07) is the authority Phase 57 cites when fixing `build_db.py`; the baseline DB (D-03) is the anchor Phase 59 (GATE-02) diffs against. Both are produced in Phase 56 and consumed later — get them right here.
</code_context>

<specifics>
## Specific Ideas

- Operator was explicit and deliberate: **nothing gets vendored into the repo** — not the XML, not the minipro source. The build pipeline downloads on rebuild; provenance/citation is handled by commit-permalink references, and the regression anchor is the committed *output* DB, not any input file. This philosophy (live input, frozen output baseline, URL-pinned citations) is the through-line for all four decisions.
</specifics>

<deferred>
## Deferred Ideas

- **v1.11 input pinning / offline determinism** — the original GATE-01/GATE-04 offline-determinism design is intentionally not pursued (D-01/D-02/D-04). If a future maintainer wants true offline-reproducible rebuilds, vendoring or SHA-pinning the XML would be the path — recorded here so the trade-off isn't silently lost.

### Reviewed Todos (not folded)
- **`w27c512-eeprom-misclassification`** (W27C/E + SST27SF/VF series misclassified as UV-only EPROMs; should be electrically erasable) — genuinely a v1.11 decode-correctness concern, but it's a **classification/decode fix (Phase 57/58)**, not a snapshot/dictionary/docs item. Deferred to the phase that touches classification. The dictionary built here should *document* the correct erasability semantics so Phase 57/58 has the authority to fix it.
- `avrdude-mcu-detection-fallback`, `cobs-decoder-framelevel-deadline-wr01` — keyword-only matches; not relevant to Phase 56 (firmware/COBS/installer scope).
</deferred>

---

*Phase: 56-snapshot-field-dictionary-corrected-docs*
*Context gathered: 2026-06-08*
