/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 */
#include <avr/pgmspace.h>

#include "rurp_serial_utils.h"
#include "rurp_shield.h"

// Phase 9: deleted the two legacy text-prefix log helpers (RAM body +
// PROGMEM body). See 09-CONTEXT.md D-02.

void rurp_serial_begin(unsigned long baud) {
    SERIAL_PORT.begin(baud);
    while (!SERIAL_PORT) {
        delayMicroseconds(1);
    }
    delay(50);
}

void rurp_serial_end() {
    SERIAL_PORT.end();
    delay(5);
}

int rurp_communication_available() {
    return SERIAL_PORT.available();
}

int rurp_communication_read() {
    return SERIAL_PORT.read();
}

int rurp_communication_peak() {
    return SERIAL_PORT.peek();
}

size_t rurp_communication_read_bytes(char* buffer, size_t size) {
    return SERIAL_PORT.readBytes(buffer, size);
}

// Phase 50 Plan 02: streaming COBS decode-in-place + CRC8 verify + drain-to-0x00 resync.
//
// Frame contract: [COBS(payload + CRC8(payload))][0x00 delimiter]
// (The '#' marker is consumed by the caller before this function is called.)
//
// Algorithm (decode-in-place, no second ~512 B buffer — FRAME-03 / Pattern 2):
//
//   The logical COBS-encoded stream represents [payload | CRC8_byte].  We use
//   a 1-byte output lookahead (`last_byte`) so the final decoded byte (the
//   CRC8) never needs to be written to buffer[], keeping out ≤ DATA_BUFFER_SIZE
//   even for a payload of exactly DATA_BUFFER_SIZE bytes.
//
//   Key invariant: every decoded byte is "queued" by calling push_decoded_byte()
//   which commits the PREVIOUS `last_byte` to buffer[out] and holds the new
//   byte in `last_byte`.  When the 0x00 delimiter arrives, `last_byte` = CRC8
//   (it was never committed).
//
//   Implicit-zero rule: after a non-254 run completes, an implicit 0x00 follows
//   the run data in the decoded stream — BUT only if more encoded data follows
//   (i.e. NOT at stream end).  We defer the decision using `implicit_zero_pending`:
//   set it when a non-254 run ends, and emit the zero (via push_decoded_byte(0))
//   when the next run-code arrives (confirming we are not at stream end).  When
//   the 0x00 delimiter arrives, `implicit_zero_pending` is simply discarded.
//
//   State (~6 B stack):
//     out                   — committed payload bytes in buffer[]
//     block_remaining       — data bytes remaining in current COBS run
//     was_254_run           — current run started with 0xFF (no implicit zero)
//     implicit_zero_pending — a deferred implicit zero from the last run
//     has_last              — `last_byte` holds a valid unwritten decoded byte
//     last_byte             — 1-byte output lookahead
//
//   Overflow guard (T-50-01): if out == DATA_BUFFER_SIZE on a commit attempt,
//   drain to the next 0x00 and return -2 (payload too large).
//   Error invariant (Pattern 3 / D-06): on ANY COBS/CRC failure, drain bytes
//   up to AND INCLUDING the next 0x00 so the RX cursor re-anchors at a frame
//   boundary.
//
// SC1 win: the 2 s timeout_ms loop is GONE; frame boundary = 0x00 delimiter.
// Negative-code contract: callers check res<0 only (Assumption A4).

/* Forward declaration: crc8_ccitt is defined below with the PROGMEM table. */
static uint8_t crc8_ccitt(uint8_t crc, uint8_t b);

static void _drain_to_delimiter(void) {
    /* Consume bytes up to and including the next 0x00 delimiter to re-anchor
     * the RX cursor at a frame boundary (Pattern 3 / D-06). */
    while (1) {
        while (rurp_communication_available() <= 0) {}
        int d = rurp_communication_read();
        if (d < 0 || (uint8_t)d == 0x00) {
            break;
        }
    }
}

