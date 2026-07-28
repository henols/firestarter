/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 *
 * Phase 12 Wave 0 — dispatch unit tests for configure_memory().
 *
 * One test per protocol in KNOWN_PROTOCOLS (build_db.py:89). Each test
 * constructs a minimal firestarter_handle_t (protocol, cmd, response_code)
 * and asserts `configure_memory()` does not raise RESPONSE_CODE_ERROR (i.e.
 * the chip resolved to a real handler).
 *
 * Phase 105 (protocol-only dispatch): dispatch is keyed on `protocol` alone
 * — there is no backward-compat fallback axis. Any unrecognized protocol,
 * including 0, reaches `configure_not_implemented()`; see
 * test_not_implemented.cpp for fail-closed coverage.
 *
 * Why TEST_ASSERT_NOT_EQUAL(RESPONSE_CODE_ERROR, ...) and not an operation-
 * pointer check? `configure_sram()` is a stub today and leaves the
 * firestarter_operation_init pointer NULL — pointer-set assertions would
 * spuriously fail. response_code is the robust dispatch-success signal.
 */

#include <Arduino.h>
#include <ArduinoFake.h>
#include <unity.h>
#include <stdio.h>

extern "C" {
#include "memory.h"
}
#include "firestarter.h"

using namespace fakeit;

void setUp(void) {
    ArduinoFakeReset();
    /* Stub Serial.write and Serial.flush so that LOG_ERROR_ID_* calls in the
     * error dispatch path (e.g. MSG_ERR_PROTOCOL_NOT_IMPLEMENTED) don't abort.
     * Dispatch tests never assert on serial output — only on response_code. */
    When(OverloadedMethod(ArduinoFake(Serial), write, size_t(uint8_t)))
        .AlwaysReturn(1);
    When(OverloadedMethod(ArduinoFake(Serial), write, size_t(const uint8_t*, size_t)))
        .AlwaysReturn(1);
    When(Method(ArduinoFake(Serial), flush)).AlwaysReturn();
}

void tearDown(void) {
}

/* Build a zero-initialized handle with only the three named fields set.
 * mem_type is retained as a vestigial (ignored) parameter to avoid
 * touching every call site now that firestarter_handle_t.mem_type is gone
 * (Phase 105 removal). */
static firestarter_handle_t make_handle(uint32_t protocol, uint8_t mem_type, uint8_t cmd) {
    (void)mem_type;
    firestarter_handle_t h = {};
    h.protocol = protocol;
    h.cmd = cmd;
    h.response_code = RESPONSE_CODE_OK;
    return h;
}

/* Positive dispatch tests — one per protocol in KNOWN_PROTOCOLS.
 * Each asserts that configure_memory() does NOT set response_code to
 * RESPONSE_CODE_ERROR (i.e. dispatch reached a real handler). */

void test_protocol_0x06_dispatches_nor_unlock(void) {
    firestarter_handle_t h = make_handle(0x06, 0, CMD_READ);
    configure_memory(&h);
    TEST_ASSERT_NOT_EQUAL(RESPONSE_CODE_ERROR, h.response_code);
}

void test_protocol_0x05_dispatches_5v_page(void) {
    firestarter_handle_t h = make_handle(0x05, 0, CMD_READ);
    configure_memory(&h);
    TEST_ASSERT_NOT_EQUAL(RESPONSE_CODE_ERROR, h.response_code);
}

void test_protocol_0x35_dispatches_5v_page(void) {
    firestarter_handle_t h = make_handle(0x35, 0, CMD_READ);
    configure_memory(&h);
    TEST_ASSERT_NOT_EQUAL(RESPONSE_CODE_ERROR, h.response_code);
}

void test_protocol_0x39_dispatches_5v_page(void) {
    firestarter_handle_t h = make_handle(0x39, 0, CMD_READ);
    configure_memory(&h);
    TEST_ASSERT_NOT_EQUAL(RESPONSE_CODE_ERROR, h.response_code);
}

void test_protocol_0x07_dispatches_eprom(void) {
    firestarter_handle_t h = make_handle(0x07, 0, CMD_READ);
    configure_memory(&h);
    TEST_ASSERT_NOT_EQUAL(RESPONSE_CODE_ERROR, h.response_code);
}

