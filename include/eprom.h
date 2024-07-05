/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 */

#ifndef EPROM_H
#define EPROM_H

#include "firestarter.h"
#ifdef __cplusplus
extern "C" {
#endif


    void configure_eprom(firestarter_handle_t* handle);
    
#ifdef __cplusplus
}
#endif
#endif // EPROM_H