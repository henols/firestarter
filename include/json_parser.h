/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 */

#ifndef JSON_PARSER_H
#define JSON_PARSER_H

#include "firestarter.h"
#include "jsmn.h"
#include "rurp_shield.h"
#ifdef __cplusplus
extern "C" {
#endif
#define NUMBER_JSNM_TOKENS 64

    int json_init(char* json, int len, jsmntok_t* tokens);
    int json_get_state(char* json, jsmntok_t* tokens, int token_count);
    int json_parse(char* json, jsmntok_t* tokens, int token_count, firestarter_handle_t* handle);
    int json_parse_config(char* json, jsmntok_t* tokens, int token_count, rurp_configuration_t* config);

#ifdef __cplusplus
}
#endif


#endif // JSON_PARSER_H