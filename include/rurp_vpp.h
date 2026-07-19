/*
 * Project Name: Firestarter
 * Copyright (c) 2026 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 */

#ifndef __RURP_VPP_H__
#define __RURP_VPP_H__

#include <stdbool.h>
#include <stdint.h>

#ifndef RURP_HAS_VPP_DAC
#define RURP_HAS_VPP_DAC 0
#endif

#ifndef RURP_VPP_DAC_BITS
#define RURP_VPP_DAC_BITS 0
#endif

#if RURP_HAS_VPP_DAC && (RURP_VPP_DAC_BITS == 0)
#error "RURP_VPP_DAC_BITS must be defined for DAC-capable boards"
#endif

#ifdef __cplusplus
extern "C" {
#endif

typedef enum rurp_vpp_control_mode {
    RURP_VPP_CONTROL_MANUAL = 0,
    RURP_VPP_CONTROL_DAC = 1
} rurp_vpp_control_mode_t;

typedef enum rurp_vpp_result {
    RURP_VPP_OK = 0,
    RURP_VPP_MANUAL_ADJUSTMENT_REQUIRED = 1,
    RURP_VPP_INVALID_ARGUMENT = 2,
    RURP_VPP_TIMEOUT = 3,
    RURP_VPP_OUT_OF_RANGE = 4
} rurp_vpp_result_t;

uint16_t rurp_read_voltage_uncalibrated_mv(void);
uint16_t rurp_apply_vpp_calibration(uint16_t uncalibrated_mv);
uint16_t rurp_read_voltage_mv(void);

bool rurp_calibrate_vpp_two_point(uint16_t measured_low_mv,
                                  uint16_t actual_low_mv,
                                  uint16_t measured_high_mv,
                                  uint16_t actual_high_mv);
void rurp_reset_vpp_calibration(void);
bool rurp_vpp_calibration_valid(void);

rurp_vpp_control_mode_t rurp_vpp_control_mode(void);
rurp_vpp_result_t rurp_set_vpp_target_mv(uint16_t target_mv,
                                         uint16_t tolerance_mv,
                                         uint16_t timeout_ms);
void rurp_disable_vpp_control(void);

#if RURP_HAS_VPP_DAC
void rurp_vpp_dac_write(uint16_t code);
void rurp_vpp_control_enable(bool enable);
void rurp_vpp_delay_ms(uint16_t milliseconds);
#endif

#ifdef __cplusplus
}
#endif

#endif // __RURP_VPP_H__
