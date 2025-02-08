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

#define PORTD_DATA_PINS (_BV() | _BV() | _BV() | _BV() | _BV() | _BV())
#define PORTC_DATA_PINS (_BV())
#define PORTE_DATA_PINS (_BV())

// #define PORTB_CONTROL_PINS (_BV(PB4) | _BV(PB5) | _BV(PB6) | _BV(PB7))
// #define PORTD_CONTROL_PINS (_BV(PD6))
// #define PORTC_CONTROL_PINS (_BV(PC7))

#define PORTB_CONTROL_PINS 0xf0
#define PORTD_CONTROL_PINS 0x40
#define PORTC_CONTROL_PINS 0x80

#define remap_bit(value, from_pos, to_pos) \
    ((value & _BV(from_pos)) == _BV(from_pos)) ? _BV(to_pos) : 0x00

constexpr int INPUT_RESOLUTION = 1023;

uint8_t rurp_get_data_pins();
void rurp_set_data_pins(uint8_t data);

void rurp_set_control_pins(uint8_t value);


uint8_t control_pins = 0x00;

void rurp_board_setup() {

    for (int i = 8; i <= 13; i++) {
        pinMode(i, OUTPUT);
    }

    Serial.begin(MONITOR_SPEED);
    while (!Serial) {
        delayMicroseconds(1);
    }
    Serial.flush();
    delay(1);
}

int rurp_communication_available() {
    return Serial.available();
}
int rurp_communication_read() {
    return Serial.read();
}

size_t rurp_communication_read_bytes(char* buffer, size_t length) {
    return Serial.readBytes(buffer, length);
}

size_t rurp_communication_write(const char* buffer, size_t size) {
    size_t bytes = Serial.write(buffer, size);
    Serial.flush();
    return bytes;
}


void rurp_log(const char* type, const char* msg) {
    Serial.print(type);
    Serial.print(": ");
    Serial.println(msg);
    Serial.flush();
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
    rurp_set_data_input(); // Ensure input mode
    return rurp_get_data_pins();
}

void rurp_set_data_output() {
    // DDRD |= PORTD_DATA_PINS; // Set pins D0-D3 and D4-D7 as output
    // DDRC |= PORTC_DATA_PINS; // Set pin D5 as output
    // DDRE |= PORTE_DATA_PINS; // Set pin D6 as output
    // log_info("Setting data pins as output");
    for (int i = 0; i < 8; i++) {
        pinMode(i, OUTPUT);
    }

}

void rurp_set_data_input() {
    // DDRD &= ~(0x04 & 0x08 & 0x02 & 0x01 & 0x10 & 0x80); // Set pins D0-D3 and D4-D7 as input
    // DDRC &= ~0x40; // Set pin D5 as input
    // DDRE &= ~0x40; // Set pin D6 as input
    // log_info("Setting data pins as input");
    for (int i = 0; i < 8; i++) {
        pinMode(i, INPUT);
    }
}

// #define READ_DATA_PINS_DIRECTLY
//  #define WRITE_DATA_PINS_DIRECTLY
#define WRITE_CONTROL_PINS_DIRECTLY

#define read_remap_bit(port, pin, to_bit) \
    (bit_is_set(port, pin)!= 0) ? _BV(to_bit) : 0x00

uint8_t rurp_get_data_pins_direct() {
    // Mapping the bits of the pins (D0-D7) to the correct bits in a byte
    uint8_t data = 0;
    data =    read_remap_bit(PINE, PE6, 7)|     // set bit 7 from D7 (PE6 from PINE)
        read_remap_bit(PIND, PD7, 6) |    // set bit 6 from D6 (PD7 from PIND)
        read_remap_bit(PINC, PC6, 5) |    // set bit 5 from D5 (PC6 from PINC)
        read_remap_bit(PIND, PD4, 4) |    // set bit 4 from D4 (PD4 from PIND)
        read_remap_bit(PIND, PD0, 3) |    // set bit 3 from D3 (PD0 from PIND)
        read_remap_bit(PIND, PD1, 2) |    // set bit 2 from D2 (PD1 from PIND)
        read_remap_bit(PIND, PD3, 1) |    // set bit 1 from D1 (PD3 from PIND)
    read_remap_bit(PIND, PD2, 0) ; // set bit 0 from D0 (PD2 from PIND)
    return data;
}