int rurp_communication_read_data(char* buffer) {
    size_t out = 0;                   /* committed payload bytes in buffer[]         */
    uint8_t block_remaining = 0;      /* data bytes remaining in current COBS run    */
    bool was_254_run = false;         /* current run started with 0xFF (no impl zero) */
    bool implicit_zero_pending = false; /* deferred implicit zero from last run       */
    bool has_last = false;            /* `last_byte` holds a valid unwritten byte     */
    uint8_t last_byte = 0;            /* 1-byte output lookahead                     */

    /* push_decoded_byte: commit previous `last_byte` to buffer, hold `b` as the
     * new `last_byte`.  Returns false and drains on overflow. */
#define PUSH(b_)                                                   \
    do {                                                           \
        if (has_last) {                                            \
            if (out >= DATA_BUFFER_SIZE) {                         \
                _drain_to_delimiter();                             \
                return -2;                                         \
            }                                                      \
            buffer[out++] = (char)last_byte;                       \
        }                                                          \
        last_byte = (b_);                                          \
        has_last = true;                                           \
    } while (0)

    while (1) {
        /* Delimiter-driven: spin until a byte is available. */
        while (rurp_communication_available() <= 0) {}

        int b = rurp_communication_read();
        if (b < 0) {
            _drain_to_delimiter();
            return -1; /* read() underrun */
        }
        uint8_t byte = (uint8_t)b;

        if (byte == 0x00) {
            /* Frame delimiter — end of encoded stream. */
            if (block_remaining != 0) {
                /* 0x00 mid-run: COBS violation. Delimiter consumed; no drain. */
                return -3;
            }
            /* `implicit_zero_pending` is discarded: it is the trailing zero
             * that COBS omits at stream end.  `last_byte` IS the CRC8. */
            break;
        }

        if (block_remaining > 0) {
            /* Data byte inside current run. */
            PUSH(byte);
            block_remaining--;
            if (block_remaining == 0 && !was_254_run) {
                implicit_zero_pending = true;
            }
        } else {
            /* Run-code byte (block_remaining == 0, not a delimiter). */
            /* The run-code's arrival confirms any pending implicit zero is
             * non-trailing (more data follows), so emit it now. */
            if (implicit_zero_pending) {
                PUSH(0);
                implicit_zero_pending = false;
            }
            was_254_run = (byte == 0xFF);
            block_remaining = byte - 1;
            /* Run code 0x01: no data bytes, one deferred implicit zero.
             * Flag it the same way as a completed non-254 run. */
            if (block_remaining == 0 && !was_254_run) {
                implicit_zero_pending = true;
            }
        }
    }

#undef PUSH

    /* --- Normal frame end --- */
    if (!has_last) {
        /* Empty frame — no CRC byte decoded. */
        return -1;
    }
    uint8_t rcvd_crc = last_byte; /* 1-byte lookahead holds the CRC8 */

    /* Recompute CRC8-CCITT over the decoded payload using the EXISTING PROGMEM
     * table accessor (D-05 / CRC-01 — UNCHANGED, no new CRC routine). */
    uint8_t computed_crc = 0;
    for (size_t i = 0; i < out; i++) {
        computed_crc = crc8_ccitt(computed_crc, (uint8_t)buffer[i]);
    }
    if (computed_crc != rcvd_crc) {
        /* CRC8 mismatch. Delimiter already consumed — no further drain needed. */
        return -4;
    }

    return (int)out;
}

size_t rurp_communication_write(const char* buffer, size_t size) {
    uint8_t checksum = 0;
    for (size_t i = 0; i < size; i++) {
        checksum ^= buffer[i];
    }

    SERIAL_PORT.write(size >> 8);
    SERIAL_PORT.write(size & 0xFF);
    SERIAL_PORT.write(checksum);
    size_t bytes = SERIAL_PORT.write(buffer, size);
    SERIAL_PORT.flush();
    return bytes;
}

