/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 *
 * Phase 138 Plan 03 (PREP-03 / D-01 / D-02 / D-04) — the single source of
 * truth the test_trace_eprom_v131 suite asserts its MERGED strobe+timing
 * stream against.
 *
 * Every literal array below (EPROM_V131_TRACE_PROTO_07/_08/_0B, pasted by
 * Phase 138 Plan 05 Task 1 from the dumps Plan 03 Task 3 produced) is
 * authored EMPIRICALLY from a recorded dump of real, UNMODIFIED production
 * code (eprom_write_execute driving the current, pre-v1.31 27C program
 * loop) — never hand-derived. This fixture freezes the pre-change v1.31
 * cadence so Phase 144's TEST-06 ("every changed strobe attributable to a
 * named decision") has something concrete to diff the new cadence against.
 * Plan 05 also switched the three protocol cases in test_trace_eprom_v131.cpp
 * from soundness-only assertions to full ordered positional equality
 * (v131_assert_stream_equals against the arrays below) as their primary
 * assertion, keeping the pre-existing overflow/determinism/response-code
 * checks alongside it.
 *
 * The trace records EVERY timing entry UNFILTERED — including the 1 µs
 * latch delay that rurp_internal_write_to_register emits after each
 * non-elided register latch. That entry looks like noise, but filtering it
 * out would hide the exact interleaving (strobe, then delay, then strobe)
 * this fixture exists to prove is captured at all. Filtering is a decision
 * this fixture deliberately declines to make.
 *
 * Unlike sdp_expected.h (which compares ONE stream — ordered strobes only),
 * this header compares a MERGED stream: strobes interleaved with the timing
 * entries that occurred between them, spliced positionally by the sequence
 * key each timing_entry_t carries (its `seq`, the strobe_count() value at
 * push time). See v131_merged_at() below for the exact splice rule.
 */

#ifndef __EPROM_V131_EXPECTED_H__
#define __EPROM_V131_EXPECTED_H__

#include <stdint.h>
#include <unity.h>
#include "firestarter.h"  /* pulls in rurp_shield.h -> LEAST_SIGNIFICANT_BYTE / MOST_SIGNIFICANT_BYTE / OUTPUT_ENABLE / CHIP_ENABLE, used only in provenance comments here, not by this header's own code */

/* Recorder accessors — symbols compiled because host_stubs.cpp defines
 * HOST_STUBS_REAL_REGISTER_UTILS (the six strobe accessors) AND
 * HOST_STUBS_RECORD_TIMING (the six timing accessors), both from Phase 138
 * Plan 03 Task 1. Declared once here so this suite gets all twelve from a
 * single place, mirroring sdp_expected.h's convention for the six strobe
 * accessors it alone needs. */
extern "C" void    clear_strobes();
extern "C" int     strobe_count();
extern "C" int     strobe_overflowed();
extern "C" uint8_t strobe_kind(int i);
extern "C" uint8_t strobe_pin(int i);
extern "C" uint8_t strobe_value(int i);

extern "C" void     clear_timings();
extern "C" int      timing_count();
extern "C" int      timing_overflowed();
extern "C" uint8_t  timing_kind(int i);
extern "C" uint32_t timing_us(int i);
extern "C" int      timing_after_strobe(int i);

/* A MERGED element. TU-local by design (the recorders' own structs are
 * TU-local too, defined inside host_stubs.cpp's .inc-include) — given its
 * own name here, exactly the rationale sdp_expected.h's sdp_strobe_t states
 * for the strobe-only case:
 *   - for a STROBE entry, `kind` is STROBE_KIND_DATA or STROBE_KIND_PIN,
 *     `pin`/`value` carry the strobe's pin+value, and `us` is 0.
 *   - for a TIMING entry, `kind` is TIMING_KIND_DELAY_US or
 *     TIMING_KIND_DELAY_MS, `us` carries the delay value, and `pin`/`value`
 *     are 0.
 * The two kind namespaces are disjoint by construction (1/2 vs 3/4), so a
 * single `kind` field unambiguously tells a reader which of the two shapes
 * applies without a separate discriminant. */
typedef struct {
    uint8_t  kind;
    uint8_t  pin;
    uint8_t  value;
    uint32_t us;
} v131_trace_entry_t;

/* Mirrors host_stubs_common.inc's two TU-local enums by value (both enums
 * are TU-local to host_stubs.cpp, not exported) — named constants here
 * rather than magic numbers in every literal array entry, exactly
 * sdp_expected.h's convention for STROBE_KIND_DATA/STROBE_KIND_PIN. */
#define STROBE_KIND_DATA     1
#define STROBE_KIND_PIN      2
#define TIMING_KIND_DELAY_US 3
#define TIMING_KIND_DELAY_MS 4

/* Total length of the merged stream: every strobe plus every timing. */
static int v131_merged_length() {
    return strobe_count() + timing_count();
}

/* Splice rule: every timing whose timing_after_strobe() equals i is emitted
 * IMMEDIATELY BEFORE strobe i (in push order among ties — the underlying
 * timing log is append-only, so increasing timing index IS push order);
 * timings whose key equals strobe_count() (i.e. they were pushed after the
 * last strobe, or no strobe exists at all) are emitted after the last
 * strobe. This is a two-pointer merge of two already-sorted sequences (the
 * strobe index 0..strobe_count() ascending, and timing_after_strobe(t)
 * ascending as t ascends, since s_strobe_count never decreases within one
 * drive) — O(merged length) per call, which is more than fast enough for
 * these small fixtures.
 *
 * Returns true and fills *out when k is a valid position; returns false
 * (leaving *out untouched) when k is out of range. */
static bool v131_merged_at(int k, v131_trace_entry_t* out) {
    int sc = strobe_count();
    int tc = timing_count();
    int pos = 0;
    int t = 0;
    for (int i = 0; i <= sc; i++) {
        while (t < tc && timing_after_strobe(t) == i) {
            if (pos == k) {
                out->kind  = timing_kind(t);
                out->pin   = 0;
                out->value = 0;
                out->us    = timing_us(t);
                return true;
            }
            pos++;
            t++;
        }
        if (i < sc) {
            if (pos == k) {
                out->kind  = strobe_kind(i);
                out->pin   = strobe_pin(i);
                out->value = strobe_value(i);
                out->us    = 0;
                return true;
            }
            pos++;
        }
    }
    return false;
}

/* Returns the index of the first element where the LIVE merged stream
 * differs from `expected` (treating a length mismatch as a divergence at
 * the shorter length), or -1 when they are equal. Never counts anything —
 * mirrors sdp_first_divergence's contract exactly: every comparison is
 * positional, over all four fields. */
static int v131_first_divergence(const v131_trace_entry_t* expected, int expected_len) {
    int recorded_len = v131_merged_length();
    int n = (recorded_len < expected_len) ? recorded_len : expected_len;
    for (int i = 0; i < n; i++) {
        v131_trace_entry_t rec;
        v131_merged_at(i, &rec);
        if (rec.kind != expected[i].kind ||
            rec.pin != expected[i].pin ||
            rec.value != expected[i].value ||
            rec.us != expected[i].us) {
            return i;
        }
    }
    if (recorded_len != expected_len) {
        return n; /* length mismatch, no earlier element difference: diverge at the shorter length */
    }
    return -1;
}

