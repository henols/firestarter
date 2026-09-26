# Phase 1: Safety Closure (Intel-flash VPP + 28C chip-ID) — Pattern Map

**Mapped:** 2026-05-11
**Files analyzed:** 8 (2 modify + 6 new)
**Analogs found:** 8 / 8

## File Classification

| New / Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---------------------|------|-----------|----------------|---------------|
| `firestarter/src/proms/flash_intel.cpp` (MODIFY: add static `flash_intel_check_vpp` + wire into `flash_intel_write_init`) | firmware-handler-edit | init-time safety check (regulator-already-up, response_code path) | `firestarter/src/proms/eprom.cpp:199-232` (`eprom_check_vpp`) + `firestarter/src/proms/eprom.cpp:250-258` (`eprom_generic_init` order) | exact |
| `firestarter/src/proms/flash_intel.cpp` static helper `flash_intel_check_vpp` | firmware-handler-helper | regulator-state-assumption: caller already enabled REGULATOR \| P1_VPP_ENABLE | `firestarter/src/proms/eprom.cpp:199-232` | exact (function body shape); peer (different regulator bit) |
| `firestarter/src/proms/eeprom_28c.cpp` (MODIFY: add static `eeprom28c_check_chip_id` + wire into `eeprom28c_write_init` BEFORE SDP-disable) | firmware-handler-edit | init-time safety check (gated on `handle->chip_id > 0`, response_code path) | `firestarter/src/proms/flash_intel.cpp:47-62` (call-site ordering) + `firestarter/src/proms/eprom.cpp:186-197` (A9-12V read mechanism) + `firestarter/src/proms/flash_intel.cpp:115-124` (compare + response shape) | exact (call-site + compare); role-match (read mechanism) |
| `firestarter/src/proms/eeprom_28c.cpp` static helper `eeprom28c_check_chip_id` | firmware-handler-helper | A9-12V identification read (REGULATOR + A9_VPP_ENABLE) then compare | `firestarter/src/proms/eprom.cpp:186-197` (`eprom_get_chip_id`) | exact (mechanism); peer (different read addresses derived from `mem_size`) |
| `firestarter/test/native/avr/test_flash_intel_vpp/test_flash_intel_vpp.cpp` | native-unity-suite | request-response (script `s_mock_vpp_mv`, drive `configure_memory` → `operation_init`, assert `response_code`) | `firestarter/test/native/avr/test_dispatch/test_configure_memory.cpp` (`make_handle`, `setUp`/`tearDown`, `main` enumeration) | exact (skeleton); peer (asserts behaviour, not dispatch) |
| `firestarter/test/native/avr/test_flash_intel_vpp/host_stubs.cpp` | native-test-stubs | link-time strong overrides for `rurp_read_voltage_mv` + `rurp_get_hardware_revision` via TU-private mutable globals | `firestarter/test/native/avr/test_dispatch/host_stubs.cpp` (every other stub byte-identical) | exact (independent suite-local copy) |
| `firestarter/test/native/avr/test_flash_intel_vpp/avr/pgmspace.h` | pgm-shim | host-side PROGMEM/PSTR/pgm_read_* neutralization | `firestarter/test/native/avr/test_dispatch/avr/pgmspace.h` | exact (verbatim copy) |
| `firestarter/test/native/avr/test_eeprom28c_chip_id/test_eeprom28c_chip_id.cpp` | native-unity-suite | request-response (script bytes via handle function pointer `firestarter_get_data`) | `firestarter/test/native/avr/test_dispatch/test_configure_memory.cpp` skeleton + Option-M2 (handle-pointer override) | exact (skeleton); peer (function-pointer mocking) |
| `firestarter/test/native/avr/test_eeprom28c_chip_id/host_stubs.cpp` | native-test-stubs | byte-identical to dispatch stubs (no per-suite mocking needed; mocks live in test TU) | `firestarter/test/native/avr/test_dispatch/host_stubs.cpp` | exact (verbatim copy) |
| `firestarter/test/native/avr/test_eeprom28c_chip_id/avr/pgmspace.h` | pgm-shim | host-side PROGMEM neutralization | `firestarter/test/native/avr/test_dispatch/avr/pgmspace.h` | exact (verbatim copy) |

---

## Pattern Assignments

### `firestarter/src/proms/flash_intel.cpp` — add static `flash_intel_check_vpp` helper

**Role:** firmware-handler-helper (inline-copy per RESEARCH.md D-04 recommendation — do NOT extract a shared helper)
**Analog:** `firestarter/src/proms/eprom.cpp:199-232` (`eprom_check_vpp`)
**Why:** Canonical VPP-compare implementation. Tolerance bands, REV0 guard, FORCE-flag downgrade, response-format shape are 1:1 reusable. The only material difference is regulator state: the analog *asserts and clears* `REGULATOR | VPE_TO_VPP` itself; the new helper runs *inside* `flash_intel_write_init`, which already asserted `REGULATOR | P1_VPP_ENABLE` and slept 500ms — the helper MUST NOT toggle the regulator.

