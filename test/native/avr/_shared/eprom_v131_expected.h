/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 *
 * Phase 144 Plan 03 (TEST-06 / D-05 / D-06 / D-08) — the single source of
 * truth the test_trace_eprom_v131 suite asserts its MERGED strobe+timing
 * stream against, RE-CAPTURED at this phase's tip.
 *
 * Every literal array below (EPROM_V131_TRACE_PROTO_07/_08/_0B) is authored
 * EMPIRICALLY from a cold dump of the REAL, UNMODIFIED post-v1.31
 * eprom_write_execute — the per-byte pulse-to-verify loop landed by Phase
 * 141, the shared eprom_hv_route_mask() HV-routing resolver landed by Phase
 * 142, and the eprom_params_t table landed by Phase 140 all bear on this
 * capture — never hand-derived. Exact capture command sequence:
 *
 *   cd /workspaces/firestarter && PLATFORMIO_BUILD_FLAGS="-D EPROM_V131_TRACE_DUMP" \
 *     pio test -e native_trace_v131 --without-testing
 *   cd /workspaces/firestarter && .pio/build/native_trace_v131/firestarter_native \
 *     > /tmp/gsd-144/trace_dump.txt
 *
 * (`pio test` swallows printf — the dump must come from invoking the built
 * binary directly, per this suite's own #ifdef EPROM_V131_TRACE_DUMP block
 * at test_trace_eprom_v131.cpp:350-361.) Measured totals, read verbatim from
 * the dump's own banners: EPROM_V131_TRACE_PROTO_07 total=91,
 * EPROM_V131_TRACE_PROTO_08 total=115, EPROM_V131_TRACE_PROTO_0B total=59 —
 * all three with strobe_overflow=0 timing_overflow=0 (recorder caps are 512
 * each; 115 is 22 percent of cap, ample headroom). This capture is confirmed
 * distinct from `.planning/phases/141-per-byte-program-loop/141-NEW-TRACE.md`
 * section 5's stale pasteable arrays (91/119/59 there — the 0x08 total is
 * wrong by +4 — never used as a source for a single line below).
 *
 * The PRE-CHANGE cadence this fixture used to hold (198/221/201 merged
 * entries, one array per protocol) is preserved byte-for-byte, untouched, at
 * test/native/avr/_shared/eprom_v131_expected_prechange.h — git blob
 * ca3e09f164e6e1c541ecb63d15bbebf5bce41d70 (a git blob SHA is content-only
 * and path-independent, so this single fact is the whole of the rename's
 * proof). That file is #included by nothing; it is a historical artifact
 * plan 144-04 diffs the arrays below against, not a second live fixture.
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
 *
 * This fixture now arms the identity gate for v1.32 drift detection
 * (tests/golden/eprom_v131_trace_inventory.json's meta.frozen_for): a future
 * divergence from the three arrays below is a regression to investigate,
 * not expected work — the inverse framing of what this file's banner said
 * before this capture replaced it.
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
 * The three merged strobe+timing streams below are the POST-v1.31 cadence,
 * one per EPROM protocol, captured by Phase 144 Plan 03 from a cold dump of
 * the real, unmodified eprom_write_execute at this phase's tip (see the file
 * header above for the exact capture command sequence; see each array's own
 * banner below for its chip identity, bus_config and measured total).
 */