/* Asserts strobe_overflowed() == 0 AND timing_overflowed() == 0 FIRST (a
 * silently overflowed recorder can produce a truncated-but-matching prefix —
 * T-138-14), then asserts the merged length, then element-by-element — and
 * on mismatch, fails with a message naming the diverging index and BOTH the
 * expected and recorded {kind,pin,value,us} quadruple at that index. This is
 * the ordered full-stream equality D-04/D-06's precedent requires; a
 * sub-sequence scan or a count cannot be substituted. */
static void v131_assert_stream_equals(const v131_trace_entry_t* expected, int expected_len, const char* ctx) {
    TEST_ASSERT_EQUAL_MESSAGE(0, strobe_overflowed(), ctx);
    TEST_ASSERT_EQUAL_MESSAGE(0, timing_overflowed(), ctx);
    TEST_ASSERT_EQUAL_MESSAGE(expected_len, v131_merged_length(), ctx);

    int div = v131_first_divergence(expected, expected_len);
    if (div != -1) {
        char msg[400];
        int rec_len = v131_merged_length();
        if (div < rec_len && div < expected_len) {
            v131_trace_entry_t rec;
            v131_merged_at(div, &rec);
            snprintf(msg, sizeof(msg),
                "%s: diverges at index %d -- expected {kind=%u pin=%u value=0x%02X us=%lu}, recorded {kind=%u pin=%u value=0x%02X us=%lu}",
                ctx, div,
                (unsigned)expected[div].kind, (unsigned)expected[div].pin, (unsigned)expected[div].value, (unsigned long)expected[div].us,
                (unsigned)rec.kind, (unsigned)rec.pin, (unsigned)rec.value, (unsigned long)rec.us);
        } else {
            snprintf(msg, sizeof(msg),
                "%s: diverges at index %d (length mismatch -- expected_len=%d recorded_len=%d)",
                ctx, div, expected_len, rec_len);
        }
        TEST_FAIL_MESSAGE(msg);
    }
}

/* Snapshot the LIVE merged stream into caller-provided storage (used for
 * stream-versus-stream comparison — e.g. the determinism proof, which drives
 * the same protocol twice and compares two snapshots positionally, since
 * clear_strobes()/clear_timings() wipe the recorders between drives).
 * Returns the number of entries copied (capped at max_len). */
static int v131_snapshot(v131_trace_entry_t* out, int max_len) {
    int n = v131_merged_length();
    if (n > max_len) n = max_len;
    for (int i = 0; i < n; i++) {
        v131_merged_at(i, &out[i]);
    }
    return n;
}

/* ─── Frozen per-protocol arrays ─────────────────────────────────────────────
 * The three merged strobe+timing streams below are the pre-change v1.31
 * cadence, one per EPROM protocol, each frozen by Phase 138 Plan 05 Task 1
 * from the empirical dumps Plan 03 Task 3 produced (see each array's own
 * banner for chip/bus_config/seed detail and the non-obvious behaviour it
 * encodes).
 */

/* ─── EPROM_V131_TRACE_PROTO_07 -- AM27C512, protocol 0x07, DIP28_27512 ─────
 * Captured EMPIRICALLY: the built native_trace_v131 binary
 * (.pio/build/native_trace_v131/firestarter_native) run DIRECTLY with
 * EPROM_V131_TRACE_DUMP defined (`pio test` swallows printf) -- never
 * hand-derived. Chip AM27C512, pinout key DIP28_27512, pins=28,
 * mem_size=65536, bus_config { address_mask=0x0000FFFF, matching_lines=16,
 * rw_line=0xFF (none), vpp_line=0xFF (none), static_high_mask=0x00000000 }
 * (138-03-TRACE-CAPTURE.md §5, derived via gen_sdp_bus_config.py's own
 * derive_row against the shipped chip_database.json -- never invented).
 * Synthetic 4-byte block at address 0 (V131_SYNTHETIC_BLOCK,
 * trace_readback_seed calls in test_trace_eprom_v131.cpp):
 *   idx0 target=0x3C converge_after=0 (already-matching byte)
 *   idx1 target=0xFF converge_after=0 (erased-state byte)
 *   idx2 target=0x55 converge_after=2 (needs 3 passes -- the worst case)
 *   idx3 target=0xAA converge_after=1 (needs 2 passes)
 * 198 merged entries (142 strobes + 56 timings, 138-03-TRACE-CAPTURE.md §2),
 * exactly 3 passes, RESPONSE_CODE_OK, zero recorder overflow, proven
 * deterministic across two drives before this array was pasted.
 *
 * Non-obvious behaviour this array encodes (at least three, per D-04/D-06):
 *  1. The FIRST pass programs ALL FOUR bytes, including idx0 (already
 *     matching its target) and idx1 (the erased-state 0xFF byte) -- because
 *     eprom_write_execute's mismatch_bitmask starts memset to 0xFF
 *     (eprom.cpp:157), not derived from an actual first verify. Phase 141's
 *     LOOP-06 changes this "program everything unconditionally" behaviour;
 *     this array freezes it as it stands today.
 *  2. The program PULSE WIDTH GROWS across passes: 100us (pass 1) / 105us
 *     (pass 2) / 110us (pass 3) for the SAME byte (idx2) in THIS SINGLE
 *     capture -- eprom.cpp:177's adaptive
 *     `org_delay + org_delay * retries / NUMBER_OF_RETRIES` formula
 *     (org_delay=100, retries=1,2 on passes 2,3). A strobe-only recorder
 *     could never distinguish these three pulses from each other.
 *  3. The LSB/MSB/CONTROL_REGISTER register cache elides a latch whenever
 *     the newly-computed value equals the cached one (rurp_register_utils.h,
 *     Phase 116 D-06's own precedent) -- e.g. byte idx0's LSB/MSB latches are
 *     both elided on pass 1 because the cache already holds (0,0) from
 *     reset_register_cache. A raw call-log golden would assert phantom
 *     entries the shield never sees.
 *  4. Every NON-elided latch contributes its own 1us TIMING_KIND_DELAY_US
 *     entry (rurp_internal_write_to_register's post-strobe
 *     delayMicroseconds(1)) -- visible throughout this array as the `us=1`
 *     entries immediately following a register-latch pin pair.
 *  5. mem_util_calculate_top_address_register unconditionally ORs in
 *     CTRL_ADDRESS_LINE_17 (0x10) for `pins==28` chips ONLY (memory.cpp:169)
 *     -- visible here as the CONTROL_REGISTER correction (ctrl 0x85->0x95)
 *     on the very first byte of pass 1, then elided for every later byte in
 *     the same pass because the corrected value stays cache-stable.
 *
 * This is the PRE-CHANGE cadence, frozen for Phase 144's TEST-06 to diff the
 * new (post-v1.31) cadence against. A future divergence from this array is
 * expected work, not a regression -- PROJECT.md's own "not behavior-
 * preserving" caveat for this milestone.
 */
