/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 *
 * Phase 141 Plan 03 (LOOP-01..LOOP-08, D-10) -- the suite skeleton for the
 * per-byte program loop oracle: setUp hooks wiring all three host_stubs.cpp
 * recorder layers, a fixed make_loop_handle/drive_loop_write contract for
 * plans 141-07/141-08 to drive against, the three bus_config_t literals
 * those plans need, and six LOOP-INDEPENDENT harness cases that prove the
 * harness itself is non-vacuous.
 *
 * This plan completes NO requirement (frontmatter requirements: []) --
 * every case below is harness self-verification, true both before and after
 * plan 141-04's loop rewrite. Dimension-1 requirement coverage (LOOP-01..08)
 * is plan 141-09's, after every piece of evidence exists.
 *
 * Plans 141-07 and 141-08 EXTEND this same file (see their own
 * files_modified) rather than creating a new one -- so every symbol,
 * constant and helper below is authored as a fixed, reusable contract, not
 * a plan-141-03-only convenience.
 */

#include <Arduino.h>
#include <ArduinoFake.h>
#include <unity.h>
#include <string.h>
#include <stdio.h>

/* A TEST TU may pair <Arduino.h> with <ArduinoFake.h> -- the 14-macro-
 * redefinition trap against the native warning watermark (1166, zero
 * headroom) bites PRODUCTION TUs that pair <Arduino.h> with the
 * avr/pgmspace.h host shim, not test TUs like this one (140-RESEARCH.md
 * Pitfall 1, restated in eprom_params.h's own header comment). */

extern "C" {
#include "memory.h"
}
#include "firestarter.h"
#include "eprom.h"
#include "eprom_params.h"
#include "eprom_budget.h"  /* Plan 143-01: eprom_worst_pulses / eprom_per_byte_budget_us /
                             * eprom_block_budget_s -- BF-3-corrected budget arithmetic. */
#include "memory_utils.h"
#include "messages.h"  /* Plan 141-07: MSG_ERR_MAX_PULSES / MSG_ERR_ENERGY_CAP --
                         * neither firestarter.h nor eprom.h/eprom_params.h/
                         * memory_utils.h pulls this in transitively. */

using namespace fakeit;

/* ─────────────────────────────────────────────────────────────────────────
 * Restated locally, because #defines inside host_stubs.cpp's translation
 * unit are invisible here, a SEPARATE translation unit -- mirrors
 * test_trace_eprom_v131.cpp's identical restatement of these same four
 * kind constants and the shared .inc's two 512 caps (host_stubs_common.inc:
 * HOST_STUBS_MAX_STROBES / HOST_STUBS_MAX_TIMINGS).
 * ───────────────────────────────────────────────────────────────────────── */
#define STROBE_KIND_DATA     1
#define STROBE_KIND_PIN      2
#define TIMING_KIND_DELAY_US 3
#define TIMING_KIND_DELAY_MS 4
#define LOOP_STROBE_CAP 512
#define LOOP_TIMING_CAP 512

/* Shared strobe/timing recorder accessors (../_shared/host_stubs_common.inc,
 * compiled into host_stubs.cpp's translation unit under the
 * HOST_STUBS_REAL_REGISTER_UTILS + HOST_STUBS_RECORD_TIMING arms). This
 * suite has no shared "_expected.h" header of its own (unlike
 * test_trace_eprom_v131, which gets these from ../_shared/eprom_v131_expected.h)
 * -- declared directly here instead, once, so plans 141-07/141-08 (which
 * extend THIS file) get the full six-strobe/six-timing set from a single
 * place without needing a new shared header. */
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
extern "C" void     timing_push(uint8_t kind, uint32_t us);

/* host_stubs.cpp's own seams (Task 1). reset_register_cache mirrors
 * test_trace_eprom_v131's seam of the same name; the rest (the
 * loop_readback_ and logged_id_ families) are new to this suite.
 * rurp_read_data_buffer and rurp_log_id/_u8/_u16/_u24/_u32 are already
 * declared via firestarter.h -> rurp_shield.h, so they are not re-declared
 * here. */
extern "C" void reset_register_cache(uint8_t lsb, uint8_t msb, rurp_register_t ctrl);

extern "C" void loop_readback_reset(void);
extern "C" void loop_readback_seed(uint16_t addr16, uint8_t target, uint16_t converge_after);
extern "C" int  loop_readback_reads(uint16_t addr16);
extern "C" int  loop_readback_seeded_count(void);

extern "C" void     clear_logged_ids(void);
extern "C" int      logged_id_count(void);
extern "C" uint8_t  logged_id_at(int i);
extern "C" uint8_t  logged_id_param_count(int i);
extern "C" uint8_t  logged_id_param(int i, int j);
extern "C" int      logged_ids_overflowed(void);

/* ─────────────────────────────────────────────────────────────────────────
 * setUp / tearDown
 * ───────────────────────────────────────────────────────────────────────── */

/* Phase 143 Plan 05 (HOST-02, D-02/D-03) -- advancing millis() clock, file-
 * static so the AlwaysDo lambda in setUp (a capture-less closure, matching
 * this file's existing delay()/delayMicroseconds() lambdas) can mutate it.
 * Reset to 0 in setUp below. Precedent: test_cobs_data_frame.cpp's own
 * millis_counter (that file uses ArduinoFake(Function) rather than this
 * file's established bare ArduinoFake() form for delay/delayMicroseconds/
 * micros -- matched to THIS file's own convention below rather than
 * switched, since both forms link and this file is already consistent). */
static unsigned long millis_counter;

void setUp(void) {
    ArduinoFakeReset();
    When(OverloadedMethod(ArduinoFake(Serial), write, size_t(uint8_t))).AlwaysReturn(1);
    When(OverloadedMethod(ArduinoFake(Serial), write, size_t(const uint8_t*, size_t))).AlwaysReturn(1);
    When(Method(ArduinoFake(Serial), flush)).AlwaysReturn();

    /* THE hook (mirrors test_trace_eprom_v131.cpp's setUp): delay()/
     * delayMicroseconds() are free functions DEFINED by ArduinoFake's
     * FunctionFake.cpp, not stubbed anywhere in the shared .inc -- every
     * suite that reaches them mocks them in its own setUp(). Capture-less
     * lambdas: timing_push is a free extern "C" symbol, nothing needs
     * capturing. Do not remove these as "unused" -- case 2 below is the
     * load-bearing, non-vacuous proof that they fire, and every later
     * drive_loop_write-based case (plans 141-07/141-08) depends on them. */
    When(Method(ArduinoFake(), delayMicroseconds)).AlwaysDo([](unsigned int us) {
        timing_push(TIMING_KIND_DELAY_US, (uint32_t)us);
    });
    When(Method(ArduinoFake(), delay)).AlwaysDo([](unsigned long ms) {
        timing_push(TIMING_KIND_DELAY_MS, (uint32_t)ms);
    });
    /* Phase 143 Plan 05 (HOST-02, D-02/D-03) -- replaces the old
     * `AlwaysReturn(0)` frozen mock. eprom.cpp's new intra-block progress
     * emission (src/proms/eprom.cpp, guarded #ifndef SERIAL_ON_IO --
     * compiled IN on this native env, exactly as on leonardo) is TIME-gated
     * via millis(): frozen at 0, it would NEVER fire, so a cadence case
     * would pass VACUOUSLY with zero frames. Advances by a fixed 200 ms
     * step per call (same fixed-increment shape as test_cobs_data_frame.cpp's
     * millis_counter precedent, which prevents an infinite spin in any
     * timeout loop that polls millis()).
     *
     * 200 ms, not a rounder 500 ms, is a deliberate, measured choice
     * (D-25 finding, this plan's own execution): the emission fires at the
     * TOP of the outer per-byte loop, BEFORE the LOOP-06 skips (by design,
     * so the cadence is skip-count-independent) -- so it also fires on
     * every iteration of every PRE-EXISTING case's drive, not just this
     * plan's own two cases. The longest pre-existing block in this suite is
     * 4 bytes (grep-confirmed), and
     * test_loop06_a_block_of_only_skipped_bytes_emits_no_pulse_at_all
     * asserts logged_id_count() == 0 on exactly such a 4-byte, all-0xFF
     * drive -- a step of 500 ms (tried first) accumulates past
     * EPROM_PROGRESS_EMIT_INTERVAL_MS (1000) within that case's own 4
     * iterations and turns it RED (observed: "Expected 0 Was 2"), which is
     * this plan's own no-change-to-pre-existing-cases constraint, violated.
     * 200 ms keeps 4 iterations' worst-case accumulated delta at 800 ms
     * (4 * 200), safely under the 1000 ms interval, while this plan's own
     * two cases below use a 16-byte block (still capped at 8 DISTINCT
     * read-back-model seeds -- LOOP_READBACK_MAX_ENTRIES) to reach enough
     * iterations for the cadence to repeat. test_progress_emits_nothing_
     * when_the_clock_does_not_advance below locally re-mocks this method
     * with AlwaysReturn(0) for the span of its own case only -- the NEXT
     * case's ArduinoFakeReset() above wipes that override and this line
     * reinstalls the advancing lambda fresh every case, so no case can ever
     * inherit another's clock behaviour. */
    millis_counter = 0;
    When(Method(ArduinoFake(), millis)).AlwaysDo([]() -> unsigned long {
        millis_counter += 200;
        return millis_counter;
    });
    When(Method(ArduinoFake(), micros)).AlwaysReturn(0);

    clear_strobes();
    clear_timings();
    clear_logged_ids();
    loop_readback_reset();
    reset_register_cache(0x00, 0x00, 0x00);
}

void tearDown(void) {
    /* Plan 141-08 (LOOP-08's DIP32 cases): reset any hardware-revision
     * override back to the file's default (REVISION_0, via
     * host_stubs_common.inc's zero-initialised s_host_config) so it can
     * never leak into a case that runs after one of the DIP32 cases below
     * -- Unity calls tearDown() even when a case fails via TEST_ASSERT's
     * longjmp, so this reset is unconditional and always runs. */
    rurp_get_config()->hardware_revision = 0;
}

/* ─────────────────────────────────────────────────────────────────────────
 * make_loop_handle -- fresh, zero-initialised handle per case. json_parse()
 * never resets pulse_delay, protocol, mem_size, vpp_mv or pins
 * (src/json_parser.c:81-89), so a stale global handle would leak state
 * between cases (the same pitfall test_eprom_params_v131.cpp's make_handle
 * and test_trace_eprom_v131.cpp's make_v131_handle both guard against).
 * Unused by this plan's own six cases (all loop-independent harness
 * self-checks) -- authored now so plans 141-07/141-08 inherit a fixed
 * contract instead of re-deriving their own. Silenced via [[maybe_unused]]
 * rather than deleted.
 * ───────────────────────────────────────────────────────────────────────── */
[[maybe_unused]] static firestarter_handle_t make_loop_handle(uint32_t protocol, uint8_t pins, uint32_t mem_size,
                                                                uint32_t pulse_delay_us, const bus_config_t& bus_config) {
    firestarter_handle_t h = {};
    h.protocol = protocol;
    h.pins = pins;
    h.mem_size = mem_size;
    h.pulse_delay = pulse_delay_us;
    h.bus_config = bus_config;
    h.cmd = CMD_WRITE;
    h.response_code = RESPONSE_CODE_OK;
    h.ctrl_flags = FLAG_SKIP_BLANK_CHECK | FLAG_SKIP_ERASE;
    return h;
}

/* ─────────────────────────────────────────────────────────────────────────
 * bus_config ground truth, copied VERBATIM (renamed LOOP_BUS_CONFIG_0x07 /
 * _0x08 / _0x0B) from test_trace_eprom_v131.cpp's V131_BUS_CONFIG_0x07 /
 * _0x08 / _0x0B -- do NOT invent new ones: a zeroed bus_config is
 * DEGENERATE, not an identity remap (mem_util_remap_address_bus starts from
 * `config.address_mask & address`, and address_mask == 0 collapses every
 * address to 0). Derivation command (run live against firestarter_app,
 * 2026-08-08):
 *   cd /workspaces/firestarter_app && python3 -c "
 *     import sys
 *     sys.path.insert(0, 'tools'); sys.path.insert(0, '.')
 *     from gen_sdp_bus_config import derive_row
 *     from firestarter.database import EpromDatabase
 *     db = EpromDatabase(skip_local_override=True)
 *     for chip in ['AM27C512', 'AM27C020', 'AM2716']:
 *         print(chip, derive_row(db, chip))"
 * Unused by this plan's own six cases -- authored now, alongside
 * make_loop_handle above, for plans 141-07/141-08.
 * ───────────────────────────────────────────────────────────────────────── */

/* AM27C512 (protocol 0x07) -- pinout DIP28_27512, mem_size 65536, pulse
 * 100 us (the modal 0x07 value). derive_row: bus=[0..15], matching_lines=16,
 * rw_line=None, vpp_pin=None, static_high=None. */
[[maybe_unused]] static const bus_config_t LOOP_BUS_CONFIG_0x07 = {
    { 0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0A, 0x0B, 0x0C, 0x0D, 0x0E, 0x0F, 0xFF },
    0x0000FFFFUL,
    16,
    0xFF,
    0xFF,
    0x00000000UL
};

/* AM27C020 (protocol 0x08) -- pinout DIP32_27C020, mem_size 262144, pulse
 * 100 us (the modal 0x08 value). derive_row: bus=[0..16,20],
 * matching_lines=17, rw_line=22, vpp_pin=21, static_high=None. Note
 * vpp_pin=21=0x15=VPP_P1_32_DIP exactly, so using_p1_as_vpp(handle) is TRUE
 * for this chip (handle.pins==32) -- mem_util_remap_address_bus therefore
 * does NOT OR a VPP bit into the address bus at all, and
 * eprom_internal_set_control_register remaps CTRL_VPE_ENABLE to
 * CTRL_VPP_P1_ENABLE for every per-pass VPE assert/release. Both are real,
 * derived-from-source consequences of this chip's actual wiring, not a
 * special case coded here. matching_lines=17 / static_high_mask=0 below is
 * also this suite's own read-back-model key derivation (host_stubs.cpp): it
 * is the reason the 16-bit LSB|MSB<<8 key equals address & 0xFFFF for this,
 * the tree's only 32-pin config. */
[[maybe_unused]] static const bus_config_t LOOP_BUS_CONFIG_0x08 = {
    { 0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0A, 0x0B, 0x0C, 0x0D, 0x0E, 0x0F, 0x10, 0x14, 0xFF },
    0x0011FFFFUL,
    17,
    0x16,
    0x15,
    0x00000000UL
};

/* AM2716 (protocol 0x0B) -- pinout DIP24_2716, mem_size 2048, pulse 500 us
 * (the modal 0x0B value, and the exact figure chip C1's adjudication table
 * names). derive_row: bus=[0..10], matching_lines=11, rw_line=None,
 * vpp_pin=11, static_high=[13]. vpp_pin=11=0x0B=VPP_P21_24_DIP exactly, so
 * using_p1_as_vpp(handle) is also TRUE for this chip (handle.pins==24) --
 * same two real consequences as AM27C020 above, this time for a completely
 * different reason (a 24-pin, not 32-pin, P1-routing constant). */
[[maybe_unused]] static const bus_config_t LOOP_BUS_CONFIG_0x0B = {
    { 0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0A, 0xFF },
    0x000007FFUL,
    11,
    0xFF,
    0x0B,
    0x00002000UL
};

/* ─────────────────────────────────────────────────────────────────────────
 * drive_loop_write -- the fixed drive-helper contract for plans 141-07/
 * 141-08. Modelled on test_trace_eprom_v131.cpp's drive_v131_write:
 *
 *   configure_memory (writes address 0 itself, memory.cpp:93)
 *   -> reset_register_cache
 *   -> clear_strobes / clear_timings / clear_logged_ids
 *   -> seed address / data_size / data_buffer
 *   -> h->firestarter_operation_main(h)  -- NEVER _init, NEVER the whole
 *      command.
 *
 * Never _init: eprom_write_execute enables the VPP regulator itself on
 * entry if it is not already enabled, so skipping _init keeps the capture
 * scoped to exactly the per-byte loop this suite exists to prove. Never the
 * whole command: command_done() writes CONTROL_REGISTER = 0x00 on every
 * exit regardless of what the write-execute path did, which would make a
 * high-voltage assertion vacuous. Never re-assign h->firestarter_get_data /
 * h->firestarter_set_data: keeping the real memory_get_data / memory_set_data
 * in the path captures the verify read's own bus activity too (D-05
 * expressed as a test constraint).
 *
 * Authored now and left UNUSED by this plan's own six cases (all
 * loop-independent harness self-checks) so plans 141-07/141-08 inherit this
 * exact, fixed contract rather than re-deriving their own. Silenced via
 * [[maybe_unused]] rather than deleted -- same treatment as
 * make_loop_handle and the three bus_config literals above.
 * ───────────────────────────────────────────────────────────────────────── */
