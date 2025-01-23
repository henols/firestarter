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
#include "rurp_hw_rev_utils.h"

constexpr int INPUT_RESOLUTION = 1023;
constexpr int AVERAGE_OF = 500;

bool comMode = true;

#ifdef SERIAL_DEBUG
#define RX_DEBUG  A0
#define TX_DEBUG  A1

void log_debug(const char* type, const char* msg);
#else
#define log_debug(type, msg)
#endif

uint8_t lsb_address;
uint8_t msb_address;
register_t control_register;


void rurp_board_setup() {
    rurp_set_data_as_output();

    DDRB = LEAST_SIGNIFICANT_BYTE | MOST_SIGNIFICANT_BYTE | CONTROL_REGISTER | OUTPUT_ENABLE | CHIP_ENABLE | READ_WRITE;

    PORTB = OUTPUT_ENABLE | CHIP_ENABLE;
    lsb_address = 0xff;
    msb_address = 0xff;
    control_register = 0xff;
    rurp_write_to_register(LEAST_SIGNIFICANT_BYTE, 0x00);
    rurp_write_to_register(MOST_SIGNIFICANT_BYTE, 0x00);
    rurp_write_to_register(CONTROL_REGISTER, 0x00);

    rurp_set_communication_mode();
}

void rurp_set_communication_mode() {
    // rurp_set_control_pin(CHIP_ENABLE | OUTPUT_ENABLE, 1);
    DDRD &= ~(0x01);
    Serial.begin(MONITOR_SPEED); // Initialize serial port
    
    while (!Serial) {
        delayMicroseconds(1);
    }
    Serial.flush();
    // delayMicroseconds(50);
    comMode = true;
}

void rurp_set_programmer_mode() {
    comMode = false;
    Serial.end(); // Close serial port
    DDRD |= 0x01;

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
    log_debug(type, msg);
    if (comMode) {
        Serial.print(type);
        Serial.print(": ");
        Serial.println(msg);
        Serial.flush();
    }
}

void rurp_set_data_as_output() {
    DDRD = 0xff;
}

void rurp_set_data_as_input() {
    DDRD = 0x00;
}


void rurp_write_to_register(uint8_t reg, register_t data) {
    bool settle = false;
    switch (reg) {
    case LEAST_SIGNIFICANT_BYTE:
        if (lsb_address == (uint8_t)data) {
            return;
        }
        lsb_address = data;
        break;
    case MOST_SIGNIFICANT_BYTE:
        if (msb_address == (uint8_t)data) {
            return;
        }
        msb_address = data;
        break;
    case CONTROL_REGISTER:
        if (control_register == data) {
            return;
        }
        if ((control_register & P1_VPP_ENABLE) > (data & P1_VPP_ENABLE)) {
            settle = true;
        }
        control_register = data;
#ifdef HARDWARE_REVISION
        data = rurp_map_ctrl_reg_to_hardware_revision(data);
#endif
        break;
    default:
        return;
    }
    rurp_write_data_buffer(data);
    PORTB |= reg;
    // Probably useless - verify later 
    delayMicroseconds(1); 
    PORTB &= ~(reg);
    //Take a break here if an address change needs time to settle
    if (settle)
    {
        delayMicroseconds(4);
    }
}

register_t rurp_read_from_register(uint8_t reg) {
    switch (reg) {
    case LEAST_SIGNIFICANT_BYTE:
        return lsb_address;
    case MOST_SIGNIFICANT_BYTE:
        return msb_address;
    case CONTROL_REGISTER:
        return control_register;
    }
    return 0;
}

void rurp_set_control_pin(uint8_t pin, uint8_t state) {
    if (state) {
        PORTB |= pin;
    }
    else {
        PORTB &= ~(pin);
    }
}


void rurp_write_data_buffer(uint8_t data) {
    rurp_set_data_as_output();
    PORTD = data;
}

uint8_t rurp_read_data_buffer() {
    return PIND;
}

double rurp_read_vcc() {
    // Read 1.1V reference against AVcc
    // Set the analog reference to the internal 1.1V
    // Default is analogReference(DEFAULT) which is connected to the external 5V
    ADMUX = _BV(REFS0) | _BV(MUX3) | _BV(MUX2) | _BV(MUX1);

    delay(2); // Wait for voltage to stabilize
    ADCSRA |= _BV(ADSC); // Start conversion
    while (bit_is_set(ADCSRA, ADSC)); // Wait for conversion to complete

    long result = ADCL;
    result |= ADCH << 8;

    // Calculate Vcc (supply voltage) in millivolts
    // 1100 mV * 1024 ADC steps / ADC reading
    return 1126400L / (double)result / 1000;
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

double rurp_get_voltage_average() {
    double voltage_average = 0;
    for (int i = 0; i < AVERAGE_OF; i++) {
        voltage_average += rurp_read_voltage();
    }

    return voltage_average / AVERAGE_OF;
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

void log_debug(const char* type, const char* msg) {
    debugSerial.print(type);
    debugSerial.print(": ");
    debugSerial.println(msg);
    debugSerial.flush();
}
#endif
#endif
