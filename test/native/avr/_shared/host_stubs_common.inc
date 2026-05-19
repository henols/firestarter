/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 *
 * Shared host-stub implementations for the [env:native] test suites.
 *
 * Phase 6 WR-06: this file consolidates the ~120 lines of `rurp_*` no-op
 * stubs, `LOG_*_MSG` PROGMEM strings, and the `Serial_::operator bool()`
 * link-only definition that previously lived (duplicated) in every per-suite
 * `host_stubs.cpp`. When a new `rurp_*` symbol is added to the firmware,
 * this is now the single edit point — suite-specific `host_stubs.cpp` files
 * only carry their unique mock state.
 *
 * Inclusion model: this file is `.inc`, not `.cpp` — each suite's
 * `host_stubs.cpp` `#include`s it once with a relative path. There is no
 * shared-TU link step, so multiple test binaries compile their own copy
 * (which is exactly what we want: each binary is a single statically-linked
 * artifact and never sees a sibling suite's stubs).
 *
 * Per-suite opt-outs (define BEFORE including this file):
 *   - HOST_STUBS_CUSTOM_VOLTAGE_MV   — suite provides its own
 *                                      rurp_read_voltage_mv (e.g.,
 *                                      test_flash_intel_vpp mocks it).
 *   - HOST_STUBS_CUSTOM_HW_REVISION  — suite provides its own
 *                                      rurp_get_hardware_revision (e.g.,
 *                                      test_flash_intel_vpp mocks it).
 *
 * Scope: only compiled into [env:native] via PIO's automatic discovery of
 * files under test/. Production builds (env:uno, env:leonardo) never see
 * this file because their src_filter excludes test/.
 *
 * Behavioural contract: every stub here is intentionally a no-op (or
 * returns 0). The dispatch tests only verify that configure_memory()
 * routes to the correct configure_*() function — they never assert on
 * hardware-register side effects. If a future test starts caring about
 * register writes, the stubs can grow to record calls; today they are
 * deliberately minimal.
 */

/* rurp_shield register I/O — the dispatch path's only direct hardware use
 * is mem_util_set_address(handle, 0) -> rurp_write_to_register(...). Stub it
 * so the call resolves and returns. */
extern "C" void rurp_write_to_register(uint8_t reg, rurp_register_t data) {
    (void)reg;
    (void)data;
}

extern "C" rurp_register_t rurp_read_from_register(uint8_t reg) {
    (void)reg;
    return 0;
}

/* Chip / data bus helpers — referenced (transitively) by the proms TUs that
 * the [env:native] build links in. None are invoked by the dispatch test's
 * call path, but they must resolve at link time. */
extern "C" void rurp_set_control_pin(uint8_t pin, uint8_t state) {
    (void)pin;
    (void)state;
}

extern "C" void rurp_set_data_output() {}
extern "C" void rurp_set_data_input() {}

extern "C" void rurp_write_data_buffer(uint8_t data) {
    (void)data;
}

extern "C" uint8_t rurp_read_data_buffer() {
    return 0;
}

extern "C" uint16_t rurp_read_vcc_mv() {
    return 5000;
}

#ifndef HOST_STUBS_CUSTOM_VOLTAGE_MV
extern "C" uint16_t rurp_read_voltage_mv() {
    return 0;
}
#endif

extern "C" long rurp_get_bandgap_adc_reading() {
    return 0;
}

extern "C" uint8_t rurp_user_button_pressed() {
    return 0;
}

/* Hardware revision / config — referenced by some proms; return safe defaults. */
#ifdef HARDWARE_REVISION
extern "C" void rurp_detect_hardware_revision() {}

#ifndef HOST_STUBS_CUSTOM_HW_REVISION
extern "C" uint8_t rurp_get_hardware_revision() {
    return 0;
}
#endif

extern "C" uint8_t rurp_get_physical_hardware_revision() {
    return 0;
}

extern "C" uint8_t rurp_map_ctrl_reg_for_hardware_revision(rurp_register_t data) {
    return (uint8_t)data;
}
#endif

extern "C" void rurp_board_setup() {}
extern "C" void rurp_load_config() {}

static rurp_configuration_t s_host_config = {};
extern "C" rurp_configuration_t* rurp_get_config() {
    return &s_host_config;
}

extern "C" void rurp_save_config(rurp_configuration_t* config) {
    (void)config;
}

extern "C" void rurp_validate_config(rurp_configuration_t* config) {
    (void)config;
}

/* Communication API — Phase 6 widened the [env:native] src_filter to pull
 * src/boards/rurp_serial_utils.cpp into the test binary (so test_messages
 * can exercise the real frame emitter end-to-end). That TU provides the
 * production rurp_communication_* implementations, so the dispatch suite no
 * longer needs to stub them. Intentionally NOT defined here. */

/* ArduinoFake declares Serial_::operator bool() in its USB-CDC header but
 * does not define it in SerialFake.cpp. rurp_serial_utils.cpp's
 * rurp_serial_begin loop `while (!SERIAL_PORT) ...` references the operator,
 * and the test binary pulls rurp_serial_utils.cpp into the link, so we
 * provide a host-side definition that returns true (matches production
 * HardwareSerial::operator bool() behaviour). The dispatch tests never call
 * rurp_serial_begin — this is link-only. */
#include <Arduino.h>
Serial_::operator bool() {
    return true;
}
