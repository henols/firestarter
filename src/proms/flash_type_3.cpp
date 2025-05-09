/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 */

#include "flash_type_3.h"

#include <Arduino.h>
#include "memory_utils.h"
#include "flash_utils.h"
#include "firestarter.h"
#include "logging.h"

void flash3_erase_execute(firestarter_handle_t* handle);
void flash3_write_init(firestarter_handle_t* handle);
void flash3_write_execute(firestarter_handle_t* handle);
void flash3_check_chip_id_execute(firestarter_handle_t* handle);

uint16_t flash3_get_chip_id(firestarter_handle_t* handle);

void flash3_generic_init(firestarter_handle_t* handle);

void configure_flash_3(firestarter_handle_t* handle) {
    debug("Configuring Flash");
    handle->firestarter_operation_init = flash3_generic_init;
    switch (handle->state) {
    case STATE_WRITE:
        handle->firestarter_operation_init = flash3_write_init;
        handle->firestarter_operation_execute = flash3_write_execute;
        break;
    case STATE_ERASE:
        handle->firestarter_operation_execute = flash3_erase_execute;
        // handle->firestarter_operation_end = m_util_blank_check;
        break;
    case STATE_BLANK_CHECK:
        handle->firestarter_operation_execute = mem_util_blank_check;
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
    if (handle->chip_id > 0) {
        flash3_check_chip_id_execute(handle);
        if (handle->response_code == RESPONSE_CODE_ERROR) {
            return;
        }
    }

    if (is_flag_set(FLAG_CAN_ERASE)) {
        if (!is_flag_set(FLAG_SKIP_ERASE)) {
            flash3_erase_execute(handle);
            delay(105); //Old chips, worst case assumed to 5% longer to erase 
        }
        else {
            debug("Skipping erase of memory");
            copy_to_buffer(handle->response_msg, "Skipping erase of memory");
        }
    }
    if (!is_flag_set(FLAG_SKIP_BLANK_CHECK)) {
        mem_util_blank_check(handle);
    }
}

void flash3_write_execute(firestarter_handle_t* handle) {
    for (uint32_t i = 0; i < handle->data_size; i++) {
        flash_execute_command(FLASH_ENABLE_WRITE);
        handle->firestarter_set_data(handle, handle->address + i, handle->data_buffer[i]);

        flash_util_verify_operation(handle, handle->data_buffer[i]);
        if (handle->response_code == RESPONSE_CODE_ERROR) {
            return;
        }
    }
}

void flash3_erase_execute(firestarter_handle_t* handle) {
    debug("Erase");
    flash_execute_command(FLASH_ERASE);
}


void flash3_check_chip_id_execute(firestarter_handle_t* handle) {
    uint16_t chip_id = flash3_get_chip_id(handle);
    if (chip_id != handle->chip_id) {
        int response_code = is_flag_set(FLAG_FORCE) ? RESPONSE_CODE_WARNING : RESPONSE_CODE_ERROR;
        firestarter_response_format(response_code, "Chip ID %#04x dont match expected ID %#04x", chip_id, handle->chip_id);
    }
}

uint16_t flash3_get_chip_id(firestarter_handle_t* handle) {
    flash_execute_command(FLASH_ENABLE_ID);
    uint16_t chip_id = handle->firestarter_get_data(handle, 0x0000) << 8;
    chip_id |= (handle->firestarter_get_data(handle, 0x0001));
    flash_execute_command(FLASH_DISABLE_ID);
    return chip_id;
}

