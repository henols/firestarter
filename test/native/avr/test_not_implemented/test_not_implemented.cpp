/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 *
 * Phase 64 — dispatch unit tests for configure_not_implemented() and
 * fail-closed dispatch arms.
 *
 * Tests assert RESPONSE_CODE_ERROR and all-three-NULL op pointers (unlike
 * the sibling test_configure_memory.cpp which avoids pointer checks because
 * configure_sram() is a stub with NULL firestarter_operation_init).
 * The not-implemented handler is self-contained and always leaves all
 * three pointers NULL — pointer assertions are safe here.
 */
#include <Arduino.h>
#include <ArduinoFake.h>
#include <unity.h>

extern "C" {
#include "memory.h"
}
#include "firestarter.h"

using namespace fakeit;

void setUp(void) {
    ArduinoFakeReset();
    When(OverloadedMethod(ArduinoFake(Serial), write, size_t(uint8_t)))
        .AlwaysReturn(1);
    When(OverloadedMethod(ArduinoFake(Serial), write, size_t(const uint8_t*, size_t)))
        .AlwaysReturn(1);
    When(Method(ArduinoFake(Serial), flush)).AlwaysReturn();
}

void tearDown(void) {}

/* Build a zero-initialized handle with only the three named fields set. */
static firestarter_handle_t make_handle(uint32_t protocol, uint8_t mem_type, uint8_t cmd) {
    firestarter_handle_t h = {};
    h.protocol = protocol;
    h.mem_type = mem_type;
    h.cmd = cmd;
    h.response_code = RESPONSE_CODE_OK;
    return h;
}

/* --- Named infeasibility arms (DISP-04) --- */

void test_protocol_0x11_fwh_not_implemented(void) {
    firestarter_handle_t h = make_handle(0x11, 0, CMD_READ);
    configure_memory(&h);
    TEST_ASSERT_EQUAL(RESPONSE_CODE_ERROR, h.response_code);
    TEST_ASSERT_NULL(h.firestarter_operation_init);
    TEST_ASSERT_NULL(h.firestarter_operation_main);
    TEST_ASSERT_NULL(h.firestarter_operation_end);
}

void test_protocol_0x2A_gal_not_implemented(void) {
    firestarter_handle_t h = make_handle(0x2A, 0, CMD_READ);
    configure_memory(&h);
    TEST_ASSERT_EQUAL(RESPONSE_CODE_ERROR, h.response_code);
    TEST_ASSERT_NULL(h.firestarter_operation_init);
    TEST_ASSERT_NULL(h.firestarter_operation_main);
    TEST_ASSERT_NULL(h.firestarter_operation_end);
}

void test_protocol_0x2B_gal_not_implemented(void) {
    firestarter_handle_t h = make_handle(0x2B, 0, CMD_READ);
    configure_memory(&h);
    TEST_ASSERT_EQUAL(RESPONSE_CODE_ERROR, h.response_code);
    TEST_ASSERT_NULL(h.firestarter_operation_init);
    TEST_ASSERT_NULL(h.firestarter_operation_main);
    TEST_ASSERT_NULL(h.firestarter_operation_end);
}

void test_protocol_0x2C_pld_not_implemented(void) {
    firestarter_handle_t h = make_handle(0x2C, 0, CMD_READ);
    configure_memory(&h);
    TEST_ASSERT_EQUAL(RESPONSE_CODE_ERROR, h.response_code);
    TEST_ASSERT_NULL(h.firestarter_operation_init);
    TEST_ASSERT_NULL(h.firestarter_operation_main);
    TEST_ASSERT_NULL(h.firestarter_operation_end);
}

/* --- Generic fail-closed catch-all (DISP-01) --- */

void test_unknown_nonzero_protocol_0x99_not_implemented(void) {
    firestarter_handle_t h = make_handle(0x99, 0, CMD_READ);
    configure_memory(&h);
    TEST_ASSERT_EQUAL(RESPONSE_CODE_ERROR, h.response_code);
    TEST_ASSERT_NULL(h.firestarter_operation_init);
    TEST_ASSERT_NULL(h.firestarter_operation_main);
    TEST_ASSERT_NULL(h.firestarter_operation_end);
}

/* --- Legacy fallback re-assertion (DISP-02): protocol==0 + mem_type=1
 * must still route to configure_eprom, not hit the not-implemented guard.
 * Mirrors test_configure_memory.cpp:159-163 — must remain green. --- */
void test_protocol_zero_with_mem_type_eprom_dispatches_eprom(void) {
    firestarter_handle_t h = make_handle(0, 1, CMD_READ); /* TYPE_EPROM = 1 */
    configure_memory(&h);
    TEST_ASSERT_NOT_EQUAL(RESPONSE_CODE_ERROR, h.response_code);
}

int main(int argc, char** argv) {
    (void)argc;
    (void)argv;
    UNITY_BEGIN();

    /* Named infeasibility arms */
    RUN_TEST(test_protocol_0x11_fwh_not_implemented);
    RUN_TEST(test_protocol_0x2A_gal_not_implemented);
    RUN_TEST(test_protocol_0x2B_gal_not_implemented);
    RUN_TEST(test_protocol_0x2C_pld_not_implemented);

    /* Generic catch-all */
    RUN_TEST(test_unknown_nonzero_protocol_0x99_not_implemented);

    /* Re-assertion: legacy fallback intact (protocol == 0) */
    RUN_TEST(test_protocol_zero_with_mem_type_eprom_dispatches_eprom);

    return UNITY_END();
}
