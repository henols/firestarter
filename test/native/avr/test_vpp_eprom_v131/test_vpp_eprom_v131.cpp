/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 *
 * Phase 142 (VPP-01..VPP-04, D-14) -- the suite skeleton for the EPROM
 * high-voltage-routing and VPP-validation oracle: setUp/tearDown hooks
 * wiring all four host_stubs.cpp recorder/mock layers, a
 * make_vpp_handle/drive_vpp_init/drive_vpp_write contract for plans 142-03/
 * 142-05/142-06 to drive against, the three bus_config_t literals those
 * plans need, and ONE harness self-check case that proves the harness
 * itself -- and the two composites Task 1 landed -- are non-vacuous.
 *
 * This plan completes NO requirement (frontmatter requirements: []) -- the
 * one case below is harness self-verification only. Dimension coverage
 * (VPP-01..04) is landed by plans 142-03/142-05/142-06 and recorded by
 * 142-07, after every piece of evidence exists.
 *
 * Plans 142-03, 142-05 and 142-06 EXTEND this same file (see their own
 * files_modified) rather than creating a new one -- so every symbol,
 * constant and helper below is authored as a fixed, reusable contract, not
 * a plan-142-01-only convenience. This mirrors the test_loop_eprom_v131.cpp
 * precedent from Phase 141 Plan 03 exactly.
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
#include "messages.h"  /* MSG_ERR_VPP_HIGH / MSG_WARN_VPP_HIGH / MSG_WARN_VPP_LOW /
                         * MSG_WARN_REV0_VPP_UNSUPPORTED -- neither firestarter.h
                         * nor eprom.h/eprom_params.h/memory_utils.h pulls this in
                         * transitively. */

using namespace fakeit;

/* ─────────────────────────────────────────────────────────────────────────
 * Restated locally, because #defines inside host_stubs.cpp's translation
 * unit are invisible here, a SEPARATE translation unit -- mirrors
 * test_loop_eprom_v131.cpp's identical restatement of these same four kind
 * constants.
 * ───────────────────────────────────────────────────────────────────────── */
#define STROBE_KIND_DATA     1
#define STROBE_KIND_PIN      2
#define TIMING_KIND_DELAY_US 3
#define TIMING_KIND_DELAY_MS 4

/* Shared strobe/timing recorder accessors (../_shared/host_stubs_common.inc,
 * compiled into host_stubs.cpp's translation unit under the
 * HOST_STUBS_REAL_REGISTER_UTILS + HOST_STUBS_RECORD_TIMING arms). */
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

/* host_stubs.cpp's own seams (Task 2). reset_register_cache mirrors the
 * sibling suite's seam of the same name; the vpp_readback_ family is this
 * suite's own extended (mismatch-window) model; set_mock_vpp_mv is this
 * suite's voltage-injection seam. rurp_read_data_buffer and
 * rurp_log_id/_u8/_u16/_u24/_u32 are already declared via firestarter.h ->
 * rurp_shield.h, so they are not re-declared here. */
extern "C" void reset_register_cache(uint8_t lsb, uint8_t msb, rurp_register_t ctrl);

extern "C" void vpp_readback_reset(void);
extern "C" void vpp_readback_seed(uint16_t addr16, uint8_t target, uint16_t converge_after, uint16_t mismatch_from);
extern "C" int  vpp_readback_reads(uint16_t addr16);
extern "C" int  vpp_readback_seeded_count(void);

extern "C" void     clear_logged_ids(void);
extern "C" int      logged_id_count(void);
extern "C" uint8_t  logged_id_at(int i);
extern "C" uint8_t  logged_id_param_count(int i);
extern "C" uint8_t  logged_id_param(int i, int j);
extern "C" int      logged_ids_overflowed(void);

extern "C" void set_mock_vpp_mv(uint16_t mv);

/* ─────────────────────────────────────────────────────────────────────────
 * setUp / tearDown
 * ───────────────────────────────────────────────────────────────────────── */

