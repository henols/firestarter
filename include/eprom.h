/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 */

#ifndef __EPROM_H__
#define __EPROM_H__

#include "firestarter.h"
#ifdef __cplusplus
extern "C" {
#endif

    void configure_eprom(firestarter_handle_t* handle);
    
#ifdef __cplusplus
}
#endif
#endif // __EPROM_H__