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
constexpr int VOLTAGE_MESSURE_PIN = A2;

constexpr int INPUT_RESOLUTION = 1023;
constexpr int AVERAGE_OF = 500;



rurp_configuration_t rurp_config;


void load_config();

uint8_t lsb_address;
uint8_t msb_address;
uint8_t controle_register;

void rurp_setup() {
    pinMode(VOLTAGE_MESSURE_PIN, INPUT);
    set_data_as_output();
    DDRB = LEAST_SIGNIFICANT_BYTE | MOST_SIGNIFICANT_BYTE | CONTROL_REGISTER | OUTPUT_ENABLE | CHIP_ENABLE | RW;

    PORTB = OUTPUT_ENABLE | CHIP_ENABLE;
    lsb_address = 0xff;
    msb_address = 0xff;
    controle_register = 0xff;
    write_to_register(LEAST_SIGNIFICANT_BYTE, 0x00);
    write_to_register(MOST_SIGNIFICANT_BYTE, 0x00);
    write_to_register(CONTROL_REGISTER, 0x00);
    load_config();
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

void set_data_as_output() {
    DDRD = 0xff;
}

void set_data_as_input() {
    DDRD = 0x00;
}

void restore_regsiters() {
    uint8_t data = lsb_address;
    lsb_address = ~lsb_address;
    write_to_register(LEAST_SIGNIFICANT_BYTE, data);
    data = msb_address;
    msb_address = ~msb_address;
    write_to_register(MOST_SIGNIFICANT_BYTE, data);
    data = controle_register;
    controle_register = ~controle_register;
    write_to_register(CONTROL_REGISTER, data);
}


void write_to_register(uint8_t reg, uint8_t data)
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
        if (controle_register == data) {
            return;
        }
        controle_register = data;
        break;
    default:
        return;
    }

    PORTD = data;
    PORTB |= reg;
    delayMicroseconds(1);
    PORTB &= ~(reg);
}

uint8_t read_from_register(uint8_t reg)
{
    switch (reg) {
    case LEAST_SIGNIFICANT_BYTE:
        return lsb_address;
    case MOST_SIGNIFICANT_BYTE:
        return msb_address;
    case CONTROL_REGISTER:
        return controle_register;
    }
    return 0;
}

void set_control_pin(uint8_t pin, uint8_t state)
{
    if (state) {
        PORTB |= pin;
    }
    else {
        PORTB &= ~(pin);
    }
}


void write_data_buffer(uint8_t data) {
    PORTD = data;
}

uint8_t read_data_buffer() {
    return PIND;
}

float rurp_read_voltage()
{
     float refRes = rurp_config.vcc / INPUT_RESOLUTION ;
    
    // float vin =13.53;
    // float vout= 1.83;
    // float k = vin / vout;

    // return analogRead(VOLTAGE_MESSURE_PIN) * refRes * k;

    float r1 = (float)rurp_config.r1;
    float r2 = (float)rurp_config.r2;
    
    float voltageDivider = ( r1 + r2) / r2;

     return analogRead(VOLTAGE_MESSURE_PIN) * refRes * voltageDivider;
}

float rurp_get_voltage_average()
{
    float voltage_average = 0;
    for (int i = 0; i < AVERAGE_OF; i++) {
        voltage_average += rurp_read_voltage();
    }

    return voltage_average / AVERAGE_OF;
}

#endif