**Excerpt to mirror** (`firestarter/src/proms/eprom.cpp:199-232`):
```c
void eprom_check_vpp(firestarter_handle_t* handle) {
    debug("Check VPP");
#ifdef HARDWARE_REVISION
    if (rurp_get_hardware_revision() == REVISION_0) {
        firestarter_warning_response("Rev0 dont support reading VPP/VPE");
        return;
    }
#endif
    if (handle->protocol == 0x0B || is_flag_set(FLAG_VPE_AS_VPP)) {
        handle->firestarter_set_control_register(handle, REGULATOR, 1);
    } else {
        handle->firestarter_set_control_register(handle, REGULATOR | VPE_TO_VPP, 1);
    }
    delay(100);
    uint16_t vpp_mv = rurp_read_voltage_mv();
#ifdef SERIAL_DEBUG
    debug_format("Checking VPP voltage %u mV", vpp_mv);
#endif
    if (vpp_mv > (uint32_t)handle->vpp_mv + 500) {
        int response_code = is_flag_set(FLAG_FORCE) ? RESPONSE_CODE_WARNING : RESPONSE_CODE_ERROR;
        firestarter_response_format(response_code, "VPP is high: %u.%uV > %u.%uV",
                                    (vpp_mv + 50) / 1000, (((vpp_mv + 50) / 100) % 10),
                                    (handle->vpp_mv + 50) / 1000, (((handle->vpp_mv + 50) / 100) % 10));
    } else if (vpp_mv < (uint32_t)handle->vpp_mv * 95 / 100) {
        firestarter_warning_response_format("VPP is low: %u.%uV < %u.%uV",
                                            (vpp_mv + 50) / 1000, (((vpp_mv + 50) / 100) % 10),
                                            (handle->vpp_mv + 50) / 1000, (((handle->vpp_mv + 50) / 100) % 10));
    }
    handle->firestarter_set_control_register(handle, REGULATOR | VPE_TO_VPP, 0);
}
```

**Shape to mirror** (new static in `flash_intel.cpp`, between line 23 forward decls and line 25 `configure_flash_intel`; per RESEARCH.md Code Examples line 466-490):
```c
static void flash_intel_check_vpp(firestarter_handle_t* handle) {
    debug("Check VPP (Intel)");
#ifdef HARDWARE_REVISION
    if (rurp_get_hardware_revision() == REVISION_0) {
        firestarter_warning_response("Rev0 dont support reading VPP/VPE");
        return;
    }
#endif
    // Caller (flash_intel_write_init) already asserted REGULATOR | P1_VPP_ENABLE
    // and delayed 500ms; do not toggle the regulator here.
    uint16_t vpp_mv = rurp_read_voltage_mv();
#ifdef SERIAL_DEBUG
    debug_format("Checking VPP voltage %u mV", vpp_mv);
#endif
    if (vpp_mv > (uint32_t)handle->vpp_mv + 500) {
        int response_code = is_flag_set(FLAG_FORCE) ? RESPONSE_CODE_WARNING : RESPONSE_CODE_ERROR;
        firestarter_response_format(response_code, "VPP is high: %u.%uV > %u.%uV",
                                    (vpp_mv + 50) / 1000, (((vpp_mv + 50) / 100) % 10),
                                    (handle->vpp_mv + 50) / 1000, (((handle->vpp_mv + 50) / 100) % 10));
    } else if (vpp_mv < (uint32_t)handle->vpp_mv * 95 / 100) {
        firestarter_warning_response_format("VPP is low: %u.%uV < %u.%uV",
                                            (vpp_mv + 50) / 1000, (((vpp_mv + 50) / 100) % 10),
                                            (handle->vpp_mv + 50) / 1000, (((handle->vpp_mv + 50) / 100) % 10));
    }
    // NO regulator clear — caller continues to use REGULATOR | P1_VPP_ENABLE through the write pulse.
}
```

**Anti-patterns to avoid:**
- Do NOT toggle `REGULATOR` / `VPE_TO_VPP` / `P1_VPP_ENABLE` inside the helper — caller owns the regulator lifecycle (the analog clears at line 231 but the new helper must not).
- Do NOT add a declaration to `flash_intel.h` — the helper is `static`, internal linkage only.
- Do NOT "fix" the literal `"Rev0 dont support reading VPP/VPE"` message — verbatim grep-able string by convention.
- Do NOT edit `eprom_check_vpp` (D-04 says inline-copy, not extract — touching verified v1.0 code risks Phase 4 HW-02 regression that no test in this milestone catches; see RESEARCH.md Pitfall 6).

---

### `firestarter/src/proms/flash_intel.cpp` — call-site in `flash_intel_write_init`

**Role:** firmware-handler-edit (insert VPP check between existing 500ms delay and chip-id branch)
**Analog:** `firestarter/src/proms/eprom.cpp:250-258` (`eprom_generic_init` order: vpp → chip_id → proceed)
**Why:** This is the canonical v1.0 "check vpp THEN chip_id" ordering. SAF-04 brings `flash_intel_write_init` into line with this established pattern (chip identity is meaningless if the rail is wrong).

**Excerpt to mirror — call-site ordering** (`firestarter/src/proms/eprom.cpp:250-258`):
```c
void eprom_generic_init(firestarter_handle_t* handle) {
    eprom_check_vpp(handle);
    if (handle->response_code == RESPONSE_CODE_ERROR) {
        return;
    }
    if (handle->chip_id > 0) {
        eprom_internal_check_chip_id(handle, is_flag_set(FLAG_FORCE) ? RESPONSE_CODE_WARNING : RESPONSE_CODE_ERROR);
    }
}
```

