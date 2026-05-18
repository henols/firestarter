#include "logging.h"

#include "firestarter.h"

// LOG_OK_MSG: used by send_ack / send_ack_const macros in logging.h.
// Phase 8 cleanup: LOG_INIT_DONE_MSG, LOG_MAIN_DONE_MSG, LOG_END_DONE_MSG,
// LOG_INFO_MSG, LOG_DATA_MSG, LOG_WARN_MSG, LOG_ERROR_MSG deleted — those
// severity bands now emit ID frames via logging_id.h (no text-prefix path).
const char LOG_OK_MSG[] PROGMEM = "OK";
