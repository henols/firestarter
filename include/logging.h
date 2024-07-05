#ifndef LOGGING_H
#define LOGGING_H

#define logOk(info) \
  log("OK", info)

#define logOkf(cformat, ...) \
  format(cformat, __VA_ARGS__); \
  logOk(handle->response_msg)

#define logInfo(info) \
  if(strlen(info)){ \
    log("INFO", info); \
  }

#define logInfof(cformat, ...) \
  format(cformat, __VA_ARGS__); \
  logInfo(handle->response_msg)

#define logData(info) \
  log("DATA", info)

#define logDataf(cformat, ...) \
  format(cformat, __VA_ARGS__); \
  logData(handle->response_msg)

#define logWarn(info) \
  log("WARN", info)

#define logWarnf(cformat, ...) \
  format(cformat, __VA_ARGS__); \
  logWarn(handle->response_msg)

#define logError(info) \
  log("ERROR", info)

#define logErrorf(cformat, ...) \
  format(cformat, __VA_ARGS__); \
  logError(handle->response_msg)

#define format(cformat, ...) \
  sprintf(handle->response_msg, cformat, __VA_ARGS__)

#endif // LOGGING_H