# Phase 109: Destructiveness Gate + Safety - Context

**Gathered:** 2026-07-02
**Status:** Ready for planning

<domain>
## Phase Boundary

Make `dev test`'s destructiveness gate **structural** and machine-enforce its
orchestrator-only contract. Building directly on Phase 108's `chip_test.py`
(the test-plan engine), this phase:

1. **SAFE-01 — plan-construction gate.** `derive_plan()` today only *annotates*
   `destructive` on write/erase steps (Phase 108, annotate-only by design). This
   phase makes it **strip** them: a non-destructive plan's *executable* `steps`
   list literally lacks write/erase (structurally absent, not skipped at exec
   time). `--destructive` is read **only** from the current CLI invocation —
   never config, never env.
2. **SWEEP-05 — non-destructive default + banner.** Default plan = id + read +
   blank-check. Whenever N of M applicable tests ran and N < M, print a loud,
   unmissable "only N of M tests ran — pass `--destructive` on a scrap chip for
   the rest" banner.
3. **PATT-03 — UV small-region write cap.** For UV-EPROM chips the destructive
   write is capped to a **small, engine-defined, high-address contiguous
   window** — never widenable by any DB field (a misconfigured/malicious DB
   entry cannot enlarge it) — so an eraser-less tester can safely retry.
4. **SAFE-02 — orchestrator-only (verify).** Every op routes through
   `chip_resolver.resolve_chip` + the existing serial/operator path; the command
   sets no VPP, builds no raw protocol command, passes no `--force`; a firmware
   VPP-guard refusal is captured as a step *finding*, never silently retried.
   (Largely already structurally true from Phase 108; this phase adds the
   explicit verification.)
5. **SAFE-03 — machine-enforced contract.** A build-failing CI gate asserts
   `dev test`'s code paths add **zero** new firmware dispatch entries and
   **zero** new VPP-set call sites.

**Host-only. Bench-free.** No firmware change. The `@dev.command("test")` CLI
handler that consumes this gate is **Phase 112**; the report/banner *rendering*
lives with the report model (**Phase 110**) and CLI (**Phase 112**), but the
gate logic, banner *data* (N/M + locked-step list), UV cap, and CI check are
this phase. Must stay fully unit-testable via mock operator +
`EpromDatabase(skip_local_override=True)` (the `dev validate-family` seam).
</domain>

<decisions>
## Implementation Decisions

