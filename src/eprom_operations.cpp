/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 */

#include "eprom_operations.h"

#include "firestarter.h"
#include "logging.h"
#include "operation_utils.h"
#include "rurp_shield.h"

bool _cunsume_data(const char* op_name, firestarter_handle_t* handle);

bool _write_eprom(firestarter_handle_t* handle);

bool _verify_eprom(firestarter_handle_t* handle);
// bool _read_eprom(firestarter_handle_t* handle);

bool eprom_read(firestarter_handle_t* handle) {
    if (!op_check_for_ok()) {
        return false;
    }

    debug("Read PROM");
    if (!op_execute_init(handle->firestarter_operation_init, handle)) {
        return true;
    }

    if (!op_execute_end(handle->firestarter_operation_end, handle)) {
        return true;
    }

    if ((handle->operation_state & 0x2F) == ENDED - 1) {
        return true;
    }

    if (can_operation_start(OPERATION)) {
        log_info_const("Start read");
        set_operation_state(OPERATION);
    }

    if (!op_execute_function(handle->firestarter_operation_execute, handle)) {
        return true;
    }

    log_data_format("Read: 0x%04lx - 0x%04lx", handle->address, handle->address + handle->data_size);

    rurp_communication_write(handle->data_buffer, handle->data_size);
    // debug_format("Read buffer: %.10s...", handle->data_buffer);

    handle->address += handle->data_size;
    if (handle->address > handle->mem_size - 1) {
        set_operation_state_done();
        log_done();
    }
    return false;
}
bool _write_eprom(firestarter_handle_t* handle) {
    debug("Write EPROM");
    if (_cunsume_data("Write", handle)) {
        return true;
    }
    return false;
}

bool eprom_write(firestarter_handle_t* handle) {
    return op_excecute_multi_step_operation(_write_eprom, handle);
}

bool _eprom_verify(firestarter_handle_t* handle) {
    debug("Verify PROM");
    if (_cunsume_data("Verify", handle)) {
        return true;
    }
    return false;
}
bool eprom_verify(firestarter_handle_t* handle) {
    return op_excecute_multi_step_operation(_eprom_verify, handle);
}

bool eprom_erase(firestarter_handle_t* handle) {
    if (!op_check_for_ok()) {
        return false;
    }

    debug("Erase PROM");
    if (is_flag_set(FLAG_CAN_ERASE)) {
        op_excecute_single_step_operation(handle);
        if (handle->response_code == RESPONSE_CODE_OK) {
            log_ok_const("Erased");
        }
    } else {
        log_error_const("Not supported");
    }
    return true;
}

bool eprom_check_chip_id(firestarter_handle_t* handle) {
    if (!op_check_for_ok()) {
        return false;
    }
    debug("Check Chip ID");
    if (handle->chip_id == 0) {
        log_error_const("No chip ID");
        return true;
    }
    if (!op_excecute_single_step_operation(handle)) {
        log_ok_const("Match");
    }
    return true;
}

bool eprom_blank_check(firestarter_handle_t* handle) {
    if (!op_check_for_ok()) {
        return false;
    }

    debug("Blank check PROM");
    if (!op_excecute_single_step_operation(handle)) {
        log_ok_const("Blank");
    }
    return true;
}

bool _cunsume_data(const char* op_name, firestarter_handle_t* handle) {
    int done_status = op_check_for_done();
    if (done_status != 0) {
        if (done_status == 1) {
            set_operation_state_done();
        }
        return false;
    }

    int len = op_read_data(handle);
    if (len < 1) {
        return false;
    }
    if (handle->address + len > handle->mem_size) {
        log_error_const("Address out of range");
        return true;
    }

    if (!op_execute_function(handle->firestarter_operation_execute, handle)) {
        return true;
    }

    handle->address += handle->data_size;
    log_ok_format("%s: 0x%04lx - 0x%04lx",op_name, handle->address - handle->data_size, (handle->address));

    return false;
}