/* ─── EPROM_V131_TRACE_PROTO_07 -- AM27C512, protocol 0x07, DIP28_27512 ─────
 * Captured EMPIRICALLY by Phase 144 Plan 03: the built native_trace_v131
 * binary (.pio/build/native_trace_v131/firestarter_native) run DIRECTLY with
 * EPROM_V131_TRACE_DUMP defined (`pio test` swallows printf) against the
 * REAL, UNMODIFIED post-v1.31 eprom_write_execute -- never hand-derived.
 * Same chip, bus_config and synthetic 4-byte block as the frozen pre-change
 * capture (test/native/avr/_shared/eprom_v131_expected_prechange.h, blob
 * ca3e09f164e6e1c541ecb63d15bbebf5bce41d70): pins=28, mem_size=65536,
 * bus_config { address_mask=0x0000FFFF, matching_lines=16, rw_line=0xFF
 * (none), vpp_line=0xFF (none), static_high_mask=0x00000000 }; idx0
 * target=0x3C converge_after=0, idx1 target=0xFF converge_after=0, idx2
 * target=0x55 converge_after=2 (3 passes), idx3 target=0xAA converge_after=1
 * (2 passes).
 *
 * total=91 (was 198 pre-change), strobe_overflow=0, timing_overflow=0
 * (recorder caps are 512 each). RESPONSE_CODE_OK, zero recorder overflow,
 * proven deterministic across two drives before this array was pasted.
 * Every entry below is pasted verbatim from the recorder's own dump output
 * -- each retains only its own trailing positional-index comment, exactly
 * as the recorder emits it; no hand-authored per-segment comment is added
 * here the way the pre-change array had them, because a segment label the
 * recorder itself never emitted would be documentation dressed as data.
 * Plan 144-04 performs the structural, per-entry attribution this array's
 * shrink from 198 to 91 entries calls for.
 *
 * This is the POST-v1.31 cadence, now frozen for v1.32 drift detection
 * (tests/golden/eprom_v131_trace_inventory.json's meta.frozen_for) -- a
 * future divergence from this array is a regression to investigate, not
 * expected work.
 */