// --- Phase 6: ID-encoded log frame emitter (CONTEXT §D-01..D-04) ---
//
// Wire frame layout (9+ bytes, W-04 u16 len):
//     bytes 0..3 : 0xAA 0x55 0xAA 0x55         (magic preamble)
//     bytes 4..5 : len_u16 = 1 + param_count + 1, big-endian MSB first (id + params + crc)
//     byte 6     : id
//     bytes 7..N : params (raw, MSB-first per type encoded by caller)
//     byte N+1   : crc8 over [id, params] — poly 0x07, seed 0x00, no refl, no XOR
//     byte N+2   : 0x0A re-sync anchor (NOT a delimiter; len is authoritative)

// 4-byte magic preamble: alternating-bit pattern, statistically incompatible
// with single-byte PORTD address-line patterns on the Uno.
static const uint8_t MAGIC_PREAMBLE[4] PROGMEM = { 0xAA, 0x55, 0xAA, 0x55 };

// CRC8-CCITT (poly 0x07, seed 0x00) — precomputed table. Sanity: t[0^0x01] = t[1] = 0x07.
static const uint8_t CRC8_TABLE[256] PROGMEM = {
    0x00, 0x07, 0x0E, 0x09, 0x1C, 0x1B, 0x12, 0x15, 0x38, 0x3F, 0x36, 0x31, 0x24, 0x23, 0x2A, 0x2D,
    0x70, 0x77, 0x7E, 0x79, 0x6C, 0x6B, 0x62, 0x65, 0x48, 0x4F, 0x46, 0x41, 0x54, 0x53, 0x5A, 0x5D,
    0xE0, 0xE7, 0xEE, 0xE9, 0xFC, 0xFB, 0xF2, 0xF5, 0xD8, 0xDF, 0xD6, 0xD1, 0xC4, 0xC3, 0xCA, 0xCD,
    0x90, 0x97, 0x9E, 0x99, 0x8C, 0x8B, 0x82, 0x85, 0xA8, 0xAF, 0xA6, 0xA1, 0xB4, 0xB3, 0xBA, 0xBD,
    0xC7, 0xC0, 0xC9, 0xCE, 0xDB, 0xDC, 0xD5, 0xD2, 0xFF, 0xF8, 0xF1, 0xF6, 0xE3, 0xE4, 0xED, 0xEA,
    0xB7, 0xB0, 0xB9, 0xBE, 0xAB, 0xAC, 0xA5, 0xA2, 0x8F, 0x88, 0x81, 0x86, 0x93, 0x94, 0x9D, 0x9A,
    0x27, 0x20, 0x29, 0x2E, 0x3B, 0x3C, 0x35, 0x32, 0x1F, 0x18, 0x11, 0x16, 0x03, 0x04, 0x0D, 0x0A,
    0x57, 0x50, 0x59, 0x5E, 0x4B, 0x4C, 0x45, 0x42, 0x6F, 0x68, 0x61, 0x66, 0x73, 0x74, 0x7D, 0x7A,
    0x89, 0x8E, 0x87, 0x80, 0x95, 0x92, 0x9B, 0x9C, 0xB1, 0xB6, 0xBF, 0xB8, 0xAD, 0xAA, 0xA3, 0xA4,
    0xF9, 0xFE, 0xF7, 0xF0, 0xE5, 0xE2, 0xEB, 0xEC, 0xC1, 0xC6, 0xCF, 0xC8, 0xDD, 0xDA, 0xD3, 0xD4,
    0x69, 0x6E, 0x67, 0x60, 0x75, 0x72, 0x7B, 0x7C, 0x51, 0x56, 0x5F, 0x58, 0x4D, 0x4A, 0x43, 0x44,
    0x19, 0x1E, 0x17, 0x10, 0x05, 0x02, 0x0B, 0x0C, 0x21, 0x26, 0x2F, 0x28, 0x3D, 0x3A, 0x33, 0x34,
    0x4E, 0x49, 0x40, 0x47, 0x52, 0x55, 0x5C, 0x5B, 0x76, 0x71, 0x78, 0x7F, 0x6A, 0x6D, 0x64, 0x63,
    0x3E, 0x39, 0x30, 0x37, 0x22, 0x25, 0x2C, 0x2B, 0x06, 0x01, 0x08, 0x0F, 0x1A, 0x1D, 0x14, 0x13,
    0xAE, 0xA9, 0xA0, 0xA7, 0xB2, 0xB5, 0xBC, 0xBB, 0x96, 0x91, 0x98, 0x9F, 0x8A, 0x8D, 0x84, 0x83,
    0xDE, 0xD9, 0xD0, 0xD7, 0xC2, 0xC5, 0xCC, 0xCB, 0xE6, 0xE1, 0xE8, 0xEF, 0xFA, 0xFD, 0xF4, 0xF3,
};

