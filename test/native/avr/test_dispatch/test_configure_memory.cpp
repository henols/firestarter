/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 *
 * Phase 12 Wave 0 — dispatch unit tests for configure_memory().
 *
 * One test per protocol in KNOWN_PROTOCOLS (build_db.py:89). Each test
 * constructs a minimal firestarter_handle_t (protocol, cmd, response_code)
 * and asserts `configure_memory()` does not raise RESPONSE_CODE_ERROR (i.e.
 * the chip resolved to a real handler).
 *
 * Phase 105 (protocol-only dispatch): dispatch is keyed on `protocol` alone
 * — there is no backward-compat fallback axis. Any unrecognized protocol,
 * including 0, reaches `configure_not_implemented()`; see
 * test_not_implemented.cpp for fail-closed coverage.
 *
 * Why TEST_ASSERT_NOT_EQUAL(RESPONSE_CODE_ERROR, ...) and not an operation-
 * pointer check? `configure_sram()` is a stub today and leaves the
 * firestarter_operation_init pointer NULL — pointer-set assertions would
 * spuriously fail. response_code is the robust dispatch-success signal.
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
    /* Stub Serial.write and Serial.flush so that LOG_ERROR_ID_* calls in the
     * error dispatch path (e.g. MSG_ERR_PROTOCOL_NOT_IMPLEMENTED) don't abort.
     * Dispatch tests never assert on serial output — only on response_code. */
    When(OverloadedMethod(ArduinoFake(Serial), write, size_t(uint8_t)))
        .AlwaysReturn(1);
    When(OverloadedMethod(ArduinoFake(Serial), write, size_t(const uint8_t*, size_t)))
        .AlwaysReturn(1);
    When(Method(ArduinoFake(Serial), flush)).AlwaysReturn();
}

void tearDown(void) {
}

/* Build a zero-initialized handle with only the three named fields set.
 * mem_type is retained as a vestigial (ignored) parameter to avoid
 * touching every call site now that firestarter_handle_t.mem_type is gone
 * (Phase 105 removal). */
static firestarter_handle_t make_handle(uint32_t protocol, uint8_t mem_type, uint8_t cmd) {
    (void)mem_type;
    firestarter_handle_t h = {};
    h.protocol = protocol;
    h.cmd = cmd;
    h.response_code = RESPONSE_CODE_OK;
    return h;
}

/* Positive dispatch tests — one per protocol in KNOWN_PROTOCOLS.
 * Each asserts that configure_memory() does NOT set response_code to
 * RESPONSE_CODE_ERROR (i.e. dispatch reached a real handler). */

void test_protocol_0x06_dispatches_nor_unlock(void) {
    firestarter_handle_t h = make_handle(0x06, 0, CMD_READ);
    configure_memory(&h);
    TEST_ASSERT_NOT_EQUAL(RESPONSE_CODE_ERROR, h.response_code);
}

void test_protocol_0x05_dispatches_5v_page(void) {
    firestarter_handle_t h = make_handle(0x05, 0, CMD_READ);
    configure_memory(&h);
    TEST_ASSERT_NOT_EQUAL(RESPONSE_CODE_ERROR, h.response_code);
}

void test_protocol_0x35_dispatches_5v_page(void) {
    firestarter_handle_t h = make_handle(0x35, 0, CMD_READ);
    configure_memory(&h);
    TEST_ASSERT_NOT_EQUAL(RESPONSE_CODE_ERROR, h.response_code);
}

void test_protocol_0x39_dispatches_5v_page(void) {
    firestarter_handle_t h = make_handle(0x39, 0, CMD_READ);
    configure_memory(&h);
    TEST_ASSERT_NOT_EQUAL(RESPONSE_CODE_ERROR, h.response_code);
}

void test_protocol_0x07_dispatches_eprom(void) {
    firestarter_handle_t h = make_handle(0x07, 0, CMD_READ);
    configure_memory(&h);
    TEST_ASSERT_NOT_EQUAL(RESPONSE_CODE_ERROR, h.response_code);
}

void test_protocol_0x08_dispatches_eprom(void) {
    firestarter_handle_t h = make_handle(0x08, 0, CMD_READ);
    configure_memory(&h);
    TEST_ASSERT_NOT_EQUAL(RESPONSE_CODE_ERROR, h.response_code);
}

void test_protocol_0x0B_dispatches_eprom(void) {
    firestarter_handle_t h = make_handle(0x0B, 0, CMD_READ);
    configure_memory(&h);
    TEST_ASSERT_NOT_EQUAL(RESPONSE_CODE_ERROR, h.response_code);
}

void test_protocol_0x0E_dispatches_sram(void) {
    firestarter_handle_t h = make_handle(0x0E, 0, CMD_READ);
    configure_memory(&h);
    TEST_ASSERT_NOT_EQUAL(RESPONSE_CODE_ERROR, h.response_code);
}

void test_protocol_0x27_dispatches_sram(void) {
    firestarter_handle_t h = make_handle(0x27, 0, CMD_READ);
    configure_memory(&h);
    TEST_ASSERT_NOT_EQUAL(RESPONSE_CODE_ERROR, h.response_code);
}

