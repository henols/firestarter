# Phase 87: Naming + Documentation Pass - Context

**Gathered:** 2026-06-25
**Status:** Ready for planning

> **Renumbered:** this is the *original* Phase 86 (Naming + Documentation Pass),
> displaced when the variant-decode phase was inserted as the new Phase 86
> (operator decision, 2026-06-25). Several format decisions below were pre-captured
> in `86-CONTEXT.md` §Deferred during that discussion and are carried forward as
> LOCKED here (not re-asked).

<domain>
## Phase Boundary

Author the human-facing **protocol vocabulary + behavior documentation** for the
*now-correct* DB produced by Phase 86, with **zero** change to firmware dispatch
structure, wire/control values, or DB records. Three deliverables:

1. **`firestarter/doc/PROTOCOLS.md`** — maps every `protocol_id` present in
   `chip_database.json` to a folder slug (from `datasheets/`) **and** a descriptive
   algorithm-axis name, plus datasheet-verified write algorithm / erase model / VPP
   behavior / pin roles per bucket (NAME-01); documents the corrected FM1608
   (SRAM_STD / 0x28) and X88C64 (`electrical.type` EEPROM) with their true
   `infoic.xml` identity tuples (NAME-04); names the phantom (0x35/0x39) and
   infeasible (0x11/0x2A/0x2B/0x2C) buckets as honest non-protocols.
2. **Inline rationale header-comments** in each firmware handler — the *why*
   (timing / VPP routing / pin behavior) cited to a committed datasheet (NAME-02).
3. **The 9-invariant → native-test traceability matrix** (NAME-03), with minimal
   gap-fill native tests added only where a cell is empty.

**In scope:** PROTOCOLS.md authoring; per-handler inline comments; the invariant
matrix + minimal gap-fill tests; documenting the Phase-86 FM1608/X88C64
corrections; naming phantom/infeasible buckets.

**Out of scope:** any DB record change (`diff_db.py` MUST be empty vs the
Phase-86-repinned baseline); any dispatch-structure or wire-value change; folder
renames under `datasheets/`; full per-family register golden traces (that is
Phase 88); any firmware behavior change; the recompose itself (Phase 89).

**Repo:** all changes land in the `firestarter` sub-repo (doc + firmware source +
native tests). Host-side: PROTOCOLS.md references the corrected DB but does not
modify it. NO dual-repo lockstep (SAFE-06).

</domain>

<decisions>
## Implementation Decisions

### Carried forward — LOCKED (decided during the Phase 86 discussion)
- **D-01:** Vocabulary doc location is **`firestarter/doc/PROTOCOLS.md`** — single
  canonical, GitHub-visible. (Not the research-only `.planning/research/PROTOCOLS.md`,
  which is a source/precedent, not the deliverable.)
- **D-02:** **Two-name scheme** — keep the existing `datasheets/<hex>-<NAME>/` folder
  slugs unchanged AND add a descriptive algorithm-axis name column. **No folder
  renames.** The doc carries both columns.
- **D-03:** **Per-handler inline rationale header-comments** citing datasheets, with
  the full prose living in PROTOCOLS.md (comments cost zero flash).
- **D-04:** Enumerate all **9** one-off invariants (not the stale "8") via
  **matrix-first traceability + gap-fill native tests** only where a cell is empty.
  The 9: 0x0B direct-VPE rail · 0x0B shared OE/VPP read-skip · 0x08 P1-as-VPP ·
  flash4 256B page boundary · VPP-skip-on-read · pulse-delay defaults · FM1608
  SRAM→FRAM · WARNING-5 0x07→0x0D override · SST39SF040 keep-Flash/EEPROM.
  *(WARNING-5 and FM1608→FRAM are now delivered by Phase 86's variant decode rather
  than a build_db override, but remain documented invariants the decode/firmware
  must preserve.)*

### Invariant matrix home (decided this discussion)
- **D-05:** The 9-invariant matrix lives **as a section inside PROTOCOLS.md**, but
  **each invariant gets a stable ID `INV-01..INV-09`** referenced in the native test
  function/docstring names — so the recompose phases (88/89) can grep the contract
  straight to its live test. One canonical doc; machine-traceable.
  *(Rationale: keeps a single source of truth per D-01 while giving SAFE-02 a
  greppable invariant↔test wiring for the recompose oracle.)*

