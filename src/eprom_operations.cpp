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

static inline bool _process_incoming_data(firestarter_handle_t* handle);
static inline bool _process_outgoing_data(firestarter_handle_t* handle);

bool eprom_read(firestarter_handle_t* handle) {
    return !op_execute_stateful_operation(_process_outgoing_data, handle);
}

bool eprom_write(firestarter_handle_t* handle) {
#ifdef SERIAL_DEBUG
    debug("Write EPROM");
#endif
    return !op_execute_stateful_operation(_process_incoming_data, handle);
}

// Return true if the operation is done, otherwise false
bool eprom_verify(firestarter_handle_t* handle) {
#ifdef SERIAL_DEBUG
    debug("Verify PROM");
#endif
    return !op_execute_stateful_operation(_process_incoming_data, handle);
}

bool eprom_erase(firestarter_handle_t* handle) {
    debug("Erase PROM");
    if (!is_flag_set(FLAG_CAN_ERASE)) {
        log_error_const("Not supported");
        return true;
    }
    return !op_execute_simple_operation(handle);
}

bool eprom_check_chip_id(firestarter_handle_t* handle) {
    debug("Check Chip ID");
    if (handle->chip_id == 0) {
        log_error_const("No chip ID");
        return true;
    }
    return !op_execute_simple_operation(handle);
}

bool eprom_blank_check(firestarter_handle_t* handle) {
    debug("Blank check PROM");
    return !op_execute_simple_operation(handle);
}

// Returns true on success/continue, false on error.
static inline bool _process_incoming_data(firestarter_handle_t* handle) {
    // The operation is "pull" based. The firmware requests a data chunk when it's ready.
    // This provides software flow control and allows for larger data chunks, improving speed.
    // We use a state flag to track if we are waiting for data.
    if (handle->address >= handle->mem_size) {
        set_operation_to_done(handle);
        return true;
    }

    // 1. Check for an incoming message from the host first. This prevents a race
    // condition where the firmware requests data after the host has already sent "DONE".
    op_message_type msg_type = op_get_message(handle);

    if (msg_type == OP_MSG_INCOMPLETE) {
        // No message from host. If we are not already waiting for data, request it.
        if (!is_operation_waiting_for_data(handle)) {
            // The host application shows its own progress, so we just ask for data.
            send_ack_const("Req data");
            set_operation_waiting_for_data(handle);
        }
        return true;  // Continue waiting.
    }

    // We have received a message. Clear the flag so we can request the next chunk.
    clear_operation_waiting_for_data(handle);

    switch (msg_type) {
        case OP_MSG_DONE:
            // The host has signaled it has no more data to send.
            set_operation_to_done(handle);
            return true;
        case OP_MSG_DATA:
            // The host sent a data packet.
            if (handle->address + handle->data_size > handle->mem_size) {
                log_error_const("Out of range");
                return false;
            }
            break;
        default:
            // An error occurred in op_get_message or an unexpected message was received.
            return false;
    }

    if (!op_execute_function(handle->firestarter_operation_main, handle)) {
        return false;
    }

    handle->address += handle->data_size;
    return true;
}

// Returns true on success/continue, false on error.
static inline bool _process_outgoing_data(firestarter_handle_t* handle) {
    if (!op_execute_function(handle->firestarter_operation_main, handle)) {
        return false;  // Error, so finished.
    }

    // The host application shows its own progress, so we send a simple message.
    log_data_const("Sending data");
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
