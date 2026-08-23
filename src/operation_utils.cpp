/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 */

#include "operation_utils.h"

#include <Arduino.h>
#include <stdlib.h>

#include "firestarter.h"
#include "logging_id.h"
#include "messages.h"
#include "rurp_shield.h"

#define ERROR -1
#define RETURN 0
#define CONTINUE 1

#define set_operation_state(state) \
    (handle->operation_state = (handle->operation_state & 0xc0) | state)

// Preserve flags (top 2 bits), increment state (lower 6 bits)
#define set_operation_state_done() \
    handle->operation_state = (handle->operation_state & 0xC0) | ((handle->operation_state & 0x3F) + 1)

// Check state (lower 6 bits), ignore flags (top 2 bits)
#define is_operation_started(state) \
    ((handle->operation_state & 0x3F) == state)

#define can_operation_start(state) \
    is_operation_started(state - 1)

#define execute_operation_state(state) \
    (can_operation_start(state) || is_operation_started(state))

#define is_all_operations_done() \
    is_operation_started(ENDED)

static inline bool _check_response(firestarter_handle_t* handle);
static inline int _execute_operation(void (*callback)(firestarter_handle_t* handle), firestarter_handle_t* handle);
static inline int _execute_operation_house_keeping(firestarter_handle_t* handle);
static inline int _execute_operation_house_keeping_func(void (*callback)(firestarter_handle_t* handle), int state, firestarter_handle_t* handle);
static inline bool _single_step_operation_callback(firestarter_handle_t* handle);

/**
 * @brief Executes a simple, non-stateful operation.
 *
 * This is a wrapper around op_execute_stateful_operation for operations that are
 * expected to complete within a single logical step (e.g., blank check). It uses
 * a callback that executes the main operation logic and marks the operation as
 * done immediately after.
 *
 * @param handle Pointer to the firestarter handle.
 * @return true when fully completed, false while the operation is in progress (e.g., waiting for ACKs).
 */
bool op_execute_simple_operation(firestarter_handle_t* handle) {
    return op_execute_stateful_operation(_single_step_operation_callback, handle);
}