**Current state at edit site** (`firestarter/src/proms/flash_intel.cpp:47-62`):
```c
void flash_intel_write_init(firestarter_handle_t* handle) {
    handle->firestarter_set_control_register(handle, REGULATOR | P1_VPP_ENABLE, 1);
    delay(500);
    if (handle->chip_id > 0) {                         // <-- insert vpp check BEFORE this branch
        flash_intel_check_chip_id(handle);
        if (handle->response_code == RESPONSE_CODE_ERROR) {
            return;
        }
    }
    if (is_flag_set(FLAG_CAN_ERASE) && !is_flag_set(FLAG_SKIP_ERASE)) {
        flash_intel_erase_execute(handle);
    }
    if (!is_flag_set(FLAG_SKIP_BLANK_CHECK)) {
        mem_util_blank_check(handle);
    }
}
```

**Target shape** (insert after line 49 `delay(500);`):
```c
void flash_intel_write_init(firestarter_handle_t* handle) {
    handle->firestarter_set_control_register(handle, REGULATOR | P1_VPP_ENABLE, 1);
    delay(500);
    flash_intel_check_vpp(handle);
    if (handle->response_code == RESPONSE_CODE_ERROR) {
        return;
    }
    if (handle->chip_id > 0) {
        flash_intel_check_chip_id(handle);
        if (handle->response_code == RESPONSE_CODE_ERROR) {
            return;
        }
    }
    // ... unchanged below
}
```

**Anti-patterns to avoid:**
- Do NOT re-assert `REGULATOR | P1_VPP_ENABLE` after the check — already on.
- Do NOT extend the check into `flash_intel_erase_execute` (line 76-85) — out of scope per CONTEXT.md "Deferred Ideas" (v1.2 follow-up).
- Do NOT change the early-return semantics from `RESPONSE_CODE_ERROR`-checked to a different code — must match `eprom_generic_init` line 252 exactly.

---

### `firestarter/src/proms/eeprom_28c.cpp` — add static `eeprom28c_check_chip_id` helper

**Role:** firmware-handler-helper (Option A from RESEARCH.md — A9-12V mechanism, datasheet-correct for AT28C family)
**Analog A (read mechanism):** `firestarter/src/proms/eprom.cpp:186-197` (`eprom_get_chip_id`)
**Analog B (compare + response shape):** `firestarter/src/proms/flash_intel.cpp:115-124` (`flash_intel_check_chip_id`)
**Why:** `eprom_get_chip_id` already implements the A9-12V hardware sequence the AT28C datasheets specify; the new helper is a peer that derives the read addresses from `handle->mem_size` (per AT28C256 = 0x7FC0/0x7FC1, AT28C64 = 0x1FC0/0x1FC1). `flash_intel_check_chip_id`'s response/compare shape (packing, FORCE-flag handling, message literal) is the project's standard chip-id-mismatch surface.

**Excerpt to mirror — A9-12V read mechanism** (`firestarter/src/proms/eprom.cpp:186-197`):
```c
uint16_t eprom_get_chip_id(firestarter_handle_t* handle) {
    debug("Get chip ID");
    handle->firestarter_set_control_register(handle, REGULATOR, 1);
    delay(50);
    handle->firestarter_set_control_register(handle, A9_VPP_ENABLE, 1);
    delay(100);
    uint16_t chip_id = handle->firestarter_get_data(handle, 0x0000) << 8;
    chip_id |= (handle->firestarter_get_data(handle, 0x0001));
    handle->firestarter_set_control_register(handle, REGULATOR | A9_VPP_ENABLE, 0);
    return chip_id;
}
```

**Excerpt to mirror — compare + response** (`firestarter/src/proms/flash_intel.cpp:115-124`):
```c
void flash_intel_check_chip_id(firestarter_handle_t* handle) {
    handle->firestarter_set_data(handle, 0, 0x90);
    uint16_t chip_id = handle->firestarter_get_data(handle, 0x0000) << 8;
    chip_id |= handle->firestarter_get_data(handle, 0x0001);
    handle->firestarter_set_data(handle, 0, 0xFF);
    if (chip_id != handle->chip_id) {
        int response_code = is_flag_set(FLAG_FORCE) ? RESPONSE_CODE_WARNING : RESPONSE_CODE_ERROR;
        firestarter_response_format(response_code, "Chip ID %#04x dont match expected ID %#04x", chip_id, handle->chip_id);
    }
}
```

**Target shape** (new static in `eeprom_28c.cpp`, before `eeprom28c_write_init` at line 49; per RESEARCH.md Code Examples lines 505-519):
```c
static void eeprom28c_check_chip_id(firestarter_handle_t* handle) {
    debug("Check chip ID (28C)");
    handle->firestarter_set_control_register(handle, REGULATOR, 1);
    delay(50);
    handle->firestarter_set_control_register(handle, A9_VPP_ENABLE, 1);
    delay(100);
    uint32_t mfr_addr = handle->mem_size - 64;  // 0x7FC0 (AT28C256) / 0x1FC0 (AT28C64) / ...
    uint16_t chip_id = handle->firestarter_get_data(handle, mfr_addr) << 8;
    chip_id |= handle->firestarter_get_data(handle, mfr_addr + 1);
    handle->firestarter_set_control_register(handle, REGULATOR | A9_VPP_ENABLE, 0);
    if (chip_id != handle->chip_id) {
        int response_code = is_flag_set(FLAG_FORCE) ? RESPONSE_CODE_WARNING : RESPONSE_CODE_ERROR;
        firestarter_response_format(response_code, "Chip ID %#04x dont match expected ID %#04x", chip_id, handle->chip_id);
    }
}
```