[[maybe_unused]] static void drive_loop_write(firestarter_handle_t* h, uint32_t base,
                                               const uint8_t* block, uint8_t n) {
    configure_memory(h);
    reset_register_cache(0x00, 0x00, 0x00);
    clear_strobes();
    clear_timings();
    clear_logged_ids();
    h->address = base;
    h->data_size = n;
    for (uint8_t i = 0; i < n; i++) {
        h->data_buffer[i] = (char)block[i];
    }
    h->firestarter_operation_main(h);
}

/* ─────────────────────────────────────────────────────────────────────────
 * Six loop-independent harness cases. Each proves the harness itself is
 * non-vacuous (including two explicit negative controls); none drives
 * eprom_write_execute or any protocol handler, so every case stays true
 * both before and after plan 141-04's loop rewrite (D-10). This plan
 * completes NO requirement -- see the file banner above.
 * ───────────────────────────────────────────────────────────────────────── */

/* The baseline every later case's assertions build on: setUp() alone must
 * leave all THREE recorders (strobe, timing, logged-id) empty and
 * un-overflowed. */
void test_setup_leaves_all_three_recorders_clean(void) {
    TEST_ASSERT_EQUAL_MESSAGE(0, strobe_count(), "strobe_count after setUp");
    TEST_ASSERT_EQUAL_MESSAGE(0, timing_count(), "timing_count after setUp");
    TEST_ASSERT_EQUAL_MESSAGE(0, logged_id_count(), "logged_id_count after setUp");
    TEST_ASSERT_EQUAL_MESSAGE(0, strobe_overflowed(), "strobe_overflowed after setUp");
    TEST_ASSERT_EQUAL_MESSAGE(0, timing_overflowed(), "timing_overflowed after setUp");
    TEST_ASSERT_EQUAL_MESSAGE(0, logged_ids_overflowed(), "logged_ids_overflowed after setUp");
}

/* Drives delay()/delayMicroseconds() DIRECTLY -- no production code
 * involved yet -- and proves the setUp() hook actually fires, in this
 * order, with the right kind and argument each time. This is the
 * load-bearing, non-vacuous proof LOOP-07's oracle (mem_util_delay_us's
 * ms/us split) depends on: a native stub records no elapsed time at all,
 * only the arguments passed to the mocked calls. */
void test_timing_hook_records_both_delay_kinds_with_their_arguments(void) {
    delay(7);
    delayMicroseconds(11);

    TEST_ASSERT_EQUAL_MESSAGE(2, timing_count(), "timing_count after delay(7); delayMicroseconds(11)");
    TEST_ASSERT_EQUAL_MESSAGE(0, timing_overflowed(), "timing_overflowed after direct delay calls");

    TEST_ASSERT_EQUAL_MESSAGE(TIMING_KIND_DELAY_MS, timing_kind(0), "entry 0 kind");
    TEST_ASSERT_EQUAL_MESSAGE(7, timing_us(0), "entry 0 us");

    TEST_ASSERT_EQUAL_MESSAGE(TIMING_KIND_DELAY_US, timing_kind(1), "entry 1 kind");
    TEST_ASSERT_EQUAL_MESSAGE(11, timing_us(1), "entry 1 us");
}

/* Positive case: reads before convergence return 0xFF, the read AT
 * convergence returns the seeded target, and the observed read count
 * matches host_stubs.cpp's documented read-count-to-pulse-count mapping
 * (converge_after=2 -> matches on read 3). */
void test_readback_model_returns_ff_until_converge_then_the_target(void) {
    loop_readback_seed(0x1234, 0x5A, 2);
    reset_register_cache(0x34, 0x12, 0x00);

    TEST_ASSERT_EQUAL_HEX8_MESSAGE(0xFF, rurp_read_data_buffer(), "read 1: before convergence");
    TEST_ASSERT_EQUAL_HEX8_MESSAGE(0xFF, rurp_read_data_buffer(), "read 2: before convergence");
    TEST_ASSERT_EQUAL_HEX8_MESSAGE(0x5A, rurp_read_data_buffer(), "read 3: converged, returns target");

    TEST_ASSERT_EQUAL_MESSAGE(3, loop_readback_reads(0x1234), "loop_readback_reads after three reads");
}

/* Negative control (T-141-GATE): with only 0x1234 seeded, an unseeded
 * address must return 0xFF and must NOT be silently created -- without
 * this, the positive case above could pass on a model that fabricates
 * entries for any address it is asked about. */
void test_readback_model_returns_ff_and_stays_unseeded_for_an_unknown_address(void) {
    loop_readback_seed(0x1234, 0x5A, 2);
    reset_register_cache(0xFF, 0x00, 0x00);

    TEST_ASSERT_EQUAL_HEX8_MESSAGE(0xFF, rurp_read_data_buffer(), "unseeded address 0x00FF must return 0xFF");
    TEST_ASSERT_EQUAL_MESSAGE(-1, loop_readback_reads(0x00FF), "unseeded address must report -1 reads, never silently created");
    TEST_ASSERT_EQUAL_MESSAGE(1, loop_readback_seeded_count(), "seeded_count must stay 1 -- the read must not have created an entry");
}

/* The exact property plan 141-08's D-09 A16-crossing case depends on: two
 * addresses on opposite sides of the 0x00FFFF/0x010000 boundary, latched
 * ALTERNATELY (interleaved reads, so a shared/aliased counter would show up
 * immediately), must keep fully independent read counters. */
void test_readback_model_distinguishes_two_addresses_across_an_a16_crossing(void) {
    loop_readback_seed(0xFFFE, 0x11, 1);
    loop_readback_seed(0x0000, 0x22, 2);

    reset_register_cache(0xFE, 0xFF, 0x00);
    TEST_ASSERT_EQUAL_HEX8_MESSAGE(0xFF, rurp_read_data_buffer(), "0xFFFE read 1: before convergence");

    reset_register_cache(0x00, 0x00, 0x00);
    TEST_ASSERT_EQUAL_HEX8_MESSAGE(0xFF, rurp_read_data_buffer(), "0x0000 read 1: before convergence");

    reset_register_cache(0xFE, 0xFF, 0x00);
    TEST_ASSERT_EQUAL_HEX8_MESSAGE(0x11, rurp_read_data_buffer(), "0xFFFE read 2: converged, returns target");

    reset_register_cache(0x00, 0x00, 0x00);
    TEST_ASSERT_EQUAL_HEX8_MESSAGE(0xFF, rurp_read_data_buffer(), "0x0000 read 2: still before convergence");

    reset_register_cache(0x00, 0x00, 0x00);
    TEST_ASSERT_EQUAL_HEX8_MESSAGE(0x22, rurp_read_data_buffer(), "0x0000 read 3: converged, returns target");

    TEST_ASSERT_EQUAL_MESSAGE(2, loop_readback_reads(0xFFFE), "0xFFFE keeps its own independent read counter");
    TEST_ASSERT_EQUAL_MESSAGE(3, loop_readback_reads(0x0000), "0x0000 keeps its own independent read counter");
}

/* rurp_log_id_u24 packs its argument big-endian into exactly 3 bytes
 * (src/boards/rurp_serial_utils.cpp) -- proves the strong rurp_log_id
 * override in host_stubs.cpp actually captures both the id and the packed
 * params, not merely that it links. */
void test_logged_id_capture_records_the_id_and_its_packed_params(void) {
    rurp_log_id_u24(0xB1, 0x012345UL);

    TEST_ASSERT_EQUAL_MESSAGE(1, logged_id_count(), "logged_id_count after one rurp_log_id_u24 call");
    TEST_ASSERT_EQUAL_HEX8_MESSAGE(0xB1, logged_id_at(0), "logged id");
    TEST_ASSERT_EQUAL_MESSAGE(3, logged_id_param_count(0), "u24 packs exactly 3 param bytes");
    TEST_ASSERT_EQUAL_HEX8_MESSAGE(0x01, logged_id_param(0, 0), "param byte 0 (MSB)");
    TEST_ASSERT_EQUAL_HEX8_MESSAGE(0x23, logged_id_param(0, 1), "param byte 1");
    TEST_ASSERT_EQUAL_HEX8_MESSAGE(0x45, logged_id_param(0, 2), "param byte 2 (LSB)");
}

/* ═════════════════════════════════════════════════════════════════════════
 * Plan 141-07 (LOOP-01, LOOP-06, LOOP-04) -- behaviour cases proving the
 * per-byte program loop's cadence, its skip rules and its energy cap,
 * driven through drive_loop_write / make_loop_handle / LOOP_BUS_CONFIG_*
 * (plan 141-03's fixed contract) against the REAL eprom_write_execute
 * (plan 141-04, src/proms/eprom.cpp). This plan supplies the WHOLE proof
 * for LOOP-01, LOOP-04 and LOOP-06 and flips NO requirement checkbox --
 * that is plan 141-09's, after every piece of evidence exists (frontmatter
 * requirements: [] is deliberate, per this plan's own <objective>).
 *
 * Plan 141-08 extends this SAME file with LOOP-03, LOOP-05, LOOP-07 and
 * LOOP-08 cases -- nothing below pre-empts those.
 * ═════════════════════════════════════════════════════════════════════════ */

/* Small local helpers, shared by every case below -- neither plan 141-03's
 * harness nor host_stubs.cpp provides them; they belong to THIS plan's own
 * cases, not to the fixed drive-helper contract. */
static int count_strobe_kind(uint8_t kind) {
    int n = strobe_count();
    int c = 0;
    for (int i = 0; i < n; i++) {
        if (strobe_kind(i) == kind) c++;
    }
    return c;
}

static int count_logged_id(uint8_t id) {
    int n = logged_id_count();
    int c = 0;
    for (int i = 0; i < n; i++) {
        if (logged_id_at(i) == id) c++;
    }
    return c;
}

static int find_logged_id(uint8_t id) {
    int n = logged_id_count();
    for (int i = 0; i < n; i++) {
        if (logged_id_at(i) == id) return i;
    }
    return -1;
}

/* LOOP_BUS_CONFIG_0x0B is the only one of the three bus_config literals
 * with a nonzero static_high_mask (0x00002000UL, bit 13):
 * mem_util_remap_address_bus (src/proms/memory.cpp:350) does
 * `reorg_address |= config.static_high_mask` UNCONDITIONALLY, on every
 * address, for both the read and the write path. So the read-back model's
 * key for a byte at real (handle-level, unmapped) address A on this
 * bus_config is A + 0x2000, not A -- source-verified, not assumed: A's low
 * 11 bits pass through address_mask (0x000007FF) unchanged, matching_lines
 * (11) already points at the config's 0xFF terminator so no per-line
 * remap runs, rw_line is 0xFF (skipped) and vpp_line's OR is skipped
 * because using_p1_as_vpp(handle) is true for this pins==24/vpp_line==0x0B
 * combination (memory_utils.h:43-47) -- static_high_mask is the ONLY term
 * left standing. LOOP_BUS_CONFIG_0x07 and _0x08 both carry
 * static_high_mask == 0x00000000UL, so neither needs this adjustment; only
 * 0x0B-driven cases below call this helper. The LOGGED payload address
 * bytes (eprom_internal_report_budget_failure's u24) are unaffected -- they
 * carry handle->address + i, the real unmapped address, never the
 * remapped register-level key. */
static uint16_t k0b(uint32_t real_addr) {
    return (uint16_t)(real_addr + 0x2000UL);
}

/* ─────────────────────────────────────────────────────────────────────────
 * LOOP-01 (task 1) -- fixed-width pulses, verify after each pulse, an
 * exact per-byte pulse count, and success at the max_pulses boundary.
 * Every case here drives protocol 0x07 (28-pin, mem_size 65536,
 * max_pulses 25, energy_cap_us 0 == uncapped -- eprom_params.cpp:50),
 * LOOP_BUS_CONFIG_0x07 (static_high_mask 0, so no key-remap adjustment is
 * needed for this protocol).
 * ───────────────────────────────────────────────────────────────────────── */

/* Case 1: each byte gets exactly the seeded number of fixed-width pulses.
 *
 * Read-count-to-pulse-count mapping (stated explicitly, per plan): the
 * loop reads FIRST (LOOP-06's skip check) and only then pulses, so seeding
 * converge_after = N means the byte matches on read N+1, i.e. after
 * exactly N pulses -- loop_readback_reads(addr) == 1 + pulses. */
/* FINDING (this plan's own, made during execution -- documented here and
 * in the SUMMARY, not silently absorbed): rurp_internal_write_to_register
 * (include/rurp_register_utils.h:63-89, production code, real via
 * HOST_STUBS_REAL_REGISTER_UTILS) shifts EVERY non-elided register write
 * (LSB, MSB, or CONTROL) through rurp_write_data_buffer() -- the EXACT same
 * function memory_set_data calls for the actual chip-data pulse. Both
 * therefore push an indistinguishable-BY-KIND STROBE_KIND_DATA entry (same
 * kind, same pin (0)). A bare "count of STROBE_KIND_DATA == total pulse
 * count" claim is consequently unsound: register-write noise varies by
 * pin count and even by call direction (0x08's bus_config.rw_line makes
 * every read<->write transition force a non-elided CONTROL rewrite, so its
 * noise SCALES with pulse count, not just a fixed per-drive floor --
 * measured directly: a 0-pulse baseline for 0x08 undercounts a genuine
 * 2-pulse run by 6, not 2).
 *
 * The robust oracle is the entry's VALUE, not a raw count: a genuine
 * chip-data pulse's rurp_write_data_buffer(data) call always carries
 * data == the byte actually being programmed (memory_set_data's own
 * `data` parameter); a register-shift's call carries a REGISTER value
 * (an LSB/MSB address byte, or a CONTROL bitmask like 0x80/0x81/0x91/etc).
 * Every seeded byte value in this file's cases (0x3C, 0x55, 0xAA, 0x0F)
 * is chosen so it can never collide with a register value these specific
 * scenarios ever produce (addresses stay under 256, so LSB/MSB never
 * exceed the low bus lines' range, and every observed CONTROL value stays
 * in the VPP/route-bit low range) -- filtering STROBE_KIND_DATA entries by
 * strobe_value() == the expected byte therefore counts pulses of THAT byte
 * exactly, independent of any register-write noise or its scaling. */
static int count_data_pulses_with_value(uint8_t value) {
    int n = strobe_count();
    int c = 0;
    for (int i = 0; i < n; i++) {
        if (strobe_kind(i) == STROBE_KIND_DATA && strobe_value(i) == value) c++;
    }
    return c;
}

void test_loop01_each_byte_gets_exactly_the_seeded_number_of_fixed_width_pulses(void) {
    firestarter_handle_t h = make_loop_handle(0x07, 28, 65536, 100, LOOP_BUS_CONFIG_0x07);
    const uint8_t block[4] = {0x3C, 0x55, 0xAA, 0x0F};
    const uint16_t converge_after[4] = {1, 2, 3, 4};
    for (int i = 0; i < 4; i++) {
        loop_readback_seed((uint16_t)i, block[i], converge_after[i]);
    }
    drive_loop_write(&h, 0, block, 4);

    TEST_ASSERT_EQUAL_MESSAGE(RESPONSE_CODE_OK, h.response_code, "response_code");

    /* Read-count-to-pulse-count mapping: the loop reads FIRST (LOOP-06's
     * skip check), pulses, and then -- because 0x07 ships
     * VERIFY_PER_PULSE_PLUS_FINAL -- reads EVERY byte ONE MORE time in the
     * unconditional final full-block pass that runs after the per-byte
     * loop (src/proms/eprom.cpp:296-314), regardless of whether that byte
     * converged, was skipped, or already matched. So
     * loop_readback_reads(addr) == 1 (skip-check) + pulses (one verify per
     * pulse) + 1 (the final pass's own read) == 2 + pulses. */
    const int expected_reads[4] = {3, 4, 5, 6}; /* 2 + converge_after[i] */
    for (int i = 0; i < 4; i++) {
        char msg[80];
        snprintf(msg, sizeof(msg), "loop_readback_reads(addr %d) == 2 + pulses (skip-check + N verify + 1 final-pass read)", i);
        TEST_ASSERT_EQUAL_MESSAGE(expected_reads[i], loop_readback_reads((uint16_t)i), msg);
    }

    /* Per-byte pulse count, cross-checked directly against the strobe
     * stream by VALUE (see count_data_pulses_with_value's own comment) --
     * independent corroboration of the reads-based counts above, from a
     * completely different signal. */
    const int expected_pulses[4] = {1, 2, 3, 4};
    for (int i = 0; i < 4; i++) {
        char msg[80];
        snprintf(msg, sizeof(msg), "count_data_pulses_with_value(block[%d]) matches converge_after[%d]", i, i);
        TEST_ASSERT_EQUAL_MESSAGE(expected_pulses[i], count_data_pulses_with_value(block[i]), msg);
    }
    TEST_ASSERT_EQUAL_MESSAGE(10,
        count_data_pulses_with_value(0x3C) + count_data_pulses_with_value(0x55) + count_data_pulses_with_value(0xAA) + count_data_pulses_with_value(0x0F),
        "total pulses across the block == 1+2+3+4");
}

