/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 *
 * Phase 116 Plan 05 — the always-green SDP harness suite (D-03).
 *
 * Executable proof that:
 *  (1) the ordered strobe recorder (116-01's HOST_STUBS_REAL_REGISTER_UTILS)
 *      captures the real production register-cache elision, including the
 *      interleaving of data bytes, latch strobes, and /CE + /OE edges
 *      (TRACE-01);
 *  (2) the harness can tell UNLOCK from LOCK from ERASE, via two index-precise
 *      planted-fault negatives (TRACE-03a/b);
 *  (3) the outcome-independent identity-gate assertions retired from
 *      test_eeprom28c_chip_id now execute in CI, on an address-keyed mock
 *      (TRACE-04).
 *
 * This suite drives flash_util_byte_flipping / memory_set_data DIRECTLY for
 * its stream cases (Tasks 1-2), and drives eeprom28c_write_init in its two
 * migrated identity cases (Task 3) -- both of which are outcome-INDEPENDENT
 * of the Phase 117 fix (test_migrated_mismatching_chip_id_errors early-
 * returns before the SDP sequence; test_migrated_zero_chip_id_skips_check
 * asserts a per-address read counter, never the SDP outcome), which is why
 * the suite stays green by construction across that fix. The parked RED
 * suite (plan 116-06) is the one that flips RED->GREEN when that fix lands.
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

/* FIX-05 (D-11, plan 117-04): EEPROM_SDP_DISABLE is DEFINED in
 * src/proms/eeprom_28c.cpp, which [env:native] links into every test binary
 * (build_src_filter = +<proms/>, test_build_src = yes). Plan 117-02 granted
 * this array external linkage (a prior extern declaration in that TU) so
 * this guard can pin the PRODUCTION table directly, not a transcription. */
extern const byte_flip_t EEPROM_SDP_DISABLE[6];

#include "../_shared/sdp_bus_config.h"
#include "../_shared/sdp_expected.h"

using namespace fakeit;

/* host_stubs.cpp's reset seam (D-05) — must run after configure_memory, which
 * itself writes address 0 (mem_util_set_address(handle, 0), memory.cpp:68). */
extern "C" void reset_register_cache(uint8_t lsb, uint8_t msb, rurp_register_t ctrl);

/* ─────────────────────────────────────────────────────────────────────────
 * setUp / tearDown
 * ───────────────────────────────────────────────────────────────────────── */

/* TRACE-04 (Pattern 3) — address-keyed mock state, reset per-case in setUp(). */
static uint32_t s_mfr_addr_keyed;
static uint8_t  s_mfr_hi_keyed;
static uint8_t  s_mfr_lo_keyed;
static int      s_reads_at_mfr_addr;
static int      s_reads_at_poll_addr;

void setUp(void) {
    ArduinoFakeReset();
    When(OverloadedMethod(ArduinoFake(Serial), write, size_t(uint8_t))).AlwaysReturn(1);
    When(OverloadedMethod(ArduinoFake(Serial), write, size_t(const uint8_t*, size_t))).AlwaysReturn(1);
    When(Method(ArduinoFake(Serial), flush)).AlwaysReturn();
    /* REQUIRED by D-05: the real rurp_register_utils.h calls delayMicroseconds
     * (rurp_internal_write_to_register:86 and the settle path :58), and
     * eeprom28c_check_chip_id / eeprom28c_wait_for_write call delay() /
     * delayMicroseconds() too. ArduinoFake ABORTS (SIGABRT) on any unmocked
     * virtual — this reads exactly like the D-13 Unity-teardown flake, but a
     * SIGABRT in a NEW suite is this (Pitfall 3), not that. Do not remove
     * these as "unused" — they are load-bearing. Plan 118-04's OBS-04
     * duration bracket adds two micros() reads around
     * eeprom28c_emit_command_sequence's call inside eeprom28c_write_init, so
     * micros() joins this load-bearing set too: a fixed value (elapsed 0)
     * keeps this always-green harness suite's behaviour unchanged, since
     * none of its cases exercise the AT28C_TBLC_MAX_US budget path. */
    When(Method(ArduinoFake(), delayMicroseconds)).AlwaysReturn();
    When(Method(ArduinoFake(), delay)).AlwaysReturn();
    When(Method(ArduinoFake(), millis)).AlwaysReturn(0);
    When(Method(ArduinoFake(), micros)).AlwaysReturn(0);

    clear_strobes();
    reset_register_cache(0x00, 0x00, 0x00);

    s_mfr_addr_keyed = 0;
    s_mfr_hi_keyed = 0xFF;
    s_mfr_lo_keyed = 0xFF;
    s_reads_at_mfr_addr = 0;
    s_reads_at_poll_addr = 0;
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
    h.chip_id = 0;
    h.mem_size = row.mem_size;
    h.bus_config = row.bus_config;
    h.ctrl_flags = FLAG_SKIP_BLANK_CHECK;
    return h;
}

/* Load-bearing order: configure_memory (which itself writes address 0) ->
 * reset_register_cache -> clear_strobes -> flash_util_byte_flipping. The
 * cache reset and strobe clear MUST both come after configure_memory
 * (test_val_5v_page.cpp:150-175 records this same hazard). ctrl_seed=0x00 is
 * what makes the 54-entry SHIPPED array correct: flash_util_byte_flipping's
 * two CTRL_READ_WRITE clears then produce no CONTROL entry because the
 * cached value is already 0x00 (unchanged). */
static void drive(firestarter_handle_t* h, const byte_flip_t* table, size_t len, rurp_register_t ctrl_seed) {
    configure_memory(h);
    reset_register_cache(0x00, 0x00, ctrl_seed);
    clear_strobes();
    flash_util_byte_flipping(h, table, len);
}

/* The FIX-01 reference emitter: h->firestarter_set_data is memory_set_data
 * (assigned by configure_memory), which routes through
 * mem_util_remap_address_bus -- the remap-aware target stream, with zero
 * hand derivation. */
static void drive_reference_emitter(firestarter_handle_t* h, const byte_flip_t* table, size_t len, rurp_register_t ctrl_seed) {
    configure_memory(h);
    reset_register_cache(0x00, 0x00, ctrl_seed);
    clear_strobes();
    for (size_t i = 0; i < len; i++) {
        h->firestarter_set_data(h, table[i].address, table[i].byte);
    }
}

/* FIX-05 (D-11) table-comparison helper: positional element-by-element
 * comparison ONLY -- no counting, no containment scan, following the
 * assertion discipline recorded at _shared/sdp_expected.h:63 and :83-85
 * ("Never counts anything ... every comparison is positional"). Two arrays
 * are "identical" here only if EVERY element's address AND byte match. */
static bool sdp_tables_identical(const byte_flip_t* a, const byte_flip_t* b, size_t len) {
    for (size_t i = 0; i < len; i++) {
        if (a[i].address != b[i].address || a[i].byte != b[i].byte) {
            return false;
        }
    }
    return true;
}

/* The single most valuable diagnostic in this phase (116-RESEARCH.md
 * §"Confirming the elision empirically"): pio test swallows printf from test
 * bodies, so run the built binary directly
 * (.pio/build/native/firestarter_native) to see this. Guarded behind
 * SDP_TRACE_DUMP -- kept in the suite for Phase 117's benefit, never compiled
 * by default. */
#ifdef SDP_TRACE_DUMP
static void dump_strobes(const char* tag) {
    printf("##### %s total=%d overflow=%d\n", tag, strobe_count(), strobe_overflowed());
    for (int i = 0; i < strobe_count(); i++) {
        if (strobe_kind(i) == STROBE_KIND_DATA) {
            printf("[%3d] DATA 0x%02X\n", i, strobe_value(i));
        } else {
            printf("[%3d] PIN  0x%02X -> %d\n", i, strobe_pin(i), strobe_value(i));
        }
    }
}
#endif

/* ─────────────────────────────────────────────────────────────────────────
 * Task 1 — ordered capture (TRACE-01, D-03, D-06)
 * ───────────────────────────────────────────────────────────────────────── */

void test_case1_ordered_capture_dip28_28c256(void) {
    firestarter_handle_t h = make_sdp_handle(SDP_BUS_CONFIGS[0]); /* AT28C256 / DIP28_28C256 */
    drive(&h, FLASH_DISABLE_WRITE_PROTECTION, 6, 0x00);
#ifdef SDP_TRACE_DUMP
    dump_strobes("case1_dip28_28c256_shipped");
#endif
    sdp_assert_stream_equals(SDP_SHIPPED_DIP28_28C256, SDP_SHIPPED_DIP28_28C256_LEN,
        "Case 1: ordered capture, DIP28_28C256, FLASH_DISABLE_WRITE_PROTECTION (== EEPROM_SDP_DISABLE, 116-03 parity)");
}

void test_case2_elision_is_real(void) {
    /* A raw call-log golden would assert 6 phantom entries here (Pitfall 4) —
     * write #4 targets the same address as write #3, so LSB/MSB are cache-
     * elided and only the payload DATA + OE + CE edges remain. */
    firestarter_handle_t h = make_sdp_handle(SDP_BUS_CONFIGS[0]);
    drive(&h, FLASH_DISABLE_WRITE_PROTECTION, 6, 0x00);
    TEST_ASSERT_EQUAL_MESSAGE(0, strobe_overflowed(), "Case 2: stream must not have overflowed");
    TEST_ASSERT_EQUAL_MESSAGE(STROBE_KIND_DATA, strobe_kind(30),
        "Case 2: index 30 must be a DATA entry -- write #4 emits no address latch (cache hit)");
    TEST_ASSERT_EQUAL_HEX8_MESSAGE(0xAA, strobe_value(30),
        "Case 2: index 30's payload must be 0xAA -- write #4's data byte");
}

void test_case3_ce_oe_edges_distinguishable(void) {
    /* Positional indices from the expected array (write #1's OE/CE triple),
     * not a scan -- distinguishes OE from CE by the `pin` field. */
    firestarter_handle_t h = make_sdp_handle(SDP_BUS_CONFIGS[0]);
    drive(&h, FLASH_DISABLE_WRITE_PROTECTION, 6, 0x00);

    TEST_ASSERT_EQUAL_MESSAGE(STROBE_KIND_PIN, strobe_kind(7), "Case 3: index 7 must be a PIN entry (/OE)");
    TEST_ASSERT_EQUAL_MESSAGE(OUTPUT_ENABLE, strobe_pin(7), "Case 3: index 7 must be OUTPUT_ENABLE");
    TEST_ASSERT_EQUAL_MESSAGE(1, strobe_value(7), "Case 3: /OE asserts high (rurp_chip_output enables output)");

    TEST_ASSERT_EQUAL_MESSAGE(STROBE_KIND_PIN, strobe_kind(8), "Case 3: index 8 must be a PIN entry (/CE low)");
    TEST_ASSERT_EQUAL_MESSAGE(CHIP_ENABLE, strobe_pin(8), "Case 3: index 8 must be CHIP_ENABLE");
    TEST_ASSERT_EQUAL_MESSAGE(0, strobe_value(8), "Case 3: /CE asserts low (rurp_chip_enable)");

    TEST_ASSERT_EQUAL_MESSAGE(STROBE_KIND_PIN, strobe_kind(9), "Case 3: index 9 must be a PIN entry (/CE high)");
    TEST_ASSERT_EQUAL_MESSAGE(CHIP_ENABLE, strobe_pin(9), "Case 3: index 9 must be CHIP_ENABLE");
    TEST_ASSERT_EQUAL_MESSAGE(1, strobe_value(9), "Case 3: /CE deasserts high (rurp_chip_disable)");
}

/* ─────────────────────────────────────────────────────────────────────────
 * Task 2 — TRACE-03a/b in-suite negatives + LOCK-05 + fixed-stream guards
 * ───────────────────────────────────────────────────────────────────────── */

/* TRACE-03a: the six-write unlock table with the terminal byte mutated from
 * the SDP-disable value (0x20) to the chip-erase value (0x10) -- a one-nibble
 * slip that turns SDP-disable into chip erase (see FLASH_ERASE vs
 * FLASH_DISABLE_WRITE_PROTECTION in flash_utils.h -- they differ ONLY in
 * this terminal byte). This planted table is retained as the MUTATION
 * FIXTURE for two consumers: the stream-level negative below
 * (test_negativeA_...) and FIX-05's anti-hollow planted-violation case
 * further below (D-11, plan 117-04), which reuses it rather than adding a
 * second copy. The production EEPROM_SDP_DISABLE array is now referenced
 * DIRECTLY by FIX-05's constant-level guard (plan 117-02 granted it external
 * linkage for exactly this purpose) -- this table stays a deliberate,
 * self-contained fixture, not a stand-in for it. */
static const byte_flip_t TEST_UNLOCK_MUTATED_TERMINAL[] = {
    {0x5555, 0xAA},
    {0x2AAA, 0x55},
    {0x5555, 0x80},
    {0x5555, 0xAA},
    {0x2AAA, 0x55},
    {0x5555, 0x10}, /* mutated: 0x20 (SDP-disable) -> 0x10 (chip-erase) */
};

void test_negativeA_unlock_mutated_diverges_and_matches_erase(void) {
    firestarter_handle_t h1 = make_sdp_handle(SDP_BUS_CONFIGS[0]);
    drive(&h1, TEST_UNLOCK_MUTATED_TERMINAL, 6, 0x00);

    int div = sdp_first_divergence(SDP_SHIPPED_DIP28_28C256, SDP_SHIPPED_DIP28_28C256_LEN);
    TEST_ASSERT_NOT_EQUAL_MESSAGE(-1, div,
        "Negative A (i): mutated-terminal-byte stream must diverge from the shipped SDP-disable stream");
    TEST_ASSERT_EQUAL_MESSAGE(50, div,
        "Negative A (i): divergence must be at index 50 -- write #6's payload byte (0x10 vs 0x20)");

    /* Clause (ii), the stronger claim: the mutated stream must be IDENTICAL
     * to driving the real FLASH_ERASE table -- a one-nibble terminal-byte
     * slip turns SDP-disable into chip erase, machine-visibly, one phase
     * before FIX-04 formalises the guard. Snapshot first: drive() clears the
     * recorder before the second drive. */
    sdp_strobe_t mutated_snapshot[64];
    int mutated_len = sdp_snapshot(mutated_snapshot, 64);

    firestarter_handle_t h2 = make_sdp_handle(SDP_BUS_CONFIGS[0]);
    drive(&h2, FLASH_ERASE, sizeof(FLASH_ERASE) / sizeof(FLASH_ERASE[0]), 0x00);

    TEST_ASSERT_EQUAL_MESSAGE(-1, sdp_first_divergence(mutated_snapshot, mutated_len),
        "Negative A (ii): mutated-unlock stream must be element-wise IDENTICAL to the real FLASH_ERASE stream");
    sdp_assert_stream_equals(mutated_snapshot, mutated_len,
        "Negative A (ii): mutated-unlock == real FLASH_ERASE (one-nibble hazard, machine-visible)");
}

/* TRACE-03b: drive the three-write FLASH_ENABLE_WRITE_PROTECTION (lock /
 * write-prefix) table where the six-write unlock stream is expected. */
void test_negativeB_lock_table_swapped_for_write_prefix(void) {
    firestarter_handle_t h = make_sdp_handle(SDP_BUS_CONFIGS[0]);
    drive(&h, FLASH_ENABLE_WRITE_PROTECTION,
        sizeof(FLASH_ENABLE_WRITE_PROTECTION) / sizeof(FLASH_ENABLE_WRITE_PROTECTION[0]), 0x00);

    int div = sdp_first_divergence(SDP_SHIPPED_DIP28_28C256, SDP_SHIPPED_DIP28_28C256_LEN);
    TEST_ASSERT_EQUAL_MESSAGE(26, div,
        "Negative B: three-write lock/write-prefix table must diverge from the six-write unlock "
        "stream at index 26 -- write #3's payload byte (0xA0 vs 0x80)");
}

/* LOCK-05 finding, recorded as a case (not prose): FLASH_ENABLE_WRITE_PROTECTION
 * and FLASH_ENABLE_WRITE are byte-identical tables in flash_utils.h (Atmel
 * doc0270 section 19 note 2 -- this duplication is datasheet-correct).
 * Phase 119 LOCK-05 requires the duplication be PRESERVED, not deduplicated.
 * A trace-based negative between THESE TWO SPECIFIC tables is therefore
 * impossible by construction -- a later editor must not try to add one. */
void test_lock05_enable_write_and_write_protection_identical(void) {
    firestarter_handle_t h1 = make_sdp_handle(SDP_BUS_CONFIGS[0]);
    drive(&h1, FLASH_ENABLE_WRITE_PROTECTION,
        sizeof(FLASH_ENABLE_WRITE_PROTECTION) / sizeof(FLASH_ENABLE_WRITE_PROTECTION[0]), 0x00);
    sdp_strobe_t snap[32];
    int len = sdp_snapshot(snap, 32);

    firestarter_handle_t h2 = make_sdp_handle(SDP_BUS_CONFIGS[0]);
    drive(&h2, FLASH_ENABLE_WRITE, sizeof(FLASH_ENABLE_WRITE) / sizeof(FLASH_ENABLE_WRITE[0]), 0x00);

    TEST_ASSERT_EQUAL_MESSAGE(-1, sdp_first_divergence(snap, len),
        "LOCK-05: FLASH_ENABLE_WRITE_PROTECTION and FLASH_ENABLE_WRITE are byte-identical tables and "
        "must therefore produce element-wise identical streams");
    sdp_assert_stream_equals(snap, len, "LOCK-05: identity between the two 3-write tables");
}

/* FIX-05 (D-10/D-11, plan 117-04): the constant-level formalisation of the
 * one-nibble chip-erase hazard test_negativeA_... already proves at the
 * STREAM level -- here it is proven directly on the two SOURCE TABLES, no
 * bus drive required. FLASH_ERASE is AA-55-80-AA-55-10; EEPROM_SDP_DISABLE
 * is AA-55-80-AA-55-20 -- they differ by ONE NIBBLE in ONE BYTE, and one of
 * them erases the whole chip (research SUMMARY.md Critical Pitfalls #3).
 *
 * Validation ceiling (D-10/D-11 caveat, must NOT be leaned on): AT28C
 * chip-erase requires OE = V_H = 12V, a rail 0x0D never routes on this
 * hardware -- but that fact is Atmel-specific and is recorded here only as a
 * MITIGATING comment, never as the guard's safety argument, because the
 * 0x0D bucket spans 20+ manufacturers whose erase gating may differ. */
void test_fix05_terminal_byte_and_table_identity_guards(void) {
    /* (1) Length sanity -- every table this guard reasons about is 6
     * elements; a length surprise would silently invalidate every index
     * below. */
    TEST_ASSERT_EQUAL_MESSAGE(6, sizeof(EEPROM_SDP_DISABLE) / sizeof(EEPROM_SDP_DISABLE[0]),
        "FIX-05: EEPROM_SDP_DISABLE must be a 6-element table");
    TEST_ASSERT_EQUAL_MESSAGE(6, sizeof(FLASH_ERASE) / sizeof(FLASH_ERASE[0]),
        "FIX-05: FLASH_ERASE must be a 6-element table");
    TEST_ASSERT_EQUAL_MESSAGE(6, sizeof(FLASH_DISABLE_WRITE_PROTECTION) / sizeof(FLASH_DISABLE_WRITE_PROTECTION[0]),
        "FIX-05: FLASH_DISABLE_WRITE_PROTECTION must be a 6-element table");

    /* (2) EEPROM_SDP_DISABLE's terminal byte, pinned on the PRODUCTION array
     * (external linkage, plan 117-02) -- not a transcription. */
    TEST_ASSERT_EQUAL_HEX8_MESSAGE(0x20, EEPROM_SDP_DISABLE[5].byte,
        "FIX-05: EEPROM_SDP_DISABLE's terminal byte must be 0x20 (SDP-disable) -- if this fails, "
        "the production 0x0D write path may now emit a chip-erase command");
    TEST_ASSERT_EQUAL_HEX32_MESSAGE(0x5555, EEPROM_SDP_DISABLE[5].address,
        "FIX-05: EEPROM_SDP_DISABLE's terminal address must be 0x5555");

    /* (3) FLASH_ERASE's terminal byte, the chip-erase value this guard
     * exists to distinguish EEPROM_SDP_DISABLE from. */
    TEST_ASSERT_EQUAL_HEX8_MESSAGE(0x10, FLASH_ERASE[5].byte,
        "FIX-05: FLASH_ERASE's terminal byte must be 0x10 (chip-erase)");
    TEST_ASSERT_EQUAL_HEX32_MESSAGE(0x5555, FLASH_ERASE[5].address,
        "FIX-05: FLASH_ERASE's terminal address must be 0x5555");

    /* (4) Distinctness: the two terminal bytes must differ, AND the two
     * arrays must be distinct OBJECTS -- a future refactor that made
     * EEPROM_SDP_DISABLE an alias of FLASH_ERASE (or vice versa) would pass
     * every value-level assertion above while erasing every chip on write. */
    TEST_ASSERT_NOT_EQUAL_MESSAGE(FLASH_ERASE[5].byte, EEPROM_SDP_DISABLE[5].byte,
        "FIX-05: FLASH_ERASE and EEPROM_SDP_DISABLE terminal bytes must differ");
    TEST_ASSERT_NOT_EQUAL_MESSAGE((const void*)EEPROM_SDP_DISABLE, (const void*)FLASH_ERASE,
        "FIX-05: EEPROM_SDP_DISABLE and FLASH_ERASE must be distinct array objects, not aliases");

    /* (5) The one-nibble claim, made literal: elements 0-4 match on BOTH
     * address and byte; element 5's address matches while its byte differs.
     * So the two tables differ at exactly one field of exactly one element. */
    for (size_t i = 0; i < 5; i++) {
        TEST_ASSERT_EQUAL_HEX32_MESSAGE(FLASH_ERASE[i].address, EEPROM_SDP_DISABLE[i].address,
            "FIX-05: elements 0-4 must match address between FLASH_ERASE and EEPROM_SDP_DISABLE");
        TEST_ASSERT_EQUAL_HEX8_MESSAGE(FLASH_ERASE[i].byte, EEPROM_SDP_DISABLE[i].byte,
            "FIX-05: elements 0-4 must match byte between FLASH_ERASE and EEPROM_SDP_DISABLE");
    }
    TEST_ASSERT_EQUAL_HEX32_MESSAGE(FLASH_ERASE[5].address, EEPROM_SDP_DISABLE[5].address,
        "FIX-05: element 5's address must still match -- only the byte differs");
    TEST_ASSERT_NOT_EQUAL_MESSAGE(FLASH_ERASE[5].byte, EEPROM_SDP_DISABLE[5].byte,
        "FIX-05: element 5's byte must differ -- the one-nibble hazard, machine-checked");

    /* (6) D-11's cross-guard: EEPROM_SDP_DISABLE must stay byte-identical to
     * FLASH_DISABLE_WRITE_PROTECTION. D-10 deliberately keeps EEPROM_SDP_DISABLE
     * as a 0x0D-local duplicate rather than driving the FIX-04-frozen
     * flash_utils.h directly, and Phase 119's LOCK-05 deliberately preserves
     * an analogous duplicate rather than deduping -- so this assertion is the
     * ONLY thing standing between that deliberate duplication and a silent
     * divergence. FLASH_DISABLE_WRITE_PROTECTION is the table every
     * SDP_FIXED_* golden and every reference-emitter guard in this suite is
     * driven from (drive_reference_emitter, above); if EEPROM_SDP_DISABLE
     * ever diverges from it, production and the oracle this harness compares
     * against have silently split. */
    TEST_ASSERT_TRUE_MESSAGE(sdp_tables_identical(EEPROM_SDP_DISABLE, FLASH_DISABLE_WRITE_PROTECTION, 6),
        "FIX-05/D-11: EEPROM_SDP_DISABLE must stay byte-identical to FLASH_DISABLE_WRITE_PROTECTION -- "
        "the production 0x0D-local table has diverged from the table this harness's goldens are driven "
        "from, and D-10's deliberate duplication is no longer safe");
}

/* FIX-05 anti-hollow counterpart (this project's standing rule: every gate
 * ships a planted-violation fixture proving the gate can actually fail).
 * Reuses TEST_UNLOCK_MUTATED_TERMINAL (above) rather than adding a second
 * planted table -- one planted table, two consumers. Proves clause (6) of
 * the guard above is not vacuous: sdp_tables_identical() CAN return false,
 * and it does so specifically because a one-nibble slip turns the
 * SDP-disable table into the chip-erase table, at the constant level,
 * matching what test_negativeA_... already proves at the stream level. */
void test_fix05_guard_rejects_planted_terminal_mutation(void) {
    TEST_ASSERT_FALSE_MESSAGE(sdp_tables_identical(TEST_UNLOCK_MUTATED_TERMINAL, EEPROM_SDP_DISABLE, 6),
        "FIX-05 anti-hollow: sdp_tables_identical must REJECT the planted terminal-byte mutation -- "
        "if this passes, the constant-level guard's D-11 cross-check clause is hollow");
    TEST_ASSERT_EQUAL_HEX32_MESSAGE(TEST_UNLOCK_MUTATED_TERMINAL[5].address, EEPROM_SDP_DISABLE[5].address,
        "FIX-05 anti-hollow: the planted mutation must match address at element 5 -- only the byte differs");
    TEST_ASSERT_NOT_EQUAL_MESSAGE(TEST_UNLOCK_MUTATED_TERMINAL[5].byte, EEPROM_SDP_DISABLE[5].byte,
        "FIX-05 anti-hollow: the planted mutation's element-5 byte must differ from EEPROM_SDP_DISABLE's");
    TEST_ASSERT_EQUAL_HEX8_MESSAGE(FLASH_ERASE[5].byte, TEST_UNLOCK_MUTATED_TERMINAL[5].byte,
        "FIX-05 anti-hollow: the planted one-nibble slip must turn the SDP-disable table into exactly "
        "the FLASH_ERASE terminal byte -- the constant-level twin of test_negativeA_...'s stream-level proof");
}

/* Fixed-stream reference-emitter guards -- one per SDP_BUS_CONFIGS row (5).
 * Green today AND after Phase 117 (memory_set_data is untouched by that fix),
 * so this pins the SDP_FIXED_* literals to real production behaviour
 * permanently, while leaving the parked suite (116-06) as the sole
 * RED-to-GREEN signal. */
void test_fixed_guard_at28c256(void) {
    firestarter_handle_t h = make_sdp_handle(SDP_BUS_CONFIGS[0]); /* AT28C256 */
    drive_reference_emitter(&h, FLASH_DISABLE_WRITE_PROTECTION, 6, 0x00);
    sdp_assert_stream_equals(SDP_FIXED_DIP28_28C256, SDP_FIXED_DIP28_28C256_LEN,
        "reference-emitter guard: AT28C256 / DIP28_28C256");
}

void test_fixed_guard_at28c64(void) {
    firestarter_handle_t h = make_sdp_handle(SDP_BUS_CONFIGS[1]); /* AT28C64 */
    drive_reference_emitter(&h, FLASH_DISABLE_WRITE_PROTECTION, 6, 0x00);
    sdp_assert_stream_equals(SDP_FIXED_DIP28_28C64, SDP_FIXED_DIP28_28C64_LEN,
        "reference-emitter guard: AT28C64 / DIP28_28C64");
}

void test_fixed_guard_at28c16(void) {
    firestarter_handle_t h = make_sdp_handle(SDP_BUS_CONFIGS[2]); /* AT28C16 */
    drive_reference_emitter(&h, FLASH_DISABLE_WRITE_PROTECTION, 6, 0x00);
    sdp_assert_stream_equals(SDP_FIXED_DIP24_2816, SDP_FIXED_DIP24_2816_LEN,
        "reference-emitter guard: AT28C16 / DIP24_2816");
}

void test_fixed_guard_at28c010(void) {
    firestarter_handle_t h = make_sdp_handle(SDP_BUS_CONFIGS[3]); /* AT28C010 */
    drive_reference_emitter(&h, FLASH_DISABLE_WRITE_PROTECTION, 6, 0x00);
    sdp_assert_stream_equals(SDP_FIXED_DIP32_28C512_EEPROM, SDP_FIXED_DIP32_28C512_EEPROM_LEN,
        "reference-emitter guard: AT28C010 / DIP32_28C512_EEPROM");
}

void test_fixed_guard_at28c040(void) {
    /* AT28C040 shares AT28C010's bus_config byte-for-byte (116-02 D-09) --
     * Pitfall 5 / CORRECTION 3: on this pinout, under a zero CONTROL seed,
     * shipped and fixed address bytes are IDENTICAL (only the /OE-edge
     * reorder distinguishes them), which is why plan 116-06's DIP32 RED
     * cases must use a deliberately stale upper-address seed rather than a
     * plain trace -- see 116-05-SUMMARY.md. */
    firestarter_handle_t h = make_sdp_handle(SDP_BUS_CONFIGS[4]); /* AT28C040 */
    drive_reference_emitter(&h, FLASH_DISABLE_WRITE_PROTECTION, 6, 0x00);
    sdp_assert_stream_equals(SDP_FIXED_DIP32_28C512_EEPROM, SDP_FIXED_DIP32_28C512_EEPROM_LEN,
        "reference-emitter guard: AT28C040 / DIP32_28C512_EEPROM");
}

/* ─────────────────────────────────────────────────────────────────────────
 * Task 3 — TRACE-04: address-keyed mock, migrated identity-gate assertions
 * ───────────────────────────────────────────────────────────────────────── */

/* Pattern 3: dispatch on ADDRESS, not call order. Virgin 0xFF everywhere
 * except the two planted manufacturer/device identity bytes. Two per-address
 * read counters (mfr / SDP-completion-poll @ 0x5555) let any previously
 * call-ordinal assertion be re-expressed positionally. */
static void mock_set_data_keyed(firestarter_handle_t*, uint32_t, uint8_t) {}
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
        /* Post-FIX-02: eeprom28c_wait_for_sdp_completion polls this address
         * for a bounded DQ6 toggle-bit settle, never an expected-byte
         * equality. A constant 0xFF return reads as "settled immediately"
         * (two consecutive samples agree) -- the fixed code deliberately
         * draws NO conclusion from that (D-05): it never writes
         * response_code from this poll, on any path. */
        return 0xFF;
    }
    return 0xFF;
}

