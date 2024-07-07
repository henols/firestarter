#ifndef LOGGING_H
#define LOGGING_H

#include <avr/pgmspace.h>

#define copyToBuffer( buf, msg) \
  strcpy_P(buf, PSTR(msg)); \


#define logOk(msg) \
  logOkBuf(handle->response_msg, msg); \

#define logOkBuf(buf, msg) \
  copyToBuffer(buf, msg); \
  logOkMsg(buf)

#define logOkMsg(msg) \
  log("OK", msg)

#define logOkf(buf, cformat, ...) \
  format(buf, cformat, __VA_ARGS__); \
  logOkMsg(buf)

#define logInfoBuf(buf, msg) \
  copyToBuffer(buf, msg); \
  logInfoMsg(buf)

#define logInfo(msg) \
  copyToBuffer(handle->response_msg, msg); \
  logInfoMsg(handle->response_msg)

#define logInfoMsg(msg) \
  if(strlen(msg)){ \
    log("INFO", msg); \
  }

#define logInfof(buf, cformat, ...) \
  format(buf, cformat, __VA_ARGS__); \
  logInfoMsg(buf)

#define logDataMsg(msg) \
  log("DATA", msg)

#define logData(msg) \
  copyToBuffer(handle->response_msg, msg);\
  logDataMsg(handle->response_msg)

#define logDataf(buf, cformat, ...) \
  format(buf, cformat, __VA_ARGS__); \
  logDataMsg(buf)

#define logWarnMsg(msg) \
  log("WARN", msg)

#define logWarnf(buf, cformat, ...) \
  format(buf, cformat, __VA_ARGS__); \
  logWarnMsg(buf)

#define logError(msg) \
  logErrorBuf(handle->response_msg,msg); \

#define logErrorBuf(buf, msg) \
  copyToBuffer(buf, msg);\
  logErrorMsg(buf)

#define logErrorMsg(msg) \
  log("ERROR", msg)

#define logErrorf(buf, cformat, ...) \
  format(buf, cformat, __VA_ARGS__); \
  logErrorMsg(buf)


#define format(buf, cformat, ...) \
  char msg[40]; \
  copyToBuffer(msg, cformat);\
  sprintf(buf, msg, __VA_ARGS__)

void log(const char* type, const char* msg);

#endif // LOGGING_H