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

/* ─────────────────────────────────────────────────────────────────────────
 * Plan 142-02 Task 1 (VPP-01): the (pins, revision) preserve-mask truth
 * table, and the 32-pin non-EPROM no-leak / byte-identity baseline.
 *
 * D-01: the `handle->pins < 32` exclusion in
 * mem_util_calculate_top_address_register (memory.cpp:172) is a VPP LEVEL
 * bug, not a routing guard -- it will be removed for Rev 2-class hardware
 * in task 2. D-02 (amended 2026-08-11, operator-confirmed): the removal is
 * gated on hardware revision ALONE -- REVISION_2_x implies preserve for
 * every pins >= 32 protocol. No handle field, no handle->protocol key.
 *
 * Group A calls mem_util_calculate_top_address_register directly
 * (declared memory_utils.h:22) and reads the return value in LOGICAL bit
 * space -- NOT through rurp_map_ctrl_reg_for_hardware_revision's physical
 * remap -- so no REV2-vs-REV0/1 disambiguation on a recorded byte is
 * needed here (contrast Group B below, which DOES need it, because it
 * reads the strobe recorder's post-remap PHYSICAL byte). address = 0 so no
 * address bit confounds the assertion.
 *
 * Every row is registered as its OWN Unity case in main() (never folded
 * into one table-driven function) so pio test's per-case pass/fail report
 * can show "exactly these three rows are RED" directly by name -- a single
 * function combining all nine would longjmp out of TEST_ASSERT on the
 * first failure and hide the rest (Unity has no try/continue).
 *
 * This task changes NO production source (git diff --exit-code -- \
 * src/proms/memory.cpp must exit 0 after this task lands). Against the
 * UNCHANGED tree, exactly the three pins==32 Rev-2-class rows below go RED
 * -- captured verbatim in this plan's SUMMARY per D-15.
 * ───────────────────────────────────────────────────────────────────────── */
static rurp_register_t truth_table_drop_bit(uint8_t pins, uint8_t revision, rurp_register_t seeded_ctrl) {
    rurp_get_config()->hardware_revision = revision;
    firestarter_handle_t h = {};
    h.pins = pins;
    reset_register_cache(0x00, 0x00, seeded_ctrl);
    rurp_register_t top_address = mem_util_calculate_top_address_register(&h, 0);
    return (rurp_register_t)(top_address & CTRL_VPP_VPE_DROP_ENABLE);
}

void test_vpp01_truthtable_pins28_rev2_2_drop_bit_present(void) {
    TEST_ASSERT_TRUE_MESSAGE(truth_table_drop_bit(28, REVISION_2_2, EPROM_HV_ROUTE_MASK) != 0,
        "row (pins=28, REVISION_2_2): drop bit must be PRESENT -- today's behaviour, unchanged");
}

void test_vpp01_truthtable_pins28_rev1_drop_bit_present(void) {
    TEST_ASSERT_TRUE_MESSAGE(truth_table_drop_bit(28, REVISION_1, EPROM_HV_ROUTE_MASK) != 0,
        "row (pins=28, REVISION_1): drop bit must be PRESENT -- today's behaviour, unchanged");
}

void test_vpp01_truthtable_pins32_rev2_0_drop_bit_present(void) {
    TEST_ASSERT_TRUE_MESSAGE(truth_table_drop_bit(32, REVISION_2_0, EPROM_HV_ROUTE_MASK) != 0,
        "row (pins=32, REVISION_2_0): drop bit must be PRESENT -- D-01/D-02, new");
}

void test_vpp01_truthtable_pins32_rev2_2_drop_bit_present(void) {
    TEST_ASSERT_TRUE_MESSAGE(truth_table_drop_bit(32, REVISION_2_2, EPROM_HV_ROUTE_MASK) != 0,
        "row (pins=32, REVISION_2_2): drop bit must be PRESENT -- D-01/D-02, new");
}

void test_vpp01_truthtable_pins32_rev2_3_drop_bit_present(void) {
    /* REVISION_2_3 must be an explicit switch case in memory.cpp's new arm,
     * never a `>= REVISION_2_0` range test -- rurp_shield.h:25-31 numbers
     * revisions 0..5, and a range test would silently swallow a future
     * REVISION_2_4. This row is what makes that requirement executable. */
    TEST_ASSERT_TRUE_MESSAGE(truth_table_drop_bit(32, REVISION_2_3, EPROM_HV_ROUTE_MASK) != 0,
        "row (pins=32, REVISION_2_3): drop bit must be PRESENT -- D-01/D-02, new; must be an explicit case, not a range test");
}