### Gap-fill test rigor (decided this discussion)
- **D-06:** Gap-fill native tests are **minimal targeted assertions** — just enough
  to pin each invariant's one observable behavior. **Full per-family register golden
  traces are explicitly Phase 88's job; do NOT duplicate that effort here.** A test
  is only added where the invariant has no existing covering assertion.

### Inline comment + citation format (decided this discussion)
- **D-07:** **One rationale header block per handler file**, citing the datasheet by
  **filename AND the specific section/page** where each timing/VPP value originates
  (anchored citations — verifiable, not just "see the datasheet"). Full prose stays
  in PROTOCOLS.md; the inline comment is the concise "why + cite".

### PROTOCOLS.md depth + non-protocol presentation (decided this discussion)
- **D-08:** **A section per protocol bucket** covering the NAME-01 four facets (write
  algorithm, erase model, VPP behavior, pin roles), datasheet-cited. Phantom
  (0x35/0x39) and infeasible (0x11/0x2A/0x2B/0x2C) buckets are grouped in a separate
  **"Honest non-protocols"** section, explicitly named as non-protocols (not buckets
  with behavior).

### Gates (carried from milestone safety model)
- **D-09:** `check_dispatch.py` exits **0 violations** and `diff_db.py` is **empty**
  against the Phase-86-repinned baseline — this phase changes no DB records (NAME-05,
  SAFE-03).
- **D-10:** `pio run -e leonardo` shows a **near-zero flash delta** — the vocabulary
  is host-side doc + source comments only; **no PROGMEM strings added to firmware**
  (NAME-05). Host toolchain stays green against CI **py3.11** (SAFE-06).

### Claude's Discretion
- Exact INV-0x naming convention for the test functions/docstrings (as long as the
  IDs in PROTOCOLS.md and the test names match and are greppable).
- Exact ordering/heading structure within PROTOCOLS.md (per-protocol sections,
  the matrix section, the non-protocols section) — planner/executor's call.
- Which existing native test files host the gap-fill assertions, and the precise
  assertion mechanics — as long as each new test is minimal (D-06) and tied to an
  INV id (D-05).
- Datasheet page/section anchor precision per handler where a datasheet lacks clean
  section numbering — cite the best available locator; an honest "p.N figure/table"
  is acceptable.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase / milestone definition
- `.planning/ROADMAP.md` — v1.16 §"Phase 87: Naming + Documentation Pass" (goal, 5
  success criteria) + §"Scope amendment" (why 87 documents the corrected world).
- `.planning/REQUIREMENTS.md` — NAME-01..05, SAFE-03, SAFE-06 (+ SAFE-02 which the
  invariant matrix feeds at Phases 88/89).

### What Phase 86 delivered (the corrected world this doc describes)
- `.planning/phases/86-variant-decode-correct-db-regen/86-CONTEXT.md` — the variant
  decode decisions (FM1608 = type4/proto0x07/variant0x4126 → 0x28; X88C64 =
  type1/proto0x34/variant0x3100/flags0x00414200 → EEPROM); §Deferred pre-captured
  the locked D-01..D-04 format decisions above.
- `.planning/phases/86-variant-decode-correct-db-regen/86-SUMMARY.md` (+ 86-0x
  plan/summary set) — final DB state (746 chips incl. 2516/2532 supplement),
  re-pinned baselines, the variant-decode rules that explain every record.
- `firestarter_app/firestarter/data/chip_database.json` — the corrected DB; the set
  of `protocol_id` values present here defines exactly which buckets PROTOCOLS.md
  must name.

### Firmware handlers to comment (the NAME-02 targets)
- `firestarter/src/proms/eprom.cpp` — 0x07/0x08/0x0B EPROM + EE-EPROM family
  (INV-01 direct-VPE rail, INV-02 OE/VPP read-skip, INV-03 0x08 P1-as-VPP,
  INV-05 VPP-skip-on-read, INV-08 WARNING-5 0x07→0x0D preserved-by-decode).
- `firestarter/src/proms/eeprom_28c.cpp` — 0x0D 28C-EEPROM (SDP, poll).
- `firestarter/src/proms/flash_intel.cpp` — 0x10 Intel flash.
- `firestarter/src/proms/flash_type_3.cpp` — 0x06 flash type-3 (SST39SF040;
  INV-09 keep-Flash/EEPROM).
- `firestarter/src/proms/flash_type_4.cpp` — 0x05 flash type-4 (INV-04 256B page
  boundary).
- `firestarter/src/proms/flash_utils.cpp` · `memory.cpp` · `sram.cpp` (0x28
  SRAM_STD / FM1608, INV-07 SRAM→FRAM) · `not_implemented.cpp` (phantom/infeasible
  + 0x34 X88C64 protocol-not-implemented).
