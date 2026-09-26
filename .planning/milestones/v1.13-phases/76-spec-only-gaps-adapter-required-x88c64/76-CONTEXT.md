# Phase 76: Spec-Only Gaps — adapter-required + X88C64 - Context

**Gathered:** 2026-06-18
**Status:** Ready for planning

<domain>
## Phase Boundary

Deliver the two spec-gated v1.13 gaps as **documented specs / classifications only** — nothing
graduates to `supported` this milestone:

- **GAP-01 (AT28C04 / AT28C16, 24-pin EEPROM):** a documented DIP24 pin-map/adapter spec + a
  *named* `resolve_pinout_key` rule arm. The chips stay `support_status: adapter-required`
  (refused in-host) until a physical DIP24 adapter exists and a golden write+read-back round-trips.
- **GAP-02 (X88C64, protocol `0x34`):** a datasheet-sourced feasibility verdict + the STORE/RECALL
  and byte/page write protocol, written down. The chip is re-classified as a documented
  feasible-candidate.

**Explicitly OUT of scope:** graduating any chip to `supported`; building a physical adapter;
committing an X88C64 firmware handler. No chip becomes newly `supported`; `check_dispatch.py` /
`diff_db.py` stay green; any firmware that lands builds `pio run -e leonardo` under the flash
ceiling with dual-repo lockstep.

</domain>

<decisions>
## Implementation Decisions

### GAP-02 — X88C64 handler gate
- **D-01:** GAP-02 delivers the **datasheet feasibility verdict + protocol spec only** (STORE/RECALL
  sequence, byte vs page write, timing). X88C64 is classified as a **documented feasible-candidate** —
  **no `0x34` firmware handler is committed this phase.** Rationale: Phase 74's flash ceiling is still
  open (74-03 deferred) and feasibility is MEDIUM; the "do NOT commit a blind handler" guardrail holds.
  The handler remains a deferred future requirement (already in REQUIREMENTS.md "Future Requirements").

### GAP-02 — host-visible classification
- **D-02:** **Reword the X88C64 `unsupported_reason` string now**, as part of GAP-02's re-classification.
  The current "XICOR NovRAM serial-parallel hybrid" is misleading — the chip is a **parallel DIP24**
  part the RURP can drive. New string reflects the datasheet verdict (parallel DIP24, feasible-candidate,
  handler not implemented). This is a host-visible one-string DB change — **`check_dispatch.py` and
  `diff_db.py` MUST stay green** (expect a 1-chip reason-string delta, no support_status/dispatch change).

### GAP-01 — resolve_pinout_key named rule arm
- **D-03:** The `resolve_pinout_key` arm in `firestarter_app/tools/build_db.py` **names AT28C04 /
  AT28C16 explicitly and routes them deterministically to `adapter-required` (refusal)**. It does NOT
  encode the DIP24→DIP32 pin remap. This is an explicit named classification, **not a resurrected
  guess table**. The chips stay refused in-host (existing `chip_resolver.py` / `database.py` refusal path).

### GAP-01 — adapter pin-map spec home & format
- **D-04:** The DIP24→DIP32 adapter pin-map lives in a **spec doc** that is the single source of truth
  (used only when a physical adapter is built). It is authored in **two layers, kept in lockstep**:
  the operator-facing copy in **`firestarter/doc/`** (GitHub-visible — someone physically builds the
  adapter) plus the **canonical investigation copy in meta `.planning/`** — matching the existing
  two-layer SHIELD-REVISIONS pattern. Format: a pin table + socket re-route description.

### Claude's Discretion
- Exact filename/section layout of the new adapter spec doc (follow the SHIELD-REVISIONS precedent).
- Exact wording of the rewritten X88C64 `unsupported_reason` (must be datasheet-accurate and keep gates green).
- Depth/structure of the X88C64 protocol write-up beyond "STORE/RECALL + byte/page write + timing".

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase scope & classification source of truth
- `.planning/v1.13-PROTOCOL-ENUMERATION.md` — **MUST read.** X88C64 `0x34` row (re-classified
  implicit-infeasible → feasible-gap, Phase 76 scope) + the support_status↔feasibility taxonomy
  (AT28C04/16 = `adapter-required` / `feasible-gap (deferred)`). Cite rows by protocol_id.