void test_protocol_0x08_dispatches_eprom(void) {
    firestarter_handle_t h = make_handle(0x08, 0, CMD_READ);
    configure_memory(&h);
    TEST_ASSERT_NOT_EQUAL(RESPONSE_CODE_ERROR, h.response_code);
}

void test_protocol_0x0B_dispatches_eprom(void) {
    firestarter_handle_t h = make_handle(0x0B, 0, CMD_READ);
    configure_memory(&h);
    TEST_ASSERT_NOT_EQUAL(RESPONSE_CODE_ERROR, h.response_code);
}

void test_protocol_0x0E_dispatches_sram(void) {
    firestarter_handle_t h = make_handle(0x0E, 0, CMD_READ);
    configure_memory(&h);
    TEST_ASSERT_NOT_EQUAL(RESPONSE_CODE_ERROR, h.response_code);
}

void test_protocol_0x27_dispatches_sram(void) {
    firestarter_handle_t h = make_handle(0x27, 0, CMD_READ);
    configure_memory(&h);
    TEST_ASSERT_NOT_EQUAL(RESPONSE_CODE_ERROR, h.response_code);
}

void test_protocol_0x28_dispatches_sram(void) {
    firestarter_handle_t h = make_handle(0x28, 0, CMD_READ);
    configure_memory(&h);
    TEST_ASSERT_NOT_EQUAL(RESPONSE_CODE_ERROR, h.response_code);
}

void test_protocol_0x29_dispatches_sram(void) {
    firestarter_handle_t h = make_handle(0x29, 0, CMD_READ);
    configure_memory(&h);
    TEST_ASSERT_NOT_EQUAL(RESPONSE_CODE_ERROR, h.response_code);
}

void test_protocol_0x10_dispatches_flash_intel(void) {
    firestarter_handle_t h = make_handle(0x10, 0, CMD_READ);
    configure_memory(&h);
    TEST_ASSERT_NOT_EQUAL(RESPONSE_CODE_ERROR, h.response_code);
}

void test_protocol_0x0D_dispatches_eeprom28c(void) {
    firestarter_handle_t h = make_handle(0x0D, 0, CMD_READ);
    configure_memory(&h);
    TEST_ASSERT_NOT_EQUAL(RESPONSE_CODE_ERROR, h.response_code);
}

/* FIX-02A (Phase 74 Plan 02): configure_flash_5v_page must handle CMD_CHECK_CHIP_ID
 * by setting a non-NULL operation_main pointer (mirroring configure_flash_nor_unlock).
 * These three tests are RED before the fix (no case in configure_flash_5v_page switch
 * → firestarter_operation_main stays NULL). */

void test_5v_page_check_chip_id_0x05_sets_operation(void) {
    firestarter_handle_t h = make_handle(0x05, 0, CMD_CHECK_CHIP_ID);
    configure_memory(&h);
    TEST_ASSERT_NOT_EQUAL_MESSAGE(RESPONSE_CODE_ERROR, h.response_code,
        "CMD_CHECK_CHIP_ID on 0x05 must not error");
    TEST_ASSERT_NOT_NULL_MESSAGE(h.firestarter_operation_main,
        "CMD_CHECK_CHIP_ID on 0x05 must set a non-NULL operation_main");
}

void test_5v_page_check_chip_id_0x35_sets_operation(void) {
    firestarter_handle_t h = make_handle(0x35, 0, CMD_CHECK_CHIP_ID);
    configure_memory(&h);
    TEST_ASSERT_NOT_EQUAL_MESSAGE(RESPONSE_CODE_ERROR, h.response_code,
        "CMD_CHECK_CHIP_ID on 0x35 must not error");
    TEST_ASSERT_NOT_NULL_MESSAGE(h.firestarter_operation_main,
        "CMD_CHECK_CHIP_ID on 0x35 must set a non-NULL operation_main");
}