uint8_t rurp_get_data_pins() {
    uint8_t data = 0;
#ifndef READ_DATA_PINS_DIRECTLY
    for (int i = 0; i < 8; i++) {
        data |= digitalRead(i) ? 1 << i : 0x00;
    }
#else
    // Mapping the bits of the pins (D0-D7) to the correct bits in a byte
    data = read_remap_bit(PIND, PD2, 0) | // set bit 0 from D0 (PD2 from PIND)
        read_remap_bit(PIND, PD3, 1) |    // set bit 1 from D1 (PD3 from PIND)
        read_remap_bit(PIND, PD1, 2) |    // set bit 2 from D2 (PD1 from PIND)
        read_remap_bit(PIND, PD0, 3) |    // set bit 3 from D3 (PD0 from PIND)
        read_remap_bit(PIND, PD4, 4) |    // set bit 4 from D4 (PD4 from PIND)
        read_remap_bit(PINC, PC6, 5) |    // set bit 5 from D5 (PC6 from PINC)
        read_remap_bit(PIND, PD7, 6) |    // set bit 6 from D6 (PD7 from PIND)
        read_remap_bit(PINE, PE6, 7);     // set bit 7 from D7 (PE6 from PINE)
#endif
    Serial.print(LOG_INFO_MSG);
    Serial.print(": Read data: 0b");
    Serial.print(data, BIN);
    uint8_t rbyte = rurp_get_data_pins_direct();
    Serial.print(" - direct: 0b");
    Serial.print(rbyte, BIN);
    Serial.print(", equal: ");
    Serial.println(data == rbyte);
    return data;
}

void rurp_set_data_pins(uint8_t byte) {
#ifndef WRITE_DATA_PINS_DIRECTLY
    for (int i = 0; i < 8; i++) {
        digitalWrite(i, (byte & (1 << i)) ? HIGH : LOW);
    }
#else

    // Mapping the bits of the byte to the correct pins (D0-D7)
    PORTD |= remap_bit(byte, 0, PD2) | // set pin D0 (PD2 in PORTD) from bit 0
        remap_bit(byte, 1, PD3) |      // set pin D1 (PD3 in PORTD) from bit 1
        remap_bit(byte, 2, PD1) |      // set pin D2 (PD1 in PORTD) from bit 2
        remap_bit(byte, 3, PD0) |      // set pin D3 (PD0 in PORTD) from bit 3
        remap_bit(byte, 4, PD4) |      // set pin D4 (PD4 in PORTD) from bit 4
        remap_bit(byte, 6, PD7);       // set pin D6 (PD7 in PORTD) from bit 6

    PORTC |= remap_bit(byte, 5, PC6);  // set pin D5 (PC6 in PORTC) from bit 5

    PORTE |= remap_bit(byte, 7, PE6);  // set pin D7 (PE6 in PORTE) from bit 7
#endif
}


byte read_set_control_pins() {
    uint8_t byte = 0;
    byte |= read_remap_bit(PORTB, PB4, 0) | // set pin D8 (PB4 in PORTB) from byte bit 0
        read_remap_bit(PORTB, PB5, 1) |      // set pin D9 (PB5 in PORTB) from byte bit 1
        read_remap_bit(PORTB, PB6, 2) |      // set pin D10 (PB6 in PORTB) from byte bit 2
     read_remap_bit(PORTB, PB7, 3);       // set pin D11 (PB7 in PORTB) from byte bit 3
    // byte |= bit_is_set(PORTB, PB7) ? _BV(3) : 0x00;
    // byte |= digitalRead(11) ? _BV(3) : 0x00;
    byte |= read_remap_bit(PORTD, PD6, 4);  // set pin D12 (PD6 in PORTD) from byte bit 4
    byte |= read_remap_bit(PORTC, PC7, 5);  // set pin D13 (PC7 in PORTC) from byte bit 5

    return byte;
}

void rurp_set_control_pins(uint8_t byte) {
    // log_info("Setting control pins");
#ifndef WRITE_CONTROL_PINS_DIRECTLY
    for (int i = 0; i < 6; i++) {
        digitalWrite(i + 8, (byte & (1 << i)) ? HIGH : LOW);
    }

#else
    // Mapping the bits of the byte to the correct pins (D8-D13)
    PORTB &= ~PORTB_CONTROL_PINS;
    PORTD &= ~PORTD_CONTROL_PINS;
    PORTC &= ~PORTC_CONTROL_PINS;

    PORTB |= remap_bit(byte, 0, PB4) | // set pin D8 (PB4 in PORTB) from byte bit 0
        remap_bit(byte, 1, PB5) |      // set pin D9 (PB5 in PORTB) from byte bit 1
        remap_bit(byte, 2, PB6) |      // set pin D10 (PB6 in PORTB) from byte bit 2
        remap_bit(byte, 3, PB7);       // set pin D11 (PB7 in PORTB) from byte bit 3
    PORTD |= remap_bit(byte, 4, PD6);  // set pin D12 (PD6 in PORTD) from byte bit 4
    PORTC |= remap_bit(byte, 5, PC7);  // set pin D13 (PD7 in PORTD) from byte bit 5
#endif
    // Serial.print(LOG_INFO_MSG);
    // Serial.print(": ");
    // Serial.print("set: 0b");
    // Serial.print(byte, BIN);
    // uint8_t rbyte = read_set_control_pins();
    // Serial.print(" - get: 0b");
    // Serial.print(rbyte, BIN);
    // Serial.print(", equal: ");
    // Serial.println(byte == rbyte);

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
void debug_buf(const char* msg) {
    rurp_log("DEBUG", msg);
}
#endif

#endif


