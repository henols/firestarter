/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 */

#ifndef LOGGING_H
#define LOGGING_H



// #ifndef __LOGGING_H__
// #define __LOGGING_H__

#include <stdio.h>
#include <avr/pgmspace.h>
#include "rurp_shield.h"

#define log_ok(msg) \
  rurp_log("OK", msg)

#define log_ok_const(msg) \
  copy_to_buffer(handle->response_msg, msg); \
  log_ok(handle->response_msg)

#define log_ok_format( cformat, ...) \
  {format(handle->response_msg, cformat, __VA_ARGS__);} \
  log_ok(handle->response_msg)


#define log_info(msg) \
  if(strlen(msg)){ \
    rurp_log("INFO", msg); \
  }

#define log_info_const(msg) \
  copy_to_buffer(handle->response_msg, msg); \
  log_info(handle->response_msg)

#define log_info_format( cformat, ...) \
  {format(handle->response_msg, cformat, __VA_ARGS__);} \
  log_info(handle->response_msg)


#define log_data(msg) \
  rurp_log("DATA", msg)

#define log_data_const(msg) \
  copy_to_buffer(handle->response_msg, msg);\
  log_data(handle->response_msg)

#define log_data_format( cformat, ...) \
  {format(handle->response_msg, cformat, __VA_ARGS__);} \
  log_data(handle->response_msg)



#define log_warn(msg) \
  rurp_log("WARN", msg)

#define log_warn_const(msg) \
  copy_to_buffer(handle->response_msg, msg);\
  log_warn(handle->response_msg)

#define log_warn_format(cformat, ...) \
  log_warn_format_buf(handle->response_msg, cformat, __VA_ARGS__)

#define log_warn_format_buf(buf, cformat, ...) \
  {format(buf, cformat, __VA_ARGS__);} \
  log_warn(buf)


#define log_error(msg) \
  rurp_log("ERROR", msg)

#define log_error_const(msg) \
  log_error_const_buf(handle->response_msg, msg)

#define log_error_const_buf(buf, msg) \
  copy_to_buffer(buf, msg);\
  log_error(buf)

#define log_error_format(cformat, ...) \
  log_error_format_buf(handle->response_msg, cformat, __VA_ARGS__)

#define log_error_format_buf(buf, cformat, ...) \
  {format(buf, cformat, __VA_ARGS__);} \
  log_error(buf)


#define copy_to_buffer( buf, msg) \
  strcpy_P(buf, PSTR(msg)); \

#define format(buf, cformat, ...) \
  char msg[80]; \
  copy_to_buffer(msg, cformat);\
  sprintf(buf, msg, __VA_ARGS__)


#ifdef SERIAL_DEBUG
extern char* debug_msg_buffer;

void debug_setup();
void debug_buf(const char* msg);

#define debug(msg) \
    { \
        debug_buf(msg); \
    }

#define debug_format(cformat, ...) \
    { \
        format(debug_msg_buffer, cformat, __VA_ARGS__); \
        debug_buf(debug_msg_buffer); \
    }

#else
#define debug(msg)
#define debug_format(cformat, ...)
#define debug_setup()
#define debug_buf(msg)
#define log_debug(type, msg)
#endif

// #endif // __LOGGING_H__