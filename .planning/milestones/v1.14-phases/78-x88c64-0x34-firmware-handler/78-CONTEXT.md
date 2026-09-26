# Phase 78: X88C64 0x34 Firmware Handler - Context

**Gathered:** 2026-06-22
**Status:** Ready for planning

<domain>
## Phase Boundary

Graduate the XICOR **X88C64P** (DIP24, 5V-only EEPROM, protocol `0x34`, **8051
multiplexed address/data bus** — ALE/WR/RD/WC, A/D0–A/D7 multiplexed, A8–A12
dedicated) to `supported` via a new `configure_x88c64` firmware handler — **IF
and ONLY IF** the gating ALE-routing control-bit question (`X88C64-FEASIBILITY.md`
Assumption A6, LOW confidence) is first resolved by investigation. The handler
implements page-write ≤32 B + toggle-bit **I/O6** polling, registered in
`memory.cpp` dispatch **before** the `protocol != 0 → configure_not_implemented`
guard. This is the **only firmware-adding gap** in v1.14 → **dual-repo lockstep**
(`firestarter/` firmware + `firestarter_app/` host).

**Gating-first structure (operator-locked):** the ALE investigation is the
FIRST plan and gates everything downstream. If ALE proves PCB-blocked (the
likely outcome — see D-01/D-02), the phase **closes cleanly with X88C64
documented-deferred (FUT-01), zero handler code** — no blind handler.

**Out of scope:** STORE/RECALL (X2210/X2212 NOVRAM family, NOT the X88C64P);
the other three v1.14 gaps (erase=P77 done, 25V NMOS=P79, AT28C adapter=P80);
read-bug RCA (v1.9). Per `X88C64-FEASIBILITY.md` §"Out of Scope".

**Carried forward from Phase 77 (SAFE-01/02/03 graduation discipline — locked,
do not re-litigate):** host-guard refusal drop is the FINAL step, gated behind
native register-bit test + host wire round-trip + Leonardo bench proof;
`check_dispatch.py` full-DB VPP-safety gate stays green (SAFE-02); any
`FLAG_*`/protocol constant touched ⇒ lockstep `constants.py` ↔ `firestarter.h`
parity tests green (SAFE-03).
</domain>

<decisions>
## Implementation Decisions

### ALE-routing investigation: method & deferral bar (gating XIC-01)
- **D-01:** **Trace-first.** The investigation is a thorough **software/schematic
  trace by Claude** — `firestarter/include/rurp_pinout.h` control-register bit
  map + `rurp_register_utils.h` / `rurp_shield.h` latch-strobe architecture +
  the shield schematic. NOT an operator physical bench-trace (reserved as a
  fallback only if the source trace is inconclusive).
