/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 *
 * v1.22 Phase 119 Plan 02 — the D-04 two-env truth-table suite for
 * is_memory_cmd() (LOCK-03).
 *
 * This suite is compiled and run in BOTH [env:native] (-D DEV_TOOLS) and
 * [env:native_nodevtools] (no -D DEV_TOOLS). Asserting on is_memory_cmd()
 * over every possible uint8_t value in both builds is a SEMANTIC proof that
 * the predicate is DEV_TOOLS-invariant — not merely a textual one (a human
 * or a grep reading its body). Plan 119-03's source-scan gate is the third
 * oracle over the same claim.
 *
 * Every case here asserts on is_memory_cmd() ONLY — never on dispatch,
 * configure_memory(), or any handler. That keeps this suite orthogonal to
 * test_dispatch (which tests what a command DOES) and focused purely on
 * what the admission gate ADMITS.
 */

#include <Arduino.h>
#include <ArduinoFake.h>
#include <unity.h>
#include <stdio.h>

#include "firestarter.h"

using namespace fakeit;

void setUp(void) {
    ArduinoFakeReset();
    /* Stub Serial.write / Serial.flush so any LOG_* call reached indirectly
     * (e.g. via a widened build_src_filter in a later plan) doesn't abort —
     * mirrors test_configure_memory.cpp:36-62. This suite's own assertions
     * never touch Serial output. */
    When(OverloadedMethod(ArduinoFake(Serial), write, size_t(uint8_t)))
        .AlwaysReturn(1);
    When(OverloadedMethod(ArduinoFake(Serial), write, size_t(const uint8_t*, size_t)))
        .AlwaysReturn(1);
    When(Method(ArduinoFake(Serial), flush)).AlwaysReturn();

    /* LOAD-BEARING, do not remove as "unused" (test_sdp_harness.cpp:75-90
     * precedent): is_memory_cmd() itself calls nothing, but ArduinoFake
     * ABORTS (SIGABRT) on any unmocked virtual reached by anything this
     * suite links against, and this suite must stay robust to a later plan
     * widening build_src_filter (e.g. Plan 119-07's Open Question 1 spike).
     * A SIGABRT in a brand-new suite is Pitfall 5, not the deferred
     * test_flash_intel_vpp Unity-teardown flake. */
    When(Method(ArduinoFake(), delay)).AlwaysReturn();
    When(Method(ArduinoFake(), delayMicroseconds)).AlwaysReturn();
    When(Method(ArduinoFake(), millis)).AlwaysReturn(0);
    When(Method(ArduinoFake(), micros)).AlwaysReturn(0);
}

void tearDown(void) {
}

/* Case 1 — the load-bearing case: EVERY value in [0, 255], not a sample.
 * Exhaustiveness over the full uint8_t domain is what makes the two-env run
 * a set-equality proof rather than a spot check. Expected membership is the
 * literal set {1,2,3,4,5,6,9,10,16} using bare numeric literals so this case
 * compiles identically whether or not the CMD_* macros it is checking
 * against exist under DEV_TOOLS — it does not reference any CMD_DEV_* macro
 * at all (see case 2's comment for why that matters). Phase 151 (LOCK-02,
 * OD-3) grew the expected set from eight values to nine by adding 16
 * (CMD_LOCK_STATUS). Note: 16 IS a real, unconditionally-defined CMD_*
 * macro (unlike 7/8), but this case still spells it as a bare literal to
 * keep the file's one deliberate rule -- case 1 names no CMD_* macro at
 * all -- true without exception. */
void test_admission_truth_table_over_every_cmd_value(void) {
    for (int c = 0; c <= 255; c++) {
        bool expected;
        switch (c) {
            case 1:
            case 2:
            case 3:
            case 4:
            case 5:
            case 6:
            case 9:
            case 10:
            case 16:
                expected = true;
                break;
            default:
                expected = false;
                break;
        }
        char msg[48];
        snprintf(msg, sizeof(msg), "is_memory_cmd(%d) mismatch", c);
        TEST_ASSERT_EQUAL_MESSAGE(expected, is_memory_cmd((uint8_t)c), msg);
    }
}

/* Case 1b — a count assertion, deliberately separate from case 1's
 * membership loop (Phase 151, LOCK-02). A truth-table-only change can be
 * satisfied by two compensating edits (e.g. adding one true and removing
 * one other true, leaving membership subtly wrong but the count right by
 * accident is not possible here, and the inverse -- membership right but
 * the count test absent -- is exactly the gap this leg closes); a direct
 * count of how many of the 256 values admit cannot be satisfied that way
 * because it is computed independently of the switch statement above. */
void test_admission_count_is_exactly_nine(void) {
    int count = 0;
    for (int c = 0; c <= 255; c++) {
        if (is_memory_cmd((uint8_t)c)) {
            count++;
        }
    }
    TEST_ASSERT_EQUAL_MESSAGE(9, count,
        "is_memory_cmd() must admit exactly nine of the 256 possible uint8_t values (Phase 151, LOCK-02)");
}

