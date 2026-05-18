/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 */

#ifdef ARDUINO_AVR_UNO
#include "rurp_shield.h"
#include <Arduino.h>
#include "rurp_register_utils.h"

#include "rurp_serial_utils.h"

#define USER_BUTTON 0x10             // USER BUTTON

constexpr int INPUT_RESOLUTION = 1023;

bool com_mode = true;

#ifdef SERIAL_DEBUG
#define RX_DEBUG  A0
#define TX_DEBUG  A1

void log_debug(PGM_P type, const char* msg);
#else
#define log_debug(type, msg)
#endif


void rurp_board_setup() {
    // Set control pins on PORTB to output.
    // PB0-3 are register select lines, PB5 is Chip Enable.
    // PB4 is User Button input.
    // NOTE: The original code included `READ_WRITE` (0x40), which would attempt to control PB6.
    // On a standard Uno, PB6 is a crystal pin and should not be used for I/O. It has been removed.
    DDRB = LEAST_SIGNIFICANT_BYTE | MOST_SIGNIFICANT_BYTE | CONTROL_REGISTER | OUTPUT_ENABLE | CHIP_ENABLE;
    PORTB = USER_BUTTON;

    rurp_chip_disable();
    rurp_chip_input();

    rurp_write_to_register(LEAST_SIGNIFICANT_BYTE, 0x00);
    rurp_write_to_register(MOST_SIGNIFICANT_BYTE, 0x00);
    rurp_write_to_register(CONTROL_REGISTER, 0x00);

    rurp_set_communication_mode();
}

void rurp_set_communication_mode() {
    // PD0 doubles as UART RX and data-bus bit 0. During programming we
    // drive PD0 as output, value = last data byte's bit 0. If we just
    // clear DDRD bit 0 and immediately call Serial.begin(), UART RXEN0 is
    // enabled while PD0 may still be LOW — UART then samples that as a
    // START BIT and queues spurious bytes (patterns reflecting data-bus
    // state during programming) into the RX ring buffer. The host reads
    // those bytes concatenated with the legitimate "OK: Req data\r\n"
    // via readline(), and if the corruption happens to break the OK
    // prefix the parser times out. Bench-discovered via FIRESTARTER_RX_TRACE
    // (firestarter_prom .planning/...04-HW-VALIDATION.md).
    //
    // Two-part fix:
    //   1. Set PORTD bit 0 = 1 BEFORE clearing DDRD bit 0. With DDR=1 and
    //      PORTD bit 0=1 the pin is actively driven HIGH. When DDR
    //      transitions to 0 (input), the internal pull-up keeps PD0 HIGH.
    //      UART hardware sees idle when RXEN0 enables — no false start bit.
    //   2. After Serial.begin() drain any RX bytes that leaked into the
    //      ring buffer (belt and braces).
    PORTD |= 0x01;
    DDRD &= ~(0x01);
    rurp_serial_begin(MONITOR_SPEED);
    while (SERIAL_PORT.available()) SERIAL_PORT.read();
    com_mode = true;
}

void rurp_set_programmer_mode() {
    com_mode = false;
    rurp_serial_end();
    DDRD |= 0x01;
}


void rurp_log(PGM_P type, const char* msg) {
    log_debug(type, msg);
    if (com_mode) {
        _firestarter_log_ram(type, msg);
    }
}

void rurp_log_P(PGM_P type, PGM_P msg) {
    if (com_mode) {
        _firestarter_log_progmem(type, msg);
    }
}

// Phase 6 — Uno strong override of rurp_log_id. The com_mode gate is critical:
// emitting on the wire while PORTD is repurposed as the data bus would corrupt
// the programming pulse (per CONTEXT §"Specific Ideas").
// Phase 8 Plan 07: debug_msg_buffer path removed; LOG_DEBUG_ID_SUB* now handles
// structured debug output directly via catalog frames.
void rurp_log_id(uint8_t id, const uint8_t* params, uint8_t param_count) {
    if (com_mode) {
        _firestarter_emit_frame(id, params, param_count);
    }
}

// Uno strong override for rurp_log_id_wide (W-04 MSG_DATA_CHUNK path).
// Same com_mode discipline as rurp_log_id; calls the wide frame emitter.
void rurp_log_id_wide(uint8_t id, const uint8_t* params, uint16_t param_count) {
    if (com_mode) {
        _firestarter_emit_frame_wide(id, params, param_count);
    }
}


void rurp_set_control_pin(uint8_t pin, uint8_t state) {
    // This function modifies only the specified control pin on PORTB,
    // leaving other bits (like the USER_BUTTON pull-up) untouched.
    // The original implementation was flawed and could clear other bits.
    if (state) {
        PORTB |= pin;
    } else {
        PORTB &= ~pin;
    }
}

uint8_t rurp_user_button_pressed() {
    return (PINB & USER_BUTTON) == 0;
}

void rurp_write_data_buffer(uint8_t data) {
    rurp_set_data_output();
    PORTD = data;
}

uint8_t rurp_read_data_buffer() {
    return PIND;
}

void rurp_set_data_output() {
    DDRD = 0xff;
}

void rurp_set_data_input() {
    // Clear PORTD before switching to input so internal pullups are disabled
    // on every data line. Without this, residual PORTD bits from the last
    // register-strobe or rurp_set_communication_mode (PORTD bit 0 = 1) leave
    // 1..2 data pins weakly biased HIGH against the chip's drive. Defensive
    // — does not on its own fix the FM1608 byte-0 read failure on Uno (see
    // .planning/debug/fm1608-fresh-chip-baseline.md).
    PORTD = 0x00;
    DDRD = 0x00;
}

#ifdef SERIAL_DEBUG
#include <SoftwareSerial.h>
SoftwareSerial debugSerial(RX_DEBUG, TX_DEBUG);

void debug_setup() {
    debugSerial.begin(57600);
}

void debug_buf(const char* msg) {
    log_debug("DEBUG", msg);
}

void log_debug(PGM_P type, const char* msg) {
    // Copy the PROGMEM type string to a RAM buffer to print.
    char type_buf[10];
    strcpy_P(type_buf, type);
    debugSerial.print(type_buf);
    debugSerial.print(": ");
    debugSerial.println(msg);
    debugSerial.flush();
}
#endif
#endif
