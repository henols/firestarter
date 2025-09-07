/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 */
#include <avr/pgmspace.h>

#include "rurp_serial_utils.h"
#include "rurp_shield.h"
#include "logging.h"

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

    // Send OK response after receiving size and hash, before receiving actual data
    
    send_ack_const("");

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

// Provide weak default implementations for logging.
// These can be overridden by a strong implementation in board-specific code.
__attribute__((weak)) void rurp_log(PGM_P type, const char* msg) {
    _firestarter_log_ram(type, msg);
}
__attribute__((weak)) void rurp_log_P(PGM_P type, PGM_P msg) {
    _firestarter_log_progmem(type, msg);
}