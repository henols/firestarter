/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 *
 * Phase 116 Plan 05 — the single source of truth both Phase-116 native suites
 * (the always-green test_sdp_harness landed here, and the parked RED
 * test_eeprom28c_sdp landed in plan 116-06) assert their ordered strobe
 * streams against (D-06).
 *
 * Every literal array below was authored EMPIRICALLY from a recorded dump of
 * real production code (never hand-derived) — see 116-RESEARCH.md §"Confirming
 * the elision empirically before trusting an expected array" for the
 * dump-then-hand-check technique, and §F4/§F5 for the independently-produced
 * reference streams the captured dumps were cross-checked against.
 *
 * D-06 raises the bar over the closest in-tree analog
 * (test_val_5v_page.cpp:199-217's recording_contains_sdp_signature, a
 * sub-sequence scan): RESEARCH §F5 proves the shipped and remap-aware-fixed
 * streams have IDENTICAL length and, on DIP32_28C512_EEPROM, identical
 * address-byte values too — so containment or counting cannot discriminate
 * them. Only ORDERED, FULL-STREAM, element-by-element equality works, and
 * every comparator here is written to name the first diverging index rather
 * than merely report "not equal".
 */

#ifndef __SDP_EXPECTED_H__
#define __SDP_EXPECTED_H__

#include <stdint.h>
#include <unity.h>
#include "firestarter.h"  /* LEAST_SIGNIFICANT_BYTE / MOST_SIGNIFICANT_BYTE / OUTPUT_ENABLE / CHIP_ENABLE (via rurp_shield.h) */

/* Recorder accessors — symbols compiled because host_stubs.cpp defines
 * HOST_STUBS_REAL_REGISTER_UTILS (116-01). Declared once here so both
 * Phase-116 suites get them from a single place. */
extern "C" void    clear_strobes();
extern "C" int     strobe_count();
extern "C" int     strobe_overflowed();
extern "C" uint8_t strobe_kind(int i);
extern "C" uint8_t strobe_pin(int i);
extern "C" uint8_t strobe_value(int i);

/* Matches host_stubs_common.inc's strobe_entry_t exactly (kind/pin/value),
 * given its own name here since the recorder's own struct is TU-local
 * (defined inside the host_stubs.cpp .inc-include, not exported). */
typedef struct {
    uint8_t kind;
    uint8_t pin;
    uint8_t value;
} sdp_strobe_t;

/* Mirrors host_stubs_common.inc's `enum { STROBE_KIND_DATA = 1, STROBE_KIND_PIN = 2 };`
 * by value (that enum is TU-local to host_stubs.cpp, not exported) — kept as a
 * named constant here rather than a magic number in every literal array entry. */
#define STROBE_KIND_DATA 1
#define STROBE_KIND_PIN  2

/* Returns the index of the first element where the LIVE recorded stream
 * differs from `expected` (treating a length mismatch as a divergence at the
 * shorter length), or -1 when they are equal. Never counts anything — D-06's
 * anti-pattern list forbids it — every comparison is positional. */
static int sdp_first_divergence(const sdp_strobe_t* expected, int expected_len) {
    int recorded_len = strobe_count();
    int n = (recorded_len < expected_len) ? recorded_len : expected_len;
    for (int i = 0; i < n; i++) {
        if (strobe_kind(i) != expected[i].kind ||
            strobe_pin(i)  != expected[i].pin  ||
            strobe_value(i) != expected[i].value) {
            return i;
        }
    }
    if (recorded_len != expected_len) {
        return n; /* length mismatch, no earlier element difference: diverge at the shorter length */
    }
    return -1;
}

/* Asserts strobe_overflowed() is 0, asserts the recorded count equals
 * expected_len, then asserts element-by-element — and on mismatch, fails
 * with a message naming the diverging index and both the expected and
 * recorded {kind, pin, value} triple at that index. This is the ordered
 * full-stream equality D-06 requires; a sub-sequence scan or a count cannot
 * be substituted (116-RESEARCH.md §F5). */
