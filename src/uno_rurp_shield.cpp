/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 */

#include "rurp_shield.h"
#include <Arduino.h>
#include <EEPROM.h>
#include "config.h"

#if board == uno
constexpr int CONFIG_START = 48;
constexpr int VOLTAGE_MEASURE_PIN = A2;
constexpr int HARDWARE_REVISION_PIN = A3;

constexpr int INPUT_RESOLUTION = 1023;
constexpr int AVERAGE_OF = 500;

#ifdef HARDWARE_REVISION

// REV 1
#define REV_1_VPE_TO_VPP      0x01
#define REV_1_A9_VPP_ENABLE   0x02
#define REV_1_VPE_ENABLE      0x04
#define REV_1_P1_VPP_ENABLE   0x08
#define REV_1_RW              0x40
#define REV_1_REGULATOR       0x80

#define REV_1_A16             REV_1_VPE_TO_VPP
#define REV_1_A17             0x10
#define REV_1_A18             0x20

// REV 2
#define REV_2_VPE_TO_VPP      0x01
#define REV_2_A9_VPP_ENABLE   0x02
#define REV_2_VPE_ENABLE      0x04
#define REV_2_P1_VPP_ENABLE   0x08
#define REV_2_P30             0x10
#define REV_2_P2              0x20
#define REV_2_P31             0x40
#define REV_2_REGULATOR       0x80

#define REV_2_P1              P1_VPP_ENABLE
#define REV_2_RW              REV_2_P31
#define REV_2_A16             REV_2_P2
#define REV_2_A17             REV_2_P30
#define REV_2_A18             P1_VPP_ENABLE
#endif

rurp_configuration_t rurp_config;


void load_config();

uint8_t lsb_address;
uint8_t msb_address;
register_t control_register;

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

#ifdef HARDWARE_REVISION
int rurp_get_hardware_revision() {
    int value = digitalRead(HARDWARE_REVISION_PIN);
    switch (value)
    {
    case 1:
        return REVISISION_1;
    case 0:
        return REVISISION_2;

    default:
        // Unknown hardware revision
        return -1;
    }
}
#endif

void load_config() {
    EEPROM.get(CONFIG_START, rurp_config);
    if (strcmp(rurp_config.version, "VER03") == 0) {
        strcpy(rurp_config.version, CONFIG_VERSION);
        rurp_config.hardware_revision = 0;
        rurp_save_config();
    } else if (strcmp(rurp_config.version, CONFIG_VERSION) != 0) {
        strcpy(rurp_config.version, CONFIG_VERSION);
        rurp_config.vcc = ARDUINO_VCC;
        rurp_config.r1 = VALUE_R1;
        rurp_config.r2 = VALUE_R2;
        rurp_config.hardware_revision = 0;
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

#ifdef HARDWARE_REVISION
uint8_t map_ctrl_reg_to_hardware_revision(uint16_t data) {
    uint8_t ctrl_reg = 0;
    int hw = rurp_get_hardware_revision();
    if(rurp_config.hardware_revision > 0) {
        hw = rurp_config.hardware_revision;
    }
    switch (hw) {
    case REVISISION_2:
        ctrl_reg = data & (A9_VPP_ENABLE | VPE_ENABLE | P1_VPP_ENABLE | A17 | RW | REGULATOR);
        ctrl_reg |= data & VPE_TO_VPP ? REV_2_VPE_TO_VPP : 0;
        ctrl_reg |= data & A16 ? REV_2_A16 : 0;
        ctrl_reg |= data & A18 ? REV_2_A18 : 0;
        break;
    case REVISISION_1:
        ctrl_reg = data;
        ctrl_reg |= data & VPE_TO_VPP ? REV_1_VPE_TO_VPP : 0;
        break;
    default:
        break;
    }

    return ctrl_reg;
}
#endif

void rurp_write_to_register(uint8_t reg, register_t data) {
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
        control_register = data;
#ifdef HARDWARE_REVISION
        data = map_ctrl_reg_to_hardware_revision(data);
#endif
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
    PORTD = data;
}

uint8_t rurp_read_data_buffer() {
    return PIND;
}

double rurp_read_voltage() {
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

double rurp_get_voltage_average() {
    double voltage_average = 0;
    for (int i = 0; i < AVERAGE_OF; i++) {
        voltage_average += rurp_read_voltage();
    }

    return voltage_average / AVERAGE_OF;
}

#endif
