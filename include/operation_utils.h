/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 */

#ifndef __UTILS_H
#define __UTILS_H

#include "firestarter.h"
#ifdef __cplusplus
extern "C" {
#endif
    int op_execute_init(void (*callback)(firestarter_handle_t* handle), firestarter_handle_t* handle);
    int op_execute_function(void (*callback)(firestarter_handle_t* handle), firestarter_handle_t* handle);

    void op_reset_timeout();

    int op_wait_for_ok(firestarter_handle_t* handle);

#ifdef __cplusplus
}
#endif

#endif // __UTILS_H