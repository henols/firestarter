/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 *
 * Phase 12 Wave 1 — host stub TU for the [env:native] dispatch test build.
 *
 * Compiling firmware sources (src/proms/*.cpp) on platform = native leaves
 * the linker hungry for hardware-side symbols defined in the AVR-only TUs
 * (src/boards/*.cpp, src/logging.c). This TU provides no-op host
 * implementations of every rurp_* symbol the proms reference, plus the
 * PROGMEM log-tag globals from src/logging.c, so the dispatch test binary
 * can link.
 *
 * Scope: only compiled into [env:native] via PIO's automatic discovery of
 * files under test/. Production builds (env:uno, env:leonardo) never see
 * this file because their src_filter excludes test/.
 *
 * Behavioural contract: every stub is intentionally a no-op (or returns 0).
 * The dispatch tests only verify that configure_memory() routes to the
 * correct configure_*() function — they never assert on hardware-register
 * side effects. If a future test starts caring about register writes, the
 * stubs can grow to record calls; today they are deliberately minimal.
 */

#include <stdint.h>
#include <stddef.h>
#include <string.h>

extern "C" {
#include "rurp_shield.h"
#include "rurp_types.h"
}

/* PROGMEM log-tag strings — defined in src/logging.c on AVR; replicated here
 * so the [env:native] link finds them. The PSTR() macro in the pgmspace stub
 * is a no-op, so these are plain const char[] in the host binary. */
extern "C" {
const char LOG_OK_MSG[] PROGMEM = "OK";
const char LOG_INIT_DONE_MSG[] PROGMEM = "INIT";
const char LOG_MAIN_DONE_MSG[] PROGMEM = "MAIN";
const char LOG_END_DONE_MSG[] PROGMEM = "END";
const char LOG_INFO_MSG[] PROGMEM = "INFO";
const char LOG_DATA_MSG[] PROGMEM = "DATA";
const char LOG_WARN_MSG[] PROGMEM = "WARN";
const char LOG_ERROR_MSG[] PROGMEM = "ERROR";
}

/* rurp_log* — no-op on host. The dispatch test never reads serial output. */
extern "C" void rurp_log(PGM_P type, const char* msg) {
    (void)type;
    (void)msg;
}

extern "C" void rurp_log_P(PGM_P type, PGM_P msg) {
    (void)type;
    (void)msg;
}

/* rurp_shield register I/O — the dispatch path's only direct hardware use
 * is mem_util_set_address(handle, 0) → rurp_write_to_register(...). Stub it
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
 * the [env:native] build now links in. None are invoked by the dispatch
 * test's call path, but they must resolve at link time. */
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

extern "C" uint16_t rurp_read_voltage_mv() {
    return 0;
}

extern "C" long rurp_get_bandgap_adc_reading() {
    return 0;
}

extern "C" uint8_t rurp_user_button_pressed() {
    return 0;
}

/* Hardware revision / config — referenced by some proms; return safe defaults. */
#ifdef HARDWARE_REVISION
extern "C" void rurp_detect_hardware_revision() {}

extern "C" uint8_t rurp_get_hardware_revision() {
    return 0;
}

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

/* Communication API — proms TUs don't call these directly, but other firmware
 * sources we may pull in via the same src_filter might. Cheap no-ops. */
extern "C" int rurp_communication_available() { return 0; }
extern "C" int rurp_communication_read() { return -1; }
extern "C" int rurp_communication_peak() { return -1; }
extern "C" size_t rurp_communication_write(const char* buffer, size_t size) {
    (void)buffer;
    return size;
}
extern "C" size_t rurp_communication_read_bytes(char* buffer, size_t length) {
    (void)buffer;
    (void)length;
    return 0;
}
extern "C" int rurp_communication_read_data(char* buffer) {
    (void)buffer;
    return 0;
}