void test_vpp01_truthtable_pins32_rev1_drop_bit_absent(void) {
    /* The load-bearing negative: Rev 1 has no eprom_check_vpp refusal of
     * its own (unlike Rev 0's MSG_WARN_REV0_VPP_UNSUPPORTED), so D-02's
     * revision gate is the ONLY thing standing between a 32-pin part and a
     * preserved drop bit that would force physical A16 permanently high on
     * this revision (drop bit and A16 share physical 0x01 on Rev 0/Rev 1). */
    TEST_ASSERT_TRUE_MESSAGE(truth_table_drop_bit(32, REVISION_1, EPROM_HV_ROUTE_MASK) == 0,
        "row (pins=32, REVISION_1): drop bit must be ABSENT -- D-02's gate, the load-bearing negative");
}

void test_vpp01_truthtable_pins32_rev0_drop_bit_absent(void) {
    TEST_ASSERT_TRUE_MESSAGE(truth_table_drop_bit(32, REVISION_0, EPROM_HV_ROUTE_MASK) == 0,
        "row (pins=32, REVISION_0): drop bit must be ABSENT");
}

void test_vpp01_truthtable_pins32_revunknown_drop_bit_absent(void) {
    /* Fail-safe direction: an unrecognised revision (0xFE) keeps TODAY's
     * stripping, matching rurp_hw_rev_utils.h:33-37's `default` leaving
     * ctrl_reg = 0. */
    TEST_ASSERT_TRUE_MESSAGE(truth_table_drop_bit(32, REVISION_UNKNOWN, EPROM_HV_ROUTE_MASK) == 0,
        "row (pins=32, REVISION_UNKNOWN): drop bit must be ABSENT -- fail-safe default direction");
}

void test_vpp01_truthtable_pins32_rev2_2_preserve_never_introduces(void) {
    /* D-02's widened-reach argument, closed structurally rather than
     * argued: with NO drop bit in the cache (seeded_ctrl = 0x00), pins==32
     * at REVISION_2_2 -- inside the new preserve arm -- must not ACQUIRE
     * one. This proves the new arm widens only a preserve, never a set: a
     * 32-pin protocol that never sets the bit can never gain it.
     * Paired non-vacuity partner: test_vpp01_truthtable_pins32_rev2_2_drop_bit_present
     * above is the IDENTICAL handle shape and revision with the bit
     * seeded, showing it PRESENT -- a mask that simply never preserved
     * anything could not pass both this case and that one. */
    TEST_ASSERT_TRUE_MESSAGE(truth_table_drop_bit(32, REVISION_2_2, 0x00) == 0,
        "row (pins=32, REVISION_2_2, no bit seeded): preserve must never INTRODUCE the drop bit");
}

/* ─────────────────────────────────────────────────────────────────────────
 * Group B -- the 32-pin non-EPROM no-leak / byte-identity baseline
 * (D-02's amendment).
 * ───────────────────────────────────────────────────────────────────────── */
