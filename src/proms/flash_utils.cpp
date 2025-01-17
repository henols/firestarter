/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 */

#include "flash_utils.h"
#include <Arduino.h>
#include "rurp_shield.h"
#include "logging.h"
#include <stdio.h>


void fu_flash_flip_data(firestarter_handle_t* handle, uint32_t address, uint8_t data);
void fu_flash_fast_address(firestarter_handle_t* handle, uint32_t address);
uint8_t fu_flash_data_poll();

void flash_byte_flipping(firestarter_handle_t* handle, const byte_flip_t* byte_flips, size_t size) {

    handle->firestarter_set_control_register(handle, RW, 0);
    for (size_t i = 0; i < size; i++) {
        fu_flash_flip_data(handle, byte_flips[i].address, byte_flips[i].byte);
    }
    handle->firestarter_set_control_register(handle, RW, 0);
}

void flash_verify_operation(firestarter_handle_t* handle, uint8_t expected_data) {

    handle->firestarter_set_control_register(handle, RW, 1);

    unsigned long timeout = millis() + 150;
    while (millis() < timeout) {
        // Check Data# Polling (DQ7)
        if ((fu_flash_data_poll() & 0x80) == (expected_data & 0x80)) { //Only check if bit 7 has flipped
            // Verify completion with an additional read
            if ((fu_flash_data_poll() & 0x80) == (fu_flash_data_poll() & 0x80)) { //No assuming other bits
                rurp_set_data_as_output();
                rurp_set_control_pin(CHIP_ENABLE, 1);
                rurp_set_control_pin(OUTPUT_ENABLE, 1);
                return;  // Operation completed successfully
            }
        }
    }
    handle->response_code = RESPONSE_CODE_ERROR;
    copy_to_buffer(handle->response_msg, "Operation timed out");
    return;
}

void fu_flash_flip_data(firestarter_handle_t* handle, uint32_t address, uint8_t data) {
    rurp_set_data_as_output();
    fu_flash_fast_address(handle, address);
    rurp_write_data_buffer(data);
    rurp_set_control_pin(CHIP_ENABLE, 0);
    rurp_set_control_pin(CHIP_ENABLE, 1);
}

void fu_flash_fast_address(firestarter_handle_t* handle, uint32_t address) {
    uint8_t lsb = address & 0xFF;
    rurp_write_to_register(LEAST_SIGNIFICANT_BYTE, lsb);
    uint8_t msb = ((address >> 8) & 0xFF);
    rurp_write_to_register(MOST_SIGNIFICANT_BYTE, msb);
}

uint8_t fu_flash_data_poll() {
    rurp_set_data_as_input();
    rurp_set_control_pin(CHIP_ENABLE, 0);
    rurp_set_control_pin(OUTPUT_ENABLE, 0);
    uint8_t data = rurp_read_data_buffer();
    rurp_set_control_pin(CHIP_ENABLE, 1);
    rurp_set_control_pin(OUTPUT_ENABLE, 1);
    return data;
}

