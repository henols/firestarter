/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 */

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
void flash_write_init(firestarter_handle_t* handle);
uint16_t flash_get_chip_id(firestarter_handle_t* handle);
void flash_internal_erase(firestarter_handle_t* handle);
void flash_check_chip_id(firestarter_handle_t* handle);
void flash_enable_write(firestarter_handle_t* handle);

void configure_flash(firestarter_handle_t* handle) {
    debug("Configuring Flash");
    handle->firestarter_write_init = flash_write_init;
    handle->firestarter_erase = flash_erase;
    handle->firestarter_blank_check = flash_blank_check;
}

void flash_write_init(firestarter_handle_t* handle) {
    if (handle->chip_id > 0) {
        flash_check_chip_id(handle);
        if (handle->response_code == RESPONSE_CODE_ERROR) {
            return;
        }
    }

    if (handle->can_erase && !handle->skip_erase) {
        flash_internal_erase(handle);
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
    flash_enable_write(handle);
}

void flash_erase(firestarter_handle_t* handle) {
    if (handle->chip_id > 0) {
        flash_check_chip_id(handle);
        if (handle->response_code == RESPONSE_CODE_ERROR) {
            return;
        }
    }
    if (handle->can_erase) {
        flash_internal_erase(handle);
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

void flash_byte_flipping(firestarter_handle_t* handle, byte_flip_t* byte_flips, size_t size) {
    for (size_t i = 0; i < size; i++) {
        handle->firestarter_set_data(handle, byte_flips[i].address, byte_flips[i].byte);
    }
}

void flash_enable_write(firestarter_handle_t* handle) {
    byte_flip_t byte_flips[] = {
        {0x5555, 0xAA},
        {0x2AAA, 0x55},
        {0x5555, 0xA0},
    };
    flash_byte_flipping(handle, byte_flips, sizeof(byte_flips) / sizeof(byte_flips[0]));
}


void flash_internal_erase(firestarter_handle_t* handle) {
    byte_flip_t byte_flips[] = {
        {0x5555, 0xAA},
        {0x2AAA, 0x55},
        {0x5555, 0x80},
        {0x5555, 0xAA},
        {0x2AAA, 0x55},
        {0x5555, 0x10},
    };
    flash_byte_flipping(handle, byte_flips, sizeof(byte_flips) / sizeof(byte_flips[0]));
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

    flash_byte_flipping(handle, enable_id, sizeof(enable_id) / sizeof(enable_id[0]));
    uint16_t chip_id = handle->firestarter_get_data(handle, 0x0000) << 8;
    chip_id |= (handle->firestarter_get_data(handle, 0x0001));
    flash_byte_flipping(handle, disable_id, sizeof(disable_id) / sizeof(enable_id[0]));   
    return chip_id;

}