void test_vpp01_dip32_nonEprom_0x10_route_is_byte_identical_before_and_after(void) {
    /* D-02's amendment: the new preserve arm's nominal reach widens to
     * EVERY 32-pin protocol on Rev 2-class (0x0E, 0x29, 0x10, 32-pin
     * flash), but none of them ever SETS the drop bit, so there is
     * nothing for the widened preserve to leak. protocol = 0x10
     * (PROTO_FLASH_INTEL, memory.cpp:99) is deliberately a 32-pin
     * NON-EPROM protocol whose route is CTRL_VPP_P1_ENABLE -- a DIFFERENT
     * bit from the EPROM family's CTRL_VPP_VPE_DROP_ENABLE.
     *
     * mem_util_set_address is firestarter_set_address for EVERY protocol
     * (memory.cpp:92, installed by configure_memory for all handles) and
     * writes CONTROL_REGISTER unconditionally (memory.cpp:231), so a plain
     * address sweep -- never a 0x10 write/read/erase operation -- covers
     * the whole surface at risk without depending on any 0x10 operation
     * semantics. The four addresses cross the A16 boundary (0x00FFFE /
     * 0x00FFFF below it, 0x010000 / 0x010001 at/above it) so the
     * top-address computation is genuinely exercised, not just re-latching
     * a static value.
     *
     * REVISION_2_2 is mandatory here for the SAME reason as every other
     * drop-bit-adjacent assertion in this suite (L-6): it disambiguates
     * the recorded PHYSICAL byte -- on the default REVISION_0/1 mapping
     * the drop bit and A16 collapse onto the same physical 0x01, which
     * would make "no drop bit leaked" undecidable from the byte alone. */
    rurp_get_config()->hardware_revision = REVISION_2_2;
    firestarter_handle_t h = make_vpp_handle(0x10 /* PROTO_FLASH_INTEL */, 32, 262144, 100, 1200, 0, VPP_BUS_CONFIG_0x08);
    configure_memory(&h);
    reset_register_cache(0x00, 0x00, 0x00);
    clear_strobes();

    const uint32_t addrs[4] = { 0x00FFFEUL, 0x00FFFFUL, 0x010000UL, 0x010001UL };
    for (int i = 0; i < 4; i++) {
        h.firestarter_set_address(&h, addrs[i]);
    }

    TEST_ASSERT_EQUAL_MESSAGE(0, strobe_overflowed(), "strobe_overflowed -- tiny four-address sweep, must be sound");

    int n = control_write_count();
    for (int i = 0; i < n; i++) {
        int v = control_write_value(i);
        char msg[128];
        snprintf(msg, sizeof(msg), "control write %d (0x%02X) must NOT carry CTRL_VPP_VPE_DROP_ENABLE_REV2 -- 0x10 never sets it, no leak", i, v);
        TEST_ASSERT_TRUE_MESSAGE(v >= 0 && (v & CTRL_VPP_VPE_DROP_ENABLE_REV2) == 0, msg);
    }

    /* Measured pre-change baseline (D-15), NOT computed by re-implementing
     * mem_util_calculate_top_address_register: this exact literal sequence
     * was observed by running this case against the UNCHANGED tree in plan
     * 142-02 task 1. It is the "before" side of D-02's byte-identity claim
     * -- task 2 must reproduce this identical sequence after the
     * preserve-mask change lands, proving the widened arm's nominal reach
     * over 0x10 is a genuine no-op.
     * PLACEHOLDER -- overwritten with the measured literal before commit. */
    TEST_ASSERT_EQUAL_MESSAGE(1, n, "control_write_count -- measured pre-change literal");
    TEST_ASSERT_EQUAL_HEX8_MESSAGE(0x20, control_write_value(0), "control write 0 -- measured pre-change literal (A16 boundary crossing, REV2-physical)");
}

/* ─────────────────────────────────────────────────────────────────────────
 * Plan 142-03 Task 1 (VPP-04, D-13/D-15) -- the over-voltage refusal gate
 * VPP-04's own wording presumed already existed for the EPROM path.
 * Confirmed false by grep (D-13): MSG_ERR_VPP_HIGH and MSG_WARN_VPP_HIGH
 * appear in NO test anywhere under test/ or tests/ before this plan.
 * test_val_eprom pins handle->vpp_mv = 0 against a 0-returning stub
 * precisely so neither compare ever fires (test_val_eprom.cpp:74);
 * test_flash_intel_vpp is protocol 0x10 and, per RESEARCH C-2, runs in no
 * PlatformIO environment and SIGABRTs after case 1, so its own SAF-04
 * assertions have never been observed to execute. This group AUTHORS the
 * gate rather than pointing at one that already exists for another family.
 *
 * ALL FOUR of (a)/(b)/(c)/(d) below are GREEN ON ARRIVAL for (a)/(b)/(c)
 * (RESEARCH C-3): eprom_check_vpp (eprom.cpp:331-394) has exactly one
 * `return` (:337, the Rev-0 warning) and it fires BEFORE any route is
 * asserted; every other path -- nominal, over-voltage ERROR (:370-371),
 * over-voltage-with-FLAG_FORCE (:367-368), under-voltage (:389-390) --
 * falls through to the UNCONDITIONAL clear at :393. (a)/(b)/(c) are
 * therefore a REGRESSION gate on behaviour that already holds, not newly-
 * established behaviour -- each is seen RED on its own named planted
 * violation in task 3 (V1/V2/V3) before its GREEN here is believed. (d) is
 * the in-range control that proves the injection seam actually varies the
 * outcome -- flipping its injected reading to 13501 must make it fail
 * (confirmed in task 3's SUMMARY).
 *
 * D-03 non-claims that bound this whole group: no claim about silicon; no
 * claim that the drop resistor produces ~13V (no native suite reads an
 * ADC -- rurp_read_voltage_mv is a mock); no claim that the refusal blocks
 * at a real over-voltage on a real part.
 * ───────────────────────────────────────────────────────────────────────── */