/* Case 2: pulse width never grows between attempts. With
 * read_settling_us == 0 and read_strobe_us == 0 (handle defaults), the
 * TIMING_KIND_DELAY_US values genuinely tied to the pulse/verify cadence
 * are {3, 100}: 3 us is memory_set_data's pre-pulse settle (memory.cpp
 * ~:300) PLUS memory_get_data's default verify-read strobe (:278-280) --
 * neither is counted toward the per-byte accumulated program time (D-02).
 * 100 us is the pulse itself (org_delay, never grown). Any FOURTH distinct
 * value would be exactly the adaptive-growth formula LOOP-02 removed.
 *
 * A third value, 1 us, IS expected and is NOT growth: it is
 * rurp_internal_write_to_register's own fixed post-latch delay
 * (include/rurp_register_utils.h:86, `delayMicroseconds(1);` -- literally
 * commented "Probably useless - verify later" in production), emitted
 * once per NON-ELIDED register write (LSB/MSB/CONTROL), entirely unrelated
 * to any pulse. This drive also emits exactly one TIMING_KIND_DELAY_MS(500)
 * entry (the once-per-block VPE-assert settle) -- excluded from this
 * case's scan by filtering on TIMING_KIND_DELAY_US, exactly as the plan's
 * own instruction says ("walk every TIMING_KIND_DELAY_US entry"). */
void test_loop01_pulse_width_never_grows_between_attempts(void) {
    firestarter_handle_t h = make_loop_handle(0x07, 28, 65536, 100, LOOP_BUS_CONFIG_0x07);
    const uint8_t block[4] = {0x3C, 0x55, 0xAA, 0x0F};
    const uint16_t converge_after[4] = {1, 2, 3, 4};
    for (int i = 0; i < 4; i++) {
        loop_readback_seed((uint16_t)i, block[i], converge_after[i]);
    }
    drive_loop_write(&h, 0, block, 4);

    TEST_ASSERT_EQUAL_MESSAGE(0, strobe_overflowed(), "strobe_overflowed -- small block, must be sound");
    TEST_ASSERT_EQUAL_MESSAGE(0, timing_overflowed(), "timing_overflowed -- small block, must be sound");

    int count_100 = 0;
    int n = timing_count();
    for (int i = 0; i < n; i++) {
        if (timing_kind(i) != TIMING_KIND_DELAY_US) continue;
        uint32_t us = timing_us(i);
        char msg[112];
        snprintf(msg, sizeof(msg), "timing entry %d (delayMicroseconds) has value %lu -- expected 1 (register-shift overhead), 3 or 100; any FOURTH distinct value is LOOP-02's growth", i, (unsigned long)us);
        TEST_ASSERT_TRUE_MESSAGE(us == 1UL || us == 3UL || us == 100UL, msg);
        if (us == 100UL) count_100++;
    }
    TEST_ASSERT_EQUAL_MESSAGE(10, count_100, "exactly one 100us pulse-width entry per pulse -- 10 total across the block (1+2+3+4)");
}

/* Case 3: a verify read follows every pulse. Deliberately does NOT assert
 * "exactly one CONTROL strobe per byte" or "no CONTROL strobe during a
 * verify read": mem_util_set_address writes CONTROL_REGISTER
 * unconditionally on every byte, for both the pulse and the verify
 * (memory.cpp:230-231), and a chip whose bus_config.rw_line is set
 * re-strobes CONTROL on the pulse-to-verify direction flip too. Both are
 * expected and neither is a LOOP-08 violation. */
void test_loop01_verify_read_follows_every_pulse(void) {
    firestarter_handle_t h = make_loop_handle(0x07, 28, 65536, 100, LOOP_BUS_CONFIG_0x07);
    const uint8_t block[4] = {0x3C, 0x55, 0xAA, 0x0F};
    const uint16_t converge_after[4] = {1, 2, 3, 4};
    for (int i = 0; i < 4; i++) {
        loop_readback_seed((uint16_t)i, block[i], converge_after[i]);
    }
    drive_loop_write(&h, 0, block, 4);

    TEST_ASSERT_EQUAL_MESSAGE(0, strobe_overflowed(), "strobe_overflowed -- small block, must be sound");
    TEST_ASSERT_EQUAL_MESSAGE(0, timing_overflowed(), "timing_overflowed -- small block, must be sound");

    int n = strobe_count();
    for (int i = 0; i < n; i++) {
        if (strobe_kind(i) != STROBE_KIND_DATA) continue;
        bool saw_pin_before_next_data = false;
        for (int j = i + 1; j < n && strobe_kind(j) != STROBE_KIND_DATA; j++) {
            if (strobe_kind(j) == STROBE_KIND_PIN) { saw_pin_before_next_data = true; break; }
        }
        char msg[96];
        snprintf(msg, sizeof(msg), "DATA strobe at index %d has no PIN strobe before the next DATA strobe (or end of stream)", i);
        TEST_ASSERT_TRUE_MESSAGE(saw_pin_before_next_data, msg);
    }
    /* This interleaving property holds for EVERY STROBE_KIND_DATA entry
     * regardless of whether it is register-shift noise or a genuine
     * chip-data pulse: every non-elided register write is ALSO
     * immediately followed by its own latch's PIN strobes
     * (rurp_internal_write_to_register), so scanning ALL of them (not
     * just the pulse-valued ones) is the stronger, more general check.
     * The total PULSE count (as opposed to the interleaving property) is
     * cross-checked precisely via the by-value filter, matching case 1. */
    TEST_ASSERT_EQUAL_MESSAGE(10,
        count_data_pulses_with_value(0x3C) + count_data_pulses_with_value(0x55) + count_data_pulses_with_value(0xAA) + count_data_pulses_with_value(0x0F),
        "total STROBE_KIND_DATA pulses (by value) matches case 1's pulse count");
}

/* Case 4: a byte that converges on its last permitted pulse succeeds --
 * the boundary proving the budget check happens AFTER the failed verify,
 * not before it. */
void test_loop01_a_byte_that_converges_on_its_last_permitted_pulse_succeeds(void) {
    firestarter_handle_t h = make_loop_handle(0x07, 28, 65536, 100, LOOP_BUS_CONFIG_0x07);
    const uint8_t block[1] = {0x3C};
    loop_readback_seed(0, block[0], 25);
    drive_loop_write(&h, 0, block, 1);

    TEST_ASSERT_EQUAL_MESSAGE(RESPONSE_CODE_OK, h.response_code,
        "response_code -- must succeed exactly at the max_pulses (25) boundary, not fail at it");
    /* 1 skip-check read + 25 verify reads (one per pulse) + 1 final-pass
     * read (0x07 ships VERIFY_PER_PULSE_PLUS_FINAL, which reads every byte
     * once more after the per-byte loop, regardless of convergence). */
    TEST_ASSERT_EQUAL_MESSAGE(27, loop_readback_reads(0), "1 skip-check + 25 verify + 1 final-pass read");
    TEST_ASSERT_EQUAL_MESSAGE(0, count_logged_id(MSG_ERR_MAX_PULSES),
        "no MSG_ERR_MAX_PULSES frame -- the budget check runs AFTER the failed verify, so a byte converging on pulse 25 never reaches it");
}

/* ─────────────────────────────────────────────────────────────────────────
 * LOOP-06 (task 2) -- skip rules for 0xFF and already-matching bytes, with
 * negative controls.
 *
 * DEVIATION FROM THE PLAN'S <action> PROSE, recorded here and in this
 * plan's own SUMMARY: cases 1-3 below drive protocol 0x0B, not 0x07 as the
 * plan's prose said, so their literal loop_readback_reads() values (the
 * plan's own <acceptance_criteria> numbers: 0, and 1/3) are actually true.
 * 0x07 ships VERIFY_PER_PULSE_PLUS_FINAL (eprom_params.cpp:50):
 * eprom_write_execute's final full-block pass (:296-314) reads EVERY byte
 * once more, unconditionally, after the per-byte loop -- including
 * 0xFF-skipped and already-matching bytes. Driving cases 1-3 on 0x07 would
 * add +1 to every loop_readback_reads() value from that pass (0 -> 1 for
 * the 0xFF byte, 1 -> 2 for the already-matching byte), CONTRADICTING the
 * plan's own stated acceptance numbers. 0x0B ships plain VERIFY_PER_PULSE
 * (no final pass), so it is the only protocol on which the per-byte loop's
 * OWN skip behaviour is directly observable, uncontaminated by a later
 * pass. Case 4 below is deliberately still 0x07 -- it is the case that
 * specifically proves the final pass DOES still run on a fully-skipped
 * block, which needs the PLUS_FINAL protocol to be meaningful at all; this
 * pairs exactly with LOOP-04 case 6 below (0x0B, the negative
 * counterpart: NO final pass runs).
 *
 * LOOP_BUS_CONFIG_0x0B's nonzero static_high_mask means every seed/read
 * key below goes through k0b() -- see that helper's own comment.
 * ───────────────────────────────────────────────────────────────────────── */

void test_loop06_an_ff_target_byte_is_never_read_and_never_pulsed(void) {
    firestarter_handle_t h = make_loop_handle(0x0B, 24, 2048, 100, LOOP_BUS_CONFIG_0x0B);
    const uint8_t block[4] = {0x3C, 0xFF, 0x55, 0xAA};
    const uint16_t converge_after[4] = {1, 0, 1, 1};
    for (int i = 0; i < 4; i++) {
        loop_readback_seed(k0b((uint32_t)i), block[i], converge_after[i]);
    }
    drive_loop_write(&h, 0, block, 4);

    TEST_ASSERT_EQUAL_MESSAGE(RESPONSE_CODE_OK, h.response_code, "response_code");
    /* The discriminating assertion: the 0xFF check runs BEFORE any read of
     * the byte, so byte 1 gets exactly ZERO reads -- not the single
     * skip-check read an already-matching byte gets (case 2 below). This
     * is what distinguishes the two skip rules from each other, and on its
     * own already proves zero pulses for that byte too: every pulse this
     * loop ever emits is followed by a verify read (LOOP-01), so zero
     * reads implies zero pulses without needing a separate strobe count
     * (which, per the noise-floor finding in LOOP-01 case 1's own comment,
     * cannot cleanly isolate "pulses" from register-shift writes anyway). */
    TEST_ASSERT_EQUAL_MESSAGE(0, loop_readback_reads(k0b(1)), "0xFF byte must get ZERO reads -- proves the 0xFF check precedes the read");
}

void test_loop06_an_already_matching_byte_is_read_once_and_never_pulsed(void) {
    firestarter_handle_t h = make_loop_handle(0x0B, 24, 2048, 100, LOOP_BUS_CONFIG_0x0B);
    const uint8_t block[2] = {0x3C, 0x55};
    loop_readback_seed(k0b(0), 0x3C, 0);  /* matches on the very first (skip-check) read */
    loop_readback_seed(k0b(1), 0x55, 2);
    drive_loop_write(&h, 0, block, 2);

    TEST_ASSERT_EQUAL_MESSAGE(RESPONSE_CODE_OK, h.response_code, "response_code");
    /* 1 read implies 0 pulses (the skip-check read itself already
     * matched); 3 reads implies exactly 3-1=2 pulses (skip-check + one
     * verify read per pulse) -- both by the same reads-imply-pulses
     * reasoning as case 1 above. */
    TEST_ASSERT_EQUAL_MESSAGE(1, loop_readback_reads(k0b(0)), "already-matching byte: exactly the skip-check read, no pulse");
    TEST_ASSERT_EQUAL_MESSAGE(3, loop_readback_reads(k0b(1)), "converging byte: skip-check read + 2 verify reads after 2 pulses");
}

void test_loop06_a_block_of_only_skipped_bytes_emits_no_pulse_at_all(void) {
    firestarter_handle_t h = make_loop_handle(0x0B, 24, 2048, 100, LOOP_BUS_CONFIG_0x0B);
    const uint8_t block[4] = {0xFF, 0xFF, 0xFF, 0xFF};
    for (int i = 0; i < 4; i++) {
        loop_readback_seed(k0b((uint32_t)i), 0xFF, 0);
    }
    drive_loop_write(&h, 0, block, 4);

    /* The ONE unavoidable DATA strobe here is the once-per-block VPE-assert
     * control-register write at the very top of eprom_write_execute -- it
     * fires unconditionally whenever CTRL_VPP_REGULATOR_ENABLE starts
     * clear (always true here: drive_loop_write's own reset_register_cache
     * always clears it before the drive), and it is NOT caused by, or
     * related to, any byte in the block. Every one of the four 0xFF bytes
     * itself contributes ZERO strobes of any kind: the `expected == 0xFF`
     * check short-circuits BEFORE any read or address-set call is ever
     * made for that byte -- confirmed independently below by all four
     * loop_readback_reads() being 0. */
    TEST_ASSERT_EQUAL_MESSAGE(1, count_strobe_kind(STROBE_KIND_DATA),
        "the ONLY DATA strobe in this drive is the structural once-per-block VPE-assert control write; no byte contributes one");
    for (int i = 0; i < 4; i++) {
        char msg[64];
        snprintf(msg, sizeof(msg), "loop_readback_reads(k0b(%d)) must be 0 -- never read at all (0x0B has no final pass)", i);
        TEST_ASSERT_EQUAL_MESSAGE(0, loop_readback_reads(k0b((uint32_t)i)), msg);
    }
    TEST_ASSERT_EQUAL_MESSAGE(RESPONSE_CODE_OK, h.response_code, "response_code");
    TEST_ASSERT_EQUAL_MESSAGE(0, logged_id_count(), "no error id logged for an all-0xFF block");

    /* Paired negative control (T-141-VACUOUS, this plan's own threat
     * register): without this, the zero-pulse assertion above could pass
     * on a loop that never ran at all (a broken drive helper, or a handle
     * that silently failed configure). A block with one byte that
     * genuinely needs programming, driven immediately afterward on a
     * disjoint address range, must push the count strictly ABOVE the
     * 1-strobe structural floor measured above -- ">0" alone would be
     * vacuously true even if that byte never pulsed, since the floor
     * itself is always >= 1. */
    firestarter_handle_t h2 = make_loop_handle(0x0B, 24, 2048, 100, LOOP_BUS_CONFIG_0x0B);
    const uint8_t block2[1] = {0x3C};
    loop_readback_seed(k0b(0x0100UL), 0x3C, 1);
    drive_loop_write(&h2, 0x0100UL, block2, 1);
    TEST_ASSERT_TRUE_MESSAGE(count_strobe_kind(STROBE_KIND_DATA) > 1,
        "negative control: a byte that needs programming must push the count above the 1-strobe structural floor -- otherwise the all-0xFF case above would be vacuous");
}

void test_loop06_the_ff_rule_does_not_suppress_the_final_verify_pass(void) {
    /* Deliberately 0x07 here (VERIFY_PER_PULSE_PLUS_FINAL) -- the
     * counterpart to the three cases above, which deliberately use 0x0B
     * (VERIFY_PER_PULSE, no final pass) to keep their read counts
     * uncontaminated. This case is what makes the verify_mode consumption
     * observable at all on a fully-skipped block: the per-byte loop itself
     * never reads any of these bytes (the 0xFF rule skips all four before
     * any read), so any read at all can only have come from the final
     * full-block pass. */
    firestarter_handle_t h = make_loop_handle(0x07, 28, 65536, 100, LOOP_BUS_CONFIG_0x07);
    const uint8_t block[4] = {0xFF, 0xFF, 0xFF, 0xFF};
    for (int i = 0; i < 4; i++) {
        loop_readback_seed((uint16_t)i, 0xFF, 0);
    }
    drive_loop_write(&h, 0, block, 4);

    TEST_ASSERT_EQUAL_MESSAGE(RESPONSE_CODE_OK, h.response_code, "response_code -- a seeded target of 0xFF matches on the final pass");
    for (int i = 0; i < 4; i++) {
        char msg[96];
        snprintf(msg, sizeof(msg), "loop_readback_reads(%d) must be >= 1 -- the final pass reads every byte even though the per-byte loop skipped them all", i);
        TEST_ASSERT_TRUE_MESSAGE(loop_readback_reads((uint16_t)i) >= 1, msg);
    }
}

/* ─────────────────────────────────────────────────────────────────────────
 * LOOP-04 (task 3) -- the 0x0B energy cap at all three shipped widths, and
 * no overprogram pulse on any live row.
 *
 * eprom_params_for(0x0B) ships energy_cap_us 50000, max_pulses 255,
 * overprogram_factor 0, verify_mode VERIFY_PER_PULSE, vpp_path
 * VPP_PATH_DIRECT_VPE (src/proms/eprom_params.cpp:52). Cases 1-4 seed
 * converge_after = 65535 so the byte can never converge and the energy
 * cap -- not a successful verify -- is what stops the loop.
 *
 * T-141-CAP (this plan's own threat register): a 100-pulse block emits far
 * more strobe/timing entries than the recorders' 512-entry caps, so these
 * LONG cases assert ONLY on loop_readback_reads (a uint16_t, uncapped),
 * response_code and the logged id -- deliberately NEVER on
 * strobe_overflowed() or timing_overflowed(), which WILL be nonzero here,
 * legitimately (the tail is dropped, the prefix stays valid, and none of
 * these cases reads the prefix).
 * ───────────────────────────────────────────────────────────────────────── */

