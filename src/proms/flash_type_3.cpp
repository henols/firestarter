/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 */

#include "flash_type_3.h"
#include <Arduino.h>
#include "flash_utils.h"
#include "memory_utils.h"
#include "firestarter.h"
#include "rurp_shield.h"
#include "logging.h"
#include <stdio.h>


void flash3_erase_execute(firestarter_handle_t* handle);

void flash3_write_init(firestarter_handle_t* handle);
void flash3_write_execute(firestarter_handle_t* handle);
void flash3_check_chip_id_execute(firestarter_handle_t* handle);

void flash3_generic_init(firestarter_handle_t* handle);

uint16_t flash3_get_chip_id(firestarter_handle_t* handle);

void f3_enable_write(firestarter_handle_t* handle);
void f3_internal_erase(firestarter_handle_t* handle);

void configure_flash3(firestarter_handle_t* handle) {
    debug("Configuring Flash type 3");
    handle->firestarter_operation_init = flash3_generic_init;
    switch (handle->state) {
    case STATE_WRITE:
        handle->firestarter_operation_init = flash3_write_init;
        handle->firestarter_operation_execute = flash3_write_execute;
        break;
    case STATE_ERASE:
        handle->firestarter_operation_execute = flash3_erase_execute;
        handle->firestarter_operation_end = memory_blank_check;
        break;
    case STATE_BLANK_CHECK:
        handle->firestarter_operation_execute = memory_blank_check;
        break;
    case STATE_CHECK_CHIP_ID:
        handle->firestarter_operation_init = NULL;
        handle->firestarter_operation_execute = flash3_check_chip_id_execute;
        break;
    }
}

void flash3_generic_init(firestarter_handle_t* handle) {
    if (handle->chip_id > 0) {
        flash3_check_chip_id_execute(handle);
    }
}

void flash3_write_init(firestarter_handle_t* handle) {
    flash3_generic_init(handle);
    if (handle->response_code == RESPONSE_CODE_ERROR) {
        return;
    }

    if (is_flag_set(FLAG_CAN_ERASE)) {
        if (!is_flag_set(FLAG_SKIP_ERASE)) {
            f3_internal_erase(handle);
            delay(105); //Old chips, worst case assumed to 5% longer to erase 
            // verify operation?
        }
        else {
            debug("Skipping erase of memory");
            copy_to_buffer(handle->response_msg, "Skipping erase of memory");
        }
    }
#ifdef EPROM_BLANK_CHECK
    if (!is_flag_set(FLAG_SKIP_BLANK_CHECK)) {
        memory_blank_check(handle);
    }
#endif
}

void flash3_write_execute(firestarter_handle_t* handle) {
    for (uint32_t i = 0; i < handle->data_size; i++) {
        // enable write
        flash_byte_flipping(handle, flash_enable_write, sizeof(flash_enable_write) / sizeof(flash_enable_write[0]));
        handle->firestarter_set_data(handle, handle->address + i, handle->data_buffer[i]);

        flash_verify_operation(handle, handle->data_buffer[i]);
        if (handle->response_code == RESPONSE_CODE_ERROR) {
            return;
        }
    }
    handle->response_code = RESPONSE_CODE_OK;
}

void flash3_erase_execute(firestarter_handle_t* handle) {
    if (is_flag_set(FLAG_CAN_ERASE)) {
        f3_internal_erase(handle);
    }
    else {
        copy_to_buffer(handle->response_msg, "Erase not supported");
        handle->response_code = RESPONSE_CODE_ERROR;
    }
}

uint16_t flash3_get_chip_id(firestarter_handle_t* handle) {
    flash_byte_flipping(handle, flash_enable_id, sizeof(flash_enable_id) / sizeof(flash_enable_id[0]));
    uint16_t chip_id = handle->firestarter_get_data(handle, 0x0000) << 8;
    chip_id |= (handle->firestarter_get_data(handle, 0x0001));
    flash_byte_flipping(handle, flash_disable_id, sizeof(flash_disable_id) / sizeof(flash_enable_id[0]));
    return chip_id;
}

void flash3_check_chip_id_execute(firestarter_handle_t* handle) {
    uint16_t chip_id = flash3_get_chip_id(handle);
    if (chip_id != handle->chip_id) {
        handle->response_code = is_flag_set(FLAG_FORCE) ? RESPONSE_CODE_WARNING : RESPONSE_CODE_ERROR;
        format(handle->response_msg, "Chip ID %#x dont match expected ID %#x", chip_id, handle->chip_id);
    }
}


void f3_enable_write(firestarter_handle_t* handle) {
    flash_byte_flipping(handle, flash_enable_write, sizeof(flash_enable_write) / sizeof(flash_enable_write[0]));
}


void f3_internal_erase(firestarter_handle_t* handle) {
    flash_byte_flipping(handle, flash_erase, sizeof(flash_erase) / sizeof(flash_erase[0]));
    handle->firestarter_set_address(handle, 0x0000);
    flash_verify_operation(handle, 0xFF);
}