static const v131_trace_entry_t EPROM_V131_TRACE_PROTO_07[] = {
    {1, 0x00, 0x81, 0UL}, /* 0 */
    {2, 0x08, 0x01, 0UL}, /* 1 */
    {3, 0x00, 0x00, 1UL}, /* 2 */
    {2, 0x08, 0x00, 0UL}, /* 3 */
    {4, 0x00, 0x00, 500UL}, /* 4 */
    {2, 0x04, 0x00, 0UL}, /* 5 */
    {1, 0x00, 0x91, 0UL}, /* 6 */
    {2, 0x08, 0x01, 0UL}, /* 7 */
    {3, 0x00, 0x00, 1UL}, /* 8 */
    {2, 0x08, 0x00, 0UL}, /* 9 */
    {2, 0x20, 0x00, 0UL}, /* 10 */
    {3, 0x00, 0x00, 3UL}, /* 11 */
    {2, 0x20, 0x01, 0UL}, /* 12 */
    {2, 0x04, 0x00, 0UL}, /* 13 */
    {1, 0x00, 0x02, 0UL}, /* 14 */
    {2, 0x01, 0x01, 0UL}, /* 15 */
    {3, 0x00, 0x00, 1UL}, /* 16 */
    {2, 0x01, 0x00, 0UL}, /* 17 */
    {2, 0x20, 0x00, 0UL}, /* 18 */
    {3, 0x00, 0x00, 3UL}, /* 19 */
    {2, 0x20, 0x01, 0UL}, /* 20 */
    {2, 0x04, 0x01, 0UL}, /* 21 */
    {1, 0x00, 0x55, 0UL}, /* 22 */
    {3, 0x00, 0x00, 3UL}, /* 23 */
    {2, 0x20, 0x00, 0UL}, /* 24 */
    {3, 0x00, 0x00, 100UL}, /* 25 */
    {2, 0x20, 0x01, 0UL}, /* 26 */
    {2, 0x04, 0x00, 0UL}, /* 27 */
    {2, 0x20, 0x00, 0UL}, /* 28 */
    {3, 0x00, 0x00, 3UL}, /* 29 */
    {2, 0x20, 0x01, 0UL}, /* 30 */
    {2, 0x04, 0x01, 0UL}, /* 31 */
    {1, 0x00, 0x55, 0UL}, /* 32 */
    {3, 0x00, 0x00, 3UL}, /* 33 */
    {2, 0x20, 0x00, 0UL}, /* 34 */
    {3, 0x00, 0x00, 100UL}, /* 35 */
    {2, 0x20, 0x01, 0UL}, /* 36 */
    {2, 0x04, 0x00, 0UL}, /* 37 */
    {2, 0x20, 0x00, 0UL}, /* 38 */
    {3, 0x00, 0x00, 3UL}, /* 39 */
    {2, 0x20, 0x01, 0UL}, /* 40 */
    {2, 0x04, 0x00, 0UL}, /* 41 */
    {1, 0x00, 0x03, 0UL}, /* 42 */
    {2, 0x01, 0x01, 0UL}, /* 43 */
    {3, 0x00, 0x00, 1UL}, /* 44 */
    {2, 0x01, 0x00, 0UL}, /* 45 */
    {2, 0x20, 0x00, 0UL}, /* 46 */
    {3, 0x00, 0x00, 3UL}, /* 47 */
    {2, 0x20, 0x01, 0UL}, /* 48 */
    {2, 0x04, 0x01, 0UL}, /* 49 */
    {1, 0x00, 0xAA, 0UL}, /* 50 */
    {3, 0x00, 0x00, 3UL}, /* 51 */
    {2, 0x20, 0x00, 0UL}, /* 52 */
    {3, 0x00, 0x00, 100UL}, /* 53 */
    {2, 0x20, 0x01, 0UL}, /* 54 */
    {2, 0x04, 0x00, 0UL}, /* 55 */
    {2, 0x20, 0x00, 0UL}, /* 56 */
    {3, 0x00, 0x00, 3UL}, /* 57 */
    {2, 0x20, 0x01, 0UL}, /* 58 */
    {2, 0x04, 0x00, 0UL}, /* 59 */
    {1, 0x00, 0x00, 0UL}, /* 60 */
    {2, 0x01, 0x01, 0UL}, /* 61 */
    {3, 0x00, 0x00, 1UL}, /* 62 */
    {2, 0x01, 0x00, 0UL}, /* 63 */
    {2, 0x20, 0x00, 0UL}, /* 64 */
    {3, 0x00, 0x00, 3UL}, /* 65 */
    {2, 0x20, 0x01, 0UL}, /* 66 */
    {2, 0x04, 0x00, 0UL}, /* 67 */
    {1, 0x00, 0x01, 0UL}, /* 68 */
    {2, 0x01, 0x01, 0UL}, /* 69 */
    {3, 0x00, 0x00, 1UL}, /* 70 */
    {2, 0x01, 0x00, 0UL}, /* 71 */
    {2, 0x20, 0x00, 0UL}, /* 72 */
    {3, 0x00, 0x00, 3UL}, /* 73 */
    {2, 0x20, 0x01, 0UL}, /* 74 */
    {2, 0x04, 0x00, 0UL}, /* 75 */
    {1, 0x00, 0x02, 0UL}, /* 76 */
    {2, 0x01, 0x01, 0UL}, /* 77 */
    {3, 0x00, 0x00, 1UL}, /* 78 */
    {2, 0x01, 0x00, 0UL}, /* 79 */
    {2, 0x20, 0x00, 0UL}, /* 80 */
    {3, 0x00, 0x00, 3UL}, /* 81 */
    {2, 0x20, 0x01, 0UL}, /* 82 */
    {2, 0x04, 0x00, 0UL}, /* 83 */
    {1, 0x00, 0x03, 0UL}, /* 84 */
    {2, 0x01, 0x01, 0UL}, /* 85 */
    {3, 0x00, 0x00, 1UL}, /* 86 */
    {2, 0x01, 0x00, 0UL}, /* 87 */
    {2, 0x20, 0x00, 0UL}, /* 88 */
    {3, 0x00, 0x00, 3UL}, /* 89 */
    {2, 0x20, 0x01, 0UL}, /* 90 */
};
#define EPROM_V131_TRACE_PROTO_07_LEN (int)(sizeof(EPROM_V131_TRACE_PROTO_07) / sizeof(EPROM_V131_TRACE_PROTO_07[0]))