void test_5v_page_check_chip_id_0x39_sets_operation(void) {
    firestarter_handle_t h = make_handle(0x39, 0, CMD_CHECK_CHIP_ID);
    configure_memory(&h);
    TEST_ASSERT_NOT_EQUAL_MESSAGE(RESPONSE_CODE_ERROR, h.response_code,
        "CMD_CHECK_CHIP_ID on 0x39 must not error");
    TEST_ASSERT_NOT_NULL_MESSAGE(h.firestarter_operation_main,
        "CMD_CHECK_CHIP_ID on 0x39 must set a non-NULL operation_main");
}

/* ─────────────────────────────────────────────────────────────────────────
 * v1.22 Phase 119 D-06/D-07/D-08 (119-07 Task 3) — the complete
 * command-by-protocol matrix enumerated as native cases, made possible by
 * Task 1 widening [env:native]/[env:native_nodevtools]'s build_src_filter
 * with operation_utils.cpp. RESEARCH F-E precomputed the full matrix, so
 * this is an enumeration to verify, not an exploration.
 *
 * One representative protocol value per family (every value within a
 * family routes to the IDENTICAL configure_* function -- see
 * firestarter/CLAUDE.md's dispatch-order table) EXCEPT where a group's own
 * members might plausibly diverge (SRAM's four ids, tested individually in
 * case group 5, since configure_sram's body is empty and any future
 * per-id divergence there is exactly the kind of regression this sweep
 * exists to catch).
 * ───────────────────────────────────────────────────────────────────────── */

struct protocol_family_row_t {
    uint32_t protocol;
    const char* family_name;
};

/* Walks configure_memory's protocol chain (memory.cpp:70-113) literally,
 * one row per KNOWN_PROTOCOLS entry -- table-driven so adding a protocol is
 * one row, not one function. */
static const protocol_family_row_t kAllProtocolFamilies[] = {
    {0x07, "eprom (0x07/0x08/0x0B)"},
    {0x08, "eprom (0x07/0x08/0x0B)"},
    {0x0B, "eprom (0x07/0x08/0x0B)"},
    {0x0D, "eeprom28c (0x0D)"},
    {0x10, "flash_intel (0x10)"},
    {0x06, "flash_nor_unlock (0x06)"},
    {0x05, "flash_5v_page (0x05/0x35/0x39)"},
    {0x35, "flash_5v_page (0x05/0x35/0x39)"},
    {0x39, "flash_5v_page (0x05/0x35/0x39)"},
    {0x0E, "sram (0x0E/0x27/0x28/0x29)"},
    {0x27, "sram (0x0E/0x27/0x28/0x29)"},
    {0x28, "sram (0x0E/0x27/0x28/0x29)"},
    {0x29, "sram (0x0E/0x27/0x28/0x29)"},
};
static const size_t kAllProtocolFamiliesCount = sizeof(kAllProtocolFamilies) / sizeof(kAllProtocolFamilies[0]);

/* Case group 1 — LOCK-04's positive safety invariant. This is the case that
 * would have caught LOCK-04's disproven literal mechanism: a blanket
 * `default:` arm added to configure_eeprom28c makes 0x0D's CMD_READ/
 * CMD_VERIFY rows fail here, since configure_memory pre-sets their generic
 * mains at memory.cpp:48-58 BEFORE the protocol chain runs. */
void test_case_group1_read_write_verify_never_null_main_for_any_protocol(void) {
    static const uint8_t cmds[] = {CMD_READ, CMD_WRITE, CMD_VERIFY};
    static const char* cmd_names[] = {"CMD_READ", "CMD_WRITE", "CMD_VERIFY"};
    for (size_t i = 0; i < kAllProtocolFamiliesCount; i++) {
        for (size_t c = 0; c < 3; c++) {
            firestarter_handle_t h = make_handle(kAllProtocolFamilies[i].protocol, 0, cmds[c]);
            configure_memory(&h);
            char msg[224];
            snprintf(msg, sizeof(msg),
                "Case group 1 (LOCK-04 positive invariant): %s on protocol 0x%02X (%s) must leave "
                "firestarter_operation_main NON-NULL -- this is the case a blanket default: arm in "
                "any configure_* handler would fail",
                cmd_names[c], (unsigned)kAllProtocolFamilies[i].protocol,
                kAllProtocolFamilies[i].family_name);
            TEST_ASSERT_NOT_NULL_MESSAGE(h.firestarter_operation_main, msg);
        }
    }
}

