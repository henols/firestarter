/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 */

#include "operation_utils.h"

#include <Arduino.h>

#include "firestarter.h"
#include "logging.h"
#include "rurp_shield.h"

#define ERROR -1
#define RETURN 0
#define CONTINUE 1

#define set_operation_state(state) \
    (handle->operation_state = (handle->operation_state & 0xc0) | state)

#define set_operation_state_done() \
    handle->operation_state++;     \
    handle->operation_state &= 0x2F

#define is_operation_started(state) \
    ((handle->operation_state & 0x2F) == state)

#define can_operation_start(state) \
    is_operation_started(state - 1)

#define execute_operation_state(state) \
    (can_operation_start(state) || is_operation_started(state))

#define is_all_operations_done() \
    is_operation_started(ENDED)

bool _check_response(firestarter_handle_t* handle);
int _execute_operation(void (*callback)(firestarter_handle_t* handle), firestarter_handle_t* handle);
int _execute_operation_house_keeping(firestarter_handle_t* handle);
int _execute_operation_house_keeping_func(void (*callback)(firestarter_handle_t* handle), int state, const char* name, firestarter_handle_t* handle);
bool _single_step_operation_callback(firestarter_handle_t* handle);

/**
 * @brief Executes a single-step operation.
 *
 * This function is a wrapper around op_excecute_multi_step_operation for operations
 * that are expected to complete within a single execution cycle of the main operation callback.
 * It calls the operation's `firestarter_operation_execute` function until it's no longer
 * in progress.
 *
 * @param handle Pointer to the firestarter handle.
 * @return true if the operation is ongoing, false if it completed (with or without an error).
 */
bool op_execute_operation(firestarter_handle_t* handle) {
    return op_execute_callback_operation(_single_step_operation_callback, handle);
}

bool op_execute_callback_operation(bool (*callback)(firestarter_handle_t* handle), firestarter_handle_t* handle) {
    if (handle->firestarter_operation_main) {
        if (is_all_operations_done()) {
            // The operation is complete from the firmware's perspective.
            // The host sends a final ACK to close the transaction.
            // We wait for it and then signal that the command is finished.
            if (op_get_message(handle) == OP_MSG_INCOMPLETE) {
                return true;  // Not finished yet, waiting for final ACK
            }
            return false;  // Received final ACK (or junk), command is finished.
        }

        int res = _execute_operation_house_keeping(handle);
        if (res != CONTINUE) {
            return res == RETURN;
        }
        // log_info_format("Operation started: %d, state: %d", is_operation_started(OPERATION), handle->operation_state);
        if (is_operation_started(MAIN)) {
            // log_info_const("Execute operation");
            return callback(handle);
        }
        return true;
    }
    return false;
}

/**
 * @brief Executes a provided function with standard operation wrappers.
 *
 * This function wraps the execution of a given callback. It sets the programmer mode,
 * executes the callback, resets the communication mode, resets the timeout, and
 * checks the response from the handle.
 *
 * @param callback The function to execute.
 * @param handle Pointer to the firestarter handle.
 * @return true if the operation was successful or is waiting for data, false on error.
 */
bool op_execute_function(void (*callback)(firestarter_handle_t* handle), firestarter_handle_t* handle) {
    if (callback != NULL) {
        log_info_const("Execute operation");
        return _execute_operation(callback, handle) != ERROR;
    }
    return false;
}

bool op_wait_for_ack(firestarter_handle_t* handle) {
    unsigned long timeout = millis() + 2000;
    while (millis() < timeout) {
        op_message_type msg_type = op_get_message(handle);
        if (msg_type == OP_MSG_ACK) {
            return true;
        }
        if (msg_type == OP_MSG_ERROR) {
            return false;
        }
        delay(10);
    }
    log_error_const("Timeout ACK");
    return false;
}