**Anti-patterns to avoid:**
- Do NOT implement the CONTEXT.md D-05 JEDEC sequence (`0xAA→0x5555, 0x55→0x2AAA, 0x90→0x5555`) — RESEARCH.md proves this is the AMD/SST convention; AT28C datasheets do NOT support software autoselect. Implementing it would silently corrupt address 0x5555 on SDP-disabled parts (RESEARCH.md AT28C JEDEC sequence verification).
- Do NOT introduce a `byte_flip_t` table for chip-id (would be needed only for Option B, which is rejected — see RESEARCH.md Reuse Audit row 3).
- Do NOT add a declaration to `eeprom_28c.h` — `static` internal linkage only.
- Do NOT add `#include "rurp_shield.h"` if already transitively available; current `eeprom_28c.cpp` does NOT directly include it — verify the `REGULATOR` / `A9_VPP_ENABLE` symbols resolve via `firestarter.h` or add the include if needed. (`flash_intel.cpp:16` includes `rurp_shield.h` directly; mirror that if the compiler complains.)
- Do NOT preserve `handle->vpp_mv` mutation during the read — `eprom_get_chip_id` does not touch `vpp_mv`; the regulator runs at its calibrated default. (RESEARCH.md Open Question 3 flags this as a planning-time investigation item, not a coding constraint.)
- Do NOT keep the literal `"Chip ID %#04x dont match expected ID %#04x"` — that is the literal to USE; verbatim from `flash_intel_check_chip_id:122`, per CONTEXT.md D-07.

---

### `firestarter/src/proms/eeprom_28c.cpp` — call-site in `eeprom28c_write_init`

**Role:** firmware-handler-edit (insert chip-id check BEFORE the SDP-disable per RESEARCH.md D-08 recommendation — fail-fast on identity before mutating chip state)
**Analog:** `firestarter/src/proms/flash_intel.cpp:47-62` (chip-id-then-action ordering) + `firestarter/src/proms/eprom.cpp:250-258` (gated on `chip_id > 0`)
**Why:** Both v1.0 init paths check identity before any state mutation. SDP-disable is a state mutation (the chip transitions out of write-protect); a mismatch should leave the chip in its protected state.

**Excerpt to mirror — gating + early-return** (`firestarter/src/proms/flash_intel.cpp:50-55`):
```c
if (handle->chip_id > 0) {
    flash_intel_check_chip_id(handle);
    if (handle->response_code == RESPONSE_CODE_ERROR) {
        return;
    }
}
```

**Current state at edit site** (`firestarter/src/proms/eeprom_28c.cpp:45-57`):
```c
void eeprom28c_write_init(firestarter_handle_t* handle) {
    flash_execute_command(EEPROM_SDP_DISABLE);              // <-- insert chip-id check BEFORE this
    if (!eeprom28c_wait_for_write(handle, 0x5555, 0x20)) {
        return;
    }
    if (!is_flag_set(FLAG_SKIP_BLANK_CHECK)) {
        mem_util_blank_check(handle);
    }
}
```

**Target shape** (per RESEARCH.md D-08 diff):
```c
void eeprom28c_write_init(firestarter_handle_t* handle) {
    if (handle->chip_id > 0) {
        eeprom28c_check_chip_id(handle);
        if (handle->response_code == RESPONSE_CODE_ERROR) {
            return;
        }
    }
    flash_execute_command(EEPROM_SDP_DISABLE);
    if (!eeprom28c_wait_for_write(handle, 0x5555, 0x20)) {
        return;
    }
    if (!is_flag_set(FLAG_SKIP_BLANK_CHECK)) {
        mem_util_blank_check(handle);
    }
}
```

**Anti-patterns to avoid:**
- Do NOT insert the chip-id check AFTER `flash_execute_command(EEPROM_SDP_DISABLE)` — leaves the chip with SDP cleared on mismatch (worse safety posture; see RESEARCH.md D-08 "Why NOT after SDP-disable").
- Do NOT skip the `chip_id > 0` guard — matches `flash_intel_write_init:50` pattern; `chip_id == 0` means "no expected ID, skip the check".
- Do NOT call `eeprom28c_wait_for_write` after the chip-id read — A9-12V identification is immediate, no polling needed (`eprom_get_chip_id` has no wait either).
- Do NOT keep `mem_util_blank_check` from running on mismatch — the early `return` on `RESPONSE_CODE_ERROR` ensures it doesn't.

---

### `firestarter/test/native/avr/test_flash_intel_vpp/test_flash_intel_vpp.cpp`

**Role:** native-unity-suite (Unity test bodies + `main` for SAF-04 / SAF-06)
**Analog:** `firestarter/test/native/avr/test_dispatch/test_configure_memory.cpp` (skeleton: includes, `using namespace fakeit`, `setUp`/`tearDown`, `make_handle` helper, `RUN_TEST` enumeration in `main`)
**Why:** This is the only existing native Unity suite. The skeleton (header includes, `extern "C" { #include ... }` for the C handler headers, ArduinoFake reset, zero-init handle helper, `UNITY_BEGIN`/`UNITY_END` `main`) is verbatim reusable.

**Excerpt to mirror — file skeleton** (`firestarter/test/native/avr/test_dispatch/test_configure_memory.cpp:31-57`):
```c
#include <Arduino.h>
#include <ArduinoFake.h>
#include <unity.h>

extern "C" {
#include "memory.h"
}
#include "firestarter.h"

using namespace fakeit;

void setUp(void) {
    ArduinoFakeReset();
}

void tearDown(void) {
}

/* Build a zero-initialized handle with only the three named fields set. */
static firestarter_handle_t make_handle(uint32_t protocol, uint8_t mem_type, uint8_t cmd) {
    firestarter_handle_t h = {};
    h.protocol = protocol;
    h.mem_type = mem_type;
    h.cmd = cmd;
    h.response_code = RESPONSE_CODE_OK;
    return h;
}
```