/* Case group 2 — LOCK-04's fail-closed claim. Every protocol OTHER THAN
 * 0x0D must leave CMD_SDP_UNLOCK/CMD_SDP_LOCK NULL-main, so the op-layer
 * guard refuses them -- LOCK-04's intent satisfied by D-06's generic guard
 * rather than by a per-handler default: arm, and provably total because it
 * needs no per-handler maintenance. */
void test_case_group2_sdp_cmds_null_main_for_every_non_0x0d_protocol(void) {
    for (size_t i = 0; i < kAllProtocolFamiliesCount; i++) {
        uint32_t protocol = kAllProtocolFamilies[i].protocol;
        if (protocol == 0x0D) {
            continue;
        }

        firestarter_handle_t h_unlock = make_handle(protocol, 0, CMD_SDP_UNLOCK);
        configure_memory(&h_unlock);
        char msg_u[224];
        snprintf(msg_u, sizeof(msg_u),
            "Case group 2 (LOCK-04 fail-closed, D-06): CMD_SDP_UNLOCK on protocol 0x%02X (%s) must "
            "leave firestarter_operation_main NULL -- refused by the generic op-layer guard, never "
            "by a per-handler default: arm",
            (unsigned)protocol, kAllProtocolFamilies[i].family_name);
        TEST_ASSERT_NULL_MESSAGE(h_unlock.firestarter_operation_main, msg_u);

        firestarter_handle_t h_lock = make_handle(protocol, 0, CMD_SDP_LOCK);
        configure_memory(&h_lock);
        char msg_l[224];
        snprintf(msg_l, sizeof(msg_l),
            "Case group 2 (LOCK-04 fail-closed, D-06): CMD_SDP_LOCK on protocol 0x%02X (%s) must "
            "leave firestarter_operation_main NULL",
            (unsigned)protocol, kAllProtocolFamilies[i].family_name);
        TEST_ASSERT_NULL_MESSAGE(h_lock.firestarter_operation_main, msg_l);
    }
}

/* Case group 3 — LOCK-02's dispatch half. On 0x0D, CMD_SDP_UNLOCK/
 * CMD_SDP_LOCK must set a non-NULL main and leave init/end NULL. RESEARCH
 * F-T's correction: NULL init/end does NOT mean those phases are skipped --
 * _execute_operation_house_keeping_func still calls op_wait_for_ack() and
 * still emits the INIT/END frame pairs. What is genuinely absent is the
 * DONE round-trip and any '#' data frame -- "no data payload, no DONE
 * round-trip", not "no INIT/END". */
void test_case_group3_sdp_cmds_dispatch_on_0x0d_with_null_init_end(void) {
    firestarter_handle_t h_unlock = make_handle(0x0D, 0, CMD_SDP_UNLOCK);
    configure_memory(&h_unlock);
    TEST_ASSERT_NOT_NULL_MESSAGE(h_unlock.firestarter_operation_main,
        "Case group 3 (LOCK-02): CMD_SDP_UNLOCK on 0x0D must set a non-NULL operation_main");
    TEST_ASSERT_NULL_MESSAGE(h_unlock.firestarter_operation_init,
        "Case group 3 (LOCK-02, F-T correction): CMD_SDP_UNLOCK's init is NULL -- this does NOT "
        "mean the INIT phase is skipped; _execute_operation_house_keeping_func still calls "
        "op_wait_for_ack() and still emits the INIT/END frame pair. What is genuinely absent is the "
        "DONE round-trip and any '#' data frame");
    TEST_ASSERT_NULL_MESSAGE(h_unlock.firestarter_operation_end,
        "Case group 3 (LOCK-02, F-T correction): CMD_SDP_UNLOCK's end is NULL, same correction as "
        "init above");

    firestarter_handle_t h_lock = make_handle(0x0D, 0, CMD_SDP_LOCK);
    configure_memory(&h_lock);
    TEST_ASSERT_NOT_NULL_MESSAGE(h_lock.firestarter_operation_main,
        "Case group 3 (LOCK-02): CMD_SDP_LOCK on 0x0D must set a non-NULL operation_main");
    TEST_ASSERT_NULL_MESSAGE(h_lock.firestarter_operation_init,
        "Case group 3 (LOCK-02, F-T correction): CMD_SDP_LOCK's init is NULL, same correction as "
        "unlock above");
    TEST_ASSERT_NULL_MESSAGE(h_lock.firestarter_operation_end,
        "Case group 3 (LOCK-02, F-T correction): CMD_SDP_LOCK's end is NULL, same correction as "
        "unlock above");
}