void test_vpp04_a_overvoltage_refusal_fires_by_id_with_payload_shape(void) {
    rurp_get_config()->hardware_revision = REVISION_2_2;  /* mandatory: on
        REVISION_0 eprom_check_vpp takes the early return at eprom.cpp:334-338
        and never reaches the over-voltage compare at all (PATTERNS SS B-8);
        also mandatory because the drop bit and A16 share physical 0x01 on
        Rev 0/1, which would make leg (b)'s drop-bit clear undecidable. */
    firestarter_handle_t h = make_vpp_handle(0x07, 28, 65536, 100, 13000, 0, VPP_BUS_CONFIG_0x07);
    set_mock_vpp_mv(13501);  /* one mV past the 13000+500 over-voltage boundary -- pins the boundary, not a wildly out-of-range value */
    drive_vpp_init(&h);

    TEST_ASSERT_EQUAL_MESSAGE(RESPONSE_CODE_ERROR, h.response_code,
        "an injected 13501 mV reading (setpoint 13000, boundary 13500) must refuse with RESPONSE_CODE_ERROR");
    TEST_ASSERT_EQUAL_MESSAGE(1, count_logged_id(MSG_ERR_VPP_HIGH),
        "MSG_ERR_VPP_HIGH (0xB8) must be logged exactly once, BY ID -- no test in this tree asserts this before this plan (D-13)");
    TEST_ASSERT_EQUAL_MESSAGE(0, count_logged_id(MSG_WARN_VPP_HIGH),
        "the hard-ERROR fork must NOT also log the WARNING id -- pins the FLAG_FORCE fork in both directions");
    int idx = find_logged_id(MSG_ERR_VPP_HIGH);
    TEST_ASSERT_TRUE_MESSAGE(idx >= 0, "MSG_ERR_VPP_HIGH must actually be present in the logged-id stream");
    TEST_ASSERT_EQUAL_MESSAGE(8, logged_id_param_count(idx),
        "the ERROR frame must carry the 8 payload bytes eprom.cpp:369-371 (LOG_ERROR_ID_BYTES) emits");
}