static firestarter_handle_t make_identity_handle(uint16_t expected_chip_id, uint32_t ctrl_flags) {
    firestarter_handle_t h = {};
    h.protocol = 0x0D;
    h.cmd = CMD_WRITE;
    h.mem_size = 32768; /* AT28C256 -- mfr_addr = mem_size - 64 = 0x7FC0 */
    h.response_code = RESPONSE_CODE_OK;
    h.chip_id = expected_chip_id;
    h.ctrl_flags = ctrl_flags | FLAG_SKIP_BLANK_CHECK;
    return h;
}

/* Mismatching identity: early-returns before the SDP sequence at all
 * (eeprom28c_write_init's `if (response_code == ERROR) return;` right after
 * eeprom28c_check_chip_id), so this is outcome-independent of the Phase 117
 * SDP-sequence fix and safe to run always-green. */
void test_migrated_mismatching_chip_id_errors(void) {
    s_mfr_addr_keyed = 32768 - 64; /* 0x7FC0 */
    s_mfr_hi_keyed = 0xDE;
    s_mfr_lo_keyed = 0xAD;
    firestarter_handle_t h = make_identity_handle(0x1F08, 0);
    configure_memory(&h);
    /* configure_memory() overwrites BOTH firestarter_get_data AND
     * firestarter_set_data (Pattern 3) -- the retired suite's own comment
     * covered only get_data. Re-assign both. */
    h.firestarter_get_data = mock_get_data_keyed;
    h.firestarter_set_data = mock_set_data_keyed;
    h.firestarter_operation_init(&h);
    TEST_ASSERT_EQUAL_MESSAGE(RESPONSE_CODE_ERROR, h.response_code,
        "migrated: mismatching identity must ERROR -- early-return before the SDP sequence, "
        "outcome-independent of the Phase 117 fix");
}