/* Case group 4 — DEVTEST-01's firmware half and the 0x0D gaps. */
void test_case_group4_0x0d_erase_and_chip_id_null_main_devtest01(void) {
    firestarter_handle_t h_erase = make_handle(0x0D, 0, CMD_ERASE);
    configure_memory(&h_erase);
    TEST_ASSERT_NULL_MESSAGE(h_erase.firestarter_operation_main,
        "Case group 4 (DEVTEST-01 fw half): CMD_ERASE on 0x0D must leave firestarter_operation_main "
        "NULL -- configure_eeprom28c has no case CMD_ERASE: arm, so this is now refused by the "
        "generic op-layer guard rather than silently reporting OK having erased nothing ('dev test' "
        "phantom erase)");

    firestarter_handle_t h_chip_id = make_handle(0x0D, 0, CMD_CHECK_CHIP_ID);
    configure_memory(&h_chip_id);
    TEST_ASSERT_NULL_MESSAGE(h_chip_id.firestarter_operation_main,
        "Case group 4: CMD_CHECK_CHIP_ID on 0x0D also leaves firestarter_operation_main NULL -- also "
        "a phantom today, honestly qualified: eprom_check_chip_id already refuses earlier with "
        "MSG_ERR_NO_CHIP_ID when handle->chip_id == 0, and TRACE-05 pinned chip_id_check: false "
        "across all 84 algorithm==13 DB entries, so in practice the host never sends a non-zero "
        "chip id for 0x0D and this cell is already refused upstream -- this guard's coverage here "
        "is real but not the primary mitigation, so this is not over-claimed as the fix for this "
        "cell");
}

/* Case group 5 — the newly-refused non-0x0D cells, enumerated: the SRAM
 * group's CMD_ERASE, CMD_BLANK_CHECK and CMD_CHECK_CHIP_ID. configure_sram's
 * body is literally just a debug log, which is why these were silent OKs
 * before this task. Tested per-id (not one representative) since
 * configure_sram is the one handler with zero per-command logic to diverge
 * on. */
void test_case_group5_sram_erase_blank_check_chip_id_null_main(void) {
    static const uint32_t sram_protocols[] = {0x0E, 0x27, 0x28, 0x29};
    for (size_t i = 0; i < 4; i++) {
        uint32_t protocol = sram_protocols[i];
        char msg[288];

        firestarter_handle_t h_erase = make_handle(protocol, 0, CMD_ERASE);
        configure_memory(&h_erase);
        snprintf(msg, sizeof(msg),
            "Case group 5: CMD_ERASE on SRAM protocol 0x%02X must leave firestarter_operation_main "
            "NULL -- configure_sram's body is literally just a debug log",
            (unsigned)protocol);
        TEST_ASSERT_NULL_MESSAGE(h_erase.firestarter_operation_main, msg);

        firestarter_handle_t h_blank = make_handle(protocol, 0, CMD_BLANK_CHECK);
        configure_memory(&h_blank);
        snprintf(msg, sizeof(msg),
            "Case group 5: CMD_BLANK_CHECK on SRAM protocol 0x%02X must leave "
            "firestarter_operation_main NULL at THIS guard -- the host's _SRAM_PROTO_IDS workaround "
            "in eprom_operations.py short-circuits check_eprom_blank BEFORE any firmware command is "
            "issued, so this guard is not reachable from that call path; it does NOT become dead "
            "code (it fires earlier and gives a materially better message) -- correct Phase 120 "
            "disposition is KEEP, not deleted, not touched here",
            (unsigned)protocol);
        TEST_ASSERT_NULL_MESSAGE(h_blank.firestarter_operation_main, msg);

        firestarter_handle_t h_chip_id = make_handle(protocol, 0, CMD_CHECK_CHIP_ID);
        configure_memory(&h_chip_id);
        snprintf(msg, sizeof(msg),
            "Case group 5: CMD_CHECK_CHIP_ID on SRAM protocol 0x%02X must leave "
            "firestarter_operation_main NULL, subject to the same upstream chip_id==0 gate noted "
            "for 0x0D in case group 4",
            (unsigned)protocol);
        TEST_ASSERT_NULL_MESSAGE(h_chip_id.firestarter_operation_main, msg);
    }
}

