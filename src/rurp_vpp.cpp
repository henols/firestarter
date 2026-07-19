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
constexpr uint16_t MAX_VPP_MV = 30000;

uint16_t clamp_u16(int64_t value) {
    if (value <= 0) return 0;
    if (value >= UINT16_MAX) return UINT16_MAX;
    return static_cast<uint16_t>(value);
}

uint16_t elapsed_ms(uint16_t elapsed, uint16_t increment) {
    const uint32_t next = static_cast<uint32_t>(elapsed) + increment;
    return next > UINT16_MAX ? UINT16_MAX : static_cast<uint16_t>(next);
}
}

uint16_t rurp_apply_vpp_calibration(uint16_t uncalibrated_mv) {
    const rurp_configuration_t* config = rurp_get_config();
    if (!rurp_vpp_calibration_valid()) {
        return uncalibrated_mv;
    }

    const int64_t calibrated =
        (static_cast<int64_t>(uncalibrated_mv) * config->vpp_gain_ppm) /
        CALIBRATION_SCALE + config->vpp_offset_mv;
    return clamp_u16(calibrated);
}

uint16_t rurp_read_voltage_mv(void) {
    return rurp_apply_vpp_calibration(rurp_read_voltage_uncalibrated_mv());
}

bool rurp_calibrate_vpp_two_point(uint16_t measured_low_mv,
                                  uint16_t actual_low_mv,
                                  uint16_t measured_high_mv,
                                  uint16_t actual_high_mv) {
    if (measured_high_mv <= measured_low_mv ||
        actual_high_mv <= actual_low_mv) {
        return false;
    }

    const int32_t measured_span =
        static_cast<int32_t>(measured_high_mv) - measured_low_mv;
    const int32_t actual_span =
        static_cast<int32_t>(actual_high_mv) - actual_low_mv;
    const int32_t gain_ppm = static_cast<int32_t>(
        (static_cast<int64_t>(actual_span) * CALIBRATION_SCALE + measured_span / 2) /
        measured_span);

    if (gain_ppm < MIN_GAIN_PPM || gain_ppm > MAX_GAIN_PPM) {
        return false;
    }

    const int32_t offset_mv = static_cast<int32_t>(actual_low_mv) -
        static_cast<int32_t>(
            (static_cast<int64_t>(measured_low_mv) * gain_ppm +
             CALIBRATION_SCALE / 2) /
            CALIBRATION_SCALE);

    rurp_configuration_t* config = rurp_get_config();
    config->vpp_gain_ppm = gain_ppm;
    config->vpp_offset_mv = offset_mv;
    config->vpp_cal_measured_low_mv = measured_low_mv;
    config->vpp_cal_actual_low_mv = actual_low_mv;
    config->vpp_cal_measured_high_mv = measured_high_mv;
    config->vpp_cal_actual_high_mv = actual_high_mv;
    rurp_save_config(config);
    return true;
}

void rurp_reset_vpp_calibration(void) {
    rurp_configuration_t* config = rurp_get_config();
    config->vpp_gain_ppm = CALIBRATION_SCALE;
    config->vpp_offset_mv = 0;
    config->vpp_cal_measured_low_mv = 0;
    config->vpp_cal_actual_low_mv = 0;
    config->vpp_cal_measured_high_mv = 0;
    config->vpp_cal_actual_high_mv = 0;
    rurp_save_config(config);
}

bool rurp_vpp_calibration_valid(void) {
    const rurp_configuration_t* config = rurp_get_config();
    return config->vpp_gain_ppm >= MIN_GAIN_PPM &&
           config->vpp_gain_ppm <= MAX_GAIN_PPM &&
           config->vpp_cal_measured_high_mv > config->vpp_cal_measured_low_mv &&
           config->vpp_cal_actual_high_mv > config->vpp_cal_actual_low_mv;
}

rurp_vpp_control_mode_t rurp_vpp_control_mode(void) {
    return rurp_vpp_dac_available()
        ? RURP_VPP_CONTROL_DAC
        : RURP_VPP_CONTROL_MANUAL;
}

rurp_vpp_result_t rurp_set_vpp_target_mv(uint16_t target_mv,
                                          uint16_t tolerance_mv,
                                          uint16_t timeout_ms) {
    if (target_mv == 0 || target_mv > MAX_VPP_MV || tolerance_mv == 0) {
        return RURP_VPP_INVALID_ARGUMENT;
    }

    if (!rurp_vpp_dac_available()) {
        return RURP_VPP_MANUAL_ADJUSTMENT_REQUIRED;
    }

    const uint16_t max_code = rurp_vpp_dac_max_code();
    if (max_code == 0) {
        return RURP_VPP_OUT_OF_RANGE;
    }

    uint32_t code =
        (static_cast<uint32_t>(target_mv) * max_code) / MAX_VPP_MV;
    uint16_t elapsed = 0;
    rurp_vpp_control_enable(true);

    while (elapsed <= timeout_ms) {
        rurp_vpp_dac_write(static_cast<uint16_t>(code));
        rurp_vpp_delay_ms(DAC_SETTLE_MS);
        elapsed = elapsed_ms(elapsed, DAC_SETTLE_MS);

        const uint16_t measured_mv = rurp_read_voltage_mv();
        if (measured_mv > MAX_VPP_MV) {
            rurp_disable_vpp_control();
            return RURP_VPP_OUT_OF_RANGE;
        }

        const int32_t error_mv =
            static_cast<int32_t>(target_mv) - measured_mv;
        if (error_mv >= -static_cast<int32_t>(tolerance_mv) &&
            error_mv <= static_cast<int32_t>(tolerance_mv)) {
            return RURP_VPP_OK;
        }

        int32_t step = static_cast<int32_t>(
            (static_cast<int64_t>(error_mv) * max_code) / MAX_VPP_MV);
        if (step == 0) step = error_mv > 0 ? 1 : -1;

        const int32_t next_code = static_cast<int32_t>(code) + step;
        if (next_code < 0 || next_code > max_code) {
            rurp_disable_vpp_control();
            return RURP_VPP_OUT_OF_RANGE;
        }
        code = static_cast<uint32_t>(next_code);
    }

    rurp_disable_vpp_control();
    return RURP_VPP_TIMEOUT;
}

void rurp_disable_vpp_control(void) {
    if (rurp_vpp_dac_available()) {
        rurp_vpp_dac_write(0);
    }
    rurp_vpp_control_enable(false);
}

__attribute__((weak)) bool rurp_vpp_dac_available(void) {
    return false;
}

__attribute__((weak)) uint16_t rurp_vpp_dac_max_code(void) {
    return 0;
}

__attribute__((weak)) void rurp_vpp_dac_write(uint16_t code) {
    (void)code;
}

__attribute__((weak)) void rurp_vpp_control_enable(bool enable) {
    (void)enable;
}

__attribute__((weak)) void rurp_vpp_delay_ms(uint16_t milliseconds) {
    (void)milliseconds;
}