bool op_execute_stateful_operation(bool (*callback)(firestarter_handle_t* handle), firestarter_handle_t* handle) {
    if (handle->firestarter_operation_main) {
        if (is_all_operations_done()) {
            // The operation is complete from the firmware's perspective.
            // The host sends a final ACK to close the transaction.
            // We wait for it and then signal that the command is finished.
            if (op_get_message(handle) == OP_MSG_INCOMPLETE) {
                return false;  // Not finished yet, waiting for final ACK
            }
            return true;  // Received final ACK (or junk), command is finished.
        }

        int res = _execute_operation_house_keeping(handle);
        if (res != CONTINUE) {
            return res != RETURN;
        }
        if (is_operation_started(MAIN)) {
            // The callback keeps its OWN documented convention (true on
            // success/continue, false on error) -- see _process_incoming_data
            // and _process_outgoing_data (eprom_operations.cpp). Flipping the
            // engine to return true-on-finished does not flip the callback,
            // so this is the one surviving negation: the nine wrapper call
            // sites no longer negate, but this single site still does.
            return !callback(handle);
        }
        return false;
    }
    // v1.22 Phase 119 D-06/D-07 (119-07 Task 2) -- the generic NULL-main
    // refusal. This is the ONE site that closes the whole phantom-success
    // class, not just SDP's corner of it. Five things this comment must
    // record (per the plan's task instructions):
    //
    // 1. THE MECHANISM IT FIXES. Before this change, a NULL
    //    firestarter_operation_main fell through to a bare `return false`
    //    here. At the time, every eprom_* caller inverted that return
    //    (`return !op_execute_stateful_operation(...)`), so the command
    //    reported "finished". loop() (firestarter.cpp:216) had already set
    //    handle.response_code = RESPONSE_CODE_OK before the dispatch switch
    //    ran, and nothing on this path ever wrote it. So the operation
    //    reported OK, emitted no error frame, and emitted no MSG_MAIN_DONE
    //    either -- it emitted nothing at all. That silence is DEVTEST-01's
    //    "dev test reports OK having done nothing" phantom erase.
    //
    // 2. WHY THE GUARD LIVES HERE AND NOWHERE ELSE (D-06). Single site,
    //    smallest flash cost, and provably TOTAL: any protocol whose
    //    handler has no arm for a command is refused here, present and
    //    future, with no per-handler maintenance. Two alternatives were
    //    rejected: (a) a pre-dispatch `protocol != 0x0D` check in
    //    configure_memory -- that would put 0x0D-specific capability
    //    knowledge into the generic dispatcher that v1.20's protocol-only
    //    rebuild deliberately kept clean; (b) a `default:` arm in every one
    //    of the six configure_* handlers -- roughly 90-130 B against a
    //    Leonardo headroom of ~2718 B for zero additional coverage over this
    //    one guard, and each of the six arms would have to be hand-written
    //    not to swallow the pre-set generic mains (see item 3).
    //
    // 3. WHY THIS CANNOT BREAK read/write/verify (D-05's other half).
    //    configure_memory pre-sets the generic main for CMD_READ, CMD_WRITE
    //    and CMD_VERIFY (proms/memory.cpp:48-58) BEFORE the protocol chain
    //    runs, so those three commands are never NULL-main for any protocol
    //    that reaches a configure_* handler -- a source-level invariant, not
    //    a hope, and test_dispatch/test_configure_memory.cpp pins it as a
    //    positive case. This is also why LOCK-04's ROADMAP-stated mechanism
    //    (a `default:` arm inside configure_eeprom28c) was disproven and
    //    corrected rather than implemented: that literal arm would fire for
    //    CMD_READ and CMD_VERIFY too, on all 84 protocol-0x0D chips, because
    //    configure_eeprom28c's own switch only overrides CMD_WRITE and adds
    //    CMD_BLANK_CHECK, leaving the pre-set generic mains for read/verify
    //    to fall through into that arm. LOCK-04 is mechanism-corrected,
    //    intent-satisfied by this single guard -- never read as failed.
    //
    // 4. THE BLAST RADIUS, AND WHAT IT DOES NOT REACH. This guard is
    //    generic, so it changes observable behaviour for every previously
    //    silent-OK (cmd, protocol) cell -- intentionally, per D-07/D-08.
    //    But op_execute_stateful_operation is reached ONLY from the six
    //    eprom_* entry points in eprom_operations.cpp; hw_read_voltage,
    //    fw_get_version, hw_get_version, hw_get_config, dt_set_registers and
    //    dt_set_address never touch the op layer at all, so `vpp`, `vpe`,
    //    `fw`, `config`, `hw`, `dev reg` and `dev address` are structurally
    //    outside this guard's reach. Also: configure_not_implemented
    //    protocols are UNCHANGED by this guard -- that handler sets
    //    response_code = RESPONSE_CODE_ERROR itself, so
    //    op_execute_function(configure_memory, ...) already returns false
    //    and parse_json already emits MSG_ERR_SETUP before the op layer is
    //    ever reached. No double error, no new frame there.
    //
    // 5. THE HOST-SIDE NOTE. firestarter_app/firestarter/eprom_operations.py's
    //    _SRAM_PROTO_IDS workaround short-circuits SRAM/FRAM blank-check
    //    BEFORE issuing any firmware command, so this guard is not reachable
    //    from check_eprom_blank. It does NOT become dead code: it fires
    //    earlier and produces a materially better user-facing message than
    //    a bare MSG_ERR_NOT_SUPPORTED would. Its comment's claim that the
    //    firmware emits 0xA4 MSG_ERR_EMPTY_INPUT is a follow-on artifact of
    //    the old silent completion (the firmware returns to CMD_IDLE, then
    //    misreads the host's next byte as a fresh frame), not a firmware
    //    refusal. Correct Phase 120 disposition: KEEP that workaround.
    //
    // This site now returns `true` directly -- the engine reports finished
    // as `true` and the nine eprom_* wrappers forward that result without
    // inverting it -- so the command still reports finished and
    // command_done() still runs (chip disabled, registers zeroed) exactly as
    // before. What changes relative to the pre-D-06 state is that an error
    // frame is now emitted and response_code is
    // RESPONSE_CODE_ERROR instead of the RESPONSE_CODE_OK loop() set: the
    // command still terminates cleanly, it just stops lying about what it
    // did. MSG_ERR_NOT_SUPPORTED (0xA5) already exists and is already
    // eprom_erase's FLAG_CAN_ERASE refusal id -- no new catalog id needed.
    LOG_ERROR_ID(MSG_ERR_NOT_SUPPORTED);
    handle->response_code = RESPONSE_CODE_ERROR;
    return true;
}

