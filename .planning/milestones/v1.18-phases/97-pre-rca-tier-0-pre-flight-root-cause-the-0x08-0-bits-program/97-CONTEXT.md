# Phase 97: PRE + RCA — Tier-0 Pre-Flight & Root-Cause the 0x08 0-Bits-Programmed Fault - Context

**Gathered:** 2026-06-29
**Status:** Ready for planning

<domain>
## Phase Boundary

A **diagnostic** phase — no firmware/host fix is written here (that is Phase 98). Phase 97 delivers four things on the seated AM27C020 (`0x08` EPROM-QUICK, 32-pin), bench-gated on **Leonardo + RURP Rev 2.0** with a DMM at socket **pin 1 (VPP)** and **pin 31 (PGM)**:

1. **PRE-01** — a non-destructive Tier-0 writability pre-flight (read oracle confirmed N≥3, blank-state SHA recorded, a single `1→0` micro-probe attempted).
2. **RCA-01** — the `0x08` 0-bits-programmed failure reproduced on real silicon with a captured signature (which bytes fail to flip, VPP ADC readback, DMM at pin 1 & pin 31, PGM-pin state).
3. **RCA-02** — a differential comparison against the passing `0x07` W27C512 isolating the differing variable(s) and exonerating the unchanged axes.
4. **RCA-03** — a named root cause (or ranked hypotheses, each carrying disconfirming evidence), classified firmware-algorithm / host-pinout / VPP-routing / addressing / silicon — sufficient to design the Phase 98 fix without further RCA.

Plus **SAFE-01** as a standing invariant: over-voltage stays ERROR-blocked at the firmware VPP check, the host `chip_resolver.resolve_chip` guard is never bypassed, AM27C020 flows through normal `0x08` dispatch with no test-only escape hatch.

**Not in this phase:** any code change to the write path, pinout, or DB; the byte-exact graduation (Phase 99); the definitive writable/dead silicon verdict (Phase 99, see D-04).
</domain>

<decisions>
## Implementation Decisions

### Tier-0 Micro-Probe (PRE-01)
- **D-01:** The Tier-0 writability micro-probe and the RCA-01 failure reproduction are **the same bench action** — a single program attempt at `0x000000` on the *current (unfixed)* path. There is **no separate destructive spend**. Observe whether *any* bit flips during that attempt:
  - **0 bits flip** (expected, given the 0-bits symptom) → failure reproduced (RCA-01) **and** writability **INDETERMINATE**. On the broken path a 0-flip is consistent with *both* "our path is broken" *and* "chip is OTP" — so it does **not** prove OTP and does **not** trigger deferral. The chip stays pristine (no cells consumed).
  - **Any bit flips** → RC-5 total-silicon-block is **OUT** and writability is partially proven; the failure signature is recorded as "partial."
- **D-02:** **PRE-01's Phase-97 deliverable is "writability indeterminate pre-fix"** — NOT a pass/fail blocker. The phase does not stall waiting for a definitive writability verdict. The planner must not treat PRE-01 as a Phase-97 gate that can fail the phase; the true writable/dead gate is the post-fix Phase 99 bench (see D-04). PRE-01 in Phase 97 = read oracle stable (N≥3 byte-identical) + blank-state SHA recorded + identity/protocol decode confirmed + micro-probe attempt result documented, never fabricated.

### RCA Exit Bar (RCA-02 / RCA-03)
- **D-03:** "Sufficient to design the fix" = **resolve the converging pair**. Each of **RC-1** (PGM pin 31 modeled as an address line) and **RC-2** (P1 VPP routing/level at pin 1) must be **individually confirmed-or-exonerated** with bench/code evidence before handoff to Phase 98, because they may *compound* (a one-axis fix could still flip 0 bits). RC-3 (JP4) and RC-4 (32-pin addressing collision) are pursued **only if** RC-1+RC-2 do not fully account for the 0-bits symptom. RC-5 is handled by the Tier-0 path (D-01/D-04). The RCA-03 record may name a single cause OR ranked hypotheses, but both pair members must carry a verdict.

### Pin-31 (PGM) Measurement Method (RCA-01 / RC-1)
- **D-05:** Primary evidence for the pin-31 program-window state = **held-rail static proxy + code-analysis**. A handheld DMM cannot resolve the ~100µs program pulse, so freeze the program-time control-register state via the proven `firestarter dev reg ... -f` technique (v1.14 held-rail method) so pin 31 sits **statically** at its program-pulse level; the operator DMMs **pin 31 and pin 1 steady-state**. Back this with file:line code-analysis of the bus-line-22 → address-bit-18 mapping (note: a 256K chip never sets A18, so pin 31 may idle **VIL** = program-active — the static measurement settles whether that holds at the socket). A logic analyzer / logic probe on the live pulse is **optional** (only if the operator has one handy), not the gating method.

