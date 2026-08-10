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
#include "memory_utils.h"

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
 * test_trace_eprom_v131's seam of the same name; the rest
 * (loop_readback_*/logged_id_*) are new to this suite. rurp_read_data_buffer
 * and rurp_log_id/_u8/_u16/_u24/_u32 are already declared via firestarter.h
 * -> rurp_shield.h, so they are not re-declared here. */
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
    /* Unused by any case in this plan, but ArduinoFake SIGABRTs on any
     * unmocked call -- cheap insurance matching house convention. */
    When(Method(ArduinoFake(), millis)).AlwaysReturn(0);
    When(Method(ArduinoFake(), micros)).AlwaysReturn(0);

    clear_strobes();
    clear_timings();
    clear_logged_ids();
    loop_readback_reset();
    reset_register_cache(0x00, 0x00, 0x00);
}

void tearDown(void) {}

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

int main(int argc, char** argv) {
    (void)argc; (void)argv;
    UNITY_BEGIN();

    RUN_TEST(test_setup_leaves_all_three_recorders_clean);
    RUN_TEST(test_timing_hook_records_both_delay_kinds_with_their_arguments);
    RUN_TEST(test_readback_model_returns_ff_until_converge_then_the_target);
    RUN_TEST(test_readback_model_returns_ff_and_stays_unseeded_for_an_unknown_address);
    RUN_TEST(test_readback_model_distinguishes_two_addresses_across_an_a16_crossing);
    RUN_TEST(test_logged_id_capture_records_the_id_and_its_packed_params);

    return UNITY_END();
}
