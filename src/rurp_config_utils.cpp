/*
 * Project Name: Firestarter
 * Copyright (c) 2025 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 */

#include "rurp_shield.h"
#include <EEPROM.h>

#define CONFIG_START 48
#define VPP_CALIBRATION_UNITY_PPM 1000000L

rurp_configuration_t rurp_config;

rurp_configuration_t* rurp_get_config() {
    return &rurp_config;
}

void rurp_load_config() {
    rurp_configuration_t* config = rurp_get_config();
    EEPROM.get(CONFIG_START, *config);
    rurp_validate_config(config);
}

void rurp_save_config(rurp_configuration_t* config) {
    EEPROM.put(CONFIG_START, *config);
}

void rurp_validate_config(rurp_configuration_t* config) {
    if (strcmp(config->version, CONFIG_VERSION) != 0) {
        strcpy(config->version, CONFIG_VERSION);
        config->r1 = VALUE_R1;
        config->r2 = VALUE_R2;
        config->hardware_revision = 0xFF;
        config->vpp_gain_ppm = VPP_CALIBRATION_UNITY_PPM;
        config->vpp_offset_mv = 0;
        config->vpp_cal_measured_low_mv = 0;
        config->vpp_cal_actual_low_mv = 0;
        config->vpp_cal_measured_high_mv = 0;
        config->vpp_cal_actual_high_mv = 0;
        rurp_save_config(config);
    }
}
