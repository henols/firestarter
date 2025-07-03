#include "logging.h"
#include "firestarter.h"

// void _firestarter_set_responce(uint8_t code, const char* msg, firestarter_handle_t* handle) {
//         strcpy_P(handle->response_msg, msg);
//     // copy_to_buffer(handle.response_msg, msg); 
//     handle->response_code = code;
// }

#ifdef INFO_LOG_METHODE
void _log_info(const char* msg, firestarter_handle_t* handle)                               {
    if (strlen(msg) && is_flag_set(FLAG_VERBOSE)) { 
        rurp_log(LOG_INFO_MSG, msg);                
    }
}
#endif