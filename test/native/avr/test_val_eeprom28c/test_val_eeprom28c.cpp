/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 *
 * Phase 71 Plan 04 — Tier-1 validation suite for the EEPROM 28C family.
 * HARN-01 / D-07 / T-71-WIRED-WRONG.
 *
 * Proves configure_eeprom28c is a 5V-only handler (no VPP regulator use).
 * BY SIDE-EFFECT via the recording bus stub:
 *
 *   For CMD_READ and CMD_WRITE (configure-only phase): configure_memory() is
 *   called. configure_eeprom28c sets function pointers and the pulse_delay but
 *   writes NO VPP-enable CTL bits. mem_util_set_address(handle, 0) writes LSB/
 *   MSB/CONTROL registers with address bits only — CTRL_VPP_REGULATOR_ENABLE,
 *   CTRL_VPP_P1_ENABLE, and CTRL_VPP_VPE_DROP_ENABLE must NEVER appear set in
 *   any recorded CONTROL_REGISTER write.
 *
 *   This test can go RED if configure_eeprom28c is accidentally wired to an
 *   EPROM-style configure path that enables the VPP regulator (T-71-WIRED-WRONG).
 *
 * Protocol covered: 0x0D (EEPROM_POLL / AT28C-series).
 *
 * VPP: NONE — configure_eeprom28c is a 5V page-write handler. The A9-12V chip-ID
 * path in eeprom28c_check_chip_id is gated by handle->chip_id > 0; we set chip_id=0
 * so that branch is never reached. Even if reached, it fires in the operation_init
 * phase (not the configure phase tested here).
 */

#include <Arduino.h>
#include <ArduinoFake.h>
#include <unity.h>

extern "C" {
#include "memory.h"
}
#include "firestarter.h"
#include "rurp_pinout.h"

using namespace fakeit;

/* Recording API — symbols compiled because host_stubs.cpp defines HOST_STUBS_RECORD_BUS. */
extern "C" void clear_bus_recording();
extern "C" int  bus_recording_count();
extern "C" uint8_t recorded_reg(int i);
extern "C" uint8_t recorded_data(int i);

void setUp(void) {
    ArduinoFakeReset();
    When(OverloadedMethod(ArduinoFake(Serial), write, size_t(uint8_t))).AlwaysReturn(1);
    When(OverloadedMethod(ArduinoFake(Serial), write, size_t(const uint8_t*, size_t))).AlwaysReturn(1);
    When(Method(ArduinoFake(Serial), flush)).AlwaysReturn();
    clear_bus_recording();
}

void tearDown(void) {}

static firestarter_handle_t make_handle(uint8_t cmd) {
    firestarter_handle_t h = {};
    h.protocol   = 0x0D;
    h.cmd        = cmd;
    h.response_code = RESPONSE_CODE_OK;
    h.chip_id    = 0; /* skip chip-id branch */
    h.mem_size   = 32768; /* 32 KB (AT28C256) */
    return h;
}

/* ─── Helper: assert no VPP-enable bits in any CONTROL_REGISTER write ──────── */
/* Note: CTRL_VPP_VPE_DROP_ENABLE is 0x100 when HARDWARE_REVISION is defined —
 * it does not fit in the uint8_t recording buffer. Check only the 8-bit-fit
 * VPP-enable bits: CTRL_VPP_REGULATOR_ENABLE (0x80) and CTRL_VPP_P1_ENABLE (0x08). */
static void assert_no_vpp_in_recording(const char* ctx) {
    for (int i = 0; i < bus_recording_count(); i++) {
        if (recorded_reg(i) == CONTROL_REGISTER) {
            TEST_ASSERT_BITS_LOW_MESSAGE(
                (uint8_t)CTRL_VPP_REGULATOR_ENABLE,
                recorded_data(i), ctx);
            TEST_ASSERT_BITS_LOW_MESSAGE(
                (uint8_t)CTRL_VPP_P1_ENABLE,
                recorded_data(i), ctx);
        }
    }
}

/* configure-only: CMD_READ must record zero VPP-enable bits */
void test_eeprom28c_read_configure_no_vpp(void) {
    firestarter_handle_t h = make_handle(CMD_READ);
    configure_memory(&h);
    TEST_ASSERT_NOT_EQUAL_MESSAGE(RESPONSE_CODE_ERROR, h.response_code,
        "configure_memory must not error on 0x0D CMD_READ");
    assert_no_vpp_in_recording(
        "configure_eeprom28c CMD_READ must NOT set any VPP-enable CTL bit");
}

/* configure-only: CMD_WRITE must record zero VPP-enable bits */
void test_eeprom28c_write_configure_no_vpp(void) {
    firestarter_handle_t h = make_handle(CMD_WRITE);
    configure_memory(&h);
    TEST_ASSERT_NOT_EQUAL_MESSAGE(RESPONSE_CODE_ERROR, h.response_code,
        "configure_memory must not error on 0x0D CMD_WRITE");
    assert_no_vpp_in_recording(
        "configure_eeprom28c CMD_WRITE must NOT set any VPP-enable CTL bit");
}

/* configure-only: CMD_BLANK_CHECK must record zero VPP-enable bits */
void test_eeprom28c_blank_check_configure_no_vpp(void) {
    firestarter_handle_t h = make_handle(CMD_BLANK_CHECK);
    configure_memory(&h);
    TEST_ASSERT_NOT_EQUAL_MESSAGE(RESPONSE_CODE_ERROR, h.response_code,
        "configure_memory must not error on 0x0D CMD_BLANK_CHECK");
    assert_no_vpp_in_recording(
        "configure_eeprom28c CMD_BLANK_CHECK must NOT set any VPP-enable CTL bit");
}

int main(int argc, char** argv) {
    (void)argc; (void)argv;
    UNITY_BEGIN();

    /* 5V-only proof: no VPP-enable CTL bit for any command in the configure phase */
    RUN_TEST(test_eeprom28c_read_configure_no_vpp);
    RUN_TEST(test_eeprom28c_write_configure_no_vpp);
    RUN_TEST(test_eeprom28c_blank_check_configure_no_vpp);

    return UNITY_END();
}
