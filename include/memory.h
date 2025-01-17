/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 */

#ifndef MEMORY_H
#define MEMORY_H
#include "firestarter.h"

#ifdef __cplusplus
extern "C" {
#endif


#define WRITE_FLAG  0
#define READ_FLAG  1

    void configure_memory(firestarter_handle_t* handle);

#ifdef __cplusplus
}
#endif

#endif // MEMORY_H