static uint8_t crc8_ccitt(uint8_t crc, uint8_t b) {
    return pgm_read_byte(&CRC8_TABLE[crc ^ b]);
}

// Board-agnostic frame emitter — same line discipline as Phase-9-deleted
// text-prefix log helpers (single-byte writes, .flush() at end). Does NOT
// consult com_mode; the strong override on Uno gates this call. Leonardo's
// USB-CDC has no PORTD aliasing risk so it uses the weak default of
// rurp_log_id which calls this unconditionally.
void _firestarter_emit_frame(uint8_t id, const uint8_t* params, uint8_t param_count) {
    // Wire-frame budget guard: `len = 1 (id) + param_count + 1 (crc)` must
    // fit in a uint8_t. With param_count >= 254 the `len` byte wraps silently
    // and the host decoder reads a shorter body than we actually emit — frame
    // desync. The catalog enforces a 24-byte PARAM_BUDGET cap upstream, but
    // this is the wire boundary; refuse oversize frames here regardless so
    // callers (including future LOG_ID_BYTES users) cannot trip the wrap.
    // Silent drop is deliberate — we cannot emit a valid frame on the same
    // serial channel without risking the desync we are trying to prevent.
    if (param_count > 65533) {   // u16 max (65535) - 2 (for id + crc)
        return;
    }

    // Magic preamble (4 bytes from PROGMEM).
    SERIAL_PORT.write((uint8_t)pgm_read_byte(&MAGIC_PREAMBLE[0]));
    SERIAL_PORT.write((uint8_t)pgm_read_byte(&MAGIC_PREAMBLE[1]));
    SERIAL_PORT.write((uint8_t)pgm_read_byte(&MAGIC_PREAMBLE[2]));
    SERIAL_PORT.write((uint8_t)pgm_read_byte(&MAGIC_PREAMBLE[3]));

    // Length field (u16 big-endian, W-04): counts id + params + crc;
    // excludes the len field itself and the trailing 0x0A anchor.
    uint16_t len_u16 = (uint16_t)(1 + param_count + 1);
    SERIAL_PORT.write((uint8_t)(len_u16 >> 8));    // MSB
    SERIAL_PORT.write((uint8_t)(len_u16 & 0xFF));  // LSB

    // CRC8 accumulator runs over [id, params].
    uint8_t crc = 0;

    // ID.
    SERIAL_PORT.write(id);
    crc = crc8_ccitt(crc, id);

    // Params.
    for (uint8_t i = 0; i < param_count; i++) {
        uint8_t b = params[i];
        SERIAL_PORT.write(b);
        crc = crc8_ccitt(crc, b);
    }

    // CRC byte.
    SERIAL_PORT.write(crc);

    // 0x0A re-sync anchor.
    SERIAL_PORT.write((uint8_t)0x0A);

    SERIAL_PORT.flush();
}

