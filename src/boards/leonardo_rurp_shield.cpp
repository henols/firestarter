/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 */


#ifdef ARDUINO_AVR_LEONARDO
#include "rurp_shield.h"
#include <Arduino.h>
#include "rurp_config_utils.h"
#include "rurp_register_utils.h"
#include "logging.h"

#include "rurp_serial_utils.h"

#define PORTD_DATA_MASK 0x9f
#define PORTC_DATA_MASK 0x40
#define PORTE_DATA_MASK 0x40

#define PORTB_CONTROL_MASK 0xf0
#define PORTD_CONTROL_MASK 0x40
#define PORTC_CONTROL_MASK 0x80

constexpr int INPUT_RESOLUTION = 1023;

uint8_t rurp_get_data_pins();
void rurp_set_data_pins(uint8_t data);
void rurp_set_control_pins(uint8_t value);

uint8_t control_pins = 0x00;

void rurp_board_setup() {
    DDRB |= PORTB_CONTROL_MASK; // Set pins D8-D13 as output
    DDRD |= PORTD_CONTROL_MASK; // Set pin D12 as output
    DDRC |= PORTC_CONTROL_MASK; // Set pin D13 as output

    SERIAL_PORT.begin(MONITOR_SPEED);
    while (!SERIAL_PORT) {
        delayMicroseconds(1);
    }
    SERIAL_PORT.flush();
    delay(1);
}



void rurp_set_control_pin(uint8_t pin, uint8_t state) {
    control_pins = state ? control_pins | pin : control_pins & ~(pin);
    rurp_set_control_pins(control_pins);
}


void rurp_write_data_buffer(uint8_t data) {
    rurp_set_data_output(); // Ensure data lines are output
    rurp_set_data_pins(data);
}

uint8_t rurp_read_data_buffer() {
    return rurp_get_data_pins();
}

void rurp_set_data_output() {
    DDRD |= PORTD_DATA_MASK; // Set pins D0-D3 and D4-D7 as output
    DDRC |= PORTC_DATA_MASK; // Set pin D5 as output
    DDRE |= PORTE_DATA_MASK; // Set pin D6 as output
}

void rurp_set_data_input() {
    DDRD &= ~PORTD_DATA_MASK; // Set pins D0-D3 and D4-D7 as output
    DDRC &= ~PORTC_DATA_MASK; // Set pin D5 as output
    DDRE &= ~PORTE_DATA_MASK; // Set pin D6 as output
}

uint8_t rurp_get_data_pins() {
    uint8_t data = PIND & 0x10; // PD4 -> bit 4.
    uint8_t rpind = PIND >> 1;
    data |= rpind & 0x40; // PD7 -> bit 6.
    data |= (rpind >> 1) & 0x03; // PD2 -> bit 0, PD3 -> bit 1.

    uint8_t lpind = PIND << 1;
    data |= (lpind & 0x04) | ((lpind << 2) & 0x08); // PD1 -> bit 2, PD0 -> bit 3.

    data |= ((PINC >> 1) & 0x20) | ((PINE << 1) & 0x80);
    return data;
}

void rurp_set_data_pins(uint8_t byte) {
    uint8_t portd_val = byte & 0x10;        // bit 4 -> PD4

    uint8_t lbyte = byte << 1;
    uint8_t portc_val = lbyte & PORTC_DATA_MASK; // bit 5 -> PC6
    portd_val |= (lbyte & 0x80) | ((lbyte << 1) & 0x0c);     // bit 6 -> PD7, bit 2 -> PD1, bit 3 -> PD0

    uint8_t rbyte = byte >> 1;
    uint8_t porte_val = rbyte & PORTE_DATA_MASK; // bit 7 -> PE6
    portd_val |= (rbyte & 0x02) | ((rbyte >> 2) & 0x01); // bit 0 -> PD2, bit 1 -> PD3

    // Clear the bits we are about to update, then set the new bits.
    PORTD = (PORTD & ~PORTD_DATA_MASK) | portd_val;
    PORTC = (PORTC & ~PORTC_DATA_MASK) | portc_val;
    PORTE = (PORTE & ~PORTE_DATA_MASK) | porte_val;
}

void rurp_set_control_pins(uint8_t byte) {
    // log_info("Setting control pins");
    uint8_t nbyte = byte << 2;
    PORTD = (PORTD & ~PORTD_CONTROL_MASK) | (nbyte & PORTD_CONTROL_MASK); // set pins D12 (PD6 in PORTD) from byte bits 4
    PORTC = (PORTC & ~PORTC_CONTROL_MASK) | (nbyte & PORTC_CONTROL_MASK); // set pins D13 (PC7 in PORTC) from byte bits 5
    PORTB = (PORTB & ~PORTB_CONTROL_MASK) | (nbyte << 2); // set pins D8-D11 (PB4-PB7 in PORTB) from byte bits 0-3
}

double rurp_read_vcc() {
    // Read 1.1V reference against AVcc
    // Set the analog reference to the internal 1.1V
    // Default is analogReference(DEFAULT) which is connected to the external 5V
    ADMUX = _BV(REFS0) | _BV(MUX4) | _BV(MUX3) | _BV(MUX2) | _BV(MUX1);

    delay(2); // Wait for voltage to stabilize
    ADCSRA |= _BV(ADSC); // Start conversion
    while (bit_is_set(ADCSRA, ADSC)); // Wait for conversion to complete
    ADCSRA |= _BV(ADSC); // Start conversion
    while (bit_is_set(ADCSRA, ADSC)); // measuring
    long result = ADCL;
    result |= ADCH << 8;

    // Calculate Vcc (supply voltage) in millivolts
    // 1100 mV * 1024 ADC steps / ADC reading
    return 1125300L / result / 1000;
}

double rurp_read_voltage() {
    double refRes = rurp_read_vcc() / INPUT_RESOLUTION;
    rurp_configuration_t* rurp_config = rurp_get_config();
    long r1 = rurp_config->r1;
    long r2 = rurp_config->r2;

    // Correct voltage divider ratio calculation
    double voltageDivider = 1.0 + static_cast<double>(r1) / r2;

    // Read the analog value and convert to voltage
    double vout = analogRead(VOLTAGE_MEASURE_PIN) * refRes;

    // Calculate the input voltage
    return vout * voltageDivider;
}


#ifdef SERIAL_DEBUG
void debug_setup() {}

void debug_buf(const char* msg) {
    rurp_log("DEBUG", msg);
}
#endif

#endif


