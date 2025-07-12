/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 */

#ifndef __OPERATION_UTILS_H__
#define __OPERATION_UTILS_H__

/**
 * @file operation_utils.h
 * @brief Provides a state machine and utility functions for managing complex, multi-step programmer operations.
 *
 * This module abstracts the common patterns of INIT-MAIN-END sequences, message passing (ACK/DONE/DATA),
 * and state management required for operations like reading, writing, and verifying EPROMs.
 */
#include "firestarter.h"
#include "logging.h"

#ifdef __cplusplus
extern "C" {
#endif

#define INIT 1
#define MAIN 3
#define END 5
#define ENDED 6

#define OPERATION_IN_PROGRESS 0x40
#define OPERATION_WAITING_FOR_DATA 0x80

enum op_message_type {
    OP_MSG_ACK,
    OP_MSG_DONE,
    OP_MSG_DATA,
    OP_MSG_INCOMPLETE,
    OP_MSG_ERROR
};


static inline void set_operation_in_progress(firestarter_handle_t* handle) {
    handle->operation_state |= OPERATION_IN_PROGRESS;
}

static inline void clear_operation_in_progress(firestarter_handle_t* handle) {
    handle->operation_state &= ~OPERATION_IN_PROGRESS;
}

static inline bool is_operation_in_progress(const firestarter_handle_t* handle) {
    return (handle->operation_state & OPERATION_IN_PROGRESS) == OPERATION_IN_PROGRESS;
}

static inline void set_operation_waiting_for_data(firestarter_handle_t* handle) {
    handle->operation_state |= OPERATION_WAITING_FOR_DATA;
}

static inline void clear_operation_waiting_for_data(firestarter_handle_t* handle) {
    handle->operation_state &= ~OPERATION_WAITING_FOR_DATA;
}

static inline bool is_operation_waiting_for_data(const firestarter_handle_t* handle) {
    return (handle->operation_state & OPERATION_WAITING_FOR_DATA) == OPERATION_WAITING_FOR_DATA;
}

/**
 * @brief Executes a simple, non-stateful operation that completes in a single logical step.
 *
 * This is a wrapper for operations like blank checks or chip ID checks, which have a main
 * execution body but don't require complex data exchange with the host.
 *
 * @param handle Pointer to the firestarter handle.
 * @return true if the operation is still ongoing (e.g., waiting for ACKs), false when fully completed.
 */
bool op_execute_simple_operation(firestarter_handle_t* handle);

/**
 * @brief Executes a stateful operation that involves multiple steps and host interaction.
 *
 * This is the main engine for complex operations. It manages the INIT, MAIN, and END phases,
 * and calls the provided callback function to perform the work of the MAIN phase.
 *
 * @param callback A function pointer to the main logic for the operation (e.g., reading or writing data).
 * @param handle Pointer to the firestarter handle.
 * @return true if the operation is still ongoing, false when fully completed.
 */
bool op_execute_stateful_operation(bool (*callback)(firestarter_handle_t* handle), firestarter_handle_t* handle);

/**
 * @brief Executes a single, non-stateful function within the programmer mode context.
 *
 * This helper function wraps a given callback, ensuring the device is in programmer mode
 * before execution and returns to communication mode afterward. It also handles checking
 * the response code set by the callback.
 *
 * @param callback The function to execute.
 * @param handle Pointer to the firestarter handle.
 * @return true if the function executed successfully (or set a WARNING), false on ERROR.
 */
bool op_execute_function(void (*callback)(firestarter_handle_t* handle), firestarter_handle_t* handle);

/**
 * @brief Resets the global command timeout counter.
 */
void op_reset_timeout();

/**
 * @brief Parses the incoming serial stream for messages from the host.
 *
 * This function is non-blocking. It checks for "OK" (ACK), "DONE", and data packets ('#').
 *
 * @param handle Pointer to the firestarter handle, used to store incoming data.
 * @return An op_message_type enum value indicating the message found, or OP_MSG_INCOMPLETE if no full message is available.
 */
op_message_type op_get_message(firestarter_handle_t* handle);

/**
 * @brief Waits for an "OK" (ACK) message from the host.
 *
 * This is a blocking function with a timeout.
 *
 * @param handle Pointer to the firestarter handle.
 * @return true if an ACK was received, false on timeout or error.
 */
bool op_wait_for_ack(firestarter_handle_t* handle);

/**
 * @brief Marks the MAIN phase of an operation as complete.
 *
 * This function sends the "MAIN: Done" message to the host and advances the internal state machine.
 *
 * @param handle Pointer to the firestarter handle.
 */
void set_operation_to_done(firestarter_handle_t* handle) ;

#ifdef __cplusplus
}
#endif

#endif  // __OPERATION_UTILS_H__