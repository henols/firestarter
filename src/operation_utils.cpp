/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 */

#include "operation_utils.h"

#include "firestarter.h"
#include "logging.h"
#include "rurp_shield.h"

bool _check_response(firestarter_handle_t* handle);
bool _execute_operation(void (*callback)(firestarter_handle_t* handle), firestarter_handle_t* handle);
bool _execute_operation_house_keeping(firestarter_handle_t* handle);
bool _execute_operation_house_keeping_func(void (*callback)(firestarter_handle_t* handle), int state, const char* name, firestarter_handle_t* handle);
bool _excecute_single_step_operation(firestarter_handle_t* handle);


bool op_excecute_single_step_operation(firestarter_handle_t* handle) {
    return op_excecute_multi_step_operation(_excecute_single_step_operation, handle);
}

bool op_excecute_multi_step_operation(bool (*callback)(firestarter_handle_t* handle), firestarter_handle_t* handle) {
    if (handle->firestarter_operation_execute) {
        if (_execute_operation_house_keeping(handle)) {
            return true;
        }
        if (is_operation_started(OPERATION)) {
            if (callback(handle)) {
                return true;
            }
        }
        return false;
    }
    return true;
}


bool op_execute_function(void (*callback)(firestarter_handle_t* handle), firestarter_handle_t* handle) {
    if (callback != NULL) {
        // log_info_const("Execute operation");
        return _execute_operation(callback, handle);
    }
    return false;
}

int op_check_ack() {
    if (rurp_communication_available() > 0 || rurp_communication_peak() == 'O') {
        if (rurp_communication_available() < 2) {
            return 0;
        }
        return rurp_communication_read() == 'O' && rurp_communication_read() == 'K';
    }

    return 0;
}

int op_check_done() {
    if (rurp_communication_available() > 0 && rurp_communication_peak() == 'D') {
        if (rurp_communication_available() < 4) {
            return -1;  // Indeterminate, wait for more data
        }
        char buf[4];
        rurp_communication_read_bytes(buf, 4);
        return !strncmp_P(buf, PSTR("DONE"), 4);
    }
    return 0;
}

int op_read_data(firestarter_handle_t* handle) {
    if (rurp_communication_available() > 0 && rurp_communication_peak() == '#') {
        if (rurp_communication_available() < 4) {
            return -1;  // Indeterminate, wait for more data
        }
        rurp_communication_read();
        handle->data_size = rurp_communication_read() << 8 | rurp_communication_read();

        uint8_t checksum_rcvd = rurp_communication_read();
// #define EXCEIVE_ERROR_CHECKING
#ifdef EXCEIVE_ERROR_CHECKING
        if (handle->data_size > DATA_BUFFER_SIZE || handle->data_size == 0) {
            log_error_format("Invalid data size received: %d", (int)handle->data_size);
            return -1;  // Error
        }
#endif
        log_info_format("Expecting %d bytes", handle->data_size);
        size_t len = rurp_communication_read_bytes(handle->data_buffer, handle->data_size);

        uint8_t checksum = 0;
        for (size_t i = 0; i < len; i++) {
            checksum ^= handle->data_buffer[i];
        }
        if (checksum != checksum_rcvd) {
            log_error_format("Checksum error %02X != %02X", checksum, checksum_rcvd);
            return -1;
        }

#ifdef EXCEIVE_ERROR_CHECKING
        if (handle->data_size > (uint32_t)len) {
            log_error_format("Not enough data: %d > %d", (int)handle->data_size, len);
            return -1;
        }
#endif
        return len;
    }
    return -1;
}

bool _execute_operation_house_keeping(firestarter_handle_t* handle) {
    if (!_execute_operation_house_keeping_func(handle->firestarter_operation_init, INITZIATION, "Init", handle)) {
        return true;
    }
    if (!_execute_operation_house_keeping_func(handle->firestarter_operation_end, CLEANUP, "End", handle)) {
        return true;
    }
    if (is_operations_done()) {
        return true;
    }
    if (can_operation_start(OPERATION)) {
        set_operation_state(OPERATION);
    }

    return false;
}

bool _execute_operation_house_keeping_func(void (*callback)(firestarter_handle_t* handle), int state, const char* name, firestarter_handle_t* handle) {
    while (execute_operation_state(state)) {
        if (can_operation_start(state)) {
            log_info_format("%s function", name);
            set_operation_state(state);
        }
        if (!_execute_operation(callback, handle)) {
            return false;
        }
        if (!is_operation_in_progress()) {
            log_info_format("%s done", name);
            if (state == INITZIATION) {
                send_init_done();
            } else {
                send_end_done();
            }
            set_operation_state_done();
            break;
        }
    }
    return true;
}

bool _excecute_single_step_operation(firestarter_handle_t* handle) {
    do {
        if (!op_execute_function(handle->firestarter_operation_execute, handle)) {
            return true;
        }
    } while (is_operation_in_progress());
    set_operation_state_done();
    send_done();
    return false;
}

bool _execute_operation(void (*callback)(firestarter_handle_t* handle), firestarter_handle_t* handle) {
    if (callback != NULL) {
        handle->response_msg[0] = '\0';
        rurp_set_programmer_mode();
        callback(handle);
        rurp_set_communication_mode();
        op_reset_timeout();
        return _check_response(handle);
    }
    return true;
}

bool _check_response(firestarter_handle_t* handle) {
    switch (handle->response_code) {
        case RESPONSE_CODE_OK:
            log_info(handle->response_msg);
            break;
        case RESPONSE_CODE_WARNING:
            log_warn(handle->response_msg);
            break;
        case RESPONSE_CODE_DATA:
            log_data(handle->response_msg);
            rurp_communication_write(handle->data_buffer, handle->data_size);
            break;
        case RESPONSE_CODE_ERROR:
            log_error(handle->response_msg);
            return false;
    }
    handle->response_code = RESPONSE_CODE_OK;
    return true;
}

