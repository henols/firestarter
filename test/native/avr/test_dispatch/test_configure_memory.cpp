/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 *
 * Phase 12 Wave 0 — dispatch unit tests for configure_memory().
 *
 * One test per protocol in KNOWN_PROTOCOLS (build_db.py:89). Each test
 * constructs a minimal firestarter_handle_t (protocol, mem_type, cmd,
 * response_code) and asserts `configure_memory()` does not raise
 * RESPONSE_CODE_ERROR (i.e. the chip resolved to a real handler, not the
 * "Memory type 0x%02x not supported" fallback).
 *
 * RED state on this commit (Wave 0): protocols 0x05, 0x06, 0x07, 0x08, 0x0B,
 * 0x0E, 0x27, 0x28, 0x29, 0x35, 0x39 are NOT yet routed by protocol prefix —
 * they fall through to `firestarter_error_response_format(...)` and set
 * response_code = RESPONSE_CODE_ERROR. Only 0x10 and 0x0D pass today.
 *
 * Wave 1 (Plan 02) lands the C++ dispatch extension and flips these tests
 * GREEN. The negative test (`test_unknown_protocol_with_unknown_mem_type_errors`)
 * must remain GREEN at every wave — it asserts the fallback error path still
 * fires for genuinely-unknown (protocol, mem_type) pairs.
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
     * error dispatch path (e.g. MSG_ERR_MEM_TYPE_UNSUPPORTED) don't abort.
     * Dispatch tests never assert on serial output — only on response_code. */
    When(OverloadedMethod(ArduinoFake(Serial), write, size_t(uint8_t)))
        .AlwaysReturn(1);
    When(OverloadedMethod(ArduinoFake(Serial), write, size_t(const uint8_t*, size_t)))
        .AlwaysReturn(1);
    When(Method(ArduinoFake(Serial), flush)).AlwaysReturn();
}

void tearDown(void) {
}

/* Build a zero-initialized handle with only the three named fields set. */
static firestarter_handle_t make_handle(uint32_t protocol, uint8_t mem_type, uint8_t cmd) {
    firestarter_handle_t h = {};
    h.protocol = protocol;
    h.mem_type = mem_type;
    h.cmd = cmd;
    h.response_code = RESPONSE_CODE_OK;
    return h;
}

/* Positive dispatch tests — one per protocol in KNOWN_PROTOCOLS.
 * Each asserts that configure_memory() does NOT set response_code to
 * RESPONSE_CODE_ERROR (i.e. dispatch reached a real handler). */

void test_protocol_0x06_dispatches_flash3(void) {
    firestarter_handle_t h = make_handle(0x06, 0, CMD_READ);
    configure_memory(&h);
    TEST_ASSERT_NOT_EQUAL(RESPONSE_CODE_ERROR, h.response_code);
}

void test_protocol_0x05_dispatches_flash4(void) {
    firestarter_handle_t h = make_handle(0x05, 0, CMD_READ);
    configure_memory(&h);
    TEST_ASSERT_NOT_EQUAL(RESPONSE_CODE_ERROR, h.response_code);
}

void test_protocol_0x35_dispatches_flash4(void) {
    firestarter_handle_t h = make_handle(0x35, 0, CMD_READ);
    configure_memory(&h);
    TEST_ASSERT_NOT_EQUAL(RESPONSE_CODE_ERROR, h.response_code);
}

void test_protocol_0x39_dispatches_flash4(void) {
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

/* Negative test: genuinely-unknown (protocol, mem_type) pair must surface
 * the error response. This must remain green across every wave. */
void test_unknown_protocol_with_unknown_mem_type_errors(void) {
    firestarter_handle_t h = make_handle(0, 99, CMD_READ);
    configure_memory(&h);
    TEST_ASSERT_EQUAL(RESPONSE_CODE_ERROR, h.response_code);
}

/* Fallback test: protocol=0 with a known mem_type still resolves via the
 * legacy mem_type chain. Must remain green across every wave. */
void test_protocol_zero_with_mem_type_eprom_dispatches_eprom(void) {
    firestarter_handle_t h = make_handle(0, 1, CMD_READ); /* TYPE_EPROM = 1 */
    configure_memory(&h);
    TEST_ASSERT_NOT_EQUAL(RESPONSE_CODE_ERROR, h.response_code);
}

int main(int argc, char** argv) {
    (void)argc;
    (void)argv;
    UNITY_BEGIN();

    /* 13 protocol-positive tests (one per KNOWN_PROTOCOLS entry) */
    RUN_TEST(test_protocol_0x06_dispatches_flash3);
    RUN_TEST(test_protocol_0x05_dispatches_flash4);
    RUN_TEST(test_protocol_0x35_dispatches_flash4);
    RUN_TEST(test_protocol_0x39_dispatches_flash4);
    RUN_TEST(test_protocol_0x07_dispatches_eprom);
    RUN_TEST(test_protocol_0x08_dispatches_eprom);
    RUN_TEST(test_protocol_0x0B_dispatches_eprom);
    RUN_TEST(test_protocol_0x0E_dispatches_sram);
    RUN_TEST(test_protocol_0x27_dispatches_sram);
    RUN_TEST(test_protocol_0x28_dispatches_sram);
    RUN_TEST(test_protocol_0x29_dispatches_sram);
    RUN_TEST(test_protocol_0x10_dispatches_flash_intel);
    RUN_TEST(test_protocol_0x0D_dispatches_eeprom28c);

    /* 1 negative + 1 fallback test (must remain green across every wave) */
    RUN_TEST(test_unknown_protocol_with_unknown_mem_type_errors);
    RUN_TEST(test_protocol_zero_with_mem_type_eprom_dispatches_eprom);

    return UNITY_END();
}
