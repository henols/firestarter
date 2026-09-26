# Phase 88: Golden Traces + Dispatch-Mirror Guard - Context

**Gathered:** 2026-06-26
**Status:** Ready for planning

> **Renumbered:** this was the original Phase 87, displaced when the variant-decode
> phase was inserted as Phase 86 (operator decision, 2026-06-25). The phase numbers
> in ROADMAP carry a `*(was 87)*` annotation.

<domain>
## Phase Boundary

Establish the **recompose oracle** that Phase 89's incremental primitive extraction
will refactor against — so every later extraction step is a *refactor-under-test*,
not a leap of faith. Two deliverables plus two verification gates:

1. **Per-family byte-exact golden register traces** (PRIM-01) — for each of the five
   recompose-target families, capture and pin the exact ordered `(reg, data)` bus
   sequence in its native `test_val_*` suite against the existing recording bus.
   The five families:
   - `eprom.cpp` — 0x07 / 0x08 / 0x0B
   - `eeprom_28c.cpp` — 0x0D
   - `flash_intel.cpp` — 0x10
   - `flash_type_3.cpp` — 0x06
   - `flash_type_4.cpp` — 0x05
2. **A dispatch-mirror invariant test** (SAFE-02) — a `test_dispatch`-class test that
   binds the protocol→handler order across all three of its representations
   (PROTOCOLS.md §0 table, `check_dispatch.py`, firmware `configure_memory()`), so a
   recompose-time dispatch drift trips immediately.
3. **Frozen-world gates** (SAFE-04 + milestone safety model): `check_dispatch.py` exits
   0 violations and `diff_db.py` is empty — **this phase changes no DB records**.
4. **SC#4 verify-present-and-unmodified**: the firmware over-voltage VPP check and the
   host `chip_resolver.resolve_chip` guard are confirmed present and untouched; the
   2516 stays `UNVERIFIED` (no irreplaceable UV part written on an unstable read path).

**In scope:** authoring per-family byte-exact golden write+chip-id traces; the
all-three-bind dispatch-mirror test; rerunning the frozen-world gates; verifying the
over-voltage / host-guard safety posture is unchanged; minimal recorder/regen
plumbing needed to produce and re-bless the golden references.

**Out of scope:** the primitive recompose itself (P7→P4→P3→P5 extraction — Phase 89);
any DB record change (`diff_db.py` MUST stay empty); any firmware behavior change; any
dispatch-structure change; per-protocol bench validation (Phase 90); implementing the
0x34 X88C64 handler (still PCB-blocked, FUT-01).

