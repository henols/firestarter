/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 */

#include "flash_type_4.h"

#include <Arduino.h>

#include "firestarter.h"
#include "flash_utils.h"
#include "logging.h"
#include "memory_utils.h"
#include "operation_utils.h"

#define PAGE_SIZE 64

void flash4_erase_execute(firestarter_handle_t* handle);
void flash4_write_init(firestarter_handle_t* handle);
void flash4_write_execute(firestarter_handle_t* handle);
static bool flash4_wait_for_page_write(firestarter_handle_t* handle, uint32_t address, uint8_t expected);

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
    if (!is_operation_in_progress(handle)) {
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
        uint32_t address = handle->address + i;
        uint8_t expected = handle->data_buffer[i];
        handle->firestarter_set_data(handle, address, expected);

        // We can only write 64 bytes per page-write, then we
        bool reached_page_end = ((address) % PAGE_SIZE) == PAGE_SIZE - 1;
        bool is_last_byte = i == handle->data_size - 1;
        if (reached_page_end || is_last_byte) {
            if (!flash4_wait_for_page_write(handle, address, expected)) {
                return;
            }
        }
    }
}

static bool flash4_wait_for_page_write(firestarter_handle_t* handle, uint32_t address, uint8_t expected) {
    // poll the last byte written until it's correct.
    uint8_t observed = 0;
    for (uint16_t j = 0; j < 1024; j++) {
        delayMicroseconds(10);
        observed = handle->firestarter_get_data(handle, address);
        if (observed == expected) {
            return true;
        }
    }

    firestarter_error_response_format("Timeout verifying 0x%02x at 0x%06lx (got 0x%02x)", expected, address, observed);
    return false;
}

void flash4_erase_execute(firestarter_handle_t* handle) {
    uint32_t address;

    // Intial state:
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
