# Phase 89: Incremental Primitive Recompose - Context

**Gathered:** 2026-06-26
**Status:** Ready for planning

> **Renumbered:** this was the original Phase 88, displaced when the variant-decode
> phase was inserted as Phase 86 (operator decision, 2026-06-25). The ROADMAP entry
> carries a `*(was 88)*` annotation.

<domain>
## Phase Boundary

Extract the four shared primitives from the duplicated `proms/` handlers in
**biggest-saving-first order** (P7 → P4 → P3 → P5), each step a *refactor-under-test*
against the Phase 88 byte-exact golden traces + dispatch-mirror, with Leonardo flash
shrinking. The four extractions:

- **P7 — SDP / const-table dedup (warm-up)** (PRIM-02): remove the duplicate
  `FLASH_ENABLE_WRITE_PROTECTION` table and the `EEPROM_SDP_DISABLE` duplicate; handler
  behavior unchanged under the native suites. Targets `include/flash_utils.h` const
  tables + `eeprom_28c.cpp`'s local SDP sequence (`{0x5555,0x80}`-style table at
  `eeprom_28c.cpp:46`).
- **P4 — chip-ID compare/report** (PRIM-03): a shared `chip_id_report` primitive
  handling compare + MSG frame + FORCE downgrade for all four call sites — eprom,
  flash_intel, eeprom28c (`eeprom_28c.cpp:73`), flash4 (via `flash_utils`,
  `flash_type_4.cpp:143-148`). Split the shared report logic from the protocol-specific
  read mechanism.
- **P3 — VPP gate** (PRIM-04): a shared `vpp_check_window` primitive (HIGH/LOW
  window-compare + byte-packing + FORCE downgrade), keyed on `handle->protocol`
  (never `electrical.type`), with regulator-routing bits parameterized per protocol.
  `eprom_check_vpp` (`eprom.cpp:262`) and `flash_intel_check_vpp`
  (`flash_intel.cpp:52`) each KEEP their own regulator-routing assertion, then call the
  shared check.
- **P5 — poll/readback verify** (PRIM-05): a shared `poll_readback` primitive used by
  `eeprom28c_wait_for_write` (`eeprom_28c.cpp:156`), `flash4_wait_for_page_write`
  (`flash_type_4.cpp:119`), and the verify-readback half of `eprom_write_execute`
  (`verify_and_update_mask`, `eprom.cpp:182`). Outer retry/page/erase algorithms stay
  intact.

Plus the always-on milestone gates (PRIM-06 / SAFE-01..04): Leonardo flash measured at
every step, `check_dispatch.py` 0 violations + `diff_db.py` empty at every step, native
golden traces stay green, safety posture unmodified.

**In scope:** the four primitive extractions; the per-step gate runs; the dedicated
primitives module; the flash measurement + final % report; deferring any single
primitive that can't meet its gate (with a documented reason).

**Out of scope:** any DB record change (`diff_db.py` MUST stay empty); any dispatch-order
change (the dispatch-mirror guards it); any wire/constant change (no dual-repo lockstep,
SAFE-06); per-protocol bench validation + PROTOCOL-LEDGER (Phase 90); the 0x34 X88C64
handler (PCB-blocked, FUT-01); changing the golden-trace harness or the over-voltage /
`resolve_chip` safety guards.

**Repo:** all changes land in the `firestarter` sub-repo (handlers + new primitives
module + native tests). **NO dual-repo lockstep** — firmware-only, wire/constant values
unchanged (SAFE-06).

</domain>

<decisions>
## Implementation Decisions

### Flash gate disposition (Area A)
- **D-01:** **Per-step `≤ +16B` tolerance, phase-cumulative net-decrease.** Each
  extraction step may rise at most +16 B vs the prior step (reuse Phase 87-04's
  `DELTA≤16` failable gate); the phase as a whole MUST end below the 25654 B Phase-88
  baseline. This honors the "monotonically shrinking" intent while tolerating the real
  call-overhead a shared function costs at its first call site — biggest-saver-first
  (P7) front-loads the headroom that P4/P3/P5 spend down. (Rejected: strict per-step
  `≤0` — can fail a legitimately-good refactor; cumulative-only — weakest per-step
  protection.) The **achieved final flash %** is reported at phase close (PRIM-06).

