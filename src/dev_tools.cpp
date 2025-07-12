/*
 * Project Name: Firestarter
 * Copyright (c) 2025 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 */

#ifdef DEV_TOOLS
#include "dev_tools.h"

#include <Arduino.h>

#include "firestarter.h"
#include "logging.h"
#include "memory_utils.h"
#include "operation_utils.h"
#include "rurp_internal_register_utils.h"
#include "rurp_shield.h"

// void rurp_internal_write_to_register(uint8_t reg, rurp_register_t data);

void dt_decode_register(firestarter_handle_t* handle, const char* reg_name, uint16_t reg, uint8_t size) {
    log_info_format("%s: 0x%02X", reg_name, reg);

    // Header
    log_info_format("%s|D7|D6|D5|D4|D3|D2|D1|D0|", size == 9 ? "|D8" : "");

    // Values - build string manually to be more efficient than many-arg sprintf
    char bit_str[40];  // "| 1" is 3 chars. 9 bits -> 3*9=27. 8 bits -> 3*8=24. 40 is safe.
    char* p = bit_str;

    if (size == 9) {
        *p++ = '|';
        *p++ = ' ';
        *p++ = ((reg >> 8) & 1) ? '1' : '0';
    }

    for (int i = 7; i >= 0; i--) {
        *p++ = '|';
        *p++ = ' ';
        *p++ = ((reg >> i) & 1) ? '1' : '0';
    }
    *p++ = '|';
    *p = '\0';

    log_info(bit_str);
}

bool dt_set_registers(firestarter_handle_t* handle) {
    // Wait for an ACK message that precedes the register data
    if (op_get_message(handle) != OP_MSG_ACK) {
        return false;
    };

    if (rurp_communication_available() < 4) {
        return false;
    };

    uint8_t msb = rurp_communication_read();
    uint8_t lsb = rurp_communication_read();
    uint16_t ctrl_reg = rurp_communication_read() << 8;
    ctrl_reg |= rurp_communication_read();
    int firestarter_reg = ctrl_reg & 0x8000;
    ctrl_reg &= 0x01FF;

    log_info_format("CE: %d, OE: %d", is_flag_set(FLAG_CHIP_ENABLE), is_flag_set(FLAG_OUTPUT_ENABLE));
    dt_decode_register(handle, "MSB", msb, 8);
    dt_decode_register(handle, "LSB", lsb, 8);
#ifdef HARDWARE_REVISION
    if (firestarter_reg) {
        dt_decode_register(handle, "CTRL", ctrl_reg, 9);
        uint8_t ctrl_version = rurp_map_ctrl_reg_for_hardware_revision(ctrl_reg);
        dt_decode_register(handle, "CTRL remapped", ctrl_version, 8);
    } else {
        dt_decode_register(handle, "CTRL", ctrl_reg, 8);
    }
#else
#endif
    send_ack("");
    rurp_set_programmer_mode();

    rurp_write_to_register(LEAST_SIGNIFICANT_BYTE, lsb);
    rurp_write_to_register(MOST_SIGNIFICANT_BYTE, msb);
    if (firestarter_reg) {
        rurp_write_to_register(CONTROL_REGISTER, ctrl_reg);
    } else {
        rurp_internal_write_to_register(CONTROL_REGISTER, ctrl_reg);
    }

    rurp_set_chip_enable(!is_flag_set(FLAG_CHIP_ENABLE));
    rurp_set_chip_output(!is_flag_set(FLAG_OUTPUT_ENABLE));

    while (!rurp_user_button_pressed()) {
        delay(200);
    }
    rurp_set_communication_mode();

    return true;
}

bool dt_set_address(firestarter_handle_t* handle) {
    log_info_format("CE: %d, OE: %d", is_flag_set(FLAG_CHIP_ENABLE), is_flag_set(FLAG_OUTPUT_ENABLE));
    log_info_format("Address: 0x%06x", handle->address);
    uint32_t address = mem_util_remap_address_bus(handle, handle->address, is_flag_set(FLAG_OUTPUT_ENABLE));
    log_info_format("Address: 0x%06x remappend", address);

    uint8_t msb = mem_util_calculate_msb_register(handle, address);
    uint8_t lsb = mem_util_calculate_lsb_register(handle, address);
    uint8_t top_address = mem_util_calculate_top_address_register(handle, address);
#ifdef HARDWARE_REVISION
    uint8_t ctrl_version = rurp_map_ctrl_reg_for_hardware_revision(top_address);
    dt_decode_register(handle, "MSB", msb, 8);
    dt_decode_register(handle, "LSB", lsb, 8);
    dt_decode_register(handle, "TOP addr", top_address, 8);
    dt_decode_register(handle, "CTRL remapped", ctrl_version, 8);
#else
    // dt_decode_ctrl(top_address);
#endif
    send_ack("");
    rurp_set_programmer_mode();
    mem_util_set_address(handle, address);
    rurp_set_chip_enable(!is_flag_set(FLAG_CHIP_ENABLE));
    rurp_set_chip_output(!is_flag_set(FLAG_OUTPUT_ENABLE));
    while (!rurp_user_button_pressed()) {
        delay(200);
    }
    rurp_set_communication_mode();

    return true;
}

#endif