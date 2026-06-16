/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 *
 * Phase 71 Plan 04 — Tier-1 validation suite for the EPROM family.
 * HARN-01 / D-07 / D-08 (verify-can-fail posture).
 *
 * Proves configure_eprom behavior BY SIDE-EFFECT via the recording bus stub:
 *
 *   POSITIVE tests (CMD_WRITE): configure_memory() + firestarter_operation_init()
 *     → eprom_write_init → eprom_generic_init → eprom_check_vpp
 *     → rurp_write_to_register(CONTROL_REGISTER, value | CTRL_VPP_REGULATOR_ENABLE)
 *     The recording must contain at least one CONTROL_REGISTER write with
 *     CTRL_VPP_REGULATOR_ENABLE set.
 *
 *   NEGATIVE CONTROL (CMD_READ, configure-only phase): configure_memory() alone
 *     (no firestarter_operation_init call). configure_memory calls
 *     mem_util_set_address(handle, 0) which writes LSB/MSB/CONTROL registers
 *     with only address bits — no VPP-enable bits. Asserts CTRL_VPP_REGULATOR_ENABLE
 *     NEVER appears in the recording (proves in-tier verify-can-fail per D-08).
 *
 * Protocols covered: 0x07 (EPROM_STD), 0x08 (EPROM_QUICK), 0x0B (EPROM_LEGACY).
 *
 * VPP mechanism (from eprom.cpp source — not guessed):
 *   0x07/0x08: CTRL_VPP_REGULATOR_ENABLE | CTRL_VPP_VPE_DROP_ENABLE
 *   0x0B:      CTRL_VPP_REGULATOR_ENABLE only (direct VPE path)
 * Both paths set CTRL_VPP_REGULATOR_ENABLE — we assert the common bit.
 *
 * NOTE: delay() must be mocked; eprom_check_vpp calls delay(100).
 * Hardware revision stub returns 1 (non-REVISION_0) via host_stubs.cpp so
 * eprom_check_vpp does not take the REV0 early-return path.
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
    /* delay() is called by eprom_check_vpp (delay(100)) and eprom_write_execute
     * (delay(500)). Must be stubbed before any ArduinoFake virtual is called. */
    When(Method(ArduinoFake(), delay)).AlwaysReturn();
    clear_bus_recording();
}

void tearDown(void) {}

/* Build a zero-initialized handle with protocol, cmd, and a VPP setpoint of 0
 * (so eprom_check_vpp voltage comparison does not error on 0 mV reading). */
static firestarter_handle_t make_handle(uint32_t protocol, uint8_t cmd) {
    firestarter_handle_t h = {};
    h.protocol   = protocol;
    h.cmd        = cmd;
    h.response_code = RESPONSE_CODE_OK;
    h.vpp_mv     = 0;  /* vpp setpoint=0 matches stub voltage=0: no warn/error */
    h.chip_id    = 0;  /* skip chip-ID branch */
    h.mem_size   = 65536; /* 64 KB — keeps blank_check from NULL-ptr in mock */
    h.ctrl_flags = FLAG_SKIP_BLANK_CHECK | FLAG_SKIP_ERASE;
    return h;
}

/* ─── Helper: scan recording for CONTROL_REGISTER writes with VPP bit set ─── */
static bool recording_has_vpp_enable(uint8_t vpp_bit) {
    for (int i = 0; i < bus_recording_count(); i++) {
        if (recorded_reg(i) == CONTROL_REGISTER &&
            (recorded_data(i) & vpp_bit)) {
            return true;
        }
    }
    return false;
}

/* NOTE: CTRL_VPP_VPE_DROP_ENABLE is 0x100 when HARDWARE_REVISION is defined —
 * it does not fit in uint8_t. The recording buffer stores uint8_t data values,
 * so CTRL_VPP_VPE_DROP_ENABLE cannot be detected via the 8-bit recording when
 * HARDWARE_REVISION is defined. Use CTRL_VPP_REGULATOR_ENABLE (0x80) and
 * CTRL_VPP_P1_ENABLE (0x08) which fit in 8 bits for VPP-enable detection. */
static bool recording_has_any_vpp_enable(void) {
    return recording_has_vpp_enable(CTRL_VPP_REGULATOR_ENABLE) ||
           recording_has_vpp_enable(CTRL_VPP_P1_ENABLE);
}

/* ─── POSITIVE tests: CMD_WRITE + init → VPP regulator must fire ─────────── */

/* Protocol 0x07 (EPROM_STD): write init must enable CTRL_VPP_REGULATOR_ENABLE. */
void test_eprom_0x07_write_enables_vpp_regulator(void) {
    firestarter_handle_t h = make_handle(0x07, CMD_WRITE);
    configure_memory(&h);
    TEST_ASSERT_NOT_EQUAL_MESSAGE(RESPONSE_CODE_ERROR, h.response_code,
        "configure_memory must not error on protocol 0x07 CMD_WRITE");
    if (h.firestarter_operation_init) {
        h.firestarter_operation_init(&h);
    }
    TEST_ASSERT_TRUE_MESSAGE(
        recording_has_vpp_enable(CTRL_VPP_REGULATOR_ENABLE),
        "configure_eprom 0x07 write must record CTRL_VPP_REGULATOR_ENABLE in CTL register");
}

/* Protocol 0x08 (EPROM_QUICK): same mechanism as 0x07. */
void test_eprom_0x08_write_enables_vpp_regulator(void) {
    firestarter_handle_t h = make_handle(0x08, CMD_WRITE);
    configure_memory(&h);
    TEST_ASSERT_NOT_EQUAL_MESSAGE(RESPONSE_CODE_ERROR, h.response_code,
        "configure_memory must not error on protocol 0x08 CMD_WRITE");
    if (h.firestarter_operation_init) {
        h.firestarter_operation_init(&h);
    }
    TEST_ASSERT_TRUE_MESSAGE(
        recording_has_vpp_enable(CTRL_VPP_REGULATOR_ENABLE),
        "configure_eprom 0x08 write must record CTRL_VPP_REGULATOR_ENABLE in CTL register");
}

