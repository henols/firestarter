/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 *
 * Phase 44 Plan 02 — Wave 0 native Unity tests for the two host-tunable
 * read-timing knobs: `read_settling_us` and `read_strobe_us`.
 *
 * RED state before Task 2: these tests will FAIL TO COMPILE because the
 * `read_settling_us` and `read_strobe_us` fields do not yet exist on
 * `firestarter_handle_t`. That compile error IS the RED gate.
 *
 * Wave 1 (Task 2) adds the fields, PROGMEM parser entries, and
 * memory_get_data() instrumentation — flipping this suite GREEN.
 *
 * Test coverage:
 *   T1 — "read-settling-delay" JSON key → handle.read_settling_us stored
 *   T2 — "read-strobe-us" JSON key      → handle.read_strobe_us stored
 *   T3 — absent keys                   → both fields default to 0
 *   T4 — value above cap (T-44-01)     → read_settling_us clamped to cap
 */

#include <Arduino.h>
#include <ArduinoFake.h>
#include <unity.h>

extern "C" {
#include "json_parser.h"
}
#include "firestarter.h"

using namespace fakeit;

/* Maximum allowed value for read-timing knobs (T-44-01 / RESEARCH §Security
 * Domain). Mirrors the cap defined in memory.cpp / json_parser.c. */
#define READ_TIMING_MAX_US 1000UL

void setUp(void) {
    ArduinoFakeReset();
    /* Stub Serial.write and Serial.flush so LOG_ERROR_ID_* calls in any
     * transitive parse path don't abort. Tests never assert on serial. */
    When(OverloadedMethod(ArduinoFake(Serial), write, size_t(uint8_t)))
        .AlwaysReturn(1);
    When(OverloadedMethod(ArduinoFake(Serial), write, size_t(const uint8_t*, size_t)))
        .AlwaysReturn(1);
    When(Method(ArduinoFake(Serial), flush)).AlwaysReturn();
}

void tearDown(void) {}

/* Build a zero-initialized handle suitable for JSON parse tests. */
static firestarter_handle_t make_handle(uint8_t cmd) {
    firestarter_handle_t h = {};   /* zero-init: ensures new fields default 0 */
    h.cmd = cmd;
    h.response_code = RESPONSE_CODE_OK;
    return h;
}

/* Helper: parse a JSON string into a handle, return the json_parse result. */
static int parse_json(const char* json_str, firestarter_handle_t* handle) {
    jsmntok_t tokens[NUMBER_JSNM_TOKENS];
    int token_count = json_init(json_str, (int)strlen(json_str), tokens);
    if (token_count < 0) return token_count;
    return json_parse(json_str, tokens, token_count, handle);
}

/* T1: "read-settling-delay":50 → handle.read_settling_us == 50 */
void test_read_settling_us_parsed_from_json(void) {
    const char* json = "{\"cmd\":1,\"read-settling-delay\":50}";
    firestarter_handle_t h = make_handle(CMD_READ);
    int rc = parse_json(json, &h);
    TEST_ASSERT_EQUAL_INT(0, rc);
    TEST_ASSERT_EQUAL_UINT32(50, h.read_settling_us);
}

/* T2: "read-strobe-us":25 → handle.read_strobe_us == 25 */
void test_read_strobe_us_parsed_from_json(void) {
    const char* json = "{\"cmd\":1,\"read-strobe-us\":25}";
    firestarter_handle_t h = make_handle(CMD_READ);
    int rc = parse_json(json, &h);
    TEST_ASSERT_EQUAL_INT(0, rc);
    TEST_ASSERT_EQUAL_UINT32(25, h.read_strobe_us);
}

/* T3: absent timing keys → both fields remain 0 (zero-init default) */
void test_read_timing_fields_default_zero_when_absent(void) {
    const char* json = "{\"cmd\":1}";
    firestarter_handle_t h = make_handle(CMD_READ);
    int rc = parse_json(json, &h);
    TEST_ASSERT_EQUAL_INT(0, rc);
    TEST_ASSERT_EQUAL_UINT32(0, h.read_settling_us);
    TEST_ASSERT_EQUAL_UINT32(0, h.read_strobe_us);
}

/* T4: value above cap → read_settling_us clamped to READ_TIMING_MAX_US
 * (T-44-01 mitigation: an absurd JSON value cannot hang the read loop). */
void test_read_settling_us_capped_at_max(void) {
    /* Use a value well above 1000µs to confirm the cap fires */
    const char* json = "{\"cmd\":1,\"read-settling-delay\":9999}";
    firestarter_handle_t h = make_handle(CMD_READ);
    int rc = parse_json(json, &h);
    TEST_ASSERT_EQUAL_INT(0, rc);
    /* After cap: handle.read_settling_us must not exceed READ_TIMING_MAX_US */
    TEST_ASSERT_TRUE_MESSAGE(h.read_settling_us <= READ_TIMING_MAX_US,
                             "read_settling_us must be capped at READ_TIMING_MAX_US");
}

int main(int argc, char** argv) {
    (void)argc;
    (void)argv;
    UNITY_BEGIN();
    RUN_TEST(test_read_settling_us_parsed_from_json);
    RUN_TEST(test_read_strobe_us_parsed_from_json);
    RUN_TEST(test_read_timing_fields_default_zero_when_absent);
    RUN_TEST(test_read_settling_us_capped_at_max);
    return UNITY_END();
}
