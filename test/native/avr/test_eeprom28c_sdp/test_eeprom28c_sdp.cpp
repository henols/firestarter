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

void setUp(void) {
    ArduinoFakeReset();
    When(OverloadedMethod(ArduinoFake(Serial), write, size_t(uint8_t))).AlwaysReturn(1);
    When(OverloadedMethod(ArduinoFake(Serial), write, size_t(const uint8_t*, size_t))).AlwaysReturn(1);
    When(Method(ArduinoFake(Serial), flush)).AlwaysReturn();
    /* REQUIRED (mirrors test_sdp_harness.cpp / D-05): the real
     * rurp_register_utils.h calls delayMicroseconds, and
     * eeprom28c_check_chip_id / eeprom28c_wait_for_write call delay() /
     * delayMicroseconds() too. ArduinoFake ABORTS (SIGABRT) on any unmocked
     * virtual. Do not remove these as "unused" — they are load-bearing. */
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
    s_poll_addr_toggles = false;
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
    h.chip_id = 0; /* skip chip-id branch for cases 1-5 */
    h.mem_size = row.mem_size;
    h.bus_config = row.bus_config;
    h.ctrl_flags = FLAG_SKIP_BLANK_CHECK;
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

    return UNITY_END();
}
