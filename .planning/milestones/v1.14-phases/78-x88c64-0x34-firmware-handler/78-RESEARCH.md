# Phase 78: X88C64 0x34 Firmware Handler — Research

**Researched:** 2026-06-22
**Domain:** Firmware handler addition (Arduino C++ / PlatformIO) + host constant parity
**Confidence:** HIGH (all critical claims verified from source code)

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **D-01 (Trace-first):** The ALE-routing investigation is a thorough software/schematic trace by Claude — `rurp_pinout.h` control-register bit map + `rurp_register_utils.h` / `rurp_shield.h` latch-strobe architecture. NOT an operator physical bench trace (reserved as fallback only if source trace is inconclusive).
- **D-02 (Deferral bar = "no clean bit"):** Close A6 as PCB-blocked → FUT-01 deferral, ZERO handler code UNLESS the trace finds either a genuinely free `CTRL_*` bit or a zero-risk reuse of an existing control line provably idle during the X88C64 write window. Do NOT pursue speculative creative multiplexing of a busy line. Scout pre-finding: the 8-bit control register is fully allocated and bit `0x100` needs a 16-bit port the ATmega lacks → PCB-block deferral is the expected landing.
- **D-03 (Deferral deliverable):** On PCB-block, deliver (a) the A6 verdict recorded in `X88C64-FEASIBILITY.md` with concrete trace evidence, and (b) a short future-unblock spec — what a future milestone needs (PCB mod / new shield-rev control bit / dedicated ALE GPIO). FUT-01 stays open. X88C64 stays `protocol-not-implemented` + host-refused.
- **D-04 (No physical chip):** Operator has neither a physical X88C64P chip nor a DIP24→DIP32 adapter. SC#4 graduation flip to `supported` is hardware-blocked this phase regardless of ALE verdict.
- **D-05 (Handler-write branch, only if ALE proves feasible per D-02):** Write the handler + bank the no-hardware-provable work, defer graduation. Deliver `configure_x88c64`, the Tier-1 native recording-stub register-sequence test (SC#2), the host wire round-trip, and the measured Leonardo flash gate (SC#3). Leave X88C64 REFUSED / `protocol-not-implemented` — the SC#4 graduation flip waits for a physical chip + adapter.
- **D-06 (Flash-ceiling contingency):** Optimize-first, then report. If a written handler pushes `pio run -e leonardo` over the ~90% gate, attempt low-risk size reductions (share helpers with `eeprom_28c.cpp`, `PROGMEM`, dead-code trim) and re-measure. Escalate to the operator only if still over after a reasonable optimization pass. Leonardo baseline ~89.5% / ~3 KB free post-v1.13; handler est. ~1–3 KB.
- **SAFE-01/02/03 (carried from Phase 77, do not re-litigate):** Host-guard refusal drop is the FINAL step, gated behind native register-bit test + host wire round-trip + Leonardo bench proof. `check_dispatch.py` full-DB VPP-safety gate stays green (SAFE-02). Any `FLAG_*` / protocol constant touched ⇒ lockstep `constants.py` ↔ `firestarter.h` parity tests green (SAFE-03).

### Claude's Discretion

- **Pinout entry strategy (A7):** Reuse `DIP24_6116` vs. create a dedicated `DIP24_X88C64` entry. Decide based on how the host wire-config actually consumes the pinout for a custom-sequenced 0x34 handler. Feasibility doc A7 (MEDIUM) notes a dedicated entry "may be cleaner"; operator left it to the planner. Only relevant on the handler-write branch.
- Exact handler file/header layout, the `0x34` constant naming, and Tier-1 test scaffold shape — planner's call, consistent with the `eeprom_28c` / `test_val_flash4` patterns.

### Deferred Ideas (OUT OF SCOPE)

None — discussion stayed within phase scope. FUT-01 = X88C64 graduation pending ALE unblock and/or physical chip+adapter, tracked in REQUIREMENTS.md; the AT28C04 DIP24→DIP32 adapter build is Phase 80.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| XIC-01 | ALE-routing question resolved before any handler code — identify a control path or document as PCB-blocked + FUT-01 | ALE trace findings §ALE-Routing Trace below; PCB-blocked verdict confirmed from source |
| XIC-02 | `configure_x88c64` handler implements 0x34 (ALE/WR/RD, page write ≤32 B, I/O6 toggle-bit polling), registered before `protocol != 0` guard | Only on handler-write branch (ALE feasible); dispatch insertion point documented §Dispatch Insertion Point |
| XIC-03 | Leonardo flash ≤ ~90% measured and recorded | Current baseline 89.5% / 3018 B free; handler-write branch analysis §Flash Budget |
| XIC-04 | X88C64P graduates to `supported`; N≥5 SHA-match on Leonardo | Hardware-blocked (D-04 — no chip); classified as deferred-until-hardware §Validation Architecture |
</phase_requirements>

---

## Summary

Phase 78 has two completely distinct branches determined by the outcome of the ALE-routing trace (XIC-01):

**Branch A — Deferral (expected outcome):** The RURP control register is 8 bits wide and fully allocated across both shield-revision layouts (`CTRL_*` bits 0x01–0x80 in the 8-bit layout; 0x01–0x100 in the `HARDWARE_REVISION` layout). The `0x100` bit exists only in the `HARDWARE_REVISION` wide layout but requires a 9-bit-wide register, which the 74HC573 strobe architecture cannot provide via a new control bit without PCB changes. No existing control line is provably idle during an X88C64 write window. The phase closes with X88C64 documented-deferred (FUT-01), a future-unblock spec, and zero handler code.

**Branch B — Handler write (only if trace finds a free/zero-risk bit):** Implement `configure_x88c64` in `eeprom_x88c64.cpp`, model on `eeprom_28c.cpp` (the closest structural analog — same 5V single-supply, page-write, toggle-bit-poll architecture), register the 0x34 dispatch arm before the generic `protocol != 0 → configure_not_implemented` guard in `memory.cpp` (insertion after line 110, before line 116), bank a Tier-1 native recording-stub test (SC#2, no hardware), and measure the Leonardo flash gate (SC#3). X88C64 stays refused at the host until physical hardware arrives (D-04/D-05).

**Primary recommendation:** Plan the deferral branch first (Plan 1 = ALE trace, deliverable = verdict + FUT-01 update). If the trace verdict is PCB-blocked (likely), the phase closes at Plan 1. Only if the trace finds a clean free bit does Plan 2 (handler write) activate.

---

## ALE-Routing Trace: A6 Verdict

### CTRL_* Bit Map — Complete Allocation Status

[VERIFIED: firestarter/include/rurp_pinout.h lines 71–97]

**8-bit layout (no `HARDWARE_REVISION` define):**

| Bit | Name | Allocated to | Notes |
|-----|------|-------------|-------|
| 0x01 | `CTRL_VPP_VPE_DROP_ENABLE` / `CTRL_ADDRESS_LINE_16` | Dual-alias: VPE drop enable AND address line 16 | Active during EPROM/flash VPP operations AND during 16-bit+ addressing |
| 0x02 | `CTRL_VPP_A9_ENABLE` | A9 VPP boost (chip ID reads) | Active during chip ID detection |
| 0x04 | `CTRL_VPE_ENABLE` | VPE direct path | Active during EPROM programming |
| 0x08 | `CTRL_VPP_P1_ENABLE` | VPP to socket pin 1 (Intel flash) | Active during Intel flash writes |
| 0x10 | `CTRL_ADDRESS_LINE_17` | Address bit 17 | Active on all 17-bit+ address chips |
| 0x20 | `CTRL_ADDRESS_LINE_18` | Address bit 18 | Active on all 18-bit address chips |
| 0x40 | `CTRL_READ_WRITE` | Read/write direction control | Active on every bus access |
| 0x80 | `CTRL_VPP_REGULATOR_ENABLE` | VPP boost regulator on/off | Active during VPP operations |

**HARDWARE_REVISION wide layout (all current production builds use `-D HARDWARE_REVISION`):**

[VERIFIED: firestarter/include/rurp_pinout.h lines 85–97; platformio.ini line 23]

| Bit | Name | Allocated to |
|-----|------|-------------|
| 0x01 | `CTRL_ADDRESS_LINE_16` | Address bit 16 (separated from VPE_DROP) |
| 0x02 | `CTRL_VPP_A9_ENABLE` | A9 VPP boost |
| 0x04 | `CTRL_VPE_ENABLE` | VPE direct path |
| 0x08 | `CTRL_VPP_P1_ENABLE` | VPP to pin 1 |
| 0x10 | `CTRL_ADDRESS_LINE_17` | Address bit 17 |
| 0x20 | `CTRL_ADDRESS_LINE_18` | Address bit 18 |
| 0x40 | `CTRL_READ_WRITE` | R/W direction |
| 0x80 | `CTRL_VPP_REGULATOR_ENABLE` | VPP regulator |
| 0x100 | `CTRL_VPP_VPE_DROP_ENABLE` | VPE-to-VPP drop (relocated from 0x01 to free ADDRESS_LINE_16) |

The `CTRL_ADDRESS_LINE_13 = 0x20` comment at line 99 is annotated "reserved — no current call-site" but overlaps with `CTRL_ADDRESS_LINE_18` at the same 0x20 bit — this is a documentation artifact, not a free bit.

### 74HC573 Strobe Architecture — Free Strobe Analysis

[VERIFIED: firestarter/include/rurp_shield.h lines 53–57; firestarter/include/rurp_register_utils.h lines 24–88]

The RURP uses three 74HC573 transparent D-latches, each with a dedicated strobe line:

| Register | Strobe constant | 74HC573 function |
|----------|-----------------|------------------|
| `LEAST_SIGNIFICANT_BYTE` (0x01) | `rurp_set_control_pin(reg, 1)` | LSB address latch |
| `MOST_SIGNIFICANT_BYTE` (0x02) | `rurp_set_control_pin(reg, 1)` | MSB address latch |
| `OUTPUT_ENABLE` (0x04) | n/a | Chip OE |
| `CONTROL_REGISTER` (0x08) | `rurp_set_control_pin(reg, 1)` | Control register latch |
| `CHIP_ENABLE` (0x20) | n/a | Chip CE |

`rurp_internal_write_to_register` (lines 63–88) writes to a 74HC573 by: (1) calling `rurp_write_data_buffer(data)` to put data on the shared 8-bit data bus, then (2) pulsing `rurp_set_control_pin(reg, 1)` HIGH then LOW to strobe the latch. This is a shared-bus architecture — only one latch can be strobed at a time. There is no "free" strobe for an ALE signal without PCB changes.

### A6 Verdict: PCB-BLOCKED

[VERIFIED from source trace above]

**Concrete evidence:**
1. Both 8-bit and wide HARDWARE_REVISION control register layouts are fully allocated — every bit position 0x01 through 0x80 is assigned a named, actively-used CTRL_* function.
2. The `0x100` bit exists in the wide layout but represents a 9-bit register. The 74HC573 CONTROL latch is 8 bits wide; the ATmega does not expose a 9-bit I/O port. Adding a `0x100` bit would require a second control register latch (PCB change: new 74HC573 + strobe line).
3. The 74HC573 strobe architecture has no unconnected strobe pins available for ALE without modifying the PCB.
4. No existing control line is provably idle during the X88C64 write window: `CTRL_READ_WRITE` (0x40) is toggled on every bus access; the VPP bits are used on other chip families but not X88C64; the ADDRESS_LINE bits drive actual address pins used even on DIP24 chips.

**Zero-risk reuse analysis (per D-02):** There is no existing control line that could be safely repurposed for ALE on an X88C64 write without risk of hardware side effects on other chip families sharing the same board. `CTRL_VPP_REGULATOR_ENABLE` could technically be toggled for a chip that uses no VPP — but pulsing it during an X88C64 write would briefly enable the boost regulator, producing an undamped VPP spike at the socket (a chip-damage path).

**FUT-01 future-unblock spec (D-03):**
A future milestone implementing X88C64 support needs ONE of:
- A new shield revision (≥ Rev 2.4) adding a 9th control bit via a second 74HC573 control latch and a dedicated Arduino GPIO strobe line for ALE.
- A dedicated Arduino GPIO pin routed directly to the X88C64 ALE pin through the socket (would require knowing which Arduino GPIO maps to a DIP32 socket pin not already occupied — needs schematic review of the Leonardo/Uno pin assignment vs. RURP socket wiring).
- A creative use of the `OUTPUT_ENABLE` or `CHIP_ENABLE` timing window as a pseudo-ALE (not recommended — this is speculative multiplexing that D-02 explicitly prohibits without clear idle-window proof).

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| ALE-routing trace (XIC-01 verdict) | Firmware / research | — | Entirely in rurp_pinout.h / rurp_shield.h — no host involvement |
| 0x34 dispatch registration | Firmware (memory.cpp) | — | Protocol dispatch is firmware-side |
| X88C64 write sequence (ALE/WR/RD, page, poll) | Firmware (new eeprom_x88c64.cpp) | — | Hardware bus sequencing |
| 0x34 constant in KNOWN_PROTOCOLS | Host (build_db.py) | — | Already present as protocol-not-implemented; no change needed until graduation |
| Host-guard refusal (chip_resolver.py) | Host | — | Currently active; MUST NOT be removed this phase (D-04/D-05) |
| Constant parity (constants.py ↔ firestarter.h) | Both (lockstep) | — | SAFE-03; only triggered if a FLAG_* or protocol constant is added |
| Flash budget gate | Firmware | Host (triggers build) | `pio run -e leonardo` measurement |
| check_dispatch.py gate | Host | — | SAFE-02; must remain green after any DB/dispatch change |
| Tier-1 native register-sequence test | Firmware (test/native/) | — | Hardware-independent; recording-stub pattern |
| Graduation (flip support_status + drop guard) | Both lockstep | — | Hardware-blocked (D-04); deferred until physical chip + adapter |

---

## Dispatch Insertion Point

[VERIFIED: firestarter/src/proms/memory.cpp lines 94–119]

Current dispatch chain order (confirmed):

```
line 74:  protocol == 0x10 → configure_flash_intel()
line 79:  protocol == 0x0D → configure_eeprom28c()
line 84:  protocol == 0x06 → configure_flash3()
line 89:  protocol in {0x05, 0x35, 0x39} → configure_flash4()
line 94:  protocol in {0x07, 0x08, 0x0B} → configure_eprom()
line 99:  protocol in {0x0E, 0x27, 0x28, 0x29} → configure_sram()
line 107: protocol in {0x11, 0x2A, 0x2B, 0x2C} → configure_not_implemented()  (named infeasible)
line 116: protocol != 0 → configure_not_implemented()   ← GENERIC FAIL-CLOSED GUARD
line 121: protocol == 0, mem_type fallbacks...
```

The `0x34` arm MUST be inserted BETWEEN line 107 and line 116 — before the generic `protocol != 0` guard. Any arm placed after line 116 is dead code.

**Exact insertion point:** After the line 111 `return;` ending the named-infeasibility arm, before the line 113 comment block `// Generic fail-closed guard`. In the handler-write branch:

```cpp
// Insert here — after line 111, before line 113
if (handle->protocol == 0x34) {
    configure_x88c64(handle);
    return;
}
```

---

## eeprom_28c.cpp — Closest Analog Analysis

[VERIFIED: firestarter/src/proms/eeprom_28c.cpp lines 1–155]

The `configure_eeprom28c` function (protocol `0x0D`) is the structural template for a future `configure_x88c64` (protocol `0x34`). Both chips are:
- 5V single-supply (no VPP regulator)
- Page-write capable (28C = 64-byte pages; X88C64 = 32-byte pages)
- Toggle-bit write-completion polling (28C = DQ7; X88C64 = I/O6)

**Reusable skeleton:**

```cpp
// eeprom_28c.cpp configure_eeprom28c structure — directly transferable
void configure_eeprom28c(firestarter_handle_t* handle) {
    handle->pulse_delay = 0;  // page write uses toggle-bit polling, not a fixed delay
    switch (handle->cmd) {
        case CMD_WRITE:
            handle->firestarter_operation_init = eeprom28c_write_init;
            handle->firestarter_operation_main = eeprom28c_write_execute;
            break;
        case CMD_BLANK_CHECK:
            handle->firestarter_operation_main = mem_util_blank_check;
            break;
    }
}
```

**Key differences X88C64 vs 28C:**

| Aspect | AT28C (0x0D) | X88C64 (0x34) |
|--------|-------------|---------------|
| Address bus | Dedicated A0–A12 | A0–A7 multiplexed on A/D pins (ALE-latched), A8–A12 dedicated |
| Write strobe | /WE pulse with data pre-set | ALE (HIGH→LOW) to latch address, then /WR strobe |
| Page size | 64 bytes | 32 bytes |
| Toggle bit | DQ7 (bit 7, standard) | I/O6 (bit 6, non-standard) — `eeprom28c_wait_for_write` checks `observed == expected`; x88c64 version must check `(observed ^ prev_observed) & 0x40` |
| Init sequence | 6-write SDP disable sequence | None (no SDP on X88C64) |
| WC pin (pin 5) | N/A | Write Control — active LOW enables writes; must be asserted LOW during write cycle |

**`eeprom28c_wait_for_write` pattern (lines 135–155):**

The 28C uses `observed == expected` to detect write completion (DQ7 returns the actual data when write is done). The X88C64 uses I/O6 TOGGLE — successive reads return alternating values while the internal write cycle is active; when the cycle completes, I/O6 stops toggling. The wait function must be re-implemented to read twice and compare `(read1 ^ read2) & 0x40 == 0` for stable I/O6.

**Shareable via D-06:** On the handler-write branch, the page-boundary logic (`(address + 1) % PAGE_SIZE == 0 || last_byte`) from `eeprom28c_write_execute` is directly reusable for the 32-byte X88C64 pages (change PAGE_SIZE to 32 in the X88C64 file). There are no true shared C functions to call (the toggle-bit logic diverges too much to share the wait function), but the structural pattern reduces implementation risk.

---

## Tier-1 Native Recording-Stub Test Pattern (SC#2)

[VERIFIED: firestarter/test/native/avr/test_val_flash4/ — all files read]

### Recording API

Activated by defining `HOST_STUBS_RECORD_BUS` before including `host_stubs_common.inc`:

```cpp
// host_stubs.cpp for new test suite
#define HOST_STUBS_RECORD_BUS
#include "../_shared/host_stubs_common.inc"
```

Available recording functions (declared in `_shared/host_stubs_common.inc` lines 64–75):

```cpp
extern "C" void    clear_bus_recording();       // reset buffer to 0 entries
extern "C" int     bus_recording_count();        // number of rurp_write_to_register calls recorded
extern "C" uint8_t recorded_reg(int i);          // register type for call i
extern "C" uint8_t recorded_data(int i);         // data value for call i (truncated to uint8_t)
```

The recording buffer is 256 entries (`HOST_STUBS_MAX_RECORDING`). The `rurp_write_to_register` stub records every call as `{reg, (uint8_t)data}`.

### What a configure_x88c64 Tier-1 Test Can Assert

**Configure-phase assertions (no operation-init call — configure_memory only):**

For the 0x34 dispatch arm (handler-write branch), a `test_val_x88c64` suite analogous to `test_val_flash4` should assert:

1. `configure_memory(&h)` with `h.protocol = 0x34` does NOT set `RESPONSE_CODE_ERROR` (dispatch test — follows `test_configure_memory.cpp` pattern).
2. No VPP-enable bits appear in any `CONTROL_REGISTER` write during the configure phase:
   - `CTRL_VPP_REGULATOR_ENABLE` (0x80) must never appear set.
   - `CTRL_VPP_P1_ENABLE` (0x08) must never appear set.
   - (Same as `assert_no_vpp_in_recording` in `test_val_flash4.cpp` lines 75–85.)

**Operation-phase assertion (call `firestarter_operation_init` + sequence write):**

For a future `configure_x88c64` handler, a recording-stub test for the write sequence can verify the register-write ORDER:

1. After `configure_memory(CMD_WRITE)`, call `h.firestarter_operation_init(&h)` if non-NULL (for X88C64 there is no SDP unlock so init may be simpler than 28C).
2. `clear_bus_recording()` after init.
3. Fill `h.data_buffer` with test data, set `h.data_size = 1`, `h.address = 0`.
4. Call `h.firestarter_operation_main(&h)`.
5. Assert the recorded sequence contains the expected ALE/WR strobes (LSB/MSB/CONTROL writes for address phase, then data bus write, then strobe for write cycle).

**Important limitation:** `recorded_data` is truncated to `uint8_t` (see `host_stubs_common.inc` line 72: `data = (uint8_t)data`). The `CTRL_VPP_VPE_DROP_ENABLE` value `0x100` under `HARDWARE_REVISION` does NOT fit in the uint8_t recording buffer. The existing `test_val_flash4` handles this by only checking the 8-bit-fit VPP bits (lines 73–85: comment explicitly notes this). The X88C64 test should follow the same approach.

### Test Suite Layout

A new suite at `test/native/avr/test_val_x88c64/` following the same layout as `test_val_flash4/`:
- `test_val_x88c64.cpp` — Unity RUN_TEST cases
- `host_stubs.cpp` — defines `HOST_STUBS_RECORD_BUS` then includes `../_shared/host_stubs_common.inc`

The `[env:native]` PlatformIO config discovers new test directories automatically — no `platformio.ini` changes needed.

---

## Flash Budget

[VERIFIED: `pio run -e leonardo` output — 2026-06-22]

```
Flash: [========= ]  89.5% (used 25654 bytes from 28672 bytes)
RAM:   [========  ]  78.1% (used 1999 bytes from 2560 bytes)
```

**Free flash: 3018 bytes (28672 - 25654). Free RAM: 561 bytes.**

The SC#3 gate is `pio run -e leonardo` ≤ ~90%, which equals ≤ 25805 bytes (90% of 28672). This means the X88C64 handler budget is **≤ 151 bytes** at exactly 90%, or about 3 KB if the operator accepts a modest overage and uses D-06 optimization.

**Realistic handler size estimate:** An `eeprom_x88c64.cpp` with configure function + write_init (simpler than 28C — no SDP unlock) + write_execute (page loop, toggle-bit wait) will be approximately 500–1500 bytes depending on implementation style and whether helpers can be shared with `eeprom_28c.cpp`.

**D-06 optimization levers (in order of impact):**
1. **Share `memory_utils.h` helpers** — `mem_util_set_address` is already called by all handlers; no duplication.
2. **Share the page-boundary calculation** — if extracted from `eeprom28c_write_execute` into a shared `flash_utils.h` helper, saves ~50 bytes.
3. **PROGMEM string savings** — any new error strings (e.g., `MSG_ERR_EEPROM_TIMEOUT` equivalent) can be placed in PROGMEM (already the pattern for all existing LOG_*_MSG strings in `logging_id.h`).
4. **No chip-ID check** — X88C64 has `chip_id_check: false` in the DB entry (verified above), so no 12V A9 VPP chip-ID routine needed; this saves ~100 bytes vs. `eeprom28c_check_chip_id`.

**Contingency:** If the handler pushes over 90%, investigate dead-code trim in adjacent handlers (unresolved `configure_not_implemented` variants) before escalating to the operator.

---

## X88C64 Write Protocol — Mapped to Firmware Sequencing

[VERIFIED: X88C64-FEASIBILITY.md §3]

The full write cycle sequence the handler must implement (handler-write branch only):

```
Phase 1: Address latch
  1. Assert /CE LOW (rurp_chip_enable analog)
  2. Set upper address A8–A12 on dedicated address pins (standard RURP address latch, MSB strobe)
  3. Place lower address A0–A7 on A/D0–A/D7 (same pins that will carry data next)
  4. ALE HIGH (set CTRL_ALE bit — requires the free bit that A6 must find)
  5. ALE LOW — address is latched on the falling edge

Phase 2: Data write
  6. Place data D0–D7 on A/D0–A/D7 (overwrite the address bits)
  7. /WR LOW — data captured
  8. /WR HIGH — rising edge latches data into page buffer

Phase 3: Repeat for up to 32 bytes (page boundary)
  Repeat phases 1–2 for each byte in the page, incrementing address.

Phase 4: Write cycle trigger
  The internal write cycle begins automatically after the last /WR HIGH in a page.
  WC must remain LOW throughout.

Phase 5: Toggle-bit poll (I/O6)
  Read the chip via /RD strobe; observe I/O6 (bit 6 of data).
  While internal write is active: successive reads return alternating I/O6 values.
  When stable (two consecutive reads return same I/O6): write cycle complete.
  Timeout after ~2000 * 10µs = 20 ms (same as eeprom28c_wait_for_write ceiling).
```

**WC pin mapping challenge:** The X88C64 has a WC (Write Control) pin at DIP pin 5. In `DIP24_6116` pinout, pin 5 is mapped as `rw-pin` in the pins dict (verified above: `"rw-pin": [21]` — that is for pin 21, not pin 5). The DIP24_6116 pinout was designed for 6116-class SRAM, not for X88C64. A dedicated `DIP24_X88C64` pinout entry that correctly maps pin 5 → WC control and pins 7–15, 13–17 → A/D bus would be cleaner and is the recommended approach for A7 (planner's discretion).

---

## Pinout Strategy: DIP24_6116 vs DIP24_X88C64 (A7 Research)

[VERIFIED: firestarter_app/firestarter/data/pinouts.json; firestarter_app/firestarter/data/chip_database.json]

**Current DIP24_6116 pin mapping:**
- `vcc-pin`: [24] — matches X88C64 VCC (correct)
- `gnd-pin`: [12] — matches X88C64 VSS (correct)
- `address-bus-pins`: [8,7,6,5,4,3,2,1,23,22,19] — 11 pins, correct count for A0–A10 on 6116 SRAM. For X88C64, pins 7–15 (A/D0–A/D7 multiplexed) AND pins 17,20,21,19,2 (A8–A12 dedicated) must be separated — the A/D bus is NOT a simple address bus.
- `data-bus-pins`: [9,10,11,13,14,15,16,17] — 8 data pins. X88C64 data is the SAME physical pins as A0–A7 (A/D bus) — the 6116 mapping conflates them.
- `ce-pin`: [18] — matches X88C64 /CE (correct)
- `oe-pin`: [20] — maps to X88C64 /RD... close but /RD is at pin 18 and /CE at pin 16. Mismatch.
- `rw-pin`: [21] — maps to X88C64 pin 21 = A8. Wrong — should be WC (pin 5) or /WR (pin 23).

**Conclusion for A7:** `DIP24_6116` is structurally incompatible with the X88C64 bus layout. A dedicated `DIP24_X88C64` pinout entry is the correct approach. The custom 0x34 handler will bypass most of the pin mapping for the multiplexed A/D bus (which requires firmware-level sequencing, not just static pin mapping), but the correct identification of VCC/GND/CE pins still matters for the bus_config the host sends.

**Recommended pinout key:** `DIP24_X88C64` with the following pins:
- `vcc-pin`: [24], `gnd-pin`: [12] — power supply (correct, same as 6116)
- `ce-pin`: [16] — X88C64 /CE is pin 16 (not 18 like 6116)
- `oe-pin`: [18] — X88C64 /RD is pin 18 (read strobe)
- Dedicated upper address pins (A8–A12): [21, 20, 19, 17, 2] — pins 21=A8, 20=A9, 19=A11, 17=A10, 2=A12
- Multiplexed A/D bus (lower 8 bits — address phase AND data phase): [7,8,9,10,11,13,14,15] — pins 7–15 (skipping 12=GND)
- `rw-pin` / WC: [5] — Write Control
- ALE: [22] — requires a free control bit (gated on ALE verdict)
- /WR: [23] — write strobe

---

## Standard Stack

No new third-party dependencies are introduced by this phase. All tools are already installed.

### Core (Firmware)
| Tool | Version | Purpose | Why Standard |
|------|---------|---------|--------------|
| PlatformIO | installed | Build/test/upload | Project standard |
| Unity | via PIO | Native C++ tests | Project standard for firmware unit tests |
| ArduinoFake | ^0.4.0 | Mock Serial/delay in native tests | Project standard for recording-stub tests |

### Core (Host)
| Tool | Version | Purpose | Why Standard |
|------|---------|---------|--------------|
| pytest | installed | Host Python tests | Project standard |
| ruff | installed | Linting (CI gate) | Project standard — Python 3.12 masks CI 3.9/3.11 drift trap |
| mypy | installed | Type checking | Project standard |

**Installation:** No new packages. `pip install -e '.[test]'` in `firestarter_app/` to ensure test toolchain is present.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Toggle-bit polling | Custom delay loop | Model on `eeprom28c_wait_for_write` | The 2000 * 10µs ceiling (20 ms) is proven; just change the bit mask from DQ7 to I/O6 |
| Page boundary detection | Custom math | Copy `(address + 1) % PAGE_SIZE == 0` from `eeprom28c_write_execute` | Tested pattern; only change PAGE_SIZE 64→32 |
| VPP-safety recording-stub test | Custom mock framework | `HOST_STUBS_RECORD_BUS` pattern from `test_val_flash4` | Already in tree, no new test infrastructure needed |
| Bus register write abstraction | Direct Arduino port writes | `rurp_write_to_register` + CTRL_* constants | Handles caching, HARDWARE_REVISION mapping, settling delays |
| Dispatch registration | New dispatch mechanism | Add `if (handle->protocol == 0x34)` arm in `memory.cpp` BEFORE line 116 | All handlers use this exact pattern |

---

## Common Pitfalls

### Pitfall 1: Inserting the 0x34 arm AFTER the generic `protocol != 0` guard
**What goes wrong:** The `if (handle->protocol != 0) { configure_not_implemented(handle); return; }` guard at line 116 catches the 0x34 arm before it executes — the 0x34 arm becomes dead code and 0xBB is always returned.
**Why it happens:** The comment on line 113 says "Must sit AFTER all implemented protocol cases" but a new developer might read it as "this is the last guard, my new arm goes here."
**How to avoid:** Insert BEFORE the line 113 comment block, immediately after the named-infeasibility block at line 111.
**Warning signs:** `pio test -e native -f "*test_dispatch*"` test for protocol 0x34 still shows `RESPONSE_CODE_ERROR`.

### Pitfall 2: Assuming the 0x100 `CTRL_VPP_VPE_DROP_ENABLE` bit can be toggled for ALE
**What goes wrong:** The bit only exists in the `HARDWARE_REVISION` layout and requires a 9-bit register width the 74HC573 cannot accommodate without PCB changes. Using 0x100 as an ALE toggle would silently wrap or be masked to 0x00 by the 8-bit data bus width.
**Why it happens:** `rurp_pinout.h:96` defines `CTRL_VPP_VPE_DROP_ENABLE = 0x100` which looks like an available constant.
**How to avoid:** `rurp_internal_write_to_register` calls `rurp_write_data_buffer(data)` which takes a `uint8_t` — any value > 0xFF is truncated. The 0x100 bit cannot be physically transmitted to the 74HC573.

### Pitfall 3: I/O6 toggle-bit poll — using `observed == expected` instead of two-read toggle check
**What goes wrong:** `eeprom28c_wait_for_write` uses `observed == expected` (DQ7 returns the actual programmed bit when write is done). X88C64 I/O6 TOGGLES — its value on write-complete does not match the programmed bit, it just stops toggling.
**Why it happens:** Copy-paste from the eeprom_28c template without adapting the poll logic.
**How to avoid:** For X88C64: read twice, check `(read1 ^ read2) & 0x40 == 0` for stable I/O6. Document with a comment citing the X88C64 datasheet.

### Pitfall 4: Python 3.12 masks CI (py3.9/3.11) ruff/codegen drift
**What goes wrong:** New Python code that is ruff-clean under 3.12 may contain backslash-in-f-string or other patterns that fail the CI ruff check targeting py3.9.
**Why it happens:** The devcontainer runs Python 3.12; CI targets 3.9/3.11.
**How to avoid:** After any host-side change, run `ruff check --target-version py39 .` from `firestarter_app/` before claiming CI green. [VERIFIED: memory project — reference_devcontainer_py312_masks_ci_py39.md]

### Pitfall 5: `check_dispatch.py` 0x34 gate — do NOT add 0x34 to `KNOWN_PROTOCOLS` in check_dispatch.py
**What goes wrong:** `check_dispatch.py` has its own `KNOWN_PROTOCOLS`-like set that intentionally excludes 0x34 (lines 112–116, 129). Adding 0x34 there would change gate semantics.
**Why it happens:** The build_db.py `KNOWN_PROTOCOLS` includes 0x34; a developer might "sync" check_dispatch.py to match.
**How to avoid:** Leave `check_dispatch.py` alone unless the handler-write branch changes the dispatch verdict for the chip (which requires confirming 0x34 stays non-dispatchable at the check_dispatch level until graduation).

### Pitfall 6: Removing the `resolve_chip` host-guard refusal before bench SHA-match
**What goes wrong:** X88C64P would pass through `resolve_chip` and attempt to drive an unverified firmware path. With no physical chip on hand (D-04), this is a dead-letter risk, but on any future hardware it would be a chip-damage path.
**How to avoid:** The host-guard removal is explicitly deferred to SC#4 (D-04/D-05). Keep `support_status: protocol-not-implemented` in chip_database.json unchanged through this phase.

---

## Architecture Patterns

### System Architecture Diagram

```
[Host CLI] → resolve_chip() → REFUSED (protocol-not-implemented)
                                    ↑
                           support_status gate in chip_resolver.py
                           (remains active until SC#4 — hardware-blocked)

[Firmware dispatch chain — handler-write branch only]
configure_memory()
  → protocol == 0x34   ← NEW ARM (insert before line 116)
      → configure_x88c64()
          → CMD_WRITE: write_init + write_execute
              → page loop: ALE latch phase → /WR strobe → I/O6 poll
          → CMD_BLANK_CHECK: mem_util_blank_check (shared)
```

### Recommended File Layout (handler-write branch only)

```
firestarter/
├── src/proms/
│   ├── memory.cpp              # +4 lines: if protocol==0x34 arm before line 116
│   ├── eeprom_x88c64.cpp       # NEW — configure_x88c64, write_init, write_execute, wait_for_write
│   └── ...
├── include/
│   ├── eeprom_x88c64.h         # NEW — void configure_x88c64(firestarter_handle_t*)
│   ├── memory.cpp              # #include "eeprom_x88c64.h" added
│   └── ...
└── test/native/avr/
    └── test_val_x88c64/        # NEW — recording-stub test suite
        ├── test_val_x88c64.cpp
        └── host_stubs.cpp      # #define HOST_STUBS_RECORD_BUS + include common.inc
```

### Pattern 1: Fail-Closed Protocol Dispatch

**What:** New protocol arms inserted BEFORE the generic `protocol != 0` guard in `memory.cpp`.
**When to use:** Every new protocol handler.

```cpp
// Source: firestarter/src/proms/memory.cpp lines 107–119 (verified)
// Insert new arm here — BEFORE the generic guard:
if (handle->protocol == 0x34) {
    configure_x88c64(handle);
    return;
}

// Generic fail-closed guard — do NOT insert arm after this:
if (handle->protocol != 0) {
    configure_not_implemented(handle);
    return;
}
```

### Pattern 2: Page-Write + Toggle-Bit Poll Structure

**What:** Page loop that triggers a poll at page boundaries, modeled on `eeprom_28c.cpp`.
**When to use:** Any 5V EEPROM with page-write + toggle-bit completion signaling.

```cpp
// Source: eeprom_28c.cpp:eeprom28c_write_execute pattern (lines 119–133)
// Adapt by changing PAGE_SIZE 64 → 32, and adapting wait function to I/O6 toggle
void x88c64_write_execute(firestarter_handle_t* handle) {
    for (uint32_t i = 0; i < handle->data_size; i++) {
        uint32_t address = handle->address + i;
        uint8_t data = handle->data_buffer[i];
        handle->firestarter_set_data(handle, address, data);  // must ALE-latch inside

        bool page_end = ((address + 1) % 32) == 0;
        bool last_byte = (i == handle->data_size - 1);
        if (page_end || last_byte) {
            if (!x88c64_wait_for_write(handle, address)) {
                return;
            }
        }
    }
}
```

### Pattern 3: Recording-Stub VPP-Safety Test

**What:** Verify the configure phase emits no VPP-enable control register bits.
**When to use:** Every new 5V (no-VPP) protocol handler — SC#2.

```cpp
// Source: firestarter/test/native/avr/test_val_flash4/test_val_flash4.cpp (verified)
void test_x88c64_configure_no_vpp(void) {
    firestarter_handle_t h = make_handle(0x34, CMD_WRITE);
    configure_memory(&h);
    TEST_ASSERT_NOT_EQUAL_MESSAGE(RESPONSE_CODE_ERROR, h.response_code,
        "configure_memory must not error on 0x34 CMD_WRITE");
    for (int i = 0; i < bus_recording_count(); i++) {
        if (recorded_reg(i) == CONTROL_REGISTER) {
            TEST_ASSERT_BITS_LOW_MESSAGE(
                (uint8_t)CTRL_VPP_REGULATOR_ENABLE,
                recorded_data(i),
                "configure_x88c64 must NOT set CTRL_VPP_REGULATOR_ENABLE");
            TEST_ASSERT_BITS_LOW_MESSAGE(
                (uint8_t)CTRL_VPP_P1_ENABLE,
                recorded_data(i),
                "configure_x88c64 must NOT set CTRL_VPP_P1_ENABLE");
        }
    }
}
```

### Anti-Patterns to Avoid
- **Speculative ALE multiplexing:** Do not attempt to toggle an existing busy CTRL_* bit as ALE (VPP_REGULATOR_ENABLE toggled "briefly" for a 5V chip) — this produces an undamped VPP spike.
- **Removing the host-guard before bench proof:** The `resolve_chip` refusal stays active until SC#4; even if the firmware handler is banked and tests pass, the host must refuse until the operator can bench-confirm.
- **Incrementing KNOWN_PROTOCOLS in check_dispatch.py:** That set intentionally excludes 0x34 (check_dispatch.py comment at lines 112–116 explains the logic). Sync build_db.py and check_dispatch.py only in structure, not membership.

---

## Runtime State Inventory

> This is not a rename/refactor phase — no state migration needed.

| Category | Items Found | Action Required |
|----------|-------------|-----------------|
| Stored data | None — X88C64 is protocol-not-implemented; no read/write records exist | None |
| Live service config | None | None |
| OS-registered state | None | None |
| Secrets/env vars | None | None |
| Build artifacts | `firestarter/.pio/build/leonardo/` — stale after any firmware change | `pio run -e leonardo` rebuilds automatically; no manual cleanup needed |

---

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Firmware native framework | Unity (via PlatformIO `[env:native]`) |
| Host framework | pytest |
| Firmware native run | `pio test -e native` (from `firestarter/`) |
| Firmware flash build | `pio run -e leonardo` (SC#3 gate) |
| Host test run | `pytest` (from `firestarter_app/`) |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | Hardware Needed? |
|--------|----------|-----------|-------------------|-----------------|
| XIC-01 (deferral branch) | A6 verdict recorded in X88C64-FEASIBILITY.md with trace evidence + future-unblock spec written | Documentation / trace | — | No |
| XIC-01 (handler branch) | A6 verdict: free bit found and documented | Documentation / trace | — | No |
| XIC-02 (handler branch) | 0x34 dispatch routes to configure_x88c64, not configure_not_implemented | Tier-1 native dispatch test | `pio test -e native -f "*test_dispatch*"` | No |
| XIC-02 (handler branch) | configure_x88c64 sets no VPP-enable bits in configure phase | Tier-1 native recording-stub test | `pio test -e native -f "*test_val_x88c64*"` | No |
| XIC-02 (handler branch) | configure_x88c64 write sequence emits correct ALE/WR order | Tier-1 native recording-stub test | `pio test -e native -f "*test_val_x88c64*"` | No |
| XIC-03 (handler branch) | Leonardo flash ≤ ~90% | Build measurement | `pio run -e leonardo` (check Flash % line) | No (build only) |
| XIC-04 | N≥5 write + read-back SHA-match on Leonardo | Tier-3 bench | Manual — Leonardo + X88C64P chip + DIP24→DIP32 adapter | YES — hardware-blocked |

### Sampling Rate
- **Per firmware task commit:** `pio test -e native` — all native suites
- **Per host task commit:** `pytest` from `firestarter_app/` + `ruff check --target-version py39`
- **Phase gate (deferral branch):** No firmware changes; host tests green; `check_dispatch.py` green (no change needed).
- **Phase gate (handler-write branch):** `pio test -e native` green + `pio run -e leonardo` ≤ 90% + `pytest` green + `check_dispatch.py` green.

### Hardware-Gated Validation (XIC-04)

SC#4 bench proof (N≥5 write + read-back SHA-match + negative control on Leonardo with X88C64P) is **hardware-blocked** per D-04. It requires:
1. A physical X88C64P chip.
2. A DIP24→DIP32 adapter (same adapter pattern as AT28C04/AT28C16 from Phase 80).

Record as "graduation pending hardware" in X88C64-FEASIBILITY.md on the handler-write branch. The existing `FUT-01` in REQUIREMENTS.md already covers the deferred graduation.

### Wave 0 Gaps (handler-write branch only)

- [ ] `firestarter/src/proms/eeprom_x88c64.cpp` — new file (configure + write functions)
- [ ] `firestarter/include/eeprom_x88c64.h` — new header
- [ ] `firestarter/test/native/avr/test_val_x88c64/test_val_x88c64.cpp` — new test suite
- [ ] `firestarter/test/native/avr/test_val_x88c64/host_stubs.cpp` — recording-stub activation
- [ ] `firestarter_app/firestarter/data/pinouts.json` — `DIP24_X88C64` entry (if A7 planner decision = dedicated pinout)

*(Deferral branch: "None — no code files created; only X88C64-FEASIBILITY.md updated with A6 verdict + future-unblock spec.")*

---

## Security Domain

> Phase 78 is a firmware handler addition for a single chip. Applicable ASVS categories are limited.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | No | No auth in firmware |
| V3 Session Management | No | Serial session is single-command |
| V4 Access Control | No | Not applicable |
| V5 Input Validation | Yes (VPP safety) | `check_dispatch.py` SAFE-02 gate — no chip with protocol 0x34 should dispatch to a VPP-enable handler |
| V6 Cryptography | No | Not applicable |

### Known Threat Patterns for This Phase

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Wrong-VPP handler routing (X88C64 0x34 reaching a 12V VPP handler) | Tampering / Damage | `check_dispatch.py` SAFE-02 gate; X88C64 stays `protocol-not-implemented` with host guard until graduation |
| Blind handler writing to unverified hardware | Tampering | D-04/D-05: no graduation without bench SHA-match; handler-write branch keeps chip refused at host layer |
| Control register bit pollution (ALE toggle via busy bit) | Tampering | D-02 deferral bar: any speculative bit reuse leads to FUT-01 deferral, not creative multiplexing |

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| X88C64 labeled "serial NOVRAM with STORE/RECALL" | X88C64 is parallel DIP24 5V EEPROM with 8051 multiplexed ALE/WR/RD bus | Phase 76 / v1.13 | Corrects misclassification; handler is feasible-candidate, not infeasible |
| Generic `protocol != 0` catch-all (Phase 64) | Named infeasibility arms + generic guard | Phase 64 / v1.12 | 0x34 arm must go BEFORE the generic guard |
| `CTRL_VPP_VPE_DROP_ENABLE = 0x01` (legacy) | `CTRL_VPP_VPE_DROP_ENABLE = 0x100` (HARDWARE_REVISION wide layout) | Phase 33 / v1.7 | The `0x100` value cannot be transmitted via an 8-bit data bus — this is the proof that no 9th control bit is available without PCB changes |

**Deprecated / outdated:**
- `STORE/RECALL` on X88C64P: confirmed absent (X88C64-FEASIBILITY.md §3, HIGH confidence). Those operations belong to X2210/X2212 NOVRAM family.
- `DIP24_6116` as X88C64 pinout: the pin mapping is structurally incompatible (mismatched /CE, /RD, WC pins); a dedicated `DIP24_X88C64` entry is needed on the handler-write branch.

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | X88C64 write cycle time is ~100 µs (EEPROM-class timing) | Write Protocol | If much longer (> 10 ms per byte), the toggle-bit poll ceiling of 20 ms may need raising; does not affect firmware correctness structurally |
| A2 | A dedicated `DIP24_X88C64` pinout entry (rather than DIP24_6116 reuse) is the correct A7 approach | Pinout Strategy | If DIP24_6116 happens to be an acceptable bus-config approximation for a custom 0x34 handler, a dedicated pinout is still more correct but not strictly required for correctness |

**If this table has only two entries:** All other claims in this research were verified directly from source code. The A6 verdict (PCB-blocked) is VERIFIED from source.

---

## Open Questions

1. **A7 — DIP24_X88C64 pinout: planner must decide**
   - What we know: DIP24_6116 mismatches X88C64 on /CE (pin 16 vs 18), /RD (pin 18 vs 20), WC (pin 5 unrepresented), and conflates A/D bus pins with separate address/data pins.
   - What's unclear: Whether the host `convert_to_programmer` function actually uses the pinout fields in a way that matters for a custom-sequenced 0x34 handler (the handler may bypass the standard bus-config path entirely for the multiplexed A/D phase).
   - Recommendation: Create `DIP24_X88C64` as a dedicated pinout entry on the handler-write branch. The cost is small (one JSON object in pinouts.json) and correctness is higher.

2. **ALE GPIO fallback option (for FUT-01 spec only)**
   - What we know: The 74HC573 strobe architecture has no free strobe for ALE; the control register is fully allocated.
   - What's unclear: Whether the Leonardo board (ATmega32u4) has any GPIO pins routed to the RURP shield board but currently unused as a direct-drive GPIO for ALE (bypassing the 74HC573 shift entirely).
   - Recommendation: For the FUT-01 future-unblock spec (D-03), document the Leonardo GPIO pin map vs. RURP socket wiring as a TODO for the future milestone — this is out of scope for Phase 78's software trace.

---

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| PlatformIO | Firmware build + native tests | ✓ | installed | — |
| Python 3.x | Host tests + ruff | ✓ | 3.12 (devcontainer) | — |
| Leonardo board | SC#3 flash gate (build only) | ✓ | build-only; no upload needed for flash% | — |
| Physical X88C64P chip | SC#4 graduation bench | ✗ | — | Deferred (D-04/FUT-01) |
| DIP24→DIP32 adapter | SC#4 graduation bench | ✗ | — | Deferred (D-04/Phase 80 pattern) |

**Missing dependencies with no fallback:**
- Physical X88C64P chip + DIP24→DIP32 adapter — block SC#4 graduation; all other SCs are software-provable.

---

## Sources

### Primary (HIGH confidence — verified from source code)
- `firestarter/include/rurp_pinout.h` lines 71–129 — CTRL_* bit map; A6 verdict (PCB-blocked, fully allocated 8-bit register, 0x100 bit requires 9-bit width) [VERIFIED: codebase]
- `firestarter/include/rurp_register_utils.h` lines 63–88 — 74HC573 strobe architecture; no free strobe for ALE [VERIFIED: codebase]
- `firestarter/include/rurp_shield.h` lines 53–57 — strobe constants (LEAST_SIGNIFICANT_BYTE, MOST_SIGNIFICANT_BYTE, CONTROL_REGISTER) [VERIFIED: codebase]
- `firestarter/src/proms/memory.cpp` lines 74–119 — dispatch insertion point confirmed: 0x34 arm goes after line 111, before line 116 [VERIFIED: codebase]
- `firestarter/src/proms/eeprom_28c.cpp` lines 1–155 — closest analog; full write_init/write_execute/wait_for_write skeleton [VERIFIED: codebase]
- `firestarter/include/firestarter.h` lines 58–68 — FLAG_* constants; no 0x34 protocol constant today [VERIFIED: codebase]
- `firestarter/test/native/avr/test_val_flash4/` + `_shared/host_stubs_common.inc` — recording-stub API (clear_bus_recording, bus_recording_count, recorded_reg, recorded_data) [VERIFIED: codebase]
- `firestarter/platformio.ini` lines 57–67 — `[env:leonardo]` confirms DATA_BUFFER_SIZE=1024; `pio run -e leonardo` is SC#3 gate [VERIFIED: codebase]
- `pio run -e leonardo` output (2026-06-22) — Flash: 89.5% / 25654 of 28672 bytes; 3018 free [VERIFIED: live build]
- `firestarter_app/firestarter/data/chip_database.json` — X88C64P entry: support_status=protocol-not-implemented, algorithm=52 (0x34), pinout=DIP24_6116 [VERIFIED: codebase]
- `firestarter_app/firestarter/data/pinouts.json` — DIP24_6116 pin layout (incompatible with X88C64 signal mapping) [VERIFIED: codebase]
- `firestarter_app/tools/build_db.py` lines 131–148, 361–370 — KNOWN_PROTOCOLS includes 0x34; 0x34 branch sets protocol-not-implemented [VERIFIED: codebase]
- `firestarter_app/tools/check_dispatch.py` lines 112–129 — 0x34 intentionally absent from check_dispatch's KNOWN_PROTOCOLS equivalent [VERIFIED: codebase]
- `firestarter_app/firestarter/chip_resolver.py` lines 54–57 — host-guard refusal for protocol-not-implemented; confirmed active and must NOT be removed this phase [VERIFIED: codebase]
- `.planning/X88C64-FEASIBILITY.md` — canonical verdict: §2 8051 multiplexed bus + DIP24 pin table; §3 write protocol (ALE-latch → /WR strobe, page write ≤32 B, I/O6 toggle-bit polling, STORE/RECALL correction); §6 Assumptions A4–A7 [VERIFIED: planning artifact]

### Secondary (MEDIUM confidence — planning documents)
- `.planning/phases/78-x88c64-0x34-firmware-handler/78-CONTEXT.md` — locked decisions D-01–D-06, canonical refs, code context
- `.planning/REQUIREMENTS.md` — XIC-01/02/03/04; FUT-01 deferral; SAFE-01/02/03
- `.planning/STATE.md` — v1.14 milestone framing; flash budget; standing bench precondition

---

## Metadata

**Confidence breakdown:**
- ALE-routing verdict (A6): HIGH — traced directly from rurp_pinout.h, rurp_register_utils.h, rurp_shield.h source; all 8 CTRL_* bits accounted for; 0x100 bit confirmed non-transmissible via 8-bit data bus
- Dispatch insertion point: HIGH — verified line-by-line in memory.cpp
- eeprom_28c analog mapping: HIGH — verified from source with line citations
- Recording-stub test API: HIGH — verified from test_val_flash4 + host_stubs_common.inc
- Flash budget: HIGH — measured live (`pio run -e leonardo` 2026-06-22)
- Pinout incompatibility (DIP24_6116 vs X88C64): HIGH — verified pin-by-pin from chip_database.json + X88C64-FEASIBILITY.md §2 pin table
- Write protocol timing (tWC): LOW (A1) — "EEPROM-class timing" is operationally sufficient; exact value from datasheet not re-fetched this session

**Research date:** 2026-06-22
**Valid until:** 2026-07-22 (firmware source stable; planning context fresh)
