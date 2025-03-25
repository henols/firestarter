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
#include "rurp_shield.h"
#include "memory_utils.h"
#include "logging.h"
#include "operation_utils.h"

bool dt_set_registers(firestarter_handle_t* handle) {
    if(rurp_communication_available() < 5 or !op_check_for_ok(handle)){
       return false;
    };

    uint8_t msb = rurp_communication_read();
    uint8_t lsb = rurp_communication_read();
    uint8_t ctrl_reg = rurp_communication_read();

    log_info_format("MSB: 0x%02x, LSB: 0x%02x, CTRL: 0x%02x, CE: %d, OE: %d", msb, lsb, ctrl_reg, is_flag_set(FLAG_CHIP_ENABLE), is_flag_set(FLAG_OUTPUT_ENABLE), handle->ctrl_flags);
    rurp_set_programmer_mode();

    rurp_write_to_register(LEAST_SIGNIFICANT_BYTE, lsb);
    rurp_write_to_register(MOST_SIGNIFICANT_BYTE, msb);
    rurp_write_to_register(CONTROL_REGISTER, ctrl_reg);

    rurp_set_chip_enable(is_flag_set(FLAG_CHIP_ENABLE) == 0);
    rurp_set_chip_output(is_flag_set(FLAG_OUTPUT_ENABLE) == 0);

    while (true) {
        delay(200);
    }
    rurp_set_communication_mode();

    return true;
}

bool dt_set_address(firestarter_handle_t* handle) {
    uint32_t address = mem_util_remap_address_bus(handle, handle->address, is_flag_set(FLAG_OUTPUT_ENABLE));
    log_info_format("Address: 0x%06x, CE: %d, OE: %d, flags: %d", handle->address, is_flag_set(FLAG_CHIP_ENABLE), is_flag_set(FLAG_OUTPUT_ENABLE), handle->ctrl_flags);
    log_info_format("Remappend address: 0x%06x", address);
    rurp_set_programmer_mode();

    mem_util_set_address(handle, address);

    rurp_set_chip_enable(is_flag_set(FLAG_CHIP_ENABLE) == 0);
    rurp_set_chip_output(is_flag_set(FLAG_OUTPUT_ENABLE) == 0);
    while (true) {
        delay(200);
    }
    rurp_set_communication_mode();

    return true;
}

#endif