/* Protocol 0x0B (EPROM_LEGACY): direct VPE path — CTRL_VPP_REGULATOR_ENABLE only. */
void test_eprom_0x0B_write_enables_vpp_regulator(void) {
    firestarter_handle_t h = make_handle(0x0B, CMD_WRITE);
    configure_memory(&h);
    TEST_ASSERT_NOT_EQUAL_MESSAGE(RESPONSE_CODE_ERROR, h.response_code,
        "configure_memory must not error on protocol 0x0B CMD_WRITE");
    if (h.firestarter_operation_init) {
        h.firestarter_operation_init(&h);
    }
    TEST_ASSERT_TRUE_MESSAGE(
        recording_has_vpp_enable(CTRL_VPP_REGULATOR_ENABLE),
        "configure_eprom 0x0B write must record CTRL_VPP_REGULATOR_ENABLE in CTL register");
}

/* ─── NEGATIVE CONTROL: CMD_READ, configure-only — VPP must NOT fire ─────── */

/* For CMD_READ, only configure_memory() is called (no firestarter_operation_init
 * call). configure_memory routes to configure_eprom which only sets function
 * pointers, then mem_util_set_address writes LSB/MSB/CONTROL with address bits
 * only — no VPP-enable bits. This asserts the configure/dispatch phase alone
 * never enables VPP (D-08 verify-can-fail: this test goes RED if a regression
 * puts VPP enable inside configure_memory or configure_eprom itself). */
void test_eprom_0x07_read_configure_only_does_not_enable_vpp(void) {
    firestarter_handle_t h = make_handle(0x07, CMD_READ);
    configure_memory(&h);
    TEST_ASSERT_NOT_EQUAL_MESSAGE(RESPONSE_CODE_ERROR, h.response_code,
        "configure_memory must not error on protocol 0x07 CMD_READ");
    /* Note: CTRL_VPP_VPE_DROP_ENABLE is 0x100 when HARDWARE_REVISION defined —
     * it cannot be detected via uint8_t recording; check 8-bit-fit VPP bits only. */
    for (int i = 0; i < bus_recording_count(); i++) {
        if (recorded_reg(i) == CONTROL_REGISTER) {
            TEST_ASSERT_BITS_LOW_MESSAGE(
                (uint8_t)CTRL_VPP_REGULATOR_ENABLE,
                recorded_data(i),
                "configure_eprom 0x07 CMD_READ configure-phase must NOT set CTRL_VPP_REGULATOR_ENABLE");
            TEST_ASSERT_BITS_LOW_MESSAGE(
                (uint8_t)CTRL_VPP_P1_ENABLE,
                recorded_data(i),
                "configure_eprom 0x07 CMD_READ configure-phase must NOT set CTRL_VPP_P1_ENABLE");
        }
    }
}

void test_eprom_0x08_read_configure_only_does_not_enable_vpp(void) {
    firestarter_handle_t h = make_handle(0x08, CMD_READ);
    configure_memory(&h);
    TEST_ASSERT_NOT_EQUAL_MESSAGE(RESPONSE_CODE_ERROR, h.response_code,
        "configure_memory must not error on protocol 0x08 CMD_READ");
    for (int i = 0; i < bus_recording_count(); i++) {
        if (recorded_reg(i) == CONTROL_REGISTER) {
            TEST_ASSERT_BITS_LOW_MESSAGE(
                (uint8_t)CTRL_VPP_REGULATOR_ENABLE,
                recorded_data(i),
                "configure_eprom 0x08 CMD_READ configure-phase must NOT set CTRL_VPP_REGULATOR_ENABLE");
        }
    }
}

void test_eprom_0x0B_read_configure_only_does_not_enable_vpp(void) {
    firestarter_handle_t h = make_handle(0x0B, CMD_READ);
    configure_memory(&h);
    TEST_ASSERT_NOT_EQUAL_MESSAGE(RESPONSE_CODE_ERROR, h.response_code,
        "configure_memory must not error on protocol 0x0B CMD_READ");
    for (int i = 0; i < bus_recording_count(); i++) {
        if (recorded_reg(i) == CONTROL_REGISTER) {
            TEST_ASSERT_BITS_LOW_MESSAGE(
                (uint8_t)CTRL_VPP_REGULATOR_ENABLE,
                recorded_data(i),
                "configure_eprom 0x0B CMD_READ configure-phase must NOT set CTRL_VPP_REGULATOR_ENABLE");
        }
    }
}

int main(int argc, char** argv) {
    (void)argc; (void)argv;
    UNITY_BEGIN();

    /* POSITIVE: write + init path enables VPP regulator, one test per protocol */
    RUN_TEST(test_eprom_0x07_write_enables_vpp_regulator);
    RUN_TEST(test_eprom_0x08_write_enables_vpp_regulator);
    RUN_TEST(test_eprom_0x0B_write_enables_vpp_regulator);

    /* NEGATIVE CONTROL: configure-only (CMD_READ, no init) — no VPP bits set */
    RUN_TEST(test_eprom_0x07_read_configure_only_does_not_enable_vpp);
    RUN_TEST(test_eprom_0x08_read_configure_only_does_not_enable_vpp);
    RUN_TEST(test_eprom_0x0B_read_configure_only_does_not_enable_vpp);

    return UNITY_END();
}