/**
 * @brief Executes a provided function with standard operation wrappers.
 *
 * This function wraps the execution of a given callback. It sets the programmer mode,
 * executes the callback, resets the communication mode, resets the timeout, and
 * checks the response from the handle.
 *
 * @param callback The function to execute.
 * @param handle Pointer to the firestarter handle.
 * @return true if the operation was successful or is waiting for data, false on error.
 */
bool op_execute_function(void (*callback)(firestarter_handle_t* handle), firestarter_handle_t* handle) {
    if (callback != NULL) {
        return _execute_operation(callback, handle) != ERROR;
    }
    return false;
}

bool op_wait_for_ack(firestarter_handle_t* handle) {
    unsigned long timeout = millis() + 1000;
    while (millis() < timeout) {
        op_message_type msg_type = op_get_message(handle);
        if (msg_type == OP_MSG_ACK) {
            return true;
        }
        if (msg_type == OP_MSG_ERROR) {
            return false;
        }
        delay(10);
    }
    LOG_ERROR_ID(MSG_ERR_TIMEOUT);
    return false;
}

/**
 * @brief Parses the incoming serial stream for messages from the host.
 *
 * This function is non-blocking. It checks for "OK" (ACK), "DONE", and data packets ('#').
 * It consumes junk characters until a valid message start is found.
 * @param handle Pointer to the firestarter handle, used to store incoming data.
 * @return An op_message_type enum value indicating the message found, or OP_MSG_INCOMPLETE if no full message is available.
 */
op_message_type op_get_message(firestarter_handle_t* handle) {
    if (rurp_communication_available() <= 0) {
        return OP_MSG_INCOMPLETE;
    }
    while (rurp_communication_available() > 0) {
        int peek = rurp_communication_peak();
        switch (peek) {
            case 'O':  // Potential "OK"
                if (rurp_communication_available() < 2) {
                    return OP_MSG_INCOMPLETE;
                }
                rurp_communication_read();  // consume 'O'
                if (rurp_communication_peak() == 'K') {
                    rurp_communication_read();  // consume 'K'
                    return OP_MSG_ACK;
                }
                // Not "OK", 'O' is consumed. Loop will treat next char as junk.
                break;

            case 'D':  // Potential "DONE"
                if (rurp_communication_available() < 4) {
                    return OP_MSG_INCOMPLETE;
                }
                char done_buf[4];
                rurp_communication_read_bytes(done_buf, 4);
                if (strncmp_P(done_buf, PSTR("DONE"), 4) == 0) {
                    return OP_MSG_DONE;
                }
                // Not "DONE", 4 bytes consumed. This is a risk.
                break;

            case '#': {  // Data packet
                // COBS framing is delimiter-driven (no fixed header size).
                // Execution reaches here only after peak()=='#' confirmed
                // available()>=1; the inner guard is unreachable.
                rurp_communication_read();  // consume '#'
                int res = rurp_communication_read_data(handle->data_buffer, DATA_BUFFER_SIZE);
                if (res < 0) {
                    LOG_ERROR_ID_U16(MSG_ERR_DATA_ERR_N, (uint16_t)res);
                    return OP_MSG_ERROR;
                }
                handle->data_size = res;
                return OP_MSG_DATA;
            }
            default:
                rurp_communication_read();
                break;
        }
    }
    return OP_MSG_INCOMPLETE;  // Nothing in buffer
}

void set_operation_to_done(firestarter_handle_t* handle) {
    LOG_INFO_ID(MSG_INFO_MAIN_DONE);
    set_operation_state_done();
    LOG_MAIN_ID(MSG_MAIN_DONE);
}

/**
 * @brief Manages the state transitions of an operation (INIT, MAIN, END).
 *
 * This function orchestrates the execution of the init and end phases of an operation,
 * ensuring they run in the correct order around the main operation logic.
 *
 * @param handle Pointer to the firestarter handle.
 * @return CONTINUE if the state machine should proceed, RETURN or ERROR to stop.
 */
static inline int _execute_operation_house_keeping(firestarter_handle_t* handle) {
    if (is_all_operations_done()) {
        return CONTINUE;
    }
    if (is_operation_started(MAIN)) {
        return CONTINUE;
    }
    if (can_operation_start(MAIN)) {
        if (!op_wait_for_ack(handle)) {
            return ERROR;
        }
        op_reset_timeout();
        set_operation_state(MAIN);
        LOG_INFO_ID(MSG_INFO_MAIN_START);
        return CONTINUE;
    }
    int res = _execute_operation_house_keeping_func(handle->firestarter_operation_init, INIT, handle);
    if (res != CONTINUE) {
        return res;
    }

    return _execute_operation_house_keeping_func(handle->firestarter_operation_end, END, handle);
}