/* Case 2 — cmd 7 and 8 (CMD_DEV_ADDRESS / CMD_DEV_REGISTER) are excluded.
 * These two macros are themselves defined inside a `#ifdef DEV_TOOLS` block
 * in firestarter.h:42-45, so this suite MUST NOT name them — doing so would
 * fail to compile under [env:native_nodevtools]. Bare numeric literals are
 * used instead, exactly the idiom firestarter_app's
 * test_revision_constants_parity.py:110-112 already uses for the identical
 * reason: "CMD_DEV_ADDRESS and CMD_DEV_REGISTER are #ifdef DEV_TOOLS in
 * firmware -- assert Python values as standalone literals only."
 *
 * This exclusion is D-01's deliberate safety tightening: a release build
 * previously ran json_parse AND configure_memory for cmd 7/8 before
 * refusing them at loop()'s default: with MSG_ERR_UNKNOWN_CMD -- i.e. it
 * configured a memory handler for a command it was about to refuse. After
 * this change it no longer does; cmd 7/8 keep their MSG_ERR_UNKNOWN_CMD
 * refusal in a release build, unchanged. */
void test_admission_rejects_dev_tool_ordinals_7_and_8(void) {
    TEST_ASSERT_FALSE_MESSAGE(is_memory_cmd(7),
        "cmd 7 (CMD_DEV_ADDRESS, DEV_TOOLS-conditional) must not be admitted");
    TEST_ASSERT_FALSE_MESSAGE(is_memory_cmd(8),
        "cmd 8 (CMD_DEV_REGISTER, DEV_TOOLS-conditional) must not be admitted");
}

/* Boundary controls around the new ninth value, 16 (CMD_LOCK_STATUS),
 * (LOCK-02). Both as bare numeric literals, matching case 1's
 * bare-literal idiom: 15 is CMD_HW_VERSION, the highest pre-existing
 * command, and must remain false; 17 is the first value above the new
 * ninth admission and must be false too, proving the growth stopped at
 * exactly one new value rather than opening a wider range. */
void test_admission_boundary_around_cmd_lock_status(void) {
    TEST_ASSERT_FALSE_MESSAGE(is_memory_cmd(15),
        "cmd 15 (CMD_HW_VERSION, highest pre-existing command) must not be admitted");
    TEST_ASSERT_FALSE_MESSAGE(is_memory_cmd(17),
        "cmd 17 (first value above the new ninth admission, 16) must not be admitted");
}

/* Case 3 — CMD_IDLE (0), RESEARCH F-B2's third behaviour delta. Today an
 * explicit {"cmd":0} frame satisfies the old `cmd < CMD_READ_VPP` guard in
 * both build configurations, runs json_parse and configure_memory, and
 * produces two error frames (0xBB MSG_ERR_PROTOCOL_NOT_IMPLEMENTED, then
 * MSG_ERR_SETUP). After is_memory_cmd() it falls to loop()'s existing
 * `case CMD_IDLE: break;` and produces silence instead. Accepted
 * deliberately in Plan 119-02 Task 2: CMD_IDLE is a firmware-internal
 * state, not a command any shipped host path emits. */
void test_admission_rejects_cmd_idle_zero(void) {
    TEST_ASSERT_FALSE_MESSAGE(is_memory_cmd(CMD_IDLE),
        "CMD_IDLE (0) must not be admitted -- RESEARCH F-B2's third delta");
}

/* Case 4 — a sample of non-memory commands unconditionally defined in both
 * build configurations. Safe to name by macro because none is
 * DEV_TOOLS-gated. */
void test_admission_rejects_non_memory_commands(void) {
    TEST_ASSERT_FALSE_MESSAGE(is_memory_cmd(CMD_READ_VPP), "CMD_READ_VPP must not be admitted");
    TEST_ASSERT_FALSE_MESSAGE(is_memory_cmd(CMD_READ_VPE), "CMD_READ_VPE must not be admitted");
    TEST_ASSERT_FALSE_MESSAGE(is_memory_cmd(CMD_FW_VERSION), "CMD_FW_VERSION must not be admitted");
    TEST_ASSERT_FALSE_MESSAGE(is_memory_cmd(CMD_CONFIG), "CMD_CONFIG must not be admitted");
    TEST_ASSERT_FALSE_MESSAGE(is_memory_cmd(CMD_HW_VERSION), "CMD_HW_VERSION must not be admitted");
}

int main(int argc, char** argv) {
    (void)argc;
    (void)argv;
    UNITY_BEGIN();

    RUN_TEST(test_admission_truth_table_over_every_cmd_value);
    RUN_TEST(test_admission_count_is_exactly_nine);
    RUN_TEST(test_admission_rejects_dev_tool_ordinals_7_and_8);
    RUN_TEST(test_admission_boundary_around_cmd_lock_status);
    RUN_TEST(test_admission_rejects_cmd_idle_zero);
    RUN_TEST(test_admission_rejects_non_memory_commands);

    return UNITY_END();
}