### Plan shape — reconciling SAFE-01 (structural absence) with SWEEP-05 (needs M)
- **D-01 (LOCKED): Advisory locked-list.** The executable `steps` list truly
  **omits** write/erase when `destructive=False` — the executor
  (`run_plan`) never iterates them, so there is no code path that could run a
  destructive op in a non-destructive run (satisfies SAFE-01's "structurally
  absent, not skipped at exec time"). The `Plan` object additionally carries a
  **separate advisory field** (e.g. `locked_destructive: list[(op, reason)]`)
  recording the write/erase steps that `--destructive` *would* have added. The
  banner (SWEEP-05) and the Phase-110 report read this advisory field for M;
  the executor never touches it. One `derive_plan` call, one object,
  transparent. Rejected: re-deriving the full plan a second time purely to
  count M (double derivation, M lives outside the plan object).
- **Implementation note for the planner:** this changes `derive_plan()`'s
  contract — the `destructive` kwarg goes from *annotate-only* (Phase 108) to
  *actually shaping the executable step list*. Keep `derive_plan` guard-bypassing
  (via `get_eprom`/`convert_to_programmer`, never `resolve_chip`) exactly as
  Phase 108 established.

### SAFE-03 CI gate — mechanism
- **D-02 (LOCKED): AST-based checker in `tools/`, gated by pytest.** Add a
  `tools/check_devtest_orchestrator.py` (AST-based, mirroring the existing
  `tools/check_dispatch.py` tool shape) that scans `chip_test.py` and the
  `dev test` handler function, **denying**: VPP-set call sites, raw
  command-dict / wire-JSON construction, and `force=True` / `--force`
  pass-through; and **asserting** the firmware is untouched. It must be
  genuinely populated and build-failing — **not** a hollow declared-empty
  detector (the accepted-tech-debt fate of v1.12's GATE-03). Rejected: a
  lighter grep/bash check (brittle, easy to fool).
- **D-03 (LOCKED): follow the established "can't-rot-hollow" wiring pattern.**
  `check_dispatch.py` is **not** a direct `ci.yml` step — it is exercised by a
  pytest (`tests/test_check_dispatch_invariants.py`) that runs it via subprocess
  and asserts **exit 0 on clean source AND exit non-zero on a planted-bad
  fixture**. The new gate MUST follow this same pattern (a `tools/` checker + a
  paired pytest with both a passing and a *deliberately-violating* fixture), so
  the `Run pytest with coverage` CI step is the actual enforcement point. A
  dedicated `ci.yml` step is optional/discretionary; the pytest is mandatory —
  a checker with no negative-fixture test is exactly the hollow-gate failure
  mode to avoid.
- **Host-only framing:** because `dev test` is host-only Python, the "zero new
  firmware dispatch entries" clause is naturally satisfied (no firmware repo
  change) — the checker asserts it, but the *real* risk it guards is a
  VPP-set / raw-command / `--force` call sneaking into the host orchestrator.

### Claude's Discretion (user answered "You decide" — grounded defaults below)
- **UV small-region window SIZE (PATT-03).** Locked shape: **small + top-anchored
  (high-address) + engine-capped module constant, never DB-configurable.**
  Exact byte count is a planner/researcher/bench-tunable detail (STATE substrate:
  "validate exact size/placement against real UV parts — bench-informed").
  Recommended starting default: **256 B at `[mem_size-256, mem_size)`** (matches
  Phase 108's `_WRITE_REGION_LENGTH=256` stand-in; base address has all high bits
  set so the address-derived XOR-fold pattern exercises the upper-address decode;
  tiny consumption → many retries on a non-erasable chip). The window replaces
  the Phase-108 `_WRITE_REGION_START=0 / _WRITE_REGION_LENGTH=256` stand-in and
  applies **only to UV-EPROM** chips; non-UV chips keep the engine's default
  region. The cap must be enforced in engine code — a DB field can never widen it.
- **"N of M" banner counting (SWEEP-05).** Planner's call within SWEEP-05's
  intent (loud, unmissable, instructs "`--destructive` on a scrap chip").
  Recommended default: **applicable-only** — M = the steps a `--destructive` run
  would actually **execute** for *this* chip (NA/inapplicable steps excluded:
  blank-check NA on SRAM/FRAM, id NA when the DB entry's chip-id sentinel is 0,
  erase NA on UV / non-`FLAG_CAN_ERASE`); N = the steps this non-destructive run
  executed. A ran-but-`BAD` step counts as "ran" (its verdict is a separate
  axis). This yields honest numbers ("3 of 5", the 2 missing being write+verify)
  rather than inflating M with never-achievable NA slots.
- Result/plan object field names (`locked_destructive` etc.), module-internal
  helper decomposition, and the exact deny-list of VPP-set / raw-command symbols
  the AST checker matches — planner's call, constrained by the locked decisions.
</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements & scope (this phase)
- `.planning/ROADMAP.md` — Phase 109 section (goal, depends-on Phase 108, 5
  success criteria) + the §v1.21 "Non-regression invariant (SAFE-01/02/03)" line
  (verified starting Phase 109, re-affirmed through Phase 114 close)
- `.planning/REQUIREMENTS.md` — SAFE-01, SAFE-02, SAFE-03, SWEEP-05, PATT-03

### Design intent (the "why" — read before planning)
- `.planning/notes/dev-test-design-decisions.md` — the technology-aware
  destructiveness table (UV = small-region write, skip electrical erase;
  EEPROM/Flash = full round-trip), the non-destructive default, and the exact
  "only N of M tests ran" banner wording this phase implements
- `.planning/phases/108-test-plan-engine-address-derived-pattern-fingerprint/108-CONTEXT.md`
  — Phase 108's locked decisions this phase builds on: D-01 (address-XOR-fold
  pattern), **D-02 (region-parameterized generator — do not bake full-chip
  assumptions; Phase 109 supplies the UV cap)**, verdict vocabulary, the
  annotate-only `derive_plan` contract that 109 evolves
- `.planning/seeds/community-chip-validation-command.md` — original `/gsd-explore` seed
- `.planning/research/SUMMARY.md` — HIGH-confidence research; the resolved open
  questions (address-derived-not-fixed pattern; FLAG-only / no-auto-graduate)

### Reusable code (firestarter_app/)
- `firestarter/chip_test.py` — the Phase-108 engine this phase modifies:
  `derive_plan()` (annotate-only → strip + advisory list), `generate_pattern(start, length)`
  (region-parameterized, ready for the UV cap), the `_WRITE_REGION_START=0 /
  _WRITE_REGION_LENGTH=256` stand-in (lines ~556–562) that PATT-03 replaces,
  `run_plan()` + `_resolve_or_none` / `_run_step` (already route through
  `resolve_chip`, set no VPP, pass no `--force` — the SAFE-02 property to preserve)
- `firestarter/chip_resolver.py:16` — `resolve_chip` (the guard every *executed*
  op routes through; SAFE-02)
- `firestarter/constants.py` — `FLAG_CAN_ERASE` (already imported in
  `chip_test.py`); electrical-type / protocol-id sets used by `derive_plan`
