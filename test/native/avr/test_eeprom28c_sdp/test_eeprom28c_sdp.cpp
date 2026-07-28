/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 *
 * Phase 116 Plan 06 authored this suite PARKED and RED-by-design
 * (v1.22 Phase 116 Plan 06, TRACE-02/TRACE-04/TRACE-06). As of v1.22 Phase
 * 117 commit 1 (D-03), the suite is ENABLED in platformio.ini's
 * [env:native] test_filter and runs under `pio test -e native`.
 *
 * This suite pins the exact ordered (LSB, MSB, data, CE) stream
 * eeprom28c_write_init emits, for each of the four 0x0D pinouts plus a
 * second DIP32 size band, and asserts it against the FIXED (post-Phase-117)
 * target — TRACE-02. At Phase 117 commit 1 it is RED against the
 * still-unfixed production tree; the verbatim capture is committed at
 * RED-BASELINE.md under "## Post-suite-edit RED baseline (Phase 117 commit
 * 1 — D-03)". It is GREEN from commit 2 onward, once plan 117-02 lands the
 * production fix.
 *
 * Phase 116's D-01 claimed that this suite's one-line test_filter addition
 * would itself BE the whole RED-to-GREEN proof. That did not hold
 * (117-CONTEXT.md D-01/D-02/D-03 supersede it): two structural conflicts
 * would have kept the suite RED post-fix for reasons unrelated to the fix —
 * the suite's own no-op `set_data` mock (the exact pointer FIX-01's emitter
 * is built on) and five assertions that encoded today's INIT-abort as the
 * expected outcome. The real flip required four edits: this test_filter
 * line, un-mocking `set_data` (D-01), flipping five response-code
 * assertions plus adding one new permanent severity-preservation regression
 * case (D-02), and this file's own suite-header rewrite.
 *
 * Cases 6-7 additionally carry TRACE-06's re-runnable evidence: with
 * CORRECTION 2's fix applied (D-12 originally mis-routed one of these two
 * into the always-green harness), both migrated identity-gate cases assert
 * the post-fix expectation — a matching identity must proceed, and a
 * FLAG_FORCE mismatch's WARNING severity must survive the completion path
 * (D-05: the completion poll never writes response_code). Case 8 is new at
 * Phase 117 commit 1: a permanent regression case proving the completion
 * poll can never destroy a prior WARNING, even when it never settles.
 *
 * Cases 9-12 are new at Phase 118 Plan 05 (D-08, OBS-02/OBS-03/OBS-05),
 * driving PRODUCTION eeprom28c_write_init via configure_memory dispatch
 * (never the harness's drive_reference_emitter):
 *  - Case 9: FLAG_SKIP_SDP_UNLOCK set -- the unlock sequence is provably
 *    absent from the recorded BUS stream, asserted on content and position
 *    (exact divergence index 0, plus an explicit walk over recorded
 *    STROBE_KIND_DATA values for EEPROM_SDP_DISABLE's own payload bytes),
 *    never on a bare strobe count.
 *  - Case 10: the flag-absent counterpart, from the SAME handle factory as
 *    Case 9, asserting the full SDP_FIXED_DIP28_28C256 stream -- the pair
 *    ships together so the contrast is one executable comparison.
 *  - Case 11: the t_BLC runtime budget WARN is observed to actually FIRE
 *    (an over-budget synthesised elapsed value via Plan 118-03's
 *    s_micros_ticks seam) and observed to NOT fire under the default
 *    elapsed value -- the anti-hollow pair for a check that would otherwise
 *    be indistinguishable from a dead branch.
 *  - Case 12: the exactly-two-new-serial-frames enumeration (and its
 *    exactly-one-WARN skip-path mirror), via a per-case Serial-frame
 *    capture reusing test_rurp_log_id.cpp's existing AlwaysDo idiom -- NOT
 *    a new general-purpose recorder (D-07 explicitly declined building
 *    one). This strengthens, but never replaces, D-07's PRIMARY assertion:
 *    the recorded BUS stream's byte-identity (Cases 1-3/10 here, and the
 *    _shared/ blob-SHA check in RED-BASELINE.md).
 *
 * Validation ceiling (RED-BASELINE.md carries this in full): every claim
 * this suite embodies is software-layer — code emits a sequence, code
 * asserts on it. No AT28C part was ever on the bench, and nothing here is
 * evidence about silicon state.
 */

#include <Arduino.h>
#include <ArduinoFake.h>
#include <unity.h>
#include <string.h>
#include <stdio.h>
#include <vector>

extern "C" {
#include "memory.h"
#include "eeprom_28c.h"
#include "messages.h"
}
#include "firestarter.h"
#include "flash_utils.h"
#include "../_shared/sdp_bus_config.h"
#include "../_shared/sdp_expected.h"

using namespace fakeit;

/* host_stubs.cpp's reset seam (D-05) — must run after configure_memory, which
 * itself writes address 0 (mem_util_set_address(handle, 0), memory.cpp:68). */
extern "C" void reset_register_cache(uint8_t lsb, uint8_t msb, rurp_register_t ctrl);

/* Plan 118-05 (D-08 constraint 1): EEPROM_SDP_DISABLE is the PRODUCTION
 * command table (external linkage granted at eeprom_28c.cpp:122, FIX-05
 * precedent -- test_sdp_harness.cpp:48 declares the identical extern).
 * Case 9's payload-byte-absence walk reads this exact array, never a
 * transcribed copy, so it stays byte-locked to whatever
 * eeprom28c_emit_command_sequence actually drives. */
extern const byte_flip_t EEPROM_SDP_DISABLE[6];

/* ─────────────────────────────────────────────────────────────────────────
 * setUp / tearDown
 * ───────────────────────────────────────────────────────────────────────── */

/* Address-keyed mock state (Pattern 3, migrated from the retired
 * test_eeprom28c_chip_id via test_sdp_harness), reset per-case in setUp().
 * Reused across ALL seven cases here: for cases 1-5 the identity axis is
 * irrelevant (chip_id == 0 skips eeprom28c_check_chip_id entirely) and the
 * mock's virgin 0xFF at 0x5555 is exactly what makes eeprom28c_wait_for_write
 * time out without contributing any further strobes to the recorded stream
 * (Task 1 acceptance criterion: strobe_overflowed() == 0, 2000 poll
 * iterations contribute zero strobes). */
static uint32_t s_mfr_addr_keyed;
static uint8_t  s_mfr_hi_keyed;
static uint8_t  s_mfr_lo_keyed;
static int      s_reads_at_mfr_addr;
static int      s_reads_at_poll_addr;
/* Case 8 (D-02, Phase 117 commit 1): when set, the 0x5555 poll address
 * toggles bit 0x40 on every read instead of returning a constant, so the
 * completion poll can never conclude. Reset false in setUp(). */
static bool     s_poll_addr_toggles;

/* Controllable micros() tick source (Plan 118-04's OBS-04 duration bracket:
 * eeprom28c_write_init reads micros() once immediately before
 * eeprom28c_emit_command_sequence's call and once immediately after, so
 * EXACTLY TWO reads occur per write_init drive). Indexed by call count
 * modulo 2 rather than an absolute count, so this stays correct even for a
 * drive helper that happens to call write_init more than once (none do
 * today). Default BOTH entries to 0 so elapsed == (ticks[1] - ticks[0]) ==
 * 0 -- the budget can never appear exceeded, which is what keeps all eight
 * existing cases in this file behaviourally identical to their pre-118-03
 * values. Plan 118-05's budget-exceeded case sets s_micros_ticks[1] to a
 * value that makes the elapsed exceed 6 * AT28C_TBLC_MAX_US before driving;
 * this array is that seam. Reset to {0, 0} (and the call counter to 0)
 * alongside the other file-static resets in setUp() below. */
static uint32_t s_micros_ticks[2];
static int      s_micros_call_count;

/* Plan 118-05 Task 2 (D-07 scope discipline): a PER-CASE Serial-frame
 * capture, reusing test_rurp_log_id.cpp:59-63's existing AlwaysDo idiom
 * verbatim (accumulate every Serial.write(uint8_t) byte into a host
 * std::vector). This is NOT the general-purpose serial-frame baseline
 * recorder D-07 explicitly declined building -- it lives local to THIS
 * suite, is cleared per-case in setUp() below alongside the other
 * file-static resets, and nothing here is added to test/native/avr/_shared/.
 * D-07's PRIMARY assertion stays the recorded BUS stream's byte-identity
 * (sdp_assert_stream_equals / the RED-BASELINE.md blob-SHA record); this
 * capture only strengthens the serial-channel half of OBS-05's claim. */
static std::vector<uint8_t> captured_frames;

/* Walks captured_frames using rurp_log_id()'s fixed, documented wire layout
 * (test_rurp_log_id.cpp's own comment: 4-byte magic, 2-byte big-endian
 * length, 1 id byte, params, 1 crc byte, 1 anchor byte) and appends each
 * frame's id byte, IN ORDER, to *out_ids. Never reads param count from a
 * message-id lookup table -- the length field alone is sufficient to find
 * the next frame's start, so this stays correct regardless of how many
 * params any given id carries. */
static void sdp_captured_frame_ids(std::vector<uint8_t>* out_ids) {
    size_t offset = 0;
    while (offset + 7 <= captured_frames.size()) {
        uint16_t len_value = (uint16_t)(((uint16_t)captured_frames[offset + 4] << 8) | captured_frames[offset + 5]);
        size_t frame_size = 4 + 2 + (size_t)len_value + 1;
        if (offset + frame_size > captured_frames.size()) {
            break; /* incomplete trailing frame -- not expected in these cases */
        }
        out_ids->push_back(captured_frames[offset + 6]);
        offset += frame_size;
    }
}

/* Content-order membership check over an already-enumerated id list --
 * never a count. */
static bool sdp_ids_contains(const std::vector<uint8_t>& ids, uint8_t id) {
    for (size_t i = 0; i < ids.size(); i++) {
        if (ids[i] == id) {
            return true;
        }
    }
    return false;
}

void setUp(void) {
    ArduinoFakeReset();
    /* Plan 118-05 Task 2: was AlwaysReturn(1) through Plan 118-04. Switched to
     * AlwaysDo so every byte is ALSO captured into captured_frames -- this is
     * additive/behaviourally-transparent to every existing case (none of
     * cases 1-8 ever inspects captured_frames), confirmed by re-running all
     * ten cases (1-8 plus the two Task-1 cases) at 10/10 before Task 2's new
     * cases were added (see 118-05-SUMMARY.md). */
    When(OverloadedMethod(ArduinoFake(Serial), write, size_t(uint8_t)))
        .AlwaysDo([](uint8_t b) -> size_t {
            captured_frames.push_back(b);
            return (size_t)1;
        });
    When(OverloadedMethod(ArduinoFake(Serial), write, size_t(const uint8_t*, size_t))).AlwaysReturn(1);
    When(Method(ArduinoFake(Serial), flush)).AlwaysReturn();
    /* REQUIRED (mirrors test_sdp_harness.cpp / D-05): the real
     * rurp_register_utils.h calls delayMicroseconds, and
     * eeprom28c_check_chip_id / eeprom28c_wait_for_write call delay() /
     * delayMicroseconds() too. ArduinoFake ABORTS (SIGABRT) on any unmocked
     * virtual. Do not remove these as "unused" — they are load-bearing. Plan
     * 118-04's OBS-04 duration bracket calls micros() twice per write_init
     * drive (immediately before and after
     * eeprom28c_emit_command_sequence's call); removing this mock produces
     * a SIGABRT indistinguishable from the deferred Unity-teardown flake
     * (D-13), not a compile error, so it is exactly as load-bearing as the
     * three mocks above it. */
    When(Method(ArduinoFake(), delayMicroseconds)).AlwaysReturn();
    When(Method(ArduinoFake(), delay)).AlwaysReturn();
    When(Method(ArduinoFake(), millis)).AlwaysReturn(0);
    When(Method(ArduinoFake(), micros)).AlwaysDo([]() -> unsigned long {
        unsigned long v = s_micros_ticks[s_micros_call_count % 2];
        s_micros_call_count++;
        return v;
    });

    clear_strobes();
    reset_register_cache(0x00, 0x00, 0x00);

    s_mfr_addr_keyed = 0;
    s_mfr_hi_keyed = 0xFF;
    s_mfr_lo_keyed = 0xFF;
    s_reads_at_mfr_addr = 0;
    s_reads_at_poll_addr = 0;
    s_poll_addr_toggles = false;
    s_micros_ticks[0] = 0;
    s_micros_ticks[1] = 0;
    s_micros_call_count = 0;
    captured_frames.clear();
}

void tearDown(void) {}

/* ─────────────────────────────────────────────────────────────────────────
 * Handle + drive helpers
 * ───────────────────────────────────────────────────────────────────────── */

/* Plan 118-05 (D-08): extra_flags defaults to 0, so every one of cases 1-8's
 * existing make_sdp_handle(row) call sites is byte-for-byte unaffected --
 * no signature churn at those eight sites. Cases 9 and 10 pass
 * FLAG_SKIP_SDP_UNLOCK or 0 respectively, from this SAME factory and the
 * SAME row, so the only difference between the two cases is the flag bit
 * (mirrors make_identity_handle's existing ctrl_flags-parameter shape at
 * lines 163-178 below). FLAG_SKIP_BLANK_CHECK stays unconditionally set in
 * both, exactly as every other case here, so the blank-check axis
 * contributes no strobes to either stream. */
static firestarter_handle_t make_sdp_handle(const sdp_bus_config_row_t& row, uint32_t extra_flags = 0) {
    firestarter_handle_t h = {};
    h.protocol = 0x0D;
    h.cmd = CMD_WRITE;
    h.response_code = RESPONSE_CODE_OK;
    h.chip_id = 0; /* skip chip-id branch for cases 1-5 */
    h.mem_size = row.mem_size;
    h.bus_config = row.bus_config;
    h.ctrl_flags = FLAG_SKIP_BLANK_CHECK | extra_flags;
    return h;
}

static firestarter_handle_t make_identity_handle(uint16_t expected_chip_id, uint32_t ctrl_flags) {
    firestarter_handle_t h = {};
    h.protocol = 0x0D;
    h.cmd = CMD_WRITE;
    h.mem_size = 32768; /* AT28C256 -- mfr_addr = mem_size - 64 = 0x7FC0 */
    h.response_code = RESPONSE_CODE_OK;
    h.chip_id = expected_chip_id;
    /* D-01 (Phase 117): dropping the set_data no-op routes cases 6-7 through
     * the real memory_set_data / mem_util_remap_address_bus for the first
     * time, so this factory now needs a real bus_config -- row 0 is
     * AT28C256 / DIP28_28C256, whose mem_size 32768 already matches this
     * factory's own h.mem_size above (and its derived mfr_addr 0x7FC0). */
    h.bus_config = SDP_BUS_CONFIGS[0].bus_config;
    h.ctrl_flags = ctrl_flags | FLAG_SKIP_BLANK_CHECK;
    return h;
}

/* Pattern 3: dispatch on ADDRESS, not call order. Virgin 0xFF everywhere
 * except the two planted manufacturer/device identity bytes; the SDP
 * completion-poll address (0x5555) is deliberately never satisfied. Migrated
 * from test_sdp_harness.cpp (116-05).
 *
 * D-01 (Phase 117 commit 1): only get_data is mocked here. The suite no
 * longer reassigns firestarter_set_data -- FIX-01 builds the emitter on
 * exactly that pointer, so a no-op there would make the post-fix recorded
 * stream empty. get_data stays mocked because it is what collapses the
 * completion poll's 2000-iteration loop to zero strobes, which is the sole
 * reason full-stream equality is possible at all. */
static uint8_t mock_get_data_keyed(firestarter_handle_t*, uint32_t addr) {
    if (addr == s_mfr_addr_keyed) {
        s_reads_at_mfr_addr++;
        return s_mfr_hi_keyed;
    }
    if (addr == s_mfr_addr_keyed + 1) {
        s_reads_at_mfr_addr++;
        return s_mfr_lo_keyed;
    }
    if (addr == 0x5555) {
        s_reads_at_poll_addr++;
        /* D-02 (Phase 117 commit 1, Case 8): post-fix the completion poll is
         * a bounded DQ6 toggle-bit poll, not an equality compare against a
         * value that is never written. A constant return means "settled
         * immediately"; s_poll_addr_toggles flips bit 0x40 on every read at
         * THIS address so it means "never settles" -- dispatch stays keyed
         * on ADDRESS, never on call order, per the rule above. The fixed
         * code draws NO conclusion from either outcome (D-05): the
         * conclusion is deferred to the page write's own poll, which has a
         * real written byte to compare against (FIX-06). */
        if (s_poll_addr_toggles) {
            return (s_reads_at_poll_addr % 2 == 0) ? (uint8_t)0x00 : (uint8_t)0x40;
        }
        return 0xFF; /* virgin default -- never satisfies the 0x20 SDP-disable poll */
    }
    return 0xFF;
}

/* The FIX-01 reference emitter: h->firestarter_set_data is memory_set_data
 * (assigned by configure_memory), which routes through
 * mem_util_remap_address_bus -- the remap-aware target stream, with zero
 * hand derivation. Identical shape to test_sdp_harness.cpp's helper of the
 * same name (separate TU, no shared linkage). */
static void drive_reference_emitter(firestarter_handle_t* h, const byte_flip_t* table, size_t len, rurp_register_t ctrl_seed) {
    configure_memory(h);
    reset_register_cache(0x00, 0x00, ctrl_seed);
    clear_strobes();
    for (size_t i = 0; i < len; i++) {
        h->firestarter_set_data(h, table[i].address, table[i].byte);
    }
}

/* Drives the REAL eeprom28c_write_init (via configure_memory dispatch) after
 * reassigning firestarter_get_data to the address-keyed mock, so the
 * 2000-iteration completion-poll timeout contributes zero strobes to the
 * recorded stream (Task 1 / Open Question 2 resolution: full-stream equality
 * is possible only because the mock satisfies no bus traffic). D-01 (Phase
 * 117): unlike Phase 116, firestarter_set_data is left as configure_memory's
 * real memory_set_data -- FIX-01 routes the emitter through that exact
 * pointer, so a no-op there would make the recorded stream empty post-fix. */
static void drive_write_init(firestarter_handle_t* h, rurp_register_t ctrl_seed) {
    configure_memory(h);
    h->firestarter_get_data = mock_get_data_keyed;
    reset_register_cache(0x00, 0x00, ctrl_seed);
    clear_strobes();
    h->firestarter_operation_init(h);
}

/* Case 5's mechanism (RESEARCH Open Question 1, second leg): reaches the
 * stale-upper-address state via an ACTUAL preceding memory_get_data() read
 * rather than a directly-seeded cache, so a reviewer cannot object that a
 * hand-seeded cache is unrepresentative. DIP32_28C512_EEPROM's rw_line (20)
 * folds READ_FLAG=1 into CONTROL bit 0x10 (CTRL_ADDRESS_LINE_17) on every
 * real read through the production get_data path — one read is sufficient.
 * Returns the CONTROL value actually left behind, so the caller can drive an
 * identically-seeded reference emitter for comparison. */
static rurp_register_t drive_write_init_after_real_read(firestarter_handle_t* h, uint32_t probe_addr) {
    configure_memory(h);
    reset_register_cache(0x00, 0x00, 0x00);
    h->firestarter_get_data(h, probe_addr); /* REAL preceding read -- production memory_get_data */
    rurp_register_t stale_ctrl = rurp_read_from_register(CONTROL_REGISTER);
    h->firestarter_get_data = mock_get_data_keyed;
    /* D-01 (Phase 117): firestarter_set_data stays the real memory_set_data
     * (see drive_write_init's comment above) -- FIX-01's emitter is built on
     * it. */
    clear_strobes();
    h->firestarter_operation_init(h);
    return stale_ctrl;
}

/* ─────────────────────────────────────────────────────────────────────────
 * Cases 1-3 — ordered capture per DIP28/DIP24 pinout (TRACE-02, D-06)
 * ───────────────────────────────────────────────────────────────────────── */

/* RED today, named mechanical reason: eeprom28c_write_init's SDP-disable
 * sequence is emitted by flash_execute_command -> flash_util_byte_flipping ->
 * fu_flash_fast_address, which writes the LITERAL {0x5555, 0x2AAA} magic
 * addresses via raw LSB/MSB register writes and NEVER consults
 * handle->bus_config. On AT28C256/DIP28_28C256, remap(0x5555) == 0x9555 (MSB
 * 0x95, not 0x55) -- the shipped stream's address bytes are simply wrong for
 * this pinout's real bus wiring, so the ordered-stream comparison against the
 * FIX-01 target (SDP_FIXED_DIP28_28C256, built on the remap-aware
 * memory_set_data) diverges from the very first MSB write. */
void test_case1_at28c256_stream_matches_fixed(void) {
    firestarter_handle_t h = make_sdp_handle(SDP_BUS_CONFIGS[0]); /* AT28C256 */
    drive_write_init(&h, 0x00);
    sdp_assert_stream_equals(SDP_FIXED_DIP28_28C256, SDP_FIXED_DIP28_28C256_LEN,
        "Case 1: AT28C256/DIP28_28C256 -- eeprom28c_write_init's raw-address shipped "
        "stream must match the FIX-01 remap-aware target");
    TEST_ASSERT_NOT_EQUAL_MESSAGE(RESPONSE_CODE_ERROR, h.response_code,
        "Case 1: the completion poll is advisory only (D-05) and must never report ERROR "
        "for a write-init that emitted the correct sequence");
}

/* RED today, same mechanism as Case 1: on AT28C64/DIP28_28C64, remap(0x5555)
 * == 0x1555 (MSB 0x15, not 0x55) and remap(0x2AAA) == 0x0AAA (MSB 0x0A, not
 * 0x2A) -- again wrong for this pinout's real 13-address-line wiring. */
void test_case2_at28c64_stream_matches_fixed(void) {
    firestarter_handle_t h = make_sdp_handle(SDP_BUS_CONFIGS[1]); /* AT28C64 */
    drive_write_init(&h, 0x00);
    sdp_assert_stream_equals(SDP_FIXED_DIP28_28C64, SDP_FIXED_DIP28_28C64_LEN,
        "Case 2: AT28C64/DIP28_28C64 -- eeprom28c_write_init's raw-address shipped "
        "stream must match the FIX-01 remap-aware target");
    TEST_ASSERT_NOT_EQUAL_MESSAGE(RESPONSE_CODE_ERROR, h.response_code,
        "Case 2: the completion poll is advisory only (D-05) and must never report ERROR "
        "for a write-init that emitted the correct sequence");
}

/* RED today, same mechanism as Case 1: on AT28C16/DIP24_2816 (11 address
 * lines), remap(0x5555) == 0x0555 (MSB 0x05) and remap(0x2AAA) == 0x02AA
 * (MSB 0x02). */
void test_case3_at28c16_stream_matches_fixed(void) {
    firestarter_handle_t h = make_sdp_handle(SDP_BUS_CONFIGS[2]); /* AT28C16 */
    drive_write_init(&h, 0x00);
    sdp_assert_stream_equals(SDP_FIXED_DIP24_2816, SDP_FIXED_DIP24_2816_LEN,
        "Case 3: AT28C16/DIP24_2816 -- eeprom28c_write_init's raw-address shipped "
        "stream must match the FIX-01 remap-aware target");
    TEST_ASSERT_NOT_EQUAL_MESSAGE(RESPONSE_CODE_ERROR, h.response_code,
        "Case 3: the completion poll is advisory only (D-05) and must never report ERROR "
        "for a write-init that emitted the correct sequence");
}

/* ─────────────────────────────────────────────────────────────────────────
 * Cases 4-5 — DIP32_28C512_EEPROM, deliberate stale-upper-address state
 * (CORRECTION 3, TRACE-02, D-09)
 * ───────────────────────────────────────────────────────────────────────── */

/*
 * CORRECTION 3 (116-RESEARCH.md CORRECTION 3 / 116-05-SUMMARY.md): a PLAIN
 * DIP32 trace against the canonical zero-CONTROL-seed SDP_FIXED_DIP32_*
 * target is decorative here. mem_util_remap_address_bus returns 0x5555
 * unchanged for this pinout (address_mask == 0xFFFF, rw_line-20's bit is
 * WRITE_FLAG == 0 on a write) -- shipped and fixed share byte-identical
 * LSB/MSB/data values under a zero seed, differing only by an INCIDENTAL
 * /OE-edge ordering artifact of which emitter function happens to be used. A
 * future fix that preserved that ordering would leave a plain trace GREEN
 * with nothing about the real bug proven.
 *
 * The REAL bug: DIP32's rw_line (20) folds into CONTROL bit 0x10
 * (CTRL_ADDRESS_LINE_17) -- the WRITE-ENABLE line this 32-pin pinout
 * repurposes an upper address line for. fu_flash_fast_address (the SHIPPED
 * emitter) writes ONLY LSB/MSB and NEVER writes CONTROL_REGISTER at all -- so
 * whatever a PRECEDING operation left in CONTROL's upper-address bits stays
 * stuck for the entire SDP sequence: /WE inhibited, and (for
 * CTRL_ADDRESS_LINE_18) the chip's real upper address wrong. The reference
 * emitter (memory_set_data, the FIX-01 target) recomputes and writes
 * CONTROL_REGISTER on every address change via mem_util_set_address, and
 * WOULD clear those stale bits.
 *
 * Non-decorative comparison target: instead of the canonical zero-seed
 * SDP_FIXED_DIP32_28C512_EEPROM array, both cases below dynamically drive the
 * reference emitter under the SAME stale seed as the shipped path, snapshot
 * it, and assert the shipped stream equals THAT snapshot. This is the
 * "large, unambiguous divergence" CORRECTION 3 calls for: shipped emits no
 * CONTROL_REGISTER entries under any seed (cache-hit branch is a no-op either
 * way), while the stale-seeded reference emitter emits an EXTRA
 * CONTROL_REGISTER write clearing the stale bits -- a difference in KIND, not
 * merely incidental ordering. It is also self-repairing: once Phase 117
 * rebuilds eeprom28c_write_init on the same remap-aware, CONTROL-writing
 * emitter, driving the "shipped" handle will produce byte-identical output to
 * driving the reference handle, and this assertion passes with no further
 * edit.
 */

/* Case 4 (STALE STATE MECHANISM: direct seed). AT28C010 (128 KB). */
void test_case4_at28c010_stale_direct_seed(void) {
    firestarter_handle_t h = make_sdp_handle(SDP_BUS_CONFIGS[3]); /* AT28C010 */
    drive_write_init(&h, CTRL_ADDRESS_LINE_17 | CTRL_ADDRESS_LINE_18);

    sdp_strobe_t shipped_snapshot[64];
    int shipped_len = sdp_snapshot(shipped_snapshot, 64);
    TEST_ASSERT_EQUAL_MESSAGE(0, strobe_overflowed(), "Case 4: shipped-path snapshot must not overflow");

    firestarter_handle_t h_ref = make_sdp_handle(SDP_BUS_CONFIGS[3]);
    drive_reference_emitter(&h_ref, FLASH_DISABLE_WRITE_PROTECTION, 6, CTRL_ADDRESS_LINE_17 | CTRL_ADDRESS_LINE_18);
    TEST_ASSERT_EQUAL_MESSAGE(0, strobe_overflowed(), "Case 4: fixed-reference drive must not overflow");
    TEST_ASSERT_GREATER_THAN_MESSAGE(SDP_FIXED_DIP32_28C512_EEPROM_LEN, strobe_count(),
        "Case 4: stale-seeded reference emitter must emit an extra CONTROL_REGISTER write "
        "clearing CTRL_ADDRESS_LINE_17|18 versus the zero-seed target -- if this ever drops "
        "to the zero-seed length, the stale seed stopped taking effect");

    sdp_assert_stream_equals(shipped_snapshot, shipped_len,
        "Case 4: AT28C010/DIP32_28C512_EEPROM, directly-seeded stale CTRL_ADDRESS_LINE_17|18 -- "
        "shipped path (no CONTROL_REGISTER write, ever) must clear the stale write-inhibit bits "
        "like the fixed reference emitter (memory_set_data) does");

    TEST_ASSERT_NOT_EQUAL_MESSAGE(RESPONSE_CODE_ERROR, h.response_code,
        "Case 4: the completion poll is advisory only (D-05) and must never report ERROR "
        "for a write-init that cleared the stale write-inhibit bits and emitted the correct "
        "sequence");
}

/* Case 5 (STALE STATE MECHANISM: a real preceding read through
 * memory_get_data, per RESEARCH Open Question 1's second leg). AT28C040
 * (512 KB) -- shares AT28C010's bus_config byte-for-byte (116-02 D-09). */
void test_case5_at28c040_stale_via_real_read(void) {
    /* Probe address 0x0000, deliberately NOT 0x5555/0x2AAA (the SDP
     * sequence's own magic addresses): CTRL_ADDRESS_LINE_17 is set by
     * rw_line's READ_FLAG bit alone, independent of which address is read, so
     * any address demonstrates the mechanism. Reusing 0x5555 would also
     * pre-warm the LSB/MSB latch cache to the SAME value write #1 of the SDP
     * sequence needs, eliding that write's address latch too (a real,
     * correct, but SEPARATE cache-elision effect) and conflating it with the
     * CONTROL-bit finding this case exists to isolate. */
    firestarter_handle_t h = make_sdp_handle(SDP_BUS_CONFIGS[4]); /* AT28C040 */
    rurp_register_t stale_ctrl = drive_write_init_after_real_read(&h, 0x0000);
    TEST_ASSERT_BITS_HIGH_MESSAGE((uint8_t)CTRL_ADDRESS_LINE_17, stale_ctrl,
        "Case 5: a real preceding read (at an arbitrary address, 0x0000) must leave "
        "CTRL_ADDRESS_LINE_17 stuck HIGH on DIP32_28C512_EEPROM -- rw_line 20 folds "
        "READ_FLAG into this CONTROL bit regardless of which address is read");

    sdp_strobe_t shipped_snapshot[64];
    int shipped_len = sdp_snapshot(shipped_snapshot, 64);
    TEST_ASSERT_EQUAL_MESSAGE(0, strobe_overflowed(), "Case 5: shipped-path snapshot must not overflow");

    firestarter_handle_t h_ref = make_sdp_handle(SDP_BUS_CONFIGS[4]);
    drive_reference_emitter(&h_ref, FLASH_DISABLE_WRITE_PROTECTION, 6, stale_ctrl);
    TEST_ASSERT_EQUAL_MESSAGE(0, strobe_overflowed(), "Case 5: fixed-reference drive must not overflow");
    TEST_ASSERT_GREATER_THAN_MESSAGE(SDP_FIXED_DIP32_28C512_EEPROM_LEN, strobe_count(),
        "Case 5: stale-seeded reference emitter must emit an extra CONTROL_REGISTER write "
        "clearing CTRL_ADDRESS_LINE_17 versus the zero-seed target");

    sdp_assert_stream_equals(shipped_snapshot, shipped_len,
        "Case 5: AT28C040/DIP32_28C512_EEPROM, stale CTRL_ADDRESS_LINE_17 reached via a REAL "
        "preceding read (memory_get_data, not a directly-seeded cache) -- shipped path must clear "
        "the write-inhibit bit like the fixed reference emitter does");

    TEST_ASSERT_NOT_EQUAL_MESSAGE(RESPONSE_CODE_ERROR, h.response_code,
        "Case 5: the completion poll is advisory only (D-05) and must never report ERROR "
        "for a write-init that cleared the stale write-inhibit bit and emitted the correct "
        "sequence");
}

/* ─────────────────────────────────────────────────────────────────────────
 * Cases 6-7 — migrated identity-gate assertions, RED half (CORRECTION 2,
 * TRACE-04, TRACE-06)
 * ───────────────────────────────────────────────────────────────────────── */

/* Migrated from the retired test_eeprom28c_chip_id (D-12), landing HERE (not
 * the always-green test_sdp_harness) per CORRECTION 2: this case is
 * SDP-outcome-dependent, so it is RED today and only goes GREEN once Phase
 * 117 fixes eeprom28c_write_init's SDP-disable completion check.
 *
 * RED today, named mechanical reason: a matching identity never sets an
 * error or warning, so eeprom28c_write_init proceeds into
 * flash_execute_command(EEPROM_SDP_DISABLE); eeprom28c_wait_for_write's
 * completion poll (0x5555 == 0x20) never succeeds against the address-keyed
 * mock's virgin 0xFF, times out after 2000 iterations, and unconditionally
 * sets RESPONSE_CODE_ERROR (eeprom_28c.cpp:151-153) -- so
 * NOT_EQUAL(RESPONSE_CODE_ERROR) fails today. */
void test_case6_matching_chip_id_proceeds(void) {
    s_mfr_addr_keyed = 32768 - 64; /* 0x7FC0 */
    s_mfr_hi_keyed = 0x1F;
    s_mfr_lo_keyed = 0x08;
    firestarter_handle_t h = make_identity_handle(0x1F08, 0);
    configure_memory(&h);
    /* configure_memory() overwrites firestarter_get_data (Pattern 3) --
     * re-assign it. D-01 (Phase 117): firestarter_set_data is left as
     * configure_memory's real memory_set_data -- FIX-01's emitter is built
     * on that exact pointer, so a no-op here would make the post-fix
     * recorded stream empty. */
    h.firestarter_get_data = mock_get_data_keyed;
    reset_register_cache(0x00, 0x00, 0x00);
    clear_strobes();
    h.firestarter_operation_init(&h);
    TEST_ASSERT_NOT_EQUAL_MESSAGE(RESPONSE_CODE_ERROR, h.response_code,
        "migrated (RED, CORRECTION 2): matching identity must proceed past SDP-disable, not "
        "time out and overwrite response_code with ERROR");
}

/* CORRECTION 2's finding, second-order evidence of the inverted completion
 * check -- the check does not merely fail, it DESTROYS severity information.
 * With FLAG_FORCE, eeprom28c_check_chip_id correctly sets
 * RESPONSE_CODE_WARNING on a chip-id mismatch (eeprom_28c.cpp:88), but
 * eeprom28c_write_init's completion wait is UNCONDITIONAL (no flag skips it):
 * eeprom28c_wait_for_write's timeout unconditionally overwrites
 * handle->response_code with RESPONSE_CODE_ERROR, destroying the WARNING.
 * D-12 originally routed this case to the always-green suite; CORRECTION 2
 * moves it here. Do NOT weaken this assertion to make it pass today -- the
 * force/severity fork is exactly what the v1.16 Phase-89 CR-01 regression
 * slipped through (see .planning memory
 * reference_golden_trace_misses_severity_fork.md). */
void test_case7_mismatching_chip_id_with_force_warns(void) {
    s_mfr_addr_keyed = 32768 - 64;
    s_mfr_hi_keyed = 0xDE;
    s_mfr_lo_keyed = 0xAD;
    firestarter_handle_t h = make_identity_handle(0x1F08, FLAG_FORCE);
    configure_memory(&h);
    /* D-01 (Phase 117): see test_case6's comment above -- firestarter_set_data
     * is left as the real memory_set_data. */
    h.firestarter_get_data = mock_get_data_keyed;
    reset_register_cache(0x00, 0x00, 0x00);
    clear_strobes();
    h.firestarter_operation_init(&h);
    TEST_ASSERT_EQUAL_MESSAGE(RESPONSE_CODE_WARNING, h.response_code,
        "migrated (RED, CORRECTION 2): mismatching identity + FLAG_FORCE must WARN, not have its "
        "severity destroyed by the unconditional SDP-disable completion wait");
}

/* ─────────────────────────────────────────────────────────────────────────
 * Case 8 — completion poll must never destroy a prior severity (D-02, D-05)
 * ───────────────────────────────────────────────────────────────────────── */

/* New at Phase 117 commit 1, a PERMANENT regression guard (not migrated,
 * not RED-only-by-construction). chip_id is 0 in make_sdp_handle, so no
 * identity path runs and the WARNING's provenance is unambiguous -- it can
 * only have been altered by the completion poll itself. s_poll_addr_toggles
 * makes the poll never conclude, so this also exercises the "never settles"
 * arm of the mock (the constant-return arm is already exercised by cases
 * 1-7). RED at this commit for a named reason: today's shipped
 * eeprom28c_write_init times out on its (0x5555, 0x20) read-back and
 * unconditionally overwrites handle->response_code with
 * RESPONSE_CODE_ERROR (eeprom_28c.cpp:153), destroying the WARNING -- the
 * same severity-destruction fork the v1.16 Phase-89 CR-01 regression
 * slipped through (.planning memory
 * reference_golden_trace_misses_severity_fork.md). */
void test_case8_completion_poll_preserves_prior_severity(void) {
    firestarter_handle_t h = make_sdp_handle(SDP_BUS_CONFIGS[0]); /* AT28C256 */
    h.response_code = RESPONSE_CODE_WARNING;
    s_poll_addr_toggles = true; /* the completion poll can never conclude */
    drive_write_init(&h, 0x00);
    TEST_ASSERT_EQUAL_MESSAGE(RESPONSE_CODE_WARNING, h.response_code,
        "Case 8: the completion poll is advisory only (D-05) and must never overwrite "
        "a prior response_code, even when it never settles");
}

/* ─────────────────────────────────────────────────────────────────────────
 * Cases 9-10 — the skip/no-skip stream pair, content-positional, from ONE
 * handle factory (D-08, Plan 118-05 Task 1, OBS-02)
 * ───────────────────────────────────────────────────────────────────────── */

/* D-08 constraint 1: drives PRODUCTION eeprom28c_write_init via
 * drive_write_init (configure_memory dispatch), never
 * drive_reference_emitter (which drives FLASH_DISABLE_WRITE_PROTECTION, a
 * DIFFERENT table -- proving nothing about the shipped FLAG_SKIP_SDP_UNLOCK
 * gate).
 *
 * D-08 constraint 2: every assertion below is on the ordered stream's
 * CONTENT, never a call count. Register-write elision (Phase 116 research
 * finding 10) is invisible to a counting test -- a bare
 * strobe_count() == 0 would pass even if the emitter ran and every write
 * happened to elide, so that check appears ONLY as secondary corroboration
 * at the end, never as the load-bearing proof. */
void test_case9_skip_flag_suppresses_unlock_stream(void) {
    firestarter_handle_t h = make_sdp_handle(SDP_BUS_CONFIGS[0], FLAG_SKIP_SDP_UNLOCK); /* AT28C256 */
    drive_write_init(&h, 0x00);

    TEST_ASSERT_EQUAL_MESSAGE(0, strobe_overflowed(),
        "Case 9 (OBS-02): recorded stream must not overflow");

    /* Content-positional divergence (D-08 constraint 2): the recorded stream
     * must diverge from the full unlock stream at EXACTLY index 0 -- the
     * unlock sequence's own first strobe is absent from the very start, not
     * merely "somewhere". Asserting the exact index, rather than != -1, is
     * itself an assertion about content and position, never a count. */
    TEST_ASSERT_EQUAL_MESSAGE(0, sdp_first_divergence(SDP_FIXED_DIP28_28C256, SDP_FIXED_DIP28_28C256_LEN),
        "Case 9 (OBS-02): FLAG_SKIP_SDP_UNLOCK set -- the recorded stream must diverge from the "
        "full unlock stream (SDP_FIXED_DIP28_28C256) starting at index 0");

    /* Content walk over every recorded DATA entry: none of EEPROM_SDP_DISABLE's
     * own payload bytes -- the PRODUCTION command sequence's own command
     * table, not a transcribed copy -- may appear as a DATA value anywhere in
     * the recorded stream. This is the assertion that survives register-write
     * elision (D-08 constraint 2): it inspects every recorded element's
     * {kind, value}, never a length or a count. */
    for (int i = 0; i < strobe_count(); i++) {
        if (strobe_kind(i) != STROBE_KIND_DATA) {
            continue;
        }
        for (size_t j = 0; j < sizeof(EEPROM_SDP_DISABLE) / sizeof(EEPROM_SDP_DISABLE[0]); j++) {
            char msg[224];
            snprintf(msg, sizeof(msg),
                "Case 9 (OBS-02): recorded DATA entry at index %d (value 0x%02X) matches "
                "EEPROM_SDP_DISABLE[%u]'s payload byte 0x%02X -- the unlock sequence must be "
                "TOTALLY ABSENT from the stream when FLAG_SKIP_SDP_UNLOCK is set",
                i, (unsigned)strobe_value(i), (unsigned)j, (unsigned)EEPROM_SDP_DISABLE[j].byte);
            TEST_ASSERT_NOT_EQUAL_MESSAGE(EEPROM_SDP_DISABLE[j].byte, strobe_value(i), msg);
        }
    }

    /* Secondary corroboration ONLY (D-08 explicitly forbids a bare
     * strobe_count() from being the load-bearing proof) -- the two content
     * assertions above are what this case actually rests on. With the whole
     * unlock block skipped and FLAG_SKIP_BLANK_CHECK also set,
     * eeprom28c_write_init emits nothing else, so the count happens to be 0. */
    TEST_ASSERT_EQUAL_MESSAGE(0, strobe_count(),
        "Case 9 (OBS-02, secondary corroboration ONLY -- see the index-0 divergence and the "
        "payload-byte-absence walk above for the load-bearing proof)");
}

/* D-08 constraint 3: the flag-absent counterpart, from the SAME handle
 * factory and the SAME row as Case 9 above, asserting the FULL
 * SDP_FIXED_DIP28_28C256 stream, ships in the SAME commit as Case 9. Case 1
 * already makes a similar full-stream assertion, but from the OLD
 * (pre-118-05) factory shape that always passed extra_flags == 0 implicitly
 * -- this counterpart exists so the skip/no-skip pair is self-contained at
 * one call site each, and so a future edit to make_sdp_handle's default
 * ctrl_flags cannot silently drift the flag-absent baseline Case 9 is
 * contrasted against. Cross-reference: Case 9 immediately above. */
void test_case10_flag_absent_emits_full_unlock_stream(void) {
    firestarter_handle_t h = make_sdp_handle(SDP_BUS_CONFIGS[0], 0); /* AT28C256, flag NOT set */
    drive_write_init(&h, 0x00);
    sdp_assert_stream_equals(SDP_FIXED_DIP28_28C256, SDP_FIXED_DIP28_28C256_LEN,
        "Case 10 (OBS-02, D-08 constraint 3): FLAG_SKIP_SDP_UNLOCK absent -- eeprom28c_write_init's "
        "stream must match the full FIX-01 remap-aware target, from the SAME handle factory Case 9 "
        "used, differing only by the flag bit");
    TEST_ASSERT_NOT_EQUAL_MESSAGE(RESPONSE_CODE_ERROR, h.response_code,
        "Case 10: the completion poll is advisory only (D-05) and must never report ERROR for a "
        "write-init that emitted the correct sequence");
}

/* ─────────────────────────────────────────────────────────────────────────
 * Case 11 — the t_BLC runtime budget WARN is observed to actually fire
 * (D-09, Plan 118-05 Task 2, OBS-03)
 * ───────────────────────────────────────────────────────────────────────── */

void test_case11_tblc_budget_exceeded_warns(void) {
    /* AT28C_TBLC_MAX_US (100) is #define'd inside eeprom_28c.cpp's own
     * translation unit (eeprom_28c.cpp:58) and is NOT exported via
     * eeprom_28c.h, so it cannot be included directly here. Mirrored as a
     * named local constant with an explicit citation, rather than left as
     * an unexplained magic number -- the sequence-length half of the
     * production budget formula (sdp_seq_len * AT28C_TBLC_MAX_US) IS derived
     * from the real EEPROM_SDP_DISABLE array below, so only the per-byte
     * microsecond ceiling itself needs mirroring. */
    const uint32_t TEST_MIRROR_AT28C_TBLC_MAX_US = 100; /* mirrors eeprom_28c.cpp:58 */
    uint32_t sdp_seq_len = (uint32_t)(sizeof(EEPROM_SDP_DISABLE) / sizeof(EEPROM_SDP_DISABLE[0]));
    uint32_t over_budget_elapsed = sdp_seq_len * TEST_MIRROR_AT28C_TBLC_MAX_US + 1;

    s_micros_ticks[0] = 0;
    s_micros_ticks[1] = over_budget_elapsed;
    firestarter_handle_t h = make_sdp_handle(SDP_BUS_CONFIGS[0]); /* flag absent -- unlock runs */
    drive_write_init(&h, 0x00);

    std::vector<uint8_t> ids;
    sdp_captured_frame_ids(&ids);

    int done_idx = -1, warn_idx = -1;
    for (size_t i = 0; i < ids.size(); i++) {
        if (ids[i] == (uint8_t)MSG_INFO_SDP_UNLOCK_DONE_US) {
            done_idx = (int)i;
        }
        if (ids[i] == (uint8_t)MSG_WARN_SDP_TBLC_EXCEEDED) {
            warn_idx = (int)i;
        }
    }
    TEST_ASSERT_TRUE_MESSAGE(warn_idx != -1,
        "Case 11 (OBS-03, D-09): an over-budget elapsed value must make MSG_WARN_SDP_TBLC_EXCEEDED "
        "appear in the captured serial frames -- a runtime check never observed to fire is "
        "indistinguishable from a dead branch");
    TEST_ASSERT_TRUE_MESSAGE(done_idx != -1 && warn_idx > done_idx,
        "Case 11 (OBS-03): MSG_WARN_SDP_TBLC_EXCEEDED must appear AFTER MSG_INFO_SDP_UNLOCK_DONE_US "
        "in the captured frame order -- the budget check runs after the after-line");
    TEST_ASSERT_EQUAL_MESSAGE(RESPONSE_CODE_OK, h.response_code,
        "Case 11 (D-02/D-05): the budget WARN must never write handle->response_code -- severity "
        "lives in the message id's band alone");

    /* Anti-hollow control, same case (D-09's own requirement): with the
     * default tick behaviour (elapsed 0) restored, the WARN id must NOT
     * appear -- an appearing-only assertion could pass against a branch that
     * always fires regardless of the measured duration. */
    s_micros_ticks[0] = 0;
    s_micros_ticks[1] = 0;
    s_micros_call_count = 0;
    captured_frames.clear();
    firestarter_handle_t h2 = make_sdp_handle(SDP_BUS_CONFIGS[0]);
    drive_write_init(&h2, 0x00);
    std::vector<uint8_t> ids_default;
    sdp_captured_frame_ids(&ids_default);
    TEST_ASSERT_FALSE_MESSAGE(sdp_ids_contains(ids_default, (uint8_t)MSG_WARN_SDP_TBLC_EXCEEDED),
        "Case 11 (anti-hollow control): with the default elapsed value (0), MSG_WARN_SDP_TBLC_EXCEEDED "
        "must NOT appear -- proves the check is conditional on the measured duration, not a branch "
        "that always fires");
}

/* ─────────────────────────────────────────────────────────────────────────
 * Case 12 — exactly the two new report frames (flag absent) / exactly one
 * WARN frame (flag set), enumerated (D-07 strengthening, OBS-05)
 * ───────────────────────────────────────────────────────────────────────── */

/* Strengthens, but never replaces, D-07's PRIMARY assertion: the recorded
 * BUS stream's byte-identity (Cases 1-3/10 above, and the _shared/ blob-SHA
 * record in RED-BASELINE.md, Plan 118-05 Task 3). This case only makes
 * OBS-05's serial-channel exception machine-checked instead of prose-only,
 * using the per-case capture declared above -- it does not build the
 * general-purpose recorder D-07 explicitly declined. */
void test_case12_flag_absent_emits_exactly_two_report_frames(void) {
    firestarter_handle_t h = make_sdp_handle(SDP_BUS_CONFIGS[0]); /* flag absent, default ticks */
    drive_write_init(&h, 0x00);

    std::vector<uint8_t> ids;
    sdp_captured_frame_ids(&ids);
    TEST_ASSERT_EQUAL_MESSAGE(2, (int)ids.size(),
        "Case 12 (OBS-05): the flag-absent default path must emit EXACTLY two report frames");
    TEST_ASSERT_EQUAL_HEX8_MESSAGE((uint8_t)MSG_INFO_SDP_UNLOCK, ids.size() > 0 ? ids[0] : (uint8_t)0xFF,
        "Case 12: frame 0 must be MSG_INFO_SDP_UNLOCK");
    TEST_ASSERT_EQUAL_HEX8_MESSAGE((uint8_t)MSG_INFO_SDP_UNLOCK_DONE_US, ids.size() > 1 ? ids[1] : (uint8_t)0xFF,
        "Case 12: frame 1 must be MSG_INFO_SDP_UNLOCK_DONE_US");
    TEST_ASSERT_FALSE_MESSAGE(sdp_ids_contains(ids, (uint8_t)MSG_WARN_SDP_UNLOCK_SKIPPED),
        "Case 12: the flag-absent path must never emit MSG_WARN_SDP_UNLOCK_SKIPPED");
    TEST_ASSERT_FALSE_MESSAGE(sdp_ids_contains(ids, (uint8_t)MSG_WARN_SDP_TBLC_EXCEEDED),
        "Case 12: the flag-absent default (elapsed 0) path must never emit MSG_WARN_SDP_TBLC_EXCEEDED");

    /* Skip-path mirror, same case -- the executable form of D-02's "in place
     * of, never in addition to": with FLAG_SKIP_SDP_UNLOCK set, EXACTLY
     * MSG_WARN_SDP_UNLOCK_SKIPPED and neither INFO id. */
    captured_frames.clear();
    firestarter_handle_t h_skip = make_sdp_handle(SDP_BUS_CONFIGS[0], FLAG_SKIP_SDP_UNLOCK);
    drive_write_init(&h_skip, 0x00);
    std::vector<uint8_t> ids_skip;
    sdp_captured_frame_ids(&ids_skip);
    TEST_ASSERT_EQUAL_MESSAGE(1, (int)ids_skip.size(),
        "Case 12 (skip mirror, D-02): the skip path must emit EXACTLY one frame");
    TEST_ASSERT_EQUAL_HEX8_MESSAGE((uint8_t)MSG_WARN_SDP_UNLOCK_SKIPPED, ids_skip.size() > 0 ? ids_skip[0] : (uint8_t)0xFF,
        "Case 12 (skip mirror): the one frame must be MSG_WARN_SDP_UNLOCK_SKIPPED");
    TEST_ASSERT_FALSE_MESSAGE(sdp_ids_contains(ids_skip, (uint8_t)MSG_INFO_SDP_UNLOCK),
        "Case 12 (skip mirror): the skip path must never emit MSG_INFO_SDP_UNLOCK");
    TEST_ASSERT_FALSE_MESSAGE(sdp_ids_contains(ids_skip, (uint8_t)MSG_INFO_SDP_UNLOCK_DONE_US),
        "Case 12 (skip mirror): the skip path must never emit MSG_INFO_SDP_UNLOCK_DONE_US");
}

/* ─────────────────────────────────────────────────────────────────────────
 * main
 * ───────────────────────────────────────────────────────────────────────── */

int main(int argc, char** argv) {
    (void)argc; (void)argv;
    UNITY_BEGIN();

    RUN_TEST(test_case1_at28c256_stream_matches_fixed);
    RUN_TEST(test_case2_at28c64_stream_matches_fixed);
    RUN_TEST(test_case3_at28c16_stream_matches_fixed);
    RUN_TEST(test_case4_at28c010_stale_direct_seed);
    RUN_TEST(test_case5_at28c040_stale_via_real_read);
    RUN_TEST(test_case6_matching_chip_id_proceeds);
    RUN_TEST(test_case7_mismatching_chip_id_with_force_warns);
    RUN_TEST(test_case8_completion_poll_preserves_prior_severity);
    RUN_TEST(test_case9_skip_flag_suppresses_unlock_stream);
    RUN_TEST(test_case10_flag_absent_emits_full_unlock_stream);
    RUN_TEST(test_case11_tblc_budget_exceeded_warns);
    RUN_TEST(test_case12_flag_absent_emits_exactly_two_report_frames);

    return UNITY_END();
}
