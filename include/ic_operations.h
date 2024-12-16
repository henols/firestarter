#ifndef IC_OPERATIONS_H
#define IC_OPERATIONS_H
#include "firestarter.h"
#ifdef __cplusplus
extern "C" {
#endif

    bool read(firestarter_handle_t* handle);
    bool write(firestarter_handle_t* handle);
    bool erase(firestarter_handle_t* handle);
    bool check_chip_id(firestarter_handle_t* handle);
    bool blank_check(firestarter_handle_t* handle);

#ifdef __cplusplus
}
#endif

#endif // IC_OPERATIONS_H