/* Zero chip_id: the identity gate evaluates false, eeprom28c_check_chip_id is
 * never called. Re-expressed (D-12/Pattern 3) as a per-address read counter
 * since the retired suite's call-ordinal byte-index vehicle no longer exists under an
 * address-keyed mock -- the intent ("the helper was not called") is preserved
 * and is now independent of the SDP outcome (measured 116-RESEARCH.md §F8:
 * mfr=0, poll=2000, total=2000). */
void test_migrated_zero_chip_id_skips_check(void) {
    s_mfr_addr_keyed = 32768 - 64;
    s_mfr_hi_keyed = 0xFF;
    s_mfr_lo_keyed = 0xFF;
    firestarter_handle_t h = make_identity_handle(0, 0);
    configure_memory(&h);
    h.firestarter_get_data = mock_get_data_keyed;
    h.firestarter_set_data = mock_set_data_keyed;
    h.firestarter_operation_init(&h);
    TEST_ASSERT_EQUAL_MESSAGE(0, s_reads_at_mfr_addr,
        "migrated: zero chip_id must skip eeprom28c_check_chip_id entirely -- re-expressed as a "
        "per-address read counter (Pattern 3), independent of the SDP outcome");
}

/* ─────────────────────────────────────────────────────────────────────────
 * main
 * ───────────────────────────────────────────────────────────────────────── */

