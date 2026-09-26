# Phase 79: 25V NMOS Ceiling Raise - Context

**Gathered:** 2026-06-23
**Status:** Ready for planning (re-plan — supersedes prior 79-01 verdict)

<domain>
## Phase Boundary

Graduate the 4 NMOS UV-EPROMs that are fail-closed at `vpp-exceeds-max` because
they need 25V VPP — **INTEL M2716**, **INTEL M2732** (the combined
`2732,2732A,M2732,M2732A` entry), **SGS-THOMSON ETC2716**, **ST M2716** — to
`support_status: supported`. Host-only change surface (`firestarter_app/`):
`RURP_VPP_CEILING_MV` 22000→25000 + `check_dispatch.py` invariant + DB regen +
test updates. Hardware-gated on a corrected chip-OUT ≥25V VPP dry-run.

**This discussion re-examined the NMOS-01 gate and found the prior verdict
measured the wrong electrical path. The phase is re-planned, not blocked.**
Scope (the 4 chips, host-only constants) is unchanged.

</domain>

<decisions>
## Implementation Decisions

### Corrected hardware model (CORRECTS RESEARCH Q3 + Q6 — operator-authoritative, 2026-06-23)
- **D-01:** The VPP boost-converter output is set by a **manual potentiometer on
  the shield**, adjusted by the operator. It is **NOT** firmware-controlled and
  **NOT** fixed by PCB feedback resistors. RESEARCH Q6's "output set by PCB
  feedback resistors" claim is **wrong**, and REQUIREMENTS.md **FUT-03**'s
  root-cause ("AP3012 ... physically set by PCB feedback resistors ... requires
  a PCB feedback-resistor change") is **wrong** — the fix is to **crank the pot
  up**, not change resistors. R1/R2 in EEPROM only scale the ADC readback (this
  part of Q6 is correct).
- **D-02:** The firmware **DOES** enforce VPP — RESEARCH Q3 ("enforcement
  confirmed absent") is **wrong**. `eprom_check_vpp` ([firestarter/src/proms/eprom.cpp:209-272](../../../firestarter/src/proms/eprom.cpp#L209-L272))
  compares the measured rail against the host-supplied `vpp_mv`:
  - **Over-voltage** (`measured > vpp_mv + 500`) → `RESPONSE_CODE_ERROR`, blocked
    (unless `FLAG_FORCE`, which downgrades to WARN). This is the chip-damage guard.
  - **Under-voltage** (`measured < vpp_mv × 95%`) → `RESPONSE_CODE_WARNING` only,
    operation **proceeds**.
  This is exactly why the host sends `vpp_mv` to the firmware: to block
  over-voltage and warn on under-voltage.

### Corrected NMOS-01 gate methodology (supersedes 79-01's measurement; keeps its discipline)
- **D-03:** The prior 79-01 dry-run used `firestarter vpp`, but `CMD_READ_VPP`
  **always** forces the **dropped** path (`CTRL_VPP_REGULATOR_ENABLE |
  CTRL_VPP_VPE_DROP_ENABLE`, [firestarter/src/hardware_operations.cpp:28](../../../firestarter/src/hardware_operations.cpp#L28)) —
  the EPROM_STD/QUICK (0x07/0x08, "~13V") path. The 4 NMOS chips are
  protocol **0x0B / EPROM_LEGACY**, which uses the **direct VPE** path (drop
  disabled, [firestarter/src/proms/eprom.cpp:145-147](../../../firestarter/src/proms/eprom.cpp#L145-L147),
  documented "12–18V direct"). So `firestarter vpp` is the **wrong tool** for
  this gate — the ~12V it read is the dropped path, not what these chips see.
  **The 79-01 NOT-CLEARED verdict is superseded — it measured the wrong rail.**
- **D-04:** The corrected NMOS-01 dry-run, before any code change:
  1. Operator **cranks the shield VPP potentiometer to max**.
  2. Hold the **direct VPE rail** (regulator + VPE, **no** drop) — use
     `firestarter dev reg 0 0 0x86 -f` (0x86 = `CTRL_VPP_REGULATOR_ENABLE(0x80)`
     + `CTRL_VPE_ENABLE(0x04)` + `CTRL_VPP_A9_ENABLE(0x02)`; the v1.14 erase-rail
     hold reusable), **chip-OUT**, socket confirmed empty.
  3. Measure the **socket VPP pin** with the operator multimeter (authoritative)
     + firmware reading cross-check; record live R1/R2 reconcile.
  4. Record the silkscreen shield rev (operator-authoritative).

### Safety stance — ≥25V remains a HARD pre-gate (operator chose conservative)
- **D-05:** Even with the corrected model, the ceiling raise (NMOS-02) and
  graduation (NMOS-03) **do NOT proceed unless the corrected dry-run measures
  ≥25V on the direct VPE path at max pot**. Do **NOT** lean on the firmware's
  under-voltage warn-and-proceed to graduate a 25V chip on an inadequate rail —
  the chip must actually receive its rated VPP. If pot-max on the direct path
  still reads < 25V → the phase stays blocked (revisit as a future hardware
  task). The combined safety boundary is the firmware over-voltage **block** +
  this ≥25V pre-gate.
- **D-06:** Downstream sequencing unchanged from the original plan once the gate
  CLEARS: (1) corrected NMOS-01 dry-run → CLEARED ≥25V; (2) `RURP_VPP_CEILING_MV`
  22000→25000 + `check_dispatch.py` `_FAMILY_VPP_INVARIANTS` ceiling 22000→25000
  in step + DB regen + test fixes; (3) graduate the 4 chips to `supported` (host
  guard self-clears from the DB) only after a Leonardo write+verify SHA-match
  with a non-vacuous negative control.

### D-07 — Safety stance REVERSED to best-effort graduation (operator-authorized 2026-06-23, SUPERSEDES D-05/D-06)
- **Context (rail-corrected 2026-06-23):** At MAX pot the **VPE** (direct 0x0B)
  rail — the one the 4 NMOS chips program on — measures **22.4V** (operator DMM)
  / 23.9V (fw `firestarter vpe`), ~90% of 25V but still below it. (The ~15–19V
  figure earlier attributed to VPE was actually VPP / 18.7V fw `firestarter vpp`.)
  Reaching a true ≥25V rail would need a boost-stage hardware change — which the
  operator declines.
- **Operator decision (authoritative):** **There will be NO hardware changes,
  ever.** The ≥25V hard pre-gate (D-05) is **retired**. Instead:
  1. The 4 NMOS chips graduate to `supported` via the host software path (79-02)
     **regardless of the bench voltage** — graduation is NO LONGER gated on a
     ≥25V reading or on a bench SHA-match.
  2. A real write uses the existing **0x0B / direct-VPE** firmware path (already
     drop-disabled — no firmware change). The firmware's `eprom_check_vpp` WARNs
     on under-voltage and **proceeds**; over-voltage is still blocked. At
     the ~22.4V VPE rail (vs 25V) the write is **best-effort**: it may or may
     not fully verify, and an under-driven write **cannot damage the chip**.
  3. **79-03 is demoted** from a hard graduation gate to **informational
     best-effort bench validation** — run it when a chip is on hand, but the
     chips stay `supported` even if the write does not SHA-match ("any is fine
     and will not hurt anything" — operator). No revert on a failed bench write.
- **Why safe:** the firmware over-voltage block remains the damage boundary;
  under-voltage is harmless; the SHA-match (when run) is informational. This
  trades a guaranteed-correct write for best-effort programmability the user
  opts into.

### Claude's Discretion
- Exact register/`dev reg` incantation for the direct-VPE hold may be refined by
  research/planner against live firmware, provided it measures the **drop-disabled**
  rail (the 0x0B path), not `firestarter vpp`'s dropped path.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase 79 evidence & requirements
- `.planning/phases/79-25v-nmos-ceiling-raise/79-01-SUMMARY.md` — prior gate run;
  its NOT-CLEARED verdict is **superseded** by D-03/D-04 (measured the dropped
  path via `firestarter vpp`, not the 0x0B direct VPE path).
- `.planning/phases/79-25v-nmos-ceiling-raise/79-RESEARCH.md` — accurate on edit
  sites, DB state, and tests; **Q3 and Q6 are CORRECTED by D-01/D-02** (FW does
  enforce; setpoint is a manual pot, not PCB resistors).
- `.planning/REQUIREMENTS.md` §"25V NMOS Support — 999.7" (NMOS-01/02/03) and
  **FUT-03** — FUT-03's PCB-resistor root-cause is **wrong per D-01**; the
  re-plan should correct it (fix = crank the pot, not change resistors).

### Firmware VPP path (source of truth for the corrected model)
- `firestarter/src/proms/eprom.cpp` §`eprom_check_vpp` (209-272) + `eprom_write_execute`
  (143-153) — over-voltage ERROR / under-voltage WARN; 0x0B direct-VPE vs
  0x07/0x08 dropped path.
- `firestarter/src/hardware_operations.cpp:28` — `CMD_READ_VPP` always uses the
  dropped path (why `firestarter vpp` is the wrong gate tool).
- `firestarter/include/rurp_pinout.h` — control-register bits
  (`CTRL_VPP_REGULATOR_ENABLE` 0x80, `CTRL_VPP_VPE_DROP_ENABLE`, `CTRL_VPE_ENABLE`
  0x04, `CTRL_VPP_A9_ENABLE` 0x02).
- `firestarter/CLAUDE.md` §"Algorithm Handlers" — handler/VPP table (0x0B =
  "12–18V direct"; 0x07/0x08 = "13V via drop").

### Host edit sites (NMOS-02)
- `firestarter_app/tools/build_db.py:117` — `RURP_VPP_CEILING_MV = 22000` (→ 25000).
- `firestarter_app/tools/check_dispatch.py:78-79` — `_FAMILY_VPP_INVARIANTS["configure_eprom"] = (0, 22000)` (→ 25000).
- `firestarter_app/firestarter/chip_resolver.py:54-57` — host guard (self-clears
  when DB regen flips `support_status` to `supported`).

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **v1.14 erase-rail hold** (`firestarter dev reg 0 0 0x86 -f`): holds the
  undropped regulator+VPE rail for DMM measurement — exactly the direct-VPE path
  the corrected NMOS-01 gate must measure. (`reference_v114_bench_erase_rail_and_test_artifact`.)
- **Phase 77 graduation pattern**: host-only `support_status` flip via `build_db.py`
  regen + host-guard self-clear; Leonardo write+verify SHA-match as the final gate.

### Established Patterns
- **Firmware measure-and-protect**: host declares `vpp_mv`; FW `eprom_check_vpp`
  enforces tolerance (over=block, under=warn). The host never controls the rail.
- **Gate-first discipline**: a hardware gate evaluated before downstream code
  changes (mirrors Phase 78 DEFER discipline) — retained, but with corrected
  measurement (D-03/D-04).

### Integration Points
- DB regen (`python3 tools/build_db.py`) is the single mechanism that both
  re-classifies the 4 chips AND clears the host guard — never hand-edit
  `support_status`.

</code_context>

<specifics>
## Specific Ideas

- Operator's framing, verbatim intent: VPP regulator is controlled by a shield
  potentiometer (not FW); the host sends `vpp_mv` to the FW so it can **block
  over-voltage and warn on under-voltage**; for 25V EPROMs the pot must be
  **cranked to max** and the direct **VPE** path used. (The "happy-go-lucky /
  hope for the best" under-voltage fallback was acknowledged but **rejected for
  graduation** — D-05 keeps the hard ≥25V pre-gate.)

</specifics>

<deferred>
## Deferred Ideas

- **Soft graduation relying on under-voltage warn-and-proceed** — considered
  (FW warns and proceeds on under-voltage with no damage risk), but **rejected**
  this phase per D-05. Could be revisited as a `--force` / best-effort write mode
  in a future phase, separate from graduating chips to `supported`.
- **Correcting REQUIREMENTS.md FUT-03 root-cause text** (PCB-resistor → manual
  pot) — flagged for the re-plan/execute step; not a new capability.

</deferred>

---

*Phase: 79-25v-nmos-ceiling-raise*
*Context gathered: 2026-06-23*
