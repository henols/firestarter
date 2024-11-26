/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 */

#include <Arduino.h>
#include "flash.h"
#include "firestarter.h"
#include "rurp_shield.h"
#include "logging.h"
#include <stdio.h>
#include "debug.h"


typedef struct byte_flip
{
    uint32_t address;
    uint8_t byte;
} byte_flip_t;


void flash_erase(firestarter_handle_t* handle);
void flash_blank_check(firestarter_handle_t* handle);
void flash_read_init(firestarter_handle_t* handle);
void flash_write_init(firestarter_handle_t* handle);
void flash_write_data(firestarter_handle_t* handle);
void flash_check_chip_id(firestarter_handle_t* handle);

uint16_t flash_get_chip_id(firestarter_handle_t* handle);
void enable_write(firestarter_handle_t* handle);
void internal_erase(firestarter_handle_t* handle);
void flip_data(firestarter_handle_t* handle, uint32_t address, uint8_t data);
void fast_address(firestarter_handle_t* handle, uint32_t address);
void verify_operation(firestarter_handle_t* handle, uint8_t expected_data);


void configure_flash(firestarter_handle_t* handle) {
    debug("Configuring Flash");
    handle->firestarter_read_init = flash_read_init;
    handle->firestarter_write_init = flash_write_init;
    handle->firestarter_write_data = flash_write_data;
    handle->firestarter_erase = flash_erase;
    handle->firestarter_blank_check = flash_blank_check;
    handle->firestarter_check_chip_id = flash_check_chip_id;
}

void flash_read_init(firestarter_handle_t* handle) {
    if (handle->chip_id > 0) {
        flash_check_chip_id(handle);
        if (handle->response_code == RESPONSE_CODE_ERROR) {
            return;
        }
    }
}

void flash_write_init(firestarter_handle_t* handle) {
    if (handle->chip_id > 0) {
        flash_check_chip_id(handle);
        if (handle->response_code == RESPONSE_CODE_ERROR) {
            return;
        }
    }

    if (handle->can_erase && !handle->skip_erase) {
        internal_erase(handle);
        delay(101);
    }
    else {
        copyToBuffer(handle->response_msg, "Skipping erase of memory");
    }
#ifdef EPROM_BLANK_CHECK
    if (handle->blank_check) {
        flash_blank_check(handle);
        if (handle->response_code == RESPONSE_CODE_ERROR) {
            return;
        }
    }
#endif
}

void flash_write_data(firestarter_handle_t* handle) {
    for (uint32_t i = 0; i < handle->data_size; i++) {
        enable_write(handle);
        handle->firestarter_set_data(handle, handle->address + i, handle->data_buffer[i]);

        verify_operation(handle, handle->data_buffer[i]);
        if (handle->response_code == RESPONSE_CODE_ERROR) {
            return;
        }
    }
    handle->response_code = RESPONSE_CODE_OK;
}

void flash_erase(firestarter_handle_t* handle) {
    if (handle->chip_id > 0) {
        flash_check_chip_id(handle);
        if (handle->response_code == RESPONSE_CODE_ERROR) {
            return;
        }
    }
    if (handle->can_erase) {
        internal_erase(handle);
    }
    else {
        copyToBuffer(handle->response_msg, "Erase not supported");
        handle->response_code = RESPONSE_CODE_ERROR;
    }
}

void flash_blank_check(firestarter_handle_t* handle) {
    for (uint32_t i = 0; i < handle->mem_size; i++) {
        uint8_t val = handle->firestarter_get_data(handle, i);
        if (val != 0xFF) {
            handle->response_code = RESPONSE_CODE_ERROR;
            format(handle->response_msg, "Memory is not blank, at 0x%06x, value: 0x%02x", i, val);
            return;
        }
    }
}

