/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 */

#include "flash_type_4.h"

#include <Arduino.h>
#include "memory_utils.h"
#include "flash_utils.h"
#include "firestarter.h"
#include "logging.h"
#include "operation_utils.h"

void flash4_erase_execute(firestarter_handle_t* handle);
void flash4_write_init(firestarter_handle_t* handle);
void flash4_write_execute(firestarter_handle_t* handle);

void configure_flash4(firestarter_handle_t* handle) {
    debug("Configuring Flash 4");
    switch (handle->cmd) {
    case CMD_WRITE:
        handle->firestarter_operation_init = flash4_write_init;
        handle->firestarter_operation_main = flash4_write_execute;
        break;
    case CMD_ERASE:
        handle->firestarter_operation_main = flash4_erase_execute;
        break;
    case CMD_BLANK_CHECK:
        handle->firestarter_operation_main = mem_util_blank_check;
        break;
    }
}

void flash4_write_init(firestarter_handle_t* handle) {
    if(!is_operation_in_progress(handle)){
        if (handle->response_code == RESPONSE_CODE_ERROR) {
            return;
        }

        if (is_flag_set(FLAG_CAN_ERASE)) {
            if (!is_flag_set(FLAG_SKIP_ERASE)) {
                flash4_erase_execute(handle);
            } else {
                copy_to_buffer(handle->response_msg, "Skipping erase.");
            }
        }
    }
    if (!is_flag_set(FLAG_SKIP_BLANK_CHECK)) {
        mem_util_blank_check(handle);
    }
}

void flash4_write_execute(firestarter_handle_t* handle) {
    for (uint32_t i = 0; i < handle->data_size; i++) {
        handle->firestarter_set_data(handle, handle->address + i, handle->data_buffer[i]);

        if ((handle->address + i) % 64 == 63) {            
            //We can only write 64 bytes per page-write, then we
            //poll the last byte written until it's correct.
            for (uint32_t j = 0; j < 1000; j++) {
                delayMicroseconds(10);
                uint8_t byte = handle->firestarter_get_data(handle, handle->address + i);
                if (byte == handle->data_buffer[i])
                    break;
            }
        }
    }
}

void flash4_erase_execute(firestarter_handle_t* handle) {
    uint32_t address;

    //Intial state:
    address = mem_util_remap_address_bus(handle, 0, READ_FLAG);
    handle->firestarter_set_address(handle, address);
    rurp_chip_disable();
    handle->firestarter_set_control_register(handle, REGULATOR | VPE_TO_VPP | VPE_ENABLE, 0);

    delay(2);

    //^CE -> LOW
    rurp_chip_enable();

    //^OE -> 12v
    handle->firestarter_set_control_register(handle, REGULATOR | VPE_TO_VPP | VPE_ENABLE, 1);

    delay(2);
    //^WE -> LOW
    address = mem_util_remap_address_bus(handle, 0, WRITE_FLAG);
    handle->firestarter_set_address(handle, address);
    delay(20);
    //^WE -> HIGH
    address = mem_util_remap_address_bus(handle, 0, READ_FLAG);
    handle->firestarter_set_address(handle, address);
    delay(2);

    //^CE -> LOW
    rurp_chip_disable();

    //^OE -> 12v
    handle->firestarter_set_control_register(handle, REGULATOR | VPE_TO_VPP | VPE_ENABLE, 0);
}