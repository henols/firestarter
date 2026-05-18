/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 *
 * Phase 6 — convenience macros for the ID-encoded log path (LFW-02).
 *
 * These macros wrap rurp_log_id() so call-sites can emit catalog-driven
 * binary frames without manually packing param byte arrays. Multi-byte
 * params are encoded MSB-first per CONTEXT §D-01..D-04.
 *
 * Coexists with the legacy log_*_const / log_*_format macros in logging.h
 * (LMIG-01). No existing call-site is converted in Phase 6 — these macros
 * are the surface Phases 7-8 will migrate call-sites to.
 */

#ifndef __LOGGING_ID_H__
#define __LOGGING_ID_H__

#include "firestarter.h"
#include "messages.h"
#include "rurp_shield.h"

// --- Unconditional ID-frame emit ---

// Zero-param: emit just the ID, no params.
#define LOG_ID(id) rurp_log_id((id), NULL, 0)

// Single u8 param, raw byte on the wire.
#define LOG_ID_U8(id, p1)                                              \
    do {                                                               \
        uint8_t _b[1] = { (uint8_t)(p1) };                             \
        rurp_log_id((id), _b, 1);                                      \
    } while (0)

// Single u16 param, MSB-first (2 wire bytes).
#define LOG_ID_U16(id, p1)                                             \
    do {                                                               \
        uint16_t _v = (uint16_t)(p1);                                  \
        uint8_t _b[2] = {                                              \
            (uint8_t)((_v >> 8) & 0xFF),                               \
            (uint8_t)(_v & 0xFF),                                      \
        };                                                             \
        rurp_log_id((id), _b, 2);                                      \
    } while (0)

// Single u24 param, MSB-first (3 wire bytes). Caller passes u32-ish; top byte dropped.
#define LOG_ID_U24(id, p1)                                             \
    do {                                                               \
        uint32_t _v = (uint32_t)(p1);                                  \
        uint8_t _b[3] = {                                              \
            (uint8_t)((_v >> 16) & 0xFF),                              \
            (uint8_t)((_v >> 8) & 0xFF),                               \
            (uint8_t)(_v & 0xFF),                                      \
        };                                                             \
        rurp_log_id((id), _b, 3);                                      \
    } while (0)

// Single u32 param, MSB-first (4 wire bytes).
#define LOG_ID_U32(id, p1)                                             \
    do {                                                               \
        uint32_t _v = (uint32_t)(p1);                                  \
        uint8_t _b[4] = {                                              \
            (uint8_t)((_v >> 24) & 0xFF),                              \
            (uint8_t)((_v >> 16) & 0xFF),                              \
            (uint8_t)((_v >> 8) & 0xFF),                               \
            (uint8_t)(_v & 0xFF),                                      \
        };                                                             \
        rurp_log_id((id), _b, 4);                                      \
    } while (0)

// Escape hatch — caller-supplied buffer + count.
#define LOG_ID_BYTES(id, buf_array, count) \
    rurp_log_id((id), (const uint8_t*)(buf_array), (uint8_t)(count))

// --- FLAG_VERBOSE-gated variants (INFO severity equivalent) ---

#define LOG_INFO_ID(id)                                                \
    do {                                                               \
        if (is_flag_set(FLAG_VERBOSE)) {                               \
            LOG_ID(id);                                                \
        }                                                              \
    } while (0)

#define LOG_INFO_ID_U8(id, p1)                                         \
    do {                                                               \
        if (is_flag_set(FLAG_VERBOSE)) {                               \
            LOG_ID_U8((id), (p1));                                     \
        }                                                              \
    } while (0)

#define LOG_INFO_ID_U16(id, p1)                                        \
    do {                                                               \
        if (is_flag_set(FLAG_VERBOSE)) {                               \
            LOG_ID_U16((id), (p1));                                    \
        }                                                              \
    } while (0)

#define LOG_INFO_ID_U24(id, p1)                                        \
    do {                                                               \
        if (is_flag_set(FLAG_VERBOSE)) {                               \
            LOG_ID_U24((id), (p1));                                    \
        }                                                              \
    } while (0)

#define LOG_INFO_ID_U32(id, p1)                                        \
    do {                                                               \
        if (is_flag_set(FLAG_VERBOSE)) {                               \
            LOG_ID_U32((id), (p1));                                    \
        }                                                              \
    } while (0)

#define LOG_INFO_ID_BYTES(id, buf_array, count)                        \
    do {                                                               \
        if (is_flag_set(FLAG_VERBOSE)) {                               \
            LOG_ID_BYTES((id), (buf_array), (count));                  \
        }                                                              \
    } while (0)

// --- Unconditional ERROR severity ---

#define LOG_ERROR_ID(id)               LOG_ID(id)
#define LOG_ERROR_ID_U8(id, p1)        LOG_ID_U8((id), (p1))
#define LOG_ERROR_ID_U16(id, p1)       LOG_ID_U16((id), (p1))
#define LOG_ERROR_ID_U24(id, p1)       LOG_ID_U24((id), (p1))
#define LOG_ERROR_ID_U32(id, p1)       LOG_ID_U32((id), (p1))
#define LOG_ERROR_ID_BYTES(id, b, n)   LOG_ID_BYTES((id), (b), (n))