void test_loop04_energy_cap_stops_at_exactly_100_pulses_at_500us(void) {
    firestarter_handle_t h = make_loop_handle(0x0B, 24, 2048, 500, LOOP_BUS_CONFIG_0x0B);
    const uint8_t block[1] = {0x00};
    loop_readback_seed(k0b(0), 0x00, 65535);
    drive_loop_write(&h, 0, block, 1);

    TEST_ASSERT_EQUAL_MESSAGE(RESPONSE_CODE_ERROR, h.response_code, "response_code");
    TEST_ASSERT_EQUAL_MESSAGE(101, loop_readback_reads(k0b(0)),
        "1 skip-check read + 100 verify reads (one per pulse) for a CORRECT 100-pulse cap at 500us; "
        "a byte that instead took 101 pulses (the off-by-one signature named below) would show 102");
    TEST_ASSERT_EQUAL_MESSAGE(1, count_logged_id(MSG_ERR_ENERGY_CAP), "exactly one MSG_ERR_ENERGY_CAP frame");
    TEST_ASSERT_EQUAL_MESSAGE(0, count_logged_id(MSG_ERR_MAX_PULSES), "MSG_ERR_MAX_PULSES must NOT be logged -- the energy cap binds first");

    int idx = find_logged_id(MSG_ERR_ENERGY_CAP);
    TEST_ASSERT_TRUE_MESSAGE(idx >= 0, "MSG_ERR_ENERGY_CAP frame must exist");
    TEST_ASSERT_EQUAL_MESSAGE(4, logged_id_param_count(idx), "payload is u24 address + u8 pulse count");
    TEST_ASSERT_EQUAL_HEX8_MESSAGE(0x00, logged_id_param(idx, 0), "address byte 0 (MSB)");
    TEST_ASSERT_EQUAL_HEX8_MESSAGE(0x00, logged_id_param(idx, 1), "address byte 1");
    TEST_ASSERT_EQUAL_HEX8_MESSAGE(0x00, logged_id_param(idx, 2), "address byte 2 (LSB)");
    TEST_ASSERT_EQUAL_MESSAGE(100, logged_id_param(idx, 3),
        "D-01's own worked example: 500us pulses against a 50000us cap must give EXACTLY 100 pulses "
        "(accumulated == i*500, tripping the >= energy_cap_us check at i == 100, accumulated == 50000 "
        "exactly, checked AFTER the pulse fires). 101 is the signature of implementing D-01's prose "
        "literally as \"if (accumulated + pulse > cap) { emit; break; }\" -- a look-ahead check BEFORE "
        "firing -- instead of the correct accumulate-then-check-after-firing shape this loop actually uses.");
}

void test_loop04_energy_cap_stops_at_exactly_50_pulses_at_1000us(void) {
    firestarter_handle_t h = make_loop_handle(0x0B, 24, 2048, 1000, LOOP_BUS_CONFIG_0x0B);
    const uint8_t block[1] = {0x00};
    loop_readback_seed(k0b(0), 0x00, 65535);
    drive_loop_write(&h, 0, block, 1);

    TEST_ASSERT_EQUAL_MESSAGE(RESPONSE_CODE_ERROR, h.response_code, "response_code");
    TEST_ASSERT_EQUAL_MESSAGE(51, loop_readback_reads(k0b(0)), "1 skip-check read + 50 verify reads (one per pulse)");
    TEST_ASSERT_EQUAL_MESSAGE(1, count_logged_id(MSG_ERR_ENERGY_CAP), "exactly one MSG_ERR_ENERGY_CAP frame");
    TEST_ASSERT_EQUAL_MESSAGE(0, count_logged_id(MSG_ERR_MAX_PULSES), "MSG_ERR_MAX_PULSES must NOT be logged -- the energy cap binds first");

    int idx = find_logged_id(MSG_ERR_ENERGY_CAP);
    TEST_ASSERT_TRUE_MESSAGE(idx >= 0, "MSG_ERR_ENERGY_CAP frame must exist");
    TEST_ASSERT_EQUAL_MESSAGE(50, logged_id_param(idx, 3), "1000us pulses against a 50000us cap must give exactly 50 pulses");
}

void test_loop04_energy_cap_stops_at_exactly_250_pulses_at_200us(void) {
    firestarter_handle_t h = make_loop_handle(0x0B, 24, 2048, 200, LOOP_BUS_CONFIG_0x0B);
    const uint8_t block[1] = {0x00};
    loop_readback_seed(k0b(0), 0x00, 65535);
    drive_loop_write(&h, 0, block, 1);

    TEST_ASSERT_EQUAL_MESSAGE(RESPONSE_CODE_ERROR, h.response_code, "response_code");
    /* Also the case that proves the uint16_t read counter was necessary:
     * a uint8_t counter would have wrapped at 256 (251 fits a uint8_t, but
     * a slightly wider block or an even smaller pulse width would not). */
    TEST_ASSERT_EQUAL_MESSAGE(251, loop_readback_reads(k0b(0)), "1 skip-check read + 250 verify reads (one per pulse)");
    TEST_ASSERT_EQUAL_MESSAGE(1, count_logged_id(MSG_ERR_ENERGY_CAP), "exactly one MSG_ERR_ENERGY_CAP frame");
    TEST_ASSERT_EQUAL_MESSAGE(0, count_logged_id(MSG_ERR_MAX_PULSES), "MSG_ERR_MAX_PULSES must NOT be logged -- the energy cap binds first");

    int idx = find_logged_id(MSG_ERR_ENERGY_CAP);
    TEST_ASSERT_TRUE_MESSAGE(idx >= 0, "MSG_ERR_ENERGY_CAP frame must exist");
    TEST_ASSERT_EQUAL_MESSAGE(250, logged_id_param(idx, 3), "200us pulses against a 50000us cap must give exactly 250 pulses");
}

void test_loop04_the_energy_cap_binds_before_max_pulses_on_every_shipped_width(void) {
    const uint32_t pulse_delays[3] = {500, 1000, 200};
    const uint8_t expected_pulses[3] = {100, 50, 250};
    for (int w = 0; w < 3; w++) {
        firestarter_handle_t h = make_loop_handle(0x0B, 24, 2048, pulse_delays[w], LOOP_BUS_CONFIG_0x0B);
        const uint8_t block[1] = {0x00};
        loop_readback_seed(k0b(0), 0x00, 65535);  /* re-seeds addr 0 in place, per host_stubs.cpp's own contract */
        drive_loop_write(&h, 0, block, 1);

        char rmsg[64];
        snprintf(rmsg, sizeof(rmsg), "response_code at width index %d", w);
        TEST_ASSERT_EQUAL_MESSAGE(RESPONSE_CODE_ERROR, h.response_code, rmsg);
        TEST_ASSERT_EQUAL_MESSAGE(1, count_logged_id(MSG_ERR_ENERGY_CAP), "MSG_ERR_ENERGY_CAP must be logged exactly once");
        /* max_pulses ships 255 on 0x0B; 250, 100 and 50 are all below it,
         * so if the energy cap did NOT bind first, this would be
         * MSG_ERR_MAX_PULSES instead -- the discriminating check D-04's
         * two distinct message ids exist to make possible. */
        TEST_ASSERT_EQUAL_MESSAGE(0, count_logged_id(MSG_ERR_MAX_PULSES), "MSG_ERR_MAX_PULSES must NEVER be logged on this row at this width");

        int idx = find_logged_id(MSG_ERR_ENERGY_CAP);
        TEST_ASSERT_TRUE_MESSAGE(idx >= 0, "MSG_ERR_ENERGY_CAP frame must exist");
        char pmsg[64];
        snprintf(pmsg, sizeof(pmsg), "pulse count payload at width index %d", w);
        TEST_ASSERT_EQUAL_MESSAGE(expected_pulses[w], logged_id_param(idx, 3), pmsg);
    }
}

void test_loop04_no_live_row_emits_an_overprogram_pulse(void) {
    /* All three shipped rows have overprogram_factor == 0
     * (eprom_params.cpp:50-52), so the overprogram path is structurally
     * unreachable through the table on any of them; the arithmetic itself
     * (eprom_overprogram_us) is proven separately by plan 141-08's
     * pure-function cases. This case proves the LOOP never emits a third,
     * extra pulse on any live row -- exactly the 2 pulses each seeded byte
     * needs, no more.
     *
     * loop_readback_reads() alone CANNOT prove this: an overprogram pulse
     * is a bare handle->firestarter_set_data() call with no verify read
     * after it (D-07's org_delay save/restore idiom, eprom.cpp:284-289),
     * so it would leave the read count completely unchanged whether it
     * fired or not. A raw STROBE_KIND_DATA COUNT is not a safe substitute
     * either: register-shift writes share the identical strobe shape as a
     * genuine chip-data pulse, and (measured directly, during this plan's
     * own execution) that noise does not even stay constant -- 0x08's
     * bus_config.rw_line makes every read<->write direction change force
     * a non-elided CONTROL rewrite, so a naive count SCALES with pulse
     * count rather than adding a fixed floor. count_data_pulses_with_value
     * (this file's own helper, see its comment above test 1) sidesteps
     * this entirely by filtering on the byte VALUE written, which a
     * register-shift can never coincidentally match for the addresses
     * used here. */
    {
        firestarter_handle_t h = make_loop_handle(0x07, 28, 65536, 100, LOOP_BUS_CONFIG_0x07);
        const uint8_t byte0[1] = {0x3C};
        loop_readback_seed(0, 0x3C, 2);
        drive_loop_write(&h, 0, byte0, 1);
        TEST_ASSERT_EQUAL_MESSAGE(2, count_data_pulses_with_value(0x3C), "0x07: exactly the 2 pulses the byte needed, no 3rd overprogram pulse");
    }
    {
        firestarter_handle_t h = make_loop_handle(0x08, 32, 262144, 100, LOOP_BUS_CONFIG_0x08);
        const uint8_t byte0[1] = {0x3C};
        loop_readback_seed(0, 0x3C, 2);
        drive_loop_write(&h, 0, byte0, 1);
        TEST_ASSERT_EQUAL_MESSAGE(2, count_data_pulses_with_value(0x3C), "0x08: exactly the 2 pulses the byte needed, no 3rd overprogram pulse");
    }
    {
        firestarter_handle_t h = make_loop_handle(0x0B, 24, 2048, 500, LOOP_BUS_CONFIG_0x0B);
        const uint8_t byte0[1] = {0x3C};
        loop_readback_seed(k0b(0), 0x3C, 2);
        drive_loop_write(&h, 0, byte0, 1);
        TEST_ASSERT_EQUAL_MESSAGE(2, count_data_pulses_with_value(0x3C), "0x0B: exactly the 2 pulses the byte needed, no 3rd overprogram pulse");
    }
}

void test_loop04_0x0B_runs_no_final_full_block_verify_pass(void) {
    /* 0x0B ships VERIFY_PER_PULSE (not VERIFY_PER_PULSE_PLUS_FINAL) -- no
     * final full-block pass runs. This is the negative counterpart to
     * LOOP-06's test_loop06_the_ff_rule_does_not_suppress_the_final_verify_pass
     * (0x07, WHICH does run one); together they prove verify_mode is read
     * from the table rather than hardcoded. */
    firestarter_handle_t h = make_loop_handle(0x0B, 24, 2048, 500, LOOP_BUS_CONFIG_0x0B);
    const uint8_t block[2] = {0x3C, 0x55};
    loop_readback_seed(k0b(0), 0x3C, 1);
    loop_readback_seed(k0b(1), 0x55, 1);
    drive_loop_write(&h, 0, block, 2);

    TEST_ASSERT_EQUAL_MESSAGE(RESPONSE_CODE_OK, h.response_code, "response_code");
    /* 2 reads per byte (1 skip-check + 1 verify after the single pulse) --
     * NOT 3, which is what a final full-block verify pass would add. */
    TEST_ASSERT_EQUAL_MESSAGE(2, loop_readback_reads(k0b(0)), "byte 0: skip-check + 1 verify, no final pass");
    TEST_ASSERT_EQUAL_MESSAGE(2, loop_readback_reads(k0b(1)), "byte 1: skip-check + 1 verify, no final pass");
}

/* ═════════════════════════════════════════════════════════════════════════
 * Plan 141-08 (LOOP-03, LOOP-05, LOOP-07, LOOP-08) -- the phase's remaining
 * four requirements, whose oracles are specialist: the overprogram
 * arithmetic (task 1, below -- a pure function, since no shipped row can
 * reach it), the hard-fail exit and its non-vacuous route disable (task 2),
 * the delay ceiling under a REAL drive plus the pre-flight refusal (task 2),
 * and the DIP32 A16-crossing seam (task 3). This plan flips NO requirement
 * checkbox -- consolidated in plan 141-09, after every piece of evidence
 * exists (frontmatter requirements: [] is deliberate).
 * ═════════════════════════════════════════════════════════════════════════ */

/* ─────────────────────────────────────────────────────────────────────────
 * Task 1 (LOOP-03, LOOP-07 arithmetic) -- the two pure functions, at their
 * boundaries. No handle, no hardware, no PROGMEM: eprom_overprogram_us and
 * mem_util_split_delay / mem_util_delay_us are called DIRECTLY.
 * ───────────────────────────────────────────────────────────────────────── */

void test_loop03_overprogram_duration_is_three_times_the_pulse_count_times_the_width(void) {
    TEST_ASSERT_EQUAL_MESSAGE(300, eprom_overprogram_us(1, 100, 3, 75000),
        "(1,100,3,75000): 1 pulse x 100us x factor 3 = 300");
    TEST_ASSERT_EQUAL_MESSAGE(1500, eprom_overprogram_us(5, 100, 3, 75000),
        "(5,100,3,75000): 5 pulses x 100us x factor 3 = 1500");
}

void test_loop03_overprogram_is_zero_when_the_factor_is_zero(void) {
    /* This is the gate every SHIPPED row takes: overprogram_factor is 0 on
     * all three live rows (eprom_params.cpp:50-52), so the per-byte loop's
     * own overprogram call (eprom.cpp:284) is inert on every protocol this
     * project ships today. D-08's pure function is the only oracle that
     * can exercise the path at a nonzero factor at all -- see the
     * remaining cases below. */
    TEST_ASSERT_EQUAL_MESSAGE(0, eprom_overprogram_us(5, 100, 0, 75000),
        "(5,100,0,75000): factor 0 -> 0, regardless of pulse_count/pulse_us/cap");
    TEST_ASSERT_EQUAL_MESSAGE(0, eprom_overprogram_us(25, 1000, 0, 75000),
        "(25,1000,0,75000): factor 0 -> 0 even at the max_pulses boundary");
}

void test_loop03_overprogram_clamps_at_the_cap_rather_than_refusing(void) {
    /* 25 x 1000 x 3 = 75000, exactly the cap -- the Intel-Intelligent worst
     * case cited on gh#15. Phase 140 D-08 / this plan's own <action>: the
     * cap CLAMPS, it does not refuse -- a request one microsecond ABOVE the
     * cap still clamps, it never becomes an error. */
    TEST_ASSERT_EQUAL_MESSAGE(75000, eprom_overprogram_us(25, 1000, 3, 75000),
        "(25,1000,3,75000): 25*1000*3=75000, exactly the cap -- the clamp is a no-op here");
    TEST_ASSERT_EQUAL_MESSAGE(75000, eprom_overprogram_us(25, 1001, 3, 75000),
        "(25,1001,3,75000): 25*1001*3=75075, ABOVE the cap -- clamps to 75000, never refuses");
}

void test_loop03_overprogram_is_32_bit_safe_at_the_uint16_ceiling(void) {
    /* The raw product 3 * 25 * 65535 = 4915125 fits uint32_t (max
     * 4294967295) but OVERFLOWS any uint16_t intermediate (max 65535): a
     * wrong intermediate type would show up here as a small or wrapped
     * value (4915125 mod 65536 = 44529), never as the correct clamp to the
     * cap. eprom_overprogram_us computes entirely in uint32_t
     * ((uint32_t)factor * pulse_count * pulse_us, per include/eprom.h's own
     * header comment). */
    TEST_ASSERT_EQUAL_MESSAGE(75000, eprom_overprogram_us(25, 65535, 3, 75000),
        "(25,65535,3,75000): raw product 3*25*65535=4915125, clamped to the 75000 cap");
}

