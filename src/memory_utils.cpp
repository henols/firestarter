/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 */

#include <Arduino.h>
#include "memory_utils.h"
#include "rurp_shield.h"
#include "logging.h"
#include <stdio.h>
#include "debug.h"

void mu_flash_flip_data(firestarter_handle_t* handle, uint32_t address, uint8_t data);
void mu_flash_fast_address(firestarter_handle_t* handle, uint32_t address);
uint8_t mu_flash_data_poll();

uint32_t utils_remap_address_bus(const firestarter_handle_t* handle, uint32_t address, uint8_t rw) {
    bus_config_t config = handle->bus_config;
    if (config.address_lines[0] != 0xff || config.rw_line != 0xff) {

        uint32_t reorg_address = config.address_mask & address;
        for (int i = config.matching_lines; i < 19 && config.address_lines[i] != 0xFF; i++) {
            if (config.address_lines[i] != i && address & (uint32_t)1 << i) {
                reorg_address |= (uint32_t)1 << config.address_lines[i];
            }
        }
        if (config.rw_line != 0xFF) {
            reorg_address |= (uint32_t)rw << config.rw_line;
        }
        return reorg_address;
    }
    return address;
}

void utils_flash_byte_flipping(firestarter_handle_t* handle, const byte_flip_t* byte_flips, size_t size) {

    handle->firestarter_set_control_register(handle, RW, 0);
    for (size_t i = 0; i < size; i++) {
        mu_flash_flip_data(handle, byte_flips[i].address, byte_flips[i].byte);
    }
    handle->firestarter_set_control_register(handle, RW, 0);
}

void utils_verify_flash_operation(firestarter_handle_t* handle, uint8_t expected_data) {

    handle->firestarter_set_control_register(handle, RW, 1);

    unsigned long now = millis();
    while (millis() - now <= 150) {
        // Check Data# Polling (DQ7)
        if ((mu_flash_data_poll() & 0x80) == (expected_data & 0x80)) { //Only check if bit 7 has flipped
            // Verify completion with an additional read
            if ((mu_flash_data_poll() & 0x80) == (mu_flash_data_poll() & 0x80)) { //No assuming other bits
                rurp_set_data_as_output();
                rurp_set_control_pin(CHIP_ENABLE, 1);
                rurp_set_control_pin(OUTPUT_ENABLE, 1);
                return;  // Operation completed successfully
            }
        }
    }
    handle->response_code = RESPONSE_CODE_ERROR;
    copyToBuffer(handle->response_msg, "Operation timed out");
    return;
}

void mu_flash_flip_data(firestarter_handle_t* handle, uint32_t address, uint8_t data) {
    rurp_set_data_as_output();
    mu_flash_fast_address(handle, address);
    rurp_write_data_buffer(data);
    rurp_set_control_pin(CHIP_ENABLE, 0);
    rurp_set_control_pin(CHIP_ENABLE, 1);
}

void mu_flash_fast_address(firestarter_handle_t* handle, uint32_t address) {
    uint8_t lsb = address & 0xFF;
    rurp_write_to_register(LEAST_SIGNIFICANT_BYTE, lsb);
    uint8_t msb = ((address >> 8) & 0xFF);
    rurp_write_to_register(MOST_SIGNIFICANT_BYTE, msb);
}

uint8_t mu_flash_data_poll() {
    rurp_set_data_as_input();
    rurp_set_control_pin(CHIP_ENABLE, 0);
    rurp_set_control_pin(OUTPUT_ENABLE, 0);
    uint8_t data = rurp_read_data_buffer();
    rurp_set_control_pin(CHIP_ENABLE, 1);
    rurp_set_control_pin(OUTPUT_ENABLE, 1);
    return data;
}

