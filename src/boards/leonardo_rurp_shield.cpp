/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 */


#ifdef ARDUINO_AVR_LEONARDO
#include "rurp_shield.h"
#include <Arduino.h>
#include "rurp_register_utils.h"
#include "logging.h"

#include "rurp_serial_utils.h"

#define PORTC_DATA_MASK 0x40
#define PORTD_DATA_MASK 0x9f // D0(PD2), D1(PD3), D2(PD1), D3(PD0), D4(PD4), D7(PD7)
#define PORTE_DATA_MASK 0x40

#define PORTB_CONTROL_MASK 0xf0
#define PORTD_CONTROL_MASK 0x40 // D12 (PD6)
#define PORTC_CONTROL_MASK 0x80

constexpr int INPUT_RESOLUTION = 1023;

uint8_t control_pins = 0x00;

void rurp_board_setup() {
    DDRB |= PORTB_CONTROL_MASK; // Set pins D8-D13 as output
    DDRC |= PORTC_CONTROL_MASK; // Set pin D13 as output (PC7)
    DDRD |= PORTD_CONTROL_MASK; // Set pin D12 as output (PD6)

    // Note: User button is not available on Leonardo shield revision.

    SERIAL_PORT.begin(MONITOR_SPEED);
    while (!SERIAL_PORT) {
        delayMicroseconds(1);
    }
    SERIAL_PORT.flush();
    delay(1);
}

void rurp_set_control_pin(uint8_t pin, uint8_t state) {
    // Update the state of the logical control pins
    control_pins = state ? (control_pins | pin) : (control_pins & ~pin);

    // Map logical control_pins bits to physical port pins
    // The control lines are scattered across PORTB, PORTC, and PORTD.
    // Logical Bit -> Arduino Pin -> MCU Pin
    // ---------------------------------------
    // Bit 0       -> D8          -> PB4
    // Bit 1       -> D9          -> PB5
    // Bit 2       -> D10         -> PB6
    // Bit 3       -> D11         -> PB7
    // Bit 4       -> D12         -> PD6
    // Bit 5       -> D13         -> PC7

    // Bits 0-3 -> PB4-PB7
    uint8_t portb_val = control_pins << 4;
    // Bit 4 -> PD6
    uint8_t portd_val = (control_pins & 0x10) << 2;
    // Bit 5 -> PC7
    uint8_t portc_val = (control_pins & 0x20) << 2;

    // Atomically update the ports using read-modify-write
    PORTB = (PORTB & ~PORTB_CONTROL_MASK) | portb_val;
    PORTD = (PORTD & ~PORTD_CONTROL_MASK) | portd_val;
    PORTC = (PORTC & ~PORTC_CONTROL_MASK) | portc_val;
}

uint8_t rurp_user_button_pressed() {
    // User button is not connected on the Leonardo shield revision.
    return 0;
}

void rurp_write_data_buffer(uint8_t data) {
    rurp_set_data_output(); // Ensure data lines are output

    // Map data bus bits (D0-D7) to their respective port pins for Leonardo.
    // This is complex due to the non-contiguous pinout.
    // Data Bit -> Arduino Pin -> MCU Pin
    // -----------------------------------
    // D0       -> D0          -> PD2
    // D1       -> D1          -> PD3
    // D2       -> D2          -> PD1
    // D3       -> D3          -> PD0
    // D4       -> D4          -> PD4
    // D5       -> D5          -> PC6
    // D6       -> D6          -> PD7
    // D7       -> D7          -> PE6

    uint8_t portd_val = ((data & _BV(0)) << 2) | // D0 to PD2
                        ((data & _BV(1)) << 2) | // D1 to PD3
                        ((data & _BV(2)) >> 1) | // D2 to PD1
                        ((data & _BV(3)) >> 3) | // D3 to PD0
                        (data & _BV(4)) |        // D4 to PD4
                        ((data & _BV(6)) << 1);  // D6 to PD7

    uint8_t portc_val = (data & _BV(5)) << 1;    // D5 to PC6
    uint8_t porte_val = (data & _BV(7)) >> 1;    // D7 to PE6

    // Atomically update the ports using read-modify-write
    PORTD = (PORTD & ~PORTD_DATA_MASK) | portd_val;
    PORTC = (PORTC & ~PORTC_DATA_MASK) | portc_val;
    PORTE = (PORTE & ~PORTE_DATA_MASK) | porte_val;
}

uint8_t rurp_read_data_buffer() {
    // Read from ports and map back to data bus bits (D0-D7)
    uint8_t pind_val = PIND;
    uint8_t pinc_val = PINC;
    uint8_t pine_val = PINE;

    uint8_t data = 0;
    data |= ((pind_val & _BV(2)) >> 2); // PD2 -> D0
    data |= ((pind_val & _BV(3)) >> 2); // PD3 -> D1
    data |= ((pind_val & _BV(1)) << 1); // PD1 -> D2
    data |= ((pind_val & _BV(0)) << 3); // PD0 -> D3
    data |= (pind_val & _BV(4));        // PD4 -> D4
    data |= ((pinc_val & _BV(6)) >> 1); // PC6 -> D5
    data |= ((pind_val & _BV(7)) >> 1); // PD7 -> D6
    data |= ((pine_val & _BV(6)) << 1); // PE6 -> D7

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
    long result = ADCL;
    result |= ADCH << 8;

    // Calculate Vcc (supply voltage) in millivolts
    // VCC_mV = (V_bandgap * ADC_resolution * 1000) / ADC_reading
    // VCC_mV = (1.1V * 1024 steps * 1000 mV/V) / ADC_reading = 1126400 / ADC_reading
    // The original value 1125300L was based on 1023 steps, which is slightly less accurate.
    if (result == 0) return 0;  // Avoid division by zero
    return 1126400L / result;
}


#ifdef SERIAL_DEBUG
void debug_setup() {}

void debug_buf(const char* msg) {
    rurp_log("DEBUG", msg);
}
#endif
#endif
