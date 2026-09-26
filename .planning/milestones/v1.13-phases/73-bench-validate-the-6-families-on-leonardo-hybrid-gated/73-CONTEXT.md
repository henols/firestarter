# Phase 73: Bench-Validate the 6 Families on Leonardo (hybrid-gated) - Context

**Gathered:** 2026-06-17
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 73 **runs the Phase-71 validation harness against real hardware** and
produces the evidence that scopes Phase 74's fixes. It does NOT build new
infrastructure — the `dev validate-family` runner, the SKIP-deferred cell
mechanism, the emitted `validation-matrix.{json,md}` artifact, and the
non-vacuous PASS oracle all already exist from Phase 71.

**In scope:**
- Confirm all six families' **Tier-1 native + Tier-2 host wire** cells are GREEN
  (already stood up GREEN in Phase 71 — re-run / confirm, don't rebuild).
- Run **Tier-3 HIL on Leonardo** for the families with chips + a working shield
  on hand; record each as a real verdict (PASS / FAIL) with an independent
  post-write full read + SHA compare and a passing negative control.
- Record families without parts as **Tier-3 SKIP-deferred** with reason.
- **Resolve the VAL-06 SRAM no-op question** with bench evidence — classify
  `configure_sram` as table-stakes-PASS or as a FIX-01 correctness defect.

**Out of scope (other v1.13 phases):**
- Any per-family correctness fix (incl. FIX-01 SRAM real read/write) → Phase 74.
- Erase path → Phase 75. Spec-only / adapter-required / X88C64 gaps → Phase 76.
- The parked **FM1608 byte-0 write bug** — pre-existing, out of v1.13 scope
  (see Deferred). It must be *separated out* as a confounder here, not fixed.
- The v1.9 shield-fleet read-bug RCA (separate deferred milestone).

</domain>

<decisions>
## Implementation Decisions

### Bench inventory & shield (this session)
- **D-01:** **On hand** (run Tier-3 now): **W27C512** (0x07 family),
  **AM29F040** (Flash AMD 0x06), **FM1608** (SRAM family — see D-05). These three
  families get real Leonardo Tier-3 cells this session.
- **D-02:** **SKIP-deferred** (no chip on hand): **AT28C256** (5V EEPROM 0x0D),
  **AT29C040** (Flash type-4 0x05), **AM28F010** (Flash Intel 0x10). Their
  Tier-1/Tier-2 software cells are already GREEN (Phase 71); record Tier-3
  SKIP-deferred with reason `no chip on hand`.
- **D-03:** **Shield = Rev 2.0** on Leonardo for this session. Rev 2.0 reads clean
  on Leonardo (Phase 44 re-scope; no known Leonardo read-path fault). Per standing
  precondition, **re-confirm `controller:` identity per port** at each task start
  (ACM numbers shuffle on replug).

### W27C512 classification correction (operator, verified live)
- **D-04:** W27C512's `electrical.type` in `chip_database.json` is **`EEPROM`**
  (electrically-erasable, **12V VPP**, 28-pin, `support_status: supported`) — NOT
  a UV-EPROM. The ROADMAP's "UV-EPROM 0x07/08/0B" wording is a **handler-family**
  label (`configure_eprom` write algorithm), not an electrical-type claim. VAL-01's
  representative chip is specifically an erasable EEPROM; downstream agents must
  describe it that way (this also feeds Phase 75's erase path). Verified:
  WINBOND `part_number: "W27C512,W27E512"`, `electrical.type: EEPROM`, `vpp_mv: 12000`.

### VAL-06 SRAM no-op method (the headline resolution)
- **D-05:** The SRAM-family Tier-3 chip is **FM1608 — which is FRAM (non-volatile),
  not volatile SRAM.** Two consequences:
  1. The volatility confound disappears (FRAM persists across power loss) → a plain
     write→read-back is electrically clean.
  2. The known **FM1608 byte-0 write bug** becomes the confounder instead.
- **D-06:** Anti-false-positive rigor = **two distinct patterns (A then B)**: write
  pattern A, read-back; write pattern B, read-back. Both round-tripping proves real
  persistence (a floating-bus echo cannot track two different writes). Patterns must
  be non-trivial (not all-0x00 / all-0xFF).
- **D-07:** Verdict bar = **baseline initial read + N≥2 confirm**: read the chip's
  initial contents as a baseline first, then require the write+read-back result to
  reproduce on ≥2 runs before recording a verdict (avoids a one-off contact fault
  reading as a no-op).
- **D-08:** **Per-byte verdict logic** (separates VAL-06 from the parked byte-0 bug):
  - *All* bytes fail to persist → genuine silent no-op → **FIX-01 correctness defect**.
  - Bytes 1..N persist but byte 0 is wrong → `configure_sram` **does** write
    (VAL-06 no-op question = **table-stakes-PASS**); byte-0 is the **separate parked
    FRAM bug** (out of v1.13 scope), recorded as such — NOT a VAL-06 failure.
- **D-09:** VAL-06 is a **hard gate** to close Phase 73 — the FM1608 bench must
  produce a definitive verdict (table-stakes-PASS or FIX-01 defect). It gates Phase
  74 FIX-01. (Inconclusive ⇒ phase stays open; do not SKIP-defer SRAM.)

### Bench-driving model
- **D-10:** **Claude drives** `dev validate-family` / serial / sideload over USB
  passthrough from the devcontainer (proven workable per bench memory). The operator
  handles only physical actions: chip insertion, shield swap, multimeter, photos.
  Plans should be structured around Claude-driven sessions with explicit
  operator hardware-action checkpoints.
- **D-11:** Pre-write gate = **standard precondition only** — verify-port +
  **live R1/R2 readback (`r1 ≈ 270000`)** + the Tier-1 recording-stub VPP assertions.
  **No separate physical chip-OUT VPP multimeter dry-run** is required this phase
  (deliberate, operator-authorized relaxation of the standing precondition: W27C512
  at 12V is EVEN-01-proven clean on Leonardo, and Leonardo is chip-OUT-exempt for
  sideload). AM29F040 + FM1608 are no-VPP paths.

### Closeability & family priority
- **D-12:** On-hand families (W27C512, AM29F040, FM1608) close on **any recorded
  Tier-3 verdict** — PASS or FAIL. Phase 73 produces evidence; a **FAIL is a valid
  outcome** that routes to Phase 74. Each needs a recorded verdict + passing negative
  control. (Exception: VAL-06/FM1608 must reach a *definitive* verdict per D-09.)
- **D-13:** Milestone/phase is **closeable at partial coverage** — the 3 chip-less
  families close as Tier-1/Tier-2 GREEN + Tier-3 SKIP-deferred (D-02). Partial
  coverage is explicit per-cell, never silent.

### Carried forward from Phase 71 (locked — not re-litigated)
- **D-14:** The non-vacuous PASS oracle is already built (Phase 71 D-08): a PASS
  requires an independent post-write full read + SHA compare on **Leonardo**
  (advisory-only on other boards); a **passing negative control** (wrong-file
  mismatch + blank/chip-out failure proving verify *can* fail); retry-count capture;
  live R1/R2 precondition. **`uno328pb` is hard-coded N/A** for any program/write
  cell — never recorded as PASS, and a 999.1/999.2 confounder is never logged as an
  algorithm bug.
- **D-15:** The `dev validate-family` runner + SKIP-deferred mechanism (Phase 71
  D-05/D-06) and the authored matrix → emitted `validation-matrix.{json,md}`
  artifact (Phase 71 D-01/D-02) are **reused, not rebuilt**. Phase 73 adds zero
  production firmware flash.

### Claude's Discretion
- Exact pattern bytes for the FM1608 A/B test (subject to D-06 non-trivial rule).
- Run ordering across the 3 on-hand families, and how operator hardware-action
  checkpoints are sequenced within Claude-driven sessions.
- Evidence-SHA capture/log format for each recorded cell (within the Phase-71
  artifact schema).
- Whether AM29F040's sector-vs-chip erase is exercised as part of its Tier-3 cell or
  recorded as advisory (Flash AMD erase is part of VAL-03's algorithm surface).

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Milestone / requirements
- `.planning/ROADMAP.md` §"Phase 73: Bench-Validate the 6 Families on Leonardo" —
  goal + 4 success criteria.
- `.planning/ROADMAP.md` §v1.13 milestone header — hybrid bench gating, standing
  bench precondition (Leonardo-only-PASS, live R1/R2, uno328pb=N/A, chip-OUT,
  ASK-rev, verify-port), flash-ceiling build order.
- `.planning/REQUIREMENTS.md` VAL-01..VAL-06 — the six requirements this phase
  delivers (VAL-06 is the headline SRAM no-op resolution).

### Upstream phase outputs (read these — they define what to run)
- `.planning/phases/71-validation-harness-matrix/71-CONTEXT.md` — the harness/matrix
  decisions Phase 73 consumes (D-05 runner, D-06 SKIP-deferred, D-08 oracle).
- `.planning/v1.13-PROTOCOL-ENUMERATION.md` — per-protocol feasibility verdicts
  (Phase 72). VAL-06 cites rows 0x0E/0x27/0x28/0x29; SRAM no-op routed to Phase 73
  → FIX-01 if confirmed.

### Harness substrate (reuse, do not fork)
- `firestarter_app/firestarter/cli_handlers.py` §`dev` group — the `dev
  validate-family` Tier-3 runner.
- The authored `validation_matrix_spec.json` (under `firestarter_app/`) + emitted
  `validation-matrix.{json,md}` results artifact — representative chips per family:
  eprom=W27C512, eeprom28c=AT28C256, flash3=AM29F040, flash4=AT29C040,
  flash_intel=AM28F010, sram=0x0E/27/28/29.
- `firestarter_app/firestarter/eprom_operations.py` — `write_cycle_eprom` /
  `consistency_check_eprom` cycle methods the runner composes.
- `firestarter/test/native/avr/_shared/host_stubs_common.inc` — recording bus stub
  (Tier-1 VPP-assertion source backing D-11).
- `firestarter_app/firestarter/data/chip_database.json` — chip electrical truth
  (source of the D-04 W27C512=EEPROM correction).

### Bench-operation memory (apply during execution)
- Standing precondition: Leonardo-only-PASS; verify `controller:` identity per port
  each task; ASK shield rev (here = Rev 2.0); chip-OUT before sideload is Uno-class
  only (Leonardo exempt); uno328pb=N/A for program/write.
- W27C512 bench gotchas: erase unsupported on the 0x07 *write* path (erase is
  Phase 75); use `-b` to write a non-blank chip.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `dev validate-family` runner (Phase 71): composes the existing cycle methods,
  records PASS/FAIL/SKIP-deferred, emits the matrix artifact. Phase 73 invokes it —
  no new read/write code.
- Non-vacuous PASS oracle (Phase 71 D-08): Leonardo-authoritative SHA compare +
  passing negative control + retry capture + live-R1 precondition + uno328pb N/A.
- Tier-1 recording bus stub: captures `rurp_*` register-write sequences — backs the
  VPP-assertion safety check that lets D-11 skip a physical meter dry-run.

### Established Patterns
- Partial bench coverage is a first-class recorded state (SKIP-deferred with reason),
  never silent omission.
- A green cell is non-vacuous only with a passing negative control proving verify
  *can* fail.

### Integration Points
- `dev validate-family` (Claude-driven, USB passthrough) → Leonardo on Rev 2.0 →
  emits per-family cells into `validation-matrix.{json,md}`.
- VAL-06 verdict → hands to Phase 74 FIX-01 (defect) or closes it not-needed (PASS).
- FAIL cells for any on-hand family → define the Phase 74 fix scope.

</code_context>

<specifics>
## Specific Ideas

- VAL-06 must distinguish **whole-write no-op** (all bytes fail → FIX-01) from the
  **byte-0-only FRAM bug** (parked, out of scope) via per-byte analysis (D-08).
- Two-pattern A→B is specifically chosen so a floating-bus / echo confound cannot
  masquerade as persistence (D-06).
- W27C512 must be described as an **electrically-erasable EEPROM (12V VPP, 0x07
  algorithm)**, not UV — the ROADMAP "UV-EPROM" label is handler-family shorthand.

</specifics>

<deferred>
## Deferred Ideas

- **FM1608 byte-0 write bug** — pre-existing parked debug item
  (`.planning/debug/fm1608-fresh-chip-baseline.md`), explicitly **out of v1.13
  scope**. Phase 73 *separates it out as a confounder* (D-08) but does not fix it.
- **Acquiring AT28C256 / AT29C040 / AM28F010** to lift their Tier-3 SKIP-deferred
  cells to real verdicts — a future bench session, not a Phase 73 blocker (D-13).

</deferred>

---

*Phase: 73-bench-validate-the-6-families-on-leonardo-hybrid-gated*
*Context gathered: 2026-06-17*
