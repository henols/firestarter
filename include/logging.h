#ifndef LOGGING_H
#define LOGGING_H

#include <avr/pgmspace.h>
#include "rurp_shield.h"

#define copyToBuffer( buf, msg) \
  strcpy_P(buf, PSTR(msg)); \


#define logOk(msg) \
  logOkBuf(handle->response_msg, msg); \

#define logOkBuf(buf, msg) \
  copyToBuffer(buf, msg); \
  logOkMsg(buf)

#define logOkMsg(msg) \
  rurp_log("OK", msg)

#define logOkf(buf, cformat, ...) \
  {format(buf, cformat, __VA_ARGS__);} \
  logOkMsg(buf)

#define logInfoBuf(buf, msg) \
  copyToBuffer(buf, msg); \
  logInfoMsg(buf)

#define logInfo(msg) \
  copyToBuffer(handle->response_msg, msg); \
  logInfoMsg(handle->response_msg)

#define logInfoMsg(msg) \
  if(strlen(msg)){ \
    rurp_log("INFO", msg); \
  }

#define logInfof(buf, cformat, ...) \
  {format(buf, cformat, __VA_ARGS__);} \
  logInfoMsg(buf)

#define logDataMsg(msg) \
  rurp_log("DATA", msg)

#define logData(msg) \
  copyToBuffer(handle->response_msg, msg);\
  logDataMsg(handle->response_msg)

#define logDataf(buf, cformat, ...) \
  {format(buf, cformat, __VA_ARGS__);} \
  logDataMsg(buf)

#define logWarn(msg) \
  copyToBuffer(handle->response_msg, msg);\
  logWarnMsg(handle->response_msg)

#define logWarnMsg(msg) \
  rurp_log("WARN", msg)

#define logWarnf(buf, cformat, ...) \
  {format(buf, cformat, __VA_ARGS__);} \
  logWarnMsg(buf)

#define logError(msg) \
  logErrorBuf(handle->response_msg, msg); \

#define logErrorBuf(buf, msg) \
  copyToBuffer(buf, msg);\
  logErrorMsg(buf)

#define logErrorMsg(msg) \
  rurp_log("ERROR", msg)

#define logErrorf(buf, cformat, ...) \
  {format(buf, cformat, __VA_ARGS__);} \
  logErrorMsg(buf)


#define format(buf, cformat, ...) \
  char msg[80]; \
  copyToBuffer(msg, cformat);\
  sprintf(buf, msg, __VA_ARGS__)


#endif // LOGGING_H