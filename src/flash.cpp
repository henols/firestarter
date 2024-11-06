/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 */

#include "flash.h"
#include "firestarter.h"
#include "rurp_shield.h"
#include "logging.h"
#include <stdio.h>
#include "debug.h"
void configure_flash(firestarter_handle_t* handle) {
    debug("Configuring Flash");
    copyToBuffer(handle->response_msg, "Flash not supported");
    handle->response_code = RESPONSE_CODE_ERROR;
}