### Abort / partial-completion policy (Area B)
- **D-02:** **Abort-that-primitive-and-continue.** If a single primitive can't meet its
  gate (flash, trace reconcile, or `check_dispatch`/`diff_db`), skip it, commit the
  clean ones, and document the deferred primitive with a reason (a FUT/CR-style row),
  leaving its call sites in their pre-extraction duplicated form. Each extraction is
  "independently reversible" by design, so the milestone captures the wins (P7/P4
  especially) without stalling on the hardest case (P3 VPP is the most likely to bind:
  protocol-keyed + per-protocol regulator routing). (Rejected: stop-whole-phase — loses
  the clean extractions; re-bless-and-force — would rubber-stamp a real change exactly
  where the oracle matters most.)

### Primitive home / module structure (Area C)
- **D-03:** **Dedicated primitives module.** The cross-family code primitives — P4
  `chip_id_report`, P3 `vpp_check_window`, P5 `poll_readback` — live in a NEW
  `firestarter/src/proms/primitives.cpp` + `firestarter/include/primitives.h`. The P7
  SDP **const-tables** stay in `include/flash_utils.h` (they are flash-specific data,
  not cross-family code). Rationale: these primitives are called from eprom + eeprom28c
  + flash handlers, so a flash-namespaced home (`flash_utils`) would mis-name them;
  a dedicated module also realizes the milestone's "primitive-decomposed architecture"
  narrative. (Rejected: grow `flash_utils` — flash-namespaced, muddies cross-family
  use; fold into `memory.cpp` — bloats the dispatch file, mixes routing with impl.)
  *(Planner discretion on exact symbol names / signatures, consistent with existing
  handler conventions; the module location is fixed.)*

