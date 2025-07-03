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

bool op_excecute_operation(firestarter_handle_t* handle) {
    if (handle->firestarter_operation_execute) {
        if (!op_execute_init(handle->firestarter_operation_init, handle)) {
            return true;
        }
        // log_ok_format("State: %d", handle->operation_state);
        set_operation_state(OPERATION);
        if (!op_execute_function(handle->firestarter_operation_execute, handle)) {
            return true;
        }
        set_operation_state_done();
        // log_ok_format("State: %d", handle->operation_state);
        if (!op_execute_end(handle->firestarter_operation_end, handle)) {
            return true;
        }
        // log_ok_format("State: %d", handle->operation_state);

        return false;
    }
    return true;
}

bool op_execute_init(void (*callback)(firestarter_handle_t* handle), firestarter_handle_t* handle) {
    while (execute_operation_state(INITZIATION)) {
        if (can_operation_start(INITZIATION)) {
            log_info_format("Init function cmd: %d", handle->cmd);
            set_operation_state(INITZIATION);
        }
        if (!_execute_operation(callback, handle)) {
            return false;
        }
        if (!check_operation_in_progress()) {
            set_operation_state_done();
            log_info_const("Init done");
            log_init_done();
            break;
        }
    }
    return true;
}

bool op_execute_end(void (*callback)(firestarter_handle_t* handle), firestarter_handle_t* handle) {
    while (execute_operation_state(CLEANUP)) {
        if (can_operation_start(CLEANUP)) {
            log_info_const("Cleanup func");
            set_operation_state(CLEANUP);
        }
        if (!_execute_operation(callback, handle)) {
            return false;
        }
        if (!check_operation_in_progress()) {
            set_operation_state_done();
            log_info_const("Cleanup done");
            log_end_done();
            break;
        }
    }
    return true;
}

bool op_execute_function(void (*callback)(firestarter_handle_t* handle), firestarter_handle_t* handle) {
    bool res = 0;
    if (callback != NULL) {
        log_info_const("Execute operation");
        res = _execute_operation(callback, handle);
        // log_info_const("Execute done");
    }
    return res;
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
            if (is_operation_started(INITZIATION)) {
                log_data_format("Init: %s", handle->response_msg);
            } else if (is_operation_started(CLEANUP)) {
                log_data_format("End: %s", handle->response_msg);
            }
            break;
        case RESPONSE_CODE_ERROR:
            log_error(handle->response_msg);
            return false;
    }
    handle->response_code = RESPONSE_CODE_OK;
    return true;
}

int op_check_for_ok() {
    if (rurp_communication_available() > 0 || rurp_communication_peak() == 'O') {
        if (rurp_communication_available() < 2) {
            return -1;
        }
        return rurp_communication_read() == 'O' && rurp_communication_read() == 'K';
    }

    return -1;
}

int op_check_for_done() {
    if (rurp_communication_available() > 0 && rurp_communication_peak() == 'D') {
        if (rurp_communication_available() < 4) {
            return -1;  // Indeterminate, wait for more data
        }
        char buf[4];
        rurp_communication_read_bytes(buf, 4);
        return !strncmp_P(buf, PSTR("DONE"), 4);
    }
    return 0;  // Not "DONE"
}

int op_check_for_number() {
    if (rurp_communication_available() > 0 && rurp_communication_peak() == '#') {
        if (rurp_communication_available() < 3) {
            return -1;  // Indeterminate, wait for more data
        }
        rurp_communication_read();
        return rurp_communication_read() << 8 | rurp_communication_read();
    }
    return -1;  // Not "DONE"
}