- `tools/check_dispatch.py` — **shape to mirror** for the new
  `tools/check_devtest_orchestrator.py` (AST-based `tools/` checker, exit-code
  discipline)
- `tests/test_check_dispatch_invariants.py` — **pattern to mirror** for the SAFE-03
  gate's pytest: runs the checker via subprocess, asserts exit 0 on clean +
  (must add) non-zero on a planted violation fixture — the anti-hollow contract
- `.github/workflows/ci.yml` — the `Run pytest with coverage` step is the real
  enforcement point (py3.11 target; watch the py3.12-masks-CI ruff/codegen trap)
- `firestarter/cli_handlers.py:1474` — `dev_validate_family` (the sibling handler
  + `EpromDatabase(skip_local_override=True)` + mock-operator unit-test seam; the
  `@dev.command("test")` handler that the SAFE-03 checker will also scan is
  **Phase 112**, not this phase)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `chip_test.derive_plan()` / `generate_pattern()` / `run_plan()` — the Phase-108
  engine. `generate_pattern` is already region-parameterized (D-02), so the UV
  cap is a matter of choosing `start`/`length` for UV chips, not touching the
  generator.
- `tools/check_dispatch.py` + `tests/test_check_dispatch_invariants.py` — the
  exact tool-plus-negative-fixture-pytest pattern the SAFE-03 gate copies.
- `EpromDatabase(skip_local_override=True)` + mock operator — keeps every 109
  change unit-testable without a bench.

### Established Patterns
- **Checker tools are gated by pytest, not by a bespoke `ci.yml` step** —
  `ci.yml` runs `pytest`, and a test subprocess-invokes the checker asserting its
  exit code (both clean-pass and planted-fail). This is the codebase's
  non-hollow-gate convention (D-03).
- `derive_plan` deliberately **bypasses** `resolve_chip` for *derivation* (via
  `get_eprom`/`convert_to_programmer`) while *execution* routes through
  `resolve_chip` — preserve this split (SAFE-02).
- `run_plan` already sets no VPP, builds no wire dict, passes no `--force` — the
  SAFE-02 property to keep and now assert mechanically.

### Integration Points
- The advisory `locked_destructive` field (D-01) is consumed by the SWEEP-05
  banner *this* phase and by the Phase-110 report model.
- The UV small-region cap (PATT-03) feeds the address-derived pattern via
  `generate_pattern(start, length)` — no generator change needed.
- The SAFE-03 checker will additionally scan the Phase-112 `dev test` handler
  once it exists; scope the checker so it tolerates the handler's absence now and
  covers it when added (or land the checker's handler-scan in Phase 112 — planner's call).
</code_context>

<specifics>
## Specific Ideas

- The UV small-region cap is explicitly a **safety-against-a-bad-DB** mechanism,
  not just a convenience: SC4 requires "a misconfigured or malicious DB entry
  cannot widen the write region." The cap must live in engine code, above/around
  any DB-sourced size — never read a region size from the chip entry.
- The SAFE-03 gate's design is a direct response to this project's own
  hollow-GATE-03 tech debt (v1.12): the operator wants the orchestrator-only
  contract *machine-enforced with a real negative test*, not merely documented.
- Fault-detection intent for the top-anchored UV window is grounded in the
  project's real RCAs (Bug A upper-address read-path faults): writing at the top
  of the address space with the address-derived XOR-fold pattern is precisely
  what surfaces stuck/aliased high address lines from a small write.
</specifics>

<deferred>
## Deferred Ideas

None from the discussion — it stayed within phase scope. Adjacent concerns are
already owned by other phases: report/banner *rendering* + provenance = Phase 110;
measured-voltage sampler = Phase 111; the `@dev.command("test")` CLI surface
(flag parsing, any interactive `--destructive` confirm, exit-code semantics) =
Phase 112; submission = Phase 113; no-auto-graduate lock = Phase 114.

### Reviewed Todos (not folded)
- `2026-06-24-skip-vpp-error-and-warning-checks-when-vpp-unused-on-reads.md`
  (score 0.9, area: firmware) — **reviewed, not folded.** It is a *firmware*
  VPP-check behavior change; Phase 109 is host-only and explicitly adds **zero**
  firmware change and **zero** VPP-set (SAFE-02/03) — the opposite axis. Keyword
  overlap (vpp/blank/read/check) only. Remaining 7 matches (avrdude fallback,
  COBS deadline, JP4 labels, photograph Rev-0, DATA_BUFFER spike, MODIFICATIONS
  rework, dead json_init) are all off-axis keyword false-positives — none folded.

</deferred>

---

*Phase: 109-Destructiveness Gate + Safety*
*Context gathered: 2026-07-02*