op_message_type op_get_message(firestarter_handle_t* handle) {
    if (rurp_communication_available() <= 0) {
        return OP_MSG_INCOMPLETE;
    }
    log_info_format("op_get_message: %d bytes available", rurp_communication_available());
    while (rurp_communication_available() > 0) {
        int peek = rurp_communication_peak();
        switch (peek) {
            case 'O':  // Potential "OK"
                log_info_const("op_get_message: Found 'O'");
                if (rurp_communication_available() < 2) {
                    return OP_MSG_INCOMPLETE;
                }
                rurp_communication_read();  // consume 'O'
                if (rurp_communication_peak() == 'K') {
                    rurp_communication_read();  // consume 'K'
                    log_info_const("op_get_message: ACK received");
                    return OP_MSG_ACK;
                }
                // Not "OK", 'O' is consumed. Loop will treat next char as junk.
                break;
                ;

            case 'D':  // Potential "DONE"
                if (rurp_communication_available() < 4) {
                    return OP_MSG_INCOMPLETE;
                }
                char done_buf[4];
                rurp_communication_read_bytes(done_buf, 4);
                if (strncmp_P(done_buf, PSTR("DONE"), 4) == 0) {
                    return OP_MSG_DONE;
                }
                // Not "DONE", 4 bytes consumed. This is a risk.
                break;

            case '#': {  // Data packet
                if (rurp_communication_available() < 4) {
                    return OP_MSG_INCOMPLETE;
                }
                rurp_communication_read();  // consume '#'

                uint8_t size_buf[2];
                if (rurp_communication_read_bytes((char*)size_buf, 2) != 2) return OP_MSG_ERROR;
                handle->data_size = (size_buf[0] << 8) | size_buf[1];

                uint8_t checksum_rcvd;
                if (rurp_communication_read_bytes((char*)&checksum_rcvd, 1) != 1) return OP_MSG_ERROR;

                if (handle->data_size > DATA_BUFFER_SIZE || handle->data_size == 0) {
                    log_error_format("BAd data size: %d", (int)handle->data_size);
                    return OP_MSG_ERROR;
                }

                log_info_format("Expecting %d bytes", handle->data_size);
                size_t len = rurp_communication_read_bytes(handle->data_buffer, handle->data_size);

                if (len < handle->data_size) {
                    log_error_const("Timeout, data packet.");
                    return OP_MSG_ERROR;
                }

                uint8_t checksum = 0;
                for (size_t i = 0; i < len; i++) {
                    checksum ^= handle->data_buffer[i];
                }
                if (checksum != checksum_rcvd) {
                    log_error_format("Bad checksum %02X != %02X", checksum, checksum_rcvd);
                    return OP_MSG_ERROR;
                }
                return OP_MSG_DATA;
            } break;
            default:
                log_info_format("op_get_message: Consuming junk char '%c' (0x%02x)", (char)peek, peek);
                rurp_communication_read();
        }
    }
    return OP_MSG_INCOMPLETE;  // Nothing in buffer
}

void set_operation_to_done(firestarter_handle_t* handle) {
    log_info_const("Main done");
    set_operation_state_done();
    send_main_done();
}

/**
 * @brief Manages the housekeeping states of an operation (init and cleanup).
 *
 * @param handle Pointer to the firestarter handle.
 * @return
 */
int _execute_operation_house_keeping(firestarter_handle_t* handle) {
    log_info_format("Housekeeping: state=0x%02x", handle->operation_state);
    if (is_all_operations_done()) {
        // log_info_const("Operations done");
        return CONTINUE;
    }
    if (is_operation_started(MAIN)) {
        // log_info_const("Operation is started");
        return CONTINUE;
    }
    // log_info_format("Can operation start: %d", can_operation_start(OPERATION));
    if (can_operation_start(MAIN)) {
        // log_info_format("Check Ack: %s", rurp_communication_peak());
        // op_message_type msg = op_get_message(handle);
        // if (msg != OP_MSG_ACK) {
        //     return (msg == OP_MSG_INCOMPLETE) ? RETURN : ERROR;
        // }
        if(!op_wait_for_ack(handle) ){
            return ERROR;
        }
        op_reset_timeout();
        set_operation_state(MAIN);
        log_info_const("Main started");
        return CONTINUE;
    }
    int res = _execute_operation_house_keeping_func(handle->firestarter_operation_init, INIT, "Init", handle);
    if (res != CONTINUE) {
        return res;
    }

    return _execute_operation_house_keeping_func(handle->firestarter_operation_end, END, "End", handle);
}