static const v131_trace_entry_t EPROM_V131_TRACE_PROTO_07[] = {
    /* one-time VPP-regulator enable (ctrl -> 0x81) + ms=500 */
    {1, 0x00, 0x81, 0UL}, {2, 0x08, 0x01, 0UL}, {3, 0x00, 0x00, 1UL}, {2, 0x08, 0x00, 0UL}, {4, 0x00, 0x00, 500UL},
    /* pass 1: VPE/route assert (ctrl -> 0x85) + ms=10 */
    {1, 0x00, 0x85, 0UL}, {2, 0x08, 0x01, 0UL}, {3, 0x00, 0x00, 1UL}, {2, 0x08, 0x00, 0UL}, {4, 0x00, 0x00, 10UL},
    /* pass 1: program byte@lsb=0x00 payload=0x3C pulse=100us */
    {2, 0x04, 0x01, 0UL},
    {1, 0x00, 0x95, 0UL}, {2, 0x08, 0x01, 0UL}, {3, 0x00, 0x00, 1UL}, {2, 0x08, 0x00, 0UL},
    {1, 0x00, 0x3C, 0UL}, {3, 0x00, 0x00, 3UL}, {2, 0x20, 0x00, 0UL}, {3, 0x00, 0x00, 100UL}, {2, 0x20, 0x01, 0UL},
    /* pass 1: program byte@lsb=0x01 payload=0xFF pulse=100us */
    {2, 0x04, 0x01, 0UL},
    {1, 0x00, 0x01, 0UL}, {2, 0x01, 0x01, 0UL}, {3, 0x00, 0x00, 1UL}, {2, 0x01, 0x00, 0UL},
    {1, 0x00, 0xFF, 0UL}, {3, 0x00, 0x00, 3UL}, {2, 0x20, 0x00, 0UL}, {3, 0x00, 0x00, 100UL}, {2, 0x20, 0x01, 0UL},
    /* pass 1: program byte@lsb=0x02 payload=0x55 pulse=100us */
    {2, 0x04, 0x01, 0UL},
    {1, 0x00, 0x02, 0UL}, {2, 0x01, 0x01, 0UL}, {3, 0x00, 0x00, 1UL}, {2, 0x01, 0x00, 0UL},
    {1, 0x00, 0x55, 0UL}, {3, 0x00, 0x00, 3UL}, {2, 0x20, 0x00, 0UL}, {3, 0x00, 0x00, 100UL}, {2, 0x20, 0x01, 0UL},
    /* pass 1: program byte@lsb=0x03 payload=0xAA pulse=100us */
    {2, 0x04, 0x01, 0UL},
    {1, 0x00, 0x03, 0UL}, {2, 0x01, 0x01, 0UL}, {3, 0x00, 0x00, 1UL}, {2, 0x01, 0x00, 0UL},
    {1, 0x00, 0xAA, 0UL}, {3, 0x00, 0x00, 3UL}, {2, 0x20, 0x00, 0UL}, {3, 0x00, 0x00, 100UL}, {2, 0x20, 0x01, 0UL},
    /* pass 1: VPE/route release (ctrl -> 0x91) */
    {1, 0x00, 0x91, 0UL}, {2, 0x08, 0x01, 0UL}, {3, 0x00, 0x00, 1UL}, {2, 0x08, 0x00, 0UL},
    /* pass 1: verify byte@lsb=0x00 */
    {2, 0x04, 0x00, 0UL},
    {1, 0x00, 0x00, 0UL}, {2, 0x01, 0x01, 0UL}, {3, 0x00, 0x00, 1UL}, {2, 0x01, 0x00, 0UL},
    {2, 0x20, 0x00, 0UL}, {3, 0x00, 0x00, 3UL}, {2, 0x20, 0x01, 0UL},
    /* pass 1: verify byte@lsb=0x01 */
    {2, 0x04, 0x00, 0UL},
    {1, 0x00, 0x01, 0UL}, {2, 0x01, 0x01, 0UL}, {3, 0x00, 0x00, 1UL}, {2, 0x01, 0x00, 0UL},
    {2, 0x20, 0x00, 0UL}, {3, 0x00, 0x00, 3UL}, {2, 0x20, 0x01, 0UL},
    /* pass 1: verify byte@lsb=0x02 */
    {2, 0x04, 0x00, 0UL},
    {1, 0x00, 0x02, 0UL}, {2, 0x01, 0x01, 0UL}, {3, 0x00, 0x00, 1UL}, {2, 0x01, 0x00, 0UL},
    {2, 0x20, 0x00, 0UL}, {3, 0x00, 0x00, 3UL}, {2, 0x20, 0x01, 0UL},
    /* pass 1: verify byte@lsb=0x03 */
    {2, 0x04, 0x00, 0UL},
    {1, 0x00, 0x03, 0UL}, {2, 0x01, 0x01, 0UL}, {3, 0x00, 0x00, 1UL}, {2, 0x01, 0x00, 0UL},
    {2, 0x20, 0x00, 0UL}, {3, 0x00, 0x00, 3UL}, {2, 0x20, 0x01, 0UL},
    /* pass 2: VPE/route assert (ctrl -> 0x95) + ms=10 */
    {1, 0x00, 0x95, 0UL}, {2, 0x08, 0x01, 0UL}, {3, 0x00, 0x00, 1UL}, {2, 0x08, 0x00, 0UL}, {4, 0x00, 0x00, 10UL},
    /* pass 2: program byte@lsb=0x02 payload=0x55 pulse=105us */
    {2, 0x04, 0x01, 0UL},
    {1, 0x00, 0x02, 0UL}, {2, 0x01, 0x01, 0UL}, {3, 0x00, 0x00, 1UL}, {2, 0x01, 0x00, 0UL},
    {1, 0x00, 0x55, 0UL}, {3, 0x00, 0x00, 3UL}, {2, 0x20, 0x00, 0UL}, {3, 0x00, 0x00, 105UL}, {2, 0x20, 0x01, 0UL},
    /* pass 2: program byte@lsb=0x03 payload=0xAA pulse=105us */
    {2, 0x04, 0x01, 0UL},
    {1, 0x00, 0x03, 0UL}, {2, 0x01, 0x01, 0UL}, {3, 0x00, 0x00, 1UL}, {2, 0x01, 0x00, 0UL},
    {1, 0x00, 0xAA, 0UL}, {3, 0x00, 0x00, 3UL}, {2, 0x20, 0x00, 0UL}, {3, 0x00, 0x00, 105UL}, {2, 0x20, 0x01, 0UL},
    /* pass 2: VPE/route release (ctrl -> 0x91) */
    {1, 0x00, 0x91, 0UL}, {2, 0x08, 0x01, 0UL}, {3, 0x00, 0x00, 1UL}, {2, 0x08, 0x00, 0UL},
    /* pass 2: verify byte@lsb=0x00 */
    {2, 0x04, 0x00, 0UL},
    {1, 0x00, 0x00, 0UL}, {2, 0x01, 0x01, 0UL}, {3, 0x00, 0x00, 1UL}, {2, 0x01, 0x00, 0UL},
    {2, 0x20, 0x00, 0UL}, {3, 0x00, 0x00, 3UL}, {2, 0x20, 0x01, 0UL},
    /* pass 2: verify byte@lsb=0x01 */
    {2, 0x04, 0x00, 0UL},
    {1, 0x00, 0x01, 0UL}, {2, 0x01, 0x01, 0UL}, {3, 0x00, 0x00, 1UL}, {2, 0x01, 0x00, 0UL},
    {2, 0x20, 0x00, 0UL}, {3, 0x00, 0x00, 3UL}, {2, 0x20, 0x01, 0UL},
    /* pass 2: verify byte@lsb=0x02 */
    {2, 0x04, 0x00, 0UL},
    {1, 0x00, 0x02, 0UL}, {2, 0x01, 0x01, 0UL}, {3, 0x00, 0x00, 1UL}, {2, 0x01, 0x00, 0UL},
    {2, 0x20, 0x00, 0UL}, {3, 0x00, 0x00, 3UL}, {2, 0x20, 0x01, 0UL},
    /* pass 2: verify byte@lsb=0x03 */
    {2, 0x04, 0x00, 0UL},
    {1, 0x00, 0x03, 0UL}, {2, 0x01, 0x01, 0UL}, {3, 0x00, 0x00, 1UL}, {2, 0x01, 0x00, 0UL},
    {2, 0x20, 0x00, 0UL}, {3, 0x00, 0x00, 3UL}, {2, 0x20, 0x01, 0UL},
    /* pass 3: VPE/route assert (ctrl -> 0x95) + ms=10 */
    {1, 0x00, 0x95, 0UL}, {2, 0x08, 0x01, 0UL}, {3, 0x00, 0x00, 1UL}, {2, 0x08, 0x00, 0UL}, {4, 0x00, 0x00, 10UL},
    /* pass 3: program byte@lsb=0x02 payload=0x55 pulse=110us */
    {2, 0x04, 0x01, 0UL},
    {1, 0x00, 0x02, 0UL}, {2, 0x01, 0x01, 0UL}, {3, 0x00, 0x00, 1UL}, {2, 0x01, 0x00, 0UL},
    {1, 0x00, 0x55, 0UL}, {3, 0x00, 0x00, 3UL}, {2, 0x20, 0x00, 0UL}, {3, 0x00, 0x00, 110UL}, {2, 0x20, 0x01, 0UL},
    /* pass 3: VPE/route release (ctrl -> 0x91) */
    {1, 0x00, 0x91, 0UL}, {2, 0x08, 0x01, 0UL}, {3, 0x00, 0x00, 1UL}, {2, 0x08, 0x00, 0UL},
    /* pass 3: verify byte@lsb=0x00 */
    {2, 0x04, 0x00, 0UL},
    {1, 0x00, 0x00, 0UL}, {2, 0x01, 0x01, 0UL}, {3, 0x00, 0x00, 1UL}, {2, 0x01, 0x00, 0UL},
    {2, 0x20, 0x00, 0UL}, {3, 0x00, 0x00, 3UL}, {2, 0x20, 0x01, 0UL},
    /* pass 3: verify byte@lsb=0x01 */
    {2, 0x04, 0x00, 0UL},
    {1, 0x00, 0x01, 0UL}, {2, 0x01, 0x01, 0UL}, {3, 0x00, 0x00, 1UL}, {2, 0x01, 0x00, 0UL},
    {2, 0x20, 0x00, 0UL}, {3, 0x00, 0x00, 3UL}, {2, 0x20, 0x01, 0UL},
    /* pass 3: verify byte@lsb=0x02 */
    {2, 0x04, 0x00, 0UL},
    {1, 0x00, 0x02, 0UL}, {2, 0x01, 0x01, 0UL}, {3, 0x00, 0x00, 1UL}, {2, 0x01, 0x00, 0UL},
    {2, 0x20, 0x00, 0UL}, {3, 0x00, 0x00, 3UL}, {2, 0x20, 0x01, 0UL},
    /* pass 3: verify byte@lsb=0x03 */
    {2, 0x04, 0x00, 0UL},
    {1, 0x00, 0x03, 0UL}, {2, 0x01, 0x01, 0UL}, {3, 0x00, 0x00, 1UL}, {2, 0x01, 0x00, 0UL},
    {2, 0x20, 0x00, 0UL}, {3, 0x00, 0x00, 3UL}, {2, 0x20, 0x01, 0UL},
};
#define EPROM_V131_TRACE_PROTO_07_LEN (int)(sizeof(EPROM_V131_TRACE_PROTO_07) / sizeof(EPROM_V131_TRACE_PROTO_07[0]))

