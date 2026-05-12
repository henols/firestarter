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
 * Task 2: test bodies filled with real assertions; eeprom28c_check_chip_id
 * static helper wired into eeprom28c_write_init before EEPROM_SDP_DISABLE.
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

/*
 * Test: matching chip-id (mock bytes = {0x1F, 0x08}, handle.chip_id = 0x1F08).
 * Helper reads mfr_addr = 32768 - 64 = 0x7FC0 (returns 0x1F) and 0x7FC1
 * (returns 0x08), packs as 0x1F08, matches handle.chip_id — no error.
 * Init proceeds past SDP-disable; response_code must NOT be ERROR.
 */
void test_eeprom28c_matching_chip_id_proceeds(void) {
    s_mock_bytes[0] = 0x1F;
    s_mock_bytes[1] = 0x08;
    firestarter_handle_t h = make_28c_handle(0x1F08, 0);
    configure_memory(&h);
    h.firestarter_operation_init(&h);
    TEST_ASSERT_NOT_EQUAL(RESPONSE_CODE_ERROR, h.response_code);
}

/*
 * Test: mismatching chip-id (mock bytes = {0xDE, 0xAD}, handle.chip_id = 0x1F08).
 * Helper packs 0xDEAD, compares unequal — RESPONSE_CODE_ERROR set;
 * early-return fires before flash_execute_command(EEPROM_SDP_DISABLE).
 */
void test_eeprom28c_mismatching_chip_id_errors(void) {
    s_mock_bytes[0] = 0xDE;
    s_mock_bytes[1] = 0xAD;
    firestarter_handle_t h = make_28c_handle(0x1F08, 0);
    configure_memory(&h);
    h.firestarter_operation_init(&h);
    TEST_ASSERT_EQUAL(RESPONSE_CODE_ERROR, h.response_code);
}

/*
 * Test: chip_id == 0 — gate evaluates false, helper never called.
 * s_mock_byte_idx must remain 0 after init (no firestarter_get_data calls).
 * This asserts the gate, not the response_code.
 */
void test_eeprom28c_zero_chip_id_skips_check(void) {
    firestarter_handle_t h = make_28c_handle(0, 0);
    configure_memory(&h);
    h.firestarter_operation_init(&h);
    TEST_ASSERT_EQUAL(0, s_mock_byte_idx);
}

/*
 * Test: mismatching chip-id + FLAG_FORCE.
 * Same {0xDE, 0xAD} / 0x1F08 mismatch, but FLAG_FORCE set on ctrl_flags.
 * FORCE downgrade: RESPONSE_CODE_WARNING instead of RESPONSE_CODE_ERROR.
 */
void test_eeprom28c_mismatching_chip_id_with_force_warns(void) {
    s_mock_bytes[0] = 0xDE;
    s_mock_bytes[1] = 0xAD;
    firestarter_handle_t h = make_28c_handle(0x1F08, FLAG_FORCE);
    configure_memory(&h);
    h.firestarter_operation_init(&h);
    TEST_ASSERT_EQUAL(RESPONSE_CODE_WARNING, h.response_code);
}

int main(int, char**) {
    UNITY_BEGIN();
    RUN_TEST(test_eeprom28c_matching_chip_id_proceeds);
    RUN_TEST(test_eeprom28c_mismatching_chip_id_errors);
    RUN_TEST(test_eeprom28c_zero_chip_id_skips_check);
    RUN_TEST(test_eeprom28c_mismatching_chip_id_with_force_warns);
    return UNITY_END();
}