void test_vpp04_b_no_hv_route_left_asserted_on_the_refusal_path(void) {
    /* SAF-04 regression, its INTENT quoted verbatim from
     * test_flash_intel_vpp.cpp:159-171 (its interception mechanism is NOT
     * copied here -- PATTERNS SS C / RESEARCH C-5 -- because replacing
     * h.firestarter_set_control_register after configure_memory would
     * remove the EPROM family's own VPE-to-P1 remap
     * (eprom_internal_set_control_register, eprom.cpp:441-447) from the
     * path under test):
     *   "high-VPP ERROR must leave the regulator cleared ... the original
     *    write_init early-returned on RESPONSE_CODE_ERROR without driving
     *    CTRL_VPP_REGULATOR_ENABLE | CTRL_VPP_P1_ENABLE low, leaving 12V
     *    applied to socket pin 1 after the firmware had just detected
     *    unsafe over-voltage -- the exact hazard the safety check exists
     *    to prevent."
     * For the EPROM family the identical hazard is 13V left on the drop-
     * resistor path after a detected over-voltage refusal (T-142-HOTRAIL).
     *
     * GREEN ON ARRIVAL (C-3): eprom_check_vpp's :393 unconditional clear
     * already runs on this path today. Planted-RED in task 3 (V2) -- and
     * that planted run is the one that proves a refusal-only gate (leg (a)
     * alone) would have passed the exact regression VPP-02 exists to
     * prevent. */
    rurp_get_config()->hardware_revision = REVISION_2_2;
    firestarter_handle_t h = make_vpp_handle(0x07, 28, 65536, 100, 13000, 0, VPP_BUS_CONFIG_0x07);
    set_mock_vpp_mv(13501);
    drive_vpp_init(&h);

    int n = control_write_count();
    TEST_ASSERT_TRUE_MESSAGE(n >= 2, "non-vacuity: at least the over-voltage assert and the refusal's own disable must both have written CONTROL");

    int last = control_write_value(n - 1);
    TEST_ASSERT_TRUE_MESSAGE(last >= 0, "the last CONTROL write must be a genuine, decodable value");
    TEST_ASSERT_TRUE_MESSAGE((last & CTRL_VPP_REGULATOR_ENABLE) == 0,
        "the LAST control value after an over-voltage refusal must have CTRL_VPP_REGULATOR_ENABLE CLEAR -- eprom_check_vpp's own :393 disable");
    TEST_ASSERT_TRUE_MESSAGE((last & CTRL_VPP_VPE_DROP_ENABLE_REV2) == 0,
        "the LAST control value after an over-voltage refusal must have the drop bit CLEAR too");

    bool saw_earlier_set = false;
    for (int i = 0; i < n - 1; i++) {
        int v = control_write_value(i);
        if (v >= 0 && (v & CTRL_VPP_REGULATOR_ENABLE)) { saw_earlier_set = true; break; }
    }
    TEST_ASSERT_TRUE_MESSAGE(saw_earlier_set,
        "an EARLIER control value must have CTRL_VPP_REGULATOR_ENABLE SET -- otherwise the 'last value clear' assertion is vacuously true of a register that was never energised at all");
    TEST_ASSERT_EQUAL_MESSAGE(0, strobe_overflowed(), "strobe_overflowed -- soundness precondition for the strobe walk above");
}

void test_vpp04_c_flag_force_downgrades_to_warning_and_still_clears_the_route(void) {
    /* GREEN ON ARRIVAL (C-3): the is_flag_set(FLAG_FORCE) fork
     * (eprom.cpp:366-372) already exists today. Planted-RED in task 3 (V3). */
    rurp_get_config()->hardware_revision = REVISION_2_2;
    firestarter_handle_t h = make_vpp_handle(0x07, 28, 65536, 100, 13000, FLAG_FORCE, VPP_BUS_CONFIG_0x07);
    set_mock_vpp_mv(13501);
    drive_vpp_init(&h);

    TEST_ASSERT_EQUAL_MESSAGE(RESPONSE_CODE_WARNING, h.response_code,
        "FLAG_FORCE must downgrade the identical over-voltage reading to RESPONSE_CODE_WARNING");
    TEST_ASSERT_EQUAL_MESSAGE(1, count_logged_id(MSG_WARN_VPP_HIGH),
        "MSG_WARN_VPP_HIGH (0x82) must be logged exactly once under FLAG_FORCE");
    TEST_ASSERT_EQUAL_MESSAGE(0, count_logged_id(MSG_ERR_VPP_HIGH),
        "the FLAG_FORCE downgrade must NOT also log the hard-error id");

    /* The downgrade IS the refusal's semantics (D-15c) -- it must leave no
     * route asserted too, exactly like leg (b) above. */
    int n = control_write_count();
    TEST_ASSERT_TRUE_MESSAGE(n >= 2, "non-vacuity: at least the over-voltage assert and the refusal's own disable must both have written CONTROL");
    int last = control_write_value(n - 1);
    TEST_ASSERT_TRUE_MESSAGE(last >= 0, "the last CONTROL write must be a genuine, decodable value");
    TEST_ASSERT_TRUE_MESSAGE((last & CTRL_VPP_REGULATOR_ENABLE) == 0,
        "the LAST control value after the FLAG_FORCE downgrade must have CTRL_VPP_REGULATOR_ENABLE CLEAR too");
    TEST_ASSERT_TRUE_MESSAGE((last & CTRL_VPP_VPE_DROP_ENABLE_REV2) == 0,
        "the LAST control value after the FLAG_FORCE downgrade must have the drop bit CLEAR too");
    bool saw_earlier_set = false;
    for (int i = 0; i < n - 1; i++) {
        int v = control_write_value(i);
        if (v >= 0 && (v & CTRL_VPP_REGULATOR_ENABLE)) { saw_earlier_set = true; break; }
    }
    TEST_ASSERT_TRUE_MESSAGE(saw_earlier_set,
        "an EARLIER control value must have CTRL_VPP_REGULATOR_ENABLE SET -- otherwise the 'last value clear' assertion is vacuously true");
    TEST_ASSERT_EQUAL_MESSAGE(0, strobe_overflowed(), "strobe_overflowed -- soundness precondition for the strobe walk above");
}

