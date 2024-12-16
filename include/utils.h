#ifndef __UTILS_H
#define __UTILS_H

#include "firestarter.h"
#ifdef __cplusplus
extern "C" {
#endif

int execute_function(void (*callback)(firestarter_handle_t* handle), firestarter_handle_t* handle);
int check_response(firestarter_handle_t* handle);

void reset_timeout();
int wait_for_ok(firestarter_handle_t* handle);

#ifdef __cplusplus
}
#endif

#endif // __UTILS_H