void setUp(void) {
    ArduinoFakeReset();
    When(OverloadedMethod(ArduinoFake(Serial), write, size_t(uint8_t))).AlwaysReturn(1);
    When(OverloadedMethod(ArduinoFake(Serial), write, size_t(const uint8_t*, size_t))).AlwaysReturn(1);
    When(Method(ArduinoFake(Serial), flush)).AlwaysReturn();

    /* All FOUR of delay/delayMicroseconds/millis/micros are mandatory:
     * ArduinoFake SIGABRTs on any unmocked call, and correction C-2
     * measured test_flash_intel_vpp aborting mid-run for exactly this
     * reason -- that suite's setUp mocks delay() only. */
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
    clear_logged_ids();
    vpp_readback_reset();
    reset_register_cache(0x00, 0x00, 0x00);
    /* No case may inherit another's injected voltage. */
    set_mock_vpp_mv(0);
}

void tearDown(void) {
    /* Reset any hardware-revision override back to the file's default
     * (REVISION_0, via the shared stub base's zero-initialised
     * s_host_config) so it can never leak into a case that runs after one
     * that overrode it -- Unity calls tearDown() even when a case fails via
     * TEST_ASSERT's longjmp, so this reset is unconditional and always
     * runs. */
    rurp_get_config()->hardware_revision = 0;
}

/* ─────────────────────────────────────────────────────────────────────────
 * make_vpp_handle -- fresh, zero-initialised handle per case.
 *
 * THE ONE MANDATORY DIVERGENCE FROM THE SIBLING SUITE'S make_loop_handle:
 * that factory never sets vpp_mv, leaving it 0, which makes
 * eprom_check_vpp's compares `0 > 0 + 500` (false) and `0 < 0 * 95 / 100`
 * (false) -- the identical vacuity trap D-13 found in
 * test_val_eprom.cpp:74. Copying that factory as-is would make every
 * VPP-04 case in this suite vacuously pass. h.vpp_mv is therefore a
 * REQUIRED parameter here, following test_flash_intel_vpp.cpp's
 * make_intel_handle precedent (h.vpp_mv = vpp_setpoint at :82).
 *
 * h.chip_id = 0 skips the chip-id branch (eprom_generic_init only reaches
 * eprom_internal_check_chip_id when chip_id > 0). ctrl_flags always carries
 * FLAG_SKIP_BLANK_CHECK | FLAG_SKIP_ERASE so a case's own extra_ctrl_flags
 * (e.g. FLAG_FORCE, FLAG_VPE_AS_VPP) never has to repeat them.
 * ───────────────────────────────────────────────────────────────────────── */
[[maybe_unused]] static firestarter_handle_t make_vpp_handle(uint32_t protocol, uint8_t pins, uint32_t mem_size,
                                                                uint32_t pulse_delay_us, uint16_t vpp_setpoint_mv,
                                                                uint32_t extra_ctrl_flags, const bus_config_t& bus_config) {
    firestarter_handle_t h = {};
    h.protocol = protocol;
    h.pins = pins;
    h.mem_size = mem_size;
    h.pulse_delay = pulse_delay_us;
    h.bus_config = bus_config;
    h.cmd = CMD_WRITE;
    h.response_code = RESPONSE_CODE_OK;
    h.chip_id = 0;
    h.ctrl_flags = extra_ctrl_flags | FLAG_SKIP_BLANK_CHECK | FLAG_SKIP_ERASE;
    h.vpp_mv = vpp_setpoint_mv;
    return h;
}

/* ─────────────────────────────────────────────────────────────────────────
 * bus_config ground truth, copied VERBATIM (renamed VPP_BUS_CONFIG_0x07 /
 * _0x08 / _0x0B) from test_loop_eprom_v131.cpp's LOOP_BUS_CONFIG_0x07 /
 * _0x08 / _0x0B (itself copied from test_trace_eprom_v131.cpp's
 * V131_BUS_CONFIG_*) -- do NOT invent new ones: a zeroed bus_config is
 * DEGENERATE, not an identity remap (mem_util_remap_address_bus starts from
 * `config.address_mask & address`, and address_mask == 0 collapses every
 * address to 0).
 * ───────────────────────────────────────────────────────────────────────── */

/* AM27C512 (protocol 0x07) -- pinout DIP28_27512, mem_size 65536, pulse
 * 100 us (the modal 0x07 value). derive_row: bus=[0..15], matching_lines=16,
 * rw_line=None, vpp_pin=None, static_high=None. */
