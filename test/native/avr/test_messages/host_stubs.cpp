/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 *
 * Phase 6 — host stub TU for the [env:native] test_messages test build.
 *
 * test_messages stubs the host-side AVR-only symbols that
 * boards/rurp_serial_utils.cpp + messages.c indirectly reference. The
 * widened [env:native] src_filter pulls those two real TUs into the test
 * binary so the production CRC8 table, MAGIC_PREAMBLE, _firestarter_emit_frame,
 * and PROGMEM MSG_PARAM_BYTES_TABLE are exercised end-to-end.
 *
 * Scope: only compiled into [env:native] via PIO's automatic discovery of
 * files under test/. Production builds (env:uno, env:leonardo) never see
 * this file because their src_filter excludes test/.
 *
 * Symbols stubbed:
 *  - rurp_log / rurp_log_P (transitively referenced via logging.h includes
 *    from rurp_serial_utils.cpp's __attribute__((weak)) defaults; never
 *    invoked by the test, but must link).
 *  - LOG_*_MSG PROGMEM strings (declared `extern` by logging.h; defined in
 *    src/logging.c on AVR; not linked here so we replicate them).
 *  - rurp_* hardware symbols (just in case the linker pulls them).
 */

#include <stdint.h>
#include <stddef.h>
#include <string.h>

#include <Arduino.h>
#include <ArduinoFake.h>

extern "C" {
#include "rurp_shield.h"
#include "rurp_types.h"
}

/* ArduinoFake declares Serial_::operator bool() in its USB-CDC header but
 * does not define it in SerialFake.cpp (commented out). rurp_serial_utils.cpp's
 * rurp_serial_begin loop `while (!SERIAL_PORT) ...` references the operator,
 * so we provide a host-side definition that returns true (matches the
 * production HardwareSerial::operator bool() behaviour). The test never
 * calls rurp_serial_begin — this is link-only. */
Serial_::operator bool() {
    return true;
}

/* PROGMEM log-tag strings — defined in src/logging.c on AVR; replicated here
 * so the [env:native] link finds them. PSTR()/PROGMEM are no-ops in the
 * pgmspace stub, so these are plain const char[] in the host binary. */
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

/* rurp_log* — text-frame helpers. Not exercised by these tests; the real
 * rurp_log_id under test goes through the binary frame emitter. Provided as
 * no-op stubs so the link resolves any transitive reference from the
 * widened src_filter (boards/rurp_serial_utils.cpp's weak defaults call
 * _firestarter_log_ram/_firestarter_log_progmem which exist in the same TU). */
extern "C" void rurp_log(PGM_P type, const char* msg) {
    (void)type;
    (void)msg;
}

extern "C" void rurp_log_P(PGM_P type, PGM_P msg) {
    (void)type;
    (void)msg;
}

/* rurp_shield hardware stubs — referenced transitively by the widened
 * src_filter (+<proms/>) since this test build links the same proms TUs as
 * test_dispatch. Mirror test_dispatch/host_stubs.cpp's stubs exactly. */
extern "C" void rurp_write_to_register(uint8_t reg, rurp_register_t data) {
    (void)reg;
    (void)data;
}

extern "C" rurp_register_t rurp_read_from_register(uint8_t reg) {
    (void)reg;
    return 0;
}

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