/* ─── EPROM_V131_TRACE_PROTO_08 -- AM27C020, protocol 0x08, DIP32_27C020 ────
 * Captured EMPIRICALLY by Phase 144 Plan 03: the built native_trace_v131
 * binary run DIRECTLY with EPROM_V131_TRACE_DUMP defined (`pio test`
 * swallows printf) against the REAL, UNMODIFIED post-v1.31
 * eprom_write_execute -- never hand-derived. Same chip, bus_config and
 * synthetic 4-byte block as the frozen pre-change capture
 * (eprom_v131_expected_prechange.h, blob
 * ca3e09f164e6e1c541ecb63d15bbebf5bce41d70): pins=32, mem_size=262144,
 * bus_config { address_mask=0x0011FFFF, matching_lines=17, rw_line=0x16
 * (22), vpp_line=0x15 (21), static_high_mask=0x00000000 }; same synthetic
 * block as _07: idx0=0x3C conv=0, idx1=0xFF conv=0, idx2=0x55 conv=2 (3
 * passes), idx3=0xAA conv=1 (2 passes). vpp_line=0x15 exactly equals
 * VPP_P1_32_DIP, so using_p1_as_vpp(handle) is TRUE for this chip.
 *
 * total=115 (was 221 pre-change), strobe_overflow=0, timing_overflow=0
 * (recorder caps are 512 each; 115 is 22 percent of cap). RESPONSE_CODE_OK,
 * zero recorder overflow, proven deterministic across two drives before
 * this array was pasted. Every entry below is pasted verbatim from the
 * recorder's own dump output -- each retains only its own trailing
 * positional-index comment; no hand-authored per-segment comment is added.
 * Plan 144-04 performs the structural, per-entry attribution this array's
 * shrink from 221 to 115 entries calls for.
 *
 * This is the POST-v1.31 cadence, now frozen for v1.32 drift detection
 * (tests/golden/eprom_v131_trace_inventory.json's meta.frozen_for) -- a
 * future divergence from this array is a regression to investigate, not
 * expected work.
 */
