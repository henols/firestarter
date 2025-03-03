/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 */


#ifdef ARDUINO_UNOR4_MINIMA
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
    control_pins = state ? (control_pins | pin) : control_pins & ~(pin);
    for (int i = 0; i < 6; i++) {
        digitalWrite(i + 8, (control_pins >> i) & 1);
    }
}

void rurp_write_data_buffer(uint8_t data) {
    rurp_set_data_output(); // Ensure data lines are output
    for (int i = 0; i < 8; i++) {
        digitalWrite(i, (data >> i) & 1);
    }
}

uint8_t rurp_read_data_buffer() {
    uint8_t data = 0;
    for (int i = 0; i < 8; i++) {
        data |= digitalRead(i) << i;
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
        pinMode(i, INPUT);
    }
}

double rurp_read_vcc() {
    // TODO: setup internal VCC reference

    return 5.0;
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