[[maybe_unused]] static const bus_config_t VPP_BUS_CONFIG_0x07 = {
    { 0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0A, 0x0B, 0x0C, 0x0D, 0x0E, 0x0F, 0xFF },
    0x0000FFFFUL,
    16,
    0xFF,
    0xFF,
    0x00000000UL
};

/* AM27C020 (protocol 0x08) -- pinout DIP32_27C020, mem_size 262144, pulse
 * 100 us (the modal 0x08 value). derive_row: bus=[0..16,20],
 * matching_lines=17, rw_line=22, vpp_pin=21, static_high=None. vpp_pin=21=
 * 0x15=VPP_P1_32_DIP exactly, so using_p1_as_vpp(handle) is TRUE for this
 * chip (handle.pins==32). matching_lines=17 / static_high_mask=0 below is
 * also this suite's own read-back-model key derivation (host_stubs.cpp): it
 * is the reason the 16-bit LSB|MSB<<8 key equals address & 0xFFFF for this,
 * the tree's only 32-pin config. */
[[maybe_unused]] static const bus_config_t VPP_BUS_CONFIG_0x08 = {
    { 0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0A, 0x0B, 0x0C, 0x0D, 0x0E, 0x0F, 0x10, 0x14, 0xFF },
    0x0011FFFFUL,
    17,
    0x16,
    0x15,
    0x00000000UL
};

/* AM2716 (protocol 0x0B) -- pinout DIP24_2716, mem_size 2048, pulse 500 us
 * (the modal 0x0B value). derive_row: bus=[0..10], matching_lines=11,
 * rw_line=None, vpp_pin=11, static_high=[13]. vpp_pin=11=0x0B=
 * VPP_P21_24_DIP exactly, so using_p1_as_vpp(handle) is also TRUE for this
 * chip (handle.pins==24). */
[[maybe_unused]] static const bus_config_t VPP_BUS_CONFIG_0x0B = {
    { 0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0A, 0xFF },
    0x000007FFUL,
    11,
    0xFF,
    0x0B,
    0x00002000UL
};

/* ─────────────────────────────────────────────────────────────────────────
 * drive_vpp_write / drive_vpp_init -- the fixed drive-helper contract for
 * plans 142-03/142-05/142-06. Both share the identical prologue (Modelled
 * on test_loop_eprom_v131.cpp's drive_loop_write):
 *
 *   configure_memory (writes address 0 itself, memory.cpp:93)
 *   -> reset_register_cache (AFTER configure_memory -- it calls
 *      mem_util_set_address(handle, 0), memory.cpp:97)
 *   -> clear_strobes / clear_timings / clear_logged_ids
 *
 * and then diverge in their terminal call:
 *   - drive_vpp_write seeds address/data_size/data_buffer and calls
 *     h->firestarter_operation_main(h) -- NEVER _init, NEVER the whole
 *     command. Never the whole command: command_done() writes
 *     CONTROL_REGISTER = 0x00 on every exit regardless of what the
 *     write-execute path did, which would make any high-voltage assertion
 *     vacuous.
 *   - drive_vpp_init calls h->firestarter_operation_init(h) instead --
 *     THE ONE MANDATORY DIVERGENCE from the sibling suite's contract, and
 *     the reason this suite exists at all: VPP-04's gate lives inside
 *     eprom_check_vpp, which is reached ONLY via _init
 *     (eprom_generic_init:412-413, installed as the default at
 *     configure_eprom:43). The sibling suite's drive_loop_write
 *     deliberately never drives _init (it would double-enable the
 *     regulator before the loop's own top-of-block check); this suite
 *     deliberately DOES, because that is the only path to the code under
 *     test.
 * ───────────────────────────────────────────────────────────────────────── */