/**
 * @brief Executes a specific housekeeping phase (INIT or END) for an operation.
 *
 * This function handles the execution loop for a specific state (INIT or END).
 * It waits for an ACK, runs the provided callback, and sends a completion message.
 *
 * @param callback The function to call (e.g., firestarter_operation_init).
 * @param state The operation state to manage (e.g., INIT).
 * @param handle Pointer to the firestarter handle.
 * @return CONTINUE if the phase is complete, RETURN or ERROR to stop.
 */
static inline int _execute_operation_house_keeping_func(void (*callback)(firestarter_handle_t* handle), int state, firestarter_handle_t* handle) {
    if (execute_operation_state(state)) {
        if (can_operation_start(state)) {
            if (!op_wait_for_ack(handle)) {
                return ERROR;
            }
            if (state == INIT) {
                LOG_INFO_ID(MSG_INFO_INIT_START);
            } else {
                LOG_INFO_ID(MSG_INFO_END_START);
            }
            set_operation_state(state);
        }

        if (_execute_operation(callback, handle) == ERROR) {
            return ERROR;
        }

        if (is_operation_in_progress(handle)) {
            return RETURN;
        }

        if (state == INIT) {
            LOG_INIT_ID(MSG_INIT_DONE);
        } else {
            LOG_END_ID(MSG_END_DONE);
        }
        set_operation_state_done();
    }
    return CONTINUE;
}

/**
 * @brief A callback for simple operations that completes in one step.
 *
 * This function is used as a callback for op_execute_simple_operation.
 * It calls the main operation function and, if successful, immediately marks the operation as done.
 *
 * @param handle Pointer to the firestarter handle.
 * @return true on success, false on error.
 */
static inline bool _single_step_operation_callback(firestarter_handle_t* handle) {
    int res = _execute_operation(handle->firestarter_operation_main, handle);
    // _execute_operation runs the main op in programmer mode (com_mode=false) and
    // restores communication mode before returning. On the Uno, rurp_log_id is
    // com_mode-gated, so a multi-step op (blank-check) cannot emit progress/errors
    // from inside programmer mode — they are silently dropped and the host times out.
    // For the standalone blank-check command, flush those frames HERE, in
    // communication mode. mem_util_blank_check stashes the not-blank offset+value in
    // data_buffer (data_size==4) and leaves handle->address as the progress counter.
    // (#transport-protocol-verify)
    if (handle->cmd == CMD_BLANK_CHECK) {
        if (res == ERROR && handle->data_size == 4) {
            LOG_ERROR_ID_BYTES(MSG_ERR_NOT_BLANK, (const uint8_t*)handle->data_buffer, 4);
        } else if (res != ERROR && is_operation_in_progress(handle)) {
            LOG_DATA_ID_U32_U32(MSG_DATA_PROGRESS, handle->address, handle->mem_size);
        }
    }
    if (res == ERROR) {
        return false;
    }
    if (!is_operation_in_progress(handle)) {
        set_operation_to_done(handle);
    }
    return true;  // Success,
}

/**
 * @brief Executes a callback function, wrapping it with mode changes and response checking.
 *
 * @param callback The function to execute.
 * @param handle Pointer to the firestarter handle, which will be passed to the callback.
 * @return true if the operation was successful, false on error.
 */
static inline int _execute_operation(void (*callback)(firestarter_handle_t* handle), firestarter_handle_t* handle) {
    if (callback != NULL) {
        rurp_set_programmer_mode();
        callback(handle);
        rurp_set_communication_mode();
        return _check_response(handle) ? RETURN : ERROR;
    }
    return CONTINUE;
}

/**
 * @brief Checks and handles the response code in the firestarter handle.
 *
 * Logs messages based on the response code and sends data if required.
 *
 * @param handle Pointer to the firestarter handle.
 * @return true if the response is OK, WARNING, or DATA. false if it's an ERROR.
 */
static inline bool _check_response(firestarter_handle_t* handle) {
    switch (handle->response_code) {
        case RESPONSE_CODE_OK:
            break;
        case RESPONSE_CODE_WARNING:
            break;
        case RESPONSE_CODE_DATA:
            rurp_communication_write(handle->data_buffer, handle->data_size);
            break;
        case RESPONSE_CODE_ERROR:
        default:
            return false;
    }
    op_reset_timeout();
    handle->response_code = RESPONSE_CODE_OK;
    return true;
}