/* ─── EPROM_V131_TRACE_PROTO_08 -- AM27C020, protocol 0x08, DIP32_27C020 ────
 * Captured EMPIRICALLY: the built native_trace_v131 binary run DIRECTLY with
 * EPROM_V131_TRACE_DUMP defined (`pio test` swallows printf) -- never
 * hand-derived. Chip AM27C020, pinout key DIP32_27C020, pins=32,
 * mem_size=262144, bus_config { address_mask=0x0011FFFF, matching_lines=17,
 * rw_line=0x16 (22), vpp_line=0x15 (21), static_high_mask=0x00000000 }
 * (138-03-TRACE-CAPTURE.md §5, derived via gen_sdp_bus_config.py's own
 * derive_row -- never invented). Same synthetic 4-byte block as _07 (address
 * 0, V131_SYNTHETIC_BLOCK): idx0=0x3C conv=0, idx1=0xFF conv=0, idx2=0x55
 * conv=2 (3 passes), idx3=0xAA conv=1 (2 passes). 221 merged entries (157
 * strobes + 64 timings, 138-03-TRACE-CAPTURE.md §2), exactly 3 passes,
 * RESPONSE_CODE_OK, zero recorder overflow, proven deterministic across two
 * drives before this array was pasted.
 *
 * Non-obvious behaviour this array encodes (at least three, per D-04/D-06):
 *  1. The FIRST pass programs ALL FOUR bytes unconditionally -- same
 *     memset(mismatch_bitmask, 0xFF, ...) start-state as _07 (eprom.cpp:157).
 *  2. The program PULSE WIDTH GROWS across passes on the same byte (idx2):
 *     100us / 105us / 110us -- eprom.cpp:177's adaptive
 *     `org_delay + org_delay * retries / NUMBER_OF_RETRIES` formula.
 *  3. vpp_line=0x15 exactly equals VPP_P1_32_DIP, so using_p1_as_vpp(handle)
 *     is TRUE for this chip (memory_utils.h) -- eprom_internal_set_control_
 *     register (eprom.cpp:319-325) remaps every CTRL_VPE_ENABLE assert/
 *     release to CTRL_VPP_P1_ENABLE instead. Visible here as ctrl 0x81->0x89
 *     (assert, +0x08 not +0x04) and 0x89->0x80 (release, -0x08) -- `_07`
 *     above shows +0x04/-0x04 for the identical call, because using_p1_as_
 *     vpp is FALSE there (vpp_line=0xFF sentinel).
 *  4. Every CONTROL_REGISTER write that clears CTRL_VPP_P1_ENABLE (a
 *     set->clear transition on that bit) carries an EXTRA 4us
 *     TIMING_KIND_DELAY_US settle entry immediately after it
 *     (rurp_internal_write_to_register's own P1-specific settle) -- `_07`
 *     never shows this entry at all, because `_07` never touches that bit.
 *  5. The LSB/MSB/CONTROL_REGISTER cache elides a latch whenever the
 *     newly-computed value equals the cached one; e.g. byte idx0's LSB/MSB
 *     latches are elided on pass 1 (cache already holds (0,0)), while its
 *     CONTROL correction (0x89->0x88, mem_util_calculate_top_address_register)
 *     still fires because that value has not yet been latched. Every
 *     non-elided latch contributes its own 1us TIMING_KIND_DELAY_US entry.
 *
 * This is the PRE-CHANGE cadence, frozen for Phase 144's TEST-06 to diff the
 * new (post-v1.31) cadence against. A future divergence from this array is
 * expected work, not a regression.
 */