void test_loop03_a_zero_cap_yields_no_overprogram_pulse(void) {
    /* Decided semantics (D-08, this plan's own <action>): eprom_params.h:52
     * defines the column as the clamp in min(3 x overprogram_factor x
     * pulse, cap), and min(product, 0) is 0 -- "0 means no clamp is
     * configured" is the fail-safe reading. The alternative reading ("0
     * means uncapped") would let a factor != 0 row emit a multi-second VPE
     * pulse the very first time one appeared -- this is the fail-safe
     * reading as well as the literal one. No shipped row has
     * overprogram_factor != 0, so this case is unreachable in production
     * and this pure-function test is its only oracle. */
    TEST_ASSERT_EQUAL_MESSAGE(0, eprom_overprogram_us(5, 100, 3, 0),
        "(5,100,3,0): cap_us=0 -> 0, the fail-safe 'no clamp configured' reading");
}

void test_loop07_split_does_not_fire_at_or_below_the_ceiling(void) {
    uint32_t ms; uint16_t us;

    mem_util_split_delay(0, &ms, &us);
    TEST_ASSERT_EQUAL_MESSAGE(0, ms, "split(0).ms");
    TEST_ASSERT_EQUAL_MESSAGE(0, us, "split(0).us");

    mem_util_split_delay(100, &ms, &us);
    TEST_ASSERT_EQUAL_MESSAGE(0, ms, "split(100).ms");
    TEST_ASSERT_EQUAL_MESSAGE(100, us, "split(100).us");

    /* The exact ceiling (16383) must NOT split -- splitting everything
     * would change the emitted trace for every shipped pulse width and
     * destroy Phase 144's ability to attribute the trace diff to cadence. */
    mem_util_split_delay(16383, &ms, &us);
    TEST_ASSERT_EQUAL_MESSAGE(0, ms, "split(16383).ms -- the exact ceiling must not split");
    TEST_ASSERT_EQUAL_MESSAGE(16383, us, "split(16383).us -- the exact ceiling must not split");
}

void test_loop07_split_fires_above_the_ceiling_and_stays_32_bit_safe(void) {
    uint32_t ms; uint16_t us;

    /* The first value that must split. */
    mem_util_split_delay(16384, &ms, &us);
    TEST_ASSERT_EQUAL_MESSAGE(16, ms, "split(16384).ms -- first value above the ceiling");
    TEST_ASSERT_EQUAL_MESSAGE(384, us, "split(16384).us -- first value above the ceiling");

    /* 0x0B's energy cap, as a single pulse. */
    mem_util_split_delay(50000, &ms, &us);
    TEST_ASSERT_EQUAL_MESSAGE(50, ms, "split(50000).ms");
    TEST_ASSERT_EQUAL_MESSAGE(0, us, "split(50000).us");

    /* The overprogram clamp. */
    mem_util_split_delay(75000, &ms, &us);
    TEST_ASSERT_EQUAL_MESSAGE(75, ms, "split(75000).ms");
    TEST_ASSERT_EQUAL_MESSAGE(0, us, "split(75000).us");

    /* minipro's own -o pulse= ceiling. */
    mem_util_split_delay(65535, &ms, &us);
    TEST_ASSERT_EQUAL_MESSAGE(65, ms, "split(65535).ms");
    TEST_ASSERT_EQUAL_MESSAGE(535, us, "split(65535).us");

    /* uint32_t max -- proving neither the division nor the modulo
     * overflows. 4294967295 / 1000 = 4294967, 4294967295 % 1000 = 295. */
    mem_util_split_delay(4294967295UL, &ms, &us);
    TEST_ASSERT_EQUAL_MESSAGE(4294967, ms, "split(4294967295).ms -- uint32_t max, division must not overflow");
    TEST_ASSERT_EQUAL_MESSAGE(295, us, "split(4294967295).us -- uint32_t max, modulo must not overflow");
}

void test_loop07_delay_us_emits_the_split_as_delay_then_delaymicroseconds(void) {
    clear_timings();
    mem_util_delay_us(75000);
    /* 75000 splits to ms=75, us=0 -- the remainder is 0, and
     * mem_util_delay_us guards delayMicroseconds on a NONZERO remainder, so
     * exactly one DELAY_MS entry (75) and NO DELAY_US entry at all. */
    TEST_ASSERT_EQUAL_MESSAGE(1, timing_count(), "mem_util_delay_us(75000): exactly one timing entry");
    TEST_ASSERT_EQUAL_MESSAGE(TIMING_KIND_DELAY_MS, timing_kind(0), "mem_util_delay_us(75000): entry 0 kind");
    TEST_ASSERT_EQUAL_MESSAGE(75, timing_us(0), "mem_util_delay_us(75000): entry 0 value");

    clear_timings();
    mem_util_delay_us(16384);
    /* 16384 splits to ms=16, us=384 -- both nonzero, so exactly TWO entries
     * in order: DELAY_MS(16) then DELAY_US(384). */
    TEST_ASSERT_EQUAL_MESSAGE(2, timing_count(), "mem_util_delay_us(16384): exactly two timing entries");
    TEST_ASSERT_EQUAL_MESSAGE(TIMING_KIND_DELAY_MS, timing_kind(0), "mem_util_delay_us(16384): entry 0 kind");
    TEST_ASSERT_EQUAL_MESSAGE(16, timing_us(0), "mem_util_delay_us(16384): entry 0 value");
    TEST_ASSERT_EQUAL_MESSAGE(TIMING_KIND_DELAY_US, timing_kind(1), "mem_util_delay_us(16384): entry 1 kind");
    TEST_ASSERT_EQUAL_MESSAGE(384, timing_us(1), "mem_util_delay_us(16384): entry 1 value");

    clear_timings();
    mem_util_delay_us(0);
    /* 0 splits to ms=0, us=0 -- both guards false, ZERO entries at all. */
    TEST_ASSERT_EQUAL_MESSAGE(0, timing_count(), "mem_util_delay_us(0): zero timing entries");
}

/* ─────────────────────────────────────────────────────────────────────────
 * Shared helpers for tasks 2/3 below -- the CONTROL-register write stream.
 *
 * Every non-elided CONTROL write (rurp_write_to_register(CONTROL_REGISTER,
 * ...), include/rurp_register_utils.h:24-59) shows up in the strobe
 * recorder as THREE consecutive entries via rurp_internal_write_to_register
 * (:63-89), in this FIXED, unconditional order, never interleaved with
 * anything else:
 *   [STROBE_KIND_DATA, pin=0,               value=<the physical byte>]
 *   [STROBE_KIND_PIN,  pin=CONTROL_REGISTER, value=1]  (latch rise)
 *   [STROBE_KIND_PIN,  pin=CONTROL_REGISTER, value=0]  (latch fall)
 * -- plan 141-07's own finding restated: STROBE_KIND_DATA is NOT a safe raw
 * pulse-count oracle, because a register-shift write pushes this exact same
 * DATA-strobe shape as a genuine chip-data pulse. These helpers exploit
 * that fixed 3-entry shape directly (locating the PIN-rise, then reading
 * the DATA entry immediately before it) instead of fighting it.
 * ───────────────────────────────────────────────────────────────────────── */
static int control_write_count(void) {
    int n = strobe_count();
    int c = 0;
    for (int i = 0; i < n; i++) {
        if (strobe_kind(i) == STROBE_KIND_PIN && strobe_pin(i) == CONTROL_REGISTER && strobe_value(i) == 1) c++;
    }
    return c;
}

static int control_write_strobe_index(int idx) {
    int n = strobe_count();
    int c = 0;
    for (int i = 0; i < n; i++) {
        if (strobe_kind(i) == STROBE_KIND_PIN && strobe_pin(i) == CONTROL_REGISTER && strobe_value(i) == 1) {
            if (c == idx) return i;
            c++;
        }
    }
    return -1;
}

/* The Nth (0-indexed) non-elided CONTROL_REGISTER write's PHYSICAL byte
 * value -- i.e. AFTER rurp_map_ctrl_reg_for_hardware_revision's per-
 * revision remap (rurp_hw_rev_utils.h), not the pre-remap LOGICAL value
 * mem_util_calculate_top_address_register computes. CTRL_VPP_REGULATOR_ENABLE
 * (0x80) is safe to check directly against this return value on EVERY
 * revision branch (both the REVISION_0/1 and REVISION_2_x remaps pass bit
 * 0x80 through unchanged). CTRL_ADDRESS_LINE_16 and CTRL_VPP_VPE_DROP_ENABLE,
 * however, COLLIDE onto the SAME physical bit (0x01) on the default test
 * revision (REVISION_0 -- host_stubs_common.inc's s_host_config is zero-
 * initialised; 141-RESEARCH.md's Axis 2 table) -- task 3's DIP32 cases
 * override the revision to REVISION_2_2, where they map to distinct
 * physical bits (0x20 / 0x01), specifically to avoid that collision. */
static int control_write_value(int idx) {
    int strobe_idx = control_write_strobe_index(idx);
    if (strobe_idx <= 0 || strobe_kind(strobe_idx - 1) != STROBE_KIND_DATA) return -1;
    return (int)strobe_value(strobe_idx - 1);
}

/* The stream index of the first GENUINE chip-data pulse -- the first
 * STROBE_KIND_DATA entry whose value matches one of the block's own byte
 * values, never a register-shift write's LSB/MSB/CONTROL byte (plan
 * 141-07's count_data_pulses_with_value finding, restated here for
 * ORDERING rather than counting). Every byte value this suite seeds
 * (0x0F/0x3C/0x55/0xAA and friends) is chosen so it can never collide with
 * an LSB/MSB address byte or a CONTROL bitmask these specific scenarios
 * ever produce. */
static int first_genuine_pulse_strobe_index(const uint8_t* values, int n_values) {
    int n = strobe_count();
    for (int i = 0; i < n; i++) {
        if (strobe_kind(i) != STROBE_KIND_DATA) continue;
        uint8_t v = strobe_value(i);
        for (int j = 0; j < n_values; j++) {
            if (values[j] == v) return i;
        }
    }
    return -1;
}

static int count_timing_ms(uint32_t val) {
    int n = timing_count();
    int c = 0;
    for (int i = 0; i < n; i++) {
        if (timing_kind(i) == TIMING_KIND_DELAY_MS && timing_us(i) == val) c++;
    }
    return c;
}

/* ─────────────────────────────────────────────────────────────────────────
 * Task 2 (LOOP-05 hard-fail + non-vacuous route disable; LOOP-07's GLOBAL
 * ceiling claim under a real drive, plus D-03's pre-flight refusal).
 * ───────────────────────────────────────────────────────────────────────── */

void test_loop05_a_byte_that_misses_within_max_pulses_aborts_the_block(void) {
    firestarter_handle_t h = make_loop_handle(0x07, 28, 65536, 100, LOOP_BUS_CONFIG_0x07);
    const uint8_t block[4] = {0x3C, 0x55, 0xAA, 0x0F};
    loop_readback_seed(0, block[0], 1);       /* converges after 1 pulse */
    loop_readback_seed(1, block[1], 65535);   /* NEVER converges within max_pulses (25) */
    loop_readback_seed(2, block[2], 1);       /* seeded, but must NEVER be reached */
    loop_readback_seed(3, block[3], 1);       /* seeded, but must NEVER be reached */
    drive_loop_write(&h, 0, block, 4);

    TEST_ASSERT_EQUAL_MESSAGE(RESPONSE_CODE_ERROR, h.response_code, "response_code");
    /* 1 skip-check read + 25 verify reads (one per pulse, all failing) --
     * budgets are checked only AFTER a failed verify, so byte 1 is read
     * exactly max_pulses+1 times before the loop gives up on it. */
    TEST_ASSERT_EQUAL_MESSAGE(26, loop_readback_reads(1), "1 skip-check + 25 verify reads (one per pulse) before MSG_ERR_MAX_PULSES");

    TEST_ASSERT_EQUAL_MESSAGE(1, count_logged_id(MSG_ERR_MAX_PULSES), "exactly one MSG_ERR_MAX_PULSES frame");
    TEST_ASSERT_EQUAL_MESSAGE(0, count_logged_id(MSG_ERR_ENERGY_CAP), "MSG_ERR_ENERGY_CAP must NOT be logged -- 0x07 ships energy_cap_us=0 (uncapped)");

    int idx = find_logged_id(MSG_ERR_MAX_PULSES);
    TEST_ASSERT_TRUE_MESSAGE(idx >= 0, "MSG_ERR_MAX_PULSES frame must exist");
    TEST_ASSERT_EQUAL_MESSAGE(4, logged_id_param_count(idx), "payload is u24 address + u8 pulse count");
    TEST_ASSERT_EQUAL_HEX8_MESSAGE(0x00, logged_id_param(idx, 0), "address byte 0 (MSB) -- base+1 == 1");
    TEST_ASSERT_EQUAL_HEX8_MESSAGE(0x00, logged_id_param(idx, 1), "address byte 1");
    TEST_ASSERT_EQUAL_HEX8_MESSAGE(0x01, logged_id_param(idx, 2), "address byte 2 (LSB) -- the failing byte's own address");
    TEST_ASSERT_EQUAL_MESSAGE(25, logged_id_param(idx, 3), "pulse count at the moment of failure -- max_pulses");

    /* The abort proof: the loop RETURNS on budget failure rather than
     * continuing to the next byte -- bytes 2 and 3 (seeded to converge
     * trivially, so a continuing loop WOULD have read them) both report
     * 0, meaning they were never read at all (loop_readback_reads() only
     * returns -1 for an address that was never SEEDED in the first place;
     * these two WERE seeded, so their untouched state reads back as their
     * own read_count of 0, not -1 -- see host_stubs.cpp's own contract). */
    TEST_ASSERT_EQUAL_MESSAGE(0, loop_readback_reads(2), "byte 2 (after the failing byte) must be UNTOUCHED -- the loop aborted the whole block");
    TEST_ASSERT_EQUAL_MESSAGE(0, loop_readback_reads(3), "byte 3 (after the failing byte) must be UNTOUCHED -- the loop aborted the whole block");
}

void test_loop05_the_loops_own_strobes_disable_the_high_voltage_route(void) {
    /* Phase 142 Plan 04 (K-1): widened to also assert the drop bit clears.
     * The REVISION_2_2 override is MANDATORY for that widening to be
     * decidable at all (L-6, copying the DIP32 cases' override idiom
     * below): on the DEFAULT REVISION_0 this case used to run on,
     * CTRL_VPP_VPE_DROP_ENABLE_REV1 (0x01) and CTRL_ADDRESS_LINE_16
     * collide onto the SAME physical bit, so a drop-bit assertion there
     * would be UNDECIDABLE, not merely weak. On REVISION_2_2 the drop bit
     * is CTRL_VPP_VPE_DROP_ENABLE_REV2 (0x01), distinct from
     * CTRL_ADDRESS_LINE_16_REV2 (0x20) -- this 28-pin, 4-byte, base-0 block
     * never crosses the A16 boundary, so the override changes nothing else
     * about this case's original claim. */
    rurp_get_config()->hardware_revision = REVISION_2_2;

    firestarter_handle_t h = make_loop_handle(0x07, 28, 65536, 100, LOOP_BUS_CONFIG_0x07);
    const uint8_t block[4] = {0x3C, 0x55, 0xAA, 0x0F};
    loop_readback_seed(0, block[0], 1);
    loop_readback_seed(1, block[1], 65535);
    loop_readback_seed(2, block[2], 1);
    loop_readback_seed(3, block[3], 1);
    drive_loop_write(&h, 0, block, 4);

    TEST_ASSERT_EQUAL_MESSAGE(RESPONSE_CODE_ERROR, h.response_code, "response_code (sanity, matches the case above)");

    /* VACUITY TRAP, named explicitly -- this is why this case exists rather
     * than driving the whole command: command_done() (src/firestarter.cpp:
     * 162-171) writes CONTROL_REGISTER = 0x00 on EVERY command exit,
     * unconditionally. An assertion driven through the whole command would
     * pass even if eprom_write_execute's own single-exit wrapper disabled
     * nothing at all, because command_done() would zero the register
     * anyway on the way out. drive_loop_write calls
     * firestarter_operation_main DIRECTLY (never the whole command, never
     * command_done()), so this assertion is scoped to eprom_write_execute's
     * OWN CONTROL strobes and is therefore meaningful. */
    int n = control_write_count();
    TEST_ASSERT_TRUE_MESSAGE(n >= 2, "non-vacuity: at least the top-of-block assert and the budget-failure disable must both have written CONTROL");

    int last = control_write_value(n - 1);
    TEST_ASSERT_TRUE_MESSAGE(last >= 0, "the last CONTROL write must be a genuine, decodable value");
    TEST_ASSERT_TRUE_MESSAGE((last & CTRL_VPP_REGULATOR_ENABLE) == 0,
        "the LAST control value emitted by operation_main must have CTRL_VPP_REGULATOR_ENABLE CLEAR -- eprom_write_execute's single-exit wrapper (Phase 142 Plan 04), via eprom_internal_report_budget_failure's EPROM_HV_ALL_OFF_MASK disable");
    TEST_ASSERT_TRUE_MESSAGE((last & CTRL_VPP_VPE_DROP_ENABLE_REV2) == 0,
        "the LAST control value emitted by operation_main must ALSO have CTRL_VPP_VPE_DROP_ENABLE_REV2 CLEAR -- the same EPROM_HV_ALL_OFF_MASK disable clears both bits together (Phase 142 Plan 04, K-1)");

    bool saw_earlier_regulator_set = false;
    bool saw_earlier_drop_set = false;
    for (int i = 0; i < n - 1; i++) {
        int v = control_write_value(i);
        if (v < 0) continue;
        if (v & CTRL_VPP_REGULATOR_ENABLE) { saw_earlier_regulator_set = true; }
        if (v & CTRL_VPP_VPE_DROP_ENABLE_REV2) { saw_earlier_drop_set = true; }
    }
    TEST_ASSERT_TRUE_MESSAGE(saw_earlier_regulator_set,
        "an EARLIER control value must have CTRL_VPP_REGULATOR_ENABLE SET -- otherwise the 'last value clear' assertion is vacuously true of a register that was never energised at all");
    TEST_ASSERT_TRUE_MESSAGE(saw_earlier_drop_set,
        "an EARLIER control value must have CTRL_VPP_VPE_DROP_ENABLE_REV2 SET too -- otherwise the new drop-bit clear-leg above is vacuously true of a bit that was never set in the first place (Phase 142 Plan 04, K-1)");
}