static void sdp_assert_stream_equals(const sdp_strobe_t* expected, int expected_len, const char* ctx) {
    TEST_ASSERT_EQUAL_MESSAGE(0, strobe_overflowed(), ctx);
    TEST_ASSERT_EQUAL_MESSAGE(expected_len, strobe_count(), ctx);

    int div = sdp_first_divergence(expected, expected_len);
    if (div != -1) {
        char msg[320];
        int rec_len = strobe_count();
        if (div < rec_len && div < expected_len) {
            snprintf(msg, sizeof(msg),
                "%s: diverges at index %d -- expected {kind=%u pin=%u value=0x%02X}, recorded {kind=%u pin=%u value=0x%02X}",
                ctx, div,
                (unsigned)expected[div].kind, (unsigned)expected[div].pin, (unsigned)expected[div].value,
                (unsigned)strobe_kind(div), (unsigned)strobe_pin(div), (unsigned)strobe_value(div));
        } else {
            snprintf(msg, sizeof(msg),
                "%s: diverges at index %d (length mismatch -- expected_len=%d recorded_len=%d)",
                ctx, div, expected_len, rec_len);
        }
        TEST_FAIL_MESSAGE(msg);
    }
}

/* ─── SHIPPED stream ────────────────────────────────────────────────────────
 * flash_execute_command(EEPROM_SDP_DISABLE) / FLASH_DISABLE_WRITE_PROTECTION
 * driven directly through flash_util_byte_flipping (fu_flash_fast_address).
 *
 * KEY FINDING (recorded here, not just in the summary): fu_flash_fast_address
 * writes ONLY LEAST_SIGNIFICANT_BYTE and MOST_SIGNIFICANT_BYTE — it never
 * consults handle->bus_config and never writes CONTROL_REGISTER at all
 * (116-RESEARCH.md §F4 footnote 1). The shipped stream is therefore
 * IDENTICAL byte-for-byte across every 0x0D pinout (DIP28_28C256,
 * DIP28_28C64, DIP24_2816, DIP32_28C512_EEPROM) — this single array is the
 * shipped ground truth for all four. Cross-checked element-by-element
 * against 116-RESEARCH.md §F4's independently-produced 54-entry stream;
 * see 116-05-SUMMARY.md for confirmation the captured dump matched exactly.
 *
 * Elision is real and load-bearing: write #4 (address 0x5555, payload 0xAA)
 * emits NO address latch at all (index 30) because the cached LSB/MSB
 * already hold 0x55/0x55 from write #3 -- rurp_write_to_register returns
 * early (rurp_register_utils.h:28-37). A raw call-log golden would assert 6
 * phantom entries here that the shield never sees (Pitfall 4).
 */
static const sdp_strobe_t SDP_SHIPPED_DIP28_28C256[] = {
    /* write #1  addr 0x5555  payload 0xAA */
    {1, 0, 0x55}, {2, 1, 1}, {2, 1, 0},
    {1, 0, 0x55}, {2, 2, 1}, {2, 2, 0},
    {1, 0, 0xAA}, {2, 4, 1}, {2, 0x20, 0}, {2, 0x20, 1},
    /* write #2  addr 0x2AAA  payload 0x55 */
    {1, 0, 0xAA}, {2, 1, 1}, {2, 1, 0},
    {1, 0, 0x2A}, {2, 2, 1}, {2, 2, 0},
    {1, 0, 0x55}, {2, 4, 1}, {2, 0x20, 0}, {2, 0x20, 1},
    /* write #3  addr 0x5555  payload 0x80 */
    {1, 0, 0x55}, {2, 1, 1}, {2, 1, 0},
    {1, 0, 0x55}, {2, 2, 1}, {2, 2, 0},
    {1, 0, 0x80}, {2, 4, 1}, {2, 0x20, 0}, {2, 0x20, 1},
    /* write #4  addr 0x5555  payload 0xAA -- ELIDED: LSB/MSB cache hit, no address latch at all */
    {1, 0, 0xAA}, {2, 4, 1}, {2, 0x20, 0}, {2, 0x20, 1},
    /* write #5  addr 0x2AAA  payload 0x55 */
    {1, 0, 0xAA}, {2, 1, 1}, {2, 1, 0},
    {1, 0, 0x2A}, {2, 2, 1}, {2, 2, 0},
    {1, 0, 0x55}, {2, 4, 1}, {2, 0x20, 0}, {2, 0x20, 1},
    /* write #6  addr 0x5555  payload 0x20 (SDP-disable terminal byte) */
    {1, 0, 0x55}, {2, 1, 1}, {2, 1, 0},
    {1, 0, 0x55}, {2, 2, 1}, {2, 2, 0},
    {1, 0, 0x20}, {2, 4, 1}, {2, 0x20, 0}, {2, 0x20, 1},
};
#define SDP_SHIPPED_DIP28_28C256_LEN (int)(sizeof(SDP_SHIPPED_DIP28_28C256) / sizeof(SDP_SHIPPED_DIP28_28C256[0]))


#endif /* __SDP_EXPECTED_H__ */
