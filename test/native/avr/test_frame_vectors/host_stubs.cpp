/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 *
 * Phase 52 Plan 02 — host stub TU for test_frame_vectors.
 *
 * Provides no-op rurp_* symbol implementations so the test binary links
 * against boards/rurp_serial_utils.cpp (pulled in via build_src_filter) on
 * the host platform = native without a real AVR toolchain.
 *
 * Mirrors the pattern from test_cobs_cmd_frame/host_stubs.cpp (Phase 51).
 * No suite-specific overrides — defaults from the shared include are correct.
 */

#include <stdint.h>
#include <stddef.h>
#include <string.h>

#include <Arduino.h>
#include <ArduinoFake.h>

extern "C" {
#include "rurp_shield.h"
#include "rurp_types.h"
}

#include "../_shared/host_stubs_common.inc"
