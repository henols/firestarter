/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 *
 * Phase 1 Plan 01-01 — SAF-04 / SAF-06 Unity tests for flash_intel_write_init
 * VPP pre-pulse safety check.
 *
 * Five test cases exercise the flash_intel_check_vpp static helper (added in
 * Task 2) via the canonical dispatch path: configure_memory() → operation_init.
 * Mock VPP voltage and hardware revision are injected through suite-local
 * set_mock_vpp_mv() / set_mock_hw_rev() setters in host_stubs.cpp.
 *
 * Wave 0 state (Task 1): test bodies are empty stubs — they compile, link, and
 * trivially PASS. Task 2 fills the bodies with assertions and wires the
 * production code check into flash_intel_write_init.
 */

#include <Arduino.h>
#include <ArduinoFake.h>
#include <unity.h>

extern "C" {
#include "flash_intel.h"
#include "memory.h"
}
#include "firestarter.h"

using namespace fakeit;

/* Declared in this suite's host_stubs.cpp; called here to inject mock state. */
extern "C" void set_mock_vpp_mv(uint16_t mv);
extern "C" void set_mock_hw_rev(uint8_t rev);

/* TU-private no-op function-pointer mocks for the handle. */
static void mock_set_ctrl_reg(struct firestarter_handle*, rurp_register_t, bool) {}
static bool mock_get_ctrl_reg(struct firestarter_handle*, rurp_register_t) { return 0; }
static void mock_set_data(struct firestarter_handle*, uint32_t, uint8_t) {}
static uint8_t mock_get_data(struct firestarter_handle*, uint32_t) { return 0xFF; }

void setUp(void) {
    ArduinoFakeReset();
    /* delay() is called by flash_intel_write_init (500 ms regulator settle).
     * ArduinoFake requires mock setup before a virtual is called or it aborts. */
    When(Method(ArduinoFake(), delay)).AlwaysReturn();
    set_mock_vpp_mv(0);
    set_mock_hw_rev(1);  /* non-REV0 default */
}

void tearDown(void) {
}

/*
 * Build a handle pre-wired for the Intel-flash write path.
 * - protocol=0x10 routes to configure_flash_intel → flash_intel_write_init
 * - chip_id=0 skips the chip-id branch so only the VPP check is exercised
 * - FLAG_SKIP_BLANK_CHECK | FLAG_SKIP_ERASE prevent blank-check and erase
 *   from running against the mock and polluting response_code
 */
static firestarter_handle_t make_intel_handle(uint16_t vpp_setpoint, uint32_t ctrl_flags) {
    firestarter_handle_t h = {};
    h.protocol = 0x10;
    h.cmd = CMD_WRITE;
    h.response_code = RESPONSE_CODE_OK;
    h.vpp_mv = vpp_setpoint;
    h.ctrl_flags = ctrl_flags | FLAG_SKIP_BLANK_CHECK | FLAG_SKIP_ERASE;
    h.chip_id = 0;  /* skip chip-id branch */
    h.firestarter_set_control_register = mock_set_ctrl_reg;
    h.firestarter_get_control_register = mock_get_ctrl_reg;
    h.firestarter_set_data = mock_set_data;
    h.firestarter_get_data = mock_get_data;
    return h;
}

/*
 * Test: nominal VPP (12000 mV against setpoint 12000 mV) — within band, no error.
 * Tolerance band: low = 12000 * 95 / 100 = 11400; high = 12000 + 500 = 12500.
 * 12000 is between 11400 and 12500 → no response_code change.
 */
void test_flash_intel_vpp_nominal_proceeds(void) {
    set_mock_vpp_mv(12000);
    firestarter_handle_t h = make_intel_handle(12000, 0);
    configure_memory(&h);
    h.firestarter_operation_init(&h);
    TEST_ASSERT_NOT_EQUAL(RESPONSE_CODE_ERROR, h.response_code);
}

/*
 * Test: low VPP (11000 mV against setpoint 12000 mV) — below 95% of setpoint.
 * 11000 < 12000 * 95 / 100 = 11400 → firestarter_warning_response_format fires,
 * response_code = RESPONSE_CODE_WARNING. Init proceeds (low-VPP is warn-and-continue).
 */
void test_flash_intel_low_vpp_warns(void) {
    set_mock_vpp_mv(11000);
    firestarter_handle_t h = make_intel_handle(12000, 0);
    configure_memory(&h);
    h.firestarter_operation_init(&h);
    TEST_ASSERT_EQUAL(RESPONSE_CODE_WARNING, h.response_code);
}

/*
 * Test: high VPP (12700 mV against setpoint 12000 mV) — above setpoint + 500.
 * 12700 > 12000 + 500 = 12500 → RESPONSE_CODE_ERROR, early return.
 */
void test_flash_intel_high_vpp_errors(void) {
    set_mock_vpp_mv(12700);
    firestarter_handle_t h = make_intel_handle(12000, 0);
    configure_memory(&h);
    h.firestarter_operation_init(&h);
    TEST_ASSERT_EQUAL(RESPONSE_CODE_ERROR, h.response_code);
}

/*
 * Test: high VPP + FLAG_FORCE — error is downgraded to warning.
 * Same 12700 mV / 12000 setpoint, but FLAG_FORCE set on ctrl_flags.
 * FORCE downgrade: RESPONSE_CODE_WARNING instead of RESPONSE_CODE_ERROR.
 */
void test_flash_intel_high_vpp_with_force_warns(void) {
    set_mock_vpp_mv(12700);
    firestarter_handle_t h = make_intel_handle(12000, FLAG_FORCE);
    configure_memory(&h);
    h.firestarter_operation_init(&h);
    TEST_ASSERT_EQUAL(RESPONSE_CODE_WARNING, h.response_code);
}

/*
 * Test: REV0 hardware — VPP ADC read is skipped entirely, warning emitted.
 * set_mock_hw_rev(0) → rurp_get_hardware_revision() == REVISION_0.
 * set_mock_vpp_mv(65535) is an extreme reading (max uint16_t) that would normally
 * trigger RESPONSE_CODE_ERROR — if it were read. REV0 guard fires first and returns
 * before the ADC compare, so response_code must NOT be RESPONSE_CODE_ERROR.
 */
void test_flash_intel_rev0_skips_vpp_check(void) {
    set_mock_hw_rev(0);
    set_mock_vpp_mv(65535);  /* max uint16_t — would trigger high-band error if ADC were read */
    firestarter_handle_t h = make_intel_handle(12000, 0);
    configure_memory(&h);
    h.firestarter_operation_init(&h);
    TEST_ASSERT_NOT_EQUAL(RESPONSE_CODE_ERROR, h.response_code);
}

int main(int, char**) {
    UNITY_BEGIN();
    RUN_TEST(test_flash_intel_vpp_nominal_proceeds);
    RUN_TEST(test_flash_intel_low_vpp_warns);
    RUN_TEST(test_flash_intel_high_vpp_errors);
    RUN_TEST(test_flash_intel_high_vpp_with_force_warns);
    RUN_TEST(test_flash_intel_rev0_skips_vpp_check);
    return UNITY_END();
}
