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
#include "rurp_pinout.h"
#include "rurp_vpp.h"

#ifdef HARDWARE_REVISION
#define REVISION_0 0
#define REVISION_1 1
#define REVISION_2_0 2
#define REVISION_2_1 3
#define REVISION_2_2 4
#define REVISION_2_3 5
#define REVISION_UNKNOWN 0xFE
#endif

#define VPP_P1_32_DIP               0x15
#define VPP_P1_28_DIP               0x0F
#define VPP_P21_24_DIP              0x0B

#define CONFIG_VERSION "VER07"

#define VALUE_R1 270000
#define VALUE_R2 44000

#define LEAST_SIGNIFICANT_BYTE 0x01
#define MOST_SIGNIFICANT_BYTE 0x02
#define OUTPUT_ENABLE 0x04
#define CONTROL_REGISTER 0x08
#define CHIP_ENABLE 0x20

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
int rurp_communication_read_data(char* buffer, size_t cap);

void rurp_log_id(uint8_t id, const uint8_t* params, uint8_t param_count);
void rurp_log_id_u8(uint8_t id, uint8_t v);
void rurp_log_id_u16(uint8_t id, uint16_t v);
void rurp_log_id_u24(uint8_t id, uint32_t v);
void rurp_log_id_u32(uint8_t id, uint32_t v);
void rurp_log_id_wide(uint8_t id, const uint8_t* params, uint16_t param_count);

void rurp_set_data_output();
void rurp_set_data_input();

#define rurp_chip_enable() rurp_set_chip_enable(0)
#define rurp_chip_disable() rurp_set_chip_enable(1)
#define rurp_chip_output() rurp_set_chip_output(0)
#define rurp_chip_input() rurp_set_chip_output(1)
#define rurp_set_chip_enable(state) rurp_set_control_pin(CHIP_ENABLE, state)
#define rurp_set_chip_output(state) rurp_set_control_pin(OUTPUT_ENABLE, state)

void rurp_set_control_pin(uint8_t pin, uint8_t state);
void rurp_write_to_register(uint8_t reg, rurp_register_t data);
rurp_register_t rurp_read_from_register(uint8_t reg);
void rurp_write_data_buffer(uint8_t data);
uint8_t rurp_read_data_buffer();

uint16_t rurp_read_vcc_mv();
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