// Phase 8 W-04 — wide variant of _firestarter_emit_frame that accepts a
// uint16_t param_count so MSG_DATA_CHUNK payloads up to 512 / 1024 bytes
// do not overflow the uint8_t loop counter. All other wire-frame fields
// (magic preamble, u16 len, CRC8, 0x0A anchor) are identical.
void _firestarter_emit_frame_wide(uint8_t id, const uint8_t* params, uint16_t param_count) {
    if (param_count > 65533) {   // u16 max (65535) - 2 (for id + crc)
        return;
    }

    // Magic preamble (4 bytes from PROGMEM).
    SERIAL_PORT.write((uint8_t)pgm_read_byte(&MAGIC_PREAMBLE[0]));
    SERIAL_PORT.write((uint8_t)pgm_read_byte(&MAGIC_PREAMBLE[1]));
    SERIAL_PORT.write((uint8_t)pgm_read_byte(&MAGIC_PREAMBLE[2]));
    SERIAL_PORT.write((uint8_t)pgm_read_byte(&MAGIC_PREAMBLE[3]));

    // Length field (u16 big-endian, W-04).
    uint16_t len_u16 = (uint16_t)(1 + param_count + 1);
    SERIAL_PORT.write((uint8_t)(len_u16 >> 8));    // MSB
    SERIAL_PORT.write((uint8_t)(len_u16 & 0xFF));  // LSB

    // CRC8 accumulator over [id, params].
    uint8_t crc = 0;

    // ID.
    SERIAL_PORT.write(id);
    crc = crc8_ccitt(crc, id);

    // Params — uint16_t loop counter for large chunks.
    for (uint16_t i = 0; i < param_count; i++) {
        uint8_t b = params[i];
        SERIAL_PORT.write(b);
        crc = crc8_ccitt(crc, b);
    }

    // CRC byte.
    SERIAL_PORT.write(crc);

    // 0x0A re-sync anchor.
    SERIAL_PORT.write((uint8_t)0x0A);

    SERIAL_PORT.flush();
}

// Phase 9: deleted the two weak-default text-prefix log helpers
// (RAM body + PROGMEM body). See 09-CONTEXT.md D-02.

// Weak default for rurp_log_id — no com_mode gate (Leonardo path). Uno
// provides a strong override in uno_rurp_shield.cpp that gates by com_mode.
__attribute__((weak)) void rurp_log_id(uint8_t id, const uint8_t* params, uint8_t param_count) {
    _firestarter_emit_frame(id, params, param_count);
}

// Fixed-shape packers. Each LOG_*_ID_U{8,16,24,32} macro previously inlined
// the byte-array build at every call site (~10-30 instructions × ~30 sites).
// Sharing the pack here keeps the call site to a single CALL and reduces
// Flash use by ~200-400 B on AVR. No com_mode gate needed; rurp_log_id
// itself routes through the strong override on Uno.
void rurp_log_id_u8(uint8_t id, uint8_t v) {
    uint8_t b[1] = { v };
    rurp_log_id(id, b, 1);
}

void rurp_log_id_u16(uint8_t id, uint16_t v) {
    uint8_t b[2] = {
        (uint8_t)((v >> 8) & 0xFF),
        (uint8_t)(v & 0xFF),
    };
    rurp_log_id(id, b, 2);
}

void rurp_log_id_u24(uint8_t id, uint32_t v) {
    uint8_t b[3] = {
        (uint8_t)((v >> 16) & 0xFF),
        (uint8_t)((v >> 8) & 0xFF),
        (uint8_t)(v & 0xFF),
    };
    rurp_log_id(id, b, 3);
}

void rurp_log_id_u32(uint8_t id, uint32_t v) {
    uint8_t b[4] = {
        (uint8_t)((v >> 24) & 0xFF),
        (uint8_t)((v >> 16) & 0xFF),
        (uint8_t)((v >> 8) & 0xFF),
        (uint8_t)(v & 0xFF),
    };
    rurp_log_id(id, b, 4);
}

// Weak default for rurp_log_id_wide — wide variant for large payloads
// (W-04 MSG_DATA_CHUNK). Uno's strong override in uno_rurp_shield.cpp should
// also provide rurp_log_id_wide; until it does, this weak default works for
// both boards (Leonardo has no com_mode gate; Uno should not call this path
// outside communication mode, which the operation-loop already ensures).
__attribute__((weak)) void rurp_log_id_wide(uint8_t id, const uint8_t* params, uint16_t param_count) {
    _firestarter_emit_frame_wide(id, params, param_count);
}