void test_loop05_a_successful_block_does_not_disable_the_route(void) {
    /* Paired negative control: a block that fully converges must leave the
     * route SET. Without this, the case above would pass on an
     * implementation that disables the route unconditionally on every
     * exit. Phase 142 Plan 04 (D-10 as amended, correction C-1, D-09) --
     * this assertion is WHY eprom_write_execute's single-exit wrapper
     * clears EPROM_HV_ALL_OFF_MASK only when response_code ==
     * RESPONSE_CODE_ERROR, never unconditionally: an unconditional clear
     * would re-arm the once-per-block guard and re-pay delay(500) on the
     * NEXT block too. This is the case that keeps that disable
     * conditional. */
    firestarter_handle_t h = make_loop_handle(0x07, 28, 65536, 100, LOOP_BUS_CONFIG_0x07);
    const uint8_t block[4] = {0x3C, 0x55, 0xAA, 0x0F};
    const uint16_t converge_after[4] = {1, 2, 3, 4};
    for (int i = 0; i < 4; i++) {
        loop_readback_seed((uint16_t)i, block[i], converge_after[i]);
    }
    drive_loop_write(&h, 0, block, 4);

    TEST_ASSERT_EQUAL_MESSAGE(RESPONSE_CODE_OK, h.response_code, "response_code -- the whole block converges");

    int n = control_write_count();
    TEST_ASSERT_TRUE_MESSAGE(n >= 1, "non-vacuity: at least the top-of-block assert must have written CONTROL");
    int last = control_write_value(n - 1);
    TEST_ASSERT_TRUE_MESSAGE(last >= 0, "the last CONTROL write must be a genuine, decodable value");
    TEST_ASSERT_TRUE_MESSAGE((last & CTRL_VPP_REGULATOR_ENABLE) != 0,
        "a SUCCESSFUL block must leave CTRL_VPP_REGULATOR_ENABLE SET -- nothing in this phase's scope disables it on the success path");
}

void test_loop07_no_recorded_us_delay_exceeds_the_avr_ceiling_under_a_real_drive(void) {
    /* protocol 0x07 ships energy_cap_us == 0 (uncapped), so D-03's
     * pre-flight refusal does not fire even at a wildly over-ceiling
     * pulse_delay -- exactly the scenario LOOP-07's GLOBAL claim ("no call
     * path can reach delayMicroseconds() above 16383us") must hold under.
     * 50000 is a value the wire can supply TODAY through json_parser.c's
     * unclamped extract_long("pulse-delay", ...) (json_parser.c ~:305). */
    firestarter_handle_t h = make_loop_handle(0x07, 28, 65536, 50000, LOOP_BUS_CONFIG_0x07);
    const uint8_t block[1] = {0x3C};
    loop_readback_seed(0, block[0], 2);  /* small: 2 pulses, neither recorder overflows */
    drive_loop_write(&h, 0, block, 1);

    TEST_ASSERT_EQUAL_MESSAGE(RESPONSE_CODE_OK, h.response_code, "response_code");
    TEST_ASSERT_EQUAL_MESSAGE(0, timing_overflowed(), "timing_overflowed -- small drive, must be sound");

    TEST_ASSERT_TRUE_MESSAGE(timing_count() > 0, "non-vacuity: the drive must have recorded at least one timing entry");

    int n = timing_count();
    for (int i = 0; i < n; i++) {
        if (timing_kind(i) != TIMING_KIND_DELAY_US) continue;
        uint32_t us = timing_us(i);
        char msg[112];
        snprintf(msg, sizeof(msg), "timing entry %d (delayMicroseconds) has value %lu -- must be <= 16383 (the AVR delayMicroseconds() accurate ceiling)", i, (unsigned long)us);
        TEST_ASSERT_TRUE_MESSAGE(us <= 16383UL, msg);
    }

    /* ArduinoFake declares delayMicroseconds(unsigned int), which is
     * 32-BIT on this host -- an over-ceiling value would arrive INTACT and
     * VISIBLE here rather than being silently truncated the way AVR's own
     * 16-bit unsigned int truncates it at cores/arduino/wiring.c's
     * `us <<= 2` step. The oracle above is therefore real, not accidental:
     * a raw, unsplit delayMicroseconds(50000) call WOULD show up as
     * exactly that value, 50000, failing the loop above immediately --
     * confirmed by planting exactly that violation (see this plan's
     * SUMMARY for the captured RED transcript). */
    TEST_ASSERT_TRUE_MESSAGE(count_timing_ms(50) >= 2,
        "at least two DELAY_MS(50) entries -- one per pulse, proving mem_util_delay_us's split actually fired (50000 -> ms=50, us=0) rather than the pulse being silently skipped");
}

void test_loop07_an_over_cap_pulse_is_refused_before_any_high_voltage_on_a_capped_row(void) {
    /* D-03's pre-flight refusal, at the row where it is actually reachable
     * (0x0B ships energy_cap_us = 50000; 0x07/0x08 ship 0 == uncapped, so
     * this refusal is structurally unreachable on either of them). */
    firestarter_handle_t h = make_loop_handle(0x0B, 24, 2048, 60000, LOOP_BUS_CONFIG_0x0B);
    configure_memory(&h);

    TEST_ASSERT_EQUAL_MESSAGE(RESPONSE_CODE_ERROR, h.response_code, "response_code -- 60000 > the 50000us energy cap");
    int idx = find_logged_id(MSG_ERR_PULSE_TOO_WIDE);
    TEST_ASSERT_TRUE_MESSAGE(idx >= 0, "MSG_ERR_PULSE_TOO_WIDE frame must exist -- non-vacuity");
    TEST_ASSERT_EQUAL_MESSAGE(4, logged_id_param_count(idx), "payload is a u32 (the requested pulse_delay)");
    TEST_ASSERT_EQUAL_HEX8_MESSAGE(0x00, logged_id_param(idx, 0), "u32 byte 0 (MSB) of 60000 (0x0000EA60)");
    TEST_ASSERT_EQUAL_HEX8_MESSAGE(0x00, logged_id_param(idx, 1), "u32 byte 1 of 60000");
    TEST_ASSERT_EQUAL_HEX8_MESSAGE(0xEA, logged_id_param(idx, 2), "u32 byte 2 of 60000");
    TEST_ASSERT_EQUAL_HEX8_MESSAGE(0x60, logged_id_param(idx, 3), "u32 byte 3 (LSB) of 60000");

    /* The pre-flight proof: NO control-register write anywhere in the
     * stream carries CTRL_VPP_REGULATOR_ENABLE -- the refusal happens
     * before any high voltage is ever enabled. */
    int n = control_write_count();
    for (int i = 0; i < n; i++) {
        int v = control_write_value(i);
        char msg[80];
        snprintf(msg, sizeof(msg), "control write %d (0x%02X) must not carry CTRL_VPP_REGULATOR_ENABLE -- refused pre-flight", i, v);
        TEST_ASSERT_TRUE_MESSAGE(v < 0 || (v & CTRL_VPP_REGULATOR_ENABLE) == 0, msg);
    }

    /* Paired passing control at a legal width, same protocol. Clear the
     * logged-id capture first: it is a single array shared for the whole
     * test case (setUp() clears it once per CASE, not once per
     * configure_memory call), and the refusal above legitimately logged
     * one MSG_ERR_PULSE_TOO_WIDE frame that must not leak into this
     * second, independent drive's own count. */
    clear_logged_ids();
    clear_strobes();
    firestarter_handle_t h2 = make_loop_handle(0x0B, 24, 2048, 500, LOOP_BUS_CONFIG_0x0B);
    configure_memory(&h2);
    TEST_ASSERT_EQUAL_MESSAGE(RESPONSE_CODE_OK, h2.response_code, "response_code -- 500us is well under the 50000us cap");
    TEST_ASSERT_EQUAL_MESSAGE(0, count_logged_id(MSG_ERR_PULSE_TOO_WIDE), "no MSG_ERR_PULSE_TOO_WIDE at a legal pulse width");
}

/* ─────────────────────────────────────────────────────────────────────────
 * Task 3 (LOOP-08) -- VPE once per block, surviving every verify read,
 * across an A16 crossing on a 32-pin part. All six cases assert
 * strobe_overflowed() == 0 as a soundness precondition (small blocks only).
 * ───────────────────────────────────────────────────────────────────────── */

void test_loop08_the_route_is_asserted_once_before_the_first_data_strobe(void) {
    firestarter_handle_t h = make_loop_handle(0x07, 28, 65536, 100, LOOP_BUS_CONFIG_0x07);
    const uint8_t block[4] = {0x3C, 0x55, 0xAA, 0x0F};
    const uint16_t converge_after[4] = {1, 2, 3, 4};
    for (int i = 0; i < 4; i++) {
        loop_readback_seed((uint16_t)i, block[i], converge_after[i]);
    }
    drive_loop_write(&h, 0, block, 4);

    TEST_ASSERT_EQUAL_MESSAGE(RESPONSE_CODE_OK, h.response_code, "response_code");
    TEST_ASSERT_EQUAL_MESSAGE(0, strobe_overflowed(), "strobe_overflowed -- small block, must be sound");
    TEST_ASSERT_EQUAL_MESSAGE(0, timing_overflowed(), "timing_overflowed -- small block, must be sound");

    int first_pulse_idx = first_genuine_pulse_strobe_index(block, 4);
    TEST_ASSERT_TRUE_MESSAGE(first_pulse_idx >= 0, "non-vacuity: a genuine chip-data pulse must have been recorded");

    /* Exactly one clear-to-set transition of CTRL_VPP_REGULATOR_ENABLE --
     * the once-per-block assert, never re-asserted per byte. */
    int n = control_write_count();
    TEST_ASSERT_TRUE_MESSAGE(n > 0, "non-vacuity: at least the top-of-block assert must have written CONTROL");
    bool prev_set = false;
    int transitions = 0;
    int transition_idx = -1;
    for (int i = 0; i < n; i++) {
        int v = control_write_value(i);
        bool now_set = (v >= 0) && (v & CTRL_VPP_REGULATOR_ENABLE);
        if (now_set && !prev_set) { transitions++; transition_idx = i; }
        prev_set = now_set;
    }
    TEST_ASSERT_EQUAL_MESSAGE(1, transitions, "exactly one clear-to-set transition of CTRL_VPP_REGULATOR_ENABLE across the whole block");

    int assert_strobe_idx = control_write_strobe_index(transition_idx);
    char ordmsg[112];
    snprintf(ordmsg, sizeof(ordmsg), "the route assert (stream index %d) must precede the first genuine data pulse (stream index %d)", assert_strobe_idx, first_pulse_idx);
    TEST_ASSERT_TRUE_MESSAGE(assert_strobe_idx < first_pulse_idx, ordmsg);

    /* Exactly one delay(500) settle, and it too precedes the first pulse --
     * the settle stays amortised once per block, which is the whole point
     * of this requirement. timing_after_strobe(i) records how many
     * strobes existed at push time, so <= first_pulse_idx means the delay
     * happened no later than immediately before that strobe. */
    TEST_ASSERT_EQUAL_MESSAGE(1, count_timing_ms(500), "exactly one delay(500) settle across the whole block");
    int m = timing_count();
    bool found_settle_before = false;
    for (int i = 0; i < m; i++) {
        if (timing_kind(i) == TIMING_KIND_DELAY_MS && timing_us(i) == 500UL && timing_after_strobe(i) <= first_pulse_idx) {
            found_settle_before = true;
        }
    }
    TEST_ASSERT_TRUE_MESSAGE(found_settle_before, "the delay(500) settle must precede the first genuine data pulse");
}

void test_loop08_the_route_bit_is_present_in_every_control_value_across_the_block(void) {
    /* Deliberately never claims the CONTROL register is written only once
     * across the whole block: mem_util_set_address writes CONTROL
     * unconditionally on every byte, for both the pulse and the verify
     * (memory.cpp:230-231), and this holds because the route bit is in
     * mem_util_calculate_top_address_register's UNCONDITIONAL preserve
     * mask (memory.cpp:161) -- NOT because a verify read leaves the
     * control register alone. */
    firestarter_handle_t h = make_loop_handle(0x07, 28, 65536, 100, LOOP_BUS_CONFIG_0x07);
    const uint8_t block[4] = {0x3C, 0x55, 0xAA, 0x0F};
    const uint16_t converge_after[4] = {1, 2, 3, 4};
    for (int i = 0; i < 4; i++) {
        loop_readback_seed((uint16_t)i, block[i], converge_after[i]);
    }
    drive_loop_write(&h, 0, block, 4);

    TEST_ASSERT_EQUAL_MESSAGE(RESPONSE_CODE_OK, h.response_code, "response_code");
    TEST_ASSERT_EQUAL_MESSAGE(0, strobe_overflowed(), "strobe_overflowed -- small block, must be sound");
    int n = control_write_count();
    TEST_ASSERT_TRUE_MESSAGE(n > 1, "non-vacuity: multiple CONTROL writes must have occurred across the block (the assert plus at least one per-byte address-set)");
    for (int i = 0; i < n; i++) {
        int v = control_write_value(i);
        char msg[80];
        snprintf(msg, sizeof(msg), "control write %d (0x%02X) must carry CTRL_VPP_REGULATOR_ENABLE", i, v);
        TEST_ASSERT_TRUE_MESSAGE(v >= 0 && (v & CTRL_VPP_REGULATOR_ENABLE) != 0, msg);
    }
}

void test_loop08_route_presence_is_not_vacuous(void) {
    /* Negative control for the case above: drive through
     * mem_util_blank_check (CMD_BLANK_CHECK's own operation_main, installed
     * by configure_eprom's own cmd-keyed switch when handle->cmd is set
     * BEFORE configure_memory runs) instead of eprom_write_execute.
     * blank_check reads via memory_get_data -> mem_util_set_address,
     * producing a genuine, non-elided CONTROL write (pins==28
     * unconditionally ORs CTRL_ADDRESS_LINE_17 into the very first address
     * write, so even address 0 differs from the reset baseline), but NEVER
     * asserts CTRL_VPP_REGULATOR_ENABLE -- that assert belongs to
     * eprom_write_execute alone, entered only via CMD_WRITE. Without this
     * case, the case above's 'for every control value, the bit is set'
     * could pass vacuously on an empty or mis-keyed stream; this shows the
     * identical filter, applied to a stream that genuinely contains
     * CONTROL writes, correctly reports the bit ABSENT throughout. */
    firestarter_handle_t h = make_loop_handle(0x07, 28, 65536, 100, LOOP_BUS_CONFIG_0x07);
    h.cmd = CMD_BLANK_CHECK;
    const uint8_t block[1] = {0x3C};
    loop_readback_seed(0, block[0], 0);  /* mismatch on the very first (only) read -- stops the scan immediately */
    drive_loop_write(&h, 0, block, 1);

    TEST_ASSERT_EQUAL_MESSAGE(RESPONSE_CODE_ERROR, h.response_code, "response_code -- blank_check reports non-blank at address 0");
    TEST_ASSERT_EQUAL_MESSAGE(0, strobe_overflowed(), "strobe_overflowed -- tiny drive, must be sound");
    int n = control_write_count();
    TEST_ASSERT_TRUE_MESSAGE(n > 0, "non-vacuity: mem_util_blank_check's own set_address call must have produced a genuine CONTROL write");
    for (int i = 0; i < n; i++) {
        int v = control_write_value(i);
        char msg[80];
        snprintf(msg, sizeof(msg), "control write %d (0x%02X) must NOT carry CTRL_VPP_REGULATOR_ENABLE -- no route was ever asserted", i, v);
        TEST_ASSERT_TRUE_MESSAGE(v >= 0 && (v & CTRL_VPP_REGULATOR_ENABLE) == 0, msg);
    }
}