void test_protocol_0x28_dispatches_sram(void) {
    firestarter_handle_t h = make_handle(0x28, 0, CMD_READ);
    configure_memory(&h);
    TEST_ASSERT_NOT_EQUAL(RESPONSE_CODE_ERROR, h.response_code);
}

void test_protocol_0x29_dispatches_sram(void) {
    firestarter_handle_t h = make_handle(0x29, 0, CMD_READ);
    configure_memory(&h);
    TEST_ASSERT_NOT_EQUAL(RESPONSE_CODE_ERROR, h.response_code);
}

void test_protocol_0x10_dispatches_flash_intel(void) {
    firestarter_handle_t h = make_handle(0x10, 0, CMD_READ);
    configure_memory(&h);
    TEST_ASSERT_NOT_EQUAL(RESPONSE_CODE_ERROR, h.response_code);
}

void test_protocol_0x0D_dispatches_eeprom28c(void) {
    firestarter_handle_t h = make_handle(0x0D, 0, CMD_READ);
    configure_memory(&h);
    TEST_ASSERT_NOT_EQUAL(RESPONSE_CODE_ERROR, h.response_code);
}

/* FIX-02A (Phase 74 Plan 02): configure_flash_5v_page must handle CMD_CHECK_CHIP_ID
 * by setting a non-NULL operation_main pointer (mirroring configure_flash_nor_unlock).
 * These three tests are RED before the fix (no case in configure_flash_5v_page switch
 * → firestarter_operation_main stays NULL). */

void test_5v_page_check_chip_id_0x05_sets_operation(void) {
    firestarter_handle_t h = make_handle(0x05, 0, CMD_CHECK_CHIP_ID);
    configure_memory(&h);
    TEST_ASSERT_NOT_EQUAL_MESSAGE(RESPONSE_CODE_ERROR, h.response_code,
        "CMD_CHECK_CHIP_ID on 0x05 must not error");
    TEST_ASSERT_NOT_NULL_MESSAGE(h.firestarter_operation_main,
        "CMD_CHECK_CHIP_ID on 0x05 must set a non-NULL operation_main");
}

void test_5v_page_check_chip_id_0x35_sets_operation(void) {
    firestarter_handle_t h = make_handle(0x35, 0, CMD_CHECK_CHIP_ID);
    configure_memory(&h);
    TEST_ASSERT_NOT_EQUAL_MESSAGE(RESPONSE_CODE_ERROR, h.response_code,
        "CMD_CHECK_CHIP_ID on 0x35 must not error");
    TEST_ASSERT_NOT_NULL_MESSAGE(h.firestarter_operation_main,
        "CMD_CHECK_CHIP_ID on 0x35 must set a non-NULL operation_main");
}

void test_5v_page_check_chip_id_0x39_sets_operation(void) {
    firestarter_handle_t h = make_handle(0x39, 0, CMD_CHECK_CHIP_ID);
    configure_memory(&h);
    TEST_ASSERT_NOT_EQUAL_MESSAGE(RESPONSE_CODE_ERROR, h.response_code,
        "CMD_CHECK_CHIP_ID on 0x39 must not error");
    TEST_ASSERT_NOT_NULL_MESSAGE(h.firestarter_operation_main,
        "CMD_CHECK_CHIP_ID on 0x39 must set a non-NULL operation_main");
}

int main(int argc, char** argv) {
    (void)argc;
    (void)argv;
    UNITY_BEGIN();

    /* 13 protocol-positive tests (one per KNOWN_PROTOCOLS entry) */
    RUN_TEST(test_protocol_0x06_dispatches_nor_unlock);
    RUN_TEST(test_protocol_0x05_dispatches_5v_page);
    RUN_TEST(test_protocol_0x35_dispatches_5v_page);
    RUN_TEST(test_protocol_0x39_dispatches_5v_page);
    RUN_TEST(test_protocol_0x07_dispatches_eprom);
    RUN_TEST(test_protocol_0x08_dispatches_eprom);
    RUN_TEST(test_protocol_0x0B_dispatches_eprom);
    RUN_TEST(test_protocol_0x0E_dispatches_sram);
    RUN_TEST(test_protocol_0x27_dispatches_sram);
    RUN_TEST(test_protocol_0x28_dispatches_sram);
    RUN_TEST(test_protocol_0x29_dispatches_sram);
    RUN_TEST(test_protocol_0x10_dispatches_flash_intel);
    RUN_TEST(test_protocol_0x0D_dispatches_eeprom28c);

    /* FIX-02A: CMD_CHECK_CHIP_ID dispatch tests (RED before flash_5v_page.cpp fix) */
    RUN_TEST(test_5v_page_check_chip_id_0x05_sets_operation);
    RUN_TEST(test_5v_page_check_chip_id_0x35_sets_operation);
    RUN_TEST(test_5v_page_check_chip_id_0x39_sets_operation);

    return UNITY_END();
}