static const v131_trace_entry_t EPROM_V131_TRACE_PROTO_08[] = {
    {1, 0x00, 0x81, 0UL}, /* 0 */
    {2, 0x08, 0x01, 0UL}, /* 1 */
    {3, 0x00, 0x00, 1UL}, /* 2 */
    {2, 0x08, 0x00, 0UL}, /* 3 */
    {4, 0x00, 0x00, 500UL}, /* 4 */
    {2, 0x04, 0x00, 0UL}, /* 5 */
    {1, 0x00, 0xC0, 0UL}, /* 6 */
    {2, 0x08, 0x01, 0UL}, /* 7 */
    {3, 0x00, 0x00, 1UL}, /* 8 */
    {2, 0x08, 0x00, 0UL}, /* 9 */
    {2, 0x20, 0x00, 0UL}, /* 10 */
    {3, 0x00, 0x00, 3UL}, /* 11 */
    {2, 0x20, 0x01, 0UL}, /* 12 */
    {2, 0x04, 0x00, 0UL}, /* 13 */
    {1, 0x00, 0x02, 0UL}, /* 14 */
    {2, 0x01, 0x01, 0UL}, /* 15 */
    {3, 0x00, 0x00, 1UL}, /* 16 */
    {2, 0x01, 0x00, 0UL}, /* 17 */
    {2, 0x20, 0x00, 0UL}, /* 18 */
    {3, 0x00, 0x00, 3UL}, /* 19 */
    {2, 0x20, 0x01, 0UL}, /* 20 */
    {2, 0x04, 0x01, 0UL}, /* 21 */
    {1, 0x00, 0x80, 0UL}, /* 22 */
    {2, 0x08, 0x01, 0UL}, /* 23 */
    {3, 0x00, 0x00, 1UL}, /* 24 */
    {2, 0x08, 0x00, 0UL}, /* 25 */
    {1, 0x00, 0x55, 0UL}, /* 26 */
    {3, 0x00, 0x00, 3UL}, /* 27 */
    {2, 0x20, 0x00, 0UL}, /* 28 */
    {3, 0x00, 0x00, 100UL}, /* 29 */
    {2, 0x20, 0x01, 0UL}, /* 30 */
    {2, 0x04, 0x00, 0UL}, /* 31 */
    {1, 0x00, 0xC0, 0UL}, /* 32 */
    {2, 0x08, 0x01, 0UL}, /* 33 */
    {3, 0x00, 0x00, 1UL}, /* 34 */
    {2, 0x08, 0x00, 0UL}, /* 35 */
    {2, 0x20, 0x00, 0UL}, /* 36 */
    {3, 0x00, 0x00, 3UL}, /* 37 */
    {2, 0x20, 0x01, 0UL}, /* 38 */
    {2, 0x04, 0x01, 0UL}, /* 39 */
    {1, 0x00, 0x80, 0UL}, /* 40 */
    {2, 0x08, 0x01, 0UL}, /* 41 */
    {3, 0x00, 0x00, 1UL}, /* 42 */
    {2, 0x08, 0x00, 0UL}, /* 43 */
    {1, 0x00, 0x55, 0UL}, /* 44 */
    {3, 0x00, 0x00, 3UL}, /* 45 */
    {2, 0x20, 0x00, 0UL}, /* 46 */
    {3, 0x00, 0x00, 100UL}, /* 47 */
    {2, 0x20, 0x01, 0UL}, /* 48 */
    {2, 0x04, 0x00, 0UL}, /* 49 */
    {1, 0x00, 0xC0, 0UL}, /* 50 */
    {2, 0x08, 0x01, 0UL}, /* 51 */
    {3, 0x00, 0x00, 1UL}, /* 52 */
    {2, 0x08, 0x00, 0UL}, /* 53 */
    {2, 0x20, 0x00, 0UL}, /* 54 */
    {3, 0x00, 0x00, 3UL}, /* 55 */
    {2, 0x20, 0x01, 0UL}, /* 56 */
    {2, 0x04, 0x00, 0UL}, /* 57 */
    {1, 0x00, 0x03, 0UL}, /* 58 */
    {2, 0x01, 0x01, 0UL}, /* 59 */
    {3, 0x00, 0x00, 1UL}, /* 60 */
    {2, 0x01, 0x00, 0UL}, /* 61 */
    {2, 0x20, 0x00, 0UL}, /* 62 */
    {3, 0x00, 0x00, 3UL}, /* 63 */
    {2, 0x20, 0x01, 0UL}, /* 64 */
    {2, 0x04, 0x01, 0UL}, /* 65 */
    {1, 0x00, 0x80, 0UL}, /* 66 */
    {2, 0x08, 0x01, 0UL}, /* 67 */
    {3, 0x00, 0x00, 1UL}, /* 68 */
    {2, 0x08, 0x00, 0UL}, /* 69 */
    {1, 0x00, 0xAA, 0UL}, /* 70 */
    {3, 0x00, 0x00, 3UL}, /* 71 */
    {2, 0x20, 0x00, 0UL}, /* 72 */
    {3, 0x00, 0x00, 100UL}, /* 73 */
    {2, 0x20, 0x01, 0UL}, /* 74 */
    {2, 0x04, 0x00, 0UL}, /* 75 */
    {1, 0x00, 0xC0, 0UL}, /* 76 */
    {2, 0x08, 0x01, 0UL}, /* 77 */
    {3, 0x00, 0x00, 1UL}, /* 78 */
    {2, 0x08, 0x00, 0UL}, /* 79 */
    {2, 0x20, 0x00, 0UL}, /* 80 */
    {3, 0x00, 0x00, 3UL}, /* 81 */
    {2, 0x20, 0x01, 0UL}, /* 82 */
    {2, 0x04, 0x00, 0UL}, /* 83 */
    {1, 0x00, 0x00, 0UL}, /* 84 */
    {2, 0x01, 0x01, 0UL}, /* 85 */
    {3, 0x00, 0x00, 1UL}, /* 86 */
    {2, 0x01, 0x00, 0UL}, /* 87 */
    {2, 0x20, 0x00, 0UL}, /* 88 */
    {3, 0x00, 0x00, 3UL}, /* 89 */
    {2, 0x20, 0x01, 0UL}, /* 90 */
    {2, 0x04, 0x00, 0UL}, /* 91 */
    {1, 0x00, 0x01, 0UL}, /* 92 */
    {2, 0x01, 0x01, 0UL}, /* 93 */
    {3, 0x00, 0x00, 1UL}, /* 94 */
    {2, 0x01, 0x00, 0UL}, /* 95 */
    {2, 0x20, 0x00, 0UL}, /* 96 */
    {3, 0x00, 0x00, 3UL}, /* 97 */
    {2, 0x20, 0x01, 0UL}, /* 98 */
    {2, 0x04, 0x00, 0UL}, /* 99 */
    {1, 0x00, 0x02, 0UL}, /* 100 */
    {2, 0x01, 0x01, 0UL}, /* 101 */
    {3, 0x00, 0x00, 1UL}, /* 102 */
    {2, 0x01, 0x00, 0UL}, /* 103 */
    {2, 0x20, 0x00, 0UL}, /* 104 */
    {3, 0x00, 0x00, 3UL}, /* 105 */
    {2, 0x20, 0x01, 0UL}, /* 106 */
    {2, 0x04, 0x00, 0UL}, /* 107 */
    {1, 0x00, 0x03, 0UL}, /* 108 */
    {2, 0x01, 0x01, 0UL}, /* 109 */
    {3, 0x00, 0x00, 1UL}, /* 110 */
    {2, 0x01, 0x00, 0UL}, /* 111 */
    {2, 0x20, 0x00, 0UL}, /* 112 */
    {3, 0x00, 0x00, 3UL}, /* 113 */
    {2, 0x20, 0x01, 0UL}, /* 114 */
};
#define EPROM_V131_TRACE_PROTO_08_LEN (int)(sizeof(EPROM_V131_TRACE_PROTO_08) / sizeof(EPROM_V131_TRACE_PROTO_08[0]))

