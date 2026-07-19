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

/* Platform measurement backend. Returns the divider/ADC result before
 * board-level two-point calibration is applied. */
uint16_t rurp_read_voltage_uncalibrated_mv(void);

/* Common calibrated measurement API used by every platform. */
uint16_t rurp_apply_vpp_calibration(uint16_t uncalibrated_mv);
uint16_t rurp_read_voltage_mv(void);

/* Store a two-point linear calibration in the common configuration.
 * measured_* values are Firestarter's uncalibrated readings; actual_* values
 * are the voltages reported by the reference meter. */
bool rurp_calibrate_vpp_two_point(uint16_t measured_low_mv,
                                  uint16_t actual_low_mv,
                                  uint16_t measured_high_mv,
                                  uint16_t actual_high_mv);
void rurp_reset_vpp_calibration(void);
bool rurp_vpp_calibration_valid(void);

/* Common control surface. AVR Uno/Leonardo use the weak manual backend and
 * return RURP_VPP_MANUAL_ADJUSTMENT_REQUIRED. DAC-capable targets override
 * the platform hooks below and use the same calibrated ADC feedback loop. */
rurp_vpp_control_mode_t rurp_vpp_control_mode(void);
rurp_vpp_result_t rurp_set_vpp_target_mv(uint16_t target_mv,
                                         uint16_t tolerance_mv,
                                         uint16_t timeout_ms);
void rurp_disable_vpp_control(void);

/* Platform hooks. The common source provides weak manual/no-DAC defaults.
 * A DAC-capable target overrides all four hooks in its board backend. */
bool rurp_vpp_dac_available(void);
uint16_t rurp_vpp_dac_max_code(void);
void rurp_vpp_dac_write(uint16_t code);
void rurp_vpp_control_enable(bool enable);
void rurp_vpp_delay_ms(uint16_t milliseconds);

#ifdef __cplusplus
}
#endif

#endif // __RURP_VPP_H__
