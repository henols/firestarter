/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 */
#include <avr/pgmspace.h>

#include "rurp_serial_utils.h"
#include "rurp_shield.h"

// --- Core Logging Functions ---

// Core logging function for RAM messages. Takes type from PROGMEM.
 void _firestarter_log_ram(PGM_P type, const char* msg) {
    SERIAL_PORT.print((const __FlashStringHelper*)type);
    SERIAL_PORT.print(F(": ")); 
    SERIAL_PORT.println(msg);
    SERIAL_PORT.flush();
}

// Core logging function for PROGMEM messages.
 void _firestarter_log_progmem(PGM_P type, PGM_P p_msg) {
    SERIAL_PORT.print((const __FlashStringHelper*)type);
    SERIAL_PORT.print(F(": "));
    SERIAL_PORT.println((const __FlashStringHelper*)p_msg);
    SERIAL_PORT.flush();
}

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

int rurp_communication_read_data(char* buffer) {
    uint8_t size_buf[2];
    if (rurp_communication_read_bytes((char*)size_buf, 2) != 2) {
        return -1;
    }
    size_t data_size = (size_buf[0] << 8) | size_buf[1];

    uint8_t checksum_rcvd;
    if (rurp_communication_read_bytes((char*)&checksum_rcvd, 1) != 1) {
        return -1;
    }

    if (data_size > DATA_BUFFER_SIZE) {
        // log_error_format("Bad size: %d", (int)handle->data_size);
        return -2;
    }

    size_t len = 0;
    unsigned long start_time = millis();
    unsigned long timeout_ms = 2000;  // A 2-second timeout for the entire data block
    while (len < data_size) {
        if (millis() - start_time > timeout_ms) {
            // log_error_const("Timeout reading data block");
            return -3;
        }
        // Read remaining bytes. readBytes will timeout and return what it has if data flow stops.
        len += rurp_communication_read_bytes(buffer + len, data_size - len);
    }

    uint8_t checksum = 0;
    for (size_t i = 0; i < len; i++) {
        checksum ^= buffer[i];
    }
    if (checksum != checksum_rcvd) {
        // log_error_format("Bad checksum %02X != %02X", checksum, checksum_rcvd);
        return -4;
    }
    return len;
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
// Wire frame layout (8+ bytes):
//     bytes 0..3 : 0xAA 0x55 0xAA 0x55         (magic preamble)
//     byte 4     : len = 1 + param_count + 1    (id + params + crc)
//     byte 5     : id
//     bytes 6..N : params (raw, MSB-first per type encoded by caller)
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

// Board-agnostic frame emitter. Sibling to _firestarter_log_ram /
// _firestarter_log_progmem — same line discipline (single-byte writes,
// .flush() at end). Does NOT consult com_mode; the strong override on Uno
// gates this call. Leonardo's USB-CDC has no PORTD aliasing risk so it
// uses the weak default of rurp_log_id which calls this unconditionally.
void _firestarter_emit_frame(uint8_t id, const uint8_t* params, uint8_t param_count) {
    // Wire-frame budget guard: `len = 1 (id) + param_count + 1 (crc)` must
    // fit in a uint8_t. With param_count >= 254 the `len` byte wraps silently
    // and the host decoder reads a shorter body than we actually emit — frame
    // desync. The catalog enforces a 24-byte PARAM_BUDGET cap upstream, but
    // this is the wire boundary; refuse oversize frames here regardless so
    // callers (including future LOG_ID_BYTES users) cannot trip the wrap.
    // Silent drop is deliberate — we cannot emit a valid frame on the same
    // serial channel without risking the desync we are trying to prevent.
    if (param_count > 253) {
        return;
    }

    // Magic preamble (4 bytes from PROGMEM).
    SERIAL_PORT.write((uint8_t)pgm_read_byte(&MAGIC_PREAMBLE[0]));
    SERIAL_PORT.write((uint8_t)pgm_read_byte(&MAGIC_PREAMBLE[1]));
    SERIAL_PORT.write((uint8_t)pgm_read_byte(&MAGIC_PREAMBLE[2]));
    SERIAL_PORT.write((uint8_t)pgm_read_byte(&MAGIC_PREAMBLE[3]));

    // Length byte: counts id + params + crc; excludes len itself and trailing 0x0A.
    uint8_t len = (uint8_t)(1 + param_count + 1);
    SERIAL_PORT.write(len);

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

// Provide weak default implementations for logging.
// These can be overridden by a strong implementation in board-specific code.
__attribute__((weak)) void rurp_log(PGM_P type, const char* msg) {
    _firestarter_log_ram(type, msg);
}
__attribute__((weak)) void rurp_log_P(PGM_P type, PGM_P msg) {
    _firestarter_log_progmem(type, msg);
}

// Weak default for rurp_log_id — no com_mode gate (Leonardo path). Uno
// provides a strong override in uno_rurp_shield.cpp that gates by com_mode
// and (under SERIAL_DEBUG) emits a terse hex-dump summary to log_debug.
__attribute__((weak)) void rurp_log_id(uint8_t id, const uint8_t* params, uint8_t param_count) {
    _firestarter_emit_frame(id, params, param_count);
}