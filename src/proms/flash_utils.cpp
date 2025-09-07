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
uint8_t fu_flash_data_poll_at_address(firestarter_handle_t* handle, uint32_t address);

void flash_util_byte_flipping(firestarter_handle_t* handle, const byte_flip_t* byte_flips, size_t size) {

    handle->firestarter_set_control_register(handle, READ_WRITE, 0);
    for (size_t i = 0; i < size; i++) {
        fu_flash_flip_data(handle, byte_flips[i].address, byte_flips[i].byte);
    }
    handle->firestarter_set_control_register(handle, READ_WRITE, 0);
}

void flash_util_verify_operation(firestarter_handle_t* handle, uint32_t program_address, uint8_t expected_data) {
    unsigned long start_time = millis();
    unsigned long timeout = start_time + 150; // 150ms max timeout
    
    uint8_t last_read = 0xFF;
    uint8_t current_read = 0xFF;
    bool first_read = true;
    
    while (millis() < timeout) {
        // Use the proven memory_get_data function which handles address mapping correctly
        current_read = handle->firestarter_get_data(handle, program_address);
        
        // DQ7 Check: When DQ7 matches expected data bit 7, operation is complete
        if ((current_read & 0x80) == (expected_data & 0x80)) {
            // Double-check to confirm completion (recommended by datasheets)
            uint8_t confirm_read = handle->firestarter_get_data(handle, program_address);
            if ((confirm_read & 0x80) == (expected_data & 0x80)) {
                return; // Success
            }
        }
        
        // DQ5 Check: If DQ5=1, device has exceeded internal timing limits
        if (current_read & 0x20) { // DQ5 set
            // Re-read to check if operation completed during DQ5 handling
            uint8_t dq5_reread = handle->firestarter_get_data(handle, program_address);
            if ((dq5_reread & 0x80) == (expected_data & 0x80)) {
                return; // Operation completed successfully
            } else {
                // True timeout error - operation failed
                firestarter_error_response("Flash operation failed (DQ5 timeout)");
                return;
            }
        }
        
        // DQ6 Toggle Check: DQ6 should toggle during operation, stop when complete
        if (!first_read) {
            bool dq6_toggling = ((current_read ^ last_read) & 0x40) != 0;
            if (!dq6_toggling) {
                // DQ6 stopped toggling - operation may be complete
                // Verify with DQ7 check
                if ((current_read & 0x80) == (expected_data & 0x80)) {
                    return; // Success
                }
            }
        }
        
        last_read = current_read;
        first_read = false;
        
        // Small delay to prevent bus hammering
        delayMicroseconds(10);
    }
    
    // Final timeout
    firestarter_error_response("Flash operation timed out");
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

uint8_t fu_flash_data_poll_at_address(firestarter_handle_t* handle, uint32_t address) {
    handle->firestarter_set_address(handle, address);
    rurp_set_data_input();
    rurp_chip_enable();
    rurp_chip_output();
    uint8_t data = rurp_read_data_buffer();
    rurp_chip_disable();
    rurp_chip_input();
    return data;
}
