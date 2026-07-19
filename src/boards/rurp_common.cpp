/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 */

#include <Arduino.h>
#include "rurp_shield.h"
#include "rurp_pinout.h"

#if defined(ARDUINO_AVR_UNO) || defined(ARDUINO_AVR_ATmega328PB) || defined(ARDUINO_AVR_LEONARDO)

long rurp_get_bandgap_adc_reading() {
#if defined(ARDUINO_AVR_UNO) || defined(ARDUINO_AVR_ATmega328PB)
    ADMUX = _BV(REFS0) | _BV(MUX3) | _BV(MUX2) | _BV(MUX1);
#elif defined(ARDUINO_AVR_LEONARDO)
    ADMUX = _BV(REFS0) | _BV(MUX4) | _BV(MUX3) | _BV(MUX2) | _BV(MUX1);
#else
#error "Unsupported board"
#endif

    delay(2);
    ADCSRA |= _BV(ADSC);
    while (bit_is_set(ADCSRA, ADSC)) {
    }

    long result = ADCL;
    result |= ADCH << 8;
    return result;
}

uint16_t rurp_read_vcc_mv() {
    const long result = rurp_get_bandgap_adc_reading();
    if (result == 0) return 0;
    return (1126400L + result / 2) / result;
}

uint16_t rurp_read_voltage_uncalibrated_mv() {
    const rurp_configuration_t* config = rurp_get_config();
    const uint32_t r1 = config->r1;
    const uint32_t r2 = config->r2;

    analogReference(DEFAULT);

    // Discard the first sample after changing the ADC reference/channel, then
    // average 16 samples to reduce boost-converter and quantization noise.
    (void)analogRead(PIN_VPP_VOLTAGE_ADC);
    uint32_t sum = 0;
    for (uint8_t i = 0; i < 16; ++i) {
        sum += analogRead(PIN_VPP_VOLTAGE_ADC);
    }
    const uint32_t voltage_adc_reading = (sum + 8) / 16;

    const long bandgap_adc_reading = rurp_get_bandgap_adc_reading();
    if (bandgap_adc_reading == 0 || r2 == 0) return 0;

    const uint64_t numerator =
        static_cast<uint64_t>(voltage_adc_reading) * 1100UL * (r1 + r2);
    const uint64_t denominator =
        static_cast<uint64_t>(bandgap_adc_reading) * r2;

    return static_cast<uint16_t>((numerator + denominator / 2) / denominator);
}

#endif
