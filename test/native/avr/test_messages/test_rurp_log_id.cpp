/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 *
 * Phase 6 — native Unity tests for rurp_log_id() wire frame.
 *
 * Asserts the exact byte sequence emitted by rurp_log_id() against the
 * locked frame contract from CONTEXT §D-01..D-04:
 *
 *     AA 55 AA 55 | len=1+param_count+1 | id | params | crc8 | 0A
 *
 * The CRC8 algorithm (poly 0x07, seed 0x00, no reflection, no final XOR)
 * is pinned by `test_crc_polynomial_smoke` — any silent refactor that
 * changes the polynomial fails this suite.
 *
 * Test cases:
 *  - test_zero_param_frame:  id=0x01, no params. Asserts CRC(0x01) == 0x07.
 *  - test_u32_param_frame:   id=0x4E, params={0x00,0x01,0x00,0x00}.
 *  - test_multi_param_frame: id=0xB1, params={0x01,0xF4,0xA2,0x05,0x00,0x03}.
 *  - test_crc_polynomial_smoke: independent ref CRC vs frame CRC for an
 *    arbitrary payload — pins poly 0x07 seed 0x00.
 *
 * Build context: [env:native] src_filter is widened in platformio.ini to
 * include `boards/rurp_serial_utils.cpp` + `messages.c`. The production
 * _firestarter_emit_frame + CRC8 table + MSG_PARAM_BYTES_TABLE are linked
 * directly into the test binary (no test-side reimplementation).
 *
 * Serial bytes are captured via ArduinoFake's Method(Serial, write) mock —
 * one .AlwaysDo handler accumulates every write into a host std::vector.
 */

#include <Arduino.h>
#include <ArduinoFake.h>
#include <unity.h>

#include <vector>
#include <cstdint>

extern "C" {
#include "rurp_shield.h"
#include "messages.h"
}

using namespace fakeit;

// Capture buffer shared by all tests; cleared in setUp.
static std::vector<uint8_t> captured;

void setUp(void) {
    ArduinoFakeReset();
    captured.clear();

    // Mock every SERIAL_PORT.write(uint8_t) — accumulate into `captured`.
    // SerialFake has two write overloads (single-byte and buffer-form); use
    // OverloadedMethod to pick the single-byte one explicitly.
    When(OverloadedMethod(ArduinoFake(Serial), write, size_t(uint8_t)))
        .AlwaysDo([](uint8_t b) -> size_t {
            captured.push_back(b);
            return (size_t)1;
        });

    // .flush() is no-op-safe; stub explicitly so ArduinoFake doesn't warn.
    When(Method(ArduinoFake(Serial), flush)).AlwaysReturn();
}

void tearDown(void) {
}

// --- Reference CRC8 (poly 0x07, seed 0x00, no refl, no XOR). Table-free
// recomputation so the test is fully independent of CRC8_TABLE in
// rurp_serial_utils.cpp. If the production table ever drifts off-spec, this
// reference disagrees with the frame's CRC byte and the test fails. ---
static uint8_t ref_crc8(const uint8_t* data, size_t n) {
    uint8_t crc = 0;
    for (size_t i = 0; i < n; i++) {
        crc ^= data[i];
        for (int k = 0; k < 8; k++) {
            crc = (crc & 0x80) ? (uint8_t)((crc << 1) ^ 0x07) : (uint8_t)(crc << 1);
        }
    }
    return crc;
}