void test_vpp04_d_in_range_reading_fires_neither_error_nor_warning(void) {
    /* The control that makes (a) and (c) mean anything: without this leg,
     * (a)'s id assertion could pass for a reason unrelated to the injected
     * reading (e.g. a resolver that always logs MSG_ERR_VPP_HIGH). Task 3's
     * SUMMARY records that flipping set_mock_vpp_mv below to 13501 makes
     * this leg fail -- a control that cannot fail is not a control. */
    rurp_get_config()->hardware_revision = REVISION_2_2;
    firestarter_handle_t h = make_vpp_handle(0x07, 28, 65536, 100, 13000, 0, VPP_BUS_CONFIG_0x07);
    set_mock_vpp_mv(13000);  /* == setpoint: 13000 > 13500 is false, 13000 < 12350 is false */
    drive_vpp_init(&h);

    TEST_ASSERT_EQUAL_MESSAGE(RESPONSE_CODE_OK, h.response_code,
        "an in-range reading (== setpoint) must leave RESPONSE_CODE_OK");
    TEST_ASSERT_EQUAL_MESSAGE(0, count_logged_id(MSG_ERR_VPP_HIGH), "no MSG_ERR_VPP_HIGH on an in-range reading");
    TEST_ASSERT_EQUAL_MESSAGE(0, count_logged_id(MSG_WARN_VPP_HIGH), "no MSG_WARN_VPP_HIGH on an in-range reading");
    TEST_ASSERT_EQUAL_MESSAGE(0, count_logged_id(MSG_WARN_VPP_LOW), "no MSG_WARN_VPP_LOW on an in-range reading");
}

/* ─────────────────────────────────────────────────────────────────────────
 * Plan 142-03 Task 2 (VPP-03, RESEARCH assumption A3) -- pre-rewrite
 * CMD_ERASE / CMD_CHECK_CHIP_ID control-value baselines. NOT feature tests:
 * they exist so plan 142-04's conversion of the hand-rolled disables at
 * eprom.cpp:174/:327/:393/:409 into EPROM_HV_ALL_OFF_MASK is a MEASURED
 * no-op on the two commands PROJECT.md:189-190 protects ("Erase, blank-
 * check, chip-ID, bus remapping and VPP validation behavior -- unchanged
 * except where a change is required for safe shared cleanup"), rather than
 * a reasoned one. The reasoning they replace: widening a CLEAR mask can
 * only clear bits already zero, so the written value is identical and
 * rurp_register_utils.h:39-41's cache-compare elides it identically --
 * plausible, and exactly the kind of claim RESEARCH says to measure, not
 * argue ("do not assert byte-identity in prose -- measure it"). Both cases
 * are planted-RED in task 3 (V4/V5): they are pure equality assertions on a
 * measured stream that would pass on any change that happens not to move a
 * bit.
 * ───────────────────────────────────────────────────────────────────────── */