### Deferral Disposition (PRE-01 ↔ BENCH-01/02)
- **D-06:** The "OTP/dead → defer BENCH to FUT, re-scope to software-fix-only" disposition is a **Phase 99 verdict**, reached **only after** the resolved converging-pair fixes (RC-1 PGM + RC-2 VPP) are applied (Phase 98) and bench-confirmed correct — **pin 1 measured 12.5–13.0V steady AND pin 31 confirmed VIL during the pulse** — and the chip **still flips 0 bits**. Path exonerated ⇒ residual cause = silicon (OTP/dead) ⇒ **FUT-06 carry-forward**, milestone re-scopes to software-fix-only, worded as a **clean disposition parallel to the W29C040** outcome (`project_v117_w29c040_locked_bootblock`) — never read or recorded as a failure. A 0-flip *before* the path is fixed never triggers deferral.

### SAFE Invariant (SAFE-01)
- **D-07:** Throughout the RCA, over-voltage stays blocked (`vpp_check_window` HIGH→ERROR, no `FLAG_FORCE` relaxation); the host `chip_resolver.resolve_chip` guard is never bypassed; AM27C020 flows through its normal `0x08` dispatch with **no test-only escape hatch**. VPP-low is only a WARNING (firmware proceeds), which is precisely why an under-voltage rail produces "0 bits, no error" — so a measured rail at pin 1 is mandatory before trusting any write verdict. The shield VPP magnitude is a **manual potentiometer** (D-07 standing): firmware enables/measures the rail but cannot set its level — confirm physically each session.

### Standing Bench Discipline (carried forward — locked, not re-litigated)
- **D-08:** `controller:` identity verified per task (ACM port numbers shuffle); live R1/R2 readback first (Leonardo, R1=270000); N≥3 byte-identical reads gate every write verdict — never trust N=1 (v1.15 saw a localized 12-byte read glitch on this chip at 0x008004–0x00800f). **Operator owns Rev 2.0 — ASK the exact silkscreen / JP4 (`JMP_VPP_P1_BYPASS`) open-vs-closed meaning before measuring or toggling JP4; the EEPROM hw byte cannot distinguish shield revs** (`user_shield_revisions`). Every program on this UV part is irreversible (no eraser on hand).

### Claude's Discretion
- Within the locked RC ranking and the 5-step Tier-0 protocol from the research brief, Claude/planner choose the concrete command sequencing, the cheapest-first disconfirmation ordering, and the held-rail control-register value(s) used for the pin-31 static proxy.
</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### RCA substrate (read first)
- `.planning/research/v1.18-AM27C020-27C-EPROM.md` — the authoritative RCA brief: datasheet facts, current `0x08` path read file:line, the 0x08-vs-0x07 differential, RC-1..RC-5 ranking each with a disconfirming bench test, the 5-step Tier-0 pre-flight, and the VPP-measurement method. Every Phase 97 decision above sits on this brief.
- `.planning/REQUIREMENTS.md` — v1.18 requirement bodies (PRE-01, RCA-01/02/03, SAFE-01) and Constraints/Standing-Context.
- `.planning/ROADMAP.md` §"Phase 97" — goal + 5 success criteria (the verbatim TRUE-conditions).

### Datasheets
- `firestarter/datasheets/0x08-EPROM-QUICK/AM27C020.pdf` — VPP 12.75V ±0.25 (12.5–13.0V window), Flashrite 100µs pulse on CE with PGM=VIL, 32-pin DIP pinout (pin 1=VPP, pin 31=PGM, pin 30=A17, pin 2=A16), 13.5V abs-max VPP/A9.
- `firestarter/datasheets/0x08-EPROM-QUICK/W27C020.pdf` — the INV-03 P1-as-VPP reference; a *different* chip (Winbond EEPROM, 12V program) — do NOT conflate with the on-hand AMD AM27C020.

### Current 0x08 code path (read direct, file:line in the brief)
- `firestarter/src/proms/eprom.cpp` — `configure_eprom`, `eprom_write_init/execute`, `eprom_check_vpp`, `program_mismatched_bytes`, `eprom_internal_set_control_register` (the `CTRL_VPE_ENABLE`→`CTRL_VPP_P1_ENABLE` rewrite for `using_p1_as_vpp`).
- `firestarter/src/proms/memory.cpp` — dispatch (`:121`), `mem_util_calculate_top_address_register`, `memory_set_data` (CE-only program pulse), `mem_util_remap_address_bus` (pin 31 → bus line 22).
- `firestarter/src/proms/primitives.cpp` — `vpp_check_window` (VPP-low = WARN/proceed, VPP-high = ERROR/block).
- `firestarter/include/memory_utils.h` (`using_p1_as_vpp`), `firestarter/include/rurp_pinout.h` (CTRL_* bits), `firestarter/include/rurp_shield.h` (`VPP_P1_32_DIP=0x15`, CHIP_ENABLE).
- `firestarter_app/firestarter/database.py` + `firestarter_app/firestarter/data/pinouts.json` — `DIP32_STD`, `pin_conversions[32][1]=21`, host bus-config build (pin-31→line-22).
- `firestarter_app/firestarter/cli_handlers.py` — `vpp`/`vpe` monitor commands (`:659`/`:671`).

