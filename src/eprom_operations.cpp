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

bool _write_eprom(firestarter_handle_t* handle);
bool _verify_eprom(firestarter_handle_t* handle);

bool _read_data(const char* op_name, firestarter_handle_t* handle);
bool _send_data(firestarter_handle_t* handle);

bool eprom_read(firestarter_handle_t* handle) {
    // Wait for recever to be ready
    if (!op_check_ack()) {
        return false;
    }
    return op_excecute_multi_step_operation(_send_data, handle);
}

bool _write_eprom(firestarter_handle_t* handle) {
    debug("Write EPROM");
    if (_read_data("Write", handle)) {
        return true;
    }
    return false;
}

bool eprom_write(firestarter_handle_t* handle) {
    return op_excecute_multi_step_operation(_write_eprom, handle);
}

bool _eprom_verify(firestarter_handle_t* handle) {
    debug("Verify PROM");
    if (_read_data("Verify", handle)) {
        return true;
    }
    return false;
}
bool eprom_verify(firestarter_handle_t* handle) {
    return op_excecute_multi_step_operation(_eprom_verify, handle);
}

bool eprom_erase(firestarter_handle_t* handle) {
    if (!op_check_ack()) {
        return false;
    }

    debug("Erase PROM");
    if (is_flag_set(FLAG_CAN_ERASE)) {
        op_excecute_single_step_operation(handle);
        if (handle->response_code == RESPONSE_CODE_OK) {
            send_ack_const("Erased");
        }
    } else {
        log_error_const("Not supported");
    }
    return true;
}

bool eprom_check_chip_id(firestarter_handle_t* handle) {
    if (!op_check_ack()) {
        return false;
    }
    debug("Check Chip ID");
    if (handle->chip_id == 0) {
        log_error_const("No chip ID");
        return true;
    }
    if (!op_excecute_single_step_operation(handle)) {
        send_ack_const("Match");
    }
    return true;
}

bool eprom_blank_check(firestarter_handle_t* handle) {
    if (!op_check_ack()) {
        return false;
    }

    debug("Blank check PROM");
    if (!op_excecute_single_step_operation(handle)) {
        send_ack_const("Blank");
    }
    return true;
}

bool _read_data(const char* op_name, firestarter_handle_t* handle) {
    int done_status = op_check_done();
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
    send_ack_format("%s: 0x%04lx - 0x%04lx", op_name, handle->address - handle->data_size, (handle->address));

    return false;
}

bool _send_data(firestarter_handle_t* handle) {
    if (!op_execute_function(handle->firestarter_operation_execute, handle)) {
        return true;
    }

    log_data_format("Read: 0x%04lx - 0x%04lx", handle->address, handle->address + handle->data_size);

    rurp_communication_write(handle->data_buffer, handle->data_size);

    handle->address += handle->data_size;
    if (handle->address >= handle->mem_size) {
        set_operation_state_done();
        send_done();
    }
    return false;
}
