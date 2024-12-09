/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 */

#ifndef RURP_SHIELD_H
#define RURP_SHIELD_H

#ifdef __cplusplus
extern "C" {
#endif

#include <stdint.h>
#include <stddef.h>
#include "config.h"
#include "rurp_defines.h"

    // Constants
#define CONFIG_VERSION  "VER05"

// Default configuration
#define ARDUINO_VCC 5.01
#define VALUE_R1 270000
#define VALUE_R2 44000

// Bit masks
#define LEAST_SIGNIFICANT_BYTE 0x01  // LEAST SIGNIFICANT BYTE
#define MOST_SIGNIFICANT_BYTE 0x02   // MOST SIGNIFICANT BYTE
#define OUTPUT_ENABLE 0x04           // OUTPUT ENABLE
#define CONTROL_REGISTER 0x08        // CONTROL REGISTER
#define USRBTN 0x10                  // USER BUTTON
#define CHIP_ENABLE 0x20             // CHIP ENABLE


#ifndef HARDWARE_REVISION
#define register_t uint8_t
#else
#define register_t uint16_t
#endif

// Struct definition
    typedef struct rurp_configuration {
        char version[6];
        double vcc;
        long  r1;
        long  r2;
        uint8_t hardware_revision;
    } rurp_configuration_t;

    // Function prototypes
    void  rurp_setup();

#ifdef SERIAL_ON_IO
    void rurp_set_programmer_mode();
    void rurp_set_communication_mode();
#else
#define rurp_set_programmer_mode();
#define rurp_set_communication_mode();
#endif
    int rurp_communication_available();
    int rurp_communication_read();
    size_t rurp_communication_write(const char* buffer, size_t size);
    size_t rurp_communication_read_bytes(char* buffer, size_t length);

    void rurp_log(const char* type, const char* msg);

    void rurp_set_data_as_output();
    void rurp_set_data_as_input();

    void rurp_set_control_pin(uint8_t pin, uint8_t state);

    void rurp_write_to_register(uint8_t reg, register_t data);
    register_t rurp_read_from_register(uint8_t reg);

    void rurp_write_data_buffer(uint8_t data);
    uint8_t rurp_read_data_buffer();

    double rurp_read_vcc();
    double rurp_read_voltage();
    double rurp_get_voltage_average();
    rurp_configuration_t* rurp_get_config();
    void rurp_save_config();

#ifdef HARDWARE_REVISION
    int rurp_get_hardware_revision();
    int rurp_get_physical_hardware_revision();

#endif

#ifdef __cplusplus
}
#endif

#endif // RURP_SHIELD_H
