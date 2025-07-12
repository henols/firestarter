/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 */

#include "rurp_shield.h"

#if defined(ARDUINO_AVR_UNO) || defined(ARDUINO_AVR_LEONARDO)

#include <Arduino.h>

/**
 * @brief Reads the raw ADC value for the internal 1.1V bandgap reference.
 * This provides a basis for calculating the actual VCC, and using the raw
 * value in other calculations preserves precision.
 * @return The raw ADC reading as a long.
 */
long rurp_get_bandgap_adc_reading() {
    // Set the analog reference to the internal 1.1V and select the bandgap channel.
    // The MUX settings are different for Uno and Leonardo.
#if defined(ARDUINO_AVR_UNO)
    ADMUX = _BV(REFS0) | _BV(MUX3) | _BV(MUX2) | _BV(MUX1);
#elif defined(ARDUINO_AVR_LEONARDO)
    ADMUX = _BV(REFS0) | _BV(MUX4) | _BV(MUX3) | _BV(MUX2) | _BV(MUX1);
#else
#error "Unsupported board"
#endif

    delay(2); // Wait for voltage to stabilize
    ADCSRA |= _BV(ADSC);              // Start conversion
    while (bit_is_set(ADCSRA, ADSC))  // Wait for conversion to complete
        ;

    long result = ADCL;
    result |= ADCH << 8;
    return result;
}

uint16_t rurp_read_vcc_mv() {
    long result = rurp_get_bandgap_adc_reading();
    // Calculate Vcc (supply voltage) in millivolts
    // VCC_mV = (V_bandgap * ADC_resolution * 1000) / ADC_reading
    // VCC_mV = (1.1V * 1024 steps * 1000 mV/V) / ADC_reading = 1126400 / ADC_reading
    if (result == 0) return 0;  // Avoid division by zero
    // Add half of the divisor to the numerator to round the result
    return (1126400L + result / 2) / result;
}

uint16_t rurp_read_voltage_mv() {
    rurp_configuration_t* rurp_config = rurp_get_config();
    uint32_t r1 = rurp_config->r1;
    uint32_t r2 = rurp_config->r2;

    // Set analog reference to default (VCC) for the measurement
    analogReference(DEFAULT);
    uint32_t voltage_adc_reading = analogRead(VOLTAGE_MEASURE_PIN);

    long bandgap_adc_reading = rurp_get_bandgap_adc_reading();
    if (bandgap_adc_reading == 0 || r2 == 0) return 0; // Avoid division by zero

    // For higher precision, we use the raw bandgap ADC reading directly.
    // Vin_mV = (voltage_adc_reading * 1100 * (R1 + R2)) / (bandgap_adc_reading * R2)
    uint64_t numerator = (uint64_t)voltage_adc_reading * 1100UL * (r1 + r2);
    uint64_t denominator = (uint64_t)bandgap_adc_reading * r2;

    // Add half of the divisor to the numerator to round the result
    return (numerator + (denominator / 2)) / denominator;
}
#endif