void test_zero_param_frame(void) {
    rurp_log_id(0x01, NULL, 0);

    // 4 magic + 1 len + 1 id + 1 crc + 1 anchor = 8 bytes.
    TEST_ASSERT_EQUAL_size_t(8, captured.size());

    TEST_ASSERT_EQUAL_HEX8(0xAA, captured[0]);
    TEST_ASSERT_EQUAL_HEX8(0x55, captured[1]);
    TEST_ASSERT_EQUAL_HEX8(0xAA, captured[2]);
    TEST_ASSERT_EQUAL_HEX8(0x55, captured[3]);
    TEST_ASSERT_EQUAL_HEX8(0x02, captured[4]);    // len = 1 (id) + 0 (params) + 1 (crc)
    TEST_ASSERT_EQUAL_HEX8(0x01, captured[5]);    // id

    // CRC over [0x01] = 0x07 — pins the polynomial choice (D-03).
    TEST_ASSERT_EQUAL_HEX8(0x07, captured[6]);

    // Also verify against the table-free reference (defence-in-depth).
    uint8_t body[1] = { 0x01 };
    TEST_ASSERT_EQUAL_HEX8(ref_crc8(body, 1), captured[6]);

    TEST_ASSERT_EQUAL_HEX8(0x0A, captured[7]);    // re-sync anchor
}

void test_u32_param_frame(void) {
    // MSG_INFO_MEM_SIZE (id=0x4E) with u32=0x00010000 encoded MSB-first.
    uint8_t params[4] = { 0x00, 0x01, 0x00, 0x00 };
    rurp_log_id(MSG_INFO_MEM_SIZE, params, 4);

    // 4 magic + 1 len + 1 id + 4 params + 1 crc + 1 anchor = 12 bytes.
    TEST_ASSERT_EQUAL_size_t(12, captured.size());

    // Magic preamble.
    TEST_ASSERT_EQUAL_HEX8(0xAA, captured[0]);
    TEST_ASSERT_EQUAL_HEX8(0x55, captured[1]);
    TEST_ASSERT_EQUAL_HEX8(0xAA, captured[2]);
    TEST_ASSERT_EQUAL_HEX8(0x55, captured[3]);

    // len = 1 (id) + 4 (params) + 1 (crc) = 0x06.
    TEST_ASSERT_EQUAL_HEX8(0x06, captured[4]);

    // id.
    TEST_ASSERT_EQUAL_HEX8(0x4E, captured[5]);
    TEST_ASSERT_EQUAL_HEX8((uint8_t)MSG_INFO_MEM_SIZE, captured[5]);

    // Params.
    TEST_ASSERT_EQUAL_HEX8(0x00, captured[6]);
    TEST_ASSERT_EQUAL_HEX8(0x01, captured[7]);
    TEST_ASSERT_EQUAL_HEX8(0x00, captured[8]);
    TEST_ASSERT_EQUAL_HEX8(0x00, captured[9]);

    // CRC over [0x4E, 0x00, 0x01, 0x00, 0x00] — table-free reference.
    uint8_t body[5] = { 0x4E, 0x00, 0x01, 0x00, 0x00 };
    TEST_ASSERT_EQUAL_HEX8(ref_crc8(body, 5), captured[10]);

    // Anchor.
    TEST_ASSERT_EQUAL_HEX8(0x0A, captured[11]);
}

void test_multi_param_frame(void) {
    // id=0xB1 (MSG_ERR_WRITE_FAILED) with u24=0x01F4A2 + u8=0x05 + u16=0x0003,
    // each encoded MSB-first by the caller. 6 param bytes total.
    uint8_t params[6] = { 0x01, 0xF4, 0xA2, 0x05, 0x00, 0x03 };
    rurp_log_id(0xB1, params, 6);

    // 4 + 1 + 1 + 6 + 1 + 1 = 14 bytes.
    TEST_ASSERT_EQUAL_size_t(14, captured.size());

    // Magic.
    TEST_ASSERT_EQUAL_HEX8(0xAA, captured[0]);
    TEST_ASSERT_EQUAL_HEX8(0x55, captured[1]);
    TEST_ASSERT_EQUAL_HEX8(0xAA, captured[2]);
    TEST_ASSERT_EQUAL_HEX8(0x55, captured[3]);

    // len = 1 + 6 + 1 = 0x08.
    TEST_ASSERT_EQUAL_HEX8(0x08, captured[4]);

    // id.
    TEST_ASSERT_EQUAL_HEX8(0xB1, captured[5]);

    // Params.
    TEST_ASSERT_EQUAL_HEX8(0x01, captured[6]);
    TEST_ASSERT_EQUAL_HEX8(0xF4, captured[7]);
    TEST_ASSERT_EQUAL_HEX8(0xA2, captured[8]);
    TEST_ASSERT_EQUAL_HEX8(0x05, captured[9]);
    TEST_ASSERT_EQUAL_HEX8(0x00, captured[10]);
    TEST_ASSERT_EQUAL_HEX8(0x03, captured[11]);

    // CRC over [0xB1, 0x01, 0xF4, 0xA2, 0x05, 0x00, 0x03].
    uint8_t body[7] = { 0xB1, 0x01, 0xF4, 0xA2, 0x05, 0x00, 0x03 };
    TEST_ASSERT_EQUAL_HEX8(ref_crc8(body, 7), captured[12]);

    // Anchor.
    TEST_ASSERT_EQUAL_HEX8(0x0A, captured[13]);
}