void test_loop08_dip32_block_crossing_an_a16_boundary_keeps_the_route_and_toggles_a16(void) {
    /* The highest-risk case in this plan. Override the hardware-revision
     * mapping to REVISION_2_2 for the duration of this case (reset
     * unconditionally in tearDown()) so the recorded PHYSICAL control byte
     * does not conflate CTRL_ADDRESS_LINE_16 and CTRL_VPP_VPE_DROP_ENABLE
     * -- on the default REVISION_0/1 mapping both remap onto the SAME
     * physical bit (0x01; 141-RESEARCH.md's Axis 2 table), which would make
     * an A16-toggle check indistinguishable from a drop-bit-toggle check.
     * On REVISION_2_x they map to distinct physical bits:
     * CTRL_ADDRESS_LINE_16_REV2 (0x20) vs CTRL_VPP_VPE_DROP_ENABLE_REV2
     * (0x01). This changes nothing about the LOGICAL behaviour under test
     * (every eprom.cpp/memory.cpp bit check operates on the pre-remap
     * logical value; only the recorded strobe BYTE differs) -- it only
     * disambiguates what THIS test can prove from the strobe stream. */
    rurp_get_config()->hardware_revision = REVISION_2_2;

    firestarter_handle_t h = make_loop_handle(0x08, 32, 262144, 100, LOOP_BUS_CONFIG_0x08);
    /* LOOP_BUS_CONFIG_0x08 has matching_lines 17 and static_high_mask 0, so
     * bits 0-16 of the address are identity-mapped by
     * mem_util_remap_address_bus and A16 rides in the CONTROL top-address
     * register (mem_util_calculate_top_address_register), never in the
     * LSB/MSB latches -- exactly why host_stubs.cpp's read-back model keys
     * on the full 16-bit (LSB | MSB<<8) pair rather than the trace suite's
     * '& 0x03' index, which would collapse all four of this block's
     * addresses onto two counters. */
    const uint32_t base = 0x00FFFEUL;
    const uint8_t block[4] = {0x3C, 0x55, 0xAA, 0x0F};  /* none is 0xFF -- every byte is genuinely programmed */
    const uint16_t keys[4] = {0xFFFE, 0xFFFF, 0x0000, 0x0001};
    for (int i = 0; i < 4; i++) {
        loop_readback_seed(keys[i], block[i], 1);
    }
    drive_loop_write(&h, base, block, 4);

    TEST_ASSERT_EQUAL_MESSAGE(RESPONSE_CODE_OK, h.response_code, "response_code");
    TEST_ASSERT_EQUAL_MESSAGE(0, strobe_overflowed(), "strobe_overflowed -- small block, must be sound");

    /* 0x08 ships VERIFY_PER_PULSE_PLUS_FINAL (eprom_params.cpp:50): 1
     * skip-check + 1 verify (converge_after=1) + 1 final-pass read = 3,
     * matching LOOP-01's established 2+pulses mapping. */
    for (int i = 0; i < 4; i++) {
        char msg[80];
        snprintf(msg, sizeof(msg), "loop_readback_reads(key[%d]=0x%04X) == 3 (skip-check + 1 verify + 1 final pass)", i, keys[i]);
        TEST_ASSERT_EQUAL_MESSAGE(3, loop_readback_reads(keys[i]), msg);
    }

    int n = control_write_count();
    TEST_ASSERT_TRUE_MESSAGE(n > 0, "non-vacuity: the block must have produced at least one CONTROL write");

    bool saw_a16_clear = false, saw_a16_set = false;
    for (int i = 0; i < n; i++) {
        int v = control_write_value(i);
        char vmsg[64];
        snprintf(vmsg, sizeof(vmsg), "control write %d must be a genuine, decodable value", i);
        TEST_ASSERT_TRUE_MESSAGE(v >= 0, vmsg);
        if (v & CTRL_ADDRESS_LINE_16_REV2) saw_a16_set = true; else saw_a16_clear = true;
        char rmsg[80];
        snprintf(rmsg, sizeof(rmsg), "control write %d (0x%02X) must carry CTRL_VPP_REGULATOR_ENABLE", i, v);
        TEST_ASSERT_TRUE_MESSAGE((v & CTRL_VPP_REGULATOR_ENABLE) != 0, rmsg);
    }
    TEST_ASSERT_TRUE_MESSAGE(saw_a16_clear, "at least one control value must have A16 CLEAR (the 0x00FFFE/0x00FFFF half of the block)");
    TEST_ASSERT_TRUE_MESSAGE(saw_a16_set, "at least one control value must have A16 SET (the 0x010000/0x010001 half) -- proves the block really crossed the boundary");
}

void test_vpp01_dip32_drop_bit_survives_the_block_on_rev2_class(void) {
    /* Same handle shape as the case above -- same override reasoning. */
    rurp_get_config()->hardware_revision = REVISION_2_2;

    firestarter_handle_t h = make_loop_handle(0x08, 32, 262144, 100, LOOP_BUS_CONFIG_0x08);
    const uint32_t base = 0x00FFFEUL;
    const uint8_t block[4] = {0x3C, 0x55, 0xAA, 0x0F};
    const uint16_t keys[4] = {0xFFFE, 0xFFFF, 0x0000, 0x0001};
    for (int i = 0; i < 4; i++) {
        loop_readback_seed(keys[i], block[i], 1);
    }
    drive_loop_write(&h, base, block, 4);

    TEST_ASSERT_EQUAL_MESSAGE(RESPONSE_CODE_OK, h.response_code, "response_code");
    TEST_ASSERT_EQUAL_MESSAGE(0, strobe_overflowed(), "strobe_overflowed -- small block, must be sound");

    int n = control_write_count();
    TEST_ASSERT_TRUE_MESSAGE(n >= 2, "non-vacuity: at least the top-of-block assert (drop SET) and the block's first set_address must both have written CONTROL");

    int first_pulse_idx = first_genuine_pulse_strobe_index(block, 4);
    TEST_ASSERT_TRUE_MESSAGE(first_pulse_idx >= 0, "non-vacuity: a genuine chip-data pulse must have been recorded");

    /* [D-01/D-02/D-04 finding, in full -- supersedes the pre-Phase-142
     * "D-09 finding" this comment used to carry, which asserted the
     * OPPOSITE outcome]. Plan 142-02 revision-gated
     * mem_util_calculate_top_address_register's preserve mask so
     * CTRL_VPP_VPE_DROP_ENABLE now SURVIVES this block's every
     * set_address() on Rev 2-class hardware (D-01/D-02) -- the inverse of
     * what this case asserted before Phase 142. Plan 142-04 (this plan)
     * then removed eprom_write_execute's explicit pins>=32 clear (D-04),
     * which is what makes that survival OBSERVABLE in the strobe stream at
     * all: with the clear gone, nothing in the write path ever re-clears
     * the bit the top-of-block assert set below.
     *
     * The drop bit is a VPP LEVEL selector (VPE dropped through the
     * resistor to the ~13V VPP level), never a route: pin-1 VPP routing on
     * a 32-pin part is a separate, PHYSICAL decision made with a jumper --
     * this file names no jumper designator and asserts no net
     * (doc/SHIELD-REVISIONS.md and .planning/v1.7-SHIELD-REVS.md document
     * that jumper's identity two contradictory ways, an open finding, not
     * resolved here).
     *
     * This case is Rev-2-class ONLY --
     * test_loop08_the_28_pin_row_keeps_its_drop_bit is its unaffected
     * 28-pin partner (pins < 32 was never gated on revision). Like every
     * other claim in this suite, this is a claim about the EMITTED
     * CONTROL-REGISTER STREAM only, never about silicon (D-03). */
    int v0 = control_write_value(0);
    TEST_ASSERT_TRUE_MESSAGE(v0 >= 0 && (v0 & CTRL_VPP_VPE_DROP_ENABLE_REV2) != 0,
        "control write 0 (the top-of-block assert) must have the drop bit SET -- the 0x08 row's ELSE branch asserts regulator|drop together");

    /* INVERTED (Phase 142 Plan 04, K-3): the positive claim replacing the
     * old "write 1 clears it" assertion -- every control value across the
     * WHOLE block, including across the A16 crossing this block
     * deliberately drives through, must carry the drop bit. */
    for (int i = 0; i < n; i++) {
        int v = control_write_value(i);
        char msg[128];
        snprintf(msg, sizeof(msg), "control write %d (0x%02X) must carry CTRL_VPP_VPE_DROP_ENABLE_REV2 -- plan 142-02's revision-gated preserve mask keeps it across every set_address on Rev 2-class hardware", i, v);
        TEST_ASSERT_TRUE_MESSAGE(v >= 0 && (v & CTRL_VPP_VPE_DROP_ENABLE_REV2) != 0, msg);
    }
}

void test_loop08_the_28_pin_row_keeps_its_drop_bit(void) {
    /* Paired control for the case above: on a 28-pin row (pins < 32), the
     * drop bit IS in the preserve mask (memory.cpp:172), so it must
     * survive every set_address() of the block. Stays on the DEFAULT
     * hardware revision (REVISION_0) -- this block is 4 bytes at base 0,
     * so address never reaches 0x010000 and A16 never becomes 1, meaning
     * physical bit 0x01 (CTRL_VPP_VPE_DROP_ENABLE_REV1, which collides with
     * CTRL_ADDRESS_LINE_16 on REVISION_0/1 per 141-RESEARCH.md's Axis 2
     * table) can ONLY ever mean the drop bit here -- no REV2 override
     * needed for this case's own claim. Without this case, the case above
     * would pass on an implementation that never sets the drop bit for ANY
     * protocol, DIP32 or not. */
    firestarter_handle_t h = make_loop_handle(0x07, 28, 65536, 100, LOOP_BUS_CONFIG_0x07);
    const uint8_t block[4] = {0x3C, 0x55, 0xAA, 0x0F};
    const uint16_t converge_after[4] = {1, 2, 3, 4};
    for (int i = 0; i < 4; i++) {
        loop_readback_seed((uint16_t)i, block[i], converge_after[i]);
    }
    drive_loop_write(&h, 0, block, 4);

    TEST_ASSERT_EQUAL_MESSAGE(RESPONSE_CODE_OK, h.response_code, "response_code");
    TEST_ASSERT_EQUAL_MESSAGE(0, strobe_overflowed(), "strobe_overflowed -- small block, must be sound");
    int n = control_write_count();
    TEST_ASSERT_TRUE_MESSAGE(n > 0, "non-vacuity: the block must have produced at least one CONTROL write");
    for (int i = 0; i < n; i++) {
        int v = control_write_value(i);
        char msg[80];
        snprintf(msg, sizeof(msg), "control write %d (0x%02X) must carry CTRL_VPP_VPE_DROP_ENABLE_REV1 -- pins<32 keeps it in the preserve mask", i, v);
        TEST_ASSERT_TRUE_MESSAGE(v >= 0 && (v & CTRL_VPP_VPE_DROP_ENABLE_REV1) != 0, msg);
    }
}

/* ═════════════════════════════════════════════════════════════════════════
 * Phase 143 Plan 01 / HOST-01 (firmware half) / BF-3 -- six pure-arithmetic
 * cases proving the corrected per-block worst-case write-time budget
 * (include/eprom_budget.h, src/proms/eprom_budget.cpp). Every case below
 * calls eprom_worst_pulses / eprom_per_byte_budget_us / eprom_block_budget_s
 * directly -- none drives eprom_write_execute, make_loop_handle or
 * drive_loop_write, so none of this plan's own cases touches the per-byte
 * loop itself. This plan flips NO requirement checkbox (frontmatter
 * requirements: [] is deliberate); it contributes the firmware half of
 * HOST-01 only -- plan 143-10 flips the HOST-* checkboxes after every piece
 * of evidence exists.
 * ═════════════════════════════════════════════════════════════════════════ */

/* Case 1: energy_cap_us == 0 means UNCAPPED, not "cap at zero". Both 0x07
 * and 0x08 ship energy_cap_us == 0 (eprom_params.cpp:50-51) -- an unguarded
 * min() would clamp every one of their bytes' pulse budget to zero. */
void test_budget_uncapped_energy_cap_is_not_a_cap_at_zero(void) {
    TEST_ASSERT_EQUAL_UINT32_MESSAGE(25, eprom_worst_pulses(25, 1000, 0),
        "energy_cap_us == 0 means UNCAPPED (0x07/0x08 both ship it) -- an unguarded min() "
        "would clamp every one of their bytes to zero instead of returning max_pulses");
    TEST_ASSERT_EQUAL_UINT32_MESSAGE(25000, eprom_per_byte_budget_us(25, 1000, 0, 0, 75000),
        "per-byte budget under UNCAPPED energy must be max_pulses * pulse_us (25 * 1000), "
        "not zero");
}

/* Case 2: the pulse count CEILS, because the shipped loop
 * (src/proms/eprom.cpp's inner for(;;)) increments accumulated BEFORE
 * testing it against energy_cap_us -- BF-3. min(max_pulses * pulse_us, cap)
 * would yield 1 for the first assertion below (50000 / 49999, truncated),
 * not the true 2. */
void test_budget_pulse_count_ceils_because_the_loop_tests_after_it_increments(void) {
    TEST_ASSERT_EQUAL_UINT32_MESSAGE(2, eprom_worst_pulses(255, 49999, 50000),
        "BF-3: ceil(50000/49999) == 2 -- the naive min(max_pulses*pulse, cap) reading "
        "would yield 1, because the loop increments accumulated before testing it");
    TEST_ASSERT_EQUAL_UINT32_MESSAGE(250, eprom_worst_pulses(255, 200, 50000),
        "BF-3: ceil(50000/200) == 250 -- divides evenly, sanity-checks the shipped 0x0B width");
    TEST_ASSERT_EQUAL_UINT32_MESSAGE(167, eprom_worst_pulses(255, 300, 50000),
        "BF-3: ceil(50000/300) == 167, not floor's 166 -- a non-dividing width must round UP");
    TEST_ASSERT_EQUAL_UINT32_MESSAGE(1, eprom_worst_pulses(255, 50000, 50000),
        "BF-3: ceil(50000/50000) == 1 -- a single pulse already meets the cap exactly");
    TEST_ASSERT_EQUAL_UINT32_MESSAGE(255, eprom_worst_pulses(255, 1, 50000),
        "BF-3: ceil(50000/1) == 50000, clamped down to max_pulses (255) -- the max_pulses "
        "ceiling still binds when the energy cap alone would allow far more pulses");
}

/* Case 3: the BF-3 headline number. firestarter/CLAUDE.md's "Algorithm
 * Handlers" 0x0B row independently derives the same 99998 us figure
 * (F-141-10) -- the naive 50000 us reading would time out a WORKING write
 * at ~51 s (D-09: a budget that is too tight is strictly worse than a
 * generous one, because it fails real silicon that was never broken). */
void test_budget_0x0b_at_49999us_is_99998us_per_byte_not_50000(void) {
    TEST_ASSERT_EQUAL_UINT32_MESSAGE(99998, eprom_per_byte_budget_us(255, 49999, 50000, 0, 75000),
        "0x0B @ --pulse-us 49999 is 99998 us/byte (two pulses), not the naive 50000 -- "
        "firestarter/CLAUDE.md's 0x0B row derives the same figure independently (F-141-10); "
        "a 50000 us budget would time out a WORKING write at ~51 s (D-09)");
}

/* Case 4: the overprogram term. All three shipped rows carry
 * overprogram_factor == 0, so the factor-0 assertion alone can never
 * distinguish "calls eprom_overprogram_us" from "always returns 0" --
 * the factor-3 assertions are the ONLY reachable proof the term is wired
 * at all. A literal `3 * overprogram_factor * pulse_us` restatement (the
 * reading D-11 and eprom_params.h's own column comment both suggest) would
 * yield 3*3*1000=9000 for the middle case below, not the shipped function's
 * 75000 -- an 8.3x under-estimate. */
void test_budget_overprogram_term_is_zero_for_factor_zero_and_clamped_for_factor_three(void) {
    TEST_ASSERT_EQUAL_UINT32_MESSAGE(25000, eprom_per_byte_budget_us(25, 1000, 0, 0, 75000),
        "factor 0 (every shipped row): overprogram term is 0, total is pulse-only 25*1000");
    TEST_ASSERT_EQUAL_UINT32_MESSAGE(100000, eprom_per_byte_budget_us(25, 1000, 0, 3, 75000),
        "factor 3, cap 75000: overprogram term must come from CALLING eprom_overprogram_us "
        "(25*1000 pulse + 75000 overprogram) -- a literal 3*factor*pulse restatement would "
        "yield 25000+9000=34000, not 100000, an 8.3x under-estimate on the overprogram term");
    TEST_ASSERT_EQUAL_UINT32_MESSAGE(35000, eprom_per_byte_budget_us(25, 1000, 0, 3, 10000),
        "factor 3, cap 10000: the overprogram term clamps at the cap (10000), giving "
        "25000+10000=35000 -- proves the clamp is honoured, not just the raw product");
}

