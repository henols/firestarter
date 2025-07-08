/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 */

#ifndef __OPERATION_UTILS_H__
#define __OPERATION_UTILS_H__

#include "firestarter.h"
#include "logging.h"

#ifdef __cplusplus
extern "C" {
#endif

#define INIT 1
#define MAIN 3
#define END 5
#define ENDED 6

#define IN_PROGRESS 0x40
#define PROGRESS_DONE 0x80

enum op_message_type {
    OP_MSG_ACK,
    OP_MSG_DONE,
    OP_MSG_DATA,
    OP_MSG_INCOMPLETE,
    OP_MSG_ERROR
};


#define is_operation_in_progress() \
    (((handle->operation_state & IN_PROGRESS) << 1) ^ (handle->operation_state & PROGRESS_DONE))

#define set_operation_in_progress() \
    (handle->operation_state |= IN_PROGRESS)

#define set_operation_progress_done() \
    (handle->operation_state |= PROGRESS_DONE)


bool op_execute_operation(firestarter_handle_t* handle);
bool op_execute_callback_operation(bool (*callback)(firestarter_handle_t* handle), firestarter_handle_t* handle);

bool op_execute_function(void (*callback)(firestarter_handle_t* handle), firestarter_handle_t* handle);

void op_reset_timeout();

op_message_type op_get_message(firestarter_handle_t* handle);
bool op_wait_for_ack(firestarter_handle_t* handle);

void set_operation_to_done(firestarter_handle_t* handle) ;

#ifdef __cplusplus
}
#endif

#endif  // __OPERATION_UTILS_H__