static const v131_trace_entry_t EPROM_V131_TRACE_PROTO_08[] = {
    /* one-time VPP-regulator enable (ctrl -> 0x81) + ms=500 */
    {1, 0x00, 0x81, 0UL}, {2, 0x08, 0x01, 0UL}, {3, 0x00, 0x00, 1UL}, {2, 0x08, 0x00, 0UL}, {4, 0x00, 0x00, 500UL},
    /* pass 1: VPE/route assert (ctrl -> 0x89) + ms=10 */
    {1, 0x00, 0x89, 0UL}, {2, 0x08, 0x01, 0UL}, {3, 0x00, 0x00, 1UL}, {2, 0x08, 0x00, 0UL}, {4, 0x00, 0x00, 10UL},
    /* pass 1: program byte@lsb=0x00 payload=0x3C pulse=100us */
    {2, 0x04, 0x01, 0UL},
    {1, 0x00, 0x88, 0UL}, {2, 0x08, 0x01, 0UL}, {3, 0x00, 0x00, 1UL}, {2, 0x08, 0x00, 0UL},
    {1, 0x00, 0x3C, 0UL}, {3, 0x00, 0x00, 3UL}, {2, 0x20, 0x00, 0UL}, {3, 0x00, 0x00, 100UL}, {2, 0x20, 0x01, 0UL},
    /* pass 1: program byte@lsb=0x01 payload=0xFF pulse=100us */
    {2, 0x04, 0x01, 0UL},
    {1, 0x00, 0x01, 0UL}, {2, 0x01, 0x01, 0UL}, {3, 0x00, 0x00, 1UL}, {2, 0x01, 0x00, 0UL},
    {1, 0x00, 0xFF, 0UL}, {3, 0x00, 0x00, 3UL}, {2, 0x20, 0x00, 0UL}, {3, 0x00, 0x00, 100UL}, {2, 0x20, 0x01, 0UL},
    /* pass 1: program byte@lsb=0x02 payload=0x55 pulse=100us */
    {2, 0x04, 0x01, 0UL},
    {1, 0x00, 0x02, 0UL}, {2, 0x01, 0x01, 0UL}, {3, 0x00, 0x00, 1UL}, {2, 0x01, 0x00, 0UL},
    {1, 0x00, 0x55, 0UL}, {3, 0x00, 0x00, 3UL}, {2, 0x20, 0x00, 0UL}, {3, 0x00, 0x00, 100UL}, {2, 0x20, 0x01, 0UL},
    /* pass 1: program byte@lsb=0x03 payload=0xAA pulse=100us */
    {2, 0x04, 0x01, 0UL},
    {1, 0x00, 0x03, 0UL}, {2, 0x01, 0x01, 0UL}, {3, 0x00, 0x00, 1UL}, {2, 0x01, 0x00, 0UL},
    {1, 0x00, 0xAA, 0UL}, {3, 0x00, 0x00, 3UL}, {2, 0x20, 0x00, 0UL}, {3, 0x00, 0x00, 100UL}, {2, 0x20, 0x01, 0UL},
    /* pass 1: VPE/route release (ctrl -> 0x80) + p1_settle_us=4 */
    {1, 0x00, 0x80, 0UL}, {2, 0x08, 0x01, 0UL}, {3, 0x00, 0x00, 1UL}, {2, 0x08, 0x00, 0UL}, {3, 0x00, 0x00, 4UL},
    /* pass 1: verify byte@lsb=0x00 */
    {2, 0x04, 0x00, 0UL},
    {1, 0x00, 0x00, 0UL}, {2, 0x01, 0x01, 0UL}, {3, 0x00, 0x00, 1UL}, {2, 0x01, 0x00, 0UL},
    {1, 0x00, 0xC0, 0UL}, {2, 0x08, 0x01, 0UL}, {3, 0x00, 0x00, 1UL}, {2, 0x08, 0x00, 0UL},
    {2, 0x20, 0x00, 0UL}, {3, 0x00, 0x00, 3UL}, {2, 0x20, 0x01, 0UL},
    /* pass 1: verify byte@lsb=0x01 */
    {2, 0x04, 0x00, 0UL},
    {1, 0x00, 0x01, 0UL}, {2, 0x01, 0x01, 0UL}, {3, 0x00, 0x00, 1UL}, {2, 0x01, 0x00, 0UL},
    {2, 0x20, 0x00, 0UL}, {3, 0x00, 0x00, 3UL}, {2, 0x20, 0x01, 0UL},
    /* pass 1: verify byte@lsb=0x02 */
    {2, 0x04, 0x00, 0UL},
    {1, 0x00, 0x02, 0UL}, {2, 0x01, 0x01, 0UL}, {3, 0x00, 0x00, 1UL}, {2, 0x01, 0x00, 0UL},
    {2, 0x20, 0x00, 0UL}, {3, 0x00, 0x00, 3UL}, {2, 0x20, 0x01, 0UL},
    /* pass 1: verify byte@lsb=0x03 */
    {2, 0x04, 0x00, 0UL},
    {1, 0x00, 0x03, 0UL}, {2, 0x01, 0x01, 0UL}, {3, 0x00, 0x00, 1UL}, {2, 0x01, 0x00, 0UL},
    {2, 0x20, 0x00, 0UL}, {3, 0x00, 0x00, 3UL}, {2, 0x20, 0x01, 0UL},
    /* pass 2: VPE/route assert (ctrl -> 0xC8) + ms=10 */
    {1, 0x00, 0xC8, 0UL}, {2, 0x08, 0x01, 0UL}, {3, 0x00, 0x00, 1UL}, {2, 0x08, 0x00, 0UL}, {4, 0x00, 0x00, 10UL},
    /* pass 2: program byte@lsb=0x02 payload=0x55 pulse=105us */
    {2, 0x04, 0x01, 0UL},
    {1, 0x00, 0x02, 0UL}, {2, 0x01, 0x01, 0UL}, {3, 0x00, 0x00, 1UL}, {2, 0x01, 0x00, 0UL},
    {1, 0x00, 0x88, 0UL}, {2, 0x08, 0x01, 0UL}, {3, 0x00, 0x00, 1UL}, {2, 0x08, 0x00, 0UL},
    {1, 0x00, 0x55, 0UL}, {3, 0x00, 0x00, 3UL}, {2, 0x20, 0x00, 0UL}, {3, 0x00, 0x00, 105UL}, {2, 0x20, 0x01, 0UL},
    /* pass 2: program byte@lsb=0x03 payload=0xAA pulse=105us */
    {2, 0x04, 0x01, 0UL},
    {1, 0x00, 0x03, 0UL}, {2, 0x01, 0x01, 0UL}, {3, 0x00, 0x00, 1UL}, {2, 0x01, 0x00, 0UL},
    {1, 0x00, 0xAA, 0UL}, {3, 0x00, 0x00, 3UL}, {2, 0x20, 0x00, 0UL}, {3, 0x00, 0x00, 105UL}, {2, 0x20, 0x01, 0UL},
    /* pass 2: VPE/route release (ctrl -> 0x80) + p1_settle_us=4 */
    {1, 0x00, 0x80, 0UL}, {2, 0x08, 0x01, 0UL}, {3, 0x00, 0x00, 1UL}, {2, 0x08, 0x00, 0UL}, {3, 0x00, 0x00, 4UL},
    /* pass 2: verify byte@lsb=0x00 */
    {2, 0x04, 0x00, 0UL},
    {1, 0x00, 0x00, 0UL}, {2, 0x01, 0x01, 0UL}, {3, 0x00, 0x00, 1UL}, {2, 0x01, 0x00, 0UL},
    {1, 0x00, 0xC0, 0UL}, {2, 0x08, 0x01, 0UL}, {3, 0x00, 0x00, 1UL}, {2, 0x08, 0x00, 0UL},
    {2, 0x20, 0x00, 0UL}, {3, 0x00, 0x00, 3UL}, {2, 0x20, 0x01, 0UL},
    /* pass 2: verify byte@lsb=0x01 */
    {2, 0x04, 0x00, 0UL},
    {1, 0x00, 0x01, 0UL}, {2, 0x01, 0x01, 0UL}, {3, 0x00, 0x00, 1UL}, {2, 0x01, 0x00, 0UL},
    {2, 0x20, 0x00, 0UL}, {3, 0x00, 0x00, 3UL}, {2, 0x20, 0x01, 0UL},
    /* pass 2: verify byte@lsb=0x02 */
    {2, 0x04, 0x00, 0UL},
    {1, 0x00, 0x02, 0UL}, {2, 0x01, 0x01, 0UL}, {3, 0x00, 0x00, 1UL}, {2, 0x01, 0x00, 0UL},
    {2, 0x20, 0x00, 0UL}, {3, 0x00, 0x00, 3UL}, {2, 0x20, 0x01, 0UL},
    /* pass 2: verify byte@lsb=0x03 */
    {2, 0x04, 0x00, 0UL},
    {1, 0x00, 0x03, 0UL}, {2, 0x01, 0x01, 0UL}, {3, 0x00, 0x00, 1UL}, {2, 0x01, 0x00, 0UL},
    {2, 0x20, 0x00, 0UL}, {3, 0x00, 0x00, 3UL}, {2, 0x20, 0x01, 0UL},
    /* pass 3: VPE/route assert (ctrl -> 0xC8) + ms=10 */
    {1, 0x00, 0xC8, 0UL}, {2, 0x08, 0x01, 0UL}, {3, 0x00, 0x00, 1UL}, {2, 0x08, 0x00, 0UL}, {4, 0x00, 0x00, 10UL},
    /* pass 3: program byte@lsb=0x02 payload=0x55 pulse=110us */
    {2, 0x04, 0x01, 0UL},
    {1, 0x00, 0x02, 0UL}, {2, 0x01, 0x01, 0UL}, {3, 0x00, 0x00, 1UL}, {2, 0x01, 0x00, 0UL},
    {1, 0x00, 0x88, 0UL}, {2, 0x08, 0x01, 0UL}, {3, 0x00, 0x00, 1UL}, {2, 0x08, 0x00, 0UL},
    {1, 0x00, 0x55, 0UL}, {3, 0x00, 0x00, 3UL}, {2, 0x20, 0x00, 0UL}, {3, 0x00, 0x00, 110UL}, {2, 0x20, 0x01, 0UL},
    /* pass 3: VPE/route release (ctrl -> 0x80) + p1_settle_us=4 */
    {1, 0x00, 0x80, 0UL}, {2, 0x08, 0x01, 0UL}, {3, 0x00, 0x00, 1UL}, {2, 0x08, 0x00, 0UL}, {3, 0x00, 0x00, 4UL},
    /* pass 3: verify byte@lsb=0x00 */
    {2, 0x04, 0x00, 0UL},
    {1, 0x00, 0x00, 0UL}, {2, 0x01, 0x01, 0UL}, {3, 0x00, 0x00, 1UL}, {2, 0x01, 0x00, 0UL},
    {1, 0x00, 0xC0, 0UL}, {2, 0x08, 0x01, 0UL}, {3, 0x00, 0x00, 1UL}, {2, 0x08, 0x00, 0UL},
    {2, 0x20, 0x00, 0UL}, {3, 0x00, 0x00, 3UL}, {2, 0x20, 0x01, 0UL},
    /* pass 3: verify byte@lsb=0x01 */
    {2, 0x04, 0x00, 0UL},
    {1, 0x00, 0x01, 0UL}, {2, 0x01, 0x01, 0UL}, {3, 0x00, 0x00, 1UL}, {2, 0x01, 0x00, 0UL},
    {2, 0x20, 0x00, 0UL}, {3, 0x00, 0x00, 3UL}, {2, 0x20, 0x01, 0UL},
    /* pass 3: verify byte@lsb=0x02 */
    {2, 0x04, 0x00, 0UL},
    {1, 0x00, 0x02, 0UL}, {2, 0x01, 0x01, 0UL}, {3, 0x00, 0x00, 1UL}, {2, 0x01, 0x00, 0UL},
    {2, 0x20, 0x00, 0UL}, {3, 0x00, 0x00, 3UL}, {2, 0x20, 0x01, 0UL},
    /* pass 3: verify byte@lsb=0x03 */
    {2, 0x04, 0x00, 0UL},
    {1, 0x00, 0x03, 0UL}, {2, 0x01, 0x01, 0UL}, {3, 0x00, 0x00, 1UL}, {2, 0x01, 0x00, 0UL},
    {2, 0x20, 0x00, 0UL}, {3, 0x00, 0x00, 3UL}, {2, 0x20, 0x01, 0UL},
};
#define EPROM_V131_TRACE_PROTO_08_LEN (int)(sizeof(EPROM_V131_TRACE_PROTO_08) / sizeof(EPROM_V131_TRACE_PROTO_08[0]))

