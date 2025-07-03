/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 */

#include "json_parser.h"

#include <stdlib.h>

#include "jsmn.h"
#include "logging.h"

uint8_t get_cmd(const char* json, jsmntok_t* tokens, int pos);

int parse_bus_config(const char* json, jsmntok_t* tokens, int token_count, firestarter_handle_t* handle);

bool get_flags(const char* json, jsmntok_t* tokens, int pos, firestarter_handle_t* handle);
bool get_memory_size(const char* json, jsmntok_t* tokens, int pos, firestarter_handle_t* handle);
bool get_address(const char* json, jsmntok_t* tokens, int pos, firestarter_handle_t* handle);
bool get_chip_id(const char* json, jsmntok_t* tokens, int pos, firestarter_handle_t* handle);
bool get_type(const char* json, jsmntok_t* tokens, int pos, firestarter_handle_t* handle);
bool get_pin_count(const char* json, jsmntok_t* tokens, int pos, firestarter_handle_t* handle);
bool get_delay(const char* json, jsmntok_t* tokens, int pos, firestarter_handle_t* handle);
bool get_vpp(const char* json, jsmntok_t* tokens, int pos, firestarter_handle_t* handle);

bool get_rw_pin(const char* json, jsmntok_t* tokens, int pos, firestarter_handle_t* handle);
bool get_vpp_pin(const char* json, jsmntok_t* tokens, int pos, firestarter_handle_t* handle);

bool get_r1(const char* json, jsmntok_t* tokens, int pos, rurp_configuration_t* config);
bool get_r2(const char* json, jsmntok_t* tokens, int pos, rurp_configuration_t* config);
bool get_rev(const char* json, jsmntok_t* tokens, int pos, rurp_configuration_t* config);

static int jsoneq_(const char* json, jsmntok_t* tok, const char* s);

#define jsoneq(json, tok, s) \
    jsoneq_(json, tok, PSTR(s))

int json_init(const char* json, int len, jsmntok_t* tokens) {
    jsmn_parser parser;
    jsmn_init(&parser);
    return jsmn_parse(&parser, json, len, tokens, sizeof(tokens) / sizeof(tokens[0]));
}

int json_parse(const char* json, jsmntok_t* tokens, int token_count, firestarter_handle_t* handle) {
    handle->address = 0;
    handle->ctrl_flags = 0;
    handle->bus_config.rw_line = 0xFF;
    handle->bus_config.vpp_line = 0xFF;
    handle->bus_config.address_lines[0] = 0xFF;
    handle->bus_config.address_mask = 0;
    handle->chip_id = 0;

    for (int i = 1; i < token_count; i++) {
        uint8_t cmd = get_cmd(json, tokens, i);
        if (cmd != 0xFF) {
            handle->cmd = cmd;
            i++;
        } else if (get_memory_size(json, tokens, i, handle)) {
            i++;
        } else if (get_address(json, tokens, i, handle)) {
            i++;
        } else if (get_flags(json, tokens, i, handle)) {
            i++;
        } else if (get_chip_id(json, tokens, i, handle)) {
            i++;
        } else if (get_pin_count(json, tokens, i, handle)) {
            i++;
        } else if (get_delay(json, tokens, i, handle)) {
            i++;
        } else if (get_vpp(json, tokens, i, handle)) {
            i++;
        } else if (get_type(json, tokens, i, handle)) {
            i++;
        } else if (get_pin_count(json, tokens, i, handle)) {
            i++;
        } else if (jsoneq(json, &tokens[i], "bus-config") == 0) {
            i +=  parse_bus_config(json, &tokens[i], token_count - i, handle) + 1;
        } else {
            firestarter_error_response_format("Unknown field: %s", json + tokens[i].start);
            return -1;
        }
    }
    if (handle->bus_config.address_lines[0] == 0xFF) {
        handle->bus_config.address_mask = 0xFFFF;
    }
    return 0;
}

int json_parse_config(const char* json, jsmntok_t* tokens, int token_count, rurp_configuration_t* config, firestarter_handle_t* handle) {
    int res = 0;
    for (int i = 1; i < token_count; i++) {
        if (get_cmd(json, tokens, i) != 0xFF) {
            i++;
        } else if (get_flags(json, tokens, i, handle)) {
            i++;
        }
#ifdef HARDWARE_REVISION
        else if (get_rev(json, tokens, i, config)) {
            i++;
            res = 1;
        }
#endif
        else if (get_r1(json, tokens, i, config)) {
            i++;
            res = 1;
        } else if (get_r2(json, tokens, i, config)) {
            i++;
            res = 1;
        } else {
            return -1;
        }
    }
    return res;
}

uint8_t json_get_cmd(const char* json, jsmntok_t* tokens, int token_count, firestarter_handle_t* handle) {
    handle->cmd = 0xFF;
    handle->ctrl_flags = 0;
    bool found_flags = false;
    for (int i = 0; i < token_count; i++) {
        uint8_t cmd = get_cmd(json, tokens, i);
        if (cmd != 0xFF) {
            handle->cmd = cmd;
            i++;
        } else if (get_flags(json, tokens, i, handle)) {
            i++;
            found_flags = true;
        }
        if (handle->cmd != 0xFF && found_flags) {
            break;
        }
    }
    return handle->cmd;
}

