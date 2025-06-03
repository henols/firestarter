/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 */

#ifndef __RURP_SHIELD_H__
#define __RURP_SHIELD_H__

#ifdef __cplusplus
extern "C" {
#endif

#include <stdint.h>
#include <stddef.h>
#include <string.h>

#define VOLTAGE_MEASURE_PIN A2

    // CONTROL REGISTER
#ifndef HARDWARE_REVISION
#define VPE_TO_VPP      0x01
#define ADDRESS_LINE_16             VPE_TO_VPP
#define A9_VPP_ENABLE   0x02
#define VPE_ENABLE      0x04
#define P1_VPP_ENABLE   0x08
#define ADDRESS_LINE_17             0x10
#define ADDRESS_LINE_18             0x20
#define READ_WRITE      0x40
#define REGULATOR       0x80

#else
#define HARDWARE_REVISION_PIN A3
#define REVISION_0 0
#define REVISION_1 1
#define REVISION_2 2

#define ADDRESS_LINE_16             0x01
#define A9_VPP_ENABLE   0x02
#define VPE_ENABLE      0x04
#define P1_VPP_ENABLE   0x08
#define ADDRESS_LINE_17             0x10
#define ADDRESS_LINE_18             0x20
#define READ_WRITE      0x40
#define REGULATOR       0x80
#define VPE_TO_VPP      0x100

#endif

#define ADDRESS_LINE_13             0x20

#ifdef HARDWARE_REVISION
// REV 1
#define REV_1_VPE_TO_VPP      0x01
#define REV_1_A9_VPP_ENABLE   0x02
#define REV_1_VPE_ENABLE      0x04
#define REV_1_P1_VPP_ENABLE   0x08
#define REV_1_RW              0x40
#define REV_1_REGULATOR       0x80

#define REV_1_ADDRESS_LINE_16             REV_1_VPE_TO_VPP
#define REV_1_ADDRESS_LINE_17             0x10
#define REV_1_ADDRESS_LINE_18             0x20

// REV 2
#define REV_2_VPE_TO_VPP      0x01
#define REV_2_A9_VPP_ENABLE   0x02
#define REV_2_VPE_ENABLE      0x04
#define REV_2_P1_VPP_ENABLE   0x08
#define REV_2_ADDRESS_LINE_17             0x10
#define REV_2_ADDRESS_LINE_16             0x20
#define REV_2_RW              0x40
#define REV_2_REGULATOR       0x80

#define REV_2_ADDRESS_LINE_18             P1_VPP_ENABLE
#endif


// Constants
#define CONFIG_VERSION "VER06"

// Default configuration
#define VALUE_R1 270000
#define VALUE_R2 44000

// Bit masks
#define LEAST_SIGNIFICANT_BYTE 0x01  // LEAST SIGNIFICANT BYTE
#define MOST_SIGNIFICANT_BYTE 0x02   // MOST SIGNIFICANT BYTE
#define OUTPUT_ENABLE 0x04           // OUTPUT ENABLE
#define CONTROL_REGISTER 0x08        // CONTROL REGISTER
#define CHIP_ENABLE 0x20             // CHIP ENABLE


#ifndef HARDWARE_REVISION
#define rurp_register_t uint8_t
#else
#define rurp_register_t uint16_t
#endif

// Struct definition
    typedef struct rurp_configuration {
        char version[6];
        long  r1;
        long  r2;
        uint8_t hardware_revision;
    } rurp_configuration_t;

    // Function prototypes
    void rurp_board_setup();
    void rurp_load_config();


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

    void rurp_set_data_output();
    void rurp_set_data_input();

#define rurp_chip_enable() rurp_set_chip_enable(0)  // CE (chip enable) on, enable chip
#define rurp_chip_disable() rurp_set_chip_enable(1) // CE (chip enable) off, disable chip
#define rurp_chip_output() rurp_set_chip_output(0)  // OE (output enable) on, enable output
#define rurp_chip_input() rurp_set_chip_output(1)   // OE (output enable) off, enable input


#define rurp_set_chip_enable(state) rurp_set_control_pin(CHIP_ENABLE, state)
#define rurp_set_chip_output(state) rurp_set_control_pin(OUTPUT_ENABLE, state)

    void rurp_set_control_pin(uint8_t pin, uint8_t state);

    void rurp_write_to_register(uint8_t reg, rurp_register_t data);
    rurp_register_t rurp_read_from_register(uint8_t reg);

    void rurp_write_data_buffer(uint8_t data);
    uint8_t rurp_read_data_buffer();

    double rurp_read_vcc();
    double rurp_read_voltage();

    uint8_t rurp_user_button_pressed();

    rurp_configuration_t* rurp_get_config();
    void rurp_save_config(rurp_configuration_t* config);
    void rurp_validate_config(rurp_configuration_t* config);

#ifdef HARDWARE_REVISION
    void rurp_detect_hardware_revision();
    uint8_t rurp_get_hardware_revision();
    uint8_t rurp_get_physical_hardware_revision();
    uint8_t rurp_map_ctrl_reg_for_hardware_revision(rurp_register_t data);
#endif

#ifdef __cplusplus
}
#endif

#endif // __RURP_SHIELD_H__
