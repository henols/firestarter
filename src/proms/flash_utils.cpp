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

void f_util_byte_flipping(firestarter_handle_t* handle, const byte_flip_t* byte_flips, size_t size) {

    handle->firestarter_set_control_register(handle, READ_WRITE, 0);
    for (size_t i = 0; i < size; i++) {
        fu_flash_flip_data(handle, byte_flips[i].address, byte_flips[i].byte);
    }
    handle->firestarter_set_control_register(handle, READ_WRITE, 0);
}

void f_util_verify_operation(firestarter_handle_t* handle, uint8_t expected_data) {

    handle->firestarter_set_control_register(handle, READ_WRITE, 1);

    unsigned long timeout = millis() + 150;
    while (millis() < timeout) {
        // Check Data# Polling (DQ7)
        // if ((fu_flash_data_poll() & 0x80) == (expected_data & 0x80)) { //Only check if bit 7 has flipped
            // Verify completion with an additional read
            if ((fu_flash_data_poll() & 0x80) == (fu_flash_data_poll() & 0x80)) { //No assuming other bits
                rurp_set_data_output();
                rurp_chip_disable();
                rurp_chip_input();
                return;  // Operation completed successfully
            }
        // }
    }
    firestarter_error_response("Operation timed out");
    return;
}

void fu_flash_flip_data(firestarter_handle_t* handle, uint32_t address, uint8_t data) {
    rurp_set_data_output();
    fu_flash_fast_address(handle, address);
    rurp_write_data_buffer(data);
    rurp_chip_input();
    rurp_chip_enable();
    rurp_chip_disable();
}

void fu_flash_fast_address(firestarter_handle_t* handle, uint32_t address) {
    uint8_t lsb = address & 0xFF;
    rurp_write_to_register(LEAST_SIGNIFICANT_BYTE, lsb);
    uint8_t msb = ((address >> 8) & 0xFF);
    rurp_write_to_register(MOST_SIGNIFICANT_BYTE, msb);
}

uint8_t fu_flash_data_poll() {
    rurp_set_data_input();
    rurp_chip_enable();
    rurp_chip_output();
    uint8_t data = rurp_read_data_buffer();
    rurp_chip_disable();
    rurp_chip_input();
    return data;
}

