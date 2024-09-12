/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 */

#include "rurp_shield.h"
#include <Arduino.h>
#include <EEPROM.h>

#if board == uno
constexpr int  CONFIG_START = 48;
constexpr int VOLTAGE_MEASURE_PIN = A2;
constexpr int HARDWARE_REVISION_PIN = A3;

constexpr int INPUT_RESOLUTION = 1023;
constexpr int AVERAGE_OF = 500;



rurp_configuration_t rurp_config;


void load_config();

uint8_t lsb_address;
uint8_t msb_address;
uint8_t control_register;

void rurp_setup() {
    pinMode(VOLTAGE_MEASURE_PIN, INPUT);
    pinMode(HARDWARE_REVISION_PIN, INPUT_PULLUP);
    rurp_set_data_as_output();
    DDRB = LEAST_SIGNIFICANT_BYTE | MOST_SIGNIFICANT_BYTE | CONTROL_REGISTER | OUTPUT_ENABLE | CHIP_ENABLE | RW;

    PORTB = OUTPUT_ENABLE | CHIP_ENABLE;
    lsb_address = 0xff;
    msb_address = 0xff;
    control_register = 0xff;
    rurp_write_to_register(LEAST_SIGNIFICANT_BYTE, 0x00);
    rurp_write_to_register(MOST_SIGNIFICANT_BYTE, 0x00);
    rurp_write_to_register(CONTROL_REGISTER, 0x00);
    load_config();
}


int rurp_get_hardware_revision(){
    int value = digitalRead(HARDWARE_REVISION_PIN);
    switch (value)
    {
    case 1:
        return 1;
    case 0:
        return 2;
    
    default:
        return -1;
    }
}

void load_config() {
    EEPROM.get(CONFIG_START, rurp_config);
    if (strcmp(rurp_config.version, CONFIG_VERSION) != 0) {
        strcpy(rurp_config.version, CONFIG_VERSION);
        rurp_config.vcc = ARDUINO_VCC;
        rurp_config.r1 = VALUE_R1;
        rurp_config.r2 = VALUE_R2;
        rurp_save_config();
    }
}

void rurp_save_config() {
    EEPROM.put(CONFIG_START, rurp_config);
}


rurp_configuration_t* rurp_get_config() {
    return &rurp_config;
}

void rurp_set_data_as_output() {
    DDRD = 0xff;
}

void rurp_set_data_as_input() {
    DDRD = 0x00;
}

// void restore_registers() {
//     uint8_t data = lsb_address;
//     lsb_address = ~lsb_address;
//     write_to_register(LEAST_SIGNIFICANT_BYTE, data);
//     data = msb_address;
//     msb_address = ~msb_address;
//     write_to_register(MOST_SIGNIFICANT_BYTE, data);
//     data = control_register;
//     control_register = ~control_register;
//     write_to_register(CONTROL_REGISTER, data);
// }


void rurp_write_to_register(uint8_t reg, uint8_t data)
{

    switch (reg) {
    case LEAST_SIGNIFICANT_BYTE:
        if (lsb_address == data) {
            return;
        }
        lsb_address = data;
        break;
    case MOST_SIGNIFICANT_BYTE:
        if (msb_address == data) {
            return;
        }
        msb_address = data;
        break;
    case CONTROL_REGISTER:
        if (control_register == data) {
            return;
        }
        control_register = data;
        break;
    default:
        return;
    }
    rurp_set_data_as_output();
    PORTD = data;
    PORTB |= reg;
    delayMicroseconds(1);
    PORTB &= ~(reg);
}

uint8_t rurp_read_from_register(uint8_t reg)
{
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

void rurp_set_control_pin(uint8_t pin, uint8_t state)
{
    if (state) {
        PORTB |= pin;
    }
    else {
        PORTB &= ~(pin);
    }
}


void rurp_write_data_buffer(uint8_t data) {
    PORTD = data;
}

uint8_t rurp_read_data_buffer() {
    return PIND;
}

double rurp_read_voltage()
{
    double refRes = rurp_config.vcc / INPUT_RESOLUTION;
    
    long r1 = rurp_config.r1;
    long r2 = rurp_config.r2;
    
    // Correct voltage divider ratio calculation
    double voltageDivider = 1.0 + static_cast<double>(r1) / r2;
    
    // Read the analog value and convert to voltage
    double vout = analogRead(VOLTAGE_MEASURE_PIN) * refRes;
    
    // Calculate the input voltage
    return vout * voltageDivider;
}

double rurp_get_voltage_average()
{
    double voltage_average = 0;
    for (int i = 0; i < AVERAGE_OF; i++) {
        voltage_average += rurp_read_voltage();
    }

    return voltage_average / AVERAGE_OF;
}

#endif
