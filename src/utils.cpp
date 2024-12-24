#include "utils.h"
#include "firestarter.h"
#include "logging.h"
#include "rurp_shield.h"

int execute_init(void (*callback)(firestarter_handle_t* handle), firestarter_handle_t* handle) {
    if (handle->init && callback != NULL) {
        debug("Init function");
        handle->init = 0;
        return execute_function(handle->firestarter_read_init, handle);
    }           
    return 1;              
}

int execute_function(void (*callback)(firestarter_handle_t* handle), firestarter_handle_t* handle) {
   if (callback != NULL) {
        rurp_set_programmer_mode();
        callback(handle);
        rurp_set_communication_mode();
        reset_timeout();
    }
    return check_response(handle);
}

int check_response(firestarter_handle_t* handle) {
    if (handle->response_code == RESPONSE_CODE_OK) {
        log_info_msg(handle->response_msg);
        return 1;
    }
    else if (handle->response_code == RESPONSE_CODE_WARNING) {
        log_warn_msg(handle->response_msg);
        handle->response_code = RESPONSE_CODE_OK;
        return 1;
    }
    else if (handle->response_code == RESPONSE_CODE_ERROR) {
        log_error_msg(handle->response_msg);
    }
    return 0;
}

int wait_for_ok(firestarter_handle_t* handle) {
    if (rurp_communication_available() < 2) {
        return 0;
    }
    if (rurp_communication_read() != 'O' || rurp_communication_read() != 'K') {
        log_info("Expecting OK");
        reset_timeout();
        return 0;
    }
    return 1;
}