- `.planning/REQUIREMENTS.md` — GAP-01, GAP-02 text + the "Future Requirements (deferred)" entries
  (adapter graduation; X88C64 handler) that this phase intentionally does NOT close.
- `.planning/ROADMAP.md` §"Phase 76" — goal, dependencies (Phase 72 done; Phase 74 flash ceiling),
  and the 3 success criteria.

### GAP-01 code surfaces (host DB build + refusal path)
- `firestarter_app/tools/build_db.py` — `resolve_pinout_key` (the named-rule-arm extension point),
  `KNOWN_PROTOCOLS`, `RURP_VPP_CEILING_MV=22000` (build_db.py:117), 0x34 inclusion (build_db.py:134-148).
- `firestarter_app/tools/diff_db.py` — uses `resolve_pinout_key`; the diff gate that must stay green.
- `firestarter_app/tests/test_build_db_inclusion.py` — inclusion/rule-arm tests; extend here.
- `firestarter_app/firestarter/chip_resolver.py`, `firestarter_app/firestarter/database.py` —
  host refusal path + `support_status` handling (the `adapter-required` / `protocol-not-implemented`
  in-host refusal; from Phase 66 taxonomy).
- `firestarter_app/firestarter/data/chip_database.json` — AT28C04/AT28C16 entries (GAP-01) and the
  `X88C64P` entry (GAP-02 reason reword).

### GAP-02 firmware reference (for the verdict — no handler committed)
- `firestarter/src/proms/memory.cpp` §74-119 — protocol dispatch table; 0x34 has no arm (the gap).

### Two-layer hardware-doc precedent (for the new adapter spec — D-04)
- `firestarter/doc/SHIELD-REVISIONS.md` — the operator-facing GitHub-visible layer pattern to mirror.
- `.planning/v1.7-SHIELD-REVS.md` — the meta investigation-canonical layer pattern to mirror.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `resolve_pinout_key` (build_db.py): the explicit named-rule-arm mechanism — extend with an
  AT28C04/AT28C16 arm rather than adding any heuristic/guess pin-map.
- `support_status` taxonomy (`adapter-required`, `protocol-not-implemented`, `supported`,
  `vpp-exceeds-max`) from Phase 66 — already drives in-host refusal; GAP-01/02 reuse it unchanged.
- `check_dispatch.py` (744-chip sweep) + `diff_db.py` — the green-gate harness both gaps must satisfy.

### Established Patterns
- Two-layer hardware docs (meta investigation-canonical + sub-repo operator-canonical, lockstep) —
  the new DIP24 adapter spec follows SHIELD-REVISIONS.
- DB changes are codegen-driven; raw codegen output is ruff-clean (do NOT hand-normalize).
- Dual-repo lockstep + meta gitlink pinning until beta cut (do NOT bump gitlinks per-phase).

### Integration Points
- build_db.py rule arm → chip_database.json regeneration → diff_db/check_dispatch gates.
- X88C64 reason-string reword is a regenerated-DB delta (1 chip), not a hand-edit of the JSON.

</code_context>

<specifics>
## Specific Ideas

- X88C64 is the `X88C64P` DB entry (XICOR NovRAM); physically DIP-24 5V **parallel** — the RURP can
  drive the parallel bus, which is *why* it is a feasible-candidate rather than infeasible.
- AT28C04/AT28C16 already have a working firmware handler (`0x0D` / `configure_eeprom28c`); the only
  blocker is the DIP24 pin-map in a DIP32-oriented socket — hence adapter-required, not unsupported.

</specifics>

<deferred>
## Deferred Ideas

- **Graduating AT28C04/16 (and X88C64) to `supported`** — needs a physical DIP24 adapter + golden
  write+read-back round-trip; explicitly out of v1.13 (REQUIREMENTS "Future Requirements").
- **X88C64 `0x34` firmware handler** — to be built in a future (likely flash-ceiling-gated) milestone
  if GAP-02's spec proves feasible; not this phase (D-01).

### Reviewed Todos (not folded)
- `avrdude-mcu-detection-fallback.md`, `cobs-decoder-framelevel-deadline-wr01.md`,
  `flash4-page-size-datasheet-sourced-cr01.md` — surfaced by keyword match only (generic
  "firmware/2026/pending" terms); none relate to adapter pinouts or X88C64. Not in scope for Phase 76.

</deferred>

---

*Phase: 76-spec-only-gaps-adapter-required-x88c64*
*Context gathered: 2026-06-18*