**Repo:** all changes land in the `firestarter` sub-repo (native tests + the
dispatch-mirror test) plus possibly a host-side parse helper if the mirror test reads
`check_dispatch.py`'s table from the app repo. **NO dual-repo lockstep** — no wire/
constant change (this mirrors Phase 87's SAFE-06 posture).

</domain>

<decisions>
## Implementation Decisions

### Trace fidelity (Area 1)
- **D-01:** Golden traces are **byte-exact full ordered `(reg, data)` sequences** —
  equality-compared against a pinned expected array, asserting both count and every
  element. This is the strongest oracle: any register-write change in Phase 89 trips
  it. (Rejected: key-register-subset and behavioral-only — those leave the recompose
  under-protected; the operator chose maximum strength.)
- **D-02:** **Re-bless is allowed in Phase 89.** The golden trace is NOT frozen
  byte-identical forever — when Phase 89 inspects a trace diff and confirms it is a
  benign reorder / behaviorally-equivalent change, it may regenerate the expected
  array. **The re-bless commit is the audit checkpoint** (the deliberate human-review
  gate). A failure in Phase 89 therefore means "inspect this diff," not automatically
  "regression." (Rejected: frozen-byte-identical — too constraining on primitive
  design; and frozen-with-escape-hatch — operator preferred re-bless as the normal
  reviewed workflow.)

### Trace coverage (Area 3)
- **D-03:** Each family gets a byte-exact golden trace for the **write/program path
  (end-to-end)** AND the **chip-id path** where the family has one. This is exactly the
  union of Phase-89's primitive touchpoints:
  - The write path inherently exercises **P3** (VPP gate), **P5** (poll + verify-
    readback), and **P7** (SDP unlock) for the families that use them.
  - The chip-id path covers **P4** (`CMD_CHECK_CHIP_ID` compare/report) — a *separate*
    command path that the write trace does not reach. Per Phase-89 SC#2, the four
    chip-id call sites are eprom, flash_intel, eeprom28c, and flash4 (`flash_utils`).
  - Read / blank-check paths stay covered by the existing Phase-87 INV tests — not
    re-traced here (avoids duplication and trace bloat).
- **D-04:** **Fixture-sizing under the 256-entry recording cap** — the recording bus
  caps at `HOST_STUBS_MAX_RECORDING = 256`. Write traces (especially flash4's 256-byte
  page write) MUST use a **minimal representative input** sized to stay under the cap
  while still exercising the full algorithm shape. (Per Phase-87 precedent, INV-04
  already switched to a 65-byte probe to avoid recording-buffer overflow — reuse that
  discipline.)

### Dispatch-mirror source of truth (Area 4)
- **D-05:** **Bind all three.** The dispatch-mirror test is a cross-representation
  consistency check proving the protocol→handler order agrees across:
  1. **`firestarter/doc/PROTOCOLS.md` §0 table** (the canonical documented order, D-01
     of Phase 87 — single source of truth). It is already machine-parseable:
     `| hex | DB chip count | handler | datasheets folder | algorithm-axis name |`
     at lines ~22–35.
  2. **`firestarter_app/tools/check_dispatch.py`** `_ALGO_MEM_TYPE` / dispatch-sim.
  3. **firmware `configure_memory()` dispatch** (the thing Phase 89 actually
     refactors).
  A drift in ANY of the three trips the test. (Rejected: native-firmware-vs-doc only,
  and host-tool-vs-doc only — the operator wanted the full three-way bind for a true
  oracle.)
- **D-06:** The dispatch-mirror guards the **full dispatch table** (all protocols incl.
  SRAM 0x0E/0x27/0x28/0x29 and 0x34 → `not_implemented`), not just the five recompose
  families — the golden traces cover the five families; the mirror covers the whole
  dispatch order. **Reuse the existing PROTOCOLS.md §0 table** — do not author a new
  canonical table.

### Carried from milestone safety model (LOCKED)
- **D-07:** `check_dispatch.py` exits **0 violations** and `diff_db.py` is **empty**
  against the Phase-86-repinned baseline — **no DB record changes this phase** (SAFE-04,
  ROADMAP SC#3).
- **D-08:** `pio run -e leonardo` shows **near-zero flash delta** — this is test +
  doc-parse work, no PROGMEM strings added to firmware. (Tests compile only into
  `[env:native]`; production builds never see them.)
- **D-09:** The firmware over-voltage VPP check and the host `chip_resolver.resolve_chip`
  guard are **verified present and unmodified** (SAFE-04, ROADMAP SC#4); the 2516 stays
  `UNVERIFIED` — not spent.

### Claude's Discretion
- **Golden-reference representation (Area 2):** the operator delegated the *form* to
  the planner — inline expected-array literal in the `test_val_*.cpp`, a generated
  `.inc` fixture header, or another committed representation. **Constraint:** it must
  be (a) committed, (b) equality-compared (count + every element), and (c) **cheaply
  regenerable** so the D-02 re-bless workflow is a one-step rerun producing a clean,
  human-reviewable git diff. A small recorder/print mode is the implied mechanism.
- Which existing native `test_val_*` suite hosts each golden trace, and the precise
  assertion helper mechanics (e.g. a shared `assert_trace_eq(expected, n)` helper) —
  planner/executor's call, consistent with the existing recording-bus API
  (`clear_bus_recording` / `bus_recording_count` / `recorded_reg` / `recorded_data`).
- Whether the dispatch-mirror test lives native-side, host-side (pytest), or as a
  small cross-repo parse harness — as long as all three representations (D-05) are
  bound. The natural split: a host-side parser binds PROTOCOLS.md ↔ check_dispatch.py,
  while the existing native `test_dispatch` per-protocol routing tests anchor the
  firmware leg; planner decides the cleanest single-test-or-pair shape.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase / milestone definition
- `.planning/ROADMAP.md` — v1.16 §"Phase 88: Golden Traces + Dispatch-Mirror Guard"
  (goal + 4 success criteria) and the surrounding Phase 87/89 entries for the
  recompose-pipeline framing.
- `.planning/REQUIREMENTS.md` — **PRIM-01** (golden traces + dispatch-order test before
  any extraction), **SAFE-01** (key on `handle->protocol` never `electrical.type`;
  WARNING-5 structural guards preserved — recurs in 89), **SAFE-02** (INV invariants
  survive each recompose step, asserted under native register tests), **SAFE-04**
  (over-voltage stays blocked; `resolve_chip` host guard never bypassed; 2516 stays
  UNVERIFIED).

### What Phase 87 delivered (the contract this oracle protects)
- `.planning/phases/87-naming-documentation-pass/87-CONTEXT.md` — the INV-01..09
  matrix + native-test traceability decisions (D-05/D-06 there); explicitly hands off
  "full per-family register golden traces" to **this** phase.
- `firestarter/doc/PROTOCOLS.md` — **§0 table** (protocol→handler, lines ~22–35) is the
  canonical documented dispatch order for the D-05 three-way bind; **§3** is the
  INV-01..09 traceability matrix (the invariants the golden traces must keep green).

### Firmware handlers traced (the PRIM-01 targets)
- `firestarter/src/proms/eprom.cpp` — 0x07/0x08/0x0B (INV-01/02/03/05/06/08).
- `firestarter/src/proms/eeprom_28c.cpp` — 0x0D (SDP, DQ7 poll; P5/P7 touchpoints).
- `firestarter/src/proms/flash_intel.cpp` — 0x10 (VPP gate, chip-id; P3/P4).
- `firestarter/src/proms/flash_type_3.cpp` — 0x06 (SST39SF040; INV-09).
- `firestarter/src/proms/flash_type_4.cpp` — 0x05 (256B page; INV-04; P4 chip-id via
  `flash_utils`).
- `firestarter/src/firestarter.cpp` — `configure_memory()` dispatch entry (the firmware
  leg of the D-05 mirror; structure unchanged).

### Test harness + gates (reuse, do not rebuild)
- `firestarter/test/native/avr/_shared/host_stubs_common.inc` — the **recording bus**
  (`HOST_STUBS_RECORD_BUS`, Phase 71 HARN-01): `clear_bus_recording`,
  `bus_recording_count`, `recorded_reg(i)`, `recorded_data(i)`; 256-entry cap. This is
  the golden-trace capture mechanism.
- `firestarter/test/native/avr/test_val_eprom/` (and `…/test_val_eeprom28c`,
  `…/test_val_flash_intel`, `…/test_val_flash3`, `…/test_val_flash4`) — the per-family
  suites that already host the INV assertions; golden traces extend these.
- `firestarter/test/native/avr/test_dispatch/test_configure_memory.cpp` — existing
  Phase-12 per-protocol routing tests; the firmware-leg anchor for the D-05 mirror.
- `firestarter_app/tools/check_dispatch.py` — `_ALGO_MEM_TYPE`, `_SRAM_PROTOCOLS`,
  `KNOWN_PROTOCOLS`; the python leg of the mirror + the 0-violations gate (D-07).
- `firestarter_app/tools/diff_db.py` — must be empty vs the re-pinned baseline (D-07).
- `firestarter_app/tools/baseline/chip_database.baseline.json` + `dispatch_baseline.json`
  — the Phase-86-repinned (746-chip) baselines this phase is frozen against.

### Safety-posture verification targets (SC#4 / SAFE-04)
- firmware over-voltage VPP check (in the eprom/flash VPP-gate paths — `eprom_check_vpp`
  / `flash_intel_check_vpp`) — verify present + unmodified.
- `firestarter_app/firestarter/` host `chip_resolver.resolve_chip` guard — verify never
  bypassed.

### Toolchain discipline
- `firestarter_app/CLAUDE.md` + `.planning/` memory: validate any host change against
  **CI py3.11** (ruff / format / mypy / pytest) — the devcontainer py3.12 masks CI;
  generated `messages.py` never hand-normalized.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **Recording bus** (`HOST_STUBS_RECORD_BUS`, `host_stubs_common.inc`) — already
  records ordered `(reg, data)` pairs with `clear_bus_recording` / `bus_recording_count`
  / `recorded_reg` / `recorded_data`. The golden traces are a thin "equality-compare the
  whole captured array against a pinned expected array" layer on top — no new harness.
- **The five `test_val_*` suites** already exist and already activate the recording bus
  for the Phase-87 INV assertions — extend them, don't create new suites.
- **PROTOCOLS.md §0 table** is already machine-parseable (markdown pipe table, hex →
  handler) — the dispatch-mirror parses it directly; no new canonical table to author.
- **`check_dispatch.py` / `diff_db.py`** are the same gates as Phases 86/87 — rerun,
  expect 0 violations / empty diff (D-07).

### Established Patterns
- This is a "freeze-the-world-then-prove-nothing-moved" pass, exactly like Phase 87:
  add tests + a guard, with hard `check_dispatch` 0-violations / empty-`diff_db` /
  zero-flash-delta gates proving no electrical/DB change.
- **INV-04 fixture-sizing precedent** (Phase 87-03): the 257→65-byte probe switch to
  avoid recording-buffer overflow is the template for D-04 minimal-input sizing.
- INV ids are greppable across doc ↔ handler ↔ test (SAFE-02, Phase 87) — golden traces
  should keep those INV assertions green, not replace them.

### Integration Points
- The byte-exact golden traces (D-01) + re-bless workflow (D-02) ARE the SAFE-02 oracle
  Phase 89 consumes: each P7/P4/P3/P5 extraction reruns `pio test -e native`, and a
  trace failure is the review trigger.
- The dispatch-mirror (D-05) is the structural backstop that lets Phase 89 keep dispatch
  order stable while recomposing handler internals.

</code_context>

<specifics>
## Specific Ideas

- Golden trace = capture the FULL ordered bus sequence, assert count + every
  `(reg, data)` element — the strongest oracle the operator could pick (D-01).
- Re-bless is a *feature*, not a failure: in Phase 89 a benign trace diff is inspected,
  the expected array regenerated, and the re-bless commit becomes the audit trail (D-02).
- The dispatch-mirror is deliberately a three-way bind (doc ↔ tool ↔ firmware) so no
  single representation can silently drift during the recompose (D-05).

</specifics>

<deferred>
## Deferred Ideas

- **The primitive recompose itself** (P7 SDP-table dedup → P4 chip-id → P3 VPP gate →
  P5 poll) — Phase 89, frozen against the golden traces + dispatch-mirror this phase
  pins.
- **Per-protocol bench validation + PROTOCOL-LEDGER** — Phase 90.
- **0x34 X88C64 programming handler** — still PCB-blocked (FUT-01); not in v1.16 scope.

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 88-golden-traces-dispatch-mirror-guard-was-87*
*Context gathered: 2026-06-26*