/* ─── EPROM_V131_TRACE_PROTO_0B -- AM2716, protocol 0x0B, DIP24_2716 ────────
 * Captured EMPIRICALLY by Phase 144 Plan 03: the built native_trace_v131
 * binary run DIRECTLY with EPROM_V131_TRACE_DUMP defined (`pio test`
 * swallows printf) against the REAL, UNMODIFIED post-v1.31
 * eprom_write_execute -- never hand-derived. Same chip, bus_config and
 * synthetic 4-byte block as the frozen pre-change capture
 * (eprom_v131_expected_prechange.h, blob
 * ca3e09f164e6e1c541ecb63d15bbebf5bce41d70): pins=24, mem_size=2048,
 * bus_config { address_mask=0x000007FF, matching_lines=11, rw_line=0xFF
 * (none), vpp_line=0x0B (11), static_high_mask=0x00002000 (bit 13) }; same
 * synthetic block as _07/_08: idx0=0x3C conv=0, idx1=0xFF conv=0, idx2=0x55
 * conv=2 (3 passes), idx3=0xAA conv=1 (2 passes). vpp_line=0x0B exactly
 * equals VPP_P21_24_DIP, so using_p1_as_vpp(handle) is also TRUE for this
 * chip.
 *
 * total=59 (was 201 pre-change), strobe_overflow=0, timing_overflow=0
 * (recorder caps are 512 each). RESPONSE_CODE_OK, zero recorder overflow,
 * proven deterministic across two drives before this array was pasted.
 * Every entry below is pasted verbatim from the recorder's own dump output
 * -- each retains only its own trailing positional-index comment; no
 * hand-authored per-segment comment is added. Plan 144-04 performs the
 * structural, per-entry attribution this array's shrink from 201 to 59
 * entries calls for.
 *
 * This is the POST-v1.31 cadence, now frozen for v1.32 drift detection
 * (tests/golden/eprom_v131_trace_inventory.json's meta.frozen_for) -- a
 * future divergence from this array is a regression to investigate, not
 * expected work.
 */