void flash_check_chip_id(firestarter_handle_t* handle) {
    uint16_t chip_id = flash_get_chip_id(handle);
    if (chip_id != handle->chip_id) {
        handle->response_code = handle->force ? RESPONSE_CODE_WARNING : RESPONSE_CODE_ERROR;
        format(handle->response_msg, "Chip ID %#x dont match expected ID %#x", chip_id, handle->chip_id);
    }
}

void byte_flipping(firestarter_handle_t* handle, byte_flip_t* byte_flips, size_t size) {
    handle->firestarter_set_control_register(handle, RW, 0);
    for (size_t i = 0; i < size; i++) {
        flip_data(handle, byte_flips[i].address, byte_flips[i].byte);
    }
    handle->firestarter_set_control_register(handle, RW, 0);
}

void enable_write(firestarter_handle_t* handle) {
    byte_flip_t byte_flips[] = {
        {0x5555, 0xAA},
        {0x2AAA, 0x55},
        {0x5555, 0xA0},
    };
    byte_flipping(handle, byte_flips, sizeof(byte_flips) / sizeof(byte_flips[0]));
}


void internal_erase(firestarter_handle_t* handle) {
    byte_flip_t byte_flips[] = {
        {0x5555, 0xAA},
        {0x2AAA, 0x55},
        {0x5555, 0x80},
        {0x5555, 0xAA},
        {0x2AAA, 0x55},
        {0x5555, 0x10},
    };
    byte_flipping(handle, byte_flips, sizeof(byte_flips) / sizeof(byte_flips[0]));
    handle->firestarter_set_address(handle, 0x0000);
    verify_operation(handle, 0xFF);
}

uint16_t flash_get_chip_id(firestarter_handle_t* handle) {
    byte_flip_t enable_id[] = {
        {0x5555, 0xAA},
        {0x2AAA, 0x55},
        {0x5555, 0x90},
    };
    byte_flip disable_id[] = {
        {0x5555, 0xAA},
        {0x2AAA, 0x55},
        {0x5555, 0xF0},
    };

    byte_flipping(handle, enable_id, sizeof(enable_id) / sizeof(enable_id[0]));
    uint16_t chip_id = handle->firestarter_get_data(handle, 0x0000) << 8;
    chip_id |= (handle->firestarter_get_data(handle, 0x0001));
    byte_flipping(handle, disable_id, sizeof(disable_id) / sizeof(enable_id[0]));
    return chip_id;
}

uint8_t data_poll() {
    rurp_set_data_as_input();
    rurp_set_control_pin(CHIP_ENABLE, 0);
    rurp_set_control_pin(OUTPUT_ENABLE, 0);
    uint8_t data = rurp_read_data_buffer();
    rurp_set_control_pin(CHIP_ENABLE, 1);
    rurp_set_control_pin(OUTPUT_ENABLE, 1);
    return data;
}

void verify_operation(firestarter_handle_t* handle, uint8_t expected_data) {

    handle->firestarter_set_control_register(handle, RW, 1);

    unsigned long now = millis();
    while (millis() - now <= 150) {

        // Check Data# Polling (DQ7)
        if ((data_poll() & 0x80) == (expected_data & 0x80)) { //Only check if bit 7 has flipped
            // Verify completion with an additional read
            if ((data_poll() & 0x80) == (data_poll() & 0x80)) { //No assuming other bits
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

void flip_data(firestarter_handle_t* handle, uint32_t address, uint8_t data) {
    rurp_set_data_as_output();
    fast_address(handle, address);
    rurp_write_data_buffer(data);
    rurp_set_control_pin(CHIP_ENABLE, 0);
    rurp_set_control_pin(CHIP_ENABLE, 1);
}

void fast_address(firestarter_handle_t* handle, uint32_t address) {
    uint8_t lsb = address & 0xFF;
    rurp_write_to_register(LEAST_SIGNIFICANT_BYTE, lsb);
    uint8_t msb = ((address >> 8) & 0xFF);
    rurp_write_to_register(MOST_SIGNIFICANT_BYTE, msb);
}