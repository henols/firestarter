#ifndef LOGGING_H
#define LOGGING_H
#include <stdio.h>
#include <avr/pgmspace.h>
#include "rurp_shield.h"
#include "debug.h"

#define copy_to_buffer( buf, msg) \
  strcpy_P(buf, PSTR(msg)); \


#define log_ok(msg) \
  log_ok_buf(handle->response_msg, msg); \

#define log_ok_buf(buf, msg) \
  copy_to_buffer(buf, msg); \
  log_ok_msg(buf)

#define log_ok_msg(msg) \
  rurp_log("OK", msg)

#define log_ok_format(buf, cformat, ...) \
  {format(buf, cformat, __VA_ARGS__);} \
  log_ok_msg(buf)

#define log_info_buf(buf, msg) \
  copy_to_buffer(buf, msg); \
  logInfoMsg(buf)

#define log_info(msg) \
  copy_to_buffer(handle->response_msg, msg); \
  log_info_msg(handle->response_msg)

#define log_info_msg(msg) \
  if(strlen(msg)){ \
    rurp_log("INFO", msg); \
  }

#define log_info_format(buf, cformat, ...) \
  {format(buf, cformat, __VA_ARGS__);} \
  log_info_msg(buf)

#define log_data_msg(msg) \
  rurp_log("DATA", msg)

#define log_data(msg) \
  copy_to_buffer(handle->response_msg, msg);\
  log_data_msg(handle->response_msg)

#define log_data_format(buf, cformat, ...) \
  {format(buf, cformat, __VA_ARGS__);} \
  log_data_msg(buf)

#define log_warn(msg) \
  copy_to_buffer(handle->response_msg, msg);\
  log_warn_msg(handle->response_msg)

#define log_warn_msg(msg) \
  rurp_log("WARN", msg)

#define log_warn_format(buf, cformat, ...) \
  {format(buf, cformat, __VA_ARGS__);} \
  log_warn_msg(buf)

#define log_error(msg) \
  log_error_buf(handle->response_msg, msg); \

#define log_error_buf(buf, msg) \
  copy_to_buffer(buf, msg);\
  log_error_msg(buf)

#define log_error_msg(msg) \
  rurp_log("ERROR", msg)

#define log_error_format(buf, cformat, ...) \
  {format(buf, cformat, __VA_ARGS__);} \
  log_error_msg(buf)


#define format(buf, cformat, ...) \
  char msg[80]; \
  copy_to_buffer(msg, cformat);\
  sprintf(buf, msg, __VA_ARGS__)


#endif // LOGGING_H