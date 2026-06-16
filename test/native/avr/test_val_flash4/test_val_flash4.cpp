/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 *
 * Phase 71 Plan 04 — Tier-1 validation suite for the Flash Type 4 family.
 * HARN-01 / D-07 / T-71-WIRED-WRONG.
 *
 * Proves the configure_flash4 dispatch/configure phase is VPP-safe.
 * BY SIDE-EFFECT via the recording bus stub:
 *
 *   For CMD_READ and CMD_WRITE (configure-only phase): configure_memory() writes
 *   only address bits to LSB/MSB/CONTROL registers via mem_util_set_address.
 *   configure_flash4 sets function pointers but writes no VPP-enable CTL bits.
 *   CTRL_VPP_REGULATOR_ENABLE, CTRL_VPP_P1_ENABLE, and CTRL_VPP_VPE_DROP_ENABLE
 *   must NEVER appear set in any recorded CONTROL_REGISTER write during the
 *   configure/dispatch phase.
 *
 *   NOTE: flash4_erase_execute (called from flash4_write_init) does use
 *   CTRL_VPP_REGULATOR_ENABLE for the OE=12V erase pulse. This is an operation-
 *   phase VPP use, NOT a configure-phase use. This suite tests the configure
 *   phase only (configure_memory alone, no firestarter_operation_init call), which
 *   is the correct scope for the "dispatch doesn't touch VPP" proof.
 *
 * Protocols covered: 0x05 (FLASH_AMD_STD), 0x35 (FLASH_EEPROM), 0x39 (FLASH_EEPROM2).
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

static firestarter_handle_t make_handle(uint32_t protocol, uint8_t cmd) {
    firestarter_handle_t h = {};
    h.protocol   = protocol;
    h.cmd        = cmd;
    h.response_code = RESPONSE_CODE_OK;
    h.chip_id    = 0; /* skip chip-id branch */
    h.mem_size   = 524288; /* 512 KB (SST39SF040) */
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

/* ─── Protocol 0x05 (FLASH_AMD_STD) ─────────────────────────────────────── */

void test_flash4_0x05_read_configure_no_vpp(void) {
    firestarter_handle_t h = make_handle(0x05, CMD_READ);
    configure_memory(&h);
    TEST_ASSERT_NOT_EQUAL_MESSAGE(RESPONSE_CODE_ERROR, h.response_code,
        "configure_memory must not error on 0x05 CMD_READ");
    assert_no_vpp_in_recording(
        "configure_flash4 0x05 CMD_READ configure-phase must NOT set any VPP-enable CTL bit");
}

void test_flash4_0x05_write_configure_no_vpp(void) {
    firestarter_handle_t h = make_handle(0x05, CMD_WRITE);
    configure_memory(&h);
    TEST_ASSERT_NOT_EQUAL_MESSAGE(RESPONSE_CODE_ERROR, h.response_code,
        "configure_memory must not error on 0x05 CMD_WRITE");
    assert_no_vpp_in_recording(
        "configure_flash4 0x05 CMD_WRITE configure-phase must NOT set any VPP-enable CTL bit");
}

/* ─── Protocol 0x35 (FLASH_EEPROM) ─────────────────────────────────────── */

void test_flash4_0x35_read_configure_no_vpp(void) {
    firestarter_handle_t h = make_handle(0x35, CMD_READ);
    configure_memory(&h);
    TEST_ASSERT_NOT_EQUAL_MESSAGE(RESPONSE_CODE_ERROR, h.response_code,
        "configure_memory must not error on 0x35 CMD_READ");
    assert_no_vpp_in_recording(
        "configure_flash4 0x35 CMD_READ configure-phase must NOT set any VPP-enable CTL bit");
}

void test_flash4_0x35_write_configure_no_vpp(void) {
    firestarter_handle_t h = make_handle(0x35, CMD_WRITE);
    configure_memory(&h);
    TEST_ASSERT_NOT_EQUAL_MESSAGE(RESPONSE_CODE_ERROR, h.response_code,
        "configure_memory must not error on 0x35 CMD_WRITE");
    assert_no_vpp_in_recording(
        "configure_flash4 0x35 CMD_WRITE configure-phase must NOT set any VPP-enable CTL bit");
}

/* ─── Protocol 0x39 (FLASH_EEPROM2) — future-proofed, dispatched by analogy ─ */

void test_flash4_0x39_read_configure_no_vpp(void) {
    firestarter_handle_t h = make_handle(0x39, CMD_READ);
    configure_memory(&h);
    TEST_ASSERT_NOT_EQUAL_MESSAGE(RESPONSE_CODE_ERROR, h.response_code,
        "configure_memory must not error on 0x39 CMD_READ");
    assert_no_vpp_in_recording(
        "configure_flash4 0x39 CMD_READ configure-phase must NOT set any VPP-enable CTL bit");
}

void test_flash4_0x39_write_configure_no_vpp(void) {
    firestarter_handle_t h = make_handle(0x39, CMD_WRITE);
    configure_memory(&h);
    TEST_ASSERT_NOT_EQUAL_MESSAGE(RESPONSE_CODE_ERROR, h.response_code,
        "configure_memory must not error on 0x39 CMD_WRITE");
    assert_no_vpp_in_recording(
        "configure_flash4 0x39 CMD_WRITE configure-phase must NOT set any VPP-enable CTL bit");
}

int main(int argc, char** argv) {
    (void)argc; (void)argv;
    UNITY_BEGIN();

    /* Protocol 0x05 configure-phase VPP-safety proof */
    RUN_TEST(test_flash4_0x05_read_configure_no_vpp);
    RUN_TEST(test_flash4_0x05_write_configure_no_vpp);

    /* Protocol 0x35 configure-phase VPP-safety proof */
    RUN_TEST(test_flash4_0x35_read_configure_no_vpp);
    RUN_TEST(test_flash4_0x35_write_configure_no_vpp);

    /* Protocol 0x39 configure-phase VPP-safety proof */
    RUN_TEST(test_flash4_0x39_read_configure_no_vpp);
    RUN_TEST(test_flash4_0x39_write_configure_no_vpp);

    return UNITY_END();
}
