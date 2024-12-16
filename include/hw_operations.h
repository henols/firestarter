#ifndef HW_OPERATIONS_H
#define HW_OPERATIONS_H
#include "firestarter.h"
#ifdef __cplusplus
extern "C" {
#endif

    bool read_voltage(firestarter_handle_t* handle);
    bool get_hw_version(firestarter_handle_t* handle);
    bool get_fw_version(firestarter_handle_t* handle);
    bool get_config(firestarter_handle_t* handle);

#ifdef __cplusplus
}
#endif

#endif // HW_OPERATIONS_H