void test_vpp03_case_e_cmd_erase_control_stream_is_pinned_pre_rewrite(void) {
    rurp_get_config()->hardware_revision = REVISION_2_2;
    firestarter_handle_t h = make_vpp_handle(0x07, 28, 65536, 100, 13000, FLAG_SKIP_BLANK_CHECK, VPP_BUS_CONFIG_0x07);
    h.cmd = CMD_ERASE;  /* MUST be set before configure_memory so configure_eprom installs eprom_erase_execute as firestarter_operation_main */
    set_mock_vpp_mv(13000);  /* in-range; this command never reaches eprom_check_vpp, kept for hygiene with the rest of the suite */

    configure_memory(&h);
    reset_register_cache(0x00, 0x00, 0x00);
    clear_strobes();
    clear_timings();
    clear_logged_ids();
    h.firestarter_operation_main(&h);

    TEST_ASSERT_EQUAL_MESSAGE(0, strobe_overflowed(), "strobe_overflowed -- soundness precondition for the enumerated sequence below");

    /* Measured pre-rewrite baseline (D-15/A3): observed by running this case
     * against the UNCHANGED tree in this plan's task 2 -- the "before" side
     * of research assumption A3. Plan 142-04 must reproduce this IDENTICAL
     * sequence after the composite-mask conversion lands. */
    int n = control_write_count();
    TEST_ASSERT_EQUAL_MESSAGE(4, n, "control_write_count -- measured pre-rewrite literal (CMD_ERASE)");
    TEST_ASSERT_EQUAL_HEX8_MESSAGE(0x80, control_write_value(0), "control write 0 -- measured pre-rewrite literal (regulator on, eprom_internal_erase:399)");
    TEST_ASSERT_EQUAL_HEX8_MESSAGE(0x90, control_write_value(1), "control write 1 -- measured pre-rewrite literal (first set_address; A17 forced for pins==28)");
    TEST_ASSERT_EQUAL_HEX8_MESSAGE(0x96, control_write_value(2), "control write 2 -- measured pre-rewrite literal (A9|VPE asserted for the erase pulse, eprom_internal_erase:402)");
    TEST_ASSERT_EQUAL_HEX8_MESSAGE(0x10, control_write_value(3), "control write 3 -- measured pre-rewrite literal (eprom_internal_erase's own disable at :409)");

    int last = control_write_value(n - 1);
    TEST_ASSERT_TRUE_MESSAGE(last >= 0, "the last CONTROL write must be a genuine, decodable value");
    TEST_ASSERT_TRUE_MESSAGE((last & CTRL_VPP_REGULATOR_ENABLE) == 0,
        "the LAST control value after CMD_ERASE must have CTRL_VPP_REGULATOR_ENABLE clear -- the property :409 provides today and must keep providing");
    TEST_ASSERT_TRUE_MESSAGE((last & CTRL_VPP_A9_ENABLE) == 0,
        "the LAST control value after CMD_ERASE must have CTRL_VPP_A9_ENABLE clear");
    TEST_ASSERT_TRUE_MESSAGE((last & CTRL_VPE_ENABLE) == 0,
        "the LAST control value after CMD_ERASE must have CTRL_VPE_ENABLE clear");
}

void test_vpp03_case_i_cmd_check_chip_id_control_stream_is_pinned_pre_rewrite(void) {
    rurp_get_config()->hardware_revision = REVISION_2_2;
    firestarter_handle_t h = make_vpp_handle(0x07, 28, 65536, 100, 13000, FLAG_SKIP_BLANK_CHECK, VPP_BUS_CONFIG_0x07);
    h.cmd = CMD_CHECK_CHIP_ID;  /* MUST be set before configure_memory so configure_eprom installs eprom_check_chip_id_execute as firestarter_operation_main */
    h.chip_id = 0xFFFF;  /* the value eprom_get_chip_id will read back: addresses 0x0000 and 0x0001 are both unseeded, and the read-back model returns 0xFF for an unseeded address (host_stubs.cpp's rurp_read_data_buffer) */
    set_mock_vpp_mv(13000);

    configure_memory(&h);
    reset_register_cache(0x00, 0x00, 0x00);
    clear_strobes();
    clear_timings();
    clear_logged_ids();
    h.firestarter_operation_main(&h);

    TEST_ASSERT_NOT_EQUAL_MESSAGE(RESPONSE_CODE_ERROR, h.response_code,
        "response_code must NOT be RESPONSE_CODE_ERROR -- proves the drive actually reached eprom_internal_check_chip_id's comparison (0xFFFF == 0xFFFF) rather than bailing out earlier");
    TEST_ASSERT_EQUAL_MESSAGE(0, strobe_overflowed(), "strobe_overflowed -- soundness precondition for the enumerated sequence below");

    /* Measured pre-rewrite baseline (D-15/A3): observed by running this case
     * against the UNCHANGED tree in this plan's task 2. */
    int n = control_write_count();
    TEST_ASSERT_EQUAL_MESSAGE(4, n, "control_write_count -- measured pre-rewrite literal (CMD_CHECK_CHIP_ID)");
    TEST_ASSERT_EQUAL_HEX8_MESSAGE(0x80, control_write_value(0), "control write 0 -- measured pre-rewrite literal (regulator on, eprom_get_chip_id:320)");
    TEST_ASSERT_EQUAL_HEX8_MESSAGE(0x82, control_write_value(1), "control write 1 -- measured pre-rewrite literal (A9 additionally asserted, eprom_get_chip_id:323)");
    TEST_ASSERT_EQUAL_HEX8_MESSAGE(0x92, control_write_value(2), "control write 2 -- measured pre-rewrite literal (first get_data's own set_address; A17 forced for pins==28)");
    TEST_ASSERT_EQUAL_HEX8_MESSAGE(0x10, control_write_value(3), "control write 3 -- measured pre-rewrite literal (eprom_get_chip_id's own disable at :327)");

    int last = control_write_value(n - 1);
    TEST_ASSERT_TRUE_MESSAGE(last >= 0, "the last CONTROL write must be a genuine, decodable value");
    TEST_ASSERT_TRUE_MESSAGE((last & CTRL_VPP_REGULATOR_ENABLE) == 0,
        "the LAST control value after CMD_CHECK_CHIP_ID must have CTRL_VPP_REGULATOR_ENABLE clear -- the property :327 provides today and must keep providing");
    TEST_ASSERT_TRUE_MESSAGE((last & CTRL_VPP_A9_ENABLE) == 0,
        "the LAST control value after CMD_CHECK_CHIP_ID must have CTRL_VPP_A9_ENABLE clear");
}