void test_crc_polynomial_smoke(void) {
    // Independent CRC computation vs the frame's embedded CRC byte. If the
    // production CRC8_TABLE is ever regenerated with the wrong polynomial,
    // seed, reflection, or final XOR, the two values disagree.
    uint8_t params[4] = { 0x12, 0x34, 0x56, 0x78 };
    rurp_log_id(0x4E, params, 4);

    TEST_ASSERT_EQUAL_size_t(12, captured.size());

    uint8_t body[5] = { 0x4E, 0x12, 0x34, 0x56, 0x78 };
    uint8_t expected_crc = ref_crc8(body, 5);

    // CRC is the second-to-last byte (anchor 0x0A is the last).
    TEST_ASSERT_EQUAL_HEX8(expected_crc, captured[10]);
    TEST_ASSERT_EQUAL_HEX8(0x0A, captured[11]);
}

void test_oversize_param_count_rejected(void) {
    // Phase 6 WR-02: _firestarter_emit_frame must refuse param_count values
    // that would wrap the length byte. `len = 1 (id) + param_count + 1 (crc)`
    // overflows for param_count >= 254 (254 + 2 == 256 → 0). The guard drops
    // the frame silently rather than emit a wrap-corrupted length prefix that
    // the host decoder would parse as a shorter body, producing desync.
    //
    // Dummy params buffer — only the count matters; nothing is read past the
    // guard. Sized at 254 to match the boundary value under test.
    uint8_t params[254];
    memset(params, 0xCC, sizeof(params));

    rurp_log_id(0x01, params, 254);

    // Strict invariant: zero serial bytes captured. If any byte landed on the
    // wire, the guard let an unsafe frame through.
    TEST_ASSERT_EQUAL_size_t(0, captured.size());

    // Also pin the 255 case explicitly — same expectation.
    rurp_log_id(0x01, params, 255);
    TEST_ASSERT_EQUAL_size_t(0, captured.size());

    // Defence-in-depth: the boundary just below the guard (253) MUST still
    // emit a well-formed frame so we know the cutoff is exact, not
    // off-by-one. 253 params → 4 magic + 1 len + 1 id + 253 params + 1 crc
    // + 1 anchor = 261 bytes. len = 1 + 253 + 1 = 255 (0xFF, max valid).
    rurp_log_id(0x01, params, 253);
    TEST_ASSERT_EQUAL_size_t(261, captured.size());
    TEST_ASSERT_EQUAL_HEX8(0xFF, captured[4]);   // len = 255
    TEST_ASSERT_EQUAL_HEX8(0x01, captured[5]);   // id
    TEST_ASSERT_EQUAL_HEX8(0x0A, captured[260]); // anchor
}

int main(int argc, char** argv) {
    (void)argc;
    (void)argv;
    UNITY_BEGIN();

    RUN_TEST(test_zero_param_frame);
    RUN_TEST(test_u32_param_frame);
    RUN_TEST(test_multi_param_frame);
    RUN_TEST(test_crc_polynomial_smoke);
    RUN_TEST(test_oversize_param_count_rejected);

    return UNITY_END();
}
