# Hardware Signal-Flow Reference: Firestarter RURP Shield

**Document Purpose:** Comprehensive tracing of the firmware's control-register bit layout, VPP routing, and per-protocol handler signal flows for validating safety claims about 12V VPP placement on socket pins.

**Analysis Date:** 2026-05-13 (initial) / 2026-05-13 (schematic-verified update)
**Scope:** Firestarter firmware v1.0+, hardware Rev 2.3 (upstream `github.com/AndersBNielsen/Relatively-Universal-ROM-Programmer` `hardware/RelativelyUniversalROMProgrammerRev2.3.pdf`)
**Key Question:** For a given pinout (e.g., DIP24_2716) and protocol handler (e.g., configure_eprom), does the firmware correctly route VPP to the intended socket pin without damaging 5V-only chips?

---

## SCHEMATIC ADDENDUM (2026-05-13)

This document was originally produced from firmware-source trace alone. A subsequent read of the upstream Rev 2.3 PCB schematic produced the following **corrections and verifications**:

**Corrections:**
- The shield uses **three 74HC573 transparent latches** (U2/U3/U4 with separate LE strobes — `RLSBLE`, `RMSBLE`, `CTRL_LE`), NOT 74HC595 shift registers. All three latches share Arduino PORTD as the D-input bus; the LE strobe selects which latch captures. This is faster and simpler than shift-register chains.
- The HV regulator is a **MIC2288** boost converter (U1) with feedback set by trimmer RV1 (50kΩ) + R8/R35/R36/R37. Verified per-schematic math: `VPE-Max ≈ 22.53V` (VPE_TO_VPP de-asserted), `VPP ≈ 12.05V` (VPE_TO_VPP asserted via Q3 switching R28 into the feedback network), `VPE-Min ≈ 9.45V`.
- The MIC2288's `~SHDN` (active-low shutdown) is gated by `~REG_DISABLE` via bodge point JP9. The CONTROL_REGISTER bit `REGULATOR (0x80)` enables the boost supply when asserted (the firmware-level meaning is "regulator on"; the hardware-level signal is its inverse).