### Bench evidence & ledger (pre-fix baseline + outcome target)
- `.planning/v1.15/bench/EVIDENCE.{md,json}` — Phase 83 row #2 + Phase 84 Task 3a: 0 bits, bad bytes 15/16 retries 20, JP4 closed, 0x07 wrote clean same session (the pre-fix seed signature).
- `.planning/v1.16/ledger/PROTOCOL-LEDGER.{md,json}` — `0x08` = `open-defect-carried (FUT-06)`; `0x07` PASS. Phase 99 updates this entry.

### Shield / hardware
- `firestarter/doc/SHIELD-REVISIONS.md` §7 + `.planning/v1.7-SHIELD-REVS.md` §3/§4 — JP4 = `JMP_VPP_P1_BYPASS`; Rev 2.0 = `P1_VPP_JMP` 1x2 header. **ASK operator the silkscreen meaning before toggling.**
</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **Held-rail DMM technique:** `firestarter dev reg 0 0 0x86 -f` holds the VPP rail for steady-state multimeter probing (v1.14 reusable, `reference_v114_bench_erase_rail_and_test_artifact`). D-05 extends this to freeze the program-time control register so pin 31 can be DMM'd statically.
- **VPP/VPE monitors:** `firestarter vpp` / `firestarter vpe` are measure-only (enable regulator + ADC, no A9/VPE/P1 socket routing) — safe with a chip seated (`reference_vpp_vpe_no_socket_routing`). Capture a window via `timeout -s INT 15 stdbuf -oL firestarter vpp`.
- **USB passthrough:** Claude can drive all firmware/host commands on the operator's bench from the devcontainer (`reference_usb_passthrough_bench`). Operator-only actions: DMM probing, JP4 toggling, photos, chip handling.

### Established Patterns
- **2×N differential isolation** (v1.17 W29C040-vs-W29C020 method): hold everything constant except the named axis; the passing sibling (here `0x07` W27C512, same `configure_eprom()`, same session/bench) exonerates the unchanged axes. RCA-02 follows this.
- **VPP-skip gates read/blank-check only** — the write path is untouched (Phase 84 T-84-14), so the 0-bits fault is genuinely in the `0x08`/32-pin write/VPP path, not transport, board, or read-side VPP handling.

### Integration Points
- This phase produces only diagnostic artifacts (signature, differential, RCA verdict) + a bench EVIDENCE row; the named root cause governs the Phase 98 fix surfaces (`eprom.cpp`, possibly `memory.cpp` / `pinouts.json` / a `DIP32_27C020` entry).
</code_context>

<specifics>
## Specific Ideas

- **Leading hypothesis to disconfirm first (RC-1):** AM27C020 programming needs CE=VIL **and** PGM(pin 31)=VIL with VPP present; `memory_set_data` strobes **only CE** and has no PGM-pulse concept; `DIP32_STD` maps pin 31 as bus line 22 (the 19th "address" line, authored for the 27C040 A18 case). The static pin-31 measurement (D-05) settles whether pin 31 actually sits at the program-active VIL during the pulse — note the brief's own observation that a 256K chip never sets address bit 18, so pin 31 *may* coincidentally idle low; bench confirmation decides RC-1 in or out.
- **Decisive single measurement:** the DMM at socket pin 1 (does the rail *reach the chip*?) vs the ADC node (`PIN_VPP_VOLTAGE_ADC=A2`, rail at the *monitor node*) — a divergence localizes a P1/JP4 routing fault vs a manual-pot magnitude fault.
- **Expected pass band:** pin 1 = 12.5–13.0V steady during the pulse (DB ships `vpp_mv=13000`; firmware HIGH threshold = vpp_mv + 500mV ⇒ tolerates ~13.5V before the over-voltage ERROR, matching the chip's 13.5V abs-max).
</specifics>

<deferred>
## Deferred Ideas

- **The Phase 98 fix itself** (PGM-pin assertion concept, P1 routing held across the full pulse window, a dedicated `DIP32_27C020` pinout distinguishing PGM from A18) — out of scope for Phase 97 (diagnostic only); governed by the RCA-03 verdict. Pin-31 changes must be scoped to the `0x08`-UV-32-pin class so existing 27C040/SST39SF040-family DIP32 users (pin 31 = A18/WE) are not broken.
- **FUT-05** (REWR-02 `0x08` rewritable write proof, W27E040 stuck-bit) — a separate deferred requirement; may benefit from the v1.18 `0x08` fix but is not v1.18 scope.

None of the 5 pending todos were folded — none touch the `0x08` write-path RCA (the closest, "Skip VPP error/warning checks when VPP unused on reads," is the read/blank-check path and already shipped in v1.15).
</deferred>

---

*Phase: 97-pre-rca-tier-0-pre-flight-root-cause-the-0x08-0-bits-programmed-fault*
*Context gathered: 2026-06-29*
