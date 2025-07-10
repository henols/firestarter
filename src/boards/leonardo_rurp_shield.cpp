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

#define PORTC_DATA_MASK 0x40
#define PORTD_DATA_MASK 0x9f
#define PORTE_DATA_MASK 0x40

#define PORTB_CONTROL_MASK 0xf0
#define PORTD_CONTROL_MASK 0x40
#define PORTC_CONTROL_MASK 0x80

#define USER_BUTTON PORTD_CONTROL_MASK

constexpr int INPUT_RESOLUTION = 1023;

uint8_t control_pins = 0x00;

void rurp_board_setup() {
    DDRB |= PORTB_CONTROL_MASK; // Set pins D8-D13 as output
    DDRC |= PORTC_CONTROL_MASK; // Set pin D13 as output

    DDRD &= ~USER_BUTTON; // Set pin D12 as input
    PORTD |= USER_BUTTON; // Enable pull-up resistor on pin D12

    SERIAL_PORT.begin(MONITOR_SPEED);
    while (!SERIAL_PORT) {
        delayMicroseconds(1);
    }
    SERIAL_PORT.flush();
    delay(1);
}

void rurp_set_control_pin(uint8_t pin, uint8_t state) {
    // log_info("Setting control pins");
    control_pins = state ? control_pins | pin : control_pins & ~(pin);
    uint8_t nbyte = control_pins << 2;
    
    PORTC = (PORTC & ~PORTC_CONTROL_MASK) | (nbyte & PORTC_CONTROL_MASK); // set pins D13 (PC7 in PORTC) from byte bits 5
    PORTB = (PORTB & ~PORTB_CONTROL_MASK) | (nbyte << 2); // set pins D8-D11 (PB4-PB7 in PORTB) from byte bits 0-3
}

uint8_t rurp_user_button_pressed() {
    return (PIND & USER_BUTTON) == 0;
}

void rurp_write_data_buffer(uint8_t data) {
    rurp_set_data_output(); // Ensure data lines are output
    
    uint8_t portd_val = data & 0x10;        // bit 4 -> PD4

    uint8_t lbyte = data << 1;
    uint8_t portc_val = lbyte & PORTC_DATA_MASK; // bit 5 -> PC6
    portd_val |= (lbyte & 0x80) | ((lbyte << 1) & 0x0c);     // bit 6 -> PD7, bit 2 -> PD1, bit 3 -> PD0

    uint8_t rbyte = data >> 1;
    uint8_t porte_val = rbyte & PORTE_DATA_MASK; // bit 7 -> PE6
    portd_val |= (rbyte & 0x02) | ((rbyte >> 2) & 0x01); // bit 0 -> PD2, bit 1 -> PD3

    // Clear the bits we are about to update, then set the new bits.
    PORTD = (PORTD & ~PORTD_DATA_MASK) | portd_val;
    PORTC = (PORTC & ~PORTC_DATA_MASK) | portc_val;
    PORTE = (PORTE & ~PORTE_DATA_MASK) | porte_val;
}

uint8_t rurp_read_data_buffer() {
    uint8_t data = PIND & 0x10; // PD4 -> bit 4.
    uint8_t rpind = PIND >> 1;
    data |= rpind & 0x40; // PD7 -> bit 6.
    data |= (rpind >> 1) & 0x03; // PD2 -> bit 0, PD3 -> bit 1.

    uint8_t lpind = PIND << 1;
    data |= (lpind & 0x04) | ((lpind << 2) & 0x08); // PD1 -> bit 2, PD0 -> bit 3.

    data |= ((PINC >> 1) & 0x20) | ((PINE << 1) & 0x80);
    return data;
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

uint16_t rurp_read_vcc_mv() {
    // Read 1.1V reference against AVcc
    // Set the analog reference to the internal 1.1V
    // Default is analogReference(DEFAULT) which is connected to the external 5V
    ADMUX = _BV(REFS0) | _BV(MUX4) | _BV(MUX3) | _BV(MUX2) | _BV(MUX1);

    delay(2); // Wait for voltage to stabilize
    ADCSRA |= _BV(ADSC);              // Start conversion
    while (bit_is_set(ADCSRA, ADSC))  // Wait for conversion to complete
        ;
    ADCSRA |= _BV(ADSC);              // Start conversion
    while (bit_is_set(ADCSRA, ADSC))  // measuring
        ;
    long result = ADCL;
    result |= ADCH << 8;

    // Calculate Vcc (supply voltage) in millivolts
    // VCC_mV = (1.1V * 1024 * 1000 mV/V) / ADC_reading
    if (result == 0) return 0;  // Avoid division by zero
    return 1125300L / result;
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
void debug_setup() {}

void debug_buf(const char* msg) {
    rurp_log("DEBUG", msg);
}
#endif
#endif
