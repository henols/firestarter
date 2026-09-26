# Phase 71: Validation Harness + Matrix - Context

**Gathered:** 2026-06-16
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 71 delivers the **software-first, flash-free spine** of the v1.13 validation
milestone: a reusable three-tier validation harness, a declarative per-family
validation matrix, and an extended `check_dispatch.py` gate. It adds **zero
production firmware flash** (`pio run -e uno/leonardo` byte-count unchanged) and
bakes in a non-vacuous PASS oracle so later bench time is spent only on
proven-RED divergences.

**In scope:**
- Tier 1: native Unity per-family suites driven by a shared **recording** bus stub
  that captures `rurp_*` register-write sequences (handler provable by side-effect).
- Tier 2: host pytest wire round-trip via `make_comm`/`fake_serial` (no serial port).
- Tier 3: a host-driven `dev validate-family` runner composing the existing
  `write_cycle_eprom`/`consistency_check_eprom` cycle methods (no read/write re-impl).
- Declarative matrix data file driving both native + bench; emits a committed
  `validation-matrix.{json,md}` results artifact.
- `check_dispatch.py` per-family dispatch invariants + populated
  `non_supported_dispatchable` inverse detector (closes v1.12 accepted tech debt).

**Out of scope (other v1.13 phases):**
- Running the matrix for real / populating PASS-FAIL-SKIP evidence → Phase 73 (Tier-3 HIL).
- Resolving the SRAM no-op question → Phase 73 (VAL-06).
- Any per-family correctness fix → Phase 74. Erase path → Phase 75. Spec-only gaps → Phase 76.
- Protocol re-research / feasibility verdicts → Phase 72.

</domain>

<decisions>
## Implementation Decisions

### Matrix source-of-truth (HARN-02)
- **D-01:** The **authored** validation matrix is a single **app-owned JSON file**
  in `firestarter_app/` (location e.g. `tools/` or `firestarter/data/` — planner's
  choice). Python reads it directly; the C++ native suites consume it via a
  **codegen step that generates a C++ header** (same pattern family as the existing
  build_db / codegen flow). Test-only — no production flash impact.
- **D-02:** This authored source is **distinct** from the **emitted results
  artifact** `validation-matrix.{json,md}` required by HARN-02 (family × board ×
  verdict × evidence SHA, recording PASS / FAIL / SKIP-deferred per cell). Keep the
  two files conceptually and physically separate: one is hand-authored input, the
  other is generated output.
- **D-03 (rejected):** Meta-repo JSON + lockstep codegen to both sub-repos
  (messages.toml-style). Rejected — the matrix is test infrastructure, not a wire
  contract, so it does not warrant cross-repo lockstep ceremony or the
  py3.12-masks-CI-3.11 drift gate.

### Recording bus stub (HARN-01)
- **D-04:** Add register-write recording to the **existing shared**
  `firestarter/test/native/avr/_shared/host_stubs_common.inc` as a **define-guarded
  opt-in buffer** (e.g. `#define HOST_STUBS_RECORD_BUS`). Existing suites
  (test_dispatch, test_cobs_*, test_read_timing, etc.) compile **unchanged** — flag
  off = today's no-op behavior. Only the new per-family validation suites define the
  flag. Preserves the WR-06 single-edit-point consolidation; does NOT fork a second
  stub `.inc` (which would re-introduce the ~120-line drift WR-06 removed).

### `dev validate-family` runner (HARN-01, Tier 3)
- **D-05:** A **new subcommand under the existing `dev` group** (alongside
  read/reg/addr/consistency-check) that **composes** the existing
  `write_cycle_eprom`/`consistency_check_eprom` methods — no re-implementation of
  read/write — and **emits the matrix results artifact**.
- **D-06:** When no board/chip is present, the runner records a **SKIP-deferred**
  cell rather than hard-failing. This is what keeps the milestone closeable at
  partial bench coverage (the Tier-1/Tier-2 software cells remain ungated).

### Scope split (Phase 71 ↔ Phase 73)
- **D-07:** Phase 71 stands up **all 6 families' Tier-1 native + Tier-2 host wire
  cells GREEN** (these tiers are software, ungated, no bench needed). Phase 73 then
  only adds **Tier-3 HIL evidence + resolves the SRAM no-op (VAL-06)**. Front-loads
  the flash-free work per the software-first build-order driver; Phase 73 becomes
  purely bench.
  - The 6 families: `configure_eprom` (0x07/08/0B), `configure_eeprom28c` (0x0D),
    `configure_flash3` (0x06), `configure_flash4` (0x05/35/39),
    `configure_flash_intel` (0x10), `configure_sram` (0x0E/27/28/29).

### Roadmap-locked items (carried forward — not re-litigated)
- **D-08:** Non-vacuous PASS oracle (HARN-03): a PASS requires an independent
  post-write full read + SHA compare on **Leonardo** (advisory-only on other
  boards); a mandatory **passing negative control** (wrong-file mismatch + blank/
  chip-out failure proving verify *can* fail); retry-count capture; and a per-task
  **live R1/R2 calibration precondition** (`r1 ≈ 270000`). `uno328pb` is hard-coded
  **N/A** for any program/write cell.
- **D-09:** HARN-04: `check_dispatch.py` gains per-family dispatch invariants AND
  its hollow `non_supported_dispatchable` inverse detector is **populated** —
  a non-`supported` chip routing to a real handler, or a family handler enabling
  VPP it must not, fails the CI gate. Closes the v1.12 accepted tech debt
  (see [[project_phase70_shipped_v112_beta_merge]] CR-01 hollow-GATE-03).
