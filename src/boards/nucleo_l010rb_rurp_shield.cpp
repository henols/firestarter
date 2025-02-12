/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 */


#ifdef ARDUINO_NUCLEO_L010RB
#include "rurp_shield.h"
#include <Arduino.h>
#include "rurp_config_utils.h"
#include "rurp_register_utils.h"
#include "logging.h"

#include "rurp_serial_utils.h"

constexpr int INPUT_RESOLUTION = 1023;

uint8_t control_pins = 0x00;

void rurp_board_setup() {
    for (int i = 0; i < 6; i++) {
        pinMode(i + 8, OUTPUT);
    }

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
    for (int i = 0; i < 6; i++) {
        digitalWrite(i + 8, control_pins & (1 << i));
    }
}

void rurp_write_data_buffer(uint8_t data) {
    rurp_set_data_output(); // Ensure data lines are output
    for (int i = 0; i < 8; i++) {
        digitalWrite(i + 1, control_pins & (1 << i));
    }
}

uint8_t rurp_read_data_buffer() {
    uint8_t data = 0;
    for(int i = 0; i < 8; i++) {
        data |= digitalRead(i) & (1 << i);
    }

    return data;
}

void rurp_set_data_output() {
    for (int i = 0; i < 8; i++) {
        pinMode(i + 1, OUTPUT);
    }
}

void rurp_set_data_input() {
    for (int i = 0; i < 8; i++) {
        pinMode(i , INPUT);
    }
}

double rurp_read_vcc() {
    // TODO: setup internal VCC reference
    
    // Read 1.1V reference against AVcc
    // Set the analog reference to the internal 1.1V
    // Default is analogReference(DEFAULT) which is connected to the external 5V
    // ADMUX = _BV(REFS0) | _BV(MUX4) | _BV(MUX3) | _BV(MUX2) | _BV(MUX1);

    // delay(2); // Wait for voltage to stabilize
    // ADCSRA |= _BV(ADSC); // Start conversion
    // while (bit_is_set(ADCSRA, ADSC)); // Wait for conversion to complete
    // ADCSRA |= _BV(ADSC); // Start conversion
    // while (bit_is_set(ADCSRA, ADSC)); // measuring
    // long result = ADCL;
    // result |= ADCH << 8;

    // // Calculate Vcc (supply voltage) in millivolts
    // // 1100 mV * 1024 ADC steps / ADC reading
    // return 1125300L / result / 1000;
    return 3.3;
}

double rurp_read_voltage() {
    // TODO deal with internal VCC and voltage divider
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