int main(int argc, char** argv) {
    (void)argc; (void)argv;
    UNITY_BEGIN();

    /* Plan 142-01 harness self-check (VPP-01..VPP-04 infrastructure) */
    RUN_TEST(test_setup_leaves_the_harness_clean_and_the_composites_correct);

    /* Plan 142-02 task 1 (VPP-01): (pins, revision) preserve-mask truth
     * table -- nine rows, RED-before-GREEN against unchanged memory.cpp --
     * plus the 32-pin non-EPROM byte-identity baseline (Group B). */
    RUN_TEST(test_vpp01_truthtable_pins28_rev2_2_drop_bit_present);
    RUN_TEST(test_vpp01_truthtable_pins28_rev1_drop_bit_present);
    RUN_TEST(test_vpp01_truthtable_pins32_rev2_0_drop_bit_present);
    RUN_TEST(test_vpp01_truthtable_pins32_rev2_2_drop_bit_present);
    RUN_TEST(test_vpp01_truthtable_pins32_rev2_3_drop_bit_present);
    RUN_TEST(test_vpp01_truthtable_pins32_rev1_drop_bit_absent);
    RUN_TEST(test_vpp01_truthtable_pins32_rev0_drop_bit_absent);
    RUN_TEST(test_vpp01_truthtable_pins32_revunknown_drop_bit_absent);
    RUN_TEST(test_vpp01_truthtable_pins32_rev2_2_preserve_never_introduces);
    RUN_TEST(test_vpp01_dip32_nonEprom_0x10_route_is_byte_identical_before_and_after);

    /* Plan 142-03 task 1 (VPP-04, D-13/D-15): the over-voltage refusal gate
     * VPP-04's own wording presumed already existed for the EPROM path --
     * confirmed false by grep (D-13). All of (a)/(b)/(c) are a REGRESSION
     * gate on behaviour that already holds (RESEARCH C-3, green on
     * arrival); (d) is the in-range control that proves the injection seam
     * changes the outcome. See task 3's planted violations V1-V3. */
    RUN_TEST(test_vpp04_a_overvoltage_refusal_fires_by_id_with_payload_shape);
    RUN_TEST(test_vpp04_b_no_hv_route_left_asserted_on_the_refusal_path);
    RUN_TEST(test_vpp04_c_flag_force_downgrades_to_warning_and_still_clears_the_route);
    RUN_TEST(test_vpp04_d_in_range_reading_fires_neither_error_nor_warning);

    /* Plan 142-03 task 2 (VPP-03, RESEARCH assumption A3): pre-rewrite
     * CMD_ERASE / CMD_CHECK_CHIP_ID control-value baselines -- NOT feature
     * tests, they pin the current stream so plan 142-04's composite-mask
     * conversion is a MEASURED no-op on the two commands PROJECT.md:189-190
     * protects. See task 3's planted violations V4/V5. */
    RUN_TEST(test_vpp03_case_e_cmd_erase_control_stream_is_pinned_pre_rewrite);
    RUN_TEST(test_vpp03_case_i_cmd_check_chip_id_control_stream_is_pinned_pre_rewrite);

    return UNITY_END();
}
