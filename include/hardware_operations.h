#ifndef __HARDWARE_OPERATIONS_H__
#define __HARDWARE_OPERATIONS_H__

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

#endif // __HARDWARE_OPERATIONS_H__