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

int op_check_response(firestarter_handle_t* handle);

int op_execute_init(void (*callback)(firestarter_handle_t* handle), firestarter_handle_t* handle) {
    if (handle->init == 1 && callback != NULL) {
        log_info_format("Init function state: %d", handle->state);
        handle->init = 0;
        int res = op_execute_function(callback, handle);
        log_info_const("Init done");  

        return res;
    }           
    return 1;              
}

int op_execute_end(void (*callback)(firestarter_handle_t* handle), firestarter_handle_t* handle) {
    if (callback != NULL) {
        log_info_const("End func");
        int res = op_execute_function(callback, handle);
        log_info_const("End done");  
        return res;
    }           
    return 1;              
}

int op_execute_function(void (*callback)(firestarter_handle_t* handle), firestarter_handle_t* handle) {
   if (callback != NULL) {
        handle->response_msg[0] = '\0';
        rurp_set_programmer_mode();
        callback(handle);
        rurp_set_communication_mode();
        op_reset_timeout();
    }
    return op_check_response(handle);
}

int op_check_response(firestarter_handle_t* handle) {
    if (handle->response_code == RESPONSE_CODE_OK) {
        log_info(handle->response_msg);
        return 1;
    }
    else if (handle->response_code == RESPONSE_CODE_WARNING) {
        log_warn(handle->response_msg);
        handle->response_code = RESPONSE_CODE_OK;
        return 1;
    }
    else if (handle->response_code == RESPONSE_CODE_ERROR) {
        log_error(handle->response_msg);
    }
    return 0;
}

int op_check_for_ok(firestarter_handle_t* handle) {
    if (rurp_communication_available() < 2) {
        return 0;
    }
    if (rurp_communication_read() != 'O' || rurp_communication_read() != 'K') {
        log_info_const("Expecting OK");
        return 0;
    }
    return 1;
}
