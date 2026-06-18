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
    /* delayMicroseconds is called by flash4_wait_for_page_write (10µs poll delay)
     * and by memory_set_data (3µs write settle). Must be stubbed so the operation-
     * phase tests (test_flash4_write_execute_*) don't abort on an unmocked call. */
    When(Method(ArduinoFake(), delayMicroseconds)).AlwaysReturn();
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

/* ─── FIX-02B (Phase 74 Plan 02): operation-phase SDP emission + VPP-safety ─ */
/*
 * These two tests exercise flash4_write_execute (the operation phase, not just
 * configure), using the recording-bus stub to observe side effects.
 *
 * Test setup: configure_memory(CMD_WRITE) wires function pointers including
 * firestarter_set_data = memory_set_data and the operation_main pointer.
 * Then clear_bus_recording() resets the capture, fill data_buffer with zeros
 * (so flash4_wait_for_page_write's DQ7 poll passes in one iteration since the
 * stub's rurp_read_data_buffer() always returns 0 = expected), set data_size=4
 * at address=0, and call h.firestarter_operation_main(&h) to drive
 * flash4_write_execute.
 *
 * The recording captures every rurp_write_to_register call:
 *   - flash_util_byte_flipping (SDP sequence) writes CONTROL_REGISTER
 *     (CTRL_READ_WRITE) + LSB/MSB for each command address pair.
 *   - memory_set_data writes LSB/MSB/CONTROL via mem_util_set_address.
 *
 * Test 1 (SDP emission, RED before fix): scans for the FLASH_ENABLE_WRITE
 * address signature — MSB writes of 0x55 (for 0x5555 and 0x5555 again) and
 * 0x2A (for 0x2AAA) in sequence before the first data address write. FAILS
 * today because flash4_write_execute has no flash_execute_command(FLASH_ENABLE_WRITE).
 *
 * Test 2 (operation-phase VPP-safety): asserts that no CTRL_VPP_REGULATOR_ENABLE
 * (0x80) or CTRL_VPP_P1_ENABLE (0x08) bit appears in any CONTROL_REGISTER write
 * during the write-execute call. Passes today and MUST keep passing after the fix.
 */

/* Helper to build a write handle with 4-byte zero data buffer at address 0. */
static firestarter_handle_t make_write_handle_with_data(void) {
    firestarter_handle_t h = {};
    h.protocol   = 0x05;
    h.cmd        = CMD_WRITE;
    h.response_code = RESPONSE_CODE_OK;
    h.chip_id    = 0; /* skip chip-id branch in write_init */
    h.mem_size   = 524288; /* 512 KB (W29C040) */
    h.address    = 0;
    h.data_size  = 4; /* small: 4 zero bytes at page 0; poll passes immediately */
    /* data_buffer is zero-initialized by {} */
    /* ctrl_flags = 0: no FLAG_CAN_ERASE, no FLAG_SKIP_BLANK_CHECK —
     * flash4_write_init would call blank-check, but we bypass init and call
     * operation_main directly. */
    return h;
}

/* Helper: scan recording for FLASH_ENABLE_WRITE address signature.
 * FLASH_ENABLE_WRITE addresses: 0x5555, 0x2AAA, 0x5555.
 * fu_flash_fast_address writes (LSB=addr&0xFF, MSB=(addr>>8)&0xFF).
 * Signature MSB pattern at start: 0x55, 0x2A, 0x55 in consecutive MSB writes.
 * Returns true if found, false if not. */
static bool recording_contains_sdp_signature(void) {
    /* Look for the MSB sequence: 0x55, 0x2A, 0x55 (MSBs of 0x5555, 0x2AAA, 0x5555) */
    int msb_seq_index = 0;
    const uint8_t msb_pattern[3] = {0x55, 0x2A, 0x55};
    for (int i = 0; i < bus_recording_count(); i++) {
        if (recorded_reg(i) == MOST_SIGNIFICANT_BYTE) {
            if (recorded_data(i) == msb_pattern[msb_seq_index]) {
                msb_seq_index++;
                if (msb_seq_index == 3) {
                    return true; /* full SDP MSB signature found */
                }
            } else {
                /* Reset if sequence breaks (partial match then mismatch) */
                msb_seq_index = (recorded_data(i) == msb_pattern[0]) ? 1 : 0;
            }
        }
    }
    return false;
}

/* Test 1 (FIX-02B SDP): flash4_write_execute must emit FLASH_ENABLE_WRITE
 * SDP 3-byte sequence at the start of each page load.
 * RED before fix (no flash_execute_command(FLASH_ENABLE_WRITE) in write path). */
void test_flash4_write_execute_emits_sdp(void) {
    firestarter_handle_t h = make_write_handle_with_data();
    configure_memory(&h);
    clear_bus_recording(); /* reset after configure_memory's set_address call */

    h.firestarter_operation_main(&h);

    TEST_ASSERT_EQUAL_MESSAGE(RESPONSE_CODE_OK, h.response_code,
        "flash4_write_execute must not error on 4-byte zero write");
    TEST_ASSERT_TRUE_MESSAGE(recording_contains_sdp_signature(),
        "flash4_write_execute must emit FLASH_ENABLE_WRITE SDP (0x5555,0x2AAA,0x5555 MSB pattern) at page start");
}

/* Test 2 (FIX-02B VPP-safety operation phase): flash4_write_execute must NEVER
 * set CTRL_VPP_REGULATOR_ENABLE (0x80) or CTRL_VPP_P1_ENABLE (0x08) in any
 * CONTROL_REGISTER write during the write-execute call.
 * Passes for the bare loop today; MUST remain green after the SDP fix since
 * flash_util_byte_flipping only sets CTRL_READ_WRITE (not VPP bits). */
void test_flash4_write_execute_no_vpp(void) {
    firestarter_handle_t h = make_write_handle_with_data();
    configure_memory(&h);
    clear_bus_recording();

    h.firestarter_operation_main(&h);

    TEST_ASSERT_EQUAL_MESSAGE(RESPONSE_CODE_OK, h.response_code,
        "flash4_write_execute must not error on 4-byte zero write");
    assert_no_vpp_in_recording(
        "flash4_write_execute (operation phase) must NOT set any VPP-enable CTL bit");
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

    /* FIX-02B: operation-phase SDP emission + VPP-safety proofs */
    RUN_TEST(test_flash4_write_execute_emits_sdp);
    RUN_TEST(test_flash4_write_execute_no_vpp);

    return UNITY_END();
}
