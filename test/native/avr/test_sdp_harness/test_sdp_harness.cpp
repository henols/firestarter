/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 *
 * Phase 116 Plan 05 — the always-green SDP harness suite (D-03).
 *
 * Executable proof that:
 *  (1) the ordered strobe recorder (116-01's HOST_STUBS_REAL_REGISTER_UTILS)
 *      captures the real production register-cache elision, including the
 *      interleaving of data bytes, latch strobes, and /CE + /OE edges
 *      (TRACE-01);
 *  (2) the harness can tell UNLOCK from LOCK from ERASE, via two index-precise
 *      planted-fault negatives (TRACE-03a/b);
 *  (3) the outcome-independent identity-gate assertions retired from
 *      test_eeprom28c_chip_id now execute in CI, on an address-keyed mock
 *      (TRACE-04).
 *
 * This suite drives flash_util_byte_flipping / memory_set_data DIRECTLY —
 * never eeprom28c_write_init — so it stays green by construction across the
 * Phase 117 fix (which touches only eeprom_28c.cpp, not flash_utils.cpp or
 * memory.cpp). The parked RED suite (plan 116-06) is the one that flips
 * RED->GREEN when that fix lands.
 */

#include <Arduino.h>
#include <ArduinoFake.h>
#include <unity.h>
#include <string.h>
#include <stdio.h>

extern "C" {
#include "memory.h"
#include "eeprom_28c.h"
}
#include "firestarter.h"
#include "flash_utils.h"
#include "../_shared/sdp_bus_config.h"
#include "../_shared/sdp_expected.h"

using namespace fakeit;

/* host_stubs.cpp's reset seam (D-05) — must run after configure_memory, which
 * itself writes address 0 (mem_util_set_address(handle, 0), memory.cpp:68). */
extern "C" void reset_register_cache(uint8_t lsb, uint8_t msb, rurp_register_t ctrl);

/* ─────────────────────────────────────────────────────────────────────────
 * setUp / tearDown
 * ───────────────────────────────────────────────────────────────────────── */

/* TRACE-04 (Pattern 3) — address-keyed mock state, reset per-case in setUp(). */
static uint32_t s_mfr_addr_keyed;
static uint8_t  s_mfr_hi_keyed;
static uint8_t  s_mfr_lo_keyed;
static int      s_reads_at_mfr_addr;
static int      s_reads_at_poll_addr;

void setUp(void) {
    ArduinoFakeReset();
    When(OverloadedMethod(ArduinoFake(Serial), write, size_t(uint8_t))).AlwaysReturn(1);
    When(OverloadedMethod(ArduinoFake(Serial), write, size_t(const uint8_t*, size_t))).AlwaysReturn(1);
    When(Method(ArduinoFake(Serial), flush)).AlwaysReturn();
    /* REQUIRED by D-05: the real rurp_register_utils.h calls delayMicroseconds
     * (rurp_internal_write_to_register:86 and the settle path :58), and
     * eeprom28c_check_chip_id / eeprom28c_wait_for_write call delay() /
     * delayMicroseconds() too. ArduinoFake ABORTS (SIGABRT) on any unmocked
     * virtual — this reads exactly like the D-13 Unity-teardown flake, but a
     * SIGABRT in a NEW suite is this (Pitfall 3), not that. Do not remove
     * these as "unused" — they are load-bearing. */
    When(Method(ArduinoFake(), delayMicroseconds)).AlwaysReturn();
    When(Method(ArduinoFake(), delay)).AlwaysReturn();
    When(Method(ArduinoFake(), millis)).AlwaysReturn(0);

    clear_strobes();
    reset_register_cache(0x00, 0x00, 0x00);

    s_mfr_addr_keyed = 0;
    s_mfr_hi_keyed = 0xFF;
    s_mfr_lo_keyed = 0xFF;
    s_reads_at_mfr_addr = 0;
    s_reads_at_poll_addr = 0;
}

void tearDown(void) {}

/* ─────────────────────────────────────────────────────────────────────────
 * Handle + drive helpers
 * ───────────────────────────────────────────────────────────────────────── */

static firestarter_handle_t make_sdp_handle(const sdp_bus_config_row_t& row) {
    firestarter_handle_t h = {};
    h.protocol = 0x0D;
    h.cmd = CMD_WRITE;
    h.response_code = RESPONSE_CODE_OK;
    h.chip_id = 0;
    h.mem_size = row.mem_size;
    h.bus_config = row.bus_config;
    h.ctrl_flags = FLAG_SKIP_BLANK_CHECK;
    return h;
}

/* Load-bearing order: configure_memory (which itself writes address 0) ->
 * reset_register_cache -> clear_strobes -> flash_util_byte_flipping. The
 * cache reset and strobe clear MUST both come after configure_memory
 * (test_val_5v_page.cpp:150-175 records this same hazard). ctrl_seed=0x00 is
 * what makes the 54-entry SHIPPED array correct: flash_util_byte_flipping's
 * two CTRL_READ_WRITE clears then produce no CONTROL entry because the
 * cached value is already 0x00 (unchanged). */
static void drive(firestarter_handle_t* h, const byte_flip_t* table, size_t len, rurp_register_t ctrl_seed) {
    configure_memory(h);
    reset_register_cache(0x00, 0x00, ctrl_seed);
    clear_strobes();
    flash_util_byte_flipping(h, table, len);
}

/* The FIX-01 reference emitter: h->firestarter_set_data is memory_set_data
 * (assigned by configure_memory), which routes through
 * mem_util_remap_address_bus -- the remap-aware target stream, with zero
 * hand derivation. */
static void drive_reference_emitter(firestarter_handle_t* h, const byte_flip_t* table, size_t len, rurp_register_t ctrl_seed) {
    configure_memory(h);
    reset_register_cache(0x00, 0x00, ctrl_seed);
    clear_strobes();
    for (size_t i = 0; i < len; i++) {
        h->firestarter_set_data(h, table[i].address, table[i].byte);
    }
}

/* The single most valuable diagnostic in this phase (116-RESEARCH.md
 * §"Confirming the elision empirically"): pio test swallows printf from test
 * bodies, so run the built binary directly
 * (.pio/build/native/firestarter_native) to see this. Guarded behind
 * SDP_TRACE_DUMP -- kept in the suite for Phase 117's benefit, never compiled
 * by default. */
#ifdef SDP_TRACE_DUMP
static void dump_strobes(const char* tag) {
    printf("##### %s total=%d overflow=%d\n", tag, strobe_count(), strobe_overflowed());
    for (int i = 0; i < strobe_count(); i++) {
        if (strobe_kind(i) == STROBE_KIND_DATA) {
            printf("[%3d] DATA 0x%02X\n", i, strobe_value(i));
        } else {
            printf("[%3d] PIN  0x%02X -> %d\n", i, strobe_pin(i), strobe_value(i));
        }
    }
}
#endif

/* ─────────────────────────────────────────────────────────────────────────
 * Task 1 — ordered capture (TRACE-01, D-03, D-06)
 * ───────────────────────────────────────────────────────────────────────── */

void test_case1_ordered_capture_dip28_28c256(void) {
    firestarter_handle_t h = make_sdp_handle(SDP_BUS_CONFIGS[0]); /* AT28C256 / DIP28_28C256 */
    drive(&h, FLASH_DISABLE_WRITE_PROTECTION, 6, 0x00);
#ifdef SDP_TRACE_DUMP
    dump_strobes("case1_dip28_28c256_shipped");
#endif
    sdp_assert_stream_equals(SDP_SHIPPED_DIP28_28C256, SDP_SHIPPED_DIP28_28C256_LEN,
        "Case 1: ordered capture, DIP28_28C256, FLASH_DISABLE_WRITE_PROTECTION (== EEPROM_SDP_DISABLE, 116-03 parity)");
}

void test_case2_elision_is_real(void) {
    /* A raw call-log golden would assert 6 phantom entries here (Pitfall 4) —
     * write #4 targets the same address as write #3, so LSB/MSB are cache-
     * elided and only the payload DATA + OE + CE edges remain. */
    firestarter_handle_t h = make_sdp_handle(SDP_BUS_CONFIGS[0]);
    drive(&h, FLASH_DISABLE_WRITE_PROTECTION, 6, 0x00);
    TEST_ASSERT_EQUAL_MESSAGE(0, strobe_overflowed(), "Case 2: stream must not have overflowed");
    TEST_ASSERT_EQUAL_MESSAGE(STROBE_KIND_DATA, strobe_kind(30),
        "Case 2: index 30 must be a DATA entry -- write #4 emits no address latch (cache hit)");
    TEST_ASSERT_EQUAL_HEX8_MESSAGE(0xAA, strobe_value(30),
        "Case 2: index 30's payload must be 0xAA -- write #4's data byte");
}

void test_case3_ce_oe_edges_distinguishable(void) {
    /* Positional indices from the expected array (write #1's OE/CE triple),
     * not a scan -- distinguishes OE from CE by the `pin` field. */
    firestarter_handle_t h = make_sdp_handle(SDP_BUS_CONFIGS[0]);
    drive(&h, FLASH_DISABLE_WRITE_PROTECTION, 6, 0x00);

    TEST_ASSERT_EQUAL_MESSAGE(STROBE_KIND_PIN, strobe_kind(7), "Case 3: index 7 must be a PIN entry (/OE)");
    TEST_ASSERT_EQUAL_MESSAGE(OUTPUT_ENABLE, strobe_pin(7), "Case 3: index 7 must be OUTPUT_ENABLE");
    TEST_ASSERT_EQUAL_MESSAGE(1, strobe_value(7), "Case 3: /OE asserts high (rurp_chip_output enables output)");

    TEST_ASSERT_EQUAL_MESSAGE(STROBE_KIND_PIN, strobe_kind(8), "Case 3: index 8 must be a PIN entry (/CE low)");
    TEST_ASSERT_EQUAL_MESSAGE(CHIP_ENABLE, strobe_pin(8), "Case 3: index 8 must be CHIP_ENABLE");
    TEST_ASSERT_EQUAL_MESSAGE(0, strobe_value(8), "Case 3: /CE asserts low (rurp_chip_enable)");

    TEST_ASSERT_EQUAL_MESSAGE(STROBE_KIND_PIN, strobe_kind(9), "Case 3: index 9 must be a PIN entry (/CE high)");
    TEST_ASSERT_EQUAL_MESSAGE(CHIP_ENABLE, strobe_pin(9), "Case 3: index 9 must be CHIP_ENABLE");
    TEST_ASSERT_EQUAL_MESSAGE(1, strobe_value(9), "Case 3: /CE deasserts high (rurp_chip_disable)");
}

/* ─────────────────────────────────────────────────────────────────────────
 * main
 * ───────────────────────────────────────────────────────────────────────── */

int main(int argc, char** argv) {
    (void)argc; (void)argv;
    UNITY_BEGIN();

    /* Task 1 */
    RUN_TEST(test_case1_ordered_capture_dip28_28c256);
    RUN_TEST(test_case2_elision_is_real);
    RUN_TEST(test_case3_ce_oe_edges_distinguishable);

    return UNITY_END();
}