**Excerpt to mirror — `main` enumeration** (`firestarter/test/native/avr/test_dispatch/test_configure_memory.cpp:157-182`):
```c
int main(int argc, char** argv) {
    (void)argc;
    (void)argv;
    UNITY_BEGIN();
    RUN_TEST(test_protocol_0x06_dispatches_flash3);
    /* ... */
    RUN_TEST(test_protocol_zero_with_mem_type_eprom_dispatches_eprom);
    return UNITY_END();
}
```

**Target shape — handle builder + tests** (per RESEARCH.md Code Examples lines 527-621):
```c
extern "C" {
#include "flash_intel.h"
#include "memory.h"
}
#include "firestarter.h"

// Declared in this suite's host_stubs.cpp; used to inject mock VPP / hw rev.
extern "C" void set_mock_vpp_mv(uint16_t mv);
extern "C" void set_mock_hw_rev(uint8_t rev);

static void mock_set_ctrl_reg(struct firestarter_handle*, rurp_register_t, bool) {}
static bool mock_get_ctrl_reg(struct firestarter_handle*, rurp_register_t) { return 0; }
static void mock_set_data(struct firestarter_handle*, uint32_t, uint8_t) {}
static uint8_t mock_get_data(struct firestarter_handle*, uint32_t) { return 0xFF; }

void setUp(void) {
    ArduinoFakeReset();
    set_mock_vpp_mv(0);
    set_mock_hw_rev(1);  // non-REV0 default
}
void tearDown(void) {}

static firestarter_handle_t make_intel_handle(uint16_t vpp_setpoint, uint32_t ctrl_flags) {
    firestarter_handle_t h = {};
    h.protocol = 0x10;
    h.cmd = CMD_WRITE;
    h.response_code = RESPONSE_CODE_OK;
    h.vpp_mv = vpp_setpoint;
    h.ctrl_flags = ctrl_flags | FLAG_SKIP_BLANK_CHECK | FLAG_SKIP_ERASE;
    h.chip_id = 0;  // skip chip-id branch
    h.firestarter_set_control_register = mock_set_ctrl_reg;
    h.firestarter_get_control_register = mock_get_ctrl_reg;
    h.firestarter_set_data = mock_set_data;
    h.firestarter_get_data = mock_get_data;
    return h;
}

// Tests (one assertion per test):
// test_flash_intel_vpp_nominal_proceeds   -> set_mock_vpp_mv(12000), assert NOT_EQUAL ERROR
// test_flash_intel_low_vpp_warns          -> set_mock_vpp_mv(11000), assert EQUAL WARNING
// test_flash_intel_high_vpp_errors        -> set_mock_vpp_mv(12700), assert EQUAL ERROR
// test_flash_intel_high_vpp_with_force_warns -> ctrl_flags |= FLAG_FORCE + 12700, assert EQUAL WARNING
// test_flash_intel_rev0_skips_vpp_check   -> set_mock_hw_rev(0) + impossible vpp, assert NOT_EQUAL ERROR

int main(int, char**) {
    UNITY_BEGIN();
    RUN_TEST(test_flash_intel_vpp_nominal_proceeds);
    RUN_TEST(test_flash_intel_low_vpp_warns);
    RUN_TEST(test_flash_intel_high_vpp_errors);
    RUN_TEST(test_flash_intel_high_vpp_with_force_warns);
    RUN_TEST(test_flash_intel_rev0_skips_vpp_check);
    return UNITY_END();
}
```

**Anti-patterns to avoid:**
- Do NOT call `flash_intel_write_init(&h)` directly — always go through `configure_memory(&h); h.firestarter_operation_init(&h);` (RESEARCH.md Pitfall 2).
- Do NOT assert `RESPONSE_CODE_ERROR` for the low-VPP case — low VPP emits `RESPONSE_CODE_WARNING` (RESEARCH.md Pitfall 3, CONTEXT.md D-01).
- Do NOT omit `FLAG_SKIP_BLANK_CHECK | FLAG_SKIP_ERASE` from the handle — otherwise `mem_util_blank_check` / `flash_intel_erase_execute` runs against the mock and the test sees spurious response_codes (RESEARCH.md Pitfall 5).
- Do NOT mock `rurp_read_voltage_mv` inside this TU — that causes a multiple-definition link error with the suite's `host_stubs.cpp`. Mock-state setters (`set_mock_vpp_mv`) live in `host_stubs.cpp` and are called from here (RESEARCH.md Pitfall 1).
- Do NOT edit `test_dispatch/host_stubs.cpp` or `test_dispatch/test_configure_memory.cpp` — D-10 / D-11 forbid it.

---

### `firestarter/test/native/avr/test_flash_intel_vpp/host_stubs.cpp`

**Role:** native-test-stubs (suite-local — independent binary per PIO `test/<dir>/` convention; safe to define mock-state setters here)
**Analog:** `firestarter/test/native/avr/test_dispatch/host_stubs.cpp` — verbatim copy EXCEPT `rurp_read_voltage_mv` and `rurp_get_hardware_revision` which become mockable.
**Why:** PIO builds each `test/<dir>/` directory as its own independent binary (RESEARCH.md A4, confirmed by `firestarter/CLAUDE.md` "Reuse pattern for future native tests"). So a per-suite `host_stubs.cpp` can provide stronger definitions of `rurp_*` symbols without conflicting with the dispatch suite. This is the load-bearing PIO insight.