uint8_t get_cmd(const char* json, jsmntok_t* tokens, int pos) {
    if (jsoneq(json, &tokens[pos], "cmd") == 0 || jsoneq(json, &tokens[pos], "state") == 0) {
        return atoi(json + tokens[pos + 1].start);
    }
    return 0xFF;
}

int parse_bus_config(const char* json, jsmntok_t* tokens, int token_count, firestarter_handle_t* handle) {
    int consumed_tokens = 0;

    for (int i = 1; i < token_count; i++) {
        if (jsoneq(json, &tokens[i], "bus") == 0) {
            handle->bus_config.matching_lines = 0xff;
            int bus_array_start = i + 1;
            int bus_array_size = tokens[bus_array_start].size;
            for (int j = 0; j < bus_array_size && j < ADDRESS_LINES_SIZE; j++) {
                handle->bus_config.address_lines[j] = atoi(json + tokens[bus_array_start + j + 1].start);
                handle->bus_config.address_mask |= 1UL << handle->bus_config.address_lines[j];
                if (handle->bus_config.matching_lines == 0xff && handle->bus_config.address_lines[j] != j) {
                    handle->bus_config.matching_lines = j;
                }
            }
            if (handle->bus_config.matching_lines == 0xff) {
                handle->bus_config.matching_lines = bus_array_size;
            }
            if (bus_array_size < ADDRESS_LINES_SIZE) {
                handle->bus_config.address_lines[bus_array_size] = 0xFF;
            }
            i += bus_array_size + 1;
            consumed_tokens += bus_array_size + 2;
        } else if (get_rw_pin(json, tokens, i, handle)) {
            i++;
            consumed_tokens += 2;
        } else if (get_vpp_pin(json, tokens, i, handle)) {
            i++;
            consumed_tokens += 2;
        }
    }
    return consumed_tokens;
}

static int jsoneq_(const char* json, jsmntok_t* tok, const char* s) {
    if (tok->type == JSMN_STRING && (int)strlen_P(s) == tok->end - tok->start &&
        strncmp_P(json + tok->start, s, tok->end - tok->start) == 0) {
        return 0;
    }
    return -1;
}

#define extract_num(element, register, type)           \
    if (jsoneq(json, &tokens[pos], element) == 0) {    \
        register = type(json + tokens[pos + 1].start); \
        return 1;                                      \
    }                                                  \
    return 0;

#define extract_long(element, register) \
    extract_num(element, register, atol)

#define extract_int(element, register) \
    extract_num(element, register, atoi)

#define extract_float(element, register) \
    extract_num(element, register, atof)

bool get_flags(const char* json, jsmntok_t* tokens, int pos, firestarter_handle_t* handle) {
    extract_long("flags", handle->ctrl_flags);
}

bool get_memory_size(const char* json, jsmntok_t* tokens, int pos, firestarter_handle_t* handle) {
    extract_long("memory-size", handle->mem_size);
}

bool get_address(const char* json, jsmntok_t* tokens, int pos, firestarter_handle_t* handle) {
    extract_long("address", handle->address);
}

bool get_chip_id(const char* json, jsmntok_t* tokens, int pos, firestarter_handle_t* handle) {
    extract_int("chip-id", handle->chip_id);
}

bool get_pin_count(const char* json, jsmntok_t* tokens, int pos, firestarter_handle_t* handle) {
    extract_int("pin-count", handle->pins);
}

bool get_type(const char* json, jsmntok_t* tokens, int pos, firestarter_handle_t* handle) {
    extract_int("type", handle->mem_type);
}

bool get_delay(const char* json, jsmntok_t* tokens, int pos, firestarter_handle_t* handle) {
    extract_long("pulse-delay", handle->pulse_delay);
}

bool get_vpp(const char* json, jsmntok_t* tokens, int pos, firestarter_handle_t* handle) {
    extract_float("vpp", handle->vpp);
}

bool get_rw_pin(const char* json, jsmntok_t* tokens, int pos, firestarter_handle_t* handle) {
    extract_int("rw-pin", handle->bus_config.rw_line);
}

bool get_vpp_pin(const char* json, jsmntok_t* tokens, int pos, firestarter_handle_t* handle) {
    extract_int("vpp-pin", handle->bus_config.vpp_line);
}

bool get_r1(const char* json, jsmntok_t* tokens, int pos, rurp_configuration_t* config) {
    extract_long("r1", config->r1);
}

bool get_r2(const char* json, jsmntok_t* tokens, int pos, rurp_configuration_t* config) {
    extract_long("r2", config->r2);
}

bool get_rev(const char* json, jsmntok_t* tokens, int pos, rurp_configuration_t* config) {
    extract_float("rev", config->hardware_revision);
}
