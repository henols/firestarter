/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 *
 * Phase 138 Plan 03 (PREP-03 / D-01 / D-02 / D-04) — captures the pre-change
 * v1.31 27C write loop's merged strobe+timing stream, for all three EPROM
 * protocols (0x07/0x08/0x0B), on a small synthetic block, from the REAL,
 * UNMODIFIED eprom_write_execute.
 *
 * Task 2 (this commit's slice): the skeleton only. Two smoke cases prove the
 * timing hook actually fires — via fakeit's .AlwaysDo, NOT a definition in
 * the shared .inc (ArduinoFake DEFINES delay()/delayMicroseconds() itself as
 * free functions; a second definition would be a link error) — before any
 * real protocol case exists. Task 3 adds the three protocol cases that drive
 * the real production write loop.
 *
 * Fakeit's void-returning .AlwaysDo (MethodStubbingProgress<void,
 * arglist...>::AlwaysDo(std::function<void(...)> method), a real specialised
 * overload in this repo's pinned fakeit.hpp / ArduinoFake 0.4.0) compiles
 * directly against delay()/delayMicroseconds()'s void signatures below — no
 * adaptation to the non-void serial_read_mock.h / test_rurp_log_id.cpp idiom
 * (both of which wrap a value-returning method) was needed.
 */

#include <Arduino.h>
#include <ArduinoFake.h>
#include <unity.h>
#include <string.h>
#include <stdio.h>

extern "C" {
#include "memory.h"
}
#include "firestarter.h"

#include "../_shared/eprom_v131_expected.h"

using namespace fakeit;

/* host_stubs.cpp's reset seam (Pitfall 5 / 138-RESEARCH.md) — must run after
 * configure_memory, which itself writes address 0
 * (mem_util_set_address(handle, 0), memory.cpp:93). */
extern "C" void reset_register_cache(uint8_t lsb, uint8_t msb, rurp_register_t ctrl);

/* timing_push itself is NOT one of eprom_v131_expected.h's twelve read
 * accessors (that header declares only the six-strobe/six-timing READ side,
 * "declared once here so consumers get them from a single place") — it is
 * the WRITE entry point only the suite that installs the fakeit hooks below
 * needs, so it is declared here, not there. Mirrors timing_push's own
 * host_stubs_common.inc doc comment: extern "C", not static, precisely so
 * this setUp() lambda can call it. */
extern "C" void timing_push(uint8_t kind, uint32_t us);

/* ─────────────────────────────────────────────────────────────────────────
 * setUp / tearDown
 * ───────────────────────────────────────────────────────────────────────── */

void setUp(void) {
    ArduinoFakeReset();
    When(OverloadedMethod(ArduinoFake(Serial), write, size_t(uint8_t))).AlwaysReturn(1);
    When(OverloadedMethod(ArduinoFake(Serial), write, size_t(const uint8_t*, size_t))).AlwaysReturn(1);
    When(Method(ArduinoFake(Serial), flush)).AlwaysReturn();

    /* THE hook (D-02). delay()/delayMicroseconds() are free functions
     * DEFINED by ArduinoFake's FunctionFake.cpp, not stubbed anywhere in the
     * shared .inc — every suite that reaches them mocks them in its own
     * setUp(), and this is the one place in THIS suite that turns a mocked
     * call into a recorded timing entry, via timing_push() (Task 1, opt-in
     * guard HOST_STUBS_RECORD_TIMING). Capture-less lambdas: timing_push is
     * a free extern "C" symbol, nothing needs capturing. Do not remove these
     * as "unused" — every protocol case's cadence depends on them. */
    When(Method(ArduinoFake(), delayMicroseconds)).AlwaysDo([](unsigned int us) {
        timing_push(TIMING_KIND_DELAY_US, (uint32_t)us);
    });
    When(Method(ArduinoFake(), delay)).AlwaysDo([](unsigned long ms) {
        timing_push(TIMING_KIND_DELAY_MS, (uint32_t)ms);
    });
    When(Method(ArduinoFake(), millis)).AlwaysReturn(0);
    When(Method(ArduinoFake(), micros)).AlwaysReturn(0);

    clear_strobes();
    clear_timings();
    reset_register_cache(0x00, 0x00, 0x00);
}

void tearDown(void) {}

/* ─────────────────────────────────────────────────────────────────────────
 * Task 2 smoke cases — prove the skeleton before any protocol case exists.
 * ───────────────────────────────────────────────────────────────────────── */

/* setUp() alone must leave both recorders empty and un-overflowed — the
 * baseline every later case's assertions build on. */
void test_smoke_setup_leaves_both_recorders_clean(void) {
    TEST_ASSERT_EQUAL_MESSAGE(0, strobe_count(), "strobe_count after setUp");
    TEST_ASSERT_EQUAL_MESSAGE(0, timing_count(), "timing_count after setUp");
    TEST_ASSERT_EQUAL_MESSAGE(0, strobe_overflowed(), "strobe_overflowed after setUp");
    TEST_ASSERT_EQUAL_MESSAGE(0, timing_overflowed(), "timing_overflowed after setUp");
}

/* Drives delayMicroseconds()/delay() DIRECTLY — no production code involved
 * yet — and proves the hook fires: two timing entries, the right kinds, the
 * right values, both keyed to strobe index 0 (no strobe has been pushed at
 * all). This is the load-bearing, non-vacuous proof that the timing layer
 * works BEFORE any protocol case depends on it. */
void test_smoke_timing_hook_fires_for_delay_and_delaymicroseconds(void) {
    delayMicroseconds(7);
    delay(3);

    TEST_ASSERT_EQUAL_MESSAGE(2, timing_count(), "timing_count after direct delay calls");
    TEST_ASSERT_EQUAL_MESSAGE(0, timing_overflowed(), "timing_overflowed after direct delay calls");

    TEST_ASSERT_EQUAL_MESSAGE(TIMING_KIND_DELAY_US, timing_kind(0), "entry 0 kind");
    TEST_ASSERT_EQUAL_MESSAGE(7, timing_us(0), "entry 0 us");
    TEST_ASSERT_EQUAL_MESSAGE(0, timing_after_strobe(0), "entry 0 seq");

    TEST_ASSERT_EQUAL_MESSAGE(TIMING_KIND_DELAY_MS, timing_kind(1), "entry 1 kind");
    TEST_ASSERT_EQUAL_MESSAGE(3, timing_us(1), "entry 1 us");
    TEST_ASSERT_EQUAL_MESSAGE(0, timing_after_strobe(1), "entry 1 seq");
}

int main(int argc, char** argv) {
    (void)argc; (void)argv;
    UNITY_BEGIN();

    /* SMOKE: the skeleton (recorders, hook wiring) — before any protocol case */
    RUN_TEST(test_smoke_setup_leaves_both_recorders_clean);
    RUN_TEST(test_smoke_timing_hook_fires_for_delay_and_delaymicroseconds);

    return UNITY_END();
}