/* ─── EPROM_V131_TRACE_PROTO_0B -- AM2716, protocol 0x0B, DIP24_2716 ────────
 * Captured EMPIRICALLY: the built native_trace_v131 binary run DIRECTLY with
 * EPROM_V131_TRACE_DUMP defined (`pio test` swallows printf) -- never
 * hand-derived. Chip AM2716, pinout key DIP24_2716, pins=24, mem_size=2048,
 * bus_config { address_mask=0x000007FF, matching_lines=11, rw_line=0xFF
 * (none), vpp_line=0x0B (11), static_high_mask=0x00002000 (bit 13) }
 * (138-03-TRACE-CAPTURE.md §5, derived via gen_sdp_bus_config.py's own
 * derive_row -- never invented). Same synthetic 4-byte block as _07/_08
 * (address 0, V131_SYNTHETIC_BLOCK): idx0=0x3C conv=0, idx1=0xFF conv=0,
 * idx2=0x55 conv=2 (3 passes), idx3=0xAA conv=1 (2 passes). 201 merged
 * entries (142 strobes + 59 timings, 138-03-TRACE-CAPTURE.md §2), exactly 3
 * passes, RESPONSE_CODE_OK, zero recorder overflow, proven deterministic
 * across two drives before this array was pasted.
 *
 * Non-obvious behaviour this array encodes (at least three, per D-04/D-06):
 *  1. The FIRST pass programs ALL FOUR bytes unconditionally -- same
 *     memset(mismatch_bitmask, 0xFF, ...) start-state as _07/_08
 *     (eprom.cpp:157).
 *  2. The program PULSE WIDTH GROWS across passes on the same byte (idx2):
 *     500us / 525us / 550us -- the SAME eprom.cpp:177 adaptive formula as
 *     _07/_08, scaled from this chip's larger 500us base (C1's adjudication,
 *     infoic-field-dictionary.md:210-217 -- NOT the 50000us BUG-2 artifact
 *     gh#15 quoted).
 *  3. protocol==0x0B takes eprom_write_execute's OTHER one-time VPP-enable
 *     branch (eprom.cpp:145-147): ctrl -> 0x80 alone (CTRL_VPP_REGULATOR_
 *     ENABLE only), NOT 0x81 like _07/_08's CTRL_VPP_VPE_DROP_ENABLE path --
 *     visible as this array's very first entry.
 *  4. vpp_line=0x0B exactly equals VPP_P21_24_DIP, so using_p1_as_vpp(handle)
 *     is ALSO TRUE for this chip (a 24-pin, not 32-pin, P1-routing constant
 *     -- a different wiring reason than _08's), so every CTRL_VPE_ENABLE
 *     assert/release is likewise remapped to CTRL_VPP_P1_ENABLE, and every
 *     P1 set->clear transition carries the same extra 4us settle _08 shows.
 *  5. This chip's static_high_mask (bit 13) is realized as a PERMANENT
 *     MSB=0x20 contribution -- mem_util_remap_address_bus ORs
 *     static_high_mask into the remapped address before it is split into
 *     LSB/MSB, so byte idx0's very first access latches MSB 0x00->0x20 (a
 *     latch _07/_08 never show at all, since their remapped MSB stays 0
 *     throughout), then stays cache-elided for every later byte in this
 *     4-byte block. A raw call-log golden that assumed MSB==0x00 for a
 *     low-address block would be wrong for this one chip.
 *
 * This is the PRE-CHANGE cadence, frozen for Phase 144's TEST-06 to diff the
 * new (post-v1.31) cadence against. A future divergence from this array is
 * expected work, not a regression.
 */
