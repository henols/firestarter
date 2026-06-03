/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 */

#if defined(ARDUINO_AVR_UNO) || defined(ARDUINO_AVR_ATmega328PB)
#include "rurp_shield.h"
#include <Arduino.h>
#include "rurp_register_utils.h"

#include "rurp_serial_utils.h"

#define USER_BUTTON 0x10             // USER BUTTON

constexpr int INPUT_RESOLUTION = 1023;

bool com_mode = true;

// Deferred-log buffer (#transport-protocol-verify, Phase 53).
// On the Uno, PORTD doubles as the data bus during programmer mode, so emitting a
// frame on the wire mid-operation would corrupt the programming pulse — hence the
// com_mode gate below. Historically rurp_log_id simply DROPPED frames while
// com_mode==false, which silently lost every operation-emitted error/progress
// frame (blank-check progress, MSG_ERR_VERIFY mismatch, etc.) -> the host saw
// nothing and timed out (bench-confirmed Uno; Leonardo unaffected — no gate).
// Instead of dropping, we BUFFER frames emitted during the programmer-mode window
// and FLUSH them the moment communication mode is restored (wire safe to drive).
// Sizing: in production builds SERIAL_DEBUG is undefined so DEBUG frames expand to
// nothing; an operation emits at most ~1-2 critical frames per programmer-mode
// window, so DEFERRED_LOG_MAX=4 has ample headroom. Narrow frames only — the wide
// (MSG_DATA_CHUNK) path runs in communication mode and is never deferred.
#define DEFERRED_LOG_MAX 4
#define DEFERRED_PARAM_MAX 8  // widest narrow frame (U32_U32 / U16x4 / progress) = 8 bytes
static uint8_t deferred_count = 0;
static struct {
    uint8_t id;
    uint8_t len;
    uint8_t params[DEFERRED_PARAM_MAX];
} deferred_log[DEFERRED_LOG_MAX];

// Phase 9: deleted the legacy SERIAL_DEBUG infrastructure (debug pin defines
// plus the soft-serial debug channel). See 09-CONTEXT.md D-02 + D-08.


void rurp_board_setup() {
    // Set control pins on PORTB to output.
    // PB0-3 are register select lines, PB5 is Chip Enable.
    // PB4 is User Button input.
    // NOTE: The original code included `CTRL_READ_WRITE` (0x40), which would attempt to control PB6.
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
    // those bytes concatenated with the legitimate "OK: Request data\r\n"
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

    // Flush frames deferred during the programmer-mode window now that the UART is
    // up and the wire is safe to drive (#transport-protocol-verify).
    for (uint8_t i = 0; i < deferred_count; i++) {
        _firestarter_emit_frame(deferred_log[i].id, deferred_log[i].params, deferred_log[i].len);
    }
    deferred_count = 0;
}

void rurp_set_programmer_mode() {
    com_mode = false;
    rurp_serial_end();
    DDRD |= 0x01;
}


// Phase 9: deleted the two legacy text-prefix log Uno strong overrides
// (RAM body + PROGMEM body). See 09-CONTEXT.md D-02.

// Phase 6 — Uno strong override of rurp_log_id. The com_mode gate is critical:
// emitting on the wire while PORTD is repurposed as the data bus would corrupt
// the programming pulse (per CONTEXT §"Specific Ideas").
// Phase 8 Plan 07: debug_msg_buffer path removed; LOG_DEBUG_ID_SUB* now handles
// structured debug output directly via catalog frames.
void rurp_log_id(uint8_t id, const uint8_t* params, uint8_t param_count) {
    if (com_mode) {
        _firestarter_emit_frame(id, params, param_count);
        return;
    }
    // Programmer mode: the wire is the data bus — defer instead of dropping, then
    // flush in rurp_set_communication_mode (#transport-protocol-verify).
    if (param_count > DEFERRED_PARAM_MAX) {
        param_count = DEFERRED_PARAM_MAX;  // truncate; no narrow frame exceeds this
    }
    if (deferred_count < DEFERRED_LOG_MAX) {
        deferred_log[deferred_count].id = id;
        deferred_log[deferred_count].len = param_count;
        for (uint8_t i = 0; i < param_count; i++) {
            deferred_log[deferred_count].params[i] = params[i];
        }
        deferred_count++;
    }
    // else: buffer full (should not happen in production — see DEFERRED_LOG_MAX);
    // drop excess rather than risk emitting on the active bus.
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

// Phase 9: deleted the legacy SERIAL_DEBUG soft-serial debug channel
// (helper-setup + log-helper + debug-channel). See 09-CONTEXT.md D-02 + D-08.
// Replacement is LOG_DEBUG_ID_SUB* from logging_id.h (Phase 8 Plan 07), which
// routes structured debug emit through the main serial port via id-frames
// rather than a separate channel.
#endif