int main(int argc, char** argv) {
    (void)argc; (void)argv;
    UNITY_BEGIN();

    /* Task 1 */
    RUN_TEST(test_case1_ordered_capture_dip28_28c256);
    RUN_TEST(test_case2_elision_is_real);
    RUN_TEST(test_case3_ce_oe_edges_distinguishable);

    /* Task 2 */
    RUN_TEST(test_negativeA_unlock_mutated_diverges_and_matches_erase);
    RUN_TEST(test_negativeB_lock_table_swapped_for_write_prefix);
    RUN_TEST(test_lock05_enable_write_and_write_protection_identical);
    RUN_TEST(test_fix05_terminal_byte_and_table_identity_guards);
    RUN_TEST(test_fix05_guard_rejects_planted_terminal_mutation);
    RUN_TEST(test_fixed_guard_at28c256);
    RUN_TEST(test_fixed_guard_at28c64);
    RUN_TEST(test_fixed_guard_at28c16);
    RUN_TEST(test_fixed_guard_at28c010);
    RUN_TEST(test_fixed_guard_at28c040);

    /* Task 3 */
    RUN_TEST(test_migrated_mismatching_chip_id_errors);
    RUN_TEST(test_migrated_zero_chip_id_skips_check);

    return UNITY_END();
}