- `firestarter/src/firestarter.cpp` — dispatch entry (structure unchanged; INV
  ordering reference).

### Gates + tests
- `firestarter_app/tools/check_dispatch.py` — 0-violations gate (D-09).
- `firestarter_app/tools/diff_db.py` — must be empty vs re-pinned baseline (D-09).
- `firestarter_app/tools/baseline/chip_database.baseline.json` +
  `dispatch_baseline.json` — the Phase-86-repinned baselines this phase is frozen against.
- `firestarter/test/` native `test_val_*` suites — where the gap-fill INV
  assertions land; run via `pio test -e native`.

### Datasheets + precedent vocab (sources, not deliverables)
- `firestarter/datasheets/README.md` + `datasheets/<hex>-<NAME>/` folders — the
  committed datasheet index from Phase 85; folder slugs feed PROTOCOLS.md column 1
  and are the citation targets for D-07. **No folder renames.**
- `.planning/research/PROTOCOLS.md` — the research-grade protocol guide (RURP
  control-register map, per-bucket behavior); a source to distill from, NOT the
  deliverable. Note: its "FM1608 algorithm 40 = 0x28" is the *derived* value —
  document the corrected ground-truth tuple instead.
- `.planning/v1.13-PROTOCOL-ENUMERATION.md` — the 12-bucket landscape + erase-scope
  findings; grounds the per-bucket behavior facets.
- `firestarter_app/CLAUDE.md` — host toolchain discipline (validate ruff/format/
  mypy/pytest against py3.11; generated `messages.py` never hand-normalized).

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **`.planning/research/PROTOCOLS.md`** already contains a near-complete RURP
  control-register map and per-bucket behavior narrative — distill (don't reinvent)
  into the GitHub-visible `firestarter/doc/PROTOCOLS.md`, corrected for the Phase-86
  ground truth.
- **`datasheets/<hex>-<NAME>/` folder slugs** (Phase 85) ARE column 1 of the
  two-name scheme — no new slug invention needed.
- **`check_dispatch.py` / `diff_db.py`** are the same empty-diff/0-violation gates
  used in Phase 86 — rerun, no change (D-09).
- **Existing `test_val_*` native suites** host the gap-fill INV assertions — extend,
  don't create a new harness.

### Established Patterns
- This phase mirrors a classic "document-the-frozen-world" pass: doc + comments +
  traceability tests, with hard empty-`diff_db` / 0-violation gates proving nothing
  electrical moved.
- Inline-comments-cost-zero-flash + prose-in-doc is the established split (NAME-02);
  the Leonardo flash-delta gate (D-10) enforces it.

### Integration Points
- The INV-0x stable IDs (D-05) are the contract Phase 88 (golden traces +
  dispatch-mirror guard) and Phase 89 (recompose) consume as SAFE-02 — name them so
  they survive the recompose grep-intact.
- PROTOCOLS.md's per-bucket set is bounded by the `protocol_id` values actually
  present in the Phase-86 `chip_database.json` — enumerate from the DB, not from memory.

</code_context>

<specifics>
## Specific Ideas

- Anchored datasheet citations (D-07): prefer `datasheets/07-W27C512/<file>.pdf p.7
  §6.2` style — a verifiable locator, not a bare filename.
- The phantom (0x35/0x39) and infeasible (0x11/0x2A/0x2B/0x2C) buckets are honest
  non-protocols — present them as such, NOT as buckets with documented behavior.
- The "FM1608 0x40" framing in old notes is a decimal-40 ↔ hex-0x28 conflation;
  record that explicitly so the historical confusion is retired in the doc (NAME-04).

</specifics>

<deferred>
## Deferred Ideas

- **Per-family register golden traces + dispatch-mirror invariant test** — Phase 88.
  This phase's gap-fill tests are deliberately minimal (D-06); the full golden-trace
  oracle is 88's job. The INV-0x IDs are the handoff.
- **The primitive recompose itself** (P7→P4→P3→P5 extraction) — Phase 89, frozen
  against the same baseline the matrix protects.
- **Per-protocol bench validation + PROTOCOL-LEDGER** — Phase 90.
- **Implementing the 0x34 X88C64 programming handler** — still PCB-blocked (FUT-01);
  this phase only *documents* its corrected `electrical.type`, it does not implement.

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 87-naming-documentation-pass*
*Context gathered: 2026-06-25*