[[maybe_unused]] static void drive_vpp_write(firestarter_handle_t* h, uint32_t base,
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

[[maybe_unused]] static void drive_vpp_init(firestarter_handle_t* h) {
    configure_memory(h);
    reset_register_cache(0x00, 0x00, 0x00);
    clear_strobes();
    clear_timings();
    clear_logged_ids();
    h->firestarter_operation_init(h);
}

/* ─────────────────────────────────────────────────────────────────────────
 * Shared helpers for later plans -- the CONTROL-register write stream.
 * VERBATIM from test_loop_eprom_v131.cpp's identical helpers (:1136-1193).
 *
 * Every non-elided CONTROL write (rurp_write_to_register(CONTROL_REGISTER,
 * ...), include/rurp_register_utils.h) shows up in the strobe recorder as
 * THREE consecutive entries via rurp_internal_write_to_register, in this
 * FIXED, unconditional order, never interleaved with anything else:
 *   [STROBE_KIND_DATA, pin=0,               value=<the physical byte>]
 *   [STROBE_KIND_PIN,  pin=CONTROL_REGISTER, value=1]  (latch rise)
 *   [STROBE_KIND_PIN,  pin=CONTROL_REGISTER, value=0]  (latch fall)
 * STROBE_KIND_DATA is NOT a safe raw pulse-count oracle, because a
 * register-shift write pushes this exact same DATA-strobe shape as a
 * genuine chip-data pulse. These helpers exploit that fixed 3-entry shape
 * directly instead of fighting it.
 * ───────────────────────────────────────────────────────────────────────── */
[[maybe_unused]] static int control_write_count(void) {
    int n = strobe_count();
    int c = 0;
    for (int i = 0; i < n; i++) {
        if (strobe_kind(i) == STROBE_KIND_PIN && strobe_pin(i) == CONTROL_REGISTER && strobe_value(i) == 1) c++;
    }
    return c;
}

[[maybe_unused]] static int control_write_strobe_index(int idx) {
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
 * mem_util_calculate_top_address_register / eprom.cpp compute. -1 means
 * "not decodable"; every assertion built on this must check `v >= 0` first. */
[[maybe_unused]] static int control_write_value(int idx) {
    int strobe_idx = control_write_strobe_index(idx);
    if (strobe_idx <= 0 || strobe_kind(strobe_idx - 1) != STROBE_KIND_DATA) return -1;
    return (int)strobe_value(strobe_idx - 1);
}

/* The stream index of the first GENUINE chip-data pulse -- the first
 * STROBE_KIND_DATA entry whose value matches one of the block's own byte
 * values, never a register-shift write's LSB/MSB/CONTROL byte. */
[[maybe_unused]] static int first_genuine_pulse_strobe_index(const uint8_t* values, int n_values) {
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

[[maybe_unused]] static int count_logged_id(uint8_t id) {
    int n = logged_id_count();
    int c = 0;
    for (int i = 0; i < n; i++) {
        if (logged_id_at(i) == id) c++;
    }
    return c;
}

[[maybe_unused]] static int find_logged_id(uint8_t id) {
    int n = logged_id_count();
    for (int i = 0; i < n; i++) {
        if (logged_id_at(i) == id) return i;
    }
    return -1;
}

/* ─────────────────────────────────────────────────────────────────────────
 * Revision-override idiom, for later plans' drop-bit / VPP-04 cases.
 *
 * Mandatory for every drop-bit assertion: on the default REVISION_0/1
 * mapping, CTRL_ADDRESS_LINE_16 and CTRL_VPP_VPE_DROP_ENABLE remap onto the
 * SAME physical bit (0x01), which would make a drop-bit claim undecidable
 * from the recorded physical byte alone. On REVISION_2_x they map to
 * distinct physical bits: CTRL_ADDRESS_LINE_16_REV2 (0x20) vs
 * CTRL_VPP_VPE_DROP_ENABLE_REV2 (0x01). This changes nothing about the
 * LOGICAL behaviour under test -- every eprom.cpp/memory.cpp bit check
 * operates on the pre-remap logical value; only the recorded strobe BYTE
 * differs.
 *
 * ALSO mandatory for every VPP-04 case, for an entirely separate reason: on
 * the default REVISION_0, eprom_check_vpp takes the early return at
 * eprom.cpp:334-338 (MSG_WARN_REV0_VPP_UNSUPPORTED) and never reaches the
 * over-voltage/under-voltage compare at all -- a VPP-04 case that forgets
 * this override would be silently vacuous, proving nothing about the
 * voltage gate it claims to test.
 * ───────────────────────────────────────────────────────────────────────── */
[[maybe_unused]] static void use_revision_2_2_for_this_case(void) {
    rurp_get_config()->hardware_revision = REVISION_2_2;
}

/* ─────────────────────────────────────────────────────────────────────────
 * The one case this plan owns: harness self-check. Three independently
 * failable groups.
 * ───────────────────────────────────────────────────────────────────────── */
void test_setup_leaves_the_harness_clean_and_the_composites_correct(void) {
    /* (a) All recorders/models start clean after setUp(). */
    TEST_ASSERT_EQUAL_MESSAGE(0, strobe_count(), "strobe_count after setUp");
    TEST_ASSERT_EQUAL_MESSAGE(0, timing_count(), "timing_count after setUp");
    TEST_ASSERT_EQUAL_MESSAGE(0, logged_id_count(), "logged_id_count after setUp");
    TEST_ASSERT_EQUAL_MESSAGE(0, strobe_overflowed(), "strobe_overflowed after setUp");
    TEST_ASSERT_EQUAL_MESSAGE(0, vpp_readback_seeded_count(), "vpp_readback_seeded_count after setUp");

    /* (b) The two composites are exactly what Task 1 wrote to
     * rurp_pinout.h. The third assertion is the C-4 / VPE-to-P1-remap
     * guard: it fails the moment someone "helpfully" adds
     * CTRL_VPP_P1_ENABLE to the all-off composite, which would leave the
     * physical VPE line never cleared on the using_p1_as_vpp() remap path
     * (eprom_internal_set_control_register, eprom.cpp:441-447). */
    TEST_ASSERT_EQUAL_MESSAGE((CTRL_VPP_REGULATOR_ENABLE | CTRL_VPP_VPE_DROP_ENABLE),
        EPROM_HV_ROUTE_MASK, "EPROM_HV_ROUTE_MASK must be exactly regulator|drop");
    TEST_ASSERT_EQUAL_MESSAGE((CTRL_VPP_REGULATOR_ENABLE | CTRL_VPP_VPE_DROP_ENABLE | CTRL_VPP_A9_ENABLE | CTRL_VPE_ENABLE),
        EPROM_HV_ALL_OFF_MASK, "EPROM_HV_ALL_OFF_MASK must be exactly regulator|drop|a9|vpe");
    TEST_ASSERT_EQUAL_MESSAGE(0, (EPROM_HV_ALL_OFF_MASK & CTRL_VPP_P1_ENABLE),
        "EPROM_HV_ALL_OFF_MASK must NOT name CTRL_VPP_P1_ENABLE (C-4 + the VPE->P1 remap)");

    /* (c) The read-back model's mismatch window. Seed one address with
     * converge_after=1, mismatch_from=2: read 0 (read_count=0 < 1) -> 0xFF;
     * read 1 (read_count=1, not < 1, not >= 2) -> target; read 2
     * (read_count=2, >= mismatch_from=2) -> bitwise-NOT of target. Without
     * this, the whole VPP-02 X4 leg in plan 142-05 (MSG_ERR_VERIFY, a byte
     * that converges mid-loop and then mismatches on the final verify
     * pass) would rest on an unverified stub. */
    const uint8_t target = 0x55;
    reset_register_cache(0x34, 0x12, 0x00);  /* LSB=0x34, MSB=0x12 -> key 0x1234 */
    vpp_readback_seed(0x1234, target, 1, 2);
    uint8_t r1 = rurp_read_data_buffer();
    uint8_t r2 = rurp_read_data_buffer();
    uint8_t r3 = rurp_read_data_buffer();
    TEST_ASSERT_EQUAL_HEX8_MESSAGE(0xFF, r1, "read 1: not yet converged");
    TEST_ASSERT_EQUAL_HEX8_MESSAGE(target, r2, "read 2: converged, matches");
    TEST_ASSERT_EQUAL_HEX8_MESSAGE((uint8_t)(~target), r3, "read 3: mismatch window reached, diverges again");
    TEST_ASSERT_EQUAL_MESSAGE(3, vpp_readback_reads(0x1234), "read_count must have advanced by exactly 3");
}

int main(int argc, char** argv) {
    (void)argc; (void)argv;
    UNITY_BEGIN();

    /* Plan 142-01 harness self-check (VPP-01..VPP-04 infrastructure) */
    RUN_TEST(test_setup_leaves_the_harness_clean_and_the_composites_correct);

    return UNITY_END();
}
