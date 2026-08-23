/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 *
 * Wave 0 native Unity tests for the two host-tunable
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
#include "jsmn.h"
#include "memory.h"
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

/* Helper: parse a JSON string into a handle, return the json_parse result.
 * Calls jsmn_parse directly with the real token budget (NUMBER_JSNM_TOKENS).
 * The dead helper this used to route around -- which computed its token
 * count as sizeof() on a pointer parameter and could never succeed for a
 * real command -- was deleted in Phase 149 as dead code (zero call sites
 * in src/). */
static int parse_json(const char* json_str, firestarter_handle_t* handle) {
    jsmntok_t tokens[NUMBER_JSNM_TOKENS];
    jsmn_parser parser;
    jsmn_init(&parser);
    int token_count = jsmn_parse(&parser, json_str, strlen(json_str),
                                 tokens, NUMBER_JSNM_TOKENS);
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

/* page-size parse contract (PGSZ-01/PGSZ-02).
 *
 * T5: "page-size":128 -> handle.page_size == 128 */
void test_page_size_parsed_from_json(void) {
    const char* json = "{\"cmd\":2,\"page-size\":128}";
    firestarter_handle_t h = make_handle(CMD_WRITE);
    int rc = parse_json(json, &h);
    TEST_ASSERT_EQUAL_INT(0, rc);
    TEST_ASSERT_EQUAL_UINT16(128, h.page_size);
}

/* T6: absent key -> handle.page_size stays 0 (fresh handle) */
void test_page_size_defaults_zero_when_absent(void) {
    const char* json = "{\"cmd\":2}";
    firestarter_handle_t h = make_handle(CMD_WRITE);
    int rc = parse_json(json, &h);
    TEST_ASSERT_EQUAL_INT(0, rc);
    TEST_ASSERT_EQUAL_UINT16(0, h.page_size);
}

/* T7 (D-05, the whole point): ONE handle, parsed TWICE. A stale 128 surviving
 * into the second, page-size-absent parse would make "absent means 64" false
 * in practice -- the exact page overrun PGSZ-02 exists to prevent. A case
 * using a fresh handle for the second parse could never detect this. */
void test_page_size_resets_between_two_parses_on_the_same_handle(void) {
    firestarter_handle_t h = make_handle(CMD_WRITE);

    int rc1 = parse_json("{\"cmd\":2,\"page-size\":128}", &h);
    TEST_ASSERT_EQUAL_INT(0, rc1);
    TEST_ASSERT_EQUAL_UINT16_MESSAGE(128, h.page_size,
        "first parse must store the delivered page-size");

    int rc2 = parse_json("{\"cmd\":2}", &h);
    TEST_ASSERT_EQUAL_INT(0, rc2);
    TEST_ASSERT_EQUAL_UINT16_MESSAGE(0, h.page_size,
        "a stale 128 surviving into the next, page-size-absent command "
        "makes \"absent means 64\" false in practice -- the exact page "
        "overrun PGSZ-02 exists to prevent");
}

/* T8 (D-11): an unknown key BEFORE a known one must not desync the token
 * walk. Asserting only "parse succeeded" would pass even with a broken
 * token_idx advance -- assert a VALUE landed instead. */
void test_unknown_key_before_a_known_key_does_not_desync_the_token_walk(void) {
    const char* json = "{\"cmd\":2,\"totally-unknown-key\":7,\"read-strobe-us\":25}";
    firestarter_handle_t h = make_handle(CMD_WRITE);
    int rc = parse_json(json, &h);
    TEST_ASSERT_EQUAL_INT(0, rc);
    TEST_ASSERT_EQUAL_UINT32_MESSAGE(25, h.read_strobe_us,
        "the known key after an unknown one must still be parsed -- a "
        "desynced token_idx would silently drop it");
}

/* T9 (D-11): the same shape, but on the new-host / old-firmware direction
 * pinned on the key this phase adds. */
void test_unknown_key_before_page_size_does_not_desync_the_token_walk(void) {
    const char* json = "{\"cmd\":2,\"totally-unknown-key\":7,\"page-size\":128}";
    firestarter_handle_t h = make_handle(CMD_WRITE);
    int rc = parse_json(json, &h);
    TEST_ASSERT_EQUAL_INT(0, rc);
    TEST_ASSERT_EQUAL_UINT16(128, h.page_size);
}

/* S1 (DECODE-05, T-157-02): an out-of-range wire `algorithm` must SATURATE
 * to the member's own maximum (0xFF on the now-narrowed uint8_t protocol),
 * never TRUNCATE into a value that names a real handler. 261 (0x105)
 * truncates to 0x05, which is PROTO_FLASH_5V_PAGE -- a real, dispatchable
 * handler. Saturating to 0xFF names no arm of configure_memory's chain. */
void test_out_of_range_algorithm_saturates_not_truncates(void) {
    const char* json = "{\"cmd\":1,\"algorithm\":261}";
    firestarter_handle_t h = make_handle(CMD_READ);
    int rc = parse_json(json, &h);
    TEST_ASSERT_EQUAL_INT(0, rc);
    TEST_ASSERT_EQUAL_UINT8_MESSAGE(0xFF, h.protocol,
        "261 must saturate to 0xFF, not truncate to 0x05 -- 0x05 is "
        "PROTO_FLASH_5V_PAGE, a real handler configure_memory would "
        "dispatch into");
}

/* S2 (DECODE-05, T-157-02) -- the load-bearing case. A correct stored byte
 * (S1) is a DIFFERENT claim from a correct dispatch decision. This case is
 * the only thing in the repository that pins the second: that a saturated
 * 0xFF reaches configure_memory's generic fail-closed tail (no named arm
 * matches 0xFF) and refuses with RESPONSE_CODE_ERROR and all three
 * operation pointers NULL -- zero hardware side effects. Do not compare
 * against a named handler's function pointer; the symbol is not exported
 * to tests. This is test_not_implemented.cpp's local idiom, and it is
 * strictly stronger. */
void test_out_of_range_algorithm_dispatch_fail_closes(void) {
    const char* json = "{\"cmd\":1,\"algorithm\":261}";
    firestarter_handle_t h = make_handle(CMD_READ);
    int rc = parse_json(json, &h);
    TEST_ASSERT_EQUAL_INT(0, rc);
    configure_memory(&h);
    TEST_ASSERT_EQUAL_MESSAGE(RESPONSE_CODE_ERROR, h.response_code,
        "this is the case that would have caught the defect: the stored "
        "byte being right (S1) is not the same claim as the dispatch "
        "fail-closing -- a saturated 0xFF must reach configure_memory's "
        "generic fail-closed tail");
    TEST_ASSERT_NULL_MESSAGE(h.firestarter_operation_init,
        "fail-closed refusal must leave firestarter_operation_init NULL");
    TEST_ASSERT_NULL_MESSAGE(h.firestarter_operation_main,
        "fail-closed refusal must leave firestarter_operation_main NULL");
    TEST_ASSERT_NULL_MESSAGE(h.firestarter_operation_end,
        "fail-closed refusal must leave firestarter_operation_end NULL");
}

/* S3 (DECODE-05) -- the non-regression guard. S1 and S2 must not be
 * satisfiable by breaking every algorithm; a valid, in-range algorithm must
 * still dispatch to a real handler. No operation-pointer assertion here:
 * test_configure_memory.cpp documents that configure_sram() is a stub
 * leaving firestarter_operation_init NULL on a genuine success path, so a
 * pointer-set assertion would spuriously fail. response_code is the robust
 * dispatch-success signal. */
void test_in_range_algorithm_still_dispatches(void) {
    const char* json = "{\"cmd\":1,\"algorithm\":5}";
    firestarter_handle_t h = make_handle(CMD_READ);
    int rc = parse_json(json, &h);
    TEST_ASSERT_EQUAL_INT(0, rc);
    TEST_ASSERT_EQUAL_UINT8_MESSAGE(5, h.protocol,
        "a valid in-range algorithm must be stored unchanged");
    configure_memory(&h);
    TEST_ASSERT_NOT_EQUAL_MESSAGE(RESPONSE_CODE_ERROR, h.response_code,
        "this case exists so S1 and S2 cannot be satisfied by breaking "
        "every algorithm -- a valid protocol must still dispatch to a "
        "real handler, not fail-close");
}

/* S4 (DECODE-05, T-157-01): an out-of-range wire `flags` must MASK, never
 * SATURATE. Saturating a bitmask to its type maximum (0xFFFF on the
 * now-narrowed uint16_t ctrl_flags) would turn on all nine flags at once --
 * a fail-open that would make is_flag_set() read true at every one of the
 * 40 call sites. Asserted per-bit, not merely as an equality, so the case
 * reads as what it prevents. is_flag_set() itself is not used here: the
 * macro captures `handle` from the enclosing scope and no call site names
 * a type. */
void test_out_of_range_flags_masks_never_sets_every_flag(void) {
    const char* json = "{\"cmd\":2,\"flags\":65536}";
    firestarter_handle_t h = make_handle(CMD_WRITE);
    int rc = parse_json(json, &h);
    TEST_ASSERT_EQUAL_INT(0, rc);
    TEST_ASSERT_EQUAL_UINT16_MESSAGE(0, h.ctrl_flags,
        "an out-of-range wire flags value must mask to the width-limited "
        "truncation, never saturate to 0xFFFF -- saturating a bitmask "
        "turns on every flag at once, a fail-open in a fail-closed phase");
    TEST_ASSERT_EQUAL_MESSAGE(0, h.ctrl_flags & FLAG_FORCE,
        "FLAG_FORCE must not be set by an out-of-range flags value");
    TEST_ASSERT_EQUAL_MESSAGE(0, h.ctrl_flags & FLAG_SKIP_ERASE,
        "FLAG_SKIP_ERASE must not be set by an out-of-range flags value");
    TEST_ASSERT_EQUAL_MESSAGE(0, h.ctrl_flags & FLAG_SKIP_BLANK_CHECK,
        "FLAG_SKIP_BLANK_CHECK must not be set by an out-of-range flags "
        "value");
}

/* S5 (DECODE-05, T-157-05): an out-of-range wire `page-size` must saturate
 * to 0xFFFF, not truncate to a plausible VALID power of two. 65600
 * (0x10040) truncates to 0x0040 = 64 -- a perfectly valid page size, which
 * is what makes the hole silent. 0xFFFF is rejected by the consumer.
 *
 * Consumer-side evidence (C-20, source-level only -- eeprom28c_page_mask
 * is `static` in src/proms/eeprom_28c.cpp and unreachable from any test):
 * 0xFFFF exceeds AT28C_PAGE_SIZE_MAX (512) AND fails the power-of-two test
 * (0xFFFF & 0xFFFE != 0), so BOTH of eeprom28c_page_mask's guards reject
 * it and the function returns AT28C_PAGE_SIZE_FALLBACK - 1 -- a MASK
 * (63), not a size (64). */
void test_out_of_range_page_size_saturates_not_truncates_to_a_valid_size(void) {
    const char* json = "{\"cmd\":2,\"page-size\":65600}";
    firestarter_handle_t h = make_handle(CMD_WRITE);
    int rc = parse_json(json, &h);
    TEST_ASSERT_EQUAL_INT(0, rc);
    TEST_ASSERT_EQUAL_UINT16_MESSAGE(0xFFFF, h.page_size,
        "65600 must saturate to 0xFFFF, not truncate to 64 -- 64 is a "
        "perfectly valid page size, which is what makes the hole silent");
}

int main(int argc, char** argv) {
    (void)argc;
    (void)argv;
    UNITY_BEGIN();
    RUN_TEST(test_read_settling_us_parsed_from_json);
    RUN_TEST(test_read_strobe_us_parsed_from_json);
    RUN_TEST(test_read_timing_fields_default_zero_when_absent);
    RUN_TEST(test_read_settling_us_capped_at_max);
    RUN_TEST(test_page_size_parsed_from_json);
    RUN_TEST(test_page_size_defaults_zero_when_absent);
    RUN_TEST(test_page_size_resets_between_two_parses_on_the_same_handle);
    RUN_TEST(test_unknown_key_before_a_known_key_does_not_desync_the_token_walk);
    RUN_TEST(test_unknown_key_before_page_size_does_not_desync_the_token_walk);
    RUN_TEST(test_out_of_range_algorithm_saturates_not_truncates);
    RUN_TEST(test_out_of_range_algorithm_dispatch_fail_closes);
    RUN_TEST(test_in_range_algorithm_still_dispatches);
    RUN_TEST(test_out_of_range_flags_masks_never_sets_every_flag);
    RUN_TEST(test_out_of_range_page_size_saturates_not_truncates_to_a_valid_size);
    return UNITY_END();
}
