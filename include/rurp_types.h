/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 */

#ifndef __RURP_TYPES_H__
#define __RURP_TYPES_H__

#include <stdint.h>

#ifndef HARDWARE_REVISION
#define rurp_register_t uint8_t
#else
#define rurp_register_t uint16_t
#endif

typedef struct rurp_configuration {
    char version[6];
    long r1;
    long r2;
    uint8_t hardware_revision;

    /* Common calibration of the complete divider + ADC measurement path.
     * calibrated_mv = uncalibrated_mv * vpp_gain_ppm / 1,000,000
     *               + vpp_offset_mv
     * The original two points are retained so later firmware can recalculate
     * coefficients if the representation changes. */
    int32_t vpp_gain_ppm;
    int32_t vpp_offset_mv;
    uint16_t vpp_cal_measured_low_mv;
    uint16_t vpp_cal_actual_low_mv;
    uint16_t vpp_cal_measured_high_mv;
    uint16_t vpp_cal_actual_high_mv;
} rurp_configuration_t;

#endif // __RURP_TYPES_H__