**Excerpt to mirror — full file** (`firestarter/test/native/avr/test_dispatch/host_stubs.cpp:1-160`): copy verbatim; the only edits are:

1. Replace `rurp_read_voltage_mv` (line 97-99 in analog):
```c
// BEFORE (verbatim from dispatch suite):
extern "C" uint16_t rurp_read_voltage_mv() {
    return 0;
}
```
```c
// AFTER (suite-local mockable):
static uint16_t s_mock_vpp_mv = 0;
extern "C" void set_mock_vpp_mv(uint16_t mv) { s_mock_vpp_mv = mv; }
extern "C" uint16_t rurp_read_voltage_mv() { return s_mock_vpp_mv; }
```

2. Replace `rurp_get_hardware_revision` (inside `#ifdef HARDWARE_REVISION` block at lines 110-124 of analog):
```c
// BEFORE (verbatim from dispatch suite):
extern "C" uint8_t rurp_get_hardware_revision() {
    return 0;
}
```
```c
// AFTER (suite-local mockable):
static uint8_t s_mock_hw_rev = 1;
extern "C" void set_mock_hw_rev(uint8_t r) { s_mock_hw_rev = r; }
extern "C" uint8_t rurp_get_hardware_revision() { return s_mock_hw_rev; }
```

All other stubs (LOG_*_MSG PROGMEM strings, `rurp_log`, `rurp_write_to_register`, `rurp_set_data_output`, `rurp_read_vcc_mv`, `rurp_board_setup`, `rurp_load_config`, `rurp_get_config`, communication API, etc.) — copied byte-for-byte from `test_dispatch/host_stubs.cpp`.

**Anti-patterns to avoid:**
- Do NOT touch `test_dispatch/host_stubs.cpp` (D-10 — must remain byte-identical).
- Do NOT use `extern` mutable globals (`extern uint16_t s_mock_vpp_mv;`) — the test TU should call the `set_mock_*` setter functions, not access the static directly. This keeps the static genuinely TU-private.
- Do NOT skip the `#ifdef HARDWARE_REVISION` guard around `set_mock_hw_rev` / `rurp_get_hardware_revision` overrides — REV0 test only compiles under that flag (RESEARCH.md A5 confirms `-D HARDWARE_REVISION` is in the shared `[env]` block, so the flag IS on for `[env:native]`; the guard preserves portability if that ever changes).
- Do NOT add new `rurp_*` symbols beyond what the analog has — if the proms TUs the new suite links reference anything more, copy the analog stub for it; do not introduce novel behaviour.

---

### `firestarter/test/native/avr/test_flash_intel_vpp/avr/pgmspace.h`

**Role:** pgm-shim (host-side neutralization of AVR PROGMEM macros for `<avr/pgmspace.h>` includes)
**Analog:** `firestarter/test/native/avr/test_dispatch/avr/pgmspace.h` — copy verbatim.
**Why:** `rurp_shield.h` unconditionally `#include <avr/pgmspace.h>` (see analog file header comment). On native this would fail; the shim resolves `PROGMEM`, `PSTR`, `PGM_P`, `pgm_read_*`, `strcpy_P`, `strlen_P`, `memcpy_P` as host-memory equivalents.

**Excerpt to mirror — full file** (`firestarter/test/native/avr/test_dispatch/avr/pgmspace.h:1-63`): copy verbatim — no edits needed. The file is 63 lines, completely self-contained.

**Anti-patterns to avoid:**
- Do NOT symlink to the dispatch suite's copy — physical copy is simpler and matches the "each test directory is its own binary" convention.
- Do NOT modify the include guard (`_AVR_PGMSPACE_H_STUB_`) — keeping the same guard across copies is fine; each TU compiles its own pre-processor pass.

---

### `firestarter/test/native/avr/test_eeprom28c_chip_id/test_eeprom28c_chip_id.cpp`

**Role:** native-unity-suite (Unity test bodies + `main` for SAF-05 / SAF-06; uses handle function-pointer mocking — no `rurp_*` overrides needed)
**Analog:** `firestarter/test/native/avr/test_dispatch/test_configure_memory.cpp` (skeleton) + RESEARCH.md Code Examples lines 642-726 (full sketch with scripted-byte mock)
**Why:** Same skeleton as the VPP suite. The novelty: chip-id read happens via `handle->firestarter_get_data(handle, addr)`, a function pointer ON the handle, so the test mocks it by setting the pointer — no link-time `rurp_*` override is needed (this is RESEARCH.md Option M2).

