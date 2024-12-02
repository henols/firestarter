/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 */

#include <Arduino.h>
#include "flash_type_2.h"
#include "memory_utils.h"
#include "firestarter.h"
#include "rurp_shield.h"
#include "logging.h"
#include <stdio.h>
#include "debug.h"

typedef struct chip_info {
    union chip {
        uint16_t id;
        struct {
            uint8_t device;
            uint8_t manufacturer;
        };
    } chip;

    uint8_t high_boot_lockout;
    uint8_t low_boot_lockout;
} chip_info_t;


void flash_2_erase(firestarter_handle_t* handle);
void flash_2_blank_check(firestarter_handle_t* handle);
void flash_2_read_init(firestarter_handle_t* handle);
void flash_2_write_init(firestarter_handle_t* handle);
void flash_2_check_chip_id(firestarter_handle_t* handle);
void flash_2_set_data(firestarter_handle_t* handle, uint32_t address, uint8_t data);

void f2_get_chip_id(firestarter_handle_t* handle, chip_info_t* chip_info);
void f2_internal_erase(firestarter_handle_t* handle);
void f2_dissable_protection(firestarter_handle_t* handle);
void f2_enable_protection(firestarter_handle_t* handle);

void (*f2_set_data)(struct firestarter_handle*, uint32_t, uint8_t);

void configure_flash_2(firestarter_handle_t* handle) {
    debug("Configuring Flash");
    handle->firestarter_read_init = flash_2_read_init;
    handle->firestarter_write_init = flash_2_write_init;
    handle->firestarter_erase = flash_2_erase;
    handle->firestarter_blank_check = flash_2_blank_check;
    handle->firestarter_check_chip_id = flash_2_check_chip_id;

    f2_set_data = handle->firestarter_set_data;
    handle->firestarter_set_data = flash_2_set_data;
    handle->pulse_delay = 0;
}

void flash_2_read_init(firestarter_handle_t* handle) {
    if (handle->chip_id > 0) {
        flash_2_check_chip_id(handle);
        if (handle->response_code == RESPONSE_CODE_ERROR) {
            return;
        }
    }
}

void flash_2_write_init(firestarter_handle_t* handle) {
    if (handle->chip_id > 0) {
        flash_2_check_chip_id(handle);
        if (handle->response_code == RESPONSE_CODE_ERROR) {
            return;
        }
    }
    f2_dissable_protection(handle);
    if (handle->can_erase && !handle->skip_erase) {
        f2_internal_erase(handle);
    }
    else {
        copyToBuffer(handle->response_msg, "Skipping erase of memory");
    }
#ifdef EPROM_BLANK_CHECK
    if (handle->blank_check) {
        flash_2_blank_check(handle);
        if (handle->response_code == RESPONSE_CODE_ERROR) {
            return;
        }
    }
#endif
}
void flash_2_set_data(firestarter_handle_t* handle, uint32_t address, uint8_t data) {
    f2_set_data(handle, address, data);
    utils_verify_flash_operation(handle, data);
}

void flash_2_erase(firestarter_handle_t* handle) {
    if (handle->chip_id > 0) {
        flash_2_check_chip_id(handle);
        if (handle->response_code == RESPONSE_CODE_ERROR) {
            return;
        }
    }
    f2_dissable_protection(handle);
    f2_internal_erase(handle);
    f2_enable_protection(handle);
}

void flash_2_blank_check(firestarter_handle_t* handle) {
    for (uint32_t i = 0; i < handle->mem_size; i++) {
        uint8_t val = handle->firestarter_get_data(handle, i);
        if (val != 0xFF) {
            handle->response_code = RESPONSE_CODE_ERROR;
            format(handle->response_msg, "Memory is not blank, at 0x%06x, value: 0x%02x", i, val);
            return;
        }
    }
}

void flash_2_check_chip_id(firestarter_handle_t* handle) {
    chip_info_t chip_info;
    f2_get_chip_id(handle, &chip_info);
    if (chip_info.chip.id != handle->chip_id) {
        handle->response_code = handle->force ? RESPONSE_CODE_WARNING : RESPONSE_CODE_ERROR;
        format(handle->response_msg, "Chip ID %#x dont match expected ID %#x", chip_info.chip.id, handle->chip_id);
    }
    else {
        format(handle->response_msg, "Boot block lockout, low: %d, high: %d", chip_info.low_boot_lockout & 0x01, chip_info.high_boot_lockout & 0x01);
    }
}

void f2_dissable_protection(firestarter_handle_t* handle) {
    utils_flash_byte_flipping(handle, flash_disable_write_protection, sizeof(flash_disable_write_protection) / sizeof(flash_disable_write_protection[0]));
}

void f2_enable_protection(firestarter_handle_t* handle) {
    utils_flash_byte_flipping(handle, flash_enable_write_protection, sizeof(flash_enable_write_protection) / sizeof(flash_enable_write_protection[0]));
}

void f2_internal_erase(firestarter_handle_t* handle) {
    utils_flash_byte_flipping(handle, flash_erase, sizeof(flash_erase) / sizeof(flash_erase[0]));
    delayMicroseconds(1);
    utils_verify_flash_operation(handle, 0xFF);
}

void f2_get_chip_id(firestarter_handle_t* handle, chip_info_t* chip_info) {
    utils_flash_byte_flipping(handle, flash_enable_id, sizeof(flash_enable_id) / sizeof(flash_enable_id[0]));

    chip_info->chip.device = handle->firestarter_get_data(handle, 0x0001);
    chip_info->chip.manufacturer = handle->firestarter_get_data(handle, 0x0000);
    chip_info->low_boot_lockout = handle->firestarter_get_data(handle, 0x0002);
    chip_info->high_boot_lockout = handle->firestarter_get_data(handle, handle->mem_size - 0x0e);
    handle->firestarter_set_address(handle, 0x0000);
    utils_flash_byte_flipping(handle, flash_disable_id, sizeof(flash_disable_id) / sizeof(flash_disable_id[0]));
}

