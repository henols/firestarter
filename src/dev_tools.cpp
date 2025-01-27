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

bool dt_set_registers(firestarter_handle_t* handle) {
    register_t lsb = 0;
    register_t msb = 0;
    register_t ctrl_reg = 0;
    rurp_write_to_register(LEAST_SIGNIFICANT_BYTE, lsb);
    rurp_write_to_register(MOST_SIGNIFICANT_BYTE, msb);
    rurp_write_to_register(CONTROL_REGISTER, ctrl_reg);

    rurp_set_chip_enable(is_flag_set(FLAG_CHIP_ENABLE));
    rurp_set_chip_output(is_flag_set(FLAG_OUTPUT_ENABLE));
    while (true)
    {
        delay(200);
    }
    rurp_set_communication_mode();
    
    return true;
}

bool dt_set_address(firestarter_handle_t* handle) {
    uint32_t address = memory_remap_address_bus(handle, handle->address, !is_flag_set(FLAG_OUTPUT_ENABLE));
    log_info_format("Address: 0x%06x, CE: %d, OE: %d, flags: %d", address, is_flag_set(FLAG_CHIP_ENABLE), is_flag_set(FLAG_OUTPUT_ENABLE), handle->ctrl_flags); 
    rurp_set_programmer_mode();

    memory_set_address(handle, address);

    rurp_set_chip_enable(is_flag_set(FLAG_CHIP_ENABLE));
    rurp_set_chip_output(is_flag_set(FLAG_OUTPUT_ENABLE));
    while (true)
    {
        delay(200);
    }
    rurp_set_communication_mode();
    
    return true;
}

#endif