**Target shape** (per RESEARCH.md Code Examples lines 642-726):
```c
#include <Arduino.h>
#include <ArduinoFake.h>
#include <unity.h>
#include <string.h>

extern "C" {
#include "eeprom_28c.h"
#include "memory.h"
}
#include "firestarter.h"

using namespace fakeit;

// Scripted byte sequence — TU-private; mock_get_data_scripted serves bytes in order.
static uint8_t s_mock_bytes[16];
static int s_mock_byte_idx;

static void mock_set_ctrl_reg(struct firestarter_handle*, rurp_register_t, bool) {}
static bool mock_get_ctrl_reg(struct firestarter_handle*, rurp_register_t) { return 0; }
static void mock_set_data(struct firestarter_handle*, uint32_t, uint8_t) {}
static uint8_t mock_get_data_scripted(struct firestarter_handle*, uint32_t /*addr*/) {
    if (s_mock_byte_idx < (int)sizeof(s_mock_bytes)) return s_mock_bytes[s_mock_byte_idx++];
    return 0xFF;
}

void setUp(void) {
    ArduinoFakeReset();
    s_mock_byte_idx = 0;
    memset(s_mock_bytes, 0xFF, sizeof(s_mock_bytes));
}
void tearDown(void) {}

static firestarter_handle_t make_28c_handle(uint16_t expected_chip_id, uint32_t ctrl_flags) {
    firestarter_handle_t h = {};
    h.protocol = 0x0D;
    h.cmd = CMD_WRITE;
    h.mem_size = 32768;  // AT28C256 (mfr_addr = 0x7FC0)
    h.response_code = RESPONSE_CODE_OK;
    h.chip_id = expected_chip_id;
    h.ctrl_flags = ctrl_flags | FLAG_SKIP_BLANK_CHECK;
    h.firestarter_set_control_register = mock_set_ctrl_reg;
    h.firestarter_get_control_register = mock_get_ctrl_reg;
    h.firestarter_set_data = mock_set_data;
    h.firestarter_get_data = mock_get_data_scripted;
    return h;
}

// test_eeprom28c_matching_chip_id_proceeds   -> bytes={0x1F,0x08}, chip_id=0x1F08, assert NOT_EQUAL ERROR
// test_eeprom28c_mismatching_chip_id_errors  -> bytes={0xDE,0xAD}, chip_id=0x1F08, assert EQUAL ERROR
// test_eeprom28c_zero_chip_id_skips_check    -> chip_id=0, assert NOT_EQUAL ERROR && s_mock_byte_idx==0
// test_eeprom28c_mismatching_chip_id_with_force_warns -> FLAG_FORCE + mismatch, assert EQUAL WARNING

int main(int, char**) {
    UNITY_BEGIN();
    RUN_TEST(test_eeprom28c_matching_chip_id_proceeds);
    RUN_TEST(test_eeprom28c_mismatching_chip_id_errors);
    RUN_TEST(test_eeprom28c_zero_chip_id_skips_check);
    RUN_TEST(test_eeprom28c_mismatching_chip_id_with_force_warns);
    return UNITY_END();
}
```

**Anti-patterns to avoid:**
- Do NOT forget `h.mem_size = 32768` — the chip-id helper computes `mfr_addr = mem_size - 64`; zero gives `0xFFFFFFC0` which the mock will serve from (test passes for wrong reason, or fails confusingly). See RESEARCH.md Pitfall 4.
- Do NOT call `eeprom28c_write_init(&h)` directly — go through `configure_memory(&h); h.firestarter_operation_init(&h);` (RESEARCH.md Pitfall 2; matches dispatch test convention).
- Do NOT skip `FLAG_SKIP_BLANK_CHECK` — the mock returns 0xFF for unscripted reads, which happens to make blank-check pass, but relying on that is fragile.
- Do NOT define a setter like `set_mock_vpp_mv` here — the VPP suite needs that (link-time override of `rurp_read_voltage_mv`); the chip-id suite uses handle pointer mocking exclusively (RESEARCH.md Validation Architecture summary table).
- Do NOT use `FLAG_FORCE` in tests other than the FORCE-warn case — RESEARCH.md table shows one-flag-per-test.

---

### `firestarter/test/native/avr/test_eeprom28c_chip_id/host_stubs.cpp`