- **D-10:** Reuse, do **not** fork: existing `[env:native]` + Unity + ArduinoFake,
  host `make_comm`/`fake_serial`, `write_cycle_eprom`/`consistency_check_eprom`,
  `check_dispatch.py`, `diff_db.py`.

### Claude's Discretion
- **Exact `dev validate-family` verb/flag spelling** (per-family arg vs `--all`/
  `--family` filter, command name) — deferred to planner (D-05/D-06 constraints hold).
- Authored-matrix JSON file path within `firestarter_app/`.
- Whether the generated C++ header is committed or built on-the-fly (determinism
  preferred either way; not a wire contract so no lockstep gate).
- Evidence-SHA capture mechanism for the emitted results artifact.
- Negative-control representation across software tiers (e.g. deliberate-mismatch
  assertion in Tier-1/Tier-2) vs the bench-only chip-out/blank failure.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Milestone / requirements
- `.planning/ROADMAP.md` §"Phase 71: Validation Harness + Matrix" — goal + 4 success criteria.
- `.planning/ROADMAP.md` §v1.13 milestone header — flash-ceiling build order, standing
  bench precondition, hybrid bench gating (the governing milestone framing).
- `.planning/REQUIREMENTS.md` HARN-01..HARN-04 — the four requirements this phase delivers.

### Reused harness substrate (reuse, do not fork — D-10)
- `firestarter/platformio.ini` §`[env:native]` (line 69) — Unity + ArduinoFake test env.
- `firestarter/test/native/avr/_shared/host_stubs_common.inc` — the shared no-op stub
  file to extend with the define-guarded recording buffer (D-04). WR-06 consolidation rationale in its header comment.
- `firestarter_app/tests/conftest.py` — `make_comm` / `fake_serial` host fixtures (Tier 2).
- `firestarter_app/firestarter/eprom_operations.py` (`write_cycle_eprom` ~L?,
  `consistency_check_eprom` L546) — cycle methods the Tier-3 runner composes.
- `firestarter_app/firestarter/cli_handlers.py` §`dev` group (L901+, consistency-check L1044)
  — where the new `dev validate-family` subcommand lands.
- `firestarter_app/tools/check_dispatch.py` — extend with per-family invariants +
  populate `non_supported_dispatchable` (HARN-04 / D-09).
- `firestarter_app/tools/diff_db.py` — DB diff gate (must stay green; not modified by 71).

### Research grounding
- `.planning/research/HARDWARE_SIM_SPEC.md` — recording-stub / hardware-simulation spec.
- `.planning/research/ARCHITECTURE_PATTERNS.md` — native/host test substrate patterns.
- `.planning/research/PROTOCOLS.md`, `.planning/research/CHIP_FAMILIES.md` — the 6 family
  algorithm-ID inventory the matrix enumerates.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `host_stubs_common.inc`: WR-06-consolidated shared stub; its header explicitly
  anticipates growing the stubs "to record calls" — exactly HARN-01's need (D-04).
- `[env:native]` Unity suites under `firestarter/test/native/avr/` (test_dispatch,
  test_eeprom28c_chip_id, test_flash_intel_vpp, test_read_timing, etc.) — per-family
  native suites slot alongside these.
- Host `make_comm`/`fake_serial` (conftest.py) — Tier-2 wire round-trip with no serial port.
- `consistency_check_eprom` / `write_cycle_eprom` (eprom_operations.py) — Tier-3 runner
  composes these; the 3-way PASS/FAIL/hw-error verdict already exists and is mirrored
  by `dev consistency-check`.

### Established Patterns
- Test-only files are PIO-discovered under `test/` and excluded from production
  `src_filter` — adding native suites and recording stubs cannot inflate production flash.
- Codegen-from-data already exists in the app (build_db pipeline) — the matrix→C++-header
  codegen (D-01) follows that established shape.
- `dev` CLI group is the home for non-production diagnostics — the new runner belongs there (D-05).

### Integration Points
- Authored matrix JSON → (a) Python host/bench reads directly, (b) codegen → C++ header
  for native suites.
- `dev validate-family` → eprom_operations cycle methods → emits `validation-matrix.{json,md}`.
- `check_dispatch.py` runs in CI as the dispatch-invariant + inverse-detector gate.

</code_context>

<specifics>
## Specific Ideas

- The matrix must make **partial bench coverage explicit, not silent** — every cell is
  PASS / FAIL / SKIP-deferred with a reason; SKIP-deferred is a first-class recorded state.
- "Provable by side-effect, not just op-pointer presence" — the recording stub must
  capture the actual `rurp_*` register-write *sequence*, so a handler that is wired but
  electrically wrong is still catchable.
- The PASS oracle must include a **negative control that itself passes** — i.e., the
  harness proves verify *can* fail (wrong file / blank chip), so a green cell is not vacuous.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope. Items intentionally pushed to later
v1.13 phases (Tier-3 evidence/SRAM no-op → 73; fixes → 74; erase → 75; spec gaps → 76;
protocol re-research → 72) are recorded as out-of-scope in the Phase Boundary, not as
new ideas.

</deferred>

---

*Phase: 71-validation-harness-matrix*
*Context gathered: 2026-06-16*