// --- Unconditional WARN severity ---

#define LOG_WARN_ID(id)                LOG_ID(id)
#define LOG_WARN_ID_U8(id, p1)         LOG_ID_U8((id), (p1))
#define LOG_WARN_ID_U16(id, p1)        LOG_ID_U16((id), (p1))
#define LOG_WARN_ID_U24(id, p1)        LOG_ID_U24((id), (p1))
#define LOG_WARN_ID_U32(id, p1)        LOG_ID_U32((id), (p1))
#define LOG_WARN_ID_BYTES(id, b, n)    LOG_ID_BYTES((id), (b), (n))

// --- Unconditional OK severity ---

#define LOG_OK_ID(id)                  LOG_ID(id)
#define LOG_OK_ID_U8(id, p1)           LOG_ID_U8((id), (p1))
#define LOG_OK_ID_U16(id, p1)          LOG_ID_U16((id), (p1))
#define LOG_OK_ID_U24(id, p1)          LOG_ID_U24((id), (p1))
#define LOG_OK_ID_U32(id, p1)          LOG_ID_U32((id), (p1))
#define LOG_OK_ID_BYTES(id, b, n)      LOG_ID_BYTES((id), (b), (n))

// --- Unconditional INIT severity ---

#define LOG_INIT_ID(id)                LOG_ID(id)
#define LOG_INIT_ID_U8(id, p1)         LOG_ID_U8((id), (p1))
#define LOG_INIT_ID_U16(id, p1)        LOG_ID_U16((id), (p1))
#define LOG_INIT_ID_U24(id, p1)        LOG_ID_U24((id), (p1))
#define LOG_INIT_ID_U32(id, p1)        LOG_ID_U32((id), (p1))
#define LOG_INIT_ID_BYTES(id, b, n)    LOG_ID_BYTES((id), (b), (n))

// --- Unconditional MAIN severity ---

#define LOG_MAIN_ID(id)                LOG_ID(id)
#define LOG_MAIN_ID_U8(id, p1)         LOG_ID_U8((id), (p1))
#define LOG_MAIN_ID_U16(id, p1)        LOG_ID_U16((id), (p1))
#define LOG_MAIN_ID_U24(id, p1)        LOG_ID_U24((id), (p1))
#define LOG_MAIN_ID_U32(id, p1)        LOG_ID_U32((id), (p1))
#define LOG_MAIN_ID_BYTES(id, b, n)    LOG_ID_BYTES((id), (b), (n))

// --- Unconditional END severity ---

#define LOG_END_ID(id)                 LOG_ID(id)
#define LOG_END_ID_U8(id, p1)          LOG_ID_U8((id), (p1))
#define LOG_END_ID_U16(id, p1)         LOG_ID_U16((id), (p1))
#define LOG_END_ID_U24(id, p1)         LOG_ID_U24((id), (p1))
#define LOG_END_ID_U32(id, p1)         LOG_ID_U32((id), (p1))
#define LOG_END_ID_BYTES(id, b, n)     LOG_ID_BYTES((id), (b), (n))

// --- Unconditional DATA severity ---

#define LOG_DATA_ID(id)                LOG_ID(id)
#define LOG_DATA_ID_U8(id, p1)         LOG_ID_U8((id), (p1))
#define LOG_DATA_ID_U16(id, p1)        LOG_ID_U16((id), (p1))
#define LOG_DATA_ID_U24(id, p1)        LOG_ID_U24((id), (p1))
#define LOG_DATA_ID_U32(id, p1)        LOG_ID_U32((id), (p1))
#define LOG_DATA_ID_BYTES(id, b, n)    LOG_ID_BYTES((id), (b), (n))

// --- DATA multi-param composites ---

// Two u16 values packed as 4 big-endian bytes.
#define LOG_DATA_ID_U16_U16(id, p1, p2)                                \
    do {                                                               \
        uint16_t _v1 = (uint16_t)(p1); uint16_t _v2 = (uint16_t)(p2); \
        uint8_t _b[4] = {                                              \
            (uint8_t)((_v1 >> 8) & 0xFF), (uint8_t)(_v1 & 0xFF),      \
            (uint8_t)((_v2 >> 8) & 0xFF), (uint8_t)(_v2 & 0xFF)       \
        };                                                             \
        rurp_log_id((id), _b, 4);                                      \
    } while (0)

// Two u32 values packed as 8 big-endian bytes.
#define LOG_DATA_ID_U32_U32(id, p1, p2)                                \
    do {                                                               \
        uint32_t _v1 = (uint32_t)(p1); uint32_t _v2 = (uint32_t)(p2); \
        uint8_t _b[8] = {                                              \
            (uint8_t)((_v1 >> 24) & 0xFF), (uint8_t)((_v1 >> 16) & 0xFF), \
            (uint8_t)((_v1 >> 8)  & 0xFF), (uint8_t)(_v1 & 0xFF),     \
            (uint8_t)((_v2 >> 24) & 0xFF), (uint8_t)((_v2 >> 16) & 0xFF), \
            (uint8_t)((_v2 >> 8)  & 0xFF), (uint8_t)(_v2 & 0xFF)      \
        };                                                             \
        rurp_log_id((id), _b, 8);                                      \
    } while (0)

#endif  // __LOGGING_ID_H__