/* Case group 6 — the unchanged path. Lets a reviewer SEE the absence of a
 * regression rather than infer it: configure_not_implemented protocols set
 * response_code = RESPONSE_CODE_ERROR themselves, so op_execute_function
 * already returns false and parse_json already emits MSG_ERR_SETUP -- the
 * op layer is never reached here, so this task's guard changes nothing. */
void test_case_group6_not_implemented_protocol_unchanged_no_double_error(void) {
    firestarter_handle_t h = make_handle(0x11, 0, CMD_READ);
    configure_memory(&h);
    TEST_ASSERT_EQUAL_MESSAGE(RESPONSE_CODE_ERROR, h.response_code,
        "Case group 6 (D-08 item 7): a configure_not_implemented protocol (0x11) must still produce "
        "RESPONSE_CODE_ERROR from configure_memory itself -- op_execute_function(configure_memory, "
        "...) already returns false and parse_json already emits MSG_ERR_SETUP; the op layer is "
        "NEVER reached for this protocol -- no double error, no new frame");
    TEST_ASSERT_NULL_MESSAGE(h.firestarter_operation_main,
        "Case group 6: configure_not_implemented leaves firestarter_operation_main NULL, unchanged "
        "by this task");
}

int main(int argc, char** argv) {
    (void)argc;
    (void)argv;
    UNITY_BEGIN();

    /* 13 protocol-positive tests (one per KNOWN_PROTOCOLS entry) */
    RUN_TEST(test_protocol_0x06_dispatches_nor_unlock);
    RUN_TEST(test_protocol_0x05_dispatches_5v_page);
    RUN_TEST(test_protocol_0x35_dispatches_5v_page);
    RUN_TEST(test_protocol_0x39_dispatches_5v_page);
    RUN_TEST(test_protocol_0x07_dispatches_eprom);
    RUN_TEST(test_protocol_0x08_dispatches_eprom);
    RUN_TEST(test_protocol_0x0B_dispatches_eprom);
    RUN_TEST(test_protocol_0x0E_dispatches_sram);
    RUN_TEST(test_protocol_0x27_dispatches_sram);
    RUN_TEST(test_protocol_0x28_dispatches_sram);
    RUN_TEST(test_protocol_0x29_dispatches_sram);
    RUN_TEST(test_protocol_0x10_dispatches_flash_intel);
    RUN_TEST(test_protocol_0x0D_dispatches_eeprom28c);

    /* FIX-02A: CMD_CHECK_CHIP_ID dispatch tests (RED before flash_5v_page.cpp fix) */
    RUN_TEST(test_5v_page_check_chip_id_0x05_sets_operation);
    RUN_TEST(test_5v_page_check_chip_id_0x35_sets_operation);
    RUN_TEST(test_5v_page_check_chip_id_0x39_sets_operation);

    /* v1.22 Phase 119 D-06/D-07/D-08 (119-07 Task 3): the complete
     * command-by-protocol matrix, enumerated as native cases. */
    RUN_TEST(test_case_group1_read_write_verify_never_null_main_for_any_protocol);
    RUN_TEST(test_case_group2_sdp_cmds_null_main_for_every_non_0x0d_protocol);
    RUN_TEST(test_case_group3_sdp_cmds_dispatch_on_0x0d_with_null_init_end);
    RUN_TEST(test_case_group4_0x0d_erase_and_chip_id_null_main_devtest01);
    RUN_TEST(test_case_group5_sram_erase_blank_check_chip_id_null_main);
    RUN_TEST(test_case_group6_not_implemented_protocol_unchanged_no_double_error);

    return UNITY_END();
}