### Re-bless threshold during extraction (Area D)
- **D-04:** **Zero-diff is the hard goal; re-bless only on review.** Aim for
  byte-identical golden traces at every extraction step (ROADMAP SC: "native traces
  unchanged"). Re-bless the expected array ONLY when the diff has been inspected,
  confirmed a genuinely-benign register reorder / behaviorally-equivalent change, and
  documented in the commit message — the Phase-88 D-02 audit checkpoint. A trace failure
  is therefore "inspect this diff," and a re-bless is the deliberate, reviewed,
  human-gated event — not a routine step. (Rejected: re-bless-freely — erodes the
  "unchanged" contract, trace diffs stop being a signal; absolute-no-re-bless — forbids
  even provably-benign reorders, may make some clean extractions impossible.)

### Carried from milestone safety model (LOCKED — not re-discussed)
- **D-05:** `check_dispatch.py` exits **0 violations** and `diff_db.py` is **empty**
  against the Phase-86-repinned 746-chip baseline **at every extraction step** — no DB
  record change, no dispatch-order change (SAFE-03, ROADMAP SC#5).
- **D-06:** Every extracted primitive keys behavior on **`handle->protocol`, never
  `electrical.type`**; the `novpp_in_eprom` / `eeprom28c_in_eprom` (WARNING-5)
  structural guards are **preserved** (SAFE-01).
- **D-07:** All NAME-03 INV-01..09 invariants survive each step, asserted under the
  native register-level tests; the byte-exact golden traces (Phase 88 D-01) are the
  SAFE-02 oracle each P7/P4/P3/P5 step reruns `pio test -e native` against.
- **D-08:** Over-voltage stays blocked at the firmware VPP check; the
  `chip_resolver.resolve_chip` host guard is never bypassed; the 2516 stays
  `UNVERIFIED` (no irreplaceable UV part written on an unstable read path) (SAFE-04).
- **D-09:** Firmware-first, **NO dual-repo lockstep** — wire/constant values unchanged;
  no `firestarter_app` change beyond rerunning the existing gates (SAFE-06). Extraction
  order is **P7 → P4 → P3 → P5** (biggest-saving-first, ROADMAP-fixed).

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase / milestone definition
- `.planning/ROADMAP.md` — v1.16 §"Phase 89: Incremental Primitive Recompose" (goal +
  5 success criteria) and the surrounding Phase 88/90 entries for the recompose-pipeline
  framing and the "biggest-saving-first" ordering.
- `.planning/REQUIREMENTS.md` — **PRIM-02** (P7 SDP/const-table dedup), **PRIM-03** (P4
  chip-ID compare/report primitive), **PRIM-04** (P3 VPP-gate primitive keyed on
  `handle->protocol`, regulator-routing parameterized), **PRIM-05** (P5 poll/readback
  primitive, outer algorithms intact), **PRIM-06** (flash measured every step,
  net-non-increase gate, final % reported), **SAFE-01/02/03/04** (the locked gates +
  safety posture).

### The oracle this phase refactors against (Phase 88 deliverables)
- `.planning/phases/88-golden-traces-dispatch-mirror-guard-was-87/88-CONTEXT.md` — the
  golden-trace decisions: **D-01** byte-exact full ordered `(reg,data)` equality
  oracle; **D-02** re-bless-is-the-audit-checkpoint workflow (this phase's D-04 inherits
  it); **D-03** write-path + chip-id coverage = the union of P3/P4/P5/P7 touchpoints;
  **D-05** the three-way dispatch-mirror.
- `firestarter/doc/PROTOCOLS.md` — **§0** dispatch table (the mirror's canonical order),
  **§3** INV-01..09 traceability matrix (the invariants extractions must keep green).

### Firmware handlers being recomposed (the PRIM-02..05 targets)
- `firestarter/include/flash_utils.h` — the SDP / `FLASH_ENABLE_WRITE_PROTECTION` const
  tables (P7 dedup source); `flash_utils.cpp` (shared flash chip-id used by flash4 P4).
- `firestarter/src/proms/eprom.cpp` — `eprom_check_vpp` (P3, line 262),
  `verify_and_update_mask` (P5 verify-readback, line 182), chip-id (P4).
- `firestarter/src/proms/eeprom_28c.cpp` — local SDP-disable table (P7, line 50),
  `eeprom28c_check_chip_id` (P4, line 77), `eeprom28c_wait_for_write` (P5, line 156).
- `firestarter/src/proms/flash_intel.cpp` — `flash_intel_check_vpp` (P3, line 52),
  chip-id (P4).
- `firestarter/src/proms/flash_type_4.cpp` — `flash4_wait_for_page_write` (P5, line
  119), `flash4_check_chip_id_execute` → `flash_util_*` (P4, lines 143-148).
- `firestarter/src/proms/flash_type_3.cpp` — 0x06 (golden-trace family; no chip-id P4
  site per Phase 88 D-03).
- **NEW:** `firestarter/src/proms/primitives.cpp` + `firestarter/include/primitives.h`
  (D-03 — the home for the P4/P3/P5 code primitives).

### Test harness + gates (reuse, do not rebuild)
- `firestarter/test/native/avr/test_val_{eprom,eeprom28c,flash_intel,flash3,flash4}/` —
  the per-family golden-trace + INV suites; rerun `pio test -e native` after every
  extraction step (the SAFE-02 oracle).
- `firestarter/test/native/avr/test_dispatch/test_configure_memory.cpp` + the
  dispatch-mirror test (Phase 88 88-04) — guards dispatch order stays fixed.
- `firestarter_app/tools/check_dispatch.py` — 0-violations gate (D-05).
- `firestarter_app/tools/diff_db.py` — must stay empty vs baseline (D-05).
- `firestarter_app/tools/baseline/chip_database.baseline.json` +
  `dispatch_baseline.json` — the Phase-86-repinned (746-chip) baselines this phase is
  frozen against.
- **Flash measurement:** `pio run -e leonardo` (baseline = **25654 B** at Phase 88
  close) — the D-01 per-step `≤+16B` / phase-net-decrease gate; precedent gate logic in
  Phase 87-04's `DELTA≤16` check.

### Safety-posture verification targets (SAFE-04 / D-08)
- firmware over-voltage VPP check (`eprom.cpp:282`, `flash_intel.cpp:65`) — verify
  present + unmodified after each extraction (P3 touches this region).
- `firestarter_app/firestarter/` host `chip_resolver.resolve_chip` guard
  (`chip_resolver.py:55`) — verify never bypassed.

### Toolchain discipline
- `firestarter/CLAUDE.md` (build/test commands; Uno 512B / Leonardo 1024B buffer).
- `firestarter_app/CLAUDE.md` + `.planning/` memory: validate any host gate run against
  **CI py3.11** (the devcontainer py3.12 masks CI); generated `messages.py` never
  hand-normalized. (Host changes here are gate-runs only — no `firestarter_app` source
  change expected, SAFE-06/D-09.)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **Golden-trace recording bus + byte-exact suites** (Phase 88) — the per-step oracle
  is already in place; this phase consumes it, adds no harness. A re-bless = regenerate
  the expected array + reviewed commit (D-04).
- **`flash_utils.{h,cpp}`** already houses the SDP const-tables and a shared flash
  chip-id used by flash4 — P7 dedups the duplicate tables into here; the flash4 P4 call
  site already delegates to `flash_util_*` (a partial precedent for the shared chip-id
  primitive).
- **WARNING-5 structural guards** (`novpp_in_eprom` / `eeprom28c_in_eprom`) already
  exist and MUST be preserved through P3/P7 (SAFE-01/D-06).
- **`check_dispatch.py` / `diff_db.py`** — the same frozen-world gates as Phases 86/87/88;
  rerun, expect 0 violations / empty diff at every step.

### Established Patterns
- "Refactor-under-test": each extraction reruns the native golden traces + the two
  host gates; a trace failure is the review trigger (D-04), not auto-regression.
- **Phase 87-04 `DELTA≤16` flash gate** is the direct precedent for D-01's per-step
  tolerance (that phase achieved delta=0 against 25654 B).
- **Independently-reversible commits** — one atomic commit per primitive, gates run
  between (enables D-02 abort-that-primitive-and-continue). *(Commit granularity is
  planner/executor discretion within this pattern.)*

### Integration Points
- P3 (VPP gate) is the highest-risk extraction: it must key on `handle->protocol`
  (D-06/SAFE-01), keep each handler's per-protocol regulator-routing assertion local,
  and not disturb the over-voltage check (D-08) — the most likely candidate for D-02
  deferral if it can't reconcile cleanly.
- P5's third call site is the **verify-readback half** of `eprom_write_execute`
  (`verify_and_update_mask`) — the outer retry/page/erase loop stays untouched; only
  the inner poll/compare is shared.

</code_context>

<specifics>
## Specific Ideas

- Flash gate = Phase 87-04's `DELTA≤16` per-step tolerance, but with a phase-level
  net-decrease requirement on top (D-01). Report the achieved final flash % at close.
- New `proms/primitives.cpp` + `include/primitives.h` is the named home for the
  cross-family P4/P3/P5 primitives; P7's SDP tables stay flash-local in `flash_utils.h`
  (D-03).
- A re-bless is a reviewed, documented, human-gated event — not a routine post-extraction
  step (D-04). Treat a trace diff as "inspect," default to zero-diff.
- If P3 (or any one primitive) won't reconcile, ship the rest and defer it with a
  documented reason rather than stalling the milestone (D-02).

</specifics>

<deferred>
## Deferred Ideas

- **Per-protocol bench validation + PROTOCOL-LEDGER.{md,json}** — Phase 90 (composes
  with the v1.13 matrix + v1.15 EVIDENCE; 6 no-silicon buckets recorded UNVERIFIED).
- **0x34 X88C64 programming handler** — still PCB-blocked (FUT-01); not in v1.16 scope.
- **Any single primitive that can't meet its gate** — deferred per D-02 with a
  documented reason (FUT/CR row), to be revisited rather than forced.

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 89-incremental-primitive-recompose*
*Context gathered: 2026-06-26*
