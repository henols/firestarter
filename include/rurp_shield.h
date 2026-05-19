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
#include <avr/pgmspace.h>
#include "rurp_types.h"

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
#define REVISION_2_0 2
#define REVISION_2_1 3
#define REVISION_2_2 4

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

#define VPP_P1_32_DIP               0x15
#define VPP_P1_28_DIP               0x0F
// 24-pin EPROM VPP magic constant. Stock DIP24_2716 pinout has vpp-pin=[21];
// the Python host's pin_conversions[24][21] = 11 = 0x0B, so the host emits
// bus_config.vpp_line = 0x0B for these chips. With this constant in place,
// using_p1_as_vpp() returns true → eprom.cpp redirects VPE_ENABLE to
// P1_VPP_ENABLE → HV exits on socket pin 1, where the operator's bodge wire
// (or Rev 2.2's built-in "red" JP4 alt-position) carries it to the chip's
// actual VPP pin (chip pin 21 = socket pin 25 with bottom-aligned 24-pin
// chip). See .planning/phases/04-hardware-validation-rurp-shield/
// 04-HW-24PIN-INVESTIGATION.md for the full hardware analysis.
#define VPP_P21_24_DIP              0x0B

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

    // Function prototypes
    void rurp_board_setup();
    void rurp_load_config();


#ifdef SERIAL_ON_IO
    void rurp_set_programmer_mode();
    void rurp_set_communication_mode();
#else
#define rurp_set_programmer_mode() ((void)0)
#define rurp_set_communication_mode() ((void)0)
#endif

    int rurp_communication_available();
    int rurp_communication_read();
    int rurp_communication_peak();
    size_t rurp_communication_write(const char* buffer, size_t size);
    size_t rurp_communication_read_bytes(char* buffer, size_t length);
    int rurp_communication_read_data(char* buffer);
    

    // Phase 9: deleted the two legacy text-prefix log declarations
    // (RAM body + PROGMEM body). See 09-CONTEXT.md D-02.

    // Phase 6 — ID-encoded wire frame emit per CONTEXT §D-01..D-04.
    // Phase 9: sole surviving log surface after the legacy text-prefix
    // helpers were deleted (LMIG-01 closed).
    void rurp_log_id(uint8_t id, const uint8_t* params, uint8_t param_count);

    // Fixed-shape packers — wrap the byte-array pack + rurp_log_id call so
    // each LOG_*_ID_U{8,16,24,32} macro invocation collapses to a single
    // CALL instruction at the call site. MSB-first wire encoding per
    // CONTEXT §D-01..D-04.
    void rurp_log_id_u8(uint8_t id, uint8_t v);
    void rurp_log_id_u16(uint8_t id, uint16_t v);
    void rurp_log_id_u24(uint8_t id, uint32_t v);
    void rurp_log_id_u32(uint8_t id, uint32_t v);

    // Phase 8 W-04 — wide variant for MSG_DATA_CHUNK payloads > 255 bytes.
    // param_count is uint16_t to avoid overflow for 512 / 1024-byte chunks.
    void rurp_log_id_wide(uint8_t id, const uint8_t* params, uint16_t param_count);

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

    uint16_t rurp_read_vcc_mv();
    uint16_t rurp_read_voltage_mv();

    long rurp_get_bandgap_adc_reading();
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
