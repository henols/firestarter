# Phase 111: Measured-Voltage Sampler (hardware-gated) - Context

**Gathered:** 2026-07-02
**Status:** Ready for planning

<domain>
## Phase Boundary

Deliver **VOLT-01** — a value-returning VPP/VPE millivolt sampler in
`firestarter_app/firestarter/hardware.py` that parses the existing
`MSG_DATA_VPP_VOLTAGE` (0xE4) / `MSG_DATA_VPE_VOLTAGE` (0xE5) wire frames the
current monitor only *prints*, and wire it into the `dev test` sweep so the
diagnostic report records the tester's actual rail voltage — turning "the write
failed" into "the write failed at 18.2V on a chip that needs 21V."

**This phase is host-only and additive.** It reuses the existing
`COMMAND_READ_VPP` (11) / `COMMAND_READ_VPE` (12) monitor command path — it
sets no VPP, builds no raw protocol command, adds no firmware dispatch entry
(the milestone's SAFE-01/02/03 non-regression invariant holds here too). The
sampler is a *return-value sibling* of today's bool-returning
`read_vpp_voltage`/`read_vpe_voltage`; the live monitor's output/behavior is
unchanged (SC3).

**Explicitly NOT this phase:** the `@dev.command("test")` CLI surface that
invokes the sweep and renders the report = Phase 112; submission = Phase 113;
disposition/no-auto-graduate = Phase 114. The `DiagnosticReport` model itself
was built in Phase 110 (this phase fills — and expands — its voltage slot).

**Success criteria (from ROADMAP.md, 3):**
1. `hardware.py` exposes value-returning `sample_vpp_mv()`/`sample_vpe_mv()`
   parsing 0xE4/0xE5 and returning the mV reading (today's variants only
   print + return `bool`).
2. The write step records the measured rail voltage into the report —
   **verified on Leonardo + RURP Rev 2.0** against a known-good chip (parsed
   mV matches the previously-printed value). ← the single hardware gate.
3. No existing `firestarter vpp`/`vpe` monitor output/behavior changes
   (additive, not a replacement).
</domain>

<decisions>
## Implementation Decisions

### Rail selection & report slot shape
- **D-01 (LOCKED): Sample BOTH rails; split the report's one slot into two.**
  The write step captures VPP **and** VPE every destructive run. The Phase-110
  report currently has a single combined `vpp_vpe_mv: int | None` slot
  (`diagnostic_report.py:297`) — this phase expands it to separate VPP/VPE
  fields. Rejected: sampling only the protocol-relevant rail (avoids a
  protocol→rail mapping that could go stale; both-rails also rules out a
  "wrong rail energized" fault); rejected VPP-only (misses the 0x0B/NMOS-UV
  chips whose write actually runs on the VPE regulator rail — see memory
  `project_phase79_gate_reexamined`).
- **Note:** expanding the Phase-110 `vpp_vpe_mv` slot into two (VPP/VPE) fields
  is squarely in this phase's remit — Phase 110 explicitly "leaves the slot"
  for Phase 111. Keep the single-source `to_dict()`/`render()` contract
  (Phase 110 D-01) intact when adding fields.

### Sampling count & aggregate
- **D-02 (LOCKED): N samples per rail → report the MEDIAN.** Grab a few frames
  from the read loop (which already streams repeated frames) and record the
  median mV — robust against a single transient misread (this project's
  VPP-misread history) while staying cheap. Rejected: single reading (a lone
  transient lands verbatim, no cross-check); rejected min (a single low
  outlier over-reports droop). N = **3–5**, exact value planner's discretion.
  Recording the raw sample count/samples in the report is discretionary.

### Timing relative to the write step
- **D-03 (LOCKED): Sample BEFORE and AFTER the write step** (two independent
  regulator reads per rail → up to 4 sample points on a destructive run). The
  VPP/VPE read is a self-contained serial command (energize regulator →
  measure → done) and `write_eprom` is a self-contained INIT→MAIN→END op — the
  rail **cannot** be tapped mid-pulse, so before/after are two *independent*
  energizations bracketing the write, not two points on one pulse. This gives
  an across-write change/droop signal. Rejected: before-only or after-only
  (less signal for the same round-trip cost the operator accepted).

### Non-destructive-run behavior
- **D-04 (LOCKED): Fire the sampler on non-destructive runs too** — take a
  single standalone VPP+VPE read even when there is no write step, as a "can
  your rig reach VPP/VPE?" diagnostic. This is **safe**: the read energizes the
  regulator and measures only, with **no A9/VPE/P1 socket routing** (memory
  `reference_vpp_vpe_no_socket_routing`) — safe with a chip seated. Fits the
  community tool + the Phase-109 "only N of M ran" story. On a non-destructive
  run the before/after slots are `NOT_MEASURED` (nothing to bracket); the
  standalone reading fills the plain VPP/VPE field. This is a behavior choice
  (when the sampler fires), not a new capability — within VOLT-01's scope.
- **Voltage field model (guidance, shape is planner's call):** destructive run
  → `{vpp,vpe}` each with `before_mv` + `after_mv` (median of N); non-
  destructive run → a single standalone `{vpp,vpe}_mv` (median of N) with
  before/after = `NOT_MEASURED`. Any absent reading (sampler error/timeout,
  frame not emitted) → `NOT_MEASURED`, never a false 0 (Phase 108/110 honest-
  fallback pattern).

### Bench validation scope (the hardware gate)
- **D-05 (LOCKED): Ship software-complete + unit-tested now; DEFER the live SC2 check.**
  Build + unit-test the sampler against **recorded/synthetic
  0xE4/0xE5 frames** (4×u16: VPP/VPE whole.frac + internal VCC whole.frac);
  defer the live "parsed mV == printed monitor value" confirmation on
  Leonardo + Rev 2.0 to a bench session as a **HUMAN-UAT / FUT item**. Matches
  the v1.17/v1.18 software-complete + hardware-deferral precedent and the
  milestone's explicit "isolate the one hardware-gated phase so the software
  MVP is never blocked" framing. Phase 112 proceeds on the sampler API
  immediately (it needs the code to *exist*, not to be bench-proven).
- **When bench-validated later (light procedure):** the non-destructive
  standalone read is checkable against `firestarter vpp`/`vpe` with any chip
  seated (no write, no consumption); the before/after write path can use an
  electrically-erasable chip (W27C512 / W29C020) that rewrites without being
  consumed. Standing bench discipline applies: live R1/R2 readback + verify
  `controller:` port identity per task; Leonardo is chip-OUT-sideload-exempt.

### Claude's Discretion (grounded defaults for research/planner)
- **Exact mV computation from the `%u.%uV` (whole/frac) frame** — parse the raw
  8 `param_bytes` via the existing `frame_parser._decode_param` u16 machinery
  (preferred over re-parsing the formatted `response.message` string); confirm
  the fractional-unit scaling. **Flagged as the likely `--research-phase 111`
  item** (frame parse + sampling count) per the v1.21 substrate.
- **Additive-sibling refactor** — extract a single-frame parse helper (e.g.
  `_sample_one_voltage(state) -> int | None`) that both the new sampler and
  (optionally) the existing `_read_voltage_loop` can call; **do NOT alter
  `_read_voltage_loop`'s printing/loop behavior** (SC3). Exact N (3–5), whether
  to record raw samples, and the flat-vs-nested voltage field shape are
  planner's call within D-01..D-04.
- **`flags` passed to the read command** — default `flags=0` unless research
  surfaces a needed flag.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements & scope (this phase)
- `.planning/ROADMAP.md` — Phase 111 section (goal, depends-on Phase 110, 3
  success criteria) + §v1.21 "Non-regression invariant (SAFE-01/02/03)" (zero
  new firmware dispatch / zero new VPP-set — holds here) + the "Phase 111 is
  the single hardware-gated validation, isolated" framing.
- `.planning/REQUIREMENTS.md` — VOLT-01 (line 42) + the exclusions table (line
  89: "the only near-firmware touch is parsing an existing VPP/VPE frame").

### Design intent (the "why" — read before planning)
- `.planning/notes/dev-test-design-decisions.md` — the two-tier diagnostic
  contract; measured VPP/VPE mV is an **auto-capture** field (not tester-
  prompted).
- `.planning/research/SUMMARY.md` — HIGH-confidence research; flags Phase 111
  (mV sampler frame parse + sampling count) as likely needing
  `/gsd-plan-phase --research-phase 111`.
- `.planning/phases/110-diagnostic-report-model-dual-output-provenance-prompts/110-CONTEXT.md`
  — the Phase-110 report model this phase fills: the single-source
  `to_dict()`/`render()` contract (D-01), the `NOT_MEASURED` honest-fallback
  (D-03), and the "leaves a slot for the Phase-111 measured VPP/VPE mV value"
  integration point that D-01 above expands.

### Reusable code (firestarter_app/)
- `firestarter/hardware.py:166` — `_read_voltage_loop` (the continuous
  print-loop + serial handshake to model the sampler on; **printing behavior
  must not change**, SC3); `:253`/`:259` — `read_vpp_voltage`/`read_vpe_voltage`
  (the bool-returning variants the mV samplers sit beside).
- `firestarter/messages.py:115-116` + `:681-698` — `MSG_DATA_VPP_VOLTAGE`
  (0xE4) / `MSG_DATA_VPE_VOLTAGE` (0xE5) defs: 4×u16 params
  (`param_bytes=8`, format `"VPP/VPE: %u.%uV, Internal VCC: %u.%uV"`).
- `firestarter/frame_parser.py:133` — `_decode_param` (u16 parse machinery) +
  `Response` namedtuple (`:17`, has `payload`/`id`) — parse the raw payload
  rather than the formatted message string.
- `firestarter/constants.py:66-67` — `COMMAND_READ_VPP=11` / `COMMAND_READ_VPE=12`
  (the `state` values the sampler sends; no new command).
- `firestarter/diagnostic_report.py:297` — `vpp_vpe_mv: int | None` (the slot
  D-01 splits into two) + `NOT_MEASURED` (`:43`); keep the single-source
  render contract.
- `firestarter/chip_test.py:501` — `run_plan()` + `:709` `_dispatch_multi_run`
  (the write/verify execution site the sampler wires into; `OP_WRITE` `:276`,
  `_DESTRUCTIVE_OPS` `:442`).
- `firestarter/cli_handlers.py:1474` — `dev_validate_family` +
  `EpromDatabase(skip_local_override=True)` + mock-operator seam (unit-test the
  sampler + wiring bench-free, against synthetic 0xE4/0xE5 frames — D-05).

### Domain / bench facts (memory)
- `reference_vpp_vpe_no_socket_routing` — the VPP/VPE read enables the
  regulator + measures only; **no socket routing** → safe with a chip seated
  (grounds D-04's non-destructive sampling).
- `project_phase79_gate_reexamined` — 0x0B (NMOS UV) write path uses the VPE
  regulator rail (~90% of 25V); 0x07/0x08 use the VPP-P1 rail (grounds D-01's
  both-rails choice).

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **`_read_voltage_loop` + `read_vpp/vpe_voltage`** — the serial handshake
  (`find_and_connect` → `expect_ack` → `send_ack` → DATA-frame loop) is exactly
  what the sampler needs; the sampler just returns the parsed mV instead of
  printing and returns after N frames instead of looping forever.
- **`frame_parser._decode_param` / `Response.payload`** — decode the 4×u16
  0xE4/0xE5 payload without re-parsing the human-formatted string.
- **`diagnostic_report.py` (Phase 110)** — the report object + `NOT_MEASURED`
  sentinel + single-source render; this phase adds VPP/VPE fields to it.
- **`dev_validate_family` mock-operator + `skip_local_override` seam** — the
  bench-free unit-test harness (build synthetic 0xE4/0xE5 frames to prove the
  parse, per D-05).

### Established Patterns
- **"Data here, rendering downstream" split** — the sampler + report fields are
  built here; the CLI render/`--output-dir` write (Phase 112) consumes them.
- **Honest-fallback over fabricated confidence** — `NOT_MEASURED` for absent
  readings (Phase 108 `indeterminate`, Phase 110 XPORT-01 `"not measured"`).
- **Orchestrator-only (SAFE-02/03)** — the sampler reuses `COMMAND_READ_VPP/VPE`
  (state 11/12); it adds **no** new firmware dispatch entry and **no** new
  VPP-set call site. Phase 109's `tools/check_devtest_orchestrator.py` AST gate
  will scan the wiring — keep it clean of VPP-set / raw-wire-dict / `--force`.

### Integration Points
- **Fills** the Phase-110 report voltage slot (`vpp_vpe_mv` → split VPP/VPE,
  each with before/after on destructive runs, standalone on non-destructive).
- **Wires into** `chip_test.py`'s write step (`_dispatch_multi_run` / `run_plan`)
  — sample before + after the destructive write; single standalone read on a
  non-destructive run.
- **Feeds** Phase 112 (the handler that renders the report + writes it).

</code_context>

<specifics>
## Specific Ideas

- The report should make the rail failure legible on one screen: for a failing
  destructive write, show VPP+VPE **before and after** so a maintainer sees "the
  rail sagged from 20.9V → 17.4V across the write" vs "the regulator never
  reached 21V to begin with" — two very different diagnoses.
- The non-destructive standalone read (D-04) means even a tester who never runs
  a destructive write still contributes a "my rig produces X mV VPP/VPE"
  data point — valuable triage for the community-report inbox.
- Parse the raw payload bytes, not the pre-formatted `"VPP: 12.05V, ..."` string
  — the formatted string is a display artifact; the millivolt truth is the
  4×u16 payload.

</specifics>

<deferred>
## Deferred Ideas

- **SC2 live hardware validation (Leonardo + Rev 2.0)** — deferred to a bench
  session as a HUMAN-UAT / FUT item per D-05. The software (sampler + wiring +
  unit tests against synthetic frames) closes this phase; the live "parsed mV
  == printed monitor value" confirmation is the deferred hardware gate. Light
  procedure documented in D-05.

### Reviewed Todos (not folded)
The todo matcher surfaced 8 matches (1 @ 0.9, 7 @ 0.6) — the **same off-axis
set Phases 109 and 110 already reviewed and rejected**. Phase 111 is host-only
(parse an existing VPP/VPE frame, no firmware change, sets no VPP); every match
is on the firmware / hardware / bench / docs axis and matched only on generic
keywords. **None folded** (scope guardrail overrides any auto-fold):
- `2026-06-24-skip-vpp-error-and-warning-checks-when-vpp-unused-on-reads.md`
  (0.9, firmware) — a firmware VPP-check *behavior* change; opposite axis (this
  phase touches no firmware and only *reads* the VPP/VPE monitor frame).
- `avrdude-mcu-detection-fallback.md`, `cobs-decoder-framelevel-deadline-wr01.md`,
  `fix-jp4-labels-and-rev2-revision-block.md`, `photograph-modified-rev-0.md`,
  `write-modifications-md-rework-trace.md`, `spike-databuffer-size-speed-delta.md`
  (all 0.6) — firmware / hardware / bench / docs work; generic-keyword
  collisions only, none describe the mV-sampler parse work.

</deferred>

---

*Phase: 111-Measured-Voltage Sampler (hardware-gated)*
*Context gathered: 2026-07-02*