static const v131_trace_entry_t EPROM_V131_TRACE_PROTO_0B[] = {
    /* one-time VPP-regulator enable (ctrl -> 0x80) + ms=500 */
    {1, 0x00, 0x80, 0UL}, {2, 0x08, 0x01, 0UL}, {3, 0x00, 0x00, 1UL}, {2, 0x08, 0x00, 0UL}, {4, 0x00, 0x00, 500UL},
    /* pass 1: VPE/route assert (ctrl -> 0x88) + ms=10 */
    {1, 0x00, 0x88, 0UL}, {2, 0x08, 0x01, 0UL}, {3, 0x00, 0x00, 1UL}, {2, 0x08, 0x00, 0UL}, {4, 0x00, 0x00, 10UL},
    /* pass 1: program byte@lsb=0x00 payload=0x3C pulse=500us */
    {2, 0x04, 0x01, 0UL},
    {1, 0x00, 0x20, 0UL}, {2, 0x02, 0x01, 0UL}, {3, 0x00, 0x00, 1UL}, {2, 0x02, 0x00, 0UL},
    {1, 0x00, 0x3C, 0UL}, {3, 0x00, 0x00, 3UL}, {2, 0x20, 0x00, 0UL}, {3, 0x00, 0x00, 500UL}, {2, 0x20, 0x01, 0UL},
    /* pass 1: program byte@lsb=0x01 payload=0xFF pulse=500us */
    {2, 0x04, 0x01, 0UL},
    {1, 0x00, 0x01, 0UL}, {2, 0x01, 0x01, 0UL}, {3, 0x00, 0x00, 1UL}, {2, 0x01, 0x00, 0UL},
    {1, 0x00, 0xFF, 0UL}, {3, 0x00, 0x00, 3UL}, {2, 0x20, 0x00, 0UL}, {3, 0x00, 0x00, 500UL}, {2, 0x20, 0x01, 0UL},
    /* pass 1: program byte@lsb=0x02 payload=0x55 pulse=500us */
    {2, 0x04, 0x01, 0UL},
    {1, 0x00, 0x02, 0UL}, {2, 0x01, 0x01, 0UL}, {3, 0x00, 0x00, 1UL}, {2, 0x01, 0x00, 0UL},
    {1, 0x00, 0x55, 0UL}, {3, 0x00, 0x00, 3UL}, {2, 0x20, 0x00, 0UL}, {3, 0x00, 0x00, 500UL}, {2, 0x20, 0x01, 0UL},
    /* pass 1: program byte@lsb=0x03 payload=0xAA pulse=500us */
    {2, 0x04, 0x01, 0UL},
    {1, 0x00, 0x03, 0UL}, {2, 0x01, 0x01, 0UL}, {3, 0x00, 0x00, 1UL}, {2, 0x01, 0x00, 0UL},
    {1, 0x00, 0xAA, 0UL}, {3, 0x00, 0x00, 3UL}, {2, 0x20, 0x00, 0UL}, {3, 0x00, 0x00, 500UL}, {2, 0x20, 0x01, 0UL},
    /* pass 1: VPE/route release (ctrl -> 0x80) + p1_settle_us=4 */
    {1, 0x00, 0x80, 0UL}, {2, 0x08, 0x01, 0UL}, {3, 0x00, 0x00, 1UL}, {2, 0x08, 0x00, 0UL}, {3, 0x00, 0x00, 4UL},
    /* pass 1: verify byte@lsb=0x00 */
    {2, 0x04, 0x00, 0UL},
    {1, 0x00, 0x00, 0UL}, {2, 0x01, 0x01, 0UL}, {3, 0x00, 0x00, 1UL}, {2, 0x01, 0x00, 0UL},
    {2, 0x20, 0x00, 0UL}, {3, 0x00, 0x00, 3UL}, {2, 0x20, 0x01, 0UL},
    /* pass 1: verify byte@lsb=0x01 */
    {2, 0x04, 0x00, 0UL},
    {1, 0x00, 0x01, 0UL}, {2, 0x01, 0x01, 0UL}, {3, 0x00, 0x00, 1UL}, {2, 0x01, 0x00, 0UL},
    {2, 0x20, 0x00, 0UL}, {3, 0x00, 0x00, 3UL}, {2, 0x20, 0x01, 0UL},
    /* pass 1: verify byte@lsb=0x02 */
    {2, 0x04, 0x00, 0UL},
    {1, 0x00, 0x02, 0UL}, {2, 0x01, 0x01, 0UL}, {3, 0x00, 0x00, 1UL}, {2, 0x01, 0x00, 0UL},
    {2, 0x20, 0x00, 0UL}, {3, 0x00, 0x00, 3UL}, {2, 0x20, 0x01, 0UL},
    /* pass 1: verify byte@lsb=0x03 */
    {2, 0x04, 0x00, 0UL},
    {1, 0x00, 0x03, 0UL}, {2, 0x01, 0x01, 0UL}, {3, 0x00, 0x00, 1UL}, {2, 0x01, 0x00, 0UL},
    {2, 0x20, 0x00, 0UL}, {3, 0x00, 0x00, 3UL}, {2, 0x20, 0x01, 0UL},
    /* pass 2: VPE/route assert (ctrl -> 0x88) + ms=10 */
    {1, 0x00, 0x88, 0UL}, {2, 0x08, 0x01, 0UL}, {3, 0x00, 0x00, 1UL}, {2, 0x08, 0x00, 0UL}, {4, 0x00, 0x00, 10UL},
    /* pass 2: program byte@lsb=0x02 payload=0x55 pulse=525us */
    {2, 0x04, 0x01, 0UL},
    {1, 0x00, 0x02, 0UL}, {2, 0x01, 0x01, 0UL}, {3, 0x00, 0x00, 1UL}, {2, 0x01, 0x00, 0UL},
    {1, 0x00, 0x55, 0UL}, {3, 0x00, 0x00, 3UL}, {2, 0x20, 0x00, 0UL}, {3, 0x00, 0x00, 525UL}, {2, 0x20, 0x01, 0UL},
    /* pass 2: program byte@lsb=0x03 payload=0xAA pulse=525us */
    {2, 0x04, 0x01, 0UL},
    {1, 0x00, 0x03, 0UL}, {2, 0x01, 0x01, 0UL}, {3, 0x00, 0x00, 1UL}, {2, 0x01, 0x00, 0UL},
    {1, 0x00, 0xAA, 0UL}, {3, 0x00, 0x00, 3UL}, {2, 0x20, 0x00, 0UL}, {3, 0x00, 0x00, 525UL}, {2, 0x20, 0x01, 0UL},
    /* pass 2: VPE/route release (ctrl -> 0x80) + p1_settle_us=4 */
    {1, 0x00, 0x80, 0UL}, {2, 0x08, 0x01, 0UL}, {3, 0x00, 0x00, 1UL}, {2, 0x08, 0x00, 0UL}, {3, 0x00, 0x00, 4UL},
    /* pass 2: verify byte@lsb=0x00 */
    {2, 0x04, 0x00, 0UL},
    {1, 0x00, 0x00, 0UL}, {2, 0x01, 0x01, 0UL}, {3, 0x00, 0x00, 1UL}, {2, 0x01, 0x00, 0UL},
    {2, 0x20, 0x00, 0UL}, {3, 0x00, 0x00, 3UL}, {2, 0x20, 0x01, 0UL},
    /* pass 2: verify byte@lsb=0x01 */
    {2, 0x04, 0x00, 0UL},
    {1, 0x00, 0x01, 0UL}, {2, 0x01, 0x01, 0UL}, {3, 0x00, 0x00, 1UL}, {2, 0x01, 0x00, 0UL},
    {2, 0x20, 0x00, 0UL}, {3, 0x00, 0x00, 3UL}, {2, 0x20, 0x01, 0UL},
    /* pass 2: verify byte@lsb=0x02 */
    {2, 0x04, 0x00, 0UL},
    {1, 0x00, 0x02, 0UL}, {2, 0x01, 0x01, 0UL}, {3, 0x00, 0x00, 1UL}, {2, 0x01, 0x00, 0UL},
    {2, 0x20, 0x00, 0UL}, {3, 0x00, 0x00, 3UL}, {2, 0x20, 0x01, 0UL},
    /* pass 2: verify byte@lsb=0x03 */
    {2, 0x04, 0x00, 0UL},
    {1, 0x00, 0x03, 0UL}, {2, 0x01, 0x01, 0UL}, {3, 0x00, 0x00, 1UL}, {2, 0x01, 0x00, 0UL},
    {2, 0x20, 0x00, 0UL}, {3, 0x00, 0x00, 3UL}, {2, 0x20, 0x01, 0UL},
    /* pass 3: VPE/route assert (ctrl -> 0x88) + ms=10 */
    {1, 0x00, 0x88, 0UL}, {2, 0x08, 0x01, 0UL}, {3, 0x00, 0x00, 1UL}, {2, 0x08, 0x00, 0UL}, {4, 0x00, 0x00, 10UL},
    /* pass 3: program byte@lsb=0x02 payload=0x55 pulse=550us */
    {2, 0x04, 0x01, 0UL},
    {1, 0x00, 0x02, 0UL}, {2, 0x01, 0x01, 0UL}, {3, 0x00, 0x00, 1UL}, {2, 0x01, 0x00, 0UL},
    {1, 0x00, 0x55, 0UL}, {3, 0x00, 0x00, 3UL}, {2, 0x20, 0x00, 0UL}, {3, 0x00, 0x00, 550UL}, {2, 0x20, 0x01, 0UL},
    /* pass 3: VPE/route release (ctrl -> 0x80) + p1_settle_us=4 */
    {1, 0x00, 0x80, 0UL}, {2, 0x08, 0x01, 0UL}, {3, 0x00, 0x00, 1UL}, {2, 0x08, 0x00, 0UL}, {3, 0x00, 0x00, 4UL},
    /* pass 3: verify byte@lsb=0x00 */
    {2, 0x04, 0x00, 0UL},
    {1, 0x00, 0x00, 0UL}, {2, 0x01, 0x01, 0UL}, {3, 0x00, 0x00, 1UL}, {2, 0x01, 0x00, 0UL},
    {2, 0x20, 0x00, 0UL}, {3, 0x00, 0x00, 3UL}, {2, 0x20, 0x01, 0UL},
    /* pass 3: verify byte@lsb=0x01 */
    {2, 0x04, 0x00, 0UL},
    {1, 0x00, 0x01, 0UL}, {2, 0x01, 0x01, 0UL}, {3, 0x00, 0x00, 1UL}, {2, 0x01, 0x00, 0UL},
    {2, 0x20, 0x00, 0UL}, {3, 0x00, 0x00, 3UL}, {2, 0x20, 0x01, 0UL},
    /* pass 3: verify byte@lsb=0x02 */
    {2, 0x04, 0x00, 0UL},
    {1, 0x00, 0x02, 0UL}, {2, 0x01, 0x01, 0UL}, {3, 0x00, 0x00, 1UL}, {2, 0x01, 0x00, 0UL},
    {2, 0x20, 0x00, 0UL}, {3, 0x00, 0x00, 3UL}, {2, 0x20, 0x01, 0UL},
    /* pass 3: verify byte@lsb=0x03 */
    {2, 0x04, 0x00, 0UL},
    {1, 0x00, 0x03, 0UL}, {2, 0x01, 0x01, 0UL}, {3, 0x00, 0x00, 1UL}, {2, 0x01, 0x00, 0UL},
    {2, 0x20, 0x00, 0UL}, {3, 0x00, 0x00, 3UL}, {2, 0x20, 0x01, 0UL},
};
#define EPROM_V131_TRACE_PROTO_0B_LEN (int)(sizeof(EPROM_V131_TRACE_PROTO_0B) / sizeof(EPROM_V131_TRACE_PROTO_0B[0]))

#endif /* __EPROM_V131_EXPECTED_H__ */
