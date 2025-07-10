/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 */

#ifdef ARDUINO_AVR_UNO
#include "rurp_shield.h"
#include <Arduino.h>
#include "rurp_config_utils.h"
#include "rurp_register_utils.h"

#define RURP_CUSTOM_LOG
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
    // rurp_set_data_as_output();

    DDRB = LEAST_SIGNIFICANT_BYTE | MOST_SIGNIFICANT_BYTE | CONTROL_REGISTER | OUTPUT_ENABLE | CHIP_ENABLE | READ_WRITE;
    PORTB = USER_BUTTON;

    rurp_chip_disable();
    rurp_chip_input();

    rurp_write_to_register(LEAST_SIGNIFICANT_BYTE, 0x00);
    rurp_write_to_register(MOST_SIGNIFICANT_BYTE, 0x00);
    rurp_write_to_register(CONTROL_REGISTER, 0x00);

    rurp_set_communication_mode();
}

void rurp_set_communication_mode() {
    DDRD &= ~(0x01);
    rurp_serial_begin(MONITOR_SPEED);
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
        rurp_log_internal(type, msg);
    }
}

void rurp_log_P(PGM_P type, PGM_P msg) {
    // For debug logging, we need to copy the PROGMEM message to RAM.
    // We can reuse the debug_msg_buffer for this.
    #ifdef SERIAL_DEBUG
    strcpy_P(debug_msg_buffer, msg);
    log_debug(type, debug_msg_buffer);
    #endif
    if (com_mode) {
        rurp_log_internal_P(type, msg);
    }
}


void rurp_set_control_pin(uint8_t pin, uint8_t state) {
    if (state) {
        PORTB |= pin | USER_BUTTON;
    }
    else {
        PORTB &= ~(pin) | USER_BUTTON;
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
    DDRD = 0x00;
}


uint16_t rurp_read_vcc_mv() {
    // Read 1.1V reference against AVcc
    // Set the analog reference to the internal 1.1V
    // Default is analogReference(DEFAULT) which is connected to the external 5V
    ADMUX = _BV(REFS0) | _BV(MUX3) | _BV(MUX2) | _BV(MUX1);

    delay(2); // Wait for voltage to stabilize
    ADCSRA |= _BV(ADSC);              // Start conversion
    while (bit_is_set(ADCSRA, ADSC))  // Wait for conversion to complete
        ;

    long result = ADCL;
    result |= ADCH << 8;

    // Calculate Vcc (supply voltage) in millivolts
    // VCC_mV = (1.1V * 1024 * 1000 mV/V) / ADC_reading = 1126400 / ADC_reading
    if (result == 0) return 0;  // Avoid division by zero
    return 1126400L / result;
}

uint16_t rurp_read_voltage_mv() {
    uint16_t vcc_mv = rurp_read_vcc_mv();
    rurp_configuration_t* rurp_config = rurp_get_config();
    uint32_t r1 = rurp_config->r1;
    uint32_t r2 = rurp_config->r2;

    if (r2 == 0) {
        return 0;  // Avoid division by zero
    }

    // Set analog reference to default (VCC) for the measurement
    analogReference(DEFAULT);
    uint32_t adc_reading = analogRead(VOLTAGE_MEASURE_PIN);

    // Vin_mV = (ADC_reading * VCC_mV * (R1 + R2)) / (1024 * R2)
    // Use 64-bit integer to avoid overflow during calculation.
    uint64_t vin_mv = (uint64_t)adc_reading * vcc_mv * (r1 + r2) / (1024UL * r2);

    return (uint16_t)vin_mv;
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