/**
 * @brief Executes a housekeeping function (init or end) for an operation.
 *
 * This function handles the execution loop for a specific state (INITZIATION or END).
 *
 * @param callback The function to call (e.g., firestarter_operation_init).
 * @param state The operation state to manage (e.g., INITZIATION).
 * @param name The name of the state for logging purposes (e.g., "Init").
 * @param handle Pointer to the firestarter handle.
 * @return
 */
int _execute_operation_house_keeping_func(void (*callback)(firestarter_handle_t* handle), int state, const char* name, firestarter_handle_t* handle) {
    // log_info_format("%s function, state: %d, current state: %d", name, state, handle->operation_state);
    if (execute_operation_state(state)) {
        // log_info_format("%s function, state: %d, can start: %d", name, state, can_operation_start(state));
        if (can_operation_start(state)) {
            log_info_format("Waiting for ACK to start %s phase", name);
            if (!op_wait_for_ack(handle)) {
                return ERROR;
            }
            // op_message_type msg = op? RETURN: ERROR;
            // op_message_type msg = op_get_message(handle);
            // if (msg != OP_MSG_ACK) {
            //     if (msg == OP_MSG_ERROR) {
            //         log_error_format("Error message received while waiting for %s ACK", name);
            //     }
            //     return (msg == OP_MSG_INCOMPLETE)? RETURN: ERROR;
            // }
            log_info_format("ACK received for %s phase", name);
            op_reset_timeout();
            log_info_format("%s func", name);
            set_operation_state(state);
        }

        if (_execute_operation(callback, handle) == ERROR) {
            return ERROR;
        }

        if (is_operation_in_progress()) {
            return RETURN;
        }
        log_info_format("%s done", name);
        if (state == INIT) {
            send_init_done();
        } else {
            send_end_done();
        }
        set_operation_state_done();
    }
    return CONTINUE;
}

/**
 * @brief The main execution loop for a single-step operation.
 *
 * This function is used as a callback for op_excecute_single_step_operation.
 * It repeatedly calls the main execute function until the operation is no longer in progress.
 *
 * @param handle Pointer to the firestarter handle.
 * @return
 */
bool _single_step_operation_callback(firestarter_handle_t* handle) {
    int res = _execute_operation(handle->firestarter_operation_main, handle);
    if (res == ERROR) {
        return false;
    }
    if (!is_operation_in_progress()) {
        set_operation_to_done(handle);
    }
    return true;  // Success,
}

/**
 * @brief Executes a callback function, wrapping it with mode changes and response checking.
 *
 * @param callback The function to execute.
 * @param handle Pointer to the firestarter handle.
 * @return true if the operation was successful, false on error.
 */
int _execute_operation(void (*callback)(firestarter_handle_t* handle), firestarter_handle_t* handle) {
    if (callback != NULL) {
        handle->response_msg[0] = '\0';
        rurp_set_programmer_mode();
        callback(handle);
        rurp_set_communication_mode();
        return _check_response(handle) ? RETURN : ERROR;
    }
    return CONTINUE;
}

/**
 * @brief Checks and handles the response code in the firestarter handle.
 *
 * Logs messages based on the response code and sends data if required.
 *
 * @param handle Pointer to the firestarter handle.
 * @return true if the response is OK, WARNING, or DATA. false if it's an ERROR.
 */
bool _check_response(firestarter_handle_t* handle) {
    switch (handle->response_code) {
        case RESPONSE_CODE_OK:
            log_info(handle->response_msg);
            // log_info_const("- OK -");
            break;
        case RESPONSE_CODE_WARNING:
            log_warn(handle->response_msg);
            break;
        case RESPONSE_CODE_DATA:
            log_data(handle->response_msg);
            rurp_communication_write(handle->data_buffer, handle->data_size);
            break;
        case RESPONSE_CODE_ERROR:
        default:
            log_error(handle->response_msg);
            return false;
    }
    op_reset_timeout();
    handle->response_code = RESPONSE_CODE_OK;
    return true;
}