**Verifications (schematic-confirmed):**
- The **ROM socket (U5)** is explicitly labeled "28/32 pin ROM" — there is NO dedicated 24-pin section.
- **JP4 (`P1_VPP_JMP`)** is a 3-pin selector jumper that gates the BJT-driven HV path to socket pin 1 via D33 (1N5819 protection diode). Closed = 28-pin VPP enabled. Upstream warns: open this jumper before installing 32-pin chips (their pin 1 = A18).
- **JP5 (`A19_CUT`)**: cuts the A18-line backfeed path so pin 1 can carry VPP without driving the U3 latch output. (The "A19" in the silkscreen name is a misnomer — there's no A19 on a 32-pin DIP.)
- **HV-reachable socket pins** (from schematic — these are the only pins with a HV BJT cascade):
  - **Pin 1** (via `P1_VPP_ENABLE` → JP4 → D33)
  - **Pin 26 / A9** (via `A9_VPP_ENABLE` → BJT cascade → D34) — for chip-ID reads
  - **Pin 31 / PGM** (via `VPE_ENABLE` → BJT cascade → D11) — for 28-pin EPROM program pulse
- All other socket pins (5V address lines, data lines, GND, VCC, CE, OE) are driven by 74HC573 latch outputs at 5V — **no HV path exists to those pins**.

**24-pin EPROM support (DIP24_2716, DIP24_2732 family — ~53+16 chips in DB):**

> **CORRECTION (2026-05-13):** This section previously stated "24-pin EPROM writes are structurally unsupported on Rev 2.x." That framing was overstated. The corrected picture is below; full investigation in [04-HW-24PIN-INVESTIGATION.md](04-HW-24PIN-INVESTIGATION.md).

Per [database.py:85-87](firestarter_app/firestarter/database.py#L85-L87), a 24-pin chip is inserted at **socket positions 5–28** (chip pin 1 at socket pin 5, chip pin 24 at socket pin 28 = VCC). With that alignment:

- 2716's VPP pin (chip pin 21) → socket pin **25** → shield's A11 latch output (5V CMOS).
- 2732's VPP pin (chip pin 20) shares with OE → socket pin **24** → shield's `~ROM_OE` signal (5V CMOS).

**Neither socket pin has a built-in HV BJT cascade on Rev 2.3.** Upstream's design has *always* required the operator to supply the HV path for 24-pin chips:

- **Rev 1.x:** explicit manual jumpers (operator-soldered).
- **Rev 2.0 / 2.1 / 2.3:** operator-soldered bodge wire from socket pin **1** → socket pin **25** (2716) or socket pin **24** (2732).
- **Rev 2.2:** built-in alternative JP4 position ("red") that does the same routing via a board-supplied jumper.

With either the bodge wire or the Rev 2.2 red jumper in place, the HV cascade at socket pin 1 (`P1_VPP_ENABLE` → JP4 → D33) feeds the 24-pin chip's VPP pin through the operator-supplied path. This is why **upstream Anders firmware unconditionally asserts `P1_VPP_ENABLE` for `romPinCount == 24`** — it relies on the operator's external routing to complete the HV path.

**Firestarter's current firmware doesn't drive this correctly.** The redirect in `eprom.cpp:268-274` (VPE_ENABLE → P1_VPP_ENABLE) is gated by `using_p1_as_vpp()` in `memory_utils.h:24-27`, which returns false for stock 24-pin pinouts (`vpp_line = 11`, not the magic 0x0F). So Firestarter asserts `VPE_ENABLE` (→ socket pin 31) instead of `P1_VPP_ENABLE` (→ socket pin 1 → operator wire → chip VPP). The result is silent write failure even on a board that's mechanically set up for 24-pin programming.

**Fix path:** extend `using_p1_as_vpp()` to return true when `handle->pins == 24`, matching upstream Anders firmware behavior. Tracked as follow_up [`24pin-eprom-firmware-vpp-path`](04-HW-VALIDATION.md) (severity MEDIUM, OPEN).

Reads of 24-pin EPROMs are unaffected — the 5V address bus is sufficient for read-mode access regardless of HV routing.

---

## ORIGINAL FIRMWARE-TRACE ANALYSIS (pre-schematic)

---

## Section 1: Bus Topology — GPIO to Socket Pin

### 1.1 Arduino Pin Mapping (UNO & Leonardo)

The RURP shield uses **three 8-bit parallel registers** (shift registers via 74HC595 logic):
1. **LEAST_SIGNIFICANT_BYTE (0x01)** — address bits [7:0]
2. **MOST_SIGNIFICANT_BYTE (0x02)** — address bits [15:8]
3. **CONTROL_REGISTER (0x08)** — control bits (VPP enable, address lines 16–18, RW, etc.)

**Data path:** Arduino GPIO → PORTD/PORTB/PORTC (depends on board) → shift register latches → socket pins via address/control muxing.

**File:** `/workspaces/firestarter_prom/firestarter/src/boards/uno_rurp_shield.cpp:31–92`
- **Address/data bus (PORTD, bits 0–7):** wired to data input of shift registers
- **Register select (PORTB, bits 0–3):** strobe lines for LEAST_SIG_BYTE, MOST_SIG_BYTE, OUTPUT_ENABLE, CONTROL_REGISTER
- **Chip enable (PORTB, bit 5):** gates the socket CE pin
- **Output enable (PORTB, bit 5):** gates the socket OE pin

**Register write sequence** (`rurp_register_utils.h:23–59`):
```c
rurp_write_to_register(uint8_t reg, rurp_register_t data) {
    // ... caching logic ...
    rurp_internal_write_to_register(reg, data);  // line 53
    if (settle) delayMicroseconds(4);            // line 57
}

// Inside uno_rurp_shield.cpp:
rurp_internal_write_to_register(uint8_t reg, rurp_register_t data) {
    rurp_write_data_buffer(data);    // PORTD = data (line 100)
    rurp_set_control_pin(reg, 1);    // strobe HIGH (line 64)
    delayMicroseconds(1);            // brief pulse (line 66)
    rurp_set_control_pin(reg, 0);    // strobe LOW (line 68)
}
```

**Socket pin routing:** The shift registers latch the 8-bit address byte when the register-select strobe (e.g., CONTROL_REGISTER) pulses. The next register write to a different strobe line drives that byte to the next shift register in the chain. Pin assignments are **statically wired**; there is no dynamic muxing of VPP to arbitrary pins at runtime.

---

### 1.2 Static Wiring: DIP Socket to Bus Lines

From `firestarter_app/firestarter/database.py:68–133`, the **pin_conversions** dict maps physical DIP pin numbers to RURP bus line indices:

**DIP24 example (e.g., 2716):**
```python
24: {
    1:  7,     # A7
    2:  6,     # A6
    ...
    21: 11,    # <-- VPP (on DIP24_2716 per pinouts.json)
    ...
    24: 13,    # VCC (tied HIGH on socket)
}
```

**DIP28 example (e.g., 27256):**
```python
28: {
    1:  15,    # A15 (or VPP, depending on pinout — see pinouts.json)
    ...
    27: 14,    # A14
    28: 13,    # VCC
}
```

**Loading in firmware:** The Python host translates the pinout JSON field (e.g., `"vpp-pin": [21]` from `DIP24_2716`) into a bus-line index via pin_conversions, then passes it in the JSON `bus-config` as the `vpp-pin` field. The firmware receives this in `handle->bus_config.vpp_line`.

**File:** `/workspaces/firestarter_prom/firestarter_app/firestarter/database.py:284–295`
```python
if pin_func in pin_map_data:
    pin_val = pin_map_data[pin_func]
    pin_to_check = pin_val[0] if isinstance(pin_val, list) else pin_val
    if pin_to_check in pin_conversions.get(pins, {}):
        resolved = pin_conversions[pins][pin_to_check]
        if pin_func == "vpp-pin" and resolved in (ROM_CE, ROM_OE):
            continue  # Skip if VPP shares pin with CE or OE
        map_config[pin_func] = resolved  # e.g., vpp_line = 11
```

---

## Section 2: Control Register Bit Layout

### 2.1 Bit Definitions (No Hardware Revision)

From `rurp_shield.h:25–33` (default build, `#ifndef HARDWARE_REVISION`):

| Bit | Name | Mask | Physical Function |
|-----|------|------|-------------------|
| 0 | `VPE_TO_VPP` | 0x01 | Drop VPE voltage through resistor divider to produce VPP (~13V) for EPROM_STD/EPROM_QUICK |
| 1 | `A9_VPP_ENABLE` | 0x02 | Route 12–13V to address line A9 (for chip-ID read on UV-EPROMs) |
| 2 | `VPE_ENABLE` | 0x04 | Apply direct VPE voltage to PGM pin (for 24-pin EPROM erase) |
| 3 | `P1_VPP_ENABLE` | 0x08 | Route VPP to socket **pin 1** (for Intel flash, 32-pin EPROM) |
| 4 | `ADDRESS_LINE_17` | 0x10 | Extend address bus to A17 (28-pin chips) |
| 5 | `ADDRESS_LINE_18` | 0x20 | Extend address bus to A18 (32-pin chips) |
| 6 | `READ_WRITE` | 0x40 | Control RW line (used in address-bus remapping) |
| 7 | `REGULATOR` | 0x80 | **Enable VPP boost regulator** (gate to 12V supply) |

### 2.2 Bit Interaction: Regulator vs. Pin Enable

**Critical rule** (from eprom.cpp:142–152):
- `REGULATOR (0x80)` must be asserted **first** to enable the 12V boost supply
- Then `P1_VPP_ENABLE (0x08)` or `A9_VPP_ENABLE (0x02)` or `VPE_ENABLE (0x04)` routes that 12V to the **intended pin**

**Example:** configure_eprom during write (eprom.cpp:142–152):
```c
if (handle->firestarter_get_control_register(handle, REGULATOR) == 0) {
    if (handle->protocol == 0x0B || is_flag_set(FLAG_VPE_AS_VPP)) {
        handle->firestarter_set_control_register(handle, REGULATOR, 1);  // line 146
    } else {
        handle->firestarter_set_control_register(handle, REGULATOR | VPE_TO_VPP, 1);  // line 149
    }
    delay(500);
}
// Then in program_mismatched_bytes (line 114–115):
// handle->firestarter_set_control_register(handle, VPE_ENABLE, 1);
```

**Socket pin targeting:** The choice of `P1_VPP_ENABLE` vs `A9_VPP_ENABLE` vs `VPE_ENABLE` is **fixed per protocol**, not per pinout:
- `P1_VPP_ENABLE` is hardwired to socket **pin 1** (for 32-pin DIP or 28-pin DIP with VPP @ pin 1)
- `A9_VPP_ENABLE` routes 12V to the **address line A9** (used for chip-ID reads, not data writes)
- `VPE_ENABLE` routes 12V to the **PGM pin** (used for 24-pin EPROM erase, not writes)

### 2.3 Hardware Revision Mapping (HARDWARE_REVISION builds)

File: `/workspaces/firestarter_prom/firestarter/include/rurp_hw_rev_utils.h:14–36`

For **Rev 2.0/2.1/2.2**, the control register layout shifts slightly:
```c
case REVISION_2_0:
case REVISION_2_1:
case REVISION_2_2: 
    ctrl_reg = data & (A9_VPP_ENABLE | VPE_ENABLE | P1_VPP_ENABLE | ADDRESS_LINE_17 | READ_WRITE | REGULATOR);
    ctrl_reg |= data & VPE_TO_VPP ? REV_2_VPE_TO_VPP : 0;   // bit 0 remapped
    ctrl_reg |= data & ADDRESS_LINE_16 ? REV_2_ADDRESS_LINE_16 : 0;  // bit 0 ↔ bit 5
    ctrl_reg |= data & ADDRESS_LINE_18 ? REV_2_ADDRESS_LINE_18 : 0;  // bit 3 ↔ pin 1 mux
    break;
```

**Implication:** Rev 2.x boards remap `VPE_TO_VPP` and address line bits to different physical pins, but the **logical bit values** remain the same in the firmware source. The `rurp_map_ctrl_reg_for_hardware_revision()` function translates before writing to hardware.

---

## Section 3: VPP Regulator + Measurement

### 3.1 VPP Boost Supply

**Hardware:** An external boost regulator (inferred from context; no explicit schematic in repo) produces ~12V from a lower input rail when `REGULATOR (0x80)` is asserted.

**Enable sequence** (common pattern, e.g., eprom.cpp:185–197):
1. Assert `REGULATOR` bit → boost supply turns on
2. Delay 50–500 ms → allow capacitors to charge and voltage to stabilize
3. Assert secondary pins (`P1_VPP_ENABLE`, `A9_VPP_ENABLE`, `VPE_ENABLE`) → route 12V to socket
4. Perform operation (read, write, erase)
5. Clear secondary pins first (if needed) → disconnect 12V from socket
6. Clear `REGULATOR` → disable boost supply

### 3.2 VPP ADC Measurement

**Pin:** Analog pin A2 (`VOLTAGE_MEASURE_PIN` in rurp_shield.h:21)

**Calibration:** Two resistors (R1, R2) form a divider; values stored in Arduino EEPROM as `rurp_configuration_t`:
```c
typedef struct rurp_configuration {
    char version[6];
    long r1;
    long r2;
    uint8_t hardware_revision;
} rurp_configuration_t;
```

**File:** `/workspaces/firestarter_prom/firestarter/include/rurp_types.h:19–24`

**Default values** (rurp_shield.h:91–92):
```c
#define VALUE_R1 270000   // 270 kΩ
#define VALUE_R2 44000    // 44 kΩ
```

**Read function** (rurp_common.cpp:51–70):
```c
uint16_t rurp_read_voltage_mv() {
    rurp_configuration_t* rurp_config = rurp_get_config();
    uint32_t r1 = rurp_config->r1;
    uint32_t r2 = rurp_config->r2;
    analogReference(DEFAULT);  // VCC = ~5V
    uint32_t voltage_adc_reading = analogRead(VOLTAGE_MEASURE_PIN);  // line 58
    long bandgap_adc_reading = rurp_get_bandgap_adc_reading();
    if (bandgap_adc_reading == 0 || r2 == 0) return 0;
    // Vin_mV = (voltage_adc_reading * 1100 * (R1 + R2)) / (bandgap_adc_reading * R2)
    uint64_t numerator = (uint64_t)voltage_adc_reading * 1100UL * (r1 + r2);
    uint64_t denominator = (uint64_t)bandgap_adc_reading * r2;
    return (numerator + (denominator / 2)) / denominator;  // line 69
}
```

**Safety validation** (eprom.cpp:199–232):
```c
void eprom_check_vpp(firestarter_handle_t* handle) {
    // ... enable REGULATOR and (for EPROM_STD/QUICK) VPE_TO_VPP ...
    uint16_t vpp_mv = rurp_read_voltage_mv();
    if (vpp_mv > (uint32_t)handle->vpp_mv + 500) {
        firestarter_response_format(response_code, "VPP is high: %u.%uV > %u.%uV", ...);
    } else if (vpp_mv < (uint32_t)handle->vpp_mv * 95 / 100) {
        firestarter_warning_response_format("VPP is low: ...", ...);
    }
    handle->firestarter_set_control_register(handle, REGULATOR | VPE_TO_VPP, 0);
}
```

**Socket pin routing for VPP measurement:**
The ADC measures the **regulator output voltage** itself, not the voltage at any specific socket pin. There is **no per-pin voltage measurement**. The regulator produces a single 12V rail, and control bits route that rail to different socket pins. The measurement validates that the regulator is functioning, not that 12V reached the correct socket pin.

---

## Section 4: Per-Protocol Handler Signal Flow

### 4.1 Protocol Dispatch (memory.cpp:44–117)

**File:** `/workspaces/firestarter_prom/firestarter/src/proms/memory.cpp:44–117`

**Dispatch order (source of truth):**
1. `protocol == 0x10` → `configure_flash_intel()` — Intel 28F
2. `protocol == 0x0D` → `configure_eeprom28c()` — AT28C 5V EEPROM (pure VCC)
3. `protocol == 0x06` → `configure_flash3()` — AMD unlock flash (5V)
4. `protocol ∈ {0x05, 0x35, 0x39}` → `configure_flash4()` — page-write flash (5V)
5. `protocol ∈ {0x07, 0x08, 0x0B}` → `configure_eprom()` — UV-EPROM (12V VPP)
6. `protocol ∈ {0x0E, 0x27, 0x28, 0x29}` → `configure_sram()` — SRAM/NVRAM (5V)
7. Fallback on `mem_type`

---

### 4.2 Protocol 0x07, 0x08, 0x0B: configure_eprom()

**File:** `/workspaces/firestarter_prom/firestarter/src/proms/eprom.cpp`

#### Initialization (eprom_generic_init, line 250–258)
- Call `eprom_check_vpp()` to validate regulator output
- If `chip_id > 0`, call `eprom_internal_check_chip_id()`

#### Chip-ID Read (eprom_get_chip_id, line 186–197)
```c
uint16_t eprom_get_chip_id(firestarter_handle_t* handle) {
    debug("Get chip ID");
    handle->firestarter_set_control_register(handle, REGULATOR, 1);      // Enable boost
    delay(50);
    handle->firestarter_set_control_register(handle, A9_VPP_ENABLE, 1);  // Route 12V to A9
    delay(100);
    uint16_t chip_id = handle->firestarter_get_data(handle, 0x0000) << 8;
    chip_id |= (handle->firestarter_get_data(handle, 0x0001));
    handle->firestarter_set_control_register(handle, REGULATOR | A9_VPP_ENABLE, 0);  // line 195
    return chip_id;
}
```
**Signal flow:** 12V boost enabled → routed to **A9 address line** (NOT to socket pin 1) → EPROMs respond with manufacturer/device ID when A9=12V and address=0x00/0x01.

#### Write (eprom_write_execute, line 142–183)
```c
void eprom_write_execute(firestarter_handle_t* handle) {
    if (handle->firestarter_get_control_register(handle, REGULATOR) == 0) {
        if (handle->protocol == 0x0B || is_flag_set(FLAG_VPE_AS_VPP)) {
            handle->firestarter_set_control_register(handle, REGULATOR, 1);               // EPROM_LEGACY
        } else {
            handle->firestarter_set_control_register(handle, REGULATOR | VPE_TO_VPP, 1); // EPROM_STD/QUICK
        }
        delay(500);
    }
    // Retry loop (lines 162–179)
    for (int w = 0; w < NUMBER_OF_RETRIES; w++) {
        program_mismatched_bytes(handle, mismatch_bitmask);  // line 163
        // ...
    }
}

void program_mismatched_bytes(firestarter_handle_t* handle, const uint8_t* mismatch_bitmask) {
    rurp_register_t programming_bits = VPE_ENABLE;
    handle->firestarter_set_control_register(handle, programming_bits, 1);   // line 116: Assert VPE_ENABLE
    delay(10);
    for (uint32_t i = 0; i < handle->data_size; i++) {
        if (mismatch_bitmask[i / 8] & (1 << (i % 8))) {
            handle->firestarter_set_data(handle, handle->address + i, handle->data_buffer[i]);
        }
    }
    handle->firestarter_set_control_register(handle, programming_bits, 0);   // line 124: Clear VPE_ENABLE
}
```

**Signal flow:**
- `REGULATOR + VPE_TO_VPP` (for protocol 0x07, 0x08) OR `REGULATOR` alone (for 0x0B)
- Then `VPE_ENABLE` during write pulse → 12V routed to **PGM pin** (via `eprom_internal_set_control_register`)
- **NOT to socket pin 1** (P1_VPP_ENABLE is NOT asserted)

#### Translation Layer (eprom_internal_set_control_register, line 268–274)
```c
void eprom_internal_set_control_register(firestarter_handle_t* handle, rurp_register_t bit, bool state) {
    if (bit & VPE_ENABLE && using_p1_as_vpp(handle)) {
        bit &= ~VPE_ENABLE;
        bit |= P1_VPP_ENABLE;  // line 271: Remap VPE_ENABLE → P1_VPP_ENABLE
    }
    ep_set_control_register(handle, bit, state);
}
```

**Conditional routing:** If `using_p1_as_vpp(handle)` (defined in memory_utils.h:24–26):
```c
static inline bool using_p1_as_vpp(const firestarter_handle_t* handle) {
    return (handle->pins == 32 && handle->bus_config.vpp_line == VPP_P1_32_DIP) ||
           (handle->pins < 32 && handle->bus_config.vpp_line == VPP_P1_28_DIP);
}
```
Then `VPE_ENABLE` is **redirected to `P1_VPP_ENABLE`** before writing to hardware.

**Implication:** For 28-pin and 32-pin chips where the pinout specifies `vpp_line == VPP_P1_28_DIP` (0x0F) or `VPP_P1_32_DIP` (0x15), the firmware sends 12V to **socket pin 1** instead of the PGM pin.

---

### 4.3 Protocol 0x0D: configure_eeprom28c()

**File:** `/workspace/firestarter_prom/firestarter/src/proms/eeprom_28c.cpp`

**Key feature:** **NO VPP regulator engagement** — AT28C chips are pure 5V parts.

#### Write (eeprom28c_write_init + eeprom28c_write_execute, line 79–115)
```c
void eeprom28c_write_init(firestarter_handle_t* handle) {
    // Check chip ID via A9-12V (line 81–86)
    if (handle->chip_id > 0) {
        eeprom28c_check_chip_id(handle);  // Asserts REGULATOR | A9_VPP_ENABLE (line 65, 67)
        if (handle->response_code == RESPONSE_CODE_ERROR) {
            return;
        }
    }
    // Disable SDP (Software Data Protection) — no VPP (line 91)
    flash_execute_command(EEPROM_SDP_DISABLE);  // Pure 5V writes to magic addresses
    // ...
}

void eeprom28c_write_execute(firestarter_handle_t* handle) {
    for (uint32_t i = 0; i < handle->data_size; i++) {
        uint32_t address = handle->address + i;
        uint8_t data = handle->data_buffer[i];
        handle->firestarter_set_data(handle, address, data);  // line 105: Pure 5V write
        // Wait for write (line 110)
        if (!eeprom28c_wait_for_write(handle, address, data)) {
            return;
        }
    }
}
```

**Signal flow:**
- **REGULATOR is NOT asserted during write** (only during optional chip-ID check at init)
- All writes are **pure 5V** via the data bus
- No `P1_VPP_ENABLE`, `A9_VPP_ENABLE`, or `VPE_ENABLE` during data writes

**Safety implication:** EEPROM_POLL (0x0D) route is **safe for 5V-only chips** because the VPP regulator never engages.

---

### 4.4 Protocol 0x0E, 0x27, 0x28, 0x29: configure_sram()

**File:** `/workspaces/firestarter_prom/firestarter/src/proms/sram.cpp:14–16`

```c
void configure_sram(firestarter_handle_t* handle) {
    debug("Configuring SRAM");
}
```

**Signal flow:** Completely empty handler — no special initialization.

The actual read/write happens via generic `memory_read_execute()` and `memory_write_execute()` from memory.cpp (line 171–212), which do **not assert any VPP bits**. SRAM operations use only the address bus, RW line, and data bus at 5V.

**Safety implication:** SRAM route (0x0E/0x27/0x28/0x29) is **safe for 5V-only chips** — VPP regulator never engages.

---

### 4.5 Protocol 0x10: configure_flash_intel()

**File:** `/workspaces/firestarter_prom/firestarter/src/proms/flash_intel.cpp`

#### Write Init (flash_intel_write_init, line 74–99)
```c
void flash_intel_write_init(firestarter_handle_t* handle) {
    handle->firestarter_set_control_register(handle, REGULATOR | P1_VPP_ENABLE, 1);  // line 75
    delay(500);
    flash_intel_check_vpp(handle);
    if (handle->response_code == RESPONSE_CODE_ERROR) {
        handle->firestarter_set_control_register(handle, REGULATOR | P1_VPP_ENABLE, 0);  // line 83
        return;
    }
    // ... chip-id check, erase, blank check ...
}

void flash_intel_check_vpp(firestarter_handle_t* handle) {
    // Caller already asserted REGULATOR | P1_VPP_ENABLE (line 33)
    uint16_t vpp_mv = rurp_read_voltage_mv();
    // ... validate voltage (line 39–48) ...
    // NO regulator clear — caller continues to use REGULATOR | P1_VPP_ENABLE (line 49)
}
```

**Signal flow:**
- Assert `REGULATOR | P1_VPP_ENABLE` → 12V routed to **socket pin 1**
- Validate voltage via ADC
- Continue with same bits asserted through write/erase operations
- Clear both bits at cleanup (flash_intel_cleanup, line 126)

**Safety implication:** FLASH_INTEL (0x10) route always uses socket **pin 1** for VPP. Correct for Intel 28F chips (which have VPP at pin 1), but would damage any other chip type routed through this handler by accident.

---

### 4.6 Protocol 0x06: configure_flash3()

**File:** `/workspaces/firestarter_prom/firestarter/src/proms/flash_type_3.cpp`

```c
void configure_flash3(firestarter_handle_t* handle) {
    debug("Configuring Flash");
    handle->firestarter_operation_init = flash3_generic_init;
    switch (handle->cmd) {
    case CMD_WRITE:
        handle->firestarter_operation_init = flash3_write_init;
        handle->firestarter_operation_main = flash3_write_execute;
        break;
    // ...
    }
}

void flash3_write_execute(firestarter_handle_t* handle) {
    for (uint32_t i = 0; i < handle->data_size; i++) {
        flash_execute_command(FLASH_ENABLE_WRITE);  // line 84: pure 5V commands
        handle->firestarter_set_data(handle, handle->address + i, handle->data_buffer[i]);
        flash_util_verify_operation(handle, handle->data_buffer[i]);
        if (handle->response_code == RESPONSE_CODE_ERROR) {
            return;
        }
    }
}
```

**Signal flow:** **No VPP regulator engagement** — all writes are pure 5V via the magic address-based unlock sequence (AMD unlock). The FLASH_ENABLE_WRITE command issues writes to magic addresses (0x5555, 0x2AAA) without asserting any VPP bits.

**Safety implication:** FLASH_AMD_ALT (0x06) route is **safe for 5V-only chips** — VPP regulator never engages.

---

### 4.7 Protocol 0x05, 0x35, 0x39: configure_flash4()

**File:** `/workspaces/firestarter_prom/firestarter/src/proms/flash_type_4.cpp`

```c
void flash4_write_init(firestarter_handle_t* handle) {
    // No VPP regulator — pure 5V page-write flow
    if (!is_flag_set(FLAG_SKIP_BLANK_CHECK)) {
        mem_util_blank_check(handle);
    }
}

void flash4_write_execute(firestarter_handle_t* handle) {
    for (uint32_t i = 0; i < handle->data_size; i++) {
        uint32_t address = handle->address + i;
        uint8_t expected = handle->data_buffer[i];
        handle->firestarter_set_data(handle, address, expected);  // line 64: pure 5V write
        // ...
    }
}
```

**Signal flow:** **No VPP regulator engagement** — all writes are pure 5V page writes (e.g., SST39SF040).

**Safety implication:** FLASH_AMD_STD/EEPROM_LIKE (0x05, 0x35, 0x39) route is **safe for 5V-only chips** — VPP regulator never engages.

---

## Section 5: Pin-Role Wiring — Validation of Safety Claims

### 5.1 Data Source: pinouts.json → bus_config

**File:** `/workspaces/firestarter_prom/firestarter_app/firestarter/data/pinouts.json`

Example entries:
```json
{
    "DIP24_2716": {
        "pins": {
            "vpp-pin": [21],
            "ce-pin": [18],
            "oe-pin": [20],
            ...
        }
    },
    "DIP28_2764": {
        "pins": {
            "vpp-pin": [1],
            "pgm-pin": [27],
            ...
        }
    },
    "DIP28_27256": {
        "pins": {
            "vpp-pin": [1],
            ...
        }
    }
}
```

**File:** `/workspaces/firestarter_prom/firestarter_app/firestarter/database.py:351–428` (_map_data)

The Python host reads the pinout and builds a `bus_config` dictionary:
```python
if pin_count and pinout_key:
    bus_config = self.get_bus_config(pin_count, pinout_key)  # line 425
    if bus_config:
        data["bus-config"] = bus_config  # line 427
```

**File:** `/workspaces/firestarter_prom/firestarter_app/firestarter/database.py:257–313` (get_bus_config)

```python
def get_bus_config(self, pins: int, variant: str):
    pin_map_data = self.get_pin_map(pins, variant)
    # ...
    for pin_func in ["rw-pin", "vpp-pin"]:  # line 284
        if pin_func in pin_map_data:
            pin_val = pin_map_data[pin_func]
            pin_to_check = pin_val[0] if isinstance(pin_val, list) else pin_val
            if pin_to_check in pin_conversions.get(pins, {}):
                resolved = pin_conversions[pins][pin_to_check]  # Translate DIP pin → bus line
                if pin_func == "vpp-pin" and resolved in (ROM_CE, ROM_OE):
                    continue  # Skip if VPP overlaps with CE/OE
                map_config[pin_func] = resolved  # line 295
```

**Example flow for DIP24_2716:**
1. Pinout JSON: `"vpp-pin": [21]`
2. pin_conversions[24][21] = `11` (bus line)
3. bus_config["vpp-pin"] = `11`
4. Firmware receives `handle->bus_config.vpp_line = 11`

**Example flow for DIP28_2764:**
1. Pinout JSON: `"vpp-pin": [1]`
2. pin_conversions[28][1] = `15` (bus line)
3. bus_config["vpp-pin"] = `15`
4. Firmware receives `handle->bus_config.vpp_line = 15`

---

### 5.2 Firmware Usage of bus_config.vpp_line

**File:** `/workspaces/firestarter_prom/firestarter/include/memory_utils.h:24–27`

```c
static inline bool using_p1_as_vpp(const firestarter_handle_t* handle) {
    return (handle->pins == 32 && handle->bus_config.vpp_line == VPP_P1_32_DIP) ||
           (handle->pins < 32 && handle->bus_config.vpp_line == VPP_P1_28_DIP);
}

// Where:
#define VPP_P1_32_DIP  0x15  (21 in decimal — bus line 21)
#define VPP_P1_28_DIP  0x0F  (15 in decimal — bus line 15)
```

**From memory.cpp (address remapping):**
```c
uint32_t mem_util_remap_address_bus(const firestarter_handle_t* handle, uint32_t address, uint8_t read_write) {
    bus_config_t config = handle->bus_config;
    // ...
    // line 242–245: Set VPP line to high if VPP is NOT on P1
    if (config.vpp_line != 0xFF && !using_p1_as_vpp(handle)) {
        reorg_address |= 1UL << config.vpp_line;
    }
    // ...
}
```

**Interpretation:**
- If `vpp_line` matches the magic constant `VPP_P1_28_DIP` (0x0F) or `VPP_P1_32_DIP` (0x15), the firmware assumes VPP is routed via the **P1_VPP_ENABLE control bit** (socket pin 1)
- If `vpp_line` is any other value, the firmware assumes VPP is on a **data-line pin** (must be driven HIGH via address remapping during reads)
- If `vpp_line == 0xFF`, VPP is not used (5V chips)

---

### 5.3 Safety Claim Verification

**Claim A:** "DIP24_2716 has vpp-pin=21, which maps to bus line 11. For DIP24 adapters, configure_eprom asserts VPE_ENABLE (redirected to P1_VPP_ENABLE if using_p1_as_vpp), placing 12V on socket pin 1."

**Verification:**
- ❌ **INCORRECT** — DIP24_2716 vpp-pin=21 maps to bus line 11, NOT bus line 15 (0x0F)
- `using_p1_as_vpp()` returns `false` because `vpp_line (11) != VPP_P1_28_DIP (15)`
- Therefore, `VPE_ENABLE` is **NOT redirected** to `P1_VPP_ENABLE` (eprom_internal_set_control_register, line 269 condition fails)
- The firmware asserts `VPE_ENABLE` which routes 12V to the **PGM pin**, not pin 1
- Bus line 11 (DIP24 socket pin 21) is driven HIGH in address remapping (memory.cpp:316) during reads to keep VPP disconnected during read cycles

---

**Claim B:** "configure_eprom always asserts P1_VPP_ENABLE during write pulse for 28-pin and 32-pin chips, putting ~12V on socket pin 1."

**Verification:**
- ⚠️ **PARTIALLY CORRECT, WITH CONDITIONS:**
  - For **28-pin chips with vpp_line = VPP_P1_28_DIP (0x0F)**: `using_p1_as_vpp()` returns `true` → `VPE_ENABLE` is redirected to `P1_VPP_ENABLE` → 12V on pin 1 ✓
  - For **28-pin chips with vpp_line ≠ 0x0F** (e.g., 11 for DIP24_2716 adapted): condition fails → `VPE_ENABLE` asserted without redirect → 12V on PGM pin (NOT pin 1)
  - For **32-pin chips with vpp_line = VPP_P1_32_DIP (0x15)**: same as 28-pin; 12V on pin 1 ✓
  - For **32-pin chips with other vpp_line values**: no redirect; 12V on alternate pin

**Implication:** The `using_p1_as_vpp()` check **gates the redirect**. If the pinout specifies a non-P1 VPP line, the redirect never fires, and the firmware attempts to route VPP via PGM pin (VPE_ENABLE), not socket pin 1 (P1_VPP_ENABLE).

---

**Claim C:** "DIP24_AT28C256 routed through configure_eprom with DIP28_2764 pinout would put 12V on socket pin 1 = A14 address pin → damage."

**Verification:**
- ❌ **INCORRECT due to protocol override (WARNING-5):**
  - AT28C256 is a 5V-only EEPROM (electrical.type = "Flash/EEPROM")
  - In `firestarter_app/CLAUDE.md`, WARNING-5 states: when a chip has `pinout=DIP28_2764` AND `protocol_id=0x07` (EPROM_STD) AND `electrical.type="Flash/EEPROM"`, the `algorithm` is flipped to `0x0D` (EEPROM_POLL)
  - EEPROM_POLL (0x0D) → `configure_eeprom28c()` → **no VPP regulator engagement** → all writes at 5V
  - So AT28C256 never reaches `configure_eprom()` if the database was regenerated with the override

**Verification source:** `/workspaces/firestarter_prom/firestarter_app/CLAUDE.md` (lines discussing WARNING-5 protocol override)

However, if an **older hand-crafted JSON** or **unapplied manual override** routes a 28C chip through `configure_eprom`:
- Pinout DIP28_2764 has vpp-pin=[1], mapping to bus line 15 = VPP_P1_28_DIP
- `using_p1_as_vpp()` would return `true` → VPE_ENABLE redirected to P1_VPP_ENABLE
- 12V would route to socket pin 1 (which is A14, not VPP) → **potential damage**
- **Mitigation:** The protocol override ensures this path is blocked in the current database.

---

**Claim D:** "configure_eeprom28c does NOT engage the VPP regulator during write."

**Verification:**
- ✅ **CORRECT**
- eeprom28c_write_init() calls optional `eeprom28c_check_chip_id()` which asserts REGULATOR + A9_VPP_ENABLE, but only if `handle->chip_id > 0`
- eeprom28c_write_execute() calls `handle->firestarter_set_data()` → `memory_set_data()` (memory.cpp:206–212) → no VPP bits asserted
- All data writes are pure 5V

---

**Claim E:** "configure_sram is essentially a no-op configure step; actual write uses memory_set_data with no VPP."

**Verification:**
- ✅ **CORRECT**
- configure_sram() body is empty (sram.cpp:14–16)
- Writes dispatch to memory_write_execute() → calls handle->firestarter_set_data → no VPP bits

---

## Section 6: Board Revisions and JP4 Jumper

### 6.1 Hardware Revision Detection

**File:** `/workspaces/firestarter_prom/firestarter/include/rurp_hw_rev_utils.h:42–68`

```c
#ifdef HARDWARE_REVISION
void rurp_detect_hardware_revision() {
    pinMode(HARDWARE_REVISION_PIN, INPUT_PULLUP);       // A3
    pinMode(VOLTAGE_MEASURE_PIN, INPUT_PULLUP);
    int value = digitalRead(HARDWARE_REVISION_PIN);
    switch (value) {
    case 1:
        revision = analogRead(VOLTAGE_MEASURE_PIN) < 1000 ? REVISION_1 : REVISION_0;
        break;
    case 0:
        revision = REVISION_2_0;
        break;
    default:
        revision = 0xFF;
    }
    pinMode(VOLTAGE_MEASURE_PIN, INPUT);
}
#endif
```

**Revisions:**
- **REVISION_0 (0):** Detected when A3=HIGH and A2 ADC>1000
- **REVISION_1 (1):** Detected when A3=HIGH and A2 ADC<1000
- **REVISION_2_0/2_1/2_2 (2, 3, 4):** Detected when A3=LOW

**JP4 Jumper:** Not explicitly defined in the firmware code provided. CLAUDE.md mentions "rev 2.0 board and jp4 is closed" but no #ifdef or control logic references JP4 by name. The revision detection uses A3 and A2 analog pins; JP4 likely configures one of these pins when closed/open.

### 6.2 Register Mapping by Revision

**File:** `/workspaces/firestarter_prom/firestarter/include/rurp_hw_rev_utils.h:14–36`

For **REVISION_2_x**, the control register bits are remapped before writing:
```c
case REVISION_2_0:
case REVISION_2_1:
case REVISION_2_2: 
    ctrl_reg = data & (A9_VPP_ENABLE | VPE_ENABLE | P1_VPP_ENABLE | ADDRESS_LINE_17 | READ_WRITE | REGULATOR);
    ctrl_reg |= data & VPE_TO_VPP ? REV_2_VPE_TO_VPP : 0;
    ctrl_reg |= data & ADDRESS_LINE_16 ? REV_2_ADDRESS_LINE_16 : 0;
    ctrl_reg |= data & ADDRESS_LINE_18 ? REV_2_ADDRESS_LINE_18 : 0;
    break;
```

**Implication:** The logical control register values in the firmware source remain the same (0x01, 0x02, 0x04, 0x08, etc.), but the physical hardware pins they control shift between revisions. The translation function ensures backward compatibility.

### 6.3 Calibration Storage

**File:** `/workspaces/firestarter_prom/firestarter/include/rurp_types.h:19–24`

```c
typedef struct rurp_configuration {
    char version[6];
    long r1;
    long r2;
    uint8_t hardware_revision;
} rurp_configuration_t;
```

Default values (rurp_shield.h:91–92):
- `VALUE_R1 = 270000` (270 kΩ)
- `VALUE_R2 = 44000` (44 kΩ)

These are stored in Arduino EEPROM and loaded at startup. Different board revisions may require different R1/R2 values for accurate VPP measurement calibration.

---

## Section 7: Safety Implications Summary

### 7.1 Verified Claims

| Claim | Status | Evidence |
|-------|--------|----------|
| (a) configure_eprom asserts P1_VPP_ENABLE for 28/32-pin chips with vpp_line == P1_* | ⚠️ Conditional | eprom_internal_set_control_register (line 268–274) redirects VPE_ENABLE → P1_VPP_ENABLE only if using_p1_as_vpp() == true |
| (b) configure_eeprom28c does NOT engage VPP regulator during write | ✅ Correct | eeprom_28c.cpp: no REGULATOR bit during write, only optional chip-ID check |
| (c) configure_sram is a no-op; write uses memory_set_data with no VPP | ✅ Correct | sram.cpp:14–16 is empty; write dispatches to generic memory_set_data |
| (d) 24-pin AT28C16 through configure_eprom + DIP24_2716 pinout → 12V on WE → damage | ❌ Blocked | Protocol override (WARNING-5) routes 5V EEPROMs to configure_eeprom28c (0x0D), not configure_eprom (0x07) |

### 7.2 Conditional Safety

**The redirect in eprom_internal_set_control_register (line 268–274) is the critical gate:**

```c
void eprom_internal_set_control_register(firestarter_handle_t* handle, rurp_register_t bit, bool state) {
    if (bit & VPE_ENABLE && using_p1_as_vpp(handle)) {
        bit &= ~VPE_ENABLE;
        bit |= P1_VPP_ENABLE;  // Only fires if using_p1_as_vpp() == true
    }
    ep_set_control_register(handle, bit, state);
}
```

**VPP routing is safe ONLY IF:**
1. The pinout JSON specifies the correct `vpp-pin` for the chip
2. database.py correctly translates `vpp-pin` → `bus_config.vpp_line` via pin_conversions
3. `using_p1_as_vpp()` logic correctly identifies magic constants VPP_P1_28_DIP (0x0F) and VPP_P1_32_DIP (0x15)
4. The protocol dispatch ensures 5V-only chips NEVER reach configure_eprom (via the WARNING-5 override for 28C EEPROMs)

**If any of these steps fails, 12V can be placed on the wrong socket pin.**

### 7.3 Attack Surface

**Unvalidated inputs** (potential hazards if bypassed):
1. **Hand-crafted JSON:** A user-supplied bus-config can lie about vpp_line
2. **Stale pinouts.json:** If the pinout database is out of date, DIP pin assignments may be wrong
3. **Missing chip_id check:** configure_eprom allows `chip_id == 0` (skip ID check), masking chip type misidentification
4. **Protocol field omitted:** If a JSON command has `algorithm: 0` (or missing), the firmware falls back to `mem_type`, which may be ambiguous

**Mitigations in place:**
- chip_database.json is **generated** from upstream infoic.xml, not hand-edited
- The protocol dispatch (memory.cpp:72–101) **always fires first**, so hand-crafted JSON with ambiguous `mem_type` is caught
- WARNING-5 override ensures no 5V EEPROM reaches configure_eprom
- VPP ADC measurement validates regulator output (though NOT per-socket-pin)

### 7.4 Remaining Validation Gaps

1. **Per-socket-pin voltage measurement:** The current ADC measures regulator output, NOT the voltage at individual socket pins. A shorted VPP line or misfired control bit could still place 12V on the wrong pin without triggering an ADC error.

2. **Address-line remapping for VPP lines:** When `vpp_line` is NOT a P1_VPP magic constant, the firmware drives it HIGH via address remapping (memory.cpp:314–245). This is correct for protecting the chip during READ cycles (VPP must be low during reads), but there is NO validation that the remapped bus line actually connects to the VPP pin.

3. **Chip-ID verification:** The chip-ID check is optional (only if `chip_id > 0`). Without it, the wrong chip type can be programmed with the wrong VPP voltage.

---

## Section 8: File Index

### Core Firmware Files

| File | Lines | Purpose |
|------|-------|---------|
| firestarter.h | 1–108 | Top-level struct definitions (firestarter_handle_t, bus_config_t) |
| rurp_shield.h | 1–167 | Control register bit definitions, board setup stubs |
| rurp_types.h | 1–25 | rurp_register_t typedef, rurp_configuration_t |
| memory.h | 1–23 | configure_memory() declaration |
| memory_utils.h | 1–31 | Address remapping, using_p1_as_vpp() inline |
| memory.cpp | 44–117 | Protocol dispatch (source of truth) |
| memory.cpp | 119–128 | memory_set_control_register(), memory_get_control_register() |
| memory.cpp | 182–194 | memory_get_data() — read with address remapping |
| memory.cpp | 202–212 | memory_set_data() — write with address remapping |
| memory.cpp | 226–249 | mem_util_remap_address_bus() — address mux logic |

### EPROM Handler (Protocol 0x07, 0x08, 0x0B)

| File | Lines | Purpose |
|------|-------|---------|
| eprom.cpp | 40–76 | configure_eprom() — init and handler dispatch |
| eprom.cpp | 78–85 | eprom_check_chip_id_init() — prepare for ID read |
| eprom.cpp | 142–183 | eprom_write_execute() — write with VPE_TO_VPP logic |
| eprom.cpp | 113–125 | program_mismatched_bytes() — asserts VPE_ENABLE |
| eprom.cpp | 186–197 | eprom_get_chip_id() — reads ID via A9-12V |
| eprom.cpp | 199–232 | eprom_check_vpp() — validates regulator output |
| eprom.cpp | 268–274 | eprom_internal_set_control_register() — VPE_ENABLE → P1_VPP_ENABLE redirect |

### EEPROM 28C Handler (Protocol 0x0D)

| File | Lines | Purpose |
|------|-------|---------|
| eeprom_28c.cpp | 34–47 | configure_eeprom28c() — no VPP |
| eeprom_28c.cpp | 79–99 | eeprom28c_write_init() — SDP disable (5V) |
| eeprom_28c.cpp | 101–115 | eeprom28c_write_execute() — page write loop |
| eeprom_28c.cpp | 55–77 | eeprom28c_check_chip_id() — optional A9-12V check |

### SRAM Handler (Protocol 0x0E, 0x27, 0x28, 0x29)

| File | Lines | Purpose |
|------|-------|---------|
| sram.cpp | 14–16 | configure_sram() — empty |

### Flash Handlers (Protocol 0x05, 0x06, 0x10, 0x35, 0x39)

| File | Lines | Purpose |
|------|-------|---------|
| flash_intel.cpp | 52–72 | configure_flash_intel() — P1_VPP_ENABLE handler |
| flash_intel.cpp | 74–99 | flash_intel_write_init() — REGULATOR + P1_VPP_ENABLE |
| flash_type_3.cpp | 30–50 | configure_flash3() — no VPP (5V) |
| flash_type_4.cpp | 25–39 | configure_flash4() — no VPP (5V) |

### Board-Level Files

| File | Lines | Purpose |
|------|-------|---------|
| uno_rurp_shield.cpp | 31–92 | UNO register I/O, PORTD/PORTB control |
| leonardo_rurp_shield.cpp | 33–151 | Leonardo register I/O, complex pin mapping |
| rurp_common.cpp | 51–70 | rurp_read_voltage_mv() — ADC calibration + math |
| rurp_register_utils.h | 23–59 | rurp_write_to_register() — register caching + revision mapping |
| rurp_hw_rev_utils.h | 14–68 | Hardware revision detection and control register remapping |

### Python Host Files

| File | Lines | Purpose |
|------|-------|---------|
| database.py | 68–133 | pin_conversions dict (DIP pin → bus line) |
| database.py | 257–313 | get_bus_config() — translate pinout → bus_config |
| database.py | 351–428 | _map_data() — extract and attach bus_config to chip data |
| database.py | 522–560 | convert_to_programmer() — finalize JSON command |
| pinouts.json | all | DIP pin role definitions (vpp-pin, ce-pin, oe-pin, etc.) |

---

## Conclusion

The firmware's **protocol dispatch (memory.cpp:44–117) is the primary safety gate**. By dispatching on `protocol` before `mem_type`, the firmware ensures that 5V-only chips (EEPROM 28C, SRAM, 5V Flash) are routed to handlers that do NOT engage the VPP regulator. The **conditional redirect in eprom_internal_set_control_register (line 268–274) is the secondary gate**, ensuring that when VPE_ENABLE is asserted, it routes to the correct socket pin (P1 vs. PGM) based on the pinout's vpp_line specification.

The **WARNING-5 protocol override** (documented in CLAUDE.md) blocks the most dangerous path: a 5V EEPROM on a DIP28_2764 pinout being routed through configure_eprom, which would place 12V on pin 1 (the A14 address pin).

However, **the system remains vulnerable to**:
1. Hand-crafted JSON with incorrect bus_config
2. Stale pinouts.json
3. Missing chip_id validation
4. Per-socket-pin voltage measurement gaps

A comprehensive safety validation flow would include:
- Chip-ID verification (currently optional)
- Per-pin voltage measurement (currently unavailable)
- Closed-loop feedback during write (currently uses DQ7 polling for EPROM, not voltage sensing)