/* Case 5: pulse_us == 0 never divides by zero. This is a GUARD, not the
 * live path: configure_eprom's own pulse-fallback switch (eprom.cpp:68-75)
 * has already resolved a zero pulse_delay before any ack is packed
 * (verified chain: parse_json calls configure_memory; init_programmer_framed
 * calls parse_json and only emits the ack afterwards). */
void test_budget_zero_pulse_width_never_divides_by_zero(void) {
    TEST_ASSERT_EQUAL_UINT32_MESSAGE(25, eprom_worst_pulses(25, 0, 50000),
        "pulse_us == 0 must return max_pulses without dividing by zero -- a guard for an "
        "unresolved pulse width, never the live path (configure_eprom's fallback switch "
        "always resolves it first)");
    TEST_ASSERT_EQUAL_UINT32_MESSAGE(0, eprom_per_byte_budget_us(25, 0, 50000, 0, 0),
        "pulse_us == 0 propagates to a zero per-byte budget (25 pulses * 0 us + 0 overprogram)");
}

/* Case 6: eprom_block_budget_s against all three shipped rows plus the
 * padding rule, and the non-EPROM "advertise nothing" contract. A returned
 * 0 means "advertise nothing", never "no time needed" -- the host's own
 * plausibility clamp then leaves its attribute None and the host's own
 * fallback applies. */
void test_budget_block_seconds_matches_the_shipped_rows_and_is_padded(void) {
    TEST_ASSERT_EQUAL_UINT16_MESSAGE(8, eprom_block_budget_s(0x07, 100, 1024),
        "0x07 @ 100us/1024B: raw 2.5s ceils to 3s, padded x2+2 == 8");
    TEST_ASSERT_EQUAL_UINT16_MESSAGE(54, eprom_block_budget_s(0x07, 1000, 1024),
        "0x07 @ 1000us/1024B: raw 25s ceils to 26s, padded x2+2 == 54");
    TEST_ASSERT_EQUAL_UINT16_MESSAGE(3358, eprom_block_budget_s(0x07, 65535, 1024),
        "0x07 @ 65535us/1024B (host ceiling): raw ~1677.7s ceils to 1678s, padded x2+2 == 3358 "
        "-- fits uint16_t with room to spare (max 65535)");
    TEST_ASSERT_EQUAL_UINT16_MESSAGE(6, eprom_block_budget_s(0x08, 100, 512),
        "0x08 @ 100us/512B (Uno-class buffer): raw 1.25s ceils to 2s, padded x2+2 == 6");
    TEST_ASSERT_EQUAL_UINT16_MESSAGE(106, eprom_block_budget_s(0x0B, 500, 1024),
        "0x0B @ 500us/1024B (modal shipped width): raw 51.2s ceils to 52s, padded x2+2 == 106");
    TEST_ASSERT_EQUAL_UINT16_MESSAGE(208, eprom_block_budget_s(0x0B, 49999, 1024),
        "0x0B @ 49999us/1024B (the BF-3 pathological width): raw 102.4s ceils to 103s, "
        "padded x2+2 == 208 -- proves the ceil pulse-count correction survives all the way "
        "to the advertised seconds value");
    TEST_ASSERT_EQUAL_UINT16_MESSAGE(106, eprom_block_budget_s(0x0B, 49999, 512),
        "0x0B @ 49999us/512B (Uno-class buffer, same pathological width): raw 51.2s ceils to "
        "52s, padded x2+2 == 106");
    TEST_ASSERT_EQUAL_UINT16_MESSAGE(0, eprom_block_budget_s(0x05, 1000, 1024),
        "0x05 (flash, no eprom_params row) must return 0 -- \"advertise nothing\", never "
        "\"no time needed\"; the host's plausibility clamp leaves the attribute None and its "
        "own fallback applies");
    TEST_ASSERT_EQUAL_UINT16_MESSAGE(0, eprom_block_budget_s(0x0D, 1000, 1024),
        "0x0D (28C EEPROM, no eprom_params row) must also return 0, same \"advertise "
        "nothing\" contract as the 0x05 case above");
}

/* ═════════════════════════════════════════════════════════════════════════
 * Phase 143 Plan 05 / HOST-02 (firmware half) / D-02, D-03 -- two cadence
 * cases proving the new time-gated MSG_DATA_PROGRESS emission
 * (src/proms/eprom.cpp, guarded #ifndef SERIAL_ON_IO -- compiled IN on this
 * native env, exactly as on leonardo) fires when the mocked clock advances
 * past EPROM_PROGRESS_EMIT_INTERVAL_MS, and fires NOT AT ALL when it does
 * not -- the non-vacuity control every cadence oracle needs (D-25,
 * T-143-VACUOUSCLOCK). This plan flips NO requirement checkbox (frontmatter
 * requirements: [] is deliberate); it contributes the firmware half of
 * HOST-02 only -- plan 143-10 flips the HOST-* checkboxes after every piece
 * of evidence exists.
 * ═════════════════════════════════════════════════════════════════════════ */

void test_progress_emits_when_the_clock_advances_past_the_interval(void) {
    /* 16 bytes: the first 8 are non-0xFF and individually seeded to
     * converge after exactly 1 pulse each (readback defaults an UNSEEDED
     * address to 0xFF forever, so a non-0xFF expected value with
     * converge_after=1 guarantees the pulse loop genuinely runs for each of
     * these) -- proving the per-byte loop actually programs real data, not
     * merely iterates. The remaining 8 are 0xFF (LOOP-06's own first skip
     * rule: `if (expected == 0xFF) continue;` short-circuits BEFORE any
     * read, so these need no read-back seed at all -- LOOP_READBACK_MAX_
     * ENTRIES caps simultaneously seeded addresses at 8, and this suite's
     * pre-existing cases never seed more). Both halves still pass through
     * this plan's progress-emit check, which sits BEFORE either LOOP-06
     * skip (D-02's own placement reason: cadence independent of how many
     * bytes are skipped) -- the extra 8 iterations exist ONLY to give the
     * mocked clock (200 ms/call, see setUp's comment for why not 500)
     * enough iterations to cross EPROM_PROGRESS_EMIT_INTERVAL_MS (1000)
     * more than once; measured, this drive produces 3 frames (at i=4, 9,
     * 14), comfortably clearing the ">= 2" bar below. */
    firestarter_handle_t h = make_loop_handle(0x07, 28, 65536, 100, LOOP_BUS_CONFIG_0x07);
    const uint8_t block[16] = {
        0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88,
        0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,
    };
    for (int i = 0; i < 8; i++) {
        loop_readback_seed((uint16_t)i, block[i], 1);
    }
    drive_loop_write(&h, 0, block, 16);

    TEST_ASSERT_EQUAL_MESSAGE(RESPONSE_CODE_OK, h.response_code, "response_code -- the 8 real bytes converge; the 8 0xFF bytes need no convergence at all");
    TEST_ASSERT_EQUAL_MESSAGE(0, logged_ids_overflowed(), "logged_ids_overflowed -- the captured prefix must be complete, not truncated");

    /* Filtered by id: the stub also records MSG_DEBUG entries from any
     * production LOG_DEBUG_ID_SUB* call in the build_src_filter (none fire
     * here -- SERIAL_DEBUG is undefined in this env -- but an unfiltered
     * count is not a sound oracle regardless, per host_stubs.cpp's own
     * module comment). */
    int n = logged_id_count();
    int progress_count = 0;
    bool have_last = false;
    uint32_t last_addr = 0;
    for (int i = 0; i < n; i++) {
        if (logged_id_at(i) != MSG_DATA_PROGRESS) continue;
        progress_count++;

        TEST_ASSERT_EQUAL_MESSAGE(8, logged_id_param_count(i),
            "MSG_DATA_PROGRESS payload is 8 bytes -- u32 address + u32 handle->mem_size (D-04: ONE payload contract, matching mem_util_blank_check's own emit byte for byte)");
        uint32_t addr = ((uint32_t)logged_id_param(i, 0) << 24) | ((uint32_t)logged_id_param(i, 1) << 16)
                      | ((uint32_t)logged_id_param(i, 2) << 8)  | (uint32_t)logged_id_param(i, 3);
        uint32_t mem_size = ((uint32_t)logged_id_param(i, 4) << 24) | ((uint32_t)logged_id_param(i, 5) << 16)
                          | ((uint32_t)logged_id_param(i, 6) << 8)  | (uint32_t)logged_id_param(i, 7);

        char amsg[112];
        snprintf(amsg, sizeof(amsg), "progress frame %d: address 0x%08lX must lie in [handle->address, handle->address + data_size)", i, (unsigned long)addr);
        TEST_ASSERT_TRUE_MESSAGE(addr >= h.address && addr < h.address + 16, amsg);
        TEST_ASSERT_EQUAL_UINT32_MESSAGE(h.mem_size, mem_size, "progress frame's second u32 must equal handle->mem_size (D-04's one payload contract -- absolute address plus chip geometry, never a block-relative pair)");

        if (have_last) {
            char imsg[128];
            snprintf(imsg, sizeof(imsg), "progress frame %d's address (0x%08lX) must be STRICTLY greater than the previous frame's (0x%08lX) -- D-03: time-bounded, not byte-counted", i, (unsigned long)addr, (unsigned long)last_addr);
            TEST_ASSERT_TRUE_MESSAGE(addr > last_addr, imsg);
        }
        last_addr = addr;
        have_last = true;
    }

    TEST_ASSERT_TRUE_MESSAGE(progress_count >= 2,
        "at least 2 MSG_DATA_PROGRESS frames must have fired while the mocked clock advanced past EPROM_PROGRESS_EMIT_INTERVAL_MS repeatedly across this 16-byte drive -- zero would mean the emission never fires (deleted or unreachable); exactly 1 would not prove the cadence REPEATS");
}

void test_progress_emits_nothing_when_the_clock_does_not_advance(void) {
    /* Non-vacuity control (D-25, T-143-VACUOUSCLOCK): without this case, the
     * positive case above could pass for the WRONG reason -- e.g. an
     * emission that fires unconditionally, every iteration, rather than one
     * genuinely gated on elapsed mocked time. Freezing millis() here
     * locally overrides setUp's advancing lambda for the rest of THIS case
     * only: the next case's own setUp() call (ArduinoFakeReset() then
     * re-When(...millis...)) wipes this override and reinstalls the
     * advancing lambda fresh, so this freeze cannot leak forward. A frozen
     * clock is exactly the state native_trace_v131 is pinned in (its own
     * setUp also pins millis() to AlwaysReturn(0), Phase 138) -- which is
     * why D-02's emission adds ZERO new frames to that frozen trace (D-24);
     * Phase 144 / TEST-06 will find zero D-02-attributable strobes there. */
    When(Method(ArduinoFake(), millis)).AlwaysReturn(0);

    firestarter_handle_t h = make_loop_handle(0x07, 28, 65536, 100, LOOP_BUS_CONFIG_0x07);
    const uint8_t block[16] = {
        0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88,
        0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,
    };
    for (int i = 0; i < 8; i++) {
        loop_readback_seed((uint16_t)i, block[i], 1);
    }
    drive_loop_write(&h, 0, block, 16);

    TEST_ASSERT_EQUAL_MESSAGE(RESPONSE_CODE_OK, h.response_code,
        "response_code -- the write must still complete successfully; a case that passes because the write failed early proves nothing");
    TEST_ASSERT_EQUAL_MESSAGE(0, count_logged_id(MSG_DATA_PROGRESS),
        "zero MSG_DATA_PROGRESS frames with the clock frozen at a constant (matching native_trace_v131's own AlwaysReturn(0) pin, D-24) -- the emission must be genuinely time-gated, never unconditional");
}

int main(int argc, char** argv) {
    (void)argc; (void)argv;
    UNITY_BEGIN();

    RUN_TEST(test_setup_leaves_all_three_recorders_clean);
    RUN_TEST(test_timing_hook_records_both_delay_kinds_with_their_arguments);
    RUN_TEST(test_readback_model_returns_ff_until_converge_then_the_target);
    RUN_TEST(test_readback_model_returns_ff_and_stays_unseeded_for_an_unknown_address);
    RUN_TEST(test_readback_model_distinguishes_two_addresses_across_an_a16_crossing);
    RUN_TEST(test_logged_id_capture_records_the_id_and_its_packed_params);

    /* LOOP-01 (plan 141-07, task 1) */
    RUN_TEST(test_loop01_each_byte_gets_exactly_the_seeded_number_of_fixed_width_pulses);
    RUN_TEST(test_loop01_pulse_width_never_grows_between_attempts);
    RUN_TEST(test_loop01_verify_read_follows_every_pulse);
    RUN_TEST(test_loop01_a_byte_that_converges_on_its_last_permitted_pulse_succeeds);

    /* LOOP-06 (plan 141-07, task 2) */
    RUN_TEST(test_loop06_an_ff_target_byte_is_never_read_and_never_pulsed);
    RUN_TEST(test_loop06_an_already_matching_byte_is_read_once_and_never_pulsed);
    RUN_TEST(test_loop06_a_block_of_only_skipped_bytes_emits_no_pulse_at_all);
    RUN_TEST(test_loop06_the_ff_rule_does_not_suppress_the_final_verify_pass);

    /* LOOP-04 (plan 141-07, task 3) */
    RUN_TEST(test_loop04_energy_cap_stops_at_exactly_100_pulses_at_500us);
    RUN_TEST(test_loop04_energy_cap_stops_at_exactly_50_pulses_at_1000us);
    RUN_TEST(test_loop04_energy_cap_stops_at_exactly_250_pulses_at_200us);
    RUN_TEST(test_loop04_the_energy_cap_binds_before_max_pulses_on_every_shipped_width);
    RUN_TEST(test_loop04_no_live_row_emits_an_overprogram_pulse);
    RUN_TEST(test_loop04_0x0B_runs_no_final_full_block_verify_pass);

    /* LOOP-03 / LOOP-07 arithmetic (plan 141-08, task 1) */
    RUN_TEST(test_loop03_overprogram_duration_is_three_times_the_pulse_count_times_the_width);
    RUN_TEST(test_loop03_overprogram_is_zero_when_the_factor_is_zero);
    RUN_TEST(test_loop03_overprogram_clamps_at_the_cap_rather_than_refusing);
    RUN_TEST(test_loop03_overprogram_is_32_bit_safe_at_the_uint16_ceiling);
    RUN_TEST(test_loop03_a_zero_cap_yields_no_overprogram_pulse);
    RUN_TEST(test_loop07_split_does_not_fire_at_or_below_the_ceiling);
    RUN_TEST(test_loop07_split_fires_above_the_ceiling_and_stays_32_bit_safe);
    RUN_TEST(test_loop07_delay_us_emits_the_split_as_delay_then_delaymicroseconds);

    /* LOOP-05 / LOOP-07 drive cases (plan 141-08, task 2) */
    RUN_TEST(test_loop05_a_byte_that_misses_within_max_pulses_aborts_the_block);
    RUN_TEST(test_loop05_the_loops_own_strobes_disable_the_high_voltage_route);
    RUN_TEST(test_loop05_a_successful_block_does_not_disable_the_route);
    RUN_TEST(test_loop07_no_recorded_us_delay_exceeds_the_avr_ceiling_under_a_real_drive);
    RUN_TEST(test_loop07_an_over_cap_pulse_is_refused_before_any_high_voltage_on_a_capped_row);

    /* LOOP-08 (plan 141-08, task 3) */
    RUN_TEST(test_loop08_the_route_is_asserted_once_before_the_first_data_strobe);
    RUN_TEST(test_loop08_the_route_bit_is_present_in_every_control_value_across_the_block);
    RUN_TEST(test_loop08_route_presence_is_not_vacuous);
    RUN_TEST(test_loop08_dip32_block_crossing_an_a16_boundary_keeps_the_route_and_toggles_a16);

    /* VPP-01 (Phase 142, plan 142-04) */
    RUN_TEST(test_vpp01_dip32_drop_bit_survives_the_block_on_rev2_class);
    RUN_TEST(test_loop08_the_28_pin_row_keeps_its_drop_bit);

    /* Phase 143 Plan 01 / HOST-01 (firmware half) / BF-3 */
    RUN_TEST(test_budget_uncapped_energy_cap_is_not_a_cap_at_zero);
    RUN_TEST(test_budget_pulse_count_ceils_because_the_loop_tests_after_it_increments);
    RUN_TEST(test_budget_0x0b_at_49999us_is_99998us_per_byte_not_50000);
    RUN_TEST(test_budget_overprogram_term_is_zero_for_factor_zero_and_clamped_for_factor_three);
    RUN_TEST(test_budget_zero_pulse_width_never_divides_by_zero);
    RUN_TEST(test_budget_block_seconds_matches_the_shipped_rows_and_is_padded);

    /* Phase 143 Plan 05 / HOST-02 (firmware half) / D-02, D-03 */
    RUN_TEST(test_progress_emits_when_the_clock_advances_past_the_interval);
    RUN_TEST(test_progress_emits_nothing_when_the_clock_does_not_advance);

    return UNITY_END();
}