static const v131_trace_entry_t EPROM_V131_TRACE_PROTO_0B[] = {
    {1, 0x00, 0x80, 0UL}, /* 0 */
    {2, 0x08, 0x01, 0UL}, /* 1 */
    {3, 0x00, 0x00, 1UL}, /* 2 */
    {2, 0x08, 0x00, 0UL}, /* 3 */
    {4, 0x00, 0x00, 500UL}, /* 4 */
    {2, 0x04, 0x00, 0UL}, /* 5 */
    {1, 0x00, 0x20, 0UL}, /* 6 */
    {2, 0x02, 0x01, 0UL}, /* 7 */
    {3, 0x00, 0x00, 1UL}, /* 8 */
    {2, 0x02, 0x00, 0UL}, /* 9 */
    {2, 0x20, 0x00, 0UL}, /* 10 */
    {3, 0x00, 0x00, 3UL}, /* 11 */
    {2, 0x20, 0x01, 0UL}, /* 12 */
    {2, 0x04, 0x00, 0UL}, /* 13 */
    {1, 0x00, 0x02, 0UL}, /* 14 */
    {2, 0x01, 0x01, 0UL}, /* 15 */
    {3, 0x00, 0x00, 1UL}, /* 16 */
    {2, 0x01, 0x00, 0UL}, /* 17 */
    {2, 0x20, 0x00, 0UL}, /* 18 */
    {3, 0x00, 0x00, 3UL}, /* 19 */
    {2, 0x20, 0x01, 0UL}, /* 20 */
    {2, 0x04, 0x01, 0UL}, /* 21 */
    {1, 0x00, 0x55, 0UL}, /* 22 */
    {3, 0x00, 0x00, 3UL}, /* 23 */
    {2, 0x20, 0x00, 0UL}, /* 24 */
    {3, 0x00, 0x00, 500UL}, /* 25 */
    {2, 0x20, 0x01, 0UL}, /* 26 */
    {2, 0x04, 0x00, 0UL}, /* 27 */
    {2, 0x20, 0x00, 0UL}, /* 28 */
    {3, 0x00, 0x00, 3UL}, /* 29 */
    {2, 0x20, 0x01, 0UL}, /* 30 */
    {2, 0x04, 0x01, 0UL}, /* 31 */
    {1, 0x00, 0x55, 0UL}, /* 32 */
    {3, 0x00, 0x00, 3UL}, /* 33 */
    {2, 0x20, 0x00, 0UL}, /* 34 */
    {3, 0x00, 0x00, 500UL}, /* 35 */
    {2, 0x20, 0x01, 0UL}, /* 36 */
    {2, 0x04, 0x00, 0UL}, /* 37 */
    {2, 0x20, 0x00, 0UL}, /* 38 */
    {3, 0x00, 0x00, 3UL}, /* 39 */
    {2, 0x20, 0x01, 0UL}, /* 40 */
    {2, 0x04, 0x00, 0UL}, /* 41 */
    {1, 0x00, 0x03, 0UL}, /* 42 */
    {2, 0x01, 0x01, 0UL}, /* 43 */
    {3, 0x00, 0x00, 1UL}, /* 44 */
    {2, 0x01, 0x00, 0UL}, /* 45 */
    {2, 0x20, 0x00, 0UL}, /* 46 */
    {3, 0x00, 0x00, 3UL}, /* 47 */
    {2, 0x20, 0x01, 0UL}, /* 48 */
    {2, 0x04, 0x01, 0UL}, /* 49 */
    {1, 0x00, 0xAA, 0UL}, /* 50 */
    {3, 0x00, 0x00, 3UL}, /* 51 */
    {2, 0x20, 0x00, 0UL}, /* 52 */
    {3, 0x00, 0x00, 500UL}, /* 53 */
    {2, 0x20, 0x01, 0UL}, /* 54 */
    {2, 0x04, 0x00, 0UL}, /* 55 */
    {2, 0x20, 0x00, 0UL}, /* 56 */
    {3, 0x00, 0x00, 3UL}, /* 57 */
    {2, 0x20, 0x01, 0UL}, /* 58 */
};
#define EPROM_V131_TRACE_PROTO_0B_LEN (int)(sizeof(EPROM_V131_TRACE_PROTO_0B) / sizeof(EPROM_V131_TRACE_PROTO_0B[0]))

#endif /* __EPROM_V131_EXPECTED_H__ */
