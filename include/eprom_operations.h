#ifndef IC_OPERATIONS_H
#define IC_OPERATIONS_H
#include "firestarter.h"
#ifdef __cplusplus
extern "C" {
#endif

    bool eprom_read(firestarter_handle_t* handle);
    bool eprom_write(firestarter_handle_t* handle);
    bool eprom_verify(firestarter_handle_t* handle);
    bool eprom_erase(firestarter_handle_t* handle);
    bool eprom_check_chip_id(firestarter_handle_t* handle);
    bool eprom_blank_check(firestarter_handle_t* handle);

#ifdef __cplusplus
}
#endif

#endif // IC_OPERATIONS_H