**Role:** native-test-stubs (suite-local, functionally identical to dispatch suite's — no mocking needed here; mocks happen in the test TU via handle function pointers)
**Analog:** `firestarter/test/native/avr/test_dispatch/host_stubs.cpp` — verbatim copy.
**Why:** PIO requires each `test/<dir>/` binary to link the `rurp_*` symbols the proms TUs reference. The dispatch suite's stubs provide every needed symbol; no edits required for the chip-id suite (Option M2 handles all mocking at the handle layer).

**Excerpt to mirror — full file** (`firestarter/test/native/avr/test_dispatch/host_stubs.cpp:1-160`): copy verbatim, no edits.

**Anti-patterns to avoid:**
- Do NOT introduce a `set_mock_chip_id_bytes` setter here — mocking happens via the handle's `firestarter_get_data` pointer in the test TU. Keeping this stubs file byte-identical to the dispatch suite's makes the "no link-time tricks" intent clear.
- Do NOT edit `test_dispatch/host_stubs.cpp` (D-10).

---

### `firestarter/test/native/avr/test_eeprom28c_chip_id/avr/pgmspace.h`

**Role:** pgm-shim (host neutralization of AVR PROGMEM)
**Analog:** `firestarter/test/native/avr/test_dispatch/avr/pgmspace.h` — copy verbatim, same 63-line file as the VPP suite's copy.

**Anti-patterns to avoid:** same as the VPP suite's pgmspace.h.

---

## Shared Patterns

### Init-time safety ordering (applies to both handler edits)
**Source:** `firestarter/src/proms/eprom.cpp:250-258` (`eprom_generic_init`)
**Apply to:** `flash_intel_write_init` (SAF-04 call-site) and `eeprom28c_write_init` (SAF-05 call-site)
```c
// Canonical order: safety check → response_code check → next step.
safety_check(handle);
if (handle->response_code == RESPONSE_CODE_ERROR) {
    return;
}
```
For SAF-04 the safety check is `flash_intel_check_vpp`; for SAF-05 it is the gated `if (handle->chip_id > 0) { eeprom28c_check_chip_id(handle); ... }` block (mirrors `flash_intel_write_init:50-55`).

### FORCE-flag downgrade
**Source:** `firestarter/src/proms/flash_intel.cpp:121` and `firestarter/src/proms/eprom.cpp:222`
**Apply to:** Both new helpers (`flash_intel_check_vpp` high-VPP branch, `eeprom28c_check_chip_id` mismatch branch)
```c
int response_code = is_flag_set(FLAG_FORCE) ? RESPONSE_CODE_WARNING : RESPONSE_CODE_ERROR;
firestarter_response_format(response_code, "<message format>", <args>);
```
Per CONTEXT.md D-07. The low-VPP branch in `flash_intel_check_vpp` always uses `firestarter_warning_response_format` (no FORCE downgrade needed — already a warning).

### Chip-id mismatch message literal (verbatim — do NOT regrammar)
**Source:** `firestarter/src/proms/flash_intel.cpp:122`
**Apply to:** `eeprom28c_check_chip_id`
```c
firestarter_response_format(response_code, "Chip ID %#04x dont match expected ID %#04x", chip_id, handle->chip_id);
```
Per CONTEXT.md D-07: "do NOT 'fix' the grammar — it would diverge from grep-able historical messages".

### REV0 hardware-revision guard (SAF-04 only)
**Source:** `firestarter/src/proms/eprom.cpp:201-206`
**Apply to:** `flash_intel_check_vpp` (mirror verbatim; not applicable to SAF-05 since AT28C is 5V-only)
```c
#ifdef HARDWARE_REVISION
    if (rurp_get_hardware_revision() == REVISION_0) {
        firestarter_warning_response("Rev0 dont support reading VPP/VPE");
        return;
    }
#endif
```

### Test handle skeleton
**Source:** `firestarter/test/native/avr/test_dispatch/test_configure_memory.cpp:50-57` (`make_handle`)
**Apply to:** Both new test TUs (`make_intel_handle`, `make_28c_handle`)
- Zero-initialize with `firestarter_handle_t h = {};`
- Set `response_code = RESPONSE_CODE_OK` explicitly.
- Set the handle's function pointers to TU-private static no-op or scripted mocks BEFORE calling `configure_memory(&h)`.
- Always set `FLAG_SKIP_BLANK_CHECK` (and `FLAG_SKIP_ERASE` for Intel) to keep the init flow focused on the safety check under test.
- Always call `configure_memory(&h); h.firestarter_operation_init(&h);` — never call the init function directly (RESEARCH.md Pitfall 2).

### PIO test-suite isolation (mocking strategy)
**Source:** `firestarter/CLAUDE.md` §"Native (Host) Test Environment" — "drop test_*.cpp files under test/native/avr/<dirname>/; extend host_stubs.cpp only if the new test references additional rurp_* symbols"
**Apply to:** All three new test directories
- Each `test/<dirname>/` is an independent binary. PIO does NOT cross-link `host_stubs.cpp` between suites.
- SAF-04 (`test_flash_intel_vpp/`): per-suite `host_stubs.cpp` provides mockable `rurp_read_voltage_mv` + `rurp_get_hardware_revision` (Option M1 — link-time strong override).
- SAF-05 (`test_eeprom28c_chip_id/`): per-suite `host_stubs.cpp` is byte-identical to dispatch's; mocking happens via `handle->firestarter_get_data` pointer in the test TU (Option M2 — handle-pointer override).

---

## No Analog Found

None. Every Phase-1 file has a strong analog in the existing codebase.

---

## Metadata

**Analog search scope:** `firestarter/src/proms/`, `firestarter/test/native/avr/`, `firestarter/include/`
**Files scanned:**
- `firestarter/src/proms/eprom.cpp` (lines 180-280; `eprom_check_vpp`, `eprom_get_chip_id`, `eprom_generic_init`, `eprom_internal_check_chip_id`)
- `firestarter/src/proms/flash_intel.cpp` (full 125 lines)
- `firestarter/src/proms/eeprom_28c.cpp` (full 91 lines)
- `firestarter/test/native/avr/test_dispatch/test_configure_memory.cpp` (full 183 lines)
- `firestarter/test/native/avr/test_dispatch/host_stubs.cpp` (full 160 lines)
- `firestarter/test/native/avr/test_dispatch/avr/pgmspace.h` (full 63 lines)
- `firestarter/include/firestarter.h` (lines 40-108; handle struct + flags + response codes)
- `firestarter/CLAUDE.md` (Native Test Environment section)

**Pattern extraction date:** 2026-05-11

**Per-plan task `<read_first>` payload — ready-to-paste references:**

| Task | Files to read before coding |
|------|------------------------------|
| SAF-04 helper + call-site | `firestarter/src/proms/eprom.cpp:186-258`, `firestarter/src/proms/flash_intel.cpp:1-65` |
| SAF-05 helper + call-site | `firestarter/src/proms/eprom.cpp:186-197`, `firestarter/src/proms/flash_intel.cpp:47-62, 115-124`, `firestarter/src/proms/eeprom_28c.cpp:1-90` |
| SAF-06 VPP suite | `firestarter/test/native/avr/test_dispatch/test_configure_memory.cpp`, `firestarter/test/native/avr/test_dispatch/host_stubs.cpp`, `firestarter/test/native/avr/test_dispatch/avr/pgmspace.h`, RESEARCH.md Code Examples lines 527-640 |
| SAF-06 chip-id suite | `firestarter/test/native/avr/test_dispatch/test_configure_memory.cpp`, `firestarter/test/native/avr/test_dispatch/host_stubs.cpp`, RESEARCH.md Code Examples lines 642-726 |
