/*
 * Project Name: Firestarter
 * Copyright (c) 2026 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 */

#include "rurp_vpp.h"
#include "rurp_shield.h"

#include <limits.h>

namespace {
constexpr int32_t CALIBRATION_SCALE = 1000000L;
constexpr int32_t MIN_GAIN_PPM = 500000L;
constexpr int32_t MAX_GAIN_PPM = 1500000L;
constexpr uint16_t DAC_SETTLE_MS = 5;

uint16_t clamp_u16(int64_t value) {
    if (value <= 0) return 0;
    if (value >= UINT