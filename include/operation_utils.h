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

#define INITZIATION 1
#define OPERATION 3
#define CLEANUP 5
#define ENDED 7

#define IN_PROGRESS 0x40
#define PROGRESS_DONE 0x80

#define set_operation_state(state) \
    (handle->operation_state = (handle->operation_state & 0xc0) | state)

#define set_operation_state_done() \
    handle->operation_state++;     \
    handle->operation_state &= 0x2F

#define check_operation_in_progress() \
    (((handle->operation_state & IN_PROGRESS) << 1) ^ (handle->operation_state & PROGRESS_DONE))

#define is_operation_started(state) \
    ((handle->operation_state & 0x2F) == state)

#define can_operation_start(state) \
    is_operation_started(state - 1)

#define execute_operation_state(state) \
    (can_operation_start(state) || (is_operation_started(state) && check_operation_in_progress()))

#define set_operation_in_progress() \
    (handle->operation_state |= IN_PROGRESS)

bool op_excecute_operation(firestarter_handle_t* handle);
bool op_execute_init(void (*callback)(firestarter_handle_t* handle), firestarter_handle_t* handle);
bool op_execute_function(void (*callback)(firestarter_handle_t* handle), firestarter_handle_t* handle);
bool op_execute_end(void (*callback)(firestarter_handle_t* handle), firestarter_handle_t* handle);

void op_reset_timeout();

int op_check_for_ok();
int op_check_for_done();
int op_check_for_number();


#ifdef __cplusplus
}
#endif

#endif  // __OPERATION_UTILS_H__