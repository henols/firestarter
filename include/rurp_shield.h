/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 */
#ifndef __RURP_SHIELD_H__
#define __RURP_SHIELD_H__

#ifdef __cplusplus
extern "C" {
#endif

#include <stdint.h>
#include <stddef.h>
#include <string.h>
#include "rurp_platform.h"
#include "rurp_types.h"
#include "rurp_pinout.h"

#ifdef HARDWARE_REVISION
#define REVISION_0 0
#define REVISION_1 1
#define REVISION_