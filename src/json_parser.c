/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 */


#include "json_parser.h"
#include <stdint.h>
#include <stdlib.h>
#include <stdio.h>
#include <stdbool.h>
#include <string.h>
#include <Arduino.h>

#include "jsmn.h"

int json_init(char* json, int len, jsmntok_t* tokens) {
    jsmn_parser parser;
    jsmn_init(&parser);
    return jsmn_parse(&parser, json, len, tokens, sizeof(tokens) / sizeof(tokens[0]));
}

#define jsoneq(json, tok, s) \
    jsoneq_(json, tok, PSTR(s))
    // jsoneq_(json, tok, s)

static int jsoneq_(const char* json, jsmntok_t* tok, const char* s) {
    if (tok->type == JSMN_STRING && (int)strlen_P(s) == tok->end - tok->start &&
        strncmp_P(json + tok->start, s, tok->end - tok->start) == 0) {
        // strcmp_P(json + tok->start, s) == 0) {
        return 0;
    }
    return -1;
}

int parse_bus_config(firestarter_handle_t* handle, const char* json, jsmntok_t* tokens, int token_count) {
    int consumed_tokens = 0;

    for (int i = 1; i < token_count; i++) {
        if (jsoneq(json, &tokens[i], "bus") == 0) {
            int bus_array_start = i + 1;
            int bus_array_size = tokens[bus_array_start].size;
            for (int j = 0; j < bus_array_size && j < 19; j++) {
                handle->bus_config.address_lines[j] = atoi(json + tokens[bus_array_start + j + 1].start);
            }
            i += bus_array_size + 1;
            consumed_tokens += bus_array_size + 2;
        }
        else if (jsoneq(json, &tokens[i], "rw-pin") == 0) {
            handle->bus_config.rw_line = atoi(json + tokens[i + 1].start);
            i++;
            consumed_tokens += 2;
        }
        else if (jsoneq(json, &tokens[i], "vpp-pin") == 0) {
            handle->bus_config.vpp_line = atoi(json + tokens[i + 1].start);
            i++;
            consumed_tokens += 2;
        }
    }
    return consumed_tokens;
}
int checkBoolean(const char* json) {
    return strncmp(json, "true", 4) == 0;
}

int json_parse(char* json, jsmntok_t* tokens, int token_count, firestarter_handle_t* handle) {
    handle->verbose = 0;
    handle->address = 0;
    handle->skip_erase = 0;
    handle->blank_check = 1;
    handle->bus_config.rw_line = 0xFF;
    handle->bus_config.vpp_line = 0;
    handle->bus_config.address_lines[0] = 0xFF;
    handle->response_code = RESPONSE_CODE_OK;
    handle->chip_id = 0;
    
    for (int i = 1; i < token_count; i++) {
        if (jsoneq(json, &tokens[i], "state") == 0) {
            handle->state = atoi(json + tokens[i + 1].start);
            i++;
        }
        else if (jsoneq(json, &tokens[i], "verbose") == 0) {
            handle->verbose = checkBoolean(json + tokens[i + 1].start);
            i++;
        }
        else if (jsoneq(json, &tokens[i], "memory-size") == 0) {
            handle->mem_size = atol(json + tokens[i + 1].start);
            i++;
        }
        else if (jsoneq(json, &tokens[i], "address") == 0) {
            handle->address = atol(json + tokens[i + 1].start);
            i++;
        }
        else if (jsoneq(json, &tokens[i], "can-erase") == 0) {
            handle->can_erase = checkBoolean(json + tokens[i + 1].start);
            i++;
        }
        else if (jsoneq(json, &tokens[i], "skip-erase") == 0) {
            handle->skip_erase = checkBoolean(json + tokens[i + 1].start);
            handle->blank_check = 0;
            i++;
        }
        else if (jsoneq(json, &tokens[i], "blank-check") == 0) {
            handle->blank_check = checkBoolean(json + tokens[i + 1].start);
            handle->skip_erase = 1;
            i++;
        }
        else if (jsoneq(json, &tokens[i], "chip-id") == 0) {
            handle->chip_id = atoi(json + tokens[i + 1].start);
            i++;
        }
        else if (jsoneq(json, &tokens[i], "type") == 0) {
            handle->mem_type = atoi(json + tokens[i + 1].start);
            i++;
        }
        else if (jsoneq(json, &tokens[i], "pin-count") == 0) {
            handle->pins = atoi(json + tokens[i + 1].start);
            i++;
        }
        else if (jsoneq(json, &tokens[i], "vpp") == 0) {
            handle->vpp = atof(json + tokens[i + 1].start);
            i++;
        }
        else if (jsoneq(json, &tokens[i], "pulse-delay") == 0) {
            handle->pulse_delay = atol(json + tokens[i + 1].start);
            i++;
        }
        else if (jsoneq(json, &tokens[i], "bus-config") == 0) {
            int consumed_tokens = parse_bus_config(handle, json, &tokens[i], token_count - i);
            i += consumed_tokens + 1;
        }
        else {
            handle->response_code = RESPONSE_CODE_ERROR;
            sprintf(handle->response_msg, "Unknown field: %s", json + tokens[i].start);
            return -1;
        }
    }
    return 0;
}

int json_parse_config(char* json, jsmntok_t* tokens, int token_count, rurp_configuration_t* config) {
    int res = 0;
    for (int i = 1; i < token_count; i++) {
        if (jsoneq(json, &tokens[i], "state") == 0) {
            i++;
        }
        else if (jsoneq(json, &tokens[i], "vcc") == 0) {
            config->vcc = atof(json + tokens[i + 1].start);
            i++;
            res = 1;
        }
        else if (jsoneq(json, &tokens[i], "r1") == 0) {
            config->r1 = atol(json + tokens[i + 1].start);
            i++;
            res = 1;
        }
        else if (jsoneq(json, &tokens[i], "r2") == 0) {
            config->r2 = atol(json + tokens[i + 1].start);
            i++;
            res = 1;
        }
        else {
            return -1;
        }
    }
    return res;
}

int json_get_state(char* json, jsmntok_t* tokens, int token_count) {
    for (int i = 0; i < token_count; i++) {
        if (jsoneq(json, &tokens[i], "state") == 0) {
            return atoi(json + tokens[i + 1].start);
        }
    }
    return -1;
}