- **D-02:** **Deferral bar = "no clean bit."** Close A6 as **PCB-blocked → FUT-01
  deferral, ZERO handler code** UNLESS the trace finds *either* a genuinely free
  `CTRL_*` bit *or* a **zero-risk reuse** of an existing control line that is
  provably idle during the X88C64 write window. We do **not** pursue speculative
  creative multiplexing of a busy line. **Scout pre-finding:** the 8-bit control
  register is fully allocated and bit `0x100` needs a 16-bit port the ATmega
  lacks ([rurp_pinout.h:71-128](../../../firestarter/include/rurp_pinout.h#L71-L129))
  → PCB-block deferral is the expected landing.
- **D-03 (deferral deliverable):** On PCB-block, deliver **(a)** the A6 verdict
  recorded in `X88C64-FEASIBILITY.md` with the concrete trace evidence, **and
  (b)** a short **future-unblock spec** — what a future milestone needs (PCB mod
  / new shield-rev control bit / dedicated ALE GPIO). FUT-01 stays open and
  becomes actionable. X88C64 stays `protocol-not-implemented` + host-refused.

### Physical readiness for the graduation gate (XIC-04)
- **D-04:** Operator has **neither a physical X88C64P chip nor a DIP24→DIP32
  adapter** on hand. Therefore the **SC#4 graduation flip to `supported` is
  hardware-blocked this phase regardless of the ALE verdict** — there is no chip
  to run the N≥5 write + read-back SHA-match + negative control on Leonardo.
- **D-05 (handler-write branch, only if ALE proves feasible per D-02):** **Write
  the handler + bank the no-hardware-provable work, defer graduation.** Deliver
  `configure_x88c64` (registered before the guard), the **Tier-1 native
  recording-stub register-sequence test** (SC#2 — no hardware needed), the host
  wire round-trip, and the measured Leonardo flash gate (SC#3). **Leave X88C64
  REFUSED / `protocol-not-implemented`** — the SC#4 graduation flip waits for a
  physical chip + adapter (record as a FUT-01-style "graduation pending hardware"
  note). The host-guard removal is NOT performed without the bench SHA-match.

### Flash-ceiling contingency (XIC-03)
- **D-06:** **Optimize-first, then report.** If a written handler pushes
  `pio run -e leonardo` over the ~90% gate, attempt **low-risk size reductions**
  (share helpers with `eeprom_28c.cpp`, `PROGMEM`, dead-code trim) and
  re-measure. Escalate the optimize-vs-accept-vs-defer call to the operator only
  if still over after a reasonable optimization pass. Leonardo baseline ~89.5%
  / ~3 KB free post-v1.13; handler est. ~1–3 KB.

### Claude's Discretion
- **Pinout entry strategy (A7) — planner's call (research flag, NOT locked):**
  reuse `DIP24_6116` vs. create a dedicated `DIP24_X88C64` entry. Decide based on
  how the host wire-config actually consumes the pinout for a custom-sequenced
  0x34 handler. Feasibility doc A7 (MEDIUM) notes a dedicated entry "may be
  cleaner"; operator left it to the planner. Only relevant on the handler-write
  branch.
- Exact handler file/header layout, the `0x34` constant naming, and Tier-1 test
  scaffold shape — planner's call, consistent with the `eeprom_28c` /
  `test_val_flash4` patterns surfaced in scout.
</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase scope, verdict & requirements
- `.planning/X88C64-FEASIBILITY.md` — **the canonical verdict.** §2 (8051 multiplexed bus, full DIP24 pin table), §3 (write protocol: ALE-latch → /WR strobe, page-write ≤32 B, I/O6 toggle-bit polling, STORE/RECALL correction), §4 (RURP feasibility, MEDIUM), §5 (what a future handler needs), §6 Assumptions A4/A5/A6/A7. **A6 is the gating question this phase resolves.**
- `.planning/ROADMAP.md` §"Phase 78: X88C64 0x34 Firmware Handler" — goal + 4 success criteria (SC#1 gating ALE, SC#2 handler+native test, SC#3 flash gate, SC#4 graduation FINAL step); §v1.14 milestone framing (build order, SAFE contract, standing bench precondition, flash budget).
- `.planning/REQUIREMENTS.md` — XIC-01/02/03/04; FUT-01 (X88C64 deferral if PCB-blocked); SAFE-01/02/03 (carried from P77); §"Out of Scope" (STORE/RECALL).
- `.planning/v1.13-PROTOCOL-ENUMERATION.md` row `0x34` — classification backing.

### Firmware (dual-repo lockstep — the handler-write branch)
- `firestarter/src/proms/memory.cpp` lines 74–119 — `configure_memory` dispatch; insert the new `0x34` arm **before line ~116** (the generic `protocol != 0 → configure_not_implemented` guard); after = dead code.
- `firestarter/src/proms/eeprom_28c.cpp` + `firestarter/include/eeprom_28c.h` — **closest analog** (protocol 0x0D, 5V single-supply, page-write + DQ7 toggle-bit poll). Model `configure_x88c64` / `eeprom_x88c64.cpp` on this; reuse helpers where possible (D-06 flash).
- `firestarter/include/rurp_pinout.h` lines 71–129 — control-register `CTRL_*` bit map (**the A6 trace target**); `firestarter/include/rurp_register_utils.h` lines 63–88 + `firestarter/include/rurp_shield.h` lines 53–56 — 74HC573 latch-strobe architecture (LSB/MSB/CONTROL strobes; no free ALE strobe today).
- `firestarter/include/firestarter.h` — command codes + `FLAG_*` bits; protocol consts are NOT defined here today; `0x34` constant TBD.
- `firestarter/test/native/avr/test_val_flash4/` (`test_val_flash4.cpp` + `host_stubs.cpp` with `#define HOST_STUBS_RECORD_BUS`) — **Tier-1 recording-stub exemplar** (SC#2); `test/native/avr/test_dispatch/test_configure_memory.cpp` — minimal dispatch test; `test/native/avr/_shared/host_stubs_common.inc` — recording API.
- `firestarter/platformio.ini` §`[env:leonardo]` (lines 57–67) — `pio run -e leonardo` is the SC#3 flash-gate measurement.

### Host (dual-repo lockstep)
- `firestarter_app/firestarter/constants.py` lines 79–88 (FLAG_*) / 97–109 (control bits) — **SAFE-03 parity mirror** of `firestarter.h`.
- `firestarter_app/tools/build_db.py` line 23 — `KNOWN_PROTOCOLS` (`0x34` present, status `protocol-not-implemented`).
- `firestarter_app/tools/check_dispatch.py` — full-DB VPP-safety gate (SAFE-02), must stay green.
- `firestarter_app/firestarter/chip_resolver.py` — `resolve_chip` host-guard refusal; its removal is the SC#4 FINAL step (**NOT performed this phase** per D-04/D-05).
- `firestarter_app/firestarter/data/chip_database.json` — X88C64P entry (`support_status: protocol-not-implemented`, `algorithm: 0x34`, `pinout: DIP24_6116`).

### Prior-phase pattern
- `.planning/phases/77-erase-write-path-graduation-0x07-ee-eproms/77-CONTEXT.md` — SAFE-01/02/03 graduation discipline this phase inherits.

### Standing bench precondition (EVERY hardware task — applies to SC#4 if it ever runs)
- `.planning/ROADMAP.md` §v1.14 "Standing bench precondition" — Leonardo is the ONLY trustworthy write/verify board (v1.9 read bug); uno328pb N/A (brownout); chip-OUT before any Uno-class sideload (**Leonardo exempt**); **ASK which silkscreen shield rev is mounted** (EEPROM byte can't distinguish Rev 2.2 / 2.0 / Modified Rev 0); re-verify `controller:` port identity per task; live `r1 ≈ 270000` reconcile.
</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **`configure_eeprom28c` (0x0D, `eeprom_28c.cpp`)** is the structural template for the new handler: 5V single-supply, page-boundary detection, toggle-bit write-completion poll. X88C64 differs by ALE-latch address phase + I/O6 (vs DQ7) toggle, but the write-init / write-execute / wait-for-write skeleton transfers directly. Sharing helpers helps the D-06 flash budget.
- **`test_val_flash4` recording-stub harness** (`HOST_STUBS_RECORD_BUS` + `clear_bus_recording`/`bus_recording_count`/`recorded_reg`/`recorded_data`) is the ready-made Tier-1 native-test pattern for SC#2 — assert the ALE/WR register sequence with no hardware.

### Established Patterns
- **Fail-closed dispatch:** new protocol arms go BEFORE the generic `protocol != 0` guard in `memory.cpp` (after = dead code). Confirmed insertion point ~line 110–115.
- **Host↔firmware constant parity** is a hard CLAUDE.md/CI rule (SAFE-03): touching any `FLAG_*`/protocol constant ⇒ lockstep `constants.py` ↔ `firestarter.h` + parity tests.
- **`check_dispatch.py`** is the standing VPP-safety regression gate (SAFE-02) after any DB/dispatch change.
- Devcontainer Python 3.12 masks CI (py3.9/3.11) — validate `ruff check` + `ruff format --check` against the target before claiming host CI green.

### Integration Points
- **The A6 blocker:** RURP control register is **8 bits, fully allocated** ([rurp_pinout.h:71-128](../../../firestarter/include/rurp_pinout.h#L71-L129)); address latches strobe via dedicated LSB/MSB/CONTROL pins (`rurp_shield.h:53-56`), not a free GPIO. No ALE strobe exists today → the trace (D-01) is expected to land on PCB-block (D-02).
- Handler-write branch chain (if A6 feasible): `chip_database.json` (0x34 entry) → host wire-config (pinout, A7) → firmware `configure_memory` 0x34 arm → `configure_x88c64` ALE/WR/RD sequence → I/O6 poll. Graduation flip + `resolve_chip` refusal removal held until bench SHA-match (D-04/D-05).
</code_context>

<specifics>
## Specific Ideas

- Operator framing: this phase is **gating-first and conservative** — "no blind handler." The trace decides; deferral is an acceptable, clean outcome, not a failure. The expected real-world landing is **documented deferral + a future-unblock spec**, because (1) the control register has no obvious free bit and (2) there is no physical chip to bench-prove anything.
- If the trace surprises us and ALE *is* feasible, **bank the firmware + native-test work now** (it's hardware-independent) but keep the chip refused until a physical X88C64P + DIP24→DIP32 adapter exist — don't fake a graduation.
</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope. (FUT-01 = X88C64 graduation pending ALE unblock and/or physical chip+adapter, tracked in REQUIREMENTS.md; the AT28C04 DIP24→DIP32 adapter build is Phase 80.)
</deferred>

---

*Phase: 78-x88c64-0x34-firmware-handler*
*Context gathered: 2026-06-22*
