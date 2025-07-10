/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 */

#include "rurp_shield.h"

#if defined(ARDUINO_AVR_UNO) || defined(ARDUINO_AVR_LEONARDO)

#include <Arduino.h>

uint16_t rurp_read_voltage_mv(uint16_t vcc_mv) {
    rurp_configuration_t* rurp_config = rurp_get_config();
    uint32_t r1 = rurp_config->r1;
    uint32_t r2 = rurp_config->r2;

    if (r2 == 0) {
        return 0;  // Avoid division by zero
    }

    // Set analog reference to default (VCC) for the measurement
    analogReference(DEFAULT);
    uint32_t adc_reading = analogRead(VOLTAGE_MEASURE_PIN);

    // Vin_mV = (ADC_reading * VCC_mV * (R1 + R2)) / (1024 * R2)
    // Use 64-bit integer to avoid overflow during calculation.
    uint64_t vin_mv = (uint64_t)adc_reading * vcc_mv * (r1 + r2) / (1024UL * r2);

    return (uint16_t)vin_mv;
}
#endif