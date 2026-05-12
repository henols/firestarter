/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 *
 * Phase 1 Plan 01-02 — SAF-05 / SAF-06 Unity tests for eeprom28c_write_init
 * A9-12V chip-id safety check.
 *
 * Four test cases exercise the eeprom28c_check_chip_id static helper (added in
 * Task 2) via the canonical dispatch path: configure_memory() → operation_init.
 * Mock chip-id bytes are injected through the handle's firestarter_get_data
 * function pointer (Option M2 — no link-time rurp_* overrides needed).
 *
 * Wave 0 state (Task 1): test bodies are empty stubs — they compile, link, and
 * trivially PASS. Task 2 fills the bodies with assertions and wires the
 * production code check into eeprom28c_write_init.
 */

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

/* Scripted byte sequence — TU-private; mock_get_data_scripted serves bytes in order.
 * setUp() resets s_mock_byte_idx to 0 and fills s_mock_bytes with 0xFF.
 * Tests set s_mock_bytes[0], s_mock_bytes[1] before driving init. */
static uint8_t s_mock_bytes[16];
static int s_mock_byte_idx;

/* TU-private no-op / scripted function-pointer mocks for the handle. */
static void mock_set_ctrl_reg(struct firestarter_handle*, rurp_register_t, bool) {}
static bool mock_get_ctrl_reg(struct firestarter_handle*, rurp_register_t) { return 0; }
static void mock_set_data(struct firestarter_handle*, uint32_t, uint8_t) {}
static uint8_t mock_get_data_scripted(struct firestarter_handle*, uint32_t /*addr*/) {
    if (s_mock_byte_idx < (int)sizeof(s_mock_bytes)) return s_mock_bytes[s_mock_byte_idx++];
    return 0xFF;
}

void setUp(void) {
    ArduinoFakeReset();
    /* delay() is called by eeprom28c_check_chip_id (50ms + 100ms regulator settle).
     * ArduinoFake requires mock setup before a virtual is called or it aborts. */
    When(Method(ArduinoFake(), delay)).AlwaysReturn();
    s_mock_byte_idx = 0;
    memset(s_mock_bytes, 0xFF, sizeof(s_mock_bytes));
}

void tearDown(void) {
}

/*
 * Build a handle pre-wired for the AT28C EEPROM write path.
 * - protocol=0x0D routes to configure_eeprom28c → eeprom28c_write_init
 * - mem_size=32768 (AT28C256): mfr_addr = 32768 - 64 = 0x7FC0
 * - chip_id=expected_chip_id (non-zero enables the check; zero skips it)
 * - FLAG_SKIP_BLANK_CHECK prevents blank-check from running against the mock
 *   and polluting response_code
 */
static firestarter_handle_t make_28c_handle(uint16_t expected_chip_id, uint32_t ctrl_flags) {
    firestarter_handle_t h = {};
    h.protocol = 0x0D;
    h.cmd = CMD_WRITE;
    h.mem_size = 32768;  /* AT28C256 — mfr_addr = mem_size - 64 = 0x7FC0 */
    h.response_code = RESPONSE_CODE_OK;
    h.chip_id = expected_chip_id;
    h.ctrl_flags = ctrl_flags | FLAG_SKIP_BLANK_CHECK;
    h.firestarter_set_control_register = mock_set_ctrl_reg;
    h.firestarter_get_control_register = mock_get_ctrl_reg;
    h.firestarter_set_data = mock_set_data;
    h.firestarter_get_data = mock_get_data_scripted;
    return h;
}

/* Task 1 skeleton: empty bodies — trivially PASS.
 * Task 2 fills these with real assertions. */

void test_eeprom28c_matching_chip_id_proceeds(void) {
}

void test_eeprom28c_mismatching_chip_id_errors(void) {
}

void test_eeprom28c_zero_chip_id_skips_check(void) {
}

void test_eeprom28c_mismatching_chip_id_with_force_warns(void) {
}

int main(int, char**) {
    UNITY_BEGIN();
    RUN_TEST(test_eeprom28c_matching_chip_id_proceeds);
    RUN_TEST(test_eeprom28c_mismatching_chip_id_errors);
    RUN_TEST(test_eeprom28c_zero_chip_id_skips_check);
    RUN_TEST(test_eeprom28c_mismatching_chip_id_with_force_warns);
    return UNITY_END();
}
