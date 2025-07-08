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

bool _write_eprom_callback(firestarter_handle_t* handle);
bool _verify_eprom_callback(firestarter_handle_t* handle);

bool _process_incoming_data(const char* op_name, firestarter_handle_t* handle);
bool _process_outgoing_data(firestarter_handle_t* handle);

bool eprom_read(firestarter_handle_t* handle) {
    return !op_execute_callback_operation(_process_outgoing_data, handle);
}

bool _write_eprom_callback(firestarter_handle_t* handle) {
    debug("Write EPROM");
    // Return true if ok, false on error
    return _process_incoming_data("Write", handle);
}

bool eprom_write(firestarter_handle_t* handle) {
    return !op_execute_callback_operation(_write_eprom_callback, handle);
}

bool _verify_eprom_callback(firestarter_handle_t* handle) {
    debug("Verify PROM");
    // Return true if ok, false on error
    return _process_incoming_data("Verify", handle);
}

// Return true if the operation is done, otherwise false
bool eprom_verify(firestarter_handle_t* handle) {
    return !op_execute_callback_operation(_verify_eprom_callback, handle);
}

bool eprom_erase(firestarter_handle_t* handle) {
    debug("Erase PROM");
    if (!is_flag_set(FLAG_CAN_ERASE)) {
        log_error_const("Not supported");
        return true;
    }
    return !op_execute_operation(handle);
}

bool eprom_check_chip_id(firestarter_handle_t* handle) {
    debug("Check Chip ID");
    if (handle->chip_id == 0) {
        log_error_const("No chip ID");
        return true;
    }
    return !op_execute_operation(handle);
}

bool eprom_blank_check(firestarter_handle_t* handle) {
    debug("Blank check PROM");
    return !op_execute_operation(handle);
}

// Returns true on success/continue, false on error.
bool _process_incoming_data(const char* op_name, firestarter_handle_t* handle) {
    op_message_type msg_type = op_get_message(handle);

    switch (msg_type) {
        case OP_MSG_DONE:
            set_operation_to_done(handle);
            return true;  // Finished is a success.
        case OP_MSG_DATA:
            // Data packet was read by op_get_message and is in handle->data_buffer
            if (handle->address + handle->data_size > handle->mem_size) {
                log_error_const("Out of range");
                return false;  // Error.
            }
            break;  // Continue to process data
        case OP_MSG_INCOMPLETE:
            return true;  // Not an error, just no data yet.
        default:
            return false;  // Error or unexpected message
    }

    if (!op_execute_function(handle->firestarter_operation_main, handle)) {
        return false; // Error.
    }

    handle->address += handle->data_size;
    send_ack_format("%s: 0x%04lx - 0x%04lx", op_name, handle->address - handle->data_size, (handle->address));
    return true; // Success.
}

// Returns true on success/continue, false on error.
bool _process_outgoing_data(firestarter_handle_t* handle) {
    if (!op_execute_function(handle->firestarter_operation_main, handle)) {
        return false; // Error, so finished.
    }

    log_data_format("Read: 0x%04lx - 0x%04lx", handle->address, handle->address + handle->data_size);
    rurp_communication_write(handle->data_buffer, handle->data_size);

    if (!op_wait_for_ack(handle)) {
        return false;
    }

    handle->address += handle->data_size;
    if (handle->address >= handle->mem_size) {
        set_operation_to_done(handle);
    }
    return true; 
}
