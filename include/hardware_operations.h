#ifndef HW_OPERATIONS_H
#define HW_OPERATIONS_H
#include "firestarter.h"
#ifdef __cplusplus
extern "C" {
#endif

    bool hw_read_voltage(firestarter_handle_t* handle);
    bool hw_get_version(firestarter_handle_t* handle);
    bool hw_get_config(firestarter_handle_t* handle);

    bool fw_get_version(firestarter_handle_t* handle);
#ifdef __cplusplus
}
#endif

#endif // HW_OPERATIONS_H