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

    return UNITY_END();
}
