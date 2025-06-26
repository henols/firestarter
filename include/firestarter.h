/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 */

#ifndef __FIRESTARTER_H__
#define __FIRESTARTER_H__

#include <stdbool.h>
#include <stdint.h>

#include "rurp_shield.h"

#define FW_VERSION VERSION ":" RURP_BOARD_NAME

#ifndef DATA_BUFFER_SIZE
#define DATA_BUFFER_SIZE 512
#endif
#define RESPONSE_MSG_SIZE 96

#define CMD_IDLE 0
#define CMD_READ 1
#define CMD_WRITE 2
#define CMD_ERASE 3
#define CMD_BLANK_CHECK 4
#define CMD_CHECK_CHIP_ID 5
#define CMD_VERIFY 6

#ifdef DEV_TOOLS
#define CMD_DEV_ADDRESS 7
#define CMD_DEV_REGISTER 8
#endif

#define CMD_READ_VPP 11
#define CMD_READ_VPE 12
#define CMD_FW_VERSION 13
#define CMD_CONFIG 14
#define CMD_HW_VERSION 15

#define RESPONSE_CODE_OK 1
#define RESPONSE_CODE_WARNING 2
#define RESPONSE_CODE_ERROR 0

// Control flags
#define FLAG_FORCE 0x01
#define FLAG_CAN_ERASE 0x02
#define FLAG_SKIP_ERASE 0x04
#define FLAG_SKIP_BLANK_CHECK 0x08
#define FLAG_VPE_AS_VPP 0x10

#define FLAG_OUTPUT_ENABLE 0x20
#define FLAG_CHIP_ENABLE 0x40

#define firestarter_warning_response(msg) \
    firestarter_set_responce(RESPONSE_CODE_WARNING, msg)

#define firestarter_warning_response_format(msg, ...) \
    firestarter_response_format(RESPONSE_CODE_WARNING, msg, __VA_ARGS__)

#define firestarter_error_response(msg) \
    firestarter_set_responce(RESPONSE_CODE_ERROR, msg)

#define firestarter_error_response_format(msg, ...) \
    firestarter_response_format(RESPONSE_CODE_ERROR, msg, __VA_ARGS__)

#define firestarter_set_responce(code, msg)    \
    copy_to_buffer(handle->response_msg, msg); \
    handle->response_code = code;

#define firestarter_response_format(code, msg, ...) \
    format(handle->response_msg, msg, __VA_ARGS__); \
    handle->response_code = code;

#define is_flag_set(flag) \
    ((handle->ctrl_flags & flag) == flag)



#define INITZIATED 0x01
#define INITZIATION_IN_PROGRESS 0x02
#define ENDED 0x04
#define ENDING_IN_PROGRESS 0x08

#define prefered_operation_state(flag) \
    (handle->operation_state = flag<<4 | (handle->operation_state & 0x0F))

#define set_prefered_operation_state() \
    (handle->operation_state |= flag>>4)

#define clear_prefered_operation_state() \
    (handle->operation_state &= ~flag>>4)

#define check_operation_state(flag) \
    ((handle->operation_state & flag) == flag)

#define set_operation_state(flag) \
    (handle->operation_state |= flag)
#define clear_operation_state(flag) \
    (handle->operation_state &= ~flag)

#define ADDRESS_LINES_SIZE 20

typedef struct bus_config {
    uint8_t address_lines[ADDRESS_LINES_SIZE];  // Array mapping address lines
    uint32_t address_mask;                      // Mask for address lines
    uint8_t matching_lines;                     // Number of matching address lines
    uint8_t rw_line;                            // RW line mapping
    uint8_t vpp_line;                           // VPP line mapping
} bus_config_t;

typedef struct firestarter_handle {
    uint8_t verbose;
    uint8_t cmd;
    uint8_t operation_state;
    uint8_t response_code;
    char response_msg[RESPONSE_MSG_SIZE];
    uint8_t mem_type;
    uint32_t protocol;
    uint8_t pins;
    uint32_t mem_size;
    uint32_t address;
    float vpp;
    uint32_t pulse_delay;
    uint32_t ctrl_flags;
    uint16_t chip_id;
    char data_buffer[DATA_BUFFER_SIZE];
    uint32_t data_size;
    bus_config_t bus_config;

    void (*firestarter_operation_init)(struct firestarter_handle*);
    void (*firestarter_operation_execute)(struct firestarter_handle*);
    void (*firestarter_operation_end)(struct firestarter_handle*);

    void (*firestarter_set_data)(struct firestarter_handle*, uint32_t, uint8_t);
    uint8_t (*firestarter_get_data)(struct firestarter_handle*, uint32_t);

    void (*firestarter_set_address)(struct firestarter_handle*, uint32_t);

    void (*firestarter_set_control_register)(struct firestarter_handle*, rurp_register_t, bool);
    bool (*firestarter_get_control_register)(struct firestarter_handle*, rurp_register_t);

} firestarter_handle_t;

#endif  // __FIRESTARTER_H__